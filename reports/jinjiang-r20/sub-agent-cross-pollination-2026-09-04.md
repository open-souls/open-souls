# Sub-agent 5-reader cross-pollination (2026-09-04 batch 14)

> 5-reader 兜底路径 demo run 留底。本文件汇总 5 份 L1-agent 报告的
> drop 候选 / love_relation / next_chapter_focus / 同点统计。
> **不**升级 effective_n（sub-agent 模拟不 = 真人读者）。

## 1. 5 份报告留底

| slug | persona_id | path |
|---|---|---|
| sub-agent-reader-A-Demo-2026-09-04 | 1 | `reports/jinjiang-r20/sub-agent-reads\sub-agent-reader-A-Demo-2026-09-04.md` |
| sub-agent-reader-B-persona2-2026-09-04 | 2 | `reports/jinjiang-r20/sub-agent-reads\sub-agent-reader-B-persona2-2026-09-04.md` |
| sub-agent-reader-C-persona3-2026-09-04 | 3 | `reports/jinjiang-r20/sub-agent-reads\sub-agent-reader-C-persona3-2026-09-04.md` |
| sub-agent-reader-D-persona4-2026-09-04 | 4 | `reports/jinjiang-r20/sub-agent-reads\sub-agent-reader-D-persona4-2026-09-04.md` |
| sub-agent-reader-E-persona5-2026-09-04 | 5 | `reports/jinjiang-r20/sub-agent-reads\sub-agent-reader-E-persona5-2026-09-04.md` |

## 2. drop 候选 · 同点统计

| chapter | A-Demo | B-persona2 | C-persona3 | D-persona4 | E-persona5 | 同点数 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| ch504 | partial留 | partial留 | partial留 | partial留 | 留 | 0 |
| ch505 | 留 | - | partial留 | partial留 | partial留 | 0 |
| ch509 | partial留 | - | - | drop | 留 | 1 |
| ch510 | drop | drop | drop | drop | drop | 5 |
| ch685 | - | drop | - | - | - | 1 |
| ch690 | - | 推测drop | - | - | - | 1 |

## 3. 同点 ≥ 3 章节（按 5-reader-cross-workflow §4 升级判断）

| chapter | 同点数 | L2 真证据 | diversity | 升级层 |
|---|:-:|:-:|:-:|---|
| ch510 | 4 (A+B+C+D+E) | 0 (sub-agent 模拟) | 0.8 (4 个不同 drop 理由) | **方向**（effective_n=0 + L2=0 阻断「结构 rewrite」） |
| ch504 | 5 (A+B+C+D+E 全留 / partial 留) | 0 | - | **方向**（positive） |

## 4. 结构性改稿任务 · 优先级

按 5-reader-cross-workflow §4 + §9.6 升级规则：

1. **ch510 (mid_a)** = 4 / 5 persona drop 候选 → **方向层已成立**；**结构 rewrite 未成立**（L2 = 0）。
2. **ch504 (mid_a)** = 5 / 5 persona 留 → **positive 方向**；可作为「范文参考」。
3. **ch505 (mid_a)** = 蜡信「拈起没拆」= A / D / E partial 留；与 ch510 末段短句密度同源问题。

## 5. 与 axe-gap.md 的 cross-check

- ch510 工程 E_min = 4 → 与 4 / 5 persona drop 一致。
- ch504 工程 E_min 实际不在 distance records（孤立包内）→ 仅作 persona 交叉证据。
- ch505 工程 E_min 不在 distance records → 同上。
- distance bottom 15 章（per distance-summary.md §6）= 全部 E_min = 4 / 5 / 6 → 与本表 drop 候选 ch510 同段（5xx 中段）。

## 6. 边界

- 本表 **不** 升级 L2 真证据（sub-agent 模拟不 = 真人读者）。
- 同点 = 4 触发「方向」层升级；**不**触发「结构 rewrite」（per §9.6 阈值 = 同点 ≥ 3 + diversity ≥ 0.5 + L2 ≥ 1）。
- 「ch510 应该改」是方向；「ch510 必须结构 rewrite」是结论 — **结论** 需要 ≥ 1 份 L2 真人 sub-agent / 真人读者落盘后才能写。
