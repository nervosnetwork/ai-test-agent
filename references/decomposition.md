# Recursive decomposition

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
