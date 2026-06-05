# liblibGameApp 当前协议恢复阶段性汇总

## 目标背景

本阶段目标已经从“继续围绕 enter-world 单链深挖”切换为两条并行主线：

1. 把 bridge/config 语义脏项拆干净。
2. 继续追除 `0x7F2` 之外是否还存在新的真网络协议。

本报告汇总截至目前所有脚本与报告得到的稳定结论，并明确哪些方向已经证伪，哪些方向应继续推进。

---

## 一、已经稳定确认的核心结论

### 1. 当前已知码表里，`0x7F2` 仍然是唯一被稳定坐实的“真网络协议码”

证据链已经形成闭环：

- outer pack:
  - `PB_DYNAMIC_PROTO_CH`
  - `tagPackData`
  - `PB_PACKDATA_CLIENT`
- handler:
  - `MpGameSurviveNetHandler`
  - `MpGameSurviveNetHandler_ver1`
- business message:
  - `PB_ROLE_ENTER_WORLD_CH`
  - `PB_RoleEnterWorldCH`
  - `handleRoleEnterWorld2Client`
  - `handleRoleEnterWorld2Host`
  - `sendMsgClientEnterHostWorld`
- core funcs:
  - `0x303FE90 sub_303FE90`
  - `0x3055718 sub_3055718`
  - `0x2FF8BF4 sub_2FF8BF4`
  - `0x2F7B8AC sub_2F7B8AC`
- bridge dispatch caller:
  - `0x445801C sub_445801C`
  - local dispatch window confirms `MOV W2, #0x7F2` before `BL sub_4451C54`

也就是说，当前最可靠的模型依然是：

`0x7F2 -> enter-world 业务链 -> MpGameSurviveNetHandler 网络路径`

### 2. 除 `0x7F2` 外，原已知码表 `0x7D3 ~ 0x7F3` 没有出现第二个像样的真网络协议闭环

优化后的 true follow-up 报告已经给出非常强的负结论：

- `0x7F2 score=18`，正锚点远高于其他码。
- 其余所有已知码 `positive_anchor_hits=0`。

这意味着：

- 如果继续只在“已知 bridge code 表”里打分，收益已经极低。
- 继续追新协议时，方法必须改变。

---

## 二、bridge/config 脏语义已经拆到较高可信度

以下几项已经可以视为当前稳定语义：

### 1. `0x7D8`

- 路径：`switch_flag_cheat + cheat_jetfly_state`
- 关键 caller：`0x44516DC`
- 不像网络协议，更像作弊标志配置位。

### 2. `0x7D9`

- 路径：`switch_flag_cheat + cheat_flymode`
- 关键 caller：`0x44516DC`
- 与 `0x7D8` 同属 cheat flag 类。

### 3. `0x7DB`

- 路径：`use-item-distance / item_type / custom_gun mixed distance-control path`
- 关键 callers：`0x44531B8`, `0x44536E4`
- 属于 use-item-distance / custom-gun 混合配置项，而非网络业务码。

### 4. `0x7ED`

- 路径：`music_paper_gain switch with item_ iteration/indexing path`
- 关键 caller：`0x4456974`
- 属于 `item_` 迭代/索引相关配置路径，不像协议消息。

此外，其余 bridge/config 语义也已大致补齐：

- `0x7D3` => heartbeat speed / time scale
- `0x7DC` => dig distance
- `0x7DD` => place-block distance
- `0x7DE` => map edit
- `0x7E7` => tackle
- `0x7E8` => grab
- `0x7E9` => dribble
- `0x7EA` => host clip / radius
- `0x7EF` => gun + system_tick

这些项整体都更像桥层配置开关/参数，不具备 `0x7F2` 那样的 `PB/handler/业务消息` 闭环证据。

---

## 三、unknown protocol hunter 两轮尝试的结果

### A. 第一轮：`liblibGameApp_unknown_protocol_hunter.py`

目标：

- 不再只盯 `KNOWN_CODES`
- 从 bind anchors / handler anchors / outer pack anchors 反扫未知 code

