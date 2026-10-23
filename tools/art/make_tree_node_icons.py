#!/usr/bin/env python3
"""SkyWynn skill-tree NODE icons - one 64 x 64 icon per node of a Skill Trees 3 tree (DRAFT v1; first tree: Mining).

Skyy (2026-10-23, Character > Trees > Mining at 150 %): "most of these use a pickaxe icon. we should make custom icons for most of these".
Every node gets its OWN picture that shows what the node DOES at a glance (coins from ore = a coin on an ore chunk, the x3 jackpot =
three gems bursting, speed = a pick with motion lines ...), drawn for the dark round node discs of the radial tree pages (SkyyTrees 0.5.0:
18 px icon in a 32 px disc at 100 %, 27 px at 150 %), so every icon is ONE bold subject with a few big accent marks.

COLOUR CODE (research/Vanilla-UI-Style-Guide.md section 15, "colour code everything"): the ACCENT marks of an icon (plus signs, sparkles,
motion lines, rays, arrows, waves) take the colour of WHAT THE NODE BOOSTS - CATS below (yield = the "helps" green #7ee08a, XP = the
level / XP gold #e8c25a, speed = the Air white-teal, health = the red #ff7a7a, damage = the Fire orange, tool / durability = the stat-name
soft white #d6e4ee, pets = the Beastmastery tree colour #d8a070, ability / sense = the Mining tree colour #8fc8ff).

Same family look as the approved art/menu-icons + art/warp-icons: this script REUSES tools/art/make_menu_icons.py (shape helpers, the Icon
painter, palettes, PNG writer - imported, never edited). ORIGINAL pixels only: no game file is read, copied, traced or recoloured.
The node list (ids, names, effect texts) is READ from tools/trees_v3_data.py - the one data table SkyyTrees builds from - so a renamed
node keeps its icon (the icon belongs to the node's saved key, not its name).

Writes (tree = Mining today; --tree <Name> for the next ones once DRAW[<Name>] has its pictures):
  art/tree-node-icons/Common/Icons/ItemsGenerated/Skyy_NodeIcon_<Tree>_<B><R>[a|b|c|Free].png   64 x 64 RGBA, hard alpha, 1 px outline
  art/tree-node-icons/sheet-<tree>.png    review sheet: every icon 2x + 1x with its node name + effect; the 100 % / 150 % disc strips
  art/tree-node-icons/sheet.png           = the newest tree's sheet (the one to show Skyy)
  art/tree-node-icons/manifest.json       node key -> icon item id -> file (bytes, sha256), category, what the icon shows (all trees)

Run:   python tools/art/make_tree_node_icons.py [--tree Mining]      (deterministic: two runs = same bytes)
       python tools/art/make_tree_node_icons.py --check                (build twice, compare, write nothing)
       python tools/art/make_tree_node_icons.py --counts               (node count of every tree, for sizing the next rounds)
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M
from make_menu_icons import (Icon, Shape, circle, ellipse, rect, rrect, poly, capsule, union, diff, inter, ering, star_pts, gear,
                             hstripes, hx, mix, png_bytes, Canvas, sha, rot_ellipse, obox, gem_facets)

ROOT = M.ROOT
sys.path.insert(0, os.path.join(ROOT, "tools"))
import trees_v3_data as V3D

OUT = os.path.join(ROOT, "art", "tree-node-icons")
ICON_DIR_REL = M.ICON_DIR_REL            # Common/Icons/ItemsGenerated
ITEM_PREFIX = "Skyy_NodeIcon_"

# ====================================================================== palettes (dark -> light; shadows cool, lights warm)
PALN = {
    "ore":    ["#0d2638", "#14405e", "#1d6290", "#2a8ac0", "#4cb4e4", "#94dcf6", "#d2f2fc"],
    "flame":  ["#5a1a06", "#922e08", "#cc5410", "#f08a1e", "#ffbe46", "#ffe58a", "#fff4cf"],
    "water":  ["#0a2034", "#10345a", "#18508a", "#2470b8", "#3c94dc", "#78bef0", "#bce2fa"],
    "copper": ["#2e1208", "#4f200f", "#7a3518", "#a64f25", "#cc6e38", "#e8975a", "#f6c69a"],
    "ruby":   ["#33060f", "#5c0c1c", "#8c1530", "#c02346", "#e84a66", "#f78f9c", "#fdd2d4"],
    "diamond": ["#123844", "#1d5a68", "#2f8494", "#4fb2bc", "#86dade", "#c2f2ee", "#eefcf8"],
    "amethyst": ["#1e0c34", "#341656", "#50247e", "#7038a8", "#9658cc", "#bf90e6", "#e6d0f6"],
    "bat":    ["#120c1c", "#1e1530", "#2c2046", "#3e2e60", "#54417c", "#71609a", "#9a8cba"],
    "abyss":  ["#08061a", "#120c30", "#1e1450", "#2e1e72", "#432c96", "#6648bc", "#9a80e0"],
    "lamp":   ["#4a3008", "#7a5410", "#b08018", "#e0b030", "#f8d860", "#fff0a0", "#fffae0"],
    # ---- the ACCENT ramps (CATS): their bright step (index 4) = the section 15 hex of that category
    "acc_yield":   ["#0c2a14", "#17502a", "#23783c", "#3aa456", "#7ee08a", "#b4f0b8", "#e2fbe0"],
    "acc_xp":      ["#3e2a08", "#6a4a10", "#9a7018", "#c89a30", "#e8c25a", "#f6e09a", "#fdf4d2"],
    "acc_speed":   ["#0e2a2c", "#1a4c50", "#2a7a7c", "#4caaa8", "#86d8d0", "#bdf0ea", "#e8fcf8"],
    "acc_health":  ["#3a0c10", "#6a1820", "#a02a30", "#d8484a", "#ff7a7a", "#ffb0a8", "#ffe0da"],
    "acc_damage":  ["#4a1606", "#7c2808", "#b84410", "#e8681c", "#ff9a3c", "#ffc884", "#ffeccc"],
    "acc_tool":    ["#1a222c", "#2e3a48", "#4a5a6c", "#7a8ca0", "#d6e4ee", "#e8f0f6", "#f6fafc"],
    "acc_pet":     ["#2e1608", "#52280e", "#7e4018", "#ac6430", "#d8a070", "#ecc8a0", "#f8ead6"],
    "acc_ability": ["#0c1e36", "#16365e", "#24568c", "#3c7cbc", "#8fc8ff", "#c0e2ff", "#e6f4ff"],
}
for _k, _v in PALN.items():
    if _k not in M.PAL:
        M.PAL[_k] = _v
        M.PALC[_k] = [hx(c) for c in _v]

# what a node boosts -> its accent ramp (sheet legend + manifest)
CATS = [
    ("yield",   "YIELD / LOOT / COINS", "#7ee08a", "style guide 15: a value that helps (green)"),
    ("xp",      "SKILL XP",             "#e8c25a", "style guide 15: level / XP / progress (gold)"),
    ("speed",   "SPEED",                "#86d8d0", "style guide 15: the Air element (white-teal) = movement / swing speed"),
    ("health",  "HEALTH / SAFETY",      "#ff7a7a", "style guide 15: the red stat colour = Health / damage taken"),
    ("damage",  "DAMAGE",               "#ff9a3c", "style guide 15: the Fire element (orange)"),
    ("tool",    "TOOL / DURABILITY",    "#d6e4ee", "style guide 15: the stat-name soft white (gear stats)"),
    ("pet",     "PETS",                 "#d8a070", "the Beastmastery tree colour (SkyyTrees UI_DATA_COLORS)"),
    ("ability", "ABILITY / SENSE",      "#8fc8ff", "the Mining tree colour (SkyyTrees TCOLOR) = the tree's own actives"),
]
CAT_HEX = dict((c[0], c[2]) for c in CATS)


def acc(cat):
    return "acc_" + cat


def A(cat, i=4):
    """an accent colour as #hex (sparkles)"""
    return PALN[acc(cat)][i]


