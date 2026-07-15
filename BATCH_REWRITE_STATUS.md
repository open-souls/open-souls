# Batch Rewrite Status

Run `python engine/batch_rewrite.py --status` to refresh.

**Total scope**: 876 chapters to bring to gold standard
- 244 §七.1 disease chapters (have real prose, just broken)
- 632 stub chapters (9-line templates, need full write)

**Per session budget** (12 parallel subagents × ~30 min each):
- ~96 chapters / session
- ~9 sessions to complete

## Workflow

1. **范文章 ready**: ch512-不接.md (苏挽 POV, 行为先于意识)
2. **Picker**: `python engine/batch_rewrite.py --pick N` chooses N targets (stubs first, then disease)
3. **Dispatch**: `python engine/batch_rewrite.py --pick N --no-skip-done --no-dry-run` writes dispatch prompts to `prompts/dispatch/ch###.txt`
4. **Run**: Each dispatch prompt is a complete brief for a subagent. Hand them to subagents via `delegate_task` or LOOP.md cron.

## Subagent Output Format

Each subagent writes:
- The chapter file itself
- `prompts/.results/ch###.md` with PASS/FAIL + lint + score + gates

A chapter counts as DONE iff:
- File size ≥ 1500 bytes (no longer a stub)
- `python engine/prose_lint.py <file>` returns 0 ERROR

## What I Did in This Session (2026-07-15)

范文章:
- [x] ch512-不接.md — 苏挽 POV 治本范文 (PASS lint, 4780 bytes)

Disease章 治本 (chunks dispatched, awaiting results):
- [ ] ch582-位置.md (阿湄 POV 糖玉场景)
- [ ] ch700-清梧回.md (余伯 POV 翻回 ch085)
- [ ] ch998-真合前夜.md (林夙 POV 阿湄的信 第三行)
- [ ] ch999-真合前拂晓.md (阿湄 POV 宿州走 7 天)

Stub 重写 (chunks dispatched, awaiting results):
- [ ] ch858-林彻站.md
- [ ] ch859-苏挽在.md
- [ ] ch860-林叙看.md
- [ ] ch863-苏挽端糖.md
- [ ] ch864-林彻看林夙.md
- [ ] ch867-灶边雪.md

**Remaining after this batch**: ~866 chapters

## How to Continue (Next Session)

```bash
# 1. See what's still failing
python engine/prose_lint.py 2>&1 | grep "✗" | wc -l

# 2. Pick next batch
python engine/batch_rewrite.py --pick 12  # stubs first

# 3. Dispatch to subagents (use the generated prompts in prompts/dispatch/)
ls prompts/dispatch/  # shows N ready-to-go dispatch prompts

# 4. After all subagents finish, verify:
python engine/batch_rewrite.py --status
```

## Critical: Do NOT Use `--no-skip-done` Carelessly

The dispatcher skips chapters already at gold (PASS lint). To re-rewrite a passing chapter:
- Delete `prompts/.results/ch###.md` (forces subagent to redo)
- Or pass `--chapters ch###,ch###` explicitly