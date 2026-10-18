#!/usr/bin/env python3
"""SkyWynn hub tab icons - a faded picture BEHIND the word of every hub tab, plus one per hub for the hub row (DRAFT v1).

Skyy (2026-10-15): "can you give the tabs in the character page custom designs? so the pet tab still says pets, but also shows a
little pet icon behind the word?" - style picked in a popup: "Icon first, themed later".

Same family look as the approved menu icons (art/menu-icons/, art/menu-icons-2/): this script REUSES that painter
(tools/art/make_menu_icons.py - imported, never edited: shapes, Icon painter with ramps / bevels / contact shadows / 1 px tinted
outline, palettes, PNG writer, sheet Canvas). Each motif is first painted as a normal hard-alpha family icon, then FADED for its
place behind a word: colours pulled toward a cool slate grey, a low overall alpha, and a per-pixel alpha cap so the tab label keeps
a WCAG contrast of >= 4.5 : 1 (>= 5 on the plain tab) over every pixel of the icon (checked on the real Sky Tab textures).

Multitool is NOT a tab any more (Skyy 2026-10-15: "i thought we scrapped the multitool menu. merging it into upgrades.").
Pocket, Identify and Teleport reuse the SkyWynn Menu tile designs (Skyy 2026-10-15: "i prefer this one").

Size: 72 x 72 px, an @2x texture = 36 x 36 UI units, centred in the 44 UI high Sky tab (4 UI clear above / below; the tab's
V border is 12 UI). Works on tabs from 110 UI wide (Character, 8 tabs = 115 UI) to 190 UI.

Writes (all ORIGINAL pixels; no game file is read):
  art/hub-tab-icons/<hub>_<tab>.png        normal tab (faded)
  art/hub-tab-icons/<hub>_<tab>_on.png     active / selected tab (brighter)
  art/hub-tab-icons/hubrow_<hub>.png (+ _on)  one per hub for the hub row (home, character, ..., settings)
  art/hub-tab-icons/manifest.json          per icon: hub, tab, label, files, bytes, sha256, min contrast; size + fade rules
  --sheet PATH                             the review contact sheet (every icon behind its word on the Sky tab, normal + active)
  --compare PATH                           the Storage > Supplies review sheet (its tab row + the approved satchel it follows)

Run:   python tools/art/make_hub_tab_icons.py [--sheet <png>] [--compare <png>]     (deterministic: two runs = same bytes)
Check: python tools/art/make_hub_tab_icons.py --check             (prints one line per check, ALL OK / N FAILED, exit 1 on fail)
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M
from make_menu_icons import (Icon, Shape, circle, ellipse, rot_ellipse, rect, rrect, poly, capsule, union, diff, inter, ering,
                             star_pts, gear, obox, bust, hstripes, folds, hx, mix, png_bytes, Canvas, PALC)

S = 72                     # icon size in px (@2x texture = 36 x 36 UI)
M.N = S                    # the sheet-1 painter reads its module-level N at render time: paint on a 72 px grid (this process only)
C = S / 2.0
ROOT = M.ROOT
OUT = os.path.join(ROOT, "art", "hub-tab-icons")
KIT = os.path.join(ROOT, "art", "ui-kit-sky", "Common", "UI", "Custom", "SkyyKit")   # our own Sky kit art (read for the checks + sheet)

# ====================================================================== extra palettes (dark -> light, same rules as sheet 1)
PAL3 = {
    "pink": ["#3a1424", "#5e2238", "#8a3650", "#b5506a", "#d97488", "#f0a2ae", "#fbd2d4"],
    "skin": ["#3b2018", "#5e3424", "#8a5236", "#b4744c", "#d39a6c", "#ecc293", "#f8e2c4"],
    "hair": ["#1e100c", "#331b12", "#4c2a18", "#683c20", "#86522c", "#a46d3e"],
    # the APPROVED black-leather satchel's ramp (art/accessory-bag-icon manifest "leather_v2", Skyy 2026-10-08) - the Supplies tab
    "bleather": ["#0f0b16", "#18131f", "#221b28", "#2d2431", "#3a2e3b", "#4c3e47", "#67565c", "#8c7a7a"],
}
for _k, _v in PAL3.items():
    if _k not in M.PAL:
        M.PAL[_k] = _v
        M.PALC[_k] = [hx(c) for c in _v]

# ====================================================================== fade rules (behind a word on the dark Sky tab)
# (order in fade(): slate desaturation, a whole-icon gain for bright motifs, a soft knee, then a hard per-pixel cap)
LABEL = {"button2Text": hx("#bdcbd3"), "buttonText": hx("#bfcdd5")}      # tools/art/make_ui_kit_sky.py (kit label colours)
FADE = {
    # desat: pull toward slate grey; alpha: overall; min contrast of the label over (icon on that tab state), per state
    "normal": {"desat": 0.30, "alpha": 0.62, "states": {"Tab": 5.0, "Tab_Hovered": 4.5, "Tab_Pressed": 5.0}, "labels": ["button2Text"]},
    "on":     {"desat": 0.10, "alpha": 0.86, "states": {"Tab_Selected": 4.5}, "labels": ["buttonText", "button2Text"]},
}
TAB_BAND = (24, 64, 40, 200)       # rows y0..y1, cols x0..x1 of the 240 x 88 Tab@2x where the word + icon sit (inside the borders)


def srgb_lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def lin_srgb(v):
    v = max(0.0, min(1.0, v))
    return 255.0 * (v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)


def rel_lum(c):
    return 0.2126 * srgb_lin(c[0]) + 0.7152 * srgb_lin(c[1]) + 0.0722 * srgb_lin(c[2])


def ratio(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


_TABBG = {}


def tab_worst_bg(state):
    """the brightest pixel of the tab texture's text band = the worst case for a light label"""
    if state not in _TABBG:
        img = P.read_png(open(os.path.join(KIT, state + "@2x.png"), "rb").read())
        y0, y1, x0, x1 = TAB_BAND
        best = None
        for y in range(y0, y1):
            for x in range(x0, x1):
                p = img[y][x]
                if best is None or rel_lum(p) > rel_lum(best): best = tuple(p[:3])
        _TABBG[state] = best
    return _TABBG[state]


def over(fg, a, bg):
    return tuple(fg[k] * a + bg[k] * (1 - a) for k in range(3))


def fade(img, mode):
    """hard-alpha family icon -> faded, partly transparent tab-background icon (alpha capped per pixel for label contrast)"""
    f = FADE[mode]
    tests = [(tab_worst_bg(st), LABEL[lb], need) for st, need in f["states"].items() for lb in f["labels"]]
    # the luminance cap on the main tab state of this mode: (label + 0.05) / target - 0.05; the knee starts at 55 % of it
    st0 = list(f["states"])[0]; lbg = rel_lum(tab_worst_bg(st0))
    cap = min((rel_lum(LABEL[lb]) + 0.05) / f["states"][st0] - 0.05 for lb in f["labels"]) * 0.97
    knee = lbg + (cap - lbg) * 0.55
    # bright motifs (amber portal, cream bunny / scroll): one gain for the whole icon first, so the 85th-percentile pixel lands at
    # the cap - the shading survives as a whole instead of every bright pixel being squashed to the same flat tone by the knee
    def slate_of(p):
        g = 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
        return mix(p[:3], (g * 0.86, g * 0.94, min(255.0, g * 1.08 + 6)), f["desat"])
    lums = sorted(rel_lum(slate_of(p)) for row in img for p in row if p[3])
    p85 = lums[int(0.85 * (len(lums) - 1))]
    want = (cap - (1 - f["alpha"]) * lbg) / f["alpha"]
    gain = min(1.0, want / p85) if p85 > 0 else 1.0
    out = P.new(S, S)
    for y in range(S):
        for x in range(S):
            p = img[y][x]
            if not p[3]: continue
            if gain < 1.0:
                p = [lin_srgb(srgb_lin(v) * gain) for v in p[:3]] + [p[3]]
            g = 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
            slate = (g * 0.86, g * 0.94, min(255.0, g * 1.08 + 6))
            col0 = mix(p[:3], slate, f["desat"])
            a = f["alpha"]; k = 1.0
            # soft knee: bright parts are compressed smoothly toward the luminance cap, so their shading survives
            fl = rel_lum(col0); lc = a * fl + (1 - a) * lbg
            if lc > knee and fl > 0:
                lt = knee + (cap - knee) * (1 - math.exp(-(lc - knee) / (cap - knee)))
                r = max(0.0, (lt - (1 - a) * lbg) / (a * fl))
                col0 = tuple(lin_srgb(srgb_lin(v) * r) for v in col0)
            col = tuple(int(round(v)) for v in col0)
            # too bright for the label: first darken the colour (keeps its hue + the alpha), then lower the alpha
            while any(ratio(lab, over(col, a, bg)) < need for bg, lab, need in tests):
                if k > 0.55: k -= 0.02
                elif a > 0.02: a -= 0.01
                else: break
                col = tuple(int(round(v * k)) for v in col0)
            out[y][x] = [col[0], col[1], col[2], int(round(a * 255))]
    return out


def min_contrast(img, mode):
    """the lowest label contrast over any icon pixel, on the worst tab state of that mode (uses the 8-bit file values)"""
    f = FADE[mode]; worst = 99.0
    for st, need in f["states"].items():
        bg = tab_worst_bg(st)
        for lb in f["labels"]:
            for row in img:
                for p in row:
                    if p[3]:
                        worst = min(worst, ratio(LABEL[lb], over(p[:3], p[3] / 255.0, bg)) / need)
    return worst      # >= 1.0 = every state reaches its target


