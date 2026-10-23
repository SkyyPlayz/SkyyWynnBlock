#!/usr/bin/env python3
"""SkyWynn radial page emblems (Radial-Trees-Spec R4) - CONCEPT v1, cloud art 2026-10-22.

Run:  python research/cloud/page-emblems-art/make_emblems.py      (--check = rebuild in memory, compare with manifest.json)
Writes next to this script:
  emblems/<Page>@2x.png   192 x 192 (the map-centre emblem box is 96 px: skyymap emb=96, SkyyTrees 0.5.0)
  emblems/<Page>.png       96 x 96  (2 x 2 box filter of the @2x)
  sheet.png               the review sheet (each emblem at 2x, 1x, on a map-centre mock with its hubs; the approved Nexus for reference)
  manifest.json           every file: path, size, bytes, sha256
Pages: Gathering (pickaxe + hatchet + hoe + fishing rod), Crafting (anvil + cooking pot + alchemy flask), Adventure (sword + boot +
map + paw for Beastmastery), Class (the 8 APPROVED class crests as a ring, art/class-emblems/*_128.png read-only).
Same family as the SkyWynn crest placeholder (tools/skyymap.py emblem_picture: navy disc + gold rings) with a heavier bevelled gold rim
and studs - the look Skyy liked on the Hylterium skill-tree centre (described in research/UI-Ideas.md 2026-10-22, never copied).
Pure Python: the painter + item glyphs live in research/cloud/ui-tiles-art/ (skyypaint.py, skyyitems.py). Deterministic.
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "ui-tiles-art"))
import skyypaint as P      # noqa: E402
import skyyitems as I      # noqa: E402

E = 192                     # @2x emblem (96 px box at 100 %)
C = E / 2.0
NAVY = P.hx("#14284a")      # skyymap ART emblemFill
GOLD = P.hx("#E8A93B")      # skyymap ART gold
INK = I.INK
CLASS_DIR = os.path.join(ROOT, "art", "class-emblems", "Common", "Icons", "ClassEmblems")
CLASSES = ["Warrior", "Berserker", "Archer", "Assassin", "Mage", "Priest", "Monk", "Spellblade"]
NEXUS = os.path.join(ROOT, "research", "cloud", "icons-1013", "icons", "Skyy_Nexus_Of_The_Void.png")

# page -> (tree hubs on that page in clockwise order with their sector angle, for the sheet mock only)
PAGES = [("Gathering", [("Mining", 45, "#9aa3ad"), ("Foraging", 135, "#6cbf48"), ("Farming", 225, "#e7bf4f"), ("Fishing", 315, "#4aa3c8")]),
         ("Crafting", [("Smithing", 0, "#d4824a"), ("Cooking", 120, "#e05a3a"), ("Alchemy", 240, "#b06ae0")]),
         ("Adventure", [("Combat", 45, "#d9443f"), ("Acrobatics", 135, "#6fd0d8"), ("Exploration", 225, "#e8c25a"),
                        ("Beastmastery", 315, "#a07850")]),
         ("Class", [("Branch 1", 0, "#E8A93B"), ("Branch 2", 120, "#f0cc80"), ("Branch 3", 240, "#a27628")])]


def base(cv, glow_col=(255, 214, 120)):
    """navy disc + inner glow, a bevelled gold rim with a dark line both sides, an inner thin ring, 8 studs"""
    lo, hi = P.hx("#0c1a33"), P.hx("#22447a")

    def fill(x, y):
        d = math.hypot(x - C, y - C - 8) / 80.0
        return P.mix(hi, lo, max(0.0, min(1.0, d)))
    cv.poly(P.circ_pts(C, C, 88, 88, 96), fill)
    cv.glow(C, C - 6, 70, glow_col, 0.22)
    for i in range(14):                                                     # faint stars in the field
        a, r = 2 * math.pi * P.hsh(301, i), 30 + 40 * P.hsh(302, i)
        cv.circle(C + r * math.cos(a), C + r * math.sin(a), 0.9 + 0.8 * P.hsh(303, i), (210, 225, 255), 0.55)
    dark, light = P.hx("#9a6a1c"), P.hx("#ffe39a")

    def rim(x, y):
        t = ((x - C) * -0.6 + (y - C) * -0.8) / 90.0
        return P.mix(dark, light, max(0.0, min(1.0, 0.5 + 0.6 * t)))
    cv.ring(C, C, 76, 92, rim)
    cv.ring(C, C, 80, 81.5, P.hx("#b07a24"), 0.8)                           # a groove in the rim
    cv.stroke(P.circ_pts(C, C, 92, 92, 96), 2.2, INK, 0.9)
    cv.stroke(P.circ_pts(C, C, 76, 76, 96), 2.0, INK, 0.9)
    cv.ring(C, C, 69, 71.5, GOLD, 0.75)
    for k in range(8):
        a = k * math.pi / 4.0 - math.pi / 2.0
        x, y = C + 86 * math.cos(a), C + 86 * math.sin(a)
        r = 5.0 if k % 2 == 0 else 3.6
        cv.circle(x, y, r, P.hx("#fff1c2") if k % 2 == 0 else P.hx("#f4c968"))
        cv.stroke(P.circ_pts(x, y, r, r, 16), 1.4, INK, 0.85)
        cv.circle(x - r * 0.3, y - r * 0.3, r * 0.35, (255, 255, 255), 0.8)


def gathering(cv):
    base(cv)
    # a fan: the four handles meet low in the middle, the heads spread out (the big heads behind, hoe + rod in front)
    px, py, size = C, C + 46, 76
    k = size / 32.0
    for fn, ang in ((I.pickaxe, -0.66), (I.hatchet, 0.66), (I.hoe, -0.2), (I.rod, 0.2)):
        if fn is I.hoe:                                                      # the hoe blade points out (left), not into the middle
            fn(cv, px + 15 * k * math.sin(ang), py - 15 * k * math.cos(ang), size, ang, flip=True)
        else:
            fn(cv, px + 15 * k * math.sin(ang), py - 15 * k * math.cos(ang), size, ang)
    cv.circle(px, py + 4, 7, P.hx("#c8925a"))                                # a leather tie where the handles meet
    cv.stroke(P.circ_pts(px, py + 4, 7, 7, 16), 1.4, INK, 0.85)
    cv.sparkle(C + 2, C - 50, 4)


def crafting(cv):
    base(cv, (255, 170, 90))
    cv.glow(C, C + 8, 60, P.hx("#ff9a3a"), 0.4)
    I.pot(cv, C - 30, C - 22, 58)
    I.flask(cv, C + 34, C - 24, 54)
    I.anvil(cv, C, C + 30, 100)
    cv.sparkle(C - 6, C + 8, 4, P.hx("#ffe6a0"))
    cv.sparkle(C + 14, C + 2, 3, P.hx("#ffe6a0"))


def adventure(cv):
    base(cv)
    I.treasure_map(cv, C - 26, C - 24, 60, -0.18)
    I.paw(cv, C + 32, C + 30, 46, 0.2)
    I.boot(cv, C - 30, C + 30, 56, 0.0)
    I.sword(cv, C + 4, C - 2, 122, 0.62)
    cv.sparkle(C + 44, C - 40, 4)


def class_ring(cv, crests):
    base(cv)
    cv.glow(C, C, 30, P.hx("#ffe9a8"), 0.7)
    cv.poly(P.star_pts(C, C, 22, 0.38, 4), P.hx("#ffd36b"))
    cv.stroke(P.star_pts(C, C, 22, 0.38, 4), 1.6, INK, 0.85)
    cv.poly(P.star_pts(C, C, 12, 0.38, 4, math.pi / 4), (255, 255, 255), 0.85)
    for k, name in enumerate(CLASSES):
        a = -math.pi / 2.0 + k * math.pi / 4.0
        x, y = C + 47 * math.cos(a), C + 47 * math.sin(a)
        sm = crests[name]
        cv.paste(sm, int(round(x - sm.w / 2.0)), int(round(y - sm.h / 2.0)))


def nexus_ref():
    """the APPROVED Nexus as SkyyRebirth 0.5.0 ships it (rm_black_hole): 140 px box @2x = 280, the 128 art doubled nearest (reference)"""
    art = P.load_png(NEXUS)
    cv = P.Canvas(280, 280)
    c = 140.0
    vc = P.hx("#9a5cff")
    cv.circle(c, c, 138, P.hx("#0b0818"), 0.96)
    cv.ring(c, c, 128, 136, vc, 0.9)
    cv.ring(c, c, 116, 119, vc, 0.4)
    o = int(c) - art.w
    for y in range(art.h):
        for x in range(art.w):
            r, g, b, a = art.get(x, y)
            if a > 0:
                for dy in (0, 1):
                    for dx in (0, 1):
                        cv.blend(o + 2 * x + dx, o + 2 * y + dy, (r, g, b), a)
    return cv


def map_mock(emb1x, hubs):
    """a 1x crop of the map centre: dark map, dotted lines, hubs 44 px at 84 px from C (Radial-Trees-Spec 2.2), the emblem in the middle"""
    W = 300
    cv = P.Canvas(W, W, P.hx("#0b1724"))
    c = W / 2.0
    for name, ang, col in hubs:
        a = math.radians(ang - 90)
        hx_, hy_ = c + 84 * math.cos(a), c + 84 * math.sin(a)
        for i in range(30):
            t = 0.3 + i * 0.05
            cv.circle(c + 84 * t * math.cos(a), c + 84 * t * math.sin(a), 0.9, P.hx("#797b7c"), 0.7)
        cv.circle(hx_, hy_, 22, P.hx("#101822"))
        cv.ring(hx_, hy_, 18, 22, P.hx(col))
        for k in range(3):                                         # a few node discs beyond each hub
            b = a + (k - 1) * 0.35
            nx, ny = c + 130 * math.cos(b), c + 130 * math.sin(b)
            cv.circle(nx, ny, 12, P.hx("#101822"))
            cv.ring(nx, ny, 10, 12, P.hx("#4a535c"))
    cv.paste(emb1x, int(c - emb1x.w / 2.0), int(c - emb1x.h / 2.0))
    return cv


def render_all():
    crests = dict((n, P.resample(P.load_png(os.path.join(CLASS_DIR, n + "_128.png")), 46, 46)) for n in CLASSES)
    out = {}
    for name, fn in (("Gathering", gathering), ("Crafting", crafting), ("Adventure", adventure)):
        cv = P.Canvas(E, E)
        fn(cv)
        out[name] = cv
    cv = P.Canvas(E, E)
    class_ring(cv, crests)
    out["Class"] = cv
    return out


def build_sheet(big, small):
    pad = 28
    W, H = 1700, 1080
    cv = P.Canvas(W, H, P.hx("#0e1a2b"))
    cv.text(pad, 18, "SKYWYNN RADIAL PAGE EMBLEMS (RADIAL-TREES-SPEC R4) - CONCEPT V1, CLOUD 2026-10-22", P.hx("#ffd36b"), 3)
    cv.text(pad, 50, "MAP CENTRE BOX = 96 PX (SKYYMAP EMB=96). PNG = 192 X 192 (@2X) + 96 X 96. NAVY DISC + BEVELLED GOLD RIM, "
                     "SAME FAMILY AS THE SKYWYNN CREST.", P.hx("#c9d8e6"), 2)
    x = pad
    y = 92
    for name, hubs in PAGES:
        cv.text(x, y, name.upper(), P.hx("#8fb8e0"), 3)
        cv.paste(big[name], x, y + 32)
        cv.paste(small[name], x + E + 20, y + 32)
        cv.text(x + E + 20, y + 32 + 100, "1X", P.hx("#9fb3c8"), 2)
        cv.text(x, y + 32 + E + 8, name + "@2X.PNG / " + name + ".PNG", P.hx("#9fb3c8"), 1)
        mm = map_mock(small[name], hubs)
        cv.paste(mm, x + 30, y + 32 + E + 26)
        cv.text(x + 30, y + 32 + E + 26 + mm.h + 6, "ON THE MAP (1X, HUBS AT 84 PX)", P.hx("#9fb3c8"), 1)
        x += 400
    # notes + the Nexus reference
    y2 = 720
    notes = ["GATHERING - PICKAXE + HATCHET CROSSED OVER A COPPER HOE + A BAMBOO FISHING ROD (MINING / FORAGING / FARMING / FISHING)",
             "CRAFTING - THE ANVIL, A COOKING POT WITH STEW + STEAM, AN ALCHEMY FLASK (SMITHING / COOKING / ALCHEMY)",
             "ADVENTURE - A SWORD ACROSS A TREASURE MAP, A BOOT, A PAW PRINT (COMBAT / EXPLORATION / ACROBATICS / BEASTMASTERY)",
             "CLASS - THE 8 APPROVED CLASS CRESTS IN A RING ROUND A GOLD STAR (FOR THE LEFT RAIL + THE NO-CLASS STATE;",
             "        WITH A CLASS THE PAGE KEEPS SHOWING THAT CLASS'S OWN CREST, AS SKYYTREES 0.5.0 DOES)",
             "",
             "NEXUS (REBIRTH, RIGHT): APPROVED 2026-10-13 - KEPT AS IS. SKYYREBIRTH 0.5.0 SHOWS IT IN A 140 PX BOX: THE 128 PX ART",
             "DOUBLED NEAREST INTO THE 280 PX @2X PICTURE. CRISP, BUT HALF THE DETAIL OF A NATIVE @2X - A 256 PX REDRAW IS",
             "OPTIONAL (QUESTION 3 IN THE README). NO SIZE CHANGE NEEDED."]
    for k, line in enumerate(notes):
        cv.text(pad, y2 + k * 22, line, P.hx("#c9d8e6"), 2)
    nx = nexus_ref()
    cv.text(W - 330, y2 - 40, "NEXUS (APPROVED, REFERENCE)", P.hx("#8fb8e0"), 2)
    cv.paste(nx, W - 320, y2 - 14)
    return cv


def main():
    check = "--check" in sys.argv
    big = render_all()
    small = dict((n, P.downscale2(c)) for n, c in big.items())
    sheet = build_sheet(big, small)
    files = {}
    for n in big:
        files["emblems/%s@2x.png" % n] = P.png_bytes(big[n])
        files["emblems/%s.png" % n] = P.png_bytes(small[n])
    files["sheet.png"] = P.png_bytes(sheet)
    man = []
    for rel in sorted(files):
        d = files[rel]
        w, h = P.struct.unpack(">II", d[16:24])
        man.append({"path": rel, "w": w, "h": h, "bytes": len(d), "sha256": hashlib.sha256(d).hexdigest()})
    if check:
        old = json.load(open(os.path.join(HERE, "manifest.json")))
        same = [m["sha256"] for m in old["files"]] == [m["sha256"] for m in man]
        print("deterministic: %s" % ("SAME BYTES" if same else "DIFFERENT"))
        sys.exit(0 if same else 1)
    if not os.path.isdir(os.path.join(HERE, "emblems")):
        os.makedirs(os.path.join(HERE, "emblems"))
    for rel, d in files.items():
        with open(os.path.join(HERE, rel), "wb") as f:
            f.write(d)
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump({"what": "SkyWynn radial page emblems (concept v1)", "generator": "make_emblems.py", "files": man}, f, indent=1,
                  sort_keys=True)
        f.write("\n")
    for m in man:
        print("%-28s %4d x %-4d %7d bytes" % (m["path"], m["w"], m["h"], m["bytes"]))


if __name__ == "__main__":
    main()
