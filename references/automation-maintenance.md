# Automation, Maintenance, and PR Work

## Implement confirmed cases

1. Read the affected review rows and find existing code with `TEST-MAP: <CASE-ID>`.
2. Use the target's native language, runner, fixtures, and CI conventions.
3. Prefer direct, readable arrange-act-assert tests. Add an abstraction only when it removes meaningful repetition without hiding the behavior or oracle.
4. Use assertions on the smallest caller-observable result, state change, side effect, or error needed to prove the expected behavior. Avoid incidental details and tautologies.
5. Update each affected scenario checkbox to `- [x]` when its `TEST-MAP` is present, or `- [ ]` when its mapping is removed.
6. Run one focused deterministic command and the mapping checker; it validates checkbox-to-code consistency.
7. If justified, run one broader suite. Use live networks only for behavior that requires them, with bounded retries.
8. Check CI once after pushing. Report pending status rather than polling unless the user explicitly requests waiting.

Explain added automation compactly. Group IDs that share the same reason and oracle; expand failed, ambiguous, or unusually risky cases only.

## Maintain an existing project

1. Read root `AGENTS.md`, the affected review document, relevant feedback, and mapped tests.
2. Resolve and reuse the declared source checkout.
3. For PR work, inspect the base/head diff first and widen source reads only as needed.
4. Preserve IDs when behavior remains the same. Add or remove rows only when observable behavior is added or removed.
5. If a row changes materially, stop at the review gate before modifying mapped tests.
6. After confirmation, update the minimum automation needed for a concrete failure mode and verify the affected scope.

For a previously unmapped area, return to the area-map and review gates.

## PR handoff

```text
PR impact: <changed behavior> -> <review document and IDs> -> <test action>
Changed cases: <only changed IDs and expectations>
Added automation: <group shared reasons/oracles; expand exceptions>
Coverage: <mapped>/<reviewed>; unmapped: <IDs or none>
Verification: <command> -> <literal result and exit status>
Residual risk: <ambiguous, manual, unavailable, or none>
Next gate: <review confirmation or implementation action>
```

Omit irrelevant fields. Passing tests support the identified behavior but do not prove unknown risks absent.
