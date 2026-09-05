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
