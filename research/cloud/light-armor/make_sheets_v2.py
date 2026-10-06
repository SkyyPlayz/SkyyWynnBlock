#!/usr/bin/env python3
"""SkyWynn Light Armor - v2 concept sheets (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/light-armor/make_sheets_v2.py
Writes the *-v2.png files next to this script. Deterministic: same code -> same bytes.
The v1 scripts (make_sheets.py, make_helmets.py) and their PNGs are left as they are;
this script only imports the v1 palettes and per-tier accent switches (cfg_for).

What is new in v2 (Skyy 2026-10-06: "a little Pixley ... at least the same pixel density
as Hytale's default, or double"):
  * the figure grid is 128 x 188 (v1: 64 x 84) - the approved v1 layout is redrawn at 2x
    (every v1 part keeps its place: v1 point (x, y) -> v2 (2x, 2y + DY));
  * a 7-step colour ramp per material (v1: 5) with soft top-left light, a 2-px bevel and
    a whole-part gradient instead of flat fills;
  * surface detail: leather grain + scuffs, finer diamond quilting with stitched seams,
    thread stitching along every leather edge, brushed metal with pits, 4-px domed rivets,
    bevelled buckles with prongs, belt holes, leaf veins, tassel creases + cut ends,
    boot laces + soles, glove fingers, bracer lacing;
  * every figure wears the chosen HALF-MASK COWL (Copper + Iron plain; Thorium .. Onyxium
    keep the half mask and add an echo of that metal's vanilla helmet; Mithril = wings).
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_sheets as ms  # noqa: E402  (palettes + cfg_for only)
from PIL import Image, ImageDraw  # noqa: E402

OUT = HERE
W, H, DY = 128, 192, 22      # figure grid; DY = headroom rows for crests / wings
SET_SCALE = 4                 # per-tier set images: 512 x 752 per figure
SHEET_SCALE = 3               # combined sheet: 384 x 564 per figure
CHEST_SCALE = 4               # chest close-ups (112 x 106 crop -> 448 x 424)
HELM_SCALE = 4                # helmet close-ups

hx = ms.hx


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (255,)


def ramp7(rp):
    """v1 5-step ramp -> [outline, 6 interior steps dark..highlight]"""
    o, d, m, l, h = rp
    return [o, d, mix(d, m, .5), m, mix(m, l, .5), l, h]


LEATHER = ramp7(ms.LEATHER)
LEATHER_IN = ramp7(ms.LEATHER_IN)
PANTS = ramp7(ms.PANTS)
STRAP = ramp7(ms.STRAP)
DUMMY = ramp7(ms.DUMMY)
GOLD = ramp7(ms.GOLD)
SOLE = ramp7(ms.ramp('#08070a', '#141216', '#1e1b21', '#29252c', '#363139'))
FACE = ramp7(ms.ramp('#1e1c1a', '#3a3632', '#524d46', '#6a645b', '#837c71'))   # mannequin face in the hood's shade
THREAD = hx('#6b6372')        # stitching on black leather
THREAD_DK = hx('#4a4450')
TAN = hx('#a87c50')           # stitching on brown straps
TIERS = [(n, b, ramp7(m)) for n, b, m in ms.TIERS]
GLOW = ms.GLOW
GLOW['Cobalt'] = hx('#d8e6ff')
GLOW['Thorium'] = hx('#e6ffd8')
BG, BG_SHADOW, INK = ms.BG, ms.BG_SHADOW, ms.INK


# ---------------------------------------------------------------- hashing (deterministic noise)
def hsh(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 982451653) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65536.0


# ---------------------------------------------------------------- masks (native v2 coords)
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)}


def _draw(fn):
    im = Image.new('1', (W, H), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(W) for y in range(H) if px[x, y]}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def poly(pts):
    return _draw(lambda d: d.polygon([tuple(p) for p in pts], fill=1))


def line(pts, w=1):
    return _draw(lambda d: d.line([tuple(p) for p in pts], fill=1, width=w))


# v1 coordinates -> v2 masks (keeps the approved v1 layout exactly, at 2x)
def R(x0, y0, x1, y1):
    return rect(2 * x0, 2 * y0 + DY, 2 * x1 + 1, 2 * y1 + 1 + DY)


def E(x0, y0, x1, y1):
    return ell(2 * x0, 2 * y0 + DY, 2 * x1 + 1, 2 * y1 + 1 + DY)


def pv(x, y):
    return (2 * x + 1, 2 * y + 1 + DY)


def P(pts):
    return poly([pv(x, y) for x, y in pts])


def Y(y):
    return 2 * y + DY


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def S(m, side):
    return m if side == 0 else mirror(m)


def MX(x, side):
    return x if side == 0 else W - 1 - x


def clip(m, y0=-999, y1=999, x0=-999, x1=999):
    return {(x, y) for x, y in m if y0 <= y <= y1 and x0 <= x <= x1}


def erode(m, k=1):
    for _ in range(k):
        m = {(x, y) for x, y in m if all(q in m for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}
    return m


def dil(m, k=1):
    out = set(m)
    for _ in range(k):
        out |= {(x + dx, y + dy) for x, y in out for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    return out


def ring(m, d):
    return erode(m, d) - erode(m, d + 1)


def bottom_rim(m, w):
    return {(x, y) for x, y in m if any((x, y + k) not in m for k in range(1, w + 1))}


def top_rim(m, w):
    return {(x, y) for x, y in m if any((x, y - k) not in m for k in range(1, w + 1))}


# ---------------------------------------------------------------- textures (adjust the light value L)
def grain(seed=0, amt=0.10):
    def f(x, y, L):
        h = hsh(x, y, seed)
        if h < 0.08:
            L -= amt * 1.5
        elif h > 0.955:
            L += amt
        return L + (hsh(x // 3, y // 3, seed + 5) - 0.5) * amt
    return f


def metal_tex(seed=0):
    def f(x, y, L):
        L += (hsh(0, y, seed) - 0.5) * 0.10           # brushed rows
        if hsh(x, y, seed + 3) < 0.035:
            L -= 0.2                                    # pits
        return L
    return f


def quilt(P=12, seed=0):
    """diamond quilting: dark seams on a P-px diagonal lattice, each diamond lit top-left"""
    g = grain(seed, 0.07)

    def f(x, y, L):
        u, v = (x + y) % P, (x - y) % P
        if u == 0 or v == 0:
            return -1 if (x // 2 + seed) % 3 else 0.62     # dark seam, every 3rd step a thread stitch
        if u in (1, 2):
            L += 0.26 if u == 1 else 0.14
        elif u >= P - 2:
            L -= 0.24
        if v >= P - 2:
            L += 0.08
        elif v in (1, 2):
            L -= 0.08
        if u == P // 2 and v == P // 2:
            L += 0.15                                   # soft shine in the middle of a diamond
        return g(x, y, L)
    return f


def grooves(*ys):
    def f(x, y, L):
        if y in ys:
            return -1
        if y - 1 in ys:
            return L + 0.25
        return L
    return f


def chain(*fs):
    def f(x, y, L):
        for g in fs:
            if g:
                L = g(x, y, L)
        return L
    return f


def facet(cx, light_left=True):
    """crystal / blade: left half lit, right half shaded"""
    def f(x, y, L):
        return L + (0.22 if (x < cx) == light_left else -0.18)
    return f


# ---------------------------------------------------------------- painter
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.px = self.im.load()
        self.kind = {}

    def put(self, x, y, c, kind=None):
        if 0 <= x < W and 0 <= y < H:
            self.px[x, y] = c
            if kind:
                self.kind[(x, y)] = kind

    def paint(self, mask, rp, kind='leather', tex=None, edge_ref=None, outline=True,
              base=0.5, grad=0.28, bevel=True):
        """Shade a part: 1-px dark outline, whole-part gradient lit top-left, 2-px bevel."""
        mask = {p for p in mask if 0 <= p[0] < W and 0 <= p[1] < H}
        if not mask:
            return mask
        ref = edge_ref if edge_ref is not None else mask
        edge = {(x, y) for x, y in mask
                if any(q not in ref for q in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)))}
        inner = mask - edge if outline else mask
        xs = [p[0] for p in mask]
        ys = [p[1] for p in mask]
        x0, y0 = min(xs), min(ys)
        w, h = max(1, max(xs) - x0), max(1, max(ys) - y0)

        def run(x, y, dx, dy):
            k = 1
            while k <= 2 and (x + dx * k, y + dy * k) in inner:
                k += 1
            return k

        for (x, y) in mask:
            if outline and (x, y) in edge:
                c = rp[0]
            else:
                L = base + grad * (1 - ((x - x0) / w + (y - y0) / h))
                if bevel:
                    t = min(run(x, y, 0, -1), run(x, y, -1, 0))
                    b = min(run(x, y, 0, 1), run(x, y, 1, 0))
                    L += {1: 0.28, 2: 0.12}.get(t, 0) - {1: 0.30, 2: 0.12}.get(b, 0)
                if tex:
                    L = tex(x, y, L)
                c = rp[0] if L <= -0.5 else rp[1 + max(0, min(5, int(round(L * 5))))]
            self.px[x, y] = c
            self.kind[(x, y)] = kind
        return mask

    def trim(self, rim, parent, rp, tex=None):
        """metal trim inside a part: outline only where the part itself ends"""
        return self.paint(rim, rp, kind='metal', edge_ref=parent, tex=tex or metal_tex(len(rim)))

    def metal(self, mask, rp, tex=None, **kw):
        return self.paint(mask, rp, kind='metal', tex=chain(metal_tex(len(mask) % 97), tex), **kw)

    def stamp(self, x, y, rows, rp, kind='metal'):
        """rows of ramp7 indices ('.' = skip)"""
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != '.':
                    self.put(x + dx, y + dy, rp[int(ch)], kind)

    def stitch(self, m, col, d=2, per=4, on=2, ys=None):
        for (x, y) in ring(m, d):
            if (x + y) % per < on and (ys is None or ys[0] <= y <= ys[1]):
                self.put(x, y, col)

    def scuffs(self, m, n, seed, col):
        """a few short diagonal scratches (wear) on leather"""
        pts = sorted(erode(m, 3))
        if not pts:
            return
        for k in range(n):
            x, y = pts[int(hsh(k, seed, 11) * len(pts))]
            ln = 2 + int(hsh(k, seed, 12) * 3)
            dx = 1 if hsh(k, seed, 13) < 0.5 else -1
            for j in range(ln):
                q = (x + j * dx, y + j)
                if q in m:
                    self.put(*q, col)


RIVET = [".00.",
         "0650",
         "0420",
         ".00."]
STUD = ["65",
        "31"]


def rivet(f, x, y, rp, small=False):
    if small:
        f.stamp(x, y, STUD, rp)
    else:
        f.stamp(x - 1, y - 1, RIVET, rp)


def buckle(f, x, y, rp, w=10, h=10):
    """bevelled square buckle frame (2 px) with a prong; (x, y) = top-left in v2 px"""
    outer = rect(x, y, x + w - 1, y + h - 1)
    hole = rect(x + 3, y + 3, x + w - 4, y + h - 4)
    f.metal(outer - hole, rp)
    cx = x + w // 2
    for yy in range(y + 2, y + h // 2 + 2):
        f.put(cx, yy, rp[5], 'metal')
        f.put(cx + 1, yy, rp[2], 'metal')
    f.put(cx, y + h // 2 + 2, rp[1], 'metal')


def leaf(f, x, y, rp, flip=False):
    """v1 5x5 leaf (tip up-right, stem down-left) redrawn at 2x with a vein; (x, y) in v1 coords"""
    pts = [(x + 0.0, y + 4.6), (x + 0.5, y + 2.4), (x + 2.2, y + 0.8), (x + 4.6, y + 0.0),
           (x + 4.0, y + 2.4), (x + 2.6, y + 3.9)]
    if flip:
        pts = [(2 * x + 4.6 - px, py) for px, py in pts]
    f.metal(P(pts), rp)
    a, b = pv(*pts[0]), pv(*pts[3])
    for k in range(1, 8):
        t = k / 8.0
        qx, qy = int(round(a[0] + (b[0] - a[0]) * t)), int(round(a[1] + (b[1] - a[1]) * t))
        f.put(qx, qy, rp[2], 'metal')
        if k in (3, 5):
            f.put(qx + (1 if not flip else -1), qy + 1, rp[6], 'metal')
    f.put(a[0], a[1] + 1, rp[0], 'metal')


def feather(r, t, w):
    """long leaf-shaped plate from root r to tip t (v2 px), width w"""
    dx, dy = t[0] - r[0], t[1] - r[1]
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    return poly([(r[0] + nx * w * .5, r[1] + ny * w * .5),
                 (r[0] + dx * .55 + nx * w, r[1] + dy * .55 + ny * w),
                 t,
                 (r[0] + dx * .6 - nx * w * .25, r[1] + dy * .6 - ny * w * .25),
                 (r[0] - nx * w * .5, r[1] - ny * w * .5)])


# ---------------------------------------------------------------- helmet: half-mask cowl + tier echo
HEAD = R(24, 0, 39, 17) | R(23, 1, 40, 16) | R(22, 3, 41, 14)


def cowl_masks():
    # soft hood: domed crown (round top), straight sides, wraps the neck, small flare onto the collar
    snug = (clip(ell(42, Y(-1), 85, Y(15)), y1=Y(7)) | rect(42, Y(7), 85, Y(21) + 1)
            | poly([(42, Y(17)), (85, Y(17)), (88, Y(22) + 1), (39, Y(22) + 1)]))
    eyes = R(24, 6, 39, 10) | R(25, 5, 38, 5)
    mask = P([(23, 11), (40, 11), (39, 18), (34, 21), (29, 21), (24, 18)])
    return snug, eyes, mask


def helmet(f, t, back):
    name, band, M = TIERS[t]
    onyx = t == 7
    rimc = GOLD if onyx else M
    snug, eyes, mask = cowl_masks()
    cx = 63.5

    # --- cowl (quilted black leather, centre seam with stitches)
    cowl = snug if back else snug - eyes
    f.paint(cowl, LEATHER, tex=quilt(8, 3), edge_ref=snug, grad=0.32)
    # hood folds: soft creases curving from the crown down the sides
    for side in (0, 1):
        for pts, lit in (([(54, Y(-1) + 2), (48, Y(4)), (45, Y(12))], 1), ([(50, Y(14)), (46, Y(20))], 1)):
            for (x, y) in S(line(pts, 1), side) & erode(snug, 2):
                f.put(x, y, LEATHER[0])
                f.put(x + (1 if side == 0 else -1), y, LEATHER[5])
    seam_y1 = Y(21) if back else Y(3)
    for y in range(Y(-1), seam_y1):
        if (y, 63) and (63, y) in snug:
            f.put(63, y, LEATHER[1])
            f.put(64, y, LEATHER[4])
            if y % 3 == 0:
                f.put(62, y, THREAD)
                f.put(65, y, THREAD)
    f.stitch(snug, THREAD_DK, d=2, per=3, on=1)
    f.scuffs(snug, 3, 40 + t, LEATHER[5])
    if back:
        # laced slit at the back of the neck: dark slit, metal eyelets, criss-cross laces
        for y in range(Y(12), Y(21)):
            f.put(63, y, LEATHER[0])
            f.put(64, y, LEATHER_IN[1])
        eys = list(range(Y(12) + 1, Y(21), 5))
        for a, b in zip(eys, eys[1:]):
            for (x, y) in line([(59, a), (68, b)], 1) | line([(68, a), (59, b)], 1):
                f.put(x, y, STRAP[4] if y < (a + b) / 2 else STRAP[2], 'leather')
        for y in eys:
            for x in (58, 68):
                f.stamp(x, y - 1, ["43", "21"], M)
    else:
        # eye band: the faceless mannequin in the hood's shade, deep shadow under the brow
        f.paint(eyes, FACE, kind='dummy', base=0.55, grad=0.2, outline=False, bevel=False)
        for (x, y) in eyes:
            if y <= Y(6) + 2:
                f.put(x, y, LEATHER_IN[1] if y <= Y(6) else FACE[1], 'dummy')
        # rolled leather rim round the face opening
        rim = (dil(eyes, 2) - eyes) & snug
        f.paint(rim, LEATHER, edge_ref=rim | eyes, base=0.62, grad=0.2, tex=grain(8, 0.06))
        # lower mask: leather plate over nose + mouth
        f.paint(mask, LEATHER, tex=grain(7, 0.08), grad=0.32)
        f.stitch(mask, THREAD, d=2, per=3, on=1)
        f.trim(top_rim(mask, 2), mask, M)
        for side in (0, 1):                               # breathing slits
            for k, y in enumerate((Y(14), Y(15) + 1, Y(17))):
                x0 = MX(51 + k, side) - (4 if side else 0)
                for x in range(x0, x0 + 5):
                    f.put(x, y, LEATHER[0])
                    f.put(x, y + 1, LEATHER[5])
            rivet(f, MX(49, side) - (1 if side else 0), Y(12), M)   # mask strap rivets
        # nose ridge (metal strip)
        ridge = rect(62, Y(10), 65, Y(17))
        f.metal(ridge, M)
        f.put(62, Y(17) + 1, M[0], 'metal')
        if onyx:
            f.trim(bottom_rim(mask, 2), mask, GOLD)

    # --- brow band (all tiers): runs round the head
    brow = R(22, 3, 41, 4) & dil(HEAD, 2)
    if t in (1, 2):
        f.trim(brow, snug, rimc)
        xs = (47, 63, 79) if t == 1 else (46, 54, 62, 70, 78)
        for x in xs:
            rivet(f, x, Y(3) + 2, M)
        if t == 2:                                        # iron: riveted cheek straps
            for side in (0, 1):
                st = S(rect(44, Y(5), 47, Y(16)), side)
                f.metal(st, M)
                for y in (Y(7), Y(12)):
                    rivet(f, MX(45, side) - (1 if side else 0), y, M, small=True)
        return

    if t == 3:   # Thorium: rounded heavy skullcap with a thick rim + ridge + round boss (echo, UNVERIFIED)
        dome = clip(ell(40, Y(-3), 87, Y(14)), y1=Y(4) + 1) & dil(HEAD, 3)
        f.metal(dome, M, grad=0.35)
        f.trim(rect(40, Y(3), 87, Y(5) + 1) & dil(HEAD, 3), dome | rect(40, Y(3), 87, Y(5) + 1), M)
        f.metal(rect(61, Y(-3) + 1, 66, Y(3)), M, base=0.62)
        for x in (45, 53, 74, 82):
            rivet(f, x, Y(4), M)
        if not back:
            boss = ell(58, Y(2), 69, Y(6) + 1)
            f.metal(boss, M, base=0.6)
            f.stamp(61, Y(3), ["66", "64"], M)
            for side in (0, 1):                          # rounded cheek guards
                cg = S(ell(39, Y(5), 48, Y(12)), side)
                f.metal(cg, M, grad=0.35)
                rivet(f, MX(43, side) - (1 if side else 0), Y(8), M)
        return

    if t == 4:   # Cobalt: angular - widow's-peak brow plate, swept temple fins, blade crest (echo, UNVERIFIED)
        for side in (0, 1):
            fin = S(P([(22, 9), (15, -4), (19, -2), (25, 4)]), side)
            f.metal(fin, M, tex=facet(MX(38, side), side == 0))
            fin2 = S(P([(22, 12), (17, 4), (24, 7)]), side)
            f.metal(fin2, M)
        crest = P([(30, 4), (31.5, -6), (33, 4)])
        f.metal(crest, M, tex=facet(64))
        if back:
            f.trim(R(22, 2, 41, 5) & dil(HEAD, 2), snug, M)
        else:
            plate = P([(22, 2), (41, 2), (41, 5), (34, 5), (31.5, 9), (29, 5), (22, 5)])
            f.metal(plate, M)
            f.put(63, Y(7), GLOW['Cobalt'], 'metal')
            f.put(64, Y(7), GLOW['Cobalt'], 'metal')
            for x in (47, 80):
                rivet(f, x, Y(3) + 2, M)
        return

    if t == 5:   # Adamantite: jagged band + crystal crown + cheek shards (echo, UNVERIFIED)
        spikes = [(24, 5), (27.5, 8), (31.5, 12), (35.5, 8), (39, 5)]
        if back:
            spikes = [(24, 5), (27.5, 7), (31.5, 9), (35.5, 7), (39, 5)]
        for k, (sx, hgt) in enumerate(spikes):
            sp = P([(sx - 1.8, 4), (sx - 0.4, 3 - hgt), (sx + 0.4, 3 - hgt + 1), (sx + 1.8, 4)])
            f.metal(sp, M, tex=facet(2 * sx + 1))
            if k == 2 and not back:
                f.put(int(2 * sx), Y(3 - hgt) + 4, GLOW['Adamantite'], 'metal')
        band = R(22, 3, 41, 5) & dil(HEAD, 2)
        band = band - {(x, Y(5) + 1) for x in range(W) if (x // 3) % 2}
        f.trim(band, snug, M)
        if not back:
            for side in (0, 1):
                sh = S(P([(22, 8), (25, 9), (23.5, 17)]), side)
                f.metal(sh, M, tex=facet(MX(47, side), side == 0))
            f.trim(bottom_rim(mask, 2), mask, M)
        return

    if t == 6:   # Mithril: circlet + leaf gem + swept feathered WINGS at the temples (Skyy: same wings as vanilla Mithril; shape UNVERIFIED)
        for side in (0, 1):
            root = (44, Y(6))
            tips = [(14, Y(1)), (17, Y(-4)), (22, Y(-7)), (28, Y(-9))]
            widths = [6, 7, 7, 6]
            for k in range(4):
                tp = tips[k]
                fm = feather((root[0] + 1 + k, root[1] - k * 2), tp, widths[k])
                fm = S(fm, side)
                f.metal(fm, M, base=0.45 + 0.05 * k)
                # quill line
                r0 = (root[0] + 1 + k, root[1] - k * 2)
                for j in range(2, 12):
                    q = (int(round(r0[0] + (tp[0] - r0[0]) * j / 14)), int(round(r0[1] + (tp[1] - r0[1]) * j / 14)))
                    f.put(MX(q[0], side), q[1], M[6] if j % 4 else M[3], 'metal')
            hub = S(ell(40, Y(3), 49, Y(9) + 1), side)
            f.metal(hub, M, base=0.6)
            f.put(MX(43, side), Y(5), M[6], 'metal')
        circ = R(22, 3, 41, 4) & dil(HEAD, 2)
        f.trim(circ, snug, M)
        if not back:
            gem = P([(31.5, -1), (34, 3), (31.5, 7), (29, 3)])
            f.metal(gem, M, base=0.6)
            f.stamp(62, Y(1) + 1, ["66", "65"], M)
            f.put(63, Y(3), GLOW['Mithril'], 'metal')
            f.put(64, Y(3) + 1, GLOW['Mithril'], 'metal')
        return

    if t == 7:   # Onyxium: gold crown + glowing onyx + swept horns (echo, UNVERIFIED)
        for side in (0, 1):
            horn = S(P([(23, 7), (19.5, 2), (17, -3), (16.5, -7), (18.5, -3.5), (21.5, 0.5), (25, 4)]), side)
            f.metal(horn, M, tex=facet(MX(40, side), side == 0))
            tip = S(P([(16.5, -7), (17.6, -4.5), (16.2, -4.8)]), side)
            f.metal(tip, GOLD)
        for sx, hgt in ((26, 4), (31.5, 7), (37, 4)):
            pt = P([(sx - 2, 4), (sx, 3 - hgt), (sx + 2, 4)])
            f.metal(pt, GOLD, tex=facet(2 * sx + 1))
            f.put(int(2 * sx) + (1 if sx == 31.5 else 0), Y(3 - hgt) + 3, GLOW['Onyxium'], 'metal')
        band = R(22, 3, 41, 5) & dil(HEAD, 2)
        f.trim(band, snug, GOLD)
        for x in (47, 54, 73, 80):
            rivet(f, x, Y(4), M, small=True)
        if not back:
            gem = ell(58, Y(2) - 1, 69, Y(6))
            f.metal(gem, GOLD, base=0.6)
            f.metal(ell(60, Y(2) + 1, 67, Y(6) - 2), M, base=0.55)
            f.stamp(61, Y(2) + 2, ["66", "6"], M)
            f.put(64, Y(4), GLOW['Onyxium'], 'metal')
            f.put(65, Y(4), GLOW['Onyxium'], 'metal')
            f.put(64, Y(4) + 1, GLOW['Onyxium'], 'metal')
            f.metal(rect(62, Y(10), 65, Y(17)), GOLD)
        return


# ---------------------------------------------------------------- the figure (v1 layout at 2x)
def draw_figure(t, back=False, bust=False, helm=True):
    name, band, M = TIERS[t]
    c = ms.cfg_for(t)
    acc = M
    G = GOLD if c['gold'] else M
    f = Fig()
    sides = (0, 1)
    leather_g = grain(t, 0.10)

    # --- mannequin
    if not bust:
        for side in sides:
            f.paint(S(R(21, 48, 31, 81), side), DUMMY, kind='dummy')
    for side in sides:
        f.paint(S(R(13, 22, 19, 58), side), DUMMY, kind='dummy')
    f.paint(R(27, 14, 36, 22), DUMMY, kind='dummy')
    if not bust and not helm:
        f.paint(HEAD, DUMMY, kind='dummy', grad=0.35)

    # --- side tassels (behind the legs, darker = farther away)
    if not bust:
        for side in sides:
            for x0, y1 in ((15, 59), (17, 61)):
                tm = S(R(x0, 47, x0 + 4, y1), side)
                f.paint(tm, LEATHER_IN, tex=grain(x0, 0.08))

    # --- legs: trousers, knee guards, boots
    if not bust:
        for side in sides:
            leg = S(R(21, 48, 31, 72), side)
            f.paint(leg, PANTS, tex=chain(grain(5 + side, 0.08),
                                          lambda x, y, L: L - 0.25 if x in (MX(52, side),) else L))
            for y in range(Y(50), Y(72), 3):                       # outer seam stitches
                f.put(MX(45, side), y, THREAD_DK)
            km = S(E(21, 59, 31, 67), side)
            f.paint(km, LEATHER, tex=chain(leather_g, grooves(Y(63)) if c['knee'] is None else None), grad=0.35)
            f.stitch(km, THREAD, d=2, per=3, on=1)
            if c['knee'] and not back:
                kx = MX(53, side)
                if c['knee'] == 'cap':
                    f.trim(top_rim(km, 4), km, M)
                    rivet(f, kx - (1 if side else 0), Y(63) + 1, G)
                elif c['knee'] == 'point':
                    f.metal(S(P([(22, 63), (26, 56), (30, 63)]), side), M, tex=facet(MX(53, side), side == 0))
                elif c['knee'] == 'spike':
                    f.metal(S(P([(24, 61), (26, 53), (28, 61)]), side), M, tex=facet(MX(53, side), side == 0))
            bm = S(R(21, 72, 31, 82) | R(20, 77, 31, 82), side)
            f.paint(bm, LEATHER, tex=leather_g)
            sole = S(R(20, 81, 31, 82), side)
            f.paint(sole, SOLE, tex=lambda x, y, L: L - 0.3 if x % 3 == 0 and y == max(yy for _, yy in sole) else L)
            cuff = S(R(20, 70, 31, 74), side)
            f.paint(cuff, LEATHER_IN if back else LEATHER, tex=chain(leather_g, grooves(Y(72))), grad=0.4)
            f.stitch(cuff, THREAD, d=2, per=3, on=1)
            if not back:                                         # laces above the strap
                for k, y in enumerate(range(Y(75) - 5, Y(75) - 1, 2)):
                    for j in range(6):
                        x = MX(50 + j, side)
                        f.put(x, y + (j if k % 2 else 5 - j) // 3, STRAP[5 if j < 3 else 3])
            st = S(R(21, 76, 31, 78), side)
            f.paint(st, STRAP, tex=grain(9, 0.08), base=0.4, grad=0.15)
            f.stitch(st, TAN, d=1, per=4, on=1)
            if not back:
                buckle(f, MX(47, side) - (9 if side else 0), Y(75) + 1, acc)
            if c['toe'] and not back:
                f.trim(S(R(20, 80, 31, 81), side), bm, M)
            f.scuffs(bm, 3, 20 + side, LEATHER[5])

    # --- tassel skirt
    if not bust:
        xs = [19, 23, 27, 31, 35, 39] if not back else [17, 21, 25, 29, 33, 37, 41]
        for k, x0 in enumerate(xs):
            y1 = 64 if k % 2 == 0 else 61
            if back:
                y1 = 63 if k % 2 == 0 else 65
            tm = R(x0, 47, x0 + 4, y1)
            yb = Y(y1) + 1
            xa, xb = 2 * x0, 2 * x0 + 9
            tm -= {(xa, yb), (xb, yb), (xa, yb - 1), (xb, yb - 1), (xa + 4, yb), (xa + 5, yb)}   # cut end + notch
            cxs = xa + 6

            def tp(x, y, L, cxs=cxs):
                if x == cxs:
                    return -1
                if x == cxs - 1:
                    return L + 0.2
                return L
            f.paint(tm, LEATHER, tex=chain(leather_g, tp), grad=0.2)
            for y in range(Y(48), yb - 3, 3):
                f.put(xa + 2, y, THREAD_DK)
                f.put(xb - 2, y, THREAD_DK)
            tip = c['tassel']
            if tip == 'dot':
                rivet(f, xa + 4, yb - 5, M, small=True)
            elif tip == 'rivet':
                rivet(f, xa + 5, yb - 6, M)
            elif tip == 'cap':
                cap = rect(xa, yb - 4, xb, yb - 1) & tm | rect(xa, yb - 4, xb, yb - 2)
                f.trim(cap, cap, M)
                if c['gold']:
                    f.put(xa + 4, yb - 3, GOLD[5], 'metal')
                    f.put(xa + 5, yb - 3, GOLD[6], 'metal')
            elif tip == 'point':
                f.metal(poly([(xa, yb - 2), (xb, yb - 2), (xa + 4.5, yb + 6)]), M, tex=facet(xa + 5))

    # --- arms
    for side in sides:
        ua = S(R(13, 33, 19, 40), side)
        f.paint(ua, LEATHER, tex=chain(leather_g, grooves(Y(36), Y(38) + 1)))
        f.stitch(ua, THREAD, d=1, per=3, on=1, ys=(Y(33), Y(40) + 1))
        em = S(E(12, 39, 20, 46), side)
        if c['elbow'] == 'full':
            f.metal(em, M, grad=0.35)
            rivet(f, MX(32, side) - (1 if side else 0), Y(42) + 1, M)
        else:
            f.paint(em, LEATHER, tex=leather_g, grad=0.35)
            f.stitch(em, THREAD, d=2, per=3, on=1)
            if c['elbow'] in ('rim', 'fin', 'spike'):
                f.trim(top_rim(em, 3), em, M)
        if c['elbow'] == 'fin' and not back:
            f.metal(S(P([(12, 41), (8, 44), (12, 45)]), side), M)
        if c['elbow'] == 'spike':
            f.metal(S(P([(12, 41), (7.5, 43), (12, 45)]), side), M, tex=facet(0, True))
        br = S(P([(13, 46), (19, 46), (20, 53), (12, 53)]), side)
        f.paint(br, LEATHER, tex=chain(leather_g, grooves(Y(49), Y(51))))
        # bracer lacing on the inner side
        for y in range(Y(47), Y(53), 3):
            f.put(MX(36, side), y, STRAP[4])
            f.put(MX(37, side), y + 1, STRAP[3])
        if c['bracer'] >= 1:
            f.trim(top_rim(br, 3), br, G)
        if c['bracer'] >= 2:
            f.trim(bottom_rim(br, 3), br, M)
        if c['rivets']:
            for x in (29, 37):
                rivet(f, MX(x, side) - (1 if side else 0), Y(50) + 1, M)
        hg = S(R(13, 53, 19, 56), side)
        f.paint(hg, LEATHER, tex=chain(leather_g, grooves(Y(55))))
        fing = S(R(13, 56, 19, 58), side)
        f.paint(fing, DUMMY, kind='dummy',
                tex=lambda x, y, L: -1 if x in (29, 32, 35, 98, 95, 92) else L)
        rivet(f, MX(31, side) - (1 if side else 0), Y(54), acc)     # stud
        f.put(MX(28, side), Y(54) + 2, LEATHER[6])

    # --- chest piece
    torso = R(20, 21, 43, 48) | R(21, 20, 42, 21)
    f.paint(torso, LEATHER, tex=quilt(12, t), grad=0.25)
    for side in sides:
        sp = S(R(20, 23, 22, 48), side)
        f.paint(sp, LEATHER, edge_ref=torso, tex=chain(leather_g, grooves(Y(30), Y(37))))
        for y in range(Y(23), Y(40), 3):
            f.put(MX(45, side), y, THREAD)
    f.scuffs(torso, 6, 30 + t, LEATHER[6])

    if not back:
        if c['gorget']:
            g = (E(22, 14, 41, 31) - E(23, 9, 40, 27)) & R(22, 22, 41, 31)
            f.metal(g, M)
            for x in (48, 63, 78):
                rivet(f, x, Y(26) + 1, M, small=True)
        if c['chest'] == 'vtrim':
            for side in sides:
                f.metal(S(P([(22, 24), (25, 24), (32, 33), (31.5, 35)]), side), M)
        if c['chest'] == 'filigree':
            curve = [(23, 25), (24, 26), (25, 27), (25, 28), (24, 29), (24, 30), (24, 31), (25, 32), (26, 33),
                     (27, 34), (26, 35), (25, 36), (25, 37)]
            pts = [pv(x, y) for x, y in curve]
            for side in sides:
                lm = S(line(pts, 2), side)
                f.paint(lm, G, kind='metal', outline=False, base=0.75)
                for (x, y) in S(line([(p[0] + 2, p[1] + 1) for p in pts], 1), side):
                    f.put(x, y, G[0], 'metal')
                for k in (2, 7, 12):                           # small curl dots
                    q = pts[k]
                    f.put(MX(q[0] - 2, side), q[1], G[6], 'metal')
    elif t >= 6:
        f.trim(rect(62, Y(22), 65, Y(40)), torso, G)              # spine line on the back
        for y in range(Y(23), Y(40), 6):
            f.put(63, y, G[6], 'metal')

    # --- diagonal chest strap
    sp = P([(19, 25), (23, 21), (45, 40), (41, 43)])
    if back:
        sp = mirror(sp)
    f.paint(sp, STRAP, tex=chain(grain(11, 0.09),
                                  lambda x, y, L: L - 0.25 if (x - y if not back else x + y) % 9 == 0 else L),
            base=0.42, grad=0.2)
    f.stitch(sp, TAN, d=2, per=3, on=1)
    if not back:
        leaf(f, 23, 22, acc)
        m = c['medal']
        if m is None or m == 'ring':
            buckle(f, 58, Y(29), acc, w=11, h=11)
        elif m == 'plate':
            p = R(28, 28, 35, 34)
            f.metal(p, M)
            f.trim(ring(p, 1) | ring(p, 2), p, M)
            for x, y in ((59, Y(29) + 1), (69, Y(29) + 1), (59, Y(33) + 1), (69, Y(33) + 1)):
                rivet(f, x, y, M)
            f.metal(R(30, 30, 33, 32), M, base=0.4)
        elif m == 'boss':
            p = E(27, 26, 36, 35)
            f.metal(p, M, grad=0.4)
            f.paint(ring(p, 3), M, kind='metal', outline=False, base=0.2, bevel=False)
            for a in range(8):
                ang = a * math.pi / 4
                rivet(f, int(64 + 7 * math.cos(ang)), int(Y(30) + 2 + 7 * math.sin(ang)), M, small=True)
            f.metal(ell(60, Y(29), 67, Y(32) + 1), M, base=0.65)
            f.stamp(61, Y(29) + 1, ["66", "6"], M)
        elif m == 'rhombus':
            f.metal(P([(31.5, 24), (37, 31), (31.5, 38), (26, 31)]), M, tex=facet(64))
            f.metal(P([(31.5, 28), (34, 31), (31.5, 34), (29, 31)]), M, tex=facet(64, False))
            f.put(63, Y(30), GLOW['Cobalt'], 'metal')
        elif m == 'shard':
            f.metal(P([(31.5, 22), (35.5, 29), (33.5, 38), (29.5, 38), (27.5, 29)]), M, tex=facet(64))
            f.metal(P([(26, 31), (27.5, 27), (29, 32)]), M, tex=facet(56))
            f.metal(P([(37, 31), (35.5, 27), (34, 32)]), M, tex=facet(73))
            f.put(62, Y(28), GLOW['Adamantite'], 'metal')
            f.put(62, Y(28) + 1, GLOW['Adamantite'], 'metal')
        elif m == 'gem':
            f.metal(P([(31.5, 23), (36, 31), (31.5, 39), (27, 31)]), M, tex=facet(64))
            f.metal(E(29, 28, 34, 34), M, base=0.6)
            f.stamp(61, Y(28) + 3, ["66", "65"], M)
            f.put(63, Y(30) + 1, GLOW['Mithril'], 'metal')
            f.put(64, Y(30) + 1, GLOW['Mithril'], 'metal')
        elif m == 'onyx':
            f.metal(P([(31.5, 21), (34, 25), (31.5, 41), (29, 25)]), GOLD, tex=facet(64))
            setting = E(26, 25, 37, 37)
            f.metal(setting, GOLD)
            for a in range(12):
                ang = a * math.pi / 6
                f.put(int(64 + 10 * math.cos(ang)), int(Y(31) + 1 + 10 * math.sin(ang)), GOLD[6], 'metal')
            f.metal(E(28, 27, 35, 35), M, grad=0.4)
            f.stamp(58, Y(27) + 4, ["66.", "65", "5"], M)
            for p in ((66, Y(32)), (67, Y(32)), (66, Y(32) + 1), (65, Y(33))):
                f.put(*p, GLOW['Onyxium'], 'metal')

    # --- wide double waist belt with holes, buckles, pouch
    b1, b2 = R(19, 40, 44, 44), R(19, 44, 44, 48)
    f.paint(b1, STRAP, tex=chain(grain(13, 0.09), grooves(Y(42) + 1)), base=0.4, grad=0.2)
    f.paint(b2, STRAP, tex=chain(grain(14, 0.09), grooves(Y(46) + 1)), base=0.36, grad=0.2)
    f.stitch(b1, TAN, d=1, per=3, on=1)
    f.stitch(b2, TAN, d=1, per=3, on=1)
    for x in range(42, 54, 4):
        f.put(x, Y(41) + 1, STRAP[0])
        f.put(x, Y(41) + 2, STRAP[5])
    if not back:
        if c['beltplate']:
            bp = R(28, 40, 35, 44)
            f.metal(bp, G)
            f.trim(ring(bp, 1), bp, G)
            rivet(f, 59, Y(41) + 2, G)
            rivet(f, 69, Y(41) + 2, G)
            f.metal(R(30, 41, 33, 43), G, base=0.35)
        else:
            buckle(f, 58, Y(40), acc, w=11, h=10)
        buckle(f, 68, Y(44), acc, w=11, h=10)
        leaf(f, 21, 40, acc)
        pouch = R(37, 46, 44, 55)
        f.paint(pouch, STRAP, tex=grain(15, 0.1), grad=0.3, base=0.4)
        f.stitch(pouch, TAN, d=2, per=3, on=1)
        flap = R(37, 46, 44, 50) | R(39, 50, 42, 51)
        f.paint(flap, STRAP, base=0.52, grad=0.3, tex=grain(16, 0.08))
        f.stitch(flap, TAN, d=2, per=3, on=1)
        rivet(f, 81, Y(50) + 1, acc)
    else:
        for x in (49, 79):
            rivet(f, x, Y(42) + 1, acc)
            rivet(f, x, Y(46) + 1, acc)

    # --- raised stand-up collar
    tall = 2 if t >= 6 else 0
    f.paint(R(24, 18 - tall, 39, 24), LEATHER_IN, tex=grain(17, 0.06))
    for side in sides:
        flap = P([(20, 16 - tall), (30, 18 - tall), (30, 25), (20, 25)]) if not back else \
            P([(20, 16 - tall), (31, 18 - tall), (31, 25), (20, 25)])
        fm = S(flap, side)
        f.paint(fm, LEATHER, tex=chain(leather_g, grooves(Y(21) + 1)), grad=0.35)
        f.stitch(fm, THREAD, d=2, per=3, on=1)
        if c['collar']:
            f.trim(top_rim(fm, 2 * c['collar']), fm, G)
        if t == 4:
            f.metal(S(P([(19, 19), (20, 13), (23, 17)]), side), M, tex=facet(MX(41, side), side == 0))
        if t == 5:
            f.metal(S(P([(20, 18), (21, 12), (23, 17)]), side), M, tex=facet(MX(43, side), side == 0))
            f.metal(S(P([(24, 18), (25, 14), (27, 18)]), side), M, tex=facet(MX(51, side), side == 0))
        if not back:
            if t <= 1:
                leaf(f, 21, 19, acc, flip=bool(side)) if side == 0 else leaf(f, 38, 19, acc, flip=True)
            else:
                rivet(f, MX(57, side) - (1 if side else 0), Y(22) + 1, acc)

    # --- layered rounded shoulder caps (lowest plate first, top cap last)
    p3 = clip(E(12, 24, 20, 36), y0=Y(30))
    p2 = clip(E(11, 19, 22, 33), y0=Y(26))
    p1 = E(10, 18, 23, 29)
    for side in sides:
        for k, pm in ((3, p3), (2, p2), (1, p1)):
            pm = S(pm, side)
            f.paint(pm, LEATHER, tex=chain(leather_g, grooves(Y(23)) if k == 1 else None), grad=0.35)
            f.stitch(pm, THREAD, d=2, per=3, on=1)
            if k in c['rims']:
                if k == 1:
                    f.trim(bottom_rim(pm, 2 * c['rim_w']), pm, M)
                else:
                    f.paint(bottom_rim(pm, 4) - bottom_rim(pm, 2), M, kind='metal', outline=False,
                            tex=metal_tex(k))
        top = S(p1, side)
        f.scuffs(top, 2, 50 + side, LEATHER[6])
        if c['gold']:
            for (x, y) in bottom_rim(top, 8) - bottom_rim(top, 6):
                if (x + y) % 3 == 0:
                    f.put(x, y, GOLD[5], 'metal')
        if c['rivets']:
            for x in (27, 33, 39):
                rivet(f, MX(x, side) - (1 if side else 0), Y(27) + 1, M)
        if c['shoulder'] in ('thick', 'peak', 'flare', 'crown'):
            f.trim(top_rim(top, 4), top, M)
        if c['shoulder'] == 'peak':
            f.metal(S(P([(12, 21), (15, 11), (19, 19)]), side), M, tex=facet(MX(31, side), side == 0))
        elif c['shoulder'] == 'spikes':
            for sx, h in ((12, 5), (16, 9), (20, 5)):
                f.metal(S(P([(sx - 1.5, 20), (sx, 19 - h), (sx + 1.5, 20)]), side), M,
                        tex=facet(MX(2 * sx + 1, side), side == 0))
        elif c['shoulder'] == 'crown':
            for sx, h in ((12, 4), (16, 6), (20, 4)):
                f.metal(S(P([(sx - 1.5, 19), (sx, 19 - h), (sx + 1.5, 19)]), side), GOLD,
                        tex=facet(MX(2 * sx + 1, side), side == 0))
        if not back:
            if t <= 1:
                leaf(f, 14, 21, acc) if side == 0 else leaf(f, 45, 21, acc, flip=True)
            elif t in (6, 7):
                rivet(f, MX(33, side) - (1 if side else 0), Y(23) + 1, M)
                f.put(MX(33, side) - (1 if side else 0), Y(24), GLOW['Mithril' if t == 6 else 'Onyxium'], 'metal')

    if helm and not bust:
        helmet(f, t, back)
    return f


# ---------------------------------------------------------------- output
font = ms.font


def armor_share(f):
    k = list(f.kind.values())
    metal = k.count('metal')
    return metal, len(k) - k.count('dummy')


def scaled(f, s, bg=True):
    im = f.im.resize((W * s, H * s), Image.NEAREST)
    if not bg:
        return im
    base = Image.new('RGBA', im.size, BG)
    d = ImageDraw.Draw(base)
    d.ellipse((28 * s, (H - 12) * s, 99 * s, H * s - 1), fill=BG_SHADOW)
    base.alpha_composite(im)
    return base


def label(im, text, sub, n=24):
    pad = 52
    out = Image.new('RGBA', (im.width, im.height + pad), BG)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((im.width // 2, im.height + 4), text, font=font(n), fill=INK, anchor='mt')
    d.text((im.width // 2, im.height + 31), sub, font=font(15), fill=(60, 64, 70, 255), anchor='mt')
    return out


def save(im, name):
    im = im.convert('RGB').quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)
    return os.path.getsize(os.path.join(OUT, name))


HELM_NOTE = {1: 'plain cowl', 2: 'plain cowl + rivets', 3: 'echo: round skullcap',
             4: 'echo: angular fins', 5: 'echo: crystal crown', 6: 'echo: helmet wings',
             7: 'echo: crown + horns'}


def main():
    sizes = {}
    fronts, backs, report = [], [], []
    for t, (name, band, M) in enumerate(TIERS):
        if t == 0:
            continue   # tier 1 = vanilla leather armor, no new design (Skyy 2026-10-06)
        fr = draw_figure(t)
        bk = draw_figure(t, back=True)
        bu = draw_figure(t, bust=True)
        report.append((name,) + armor_share(fr))
        a, b = scaled(fr, SET_SCALE), scaled(bk, SET_SCALE)
        pair = Image.new('RGBA', (a.width * 2 + 16, a.height), BG)
        pair.paste(a, (0, 0))
        pair.paste(b, (a.width + 16, 0))
        d = ImageDraw.Draw(pair)
        d.text((10, 8), 'front', font=font(16), fill=INK)
        d.text((a.width + 26, 8), 'back', font=font(16), fill=INK)
        n1 = f'{name.lower()}-set-v2.png'
        sizes[n1] = save(label(pair, f'{name} Light Armor (v2)',
                               f'{band}  |  half-mask cowl: {HELM_NOTE[t]}  |  concept, cloud draft'), n1)
        crop = bu.im.crop((8, Y(9), 120, Y(62)))
        ch = crop.resize((crop.width * CHEST_SCALE, crop.height * CHEST_SCALE), Image.NEAREST)
        base = Image.new('RGBA', ch.size, BG)
        base.alpha_composite(ch)
        n2 = f'{name.lower()}-chest-v2.png'
        sizes[n2] = save(label(base, f'{name} Light Chest (v2)', f'{band}  |  front close-up'), n2)
        fronts.append(scaled(fr, SHEET_SCALE))
        backs.append(scaled(bk, SHEET_SCALE))

    # combined sheet: fronts on top, backs below
    fw, fh = fronts[0].size
    gap, top, labh = 16, 92, 54
    fronts.insert(0, None)
    backs.insert(0, None)
    sheet_w = len(TIERS) * fw + (len(TIERS) + 1) * gap
    sheet_h = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 16), 'SkyWynn Light Armor - v2 concept (cloud draft)', font=font(40), fill=INK, anchor='mt')
    d.text((sheet_w // 2, 62), '2x detail (128 x 192 figure grid, v1 was 64 x 84)  |  half-mask cowl on every tier  |  '
           'Thorium..Onyxium helmets echo the vanilla metal helmets (guesses, UNVERIFIED)',
           font=font(18), fill=(60, 64, 70, 255), anchor='mt')
    grey = (110, 114, 120, 255)
    for i, (name, band, M) in enumerate(TIERS):
        x = gap + i * (fw + gap)
        y = top
        if fronts[i] is None:
            y2 = top + fh + labh + gap
            d.rectangle((x, y, x + fw - 1, y2 + fh - 1), fill=(166, 171, 177, 255), outline=(140, 145, 151, 255), width=3)
            for k, ln in enumerate(['Tier 1', 'vanilla leather', 'armor', '', '(no new design)']):
                d.text((x + fw // 2, y + 200 + k * 34), ln, font=font(26 if k < 3 else 20), fill=grey, anchor='mt')
            d.text((x + fw // 2, y + fh + 6), 'Leather', font=font(26), fill=grey, anchor='mt')
            d.text((x + fw // 2, y + fh + 34), band + '  (vanilla)', font=font(15), fill=grey, anchor='mt')
            continue
        sheet.paste(fronts[i], (x, y))
        d.text((x + fw // 2, y + fh + 6), name, font=font(26), fill=INK, anchor='mt')
        d.text((x + fw // 2, y + fh + 34), f'{band}  (front)  |  {HELM_NOTE[i]}', font=font(15),
               fill=(60, 64, 70, 255), anchor='mt')
        for j, col in enumerate([M[5], M[3], M[1]]):
            d.rectangle((x + 8 + j * 18, y + 8, x + 22 + j * 18, y + 22), fill=col, outline=M[0])
        y2 = top + fh + labh + gap
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), name + ' (back)', font=font(18), fill=(60, 64, 70, 255), anchor='mt')
    sizes['light-armor-sheet-v2.png'] = save(sheet, 'light-armor-sheet-v2.png')

    # helmets-v2: head + shoulders, front and back, every tier
    cx0, cy0, cx1, cy1 = 4, 0, 124, Y(30)
    cw, chh = (cx1 - cx0) * HELM_SCALE, (cy1 - cy0) * HELM_SCALE
    left, gap, top, labh = 20, 16, 96, 56
    n = len(TIERS) - 1
    hw = left + n * (cw + gap)
    hh = top + 2 * (chh + labh) + gap
    hs = Image.new('RGBA', (hw, hh), BG)
    d = ImageDraw.Draw(hs)
    d.text((hw // 2, 16), 'SkyWynn Light Armor - half-mask cowl helmets v2 (cloud draft)', font=font(40), fill=INK, anchor='mt')
    d.text((hw // 2, 62), 'Copper + Iron: plain cowl  |  Thorium..Onyxium: same half mask + an echo of that metal\'s vanilla '
           'helmet (Mithril = the vanilla helmet wings)  |  echo shapes are guesses, UNVERIFIED',
           font=font(18), fill=(60, 64, 70, 255), anchor='mt')
    for i in range(1, len(TIERS)):
        name, band, M = TIERS[i]
        x = left + (i - 1) * (cw + gap)
        for r, back in enumerate((False, True)):
            f = draw_figure(i, back=back)
            im = f.im.crop((cx0, cy0, cx1, cy1)).resize((cw, chh), Image.NEAREST)
            cell = Image.new('RGBA', im.size, BG)
            cell.alpha_composite(im)
            y = top + r * (chh + labh)
            hs.paste(cell, (x, y))
            if r == 0:
                d.text((x + cw // 2, y + chh + 4), f'{name} - front', font=font(24), fill=INK, anchor='mt')
                d.text((x + cw // 2, y + chh + 32), HELM_NOTE[i], font=font(16), fill=(60, 64, 70, 255), anchor='mt')
            else:
                d.text((x + cw // 2, y + chh + 4), f'{name} - back', font=font(20), fill=(60, 64, 70, 255), anchor='mt')
    sizes['helmets-v2.png'] = save(hs, 'helmets-v2.png')

    for name, metal, armor in report:
        print(f'{name:11s} metal accents {metal:5d} px of {armor:5d} armor px = {100 * metal / armor:4.1f}%')
    tot = 0
    for k, v in sizes.items():
        tot += v
        print(f'{k:28s} {v // 1024:5d} KB')
    print(f'total v2 PNGs {tot // 1024} KB')


if __name__ == '__main__':
    main()
