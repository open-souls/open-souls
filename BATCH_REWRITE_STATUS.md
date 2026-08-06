# Batch Rewrite Status

Run `python engine/batch_rewrite.py --status` to refresh.

**Total scope**: 876 chapters to bring to gold standard
- 244 §七.1 disease chapters (have real prose, just broken)
- 632 stub chapters (9-line templates, need full write)

**Per dispatch budget** (2 bounded Claude workers; `$12.0` max per job, 420-second Claude timeout; 500-second outer safety window):
- Each job receives only its target chapter prompt and compact context.
- A job is not publishable until the outer runner writes an independent receipt.

## Workflow

1. **范文章 ready**: ch512-不接.md (苏挽 POV, 行为先于意识)
2. **Picker**: `python engine/batch_rewrite.py --pick N` chooses N targets (stubs first, then disease)
3. **Dispatch**: `python engine/batch_rewrite.py --pick N --no-skip-done --no-dry-run` writes dispatch prompts to `prompts/dispatch/ch###.txt`
4. **Run**: `python engine/run_dispatch.py --workers 2 --max-budget-usd 12.0 --effort high` runs bounded `claude -p` jobs and writes independent PASS/BLOCKED receipts to `prompts/.results/`.

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
- [x] ch998-真合前夜.md (alternate branch；林夙 POV 阿湄的信第三行，正文与独立门已修复)
- [x] ch999-真合前拂晓.md (canonical branch；主编复读通过)

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

## 主编复核快照 · 2026-08-04（持续更新）

### 最新后验收快照

- `python engine/batch_rewrite.py --status` 最新为：607 个静态 stub 编号、69 个实际剩余 stub、220 个仅存在于 manifest 而未落盘的编号、356 个唯一 lint 错误号、125 个当前候选文件未过完整发布门。
- `python tools/review_batch.py --strict-editorial ch960-ch1000`：41 章通过，0 章拒发；ch960–ch1000 已形成连续 41/41 绿段。
- ch513、ch514 的 Claude worker 均因超时保持 BLOCKED 且未改文件；主编重写后分别为 1761、1624 字，strict editorial 2/2 通过。
- ch530、ch531 的 Claude worker 均改动了目标但留下公式/元数据问题；主编重写后分别为 1648、1845 字，strict editorial 2/2 通过，方向/墙/物象位置/自指回环均为 0。
- ch532、ch533 的 Claude worker 均改动了目标但留下字数/公式/证据问题；主编重写后分别为 1579、1708 字，strict editorial 2/2 通过，公式与物象位置回环均为 0。
- ch534、ch535 的 Claude worker 分别留下大规模公式回环和超时半成稿；主编重写后分别为 1503、1513 字，strict editorial 2/2 通过，ch535 保留水下线并补齐有效 review/score。
- ch536、ch537 的 Claude worker 分别超时未改、留下短公式半成稿并写出旁支 `ch537-new.md`；主编重写后分别为 1503、1542 字，strict editorial 2/2 通过，未成年安全门通过；旁支原样保留，未作为正文。
- ch538、ch539 的 Claude worker 分别未改目标/误报合法并行目标、以及留下 1323 字公式半成稿；主编重写后分别为 1696、1894 字，strict editorial 2/2 通过，视角边界和水下证据链完成分章。
- ch540 的 Claude worker 完成了目标改写但只留下 1216 字的“看见”清单，缺少有效发布门证据；主编保留糖玉、湿信、车帘与湿墨事实，重写出出水后的证据核对和叶观澜落笔压力，正文 2007 字，strict editorial PASS。
- ch542 的 Claude worker 在 420 秒窗口内 BLOCKED 且未改目标；主编重写为牛阿大、林窈、老仆在灶边分开岸绳信号、冬账旧纸与“未见人影”，正文 1862 字，strict editorial PASS。
- ch543、ch544 的 Claude worker 均改动目标但留下旧模板回环或半成稿问题；主编分别重写为苏挽把糖水、岸绳与灶后残纸分栏入账，以及林彻在林崇追问下把听闻与亲见分栏并落名，正文 1666、1788 字，strict editorial 2/2 通过。
- ch545、ch546 的 Claude worker 均改动目标但留下公式/安全/元数据问题；主编分别重写为林叙拆分水底见闻并把署名留给林夙，以及林崇拒绝家印替水下作证、以亲见内容发出回信，正文 1636、1571 字，strict editorial 2/2 通过。
- ch547、ch548 的 Claude worker 分别留下 31 处方向/79 处物象回环，以及超时未改；主编分别重写为灶边雪水保护残纸、原件抄件分送，以及余伯与宋观山核对清梧旧页来处，正文 1552、1548 字，strict editorial 2/2 通过。
- ch549、ch550 的 Claude worker 分别超时未改、以及留下 129 处物象位置回环；主编分别重写为苏挽留在药庐分袋保存四类待验物，以及林叙见林夙与林崇围绕铜扣、秤盘、家印和空栏落名，正文 1517、1503 字，strict editorial 2/2 通过。
- ch551、ch553 的 Claude worker 分别自报清理但仍留下 4 处方向/77 处物象回环，以及留下 31 处物象槽位；主编分别保留铜扣、清梧南城传言并登记“未验”，以及重写清梧旧页白面、南城路线与水下纸角，正文 1556、1510 字，strict editorial 2/2 通过。
- ch554、ch555 的 Claude worker 分别超时未改、以及基础门通过但只留下 1120 字并残留方向公式；主编分别重写叶清梧在南城白墙前登场、叶观澜用算盘分三封不同范围的信，正文 1556、1506 字，strict editorial 2/2 通过。
- ch556、ch557 的 Claude worker 分别超时未改、以及改动后仍留下 31 处方向/66 处物象/19 处自我承担回环；主编分别重写林崇收到叶观澜分级通知并拆分三份记录、余伯恢复旧账“还”字并核对两条来源，正文 1509、1503 字，strict editorial 2/2 通过；“她姓姜，他也是姜”保留为未并案悬念。
- ch558、ch559 的 Claude worker 均标记 BLOCKED；ch558 未改目标，主编整章回炉为林彻在院门核对三类来源、听王姨娘补充叶清梧与旧秤见闻并为亲见落名，正文 1554 字；ch559 留下可读正文但缺 review 证据，主编补齐叶清梧入账与林崇责任落点，正文 1988 字；strict editorial 2/2 通过。
- ch560、ch563 的 Claude worker 均标记 BLOCKED；ch560 未留下改稿且目标曾被删除，主编恢复并整章回炉为林叙拆分林崇回执、南城路线和水下纸角，正文 1544 字；ch563 留下可读正文但缺 review，主编补齐余伯停在半字、封面可拆和“下一位来写”的证据，正文 2029 字；strict editorial 2/2 通过。
- ch564、ch565 的 Claude worker 均超时未改；主编分别回炉为叶观澜划掉“阿湄亲启”并写明可退送达单、阿湄让苏挽代读前两页并留下最后一页，正文 1535、1610 字；strict editorial 2/2 通过。
- ch566、ch567 的 Claude worker 均改动但留下不足 1500 字的半成稿；主编分别重写林崇核对苓字与旧簪、划掉林夙收件人并交还拆信决定，以及林夙与苏挽核对苓字、划痕和阿湄末页，正文 1516、1623 字；strict editorial 2/2 通过。
- ch568、ch569 的 Claude worker 分别超时未改、以及留下 1454 字且缺 review/score 的半成稿；主编分别重写宋观山核对双玉和第二来源、决定明日去山门外，以及苏挽分栏抄“叶清梧·还”、接过余伯的笔并分开保管帕与糖纸，正文 1511、1503 字；strict editorial 2/2 通过。
- ch570、ch572 的 Claude worker 均改动但留下不足 1500 字或公式残留的半成稿；主编分别扩写余伯补回“梧”字、分离双玉与身份结论，以及整章回炉为牛阿大在灶灰中捡焦纸、核对“还”字并送余伯，正文 1500、1501 字；strict editorial 2/2 通过。
- ch573 的 Claude worker 自报完成但留下 58 处物象槽位回声且正文仅 1471 字；主编拒收旧模板，重写为叶清梧把糖纸、焦纸、冬账和苏挽抄件分开登记，正文 1678 字，strict editorial PASS。
- ch574 的 Claude worker 超时并删除目标文件；主编恢复目标并重写为林彻收到三份“还”字抄件、拒绝替林夙虚构收件人，正文 1736 字，strict editorial PASS；Claude 回执保留 BLOCKED。
- ch575、ch576 的 Claude worker 均改动目标但留下公式回环或元数据失败；主编分别重写为林叙等林夙回话、核对焦纸封袋和林窈半字见闻，以及林崇拒绝用家印替“还”字确认收件人并亲自发出未验信，正文 1673、1579 字，strict editorial 2/2 通过。
- ch577 的 Claude worker 自报完成但独立门抓到 67 处物象回环和 24 处自指回环；主编重写为沈疏桐核对旧环、两份门房记录和赤渊斋门柱弧痕，正文 1760 字，strict editorial PASS。
- ch578 的 Claude worker 超时未留下有效改稿；主编重写余伯把六十二年旧笔交给苏挽，要求她先记来源、交接与空栏，正文 1614 字，strict editorial PASS。
- ch579 的 Claude worker 留下 1385 字身份揭示半稿且缺 evidence review；主编重写为苏挽写下“我姓苏，我也姓姜”，沈疏桐同步核对铜环与门柱旧痕，正文 1646 字，strict editorial PASS。
- ch580 的 Claude worker 留下 104 处物象回环；主编重写为林叙处理苏挽“原件”纸条、林崇确认来源、林夙在北门落名，正文 1582 字，strict editorial PASS。
- ch583 的 Claude worker 留下 51 处物象回环并保留苏挽自配对；主编重写为苏挽端糖核对北门车声、木匣和叶府青木牌，正文 1674 字，strict editorial PASS。
- ch585 的 Claude worker 留下 56 处方向、102 处物象和 68 处自指回环；主编重写为林叙等北门回执、拆分车牌/糖纸/未验乘客，正文 1551 字，strict editorial PASS。
- ch586 的 Claude worker 超时后留下 135 处物象回环半稿；主编重写为叶观澜下车、交接无封木匣、确认车内咳声但拒绝补出乘客身份，正文 1701 字，strict editorial PASS。
- ch587 的 Claude worker 超时未改目标且保留错误自配对；主编重写为林夙、苏挽、阿湄和叶观澜车马记录在谷口分栏落名，正文 1506 字，strict editorial PASS。
- ch588 的 Claude worker 超时未改目标；主编重写为林彻面对王姨娘传话、周平北门抄件和送达见证栏，正文 1538 字，strict editorial PASS。
- ch589 的 Claude worker 留下 1318 字半稿；主编修复一次误写的外层路径并重写为叶观澜三步核对车马、木匣与“还”字，正文 1573 字，strict editorial PASS。
- ch960–ch973 已形成连续 14/14 绿段：正文指标依次为 1729、1651、2187、1521、1611、1516、1603、1507、1512、1500、1502、1597、2229、1500。
- 这组数据覆盖的是本轮主编复核范围，不是全书市场证明；旧条目中 ch960–ch973 的旧字数记录已被本节最新实测覆盖。

