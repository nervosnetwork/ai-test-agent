from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_test_map import build_report
from check_test_design import check_design
from check_test_evidence import build_evidence_report, validate_coverage, execution_for
from evidence_annotations import render_python, verify_comments_only
from workflow_lib import (design_hash, freeze_inputs, fresh_inputs, git, read_json, fingerprint,
                          snapshot, digest, validate_schema, write_json)
from migrate_repo_tests import preview, apply, refresh
import agent_adapters

REVIEW = '''# Admission
Scope: admission only; no whole-PR claim.

### SPEC-01：limit
Condition: valid positive limit
Expected: accepts below limit, rejects at limit
Observable: return value and unchanged old state
Basis: inputs/requirements.md
Source: explicit
Testing: required

## Tree
<!-- TEST-TREE-BEGIN -->
- Admission
  - API-01 [primary] -> SPEC-01: accepted
  - API-02 [primary] -> SPEC-01: rejected
  - API-01 [ref] -> SPEC-01: shared branch
  - [not_applicable] persistence — no persistent state
<!-- TEST-TREE-END -->

## Cases
<!-- TEST-CASES-BEGIN -->
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `API-01` | - [x] valid request | return value equals input | corruption | P0 |
| `API-02` | - [ ] limit reached | rejected without mutation | old state damaged | P1 |
<!-- TEST-CASES-END -->
'''
CODE = '''import unittest

class Admission(unittest.TestCase):
    # TEST-MAP: API-01
    def test_valid(self):
        value = int("3")
        self.assertEqual(value, 3)
'''


def cli(script, *args, root=ROOT, env=None):
    return subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *args], cwd=root,
                          text=True, capture_output=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})


