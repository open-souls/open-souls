# -*- coding: utf-8 -*-
"""把插章拍平进主线，全书重排为连续 1..N。

阅读顺序 = 主线按 chapter 升序，每个插章插在其 insert_after 锚点之后；
同锚点多插章按 I-NNN 升序。然后整体重编号。

动作：改 frontmatter chapter、删 insert_after、改正文 # 标题、把文件重命名/移进 chronicle/、
重建 INDEX.md（保留原日期）。dry-run 只打印不落地。
"""
import os, re, glob, sys, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASON = os.path.join(ROOT, "seasons", "01-xianxia")
CHRON = os.path.join(SEASON, "chronicle")
INTER = os.path.join(SEASON, "interludes")
DRY = "--apply" not in sys.argv

_D = "零一二三四五六七八九"
def cn(n):
    if n < 10: return _D[n]
    if n < 20: return "十" + (_D[n % 10] if n % 10 else "")
    if n < 100:
        t, o = divmod(n, 10); return _D[t] + "十" + (_D[o] if o else "")
    h, r = divmod(n, 100); s = _D[h] + "百"
    if r == 0: return s
    if r < 10: return s + "零" + _D[r]
    if r < 20: return s + "一十" + (_D[r % 10] if r % 10 else "")
    t, o = divmod(r, 10); return s + _D[t] + "十" + (_D[o] if o else "")

def fm_block(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2), m) if m else (None, None, None)

def safe(t):
    return re.sub(r'[\\/:*?"<>|]', "", t).strip()

def load_dates():
    dates = {}
    idx = os.path.join(CHRON, "INDEX.md")
    if os.path.exists(idx):
        for line in open(idx, encoding="utf-8"):
            m = re.search(r"第\s*(\d+)\s*回.*?（(\d{4}-\d{2}-\d{2})）", line)
            if m: dates[int(m.group(1))] = m.group(2)
    return dates

def collect():
    items = []  # dict: path, dir, cur(int main)/None, anchor, code, fm, body, raw
    for d, src in (("chron", CHRON), ("inter", INTER)):
        for p in glob.glob(os.path.join(src, "*.md")):
            if os.path.basename(p) == "INDEX.md": continue
            raw = open(p, encoding="utf-8").read()
            fmtext, body, _ = fm_block(raw)
            if fmtext is None: continue
            fm = yaml.safe_load(fmtext) or {}
            if not fm.get("cast"): continue
            ch = fm.get("chapter")
            it = {"path": p, "raw": raw, "fmtext": fmtext, "body": body,
                  "title": str(fm.get("title", "")).strip(), "cast": fm.get("cast") or []}
            if isinstance(ch, str) and ch.startswith("I-"):
                it["cur"] = None
                it["code"] = int(re.match(r"I-(\d+)", ch).group(1))
                ia = str(fm.get("insert_after", "") or "")
                m = re.search(r"(\d+)", ia)
                it["anchor"] = int(m.group(1)) if m else 10**9
            else:
                it["cur"] = int(ch); it["code"] = -1; it["anchor"] = None
            items.append(it)
    return items

def order(items):
    mains = sorted([i for i in items if i["cur"] is not None], key=lambda x: x["cur"])
    inter_by = {}
    for i in items:
        if i["cur"] is None:
            inter_by.setdefault(i["anchor"], []).append(i)
    for k in inter_by: inter_by[k].sort(key=lambda x: x["code"])
    seq = []
    for m in mains:
        seq.append(m)
        seq.extend(inter_by.get(m["cur"], []))
    # 锚点不存在的插章（理论上没有）兜底接尾
    placed = {id(x) for x in seq}
    for i in items:
        if id(i) not in placed: seq.append(i)
    return seq

def rewrite(seq, dates):
    used = set()
    lines_idx = []
    for newn, it in enumerate(seq, 1):
        # frontmatter: 改 chapter，删 insert_after
        fmt = re.sub(r"(?m)^chapter:.*$", "chapter: %d" % newn, it["fmtext"])
        fmt = re.sub(r"(?m)^insert_after:.*\n?", "", fmt)
        # body: 改首个 # 标题
        body = re.sub(r"(?m)^#\s*(?:第[一-鿿]+回|插章[一-鿿]+)\s*·\s*(.*)$",
                      "# 第%s回 · \\1" % cn(newn), it["body"], count=1)
        newtext = "---\n%s\n---\n\n%s" % (fmt.strip("\n"), body.lstrip("\n"))
        fn = "%03d-%s.md" % (newn, safe(it["title"]) or "无题")
        dst = os.path.join(CHRON, fn)
        while dst in used:  # 同名兜底
            fn = "%03d-%s_.md" % (newn, safe(it["title"])); dst = os.path.join(CHRON, fn)
        used.add(dst)
        date = dates.get(it["cur"], "") if it["cur"] is not None else ""
        lines_idx.append("- 第%d回《%s》— %s%s" %
                         (newn, it["title"], " / ".join(it["cast"]),
                          ("（%s）" % date) if date else ""))
        if DRY:
            tag = "主" if it["cur"] is not None else "插I-%03d@ch%s" % (it["code"], it["anchor"])
            if newn <= 12 or newn % 80 == 0:
                print("  %3d <- %-22s [%s]" % (newn, os.path.basename(it["path"]), tag))
            continue
        with open(it["path"], "w", encoding="utf-8") as f:
            f.write(newtext)
        if os.path.abspath(it["path"]) != os.path.abspath(dst):
            os.replace(it["path"], dst)
    if not DRY:
        with open(os.path.join(CHRON, "INDEX.md"), "w", encoding="utf-8") as f:
            f.write("# 连载目录\n\n" + "\n".join(lines_idx) + "\n")

def main():
    items = collect()
    seq = order(items)
    dates = load_dates()
    print("总章数: %d (主线 %d + 插章 %d)" %
          (len(seq), sum(1 for i in items if i["cur"] is not None),
           sum(1 for i in items if i["cur"] is None)))
    print("模式:", "DRY-RUN (加 --apply 落地)" if DRY else "APPLY")
    rewrite(seq, dates)
    print("完成。" if not DRY else "(dry-run, 未写文件)")

if __name__ == "__main__":
    main()
