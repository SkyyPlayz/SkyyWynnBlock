#!/usr/bin/env python3
"""Review sheet for the Monk claws v1: base tier in 4 views, every tier side by side with its icon at 1x and 4x,
and the optional equip animation as frames. Reads the REAL generated files. Big labels, little text."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mc_render import render, rot_basis, bounds  # noqa: E402
import make_monk_claws as MC  # noqa: E402

ART = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "art", "monk-claws"))
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ART, "sheet.png"))
BG = (46, 50, 60, 255)
CELL = (68, 74, 88, 255)
SLOT = (30, 32, 38, 255)
INK = (240, 236, 226)
SAFF = (240, 138, 48)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda s: ImageFont.truetype(FB, s)

VIEWS = [("SIDE", rot_basis((0, -1, 0), (-1, 0, 0))),
         ("TOP", rot_basis((-1, 0, 0), (0, 1, 0))),
         ("FRONT", rot_basis((-0.3, -0.25, 1), (-1, 0, 0))),
         ("3/4", rot_basis((-0.8, -0.75, 0.35), (-1, 0, 0), 12))]
HERO = rot_basis((-0.8, -0.75, 0.35), (-1, 0, 0), 12)


def load(tier):
    b = os.path.join(ART, "Common/Items/Weapons/Fist/SkyyArmory_Claws_%s" % tier)
    return json.load(open(b + ".blockymodel")), Image.open(b + "_Texture.png").convert("RGBA")


def text_c(d, xy, s, size, fill=INK):
    f = F(size)
    w = d.textlength(s, font=f)
    d.text((xy[0] - w / 2, xy[1]), s, font=f, fill=fill)


def main():
    W = 2000
    base_m, base_t = load(MC.TIERS[0])
    anim = json.load(open(os.path.join(ART, "Common/Items/Weapons/Animations/SkyyArmory_Claws/SkyyArmory_Claws_Extend.blockyanim")))
    H = 120 + 880 + 60 + 700 + 60 + 360 + 30
    sheet = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((40, 28), "MONK CLAWS", font=F(64), fill=INK)
    d.text((40 + d.textlength("MONK CLAWS ", font=F(64)), 46), "v1", font=F(44), fill=SAFF)
    # row 1: base tier, 4 views in a 2 x 2 grid (each view filled to its cell)
    y0 = 120
    text_c(d, (W - 230, 50), "COPPER", 48, SAFF)
    cw, ch = (W - 80 - 20) // 2, 430
    for i, (lab, R) in enumerate(VIEWS):
        x = 40 + (i % 2) * (cw + 20)
        y = y0 + (i // 2) * (ch + 20)
        d.rounded_rectangle((x, y, x + cw, y + ch), 18, fill=CELL)
        img, _ = render(base_m, base_t, R, size=cw, scale=None, fill=0.9, ss=3, bg=(0, 0, 0, 0), wh=(cw - 200, ch - 20))
        sheet.alpha_composite(img, (x + 180, y + 10))
        d.text((x + 28, y + 22), lab, font=F(52), fill=INK)
    y0 += ch + 20 - 520 + ch
    # row 2: every tier
    y1 = y0 + 520 + 60
    d.text((40, y1 - 52), "ALL TIERS", font=F(40), fill=INK)
    n = len(MC.TIERS)
    tw = (W - 80 - (n - 1) * 14) // n
    lo_all, hi_all = bounds(base_m, HERO)
    hs = 0.92 * min(tw / (hi_all - lo_all)[0], 250 / (hi_all - lo_all)[1])
    for i, tier in enumerate(MC.TIERS):
        m, t = load(tier)
        x = 40 + i * (tw + 14)
        d.rounded_rectangle((x, y1, x + tw, y1 + 700), 18, fill=CELL)
        text_c(d, (x + tw / 2, y1 + 12), tier.upper(), 30, SAFF if i == 0 else INK)
        img, _ = render(m, t, HERO, size=tw, scale=hs, ss=3, bg=(0, 0, 0, 0), wh=(tw, 260))
        sheet.alpha_composite(img, (x, y1 + 50))
        icon = Image.open(os.path.join(ART, "Common/Icons/ItemsGenerated/SkyyArmory_Fist_Claws_%s.png" % tier)).convert("RGBA")
        # 1x
        sx = int(x + tw / 2 - 32 - 4)
        d.rectangle((sx, y1 + 318, sx + 72, y1 + 318 + 72), fill=SLOT)
        sheet.alpha_composite(icon, (sx + 4, y1 + 322))
        text_c(d, (x + tw / 2, y1 + 292), "1x", 22)
        # 4x
        big = icon.resize((256, 256), Image.NEAREST) if tw >= 256 else icon.resize((tw - 16, tw - 16), Image.NEAREST)
        bx = int(x + (tw - big.width) / 2)
        d.rectangle((bx, y1 + 420, bx + big.width, y1 + 420 + big.height), fill=SLOT)
        sheet.alpha_composite(big, (bx, y1 + 420))
        text_c(d, (x + tw / 2, y1 + 396), "4x" if big.width == 256 else "%.1fx" % (big.width / 64.0), 22)
    # row 3: optional equip animation
    y2 = y1 + 700 + 60
    d.text((40, y2 - 52), "EQUIP (optional): blades pop out", font=F(40), fill=INK)
    times = [4, 9, 14, anim["duration"]]
    fw = (W - 80 - (len(times) - 1) * 14) // len(times)
    for i, tm in enumerate(times):
        x = 40 + i * (fw + 14)
        d.rounded_rectangle((x, y2, x + fw, y2 + 360), 18, fill=CELL)
        img, _ = render(base_m, base_t, VIEWS[0][1], size=fw, scale=0.9 * fw / 60.0, ss=3, bg=(0, 0, 0, 0), wh=(fw, 300),
                        anim=anim, time=tm, center=last_c)
        if i == 0:
            pass
        sheet.alpha_composite(img, (x, y2 + 44))
        text_c(d, (x + fw / 2, y2 + 8), "%.2f s" % (tm / 60.0), 28)
    sheet.convert("RGB").save(OUT, optimize=True)
    print("sheet ->", OUT, sheet.size)


last_c = None
if __name__ == "__main__":
    # fixed centre for the animation frames = centre of the fully-out pose in the side view
    m0, _ = load(MC.TIERS[0])
    lo, hi = bounds(m0, VIEWS[0][1])
    last_c = (lo + hi) / 2
    main()
