# Initialize a Test Project

Use the same two human gates as [workflow-gates.md](workflow-gates.md), not a separate map approval.
Honor an explicit map-only request by stopping at the map; otherwise prepare the selected scope for G1.

## Preparation: test-area map

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
5. Replace `reviews/README.md` with a concise hierarchical area map: responsibility, boundary, entry points, observable outcomes, and planned review paths. Split broad areas into coherent capabilities/behavior groups rather than a flat module list. Follow the overview rules in [decomposition.md](decomposition.md); mark unread branches with reasons and next entry points. This is a navigation map, not completed test coverage; Case rows belong in the selected review documents.
6. Continue preparing those documents when included in the request; do not write automated tests yet.

## G1: completed test-point documents and B review

For all reviews in the requested scope, follow `review-cases.md` with the compact template.
Spec → 测试树 → 用例 is mandatory even for a simple behavior; use `decomposition.md` to expand only
as far as observable outcomes require. This does not activate full PR-v2. Validate the selected design,
preserve unfinished frontier nodes, complete independent B review and address findings. Then stop
with all selected documents and changed rows for the user's review.

## G2: first automated Case

After G1 confirmation, follow `automation-maintenance.md` to implement and check only the first Case.
Stop for the user's standards confirmation; after approval, automate the remaining confirmed scope
without per-Case or final human gates.

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
