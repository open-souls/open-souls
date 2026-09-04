# -*- coding: utf-8 -*-
"""P3 v7: also handle multi-paragraph fragmented lines."""
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
        if (line.startswith("  ") or line.startswith(" ")) and cur_key and line != cur_key + ":":
            stripped = line.lstrip(" ")
            cur_buf.append(stripped)
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


def pick_anchor(body_for_match, body_raw):
    text = re.sub(r"^#.*$", "", body_raw, flags=re.M)
    text = re.sub(r"^\*+\s*\*+$", "", text, flags=re.M)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return ""
    # Strategy A: walk backwards, try each sentence (already-joined-into-paragraph)
    for para in reversed(paragraphs[-10:]):
        para_clean = re.sub(r"\*\*", "", para).strip()
        sents = re.split(r"(?<=[。！？!?])", para_clean)
        sents = [s.strip() for s in sents if s.strip()]
        for sent in reversed(sents):
            sent_clean = sent.rstrip("。！？!?\n\"\'「」")
            for length in [30, 25, 20, 15, 12, 10, 8]:
                if len(sent_clean) >= length:
                    candidate = sent_clean[:length]
                    if candidate in body_for_match:
                        return candidate
    # Strategy B: merge last lines across paragraphs
    fragments = []
    for para in reversed(paragraphs[-8:]):
        para_clean = re.sub(r"\*\*", "", para).strip()
        if para_clean:
            fragments.insert(0, para_clean.rstrip("。！？!?\n\"\'「」"))
        merged = "".join(fragments)
        for length in [30, 25, 20, 15, 12, 10, 8]:
            if len(merged) >= length:
                candidate = merged[-length:]  # take from end
                if candidate in body_for_match:
                    return candidate
    return ""


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
        anchor = pick_anchor(body_for_match, body)
        if not anchor:
            failed.append((p.name, "no_anchor"))
            continue
        if len(anchor) > 30:
            anchor = anchor[-30:]
        new_text = re.sub(
            r"(hook:\s*\|\s*\n)((?:[ \t]+.*\n?)+)",
            lambda m: m.group(1) + "  " + anchor + "\n",
            text,
            count=1,
        )
        if new_text == text:
            new_text = re.sub(
                r"^(hook:\s*)([^\n|].*?)$",
                lambda m: m.group(1) + "|\n  " + anchor + "\n",
                text,
                count=1,
                flags=re.M,
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
    print("P3 v7:", len(fixed), "fixed,", len(failed), "failed")


if __name__ == "__main__":
    main()
