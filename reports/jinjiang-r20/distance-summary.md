# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-04
> Source: tools/jinjiang_chapter_distance.py
> Range: 1145 contiguous chapters
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (see section 3).
> This report only measures the engineering side distance.

## 1. One-line answer

Of 1145 chapters, only **7 (0.6%)** clear the engineering 8.5 blowup line. **10 chapters** have any reader-blindtest signal that can layer onto R-track. The other 1135 chapters cannot be claimed as blowup or addictive by any means available right now.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 626 | 54.7% | clearly needs rewrite (structural) |
| 5-5.99 | 114 | 10.0% | needs choice or action |
| 6-6.99 | 152 | 13.3% | near entry |
| 7-7.99 | 187 | 16.3% | past publish floor, not yet blowup |
| 8-8.49 | 59 | 5.2% | close to blowup line |
| 8.5+ | 7 | 0.6% | above blowup line |

**Per-dimension weakness (E_dim < 7 means the chapter cannot enter the blindtest pool)**:

| dim | fail chapters | main symptom |
|---|---:|---|
| E1 opening conflict | 29 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 307 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 526 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 600 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 310 | named characters are present but no relationship moves |

## 3. Reader blindtest layer (R-track)

- Current coverage: **10 chapters** indexed by reader JSONs (drop or next_chapter_focus).
- All coverage is from historical reader-*.json files. There are 0 L2 真人 sub-agent entries.
- tools/reader_panel_runner.py check currently: L2-real=0, L2-reader=0, L1=6, effective_n=0.
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 4. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 253 | 0 | reader evidence missing |
| blowup chapter (min>=8.5) | 7 | 0 | same |
| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |

## 5. Bottom 15 chapters by E_min (next-round rewrite candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 4 | 10 | 10 | 4 | 10 | 7 | seasons\01-xianxia\chronicle\001-退婚书.md |
| 2 | 4 | 7 | 10 | 4 | 9 | 6 | seasons\01-xianxia\chronicle\002-叫对人.md |
| 3 | 4 | 10 | 10 | 4 | 10 | 7 | seasons\01-xianxia\chronicle\003-三年一碗.md |
| 5 | 4 | 10 | 10 | 4 | 10 | 7 | seasons\01-xianxia\chronicle\005-两清.md |
| 7 | 4 | 10 | 10 | 4 | 7 | 6 | seasons\01-xianxia\chronicle\007-林崇称量.md |
| 9 | 4 | 7 | 6 | 4 | 5 | 7 | seasons\01-xianxia\chronicle\009-林彻磨局.md |
| 10 | 4 | 10 | 10 | 4 | 10 | 7 | seasons\01-xianxia\chronicle\010-赤渊茶凉.md |
| 11 | 4 | 10 | 10 | 4 | 5 | 7 | seasons\01-xianxia\chronicle\011-藕荷衣.md |
| 14 | 4 | 10 | 6 | 4 | 4 | 5 | seasons\01-xianxia\chronicle\014-压四天.md |
| 15 | 4 | 7 | 10 | 4 | 7 | 7 | seasons\01-xianxia\chronicle\015-代签.md |
| 16 | 4 | 10 | 6 | 4 | 4 | 4 | seasons\01-xianxia\chronicle\016-云栀井台.md |
| 17 | 4 | 10 | 10 | 4 | 5 | 8 | seasons\01-xianxia\chronicle\017-露底.md |
| 18 | 4 | 10 | 10 | 4 | 8 | 6 | seasons\01-xianxia\chronicle\018-余伯案头.md |
| 19 | 4 | 10 | 10 | 4 | 6 | 7 | seasons\01-xianxia\chronicle\019-被举.md |
| 20 | 4 | 10 | 6 | 4 | 4 | 4 | seasons\01-xianxia\chronicle\020-街中一眼.md |

## 6. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1046 | 9 | 10 | 10 | 10 | 10 | 9 | seasons\01-xianxia\chronicle\1046-灶边.md |
| 291 | 9 | 10 | 10 | 10 | 10 | 9 | seasons\01-xianxia\chronicle\291-升堂.md |
| 653 | 9 | 10 | 10 | 10 | 10 | 9 | seasons\01-xianxia\chronicle\653-新痕.md |
| 755 | 9 | 10 | 10 | 10 | 9 | 9 | seasons\01-xianxia\chronicle\755-半个真相.md |
| 761 | 9 | 10 | 10 | 10 | 10 | 9 | seasons\01-xianxia\chronicle\761-林窈不哭.md |
| 775 | 9 | 10 | 10 | 10 | 10 | 9 | seasons\01-xianxia\chronicle\775-林叙看.md |
| 792 | 9 | 10 | 10 | 10 | 9 | 9 | seasons\01-xianxia\chronicle\792-苏挽在.md |
| 1061 | 8 | 10 | 10 | 10 | 8 | 8 | seasons\01-xianxia\chronicle\1061-苏挽端糖.md |
| 1105 | 8 | 10 | 10 | 10 | 10 | 8 | seasons\01-xianxia\chronicle\1105-苏挽在.md |
| 1118 | 8 | 10 | 10 | 10 | 9 | 8 | seasons\01-xianxia\chronicle\1118-林崇信.md |

## 7. Rewrite path (driven by section 5 weakness)

1. First fill R-track: tools/reader_subagent_driver.py + 真人 sub-agent run, 5 personas with isolation evidence -> effective_n >= 3 AND diversity >= 0.5 before any aggregate judgement.
2. Then fix E3 (ending hook) for 526 chapters: every chapter ending must add a concrete question the next chapter must answer, ban 她没回 / 明日再看 / pure mood.
3. Then fix E4 (POV agency) for 600 chapters: at least 2 agency verbs per chapter (决定 / 改为 / 不再 / 签下).
4. Then fix E2 (mid-turn choice) for 307 chapters: the mid section must contain a real POV choice with a cost.
5. Last fix E5 (relationship cost) for 310 chapters: at least one named-pair relationship must visibly move each chapter.
6. After every 3-chapter rewrite batch: run tools/reader_panel_runner.py check + aggregate and tools/jinjiang_chapter_distance.py --out, diff against this snapshot.

## 8. Forbidden shortcuts

- Do NOT cite this snapshot E_min average 5.09/10 as 接近爆款. It is an engineering floor, not a market score.
- Do NOT treat the 10-chapter R-track coverage as a substitute for 1145-chapter blindtest. It is just historical JSON indexing.
- Do NOT skip E3 / E4 fixes during the L2=0 window. With R-track missing, the engineering weakness is the only fixable evidence.
