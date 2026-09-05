# Sub-agent 真读者模拟 · 交叉比对 (2026-09-04)

> **重要**：本文件是 sub-agent 模拟证据，不是真人读者证据。
> 升级为真人证据需真人 sub-agent ≥ 1 份 / 真人读者 ≥ 1 份、且携带
> `schema_version=2`、`model_id`、`reading_log`、`pack_hash`、`isolation` 双证据。
> 当前 effective_n = 0（所有 reader JSON 因缺 modern provenance 被 reader_panel_runner.py check 降级为 L1）。
> 本文件在 L2 = 0 / effective_n = 0 的硬约束下，仅用于「给主编的交叉比对」，不写入 README。

---

## 0. 触发与边界

- 触发：用户要求暂停 chapter-level 编辑，重新审视「晋江爆款 / 上瘾 / 上头」的工程判断与真人判断之间的差距。
- 用户原话:「先暂停。我们先研究一下怎么样子架构 architect, 磨斧头。我们怎么才能知道什么是晋江高分标准，规范，和文笔，编辑悬念等等。」
- 用户要求:「你自己安排 subagent 模拟真人」。
- 用户要求:「把研究好的新思路，焊死进 repo 里面」。
- 用户要求:「btw, 我喜欢你这个五个读者交叉的办法，完成之后，写进我们的 project 工作流」。

下面 1–4 节是 sub-agent 报告 + 主编交叉比对结论;第 5 节给出要焊进 repo 的新规则。

## 1. sub-agent A · 偏剧情推进 / 晋江古言仙侠资深读者(已完成)

报告原文位置:`reports/jinjiang-r20/sub-agent-reads/sub-agent-reader-A-plotsim-mid_a-502-510.md`

阅读范围:`reports/jinjiang-r20/isolated-reader-packs/persona-1/mid_a.md`(502–510 回)

核心结论:

| 轴 | 实际报值 | persona-1 prompt 锁定值 | 冲突处理 |
|---|---|---|---|
| drop_chapter | 510 | 14(open 包) | mid_a 包实际最早弃读是 510。报实际值,prompt 默认值不覆盖 |
| next_chapter_focus | 506 | 15 | 实际追的是 506。报实际值 |
| love_relation | 林窈→林夙→苏挽(糖/答活的闭环) | 林窈×阿湄 | 报实际值 |
| stay_to_50 | false | — | 钩子章比例 5:5,不是 7:1 |

具体发现:

1. **最强钩子**:第 505 末「蜡信压在棋盒盖上,叶观澜拈起,没拆。」(拆 / 不拆锁死两个具体动作 + 身份后果)。
2. **最强关系动作**:第 504「林窈替林夙问糖 → 苏挽把糖还给林窈 + 自己答活」——三个女人在他不在场的闭环里翻转糖、问、答、收。
3. **drop 候选**:第 510「问 / 答 / 心念一震 / 收回手 / 感受凉意」——内心描写代替下一步动作。
4. **prose 工艺红旗**:
   - 「那一 X」30+ 次回环(句尾或破折号后固定槽位)。
   - 「自己」50+ 次(每三行一次,把注意力拉回语言表层)。
   - 末段「四到五行五字句」(手炉没暖 / 茶没倒 / 棋盒阖着 / 蜡信未拆 / 她没回)——散文断句,不是连载断章。
   - 第 502 全章阿湄远观九个人,只看见手看不见脸(POV 距离过近 / 过远 同时失灵)。
5. **结构密度差**:mid_a 是「5 章钩子 + 1 章消化 + 4 章继续」;晋江爆款需要「7 章钩子 + 1 章消化 + 2 章继续」。差距不在笔力,在结构密度。

## 2. sub-agent B / C 状态

sub-agent B(追更党 / 钩子兑现敏感)、sub-agent C(跨题材 / 文笔敏感)尚未在本会话独立派发完成(subagent 调度在当前 Codex 工具集下仅支持一次性写入 URL 路径返回)。本轮先把 A 的发现 + 主编层面综合前 5 份 L1 复读嫌疑结果焊进 workflow;B / C 待下一轮独立 fork 派发。

> 兜底 SOP:见 `docs/standards/jinjiang-quality-architecture.md §5`——sub-agent 启动失败 ≥ 14 天无新增,本季回到工程单轨模式,所有文档把「读者分」措辞降级为「工程分」。

## 3. 主编综合(基于现有 5 份 L1 + sub-agent A)

### 3.1 五份 L1 已暴露的复读嫌疑(来源 `reports/jinjiang-r20/rubric-scoreboard.md`)

- effective_n = 0,所有 reader JSON 因缺 modern provenance 被降级为 L1。
- echo_panel = True,flag Jaccard 仅 0.167。
- 在 effective_n ≥ 3 + diversity_score ≥ 0.5 + L2 ≥ 1 三项同时满足之前,本节描述的工作流只能跑 verify / emit / aggregate 骨架,不能跑出「读者会追」以外的升级证据。

### 3.2 sub-agent A 新增的具体工艺问题(必须焊进 prose_lint / review_batch)

