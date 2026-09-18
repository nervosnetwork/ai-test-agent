# {{PROJECT_NAME}} {{SUITE_LABEL}} Test Instructions

Read root `../../AGENTS.md`; this file routes suite work.

- Focus: {{SUITE_FOCUS}}.
- Reviews: root `../../reviews/`; executable areas: {{CODE_DIRS}}; reusable inputs: `fixtures/`.
- Read root corrective feedback before case changes.
- Keep globally unique Case IDs, nearby `TEST-MAP` comments and matching scenario checkboxes.
- After confirmation, implement direct, readable tests; add abstraction only without hiding assertions that prove the expected behavior.
- B checks actual code and all selected Cases; gaps belong in current derived reports. B never changes expectations. Only validated managed evidence comments may be rendered automatically.
- Verify focused commands and `python3 ../../scripts/check_test_map.py`. Preserve native runner selectors and parameter instances.
- No automatic next-document work or repeated CI polling. Mapping, semantic coverage and execution are separate.