# ====================================================================== part helpers (64-px icon units, y down)
def unit(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L


def pick(ic, hx0, hy0, cx, cy, arm=15.0, bend=5.0, hr=3.3, r=2.5, head="steel", handle="wood", line=True):
    """a pickaxe: handle from (hx0, hy0) to the head centre (cx, cy); the curved head spans 2 x arm across the handle"""
    ux, uy = unit(hx0, hy0, cx, cy)
    px, py = -uy, ux
    ic.add(capsule(hx0, hy0, cx + ux * 2, cy + uy * 2, r), handle, mode="cyl", axis=(ux, uy), base=0.58, pattern=hstripes(5, 0.05))
    a1 = (cx + px * arm * 0.55 - ux * bend * 0.35, cy + py * arm * 0.55 - uy * bend * 0.35)
    a2 = (cx + px * arm - ux * bend, cy + py * arm - uy * bend)
    b1 = (cx - px * arm * 0.55 - ux * bend * 0.35, cy - py * arm * 0.55 - uy * bend * 0.35)
    b2 = (cx - px * arm - ux * bend, cy - py * arm - uy * bend)
    hd = union(capsule(cx, cy, a1[0], a1[1], hr), capsule(a1[0], a1[1], a2[0], a2[1], hr * 0.62),
               capsule(cx, cy, b1[0], b1[1], hr), capsule(b1[0], b1[1], b2[0], b2[1], hr * 0.62))
    ic.add(hd, head, base=0.6, grad=0.6, bevel=1.1, line=line)
    ic.add(circle(cx, cy, hr + 0.7), head, mode="sphere", base=0.5)
    return a2, b2


def ore_chunk(ic, cx, cy, s=1.0, ore="ore", stone="stone", spots=None, line=False):
    pts = [(-14, 8), (-13, -3), (-5, -11), (7, -10.5), (14.5, -2), (13, 9), (2, 12.5)]
    ic.add(poly([(cx + x * s, cy + y * s) for x, y in pts]), stone, base=0.5, grad=0.6, pattern=hstripes(4.5 * s, 0.07, 1), line=line)
    for (x, y, r) in (spots or ((-5, -2, 3.8), (5.5, 3.5, 3.2), (4.5, -6, 2.3), (-6.5, 6.5, 2.2))):
        ic.add(circle(cx + x * s, cy + y * s, r * s), ore, mode="sphere", base=0.62, line=True)


def gem(ic, cx, cy, s, pal, line=False):
    for pts, b in gem_facets(cx, cy, s):
        ic.add(poly(pts), pal, base=b, grad=0.3, bevel=0.6, line=line)


def coin(ic, cx, cy, r):
    ic.add(circle(cx, cy, r), "gold", mode="sphere", base=0.62, line=True)
    ic.add(ering(cx, cy, r * 0.74, r * 0.74, r * 0.6, r * 0.6), "gold", base=0.38, bevel=0, cast=False, rim=False)
    ic.add(poly(star_pts(cx, cy, r * 0.46, r * 0.2, 4)), "gold", base=0.9, bevel=0, cast=False)


def ingot(ic, cx, cy, s, pal):
    ic.add(poly([(cx - 13 * s, cy + 5 * s), (cx + 13 * s, cy + 5 * s), (cx + 10 * s, cy - 3 * s), (cx - 10 * s, cy - 3 * s)]), pal,
           base=0.52, grad=0.5, line=True)
    ic.add(poly([(cx - 10 * s, cy - 3 * s), (cx + 10 * s, cy - 3 * s), (cx + 8 * s, cy - 7 * s), (cx - 8 * s, cy - 7 * s)]), pal,
           base=0.86, grad=0.4, bevel=0.6)


def flame(ic, cx, cy, s, pal="flame"):
    ic.add(union(circle(cx, cy + 3 * s, 7.5 * s), poly([(cx - 7.3 * s, cy + 1.5 * s), (cx - 1 * s, cy - 13 * s), (cx + 7.3 * s, cy + 1.5 * s)])),
           pal, base=0.45, grad=0.7, bevel=0.8)
    ic.add(union(circle(cx, cy + 5 * s, 4.2 * s), poly([(cx - 4 * s, cy + 4 * s), (cx + 0.5 * s, cy - 5 * s), (cx + 4 * s, cy + 4 * s)])),
           pal, base=0.9, grad=0.4, bevel=0, cast=False)


def eye(ic, cx, cy, s, iris="ore", lid="cream"):
    w = 12.0 * s; h = 6.5 * s
    R = (w * w + h * h) / (2 * h)
    alm = inter(circle(cx, cy + R - h, R), circle(cx, cy - R + h, R))
    ic.add(alm, lid, base=0.78, grad=0.4, bevel=0.7, line=True)
    ic.add(inter(circle(cx, cy, 5.2 * s), alm), iris, mode="sphere", base=0.6, sphere=(cx, cy, 5.2 * s, 5.2 * s), rim=False)
    ic.add(inter(circle(cx, cy, 2.3 * s), alm), "navy", base=0.15, bevel=0, cast=False, rim=False)
    ic.px(int(cx - 2.2 * s), int(cy - 2.2 * s), "#eefcf8")
    return alm


def heart(cx, cy, s):
    return union(circle(cx - 5 * s, cy - 3 * s, 5.6 * s), circle(cx + 5 * s, cy - 3 * s, 5.6 * s),
                 poly([(cx - 10.4 * s, cy - 1.2 * s), (cx + 10.4 * s, cy - 1.2 * s), (cx, cy + 11 * s)]))


def boot_shape(cx, cy, s):
    return union(rrect(cx - 7 * s, cy - 13 * s, cx + 3 * s, cy + 3 * s, 1.5 * s),
                 poly([(cx - 7 * s, cy + 1 * s), (cx + 2 * s, cy - 2 * s), (cx + 11 * s, cy + 2 * s), (cx + 13 * s, cy + 6 * s),
                       (cx + 13 * s, cy + 8 * s), (cx - 7 * s, cy + 8 * s)]))


def boot(ic, cx, cy, s, pal="leather", sole="wood", **kw):
    ic.add(boot_shape(cx, cy, s), pal, base=0.58, grad=0.5, **kw)
    ic.add(rect(cx - 7 * s, cy + 6 * s, cx + 13 * s, cy + 8.6 * s), sole, base=0.3, bevel=0)
    ic.add(rect(cx - 7.6 * s, cy - 13 * s, cx + 3.6 * s, cy - 10 * s), pal, base=0.75, bevel=0)


def paw(ic, cx, cy, s, pal):
    p = union(ellipse(cx, cy + 4 * s, 7.2 * s, 5.6 * s), circle(cx - 9 * s, cy - 4.5 * s, 3.2 * s), circle(cx - 3.2 * s, cy - 9.6 * s, 3.3 * s),
              circle(cx + 3.2 * s, cy - 9.6 * s, 3.3 * s), circle(cx + 9 * s, cy - 4.5 * s, 3.2 * s))
    ic.add(p, pal, base=0.58, grad=0.6, bevel=0.9, line=True)


def lines(ic, segs, cat, r=1.5, base=0.7):
    for (x0, y0, x1, y1) in segs:
        ic.add(capsule(x0, y0, x1, y1, r), acc(cat), base=base, grad=0.4, bevel=0, cast=False)


def arc(ic, cx, cy, R, a0, a1, w, cat, base=0.7, steps=14):
    """a thick arc (accent) from angle a0 to a1 (degrees, 0 = right, 90 = down)"""
    pts_o, pts_i = [], []
    for k in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * k / steps)
        pts_o.append((cx + (R + w / 2) * math.cos(a), cy + (R + w / 2) * math.sin(a)))
        pts_i.append((cx + (R - w / 2) * math.cos(a), cy + (R - w / 2) * math.sin(a)))
    ic.add(poly(pts_o + pts_i[::-1]), acc(cat), base=base, grad=0.3, bevel=0, cast=False)


def plus(ic, cx, cy, s, cat, line=True):
    ic.add(union(rect(cx - 1.9 * s, cy - 6 * s, cx + 1.9 * s, cy + 6 * s), rect(cx - 6 * s, cy - 1.9 * s, cx + 6 * s, cy + 1.9 * s)), acc(cat),
           base=0.72, grad=0.5, bevel=0.8, line=line)


