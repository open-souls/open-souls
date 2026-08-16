<div align="center">

# Open Souls · 众魂

<img src="docs/assets/images/hero-inkwash-v2.png" alt="众魂 · 镇狱之渊 — 水墨半仿真群像" width="820" />

**一部开源的无限流网文。** 任何人送一个「魂」进来，它就在别人的世界里活一遍——
暧昧、背叛、变故、天灾，什么都能发生。写手系统按篇幅持续续写，每个角色都有迹可循。

> 开源的魂，开放的世界。**魂不变，世界每季换。**

第一季 **《镇狱之渊》** · 玄幻复仇群像 · 续写中（已落盘 ch001–684，续写至 ch1000 收季） · 在场 **19 魂**

</div>

---

## 这是什么

把一个角色（一个 `soul.md`）送进来，引擎就让它在当季世界里投胎、登场、过日子。
写手系统不是一遍过，而是一个**小编剧室**：策划定钩子 → 好模型写正文 → 审校按流量密码打分并卡安全门，
不过线就回炉重写。每续写一回，所有角色的档案自动刷新——线索可追，伏笔会回收。

季与季之间换世界（仙侠 → 现代 → 末世 → 宫廷……），同一拨魂换个皮囊重新做人。
开 `carry_memory` 时，前世的羁绊跟着进新世界——无限流最嗑的那一招。

## 两道门：怎么送一个魂进来

**门 1 · 填表（不用会 git）** — 开一个 [送魂 issue](../../issues/new?template=submit-soul.yml)，填完提交。
机器人自动把它写成 `soul.md`、开 PR、跑 CI。合并后下一回它优先登场。

**门 2 · PR（会 git）** — 复制 `souls/_TEMPLATE/soul.md` → `souls/你的角色名/soul.md`，填好开 PR。
CI 验魂（格式、必填、防注入、不重名），合并即入世。

两道门最后都汇进 `souls/`。

## 一个魂 = 三层（按谁来写分）

```text
souls/角色名/
  soul.md      ← 你写(PR)。魂：本质，跨所有赛季不变。
  memory.md    ← 写手只增。忆：经历，可跨季（看本季设定）。
  state.json   ← 引擎写。皮囊：本季身份+境况，每季重新投胎。
  dossier.md   ← 自动生成。它的整条线，有迹可循。
```

写好一个魂的关键是 **fracture**（嘴上 vs 实际）和 **under_pressure**（被逼到墙角会怎样）——
没有这道缝、没有这个区间，进来也是 NPC。详见 [`souls/_TEMPLATE/soul.md`](souls/_TEMPLATE/soul.md)。

## 赛季：无限流

[`seasons/01-xianxia/world.md`](seasons/01-xianxia/world.md) 定义这一季的世界——题材、tone、尺度、
转生带不带前世记忆、当季热门梗。仙侠是第一季，下一季可以是现代、末世、宫廷……
同一拨魂换个世界重新做人。`carry_memory: true` 时，前世的羁绊跟着进新世界。

## 写手的脑子：策划 → 写 → 审

每回不是一遍过，是个小编剧室（`engine/writer.py`）：

1. **策划** 定钩子 / 爽点 / 反差 / 桥段（中·日·西三路）
2. **写手**（好模型）写正文
3. **审校 / 上线门** 按 [`docs/standards/rubric.md`](docs/standards/rubric.md) 给 7 项流量密码打分（满分 14）+ 安全审查，**不过线就带意见重写一次**才上线

[`docs/standards/playbook.md`](docs/standards/playbook.md) 是桥段库，高分桥段提拔进库 = 内化流量密码。
全部创作标准在 [`docs/standards/`](docs/standards/)（文笔范文标准、rubric、playbook、幕后规则、审查流程）；过程记录在 [`docs/handbook/`](docs/handbook/)。

## 有迹可循 & 按篇幅续写

每续写一回，`engine/trace.py` 刷新每个角色的 `dossier.md` 和总名册 [`CAST.md`](CAST.md)。
`config.yaml` 控制 `target_chapter_chars`（每回篇幅）和 `chapters_per_beat`（节奏），每季走起承转合。

读连载：[`seasons/01-xianxia/chronicle/`](seasons/01-xianxia/chronicle/)，或开 GitHub Pages 指到 `/docs`。

