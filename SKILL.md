---
name: ai-test-agent
description: Design and validate standalone acceptance tests or requested security reviews with independent oracles, stable Case IDs and reproducible evidence. Use for case review, mapped-test maintenance or PR test impact; skip routine unit-test edits without review documents.
---

# AI Test Agent

Root `reviews/` centrally holds test intent; executable tests live under `suites/<suite>/`.
Case ID = Test Point ID. Preserve IDs; no duplicate case/status ledgers.

## Default: focused, compact

- Complete the requested scope through the two gates below. Do not automatically continue to the next interface.
- Use [workflow](references/workflow.md) for scope and authorization; end-to-end requests do not replace G1/G2 approvals.
- Read project instructions, affected rows/mappings and matching references; reuse existing design.
- Compact work includes B design review, not full PR-v2 accounting/state unless requested or required.
  Existing `.ai-test-agent/` state alone is not a request; preserve active gates. Intent-preserving
  follow-up edits need no G1, B call, freeze or report.
- Use native runners, fixtures and style; isolated builds needed by authorized tests are allowed.
  Use bundled evidence tools instead of ad hoc hash/report scripts.
- Scope limits breadth, not test-tree depth. Split distinct observable outcomes; group variations
  sharing setup, action and oracle; mark unread branches with a resume point.
- Reviews require **Spec → 测试树 → 用例**. State oracle, entry, observation and verification layer
  outside the table; follow [verification quality](references/verification-quality.md).
- Run focused tests and both checkers once after changes; broaden only for affected shared
  dependencies. Bound network retries. Do not repeatedly poll CI or reread unchanged files.

## Review and implementation

Use [templates/test-review.md](templates/test-review.md), including all three sections and its five-column Case table.

Rows state precondition/action and observable result. P0/P1/P2 denote blocker/important/edge.
Use `待确认：<decision>` for unresolved expectations. `[x]` means `TEST-MAP` exists, not a pass.

Follow [workflow-gates](references/workflow-gates.md):
1. **G1 — documents:** finish every selected test-point document, complete independent B review and
   address findings, then stop for the user's review. No automation yet.
2. **G2 — first case:** after G1 approval, implement only the first representative automated Case;
   show its code and focused check result, then stop for the user's standards confirmation.
After G2 approval, implement, run and repair the remaining confirmed Cases automatically. No per-Case
approval or final human gate. Case-review-only requests end at G1. Read root feedback before revisions.

Implement direct, readable tests; avoid abstraction that hides assertions which prove the expected behavior.
Use one `TEST-MAP: <CASE-ID>` per native comment and synchronize affected checkboxes.
Python tests: mapping above definition; numbered Chinese docstring steps; matching numbered code-block comments.
See the [format](references/automation-maintenance.md#test-comment-format).
Run `scripts/check_test_design.py --review <path>` for structural links and
`scripts/check_test_map.py --review <path>` after automation for mapping. Migrate selected legacy
reviews for material Case changes, not unrelated reviews.
Never weaken expectations or change product code just to pass tests.
`TEST-MAP` proves association only. Runner outcomes do not prove the asserted security property.
Use [execution evidence](references/execution-evidence.md) for requested results; unsupported counts
stay unknown. Never award yourself independent B review.

## Read only the needed route

| Request | Reference |
| --- | --- |
| Help; no target | [help](references/help.md); no repository inspection |
| Initialize / migrate | [initialize](references/initialize.md) |
| Add / revise cases | [review-cases](references/review-cases.md) |
| Implement / maintain automation | [automation-maintenance](references/automation-maintenance.md) |
| PR impact / explicit full PR-v2 | [pr-analysis](references/pr-analysis.md) |
| Requested security audit / funds risk | [security-review](references/security-review.md) |

## Output budget

Default Markdown: scope/source in 1–3 lines, required Spec → 测试树 → 用例, actual open decisions.
Omit empty sections, N/A lists and tool logs. Edit in place; no summary files.

Chat handoff: changed IDs + result + next decision, at most 3 bullets. Link documents;
G1 still exposes every changed row. Include verification (command, result, exit status);
expand failures or material uncertainty only.
Added automation: group IDs sharing an oracle. Keep mapping, independent review and execution distinct.
