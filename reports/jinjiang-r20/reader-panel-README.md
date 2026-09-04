# reader panel 历史文件说明

> 这些 `reader-*.json` 文件是在 `tools/reader_panel_runner.py` 的 `isolation` /
> `schema_version` 校验落地之前生成的。它们当前都因 `isolation.no_chronicle = false`
> / `schema_version < 2` 被 runner **降级为 L1**——这正是它们应该被标记的状态。

## 为什么不删除？

- 它们是历史决策的实物证据，与 `reports/jinjiang-r20/reader-blindtest-results.md` 一起保留。
- 删除会破坏轮次对比的可追溯性。
- 任何把它们当 L2 计入新汇总的行为都会被 `reader_panel_runner.py` 自动拒绝。

## 下一轮要补什么？

要拿到 ≥1 份有效 L2，必须：

1. 在独立 fork 会话里运行 `py -3 -X utf8 tools/reader_panel_runner.py emit-prompt <persona_id>` 生成 persona prompt；
2. sub-agent 在 isolation cwd 里只读盲读包，写出 schema_version=2 的 JSON；
3. 主会话落盘到 `reader-<n>-真人-<persona>.json`，runner 会校验并把它升入 L2。

详见：`docs/reader-subagent-workflow.md §5`。
