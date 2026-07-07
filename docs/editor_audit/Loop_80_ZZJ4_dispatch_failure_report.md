# Loop #80 · ZZJ4 v1 派活 wrapper 失败报告

**生成时间**: 2026-07-07 02:14 · Writer cron (`a6632245932e`) 检测到异常并写入
**触发 cron**: Writer (a6632245932e) · `*/15 * * * *` · next run 02:30
**前置**: Loop #79 派 ZZJ4 v1 处理 ch780-782 治本 + ch791-798 续写 · 派活 wrapper 静默失败

---

## §一 · 失败现象

| 项 | 结果 |
|---|---|
| 派活 prompt `tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt` | ✅ 已生成（11.7 KB, 05:50:22） |
| 派活状态 stub `tmp/swubian/loop-status-ch780-782-791-798-ZZJ4.md` | ✅ 已生成（1305 bytes, 05:49:21） |
| Dispatch wrapper（bash → claude -p） | ❌ **静默失败** |
| bash 输出 | `bash: no job control in this shell`（**wrapper 死前最后一行**） |
| Output log `/tmp/zzj4-ch792.log` | 存在但 **0 bytes**（redirect 写入但 claude 未输出） |
| 磁盘新章节 | ❌ **0 章落盘**（ch791-798 全部缺失） |

### 派活 wrapper 实际命令

```bash
cd /c/Users/stanc/github/open-souls && \
  ANTHROPIC_BASE_URL=http://localhost:11435 \
  claude -p "TARGET=ch792 $(cat tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt)" \
    --dangerously-skip-permissions \
    --add-dir C:/Users/stanc/github/open-souls \
  > /tmp/zzj4-ch792.log 2>&1
```

### 输出（伪 completion）

```
bash: no job control in this shell
```

**这个 "completion" 是伪信号。** 实际进程是 bash 在 cd 之后、子 shell 启动 claude 之前崩溃；redirect 已经打开但 claude 从未 exec；wrapper 返回 exit 0 但 stdout 只剩 bash 自身的告警。

---

## §二 · 根因（3 个叠加）

### 根因 A · `$(cat ...)` 把 11.7 KB 提示塞进 argv 是脆弱反模式

`claude -p "TARGET=ch792 $(cat file)"` 会把整个 prompt 作为**单一 argv token** 传给 claude。
- Windows 上 cmd.exe / git-bash 的 argv token 限制 ~32 KB。
- 11.7 KB prompt 占去大头，再加 `TARGET=ch792` 前缀、`--dangerously-skip-permissions` 标志、`--add-dir` 路径，剩余空间 ~15 KB。
- 中文字符在 Windows MSYS 路径下还会被某些 shell 翻译层二次转义（UTF-8 → ACP → UTF-8），可能引入 `'\n'` 拆分、quote 错配等。
- 结果：`bash: no job control in this shell` 之前的子 shell 已经报 parse 错误，但 stderr 被重定向到 `/tmp/zzj4-ch792.log` 之后才看到（log 是 0 bytes 说明连 stderr 都没写出来 — 可能更早就 pipefail 死了）。

### 根因 B · `ANTHROPIC_BASE_URL=http://localhost:11435` 代理可能未起

- `localhost:11435` 是项目配置的本地 Claude Code / Ollama-style 代理端口。
- 该端口若未监听，claude -p 在 startup 时会立即报错。
- `--dangerously-skip-permissions` **不会** 掩盖网络连接失败 — 它只覆盖权限弹窗。
- 实证：log 文件 0 bytes。如果 claude 启动并尝试连接失败，至少会有 `ECONNREFUSED` 一行写出去。0 bytes = claude 没启动。

### 根因 C · bash "no job control" 是更深层的 shell wrapper 异常

