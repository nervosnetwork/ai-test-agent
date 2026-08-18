# Initialize a Test Project

Initialization has three conversational gates. Complete only the current gate.

## Gate 1: test-area map

1. Inspect architecture, public entry points, state ownership, build/test commands, CI, and existing tests using targeted reads.
2. Select only runners or assurance approaches supported by evidence.
3. Generate the skeleton:

   ```bash
   python3 <skill>/scripts/init_repo_tests.py \
     --project <name> \
     --source-repo <path-or-url> \
     --suites <suite> [<suite> ...] \
     --output <test-project>
   ```

4. Fill stable target facts in root `AGENTS.md`.
5. Replace `reviews/README.md` with a concise area map: responsibility, boundary, entry points, observable outcomes, and planned review paths.
6. Present the map and stop. Do not create review rows or tests.

## Gate 2: review cases

After map confirmation, select one coherent review document and follow `review-cases.md`. Stop after presenting the changed rows.

## Gate 3: automation

After row confirmation, follow `automation-maintenance.md`. Implement only confirmed IDs.

## Layout choice

Use the flat layout for one runner or assurance approach:

```text
<project>-tests/
├── AGENTS.md
├── README.md
├── source/<project>/
├── reviews/<area>/<behavior>.md
├── tests/ or benchmarks/ or targets/
├── fixtures/
└── scripts/check_test_map.py
```

Create `suites/<suite>/` only for genuinely independent runners such as API, P2P, performance, or fuzz. Keep case IDs unique across the project.

Reuse a matching checkout under `source/<project>/`; clone only when absent and never overwrite a conflicting path.
