# handbook · 创作记录（历史·报告·统计）

镇狱之渊的**过程性文档**集中在这里——审查报告、润色日志、规划、统计、lint 快照。
都是历史记录，不是要遵循的标准；引擎和站点都不读本目录，删改不影响生成与发布。

> **权威标准不在这里** → 见 `../standards/`（文笔范文标准、rubric、playbook、幕后规则、审查流程）。

> **不在这里的项目文件（各有归处，勿移）：**
> - 章节正文 → `seasons/01-xianxia/chronicle/`
> - 故事设定/状态（引擎读）→ `seasons/01-xianxia/{world.md, npcs.md, arc.json, ties.json}`、根目录 `trends.md`
> - 角色灵魂 → `souls/`　·　引擎 → `engine/`　·　发布站点 → `docs/{index.html, read.html, chronicle.json, *.epub}`
> - 执笔总规则 → 根目录 `CLAUDE.md`

---

## 命名约定（前缀即类别）

| 前缀 | 含义 | 文件 |
|------|------|------|
| `PHASE*-…-AUDIT` | 阶段/章段的剧情漏洞·伏笔·CP·POV 核查报告 | `PHASE2-AUDIT-REPORT.md`、`PHASE2-CP-AUDIT.md`、`PHASE3-CH215-280-AUDIT.md`、`PHASE4-CH301-435-AUDIT.md`、`PHASE4-E-POSTFAKE-AUDIT.md` |
| `AUDIT-GOLD-…` / `AUDIT-RANGE-…` | 金标/区段专项审查 | `AUDIT-GOLD-01-PROSE.md` … `AUDIT-GOLD-05-THEME.md`、`AUDIT-RANGE-06-CH261-310.md` |
| `POLISH-S1-…` | 第一季逐段精修日志（按章号区间） | `POLISH-S1-15.md` … `POLISH-S1-475-489.md` |
| `POLISH-STATUS.md` | 润色总进度与文档索引 | — |
| `plan-` | 规划草案 | `plan-ch200-465.md`、`plan-ch429-458-archived.md`（已归档） |
| `metrics-` / `summary-` | 指标与阶段小结 | `metrics-kpi-v3.txt`、`summary-v4.md` |
| `cast-` | 出场统计/缺席追踪（曾是 `_cast_*`） | `cast-gaps.txt`、`cast-size.txt`、`cast-stats.txt`、`cast-update-ch121-240.log` |
| `lint-` | 文笔门 `prose_lint.py` 的扫描输出快照 | `lint-baseline-2026-06-24-v2.txt`、`lint-full-2026-06-24.txt` |

## 入口
- 要写/审一章 → 去 `../standards/文笔范文标准.md`。
- 想看精修进度 → 本目录 `POLISH-STATUS.md`。

> 注：本目录在 `docs/` 下会随 GitHub Pages 发布（含剧透/规划）。若不想公开，把 `handbook/` 与 `standards/` 一起移出 `docs/` 即可——记得同步改 `engine/writer.py` 里 `docs/standards/{rubric,playbook}.md` 两处路径。
