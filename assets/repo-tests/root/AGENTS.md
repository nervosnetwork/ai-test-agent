# {{PROJECT_NAME}} Test Project

## Target

- Source: {{SOURCE_REPOSITORY}}
- Checkout: `source/{{PROJECT_SLUG}}/`
- Revision and entry points: [fill after discovery]; stable commands: suite READMEs.

{{TEST_LAYOUT_DESCRIPTION}}

{{SUITE_LIST}}

## Workflow

Follow `docs/ai-test-agent/workflow.md` for scope and authorization; reuse completed confirmations.
`workflow-gates.md` defines two human stops: finish all selected documents and independent B review,
address findings, then present G1 for design review. After approval, implement only the first Case
and present G2 for standards confirmation. Then finish remaining confirmed Cases, runs and fixes
without per-Case or final human gates. End-to-end scope authorization is not either gate's approval.
Map-only requests stop at the map; unknown business rules block dependent Cases only.

Use `templates/test-review.md`: Spec → 测试树 → 用例, sourced rules, linked leaves and stable IDs.
Scope limits breadth, not test-tree depth. Keep unread branches and resume points explicit; use
`docs/ai-test-agent/decomposition.md` as needed. Migrate only selected legacy reviews for material
changes. Preserve `用例 | 场景 | 预期结果 | 防止的问题 | 优先级`; `[x]` means TEST-MAP only.
Write `待确认：<decision>` for unresolved expectations; paths/logs stay outside rows.

State the independent oracle, actual entry, fresh observation and verification layer outside the
table; see `docs/ai-test-agent/verification-quality.md`. Implement direct, readable tests; avoid
abstraction hiding assertions which prove the expected behavior. Security negatives keep signatures
and prerequisites valid until the intended checker. Requested audits use `security-review.md` and
`templates/security-review.md`: assets, authority, invariants and attack paths.

Use native runners, fixtures and style; isolated builds required by authorized tests are allowed.
Never weaken expectations or change product code to pass. No production action is implied.
Intent-preserving follow-up edits need no G1, B call, freeze or report.
Use one `TEST-MAP: <CASE-ID>` per native comment; update affected mappings and checkboxes.
Python mappings precede definitions; numbered Chinese docstring steps match code-block comments.
See `docs/ai-test-agent/automation-maintenance.md#test-comment-format`.

Read root `reviews/review-feedback.md` before revisions. Append only human corrections:
`- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>`.
Preserve wording, collapse line breaks and escape `|`; this is not a case status or approval ledger.

## Full PR-v2

Use `docs/ai-test-agent/pr-analysis.md` when requested or required. Existing `.ai-test-agent/`
state alone is not a request; never downgrade an active scope to bypass gates. Preserve B design
review, diff→Spec accounting, A responses and G1. After first-Case G2, coverage review and execution
continue automatically. Use `templates/test-review-full.md`, `test-design.md`, `coverage-review.md`
and `agent-adapters.md`. Transport testing is not host-attested independence.

## Verify

Run focused tests and `scripts/check_test_design.py --review <path>` plus
`scripts/check_test_map.py --review <path>` once per batch; broaden only for shared impact.
No repeated CI polling. Use `docs/ai-test-agent/execution-evidence.md` for requested native receipts.
Mapping, execution and behavior proof remain separate; unsupported outcomes stay unknown.
Keep current derived `reports/<scope>/` and disposable `.ai-test-agent/current/<scope>/` state.
Report changed IDs, command/result/exit status and open decisions; no duplicate ledgers.
