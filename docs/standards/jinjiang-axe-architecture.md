# 晋江磨斧头架构 v1（项目级索引 · 2026-09-04 焊入）

> 目的：把"我们怎么才能知道什么是晋江高分标准，规范，文笔，编辑悬念"
> 这一组模糊问题，翻译成**6 份互相引用、互相钉死、不漂移**的项目级文档。
>
> 适用：每一章动笔前、动笔后、跨章 ≥ 30 章累计改稿后。
> 不替代：canonical 主流程 `docs/standards/novel-workflow.md`。
> 维护：项目维护者。每两周或每 ≥ 30 章累计改稿后必须复审本索引与下层文档。
>
> 上游触发（用户原话 2026-09-04）：
> "先暂停。我们先研究一下怎么样子架构 architect, 磨斧头。
> 我们怎么才能知道什么是晋江高分标准，规范，和文笔，编辑悬念等等。
> 把研究好的新思路，焊死进 repo 里面，然后我们再继续。"

## 0. 三句话

1. **磨斧头 = 6 文档脊柱**。任何"距晋江爆款还差多少"的回答，必须能指回这 6 份文档里的至少一条硬规则；不能指回 = 没磨过斧。
2. **磨斧头不等同于改稿**。磨斧头是**改稿前**先把工具 / 标准 / 读者协议 / 词表焊进 repo；改稿是**磨完后**按硬规则动笔。
3. **L2 = 0 期间禁词清单**已焊进 `reader_panel_runner.py` + `磨斧头研究-2026-09-04.md §13`。任何"读者会追 / 爆款 / 上瘾"措辞都是 CI 拒，不接受手写例外。

## 1. 6 文档脊柱（不可漏链）

```
1. docs/standards/jinjiang-quality-architecture.md
   四层证据栈 S0 官方 / S1 共识 / S2 工程 / S3 真人
   不混命名：S2 != L1，S3 != L2
2. docs/standards/jinjiang-edit-modes.md
   编辑端 5 模式 M1 开场钩 / M2 中段选择 / M3 章尾钩 / M4 主动 / M5 关系后果
   每条：触发条件 + 禁用清单 + 工艺清单
3. docs/standards/晋江爆款基线.md
   工程 5 维 E1-E5（机器可打分）+ 真人 5 维 R1-R5（盲读打分）
   + 编辑五问 + 上瘾单元 + 双轨合并公式
4. docs/standards/5-reader-cross-workflow.md
   5 persona 池 + 同点 >= 3 升级规则 + 复读去重 + isolation 硬门
   + 措辞词表（与 §1 §2 §3 互锁）
5. docs/standards/novel-workflow.md
   canonical 主流程；本文件"附 · 5 读者交叉 + 真人 sub-agent 工作流
   （必跑节点）"是 §4 的硬约束落地
6. reports/jinjiang-r20/磨斧头研究-2026-09-04.md
   研究端留底：S0 事实 / S1 共识 / 5 工艺红旗 / JJ-LINT 路线图 /
   sub-agent 模拟边界 / 措辞词表 / 维护纪律
```

**漏链判定**：

- 报告只引 §3 不引 §1 = 漏"哪些层能证明"
- 改稿只动 §5 不动 §2 = 漏"为什么这么改"
- 同点判断只动 §4 不动 §6 = 漏"5 工艺红旗的工程实现"

## 2. 6 文档的硬互锁

| 触发改动 | 必须同步改 | 钉死回归测试 |
|---|---|---|
| §1 四层栈的层名 / 边界 | §4 §5 §6 + 本文件 | `tests/test_reader_panel_runner.py` |
| §2 5 模式的判据 / 禁用清单 | §3 工程 5 维 + §6 §4.2 | `tools/chapter_by_chapter_audit.py` + §6 §4.2 |
| §3 工程 5 维公式 | §2 + `tools/jinjiang_chapter_distance.py` | `tests/test_jinjiang_chapter_distance.py` |
| §3 真人 5 维公式 | §4 + `tools/reader_panel_runner.py` | `tests/test_reader_panel_runner.py` |
| §4 persona 表 / 阈值 | §3 §5 §6 + `prompts/reader/personas.json` | `tests/test_reader_subagent_driver.py` |
| §5 主流程节点 | §4 + handoff.md + SKILL.md | 无（流程文档） |
| §6 措辞词表 | §1 §3 §4 §5 + `tools/reader_panel_runner.py` | `tests/test_reader_panel_runner.py` |
| §6 JJ-LINT 规则 | `engine/prose_lint.py` | 暂无（v1 留待 batch 15） |

## 3. 磨斧头研究产出 · 已焊 vs 待焊 vs 已批留底

### 3.1 已焊（v1 落地）

| 研究端产出 | 落地位置 | 落地状态 |
|---|---|---|
| 四层证据栈 S0/S1/S2/S3 | §1 | 已焊 |
| 5 编辑模式 M1-M5 | §2 | 已焊 |
| 工程 + 真人 5 维 | §3 | 已焊 |
| 5 persona + 同点 >= 3 | §4 | 已焊 |
| canonical 主流程读者侧硬约束 | §5 附 | 已焊 |
| 措辞词表 13 条 | §6 §13 + `reader_panel_runner.py` | 已焊 |
| isolation 8 字段硬门 | §6 §9.2 + §4 §9.2 | 已焊 |
| agent_n / human_reader_n / platform_signal_n 三栏 | §6 §9.3 + §4 §9.3 | 已焊 |
| 同包前后对照硬门 | §6 §9.4 + §4 §9.4 | 已焊 |
| 升级阈值统一（§4 §9.6） | §4 §9.6 + §1 §6 | 已焊 |
| 真人 sub-agent 兜底 SOP | §1 §5 + §4 §6 | 已焊 |

