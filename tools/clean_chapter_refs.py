"""Remove inline chNNN references from chapter prose.

Frontmatter is preserved. Only body text is edited.
Default mode reports replacements; --apply writes files.
"""
from pathlib import Path
import argparse, json, re

ROOT = Path(__file__).resolve().parent.parent
CHRONICLE = ROOT / "seasons" / "01-xianxia" / "chronicle"
REPORT = ROOT / "reports" / "jinjiang-r20" / "chapter-ref-clean.json"
REF_RE = re.compile(r"(?<![A-Za-z0-9_])ch(\d{3,4})(?![A-Za-z0-9_])")
DIGITS = "零一二三四五六七八九"

def chinese_number(n: int) -> str:
    if n < 10:
        return DIGITS[n]
    if n < 20:
        return "十" if n == 10 else "十" + DIGITS[n - 10]
    if n < 100:
        return DIGITS[n // 10] + "十" + (DIGITS[n % 10] if n % 10 else "")
    if n < 1000:
        return DIGITS[n // 100] + "百" + (("零" + chinese_number(n % 100)) if n % 100 and n % 100 < 10 else (chinese_number(n % 100) if n % 100 else ""))
    if n < 10000:
        tail = n % 1000
        if tail == 0:
            return DIGITS[n // 1000] + "千"
        if tail < 100:
            return DIGITS[n // 1000] + "千零" + chinese_number(tail)
        return DIGITS[n // 1000] + "千" + chinese_number(tail)
    return str(n)

def split_body(text: str):
    if text.startswith("---"):
        close = re.search(r"\n---\s*(?:\n|$)", text[3:])
        if close:
            end = 3 + close.end()
            return text[:end], text[end:]
    return "", text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    rows=[]
    total=0
    for path in sorted(CHRONICLE.glob("*.md")):
        if path.name in {"INDEX.md", "test_write.md"} or path.name.startswith("_"):
            continue
        text=path.read_text(encoding="utf-8")
        prefix, body=split_body(text)
        matches=list(REF_RE.finditer(body))
        if not matches:
            continue
        replacements=[]
        def repl(m):
            number=int(m.group(1))
            replacements.append({"from":m.group(0),"to":"第"+chinese_number(number)+"回"})
            return "第"+chinese_number(number)+"回"
        new_body=REF_RE.sub(repl, body)
        total += len(matches)
        if args.apply:
            path.write_text(prefix+new_body, encoding="utf-8")
        rows.append({"file":path.name,"matches":len(matches),"replacements":replacements})
    REPORT.write_text(json.dumps({"apply":args.apply,"files":len(rows),"replacements":total,"rows":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    print("mode:", "APPLY" if args.apply else "DRY-RUN")
    print("files:", len(rows))
    print("replacements:", total)
    print("report:", REPORT)

if __name__ == "__main__":
    main()