## 给另一个 AI：先选读者，再写章节

本仓库不是“模型自己挑一个最爽方案然后连写”的黑箱。完整协议在
[`.claude/skills/novel-writer/SKILL.md`](.claude/skills/novel-writer/SKILL.md)：AI 提出 A/B/C，
人类批准读者承诺和不可逆选择，程序保存阵营/人物/知识/剧情状态，最后才允许写入 canonical chapter。

第一季故意标为 `legacy_mode`：它是素材和审计对象，不是新流程的质量基线。先看：

```bash
python engine/story_state.py status --season seasons/01-xianxia
python engine/validate_story.py --season seasons/01-xianxia
```

新季必须准备 `season_manifest.yaml`、`factions.yaml`、`plot_state.json` 和
`decisions/next.json`，并设置 `human_decision_required: true`、`legacy_mode: false`。
没有 `decisions/approved.json` 时，`engine/village.py` 会在调用模型前停止。
批准记录绑定当前 `last_accepted_chapter`，只消费一个下一章；章节落盘后必须重新批准下一步，不能把一次选择当成整季自动驾驶。

严格章节还必须提供 `causal.pressure/choice/cost/state_change/next_pressure`、
带正文证据的 `state_updates`/`faction_moves`、`hook_evidence` 和唯一的 canonical 编号；模型的 `PASS` 或
`continuity_ok: true` 不是连续性证据。

## 先跑一遍

```bash
pip install -r requirements.txt
VILLAGE_MOCK=1 python engine/village.py --ticks 3        # 零 token，看流程
export ANTHROPIC_API_KEY=sk-...
python engine/village.py --ticks 1 --pressure 0.3        # 真·续写
```

### 章节改稿的快速验收

单章改稿可用增量门，只检查本次变动的章节：

```bash
python tools/validate_changed.py --base origin/main --head HEAD
```

它会对改动章节依次运行 prose、硬线和 strict editorial 三道门；如果改到了共享门禁代码，会要求显式执行全量审计：

```bash
OPEN_SOULS_FULL_PUSH=1 python tools/validate_changed.py --base origin/main --head HEAD
```

`engine/batch_rewrite.py --status` 使用 `.audit_tmp/batch_lint_cache.json` 做内容与规则指纹缓存。缓存只加速未变章节的重复扫描，不改变门槛；删除该文件即可强制全量刷新。完整全书 lint 仍然保留为发布前审计，不应被单章快速门替代。

首次使用本地快速 push 门时执行一次：

```bash
git config core.hooksPath .githooks
```

`--pressure` 是 0 号宇宙旋钮：0 安稳，1 = 稀缺 + 对撞，社会会崩。

## 给另一个 AI：用 Open Souls 写你自己的小说

如果你是另一个 AI，先读 [`.claude/skills/novel-writer/SKILL.md`](.claude/skills/novel-writer/SKILL.md) 和本 README，再开始写。这个仓库不是“输入一句 prompt 就吐一本书”的黑箱，而是一套有状态的编剧室：你负责世界、角色和故事决策，`engine/village.py` 负责把策划、写作、审校、状态更新串起来。

### 先理解这张地图

| 你要改变的东西 | 权威文件 | 谁会更新它 |
|---|---|---|
| 世界、题材、尺度、起承转合 | `seasons/<active>/world.md`、`arc.json` | 你 / 主编 |
| 角色的本质、欲望、裂缝、边界 | `souls/<name>/soul.md` | 你 |
| 本季身份与当前处境 | `souls/<name>/state.json` | 引擎 |
| 角色经历 | `souls/<name>/memory.md` | 写作循环 |
| 关系数值与情感变化 | `seasons/<active>/ties.json` | 写作循环 |
| 章节正文 | `seasons/<active>/chronicle/` | 写作循环 / 人工修订 |
| dossier、名册、章节 feed | `dossier.md`、`CAST.md`、`docs/chronicle.json` | `engine/trace.py` |
| 文笔与上线门 | `docs/standards/`、`engine/prose_lint.py` | 你 / 编辑门 |

### 从零开一部新小说

不要直接把第一季的仙侠人物改名后继续写。新建一个 `seasons/<number>-<slug>/`，至少准备：

