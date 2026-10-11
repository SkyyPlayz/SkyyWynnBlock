#!/usr/bin/env python3
"""SkyyGear rarity tooltip backgrounds + arrows + slot frames - "magic scroll" family (DRAFT v1, all ORIGINAL pixels).

Skyy 2026-10-10: "can we design cool images with the rarity color bonuses? and can we do custom shaped borders, for cool custom
frame shapes?" then "lets start normal with a cool magic scroll look." -> every rarity is a scroll (parchment rim, rolled ends on the
LEFT and RIGHT, a dark ink-washed text area); it gets more magical with rarity (brass / silver / gold / obsidian knobs, gems, filigree,
glowing runes, flames) and each rarity keeps its own colour.

Writes art/tooltip-frames/:
  Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>@2x.png        107 x 107 (vanilla ItemTooltip*@2x size), 9-slice border 48 px (= 24 UI units)
  Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>.png           54 x 54   1x, border 24 px
  Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>Arrow@2x.png   66 x 48   (vanilla arrow size; drawn at 33 x 24 UI units, Bottom: -8)
  Common/UI/SkyyGear/Tooltips/Tooltip_<Rarity>Arrow.png      33 x 24
  Common/UI/SkyyGear/Slots/Slot_<Rarity>@2x.png              148 x 148 (vanilla Slot*@2x size = 74 UI units)
  Common/UI/SkyyGear/Slots/Slot_<Rarity>.png                 74 x 74
  sheet.png, manifest.json
Run: python tools/art/make_tooltip_frames.py   (deterministic)      Check: python tools/art/validate_tooltip_frames.py
Pure Python 3 (no Pillow); PNG helpers + 5x7 font from tools/art/emblem_png.py.

9-SLICE RULES (from the client's InGame/Tooltips/ItemTooltip.ui: Background (TexturePath, Border: 24); the @2x file is 107 px):
  the tooltip is drawn on a 108 px design canvas; columns / rows 48..59 are the stretch strip: there the shader ignores the
  coordinate along the strip (it is told "far from any corner"), so every strip pixel only depends on its depth from the edge.
  Column 54 and row 54 are then dropped -> 107 px with an 11 px strip (48..58), like vanilla. Corner art lives only inside the
  48 x 48 corner patches; edges carry only things that are the same all along them (the rolls, the parchment band, the ink lines).
"""
import hashlib, json, math, os, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "art", "tooltip-frames")
TIP_DIR = "Common/UI/SkyyGear/Tooltips"
SLOT_DIR = "Common/UI/SkyyGear/Slots"
SS = 4                      # supersampling per axis
BIG = 1.0e4                 # "far from the corner" (stretch strip)
CAN = 108                   # tooltip design canvas (@2x units)
BORDER2X = 48               # 9-slice border in @2x pixels (= Border: 24 UI units)
BODY = (22, 21, 86, 86)     # parchment sheet rect on the 108 canvas (x0, y0, x1, y1) = vanilla box placement
SLOT2X = 148
ARROW2X = (66, 48)

# (id, Name, rarity hex = SkyyGear RARITIES text colour)
RARITIES = [
    ("normal", "Normal", "#FFFFFF"), ("unique", "Unique", "#FFFF55"), ("rare", "Rare", "#FF55FF"),
    ("legendary", "Legendary", "#55FFFF"), ("fabled", "Fabled", "#FF5555"), ("mythic", "Mythic", "#CC66CC"),
    ("set", "Set", "#55FF55"), ("untiered", "Untiered", "#FFAA00"),
]


