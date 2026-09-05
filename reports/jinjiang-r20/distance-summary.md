# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-04 (post frontmatter-strip fix, regenerated from chapter-distance.json)
> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py
> Range: 1145 contiguous chapters
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (L2-real = 0, L1-effective filtered by echo_panel).
> This report only measures the engineering side distance.

## 1. One-line answer

After the frontmatter-strip fix, **11 chapters** clear the engineering 8.5 blowup line and **584 (47.6%)** sit in the 7-8.49 publish-eligible band.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 191 | 15.6% | clearly needs rewrite (structural) |
| 5-6.99 | 441 | 35.9% | needs choice or action |
| 7-7.99 | 469 | 38.2% | near entry, fix one dim |
| 8-8.49 | 115 | 9.4% | publish-ready single-chapter |
| >=8.5 | 11 | 0.9% | blowup-engineered single-chapter |

Average E_min: **6.18/10**. This is the engineering floor; do not cite it as 接近爆款.

## 3. Per-dimension fail counts (E_dim < 7.0)

| dim | failing chapters | meaning |
|---|---:|---|
| E1 opening conflict | 0 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 113 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 98 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 415 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 377 | named characters are present but no relationship moves |

## 4. Reader blindtest layer (R-track)

- panel_files: 0 (L2-real = 0, L1 downgraded by echo_panel)
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 5. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 595 | 0 | reader evidence missing |
| blowup chapter (min>=8.5) | 11 | 0 | same |
| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |

## 6. Bottom 15 chapters by E_min (next-round rewrite candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1136 | 4 | 10 | 10 | 4 | 10 | 6 | `seasons\01-xianxia\chronicle\1136-灶边.md` |
| 1126 | 4 | 10 | 6 | 4 | 4 | 5 | `seasons\01-xianxia\chronicle\1126-灶边雪.md` |
| 1120 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1120-林叙看.md` |
| 1070 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\1070-林叙等.md` |
| 1036 | 4 | 10 | 10 | 4 | 6 | 6 | `seasons\01-xianxia\chronicle\1036-林彻站.md` |
| 1025 | 4 | 10 | 10 | 4 | 6 | 6 | `seasons\01-xianxia\chronicle\1025-灶边雪.md` |
| 1023 | 4 | 10 | 6 | 10 | 4 | 5 | `seasons\01-xianxia\chronicle\1023-林叙等.md` |
| 982 | 4 | 10 | 10 | 4 | 10 | 7 | `seasons\01-xianxia\chronicle\982-旧仆不答.md` |
| 967 | 4 | 10 | 6 | 10 | 4 | 6 | `seasons\01-xianxia\chronicle\967-落.md` |
| 956 | 4 | 10 | 10 | 4 | 10 | 8 | `seasons\01-xianxia\chronicle\956-伸手.md` |
| 927 | 4 | 10 | 6 | 10 | 4 | 4 | `seasons\01-xianxia\chronicle\927-灶边.md` |
| 858 | 4 | 10 | 10 | 4 | 10 | 7 | `seasons\01-xianxia\chronicle\858-三张.md` |
| 828 | 4 | 10 | 10 | 4 | 9 | 7 | `seasons\01-xianxia\chronicle\828-林彻看林夙.md` |
| 810 | 4 | 7 | 10 | 4 | 5 | 8 | `seasons\01-xianxia\chronicle\810-阿湄不接信.md` |
| 808 | 4 | 10 | 10 | 4 | 10 | 8 | `seasons\01-xianxia\chronicle\808-苏挽最后写.md` |

## 7. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 291 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\291-升堂.md` |
| 435 | 9 | 10 | 10 | 10 | 9 | 9 | `seasons\01-xianxia\chronicle\435-来处.md` |
| 557 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\557-新痕.md` |
| 584 | 9 | 10 | 10 | 10 | 9 | 9 | `seasons\01-xianxia\chronicle\584-三个人.md` |
| 602 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\602-睁眼.md` |
| 605 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\605-水落.md` |
| 653 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\653-新痕.md` |
| 706 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\706-林叙等.md` |
| 775 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\775-林叙看.md` |
| 788 | 9 | 10 | 10 | 10 | 10 | 9 | `seasons\01-xianxia\chronicle\788-巷口一顶车.md` |

## 8. Distance is regenerated, never hand-edited

Refresh with: `py -3 -X utf8 tools/refresh_distance_summary.py`
after `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`
