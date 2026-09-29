# {{PROJECT_NAME}} Tests

This repository stores human-reviewed test intent and automation mapped by `TEST-MAP: <CASE-ID>`.

{{TEST_LAYOUT_DESCRIPTION}}

{{SUITE_LIST}}

- `source/{{PROJECT_SLUG}}/`: ignored product checkout.
- `reviews/`: centralized behavior tables for every suite.
- `suites/<suite>/`: module-owned executable automation, commands, and fixtures.
- `scripts/check_test_map.py`: computed mapping coverage.

Work on one review document at a time: present changed rows, stop for confirmation, implement confirmed cases, then run a focused test and the mapping checker. Stable commands follow.

{{COMMANDS_BLOCK}}

```bash
python3 scripts/check_test_map.py
python3 scripts/check_test_map.py --require-complete  # only for intentionally complete scope
```

## PR v2

Keep change summary, Spec and test tree with the unique Case table. Independent B reviews design
before human confirmation, then actual test assertions before final execution. Start with
`docs/ai-test-agent/pr-analysis.md`. Current derived reports go in ignored `reports/<scope>/`;
input/gate state goes in ignored `.ai-test-agent/current/<scope>/`. No automatic product merge.

```bash
python3 scripts/check_test_design.py --review reviews/<area>/<behavior>.md
python3 scripts/check_test_evidence.py --scope <scope> --require-reviewed
```
