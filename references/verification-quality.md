# Verification quality

Before automation, explain the following for each high-risk Case or group sharing one oracle.
Keep this prose outside the five-column table; reuse common setup rather than repeating fields.

- **Oracle:** where the expected value/rule comes from, independently of the operation under test.
  Examples: hand-calculated balances, conservation equations, protocol vectors, an external decoder
  or a separately derived model. A second call to the same production calculation is not independent.
- **Entry:** the actual CLI, HTTP endpoint, browser action or contract transaction exercised.
  Production builders may prepare fixtures; their output alone does not establish correctness.
- **Observation:** the new response, state transition, recipient/value or side effect asserted after
  the operation. Distinguish a fresh observation from cached state and mocked return values.
- **Layer:** what this evidence establishes and what it does not. Host checks, injected wallets,
  RPC mocks, actual script execution and a real-node funds flow are separate layers.

For security-sensitive negative cases, prove a valid baseline reaches the intended layer. Change the
attack-relevant input while keeping prerequisites valid, then assert the rejection source and unchanged
funds/state. For example, re-sign an altered payment before checking that the validator rejects it;
a stale signature only demonstrates lock rejection. A resolver refusing a spent UTXO does not prove
the contract's paid-state logic. A mocked server denial does not prove on-chain authorization.

Inspect that the runner actually collects the test, that assertions cover the claimed outcome, and
that waits/retries/exceptions cannot skip the observation. All skips, absent inputs and unsupported
runner evidence remain visible. Use a focused mutation or old-fails/new-passes check when it adds
confidence; never mutate production funds or change the expected rule merely to make a test green.

Spec provenance, oracle independence and review independence are different questions. Record
inferences as such; a self-reviewed test can use an independent arithmetic oracle without having
received independent B review. A structural checker validates links, not these semantic judgments.
