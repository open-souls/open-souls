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

# NOTE: `停了|停住` removed from patterns — legitimate narrative pause beats are not machine jargon.
# Only true machine-loop / physical-coord / robotic-repetition patterns flagged.
jargon_patterns = {
    "repeat_anwan": re.compile(r"按完按完|按完又按|按完按到位"),
    "repeating_segment": re.compile(r"那一截|这一截|那一斜"),
    "repeating_pos": re.compile(r"偏右一寸|偏左一寸|正中央偏右|偏右三尺"),
    "pos_loop_extended": re.compile(r"正中偏右那一段|正中偏右那一寸|偏右那段|正中偏右那|偏右一截|正中偏右|偏left那一|偏右那一"),
    "chapter_ref": re.compile(r"ch\d+"),
    "robotic_repetition": re.compile(r"自己接她自己|他自己自己|自己抬他自己"),
    "pressed_sixty_years": re.compile(r"压过六十年的那一种|压了六十年"),
    "by_path_phrase": re.compile(r"的来路——是|的来路是|的来处——|的来处是|的去处——是"),
    "by_position_phrase": re.compile(r"的位——是|的位是"),
    "throat_motion": re.compile(r"喉底压住|喉底动|喉底开|喉底压|喉底位|喉底一寸|喉底那一截"),
    # 按的位/按的那一截 — chapter-specific pathology when used as machine coord filler.
    # These are real jargon ONLY when density is high (>5 per chapter).
    "pressed_pos_dense": re.compile(r"按的位|按的那一截|按的位置|按的位是"),
}

pre_500_infections = []
post_500_infections = []

for f in files:
    ch_num = get_num(f)
    filepath = os.path.join(base_dir, f)
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    parts = content.split("---")
    body = "---\n".join(parts[2:]) if len(parts) >= 3 else content
    # Strip frontmatter fields that legitimately contain ch\d+ citations
    # (ships: cross-chapter anchor references, review: 维度 scores).
    # These are SOP-correct usage, NOT machine jargon.
    fm = parts[1] if len(parts) > 1 else ""
    for field in ["ships:", "review:", "score:"]:
        if field in fm:
            fm = re.split(rf'\n{field}', fm, maxsplit=1)[0].rstrip() + "\n"
    body = fm + body
    # Also strip any HTML comments
    body_clean = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    # Strip residual review 维度 lines (block scalars past split point)
    body_clean = re.sub(r'^\s*维度\d+[^\n]*\n?', '', body_clean, flags=re.MULTILINE)
    body_clean = re.sub(r'^\s*维度[一二三四五六七八九十0-9]+[：:][^\n]*\n?', '', body_clean, flags=re.MULTILINE)
    # Strip residual ships lines that survived the split (cross-chapter citations)
    body_clean = re.sub(r'^\s*[^\n]*ch\d+[^\n]*\n?', '', body_clean, flags=re.MULTILINE)
    
    issues = []
    body_lines = max(len([l for l in body_clean.split("\n") if l.strip()]), 1)
    for issue_type, pattern in jargon_patterns.items():
        matches = pattern.findall(body_clean)
        if ch_num < 500 and issue_type == "repeating_segment" and len(matches) <= 2:
            continue
        # pressed_pos_dense only flagged when count > 5 per chapter (machine-loop pathology)
        if issue_type == "pressed_pos_dense" and len(matches) <= 5:
            continue
        # repeating_segment: only flag when density > 100/1k body lines (machine-loop pathology)
        # Below that, repeated motifs like "她那一截袖口" (anchor reuse) are legitimate.
        if issue_type == "repeating_segment":
            density = len(matches) * 1000 / body_lines
            if density < 100:
                continue
        if matches:
            issues.append((issue_type, len(matches), list(set(matches)), round(len(matches)*1000/body_lines, 1)))
            
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
            for tup in r["issues"]:
                itype, count, ex, density = tup
                out_f.write(f"- `{itype}`: {count} matches, density {density}/1k lines (Sample: {ex})\n")
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
            for tup in r["issues"]:
                itype, count, ex, density = tup
                out_f.write(f"- `{itype}`: {count} matches, density {density}/1k lines (Sample: {ex})\n")
            out_f.write("```text\n")
            for s in r["samples"]:
                out_f.write(f"{s}\n")
            out_f.write("```\n\n")

print(f"[{current_time}] Chapter audit complete.")
