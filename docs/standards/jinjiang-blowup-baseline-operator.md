# Jinjiang blowup baseline - operator manual

> Purpose: turn docs/standards/jinjiang-blowup-baseline.md into something you can actually run. This doc is the single entry point for the per-chapter rewrite loop and the reader-panel loop.

> Scope: season 1 only. New seasons must re-run both loops before claiming any quality.

## 0. The two loops (always paired)

    chapter md  ->  [prose_lint + audit + rubric + chapter_distance]  ->  E1..E5
                                                                          |
                                                                          v
                  [5 L1 + 1 L2 sub-agent, check + aggregate]       R1..R5
                                                                          |
                                                                          v
                  edit-decision-protocol section 3 (rewrite order)

You never run one loop without the other. Engineering alone does not give you reader evidence. Reader alone does not give you prose that does not break.

## 1. Per-chapter single shot

    py -3 -X utf8 tools/jinjiang_chapter_distance.py path/to/chapter.md

Returns:

| field | meaning |
|---|---|
| E1..E5 | the five engineering dimensions, 0-10 each |
| engineering_min | the lowest dim. Below 7 means this chapter does not enter the blindtest pool |
| R1..R5 | null until reader JSONs cover this chapter |
| reader_min | null until reader evidence exists |
| gates.publish / blowup_chapter / addictive_chapter | three concrete pass/fail flags |

If you only have one chapter in hand and no reader JSON covers it, this is the honest answer: it tells you what engineering dimension to fix, and warns you that no reader signal exists yet.

## 2. Bulk corpus snapshot

    py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json

Generates one record per chapter (1145 today). The companion markdown is reports/jinjiang-r20/distance-summary.md. This is the canonical answer for how far we are from blowup, in the current worktree. It is regenerated every time you want a fresh diff, never written by hand.

## 3. Reader loop

### 3.1 Five persona panel (L1)

    py -3 -X utf8 tools/reader_panel_runner.py regenerate
    py -3 -X utf8 tools/reader_panel_runner.py emit-prompt 1
    py -3 -X utf8 tools/reader_panel_runner.py emit-prompt 2
    py -3 -X utf8 tools/reader_panel_runner.py emit-prompt 3
    py -3 -X utf8 tools/reader_panel_runner.py emit-prompt 4
    py -3 -X utf8 tools/reader_panel_runner.py emit-prompt 5

Each emit-prompt writes reports/jinjiang-r20/reader-prompt-N.txt containing the persona, keep_if / drop_if / must_disagree_with hard constraints, and the isolation protocol. The five prompts are designed to be handed to five independent LLM calls (or five real human readers).

### 3.2 真人 sub-agent / 真人读者 (L2)

The L1 prompts above will produce L1 JSONs. To count as L2, a JSON must satisfy:

1. source starts with 真人读者 or 真人 sub-agent.
2. schema_version equals 2.
3. model_id, reading_log, pack_hash are all present (provenance keys).
4. isolation.no_chronicle is true AND isolation.no_frontmatter is true.
5. isolation.cwd and isolation.persona_seed are filled with the actual run path.

If any of these is missing, tools/reader_panel_runner.py check will downgrade the file to L1 and print the downgrade reason. Files that fail this gate are visible in reports/jinjiang-r20/reader-blindtest-results.md.

### 3.3 Aggregate

    py -3 -X utf8 tools/reader_panel_runner.py check
    py -3 -X utf8 tools/reader_panel_runner.py aggregate

Outputs reports/jinjiang-r20/reader-blindtest-results.md with effective_n, diversity_score, echo_panel, and per-signal counts.

Hard rules from the aggregate output:

| output value | meaning |
|---|---|
| effective_n >= 3 | upgrade judgments allowed |
| echo_panel = True | L1 unanimous findings are复读嫌疑, downgraded |
| L2 = 0 | 爆款 / 上瘾 / 读者会追 claims are FORBIDDEN |

## 4. Edit decision matrix

After running both loops, feed the results into reports/jinjiang-r20/edit-decision-protocol.md section 3:

1. Short chapters: add a choice, resistance, cost, or new information. Do not add empty scenery.
2. Weak endings: add a concrete question the next chapter must answer. Do not add a vague metaphor.
3. Repeated sentences: delete the whole sentence. Do not paraphrase.
4. Filler paragraphs: delete the whole paragraph. Do not soften.
5. Opening sentences too uniform: redo the first sentence. Do not disturb the mid section.

Do not pick a chapter to rewrite unless both E_min and R_min (when available) tell you which dimension is failing.

## 5. Cross-pollination rule (the 5 readers cross protocol)

L1 is not allowed to be 5 copies of one prompt. The runner enforces this:

- Each L1 JSON must reference a different isolation.persona_seed.
- The runner diversity_score reports flag / drop / reason Jaccard. Any axis below the floor (flag < 0.5, drop < 0.4, reason < 0.4) flips echo_panel to True.
- When echo_panel is True, L1 unanimous findings do not count toward upgrade thresholds.

If your five L1s read identical, you have复读嫌疑, not five readers. Re-issue each L1 against a different persona seed and different reading order.

## 6. Promotion gate (L2 sample size)

A chapter-by-chapter judgment of the form this chapter is 爆款 requires:

