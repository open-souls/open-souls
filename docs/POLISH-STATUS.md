# Polish Status · 2026-06-24 实时

> 主编在跑的精修 sweep 实时状态。每有重大变化更新。

## 进度

| 维度 | baseline | 当前 | 变化 |
|------|---------|------|------|
| ERROR | 189 | **0** | -189 (100%) |
| WARN | 235 | 67 | -168 (71%) |
| Total | 424 | 465 | +41 (cron 加 + 批次 39/40 补) |

**全卷 0 ERROR，prose_lint CI 过线。**

## ✅ 本周期新增：批次 39 + 批次 40 (ch436-465, 30 章 S++)

- 批次 39 (ch436-450): `docs/POLISH-S1-436-450.md` (commit ccece82) — 15/15 章 S++
- 批次 40 (ch451-465): `docs/POLISH-S1-451-465.md` (commit e83ab7b) — 15/15 章 S++
- 锚点系列推进至 **第 183 种身体**（+29）
- **新副 CP 开启**: 凌朔×沈疏桐（4 阶全部到位）
- **新锚点系列**: 林窈→林夙 糖（4 级全部到位）+ 牛阿大→林夙 粥（1 级）
- INDEX.md 同步补 ch436-465 目录

## 全卷 polish session 总览（截至 2026-06-24）

**12 个 Phase 3 子代理完成**：
- Phase 3-A: 沈疏桐伏笔回收 (ch429-435)
- Phase 3-B: 叶观澜 前置 (ch030/060/085/091/100/120/150)
- Phase 3-C: ch215-280 audit (8 HIGH items identified)
- Phase 3-D: ch215-280 plot holes fix
- Phase 3-E: ch005-018 ships backfill
- Phase 3-F: POV rotation ch300-400 (14 chapters)
- Phase 3-G: 苏×亚 ch301-350 (3→10 entries)
- Phase 3-H: 苏×亚 ch351-400 (already + enhanced)
- Phase 3-I: 苏×亚 ch201-250 (4→9 entries)
- Phase 3-J: 苏×亚 ch101-200 (8→12 entries)
- Phase 3-K: 苏×亚 ch251-300 (6→9 entries)
- Phase 3-L: 苏×亚 ch351-400 (6→8 entries, 暗流 HINT)

**CP 全卷分布（终态）**：
- 林×苏挽: 129 entries (29.7%)
- 林×阿湄: 149 entries (34.3%)
- 苏挽×阿湄: **56 entries (12.9%)** ← baseline ~3% → 12.9%

**POV 旋转**: 林夙 98.4% → 88% (ch251-300 现在 75%)

**伏笔**: 8 HIGH items 全部 resolved (林崇 direct 由 cron ch433/435 自然落地)

---

## v4 改动（2026-06-24）

**核心结构改动**：
- 假死事件从 ch458 提前到 ch300 区间
- OFFSCREEN 周从 ch300 持续到 ch450（147 章）
- 林夙 INDEX 出场 97.9% → 71.1%（达成 70% 目标）

**新增文件**：
- `arc.json` 改 4 个 beat 定义
- `_plan_ch200-465.md`（替代 v3 plan）
- `_OFFSCREEN_RULES.md`（OFFSCREEN 周写作规则）
- `interludes/I-001~I-015.md`（15 插章，前置分布 ch3-40）

**新写章节**：
- ch200《那一兜》假死前最后 100 章起手
- ch300《那条道》假死当日
- ch304《她没接》阿湄收到噩耗
- ch305《她说》阿湄处理"他没回来"
- ch320《她的刀》阿湄黑化起点
- ch355《她接》苏挽黑化起点
- ch360《他以为》叶观澜以为得手

**归档**：
- `_plan_ch429-458.md` → `_plan_ch429-458_v3_archived.md`（保留作历史）

**Anchor 序列**: SX-A-1 ~ SX-A-30 (30 个 1级·建立 锚点, 跨 ch101-435 分布)

## 已完成

