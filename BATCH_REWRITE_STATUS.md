# Batch Rewrite Status

Run `python engine/batch_rewrite.py --status` to refresh.

**Total scope**: 876 chapters to bring to gold standard
- 244 §七.1 disease chapters (have real prose, just broken)
- 632 stub chapters (9-line templates, need full write)

**Per dispatch budget** (2 bounded Claude workers; `$8.0` max per job, 420-second timeout):
- Each job receives only its target chapter prompt and compact context.
- A job is not publishable until the outer runner writes an independent receipt.

## Workflow

1. **范文章 ready**: ch512-不接.md (苏挽 POV, 行为先于意识)
2. **Picker**: `python engine/batch_rewrite.py --pick N` chooses N targets (stubs first, then disease)
3. **Dispatch**: `python engine/batch_rewrite.py --pick N --no-skip-done --no-dry-run` writes dispatch prompts to `prompts/dispatch/ch###.txt`
4. **Run**: `python engine/run_dispatch.py --workers 2 --max-budget-usd 8.0` runs bounded `claude -p` jobs and writes independent PASS/BLOCKED receipts to `prompts/.results/`.

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

## 主编复核快照 · 2026-08-04

- 机器扫描：1330 个章文件；559 章 ERROR，121 章 WARN。
- `_STUB_MANIFEST.json` 当前使用 `chapter_numbers`，共 607 个 stub 编号；调度器已兼容该格式。
- `python engine/batch_rewrite.py --status` 同时报告静态 stub 总数与实际 `stubs_remaining`，避免把已完成章节重复算进待办；当前为 607 个静态 stub 编号、实际剩余 stub 549 个、391 个唯一 lint 错误号，其中 384 个当前候选文件仍未过完整发布门。扩展公式门新增捕获了旧稿变体，数字变化按独立门结果记录。本轮主编复核范围已扩至 ch964，剩余章节仍需继续清理。
- strict editorial 现额外卡高频物象位置（`那一寸/那一道/那一截` 等）与“我/他/她自己”自我承担回声；调度器只给 Claude `Read,Edit`，本地门负责验证，超时从 900 秒收紧为 420 秒，避免反复回读上下文吞掉整笔预算。
- runner 现在快照目标以外的 prompt、receipt、根目录和 `engine/tools/tests`；Claude 生成伪 receipt 或 sidecar 草稿都会写入 `side_effects` 并保持 BLOCKED。
- `ch1000-撕账.md` 已由 Claude 草稿经主编回炉：正文 1573 汉字，strict editorial review PASS，score 12/14。
- `ch999-真合前拂晓.md` 已由 Claude 草稿经主编复读和局部回炉：正文 1654 汉字，strict editorial review PASS，score 13/14；已修复时间锚、重复解释和林夙 POV 越界。
- `ch881-林崇看.md` 已由 Claude 高预算重写、主编降分复核：正文 2305 汉字，strict editorial review PASS，score 12/14；当前判定为可连载初稿，不称爆款成稿。
- `ch890-林叙看.md` 已由 Claude 窄上下文重写、主编重构现场：正文 1556 汉字，strict editorial review PASS，score 12/14；修复“方向朝着”公式、让林夙现场施压，并把报信暂压在盖碗下。
- `ch896-林崇信.md` 的 Claude 首稿经主编拒收后重构：正文 1637 汉字，strict editorial review PASS，score 12/14；让林崇、林彻、王姨娘、老仆在东堂用旧契、茶盏和封信完成一次有代价的定夺。
- `ch897-灶边雪.md` 的 Claude 半成稿经主编修证据与禁词：正文 1902 汉字，strict editorial review PASS，score 12/14；让林夙、苏挽、阿湄在灶火、雪水和第七页旧契之间完成拆信与藏页选择。
- `ch898-林彻站.md` 的 Claude 首稿达到预算上限后被 runner 标为 BLOCKED；主编清掉“方式/那一路”自指公式后复核：正文 1542 汉字，strict editorial review PASS，score 12/14。
- `ch900-林叙看.md` 的 Claude 半成稿达到预算上限且仅 1192 字；主编补足林夙隔门施压与第三行选择后复核：正文 1637 汉字，strict editorial review PASS，score 12/14。
- `ch902-灶边.md` 的 Claude 首稿机器门通过但公式扫描拒收；主编整章重构后复核：正文 1698 汉字，strict editorial review PASS，score 12/14。
- `ch903-苏挽端糖.md` 的 Claude 首稿自报重写但目标 hash 未变化，扩展回声门抓到 31 处物象位置；主编确认原稿整章模板循环后重写为苏挽拒绝交名、带走赤线的糖摊物证链，正文 1556 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch904-林彻看林夙.md` 的 Claude 修订达到 $4 预算上限并被 runner 标为 BLOCKED；主编拒收其重复解释和自评元数据，整章重写为林彻、林夙、林崇在耳房的正面交锋；正文 1715 汉字，最终 lint、公式扫描与 strict editorial review PASS，但 Claude 运行本身不记为 PASS。
- `ch905-林叙等.md` 的 Claude 首稿机器门通过；主编复读后清掉自解释腔并把模型 13/14 降为 12/14，正文 1675 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch906-林崇信.md` 的 Claude 首稿机器门通过但被主编拒收，因「那一截/那一寸/停住/抬眼」循环整章重写；正文 1895 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 首稿不记为最终 PASS。
- `ch908-林彻站.md` 的 Claude 调用成功但没有改文件，原稿有 37 处方向回环、16 处自我修复回环；主编整章重构为东书房交信，正文 1564 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 不记为 PASS。
- `ch909-苏挽在.md` 的 Claude 调用成功但没有改文件，原稿还有同构公式、重复 hook 和苏挽×苏挽自配对；主编整章重构为药庐物证链，正文 1592 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 不记为 PASS。
- `ch910-林叙看.md` 的 Claude 首稿机器门通过；主编复读后修掉「看的方式是掂」解释腔，正文 2270 汉字，最终 lint、公式扫描与 strict editorial review PASS，score 12/14。
- `ch913-苏挽端糖.md` 的 Claude 首稿达到 $4 预算上限并被主编判定为旧模板换名；主编重写为糖摊交易、旧秤与半印物证链，正文 1674 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 首稿不记为 PASS。
- `ch914-林彻看林夙.md` 的 Claude 首稿达到 $4 预算上限并留下 1498 字半成稿；主编修正笔锋解释腔、hook 和字数后复核：正文 1533 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch915-林叙等.md` 的 Claude 首稿机器门通过；主编重写 review/hook、清掉「久是他自己定的」「方才」等腔词，正文 2296 汉字，最终 lint、公式扫描与 strict editorial review PASS，score 12/14。
- `ch916-林崇信.md` 的首稿留下「方向朝着」并有严重“我自己”回声，第二次 Claude 返工达到 $4 上限；主编重写为林崇压私印、烧半页旧账、林彻拒绝遮字，正文 1697 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch917-灶边雪.md` 的 Claude 重写通过基础机器门；主编复读后压掉“盏底那道痕/揣/方才/自己”回声，保留苏挽拒送账页、阿湄补帕、余伯门外硬钩子，正文 1743 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch918-林彻站.md` 的 Claude 自报删净公式但独立门抓到 13 处「方向朝着」与 51 处物象回声；主编拒收后重写为林彻送私印信、留下赤线、拒绝替父亲拆话，正文 1604 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch919-苏挽在.md` 的 Claude 路由超时且无 receipt；主编重写为苏挽保留第七页原件、给林叙送纸角提示并留在余伯院，正文 1540 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch920-林叙看.md` 的 Claude 首稿虽修改目标文件，但只有 1240 字且缺 review/score 元数据，独立 strict editorial 拒收；主编重写为林叙拆信、林崇承认第三行留白、林夙带纸角去找苏挽，正文 2198 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch924-林彻看林夙.md` 的 Claude 首稿独立门抓到 16 处方向回环、5 处自我修复回环和 62 处物象位置回声；主编重写为林彻拆分赤线/黑扣、林崇封门失败、林夙去见苏挽，正文 2218 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch925-林叙等.md` 的 Claude 首稿正文虽达 2508 字，但独立公式/回声门抓到 54 处物象位置回声；主编重写为林叙等林夙带回黑扣、林崇面对被撕封令、林夙在第三行落名，正文 2238 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch927-灶边雪.md` 的 Claude 首稿独立门抓到 59 处物象位置回声且超出外层时间预算；主编重写为苏挽在灶边验黑扣、拒交第七页原件、阿湄留住青粉与鞋印，正文 2386 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch928-林彻站.md` 的 Claude 首稿独立门抓到 52 处方向回环、4 处自指方式公式、100 处物象位置回声和 35 处自指回声；主编重写为林彻承认开门、把红线与木牌留在案上、要求林崇用私印承担，正文 1624 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch929-苏挽在.md` 的 Claude 首稿基础 lint 通过但缺独立 editorial 元数据门；主编重写为苏挽把第七页原件带进余伯院、只交半张抄件、与阿湄留下门外青粉和鞋印，正文 1566 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch930-林叙看.md` 的 Claude 首稿独立门抓到 3 处方向公式和 28 处自指回声；主编重写为林叙用水、灯和纸纤维验半张抄件，拒绝林崇用私印补缺，并让林夙追查旧染坊，正文 1589 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch933-苏挽端糖.md` 的 Claude 首稿基础门通过但独立 editorial 门拒收其缺少可信复核元数据且仍有换名复述；主编重写为苏挽端糖出门、用半块糖换半张抄件、阿湄封存旧线，正文 1595 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch934-林彻看林夙.md` 的 Claude 调用成功但没有修改目标，原稿有 37 处方向回环、14 处自我修复公式和 76 处物象位置回声；主编整章重写为林彻、林夙追到旧染坊，以三股封线、旧蜡和失册线索打开下一步，正文 1802 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch935-林叙等.md` 的 Claude 修改目标但留下 lint 与严格编辑失败的半成稿；主编整章重写为林叙验木片与封条、林崇落印、林夙带回第三股封线，正文 1830 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch936-林崇信.md` 的 Claude 首稿只有 892 字且缺少 review/score，独立严格门拒收；主编整章回炉为林崇把旧染坊封令与失册责任拆开落名，正文 1526 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch937-灶边雪.md` 的 Claude 首稿膨胀到 39309 字，方向/自我修复/物象回声达到上千次，独立门拒收；主编整章回炉为苏挽在灶边验糖纸与黑蜡、林夙携无印拓纸、阿湄发现门外靛蓝鞋印，正文 1508 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch938-林彻站.md` 的 Claude 首稿正文虽有 3924 字，却有 66 处方向公式、174 处物象位置回声和 84 处自我承担回声；主编整章回炉为林彻挡私印、分开原纸与拓纸、把无印纸送往余伯院，正文 1502 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch939-苏挽在.md` 的 Claude 首稿只有 1492 字且残留方向/自指方式公式并缺 review/score；主编整章回炉为苏挽用余伯旧砚验无印白纸，认出北街靛坊十七号箱，正文 1506 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch940-林叙看.md` 的 Claude 首稿虽有 1751 字，却有 4 处自指方式和 67 处物象回声且 review 证据不在正文；主编整章回炉为林叙把箱标、空页与林崇封令分开，追纸并留下十七号箱线索，正文 1523 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch943-苏挽端糖.md` 的 Claude 首稿残留 11 处方向公式、17 处自指方式公式和 52 处物象回声，并保留苏挽×苏挽错误配对；主编整章回炉为苏挽用半块糖换北街靛坊短笺与废井路线，正文 1614 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch944-林彻看林夙.md` 的 Claude 首稿残留 31 处物象位置回声；主编整章回炉为林彻拆开黑线、短笺、拓纸与私印签收，沿雪水追向废井，正文 1507 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch945-林叙等.md` 的 Claude 首稿残留方向、自我修复、自称与物象位置回声；主编整章回炉为林叙以箱底灰、木屑、木扣和空白见证位逼林崇补写失册，正文 1509 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch947-灶边雪.md` 的 Claude 首稿残留方向公式且 frontmatter 工程化；主编整章回炉为苏挽用灶火验蓝蜡、阿湄留鞋印与白纤维、余伯把原纸和拓纸分层，正文 1688 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch948-林彻站.md` 的 Claude 首稿残留 39 处方向公式、27 处自指方式、82 处物象位置和 52 处自称回声；主编拒收公式循环后重写为林彻挡私印签收、林夙带缺角箱板、林叙落第三见证名，正文 1526 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch949-苏挽在.md` 的 Claude 首稿残留方向与物象位置回声且缺 editorial 元数据；主编整章回炉为苏挽并列叶清梧旧账、蓝蜡折痕和东堂签收白纸，写三栏见证并拒绝补名，正文 1585 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch950-林叙看.md` 的 Claude 首稿残留 wall_formula 与物象位置回声且缺 editorial 元数据；主编整章回炉为林叙核对箱板缺口、旧封令缺页与经手时间，落下第三位见证，正文 1507 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch951-林崇看.md` 的 Claude 首稿残留 32 处方向、25 处墙式、86 处物象位置和 40 处自称回声；主编拒收公式循环后重写为林崇核对内库锁、蓝蜡钥匙与旧令缺页，亲自写下开锁事实，正文 1505 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch952-灶边.md` 的 Claude 首稿基础字数不足且残留 46 处物象位置回声；主编整章回炉为林夙、苏挽、阿湄在灶火下验缺页背痕、分离蓝砂纤维，并接住门外沾蓝钥匙，正文 1501 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch953-苏挽端糖.md` 的 Claude 首稿残留方向、不必替、墙式与自称回声；主编整章回炉为苏挽以半糖换东廊证人的钥匙时辰与鞋印，保留原纸和空姓名，正文 1576 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch954-林彻看林夙.md` 的 Claude 首稿只有 1463 字且有 50 处物象位置回声；主编整章回炉为林彻核对林夙手上蓝蜡、钥匙停顿与门内半页，决定不开门并留下手印，正文 1509 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch955-林叙等.md` 的 Claude 首稿仍是旧模板且只有 wall_formula 通过门；主编整章回炉为林叙核验钥匙、半页与两张手印，等钥匙回栏后把开内库责任递给林崇，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch956-林崇信.md` 的 Claude 首稿触发 24 处方向、16 处墙式与 72 处物象位置回声；主编拒收后重写为林崇核对记录、退回王姨娘代写信、要求林彻自写承担，并决定暂不开内库，正文 1501 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch957-灶边雪.md` 的 Claude 首稿触发 51 处物象位置回声；主编重写为林夙在灶边以火验钥匙册缺行、把灰砂/雪印/木屑分栏，并将带半指印的拓纸送进东堂，正文 1589 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch958-林彻站.md` 的 Claude 调度在外层时限内未返回；主编重写为林彻把空栏先送入内库记录、要求三方落名并以柜牌/匣盖异字暂不取物，正文 1762 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch959-苏挽在.md` 的 Claude 首稿虽过基础与公式门，但缺严格编辑元数据且仍是静态动作模板；主编重写为苏挽复验柜牌、匣盖、蓝蜡与纸背淡墨，逼林叙把听见与看见分栏，正文 1553 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch960-林叙看.md` 的 Claude 首稿残留 25 处方向公式、37 处物象位置回声和 18 处自称回声；主编重写为林叙面对林崇私印仍保留空栏，沿旧册断线找出半个“子”字，正文 1483 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch961-林崇看.md` 的 Claude 首稿缺严格编辑元数据，且把林叙未经证明写成撕页人；主编重写为林崇在灶边验重缝红蜡与蓝纤维，只把责任写成待验并交物证给苏挽，正文 1308 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch962-灶边.md` 的 Claude 首稿在 stream 中断前膨胀，触发 133 处方向、309 处物象位置和 229 处自称回声；主编重写为苏挽、林夙、阿湄拆分红蜡/蓝纤维/旧棉布，发现“归西柜”半行，正文 1413 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch963-苏挽端糖.md` 的 Claude 首稿缺有效严格编辑放行且仍围绕旧物象清单；主编重写为苏挽用两块糖换门房的两段时辰，形成纸入与锁响的可追查时间差，正文 1171 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch964-林彻看林夙.md` 的 Claude 调度在外层 1000 秒时限内未返回，目标仍是旧公式稿；主编重写为林彻接两段时辰、与林夙对验旧锁并留下红蜡与蓝纤维新证，正文 1255 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- linter 已扩展拦截 `方向落在/方向不必替/不必替上一世/自己守` 变体；新增 `engine/run_dispatch.py`，独立运行 Claude 与本地发布门。
- 批量工单现在只带目标章相关 cast、前后 hook 与范文章路径，并要求 `review_batch.py --strict-editorial` 通过后才算 PASS。
