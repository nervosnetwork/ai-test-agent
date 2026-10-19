from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from diff_spec_coverage import diff_inventory, validate_diff_coverage
from check_test_design import check_design
from pr_workflow import review
from workflow_lib import git, read_json, validate_schema, write_json
from test_v2_tools import Fixture, put


DIFF = '''diff --git a/api.py b/api.py
index 123..456 100644
--- a/api.py
+++ b/api.py
@@ -1 +1 @@
-old
+new
@@ -40 +40 @@
-reject
+accept
diff --git a/old.txt b/new.txt
similarity index 100%
rename from old.txt
rename to new.txt
diff --git a/asset.bin b/asset.bin
Binary files a/asset.bin and b/asset.bin differ
diff --git a/run b/run
old mode 100644
new mode 100755
diff --git a/empty b/empty
new file mode 100644
index 0000000..e69de29
diff --git a/removed b/removed
deleted file mode 100644
index e69de29..0000000
'''


def mapped(unit, spec='reviews/api/limit.md#spec-01'):
    return {'change_id': unit['change_id'], 'status': 'mapped', 'spec_refs': [spec],
            'reason': 'The admission contract specifies the changed threshold and preserved state.',
            'finding_ids': []}


class DiffAccountingTests(unittest.TestCase):
    def setUp(self):
        self.units = diff_inventory(DIFF, 'product.diff')
        self.state = {'diff_inventory': self.units, 'all_spec_refs': ['reviews/api/limit.md#spec-01']}
        self.value = {'diff_coverage': [mapped(unit) for unit in self.units], 'findings': []}

    def test_inventory_covers_all_lines_including_hunkless_changes(self):
        self.assertEqual(len(self.units), 7)
        self.assertEqual(len({unit['change_id'] for unit in self.units}), 7)
        self.assertEqual(sum(bool(unit['hunk_header']) for unit in self.units), 2)
        covered = []
        for unit in self.units:
            start, end = map(int, unit['location'].split(':')[1].split('-'))
            covered.extend(range(start, end + 1))
        self.assertEqual(covered, list(range(1, len(DIFF.splitlines()) + 1)))
        self.assertEqual(diff_inventory(DIFF, 'product.diff'), self.units)
        self.assertNotEqual(diff_inventory(DIFF.replace('+new', '+other'), 'product.diff')[0]['change_id'],
                            self.units[0]['change_id'])
        self.assertEqual(diff_inventory('', 'product.diff'), [])
        with self.assertRaisesRegex(ValueError, 'complete git unified diff'):
            diff_inventory('truncated input', 'product.diff')

    def test_every_unit_requires_one_record(self):
        validate_diff_coverage(self.state, self.value)
        for change in ('missing', 'duplicate', 'unknown'):
            with self.subTest(change=change):
                value = copy.deepcopy(self.value)
                if change == 'missing':
                    value['diff_coverage'].pop()
                elif change == 'duplicate':
                    value['diff_coverage'].append(value['diff_coverage'][0])
                else:
                    value['diff_coverage'][0]['change_id'] = 'DIFF-' + '0' * 64
                with self.assertRaises(ValueError):
                    validate_diff_coverage(self.state, value)

    def test_dispositions_require_real_links_reasons_and_findings(self):
        for changes in ({'spec_refs': []}, {'spec_refs': ['invented#spec-01']}, {'reason': ' '},
                        {'status': 'gap'}, {'status': 'unanalysed'},
                        {'finding_ids': ['F-99']}, {'status': 'no_behavior_change'},
                        {'status': 'out_of_scope'}):
            with self.subTest(changes=changes):
                value = copy.deepcopy(self.value)
                value['diff_coverage'][0].update(changes)
                with self.assertRaises(ValueError):
                    validate_diff_coverage(self.state, value)
        for status in ('no_behavior_change', 'out_of_scope'):
            value = copy.deepcopy(self.value)
            value['diff_coverage'][0].update(status=status, spec_refs=[])
            validate_diff_coverage(self.state, value)

    def test_legacy_evidence_or_state_requires_new_review(self):
        with self.assertRaisesRegex(ValueError, 'missing diff_coverage'):
            validate_diff_coverage(self.state, {'findings': []})
        with self.assertRaisesRegex(ValueError, 'prepare and review'):
            validate_diff_coverage({}, self.value)
        schema = read_json(ROOT / 'schemas/design-review.schema.json')
        evidence = {'schema_version': '2.0', 'scope': 'test', 'input_fingerprint': '0' * 64,
                    'reviewer': {'session': 'B', 'model': 'fixture', 'isolation': 'isolation_unverified'},
                    'acknowledgements': [], 'findings': []}
        with self.assertRaisesRegex(ValueError, 'missing diff_coverage'):
            validate_schema(evidence, schema)
        evidence['diff_coverage'] = []
        validate_schema(evidence, schema)


