# Review Cases and Feedback

## Source-derived cases

Before writing rows, inspect only evidence relevant to the selected behavior: inputs, outputs, state changes, errors, existing tests, dependencies, limits, ordering/replay, persistence/restart, compatibility, and security-sensitive inputs.

Emit only supported cases. Prefer one case that proves a coherent observable result over field-by-field cases sharing the same request and oracle. Split larger scopes coherently without silently dropping behavior.

Use `templates/test-review.md`. Summarize genuine N/A decisions or unresolved behavior in short prose.

## Corrective feedback

Before revising cases, read the nearest `reviews/review-feedback.md` when it exists.

When a human corrects AI-authored cases—missing or unnecessary cases, scenario or expectation errors, priority changes, merges, splits, renames, or deletions—append one physical line:

```text
- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | feedback: <human feedback verbatim>
```

- Create the file on the first correction.
- Preserve the human wording; collapse line breaks to spaces and escape literal `|` as `\|`.
- Apply the correction directly and preserve IDs where behavior is unchanged.
- Do not record approval without a correction.
- Keep the file as reusable analysis feedback, not a case status, approval ledger, resolution log, or run history.

In a single-suite project use root `reviews/review-feedback.md`; in a multi-suite project use the affected suite's file.
