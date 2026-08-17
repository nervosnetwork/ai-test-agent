# {{PROJECT_NAME}} {{SUITE_LABEL}} Test Instructions

Read and follow root `../../AGENTS.md`. This file contains only {{SUITE_LABEL}}-specific routing.

## Scope

- Focus: {{SUITE_FOCUS}}.
- Review documents: `reviews/`.
- Executable areas: {{CODE_DIRS}}.
- Shared or reusable inputs: `fixtures/`.

## Workflow

1. Read root instructions, this file, the affected review document, and this suite's README.
2. Read `reviews/review-feedback.md` when it exists and apply relevant prior corrections.
3. Create or materially revise review rows before touching tests.
4. Present the complete changed row set and stop for explicit human confirmation.
5. Record corrective feedback using the root format, update the rows, and present material changes again.
6. After confirmation, implement automation under {{CODE_DIRS}} with `TEST-MAP: <CASE-ID>` comments.
7. Run the focused suite command and `python3 ../../scripts/check_test_map.py --root ../..`.

Keep case IDs globally unique across the test project. Do not add status columns or a separate automation mapping document.
