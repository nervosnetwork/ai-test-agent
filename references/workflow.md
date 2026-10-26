# Choose the authorized workflow

Infer the requested outcome from the conversation; preserve prior authorization and explicit stop points.
Choose one route for the declared scope, without automatically expanding into neighboring interfaces.

| Request | Route | Completion |
| --- | --- | --- |
| Propose a map, review cases, or stop for review | Review-only | Present the complete changed rows/map and wait before implementation. |
| Review then implement/validate/synchronize | End-to-end | Discover, design, self-review, implement, run focused checks and publish to the authorized destination. |
| Explicit full PR-v2 or a project requirement for it | Full PR-v2 | Keep the existing independent B evidence, exact design confirmation and G1/G2 rules. |

In end-to-end work, an area map and changed rows remain reviewable artifacts, not new mandatory
conversation stops. Complete the requested interfaces in coherent batches. Do not ask for the same
permission again after a wording change, test-runner repair or routine implementation decision.
Initialization, existing project maintenance and security work follow the same authorization rule.
Do not infer end-to-end authorization from a request only to propose or inspect tests.

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