- 机器扫描：1330 个章文件；559 章 ERROR，121 章 WARN。
- `_STUB_MANIFEST.json` 当前使用 `chapter_numbers`，共 607 个 stub 编号；调度器已兼容该格式。
- `python engine/batch_rewrite.py --status` 同时报告静态 stub 总数、真实落盘的 `stubs_remaining` 与 manifest-only 的 `stubs_missing`，避免把不存在的章节伪装成可派发任务；当前为 607 个静态 stub 编号、实际剩余 stub 49 个、manifest-only 编号 220 个、354 个唯一 lint 错误号，其中 105 个当前候选文件仍未过完整发布门。扩展公式门新增捕获了旧稿变体，数字变化按独立门结果记录。本轮主编复核范围已扩至 ch1000；ch960–ch1000、ch513–ch520、ch523–ch525、ch527–ch540、ch542–ch589、ch642–ch650、ch671–ch800 已通过 1500 字发布门与 strict editorial 联合门；ch651、ch652、ch656 尚未形成绿段声明。
- runner 的受保护快照现覆盖目标章节所在目录，可拦截 Claude 在目标旁写 `chNNN-new.md` 等 sibling 草稿；并行批次的合法目标另行列入允许集合，避免两个目标互相误报。
- 并行 runner 现在把同一批次的合法目标集合传入 side-effect gate，避免 ch538 因 ch539 的合法并行写入被误报；新增并行授权回归后 `tests/test_run_dispatch.py` 为 8/8。
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
- `ch965-林叙等.md` 的 Claude 首稿引入未铺垫的收骨情节，并触碰目标外音频/缓存；主编重写为林叙等林彻门边记录、分发副本与保留正式账的责任冲突，正文 1087 汉字，最终 lint、公式扫描与 strict editorial review PASS，side_effects 原样保留，Claude 回执保留 BLOCKED。
- `ch966-林崇信.md` 的 Claude 首稿触发 38 处方向、5 处墙式、63 处物象和 20 处自称回声，并产生越权音频副作用；主编重写为林崇退回王姨娘代写信、让林彻亲自落下未开柜责任，正文 1226 汉字，最终 lint、公式扫描与 strict editorial review PASS，side_effects 原样保留，Claude 回执保留 BLOCKED。
- linter 已扩展拦截 `方向落在/方向不必替/不必替上一世/自己守` 变体；新增 `engine/run_dispatch.py`，独立运行 Claude 与本地发布门。
- 批量工单现在只带目标章相关 cast、前后 hook 与范文章路径，并要求 `review_batch.py --strict-editorial` 通过后才算 PASS。
- 最新主编复核范围已扩至 ch1000：ch967–ch1000 均已由主编独立复读并通过 strict prose、安全、元数据与公式门；其中 ch979–ch1000 另已通过 1500 字发布门，ch967–ch978 虽已通过内容硬线但仍是短章候选，剩余章节继续清理。
- `ch977-灶边雪.md` 的 Claude 首稿残留 52 处方向、2 处墙式、79 处物象和 67 处自称回声；主编重写为灶边接收说明信副本、核对折缝、原件留东堂，正文 834 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch979-苏挽在.md` 的 Claude 首稿虽改写目标文件，仍残留方向公式与机械物象循环；主编重写并补足送纸口供，形成苏挽在灶边核对折缝、红蜡、蓝纤维与辰时二刻回纸，正文 1502 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch980-林叙看.md` 的 Claude 首稿形式门误放行但正文循环堆叠“袖底/折痕/那一截”，主编重写并补足旧档物证，将回纸的到达时辰、送达范围、经手人空栏与退婚旧档切成下一线，正文 1503 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch981-林崇看.md` 的 Claude 首稿膨胀为 8419 字并重复方向/位置/旧印动作；主编压缩为林崇开卷、林彻看原件、林夙看抄件的证据场景，正文 1532 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch982-灶边.md` 的 Claude 首稿仍是灶/烟/栗子/搁回旧模板；主编重写为退婚旧档抄条送灶边、林夙为见闻落名、水痕待验，正文 1533 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch983-苏挽端糖.md` 的 Claude 首稿未修改目标文件并扫描出 37 处方向公式、76 处物象槽位；主编重写为端糖询问门房、校验辰时初与东堂辰时三刻，正文 1539 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch984-林彻看林夙.md` 的 Claude 首稿虽达字数但仍有 46 处方向/位置回声和 48 处自称回声；主编重写为林彻、林夙分别确认原件与抄件，并把门房时辰分卷，正文 1668 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch985-林叙等.md` 的 Claude 首稿仍残留方向/不必替/物象位置循环；主编重写为林叙接收三份见闻、等待漏刻回纸并保持三袋分卷，正文 1501 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch986-林崇信.md` 的 Claude 首稿被 wall_formula 与物象槽位门拦截；主编重写为林崇审阅漏刻回纸、拒绝私印定性并写分卷责任信，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch987-灶边雪.md` 的 Claude 首稿未在外层 runner 500 秒窗口内返回，确认孤儿子进程后终止；主编重写为灶边接收分卷信副本、退婚书抄件和林夙送件凭条，正文 1561 汉字，最终 lint、公式扫描与 strict editorial review PASS，人工收据保留 BLOCKED。
- `ch988-林彻站.md` 的 Claude 首稿仍有 21 处墙式回环、75 处物象位置回声；主编重写为林彻读取灶边回纸、分别落名并站到东堂门边等直接送达者，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch989-苏挽在.md` 的 Claude 首稿只有 1151 字且残留方向、墙和物象槽位回声；主编重写为苏挽接收林彻门边补记，分开“未见门开”和“原件未见”，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch990-林叙看.md` 的 Claude 首稿膨胀到 12202 字并触发方向/不必替/墙式/物象回声；主编重写为林叙整理四份索引并把“等候结束时刻”退回见闻人，正文 1533 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch991-林崇看.md` 的 Claude 首稿仍有方向与物象槽位循环；主编重写为林崇审核四袋索引、写明空栏不是漏写，并签发灶边副本，正文 1525 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch992-灶边.md` 的 Claude 首稿触发 79 处方向、19 处墙式、197 处物象槽位和 92 处自称回声；主编重写为灶边接收两只副本袋并逐项保留原件未到，正文 1535 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch993-苏挽端糖.md` 的 Claude 调度在外层 500 秒窗口内未形成收据，目标未改且原稿触发 37 处方向、14 处不必替、76 处物象槽位和 35 处自称回声；主编重写为苏挽把糖、人情与四源索引分开，林叙只为自己见过的副本落名，正文 1651 汉字，最终 lint、公式扫描与 strict editorial review PASS，人工收据保留 BLOCKED。
- `ch994-林彻看林夙.md` 的 Claude 调度在外层 500 秒窗口内未形成收据，目标曾被改到 1385 字且缺合格 review/score；主编保留豁口与十三岁接盏素材，重写为叶清梧抄页、林崇秤砣与林彻落名的冲突，正文 1752 汉字，最终 lint、公式扫描与 strict editorial review PASS，人工收据保留 BLOCKED。
- `ch995-林叙等.md` 的 Claude 首稿触发 23 处方向、3 处墙式和 68 处物象槽位；主编重写为林叙等待林彻门边补记，拆开四源索引、送达路径和“未见”范围，正文 1511 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch996-林崇信.md` 的 Claude 调度在 420 秒窗口内未返回有效首稿；主编重写为林崇收到五栏补问单，拒绝私印补出原件责任，正式写下原册留东堂、副本送灶边和空白保留的分卷信，正文 1706 汉字，最终 lint、公式扫描与 strict editorial review PASS，人工收据保留 BLOCKED。
- `ch997-灶边雪.md` 的 Claude 首稿虽达1503字但保留苏挽×苏挽自配对且与 beat 不一致；主编重写为灶边接收正式分卷副本、王姨娘无落款残纸、雪水范围和拓记交接，正文 1593 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch998-林彻站.md` 的 Claude 首稿残留 64 处物象槽位和 19 处自称回声；主编重写为林彻站在东堂门槛外，要求取册条拆出钥匙交接、见证人和“听见钥匙但未见柜门”的范围，正文 1654 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch999-真合前拂晓.md` 的 Claude 调度在 420 秒窗口内未返回且目标未变；主编复读现有成稿，确认苏挽等待、阿湄传话、林夙开信的事件链与正文 review 证据一致，正文 1654 汉字，最终 lint、公式扫描与 strict editorial review PASS，保留原稿。
- `ch1000-撕账.md` 的 Claude 首稿公式门通过但正文只有 1408 字且缺 review；主编补足三本账的责任分层和归隐谷三死讯转折，正文 1624 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- duplicate branch audit：`ch998-真合前夜.md` 与 `ch999-苏挽在.md` 标记为 `branch: alternate`，保留文件但不参与 canonical 选章；主编分别重写至 1521 字并通过 strict prose、安全、元数据与公式门，收据见 `prompts/.results/ch998-alternate.md` 与 `ch999-alternate.md`。
- `ch975-林叙等.md` 的 Claude 首稿丢失 frontmatter且残留方向公式，并把前章责任重新置空；主编重写为林叙接收已落名副本、另列取药时辰，正文 873 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch976-林崇信.md` 的 Claude 首稿膨胀并残留 7 处方向、26 处墙式和 100 处物象回声，缺合格 review/score；主编重写为王姨娘说明信、老仆取药时辰、林彻未开见证三栏交割，正文 796 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch973-苏挽端糖.md` 的 Claude 首稿残留 15 处方向回环和 38 处物象槽位；主编重写为苏挽端糖核对来客簿，把取药时辰与送信事实分开，正文 823 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch974-林彻看林夙.md` 的 Claude 首稿残留 45 处方向、7 处自我修复、99 处物象和 36 处自称回声；主编重写为林彻与林夙分别落名、林崇封存私印，正文 1045 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch971-林崇看.md` 的 Claude 调用成功但目标 hash 未变，旧模板仍有 37 处方向、16 处自我修复、76 处物象和 35 处自称回声；主编重写为林崇审无经手人准取旧信，正文 1080 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch972-灶边.md` 的原稿只有 89 字且无 frontmatter；Claude 扩写后仍残留 3 处方向、35 处物象回声并缺合格 review/hook，主编重写为灶边保存旧信副本、四栏留痕并端糖去药庐，正文 905 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch969-苏挽在.md` 的 Claude 首稿虽然整章改写，却残留 60 处物象槽位和 13 处方向回环；主编重写为药庐低损比对蓝丝拓痕，保留“颜色相近，不能定根”的限制，正文 1065 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch970-林叙看.md` 的 Claude 首稿仍残留方向、物象和自称回声；主编重写为东堂正式归账、私印不补名、林夙带走副本而不取原件，正文 1093 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch590-林叙看.md` 的 Claude worker 返回 BLOCKED：目标仍是旧模板，命中 37 处方向、76 处物象位置和 35 处自称回环；主编重写为林叙拆分北门车马抄件、木匣回执和冬账第七页，林夙亲见空栏并落名，正文 1548 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch593-苏挽端糖.md` 的 Claude worker 虽改出 1879 字首稿，但仍命中物象槽位并缺合格 metadata；主编重写为苏挽在空栏写下“苏挽在”，再把旧笔、糖纸、帕子与两种来源的糖分开记录，端糖到山门等待收件人，正文 1550 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch594-林崇那一步.md` 的 Claude worker 返回 BLOCKED，半成稿仍命中 3 处方向、18 处墙式和 137 处物象回环；主编重写为林崇拒绝用家印补出收件人，和林彻分卷后亲自承担送达，正文 1569 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch595-叶观澜记那笔.md` 的 Claude worker 超时并留下 1096 字、缺 metadata 的半成稿；主编重写为叶观澜比对旧信与冬账笔势，记录“相似”而不把它写成身份，正文 1511 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch597-林夙复盘之眼开.md` 的 Claude worker 未改目标并保留 37 处方向、76 处物象、35 处自称回环；主编重写为林夙按时间线重排苏挽、阿湄的见闻，让“复盘之眼”识别交接后的空处，正文 1534 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch598-林崇听见.md` 的 Claude worker 写出 1428 字但仍命中 54 处物象槽位且缺严格元数据；主编重写为林崇把钥匙、门闩、脚步、叩门与王姨娘推断分栏，正文 1514 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch599-叶观澜受那一下.md` 的 Claude worker 改写后仍命中 20 处方向与 46 处物象回环；主编保留“叶家大房来帖”压力，重写为叶观澜承认帖子送达但拒绝替车中人和木匣认领，正文 1544 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch600-林叙看.md` 的 Claude worker 仍命中 40 处方向、90 处物象和 32 处自称回环；主编重写为林叙核对叶家帖子来源，交给林夙阅读但不把阅读写成收取，正文 1554 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch601-林崇看.md` 的 Claude worker 在外层超时，留下明确记录的 `.bak` 旁支并改出公式半成稿；主编保留旁支供审计，重写为林崇发现旧账“林夙收”疑似后添，分开墨色、传言和原页，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch602-灶边.md` 的 Claude worker 同批超时并留下同一 `.bak` side effect；主编重写为牛阿大、林窈、老仆分辨灶灰残纸、糖纸与红釉碎片，正文 1503 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch603-叶观澜看林窈.md` 的 Claude worker 虽改写目标仍留 8 处方向公式、缺 review/score 且 cast 漏列林窈；主编重写为林窈在成人陪同下仅交付糖纸，叶观澜和苏挽明确她不为车中人或旧账收件人作证，正文 1502 汉字，最终 lint、公式、安全与 strict editorial review PASS。
- `ch604-林彻看林夙.md` 的 Claude worker 留下 44 处方向、92 处物象和 48 处自称回环；主编重写为林彻与林夙核对旧账后添字，确认认得字形不等于认领事件，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch605-林叙等.md` 的 Claude worker 未改目标，旧模板仍命中 37 处方向、76 处物象和 35 处自称回环；主编重写为林叙等待灶灰、药房和旧档三条有时辰的回件，正文 1501 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch606-林崇信.md` 的 Claude worker 虽完成首稿但缺严格 metadata；主编重写为林崇发出一封只写见闻、不代林夙认领的信，余伯记录送达，正文 1545 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch607-灶边雪.md` 的 Claude worker 留下 83 处物象槽位回环；主编重写为雪水改变林崇信件回执的纸角，明确湿痕能证明经过雪地、不能证明送件人，正文 1502 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch608-林彻站.md` 的 Claude worker 超时且仍有 31 处物象回环；主编重写为林彻在门槛外区分纸套送达、副本阅读和原信未收，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch609-阿湄接信.md` 的 Claude 首稿触发未成年亲密硬线、4 处 wall_formula 与严格正文门；主编重写为阿湄在叶观澜、林夙可见范围内接收七年前旧信，分开原件、附页、副本与回执，并拒绝由信件替她补出身份，正文 1534 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch610-林叙看.md` 的 Claude 首稿未改变旧模板并保留公式回声；主编重写为林叙接收阿湄副本，逐层区分旧信、今日日附页、回执、原件与冬账，等待药簿和旧柜回件，正文 1535 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch612-叶观澜最后看.md` 的 Claude worker 超时并留下可审计的 `temp_ch612.ps1` 旁支，首稿命中 26 处方向、58 处物象和 82 处自称回声；主编保留旁支，重写为叶观澜核对十三岁旧账、兰线帕与取档条，明确相似不能替空栏补名，正文 1608 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，人工收据保留 BLOCKED。
- `ch613-林窈不哭.md` 的 Claude 首稿虽完成整章仍触发方向公式；主编重写为林窈在灶边接收旧账副本，安全地分开糖纸、欠条和磨刀石，哭声落在山门外并保留欠条交接，正文 1554 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch614-林彻看林夙.md` 的 Claude 首稿残留 19 处方向、66 处物象和 34 处自称回声，且 hook 沿用上一章模板；主编重写为林彻在父案前把未到、未交、未认三栏分开，并将退回条送往东堂，正文 1610 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch615-林叙等.md` 的 Claude 首稿只有约 1306 字并残留墙式与自称回声；主编重写为林叙分开林彻副页、药庐回条、林窈欠条和牛阿大送食，最后亲自去东堂问林夙落名，正文 1566 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch616-林崇信.md` 的 Claude 首稿只有约 917 字、残留 12 处方向公式且 hook 重复；主编重写为林崇核对东堂退回条和林叙副页，写一封不盖家印、只陈述所见并等林夙亲拆的信，正文 1570 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch617-凌朔接沈疏桐.md` 的 Claude worker 未改目标，旧稿命中 37 处方向、76 处物象和 35 处自称回声；主编重写为北桥接人、发现跟踪者、换水渠路线并保留林夙未解释的新信，正文 1741 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch618-林彻站.md` 的 Claude 首稿仍有 15 处方向、42 处物象回声且正文只有 1138 字；主编重写为林彻核对林夙出门口信，带退回条与青玉佩到山门，在门外等待而不代签，正文 1593 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch619-苏挽在.md` 的 Claude 首稿命中 7 处 §七.1 公式、7 处方向和 32 处物象回声，正文只有 1402 字；主编重写为苏挽在余伯院里分开叶清梧旧账、兰帕、糖纸和药庐回条，明确要求先看原页，正文 1808 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch620-林叙看.md` 的 Claude 首稿虽然很长但命中 39 处方向、84 处物象和墙式回声；主编重写为林叙在东堂分开三份回条、青玉佩和林崇白线信，确认林夙不在不能成为代拆理由，正文 1588 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch621-林崇看.md` 的 Claude 首稿通过基础 lint 但命中 62 处物象回环且 hook 重复；主编重写为林崇用旧秤校平纸袋、封存红泥和收回家印，只认林夙本人落名，正文 1589 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch623-苏挽端糖.md` 的 Claude 首稿命中 37 处方向、76 处物象和 35 处自称回声，正文只有 1387 字；主编重写为苏挽把药庐白糖送到山门，记录门房代存、收件人待定与林窈糖纸，正文 1527 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch624-林彻看林夙.md` 的 Claude 首稿命中 55 处方向、60 处物象和 48 处自称回声，正文只有 1431 字；主编重写为林彻与林夙当面核对短腿凳、山门回条和未收玉佩，林崇把亲缘压力与正式交接分开，正文 1509 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch625-林叙等.md` 的 Claude worker 超时且未改目标，旧模板命中 37 处方向、76 处物象和 35 处自称回声；主编重写为林叙等林夙回信、药庐回条和欠条回收，设定明日午前截止并停止重复催问，正文 1526 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，人工收据保留 BLOCKED。
- `ch626-阿湄陪着走.md` 的 Claude 首稿基础 lint 通过但只有 1171 字、review 缺证据；主编重写为阿湄陪苏挽完成药庐回条和林窈糖丸交付，随后在车帘前回应叶观澜，正文 1509 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch627-巷口一顶车.md` 的 Claude 首稿命中 40 处方向、51 处物象槽位和 22 处自称回环；主编重写车件、回条与六十二年前半页的交接，补足正文并保留空白不认收，正文 1875 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch628-余伯收尾.md` 的 Claude 首稿基础 lint 与公式扫描通过但 strict review 缺正文证据；主编校正 review 引文并核对余伯、林夙、叶观澜旧页线，保留裴无咎门外钩子，正文 1549 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch629-裴无咎来找.md` 的 Claude 流在 269 秒时断流且未改目标；主编重写裴无咎入账房、裴家退回条与西仓旧档线，保留玩笑下的认真并把风险落在可查动作上，正文 1757 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch630-牛阿大还债.md` 的 Claude worker 在 420 秒窗口内未形成有效产出且未改目标；主编重写牛阿大还米还药、林窈拒绝担保与名字入账，保留下一章山门回条钩子，正文 1597 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch633-苏挽端糖.md` 的 Claude 首稿留下 3 处方向公式、正文 1497 字且 review 不足；主编重写苏挽端糖的药庐交付、余伯原页记录与阿湄门外承接，正文 1513 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch634-阿湄再念.md` 的 Claude 首稿基础 lint 与公式扫描通过但 strict review 缺正文证据且正文公式化严重；主编重写阿湄分开旧称、名字、空栏与糖玉，保留林窈交给林夙的回条钩子，正文 1816 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch635-林叙等.md` 的 Claude 首稿虽有 2236 字但仍命中 12 处方向、52 处物象槽位且缺 review；主编重构林窈递回条、林叙等本人、牛阿大核物与代送边界，正文 1934 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch636-林崇信.md` 的 Claude 首稿命中 31 处方向、75 处物象与 31 处自称回环且缺 review/score；主编重写林崇的秤盘、分信与林夙本人接纸，正文 1647 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch637-苏挽最后写.md` 的 Claude 新提示后方向公式降至 1 处，但仍有 6 处 wall_formula、34 处物象槽位且 review 缺失；主编重写皂衣信、林窈回条与苏挽最后一行记录，正文 1760 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch638-林彻站.md` 的 Claude 新提示后方向公式降至 4 处，但仍有 5 处 wall_formula、37 处物象槽位且正文不足 1500；主编重写林彻核对冬账缺页、周平副本与王姨娘旧帕，正文 1664 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch639-清梧走了.md` 的 Claude worker 在 420 秒窗口内留下根目录 `_c639.txt`、`_c639_check.txt`、`_c639_hits.txt` side effects，正文只差长度且缺 review/score；主编保留审计旁支，重写并补足林夙确认叶清梧离开、空信与不烧选择，正文 1547 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch640-林叙看.md` 的 Claude 首稿命中 11 处方向、11 处 wall_formula 和 37 处物象槽位；主编重写林叙读信、林崇要求与副本分发，正文 1660 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch642-灶边.md` 的 Claude 首稿仍命中 25 处方向、8 处 wall_formula 和 52 处物象槽位，且正文/metadata 未达门；主编重写牛阿大核对米药、灶灰半字与林窈口信，正文 1611 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch643-苏挽接阿湄.md` 的 Claude 首稿方向公式降到 2 处但仍有 3 处 wall_formula 且缺 review/score；主编重写苏挽接阿湄的空锦囊、药碗、糖纸与待本人回条，正文 1778 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch644-林窈不让走.md` 的 Claude 首稿仍命中 10 处 wall_formula，且未成年边界需单独复核；主编重写林窈在东院拽住苏挽袖口、用明早菜馅包子留人，移除含糊身体描写并通过安全门，正文 1586 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch645-凌朔站到那一边.md` 的 Claude worker 在 420 秒窗口内未形成有效改稿，目标保留旧模板并命中 31 处 self_claim；主编重写赤渊收回旧账与印、凌朔在交割册留下选择并公开站到林夙一边，正文 1558 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch646-林崇信.md` 的 Claude 首稿有 45 处方向回环和 64 处物象位置回环；主编重写为林崇在余伯院收回家印、在信尾写下“林崇亲见”，并让苏挽带走余伯的笔，正文 1528 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch647-巷口一张脸.md` 的 Claude worker 在 420 秒窗口内未形成有效改稿且旧稿保留自配对；主编重写为林夙在巷口等苏挽、确认林崇落名的信并尊重她本人拆信，正文 1557 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch648-林彻站.md` 的 Claude 首稿基础 lint 与公式扫描通过但缺严格 review evidence；主编独立复读并补证据后保留其“拒绝追回林崇信、在灶边消息前等待”的现场，正文 1627 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch649-那半页.md` 的 Claude 首稿命中 7 处方向、3 处 wall_formula、39 处物象槽位；主编重写为苏挽带信、阿湄交半页旧账、林夙拒绝用相似笔迹补出身份，正文 1588 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch650-林叙看.md` 的 Claude 首稿仍有 3 处第二道墙且缺 review；主编重写为林叙不再用蒸糕换林崇认可，林夙接下未入家账的包裹，正文 1633 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch653-一兜.md` 的 Claude worker 超时并保留旧模板；主编重写为林夙在山门公开报姓名、余伯以凉茶见证、苏挽从桂花糖香确认“我看见了”，正文 1671 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch654-林彻看林夙.md` 的 Claude 首稿命中 20 处方向、2 处 wall_formula、45 处物象位置，并越权生成 `ch655-暗处.md`；主编重写林夙拒绝旧茶与磨墨安排、林崇交出无家印旧信，正文 1622 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，旁支原样保留。
- `ch655-林叙等.md` 的 Claude 首稿基础 lint 与公式扫描通过但严格 metadata 未过，并越权生成 `ch655-暗处.md`；主编重写林叙把牛阿大的新账和林窈的空栏交还本人，正文 1555 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，旁支原样保留。
- `ch656-糖纸.md` 的 Claude 首稿基础 lint 与公式扫描通过但严格 metadata 未过；主编重写为林窈隔门回应林夙、打开门却保留写账选择，正文 1814 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch657-灶边雪.md` 的 Claude 首稿命中 15 处方向句式、26 处自我承担回环并缺严格 metadata；主编重写为老仆与牛阿大在灶房分工、牛阿大留下自己的账字并把热粥送往东院，正文 1961 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch658-林彻站.md` 的 Claude 首稿命中 4 处自指解释墙、51 处物象位置回环并缺严格 metadata；主编重写为林彻记录送信泥痕、把苏挽旧帕送回原主、封存无名信，正文 1629 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch659-信.md` 的 Claude 首稿命中 2 处自指解释墙并缺严格 metadata；主编重写为沈疏桐拿原信追问林夙，把赤渊斋第三根柱的旧死局改成可量取的裂缝与经手记录，正文 1712 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch660-林叙看.md` 的 Claude 首稿未改目标，保留 37 处方向、16 处自我修复、76 处物象和 35 处自称回环，并缺严格 metadata；主编重写为林叙分栏记录待收纸套、赤渊信与苏挽回条，林崇的家印不再替林夙签收，正文 1625 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch663-名字.md` 的 Claude 首稿基础 lint 与公式扫描通过但严格 metadata 未过；主编重写为林窈在旧账空栏区分记忆与可核原页，隔门念出“苓”并把名字留给自己记录，正文 1573 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch664-裂痕.md` 的 Claude 正文通过基础文笔和公式门但严格 metadata 缺 review；主编复读后保留叶观澜在半页背面由“收件位”转为亲自发信的关键选择，补齐证据型 review，正文 1870 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch665-合.md` 的 Claude 首稿命中 5 处第二道墙、14 处自指解释和 52 处物象回环，且超出目标长度；主编重写为苏挽、阿湄、林窈分别交回条、改名纸与记忆说明，林夙只合并纸页不合并证言，末尾由余伯发现旧账未被擦掉的字，正文 1641 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch667-两把.md` 的 Claude 正文与公式门通过但严格 metadata 缺 review，且首稿保留章号交叉引用和轻微模板化解释；主编重写为苏挽交付未开锋新刃、阿湄核对旧刀后决定带走，并把林窈糖纸作为独立回条转交，正文 1595 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch668-纸.md` 的 Claude 首稿命中 3 处自指解释墙、正文仅 1227 字且缺严格 metadata；主编重写为十三岁林叙在门房登记未拆青纸信、走到南桥交给凌朔并记录布套和回件责任，正文 1591 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch669-车.md` 的 Claude 正文与公式门通过但严格 metadata 未过，且首稿仍有章号引用、车题未形成完整事件；主编重写为凌朔接信后查门外空车，分开车案与信案，留下车辕、青布、手印和经手人记录，正文 1614 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch670-南道.md` 的 Claude 超时未改目标，旧稿正文 1217 字并有大段方向/自我循环；主编重写为阿湄带两把刀走南道，发现空车与缺指车夫见闻后不追人，留下标记并把记录交回凌朔与苏挽，正文 1689 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS。
- `ch671-相看.md` 的 Claude 首稿命中 31 处物象位置回声且用占位钩子收尾；主编重写为林夙与叶观澜第一次正面相看，叶观澜叫出名字，林夙要求当面写清旧信来处，并由苏挽接住次日查账安排，正文 1813 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch672-名字.md` 的 Claude 首稿命中 5 处墙式公式且重复呼唤名字；主编重写为叶观澜拆下残缺封泥、分开叶清梧半页与新记录，把旧信改成可核验的证词并交出后库钥匙，正文 1807 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch673-对赌.md` 的 Claude 首稿自报 1531 字但独立门实际仅 1250 字且缺合格 review；主编重写为林夙用旧页、钥匙和记录设赌，叶观澜把钥匙交到可记录的桌面，苏挽在赌局定案前赶到，正文 1874 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch674-观局.md` 的 Claude 未实际改目标且旧模板命中 19 处自称回环；主编重写为苏挽把赌局拆成旧纸、封泥、钥匙三栏，先问叶观澜并把带活口条件的纸条送给阿湄，正文 1617 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch675-那一瞬.md` 的 Claude 首稿仍是位置与动作回环且 frontmatter 堆叠章号；主编重写为阿湄带着苏挽的问回门，确认第三柜物证后让第二刀割开叶观澜左肩袖缝，不取命、不替赌局判输赢，正文 1666 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch676-血痕.md` 的 Claude 首稿命中 4 处墙式与 39 处物象槽位；主编重写为阿湄刀口松开叶观澜袖内旧缝，掉出“第三柜/左二格/不取原册”薄纸，叶观澜先登记伤和物证，再接受止血，正文 1578 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch677-候他.md` 的 Claude 未改目标且旧稿全是位置回环；主编重写为林夙与苏挽核对后库旧图、第三柜旧牌与现门尺寸，把“未见门开”写入记录并等叶观澜落子，正文 1511 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch678-落子.md` 的 Claude 调度在章节时限后失败且目标仍是旧模板；主编重写为叶观澜把旧图、薄纸、柜牌和钥匙分开落名，明确由余伯见证开门、林夙先看原页，正文 1530 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch679-止步.md` 的 Claude 首稿仍是旧模板，主编重写为林夙在后库门槛外拒绝无记录进入，余伯验新柜牌、门缝灰与未取原册，正文 1641 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch680-替问.md` 的 Claude 首稿虽自报 2481 字，但独立复读抓到位置/方向/自己回声并与 ch679 现场重复；主编重写为苏挽分开新牌、旧图、门槛灰、伤册和叶观澜的待查名字，最后把“叶观澜还剩几张牌”交给林夙，正文 1661 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch681-三张.md` 的 canonical 稿仍是位置/自己回环；主编独立重写为林夙把旧页、袖口伤和名册末页拆成三项未决，苏挽只记可核验项，正文 1571 汉字，最终 lint、公式扫描与 strict editorial review PASS。
- `ch682-灶边.md` 的 Claude 首稿虽有 1734 字但命中 12 处方向、4 处墙式和 39 处物象回声；主编重写为老仆把写给牛阿大的信交到灶房，林窈带来第七页抄件，牛阿大亲手落名并留下叶清梧旧勺证词，正文 1548 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch683-翻末.md` 的 Claude 首稿实际仅 1158 字且命中 27 处“自己”回声；主编重写为叶观澜在见证人面前拆末页，区分叶清梧原字、叶观澜补字与今日认账，并保留三份抄件，正文 1661 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch684-糖印.md` 的 Claude 首稿虽有 2479 汉字但命中 3 处方式墙、20 处“自己”回声；主编重写为糖壳在叶观澜认账后裂开，护息玉只在空纸上承印“叶清梧·半个身位”，正文 1571 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch685-印开.md` 的 Claude 首稿基础门通过但缺 review evidence，仍是“自己开/印出”模板；主编重写为林窈在井台交代护息玉保管、糖壳包藏和未交信，在苏挽记录纸上落名并等余伯翻第七页，正文 1573 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch686-林崇信.md` 的 Claude 调度在章级时限后留下 25 处方向、34 处物象和自称回声；主编重写为林崇收到林窈署名抄件，拒绝用家印替未验第七页背书，并保留十三岁旧信封作责任对照，正文 1503 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch687-灶边雪.md` 的 Claude 首稿基础门通过但仍是短问/动作/空门模板；主编重写为老仆收林窈证词、牛阿大留粥、叶观澜携钥匙到灶房，将到场、问信、未入门分开记录，正文 1663 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch688-他错.md` 的 Claude 首稿只差字数且缺 review/score，并重复“认/自己”尾音；主编重写为叶观澜明确拆分叶清梧旧字、经手栏和保护/隐瞒责任，在雪亭签下认错并留下等原信，正文 1510 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch689-苏挽在.md` 的 Claude 首稿命中 9 处方向公式和 48 处物象位置回声；主编重写为苏挽在药庐建立临时见证处，分开阿湄便签、林窈证词和第七页抄件，面对门外来客先定验物与落名规则，正文 1541 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch690-林叙看.md` 的 Claude 首稿实际正文不足 1000 字且缺可核验 review；主编重写为林叙在东书房看见旧秤、未验第七页与林夙承接责任，选择把茶送回灶房并把赤渊斋外廊留给下一件物证，正文 1556 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch691-袖玉.md` 的 Claude 首稿实际正文未达 1500 字且缺 review；主编重写为沈疏桐在赤渊斋外廊验看袖中玉，分开玉背刮痕、补写的“叶清梧”、母亲旧信和个人推断，再把玉送往余伯处核验，正文 1798 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch693-苍梧.md` 的 Claude 调度结束时未形成独立回执，目标仍是位置/动作回声旧稿；主编重写为林叙带林窈署名抄件到余伯院，把亲见、转述、待验姓名分栏，追问叶清梧作为一个人而非叶家关系，正文 1609 汉字，最终 lint、公式扫描与 strict editorial review PASS，记录为 MANUAL_PASS。
- `ch694-那一页.md` 的 Claude 回执明确 `changed: no` 且严格门失败；主编重写为余伯用沈疏桐送来的玉对照旧账，展示“叶清梧，暂留，半个身位”的半页、缺失的见证和未决的去处，正文 1584 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch695-风停.md` 的 Claude 在章节级超时前留下 30 处 motif 回声和 3 处墙式公式；主编重写为林夙以护息玉听见余伯翻页传来的“叶清梧，暂留，半个身位”，将叶观澜的承认与叶清梧的意愿分栏记录，选择听见但不追，正文 1544 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch696-林崇信.md` 的 Claude 首稿保留堂屋、纸鸢、旧秤和信的骨架，但命中两处公式且正文不足 1500；主编重写为林崇把林夙送来的信、家印与亲见白纸分开，写下“家印未用”，拒绝替儿子把未验旧页收进林家账，正文 1532 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch697-他记.md` 的 Claude 自报无公式，但独立扫描抓到 wall_formula 28、motif_slot 41、self_claim 42；主编重写为叶观澜在旧信、护息玉印痕和余伯问句旁分栏记事实，承认改账与未获同意，收回笔不覆盖叶清梧空白，正文 1506 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch698-错在哪.md` 的 Claude 在章节级超时后未改目标，旧稿命中 self_claim 25；主编重写为余伯以林崇亲见纸、沈疏桐玉和六十二年前按痕核对责任，承认“错在替答”，把回答留给叶观澜，正文 1500 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch699-他信.md` 的 Claude 首稿实际正文只有 1461 字且严格 review 缺证据；主编重写为余伯交出旧笔、叶观澜核对原信封口并签下取笔记录，把“接笔”与“信不重写”分开，正文 1513 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch702-左袖.md` 的 Claude 首稿虽自报无禁用词，但独立门抓到 2 处 wall_formula；主编重写为沈疏桐用秤砣、指环、旧帕验看左袖双重刃痕，确认浅痕疑似叶清梧留力并将动机保留待核，正文 1548 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch703-苏漪母.md` 的 Claude 在章节级超时后留下长度充足但墙式回声严重的旧稿；主编重写为苏漪在苏挽旧屋验看画像、拓出背面“苓”字、把前主母称谓与母亲姓名分开，并把童年草蚱蜢作为旁证，正文 1550 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch704-窈母.md` 的 Claude 首稿命中 wall_formula 5；主编重写为林窈分辨母亲原抄与林崇副本，翻出糖纸背面“窈儿别怕”，将三份证据分栏收存，正文 1519 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch705-林叙等.md` 的 Claude 正文基础门通过，但独立严格门抓到 self_claim 18；主编重写为林叙收下林窈的糖纸与牛阿大的草帽，走二十三里到旧档室，把未署名的信放在桌上，正文 1624 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch706-临安街.md` 的 Claude 在 420 秒章节级上限后未改目标；主编重写为林夙核对雨痕、草帽、旧档登记和门外脚印，选择不替送信人拆信，正文 1640 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch707-清梧署.md` 的 Claude 自报 0 公式命中，但独立门抓到 wall_formula 5；主编重写为林夙拆开无名信只看见“叶清梧”署名，门灯下见人影后把脚步留在门槛内，正文 1558 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch708-巷子.md` 的 Claude 在 420 秒章节级上限后未改目标；主编重写为人影进巷、青线留档，林夙低头辨出地上的长线来自灯下影子，正文 1573 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch692-清梧.md`、`ch700-清梧回.md`、`ch701-远更南.md` 原稿分别存在短稿/缺 review、方向墙回环、自指回环与短稿；主编独立重写为半页旧账分栏、余伯等叶观澜翻页、阿湄沿南道收双重刃痕衣料，正文分别 1568、1531、1520 汉字，三章最终 lint、公式扫描与 strict editorial review PASS，记录为 MANUAL_PASS。
- `ch709-灯投.md` 的 Claude 超时且未改目标；主编重写为林夙移动煤灯验证影线，封存青线、收据和未拆信，正文 1545 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch710-不抬.md` 的 Claude 草稿长度足够但 strict editorial 未过，并因主编并发修复触发 side-effect gate；主编重写为林夙分开信、证物袋与门外草帽，坐回门口不抬头，正文 1505 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch711-清梧夜.md` 的 Claude 首稿未形成独立回执且正文仅 1151 字；主编重写为余伯核对叶观澜签名、旧页与清梧页码，合上留白页，正文 1503 汉字，最终 lint、公式扫描与 strict editorial review PASS，记录为 MANUAL_PASS。
- `ch712-灶边.md`、`ch713-南信.md` 的 Claude 回执因运行期 TTS 旁路文件触发 side-effect gate；主编复读后分别保留牛阿大在灶边不刻完的“夙”字、林夙拆分宿州来信并把半页证据交给沈疏桐，正文 1524、1508 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch714-林彻看林夙.md` 的 Claude 回执自报整章完成，但独立门抓到 3 处方向/自我公式且正文仅 1207 字；主编重写为林彻在门外亲见林崇称信而非称人，分开封面、封口、亲见与未读末行，并保留糖纸不代读，正文 1806 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch715-远道.md` 的 Claude 章级超时且未改目标；主编重写为林窈走二十三里到旧糖铺，交出姐姐留过的糖纸，拆分糖印、纸纹、旧账与人物姓名的证据边界，正文 1702 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch716-不站.md` 的 Claude 章级超时且未改目标，并留下 22 处自我承担回环；主编重写为叶观澜以轮椅到南廊，核对旧信封、清梧残纸、糖纸收处与经手链，拒绝替任何人先拆或先判，正文 1542 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch717-坐南.md` 的 Claude 生成稿缺 review/score 且保留模板化自证；主编重写为沈疏桐坐南廊核验旧蜡、纸纤维、南信转述与糖纸收处，把未拆信留给后续亲验，正文 1597 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch718-旧墨.md` 的 Claude 章级超时且未改目标，旧稿正文仅 968 字；主编重写为余伯核验 ch085 第三页纸纤维、六十年旧墨、后添“还”字与糖铺收纸凭，保留未拆信与下一页空白，正文 1514 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch719-糖铺老.md` 的 Claude 章级超时后留下缺 review 的糖铺稿；主编重写为糖铺老人核对糖纸折纹、桂花糖残痕、旧柜账和收纸时辰，只写可复查凭条，不替纸认人，正文 1556 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch720-粥外.md` 的 Claude 章级超时且未改目标，旧稿正文仅 949 字；主编重写为林叙在粥棚核对碗底刻字、南廊空椅、送达时辰与收粥名，拒绝把无人认领的粥端进房，正文 1503 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch723-认字.md` 的 Claude 章级超时且未改目标，旧稿正文仅 1001 字；主编重写为林夙在 ch085 旧卷上逐笔核对“叶清梧”的墨层、行距、纸边与拓记，经亲见/转述/待验分栏认字不认人，正文 1556 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch724-抬脸.md` 的 Claude 回执指向缺失的目标路径且独立门抓到 32 处物象槽位；主编恢复正确季目录路径，重写为林夙在深巷核对衣角、脚印、药堂半戳、红线与宿州信，把可见物、转述和待验落笔人分栏，正文 1668 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch725-深巷.md` 的 Claude 首稿虽过基础 lint 但独立门抓到 33 处物象槽位；主编重写为林夙与余伯在旧档室核对宿州来信、两道刃痕、木屑和红线，保留第三折署名未全读的承接，正文 1601 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch726-署名.md` 的 Claude worker 读完目标但 `changed: no`，没有写入正文；主编重写为林夙展开宿州信末折，逐项核对“叶清梧”三字与旧页的墨层、停顿、缺口和拓痕，确认认字不等于认人，正文 1576 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch727-余伯接函.md` 的 Claude worker 读完目标但 `changed: no`，没有写入正文；主编重写为余伯在东桌接收林叙经手的旧函，分开函套、封口、旧墨、木牌与署名，保留收件栏空白，正文 1587 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch728-林彻站.md` 的 Claude 首稿命中 53 处方向、69 处物象槽位和 34 处自指回环；主编重写为林彻在大公子院核对余伯湿信、王姨娘莲粥、林夙帛条与庚帖，拒绝替林夙先读或把热粥接成回答，正文 1613 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch729-苏挽不移.md` 的 Claude 首稿基础 lint 通过但留下严格自指公式；主编重写为苏挽在余伯院分列旧函封角、阿湄手帕、林叙门外粥、林窈空糖纸和余伯窄笔，按住信角不拆不移，正文 1545 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch730-林窈远递.md` 的 Claude 首稿命中 2 处 wall_formula；主编保留林窈安全递送新糖纸、半块桂花糖、旧纸副页、糖铺收纸栏与巷口泥点，明确糖与纸分开登记，正文 1570 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch733-林夙回.md` 的 Claude 首稿命中 9 处 wall_formula，且“巷口交函”触发硬线误报；主编重写为林夙回到旧档室追问“叶清梧是谁”，把宿州信、旧函、拓记、经手与落笔人分栏，修复误报并补齐证据，正文 1547 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch734-林彻看林夙.md` 的 Claude 首稿命中 7 处方向、12 处 wall 和 38 处物象回声；主编重写为林夙在林彻见证下亲收湿信、写下“亲收，未拆”，林崇保留家印，正文 1552 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch735-阿湄到宿.md` 的 Claude 首稿基础 lint 通过但缺主编证据元数据；主编重写为阿湄抵达宿州后核对门房时辰、井栏干米、两道刃痕、红线和药堂回条，亲见/转述/待验分栏，正文 1538 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch737-林叙送汤.md` 的 Claude 在章节窗口末留下 wall_formula 半稿；主编重写为林叙核对汤签、灶房印、肩带补线，把汤放到余伯院门外并写“送到门外，未收”，正文 1509 汉字，最终 lint、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch738-林窈攥纸.md` 的 Claude 首稿命中 2 处 wall_formula；主编重写为林窈在三房外巷核对糖纸折痕、糖液、槐皮碎屑与汤凭，把“纸在我手，未交他人”写入安全保管记录，正文 1510 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch739-叶观澜写.md` 的 Claude 调度超时并留下 33 处 motif_slot；主编重写为叶观澜在轮椅上核对旧纸、余伯墨痕、苏挽拓件与林夙湿信，把“字可比，人未定”与亲见署名分列，正文 1706 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch740-沈疏桐称.md` 的 Claude 首稿命中 4 处 wall_formula、36 处 motif_slot 且独立字数门失败；主编修复 frontmatter 后重写为空铜秤、两人各自落责、旧帕单列，正文 1657 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch741-林崇看.md` 的 Claude 回执自报过门，但独立审稿抓到填充句且缺正文证据；主编重写东堂荐书核验，保留“林彻”落责、拒盖家印与文章待呈，正文 1524 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch742-灶边.md` 的 Claude 超时未改文件，原稿含 37 处方向回环、16 处自我修复、76 处物象回声且不足 1500 字；主编重写灶灰残纸与“宿州信”核验链，保留林窈安全记账和老仆待核边界，正文 1535 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch743-林夙接信.md` 的 Claude 超时未改文件，原稿命中 3 处 wall_formula 与 20 处 self_claim；主编重建林夙收件流程，核对宿州来源、蓝蜡缺口和经手时辰，只写“亲收，未拆”，将拆封交给苏挽，正文 1698 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch744-苏挽拆信.md` 的 Claude 超时未改文件，原稿命中 6 处 wall_formula；主编重建苏挽拆信场景，读取宿州南街旧档、七号柜与叶字残笔，将亲见、转述、待验分栏并保留后续查证动作，正文 2034 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch745-阿湄换路.md` 的 Claude 自报过门但独立审稿抓到 15 处 wall_formula；主编重写阿湄在宿州避开药铺旧路、进入水巷灰门，取得七号柜蓝线与残纸并把路线物证分栏，正文 1910 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch746-余伯算账.md` 的 Claude 超时未改文件且缺正文证据；主编重写余伯核对收件、驿费、七号柜钥与水巷拓图，算出钥未还和三钱缺项，保留亲见、转述、待验边界，正文 2150 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch747-林窈再递.md` 的 Claude 基础 lint 通过但独立严格门缺正文证据且仅 1231 字；主编重写林窈在糖铺安全复核折缝、糖印、时辰与纸张来源，再将新糖纸递回内院，正文 1677 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch748-林叙坐廊.md` 的 Claude 超时未改文件，原稿是重复坐廊模板且有“朝”临界告警；主编重写林叙接收林窈糖纸、核对第三折糖印、分开宿州物证并写下“递回，未拆”，正文 1856 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch749-观澜不写.md` 的 Claude 未改文件，原稿命中 4 处 wall_formula、27 处 self_claim；主编重写叶观澜拒绝把未证姓名写入回信，撕页入待验格并登记未送原因，正文 1508 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch750-沈疏桐叠.md` 的 Claude 改写后仍命中 3 处 wall_formula 且独立字数门不足；主编重写沈疏桐分叠糖纸、叶字拓件、蓝蜡残片，建立来源时辰目录并保持姓名待验，正文 1642 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch752-阿湄再写.md` 的 Claude 改写后仍有 10 处公式、11 处自指与 49 处物象回环；主编重写阿湄删去安字、补七号柜物证与经手时辰，改走北门并拿到签收副联，正文 1576 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch753-苏挽递签.md` 的 Claude 超时未改文件且原稿命中 wall_formula、motif_slot；主编重写苏挽分列第二封信、北门寄单、叶字副本，由林夙签下亲收未拆并保留姓名待验，正文 1553 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch754-余伯再递.md` 的 Claude 超时未改文件且原稿命中 5 处 wall_formula；主编重写余伯核对北门副联、三钱欠项、见证条与第二封信，按经手、收件、拆封顺序再递给林夙，正文 1500 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch755-疏桐坐中.md` 的 Claude 超时未改文件且原稿命中 4 处 wall_formula；主编重写沈疏桐坐到桌中，分列蓝封、费用欠项、叶字副本与撕页，让林夙确认收件而不替旧字认名，正文 1627 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch756-林夙认梧.md` 的 Claude 超时并留下公式化候选；主编重写林夙第二次辨认梧字，补入七号柜三张旧纸与分列交接，蓝封保持未拆，正文 1644 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch757-观澜翻牌.md` 的 Claude 首稿仍是旧模板公式且未交付可用正文；主编重写叶观澜翻出七号柜旧牌，发送柜账拓本而保留姓名待验，正文 1614 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch758-林彻站.md` 的 Claude 超时未改文件且目标仍为旧模板；主编重写林彻面对七号柜拓本、荐书与家印，选择只写“以文自陈”，正文 1515 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch759-阿湄不回.md` 的 Claude 首稿虽有 2422 字但命中 wall_formula；主编重写阿湄收到七柜回条后不回人名，把木牌夹入第三封信并留在槐根暗线，正文 1609 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch760-苏挽不拆.md` 的 Claude 首稿基础 lint 通过但仍是牌面回声并缺有效严格审稿；主编重写苏挽登记第三封、木牌正面与见证规则，保持封件未拆、背面未验，正文 1528 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch761-余伯算账.md` 的 Claude 首稿基础 lint 通过但含方向、物象与自指回声；主编重写余伯核对三钱半刻差、木牌与六十二年前录字，原页留案不先报，正文 1633 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch763-林窈不递.md` 的 Claude 流中断且未改目标；主编重写林窈核对糖印、折痕与时辰，把原件留在木盒，只递糖印副条，正文 1538 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch764-对峙.md` 的 Claude 首稿虽有 2005 字但仍是站位与物象回声化伪对峙；主编重写叶观澜与林夙核对旧录、七柜拓本、未拆蓝封，承认录字而不替梧字落名，正文 1548 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch765-拔刀.md` 的 Claude 超时未改目标且原稿仍是动作回声；主编重写阿湄核对旧蓝蜡、七柜木牌与传线，切断暗线并把刀柄露成求援标记，正文 1666 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch766-判打.md` 的 Claude 首稿仍是消息清单与自指回声；主编重写苏挽核对刀柄、蓝蜡、梧字记录，判定打断传线、不碰持刀人，正文 1553 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch767-刀落.md` 的 Claude 首稿留下严格编辑字数门失败与明显自指回环；主编重写阿湄以第三封信、七柜原页和旧蓝蜡逼问叶观澜，刀停在胸前一寸但不伤人，正文 1503 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch768-还手.md` 的 Claude 首稿超时并留下自指、墙式与基础 lint 问题；主编重写叶观澜偏开刀锋而不夺刀、交还旧蓝蜡并说明它是留给阿湄的选择信号，补齐七柜第六格与叶清梧原页信息，正文 1505 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch769-不躲.md` 的 Claude worker 超时未改目标；主编整章回炉为叶观澜让阿湄带走第三封信、把七柜原页留在门前，并从纸底旧字核出“未归”被后补成“已归”，正文 1616 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch770-伸手.md` 的 Claude worker 超时未改目标；主编整章回炉为林夙拦住叶观澜先取原纸，用茶水、白石粉和旧药方核出“已归”为后补墨，并把经手先手留在纸外，正文 1624 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch773-看.md` 的 Claude 首稿仍是眼底秤影与自指位置回声，且独立 lint 失败；主编重写林夙辨出叶观澜把旧秤影压到眼前的人身上，确认原页与林崇旧字，并以青砖下秤声收钩，正文 1516 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch774-看错.md` 的 Claude worker 超时未形成可用终稿；主编重写叶观澜承认把林夙看成旧日林崇，保留原页不再归入叶家，并让林崇持旧秤在门外开口“叶先生，六十年”，正文 1554 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch775-林崇.md` 的 Claude 首稿达字数但留下 wall_formula 与旧秤回声；主编重写林崇把六十年拆成林夙、阿窈的娘、叶清梧三笔，确认“已归”非他所补，并把秤杆横过门槛，正文 1696 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch776-到.md` 的 Claude 首稿有 30 处物象槽位和墙式回声；主编重写林崇踏入门内，把秤砣放到叶观澜面前，确认叶清梧“未归”与叶观澜把假话当真，等他先开口，正文 1526 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch777-见.md` 的 Claude 超时且未改目标；主编重写为林崇逼叶观澜承认知道叶清梧未归却默许“已归”留在原页，并说出“我等了六十年”，正文 1589 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch778-等.md` 的 Claude 超时且未改目标；主编重写为林崇铺开姓名、经手、承担三栏，林夙只作见证，叶观澜认领第一笔，正文 1517 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch779-六十.md` 的 Claude 超时且未改目标；主编重写林崇把六十年落成承担栏外的可核验数字，并让叶观澜交出藏信旧盒，正文 1759 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch780-那一笔.md` 的 Claude 超时且未改目标；主编重写第三封信与裁纸旧刀的证词链，叶观澜承认给刀并交出刀柄，为 781 的落刀留下实物压力，正文 1791 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch782-补.md` 的 Claude 有写入但首稿命中 17 处 wall_formula 与 45 处 motif_slot；主编整章回炉为旧刀逼近却不让伤口替证词签字，林崇把刀停在颈侧一寸外，正文 1692 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch783-接住.md` 的 Claude 低成本结束且未改目标；主编重写为叶观澜接住刀柄、亲手割掉“已归”，并把回条送出，正文 1747 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch784-他挡.md` 的 Claude 有写入但严格门拒收模板回声；主编重写叶观澜挡住收刀、亲手落名，并把三份副本送出叶家控制范围，正文 1589 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch785-林叙等.md` 的 Claude 有写入但严格门拒收物象回声；主编重写林叙不破门、让林窈单列母亲姓名，牛阿大以水和灯守场，正文 1560 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch786-林崇信.md` 的 Claude 超时未改目标；主编重写余伯交出叶观澜六十二年前留下的“录”，林崇把信交给林夙，由他决定是否送达，正文 1524 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch787-灶边雪.md` 的 Claude 首稿命中 36 处方向公式、47 处 motif_slot 与 42 处 self_claim；主编重写老仆认出牛阿大，把粥、纸和灶火交给他送入柴房，正文 1506 汉字，最终 lint、安全、公式扫描与 strict editorial review PASS，Claude 回执保留 BLOCKED。
- `ch788-林彻站.md`：Claude worker 超时且未改目标；主编重写为林彻保留“见证：林夙在”的副本，未焚毁或改字，站到父亲门外递入，正文 1634 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch789-苏挽在.md`：Claude worker 有写入但留下 2 处 wall_formula，严格门拒收；主编重写为苏挽保留原账、交出可核验副本、拒绝叶家取原页，正文 1591 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch790-林叙看.md`：Claude 未改目标且回执 BLOCKED；主编重写林崇拒绝替林叙落名、林夙取走原页、林叙把经手事实写进第三页，正文 1599 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch794-半山.md`：Claude 未改目标，原回执虽过 lint 与公式门但 strict 元数据拒收；主编重写半山药瓶、蓝线副本与糖纸的证据交接，林夙叫阿湄后她带证据下山，正文 1653 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch795-父亲先见.md`：Claude 有写入但留下方向与 wall_formula；主编重写叶观澜看见林夙点名、故意放证据下山，并把“父亲先见”送入祠堂，正文 1653 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch796-林崇信.md`：Claude 有写入但正文 lint 与 strict 失败；主编重写林崇在祠堂读出四字是杀令，开旧页核验后让“不准”先传给阿湄，正文 1579 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch797-偏房门口.md`：Claude 超时后只留下旧模板半成稿；主编重写阿湄听见林崇“不准”、确认这是截杀令，割断叶观澜红绳并带瓶与副本下山，正文 1656 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch798-山顶之上.md`：Claude 有写入但 strict 拒收；主编重写叶观澜收到红绳、香灰与半字三件失控证据，决定不追阿湄，留门等林夙上山，正文 1554 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch799-山门外.md`：Claude 超时未改目标且命中 30 处 self_claim；主编重写林夙在山门接住阿湄带下来的药瓶线索与苏挽交出的蓝线副本，收下林窈糖玉后独自上山，正文 1540 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
- `ch800-林叙等.md`：Claude 超时未改目标且旧模板命中方向、物象位置与自指公式；主编重写林叙留下未获同意的第三页，改信署正牛阿大之名，最终被牛阿大拒绝代送并由林窈拆穿回报心思，正文 1514 汉字，最终 lint、公式扫描、strict editorial 与 safety PASS。
