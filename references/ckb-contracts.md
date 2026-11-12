# CKB contract validation in an independent test project

Use this reference only for CKB lock/type script functional testing or a requested
security review. `ai-test-agent` owns the review, Case IDs, gates, mappings, and
evidence. A separate CKB test project owns contract-specific fixtures, native
`ckb-testtool`/node runners, and any deployed-binary inventory. Do not copy a
second Case/status ledger into a contract profile or move Rust dependencies into
this generic Skill. Follow `workflow.md` and the project's Case preferences.

## Model the external API and internal reads

A CKB contract's external API is a set of allowed transaction transitions:
spend, create, update, and destroy, as applicable. Describe the actor, prior
live Cells, controlled transaction fields, allowed next Cells, and security
invariant. Lock scripts authorize consumed inputs; type scripts validate groups
formed from inputs and outputs. A script only accepts or rejects; the node
applies the UTXO transition.

Treat `ckb_load_*` calls as reads of implicit parameters. Map each relevant
function/read to `source`, index, offset, decoded field, attacker control,
validation, and downstream use. Include `args`, input/output Cell data and
capacity, witnesses, `since`, header/cell deps, and script-group position.
Built-in scripts such as Type ID require a host-side read map instead of a
fictitious syscall map. A synthetic fixture can choose existing Cell/header
values but does not prove an attacker can create that chain state.

Use the profile only for identity, API, read graph, and trust assumptions.
Put normative Spec, test tree, Case rows, decisions, and automation checkboxes
in root `reviews/`, with globally unique numeric-suffix Case IDs. Functional
and adversarial Cases may share one action and fixture, but do not duplicate
their Case rows in the profile. Executable tests belong to `suites/<suite>/`;
use one native `TEST-MAP: <CASE-ID>` comment per associated Case.

## Design the verification

Begin with a transaction that reaches and passes the target script. Recombine
one binding at a time: position (input/witness/output group), identity
(signer/header/code dep), amount, or time. Keep unrelated locks and transaction
structure valid; re-sign changed transactions when testing a type-script rule.
When testing signature coverage itself, mutate after signing instead. Choose
distinguishable fixtures so an accidental swap cannot still satisfy the rule.

Derive each oracle from a protocol rule or independently stated asset/authority
invariant, not from the same contract branch or builder under test. Record the
expected rejection layer and error, accepted control, minimized counterexample,
and unchanged state/funds where relevant. `ckb-testtool` property/fuzz runs are
concrete executions, not formal proofs. For a production claim, pin network,
activation epoch, `code_hash`, `hash_type`, code-cell outpoint and binary hash,
source revision, and upgrade authority; verify a chain-reachable node path.
Mempool policy rejection alone does not establish block-consensus rejection.
Version-changing fixes need explicit pre/post-hardfork expectations.

## Orchestrate the external suite

Use the existing checkers with the test-project root; no CKB-specific checker
is needed for Case links. From any working directory, with `AGENT` and `LAB`
set to the respective repository paths:

```sh
python3 "$AGENT/scripts/check_test_design.py" --root "$LAB" \
  --review reviews/system/type-id.md
python3 "$AGENT/scripts/check_test_map.py" --root "$LAB" \
  --review reviews/system/type-id.md --require-complete
python3 "$AGENT/scripts/run_with_evidence.py" --root "$LAB" --product . \
  --scope ckb-system-type-id --timeout 600 \
  --input suites/ckb-testtool/Cargo.toml \
  --input suites/ckb-testtool/Cargo.lock \
  --input suites/ckb-testtool/src/lib.rs \
  --input suites/ckb-testtool/tests/type_id_properties.rs \
  --input contracts/system/type-id.md \
  --input reviews/system/type-id.md \
  -- cargo test --manifest-path suites/ckb-testtool/Cargo.toml --locked
```

The receipt above is suite-level because plain `cargo test` supplies no JUnit
report. Do not infer per-Case pass counts from console text. Use `--junit`
only with a native runner that actually writes `{junit}`. A `--product .`
receipt identifies the lab checkout, not the deployed script binary; record
that binary separately. Full-node execution belongs in a separate suite and
must preserve its own network/epoch identity. Follow `execution-evidence.md`
for receipts and the active workflow's gates before automating new Cases.