def put(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')
    return path


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'tests'
        self.root.mkdir()
        self.product = Path(self.temp.name) / 'product'
        self.product.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.product)], check=True)
        git(self.product, 'config', 'user.name', 'Fixture')
        git(self.product, 'config', 'user.email', 'fixture@example.invalid')
        put(self.product, 'product.py', 'def admit(n):\n    return n < 3\n')
        git(self.product, 'add', '.')
        git(self.product, 'commit', '-qm', 'baseline')
        self.head = git(self.product, 'rev-parse', 'HEAD')
        self.review = put(self.root, 'reviews/api/limit.md', REVIEW)
        self.code = put(self.root, 'suites/api/tests/test_admission.py', CODE)
        put(self.root, 'suites/api/fixtures/input.json', '{}\n')
        put(self.root, 'inputs/requirements.md', 'Admit below limit; preserve old state at limit.\n')
        put(self.root, 'runner.conf', 'deterministic\n')
        design = check_design(self.root, ['reviews/api/limit.md'])
        self.assertEqual(design['errors'], [])
        self.state = {'schema_version': '2.0', 'scope': 'limit', 'scope_boundary': 'admission only',
                      'reviews': ['reviews/api/limit.md'], 'materials': ['inputs/requirements.md'],
                      'dependencies': ['inputs/requirements.md', 'runner.conf'], 'required_cases': [],
                      'command': [sys.executable, str(ROOT / 'scripts/run_unittest.py'), 'discover', '-s', 'suites/api/tests'],
                      'cwd': '.', 'product': {'root': str(self.product), 'base_tip': self.head, 'head': self.head, 'diff_base': self.head},
                      'cases': design['cases'], 'spec_refs': design['spec_refs'], 'design_decisions': [],
                      'design_adapter': {'contract_tested': True}, 'coverage_adapter': {'contract_tested': True},
                      'stage': 'COVERAGE_REVIEWED'}
        self.state['coverage_input'] = freeze_inputs(self.root, self.state)
        self.coverage = {'schema_version': '2.0', 'scope': 'limit',
                         'input_fingerprint': self.state['coverage_input']['fingerprint'],
                         'reviewer': {'model': 'unavailable', 'session': 'B', 'isolation': 'contract_tested'},
                         'cases': [self.record('API-01', 'covered'), self.record('API-02', 'missing')]}

    def record(self, case, coverage):
        binding = {'file': 'suites/api/tests/test_admission.py', 'symbol': 'Admission.test_valid',
                   'runner_selector': 'test_admission.Admission.test_valid', 'parameters': [],
                   'setup': 'input 3', 'trigger': 'parse input', 'observation': 'value of this call',
                   'assertions': [{'file': 'suites/api/tests/test_admission.py', 'symbol': 'Admission.test_valid',
                                   'text': 'self.assertEqual(value, 3)'}], 'missing': []}
        return {'case_id': case, 'spec_refs': self.state['spec_refs'][case], 'coverage': coverage,
                'bindings': [binding] if coverage != 'missing' else [], 'limitations': []}

    def workflow(self, *args):
        return cli('pr_workflow.py', '--root', str(self.root), *args)

    def analyze(self):
        run = self.workflow('analyze', '--scope', 'limit', '--pr', 'local PR', '--product', str(self.product),
                            '--base', self.head, '--review', 'reviews/api/limit.md', '--material', 'inputs/requirements.md',
                            '--dependency', 'runner.conf', '--scope-boundary', 'admission only',
                            '--command', json.dumps(self.state['command']))
        self.assertEqual(run.returncode, 0, run.stderr)

    def state_file(self):
        return self.root / '.ai-test-agent/current/limit/state.json'

    def advance_design(self):
        self.analyze()
        self.assertOK(self.workflow('prepare', '--scope', 'limit'))
        state = read_json(self.state_file())
        evidence = {'schema_version': '2.0', 'scope': 'limit', 'input_fingerprint': state['design_input']['fingerprint'],
                    'reviewer': {'session': 'simulated B', 'model': 'unavailable', 'isolation': 'contract_tested'}, 'findings': []}
        write_json(self.root / 'design.json', evidence)
        self.assertOK(self.workflow('review', '--scope', 'limit', '--phase', 'design', '--evidence', str(self.root / 'design.json')))

    def assertOK(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class DesignTests(Fixture):
    def test_explicit_blocks_exclude_spec_and_report_rows(self):
        self.review.write_text(REVIEW + '\n| `SPEC-01` | - [ ] text | a | b | P0 |\n| `API-01` | - [ ] report | a | b | P0 |\n')
        report = build_report(self.root)
        self.assertEqual(report['review_case_count'], 2)
        self.assertEqual(report['duplicate_review_ids'], {})
        put(self.root, 'reports/limit/coverage.md', '| `API-01` | - [ ] missing | x | x | P0 |\n')
        self.assertEqual(build_report(self.root)['review_case_count'], 2)

    def test_scope_does_not_require_unselected_automation(self):
        other = put(self.root, 'reviews/other.md', '| `OTHER-01` | - [ ] other | result | problem | P1 |\n')
        selected = build_report(self.root, ['reviews/api/limit.md'])
        self.assertEqual(selected['review_case_count'], 2)
        self.assertNotIn('OTHER-01', selected['unautomated'])
        other.write_text('| `API-01` | - [x] duplicate | result | problem | P1 |\n')
        self.assertIn('API-01', build_report(self.root, ['reviews/api/limit.md'])['duplicate_review_ids'])

    def test_scoped_cli_completeness_keeps_global_orphans(self):
        put(self.root, 'reviews/one.md', '| `ONE-01` | - [x] scenario | result | problem | P1 |\n')
        put(self.root, 'suites/api/tests/one.py', '# TEST-MAP: ONE-01\n')
        run = cli('check_test_map.py', '--root', str(self.root), '--review', 'reviews/one.md', '--require-complete', '--json')
        self.assertOK(run)
        self.assertEqual(json.loads(run.stdout)['automation_coverage'], '1/1')
        put(self.root, 'suites/api/tests/orphan.py', '# TEST-MAP: ORPHAN-01\n')
        run = cli('check_test_map.py', '--root', str(self.root), '--review', 'reviews/one.md', '--require-complete')
        self.assertEqual(run.returncode, 1)

    def test_tree_cross_references_are_deduplicated(self):
        result = check_design(self.root, self.state['reviews'])
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['spec_refs']['API-01'], ['reviews/api/limit.md#spec-01'])

    def test_dangling_orphan_duplicate_primary_and_missing_spec_fail(self):
        mutations = [('API-02 [primary]', 'API-99 [primary]'),
                     ('API-01 [ref]', 'API-01 [primary]'),
                     ('-> SPEC-01: rejected', '-> SPEC-99: rejected'),
                     ('  - API-02 [primary] -> SPEC-01: rejected\n', ''),
                     ('Basis: inputs/requirements.md\n', '')]
        for before, after in mutations:
            with self.subTest(before=before):
                self.review.write_text(REVIEW.replace(before, after))
                self.assertTrue(check_design(self.root, self.state['reviews'])['errors'])

    def test_unresolved_branches_and_inferences_are_decisions(self):
        self.review.write_text(REVIEW.replace('Source: explicit', 'Source: inference').replace('[not_applicable]', '[pending]'))
        result = check_design(self.root, self.state['reviews'])
        self.assertFalse(result['errors'])
        self.assertEqual(len(result['needs_decision']), 2)

    def test_unexplained_disposition_and_empty_spec_rule_fail(self):
        self.review.write_text(REVIEW.replace(' — no persistent state', ''))
        self.assertTrue(check_design(self.root, self.state['reviews'])['errors'])
        self.review.write_text(REVIEW.replace('Testing: required', 'Testing: not_tested'))
        self.assertTrue(check_design(self.root, self.state['reviews'])['errors'])

    def test_v1_still_maps_but_requires_selected_migration(self):
        self.review.write_text('| `API-01` | - [x] scenario | result | problem | P0 |\n')
        self.assertEqual(build_report(self.root)['automation_coverage'], '1/1')
        self.assertTrue(check_design(self.root, self.state['reviews'])['errors'])

    def test_design_hash_ignores_only_case_checkboxes(self):
        before = design_hash(self.root, self.state['reviews'])
        self.review.write_text(REVIEW.replace('- [x] valid', '- [ ] valid'))
        self.assertEqual(design_hash(self.root, self.state['reviews']), before)
        for change in [('P1', 'P0'), ('return value equals input', 'anything'), ('admission only', 'all behavior')]:
            self.review.write_text(REVIEW.replace(*change))
            self.assertNotEqual(design_hash(self.root, self.state['reviews']), before)

    def test_invalid_scope_review_path(self):
        with self.assertRaises(ValueError):
            build_report(self.root, ['../outside.md'])


