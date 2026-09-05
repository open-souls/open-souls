# 5 读者交叉工作流(焊死在主流程)

> 目的:把「5 读者交叉 + 真人 sub-agent」从临时协议固化为**项目级硬约束**。
> 任何改稿循环在动笔前、动笔后都必须按本文件 §3 / §4 跑完,缺一不可。
>
> 上游协议:`docs/reader-subagent-workflow.md`(盲读协议)
> 工程实现:`tools/reader_panel_runner.py` + `tools/reader_subagent_driver.py`
> 跨比对档案:`reports/jinjiang-r20/sub-agent-cross-pollination-2026-09-04.md`
> 上层架构:`docs/standards/jinjiang-quality-architecture.md`
> 主流程:`docs/standards/novel-workflow.md`(canonical)
> 工程 5 维 + 真人 5 维:`docs/standards/晋江爆款基线.md`
> 编辑模式:`docs/standards/jinjiang-edit-modes.md`(本轮新增)

---

## 0. 三句话

1. 5 读者不是 5 份同模板复读。每份 persona 必须挂**不同的 keep_if / drop_if / must_disagree_with**,分配到不同的 drop_chapter / love_relation / next_chapter_focus,否则就是复读嫌疑(echo_panel=True)。
2. L1 模型代理 ≠ 真人读者。真人 sub-agent / 真人读者必须 ≥ 1 份才算 L2;L2 = 0 时禁止任何「读者会追 / 爆款 / 上瘾 / 读者确认 / 多数读者」措辞。
3. 5 读者交叉的最大价值不在「5 个判断」,在「5 个判断中**重复出现的具体章号 / 具体物 / 具体动作**」——这是升级为结构性改稿任务的硬证据。

## 1. 5 persona 池(焊死的差异化)

| id | label | keep_if | drop_if | must_disagree_with |
|---|---|---|---|---|
| 1 | 晋江古言仙侠资深读者 | 角色做选择且付代价 | 中段三章以上无身份后果兑现 | 不要用金手指或作者文笔代替具体阅读证据 |
| 2 | 晋江追更党,敏感钩子 | 每章有下一章必答的具体问题 | 章末落成泛化情绪或明日再看 | 不要把有悬念等同于有钩子,必须指出下章要回答什么 |
| 3 | 晋江现言读者跨题材测试 | 不靠术语也能看懂本章六成核心冲突 | 首段铺人物关系而非冲突,或连续换 POV | 不要把看懂古言名词当作独立可读 |
| 4 | 晋江女强权谋线读者 | 女主或 POV 主动决定并承担身份后果 | 主角静观、不替、不决定 | 不要用男主是否强大替代女主的行动证据 |
| 5 | 晋江新读者 | 出现一次让人心里疼过的关系动作 | 三章以上没有新建立的关系升压 | 不要用「文笔好」作为留下理由,必须说清人物动作 |

**焊死的差异化轴**:
- drop_chapter:每份 persona 必须锁一个不同的章号(默认由 `tools/reader_subagent_driver.py emit` 决定)。
- love_relation:每份 persona 必须锁一个不同的关系(默认由 emit 决定)。
- next_chapter_focus:每份 persona 必须锁一个不同的章号(默认由 emit 决定)。
- isolation.persona_seed:每份 L1 JSON 必须填不同的种子字符串。

**机器可校验**:任一轴在 5 份 L1 之间重复,`tools/reader_subagent_driver.py verify` 报复读嫌疑,effective_n 自动降级。

## 2. 5 读者交叉协议(从 emit 到 aggregate)

