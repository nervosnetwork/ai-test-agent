# Spec, tree and B design review

Use `templates/test-review.md`. Spec, Markdown nested test tree and the unique Case table live in one
root review. Rules are `### SPEC-01：...` headings, never a competing five-column rule table.
The template's fixed English field keys support deterministic parsing; values may use any language.

- `Condition`, `Expected`, `Observable`, `Basis`, `Source`, `Testing` are required.
- `Source: explicit|observation|inference`; observations/inferences remain explicit human decisions.
- `Testing: required`, or `Testing: not_tested — <reason>`.
- Place the tree between `TEST-TREE-BEGIN/END` HTML comments and cases between `TEST-CASES-BEGIN/END`.
- A leaf uses `RPC-01 [primary] -> SPEC-01`; cross-branch reuse uses `[ref]` and the same ID.
- Each Case has exactly one primary owner and at least one Spec. Each tested Spec has a Case.
- Mark unresolved branches `[pending]` or `[unanalysed]`, and N/A branches `[not_applicable]`, each
  followed by ` — <reason>`. Mark every unevaluated leaf; do not use an empty category to imply coverage.

Group by observed behavior, not files or a universal category checklist. Tree size is not a proof of
exhaustiveness. The structure checker reports dangling/isolated Cases and missing links, not whether
A omitted an entire behavior. Unmarked legacy reviews remain supported by the mapping checker but
need explicit blocks/Spec/tree before joining v2 design validation.

```sh
python3 scripts/check_test_design.py --review reviews/p2p/connection-limit.md --json
python3 scripts/pr_workflow.py prepare --scope connection-limit
python3 scripts/pr_workflow.py review --scope connection-limit --phase design --backend codex
```

See [agent-adapters.md](agent-adapters.md) before choosing a backend. B reads raw PR/spec/source,
project conventions and the design independently. For each finding it supplies location, basis,
suggestion and impact. A records accepted, duplicate, not_applicable or needs_decision, with a concrete
response (existing Case/rule when declining). An added test point is not a confirmed product defect.
A may import a structured review with `--evidence <JSON>`; imported reviews remain isolation_unverified.
Default budget is one full review plus one targeted revision per phase, not one B per Case.
If A changes the reviewed design, `prepare` again and review that version. Exhausted budgets never
turn critical disagreements into approval; ask the human for a new bounded scope/review budget.

## G1

Present change summary, Spec, tree, the **complete changed row set**, B findings and unresolved matters,
then stop. Only after explicit human confirmation run:

```sh
python3 scripts/pr_workflow.py confirm --scope connection-limit \
  --human '<reviewer>' --confirmation '<verbatim current-scope permission>'
```

Use `--decision '<human resolution>'` for listed ambiguities; a material expectation change first
requires updated rows and review. Scripts store permission in disposable scope context, not feedback
or a hand-maintained approval ledger. Same-user local state is not an unforgeable human attestation.
Mapping-only checkbox changes are ignored by the semantic design fingerprint; other text changes,
priorities, scope, requirements and product inputs are not.
