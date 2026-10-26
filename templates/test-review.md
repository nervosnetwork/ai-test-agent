# [接口或行为] 用例

范围：[本轮行为；未分析部分]
依据：[需求/源码路径与版本；实现观察或推断须注明]

## Spec

### SPEC-01：[可观察行为规则]
Condition: [前置条件]
Expected: [预期行为]
Observable: [调用方可观察结果]
Basis: [需求/协议/确认规则的路径或链接]
Source: explicit
Testing: required

## 测试树

<!-- TEST-TREE-BEGIN -->
- [行为]
  - [条件与结果]：AREA-01 [primary] -> SPEC-01
<!-- TEST-TREE-END -->

## 用例

<!-- TEST-CASES-BEGIN -->
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `[AREA-01]` | - [ ] [前置条件]下[操作] | [可观察结果] | [具体故障] | P0 |
<!-- TEST-CASES-END -->

## 验证设计

- 独立预期：[预期值／规则的独立来源；共用同一 oracle 的用例合并说明]
- 实际入口与观察：[经过什么真实路径、操作后检查什么新结果]
- 证明边界：[host／HTTP／浏览器注入／实际 VM／真实节点；反例应在何处拒绝]

<!-- 删除本注释和未使用的占位项，但保留 Spec、测试树、用例三节及两个 TEST 块标记。
Source: explicit|observation|inference；后两者需人工确认。Testing: required 或 not_tested — 原因。
每个 Case 唯一 [primary]，复用用 [ref]；未完成分支用 [pending]/[unanalysed] — 原因与下一步。
仅有实际问题时追加“待确认”；预期未定写“待确认：具体决定”。完整 PR-v2 使用 test-review-full.md。
按用户授权选择仅评审或连续完成；仅评审时展示完整变更行并等确认。完整 PR-v2 保留 G1。
勾选只表示 TEST-MAP 存在；运行结果和安全性质证明分别报告。 -->
