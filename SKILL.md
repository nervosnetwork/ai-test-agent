---
name: ai-test-agent
description: Maintain reviewer-first standalone test projects that use concise case tables and TEST-MAP comments. Use when the user explicitly invokes $ai-test-agent, works in a generated test project, asks to map or review test areas and cases, synchronize mapped automation, or assess PR test impact. Skip this skill for routine unit-test edits that have no review documents or TEST-MAP workflow.
---

# AI Test Agent

Use two sources of truth:

- `reviews/` contains behavior a human can judge.
- Executable tests contain a nearby `TEST-MAP: <CASE-ID>` comment.

Do not create coverage ledgers, approval statuses, or internal ID chains.

## Scope and token discipline

Keep each invocation bounded:

- Advance one gate for one interface, coherent behavior, or review document.
- Do not automatically continue to the next interface, area, or document.
- Group related fields proved by the same operation and oracle instead of creating one case per field.

Keep context small:

- Read the nearest `AGENTS.md`, affected review document, feedback file, mapped tests, and only the source or diff needed for the current behavior.
- Locate with `rg` or equivalent before reading targeted ranges. Avoid repository-wide file dumps and repeated reads of unchanged instructions.
- Batch related reads and checks.
- After context compaction, recover from current files, `git diff`, and the affected document rather than replaying the whole repository.

Verification should also be bounded:

- Run the narrowest deterministic or focused test first, then the mapping checker.
- Run one broader suite only when the focused result passes and the changed scope justifies it.
- Use live networks only when the case requires them; bound retries and treat repeated unavailability as residual risk.
- Inspect CI once. Do not repeatedly poll or wait for CI unless the user explicitly asks.

## Review contract

Use one stable ID per independently observable case, such as `RPC-01`. The case ID is also the Test Point ID.

Use this exact table:

```markdown
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | 提交有效请求 | 返回结果并产生一次预期副作用 | 正常请求失败或被重复处理 | P0 |
```

- Keep every row self-contained and behavior-focused.
- Use `P0` for release-blocking core behavior, `P1` for important failures and boundaries, and `P2` for lower-impact edges.
- Write `待确认：<decision>` in the expected-result cell when behavior is ambiguous.
- Preserve an ID when wording, expectation, or priority changes. Add an ID only for a new observable behavior.
- Keep paths, implementation steps, evidence chains, run history, and automation status outside the table.

Read [references/review-cases.md](references/review-cases.md) only when creating or materially revising review rows or recording corrective feedback.

## Mandatory review gate

For every new, deleted, or materially changed row:

1. Edit the complete changed row set.
2. Present it and stop before changing mapped automation.
3. Wait for explicit human confirmation.
4. Apply corrections, record corrective feedback, and present material expectation changes again.
5. Generate or update mapped tests only after the current rows are confirmed.

Do not combine review and implementation in one handoff. Existing unchanged rows remain eligible for implementation.

## Automation mapping

Put one nearby native-language comment on each mapped test:

```python
# TEST-MAP: RPC-02
def test_missing_parameter(...):
    ...
```

Mapping facts come from code:

- no matching comment: unautomated;
- matching comment: automated;
- unknown case ID: orphan mapping;
- repeated review ID: duplicate that must be fixed.

Run `python3 scripts/check_test_map.py`. Use `--require-complete` only when the requested scope is expected to be fully automated.

Read [references/automation-maintenance.md](references/automation-maintenance.md) only after review confirmation, when maintaining existing mappings, or when analyzing a PR.

## Route the request

- Help or no concrete target: read [references/help.md](references/help.md) and return concise usage help without inspecting repositories.
- New standalone test project: read [references/initialize.md](references/initialize.md) and perform only the current initialization gate.
- New or changed cases: follow the review contract and read `references/review-cases.md`.
- Confirmed automation, existing mapped maintenance, or PR impact: read `references/automation-maintenance.md`.

## Compact handoff

Report only relevant fields:

```text
Scope: <interface, behavior, document, or PR>
Changed cases: <IDs and concise expectation changes>
Added automation: <group cases sharing the same reason/oracle; expand only exceptions>
Coverage: <mapped>/<reviewed>; unmapped: <IDs or none>
Verification: <command> -> <literal result and exit status>
Residual risk: <ambiguous, manual, unavailable, or none>
Next gate: <exact confirmation or action>
```

Do not repeat full unchanged tables or explain every passing assertion separately unless the user asks.