class DiffReviewWorkflowTests(Fixture):
    def prepare_changed_product(self):
        put(self.product, 'product.py', 'def admit(n):\n    return n < 5\n')
        git(self.product, 'add', '.')
        git(self.product, 'commit', '-qm', 'change admission limit')
        self.analyze()
        self.assertOK(self.workflow('prepare', '--scope', 'limit'))
        state = read_json(self.state_file())
        self.assertEqual(len(state['diff_inventory']), 1)
        return state

    def evidence(self, state):
        return {'schema_version': '2.0', 'scope': 'limit',
                'input_fingerprint': state['design_input']['fingerprint'],
                'reviewer': {'session': 'B', 'model': 'fixture', 'isolation': 'isolation_unverified'},
                'acknowledgements': [{'case_id': case, 'spec_refs': refs}
                                     for case, refs in state['spec_refs'].items()],
                'diff_coverage': [mapped(unit) for unit in state['diff_inventory']], 'findings': []}

    def review_and_respond(self, state, evidence):
        write_json(self.root / 'design.json', evidence)
        self.assertOK(self.workflow('review', '--scope', 'limit', '--phase', 'design',
                                    '--evidence', str(self.root / 'design.json')))
        response = {'schema_version': '2.0', 'scope': 'limit',
                    'input_fingerprint': state['design_input']['fingerprint'],
                    'responses': [{'finding_id': item['finding_id'], 'disposition': 'accepted',
                                   'response': 'Accepted; will add the missing Spec.'}
                                  for item in evidence['findings']]}
        write_json(self.root / 'response.json', response)
        self.assertOK(self.workflow('respond', '--scope', 'limit', '--responses', str(self.root / 'response.json')))

    def confirm(self, *args):
        return self.workflow('confirm', '--scope', 'limit', '--human', 'fixture', '--confirmation', 'reviewed', *args)

    def test_complete_mapping_report_and_gate(self):
        state = self.prepare_changed_product()
        self.review_and_respond(state, self.evidence(state))
        report = (self.root / 'reports/limit/design-review.md').read_text()
        self.assertIn(state['diff_inventory'][0]['location'], report)
        self.assertIn('reviews/api/limit.md#spec-01', report)
        self.assertIn('API-01', report)
        self.assertOK(self.confirm())
        self.assertEqual(read_json(self.state_file())['stage'], 'DESIGN_CONFIRMED')

    def test_gap_blocks_g1_even_after_a_acceptance_and_human_decision(self):
        state = self.prepare_changed_product()
        evidence = self.evidence(state)
        evidence['diff_coverage'][0].update(status='gap', spec_refs=[], finding_ids=['F-01'])
        evidence['findings'] = [{'finding_id': 'F-01', 'location': state['diff_inventory'][0]['location'],
                                 'basis': 'new rejection outcome absent from Spec', 'suggestion': 'add rule',
                                 'impact': 'unrepresented behavior'}]
        self.review_and_respond(state, evidence)
        result = self.confirm('--decision', 'accept everything')
        self.assertEqual(result.returncode, 1)
        self.assertIn('diff-to-Spec coverage incomplete', result.stderr)
        self.assertNotIn('approval', read_json(self.state_file()))
        # Preparing corrected design and obtaining a new B result reopens the normal gate.
        self.assertOK(self.workflow('prepare', '--scope', 'limit'))
        state = read_json(self.state_file())
        self.review_and_respond(state, self.evidence(state))
        self.assertOK(self.confirm())

    def test_slice_exclusion_needs_explicit_scope_decision(self):
        state = self.prepare_changed_product()
        evidence = self.evidence(state)
        evidence['diff_coverage'][0].update(status='out_of_scope', spec_refs=[],
                                           reason='Threshold changes excluded from this slice; next: threshold review.')
        self.review_and_respond(state, evidence)
        self.assertEqual(self.confirm().returncode, 1)
        self.assertEqual(read_json(self.state_file())['stage'], 'NEEDS_DECISION')
        self.assertOK(self.confirm('--decision', 'Confirm partial scope; threshold review remains outstanding.'))
        self.assertIn('[out_of_scope]', (self.root / 'reports/limit/design-review.md').read_text())

    def test_complete_cases_do_not_hide_missing_diff_accounting(self):
        state = self.prepare_changed_product()
        evidence = self.evidence(state)
        evidence['diff_coverage'] = []
        write_json(self.root / 'design.json', evidence)
        result = self.workflow('review', '--scope', 'limit', '--phase', 'design',
                               '--evidence', str(self.root / 'design.json'))
        self.assertEqual(result.returncode, 1)
        self.assertIn('diff coverage set mismatch', result.stderr)

    def test_raw_diff_cannot_be_truncated_before_prepare(self):
        self.prepare_changed_product()
        (self.root / 'reports/limit/product.diff').write_text('')
        result = self.workflow('prepare', '--scope', 'limit')
        self.assertEqual(result.returncode, 1)
        self.assertIn('raw diff changed', result.stderr)
        self.assertEqual(read_json(self.state_file())['stage'], 'STALE')

    def test_not_tested_spec_is_available_without_a_case(self):
        self.review.write_text(self.review.read_text() + '''
### SPEC-02：documented compatibility
Condition: legacy caller
Expected: compatibility preserved
Observable: same response
Basis: inputs/requirements.md
Source: explicit
Testing: not_tested — manual verification deferred
''')
        design = check_design(self.root, self.state['reviews'])
        self.assertEqual(design['errors'], [])
        self.assertIn('reviews/api/limit.md#spec-02', design['all_spec_refs'])
        state = self.prepare_changed_product()
        evidence = self.evidence(state)
        evidence['diff_coverage'][0]['spec_refs'] = ['reviews/api/limit.md#spec-02']
        self.review_and_respond(state, evidence)
        self.assertOK(self.confirm())

    def test_live_adapter_packet_contains_complete_diff_inventory(self):
        state = self.prepare_changed_product()
        evidence = self.evidence(state)
        metadata = {'isolation': 'isolation_unverified'}
        args = SimpleNamespace(phase='design', timeout=10, evidence=None, backend='codex', contract=None)
        with patch('pr_workflow.agent_adapters.invoke', return_value=(evidence, metadata)) as invoke:
            review(self.root, state, self.root / 'reports/limit', args)
        packet = read_json(self.root / 'reports/limit/design-input.json')
        self.assertEqual(packet['diff_inventory'], state['diff_inventory'])
        self.assertEqual(packet['all_spec_refs'], state['all_spec_refs'])
        prompt = invoke.call_args.args[3]
        self.assertIn('Start from every raw diff inventory unit', prompt)
        self.assertIn('diff_coverage', prompt)
