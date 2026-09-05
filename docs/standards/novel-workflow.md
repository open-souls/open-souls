# Open Souls 小说工作流规范

这份文档是小说写作流程的项目级约束。`.claude/skills/novel-writer/SKILL.md`
负责把它交给 AI 执行；本文件负责让人和其他工具能直接审阅同一份规则。

## 先解决什么问题

第一季不是“世界观不够多”，而是没有把世界观变成可推进、可验收的状态：

- 读者入口把男频复仇升级、群像和情感线同时当成第一承诺，导致故事错位；
- 人物卡有描述，却没有每一方当前目标、资源、红线、行动和知识差；
- 情节由模型自行挑“最强方案”，人类没有真正拥有主线选择；
- 章节可以声称连续性、能动性和质量，却没有留下“压力 → 选择 → 代价 → 状态变化 → 下一压力”的因果证据；
- 旧稿存在重复编号、短章和占位钩子，不能把它们当作已验证的 canonical history。

因此，写作流程先做产品选择，再做剧情选择，最后才做 prose：

```text
读者承诺/奖励比例
        ↓ 人类批准
阵营与人物的当前状态
        ↓ AI 提案 2–4 个可取舍方案
本回的压力—选择—代价—状态变化
        ↓ 独立验证
canonical chapter + plot_state 更新
```

## 读者承诺侧 · 5 读者交叉协议(2026-09-04 焊入)

> 用户原话(2026-09-04):「btw, 我喜欢你这个五个读者交叉的办法,完成之后,写进我们的 project 工作流」。
> 本节就是把上一会话已焊死的 docs/standards/5-reader-cross-workflow.md 作为读者承诺侧硬约束焊进本主流程。
> 完整规则与 persona 表 / 独立性硬门 / 语言门禁 见 5-reader-cross-workflow.md。

### 主流程读者侧三问

1. **谁判断?**:5 份 L1(模型代理)+ ≥ 1 份 L2(真人读者 / 真人 sub-agent)。L1 unanimous 在 echo_panel=True 时不构成共识。
2. **怎么升级?**:读者结论升级为「方向」必须 effective_n ≥ 3 + diversity_score ≥ 0.5 + L2 ≥ 1 同时满足;升级为「结构性改稿任务」再叠加同点 ≥ 3 + ≥ 1 份 L2 真证据。任一不满足只能作为单点观察,不写进 edit-decision-protocol.md §3 改稿顺序。
3. **何时跑?**:动笔前 / 动笔后 / 跨章 ≥ 30 章累计改稿后,具体步骤见 5-reader-cross-workflow.md §2 与 §6。

### 真人证据空窗期(本季硬约束)

- effective_n = 0:所有「真人」文件名文件因缺 modern provenance 被 reader_panel_runner.py check 降级为 L1。
- 文档 / README / commit message / 群聊 全部禁止「读者会追」「爆款」「上瘾」「上头」「读者确认」等措辞(完整词表见 磨斧头研究-2026-09-04.md §13)。
- 工程分不等于市场分;真人证据空窗期一切「读者分」措辞一律降级为「工程分」。

### sub-agent 模拟的边界(2026-09-04 焊入)

本季真人 sub-agent / 真人读者启动失败(≥ 14 天无新增 L2 JSON),自动进入 sub-agent 模拟兜底路径。sub-agent 模拟分两类:

