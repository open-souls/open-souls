# 读者盲读工作流（含 sub-agent 模拟 + 真人切点）

> 目的：把晋江盲读从临时工具固化进工程流程，使改稿与判断不再依赖某次会话。
>
> 协议：`reports/jinjiang-r20/reader-blindtest-protocol.md`
> 评分：`reports/jinjiang-r20/jinjiang-rubric.md`
> 改稿：`reports/jinjiang-r20/edit-decision-protocol.md`
> 工程基线：`docs/standards/晋江爆款基线.md`
> 入口脚本：`tools/reader_panel_runner.py`（取代 `tools/reader_subagent_workflow.py` 旧的 main 入口）
> 配套：`prompts/reader/personas.json`

## 0. 边界（先看）

- 盲读分两层，**两层都必须执行**：
  - **L1 模型代理模拟**：≥5 份结构化 JSON，由 agent 或脚本生成。只用于覆盖与方向识别。
  - **L2 真人 sub-agent / 真人读者**：≥1 份起步，逐步替换为真人读者。最终升级判定权。
- 模型代理 ≠ 真人读者。任何把模型代理当真人用的判断（如"读者会追""上瘾""爆款"）**禁止**。
- L1 < 5 份时，禁止使用"多名读者共同"等聚合结论。
- L2 真实样本 = 0 时，**禁止使用"读者会追""读者确认""上瘾""爆款"等判断**。这是工程层硬约束，不是软建议。
- L1 必须先过 diversity 校验；复读嫌疑高时 L1 整体不计入 effective_n。

## 1. 角色与产出物

| 角色 | 产出物 | 文件 |
|---|---|---|
| L1 模型代理盲读 | ≥5 份 persona JSON | `reports/jinjiang-r20/reader-<n>.json` |
| L2 真人 sub-agent 盲读 | ≥1 份 JSON | `reports/jinjiang-r20/reader-<n>-真人-<persona>.json` |
| L2 真人读者盲读 | 由人输入替换同位置 JSON | 同上 |
| 聚合汇总 | Markdown | `reports/jinjiang-r20/reader-blindtest-results.md` |
| 摘要 | JSON | `reports/jinjiang-r20/blindtest-summaries.json` |
| 盲读包 | 4 包 markdown | `reports/jinjiang-r20/blindtest_packs/*.md` |

**必填字段**（缺一项视为不合格，需要重跑）：

```json
{
  "id": "1",
  "label": "晋江古言仙侠资深读者",
  "perspective": "常读古言仙侠...",
  "drop": {"pack": "mid_a", "chapter": "506", "reason": "..."},
  "love_relation": {"name": "林彻×林夙", "reason": "..."},
  "next_chapter_focus": {"chapter": "1145", "reason": "..."},
  "stay_to_50": false,
  "stay_reason": "...",
  "pattern_flags": {
    "info_not_action": true,
    "smart_drop": false,
    "passive_chain": true
  },
  "isolation": {
    "no_chronicle": true,
    "no_frontmatter": true,
    "cwd": "/isolated/cwd",
    "persona_seed": "persona-1-2026-09-04"
  },
  "source": "真人 sub-agent（独立 fork 模型会话），通过 mcp 回到本会话。"
}
```

## 2. 5 份 persona 池（必带差异化）

L1 必须从 `prompts/reader/personas.json` 中各取一份 persona，**禁止同一模板复制**。每份 persona 都自带"留下条件 / 触发弃读 / 反向自检"三项硬约束。

| id | label | 留下条件 | 触发弃读 |
|----|------|---------|---------|
| 1 | 晋江古言仙侠资深读者 | 角色做选择且付代价 | 中段三章以上无身份后果兑现 |
| 2 | 晋江追更党，敏感钩子 | 每章有下一章必答的具体问题 | 章末落"她没回""明日再看" |
| 3 | 晋江现言读者跨题材测试 | 60% 章节独立可读 | 首段铺人物关系而非冲突 |
| 4 | 晋江女强权谋线读者 | 女主/POV 主动决定 + 身份后果 | 主角静观、不替、不决定 |
| 5 | 晋江新读者 | 出现一次让心里疼过的情感动作 | 三章以上无新建立的关系升压 |

