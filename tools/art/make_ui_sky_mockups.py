#!/usr/bin/env python3
"""SkyWynn "Isles of the Void" UI sky MOCKUPS - 4 concept approaches for rarity tooltips + slot frames (CONCEPT ONLY, all ORIGINAL pixels).

Skyy 2026-10-10: "how about we come up with several approaches, and for the Isles of the void theams, make some simple mockups ...
im picturing a lighter softer look, maybe like flowing clouds, with softer light glowy almost water color magic looking swirls and
shapes. (then for the rarities, you keep the clody/ sky theme so some get more stormy, some get more sunny ... legendary could have
blue lighting, mythic its night, and the clouds open up to show a magical stary/ galactic scene bordered by clouds shining purple
from the purple moon."

Approaches: 1 CLOUD FRAME, 2 SKY WINDOW, 3 WATERCOLOUR SWIRL, 4 FLOATING ISLE.
Every approach renders, per rarity, a real-size @2x tooltip texture (107 x 107, 9-slice border 48 px = Border 24 UI units, built
exactly like tools/art/make_tooltip_frames.py: 108 px design canvas, the 48..59 strip only depends on depth from the edge, then
column / row 54 dropped) and a 148 x 148 @2x slot (scaled whole). The sheet shows them 9-sliced the way the client does it.
These textures are NOT written as assets - only the review sheet is written (art/ui-sky-mockups/sheet.png).

Run: python tools/art/make_ui_sky_mockups.py      (deterministic; pure Python 3, no Pillow; uses all CPU cores)
Helpers: tools/art/emblem_png.py (font, downsample) + tools/art/make_tooltip_frames.py (Canvas, nine_slice, sword_icon).
"""
import math, os, random, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_tooltip_frames as TF

P._F.setdefault("@", "01110100011011110101101111000001110")   # sheet labels only

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "art", "ui-sky-mockups")
CAN = 108                  # tooltip design canvas (@2x px); strip 48..59; drop 54 -> 107
S0, S1 = 48, 60
BIG = 1.0e4
SS_TIP, SS_SLOT = 3, 2
SLOT = 148

RAR = [("normal", "Normal", "#FFFFFF", "CLEAR DAY"), ("unique", "Unique", "#FFFF55", "GOLDEN SUN"),
       ("rare", "Rare", "#FF55FF", "PINK DRIFT"), ("legendary", "Legendary", "#55FFFF", "BLUE STORM"),
       ("fabled", "Fabled", "#FF5555", "RED TEMPEST"), ("mythic", "Mythic", "#CC66CC", "STAR NIGHT"),
       ("set", "Set", "#55FF55", "GREEN DAWN"), ("untiered", "Untiered", "#FFAA00", "EMBER SUNSET")]

# sky mood per rarity: sky0 = zenith, sky1 = horizon, cl / cs = cloud lit / shade, glow = magic glow (rarity colour),
# panel = text-area colour (kept dark: white / grey / green / red / gold text must read), fx = extras
MOOD = {
    "normal":    dict(sky0=(104, 170, 232), sky1=(206, 232, 250), cl=(252, 253, 255), cs=(170, 192, 226), glow=(236, 246, 255),
                      panel=(18, 28, 54), fx={"sun"}, sun=(255, 244, 196), grass=(98, 182, 84), water=(176, 226, 255)),
    "unique":    dict(sky0=(96, 166, 234), sky1=(255, 232, 164), cl=(255, 250, 232), cs=(226, 192, 138), glow=(255, 236, 110),
                      panel=(26, 28, 52), fx={"sun", "rays"}, sun=(255, 224, 104), grass=(150, 196, 74), water=(190, 232, 255)),
    "rare":      dict(sky0=(146, 150, 226), sky1=(248, 198, 234), cl=(255, 238, 250), cs=(200, 152, 212), glow=(255, 120, 255),
                      panel=(32, 20, 52), fx={"puffs"}, grass=(108, 184, 112), water=(236, 196, 255), flower=(255, 140, 230)),
    "legendary": dict(sky0=(30, 46, 86), sky1=(96, 126, 170), cl=(172, 190, 218), cs=(64, 76, 108), glow=(85, 255, 255),
                      panel=(12, 28, 52), fx={"bolt", "rain", "storm"}, bolt=(190, 248, 255), grass=(70, 140, 112), water=(120, 240, 255)),
    "fabled":    dict(sky0=(52, 16, 30), sky1=(156, 60, 56), cl=(200, 134, 128), cs=(76, 30, 42), glow=(255, 85, 85),
                      panel=(40, 16, 28), fx={"bolt", "rain", "storm"}, bolt=(255, 200, 160), grass=(120, 96, 64), water=(255, 120, 80)),
    "mythic":    dict(sky0=(10, 6, 30), sky1=(58, 22, 96), cl=(124, 84, 168), cs=(40, 22, 70), glow=(214, 110, 255),
                      panel=(16, 9, 36), fx={"night"}, moon=(226, 168, 255), grass=(126, 84, 190), water=(220, 160, 255)),
    "set":       dict(sky0=(68, 118, 150), sky1=(226, 244, 176), cl=(244, 255, 236), cs=(146, 194, 160), glow=(85, 255, 85),
                      panel=(14, 38, 40), fx={"aurora", "sun"}, sun=(240, 255, 190), grass=(84, 214, 92), water=(170, 255, 210)),
    "untiered":  dict(sky0=(84, 34, 70), sky1=(255, 154, 70), cl=(255, 210, 160), cs=(168, 80, 72), glow=(255, 170, 0),
                      panel=(42, 22, 26), fx={"ember", "sun", "low"}, sun=(255, 140, 50), grass=(206, 126, 46), water=(255, 180, 80)),
}
GOLD_D, GOLD, GOLD_L = (138, 92, 30), (226, 176, 58), (255, 238, 156)
WHITE = (255, 255, 255)
LX, LY, LZ = -0.45, -0.70, 0.55
_l = math.sqrt(LX * LX + LY * LY + LZ * LZ); LX, LY, LZ = LX / _l, LY / _l, LZ / _l
ORI = {0: (1, 1), 1: (-1, 1), 2: (1, -1), 3: (-1, -1)}   # canvas dir of +a, +b per corner (a, b point inward)


# ---------------------------------------------------------------- maths
def clamp01(v): return 0.0 if v < 0 else 1.0 if v > 1 else v
def smooth(e0, e1, x):
    t = clamp01((x - e0) / (e1 - e0)); return t * t * (3 - 2 * t)
def mix(a, b, t):
    t = clamp01(t); return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)
def mul(a, f): return (min(255, a[0] * f), min(255, a[1] * f), min(255, a[2] * f))
def add(a, b, f): return (min(255, a[0] + b[0] * f), min(255, a[1] + b[1] * f), min(255, a[2] + b[2] * f))


def over(acc, col, al):
    """straight-alpha 'over' into acc = [r, g, b, a(0..1)]"""
    if al <= 0.002: return
    if al > 1: al = 1.0
    oa = al + acc[3] * (1 - al)
    k = acc[3] * (1 - al)
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


# ---------------------------------------------------------------- shared painted elements (dx, dy in canvas px, y down)
def sparkle(dx, dy, s):
    ax, ay = abs(dx), abs(dy)
    if ax > s or ay > s: return 0.0
    arm = max(math.exp(-ay * ay / 0.35) * (1 - ax / s), math.exp(-ax * ax / 0.35) * (1 - ay / s))
    return min(1.0, arm + math.exp(-(dx * dx + dy * dy) / 1.1))


def paint_sun(acc, dx, dy, r, col, rays):
    d = math.hypot(dx, dy)
    if d > r * 3.4: return
    over(acc, mix(col, WHITE, 0.3), 0.55 * math.exp(-max(0.0, d - r) / (r * 0.7)))
    if rays and d > r:
        ang = math.atan2(dy, dx)
        over(acc, mix(col, WHITE, 0.5), 0.42 * ((0.5 + 0.5 * math.cos(ang * 9)) ** 5) * math.exp(-(d - r) / (r * 1.3)))
    over(acc, mix(col, WHITE, 0.55 * clamp01(1 - d / r)), clamp01(r - d + 0.5))


