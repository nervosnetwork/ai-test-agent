# {{PROJECT_NAME}} Test Project Instructions

This is the canonical project instruction file.

## Target

- Source repository: {{SOURCE_REPOSITORY}}
- Local checkout: `source/{{PROJECT_SLUG}}/`
- Default revision: [branch, tag, or commit]
- Test objects and entry points: [fill after discovery]
- Stable setup, focused-test, and full-test commands: [fill after integration]

{{TEST_LAYOUT_DESCRIPTION}}

Initialized approaches: {{SUITE_TYPES}}.

{{SUITE_LIST}}

## Workflow

Work on one interface or review document and one gate at a time. Do not automatically advance to the next area.

1. Write or materially revise reviewer-facing rows.
2. Present the complete changed row set and stop before changing automated tests.
3. Wait for explicit confirmation.
4. Implement only confirmed cases with direct, readable tests and `TEST-MAP: <CASE-ID>` comments. Add an abstraction only when it removes meaningful repetition without hiding the assertions that prove the expected behavior.
5. Run the focused command and `python3 scripts/check_test_map.py`. Run a broader suite only when justified; inspect CI once rather than polling it.

Split larger scopes coherently instead of omitting behavior. Group related fields proved by the same operation and oracle.

## Review rows

```markdown
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | - [ ] [scenario] | [observable result] | [problem prevented] | P0 |
```

- Use globally unique stable IDs and plain product language.
- Preserve an ID when editing the same behavior.
- Use `待确认：<decision>` for ambiguity.
- Prefix each scenario with `- [ ]` when it has no mapped automation or `- [x]` when its `TEST-MAP` exists. New rows start unchecked.
- Do not add approval, coverage, any other automation-status field, paths, implementation plans, or run history to the table.

## Feedback and mapping

Read root `reviews/review-feedback.md` before revising cases. On corrective feedback, append:

```text
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>
```

Preserve the wording, collapse line breaks, escape `|` as `\|`, and do not record approval without a correction. This is learning feedback, not a case status or approval ledger.

Map each automated case with one nearby `TEST-MAP: <CASE-ID>` comment. Keep the scenario checkbox synchronized when mappings are added or removed. Coverage is computed from code; the checkbox is a visible projection, not a mapping ledger.

## Efficiency and handoff

- Read targeted source ranges and affected files; avoid repository dumps and repeated unchanged reads.
- Prefer one focused deterministic run. Bound live-network retries and report repeated unavailability as residual risk.
- Group automation explanations by shared reason and oracle; expand only changed, failed, ambiguous, or high-risk cases.
- Report changed IDs, coverage, literal verification result/exit status, residual risk, and the exact next gate. Do not repeat unchanged tables.

Keep stable commands current in the relevant README. Do not create per-PR reports, run archives, approval histories, or status ledgers.
