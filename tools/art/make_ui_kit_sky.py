#!/usr/bin/env python3
"""SKY WINDOW UI KIT - the approved SkyyGear "SKY WINDOW" tooltip theme carried over to every menu / hub page. All pixels ORIGINAL.

Skyy 2026-10-10, on the SKY WINDOW tooltips (art/tooltip-sky/): "beautiful! can we design it all with the new theme". Then (Hubs-Spec
Q6): "Each hub its own mood" - the same Sky Window page frame, but the corner windows differ per hub: Character = sunrise, Storage =
night vault (stars), Market = golden noon, Smithing = ember forge, World = clear sky, Social = sunset (+ a neutral frame for every
other page). Element names, sizes and borders follow research/Hubs-Spec.md section 7.3.

The kit reuses the tooltip theme's own painters (tools/art/make_tooltip_sky.py: gold bevel, sky scenes, clouds, isle + waterfall,
sparkles), so pages and tooltips are one family: a crisp bevelled emblem-gold frame, a clear-sky ribbon between two gold tubes, round
gold-ringed sky WINDOWS with glowing gold star points in the fixed corners, and dark navy interiors that keep every kit text colour
readable (>= 4.5:1, measured here and by the validator).

Writes art/ui-kit-sky/:
  Common/UI/Custom/SkyyKit/<Element>[_<State>]@2x.png   (markup path "SkyyKit/<Element>[_<State>].png", no @2x)
  Common/UI/Custom/SkyyKit/HubIcon_<Hub>@2x.png (128) + HubIcon_<Hub>.png (64, hard alpha, item-icon size)
  sheet.png, manifest.json (bytes + sha256 + Border in UI units + kit element + contrast table)
Run:   python tools/art/make_ui_kit_sky.py        (deterministic, pure Python 3, no Pillow, every CPU core)
Check: python tools/art/validate_ui_kit_sky.py

9-SLICE RULES (art/tooltip-sky/README.md): @2x = 2 texture px per UI unit (the max); Border is in UI units; edges + centre STRETCH
(never tile). In a stretched strip the sampler gets BIG ("far from any corner"), so strip pixels depend only on the depth from the edge;
all corner art lives inside the fixed corner patches. Buttons / tabs keep a smooth vertical face gradient in their middle rows (it is
stretched, which is fine for a smooth ramp), so only their columns are strip-uniform; the manifest says which axis each one keeps.
Strip-uniform axes are rendered narrow (2 x border + 4 px) and widened by repeating the strip column: exact and fast.
"""
import hashlib, json, math, os, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_tooltip_sky as T          # the approved SKY WINDOW painters (read only; importing does not run it)

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "art", "ui-kit-sky")
KIT = "Common/UI/Custom/SkyyKit"
INLINE = "SkyyKit"
BIG = 1.0e4
SS = 4

clamp01, smooth, mix, mul, add, over, bevel, sparkle = T.clamp01, T.smooth, T.mix, T.mul, T.add, T.over, T.bevel, T.sparkle
GOLD_D, GOLD, GOLD_L, GOLD_W, WHITE = T.GOLD_D, T.GOLD, T.GOLD_L, T.GOLD_W, T.WHITE
SKY = T.MOOD["normal"]                         # CLEAR DAY: the frame ribbon on every page
OUTL = (18, 13, 28)                            # violet-black outline (menu icon family)
NAVY = (13, 21, 39)                            # page interior
PANEL_IN = (9, 15, 29)                         # section panel interior
INSET_IN = (6, 10, 21)                         # inset sub-box interior
SKYLINE = (150, 204, 244)                      # thin sky-blue inner line
GLOW = (214, 236, 255)
FRAME_ALPHA = 0.98                             # the frame centre: 98 % opaque (Hubs-Spec 7.3)

# ---------------------------------------------------------------- hub moods (corner windows); palettes built on the tooltip moods
SUNRISE = dict(T.MOOD["untiered"], sky0=(118, 146, 214), sky1=(255, 212, 164), cl=(255, 244, 232), cs=(206, 170, 190),
               glow=(255, 214, 150), sun=(255, 236, 176), grass=(110, 196, 96), water=(190, 232, 255), tree=(80, 160, 80))
FORGE = dict(T.MOOD["untiered"], sky0=(46, 14, 12), sky1=(214, 84, 26), cl=(255, 170, 100), cs=(110, 40, 30), glow=(255, 140, 40),
             sun=(255, 150, 50), grass=(150, 90, 40), water=(255, 190, 110), tree=(200, 80, 30))
SUNSET = dict(T.MOOD["rare"], sky0=(86, 52, 128), sky1=(255, 150, 112), cl=(255, 206, 190), cs=(170, 96, 130), glow=(255, 150, 120),
              sun=(255, 176, 96), tree=(214, 110, 90), water=(255, 200, 200), grass=(160, 150, 90))


def top(rid, m, ci, mirror=False):
    if mirror: return lambda x, y: T.scene_top(rid, m, ci, -x, y)
    return lambda x, y: T.scene_top(rid, m, ci, x, y)


def isle(rid, m, ci):
    return lambda x, y: T.scene_isle(rid, m, ci, x, y)


N = T.MOOD
# frame variant -> (label, [top-left, top-right, bottom-left, bottom-right] scenes, glow colour of the windows)
MOODS = {
    "":          ("NEUTRAL - CLEAR SKY", [top("normal", N["normal"], 0), top("normal", N["normal"], 1),
                                          top("normal", N["normal"], 1, True), top("normal", N["normal"], 0, True)], GLOW),
    "Character": ("SUNRISE", [top("untiered", SUNRISE, 0), top("untiered", SUNRISE, 0, True),
                              isle("normal", SUNRISE, 2), isle("normal", SUNRISE, 3)], (255, 226, 170)),
    "Storage":   ("NIGHT VAULT", [top("mythic", N["mythic"], 0), top("mythic", N["mythic"], 1),
                                  isle("mythic", N["mythic"], 2), isle("mythic", N["mythic"], 3)], (214, 150, 255)),
    "Market":    ("GOLDEN NOON", [top("unique", N["unique"], 0), top("unique", N["unique"], 1),
                                  isle("unique", N["unique"], 2), isle("unique", N["unique"], 3)], (255, 226, 120)),
    "Smithing":  ("EMBER FORGE", [top("untiered", FORGE, 1, True), top("untiered", FORGE, 1),
                                  isle("untiered", FORGE, 2), isle("untiered", FORGE, 3)], (255, 160, 70)),
    "World":     ("CLEAR SKY", [top("normal", N["normal"], 0), top("normal", N["normal"], 1),
                                isle("normal", N["normal"], 2), isle("normal", N["normal"], 3)], GLOW),
    "Social":    ("SUNSET", [top("untiered", SUNSET, 0), top("untiered", SUNSET, 0, True),
                             isle("rare", SUNSET, 2), isle("rare", SUNSET, 3)], (255, 180, 150)),
}
HUB_NAMES = ["Character", "Storage", "Market", "Smithing", "World", "Social"]


# ---------------------------------------------------------------- geometry helpers (@2x px)
def axis(v, full, b):
    """-> (depth from the nearest edge, side -1 / +1). b > 0: the middle strip [b, full - b) returns BIG. b == 0: real depth."""
    side = -1 if v < full / 2.0 else 1
    if b and b <= v < full - b: return BIG, side
    return (v if side < 0 else full - v), side


def rbox(a, b, inset, R, sx, sy):
    """depth inside a rounded box (corner radius R) + outward screen normal"""
    ax, by = a - inset, b - inset
    if ax < R and by < R:
        dx, dy = R - ax, R - by; h = math.hypot(dx, dy)
        if h < 1e-6: return R, (sx * 0.707, sy * 0.707)
        return R - h, (sx * dx / h, sy * dy / h)
    if ax < by: return ax, (sx, 0.0)
    return by, (0.0, sy)


def tube(acc, d, d0, d1, nx, ny, dark=GOLD_D, light=GOLD_L, edge=0.55, spec=True):
    """a bevelled tube between depths d0..d1 (outward normal nx, ny), dark outlined edges"""
    if d < d0 - 0.6 or d > d1 + 0.6: return
    s = 1 - 2 * (d - d0) / (d1 - d0)
    c = bevel(s, nx, ny, dark, light, spec)
    if d < d0 + 0.35 or d > d1 - 0.35: c = mix(c, dark, edge)
    over(acc, c, clamp01((d - d0 + 0.6) * 1.8) * clamp01((d1 + 0.6 - d) * 1.8))


# ---------------------------------------------------------------- the big-frame profile (Frame sides = Header sides)
BANDS = {"page": (1.2, 5.6, 12.4, 15.4, 16.4, 17.6), "card": (1.0, 4.2, 8.6, 10.8, 11.6, 12.6)}


def frame_profile(acc, d, nx, ny, inner, kind="page", alpha=1.0):
    o0, o1, r1, i1, k1, l1 = BANDS[kind]
    if d < o0 + 0.3: over(acc, OUTL, clamp01((d + 0.4) * 2))
    if o1 - 0.4 <= d <= r1 + 0.4:                                            # clear-sky ribbon with a soft cloud streak
        t = clamp01((d - o1) / (r1 - o1))
        c = mix(mix(SKY["sky1"], WHITE, 0.25), SKY["sky0"], t ** 0.9)
        c = mix(c, mix(SKY["cl"], WHITE, 0.5), 0.5 * math.exp(-((d - (o1 + r1) / 2 - 0.2) / 0.9) ** 2))
        over(acc, c, 1.0)
    tube(acc, d, o0, o1, nx, ny)
    tube(acc, d, r1, i1, nx, ny, edge=0.5)
    if d > i1 - 0.1:
        if d < k1: over(acc, mul(inner, 0.5), 1.0)
        elif d < l1: over(acc, mix(SKYLINE, WHITE, 0.15), 1.0)
        else: over(acc, mix(inner, SKY["sky0"], 0.30 * math.exp(-(d - l1) / 3.2)), alpha)


# ---------------------------------------------------------------- corner ornaments
def window(acc, lx, ly, ring_r, glass_r, scene):
    """a round gold-ringed sky window; (lx, ly) = screen offset from its centre; scene(x, y) in tooltip scene units"""
    dd = math.hypot(lx, ly)
    if dd > ring_r + 0.7: return
    if glass_r - 0.4 <= dd:
        mid, half = (glass_r + ring_r) / 2, (ring_r - glass_r) / 2
        s = (dd - mid) / half
        rx, ry = lx / max(dd, 1e-6), ly / max(dd, 1e-6)
        c = bevel(-s, -rx, -ry, GOLD_D, GOLD_L) if s < 0 else bevel(s, rx, ry, GOLD_D, GOLD_L)
        if dd > ring_r - 0.5 or dd < glass_r + 0.4: c = mix(c, GOLD_D, 0.6)
        over(acc, c, clamp01((dd - glass_r + 0.4) * 2.2) * clamp01((ring_r + 0.6 - dd) * 2.2))
    if dd < glass_r + 0.4:
        k = T.WIN_R / glass_r
        col = scene(lx * k, ly * k)[:3]
        col = mix(col, mul(col, 0.55), smooth(glass_r - 2.0, glass_r, dd))                      # inner shadow at the glass edge
        sheen = math.exp(-((math.hypot(lx * k + 2.5, ly * k + 2.5) - 9.0) / 1.1) ** 2) * clamp01(-(lx + ly) * k / 8)
        col = mix(col, WHITE, 0.22 * sheen)
        over(acc, col, clamp01((glass_r + 0.4 - dd) * 2.2))


