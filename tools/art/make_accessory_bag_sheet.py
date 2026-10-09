#!/usr/bin/env python3
"""make_accessory_bag_sheet - writes the Accessory Bag menu icon, its review sheet and manifest.json.

Runs make_accessory_bag_icon.py's drawing (same code, in memory), then builds ONE review image for Skyy: big clear labels on a
plain background, the icon at actual size / 4x / 8x (nearest neighbour) on a dark and a light background, a mock of the
SkyWynn Menu grid (84 px slots, 62 px icons - SkyyMenu ItemGrid SlotSize 84 / SlotIconSize 62) and the gem list (FINAL: Option B gems, Skyy 2026-10-08).
Font: Atkinson Hyperlegible (falls back to DejaVu Sans). Deterministic: two runs = same bytes.

Run:  python make_accessory_bag_sheet.py [--out DIR]
"""
import argparse
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_accessory_bag_icon as IC  # noqa: E402

FONT_DIRS = ["/usr/share/fonts/truetype/sand-box/google/Atkinson Hyperlegible/AtkinsonHyperlegible-%s.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"]
PAGE = (246, 244, 239)          # plain warm off-white page
INK = (28, 28, 32)
SUB = (78, 80, 90)
DARK_BG = (27, 35, 48)          # dark menu-like background
LIGHT_BG = (214, 219, 226)      # light background
SLOT_BG = (22, 29, 40)
SLOT_EDGE = (52, 64, 80)
PANEL = (14, 19, 27)


def font(size, bold=True):
    for pat in FONT_DIRS:
        p = pat % ("Bold" if bold else "Regular") if "Atkinson" in pat else pat % ("-Bold" if bold else "")
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def tile(img, scale, bg, pad):
    w = img.width * scale + 2 * pad
    t = Image.new("RGBA", (w, w), bg + (255,))
    t.alpha_composite(img.resize((img.width * scale, img.height * scale), Image.NEAREST), (pad, pad))
    return t


def menu_mock(icon):
    """3 x 1 strip of SkyWynn-Menu-like slots (84 px, icon drawn at 62 px) with the bag in the middle; plus the name"""
    W, H = 3 * 84 + 2 * 16, 84 + 2 * 16 + 40
    m = Image.new("RGBA", (W, H), PANEL + (255,))
    d = ImageDraw.Draw(m)
    ic62 = icon.resize((62, 62), Image.LANCZOS)
    for i in range(3):
        x, y = 16 + i * 84, 16
        d.rectangle([x + 2, y + 2, x + 81, y + 81], fill=SLOT_BG, outline=SLOT_EDGE, width=2)
        if i == 1:
            m.alpha_composite(ic62, (x + 11, y + 11))
    f = font(22)
    txt = "Accessory Bag"
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, 16 + 84 + 6), txt, font=f, fill=(214, 228, 238))
    return m


