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
