---
name: ai-test-agent
description: Initialize or maintain a standalone test project built around concise human-reviewed case tables and direct code mappings. Use whenever Codex needs to decompose a product into reviewable test areas, create or revise interface and behavior test cases, analyze PR test impact, implement mapped automation, report dynamic automation coverage, or explain the workflow. Keep reviewer-facing documents free of status bookkeeping and internal ID chains.
---

# AI Test Agent

Build test projects around two sources of truth:

- `reviews/` records what humans need to review: one stable case ID, scenario, expected result, prevented problem, and priority.
- Executable tests record what is automated through the exact nearby comment `TEST-MAP: <CASE-ID>`.

Do not make reviewers navigate `MOD -> FUNC -> COV -> TP` dictionaries. Inspect those concerns internally, then present each case as a self-contained row.

## Show Usage Help

When the user invokes `$ai-test-agent help`, asks how to use the skill, or provides no concrete target or action, return concise help without inspecting or modifying repositories.

Include these copyable prompts:

- Initialize: `Use $ai-test-agent to initialize a standalone test project for <source repository or path>. First propose the test areas and review-document map, then stop for review. After confirmation, create concise case tables and implement the agreed cases with TEST-MAP comments.`
- Review a PR: `Use $ai-test-agent in <test-project path> to analyze <PR URL or number>, update affected review cases and mapped tests, and verify the affected scope.`
- Maintain coverage: `Use $ai-test-agent in <test-project path> to add or revise cases for <interface, behavior, or risk> and synchronize automation.`

Initialization needs a source repository or path. Maintenance needs the existing test-project path and requested change.

## Core Review Contract

Use one reviewer-facing ID for each independently observable case, such as `RPC-01`, `P2P-04`, or `STORE-12`. The case ID is also the Test Point ID; do not create a second `TP-*` ID.

Use this exact table shape:

```markdown
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | 提交有效请求 | 返回结果并产生一次预期副作用 | 正常请求失败或被重复处理 | P0 |
```

Reviewer-facing rules:

- Put everything needed to judge a case on one physical row.
- Describe concrete product behavior, not coverage taxonomy.
- Use `P0` for release-blocking core behavior, `P1` for important failures, recovery, and boundaries, and `P2` for lower-impact edges.
- Write `待确认：<decision>` in the expected-result cell when product behavior is ambiguous, and call it out in `本轮需要确认`.
- Preserve a case ID when correcting its wording, expectation, or priority. Add a new ID only for a new independently observable behavior.
- Directly edit or remove obsolete rows. Do not maintain per-case `PROPOSED`, `APPROVED`, `COVERED`, or automation statuses.
- Do not put test file paths, implementation steps, source-evidence chains, execution history, or internal mapping tables in the main case table.

Before writing cases, internally consider core behavior, input validation, state changes, failures and recovery, caller trust, cross-component effects, ordering and replay, persistence and restart, compatibility, resource limits, and security-sensitive inputs. Emit only target-supported cases. Summarize genuine N/A decisions or unresolved behavior in short prose when they matter to review.

## Mandatory Review Gate

New or materially changed review rows must complete human review before any corresponding automated test code is generated or modified:

1. Create or revise the reviewer-facing rows.
2. Present the complete changed set and stop.
3. Wait for explicit human confirmation or correction.
4. Apply corrections and present the changed rows again when expectations materially change.
5. Generate or update automated tests only after the human confirms the current rows are ready for implementation.

Do not collapse review and implementation into one handoff. Existing unchanged rows in an established test project remain eligible for implementation; every new, deleted, or behavior-changing row reopens the gate. Keep confirmation conversational—do not add approval statuses to the document.

## Review Feedback Collection

Treat a human correction to AI-authored review cases as reusable analysis feedback. Before creating or revising cases, read the relevant `reviews/review-feedback.md` when it exists and apply applicable prior corrections.

When the human requests a missing or unnecessary case, corrects a scenario or expected result, changes a priority, or asks to merge, split, rename, or delete cases:

1. Append one physical line to the affected review directory's `review-feedback.md`; create it on the first correction.
2. Use: `- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>`.
3. Preserve the human's wording. Collapse line breaks to spaces and escape literal `|` characters as `\|` only so the record remains one valid line.
4. Apply the correction directly to the review rows, preserving stable case IDs where the behavior remains the same.
5. Present materially changed rows again and keep the mandatory review gate closed until explicit confirmation.

Do not record approval without a correction. Keep the file limited to model, affected cases or scope, and feedback; it is learning history, not a case status, approval ledger, resolution log, or execution history. In a single-suite project use root `reviews/review-feedback.md`; in a multi-suite project use the affected suite's `reviews/review-feedback.md`.

## Automation Mapping

Map executable tests directly to the review case with one nearby comment:

```python
# TEST-MAP: RPC-02
def test_missing_parameter(...):
    ...
```

Use the native comment syntax for the implementation language, but preserve the literal `TEST-MAP: <CASE-ID>` payload. The scenario and oracle already exist in the review row and test assertions, so do not repeat them in the comment.

Treat automation as code-derived fact rather than document state:

- No matching `TEST-MAP` comment: not automated.
- One or more matching comments: automated.
- A comment referencing no review case: orphan mapping that must be fixed.
- The same case ID appearing in multiple review rows: duplicate review ID that must be fixed.