def build_sheet(icon, gems, before=None):
    """FINAL sheet: actual size, 32 px, 4x, 8x (dark + light), the menu mock, the gem list and a small before / after at 4x"""
    S = Image.new("RGBA", (1520, 1580 if before is not None else 1180), PAGE + (255,))
    d = ImageDraw.Draw(S)
    F1, F2, F3 = font(46), font(30), font(24, bold=False)
    d.text((40, 28), "Accessory Bag  -  menu icon  (64 x 64)  -  FINAL", font=F1, fill=INK)
    d.text((40, 88), "For the SkyWynn Menu tile and the Workbench \"Accessories & Bags\" tab.  Gems: Option B.  Leather: lighter, more leather look.",
           font=F3, fill=SUB)

    y = 140
    d.text((40, y), "1.  Actual size (64 px)", font=F2, fill=INK)
    d.text((520, y), "2.  4 times bigger", font=F2, fill=INK)
    y += 46
    S.alpha_composite(tile(icon, 1, DARK_BG, 24), (40, y))
    S.alpha_composite(tile(icon, 1, LIGHT_BG, 24), (172, y))
    small = icon.resize((32, 32), Image.LANCZOS)
    S.alpha_composite(tile(small, 1, DARK_BG, 24), (304, y))
    S.alpha_composite(tile(small, 1, LIGHT_BG, 24), (404, y))
    d.text((40, y + 122), "dark", font=F3, fill=SUB)
    d.text((172, y + 122), "light", font=F3, fill=SUB)
    d.text((304, y + 122), "small (32 px)", font=F3, fill=SUB)
    S.alpha_composite(tile(icon, 4, DARK_BG, 16), (520, y))
    S.alpha_composite(tile(icon, 4, LIGHT_BG, 16), (820, y))
    d.text((520, y + 296), "dark", font=F3, fill=SUB)
    d.text((820, y + 296), "light", font=F3, fill=SUB)

    d.text((1140, 140), "3.  On a menu (mock)", font=F2, fill=INK)
    S.alpha_composite(menu_mock(icon), (1140, 186))
    d.text((1140, 186 + 166), "not the real game screen -", font=F3, fill=SUB)
    d.text((1140, 186 + 194), "84 px slots, 62 px icon", font=F3, fill=SUB)

    y = 540
    d.text((40, y), "4.  8 times bigger (to see every pixel)", font=F2, fill=INK)
    y += 46
    S.alpha_composite(tile(icon, 8, DARK_BG, 16), (40, y))
    S.alpha_composite(tile(icon, 8, LIGHT_BG, 16), (600, y))

    gx = 1180
    d.text((gx, 540), "5.  Gems, left to right", font=F2, fill=INK)
    yy = 600
    for name, cols in gems:
        d.rectangle([gx, yy, gx + 56, yy + 56], fill=tuple(int(v) for v in IC.hx(cols[1])), outline=INK, width=2)
        d.text((gx + 72, yy + 2), name, font=F2, fill=INK)
        d.text((gx + 72, yy + 34), "%s  %s" % (IC.GEM_COLOUR_WORD[name], cols[1]), font=font(20, bold=False), fill=SUB)
        yy += 80

    if before is not None:
        y = 1180
        d.text((40, y), "6.  Before  vs  after  (4 times bigger)  -  lighter black leather, more leather look", font=F2, fill=INK)
        y += 50
        for i, (im, label) in enumerate(((before, "BEFORE"), (icon, "AFTER"))):
            for j, bg in enumerate((DARK_BG, LIGHT_BG)):
                x = 40 + i * 600 + j * 290
                S.alpha_composite(tile(im, 4, bg, 9), (x, y + 40))
            d.text((40 + i * 600, y), label, font=F2, fill=INK)
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=IC.DEFAULT_OUT)
    args = ap.parse_args()
    before = IC.make_icon(IC.GEMS_LINES, look="v1")      # the previous FINAL (darker leather), for the comparison only
    icon = IC.make_icon(IC.GEMS_LINES, look="v2")
    ip = os.path.join(args.out, IC.ICON_REL)
    IC.save_png(icon, ip)
    sp = os.path.join(args.out, "sheet.png")
    IC.save_png(build_sheet(icon, IC.GEMS_LINES, before), sp)

    def entry(rel, what, extra=None):
        p = os.path.join(args.out, rel)
        with open(p, "rb") as fh:
            data = fh.read()
        im = Image.open(p)
        e = {"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "image_size": list(im.size),
             "mode": im.mode, "what": what}
        if extra:
            e.update(extra)
        return e

    man = {
        "item": "Accessory Bag menu icon (SkyWynn Menu tile + Workbench 'Accessories & Bags' tab)",
        "status": "FINAL gems picked by Skyy (Option B) + leather tweak v2; not committed, not wired in",
        "look": "v2",
        "history": [
            "v1: first FINAL - Option B gems (Skyy 2026-10-08: \"Use Option B gem colors\")",
            "v2: leather tweak (Skyy 2026-10-08: \"Make it a little brighter with a more leather look (still black leather, just "
            "lighter\") - lighter charcoal-black leather, soft sheen, worn lighter edges + corners, faint grain, lighter "
            "dashed stitching on flap / tongue / body, soft body folds; gold handle, clasp and gems unchanged"],
        "replaces": "vanilla Utility_Bag_Seed icon (SkyyMenu ENTRIES 'Accessory Bag'; tools/skyywbtab.py ICON_SRC)",
        "files": [
            entry(IC.ICON_REL, "64x64 RGBA item icon, transparent background, alpha only 0 or 255 (no partial alpha, so straight "
                               "vs premultiplied alpha makes no difference)",
                  {"gems_left_to_right": [{"line": n, "colour": IC.GEM_COLOUR_WORD[n], "hex_mid": c[1],
                                           "ramp_dark_mid_light_glint": c} for n, c in IC.GEMS_LINES],
                   "gem_choice": "Skyy 2026-10-08: \"Use Option B gem colors\"",
                   "cyan_source": "tools/art/make_accessory_icons.py WING ramp (the approved Speed accessory icon's wings), "
                                  "stops 2-5 (its outline tone #0c3a44 skipped); red/yellow/blue/green ramps = tools/art/make_bags.py ACC_GEMS"}),
            entry("sheet.png", "FINAL review sheet (actual size, 32 px, 4x, 8x on dark + light, menu mock, gem list, "
                               "before vs after at 4x)"),
        ] + ([{"path": "README.md", "what": "what it is, how made, gem colour source, UNVERIFIED items, open questions"}]
             if os.path.exists(os.path.join(args.out, "README.md")) else []),
        "generators": ["tools/art/make_accessory_bag_icon.py", "tools/art/make_accessory_bag_sheet.py"],
        "view": {"yaw_deg": IC.YAW, "pitch_deg": IC.PITCH, "fill_px": IC.FILL, "supersample": IC.SS},
        "model_boxes": [{"name": b.name, "material": b.mat, "from": [float(v) for v in b.lo], "to": [float(v) for v in b.hi]}
                        for b in IC.build_bag()],     # LOOK is v2 here (make_icon(look="v2") ran last)
        "palette": {"leather_v2": ["#%02x%02x%02x" % tuple(int(v) for v in c) for c in IC.LEATHER_V2],
                    "leather_v1_before": ["#%02x%02x%02x" % tuple(int(v) for v in c) for c in IC.LEATHER_V1],
                    "stitch_thread_v2": ["#%02x%02x%02x" % tuple(int(v) for v in c) for c in IC.THREAD],
                    "gold": ["#%02x%02x%02x" % tuple(int(v) for v in c) for c in IC.GOLD]},
        "description": "Original 64x64 Hytale-style icon: a chunky black leather satchel (soft charcoal-black with cool violet "
                       "shadows, a soft sheen, worn lighter edges, faint grain and lighter dashed stitching; never #000) with a "
                       "gold carry handle, a front flap with a stepped (rounded) hem and a leather strap tongue, a small gold "
                       "clasp bar on the tongue holding 5 small cut gems in the booster-line colours, left to right Health red, "
                       "Stamina yellow, Mana blue, Regeneration green, Speed cyan. 3/4 view, light from above, hue-shifted "
                       "shadows, 1 px dark outline.",
    }
    with open(os.path.join(args.out, "manifest.json"), "w", newline="\n") as fh:
        json.dump(man, fh, indent=2)
        fh.write("\n")
    print("icon:", ip)
    print("sheet:", sp)
    print("manifest:", os.path.join(args.out, "manifest.json"))


if __name__ == "__main__":
    main()
