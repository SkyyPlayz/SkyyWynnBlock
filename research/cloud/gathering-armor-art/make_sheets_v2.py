#!/usr/bin/env python3
"""SkyWynn Mining v2 + Farming v2-detail - concept sheets (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/gathering-armor-art/make_sheets_v2.py
Writes mining-sheet-v2.png and farming-sheet-v2-detail.png next to this script.
The v1 script (make_sheets.py) and its PNGs are not changed; this script
imports it (read only) for the painter, palettes and the approved designs.
Deterministic: same code -> same bytes.

Skyy's art review 2026-10-06 (docs/answered/gear.md, LOCKED):
- Mining starts at COPPER (no T0 Miner's Leather); Iron and up echo the
  vanilla metal armors' style (own silhouette per tier, not recolours);
  the lamp helmets stay (the lamp must REALLY light - SkyyAccessories
  Lantern code, see README).
- Farming crop armor look approved: unchanged, only more detail.
- Every sheet 2x-4x the detail of v1.

How the detail is made: each figure is designed on the v1 64 x 84 grid,
then rendered at 2x (128 x 168) by a ramp-aware upscaler (up2): EPX corner
smoothing, 1-px outlines on the fine grid (v1 outlines were 2 fine px),
a 1-px bevel per part (lit top-left), and material texture by part kind
(leather grain + stitching, cloth weave, metal rim light + brushed streaks
+ glints, fur tufts). Shown at x3 (v1 was 64-grid x5).
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

    def paint(self, mask, rp, pattern=None, outline=True, edge_ref=None, kind='cloth'):
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
KIND_MAT = {'trim': 'metal', 'metal': 'metal', 'dummy': 'dummy', 'cloth': 'cloth', 'glow': 'none', 'raw': 'none'}
STITCHED = {'leather', 'denim', 'canvas'}
TEX['canvas'] = tex_cloth
MATS = {}       # tuple(ramp) -> material, filled below


def mats(names, mat):
    for n in names:
        MATS[tuple(getattr(m, n))] = mat


mats(['LEATHER', 'LEATHER_IN', 'BROWN'], 'leather')
mats(['TROUSER', 'TROUSER_B', 'ONION_T'], 'denim')
mats(['CANVAS'], 'canvas')
mats(['SHIRT_M', 'LINEN', 'COTTON', 'BLUE_COT', 'SILK', 'SAGE', 'FIBRE', 'SCARF', 'SHALE', 'SAND'], 'cloth')
mats(['STRAW', 'WHEAT_C', 'ROPE'], 'straw')
mats(['CARROT', 'LEAF', 'CAULI', 'PUMPKIN', 'VINE', 'CHILLI', 'DRIED', 'BOLL', 'ONION', 'ONION_G', 'ALLIUM'], 'veg')
mats(['GOLD'] + [], 'metal')
for _r in m.METALS.values():
    MATS[tuple(_r)] = 'metal'
MATS[tuple(m.DUMMY)] = 'dummy'


def show(img, shadow=True):
    """fine-grid figure -> display image on the sheet background"""
    s = SHOW
    im = img.resize((img.width * s, img.height * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, m.BG)
    if shadow:
        d = ImageDraw.Draw(base)
        k = K * s
        d.ellipse((14 * k, (79 + m.TOP) * k, 49 * k, (84 + m.TOP) * k - 1), fill=m.BG_SHADOW)
    base.alpha_composite(im)
    return base


def save(im, name):
    im = im.convert('RGB').quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def make_sheet(title, note, tiers, draw, swatch, fname, top_rows):
    m.TOP = top_rows
    fronts = [show(up2(draw(i))) for i in range(len(tiers))]
    backs = [show(up2(draw(i, back=True))) for i in range(len(tiers))]
    fw, fh = fronts[0].size
    gap, top, labh = 18, 96, 54
    n = len(tiers)
    sheet_w = n * fw + (n + 1) * gap
    sheet_h = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sheet_w, sheet_h), m.BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), title, font=m.font(38), fill=m.INK, anchor='mt')
    d.text((sheet_w // 2, 60), note, font=m.font(18), fill=(60, 64, 70, 255), anchor='mt')
    for i, row in enumerate(tiers):
        x = gap + i * (fw + gap)
        sheet.paste(fronts[i], (x, top))
        d.text((x + fw // 2, top + fh + 6), row[0], font=m.font(24), fill=m.INK, anchor='mt')
        d.text((x + fw // 2, top + fh + 33), row[1] + '  (front)', font=m.font(15), fill=(60, 64, 70, 255), anchor='mt')
        for j, col in enumerate(swatch(i)):
            d.rectangle((x + 8 + j * 18, top + 8, x + 22 + j * 18, top + 22), fill=col, outline=(30, 30, 34, 255))
        y2 = top + fh + labh + gap
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), row[0] + ' (back)', font=m.font(17), fill=(60, 64, 70, 255), anchor='mt')
    save(sheet, fname)
    return sheet


# ================================================================ FARMING v2-detail (design unchanged)
def farming():
    def sw_c(i):
        L = m.CROP_LOOK[m.CROPS[i][0]]
        return [L['c'][3], L['c'][2], L['c'][1], L['a'][2], L['shirt'][3]]
    tiers = [(f'T{r[0]} {r[1]}', r[2]) for r in m.CROPS]
    make_sheet('SkyWynn Farming Armor (crop armor) - v2 detail (cloud draft)',
               'the approved crop-armor look, unchanged - drawn at 2x detail (128 x 168 per figure): weave, stitching, bevels, texture',
               tiers, m.draw_crop_farmer, sw_c, 'farming-sheet-v2-detail.png', 8)


# ================================================================ MINING v2 (Copper first; Iron+ echo the vanilla metal armors)
FUR = ramp('#4a4a52', '#a4a8b2', '#c8ccd4', '#e4e6ec', '#ffffff')          # Cobalt: frost fur
SHADOW = ramp('#0a0c18', '#1c2038', '#262c4a', '#323a5e', '#444e78')       # Cobalt: shadoweave cloak
CINDER = ramp('#1a0604', '#4a1208', '#6e1e0c', '#962e12', '#c44a1a')       # Adamantite: cindercloth
STORM = ramp('#0e141c', '#24303e', '#303e50', '#3e4e64', '#56687e')        # Mithril: storm leather
ONYX = ramp('#07040c', '#170e22', '#221532', '#2f1e44', '#432c5c')         # Onyxium: onyx cloth / plate base
CRYSTAL = ramp('#2a0f40', '#6a2aa0', '#9a4ad8', '#c88af0', '#f4dcff')      # Onyxium crystals
VENOM = ramp('#0e2a10', '#2e7a22', '#4cb83a', '#86e85a', '#d4ffb0')        # Thorium: venom vial
EMBER = hx('#ff8a2a')
mats([], 'cloth')
for _r, _m in ((FUR, 'fur'), (SHADOW, 'cloth'), (CINDER, 'cloth'), (STORM, 'leather'), (ONYX, 'leather'),
               (CRYSTAL, 'metal'), (VENOM, 'veg')):
    MATS[tuple(_r)] = _m

MINING2 = [  # name, band, metal, lamp (colour, strength), vanilla echo (UNVERIFIED guess)
    ('Copper Miner', 'Lv 10-18', 'Copper', ('#ffd27a', 0.45), 'the approved v1 Copper Miner'),
    ('Iron Miner', 'Lv 15-23', 'Iron', ('#ffe49a', 0.55), 'knight plate: kettle hat, mail, lames'),
    ('Thorium Miner', 'Lv 20-28', 'Thorium', ('#fff2b4', 0.70), 'desert: cone helm, scales, wraps'),
    ('Cobalt Miner', 'Lv 25-38', 'Cobalt', ('#d8ecff', 0.80), 'frost: angular plate, fur, goggles'),
    ('Adamantite Miner', 'Lv 35-43', 'Adamantite', ('#fff0c8', 0.90), 'heavy: horned great-helm, spikes'),
    ('Mithril Miner', 'Lv 40-49', 'Mithril', ('#e6ffff', 1.0), 'winged helm, feather lames, cape'),
    ('Onyxium Miner', 'Lv 40-49 (50+ later)', 'Onyxium', ('#ff8af2', 1.0), 'onyx + gold, crystal crown'),
]


def mail(x, y, i):
    """chain mail rings"""
    if i == 0:
        return 0
    if (x + y) % 2 == 1:
        return 1
    return 3 if (x // 2 + y // 2) % 2 == 0 and i >= 2 else 2


def scales(x, y, i):
    """thorium lamellar scales: rows 3 high, 4 wide, offset"""
    if i == 0:
        return 0
    r = y // 3
    u = (x + (r % 2) * 2) % 4
    v = y % 3
    if v == 2:
        return 1
    if u == 3:
        return 1
    if u == 0 and v == 0:
        return 4 if i >= 2 else 3
    return 3 if v == 0 else 2


def chevrons(x, y, i):
    if i in (2, 3, 4) and int(y - abs(x - 31.5) * 0.6) % 5 == 0:
        return 1
    return i


def folds(x, y, i):
    if i == 0:
        return 0
    k = (x + y // 7) % 5
    return 1 if k == 0 else (3 if k == 1 and i >= 2 else i)


def arcs(x, y, i):
    """engraved mithril arcs"""
    if i in (2, 3) and int(((x - 31.5) ** 2) / 14 + y) % 6 == 0:
        return 3 if i == 2 else 4
    return i


def gpx(f, x, y, col):
    """raw pixel (glow / ember): set without a ramp"""
    if 0 <= x < m.W and -m.TOP <= y < m.H:
        f._px[x, y + m.TOP] = col
        f.kind[(x, y)] = 'glow'
        f.meta.pop((x, y), None)


def lamp(f, lx, ly, col_s, st, housing):
    col = hx(col_s)
    f.paint(ell(lx - 3, ly - 3, lx + 4, ly + 4), housing, kind='trim')
    for (x, y) in ell(lx - 2, ly - 2, lx + 3, ly + 3):
        gpx(f, x, y, mix(hx('#5a5040'), col, 0.45 + 0.55 * st))
    gpx(f, lx - 1, ly - 1, hx('#ffffff'))
    gpx(f, lx, ly - 1, mix(col, hx('#ffffff'), 0.6))
    rr = 3 + int(st * 4)
    for y in range(ly - rr - 2, ly + rr + 3):
        for x in range(lx - rr - 2, lx + rr + 3):
            d2 = (x - lx - 0.5) ** 2 + (y - ly - 0.5) ** 2
            if 3.5 ** 2 < d2 <= (rr + 2) ** 2 and -m.TOP <= y < m.H and 0 <= x < m.W:
                a = st * 0.55 * (1 - (d2 ** 0.5 - 3.5) / (rr - 1.5))
                if a <= 0:
                    continue
                if (x, y) in f.kind:
                    gpx(f, x, y, mix(f.get(x, y), col, a))
                else:
                    f._px[x, y + m.TOP] = col[:3] + (int(255 * a * 0.8),)
    if st >= 0.9:
        for k in range(3, 6):
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                x, y = lx + (dx * k if dx < 0 else dx * k + 1), ly + (dy * k if dy < 0 else dy * k + 1)
                if (x, y) not in f.kind and -m.TOP <= y < m.H:
                    f._px[x, y + m.TOP] = col[:3] + (int(255 * (1.2 - k * 0.18)),)


def side_rivet(f, x, y, side, M):
    m.rivet(f, X(x, side) - (1 if side else 0), y, M)


def draw_miner2(t, back=False):
    """t = 0 Copper ... 6 Onyxium"""
    name, band, mk, lp, echo = MINING2[t]
    if t == 0:
        f = m.draw_miner(1, back)          # the approved v1 Copper Miner, unchanged design
        return f
    M = m.METALS[mk]
    T = t + 1                               # metal tier number 2..7
    f = Fig2()
    m.mannequin(f, back)
    sides = (0, 1)
    L = m.LEATHER
    trous = {2: L, 3: m.SAND, 4: L, 5: L, 6: STORM, 7: ONYX}[T]
    sleeve = {2: m.SHIRT_M, 3: m.SAND, 4: SHADOW, 5: CINDER, 6: STORM, 7: ONYX}[T]
    cloak = {4: SHADOW, 6: STORM, 7: ONYX}.get(T)
    cl = None
    if cloak:
        cl = poly([(17, 20), (46, 20), (50, 74 if T != 4 else 68), (13, 74 if T != 4 else 68)])
        if not back:
            f.paint(cl, cloak, pattern=folds)
            f.trim(bottom_rim(cl, 2), cl, M if T != 7 else m.GOLD)

    # ---------------- legs
    for side in sides:
        if T == 3:      # baggy desert trousers
            f.paint(S(poly([(20, 48), (31, 48), (31, 71), (19, 71)]), side), trous, pattern=folds)
        else:
            f.paint(S(rect(21, 48, 31, 73), side), trous, pattern=m.banded(55))
        bm = S(rect(21, 73, 31, 82) | rect(20, 77, 31, 82), side)
        f.paint(bm, m.BROWN if T not in (6, 7) else (STORM if T == 6 else ONYX), pattern=m.banded(79))
        if T == 2:
            f.paint(S(rect(22, 65, 30, 74), side), M, pattern=m.banded(68, 71), kind='trim')     # greave
            f.paint(S(ell(21, 57, 31, 66), side), M, kind='trim')                               # knee cop
            f.paint(S(ell(23, 59, 29, 64), side), M, outline=False, kind='trim',
                    pattern=lambda x, y, i: 4 if (x + y) % 5 == 0 else 3)
            f.paint(S(rect(20, 76, 31, 82), side), M, pattern=m.banded(78, 80), kind='trim')    # sabaton lames
        if T == 3:
            f.paint(S(rect(20, 64, 31, 73), side), m.SAND, pattern=m.wrap_pat)
            f.paint(S(poly([(26, 56), (30, 60), (26, 65), (22, 60)]), side), M, pattern=scales, kind='trim')
            f.trim(S(rect(20, 80, 31, 82), side), bm, M)
        if T == 4:
            f.paint(S(rect(19, 66, 32, 71), side), FUR)                                          # fur boot cuff
            f.paint(S(rect(20, 71, 31, 82) | rect(19, 77, 32, 82), side), m.BROWN, pattern=m.banded(79))
            f.paint(S(poly([(21, 56), (31, 56), (30, 63), (26, 66), (22, 63)]), side), M, pattern=chevrons, kind='trim')
            f.trim(S(rect(19, 80, 32, 82), side), bm, M)
        if T == 5:
            f.paint(S(rect(20, 62, 32, 76), side), M, pattern=m.banded(66, 70, 74), kind='trim')
            f.paint(S(ell(19, 55, 33, 67), side), M, kind='trim')
            f.paint(S(poly([(23, 58), (26, 49), (29, 58)]), side), M, kind='trim')                 # knee spike
            f.paint(S(poly([(19, 75), (32, 75), (32, 82), (17, 82), (17, 79)]), side), M,
                    pattern=m.banded(78), kind='trim')                                             # sabaton
            for y in (64, 68, 72):
                gpx(f, X(26, side), y, EMBER)
        if T == 6:
            f.paint(S(rect(22, 64, 30, 74), side), M, pattern=arcs, kind='trim')
            f.paint(S(ell(22, 57, 30, 65), side), M, kind='trim')
            f.paint(S(poly([(21, 73), (15, 67), (17, 75), (21, 77)]), side), M, kind='trim')        # ankle wing fin
        if T == 7:
            g = S(rect(21, 63, 31, 75), side)
            f.paint(g, M, kind='trim')
            f.trim(S(rect(21, 63, 31, 64), side), g, m.GOLD)
            f.paint(S(poly([(26, 54), (29, 59), (26, 64), (23, 59)]), side), CRYSTAL, kind='trim')
            f.trim(S(rect(20, 80, 31, 82), side), bm, m.GOLD)

    # ---------------- arms
    for side in sides:
        f.paint(S(rect(13, 30, 19, 45), side), sleeve, pattern=m.banded(37) if T != 3 else folds)
        gl = S(poly([(13, 44), (19, 44), (20, 54), (12, 54)]), side)
        f.paint(gl, L, pattern=m.banded(48))
        if T == 2:
            f.paint(S(ell(12, 38, 20, 46), side), M, kind='trim')                                   # couter
            f.paint(S(rect(12, 46, 20, 53), side), M, pattern=m.banded(49), kind='trim')            # vambrace
            m.hands(f, side, M)
        elif T == 3:
            f.paint(S(rect(12, 45, 20, 52), side), m.SAND, pattern=m.wrap_pat)
            f.paint(S(rect(12, 47, 20, 49), side), M, kind='trim')
            m.hands(f, side, L)
        elif T == 4:
            f.paint(S(rect(11, 43, 21, 46), side), FUR)
            f.paint(S(rect(11, 46, 21, 57), side), M, pattern=m.banded(50, 54), kind='trim')
        elif T == 5:
            f.paint(S(poly([(12, 36), (19, 38), (14, 33)]), side), M, kind='trim')                 # elbow spike
            f.paint(S(rect(11, 43, 21, 57), side), M, pattern=m.banded(47, 51), kind='trim')
            for y in (53, 56):
                f.dots([(X(x, side), y, 4) for x in (12, 15, 18)], M)                               # knuckle studs
        elif T == 6:
            f.paint(S(poly([(13, 44), (19, 44), (21, 53), (12, 53)]), side), M, pattern=arcs, kind='trim')
            f.paint(S(poly([(12, 45), (8, 40), (10, 47), (12, 50)]), side), M, kind='trim')         # fin
            m.hands(f, side, STORM)
        elif T == 7:
            f.paint(S(rect(12, 44, 20, 54), side), M, kind='trim')
            f.trim(S(rect(12, 44, 20, 45), side) | S(rect(12, 51, 20, 52), side), S(rect(12, 44, 20, 54), side), m.GOLD)
            m.hands(f, side, ONYX)

    # ---------------- torso
    f.paint(rect(20, 21, 43, 48) | rect(21, 20, 42, 21), m.SHIRT_M, pattern=m.fine)
    if T == 2:
        f.paint(rect(20, 38, 43, 54), M, pattern=mail, kind='trim')                                 # hauberk skirt
        bp = poly([(21, 21), (42, 21), (43, 30), (41, 41), (22, 41), (20, 30)]) if not back else rect(20, 21, 43, 41)
        f.paint(bp, M, pattern=m.banded(36, 39), kind='trim')
        if not back:
            f.dots([(31, y, 4) for y in range(23, 35)] + [(32, y, 2) for y in range(23, 35)], M)    # centre ridge
            for x, y in ((23, 23), (39, 23), (23, 33), (39, 33)):
                m.rivet(f, x, y, M)
    elif T == 3:
        f.paint(rect(20, 21, 43, 46), M, pattern=scales, kind='trim')
        sash = poly([(19, 24), (23, 20), (45, 41), (41, 44)])
        if back:
            sash = mirror(sash)
        f.paint(sash, m.SAND, pattern=m.wrap_pat)
        f.paint(rect(19, 40, 44, 44), m.SAND, pattern=m.wrap_pat)
        if not back:
            f.paint(poly([(37, 44), (41, 44), (42, 58), (38, 56)]), m.SAND, pattern=folds)          # sash tail
    elif T == 4:
        cu = poly([(19, 21), (44, 21), (45, 31), (39, 46), (24, 46), (18, 31)])
        f.paint(cu, M, pattern=chevrons, kind='trim')
        if not back:
            f.paint(poly([(29, 30), (34, 30), (31.5, 40)]), M, kind='trim')
    elif T == 5:
        bp = poly([(19, 20), (44, 20), (46, 33), (42, 46), (21, 46), (17, 33)])
        f.paint(bp, M, pattern=m.banded(26, 31, 36, 41), kind='trim')
        f.dots([(31, y, 4) for y in range(21, 45)] + [(32, y, 1) for y in range(21, 45)], M)
        for x0, y0 in ((24, 28), (38, 33), (26, 38), (36, 24)):                                    # ember seams
            for k in range(3):
                gpx(f, x0 + k, y0 + (k % 2), EMBER)
        tab = rect(26, 46, 37, 64)
        f.paint(tab, CINDER, pattern=folds)
        f.trim(bottom_rim(tab, 2), tab, M)
        for x in range(27, 37, 3):
            gpx(f, x, 63, EMBER)
    elif T in (6, 7):
        bp = poly([(20, 21), (43, 21), (43, 34), (38, 45), (25, 45), (20, 34)])
        f.paint(bp, M, kind='trim')
        if T == 7:
            f.trim(bp - m.clip(bp, x0=22, x1=41, y0=23, y1=43), bp, m.GOLD)
            f.paint(rect(31, 23, 32, 43), m.GOLD, outline=False, kind='trim')
        if not back:
            gem = poly([(31.5, 25), (35, 29), (31.5, 34), (28, 29)])
            f.paint(gem, M if T == 6 else m.GOLD, kind='trim')
            for (x, y) in poly([(31.5, 27), (33, 29), (31.5, 32), (30, 29)]):
                gpx(f, x, y, mix(M[3] if T == 6 else CRYSTAL[3], hx(lp[0]), 0.5))
            gpx(f, 31, 28, hx('#ffffff'))

    # ---------------- tool belt (every tier), ore pouch, pick
    belt = rect(19, 44, 44, 48)
    f.paint(belt, m.BROWN if T != 7 else ONYX, pattern=m.banded(46))
    if not back:
        m.buckle(f, 29, 44, M if T != 7 else m.GOLD, w=6, h=5)
        f.paint(rect(37, 48, 44, 56), m.BROWN)
        f.paint(rect(37, 48, 44, 50), m.BROWN, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        f.dots([(40, 50, 3), (41, 50, 2)], M)
        f.paint(line([(22, 47), (22, 58)], 1), m.BROWN)
        f.paint(poly([(18, 48), (22, 46), (26, 48), (22, 49)]), M, kind='trim')
        if T == 3:          # venom vial on the belt
            f.paint(rect(34, 47, 36, 53), VENOM, kind='trim')
            gpx(f, 35, 50, hx('#c8ff9a'))

    # ---------------- cloak over the back
    if cloak and back:
        f.paint(cl, cloak, pattern=folds)
        f.trim(bottom_rim(cl, 2), cl, M if T != 7 else m.GOLD)
    if back:                # lamp battery clipped on the belt
        f.paint(rect(28, 41, 35, 49), m.BROWN)
        f.dots([(29, 42, 4), (30, 42, 3), (34, 48, 1)], m.BROWN)
        f.paint(rect(30, 43, 33, 44), M, kind='trim')
        f.paint(line([(31, 41), (31, 18)], 1), m.LEATHER)

    # ---------------- pauldrons
    for side in sides:
        if T == 2:
            for k, (e, y0) in enumerate(((ell(10, 19, 24, 30), None), (ell(10, 23, 23, 34), 29), (ell(11, 27, 22, 38), 33))):
                f.paint(S(clip(e, y0=y0) if y0 else e, side), M, kind='trim')
            side_rivet(f, 14, 22, side, M)
            side_rivet(f, 19, 22, side, M)
        elif T == 3:
            f.paint(S(poly([(12, 20), (22, 19), (24, 24), (21, 33), (12, 31), (10, 25)]), side), M,
                    pattern=scales, kind='trim')
        elif T == 4:
            pa = S(poly([(8, 19), (24, 18), (25, 29), (9, 32)]), side)
            f.paint(pa, M, pattern=chevrons, kind='trim')
            f.trim(S(rect(8, 18, 25, 20), side) & pa, pa, M)
        elif T == 5:
            f.paint(S(poly([(10, 19), (8, 8), (14, 17)]), side), M, kind='trim')
            f.paint(S(poly([(15, 17), (16, 6), (20, 17)]), side), M, kind='trim')
            f.paint(S(ell(6, 16, 25, 34), side), M, pattern=m.banded(22, 27), kind='trim')
            gpx(f, X(15, side), 25, EMBER)
        elif T == 6:
            for pts in ([(12, 20), (24, 19), (23, 25), (11, 27)], [(11, 25), (22, 24), (20, 30), (9, 32)],
                        [(10, 30), (19, 29), (17, 35), (8, 37)]):
                f.paint(S(poly(pts), side), M, kind='trim')
        elif T == 7:
            for cx, h in ((12, 9), (16, 12), (20, 8)):
                f.paint(S(poly([(cx - 2, 21), (cx, 21 - h), (cx + 2, 21)]), side), CRYSTAL, kind='trim')
            pa = S(ell(9, 18, 24, 31), side)
            f.paint(pa, M, kind='trim')
            f.trim(S(m.bottom_rim(ell(9, 18, 24, 31), 2), side), pa, m.GOLD)

    if T == 4 and not back:     # fur mantle over the shoulders
        f.paint(poly([(17, 18), (46, 18), (47, 24), (40, 27), (31.5, 29), (23, 27), (16, 24)]), FUR)
    elif T == 4:
        f.paint(rect(17, 18, 46, 24), FUR)
    elif T in (5, 6):
        f.paint(rect(24, 16, 39, 22), M, pattern=m.banded(19), kind='trim')                       # gorget
    elif T == 7:
        f.paint(rect(24, 16, 39, 22), m.GOLD, pattern=m.banded(19), kind='trim')

    # ---------------- helmets (each echoes its vanilla metal helmet - UNVERIFIED) + the lamp
    lx, ly = 31, -2
    if T == 2:      # mail coif + kettle hat
        coif = rect(21, 4, 42, 22)
        if not back:
            coif = coif - (ell(24, 4, 39, 21) & rect(24, 6, 39, 21))
        f.paint(coif, M, pattern=mail, kind='trim')
        f.paint(ell(21, -7, 42, 12) & rect(20, -8, 43, 3), M, pattern=m.banded(-1), kind='trim')
        f.paint(poly([(14, 7), (19, 3), (44, 3), (49, 7), (47, 9), (16, 9)]), M, kind='trim')
        for x in (23, 27, 36, 40):
            m.rivet(f, x, 1, M)
        lx, ly = 31, -2
    elif T == 3:    # turban-wrapped cone helm + havelock + face scarf
        if back:
            f.paint(poly([(20, 2), (43, 2), (46, 22), (17, 22)]), m.SAND, pattern=folds)
        else:
            for side in sides:
                f.paint(S(poly([(19, 4), (23, 4), (24, 20), (18, 22)]), side), m.SAND, pattern=folds)
            f.paint(rect(23, 12, 40, 19), m.SAND, pattern=m.banded(14, 17))
        cone = poly([(31.5, -12), (37, -5), (42, 2), (42, 5), (21, 5), (21, 2), (26, -5)])
        f.paint(cone, M, pattern=lambda x, y, i: 1 if i in (2, 3) and x in (26, 31, 37) else i, kind='trim')
        f.paint(rect(19, 1, 44, 6), m.SAND, pattern=m.wrap_pat)
        lx, ly = 31, -3
    elif T == 4:    # angular helm, fur ring, goggles
        helm = poly([(20, 7), (21, -1), (25, -6), (38, -6), (42, -1), (43, 7)])
        f.paint(helm, M, pattern=chevrons, kind='trim')
        f.paint(rect(30, -7, 33, 6), M, kind='trim')
        ring = (ell(19, 2, 44, 23) - ell(23, 6, 40, 21)) & rect(18, 4, 45, 21) if not back else poly([(20, 3), (43, 3), (46, 22), (17, 22)])
        f.paint(ring, FUR)
        if not back:
            f.paint(rect(24, 9, 39, 12), L)
            for gx in (25, 33):
                f.paint(ell(gx, 8, gx + 5, 13), M, kind='trim')
                for (x, y) in ell(gx + 1, 9, gx + 4, 12):
                    gpx(f, x, y, mix(M[3], hx('#9ad0ff'), 0.6))
                gpx(f, gx + 1, 9, hx('#ffffff'))
        lx, ly = 31, -1
    elif T == 5:    # closed horned great-helm, T slit
        for side in sides:
            f.paint(S(poly([(21, 1), (16, -2), (12, -8), (13, -12), (17, -6), (23, -3)]), side), ramp('#2a2420', '#6e6458', '#8e8476', '#b0a696', '#d6ccbc'), kind='trim')
        gh = poly([(20, -1), (24, -6), (39, -6), (43, -1), (44, 18), (19, 18)])
        f.paint(gh, M, pattern=m.banded(4, 14), kind='trim')
        f.paint(rect(30, -8, 33, -1), M, kind='trim')
        if not back:
            for (x, y) in rect(22, 7, 41, 8) | rect(30, 9, 33, 14):
                gpx(f, x, y, mix(hx('#140404'), EMBER, 0.35 if y > 8 else 0.15))
            f.dots([(x, 16, 1) for x in (24, 26, 37, 39)], M)
        lx, ly = 31, 1
    elif T == 6:    # winged helm (echo of the vanilla Mithril helmet, UNVERIFIED)
        feathers = ([(21, 4), (13, 3), (6, 5), (11, 7), (21, 8)],                        # lowest first
                    [(21, 1), (12, -2), (4, -3), (8, 1), (14, 3), (21, 5)],
                    [(21, -2), (14, -7), (6, -12), (9, -7), (14, -3), (21, 2)])
        for side in sides:
            for pts in feathers:
                fm = S(poly(pts), side)
                f.paint(fm, M, kind='trim')
                spine = {(x, y) for x, y in fm if (x, y + 1) in fm and (x, y - 1) in fm and (x, y + 2) not in fm}
                f.dots([(x, y, 4) for x, y in spine if (x, y) in fm], M)
        dome = ell(20, -6, 43, 16) & rect(19, -8, 44, 8)
        f.paint(dome, M, pattern=arcs, kind='trim')
        f.paint(rect(20, 6, 43, 8), M, kind='trim')
        for side in sides:
            f.paint(S(poly([(20, 8), (25, 8), (25, 15), (22, 18), (20, 17)]), side), M, kind='trim')
        if back:
            f.paint(rect(20, 8, 43, 18), M, pattern=m.banded(12, 15), kind='trim')
        else:
            f.paint(rect(31, 8, 32, 13), M, kind='trim')
        f.paint(poly([(30, 5), (30, -8), (31.5, -11), (33, -8), (33, 5)]), M, kind='trim')
        lx, ly = 31, 0
    elif T == 7:    # onyx crown helm with crystal points
        for cx, hgt in ((23, 5), (27, 8), (31.5, 11), (36, 8), (40, 5)):
            f.paint(poly([(cx - 2, 0), (cx, -hgt - 1), (cx + 2, 0)]), CRYSTAL, kind='trim')
        dome = ell(20, -5, 43, 14) & rect(19, -6, 44, 7)
        f.paint(dome, M, kind='trim')
        f.paint(rect(19, 4, 44, 7), m.GOLD, kind='trim')
        for side in sides:
            f.paint(S(poly([(20, 7), (24, 7), (25, 14), (22, 17), (20, 15)]), side), m.GOLD, kind='trim')
        if back:
            f.paint(rect(20, 7, 43, 17), M, kind='trim')
        lx, ly = 31, 0
    if not back:
        lamp(f, lx, ly, lp[0], lp[1], M if T >= 3 else m.BROWN)
    return f


def mining():
    def sw(i):
        name, band, mk, lp, echo = MINING2[i]
        Mr = m.METALS[mk]
        return [Mr[3], Mr[2], Mr[1], hx(lp[0])]
    tiers = [(f'T{i + 1} {r[0]}', r[1]) for i, r in enumerate(MINING2)]
    make_sheet('SkyWynn Mining Armor - v2 (cloud draft)',
               'starts at Copper; Iron and up each echo their vanilla metal armor (own silhouette); every lamp must REALLY light (Lantern code)',
               tiers, draw_miner2, sw, 'mining-sheet-v2.png', 12)


def main():
    which = sys.argv[1:] or ['mining', 'farming']
    if 'farming' in which:
        farming()
    if 'mining' in which:
        mining()
    print('wrote', ', '.join(which), 'in', OUT)


if __name__ == '__main__':
    main()
