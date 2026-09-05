# 晋江质量架构 · 项目级工作流 v1

> 目的：把"晋江爆款 / 上瘾"这一模糊目标，拆成**可分层、可验证、可改稿、可审计**的四级判断链。
>
> 适用：本季及所有未来季的连载改稿循环。
>
> 维护方：项目维护者。每两周或每 ≥ 30 章累计改稿后，必须复审本文档与下层文档是否一致。
>
> 不替代：`晋江爆款基线.md`（工程 5 维 + 真人 5 维）、`novel-workflow.md`（canonical 流程）、
> `reader-subagent-workflow.md`（盲读协议）、`SKILL.md`（AI 入口）。

## 0. 三句话

1. "晋江爆款"不是晋江官方术语，是创作者社区的口语说法。它**没有**一个可被引用的官方标准。
2. 我们把"爆款"翻译成"工程 5 维 + 真人 5 维**同章双轨打分**"，每条基线必须能在本文档里被指出证据层（晋江官方 / 行业共识 / 工程启发式 / 真人读者）。
3. 没有真人读者证据（reader L2 ≥ 1）时，**任何**"读者会追 / 爆款 / 上瘾"判断一律禁止。工程分只能叫"工程 5 维已达成 / 未达成"。

## 1. 四层判断栈（不可漏层）

```
┌──────────────────────────────────────────────────────────────┐
│ S0  晋江官方可验证事实                                          │
│     - help.jjwxc.net 收藏、VIP、营养液、霸王票、合规、标语       │
│     - 不能回答"什么是爆款文笔"，只能回答"什么条件可签约"         │
├──────────────────────────────────────────────────────────────┤
│ S1  行业共识（标记为推断）                                       │
│     - 钩子前置、信息密度、情感碾压、付费节点、关系升级、反降智     │
│     - 来自创作者社区与公开访谈，不是官方文档                       │
├──────────────────────────────────────────────────────────────┤
│ S2  本项目工程启发式（机器可打分）                                │
│     - E1 开场冲突 / E2 中段选择 / E3 章尾钩子 / E4 人物主动 /    │
│       E5 关系后果（来自 chapter_distance.py）                    │
│     - 不等于"读者会追"，但低于 7.0 的章节无资格进盲读池            │
├──────────────────────────────────────────────────────────────┤
│ S3  真人读者证据（reader L2：真人 sub-agent 或真人读者）          │
│     - R1-R5 同章同测，必须 source + isolation + provenance 齐备  │
│     - effective_n ≥ 3 + diversity_score ≥ 0.5 + reader L2 ≥ 1    │
└──────────────────────────────────────────────────────────────┘
```

**任何环节漏层 = 越界**。具体边界：

- S0 漏层 → 不可宣称"晋江机制上属于爆款"；
- S1 漏层 → 不可把行业共识写进机器公式当硬门槛；
- S2 漏层 → 不可用工程分替代读者分；
- S3 漏层 → 不可在任何文档、PR、群消息里写"读者会追 / 上瘾"。

> 工程层（chapter_distance.py）用 L1/L2 标记"工程维度 / 真人维度"。
> 本文档用 S0/S1/S2/S3 标记"四层证据栈"。两套命名不混用，看到 S2 = 工程层、看到 L2 = 真人读者层。

## 2. 各层之间的硬规则

### 2.1 S0 → S1 → S2：每条工程 rubric 必须可指回证据层

| 维度 | 当前落点 | 证据层 | 备注 |
|---|---|---|---|
| E1 开场冲突 | `tools/jinjiang_chapter_distance.py` `e_score.E1` | S2 工程启发式 | 行业中"钩子前置"是 S1 共识；E1 把"动作动词 ≥ 2 + 阻力词"作为机器代理 |
| E2 中段选择 | `e_score.E2` | S2 工程启发式 | "信息密度 / 选择改变局面"是 S1 共识；用"决定 / 改为 / 主动"等词代理 |
| E3 章尾钩子 | `e_score.E3` | S2 + reader L2 | "情感碾压 + 钩兑现"是 S1 共识；机器靠 `hook_signal` 启发式 |
| E4 人物主动 | `e_score.E4` | S2 工程启发式 | "反降智"是 S1 共识；机器数 agency 词 |
| E5 关系后果 | `e_score.E5` | S2 工程启发式 | "关系升级"是 S1 共识；机器数 named 角色 + agency |
| R1-R5 真人 | `tools/reader_panel_runner.py` `r_score` | reader L2 | 唯一可被认作"读者证据"的层 |