def hx(s):
    s = s.lstrip("#"); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def mix(a, b, t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def mul(a, f):
    return (min(255, a[0] * f), min(255, a[1] * f), min(255, a[2] * f))


def clamp01(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


# ---------------------------------------------------------------- shared palette
OUTL = (36, 24, 22)          # ink outline (warm near-black)
PARCH = (214, 190, 146)      # parchment
PARCH_D = (150, 118, 82)
PARCH_L = (238, 222, 184)
WASH = (72, 57, 50)          # ink wash next to the rim
C_IN = (27, 24, 31)          # text area (dark ink-washed slate) - white / grey / green / red text must read on it
WOOD = (120, 78, 44)
METALS = {"wood": (122, 80, 46), "brass": (196, 160, 70), "silver": (176, 184, 198), "gold": (226, 176, 58),
          "obsidian": (52, 36, 70), "charred": (70, 44, 32)}
GOLD = METALS["gold"]

# per rarity look. trim = ink line colour; knob = knob metal; glyph = (colour, strength 0..1, glow);
# glow = (colour, inner wash strength, shadow alpha); sheet = sheet-corner shape
STYLE = {
    "normal":    dict(trim=(104, 74, 50), knob="wood", glyph=((92, 64, 42), 0.45, False), glow=None, sheet=("square",),
                      roll_lines=False, double=None, shadow=((0, 0, 0), 30)),
    "unique":    dict(trim=hx("#FFFF55"), knob="brass", glyph=((150, 120, 30), 0.55, False), glow=(hx("#FFFF55"), 0.10),
                      sheet=("notch", 7), roll_lines=True, double=None, shadow=((0, 0, 0), 30)),
    "rare":      dict(trim=hx("#FF55FF"), knob="silver", glyph=((150, 50, 150), 0.6, False), glow=(hx("#FF55FF"), 0.12),
                      sheet=("chamfer", 10), roll_lines=True, double=None, shadow=((0, 0, 0), 30)),
    "legendary": dict(trim=hx("#55FFFF"), knob="gold", glyph=((40, 170, 180), 0.8, True), glow=(hx("#55FFFF"), 0.14),
                      sheet=("round", 8), roll_lines=True, double=GOLD, shadow=((20, 60, 70), 40)),
    "fabled":    dict(trim=hx("#FF5555"), knob="gold", glyph=((190, 50, 40), 0.8, True), glow=(hx("#FF5555"), 0.14),
                      sheet=("chamfer", 6), roll_lines=True, double=GOLD, shadow=((40, 0, 0), 44)),
    "mythic":    dict(trim=hx("#CC66CC"), knob="obsidian", glyph=((240, 170, 250), 1.0, True), glow=(hx("#CC66CC"), 0.30),
                      sheet=("chamfer", 9), roll_lines=True, double=(240, 180, 245), shadow=(hx("#CC66CC"), 90)),
    "set":       dict(trim=hx("#55FF55"), knob="wood", glyph=((60, 120, 50), 0.6, False), glow=(hx("#55FF55"), 0.10),
                      sheet=("round", 6), roll_lines=True, double=None, shadow=((0, 0, 0), 30)),
    "untiered":  dict(trim=hx("#FFAA00"), knob="charred", glyph=((255, 150, 40), 0.9, True), glow=(hx("#FFAA00"), 0.20),
                      sheet=("jagged",), roll_lines=True, double=None, shadow=((120, 50, 0), 60)),
}

# 3 x 5 runes (original glyphs), rows top -> bottom
RUNES = ["010111010010010", "111100110100111", "101010010010101", "110101110101110", "011100010001110",
         "100110101011001", "111010010010111", "101101111001001"]


# ---------------------------------------------------------------- primitives (canvas-oriented offsets dx, dy; light from top-left)
def gem(dx, dy, r, col):
    d = abs(dx) + abs(dy)
    if d > r: return None
    if d > r - 1.1: return mul(col, 0.30)
    base = mul(col, 0.62)
    if dx + dy < -0.2: base = mix(col, (255, 255, 255), 0.18)      # lit facet
    elif dx - dy > 0.6: base = mul(col, 0.80)
    if (dx + r * 0.35) ** 2 + (dy + r * 0.35) ** 2 < (r * 0.18 + 0.5) ** 2: base = mix(col, (255, 250, 240), 0.75)
    return base


def ball(dx, dy, r, col):
    d2 = dx * dx + dy * dy
    if d2 > r * r: return None
    if d2 > (r - 1.0) ** 2: return mix(OUTL, col, 0.25)
    nz = math.sqrt(max(0.0, 1 - d2 / (r * r)))
    l = clamp01(0.35 + 0.65 * ((-dx * 0.55 - dy * 0.65) / r + nz * 0.55))
    c = mix(mul(col, 0.45), col, l * 1.25)
    if (dx + r * 0.38) ** 2 + (dy + r * 0.38) ** 2 < (r * 0.22) ** 2: c = mix(c, (255, 248, 230), 0.7)
    return c


def ring(dx, dy, rx, ry, w, col):
    q = math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    rr = (rx + ry) / 2.0
    if abs(q - 1.0) * rr > w: return None
    if abs(q - 1.0) * rr > w - 0.8: return mul(col, 0.35)
    return mix(mul(col, 0.7), mix(col, (255, 255, 255), 0.25), clamp01(0.5 - (dx + dy) / (2 * rr)))


def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
    t = clamp01(((px - ax) * vx + (py - ay) * vy) / L2) if L2 else 0.0
    return math.hypot(px - (ax + vx * t), py - (ay + vy * t)), t


def spike(px, py, ax, ay, bx, by, w, col):
    d, t = seg_dist(px, py, ax, ay, bx, by)
    ww = w * (1 - t) + 0.3
    if d > ww: return None
    if d > ww - 0.9: return mul(col, 0.30)
    return mix(mul(col, 0.65), mix(col, (255, 240, 200), 0.45), clamp01(1 - d / ww) * (1 - t * 0.3))


def leaf(da, db, ang, L, W, col):
    ca, sa = math.cos(ang), math.sin(ang)
    u = da * ca + db * sa; v = -da * sa + db * ca
    if u < 0 or u > L: return None
    half = W * math.sin(math.pi * u / L)
    if abs(v) > half: return None
    if abs(v) > half - 0.9: return mul(col, 0.35)
    if abs(v) < 0.5: return mul(col, 0.6)
    return mix(col, (230, 255, 200), 0.25) if v < 0 else col


def flame(da, db, base_b, tip_b, a0, w0, col):
    """an upward (toward -b) flame tongue from base_b to tip_b around a = a0"""
    if not tip_b <= db <= base_b: return None
    u = (base_b - db) / (base_b - tip_b)
    half = w0 * (1 - u) ** 0.7 + 0.2
    off = abs(da - (a0 + 0.8 * math.sin(u * 5.0)))
    if off > half: return None
    core = 1 - off / half
    return mix(mix(mul(col, 0.7), col, u), (255, 236, 255), core * (1 - u) * 0.85)


def tri(x):
    x = x - math.floor(x); return 2 * x if x < 0.5 else 2 - 2 * x


# ---------------------------------------------------------------- sheet edge profile (depth t from the parchment edge)
def profile(rid, t, lf):
    st = STYLE[rid]
    if t < 1.5: return OUTL
    if t < 7.0:                                           # parchment band
        p = (t - 1.5) / 5.5
        c = PARCH
        if p < 0.22: c = PARCH_L if lf > 0 else mix(PARCH, PARCH_D, 0.3)
        elif p > 0.75: c = mix(PARCH, PARCH_D, 0.55)
        c = mix(c, st["trim"], 0.08 if rid != "normal" else 0.0)
        return mul(c, 1.0 + 0.06 * lf)
    if t < 9.2:                                           # rarity ink line
        c = st["trim"]
        return mix(c, (255, 255, 255), 0.2) if t < 7.8 and lf > 0 else (mul(c, 0.8) if t > 8.6 else c)
    if t < 10.2: return OUTL
    if st["double"] is not None and 11.4 <= t < 12.6:     # second (inner) line: gold / glow
        return st["double"]
    w = clamp01((t - 10.2) / 7.0)
    c = mix(WASH, C_IN, w ** 0.8)
    if st["glow"]:
        c = mix(c, st["glow"][0], st["glow"][1] * (1 - w) ** 2)
    return c


def sheet_depth(rid, a, b, ci):
    """inside distance of the parchment sheet (corner coords; a, b may be BIG)"""
    sa = a - 10.0
    kind = STYLE[rid]["sheet"]
    if kind[0] == "square" or sa >= 30 or b >= 30:
        return min(sa, b)
    if kind[0] == "notch":
        n = kind[1]; dr = min(sa, b)
        dn = (b - n) if sa < n else (sa - n) if b < n else max(sa - n, b - n)
        if sa < n and b < n: dn = -min(n - sa, n - b)
        return min(dr, dn)
    if kind[0] == "chamfer":
        return min(sa, b, (sa + b - kind[1]) / math.sqrt(2))
    if kind[0] == "round":
        r = kind[1]
        if sa < r and b < r: return r - math.hypot(r - sa, r - b)
        return min(sa, b)
    if kind[0] == "jagged":                              # torn / burnt corner, different per corner
        jag = 0.0
        if a < 24:
            fade = clamp01((24 - a) / 10.0)
            jag = (2.0 + 3.0 * tri((a + ci * 2.7) / 3.3)) * fade
        bb = b - jag
        cut = (sa + bb - (5 + 2 * (ci % 3))) / math.sqrt(2)
        return min(sa, bb, cut)
    return min(sa, b)


# ---------------------------------------------------------------- roll (vertical cylinder at a = 3, radius 9; uniform along b)
RC, RR = 3.0, 9.0


def roll_colour(rid, a, b, sx, corner, ci):
    st = STYLE[rid]
    n = (a - RC) / RR                                     # -1 (outer) .. +1 (inner)
    nc = n * sx                                           # canvas-oriented: - = left side
    if abs(n) > 0.88: return OUTL
    base = mix(PARCH, st["trim"], 0.05 if rid != "normal" else 0.0)
    lit = clamp01(0.55 + 0.5 * math.sqrt(max(0.0, 1 - n * n)) - 0.25 * nc)
    c = mix(mul(base, 0.55), mix(base, PARCH_L, 0.4), lit)
    if abs(n - 0.42) < 0.07: c = mul(c, 0.62)             # the paper's curled edge
    if st["roll_lines"] and abs(abs(n) - 0.70) < 0.06: c = mix(c, st["trim"], 0.85)
    if corner and b < BIG:
        if b < -3.5:                                      # end cap ring
            mc = METALS[st["knob"]]
            return mix(mul(mc, 0.6), mc, lit) if b > -5.5 else mul(mc, 0.4)
        # rune band on the roll near each end
        for k, b0 in enumerate((1.5, 13.0)):
            cx = int(math.floor((a - (RC - 3.0)) / 2.0)); cy = int(math.floor((b - b0) / 2.0))
            if 0 <= cx < 3 and 0 <= cy < 5:
                rune = RUNES[(ci * 2 + k + len(rid)) % len(RUNES)]
                if rune[cy * 3 + cx] == "1":
                    gcol, gs, glowing = st["glyph"]
                    return mix(c, gcol, gs) if not glowing else mix(mix(c, gcol, gs), (255, 255, 255), 0.25)
    return c


# ---------------------------------------------------------------- knobs + sheet-corner ornaments (corner patches only)
def knob_and_ornaments(rid, a, b, sx, sy, ci):
    st = STYLE[rid]
    dxk, dyk = (a - RC) * sx, b * sy                      # canvas-oriented offsets from the roll's end
    mc = METALS[st["knob"]]
    # --- extras that sit in FRONT of the knob
    if rid == "mythic":
        for a0, base, tip, w0 in ((RC, -14.0, -21.0, 3.2), (RC - 4.0, -9.5, -15.5, 1.8), (RC + 4.2, -10.0, -16.5, 1.8)):
            c = flame(a, b, base, tip, a0, w0, st["trim"])
            if c: return c
    if rid == "untiered":
        rnd = [(-5, -19, 2.4), (6, -18, 2.2), (-8, -12, 1.8), (9, -11, 1.6)]
        for k, (ex, ey, w) in enumerate(rnd):
            j = ((ci * 5 + k * 3) % 7) - 3
            c = spike(a, b, RC, -9.0, RC + ex + j * 0.7, ey + j * 0.5, w, st["trim"])
            if c: return c
    if rid == "set":
        for ang, L in ((math.radians(-150), 9.0), (math.radians(-30), 9.0)):
            c = leaf(a - RC, b + 8.0, ang, L, 2.8, (70, 170, 60))
            if c: return c
    if rid == "legendary":
        for side in (-1, 1):
            c = ring(a - (RC + side * 5.5), b + 12.0, 2.3, 2.3, 1.1, GOLD)
            if c: return c
    # --- the knob itself: stub + finial
    if abs(a - RC) <= 2.6 and -10.0 <= b <= -5.5:
        return mix(mul(mc, 0.5), mc, clamp01(0.6 - 0.3 * (a - RC) * sx / 2.6)) if abs(a - RC) < 1.8 else mul(mc, 0.35)
    if rid in ("rare",):
        c = gem(dxk, (b + 13.0) * sy, 5.0, st["trim"])
        if c: return c
    elif rid in ("fabled",):
        c = gem(dxk, (b + 13.0) * sy, 4.2, st["trim"])
        if c: return c
        if abs(a - RC) <= 4.8 and -10.6 <= b <= -8.6:                         # gold collar
            return mix(mul(GOLD, 0.7), mix(GOLD, (255, 240, 200), 0.3), clamp01(0.5 - (a - RC) * sx / 6.0))
        for side in (-1, 1):                                                    # crown prongs
            c = spike(a, b, RC + side * 4.0, -10.0, RC + side * 5.6, -18.5, 1.5, GOLD)
            if c: return c
    elif rid == "unique":
        c = spike(a, b, RC, -13.0, RC, -19.5, 1.8, mc)
        if c: return c
        c = ball(dxk, (b + 12.5) * sy, 4.3, mc)
        if c: return c
    elif rid == "legendary":
        c = gem(dxk, (b + 12.5) * sy, 3.2, st["trim"])
        if c: return c
        c = ball(dxk, (b + 12.5) * sy, 4.8, GOLD)
        if c: return c
    else:
        c = ball(dxk, (b + 12.5) * sy, 4.6 if rid != "mythic" else 4.2, mc)
        if c:
            if rid == "mythic" and (dxk * dxk + (b + 12.5) ** 2) < 2.2 ** 2: return mix(st["trim"], (255, 230, 255), 0.4)
            return c
    # --- sheet-corner ornaments (on the parchment band next to the roll)
    if rid == "rare":
        return gem((a - 18.0) * sx, (b - 4.0) * sy, 3.8, st["trim"])
    if rid == "legendary":
        c = gem((a - 18.0) * sx, (b - 4.0) * sy, 1.9, st["trim"])
        if c: return c
        c = ring((a - 18.0), (b - 4.0), 3.6, 3.6, 1.2, GOLD)
        if c: return c
        if 12.5 <= a <= 14.8 and 3.2 <= b <= 4.8: return GOLD
        if 21.4 <= a <= 23.5 and 3.2 <= b <= 4.8: return GOLD
        return None
    if rid == "fabled":
        if 13.0 <= a <= 23.0 and -3.0 <= b <= 7.0:
            ea = min(a - 13.0, 23.0 - a, b + 3.0, 7.0 - b)
            if ea < 0.9: return OUTL
            if ea < 2.0: return GOLD if (a - 13.0) + (b + 3.0) > 4 else mix(GOLD, (255, 240, 200), 0.4)
            c = gem((a - 18.0) * sx, (b - 2.0) * sy, 2.6, GOLD)
            if c: return c
            return mix(mul(st["trim"], 0.55), st["trim"], clamp01(0.7 - ((a - 18.0) * sx + (b - 2.0) * sy) / 8.0))
        return None
    if rid == "set":
        return ring(a - 18.0, b - 4.0, 4.4, 2.8, 1.25, (120, 200, 120))
    if rid == "unique":
        if 13.0 <= a <= 16.6 and 2.0 <= b <= 5.6:
            return OUTL if (a < 13.8 or a > 15.8 or b < 2.8 or b > 4.8) else st["trim"]
        return None
    return None


# ---------------------------------------------------------------- tooltip shader
def tip_corner_coords(X, Y):
    left = X < CAN / 2; top = Y < CAN / 2
    a = X - BODY[0] if left else BODY[2] - X
    b = Y - BODY[1] if top else BODY[3] - Y
    inA = X < BORDER2X or X >= CAN - BORDER2X
    inB = Y < BORDER2X or Y >= CAN - BORDER2X
    if not inA: a = BIG
    if not inB: b = BIG
    sx = 1 if left else -1; sy = 1 if top else -1
    ci = (0 if left else 1) + (0 if top else 2)
    return a, b, sx, sy, inA and inB, ci


def tip_sample(rid, X, Y):
    a, b, sx, sy, corner, ci = tip_corner_coords(X, Y)
    if corner:
        c = knob_and_ornaments(rid, a, b, sx, sy, ci)
        if c: return c
    if a < BIG and abs(a - RC) <= RR and b >= -6.0:
        return roll_colour(rid, a, b, sx, corner, ci)
    t = sheet_depth(rid, a, b, ci)
    if t >= 0:
        lf = 1.0 if (b <= a - 10 and sy > 0) else (-1.0 if b <= a - 10 else (0.4 if sx > 0 else -0.4))
        c = profile(rid, t, lf)
        if rid in ("untiered",) and corner and t < 7.0 and b < 14 and a < 26:   # burnt edge glow
            c = mix(c, (255, 140, 30), clamp01(0.5 - t / 9.0))
        if rid == "normal" and corner and 1.6 <= t < 7.0 and 13.0 <= a <= 24.0 and 2.0 <= b <= 6.0:
            if int(a) % 3 == 0 and int(b) % 2 == 0: c = mix(c, (110, 80, 52), 0.5)   # faint ink marks
        if rid == "mythic" and corner and 1.6 <= t < 7.0 and 13.0 <= a <= 24.0 and 2.0 <= b <= 6.0:
            if (int(a) + int(b)) % 4 == 0: c = mix(c, (250, 200, 255), 0.8)
        return c
    return None


def tip_shadow(rid, X, Y):
    a, b, sx, sy, corner, ci = tip_corner_coords(X, Y)
    r = 8.0
    qa = r - (a + 6.0); qb = r - (b + 6.0)
    sd = math.hypot(max(qa, 0.0), max(qb, 0.0)) + min(max(qa, qb), 0.0) - r
    col, a0 = STYLE[rid]["shadow"]
    if sd <= 0: return col, a0
    if sd >= 16: return col, 0
    return col, a0 * (1 - sd / 16.0) ** 2


def render(w, h, sample, shadow, unit):
    """generic supersampled render: unit = canvas units per output pixel. Opaque where >= half the samples hit (hard alpha);
    elsewhere the soft shadow / glow (alpha < 128)."""
    img = P.new(w, h)
    n = SS * SS
    for py in range(h):
        row = img[py]
        for px in range(w):
            r = g = bl = 0.0; hits = 0
            for sy_ in range(SS):
                Y = (py + (sy_ + 0.5) / SS) * unit
                for sx_ in range(SS):
                    X = (px + (sx_ + 0.5) / SS) * unit
                    c = sample(X, Y)
                    if c is not None:
                        hits += 1; r += c[0]; g += c[1]; bl += c[2]
            if hits * 2 >= n:
                row[px] = [int(round(r / hits)), int(round(g / hits)), int(round(bl / hits)), 255]
            elif shadow is not None:
                col, al = shadow((px + 0.5) * unit, (py + 0.5) * unit)
                al = int(round(min(al, 110)))
                row[px] = [col[0], col[1], col[2], al] if al > 0 else [0, 0, 0, 0]
    return img


def drop_centre(img, k):
    """drop column k and row k (108 -> 107)"""
    return [r[:k] + r[k + 1:] for i, r in enumerate(img) if i != k]


def make_tooltip(rid):
    s2 = drop_centre(render(CAN, CAN, lambda X, Y: tip_sample(rid, X, Y), lambda X, Y: tip_shadow(rid, X, Y), 1.0), CAN // 2)
    s1 = render(CAN // 2, CAN // 2, lambda X, Y: tip_sample(rid, X, Y), lambda X, Y: tip_shadow(rid, X, Y), 2.0)
    return s2, s1


# ---------------------------------------------------------------- arrow: a V that the parchment rim folds into
# Client: Group #Arrow Anchor (Width 33, Height 24, Bottom: -8) inside the tooltip group -> arrow row r (@2x) sits on tooltip row
# 75 + r, i.e. the tooltip's depth from its bottom edge is t = 10 - r. Its top 10 rows overlay the bottom rim.
ATIP, ASLOPE = 36.0, 0.72


def arrow_sample(rid, X, Y):
    q = abs(X - ARROW2X[0] / 2.0)
    H = (ATIP - Y) * ASLOPE
    if rid == "untiered": H -= 2.2 * tri((Y + (1 if X < 33 else 3)) / 4.0)
    if q > H or Y < 0: return None
    e = (H - q) / math.sqrt(1 + ASLOPE * ASLOPE)
    s = max(10.0 - Y, e)
    st = STYLE[rid]
    # tip ornaments
    tipdy = Y - (ATIP - 13.0)
    if rid in ("rare", "legendary", "fabled"):
        c = gem(X - 33.0, tipdy, 3.6, st["trim"] if rid != "fabled" else GOLD)
        if c: return c
    if rid == "mythic":
        c = flame(X - 33.0, -Y, -14.0, -27.0, 0.0, 2.6, st["trim"])
        if c: return c
    if rid == "set":
        c = leaf(X - 33.0, Y - (ATIP - 21.0), math.radians(90), 11.0, 2.6, (70, 170, 60))
        if c: return c
    return profile(rid, s, -0.6)


def arrow_shadow(rid, X, Y):
    if Y < 10: return (0, 0, 0), 0
    q = abs(X - 33.0); H = (ATIP - Y) * ASLOPE
    sd = (q - H) / math.sqrt(1 + ASLOPE * ASLOPE) if Y <= ATIP else math.hypot(q, Y - ATIP)
    col, a0 = STYLE[rid]["shadow"]
    if sd <= 0: return col, a0
    return col, a0 * (1 - sd / 12.0) ** 2 if sd < 12.0 else 0.0


def make_arrow(rid):
    s2 = render(ARROW2X[0], ARROW2X[1], lambda X, Y: arrow_sample(rid, X, Y), lambda X, Y: arrow_shadow(rid, X, Y), 1.0)
    s1 = render(ARROW2X[0] // 2, ARROW2X[1] // 2, lambda X, Y: arrow_sample(rid, X, Y), lambda X, Y: arrow_shadow(rid, X, Y), 2.0)
    return s2, s1


# ---------------------------------------------------------------- slot frames (scaled whole, no 9-slice; hard alpha only)
SLOT_INSET, SLOT_K = 6.0, 1.45
SLOT_SHAPE = {"normal": ("round", 3), "unique": ("notch", 9), "rare": ("chamfer", 14), "legendary": ("round", 10),
              "fabled": ("chamfer", 8), "mythic": ("chamfer", 12), "set": ("round", 9), "untiered": ("jagged",)}


def slot_shape(rid, a, b, ci):
    kind = SLOT_SHAPE[rid]
    if kind[0] == "round":
        r = kind[1]
        return r - math.hypot(r - a, r - b) if (a < r and b < r) else min(a, b)
    if kind[0] == "notch":
        n = kind[1]
        if a < n and b < n: return -min(n - a, n - b)
        return min(min(a, b), (b - n) if a < n else (a - n) if b < n else max(a - n, b - n))
    if kind[0] == "chamfer":
        return min(a, b, (a + b - kind[1]) / math.sqrt(2))
    v = a - b
    c = 11.0 + 4.0 * tri((v + ci * 2.3) / 4.2)
    return min(a, b, (a + b - c) / math.sqrt(2))


def slot_ornament(rid, a, b, sx, sy, ci):
    st = STYLE[rid]; tr = st["trim"]
    if rid == "rare":
        return gem((a - 7.0) * sx, (b - 7.0) * sy, 5.5, tr) or gem((a - 19.0) * sx, (b - 3.4) * sy, 2.4, tr) \
            or gem((a - 3.4) * sx, (b - 19.0) * sy, 2.4, tr)
    if rid == "legendary":
        c = gem((a - 3.5) * sx, (b - 3.5) * sy, 3.4, tr)
        if c: return c
        if -3.6 <= a <= -0.6 and -3.6 <= b <= 16 or -3.6 <= b <= -0.6 and -3.6 <= a <= 16:
            return mix(GOLD, (255, 240, 190), 0.35) if (a < -2.2 or b < -2.2) else mul(GOLD, 0.75)
        return ring(a - 16.5, b + 2.0, 2.2, 2.2, 1.0, GOLD) or ring(a + 2.0, b - 16.5, 2.2, 2.2, 1.0, GOLD)
    if rid == "fabled":
        if -3.0 <= a <= 11.0 and -3.0 <= b <= 11.0 and a + b >= 1.0:
            ea = min(a + 3.0, 11.0 - a, b + 3.0, 11.0 - b, (a + b - 1.0) / 1.4)
            if ea < 0.9: return OUTL
            if ea < 2.2: return GOLD
            c = gem((a - 5.5) * sx, (b - 5.5) * sy, 2.8, GOLD)
            return c or mix(mul(tr, 0.55), tr, clamp01(0.7 - ((a - 5.5) * sx + (b - 5.5) * sy) / 8.0))
        return None
    if rid == "mythic":
        u = -(a + b) / math.sqrt(2); v = (a - b) / math.sqrt(2)
        for v0, L, w in ((0.0, 12.0, 2.8), (-4.5, 8.0, 1.6), (4.5, 8.0, 1.6)):
            c = flame(v, (a + b) / math.sqrt(2), 8.5, 8.5 - L, v0, w, tr)
            if c: return c
        return None
    if rid == "set":
        c = ring(a - 2.0, b - 2.0, 4.5, 4.5, 1.2, (120, 200, 120))
        if c: return c
        return leaf(a - 6.0, b + 1.0, 0.0, 10.0, 2.6, (70, 170, 60)) or leaf(a + 1.0, b - 6.0, math.pi / 2, 10.0, 2.6, (70, 170, 60))
    if rid == "untiered":
        for k, (ex, ey) in enumerate(((-6, -2), (-2, -6), (-5, -5))):
            j = ((ci * 3 + k * 2) % 5) - 2
            c = spike(a, b, 7.0 + j * 0.5, 7.0 - j * 0.5, ex + j * 0.6, ey - j * 0.6, 2.2, tr)
            if c: return c
        return None
    if rid == "unique":
        if 9.0 <= a <= 13.0 and 9.0 <= b <= 13.0:
            return OUTL if min(a - 9.0, 13.0 - a, b - 9.0, 13.0 - b) < 0.9 else tr
        return None
    return None


def slot_sample(rid, X, Y):
    n = SLOT2X
    left = X < n / 2; top = Y < n / 2
    a = ((X if left else n - X) - SLOT_INSET) / SLOT_K
    b = ((Y if top else n - Y) - SLOT_INSET) / SLOT_K
    sx = 1 if left else -1; sy = 1 if top else -1; ci = (0 if left else 1) + (0 if top else 2)
    if a < 24 and b < 24:
        c = slot_ornament(rid, a, b, sx, sy, ci)
        if c: return c
    t = slot_shape(rid, a, b, ci)
    if t < 0: return None
    st = STYLE[rid]
    lf = 1.0 if (b <= a and sy > 0) or (a < b and sx > 0) else -1.0
    if t < 1.2: return OUTL
    if t < 4.6:
        c = PARCH_L if (t < 2.0 and lf > 0) else (mix(PARCH, PARCH_D, 0.5) if t > 3.9 else PARCH)
        if rid == "normal" and t >= 2.0 and (a < 20 and b < 20) and (int(a * 1.5) + int(b * 1.5)) % 5 == 0: c = mix(c, (110, 80, 52), 0.5)
        if rid == "mythic" and t >= 2.0 and (int(a) + int(b)) % 4 == 0: c = mix(c, (250, 200, 255), 0.7)
        return mul(c, 1.0 + 0.05 * lf)
    if t < 6.4:
        c = st["trim"]
        return mix(c, (255, 255, 255), 0.2) if (t < 5.2 and lf > 0) else c
    if t < 7.1: return OUTL
    if st["double"] is not None and 8.0 <= t < 8.8: return st["double"]
    # fill: dark ink wash, faint rarity tint toward the bottom right, lighter near the rim
    d = (X + Y) / (2.0 * n)
    c = mix((40, 36, 46), (30, 27, 35), d)
    if st["glow"]: c = mix(c, st["glow"][0], st["glow"][1] * 0.6 * d + st["glow"][1] * clamp01(1 - (t - 7.1) / 6.0) ** 2)
    return mix(c, WASH, clamp01(1 - (t - 7.1) / 4.0) * 0.6)


def make_slot(rid):
    s2 = render(SLOT2X, SLOT2X, lambda X, Y: slot_sample(rid, X, Y), None, 1.0)
    s1 = render(SLOT2X // 2, SLOT2X // 2, lambda X, Y: slot_sample(rid, X, Y), None, 2.0)
    return s2, s1


# ---------------------------------------------------------------- outputs
def rel_paths(name):
    return {"tip2": "%s/Tooltip_%s@2x.png" % (TIP_DIR, name), "tip1": "%s/Tooltip_%s.png" % (TIP_DIR, name),
            "arr2": "%s/Tooltip_%sArrow@2x.png" % (TIP_DIR, name), "arr1": "%s/Tooltip_%sArrow.png" % (TIP_DIR, name),
            "slot2": "%s/Slot_%s@2x.png" % (SLOT_DIR, name), "slot1": "%s/Slot_%s.png" % (SLOT_DIR, name)}


def png_bytes(img):
    w, h = P.size(img); raw = bytearray()
    for row in img:
        raw.append(0)
        for p in row: raw.extend(bytes(max(0, min(255, int(round(v)))) for v in p))
    return encode_png(w, h, bytes(raw))


def encode_png(w, h, raw):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def build_all():
    """-> {rel path: (image, png bytes)} for every texture"""
    out = {}
    for rid, name, _hex in RARITIES:
        rp = rel_paths(name)
        t2, t1 = make_tooltip(rid); a2, a1 = make_arrow(rid); s2, s1 = make_slot(rid)
        for k, img in (("tip2", t2), ("tip1", t1), ("arr2", a2), ("arr1", a1), ("slot2", s2), ("slot1", s1)):
            out[rp[k]] = (img, png_bytes(img))
    return out


# ---------------------------------------------------------------- sheet (bytearray canvas)
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

    def text(self, x, y, s, c, scale=2, bold=False):
        for ch in s:
            g = P._F.get(ch) or P._F.get(ch.upper()) or P._F[" "]
            for i, bit in enumerate(g):
                if bit == "1":
                    self.fill(x + (i % 5) * scale, y + (i // 5) * scale, x + (i % 5 + 1) * scale + (1 if bold else 0),
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


SAMPLE = [("name", None), ("Attack Speed: Fast", (170, 170, 170)), ("", None), (("Strength", "+12"), (85, 255, 85)),
          (("Crit Chance", "+5%"), (85, 255, 85)), (("Defense", "-3"), (255, 85, 85)), ("", None),
          ("Ability: Skyfall", (255, 170, 0)), ("Deals 250 damage", (230, 230, 230)), ("Mana Cost: 40", (85, 255, 255)),
          ("", None), ("Can be reforged", (130, 130, 130)), ("type", None)]


def draw_tooltip(cv, files, name, colour, x, y, W, H, arrow_x):
    rp = rel_paths(name)
    cv.blit(nine_slice(files[rp["tip1"]][0], 24, W, H), x, y)
    cv.blit(files[rp["arr1"]][0], x + arrow_x, y + H - 16)
    tx, ty = x + 24, y + 21
    rows = [r for r in SAMPLE]
    maxl = (H - 21 - 24) // 18
    if len(rows) > maxl: rows = rows[:maxl - 1] + [rows[-1]]
    for item, c in rows:
        if item == "name":
            cv.text(tx, ty, "%s Skyblade" % name, colour, 2, bold=True)
        elif item == "type":
            cv.text(tx, ty, "%s SWORD" % name.upper(), colour, 2, bold=True)
        elif isinstance(item, tuple):
            cv.text(tx, ty, item[0], (230, 230, 230), 2)
            cv.text(x + W - 24 - len(item[1]) * 12, ty, item[1], c, 2)
        elif item:
            cv.text(tx, ty, item, c, 2)
        ty += 18


def sword_icon(colour):
    """a simple ORIGINAL placeholder item (64 x 64) so the slot mock shows icon coverage"""
    img = P.new(64, 64)
    for y in range(64):
        for x in range(64):
            u = (x - y) / math.sqrt(2); v = (x + y) / math.sqrt(2) - 45   # along the blade diagonal
            if abs(u) <= 4.5 and -38 <= v <= 14:
                img[y][x] = list(mix((220, 226, 236), colour, 0.25)) + [255] if abs(u) < 3.2 else [40, 40, 52, 255]
            if abs(v - 14) <= 2.5 and abs(u) <= 12: img[y][x] = [70, 48, 30, 255] if abs(v - 14) > 1.2 else [200, 160, 70, 255]
            if 14 < v <= 26 and abs(u) <= 2.2: img[y][x] = [96, 62, 36, 255]
    return img


def make_sheet(files):
    W, H = 1500, 3420
    cv = Canvas(W, H, (52, 60, 56))
    for y in range(0, H, 40):                          # faint checker so shadows + cut alpha show
        for x in range(0, W, 40):
            if (x // 40 + y // 40) % 2: cv.fill(x, y, x + 40, y + 40, (58, 66, 62))
    cv.text(20, 16, "SKYYGEAR RARITY TOOLTIP FRAMES - MAGIC SCROLL - DRAFT V1", (238, 222, 184), 3, bold=True)
    cv.text(20, 48, "1X UI SCALE. EACH FRAME 9-SLICED (BORDER 24) TO 3 SIZES, ARROW AT 3 POSITIONS. SLOT 1X + 2X.", (200, 200, 200), 2)
    y = 84
    # Normal first, big hero row (2x tooltip image stretched at @2x)
    rp = rel_paths("Normal")
    cv.text(20, y, "NORMAL - THE MAGIC SCROLL (2X TEXTURE, 9-SLICED, SHOWN 1:1)", (255, 255, 255), 2, bold=True)
    big = nine_slice(files[rp["tip2"]][0], 48, 760, 300)
    cv.blit(big, 20, y + 24); cv.blit(files[rp["arr2"]][0], 20 + 120, y + 24 + 300 - 32)
    cv.text(20 + 48, y + 24 + 42, "Normal Skyblade", (255, 255, 255), 3, bold=True)
    cv.text(20 + 48, y + 24 + 80, "Attack Speed: Fast", (170, 170, 170), 3)
    cv.text(20 + 48, y + 24 + 112, "Strength", (230, 230, 230), 3); cv.text(20 + 760 - 48 - 3 * 18, y + 24 + 112, "+12", (85, 255, 85), 3)
    cv.text(20 + 48, y + 24 + 144, "Defense", (230, 230, 230), 3); cv.text(20 + 760 - 48 - 2 * 18, y + 24 + 144, "-3", (255, 85, 85), 3)
    cv.text(20 + 48, y + 24 + 186, "Can be reforged", (130, 130, 130), 3)
    cv.text(20 + 48, y + 24 + 218, "NORMAL SWORD", (255, 255, 255), 3, bold=True)
    cv.blit(files[rp["tip2"]][0], 820, y + 24, 2)
    cv.text(820, y + 24 + 220, "RAW 107X107 @2X (X2)", (200, 200, 200), 2)
    cv.blit(files[rp["slot2"]][0], 1100, y + 24)
    cv.blit(sword_icon((255, 255, 255)), 1100 + 10, y + 24 + 10, 2)
    cv.blit(files[rp["arr2"]][0], 1280, y + 24, 2)
    cv.text(1100, y + 24 + 160, "SLOT @2X", (200, 200, 200), 2)
    cv.text(1280, y + 24 + 110, "ARROW X2", (200, 200, 200), 2)
    y += 24 + 300 + 40
    for rid, name, hexs in RARITIES:
        colour = hx(hexs)
        cv.text(20, y, name.upper(), colour, 3, bold=True)
        rp = rel_paths(name)
        cv.blit(files[rp["slot2"]][0], 20, y + 30)
        cv.blit(sword_icon(colour), 30, y + 40, 2)
        cv.blit(files[rp["slot1"]][0], 20 + 34, y + 190)
        draw_tooltip(cv, files, name, colour, 190, y + 4, 320, 170, 40)
        draw_tooltip(cv, files, name, colour, 534, y + 4, 400, 220, 184)
        draw_tooltip(cv, files, name, colour, 958, y + 4, 480, 262, 380)
        y += 300
    # 9-slot inventory mock (@2x slots, 1:1)
    cv.text(20, y, "INVENTORY MOCK - 9 SLOTS AT @2X (148 PX), PLACEHOLDER SWORD ICON", (238, 222, 184), 2, bold=True)
    y += 26
    cv.fill(20, y, 20 + 3 * 152 + 16, y + 3 * 152 + 16, (26, 30, 38))
    order = RARITIES + [None]
    for i, r in enumerate(order):
        gx, gy = 28 + (i % 3) * 152, y + 8 + (i // 3) * 152
        if r is None:
            cv.blit(files[rel_paths("Normal")["slot2"]][0], gx, gy); continue
        cv.blit(files[rel_paths(r[1])["slot2"]][0], gx, gy)
        cv.blit(sword_icon(hx(r[2])), gx + 10, gy + 10, 2)
    # the same at 1x in a hotbar-like row
    cv.text(540, y, "1X ROW (74 PX)", (200, 200, 200), 2)
    for i, r in enumerate(RARITIES):
        gx = 540 + i * 78
        cv.blit(files[rel_paths(r[1])["slot1"]][0], gx, y + 24)
        cv.blit(sword_icon(hx(r[2])), gx + 5, y + 29)
    cv.text(540, y + 120, "EMPTY SLOT (NORMAL FRAME) = BOTTOM RIGHT OF THE MOCK", (170, 170, 170), 2)
    return cv.png()


def main():
    files = build_all()
    man = {"what": "SkyyGear rarity tooltip backgrounds + arrows + slot frames - magic scroll family, DRAFT v1",
           "generator": "tools/art/make_tooltip_frames.py", "validator": "tools/art/validate_tooltip_frames.py",
           "deterministic": True, "original_pixels": True,
           "nine_slice": {"tooltip_2x": [107, 107], "border_2x_px": BORDER2X, "border_ui_units": 24, "stretch_strip_2x": [48, 58],
                          "tooltip_1x": [54, 54], "border_1x_px": 24, "arrow_2x": list(ARROW2X), "arrow_ui": [33, 24],
                          "slot_2x": [SLOT2X, SLOT2X], "slot_ui": [74, 74]},
           "rarities": [{"id": r, "name": n, "hex": h, "paths": rel_paths(n)} for r, n, h in RARITIES], "files": []}
    for rel in sorted(files):
        data = files[rel][1]
        p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh: fh.write(data)
        man["files"].append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    sheet = make_sheet(files)
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh: fh.write(sheet)
    man["files"].append({"path": "sheet.png", "bytes": len(sheet), "sha256": hashlib.sha256(sheet).hexdigest()})
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(man, fh, indent=1); fh.write("\n")
    print("wrote %d textures + sheet.png + manifest.json to %s" % (len(files), OUT))


if __name__ == "__main__":
    main()
