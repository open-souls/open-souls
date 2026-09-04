# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-04 (post hook-signal refresh)
> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py
> Range: 1145 contiguous chapters
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (see section 3).
> This report only measures the engineering side distance.

## 1. One-line answer

Of 1145 chapters, only **8 (0.7%)** clear the engineering 8.5 blowup line. **10** chapters have any reader-blindtest signal that can layer onto R-track. The other 1135 chapters cannot be claimed as blowup or addictive by any means available right now.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 262 | 22.9% | clearly needs rewrite (structural) |
| 5-6.99 | 477 | 41.7% | needs choice or action |
| 7-7.99 | 300 | 26.2% | near entry, fix one dim |
| 8-8.49 | 98 | 8.6% | publish-ready single-chapter |
| >=8.5 | 8 | 0.7% | blowup-engineered single-chapter |

Average E_min: **5.82/10**. This is the engineering floor; do not cite it as 接近爆款.

## 3. Per-dimension fail counts (E_dim < 7.0)

After the 2026-09-04 hook-signal refresh, the failing-chapter counts are:

| dim | failing chapters | meaning |
|---|---:|---|
| E1 opening conflict | 29 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 307 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 106 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 600 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 310 | named characters are present but no relationship moves |

Compared to the 2026-09-04 phase-1 snapshot: E3 fell from 526 -> 106 after the hook-signal refresh in tools/chapter_by_chapter_audit.py. The previous count was inflated by a keyword-only detector that did not recognise question marks, future-intent verbs, or noun-phrase closing beats (e.g. ch506 刀柄方向拉长一寸). E4 remains the dominant single-dimension failure.

## 4. Reader blindtest layer (R-track)

- Current coverage: **10 chapters** indexed by reader JSONs (drop or next_chapter_focus).
- All coverage is from historical reader-*.json files. There are 0 L2 真人 sub-agent entries.
- tools/reader_panel_runner.py check currently: L2-real=0, L2-reader=0, L1=6, effective_n=0.
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 5. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 406 | 0 | reader evidence missing |
| blowup chapter (min>=8.5) | 8 | 0 | same |
| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |

## 6. Bottom 15 chapters by E_min (next-round rewrite candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 14 | 4 | 10 | 6 | 4 | 4 | 5 | seasons/01-xianxia/chronicle/014-压四天.md |
| 15 | 4 | 7 | 10 | 4 | 7 | 7 | seasons/01-xianxia/chronicle/015-代签.md |
| 16 | 4 | 10 | 6 | 4 | 4 | 4 | seasons/01-xianxia/chronicle/016-云栀井台.md |
| 20 | 4 | 10 | 6 | 4 | 4 | 4 | seasons/01-xianxia/chronicle/020-街中一眼.md |
| 25 | 4 | 10 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/025-破封.md |
| 37 | 4 | 7 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/037-报名.md |
| 45 | 4 | 7 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/045-闭眼靠手.md |
| 46 | 4 | 10 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/046-取药日.md |
| 49 | 4 | 10 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/049-旧路.md |
| 50 | 4 | 10 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/050-第二人.md |
| 52 | 4 | 10 | 6 | 4 | 6 | 7 | seasons/01-xianxia/chronicle/052-抽页.md |
| 55 | 4 | 7 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/055-叶观澜看.md |
| 58 | 4 | 10 | 6 | 10 | 4 | 5 | seasons/01-xianxia/chronicle/058-旧档.md |
| 64 | 4 | 10 | 6 | 10 | 4 | 4 | seasons/01-xianxia/chronicle/064-一触.md |
| 66 | 4 | 10 | 6 | 10 | 4 | 5 | seasons/01-xianxia/chronicle/066-旧派.md |

## 7. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 291 | 9 | 10 | 10 | 10 | 10 | 9 | seasons/01-xianxia/chronicle/291-升堂.md |
| 605 | 9 | 10 | 10 | 10 | 10 | 9 | seasons/01-xianxia/chronicle/605-水落.md |
| 653 | 9 | 10 | 10 | 10 | 10 | 9 | seasons/01-xianxia/chronicle/653-新痕.md |
| 755 | 9 | 10 | 10 | 10 | 9 | 9 | seasons/01-xianxia/chronicle/755-半个真相.md |
| 761 | 9 | 10 | 10 | 10 | 10 | 9 | seasons/01-xianxia/chronicle/761-林窈不哭.md |
| 775 | 9 | 10 | 10 | 10 | 10 | 9 | seasons/01-xianxia/chronicle/775-林叙看.md |
| 792 | 9 | 10 | 10 | 10 | 9 | 9 | seasons/01-xianxia/chronicle/792-苏挽在.md |
| 1046 | 9 | 10 | 10 | 10 | 10 | 9 | seasons/01-xianxia/chronicle/1046-灶边.md |
| 116 | 8 | 10 | 10 | 10 | 10 | 8 | seasons/01-xianxia/chronicle/116-监守.md |
| 121 | 8 | 10 | 10 | 10 | 9 | 8 | seasons/01-xianxia/chronicle/121-压定.md |

## 8. Rewrite path (driven by section 5 weakness)

1. First fill R-track: tools/reader_subagent_driver.py emit + 真人 sub-agent run, 5 personas with isolation evidence -> effective_n >= 3 AND diversity >= 0.5 before any aggregate judgement.
2. Then fix E4 (POV agency) for 600 chapters: at least 2 agency verbs per chapter (决定 / 改为 / 不再 / 签下).
3. Then fix E2 (mid-turn choice) for 307 chapters: the mid section must contain a real POV choice with a cost.
4. Then fix E5 (relationship cost) for 310 chapters: at least one named-pair relationship must visibly move each chapter.
5. Last fix E3 (ending hook) for 106 chapters: every chapter ending must add a concrete question the next chapter must answer, ban 她没回 / 明日再看 / pure mood. (E3 used to be the dominant failure but the hook-signal refresh brought it down from 526 to 106; the remaining 106 are genuinely weak endings.)
6. After every 3-chapter rewrite batch: run tools/reader_panel_runner.py check + aggregate and tools/jinjiang_chapter_distance.py --out, diff against this snapshot.

## 9. Forbidden shortcuts

- Do NOT cite this snapshot E_min average 5.82/10 as 接近爆款. It is an engineering floor, not a market score.
- Do NOT treat the 10-chapter R-track coverage as a substitute for 1145-chapter blindtest. It is just historical JSON indexing.
- Do NOT skip E3 / E4 fixes during the L2=0 window. With R-track missing, the engineering weakness is the only fixable evidence.
- Do NOT cite the post-refresh E3 drop (526 -> 106) as a real quality gain. It only reflects the diagnostic becoming honest; the underlying text did not change.
