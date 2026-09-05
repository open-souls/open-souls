---
run_id: 01a06bb9-f3fe-77d3-988b-204e03406335-demo-E
persona_seed: l1-persona-5-2026-09-04-demo
persona_id: 5
pack_hash: 892df4c69d659635
cwd: C:\Users\stanc\github\open-souls
no_chronicle: true
no_frontmatter: true
read_time: ch501-510 / 4 packs (open, mid_a, mid_b, latest)
source: 读者 sub-agent 模拟
---

# Sub-agent E · Persona 5 盲读 · mid_a (ch501–510)

> 兜底路径 demo run (2026-09-04 batch 14)。L1-agent，**不升级 effective_n**。
> persona 5 = 晋江新读者，不预设世界观，敏感情感碾压与人物动作。

## 1. 盲读对象
- pack: `mid_a`（ch501–510）。

## 2. 留存（让人心里疼过的关系动作）
| 章 | 留下 | 验证短语 |
|---|---|---|
| 504 | 是：苏漪把帕子攥紧，指节压住兰的绣线 = 身体 + 物件 + 关系三合一，新读者能立刻 get「这是告别」。 | 「苏漪把帕子攥紧，指节压住兰的绣线」 |
| 505 | 偏弱：叶观澜「拈起，没拆」= 克制不介入，新读者需要更多上下文才能 get 疼。 | 「拈起，没拆」 |
| 509 | 是：林窈替林夙问糖 → 苏挽还糖 + 自己答活 = 关系动作三连，新读者能 get「苏挽承担了」。 | 「自己答活」 |
| 510 | 否：林夙问余伯 = 信息灌入型，新读者不知道「肆南」是谁 = 弃读。 | 「肆南旧账」 |

## 3. drop 候选
| 章 | drop 理由 | 验证短语 |
|---|---|---|
| 510 | 「肆南旧账」「青田石印章」= 无世界观预设的新读者无法建模。 | 「肆南旧账」「青田石印章」 |

## 4. 留下理由（按 keep_if「出现一次让人心里疼过的关系动作」）

504 = 苏漪攥帕 + 苏挽站到日斜 = 关系动作 + 身体代价 = 满足 persona 5 keep_if。
走 509 = 「自己答活」= 关系升压 = 满足。
510 看不到关系动作，全是信息灌入 = drop。

## 5. 工艺清单（per 磨斧头研究 §4）
- **新读者门槛**：首章 180 字内 ≥ 3 个世界观术语 = 弃读（与 persona 3 一致）。
- **关系动作密度**：504 + 509 = 两次关系动作 / 10 章 = 满足 keep_if。

## 6. 与同点统计的关系
本报告 = L1 模拟，不计 effective_n。
**与 sub-agent A Demo / B / C / D 同点**：
- 同 drop 候选 = ch510（A / C / D / E 四个 persona 都 drop ch510）= **同点 = 4**。
- 同留下 = 504（A 留 504「苏挽抽帕搁在苏漪手心」= 关系动作；E 留 504「苏漪攥帕」= 同章同关系）。

**5-reader-cross §4 升级判断**：
- 同点 ≥ 3（drop 候选 ch510）= ✓
- diversity_score ≥ 0.5 = need to compute（4 个不同 persona + 不同 drop 理由 + 不同 pack_hash 不变）
- L2 ≥ 1 = ✗（sub-agent 模拟不升级 L2）

→ 同点过线 + diversity 待算 + L2 = 0 = **只够触发「方向」层，不够「结构性改稿任务」**。

## 7. 边界面
- **不**升级 effective_n。
- **不**写「读者会追」措辞。
- **不**写「新读者一定会 drop」类因果结论。
- **记**：本报告 + A + C + D 共同把 ch510 标为 drop 候选；**记**：本报告 + A 同点 = 1（504 留 + 504 同关系）。