# ====================================================================== helpers
def rp(pts, ang, cx=C, cy=C):
    """rotate local points (about 0, 0) by ang degrees (clockwise on screen) and move them to (cx, cy)"""
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def heart(cx, cy, s):
    """a heart: lobes at cy, point at cy + 36 s"""
    return union(circle(cx - 9.5 * s, cy, 12 * s), circle(cx + 9.5 * s, cy, 12 * s),
                 poly([(cx - 20.8 * s, cy + 4.5 * s), (cx + 20.8 * s, cy + 4.5 * s), (cx, cy + 36 * s)]))


def swirl_f(cx, cy, rx, ry, k=3):
    def f(x, y):
        dx, dy = (x - cx) / rx, (y - cy) / ry; r = math.hypot(dx, dy); a = math.atan2(dy, dx)
        return 0.25 + 0.55 * (1 - r) + 0.2 * math.sin(k * a + r * 8.0)
    return f


# ====================================================================== motifs reused from the SkyWynn Menu tiles (Skyy 2026-10-15)
# Skyy, looking at the contact sheet next to the menu icon grid: "pocket icon could use a little work. i prefer this one. for the
# identify, and the teleport portal." -> these three tabs reuse the approved sheet-1 tile designs (tools/art/make_menu_icons.py,
# imported, not edited): painted with that builder on its own 64 px grid, the loose sparkles outside the motif dropped (noise at
# tab size), then placed in the middle of the 72 px square and faded like every other tab icon.
class Sheet1Motif:
    def __init__(self, builder):
        self.builder = builder

    def render(self):
        ic = self.builder()
        bbs = [ly.shape.bb for ly in ic.layers]
        ic.pix = [(x, y, c) for (x, y, c) in ic.pix if any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in bbs)]
        old = M.N
        M.N = 64
        try:
            img = ic.render()
        finally:
            M.N = old
        out = P.new(S, S); o = (S - 64) // 2
        for y in range(64):
            for x in range(64):
                if img[y][x][3]: out[y + o][x + o] = list(img[y][x])
        return out


def t_pocket():
    return Sheet1Motif(M.icon_pocket)


def t_identify():
    return Sheet1Motif(M.icon_identify)


def t_teleport():
    return Sheet1Motif(M.icon_teleport)


# ====================================================================== CHARACTER hub (teal + gold, "your stuff")
def t_stats():
    ic = Icon("stats")
    h = heart(36, 21, 1.12)
    ic.add(h, "red", base=0.55, grad=0.6, bevel=1.2, bev=0.2)
    inner = heart(36, 22.5, 0.9)
    for k, (x0, top) in enumerate(((23, 38), (32, 31), (41, 23))):
        ic.add(inter(rect(x0, top, x0 + 7.5, 49), inner), "gold", base=0.58 + 0.07 * k, grad=0.5, bevel=0.8, line=True)
    ic.add(inter(rect(19, 49, 53, 51.5), inner), "cream", base=0.7, bevel=0, cast=False)
    return ic


def t_skills():
    ic = Icon("skills")
    ic.add(poly([(27, 42), (34, 46), (29, 65), (25, 60), (20, 64)]), "teal", base=0.42, grad=0.5, pattern=folds(0.9, 0.05))
    ic.add(poly([(45, 42), (38, 46), (43, 65), (47, 60), (52, 64)]), "teal", base=0.32, grad=0.5, pattern=folds(0.9, 0.05))
    ic.add(circle(36, 29, 21), "gold", mode="sphere", base=0.62)
    ic.add(circle(36, 29, 15.5), "teal", mode="sphere", base=0.4, line=True, sphere=(36, 29, 15.5, 15.5))
    ic.add(poly(star_pts(36, 29.5, 12.5, 5.2, 5)), "gold", base=0.72, grad=0.6, bevel=0.9, line=True)
    return ic


def t_trees():
    ic = Icon("trees")
    ic.add(ellipse(36, 63, 17, 3.6), "grass", base=0.45, grad=0.5)
    ic.add(poly([(31.5, 63), (40.5, 63), (38.5, 36), (33.5, 36)]), "wood", mode="cyl", axis=(0, 1), base=0.55, pattern=hstripes(5, 0.05))
    for a, b in (((36, 46), (18, 32)), ((36, 42), (54, 30)), ((36, 38), (36, 18))):
        ic.add(capsule(a[0], a[1], b[0], b[1], 2.6), "wood", base=0.5, grad=0.4, bevel=0.6)
    for (x, y, r, b) in ((18, 30, 9, 0.5), (54, 28, 9, 0.42), (36, 16, 10.5, 0.6)):
        ic.add(circle(x, y, r), "green", mode="sphere", base=b, line=True)
        ic.add(circle(x, y + 0.5, 3.2), "gold", mode="sphere", base=0.7, bevel=0)
    return ic


def t_class():
    ic = Icon("class")
    # staff (behind): wood shaft, gold claw, violet orb at the top left
    ic.add(poly(rp(box(-2.6, -22, 2.6, 34), -45, 36, 38)), "wood", base=0.55, grad=0.5, bevel=0.8)
    tip = rp([(0, -27)], -45, 36, 38)[0]
    ic.add(ering(tip[0], tip[1], 9.5, 9.5, 6.5, 6.5), "gold", mode="torus", torus=(tip[0], tip[1], 9.5, 9.5, 6.5, 6.5), base=0.6, bevel=0)
    ic.add(circle(tip[0], tip[1], 7), "void", mode="sphere", base=0.62, line=True)
    # sword (front): steel blade with a fuller, gold guard, leather grip, gold pommel; tip to the top right
    blade = [(-3.8, -27), (0, -33), (3.8, -27), (3.8, 10), (-3.8, 10)]
    ic.add(poly(rp(blade, 45, 36, 38)), "steel", base=0.66, grad=0.55, bevel=1.1, bev=0.2, line=True)
    ic.add(poly(rp(box(-0.8, -25, 0.8, 8), 45, 36, 38)), "steel", base=0.4, bevel=0, cast=False)
    ic.add(poly(rp(box(-11.5, 10, 11.5, 14.8), 45, 36, 38)), "gold", base=0.62, grad=0.6, bevel=0.8, line=True)
    ic.add(poly(rp(box(-2.4, 14.8, 2.4, 25), 45, 36, 38)), "leather", base=0.5, grad=0.4, bevel=0.6, pattern=hstripes(2.2, 0.08))
    pm = rp([(0, 28)], 45, 36, 38)[0]
    ic.add(circle(pm[0], pm[1], 3.6), "gold", mode="sphere", base=0.65)
    return ic


def t_pets():
    ic = Icon("pets")
    ox, oy = -2.0, 2.0                      # shifts the bunny so its silhouette sits centred
    E = lambda x, y, rx, ry: ellipse(x + ox, y + oy, rx, ry)
    Ci = lambda x, y, r: circle(x + ox, y + oy, r)
    ic.add(rot_ellipse(33 + ox, 14 + oy, 11, 3.7, -75), "cream", base=0.38, grad=0.4)                  # back ear
    ic.add(E(46, 59, 10, 3.4), "cream", base=0.4, grad=0.4)                                             # hind foot
    ic.add(E(42, 46, 17, 14), "cream", base=0.62, grad=0.55, bevel=1.1)                                 # body
    ic.add(Ci(58.5, 44.5, 4.6), "cream", mode="sphere", base=0.85)                                      # tail
    ic.add(Ci(49, 49, 8.5), "cream", base=0.5, grad=0.5, bevel=0.8)                                     # haunch
    ic.add(E(27, 58, 6, 3), "cream", base=0.6, grad=0.4)                                                # front paw
    ic.add(Ci(26, 32, 11), "cream", base=0.72, grad=0.55, bevel=1.1, line=True)                         # head
    ic.add(E(18.5, 36, 5.2, 4.2), "cream", base=0.8, grad=0.3, bevel=0.7)                               # muzzle
    ic.add(rot_ellipse(26 + ox, 13 + oy, 11.5, 4.0, -100), "cream", base=0.66, grad=0.5, line=True)    # front ear
    ic.add(rot_ellipse(26 + ox, 14 + oy, 8, 1.8, -100), "pink", base=0.62, bevel=0, cast=False)        # inner ear
    ic.add(Ci(24, 30, 2.0), "navy", base=0.2, bevel=0, cast=False)                                      # eye
    ic.px(int(23 + ox), int(29 + oy), "#efe2c0")
    ic.add(Ci(14.3, 35, 1.4), "pink", base=0.7, bevel=0, cast=False)                                    # nose
    return ic


def t_accessories():
    ic = Icon("accessories")
    chain = diff(ering(36, 12, 23, 30, 20.5, 27.5), rect(0, 0, 72, 12))
    ic.add(chain, "gold", base=0.55, grad=0.5, bevel=0,
           pattern=lambda x, y: -0.16 if int(math.atan2(y - 12, x - 36) * 9) % 2 else 0.0)
    ic.add(circle(13, 11, 2.6), "gold", mode="sphere", base=0.6)
    ic.add(circle(59, 11, 2.6), "gold", mode="sphere", base=0.6)
    ic.add(ering(36, 36, 3.6, 3.6, 1.8, 1.8), "gold", base=0.6, bevel=0)                              # bail
    ic.add(circle(36, 50, 13), "gold", mode="sphere", base=0.62, line=True)                             # setting
    gem = [(36, 40), (45.5, 50), (36, 61), (26.5, 50)]
    ic.add(poly(gem), "teal", base=0.55, grad=0.7, bevel=1.0, bev=0.22, line=True)
    ic.add(poly([(36, 40), (45.5, 50), (36, 50)]), "teal", base=0.35, bevel=0, cast=False)
    ic.add(poly([(36, 50), (26.5, 50), (36, 61)]), "teal", base=0.42, bevel=0, cast=False)
    ic.px(31, 46, "#bff2e1"); ic.px(32, 45, "#bff2e1")
    return ic