class EvidenceTests(Fixture):
    def test_valid_evidence_and_report_includes_missing_case(self):
        self.assertEqual(validate_coverage(self.root, self.state, self.coverage), [])
        report = build_evidence_report(self.root, self.state, self.coverage)
        self.assertEqual(len(report['cases']), 2)
        self.assertEqual(report['cases'][1]['coverage'], 'missing')
        self.assertEqual(report['cases'][0]['execution'], 'not_run')
        self.assertEqual(report['result'], 'blocked')

    def test_acceptance_requires_all_dimensions_and_preserves_failure_facts(self):
        # Isolate the ready branch to one complete required Case, with script-bound execution.
        self.review.write_text(REVIEW.replace('  - API-02 [primary] -> SPEC-01: rejected\n', '').replace('| `API-02` | - [ ] limit reached | rejected without mutation | old state damaged | P1 |\n', ''))
        design = check_design(self.root, self.state['reviews'])
        self.state.update({'cases': design['cases'], 'spec_refs': design['spec_refs'], 'stage': 'EXECUTED', 'approval': {'human': 'fixture'}})
        self.state['coverage_input'] = freeze_inputs(self.root, self.state)
        self.coverage['cases'] = self.coverage['cases'][:1]
        self.coverage['input_fingerprint'] = self.state['coverage_input']['fingerprint']
        log = put(self.root, 'reports/limit/execution.log', 'Ran 1 test\nOK\n')
        execution = {'input_fingerprint': self.coverage['input_fingerprint'], 'collected': 1,
                     'status': 'passed', 'exit_code': 0, 'level': 'selector',
                     'output_file': 'reports/limit/execution.log', 'output_sha256': digest(log.read_bytes()),
                     'results': [{'selector': 'test_admission.Admission.test_valid', 'status': 'passed'}]}
        report = build_evidence_report(self.root, self.state, self.coverage, execution)
        self.assertEqual(report['result'], 'ready_for_acceptance')
        self.state['approval'] = None
        self.assertEqual(build_evidence_report(self.root, self.state, self.coverage, execution)['result'], 'needs_decision')
        self.state['approval'] = {'human': 'fixture'}
        execution['status'] = 'failed'
        self.assertEqual(build_evidence_report(self.root, self.state, self.coverage, execution)['result'], 'blocked')
        execution['status'] = 'passed'
        log.write_text('changed log')
        report = build_evidence_report(self.root, self.state, self.coverage, execution)
        self.assertEqual(report['result'], 'blocked')
        self.assertEqual(report['cases'][0]['execution'], 'not_run')

    def test_absent_evidence_stays_not_reviewed_not_covered(self):
        report = build_evidence_report(self.root, self.state)
        self.assertEqual(report['cases'][0]['coverage'], 'uncertain')
        self.assertEqual(report['cases'][1]['coverage'], 'missing')
        self.assertTrue(all(c['validity'] == 'not_reviewed' for c in report['cases']))

    def test_incomplete_and_duplicate_case_sets_rejected(self):
        self.coverage['cases'].pop()
        self.assertTrue(validate_coverage(self.root, self.state, self.coverage))
        self.coverage['cases'].append(copy.deepcopy(self.coverage['cases'][0]))
        self.assertTrue(validate_coverage(self.root, self.state, self.coverage))

    def test_covered_missing_assertion_or_literal_location_rejected(self):
        original = copy.deepcopy(self.coverage)
        for mutate in ('empty', 'wrong_text', 'wrong_symbol', 'gap'):
            self.coverage = copy.deepcopy(original)
            binding = self.coverage['cases'][0]['bindings'][0]
            if mutate == 'empty':
                binding['assertions'] = []
            elif mutate == 'wrong_text':
                binding['assertions'][0]['text'] = 'assert imaginary()'
            elif mutate == 'wrong_symbol':
                binding['assertions'][0]['symbol'] = 'absent'
            else:
                binding['missing'] = ['missing preservation assertion']
            self.assertTrue(validate_coverage(self.root, self.state, self.coverage), mutate)

    def test_schema_rejects_unknown_fields_types_and_status(self):
        schema = read_json(ROOT / 'schemas/coverage.schema.json')
        for mutate in ('unexpected', 'coverage', 'cases'):
            record = copy.deepcopy(self.coverage)
            if mutate == 'unexpected':
                record['approved'] = True
            elif mutate == 'coverage':
                record['cases'][0]['coverage'] = 'passed'
            else:
                record['cases'] = {}
            with self.assertRaises(ValueError):
                validate_schema(record, schema)

    def test_snapshot_changes_in_test_helper_config_spec_and_product(self):
        for name in ('suites/api/tests/test_admission.py', 'suites/api/fixtures/input.json', 'runner.conf', 'reviews/api/limit.md'):
            path = self.root / name
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            self.assertFalse(fresh_inputs(self.root, self.state, self.state['coverage_input']), name)
            report = build_evidence_report(self.root, self.state, self.coverage)
            self.assertEqual(report['cases'][0]['validity'], 'stale')
            path.write_bytes(original)
        put(self.product, 'product.py', 'def admit(n):\n    return True\n')
        self.assertFalse(fresh_inputs(self.root, self.state, self.state['coverage_input']))

    def test_new_suite_input_and_new_product_head_invalidate(self):
        helper = put(self.root, 'suites/api/new_helper.py', 'VALUE = 3\n')
        self.assertFalse(fresh_inputs(self.root, self.state, self.state['coverage_input']))
        helper.unlink()
        git(self.product, 'commit', '--allow-empty', '-qm', 'new head')
        self.assertFalse(fresh_inputs(self.root, self.state, self.state['coverage_input']))

    def test_symlink_outside_snapshot_is_rejected(self):
        outside = put(self.product, 'outside.txt', 'outside')
        (self.root / 'runner.conf').unlink()
        (self.root / 'runner.conf').symlink_to(outside)
        with self.assertRaises(ValueError):
            freeze_inputs(self.root, self.state)

    def test_execution_selector_parameters_and_unstable(self):
        item = self.coverage['cases'][0]
        fp = 'fixed'
        execution = {'input_fingerprint': fp, 'collected': 1, 'status': 'passed', 'results': [
            {'selector': 'test_admission.Admission.test_valid', 'status': 'passed'}]}
        self.assertEqual(execution_for(item, execution, fp), ('passed', False))
        item['bindings'][0]['parameters'] = ['test_valid (n=1)', 'test_valid (n=2)']
        self.assertEqual(execution_for(item, execution, fp), ('not_run', False))
        execution['results'] = [{'selector': p, 'status': 'passed'} for p in item['bindings'][0]['parameters']]
        self.assertEqual(execution_for(item, execution, fp), ('passed', False))
        execution['results'].append(execution['results'][0])
        self.assertEqual(execution_for(item, execution, fp), ('passed', True))
        execution['collected'] = 0
        self.assertEqual(execution_for(item, execution, fp), ('not_run', False))

    def test_wrong_input_fingerprint_and_edited_evidence_are_rejected(self):
        self.coverage['input_fingerprint'] = '0' * 64
        self.assertTrue(validate_coverage(self.root, self.state, self.coverage))
        self.coverage['input_fingerprint'] = self.state['coverage_input']['fingerprint']
        self.state['coverage_evidence_hash'] = fingerprint(self.coverage)
        self.coverage['cases'][0]['limitations'].append('new')
        self.assertTrue(build_evidence_report(self.root, self.state, self.coverage)['errors'])