**怎么校验差异化**：`tools/reader_panel_runner.py` 的 `diversity_score()` 计算 flag/drop/reason 三个轴上的平均 Jaccard 距离；任一 < 阈值即视为复读嫌疑（echo_panel=True），L1 不计入 effective_n。阈值：`flag ≥ 0.5`、`reason ≥ 0.4`、`drop ≥ 0.4`。

## 3. 工作流（必跑顺序）

```
[主会话]  生成盲读包  py -3 -X utf8 tools\reader_blindtest_pack.py
            ↓
         启动 ≥5 份 L1  (5 个独立 persona 调用，persona seed 写到 isolation)
            ↓
         启动真人 sub-agent  (≥1 份独立 fork 会话，独立 cwd + 禁止读 chronicle/)
            ↓
[主会话]  py -3 -X utf8 tools\reader_panel_runner.py check
            ↓
         py -3 -X utf8 tools\reader_panel_runner.py aggregate
            ↓
         看 effective_n + echo_panel + 升级项
            ↓
         effective_n ≥ 3 + 不 echo → 写入 edit-decision-protocol §3 顺序
            ↓
[下一轮]  改稿后再次生成盲读包（保留 seed），覆盖相同章节
```

## 4. L1 模型代理盲读要点

- L1 5 份必须分别调用，persona 互不相同，**禁止同一模板复制 5 份**。
- L1 只能读盲读包正文（`reports/jinjiang-r20/blindtest_packs/*.md`），**禁止**读 `chronicle/` 原档、`frontmatter`、`review`、`score` 或 grader 输出。
- L1 输出必须是结构化 JSON，不要写散文式分析。
- 每一份 L1 必须在 `drop`/`love_relation`/`next_chapter_focus` 里指到具体章节号，不能用"整本"代替。
- L1 必须在 `isolation.persona_seed` 里写明当次种子（persona + 日期），让复读嫌疑可复测。

## 5. L2 真人 sub-agent 工作方式

- 由主 Codex 会话通过 `spawn_agent`/`multi_agent_v1` 调用**独立 fork 会话**。
- 传给 sub-agent 的最小任务包（`tools/reader_panel_runner.py emit-prompt <persona_id>` 自动生成）：
  1. 本工作流文档；
  2. 4 个盲读包路径；
  3. persona 描述（label + perspective + 留下条件 + 触发弃读 + 反向自检）；
  4. 必填字段清单；
  5. 落盘文件名约定（`reader-<n>-真人-<persona>.json`）。
- sub-agent 完成盲读后必须写一份 JSON，再由主会话持久化到 `reader-<n>-真人-<persona>.json`。
- sub-agent 必须独立 cwd 启动，**禁止**读 `chronicle/` 原档、`frontmatter`、`review`；在 JSON 中通过 `isolation.no_chronicle = true / no_frontmatter = true` 自证。
- sub-agent 的判断**不带**模型代理模拟字样；`source` 字段必须写明"真人 sub-agent（独立 fork 模型会话），通过 mcp 回到本会话"。
- 当真人 sub-agent 增加到 3 份及以上时，结构任务升级规则切换为：**真人 sub-agent 不少于 3 人同点，才升级**。

## 6. L2 真人读者录入（可选）

- 真人读者盲读由人按 persona 阅读盲读包后填一份 JSON。
- 文件名同 sub-agent：`reader-<n>-真人-<persona>.json`，`source` 字段写"真人读者，作者以外"。
- ≥1 份真人读者 + ≥2 份真人 sub-agent 才视为"L2 完整"。

## 7. 升级矩阵（effective_n ≥ 3 才允许升级）

> **复读嫌疑（echo_panel=True）时不升级，仅作方向记录。**

