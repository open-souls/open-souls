"""CI gate: validate every cast/<name>/soul.md. Exits non-zero on any bad soul."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
import soul as SOUL


def main():
    targets = sys.argv[1:] or glob.glob("souls/*/soul.md")
    names, bad = {}, False
    for p in targets:
        if os.sep + "_" in p:
            continue
        try:
            meta = SOUL.parse(p)
            errs = SOUL.validate(meta)
            if meta["name"] in names:
                errs.append(f"角色名「{meta['name']}」和 {names[meta['name']]} 重了")
            names[meta["name"]] = p
            if errs:
                bad = True
                print(f"✗ {p}\n   " + "\n   ".join(errs))
            else:
                print(f"✓ {p} — {meta['name']}：{meta['one_line']}")
        except Exception as e:
            bad = True
            print(f"✗ {p}\n   {e}")
    if bad:
        print("\n有灵魂没过。修好上面的，村子才收。")
        sys.exit(1)
    print("\n全部通过，欢迎进 Open Souls。")


if __name__ == "__main__":
    main()
