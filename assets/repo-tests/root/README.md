# {{PROJECT_NAME}} Tests

This repository owns human-reviewed test intent and mapped automation for `{{PROJECT_NAME}}` independently from the product source repository.

## Layout

{{TEST_LAYOUT_DESCRIPTION}}

{{SUITE_LIST}}

- `source/{{PROJECT_SLUG}}/`: ignored local checkout of the tested product.
- `scripts/check_test_map.py`: computes automation coverage from `TEST-MAP` comments.
- `templates/test-review.md`: reviewer-first case-table template.

## Review and Implementation

1. Inspect target behavior and write or revise the complete case rows.
2. Present the changed rows for human review and stop.
3. After explicit confirmation, implement tests with `TEST-MAP: <CASE-ID>` comments.
4. Keep added tests direct and readable; avoid abstractions that do not clearly improve maintenance.
5. Run focused tests and the mapping checker, then explain why each test was added and how its assertions prove the expected behavior.

Review documents do not store approval or automation statuses. Corrections directly update the relevant row while preserving its ID.

Corrective human feedback is appended to the affected `reviews/review-feedback.md` and read before later case analysis. Approval without a requested correction is not recorded.

## Stable Commands

{{COMMANDS_BLOCK}}

Mapping check:

```bash
python3 scripts/check_test_map.py
```

Require every review case to have code mapping:

```bash
python3 scripts/check_test_map.py --require-complete
```