- ✅ **Batch A** (ch001-100) — 100/100 章过 lint + 84+ 新锚点
- ✅ **Batch B** (ch101-200) — 100/100 章过 lint + ships 字段回补 23 章
- ✅ **Batch C** (ch201-300) — 99/99 章过 lint
- ✅ **Batch D** (ch301-424) — 0 ERROR + ch423/424 anchors/payoff/transitions 补齐
- ✅ **ch425-428** (cron 新章) — 4 章 inline polished
- ✅ **ch429-435** (Phase 3-A) — 沈疏桐伏笔回收 ✓ 落在 24 章窗口内 (ch429)
- ✅ **ch030/060/085/091/100/120/150** (Phase 3-B) — 叶观澜前置 ✓ 7 章插入完成
- ✅ **ch300** (1 个残留 filler) — 已修
- ✅ 3 份 audit 报告（伏笔 + CP + ch215-280）写入 docs/

## 进行中（agents 后台）

- 🚀 **Phase 2 POV 旋转** (ch201-428) — 似乎停滞，输出文件 1h+ 未更新
- 🚀 **Phase 3-D ch215-280 plot holes fix** (ch281-300 only) — 8 HIGH items per audit
- 🚀 **Phase 3-F POV rotation ch300-400** — 94-96% 林夙 → 75-80% 目标

## ✅ 已完成（this cycle）

- ✅ **Phase 3-A 沈疏桐伏笔回收** — ch429-435 ✓ (reveal in ch429)
- ✅ **Phase 3-B 叶观澜前置** — ch030/060/085/091/100/120/150 (7 章)
- ✅ **Phase 3-E ch005-018 ships backfill** — 10 章 (4 章 already had ships)

## ✅ Phase 3-C audit 完成 (ch215-280)

详见 `docs/PHASE3-CH215-280-AUDIT.md`

**HIGH 风险伏笔（已收）：**
1. ch235 赤渊"放了一个" — ✓ 已修（ch300 补笔，描述 mechanism）
2. ch269 "故人" 身份 — ✓ 已修（ch288 补笔 → 叶观澜 scout）
3. ch277 沈疏桐"知道了就够了" — ✓ 留白是 §3 设计本身
4. ch274 **首引者 alive** — ✓ 已由 ch290/295/300 揭
5. ch279 阿湄压制层闪现 — ✓ §9 要求 ≥3 章前置，已补 ch285/291/298

**HIGH 5 林崇直接出场** — 未补（agent 判定需要 dedicated session），林叙-as-proxy 维持信道

**Cast 问题（部分修复）：**
- 林崇 1 章 — 仍是 1 章，林叙代理保留信道
- 凌朔 4 章 — ch284/293 补到 6 章
- 叶清梧 0 章 — 未触及（§9 "另一半人"未揭，仍待 ch440+）

## ✅ Phase 2 + Phase 3-F POV 旋转完成

**25 章改 POV** (ch244-385)：
- Phase 2: 11 章 (ch244/245/259/260/261/264/266/267/275/286/314)
- Phase 3-F: 14 章 (ch301/305/309/318/321/325/330/339/351/355/363/371/383/385)

**POV 分布（旋转后）：**
| 范围 | 林夙 POV | 旋转前 | 状态 |
|------|---------|--------|------|
| ch001-200 | 100% | 100% | 不动（早期作品）|
| ch201-250 | 84% | 88% | ↓ 4pp |
| **ch251-300** | **74%** | 90% | **↓ 16pp** ✓ |
| ch301-350 | 78% | 96% | ↓ 18pp ✓ |
| ch351-400 | 82% | 94% | ↓ 12pp ✓ |
| ch401-450 | 72% | 72% | 已达目标 |

**整体**: 88% 林夙 / 12% 其他 (从 98.4% → 88%，距离 60% 目标还差 28pp)

**新 POV 角色**: 苏挽×23, 阿湄×14, 裴无咎×5, 沈疏桐×4, 牛阿大×1, 余伯×1, 凌朔×1, 叶观澜×1, 林窈×1

## ✅ Phase 3-G 苏×阿 补足完成

**6 章添加苏×阿 暗流场景**（ch308/312/318/320/323/346）

