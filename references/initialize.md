# Initialize a Test Project

Initialization has three design stages. Follow [workflow.md](workflow.md): stop after the requested
map/case review in review-only mode; in authorized end-to-end mode complete all requested stages.

## Stage 1: test-area map

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
5. Replace `reviews/README.md` with a concise hierarchical area map: responsibility, boundary, entry points, observable outcomes, and planned review paths. Split broad areas into coherent capabilities/behavior groups rather than a flat module list. Follow the overview rules in [decomposition.md](decomposition.md); mark unread branches with reasons and next entry points. This is a navigation map, not completed test coverage; keep Case rows for Stage 2.
6. In review-only mode present the map and stop. In end-to-end mode retain the map and continue
   with the requested review scope; do not ask for another initialization confirmation.

## Stage 2: review cases

After map review, select a coherent review and follow `review-cases.md` with the compact template.
Spec → 测试树 → 用例 is mandatory even for a simple behavior; use `decomposition.md` to expand only
as far as observable outcomes require. This does not activate PR-v2 or B review. Validate the
selected design and preserve unfinished frontier nodes. Stop after presenting changed rows only
when the user requested staged review or an actual product decision remains unresolved.

## Stage 3: automation

Follow `automation-maintenance.md` for confirmed rows or the unambiguous rows covered by the user's
end-to-end authorization. A pending decision blocks dependent Cases, not the whole unrelated scope.

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
`docs/ai-test-agent/`. Both compact and full templates are included; full PR-v2 remains opt-in. Initialization remains additive and does not rewrite existing generated copies.
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
that baseline using `workflow.md` (G1 remains required for full PR-v2). Existing `[x]` Cases start
with semantic evidence `not_reviewed`, never `covered`.
Other legacy reviews still participate in global duplicate/structure checks. Without B, keep independent
review incomplete rather than having A award itself B approval.