class AnnotationTests(Fixture):
    def test_idempotent_managed_comments_preserve_code(self):
        case = self.coverage['cases'][0]
        entries = [(case, case['bindings'][0])]
        first = render_python(CODE, entries)
        self.assertIn('TEST-EVIDENCE-BEGIN: API-01', first)
        self.assertEqual(render_python(first, entries), first)
        verify_comments_only(CODE, first)
        self.assertIn('# TEST-MAP: API-01', first)

    def test_directives_and_docstrings_preserved(self):
        code = CODE.replace('    # TEST-MAP', '    # type: ignore\n    # TEST-MAP').replace('        value', '        """Example: >>> 1 + 1"""\n        value')
        case = self.coverage['cases'][0]
        result = render_python(code, [(case, case['bindings'][0])])
        self.assertIn('# type: ignore', result)
        self.assertIn('>>> 1 + 1', result)
        with self.assertRaises(ValueError):
            verify_comments_only(code, result.replace('# type: ignore', '# type: noignore'))
        with self.assertRaises(ValueError):
            verify_comments_only(code, result.replace('self.assertEqual(value, 3)', 'self.assertEqual(value, 4)'))

    def test_tool_directive_inside_managed_block_rejected(self):
        bad = CODE.replace('    def test_valid', '    # TEST-EVIDENCE-BEGIN: API-01\n    # type: ignore\n    # TEST-EVIDENCE-END: API-01\n    def test_valid')
        case = self.coverage['cases'][0]
        with self.assertRaises(ValueError):
            render_python(bad, [(case, case['bindings'][0])])

    def test_markers_inside_strings_are_not_comments(self):
        code = 'message = """\n# TEST-EVIDENCE-BEGIN: API-01\n# arbitrary string\n# TEST-EVIDENCE-END: API-01\n"""\n' + CODE
        case = self.coverage['cases'][0]
        result = render_python(code, [(case, case['bindings'][0])])
        self.assertIn('# arbitrary string', result)
        verify_comments_only(code, result)

    def test_generated_text_cannot_become_python_or_pragma(self):
        case = self.coverage['cases'][0]
        case['bindings'][0]['setup'] = 'x\n# type: ignore\nprint("unexpected")'
        result = render_python(CODE, [(case, case['bindings'][0])])
        self.assertIn('# Evidence | # type: ignore', result)
        verify_comments_only(CODE, result)


