#!/usr/bin/env python3
"""Check art/tooltip-sky/ (SkyyGear SKY WINDOW rarity tooltips, arrows, slot frames). One line per check, ALL OK / N FAILED (exit 1).

Checks: every texture exists at the vanilla size (tooltip 107 / 54, arrow 66x48 / 33x24, slot 148 / 74); the 9-slice stretch strip is
uniform (@2x columns + rows 48..58, 1x 24..29) so Border: 24 never smears corner art; the text panel is fully opaque (alpha 255 at
depth >= 20 px @2x along the whole edge strip and in the centre); soft alpha only outside the frame and never above the cap (110);
text contrast on the panel >= 4.5:1 for white, grey, green, red, gold, aqua and the rarity colour; the arrow's top rows are transparent
outside the V (it never paints over corner art) and the V is centred; the slot centre is a mid-tone (icons stay readable); no two
textures are identical; manifest bytes + sha256 + the exact quality-asset field values match; the generator is deterministic (a fresh
in-memory run gives the same bytes); none of our paths exists in vanilla Assets.zip (read only).
"""
import hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_tooltip_sky as M

ASSETS = r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip"
fails = []


def check(ok, msg):
    print(("OK    " if ok else "FAIL  ") + msg)
    if not ok: fails.append(msg)


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
    mr = {r["name"]: r for r in man["rarities"]}
    sizes = {"tip2": (107, 107), "tip1": (54, 54), "arr2": (66, 48), "arr1": (33, 24), "slot2": (148, 148), "slot1": (74, 74)}
    seen = {}
    for rid, name, hexs, _mood in M.RARITIES:
        rp = M.rel_paths(name)
        q = mr.get(name, {}).get("quality_asset_fields", {})
        check(q == M.quality_fields(name) and q.get("ItemTooltipTexture") == "UI/ItemQualities/SkyyGear/Tooltips/Tooltip_%s.png" % name
              and q.get("ItemTooltipArrowTexture") == "UI/ItemQualities/SkyyGear/Tooltips/Tooltip_%sArrow.png" % name
              and q.get("SlotTexture") == q.get("BlockSlotTexture") == q.get("SpecialSlotTexture") == "UI/ItemQualities/SkyyGear/Slots/Slot_%s.png" % name,
              "%s manifest quality-asset fields exact" % name)
        for k, rel in rp.items():
            p = os.path.join(M.OUT, rel)
            if not os.path.exists(p):
                check(False, rel + " exists"); continue
            data = open(p, "rb").read(); img = P.read_png(data)
            check(P.size(img) == sizes[k], "%s is %dx%d" % (rel, sizes[k][0], sizes[k][1]))
            check(rel in mf and mf[rel]["bytes"] == len(data) and mf[rel]["sha256"] == hashlib.sha256(data).hexdigest(),
                  rel + " matches the manifest")
            h = hashlib.sha256(data).hexdigest()
            check(h not in seen, rel + " differs from every other texture" + (" (same as %s)" % seen.get(h) if h in seen else ""))
            seen[h] = rel
            if k in ("tip2", "tip1"):
                lo, hi, f = (48, 58, 1) if k == "tip2" else (24, 29, 2)
                check(strip_ok(img, lo, hi), "%s 9-slice strip %d..%d uniform" % (rel, lo, hi))
                w = P.size(img)[0]
                dep = 20 // f                                   # panel starts at box depth ~13 + inset 6 (@2x)
                opaque = all(img[y][x][3] == 255 for y in range(dep, w - dep) for x in range(dep, w - dep)
                             if (lo <= x <= hi or lo <= y <= hi))
                check(opaque, rel + " text panel fully opaque (strips + centre)")
                soft = [px[3] for row in img for px in row if 0 < px[3] < 255]
                outer_ok = all(img[y][x][3] in (0, 255) or min(x, y, w - 1 - x, w - 1 - y) < 7 // f + 1
                               or (x < lo or x > hi) and (y < lo or y > hi) for y in range(w) for x in range(w))
                check(max(soft or [0]) <= 254 and outer_ok, rel + " soft alpha only outside the frame (edge halo / corner art)")
                halo = max([img[y][0][3] for y in range(w)] + [img[0][x][3] for x in range(w)])
                check(halo <= M.SOFT_MAX, "%s outermost halo alpha <= %d (got %d)" % (rel, M.SOFT_MAX, halo))
            if k == "tip2":
                c = tuple(img[53][53][:3])
                ratios = {n: M.contrast(c, t) for n, t in M.TEXT.items()}
                ratios["rarity"] = M.contrast(c, M.hx(hexs))
                worst = min(ratios, key=ratios.get)
                check(ratios[worst] >= 4.5, "%s text panel #%02x%02x%02x contrast >= 4.5 (worst %s %.2f)" % ((name,) + c + (worst, ratios[worst])))
                check(abs(mr[name]["contrast"]["min_required"] - round(ratios[worst], 2)) < 0.011, name + " manifest contrast table current")
            if k in ("arr2", "arr1"):
                f = 1 if k == "arr2" else 2
                w, hgt = P.size(img)
                mid = w / 2.0
                # rows overlaying the tooltip (top 26 @2x): pixels outside the V must be fully transparent
                bad = 0
                for y in range(int(26 / f)):
                    Y = (y + 0.5) * f; H = (M.ATIP - Y) * M.ASL
                    for x in range(w):
                        if abs((x + 0.5) * f - mid * f) > H + 1.5 and img[y][x][3] != 0: bad += 1
                check(bad == 0, rel + " transparent outside the V over the tooltip rim (%d stray px)" % bad)
                sym = all(abs(img[y][x][3] - img[y][w - 1 - x][3]) <= 2 for y in range(hgt) for x in range(w))
                check(sym, rel + " V symmetric (alpha)")
                check(img[hgt - 1][0][3] == 0 and img[hgt - 1][w - 1][3] == 0, rel + " bottom corners empty")
            if k in ("slot2", "slot1"):
                w = P.size(img)[0]; c0, c1 = int(w * 0.3), int(w * 0.7)
                lum = [M.rl(img[y][x][:3]) for y in range(c0, c1) for x in range(c0, c1)]
                avg = sum(lum) / len(lum)
                bg = tuple(int(round(sum(img[y][x][i] for y in range(c0, c1) for x in range(c0, c1)) / len(lum))) for i in range(3))
                cw = M.contrast(bg, (230, 232, 240)); cd = M.contrast(bg, (40, 40, 52))
                check(0.04 <= avg <= 0.25 and cw >= 3.0 and cd >= 1.5,
                      "%s centre mid-tone (lum %.3f; vs light icon %.1f, vs dark icon %.1f)" % (rel, avg, cw, cd))
                check(all(img[y][x][3] == 255 for y in range(8 // (2 if k == "slot1" else 1) + 2, w - 10) for x in range(10, w - 10)),
                      rel + " inside fully opaque")
    sp = os.path.join(M.OUT, "sheet.png")
    check(os.path.exists(sp) and man["sheet"]["sha256"] == hashlib.sha256(open(sp, "rb").read()).hexdigest(), "sheet.png exists + matches the manifest")
    check(os.path.exists(os.path.join(M.OUT, "README.md")), "README.md exists")
    fresh = M.build_all()
    same = all(open(os.path.join(M.OUT, rel), "rb").read() == v[1] for rel, v in fresh.items())
    check(same, "generator deterministic (fresh run = files on disk)")
    if os.path.exists(ASSETS):
        names = set(zipfile.ZipFile(ASSETS).namelist())
        check(not any(rel in names for rel in fresh), "no path collides with vanilla Assets.zip")
    else:
        print("SKIP  Assets.zip not found (collision check)")
    print("ALL OK" if not fails else "%d FAILED" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