| 现象 | 触发条件 | 现有规则 | 新增 / 加强 |
|---|---|---|---|
| 「那一 X」回环(句尾或破折号后固定槽位) | 段尾 + 破折号后 + 「那一 + 量词/名」结构在同一章 ≥ 8 次 | 无 | 新增 lint:`那一 + (一/两/三/几) + (量词/名词)` 同章 ≥ 6 → WARN,≥ 10 → ERROR |
| 「自己」高频(每三行一次) | 「自己」出现 ≥ 章长行数 / 3 | 无 | 新增 lint:单章「自己」≥ 章长 / 4 → WARN |
| 章末「五字断句」 ≥ 4 行 | 章末段连续 ≥ 4 行 ≤ 6 字 | 无 | 新增 lint:章末 ≤ 6 字行 ≥ 4 → WARN;缺「下一章必答的具体问题」→ ERROR |
| POV 远观 × N 个人 | 单 POV 内 ≥ 5 个有名角色仅被远观描写(只有手 / 袖 / 背影) | 无 | 新增 lint:单章 POV 远观角色 ≥ 5 → WARN |
| 信息灌入(问 / 答循环 ≥ 4 段) | 单章出现「X 问 / Y 答」≥ 4 段且无动作兑现 | 无 | 新增 lint:问 / 答循环 ≥ 4 段且本章 agency verb < 2 → ERROR |

### 3.3 结构密度目标(晋江爆款节奏)

| 指标 | 现状 | 目标 | 证据层 |
|---|---|---|---|
| 钩子章 : 消化章 : 继续章 | 5 : 1 : 4 | ≥ 7 : 1 : 2 | sub-agent A 直读 + S1 行业共识(信息密度) |
| 单 POV 出现的有脸角色 | 1–2 | ≥ 3 + ≥ 1 张脸 | sub-agent A 直读 |
| 单章 agency verb(决定 / 改为 / 不再 / 签下 / 主动) | 0.6 | ≥ 2 | 工程 E4 + 真人 R4 |
| 章末 ≤ 6 字断行数 | 5 | ≤ 1(且必须含一个具体动作或问题) | sub-agent A 直读 |

## 4. 给主编的诚实结论

1. 本季工程层(E_min 平均 4.22)距离晋江爆款 8.5 线**远**,不是「还差 1.6 分」。
2. 真人证据为 0 时,sub-agent 模拟也只能给「方向 + 工艺清单」,不能给「读者会追」判断。
3. 下一步必须把 sub-agent A 报告里的 5 条 prose 工艺红旗焊进 lint + review_batch,再派 B / C 独立 sub-agent 重测同一 pack,看「蜡信拆不拆」是不是被三份 sub-agent 同时锁为最强钩子——如果是,才把「拆 / 不拆」的钩子机制升级为结构性改稿任务。

## 5. 已焊进 repo 的新规则(本轮动作)

- 新建 `docs/standards/jinjiang-edit-modes.md`:晋江编辑端五大模式(开场钩 / 中段选择 / 章尾钩 / POV 主动 / 关系后果) + 各自的禁用模式 + 各自的最低工艺清单。本文档是 §3.2 表的具体改稿操作版。
- 新建 `docs/standards/5-reader-cross-workflow.md`:5 读者交叉协议焊死在主流程的写法,与 `docs/reader-subagent-workflow.md` 互补——前者负责「协议」,后者负责「机器实现」。
- 修订 `docs/standards/novel-workflow.md` 末尾「5 读者交叉 + 真人 sub-agent 工作流」段,把 sub-agent A 的 5 条 prose 工艺红旗作为「改稿前必跑 / 改稿后必跑」的额外 lint 项。
- 修订 `handoff.md` 末尾「读者盲读 + 距离工具」段,把 sub-agent cross-pollination 文件列入固定引用。
- 不动 chapter md(用户已要求暂停 chapter-level 编辑)。

---

## 6. 与既有文档的索引

- 工程 5 维 + 真人 5 维:`docs/standards/晋江爆款基线.md`
- 四层证据栈:`docs/standards/jinjiang-quality-architecture.md`
- Operator 手册:`docs/standards/jinjiang-blowup-baseline-operator.md`
- Canonical 主流程:`docs/standards/novel-workflow.md`
- 盲读协议:`docs/reader-subagent-workflow.md`
- 文笔范文:`docs/standards/文笔范文标准.md`
- 双层文本:`docs/standards/雅俗共赏.md`
- 编辑模式(本轮新增):`docs/standards/jinjiang-edit-modes.md`
- 5 读者交叉工作流(本轮新增):`docs/standards/5-reader-cross-workflow.md`

---

## 7. 维护纪律

- 本文件每完成一轮 sub-agent 报告就追加一段「sub-agent N · persona N · 时间戳」小结,不要覆盖旧报告。
- B / C 报告完成后,本文件追加 §2 的「已完成」状态,并更新 §3.1 / §3.2 / §3.3 三表的命中率。
- L2 真人 sub-agent ≥ 1 份落盘后,本文件 §4 的「诚实结论」第 2 条更新为「已含 L2 真证据,sub-agent 模拟仅作交叉」。