def paint_moon(acc, dx, dy, r, col):
    d = math.hypot(dx, dy)
    if d > r * 3.6: return
    over(acc, col, 0.62 * math.exp(-max(0.0, d - r) / (r * 0.85)))
    if d < r + 0.5:
        c = mix(col, WHITE, 0.45 * clamp01(1 - math.hypot(dx + r * 0.3, dy + r * 0.3) / r))
        for cx, cy, cr in ((0.25, -0.1, 0.22), (-0.3, 0.35, 0.16), (0.1, 0.45, 0.12)):     # soft craters
            if math.hypot(dx - cx * r, dy - cy * r) < cr * r: c = mul(c, 0.86)
        sd = math.hypot(dx + r * 0.55, dy - r * 0.15)                                       # crescent shade
        c = mix(c, mul(col, 0.42), 0.75 * smooth(r * 0.95, r * 0.65, sd))
        over(acc, c, clamp01(r - d + 0.5))


def paint_bolt(acc, dx, dy, pts, col, glow, w=0.75):
    dist = poly_dist(dx, dy, pts)
    if dist > 9: return
    over(acc, glow, 0.55 * math.exp(-dist / 2.4))
    over(acc, mix(col, WHITE, 0.6), clamp01(w + 0.5 - dist))


def stars(x, y, cell=4.0, dens=0.55):
    i, j = int(math.floor(x / cell)), int(math.floor(y / cell))
    h = h3(i + 311, j + 97, 5)
    if h > dens: return 0.0
    sx = (i + 0.2 + 0.6 * h3(i, j, 1)) * cell; sy = (j + 0.2 + 0.6 * h3(i, j, 2)) * cell
    br = 0.4 + 0.6 * h3(i, j, 3)
    d2 = (x - sx) ** 2 + (y - sy) ** 2
    s = br * math.exp(-d2 / 0.35)
    if br > 0.85: s = max(s, sparkle(x - sx, y - sy, 2.6) * br)
    return s


def galaxy(x, y):
    """night sky + nebula + stars at canvas px (x, y) -> colour"""
    n = fbm(x * 0.09 + 3.1, y * 0.09 + 7.7)
    m = fbm(x * 0.05 + 11.0, y * 0.05 + 2.0)
    c = mix((12, 6, 34), (70, 24, 120), smooth(0.35, 0.8, n))
    c = mix(c, (40, 70, 170), 0.55 * smooth(0.5, 0.85, m))
    c = mix(c, (255, 140, 240), 0.25 * smooth(0.62, 0.9, n))
    s = stars(x, y)
    return mix(c, (255, 244, 255), s)


def cloud_shade(nx, ny, nz, cl, cs):
    l = clamp01(0.30 + 0.85 * (nx * LX + ny * LY + nz * LZ))
    return mix(cs, cl, l)


def soft_shade(nx, ny, nz, cl, cs):
    """gentler, watercolour-like cloud light (less 'bubble' than cloud_shade)"""
    l = clamp01(0.5 + 0.55 * (nx * LX + ny * LY + nz * LZ - 0.45))
    return mix(mix(cs, cl, 0.35), cl, l)


def coords(X, Y):
    a = BIG if S0 <= X < S1 else (X if X < 54 else CAN - X)
    b = BIG if S0 <= Y < S1 else (Y if Y < 54 else CAN - Y)
    return a, b, (0 if X < 54 else 1) + (0 if Y < 54 else 2)


def boxd(a, b, inset, R, ci):
    """depth inside a rounded box (inset from the canvas edge, corner radius R) + outward canvas unit vector"""
    sx, sy = ORI[ci]
    ax, by = a - inset, b - inset
    if ax < R and by < R:
        dx, dy = R - ax, R - by; h = math.hypot(dx, dy)
        if h < 1e-6: return R, (-sx * 0.707, -sy * 0.707)
        return R - h, (-sx * dx / h, -sy * dy / h)
    if ax < by: return ax, (-sx, 0.0)
    return by, (0.0, -sy)


def corner_fade(a, b):
    """1 deep inside a corner patch, 0 at its inner boundary (48) - ornaments must vanish before the stretch strip"""
    if a >= 48 or b >= 48: return 0.0
    return 1.0 - smooth(39.0, 46.5, max(a, b))


def panel_fill(acc, d, d0, m, alpha=0.95, rim=0.42):
    if d < d0 - 1.5: return
    al = alpha * smooth(d0 - 1.5, d0 + 1.0, d)
    c = mix(m["panel"], m["glow"], rim * math.exp(-max(0.0, d - d0) / 2.2))
    over(acc, c, al)


# ================================================================ APPROACH 1: CLOUD FRAME
# a thick soft cloud rim (two rolled cloud "tubes" along the stretched edges - depth-only, so they stretch cleanly; real round puffs
# only in the 48 px corners), a watercolour glow halo, a flat twilight-blue text panel; the mood (sun / storm / night) sits in the
# corner puffs.
PUFFS = {0: [(27, 12, 10.5), (12, 28, 10.5), (26, 27, 9.0), (39, 9, 6.5), (9, 39, 6.5), (37, 22, 6.0), (22, 37, 6.0)],
         1: [(17, 17, 13.0), (33, 10, 9.0), (10, 33, 9.0), (31, 27, 7.0), (27, 31, 7.0), (41, 8, 5.0), (8, 41, 5.0)],
         2: [(17, 18, 12.5), (32, 11, 9.5), (11, 32, 8.5), (30, 27, 7.5), (25, 33, 6.0), (41, 9, 5.0), (8, 41, 5.0)],
         3: [(18, 17, 13.0), (33, 9, 8.5), (10, 32, 9.5), (28, 29, 7.0), (34, 23, 6.0), (41, 7, 5.0), (7, 41, 5.0)]}
SPARK1 = {0: [(42, 30, 3.6), (30, 42, 3.0), (5, 5, 2.6)], 1: [(4, 4, 3.0), (40, 34, 3.2), (34, 41, 2.6)],
          2: [(40, 36, 3.2), (4, 4, 2.6), (43, 22, 2.4)], 3: [(38, 38, 3.4), (4, 4, 2.6), (22, 43, 2.4)]}


def cloud_sample(rid, a, b, ci):
    m = MOOD[rid]; fx = m["fx"]; sx, sy = ORI[ci]
    acc = [0.0, 0.0, 0.0, 0.0]
    d, (ox, oy) = boxd(a, b, 3, 24, ci)
    cf = corner_fade(a, b)
    cl, cs = m["cl"], m["cs"]
    if "night" in fx: cl = mix(cl, m["moon"], 0.25)
    if d < 0:                                          # watercolour halo (stronger in the corners)
        over(acc, mix(m["glow"], m["sky1"], 0.4), (0.35 + 0.3 * cf) * math.exp(d / 2.5))
    if cf > 0:                                         # corner sky behind the puffs
        if "sun" in fx and ci == (2 if "low" in fx else 0):
            paint_sun(acc, sx * (a - 11), sy * (b - 11), 8.5 if "rays" in fx else 7.5, m["sun"], "rays" in fx)
        if "aurora" in fx and ci < 2:
            yy = 5 + 2.5 * math.sin(a * 0.22 + ci)
            over(acc, mix((90, 255, 160), (120, 220, 255), a / 48.0), 0.55 * cf * math.exp(-((b - yy) ** 2) / 6.0))
    # two rolled cloud tubes along every edge (depth-only)
    for (d0, d1, dark) in ((-1.0, 12.0, 0.0), (9.0, 23.0, 0.12)):
        if d0 <= d <= d1:
            s = 1 - 2 * (d - d0) / (d1 - d0)
            nz = math.sqrt(max(0.0, 1 - s * s))
            c = mix(soft_shade(s * ox, s * oy, nz, cl, cs), cs, dark)
            c = mul(c, 1 - 0.035 * (0.5 + 0.5 * math.sin(d * 2.1)))        # faint flowing streaks
            over(acc, c, clamp01((d - d0) * 1.4) * clamp01((d1 - d) * 1.2))
    panel_fill(acc, d, 22.0, m, 0.98, 0.42)
    if cf > 0:
        puffs = PUFFS[ci]
        sc = 1.1 if "storm" in fx else 1.0
        for (pa, pb, r) in puffs:
            r2 = r * sc
            dd = math.hypot(a - pa, b - pb)
            if dd > r2 + 1: continue
            nx, ny = sx * (a - pa) / r2, sy * (b - pb) / r2
            nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            c = soft_shade(nx, ny, nz, cl, cs)
            if "night" in fx: c = add(c, m["moon"], 0.6 * (1 - nz) ** 2)
            if "ember" in fx: c = add(c, (255, 150, 60), 0.35 * (1 - nz) ** 2)
            over(acc, c, clamp01((r2 - dd) / 1.8 + 0.3) * clamp01(cf * 1.6))
        if "night" in fx:                        # clouds part: a galaxy hole; the purple moon in the top right
            hr = 12.5 if ci == 1 else 10.0
            dd = math.hypot(a - 19, b - 19)
            if dd < hr + 5:
                over(acc, m["moon"], 0.75 * cf * math.exp(-abs(dd - hr) / 1.6))
                g = galaxy(sx * a + 300 * (ci & 1), sy * b + 300 * (ci >> 1))
                over(acc, g, clamp01(hr - dd + 0.5) * cf)
                if ci == 1: paint_moon(acc, sx * (a - 18), sy * (b - 18), 7.0, m["moon"])
        if "bolt" in fx and ci in (1, 2):
            pts = [(15, 5), (22, 16), (17, 19), (28, 31), (22, 33), (33, 44)]
            paint_bolt(acc, sx * a, sy * b, [(sx * p, sy * q) for p, q in pts], m["bolt"], m["glow"], 0.9)
        if "ember" in fx:
            for k in range(6):
                ex, ey = 4 + 38 * h3(ci, k, 1), 4 + 38 * h3(ci, k, 2)
                dd = math.hypot(a - ex, b - ey)
                if dd < 5: over(acc, mix((255, 120, 20), (255, 230, 120), 0.4), cf * (0.95 * math.exp(-dd * dd / 1.0) + 0.3 * math.exp(-dd / 1.8)))
        for (pa, pb, s) in SPARK1[ci]:
            v = sparkle(sx * (a - pa), sy * (b - pb), s * (1.3 if "night" in fx else 1.0))
            if v > 0: over(acc, mix(m["glow"], WHITE, 0.65), v * cf)
    return acc


