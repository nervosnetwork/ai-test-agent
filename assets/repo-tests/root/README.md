# {{PROJECT_NAME}} Tests

This repository stores human-reviewed test intent and automation mapped by `TEST-MAP: <CASE-ID>`.

{{TEST_LAYOUT_DESCRIPTION}}

{{SUITE_LIST}}

- `source/{{PROJECT_SLUG}}/`: ignored product checkout.
- `reviews/`: concise behavior tables.
- `scripts/check_test_map.py`: computed mapping coverage.

Work on one review document at a time: present changed rows, stop for confirmation, implement confirmed cases, then run a focused test and the mapping checker. Stable commands follow.

{{COMMANDS_BLOCK}}

```bash
python3 scripts/check_test_map.py
python3 scripts/check_test_map.py --require-complete  # only for intentionally complete scope
```