结果：

- 跑出了大量“未知候选码”，例如：`0x100`, `0x110`, `0x120`, `0x1B0`, `0x380`, `0xA00` 等。
- 但这批结果很快暴露出明显假阳性特征：
  1. `BIND CALLER CODE EXTRACTION` 全空。
  2. `KNOWN CONTROL ROWS` 中连 `0x7F2` 都没命中。
  3. `ANCHOR WINDOWS` 全空。
  4. 很多候选完全依赖 enter-world handler / sender 内部的普通立即数。

结论：

- 第一轮 hunter 主要抓到的是：
  - 结构偏移
  - 普通立即数
  - 字段偏移
  - 局部状态/长度/标志值
- 不是协议码本身。

### B. 第二轮：`liblibGameApp_unknown_protocol_hunter_narrow.py`

目标：

- 缩到 local dispatch / bind window
- 只保留 `sub_4451C54` 附近窗口、bind anchor 附近窗口里的立即数

结果：

- `0x7F2` 成功回到控制组里：
  - `code=0x7F2 score=4 known=yes dispatch_hits=1`
  - 其窗口明确显示：
    - caller `0x445801C`
    - `MOV W2, #0x7F2`
    - `BL sub_4451C54`
- 但 surviving unknown codes 仍然站不住：
  - `0x120`
  - `0x1D0`
  - `0x1E0`
  - `0x408`
  - `0x130`
  - `0x170`
  - `0x231`
  - `0x12D8`
  - `0x278`
  - `0x1A0`

窗口级别证据已经说明这些不是协议号，而是字段/偏移：

- `0x231` 来自 `LDRB W8, [X19,#0x231]`
- `0x12D8` 来自虚表/成员访问链 `LDR X8, [X8,#0x12D8]`
- `0x408` 来自 `LDR X9, [X19,#0x408]`
- `0x278` 来自 `STR X8, [X21,#0x278]`
- `0x1D0 / 0x1E0` 对应的是栈帧与 `item_/music_paper` 路径混入
- `0x120` 本质上也是局部对象/栈布局相关噪声，不是注册协议号

结论：

- 第二轮 narrow hunter 已经把问题钉死：
  “未知候选”大多是对象偏移/字段偏移，不是真协议号。
- 继续扫 dispatch window 里的立即数，边际收益已经很低。

---

## 四、当前最重要的方法论结论

现在已经可以明确：

1. `sub_4451C54` 的 caller window 确实能可靠恢复“已知 bridge/config code”与 `0x7F2`。
2. 但如果未知协议号存在，它未必会以简单 `MOV W2, #imm` 的形式长期暴露在当前已观察到的局部窗口里。
3. 继续从“立即数枚举”角度硬扫，容易被这些东西污染：
   - 成员偏移
   - 栈偏移
   - 虚表槽偏移
   - 配置字段偏移
   - builder 中间对象布局

因此，下一步应停止“未知立即数打分”主线，改追：

- `sub_4451C54` 把 `W2` 最终写到哪里
- 谁消费这个 code
- 是进入 map/table/registry，还是通过虚表分发到下游

换句话说，下一阶段的关键不再是：

- “有哪些可疑立即数？”

而是：

- “协议号在 bridge_dispatch_entry 里是如何被存储、转发、索引、消费的？”

---

## 五、已经新建的下一步脚本

已写入新脚本：

- `E:/TEMP_SHARE/ida_scripts/liblibGameApp_protocol_table_writer_trace.py`

目标：

- 沿 `sub_4451C54` 的下游写入/消费链追踪
- 重点看：
  - `0x445FEA8 bridge_state_lookup`
  - `0x4443D9C downstream_object_builder`
  - `0x7CC0904 value_box_builder`
  - `0x8850450 parsed_int_value_setter`
  - `0x6660D90 client_msgcode_downstream_stage`
  - `0x8852C0C bridge_virtual_dispatch_loader`
