# Open Souls 小说 Agent 交接

> 更新时间：2026-08-04
> 工作目录：`C:\Users\stanc\github\open-souls`
> 当前分支：`main`
> 上一份已推送的交接提交：`c843432`（`docs: add novel agent handoff`）
> 上一份已推送的小说工作提交：`d1af5c6`（`editor: pass chapters 042 and 054`）

## 目标与工作分工

当前目标是把《镇狱之渊》从“能生成章节”推进到可持续连载、达到晋江向读者预期的小说质量，并把小说 agent 做成可以反复迭代的生产流程。

- Claude Code 是受限的单章执行者：根据明确的目标章节、上下文和验收条件改稿。
- 主编是独立审核者：重新读正文，检查人物、因果、节奏、钩子、语言和安全边界，不接受 Claude 自报的 PASS。
- 机器检查是底线，不是文学质量证明：lint 通过不等于好看，更不等于爆款。
- 当前只把“单章可验证通过”当作阶段性目标；整本书的晋江水准和市场表现仍需要持续的人类阅读、连载反馈和读者证据。

## 已完成

### 1. Agent 与批处理流程

- `engine/batch_rewrite.py` 已能解析精确的 `(chapter, path)` 失败目标，同时支持 `NNN-*.md` 与 `chNNN-*.md` 文件名。
- 已处理同编号重复分支问题：如果 canonical 文件通过、另一个重复文件失败，状态和 picker 会继续暴露真实失败路径，不会静默改错文件。
- alternate / parallel / archive 分支不会被自动改写，但会在状态中报告，避免把历史分支误当成主线。
- prompt 会携带 `TARGET_FILE`，`engine/run_dispatch.py` 会尊重这个绝对目标路径；因此 Claude 不会因为同编号文件存在而自行选到另一份稿子。
- 已加入受控的副作用快照、目标文件约束、严格 editorial gate、安全检查和确定性 prose lint；Claude 的返回内容必须经过本地独立检查。
- Windows 下超时会杀掉受控的 Claude 子进程树，避免批处理返回后留下失控进程。
- 默认预算已提高到每章 `12.0 USD`，推荐调用方式：

  ```powershell
  python engine/run_dispatch.py --chapters chNNN,chMMM --workers 2 --max-budget-usd 12.0 --effort high --timeout-sec 420
  ```

- `tools/review_batch.py` 的严格入口是 `--strict-editorial --file <target>`；不要只看 Claude receipt。
- `BATCH_REWRITE_STATUS.md` 已记录 picker 审计、批处理结果和当前限制。

### 2. 本轮及前轮主编改稿

本轮 Claude 的产出全部经过主编复读；Claude 被阻断、超时或缺少验收元数据时，由主编直接回炉，不把模型状态伪装成通过。

| 章节 | 主编结果 | 证据 |
|---|---|---|
| 034《顺手》 | 1596 字，补足阿湄偷宗门信、首次遇见林夷的动作和压力；lint、安全、formula、strict editorial 均通过 | `a2d85a7` |
| 035《凌朔案前》 | 1560 字，收紧凌朔/沈疏桐冷案和林夷旧印的因果；各项聚焦 gate 通过 | `a2d85a7` |
| 042《姜玉衡议》 | 1536 字，保留玉尺—林家三公子—余师兄旧账—屏风呼吸的信息链，去除模板化墙式表达；各项聚焦 gate 通过 | `d1af5c6` |
| 054《礼匣》 | 1727 字，保留 Claude 有效场面，补充主编审核元数据并清掉重复模板词；各项聚焦 gate 通过 | `d1af5c6` |
| 881 alternate 分支 | 已做过路径明确的替代分支清理 | `abc56ea` |
| 932 | 已做过主编清理并提交 | `4520e3d` |

本轮 Claude 的具体情况：034、035 有实际改动但因严格 editorial 不通过；042 超时且未形成可接收改动；054 有实际场面但缺 review/score 元数据。最终提交内容以主编版本为准。

### 3. handoff 提交之后的最近一批

本批目标是 picker 选出的 `061-蒹葭.md` 和 `116-监守.md`。两路 Claude runner 最终都为 `BLOCKED`，没有任何一章可以直接收稿。

- `061-蒹葭.md`：Claude `ok`，实际改动 `120 insertions / 146 deletions`；prose lint、safety、formula scan 都通过，但严格 editorial 因 frontmatter 缺 `review` 和 `score` 拒收。当前改稿仍在工作树中，尚未提交，也没有被主编确认采用。
- `116-监守.md`：Claude 在 `425.9s` 超时，`changed: no`；receipt 记录 prose lint、strict editorial、formula scan 均失败，命中 `wall_formula: 3`。正文没有被改动。
- 本次 runner 以 exit code `1` 返回；没有启动下一批，也没有把 Claude 的 BLOCKED 结果伪装成通过。