def arrow(ic, cx, cy, s, cat, ang=-90.0, line=True):
    """a fat arrow pointing at ang (degrees; -90 = up), centred on (cx, cy)"""
    pts = [(-7, 2.6), (1, 2.6), (1, 7), (9, 0), (1, -7), (1, -2.6), (-7, -2.6)]
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ic.add(poly([(cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s) for x, y in pts]), acc(cat), base=0.72, grad=0.5, bevel=0.8, line=line)


def burst(ic, cx, cy, R, r, n, pal, rot=-90.0, base=0.75, line=False):
    ic.add(poly(star_pts(cx, cy, R, r, n, rot)), pal, base=base, grad=0.4, bevel=0.6, line=line)


def spark(ic, x, y, cat, size=2):
    ic.sparkle(x, y, size, PALN[acc(cat)][6], PALN[acc(cat)][4])


def bat(ic, cx, cy, s, pal="bat", line=True, base=0.55):
    wl = [(cx - 3 * s, cy - 2 * s), (cx - 10 * s, cy - 7 * s), (cx - 17 * s, cy - 4 * s), (cx - 15 * s, cy + 1 * s), (cx - 12 * s, cy - 0.5 * s),
          (cx - 10 * s, cy + 3.5 * s), (cx - 7 * s, cy + 1 * s), (cx - 3 * s, cy + 4 * s)]
    wing_l = poly(wl)
    wing_r = poly([(2 * cx - x, y) for x, y in wl])
    body = union(ellipse(cx, cy + 1 * s, 4 * s, 5.5 * s), poly([(cx - 3.6 * s, cy - 3 * s), (cx - 2.4 * s, cy - 7.5 * s), (cx - 0.8 * s, cy - 3.5 * s)]),
                 poly([(cx + 3.6 * s, cy - 3 * s), (cx + 2.4 * s, cy - 7.5 * s), (cx + 0.8 * s, cy - 3.5 * s)]))
    ic.add(union(wing_l, wing_r, body), pal, base=base, grad=0.6, bevel=0.8, line=line)
    ic.px(int(cx - 1.6 * s), int(cy - 0.5 * s), "#ff7a7a"); ic.px(int(cx + 1.6 * s), int(cy - 0.5 * s), "#ff7a7a")


