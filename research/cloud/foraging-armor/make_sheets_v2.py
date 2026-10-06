#!/usr/bin/env python3
"""SkyWynn Foraging Armor v2 - concept sheet (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/foraging-armor/make_sheets_v2.py
Writes foraging-armor-sheet-v2.png next to this script. The v1 script
(make_sheets.py) and its PNGs are not changed; this script imports it (read
only) for the painter, palettes and the approved designs.
Deterministic: same code -> same bytes.

Skyy's art review 2026-10-06 (docs/answered/gear.md, LOCKED): "i love
everything but the helmet of the gold wood. make it more like the mithril
armors helmet." -> the same approved designs at 2x-4x detail; the ONLY
design change is the Goldenwood helmet, which now echoes the vanilla Mithril
helmet (winged helm - the wing / crest description is UNVERIFIED, no game
files in the cloud). Its wings are golden leaves (still obviously wood).

How the detail is made: each figure is designed on the v1 64 x 84 grid,
then rendered at 2x (128 x 168) by a ramp-aware upscaler (up2, the same code
as research/cloud/gathering-armor-art/make_sheets_v2.py, copied): EPX corner
smoothing, 1-px outlines on the fine grid, a 1-px bevel per part (lit
top-left), and material texture by part (bark grain, leaf gloss, cloth
twill, rope weave, gold rim light + glints). Shown at x3 (v1 was 64-grid x5).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_sheets as m  # noqa: E402  (v1, read only)
from PIL import Image, ImageDraw  # noqa: E402

OUT = HERE
K = 2            # fine pixels per v1 grid pixel
SHOW = 3         # display scale of the fine grid
hx, ramp, mix = m.hx, m.ramp, m.mix
rect, ell, poly, line, clip, S, X = m.rect, m.ell, m.poly, m.line, m.clip, m.S, m.X
bottom_rim, top_rim, mirror = m.bottom_rim, m.top_rim, m.mirror


# ================================================================ painter that remembers ramps
class Fig2(m.Fig):
    """v1 Fig + a record of which ramp / kind painted each pixel (for up2)."""

    def __init__(self):
        super().__init__()
        self.meta = {}

    def paint(self, mask, rp, pattern=None, outline=True, edge_ref=None, kind='wood'):
        super().paint(mask, rp, pattern=pattern, outline=outline, edge_ref=edge_ref, kind=kind)
        tr = tuple(rp)
        for p in mask:
            if 0 <= p[0] < m.W and -m.TOP <= p[1] < m.H:
                self.meta[p] = (tr, kind)

    def dots(self, pts, rp, kind='trim'):
        super().dots(pts, rp, kind=kind)
        tr = tuple(rp)
        for x, y, i in pts:
            if 0 <= x < m.W and -m.TOP <= y < m.H:
                self.meta[(x, y)] = (tr, kind)

    def get(self, x, y):
        return self._px[x, y + m.TOP]


m.Fig = Fig2      # the v1 draw functions now build Fig2 figures


# ================================================================ 2x ramp-aware upscaler
def hsh(x, y, s=0):
    v = (x * 73856093) ^ (y * 19349663) ^ (s * 83492791)
    v = (v ^ (v >> 13)) * 1274126177
    return (v >> 7) & 0xff


METALLIC = {'trim', 'metal'}
SOFT = {'cloth', 'leather'}


def up2(f, tex=True):
    """64-grid Fig -> 2x RGBA image with real extra detail (see module doc)."""
    w, h = f.im.size
    px = f.im.load()
    ramps, rid = [], {}
    lab = {}
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c[3] == 0:
                continue
            mt = f.meta.get((x, y - m.TOP))
            if mt and c in mt[0]:
                rp, kind = mt
                if rp not in rid:
                    rid[rp] = len(ramps)
                    ramps.append(rp)
                lab[(x, y)] = ('r', rid[rp], rp.index(c), kind)
            else:
                lab[(x, y)] = ('c', c, f.kind.get((x, y - m.TOP), 'raw'))
    # --- EPX / Scale2x on the labels (rounds stair-step corners)
    W2, H2 = w * K, h * K
    L = {}
    for (x, y), P in lab.items():
        A, B, C, D = lab.get((x, y - 1)), lab.get((x + 1, y)), lab.get((x - 1, y)), lab.get((x, y + 1))
        e = [P, P, P, P]
        if C == A and C != D and A != B and A is not None:
            e[0] = A
        if A == B and A != C and B != D and B is not None:
            e[1] = B
        if D == C and D != B and C != A and C is not None:
            e[2] = C
        if B == D and B != A and D != C and D is not None:
            e[3] = D
        for k, (dx, dy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            L[(2 * x + dx, 2 * y + dy)] = e[k]
    def is_out(lb):
        return lb is not None and lb[0] == 'r' and lb[2] == 0

    def is_in(lb):
        return lb is not None and not is_out(lb)

    # --- 1-px outlines: drop the inner fine pixel of every 2-px outline
    L2 = dict(L)
    for (x, y), lb in L.items():
        if not is_out(lb):
            continue
        for dx, dy in ((1, 0), (0, 1)):
            prev, nxt = L.get((x - dx, y - dy)), L.get((x + dx, y + dy))
            nxt2 = L.get((x + 2 * dx, y + 2 * dy))
            rep = None
            if is_out(prev) and is_in(nxt):
                rep = nxt
            elif is_out(nxt) and is_in(prev) and nxt2 is None:
                rep = prev
            if rep is not None:
                if rep[0] == 'r':
                    L2[(x, y)] = ('r', rep[1], 1 if rep[2] >= 1 else 0, rep[3], 'seam')
                else:
                    L2[(x, y)] = ('c', mix(rep[1], (0, 0, 0, 255), 0.35)[:3] + (rep[1][3],), rep[2])
                break
    L = L2

    def same(a, b):
        return b is not None and a[0] == 'r' and b[0] == 'r' and a[1] == b[1] and not is_out(b)

    out = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    op = out.load()
    for (x, y), lb in L.items():
        if lb[0] == 'c':
            op[x, y] = lb[1]
            continue
        rp = ramps[lb[1]]
        i, kind = lb[2], lb[3]
        mat = MATS.get(rp) or KIND_MAT.get(kind, 'plain')
        top_ = 4 if len(rp) == 5 else len(rp) - 1
        if i == 0 or not tex or mat == 'none' or i > 4:
            op[x, y] = rp[i]
            continue
        u, l_, r_, d_ = L.get((x, y - 1)), L.get((x - 1, y)), L.get((x + 1, y)), L.get((x, y + 1))
        lt = not same(lb, u) or not same(lb, l_)
        dk = not same(lb, d_) or not same(lb, r_)
        j = i
        if lt and not dk and mat != 'dummy':
            j = min(4, i + 1)                       # 1 fine px rim light (top-left)
        elif dk and not lt and i >= 2:
            j = i - 1                               # 1 fine px inner shadow (bottom-right)
        else:
            j = TEX.get(mat, tex_plain)(x, y, i, lb[1])
        op[x, y] = rp[max(1, min(top_, j))]
    # --- stitching: a dashed light line 2 fine px inside the outline of leather / canvas parts
    if tex:
        pts = []
        for (x, y), lb in L.items():
            if lb[0] != 'r' or lb[2] == 0 or len(lb) > 4:
                continue
            if (MATS.get(ramps[lb[1]]) or KIND_MAT.get(lb[3])) not in STITCHED:
                continue
            if any(is_out(L.get((x + dx, y + dy))) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            hit = [(dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)) if is_out(L.get((x + dx, y + dy)))]
            if hit and (x + y) % 4 < 2:
                pts.append((x, y, lb))
        for x, y, lb in pts:
            rp = ramps[lb[1]]
            op[x, y] = rp[min(4, max(3, lb[2] + 1))]
    return out


# ---------------------------------------------------------------- fine-grid material textures
# each: (fine x, fine y, ramp index, ramp id) -> new ramp index
def tex_plain(x, y, i, s):
    h = hsh(x, y, s)
    return i - 1 if h < 12 and i >= 2 else (i + 1 if h > 246 else i)


def tex_metal(x, y, i, s):
    st = hsh(x // 7, y, s + 3)                      # brushed horizontal streaks
    if i in (2, 3) and st < 36:
        i = i + 1 if st < 12 else i - 1
    if hsh(x, y, s) > 252 and i >= 3:               # glints
        i = 4
    return i


def tex_leather(x, y, i, s):
    h = hsh(x, y, s)
    g = hsh(x // 2, y // 3, s + 9)                  # pebbled grain + creases
    if i >= 2 and g < 28:
        return i - 1
    if h > 240 and i <= 3:
        return i + 1
    return i


def tex_cloth(x, y, i, s):                          # twill: fine diagonal threads
    if i >= 2 and (x + 2 * y) % 5 == 0:
        return i - 1
    if (x + 2 * y) % 5 == 2 and hsh(x, y, s) < 70:
        return i + 1
    return i


def tex_denim(x, y, i, s):
    if i >= 2 and (x - y) % 3 == 0:
        return i - 1
    return i + 1 if hsh(x, y, s) > 244 else i


def tex_straw(x, y, i, s):                          # basket weave, 3 x 3 cells
    cx, cy = x // 3, y // 3
    u, v = x % 3, y % 3
    if (cx + cy) % 2 == 0:
        return i - 1 if v == 2 and i >= 2 else (i + 1 if v == 0 and i <= 3 else i)
    return i - 1 if u == 2 and i >= 2 else (i + 1 if u == 0 and i <= 3 and hsh(x, y, s) < 160 else i)


def tex_veg(x, y, i, s):                            # smooth skin, soft gloss flecks + pores
    h = hsh(x, y, s)
    if h > 246 and i <= 3:
        return i + 1
    if h < 8 and i >= 2:
        return i - 1
    return i


def tex_fur(x, y, i, s):                            # tufts: short vertical strokes
    t = hsh(x, y // 3, s)
    if t < 70 and i >= 2:
        return i - 1
    if t > 200:
        return min(4, i + 1)
    return i


def tex_wood(x, y, i, s):                           # grain streaks + knots
    g = hsh(x, y // 5, s + 1)
    if i >= 2 and g < 40:
        return i - 1
    if g > 236 and i <= 3:
        return i + 1
    return i


def tex_dummy(x, y, i, s):
    return i


TEX = {'plain': tex_plain, 'metal': tex_metal, 'leather': tex_leather, 'cloth': tex_cloth, 'denim': tex_denim,
       'straw': tex_straw, 'veg': tex_veg, 'fur': tex_fur, 'wood': tex_wood, 'dummy': tex_dummy}
KIND_MAT = {'trim': 'plain', 'metal': 'metal', 'dummy': 'dummy', 'cloth': 'cloth', 'glow': 'none', 'raw': 'none',
            'wood': 'wood', 'leaf': 'veg', 'sap': 'none'}
STITCHED = {'leather', 'denim', 'canvas'}
TEX['canvas'] = tex_cloth
MATS = {}       # tuple(ramp) -> material, filled below


def mats(names, mat):
    for n in names:
        MATS[tuple(getattr(m, n))] = mat


MATS[tuple(m.GOLD)] = 'metal'
MATS[tuple(m.PANTS)] = 'cloth'
MATS[tuple(m.VINE)] = 'veg'
MATS[tuple(m.LEAF_GREEN)] = 'veg'
MATS[tuple(m.DUMMY)] = 'dummy'
for _t, _row in enumerate(m.TIERS):
    if _row[3] is None:
        continue
    MATS.setdefault(tuple(_row[3]), 'wood')
    MATS.setdefault(tuple(_row[4]), 'straw' if _t == 1 else 'wood')
    MATS.setdefault(tuple(_row[5]), 'veg')


# ================================================================ Goldenwood helmet (echo of the vanilla Mithril helmet)
def goldenwood_helmet(f, back):
    """winged helm carved from goldenwood: dome + gold brow band + cheek guards + nasal + crest;
    the wings are layered gold leaves (feathers), like the Mithril helmet's wings (UNVERIFIED)."""
    t = 7
    WD, LF = m.TIERS[t][3], m.TIERS[t][5]
    core = hx(m.TIERS[t][6][0])
    G = m.GOLD
    # clear the v1 crown (and its leaves) above the brow, then restore the head under it
    for y in range(-m.TOP, 20):
        for x in range(12, 52):
            if y > 8 and not 20 <= x <= 43:
                continue                    # below the brow: only the area the v1 hood covered
            if f.kind.get((x, y)) not in (None, 'dummy'):
                f.px[x, y] = (0, 0, 0, 0)
                f.kind.pop((x, y), None)
                f.meta.pop((x, y), None)
    head = rect(24, 0, 39, 17) | rect(23, 1, 40, 16) | rect(22, 3, 41, 14)
    neck = rect(27, 14, 36, 22)
    f.paint(clip(neck, y1=19), m.DUMMY, edge_ref=neck, kind='dummy')
    f.paint(head, m.DUMMY, kind='dummy')
    sides = (0, 1)
    # wings: three stacked gold-leaf feathers per side, lowest first
    feathers = ([(21, 4), (13, 3), (6, 5), (11, 7), (21, 8)],
                [(21, 1), (12, -2), (4, -3), (8, 1), (14, 3), (21, 5)],
                [(21, -2), (14, -6), (7, -8), (9, -5), (14, -2), (21, 2)])
    for side in sides:
        for k, pts in enumerate(feathers):
            fm = S(poly(pts), side)
            f.paint(fm, G, kind='trim')
            vein = {(x, y) for x, y in fm if (x, y + 1) in fm and (x, y - 1) in fm and (x, y + 2) not in fm}
            f.dots([(x, y, 1) for x, y in vein], WD)
    # dome of goldenwood with gold streaks
    # gorget / collar of goldenwood under the helm (where the v1 hood ended), gold rim
    gor = rect(20, 16, 43, 20)
    f.paint(gor, WD, pattern=m.bark(t, 94))
    f.trim(bottom_rim(gor, 2), gor, G)
    dome = ell(19, -7, 44, 18) & rect(18, -8, 45, 8)
    f.paint(dome, WD, pattern=m.bark(t, 97))
    # raised crest ridge (gold), brow band, cheek guards, nasal
    crest = poly([(30, 6), (30, -6), (31.5, -9), (33, -6), (33, 6)])
    f.paint(crest, G, kind='trim')
    f.paint(rect(19, 6, 44, 8), G, kind='trim')
    for side in sides:
        cg = S(poly([(19, 8), (25, 8), (25, 14), (23, 17), (19, 17)]), side)
        f.paint(cg, WD, pattern=m.bark(t, 96))
        f.trim(S(rect(19, 15, 25, 17), side) & cg, cg, G)
    if back:
        nape = rect(20, 8, 43, 18)
        f.paint(nape, WD, pattern=m.bark(t, 95))
        f.trim(bottom_rim(nape, 2), nape, G)
        f.glow(line([(31, -4), (31, 16)], 1), core, 0.8)
    else:
        f.paint(rect(31, 8, 32, 13), G, kind='trim')
        # gold-leaf gem on the brow (kept from v1) + small leaves where the wings meet the dome
        f.paint(poly([(31.5, 2), (34, 5), (31.5, 8), (29, 5)]), G)
        f.px[31, 5] = core
        f.px[32, 5] = hx('#fffbe6')
        f.kind[(31, 5)] = f.kind[(32, 5)] = 'sap'
    for side in sides:
        m.leaf(f, X(18, side) - (4 if side else 0), 2, LF, flip=bool(side), kind='trim')


