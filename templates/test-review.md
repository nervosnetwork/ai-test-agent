# [接口或行为名称] 用例评审

评审范围：[当前行为切片；其他部分明确标为未分析]
源码版本：[base tip / head / merge-base]
原始材料：[PR、需求与原始 diff 索引]

## 变更说明

- 目的与实际改动：[分别记录 PR 声明和代码观察，保留冲突]
- 前后行为：[旧行为 → 新行为]
- 直接/间接影响：[相邻路径和需要保持的兼容行为]
- 未读材料：[具体缺口或无]

## Spec

### SPEC-01：正常行为
Condition: [前置条件]
Expected: [预期行为]
Observable: [调用方可观察的结果]
Basis: [需求/协议/已确认规则的路径或链接]
Source: explicit
Testing: required

### SPEC-02：边界行为
Condition: [边界条件]
Expected: [预期行为]
Observable: [可观察结果]
Basis: [当前实现观察；等待负责人确认]
Source: observation
Testing: required

### SPEC-03：待确认行为
Condition: [场景]
Expected: [候选预期]
Observable: [预期的可观察结果]
Basis: [推断及缺少的依据]
Source: inference
Testing: required

## 测试树

按实际行为递归拆分，直到叶子有明确前置条件、操作和可观察预期。下面只示意层级，
不是固定分类或层数要求；简单行为可更浅，复杂状态和不同结果继续展开。
预算不足时保留未展开节点、原因和下一步入口，不把概览当成完整测试设计。

<!-- TEST-TREE-BEGIN -->
- [能力/行为范围]
  - [当前操作]
    - [前置状态/条件 A]
      - [AREA-01] [primary] -> SPEC-01：[操作 → 可观察结果]
    - [前置状态/条件 B]
      - [影响结果的边界或决策]
        - [AREA-02] [primary] -> SPEC-02：[操作 → 不同的可观察结果]
      - [AREA-03] [primary] -> SPEC-03：[候选行为，预期待确认]
    - [pending] [尚未展开的已知分支] — [缺少的决定/工作；下一步入口]
  - [unanalysed] [相邻行为及跨边界影响] — [未读材料及下一步源码入口]
<!-- TEST-TREE-END -->

## 待评审用例

<!-- TEST-CASES-BEGIN -->
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `[AREA-01]` | - [ ] 当[前置状态]，执行[操作] | [可直接观察的结果] | [用户或系统会遇到的具体问题] | P0 |
| `[AREA-02]` | - [ ] 当[边界或错误输入]，执行[操作] | [拒绝、回滚、恢复或状态保持] | [错误输入可能造成的具体问题] | P1 |
| `[AREA-03]` | - [ ] [尚未明确的场景] | 待确认：[需要 Reviewer 决定的结果] | [不确认会产生的行为歧义] | P1 |
<!-- TEST-CASES-END -->

## 本轮需要确认

- [B 对完整 diff → Spec 的核对：对应规则、非行为改动依据、遗漏或未读项、待确认范围排除；引用本轮 B 报告]
- [B 设计意见及逐项采纳/重复/不适用/待裁定的处理和依据]
- [预期、范围、成本或高风险争议]

<!--
Replace bracketed authoring placeholders before validation. Keep one physical row per case.
Source is explicit, observation or inference; observation/inference remains a human decision.
Testing is required, or "not_tested — <reason>". Tree primary ownership is unique;
additional references use [ref]. Branch dispositions: [pending], [unanalysed], [not_applicable], each with a reason after —.
Checkboxes mirror mappings only. Present all changed rows and stop at G1 before automation.
-->