def stone_wall(ic, x0, y0, x1, y1):
    ic.add(rect(x0, y0, x1, y1), "stone", base=0.42, grad=0.5,
           pattern=lambda x, y: -0.16 if (int(y - y0) % 7 == 0 or int(x - x0 + (3.5 if int((y - y0) // 7) % 2 else 0)) % 11 == 0) else 0)


def shield(ic, cx, cy, s, pal="steel", line=True):
    sh = union(rrect(cx - 9 * s, cy - 10 * s, cx + 9 * s, cy + 1 * s, 2 * s), poly([(cx - 9 * s, cy), (cx + 9 * s, cy), (cx, cy + 12 * s)]))
    ic.add(sh, pal, base=0.6, grad=0.6, bevel=1.0, line=line)
    return sh


def sack(ic, cx, cy, s, pal="leather"):
    body = union(ellipse(cx, cy + 4 * s, 13 * s, 11 * s), poly([(cx - 6 * s, cy - 5 * s), (cx + 6 * s, cy - 5 * s), (cx + 9 * s, cy + 2 * s),
                                                                (cx - 9 * s, cy + 2 * s)]))
    ic.add(body, pal, base=0.55, grad=0.6, bevel=1.0, line=True, pattern=lambda x, y: 0.05 * math.sin(x * 0.8))
    ic.add(rrect(cx - 7 * s, cy - 7.5 * s, cx + 7 * s, cy - 4 * s, 1.5 * s), "gold", base=0.6, grad=0.5, line=True)


def mountain_shape(cx, by, s):
    return poly([(cx - 28 * s, by), (cx - 15 * s, by - 20 * s), (cx - 9 * s, by - 15 * s), (cx + 1 * s, by - 30 * s), (cx + 12 * s, by - 16 * s),
                 (cx + 17 * s, by - 21 * s), (cx + 28 * s, by)])


def charge_sticks(ic, cx, cy, s):
    for k, dx in enumerate((-6.5, 0.0, 6.5)):
        ic.add(rrect(cx + (dx - 3.2) * s, cy - 10 * s, cx + (dx + 3.2) * s, cy + 11 * s, 1.4 * s), "red", mode="cyl", axis=(0, 1),
               base=0.6 - 0.05 * k)
    ic.add(rect(cx - 10.2 * s, cy - 3 * s, cx + 10.2 * s, cy + 1 * s), "wood", base=0.45, grad=0.4, bevel=0.6, line=True)
    ic.add(capsule(cx, cy - 10 * s, cx + 4 * s, cy - 15 * s, 0.9 * s), "cream", base=0.4, bevel=0, cast=False)


def ring_item(ic, cx, cy, s, gem_pal="emerald"):
    ic.add(ering(cx, cy, 9 * s, 9 * s, 6 * s, 6 * s), "gold", mode="torus", torus=(cx, cy, 9 * s, 9 * s, 6 * s, 6 * s), bevel=0, line=True)
    gem(ic, cx, cy - 10 * s, 0.42 * s, gem_pal, line=True)


def hammer(ic, hx0, hy0, cx, cy, s=1.0, head="steel"):
    ux, uy = unit(hx0, hy0, cx, cy); px, py = -uy, ux
    ic.add(capsule(hx0, hy0, cx, cy, 2.3 * s), "wood", mode="cyl", axis=(ux, uy), base=0.58)
    w, h = 10.0 * s, 5.5 * s
    pts = [(cx + px * w + ux * h, cy + py * w + uy * h), (cx - px * w + ux * h, cy - py * w + uy * h),
           (cx - px * w - ux * h, cy - py * w - uy * h), (cx + px * w - ux * h, cy + py * w - uy * h)]
    ic.add(poly(pts), head, base=0.6, grad=0.6, bevel=1.1, line=True)


# ====================================================================== MINING (44 nodes: 3 branches; key "Mining.b<branch>.<id>")
def m_prospectors_eye():
    ic = Icon("ProspectorsEye")
    stone_wall(ic, 6, 30, 58, 58)
    for (x, y, r) in ((17, 44, 3.6), (40, 50, 3.0), (49, 38, 2.4)):
        ic.add(circle(x, y, r), "ore", mode="sphere", base=0.72, line=True)
    eye(ic, 32, 20, 2.2)
    lines(ic, [(10, 8, 15, 12), (54, 8, 49, 12), (32, 1.5, 32, 5)], "ability", 1.4)
    spark(ic, 17, 44, "ability", 2); spark(ic, 49, 37, "ability", 1)
    return ic


def m_quick_swing():
    ic = Icon("QuickSwing")
    arc(ic, 42, 46, 34, 205, 262, 3.0, "speed")
    arc(ic, 42, 46, 26, 210, 258, 2.6, "speed", base=0.55)
    lines(ic, [(4, 34, 12, 34), (6, 42, 13, 41)], "speed", 1.4)
    pick(ic, 52, 56, 34, 22, arm=17)
    return ic


def m_rich_seams():
    ic = Icon("RichSeams")
    ore_chunk(ic, 28, 38, 1.55, line=True)
    plus(ic, 50, 14, 1.25, "yield")
    spark(ic, 14, 16, "yield", 2); spark(ic, 52, 34, "yield", 1)
    return ic


def ore_cube(ic, x0, y0, d, ore="ore"):
    obox(ic, x0, y0, x0 + d, y0 + d, d * 0.55, "stone", base=0.5)
    ic.add(circle(x0 + d * 0.45, y0 + d * 0.5, d * 0.24), ore, mode="sphere", base=0.7, line=True)


def m_vein_burst():
    ic = Icon("VeinBurst")
    burst(ic, 32, 33, 29, 10, 8, acc("ability"), rot=-67.5, base=0.62)
    burst(ic, 32, 33, 17, 7, 8, acc("ability"), base=0.9)
    ore_cube(ic, 8, 8, 13); ore_cube(ic, 42, 6, 12); ore_cube(ic, 9, 42, 11); ore_cube(ic, 41, 41, 13)
    return ic


def m_wide_burst():
    ic = Icon("WideBurst")
    ic.add(ering(32, 32, 24, 24, 20.5, 20.5), acc("ability"), base=0.6, bevel=0, line=True)
    ore_cube(ic, 22, 23, 15)
    for a in (-45, 45, 135, 225):
        r = 22.5
        arrow(ic, 32 + r * math.cos(math.radians(a)), 32 + r * math.sin(math.radians(a)), 0.9, "ability", ang=a)
    return ic


def m_burst_recovery():
    ic = Icon("BurstReach")
    burst(ic, 24, 38, 22, 8, 8, acc("ability"), rot=-67.5, base=0.62)
    burst(ic, 24, 38, 12, 5, 8, acc("ability"), base=0.92)
    ore_cube(ic, 36, 10, 17)
    plus(ic, 52, 47, 1.05, "ability")
    return ic


def m_chain_fortune():
    ic = Icon("ChainFortune")
    for (x, y, rot) in ((14, 46, -40), (25, 36, 50), (36, 26, -40)):
        ic.add(diff(rot_ellipse(x, y, 9.5, 5.6, rot), rot_ellipse(x, y, 6.2, 2.5, rot)), "steel", base=0.6, grad=0.5, bevel=0.9, line=True)
    ic.add(circle(46, 20, 12), acc("xp"), mode="sphere", base=0.62, line=True)
    ic.add(poly(star_pts(46, 20.5, 7, 3, 4)), acc("xp"), base=0.95, bevel=0, cast=False)
    arrow(ic, 50, 47, 1.05, "xp")
    return ic


def m_gem_eye():
    ic = Icon("GemEye")
    gem(ic, 36, 30, 1.8, "ruby", line=True)
    eye(ic, 17, 50, 1.1, iris="emerald")
    spark(ic, 55, 10, "yield", 2); spark(ic, 12, 22, "yield", 1)
    plus(ic, 54, 49, 0.9, "yield")
    return ic


def m_smelters_touch():
    ic = Icon("SmeltersTouch")
    flame(ic, 32, 42, 1.65)
    ingot(ic, 32, 25, 1.45, "steel")
    spark(ic, 53, 10, "yield", 2); spark(ic, 11, 13, "yield", 1)
    return ic


def m_steady_pick():
    ic = Icon("SteadyPick")
    pick(ic, 28, 48, 32, 15, arm=17)
    wave = [(4, 53), (16, 53), (20, 46), (25, 60), (30, 50), (34, 53), (60, 53)]
    for k in range(len(wave) - 1):
        lines(ic, [(wave[k][0], wave[k][1], wave[k + 1][0], wave[k + 1][1])], "speed", 1.6)
    return ic


def m_motherlode():
    ic = Icon("Motherlode")
    burst(ic, 32, 38, 30, 12, 12, "gold", rot=-90, base=0.62)
    gem(ic, 16, 36, 1.05, "emerald", line=True)
    gem(ic, 48, 36, 1.05, "ruby", line=True)
    gem(ic, 32, 30, 1.35, "diamond", line=True)
    spark(ic, 8, 10, "yield", 2); spark(ic, 56, 12, "yield", 2); spark(ic, 32, 58, "yield", 1)
    return ic


def m_vein_sense():
    ic = Icon("VeinSense")
    for R, b in ((27, 0.55), (21, 0.72)):
        arc(ic, 32, 30, R, 150, 210, 2.8, "ability", base=b)
        arc(ic, 32, 30, R, -30, 30, 2.8, "ability", base=b)
    eye(ic, 32, 30, 1.4)
    ore_cube(ic, 25, 45, 12)
    return ic


def m_seismic_pulse():
    ic = Icon("SeismicPulse")
    ic.add(rect(3, 44, 61, 58), "stone", base=0.48, grad=0.5, pattern=hstripes(4, 0.06))
    ic.add(poly([(30, 44), (35, 44), (33, 49), (37, 53), (31, 58), (32, 52), (28, 49)]), "navy", base=0.15, bevel=0, cast=False, rim=False)
    for R, b in ((26, 0.5), (18, 0.65), (10, 0.85)):
        arc(ic, 32, 44, R, 195, 345, 2.8, "ability", base=b)
    burst(ic, 12, 14, 7, 3, 5, "gold", base=0.8, line=True)
    burst(ic, 52, 12, 6, 2.6, 5, "gold", base=0.8, line=True)
    return ic


def m_overclock():
    ic = Icon("Overclock")
    ic.add(gear(30, 34, 24, 18, 10, hole=0, tooth=0.5), "steel", base=0.55, grad=0.6, bevel=1.0, line=True)
    ic.add(circle(30, 34, 11.5), "steel", base=0.32, bevel=0, cast=False)
    arrow(ic, 30, 34, 1.35, "xp")
    spark(ic, 56, 8, "xp", 2); spark(ic, 57, 26, "xp", 1)
    return ic


def m_bottomless_pockets():
    ic = Icon("BottomlessPockets")
    sack(ic, 30, 38, 1.5)
    ore_chunk(ic, 22, 12, 0.6)
    ore_chunk(ic, 40, 9, 0.5)
    plus(ic, 53, 50, 1.0, "yield")
    return ic


def m_heart_of_the_mountain():
    ic = Icon("HeartOfTheMountain")
    ic.add(mountain_shape(32, 60, 1.05), "stone", base=0.5, grad=0.6, pattern=hstripes(5, 0.07, 2), line=True)
    ic.add(poly([(33, 28.5), (28, 34), (37.5, 34)]), "cream", base=0.85, bevel=0)                         # snow cap
    ic.add(circle(32, 46, 10.5), acc("ability"), mode="sphere", base=0.45, rim=False, bevel=0)               # glow
    ic.add(heart(32, 46, 0.72), "ore", base=0.7, grad=0.6, bevel=0.8, line=True)
    spark(ic, 10, 14, "ability", 2); spark(ic, 55, 18, "ability", 1)
    return ic


def m_tool_mastery():
    ic = Icon("ToolMastery")
    for k, (pal, x, h) in enumerate((("copper", 4, 10), ("steel", 22, 17), ("gold", 40, 24))):
        ic.add(rect(x, 60 - h, x + 18, 60), pal, base=0.5 + 0.05 * k, grad=0.5, line=True)
        ic.add(rect(x, 60 - h, x + 18, 60 - h + 2.5), pal, base=0.85, bevel=0)
    pick(ic, 36, 32, 46, 13, arm=11, hr=2.7, r=2.0, head="gold")
    lines(ic, [(4, 22, 18, 22), (8, 30, 22, 30), (6, 14, 16, 14)], "speed", 1.5)
    return ic


def m_durable_grip():
    ic = Icon("DurableGrip")
    ic.add(capsule(10, 56, 44, 14, 5.0), "wood", mode="cyl", axis=(0.63, -0.78), base=0.58)
    for t in (0.28, 0.42, 0.56, 0.7):
        x, y = 10 + (44 - 10) * t, 56 + (14 - 56) * t
        ic.add(rot_ellipse(x, y, 6.6, 2.4, 50), "leather", base=0.62, grad=0.4, bevel=0.6, line=True)
    shield(ic, 47, 42, 1.0, pal=acc("tool"))
    ic.add(capsule(43, 39, 46, 43, 1.1), "steel", base=0.3, bevel=0, cast=False)
    ic.add(capsule(46, 43, 52, 35, 1.1), "steel", base=0.3, bevel=0, cast=False)
    return ic


def m_stoneskin():
    ic = Icon("Stoneskin")
    ic.add(rect(6, 52, 58, 60), "stone", base=0.45, grad=0.4)
    boot(ic, 28, 41, 1.45, pal="stone", sole="stone", line=True)
    for (x, y) in ((22, 26), (30, 32), (23, 38)):
        ic.add(rect(x - 3, y - 2.5, x + 3, y + 2.5), "stone", base=0.75, bevel=0.6)
    lines(ic, [(48, 6, 48, 18), (55, 10, 55, 22), (41, 3, 41, 12)], "health", 1.6)
    lines(ic, [(6, 50, 12, 46), (58, 50, 52, 46)], "health", 1.3)
    return ic


def m_rockhide():
    ic = Icon("Rockhide")
    h = heart(32, 31, 2.25)
    ic.add(h, acc("health"), base=0.58, grad=0.6, bevel=1.1, line=True)
    ic.add(inter(h, Shape(lambda x, y: x + y * 0.4 > 44 and int((x * 0.7 + y) // 9) % 2 == 0, h.bb)), "stone", base=0.6, grad=0.5, bevel=0.7)
    ic.add(inter(h, Shape(lambda x, y: x + y * 0.4 > 44 and int((x * 0.7 + y) // 9) % 2 == 1, h.bb)), "stone", base=0.45, grad=0.5, bevel=0.7)
    spark(ic, 16, 18, "health", 1)
    return ic


def m_echo_step():
    ic = Icon("EchoStep")
    for k, dx in enumerate((-22, -11)):
        ic.add(boot_shape(40 + dx, 38, 1.3), acc("speed"), base=0.3 + 0.25 * k, bevel=0, cast=False, line=True)
    boot(ic, 40, 38, 1.3, line=True)
    lines(ic, [(2, 50, 10, 50)], "speed", 1.4)
    return ic


def m_gear_resonance():
    ic = Icon("GearResonance")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 38, R, 200, 340, 2.6, "speed", base=b)
    dome = union(inter(ellipse(32, 40, 19, 19), rect(0, 0, 64, 40)), rect(13, 38, 51, 43))
    ic.add(dome, "copper", base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(9, 42, 55, 47), "copper", base=0.42, grad=0.4, line=True)                                   # brim
    ic.add(rrect(26, 27, 38, 37, 2.5), "steel", base=0.5, line=True)
    ic.add(circle(32, 32, 4), "lamp", mode="sphere", base=0.85)
    lines(ic, [(32, 50, 32, 60), (22, 50, 18, 58), (42, 50, 46, 58)], "speed", 1.4)
    return ic


def m_quick_repair():
    ic = Icon("QuickRepair")
    pick(ic, 12, 56, 26, 38, arm=13, hr=3.0, r=2.2)
    hammer(ic, 54, 50, 40, 22, 1.0)
    burst(ic, 31, 30, 8, 3, 4, acc("tool"), base=0.85, line=True)
    arc(ic, 32, 32, 27, 200, 300, 2.6, "tool")
    arrow(ic, 50.5, 9.5, 0.65, "tool", ang=-15)
    return ic


def m_emergency_pick():
    ic = Icon("EmergencyPick")
    pick(ic, 40, 58, 30, 22, arm=17)
    ic.add(poly([(20, 18), (24, 22), (21, 24), (25, 28), (23, 29), (19, 25), (22, 23)]), "navy", base=0.2, bevel=0, cast=False, rim=False)
    lines(ic, [(4, 40, 16, 40), (6, 48, 18, 48), (8, 56, 20, 56)], "speed", 1.5)
    ic.add(circle(52, 14, 9), acc("health"), mode="sphere", base=0.6, line=True)
    ic.add(rrect(50.4, 7.5, 53.6, 16.5, 1.2), "cream", base=0.85, bevel=0, cast=False)
    ic.add(circle(52, 19.5, 1.7), "cream", base=0.85, bevel=0, cast=False)
    return ic


def m_trinket_seams():
    ic = Icon("TrinketSeams")
    ore_chunk(ic, 24, 42, 1.25, line=True)
    ring_item(ic, 44, 22, 1.25)
    plus(ic, 53, 50, 0.95, "yield")
    spark(ic, 9, 12, "yield", 1)
    return ic


def m_hardened_edge():
    ic = Icon("HardenedEdge")
    ic.add(capsule(6, 58, 26, 34, 2.6), "wood", mode="cyl", axis=(0.64, -0.77), base=0.58)
    blade = poly([(18, 30), (30, 26), (46, 18), (60, 6), (50, 24), (36, 36), (26, 42)])
    ic.add(blade, "steel", base=0.62, grad=0.6, bevel=1.1, line=True)
    ic.add(poly([(46, 18), (60, 6), (55, 15), (44, 22)]), "steel", base=0.98, bevel=0, cast=False)
    for R, b in ((22, 0.62), (16, 0.8)):
        arc(ic, 44, 38, R, 20, 110, 2.6, "damage", base=b)
    spark(ic, 58, 5, "damage", 2)
    return ic


def m_tool_tempering():
    ic = Icon("ToolTempering")
    for (x, y, r) in ((14, 14, 6), (22, 9, 5), (9, 7, 4)):
        ic.add(circle(x, y, r), "cloud", mode="sphere", base=0.7)
    pick(ic, 18, 56, 36, 30, arm=17, head="flame")
    arrow(ic, 50, 46, 1.0, "tool")
    return ic


def m_lucky_strike():
    ic = Icon("LuckyStrike")
    pick(ic, 52, 58, 40, 24, arm=14, hr=2.8, r=2.1)
    for (dx, dy) in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
        ic.add(circle(22 + dx, 30 + dy, 7), "green", mode="sphere", base=0.6, line=True)
    ic.add(capsule(22, 32, 16, 52, 1.6), "green", base=0.45, bevel=0)
    ic.add(circle(22, 30, 2.6), "green", base=0.85, bevel=0, cast=False)
    spark(ic, 56, 8, "tool", 2)
    arc(ic, 40, 24, 19, -70, 20, 2.4, "tool")
    return ic


def m_blast_hammer():
    ic = Icon("BlastHammer")
    burst(ic, 40, 22, 22, 9, 8, acc("ability"), rot=-67.5, base=0.62)
    hammer(ic, 10, 58, 36, 26, 1.35)
    ore_cube(ic, 46, 44, 11); ore_cube(ic, 4, 4, 9)
    return ic


def m_masterwork_pick():
    ic = Icon("MasterworkPick")
    pick(ic, 12, 58, 36, 26, arm=20, bend=6, hr=3.8, r=2.8, head="gold")
    gem(ic, 36, 26, 0.5, "diamond", line=True)
    burst(ic, 52, 46, 9, 3.4, 4, "gold", base=0.9, line=True)
    spark(ic, 10, 10, "tool", 2); spark(ic, 56, 6, "tool", 1)
    return ic


def m_cave_sense():
    ic = Icon("CaveSense")
    bat(ic, 32, 18, 1.55)
    sack(ic, 32, 44, 0.95, pal="leather")
    coin(ic, 47, 52, 6)
    plus(ic, 13, 49, 0.95, "yield")
    return ic


def m_lantern_lore():
    ic = Icon("LanternLore")
    for a in range(0, 360, 45):
        x0, y0 = 32 + 17 * math.cos(math.radians(a)), 35 + 17 * math.sin(math.radians(a))
        x1, y1 = 32 + 27 * math.cos(math.radians(a)), 35 + 27 * math.sin(math.radians(a))
        lines(ic, [(x0, y0, x1, y1)], "ability", 1.7)
    ic.add(ering(32, 10, 5, 5, 2.8, 2.8), "steel", base=0.55, bevel=0, line=True)
    ic.add(rrect(22, 14, 42, 19, 1.5), "steel", base=0.6, grad=0.5, line=True)
    ic.add(rect(24, 19, 40, 46), "lamp", mode="cyl", axis=(0, 1), base=0.75)
    flame(ic, 32, 34, 0.7)
    for x in (24, 32, 40):
        ic.add(rect(x - 1.2, 19, x + 1.2, 46), "steel", base=0.45, bevel=0)
    ic.add(rrect(21, 45, 43, 50, 1.5), "steel", base=0.5, grad=0.5, line=True)
    return ic


def m_depth_charge():
    ic = Icon("DepthCharge")
    burst(ic, 46, 12, 11, 4.5, 8, "flame", base=0.75)
    charge_sticks(ic, 28, 38, 1.4)
    spark(ic, 47, 12, "ability", 2)
    return ic


def m_bigger_bang():
    ic = Icon("BiggerBang")
    burst(ic, 32, 32, 21, 10, 10, "flame", base=0.6, line=True)
    burst(ic, 32, 32, 12, 6, 10, "flame", base=0.92, rot=-72)
    for a in (-45, 45, 135, 225):
        r = 24
        arrow(ic, 32 + r * math.cos(math.radians(a)), 32 + r * math.sin(math.radians(a)), 0.82, "ability", ang=a)
    return ic


def m_safe_fuse():
    ic = Icon("SafeFuse")
    charge_sticks(ic, 22, 30, 1.05)
    burst(ic, 27, 12, 5, 2, 6, "flame", base=0.85)
    sh = shield(ic, 42, 40, 1.35)
    ic.add(heart(42, 37, 0.62), acc("health"), base=0.62, grad=0.5, bevel=0.6)
    return ic


def m_pet_digger():
    ic = Icon("PetDigger")
    pick(ic, 54, 58, 44, 22, arm=12, hr=2.8, r=2.0)
    paw(ic, 24, 36, 1.55, acc("pet"))
    ore_chunk(ic, 48, 52, 0.42)
    plus(ic, 12, 10, 0.85, "pet")
    return ic


def m_deep_bounty():
    ic = Icon("DeepBounty")
    ore_chunk(ic, 24, 26, 1.25, line=True)
    coin(ic, 43, 44, 13)
    spark(ic, 56, 16, "yield", 2); spark(ic, 10, 52, "yield", 1)
    return ic


def m_cave_stalker():
    ic = Icon("CaveStalker")
    stone_wall(ic, 6, 28, 58, 60)
    bat(ic, 32, 45, 1.45, pal=acc("ability"), base=0.6)
    eye(ic, 32, 15, 1.7)
    return ic


def m_miners_fortune():
    ic = Icon("MinersFortune")
    ore_chunk(ic, 26, 46, 1.1, line=True)
    gem(ic, 33, 21, 1.15, "emerald", line=True)
    plus(ic, 53, 13, 1.05, "yield")
    lines(ic, [(33, 39, 33, 44), (24, 36, 21, 40), (42, 36, 45, 40)], "yield", 1.2)
    return ic


def m_geode_cracker():
    ic = Icon("GeodeCracker")
    ic.add(circle(30, 36, 23), "stone", mode="sphere", base=0.55, line=True)
    inside = ellipse(30, 36, 16, 16)
    ic.add(inside, "amethyst", base=0.22, bevel=0, cast=False)
    for (x, y, a) in ((22, 30, -30), (30, 26, 0), (38, 31, 30), (25, 41, -60), (36, 42, 60), (30, 36, 0)):
        ic.add(inter(rot_ellipse(x, y, 3.0, 6.5, a), inside), "amethyst", base=0.75, grad=0.6, bevel=0.6)
    ic.add(poly([(30, 13), (34, 20), (29, 24), (33, 30), (27, 25), (31, 20)]), "navy", base=0.15, bevel=0, cast=False, rim=False)
    plus(ic, 54, 12, 1.0, "yield")
    return ic


def m_dust_sweep():
    ic = Icon("DustSweep")
    mag = diff(union(circle(20, 22, 15), rect(5, 22, 35, 42)), union(circle(20, 22, 6.5), rect(13.5, 22, 26.5, 43)))
    ic.add(mag, "red", base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(5, 34, 13.5, 43), "steel", base=0.7, grad=0.4, line=True)
    ic.add(rect(26.5, 34, 35, 43), "steel", base=0.7, grad=0.4, line=True)
    lines(ic, [(10, 47, 13, 54), (31, 47, 36, 53), (40, 36, 48, 38)], "yield", 1.4)
    ore_chunk(ic, 50, 52, 0.42); ore_chunk(ic, 22, 57, 0.32); ore_chunk(ic, 54, 28, 0.36)
    return ic


def m_pet_synergy():
    ic = Icon("PetSynergy")
    burst(ic, 32, 32, 30, 15, 8, "gold", rot=-67.5, base=0.62)
    paw(ic, 32, 35, 1.45, acc("pet"))
    spark(ic, 52, 10, "pet", 2); spark(ic, 10, 50, "pet", 1)
    arrow(ic, 52, 50, 0.9, "pet")
    return ic


def m_abyss_walker():
    ic = Icon("AbyssWalker")
    ic.add(ellipse(32, 54, 28, 8), "abyss", base=0.4, grad=0.6, bevel=0)
    ic.add(ellipse(32, 54, 18, 4.2), "abyss", base=0.12, bevel=0, cast=False)
    boot(ic, 34, 32, 1.45, line=True)
    lines(ic, [(2, 22, 14, 22), (4, 30, 16, 30), (6, 38, 18, 38)], "speed", 1.5)
    return ic


def m_core_tap():
    ic = Icon("CoreTap")
    ic.add(circle(32, 34, 21), "abyss", mode="sphere", base=0.45, line=True)
    ic.add(circle(32, 34, 13), acc("ability"), mode="sphere", base=0.75, line=True)
    ic.add(circle(28, 30, 4), acc("ability"), base=1.0, bevel=0, cast=False, rim=False)
    gem(ic, 9, 14, 0.5, "ruby", line=True); gem(ic, 55, 12, 0.5, "emerald", line=True); gem(ic, 55, 54, 0.45, "diamond", line=True)
    spark(ic, 9, 52, "ability", 2)
    return ic


# (node key "<Tree>.b<branch>.<id | r<row>.free>", file stem, category, draw fn, what the icon shows)
DRAW = {
 "Mining": [
  ("Mining.b1.r1.free", "B1R1Free", "ability", m_prospectors_eye, "a wide-open eye over a stone wall whose blue ore glints through"),
  ("Mining.b1.r1a", "B1R1a", "speed", m_quick_swing, "an iron pickaxe mid-swing with teal swoosh arcs + speed lines"),
  ("Mining.b1.r1b", "B1R1b", "yield", m_rich_seams, "a big ore chunk with blue ore spots + a green plus and sparkles (Mining Fortune)"),
  ("Mining.b1.r2.free", "B1R2Free", "ability", m_vein_burst, "four ore cubes flying apart from a blue 8-point burst"),
  ("Mining.b1.r2a", "B1R2a", "ability", m_wide_burst, "an ore cube in a blue ring with four arrows pushing outward (bigger vein)"),
  ("Mining.b1.r2b", "B1R2b", "ability", m_burst_recovery, "a blue burst + one more ore cube with a blue plus (Burst breaks 1 more ore)"),
  ("Mining.b1.r2c", "B1R2c", "xp", m_chain_fortune, "three steel chain links into a gold XP orb + a gold up arrow"),
  ("Mining.b1.r3a", "B1R3a", "yield", m_gem_eye, "a big cut ruby, a small green-eyed eye + a green plus (gem chance)"),
  ("Mining.b1.r3b", "B1R3b", "yield", m_smelters_touch, "an iron bar on a flame (auto-smelt), green sparkles"),
  ("Mining.b1.r3c", "B1R3c", "speed", m_steady_pick, "an upright pickaxe over a steady teal rhythm line"),
  ("Mining.b1.r4a", "B1R4a", "yield", m_motherlode, "three gems (emerald, diamond, ruby) bursting from a gold jackpot star (x3)"),
  ("Mining.b1.r4b", "B1R4b", "ability", m_vein_sense, "an eye with blue range arcs either side, an ore cube below (more range)"),
  ("Mining.b1.r5a", "B1R5a", "ability", m_seismic_pulse, "cracked ground sending blue shock arcs up, two gold stun stars"),
  ("Mining.b1.r5b", "B1R5b", "xp", m_overclock, "a steel cog with a gold up arrow in its hub, gold sparks (more XP)"),
  ("Mining.b1.r5c", "B1R5c", "yield", m_bottomless_pockets, "a gold-tied leather sack with ore chunks spilling on top + a green plus"),
  ("Mining.b1.r6", "B1R6", "ability", m_heart_of_the_mountain, "a snow-capped stone mountain with a glowing blue crystal heart (capstone)"),
  ("Mining.b2.r1a", "B2R1a", "speed", m_tool_mastery, "a gold pick on a copper / iron / gold podium (tool tiers) + speed lines"),
  ("Mining.b2.r1b", "B2R1b", "tool", m_durable_grip, "a leather-wrapped pick handle with a soft-white shield + tick (less wear)"),
  ("Mining.b2.r2.free", "B2R2Free", "health", m_stoneskin, "a stone-plated boot landing on stone, red fall lines (less fall damage)"),
  ("Mining.b2.r2a", "B2R2a", "health", m_rockhide, "a red heart half covered in stone plates (+ max Health)"),
  ("Mining.b2.r2b", "B2R2b", "speed", m_echo_step, "a leather boot with two teal after-images behind it (move speed)"),
  ("Mining.b2.r3a", "B2R3a", "speed", m_gear_resonance, "a copper miner's helmet with its lamp, teal resonance arcs (per armor piece)"),
  ("Mining.b2.r3b", "B2R3b", "tool", m_quick_repair, "a hammer striking a pickaxe head, white repair spark + a turn arrow"),
  ("Mining.b2.r3c", "B2R3c", "speed", m_emergency_pick, "a cracked pickaxe with a red warning badge (!) and teal speed lines"),
  ("Mining.b2.r4a", "B2R4a", "yield", m_trinket_seams, "a gold emerald ring over an ore chunk + a green plus (per accessory)"),
  ("Mining.b2.r4b", "B2R4b", "damage", m_hardened_edge, "a sharpened pick point with a white edge glint, orange slash arcs"),
  ("Mining.b2.r5a", "B2R5a", "tool", m_tool_tempering, "a glowing hot pickaxe head with steam puffs + a white up arrow (tool tier)"),
  ("Mining.b2.r5b", "B2R5b", "tool", m_lucky_strike, "a four-leaf clover beside a pickaxe, white refund arc + spark"),
  ("Mining.b2.r5c", "B2R5c", "ability", m_blast_hammer, "a heavy sledgehammer before a blue burst, ore cubes flying"),
  ("Mining.b2.r6", "B2R6", "tool", m_masterwork_pick, "an ornate gold pickaxe with a diamond set in its head (capstone)"),
  ("Mining.b3.r1a", "B3R1a", "yield", m_cave_sense, "a cave bat over a loot sack and a coin + a green plus (cave-mob loot)"),
  ("Mining.b3.r1b", "B3R1b", "ability", m_lantern_lore, "a miner's lantern with a flame inside and blue light rays all round"),
  ("Mining.b3.r2.free", "B3R2Free", "ability", m_depth_charge, "a bundle of three red charge sticks with a lit fuse spark"),
  ("Mining.b3.r2a", "B3R2a", "ability", m_bigger_bang, "a fiery explosion with four blue arrows pushing outward (bigger radius)"),
  ("Mining.b3.r2b", "B3R2b", "health", m_safe_fuse, "charge sticks behind a steel shield with a red heart (no self-damage)"),
  ("Mining.b3.r3a", "B3R3a", "pet", m_pet_digger, "a big tan paw print beside a pickaxe and an ore chunk + a tan plus"),
  ("Mining.b3.r3b", "B3R3b", "yield", m_deep_bounty, "an ore chunk with a big gold coin in front, green sparkles (ore pays coins)"),
  ("Mining.b3.r3c", "B3R3c", "ability", m_cave_stalker, "an eye above a stone wall with a glowing blue bat seen through it"),
  ("Mining.b3.r4a", "B3R4a", "yield", m_miners_fortune, "an emerald popping out of an ore chunk + a green plus (gem chance)"),
  ("Mining.b3.r4b", "B3R4b", "yield", m_geode_cracker, "a cracked stone geode full of purple crystals + a green plus"),
  ("Mining.b3.r4c", "B3R4c", "yield", m_dust_sweep, "a red magnet pulling ore bits in along green pull lines (pickup radius)"),
  ("Mining.b3.r5a", "B3R5a", "pet", m_pet_synergy, "a tan paw on a tan star burst + a tan up arrow (pet abilities stronger)"),
  ("Mining.b3.r5b", "B3R5b", "speed", m_abyss_walker, "a boot striding over a dark violet abyss, teal speed lines"),
  ("Mining.b3.r6", "B3R6", "ability", m_core_tap, "a glowing blue deep core in a dark shell, three gems flung out (capstone)"),
 ],
}


# ====================================================================== the node list (from the ONE data table)
def tree_nodes(name):
    """every node of a tree as the radial page shows it: [(key, branch name, row, kind 'free' | 'up' | 'cap', id, name, max, text)]"""
    t = V3D.tree(name)
    out = []
    for bn, b in enumerate(t["branches"]):
        for r in b["rows"]:
            if r.get("free"):
                out.append(("%s.b%d.r%d.free" % (name, bn + 1, r["r"]), b["name"], r["r"], "free", "r%d.free" % r["r"], r["free"]["name"], 0,
                            r["free"]["text"]))
            for u in r["ups"]:
                out.append(("%s.b%d.%s" % (name, bn + 1, u["id"]), b["name"], r["r"], "cap" if r.get("cap") else "up", u["id"], u["name"],
                            u["max"], u["text"]))
    return out


def counts():
    return [(t["name"], t["kind"], len(t["branches"]), len(tree_nodes(t["name"]))) for t in V3D.TREES]


def icon_id(tree, stem):
    return "%s%s_%s" % (ITEM_PREFIX, tree, stem)


def icon_rel(tree, stem):
    return "%s/%s.png" % (ICON_DIR_REL, icon_id(tree, stem))


def build_icons(tree):
    nodes = tree_nodes(tree)
    rows = DRAW.get(tree)
    if rows is None:
        raise SystemExit("no pictures for the %s tree yet - add DRAW[%r] (one row per node; --counts lists the sizes)" % (tree, tree))
    keys = [n[0] for n in nodes]
    have = [r[0] for r in rows]
    if sorted(keys) != sorted(have) or len(set(have)) != len(have):
        raise SystemExit("DRAW[%s] does not match tools/trees_v3_data.py: missing %s, extra %s" % (tree, sorted(set(keys) - set(have)),
                                                                                              sorted(set(have) - set(keys))))
    stems = [r[1] for r in rows]
    assert len(set(stems)) == len(stems), "a file stem twice"
    for r in rows:
        assert r[2] in CAT_HEX, r
    byk = dict((r[0], r) for r in rows)
    out = []
    for n in nodes:
        r = byk[n[0]]
        img = r[3]().render()
        out.append((n, r, img, png_bytes(img)))
    return out


# ====================================================================== preview helpers (sheet only)
def resample(img, n):
    """area-average a 64 px RGBA icon down to n px (alpha-weighted) - the client's scaled look, for the sheet"""
    N = len(img); f = N / float(n)
    out = P.new(n, n)
    for oy in range(n):
        y0, y1 = oy * f, (oy + 1) * f
        for ox in range(n):
            x0, x1 = ox * f, (ox + 1) * f
            r = g = b = a = wsum = 0.0
            for sy in range(int(y0), min(N, int(math.ceil(y1)))):
                wy = min(y1, sy + 1) - max(y0, sy)
                for sx in range(int(x0), min(N, int(math.ceil(x1)))):
                    w = wy * (min(x1, sx + 1) - max(x0, sx))
                    p = img[sy][sx]; pa = p[3] / 255.0 * w
                    r += p[0] * pa; g += p[1] * pa; b += p[2] * pa; a += pa; wsum += w
            if a > 0:
                out[oy][ox] = [r / a, g / a, b / a, 255.0 * a / wsum]
    return out


def disc(cv, cx, cy, r_in, r_out, col, ss=4):
    """an anti-aliased ring (r_in = 0: a disc) on the RGB canvas"""
    for y in range(int(cy - r_out - 1), int(cy + r_out + 2)):
        for x in range(int(cx - r_out - 1), int(cx + r_out + 2)):
            cov = 0
            for sy in range(ss):
                for sx in range(ss):
                    d = math.hypot(x + (sx + 0.5) / ss - cx, y + (sy + 0.5) / ss - cy)
                    if r_in <= d <= r_out:
                        cov += 1
            if cov and 0 <= x < cv.w and 0 <= y < cv.h:
                a = cov / float(ss * ss); i = (y * cv.w + x) * 3
                for k in range(3):
                    cv.b[i + k] = int(round(col[k] * a + cv.b[i + k] * (1 - a)))


DISC = hx("#101822"); RING = hx("#8fc8ff"); GOLDR = hx("#E8A93B"); LOCKR = hx("#4a535c")


def node_disc(cv, x, y, size, icon64, ring=RING):
    """a node as the radial page draws it: dark disc + ring (skyymap.node_picture geometry) + the icon at 18 / 32 of the disc"""
    k = size / 64.0; c = size / 2.0
    disc(cv, x + c, y + c, 0, 27 * k, DISC)
    disc(cv, x + c, y + c, 23 * k, 27.5 * k, ring)
    isz = int(round(size * 18.0 / 32.0))
    small = resample(icon64, isz)
    o = int(round(c - isz / 2.0))
    cv.blit(small, x + o, y + o, 1)


BG = (24, 26, 38); PANEL = (34, 37, 52); INK = (226, 228, 236); DIM = (150, 156, 176); GOLDT = hx("#e0b060")


def wrap(s, n):
    words, out, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur: out.append(cur)
    return out


def clean(s):
    s = s.replace("’", "'").replace("x3", "X3")
    return "".join(ch if (ch in P._F or ch.upper() in P._F) else " " for ch in s)


def build_sheet(tree, built):
    COLS, CW, CH = 4, 316, 236
    branches = []
    for n, r, img, data in built:
        if not branches or branches[-1][0] != n[1]:
            branches.append((n[1], []))
        branches[-1][1].append((n, r, img))
    W = 24 + COLS * CW + 8
    hb = sum(44 + ((len(items) + COLS - 1) // COLS) * CH + 14 for _, items in branches)
    strip_h = 60 + len(branches) * (32 + 12) + 30 + len(branches) * (48 + 12) + 40
    H = 150 + hb + strip_h + 40
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "SKYWYNN %s TREE - NODE ICONS - DRAFT V1" % tree.upper(), GOLDT, 4)
    cv.text(24, 60, "ONE 64 PX ICON PER NODE (%d). EACH CELL: 2X ICON, 1X ICON, THE NODE ON ITS DISC AT 100 %% + 150 %%." % len(built), DIM, 2)
    x = 24
    cv.text(24, 84, "ACCENT COLOUR = WHAT THE NODE BOOSTS:", DIM, 2)
    y = 108; x = 24
    for cid, lab, hexc, _why in CATS:
        cv.rect(x, y, x + 14, y + 14, hx(hexc)); x2 = cv.text(x + 20, y + 4, lab, INK, 1)
        x = x2 + 22
    y = 140
    for bname, items in branches:
        rows = (len(items) + COLS - 1) // COLS
        h = 44 + rows * CH
        cv.rect(16, y, W - 8, y + h, PANEL)
        cv.rect(16, y, W - 8, y + 3, RING)
        cv.text(28, y + 14, "BRANCH %s" % bname.upper(), RING, 2)
        for k, (n, r, img) in enumerate(items):
            cx = 28 + (k % COLS) * CW; cy = y + 44 + (k // COLS) * CH
            cv.checker(cx, cy, 136, 136, (52, 56, 74), (44, 48, 64))
            cv.blit(img, cx + 4, cy + 4, 2)
            cv.rect(cx + 144, cy, cx + 144 + 72, cy + 72, (16, 20, 30))
            cv.blit(img, cx + 148, cy + 4, 1)
            cv.rect(cx + 144, cy + 78, cx + 144 + 120, cy + 136, (16, 20, 30))
            node_disc(cv, cx + 150, cy + 91, 32, img)
            node_disc(cv, cx + 196, cy + 83, 48, img)
            cv.rect(cx + 272, cy, cx + 286, cy + 14, hx(CAT_HEX[r[2]]))
            tag = {"free": "FREE PERK", "cap": "CAPSTONE"}.get(n[3], "UPGRADE")
            cv.text(cx + 272, cy + 20, "R%d" % n[2], DIM, 1)
            nm = clean(n[5]).upper()
            cv.text(cx, cy + 144, nm[:25], INK, 2)
            cv.text(cx, cy + 164, "%s  %s  %s" % (n[0].split(".", 1)[1].upper(), tag, ("MAX %d" % n[6]) if n[6] else ""), DIM, 1)
            for li, ln in enumerate(wrap(clean(n[7]), 48)[:5]):
                cv.text(cx, cy + 178 + li * 10, ln.upper(), (200, 206, 220), 1)
        y += h + 14
    # ---- the strips: every node on its disc at real size (100 % = 32 px disc, 150 % = 48 px disc)
    cv.rect(16, y, W - 8, y + strip_h, (11, 14, 22))
    cv.text(28, y + 14, "AT REAL SIZE ON THE NODE DISC (TREE COLOUR RING = LEARNT) - 100 %", INK, 2)
    yy = y + 40
    for bname, items in branches:
        for k, (n, r, img) in enumerate(items):
            node_disc(cv, 28 + k * 38, yy, 32, img)
        yy += 44
    cv.text(28, yy + 6, "150 %", INK, 2)
    yy += 30
    for bname, items in branches:
        for k, (n, r, img) in enumerate(items):
            node_disc(cv, 28 + k * 54, yy, 48, img, ring=GOLDR if k % 3 == 1 else (LOCKR if k % 3 == 2 else RING))
        yy += 60
    return cv.png()


# ====================================================================== write
def write_all(tree):
    built = build_icons(tree)
    os.makedirs(os.path.join(OUT, ICON_DIR_REL), exist_ok=True)
    files, nodes = [], []
    for n, r, img, data in built:
        rel = icon_rel(tree, r[1])
        with open(os.path.join(OUT, rel), "wb") as fh:
            fh.write(data)
        files.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
        nodes.append({"key": n[0], "saved_key": "Skill." + n[0] if n[3] != "free" else "", "tree": tree, "branch": n[1], "row": n[2],
                      "kind": n[3], "id": n[4], "name": n[5], "max": n[6], "effect": n[7], "icon_id": icon_id(tree, r[1]),
                      "file": rel, "category": r[2], "accent": CAT_HEX[r[2]], "shows": r[4]})
    sheet = build_sheet(tree, built)
    sname = "sheet-%s.png" % tree.lower()
    for nm in (sname, "sheet.png"):
        with open(os.path.join(OUT, nm), "wb") as fh:
            fh.write(sheet)
    mpath = os.path.join(OUT, "manifest.json")
    man = {}
    if os.path.isfile(mpath):
        man = json.load(open(mpath, encoding="utf8"))
    man.update({
        "what": "SkyWynn skill-tree node icons (one 64 x 64 item icon per Skill Trees 3 node) - DRAFT v1, not wired in yet",
        "generator": "tools/art/make_tree_node_icons.py", "deterministic": True, "original_pixels": True,
        "icon_rules": {"size": [64, 64], "alpha": "hard (0 or 255)", "outline": "1 px #120e1c tinted toward the touching part",
                       "light": "top left", "no_pure_black_or_white": True, "shown_at": "18 px in a 32 px disc (100 %), 27 px at 150 %"},
        "categories": dict((c[0], {"label": c[1], "accent": c[2], "why": c[3]}) for c in CATS),
        "item_json": {"path": "Server/Item/Items/Utility/<icon_id>.json", "icon": "Icons/ItemsGenerated/<icon_id>.png",
                      "png_in_jar": "Common/Icons/ItemsGenerated/<icon_id>.png", "see": "README.md section 3"},
    })
    trees = man.get("trees", {})
    trees[tree] = {"count": len(nodes), "sheet": sname, "nodes": nodes, "files": files}
    man["trees"] = dict(sorted(trees.items()))
    man["node_counts"] = dict((t, {"kind": k, "branches": b, "nodes": c}) for t, k, b, c in counts())
    with open(mpath, "w", newline="\n") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    print("wrote %d %s node icons + %s + sheet.png + manifest.json to %s" % (len(nodes), tree, sname, OUT))


def main():
    a = sys.argv[1:]
    tree = a[a.index("--tree") + 1] if "--tree" in a else "Mining"
    if "--counts" in a:
        for t, k, b, c in counts():
            print("%-13s %-5s %d branches %3d nodes%s" % (t, k, b, c, "  (icons done)" if t in DRAW else ""))
        return
    if "--check" in a:
        one = [d for _, _, _, d in build_icons(tree)]
        two = [d for _, _, _, d in build_icons(tree)]
        assert one == two, "not deterministic"
        print("OK: %d %s icons, two builds byte-identical" % (len(one), tree))
        return
    write_all(tree)


if __name__ == "__main__":
    main()
