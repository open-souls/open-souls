# -*- coding: utf-8 -*-
"""Patch _build_corpus_map.py to handle 1-space-indented hook blocks."""
import re

path = 'prompts/.notes/_build_corpus_map.py'
src = open(path, encoding='utf-8').read()

old = '''def split_front_matter(text: str):
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    head = m.group(1)
    body = text[m.end():]
    out = {}
    cur_key = None
    cur_buf = []
    for line in head.splitlines():
        if line.startswith("  ") and cur_key:
            cur_buf.append(line[2:])
            continue
        if cur_key:
            out[cur_key] = "\\n".join(cur_buf).strip()
        m2 = RE_KV.match(line)
        if m2:
            cur_key, val = m2.group(1), m2.group(2)
            cur_buf = [val] if val else []
        else:
            cur_key = None
            cur_buf = []
    if cur_key:
        out[cur_key] = "\\n".join(cur_buf).strip()
    return out, body'''

new = '''def split_front_matter(text: str):
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    head = m.group(1)
    body = text[m.end():]
    out = {}
    cur_key = None
    cur_buf = []
    for line in head.splitlines():
        # Accept either 1+ or 2+ space indent for continuation
        if (line.startswith("  ") or line.startswith(" ")) and cur_key and line != cur_key + ":":
            # strip the leading whitespace (1 or 2 chars)
            stripped = line.lstrip(" ")
            cur_buf.append(stripped)
            continue
        if cur_key:
            out[cur_key] = "\\n".join(cur_buf).strip()
        m2 = RE_KV.match(line)
        if m2:
            cur_key, val = m2.group(1), m2.group(2)
            cur_buf = [val] if val else []
        else:
            cur_key = None
            cur_buf = []
    if cur_key:
        out[cur_key] = "\\n".join(cur_buf).strip()
    return out, body'''

if old in src:
    src = src.replace(old, new)
    open(path, 'w', encoding='utf-8').write(src)
    print('Patched')
else:
    print('NOT FOUND - need to find pattern')
