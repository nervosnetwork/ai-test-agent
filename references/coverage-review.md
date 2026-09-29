# B coverage, comments and execution

## Inputs and semantic review

A freezes implementation with `pr_workflow.py implemented --scope <scope>` after G1 and checkbox sync.
B receives all selected Cases, confirmed Spec, actual test/helper/fixture code, necessary product paths
and available execution outputs. B must inspect code, not only TEST-MAP, test names or A explanations.
For every Case explain real setup, triggered path, new observation, effective assertions and limits.
Check mocks, waits, retries, swallowed exceptions, stale observations, tautologies and runner collection.
Performance needs workload/metric/threshold/conditions; fuzz needs input domain, seeds/budget and actual
results. A finite run never establishes all-input coverage.

Use `schemas/coverage.schema.json` for the evidence envelope, scope/input fingerprint, reviewer and
all Case records. Bindings use file, qualified symbol, runner selector, optional concrete parameter
selectors, setup/trigger/observation, located assertions and missing checks. `limitations` remain visible.
The script verifies structure and literal code locations; it cannot establish assertion semantics.

```sh
python3 scripts/pr_workflow.py review --scope <scope> --phase coverage --backend <codex|claude>
python3 scripts/pr_workflow.py annotate --scope <scope>
python3 scripts/pr_workflow.py run --scope <scope> --timeout 120
python3 scripts/pr_workflow.py continue --scope <scope>
python3 scripts/check_test_evidence.py --scope <scope> --require-reviewed --json
```

## Four independent dimensions

- Mapping exists: code scan; controls the old checkbox only.
- B coverage: `covered`, `partial`, `missing`, `uncertain`.
- Validity: `current`, `stale`, `not_reviewed`.
- Actual execution: `passed`, `failed`, `skipped`, `not_run`, `blocked`, plus `unstable`.

Covered needs specific assertions and no known binding gaps. Missing implementation has no binding
but always appears in the report. Parameter selectors identify actual instances; function-level success
does not cover unexecuted parameters. Multiple mappings may jointly establish one Case; explain them.

## Single-source annotations

Both report and comments are rendered from B's structured record. Python managed blocks use
`# TEST-EVIDENCE-BEGIN/END: <ID>` and `# Evidence | ...` content. Existing unmanaged comments,
pragma directives, collection decorators, doctests and executable code are preserved byte-for-byte
outside those blocks. Python AST and token checks validate each render before any write. Repeat renders
are idempotent. Unsupported languages produce `annotation-proposals.json` for a language-aware human
review; they are never auto-edited or advertised as validated comment-only changes.

Comments explain stable verification, not a last-passed timestamp, model name or embedded source hash.
If code lacks an assertion, describe the gap, never an imaginary check. B input snapshot and final
execution snapshot are separate; a receipt records verified managed-comment changes. All other changes
return to B. Product head, semantic design, tests, dependencies, fixtures and config invalidate scope
results conservatively. Re-run `implemented` after fixing tests without changing confirmed intent;
material design changes return to G1. Do not weaken assertions, loosen thresholds, skip failing tests
or patch product code merely to make the result green.

## Execution and G2

The command/cwd are fixed in the manifest. Tests receive a minimal environment without model keys,
production secrets or real wallet assets. Add a project-specific isolated runner for extra environment
needs. The bundled `run_unittest.py` records exact native test IDs and subtest parameter selectors plus
a runner-produced selector-to-file/symbol manifest to `AI_TEST_AGENT_RESULT`; per-Case credit requires
that manifest to match B's reviewed binding. Other commands without a supported result record remain suite-level.
No per-Case pass is inferred from process exit 0. Zero collection, all skips, timeout, parsing errors,
missing selectors, input mutation and unstable duplicate outcomes do not count as acceptance.
Full output, command, environment key names, product revision, duration and exit status are saved.
Suspected product failures, test defects, environment failures and unstable results need explicit triage;
the generic runner leaves unknown causes `unclassified` rather than guessing.

`coverage.md` starts from the selected Case set, gap-first, then offers code evidence. P0 and explicit
`--require-case` Cases need current covered evidence and corresponding stable pass results. Current
implementation conservatively routes **any** remaining gap, unverified B or unresolved decision to G2;
it has no automated risk-waiver service. Human-accepted deferrals must remain visible and do not turn
missing into covered. Read `acceptance.json` through a trusted external operator/CI entry if strong
control is needed. `ready_for_acceptance` means ready for human acceptance, never automatic PR merge.

Sample covered/high-risk Cases as well as B-reported gaps. Optional local fault injection or old-fails /
new-passes checks can assess oracle quality when appropriate. They are not default production actions.
