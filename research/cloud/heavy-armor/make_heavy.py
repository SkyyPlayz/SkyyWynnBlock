#!/usr/bin/env python3
"""SkyWynn Heavy Armor tier 1 - Heavy Leather concept (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/heavy-armor/make_heavy.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

Reuses the painter, mask helpers and mannequin palette of
research/cloud/light-armor/make_sheets.py (imported, never changed), so the
figure has the same 64 x 84 grid, 1-px outline and 4-step top-left shading.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'light-armor'))
import make_sheets as ms  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

rect, ell, poly, mirror, clip = ms.rect, ms.ell, ms.poly, ms.mirror, ms.clip
top_rim, bottom_rim, banded, X = ms.top_rim, ms.bottom_rim, ms.banded, ms.X
SCALE, CHEST_SCALE = ms.SCALE, ms.CHEST_SCALE

# ---------------------------------------------------------------- palettes [outline, dark, mid, light, highlight]
HIDE = ms.ramp('#1f0f07', '#4a2814', '#6a3c1f', '#8a542c', '#ab7040')      # thick boiled brown leather (plates)
PAD = ms.ramp('#4a3520', '#8f7149', '#b39365', '#cfb183', '#ead4a8')       # tan padding / gambeson
PAD_IN = ms.ramp('#2e2114', '#5e4830', '#77603f', '#8f7650', '#a68c63')    # padding on the far side / back
STRAP = ms.ramp('#140a05', '#33200f', '#4a2f18', '#634024', '#7d5533')     # dark belt + straps
STUD = ms.ramp('#1e1f22', '#4c4f55', '#72767d', '#9da1a8', '#c9ccd1')      # dull iron studs + rivets
BRASS = ms.BRASS                                                           # buckles (same brass as Light)
DUMMY = ms.DUMMY


def gambeson(x, y, i):
    """quilted padding: stitched channels every 4 px across, every 5 px down"""
    if i == 0:
        return 0
    if x % 4 == 0 or y % 5 == 0:
        return 1
    if x % 4 == 1:
        return min(4, i + 1)
    return i


def lames(*rows):
    """overlapping leather bands: a dark seam row, then a lit row under it"""
    def f(x, y, i):
        if i in (2, 3, 4) and y in rows:
            return 1
        if i in (2, 3) and y - 1 in rows:
            return 3
        return i
    return f


def studs(f, pts, rp=STUD):
    for x, y in pts:
        f.dots([(x, y, 4), (x + 1, y, 2), (x, y + 1, 2), (x + 1, y + 1, 1)], rp)


def heavy_buckle(f, x, y):
    ms.buckle(f, x, y, BRASS, w=7, h=7)
    f.dots([(x + 3, y + 3, 3), (x + 3, y + 4, 2)], BRASS)


# ---------------------------------------------------------------- the figure
def draw_heavy(back=False, bust=False):
    f = ms.Fig()
    sides = (0, 1)

    def S(m, side):
        return m if side == 0 else mirror(m)

    # --- mannequin (same neutral faceless figure as the Light sheets)
    if not bust:
        f.paint(rect(21, 48, 31, 81) | rect(32, 48, 42, 81), DUMMY, kind='dummy')
    for side in sides:
        f.paint(S(rect(13, 22, 19, 58), side), DUMMY, kind='dummy')
    f.paint(rect(27, 14, 36, 22), DUMMY, kind='dummy')
    head = rect(24, 0, 39, 17) | rect(23, 1, 40, 16) | rect(22, 3, 41, 14)
    if not bust:
        f.paint(head, DUMMY, kind='dummy')

    # --- legs: padded trousers, big knee cops, studded greaves, heavy boots
    if not bust:
        for side in sides:
            f.paint(S(rect(20, 48, 31, 74), side), PAD_IN if back else PAD, pattern=gambeson)
            gr = S(poly([(20, 64), (31, 64), (31, 76), (21, 76)]), side)
            f.paint(gr, HIDE, pattern=lames(69))
            if not back:
                studs(f, [(X(22, side) - (1 if side else 0), 66), (X(22, side) - (1 if side else 0), 72),
                          (X(29, side) - (1 if side else 0), 66), (X(29, side) - (1 if side else 0), 72)])
            km = S(ell(19, 56, 32, 67), side)
            f.paint(km, HIDE, pattern=lames(61))
            f.paint(S(ell(23, 58, 28, 63), side), HIDE)            # raised knee boss
            if not back:
                studs(f, [(X(25, side) - (1 if side else 0), 60)])
            bm = S(rect(19, 75, 32, 82) | rect(18, 78, 32, 82), side)
            f.paint(bm, STRAP, pattern=banded(80))
            f.paint(S(rect(19, 74, 32, 76), side), PAD_IN if back else PAD)   # boot cuff roll
            f.paint(S(rect(20, 78, 31, 79), side), HIDE, outline=False)
            if not back:
                ms.buckle(f, X(24, side) - (4 if side else 0), 77, BRASS, w=5, h=4)

    # --- tassets: three big studded flaps over the hips (front), two on the back
    if not bust:
        f.paint(rect(18, 46, 45, 62), PAD_IN if back else PAD, pattern=gambeson)   # padded skirt
        flaps = [(18, 26, 56), (27, 36, 58), (37, 45, 56)] if not back else [(18, 31, 57), (32, 45, 57)]
        for x0, x1, y1 in flaps:
            tm = rect(x0, 46, x1, y1) | rect(x0 + 1, y1 + 1, x1 - 1, y1 + 1)
            f.paint(tm, HIDE, pattern=lames(52))
            f.paint(bottom_rim(tm, 2) - bottom_rim(tm, 1), PAD, outline=False)   # tan padding edge
            if not back:
                studs(f, [(x0 + 2, y1 - 3), (x1 - 3, y1 - 3)])

    # --- arms: padded sleeve, thick studded bracer, full leather gauntlet
    for side in sides:
        f.paint(S(rect(12, 32, 20, 43), side), PAD_IN if back else PAD, pattern=gambeson)
        br = S(poly([(11, 44), (21, 44), (21, 53), (11, 53)]), side)
        f.paint(br, HIDE, pattern=lames(48))
        f.paint(S(rect(11, 44, 21, 45), side), STRAP, outline=False)     # bracer strap
        if not back:
            studs(f, [(X(13, side) - (1 if side else 0), 50), (X(18, side) - (1 if side else 0), 50)])
        gl = S(rect(12, 53, 20, 59) | rect(11, 54, 21, 58), side)
        f.paint(gl, STRAP, pattern=banded(56))
        f.dots([(X(14, side), 55, 3), (X(16, side), 55, 3), (X(18, side), 55, 3)], STRAP, kind='leather')

    # --- torso: tan gambeson under a thick boiled-leather cuirass
    torso = rect(18, 20, 45, 48)
    f.paint(torso, PAD_IN if back else PAD, pattern=gambeson)
    if not back:
        cu = poly([(20, 21), (43, 21), (44, 30), (42, 41), (21, 41), (19, 30)])
        f.paint(cu, HIDE)
        # centre ridge: lit left half, shaded right half
        f.dots([(31, y, 4) for y in range(23, 40)] + [(32, y, 1) for y in range(23, 40)], HIDE, kind='leather')
        # two riveted chest plates (left + right), then abdomen lames
        for side in sides:
            pl = S(poly([(21, 23), (30, 23), (30, 31), (22, 32)]), side)
            f.paint(pl, HIDE, edge_ref=pl)
            studs(f, [(X(22, side) - (1 if side else 0), 24), (X(28, side) - (1 if side else 0), 24),
                      (X(23, side) - (1 if side else 0), 29), (X(28, side) - (1 if side else 0), 29)])
        f.paint(rect(21, 33, 42, 41), HIDE, pattern=lames(35, 38))
        studs(f, [(x, 33) for x in (22, 27, 35, 40)] + [(x, 39) for x in (22, 40)])
        for side in sides:     # dark shoulder straps holding the cuirass
            f.paint(S(rect(22, 19, 24, 41), side), STRAP, pattern=banded(26, 34))
            studs(f, [(X(22, side) - (1 if side else 0), 37)], BRASS)
    else:
        bp = poly([(20, 21), (43, 21), (44, 30), (42, 41), (21, 41), (19, 30)])
        f.paint(bp, HIDE, pattern=lames(28, 32, 36))
        # crossed back straps
        for m in (poly([(20, 22), (23, 22), (43, 39), (40, 40)]), mirror(poly([(20, 22), (23, 22), (43, 39), (40, 40)]))):
            f.paint(m, STRAP)
        f.paint(ell(28, 27, 35, 34), STRAP)
        studs(f, [(31, 30)], BRASS)

    # --- thick double belt with a big brass buckle
    belt = rect(17, 41, 46, 47)
    f.paint(belt, STRAP, pattern=banded(44))
    if not back:
        heavy_buckle(f, 28, 41)
        studs(f, [(20, 42), (24, 42), (38, 42), (42, 42)], BRASS)
        pouch = rect(40, 46, 46, 54)
        f.paint(pouch, HIDE)
        f.paint(rect(40, 46, 46, 49), HIDE, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        studs(f, [(42, 48)], BRASS)
    else:
        studs(f, [(x, 42) for x in (20, 26, 31, 36, 42)], BRASS)

    # --- padded collar roll (gorget)
    gor = ell(19, 15, 44, 28) & rect(0, 17, 63, 25)
    f.paint(gor, PAD_IN if back else PAD, pattern=lambda x, y, i: 1 if i in (2, 3) and x % 3 == 0 else i)
    f.paint(rect(25, 18, 38, 20) if not back else rect(25, 17, 38, 19), STRAP if not back else PAD_IN)

    # --- big layered pauldrons (lowest plate first, top cap last), studded rims
    p3 = clip(ell(9, 26, 21, 41), y0=33)
    p2 = clip(ell(8, 21, 22, 36), y0=27)
    p1 = ell(6, 15, 23, 29)
    for side in sides:
        for k, pm in ((3, p3), (2, p2), (1, p1)):
            pm = S(pm, side)
            f.paint(pm, HIDE)
            f.paint(bottom_rim(pm, 2) - bottom_rim(pm, 1), PAD, outline=False)   # tan padding edge
        if not back:
            for x in (9, 13, 17):
                studs(f, [(X(x, side) - (1 if side else 0), 25)])
            for x in (11, 16):
                studs(f, [(X(x, side) - (1 if side else 0), 32)])
        else:
            for x in (10, 15, 20):
                studs(f, [(X(x, side) - (1 if side else 0), 25)])
        f.paint(S(rect(14, 16, 19, 18), side), STRAP)                # shoulder strap tab

    # --- helm: padded leather cap, studded brow band, cheek guards, nose guard
    if not bust:
        cap = ({(x + dx, y + dy) for x, y in head for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
               & rect(0, 0, 63, 9))
        f.paint(cap, HIDE, pattern=lambda x, y, i: 1 if i in (2, 3, 4) and x in (27, 31, 36) else i)
        brow = rect(21, 7, 42, 10)
        f.paint(brow, PAD_IN if back else PAD, pattern=banded(9) if back else None)
        if back:
            f.paint(rect(22, 10, 41, 15), HIDE, pattern=lames(13))    # neck guard
        else:
            for side in sides:
                f.paint(S(poly([(21, 10), (25, 10), (25, 17), (22, 18)]), side), HIDE)   # cheek guards
                studs(f, [(X(23, side) - (1 if side else 0), 13)])
            f.dots([(31, y, 3) for y in range(10, 15)] + [(32, y, 1) for y in range(10, 15)], HIDE, kind='leather')
            studs(f, [(x, 8) for x in (23, 27, 35, 39)])
    return f


# ---------------------------------------------------------------- output
font = ms.font


def save(im, name):
    im = im.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(HERE, name), optimize=True)


def chest_closeup(f):
    crop = f.im.crop((2, 9, 62, 62))
    ch = crop.resize((crop.width * CHEST_SCALE, crop.height * CHEST_SCALE), Image.NEAREST)
    base = Image.new('RGBA', ch.size, ms.BG)
    base.alpha_composite(ch)
    return base


def main():
    fr, bk, bu = draw_heavy(), draw_heavy(back=True), draw_heavy(bust=True)
    a, b = ms.scaled(fr, SCALE), ms.scaled(bk, SCALE)
    # set: front + back
    pair = Image.new('RGBA', (a.width * 2 + 12, a.height), ms.BG)
    pair.paste(a, (0, 0))
    pair.paste(b, (a.width + 12, 0))
    d = ImageDraw.Draw(pair)
    d.text((8, 6), 'front', font=font(14), fill=ms.INK)
    d.text((a.width + 20, 6), 'back', font=font(14), fill=ms.INK)
    save(ms.label(pair, 'Heavy Leather Armor (Heavy tier 1)', 'Lv 1-13  |  concept, cloud draft'), 'heavy-leather-set.png')
    ch = chest_closeup(bu)
    save(ms.label(ch, 'Heavy Leather Cuirass', 'Lv 1-13  |  front close-up'), 'heavy-leather-chest.png')

    # overview sheet: Light Copper (for bulk comparison) | Heavy front | Heavy back | chest close-up
    light = ms.scaled(ms.draw_figure(1), SCALE)
    chs = ch.resize((ch.width * a.height // ch.height, a.height), Image.NEAREST)
    gap, top, labh = 16, 70, 50
    cells = [(light, 'Light Copper (for scale)', 'Lv 10-18  |  existing design'),
             (a, 'Heavy Leather - front', 'Lv 1-13  |  Heavy tier 1'),
             (b, 'Heavy Leather - back', ''),
             (chs, 'Cuirass close-up', 'front')]
    sw = sum(c[0].width for c in cells) + gap * (len(cells) + 1)
    sheet = Image.new('RGBA', (sw, top + a.height + labh + 64), ms.BG)
    d = ImageDraw.Draw(sheet)
    d.text((sw // 2, 18), 'SkyWynn Heavy Armor tier 1 - Heavy Leather (cloud draft)', font=font(34), fill=ms.INK, anchor='mt')
    x = gap
    for im, t1, t2 in cells:
        sheet.paste(im, (x, top))
        d.text((x + im.width // 2, top + im.height + 6), t1, font=font(20), fill=ms.INK, anchor='mt')
        d.text((x + im.width // 2, top + im.height + 32), t2, font=font(14), fill=(60, 64, 70, 255), anchor='mt')
        x += im.width + gap
    # palette swatches
    y = top + a.height + labh + 20
    x = gap
    for nm, rp in (('hide', HIDE), ('padding', PAD), ('straps', STRAP), ('studs', STUD), ('buckles', BRASS)):
        for j, col in enumerate(rp[1:]):
            d.rectangle((x + j * 16, y, x + 12 + j * 16, y + 12), fill=col, outline=rp[0])
        d.text((x + 70, y - 1), nm, font=font(14), fill=ms.INK)
        x += 160
    save(sheet, 'heavy-armor-sheet.png')

    k = list(fr.kind.values())
    print('armor px (front):', len(k) - k.count('dummy'), '| light copper:',
          sum(1 for v in ms.draw_figure(1).kind.values() if v != 'dummy'))


if __name__ == '__main__':
    main()
