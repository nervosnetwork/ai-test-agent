# Requested security review

Use this route for an explicit security audit, attack-path investigation or funds-risk question.
Ordinary functional acceptance does not automatically become an exhaustive security audit.
Follow `workflow.md` for authorization; use `templates/security-review.md` with existing Case IDs.

Start from assets and trust boundaries: who can change code/roots/configuration, authorize a
payment, supply a proof, select inputs and receive outputs? Distinguish an unprivileged caller,
a beneficiary, a coordinator and each privileged key holder. Inspect all relevant exits, including
upgrades, migrations and recovery paths, rather than only the normal withdrawal entry point.

Review in complementary passes:

1. Trace assets, authority and source-to-sink paths from actual entry points.
2. Challenge invariants: individual/shared/global limits, retained balances, exact asset identity,
   fees/capacity, cumulative state, replay, proof authentication and resource/liveness boundaries.
3. Validate plausible counterexamples with the real execution layer where available. Establish a
   valid baseline, preserve signatures/prerequisites and attribute rejection precisely.

Use `verification-quality.md`; existing happy-path or unit-test counts do not substitute for this work.
Do not describe these passes as a dedicated scanner run unless that scanner actually ran. A request
for depth does not itself authorize spawning agents or invoking unavailable external services.

For each candidate, record source location and immutable revision, attacker capability, required
preconditions, complete path to the asset, intended invariant, affected funds/liveness and evidence
that supports or refutes it. Separate **validated defect**, **conditional authority/trust risk**,
**unvalidated candidate** and **rejected candidate**. Severity depends on reachable impact and
preconditions; a test priority is not a vulnerability severity. Do not infer production exposure
without the deployed binary/profile, code cell and authority evidence.

Example: profile-bound roots can prevent arbitrary payouts under current code while a retained
code-upgrade authority can replace those rules. Report the latter's precise key requirements and
potential loss; do not claim either unprivileged theft or permanent immutability without proof.

Synchronize validated findings and material unresolved trust risks with reproduction commands,
counterevidence and concrete mitigations. State what was scanned and what was not. A finite scan
with no validated theft path supports only that scoped conclusion, never absence of all funds risk.
