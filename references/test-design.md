# Spec, tree and B design review

Spec, Markdown nested test tree and the unique Case table are mandatory in every selected review.
All material design work uses the two gates in [workflow-gates.md](workflow-gates.md).
For full PR-v2, use `templates/test-review-full.md` and the additional evidence checks below, not extra human gates.
Use `verification-quality.md` to review independent oracles and claimed verification layers.
Rules are `### SPEC-01：...` headings, never a competing five-column rule table.
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
need explicit blocks/Spec/tree when selected for design validation.

Keep prose terse: shared context once, short rule values, tree labels plus IDs rather than repeated
case descriptions. Link B reports/responses instead of copying them into the review. Omit empty
question sections; preserve the required Spec fields, markers and complete changed rows.

## Recursive decomposition

Apply [decomposition.md](decomposition.md) to the Spec/tree; the review below checks its result.

### Depth review before G1

B first checks raw diff → Spec completeness below, then requirements/source against the hierarchy: omitted children, mixed outcomes hidden
inside a broad Case, category-only leaves, unexplored cross-boundary effects and misleading scope
claims. A shallow branch is valid when its leaf meets the stop rule; many indentation levels do not
prove completeness. The structure checker validates links and leaf dispositions, not semantic depth.

### Raw diff → Spec completeness

B starts from the **complete frozen diff**, not just A's existing Specs or selected Cases. `prepare`
derives `diff_inventory` from every hunk; file headers/metadata accompany the first hunk, and changes
without hunks (binary files, renames, mode changes, empty-file additions/deletions) still get a unit.
These snapshot-local change IDs locate evidence, not new Case IDs or a hand-maintained coverage ledger.

For every inventory unit, B returns one `diff_coverage` entry in `design-review.json`, with `change_id`,
`status`, `spec_refs`, a concrete `reason` and `finding_ids`. One hunk can contain several independent
behavior changes; link all corresponding Specs and check their actual conditions/results against
old/new code, including removed behavior, failures, state, compatibility and cross-boundary effects.

- `mapped`: every relevant behavior in the unit is represented by the cited existing Specs. Specs
  marked `Testing: not_tested` still count as defined behavior, not automated test coverage.
- `no_behavior_change`: explain evidence that no behavior Spec is needed. File type alone is not a
  reason: configuration, documentation, tests, binary assets and refactors can change contracts.
- `gap` / `unanalysed`: some behavior lacks an adequate Spec, or evidence remains unread. Link at
  least one B finding. Even one partial hunk stays incomplete; a generic Spec link is not enough.
- `out_of_scope`: justify an explicit slice boundary, identify the affected behavior and next review
  destination. It requires a human scope decision and stays outside any full-diff coverage claim.

Missing/duplicate/unknown units, nonexistent Spec links and missing gap findings fail validation.
G1 stays closed for `gap` or `unanalysed`, even if A says accepted or a human supplies `--decision`:
update the design and obtain a fresh B review first. Exclusions permit only a confirmed partial scope.
An empty finding list needs both complete diff accounting and exact Case/Spec acknowledgements.
The derived Markdown B report presents both directions; do not duplicate this evidence in Case rows.
Scripts check accounting and links, not semantic truth; B must independently justify every disposition.
Older review evidence without `diff_coverage` requires `prepare` and a new B review before G1.

```sh
python3 scripts/check_test_design.py --review reviews/p2p/connection-limit.md --json
python3 scripts/pr_workflow.py prepare --scope connection-limit
python3 scripts/pr_workflow.py review --scope connection-limit --phase design --backend codex
python3 scripts/pr_workflow.py respond --scope connection-limit --responses reports/connection-limit/a-response.json
```

See [agent-adapters.md](agent-adapters.md) before choosing a backend. B reads raw PR/spec/source,
project conventions and the design independently. B must acknowledge the exact Spec references for
every selected Case and, for each finding, supplies an ID, location, basis, suggestion and impact.
In the separate `respond`
phase, A records accepted, duplicate, not_applicable or needs_decision for every B finding, with a
concrete response (existing Case/rule when declining). G1 remains closed until that response set is exact.
An added test point is not a confirmed product defect.
A may import a structured review with `--evidence <JSON>`; imported reviews remain isolation_unverified.
Default budget is one full review plus one targeted revision per phase, not one B per Case.
If A changes the reviewed design, `prepare` again and review that version. Exhausted budgets never
turn critical disagreements into approval; ask the human for a new bounded scope/review budget.

## G1 — completed documents and B review

Present the **complete changed row set**, a short change summary and unresolved matters; link the
current Spec/tree, B diff→Spec accounting, Case/Spec acknowledgements, findings and A responses
instead of reproducing them in chat. Make the complete evidence available for review, then stop. Only after explicit human confirmation run:

```sh
python3 scripts/pr_workflow.py confirm --scope connection-limit \
  --human '<reviewer>' --confirmation '<verbatim current-scope permission>'
```

Use `--decision '<human resolution>'` for listed ambiguities; a material expectation change first
requires updated rows and review. Scripts store permission in disposable scope context, not feedback
or a hand-maintained approval ledger. Same-user local state is not an unforgeable human attestation.
After G1 confirmation, implement only the first representative Case and stop at G2 for the user's
standards confirmation; follow `workflow-gates.md` before batch implementation.
Mapping-only checkbox changes are ignored by the semantic design fingerprint; other text changes,
priorities, scope, requirements and product inputs are not.
