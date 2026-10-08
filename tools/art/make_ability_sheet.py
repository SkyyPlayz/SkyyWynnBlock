#!/usr/bin/env python3
"""make_ability_sheet - the review sheet (sheet.png) + manifest.json for the SkyWynn Mage + Priest ability icons.

Sheet (Skyy is dyslexic, so: plain light page, big Atkinson Hyperlegible labels, lots of space): one band per class with its
colour swatch, then each icon at 4x (nearest neighbour), 2x and actual size (64 px), plus a 32 px copy; a dark HUD-like strip
at the bottom shows all 10 at 64 and 32 px side by side. Reads the PNGs written by make_ability_icons.py (run that first).
Deterministic: two runs = same bytes.

Run:  python3 make_ability_sheet.py [--out DIR]
"""
import argparse
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ability_icons as M  # noqa: E402
from ability_icon_meta import CLASS_INFO, META  # noqa: E402

FONTS = {True: ["/usr/share/fonts/truetype/sand-box/google/Atkinson Hyperlegible/AtkinsonHyperlegible-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
         False: ["/usr/share/fonts/truetype/sand-box/google/Atkinson Hyperlegible/AtkinsonHyperlegible-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]}
PAGE = (246, 244, 239)
INK = (28, 28, 34)
SUB = (84, 86, 96)
HUD = (22, 27, 36)
HUD_EDGE = (52, 62, 78)


def font(size, bold=True):
    for p in FONTS[bold]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def ctext(d, cx, y, txt, f, fill):
    w = d.textlength(txt, font=f)
    d.text((cx - w / 2, y), txt, font=f, fill=fill)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load(out, st, fn):
    return Image.open(os.path.join(out, M.rel_path(st, fn))).convert("RGBA")


def build_sheet(out):
    COLW, PADX = 300, 40
    W = PADX * 2 + 5 * COLW
    BAND_H = 630
    TOP = 150
    HUD_H = 260
    H = TOP + 2 * BAND_H + HUD_H + 40
    im = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(im)
    d.text((PADX, 28), "SkyWynn ability icons - Mage + Priest", font=font(52), fill=INK)
    d.text((PADX, 92), "Defaults used: round dark frame + class-colour rim, dark background with a class tint.   "
                       "Sizes: 4x, 2x, actual 64 px, 32 px.", font=font(24, False), fill=SUB)
    for b, cls in enumerate(("Mage", "Priest")):
        y0 = TOP + b * BAND_H
        info = CLASS_INFO[cls]
        col = hexrgb(info["hex"])
        # band header: swatch + class name + colour
        d.rounded_rectangle([PADX, y0 + 6, PADX + 64, y0 + 70], 12, fill=col, outline=INK, width=3)
        d.text((PADX + 86, y0 + 4), cls.upper(), font=font(50), fill=INK)
        nw = d.textlength(cls.upper(), font=font(50))
        d.text((PADX + 86 + nw + 24, y0 + 22), "class colour %s  -  %s" % (info["hex"], info["theme"]), font=font(24, False),
               fill=SUB)
        d.line([PADX, y0 + 84, W - PADX, y0 + 84], fill=col, width=6)
        icons = [ic for ic in M.ICONS if ic[0].name == cls]
        for i, (st, fn, disp, _p) in enumerate(icons):
            cx = PADX + i * COLW + COLW // 2
            ic = load(out, st, fn)
            y = y0 + 104
            im.alpha_composite(ic.resize((256, 256), Image.NEAREST), (cx - 128, y))
            y += 270
            # 2x, 1x, 32 px in a row
            x = cx - (128 + 64 + 32 + 2 * 14) // 2
            im.alpha_composite(ic.resize((128, 128), Image.NEAREST), (x, y))
            im.alpha_composite(ic, (x + 128 + 14, y + 64))
            im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 128 + 14 + 64 + 14, y + 96))
            d.text((x + 128 + 14 + 8, y + 34), "64", font=font(20, False), fill=SUB)
            d.text((x + 128 + 14 + 64 + 14 + 2, y + 66), "32", font=font(20, False), fill=SUB)
            y += 142
            ctext(d, cx, y, disp, font(38), INK)
            ctext(d, cx, y + 48, META[fn]["slot"] + "  -  " + META[fn]["status"].split(" (")[0], font(22, False), SUB)
    # HUD strip
    y0 = TOP + 2 * BAND_H
    d.text((PADX, y0), "On a dark HUD (actual size 64 px, then 32 px)", font=font(30), fill=INK)
    d.rounded_rectangle([PADX, y0 + 50, W - PADX, y0 + 50 + 190], 14, fill=HUD, outline=HUD_EDGE, width=3)
    x = PADX + 24
    for i, (st, fn, disp, _p) in enumerate(M.ICONS):
        ic = load(out, st, fn)
        im.alpha_composite(ic, (x, y0 + 50 + 24))
        im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 16, y0 + 50 + 24 + 64 + 18))
        x += 64 + 76 if i != 4 else 64 + 76 + 40
    return im.convert("RGB")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build_manifest(out):
    files = []
    for st, fn, disp, _p in M.ICONS:
        rp = M.rel_path(st, fn)
        p = os.path.join(out, rp)
        im = Image.open(p)
        m = META[fn]
        files.append({
            "path": rp, "bytes": os.path.getsize(p), "sha256": sha(p), "image_size": list(im.size), "mode": im.mode,
            "what": "64x64 RGBA ability icon; round frame, alpha 0 outside the circle and 255 inside (hard alpha only)",
            "class": st.name, "ability": disp, "file_name": fn + ".png", "slot": m["slot"], "status": m["status"],
            "cost_cooldown": m["cost_cd"], "ability_does": m["does"], "icon_shows": m["shows"], "palettes": m["palette"],
        })
    for extra, what in (("sheet.png", "review sheet for Skyy: every icon at 4x / 2x / 64 / 32 px, grouped by class with the "
                                      "class colour swatch, plus a dark HUD strip"),
                        ("README.md", "what this is, ability -> meaning, colours, defaults, UNVERIFIED, open questions")):
        p = os.path.join(out, extra)
        if os.path.exists(p):
            files.append({"path": extra, "bytes": os.path.getsize(p), "what": what}
                         | ({"sha256": sha(p)} if extra == "sheet.png" else {}))
    ramps = {}
    for name in ("FRAME", "MAGE_RIM", "PRIEST_RIM", "FIRE", "ROCK", "ARCANE", "MANA", "ICE", "STARLIGHT", "GOLD", "HOLY",
                 "SOUL", "ROSE", "FEATHER", "STEEL"):
        ramps[name] = [M.K.hexs(c) for c in getattr(M, name)]
    return {
        "item": "Class ability icons - Mage + Priest (ART-RESUME NEXT ITEM 5)",
        "status": "candidate for Skyy's review; NOT committed, NOT wired in, NOT seen in game",
        "generator": ["tools/art/make_ability_icons.py", "tools/art/ability_icon_core.py", "tools/art/ability_icon_meta.py",
                      "tools/art/make_ability_sheet.py", "tools/art/validate_ability_icons.py"],
        "deterministic": True,
        "defaults_used": {"frame": "round dark slate frame band with a class-colour rim (bevelled, top lit)",
                          "background": "dark field tinted toward the class colour (Mage navy #26335e -> #0e1226, "
                                        "Priest warm umber #43381e -> #15100c, radial)"},
        "class_colours": {k: v["hex"] for k, v in CLASS_INFO.items()},
        "frame_geometry_px": {"outer_radius": M.K.R_OUT, "dark_band_inner": M.K.R_FRAME_IN, "rim_inner": M.K.R_RIM_IN,
                              "field_radius": M.K.R_FIELD, "centre": [32, 32]},
        "ramps_dark_to_light": ramps,
        "files": files,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=M.DEFAULT_OUT)
    a = ap.parse_args()
    sheet = build_sheet(a.out)
    sp = os.path.join(a.out, "sheet.png")
    sheet.save(sp, optimize=True)
    print("wrote", sp, sheet.size)
    mp = os.path.join(a.out, "manifest.json")
    with open(mp, "w") as f:
        json.dump(build_manifest(a.out), f, indent=2)
        f.write("\n")
    print("wrote", mp)


if __name__ == "__main__":
    main()
