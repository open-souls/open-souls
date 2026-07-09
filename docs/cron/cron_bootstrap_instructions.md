# Editorial Cron System Bootstrap Instructions

This folder contains backup scripts and core configurations for the automated audit and task dispatch systems. In case of a system reset or environment migration, follow these instructions to re-bootstrap the loops.

---

## 🚀 Bootstrap Commands

To set up the automated sweeps again, run the following two `schedule` tool calls inside your agent shell:

### 1. 60-Minute Chapter Diagnostic Loop
* **Schedule Mode**: Cron
* **Cron Expression**: `*/60 * * * *`
* **Command Prompt**: 
  `Run the automatic novel audit sweep script python c:\Users\stanc\github\open-souls\docs\editor_audit\cron_chapter_audit.py and update the ledger.`

### 2. 30-Minute Task Board Dispatch Loop
* **Schedule Mode**: Cron
* **Cron Expression**: `*/30 * * * *`
* **Command Prompt**: 
  `Run the dynamic editor agent task dispatcher script python c:\Users\stanc\github\open-souls\docs\editor_audit\cron_agent_task_dispatcher.py and update the task board.`

---

## 💡 How to Manually Invoke Local `claude -p` for Any Chapter (Single-File Method)

Rather than keeping redundant prompt copies, you can dynamically prepend the target chapter ID and pipe it to Claude via standard input.

To manually trigger a rewrite for **Ch 519** (or any other chapter), run this single-line command in PowerShell:

```powershell
$env:ANTHROPIC_BASE_URL="http://localhost:11435"; ("TARGET=ch519`n" + (Get-Content -Raw C:\Users\stanc\github\open-souls\prompts\rewrite-one.txt)) | claude -p --dangerously-skip-permissions --add-dir C:/Users/stanc/github/open-souls > C:\Users\stanc\github\open-souls\prompts\.results\ch519.log 2>&1
```