def t_collections():
    ic = Icon("collections")
    dy = -3
    ic.add(poly([(6, 22 + dy), (36, 26 + dy), (66, 22 + dy), (66, 55 + dy), (36, 59 + dy), (6, 55 + dy)]), "teal", base=0.45, grad=0.5)
    ic.add(poly([(9, 19 + dy), (35, 23 + dy), (35, 55 + dy), (9, 51 + dy)]), "cream", base=0.76, grad=0.4,
           pattern=lambda x, y: -0.1 if x > 32 else 0)
    ic.add(poly([(37, 23 + dy), (63, 19 + dy), (63, 51 + dy), (37, 55 + dy)]), "cream", base=0.62, grad=0.4,
           pattern=lambda x, y: -0.1 if x < 40 else 0)
    for k in range(5):                                                                                  # text lines
        y0 = 27 + dy + 5 * k
        ic.add(capsule(13, y0 + 0, 30 - (5 if k == 4 else 0), y0 + 2.6, 0.75), "cream", base=0.32, bevel=0, cast=False)
        ic.add(capsule(42, y0 + 2.6, 59 - (7 if k == 4 else 0), y0, 0.75), "cream", base=0.25, bevel=0, cast=False)
    ic.add(rect(35, 23 + dy, 37, 58 + dy), "teal", base=0.28, bevel=0)                                  # spine
    ic.add(poly([(45, 55 + dy), (50, 54 + dy), (50, 66 + dy), (47.5, 63 + dy), (45, 66 + dy)]), "gold", base=0.6, grad=0.5, bevel=0.6, line=True)
    return ic


def t_profiles():
    ic = Icon("profiles")
    ic.add(rrect(14, 7, 58, 65, 3), "gold", base=0.6, grad=0.6, bevel=1.2, bev=0.2)
    field = rect(19.5, 12.5, 52.5, 59.5)
    ic.add(field, "teal", base=0.22, grad=-0.3, bevel=0, line=True)
    b = Icon("tmp")
    bust(b, 36, 18, 1.15, PALC["teal"], base=0.68)
    for ly in b.layers:
        ly.shape = inter(ly.shape, field); ic.layers.append(ly)
    ic.layers[-1].line = True; ic.layers[-3].line = True
    for (x, y) in ((16.5, 9.5), (55.5, 9.5), (16.5, 62.5), (55.5, 62.5)):
        ic.add(circle(x, y, 1.3), "gold", base=0.9, bevel=0, cast=False)
    return ic


# ====================================================================== STORAGE hub (teal / leather / steel)
def t_supplies():
    """Storage > Supplies (SkyyCooking: the Potion Flask + Food Pouch): the approved black-leather satchel (art/accessory-bag-icon look -
    stepped flap, strap tongue, gold clasp; no booster gems - those belonged to the bag of charms) with a red potion flask and a tied
    brown food pouch peeking out of its top"""
    ic = Icon("supplies")
    # behind the bag: the food pouch (right) and the potion flask (left)
    ic.add(ellipse(46, 24, 8.5, 7.5), "leather", base=0.58, grad=0.55, pattern=folds(1.1, 0.06), line=True)     # food pouch
    ic.add(poly([(42, 18), (50, 18), (52.5, 12.5), (39.5, 12.5)]), "leather", base=0.7, grad=0.4, bevel=0.7)         # its ruffled top
    ic.add(rect(41.5, 17, 50.5, 19.3), "gold", base=0.6, bevel=0, cast=False)                                     # the tie
    ic.add(circle(25, 24.5, 9.5), "red", mode="sphere", base=0.62, line=True)                                        # flask body
    ic.add(rect(22, 12, 28, 17), "glass", base=0.6, grad=0.4, bevel=0.7, line=True)                             # neck
    ic.add(rrect(21, 7, 29, 12.5, 1.2), "wood", base=0.62, grad=0.5, bevel=0.8, line=True)                          # cork
    ic.px(21, 20, "#f7a493"); ic.px(22, 19, "#f7a493")
    # the satchel: a soft rounded body with a thin side gusset, a rounded flap with a stitched hem, the strap tongue + gold clasp
    ic.add(rrect(13.5, 31, 56, 62, 7), "bleather", base=0.38, grad=0.4, bevel=0.6)                                 # side gusset
    ic.add(rrect(10, 33, 51, 64, 7), "bleather", base=0.6, grad=0.5, bevel=1.0, pattern=folds(0.55, 0.05), line=True)   # body
    ic.add(poly([(10, 33), (51, 33), (56, 31), (14.5, 31)]), "bleather", base=0.85, bevel=0, cast=False)            # top lip
    flap = union(rect(9, 31, 52, 41), rrect(9, 31, 52, 48, 8))
    ic.add(flap, "bleather", base=0.74, grad=0.55, bevel=1.1, line=True)                                            # front flap
    ic.add(diff(rrect(11.5, 31, 49.5, 45.8, 6.5), rrect(12.5, 31, 48.5, 44.8, 5.5), rect(0, 0, 72, 38)), "bleather", base=0.98, bevel=0, cast=False)   # stitched hem
    ic.add(union(rect(27.5, 37, 33.5, 53), rrect(27.5, 37, 33.5, 56, 3)), "bleather", base=0.84, grad=0.5, bevel=0.9, line=True)   # strap tongue
    ic.add(rrect(24.5, 48.5, 36.5, 52.5, 1.0), "gold", base=0.62, grad=0.6, bevel=0.8, line=True)                  # clasp bar
    ic.add(circle(30.5, 50.5, 1.3), "gold", mode="sphere", base=0.85, bevel=0, cast=False)
    return ic


def t_requip():
    ic = Icon("requip")
    ic.add(diff(ering(36, 10.5, 5, 5, 2.8, 2.8), rect(31, 10.5, 36, 16)), "gold", base=0.6, bevel=0)  # hanger hook
    ic.add(capsule(36, 15, 36, 18.5, 1.3), "gold", base=0.55, bevel=0)
    ic.add(union(capsule(36, 18.5, 11, 28, 2.0), capsule(36, 18.5, 61, 28, 2.0)), "gold", base=0.58, grad=0.5, bevel=0.6)
    plate = poly([(17, 25), (28, 22.5), (36, 28), (44, 22.5), (55, 25), (60, 36), (52, 40), (51, 59), (36, 64), (21, 59), (20, 40), (12, 36)])
    ic.add(plate, "steel", base=0.6, grad=0.6, bevel=1.2, bev=0.2, line=True)
    ic.add(poly([(17, 25), (28, 22.5), (24, 34), (12, 36)]), "teal", base=0.55, grad=0.5, bevel=0.8, line=True)     # pauldrons
    ic.add(poly([(55, 25), (44, 22.5), (48, 34), (60, 36)]), "teal", base=0.4, grad=0.5, bevel=0.8, line=True)
    ic.add(poly([(34.5, 30), (37.5, 30), (37.5, 62), (34.5, 62)]), "steel", base=0.82, bevel=0, cast=False)          # ridge
    ic.add(capsule(23, 49, 49, 49, 1.2), "teal", base=0.5, bevel=0, cast=False)
    return ic


def t_vault():
    ic = Icon("vault")
    ic.add(rect(6, 26, 12, 46), "steel", base=0.45, grad=0.4)                                           # hinge
    ic.add(circle(36, 36, 28), "steel", base=0.55, grad=0.6, bevel=1.2, bev=0.2)
    ic.add(ering(36, 36, 28, 28, 23, 23), "steel", mode="torus", torus=(36, 36, 28, 28, 23, 23), base=0.62, bevel=0)
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        ic.add(circle(36 + 25.5 * math.cos(a), 36 + 25.5 * math.sin(a), 1.6), "steel", mode="sphere", base=0.8, bevel=0)
    for k in range(3):
        a = math.radians(90 + 60 * k); dx, dy = 17 * math.cos(a), 17 * math.sin(a)
        ic.add(capsule(36 - dx, 36 - dy, 36 + dx, 36 + dy, 2.0), "gold", base=0.58, grad=0.5, bevel=0.6)
    ic.add(ering(36, 36, 15.5, 15.5, 12.5, 12.5), "gold", mode="torus", torus=(36, 36, 15.5, 15.5, 12.5, 12.5), base=0.6, bevel=0, line=True)
    ic.add(circle(36, 36, 5.5), "gold", mode="sphere", base=0.65, line=True)
    return ic


def t_bank():
    ic = Icon("bank")
    ox, oy = 4, 3
    ic.add(rect(8 + ox, 24 + oy, 56 + ox, 47 + oy), "stone", base=0.12, grad=0.4, bevel=0)
    for cxp in (13.5, 25, 39, 50.5):
        ic.add(rect(cxp - 3.2 + ox, 25 + oy, cxp + 3.2 + ox, 47 + oy), "stone", mode="cyl", axis=(0, 1), base=0.7)
        ic.add(rect(cxp - 4.2 + ox, 24 + oy, cxp + 4.2 + ox, 26.5 + oy), "stone", base=0.6, bevel=0)
    ic.add(rect(6 + ox, 19.5 + oy, 58 + ox, 24.5 + oy), "stone", base=0.6, grad=0.4)
    ic.add(poly([(5 + ox, 20 + oy), (59 + ox, 20 + oy), (32 + ox, 5 + oy)]), "green", base=0.55, grad=0.6)
    ic.add(poly([(12 + ox, 18.5 + oy), (52 + ox, 18.5 + oy), (32 + ox, 9 + oy)]), "stone", base=0.55, grad=0.5, bevel=0.8)
    ic.add(circle(32 + ox, 14.5 + oy, 3.2), "gold", mode="sphere", base=0.7)
    ic.add(rect(7 + ox, 47 + oy, 57 + ox, 51 + oy), "stone", base=0.6, grad=0.4)
    ic.add(rect(4 + ox, 51 + oy, 60 + ox, 57 + oy), "stone", base=0.45, grad=0.4)
    return ic


