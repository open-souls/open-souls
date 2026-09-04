# -*- coding: utf-8 -*-
"""P3 v3: handle 1-space indent + re-process all 13 remaining."""
from __future__ import annotations
import os, re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHRON = ROOT / "seasons" / "01-xianxia" / "chronicle"

sys.path.insert(0, str(ROOT / "engine"))
import prose_lint as PL

RE_FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RE_KV = re.compile(r"^([A-Za-z_]+):\s*(.*)$")


def split_front_matter(text):
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    head = m.group(1)
    body = text[m.end():]
    out = {}
    cur_key, cur_buf = None, []
    for line in head.splitlines():
        if line.startswith("  ") and cur_key:
            cur_buf.append(line[2:])
            continue
        if cur_key:
            out[cur_key] = "\n".join(cur_buf).strip()
        m2 = RE_KV.match(line)
        if m2:
            cur_key, val = m2.group(1), m2.group(2)
            cur_buf = [val] if val else []
        else:
            cur_key, cur_buf = None, []
    if cur_key:
        out[cur_key] = "\n".join(cur_buf).strip()
    return out, body


def get_hook(text):
    fm, _ = split_front_matter(text)
    return fm.get("hook", "")


def clean_pipe(s):
    if not s:
        return ""
    if s.startswith("|"):
        s = s[1:]
    return re.sub(r"\n\s+", "\n", s).strip()


def pick_anchor(body):
    text = re.sub(r"^#.*$", "", body, flags=re.M)
    text = re.sub(r"^\*+\s*\*+$", "", text, flags=re.M)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return ""
    pieces = []
    for para in reversed(paragraphs[-5:]):
        para = re.sub(r"\*\*", "", para).strip()
        sents = re.split(r"(?<=[。！？!?])", para)
        sents = [s.strip() for s in sents if s.strip()]
        if sents:
            pieces.insert(0, sents[-1])
        else:
            pieces.insert(0, para)
        merged = "".join(pieces)
        if len(merged) >= 18:
            if len(merged) > 30:
                merged = merged[-30:]
            return merged
    merged = "".join(pieces)
    return merged[-30:] if len(merged) > 30 else merged


def main():
    files = sorted(CHRON.glob("*.md"))
    files = [p for p in files if p.name not in ("INDEX.md", "_STUB_MANIFEST.json") and not p.name.startswith("test_")]

    fixed = []
    failed = []
    for p in files:
        text = p.read_text(encoding="utf8")
        hook = clean_pipe(get_hook(text))
        first8 = hook[:8]
        body_for_match = PL.body_of(text)
        if first8 and first8 in body_for_match:
            continue
        _, body = split_front_matter(text)
        anchor = pick_anchor(body)
        if not anchor or len(anchor) < 8:
            failed.append((p.name, "no_anchor"))
            continue
        if len(anchor) > 30:
            anchor = anchor[-30:]
        # Match hook block with 1 or 2 space indent
        new_text = re.sub(
            r"(hook:\s*\|\s*\n)((?:[ \t]+.*\n?)+)",
            lambda m: m.group(1) + "  " + anchor + "\n",
            text,
            count=1,
        )
        if new_text == text:
            failed.append((p.name, "no_hook_block"))
            continue
        p.write_text(new_text, encoding="utf8")
        fixed.append((p.name, anchor))

    out_path = ROOT / "prompts" / ".notes" / "_p3_plan.json"
    out_path.write_text(json.dumps({
        "fixed": [{"file": f, "anchor": a} for f, a in fixed],
        "failed": [{"file": f, "reason": r} for f, r in failed],
    }, ensure_ascii=False, indent=2), encoding="utf8")
    print("P3 v3:", len(fixed), "fixed,", len(failed), "failed")


if __name__ == "__main__":
    main()