# ================================================================ APPROACH 2: SKY WINDOW
# a thin ornate gold frame (emblem gold) with a soft sky ribbon between two gold lines, a flat deep-sky panel; each corner is a round
# gold-ringed WINDOW onto a tiny sky scene that carries the rarity mood (corners never stretch, so the scenes stay crisp), with a
# glowing gold star point aimed at the corner.
MED_C, MED_R = 22.0, 19.0
WIN_R = MED_R - 3.4


def window_scene(rid, u, v, ci, rw=WIN_R):
    """u, v in -1..1 inside the window (v down, u mirrored so the scene faces the box centre) -> RGBA acc"""
    m = MOOD[rid]; fx = m["fx"]
    acc = [0.0, 0.0, 0.0, 0.0]
    if "night" in fx:
        over(acc, galaxy(u * rw + 40 * ci, v * rw + 7 * ci), 1.0)
    else:
        over(acc, mix(m["sky0"], m["sky1"], (v + 1) / 2), 1.0)
    if ci < 2:
        if "night" in fx and ci == 1: paint_moon(acc, (u + 0.05) * rw, (v + 0.1) * rw, rw * 0.36, m["moon"])
        elif "sun" in fx and "low" not in fx: paint_sun(acc, (u + 0.15) * rw, (v + 0.2) * rw, rw * 0.27, m["sun"], "rays" in fx)
        if "aurora" in fx:
            yy = -0.35 + 0.18 * math.sin(u * 4 + ci)
            over(acc, mix((90, 255, 160), (130, 220, 255), (u + 1) / 2), 0.7 * math.exp(-((v - yy) ** 2) / 0.02))
        if "storm" in fx:
            q = 0.15 * math.sin(u * 7) - 0.2
            if v < q: over(acc, cloud_shade(0, -0.4, 0.9, m["cl"], m["cs"]), clamp01((q - v) * rw + 0.5))
            paint_bolt(acc, u * rw, v * rw, [(-2, -3), (1, 1), (-1, 2), (3, 8), (1, 8.5), (4, 13)], m["bolt"], m["glow"], 0.7)
        if "puffs" in fx:
            for (pu, pv, pr) in ((-0.3, 0.05, 0.3), (0.15, -0.1, 0.25)):
                dd = math.hypot(u - pu, v - pv)
                if dd < pr: over(acc, mix(m["cs"], m["cl"], 0.5 + 0.5 * (pv - v) / pr), clamp01((pr - dd) * rw))
    else:
        if "low" in fx: paint_sun(acc, (u - 0.25) * rw, (v - 0.05) * rw, rw * 0.33, m["sun"], False)
        ix, iy = u + 0.1, v + 0.05                     # a tiny floating isle + waterfall over a cloud sea
        if -0.55 < ix < 0.5 and -0.12 < iy < 0.55 - abs(ix) * 0.7:
            c = m["grass"] if iy < 0.02 else mix((120, 92, 70), (70, 56, 60), (iy + 0.1) / 0.6)
            if "night" in fx: c = mul(c, 0.6)
            over(acc, c, 1.0)
        if 0.38 < ix < 0.5 and 0.0 < iy < 0.8:
            over(acc, mix(m["water"], WHITE, 0.3 * (0.5 + 0.5 * math.sin(iy * 40))), 0.95)
        if "storm" in fx:
            q = (u * 0.5 + v * rw * 0.25) % 1.0
            over(acc, mix(m["cl"], m["glow"], 0.3), 0.3 * clamp01(1 - abs(q - 0.5) * 8))
    q = 0.55 + 0.1 * math.sin(u * 6 + ci * 2) + 0.06 * math.sin(u * 13)          # cloud sea
    if v > q - 0.04:
        lit = clamp01(1 - (v - q) * 3)
        c = mix(m["cs"], m["cl"], 0.35 + 0.65 * lit)
        if "night" in fx: c = add(c, m["moon"], 0.3 * lit)
        over(acc, c, clamp01((v - q + 0.04) * 20))
    for k in range(3):
        px, py = -0.6 + 1.2 * h3(ci, k, 7), -0.7 + 1.0 * h3(ci, k, 8)
        s = sparkle((u - px) * rw, (v - py) * rw, 2.4)
        if s > 0: over(acc, mix(m["glow"], WHITE, 0.6), s)
    return acc


def window_sample(rid, a, b, ci):
    m = MOOD[rid]; fx = m["fx"]; sx, sy = ORI[ci]
    acc = [0.0, 0.0, 0.0, 0.0]
    d, (ox, oy) = boxd(a, b, 6, 4, ci)
    cf = corner_fade(a, b)
    night = "night" in fx
    ring = (210, 200, 255) if night else GOLD
    ring_d, ring_l = ((90, 60, 140), (255, 236, 255)) if night else (GOLD_D, GOLD_L)
    if d < 0: over(acc, mul(m["panel"], 0.6), 0.35 * math.exp(d / 3.0))

    def tube(d0, d1):
        if d0 - 0.5 <= d <= d1 + 0.5:
            s = max(-1.0, min(1.0, 1 - 2 * (d - d0) / (d1 - d0))); nz = math.sqrt(max(0.0, 1 - s * s))
            l = clamp01(0.3 + 0.9 * (s * ox * LX + s * oy * LY + nz * LZ))
            over(acc, mix(ring_d, ring_l, l), clamp01((d - d0 + 0.5) * 2) * clamp01((d1 + 0.5 - d) * 2))
    if 2.5 < d < 10:                                   # sky ribbon between the gold lines (depth gradient = stretches cleanly)
        t = (d - 2.5) / 7.5
        c = mix(mix(m["sky1"], WHITE, 0.25), m["sky0"], t) if not night else mix((120, 70, 190), (40, 16, 80), t)
        over(acc, c, 1.0)
    tube(0.0, 2.8)
    tube(9.6, 11.2)
    if 11.2 < d < 14.0: over(acc, mul(m["panel"], 0.7), 0.98)
    if 12.4 <= d <= 13.4: over(acc, m["glow"], 0.9 * clamp01(min(d - 12.4, 13.4 - d) * 3 + 0.3))
    panel_fill(acc, d, 13.6, m, 0.98, 0.25)
    if cf > 0:
        dd = math.hypot(a - MED_C, b - MED_C)
        if MED_R - 1 < dd < MED_R + 10:
            over(acc, mix(m["glow"], GOLD_L, 0.3), 0.6 * cf * math.exp(-(dd - MED_R) / 3.0))
        # star point aimed at the canvas corner ("the thing on top glowed")
        dpt = (MED_C - a + MED_C - b) / math.sqrt(2); per = abs(a - b) / math.sqrt(2)
        L = MED_R + 9.0
        if MED_R - 2 < dpt < L and per < (L - dpt) * 0.45:
            c = mix(ring_l, ring, clamp01(per / 2.5)) if (a - b) * sx * sy >= 0 else mix(ring, ring_d, 0.35)
            over(acc, c, clamp01(((L - dpt) * 0.45 - per) * 2) * cf)
        tp = MED_C - (L - 1) / math.sqrt(2)
        v = sparkle(sx * (a - tp), sy * (b - tp), 5.5)
        if v > 0: over(acc, mix(m["glow"], WHITE, 0.7), 0.9 * v * cf)
        if WIN_R - 0.2 <= dd <= MED_R + 0.6:             # bevelled ring
            s = max(-1.0, min(1.0, (dd - (MED_R - 1.4)) / 1.8))
            nxr, nyr = sx * (a - MED_C) / max(dd, 1e-6), sy * (b - MED_C) / max(dd, 1e-6)
            nz = math.sqrt(max(0.0, 1 - s * s))
            l = clamp01(0.3 + 0.9 * (s * nxr * LX + s * nyr * LY + nz * LZ))
            over(acc, mix(ring_d, ring_l, l), clamp01(min(dd - (WIN_R - 0.2), MED_R + 0.6 - dd) * 2.5) * cf)
        if dd < WIN_R + 0.5:
            v2 = sy * (b - MED_C) / WIN_R
            u = (a - MED_C) / WIN_R                      # local: + toward the box centre, so every scene faces inward
            sc = window_scene(rid, u, v2, ci)
            over(acc, sc[:3], sc[3] * clamp01((WIN_R + 0.5 - dd) * 2.5) * clamp01(cf * 1.5))
    return acc