任何对 E1-E5 公式的修改，必须先回答：

- 修改后是否仍指向 S1 共识？还是**降为更弱的工程启发式**？
- 是否会让 ≥ 8.5 的章节数量被人为抬高（破坏 996/1145 的诚实基线）？

### 2.2 S2 → S3：工程分进盲读池不等于进入发布候选

- 工程分 < 7.0 → **不进盲读池**（保机器底线）。
- 工程分 ≥ 7.0 但 reader L2 = 0 → **只在 `distance-summary.md` 标"publish-eligible 候选"**，**不**在 `reader-blindtest-results.md` 里写"读者会追"。
- 工程分 ≥ 7.0 且 reader L2 ≥ 1 且 diversity_score ≥ 0.5 → 升级证据出现，可写"读者分 ≥ 7.0 的 N 章"。

### 2.3 S3 → 报告：报告语言受 effective_n 强约束

| effective_n 区间 | 报告允许的措辞 | 禁止的措辞 |
|---|---|---|
| 0 | "工程 5 维已修，但 reader L2 证据缺失" | "读者会追 / 爆款 / 上瘾" |
| 1-2 | "1-2 名读者倾向 X，但不构成多人共识" | "多名读者 / 多数读者 / 爆款" |
| ≥ 3 且 diversity ≥ 0.5 | "≥ 3 名独立读者同点，可作为方向" | 把方向写进结构性 rewrite 任务 |
| ≥ 3 且 diversity < 0.5 | "复读嫌疑高，仅作方向记录" | "共识 / 同点" |
| ≥ 5 且 diversity ≥ 0.6 | "5 名独立读者同点，可升级" | 把升级等同于"已爆款" |

> 这一约束焊死在 `tools/reader_panel_runner.py aggregate()` 的输出顶部与
> `tools/jinjiang_chapter_distance.py main()` 的 boundary 字段。

## 3. 改稿循环的四道门（不可越级）

```
[策划]   人类写 season_manifest.yaml / factions.yaml / plot_state.json / decisions/next.json
  ↓ 人类批准
[动笔前] lint → audit → distance 距离快照
  ↓ 锁 baseline
[改稿]   review_batch.py --strict-editorial + prose_lint.py
  ↓ 单章通过
[动笔后] distance 重跑 → reader_panel_runner check + aggregate → commit
  ↓ effective_n ≥ 3 + diversity ≥ 0.5
[升级]   edit-decision-protocol §3 触发结构 rewrite
```

任何越级（例如跳过 distance 直接 commit、跳过 reader_panel_runner 直接进发布）= 工程层硬错误，必须在 PR review 阶段 BLOCKED。

## 4. pack_hash 漂移审计（已实现）

盲读包文本一旦变化，之前所有 reader JSON 的 `pack_hash` 字段就**自动失效**。
`tools/reader_panel_runner.py` 已实现 drift 检测：

- `_load_panel()` 把每份 reader JSON 的 `pack_hash` 与当前 `_pack_hash()` 比较；不一致时记录为 stale 列表。
- `aggregate()` 启动时把 stale 文件名从 effective_n 计算中过滤掉。
- 报告顶部出现 `## pack_hash drift 警告` 块列出 stale 文件。
- `tests/test_reader_panel_runner.py::test_stale_pack_hash_is_filtered` 钉死回归。

维护义务：

- 修改 `tools/reader_blindtest_pack.py` 的 `random.Random(42)` 种子或章节范围时，必须显式告诉用户 pack_hash 变了、旧 reader 全部 stale。
- `reports/jinjiang-r20/blindtest_packs/*.md` 改一个字也算漂移。
- 漂移后 `aggregate()` 输出会显式列出 stale；不允许 silent filter。

## 5. 真人 sub-agent 启动失败的兜底

`SKILL.md` / `handoff.md` 仍写 `agent-relay delegate --backend claude-task` 这种
在当前 Windows 环境跑不通的指令。这是历史遗留，会**让真人 sub-agent 永远 reader L2 = 0**。

