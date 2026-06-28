"""
为每个 SSML 脚本派一个 claude -p 子代理，重点加情感标记，不靠速率快慢。

用法：
  python tools/tts_improve_ssml.py              # 全部 502 章
  python tools/tts_improve_ssml.py --chapters 1-10
  python tools/tts_improve_ssml.py --workers 8
"""

import os
import re
import subprocess
import concurrent.futures
import argparse
import sys
import tempfile

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = "tools/tts_scripts"
ENDPOINT   = "http://localhost:11436"
WORKERS    = 5

PROMPT = """\
你在改进一份中文有声书 SSML 脚本，引擎是 Microsoft Edge TTS，声线：
  Xiaoxiao（女，旁白/苏挽）、Yunxi（男，林夙/少年声）、Yunjian（男，赤渊/老成声）

## 核心原则
- **强调情感与自然，不靠速率快慢**
- 不要为了"有标记"而堆标记；每个标记都要有戏剧或情感理由

## 可用工具（优先级顺序）

### 1. `<mstts:express-as style="...">` ← 最重要
按场景切换情绪，不要整篇套同一个 style：
  - 平静旁白/叙事：narration-relaxed
  - 悲伤/压抑：sad
  - 温情/共情：empathetic（Xiaoxiao）/ affectionate（Xiaoxiao）
  - 愤怒/强硬对话：angry
  - 轻松闲聊：chat
  - Yunjian 旁白：documentary-narration

### 2. `<break time="Xms"/>` ← 情感停顿，不是节拍器
只放在真正有重量的地方：
  - 戏剧性反转前后：800–1200ms
  - 人物沉默 / 思考 / 克制：400–700ms
  - 段落自然呼吸：200–400ms
  - **不要每句末尾都加**

### 3. `<emphasis level="moderate/strong">` ← 情感高峰关键词
  - 场景核心词、角色最在意的那句话

### 4. `<prosody pitch="+X%/-X%">` ← 对话音调微调
  - 压抑/悲伤：-5% 左右
  - 强调/紧张：+5-8%
  - 不要 rate 快慢（章节标题那行 rate="slow" 可保留）

## 格式要求
- 保留 `<speak>` 外层
- 若使用 `mstts:` 标签，speak 开标签加 `xmlns:mstts="http://www.w3.org/2001/mstts"`
- 中文文本一字不改
- **直接输出改好的 SSML，不加解释，不加代码块**

## 当前 SSML
{content}"""


def improve_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    prompt = PROMPT.format(content=content)

    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = ENDPOINT

    # Write prompt to temp file to avoid Windows cmd line length limit
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8",
                                     delete=False) as tf:
        tf.write(prompt)
        tf_path = tf.name

    try:
        with open(tf_path, "r", encoding="utf-8") as tf:
            result = subprocess.run(
                ["claude.cmd", "-p", "--dangerously-skip-permissions", "-"],
                stdin=tf,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=180,
            )
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: {filepath}"
    except Exception as e:
        return f"ERROR: {filepath} — {e}"
    finally:
        os.unlink(tf_path)

    if result.returncode != 0:
        err = (result.stderr or "").strip()[:300]
        return f"FAIL [{result.returncode}]: {filepath} — {err}"

    output = (result.stdout or "").strip()

    # Strip code block if agent wrapped it
    if "```" in output:
        m = re.search(r"```(?:xml|ssml)?\n([\s\S]*?)```", output)
        if m:
            output = m.group(1).strip()

    if not output.lstrip().startswith("<speak"):
        preview = output[:200].replace("\n", "\\n")
        return f"BAD_OUTPUT: {filepath} — {repr(preview)}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output + "\n")

    return f"OK: {os.path.basename(filepath)}"


def parse_range(s: str):
    """'1-10' → [1..10]; '5' → [5]"""
    m = re.match(r"^(\d+)-(\d+)$", s)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    return [int(s)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapters", help="e.g. 1-50 or 7")
    parser.add_argument("--workers", type=int, default=WORKERS)
    args = parser.parse_args()

    all_files = sorted(
        os.path.join(SCRIPT_DIR, f)
        for f in os.listdir(SCRIPT_DIR)
        if f.endswith(".ssml")
    )

    if args.chapters:
        nums = set(parse_range(args.chapters))
        all_files = [
            f for f in all_files
            if (m := re.search(r"ch(\d+)\.ssml$", f)) and int(m.group(1)) in nums
        ]

    print(f"Processing {len(all_files)} files with {args.workers} workers …", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(improve_file, f): f for f in all_files}
        for future in concurrent.futures.as_completed(futures):
            print(future.result(), flush=True)


if __name__ == "__main__":
    main()