class WorkflowTests(Fixture):
    def test_unconfirmed_implementation_and_wrong_phase_are_blocked(self):
        self.analyze()
        result = self.workflow('implemented', '--scope', 'limit')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(read_json(self.state_file())['stage'], 'BLOCKED')

    def test_g1_checkbox_only_change_keeps_confirmation(self):
        self.advance_design()
        self.assertOK(self.workflow('confirm', '--scope', 'limit', '--human', 'simulated reviewer', '--confirmation', 'fixture approved'))
        self.review.write_text(REVIEW.replace('- [ ] limit', '- [x] limit'))
        self.code.write_text(CODE + '\n# TEST-MAP: API-02\n')
        self.assertOK(self.workflow('implemented', '--scope', 'limit'))
        self.assertEqual(read_json(self.state_file())['stage'], 'IMPLEMENTED')

    def test_continue_before_prepare_is_read_only_status(self):
        self.analyze()
        self.assertOK(self.workflow('continue', '--scope', 'limit'))
        self.assertEqual(read_json(self.state_file())['stage'], 'INPUT_READY')

    def test_head_drift_before_prepare_rejects_stale_raw_diff(self):
        self.analyze()
        git(self.product, 'commit', '--allow-empty', '-qm', 'new head')
        result = self.workflow('prepare', '--scope', 'limit')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(read_json(self.state_file())['stage'], 'STALE')

    def test_human_can_resolve_pending_decision_without_spending_b_call(self):
        self.review.write_text(REVIEW.replace('Source: explicit', 'Source: inference'))
        self.advance_design()
        result = self.workflow('confirm', '--scope', 'limit', '--human', 'fixture', '--confirmation', 'approved')
        self.assertEqual(result.returncode, 1)
        before = read_json(self.state_file())
        self.assertEqual(before['stage'], 'NEEDS_DECISION')
        self.assertOK(self.workflow('confirm', '--scope', 'limit', '--human', 'fixture', '--confirmation', 'approved', '--decision', 'Accept candidate rule for this fixture'))
        after = read_json(self.state_file())
        self.assertEqual(after['stage'], 'DESIGN_CONFIRMED')
        self.assertEqual(before['review_calls'], after['review_calls'])

    def test_material_design_change_requires_new_g1(self):
        self.advance_design()
        self.assertOK(self.workflow('confirm', '--scope', 'limit', '--human', 'fixture', '--confirmation', 'approved'))
        self.review.write_text(REVIEW.replace('return value equals input', 'any non-null value'))
        result = self.workflow('implemented', '--scope', 'limit')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(read_json(self.state_file())['stage'], 'STALE')

    def full_coverage(self):
        self.advance_design()
        self.assertOK(self.workflow('confirm', '--scope', 'limit', '--human', 'fixture', '--confirmation', 'approved'))
        self.assertOK(self.workflow('implemented', '--scope', 'limit'))
        state = read_json(self.state_file())
        self.coverage['input_fingerprint'] = state['coverage_input']['fingerprint']
        write_json(self.root / 'coverage-input.json', self.coverage)
        self.assertOK(self.workflow('review', '--scope', 'limit', '--phase', 'coverage', '--evidence', str(self.root / 'coverage-input.json')))

    def test_full_cli_flow_missing_case_never_accepted(self):
        self.full_coverage()
        self.assertOK(self.workflow('annotate', '--scope', 'limit'))
        first = self.code.read_bytes()
        receipt = read_json(self.root / 'reports/limit/annotation-receipt.json')
        self.assertTrue(receipt['changes'])
        self.assertOK(self.workflow('annotate', '--scope', 'limit'))
        self.assertEqual(self.code.read_bytes(), first)
        self.assertEqual(receipt, read_json(self.root / 'reports/limit/annotation-receipt.json'))
        self.assertOK(self.workflow('run', '--scope', 'limit'))
        execution = read_json(self.root / 'reports/limit/execution.json')
        self.assertEqual(execution['exit_code'], 0)
        self.assertEqual(execution['collected'], 1)
        self.assertEqual(execution['results'][0]['selector'], 'test_admission.Admission.test_valid')
        self.assertOK(self.workflow('continue', '--scope', 'limit'))
        acceptance = read_json(self.root / 'reports/limit/acceptance.json')
        self.assertEqual(acceptance['cases'][0]['execution'], 'passed')
        self.assertEqual(acceptance['cases'][1]['coverage'], 'missing')
        self.assertEqual(acceptance['result'], 'needs_decision')
        self.assertFalse(acceptance['independent_review'])
        self.assertNotIn('OPENAI_API_KEY', execution['environment_keys'])
        strict = cli('check_test_evidence.py', '--root', str(self.root), '--scope', 'limit', '--require-reviewed')
        self.assertEqual(strict.returncode, 1)

    def test_fixture_drift_blocks_final_execution(self):
        self.full_coverage()
        put(self.root, 'suites/api/fixtures/input.json', '{"changed":true}')
        result = self.workflow('run', '--scope', 'limit')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(read_json(self.state_file())['stage'], 'STALE')

    def test_schema_error_retains_recovery_stage_and_budget(self):
        self.advance_design()
        self.assertOK(self.workflow('confirm', '--scope', 'limit', '--human', 'fixture', '--confirmation', 'approved'))
        self.assertOK(self.workflow('implemented', '--scope', 'limit'))
        put(self.root, 'bad.json', '{"truncated":')
        self.assertEqual(self.workflow('review', '--scope', 'limit', '--phase', 'coverage', '--evidence', str(self.root / 'bad.json')).returncode, 1)
        blocked = read_json(self.state_file())
        self.assertEqual(blocked['stage'], 'BLOCKED')
        self.assertEqual(blocked['resume_from'], 'IMPLEMENTED')
        self.assertEqual(blocked['review_calls']['coverage'], 1)
        self.assertOK(self.workflow('retry', '--scope', 'limit'))
        self.assertEqual(read_json(self.state_file())['stage'], 'IMPLEMENTED')

    def test_zero_exit_without_result_file_is_not_case_pass(self):
        self.state['command'] = [sys.executable, '-c', 'print("no runner tests")']
        self.full_coverage()
        self.assertOK(self.workflow('run', '--scope', 'limit'))
        execution = read_json(self.root / 'reports/limit/execution.json')
        self.assertEqual(execution['exit_code'], 0)
        self.assertEqual(execution['status'], 'not_run')
        self.assertEqual(execution['level'], 'suite')
        self.assertOK(self.workflow('continue', '--scope', 'limit'))
        self.assertEqual(read_json(self.root / 'reports/limit/acceptance.json')['result'], 'blocked')

    def test_timeout_retains_output_and_remains_blocked(self):
        self.state['command'] = [sys.executable, '-c', 'import time; print("started",flush=True); time.sleep(20)']
        self.full_coverage()
        self.assertOK(self.workflow('run', '--scope', 'limit', '--timeout', '1'))
        execution = read_json(self.root / 'reports/limit/execution.json')
        self.assertEqual(execution['status'], 'blocked')
        self.assertEqual(execution['failure_kind'], 'runner_or_timeout')
        self.assertIn('started', (self.root / 'reports/limit/execution.log').read_text())

    def test_unsupported_language_is_proposed_not_modified(self):
        # Same-state imported evidence; this test exercises only the comment renderer boundary.
        from pr_workflow import annotate
        rust = put(self.root, 'suites/api/tests/sample.rs', '// TEST-MAP: API-02\nfn test_limit() { assert!(true); }\n')
        self.review.write_text(REVIEW.replace('- [ ] limit', '- [x] limit'))
        self.state['coverage_input'] = freeze_inputs(self.root, self.state)
        self.coverage['input_fingerprint'] = self.state['coverage_input']['fingerprint']
        self.coverage['cases'][1]['coverage'] = 'partial'
        b = copy.deepcopy(self.coverage['cases'][0]['bindings'][0])
        b.update({'file':'suites/api/tests/sample.rs', 'symbol':'test_limit', 'runner_selector':'test_limit',
                  'assertions':[], 'missing':['no real admission trigger']})
        self.coverage['cases'][1]['bindings'] = [b]
        reports = self.root / 'reports/limit'
        write_json(reports / 'coverage.json', self.coverage)
        before = rust.read_bytes()
        annotate(self.root, self.state, reports)
        self.assertEqual(rust.read_bytes(), before)
        proposals = read_json(reports / 'annotation-proposals.json')
        self.assertEqual(proposals[0]['case_id'], 'API-02')

    def test_budget_exhaustion_is_needs_decision(self):
        self.advance_design()
        self.assertOK(self.workflow('prepare', '--scope', 'limit'))
        self.assertOK(self.workflow('review', '--scope', 'limit', '--phase', 'design', '--evidence', str(self.root / 'design.json')))
        self.assertOK(self.workflow('prepare', '--scope', 'limit'))
        self.assertEqual(self.workflow('review', '--scope', 'limit', '--phase', 'design', '--evidence', str(self.root / 'design.json')).returncode, 1)
        self.assertEqual(read_json(self.state_file())['stage'], 'NEEDS_DECISION')