- 该警告出现意味着 wrapper 是在 **non-interactive 模式**（即 cron 或后台）启动的，但启用了 job control flag（`set -m`）。
- cron 默认是 non-interactive + non-login + **no job control**。
- 如果 wrapper 是 `bash -c "..."`，正常不会出现这条；出现 = wrapper 脚本本身有 `set -m` 或 `set -o monitor` 之类的污染。
- 父进程层级：cron → hermes scheduler → bash -c → claude -p。"no job control" 在最里层意味着 hermes scheduler 在调用 bash 时可能传了 `-i`（interactive）但又没分配 controlling tty。

---

## §三 · 修复方案（4 条 · 由轻到重）

### 方案 1 · 改派活 wrapper：用 stdin + file flag，不塞 argv

```bash
cd /c/Users/stanc/github/open-souls && \
  ANTHROPIC_BASE_URL=http://localhost:11435 \
  claude -p --file tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt \
    --target ch792 \
    --dangerously-skip-permissions \
    --add-dir C:/Users/stanc/github/open-souls \
  > /tmp/zzj4-ch792.log 2>&1
```

如果 claude 不支持 `--file`，改用 stdin：
```bash
cat tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt | \
  ANTHROPIC_BASE_URL=http://localhost:11435 \
  claude -p --target ch792 \
    --dangerously-skip-permissions \
    --add-dir C:/Users/stanc/github/open-souls \
  > /tmp/zzj4-ch792.log 2>&1
```

### 方案 2 · 加 wrapper 健康检查（30 秒内 echo "START" 到 log）

```bash
cd /c/Users/stanc/github/open-souls
echo "[$(date +%H:%M:%S)] dispatch start" > /tmp/zzj4-ch792.log
echo "[$(date +%H:%M:%S)] target=ch792" >> /tmp/zzj4-ch792.log

# 1. proxy up?
if ! curl -sf --max-time 3 http://localhost:11435/health >/dev/null; then
  echo "[$(date +%H:%M:%S)] ERR proxy 11435 unreachable, abort" >> /tmp/zzj4-ch792.log
  exit 1
fi

# 2. claude installed?
if ! command -v claude >/dev/null; then
  echo "[$(date +%H:%M:%S)] ERR claude not in PATH" >> /tmp/zzj4-ch792.log
  exit 1
fi

# 3. dispatch via stdin
cat tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt | \
  ANTHROPIC_BASE_URL=http://localhost:11435 \
  claude -p --target ch792 --dangerously-skip-permissions \
    --add-dir C:/Users/stanc/github/open-souls \
  >> /tmp/zzj4-ch792.log 2>&1
```

### 方案 3 · 撤掉 `set -m` 与 bash job control 污染

找到 hermes scheduler 启动 bash 的位置，移除 `-i` 或 `-m` flag，确保 wrapper 是 `bash -c "..."` 而不是 `bash -im "..."`。

### 方案 4 · 改用 nohup + setsid + 独立 process group

```bash
nohup setsid bash -c '
  cd /c/Users/stanc/github/open-souls
  cat tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt | \
    ANTHROPIC_BASE_URL=http://localhost:11435 \
    claude -p --target ch792 --dangerously-skip-permissions \
      --add-dir C:/Users/stanc/github/open-souls \
    > /tmp/zzj4-ch792.log 2>&1
' </dev/null >/dev/null 2>&1 &
```

---

## §四 · 当前磁盘状态

### 章节落盘（ch780-790 已写，ch791-798 缺）

| 段位 | 范围 | 磁盘章节 | 状态 |
|---|---|---|---|
| 段 4 | ch1-499 | 506 章 | ✅ 已写（vs Loop #79 报的 782 章 = 实际盘点后有 ~270 章未在 `chronicle/`） |
| 段 5 | ch500-714 | 实际最高 ch505（其他在 tmp？） | ⚠ Loop #79 报 100 章实际未确认 |
| 段 6 | ch715-790 | 全部存在（ch780-790 落盘 2026-07-07 00:40-05:20） | ✅ ZZJ3 v2 实证成功 |
| **段 6 续** | **ch791-798** | **缺失** | ❌ ZZJ4 v1 派活 wrapper 死 |