# ====================================================================== MARKET hub (green + gold, money)
def t_bazaar():
    ic = Icon("bazaar")
    ic.add(rect(12, 24, 16.5, 64), "wood", mode="cyl", axis=(0, 1), base=0.55)                          # posts
    ic.add(rect(55.5, 24, 60, 64), "wood", mode="cyl", axis=(0, 1), base=0.45)
    ic.add(rect(10, 46, 62, 62), "wood", base=0.5, grad=0.5, pattern=hstripes(4, 0.08))                 # counter
    ic.add(rect(8, 43, 64, 47.5), "wood", base=0.68, grad=0.4)
    ic.add(circle(21, 38.5, 4.6), "red", mode="sphere", base=0.6)                                       # goods
    ic.add(circle(30, 39, 4.2), "gold", mode="sphere", base=0.62)
    ic.add(circle(25.5, 33.5, 4.0), "green", mode="sphere", base=0.6)
    obox(ic, 40, 34, 51, 43, 6, "wood", base=0.5)
    # striped awning + scalloped edge
    n = 6
    for k in range(n):
        tx0, tx1 = 12 + 48 * k / n, 12 + 48 * (k + 1) / n
        bx0, bx1 = 5 + 62 * k / n, 5 + 62 * (k + 1) / n
        ic.add(poly([(tx0, 9), (tx1, 9), (bx1, 23), (bx0, 23)]), "green" if k % 2 == 0 else "cream",
               base=0.55 if k % 2 == 0 else 0.72, grad=0.5, bevel=0.7)
        ic.add(circle((bx0 + bx1) / 2, 23, (bx1 - bx0) / 2), "green" if k % 2 == 0 else "cream",
               base=0.4 if k % 2 == 0 else 0.58, bevel=0.7)
    return ic


def t_auctions():
    ic = Icon("auctions")
    ic.add(ellipse(36, 60, 21, 5), "wood", base=0.3, grad=0.4)                                          # sound block
    ic.add(rect(15, 54, 57, 60), "wood", base=0.35, grad=0.5)
    ic.add(ellipse(36, 54, 21, 5), "wood", base=0.66, grad=0.5, line=True)
    ic.add(poly(rp(box(-2.8, 0, 2.8, 34), -40, 33, 26)), "wood", base=0.55, grad=0.5, bevel=0.8)        # handle
    head = box(-15, -7.5, 15, 7.5)
    ic.add(poly(rp(head, 50, 33, 26)), "mahog", base=0.58, grad=0.6, bevel=1.2, bev=0.2, line=True)
    for s in (-10.5, 10.5):
        ic.add(poly(rp(box(s - 1.8, -7.8, s + 1.8, 7.8), 50, 33, 26)), "gold", base=0.62, grad=0.5, bevel=0.6)
    return ic


def t_merchants():
    ic = Icon("merchants")
    ic.add(poly([(24, 64), (48, 64), (43, 57), (29, 57)]), "gold", base=0.5, grad=0.5)                 # foot
    ic.add(rect(34, 12, 38, 58), "gold", mode="cyl", axis=(0, 1), base=0.58)                            # post
    ic.add(circle(36, 10, 3.8), "gold", mode="sphere", base=0.68)
    ic.add(capsule(10, 19, 62, 19, 2.1), "gold", mode="cyl", axis=(1, 0), base=0.6)                     # beam
    for px_, b in ((14, 0.55), (58, 0.45)):
        ic.add(union(capsule(px_, 20, px_ - 8.5, 40, 0.7), capsule(px_, 20, px_ + 8.5, 40, 0.7)), "gold", base=0.5, bevel=0)
        ic.add(diff(ellipse(px_, 40, 11, 7), rect(0, 0, 72, 40)), "gold", base=b, grad=0.5, line=True)
        ic.add(ellipse(px_, 40, 11, 2.2), "gold", base=b + 0.2, bevel=0, cast=False)
    ic.add(circle(14, 37.5, 2.8), "green", mode="sphere", base=0.6)                                    # a coin + a gem on the pans
    ic.add(poly([(58, 33.5), (61, 37.5), (58, 39.5), (55, 37.5)]), "emerald", base=0.62, grad=0.6, bevel=0.5)
    return ic


# ====================================================================== SMITHING hub (steel + amber)
def t_gear():
    ic = Icon("gear")
    plume = union(*[circle(36 + 3.2 * k, 12 - 1.2 * k + 0.12 * k * k, 5.2 - 0.25 * k) for k in range(8)])
    ic.add(plume, "amber", base=0.55, grad=0.6, pattern=folds(1.3, 0.06), line=True)
    helm = union(circle(36, 33, 20), rrect(16, 33, 56, 62, 5))
    ic.add(helm, "steel", base=0.6, grad=0.6, bevel=1.3, bev=0.2, line=True)
    ic.add(rect(34.4, 13.5, 37.6, 36), "steel", base=0.82, bevel=0, cast=False)                        # ridge
    ic.add(union(rect(21, 37, 51, 41.5), rect(34, 41.5, 38, 55)), "navy", base=0.15, bevel=0, cast=False)   # T visor
    for (x, y) in ((22, 50), (50, 50), (22, 56), (50, 56)):
        ic.add(circle(x, y, 1.4), "steel", mode="sphere", base=0.8, bevel=0)
    return ic


def t_recipes():
    ic = Icon("recipes")
    ic.add(rect(16, 14, 56, 58), "cream", base=0.68, grad=0.45)
    ic.add(capsule(11, 13, 61, 13, 4.6), "cream", mode="cyl", axis=(1, 0), base=0.62)
    ic.add(capsule(11, 59, 61, 59, 4.6), "cream", mode="cyl", axis=(1, 0), base=0.5)
    for i in range(3):
        for j in range(3):
            x0, y0 = 22 + 10 * i, 21.5 + 10 * j
            ic.add(rect(x0, y0, x0 + 8, y0 + 8), "cream", base=0.3, bevel=0, cast=False)
    ic.add(rect(33.5, 23, 38.5, 28), "gold", base=0.62, grad=0.6, bevel=0.6)                           # ingot (top middle)
    ic.add(capsule(35.9, 33.5, 35.9, 39.5, 1.2), "wood", base=0.6, bevel=0)                            # stick (centre)
    ic.add(capsule(35.9, 43.5, 35.9, 49.5, 1.2), "wood", base=0.55, bevel=0)                           # stick (bottom)
    ic.add(poly([(26, 23), (29, 25.5), (26, 28), (23, 25.5)]), "emerald", base=0.62, grad=0.6, bevel=0.5)
    return ic


def t_reforge():
    ic = Icon("reforge")
    anvil = poly([(6, 29), (20, 27), (58, 27), (64, 29), (64, 35), (52, 37), (47, 43), (49, 48), (56, 50), (56, 58), (16, 58),
                  (16, 50), (23, 48), (25, 43), (21, 37), (12, 35)])
    ic.add(anvil, "steel", base=0.55, grad=0.6, bevel=1.3, bev=0.2, line=True)
    ic.add(rect(20, 27, 64, 30), "steel", base=0.85, bevel=0, cast=False)
    ic.add(rrect(28, 20, 46, 27.5, 1.5), "amber", base=0.72, grad=0.5, bevel=0.6, line=True)          # glowing blade blank
    for (x, y, r) in ((24, 13, 4.6), (37, 8.5, 5.6), (50, 14, 4.2)):
        ic.add(poly(star_pts(x, y, r, r * 0.38, 4)), "amber", base=0.75, grad=0.4, bevel=0)
    return ic


def t_upgrade():
    ic = Icon("upgrade")
    arrow = poly([(36, 5), (62, 32), (47, 32), (47, 61), (25, 61), (25, 32), (10, 32)])
    ic.add(arrow, "gold", base=0.6, grad=0.6, bevel=1.4, bev=0.22, line=True)
    ic.add(poly([(36, 14), (52, 30.5), (20, 30.5)]), "gold", base=0.8, grad=0.3, bevel=0, cast=False)
    ic.add(poly(star_pts(36, 45, 7.5, 3.1, 5)), "amber", base=0.5, grad=0.5, bevel=0.6, line=True)
    return ic


# ====================================================================== WORLD hub (amber / gold, travel)
def t_island():
    ic = Icon("island")
    top, rw, depth = 44, 27, 20
    rock = poly([(C - rw, top), (C + rw, top), (C + rw * 0.82, top + depth * 0.35), (C + rw * 0.45, top + depth * 0.6),
                 (C + rw * 0.12, top + depth), (C - rw * 0.2, top + depth * 0.82), (C - rw * 0.55, top + depth * 0.5),
                 (C - rw * 0.85, top + depth * 0.3)])
    ic.add(rock, "stone", base=0.42, grad=0.6, pattern=hstripes(4, 0.1, 1))
    ic.add(inter(rock, rect(0, top - 1, 72, top + 4)), "soil", base=0.5, grad=0.4, bevel=0)
    ic.add(union(ellipse(C, top - 1, rw + 1, 5.5), *[circle(C - rw + 3 + 6 * k, top + 3.6, 1.6) for k in range(0, 9, 2)]),
           "grass", base=0.6, grad=0.6)
    ic.add(rect(45.5, 45, 49.5, 66), "glass", base=0.7, grad=0.3, bevel=0, pattern=hstripes(3, 0.15))  # waterfall
    ic.add(rect(33.5, 26, 38.5, 43), "wood", mode="cyl", axis=(0, 1), base=0.55)                       # tree
    ic.add(circle(28, 25, 7.5), "green", mode="sphere", base=0.45)
    ic.add(circle(44, 24, 7.5), "green", mode="sphere", base=0.4)
    ic.add(circle(36, 17, 11), "green", mode="sphere", base=0.58, line=True)
    return ic


