#!/usr/bin/env python3
"""SkyyGear rarity tooltips + arrows + slot frames - "SKY WINDOW" (Isles of the Void), FINAL production textures, all ORIGINAL pixels.

Skyy 2026-10-10 picked approach 2 of art/ui-sky-mockups/sheet.png: "I like 2 the best. Of the themes". Earlier: "lighter softer look,
maybe like flowing clouds, with softer light glowy almost water color magic looking swirls and shapes ... for the rarities, you keep the
clody/ sky theme so some get more stormy, some get more sunny ... legendary could have blue lighting, mythic its night, and the clouds
open up to show a magical stary/ galactic scene bordered by clouds shining purple from the purple moon." (+ loved the menu emblem's glow
and sparkly water).

The look: a crisp bevelled gold frame (menu-emblem gold) with a soft glow halo in the rarity colour and a sky-gradient ribbon between two
gold lines; each corner holds a round gold-ringed WINDOW onto a tiny finished sky scene in the rarity mood (top: the sky object - sun /
storm / galaxy / moon / aurora; bottom: a floating isle with a sparkly waterfall over a cloud sea, like the menu emblem), a glowing gold
star point aimed out of every corner, small gold studs on the frame; a dark mood-tinted text panel (contrast >= 4.5:1 for every text
colour). Arrow = the gold frame folding down into a V with a glowing gem; slots = the gold frame around a soft mid-tone mood sky.

Writes art/tooltip-sky/:
  Common/UI/SkyyGear/Tooltips/Tooltip_<R>@2x.png        107 x 107   9-slice, border 48 px (= Border: 24 UI units), strip 48..58
  Common/UI/SkyyGear/Tooltips/Tooltip_<R>.png           54 x 54     1x twin, border 24 px, strip 24..29
  Common/UI/SkyyGear/Tooltips/Tooltip_<R>Arrow@2x.png   66 x 48     (+ 1x 33 x 24) never stretched
  Common/UI/SkyyGear/Slots/Slot_<R>@2x.png              148 x 148   (+ 1x 74 x 74) scaled whole
  sheet.png, manifest.json
Run:   python tools/art/make_tooltip_sky.py        (deterministic, pure Python 3, no Pillow, uses every CPU core, ~1 min)
Check: python tools/art/validate_tooltip_sky.py

9-SLICE RULES (client InGame/Tooltips/ItemTooltip.ui: Background (TexturePath, Border: 24); @2x file 107 px): the tooltip is drawn on a
108 px design canvas; in columns / rows 48..59 the shader is told "far from any corner" (coordinate = BIG), so every strip pixel depends
only on its depth from the edge; column + row 54 are then dropped -> 107 px with an 11 px strip. Corner art only inside the 48 px corner
patches; the edges carry only depth bands (gold lines, sky ribbon, panel glow), which stretch cleanly.
"""
import hashlib, json, math, os, random, struct, sys, zlib
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "art", "tooltip-sky")
TIP_DIR = "Common/UI/SkyyGear/Tooltips"
SLOT_DIR = "Common/UI/SkyyGear/Slots"
CAN = 108                     # tooltip design canvas (@2x px)
S0, S1 = 48, 60               # stretch strip on the canvas (48..59), column / row 54 dropped
BIG = 1.0e4
SS = 4                        # supersamples per axis
SLOT = 148
ARROW = (66, 48)
INSET, BOX_R = 6.0, 4.0       # gold frame box: inset from the canvas edge, corner radius
SOFT_MAX = 110                # soft alpha cap (halo / glow), like vanilla's shadow

# (id, Name, hex = SkyyGear RARITIES text colour, build_skyygear_0.2.20.py line ~1627, mood)
RARITIES = [("normal", "Normal", "#FFFFFF", "CLEAR DAY"), ("unique", "Unique", "#FFFF55", "GOLDEN SUN"),
            ("rare", "Rare", "#FF55FF", "PINK CLOUD DRIFT"), ("legendary", "Legendary", "#55FFFF", "SLATE STORM"),
            ("fabled", "Fabled", "#FF5555", "CRIMSON TEMPEST"), ("mythic", "Mythic", "#CC66CC", "STAR NIGHT"),
            ("set", "Set", "#55FF55", "GREEN DAWN"), ("untiered", "Untiered", "#FFAA00", "EMBER SUNSET")]

# sky0 zenith, sky1 horizon, cl / cs cloud lit / shade, glow = rarity glow, panel = text area (dark), grass / water / tree / rock
MOOD = {
    "normal":    dict(sky0=(92, 160, 230), sky1=(206, 234, 252), cl=(255, 255, 255), cs=(170, 194, 228), glow=(214, 236, 255),
                      panel=(18, 28, 54), sun=(255, 246, 204), grass=(104, 190, 86), water=(176, 228, 255), tree=(66, 150, 70)),
    "unique":    dict(sky0=(96, 158, 226), sky1=(255, 224, 146), cl=(255, 248, 226), cs=(228, 178, 112), glow=(255, 226, 92),
                      panel=(28, 26, 48), sun=(255, 220, 92), grass=(150, 198, 72), water=(196, 236, 255), tree=(214, 172, 52)),
    "rare":      dict(sky0=(148, 144, 228), sky1=(252, 200, 236), cl=(255, 242, 252), cs=(206, 150, 212), glow=(255, 128, 255),
                      panel=(34, 20, 54), sun=(255, 236, 246), grass=(112, 186, 116), water=(232, 200, 255), tree=(255, 150, 214)),
    "legendary": dict(sky0=(26, 40, 78), sky1=(84, 114, 160), cl=(166, 186, 218), cs=(52, 64, 98), glow=(85, 255, 255),
                      panel=(12, 28, 52), bolt=(196, 250, 255), grass=(66, 136, 112), water=(120, 240, 255), tree=(40, 84, 76)),
    "fabled":    dict(sky0=(44, 10, 24), sky1=(148, 50, 48), cl=(184, 98, 96), cs=(56, 14, 28), glow=(255, 85, 85),
                      panel=(40, 14, 26), bolt=(255, 214, 140), grass=(122, 94, 62), water=(255, 196, 176), tree=(110, 30, 34)),
    "mythic":    dict(sky0=(10, 6, 30), sky1=(56, 22, 96), cl=(132, 92, 178), cs=(34, 18, 64), glow=(214, 110, 255),
                      panel=(16, 9, 36), moon=(226, 168, 255), grass=(118, 80, 186), water=(220, 164, 255), tree=(236, 186, 255)),
    "set":       dict(sky0=(60, 106, 146), sky1=(226, 244, 180), cl=(242, 255, 234), cs=(136, 188, 158), glow=(85, 255, 85),
                      panel=(12, 36, 38), sun=(244, 255, 196), grass=(84, 214, 92), water=(170, 255, 214), tree=(52, 168, 84)),
    "untiered":  dict(sky0=(78, 28, 66), sky1=(255, 148, 64), cl=(255, 204, 152), cs=(158, 72, 68), glow=(255, 170, 0),
                      panel=(42, 20, 24), sun=(255, 130, 42), grass=(196, 120, 46), water=(255, 186, 90), tree=(230, 96, 30)),
}
GOLD_D, GOLD, GOLD_L, GOLD_W = (118, 74, 22), (222, 170, 52), (255, 234, 146), (255, 251, 224)
WHITE = (255, 255, 255)
LX, LY, LZ = -0.45, -0.70, 0.55                      # light from the upper left, toward the viewer
_l = math.sqrt(LX * LX + LY * LY + LZ * LZ); LX, LY, LZ = LX / _l, LY / _l, LZ / _l
ORI = {0: (1, 1), 1: (-1, 1), 2: (1, -1), 3: (-1, -1)}  # canvas direction of +a, +b per corner (a, b = depth from the canvas edges)
MED_C, RING_R, WIN_R = 21.0, 17.0, 13.6              # corner window: centre (a = b), ring outer radius, glass radius

# text colours the tooltip uses (Hytale / SkyyGear): white, grey, green, red, gold, aqua (+ the rarity colour)
TEXT = {"white": (255, 255, 255), "grey": (170, 170, 170), "green": (85, 255, 85), "red": (255, 85, 85), "gold": (255, 170, 0),
        "aqua": (85, 255, 255)}


# ---------------------------------------------------------------- maths
def clamp01(v): return 0.0 if v < 0 else 1.0 if v > 1 else v
def smooth(e0, e1, x):
    t = clamp01((x - e0) / (e1 - e0)); return t * t * (3 - 2 * t)
def mix(a, b, t):
    t = clamp01(t); return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)
def mul(a, f): return (min(255, a[0] * f), min(255, a[1] * f), min(255, a[2] * f))
def add(a, b, f): return (min(255, a[0] + b[0] * f), min(255, a[1] + b[1] * f), min(255, a[2] + b[2] * f))
def hx(s):
    s = s.lstrip("#"); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def over(acc, col, al):
    """straight-alpha 'over' into acc = [r, g, b, a(0..1)]"""
    if al <= 0.002: return
    if al > 1: al = 1.0
    oa = al + acc[3] * (1 - al); k = acc[3] * (1 - al)
    acc[0] = (col[0] * al + acc[0] * k) / oa; acc[1] = (col[1] * al + acc[1] * k) / oa; acc[2] = (col[2] * al + acc[2] * k) / oa
    acc[3] = oa


