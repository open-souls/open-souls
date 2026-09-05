# Distance to Jinjiang blowup - full season engineering snapshot

> Generated: 2026-09-04 (post frontmatter-strip fix)
> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py
> Range: 1145 contiguous chapters
> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6
> Honest note: R-track real reader evidence = 0 valid samples (see section 3).
> This report only measures the engineering side distance.

## 1. One-line answer

After the 2026-09-04 frontmatter-strip fix, **0 chapters** clear the engineering 8.5 blowup line and **34 (3.0%)** sit in the 7-7.99 publish-eligible band. The previous snapshot reported 8 chapters over 8.5 and 406 over 7.0; that was inflated by review-block DECISION hits leaking into E4/E5. This is the honest distance.

## 2. Engineering score distribution (E_min = min(E1..E5))

| bucket | chapters | share | meaning |
|---|---:|---:|---|
| <5 | 996 | 87.0% | clearly needs rewrite (structural) |
| 5-6.99 | 115 | 10.0% | needs choice or action |
| 7-7.99 | 34 | 3.0% | near entry, fix one dim |
| 8-8.49 | 0 | 0.0% | publish-ready single-chapter |
| >=8.5 | 0 | 0.0% | blowup-engineered single-chapter |

Average E_min: **4.22/10**. This is the engineering floor; do not cite it as 接近爆款.

Compared to the 2026-09-04 phase-2 snapshot: total <5 chapters jumped from 262 to 996 because review-block DECISION hits no longer inflate E4/E5. The previous snapshot was systematically optimistic by ~1.6 points on E_min. This is the truthful baseline.

## 3. Per-dimension fail counts (E_dim < 7.0)

After the frontmatter-strip fix:

| dim | failing chapters | meaning |
|---|---:|---|
| E1 opening conflict | 736 | opens on scenery or character relations, no action or resistance |
| E2 mid-turn choice | 497 | POV never makes a real mid-chapter choice, just records or passes through |
| E3 ending hook | 101 | ends on mood or generalization, leaves no specific next-chapter question |
| E4 POV agency | 894 | agency-verb density is too low, POV feels like an observer |
| E5 relationship cost | 692 | named characters are present but no relationship moves |

E4 is still the dominant single-dimension failure: 894 / 1145 chapters (78%) lack a real agency verb in the body. E1 jumped from 29 to 736 because the old snapshot was reading review-block RESISTANCE words (e.g. 「不签」「不再」) and counting them as opening-paragraph resistance.

## 4. Reader blindtest layer (R-track)

- Current coverage: **10 chapters** indexed by reader JSONs (drop or next_chapter_focus).
- All coverage is from historical reader-*.json files. There are 0 L2 真人 sub-agent entries.
- tools/reader_panel_runner.py check currently: L2-real=0, L2-reader=0, L1=6, effective_n=0.
- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.

## 5. Distance to the three gates

| gate | engineering pass count | real pass count with R-track | gap |
|---|---:|---:|---|
| publish (min>=7.0) | 34 | 0 | reader evidence missing |
| blowup chapter (min>=8.5) | 0 | 0 | same |
| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |

## 6. Bottom 15 chapters by E_min (next-round rewrite candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 4 | 4 | 10 | 10 | 10 | 7 | seasons\01-xianxia\chronicle\001-退婚书.md |
| 2 | 4 | 4 | 6 | 10 | 4 | 4 | seasons\01-xianxia\chronicle\002-叫对人.md |
| 3 | 4 | 4 | 10 | 10 | 8 | 7 | seasons\01-xianxia\chronicle\003-三年一碗.md |
| 4 | 4 | 4 | 10 | 10 | 6 | 6 | seasons\01-xianxia\chronicle\004-林窈井边.md |
| 7 | 4 | 4 | 10 | 10 | 5 | 6 | seasons\01-xianxia\chronicle\007-林崇称量.md |
| 8 | 4 | 7 | 6 | 10 | 4 | 4 | seasons\01-xianxia\chronicle\008-一眼.md |
| 9 | 4 | 7 | 6 | 10 | 4 | 4 | seasons\01-xianxia\chronicle\009-林彻磨局.md |
| 10 | 4 | 7 | 6 | 10 | 4 | 4 | seasons\01-xianxia\chronicle\010-赤渊茶凉.md |
| 11 | 4 | 10 | 6 | 10 | 4 | 4 | seasons\01-xianxia\chronicle\011-藕荷衣.md |
| 12 | 4 | 4 | 6 | 10 | 4 | 5 | seasons\01-xianxia\chronicle\012-夹道.md |
| 13 | 4 | 7 | 6 | 10 | 4 | 4 | seasons\01-xianxia\chronicle\013-她来过.md |
| 14 | 4 | 7 | 6 | 4 | 4 | 4 | seasons\01-xianxia\chronicle\014-压四天.md |
| 15 | 4 | 4 | 6 | 4 | 4 | 5 | seasons\01-xianxia\chronicle\015-代签.md |
| 16 | 4 | 7 | 6 | 4 | 4 | 4 | seasons\01-xianxia\chronicle\016-云栀井台.md |
| 17 | 4 | 7 | 6 | 10 | 4 | 5 | seasons\01-xianxia\chronicle\017-露底.md |

## 7. Top 10 chapters by E_min (model-paragraph candidates)

| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |
|---:|---:|---:|---:|---:|---:|---:|---|
| 223 | 7 | 7 | 10 | 10 | 7 | 7 | seasons\01-xianxia\chronicle\223-第三遍.md |
| 236 | 7 | 7 | 10 | 10 | 7 | 7 | seasons\01-xianxia\chronicle\236-那道痕.md |
| 244 | 7 | 7 | 10 | 10 | 7 | 8 | seasons\01-xianxia\chronicle\244-知道一些.md |
| 259 | 7 | 7 | 10 | 10 | 7 | 7 | seasons\01-xianxia\chronicle\259-踏出去.md |
| 299 | 7 | 10 | 10 | 10 | 8 | 7 | seasons\01-xianxia\chronicle\299-收着.md |
| 546 | 7 | 7 | 10 | 10 | 7 | 7 | seasons\01-xianxia\chronicle\546-端碗.md |
| 575 | 7 | 7 | 10 | 10 | 7 | 8 | seasons\01-xianxia\chronicle\575-改写.md |
| 583 | 7 | 7 | 10 | 10 | 8 | 7 | seasons\01-xianxia\chronicle\583-落款.md |
| 605 | 7 | 7 | 10 | 10 | 8 | 9 | seasons\01-xianxia\chronicle\605-水落.md |
| 622 | 7 | 7 | 10 | 10 | 7 | 7 | seasons\01-xianxia\chronicle\622-问路.md |

## 8. Frontmatter-strip diff vs prior snapshot

| metric | pre-fix (polluted) | post-fix (clean) | delta |
|---|---:|---:|---:|
| chapters over 7.0 | 406 | 34 | -372 |
| chapters over 8.5 | 8 | 0 | -8 |
| average E_min | 5.82 | 4.22 | 1.60 |
| E4 fail count | 600 | 894 | +294 |
| E5 fail count | 310 | 692 | +382 |
| E1 fail count | 29 | 736 | +707 |

The diff above is the engineering layer, not a literary judgment. The 2026-09-04 phase-2 batch 6 commit (tools/jinjiang_chapter_distance.py + tests/test_jinjiang_chapter_distance.py) fixed the frontmatter-strip bug. The next round can now trust the engineering numbers when picking rewrite targets.