# ================================================================ APPROACH 3: WATERCOLOUR SWIRL
# no hard frame: a pale watercolour sky wash whose stretched edges become flowing streaks (depth-only bands = wind lines),
# corner pigment blooms with darker watercolour edges, glowing magic swirls + sparkles, and a soft translucent ink-pool panel.
def spiral(lx, ly, k, rmin, rmax, w):
    r = math.hypot(lx, ly)
    if r < rmin * 0.6 or r > rmax + w + 1: return 0.0
    th = math.atan2(ly, lx) % (2 * math.pi)
    n = round((r / k - th) / (2 * math.pi))
    best = 1e9
    for nn in (n - 1, n, n + 1):
        rs = k * (th + 2 * math.pi * nn)
        if rmin * 0.6 <= rs <= rmax: best = min(best, abs(r - rs))
    if best > 50: return 0.0
    ww = w * (0.35 + 0.65 * clamp01((r - rmin * 0.6) / (rmax - rmin * 0.6)))
    return clamp01(ww - best + 0.5)


SWIRLS = {0: [(19, 19, 1.7, 3, 18, 1.5), (38, 10, 0.95, 1.5, 7, 1.0)], 1: [(19, 18, 1.6, 3, 17, 1.5), (10, 37, 0.95, 1.5, 7, 1.0)],
          2: [(18, 19, 1.6, 3, 17, 1.5), (37, 11, 0.95, 1.5, 7, 1.0)], 3: [(19, 19, 1.7, 3, 18, 1.5), (11, 38, 0.95, 1.5, 7, 1.0)]}


def water_sample(rid, a, b, ci):
    m = MOOD[rid]; fx = m["fx"]; sx, sy = ORI[ci]
    acc = [0.0, 0.0, 0.0, 0.0]
    d, (ox, oy) = boxd(a, b, 2, 26, ci)
    cf = corner_fade(a, b)
    paper = (250, 247, 238)
    soft = "storm" not in fx and "night" not in fx
    wash = mix(m["sky1"], paper, 0.45) if soft else mix(m["sky1"], m["cl"], 0.35)
    if -1.5 <= d < 31:
        streak = 0.5 + 0.5 * math.sin(d * 0.95 + 1.0) * math.sin(d * 0.37)
        c = mix(wash, m["sky0"], 0.10 + 0.24 * streak)
        al = 0.84 * smooth(-1.5, 3.0, d)
        al = min(1.0, al + 0.18 * math.exp(-max(0.0, d) / 1.3))         # pigment edge (watercolour dries darker at the rim)
        c = mix(c, m["sky0"], 0.35 * math.exp(-max(0.0, d) / 1.5))
        over(acc, c, al)
    if cf > 0:
        for (ba, bb, br, col, kk) in ((18, 18, 19, m["glow"], 0), (37, 9, 9, m["sky0"], 1), (9, 37, 9, m["sky0"], 2)):
            dd = math.hypot(a - ba, b - bb)
            rr = br * (0.82 + 0.36 * fbm(a * 0.13 + 9 * ci + kk, b * 0.13 + 4 * kk))
            if dd < rr + 1:
                inside = clamp01(rr - dd + 0.5)
                if "night" in fx and kk == 0:
                    over(acc, galaxy(sx * a + 200 * ci, sy * b), 0.97 * inside * cf)
                    over(acc, m["moon"], 0.6 * smooth(rr - 3.5, rr, dd) * inside * cf)
                else:
                    over(acc, mix(col, WHITE, 0.15), (0.30 + 0.40 * smooth(rr - 3.5, rr, dd)) * inside * cf)
        if "night" in fx and ci == 1: paint_moon(acc, sx * (a - 18), sy * (b - 18), 7.0, m["moon"])
        if "sun" in fx and ci == (2 if "low" in fx else 0): paint_sun(acc, sx * (a - 16), sy * (b - 16), 7.5, m["sun"], "rays" in fx)
        for (pa, pb, k, rmin, rmax, w) in SWIRLS[ci]:
            lx, ly = sx * (a - pa), sy * (b - pb)
            if ci in (1, 2): lx = -lx
            if math.hypot(lx, ly) < rmax + 7:
                over(acc, m["glow"], 0.38 * spiral(lx, ly, k, rmin, rmax, w + 3.0) * cf)
                v = spiral(lx, ly, k, rmin, rmax, w)
                if v > 0: over(acc, mix(m["glow"], WHITE, 0.55), v * cf)
        if "bolt" in fx and ci in (1, 2):
            pts = [(10, 4), (17, 14), (12, 17), (23, 29), (18, 31), (28, 43)]
            paint_bolt(acc, sx * a, sy * b, [(sx * p, sy * q) for p, q in pts], m["bolt"], m["glow"], 0.8)
        if "aurora" in fx and ci < 2:
            yy = 5 + 2.5 * math.sin(a * 0.25 + ci)
            over(acc, mix((90, 255, 160), (120, 220, 255), a / 48.0), 0.5 * cf * math.exp(-((b - yy) ** 2) / 5.0))
        if "ember" in fx:
            for k in range(7):
                ex, ey = 4 + 38 * h3(ci, k, 11), 4 + 38 * h3(ci, k, 12)
                dd = math.hypot(a - ex, b - ey)
                if dd < 5: over(acc, (255, 196, 80), cf * (0.95 * math.exp(-dd * dd / 0.9) + 0.25 * math.exp(-dd / 1.7)))
        for k in range(5):
            pa, pb = 3 + 40 * h3(ci, k, 21), 3 + 40 * h3(ci, k, 22)
            if min(pa, pb) > 30: continue
            v = sparkle(sx * (a - pa), sy * (b - pb), 2.2 + 1.8 * h3(ci, k, 23))
            if v > 0: over(acc, mix(m["glow"], WHITE, 0.7), v * cf)
    if d > 24:                                         # soft translucent ink pool (feathered, no line)
        al = 0.98 * smooth(24, 30, d)
        c = mix(m["panel"], m["glow"], 0.22 * math.exp(-max(0.0, d - 26) / 2.5))
        over(acc, c, al)
    return acc