def t_explore():
    ic = Icon("explore")
    ic.add(ering(36, 8.5, 4.6, 4.2, 2.4, 2.0), "gold", base=0.6, bevel=0)
    ic.add(circle(36, 38, 26), "gold", mode="sphere", base=0.6)
    ic.add(circle(36, 38, 20.5), "cream", base=0.72, grad=0.4, bevel=0, line=True)
    for (x0, y0, x1, y1) in ((35, 19, 37, 23), (35, 53, 37, 57), (17, 37, 21, 39), (51, 37, 55, 39)):
        ic.add(rect(x0, y0, x1, y1), "cream", base=0.3, bevel=0, cast=False)
    ic.add(poly([(36, 20), (41.5, 38), (30.5, 38)]), "red", base=0.62, grad=0.6, bevel=0.6, line=True)
    ic.add(poly([(30.5, 38), (41.5, 38), (36, 56)]), "steel", base=0.55, grad=0.6, bevel=0.6, line=True)
    ic.add(circle(36, 38, 2.4), "gold", mode="sphere", base=0.7)
    return ic


def t_quests():
    ic = Icon("quests")
    ic.add(rect(14, 22, 19, 65), "wood", mode="cyl", axis=(0, 1), base=0.5)
    ic.add(rect(53, 22, 58, 65), "wood", mode="cyl", axis=(0, 1), base=0.42)
    ic.add(rect(10, 17, 62, 50), "wood", base=0.52, grad=0.5, pattern=hstripes(5.5, 0.08), line=True)
    ic.add(poly([(5, 19), (67, 19), (59, 8), (13, 8)]), "mahog", base=0.55, grad=0.6, pattern=hstripes(3, 0.07), line=True)
    paper = poly(rp(box(-10, -13, 10, 13), 4, 36, 34))
    ic.add(paper, "cream", base=0.75, grad=0.4, bevel=0.8, line=True)
    ic.add(rrect(33.6, 24.5, 38.4, 37.5, 2), "amber", base=0.6, grad=0.5, bevel=0.6)
    ic.add(circle(36, 42, 2.6), "amber", mode="sphere", base=0.62)
    ic.add(circle(36.6, 22.5, 1.8), "red", mode="sphere", base=0.7)
    return ic


# ====================================================================== SOCIAL hub (violet)
def t_players():
    ic = Icon("players")
    ic.add(poly([(15, 70), (17, 60), (24, 57), (44, 57), (51, 60), (53, 70)]), "violet", base=0.5, grad=0.5)
    ic.add(rect(28, 53, 40, 59), "skin", base=0.3, bevel=0)
    x0, y0, x1, y1, d = 16, 25, 47, 56, 14
    obox(ic, x0, y0, x1, y1, d, "skin", base=0.55)
    ox, oy = d * 0.55, d * 0.6
    ic.add(poly([(x0, y0), (x1, y0), (x1 + ox, y0 - oy), (x0 + ox, y0 - oy)]), "hair", base=0.72, grad=0.4)
    ic.add(union(rect(x0, y0, x1, y0 + 6.5), rect(x0, y0, x0 + 4, y0 + 14)), "hair", base=0.5, grad=0.4)
    ic.add(poly([(x1, y0), (x1 + ox, y0 - oy), (x1 + ox, y0 + 15 - oy), (x1, y0 + 15)]), "hair", base=0.28, grad=0.3)
    for ex in (24, 35):
        ic.add(rect(ex, 36, ex + 5, 41), "cream", base=0.85, bevel=0, cast=False)
        ic.add(rect(ex + 2.5, 36, ex + 5, 41), "navy", base=0.4, bevel=0, cast=False)
    ic.add(rect(28, 47, 36, 49.5), "skin", base=0.18, bevel=0, cast=False)
    for ly in ic.layers:
        ly.shape = inter(ly.shape, rect(0, 0, 72, 66))
    return ic


def t_party():
    ic = Icon("party")
    bust(ic, 16, 14, 0.9, PALC["violet"], base=0.36)
    bust(ic, 56, 14, 0.9, PALC["violet"], base=0.3)
    bust(ic, 36, 10, 1.15, PALC["violet"], base=0.74, line=True)
    for ly in ic.layers:
        ly.shape = inter(ly.shape, rect(0, 0, 72, 64))
    ic.add(poly(star_pts(36, 51, 6, 2.5, 5)), "gold", base=0.75, grad=0.5, bevel=0.5, line=True)
    return ic


def t_guild():
    ic = Icon("guild")
    cloth = poly([(17, 11), (55, 11), (55, 64), (36, 53), (17, 64)])
    ic.add(cloth, "violet", base=0.52, grad=0.5, pattern=folds(0.42, 0.09, 17))
    ic.add(diff(cloth, poly([(20.5, 14), (51.5, 14), (51.5, 58.3), (36, 49.6), (20.5, 58.3)])), "gold", base=0.55, grad=0.5, bevel=0, cast=False)
    shield = poly([(27, 21), (45, 21), (45, 33), (36, 42), (27, 33)])
    ic.add(shield, "gold", base=0.65, grad=0.6, bevel=0.8, line=True)
    ic.add(poly([(29.8, 23.6), (42.2, 23.6), (42.2, 32), (36, 38.4), (29.8, 32)]), "violet", base=0.3, grad=0.4, bevel=0, cast=False)
    ic.add(poly(star_pts(36, 29.5, 5.2, 1.7, 4)), "gold", base=0.85, bevel=0)
    ic.add(capsule(11, 10, 61, 10, 2.5), "gold", mode="cyl", axis=(1, 0), base=0.55)
    ic.add(circle(8, 10, 3.4), "gold", mode="sphere", base=0.62)
    ic.add(circle(64, 10, 3.4), "gold", mode="sphere", base=0.62)
    return ic


# ====================================================================== SETTINGS hub (steel)
def t_settings():
    ic = Icon("settings")
    for k, (y, kx) in enumerate(((20, 46), (36, 26), (52, 40))):
        ic.add(capsule(12, y, 60, y, 3.0), "steel", base=0.25, grad=0.3, bevel=0.6)                       # track
        ic.add(capsule(12, y, kx, y, 3.0), "teal", base=0.55, grad=0.4, bevel=0.6)                        # filled part
        ic.add(circle(kx, y, 6.5), "steel", mode="sphere", base=0.68, line=True)                          # knob
        ic.add(circle(kx, y, 2.4), "gold", base=0.6, bevel=0, cast=False)
    return ic


def t_hud():
    ic = Icon("hud")
    ic.add(rrect(6, 11, 66, 61, 4), "steel", base=0.55, grad=0.6, bevel=1.2, bev=0.2)
    ic.add(rect(11, 16, 61, 56), "navy", base=0.3, grad=-0.2, bevel=0, line=True)
    for k in range(3):
        ic.add(heart(17 + 8 * k, 21.5, 0.2), "red", base=0.62, grad=0.5, bevel=0.4)
    ic.add(rect(14, 31, 38, 34), "blue", base=0.6, bevel=0, cast=False)
    ic.add(rect(38, 31, 44, 34), "navy", base=0.6, bevel=0, cast=False)
    ic.add(union(capsule(36, 38, 36, 44, 0.9), capsule(33, 41, 39, 41, 0.9)), "cream", base=0.75, bevel=0, cast=False)
    for k in range(6):
        x0 = 15 + 7.3 * k
        ic.add(rect(x0, 47, x0 + 6, 53), "steel", base=0.62 if k != 1 else 0.85, bevel=0.6, line=True)
    ic.add(rect(23.5, 49, 26.5, 51), "gold", base=0.7, bevel=0, cast=False)
    return ic


def t_layout():
    ic = Icon("layout")
    for (x0, y0, b) in ((10, 10, 0.62), (38, 10, 0.55), (10, 38, 0.5)):
        ic.add(rrect(x0, y0, x0 + 24, y0 + 24, 3), "steel", base=b, grad=0.5, bevel=1.0, line=True)
        ic.add(rrect(x0 + 5, y0 + 5, x0 + 19, y0 + 19, 2), "steel", base=b - 0.25, bevel=0, cast=False)
    ic.add(rrect(38, 38, 62, 62, 3), "steel", base=0.2, bevel=0, cast=False)                             # the empty spot
    ic.add(rrect(42, 42, 66, 66, 3), "gold", base=0.6, grad=0.6, bevel=1.1, bev=0.2, line=True)          # the tile being moved
    ic.add(poly(star_pts(54, 54, 6, 2.4, 4)), "gold", base=0.9, bevel=0, cast=False)
    return ic


def t_mods():
    ic = Icon("mods")
    piece = diff(union(rrect(15, 22, 53, 60, 3), circle(34, 16.5, 7), circle(58.5, 41, 7)), circle(15, 41, 6.5))
    ic.add(piece, "steel", base=0.58, grad=0.6, bevel=1.3, bev=0.2, line=True)
    ic.add(diff(rrect(20, 27, 48, 55, 2), circle(15, 41, 10)), "teal", base=0.42, grad=0.4, bevel=0.6, cast=False)
    return ic