def star_point(acc, a, b, ca, cb, ring_r, L, sx, sy, glow=GLOW, spark=5.2, width=0.42):
    """a glowing gold star point from the window (centre ca, cb in depth coords) toward the texture corner (depth 0, 0)"""
    dpt = ((ca - a) + (cb - b)) / math.sqrt(2); per = abs((a - ca) - (b - cb)) / math.sqrt(2)
    if ring_r - 2 < dpt < L and per < (L - dpt) * width:
        upper = ((a - ca) - (b - cb)) * sx * sy >= 0
        c = mix(GOLD_L, GOLD, clamp01(per / 2.4)) if upper else mix(GOLD, GOLD_D, 0.45)
        if per < 0.45: c = mix(c, GOLD_W, 0.5)
        over(acc, c, clamp01(((L - dpt) * width - per) * 2.2))
    tpa, tpb = ca - (L - 0.6) / math.sqrt(2), cb - (L - 0.6) / math.sqrt(2)
    ddt = math.hypot(a - tpa, b - tpb)
    if ddt < 12: over(acc, mix(glow, GOLD_L, 0.4), 0.5 * math.exp(-ddt / 2.0))
    v = sparkle(a - tpa, b - tpb, spark)
    if v > 0: over(acc, mix(glow, WHITE, 0.75), v)


def stud(acc, a, b, pa, pb, r=3.0, glow=GLOW):
    q = abs(a - pa) + abs(b - pb)
    if q < 2 * r: over(acc, mix(glow, GOLD_L, 0.5), 0.45 * math.exp(-q / 1.4))
    if q < r:
        over(acc, GOLD_L if (a - pa) + (b - pb) < 0 else GOLD, clamp01((r - q) * 2))
        if q < r / 3: over(acc, GOLD_W, clamp01((r / 3 - q) * 2) * 0.8)


def corner_spark(acc, a, b, pa, pb, s, col=GOLD_L, glow=0.35):
    q = math.hypot(a - pa, b - pb)
    if q < s * 1.6: over(acc, mix(GLOW, GOLD_L, 0.5), glow * math.exp(-q / (s * 0.35)))
    v = sparkle(a - pa, b - pb, s)
    if v > 0: over(acc, mix(col, WHITE, 0.45), v)


def window_glow(acc, dd, ring_r, limit_f, glow=GLOW):
    if dd > ring_r - 1 and limit_f > 0: over(acc, mix(glow, GOLD_L, 0.35), 0.5 * limit_f * math.exp(-(dd - ring_r) / 2.4))


# ---------------------------------------------------------------- Frame / Frame_<Hub> (160, Border 32) + CardFrame (160, Border 32)
FR_S, FR_B = 160, 64
FR_C, FR_RING, FR_GLASS = 30.0, 27.0, 21.0          # page window: centre depth, ring / glass radius (glass = 21 UI across)
CD_C, CD_RING, CD_GLASS = 21.0, 17.5, 13.0          # card window (smaller)


def frame_sample(variant, card, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, FR_B); b, sy = axis(Y, H, FR_B)
    d, (nx, ny) = rbox(a, b, 0, 12.0 if not card else 9.0, sx, sy)
    if d < -0.5: return acc
    frame_profile(acc, d, nx, ny, NAVY, "card" if card else "page", FRAME_ALPHA)
    if a < FR_B and b < FR_B:
        _lab, scenes, glow = MOODS[variant]
        ci = (0 if sx < 0 else 1) + (0 if sy < 0 else 2)
        c, ring, glass = (CD_C, CD_RING, CD_GLASS) if card else (FR_C, FR_RING, FR_GLASS)
        dd = math.hypot(a - c, b - c)
        window_glow(acc, dd, ring, 1.0 - smooth(50.0, 61.0, max(a, b)), glow)
        star_point(acc, a, b, c, c, ring, ring + (7.5 if card else 10.5), sx, sy, glow, spark=4.6 if card else 5.6)
        if not card:
            stud(acc, a, b, 52.0, 9.0, glow=glow); stud(acc, a, b, 9.0, 52.0, glow=glow)
        else:
            stud(acc, a, b, 44.0, 6.4, 2.4, glow); stud(acc, a, b, 6.4, 44.0, 2.4, glow)
        lx = (a - c) * (1 if sx < 0 else -1); ly = (b - c) * (1 if sy < 0 else -1)
        window(acc, lx, ly, ring, glass, scenes[ci])
    return acc


# ---------------------------------------------------------------- Header (600 x 76, HorizontalBorder 60, VerticalBorder 0)
HD_W, HD_H, HD_HB = 600, 76, 120
TITLE_TOP, TITLE_BOT = (34, 52, 92), (17, 27, 52)


def title_inner(Y):
    c = mix(TITLE_TOP, TITLE_BOT, clamp01((Y - 16) / 54))
    return mix(c, SKY["sky0"], 0.10 * math.exp(-((Y - 30) / 6.0) ** 2))


def header_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, HD_HB)
    if Y < H / 2: d, (nx, ny) = rbox(a, Y, 0, 10.0, sx, -1)
    else: d, (nx, ny) = a, (sx, 0.0)
    frame_profile(acc, d, nx, ny, title_inner(Y))
    e = H - Y                                                                       # bottom seam: a gold line
    if d > BANDS["page"][3] - 0.2 and e < 5.4:
        if e < 1.0: over(acc, OUTL, 1.0)
        tube(acc, e, 1.0, 4.0, 0.0, 1.0, edge=0.5)
        if 4.0 <= e < 5.4: over(acc, mix(SKYLINE, WHITE, 0.1), 0.55 * clamp01(5.4 - e))
    if a < HD_HB:                                                                   # the cap: a small sky gem, a wing, studs
        cy = 38.0; ca = 34.0
        dd = math.hypot(a - ca, Y - cy)
        window_glow(acc, dd, 12.0, 1.0)
        if 50 < a < 112:                                                            # gold wing toward the title
            t = (a - 50) / 62.0
            hw = 2.6 * (1 - t) ** 0.8 + 0.4
            q = Y - cy
            if abs(q) < hw + 0.6:
                over(acc, bevel(-q / max(hw, 0.4), 0.0, -1.0, GOLD_D, GOLD_L), clamp01((hw + 0.5 - abs(q)) * 2.0) * (1 - smooth(104, 112, a)))
            g = math.exp(-abs(q) / 2.2) * (1 - t) * 0.25
            if g > 0.01: over(acc, mix(GLOW, GOLD_L, 0.5), g)
        corner_spark(acc, a, Y, 106.0, cy, 5.0)
        stud(acc, a, Y, 70.0, 9.0)
        corner_spark(acc, a, Y, 4.0, 4.0, 5.5, glow=0.4)
        window(acc, (a - ca) * (1 if sx < 0 else -1), Y - cy, 12.5, 9.0, top("normal", N["normal"], 0 if sx < 0 else 1))
    return acc


# ---------------------------------------------------------------- HeaderOrnament (472 x 44 = 236 x 22 UI, not sliced)
HO_W, HO_H, HO_CX, HO_CY, HO_RING, HO_GLASS = 472, 44, 236.0, 27.0, 15.0, 11.5


def ornament_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    lx, ly = X - HO_CX, Y - HO_CY
    ax = abs(lx); dd = math.hypot(lx, ly)
    if dd > HO_RING - 1: over(acc, mix(GLOW, GOLD_L, 0.35), 0.5 * math.exp(-(dd - HO_RING) / 2.6))
    for (y0, y1, x1, w0) in ((-2.0, -9.0, 214.0, 3.2), (3.0, 7.5, 150.0, 2.0), (0.5, 1.5, 96.0, 1.2)):
        if HO_RING - 3 < ax < x1:
            t = (ax - (HO_RING - 3)) / (x1 - (HO_RING - 3))
            yc = y0 + (y1 - y0) * t * t
            hw = w0 * (1 - t) ** 0.7 + 0.35
            q = ly - yc
            if abs(q) < hw + 0.7:
                over(acc, bevel(-q / max(hw, 0.4), 0.0, -1.0, GOLD_D, GOLD_L), clamp01((hw + 0.5 - abs(q)) * 2.0))
    for (tx, ty, s) in ((214.0, -9.0, 6.0), (150.0, 7.5, 4.5), (96.0, 1.5, 3.5)):
        q = math.hypot(ax - tx, ly - ty)
        if q < 9: over(acc, mix(GLOW, GOLD_L, 0.4), 0.4 * math.exp(-q / 2.0))
        v = sparkle(ax - tx, ly - ty, s)
        if v > 0: over(acc, mix(GLOW, WHITE, 0.7), v)
    for px in (60.0, 120.0, 180.0):                                                  # studs riding the long wing
        t = (px - (HO_RING - 3)) / (214.0 - (HO_RING - 3))
        stud(acc, ax, ly, px, -2.0 - 7.0 * t * t, 2.4)
    h = -(ly + HO_RING - 1.5)                                                        # a star point straight up
    if 0 < h < 11.5 and ax < (11.5 - h) * 0.42:
        c = mix(GOLD_L, GOLD, clamp01(ax / 2.4)) if lx <= 0 else mix(GOLD, GOLD_D, 0.45)
        over(acc, c, clamp01(((11.5 - h) * 0.42 - ax) * 2.2))
    v = sparkle(lx, ly + HO_RING + 10.5, 4.5)
    if v > 0: over(acc, mix(GLOW, WHITE, 0.75), v)
    window(acc, lx, ly, HO_RING, HO_GLASS, top("normal", N["normal"], 0))
    return acc


