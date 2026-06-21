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