- 同时保留已知 caller 作为对照：
  - `0x44516DC`
  - `0x44531B8`
  - `0x44536E4`
  - `0x4454A4C`
  - `0x4456974`
  - `0x4457554`
  - `0x44578E8`
  - `0x445801C`

这支脚本的意义是：

- 从“枚举 code”转向“恢复 code 的存储/索引模型”。
- 这更符合当前证据形态，也更可能逼近未知协议真正的注册表/容器。

---

## 六、当前阶段最可靠的工作结论

到目前为止，可以把结论压缩成下面几句：

1. `0x7F2` 是当前唯一稳定坐实的真网络协议码。
2. `0x7D8/0x7D9/0x7DB/0x7ED` 等脏桥语义已经基本拆清，属于 bridge/config 路径而非真协议。
3. 两轮 unknown protocol hunter 都没有成功找出可信的新协议号。
4. narrow pass 已确认大部分 surviving unknown 候选是字段偏移/对象偏移，不是协议码。
5. 下一步应转入 `sub_4451C54` 下游 table / writer / consumer 链追踪，而不是继续扫立即数。

---

## 七、建议的后续执行顺序

建议按这个顺序继续：

1. 运行：
   - `E:/TEMP_SHARE/ida_scripts/liblibGameApp_protocol_table_writer_trace.py`

2. 重点看报告里：
   - `bridge_dispatch_entry` 内部如何使用 `W2`
   - `sub_445FEA8 / sub_4443D9C / sub_6660D90` 是否出现 `map/table/index` 写入
   - `sub_8852C0C` 是否提供“协议号 -> 虚表槽/回调槽”的桥

3. 如果这条链仍然过宽，再继续拆成更窄的脚本：
   - 专盯 `sub_4451C54` 内部 `W19/W2` 流向
   - 或专盯 `sub_8852C0C / sub_6660D90` 的写表动作

---

## 八、目前已知的所有发包逻辑

这里的“发包逻辑”仅指**目前已经有稳定证据支撑**的发送链，不把仅出现 bind/type 名称、但尚未和明确业务消息闭环起来的项强行当作已确认发包协议。

### 1. 当前唯一被完整闭环坐实的发包业务：`0x7F2 -> enter-world`

目前已经能稳定串起来的发送链是：

- protocol code:
  - `0x7F2`
- business message:
  - `PB_ROLE_ENTER_WORLD_CH`
  - `PB_RoleEnterWorldCH`
- send funcs:
  - `0x303FE90 sub_303FE90`
  - `0x3055718 sub_3055718`
- recv funcs / peer handlers:
  - `0x2FF8BF4 sub_2FF8BF4`
  - `0x2F7B8AC sub_2F7B8AC`
- outer pack / envelope:
  - `PB_DYNAMIC_PROTO_CH`
  - `tagPackData`
  - `PB_PACKDATA_CLIENT`
- handler family:
  - `MpGameSurviveNetHandler`
  - `MpGameSurviveNetHandler_ver1`

可以把这条链压缩成：

`sendMsgClientEnterHostWorld -> PB_ROLE_ENTER_WORLD_CH -> PB_DYNAMIC_PROTO_CH / packdata outer layer -> bridge dispatch code 0x7F2 -> MpGameSurviveNetHandler network path`

### 2. 已确认的发送函数与证据

#### A. `0x303FE90 sub_303FE90`

这是目前最明确的主发送函数之一。稳定证据包括：

- 字符串命中：
  - `MpGameSurviveNetHandler::sendMsgClientEnterHostWorld PB_ROLE_ENTER_WORLD_CH`
- 报告 xref：
  - `0x3040980 -> func=0x303FE90 sub_303FE90`
- 语义：
  - `MpGameSurviveNetHandler` 侧发起 `sendMsgClientEnterHostWorld`
  - 业务消息是 `PB_ROLE_ENTER_WORLD_CH`
  - 该发送路径最终与 `0x7F2` 的 bridge dispatch 闭环对应

#### B. `0x3055718 sub_3055718`

