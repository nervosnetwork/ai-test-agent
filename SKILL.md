---
name: ai-test-agent
description: Maintain standalone test projects with concise review cases, stable Case IDs and TEST-MAP automation. Use for case review, mapped-test maintenance or PR test impact; skip routine unit-test edits without review documents.
---

# AI Test Agent

Root `reviews/` centrally holds test intent; executable tests live under `suites/<suite>/`.
Case ID = Test Point ID. Preserve IDs; no duplicate case/status ledgers.

## Default: focused, compact

- Complete the requested scope and current gate. Do not automatically continue to the next interface.
- Read project instructions and the matching reference. Locate rows and mappings with
  `check_test_map.py --json`, symbols with `rg`; reuse existing design.
- Ordinary cases, PR impact and maintenance use the compact path: no B, snapshots, per-hunk
  accounting or reports unless full PR-v2 is requested or required. Existing `.ai-test-agent/`
  state alone is not a request; do not bypass an active scope's gate. Intent-preserving follow-up
  edits need no G1, B call, freeze or report. Compact work is not whole-PR acceptance.
- Use the project's runner, fixtures and style. No ad hoc scripts for hashes, manifests, reports or
  annotations; no product builds, run harnesses or other-language edits unless requested.
- Scope limits breadth, not test-tree depth. Split distinct observable outcomes; group variations
  sharing setup, action and oracle; mark unread branches with a resume point.
- Every selected review requires **Spec → 测试树 → 用例** in one document, including compact work:
  sourced rules, linked testable leaves, and Case scenarios/oracles.
- Run focused tests and both checkers once after changes; broaden only for affected shared
  dependencies. Bound network retries. Do not repeatedly poll CI or reread unchanged files.

## Review and implementation

Use [templates/test-review.md](templates/test-review.md), including all three sections even for
simple behavior. Keep its five-column Case table.

Rows state precondition/action and observable result. P0/P1/P2 denote blocker/important/edge.
Use `待确认：<decision>` for unresolved expectations. `[x]` means `TEST-MAP` exists, not a pass.

For material Case changes, present every changed row and stop at G1. Generate or update mapped tests only after
explicit human confirmation. Do not combine review and implementation in one handoff.
Wording/checkbox-only edits retain confirmation. Read root feedback before Case revisions.

Implement direct, readable tests; avoid abstraction that hides assertions which prove the expected behavior.
Use one `TEST-MAP: <CASE-ID>` per native comment, inspect all affected mappings and synchronize checkboxes.
Python tests: mapping above definition; numbered Chinese docstring steps; matching numbered code-block comments.
See the [format](references/automation-maintenance.md#test-comment-format).
Run `scripts/check_test_design.py --review <path>` for structural links and
`scripts/check_test_map.py --review <path>` after automation for mapping. Migrate selected legacy
reviews for material Case changes, not unrelated reviews.
Never weaken expectations or change product code just to pass tests.

## Read only the needed route

| Request | Reference |
| --- | --- |
| Help; no target | [help](references/help.md); no repository inspection |
| Initialize / migrate | [initialize](references/initialize.md) |
| Add / revise cases | [review-cases](references/review-cases.md) |
| Confirmed automation | [automation-maintenance](references/automation-maintenance.md) |
| PR impact / explicit full PR-v2 | [pr-analysis](references/pr-analysis.md) |

## Output budget

Default Markdown: scope/source in 1–3 lines, required Spec → 测试树 → 用例, actual open decisions.
Omit empty sections, N/A lists and tool logs. Edit in place; no summary files.

Chat handoff: changed IDs + result + next decision, normally at most 3 bullets. Link the document
instead of pasting it; G1 must still expose every changed row for review. For implementation include
one verification line (command, result, exit status); expand failures or material uncertainty only.
Added automation: group IDs sharing an oracle. Keep mapping, independent review and execution distinct.