_orig_cfg = m.cfg_for


def draw_v2(t, back=False):
    if t != 7:
        return m.draw_figure(t, back)
    m.cfg_for = lambda tt: dict(_orig_cfg(tt), hood=False)
    try:
        f = m.draw_figure(t, back)
    finally:
        m.cfg_for = _orig_cfg
    goldenwood_helmet(f, back)
    return f


def show(img):
    s = SHOW
    im = img.resize((img.width * s, img.height * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, m.BG)
    d = ImageDraw.Draw(base)
    k = K * s
    d.ellipse((14 * k, (79 + m.TOP) * k, 49 * k, (84 + m.TOP) * k - 1), fill=m.BG_SHADOW)
    base.alpha_composite(im)
    return base


def save(im, name):
    im = im.convert('RGB').quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def main():
    fronts, backs = [None], [None]
    for t in range(1, len(m.TIERS)):
        fronts.append(show(up2(draw_v2(t))))
        backs.append(show(up2(draw_v2(t, back=True))))
    fw, fh = fronts[1].size
    gap, top, labh = 18, 96, 54
    n = len(m.TIERS)
    sheet_w = n * fw + (n + 1) * gap
    sheet_h = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sheet_w, sheet_h), m.BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), 'SkyWynn Foraging Armor - v2 detail (cloud draft)', font=m.font(38), fill=m.INK, anchor='mt')
    d.text((sheet_w // 2, 60), 'the approved designs at 2x detail (128 x 168 per figure); only change: the Goldenwood helmet now '
           'echoes the vanilla Mithril helmet (winged helm, gold-leaf wings)', font=m.font(18), fill=(60, 64, 70, 255), anchor='mt')
    for i, (name, band, echo, WD, TR, LF, sap) in enumerate(m.TIERS):
        x = gap + i * (fw + gap)
        y = top
        y2 = top + fh + labh + gap
        if fronts[i] is None:
            d.rectangle((x, y, x + fw - 1, y2 + fh - 1), fill=(166, 171, 177, 255), outline=(140, 145, 151, 255), width=3)
            for k, ln in enumerate(['Tier 0', 'vanilla Wood', 'armor', '(Armor_Wood)', '', '(no new design)']):
                d.text((x + fw // 2, y + 170 + k * 34), ln, font=m.font(26 if k < 4 else 20),
                       fill=(110, 114, 120, 255), anchor='mt')
            d.text((x + fw // 2, y + fh + 6), 'Wood', font=m.font(26), fill=(110, 114, 120, 255), anchor='mt')
            d.text((x + fw // 2, y + fh + 34), band + '  (vanilla)', font=m.font(15), fill=(110, 114, 120, 255), anchor='mt')
            continue
        sheet.paste(fronts[i], (x, y))
        d.text((x + fw // 2, y + fh + 6), name + ('  (new helmet)' if i == 7 else ''), font=m.font(26), fill=m.INK, anchor='mt')
        d.text((x + fw // 2, y + fh + 34), f'{band}  echoes {echo}', font=m.font(15), fill=(60, 64, 70, 255), anchor='mt')
        for j, col in enumerate([WD[3], WD[2], WD[1], TR[2], hx(sap[0])]):
            d.rectangle((x + 8 + j * 18, y + 8, x + 22 + j * 18, y + 22), fill=col, outline=WD[0])
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), name + ' (back)', font=m.font(17), fill=(60, 64, 70, 255), anchor='mt')
    save(sheet, 'foraging-armor-sheet-v2.png')
    print('wrote foraging-armor-sheet-v2.png in', OUT)


if __name__ == '__main__':
    main()
