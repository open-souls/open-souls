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

jargon_patterns = {
    "repeat_anwan": re.compile(r"按完按完|按完又按|按完按到位"),
    "repeating_segment": re.compile(r"那一截|这一截|那一斜|那一段"),
    "repeating_pos": re.compile(r"偏右一寸|偏左一寸|正中央偏右|偏右三尺"),
    "pos_loop_extended": re.compile(r"正中偏右那一段|正中偏右那一寸|偏右那段|正中偏右那|偏右一截|正中偏右|偏左那一|偏右那一"),
    "chapter_ref": re.compile(r"ch\d+"),
    "robotic_repetition": re.compile(r"自己接她自己|他自己自己|自己抬他自己"),
    "pressed_sixty_years": re.compile(r"压过六十年的那一种|压了六十年"),
    "shaped_self_y": re.compile(r"是他自己按住|是她自己按住|是他自己|是她自己"),
    "by_path_phrase": re.compile(r"的来路——是|的来路是|的来处——|的来处是|的去处——是"),
    "by_position_phrase": re.compile(r"的位——是|的位是"),
    "stop_loop": re.compile(r"停了|停住"),
    "throat_motion": re.compile(r"喉底压住|喉底动|喉底开|喉底"),
}

pre_500_infections = []
post_500_infections = []

for f in files:
    ch_num = get_num(f)
    filepath = os.path.join(base_dir, f)
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        
    parts = content.split("---")
    body = "---".join(parts[2:]) if len(parts) >= 3 else content
    body_clean = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    
    issues = []
    for issue_type, pattern in jargon_patterns.items():
        matches = pattern.findall(body_clean)
        if ch_num < 500 and issue_type == "repeating_segment" and len(matches) <= 2:
            continue
        if matches:
            issues.append((issue_type, len(matches), list(set(matches))))
            
    if issues:
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
            "samples": sample_lines
        }
        
        if ch_num < 500:
            pre_500_infections.append(report)
        else:
            post_500_infections.append(report)

# 写入合并报告（英文文件名）
out_path = r"c:\Users\stanc\github\open-souls\docs\editor_audit\chapter_diagnostic_ledger.md"
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(out_path, "w", encoding="utf-8") as out_f:
    out_f.write(f"# Season 01 Chapter Diagnostic Ledger (Ch1 - Ch714)\n\n")
    out_f.write(f"> **Audit Tool**: Antigravity Jargon Linter v1.4\n")
    out_f.write(f"> **Last Updated Timestamp**: `{current_time}` (Auto Audit Loop)\n")
    out_f.write(f"> **Status**: Pre-500 suspicious: {len(pre_500_infections)} | Post-500 suspicious: {len(post_500_infections)}\n\n")
    out_f.write("---\n\n")
    
    out_f.write("## 🟢 Part 1: Ch1 - Ch499 Minor Jargon Anomalies\n")
    if not pre_500_infections:
        out_f.write("✅ All text is clean.\n\n")
    else:
        for r in pre_500_infections:
            out_f.write(f"### 🛑 [Ch {r['chapter']:03d}] {r['filename']}\n")
            for itype, count, ex in r["issues"]:
                out_f.write(f"- `{itype}`: {count} matches (Sample: {ex})\n")
            out_f.write("```text\n")
            for s in r["samples"]:
                out_f.write(f"{s}\n")
            out_f.write("```\n\n")
            
    out_f.write("\n---\n\n")
    
    out_f.write("## 🔴 Part 2: Ch500 - Ch714 Systematic Machine Jargon\n")
    if not post_500_infections:
        out_f.write("✅ Clear! All machine jargon fixed.\n\n")
    else:
        for r in post_500_infections:
            out_f.write(f"### 🛑 [Ch {r['chapter']:03d}] {r['filename']}\n")
            for itype, count, ex in r["issues"]:
                out_f.write(f"- `{itype}`: {count} matches (Sample: {ex})\n")
            out_f.write("```text\n")
            for s in r["samples"]:
                out_f.write(f"{s}\n")
            out_f.write("```\n\n")

print(f"[{current_time}] Chapter audit complete.")
