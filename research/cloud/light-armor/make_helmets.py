#!/usr/bin/env python3
"""SkyWynn Light Armor - helmet options (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/light-armor/make_helmets.py
Writes helmets.png next to this script. Deterministic.

Reuses the painter, palettes and figure of make_sheets.py (imported, not
changed). The figure grid gets 6 extra rows on top (64 x 90) so a hood can
rise above the mannequin's head; helmet coordinates below are in that padded
grid (the head is x 22-41, y 6-23; the neck y 20-28).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_sheets as ms  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

D = 6                    # headroom rows added above the 64 x 84 figure
PH = ms.H + D            # padded height
SCALE = 6
CROP = (0, 0, 64, 50)    # head + shoulders + upper chest

COPPER = ms.TIERS[1][2]
ONYX = ms.TIERS[7][2]
GOLD = ms.GOLD
L, LI = ms.LEATHER, ms.LEATHER_IN
GLOW = ms.GLOW['Onyxium']


def dil(m, k=1):
    out = set(m)
    for _ in range(k):
        out |= {(x + dx, y + dy) for x, y in out for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    return out


def padded_figure(t):
    """the existing Light figure (front) on a 64 x 90 grid, plus a painter for it"""
    base = ms.draw_figure(t)
    ms.H = PH
    f = ms.Fig()
    f.im.paste(base.im, (0, D))
    f.px = f.im.load()
    f.kind = {(x, y + D): k for (x, y), k in base.kind.items()}
    return f


# ---------------------------------------------------------------- option A: hood with a metal rim
def hood(f, M, onyx):
    rimc = GOLD if onyx else M
    outer = ms.ell(19, 1, 44, 26) | ms.poly([(18, 18), (45, 18), (47, 30), (16, 30)])
    outer |= ms.poly([(28, 3), (31.5, 0), (35, 3)])            # small peak
    face = ms.ell(24, 8, 39, 28) & ms.rect(0, 0, 63, 23)       # opening: the face shows
    f.paint(outer - face, L, pattern=ms.banded(26))
    rim = (dil(face, 2) & outer) - face
    f.trim(rim, outer, rimc)
    shade = ms.top_rim(face, 2)                                # hood lining shadow on the brow
    f.paint(shade, LI, outline=False)
    # drape seam + hem rim on the shoulders
    f.trim(ms.bottom_rim(outer, 1) & ms.rect(0, 28, 63, 31), outer, M)
    if onyx:
        f.trim(ms.top_rim(outer, 2) & ms.rect(23, 0, 40, 9), outer, M)   # violet crown band
        f.paint(ms.poly([(31.5, 3), (34, 6), (31.5, 10), (29, 6)]), GOLD, kind='metal')
        f.px[31, 6] = GLOW
        f.px[32, 6] = GLOW
        for x in (21, 42):                                       # glow studs at the temples
            f.dots([(x, 16, 4), (x, 17, 2)], M)
        ms.buckle(f, 29, 26, GOLD)
    else:
        ms.leaf(f, 20, 11, M)
        ms.leaf(f, 39, 11, M, flip=True)
        ms.buckle(f, 29, 26, M)                                  # throat ring clasp


# ---------------------------------------------------------------- option B: half-mask cowl
def cowl(f, M, onyx):
    rimc = GOLD if onyx else M
    head = ms.rect(24, 6, 39, 23) | ms.rect(23, 7, 40, 22) | ms.rect(22, 9, 41, 20)
    snug = dil(head, 1) & ms.rect(0, 0, 63, 27)
    snug |= ms.rect(22, 20, 41, 27)                              # wraps the neck
    eyes = ms.rect(24, 12, 39, 16) | ms.rect(25, 11, 38, 11)     # open eye band
    f.paint(snug - eyes, L, pattern=ms.quilt)
    # brow band (metal) above the eye band
    brow = ms.rect(23, 9, 40, 10)
    f.trim(brow, snug, rimc)
    # lower mask plate: from the nose down, over the mouth
    mask = ms.poly([(23, 17), (40, 17), (39, 24), (34, 27), (29, 27), (24, 24)])
    f.paint(mask, L)
    f.trim(ms.top_rim(mask, 1), mask, M)
    f.dots([(31, y, 4) for y in range(16, 22)] + [(32, y, 2) for y in range(16, 22)] + [(31, 22, 1), (32, 22, 1)], M)   # nose ridge
    for y in (22, 24):                                           # breathing slits
        f.dots([(x, y, 1) for x in (27, 28, 35, 36)], L)
    if onyx:
        f.trim(ms.bottom_rim(mask, 1), mask, GOLD)                # gold edge along the mask
        f.dots([(26, 23, 3), (37, 23, 3), (27, 24, 1), (36, 24, 1)], GOLD)
        f.paint(ms.poly([(31.5, 3), (34, 7), (31.5, 11), (29, 7)]), GOLD, kind='metal')   # crest gem
        f.paint(ms.ell(30, 5, 33, 8), M, kind='metal')
        f.px[31, 6] = GLOW
        f.px[23, 11] = GLOW
        f.px[40, 11] = GLOW
    else:
        f.dots([(x, 9, 4) for x in (25, 31, 38)], M)             # brow rivets
        f.dots([(24, 19, 4), (39, 19, 4)], M)                    # mask strap rivets


# ---------------------------------------------------------------- option C: open leather cap
def cap(f, M, onyx):
    rimc = GOLD if onyx else M
    dome = ms.ell(21, 2, 42, 22) & ms.rect(0, 0, 63, 12)
    flaps = ms.poly([(21, 11), (25, 11), (25, 21), (22, 22)]) | ms.poly([(38, 11), (42, 11), (41, 22), (38, 21)])
    capm = dome | flaps
    f.paint(capm, L, pattern=lambda x, y, i: 1 if i in (2, 3) and x in (27, 31, 36) and y < 11 else i)
    band = ms.rect(21, 10, 42, 12) & capm | ms.rect(21, 11, 42, 12)
    f.trim(band, band, rimc)                                     # brow band
    # chin strap (brown) with a small buckle
    strap = ms.rect(23, 22, 24, 25) | ms.rect(39, 22, 40, 25) | ms.rect(24, 25, 39, 26)
    f.paint(strap, ms.STRAP, outline=False)
    f.dots([(23, 22, 0), (40, 22, 0)], ms.STRAP)
    f.dots([(30, 25, 3), (31, 25, 3), (32, 25, 3), (30, 26, 1), (32, 26, 1), (31, 26, 2)], M)
    if onyx:
        f.paint(ms.poly([(31.5, 0), (34, 4), (31.5, 9), (29, 4)]), GOLD, kind='metal')    # crest fin
        f.paint(ms.ell(30, 2, 33, 5), M, kind='metal')
        f.px[31, 3] = GLOW
        f.dots([(x, 11, 4) for x in (24, 28, 35, 39)], M)        # violet studs in the gold band
        f.dots([(23, 17, 3), (40, 17, 3)], GOLD)
        f.px[31, 11] = GLOW
    else:
        f.dots([(x, 11, 4) for x in (24, 28, 35, 39)], M)        # band rivets
        f.trim(ms.rect(31, 3, 32, 10) & capm, capm, M)           # copper ridge strip
        f.dots([(23, 17, 3), (40, 17, 3)], M)


OPTIONS = [('A  Hood + metal rim', hood), ('B  Half-mask cowl', cowl), ('C  Open leather cap', cap)]
ROWS = [(1, 'Copper', COPPER, False), (7, 'Onyxium', ONYX, True)]


def main():
    font = ms.font
    cw, chh = (CROP[2] - CROP[0]) * SCALE, (CROP[3] - CROP[1]) * SCALE
    gap, left, top, labh = 16, 130, 74, 30
    sheet_w = left + len(OPTIONS) * (cw + gap)
    sheet_h = top + len(ROWS) * (chh + labh + gap)
    sheet = Image.new('RGBA', (sheet_w, sheet_h), ms.BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), 'SkyWynn Light Armor - helmet options (cloud draft)', font=font(30), fill=ms.INK, anchor='mt')
    d.text((sheet_w // 2, 48), 'front view, on the same figure as light-armor-sheet.png  |  3 options x Copper + Onyxium',
           font=font(14), fill=(60, 64, 70, 255), anchor='mt')
    for r, (t, name, M, onyx) in enumerate(ROWS):
        y = top + r * (chh + labh + gap)
        d.text((left // 2, y + chh // 2 - 14), name, font=font(24), fill=ms.INK, anchor='mt')
        d.text((left // 2, y + chh // 2 + 14), ms.TIERS[t][1], font=font(14), fill=(60, 64, 70, 255), anchor='mt')
        for j, col in enumerate([M[3], M[2], M[1]]):
            d.rectangle((left // 2 - 26 + j * 18, y + chh // 2 + 36, left // 2 - 14 + j * 18, y + chh // 2 + 48),
                        fill=col, outline=M[0])
        for c, (oname, fn) in enumerate(OPTIONS):
            ms.H = 84
            f = padded_figure(t)
            fn(f, M, onyx)
            ms.H = 84
            im = f.im.crop(CROP).resize((cw, chh), Image.NEAREST)
            cell = Image.new('RGBA', im.size, ms.BG)
            cell.alpha_composite(im)
            x = left + c * (cw + gap)
            sheet.paste(cell, (x, y))
            d.text((x + cw // 2, y + chh + 6), f'{oname} - {name}', font=font(16), fill=ms.INK, anchor='mt')
    out = sheet.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out.save(os.path.join(HERE, 'helmets.png'), optimize=True)
    print('wrote helmets.png', sheet.size)


if __name__ == '__main__':
    main()
