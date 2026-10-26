# {{PROJECT_NAME}} Tests

This repository stores reviewable test intent and automation associated by `TEST-MAP: <CASE-ID>`.

{{TEST_LAYOUT_DESCRIPTION}}

{{SUITE_LIST}}

- `source/{{PROJECT_SLUG}}/`: ignored product checkout.
- `reviews/`: centralized behavior tables for every suite.
- `suites/<suite>/`: module-owned executable automation, commands, and fixtures.
- `scripts/check_test_map.py`: Case-to-code association only.
- `scripts/run_with_evidence.py`: requested native execution receipts without PR-v2 setup.

Write Spec → 测试树 → 用例 and independent verification design, then validate links. For review-only
work present changes and stop; for an authorized end-to-end request self-review and implement the
unambiguous Cases, run focused verification and synchronize as requested. Unknown business rules
block dependent Cases only. See `docs/ai-test-agent/workflow.md`; full PR-v2 gates remain separate.
Stable commands follow.

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

## PR v2

Keep change summary, Spec and test tree with the unique Case table. Independent B reviews design
before human confirmation, then actual test assertions before final execution. Start with
`docs/ai-test-agent/pr-analysis.md`. Current derived reports go in ignored `reports/<scope>/`;
input/gate state goes in ignored `.ai-test-agent/current/<scope>/`. No automatic product merge.

```bash
python3 scripts/check_test_design.py --review reviews/<area>/<behavior>.md
python3 scripts/check_test_evidence.py --scope <scope> --require-reviewed
```
