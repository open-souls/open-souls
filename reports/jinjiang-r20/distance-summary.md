# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-04 (post frontmatter-strip fix, regenerated from chapter-distance.json)
> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py
> Range: 1145 contiguous chapters
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (L2-real = 0, L1-effective filtered by echo_panel).
> This report only measures the engineering side distance.

## 1. One-line answer

After the frontmatter-strip fix, **0 chapters** clear the engineering 8.5 blowup line and **129 (10.5%)** sit in the 7-8.49 publish-eligible band.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 473 | 38.5% | clearly needs rewrite (structural) |
| 5-6.99 | 625 | 50.9% | needs choice or action |
| 7-7.99 | 124 | 10.1% | near entry, fix one dim |
| 8-8.49 | 5 | 0.4% | publish-ready single-chapter |
| >=8.5 | 0 | 0.0% | blowup-engineered single-chapter |

Average E_min: **5.06/10**. This is the engineering floor; do not cite it as 接近爆款.

## 3. Per-dimension fail counts (E_dim < 7.0)

| dim | failing chapters | meaning |
|---|---:|---|
| E1 opening conflict | 0 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 316 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 124 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 869 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 892 | named characters are present but no relationship moves |

## 4. Reader blindtest layer (R-track)

- panel_files: 0 (L2-real = 0, L1 downgraded by echo_panel)
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 5. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 129 | 0 | reader evidence missing |
| blowup chapter (min>=8.5) | 0 | 0 | same |
| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |

## 6. Bottom 15 chapters by E_min (next-round rewrite candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1136 | 4 | 10 | 6 | 4 | 4 | 4 | `seasons\01-xianxia\chronicle\1136-灶边.md` |
| 1135 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1135-林崇看.md` |
| 1134 | 4 | 10 | 10 | 10 | 6 | 7 | `seasons\01-xianxia\chronicle\1134-林叙看.md` |
| 1132 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1132-林崇信.md` |
| 1126 | 4 | 10 | 6 | 4 | 4 | 4 | `seasons\01-xianxia\chronicle\1126-灶边雪.md` |
| 1124 | 4 | 7 | 10 | 10 | 6 | 6 | `seasons\01-xianxia\chronicle\1124-林彻看林夙.md` |
| 1123 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1123-苏挽端糖.md` |
| 1120 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1120-林叙看.md` |
| 1115 | 4 | 7 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1115-灶边.md` |
| 1113 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1113-林彻站.md` |
| 1106 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1106-林叙看.md` |
| 1099 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1099-灶边雪.md` |
| 1089 | 4 | 10 | 10 | 10 | 7 | 8 | `seasons\01-xianxia\chronicle\1089-苏挽端糖.md` |
| 1080 | 4 | 10 | 10 | 10 | 5 | 6 | `seasons\01-xianxia\chronicle\1080-林崇看.md` |
| 1078 | 4 | 10 | 10 | 10 | 5 | 6 | `seasons\01-xianxia\chronicle\1078-苏挽在.md` |

## 7. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 597 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\597-灶边雪.md` |
| 598 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\598-回问.md` |
| 703 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\703-判官.md` |
| 775 | 8 | 10 | 10 | 10 | 9 | 9 | `seasons\01-xianxia\chronicle\775-林叙看.md` |
| 1074 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\1074-灶边.md` |
| 115 | 7 | 7 | 10 | 10 | 7 | 7 | `seasons\01-xianxia\chronicle\115-炉下.md` |
| 116 | 7 | 7 | 10 | 10 | 8 | 7 | `seasons\01-xianxia\chronicle\116-监守.md` |
| 244 | 7 | 7 | 10 | 10 | 7 | 7 | `seasons\01-xianxia\chronicle\244-知道一些.md` |
| 275 | 7 | 7 | 10 | 10 | 7 | 7 | `seasons\01-xianxia\chronicle\275-回来了.md` |
| 291 | 7 | 10 | 10 | 10 | 7 | 8 | `seasons\01-xianxia\chronicle\291-升堂.md` |

## 8. Distance is regenerated, never hand-edited

Refresh with: `py -3 -X utf8 tools/refresh_distance_summary.py`
after `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
