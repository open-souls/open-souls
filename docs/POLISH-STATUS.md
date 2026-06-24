# Polish Status · 2026-06-24 实时

> 主编在跑的精修 sweep 实时状态。每有重大变化更新。

## 进度

| 维度 | baseline | 当前 | 变化 |
|------|---------|------|------|
| ERROR | 189 | **0** | -189 (100%) |
| WARN | 235 | 64 | -171 (73%) |
| Total | 424 | 428 | +4 (cron 加) |

**全卷 0 ERROR，prose_lint CI 过线。**

## 已完成

- ✅ **Batch B** (ch101-200) — 100/100 章过 lint + ships 字段回补 23 章
- ✅ **Batch C** (ch201-300) — 99/99 章过 lint
- ✅ **Batch D** (ch301-424) — 0 ERROR + ch423/424 anchors/payoff/transitions 补齐
- ✅ **ch425-428** (cron 新章) — 4 章 inline polished
- ✅ **ch300** (1 个残留 filler) — 已修
- ✅ 2 份 audit 报告（伏笔 + CP）写入 docs/

## 进行中（agents 后台）

- 🚀 **Batch A** (ch001-100) — editing agent
- 🚀 **Phase 2 POV 旋转** (ch201-428) — 目标把林夙 POV 从 98.4% 压到 60%

## 下一步触发

- 任何 agent 返回 → 跑 `tools/review_batch.py <range>` 抽检
- Batches A + B 返回 → 全卷 lint 复跑
- Phase 2 POV 完成 → 复跑 audit 看 POV 比例

## Phase 2/3 backlog

1. **POV 旋转** (进行中)
2. **ch301-350 苏×阿 补足** (audit 标出断崖)
3. **沈疏桐线 24 章内必须揭** (audit 标出紧迫)
4. **叶观澜前置** (POLISH §4.3 表)
5. **plot holes 修复** (待 audit 补 ch215-280)

## 文档

- `seasons/01-xianxia/JINJIANG-POLISH-PLAN.md` — 总纲（标 LOCKED）
- `docs/REVIEW-PROTOCOL.md` — 主编 review 9 条硬门
- `docs/PHASE2-AUDIT-REPORT.md` — 伏笔 actionable
- `docs/PHASE2-CP-AUDIT.md` — CP 同框 + POV 校准
- `docs/PHASE2-PROMPTS.md` — Phase 2 subagent prompts
- `docs/PHASE3-PROMPTS.md` — Phase 3 subagent prompts
- `tools/review_batch.py` — 批量审查工具
