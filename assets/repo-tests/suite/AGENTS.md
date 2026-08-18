# {{PROJECT_NAME}} {{SUITE_LABEL}} Test Instructions

Read root `../../AGENTS.md`; this file only routes suite-specific work.

- Focus: {{SUITE_FOCUS}}.
- Reviews: `reviews/`; executable areas: {{CODE_DIRS}}; reusable inputs: `fixtures/`.
- Read `reviews/review-feedback.md` when present.
- Keep case IDs globally unique and map tests with `TEST-MAP: <CASE-ID>`.
- After confirmation, implement direct, readable tests; add an abstraction only when it improves readability without hiding behavior or assertions that prove the expected behavior.
- Verify with the focused suite command and `python3 ../../scripts/check_test_map.py --root ../..`.
- Do not advance to another review document automatically or poll CI repeatedly.
