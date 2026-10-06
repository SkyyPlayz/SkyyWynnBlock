#!/usr/bin/env python3
"""SkyWynn Cloth tier 1 - Crude Robe concept (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/cloth-armor/make_robe.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

Reuses the painter, mask helpers and mannequin palette of
research/cloud/light-armor/make_sheets.py (imported, never changed): same
64 x 84 grid, 1-px outline, 4-step shading lit from the top-left.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'light-armor'))
import make_sheets as ms  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

rect, ell, poly, mirror, clip = ms.rect, ms.ell, ms.poly, ms.mirror, ms.clip
top_rim, bottom_rim, X = ms.top_rim, ms.bottom_rim, ms.X
SCALE, CHEST_SCALE = ms.SCALE, ms.CHEST_SCALE

# ---------------------------------------------------------------- palettes [outline, dark, mid, light, highlight]
ROBE = ms.ramp('#0f2414', '#2a5c31', '#3b7a42', '#519a55', '#72bb6e')      # dyed green fibre (inner robe)
CLOAK = ms.ramp('#10180a', '#273a17', '#364f20', '#48662a', '#5f803a')     # moss-green outer cloak + mantle
LINING = ms.ramp('#070d08', '#0f1c11', '#152718', '#1c321f', '#243d27')    # hood lining / deep shadow
FIBRE = ms.ramp('#3b3220', '#7a6a46', '#9a8a5e', '#b8a87a', '#d6c89c')     # undyed fibre: trims, wraps
ROPE = ms.ramp('#33260f', '#6e5428', '#957238', '#b8924c', '#d8b46c')      # rope belt + cords
CRYSTAL = ms.ramp('#0b3320', '#178a4a', '#2fc46a', '#7cf0a0', '#d4ffe2')   # green crystal shards
GLOW = ms.hx('#eafff0')
DUMMY = ms.DUMMY


def weave(x, y, i):
    """rough hand weave: faint cross-hatch plus a few uneven slubs"""
    if i == 0:
        return 0
    h = (x * 7 + y * 13 + (x * y) % 5) % 17
    if i in (2, 3) and h == 0:
        return i - 1
    if i == 2 and h == 9:
        return 3
    if i == 2 and (x + 2 * y) % 6 == 0:
        return 1 if (x // 3) % 2 else 2
    return i


def rope_pat(x, y, i):
    if i == 0:
        return 0
    return (4, 3, 1)[(x + y) % 3] if i >= 2 else i


# small rune glyphs (3 x 3, '#' = dark stitch) repeated along trims
RUNES = [["#.#", ".#.", "#.#"], ["##.", "#.#", "##."], [".#.", "###", ".#."], ["#..", "##.", "#.#"]]


def rune_band(f, x0, x1, y0, rp=FIBRE, step=5):
    """a 5-px tall fibre trim with stitched runes (top-left lit edge)"""
    band = rect(x0, y0, x1, y0 + 4)
    f.paint(band, rp, pattern=lambda x, y, i: i if i in (0, 1) else (3 if y == y0 + 1 else 2))
    k = 0
    for gx in range(x0 + 2, x1 - 2, step):
        g = RUNES[(k + gx) % len(RUNES)]
        f.dots([(gx + dx, y0 + 1 + dy, 1) for dy, row in enumerate(g) for dx, ch in enumerate(row) if ch == '#'], rp, kind='trim')
        k += 1


def rune_strip(f, x0, y0, y1, rp=FIBRE):
    """a vertical 3-px fibre trim with a rune dot every 4 rows (cloak edges)"""
    m = rect(x0, y0, x0 + 2, y1)
    f.paint(m, rp, pattern=lambda x, y, i: i if i in (0, 1) else 2 + (y % 4 == 1))
    f.dots([(x0 + 1, y, 1) for y in range(y0 + 2, y1 - 1, 4)], rp, kind='trim')


def shard(f, x, y, big=False):
    """a green crystal shard (rough, unpolished), lit top-left, one glow pixel"""
    if big:
        m = poly([(x, y), (x + 3, y + 4), (x + 2, y + 10), (x - 2, y + 10), (x - 3, y + 4)])
    else:
        m = poly([(x, y), (x + 2, y + 3), (x + 1, y + 6), (x - 1, y + 6), (x - 2, y + 3)])
    f.paint(m, CRYSTAL, kind='crystal')
    f.dots([(x - 1, y + 3, 4), (x, y + 2, 4)], CRYSTAL, kind='crystal')
    f.px[x, y + (4 if big else 3)] = GLOW


# ---------------------------------------------------------------- the figure
def draw_robe(back=False, bust=False):
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
    face = ell(25, 6, 38, 26) & rect(0, 0, 63, 21)       # the hood opening: only this part of the head shows
    if not bust and not back:
        f.paint(head & face, DUMMY, kind='dummy', outline=False)

    # --- outer cloak, back layer (seen at the sides on the front view, whole on the back view)
    cb = poly([(17, 24), (46, 24), (49, 75), (14, 75)])
    if not bust:
        if not back:
            f.paint(cb, LINING, pattern=weave)
            for side in sides:
                f.paint(S(poly([(14, 40), (18, 40), (18, 75), (14, 75)]), side) & cb, CLOAK, pattern=weave, edge_ref=cb)

    # --- feet: fibre-wrapped shoes peeking under the robe
    if not bust:
        for side in sides:
            sh = S(rect(21, 78, 30, 82) | rect(20, 80, 30, 82), side)
            f.paint(sh, FIBRE, pattern=lambda x, y, i: 1 if i in (2, 3, 4) and (x + y) % 3 == 0 else i)

    # --- inner robe: long skirt flaring to the ankles, rune hem
    if not bust:
        skirt = poly([(20, 44), (43, 44), (47, 79), (16, 79)])
        f.paint(skirt, ROBE, pattern=weave)
        # ragged hem: a few notches cut out of the bottom row
        for x in (19, 26, 33, 41):
            f.px[x, 79] = (0, 0, 0, 0)
            f.kind.pop((x, 79), None)
        rune_band(f, 17, 46, 73)
        if back:   # the closed cloak hangs over the robe on the back
            f.paint(cb, CLOAK, pattern=weave)
            for x in range(16, 48, 6):                              # fold lines
                f.dots([(x + (y // 9) % 2, y, 1) for y in range(40, 69, 2)], CLOAK, kind='leather')
            rune_band(f, 15, 48, 70)

    # --- torso of the robe
    f.paint(rect(20, 21, 43, 46), ROBE, pattern=weave)

    # --- outer cloak, front: two long open panels framing the robe
    if not back:
        y1 = 72 if not bust else 60
        for side in sides:
            pn = S(poly([(19, 24), (28, 24), (27, 45), (25, y1), (17, y1 - 1)]), side)
            f.paint(pn, CLOAK, pattern=weave)
            rune_strip(f, X(25, side) - (2 if side else 0), 30, y1 - 3)

    # --- wide bell sleeves with fibre cuffs, bare hands
    for side in sides:
        sl = S(poly([(13, 24), (20, 24), (22, 51), (9, 53)]), side)
        f.paint(sl, ROBE, pattern=weave)
        cuff = S(poly([(10, 49), (22, 48), (22, 52), (9, 53)]), side)
        f.paint(cuff, FIBRE, pattern=lambda x, y, i: 1 if i in (2, 3) and x % 3 == 0 else i)
        f.paint(S(rect(14, 53, 18, 58), side), DUMMY, kind='dummy')

    # --- rope belt: twisted rope, knot on the wearer's right, hanging ends; crystal medallion on a cord
    belt = rect(19, 43, 44, 45)
    f.paint(belt, ROPE, pattern=rope_pat)
    if not back:
        knot = ell(22, 41, 27, 47)
        f.paint(knot, ROPE, pattern=rope_pat)
        for x0, y1 in ((23, 60), (26, 57)):
            f.paint(rect(x0, 47, x0 + 1, y1), ROPE, outline=False, pattern=lambda x, y, i: 1 if y % 3 == 0 else 3 - (x % 2))
            f.dots([(x0, y1 + 1, 2), (x0 + 1, y1 + 2, 1), (x0 - 1, y1 + 2, 1)], FIBRE)   # frayed ends
        # medallion: cord from the belt + a rough shard in a fibre-wrapped setting
        f.dots([(36, y, 1) for y in range(46, 49)] + [(38, y, 1) for y in range(46, 49)], ROPE)
        f.paint(ell(33, 48, 41, 56), FIBRE)
        shard(f, 37, 48)
    else:
        f.paint(ell(29, 41, 34, 47), ROPE, pattern=rope_pat)

    # --- layered mantle (short cape over the shoulders) with a ragged hem
    mant = ell(11, 15, 52, 40) & rect(0, 18, 63, 35)
    rag = {(x, y) for x, y in mant if y >= 32 and (x % 5 in (0, 1)) and y >= 34}
    mant = (mant - rag) - {(x, y) for x, y in mant if y >= 33 and x % 5 == 0}
    f.paint(mant, CLOAK, pattern=weave)
    f.paint(bottom_rim(mant, 2) - bottom_rim(mant, 1), FIBRE, outline=False, kind='trim')
    if not back:
        f.paint(ell(19, 20, 44, 34) & rect(0, 22, 63, 30), ROBE, pattern=weave)      # 2nd layer under the hood
        f.paint(bottom_rim(ell(19, 20, 44, 34) & rect(0, 22, 63, 30), 1), FIBRE, outline=False, kind='trim')

    # --- hood (up): deep opening, face in shadow, crystal clasp at the throat
    hood = ell(18, 0, 45, 30) & rect(0, 0, 63, 26)
    if not back:
        f.paint(hood - face, ROBE, pattern=weave)
        f.paint(top_rim(face, 4), LINING, outline=False)                 # deep shadow under the brow
        f.paint(top_rim(face, 6) - top_rim(face, 4), LINING, outline=False,
                pattern=lambda x, y, i: 1 if (x + y) % 2 else 2)        # shadow fading onto the face
        edge = ({(x + dx, y + dy) for x, y in face for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, -2))}
                & hood) - face
        f.trim(edge, hood, FIBRE)                                        # stitched fibre rim on the hood
        f.dots([(x, y, 1) for x, y in edge if (x + y) % 4 == 0 and y < 10], FIBRE, kind='trim')
        f.paint(rect(29, 21, 34, 25), ROPE, pattern=rope_pat)            # clasp cord
        shard(f, 31, 20, big=True)                                       # crystal clasp
    else:
        f.paint(hood | (head & rect(0, 0, 63, 20)), ROBE, pattern=weave)
        f.paint(poly([(31.5, 6), (33, 22), (30, 22)]), ROBE, outline=False,
                pattern=lambda x, y, i: 1)                               # back seam
        f.paint(rect(28, 26, 35, 27), FIBRE)
    return f


# ---------------------------------------------------------------- output
font = ms.font


def save(im, name):
    im = im.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(HERE, name), optimize=True)


def main():
    fr, bk, bu = draw_robe(), draw_robe(back=True), draw_robe(bust=True)
    a, b = ms.scaled(fr, SCALE), ms.scaled(bk, SCALE)
    pair = Image.new('RGBA', (a.width * 2 + 12, a.height), ms.BG)
    pair.paste(a, (0, 0))
    pair.paste(b, (a.width + 12, 0))
    d = ImageDraw.Draw(pair)
    d.text((8, 6), 'front', font=font(14), fill=ms.INK)
    d.text((a.width + 20, 6), 'back', font=font(14), fill=ms.INK)
    save(ms.label(pair, 'Crude Robe (Cloth tier 1)', 'Lv 1-13  |  concept, cloud draft'), 'crude-robe-set.png')

    # close-up: hood, clasp, mantle and the belt medallion (head included - the hood is the robe's face)
    fr2 = draw_robe()
    crop = fr2.im.crop((4, 0, 60, 60))
    ch = crop.resize((crop.width * CHEST_SCALE, crop.height * CHEST_SCALE), Image.NEAREST)
    base = Image.new('RGBA', ch.size, ms.BG)
    base.alpha_composite(ch)
    save(ms.label(base, 'Crude Robe - hood + chest', 'front close-up: crystal clasp, rope belt, shard medallion'), 'crude-robe-chest.png')

    light = ms.scaled(ms.draw_figure(1), SCALE)
    chs = base.resize((base.width * a.height // base.height, a.height), Image.NEAREST)
    gap, top, labh = 16, 70, 50
    cells = [(a, 'Crude Robe - front', 'Lv 1-13  |  Cloth tier 1'),
             (b, 'Crude Robe - back', ''),
             (chs, 'Hood + chest close-up', 'front'),
             (light, 'Light Copper (for scale)', 'existing design')]
    sw = sum(c[0].width for c in cells) + gap * (len(cells) + 1)
    sheet = Image.new('RGBA', (sw, top + a.height + labh + 64), ms.BG)
    d = ImageDraw.Draw(sheet)
    d.text((sw // 2, 18), 'SkyWynn Cloth tier 1 - Crude Robe (cloud draft)', font=font(34), fill=ms.INK, anchor='mt')
    x = gap
    for im, t1, t2 in cells:
        sheet.paste(im, (x, top))
        d.text((x + im.width // 2, top + im.height + 6), t1, font=font(20), fill=ms.INK, anchor='mt')
        d.text((x + im.width // 2, top + im.height + 32), t2, font=font(14), fill=(60, 64, 70, 255), anchor='mt')
        x += im.width + gap
    y = top + a.height + labh + 20
    x = gap
    for nm, rp in (('robe', ROBE), ('cloak', CLOAK), ('fibre trim', FIBRE), ('rope', ROPE), ('crystal', CRYSTAL)):
        for j, col in enumerate(rp[1:]):
            d.rectangle((x + j * 16, y, x + 12 + j * 16, y + 12), fill=col, outline=rp[0])
        d.text((x + 70, y - 1), nm, font=font(14), fill=ms.INK)
        x += 170
    save(sheet, 'crude-robe-sheet.png')
    k = list(fr.kind.values())
    print('front: crystal px', k.count('crystal'), 'of', len(k) - k.count('dummy'), 'armor px')


if __name__ == '__main__':
    main()
