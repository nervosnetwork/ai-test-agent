# Automation and maintenance

1. Reuse project instructions, source checkout, affected rows, mappings and current gate confirmations.
   Follow [workflow-gates.md](workflow-gates.md): G1 requires completed documents, B review and human
   approval; then implement only the first Case and stop at G2 for standards confirmation.
2. After G2 confirmation, implement the remaining confirmed Cases automatically using that example.
   Implement direct, readable tests with native runners/fixtures. Avoid abstraction that hides
   assertions which prove the expected behavior. Keep setup/action/oracle visible; group shared setup.
3. Synchronize all affected inputs, actions, assertions, mappings and scenario checkboxes. Remove obsolete
   mappings after merges/deletions. Wording-only changes need alignment inspection, not automatic rewrites.
4. Run focused deterministic tests, `check_test_design.py --review <path>` and
   `check_test_map.py --review <path>` once after the batch. Broaden
   for affected shared dependencies, not by default. Bound live-network retries; inspect CI once.

Report changed IDs, command/result/exit status and any actual gap or next decision. Mapping presence
is not assertion coverage or execution. Avoid per-case success explanations and extra summary files.
Never weaken expectations or modify product code merely to turn a run green.

Follow-up renames, moves, style cleanups and runner fixes that keep intent and assertions stay on this
compact path even inside a PR-v2 scope: no G1, B call, freeze or report. Edit, run focused tests, hand off.

For ordinary PR impact use the compact route in `pr-analysis.md`. For an active or explicitly requested
full PR-v2 scope, follow `coverage-review.md` after G2 and batch implementation: freeze implementation,
independent B coverage evidence, managed comments and frozen execution, without a final human gate.
Changed design returns to G1; changed test dependencies return to B coverage review automatically.
Compact work claims only its actual B design review, not independently reviewed implementation coverage.

## Test comment format

For Python mapped tests, keep `# TEST-MAP: <CASE-ID>` above the test definition (above any decorators).
Start the function with a Chinese docstring listing the scenario steps as `1.`, `2.`, `3.`, …:
describe setup/actions and the observable checks, not implementation trivia. Before each corresponding
code block, add a concise `# 1. …`, `# 2. …`, … comment with matching numbering and meaning.
Use as many steps as the scenario needs; three is an example, not a fixed count. Separate step blocks
with blank lines. Keep comments aligned when actions or assertions change; retain Case IDs and behavior
for comment-only edits. Other languages use native comments for the same structure.

Format example (ellipses stand for existing test code, not an executable test implementation):

```python
# TEST-MAP: VT2-45
def test_locally_rejected_slow_transaction_recovers_when_conflict_is_replaced(self):
    """
    1. 慢交易 A 网络超时后隔离对端；快速交易 B 占用 A 的输入。
    2. 本地提交 A，检查手续费不足以替换 B 而返回 RBFRejected。
    3. 交易 C 替换 B 后释放 A 的输入；不重交 A，检查它自动恢复并确认。
    """
    # 1. 构造 A 超时后隔离对端、B 占用 A 输入的状态。
    ...

    # 2. 本地提交 A，断言因替换手续费不足而返回 RBFRejected。
    ...

    # 3. 用 C 替换 B；不重交 A，断言 A 自动恢复并确认。
    ...
```
