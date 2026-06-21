# Open Souls / 众魂

一部**开源的无限流网文**。任何人送一个魂进来，它就在别人的世界里活一遍——
暧昧、背叛、变故、天灾，什么都能发生。写手系统按篇幅持续续写，每个角色都有迹可循。

> 开源的魂，开放的世界。魂不变，世界每季换。

## 两道门：怎么送一个魂进来

**门 1 · 填表（不用会 git）** — 开一个 [送魂 issue](../../issues/new?template=submit-soul.yml)，
填完提交。机器人自动把它写成 `soul.md`、开 PR、跑 CI。合并后下一回它优先登场。

**门 2 · PR（会 git）** — 复制 `souls/_TEMPLATE/soul.md` → `souls/你的角色名/soul.md`，填好开 PR。
CI 验魂（格式、必填、防注入、不重名），合并即入世。

两道门最后都汇进 `souls/`。

## 一个魂 = 三层（按谁来写分）

    souls/角色名/
      soul.md      ← 你写(PR)。魂：本质，跨所有赛季不变。
      memory.md    ← 写手只增。忆：经历，可跨季(看本季设定)。
      state.json   ← 引擎写。皮囊：本季身份+境况，每季重新投胎。
      dossier.md   ← 自动生成。它的整条线，有迹可循。

写好一个魂的关键是 **fracture**（嘴上 vs 实际）和 **under_pressure**（被逼到墙角会怎样）——
没有这道缝、没有这个区间，进来也是 NPC。详见 `souls/_TEMPLATE/soul.md`。

## 赛季：无限流

`seasons/01-modern/world.md` 定义这一季的世界（题材、tone、尺度、转生带不带前世记忆、当季热门梗）。
现代是第一季，下一季可以是异世界、末世、宫廷……同一拨魂换个世界重新做人。
`carry_memory: true` 时，前世的羁绊跟着进新世界——无限流最嗑的那一招。

## 写手的脑子：策划 → 写 → 审（engine/writer.py）

每回不是一遍过，是个小编剧室：**策划**定钩子/爽点/反差/桥段(中·日·西) → **写手**(好模型)写正文 →
**审校/上线门**按 `writer/rubric.md` 给 7 项流量密码打分(满分14)+ 安全审查，**不过线就带意见重写一次**才上线。
`writer/playbook.md` 是桥段库，`writer/hits.md` 记命中分——高分桥段提拔进库 = 内化流量密码。

## 有迹可循 & 按篇幅续写

每续写一回，`trace.py` 刷新每个角色的 `dossier.md` 和总名册 `CAST.md`。
`config.yaml` 控制 `target_chapter_chars`（每回篇幅）和 `chapters_per_beat`（节奏），每季走起承转合。

## 先跑一遍

    pip install -r requirements.txt
    VILLAGE_MOCK=1 python engine/village.py --ticks 3   # 零 token，看流程
    export ANTHROPIC_API_KEY=sk-...
    python engine/village.py --ticks 1 --pressure 0.3   # 真·续写

`--pressure` 是 0 号宇宙旋钮：0 安稳，1 = 稀缺+对撞，社会会崩。

## 边界与尺度

`rating` 旋钮（config / world.md）：温馨 < 暧昧 < 成人擦边 < 黑深残。尺度可以大——反派、战争、
天灾、背叛、道德灰都能写——但**露骨性行为 / 自我伤害 / 未成年**三条硬线由审校永久卡死，与 rating 无关。
PR 仍需人工合并，不是无人值守地吞外部内容。