# ================================================================ APPROACH 4: FLOATING ISLE
# a soft sky-blue rim + thin gold line; tiny floating islands with waterfalls hang off the bottom corners (like the menu emblem),
# a glowing gold compass star top left, the mood's sky object (sun / storm cloud / purple moon) top right.
def star8(dx, dy, R):
    r = math.hypot(dx, dy)
    if r > R: return None
    ang = math.atan2(dy, dx)
    t = abs(((ang + math.pi / 8) % (math.pi / 4)) - math.pi / 8) / (math.pi / 8)     # 0 at a point, 1 between
    idx = int(math.floor((ang + math.pi / 8) / (math.pi / 4))) % 2
    tipR = R if idx == 0 else R * 0.55
    lim = tipR * (1 - t) + R * 0.2 * t
    if r > lim: return None
    side = ((ang + math.pi / 8) % (math.pi / 4)) < math.pi / 8
    c = GOLD_L if side else GOLD
    if r < R * 0.2: c = (150, 220, 255)
    return c, clamp01(lim - r + 0.5)


def isle_sample(rid, a, b, ci):
    m = MOOD[rid]; fx = m["fx"]; sx, sy = ORI[ci]
    acc = [0.0, 0.0, 0.0, 0.0]
    d, (ox, oy) = boxd(a, b, 6, 12, ci)
    cf = corner_fade(a, b)
    night = "night" in fx
    if d < 0: over(acc, mul(m["sky0"], 0.5), 0.3 * math.exp(d / 3.0))
    rim_l = mix(m["sky1"], WHITE, 0.45); rim_d = mix(m["sky0"], m["panel"], 0.25)
    if -0.6 <= d <= 9.0:
        s = 1 - 2 * (d + 0.6) / 9.6; nz = math.sqrt(max(0.0, 1 - s * s))
        l = clamp01(0.25 + 0.9 * (s * ox * LX + s * oy * LY + nz * LZ))
        c = mix(rim_d, rim_l, l)
        c = mul(c, 1 - 0.04 * (0.5 + 0.5 * math.sin(d * 2.4)))
        if d < 0.6: c = mul(rim_d, 0.7)
        over(acc, c, clamp01((d + 0.6) * 2) * clamp01((9.0 - d) * 2))
    if 9.0 < d <= 10.6: over(acc, GOLD if not night else (214, 170, 255), 0.97)
    panel_fill(acc, d, 10.6, m, 0.98, 0.35)
    if cf > 0:
        if ci == 0:                          # glowing compass star (menu-emblem homage)
            dx, dy = a - 19, b - 19
            r = math.hypot(dx, dy)
            over(acc, mix(GOLD_L, m["glow"], 0.4), 0.7 * cf * math.exp(-max(0.0, r - 5) / 6.0))
            st = star8(dx, dy, 15.5)
            if st: over(acc, st[0], st[1] * cf)
            v = sparkle(a - 35, b - 7, 3.6)
            if v > 0: over(acc, WHITE, v * cf)
        elif ci == 1:                        # the mood's sky object
            dx, dy = -(a - 19), b - 19
            if night:
                hd = math.hypot(a - 19, b - 19)
                over(acc, m["moon"], 0.6 * cf * math.exp(-max(0.0, hd - 15) / 2.2))
                over(acc, galaxy(a + 50.0, b * 1.0), clamp01(15 - hd) * cf)
                paint_moon(acc, dx, dy, 7.5, m["moon"])
            elif "storm" in fx:
                for (pa, pb, r) in ((16, 15, 9), (28, 13, 7.5), (22, 8, 7), (8, 22, 6), (31, 22, 5)):
                    dd = math.hypot(a - pa, b - pb)
                    if dd < r + 1:
                        nx, ny = -(a - pa) / r, (b - pb) / r; nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                        over(acc, cloud_shade(nx, ny, nz, m["cl"], m["cs"]), clamp01(r - dd + 0.5) * cf)
                paint_bolt(acc, -a, b, [(-18, 22), (-14, 29), (-18, 31), (-13, 41), (-17, 42), (-12, 47)], m["bolt"], m["glow"], 0.9)
            elif "low" in fx:
                paint_sun(acc, dx, dy, 9.0, m["sun"], False)
            else:
                paint_sun(acc, dx, dy, 8.0 if "rays" not in fx else 9.0, m.get("sun", (255, 240, 200)), "rays" in fx)
                if "aurora" in fx:
                    yy = 5 + 2.5 * math.sin(a * 0.22)
                    over(acc, (110, 255, 170), 0.5 * cf * math.exp(-((b - yy) ** 2) / 5.0))
            if "puffs" in fx or "ember" in fx:
                for (pa, pb, r) in ((26, 27, 8), (36, 19, 6.5)):
                    dd = math.hypot(a - pa, b - pb)
                    if dd < r + 1:
                        nx, ny = -(a - pa) / r, (b - pb) / r; nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                        over(acc, cloud_shade(nx, ny, nz, m["cl"], m["cs"]), clamp01(r - dd + 0.5) * cf)
        else:                                # bottom corners: floating isle + waterfall (local x = a inward, h = b up)
            x, h = a, b
            if 9.0 <= x <= 13.0 and 1 <= h <= 34:          # waterfall off the outer side, mist + sparkle at the bottom
                ripple = 0.5 + 0.5 * math.sin(h * 1.4 + x * 0.9)
                over(acc, mix(m["water"], WHITE, 0.4 * ripple), 0.93 * cf)
            mh = math.hypot(x - 11, (h - 3) * 1.4)
            if mh < 9: over(acc, mix(m["water"], WHITE, 0.6), 0.6 * cf * math.exp(-mh / 3.0))
            v = sparkle(x - 18, h - 5, 3.2)
            if v > 0: over(acc, WHITE, v * cf)
            cx = 24.0
            if 12 <= h <= 34:                                # rock underside (stepped cone)
                st = math.floor((h - 11) / 23.0 * 5 + 0.6) / 5.0
                half = 14.0 * max(0.12, st) ** 0.85 - 1.5 * (int(h) % 2 == 0 and h < 20)
                if abs(x - cx - 1.5 * (st < 0.5)) < half:
                    t = (34 - h) / 22.0
                    c = mix((156, 122, 92), (72, 58, 76), t)
                    if int(h) % 5 == 0: c = mul(c, 0.86)
                    if abs(x - cx) > half - 1.2: c = mul(c, 0.75)
                    if night: c = mix(c, (60, 36, 96), 0.5)
                    over(acc, c, clamp01((half - abs(x - cx - 1.5 * (st < 0.5))) * 1.5) * cf)
            if 33 <= h <= 38.5 and abs(x - cx) < 15:          # soil + grass cap
                c = m["grass"] if h > 35 else mix(m["grass"], (110, 80, 50), 0.55)
                c = mix(c, WHITE, 0.3 * clamp01(h - 37.5))
                over(acc, c, clamp01((15 - abs(x - cx)) * 1.5) * cf)
                if "flower" in m and int(x * 3) % 5 == 0 and h > 37: over(acc, m["flower"], cf)
            dl = math.hypot(x - 30, h - 37.5)                 # one glowing crystal / bush on top
            if dl < 6: over(acc, mix(m["glow"], WHITE, 0.4), 0.4 * cf * math.exp(-dl / 2.0))
            if dl < 2.6: over(acc, mix(m["grass"], WHITE, 0.35) if not night else (236, 186, 255), clamp01(2.6 - dl) * cf)
            dw = math.hypot((x - 34) * 0.5, h - 12)          # cloud wisp under the island
            if dw < 3.5: over(acc, mix(m["cl"], WHITE, 0.3), 0.8 * clamp01(3.5 - dw) * cf)
    return acc


APPROACHES = [("cloud", "1  CLOUD FRAME", cloud_sample), ("window", "2  SKY WINDOW", window_sample),
              ("water", "3  WATERCOLOUR SWIRL", water_sample), ("isle", "4  FLOATING ISLE", isle_sample)]
SAMPLERS = {k: f for k, _n, f in APPROACHES}