**苏×阿 ch301-350 co-occurrence**: 3 → 9 (超额完成 4-6 章目标)

**新增锚点 SX-A-7~12**：
- SX-A-7 ch308: 阿湄搁茶隔两寸；苏挽挪近半寸（距离锚点）
- SX-A-8 ch312: 阿湄递暖壶，肩挨肩三步半，未竟停顿
- SX-A-9 ch318: 袖角擦桌沿，苏挽指节收一分（感官·手）
- SX-A-10 ch320: 阿湄添半盏凉水，苏挽挪近一寸（重复小动作）
- SX-A-11 ch323: 阿湄剩半瓣橘子 vs 苏挽隔两寸搁茶（距离·变体）
- SX-A-12 ch346: 苏挽递凉茶半息，阿湄接；空出来的手收袖里

**Anchor level**: 全部 B-mode（暗流）per CLAUDE.md §八，相邻差 ≤1

## 下一步触发

- 任何 agent 返回 → 跑 `python tools/review_batch.py <range>` 抽检
- Batches 全完成 → 全卷 lint 复跑
- Phase 2 POV 完成 → 复跑 audit 看 POV 比例

## Phase 2/3 backlog

1. **POV 旋转** (进行中)
2. **沈疏桐揭穿** (Phase 3-A in flight)
3. **叶观澜前置** (Phase 3-B in flight)
4. **ch215-280 plot holes** (Phase 3-C audit in flight)
5. **ch301-350 苏×阿 补足** (待 Phase 2 POV 完成后)
6. **苏挽×阿湄 ch411-424 黑化期搭档弧** (audit 标出可强化)

## 文档

- `seasons/01-xianxia/JINJIANG-CRAFT.md` — 晋江手法全谱
- `docs/PHASE2-AUDIT-REPORT.md` — 伏笔 actionable
- `docs/PHASE2-CP-AUDIT.md` — CP 同框 + POV 校准
- `docs/PHASE3-CH215-280-AUDIT.md` — 中段 plot holes (audit in flight)
- `tools/review_batch.py` — 批量审查工具

## ✅ Phase 4-A ch301-435 plot hole audit

`docs/PHASE4-CH301-435-AUDIT.md` (309 lines)

**6 HIGH items identified:**
1. 叶清梧 完全缺席 (CLAUDE.md §3 另一半人)
2. 宋观山 身份未揭
3. 首引者/房间里第三人 身份未揭
4. Beat 编号 ch423-428 跳号 (HIGH 节奏断点)
5. ch432 叶观澜 折信收信人未揭
6. **阿湄 5 章缺席 ch428-432 (违反 3-cap)** ✓ Phase 4-B 已修

**Cast rotation violations (6):** 阿湄 5章 / 沈疏桐 11章 / 牛阿大 34章 / 林叙 60章 / 叶观澜 63章 / 裴无咎 20章

**12 MED / 10 LOW** — 见 audit doc

**0 hard line violations** ✓

## ✅ Phase 4-E ch436-465 post-假杀 audit

`docs/PHASE4-E-POSTFAKE-AUDIT.md` (387 lines)

**假杀验证: ✓ 假死（fake death）CONFIRMED**
- ch465 末段 "水底下，林夙睁着眼" + "按袖口" — 最直接证据
- 5 witnesses positioned: 裴无咎+牛阿大（崖边）/ 凌朔+沈疏桐（山门）/ 阿湄（岔路）
- 策划者: 叶观澜 (ch456) + 林夙共谋 (ch457)
- 觉醒: 阿湄 (ch445/ch457/ch460/ch464) 正确执行 CLAUDE.md §9 layer 3

**HIGH items 8 项 (5 伏笔 + 3 硬线)**:
- 伏笔 (5): 宋观山身份 / 林崇房中第三人 / 叶观澜 ch432 折信收信人 / 叶清梧完全缺席 / 首引者完整链
- 硬线 (3): 7 章单字标题 (ch453/455/456/457/460/461/462) / ch455-458 cast=2 x4连 / ch448-451 阿湄缺席 x4连

**22 条 区间内 payoff** + **9 条跨段未收** — 见 audit doc

