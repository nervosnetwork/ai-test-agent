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

## Layout

Keep reviewer-facing intent centralized at the root and group all executable automation by module or runner under `suites/`, even when the project starts with one suite:

```text
<project>-tests/
├── AGENTS.md
├── README.md
├── source/<project>/
├── reviews/<area>/<behavior>.md
├── suites/<suite>/
│   ├── tests/ or case/ or benchmarks/ or targets/
│   └── fixtures/
└── scripts/check_test_map.py
```

Do not create suite-local `reviews/` copies. Add another `suites/<suite>/` directory when a new module or runner needs separate commands, fixtures, or executable ownership. Keep case IDs unique across the project.

Reuse a matching checkout under `source/<project>/`; clone only when absent and never overwrite a conflicting path.

## v2 assets and selected migration

New projects copy standalone v2 runtime scripts, schemas, templates and references under
`docs/ai-test-agent/`. Initialization remains additive and does not rewrite existing generated copies.
Keep `reports/` and `.ai-test-agent/` ignored. Updating the installed Skill does not update project files.

For an old project, preview before applying, using the migration tool from the installed Skill:

```sh
python3 <skill>/scripts/migrate_repo_tests.py --root <test-project> \
  --plan <test-project>/.ai-test-agent/migration/plan.json
# Inspect migration.patch, proposed files and conflicts; only after explicit approval:
python3 <skill>/scripts/migrate_repo_tests.py --root <test-project> \
  --plan <test-project>/.ai-test-agent/migration/plan.json --apply --confirm <printed-confirmation-hash>
# Roll back only unchanged migrated files using the same reviewed plan:
python3 <skill>/scripts/migrate_repo_tests.py --root <test-project> \
  --plan <test-project>/.ai-test-agent/migration/plan.json --rollback --confirm <printed-confirmation-hash>
```

The preview preserves custom AGENTS prose and proposes runtime/template updates explicitly. Merge conflicting custom instructions/templates into the `proposed/` files, then rerun the
migration command with `--refresh-plan`. Inspect the rebuilt patch and use its new confirmation hash;
unrefreshed modified proposals are rejected rather than silently applied. Destination changes since
preview require a fresh plan. No reviews, Case IDs or TEST-MAP comments are renumbered or rewritten. Do not use
initializer `--force` for a blind upgrade. Add Spec/tree/blocks only to the current behavior, then review
that baseline at G1. Existing `[x]` Cases start with semantic evidence `not_reviewed`, never `covered`.
Other legacy reviews still participate in global duplicate/structure checks. Without B, keep independent
review incomplete rather than having A award itself B approval.