_R = random.Random(20261010)
PERM = list(range(256)); _R.shuffle(PERM); PERM = PERM * 2
VAL = [_R.random() for _ in range(256)]
def h3(i, j, k=0): return VAL[PERM[(PERM[(PERM[i & 255] + j) & 255] + k) & 255]]


def vnoise(x, y):
    xi, yi = math.floor(x), math.floor(y); xf, yf = x - xi, y - yi; xi, yi = int(xi), int(yi)
    u = xf * xf * (3 - 2 * xf); v = yf * yf * (3 - 2 * yf)
    a = h3(xi, yi); b = h3(xi + 1, yi); c = h3(xi, yi + 1); d = h3(xi + 1, yi + 1)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def fbm(x, y): return 0.5 * vnoise(x, y) + 0.3 * vnoise(2.03 * x + 5.2, 2.03 * y + 1.3) + 0.2 * vnoise(4.1 * x + 9.1, 4.1 * y + 3.7)


def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
    t = clamp01(((px - ax) * vx + (py - ay) * vy) / L2) if L2 else 0.0
    return math.hypot(px - (ax + vx * t), py - (ay + vy * t))


def poly_dist(px, py, pts):
    return min(seg_dist(px, py, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(len(pts) - 1))


def bevel(s, nx, ny, dark, light, spec=True):
    """tube shading: s in -1..1 across the tube, (nx, ny) = outward screen normal of the tube's outer side"""
    s = max(-1.0, min(1.0, s)); nz = math.sqrt(max(0.0, 1 - s * s))
    l = clamp01(0.28 + 0.92 * (s * nx * LX + s * ny * LY + nz * LZ))
    c = mix(dark, light, l)
    if spec and l > 0.9: c = mix(c, GOLD_W, (l - 0.9) * 6)
    return c


# ---------------------------------------------------------------- painted elements (local px, y down)
def sparkle(dx, dy, s):
    ax, ay = abs(dx), abs(dy)
    if ax > s or ay > s: return 0.0
    arm = max(math.exp(-ay * ay / 0.3) * (1 - ax / s) ** 1.5, math.exp(-ax * ax / 0.3) * (1 - ay / s) ** 1.5)
    return min(1.0, arm + math.exp(-(dx * dx + dy * dy) / 0.9))


def paint_sun(acc, dx, dy, r, col, rays=0, halo=1.0):
    d = math.hypot(dx, dy)
    over(acc, mix(col, WHITE, 0.35), 0.6 * halo * math.exp(-max(0.0, d - r) / (r * 0.75)))
    if rays and d > r * 0.9:
        ang = math.atan2(dy, dx)
        over(acc, mix(col, WHITE, 0.55), 0.5 * ((0.5 + 0.5 * math.cos(ang * rays)) ** 6) * math.exp(-(d - r) / (r * 1.4)))
    over(acc, mix(col, WHITE, 0.7 * clamp01(1 - d / r) ** 0.7), clamp01(r - d + 0.5))


def paint_moon(acc, dx, dy, r, col):
    d = math.hypot(dx, dy)
    over(acc, col, 0.62 * math.exp(-max(0.0, d - r) / (r * 0.8)))
    if d < r + 0.5:
        c = mix(col, WHITE, 0.5 * clamp01(1 - math.hypot(dx + r * 0.3, dy + r * 0.3) / r))
        for cx, cy, cr in ((0.25, -0.1, 0.22), (-0.3, 0.35, 0.16), (0.1, 0.45, 0.12)):          # soft craters
            if math.hypot(dx - cx * r, dy - cy * r) < cr * r: c = mul(c, 0.86)
        sd = math.hypot(dx + r * 0.6, dy - r * 0.15)                                            # crescent shade
        c = mix(c, mul(col, 0.4), 0.75 * smooth(r * 0.95, r * 0.6, sd))
        over(acc, c, clamp01(r - d + 0.5))


def paint_bolt(acc, dx, dy, pts, col, glow, w=0.6, branch=None):
    dist = poly_dist(dx, dy, pts)
    if branch: dist2 = poly_dist(dx, dy, branch)
    else: dist2 = 99.0
    if min(dist, dist2) > 9: return
    over(acc, glow, 0.6 * math.exp(-min(dist, dist2 + 0.8) / 2.0))
    over(acc, mix(col, WHITE, 0.55), clamp01(w + 0.5 - dist))
    over(acc, mix(col, WHITE, 0.3), clamp01(w * 0.55 + 0.5 - dist2))


def stars(x, y, cell=3.2, dens=0.5):
    i, j = int(math.floor(x / cell)), int(math.floor(y / cell))
    h = h3(i + 311, j + 97, 5)
    if h > dens: return 0.0
    sx = (i + 0.2 + 0.6 * h3(i, j, 1)) * cell; sy = (j + 0.2 + 0.6 * h3(i, j, 2)) * cell
    br = 0.4 + 0.6 * h3(i, j, 3)
    d2 = (x - sx) ** 2 + (y - sy) ** 2
    s = br * math.exp(-d2 / 0.3)
    if br > 0.86: s = max(s, sparkle(x - sx, y - sy, 2.2) * br)
    return s


def galaxy(x, y, with_stars=True):
    """night sky + soft nebula + stars"""
    n = fbm(x * 0.11 + 3.1, y * 0.11 + 7.7)
    m = fbm(x * 0.06 + 11.0, y * 0.06 + 2.0)
    c = mix((12, 6, 34), (66, 22, 116), smooth(0.35, 0.8, n))
    c = mix(c, (38, 66, 168), 0.5 * smooth(0.5, 0.85, m))
    c = mix(c, (255, 140, 240), 0.22 * smooth(0.62, 0.9, n))
    return mix(c, (255, 244, 255), stars(x, y)) if with_stars else c


def galaxy_swirl(acc, dx, dy, R):
    """a little spiral galaxy (2 arms) with a bright core"""
    r = math.hypot(dx, dy) + 1e-6
    if r > R * 1.25: return
    th = math.atan2(dy, dx)
    arm = (0.5 + 0.5 * math.cos(2 * th - 4.2 * math.log(r / R + 0.1))) ** 4
    fade = math.exp(-r / (R * 0.5))
    over(acc, mix((150, 70, 230), (255, 170, 245), arm), 0.95 * arm * fade)
    over(acc, (120, 150, 255), 0.25 * fade)
    over(acc, mix((255, 230, 255), WHITE, 0.5), clamp01(1.2 * math.exp(-r * r / (R * R * 0.05))))


def puff_cloud(acc, lx, ly, puffs, cl, cs, rim=None, rimk=0.0, alpha=1.0, glow=None):
    """a soft cloud made of round puffs (back to front), lit from the upper left; rim = coloured edge light"""
    for (px, py, r) in puffs:
        dd = math.hypot(lx - px, ly - py)
        if dd > r + 0.8: continue
        nx, ny = (lx - px) / r, (ly - py) / r
        nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        l = clamp01(0.42 + 0.7 * (nx * LX + ny * LY + nz * LZ))
        c = mix(cs, cl, l)
        if rim is not None: c = add(c, rim, rimk * (1 - nz) ** 1.6 * (0.2 + 0.8 * clamp01(-ny * 1.3 + 0.1)))   # lit from above
        if glow is not None: c = add(c, glow[0], glow[1] * nz)
        over(acc, c, alpha * clamp01((r - dd) * 1.4 + 0.45))


def cloud_sea(acc, lx, ly, top, cl, cs, seed, rim=None, rimk=0.0, alpha=1.0):
    """a rolling cloud sea: a row of round bumps over a flat bank (soft lit tops)"""
    e = top + 1.8
    for k in range(-4, 5):
        cx = k * 4.6 + 1.6 * h3(seed, k, 3); r = 2.6 + 1.4 * h3(seed, k, 4)
        q = r * r - (lx - cx) ** 2
        if q > 0: e = min(e, top + 1.8 - math.sqrt(q) + 1.2)
    if ly < e - 0.6: return
    depth = ly - e
    c = mix(cs, cl, clamp01(1 - depth / 5.5) ** 0.8)
    if rim is not None: c = add(c, rim, rimk * math.exp(-max(0.0, depth) / 1.3))
    over(acc, c, alpha * clamp01(depth * 1.6 + 1.0))


def rain(acc, lx, ly, col, a=0.32):
    q = (lx * 0.45 + ly * 0.15) % 2.6
    if q < 0.45: over(acc, col, a * (1 - q / 0.45) * (0.6 + 0.4 * h3(int(lx * 0.45 + ly * 0.15), 7)))


def embers(acc, lx, ly, seed, n=6, R=12.0):
    for k in range(n):
        ex, ey = -R + 2 * R * h3(seed, k, 11), -R + 2 * R * h3(seed, k, 12)
        dd = math.hypot(lx - ex, ly - ey)
        if dd < 4:
            over(acc, (255, 120, 30), 0.45 * math.exp(-dd / 1.3))
            over(acc, mix((255, 150, 40), (255, 240, 150), h3(seed, k, 13)), clamp01(1.0 - dd * 1.2))


# ---------------------------------------------------------------- corner window scenes (local px from the window centre, y down)
def sky_bg(m, ly, night, ox=0.0, oy=0.0, lx=0.0):
    if night: return galaxy(lx + ox, ly + oy)
    return mix(m["sky0"], m["sky1"], (ly + WIN_R) / (2 * WIN_R))


def scene_top(rid, m, ci, lx, ly):
    acc = [0.0, 0.0, 0.0, 0.0]
    night = rid == "mythic"
    over(acc, sky_bg(m, ly, night, 40.0 * ci, 13.0 * ci, lx), 1.0)
    cl, cs = m["cl"], m["cs"]
    left = ci == 0
    if rid == "normal":
        if left:
            paint_sun(acc, lx + 3.5, ly + 3.5, 3.4, m["sun"])
            puff_cloud(acc, lx, ly, [(1.5, 4.0, 2.4), (4.5, 3.0, 2.8), (7.0, 4.4, 2.0)], cl, cs)
        else:
            puff_cloud(acc, lx, ly, [(-5.5, -3.5, 2.2), (-3.0, -4.2, 2.8), (-0.5, -3.4, 2.0)], cl, cs)
            puff_cloud(acc, lx, ly, [(1.0, 2.0, 2.2), (3.6, 1.0, 3.0), (6.2, 2.2, 2.1)], cl, cs)
            for (bx, by) in ((-3.0, 0.5), (-0.8, -0.6)):                         # two tiny birds
                ddx, ddy = lx - bx, ly - by
                if abs(ddx) < 1.3 and abs(ddy - abs(ddx) * 0.55 + 0.3) < 0.28: over(acc, (70, 92, 130), 0.9)
        cloud_sea(acc, lx, ly, 7.0, cl, cs, ci)
    elif rid == "unique":
        if left:
            paint_sun(acc, lx + 1.5, ly + 1.5, 4.2, m["sun"], rays=12, halo=1.3)
        else:
            ang = math.atan2(ly + 16, lx + 16); d = math.hypot(lx + 16, ly + 16)          # god rays from a sun off to the upper left
            over(acc, mix(m["sun"], WHITE, 0.5), 0.38 * (0.5 + 0.5 * math.cos(ang * 22)) ** 4 * clamp01(1 - (d - 8) / 26))
            puff_cloud(acc, lx, ly, [(-2.0, 1.5, 2.6), (1.2, 0.4, 3.3), (4.6, 1.6, 2.6)], cl, cs, rim=m["sun"], rimk=0.55)
        cloud_sea(acc, lx, ly, 7.2, cl, cs, ci, rim=m["sun"], rimk=0.35)
    elif rid == "rare":
        if left:
            paint_sun(acc, lx - 2.0, ly + 5.0, 3.0, m["sun"], halo=0.8)
            puff_cloud(acc, lx, ly, [(-6.0, -1.0, 3.0), (-2.6, -2.6, 3.6), (1.4, -1.6, 3.0), (4.6, 0.2, 2.4)], cl, cs, rim=m["glow"], rimk=0.25)
            puff_cloud(acc, lx, ly, [(-4.0, 3.2, 2.4), (-1.0, 2.6, 2.6)], cl, cs)
        else:
            puff_cloud(acc, lx, ly, [(-6.4, -3.8, 2.2), (-3.4, -4.6, 2.8), (-0.4, -3.6, 2.2)], cl, cs, rim=m["glow"], rimk=0.25)
            puff_cloud(acc, lx, ly, [(0.6, 1.2, 2.6), (3.6, 0.2, 3.0), (6.4, 1.4, 2.2)], cl, cs, rim=m["glow"], rimk=0.25)
            for k in range(5):                                                     # drifting petals
                px, py = -9 + 18 * h3(ci, k, 41), -9 + 16 * h3(ci, k, 42)
                dd = math.hypot((lx - px) * 1.4, ly - py)
                if dd < 0.9: over(acc, mix(m["tree"], WHITE, 0.3), clamp01((0.9 - dd) * 2))
        cloud_sea(acc, lx, ly, 7.4, cl, cs, ci, rim=m["glow"], rimk=0.2)
    elif rid in ("legendary", "fabled"):
        flash = m["glow"]
        if left:
            pts = [(-1.5, -1.0), (1.0, 2.0), (-0.6, 3.0), (2.0, 6.2), (0.6, 6.8), (2.8, 11.0)]
            br = [(1.0, 2.0), (4.0, 3.6), (5.2, 6.0)]
        else:
            pts = [(1.0, -1.0), (-1.4, 2.4), (0.4, 3.2), (-2.2, 6.6), (-0.8, 7.0), (-3.0, 11.0)]
            br = [(-1.4, 2.4), (-4.6, 4.2)]
        if rid == "fabled" and not left:                                           # tempest swirl band behind
            r = math.hypot(lx - 1, ly + 2); th = math.atan2(ly + 2, lx - 1)
            sw = (0.5 + 0.5 * math.sin(th * 2 + r * 0.7)) ** 2
            over(acc, mix(cs, cl, 0.35), 0.5 * sw * clamp01(1 - r / 13))
        if ly > -2: rain(acc, lx, ly, mix(cl, flash, 0.25), 0.3)
        paint_bolt(acc, lx, ly, pts, m["bolt"], flash, 0.62, br)
        puff_cloud(acc, lx, ly, [(-8, -6.0, 4.4), (-3.4, -7.0, 4.6), (1.6, -6.2, 4.4), (6.4, -6.8, 4.2),
                                 (-5.6, -2.8, 3.0), (-1.2, -2.4, 3.4), (3.6, -2.6, 3.0), (7.6, -3.4, 2.6)],
                   cl, cs, glow=(flash, 0.0), alpha=1.0)
        dd = math.hypot(lx - pts[0][0], ly - pts[0][1] + 1.0)                     # the cloud glows where the bolt leaves it
        over(acc, mix(flash, WHITE, 0.4), 0.55 * math.exp(-dd / 2.4))
        cloud_sea(acc, lx, ly, 8.4, mul(cl, 0.85), cs, ci, rim=flash, rimk=0.15)
    elif rid == "mythic":
        if left:
            galaxy_swirl(acc, lx + 0.5, ly + 0.5, 11.0)
            puff_cloud(acc, lx, ly, [(-10.0, 4.4, 2.4), (-7.8, 5.4, 2.8), (-5.2, 6.6, 2.6), (5.8, 6.4, 2.6), (8.2, 5.0, 2.6),
                                     (10.2, 3.8, 2.0)], cs, mul(cs, 0.7),
                       rim=m["moon"], rimk=1.6)
        else:
            paint_moon(acc, lx - 0.5, ly + 0.2, 5.2, m["moon"])
            puff_cloud(acc, lx, ly, [(-9.0, 4.0, 2.0), (-7.0, 5.0, 2.4), (-4.6, 6.0, 2.4), (4.2, 6.2, 2.4), (6.6, 5.0, 2.4),
                                     (8.8, 3.8, 1.9)], cs, mul(cs, 0.7),
                       rim=m["moon"], rimk=1.6)
        cloud_sea(acc, lx, ly, 8.6, cl, cs, ci, rim=m["moon"], rimk=0.7)
    elif rid == "set":
        if left:
            over(acc, mix(m["sun"], WHITE, 0.3), 0.45 * math.exp(-max(0.0, abs(ly - 6.0) - 0.5) / 2.2))   # dawn glow on the horizon
            paint_sun(acc, lx + 0.5, ly - 4.6, 3.6, m["sun"], halo=1.2)
            yy = -5.5 + 1.6 * math.sin(lx * 0.45)
            over(acc, mix((90, 255, 160), (120, 220, 255), (lx + 10) / 20), 0.5 * math.exp(-((ly - yy) ** 2) / 1.6))
        else:
            over(acc, (20, 54, 70), 0.55 * clamp01((4 - ly) / 10))
            for (y0, ph, amp, c) in ((-7.0, 0.0, 2.0, (90, 255, 150)), (-3.0, 1.7, 1.6, (110, 230, 255))):
                yy = y0 + amp * math.sin(lx * 0.5 + ph)
                if ly > yy - 0.6:
                    curtain = math.exp(-(ly - yy) / 3.2) * (0.65 + 0.35 * math.sin(lx * 2.1 + ph * 3))
                    over(acc, c, 0.75 * curtain * clamp01((ly - yy + 0.6) * 1.5))
            for k in range(4):
                px, py = -9 + 18 * h3(ci, k, 51), -10 + 8 * h3(ci, k, 52)
                s = sparkle(lx - px, ly - py, 1.6)
                if s > 0: over(acc, WHITE, s * 0.8)
        cloud_sea(acc, lx, ly, 7.8, cl, cs, ci, rim=m["sun"], rimk=0.25)
    elif rid == "untiered":
        if left:
            paint_sun(acc, lx + 1.0, ly - 5.8, 4.4, m["sun"], halo=1.4)
            for k in range(3):                                                      # soft sunset cloud wisps
                yy = -6.0 + 2.8 * k + 0.4 * math.sin(lx * 0.5 + k)
                x0, x1 = -11.0 + 2.5 * k, 5.0 - 2.0 * k
                wv = 0.85 * clamp01(1 - abs(ly - yy) / 0.9) * smooth(x0, x0 + 3, lx) * (1 - smooth(x1 - 3, x1, lx))
                over(acc, mix(m["cl"], (255, 236, 200), 0.5 * clamp01(yy - ly + 0.5)), wv)
        else:
            puff_cloud(acc, lx, ly, [(-4.0, -2.0, 2.8), (-0.6, -3.0, 3.4), (3.0, -1.8, 2.8), (6.0, -2.6, 2.2)],
                       mix(m["cl"], m["sun"], 0.2), m["cs"], rim=(255, 170, 60), rimk=0.6)
            embers(acc, lx, ly, ci + 3, 6, 10.0)
        cloud_sea(acc, lx, ly, 6.8, cl, cs, ci, rim=m["sun"], rimk=0.5)
    # glints
    for k in range(2):
        px, py = -8 + 16 * h3(ci, k, 7 + len(rid)), -9 + 9 * h3(ci, k, 8 + len(rid))
        s = sparkle(lx - px, ly - py, 1.9)
        if s > 0: over(acc, mix(m["glow"], WHITE, 0.65), s * 0.9)
    return acc


def scene_isle(rid, m, ci, lx, ly):
    """bottom corners: a tiny floating isle with a sparkly waterfall over a cloud sea (menu-emblem homage)"""
    acc = [0.0, 0.0, 0.0, 0.0]
    night = rid == "mythic"
    ws = -1 if ci == 2 else 1                       # the waterfall falls on the outer side
    over(acc, sky_bg(m, ly, night, 71.0 * ci, 5.0, lx), 1.0)
    cl, cs = m["cl"], m["cs"]
    # mood extras behind the isle
    if rid in ("legendary", "fabled"):
        over(acc, mul(m["cs"], 0.9), 0.45 * clamp01((-2 - ly) / 8))
        rain(acc, lx, ly, mix(cl, m["glow"], 0.25), 0.28)
    elif rid == "unique":
        ang = math.atan2(ly + 14, lx + 14 * ws); d = math.hypot(lx + 14 * ws, ly + 14)
        over(acc, mix(m["sun"], WHITE, 0.5), 0.3 * (0.5 + 0.5 * math.cos(ang * 20)) ** 4 * clamp01(1 - (d - 6) / 26))
    elif rid == "set":
        yy = -8.5 + 1.4 * math.sin(lx * 0.5 + ci)
        over(acc, mix((90, 255, 160), (120, 220, 255), (lx + 10) / 20), 0.45 * math.exp(-((ly - yy) ** 2) / 1.8))
    elif rid == "untiered":
        paint_sun(acc, lx + 6.0 * ws, ly - 7.5, 3.2, m["sun"], halo=0.9)
    elif rid == "rare":
        puff_cloud(acc, lx, ly, [(-6.0 * ws, -7.0, 2.2), (-3.4 * ws, -7.8, 2.6)], cl, cs, rim=m["glow"], rimk=0.25, alpha=0.9)
    elif rid == "normal":
        puff_cloud(acc, lx, ly, [(-6.0 * ws, -7.2, 2.0), (-3.6 * ws, -7.8, 2.4), (-1.4 * ws, -7.0, 1.8)], cl, cs, alpha=0.95)
    rim = m.get("moon") if night else (m["glow"] if rid in ("legendary", "fabled") else None)
    cloud_sea(acc, lx, ly, 7.2, cl, cs, ci + 5, rim=rim, rimk=0.6 if night else 0.15)
    cx = -1.2 * ws
    rx = lx - cx
    # rock underside: a jagged stepped cone, lit on the left
    if 0.3 <= ly <= 8.8:
        t = (ly - 0.3) / 8.5
        half = 7.3 * (1 - t) ** 0.85 + 0.8 * (h3(int(ly * 1.2), 3, ci) - 0.5)
        if abs(rx + 0.6 * t * ws) < half:
            c = mix((158, 124, 94), (72, 58, 78), t)
            if (rx + 0.6 * t * ws) > half - 1.4: c = mul(c, 0.72)
            elif (rx + 0.6 * t * ws) < -half + 1.2: c = mix(c, (190, 160, 128), 0.35)
            if int(ly * 1.25) % 3 == 0: c = mul(c, 0.88)
            if night: c = mix(c, (64, 36, 104), 0.5)
            if rid == "fabled": c = mix(c, (90, 30, 34), 0.35)
            over(acc, c, clamp01((half - abs(rx + 0.6 * t * ws)) * 2.0))
    # soil + grass cap
    if -2.6 <= ly <= 0.6 and abs(rx) < 7.6:
        edge = clamp01((7.6 - abs(rx)) * 2.0)
        if ly < -0.9:
            c = mix(m["grass"], WHITE, 0.3 * clamp01((-1.9 - ly) * 1.5))
            if night: c = mix(c, (150, 110, 220), 0.3)
        else:
            c = mix(m["grass"], (112, 80, 52), 0.6)
        over(acc, c, edge * clamp01((ly + 2.6) * 2.0))
    # a little stream on the grass to the waterfall + the waterfall + mist + sparkles
    if -2.6 <= ly <= -1.5 and 4.6 <= rx * ws <= 7.4:                     # the spring spilling over the lip
        over(acc, mix(m["water"], WHITE, 0.45), 0.95 * clamp01((rx * ws - 4.6) * 1.5))
    wx = cx + 7.9 * ws + 0.12 * max(0.0, ly + 1.5) * ws                   # the fall bows out a little as it drops
    hw = 1.05 + 0.08 * max(0.0, ly + 1.5)
    if -2.2 <= ly <= 8.6 and abs(lx - wx) < hw:
        ripple = 0.5 + 0.5 * math.sin((lx - wx) * 4.2 + ly * 0.7)
        c = mix(m["water"], WHITE, 0.15 + 0.5 * ripple)
        if (lx - wx) * ws > hw - 0.45: c = mul(c, 0.82)                  # shaded outer edge = a round, glassy fall
        over(acc, c, 0.95 * clamp01((hw - abs(lx - wx)) * 2.2))
    dm = math.hypot((lx - wx) * 0.8, (ly - 8.2) * 1.3)
    if dm < 5: over(acc, mix(m["water"], WHITE, 0.65), 0.7 * math.exp(-dm / 1.6))
    for (sx_, sy_, s) in ((wx + 1.4 * ws, 3.0, 1.7), (wx - 0.4 * ws, 6.0, 1.5), (wx + 2.4 * ws, 8.6, 2.2)):
        v = sparkle(lx - sx_, ly - sy_, s)
        if v > 0: over(acc, WHITE, v)
    # a tree (or Mythic's crystal) + the glowing emblem crystal
    tx = cx - 3.4 * ws
    if night:
        d = abs(lx - tx) / 1.3 + abs(ly + 5.2) / 3.0
        if d < 1.6: over(acc, (214, 110, 255), 0.5 * (1.6 - d))
        if d < 1: over(acc, mix((236, 186, 255), WHITE, 0.5 if lx < tx else 0.0), clamp01((1 - d) * 3))
    else:
        if abs(lx - tx) < 0.5 and -4.6 <= ly <= -2.4: over(acc, (96, 66, 44), 1.0)
        lean = 0.9 * ws if rid in ("legendary", "fabled") else 0.0
        puff_cloud(acc, lx, ly, [(tx - 1.0 + lean, -5.0, 1.7), (tx + 1.0 + lean, -5.2, 1.7), (tx + lean, -6.6, 1.9)],
                   mix(m["tree"], WHITE, 0.25), mul(m["tree"], 0.6))
    gx, gy = cx + 1.6 * ws, -3.3
    d = abs(lx - gx) / 0.9 + abs(ly - gy) / 1.9
    over(acc, mix(m["glow"], WHITE, 0.4), 0.6 * math.exp(-max(0.0, d - 0.6) * 1.1))
    if d < 1: over(acc, mix(m["glow"], WHITE, 0.55 if lx < gx else 0.15), clamp01((1 - d) * 3))
    if rid == "untiered": embers(acc, lx, ly, ci + 9, 4, 10.0)
    if night:
        v = sparkle(lx + 5.0 * ws, ly + 7.0, 2.0)
        if v > 0: over(acc, WHITE, v)
    return acc


# ---------------------------------------------------------------- tooltip sampler
def coords(X, Y):
    a = BIG if S0 <= X < S1 else (X if X < 54 else CAN - X)
    b = BIG if S0 <= Y < S1 else (Y if Y < 54 else CAN - Y)
    return a, b, (0 if X < 54 else 1) + (0 if Y < 54 else 2)


def boxd(a, b, inset, R, ci):
    """depth inside a rounded box + outward canvas unit vector"""
    sx, sy = ORI[ci]
    ax, by = a - inset, b - inset
    if ax < R and by < R:
        dx, dy = R - ax, R - by; h = math.hypot(dx, dy)
        if h < 1e-6: return R, (-sx * 0.707, -sy * 0.707)
        return R - h, (-sx * dx / h, -sy * dy / h)
    if ax < by: return ax, (-sx, 0.0)
    return by, (0.0, -sy)


# frame bands, in depth d from the box edge (box = INSET px in from the canvas edge)
OUT0, OUT1 = 0.0, 2.8         # outer gold tube
RIB1 = 9.2                    # sky ribbon OUT1..RIB1
IN1 = 11.0                    # inner gold tube RIB1..IN1
DARK1 = 11.7                  # dark separation
LINE1 = 12.8                  # rarity glow line DARK1..LINE1, then the panel


def frame_profile(acc, m, d, ox, oy, night):
    """paint the depth-only frame bands at box depth d; (ox, oy) = outward screen normal"""
    if d < OUT0:
        over(acc, mix(m["glow"], GOLD_L, 0.45), 0.42 * math.exp((d - OUT0) / 2.6))      # soft glow halo outside
        if d < OUT0 - 0.6: return
    if OUT1 - 0.4 <= d <= RIB1 + 0.4:                                                  # sky ribbon (depth gradient + a cloud streak)
        t = clamp01((d - OUT1) / (RIB1 - OUT1))
        if night:
            c = mix((132, 82, 204), (36, 14, 78), t)
            c = add(c, m["moon"], 0.35 * math.exp(-((d - 5.2) / 1.0) ** 2))
        else:
            c = mix(mix(m["sky1"], WHITE, 0.3), m["sky0"], t ** 0.9)
            c = mix(c, mix(m["cl"], WHITE, 0.5), 0.55 * math.exp(-((d - 5.0) / 0.9) ** 2))
        over(acc, c, 1.0)
    if OUT0 - 0.6 <= d <= OUT1 + 0.5:                                                  # outer gold tube with a dark outline
        s = 1 - 2 * (d - OUT0) / (OUT1 - OUT0)
        c = bevel(s, ox, oy, GOLD_D, GOLD_L)
        if d < OUT0 + 0.35 or d > OUT1 - 0.3: c = mix(c, GOLD_D, 0.55)
        over(acc, c, clamp01((d - OUT0 + 0.6) * 1.7) * clamp01((OUT1 + 0.5 - d) * 2))
    if RIB1 - 0.5 <= d <= IN1 + 0.5:                                                   # inner gold tube
        s = 1 - 2 * (d - RIB1) / (IN1 - RIB1)
        c = bevel(s, ox, oy, GOLD_D, GOLD_L)
        if d < RIB1 + 0.25 or d > IN1 - 0.25: c = mix(c, GOLD_D, 0.5)
        over(acc, c, clamp01((d - RIB1 + 0.5) * 2) * clamp01((IN1 + 0.5 - d) * 2))
    if d > IN1:
        if d < DARK1: over(acc, mul(m["panel"], 0.55), 1.0)
        elif d < LINE1: over(acc, mix(m["glow"], WHITE, 0.25), 1.0)
        else: over(acc, mix(m["panel"], m["glow"], 0.32 * math.exp(-(d - LINE1) / 2.0)), 1.0)


def corner_art(acc, rid, m, a, b, ci, night):
    sx, sy = ORI[ci]
    dd = math.hypot(a - MED_C, b - MED_C)
    # frame studs (little gold diamonds on the ribbon, beside each window)
    for (pa, pb) in ((41.0, INSET + 6.0), (INSET + 6.0, 41.0)):
        q = abs(a - pa) + abs(b - pb)
        if q < 6.0: over(acc, mix(m["glow"], GOLD_L, 0.5), 0.5 * math.exp(-q / 1.4))
        if q < 3.0:
            lit = (sx * (a - pa) * LX + sy * (b - pb) * LY) < 0
            over(acc, GOLD_L if lit else GOLD, clamp01((3.0 - q) * 2))
            if q < 1.0: over(acc, GOLD_W, clamp01((1.0 - q) * 2) * 0.8)
    # soft glow round the window
    if dd > RING_R - 1:
        f = 1.0 - smooth(40.0, 47.0, max(a, b))
        over(acc, mix(m["glow"], GOLD_L, 0.35), 0.55 * f * math.exp(-(dd - RING_R) / 2.4))
    # star point aimed out of the corner + its glowing sparkle
    dpt = (MED_C - a + MED_C - b) / math.sqrt(2); per = abs(a - b) / math.sqrt(2)
    L = RING_R + 8.6
    if RING_R - 2 < dpt < L and per < (L - dpt) * 0.42:
        upper = (a - b) * sx * sy >= 0
        c = mix(GOLD_L, GOLD, clamp01(per / 2.4)) if upper else mix(GOLD, GOLD_D, 0.45)
        if per < 0.45: c = mix(c, GOLD_W, 0.5)
        over(acc, c, clamp01(((L - dpt) * 0.42 - per) * 2.2))
    tp = MED_C - (L - 0.6) / math.sqrt(2)
    ddt = math.hypot(a - tp, b - tp)
    over(acc, mix(m["glow"], GOLD_L, 0.4), 0.5 * math.exp(-ddt / 2.0))
    v = sparkle(sx * (a - tp), sy * (b - tp), 5.2)
    if v > 0: over(acc, mix(m["glow"], WHITE, 0.75), v)
    # the gold ring (bevelled torus) + glass
    if WIN_R - 0.4 <= dd <= RING_R + 0.6:
        s = (dd - (WIN_R + RING_R) / 2) / ((RING_R - WIN_R) / 2)
        rx, ry = sx * (a - MED_C) / max(dd, 1e-6), sy * (b - MED_C) / max(dd, 1e-6)
        c = bevel(-s, -rx, -ry, GOLD_D, GOLD_L) if s < 0 else bevel(s, rx, ry, GOLD_D, GOLD_L)
        if dd > RING_R - 0.45 or dd < WIN_R + 0.35: c = mix(c, GOLD_D, 0.6)
        over(acc, c, clamp01((dd - WIN_R + 0.4) * 2.2) * clamp01((RING_R + 0.6 - dd) * 2.2))
    if dd < WIN_R + 0.4:
        lx, ly = sx * (a - MED_C), sy * (b - MED_C)
        sc = scene_top(rid, m, ci, lx, ly) if ci < 2 else scene_isle(rid, m, ci, lx, ly)
        col = sc[:3]
        col = mix(col, mul(col, 0.55), smooth(WIN_R - 2.2, WIN_R, dd))                 # inner shadow at the glass edge
        sheen = math.exp(-((math.hypot(lx + 2.5, ly + 2.5) - 9.0) / 1.1) ** 2) * clamp01(-(lx + ly) / 8)
        col = mix(col, WHITE, 0.22 * sheen)                                             # glass sheen, upper left
        over(acc, col, clamp01((WIN_R + 0.4 - dd) * 2.2))


def tip_sample(rid, X, Y):
    m = MOOD[rid]; night = rid == "mythic"
    a, b, ci = coords(X, Y)
    acc = [0.0, 0.0, 0.0, 0.0]
    d, (ox, oy) = boxd(a, b, INSET, BOX_R, ci)
    frame_profile(acc, m, d, ox, oy, night)
    if a < S0 and b < S0: corner_art(acc, rid, m, a, b, ci, night)
    return acc


# ---------------------------------------------------------------- arrow: the gold frame folds down into a V
# Client: Group #Arrow Anchor (Width 33, Height 24, Bottom: -8) -> @2x arrow row r lies on tooltip depth t = 32 - r from the bottom edge.
# Inside the V the bands use box depth s = max(t - INSET, e) (e = distance in from the V's slanted edge): at the V edge s equals the
# tooltip's own depth there, so the frame lines bend seamlessly into the V. Outside the V the arrow is transparent.
ATIP, ASL = 44.0, 0.72


def arrow_sample(rid, X, Y):
    m = MOOD[rid]; night = rid == "mythic"
    acc = [0.0, 0.0, 0.0, 0.0]
    q = abs(X - ARROW[0] / 2.0); H = (ATIP - Y) * ASL
    t = 32.0 - Y
    k = math.sqrt(1 + ASL * ASL)
    e = (H - q) / k
    side = 1.0 if X >= ARROW[0] / 2.0 else -1.0
    bt = t - INSET
    if q < H:
        if bt >= e: frame_profile(acc, m, bt, 0.0, 1.0, night)
        else: frame_profile(acc, m, e, side / k, ASL / k, night)
    elif bt < 0 and e > -12:
        frame_profile(acc, m, e, side / k, ASL / k, night)        # the soft halo round the hanging V only
    # the glowing gem near the tip + a sparkle at the point
    gy = ATIP - 11.5
    gd = abs(X - 33.0) / 2.6 + abs(Y - gy) / 3.6
    if gd < 2.2: over(acc, mix(m["glow"], GOLD_L, 0.3), 0.45 * math.exp(-max(0.0, gd - 0.8) * 1.6))
    if gd < 1.35:
        c = GOLD if gd > 1.0 else mix(m["glow"], WHITE, 0.55 if X < 33 and Y < gy else 0.1)
        if gd > 1.0 and (X < 33) == (Y < gy): c = GOLD_L
        over(acc, c, clamp01((1.35 - gd) * 3))
    v = sparkle(X - 33.0, Y - (ATIP + 0.5), 3.4)
    if v > 0: over(acc, mix(m["glow"], WHITE, 0.75), v * 0.9)
    return acc


# ---------------------------------------------------------------- slot frames (148 @2x, scaled whole)
SL_INSET, SL_R = 3.0, 9.0


def slot_sample(rid, X, Y):
    m = MOOD[rid]; night = rid == "mythic"
    acc = [0.0, 0.0, 0.0, 0.0]
    a = min(X, SLOT - X); b = min(Y, SLOT - Y)
    ci = (0 if X < SLOT / 2 else 1) + (0 if Y < SLOT / 2 else 2)
    sx, sy = ORI[ci]
    d, (ox, oy) = boxd(a, b, SL_INSET, SL_R, ci)
    if d < -0.5: return acc
    # soft mid-tone mood sky, darker toward the centre where the icon sits
    v = Y / SLOT
    if night: sky = mix(galaxy(X * 0.3 + 9, Y * 0.3 + 3, False), (40, 18, 80), 0.25)   # stars added after the mid-tone lift
    else: sky = mix(m["sky0"], m["sky1"], v)
    vig = math.hypot(X - SLOT / 2, Y - SLOT / 2) / (SLOT / 2)
    sky = mix(sky, m["panel"], 0.62 - 0.22 * clamp01(vig))
    tgt = 0.075 + 0.04 * clamp01(vig)                                      # keep the fill a mid-tone so dark icons still read
    if rl(sky) < tgt:
        lift = mix(m["sky1"], m["cl"], 0.5) if not night else (128, 92, 182)
        lo, hi = 0.0, 1.0
        for _ in range(7):
            md = (lo + hi) / 2
            if rl(mix(sky, lift, md)) < tgt: lo = md
            else: hi = md
        sky = mix(sky, lift, hi)
    if night: sky = mix(sky, (255, 244, 255), 0.5 * stars(X * 0.3 + 9, Y * 0.3 + 3, 3.2, 0.3))
    over(acc, sky, 1.0)
    lw = Y - (SLOT - 34) - 5 * math.sin(X * 0.075) - 3 * math.sin(X * 0.19 + 1)
    if lw > 0:
        c = mix(m["cl"], m["cs"], clamp01(lw / 22))
        if night: c = add(mix(m["cs"], m["cl"], 0.4), m["moon"], 0.35 * math.exp(-lw / 5))
        over(acc, mix(c, m["panel"], 0.5), 0.75 * clamp01(lw / 3))
    # mood accent in the top-right margin (partly under the icon, kept soft)
    ax_, ay_ = X - (SLOT - 30), Y - 30
    if rid in ("normal", "unique", "set"): paint_sun(acc, ax_, ay_, 7.0, mix(m["sun"], m["panel"], 0.2), rays=12 if rid == "unique" else 0, halo=0.6)
    elif rid == "untiered": paint_sun(acc, ax_, Y - (SLOT - 40), 8.0, mix(m["sun"], m["panel"], 0.15), halo=0.7)
    elif rid == "mythic": paint_moon(acc, ax_, ay_, 7.5, mix(m["moon"], m["panel"], 0.15))
    elif rid in ("legendary", "fabled"):
        paint_bolt(acc, X, Y, [(SLOT - 34, 12), (SLOT - 40, 26), (SLOT - 33, 28), (SLOT - 42, 46)], mix(m["bolt"], m["panel"], 0.25),
                   m["glow"], 0.9)
    elif rid == "rare":
        puff_cloud(acc, X, Y, [(SLOT - 40, 26, 7), (SLOT - 28, 22, 9), (SLOT - 16, 28, 6)], mix(m["cl"], m["panel"], 0.35),
                   mix(m["cs"], m["panel"], 0.4), rim=m["glow"], rimk=0.2)
    # inner glow + rarity line + gold bevel frame
    if d > 7.4: over(acc, m["glow"], 0.32 * math.exp(-(d - 7.4) / 3.0))
    if 6.2 <= d <= 7.6: over(acc, mix(m["glow"], WHITE, 0.25), clamp01(min(d - 6.2, 7.6 - d) * 2.5 + 0.3))
    if 5.0 <= d < 6.2: over(acc, mul(m["panel"], 0.55), 1.0)
    if -0.5 <= d <= 5.4:
        s = 1 - 2 * d / 5.0
        c = bevel(s, ox, oy, GOLD_D, GOLD_L)
        if d < 0.45 or d > 4.7: c = mix(c, GOLD_D, 0.55)
        over(acc, c, clamp01((d + 0.5) * 2) * clamp01((5.4 - d) * 2))
    # gold star studs in the corners
    q = abs(a - 9.5) + abs(b - 9.5)
    if q < 12: over(acc, mix(m["glow"], GOLD_L, 0.4), 0.45 * math.exp(-q / 2.6))
    st = sparkle(sx * (a - 9.5), sy * (b - 9.5), 7.5)
    if st > 0: over(acc, mix(GOLD_L, WHITE, 0.4), st)
    return acc


# ---------------------------------------------------------------- render
def render(fn, w, h, unit, ss=SS):
    img = []; inv = 1.0 / ss; n = ss * ss
    for py in range(h):
        row = []
        for px in range(w):
            r = g = bl = al = 0.0
            for j in range(ss):
                Y = (py + (j + 0.5) * inv) * unit
                for i in range(ss):
                    X = (px + (i + 0.5) * inv) * unit
                    c = fn(X, Y)
                    if c[3] > 0:
                        r += c[0] * c[3]; g += c[1] * c[3]; bl += c[2] * c[3]; al += c[3]
            if al > 0:
                A = al / n * 255.0
                if A >= 254.0: A = 255.0                          # opaque where the frame / panel covers the pixel
                row.append([int(round(r / al)), int(round(g / al)), int(round(bl / al)), int(round(A))])
            else:
                row.append([0, 0, 0, 0])
        img.append(row)
    return img


def drop_centre(img, k):
    return [r[:k] + r[k + 1:] for i, r in enumerate(img) if i != k]


def make_one(rid):
    t2 = drop_centre(render(lambda X, Y: tip_sample(rid, X, Y), CAN, CAN, 1.0), CAN // 2)
    t1 = render(lambda X, Y: tip_sample(rid, X, Y), CAN // 2, CAN // 2, 2.0)
    a2 = render(lambda X, Y: arrow_sample(rid, X, Y), ARROW[0], ARROW[1], 1.0)
    a1 = render(lambda X, Y: arrow_sample(rid, X, Y), ARROW[0] // 2, ARROW[1] // 2, 2.0)
    s2 = render(lambda X, Y: slot_sample(rid, X, Y), SLOT, SLOT, 1.0, 3)
    s1 = render(lambda X, Y: slot_sample(rid, X, Y), SLOT // 2, SLOT // 2, 2.0, 3)
    return rid, {"tip2": t2, "tip1": t1, "arr2": a2, "arr1": a1, "slot2": s2, "slot1": s1}


def rel_paths(name):
    return {"tip2": "%s/Tooltip_%s@2x.png" % (TIP_DIR, name), "tip1": "%s/Tooltip_%s.png" % (TIP_DIR, name),
            "arr2": "%s/Tooltip_%sArrow@2x.png" % (TIP_DIR, name), "arr1": "%s/Tooltip_%sArrow.png" % (TIP_DIR, name),
            "slot2": "%s/Slot_%s@2x.png" % (SLOT_DIR, name), "slot1": "%s/Slot_%s.png" % (SLOT_DIR, name)}


def quality_fields(name):
    """the exact SkyyGear quality-asset field values for this rarity (paths without @2x; the client finds the @2x file)"""
    return {"ItemTooltipTexture": "UI/SkyyGear/Tooltips/Tooltip_%s.png" % name,
            "ItemTooltipArrowTexture": "UI/SkyyGear/Tooltips/Tooltip_%sArrow.png" % name,
            "SlotTexture": "UI/SkyyGear/Slots/Slot_%s.png" % name,
            "BlockSlotTexture": "UI/SkyyGear/Slots/Slot_%s.png" % name,
            "SpecialSlotTexture": "UI/SkyyGear/Slots/Slot_%s.png" % name}


def encode_png(w, h, raw):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def png_bytes(img):
    w, h = P.size(img); raw = bytearray()
    for row in img:
        raw.append(0)
        for p in row: raw.extend(bytes(max(0, min(255, int(v))) for v in p))
    return encode_png(w, h, bytes(raw))


def build_all(procs=None):
    """-> {rel path: (image, png bytes)} for every texture"""
    with Pool(procs or min(len(RARITIES), os.cpu_count() or 4)) as pool:
        res = dict(pool.map(make_one, [r[0] for r in RARITIES]))
    out = {}
    for rid, name, _hex, _mood in RARITIES:
        rp = rel_paths(name)
        for k, img in res[rid].items():
            out[rp[k]] = (img, png_bytes(img))
    return out


# ---------------------------------------------------------------- contrast
def rl(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(a, b):
    la, lb = rl(a), rl(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def contrast_table(files):
    """per rarity: contrast of every text colour on the @2x tooltip centre pixel (opaque) -> {name: {colour: ratio}}"""
    out = {}
    for rid, name, hexs, _m in RARITIES:
        img = files[rel_paths(name)["tip2"]][0]
        c = tuple(img[53][53][:3])
        row = {k: round(contrast(v, c), 2) for k, v in TEXT.items()}
        row["rarity"] = round(contrast(hx(hexs), c), 2)
        row["dimgrey130"] = round(contrast((130, 130, 130), c), 2)
        out[name] = {"centre": "#%02x%02x%02x" % c, "alpha": img[53][53][3], "ratios": row,
                     "min_required": round(min(v for k, v in row.items() if k != "dimgrey130"), 2)}
    return out


# ---------------------------------------------------------------- sheet canvas (bytearray)
P._F.setdefault("@", "01110100011011110101101111000001110")
P._F.setdefault("!", "00100001000010000100001000000000100")
P._F.setdefault("?", "01110100010000100110001000000000100")


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes((bg[0], bg[1], bg[2], 255)) * (w * h))

    def fill(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(self.w, x1), min(self.h, y1)
        if x1 <= x0: return
        line = bytes((int(c[0]), int(c[1]), int(c[2]), 255)) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 4; self.px[i:i + len(line)] = line

    def over(self, x, y, p):
        if not (0 <= x < self.w and 0 <= y < self.h) or p[3] <= 0: return
        i = (y * self.w + x) * 4; a = p[3] / 255.0
        for k in range(3): self.px[i + k] = int(round(p[k] * a + self.px[i + k] * (1 - a)))

    def blit(self, img, ox, oy, scale=1):
        for y, row in enumerate(img):
            for x, p in enumerate(row):
                if p[3] <= 0: continue
                for yy in range(scale):
                    for xx in range(scale): self.over(ox + x * scale + xx, oy + y * scale + yy, p)

    def text(self, x, y, s, c, scale=2, bold=False, italic=False):
        for ch in s:
            g = P._F.get(ch) or P._F.get(ch.upper()) or P._F[" "]
            for i, bit in enumerate(g):
                if bit == "1":
                    sh = (3 - i // 5) * scale // 3 if italic else 0
                    self.fill(x + (i % 5) * scale + sh, y + (i // 5) * scale, x + (i % 5 + 1) * scale + (1 if bold else 0) + sh,
                              y + (i // 5 + 1) * scale, c)
            x += 6 * scale
        return x

    def png(self):
        raw = bytearray(); stride = self.w * 4
        for y in range(self.h):
            raw.append(0); raw.extend(self.px[y * stride:(y + 1) * stride])
        return encode_png(self.w, self.h, bytes(raw))


def nine_slice(img, border, W, H):
    """stretch like the client: corners fixed, edges + centre stretched (nearest)"""
    w, h = P.size(img)
    def src(v, full, out_full):
        if v < border: return v
        if v >= out_full - border: return full - (out_full - v)
        mid = full - 2 * border
        return border + min(mid - 1, (v - border) * mid // max(1, out_full - 2 * border))
    return [[img[src(y, h, H)][src(x, w, W)] for x in range(W)] for y in range(H)]


def sword_icon(colour):
    """a simple ORIGINAL placeholder sword (64 x 64)"""
    img = P.new(64, 64)
    for y in range(64):
        for x in range(64):
            u = (x - y) / math.sqrt(2); v = (x + y) / math.sqrt(2) - 45
            if abs(u) <= 4.5 and -38 <= v <= 14:
                img[y][x] = list(mix((220, 226, 236), colour, 0.25)) + [255] if abs(u) < 3.2 else [40, 40, 52, 255]
            if abs(v - 14) <= 2.5 and abs(u) <= 12: img[y][x] = [70, 48, 30, 255] if abs(v - 14) > 1.2 else [200, 160, 70, 255]
            if 14 < v <= 26 and abs(u) <= 2.2: img[y][x] = [96, 62, 36, 255]
    return img


def dark_icon():
    """an ORIGINAL dark placeholder (iron-ish helmet blob) to show how dark icons read on the slot sky"""
    img = P.new(64, 64)
    for y in range(64):
        for x in range(64):
            dx, dy = (x - 32) / 22.0, (y - 34) / 22.0
            if dx * dx + dy * dy < 1 and y < 46:
                c = (58, 60, 70) if not (abs(x - 32) < 3 and y > 26) else (24, 24, 30)
                if y > 38 and abs(x - 32) > 6: c = (44, 46, 54)
                img[y][x] = list(mix(c, (120, 124, 140), clamp01(-(dx + dy) * 0.6))) + [255]
    return img


def game_bg(cv, x, y, w, h, seed=0):
    """a plain light 'in-game' backdrop (day sky + an island band)"""
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = mix((122, 176, 226), (206, 228, 246), t * 1.4)
        if t > 0.84: c = mix((84, 140, 70), (54, 96, 52), (t - 0.84) / 0.16)
        cv.fill(x, y + yy, x + w, y + yy + 1, c)
    for k in range(4):
        cx, cy, r = x + int(w * h3(k, seed, 41)), y + int(h * 0.55 * h3(k, seed, 42)), 22 + int(26 * h3(k, seed, 43))
        for yy in range(-r, r):
            for xx in range(-2 * r, 2 * r):
                q = (xx / 2.0) ** 2 + yy * yy
                if q < r * r and x <= cx + xx < x + w and y <= cy + yy < y + h:
                    cv.over(cx + xx, cy + yy, (250, 252, 255, int(100 * (1 - q / (r * r)))))


# SkyyGear 0.2.19 tooltip style: Wynncraft top (name, speed, label/value base rows, green + / red - rolled rows, Class Req, Lv. Min),
# SkyBlock bottom (bold gold Ability + grey text + Mana Cost, italic flavour, reforge line, bold RARITY TYPE)
G_GREY, G_DIM, G_GREEN, G_RED, G_GOLD, G_AQUA, G_WHITE = (170, 170, 170), (130, 130, 130), (85, 255, 85), (255, 85, 85), \
    (255, 170, 0), (85, 255, 255), (255, 255, 255)
ITEMS = {"normal": ("Skyward Blade", "SWORD"), "unique": ("Sunforged Saber", "SWORD"), "rare": ("Cloudpetal Staff", "STAFF"),
         "legendary": ("Stormcaller", "SWORD"), "fabled": ("Tempest Fang", "CLAWS"), "mythic": ("Voidmoon Wand", "WAND"),
         "set": ("Dawnwarden Helm", "HELMET"), "untiered": ("Emberfall Bow", "BOW")}


def tip_rows(rid, name, size):
    item, typ = ITEMS[rid]
    rows = [("*", item, None), ("", "Fast Attack Speed", G_GREY), ("", "", None),
            ("", "Damage 22-30", G_WHITE), ("", "Health +16", G_WHITE),
            ("+", "+ Strength   +12", G_GREEN), ("+", "+ Crit Chance   +5%", G_GREEN), ("", "- Walk Speed   -2%", G_RED), ("", "", None),
            ("", "Class Req: Warrior", G_GREY), ("", "Lv. Min: 15 Swordsmanship", G_GREEN), ("", "", None),
            ("*g", "Ability: Charged Attack", G_GOLD), ("", "Full charge hits all foes", G_GREY), ("", "within 6 blocks.", G_GREY),
            ("m", "Mana Cost: 40", None), ("", "", None),
            ("~", "Woven from the open sky.", G_GREY), ("", "This item can be reforged!", G_GREY), ("*", "%s %s" % (name.upper(), typ), None)]
    if size == 1:
        rows = rows[:9] + rows[12:16] + rows[18:]
    elif size == 2:
        rows = rows[:3] + rows[5:8] + [rows[-1]]
    return rows


def draw_tooltip(cv, files, rid, name, colour, x, y, W, H, arrow_x, scale, rows):
    """scale 1 = 1x textures, UI scale 1 (font scale 2, line 18); scale 2 = @2x textures 1:1 (font scale 3, line 26)"""
    rp = rel_paths(name)
    if scale == 1:
        cv.blit(nine_slice(files[rp["tip1"]][0], 24, W, H), x, y)
        cv.blit(files[rp["arr1"]][0], x + arrow_x, y + H - 16)
        fs, lh, padx, pady = 2, 17, 24, 21
    else:
        cv.blit(nine_slice(files[rp["tip2"]][0], 48, W, H), x, y)
        cv.blit(files[rp["arr2"]][0], x + arrow_x, y + H - 32)
        fs, lh, padx, pady = 3, 26, 48, 42
    tx, ty = x + padx, y + pady
    for kind, s, c in rows:
        if not s:
            ty += lh // 2; continue
        if kind == "*": cv.text(tx, ty, s, colour, fs, bold=True)
        elif kind == "*g": cv.text(tx, ty, s, c, fs, bold=True)
        elif kind == "~": cv.text(tx, ty, s, c, fs, italic=True)
        elif kind == "m":
            e = cv.text(tx, ty, "Mana Cost:", G_GREY, fs); cv.text(e + 6 * fs, ty, "40", G_AQUA, fs)
        else: cv.text(tx, ty, s, c, fs)
        ty += lh
    return ty


def rows_height(rows, lh):
    return sum(lh // 2 if not r[1] else lh for r in rows)


def make_sheet(files, table):
    W = 2060
    H = 7000
    cv = Canvas(W, H, (30, 34, 46))
    for yy in range(0, H, 40):
        for xx in range(0, W, 40):
            if (xx // 40 + yy // 40) % 2: cv.fill(xx, yy, xx + 40, yy + 40, (34, 38, 52))
    cv.text(24, 18, "SKYYGEAR RARITY FRAMES - SKY WINDOW (ISLES OF THE VOID) - FINAL TEXTURES", (255, 236, 170), 4, bold=True)
    cv.text(24, 62, "REAL 9-SLICE: 107 PX @2X TEXTURE (54 PX 1X), 48 PX (24 UI) CORNERS FIXED, EDGES + CENTRE STRETCH. ARROW 66X48 @2X, "
            "NEVER STRETCHED. SLOT 148 @2X SCALED WHOLE.", (200, 206, 224), 2)
    cv.text(24, 84, "TOP: LEGENDARY + MYTHIC AT @2X 1:1 (UI SCALE 2). BELOW: EVERY RARITY AT UI SCALE 1 (1X TEXTURES), 3 TOOLTIP SIZES, "
            "ARROW, RAW TEXTURES, 9-SLOT ROW.", (160, 166, 186), 2)
    y = 120
    # heroes @2x 1:1
    for k, (rid, name, hexs, mood) in enumerate((RARITIES[3], RARITIES[5])):
        x = 24 + k * 1012
        rows = tip_rows(rid, name, 0)
        th = rows_height(rows, 26) + 42 + 40
        game_bg(cv, x, y, 990, th + 80, k)
        draw_tooltip(cv, files, rid, name, hx(hexs), x + 20, y + 16, 950, th, 260, 2, rows)
        cv.text(x, y + th + 90, "%s - %s - @2X 1:1 (475 X %d UI)" % (name.upper(), mood, th // 2), (220, 224, 236), 2)
    y += th + 130
    # rarity rows
    bgs = (30, 34, 46)
    for i, (rid, name, hexs, mood) in enumerate(RARITIES):
        col = hx(hexs)
        r0, r1, r2 = tip_rows(rid, name, 0), tip_rows(rid, name, 1), tip_rows(rid, name, 2)
        h0 = rows_height(r0, 17) + 21 + 20; h1 = rows_height(r1, 17) + 21 + 20; h2 = rows_height(r2, 17) + 21 + 20
        bh = max(h0 + 50, 380)
        cv.fill(16, y - 8, W - 16, y + bh + 44, (24, 28, 40))
        cv.text(28, y, "%s  -  %s" % (name.upper(), mood), col, 3, bold=True)
        tb = table[name]
        cv.text(560, y + 4, "TEXT PANEL %s  LOWEST CONTRAST %.1f:1 (AA 4.5)" % (tb["centre"].upper(), tb["min_required"]),
                (150, 230, 150) if tb["min_required"] >= 4.5 else (255, 140, 120), 2)
        y += 34
        game_bg(cv, 20, y, 1380, bh, i)
        draw_tooltip(cv, files, rid, name, col, 32, y + 12, 360, h0, 30, 1, r0)
        draw_tooltip(cv, files, rid, name, col, 412, y + 12, 420, h1, 190, 1, r1)
        draw_tooltip(cv, files, rid, name, col, 852, y + 12, 480, h2, 400, 1, r2)
        cv.text(412, y + h1 + 34, "360 / 420 / 480 UI WIDE (CLIENT 320-480), ARROW AT 3 SPOTS", (40, 50, 70), 2)
        # raw textures + arrow + slots on the right
        rp = rel_paths(name)
        xr = 1420
        cv.fill(xr, y, xr + 222, y + 222, (60, 64, 78))
        cv.blit(files[rp["tip2"]][0], xr + 4, y + 4, 2)
        for q in (48, 59):
            for t in range(0, 214, 6):
                cv.fill(xr + 4 + q * 2, y + 4 + t, xr + 5 + q * 2, y + 7 + t, (255, 255, 255))
                cv.fill(xr + 4 + t, y + 4 + q * 2, xr + 7 + t, y + 5 + q * 2, (255, 255, 255))
        cv.fill(xr + 232, y, xr + 232 + 140, y + 104, (60, 64, 78))
        cv.blit(files[rp["arr2"]][0], xr + 236, y + 4, 2)
        cv.text(xr + 232, y + 110, "ARROW @2X X2", (180, 186, 204), 1)
        cv.text(xr, y + 228, "TOOLTIP @2X X2 (DASHED = CUTS)", (180, 186, 204), 1)
        cv.blit(files[rp["slot2"]][0], xr + 232 + 150, y)
        cv.blit(sword_icon(col), xr + 232 + 150 + 10, y + 10, 2)
        cv.text(xr + 382, y + 154, "SLOT @2X", (180, 186, 204), 1)
        cv.blit(files[rp["slot1"]][0], xr + 232, y + 130)
        cv.blit(dark_icon(), xr + 237, y + 135)
        cv.text(xr + 232, y + 208, "1X + DARK ICON", (180, 186, 204), 1)
        # 9-slot inventory row (UI scale 1): this rarity in slot 1 + 5, the others around it
        yi = y + 260
        cv.fill(xr - 6, yi - 6, xr + 9 * 70 + 2, yi + 80, (46, 52, 66))
        order = [rid] + [r[0] for r in RARITIES if r[0] != rid]
        names = {r[0]: r for r in RARITIES}
        for s in range(9):
            sx_ = xr + s * 70
            if s == 8:                                     # an empty plain slot for comparison
                cv.fill(sx_ + 2, yi + 2, sx_ + 66, yi + 66, (60, 66, 82)); cv.fill(sx_ + 5, yi + 5, sx_ + 63, yi + 63, (40, 44, 58))
                continue
            rr = names[order[s]]
            cv.blit(P.downsample(files[rel_paths(rr[1])["slot2"]][0], 2), sx_ - 3, yi - 3)   # 74 px slot, 70 px pitch (overlap like the grid)
            cv.blit(sword_icon(hx(rr[2])) if s != 4 else dark_icon(), sx_ + 2, yi + 2)
        cv.text(xr, yi + 90, "9-SLOT ROW, UI SCALE 1 (SLOT 74 UI)", (180, 186, 204), 1)
        y += max(bh + 52, 440)
    out = Canvas(W, y + 20, (30, 34, 46))
    out.px[:] = cv.px[:W * (y + 20) * 4]
    return out.png()


# ---------------------------------------------------------------- main
def main():
    files = build_all()
    table = contrast_table(files)
    for name, t in table.items():
        print("  %-9s panel %s  min %.2f  %s" % (name, t["centre"], t["min_required"],
                                                  " ".join("%s %.1f" % (k, v) for k, v in t["ratios"].items())))
    for rel, (img, data) in files.items():
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh: fh.write(data)
    sheet = make_sheet(files, table)
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh: fh.write(sheet)
    man = {
        "what": "SkyyGear rarity tooltip backgrounds + arrows + slot frames - SKY WINDOW (Isles of the Void), final textures",
        "generator": "tools/art/make_tooltip_sky.py", "validator": "tools/art/validate_tooltip_sky.py",
        "deterministic": True, "original_pixels": True,
        "nine_slice": {"tooltip_2x": [107, 107], "border_2x_px": 48, "border_ui_units": 24, "stretch_strip_2x": [48, 58],
                       "tooltip_1x": [54, 54], "border_1x_px": 24, "stretch_strip_1x": [24, 29],
                       "arrow_2x": list(ARROW), "arrow_ui": [33, 24], "slot_2x": [SLOT, SLOT], "slot_ui": [74, 74]},
        "rarities": [], "files": [],
        "sheet": {"path": "sheet.png", "bytes": len(sheet), "sha256": hashlib.sha256(sheet).hexdigest()},
    }
    for rid, name, hexs, mood in RARITIES:
        man["rarities"].append({"id": rid, "name": name, "hex": hexs, "mood": mood, "quality_asset_fields": quality_fields(name),
                                "paths": rel_paths(name), "contrast": table[name]})
    for rel in sorted(files):
        data = files[rel][1]; w, h = P.size(files[rel][0])
        man["files"].append({"path": rel, "w": w, "h": h, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(man, fh, indent=1); fh.write("\n")
    print("wrote %d textures + sheet.png (%d bytes) + manifest.json to %s" % (len(files), len(sheet), OUT))


if __name__ == "__main__":
    main()
