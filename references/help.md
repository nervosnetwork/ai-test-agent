# Usage Help

Return only the prompts relevant to the user's question.

- Initialize: `Use $ai-test-agent to initialize a standalone test project for <source repository or path>. Inspect the target, propose one bounded test-area map, and stop for review.`
- Review cases: `Use $ai-test-agent in <test-project path> to create or revise cases for <one interface or behavior>. Present the changed rows and stop for confirmation.`
- Implement confirmed cases: `Use $ai-test-agent in <test-project path> to implement confirmed case IDs <IDs>, add TEST-MAP comments, and run focused verification plus the mapping checker.`
- Review a PR: `Use $ai-test-agent in <test-project path> to analyze <PR URL or number>, produce a change summary, Spec, test tree and independent B design review for one behavior, then stop for confirmation before automation.`

Initialization needs a source repository or path. Maintenance needs the test-project path and one bounded requested change.

- Continue PR: `Use $ai-test-agent to implement the confirmed scope <scope>, have B inspect actual assertion coverage, render evidence, and execute focused tests. Keep gaps and unverified isolation visible.`
- Upgrade: `Use $ai-test-agent to preview the v2 migration of <test-project>; preserve custom instructions and stable IDs, and show the diff before applying.`
