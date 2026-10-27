# Usage help

Return only the relevant prompt; do not inspect repositories for a help-only question.

- Initialize: `Use $ai-test-agent to initialize a test project for <source>; propose the area map and stop.`
- Cases only: `Use $ai-test-agent in <test-project> to revise <behavior> cases; do not implement tests.`
- Design: `Use $ai-test-agent in <test-project> to finish <scope> test-point documents and independent B review, then stop for my review at G1.`
- First Case: `The G1 design is approved. Implement only the first automated Case for <scope>, run its focused check and stop at G2 for my standards review.`
- Continue: `The first Case meets my standards. Finish the remaining confirmed <scope> automation and focused checks without further routine approvals.`
- End-to-end: `Use $ai-test-agent to review, implement and validate <scope>, then synchronize results to <authorized destination>; retain G1/G2 and complete remaining work automatically after both approvals.`
- Security: `Use $ai-test-agent to audit funds risk in <source revision>, referencing <security review Cases>; trace attack paths, validate candidates and report evidence and remaining trust assumptions.`
- PR impact: `Use $ai-test-agent to assess <PR> test impact; keep the review compact.`
- Full PR-v2: `Use $ai-test-agent for full PR-v2 on <PR/scope>, including independent B review and human gates.`
- Migrate: `Use $ai-test-agent to preview an upgrade of <test-project>; preserve custom instructions and IDs.`
