# {{PROJECT_NAME}} Test Project Instructions

This file is the canonical instruction source for the standalone test project.

## Purpose

- Keep test intent easy for humans to review.
- Keep executable tests independent from the product source repository.
- Use one stable reviewer-facing case ID, such as `RPC-01`, from review row to test code.
- Derive automation coverage from code rather than storing statuses or mapping ledgers.

## Test Target

- Source repository: {{SOURCE_REPOSITORY}}
- Local source checkout: `source/{{PROJECT_SLUG}}/`
- Default revision: [branch, tag, or commit]
- Test objects: [services, interfaces, protocols, components, or binaries]
- Stable entry points: [commands, endpoints, configuration, or public APIs]
- Reference material: [repo-relative documents or stable specifications]

Keep stable shared facts here. Keep behavior-specific cases in review documents.

## Layout

{{TEST_LAYOUT_DESCRIPTION}}

Initialized approaches: {{SUITE_TYPES}}.

{{SUITE_LIST}}

## Human Review Contract

Use one review document per coherent interface or behavior. Keep the main table exactly:

```markdown
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | [scenario] | [observable result] | [concrete problem prevented] | P0 |
```

- Keep each row self-contained and use plain product language.
- Use globally unique case IDs. The review case ID is the only Test Point ID.
- Preserve IDs when correcting wording, expectation, or priority.
- Directly edit or remove obsolete rows; do not add approval, coverage, or automation statuses.
- Do not place test paths, implementation plans, internal ID chains, or run history in review tables.
- Use `待确认：<decision>` when behavior is ambiguous and call it out below the table.

## Mandatory Review Gate

For every new, deleted, or materially changed review row:

1. Update the complete reviewer-facing row set.
2. Present it and stop before changing automated tests.
3. Wait for explicit human confirmation.
4. Apply corrections and present material expectation changes again.
5. Generate or update mapped test code only after confirmation.

Do not combine review and implementation in one handoff. Existing unchanged rows remain eligible for implementation. Keep confirmation conversational rather than adding document statuses.

## Review Feedback

Before creating or revising cases, read the relevant `reviews/review-feedback.md` when it exists.

When a human corrects AI-authored cases—missing or unnecessary cases, scenario or expectation errors, priority changes, merges, splits, renames, or deletions—append one physical line to the affected review directory's `review-feedback.md`:

```text
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>
```

Create the file on the first correction. Preserve the feedback wording, collapse line breaks to spaces, and escape literal `|` characters as `\|`. Do not record approval without a correction. The file is reusable analysis feedback, not a case status, approval ledger, resolution log, or execution history.

## Automation Mapping

Every mapped automated test has one nearby native-language comment whose payload is exactly:

```text
TEST-MAP: <CASE-ID>
```

The scenario and oracle belong in the review row and assertions, not in the mapping comment. Run:

```bash
python3 scripts/check_test_map.py
```

The checker computes mapped and unmapped cases, duplicate review IDs, and orphan code mappings. Do not write computed automation results back into review documents.

Keep supplemental tests simple, readable, and easy to maintain. Prefer a direct arrange-act-assert flow and the target's existing fixtures. Add abstractions such as helpers, wrappers, builders, shared setup, or parameterization only when they remove meaningful repetition without hiding the behavior or oracle. Assert the smallest set of caller-observable results, state changes, side effects, or errors that proves the review row; avoid incidental implementation details and tautological checks.

## Source Workspace

- Reuse a matching checkout under `source/{{PROJECT_SLUG}}/`.
- Clone the declared repository only when the path is absent.
- Do not overwrite a conflicting path.
- Product source is long-lived local data excluded by `.gitignore`.
- For PR work, inspect the base/head diff first and read wider context only as needed.

## Maintenance

- Read the affected review document before changing tests.
- Read relevant prior corrective feedback before analyzing coverage.
- Find mapped code with `TEST-MAP: <CASE-ID>`; do not create a separate mapping ledger.
- Update review rows first when product behavior changes, then stop for the mandatory review gate.
- After confirmation, update automation, run focused tests, and run the mapping checker.
- For every added or materially changed automated case, report why it was needed and how its observable assertions prove the expected behavior.
- Keep setup, full-run, and focused-run commands current in the relevant README.
- Do not create per-PR report directories, status histories, approval ledgers, or result archives.

## Handoff

Report only relevant fields:

```text
Review scope: <area, interface, behavior, or PR>
Changed cases:
- <ID> [P0/P1/P2] <scenario> -> <expected result>
Added automation:
- <ID>: why <specific behavior or regression risk>; assertions <observable result/state/error checked and why it proves the expectation>
Automation coverage: <mapped>/<reviewed>; unmapped: <IDs or none>
Verification: <command> -> <result and exit status>
Residual risk: <ambiguous, manual, unobservable, or none>
Needs review: <exact product decision or none>
Next gate: <review confirmation required before implementation, or next implementation action>
```

Omit irrelevant sections rather than printing placeholder fields.