### 3.2 本批 v1 新焊（2026-09-04 batch 14）

| 研究端产出 | 落地位置 | 落地状态 |
|---|---|---|
| 6 文档脊柱索引（本文件） | `docs/standards/jinjiang-axe-architecture.md` | **本批新增** |
| JJ-LINT-01 那一X 物象回环 | `engine/prose_lint.py` | **本批焊入**（6 WARN；40 仅作研究分层参考，默认不升级 ERROR） |
| JJ-LINT-02 自己 回环（独立计） | `engine/prose_lint.py` | **本批焊入**（thresholds: 行数/4 WARN，WARN-only 不升级 ERROR） |
| JJ-LINT-07 单字断章 | `engine/prose_lint.py` | **本批焊入**（thresholds: 末行 ≤ 2 汉字 WARN） |
| sub-agent 模拟真人 · 1 次端到端 demo | `reports/jinjiang-r20/sub-agent-reads/sub-agent-reader-Demo-2026-09-04.md` | **本批新增** |
| demo run 留底 | §6 §15 + §4 §11 | **本批追加** |

### 3.3 待焊（v1 显式延后到 batch 15+）

| 研究端产出 | 延后原因 | 重启条件 |
|---|---|---|
| JJ-LINT-03 末段短句密度 | 与 §2 M3 章尾钩语义重叠；先观察 JJ-LINT-07 单字断章命中，再决定是否合并 | batch 15 复审 JJ-LINT-07 命中率 |
| JJ-LINT-04 POV 远观 | 跨章对话 + 多人 POV 检测需要新 fixture，先放开 | batch 15 准备 test fixture |
| JJ-LINT-05 问答空转 | 与 §2 M2 中段选择部分重叠，需要先看 E2 命中分布 | batch 16 复审 |
| JJ-LINT-06 末段气氛句 | 与现有 FILLER 检测重叠；先观察 FILLER 命中 | batch 15 复审 |
| E6 章末钩类型枚举 | `tools/jinjiang_chapter_distance.py` 没有钩类型字段 | batch 16 工程改造 |
| POV 主动发起方识别 | 需要新 schema 字段 | batch 16 schema 改造 |
| `info_gap_count` 字段 | 需要新 audit 字段 | batch 17 audit 改造 |
| `bucket_beat_score` 字段 | 需要节奏量化模型 | batch 17+ 启动研究 |

## 4. 磨斧头不可省的三件事

1. **跑 verify**：`py -3 -X utf8 tools/reader_subagent_driver.py verify`
   任何时点开改稿循环前必跑，证明 5 份 L1 在 drop_chapter / love_relation / next_chapter_focus
   三轴上是分化的。
2. **跑 check + aggregate**：`py -3 -X utf8 tools/reader_panel_runner.py check` + `aggregate`
   锁 baseline 的 effective_n / diversity_score / echo_panel / drift 警告。
3. **锁 distance 快照**：`py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
   + `py -3 -X utf8 tools/refresh_distance_summary.py`
   锁本季距离晋江爆款的诚实答案。

**缺任一 = 工程层硬错误，必须在 PR review 阶段 BLOCKED**。

## 5. 边界（不可越线）

- 磨斧头文档不动 chapter md / pack_hash / reader JSON 已写字段。
- §6 留底的"研究端建议"不是工程硬门；工程硬门在 §1 §2 §3 §4 §5 已经焊过的条目上。
- §3.3 延后清单里的任何一条，**没有本批施工** = 允许；**偷偷施工** = 越级。
- 本文件每两周或 ≥ 30 章累计改稿后必须复审 §3 三张表的迁移。
- 修改 §6 §13 措辞词表前必须先看 `tools/reader_panel_runner.py` 的
  `FORBIDDEN_TERMS_ALWAYS` / `FORBIDDEN_TERMS_WITH_PROVENANCE` 是否同步；
  不同步 = 文档与代码漂移。

## 6. 与下一季的关系

- 老季（`legacy_mode: true`）只作为素材与审计对象；本季必须用本索引跑完整 baseline。
- 新季必须设置 `human_decision_required: true` + `legacy_mode: false`，且至少有一个
  上瘾单元先跑通本索引 §3 §3.1 全部 11 条 + §3.2 全部 5 条 = 16 条已焊项。

## 7. 维护纪律

- 本文件 §3 三张表新增 / 迁移条目，必须同步在 git commit message 标注
  `磨斧头 / axe-architecture / batch-N`。
- 改 §2 互锁表的任意一行 → 必须先在 §1 §2 §3 §4 §5 §6 找到引用该行的位置同步修改。
- 跨文档命名漂移（`S2 != L1`, `S3 != L2`）发现后必须在 24 小时内复审 6 文档全链。