**节奏**: 收网期完成度高，假杀 payoff 干净，下一 phase = 噩耗传开+黑化展开

## ✅ Phase 4-F: post-假杀 hard-line fixes (COMPLETE)

**3 hard-line violations fixed:**

1. **7 章单字标题 → 2+ 字**: ch453 写好 / ch455 听罢 / ch456 算过 / ch457 信里 / ch460 转身 / ch461 分定 / ch462 定下 — title field only, no body changes
2. **ch448 阿湄 body mention**: "阿湄不在那条道上。林夙袖子里那张她没寄到的信，还在。" (relay/item-type via 林夙's袖子里 unsent letter)
3. **ch456 cast expanded**: [叶观澜, 沈疏桐, 阿湄(远景)] + body "东边那条道上，阿湄还在走。她不知道，她在走的那条道，是叶观澜算过的那条。"

**Verified:**
- review_batch ch448-462 → 15/15 PASS, 0 ERROR (review_batch.py fix for prose_lint_exempt 也完成)
- 阿湄 ≥4章 gaps 全部消除 (现在最大 gap = 3章)
- ch455-458 cast streak: 2/3/2/2 — 不再 4 consecutive =2 ✓
- 文件未改 ch465, 未改 hooks, 未加完整场景

**book state · 2026-06-24**:
- 465 章 / 0 ERROR / ch436-465 全 30 章 review PASS (11 EXEMPT, 19 WARN-only)
- review_batch.py 已修 exempt-crash (was: `m['micro']` for prose_lint_exempt → now: print EXEMPT line)
- Phase 4-E audit 完成 (docs/PHASE4-E-POSTFAKE-AUDIT.md, 387 lines, 8 HIGH items)
- Phase 4-F 完成 (3 硬线违规全修)
- 5 HIGH 伏笔 仍待 ch466+ (cron 续推后处理)

## ✅ Phase 4-D 阿湄 ch434-444 缺席补回 (cron 后新违例)

**4 章补过场** (ch435/440/442/444) — Phase 4-B 后 cron 推广 ch436-444 又产生 11 章缺席

- ch434-444 阿湄 body mentions: ch434=8, ch435=**1 (was 0)**, ch436=4, ch437=2, ch438=4, ch439=3, ch440=**1 (was 0)**, ch441=6, ch442=**1 (was 0)**, ch443=9, ch444=**1 (was 0)**
- 全部 11 章 ≥1 阿湄 body mention
- Cast 未改 (3-cap cast 规则仍 violate，但叙事空洞已破)
- 0 ERROR

**Insertion types:**
- ch435: 余伯 silent acknowledgment that 阿湄 brought 林崇
- ch440: 林崇 internal note that 阿湄 left halfway
- ch442: 林夙 silent link of 阿湄 to 叶观澜 (after "叶观澜带走了她")
- ch444: 林窈 quiet noting of 阿湄's departure

## ✅ Phase 4-B 阿湄 5章缺席补回

**2 章补过场** (ch429/430) — 叙事空洞已破

- ch428-432 阿湄 body mentions: ch428=3, ch429=**1 (was 0)**, ch430=**1 (was 0)**, ch431=10, ch432=8
- Cast 未改 (3-cap cast 规则仍 violate，但叙事层面已 OK)
- All 5 章 ch428-432 review: 5/5 PASS, 0 ERROR
- Beat 编号修正 **SKIPPED** — cron 主动 regenerate，覆盖风险

**Insertion types:**
- ch429: 60字 — 林夙袖里 阿湄塞的小包姜片（sensory anchor, 重复小动作 pattern）
- ch430: 86字 — 凌朔 转交 阿湄南下前口信「替我看着」（relay pattern, ch431 苏挽 dialogue setup）

## ✅ Phase 3-L ch351-400 苏×亚 补足

**1 章补 2 锚** (ch355 单一合规 cast，2 锚分两 `---` 段) — SX-A-29~30, **1级·建立 + 暗流 HINT**

- ch351-400 苏×亚 entries: 6 → **8** (12% → 16%)
- All 50 章 ch351-400 lint: 50/50 PASS, 0 ERROR

**锚点：**
- **SX-A-29 / ch355**: 苏挽绕半寸不让阿湄让——主动调方向，阿湄没抬头（1级·暗流 hint）
- **SX-A-30 / ch355**: 苏挽袖口松一下又收——阿湄只看见"松"，没看见"收"（半动作·被半见）

## ✅ Phase 3-K ch251-300 苏×亚 补足

**3 章补足** (ch252/258/262) — SX-A-26~28 anchor series, **情愫期 1级·建立**

- ch251-300 苏×亚 entries: 6 → **9** (12% → 18%, 对齐 ch201-250)
- All 50 章 ch251-300 lint: 50/50 PASS, 0 ERROR, WARN no delta

**锚点：**
- **SX-A-26 / ch252**: 阿湄问"落款年份"，苏递档页；同物件·不同方向，没看着彼此
- **SX-A-27 / ch258**: 阿湄说"我去"，苏挽没点头没看；同步决定·中隔一段廊
- **SX-A-28 / ch262**: 同街同时辰，苏挽步子快半拍收；阿湄余光看见，没出声

## ✅ Phase 3-J ch101-200 苏×亚 补足

**4 章补足** (ch109/112/113/180) — SX-A-22~25 anchor series, **情愫期 1级·建立**

- ch101-200 苏×亚 entries: 8 → **12** (8% → 12%, 对齐 ch251-300)
- All 100 章 ch101-200 lint: 100/100 PASS, 0 ERROR, WARN no delta

**锚点：**
- **SX-A-22 / ch109**: 字条边角卷了压平——苏挽认得那种压法，是余伯桌沿角度（细节共鸣）
- **SX-A-23 / ch112**: 阿湄拇指在纸角按了一下——把一件事压到没人能立刻看见的位置（动作暗示）
- **SX-A-24 / ch113**: 阿湄说"姜玉衡"——苏挽听见同字，认得同一份档案，没说出来（信息共鸣）
- **SX-A-25 / ch180**: 苏挽把茶杯搁在布袋和阿湄中间——给这件事划了一个两人共同可见的位置（空间锚点）

## ✅ Phase 3-I ch201-250 苏×亚 补足

**5 章补足** (ch233/245/248/249/250) — SX-A-17~21 anchor series, **情愫期 1级·建立**

- ch201-250 苏×亚 entries: 4 → **9** (8% → 18%, 对齐 ch251-300 12%)
- All new entries at 1级 (no skipping — adjacent差 ≤1 maintained)
- All 18 章 ch233-250 lint: 0 ERROR / 0 micro-warn

**锚点：**
- **SX-A-17 / ch233**: 阿湄朝信藏处看一眼——认得苏挽的字，没问
- **SX-A-18 / ch245**: 阿湄扫三行急信——记了，没出声 (POV 阿湄 internal)
- **SX-A-19 / ch248**: 廊下吃粥同一条风带走——隔柱，谁也没抬眼
- **SX-A-20 / ch249**: 苏挽先开那句话，阿湄没看她——压在眼底里
- **SX-A-21 / ch250**: 阿湄把自己那碗往苏挽那侧挪一寸——没挨着，没看

## ✅ Phase 3-H ch351-400 苏×亚 增强

**4 章增强**（ch374/379/390/395）— SX-A-13~16 anchor series

ch351-400 entries: 6 (12% density, 对齐 ch251-300)

**苏×亚 全卷密度（终态）**：
- ch001-100: 0% (早期)
- ch101-200: 12 entries (12%) (Phase 3-J 助推)
- ch201-250: 9 entries (18%) (Phase 3-I 助推)
- ch251-300: 9 entries (18%) (Phase 3-K 助推)
- ch301-350: 10 entries (20%) (Phase 3-G 助推)
- ch351-400: **8 entries (16%)** ← Phase 3-L 助推
- ch401-435: 8 entries (~23%) (活跃)
- **全卷 56 entries / 435 章 (12.9% 平均)** — 从 baseline ~3% 拉到 12.9%
- `engine/prose_lint.py` — 文笔 lint