class RunnerTests(Fixture):
    def run_native(self, code):
        self.code.write_text(code)
        target = self.root / 'result.json'
        run = cli('run_unittest.py', 'discover', '-s', 'suites/api/tests', root=self.root, env={'AI_TEST_AGENT_RESULT': str(target)})
        return run, read_json(target)

    def test_zero_skipped_failed_and_passed_are_distinct(self):
        scenarios = [('', 0, 0, []),
                     (CODE, 0, 1, ['passed']),
                     (CODE.replace('    def test_valid', '    @unittest.skip("reason")\n    def test_valid'), 0, 1, ['skipped']),
                     (CODE.replace('value, 3', 'value, 4'), 1, 1, ['failed'])]
        for code, rc, collected, statuses in scenarios:
            run, result = self.run_native(code)
            self.assertEqual(run.returncode, rc, run.stderr)
            self.assertEqual(result['collected'], collected)
            self.assertEqual([r['status'] for r in result['results']], statuses)

    def test_unittest_subtest_records_concrete_parameters(self):
        code = CODE.replace('        value = int("3")\n        self.assertEqual(value, 3)', '        for n in [1, 2]:\n            with self.subTest(n=n):\n                self.assertLess(n, 3)')
        run, result = self.run_native(code)
        self.assertEqual(run.returncode, 0)
        ids = [r['selector'] for r in result['results']]
        self.assertIn('test_admission.Admission.test_valid (n=1)', ids)
        self.assertIn('test_admission.Admission.test_valid (n=2)', ids)


