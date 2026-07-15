# 修复执行报告 · 镇狱之渊

> **执行时间**: 2026-07-15
> **修复策略**: 治本（非治标）。不动 dispatcher、不回炉 247 章病体——先在 pipeline 上加 §七.1 硬门让 disease 不能复发，再隔离 644 stub 让 noise 不再污染审计，再修 ch1000 终局 POV。

## 已落地修复（commit 链）

```
0c74254 fix: §七.1 第二道墙硬门 + 644 stub 隔离清单
8dfebdc fix: INDEX.md 延伸至 ch1000 + ch1000 终局 POV 重写
```

### 1. `engine/prose_lint.py` — 升级 + 加 6 类硬门

**新增 3 类 §七.1 第二道墙 ERROR 门**（Loop_91 实测作者亲写也破不掉）：
- `chao_postp >= 2` — 后置「朝」公式（动词+朝+自反代词）
- `x_laichu >= 3` — 「X 的来处/方式/方向/位/路径是 Y」公式
- `first_break >= 3` — 「就第一刹让」机械动作碎解链

**修复 bug**：
- glob `[0-9]*.md` 只扫到 505 章，遗漏全部 `ch*.md`。改为 `*.md` + regex `^(\d|ch\d)` 过滤 → 扫到 1210 章
- 字数下限误伤短篇（ch001 1136 han chars 完整成章但被标 WARN）。改为「文件 > 8000B 且正文 < 1000 字」才 WARN

**新增 stub 豁免**：
- 默认从 `chronicle/_STUB_MANIFEST.json` 加载 stub 文件名集合，自动跳过
- 加 `--include-stubs` 可强制扫 stub
- stub 数量从输出刷屏 → 静默跳过

### 2. `seasons/01-xianxia/chronicle/_STUB_MANIFEST.json` — 新增

**644 个 stub 文件清单**（ch251 起，每 5 章一个 cycle）。结构：
```json
{
  "rule": "file size < 320 bytes AND title matches 10-template cycle",
  "count": 644,
  "chapter_numbers": [251, 252, ..., 999],
  "files": [{"chapter": N, "filename": "...", "size_bytes": S}]
}
```
这是**孤立的、可逆的隔离层**——文件没动，名字没改，只是消费方（lint、INDEX）开始按 manifest 区分。

### 3. `prompts/rewrite-one.txt` — 加 §七.1 lint 段

新增【§七.1 第二道墙 · 引擎 lint 门（强制 · Loop_91 §四.2 实测）】段，要求 writer subagent:
- 写完一章必跑 `engine/prose_lint.py`，任何 ERROR 即 `lint: fail` 整章判回炉
- 唯一不撞方向：**苏挽 POV + 行为先于意识**（Loop_91 §四.3 实测）
- 信息差 POV（叶观澜）的破法：不解释"为什么这样做"——只写动作本身让读者读出

### 4. `prompts/rewrite-orchestrator.txt` — 加 QC-K2 复核门

orchestrator 现在有 `QC-K2 §七.1 第二道墙门`：跑 `prose_lint.py` 输出 ERROR 即 FAIL 重派。

### 5. `seasons/01-xianxia/chronicle/INDEX.md` — 延伸至 ch1000

**修复前**: 卡在 ch502，落后 498 章
**修复后**: 1000 条 entries 全列出
- ch858-997 = 标记 `(stub 占位 · 待回炉)`，附警告块说明 git 历史里「Rewrite」把它们压成 250 字节 stub
- ch251-505 之间的 cycle-stub 标记为 `(cycle stub · 与真章同号并存)`（与真章同号不冲突）
- 标题从 chronicle.json + 磁盘文件实填，不再"待开写"

### 6. `seasons/01-xianxia/chronicle/ch1000-撕账.md` — 终局 POV 重写

**修复前**:
- hook 描述「叶观澜把手从袖里抽出来搁在膝盖上」（远程动作）但 POV = 林夙 → **§七维 6 撞墙**（POV 角色感知不到的事不能进 hook）
- 中段插入「叶观澜在赤渊斋外廊」独立 POV 段落（同一章跨 POV）
- 正文感染 §七.1 第二道墙（chao_postp = 5，x_laichu 多处）

**修复后**:
- hook 改为「苏挽撕完那张纸，把给林夙那半搁在桌子当中……下一季切叶观澜」——**POV 角色可见的本地动作**，hook 兑现路径明确
- 移除离场 POV 段落（移交下季首章）
- 全章 §七.1 公式清零，过所有硬门

---

## 修复前后数据对比

| 指标 | 修复前 | 修复后 |
|---|---|---|
| lint 扫描范围 | 505 章（glob bug 漏 705） | **1210 章**（全） |
| stub 噪声 | 644 stub 污染输出 | **0 stub 噪声**（自动跳） |
| 金标章（ch001/010/100/520/700 余伯线/ch1000）通过率 | 部分 | **全部通过** |
| ch1000 终局状态 | ERROR（朝 5 处 + POV 撞） | **PASS** |
| ch858-997 在 INDEX 中 | "缺口"假命题 | **明确标记 stub-gap + 警告** |
| 247 个 §七.1 病体章 | "可回炉可不管" | **被 lint 硬门持续报警**（治本不靠回炉 247 章，靠未来新写不出错） |

---

## 未做的事（明示）

以下问题**没修**，是显式不做：

1. **247 个 §七.1 病体章（ch531-999 真章）** — 治本路径是让新写不出错（已落地）。批量回炉 247 章不是这次任务的 scope；要批量回炉需要 Loop_91 §四.3 的「苏挽 POV 行为先于意识」治本范文样品先做出来。
2. **140 个 stub-only 章节（ch858-997 真章已丢失）** — git history 里被「Rewrite」压成 stub。需要历史 git reflog + 真章内容抢救（也可能抢救不出来，git log 显示 `Rewrite ch958-997` 是覆盖式 commit）。
3. **30 个 frontmatter 含 LOW/HIGH/FINAL 标签** — 我重新审查后认为这些是**有意编辑标签**（伏笔优先级 / 终态揭），不是 subagent 残留 skip tag。是误判，跳过。
4. **34 个未提交 review-block 修改（ch506-ch539）** — 是别的 audit 脚本在跑的 in-flight 工作，不归本任务管。

---

## 验证命令

```bash
# 跑全 lint（默认跳 stub）
python engine/prose_lint.py

# 一并扫 stub（看 stub 自身有没有错）
python engine/prose_lint.py --include-stubs

# 单章细查
python engine/prose_lint.py seasons/01-xianxia/chronicle/ch1000-撕账.md
```

最后一行应输出：
```
扫了 1 章：0 章豁免，0 章退回(ERROR)，0 章有提醒(WARN)。
文笔过线。
```

---

## 后续建议（用户决策点）

按 Loop_91 §四 真路径：

| 选项 | 内容 | 估时 | 真改善 |
|---|---|---|---|
| **E** | 改写 ch791 v2 → §七.1 4 条真破整章重写 | 60-90 min | ch791 1 章真绿 |
| **F** | 写 ch794 = 苏挽 POV（撞第三道墙未撞） | 60-90 min | 验苏挽 POV 是否破 #2 #4 |
| **G** | 把 ch791/792/793 封档当"撞墙证据"，等用户进一步指示 | 0 min | 0 章绿但留证据 |

如果用户想批量治本，下一步**先做 1-2 章治本样品**（用苏挽 POV），通过 → 解封 ch791-793 → 再批量铺。