1. E_min >= 8.5 for at least 3 consecutive chapters (blowup chapter).
2. R_min >= 7.5 for at least 5 consecutive chapters, and at least 2 L2 真人 readers confirming.
3. effective_n >= 3 with diversity_score >= 0.5.

Anything weaker is recorded as a direction, not a judgment. The distance-summary.md report always prints the gate counts side-by-side with this requirement.

## 7. Forbidden shortcuts

- Engineering score alone is not a market score.
- L1 unanimous findings are not multi-reader consensus when echo_panel = True.
- The filename reader-N-真人.json is not evidence; only source + isolation together are.
- avg_binge_score 9.97 from chapter-by-chapter-audit.py is mechanical and does not mean 读者 will追.
- avg_engineering 5.09 from distance-summary.md is an engineering floor; saying it is close to 爆款 is a forbidden shortcut.

## 8. The five reader cross-pollination protocol

This is the protocol the user asked for. Five L1 personas read the same four packs but each holds a different keep_if / drop_if / must_disagree_with triple, and is asked to cite a different concrete chapter + line. They never share a reading order.

| axis | enforcement |
|---|---|
| keep_if | persona 1: 角色做选择且付代价 / persona 2: 每章有下一章必答的问题 / persona 3: 不靠术语也能看懂 60% / persona 4: POV 主动决定并承担身份后果 / persona 5: 出现一次让人心里疼过的关系动作 |
| drop_if | per persona, must name a different chapter and pack |
| next_chapter_focus | must name a different chapter per persona |
| love_relation | must name a different relationship per persona |
| isolation.persona_seed | must be unique per JSON |
| model_id | each L1 records its own |

If two personas produce the same drop chapter, the runner flags them as复读嫌疑 and downgrades. This is the mechanical part of the cross-pollination.

## 9. Sub-agent runner

tools/reader_subagent_driver.py IS now the orchestrator. Three subcommands:

1. verify: locks the cross-pollination invariants in code (drop_chapter, love_relation, next_chapter_focus must each rotate to >= 4 distinct values across the five personas).
2. emit: writes isolated persona packs into reports/jinjiang-r20/isolated-reader-packs/persona-N/, produces five reader-prompt-N.txt plus one reader-prompt-real.txt. Each persona prompt embeds a unique isolation.persona_seed and deterministic rotation of drop_chapter, drop_pack, love_relation, next_chapter_focus.
3. aggregate: proxies to tools/reader_panel_runner.py {check, aggregate}.

The driver is model-agnostic. It does NOT spawn a sub-agent on its own. The host Codex session hands each prompt to a 真人 sub-agent (or a real reader). Until that happens, the panel shows L2 = 0 and 爆款 / 上瘾 / 读者会追 judgments are FORBIDDEN.

## 10. Failure-dimension to rewrite-action table

tools/jinjiang_chapter_distance.py already tells you which E dimension is below 7.0. This table is the bridge from diagnosis to specific edits. It is the only place we have locked the engineering rewrite recipes; the reader loop must run before AND after applying any of these.

| E dim | symptom | what to add or delete | what NEVER to do |
|---|---|---|---|
| E1 opening conflict | first 180 chars lack >= 2 action verbs or no resistance word | add a concrete action in the opening sentence; add a resistance word (却 / 但 / 没有 / 拦) in the same paragraph | do not add scenery or backstory in the opening line |
| E2 mid-turn choice | mid section has no decision verb | insert one mid-section choice with cost (决定 / 改为 / 不再 / 签下); the choice must change at least one named relationship | do not paraphrase a previous choice |
| E3 ending hook | audit hook_signal false; ending ends on mood | rewrite the last 1-2 sentences so they stop on action, identity slip, unanswered question or new evidence (忽然 / 却 / 没[有再] / 门外 / 脚步 / 声音 / 信 / 敲) | do not replace the hook with a metaphor or summary line (屋里很安静 / 明日再看) |
| E4 POV agency | less than 2 decision verbs in the whole body | insert 2+ agency verbs (决定 / 改为 / 不再 / 签下 / 主动) spoken or acted by the POV character | do not attribute agency to narrator commentary |
| E5 relationship cost | named characters present but no relationship move | show one named pair visibly shifting; the move must be observable in a single sentence | do not list cast in frontmatter and call it a relationship move |

For each rewrite, the runtime check is exactly:

`
py -3 -X utf8 engine/prose_lint.py <目标章>
py -3 -X utf8 tools/review_batch.py --strict-editorial --file <目标章>
py -3 -X utf8 tools/jinjiang_chapter_distance.py <目标章>
`

If a chapter fails one of these after the rewrite, do NOT raise the engineering score by lowering the audit threshold. Re-edit.

## 11. Cross-chapter rewrite cadence

1. Pick the bottom 3 chapters from reports/jinjiang-r20/distance-summary.md section 5.
2. For each, decide which E dim to fix (the distance output already names it).
3. Edit ONLY the failing dim per the table in section 10. Do not reflow other dims.
4. Run the per-chapter runtime check listed above.
5. Run py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json and py -3 -X utf8 tools/reader_panel_runner.py aggregate.
6. Commit and push. The push gate (tools/validate_changed.py) only escalates when chapter files changed, so infrastructure commits can land without retesting every chapter.