因此，下一位接手者首先要处理工作树里的 061：重新读全文，判断 Claude 的场面是否值得保留，补足基于正文事实的 review/score 后再跑完整 gate；如果主编复读认为语言或人物压力不够，直接整章回炉。116 则应按原路径重新规划，不能把超时当作已完成。

### 4. 已完成的验证

- `python -m pytest -q`：`44 passed`。
- `python engine/validate.py`：全部 souls 通过。
- `git diff --check`：通过。
- 042、054 的自定义 hardline 扫描结果为空；034、035 也经过同样的聚焦门禁。
- 已将上述改动提交并推送到 `origin/main`；当前 handoff 文档提交完成后，以 `git log -1` 和远端状态为准。

## 当前实测状态

最近一次 `python engine/batch_rewrite.py --status`（包含 061 的 prose lint 改善，但不代表严格 editorial 已通过）：

```text
stubs_total=607 stubs_remaining=194 stubs_missing=0 disease_or_lint_errors=331 error_files=331 unfinished_lint=331 hidden_duplicate_errors=298 alternate_error_files=0
```

最近一次全书 `python engine/prose_lint.py`（读取当前工作树，包含未接收的 061 改稿）：

```text
扫了 1331 章：0 章豁免，331 章退回(ERROR)，77 章有提醒(WARN)。
```

这意味着：

- agent 的流程和局部质量门禁已经可用，但全书仍不是绿灯，不能声称整本完成；最近的 061 也只是 prose lint 通过，仍未过 strict editorial。
- `hidden_duplicate_errors=298` 是需要优先处理的路径问题；不能只用 `_chapter_file(ch)` 找 canonical 文件。
- `stubs_remaining=194` 是 manifest 中尚未完整通过的候选计数，不等于所有候选都是字面上的九行 stub。
- 当前已经有主编验收的章节，但还没有完成整本逐章人类通读，也没有真实读者留存、追更、评论或晋江数据证据。
- 当前工作树有一个未接收的 Claude 改稿：`seasons/01-xianxia/chronicle/061-蒹葭.md`。在主编完成复读和 gate 之前，不要把它加入小说工作提交。

## 下一步执行队列

1. 先处理当前未接收改稿：复读 061，决定保留并补齐 metadata，或整章重写；确认它通过 prose、safety、strict editorial 和 hardline 扫描后，才允许提交。

2. 再确认状态和下一批精确目标：

   ```powershell
   python engine/batch_rewrite.py --status
   python engine/batch_rewrite.py --disease-only --pick 2 --dry-run
   python engine/batch_rewrite.py --disease-only --pick 2
   ```

3. 检查生成的 prompt 是否包含正确的 `TARGET_FILE`，再做 dispatch dry-run：

   ```powershell
   python engine/run_dispatch.py --chapters chNNN,chMMM --workers 2 --dry-run
   ```

4. 用高预算运行 Claude：

   ```powershell
   python engine/run_dispatch.py --chapters chNNN,chMMM --workers 2 --max-budget-usd 12.0 --effort high --timeout-sec 420
   ```

5. 主编独立读每个目标文件，并逐项执行：

   ```powershell
   python engine/prose_lint.py <target>
   python engine/safety_lint.py <target>
   python tools/review_batch.py --strict-editorial --file <target>
   ```

   另外要做 hardline / 模板回声扫描，确认没有把 Claude 的“解释型修补”留在成稿里。

6. 若 Claude 超时、阻断、只补 metadata、正文不足或仍有公式化表达，主编直接重写目标章节。主编结果写入对应的 `prompts/.results/chNNN.md` receipt，但不能覆盖 Claude 原始状态。

7. 每批完成后重新跑测试、validate、聚焦 gate 和全书状态；同步更新 `BATCH_REWRITE_STATUS.md` 与本交接文档，再只 stage 明确的目标文件，提交并推送。

8. 持续处理真实失败路径，直到机器错误显著收敛；随后进入连续章节的人类通读、人物线/伏笔线审计、开篇留存和读者反馈验证。没有这些证据，不把“模型评分高”写成“晋江爆款”。

## 不可退让的编辑底线

