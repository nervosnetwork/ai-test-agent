# Two human gates

These are conversational gates for test design and automation, including full PR-v2.
Reuse current documents, B findings and explicit user confirmations; do not restart completed work.
Prepare all documents in the requested scope before G1, not one approval per document.

## G1 — completed documents and independent B review

A completes Spec → 测试树 → 用例, checks structural links, then asks B to review the entire selected
design against raw requirements/source. Use a separate reviewer session with explicit scope and raw
inputs, not A's conversation or conclusions. B checks omissions, expectations, boundaries and
observability. Follow `agent-adapters.md` for reviewer boundaries; a B review alone does not opt into
the full PR-v2 machinery or require a host-attestation service.

Address actionable findings and have B check material revisions before presenting the final design.
Do not label A's self-review as independent B review or missing B work as completed. Keep reviewer
identity, findings and their resolution available; link existing evidence rather than duplicate reports.
Stop with every changed row, the completed documents and B's outcome for the user's review.
Unresolved requirement decisions are explicit at this handoff, never silently chosen by A.
Write no automated Cases before the user's explicit design approval. A case-review-only task ends here.

## G2 — first automated Case meets the standard

After G1 approval, choose the first representative confirmed Case, implement only that Case and the
minimum fixtures/helpers it needs, and run its focused check. If a suitable first Case already exists,
inspect and adapt it instead of recreating it. Do not batch-implement the remaining Cases yet.

Present the Case ID, actual code/diff and command/result, including any execution limitation. Check
readable setup/actions/assertions, native fixture style, TEST-MAP placement, and the required numbered
Chinese steps/comments for Python. Stop for the user's confirmation that this is the desired standard.
If corrections are requested, revise this first Case and stay at G2; G1 approval is not G2 approval.

## After G2 — automatic completion

The user's standards confirmation releases the remaining confirmed scope for implementation, focused
runs, mapping/checkbox updates and test-side fixes using the approved example. Verify once per changed
batch; do not ask for another approval per Case, document, test run or final handoff. Full PR-v2's
coverage review and evidence checks run automatically here, not as an additional human gate.

Report final results and genuine unresolved blockers; do not weaken assertions or change product code
to obtain passes. Material expectation/scope changes return affected design to G1. Reopen G2 only if
the agreed implementation standard changes, not for routine fixes or additional Cases in that scope.
Intent-preserving maintenance and impact-only questions do not replay these gates.

Compact work uses conversation confirmations, not a new approval ledger. The bundled full PR-v2 CLI
records G1 and evidence; G2 is enforced by these skill instructions, not a new CLI transition.
`implemented`, process exit 0 and report status labels never substitute for the user's G2 confirmation.
