# Execution evidence

Keep three questions separate: is a Case associated with code, what did a native runner report,
and do the assertions actually establish the intended behavior? `TEST-MAP`, a successful process
and a proof of a funds invariant answer different questions. Use `verification-quality.md` for the last.

`check_test_map.py` prints **case mappings**. JSON adds `mapped`, `unmapped`, `mapped_case_count`
and `mapping_ratio`; legacy `automated*`/`automation_coverage` fields remain compatibility aliases
for association only. `execution` and `behavior_verification` are explicitly `not_checked`.
`--require-complete` still requires associations, not passing tests or automated manual review.

## Compact native receipt

For requested execution evidence, run the actual project command with the bundled wrapper. No B
dispatch, full-workflow state, handwritten counts or Case-pass ledger is required. For example:

```sh
python3 scripts/run_with_evidence.py --root . --product source/product --scope withdrawal \
  --input suites/api/tests/test_withdrawal.py --input requirements.txt --junit \
  -- python3 -m pytest suites/api/tests/test_withdrawal.py '--junitxml={junit}'
```

`{junit}` is replaced in argv with an absolute fresh report path inside `reports/<scope>/`.
The native command must write JUnit XML; the wrapper does not translate console prose into counts.
Without `--junit`, record command/log/exit status and leave test outcomes unknown. No shell is
inserted. Use an isolated project runner for additional runtime/environment needs; the wrapper
forwards only standard process/locale/temp environment keys, not model or production credentials.

The generated `execution.json` and `execution.log` contain actual argv/cwd, timestamps/duration,
exit status, wrapper runtime/platform, product commit and tracked/untracked changes, declared test-input
hashes, log/report hashes and native testcase outcomes. Declare shared fixtures, runner/build config
and lockfiles with repeated `--input`; no automatic complete dependency closure is claimed.
The product must be a Git checkout. Keep outputs outside it or ignored, so they do not change the
product being measured. Ignored build artifacts and real deployed binaries require separate identity
evidence; a source SHA alone does not identify them.

JUnit counts describe reported testcase records, not unique review Cases or proof that each test
body reached a particular line. Parameterized records remain distinct; skips and errors remain visible.
Zero tests, all skips, malformed/missing reports, report failures despite exit 0, timeout, or detected
input drift yield a nonzero wrapper status. A command without a supported report remains suite-level
even at exit 0. Duplicate native selectors are marked ambiguous; no per-Case credit is inferred.

Each scope retains only its current derived receipt; a run clears its owned old native report before
launch, preventing a stale success from being reused. A receipt cannot overwrite an active PR-v2 scope.
The wrapper does not claim independent semantic review, complete coverage or production acceptance.

## Full PR-v2

Keep using `pr_workflow.py run` and `coverage-review.md`. Its frozen inputs, runner selector manifest,
independent B and human gates remain required; a compact receipt cannot satisfy those gates.