- 一次 Claude 任务只服务明确目标章节，不允许扫描整个仓库或擅自改写邻章。
- 正文要有具体动作、物件、关系压力和可追踪因果；避免 `方向朝着`、自我修补、墙式公式、重复的“那一 X”和“自己”回声。
- 正文目标至少 1500 个汉字；frontmatter 必须有基于正文事实的 `review` 和 `score`，score 至少 `12/14`；review 中的引用必须能在正文逐字找到。
- hook 必须在正文中以真实动作、选择或对话出现，不能只写在 metadata 里。
- 遵守安全边界，特别关注 `林窈`、`阿湄` 等未成年角色，不出现禁止的未成年亲密或自伤内容。
- 主编对最终文学质量负责；Claude 是执行者，不是最终裁判。

## 工作区注意事项

当前工作区存在此前留下的未跟踪产物。除非任务明确要求，不要顺手 stage 或删除它们，包括：

- `prompts/dispatch/*.txt` 和 `prompts/.results/` receipt；
- 根目录误留的 `chronicle/`；
- `_c639*`、临时脚本、计数文件、`.bak` 备份；
- `seasons/01-xianxia/chronicle/ch537-new.md`；
- `seasons/01-xianxia/chronicle/ch601-林崇看.md.bak`；
- `seasons/01-xianxia/chronicle/ch789-苏挽在.md.bak`。

提交时使用明确路径，例如本次只提交 `handoff.md`；不要用全量 `git add .`。

## 读者盲读 + 距离工具（r20 工作流，必跑节点）

> 项目级四层证据栈（S0 晋江官方 / S1 行业共识 / S2 工程启发式 / S3 真人读者）
> 的完整定义见 docs/standards/jinjiang-quality-architecture.md。本节是主编交接侧的复述。

> 这是项目级读者质量基线。5 读者交叉办法已经焊死在 canonical 工作流，不是附录。
> `effective_n = 0` / `L2 = 0` 的窗口期，"读者会追 / 爆款 / 上瘾"任何措辞一律禁止。

所有改稿必须按下面的顺序串起来：

