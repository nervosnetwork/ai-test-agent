# Review cases

Read the selected rows, matching mappings, relevant source and root feedback only. Derive cases from
observable inputs/results/state changes; inspect additional paths when the evidence requires them.
Group variations with the same operation and oracle; separate independently failing outcomes.

Use `templates/test-review.md`: **Spec → 测试树 → 用例** is required for every selected review,
including simple behaviors and compact PR impact. Cite each observable rule's basis, decompose it
into a Markdown hierarchy, and link every testable leaf to a Spec and stable Case ID
([decomposition.md](decomposition.md)). The unique five-column table supplies scenarios and oracles.
Keep cells to one concise sentence or short clauses; put shared setup above the table once. Omit
only empty optional question sections, stock risks, exhaustive N/A lists, execution logs and
tutorials. Keep unread branches explicit. For a selected legacy review without these sections,
add them before materially changing Cases; leave unrelated reviews unchanged. Full PR-v2 additionally
uses `templates/test-review-full.md` and `test-design.md` for independent review gates.

Describe independent expected values, actual entry, fresh observation and claimed verification layer
outside the table, grouping Cases sharing one oracle. Follow `verification-quality.md`; production
fixture construction alone is not an independent expected result.

Run `python3 scripts/check_test_design.py --review <path>` before implementation; its structural checks do
not establish semantic completeness. Compact review does not invoke B or the full PR-v2 workflow.

New rows start `- [ ]`; `- [x]` mirrors existing `TEST-MAP` presence. Preserve stable IDs. Present every
changed row (including deletions). In review-only mode wait before mapped implementation; authorized
end-to-end work self-reviews and proceeds with unambiguous Cases under `workflow.md`. Full PR-v2 keeps
G1. Do not paste unchanged rows or resolve unknown product policy by guessing.

## Corrective feedback

Read root `reviews/review-feedback.md` before revisions. On a human correction, create it if needed
and append one physical line, preserving wording (collapse line breaks; escape literal `|` as `\|`):

```text
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>
```

Do not record approval without a correction. This is reusable feedback, not a case status or run history.
