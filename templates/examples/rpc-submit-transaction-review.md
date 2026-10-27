# `submit_transaction` RPC 用例评审

评审范围：确认交易提交接口的成功、输入校验、下游失败和重复提交行为  
源码版本：示例 revision

## 接口说明

请求：

```json
{"jsonrpc":"2.0","id":1,"method":"submit_transaction","params":{"raw_tx":"0x010203..."}}
```

成功：返回交易哈希。

```json
{"jsonrpc":"2.0","id":1,"result":{"tx_hash":"0xabc123..."}}
```

失败：参数错误返回 `-32602`；交易被接纳服务拒绝返回 `-32010`；接纳服务不可用返回 `-32001`。

接口负责参数检查、交易解码、调用交易接纳服务并返回结果；签名、手续费、持久化和广播规则由其他模块负责。

## Spec

### SPEC-01：成功提交
Condition: 交易格式正确且接纳服务接受
Expected: 只调用一次接纳服务并返回交易哈希
Observable: RPC 结果包含接纳后的哈希
Basis: 上述接口说明；示例 revision
Source: explicit
Testing: required

### SPEC-02：缺少参数
Condition: 请求缺少 raw_tx
Expected: 拒绝请求且不调用接纳服务
Observable: RPC 返回 -32602
Basis: 上述接口说明；示例 revision
Source: explicit
Testing: required

### SPEC-03：非法编码
Condition: raw_tx 编码不合法
Expected: 拒绝请求且服务保持可用
Observable: RPC 返回 -32602；进程继续响应
Basis: 上述接口说明；示例 revision
Source: explicit
Testing: required

### SPEC-04：请求过大
Condition: 解码后的交易超过大小限制
Expected: 在接纳前拒绝并限制资源使用
Observable: RPC 返回拒绝；接纳服务未调用
Basis: 示例 revision 的请求大小限制；错误码待确认
Source: inference
Testing: required

### SPEC-05：接纳服务拒绝
Condition: 交易可解码但被接纳服务拒绝
Expected: 返回拒绝原因且不入队
Observable: RPC 返回 -32010
Basis: 上述接口说明；示例 revision
Source: explicit
Testing: required

### SPEC-06：接纳服务不可用
Condition: 接纳服务超时或不可用
Expected: 返回失败且后续请求可继续处理
Observable: RPC 返回 -32001 且无交易哈希
Basis: 上述接口说明；示例 revision
Source: explicit
Testing: required

### SPEC-07：重复提交
Condition: 连续两次提交同一笔有效交易
Expected: 待确认：幂等成功或约定的重复错误；不能重复入队
Observable: 第二次 RPC 结果与入队次数
Basis: 示例 revision；重复提交契约待确认
Source: inference
Testing: required

## 测试树

<!-- TEST-TREE-BEGIN -->
- 交易提交
  - 接纳成功：RPC-01 [primary] -> SPEC-01
  - 输入拒绝
    - 缺少参数：RPC-02 [primary] -> SPEC-02
    - 非法编码：RPC-03 [primary] -> SPEC-03
    - 超过大小限制：RPC-04 [primary] -> SPEC-04
  - 接纳失败
    - 明确拒绝：RPC-05 [primary] -> SPEC-05
    - 超时或不可用：RPC-06 [primary] -> SPEC-06
  - 重复请求：RPC-07 [primary] -> SPEC-07
<!-- TEST-TREE-END -->

## 用例

<!-- TEST-CASES-BEGIN -->
| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | - [ ] 提交格式正确且可以被接纳的交易 | 接纳服务只调用一次；返回接纳后的交易哈希 | 正常交易提交失败，或者同一请求被处理多次 | P0 |
| `RPC-02` | - [ ] 请求中缺少 `raw_tx` | 返回 `-32602`；不调用接纳服务 | 不完整请求进入核心交易逻辑 | P1 |
| `RPC-03` | - [ ] `raw_tx` 没有 `0x` 前缀、包含非十六进制字符或长度为奇数 | 返回 `-32602`；不调用接纳服务；RPC 进程保持正常 | 非法编码造成错误交易提交或服务异常 | P1 |
| `RPC-04` | - [ ] 解码后的交易超过请求大小限制 | 在调用接纳服务前拒绝；资源使用不超过配置限制 | 超大请求造成内存或 CPU 资源耗尽 | P1 |
| `RPC-05` | - [ ] 交易能解码，但接纳服务拒绝该交易 | 返回 `-32010` 和拒绝原因；交易不入队 | 被拒绝的交易被错误报告为成功 | P0 |
| `RPC-06` | - [ ] 接纳服务超时或不可用 | 返回 `-32001`；不返回交易哈希；下一次请求仍能处理 | 下游故障被错误报告为成功，或单次超时拖垮接口 | P1 |
| `RPC-07` | - [ ] 连续两次提交同一笔有效交易 | 待确认：两次返回相同哈希，或者第二次返回约定的重复错误；不得产生两次入队副作用 | 客户端重试时产生重复处理或不兼容行为 | P1 |
<!-- TEST-CASES-END -->

## 本轮需要确认

- `RPC-07`：重复提交究竟是幂等成功还是返回重复错误。
- `RPC-04`：超大请求使用 `-32602` 还是单独的错误码。
- 其余用例的场景、结果和优先级是否符合接口契约。

<!--
Review-only work stops before implementation. Authorized end-to-end work can self-review and
implement unambiguous Cases; keep RPC-07's business decision pending. Tests map directly with
comments such as: TEST-MAP: RPC-02. Mapping alone never establishes execution or behavior proof.
-->