1. **距离快照**（每次改稿后必跑）：
   - `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
   - 同步查看 `reports/jinjiang-r20/distance-summary.md`。这是当前工作树距离晋江爆款的诚实答案；
     在 `effective_n = 0` / `L2 = 0` 时，任何"接近爆款""读者会追""上瘾"类判断一律禁止。
2. **盲读包 + 五读者交叉协议**：
   - `py -3 -X utf8 tools/reader_panel_runner.py regenerate` 生成 4 包。
   - `py -3 -X utf8 tools/reader_subagent_driver.py verify` 检查交叉协议 5 份 L1 的 drop_chapter / love_relation / next_chapter_focus 是否各自 >= 4 个不同值。
   - `py -3 -X utf8 tools/reader_subagent_driver.py emit` 生成 5 份 persona prompt + 1 份 L2 真人 sub-agent prompt，每个 persona prompt 内嵌 isolation.persona_seed 和确定性 rotation。
   - 真人 sub-agent / 真人读者回填的 JSON 落 `reports/jinjiang-r20/reader-N.json` 后，再跑：
     - `py -3 -X utf8 tools/reader_panel_runner.py check`
     - `py -3 -X utf8 tools/reader_panel_runner.py aggregate`
3. **每批改稿必跑的门**（顺序固定，不允许跳过）：
   - `py -3 -X utf8 engine/prose_lint.py <目标章>`
   - `py -3 -X utf8 tools/review_batch.py --strict-editorial --file <目标章>`
   - 复跑第 1 步的距离工具，对比 bottom-list 与 gate 计数。
   - 复跑第 2 步的盲读聚合，把 effective_n / diversity_score / 升级项 diff 写入 `reports/jinjiang-r20/reader-blindtest-results.md` 的轮次对比段。
4. **不可越线的硬约束**（与 `docs/standards/晋江爆款基线.md` 一致）：
   - 工程分不替代真人分；真人分不替代工程分；任一低于 7.0 禁止聚合判断。
   - `L2 = 0` 时，禁止在 README / 报告 / 群里使用"读者会追 / 爆款 / 上瘾"。
   - L1 unanimous 在 `echo_panel = True` 时不构成多人共识。
   - `engine/prose_lint.py` 是地板，通过不等于合格；`tools/chapter_by_chapter_audit.py` 是初筛；`tools/jinjiang_rubric.py` 是工程 5 维；`tools/reader_panel_runner.py` 是真人 5 维；四道门按序串行。

具体执行命令、协议细节和失败模式见：
- `docs/standards/jinjiang-blowup-baseline-operator.md`
- `docs/standards/晋江爆款基线.md`
- `docs/reader-subagent-workflow.md`
- `docs/standards/novel-workflow.md` 末尾"5 读者交叉 + 真人 sub-agent 工作流（必跑节点）"段（verify / emit / aggregate 三步必须出现在改稿循环）

提交规范保持不变：每批只 stage 明确的目标文件，不要 `git add .`。


## 编辑端 5 模式 + 工艺 5 条（2026-09-04 焊入，与上面四层证据栈 + 5 读者交叉并列硬约束）

> 主流程新增的两个**编辑端**硬约束：每个 chapter md 写之前必须先回答「5 模式（M1–M5）」中的哪几条、哪几条踩禁；每个 chapter md 改稿时必须按「工艺 5 条」的具体动作执行。
>
> 这是 `novel-workflow.md` 末尾「5 读者交叉 + 真人 sub-agent 工作流」的**同伴节点**，不是替代。
>
> 详见：
> - `docs/standards/jinjiang-edit-modes.md` —— M1–M5 的诊断层 + 改稿操作表 §8
> - `docs/standards/novel-workflow.md` 末尾「改稿工艺 5 条硬规则」段 —— 改稿工艺层
> - `docs/standards/5-reader-cross-workflow.md` —— 5 读者交叉协议的完整定义
> - `reports/jinjiang-r20/sub-agent-cross-pollination-2026-09-04.md` —— sub-agent A 直读发现的 5 条工艺红旗出处

### 与上一节「读者盲读 + 距离工具」的固定顺序

诊断（reader_panel_runner + chapter_distance） → 诊断（M1–M5 哪条失败） → 操作（工艺 5 条） → 验证（重跑 reader_panel_runner + chapter_distance）。任一环跳过 = 改稿循环不闭环。

---

## 磨斧头阶段检查表（2026-09-04，本会话）

> 本节是「编辑端 5 模式 + 工艺 5 条」段的**同伴节点**，不是替代。
> 触发：用户原话「先暂停。我们先研究一下怎么样子架构 architect, 磨斧头。
> 我们怎么才能知道什么是晋江高分标准，规范，和文笔，编辑悬念等等。
> 把研究好的新思路，焊死进 repo 里面，然后我们再继续。」

### 改稿循环必跑的 4 道门（顺序固定，不允许跳过）

每改一章必跑：
1. `py -3 -X utf8 tools/jinjiang_chapter_distance.py <file>` — E1-E5 工程 5 维 + E_min。
2. `py -3 -X utf8 tools/review_batch.py --strict-editorial --file <file>` — M1-M5 编辑端校验。
3. `py -3 -X utf8 engine/prose_lint.py <file>` — 6 道墙 + 未来 JJ-LINT-01-07。
4. `py -3 -X utf8 tools/chapter_by_chapter_audit.py --chapter <ch>` — hook_signal / binge_score / issue tag。

每批改稿后必跑：
5. `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
6. `py -3 -X utf8 tools/refresh_distance_summary.py`
7. `py -3 -X utf8 tools/reader_panel_runner.py check`
8. `py -3 -X utf8 tools/reader_panel_runner.py aggregate`

任一 ERROR / 任一 stale / 任一复读嫌疑 = 不准 commit。

### 5 读者交叉必跑的 3 步（顺序固定）

每批改稿前：
- `py -3 -X utf8 tools/reader_subagent_driver.py verify` — 5 份 L1 三轴必须各自 >= 4 个不同值。
- `py -3 -X utf8 tools/reader_subagent_driver.py emit` — 生成 5 份 persona prompt + 1 份 L2 真人 sub-agent prompt。

真人 sub-agent / 真人读者落 JSON 后：
- `py -3 -X utf8 tools/reader_panel_runner.py check` — schema_version=2 + model_id + reading_log + pack_hash + isolation 双证据，缺一项 = 降级 L1。

### 文档自检表（每章必查）

