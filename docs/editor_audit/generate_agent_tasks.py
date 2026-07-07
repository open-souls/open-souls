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

# 读取全书诊断名册以获取最新的病变状态
ledger_path = os.path.join(docs_dir, "季01_病体诊断名册_全书.md")

infected_chapters = []
if os.path.exists(ledger_path):
    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 提取所有带有 🛑 [Ch XXX] 的章节号，这些是当前依然未修好的病体
    infected_chapters = [int(x) for x in re.findall(r'🛑 \[Ch (\d+)\]', content)]

# 已修复的章节 = 500章之后但在诊断名册里没有出现的章节
fixed_chapters = []
for f in files:
    num = get_num(f)
    if num >= 500 and num not in infected_chapters:
        fixed_chapters.append(num)

# 计算待修复章节
pending_chapters = sorted(list(set(infected_chapters)))

# 动态选取优先级最高（序号最小）的 5 个章节作为下一批派活目标
next_batch = pending_chapters[:5] if pending_chapters else []

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 写入指导性工作安排文档
tasks_path = os.path.join(docs_dir, "其他编辑Agent工作安排.md")
with open(tasks_path, "w", encoding="utf-8") as out_f:
    out_f.write(f"# 🤖 其他编辑 Agent 工作安排与任务看板\n\n")
    out_f.write(f"> **调度工具**: Antigravity Task Dispatcher v1.0\n")
    out_f.write(f"> **最近派活更新时间**: `{current_time}`\n")
    out_f.write(f"> **进度统计**: 累计确认病变 {len(infected_chapters) + len(fixed_chapters)} 章 | 已修复 {len(fixed_chapters)} 章 | 待修复 {len(pending_chapters)} 章\n\n")
    out_f.write("---\n\n")
    
    out_f.write("## 📌 1. 当前待领取的任务清单 (下一批次优先级最高)\n")
    out_f.write("请其他编辑 Agent 认领以下章节进行重写，并在重写完成后提交主编审核：\n\n")
    
    if not next_batch:
        out_f.write("🎉 **完美！所有系统性病变章节已全部修缮完毕！无待修任务。**\n\n")
    else:
        for ch in next_batch:
            filename = [f for f in files if get_num(f) == ch][0]
            out_f.write(f"### 📋 [待修缮] Ch {ch:03d} | {filename}\n")
            out_f.write(f"- **修缮指令**：根据大纲 §七 SOP 公式进行重写。去除所有“那一截”、“按完按完”、“偏右一寸”等物理坐标。将偏右/偏左一寸翻译为视线对齐或防备姿态。\n")
            out_f.write(f"- **爆点增压**：若涉及决战人物（林夙、阿湄、苏挽、叶观澜、林崇、林彻），必须融入大纲 §十 的“打脸增压与情绪释放”硬指标。\n\n")
            
    out_f.write("---\n\n")
    
    out_f.write("## 📜 2. 核心协作规范（所有 Agent 必须遵守）\n")
    out_f.write("1. **翻译公式**：严禁在正文中使用任何 `ch\\d+` 的前置章节直引。将所有的距离、偏正方位词，翻译为角色的体温、动作阻力、指节发白和衣物摩擦声。\n")
    out_f.write("2. **验收流程**：重写章节后，必须通过 `grep` 验证无 `按完` 及 `ch\\d+` 机器词，与 Ch500 以前的范文质量对齐，方可合入分支。\n")
    out_f.write("3. **工作区说明**：修改请直接覆盖 `seasons/01-xianxia/chronicle/` 下的源文件，15分钟后我的自动轮询会识别出您的更改，并更新看板进度。\n\n")
    
    out_f.write("---\n\n")
    
    out_f.write("## 📈 3. 最新已修缮章节归档\n")
    if not fixed_chapters:
        out_f.write("- 暂无归档章节。\n")
    else:
        out_f.write(f"以下 {len(fixed_chapters)} 个章节已由主编或编辑 Agent 成功修缮并归档：\n\n")
        # 打印最近修好的15章
        for ch in sorted(fixed_chapters)[-15:]:
            filename = [f for f in files if get_num(f) == ch][0]
            out_f.write(f"- `[x]` Ch {ch:03d} | {filename}\n")
        if len(fixed_chapters) > 15:
            out_f.write(f"- ... 及其他 {len(fixed_chapters) - 15} 个更早修缮的章节。\n")

print(f"[{current_time}] Agent task board updated.")