def t_setup():
    ic = Icon("setup")
    ic.add(gear(47, 26, 20, 15, 9, hole=6, tooth=0.5), "steel", base=0.45, grad=0.5, bevel=1.0, line=True)
    wr = [(-3.8, -10), (3.8, -10), (3.8, 30), (-3.8, 30)]
    ic.add(poly(rp(wr, -45, 32, 40)), "steel", base=0.66, grad=0.55, bevel=1.1, bev=0.2, line=True)
    hc = rp([(0, -16)], -45, 32, 40)[0]
    jaw = diff(circle(hc[0], hc[1], 10.5), poly(rp(box(-3.6, -30, 3.6, -15), -45, 32, 40)))
    ic.add(jaw, "steel", base=0.7, grad=0.55, bevel=1.2, bev=0.2, line=True)
    ic.add(poly(rp(box(-1.6, 6, 1.6, 26), -45, 32, 40)), "gold", base=0.6, bevel=0, cast=False)
    return ic


# ====================================================================== HUB ROW (one per hub)
def r_home():
    ic = Icon("home")
    ic.add(rect(47, 11, 54, 26), "stone", base=0.5, grad=0.5)                                            # chimney
    ic.add(rect(14, 33, 58, 63), "cream", base=0.62, grad=0.45)                                          # walls
    ic.add(poly([(6, 36), (36, 9), (66, 36)]), "mahog", base=0.55, grad=0.6, pattern=hstripes(3.5, 0.07), line=True)
    ic.add(rrect(30, 45, 42, 63, 1.5), "wood", base=0.4, grad=0.4, line=True)                            # door
    ic.add(circle(39, 55, 1.2), "gold", base=0.85, bevel=0, cast=False)
    for x0 in (17.5, 46.5):
        ic.add(rect(x0, 41, x0 + 8, 49), "amber", base=0.85, bevel=0, line=True)                          # lit windows
        ic.add(union(rect(x0 + 3.4, 41, x0 + 4.6, 49), rect(x0, 44.4, x0 + 8, 45.6)), "wood", base=0.4, bevel=0, cast=False)
    ic.add(circle(36, 25, 3.3), "gold", mode="sphere", base=0.7)
    return ic


def r_character():
    ic = Icon("character")
    ic.add(poly([(8, 68), (11, 54), (22, 49), (50, 49), (61, 54), (64, 68)]), "teal", base=0.55, grad=0.55, bevel=1.1, line=True)  # shoulders
    ic.add(rect(30, 44, 42, 51), "skin", base=0.3, bevel=0)                                            # neck
    ic.add(rect(19, 12, 53, 46), "skin", base=0.6, grad=0.5, bevel=1.1, bev=0.2, line=True)           # front-view head
    ic.add(union(rect(19, 12, 53, 20), rect(19, 12, 23.5, 30), rect(48.5, 12, 53, 30)), "hair", base=0.55, grad=0.5)
    for ex in (26, 40):
        ic.add(rect(ex, 27, ex + 6, 33), "cream", base=0.85, bevel=0, cast=False)
        ic.add(rect(ex + 3, 27, ex + 6, 33), "navy", base=0.4, bevel=0, cast=False)
    ic.add(rect(31, 39, 41, 41.5), "skin", base=0.2, bevel=0, cast=False)
    ic.add(poly([(36, 51), (42, 58), (36, 65), (30, 58)]), "gold", base=0.66, grad=0.6, bevel=0.8, line=True)  # gold collar gem
    ic.add(poly([(36, 54.5), (38.6, 58), (36, 61.5), (33.4, 58)]), "emerald", base=0.65, bevel=0, cast=False)
    for ly in ic.layers:
        ly.shape = inter(ly.shape, rect(0, 0, 72, 68))
    return ic


def r_storage():
    ic = Icon("storage")
    f, t, r = obox(ic, 9, 32, 53, 62, 16, "wood", base=0.5, pattern=hstripes(5, 0.06))
    ic.add(rect(9, 38, 53, 41), "mahog", base=0.35, bevel=0, cast=False)                                 # lid seam
    for bx in (16, 44):
        ic.add(rect(bx, 32, bx + 4, 62), "gold", base=0.58, grad=0.5, bevel=0.6)
        ic.add(poly([(bx, 32), (bx + 4, 32), (bx + 4 + 8.8, 32 - 9.6), (bx + 8.8, 32 - 9.6)]), "gold", base=0.75, bevel=0)
    ic.add(rrect(27, 36, 35, 46, 1.5), "gold", base=0.65, grad=0.6, bevel=0.8, line=True)               # lock
    ic.add(circle(31, 40, 1.5), "navy", base=0.2, bevel=0, cast=False)
    return ic


def r_market():
    ic = Icon("market")
    for k in range(5):
        yk = 62 - 4 * k
        ic.add(union(rect(7, yk, 29, yk + 3.2), ellipse(18, yk + 3.2, 11, 3)), "gold", base=0.38, grad=0.5, bevel=0)
        ic.add(ellipse(18, yk, 11, 3), "gold", base=0.8, grad=0.5, bevel=0.6)
    ic.add(circle(45, 31, 21), "gold", mode="sphere", base=0.62, line=True)
    ic.add(ering(45, 31, 17, 17, 15, 15), "gold", base=0.35, bevel=0, cast=False)
    ic.add(poly([(45, 20), (53, 31), (45, 42), (37, 31)]), "emerald", base=0.6, grad=0.7, bevel=0.9, bev=0.2, line=True)
    return ic


def r_smithing():
    ic = Icon("smithing")
    for ang, base in ((-38, 0.5), (38, 0.66)):
        ic.add(poly(rp(box(-3.2, -8, 3.2, 37), ang, 36, 32)), "wood", base=base, grad=0.5, bevel=0.8)
        ic.add(poly(rp(box(-14.5, -22, 14.5, -7), ang, 36, 32)), "steel", base=base, grad=0.6, bevel=1.2, bev=0.2, line=True)
        ic.add(poly(rp(box(-4.2, -22.5, 4.2, -6.5), ang, 36, 32)), "amber", base=base, bevel=0, cast=False)
    return ic


def r_world():
    ic = Icon("world")
    globe = circle(36, 36, 27)
    ic.add(globe, "blue", mode="sphere", base=0.55)
    land = union(ellipse(26, 26, 11, 7), ellipse(22, 34, 6, 9), ellipse(47, 43, 10, 7), ellipse(50, 23, 5, 4), ellipse(34, 55, 8, 3.5))
    ic.add(inter(land, globe), "green", base=0.6, grad=0.6, bevel=0.7, line=True)
    ic.add(inter(ering(36, 36, 13, 27, 11.8, 25.8), globe), "cloud", base=0.4, bevel=0, cast=False, rim=False)
    ic.add(inter(rect(9, 35.4, 63, 36.6), globe), "cloud", base=0.4, bevel=0, cast=False, rim=False)
    ic.add(ering(36, 36, 31, 9, 28.5, 7), "gold", mode="torus", torus=(36, 36, 31, 9, 28.5, 7), base=0.6, bevel=0)
    ic.add(inter(ering(36, 36, 31, 9, 28.5, 7), rect(0, 36, 72, 72)), "gold", base=0.7, bevel=0, line=True)
    return ic


def r_social():
    ic = Icon("social")
    bust(ic, 25, 10, 1.0, PALC["violet"], base=0.4)
    bust(ic, 47, 14, 1.05, PALC["violet"], base=0.72, line=True)
    for ly in ic.layers:
        ly.shape = inter(ly.shape, rect(0, 0, 72, 66))
    return ic


def r_settings():
    ic = Icon("settings")
    ic.add(gear(36, 36, 29, 22, 10, hole=9, tooth=0.5, rot=9), "steel", base=0.58, grad=0.6, bevel=1.3, bev=0.2, line=True)
    ic.add(ering(36, 36, 15, 15, 9, 9), "steel", mode="torus", torus=(36, 36, 15, 15, 9, 9), base=0.6, bevel=0, line=True)
    ic.add(ering(36, 36, 9, 9, 6.5, 6.5), "gold", base=0.6, bevel=0, cast=False)
    return ic


