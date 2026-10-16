#!/usr/bin/env python3
"""make_class_emblems - the SkyWynn CLASS EMBLEMS (one shield crest per class, 64 x 64 + 128 x 128 + a grey 'locked' 64), our own art.

Why this file: Skyy 2026-10-16 (docs/answered/ui.md, CLASS ICONS ON PROFILES): "didn't we make class icons? why arnt they shown
here?" - we did: the cloud class emblems (research/cloud/class-art/, APPROVED by Skyy 2026-10-06, docs/answered/gear.md line 86:
"they look great!", v2 Monk wrapped fist + Priest soul cage v2 done 10-07, v2 detail for the other 5 on 10-08). They were never
brought into art/ or given the 8th class. This script:
  * ships the 7 approved crests exactly as approved (the PNGs in research/cloud/class-art/icons/), and re-renders them with the
    approved drawing code (research/cloud/class-art/make_emblems.py, imported read-only - not copied, not changed) as a check,
  * adds the SPELLBLADE crest (DRAFT, for Skyy's review) drawn with the same painter, crest and detail level: a two-handed
    greatsword with a glowing teal rune fuller in front of an arcane crescent sweep (the class's arc + Momentum), field = the
    Spellblade class colour #6fd0d8 (SkyyClasses / SkyyProfiles ClassDefs),
  * writes the game-ready set + a review sheet + manifest.json.

Original pixels drawn from code. No vanilla file, other mod or reference picture is read, copied or traced. Pillow only (the
approved painter is pure Python + Pillow). Deterministic: two runs = same pixels.

Run:  python tools/art/make_class_emblems.py [--out DIR]
Out:  <out>/Common/Icons/ClassEmblems/<Class>.png (64), <Class>_128.png, <Class>_Locked.png, <out>/sheet.png, <out>/manifest.json
      (default out = art/class-emblems)
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLOUD = os.path.join(ROOT, "research", "cloud", "class-art")
DEFAULT_OUT = os.path.join(ROOT, "art", "class-emblems")

_spec = importlib.util.spec_from_file_location("cloud_class_emblems", os.path.join(CLOUD, "make_emblems.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

# ---------------------------------------------------------------------------------------------------------- the classes
# (name, colour, role, weapons, status). Colours = ClassDefs.COLORS (the approved emblem colours) + Spellblade #6fd0d8.
CLASSES = [(n, c, r, w, "APPROVED") for (n, c, r, w) in E.CLASSES] + [
    ("Spellblade", "#6fd0d8", "Frontline sweeper + boss debuffer", "Two-handed swords, Great shield", "DRAFT"),
]

# ---------------------------------------------------------------------------------------------------------- Spellblade symbol
ARCL = E.ramp("#a882f0", 6, light=0.75)            # the arcane crescent sweep (breach violet - reads on the teal field)
RUNE = E.ramp("#5fe6f0", 5, light=0.8)             # glowing rune fuller + guard gem
TGRIP = E.ramp("#2c4a54", 5, light=0.9)            # dark teal leather grip (the Spellblade ability icons' TEALGRIP)
VIOL = E.ramp("#9a6ae6", 5, light=0.7)             # breach violet (pommel gem; Arcane Breach is violet in the ability icons)


def crescent(cv, cx, cy, r, thick, a_mid, span, k):
    """crescent sweep (grid units): circle r round (cx, cy) minus the same-size circle shifted `thick` toward the inside at angle
    a_mid (radians), kept within +/- span / 2 of a_mid - thickest in the middle, tapering to points"""
    ox, oy = cx - math.cos(a_mid) * thick, cy - math.sin(a_mid) * thick
    outer = E.ell(cv, cx * k, cy * k, r * k, r * k)
    inner = E.ell(cv, ox * k, oy * k, r * k, r * k)
    out = set()
    for (x, y) in outer - inner:
        a = math.atan2((y + 0.5) / k - cy, (x + 0.5) / k - cx)
        d = (a - a_mid + math.pi) % (2 * math.pi) - math.pi
        if abs(d) <= span / 2:
            out.add((x, y))
    return out


def greatsword(cv, cx, cy, ang, k):
    """the Spellblade's two-handed sword (local: tip at -y, guard at y = 0): broad bevelled blade with a honed edge and a glowing
    teal rune fuller, a long straight crossguard with flared ends and a teal gem, a LONG two-hand grip with a criss-cross wrap and
    a mid-grip ring, a violet pommel gem"""
    E.blade(cv, cx, cy, ang, k, [(0, -38), (5.2, -31), (5.0, -3.2), (6.4, -1.6), (-6.4, -1.6), (-5.0, -3.2), (-5.2, -31)])
    # glowing rune fuller: dashes of teal light down the centre
    for y0 in (-29.5, -23.5, -17.5, -11.5, -6.5):
        m = E.lp(cv, [(-0.9, y0), (0.9, y0), (0.9, y0 + 3.6), (-0.9, y0 + 3.6)], cx, cy, ang, k)
        E.shade(cv, m, RUNE, 'grad', outline=False, bevel=0.0, level=0.18)
    # straight crossguard with flared ends + centre block with the teal gem
    E.part(cv, [(-13, -2.6), (13, -2.6), (14.2, -0.4), (13, 2.2), (-13, 2.2), (-14.2, -0.4)], cx, cy, ang, k, E.DSTEEL, noise=0.03,
           seed=51)
    for s in (-1, 1):
        E.lknob(cv, 13.6 * s, -0.2, 2.0, cx, cy, ang, k, E.STEEL)
    E.part(cv, [(-3.6, -3.2), (3.6, -3.2), (4.0, 1.4), (0, 4.2), (-4.0, 1.4)], cx, cy, ang, k, E.STEEL, level=0.04)
    E.part(cv, [(0, -2.0), (2.0, 0.2), (0, 2.4), (-2.0, 0.2)], cx, cy, ang, k, RUNE, outline=k > 1)
    # long two-hand grip: dark teal leather, criss-cross wrap, a steel ring in the middle
    g = E.part(cv, [(-2.3, 3.4), (2.3, 3.4), (2.5, 19.5), (-2.5, 19.5)], cx, cy, ang, k, TGRIP, noise=0.05, seed=52)
    E.crosswrap(cv, E.erode(g, 1) if k > 1 else g, cx, cy, ang, k, 3.4, 19.5, 2.3, E.ramp('#5a7e86', 5))
    E.part(cv, [(-2.9, 10.6), (2.9, 10.6), (2.9, 12.4), (-2.9, 12.4)], cx, cy, ang, k, E.STEEL)
    E.part(cv, [(-3.1, 19.2), (3.1, 19.2), (3.1, 20.8), (-3.1, 20.8)], cx, cy, ang, k, E.STEEL)
    # pommel: steel ball with a violet gem
    P = E.xf([(0, 23.2)], cx, cy, ang)[0]
    m = E.ell(cv, P[0] * k, P[1] * k, 3.0 * k, 3.0 * k)
    E.shade(cv, m, E.STEEL, 'sphere', cx=(P[0] - 1) * k, cy=(P[1] - 1) * k, rx=3.8 * k, ry=3.8 * k)
    if k > 1:
        E.knob(cv, P[0], P[1], 1.2, k, VIOL)


def spellblade(cv, k, rp):
    # the arcane crescent sweep behind the sword (the wide arc of Arcane Breach / Momentum), sweeping round the lower left
    m = crescent(cv, 33.0, 31.0, 20.0, 6.5, math.radians(140.0), math.radians(170.0), k)
    E.shade(cv, m, ARCL, 'grad', bevel=0.14, level=0.04)
    if k > 1:      # bright inner edge of the sweep
        core = crescent(cv, 33.0, 31.0, 18.6, 2.4, math.radians(140.0), math.radians(120.0), k) & m
        E.shade(cv, core, ARCL, 'flat', outline=False, bevel=0.0, v=0.96)
    greatsword(cv, 34.0, 33.5, 0.62, k)


E.SYMBOLS["Spellblade"] = spellblade


# ---------------------------------------------------------------------------------------------------------- output
def rel(name, kind):
    suffix = {"64": "", "128": "_128", "locked": "_Locked"}[kind]
    return "Common/Icons/ClassEmblems/%s%s.png" % (name, suffix)


def render(name, col):
    i64 = E.emblem(name, col, 64).img()
    i128 = E.emblem(name, col, 128).img()
    return {"64": i64, "128": i128, "locked": E.locked(i64)}


def same_pixels(a, b):
    return a.size == b.size and a.convert("RGBA").tobytes() == b.convert("RGBA").tobytes()


FONT_PATHS = {True: ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/segoeuib.ttf"],
              False: ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/segoeui.ttf"]}


def font(sz, bold=True):
    for p in FONT_PATHS[bold]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


PAGE = (246, 244, 239)
INK = (28, 28, 34)
SUB = (84, 86, 96)
HUD = (22, 27, 36)
HUD_EDGE = (52, 62, 78)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def sheet(res):
    """plain light page, big labels (Skyy is dyslexic): per class the 128 at 2x, then 128 / 64 / 32 / locked, name, colour,
    APPROVED or DRAFT tag; a dark HUD strip with all 8 at 64 and 32 px; a dark Profiles-style row mock"""
    COLW, PADX = 300, 40
    W = PADX * 2 + 4 * COLW
    rows = (len(res) + 3) // 4
    CELL_H = 560
    TOP = 150
    H = TOP + rows * CELL_H + 360
    im = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(im)
    d.text((PADX, 26), "SkyWynn class emblems - 8 classes", font=font(52), fill=INK)
    d.text((PADX, 92), "7 approved crests (Skyy 2026-10-06) + the new Spellblade crest (DRAFT, for review).   "
                       "Sizes: 128 at 2x, 128, 64, 32, locked 64.", font=font(22, False), fill=SUB)
    for i, (name, col, role, weapons, status, imgs) in enumerate(res):
        cx = PADX + (i % 4) * COLW + COLW // 2
        y0 = TOP + (i // 4) * CELL_H
        im.alpha_composite(imgs["128"].resize((256, 256), Image.NEAREST), (cx - 128, y0))
        y = y0 + 266
        x = cx - (128 + 64 + 32 + 64 + 3 * 8) // 2
        im.alpha_composite(imgs["128"], (x, y))
        im.alpha_composite(imgs["64"], (x + 136, y + 64))
        im.alpha_composite(imgs["64"].resize((32, 32), Image.BOX), (x + 208, y + 96))
        im.alpha_composite(imgs["locked"], (x + 248, y + 64))
        y += 140
        tw = d.textlength(name.upper(), font=font(36))
        d.text((cx - tw / 2, y), name.upper(), font=font(36), fill=INK)
        d.rounded_rectangle([cx - 24 - tw / 2 - 36, y + 8, cx - tw / 2 - 16, y + 36], 6, fill=hexrgb(col), outline=INK, width=2)
        for li, sub in enumerate((col, weapons)):
            sw = d.textlength(sub, font=font(18, False))
            d.text((cx - sw / 2, y + 44 + li * 22), sub, font=font(18, False), fill=SUB)
        tag = "APPROVED" if status == "APPROVED" else "NEW - FOR REVIEW"
        tcol = (40, 120, 60) if status == "APPROVED" else (176, 70, 20)
        tw2 = d.textlength(tag, font=font(20))
        d.rounded_rectangle([cx - tw2 / 2 - 12, y + 94, cx + tw2 / 2 + 12, y + 126], 8, outline=tcol, width=3)
        d.text((cx - tw2 / 2, y + 97), tag, font=font(20), fill=tcol)
    y0 = TOP + rows * CELL_H
    d.text((PADX, y0), "On a dark HUD (64 px, then 32 px) and in a Profiles-style row", font=font(30), fill=INK)
    d.rounded_rectangle([PADX, y0 + 50, W - PADX, y0 + 170], 14, fill=HUD, outline=HUD_EDGE, width=3)
    x = PADX + 24
    for name, col, role, weapons, status, imgs in res:
        im.alpha_composite(imgs["64"], (x, y0 + 78))
        im.alpha_composite(imgs["64"].resize((32, 32), Image.BOX), (x + 70, y0 + 94))
        x += 142
    # Profiles row mock (the screenshot Skyy sent: 'Spellblade Aragorn - ACTIVE')
    ry = y0 + 190
    d.rounded_rectangle([PADX, ry, W - PADX, ry + 120], 14, fill=HUD, outline=HUD_EDGE, width=3)
    sb = [r for r in res if r[0] == "Spellblade"][0]
    wr = [r for r in res if r[0] == "Warrior"][0]
    for j, (r, label, state) in enumerate(((sb, "Spellblade Aragorn", "ACTIVE"), (wr, "Warrior (empty slot)", "LOCKED"))):
        bx = PADX + 20 + j * 580
        im.alpha_composite(r[5]["64"] if state == "ACTIVE" else r[5]["locked"], (bx, ry + 28))
        d.text((bx + 80, ry + 34), label, font=font(28), fill=hexrgb(r[1]) if state == "ACTIVE" else (150, 160, 172))
        d.text((bx + 80, ry + 72), state, font=font(20, False), fill=(183, 206, 221))
    return im.convert("RGB")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()
    res = []
    for name, col, role, weapons, status in CLASSES:
        imgs = render(name, col)
        if status == "APPROVED":
            # the APPROVED PNGs are the source of truth: ship their pixels as Skyy saw them. A re-render matches them except a
            # handful of anti-aliasing pixels on the Archer's thin bow string under a newer Pillow (4 px at 64, 9 px at 128) -
            # reported, never shipped.
            for kind, fn in (("64", "64"), ("128", "128"), ("locked", "64-locked")):
                ref = Image.open(os.path.join(CLOUD, "icons", "class-%s-%s.png" % (name.lower(), fn))).convert("RGBA")
                if not same_pixels(imgs[kind], ref):
                    print("  note: %s %s re-render differs from the approved PNG; the approved PNG is used" % (name, kind))
                imgs[kind] = ref
        for kind, im in imgs.items():
            p = os.path.join(a.out, rel(name, kind))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            im.save(p, optimize=True)
        res.append((name, col, role, weapons, status, imgs))
        print("wrote", name, status)
    sp = os.path.join(a.out, "sheet.png")
    sheet(res).save(sp, optimize=True)
    print("wrote", sp)
    files = []
    for name, col, role, weapons, status, imgs in res:
        for kind in ("64", "128", "locked"):
            p = os.path.join(a.out, rel(name, kind))
            files.append({"path": rel(name, kind), "bytes": os.path.getsize(p), "sha256": sha(p),
                          "image_size": list(imgs[kind].size), "class": name, "class_colour": col, "kind": kind,
                          "status": "APPROVED by Skyy 2026-10-06 (docs/answered/gear.md line 86), same pixels as "
                                    "research/cloud/class-art/icons/" if status == "APPROVED" else
                                    "DRAFT - waiting for Skyy's review, NOT committed"})
    files.append({"path": "sheet.png", "bytes": os.path.getsize(sp), "sha256": sha(sp), "what": "review sheet, all 8 classes"})
    man = {
        "item": "Class emblems (shield crests) - " + ", ".join(c[0] for c in CLASSES),
        "in_game": "NOT wired in, NOT seen in game",
        "generator": ["tools/art/make_class_emblems.py", "research/cloud/class-art/make_emblems.py (approved painter, imported)"],
        "deterministic": True,
        "approved_source": "research/cloud/class-art/ (Skyy 2026-10-06 'they look great!'; v2 Monk + Priest 10-07; v2 others 10-08)",
        "sizes": {"64": "64 x 64 RGBA (lists, HUD, Profiles rows)", "128": "128 x 128 RGBA (class cards)",
                  "locked": "64 x 64 grey 'coming later / empty slot' version"},
        "class_colours": {c[0]: c[1] for c in CLASSES},
        "files": files,
    }
    mp = os.path.join(a.out, "manifest.json")
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2)
        f.write("\n")
    print("wrote", mp)


if __name__ == "__main__":
    main()
