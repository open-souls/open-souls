# Editorial Cron System Bootstrap Instructions

This folder contains backup scripts for the automated audit and task dispatch systems. In case of a system reset or environment migration, follow these instructions to re-bootstrap the loops.

---

## 🚀 Bootstrap Commands

To set up the automated sweeps again, run the following two `schedule` tool calls inside your agent shell:

### 1. 30-Minute Chapter Diagnostic Loop
* **Schedule Mode**: Cron
* **Cron Expression**: `*/30 * * * *`
* **Command Prompt**: 
  `Run the automatic novel audit sweep script python c:\Users\stanc\github\open-souls\docs\editor_audit\cron_chapter_audit.py and update the ledger.`

### 2. 15-Minute Task Board Dispatch Loop
* **Schedule Mode**: Cron
* **Cron Expression**: `*/15 * * * *`
* **Command Prompt**: 
  `Run the dynamic editor agent task dispatcher script python c:\Users\stanc\github\open-souls\docs\editor_audit\cron_agent_task_dispatcher.py and update the task board.`

---

## 📂 Backup Scripts Reference

* **[cron_chapter_audit.py](file:///c:/Users/stanc/github/open-souls/docs/editor_audit/cron/cron_chapter_audit.py)**: Loads all `chronicle/*.md` files, verifies styling parameters (eliminating '按完', index tags, and 3D offset variables), and updates `chapter_diagnostic_ledger.md`.
* **[cron_agent_task_dispatcher.py](file:///c:/Users/stanc/github/open-souls/docs/editor_audit/cron/cron_agent_task_dispatcher.py)**: Compares current repository files with the ledger to figure out the active queue, and writes the top 5 priorities to `agent_work_schedule.md`.
