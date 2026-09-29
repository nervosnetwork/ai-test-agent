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

## Recursive decomposition

Apply these rules to both project-wide design and PR/diff design. Size changes how much breadth fits
in one scope, not how deeply its selected behaviors need analysis. Tree depth follows evidence;
there is no fixed minimum or maximum and no requirement to pad a simple behavior with categories.

1. Build a compact hierarchy from the requested scope: observable capabilities, their responsibilities
   and affected behavior paths. For a diff include relevant callers, shared state and downstream
   effects, not only changed lines. Keep siblings visible; mark unread branches `[unanalysed]` with
   the specific missing input and next entry point. An overview is not a finished test design.
2. Expand each selected branch recursively. Split when it still contains different preconditions,
   state transitions, decisions, failure/recovery outcomes or independently failing obligations.
   Choose the relevant axis from requirements and code; do not mechanically insert every category
   or enumerate a Cartesian product. Typical shape: capability → operation → state/condition →
   outcome → Case. Different branches may have different depths.
3. Stop only when a leaf identifies a concrete precondition/input, action and observable expected
   result, and remaining variations share the same operation and oracle. A module, function, or
   label such as “normal/errors/boundaries” alone is not a testable leaf. Split mixed outcomes;
   retain grouped fields or equivalent inputs when one coherent Case proves them together.
4. Link each testable leaf to its stable Case ID and sourced Spec in the same review document.
   Reorganizing the hierarchy alone preserves IDs and rows; reuse `[ref]` rather than duplicate
   definitions. Keep candidate expectations explicit and subject to G1.
5. Under context/time pressure, finish a smaller subtree, not a shallower substitute for the whole
   scope. Record each unfinished frontier as `[unanalysed]` (unread evidence) or `[pending]`
   (known decision/work outstanding), with a reason and the next source/decision to inspect. Retain
   the hierarchy in the review and resume from those nodes on continuation. Do not silently turn
   in-scope missing analysis into an exclusion. If it changes the promised scope, present the reduced
   scope for a human decision; no whole-scope completeness claim while frontier nodes remain.

For whole-project initialization, Gate 1 creates only the hierarchical area map and planned review
paths, not Case rows. After map confirmation, use the same recursive procedure inside the selected
Gate 2 review. Other review documents remain unanalysed until selected; depth is not permission to
advance a gate or start automation.

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

## G1

Present change summary, Spec, tree, the **complete changed row set**, B diff→Spec accounting and Case/Spec
acknowledgements, B findings, A responses and unresolved matters,
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
