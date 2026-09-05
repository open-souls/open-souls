# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-04 (post frontmatter-strip fix, regenerated from chapter-distance.json)
> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py
> Range: 1145 contiguous chapters
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (L2-real = 0, L1-effective filtered by echo_panel).
> This report only measures the engineering side distance.

## 1. One-line answer

After the frontmatter-strip fix, **1 chapters** clear the engineering 8.5 blowup line and **197 (17.2%)** sit in the 7-8.49 publish-eligible band.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 520 | 45.4% | clearly needs rewrite (structural) |
| 5-6.99 | 427 | 37.3% | needs choice or action |
| 7-7.99 | 153 | 13.4% | near entry, fix one dim |
| 8-8.49 | 44 | 3.8% | publish-ready single-chapter |
| >=8.5 | 1 | 0.1% | blowup-engineered single-chapter |

Average E_min: **5.11/10**. This is the engineering floor; do not cite it as 接近爆款.

## 3. Per-dimension fail counts (E_dim < 7.0)

| dim | failing chapters | meaning |
|---|---:|---|
| E1 opening conflict | 14 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 492 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 95 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 888 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 689 | named characters are present but no relationship moves |

## 4. Reader blindtest layer (R-track)

- panel_files: 0 (L2-real = 0, L1 downgraded by echo_panel)
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 5. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 198 | 0 | reader evidence missing |
| blowup chapter (min>=8.5) | 1 | 0 | same |
| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |

## 6. Bottom 15 chapters by E_min (next-round rewrite candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1144 | 4 | 10 | 10 | 4 | 5 | 6 | `seasons\01-xianxia\chronicle\1144-撕账.md` |
| 1141 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1141-林彻站.md` |
| 1136 | 4 | 10 | 6 | 4 | 4 | 4 | `seasons\01-xianxia\chronicle\1136-灶边.md` |
| 1135 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1135-林崇看.md` |
| 1132 | 4 | 10 | 6 | 10 | 4 | 6 | `seasons\01-xianxia\chronicle\1132-林崇信.md` |
| 1126 | 4 | 10 | 6 | 4 | 4 | 5 | `seasons\01-xianxia\chronicle\1126-灶边雪.md` |
| 1123 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1123-苏挽端糖.md` |
| 1121 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1121-林崇看.md` |
| 1120 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1120-林叙看.md` |
| 1115 | 4 | 7 | 6 | 10 | 4 | 6 | `seasons\01-xianxia\chronicle\1115-灶边.md` |
| 1113 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1113-林彻站.md` |
| 1111 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1111-林叙等.md` |
| 1107 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1107-林崇看.md` |
| 1106 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1106-林叙看.md` |
| 1100 | 4 | 10 | 10 | 4 | 6 | 7 | `seasons\01-xianxia\chronicle\1100-林彻站.md` |

## 7. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 775 | 9 | 10 | 10 | 10 | 9 | 9 | `seasons\01-xianxia\chronicle\775-林叙看.md` |
| 597 | 8 | 10 | 10 | 10 | 8 | 8 | `seasons\01-xianxia\chronicle\597-灶边雪.md` |
| 605 | 8 | 10 | 10 | 10 | 8 | 9 | `seasons\01-xianxia\chronicle\605-水落.md` |
| 660 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\660-第三人.md` |
| 664 | 8 | 10 | 10 | 10 | 9 | 8 | `seasons\01-xianxia\chronicle\664-阿湄不动.md` |
| 669 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\669-不封口.md` |
| 670 | 8 | 10 | 10 | 10 | 9 | 8 | `seasons\01-xianxia\chronicle\670-林叙等.md` |
| 674 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\674-那一半边.md` |
| 683 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\683-不挪灯.md` |
| 696 | 8 | 10 | 10 | 10 | 10 | 8 | `seasons\01-xianxia\chronicle\696-笔蘸新墨.md` |

## 8. Distance is regenerated, never hand-edited

Refresh with: `py -3 -X utf8 tools/refresh_distance_summary.py`
after `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