# ---------------------------------------------------------------- Close (+ _Hovered) 64 x 64, not sliced
def close_sample(state, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    lx, ly = X - 32.0, Y - 32.0
    dd = math.hypot(lx, ly)
    hov = state == "hovered"
    if hov and dd > 27: over(acc, mix(GLOW, GOLD_L, 0.4), 0.55 * math.exp(-(dd - 27) / 1.6))
    if dd > 29.5: return acc
    if dd > 28.3: over(acc, OUTL, clamp01((29.5 - dd) * 2))
    if 23.0 <= dd <= 28.6:
        s = (dd - 25.8) / 2.8; rx, ry = lx / dd, ly / dd
        c = bevel(-s, -rx, -ry, GOLD_D, GOLD_L) if s < 0 else bevel(s, rx, ry, GOLD_D, GOLD_L)
        over(acc, c, clamp01((dd - 22.6) * 2) * clamp01((28.6 - dd) * 2))
    if dd < 23.2:
        c = mix((30, 46, 80) if hov else (18, 28, 52), (10, 16, 32), clamp01((ly + 20) / 40))
        if hov: c = mix(c, SKY["sky0"], 0.25 * math.exp(-max(0.0, 23 - dd) / 4.0))
        if dd > 21.8: c = mul(c, 0.5)
        over(acc, c, clamp01((23.2 - dd) * 2))
        u, v = (lx + ly) / math.sqrt(2), (lx - ly) / math.sqrt(2)                    # the X: two tapered gold blades
        best = None
        for (p, q) in ((u, v), (v, u)):
            if abs(p) < 13.5:
                hw = 3.4 * (1 - abs(p) / 13.5) ** 0.6 + 0.5
                if abs(q) < hw + 0.6:
                    c2 = bevel(-q / max(hw, 0.4) * (1 if p >= 0 else -1), 0.707, -0.707, GOLD_D, GOLD_W if hov else GOLD_L)
                    al = clamp01((hw + 0.5 - abs(q)) * 2)
                    if abs(q) > hw - 0.6: c2 = mix(c2, GOLD_D, 0.6)
                    over(acc, c2, al)
        sp = sparkle(lx, ly, 6.0 if hov else 4.5)
        if sp > 0: over(acc, mix(GLOW, WHITE, 0.7), sp)
    return acc


# ---------------------------------------------------------------- Panel (64, Border 12) + PanelInset (48, Border 8)
def panel_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, 24); b, sy = axis(Y, H, 24)
    d, (nx, ny) = rbox(a, b, 0, 7.0, sx, sy)
    if d < -0.5: return acc
    if d < 1.0: over(acc, OUTL, clamp01((d + 0.5) * 2))
    tube(acc, d, 0.9, 3.4, nx, ny, edge=0.45)
    if d > 3.3:
        if d < 4.1: over(acc, mul(PANEL_IN, 0.5), 1.0)
        elif d < 4.9: over(acc, mix(PANEL_IN, SKYLINE, 0.45), 1.0)
        else: over(acc, mix(PANEL_IN, SKY["sky0"], 0.16 * math.exp(-(d - 4.9) / 2.6)), 1.0)
    if a < 24 and b < 24:
        corner_spark(acc, a, b, 2.8, 2.8, 7.0, glow=0.45)
        stud(acc, a, b, 15.0, 2.2, 1.8); stud(acc, a, b, 2.2, 15.0, 1.8)
    return acc


def inset_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, 16); b, sy = axis(Y, H, 16)
    d, (nx, ny) = rbox(a, b, 0, 5.0, sx, sy)
    if d < -0.5: return acc
    over(acc, (96, 78, 48), clamp01((d + 0.5) * 2))                                  # a thin dim-gold line
    if d > 1.2:
        c = INSET_IN
        if sy < 0 and b < BIG: c = mix(c, (0, 0, 0), 0.5 * math.exp(-max(0.0, b - 1.2) / 3.0))   # recessed: shadow from the top
        over(acc, c, clamp01((d - 1.2) * 2 + 0.2))
    return acc


# ---------------------------------------------------------------- Row / Row_Hovered / Row_Selected (64 x 48, Border 8)
ROW_IN = {"normal": (16, 26, 46), "hovered": (24, 40, 68), "selected": (24, 42, 74)}


def row_sample(state, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, 16); b, sy = axis(Y, H, 16)
    d, (nx, ny) = rbox(a, b, 0, 5.0, sx, sy)
    if d < -0.5: return acc
    inner = ROW_IN[state]
    if state == "normal":
        over(acc, (38, 56, 84), clamp01((d + 0.5) * 2))
        if d > 1.2:
            c = inner
            if sy < 0 and b < 3.2: c = mix(inner, (56, 80, 116), 0.6 * clamp01(3.2 - b))
            if sy > 0 and b < 3.0: c = mix(inner, (8, 12, 22), 0.5 * clamp01(3.0 - b))
            over(acc, c, clamp01((d - 1.2) * 2 + 0.2))
    elif state == "hovered":
        over(acc, (110, 168, 228), clamp01((d + 0.5) * 2))
        if d > 1.4:
            c = mix(inner, SKY["sky0"], 0.35 * math.exp(-(d - 1.4) / 2.2))
            if sy < 0 and b < 3.4: c = mix(c, (150, 200, 240), 0.35 * clamp01(3.4 - b))
            over(acc, c, clamp01((d - 1.4) * 2 + 0.2))
    else:                                                                             # gold left bar + faint sky tint
        over(acc, mix(GOLD_D, GOLD, 0.5), clamp01((d + 0.5) * 2))
        if d > 1.2:
            c = mix(inner, SKY["sky0"], 0.22 * math.exp(-(d - 1.2) / 3.0))
            if sy < 0 and b < 3.4: c = mix(c, (160, 206, 244), 0.3 * clamp01(3.4 - b))
            over(acc, c, clamp01((d - 1.2) * 2 + 0.2))
        if sx < 0 and a < 16:                                                         # the bar (depth from the left edge)
            if a < 9.0 and b > 2.6:
                c = bevel((5.0 - a) / 3.0, -1.0, 0.0, GOLD_D, GOLD_L)
                over(acc, c, clamp01((a - 1.6) * 2) * clamp01((8.6 - a) * 2) * clamp01((b - 2.6) * 1.5))
            if 8.6 < a < 14 and b > 2: over(acc, mix(GOLD, GOLD_L, 0.6), 0.3 * math.exp(-(a - 8.6) / 2.0) * clamp01(b - 2))
            if b < 16: corner_spark(acc, a, b, 5.2, 3.2, 4.6, glow=0.35)
    return acc


# ---------------------------------------------------------------- Tab (240 x 88, HorizontalBorder 20, VerticalBorder 12)
TB_HB = 40


def tab_sample(state, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, TB_HB)
    tp = Y < H / 2
    e = H - Y
    if tp: d, (nx, ny) = rbox(a, Y, 0, 12.0, sx, -1)
    else: d, (nx, ny) = a, (sx, 0.0)
    if d < -0.5: return acc
    t = clamp01((Y - 4) / 80.0)
    spec = False
    if state == "normal":
        face = mix((38, 54, 86), (21, 31, 54), t); rim = (mul(GOLD_D, 0.55), mix((112, 104, 92), GOLD, 0.25))
    elif state == "hovered":
        face = mix((52, 76, 116), (27, 41, 70), t); rim = (mul(GOLD_D, 0.75), mix((176, 186, 200), GOLD_L, 0.35))
    elif state == "pressed":
        face = mix((16, 24, 42), (32, 46, 74), t); rim = (mul(GOLD_D, 0.6), mix((140, 136, 128), GOLD, 0.35)); nx, ny = -nx, -ny
    else:
        face = mix((34, 54, 94), (17, 28, 54), t); rim = (GOLD_D, GOLD_L); spec = True
        face = mix(face, SKY["sky0"], 0.24 * math.exp(-max(0.0, Y - 4) / 12.0))       # soft sky glow at the top
    if d < 1.2: over(acc, OUTL, clamp01((d + 0.5) * 2))
    tube(acc, d, 1.1, 3.8, nx, ny, rim[0], rim[1], edge=0.45, spec=spec)
    if d > 3.7:
        c = face
        if state == "hovered": c = mix(c, (130, 186, 240), 0.30 * math.exp(-(d - 3.7) / 2.2))
        if state == "pressed": c = mix(c, (0, 0, 0), 0.3 * math.exp(-max(0.0, Y - 4) / 6.0))
        over(acc, c, 1.0)
    if state == "selected":
        if d > 1.0 and e < 14:
            if e < 1.0: over(acc, OUTL, 1.0)
            tube(acc, e, 1.0, 5.4, 0.0, 1.0, edge=0.45)
            if e > 5.4: over(acc, mix(GOLD, GOLD_L, 0.6), 0.45 * math.exp(-(e - 5.4) / 3.2))
        if a < TB_HB and tp: corner_spark(acc, a, Y, 3.4, 3.4, 6.0, glow=0.4)
        if a < TB_HB and e < 24: corner_spark(acc, a, e, 6.0, 3.2, 4.6, glow=0.3)
    elif d > 1.0 and e < 2.2:
        over(acc, (9, 13, 24), clamp01(2.2 - e))
    return acc


# ---------------------------------------------------------------- buttons: Primary / Secondary / Tertiary / Danger
BTN = {   # family: state -> (face top, face bottom, rim dark, rim light, inner glow, corner sparkles)
    "Primary": {"normal": ((116, 78, 26), (78, 50, 16), GOLD_D, GOLD_L, None, True),
                "hovered": ((128, 88, 30), (86, 56, 18), GOLD_D, GOLD_W, (255, 214, 120), True),
                "pressed": ((66, 42, 14), (96, 64, 22), GOLD_D, GOLD, None, False),
                "disabled": ((60, 58, 56), (42, 41, 42), (54, 48, 40), (126, 116, 98), None, False)},
    "Secondary": {"normal": ((62, 82, 114), (34, 46, 70), (40, 50, 70), (176, 196, 222), None, True),
                  "hovered": ((74, 98, 136), (40, 56, 84), (46, 58, 82), (220, 234, 250), (150, 204, 244), True),
                  "pressed": ((28, 38, 58), (50, 66, 94), (36, 44, 62), (140, 160, 186), None, False),
                  "disabled": ((56, 60, 68), (40, 42, 48), (44, 46, 52), (110, 114, 124), None, False)},
    "Tertiary": {"normal": ((30, 42, 66), (20, 29, 48), (40, 40, 44), (124, 112, 90), None, False),
                 "hovered": ((42, 60, 92), (26, 38, 62), (54, 52, 50), (190, 170, 120), (130, 186, 240), False),
                 "pressed": ((14, 21, 36), (28, 40, 62), (40, 40, 44), (124, 112, 90), None, False),
                 "active": ((40, 64, 104), (22, 36, 64), GOLD_D, GOLD_L, (150, 204, 244), True)},
    "Danger": {"normal": ((150, 40, 48), (88, 20, 28), (82, 16, 24), (255, 156, 146), None, True),
               "hovered": ((168, 46, 54), (100, 24, 32), (92, 18, 26), (255, 196, 186), (255, 120, 110), True),
               "pressed": ((76, 16, 24), (120, 30, 38), (70, 14, 20), (220, 120, 112), None, False)},
}


