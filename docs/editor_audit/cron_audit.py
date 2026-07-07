import os
import re
import yaml
import datetime
import sys

# Force output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle"
files = [f for f in os.listdir(base_dir) if f.endswith(".md") and not f.endswith(".bak")]

def get_num(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 9999
files.sort(key=get_num)

# 扩充检测 pattern —— v2 升级 (Loop #79 触发)
# 修复原版"repeating_pos"只抓 4 个变体导致漏报（正中偏右那段 / 正中偏右那一段 / 偏右那段 等都漏掉）
# 新增"press_loop"（按完按完 / 按完又按）"pos_loop_extended"（扩展物理坐标）"format_marker"（按/抬/看的位——是）
jargon_patterns = {
    # 复读模板（机械复读）
    "repeat_anwan": re.compile(r"按完按完|按完又按|按完按到位"),
    # 翻译公式禁用 segment（§七 SOP 第一条）
    "repeating_segment": re.compile(r"那一截|这一截|那一斜|那一段"),
    # 物理坐标循环（§七 SOP 第一条 — 翻译为：触觉/温度/视线对准/伸手距离）
    "repeating_pos": re.compile(r"偏右一寸|偏左一寸|正中央偏右|偏右三尺"),
    "pos_loop_extended": re.compile(r"正中偏右那一段|正中偏右那一寸|偏右那段|正中偏右那|偏右一截|正中偏右|偏左那一|偏右那一"),
    # 前文章节直引（§七 SOP 第三条 — 翻译为：触觉/情感记忆）
    "chapter_ref": re.compile(r"ch\d+"),
    # 机械复读（自我指涉空转）
    "robotic_repetition": re.compile(r"自己接她自己|他自己自己|自己抬他自己"),
    # 范式污染 6 件套（散文铁律 3.0 升级版）
    "pressed_sixty_years": re.compile(r"压过六十年的那一种|压了六十年"),
    "shaped_self_y": re.compile(r"是他自己按住|是她自己按住|是他自己|是她自己"),
    "by_path_phrase": re.compile(r"的来路——是|的来路是|的来处——|的来处是|的去处——是"),
    "by_position_phrase": re.compile(r"的位——是|的位是"),
    "stop_loop": re.compile(r"停了|停住"),
    "throat_motion": re.compile(r"喉底压住|喉底动|喉底开|喉底"),
}

# 按 ch_num 范围分层判据（v2.1 修正 —— Loop #79 修辞 anchor vs 真病体二分）
# 段 4 范文保护区（ch001-499）：停/是他自己 等都是合法修辞，**只在显著超标时报警**
# 段 5 病体高发区（ch500-714）：**硬阈值 0/1 报警**
# 段 6+（ch715-1000）：按 v4 散文铁律 4.0 阈值（停 ≤ 3，喉底 ≤ 4 等）
THRESHOLDS = {
    "段 4（ch1-499 范文保护）": {
        # 范文保护区：允许合法修辞，「停了」≤ 5 / 「shaped_self_y」≤ 5 不算病体
        "repeat_anwan": 0,
        "repeating_segment": 5,
        "repeating_pos": 0,
        "pos_loop_extended": 0,
        "chapter_ref": 10,   # ship 引用允许，单章 ≤ 10
        "robotic_repetition": 0,
        "pressed_sixty_years": 0,
        "shaped_self_y": 10,  # 正常叙事「是他自己」允许
        "by_path_phrase": 0,
        "by_position_phrase": 5,
        "stop_loop": 8,       # 范文允许 5-8 次
        "throat_motion": 5,
    },
    "段 5（ch500-714 病体高发）": {
        "repeat_anwan": 0,
        "repeating_segment": 3,
        "repeating_pos": 2,
        "pos_loop_extended": 2,
        "chapter_ref": 5,
        "robotic_repetition": 0,
        "pressed_sixty_years": 0,
        "shaped_self_y": 3,
        "by_path_phrase": 0,
        "by_position_phrase": 1,
        "stop_loop": 3,
        "throat_motion": 4,
    },
    "段 6+（ch715+ 决战）": {
        "repeat_anwan": 0,
        "repeating_segment": 3,
        "repeating_pos": 1,
        "pos_loop_extended": 1,
        "chapter_ref": 5,
        "robotic_repetition": 0,
        "pressed_sixty_years": 0,
        "shaped_self_y": 3,
        "by_path_phrase": 0,
        "by_position_phrase": 1,
        "stop_loop": 3,
        "throat_motion": 4,
    },
}

def get_threshold_segment(ch_num):
    if ch_num < 500:
        return "段 4（ch1-499 范文保护）"
    elif ch_num < 715:
        return "段 5（ch500-714 病体高发）"
    else:
        return "段 6+（ch715+ 决战）"

pre_500_infections = []
post_500_infections = []
frontmatter_pollution = []  # 新增：frontmatter 字段塞 long metadata 也算污染

for f in files:
    ch_num = get_num(f)
    filepath = os.path.join(base_dir, f)
    with open(filepath, "r", encoding="utf-8") as file:
        full_content = file.read()

    # 拆分 frontmatter + body
    parts = full_content.split("---")
    body = "---".join(parts[2:]) if len(parts) >= 3 else full_content
    body_clean = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)

    # body 端检测
    issues = []
    seg = get_threshold_segment(ch_num)
    thresholds = THRESHOLDS[seg]
    for issue_type, pattern in jargon_patterns.items():
        matches = pattern.findall(body_clean)
        threshold = thresholds.get(issue_type, 0)
        if len(matches) <= threshold:
            continue
        issues.append((issue_type, len(matches), list(set(matches))[:5]))

    # frontmatter 端检测（v2 新增 — Loop #79 §七 SOP 补则）
    # thread / beat 字段塞了位置说明 metadata = 字段污染
    fm_pollution = []
    if len(parts) >= 3:
        try:
            fm = yaml.safe_load(parts[1])
            if fm:
                for field in ["thread", "beat"]:
                    val = str(fm.get(field, ""))
                    if len(val) > 200:
                        fm_pollution.append((field, len(val), val[:80] + "..."))
        except yaml.YAMLError:
            fm_pollution.append(("yaml_parse_error", 0, "frontmatter YAML 解析失败（可能含 ** 加粗等 markdown 语法）"))

    if issues or fm_pollution:
        lines = body_clean.split("\n")
        sample_lines = []
        for line in lines:
            if any(pat.search(line) for pat in jargon_patterns.values()):
                if len(line.strip()) > 5:
                    sample_lines.append(line.strip())
                    if len(sample_lines) >= 3:
                        break

        report = {
            "chapter": ch_num,
            "filename": f,
            "issues": issues,
            "fm_pollution": fm_pollution,
            "samples": sample_lines,
            "body_chars": len(re.sub(r"\s", "", body_clean)),
            "dash_count": body_clean.count("——"),
            "zhongzheng_count": body_clean.count("正中偏右"),
            "pianyou_count": body_clean.count("偏右"),
            "ch_ref_count": len(re.findall(r"ch\d+", body_clean)),
        }

        if ch_num < 500:
            pre_500_infections.append(report)
        else:
            post_500_infections.append(report)

