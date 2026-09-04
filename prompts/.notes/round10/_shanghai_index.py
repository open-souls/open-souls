import json, re, os
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
CHRON = "seasons/01-xianxia/chronicle"
results = []
for c in gs:
    fp = os.path.join(CHRON, c["file"])
    if not os.path.exists(fp): continue
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    body = text[m.end():] if m else text
    body_stripped = body.strip()
    cast_match = re.findall(r"^cast:\s*\[(.*?)\]", text, re.MULTILINE | re.DOTALL)
    cast_count = 0
    if cast_match:
        cast_count = len([x for x in cast_match[0].split(",") if x.strip()])
    dialogue_count = len(re.findall(r"[\u300c\u300d\u201c\u201d]", body))
    motif_count = len(re.findall(r"(刀|灯|袖|窗|桌|椅|门|帘|杯|茶|纸|墨|笔|砚|信|鞋|布|帕|镜|玉|火|光|影|瓷|碗|枕|榻|案|栏|墙|砖|风|雪|雨|树|叶|花|水|井|酒|弦|琴|伞|香|灰|屋)", body))
    sentences = re.split(r"[\u3002\uff1f\uff01]", body_stripped)
    sentences = [s.strip() for s in sentences if s.strip()]
    short_sentences = sum(1 for s in sentences if len(s) < 12)
    f_ratio = short_sentences / max(1, len(sentences))
    ends_question = body_stripped.rstrip().endswith("\u003f") or body_stripped.rstrip().endswith("\uff1f")
    ends_ellipsis = body_stripped.rstrip().endswith("\u2026")
    results.append({
        "file": c["file"],
        "total_27": c["total_27"],
        "cast_count": cast_count,
        "dialogue_count": dialogue_count,
        "motif_count": motif_count,
        "sentences": len(sentences),
        "f_ratio": round(f_ratio, 2),
        "ends_q": ends_question,
        "ends_ellipsis": ends_ellipsis,
    })

print("=== Top 30 by 物象 density ===")
for r in sorted(results, key=lambda x: -x["motif_count"])[:30]:
    print(f"  {r['file']:35s} total={r['total_27']} 物象={r['motif_count']:>3} 对话={r['dialogue_count']:>3} F比={r['f_ratio']}")

print("\n=== Top 30 by F-style 节奏 ===")
for r in sorted(results, key=lambda x: -x["f_ratio"])[:30]:
    print(f"  {r['file']:35s} total={r['total_27']} F比={r['f_ratio']:.2f} 句子={r['sentences']:>3} 短句={int(r['f_ratio']*r['sentences']):>3}")

# Distribution
print("\n=== Cast count distribution ===")
from collections import Counter
cc = Counter(r["cast_count"] for r in results)
for k in sorted(cc.keys()):
    print(f"  cast={k}: {cc[k]}")

# Stats
import statistics
print("\n=== Aggregate stats ===")
print(f"  avg 物象: {statistics.mean(r['motif_count'] for r in results):.1f}")
print(f"  avg 对话: {statistics.mean(r['dialogue_count'] for r in results):.1f}")
print(f"  avg F比: {statistics.mean(r['f_ratio'] for r in results):.2f}")
print(f"  ends ?: {sum(1 for r in results if r['ends_q'])}")
print(f"  ends …: {sum(1 for r in results if r['ends_ellipsis'])}")