def button_sample(fam, state, hb, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    top_c, bot_c, rd, rl_, glow, sp = BTN[fam][state]
    a, sx = axis(X, W, hb)
    sy = -1 if Y < H / 2 else 1
    b = Y if sy < 0 else H - Y
    R = 10.0 if H >= 80 else 8.0
    d, (nx, ny) = rbox(a, b, 0, R, sx, sy)
    if d < -0.5: return acc
    pressed = state == "pressed"
    rim1 = 5.0 if H >= 80 else 4.0
    if d < 1.4: over(acc, OUTL, clamp01((d + 0.5) * 2))
    if pressed: nx, ny = -nx, -ny                                                  # sunken: the bevel lighting flips
    tube(acc, d, 1.3, rim1, nx, ny, rd, rl_, edge=0.45, spec=state != "disabled")
    if d > rim1 - 0.1:
        t = clamp01((Y - 6) / (H - 12.0))
        c = mix(top_c, bot_c, t)
        if state not in ("pressed", "disabled"):
            c = mix(c, mix(top_c, WHITE, 0.35), 0.35 * (1 - smooth(H * 0.09, H * 0.30, Y)))   # soft top gloss
        if pressed: c = mix(c, (0, 0, 0), 0.35 * math.exp(-max(0.0, Y - 5) / 6.0))
        if d < rim1 + 0.8: c = mix(c, mul(bot_c, 0.6), 0.6)
        if glow is not None: c = mix(c, glow, 0.38 * math.exp(-(d - rim1 - 0.8) / 2.4))
        over(acc, c, 1.0)
    if sp and a < hb and sy < 0:
        s = 5.0 if state in ("normal", "active") else 6.0
        corner_spark(acc, a, b, 4.2, 4.2, s if H >= 80 else s - 0.8, glow=0.35 if state == "normal" else 0.5)
    return acc


# ---------------------------------------------------------------- InputBox (96 x 64, Border 16) + CheckBox (44, Border 7) + CheckMark
INPUT_IN = (7, 11, 22)


def input_sample(state, bpx, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, bpx); b, sy = axis(Y, H, bpx)
    d, (nx, ny) = rbox(a, b, 0, 5.0, sx, sy)
    if d < -0.5: return acc
    if d < 1.0: over(acc, OUTL, clamp01((d + 0.5) * 2))
    if state == "selected": tube(acc, d, 0.9, 3.0, nx, ny, edge=0.4)
    elif state == "hovered": tube(acc, d, 0.9, 3.0, -nx, -ny, (84, 62, 30), (214, 172, 96), edge=0.4, spec=False)
    else: tube(acc, d, 0.9, 3.0, -nx, -ny, (54, 42, 28), (140, 112, 70), edge=0.4, spec=False)   # recessed: lit bottom-right
    if d > 2.9:
        c = INPUT_IN
        if d < 3.6: c = mul(INPUT_IN, 0.4)
        elif state == "selected" and d < 4.6: c = mix(INPUT_IN, SKYLINE, 0.55)
        elif state == "selected": c = mix(INPUT_IN, SKY["sky0"], 0.22 * math.exp(-(d - 4.6) / 2.6))
        if sy < 0 and b < BIG: c = mix(c, (0, 0, 0), 0.5 * math.exp(-max(0.0, b - 3.6) / 3.0))
        over(acc, c, 1.0)
    if state == "selected" and a < bpx and b < bpx: corner_spark(acc, a, b, 2.4, 2.4, min(5.4, bpx * 0.4), glow=0.35)
    return acc


def checkmark_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    pts = [(7.5, 16.5), (13.0, 22.5), (24.5, 9.0)]
    dist = T.poly_dist(X, Y, pts)
    if dist < 6: over(acc, mix(GLOW, GOLD_L, 0.4), 0.35 * math.exp(-dist / 1.8))
    if dist < 3.8: over(acc, OUTL, clamp01((3.8 - dist) * 2))
    if dist < 2.6:
        s = clamp01(1 - dist / 2.6)
        c = mix(GOLD_D, GOLD_L, s) if (X + Y) < 34 else mix(GOLD_D, GOLD, s)
        if dist < 0.8: c = mix(c, GOLD_W, 0.5)
        over(acc, c, clamp01((2.6 - dist) * 2))
    v = sparkle(X - 24.5, Y - 9.0, 5.0)
    if v > 0: over(acc, mix(GLOW, WHITE, 0.7), v)
    return acc


# ---------------------------------------------------------------- ScrollTrack / ScrollHandle (12 x 24, Border 3; bar Size 6 UI)
def scroll_sample(state, W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, 6); b, sy = axis(Y, H, 6)
    d, (nx, ny) = rbox(a, b, 0, 6.0, sx, sy)
    if d < -0.5: return acc
    if state == "track":
        over(acc, (84, 68, 42), clamp01((d + 0.5) * 2))                               # a thin gold thread round a dark groove
        if d > 1.0: over(acc, mix((5, 8, 18), (16, 24, 42), clamp01((d - 1) / 4)), clamp01((d - 1.0) * 2 + 0.2))
        return acc
    if d < 0.9: over(acc, OUTL, clamp01((d + 0.5) * 2))
    dark, light = {"normal": (GOLD_D, GOLD_L), "hovered": (GOLD, GOLD_W), "dragged": (GOLD_D, GOLD_L)}[state]
    if d > 0.6:
        s = clamp01(1 - (d - 0.6) / 4.6)
        c = bevel(s, nx, ny, dark, light)
        if state == "dragged": c = mix(c, SKYLINE, 0.45 * clamp01((d - 2.5) / 2.0))
        over(acc, c, clamp01((d - 0.6) * 2 + 0.2))
    return acc


# ---------------------------------------------------------------- Separator (64 x 4, HorizontalBorder 8, 2 UI tall)
def separator_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    a, sx = axis(X, W, 16)
    taper = smooth(0.5, 15.0, a) if a < BIG else 1.0
    hw = 1.65 * taper + 0.25
    q = Y - 2.0
    if abs(q) < hw + 0.6:
        c = bevel(-q / max(hw, 0.4), 0.0, -1.0, GOLD_D, GOLD_L)
        if abs(q) > hw - 0.5: c = mix(c, GOLD_D, 0.5)
        over(acc, c, clamp01((hw + 0.5 - abs(q)) * 2.0) * clamp01(a * 0.8))
    return acc


# ---------------------------------------------------------------- SlotEmpty (148, not sliced; the tooltip-sky Slot_<R> family)
def slot_sample(W, H, X, Y):
    acc = [0.0, 0.0, 0.0, 0.0]
    S = 148
    a = min(X, S - X); b = min(Y, S - Y)
    sx = -1 if X < S / 2 else 1; sy = -1 if Y < S / 2 else 1
    d, (nx, ny) = rbox(a, b, 3.0, 9.0, sx, sy)
    if d < -0.5: return acc
    vig = math.hypot(X - S / 2, Y - S / 2) / (S / 2)
    sky = mix(mix(SKY["sky0"], SKY["sky1"], Y / S), NAVY, 0.80 - 0.12 * clamp01(vig))
    over(acc, sky, 1.0)
    lw = Y - (S - 30) - 4 * math.sin(X * 0.075) - 3 * math.sin(X * 0.19 + 1)       # a faint cloud bank at the bottom
    if lw > 0: over(acc, mix(mix(SKY["cl"], SKY["cs"], clamp01(lw / 22)), NAVY, 0.72), 0.7 * clamp01(lw / 3))
    if d > 7.4: over(acc, SKY["sky0"], 0.22 * math.exp(-(d - 7.4) / 3.0))
    if 6.2 <= d <= 7.6: over(acc, mix(SKYLINE, WHITE, 0.15), clamp01(min(d - 6.2, 7.6 - d) * 2.5 + 0.3))
    if 5.0 <= d < 6.2: over(acc, mul(NAVY, 0.55), 1.0)
    if -0.5 <= d <= 5.4:
        s = 1 - 2 * d / 5.0
        c = bevel(s, nx, ny, GOLD_D, GOLD_L)
        if d < 0.45 or d > 4.7: c = mix(c, GOLD_D, 0.55)
        over(acc, c, clamp01((d + 0.5) * 2) * clamp01((5.4 - d) * 2))
    q = abs(a - 9.5) + abs(b - 9.5)
    if q < 12: over(acc, mix(GLOW, GOLD_L, 0.4), 0.4 * math.exp(-q / 2.6))
    st = sparkle(a - 9.5, b - 9.5, 7.0)
    if st > 0: over(acc, mix(GOLD_L, WHITE, 0.4), st)
    return acc


# ---------------------------------------------------------------- HUB ICONS (round sky-window badge + symbol), 128 @2x / 64
HI = 128
HI_C, HI_RING, HI_GLASS = 64.0, 61.0, 50.0
# hub -> (scene logic rid, palette, top / isle, ci)
HUBS = [("Character", "untiered", SUNRISE, "top", 0), ("Storage", "mythic", N["mythic"], "top", 0),
        ("Market", "unique", N["unique"], "top", 0), ("Smithing", "untiered", FORGE, "top", 1),
        ("World", "normal", N["normal"], "isle", 2), ("Social", "untiered", SUNSET, "top", 0)]
MAT = {"gold": (GOLD_D, GOLD, GOLD_L), "steel": ((52, 58, 76), (128, 138, 160), (222, 228, 240)),
       "wood": ((70, 38, 20), (146, 90, 46), (214, 150, 88)), "teal": ((14, 66, 78), (36, 140, 150), (126, 222, 214)),
       "violet": ((50, 30, 96), (110, 76, 186), (196, 166, 250)), "skin": ((150, 92, 64), (226, 168, 124), (255, 222, 186)),
       "hair": ((46, 26, 18), (92, 56, 32), (150, 100, 60)), "emerald": ((14, 90, 50), (40, 190, 100), (190, 255, 210)),
       "dark": ((10, 8, 16), (24, 18, 30), (50, 40, 60))}


def sd_circle(x, y, cx, cy, r): return math.hypot(x - cx, y - cy) - r


def sd_box(x, y, cx, cy, hx_, hy_, r=0.0):
    qx, qy = abs(x - cx) - hx_ + r, abs(y - cy) - hy_ + r
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r


def sd_capsule(x, y, ax_, ay_, bx, by, r): return T.seg_dist(x, y, ax_, ay_, bx, by) - r


def sd_poly(x, y, pts):
    """convex polygon, clockwise on screen (y down); exact inside, close enough outside for an outline band"""
    m = -1e9
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0; L = math.hypot(ex, ey)
        m = max(m, (x - x0) * (ey / L) + (y - y0) * (-ex / L))
    return m


def bust(cx, cy, k, body="teal"):
    """a blocky player bust: shoulders, head, hair, eyes"""
    return [(lambda X, Y: sd_box(X, Y, cx, cy + 30 * k, 26 * k, 16 * k, 10 * k), body),
            (lambda X, Y: sd_box(X, Y, cx, cy, 14 * k, 14 * k, 3 * k), "skin"),
            (lambda X, Y: max(sd_box(X, Y, cx, cy - 6 * k, 15 * k, 9 * k, 3 * k), Y - (cy - 4 * k)), "hair"),
            (lambda X, Y: min(sd_box(X, Y, cx - 6 * k, cy + 3 * k, 2.2 * k, 2.6 * k), sd_box(X, Y, cx + 6 * k, cy + 3 * k, 2.2 * k, 2.6 * k)),
             "dark")]


def hub_layers(name):
    if name == "Character":
        return bust(64.0, 58.0, 1.0, "teal") + [(lambda X, Y: sd_poly(X, Y, [(64, 82), (70, 89), (64, 96), (58, 89)]), "gold")]
    if name == "Storage":
        return [(lambda X, Y: sd_box(X, Y, 64, 80, 32, 18, 3), "wood"),
                (lambda X, Y: sd_box(X, Y, 64, 56, 32, 11, 7), "wood"),
                (lambda X, Y: min(sd_box(X, Y, 43, 70, 4, 29, 1), sd_box(X, Y, 85, 70, 4, 29, 1)), "gold"),
                (lambda X, Y: sd_box(X, Y, 64, 66, 33, 3, 1), "gold"),
                (lambda X, Y: sd_box(X, Y, 64, 70, 7, 9, 2), "gold"),
                (lambda X, Y: min(sd_circle(X, Y, 64, 68, 2.4), sd_box(X, Y, 64, 73, 1.1, 3)), "dark")]
    if name == "Market":
        return [(lambda X, Y: sd_box(X, Y, 48, 92, 20, 6, 6), "gold"),
                (lambda X, Y: sd_box(X, Y, 48, 83, 20, 6, 6), "gold"),
                (lambda X, Y: sd_box(X, Y, 48, 74, 20, 6, 6), "gold"),
                (lambda X, Y: sd_circle(X, Y, 78, 58, 22), "gold"),
                (lambda X, Y: abs(math.hypot(X - 78, Y - 58) - 16.5) - 1.2, "dark"),
                (lambda X, Y: sd_poly(X, Y, [(78, 47), (87, 58), (78, 69), (69, 58)]), "emerald")]
    if name == "Smithing":
        return [(lambda X, Y: sd_box(X, Y, 66, 98, 24, 6, 2), "steel"),
                (lambda X, Y: sd_box(X, Y, 66, 86, 11, 8, 1), "steel"),
                (lambda X, Y: min(sd_box(X, Y, 68, 72, 30, 8, 2), sd_poly(X, Y, [(40, 65), (40, 79), (18, 70), (18, 67)])), "steel"),
                (lambda X, Y: sd_capsule(X, Y, 58, 58, 82, 26, 3.2), "wood"),
                (lambda X, Y: sd_poly(X, Y, [(72, 16), (98, 34), (91, 44), (65, 26)]), "gold")]
    if name == "World":
        return []                                                     # the floating isle in the window IS the symbol
    if name == "Social":
        return bust(80.0, 48.0, 0.78, "violet") + bust(54.0, 62.0, 0.9, "teal")
    raise ValueError(name)


def hub_sample(idx, W, H, X, Y):
    name, rid, m, kind, ci = HUBS[idx]
    acc = [0.0, 0.0, 0.0, 0.0]
    lx, ly = X - HI_C, Y - HI_C
    dd = math.hypot(lx, ly)
    if dd > HI_RING + 1.8: return acc
    if dd > HI_RING - 0.4: over(acc, OUTL, clamp01((HI_RING + 1.8 - dd) * 2))
    scene = (lambda x, y: T.scene_top(rid, m, ci, x, y)) if kind == "top" else (lambda x, y: T.scene_isle(rid, m, ci, x, y))
    layers = hub_layers(name)
    glass_sd = dd - HI_GLASS
    if layers:
        su = min(f(X, Y) for f, _m in layers)
        def scene2(x, y):                                             # a soft dark halo behind the symbol: reads on any sky
            c = scene(x, y)
            if su > 0: return list(mix(c[:3], (10, 14, 30), 0.45 * math.exp(-su / 3.5))) + [c[3]]
            return c
        window(acc, lx, ly, HI_RING, HI_GLASS, scene2)
    else:
        window(acc, lx, ly, HI_RING, HI_GLASS, scene)
    for f, mname in layers:
        s = max(f(X, Y), glass_sd + 1.0)
        if s > 0.6: continue
        dk, md, lt = MAT[mname]
        e = 0.7
        gx = (f(X + e, Y) - f(X - e, Y)) / (2 * e); gy = (f(X, Y + e) - f(X, Y - e)) / (2 * e)
        base = mix(md, lt, 0.35 * clamp01(-(lx + ly) / 70.0 + 0.4))
        if s > -4.5:
            facing = gx * -0.6 + gy * -0.8                            # outward normal toward the light (upper left)
            if facing > 0: base = mix(base, lt, 0.8 * facing * clamp01((s + 4.5) / 3.0))
            else: base = mix(base, dk, 0.7 * -facing * clamp01((s + 4.5) / 3.0))
        if mname == "gold" and s < -2.5:
            base = mix(base, GOLD_W, 0.4 * math.exp(-((lx + 12) ** 2 + (ly + 14) ** 2) / 600.0))
        c = mix(base, OUTL, clamp01((s + 1.8) * 1.2))                  # a 1.5 px outline round every part
        over(acc, c, clamp01((0.6 - s) * 1.6))
    if name == "Smithing":
        for (px, py, sz) in ((34, 58, 6.0), (100, 62, 5.0), (90, 76, 4.0)):
            v = sparkle(X - px, Y - py, sz)
            if v > 0 and glass_sd < -1: over(acc, mix((255, 170, 60), (255, 246, 200), v), v)
    v = sparkle(X - (HI_C + 43.1), Y - (HI_C - 43.1), 9.0)
    if v > 0: over(acc, mix(GLOW, WHITE, 0.7), v)
    return acc


# ---------------------------------------------------------------- the element table
# (stem, kit element, state, w, h, (h border px, v border px) or None, sampler(W, H, X, Y), uniform axes)
def elements():
    E = [("Frame", "page frame body, neutral clear sky (every non-hub page)", "", FR_S, FR_S, (FR_B, FR_B),
          lambda W, H, X, Y: frame_sample("", False, W, H, X, Y), "xy")]
    for hub in HUB_NAMES:
        E.append(("Frame_%s" % hub, "page frame body, %s hub mood: %s" % (hub, MOODS[hub][0].lower()), hub.lower(), FR_S, FR_S,
                  (FR_B, FR_B), (lambda h: lambda W, H, X, Y: frame_sample(h, False, W, H, X, Y))(hub), "xy"))
    E += [("Header", "page title bar (38 UI high)", "", HD_W, HD_H, (HD_HB, 0), header_sample, "x"),
          ("HeaderOrnament", "crest over the title bar (fixed 236 x 22 UI, like vanilla's Top -12 decoration)", "", HO_W, HO_H, None,
           ornament_sample, ""),
          ("CardFrame", "card frame (Smithing set cards, Profiles cards, hub tiles)", "", FR_S, FR_S, (FR_B, FR_B),
           lambda W, H, X, Y: frame_sample("", True, W, H, X, Y), "xy")]
    for st, sfx in (("normal", ""), ("hovered", "_Hovered"), ("pressed", "_Pressed"), ("selected", "_Selected")):
        E.append(("Tab" + sfx, "hub bar tab (44 UI high, good down to 110 UI wide)", st, 240, 88, (TB_HB, 24),
                  (lambda s: lambda W, H, X, Y: tab_sample(s, W, H, X, Y))(st), "x"))
    fams = [("Primary", 48, ["normal", "hovered", "pressed", "disabled"], 440, 88),
            ("Secondary", 24, ["normal", "hovered", "pressed", "disabled"], 440, 88),
            ("Tertiary", 24, ["normal", "hovered", "pressed", "active"], 256, 64),
            ("Danger", 24, ["normal", "hovered", "pressed"], 440, 88)]
    for fam, hb, states, w, h in fams:
        for st in states:
            stem = fam + ("" if st == "normal" else "_" + st.capitalize())
            E.append((stem, "%s button" % fam.lower(), st, w, h, (hb, 24),
                      (lambda f, s, b: lambda W, H, X, Y: button_sample(f, s, b, W, H, X, Y))(fam, st, hb), "x"))
    for st, sfx in (("normal", ""), ("hovered", "_Hovered")):
        E.append(("Close" + sfx, "close X (fixed 32 x 32 UI)", st, 64, 64, None,
                  (lambda s: lambda W, H, X, Y: close_sample(s, W, H, X, Y))(st), ""))
    E += [("Panel", "panel / inner well (lists, info boxes)", "", 64, 64, (24, 24), panel_sample, "xy"),
          ("PanelInset", "sub-box inside a panel", "", 48, 48, (16, 16), inset_sample, "xy")]
    for st, sfx in (("normal", ""), ("hovered", "_Hovered"), ("selected", "_Selected")):
        E.append(("Row" + sfx, "list row (replaces the colour rows)", st, 64, 48, (16, 16),
                  (lambda s: lambda W, H, X, Y: row_sample(s, W, H, X, Y))(st), "xy"))
    for st, sfx in (("normal", ""), ("hovered", "_Hovered"), ("selected", "_Selected")):
        E.append(("InputBox" + sfx, "text / search field", st, 96, 64, (32, 32),
                  (lambda s: lambda W, H, X, Y: input_sample(s, 32, W, H, X, Y))(st), "xy"))
    E += [("CheckBox", "check box frame (22 x 22 UI)", "", 44, 44, (14, 14), lambda W, H, X, Y: input_sample("hovered", 14, W, H, X, Y), "xy"),
          ("CheckMark", "check mark (16 x 16 UI)", "", 32, 32, None, checkmark_sample, ""),
          ("ScrollTrack", "scrollbar track (ScrollbarStyle Background)", "", 12, 24, (6, 6),
           lambda W, H, X, Y: scroll_sample("track", W, H, X, Y), "xy")]
    for st, sfx in (("normal", ""), ("hovered", "_Hovered"), ("dragged", "_Dragged")):
        E.append(("ScrollHandle" + sfx, "scrollbar handle", st, 12, 24, (6, 6),
                  (lambda s: lambda W, H, X, Y: scroll_sample(s, W, H, X, Y))(st), "xy"))
    E += [("Separator", "thin gold separator line (2 UI high)", "", 64, 4, (16, 0), separator_sample, "x"),
          ("SlotEmpty", "empty item well (74 x 74 UI, tooltip-sky Slot family)", "", 148, 148, None, slot_sample, "")]
    return E


def widen(img, hb, w, vb, h):
    """expand a narrow render (2 x border + 4 px) to the final size by repeating the (uniform) strip column / row"""
    if hb:
        img = [r[:hb] + [list(r[hb]) for _ in range(w - 2 * hb)] + r[len(r) - hb:] for r in img]
    if vb:
        img = img[:vb] + [[list(p) for p in img[vb]] for _ in range(h - 2 * vb)] + img[len(img) - vb:]
    return img


def render_job(i):
    E = elements()
    if i < len(E):
        stem, _el, _st, w, h, hv, fn, uni = E[i]
        hb = hv[0] if hv and "x" in uni else 0
        vb = hv[1] if hv and "y" in uni else 0
        wn = 2 * hb + 4 if hb else w
        hn = 2 * vb + 4 if vb else h
        img = T.render(lambda X, Y: fn(wn, hn, X, Y), wn, hn, 1.0, SS)
        return stem, widen(img, hb, w, vb, h)
    k = i - len(E)
    img = T.render(lambda X, Y: hub_sample(k, HI, HI, X, Y), HI, HI, 1.0, 3)
    return "HubIcon_" + HUBS[k][0], img


def hard_alpha(img):
    return [[[p[0], p[1], p[2], 255] if p[3] >= 128 else [0, 0, 0, 0] for p in row] for row in img]


def build_all(procs=None):
    """-> {rel path: (image, png bytes)}"""
    n = len(elements()) + len(HUBS)
    with Pool(procs or min(n, os.cpu_count() or 4)) as pool:
        res = pool.map(render_job, range(n))
    out = {}
    for stem, img in res:
        out["%s/%s@2x.png" % (KIT, stem)] = img
        if stem.startswith("HubIcon_"):
            out["%s/%s.png" % (KIT, stem)] = hard_alpha(P.downsample(img, 2))
    return {k: (v, T.png_bytes(v)) for k, v in out.items()}


# ---------------------------------------------------------------- contrast (text colours of tools/skyyui.py COLOR, read only)
TXT = {"text": "#96a9be", "white": "#ffffff", "title": "#b4c8c9", "panelTitle": "#afc2c3", "section": "#9aacbc",
       "caption": "#878e9c", "captionLight": "#5a6a7a", "rowName": "#d6e4ee", "rowSub": "#7f93a6", "rowBadge": "#9aacbc",
       "buttonText": "#bfcdd5", "button2Text": "#bdcbd3", "disabled": "#797b7c", "placeholder": "#6e7da1", "value": "#b7cedd",
       "propKey": "#7a8a9a", "summary": "#8fa6ba", "gold": "#E8A93B", "error": "#ff6b6b", "success": "#39f493",
       "warning": "#ffcc00", "info": "#7caacc", "Legendary": "#55FFFF", "Mythic": "#CC66CC", "Fabled": "#FF5555", "Rare": "#FF55FF"}
PAGE_TXT = ["text", "white", "title", "rowName", "value", "summary", "caption", "section", "gold", "error", "success", "warning",
            "info", "Legendary", "Mythic", "Fabled", "Rare"]
# stem -> ((column x, rows y0..y1 where text sits, @2x px), colours that must reach 4.5:1, colours only reported)
CONTRAST = {"Frame": ((80, 70, 90), PAGE_TXT, ["captionLight", "propKey", "disabled"]),
            "CardFrame": ((80, 70, 90), PAGE_TXT, ["captionLight", "propKey", "disabled"]),
            "Header": ((300, 30, 46), ["title"], []),
            "Panel": ((32, 28, 36), ["text", "white", "panelTitle", "rowName", "value", "propKey", "summary", "caption", "gold",
                                     "success", "error", "info", "Legendary", "Mythic"], ["captionLight", "disabled"]),
            "PanelInset": ((24, 20, 28), ["text", "white", "value", "propKey", "summary", "caption", "gold"], ["captionLight"]),
            "Tab": ((120, 30, 58), ["button2Text"], []), "Tab_Hovered": ((120, 30, 58), ["button2Text"], []),
            "Tab_Pressed": ((120, 30, 58), ["button2Text"], []), "Tab_Selected": ((120, 30, 58), ["buttonText", "button2Text"], []),
            "SlotEmpty": ((74, 60, 88), [], ["white"])}
for _h in HUB_NAMES: CONTRAST["Frame_" + _h] = CONTRAST["Frame"]
for _s in ("", "_Hovered", "_Selected"):
    CONTRAST["Row" + _s] = ((32, 20, 28), ["rowName", "rowSub", "rowBadge", "text", "white", "gold"], [])
    CONTRAST["InputBox" + _s] = ((48, 26, 38), ["white", "text"], ["placeholder"])
for _f, _lab, _sts in (("Primary", "buttonText", ("", "_Hovered", "_Pressed")), ("Secondary", "button2Text", ("", "_Hovered", "_Pressed")),
                       ("Tertiary", "button2Text", ("", "_Hovered", "_Pressed", "_Active")), ("Danger", "buttonText", ("", "_Hovered", "_Pressed"))):
    for _s in _sts:
        CONTRAST[_f + _s] = ((220 if _f != "Tertiary" else 128, 30, 58) if _f != "Tertiary" else (128, 22, 42), [_lab], [])
for _f in ("Primary", "Secondary"):
    CONTRAST[_f + "_Disabled"] = ((220, 30, 58), [], ["disabled"])


def contrast_table(files):
    out = {}
    for stem, ((x, y0, y1), need, extra) in CONTRAST.items():
        img = files["%s/%s@2x.png" % (KIT, stem)][0]
        px = [tuple(img[y][x][:3]) for y in range(y0, y1 + 1)]
        row = {k: round(min(T.contrast(T.hx(TXT[k]), p) for p in px), 2) for k in need + extra}
        mn = min([row[k] for k in need] or [99.0])
        c = px[len(px) // 2]
        out[stem] = {"bg_centre": "#%02x%02x%02x" % c, "column": x, "rows_checked": [y0, y1], "ratios": row,
                     "must_reach_4_5": need, "report_only": extra, "min_required": round(mn, 2)}
    return out


# ---------------------------------------------------------------- sheet
def nine(img, hb, vb, W, H):
    """client-like 9-slice (stretch, nearest): hb / vb border in texture px (0 = that axis scales whole)"""
    w, h = P.size(img)
    def src(v, full, out_full, b):
        if b == 0: return min(full - 1, v * full // max(1, out_full))
        if v < b: return v
        if v >= out_full - b: return full - (out_full - v)
        mid = full - 2 * b
        return b + min(mid - 1, (v - b) * mid // max(1, out_full - 2 * b))
    xs = [src(x, w, W, hb) for x in range(W)]
    return [[img[src(y, h, H, vb)][x] for x in xs] for y in range(H)]


def text_w(s, scale): return len(s) * 6 * scale


class Sheet(T.Canvas):
    def ctext(self, cx, y, s, c, scale=2, bold=False):
        return self.text(int(cx - text_w(s, scale) / 2), y, s, c, scale, bold)

    def rtext(self, rx, y, s, c, scale=2, bold=False):
        return self.text(rx - text_w(s, scale), y, s, c, scale, bold)


def C(k): return T.hx(TXT[k])


def make_sheet(files, table):
    E = elements()
    meta = {e[0]: e for e in E}
    one = {e[0]: P.downsample(files["%s/%s@2x.png" % (KIT, e[0])][0], 2) for e in E}
    icon2 = {h[0]: files["%s/HubIcon_%s@2x.png" % (KIT, h[0])][0] for h in HUBS}
    icon1 = {h[0]: files["%s/HubIcon_%s.png" % (KIT, h[0])][0] for h in HUBS}

    def put(cv, stem, x, y, w, h):
        hv = meta[stem][5] or (0, 0)
        cv.blit(nine(one[stem], hv[0] // 2, hv[1] // 2, w, h), x, y)

    def label_btn(cv, stem, x, y, w, h, s, col):
        cv.ctext(x + w // 2, y + (h - 14) // 2 + (1 if "Pressed" in stem else 0), s, col, 2, bold=True)

    def page(cv, ox, oy, PW, PH, frame, title):
        put(cv, frame, ox, oy + 38, PW, PH - 38)
        put(cv, "Header", ox, oy, PW, 38)
        cv.blit(one["HeaderOrnament"], ox + PW // 2 - 118, oy - 12)
        cv.ctext(ox + PW // 2, oy + 13, title, C("title"), 2, bold=True)

    W, H = 2100, 6400
    cv = Sheet(W, H, (24, 28, 40))
    for yy in range(0, H, 40):
        for xx in range(0, W, 40):
            if (xx // 40 + yy // 40) % 2: cv.fill(xx, yy, xx + 40, yy + 40, (28, 32, 46))
    cv.text(24, 18, "SKYWYNN UI KIT - SKY WINDOW (ISLES OF THE VOID) - DRAFT V1", (255, 236, 170), 4, bold=True)
    cv.text(24, 62, "EVERY MENU / HUB PAGE IN THE TOOLTIP THEME SKYY APPROVED, EACH HUB WITH ITS OWN MOOD IN THE CORNER WINDOWS. "
            "ALL PIXELS ORIGINAL.", (200, 206, 224), 2)
    cv.text(24, 84, "MOCKS ARE AT UI SCALE 1 (1080P) FROM THE REAL TEXTURES (1X = @2X / 2). 5X7 STAND-IN FONT; THE GAME FONT IS "
            "NARROWER. ITEM NAMES ARE PLACEHOLDERS.", (150, 156, 176), 2)

    # ------------------------------------------------ mock 1: Storage hub (1100 x 860 UI), hub bar + sub tabs
    ox, oy = 40, 160
    T.game_bg(cv, ox - 20, oy - 34, 1140, 930, 3)
    PW, PH = 1100, 860
    page(cv, ox, oy, PW, PH, "Frame_Storage", "STORAGE")
    pad = 24
    ix0, iy0, iw = ox + pad, oy + 38 + pad, PW - 2 * pad
    hubs = [("CHARACTER", "Tab"), ("STORAGE", "Tab_Selected"), ("MARKET", "Tab_Hovered"), ("SMITHING", "Tab_Pressed"),
            ("WORLD", "Tab"), ("SOCIAL", "Tab")]
    tw = (iw - 5 * 5) // 6
    tx = ix0
    for nm, st in hubs:
        put(cv, st, tx, iy0, tw, 44)
        label_btn(cv, st, tx, iy0, tw, 44, nm, C("buttonText" if st == "Tab_Selected" else "button2Text"))
        tx += tw + 5
    sy0 = iy0 + 54
    subs = [("POCKET", "Tertiary"), ("REQUIP", "Tertiary_Hovered"), ("VAULT", "Tertiary_Active"), ("BANK", "Tertiary")]
    tx = ix0
    for nm, st in subs:
        put(cv, st, tx, sy0, 150, 32)
        label_btn(cv, st, tx, sy0, 150, 32, nm, C("buttonText" if st.endswith("Active") else "button2Text"))
        tx += 156
    put(cv, "InputBox", ix0 + iw - 360, sy0 - 3, 360, 38)
    cv.text(ix0 + iw - 360 + 12, sy0 + 9, "SEARCH ITEMS...", C("placeholder"), 2)
    put(cv, "Separator", ix0, sy0 + 46, iw, 2)
    px0, py0, pw, ph = ix0, sy0 + 60, 660, 548
    put(cv, "Panel", px0, py0, pw, ph)
    cv.text(px0 + 14, py0 + 12, "VAULT PAGE 3 OF 9", C("panelTitle"), 2, bold=True)
    cv.rtext(px0 + pw - 30, py0 + 12, "41 / 54 SLOTS", C("caption"), 2)
    rows = [("COBBLESTONE", "STONE - 30 STACKS", "X 1920", "Row", (150, 150, 160)),
            ("IRON INGOT", "METAL - RESOURCE", "X 448", "Row_Hovered", (200, 206, 220)),
            ("SKYWARD BLADE", "LEGENDARY SWORD", "X 1", "Row_Selected", C("Legendary")),
            ("COPPER INGOT", "METAL - RESOURCE", "X 96", "Row", (230, 140, 80)),
            ("RUBBLE", "STONE - JUNK", "X 512", "Row", (130, 120, 110)),
            ("STICKS", "WOOD - RESOURCE", "X 240", "Row", (170, 120, 70)),
            ("PLANT FIBRE", "FARMING - RESOURCE", "X 77", "Row", (120, 190, 90)),
            ("SHELLS", "FISHING - RESOURCE", "X 13", "Row", (240, 220, 200))]
    ry = py0 + 40
    rw = pw - 24 - 14
    for nm, sub, badge, st, ic in rows:
        put(cv, st, px0 + 12, ry, rw, 56)
        cv.fill(px0 + 26, ry + 8, px0 + 66, ry + 48, (12, 18, 30)); cv.fill(px0 + 27, ry + 9, px0 + 65, ry + 47, (26, 37, 48))
        for yy in range(-10, 11):
            hw = 10 - abs(yy)
            cv.fill(px0 + 46 - hw, ry + 28 + yy, px0 + 46 + hw, ry + 29 + yy, ic if yy > -4 else mix(ic, WHITE, 0.35))
        cv.text(px0 + 80, ry + 10, nm, C("rowName"), 2, bold=True)
        cv.text(px0 + 80, ry + 32, sub, C("rowSub"), 2)
        cv.rtext(px0 + 12 + rw - 16, ry + 21, badge, C("rowBadge"), 2)
        ry += 59
    put(cv, "ScrollTrack", px0 + pw - 22, py0 + 40, 6, 59 * 8 - 3)
    put(cv, "ScrollHandle_Hovered", px0 + pw - 22, py0 + 110, 6, 150)
    rx0 = px0 + pw + 16; rw2 = ix0 + iw - rx0
    put(cv, "Panel", rx0, py0, rw2, 236)
    cv.text(rx0 + 14, py0 + 12, "SELECTED", C("panelTitle"), 2, bold=True)
    put(cv, "SlotEmpty", rx0 + rw2 - 14 - 74, py0 + 12, 74, 74)
    cv.text(rx0 + 14, py0 + 44, "SKYWARD BLADE", C("Legendary"), 2, bold=True)
    put(cv, "PanelInset", rx0 + 12, py0 + 96, rw2 - 24, 126)
    for k, (key, val, col) in enumerate((("SLOT", "12", "value"), ("AMOUNT", "1", "value"), ("REFORGE", "SHARP", "value"),
                                         ("WORTH", "2400 COINS", "gold"))):
        yk = py0 + 108 + k * 27
        cv.text(rx0 + 24, yk, key, C("propKey"), 2, bold=True)
        cv.text(rx0 + 150, yk, val, C(col), 2)
    by = py0 + 250
    for txt, st, lab in (("WITHDRAW", "Primary_Hovered", "buttonText"), ("MOVE TO POCKET", "Secondary", "button2Text"),
                         ("SELL TO MARKET", "Danger", "buttonText")):
        put(cv, st, rx0, by, rw2, 44); label_btn(cv, st, rx0, by, rw2, 44, txt, C(lab)); by += 50
    half = (rw2 - 6) // 2
    put(cv, "Primary_Disabled", rx0, by, half, 44); label_btn(cv, "x", rx0, by, half, 44, "UPGRADE", C("disabled"))
    put(cv, "Secondary_Pressed", rx0 + half + 6, by, half, 44)
    label_btn(cv, "Pressed", rx0 + half + 6, by, half, 44, "SPLIT", C("button2Text"))
    by += 56
    put(cv, "CheckBox", rx0, by + 2, 22, 22); cv.blit(one["CheckMark"], rx0 + 3, by + 5)
    cv.text(rx0 + 32, by + 6, "KEEP 1 IN VAULT", C("text"), 2)
    by += 34
    cv.text(rx0, by, "AMOUNT TO WITHDRAW", C("text"), 2, bold=True)
    put(cv, "InputBox_Selected", rx0, by + 22, rw2, 38)
    e = cv.text(rx0 + 12, by + 34, "64", C("white"), 2)
    cv.fill(e + 2, by + 31, e + 4, by + 51, (230, 236, 246))
    fy = oy + PH - pad - 44
    put(cv, "Separator", ix0, fy - 12, iw, 2)
    put(cv, "Secondary", ix0 + 20, fy, 172, 44); label_btn(cv, "x", ix0 + 20, fy, 172, 44, "CLOSE", C("button2Text"))
    put(cv, "Secondary_Hovered", ix0 + 198, fy, 172, 44); label_btn(cv, "x", ix0 + 198, fy, 172, 44, "BACK", C("button2Text"))
    cv.text(ix0 + 390, fy + 15, "+ DEPOSITED 64 IRON INGOT", C("success"), 2)
    put(cv, "Primary", ix0 + iw - 20 - 220, fy, 220, 44)
    label_btn(cv, "x", ix0 + iw - 20 - 220, fy, 220, 44, "DEPOSIT ALL", C("buttonText"))
    put(cv, "Close", ox + PW - 40, oy + 3, 32, 32)
    for k, line in enumerate(("MOCK 1 - STORAGE HUB, FRAME_STORAGE (NIGHT VAULT), 1100 X 860 UI, PADDING 24",
                              "HUB BAR: STORAGE SELECTED, MARKET HOVERED, SMITHING PRESSED",
                              "SUB TABS = TERTIARY (VAULT ACTIVE). ROWS: NORMAL, HOVERED, SELECTED",
                              "WITHDRAW = PRIMARY HOVERED, MOVE = SECONDARY, SELL = DANGER",
                              "UPGRADE = PRIMARY DISABLED, SPLIT = SECONDARY PRESSED, BACK = SECONDARY HOVERED")):
        cv.text(ox, oy + PH + 24 + 22 * k, line, (220, 224, 236) if k == 0 else (180, 186, 204), 2)

    # ------------------------------------------------ mock 2: the hub tiles (neutral Frame, CardFrame tiles)
    hx0, hy0 = 1220, 160
    HW, HH = 820, 520
    T.game_bg(cv, hx0 - 20, hy0 - 34, HW + 40, HH + 56, 7)
    page(cv, hx0, hy0, HW, HH, "Frame", "SKYWYNN MENU")
    caps = {"Character": "PROFILE, SKILLS", "Storage": "VAULT, BANK", "Market": "BAZAAR, AUCTION", "Smithing": "CRAFT, REFORGE",
            "World": "TELEPORT, ISLES", "Social": "PARTY, GUILD"}
    tw_, th_, gap = 238, 196, 14
    gx0 = hx0 + (HW - 3 * tw_ - 2 * gap) // 2
    for k, (nm, *_r) in enumerate(HUBS):
        cx_ = gx0 + (k % 3) * (tw_ + gap); cy_ = hy0 + 38 + 34 + (k // 3) * (th_ + gap)
        put(cv, "CardFrame", cx_, cy_, tw_, th_)
        cv.blit(icon1[nm], cx_ + tw_ // 2 - 32, cy_ + 28)
        cv.ctext(cx_ + tw_ // 2, cy_ + 112, nm.upper(), C("title"), 2, bold=True)
        cv.ctext(cx_ + tw_ // 2, cy_ + 138, caps[nm], C("caption"), 2)
    cv.text(hx0, hy0 + HH + 24, "MOCK 2 - THE SIX HUB TILES (NEUTRAL FRAME, CARDFRAME TILES, HUB ICONS AT 64 UI).", (220, 224, 236), 2)
    # the 7 frame moods, each as a small page at UI scale 1
    fy0 = oy + PH + 150
    cv.text(40, fy0, "THE PAGE FRAME IN EVERY MOOD (360 X 240 UI EACH):", (255, 236, 170), 2, bold=True)
    fy0 += 30
    variants = [("Frame", "NEUTRAL")] + [("Frame_" + h, h.upper()) for h in HUB_NAMES]
    for k, (stem, nm) in enumerate(variants):
        x_ = 50 + (k % 4) * 510; y_ = fy0 + 40 + (k // 4) * 300
        T.game_bg(cv, x_ - 10, y_ - 22, 380, 290, k)
        page(cv, x_, y_, 360, 240, stem, nm)
        cv.text(x_ + 26, y_ + 38 + 30, (MOODS[stem[6:]][0] if stem != "Frame" else MOODS[""][0]), C("text"), 2)
        cv.text(x_ + 26, y_ + 38 + 56, "BODY TEXT STAYS READABLE", C("rowName"), 2, bold=True)
        cv.text(x_ + 26, y_ + 38 + 80, "CAPTION LINE", C("caption"), 2)
    y = fy0 + 40 + 2 * 300 + 10

    # ------------------------------------------------ hub icons
    cv.fill(16, y - 10, W - 16, y + 34, (40, 46, 64))
    cv.text(28, y, "HUB ICONS - 64 PX (ITEM-ICON SIZE, HARD ALPHA) ON DARK + LIGHT, AND THE @2X 128 PX FILE", (255, 236, 170), 2, bold=True)
    y += 50
    moodn = {"Character": "SUNRISE", "Storage": "NIGHT VAULT", "Market": "GOLDEN NOON", "Smithing": "EMBER FORGE", "World": "CLEAR SKY",
             "Social": "SUNSET"}
    for k, (nm, *_r) in enumerate(HUBS):
        x_ = 28 + k * 340
        cv.blit(icon1[nm], x_, y)
        cv.fill(x_ + 72, y, x_ + 72 + 64, y + 64, (214, 222, 232)); cv.blit(icon1[nm], x_ + 72, y)
        cv.blit(icon2[nm], x_ + 150, y)
        cv.text(x_, y + 80, nm.upper(), (220, 224, 236), 2, bold=True)
        cv.text(x_, y + 100, moodn[nm], (150, 156, 176), 2)
    y += 160

    # ------------------------------------------------ every element raw with its 9-slice cuts + stretched at 1x
    cv.fill(16, y - 10, W - 16, y + 34, (40, 46, 64))
    cv.text(28, y, "THE ELEMENTS - RAW @2X TEXTURE (X2 WHEN SMALL) ON CHECKER, DASHED = 9-SLICE CUTS, THEN STRETCHED AT 1X",
            (255, 236, 170), 2, bold=True)
    y += 50
    demo = {"Frame": (300, 200), "CardFrame": (240, 180), "Header": (500, 38), "Panel": (300, 140), "PanelInset": (240, 90),
            "ScrollTrack": (6, 140), "Separator": (300, 2), "CheckBox": (22, 22)}
    x = 28; rowh = 0
    for stem, el, st, w, h, hv, _fn, uni in E:
        if stem.startswith("Frame_"): continue                       # shown above as small pages
        z = 2 if w <= 200 else 1
        raw = files["%s/%s@2x.png" % (KIT, stem)][0]
        if hv is None: dw, dh = 0, 0
        elif stem in demo: dw, dh = demo[stem]
        elif stem.startswith(("Row",)): dw, dh = 360, 56
        elif stem.startswith("InputBox"): dw, dh = 300, 38
        elif stem.startswith("ScrollHandle"): dw, dh = 6, 60
        elif stem.startswith("Tertiary"): dw, dh = 150, 32
        else: dw, dh = 200, 44
        cw = max(w * z, dw, 230) + 30
        chh = h * z + (dh + 16 if dw else 0) + 60
        if x + cw > W - 20: x = 28; y += rowh + 20; rowh = 0
        for yy in range(0, h * z, 8):
            for xx in range(0, w * z, 8):
                cv.fill(x + xx, y + yy, x + min(xx + 8, w * z), y + min(yy + 8, h * z), (70, 74, 88) if (xx // 8 + yy // 8) % 2 else (54, 58, 72))
        cv.blit(raw, x, y, z)
        if hv:
            for q in ([hv[0], w - hv[0]] if hv[0] else []):
                for t in range(0, h * z, 6): cv.fill(x + q * z, y + t, x + q * z + 1, y + t + 3, (255, 255, 255))
            for q in ([hv[1], h - hv[1]] if hv[1] else []):
                for t in range(0, w * z, 6): cv.fill(x + t, y + q * z, x + t + 3, y + q * z + 1, (255, 255, 255))
        yy = y + h * z + 8
        if dw:
            cv.fill(x - 4, yy - 4, x + dw + 4, yy + dh + 4, (20, 24, 36))
            put(cv, stem, x, yy, dw, dh)
            if dh >= 32 and stem.startswith(("Tab", "Primary", "Secondary", "Tertiary", "Danger")):
                lab = "buttonText" if stem.startswith(("Primary", "Danger")) or stem in ("Tab_Selected", "Tertiary_Active") else "button2Text"
                if stem.endswith("Disabled"): lab = "disabled"
                label_btn(cv, stem, x, yy, dw, dh, "LABEL", C(lab))
            if stem.startswith("Row"):
                cv.text(x + 14, yy + 10, "ROW NAME", C("rowName"), 2, bold=True); cv.text(x + 14, yy + 32, "ROW SUB LINE", C("rowSub"), 2)
            if stem.startswith("InputBox"):
                cv.text(x + 12, yy + 12, "PLACEHOLDER" if stem == "InputBox" else "TYPED TEXT", C("placeholder" if stem == "InputBox" else "white"), 2)
            yy += dh + 16
        bt = ("BORDER %d UI" % (hv[0] // 2) if hv[0] == hv[1] else "H %d V %d UI" % (hv[0] // 2, hv[1] // 2)) if hv else "NOT SLICED"
        cv.text(x, yy, stem.upper(), (255, 236, 170), 2, bold=True)
        cv.text(x, yy + 20, "%dX%d @2X  %s" % (w, h, bt), (180, 186, 204), 1)
        if stem in table and table[stem]["must_reach_4_5"]:
            cv.text(x, yy + 32, "MIN TEXT CONTRAST %.1f" % table[stem]["min_required"], (150, 230, 150) if table[stem]["min_required"] >= 4.5 else (255, 140, 120), 1)
        rowh = max(rowh, chh)
        x += cw
    y += rowh + 40
    # ------------------------------------------------ buttons at game size
    cv.fill(16, y - 10, W - 16, y + 34, (40, 46, 64))
    cv.text(28, y, "BUTTONS AT GAME SIZE (1X): NORMAL 172 X 44 AND SMALL 150 X 32 (TERTIARY: 150 X 32 AND 110 X 32)",
            (255, 236, 170), 2, bold=True)
    y += 50
    for fam, lab, sts in (("Primary", "buttonText", ("", "_Hovered", "_Pressed", "_Disabled")),
                          ("Secondary", "button2Text", ("", "_Hovered", "_Pressed", "_Disabled")),
                          ("Danger", "buttonText", ("", "_Hovered", "_Pressed")),
                          ("Tertiary", "button2Text", ("", "_Hovered", "_Pressed", "_Active"))):
        x = 28
        cv.text(x, y + 15, fam.upper(), (220, 224, 236), 2, bold=True)
        x += 130
        sizes = ((172, 44), (150, 32)) if fam != "Tertiary" else ((150, 32), (110, 32))
        for s in sts:
            stem = fam + s
            for (bw, bh) in sizes:
                put(cv, stem, x, y + (48 - bh) // 2, bw, bh)
                l2 = "disabled" if s == "_Disabled" else ("buttonText" if s == "_Active" else lab)
                label_btn(cv, stem, x, y + (48 - bh) // 2, bw, bh, (s[1:] or "NORMAL").upper(), C(l2))
                x += bw + 6
            x += 10
        y += 66
    y += 20
    # ------------------------------------------------ contrast table
    cv.fill(16, y - 10, W - 16, y + 34, (40, 46, 64))
    cv.text(28, y, "TEXT CONTRAST - LOWEST WCAG RATIO OVER THE TEXT ROWS; MUST REACH 4.5 EXCEPT REPORT-ONLY", (255, 236, 170), 2, bold=True)
    y += 46
    for stem, t in table.items():
        need = " ".join("%s %.1f" % (k.upper(), t["ratios"][k]) for k in t["must_reach_4_5"])
        rep = " ".join("%s %.1f" % (k.upper(), t["ratios"][k]) for k in t["report_only"])
        cv.text(28, y, "%s %s" % (stem.upper(), t["bg_centre"].upper()), (220, 224, 236), 1)
        cv.text(300, y, need + ("   REPORT ONLY: " + rep if rep else ""), (150, 230, 150) if t["min_required"] >= 4.5 else (255, 140, 120), 1)
        y += 14
    y += 30
    out = T.Canvas(W, y, (24, 28, 40))
    out.px[:] = cv.px[:W * y * 4]
    return out.png()


# ---------------------------------------------------------------- manifest
def border_ui(hv):
    if hv is None: return None
    if hv[0] == hv[1]: return {"Border": hv[0] // 2}
    return {"HorizontalBorder": hv[0] // 2, "VerticalBorder": hv[1] // 2}


def skyyui_use(stem):
    if stem == "Frame" or stem.startswith("Frame_"):
        return "page_shell body: replaces ContainerPatch.png (Border 23) - Frame on every page, Frame_<Hub> on that hub's pages; padding 24"
    fixed = {"Header": "page_shell title bar: replaces ContainerHeader.png (HorizontalBorder 50, VerticalBorder 0)",
             "HeaderOrnament": "page_shell decorated: replaces ContainerDecorationTop.png (Group Width 236, Height 22, Top -12); "
                               "drop ContainerDecorationBottom",
             "CardFrame": "card / tile background (list_card, hub tiles, Smithing set cards, Profiles cards)",
             "Panel": "panel(kind simple / full): replaces ContainerPanelPatch.png (Border 4) / ContainerFullPatch.png (Border 20)",
             "PanelInset": "panel(kind well / secondary): replaces #000000(0.15) / ContainerBackgroundSecondary.png",
             "CheckBox": "checkbox_style Background: replaces CheckBoxFrame.png (Border 7)",
             "CheckMark": "checkbox_style checked: replaces Checkmark.png",
             "ScrollTrack": "scrollbar_style Background: replaces Scrollbar.png (Border 3; Size 6, Spacing 6 unchanged)",
             "Separator": "separator(content / form / fancy): a Group Height 2 with this background (HorizontalBorder 8, VerticalBorder 0)",
             "SlotEmpty": "item_frame / icon_cell empty well (if probe K1(c) lets ItemGrid slots take a texture)",
             "Close": "close_button Default", "Close_Hovered": "close_button Hovered + Pressed"}
    if stem in fixed: return fixed[stem]
    if stem.startswith("Tab"): return "tab_row / hub_bar_markup: tab %s" % (stem[4:] or "Default").lower()
    if stem.startswith("Row"): return "row_style / hover_row: %s (replaces the colour rows)" % (stem[4:] or "Default").lower()
    if stem.startswith("InputBox"): return "text_field / search_field / value_box: %s (vanilla InputBox*.png, Border 16)" % (stem[9:] or "Default").lower()
    if stem.startswith("ScrollHandle"): return "scrollbar_style %s" % {"": "Handle", "_Hovered": "HoveredHandle", "_Dragged": "DraggedHandle"}[stem[12:]]
    fam, _, st = stem.partition("_")
    return "button_style(kind=%s) %s" % ({"Danger": "destructive"}.get(fam, fam.lower()), st or "Default")


def main():
    files = build_all()
    table = contrast_table(files)
    for stem, t in table.items():
        flag = "ok " if t["min_required"] >= 4.5 else "LOW"
        print("  %s %-22s bg %s  %s" % (flag, stem, t["bg_centre"], " ".join("%s %.2f" % kv for kv in t["ratios"].items())))
    for rel, (img, data) in files.items():
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh: fh.write(data)
    sheet = make_sheet(files, table)
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh: fh.write(sheet)
    E = elements()
    man = {"what": "SkyWynn UI kit - SKY WINDOW theme (Isles of the Void), research/Hubs-Spec.md 7.3 element list + per-hub page "
                   "frame moods + hub icons. DRAFT v1, not wired in.",
           "generator": "tools/art/make_ui_kit_sky.py", "validator": "tools/art/validate_ui_kit_sky.py",
           "deterministic": True, "original_pixels": True, "scale": "@2x = 2 texture px per UI unit; border values are UI units",
           "jar_root": KIT + "/", "markup_path": INLINE + "/<Element>.png (no @2x; relative to Common/UI/Custom/)",
           "hub_frames": {h: "Frame_" + h for h in HUB_NAMES}, "hub_moods": {h: MOODS[h][0] for h in HUB_NAMES},
           "elements": [], "hub_icons": [], "files": [], "contrast": table,
           "sheet": {"path": "sheet.png", "bytes": len(sheet), "sha256": hashlib.sha256(sheet).hexdigest()}}
    for stem, el, st, w, h, hv, _fn, uni in E:
        rel = "%s/%s@2x.png" % (KIT, stem)
        data = files[rel][1]
        man["elements"].append({"element": stem, "file": rel, "markup_path": "%s/%s.png" % (INLINE, stem), "kit_element": el,
                                "state": st or "default", "w": w, "h": h, "ui_size": [w // 2, h // 2], "border": border_ui(hv),
                                "strip_uniform": uni, "skyyui_use": skyyui_use(stem), "bytes": len(data),
                                "sha256": hashlib.sha256(data).hexdigest()})
    for nm, rid, _m, kind, ci in HUBS:
        for sfx, size in (("@2x", 128), ("", 64)):
            rel = "%s/HubIcon_%s%s.png" % (KIT, nm, sfx)
            data = files[rel][1]
            man["hub_icons"].append({"file": rel, "hub": nm, "mood": MOODS[nm][0], "w": size, "h": size, "border": None,
                                     "markup_path": "%s/HubIcon_%s.png" % (INLINE, nm),
                                     "use": "hub tile icon: 64 x 64 UI via the @2x file; the plain 64 px file = item-icon size, hard alpha",
                                     "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    for rel in sorted(files):
        data = files[rel][1]; w, h = P.size(files[rel][0])
        man["files"].append({"path": rel, "w": w, "h": h, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(man, fh, indent=1); fh.write("\n")
    print("wrote %d textures + sheet.png (%d bytes) + manifest.json to %s" % (len(files), len(sheet), OUT))


if __name__ == "__main__":
    main()