| 信号 | L1 复读嫌疑=0 时的升级阈值 | L2 真实样本存在时的升级阈值 | 升级动作 | 退出条件 |
|------|-------------------------|--------------------------|---------|---------|
| 同章弃读 | ≥4 名 L1（避免去重后 echo trio） | ≥2 名 L2 同点 | `edit-decision-protocol §3` 步 1 强制改稿 | 该章下一轮 L2 ≥1 名 stay |
| 同关系追问 | ≥3 名 L1+L2 | ≥2 名 L2 同点 | 该关系必须有可见动作兑现 | 该关系在 ≥5 章内出现至少 1 次主动承担动作 |
| 同一禁区（pattern_flag 三键之一） | ≥3 名 L1+L2（已含 readout diff） | ≥2 名 L2 真投中 | 写入禁区条文 `rubric §3` | 下一轮同包 flag 命中 < 1 |
| 50 章留存失败 | 意愿份数 ≥ 总数一半 | ≥2 名 L2 yes | 中段包整体重审 | 中段包 L2 ≥1 名 yes |
| 跨题材门槛失败 | persona 3 ≥1 名 L1/L2 弃读 | ≥1 名 L2 + ≥2 名 L1 | 单章独立可读必须先修 | persona 3 在同包 ≥3 章独立可读 |

**禁止**：

- "5 份 L1 + 0 份 L2" 就改 structural rewrite。
- 用 `info_not_action` 命中人数去证明"读者会弃读"。flag 是结构诊断信号，不驱动"取消发布"。
- 把 `reader-1-真人.json` 等历史文件直接当成 L2 计入；隔离字段未填或填 false 必须降级为 L1。

## 8. 与改稿循环的强耦合（hard coupling）

- **改稿前**：必须先跑本工作流的盲读，盲读结果驱动改稿顺序。
- **改稿后**：必须重跑盲读，覆盖相同章节，且 isolation.persona_seed 必须沿用上次 seed。
- **一轮 ≥ 3 章改稿后**：必须跑一次 `tools/reader_panel_runner.py aggregate`，把 effective_n / diversity_score / 升级项 diff 写入 `reports/jinjiang-r20/reader-blindtest-results.md` 的"轮次对比"段。
- **跨章节 ≥ 30 章累计改稿后**：必须把 persona 池与盲读包范围（开篇/中段 A/中段 B/最新）一起刷新，避免读者记忆偏差；同时把旧的盲读包移到 `reports/jinjiang-r20/panel_<date>/` 归档。

## 9. 不允许的省略

- 不能跳过生成盲读包，直接读 chronicle 原档。
- 不能让 L1 代理超过 5 份而不补 L2。
- L2 真实样本 = 0 时禁止使用"读者确认 / 读者会追 / 上瘾 / 爆款"判断。
- L1 < 5 份时禁止聚合"多名读者共同"结论。
- 不能用 `score: N/14`、`binge_score`、`engineering_score` 替代盲读结果。
- 不能把 echo_panel=True 时的 L1 unanimous 结论当成多人共识。
- 不能用文件名（`reader-*-真人.json`）判定 L2；只有 `source` + `isolation` 双证据齐备才算 L2。

## 10. 当前会话归档

- 2026-09-04：5 份模型代理 + 1 份"真人"文件名文件。
  - **当前 effective_n = 0**：所有"真人"文件名文件因缺少 isolation 双证据被降级为 L1。
  - echo_panel = True：5 份 L1 的 flag Jaccard 仅 0.167，复读嫌疑高。
  - 中段包 504–506 区间被升级为下一轮改稿方向（**未达升级阈值，仅作方向记录**）。
- 下一轮**先**补 isolation 双证据 + ≥1 份真人 sub-agent，再谈升级。
- 后续每次复测必须把 persona_seed / pack_hash / model_id 一并存档。

## 11. 改稿循环 diff（每轮必跑）

每轮盲读结果必须能回答下列问题：

1. 上一轮升级项退出没？（命中人数是否下降、退出条件是否达成）
2. diversity_score 升降（≥0.5 算合格）
3. effective_n 变化（≥3 才能继续谈升级）
4. persona_seed 是否沿用（防止读者记忆偏差）

`tools/reader_panel_runner.py` 当前一轮的输出顶部 `effective_n` / `diversity_score` / `echo_panel` 三行即为这一轮的 diff 锚点。
