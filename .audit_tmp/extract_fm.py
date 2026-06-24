#!/usr/bin/env python3
"""Extract frontmatter (pov, cast, chapter) for all 424 chapters."""
import os
import re
import json
import sys
from pathlib import Path

CHRON = Path(r"C:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle")
files = sorted([f for f in CHRON.glob("*.md") if f.name != "INDEX.md"])

import yaml

def patch_anchors_block(text):
    """The anchors block uses unquoted multi-line values for 场景: and 触发条件:.
    PyYAML chokes because it can't tell where the value ends. Pre-quote them."""
    lines = text.split("\n")
    out = []
    i = 0
    in_anchors = False
    while i < len(lines):
        line = lines[i]
        if re.match(r"^anchors:\s*$", line):
            out.append(line)
            in_anchors = True
            i += 1
            continue
        if in_anchors:
            # Detect end of anchors block: top-level key (no leading spaces)
            if line and not line[0].isspace():
                in_anchors = False
                out.append(line)
                i += 1
                continue
            # In anchors, fix multi-line unquoted values for 场景: and 触发条件:
            m = re.match(r"^(\s+)(场景|触发条件):\s+(.+)$", line)
            if m:
                indent, key, val = m.group(1), m.group(2), m.group(3)
                # If value contains line break or doesn't end cleanly, force-quote
                if ":" in val and not (val.startswith('"') or val.startswith("'")):
                    val_q = '"' + val.replace('"', '\\"') + '"'
                    out.append(f"{indent}{key}: {val_q}")
                    i += 1
                    continue
        out.append(line)
        i += 1
    return "\n".join(out)

out = []
err_files = []
for f in files:
    text = f.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        continue
    end = text.find("\n---", 4)
    if end == -1:
        continue
    fm_text = text[4:end]
    fm_text_patched = patch_anchors_block(fm_text)
    try:
        fm = yaml.safe_load(fm_text_patched)
        if not isinstance(fm, dict):
            fm = {}
    except Exception as e:
        err_files.append((f.name, str(e)[:120]))
        fm = {}

    chap = fm.get("chapter", 0)
    try:
        chap = int(chap)
    except:
        chap = 0
    pov = fm.get("pov", "")
    if not isinstance(pov, str):
        pov = str(pov)
    cast = fm.get("cast", [])
    if not isinstance(cast, list):
        cast = []
    out.append({"file": f.name, "chapter": chap, "pov": pov, "cast": cast})

out.sort(key=lambda x: x["chapter"])
print(f"Total: {len(files)}, Parsed: {len(out)}, YAML errors: {len(err_files)}", flush=True)
for name, err in err_files:
    print(f"  ERR {name}: {err}", flush=True)

out_path = Path(r"C:\Users\stanc\github\open-souls\.audit_tmp\fm.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False)
print(f"Wrote: {out_path}", flush=True)
