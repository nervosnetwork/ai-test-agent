# Confirmed automation and maintenance

1. Reuse project instructions, source checkout, affected rows and all corresponding `TEST-MAP` sites.
   If case intent changes, update rows and stop at G1 before editing mapped automation.
2. Implement direct, readable tests with native runners/fixtures. Avoid abstraction that hides
   assertions which prove the expected behavior. Keep setup/action/oracle visible; group shared setup.
3. Synchronize all affected inputs, actions, assertions, mappings and scenario checkboxes. Remove obsolete
   mappings after merges/deletions. Wording-only changes need alignment inspection, not automatic rewrites.
4. Run focused deterministic tests and `check_test_map.py --review <path>` once after the batch. Broaden
   for affected shared dependencies, not by default. Bound live-network retries; inspect CI once.

Report changed IDs, command/result/exit status and any actual gap or next decision. Mapping presence
is not assertion coverage or execution. Avoid per-case success explanations and extra summary files.
Never weaken expectations or modify product code merely to turn a run green.

Follow-up renames, moves, style cleanups and runner fixes that keep intent and assertions stay on this
compact path even inside a PR-v2 scope: no G1, B call, freeze or report. Edit, run focused tests, hand off.

For ordinary PR impact use the compact route in `pr-analysis.md`. For an active or explicitly requested
full PR-v2 scope, follow `coverage-review.md` after G1: freeze implementation, independent B evidence,
managed comments, frozen execution and G2. Changed design returns to G1; changed test dependencies
return to B. Compact work never claims independent review.