# 计算章节范围（动态，不再硬写 714）
all_chs = sorted(set(get_num(f) for f in files if get_num(f) < 9000))
max_ch = max(all_chs) if all_chs else 0
min_ch = min(all_chs) if all_chs else 0

# 写入合并报告
out_path = r"c:\Users\stanc\github\open-souls\docs\editor_audit\季01_病体诊断名册_全书.md"
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(out_path, "w", encoding="utf-8") as out_f:
    out_f.write(f"# 季01·全书章节病体体检名册 (Ch{min_ch} - Ch{max_ch})\n\n")
    out_f.write(f"> **诊断工具**: Antigravity Jargon Linter v2.0 (Loop #79 升级)\n")
    out_f.write(f"> **最近更新时间戳**: `{current_time}` (自动轮询审计)\n")
    out_f.write(f"> **检测项**: repeat_anwan / repeating_segment / repeating_pos / pos_loop_extended / chapter_ref / robotic_repetition / pressed_sixty_years / shaped_self_y / by_path_phrase / by_position_phrase / stop_loop / throat_motion / frontmatter long metadata\n")
    out_f.write(f"> **状态**: Ch{min_ch}-499 疑似 {len(pre_500_infections)} 章 | Ch500-Ch{max_ch} 疑似 {len(post_500_infections)} 章\n\n")
    out_f.write("---\n\n")

    out_f.write(f"## 🟢 第一部分：Ch{min_ch} - 499 局部轻微旧痕区\n")
    if not pre_500_infections:
        out_f.write("✅ 正文完全洁净。\n\n")
    else:
        for r in pre_500_infections:
            out_f.write(f"### 🛑 [Ch {r['chapter']:03d}] {r['filename']}\n")
            for itype, count, ex in r["issues"]:
                out_f.write(f"- `{itype}`: {count}次 (范例: {ex})\n")
            if r["fm_pollution"]:
                for fname, flen, fex in r["fm_pollution"]:
                    out_f.write(f"- ⚠️ frontmatter `{fname}` 字段长 {flen} 字符（>200）\n")
            out_f.write("```text\n")
            for s in r["samples"]:
                out_f.write(f"{s}\n")
            out_f.write("```\n\n")

    out_f.write("\n---\n\n")

    out_f.write(f"## 🔴 第二部分：Ch500 - Ch{max_ch} 系统性病变区\n")
    if not post_500_infections:
        out_f.write("✅ 无机器污染章节，病体清理完毕！\n\n")
    else:
        # 段位分层
        sections = {
            "段 4（ch500-549 · 范文保护区 · 应 0/章污染）": [r for r in post_500_infections if 500 <= r["chapter"] <= 549],
            "段 5（ch550-650 · Subagent 派活事故区 · 高发）": [r for r in post_500_infections if 550 <= r["chapter"] <= 650],
            "段 6（ch651-790 · 决战场）": [r for r in post_500_infections if 651 <= r["chapter"] <= 790],
            "段 6 后（ch791-1000 · 待写 · 不该有病体）": [r for r in post_500_infections if 791 <= r["chapter"] <= 1000],
        }
        for section_name, section_reports in sections.items():
            out_f.write(f"\n### {section_name}\n")
            if not section_reports:
                out_f.write("✅ 此段洁净。\n\n")
                continue
            out_f.write(f"🔴 污染章数: {len(section_reports)}\n\n")
            for r in section_reports:
                out_f.write(f"#### 🛑 [Ch {r['chapter']:04d}] {r['filename']}（{r['body_chars']} 字 · 破折号 {r['dash_count']} · 正中偏右 {r['zhongzheng_count']} · 偏右 {r['pianyou_count']} · ch## 直引 {r['ch_ref_count']}）\n")
                for itype, count, ex in r["issues"]:
                    out_f.write(f"- `{itype}`: {count}次 (范例: {ex})\n")
                if r["fm_pollution"]:
                    for fname, flen, fex in r["fm_pollution"]:
                        out_f.write(f"- ⚠️ frontmatter `{fname}` 长 {flen} 字符\n")
                out_f.write("```text\n")
                for s in r["samples"]:
                    out_f.write(f"{s}\n")
                out_f.write("```\n\n")

    # 新增：§七 SOP 复核段（Loop #79 升级 —— v4 PASS 不等于 §七 SOP PASS）
    out_f.write("\n---\n\n")
    out_f.write("## ⚠️ §七 SOP 复核段（v2.0 新增 · Loop #79 触发）\n\n")
    out_f.write("> **关键事实**：v4 散文铁律只抓 10 变体（`的方式/位/方向/力/时辰/样式/样子/光景/模样/样貌`），\n")
    out_f.write("> **不抓**：正中偏右物理坐标循环、ch[0-9]+ 直接引用、`的来处` 破折号循环。\n")
    out_f.write("> 下面这几章已通过 v4 散文铁律但 **§七 SOP FAIL**（必须人工复查 + 派修复 subagent）：\n\n")
    qise_fail = [r for r in post_500_infections if r["zhongzheng_count"] >= 3 or r["ch_ref_count"] >= 10 or r["dash_count"] >= 30]
    out_f.write(f"**§七 SOP FAIL 章节数**: {len(qise_fail)} / {len(post_500_infections)}\n\n")
    if qise_fail:
        out_f.write("| Ch | 文件名 | 字数 | 破折号 | 正中偏右 | 偏右 | ch## 直引 | 判定 |\n")
        out_f.write("|---|---|---|---|---|---|---|---|\n")
        for r in sorted(qise_fail, key=lambda x: -x["zhongzheng_count"]):
            verdict = "🔴 §七 FAIL"
            out_f.write(f"| {r['chapter']:04d} | {r['filename']} | {r['body_chars']} | {r['dash_count']} | {r['zhongzheng_count']} | {r['pianyou_count']} | {r['ch_ref_count']} | {verdict} |\n")
        out_f.write("\n")

    out_f.write("\n---\n\n")
    out_f.write("## 📋 §七 SOP 处理建议（按段位分层）\n\n")
    out_f.write("- **段 4（ch500-549）**：范文保护区，应 0 污染。若仍命中 → 检查是否 ZZG/ZZH 派活残留。\n")
    out_f.write("- **段 5（ch550-650）**：Subagent 派活事故高发区，**必须重写**（不亲修 —— 22 章 × 4 分钟 subagent vs 110 分钟亲修 = 派 ZZJ2 类专项修复）。\n")
    out_f.write("- **段 6（ch651-790）**：决战场，**已写章节**中 §七 SOP FAIL 章必须按 4 条翻译公式（物理坐标→触觉、自我指涉→心理意象、前文引用→两世意象、`X 的方式`→动作选择）全盘重写。\n")
    out_f.write("- **段 7-8（ch791-1000）**：尚未写完，派活 prompt 必须强制 attach §七.1 4 条翻译公式 + v4 散文铁律。\n\n")

print(f"[{current_time}] Auto audit v2.0 complete. Pre-500: {len(pre_500_infections)} | Post-500: {len(post_500_infections)} | §七 FAIL: {len(qise_fail)}")