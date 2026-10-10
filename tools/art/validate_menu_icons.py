#!/usr/bin/env python3
"""Check art/menu-icons/ (SkyWynn Menu tile icons). Prints one line per check and ALL OK / N FAILED (exit 1 on a failure).

Checks: every tile icon exists; 64 x 64 RGBA PNG; hard alpha (0 / 255); no #000000 / #ffffff; a 1 px dark outline (every solid
pixel touching transparency is dark) on our generated icons; the art fills the slot (>= 40 px on its long side) and stays inside
it (1 px margin); no two icons identical; the Accessory Bag is a byte copy of art/accessory-bag-icon; manifest bytes + sha256 match
the files; the generator is deterministic (a fresh in-memory run gives the same bytes); none of our paths exists in vanilla
Assets.zip (read only, skipped if the zip is not there).
"""
import hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M

ASSETS = r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip"
fails = []


def check(ok, msg):
    print(("OK    " if ok else "FAIL  ") + msg)
    if not ok: fails.append(msg)


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def main():
    man = json.load(open(os.path.join(M.OUT, "manifest.json"), encoding="utf-8"))
    files = {f["path"]: f for f in man["files"]}
    check(len(man["tiles"]) == len(M.TILES) == 23, "23 tiles in the manifest and the generator")
    fresh = M.build_icons()
    seen = {}
    for name, label, cat, slot, fn, what in M.TILES:
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
        check(max(max(xs) - min(xs), max(ys) - min(ys)) + 1 >= 40 and min(xs) >= 0 and min(ys) >= 0 and max(xs) <= 63 and max(ys) <= 63,
              "%s: fills %d x %d px of the slot" % (name, max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
        if fn is not None:
            edge = [(x, y) for x, y in solid if any(not (0 <= x + dx < 64 and 0 <= y + dy < 64) or img[y + dy][x + dx][3] == 0
                                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
            check(all(lum(img[y][x]) < 48 for x, y in edge), "%s: 1 px dark outline (%d edge px)" % (name, len(edge)))
            check(min(xs) >= 1 and min(ys) >= 1 and max(xs) <= 62 and max(ys) <= 62, "%s: 1 px margin" % name)
        else:
            src = open(os.path.join(M.ROOT, M.BAG_SRC_REL), "rb").read()
            check(src == data, "%s: byte copy of %s" % (name, M.BAG_SRC_REL))
        h_ = hashlib.sha256(data).hexdigest()
        check(h_ not in seen, "%s: unique (not identical to %s)" % (name, seen.get(h_)))
        seen[h_] = name
        f = files.get(rel)
        check(bool(f) and f["bytes"] == len(data) and f["sha256"] == h_, "%s: manifest bytes + sha256" % name)
        check(fresh[name][1] == data, "%s: deterministic (fresh run = same bytes)" % name)
    sheet = open(os.path.join(M.OUT, "sheet.png"), "rb").read()
    f = files.get("sheet.png")
    check(bool(f) and f["bytes"] == len(sheet) and f["sha256"] == hashlib.sha256(sheet).hexdigest(), "sheet.png: manifest bytes + sha256")
    check(M.build_sheet(fresh) == sheet, "sheet.png: deterministic")
    if os.path.exists(ASSETS):
        names = set(zipfile.ZipFile(ASSETS).namelist())
        clash = [M.icon_rel(t[0]) for t in M.TILES if M.icon_rel(t[0]) in names]
        check(not clash, "no icon path exists in vanilla Assets.zip %s" % (clash or ""))
    else:
        print("SKIP  Assets.zip not found (vanilla path clash check)")
    print("ALL OK" if not fails else "%d FAILED" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