# ---------------------------------------------------------------- slots (148 @2x, scaled whole - free art, but icon covers 128 px centre)
def slot_sample(app, rid, X, Y):
    m = MOOD[rid]; fx = m["fx"]
    acc = [0.0, 0.0, 0.0, 0.0]
    # box depth for a full-size rounded square
    a = min(X, SLOT - X); b = min(Y, SLOT - Y)
    ci = (0 if X < SLOT / 2 else 1) + (0 if Y < SLOT / 2 else 2)
    sx, sy = ORI[ci]
    v = Y / SLOT
    night = "night" in fx
    if app == "cloud":
        d, (ox, oy) = boxd(a, b, 3, 22, ci)
        if d < 0: return acc
        fill = mix(mix(m["sky0"], m["panel"], 0.35), mix(m["sky1"], m["panel"], 0.55), v)
        if night: fill = mix(galaxy(X * 0.7, Y * 0.7), m["panel"], 0.35)
        over(acc, fill, clamp01(d * 2))
        over(acc, m["glow"], 0.45 * math.exp(-max(0.0, d - 7) / 3.0) * clamp01(d - 5))
        if d <= 7:
            s = 1 - 2 * d / 7.0; nz = math.sqrt(max(0.0, 1 - s * s))
            over(acc, cloud_shade(s * ox, s * oy, nz, m["cl"], m["cs"]), clamp01(d * 2) * clamp01((7 - d) * 1.5))
        for (pa, pb, r) in ((22, 10, 12), (44, 6, 9), (8, 26, 9)):
            if ci < 2: continue
            dd = math.hypot(a - pa, b - pb)
            if dd < r + 1:
                nx, ny = sx * (a - pa) / r, sy * (b - pb) / r; nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                c = cloud_shade(nx, ny, nz, m["cl"], m["cs"])
                if night: c = add(c, m["moon"], 0.5 * (1 - nz) ** 2)
                over(acc, c, clamp01(r - dd + 0.5))
        if "bolt" in fx and ci == 1:
            paint_bolt(acc, -a, b, [(-14, 8), (-20, 18), (-16, 20), (-24, 34)], m["bolt"], m["glow"], 0.9)
        if night and ci == 1: paint_moon(acc, -(a - 26), b - 26, 9, m["moon"])
        if "sun" in fx and ci == 0: paint_sun(acc, a - 24, b - 24, 9, m["sun"], "rays" in fx)
    elif app == "window":
        d, (ox, oy) = boxd(a, b, 4, 5, ci)
        if d < 0: return acc
        sc = window_scene(rid, (X / SLOT) * 2 - 1, (Y / SLOT) * 2 - 1, 0 if X < 90 else 1)
        over(acc, mul(sc[:3], 0.72), 1.0)
        vig = math.hypot(X - SLOT / 2, Y - SLOT / 2) / (SLOT / 2)
        over(acc, m["panel"], 0.25 + 0.25 * (1 - vig))
        if d <= 4.5:
            s = 1 - 2 * d / 4.5; nz = math.sqrt(max(0.0, 1 - s * s))
            l = clamp01(0.3 + 0.9 * (s * ox * LX + s * oy * LY + nz * LZ))
            over(acc, mix(GOLD_D, GOLD_L, l), clamp01(d * 2) * clamp01((4.5 - d) * 2))
        if 6 <= d <= 7.4: over(acc, m["glow"], 0.85)
        ds = abs(a - 9) + abs(b - 9)
        if ds < 7: over(acc, mix(GOLD_L, GOLD, ds / 7), clamp01((7 - ds) * 2))
        if ds < 14: over(acc, mix(m["glow"], WHITE, 0.6), 0.6 * sparkle(sx * (a - 9), sy * (b - 9), 9))
    elif app == "water":
        d, (ox, oy) = boxd(a, b, 3, 30, ci)
        if d < -2: return acc
        over(acc, mix(m["sky1"], (250, 247, 238), 0.4) if not night and "storm" not in fx else mix(m["sky1"], m["cl"], 0.3),
             0.85 * smooth(-2, 3, d))
        over(acc, m["sky0"], 0.3 * math.exp(-max(0.0, d) / 1.5) * smooth(-2, 0, d))
        rr = 30 * (0.85 + 0.3 * fbm(X * 0.05 + ci, Y * 0.05))
        dd = math.hypot(a - 20, b - 20)
        if ci in (0, 3) and dd < rr:
            if night: over(acc, galaxy(X * 0.6, Y * 0.6), 0.95)
            else: over(acc, m["glow"], 0.35 + 0.35 * smooth(rr - 5, rr, dd))
        pool = 0.88 * smooth(16, 30, d)
        over(acc, m["panel"], pool)
        if ci == 0:
            v2 = spiral(a - 22, b - 22, 2.2, 4, 18, 1.8)
            over(acc, m["glow"], 0.35 * spiral(a - 22, b - 22, 2.2, 4, 18, 4.5))
            over(acc, mix(m["glow"], WHITE, 0.55), v2)
        if night and ci == 3: paint_moon(acc, -(a - 22), -(b - 22), 9, m["moon"])
        if "bolt" in fx and ci == 3: paint_bolt(acc, -a, -b, [(-12, -40), (-20, -28), (-15, -26), (-24, -12)], m["bolt"], m["glow"], 0.9)
        for k in range(3):
            px, py = 10 + 128 * h3(k, 3, 31), 10 + 128 * h3(k, 3, 32)
            s = sparkle(X - px, Y - py, 4.0)
            if s > 0: over(acc, WHITE, s * 0.9)
    else:  # isle
        d, (ox, oy) = boxd(a, b, 3, 14, ci)
        if d < 0: return acc
        fill = mix(mix(m["sky0"], m["panel"], 0.3), mix(m["sky1"], m["panel"], 0.5), v)
        if night: fill = mix(galaxy(X * 0.7, Y * 0.7), m["panel"], 0.3)
        over(acc, fill, 1.0)
        if d <= 7:
            s = 1 - 2 * d / 7.0; nz = math.sqrt(max(0.0, 1 - s * s))
            l = clamp01(0.25 + 0.9 * (s * ox * LX + s * oy * LY + nz * LZ))
            over(acc, mix(mix(m["sky0"], m["panel"], 0.25), mix(m["sky1"], WHITE, 0.45), l), clamp01(d * 2) * clamp01((7 - d) * 2))
        if 7 < d <= 9: over(acc, GOLD if not night else (214, 170, 255), 0.95)
        if ci == 0:
            st = star8(a - 20, b - 20, 14)
            r = math.hypot(a - 20, b - 20)
            over(acc, mix(GOLD_L, m["glow"], 0.4), 0.5 * math.exp(-max(0.0, r - 4) / 6.0))
            if st: over(acc, st[0], st[1])
        if ci == 3:
            x, h = a, b
            if 12 <= x <= 16 and 4 <= h <= 30: over(acc, mix(m["water"], WHITE, 0.3 * (0.5 + 0.5 * math.sin(h * 1.2))), 0.9)
            cx = 30
            if 16 <= h <= 30:
                half = 15 * ((h - 14) / 16.0) ** 0.8 if h > 14 else 0
                if abs(x - cx) < half: over(acc, mix((150, 118, 90), (70, 58, 74), (30 - h) / 16), clamp01((half - abs(x - cx)) * 1.5))
            if 30 <= h <= 35 and abs(x - cx) < 16:
                over(acc, m["grass"] if h > 31.5 else mix(m["grass"], (110, 80, 50), 0.5), clamp01((16 - abs(x - cx)) * 1.5))
    return acc


# ---------------------------------------------------------------- rendering
def render(fn, w, h, unit, ss):
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
            row.append([r / al, g / al, bl / al, al / n * 255.0] if al > 0 else [0, 0, 0, 0])
        img.append(row)
    return img


def job(args):
    app, rid = args
    f = SAMPLERS[app]
    tip = render(lambda X, Y: f(rid, *coords(X, Y)), CAN, CAN, 1.0, SS_TIP)
    tip = [r[:54] + r[55:] for i, r in enumerate(tip) if i != 54]            # 108 -> 107, strip 48..58
    slot = render(lambda X, Y: slot_sample(app, rid, X, Y), SLOT, SLOT, 1.0, SS_SLOT)
    tip = [[[int(round(v)) for v in p] for p in r] for r in tip]
    slot = [[[int(round(v)) for v in p] for p in r] for r in slot]
    return app, rid, tip, slot


def check_strip(img):
    for y in range(107):
        row = img[y]
        for x in range(49, 59):
            if row[x] != row[48]: return False
    for x in range(107):
        for y in range(49, 59):
            if img[y][x] != img[48][x]: return False
    return True


# ---------------------------------------------------------------- contrast
def lum(c):
    def ch(v):
        v /= 255.0; return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def contrast(c1, c2):
    l1, l2 = lum(c1), lum(c2); hi, lo = max(l1, l2), min(l1, l2); return (hi + 0.05) / (lo + 0.05)