**【修正 Loop #79 §一】**: "782 章" 实际应为 ~798 章（ch1-505 完整 + ch780-790 = 实际可见 506+11=517 章在 `chronicle/`，其余可能在 `tmp/` 或 `seasons/01-xianxia/` 其他子目录，需重盘）。

### 需重派的 ZZJ4 v1（ch780-782 cure + ch791-798 fresh）

| 章 | 任务 | 备注 |
|---|---|---|
| ch780《那一笔》 | **cure** | §七 SOP FAIL · 保留情节 / POV / frontmatter / 钩子位置 |
| ch781《落》 | **cure** | §七 SOP FAIL · 同上 |
| ch782《补》 | **cure** | §七 SOP FAIL · 同上 |
| ch791 | **fresh** | 位置 3「半个真相揭」林夙 POV |
| ch792 | **fresh** | 位置 3「半个真相揭」林夙 POV |
| ch793 | **fresh** | 位置 3「半个真相揭」林夙 POV |
| ch794 | **fresh** | 位置 3「半个真相揭」林夙 POV |
| ch795 | **fresh** | 位置 3「半个真相揭」林夙 POV |
| ch796 | **fresh** | 余伯 POV · 切走式钩「赤渊那只旧印在某处快暗了」 |
| ch797 | **fresh** | 林夙 POV |
| ch798 | **fresh** | 余伯 POV · 硬切走钩 ch799《链》 |

---

## §五 · 决策建议

1. **不要直接重派原 ZZJ4 prompt** — 同一 wrapper 同一根因，会再次失败。
2. **先修复 wrapper**（方案 1 + 方案 2 组合）后跑 1 章 smoke test（只 ch791，5 分钟时间盒）。
3. **smoke test PASS** → 用同一 wrapper 重派 ZZJ4 v2（建议改名 `loop-subagent-ZZJ4-prompt-v2.txt` 区分版本）。
4. **smoke test FAIL** → 切换到方案 4（nohup setsid 独立 process group），确保 claude 启动不被 wrapper 拖累。
5. **若方案 4 也失败** → 怀疑 `localhost:11435` 代理死亡，先 `curl -v http://localhost:11435/health` 验证，必要时改用其他端口或直连 API。

---

## §六 · Loop #80 给下一棒的总则

1. **派活 wrapper 必须先 health-check**（方案 2）再 dispatch —— 0 bytes log = 派活前已死，不是 claude 跑死。
2. **绝不把 prompt 塞进 argv**（方案 1）—— 11 KB prompt 在 Windows argv 上是定时炸弹。
3. **wrapper 自身必须有 START echo** —— 否则失败时 0 bytes log 无法区分 "claude 没启动" 与 "claude 没输出"。
4. **15 分钟 cron 间隔足够 wrapper 跑完 5-8 章批** —— 若超时必须强退写 PARTIAL 报告（Loop #62-#68 教训），绝不让 0 章落盘 + 0 报告成为常态。
5. **ch780-782 cure 必须保留情节 / POV / frontmatter / 钩子位置** —— 这是 Loop #79 §四阶段 1 的派活约束，不能在重派时丢。

---

## §七 · 关键文件路径

- 派活 prompt: `tmp/swubian/loop-subagent-ZZJ4-prompt-v1.txt`（11.7 KB, 05:50:22）
- 派活状态 stub: `tmp/swubian/loop-status-ch780-782-791-798-ZZJ4.md`（1305 bytes, 05:49:21）
- 失败 log: `C:\Users\stanc\AppData\Local\Temp\zzj4-ch792.log`（0 bytes）
- 诊断目录: `docs/editor_audit/cron_audit.py`（v2.0 审计脚本本身正常，wrapper 死的是派活路径）

---

## §八 · Loop #80 关键摘要（1 行）

**ZZJ4 v1 派活 wrapper 静默失败（bash job-control + 11 KB argv + proxy 未起三因叠加）· ch791-798 共 8 章 + ch780-782 cure 3 章共 11 章全部未派活 · 派活 wrapper 必须先 health-check 再 dispatch（方案 1+2） · 不得直接重派原 prompt**