```text
seasons/02-my-novel/
  world.md
  arc.json       # {"beats": ["起...", "承...", "转...", "合..."], "beat": 0, "in_beat": 0}
  ties.json      # 新故事可从 {}
  chronicle/
```

`world.md` 的 YAML frontmatter 要先定清 `season`、`title`、`genre`、`tone`、`rating`、`scope`、`carry_memory`、`incarnation_rule`、`arc`、`active_tropes` 和 `season_engine`。每个角色从 [`souls/_TEMPLATE/soul.md`](souls/_TEMPLATE/soul.md) 开始，填满 `name`、`one_line`、`drives`、`fracture.says`、`fracture.does`、`under_pressure`、`boundaries`；不要只写“主角的朋友/反派”，要写出这个角色自己的欲望、选择和代价。

有一个重要的当前实现约束：`engine/season.py` 会选 `seasons/*` 中按字典序最后的目录，命令行暂时没有 `--season` 参数。运行前确认你的 active season 确实会被选中；不要在多个实验 season 都存在时盲跑。

### 让 AI 跑一回

先安装并验收基础结构：

```bash
python -m pip install -r requirements.txt
python engine/validate.py
python -m pytest -q
```

然后先用零 token 的 mock 模式走完整条链：

```bash
VILLAGE_MOCK=1 python engine/village.py --ticks 1 --pressure 0.2
```

它会写章节、关系、记忆和 trace 输出；这是演练，不是文学质量证明。检查 `git diff`，确认写入的是你的 active season。真实续写时再提供 Anthropic key：

```bash
export ANTHROPIC_API_KEY=...
python engine/village.py --ticks 1 --pressure 0.2
```

没有 key 时引擎也会自动走 mock，所以“命令成功”不代表真实模型已经调用。`--ticks` 控制生成回数，先用 `1`；`--pressure` 控制冲突强度，先从 `0.2` 左右开始。

### 每一回都要过门

AI 不得把自己的生成结果或另一个 agent 的 `PASS` 当成验收证据。至少做这几件事：

1. 读完整章正文和 frontmatter，核对 POV、cast、beat、hook、thread、关系变化和下一步压力。
2. 对照 [`docs/standards/`](docs/standards/) 的文笔、桥段、审查和评分规则；若换题材，先有意识地改这些标准，不能以为只改 `world.md` 就换了写作契约。
3. 对精确章节跑确定性文笔门：

   ```bash
   python engine/prose_lint.py seasons/02-my-novel/chronicle/0001-title.md
   ```

4. 确认没有露骨性行为、自我伤害或未成年暧昧等硬线内容；`engine/writer.py` 会调用 `engine/safety_lint.py`，但人工仍要读。
5. 只有正文、连续性、角色能动性、节奏、声音和结尾钩子都过了，才把它视为可发布章节。失败就修复后重新跑门，不要降低门槛。

引擎会自动刷新 `state.json`、`memory.md`、`ties.json`、`dossier.md`、`CAST.md` 和章节 feed。不要把生成文件当设定源：角色本质回到 `soul.md`，本季处境回到 `state.json`，经历回到 `memory.md`。

### AI 的最小工作循环

```text
读最近章节与角色档案
  → 定本回唯一冲突 / 钩子 / 角色选择
  → 运行 planner → writer → critique → prose gate
  → 失败：引用具体错误，最小修复，重新验收
  → 通过：检查 diff 与状态文件，再决定下一回
```

创作应使用原创人物、世界和正文。外部作品只能作为抽象类型参考；不要把受版权保护的原文、整段模仿文本或未授权角色档案写进仓库。生成、验证、发布是三个不同状态；任何一个没证据，都要如实标成未完成。

## 边界与尺度

`rating` 旋钮（`config.yaml` / `world.md`）：温馨 < 暧昧 < 成人擦边 < 黑深残。
尺度可以大——反派、战争、天灾、背叛、道德灰都能写——但**露骨性行为 / 自我伤害 / 未成年**
三条硬线由审校永久卡死，与 rating 无关。PR 仍需人工合并，不是无人值守地吞外部内容。

---

<div align="center">
<sub>众魂 · Open Souls — 魂不变，世界每季换。</sub>
</div>