```
[动笔前]
  step 1: 锁距离快照
    py -3 -X utf8 tools\jinjiang_chapter_distance.py --out reports\jinjiang-r20\chapter-distance.json
    reports\jinjiang-r20\distance-summary.md 是「当前距离晋江爆款的诚实答案」。

  step 2: 锁 5 份 L1 交叉协议
    py -3 -X utf8 tools\reader_subagent_driver.py verify
    任一轴(drop_chapter / love_relation / next_chapter_focus) 退化 = 复读嫌疑,echo_panel=True。

  step 3: 生成 5 份 persona prompt + 1 份 L2 真人 sub-agent prompt
    py -3 -X utf8 tools\reader_subagent_driver.py emit
    每份 prompt 内嵌唯一的 isolation.persona_seed + 独立的 rotation。
    落到 reports\jinjiang-r20\reader-prompt-{1..5}.txt + reader-prompt-real.txt。

  step 4: 跑盲读聚合 baseline
    py -3 -X utf8 tools\reader_panel_runner.py check
    py -3 -X utf8 tools\reader_panel_runner.py aggregate
    把 baseline 的 effective_n / diversity_score / echo_panel 写入
    reports\jinjiang-r20\reader-blindtest-results.md 的「轮次对比」段。

[改稿中]
  step 5: 改稿前先看「最低维」是哪一条
    tools\jinjiang_chapter_distance.py 输出已经点名每章失败的 E 维。
    docs\standards\jinjiang-edit-modes.md §8 是改稿操作表。
    只改失败的维,不 reflow 其他维。

[动笔后]
  step 6: 重跑距离快照,对比 bottom-list 与 gate 计数。
  step 7: 复跑 verify + emit(同 pack_hash 下不需要 --new-seed)。
    如果刷新了盲读包,必须 --new-seed 并把旧的
    reports\jinjiang-r20\blindtest_packs\*.md 归档到 reports\jinjiang-r20\panel_<date>\
  step 8: 复跑 check + aggregate,把 effective_n / diversity_score / 升级项 diff 写入
    reports\jinjiang-r20\reader-blindtest-results.md 的「轮次对比」段。
  step 9: tools\reader_panel_runner.py check 自动把缺 modern provenance 的「真人」文件名文件
    降级为 L1 并打印原因。真人 sub-agent 回填的 JSON 必须带齐
    schema_version=2 / model_id / reading_log / pack_hash / isolation 双证据,
    缺一项就当 L1。
```

## 3. 真人 sub-agent 派发与验收

### 3.1 派发路径(三种,优先级递减)

1. **优先**:在 fork 会话跑 `py -3 -X utf8 tools\reader_panel_runner.py emit-prompt 1..5`,
   把 5 份 JSON 手工落盘到 `reader-N-真人-<persona>.json`。
2. **离线**:真人读者按 `prompts\reader\personas.json` 选一份 persona 阅读 4 个盲读包,
   写一份 JSON 落 `reader-N-真人-<persona>.json`。
