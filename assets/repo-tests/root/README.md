# {{PROJECT_NAME}} Tests

This repository stores test intent and automation mapped by `TEST-MAP: <CASE-ID>`.

{{TEST_LAYOUT_DESCRIPTION}}

{{SUITE_LIST}}

- `source/{{PROJECT_SLUG}}/`: ignored product checkout.
- `reviews/`: centralized behavior tables for every suite.
- `suites/<suite>/`: module-owned executable automation, commands, and fixtures.
- `scripts/check_test_map.py`: Case-to-code association only.
- `scripts/run_with_evidence.py`: requested native execution receipts without PR-v2 setup.

Use exactly two human gates (`docs/ai-test-agent/workflow-gates.md`):
1. Finish all selected Spec → 测试树 → 用例 documents and independent B review; stop at G1 for design review.
2. After approval, implement and check only the first Case; stop at G2 for standards confirmation.
Then finish the remaining automation, focused runs and fixes automatically, with no final approval gate.
Case-review-only requests end at G1. Run both checkers once per changed batch. Stable commands follow.

{{COMMANDS_BLOCK}}

```bash
python3 scripts/check_test_design.py --review reviews/<area>/<behavior>.md
python3 scripts/check_test_map.py
python3 scripts/check_test_map.py --require-complete  # only for intentionally complete scope
```

Mapping, native runner outcomes and proof of the intended behavior are separate facts. Use
`docs/ai-test-agent/execution-evidence.md` for a compact receipt, and `security-review.md` for
requested assets/authority/attack-path review. An injected wallet or host rejection is not proof
of a real-node funds flow or validator rejection.

## PR v2 (explicit opt-in or existing project requirement)

Keep change summary, Spec and test tree with the unique Case table. Independent B reviews design
before G1, then actual test assertions automatically after first-Case G2 approval. Start with
`docs/ai-test-agent/pr-analysis.md`. Current derived reports go in ignored `reports/<scope>/`;
input/gate state goes in ignored `.ai-test-agent/current/<scope>/`. No automatic product merge.

```bash
python3 scripts/check_test_design.py --review reviews/<area>/<behavior>.md
python3 scripts/check_test_evidence.py --scope <scope> --require-reviewed
```
