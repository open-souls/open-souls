# standards · 创作标准（权威·要遵循）

写作 / 审查 / 续写时**必须遵循**的标准都集中在这里。
其中两份（`rubric.md`、`playbook.md`）同时被写作引擎读取，因此用 ascii 文件名。

| 文件 | 定义 | 谁用 |
|------|------|------|
| **`文笔范文标准.md`** | **唯一文笔标准**：文笔七维 + 以第1–10回为范文 + 反范文。合并自原 JINJIANG-CRAFT（宏观手法）与文笔七维。 | 人 / AI 写作与审校 |
| **`雅俗共赏.md`** | **双层文本标准**：表层（爽）保下限 + 深层（文学）抬上限，一笔写两层，被欣赏最大化。与 `CLAUDE.md §零` 男女频平衡正交。 | 人 / AI 写作与审校 |
| `幕后叙事规则.md` | 幕后 / 省略（offscreen）叙事的处理规则。 | 人 / AI 写作 |
| `审查流程.md` | 章节审查的流程规范（原 REVIEW-PROTOCOL）。 | 审校 |
| `评审方法.md` | 单章 `review: \|` + `score: N/14` 的手搓方法论（七维 + 9 硬门 + 输出格式 + worked example）。 | 审校 |
| `rubric.md` | 章级评分表（钩子/爽痛/反差…）+ 节奏硬门 + 安全审查。 | 引擎 `engine/writer.py` ＋ 人 |
| `playbook.md` | 流量密码 · 桥段库（中/日/西套路）。 | 引擎 `engine/writer.py` ＋ 人 |

## 入口
写 / 审一章前，先读 **`文笔范文标准.md`**；评分用 `rubric.md`；单章手搓 `review: \|` + `score: N/14` 看 **`评审方法.md`**；机器门跑 `engine/prose_lint.py`。
拿不准怎么写——翻回第 1–10 回对，那十章就是范文本体。

## 关系
- **机器反向门**：`engine/prose_lint.py`（地板，只卡垮没垮）。本目录是天花板。
- **历史记录 / 报告**（审查报告、润色日志、规划、统计、lint 快照）在 `../handbook/`，不属于"标准"。
- **执笔总规则**（角色出场/cast 节奏/亲密系统等全局铁律）在仓库根 `CLAUDE.md`，不放这里（Claude Code 自动加载）。
- **故事设定/状态**（引擎读）在 `seasons/01-xianxia/{world.md, npcs.md, arc.json, ties.json}`，是项目数据，不是标准。

> 注：本目录在 `docs/` 下会随 GitHub Pages 发布。若不想公开标准，把 `standards/` 与 `handbook/` 一起移出 `docs/` 即可——记得同步改 `engine/writer.py` 里 `docs/standards/{rubric,playbook}.md` 两处路径。