TEXT = {"white": (255, 255, 255), "grey": (170, 170, 170), "green": (85, 255, 85), "red": (255, 85, 85), "gold": (255, 170, 0),
        "aqua": (85, 255, 255)}
LIGHT_BG = (206, 228, 246)


def centre_colour(tip):
    p = tip[53][53]; al = p[3] / 255.0
    return tuple(p[k] * al + LIGHT_BG[k] * (1 - al) for k in range(3))


# ---------------------------------------------------------------- sheet
HERO_ROWS = [("name", None), ("Attack Speed: Fast", (170, 170, 170)), ("", None), (("Health", "+120"), (85, 255, 85)),
             (("Strength", "+12"), (85, 255, 85)), (("Crit Chance", "+5%"), (85, 255, 85)), (("Defense", "-3"), (255, 85, 85)),
             ("", None), (("Ability: Thunderclap", "RIGHT CLICK"), "ability"), ("Calls blue lightning on foes", (170, 170, 170)),
             ("within 6 blocks: 250 damage.", (170, 170, 170)), (("Mana Cost:", "40"), "mana"), ("", None),
             ("Can be reforged", (130, 130, 130)), ("type", None)]
MYTH_ROWS = [("name", None), ("Attack Speed: Slow", (170, 170, 170)), ("", None), (("Intelligence", "+40"), (85, 255, 85)),
             (("Mana Regen", "+8/5s"), (85, 255, 85)), ("", None), (("Ability: Starfall", "RIGHT CLICK"), "ability"),
             ("Moonlight rains on your foes.", (170, 170, 170)), ("type", None)]


def game_bg(cv, x, y, w, h, seed=0):
    """a plain 'in-game' backdrop: light day sky + a green island band (shows how a light frame reads on light scenery)"""
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = mix((122, 176, 226), (206, 228, 246), t * 1.4)
        if t > 0.82: c = mix((84, 140, 70), (54, 96, 52), (t - 0.82) / 0.18)
        cv.fill(x, y + yy, x + w, y + yy + 1, c)
    for k in range(5):                       # a few soft background clouds
        cx, cy, r = x + int(w * h3(k, seed, 41)), y + int(h * 0.55 * h3(k, seed, 42)), 26 + int(30 * h3(k, seed, 43))
        for yy in range(-r, r):
            for xx in range(-2 * r, 2 * r):
                q = (xx / 2.0) ** 2 + yy * yy
                if q < r * r and x <= cx + xx < x + w and y <= cy + yy < y + h:
                    cv.over(cx + xx, cy + yy, (250, 252, 255, int(110 * (1 - q / (r * r)))))


def arrow_img(app, rid):
    """simple 66 x 48 @2x mock arrow in the approach's rim colours (concept only)"""
    m = MOOD[rid]
    rim = {"cloud": m["cl"], "window": GOLD, "water": mix(m["sky1"], (250, 247, 238), 0.45), "isle": mix(m["sky1"], WHITE, 0.4)}[app]
    img = P.new(66, 48)
    for y in range(48):
        for x in range(66):
            acc = [0.0, 0.0, 0.0, 0.0]
            for j in range(3):
                for i in range(3):
                    X, Y = x + (i + 0.5) / 3, y + (j + 0.5) / 3
                    q = abs(X - 33); lim = (40 - Y) * 0.8
                    if Y < 40 and q < lim:
                        c = m["panel"] if q < lim - 5 or Y < 6 else rim
                        if Y < 6 and q < lim - 5: c = m["panel"]
                        acc[0] += c[0] / 9; acc[1] += c[1] / 9; acc[2] += c[2] / 9; acc[3] += 1 / 9
            if acc[3] > 0:
                img[y][x] = [acc[0] / acc[3], acc[1] / acc[3], acc[2] / acc[3], acc[3] * 255 * 0.97]
    return img


def draw_text_rows(cv, rows, x, y, W, name, kind, colour, scale=3):
    lh = 9 * scale; tx = x + 48; ty = y + 44
    for item, c in rows:
        if item == "name":
            cv.text(tx, ty, "%s %s" % (name, "Stormcaller" if kind == "sword" else "Voidcaller"), colour, scale, bold=True)
        elif item == "type":
            cv.text(tx, ty, "%s %s" % (name.upper(), "SWORD" if kind == "sword" else "WAND"), colour, scale, bold=True)
        elif isinstance(item, tuple):
            if c == "ability":
                cv.text(tx, ty, item[0], (255, 170, 0), scale)
                cv.text(x + W - 48 - len(item[1]) * 6 * scale, ty, item[1], (255, 255, 85), scale, bold=True)
            elif c == "mana":
                e = cv.text(tx, ty, item[0], (130, 130, 130), scale)
                cv.text(e + 6 * scale, ty, item[1], (85, 255, 255), scale)
            else:
                cv.text(tx, ty, item[0], (230, 230, 230), scale)
                cv.text(x + W - 48 - len(item[1]) * 6 * scale, ty, item[1], c, scale)
        elif item:
            cv.text(tx, ty, item, c, scale)
        ty += lh
    return ty


DESC = {
    "cloud": ["PUFFY SOFT CLOUD RIM, WATERCOLOUR GLOW HALO,", "FLAT TWILIGHT-BLUE TEXT PANEL. THE MOOD LIVES",
              "IN THE CORNER PUFFS (SUN, STORM, GALAXY HOLE)."],
    "window": ["THIN ORNATE GOLD FRAME (EMBLEM GOLD). EACH CORNER", "IS A ROUND WINDOW ONTO A TINY SKY SCENE THAT",
               "CARRIES THE RARITY MOOD. GLOWING GOLD STAR POINTS."],
    "water": ["NO HARD FRAME: A PALE WATERCOLOUR SKY WASH, ITS", "EDGES FLOW AS WIND STREAKS. PIGMENT BLOOMS, MAGIC",
              "SWIRLS + SPARKLES. SOFT TRANSLUCENT INK-POOL PANEL."],
    "isle": ["SOFT SKY-BLUE RIM + GOLD LINE. FLOATING ISLES WITH", "WATERFALLS HANG OFF THE BOTTOM CORNERS, A GLOWING",
             "COMPASS STAR TOP LEFT, THE MOOD'S SKY TOP RIGHT."],
}
LIMITS = {
    "cloud": ["ENGINE: PUFFS ONLY IN THE 4 CORNERS (24 UI EACH);", "THE EDGES ARE SMOOTH CLOUD ROLLS (STRETCHED).",
              "WIDE TOOLTIPS = LONG PLAIN CLOUD RUNS BETWEEN."],
    "window": ["ENGINE: SCENES FIT IN A 13 UI ROUND WINDOW (TINY", "AT 1X). NO TOP-CENTRE CREST POSSIBLE (EDGES", "STRETCH). FRAME LINES STAY CRISP AT ANY SIZE."],
    "water": ["ENGINE: BLOOMS + SWIRLS ONLY IN CORNERS, EDGE", "TEXTURE CAN ONLY RUN ALONG THE EDGE (STREAKS).",
              "SOFT ALPHA EVERYWHERE - NEEDS AN IN-GAME CHECK."],
    "isle": ["ENGINE: ISLES MUST FIT 24 UI CORNERS, WATERFALL", "ENDS AT THE TEXTURE EDGE. THE ARROW (CLIENT-PLACED)",
             "CAN OVERLAP A BOTTOM ISLE ON NARROW TOOLTIPS."],
}


