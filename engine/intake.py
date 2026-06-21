"""Form / issue submission -> cast/<name>/soul.md. Used by the intake workflow.

  python engine/intake.py submission.json
Produces a soul.md, validates it, exits non-zero if the submission is unusable.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
import yaml
import soul as SOUL


def slug(name):
    # 文件夹 = 角色名（中英文都行，只去掉文件系统非法字符），和引擎写 state 的命名一致
    safe = re.sub(r'[\\/:*?"<>|]+', "", name).strip()
    return safe or ("soul-" + str(abs(hash(name)) % 10000))


def build(data):
    drives = data.get("drives", "")
    drives = [d.strip() for d in re.split(r"[，,、]", drives) if d.strip()] if isinstance(drives, str) else drives
    meta = {
        "name": (data.get("name") or "").strip(),
        "pronoun": (data.get("pronoun") or "他").strip(),
        "one_line": (data.get("one_line") or "").strip(),
        "drives": drives,
        "fracture": {"says": (data.get("says") or "").strip(),
                     "does": (data.get("does") or "").strip()},
        "under_pressure": (data.get("under_pressure") or "").strip(),
        "voice": (data.get("voice") or "").strip(),
        "boundaries": (data.get("boundaries") or "可暧昧可心碎；不写露骨、不写自我伤害").strip(),
    }
    sr = data.get("seed_relations")
    if sr:
        meta["seed_relations"] = sr
    return meta


def to_md(meta, backstory=""):
    fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{fm}\n---\n{backstory.strip()}\n"


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    meta = build(data)
    errs = SOUL.validate(meta)
    if errs:
        print("✗ 这份投稿还进不了村：\n   " + "\n   ".join(errs))
        sys.exit(1)
    name = meta["name"]
    d = os.path.join("souls", slug(name))
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "soul.md")
    open(path, "w", encoding="utf-8").write(to_md(meta, data.get("backstory", "")))
    print(f"✓ 写好灵魂：{path}\n   {name}：{meta['one_line']}")
    print(f"   下一回续写就会优先让 ta 登场。")


if __name__ == "__main__":
    main()