class MigrationTests(Fixture):
    def test_preview_apply_idempotence_and_rollback_preserve_reviews_and_custom_prose(self):
        put(self.root, 'AGENTS.md', '# Custom instructions\nKeep sentinel.\nDo not create per-PR reports, run archives, approval histories, or status ledgers.\n')
        original = self.review.read_bytes()
        plan_file = self.root / '.ai-test-agent/migration/plan.json'
        plan = preview(self.root, plan_file)
        self.assertFalse((self.root / 'scripts/check_test_design.py').exists())
        self.assertGreater(apply(self.root, plan_file, plan['confirmation'])['changed'], 0)
        self.assertEqual(self.review.read_bytes(), original)
        self.assertIn('Keep sentinel.', (self.root / 'AGENTS.md').read_text())
        self.assertEqual(apply(self.root, plan_file, plan['confirmation'])['changed'], 0)
        self.assertGreater(apply(self.root, plan_file, plan['confirmation'], True)['changed'], 0)
        self.assertFalse((self.root / 'scripts/check_test_design.py').exists())
        self.assertEqual(self.review.read_bytes(), original)
        self.assertNotIn('## PR v2', (self.root / 'AGENTS.md').read_text())

    def test_custom_template_merge_requires_refreshed_confirmation(self):
        put(self.root, 'templates/test-review.md', 'custom prior template\n')
        plan_file = self.root / '.ai-test-agent/migration/plan.json'
        plan = preview(self.root, plan_file)
        proposed = plan_file.parent / 'proposed/templates/test-review.md'
        proposed.write_text(proposed.read_text() + '\nRetained custom review requirement.\n')
        with self.assertRaises(ValueError):
            apply(self.root, plan_file, plan['confirmation'])
        updated = refresh(self.root, plan_file)
        self.assertNotEqual(plan['confirmation'], updated['confirmation'])
        apply(self.root, plan_file, updated['confirmation'])
        self.assertIn('Retained custom review requirement.', (self.root / 'templates/test-review.md').read_text())
        apply(self.root, plan_file, updated['confirmation'], True)
        self.assertEqual((self.root / 'templates/test-review.md').read_text(), 'custom prior template\n')

    def test_migration_rejects_modified_plan_source_or_destination(self):
        put(self.root, 'AGENTS.md', '# Original\n')
        plan_file = self.root / '.ai-test-agent/migration/plan.json'
        plan = preview(self.root, plan_file)
        with self.assertRaises(ValueError):
            apply(self.root, plan_file, 'not-confirmed')
        put(self.root, 'AGENTS.md', '# Changed since preview\n')
        with self.assertRaises(ValueError):
            apply(self.root, plan_file, plan['confirmation'])
        self.assertFalse((self.root / 'scripts/check_test_design.py').exists())

    def test_init_generated_runtime_self_contained_and_additive(self):
        project = Path(self.temp.name) / 'generated'
        args = ('--project', 'Example', '--source-repo', str(self.product), '--suites', 'integration', 'p2p', 'performance', 'fuzz', '--output', str(project))
        self.assertOK(cli('init_repo_tests.py', *args))
        for file in ['scripts/pr_workflow.py', 'scripts/workflow_lib.py', 'scripts/agent_adapters.py', 'schemas/coverage.schema.json', 'docs/ai-test-agent/coverage-review.md', 'templates/coverage-report.md']:
            self.assertTrue((project / file).is_file(), file)
        probe = subprocess.run([sys.executable, str(project / 'scripts/pr_workflow.py'), '--help'], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(probe.returncode, 0, probe.stderr)
        original = (project / 'scripts/check_test_evidence.py').read_text()
        put(project, 'scripts/check_test_evidence.py', original + '\n# custom sentinel\n')
        self.assertOK(cli('init_repo_tests.py', *args))
        self.assertIn('# custom sentinel', (project / 'scripts/check_test_evidence.py').read_text())


class AdapterTests(unittest.TestCase):
    def test_commands_start_new_sessions_and_restrict_tools(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            schema = put(root, 'schema.json', '{}')
            for backend in ('codex', 'claude'):
                argv = agent_adapters.command(backend, backend, root, schema, root / 'output.json')
                self.assertNotIn('resume', argv)
                self.assertNotIn('--continue', argv)
                self.assertFalse(any('bypass' in arg for arg in argv))
                self.assertNotIn('--model', argv)
                self.assertIn('--ephemeral' if backend == 'codex' else '--no-session-persistence', argv)
            self.assertIn('read-only', agent_adapters.command('codex', 'codex', root, schema, root / 'out'))
            self.assertIn('Read,Grep,Glob', agent_adapters.command('claude', 'claude', root, schema, root / 'out'))

    def test_missing_backend_is_explicit(self):
        with patch('agent_adapters.shutil.which', return_value=None):
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                agent_adapters.probe('codex')

    def test_fake_cli_transport_never_receives_parent_conversation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            schema = put(root, 'schema.json', '{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"],"additionalProperties":false}')
            fake = put(root, 'codex', '#!/usr/bin/env python3\nimport sys,json,pathlib\nargs=sys.argv[1:]\nif "--version" in args: print("test-cli 1")\nelif "--help" in args: print("--ephemeral --sandbox --output-schema --output-last-message --ignore-user-config")\nelse:\n text=sys.stdin.read()\n assert "A_PRIVATE_SENTINEL" not in text\n pathlib.Path(args[args.index("--output-last-message")+1]).write_text(json.dumps({"ok":True}))\n')
            fake.chmod(0o755)
            with patch('agent_adapters.shutil.which', return_value=str(fake)):
                value, metadata = agent_adapters.invoke('codex', root, schema, 'Explicit B-only packet', 5, root / 'out.json')
            self.assertEqual(value, {'ok': True})
            self.assertFalse(metadata['contract_tested'])
            self.assertEqual(metadata['isolation'], 'isolation_unverified')
            self.assertEqual(metadata['exit_code'], 0)


if __name__ == '__main__':
    unittest.main()
