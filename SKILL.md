---
name: ai-test-agent
description: Design and validate standalone acceptance tests or requested security reviews with independent oracles, stable Case IDs and reproducible evidence. Use for case review, mapped-test maintenance or PR test impact; skip routine unit-test edits without review documents.
---

# AI Test Agent

Root `reviews/` centrally holds test intent; executable tests live under `suites/<suite>/`.
Case ID = Test Point ID. Preserve IDs; no duplicate case/status ledgers.

## Default: focused, compact

- Complete the requested scope. Do not automatically continue to the next interface outside it.
- Select review-only, authorized end-to-end, or full PR-v2 using [workflow](references/workflow.md).
  An explicit request to review, implement, validate and synchronize authorizes that sequence;
  do not insert repeated map/row confirmations. Keep unresolved business rules visible and continue
  independent work. End-to-end authorization does not imply independent review or production actions.
- Read project instructions and the matching reference. Locate rows and mappings with
  `check_test_map.py --json`, symbols with `rg`; reuse existing design.
- Ordinary cases, PR impact and maintenance use the compact path: no B, per-hunk accounting or
  full PR-v2 state unless requested or required. Existing `.ai-test-agent/`
  state alone is not a request; do not bypass an active scope's gate. Intent-preserving follow-up
  edits need no G1, B call, freeze or report. Compact work is not whole-PR acceptance.
- Use native runners, fixtures and style; isolated builds needed by authorized tests are allowed.
  Use bundled evidence tools instead of ad hoc hash/report scripts.
- Scope limits breadth, not test-tree depth. Split distinct observable outcomes; group variations
  sharing setup, action and oracle; mark unread branches with a resume point.
- Reviews require **Spec → 测试树 → 用例**. State oracle, entry, observation and verification layer
  outside the table; follow [verification quality](references/verification-quality.md).
- Run focused tests and both checkers once after changes; broaden only for affected shared
  dependencies. Bound network retries. Do not repeatedly poll CI or reread unchanged files.

## Review and implementation

Use [templates/test-review.md](templates/test-review.md), including all three sections even for
simple behavior. Keep its five-column Case table.

Rows state precondition/action and observable result. P0/P1/P2 denote blocker/important/edge.
Use `待确认：<decision>` for unresolved expectations. `[x]` means `TEST-MAP` exists, not a pass.

Review-only presents changed rows and stops. Authorized end-to-end self-reviews and implements
unambiguous Cases without another confirmation. Full PR-v2 retains B and human G1/G2.
Wording/checkbox edits retain confirmation. Read root feedback before Case revisions.

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
| Confirmed automation | [automation-maintenance](references/automation-maintenance.md) |
| PR impact / explicit full PR-v2 | [pr-analysis](references/pr-analysis.md) |
| Requested security audit / funds risk | [security-review](references/security-review.md) |

## Output budget

Default Markdown: scope/source in 1–3 lines, required Spec → 测试树 → 用例, actual open decisions.
Omit empty sections, N/A lists and tool logs. Edit in place; no summary files.

Chat handoff: changed IDs + result + next decision, normally at most 3 bullets. Link the document
instead of pasting it; G1 must still expose every changed row for review. For implementation include
one verification line (command, result, exit status); expand failures or material uncertainty only.
Added automation: group IDs sharing an oracle. Keep mapping, independent review and execution distinct.