这是 enter-world 发包链的 ver1 变体发送函数。稳定证据包括：

- 字符串命中：
  - `MpGameSurviveNetHandler_ver1::sendMsgClientEnterHostWorld PB_ROLE_ENTER_WORLD_CH`
- 报告 xref：
  - `0x3055F40 -> func=0x3055718 sub_3055718`
- 语义：
  - `MpGameSurviveNetHandler_ver1` 侧也存在同名发包逻辑
  - 说明 enter-world 发送链至少存在主版本 + ver1 变体两套已知实现

### 3. 已确认的收包 / 对端处理函数

当前已知发包逻辑不是孤立字符串，而是有接收端业务处理作为闭环支撑：

#### A. `0x2FF8BF4 sub_2FF8BF4`

稳定对应 host 侧 enter-world 处理：

- `handleRoleEnterWorld2Host PB_RoleEnterWorldCH`
- `MpGameSurviveNetHandler::handleRoleEnterWorld2Host() pb parse err`
- `MpGameSurviveNetHandler::handleRoleEnterWorld2Host() worldmgr is null`
- `MpGameSurviveNetHandler::handleRoleEnterWorld2Host() uin is 0, forbid enter`
- `MpGameSurviveNetHandler::handleRoleEnterWorld2Host() getConnection()->isMemberFull() full`

这说明 enter-world 发包的落点不是抽象 bind，而是明确进入 `PB_RoleEnterWorldCH` 的 host 业务处理路径。

#### B. `0x2F7B8AC sub_2F7B8AC`

稳定对应 client 侧 enter-world 处理：

- `MpGameSurviveNetHandler::handleRoleEnterWorld2Client():`

因此当前最可靠的对端业务模型是：

- client 发起 enter-world 消息
- host / client 两侧都存在 `MpGameSurviveNetHandler` 家族处理函数
- `0x7F2` 是该业务链已坐实的 bridge code

### 4. 已确认的外层包装与发送外壳

目前已知 enter-world 发包不是裸业务消息，而是经过 outer pack / transport envelope 包装。

#### A. `PB_DYNAMIC_PROTO_CH`

当前最强证据：

- 报告中直接出现：
  - `PB_DYNAMIC_PROTO_CH sendToHost`
- 并且在已有闭环中，它与：
  - `PB_ROLE_ENTER_WORLD_CH`
  - `sendMsgClientEnterHostWorld`
  - `0x303FE90 / 0x3055718`
  - `0x7F2`
 共同出现

这说明当前最可信的发送模型是：

- 业务 pb：`PB_ROLE_ENTER_WORLD_CH`
- 外层动态包：`PB_DYNAMIC_PROTO_CH`
- 发送方向：`sendToHost`

#### B. `tagPackData` 与 `PB_PACKDATA_CLIENT`

这两类 outer pack 类型已稳定出现于 bind 证据中：

- `tagPackData`
  - 更偏 host / tagged outer data 路径
- `PB_PACKDATA_CLIENT`
  - 更偏 client packdata 路径

它们的重要性在于：

- 说明 `MpGameSurviveNetHandler` 家族并不是只直接处理业务 pb
- 还存在外层 packdata 包装层，再由 handler 绑定到具体处理函数

### 5. 已确认的 handler / bind 形态

以下 bind/type 证据已经稳定，可用于描述**我们现在知道的发包外层接口形态**。

#### A. 通用网络 handler 锚点

- `0x62B2564 sub_62B2564`
  - `std::__bind<void (GameNetClientMsgHandler::*)(PB_PACKDATA_CLIENT const&), ...>`
- `0x62B2B80 sub_62B2B80`
  - `std::__bind<void (GameNetHostMsgHandler::*)(uint, tagPackData const&), ...>`

这说明更通用的网络分发框架里，至少有：

- `GameNetClientMsgHandler <-> PB_PACKDATA_CLIENT`
- `GameNetHostMsgHandler <-> uint + tagPackData`

