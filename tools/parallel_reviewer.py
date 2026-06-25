# -*- coding: utf-8 -*-
import os
# Force use of active local API gateway and developer-key
os.environ["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:11435"
os.environ["ANTHROPIC_API_KEY"] = "developer-key"

import sys
import re
import concurrent.futures

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import llm
import prose_lint as PL

CHRONICLE = os.path.join(ROOT, "seasons", "01-xianxia", "chronicle")
STANDARD_PATH = os.path.join(ROOT, "docs", "standards", "文笔范文标准.md")

def read_standard():
    with open(STANDARD_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_chapter_file(num):
    candidates = [f for f in os.listdir(CHRONICLE) if re.match(rf"^{num:03d}-", f)]
    canonical = [f for f in candidates if not re.search(r"-(?:扩写|alt|draft|副本)", f)]
    chosen = (canonical or candidates)
    chosen.sort(key=lambda x: (len(x), x))
    if chosen:
        return os.path.join(CHRONICLE, chosen[0])
    return None

def run_review_for_chapter(num, standard_text):
    path = get_chapter_file(num)
    if not path:
        return f"Chapter {num} file not found."
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split frontmatter and body
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.S)
    if not m:
        return f"Chapter {num} frontmatter not found."
    
    frontmatter = m.group(1)
    body = m.group(2)
    
    # Skip if review and score are already present
    if "review:" in frontmatter and "score:" in frontmatter:
        return f"Chapter {num} already has review and score. Skipping."

    # Remove existing review and score if present
    # We want to replace existing review: | and score: lines
    fm_lines = frontmatter.split("\n")
    new_fm_lines = []
    in_review = False
    for line in fm_lines:
        if line.startswith("review:"):
            in_review = True
            continue
        if line.startswith("score:"):
            in_review = False
            continue
        if in_review:
            # Skip review lines (usually indented)
            if line.startswith(" ") or line.strip() == "":
                continue
            else:
                in_review = False
        new_fm_lines.append(line)
    
    cleaned_fm = "\n".join(new_fm_lines).strip()
    
    system_prompt = (
        "你是一个极其严格的小说主编，专门负责对照「文笔范文标准」对章节文笔进行评分和提供修改意见。\n"
        "请严格对照以下标准，对正文逐句进行分析打分。你的评语必须刻薄、专业、具体，直接指出哪一句行，哪一句垮了。\n\n"
        "【文笔七维标准】\n"
        f"{standard_text}\n\n"
        "请严格按以下 YAML 格式输出你的审稿结果（不要用 ```yaml 等 Markdown 代码块包裹，直接输出 YAML 内容，以 review: | 开头）：\n"
        "review: |\n"
        "  维度N<名>(分): 论据——引正文原句，点名对照范文哪一条（A/B/C/D/E/F/G/H/I/J），说明到位或差在哪。\n"
        "  修复方向: 一条可执行的改法——指出具体句子/位置，给出怎么改。\n"
        "score: N/14\n\n"
        "注意：\n"
        "1. 七维每维 0/1/2 分，满分 14 分。\n"
        "2. review 块中只需写有话可说的维度，通常 4-6 条，但必须同时包含满分维和失分维（如有），失分维必写为什么。\n"
        "3. 论据必须引正文里的真句，不空夸，并点名对照范文编号。\n"
        "4. review 的每一行都要有缩进（通常两个空格）。"
    )
    
    user_prompt = (
        f"请审阅以下章节的正文内容，并给出 YAML 格式的 review 和 score：\n\n"
        f"【正文】\n"
        f"{body}"
    )
    
    # We route to Sonnet/Haiku via llm.complete. Let's use scene_weight=6 (heavy/sonnet) to ensure high-quality reviews.
    response = llm.complete(system_prompt, user_prompt, scene_weight=6, max_tokens=4000)
    
    # Extract YAML block if user wrapped it in codeblocks
    if "```" in response:
        # Try to find YAML block
        m_yaml = re.search(r"review:.*score:\s*\d+/14", response, re.S)
        if m_yaml:
            yaml_part = m_yaml.group(0)
        else:
            yaml_part = response.strip("` \n")
            if yaml_part.startswith("yaml"):
                yaml_part = yaml_part[4:].strip()
    else:
        yaml_part = response.strip()
    
    # Double check format
    if not yaml_part.startswith("review:") or "score:" not in yaml_part:
        return f"Failed to get valid YAML format for Chapter {num}. Response: {response[:300]}"
    
    # Let's assemble the new frontmatter
    # Put review right after hook: | ... block or at the end
    fm_lines = cleaned_fm.split("\n")
    hook_start_idx = -1
    hook_end_idx = -1
    for i, line in enumerate(fm_lines):
        if line.startswith("hook:"):
            hook_start_idx = i
            for j in range(i + 1, len(fm_lines)):
                if fm_lines[j].strip() == "":
                    continue
                if not (fm_lines[j].startswith(" ") or fm_lines[j].startswith("\t")):
                    hook_end_idx = j
                    break
            else:
                hook_end_idx = len(fm_lines)
            break
            
    if hook_end_idx != -1:
        new_fm_lines = fm_lines[:hook_end_idx] + yaml_part.split("\n") + fm_lines[hook_end_idx:]
        final_fm = "\n".join(new_fm_lines)
    else:
        final_fm = cleaned_fm + "\n" + yaml_part
    
    # Remove excessive blank lines
    final_fm = re.sub(r"\n{3,}", "\n\n", final_fm)
    
    new_content = f"---\n{final_fm.strip()}\n---\n{body}"
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    return f"Successfully reviewed Chapter {num}."

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=502, help="Start chapter number")
    parser.add_argument("--count", type=int, default=5, help="Number of chapters to review backwards")
    args = parser.parse_args()
    
    standard_text = read_standard()
    
    chapters_to_review = []
    for i in range(args.count):
        num = args.start - i
        if num > 0:
            chapters_to_review.append(num)
            
    print(f"Starting parallel review for chapters: {chapters_to_review}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(run_review_for_chapter, num, standard_text): num for num in chapters_to_review}
        for future in concurrent.futures.as_completed(futures):
            num = futures[future]
            try:
                res = future.result()
                print(res)
            except Exception as e:
                print(f"Chapter {num} raised an exception: {e}")

if __name__ == "__main__":
    main()
