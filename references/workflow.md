# Choose the authorized workflow

Infer the requested outcome from the conversation; preserve prior authorization and explicit stop points.
Choose one route for the declared scope, without automatically expanding into neighboring interfaces.

| Request | Route | Completion |
| --- | --- | --- |
| Propose a map, review cases, or stop for review | Review-only | Stop at the requested map; for Case design, finish all selected documents and B review before the user's G1 review. |
| Review then implement/validate/synchronize | Two gates, then end-to-end | Complete G1; implement only the first Case for G2 standards confirmation; then finish the remaining confirmed scope automatically. |
| Continue an already confirmed scope or intent-preserving maintenance | End-to-end continuation | Reuse G1/G2 confirmations; implement, check and synchronize without repeating them. |
| Explicit full PR-v2 or a project requirement for it | Full PR-v2 | Use the same two human gates plus independent design/coverage evidence checks, not an additional final human gate. |

Follow [workflow-gates.md](workflow-gates.md) for the exact two stops. An end-to-end request establishes
scope, not either gate's approval. Do not add a map-only gate or request approval per document, Case,
test run or final handoff. After G2, complete coherent batches without repeating permission for wording
changes, test-runner repairs or routine implementation decisions. Initialization and newly designed
security Cases follow the same gates. Inspection/audit-only questions do not imply test implementation.

Missing business rules remain `待确认：<decision>`. Ask for the actual decision and continue cases
that do not depend on it; do not turn an implementation observation into an approved requirement.
Keep blocked and unexecuted items visible. Self-review is not human confirmation or independent B.
An active full PR-v2 scope must not be downgraded to bypass a gate; changing its reviewed design
still requires fresh evidence and current-design human confirmation.

Authorization covers the requested tests and isolated builds needed to exercise the product.
It does not authorize product policy changes, production deployment, real payments or messages to
unrequested recipients. Synchronize results only to destinations the user authorized.

Keep a small handoff: changed behavior, literal verification outcome, open decisions and next action.
Execution receipts are generated evidence; do not maintain a second Case or approval ledger.
