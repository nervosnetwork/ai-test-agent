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

Run `python3 scripts/check_test_design.py --review <path>` once after the changed batch; its structural checks do
not establish semantic completeness. Complete B's independent design review and address findings using
[workflow-gates.md](workflow-gates.md); compact work does not activate full PR-v2.

New rows start `- [ ]`; `- [x]` mirrors existing `TEST-MAP` presence. Preserve stable IDs.
Finish all selected documents and B review before stopping at G1 with every changed row (including
deletions) for the user's review. After approval, automation requests proceed to one first Case at G2,
not batch implementation. Case-review-only requests end at G1.

## Corrective feedback

Read root `reviews/review-feedback.md` before revisions. On a human correction, create it if needed
and append one physical line, preserving wording (collapse line breaks; escape literal `|` as `\|`):

```text
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>
```

Do not record approval without a correction. This is reusable feedback, not a case status or run history.
