# -*- coding: utf-8 -*-
"""Fix load_stub_set() to accept both old dict-list and new string-list formats."""
import re

path = 'engine/prose_lint.py'
src = open(path, encoding='utf-8').read()

new_func = '''def load_stub_set():
    """Read _STUB_MANIFEST.json, return stub filename set.

    Compatible with two files format:
      - files: [{"filename": "..."}, ...]   (legacy dict list)
      - files: ["...", ...]                  (new string list, post P0)
    """
    if not os.path.isfile(STUB_MANIFEST):
        return set()
    try:
        with open(STUB_MANIFEST, encoding="utf-8") as fh:
            data = json.load(fh)
        out = set()
        for entry in data.get("files", []):
            if isinstance(entry, dict):
                fn = entry.get("filename", "")
                if fn:
                    out.add(fn)
            elif isinstance(entry, str):
                if entry:
                    out.add(entry)
        return {x for x in out if x}
    except Exception:
        return set()'''

pattern = re.compile(
    r'def load_stub_set\(\):.*?return set\(\)',
    re.DOTALL,
)
new_src, n = pattern.subn(new_func, src)
if n == 0:
    print('PATTERN NOT MATCHED')
else:
    open(path, 'w', encoding='utf-8').write(new_src)
    print('replaced', n, 'occurrence(s)')
