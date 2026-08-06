# Open Souls 小说 Agent 交接

> 更新时间：2026-08-04
> 工作目录：`C:\Users\stanc\github\open-souls`
> 当前分支：`main`
> 本文档对应的上一份工作提交：`d1af5c6`（`editor: pass chapters 042 and 054`）

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

### 3. 已完成的验证

- `python -m pytest -q`：`44 passed`。
- `python engine/validate.py`：全部 souls 通过。
- `git diff --check`：通过。
- 042、054 的自定义 hardline 扫描结果为空；034、035 也经过同样的聚焦门禁。
- 已将上述改动提交并推送到 `origin/main`；当前 handoff 文档提交完成后，以 `git log -1` 和远端状态为准。

## 当前实测状态

最近一次 `python engine/batch_rewrite.py --status`：

```text
stubs_total=607 stubs_remaining=194 stubs_missing=0 disease_or_lint_errors=332 error_files=332 unfinished_lint=332 hidden_duplicate_errors=298 alternate_error_files=0
```

最近一次全书 `python engine/prose_lint.py`：

```text
扫了 1331 章：0 章豁免，332 章退回(ERROR)，77 章有提醒(WARN)。
```

这意味着：

- agent 的流程和局部质量门禁已经可用，但全书仍不是绿灯，不能声称整本完成。
- `hidden_duplicate_errors=298` 是需要优先处理的路径问题；不能只用 `_chapter_file(ch)` 找 canonical 文件。
- `stubs_remaining=194` 是 manifest 中尚未完整通过的候选计数，不等于所有候选都是字面上的九行 stub。
- 当前已经有主编验收的章节，但还没有完成整本逐章人类通读，也没有真实读者留存、追更、评论或晋江数据证据。

## 下一步执行队列

1. 先确认状态和下一批精确目标：

   ```powershell
   python engine/batch_rewrite.py --status
   python engine/batch_rewrite.py --disease-only --pick 2 --dry-run
   python engine/batch_rewrite.py --disease-only --pick 2
   ```

2. 检查生成的 prompt 是否包含正确的 `TARGET_FILE`，再做 dispatch dry-run：

   ```powershell
   python engine/run_dispatch.py --chapters chNNN,chMMM --workers 2 --dry-run
   ```

3. 用高预算运行 Claude：

   ```powershell
   python engine/run_dispatch.py --chapters chNNN,chMMM --workers 2 --max-budget-usd 12.0 --effort high --timeout-sec 420
   ```

4. 主编独立读每个目标文件，并逐项执行：

   ```powershell
   python engine/prose_lint.py <target>
   python engine/safety_lint.py <target>
   python tools/review_batch.py --strict-editorial --file <target>
   ```

   另外要做 hardline / 模板回声扫描，确认没有把 Claude 的“解释型修补”留在成稿里。

5. 若 Claude 超时、阻断、只补 metadata、正文不足或仍有公式化表达，主编直接重写目标章节。主编结果写入对应的 `prompts/.results/chNNN.md` receipt，但不能覆盖 Claude 原始状态。

6. 每批完成后重新跑测试、validate、聚焦 gate 和全书状态；同步更新 `BATCH_REWRITE_STATUS.md` 与本交接文档，再只 stage 明确的目标文件，提交并推送。

7. 持续处理真实失败路径，直到机器错误显著收敛；随后进入连续章节的人类通读、人物线/伏笔线审计、开篇留存和读者反馈验证。没有这些证据，不把“模型评分高”写成“晋江爆款”。

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