- **读者端 sub-agent 模拟**:落 reports/jinjiang-r20/sub-agent-reads/*.md,**不升级 L2**,仅作方向 + 工艺清单。
- **研究端 sub-agent 审查**:代码 / 文档 / 工程审查,落 磨斧头研究-<date>.md 留底,**不计入 effective_n**。

派发协议见 磨斧头研究-2026-09-04.md §14。

### 与「权威状态文件」段的接驳

- 读者侧判断不进入 season_manifest.yaml(那是产品定位层)。
- 读者侧判断进入 reports/jinjiang-r20/reader-blindtest-results.md(那是读者证据层)。
- 改稿顺序进入 reports/jinjiang-r20/edit-decision-protocol.md §3(那是工程改稿层)。

## 权威状态文件

每个新 season 必须拥有：

- `season_manifest.yaml`：主读者、入口承诺、核心问题、奖励比例、禁区和规则；
- `factions.yaml`：阵营的公开目标、隐藏目标、资源、红线、当前行动和立场；
- `plot_state.json`：开放线索、人物目标、知识差、阵营行动、状态更新、当前压力和最近一次因果转移；
- `decisions/next.json`：AI 提出的 A/B/C（或更多）选项；
- `decisions/approved.json`：绑定当前 `last_accepted_chapter`、只消费下一章的人类批准方向。

新季必须设置 `human_decision_required: true` 和 `legacy_mode: false`。没有批准项，
`engine/village.py` 必须在任何 LLM 调用和状态写入之前停止。
严格季至少需要两个真正不同的选项；每个选项要写清 `winner`、`loser`、`cost` 和 `next_pressure`，否则只是换皮的同一条剧情，不算人类选择题。

第一季的 `legacy_mode: true` 是审计标记，不是质量背书。旧稿应报告问题、提供素材，
不能为了让检查变绿而批量补写假因果。

## 人和 AI 的边界

人类拥有主读者、入口承诺、奖励比例、canonical 方向、不可逆代价和最终发布决定。

AI 可以读取有界状态、提出有真实取舍的方案、执行已批准方案并提交证据。AI 不得：

- 从候选方案中自行挑选并当成人类意图；
- 用 `continuity_ok: true`、`agency_ok: true` 或分数替代证据；
- 未经批准改写阵营立场、知识差、人物目标或 canonical 历史；
- 把完整 chronicle 无界地塞进 prompt。

## 章节最低契约

严格季的 canonical chapter 必须满足 manifest 中的最小正文长度，并包含：

```yaml
canonical: true
decision_id: B
hook_evidence: "正文中逐字出现的可核查短语"
causal:
  pressure: "本回无法回避的外部压力"
  choice: "人物做出的不可替代选择"
  cost: "选择立即支付的代价"
  state_change: "人物、关系或阵营发生的可观察变化"
  next_pressure: "下一回必须面对的压力"
state_updates:
  - entity: "人物、关系或制度"
    change: "正文中能核对的变化"
    evidence: "正文中逐字出现的短引文"
faction_moves:
  - faction: "faction id"
    move: "本回实际行动"
    consequence: "产生的后果"
    stance_change: "本回立场如何改变，或为何被迫维持"
    evidence: "正文中逐字出现的短引文"
```

`hook_evidence` 必须原样出现在正文中，`state_updates` 和 `faction_moves` 不能是空列表；每条更新都必须带有完整字段和正文中的 `evidence` 短引文，`faction_moves` 的 faction id 必须存在于 `factions.yaml`。`decision_id` 必须等于本次人类批准的 id；一次批准只允许推进一个下一章，写入后必须重新批准。程序只在章节
写入成功且契约通过后，才更新 `plot_state.json`、关系、记忆和 arc；下游写入失败会回滚本次提交，不能留下半套状态。

## 验收顺序

1. 安全、正文和 frontmatter 类型检查；
2. canonical 编号唯一性和重复文件审计；
3. hook 的正文证据；
4. causal 五项、state/faction 更新和已批准 `decision_id`；
5. 独立 verifier 读取正文、状态和 diff；
6. 人类决定发布、重写、废弃或结束本季。

可重复运行：

```powershell
python engine/story_state.py status --season seasons/02-example
python engine/validate_story.py --season seasons/02-example
VILLAGE_MOCK=1 python engine/village.py --ticks 1
```

`engine/run_dispatch.py`, `engine/batch_rewrite.py`, and the legacy batch-polish
path are only for `legacy_mode` repair. A strict season must enter through
`engine/village.py`; the legacy paths do not atomically consume a human decision
or advance `plot_state`.

mock 只证明门禁和状态写入顺序，不证明文学质量。真正的章节仍需要独立文笔、连续性、
人物能动性和安全审稿。


## 附 · 5 读者交叉 + 真人 sub-agent 工作流（必跑节点）

> 项目级四层证据栈（S0 晋江官方 / S1 行业共识 / S2 工程启发式 / S3 真人读者）的完整定义见
> docs/standards/jinjiang-quality-architecture.md；本节是它在 canonical 主流程的复述与硬约束落地。

这一节不是附录，是 canonical 工作流的固定节点。任何改稿循环在动笔前、动笔后都要按
下面序列跑完，缺一不可。背景解释放在 `docs/reader-subagent-workflow.md`，工程实现细节
放在 `docs/standards/jinjiang-blowup-baseline-operator.md` §5/§8/§9，
这里只负责把"必跑"焊死在主流程。

### 为什么是 5 份 L1 + ≥1 份 L2，不是一份 L1 自己读

- 模型代理不等于真人读者。一份 L1 没有任何"多名读者共同"的意义。
- 5 份 L1 的价值不在于"平均意见"，在于交叉协议：每份 persona 必须挂不同的
  keep_if / drop_if / must_disagree_with，必须被分配到不同的 drop_chapter、
  love_relation、next_chapter_focus，否则就是复读嫌疑。
- L2 真人 sub-agent / 真人读者至少 1 份是升级判定的硬门槛。L2 = 0 时任何"读者会追 /
  爆款 / 上瘾"判断一律禁止，这是工程层硬约束，不是软建议。

### 改稿前必跑（动笔前）

1. 锁距离快照
   `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
   `reports/jinjiang-r20/distance-summary.md` 是本工作树距离晋江爆款的诚实答案。
2. 锁 5 份 L1 交叉协议
   `py -3 -X utf8 tools/reader_subagent_driver.py verify`
   任一轴（drop_chapter / love_relation / next_chapter_focus）退化就视为复读嫌疑，
   echo_panel 翻 True。verify 只校验"形式上的差异化"，真正的差异化来自下一节 emit。
3. 生成 5 份 persona prompt + 1 份 L2 真人 sub-agent prompt
   `py -3 -X utf8 tools/reader_subagent_driver.py emit`
   每份 prompt 内嵌唯一的 isolation.persona_seed、独立的 rotation，
   落到 `reports/jinjiang-r20/reader-prompt-{1..5}.txt` 与 `reports/jinjiang-r20/reader-prompt-real.txt`。
4. 跑盲读聚合 baseline
   `py -3 -X utf8 tools/reader_panel_runner.py check`
   `py -3 -X utf8 tools/reader_panel_runner.py aggregate`
   把 baseline 的 effective_n / diversity_score / echo_panel 写入
   `reports/jinjiang-r20/reader-blindtest-results.md` 的"轮次对比"段。

### 改稿后必跑（动笔后）

1. 重跑距离快照，对比 bottom-list 与 gate 计数。
2. 复跑 verify + emit（同 pack_hash 下不需要 --new-seed；如果刷新了盲读包，必须 --new-seed 并把
   旧 `reports/jinjiang-r20/blindtest_packs/*.md` 归档到 `reports/jinjiang-r20/panel_<date>/`）。
3. 复跑 check + aggregate，把 effective_n / diversity_score / 升级项 diff 写入
   `reports/jinjiang-r20/reader-blindtest-results.md` 的"轮次对比"段。
4. `tools/reader_panel_runner.py check` 会自动把缺 modern provenance 的"真人"文件名文件降级
   为 L1 并打印原因。真人 sub-agent 回填的 JSON 必须带齐 schema_version=2 / model_id /
   reading_log / pack_hash / isolation 双证据，缺一项就当 L1。

### 真人 sub-agent / 真人读者的安排

- 真人 sub-agent 通过 `agent-relay delegate --backend claude-task --task <prompt-file>`
  跑独立 fork 会话，独立 cwd 启动，JSON 里 self-attest isolation.no_chronicle = true、
  isolation.no_frontmatter = true，source 字段以"真人 sub-agent"开头。
- 当真人 sub-agent 大于等于 3 份时，结构任务升级规则切换为"真人 sub-agent 不少于 3 人同点，才升级"。
- 大于等于 1 份真人读者 + 大于等于 2 份真人 sub-agent 才视为 L2 完整。
- L2 真实样本 = 0 时禁止使用"读者确认 / 读者会追 / 上瘾 / 爆款"判断。

### 与改稿循环的硬耦合（不可省略）

- 改稿前没跑盲读 → 不准下笔。
- 改稿后没跑盲读复测 → 不准 commit。
- 一次大于等于 3 章改稿后必须跑一次 aggregate，把 effective_n / diversity_score / 升级项 diff
  写入"轮次对比"段。
- 跨章节大于等于 30 章累计改稿后，必须把 persona 池与盲读包范围（开篇/中段 A/中段 B/最新）
  一起刷新，旧 pack 归档到 `reports/jinjiang-r20/panel_<date>/`。

### 当前会话的现实（截至 2026-09-04）

- effective_n = 0：所有"真人"文件名文件因缺少 modern provenance 被降级为 L1。
- echo_panel = True：5 份 L1 flag Jaccard 仅 0.167，复读嫌疑高。
- 在 effective_n 大于等于 3 + diversity_score 大于等于 0.5 + L2 大于等于 1 三项同时满足之前，
  本节描述的工作流只能跑 verify / emit / aggregate 骨架，不能跑出"读者会追"以外的升级证据。

---

## 附 · 改稿工艺 5 条硬规则（sub-agent 模拟 + 真人盲读共同支持，2026-09-04 焊入）

> 这一节是上一节的**同伴节点**：盲读协议只负责「谁来判断 / 怎么判断」，
> 工艺规则只负责「判断出失败时，改稿具体怎么改」。
>
> 来源：`reports/jinjiang-r20/sub-agent-cross-pollination-2026-09-04.md §3.2`
> 操作表：`docs/standards/jinjiang-edit-modes.md §8`
>
> 这一节是工艺清单层，下一节是「哪一章必须改」的选择层。

### 5 条硬规则

1. **「那一 X」回环禁单章 ≥ 6 次**
   - 触发：单章出现「那一 + (一/两/三/几) + (量词/名词)」≥ 6 次（≥ 10 视为 ERROR）。
   - 出处：sub-agent A 直接红旗，mid_a 502–510 出现 30+ 次。
   - 改稿：删整句；不换同义词。

2. **「自己」高频禁单章 ≥ 章长 / 4**
   - 触发：单章「自己」出现次数 ≥ 章长行数 / 4。
   - 出处：sub-agent A 直接红旗，mid_a 包出现 50+ 次。
   - 改稿：把「自己」换成动作主语；不删动作。

3. **章末「五字断句」 ≥ 4 行**
   - 触发：章末段连续 ≥ 4 行 ≤ 6 字。
   - 出处：sub-agent A 直接红旗，mid_a 多个章末「手炉没暖 / 茶没倒 / 棋盒阖着 / 蜡信未拆 / 她没回」是散文断句。
   - 改稿：合并或补具体动作 / 问题；不要把 5 字断句当连载断章。

4. **POV 远观角色 ≥ 5 仅看见手 / 袖**
   - 触发：单章 POV 远观有名角色 ≥ 5，但仅描写手 / 袖 / 背影（POV 距离过远）。
   - 出处：sub-agent A 直接红旗，mid_a 第 502 全章阿湄远观九人只看见手。
   - 改稿：拆 POV；让 POV 进入单人近景；不要远观一群。

5. **问 / 答循环 ≥ 4 段 + agency verb < 2**
   - 触发：单章出现「X 问 / Y 答」结构 ≥ 4 段，且本章 agency verb < 2。
   - 出处：sub-agent A 直接红旗，mid_a 第 510 二十九年前旧账问答占前 80 行。
   - 改稿：在循环里插 ≥ 1 个动作兑现；agency verb 加到 ≥ 2；不要 paraphrase 旧问答。

### 与改稿循环的硬耦合（不可省略）

- 任一条触发 ERROR → 该章必须结构性重写，不准 commit。
- 任一条触发 WARN → 该章必须重写一段才准 commit，不准 silent filter。
- 5 条规则写入 `engine/prose_lint.py` + `tools/review_batch.py --strict-editorial` 是工程硬门，不在 README 里写「读者建议」。
- 5 条规则与 `tools/jinjiang_chapter_distance.py` 的 E1–E5 互为校验：lint ERROR 的章，E 维必有一条 < 7；E 维 < 7 的章，lint 必报至少一条 WARN。

### 与「5 读者交叉 + 真人 sub-agent 工作流」的关系

- 工艺 5 条 = **改稿操作层**（哪条失败就改哪条）。
- 5 读者交叉 = **判断层**（同一章 / 同一关系 / 同一钩子被多读者锁定，才升级为结构性改稿任务）。
- 编辑模式 5 维（M1–M5）= **诊断层**（每章在哪一维失败，由它点名）。
- 三层必须同时跑：先 `5-reader-cross-workflow.md` 锁定读者判断 → 再 `jinjiang-edit-modes.md` 锁定失败维 → 再读本节工艺 5 条锁定改稿动作。任一层跳过 = 改稿循环不闭环。

---
---

## 附 · 磨斧头阶段焊死段（2026-09-04，本会话）

> 触发：用户原话「先暂停。我们先研究一下怎么样子架构 architect, 磨斧头。
> 我们怎么才能知道什么是晋江高分标准，规范，和文笔，编辑悬念等等。
> 把研究好的新思路，焊死进 repo 里面，然后我们再继续。」

> 研究报告落盘：`reports/jinjiang-r20/磨斧头研究-2026-09-04.md`
> 上游 sub-agent 报告：
>   - sub-agent A（晋江文笔与悬念工艺员）= 已落 `reports/jinjiang-r20/sub-agent-reads/sub-agent-reader-A-plotsim-mid_a-502-510.md`
>   - sub-agent Raman（晋江编辑标准研究员）= 已落 研究总结第 1 / 6 节
>   - sub-agent B / C = 待后续会话派发

> 这一节是「改稿工艺 5 条」的**升级版研究总结**，不重复上一节已焊规则。
> 只补「上一节之后又发现的事」与「下一批必须跑的施工清单」。

### 三层证据栈自检（截至 2026-09-04 实地核数）

| 层 | 已焊 | 缺口 | 下批施工 |
|---|---|---|---|
| S0 晋江官方事实 | `research-notes.md` 第 1 节 手写笔记 | 缺机器可校验版本 | 落 `reports/jinjiang-r20/jinjiang-official-facts.md` |
| S1 行业共识 | `晋江爆款基线.md` 第 1-5 节 + `文笔范文标准.md` | 缺 E6 钩类型 + POV 主动发起方 + 节奏周期 + 上瘾单元 | 加 E6 / info_gap_count / bucket_beat_score / addictive_units |
| S2 工程启发式 | E1-E5 + 6 道 lint | 缺工艺 5 条实现 + 禁区 9 | 把 JJ-LINT-01-07 焊进 `engine/prose_lint.py` + `review_batch.py` |
| S3 真人读者 | `reader_panel_runner.py` + `5-reader-cross-workflow.md` | L2 = 0 / effective_n = 0 | 派 B / C 真人 sub-agent；>= 14 天仍 0 启动工程单轨模式 |

### M1-M5 vs E1-E5 vs R1-R5 一致性矩阵（2026-09-04 实地核）

- M1 = E1：1:1 已焊。
- M2 = E2：1:1 已焊。
- M3 = E3：1:1 已焊 + 缺 E6 钩子类型枚举 + 连续 <= 2 章硬门。
- M4 = E4：1:1 已焊。
- M5 = E5：1:1 已焊 + 缺 POV 主动发起方识别。
- R1-R5：与 M1-M5 对位，已落 `reader_panel_runner.py`，缺 sub-agent B / C 真人证据。

### 工艺 5 条 -> 升级版 lint 草表（JJ-LINT-01-07）

来自 sub-agent A 直读 + 本会话核数（992 / 1097 / 1086 / 1076 / 1074 / 1131）。

| 规则 | 触发 | 等级 | 现 lint 状态 | 抽样命中 |
|---|---|---|---|---|
| JJ-LINT-01 那一 X | len(re.findall(r"那一[一-鿿]{1,3}", body)) >= 6 | WARN, >= 10 ERROR | MOTIF_SLOT 阈 30 偏高 | 1076 = 18 (ERROR 阈) |
| JJ-LINT-02 自己 | body.count("自己") >= 行数 / 4 | WARN, >= 1/2 ERROR | SELF_CLAIM 只匹配"我/他/她自己" | 6 章全部 < 阈（实测 0-4） |
| JJ-LINT-03 末段短句密度 | 末 6 行 >= 4 行 <= 6 字且无具体动作 | WARN | 无 | 1097 = 4/6 (WARN) |
| JJ-LINT-04 POV 远观 | 同章 >= 5 个有名角色 >= 80% 描写仅手 / 袖 / 背影 | WARN | 无 | 6 章 = 0 |
| JJ-LINT-05 问答空转 | len(re.findall(r"「", body)) >= 8 且 agency < 2 | ERROR | 无 | 6 章 = 0 |
| JJ-LINT-06 末段气氛句 | 末 3 行内任意一行匹配 (屋里|夜|风|雪|火|雨|街上).*(很静|没?停|没?熄|没?响) | WARN | 无 | 1074 = 「灶里的火没有熄。」命中 |
| JJ-LINT-07 单字断章 | 末行匹配 ^[一-鿿]{1,2}[。！？…」』]$ | ERROR | 无 | 1097 = 「等一根。」边界 (5 字) |

### 必须焊进 repo 的硬规则（下一批 batch 13 起执行）

1. **E6 钩子类型枚举 + 连续 <= 2 章硬门** 落到 `tools/jinjiang_chapter_distance.py`
   与 `docs/standards/jinjiang-edit-modes.md` 第 4.3 节。类型枚举见
   `docs/standards/文笔范文标准.md` 第 三.3 节（炸钩 / 反转钩 / 抉择钩 / 未竟钩 /
   细思极恐钩 / 关系钩 / 泛化情绪 / 不可判）。
2. **POV 主动发起方识别** 落到 `tools/jinjiang_chapter_distance.py` E5 子项
   `e5_pov_initiator`：POV 角色本句是否动作主语占 >= 50% 中段选择动词。不达标则 E5 降一档（4 分）。
3. **禁区 9 女主被动** 落到 `engine/prose_lint.py` WARN + `晋江爆款基线.md` 第 3 节：
   单章 POV 是女主时，被动语态 / 被替 / 被让位累计 >= 3 次 -> WARN。
4. **JJ-LINT-01-05** 落到 `engine/prose_lint.py` + `tools/review_batch.py --strict-editorial` + 钉死回归测试。
5. **JJ-LINT-06-07** 落到 `engine/prose_lint.py`（与 M3 禁用直接冲突的补充）。
6. **info_gap_count / bucket_beat_score / addictive_units** 三个字段加进
   `tools/chapter_by_chapter_audit.py` 输出，并在 `distance-summary.md` 第 6 节之后
   新增一段「节奏 / 信息差 / 上瘾单元」。
7. **本季定位 虐心 7:3** 从 `文笔范文标准.md` 第 三.4 节 移到 season_manifest.yaml，
   并在 `research-notes.md` 第 2 节 注明这是项目级定位而非晋江标准。
8. **book_launched: true** 加进 season_manifest.yaml，锁定本季已过开书期。

### 工程 / 真人 / sub-agent 模拟 三层证据链（与主流程硬耦合）

- 任一 chapter 改稿前必跑：`tools/jinjiang_chapter_distance.py <file>` +
  `tools/review_batch.py --strict-editorial --file <file>` + `engine/prose_lint.py <file>`
  （任一 ERROR 都不准下笔）。
- 任一 chapter 改稿后必跑：同上 + `tools/refresh_distance_summary.py` +
  `tools/reader_panel_runner.py check` + `tools/reader_panel_runner.py aggregate`
  （任一 stale 都不准 commit）。
- 5 读者交叉协议任一轴退化 = 复读嫌疑 = 改稿循环中断，先修 `reader_subagent_driver.py`。
- L2 = 0 + drift 非空 = 读者基线双重削弱 = 所有文档「读者分」降级「工程分」。

### 不允许的省略（焊进本节是为了防反复踩坑）

- 工程 7.0 != 爆款。
- 工程 9.8 只是机械信号接近上限，不是市场分。
- L1 unanimous 在 echo_panel = True 时**不**构成多人共识。
- 真人 sub-agent / 真人读者的 isolation 双证据必须机器可校验，不是 sub-agent 自报。
- 不能把 sub-agent 模拟的内部数字（不是它报的章号 / 关系 / 钩子）当成事实。
- pack_hash = f64e35b7cac0c896 是当前基线；动 `reader_blindtest_pack.py` 必须显式告诉用户漂移。

### 维护纪律

- 改本节任一条 -> 必须同步改 `handoff.md` 末尾「磨斧头检查表」段，
  避免两份文档漂移。
- 改 JJ-LINT 任意一条 -> 必须先在 `reports/jinjiang-r20/磨斧头研究-2026-09-04.md` 第 4.2 节
  登记，再写 lint，最后才修改章节。
- 派 B / C sub-agent -> 必须先在 `reports/jinjiang-r20/sub-agent-cross-pollination-2026-09-04.md` 第 2 节
  追加「已完成」状态。
- L2 真人 sub-agent >= 1 份落盘 -> 必须更新本节「S3 真人读者」行 + 第 4.2 节 命中率 + 第 10 节 第 2 条。
