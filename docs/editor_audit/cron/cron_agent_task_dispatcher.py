import os
import re
import datetime
import sys

# Force output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle"
docs_dir = r"c:\Users\stanc\github\open-souls\docs\editor_audit"

files = [f for f in os.listdir(base_dir) if f.endswith(".md") and not f.endswith(".bak")]
def get_num(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 9999
files.sort(key=get_num)

# 读取英文版全书诊断名册
ledger_path = os.path.join(docs_dir, "chapter_diagnostic_ledger.md")

infected_chapters = []
if os.path.exists(ledger_path):
    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Extract chapter numbers from 🛑 [Ch XXX] markers
    infected_chapters = [int(x) for x in re.findall(r'🛑 \[Ch (\d+)\]', content)]

# 已修复的章节
fixed_chapters = []
for f in files:
    num = get_num(f)
    if num >= 500 and num not in infected_chapters:
        fixed_chapters.append(num)

pending_chapters = sorted(list(set(infected_chapters)))

# Priority order: by chapter number ascending (subagents work earliest issues first).
# Within same range, prefer higher-jargon-density chapters if density info available.
def density_hint(ch):
    """Extract max density from ledger entry for chapter ch."""
    pattern = rf'### 🛑 \[Ch {ch:03d}\][\s\S]*?(?=### 🛑|\Z)'
    m = re.search(pattern, content)
    if not m:
        return 0
    block = m.group(0)
    densities = [float(x) for x in re.findall(r'density ([\d.]+)/1k lines', block)]
    return max(densities) if densities else 0

pending_chapters.sort(key=lambda c: (c, -density_hint(c)))
next_batch = pending_chapters[:5] if pending_chapters else []

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 写入英文版工作安排文档
tasks_path = os.path.join(docs_dir, "agent_work_schedule.md")
with open(tasks_path, "w", encoding="utf-8") as out_f:
    out_f.write(f"# Agent Work Schedule & Task Board\n\n")
    out_f.write(f"> **Dispatcher**: Antigravity Task Dispatcher v1.1\n")
    out_f.write(f"> **Last Dispatched Timestamp**: `{current_time}`\n")
    out_f.write(f"> **Progress**: Total infected: {len(infected_chapters) + len(fixed_chapters)} | Fixed: {len(fixed_chapters)} | Pending: {len(pending_chapters)}\n\n")
    out_f.write("---\n\n")
    
    out_f.write("## 📌 1. Queue of Pending Editorial Assignments\n")
    out_f.write("Subagents must claim and rewrite the following chapters, then submit for review:\n\n")
    
    if not next_batch:
        out_f.write("🎉 **All machine jargon has been successfully cleared!**\n\n")
    else:
        for ch in next_batch:
            filename = [f for f in files if get_num(f) == ch][0]
            out_f.write(f"### 📋 [PENDING] Ch {ch:03d} | {filename}\n")
            out_f.write(f"- **Guidelines**: Rewrite according to `season_01_editorial_blueprint.md` §七 (SOP translations). Eliminate words like '那一截', '按完按完', and physical dimensional offsets.\n")
            out_f.write(f"- **Climax Payoff**: If rewriting showdown chapters, make sure to integrate the catharsis requirements in §十.\n\n")
            
    out_f.write("---\n\n")
    
    out_f.write("## 📜 2. Collaboration Protocol\n")
    out_f.write("1. **Translation Rules**: Never use inline chapter code references like `ch\\d+`. Translate coordinate positions into relative poses and sensory details.\n")
    out_f.write("2. **Git Commit**: Commit changes directly to `seasons/01-xianxia/chronicle/`. The automated dispatcher script will verify the changes in 15 minutes and pop the chapter out of the queue.\n\n")
    
    out_f.write("---\n\n")
    
    out_f.write("## 📈 3. Archival of Fixed Chapters\n")
    if not fixed_chapters:
        out_f.write("- No chapters fixed yet.\n")
    else:
        out_f.write(f"The following {len(fixed_chapters)} chapters have been successfully cleaned and archived:\n\n")
        for ch in sorted(fixed_chapters)[-15:]:
            filename = [f for f in files if get_num(f) == ch][0]
            out_f.write(f"- `[x]` Ch {ch:03d} | {filename}\n")
        if len(fixed_chapters) > 15:
            out_f.write(f"- ... and {len(fixed_chapters) - 15} other earlier chapters.\n")

print(f"[{current_time}] Task schedule board updated.")