Run `python3 scripts/check_test_map.py` to report current mapping coverage. Use `--require-complete` only when the requested scope is expected to be fully automated. Report the computed summary in the handoff, for example `Automation coverage: 6/7; unmapped: RPC-07`; do not write it back into review documents.

## Project Layout

Default to the simplest structure justified by the target.

For one test runner or assurance approach:

```text
<project>-tests/
├── AGENTS.md
├── README.md
├── source/<project>/
├── reviews/<area>/<interface-or-behavior>.md
├── tests/
├── fixtures/
├── scripts/check_test_map.py
└── templates/test-review.md
```

Use `benchmarks/` instead of `tests/` for a performance-only project and `targets/` for a fuzz-only project.

Create `suites/<suite>/` only when the target genuinely needs multiple independent runners or assurance approaches such as API, P2P, performance, or fuzz. Each suite owns its review documents, executable area, fixtures or inputs, README commands, and case-ID prefix. Keep case IDs unique across the whole test project.

Keep the product checkout under `source/<project>/`, excluded from the test repository. Reuse a matching checkout, clone only when absent, and never overwrite a conflicting path.

## Initialize a Test Project

Treat initialization as three conversational gates. Confirmation is represented by the conversation and current document content, not persisted status labels.

### Gate 1: Test-Area Map

1. Inspect the target architecture, public interfaces, state ownership, deployment shape, build system, existing tests, runnable services, CI, and risks.
2. Select only the runners or assurance approaches supported by that evidence.
3. Generate the skeleton:

   ```bash
   python3 <skill>/scripts/init_repo_tests.py --project <name> --source-repo <path-or-url> --suites <suite> [<suite> ...] --output <test-project>
   ```

4. Fill stable target information in root `AGENTS.md`.
5. Replace the placeholder in `reviews/README.md` with a concise map: area, responsibility, boundary, entry points, observable outcomes, and planned review-document paths.
6. Present the map and stop for correction or confirmation. Do not create case rows or executable tests yet.

### Gate 2: Review Cases

1. Select one confirmed interface, behavior, or coherent review document.
2. Read the relevant `reviews/review-feedback.md` when it exists.
3. Inspect actual source behavior, errors, state changes, dependencies, limits, existing tests, and observable failure modes.
4. Create or update `reviews/<area>/<name>.md` from `templates/test-review.md`. In a multi-suite project, use the relevant suite's `reviews/` directory.
5. Produce a bounded table of source-derived cases. Prefer a complete interface or coherent behavior over an arbitrary number of rows.
6. Present the complete new or changed row set and decisions that need review, then stop before generating test code. Record corrective feedback, edit the rows directly, and present material expectation changes again.
7. Repeat document by document until the agreed scope has clear expected results and no unresolved review decision is hidden.

### Gate 3: Automation

1. Start only after the user explicitly confirms that the current review document or changed case IDs have completed review and are ready for implementation.
2. Use the target's native language, runner, dependency conventions, and CI style.
3. Add `TEST-MAP: <CASE-ID>` beside every mapped automated test.
4. Run the narrowest meaningful tests, then run `python3 scripts/check_test_map.py` for the affected project.
5. Report implemented IDs, computed automation coverage, verification results, and remaining ambiguous or manual behavior.

## Maintain a Test Project

1. Work from the generated test-project root and read its `AGENTS.md` and relevant README.
2. Resolve and reuse the declared source checkout.
3. Read the affected review document, relevant `reviews/review-feedback.md` when present, and mapped tests. Search code for `TEST-MAP: <CASE-ID>` rather than consulting a separate mapping ledger.
4. For PR analysis, fetch base and head revisions, inspect the diff first, then read wider source context only as needed.
5. Translate each changed behavior into the affected review rows and the minimum test change needed for a concrete failure mode.
6. Directly update existing rows when expectations or wording change; preserve IDs. Add or remove rows only when independently observable behavior is added or removed.
7. If any row is new, deleted, or materially changed, present the complete changed set and stop for human review before touching mapped test code.
8. After explicit confirmation, synchronize automatable tests and keep `TEST-MAP` comments current.
9. Run focused verification and the mapping checker. Report unresolved product decisions and unautomated cases without persisting statuses or PR-specific reports.

For a previously unmapped product area, return to the test-area and review-case gates before implementation.

## PR Review Output

Keep PR handoffs compact:

```text
PR impact:
- <changed behavior> -> <review document and case IDs> -> <required test action>
Changed cases:
- <ID> [P0/P1/P2] <scenario> -> <expected result>
Automation coverage: <mapped>/<reviewed>; unmapped: <IDs or none>
Verification: <command> -> <result and exit status>
Residual risk: <ambiguous, manual, unobservable, or none>
Needs review: <exact product decision or none>
Next gate: <explicit review confirmation needed before implementation, or implementation/verification action>
```

Omit irrelevant sections instead of printing placeholder `none` fields. Passing tests support the identified behavior but do not prove that unknown risks are absent.

## Persistence Rules

Persist only:

- root and suite instructions plus stable commands;
- the test-area index in `reviews/README.md`;
- concise review documents;
- append-only corrective feedback in `reviews/review-feedback.md`, created on the first correction;
- executable tests, fixtures, and configuration;
- the deterministic mapping checker.

Do not create separate module/function/coverage dictionaries, test-point status ledgers, automation mapping tables, approval histories, PR report directories, run histories, or result archives. The narrowly scoped corrective-feedback file is the only review-history exception.
