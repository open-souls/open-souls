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

## 边界与尺度

`rating` 旋钮（`config.yaml` / `world.md`）：温馨 < 暧昧 < 成人擦边 < 黑深残。
尺度可以大——反派、战争、天灾、背叛、道德灰都能写——但**露骨性行为 / 自我伤害 / 未成年**
三条硬线由审校永久卡死，与 rating 无关。PR 仍需人工合并，不是无人值守地吞外部内容。

---

<div align="center">
<sub>众魂 · Open Souls — 魂不变，世界每季换。</sub>
</div>
