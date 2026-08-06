---
name: open-souls
description: >
  Open Souls / 众魂 —— 一个开源的无限流网文世界。把一个魂(soul.md)用 PR 或填表送进来，
  写手系统(策划→写→审，自带流量密码评分与上线审查)按篇幅持续续写一部可追的群像连载，
  每季换一个世界(现代→异世界→…)，角色有迹可循。触发场景：续写一回 / run open souls /
  过一回日子 / 送一个角色 / 加新魂 / 换季 / 看连载进展 / 给某角色立传 / 调写手手感。
  也用于把一份角色描述转成 soul.md、或重写不够"嗑"的章节。
---

# Open Souls

开源无限流网文世界。详见 `README.md`。常用动作：

- **续写一回**：`python engine/village.py --ticks 1 --pressure 0.2`
  （`VILLAGE_MOCK=1` 可零 token 干跑看流程）
- **送一个魂进来**：把描述写进 `souls/角色名/soul.md`（照 `souls/_TEMPLATE/soul.md`），
  或 `python engine/intake.py 表单.json`，然后 `python engine/validate.py` 验。
- **看连载**：`seasons/*/chronicle/`，或开 GitHub Pages 指到 `/docs`。
- **追一个角色的线**：`souls/角色名/dossier.md`；总名册 `CAST.md`。
- **调写手手感**：改 `writer/playbook.md`(桥段库)、`writer/rubric.md`(上线评分)、`config.yaml`(篇幅/节奏/rating)。

## 工序（engine/writer.py）
策划(定钩子/反差/桥段) → 写手(好模型写正文) → 审校(打分+安全审查，不过线重写一次才上线)。
硬线：露骨性行为 / 自我伤害 / 未成年——永久卡死，与 rating 无关。

## 当前发布门

生成稿只有同时满足以下条件，`engine/village.py` 才会推进关系、记忆、节拍并写入连载：

- `prose_lint` 通过：中文叙述、句子节奏、填充描写、机械公式、重复句式回环（包括“方向落在/方向不必替/不必替上一世/自己守”变体）和目标字数都过线；strict editorial 还会卡同一物象位置与“我/他/她自己”高频回声。
- 审校分数、开篇冲突、节拍、连续性、人物主动性和安全门都通过；文笔复读失败会继续重写，达到次数上限仍失败则拒发。
- 章节带完整 YAML frontmatter：季、回数、标题、角色、POV、主线、节拍、关系线和章末 hook；缺字段或占位标题拒发。
- 新生成章还必须落真实 review 证据块和 score: N/14；review 至少逐字引用一条正文原句（用「」等标记），上线档分数低于 12/14 拒发；不能沿用模型随手写的虚高分数。
- 批量重写必须通过受限 `python engine/run_dispatch.py --max-budget-usd 12.0 --effort high`：Claude 只拿目标章 prompt，只获 `Read,Edit` 且单任务 420 秒上限；Windows 超时会按进程树终止 `claude.cmd` 包装进程及其子进程，避免孤儿任务。runner 还会快照目标以外的 prompt、receipt、根目录和 agent/tool/test 文件，任何副作用都 BLOCKED。返回后由本地 lint、strict editorial 和公式/回声扫描独立决定 PASS；Claude 自报 PASS 不具备放行权。
- 元数据也会防回路：章末 hook 不能原样重复最近章节，关系线不能写成角色与自己的自配对。
- Claude 批量写手提示已加内容先行门：范章只作节奏参照，不得复制其病句；每章先落一个可观察冲突、一个人物选择和一个不可逆新信息，再写成 1800–2600 字正文。`方向/位置/那一寸/那一截/那一道` 不能承担心理解释，物象重复必须带来新信息；hook 必须是正文真实出现的独特动作或对白，不能用“下一章切下批头一章”占位。
- 结构化模型输出会做有限重试；模型/API/JSON 失败是干净 no-op，不推进状态、不写半章。

这些是机器上线门，不等同于“晋江爆款”证明。编辑仍需逐章检查人物欲望、情绪兑现、追更钩子、连续性和原创边界；`VILLAGE_MOCK=1` 只验证流程与拒发逻辑，不代表成稿质量。
