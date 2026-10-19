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
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>
```

Do not record approval without a correction. This is reusable feedback, not a case status or run history.