def make_sheet(res, report):
    COLW, GAP, X0 = 780, 34, 30
    W = X0 * 2 + 4 * COLW + 3 * GAP
    H = 2600
    ymax = 0
    cv = TF.Canvas(W, H, (30, 34, 46))
    for y in range(0, H, 40):
        for x in range(0, W, 40):
            if (x // 40 + y // 40) % 2: cv.fill(x, y, x + 40, y + 40, (34, 38, 52))
    cv.text(X0, 18, "SKYWYNN - ISLES OF THE VOID - UI SKY MOCKUPS (CONCEPT, NOT FINAL ASSETS)", (240, 236, 255), 4, bold=True)
    cv.text(X0, 62, "4 APPROACHES. REAL 9-SLICE: 107 PX @2X TEXTURE, 48 PX (24 UI) CORNERS FIXED, EDGES + CENTRE STRETCH. SLOTS 148 PX @2X SCALED WHOLE.",
            (200, 206, 224), 2)
    cv.text(X0, 84, "HERO TOOLTIPS SHOWN 1:1 AT @2X (= UI SCALE 2). RARITY STRIP AT 1X. ALL PIXELS ORIGINAL. GENERATOR: TOOLS/ART/MAKE_UI_SKY_MOCKUPS.PY",
            (160, 166, 186), 2)
    for ai, (app, title, _f) in enumerate(APPROACHES):
        x = X0 + ai * (COLW + GAP); y = 120
        cv.fill(x - 8, y - 8, x + COLW + 8, H - 20, (24, 28, 40))
        cv.text(x, y, title, (255, 236, 170), 4, bold=True); y += 44
        for ln in DESC[app]:
            cv.text(x, y, ln, (214, 220, 236), 2); y += 22
        y += 10
        # hero: Legendary
        tip = res[(app, "legendary")][0]
        tw, th = 720, 488
        game_bg(cv, x, y, COLW, th + 70, ai)
        cv.blit(TF.nine_slice(tip, 48, tw, th), x + 30, y + 16)
        cv.blit(arrow_img(app, "legendary"), x + 30 + 120, y + 16 + th - 32)
        draw_text_rows(cv, HERO_ROWS, x + 30, y + 16, tw, "Legendary", "sword", TF.hx("#55FFFF"))
        y += th + 70 + 8
        cmin, cname = report[app]
        cv.text(x, y, "LEGENDARY @2X 1:1 (360 X 244 UI). LOWEST TEXT CONTRAST", (200, 206, 224), 2)
        cv.text(x, y + 22, "ON ANY RARITY: %.1f:1 (%s TEXT, AA NEEDS 4.5)" % (cmin, cname.upper()), (150, 230, 150) if cmin >= 4.5 else (255, 140, 120), 2)
        y += 52
        # mythic hero
        tip = res[(app, "mythic")][0]
        th2 = 300
        game_bg(cv, x, y, COLW, th2 + 30, ai + 7)
        cv.blit(TF.nine_slice(tip, 48, tw, th2), x + 30, y + 14)
        draw_text_rows(cv, MYTH_ROWS[:3] + MYTH_ROWS[3:5] + MYTH_ROWS[6:8] + [MYTH_ROWS[-1]], x + 30, y + 14, tw, "Mythic", "wand",
                       TF.hx("#CC66CC"), 2)
        y += th2 + 30 + 6
        cv.text(x, y, "MYTHIC @2X 1:1 (NIGHT, CLOUDS PART, PURPLE MOON)", (200, 206, 224), 2); y += 30
        # the raw 107 px @2x textures, x3 - this is ALL the art the client gets (48 px corners fixed, middle strip stretched)
        cv.text(x, y, "RAW 107 PX @2X TEXTURES X3 (LEGENDARY, MYTHIC)", (255, 236, 170), 2); y += 24
        for k, rid in enumerate(("legendary", "mythic")):
            gx = x + k * 340
            cv.fill(gx, y, gx + 330, y + 330, (60, 64, 78))
            cv.blit(res[(app, rid)][0], gx + 4, y + 4, 3)
            for q in (48, 59):                        # mark the 9-slice cut lines
                for t in range(0, 321, 6):
                    cv.fill(gx + 4 + q * 3, y + 4 + t, gx + 5 + q * 3, y + 7 + t, (255, 255, 255))
                    cv.fill(gx + 4 + t, y + 4 + q * 3, gx + 7 + t, y + 5 + q * 3, (255, 255, 255))
        cv.text(x + 690, y + 10, "DASHED", (160, 166, 186), 1)
        cv.text(x + 690, y + 22, "= 9-SLICE", (160, 166, 186), 1)
        cv.text(x + 690, y + 34, "CUTS", (160, 166, 186), 1)
        y += 342
        # slots
        cv.text(x, y, "SLOT FRAMES @2X (148 PX = 74 UI), PLACEHOLDER ICON", (255, 236, 170), 2); y += 24
        cv.fill(x, y, x + 4 * 156 + 12, y + 2 * 156 + 12, (22, 26, 36))
        for i, (rid, name, hexs, mood) in enumerate(RAR):
            gx, gy = x + 8 + (i % 4) * 156, y + 8 + (i // 4) * 156
            cv.blit(res[(app, rid)][1], gx, gy)
            cv.blit(TF.sword_icon(TF.hx(hexs)), gx + 10, gy + 10, 2)
        # 1x slot column on the right
        for i, (rid, name, hexs, mood) in enumerate(RAR[:4]):
            s1 = P.downsample(res[(app, rid)][1], 2)
            cv.blit(s1, x + 4 * 156 + 30, y + 4 + i * 80)
            cv.blit(TF.sword_icon(TF.hx(hexs)), x + 4 * 156 + 35, y + 9 + i * 80)
        cv.text(x + 4 * 156 + 30, y + 330, "1X", (160, 166, 186), 2)
        y += 2 * 156 + 12 + 34
        # rarity strip at 1x
        cv.text(x, y, "8 RARITY MOODS - 1X TOOLTIPS (160 X 100 UI)", (255, 236, 170), 2); y += 24
        game_bg(cv, x, y, COLW, 2 * 152 + 8, ai + 3)
        for i, (rid, name, hexs, mood) in enumerate(RAR):
            gx, gy = x + 12 + (i % 4) * 192, y + 8 + (i // 4) * 152
            big = TF.nine_slice(res[(app, rid)][0], 48, 320, 200)
            cv.blit(P.downsample(big, 2), gx, gy)
            cv.text(gx + 26, gy + 26, name.upper(), TF.hx(hexs), 2, bold=True)
            cv.text(gx + 26, gy + 50, mood, (230, 230, 230), 1)
            cv.text(gx + 26, gy + 62, "+12 STR", (85, 255, 85), 1)
            cv.text(gx + 26, gy + 72, "-3 DEF", (255, 85, 85), 1)
        y += 2 * 152 + 16
        for ln in LIMITS[app]:
            cv.text(x, y, ln, (255, 190, 150), 2); y += 22
        ymax = max(ymax, y)
    out = TF.Canvas(W, ymax + 30, (30, 34, 46))
    out.px[:] = cv.px[:W * (ymax + 30) * 4]
    out.fill(0, ymax + 12, W, ymax + 30, (30, 34, 46))
    return out.png()


def main():
    jobs = [(app, rid) for app, _t, _f in APPROACHES for rid, *_r in RAR]
    with Pool(min(len(jobs), os.cpu_count() or 4)) as pool:
        out = pool.map(job, jobs)
    res = {(app, rid): (tip, slot) for app, rid, tip, slot in out}
    report = {}
    print("contrast of text on the tooltip centre (over a light sky, worst case) - min over white/grey/green/red/gold/aqua")
    for app, _t, _f in APPROACHES:
        worst = 99.0
        cells = []
        for rid, name, hexs, _m in RAR:
            tip = res[(app, rid)][0]
            assert len(tip) == 107 and len(tip[0]) == 107
            assert check_strip(tip), "stretch strip not uniform: %s %s" % (app, rid)
            cc = centre_colour(tip)
            vals = {k: contrast(c, cc) for k, c in TEXT.items()}
            vals["rarity"] = contrast(TF.hx(hexs), cc)
            vals["dkgrey130"] = contrast((130, 130, 130), cc)
            mn = min(v for k, v in vals.items() if k != "dkgrey130")
            if mn < worst: worst, wname = mn, min((v, k) for k, v in vals.items() if k != "dkgrey130")[1]
            cells.append("%s %.1f (dk %.1f)" % (name, mn, vals["dkgrey130"]))
        report[app] = (worst, wname)
        print("  %-6s %s" % (app, " | ".join(cells)))
    os.makedirs(OUT, exist_ok=True)
    data = make_sheet(res, report)
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh: fh.write(data)
    print("wrote %s (%d bytes)" % (os.path.join(OUT, "sheet.png"), len(data)))
    if len(sys.argv) > 1:          # optional: dump raw textures for inspection into a scratch dir
        d = sys.argv[1]; os.makedirs(d, exist_ok=True)
        for (app, rid), (tip, slot) in res.items():
            P.write_png(os.path.join(d, "%s_%s_tip.png" % (app, rid)), tip)
            P.write_png(os.path.join(d, "%s_%s_slot.png" % (app, rid)), slot)


if __name__ == "__main__":
    main()