# ====================================================================== the icon list
# (hub, tab, label on the tab, builder, what it shows)
TABS = [
    ("character", "stats", "Stats", t_stats, "a red heart with three rising gold bars inside it"),
    ("character", "skills", "Skills", t_skills, "a gold star medal (teal centre, gold star) on two teal ribbons"),
    ("character", "trees", "Trees", t_trees, "a branching tree: a trunk that splits into three round green crowns, each with a gold node (a skill tree)"),
    ("character", "class", "Class", t_class, "a crossed wooden staff (violet orb in a gold claw) and steel sword (gold guard)"),
    ("character", "pets", "Pets", t_pets, "a sitting cream bunny facing left (long ears with pink insides, round tail)"),
    ("character", "accessories", "Accessories", t_accessories, "a gold chain amulet with a teal diamond gem in a round gold setting"),
    ("character", "collections", "Collections", t_collections, "an open teal book with text lines and a gold bookmark ribbon"),
    ("character", "profiles", "Profiles", t_profiles, "a gold picture frame holding a teal player portrait (head and shoulders)"),
    ("storage", "pocket", "Pocket", t_pocket, "the SkyWynn Menu's Pocket Dimension tile: a teal drawstring pouch with a violet-teal swirl rising out of its void opening"),
    ("storage", "requip", "Requip", t_requip, "a steel chestplate with teal pauldrons hanging on a gold clothes hanger"),
    ("storage", "vault", "Vault", t_vault, "a round steel vault door (bolt ring, side hinge) with a gold spoked wheel"),
    ("storage", "bank", "Bank", t_bank, "a stone bank with four columns, a green roof, a gold coin in the pediment and steps"),
    ("storage", "supplies", "Supplies", t_supplies, "the approved black-leather satchel (stepped flap, strap tongue, gold clasp) with a red potion flask and a tied brown food pouch peeking out of its top"),
    ("market", "bazaar", "Bazaar", t_bazaar, "a market stall: green / cream striped scalloped awning, wooden counter, fruit and a crate"),
    ("market", "auctions", "Auctions", t_auctions, "an auction gavel (mahogany head, gold bands) over its round sound block"),
    ("market", "merchants", "Merchants", t_merchants, "gold balance scales with a coin on one pan and an emerald on the other"),
    ("smithing", "gear", "Gear", t_gear, "a steel knight helmet with a T visor, rivets and an amber plume"),
    ("smithing", "recipes", "Recipes", t_recipes, "a recipe scroll with a 3 x 3 crafting grid (gold ingot, two sticks, an emerald)"),
    ("smithing", "reforge", "Reforge", t_reforge, "a steel anvil with a glowing amber blade blank and three amber sparks"),
    ("smithing", "upgrade", "Upgrade", t_upgrade, "a big gold up-arrow with an amber star in its shaft"),
    ("smithing", "identify", "Identify", t_identify, "the SkyWynn Menu's Identify tile: a gold magnifying glass over a cut emerald (the gem shows magnified in the lens)"),
    ("world", "teleport", "Teleport", t_teleport, "the SkyWynn Menu's Teleport tile: a gold portal ring (amber gem studs) round swirling amber energy on a stone plinth"),
    ("world", "island", "Island", t_island, "a floating island with one round tree and a little waterfall"),
    ("world", "explore", "Explore", t_explore, "a gold compass with a cream face, red north / steel south needle"),
    ("world", "quests", "Quests", t_quests, "a wooden job board (mahogany roof) with a pinned paper showing an amber '!'"),
    ("social", "players", "Players", t_players, "a blocky player head in 3/4 view (brown hair, two eyes) on violet shoulders"),
    ("social", "party", "Party", t_party, "three violet player busts (the front one bigger) over a gold star"),
    ("social", "guild", "Guild", t_guild, "a violet guild banner with a gold edge and a gold shield + star, on a gold rod"),
    ("settings", "settings", "Settings", t_settings, "three slider tracks with teal fill and steel knobs at different spots"),
    ("settings", "hud", "HUD", t_hud, "a steel screen frame showing HUD parts: three hearts, a mana bar, a crosshair and a hotbar"),
    ("settings", "layout", "Layout", t_layout, "a 2 x 2 grid of steel tiles; the fourth tile is gold and lifted out of its spot (being moved)"),
    ("settings", "mods", "Mods", t_mods, "a steel puzzle piece with a teal face"),
    ("settings", "setup", "Server Setup", t_setup, "a steel wrench in front of a steel cog"),
]
ROW = [
    ("hubrow", "home", "Home", r_home, "a little house: mahogany roof, cream walls, two lit windows, a chimney"),
    ("hubrow", "character", "Character", r_character, "a front-view blocky player head (brown hair) on teal shoulders with a gold-and-emerald collar gem"),
    ("hubrow", "storage", "Storage", r_storage, "a wooden chest with gold bands and a gold lock"),
    ("hubrow", "market", "Market", r_market, "a stack of gold coins next to a big gold coin with an emerald"),
    ("hubrow", "smithing", "Smithing", r_smithing, "two crossed smithing hammers (steel heads, amber cores)"),
    ("hubrow", "world", "World", r_world, "a blue globe with green islands, faint lines and a gold ring round it"),
    ("hubrow", "social", "Social", r_social, "two violet player busts, one behind the other"),
    ("hubrow", "settings", "Settings", r_settings, "a steel cog with a gold centre ring"),
]
ALL = TABS + ROW
HUB_ORDER = ["character", "storage", "market", "smithing", "world", "social", "settings"]


def fname(hub, tab, mode):
    return "%s_%s%s.png" % (hub, tab, "_on" if mode == "on" else "")


def recentre(img):
    """move the painted motif (whole px) so its bounding box sits in the middle of the 72 px square"""
    pts = [(x, y) for y in range(S) for x in range(S) if img[y][x][3]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    dx = int(round((S - 1 - max(xs) - min(xs)) / 2.0)); dy = int(round((S - 1 - max(ys) - min(ys)) / 2.0))
    out = P.new(S, S)
    for x, y in pts:
        if 0 <= x + dx < S and 0 <= y + dy < S: out[y + dy][x + dx] = list(img[y][x])
    return out


def build_icons():
    """(hub, tab) -> {"base": hard-alpha image, "normal": (img, png), "on": (img, png)} - pure, no file writes"""
    out = {}
    for hub, tab, label, fn, what in ALL:
        base = recentre(fn().render())
        d = {"base": base}
        for mode in ("normal", "on"):
            img = fade(base, mode)
            d[mode] = (img, png_bytes(img))
        out[(hub, tab)] = d
    return out


# ====================================================================== contact sheet
BG = (24, 26, 38); PANEL = (34, 37, 52); INK = (226, 228, 236); DIM = (150, 156, 176); GOLDT = hx("#e0b060")


def load_kit(name):
    return P.read_png(open(os.path.join(KIT, name + "@2x.png"), "rb").read())


def nine(src, w, h, hb, vb):
    """9-slice (stretched edges + centre, like the client) -> an RGBA image w x h; hb / vb in px"""
    sw, sh = P.size(src); out = P.new(w, h)
    def mapc(t, n, s, b):
        if t < b: return t
        if t >= n - b: return s - (n - t)
        return b + int((t - b) * (s - 2 * b) / max(1, n - 2 * b))
    for y in range(h):
        sy = mapc(y, h, sh, vb)
        for x in range(w):
            out[y][x] = list(src[sy][mapc(x, w, sw, hb)])
    return out


def word(cv, cx, cy, s, col, scale=3):
    """the tab word, centred (5 x 7 bitmap font, drawn twice 1 px apart = a bolder stroke like the game's button font)"""
    w = len(s) * 6 * scale - scale + 1
    x = int(cx - w / 2); y = int(cy - 7 * scale / 2)
    cv.text(x, y, s, col, scale); cv.text(x + 1, y, s, col, scale)


def tab_w(n):
    """hub bar rule (Hubs-Spec 2.2): tw = (w - 5 (n - 1)) / n on the 960 page, capped at 190 UI"""
    return min(190, int((960 - 5 * (n - 1)) / n))


def draw_tab(cv, x, y, wui, state, icon, label, scale=2):
    w, h = wui * scale, 44 * scale
    t = nine(load_kit(state), w, h, 40, 24)
    if scale == 1:
        t = P.downsample(nine(load_kit(state), w * 2, h * 2, 40, 24), 2)
    cv.blit(t, x, y)
    ic = icon if scale == 2 else P.downsample(icon, 2)
    s = P.size(ic)[0]
    cv.blit(ic, x + (w - s) // 2, y + (h - s) // 2)
    col = LABEL["buttonText"] if state == "Tab_Selected" else LABEL["button2Text"]
    word(cv, x + w / 2, y + h / 2, label.upper(), col, 3 if scale == 2 else (2 if len(label) <= 8 else 1))


def build_sheet(icons):
    groups = [(h, [t for t in TABS if t[0] == h]) for h in HUB_ORDER] + [("hub row", ROW)]
    gap = 10
    W = 60 + max(len(g) * (tab_w(len(g)) * 2 + gap) for _, g in groups)
    W = max(W, 1900)
    row_h = 88 + 12
    blockh = 40 + 2 * row_h + 30 + 84 + 64 + 16
    H = 150 + len(groups) * (blockh + 14)
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "SKYWYNN HUB TAB ICONS - DRAFT V1 - CONTACT SHEET", GOLDT, 4)
    cv.text(24, 60, "SKYY 2026-10-15: \"SO THE PET TAB STILL SAYS PETS, BUT ALSO SHOWS A LITTLE PET ICON BEHIND THE WORD\" - \"ICON FIRST, THEMED LATER\"", DIM, 2)
    cv.text(24, 84, "ICONS 72 X 72 PX = @2X (36 X 36 UI), CENTRED ON THE REAL SKY TAB TEXTURES AT @2X. ROW 1 NORMAL (TAB), ROW 2 ACTIVE (TAB_SELECTED + _ON).", DIM, 2)
    cv.text(24, 106, "BELOW: EACH ICON ALONE ON CHECKER (NORMAL / ON / UNFADED SOURCE), THEN THE BAR AT 1X (HALF SIZE, ONE TAB ACTIVE). MOCK FONT, NOT THE GAME FONT.", DIM, 2)
    y = 140
    for hub, items in groups:
        n = len(items); wui = tab_w(n)
        cv.rect(16, y, W - 16, y + blockh, PANEL)
        cv.rect(16, y, W - 16, y + 3, GOLDT)
        cv.text(28, y + 13, ("%s  (%d TABS, %d UI WIDE EACH)" % (hub.upper(), n, wui)), GOLDT, 2)
        for r, (state, mode) in enumerate((("Tab", "normal"), ("Tab_Selected", "on"))):
            for k, t in enumerate(items):
                draw_tab(cv, 28 + k * (wui * 2 + gap), y + 40 + r * row_h, wui, state, icons[(t[0], t[1])][mode][0], t[2])
        yy = y + 40 + 2 * row_h + 4
        cv.text(28, yy, "ALONE (NORMAL / ON / SOURCE):", DIM, 1)
        yy += 14
        for k, t in enumerate(items):
            x0 = 28 + k * 236
            d = icons[(t[0], t[1])]
            for j, img in enumerate((d["normal"][0], d["on"][0], d["base"])):
                cv.checker(x0 + j * 76, yy, 72, 72, (52, 56, 74), (44, 48, 64))
                cv.blit(img, x0 + j * 76, yy)
        yy += 84
        cv.text(28, yy, "AT 1X (HALF SIZE), THE SECOND TAB ACTIVE:", DIM, 1)
        yy += 12
        for k, t in enumerate(items):
            act = (k == 1)
            draw_tab(cv, 28 + k * (wui + 5), yy, wui, "Tab_Selected" if act else "Tab",
                     icons[(t[0], t[1])]["on" if act else "normal"][0], t[2], scale=1)
        y += blockh + 14
    return cv.png()


def build_compare(icons):
    """the Supplies review sheet: the Storage tab row (normal + active) with Supplies next to its neighbours, Supplies alone at 4x
    (source / normal / on), and the approved 64 px satchel item icon it follows (art/accessory-bag-icon, our own art)"""
    items = [t for t in TABS if t[0] == "storage"]
    wui = tab_w(len(items)); gap = 10
    W = max(60 + len(items) * (wui * 2 + gap), 1300); H = 640
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "STORAGE > SUPPLIES TAB PICTURE - NEXT TO ITS NEIGHBOURS", GOLDT, 3)
    cv.text(24, 50, "ROW 1 NORMAL (TAB), ROW 2 ACTIVE (TAB_SELECTED + _ON), @2X. MOCK FONT, NOT THE GAME FONT.", DIM, 2)
    for r, (state, mode) in enumerate((("Tab", "normal"), ("Tab_Selected", "on"))):
        for k, t in enumerate(items):
            draw_tab(cv, 24 + k * (wui * 2 + gap), 80 + r * 100, wui, state, icons[(t[0], t[1])][mode][0], t[2])
    y = 290
    cv.text(24, y, "SUPPLIES AT 4X: SOURCE / NORMAL / ON          THE APPROVED SATCHEL ITEM ICON (64 PX, 4X)", DIM, 2)
    d = icons[("storage", "supplies")]
    for j, img in enumerate((d["base"], d["normal"][0], d["on"][0])):
        cv.checker(24 + j * 300, y + 28, 288, 288, (52, 56, 74), (44, 48, 64))
        cv.blit(img, 24 + j * 300, y + 28, 4)
    bag = os.path.join(ROOT, "art", "accessory-bag-icon", "Common", "Icons", "ItemsGenerated", "SkyyAccessories_Bag_Menu.png")
    cv.checker(24 + 3 * 300 + 20, y + 28, 256, 256, (52, 56, 74), (44, 48, 64))
    cv.blit(P.read_png(open(bag, "rb").read()), 24 + 3 * 300 + 20, y + 28, 4)
    return cv.png()


