# [行为] 评审

范围：[当前切片；未分析部分]
版本：[base / head / merge-base]；依据：[原始需求与 diff 索引]

## 变更

- [旧行为 → 新行为；实际影响。仅补充与 PR 声明的冲突或未读材料。]

## Spec

### SPEC-01：[行为规则]
Condition: [前置条件]
Expected: [预期行为]
Observable: [调用方可观察结果]
Basis: [需求/协议/确认规则的路径或链接]
Source: explicit
Testing: required

## 测试树

<!-- TEST-TREE-BEGIN -->
- [行为]
  - [条件]：AREA-01 [primary] -> SPEC-01
<!-- TEST-TREE-END -->

## 用例

<!-- TEST-CASES-BEGIN -->
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `[AREA-01]` | - [ ] [前置条件]下[操作] | [可观察结果] | [具体故障] | P0 |
<!-- TEST-CASES-END -->

## 验证设计

- 独立预期：[独立规则／手算／协议向量及关联 Case]
- 实际入口与观察：[真实触发路径、操作后状态与有效断言]
- 证明边界：[实际验证层；恶意输入仍满足哪些前提；预期拒绝位置]

<!-- 按实际行为扩展 Spec/分支/用例，不按模板凑数。Spec 字段与标记供校验器解析，保留原样。
Source: explicit|observation|inference；后两者需人工确认。Testing: required 或 not_tested — 原因。
每个 Case 唯一 [primary]，复用用 [ref]；未完成分支用 [pending]/[unanalysed] — 原因与下一步。
仅有实际问题时添加“待确认”；链接 B 报告和 A 回复，不复制它们。
G1：本轮全部文档及 B 独立审核完成后交用户 review。确认后仅写第一个自动化用例，在 G2 等待用户确认规范。
G2 确认后自动完成剩余实现、覆盖审核及执行，不追加末尾人工门禁。 -->
