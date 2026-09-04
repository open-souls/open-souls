import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# True 30-分门槛: every dim >= 1.5
all20 = []
for c in gs:
    all20_dim = (all(x >= 1 for x in c["d7"]) 
                 and all(x >= 1 for x in c["rubric"]) 
                 and all(x >= 1 for x in c["pub"]))
    if all20_dim:
        all20.append(c)
print(f"every dim >=1: {len(all20)}/{len(gs)} ({100*len(all20)/len(gs):.1f}%)")
# every dim >= 1.5
all15 = [c for c in gs if all(x >= 1.5 for x in c["d7"]) and all(x >= 1.5 for x in c["rubric"]) and all(x >= 1.5 for x in c["pub"])]
print(f"every dim >=1.5 (true 30-分 门槛): {len(all15)}/{len(gs)} ({100*len(all15)/len(gs):.1f}%)")
# Every dim >= 1.2
all12 = [c for c in gs if all(x >= 1.2 for x in c["d7"]) and all(x >= 1.2 for x in c["rubric"]) and all(x >= 1.2 for x in c["pub"])]
print(f"every dim >=1.2: {len(all12)}/{len(gs)} ({100*len(all12)/len(gs):.1f}%)")
# Every dim >= 1.0
all10 = [c for c in gs if all(x >= 1 for x in c["d7"]) and all(x >= 1 for x in c["rubric"]) and all(x >= 1 for x in c["pub"])]
print(f"every dim >=1.0: {len(all10)}/{len(gs)} ({100*len(all10)/len(gs):.1f}%)")

# Per-dim failure count (what dims block the most chapters from being "all >= 1")
print()
print("Per-dim failure frequency (chapters where this dim < 1):")
for i, name in enumerate(["d7节奏","d7用词","d7潜台","d7感官","d7对话","d7视角","d7克制","钩子","爽痛","反差","拉扯","记忆","代入","新","画面","截图","独立","cast3-5","开场","收尾"]):
    if i < 7: arr = [c["d7"][i] for c in gs]
    elif i < 14: arr = [c["rubric"][i-7] for c in gs]
    else: arr = [c["pub"][i-14] for c in gs]
    under1 = sum(1 for x in arr if x < 1)
    under15 = sum(1 for x in arr if x < 1.5)
    print(f"  {name:<10} <1: {under1:>4}  <1.5: {under15:>4}  avg: {sum(arr)/len(arr):.2f}")