3. **兜底**:本会话内 sub-agent 模拟(`reports\jinjiang-r20\sub-agent-reads\`),
   标注为 `sub-agent` 而非 `真人 sub-agent`,不升级 effective_n。

### 3.2 真人 sub-agent 与 sub-agent 模拟的区别(硬边界)

| 维度 | 真人 sub-agent(L2 真) | sub-agent 模拟(本会话) |
|---|---|---|
| source | 必须以「真人 sub-agent」开头 | 必须以「sub-agent」开头 |
| fork | 独立 fork 会话,独立 cwd | 本会话同 cwd |
| isolation.no_chronicle | true,机器校验 | true,人工声明 |
| isolation.no_frontmatter | true,机器校验 | true,人工声明 |
| isolation.cwd | 实际 run path | 实际 run path |
| isolation.persona_seed | 真人 sub-agent run 种子 | sub-agent run 种子 |
| 是否计入 effective_n | 是(L2 真) | 否,只入 `sub-agent-reads/` |
| 是否能升级读者判断 | 是(≥ 1 份 + effective_n ≥ 3) | 否,只能作为交叉比对 |

### 3.3 真人 sub-agent ≥ 1 份的最低硬要求

1. `source` 字段以「真人 sub-agent」或「真人读者」开头。
2. `schema_version` 等于 2。
3. `model_id`、`reading_log`、`pack_hash` 都填齐。
4. `isolation.no_chronicle` = true AND `isolation.no_frontmatter` = true。
5. `isolation.cwd` 是实际 run path,`isolation.persona_seed` 是当次种子。

缺任一项,`tools\reader_panel_runner.py check` 把该 JSON 降级为 L1 并打印原因。

## 4. 5 读者交叉 → 结构性改稿任务的升级规则

只有下列情况同时满足,才把读者结论升级为**结构性改稿任务**:

1. ≥ 3 份 reader JSON 在同一章 / 同一关系 / 同一钩子上得出同类判断(同点 ≥ 3)。
2. 同点 ≥ 3 中至少有 1 份是 L2 真人 sub-agent 或真人读者。
3. diversity_score ≥ 0.5(避免复读嫌疑升级)。
4. echo_panel = False(5 份之间未触发复读)。
5. 工程 E_min 与真人 R_min 同时显示失败(工程至少 E < 7,真人至少 R < 7)。

任一不满足,只能作为「单点观察」,不写进 `reports\jinjiang-r20\edit-decision-protocol.md §3` 的改稿顺序。

## 5. 与已有文档的边界(不能混用)

| 命名 | 含义 | 适用 |
|---|---|---|
| S0 / S1 / S2 / S3 | 四层证据栈(晋江官方 / 行业共识 / 工程启发式 / 真人读者) | `jinjiang-quality-architecture.md` |
| E1 / E2 / E3 / E4 / E5 | 工程 5 维 | `晋江爆款基线.md §1` + `jinjiang_chapter_distance.py` |
| R1 / R2 / R3 / R4 / R5 | 真人 5 维 | `晋江爆款基线.md §2` + `reader_panel_runner.py` |
| L1 / L2 | 模型代理 / 真人(分类) | `reader-subagent-workflow.md` |
| M1 / M2 / M3 / M4 / M5 | 编辑端 5 模式 | `jinjiang-edit-modes.md`(本轮新增) |
| effective_n / diversity_score / echo_panel | 聚合统计 | `reader_panel_runner.py aggregate` |

## 6. 真人 sub-agent / 真人读者启动失败的兜底 SOP

完整版见 `docs\standards\jinjiang-quality-architecture.md §5`。

本节复述兜底链:

1. 优先路径(本轮优先使用):在 fork 会话跑 `emit-prompt 1..5`,把 5 份 JSON 手工落盘。
2. 离线路径:真人读者按 `prompts\reader\personas.json` 读 4 个盲读包,写一份 JSON。
3. 兜底路径(本轮已使用):本会话 sub-agent 模拟,落 `sub-agent-reads\`,不升级 L2。
4. 失败识别:≥ 14 天内**都无新增** reader L2 文件,本季自动回到「工程单轨模式」,所有文档把「读者分」措辞降级为「工程分」。
5. 失败时报告:`aggregate()` 必须把 `## pack_hash drift 警告` 一起加进结果顶部;L2 = 0 + drift 不为空时读者基线被双重削弱。

## 7. 当前会话的硬约束(截至 2026-09-04)

- effective_n = 0:所有「真人」文件名文件因缺 modern provenance 被降级为 L1。
- echo_panel = True:5 份 L1 flag Jaccard 仅 0.167,复读嫌疑高。
- sub-agent A 模拟已完成(`reports\jinjiang-r20\sub-agent-reads\sub-agent-reader-A-plotsim-mid_a-502-510.md`),落兜底路径。
- sub-agent B / C 待下一轮独立 fork 派发。
- 在 effective_n ≥ 3 + diversity_score ≥ 0.5 + L2 ≥ 1 三项同时满足之前,
  本节描述的工作流只能跑 verify / emit / aggregate 骨架,不能跑出「读者会追」以外的升级证据。

## 8. 维护纪律

- 改 §1 persona 表任一行的 keep_if / drop_if / must_disagree_with → 必须同步改
  `prompts\reader\personas.json` + `tools\reader_subagent_driver.py` 公式 +
  `tests\test_reader_subagent_driver.py` 钉死回归。
- 改 §4 升级规则阈值(默认 ≥ 3 / diversity ≥ 0.5) → 必须先在 `jinjiang-quality-architecture.md §5`
  同步改,避免两份文档漂移。
- 新增 sub-agent 报告 → 必须先在 `reports\jinjiang-r20\sub-agent-cross-pollination-<date>.md`
  追加,不要覆盖旧报告。
- sub-agent 报告 ≥ 3 份同点(同一章 / 同一关系 / 同一钩子) → 触发 §4 升级规则的「同点 ≥ 3」检查,
  通过后写入 `reports\jinjiang-r20\edit-decision-protocol.md §3` 改稿顺序。
