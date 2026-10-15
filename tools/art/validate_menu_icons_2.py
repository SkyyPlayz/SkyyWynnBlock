#!/usr/bin/env python3
"""Check art/menu-icons-2/ (SkyWynn Menu icons sheet 2: Teleport page, shared buttons, Accept / Deny, Shards tile).
Prints one line per check and ALL OK / N FAILED (exit 1 on a failure).

Checks (same as tools/art/validate_menu_icons.py): every icon exists; 64 x 64 RGBA PNG; hard alpha (0 / 255); no #000000 / #ffffff;
a 1 px dark outline (every solid pixel touching transparency is dark); the art fills the slot (>= 40 px on its long side) with a 1 px
margin; no two icons identical (also none identical to a sheet-1 icon); no id clashes with sheet 1; manifest bytes + sha256 match the
files; the generator is deterministic (a fresh in-memory run gives the same bytes, icons and sheet).
Game files are NOT read. The optional vanilla path-clash check runs only with --assets <path to a COPY of Assets.zip>.
"""
import hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M1
import make_menu_icons_2 as M

fails = []


def check(ok, msg):
    print(("OK    " if ok else "FAIL  ") + msg)
    if not ok: fails.append(msg)


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def main(argv):
    man = json.load(open(os.path.join(M.OUT, "manifest.json"), encoding="utf-8"))
    files = {f["path"]: f for f in man["files"]}
    check(len(man["icons"]) == len(M.ICONS) == 14, "14 icons in the manifest and the generator")
    sheet1 = set(t[0] for t in M1.TILES)
    clash = [t[0] for t in M.ICONS if t[0] in sheet1]
    check(not clash, "no icon name clashes with sheet 1 %s" % (clash or ""))
    s1_hashes = set()
    for t in M1.TILES:
        p = os.path.join(M1.OUT, M1.icon_rel(t[0]))
        if os.path.exists(p): s1_hashes.add(hashlib.sha256(open(p, "rb").read()).hexdigest())
    fresh = M.build_icons()
    seen = {}
    ment = {e["name"]: e for e in man["icons"]}
    for t in M.ICONS:
        name = t[0]
        rel = M.icon_rel(name); path = os.path.join(M.OUT, rel)
        if not os.path.exists(path):
            check(False, "%s exists" % rel); continue
        data = open(path, "rb").read()
        w, h = P.png_size(data)
        check((w, h) == (64, 64) and data[25] == 6, "%s: 64 x 64 RGBA" % name)
        img = P.read_png(data)
        alphas = set(p[3] for r in img for p in r)
        check(alphas <= {0, 255}, "%s: hard alpha" % name)
        solid = [(x, y) for y in range(64) for x in range(64) if img[y][x][3]]
        check(not any(tuple(img[y][x][:3]) in ((0, 0, 0), (255, 255, 255)) for x, y in solid), "%s: no pure black / white" % name)
        xs = [x for x, y in solid]; ys = [y for x, y in solid]
        check(max(max(xs) - min(xs), max(ys) - min(ys)) + 1 >= 40, "%s: fills %d x %d px of the slot" % (name, max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
        edge = [(x, y) for x, y in solid if any(not (0 <= x + dx < 64 and 0 <= y + dy < 64) or img[y + dy][x + dx][3] == 0
                                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        check(all(lum(img[y][x]) < 48 for x, y in edge), "%s: 1 px dark outline (%d edge px)" % (name, len(edge)))
        check(min(xs) >= 1 and min(ys) >= 1 and max(xs) <= 62 and max(ys) <= 62, "%s: 1 px margin" % name)
        h_ = hashlib.sha256(data).hexdigest()
        check(h_ not in seen and h_ not in s1_hashes, "%s: unique (not identical to %s)" % (name, seen.get(h_) or ("a sheet-1 icon" if h_ in s1_hashes else None)))
        seen[h_] = name
        f = files.get(rel); e = ment.get(name)
        check(bool(f) and f["bytes"] == len(data) and f["sha256"] == h_ and bool(e) and e["sha256"] == h_ and e["bytes"] == len(data)
              and e["id"] == "Skyy_Menu_Icon_" + name and e["replaces_vanilla_id"] == t[5], "%s: manifest id / bytes / sha256 / replaces" % name)
        check(fresh[name][1] == data, "%s: deterministic (fresh run = same bytes)" % name)
    sheet = open(os.path.join(M.OUT, "sheet.png"), "rb").read()
    f = files.get("sheet.png")
    check(bool(f) and f["bytes"] == len(sheet) and f["sha256"] == hashlib.sha256(sheet).hexdigest(), "sheet.png: manifest bytes + sha256")
    check(M.build_sheet(fresh) == sheet, "sheet.png: deterministic")
    if "--assets" in argv:
        z = argv[argv.index("--assets") + 1]
        names = set(zipfile.ZipFile(z).namelist())
        clash = [M.icon_rel(t[0]) for t in M.ICONS if M.icon_rel(t[0]) in names]
        check(not clash, "no icon path exists in vanilla Assets.zip %s" % (clash or ""))
    else:
        print("SKIP  vanilla path clash check (pass --assets <copy of Assets.zip> to run it)")
    print("ALL OK" if not fails else "%d FAILED" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
