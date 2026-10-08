#!/usr/bin/env python3
"""make_ability_sheet - review sheets + manifest.json for the SkyWynn class ability icons.

sheet.png = every class that has icons (APPROVED / FOR REVIEW tag per class); sheet-<class>.png = one sheet per class still
waiting for Skyy (CLASS_INFO review != "approved" in ability_icon_meta.py), so Skyy can review one class at a time.

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


def classes_done():
    seen = []
    for st, *_r in M.ICONS:
        if st.name not in seen:
            seen.append(st.name)
    return seen


def build_sheet(out, classes, title, show_hud=True):
    """one band per class (swatch, name, colour, status), each icon at 4x / 2x / 64 / 32 px, then a dark HUD strip"""
    COLW, PADX = 300, 40
    W = PADX * 2 + 5 * COLW
    BAND_H = 630
    TOP = 150
    HUD_ROW = 150
    HUD_H = (70 + len(classes) * HUD_ROW + 30) if show_hud else 0
    H = TOP + len(classes) * BAND_H + HUD_H + 30
    im = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(im)
    d.text((PADX, 28), title, font=font(52), fill=INK)
    d.text((PADX, 92), "Frame: round dark frame + class-colour rim. Background: dark with a class tint.   "
                       "Sizes: 4x, 2x, actual 64 px, 32 px.", font=font(24, False), fill=SUB)
    for b, cls in enumerate(classes):
        y0 = TOP + b * BAND_H
        info = CLASS_INFO[cls]
        col = hexrgb(info["hex"])
        d.rounded_rectangle([PADX, y0 + 6, PADX + 64, y0 + 70], 12, fill=col, outline=INK, width=3)
        d.text((PADX + 86, y0 + 4), cls.upper(), font=font(50), fill=INK)
        nw = d.textlength(cls.upper(), font=font(50))
        tag = "APPROVED" if info.get("review") == "approved" else "NEW - FOR REVIEW"
        tw = d.textlength(tag, font=font(26))
        tagcol = (40, 120, 60) if info.get("review") == "approved" else (176, 70, 20)
        d.rounded_rectangle([W - PADX - tw - 28, y0 + 14, W - PADX, y0 + 58], 10, outline=tagcol, width=3)
        d.text((W - PADX - tw - 14, y0 + 20), tag, font=font(26), fill=tagcol)
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
            x = cx - (128 + 64 + 32 + 2 * 14) // 2
            im.alpha_composite(ic.resize((128, 128), Image.NEAREST), (x, y))
            im.alpha_composite(ic, (x + 128 + 14, y + 64))
            im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 128 + 14 + 64 + 14, y + 96))
            d.text((x + 128 + 14 + 8, y + 34), "64", font=font(20, False), fill=SUB)
            d.text((x + 128 + 14 + 64 + 14 + 2, y + 66), "32", font=font(20, False), fill=SUB)
            y += 142
            ctext(d, cx, y, disp, font(38), INK)
            ctext(d, cx, y + 48, META[fn]["slot"] + "  -  " + META[fn]["status"].split(" (")[0], font(22, False), SUB)
    if show_hud:
        y0 = TOP + len(classes) * BAND_H
        d.text((PADX, y0), "On a dark HUD (actual size 64 px, then 32 px)", font=font(30), fill=INK)
        d.rounded_rectangle([PADX, y0 + 50, W - PADX, y0 + 50 + len(classes) * HUD_ROW + 10], 14, fill=HUD, outline=HUD_EDGE,
                            width=3)
        for r, cls in enumerate(classes):
            yy = y0 + 50 + 20 + r * HUD_ROW
            d.text((PADX + 24, yy + 40), cls, font=font(30), fill=hexrgb(CLASS_INFO[cls]["hex"]))
            x = PADX + 190
            for st, fn, disp, _p in [ic for ic in M.ICONS if ic[0].name == cls]:
                ic = load(out, st, fn)
                im.alpha_composite(ic, (x, yy + 6))
                im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 64 + 16, yy + 22))
                x += 64 + 16 + 32 + 120
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
    extras = [("sheet.png", "review sheet with EVERY done class: each icon at 4x / 2x / 64 / 32 px, grouped by class with the "
                            "class colour swatch + APPROVED / FOR REVIEW tag, plus a dark HUD strip")]
    for c in classes_done():
        if c in review_classes():
            extras.append(("sheet-%s.png" % c.lower(), "review sheet for the NEW %s icons only (same layout)" % c))
        else:  # approved class: its per-class sheet stays as Skyy reviewed it (not rebuilt)
            extras.append(("sheet-%s.png" % c.lower(), "the %s review sheet as Skyy reviewed + approved it (same layout)" % c))
    extras.append(("README.md", "what this is, ability -> meaning, colours, defaults, UNVERIFIED, open questions"))
    for extra, what in extras:
        p = os.path.join(out, extra)
        if os.path.exists(p):
            files.append({"path": extra, "bytes": os.path.getsize(p), "what": what}
                         | ({"sha256": sha(p)} if extra.endswith(".png") else {}))
    ramps = {}
    for name in ("FRAME", "MAGE_RIM", "PRIEST_RIM", "MONK_RIM", "FIRE", "ROCK", "ARCANE", "MANA", "ICE", "STARLIGHT", "GOLD",
                 "HOLY", "SOUL", "ROSE", "FEATHER", "STEEL", "SAFFRON", "LINEN", "SKIN", "SHOE", "SOLE", "WIND", "WATER", "ASSN_RIM", "SHADE",
                 "LILAC", "POISON", "GLASS", "SMOKE", "IRON", "WOOD"):
        ramps[name] = [M.K.hexs(c) for c in getattr(M, name)]
    return {
        "item": "Class ability icons - " + ", ".join(classes_done()),
        "status": {c: (("APPROVED by Skyy + committed" + (" (answer: \"%s\")" % CLASS_INFO[c]["answer"]
                                                          if CLASS_INFO[c].get("answer") else ""))
                       if CLASS_INFO[c].get("review") == "approved" else "NEW - waiting for Skyy's review, NOT committed")
                   for c in classes_done()},
        "in_game": "NOT wired in, NOT seen in game",
        "generator": ["tools/art/make_ability_icons.py", "tools/art/preview_ability_icons.py", "tools/art/ability_icon_core.py", "tools/art/ability_icon_meta.py",
                      "tools/art/make_ability_sheet.py", "tools/art/validate_ability_icons.py"],
        "deterministic": True,
        "defaults_used": {"frame": "round dark slate frame band with a class-colour rim (bevelled, top lit)",
                          "background": "dark field tinted toward the class colour, radial: " + ", ".join(
                              "%s %s -> %s" % (st.name, M.K.hexs(st.field_c), M.K.hexs(st.field_e))
                              for st in [M.MAGE, M.PRIEST, M.MONK, M.ASSASSIN] if st.name in classes_done())},
        "class_colours": {k: v["hex"] for k, v in CLASS_INFO.items()},
        "frame_geometry_px": {"outer_radius": M.K.R_OUT, "dark_band_inner": M.K.R_FRAME_IN, "rim_inner": M.K.R_RIM_IN,
                              "field_radius": M.K.R_FIELD, "centre": [32, 32]},
        "ramps_dark_to_light": ramps,
        "files": files,
    }


def review_classes():
    return [c for c in classes_done() if CLASS_INFO[c].get("review") != "approved"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=M.DEFAULT_OUT)
    a = ap.parse_args()
    done = classes_done()
    sheet = build_sheet(a.out, done, "SkyWynn ability icons - " + ", ".join(done))
    sp = os.path.join(a.out, "sheet.png")
    sheet.save(sp, optimize=True)
    print("wrote", sp, sheet.size)
    for c in review_classes():
        sh = build_sheet(a.out, [c], "SkyWynn ability icons - %s (new, for review)" % c)
        sp = os.path.join(a.out, "sheet-%s.png" % c.lower())
        sh.save(sp, optimize=True)
        print("wrote", sp, sh.size)
    mp = os.path.join(a.out, "manifest.json")
    with open(mp, "w") as f:
        json.dump(build_manifest(a.out), f, indent=2)
        f.write("\n")
    print("wrote", mp)


if __name__ == "__main__":
    main()