# ====================================================================== write
def sha(b):
    return hashlib.sha256(b).hexdigest()


def manifest(icons):
    files = []; entries = []
    for hub, tab, label, fn, what in ALL:
        d = icons[(hub, tab)]; e = {"hub": hub, "tab": tab, "label": label, "shows": what}
        for mode in ("normal", "on"):
            data = d[mode][1]; f = fname(hub, tab, mode)
            files.append({"path": f, "bytes": len(data), "sha256": sha(data)})
            e["file" if mode == "normal" else "file_on"] = f
            e["min_contrast_x_target" if mode == "normal" else "min_contrast_x_target_on"] = round(min_contrast(d[mode][0], mode), 3)
        entries.append(e)
    return {
        "what": "SkyWynn hub tab icons - a faded picture behind each hub tab's word + one per hub for the hub row (DRAFT v1)",
        "generator": "tools/art/make_hub_tab_icons.py", "validator": "tools/art/make_hub_tab_icons.py --check",
        "reuses": "tools/art/make_menu_icons.py (shape helpers, painter, palettes); reads art/ui-kit-sky Tab textures for the checks",
        "deterministic": True, "original_pixels": True,
        "size": {"px": [S, S], "density": "@2x", "ui_units": [S // 2, S // 2], "tab_ui": "44 high, 110-190 wide",
                 "placement": "centred in the tab, under the label"},
        "fade": {m: {"desat_to_slate": FADE[m]["desat"], "alpha_max": FADE[m]["alpha"], "min_contrast_per_state": FADE[m]["states"],
                     "labels": dict((k, M.hexs(LABEL[k])) for k in FADE[m]["labels"])} for m in FADE},
        "tab_worst_bg": dict((st, M.hexs(tab_worst_bg(st))) for m in FADE for st in FADE[m]["states"]),
        "icons": entries,
        "files": files,
    }


def main(argv):
    icons = build_icons()
    os.makedirs(OUT, exist_ok=True)
    for hub, tab, label, fn, what in ALL:
        for mode in ("normal", "on"):
            with open(os.path.join(OUT, fname(hub, tab, mode)), "wb") as fh:
                fh.write(icons[(hub, tab)][mode][1])
    with open(os.path.join(OUT, "manifest.json"), "w", newline="\n") as fh:
        json.dump(manifest(icons), fh, indent=1); fh.write("\n")
    print("wrote %d icons (%d files) + manifest.json to %s" % (len(ALL), 2 * len(ALL), OUT))
    if "--sheet" in argv:
        p = argv[argv.index("--sheet") + 1]
        with open(p, "wb") as fh:
            fh.write(build_sheet(icons))
        print("wrote contact sheet", p)
    if "--compare" in argv:
        p = argv[argv.index("--compare") + 1]
        with open(p, "wb") as fh:
            fh.write(build_compare(icons))
        print("wrote the Supplies comparison sheet", p)


# ====================================================================== validator
def check_all(argv):
    fails = []
    def check(ok, msg):
        print(("OK    " if ok else "FAIL  ") + msg)
        if not ok: fails.append(msg)
    man = json.load(open(os.path.join(OUT, "manifest.json"), encoding="utf-8"))
    files = dict((f["path"], f) for f in man["files"])
    want = set(fname(t[0], t[1], m) for t in ALL for m in ("normal", "on"))
    check(len(TABS) == 33 and len(ROW) == 8 and not any(t[1] == "multitool" for t in TABS),
          "33 hub tabs (Hubs-Spec 1.2 minus Multitool, merged into Upgrade, + Storage > Supplies) + 8 hub-row icons in the generator")
    check(set(files) == want, "manifest file list = the %d expected files" % len(want))
    present = set(f for f in os.listdir(OUT) if f.endswith(".png"))
    extra = present - want - {"contact-sheet.png", "supplies-compare.png"}
    check(not extra, "no stray PNGs in art/hub-tab-icons %s" % (sorted(extra) or ""))
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    forbidden = ["Assets" + ".zip", "Hytale" + "Server", "App" + "Data", "User" + "Data"]
    art = os.path.join(ROOT, "art")
    check(not any(f in src for f in forbidden) and KIT.startswith(art) and OUT.startswith(art),
          "the generator reads no game file (no vanilla path in it; it reads only art/ui-kit-sky and writes art/hub-tab-icons)")
    fresh = build_icons()
    seen = {}
    for hub, tab, label, fn, what in ALL:
        base = fresh[(hub, tab)]["base"]
        xs = [x for y in range(S) for x in range(S) if base[y][x][3]]; ys = [y for y in range(S) for x in range(S) if base[y][x][3]]
        bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        cx, cy = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
        check(max(bw, bh) >= 50 and min(xs) >= 1 and min(ys) >= 1 and max(xs) <= S - 2 and max(ys) <= S - 2,
              "%s_%s: motif %d x %d px, 1 px margin" % (hub, tab, bw, bh))
        check(abs(cx - (S - 1) / 2.0) <= 4 and abs(cy - (S - 1) / 2.0) <= 4, "%s_%s: centred (bbox centre %.1f, %.1f)" % (hub, tab, cx, cy))
        lumsum = {}
        for mode in ("normal", "on"):
            f = fname(hub, tab, mode); path = os.path.join(OUT, f)
            if not os.path.exists(path):
                check(False, "%s exists" % f); continue
            data = open(path, "rb").read()
            check(P.png_size(data) == (S, S) and data[25] == 6, "%s: %d x %d RGBA" % (f, S, S))
            img = P.read_png(data)
            al = [p[3] for r in img for p in r if p[3]]
            check(max(al) <= int(round(FADE[mode]["alpha"] * 255)) and max(al) < 255, "%s: partly transparent (alpha max %d / 255)" % (f, max(al)))
            mc = min_contrast(img, mode)
            check(mc >= 1.0, "%s: label contrast >= target on every pixel (worst %.2f x target)" % (f, mc))
            h_ = sha(data)
            check(h_ not in seen, "%s: unique (not identical to %s)" % (f, seen.get(h_)))
            seen[h_] = f
            e = files.get(f)
            check(bool(e) and e["bytes"] == len(data) and e["sha256"] == h_, "%s: manifest bytes + sha256" % f)
            check(fresh[(hub, tab)][mode][1] == data, "%s: deterministic (fresh run = same bytes)" % f)
            bg = tab_worst_bg("Tab")
            lumsum[mode] = sum(rel_lum(over(p[:3], p[3] / 255.0, bg)) for r in img for p in r if p[3])
        if len(lumsum) == 2:
            check(lumsum["on"] > lumsum["normal"], "%s_%s: the _on variant is brighter than the normal one" % (hub, tab))
    print("ALL OK" if not fails else "%d FAILED" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        sys.exit(check_all(sys.argv[1:]))
    main(sys.argv[1:])
