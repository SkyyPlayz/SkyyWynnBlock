#!/usr/bin/env python3
"""Check art/tooltip-frames/ (SkyyGear rarity tooltip backgrounds, arrows, slot frames). One line per check, ALL OK / N FAILED (exit 1).

Checks: every texture exists at the vanilla size (tooltip 107 / 54, arrow 66x48 / 33x24, slot 148 / 74); the 9-slice stretch strip
is uniform (@2x columns + rows 48..58, 1x 24..29) so the client's Border: 24 stretch never smears corner art; alpha is hard (255)
on the frame and only soft (<= 110) in the shadow / glow (slots: 0 or 255 only); the text area is dark enough (contrast >= 4.5 for
white, grey, green, red, gold, aqua and the rarity colour); no two rarities share a texture; manifest bytes + sha256 match; the
generator is deterministic (a fresh in-memory run gives the same bytes); none of our paths exists in vanilla Assets.zip.
"""
import hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_tooltip_frames as M

ASSETS = r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip"
fails = []


def check(ok, msg):
    print(("OK    " if ok else "FAIL  ") + msg)
    if not ok: fails.append(msg)


def rl(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(a, b):
    la, lb = rl(a), rl(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def strip_ok(img, lo, hi):
    w, h = P.size(img)
    for y in range(h):
        if any(img[y][x] != img[y][lo] for x in range(lo, hi + 1)): return False
    for x in range(w):
        if any(img[y][x] != img[lo][x] for y in range(lo, hi + 1)): return False
    return True


def main():
    man = json.load(open(os.path.join(M.OUT, "manifest.json"), encoding="utf-8"))
    mf = {f["path"]: f for f in man["files"]}
    sizes = {"tip2": (107, 107), "tip1": (54, 54), "arr2": (66, 48), "arr1": (33, 24), "slot2": (148, 148), "slot1": (74, 74)}
    texts = [(255, 255, 255), (170, 170, 170), (85, 255, 85), (255, 85, 85), (255, 170, 0), (85, 255, 255)]
    seen = {}
    for rid, name, hexs in M.RARITIES:
        rp = M.rel_paths(name)
        for k, rel in rp.items():
            p = os.path.join(M.OUT, rel)
            if not os.path.exists(p):
                check(False, rel + " exists"); continue
            data = open(p, "rb").read(); img = P.read_png(data)
            check(P.size(img) == sizes[k], "%s is %dx%d" % (rel, sizes[k][0], sizes[k][1]))
            check(rel in mf and mf[rel]["bytes"] == len(data) and mf[rel]["sha256"] == hashlib.sha256(data).hexdigest(),
                  rel + " matches the manifest")
            al = {px[3] for row in img for px in row}
            if k.startswith("slot"):
                check(al <= {0, 255}, rel + " hard alpha (0 / 255)")
            else:
                check(all(a == 255 or a <= 110 for a in al), rel + " frame alpha hard, shadow / glow soft (<= 110)")
            if k == "tip2": check(strip_ok(img, 48, 58), rel + " 9-slice strip 48..58 uniform")
            if k == "tip1": check(strip_ok(img, 24, 29), rel + " 9-slice strip 24..29 uniform")
            if k == "tip2":
                c = img[53][53][:3]
                worst = min(contrast(c, t) for t in texts + [M.hx(hexs)])
                check(worst >= 4.5, "%s text area %s contrast >= 4.5 (worst %.1f)" % (name, c, worst))
            h = hashlib.sha256(data).hexdigest()
            check(h not in seen, rel + " differs from every other texture" + (" (same as %s)" % seen.get(h) if h in seen else ""))
            seen[h] = rel
    check(os.path.exists(os.path.join(M.OUT, "sheet.png")), "sheet.png exists")
    fresh = M.build_all()
    same = all(open(os.path.join(M.OUT, rel), "rb").read() == v[1] for rel, v in fresh.items())
    check(same, "generator deterministic (fresh run = files on disk)")
    if os.path.exists(ASSETS):
        names = set(zipfile.ZipFile(ASSETS).namelist())
        check(not any(rel in names for rel in fresh), "no path collides with vanilla Assets.zip")
    print("ALL OK" if not fails else "%d FAILED" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
