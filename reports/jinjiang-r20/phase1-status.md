# Phase 1 · 把小说 review 到晋江爆款基线 · 进度

> 时间：2026-09-04（America/Denver）
> 任务：把小说 review / edit 到晋江爆款、上瘾、上头。
> 当前：本轮已完成机器层基建，不改正文。

## 1. 本轮已落地（全部只读，可直接验）

| 文件 | 角色 |
|------|------|
| `tools/reader_panel_runner.py` | 替换旧 `reader_subagent_workflow.py` 主入口；带 `check / aggregate / emit-prompt / regenerate` 四个子命令；diversity_score 三轴；effective_n = L2 + diversified L1 |
| `tests/test_reader_panel_runner.py` | 7/7 passed，钉死 P0：L2 必须 source + isolation + provenance；文件名不算证据；L1 复读不计入 effective_n |
| `docs/reader-subagent-workflow.md` | 11 节：边界 / 角色与产出 / persona 池 / 工作流 / L1 要点 / L2 sub-agent / L2 真人读者 / 升级矩阵 / 改稿耦合 / 不允许省略 / 当前归档 / 改稿循环 diff |
| `docs/standards/晋江爆款基线.md` | 工程 5 维 + 真人 5 维 + 禁区 8 条 + 双轨打分公式 + "上瘾单元" |
| `prompts/reader/personas.json` | 5 份差异化 persona，含反向自检 |
| `reports/jinjiang-r20/reader-prompt-3.txt` | emit-prompt 示范产物 |
| `reports/jinjiang-r20/rewrite_plans/mid_a-rewrite-plan.md` | mid_a 504–506 改稿方向（只读） |
| `reports/jinjiang-r20/edit_queues/phase1-machine-edits.md` | 机器层可改稿队列（不动正文） |
| `reports/jinjiang-r20/reader-panel-README.md` | 历史文件为何被降级 |
| `docs/standards/novel-workflow.md` 末段 | "读者盲读工作流（双轨基线）" |
| `docs/handbook/主编协作手册.md` 末段 | "与读者盲读工作流的对接" |
| `reports/jinjiang-r20/reader-blindtest-results.md` | 已更新，含 effective_n / diversity_score / echo_panel / 升级项 |

## 2. 已验证的工程数据

- `tools/chapter_by_chapter_audit.py` 跑过 1145 章：
  - 平均 binge_score = 9.98（门槛 9.5 ✓）
  - 平均字数 1817（门槛 1500 ✓）
  - 0 编辑标记 / 0 公式回环 / 0 短章
  - 526 章尾弱 / 89 句重 / 34 填充描写 / 1 开句同构

## 3. 当前未达成（与 goal 对照）

- **effective_n = 0**：L2 真实样本 = 0，所谓"5/5 命中"是 L1 复读。
- **改稿**:未启动。L2 ≥2 同点才能动笔。
- **mid_a 504–506**:方向记录已落，未达改稿阈值。

## 4. 下一步（按阻塞顺序）

1. **真人 sub-agent 上线**：在 fork 会话里跑 `py -3 -X utf8 tools/reader_panel_runner.py emit-prompt <1-5>`，把 schema_version=2 的 JSON 落盘到 `reader-<n>-真人-<persona>.json`。当前会话内 spawn_agent / multi_agent_v1 报 unsupported call，是已知阻塞。
2. **effective_n ≥ 3 + echo_panel=False** → 进入改稿循环。
3. **先做 P0 填充描写 34 章**（机器可改、不涉文学判断），跑 lint + audit 校验。
4. **再做 P1 句重 89 章**（每章挑保留哪一句）。
5. **最后做 P1 章尾弱 526 章**（最大体量，按 50 章试点）。
6. 每改 10–20 章重跑盲读对比。

## 5. 一句话

机器层基建到位 + 7 个测试绿 + 真实差距摆在台面；下一步阻塞在"真人 sub-agent 上线"，本会话内无法绕开。
