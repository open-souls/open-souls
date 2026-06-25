# 上线检查单（DoD · 总编落地前逐条勾）

写进 frontmatter / 提交前，这一回必须全勾。任一项不勾 → 回炉，别提交。

## A. 安全（任一违例 = 整章打回，与 rating 无关）
- [ ] 无露骨性行为（暧昧/张力/留白/fade-to-black 可以）
- [ ] 无自我伤害的方法或细节
- [ ] 林窈(13)及任何未成年不涉及性或恋爱

## B. 机器门（地板，0 ERROR 才算落地）
- [ ] `python engine/prose_lint.py <章节路径>` → 0 ERROR
- [ ] 正文是通顺中文：无英文对话标签（he said…）、无成串拉丁字母
- [ ] 无逗号碎句：微碎片率 ≤ 42% 且 平均段长 ≥ 3.5

## C. 文笔七维（编辑部上线档）
- [ ] score ≥ 12/14
- [ ] 无任一维 = 0
- [ ] review 块每维引了真句 + 行号 + 范文 A–J 对照
- [ ] `score: N/14` 格式正确（非「13分」「12.5/14」「满分」）

## D. 9 硬门（无 FAIL；PARTIAL 须记项目级备忘）
- [ ] 门1 硬线 / 门2 锚点不跳级 / 门3 单一钩子落物象 / 门4 缺席与cast节奏
- [ ] 门5 回改 / 门6 beat 节奏 / 门7 声线指纹 / 门8 群像不工具人 / 门9 frontmatter

## E. 章级 rubric + 节奏
- [ ] rubric ≥ 9/14（钩子/爽痛/反差/拉扯/记忆点/代入/新）
- [ ] 开场强度 ≥ 7/10；转折卡 ≈22/47/68%，89% 再翻 + 留钩

## F. frontmatter（照 CLAUDE.md §六 / 评审方法§三）
- [ ] 8 字段齐：season / chapter / title / cast / pov / beat / ships / hook
- [ ] 标题 2–4 字（非纯单字/纯地点/纯人名/语气词）
- [ ] cast ≥ 4 人
- [ ] beat = 起|承|转|合 + 序号/总数（编号不跳）
- [ ] ships 注明本回埋的锚点类型；不臃肿（>1000 字符记 P0 迁出）
- [ ] hook 含引号 → `|` block scalar
- [ ] `review: |` 块 2 空格缩进，插在 hook 之后、闭合 `---` 之前
- [ ] 不动正文，不动其它 frontmatter 字段

## G. 连续性 / soul 维护
- [ ] cast 与近 3 章不同规模；缺席最久者已安排
- [ ] 锚点曲线相邻差 ≤1、距上次升级 ≥3 章
- [ ] 声线全员对齐
- [ ] 触发 soul.md 更新的，已更新 incarnation/seed_relations（或新角色 origin/incarnation/appearance）

## H. 落盘
- [ ] 文件名 `seasons/01-xianxia/chronicle/NNN-标题.md`（三位补零）
- [ ] 回炉次数 ≤ 2；若硬不过已停手报人，未硬上线
