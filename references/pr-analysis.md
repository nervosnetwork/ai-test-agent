# PR analysis

## Default: compact impact review

Reuse the known checkout and revision; inspect the diff summary, affected behavior and existing cases.
Read only needed source ranges. Update one review with scope/source, a short before → after note,
required Spec → 测试树 → 用例 and changed rows using `templates/test-review.md`. Validate the
selected design, mark unread branches and resume points; stop at G1
for material case changes. An impact-only question needs a short answer, not new review files.
Do not launch B, hash a whole workspace or create reports for this path. It is not full-PR acceptance.

## Full PR-v2: explicit request or existing project requirement

Use the rest of this reference only for requested independent design/coverage review or a controlled
PR-v2 workflow. Continue active scope state without repeating completed stages; never switch modes
to bypass gates. Use `templates/test-review-full.md`; all existing checks below remain required.


Keep the skill's reviewer-first gates. Reuse the product checkout; never overwrite a conflicting path.
For large PRs, present a change overview and select one observable-behavior slice. Label other slices
and cross-boundary effects unanalysed. Whole-PR acceptance requires aggregation, not renaming a slice.
Keep that overview hierarchical and recursively expand the selected slice using
[decomposition.md](decomposition.md). A large diff is not a reason to flatten
states, conditions and distinct outcomes into first-level cases. Preserve unfinished branches with
specific missing evidence and resume points; scope selection limits breadth, not depth.
The complete frozen diff remains B's coverage denominator even for a slice: each change needs a Spec
mapping, a justified non-behavior disposition, or a visible gap/exclusion. Selecting fewer Cases must
not remove changes from the diff inventory. See `test-design.md` for the diff→Spec gate.

Fix both repositories: product PR, base tip, head, merge-base/diff base; test-project revision,
selected reviews and Case set, uncommitted tests, shared helpers/fixtures, build/runner config,
raw PR description, requirements, test command and environment constraints. A branch/PR number
is an index, not an immutable version. Preserve raw materials for B rather than only A's summary.

Write purpose, actual edits, before/after observable behavior, direct/indirect impact, compatibility,
and unread inputs. Keep PR-description/diff conflicts visible. Each Spec rule needs condition,
expected behavior, observation and cited basis. Classify its Source as `explicit` (a requirement,
protocol or confirmed rule), `observation` (what code does), or `inference` (candidate expectation).
These are provenance categories, not subjective confidence scores. Observation is not a requirement.
Do not discard a plausible defect just because no Spec yet exists; show evidence and ask for a decision.
Accepted limitations have a specific scope and do not excuse newly discovered effects.

## Controlled local entry

After fetching raw PR materials through available project tools, save them in the test project.
The script does not fetch PRs, change the product checkout or automatically discover every dependency.
It hashes the entire nonignored dirty product tree, selected reviews, declared dependencies and all
suite/test inputs. Explicitly include root-level runner, lockfile and build inputs; changes in unknown
dependencies warrant conservative re-review.

```sh
python3 scripts/pr_workflow.py --root . analyze \
  --scope connection-limit --pr '<PR URL>' --product source/product \
  --base '<base commit>' --head '<head commit>' \
  --review reviews/p2p/connection-limit.md \
  --material inputs/pr-description.md --material inputs/requirements.md \
  --dependency pyproject.toml --dependency scripts/run_unittest.py \
  --scope-boundary 'Connection admission only; handshake accounting unanalysed' \
  --command '["python3","scripts/run_unittest.py","discover","-s","suites/p2p/tests"]'
```

`--review`, `--material`, `--dependency`, `--require-case` repeat. The runner command is JSON argv,
not a shell command. A unique scope has one current state; `prepare` refreshes its design rather than
creating per-run archives. The current product checkout must match head. Inspect
`reports/<scope>/input-index.json` and `product.diff`, then follow [test-design.md](test-design.md).