#### B. `MpGameSurviveNetHandler` 家族已知 bind

- `0x3041AF0 sub_3041AF0`
  - `std::__bind<void (MpGameSurviveNetHandler::*)(uint, tagPackData const&), ...>`
- `0x3041BA0 sub_3041BA0`
  - `std::__bind<void (MpGameSurviveNetHandler::*)(PB_PACKDATA_CLIENT const&), ...>`
- `0x3041C54 sub_3041C54`
  - `std::__bind<void (MpGameSurviveNetHandler::*)(int, tagPackData const&), ...>`
- `0x3041D08 sub_3041D08`
  - `std::__bind<bool (MpGameSurviveNetHandler::*)(PB_PACKDATA_CLIENT const&), ...>`
- `0x3056580 sub_3056580`
  - `std::__bind<void (MpGameSurviveNetHandler::*)(uint, tagPackData const&), MpGameSurviveNetHandler_ver1*, ...>`

这些证据说明：

1. `MpGameSurviveNetHandler` 既处理 `tagPackData`，也处理 `PB_PACKDATA_CLIENT`。
2. 参数签名存在 `void / bool`、`uint / int` 的多种变体，说明这是一个多入口网络 handler 家族，而不是单一发送函数。
3. `MpGameSurviveNetHandler_ver1` 不是孤立符号，而是实际参与到了 bind 链中。

### 6. 目前能确认的“发包逻辑范围”与“不能确认的部分”

#### 已确认的部分

目前真正能写成稳定结论的发包逻辑只有：

- `sendMsgClientEnterHostWorld`
- 消息体：`PB_ROLE_ENTER_WORLD_CH`
- 外层壳：`PB_DYNAMIC_PROTO_CH`
- outer pack 相关类型：`tagPackData` / `PB_PACKDATA_CLIENT`
- handler 家族：`MpGameSurviveNetHandler` / `MpGameSurviveNetHandler_ver1`
- bridge code：`0x7F2`

#### 还不能强行确认的部分

虽然 bind/type 证据里已经暴露出很多接口形态，但当前还**不能**把它们都直接提升为“已知独立发包协议”，原因是：

1. 它们目前大多只有 bind/type 级证据。
2. 还没有像 `0x7F2` 一样形成 `协议号 -> 业务消息 -> send func -> recv func -> handler` 的完整闭环。
3. 两轮 unknown hunter 已证明，继续把零散立即数硬解释成新协议号，假阳性很高。

所以现阶段更准确的表述是：

- **我们已经知道 enter-world 这条发包链的完整骨架。**
- **我们也已经知道它挂载在 `MpGameSurviveNetHandler` / `GameNet*MsgHandler` 这一整套 packdata 分发框架上。**
- **但除 `0x7F2` 外，还没有第二条发送协议被稳定坐实到同等可信度。**

---

## 附：当前已落地的关键脚本

- `liblibGameApp_true_network_candidate_recover.py`
- `liblibGameApp_bridge_config_semantic_recover.py`
- `liblibGameApp_dirty_bridge_semantics_narrow.py`
- `liblibGameApp_true_protocol_followup.py`
- `liblibGameApp_unknown_protocol_hunter.py`
- `liblibGameApp_unknown_protocol_hunter_narrow.py`
- `liblibGameApp_protocol_table_writer_trace.py`

## 附：当前最重要的报告

- `liblibGameApp_true_network_candidate_recover_report.txt`
- `liblibGameApp_bridge_config_semantic_recover_report.txt`
- `liblibGameApp_dirty_bridge_semantics_narrow_report.txt`
- `liblibGameApp_true_protocol_followup_report.txt`
- `liblibGameApp_unknown_protocol_hunter_report.txt`
- `liblibGameApp_unknown_protocol_hunter_narrow_report.txt`

---

## 结尾结论

目前最关键的判断已经成立：

**“继续从未知立即数里猜协议号”这条路基本到头了。**

真正该追的是 `sub_4451C54` 之后那条 `code` 写入/消费链。
