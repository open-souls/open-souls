# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-05 (regenerated from chapter-distance.json)
> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py
> Range: 1227 chapter records
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (L2-real = 0, L1-effective filtered by echo_panel).
> This report only measures the engineering side distance.

## 1. One-line answer

After the frontmatter-strip fix, **0 chapters** clear the engineering 8.5 blowup line and **145 (11.8%)** sit in the 7-8.49 publish-eligible band.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 439 | 35.8% | clearly needs rewrite (structural) |
| 5-6.99 | 643 | 52.4% | needs choice or action |
| 7-7.99 | 135 | 11.0% | near entry, fix one dim |
| 8-8.49 | 10 | 0.8% | publish-ready single-chapter |
| >=8.5 | 0 | 0.0% | blowup-engineered single-chapter |

Average E_min: **5.14/10**. This is the engineering floor; do not cite it as 接近爆款.

## 3. Per-dimension fail counts (E_dim < 7.0)

| dim | failing chapters | meaning |
|---|---:|---|
| E1 opening conflict | 0 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 316 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 124 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 869 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 816 | named characters are present but no relationship moves |

## 4. Reader blindtest layer (R-track)

- panel_files: 0 (L2-real = 0, L1 downgraded by echo_panel)
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 5. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 145 | 0 | reader evidence missing |
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
| 1123 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1123-苏挽端糖.md` |
| 1120 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1120-林叙看.md` |
| 1115 | 4 | 7 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1115-灶边.md` |
| 1113 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1113-林彻站.md` |
| 1106 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1106-林叙看.md` |
| 1099 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1099-灶边雪.md` |
| 1080 | 4 | 10 | 10 | 10 | 5 | 7 | `seasons\01-xianxia\chronicle\1080-林崇看.md` |
| 1072 | 4 | 10 | 10 | 10 | 7 | 7 | `seasons\01-xianxia\chronicle\1072-林彻站.md` |
| 1070 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1070-林叙等.md` |
| 1065 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1065-林叙看.md` |

## 7. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 339 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\339-她说.md` |
| 597 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\597-灶边雪.md` |
| 598 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\598-回问.md` |
| 660 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\660-第三人.md` |
| 664 | 8 | 10 | 10 | 10 | 9 | 8 | `seasons\01-xianxia\chronicle\664-阿湄不动.md` |
| 669 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\669-不封口.md` |
| 775 | 8 | 10 | 10 | 10 | 9 | 8 | `seasons\01-xianxia\chronicle\775-林叙看.md` |
| 800 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\800-苏挽端糖.md` |
| 814 | 8 | 10 | 10 | 10 | 9 | 8 | `seasons\01-xianxia\chronicle\814-叶观澜离前夜.md` |
| 829 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\829-灯笼.md` |

## 8. Distance is regenerated, never hand-edited

Refresh with: `py -3 -X utf8 tools/refresh_distance_summary.py`
after `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