兜底 SOP（本项目内焊死）：

1. **优先路径**：在 fork 会话里跑 `py -3 -X utf8 tools/reader_panel_runner.py emit-prompt 1..5`，
   把 5 份 JSON 手工落盘到 `reader-N-真人-<persona>.json`。
2. **离线路径**：真人读者按 `prompts/reader/personas.json` 选一份 persona 阅读
   4 个盲读包，写一份 JSON 落 `reader-N-真人-<persona>.json`。
3. **失败识别**：上述两条路若在 ≥ 14 天内**都无新增** reader L2 文件，本季自动回到"工程单轨
   模式"，所有文档必须把"读者分"措辞降级为"工程分"。
4. **失败时报告**：每次 `aggregate()` 必须把 "## pack_hash drift 警告" 一起加进结果顶部；
   当 reader L2 = 0 + drift 不为空时，读者基线被双重削弱。

## 6. 不可越线的边界（汇总）

- lint 通过 ≠ 艺术质量通过。
- 工程 9.8 分只是机械信号接近上限，**不是市场分**。
- L1 unanimous 在 `echo_panel = True` 时**不**构成多人共识。
- **reader L2 = 0** 时禁止在 README / 报告 / 群消息里使用
  "读者会追 / 爆款 / 上瘾 / 读者确认 / 多数读者"。
- 任何对工程公式的修改必须先回答"会不会让 ≥ 8.5 章节数量被人为抬高"。
- 任何对 persona 池或盲读包范围的修改必须先把旧 pack 归档到
  `reports/jinjiang-r20/panel_<date>/`，避免读者记忆漂移。
- 真人 sub-agent / 真人读者的 isolation 双证据（`no_chronicle` + `no_frontmatter`）必须
  **机器可校验**（JSON 字符串），不是"sub-agent 自报"。

## 7. 与已有文档的索引

- 工程 5 维 + 真人 5 维 + 禁区 + 上瘾单元：`docs/standards/晋江爆款基线.md`
- Canonical 主流程：`docs/standards/novel-workflow.md` 末尾"5 读者交叉 + 真人 sub-agent 工作流"
- 盲读协议：`docs/reader-subagent-workflow.md`（11 节）
- Operator 手册：`docs/standards/jinjiang-blowup-baseline-operator.md`（§5/§8/§9 工程实现）
- 主编交接：`handoff.md` 末尾"读者盲读 + 距离工具（r20 工作流）"段
- AI 入口：`SKILL.md` 中"5 读者交叉 + 距离工具（r20 双轨基线，必跑节点）"
- 研究笔记：`reports/jinjiang-r20/research-notes.md`（S0/S1 边界）
- 基线手册：`reports/jinjiang-r20/jinjiang-rubric.md`（写作侧硬规则）
- 改稿 playbook：`reports/jinjiang-r20/blow-up-playbook.md`
- 距离快照：`reports/jinjiang-r20/distance-summary.md`（不可手写）
- 盲读结果：`reports/jinjiang-r20/reader-blindtest-results.md`（不可手写）
- 本轮磨斧头研究留底：`reports/jinjiang-r20/磨斧头研究-2026-09-05.md`（rubric 修复实测 / E5 POV 主动发起方 / E6 钩子类型枚举 / JJ-LINT-03/05/06 焊接记录）
- 7 维工程 rubric：`reports/jinjiang-r20/rubric-scoreboard.{json,md}`（与距离 E1-E5 并列,取低;rubric 修复于 2026-09-05）

## 8. 文档维护纪律

- 改 `晋江爆款基线.md` 或 `jinjiang-blowup-baseline-operator.md` → 必须同步改本文档 §2.1 表格。
- 改 `tools/jinjiang_chapter_distance.py` 公式 → 必须先看 `distance-summary.md` 重跑后
  8.5+ 章节数量是否被人为抬高；抬高就回滚。
- 改 `tools/reader_panel_runner.py` 的 `_classify` / `_pack_hash` / `diversity_score` /
  `_pack_hash_stale_entries` → 必须同步改 `tests/test_reader_panel_runner.py` 钉死回归。
- 改 persona 池或盲读包范围 → 必须先归档旧 pack 到 `panel_<date>/`，并在
  `phase1-status.md` 记录旧 effective_n → 新 effective_n 的过渡。
