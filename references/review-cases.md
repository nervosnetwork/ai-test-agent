# Review cases

Read the selected rows, matching mappings, relevant source and root feedback only. Derive cases from
observable inputs/results/state changes; inspect additional paths when the evidence requires them.
Group variations with the same operation and oracle; separate independently failing outcomes.

Use `templates/test-review.md`: scope/source, five-column cases, actual questions only. Keep cells to
one concise sentence or short clauses; put shared setup above the table once. Omit empty sections,
stock risks, exhaustive N/A lists, execution logs and tutorials. Complex scopes may add a compact
hierarchy with Case IDs ([decomposition.md](decomposition.md)); keep unread branches explicit. Preserve an existing Spec/tree rather than
reformatting it for brevity. Full PR-v2 alone uses `templates/test-review-full.md` and `test-design.md`.

New rows start `- [ ]`; `- [x]` mirrors existing `TEST-MAP` presence. Preserve stable IDs. Present every
changed row (including deletions) and wait at G1 before mapped implementation; do not paste unchanged rows.

## Corrective feedback

Read root `reviews/review-feedback.md` before revisions. On a human correction, create it if needed
and append one physical line, preserving wording (collapse line breaks; escape literal `|` as `\|`):

```text
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim> | type: <漏测\|预期\|环境\|位置\|流程>
```

Do not record approval without a correction. This is reusable feedback, not a case status or run history.

`type` classifies the correction; pick the closest one:

| type | Meaning |
| --- | --- |
| 漏测 | Missing cases, roles, boundaries or insufficient decomposition |
| 预期 | Wrong expected result or oracle; assertion does not prove the behavior |
| 环境 | Runtime baseline, binaries, fork, CI scope, skip rules |
| 位置 | Case, review or automation placed in the wrong file or directory |
| 流程 | Gate order, handoff, commit split, wording or communication |

Before revising, apply every matching line for the scope, not only the latest. Promotion rule: when the
same lesson appears in two or more test projects, propose it as a general rule in this skill
([general lessons](test-design.md#general-lessons) or the matching reference) in a separate change; afterwards keep only
project-specific lines (paths, PR scope, local decisions) in the project file. Never delete or reword a
human line to promote it; mark it `promoted: <skill rule>` at line end instead.
