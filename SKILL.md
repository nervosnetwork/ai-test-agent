---
name: ai-test-agent
description: Maintain standalone test projects with concise review cases, stable Case IDs and TEST-MAP automation. Use for case review, mapped-test maintenance or PR test impact; skip routine unit-test edits without review documents.
---

# AI Test Agent

Root `reviews/` centrally holds test intent; executable tests live under `suites/<suite>/`.
Case ID = Test Point ID. Preserve IDs; no duplicate case/status ledgers.

## Default: focused, compact

- Complete the requested scope and current gate. Do not automatically continue to the next interface.
- Read project instructions, then only the matching reference below. Locate relevant rows, mappings,
  feedback and source ranges before reading (`check_test_map.py --json` lists row/mapping locations;
  `rg` for symbols); reuse unchanged inputs and existing design.
- Ordinary case edits, PR impact and mapped maintenance use the compact path. Do not start B agents,
  frozen snapshots, per-hunk accounting or evidence reports unless full PR-v2 is explicitly requested
  or required by project instructions. Existing `.ai-test-agent/` state alone is not a request; continue
  a PR-v2 scope only when the current request targets its next gate, never downgrading it to bypass review.
  Follow-up renames, moves, style cleanups and runner fixes that keep case intent and assertions need
  no G1, B call, freeze or report. Compact work is not independent review or whole-PR acceptance.
- Use the project's runner, fixtures and style. No ad hoc scripts for hashes, manifests, reports or
  annotations; no product builds, run harnesses or other-language edits unless requested.
- Scope limits breadth, not test-tree depth. Split distinct observable outcomes; group variations
  sharing setup, action and oracle; mark unread branches with a resume point.
- Run focused tests and the mapping checker once after changes; broaden only for affected shared
  dependencies. Bound network retries. Do not repeatedly poll CI or reread unchanged files.

## Review and implementation

Use [templates/test-review.md](templates/test-review.md). Keep this five-column table:

| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | - [ ] 提交有效请求 | 返回结果；只处理一次 | 请求失败或重复处理 | P0 |

Each row states precondition/action and observable result. P0 = core release blocker, P1 = important
failure/boundary, P2 = lower-impact edge. Unresolved expectations use `待确认：<decision>`.
`[x]` means a `TEST-MAP` exists, not review approval or a test pass. Paths and run logs stay outside rows.

For added, deleted or materially changed cases, present the complete changed row set and stop at G1.
Generate or update mapped tests only after explicit human confirmation of the current design.
Do not combine review and implementation in one handoff. Wording/checkbox-only edits keep existing
confirmation when intent is unchanged. Read root feedback and [lessons](references/test-design.md#general-lessons) before revisions.

Implement direct, readable tests; avoid abstraction that hides assertions which prove the expected behavior.
Use one `TEST-MAP: <CASE-ID>` per native comment, inspect all affected mappings and synchronize checkboxes.
Python tests: mapping above definition; numbered Chinese docstring steps; matching numbered code-block comments.
See the [format](references/automation-maintenance.md#test-comment-format).
Run `python3 scripts/check_test_map.py --review <path>`; completeness means mapping only.
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

Default Markdown: scope/source in 1–3 lines, case table, actual open decisions; optional short tree.
Omit empty sections, N/A lists and tool logs. Edit in place; no summary files.

Chat handoff: changed IDs + result + next decision, normally at most 3 bullets. Link the document
instead of pasting it; G1 must still expose every changed row for review. For implementation include
one verification line (command, result, exit status); expand failures or material uncertainty only.
Added automation: group IDs sharing an oracle. Keep mapping, independent review and execution distinct.