| 文档 | 必须存在的关键字 | 检查方法 |
|---|---|---|
| `docs/standards/novel-workflow.md` | 含「磨斧头阶段焊死段」+「JJ-LINT-01-07」+「M1-M5 vs E1-E5」 | `grep -c 磨斧头阶段焊死段` 应 >= 1 |
| `docs/standards/5-reader-cross-workflow.md` | 含「drop_chapter / love_relation / next_chapter_focus 三轴」+「effective_n >= 3」+「L2 >= 1」 | `grep -c 复读嫌疑` 应 >= 1 |
| `docs/standards/jinjiang-quality-architecture.md` | 含「四层证据栈 S0-S3」+「effective_n = 0」+「>= 14 天」 | `grep -c pack_hash drift` 应 >= 1 |
| `docs/standards/jinjiang-blowup-baseline-operator.md` | 含「lint + audit + distance + review_batch」+「E1-E5 互为校验」 | `grep -c distance 重跑` 应 >= 1 |
| `docs/standards/jinjiang-edit-modes.md` | 含「M1 开场钩 / M3 章尾钩 / M5 关系后果」+「禁用」清单 | `grep -c 改稿操作表` 应 >= 1 |
| `docs/standards/晋江爆款基线.md` | 含「工程 5 维 + 真人 5 维」+「禁区 1-8」+「上瘾单元」 | `grep -c 双轨打分` 应 >= 1 |
| `handoff.md`（本文件） | 含「读者盲读 + 距离工具」+「5 模式 + 工艺 5 条」+「磨斧头检查表」 | `grep -c 磨斧头阶段检查表` 应 >= 1 |
| `reports/jinjiang-r20/distance-summary.md` | 含「197 publish-eligible」+「1 ch775 at 9.0」+「L2 = 0」 | 必须由 `refresh_distance_summary.py` 生成，不准手写 |
| `reports/jinjiang-r20/reader-blindtest-results.md` | 含「effective_n」+「diversity_score」+「echo_panel」+「L2 = 0」 | 同上 |
| `reports/jinjiang-r20/磨斧头研究-2026-09-04.md` | 含「S0/S1/S2/S3」+「JJ-LINT-01-07」+「不允许的省略」 | 新增留底 |
| `reports/jinjiang-r20/sub-agent-cross-pollination-2026-09-04.md` | 含「sub-agent A」+「sub-agent B / C」+「同点 >= 3」 | 既有 |

### 工艺 / 编辑 5 维（M1-M5）vs 工程 5 维（E1-E5） vs 真人 5 维（R1-R5）自检

- M1 开场钩 <-> E1 开场冲突 <-> R1 跨题材可读：1:1 已焊。
- M2 中段选择 <-> E2 中段选择 <-> R2 钩兑现：1:1 已焊，缺「下一章是否兑现」跨章。
- M3 章尾钩 <-> E3 章尾钩 <-> R3 关系后果兑现：1:1 + 缺 E6 钩子类型枚举 + 缺跨章兑现。
- M4 POV 主动 <-> E4 POV 主动 <-> R4 主动选择：1:1 已焊。
- M5 关系后果 <-> E5 关系后果 <-> R5 不踩禁区：1:1 + 缺 POV 主动发起方识别 + 缺禁区 9。

任一缺位 = 下批 batch 13 起施工对象。

### 不可越线的边界（汇总）

- 工程 7.0 != 爆款，工程 9.8 也不是市场分。
- L1 unanimous 在 echo_panel = True 时**不**构成多人共识。
- L2 = 0 时，禁止在 README / 报告 / 群里使用「读者会追 / 爆款 / 上瘾 / 读者确认」。
- 真人 sub-agent / 真人读者的 isolation 双证据必须机器可校验，不是自报。
- 不把 sub-agent 模拟的内部数字（不是它报的章号 / 关系 / 钩子）当成事实；事实以可重跑核数为准。
- pack_hash = f64e35b7cac0c896 是当前基线；动 `reader_blindtest_pack.py` 必须显式告诉用户漂移。
- 不改 chapter md 的 review / score 字段（已写好的 12/14 是诚实判断，不准为了提分而改）。
- 不改 reader JSON 已写好的 drop / love_relation / next_chapter_focus 字段。
- 一次只 stage 明确的目标文件，不要 `git add .`。

### 与上一节「编辑端 5 模式 + 工艺 5 条」的接驳

诊断（reader_panel_runner + chapter_distance） → 诊断（M1-M5 哪条失败） → 操作（工艺 5 条） → 验证（重跑 reader_panel_runner + chapter_distance） → 自检（本检查表）→ commit。任一环跳过 = 改稿循环不闭环。

### 维护纪律

- 改本检查表任一条 -> 必须同步改 `docs/standards/novel-workflow.md` 末尾「磨斧头阶段焊死段」段。
- 改 JJ-LINT 任意一条 -> 必须先在 `reports/jinjiang-r20/磨斧头研究-2026-09-04.md` 第 4.2 节登记，再写 lint。
- 派 B / C sub-agent -> 必须先在 `reports/jinjiang-r20/sub-agent-cross-pollination-2026-09-04.md` 第 2 节追加完成状态。
- L2 真人 sub-agent >= 1 份落盘 -> 必须更新本检查表「S3 真人读者」行 + 文档自检表 + 对外口径。
