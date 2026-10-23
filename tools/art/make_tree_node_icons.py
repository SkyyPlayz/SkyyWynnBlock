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

Drawings: one module per tree, tools/art/node_icons/<tree>.py (ROWS; see "the per-tree drawings" below). The painter functions here are a
STABLE API - tools/art/make_class_node_icons.py (the 8 class trees, node_icons/class_<Class>.py) imports them: never rename or re-sign them.
Writes (--tree <Name> for one tree, --all for every skill tree that has a module):
  art/tree-node-icons/Common/Icons/ItemsGenerated/Skyy_NodeIcon_<Tree>_<B><R>[a|b|c|Free].png   64 x 64 RGBA, hard alpha, 1 px outline
  art/tree-node-icons/sheet-<tree>.png    review sheet: every icon 2x + 1x with its node name + effect; the 100 % / 150 % disc strips
  art/tree-node-icons/sheet.png           = the Mining sheet (approved by Skyy 2026-10-23: "i love it!")
  art/tree-node-icons/manifest.json       node key -> icon item id -> file (bytes, sha256), category, what the icon shows (all trees)

Run:   python tools/art/make_tree_node_icons.py [--tree Mining | --all]  (deterministic: two runs = same bytes)
       python tools/art/make_tree_node_icons.py --check [--all]          (build twice, compare, write nothing)
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
    "wheat":  ["#3e2a08", "#664610", "#946a18", "#c2942a", "#e2bc46", "#f4dc82", "#fdf2c2"],
    "bone":   ["#3a3226", "#5c5240", "#83775e", "#ab9f82", "#cdc4a8", "#e6dfc8", "#f6f2e4"],
    "poison": ["#14280a", "#244812", "#3a6e18", "#5a9a20", "#86c42e", "#b6e45a", "#e2f8a6"],
    "honey":  ["#3e1e04", "#6a3608", "#9a5410", "#cc7a1a", "#eca23a", "#f8c870", "#fde8b8"],
    # ---- the ACCENT ramps (CATS): their bright step (index 4) = the section 15 hex of that category
    "acc_yield":   ["#0c2a14", "#17502a", "#23783c", "#3aa456", "#7ee08a", "#b4f0b8", "#e2fbe0"],
    "acc_xp":      ["#3e2a08", "#6a4a10", "#9a7018", "#c89a30", "#e8c25a", "#f6e09a", "#fdf4d2"],
    "acc_speed":   ["#0e2a2c", "#1a4c50", "#2a7a7c", "#4caaa8", "#86d8d0", "#bdf0ea", "#e8fcf8"],
    "acc_health":  ["#3a0c10", "#6a1820", "#a02a30", "#d8484a", "#ff7a7a", "#ffb0a8", "#ffe0da"],
    "acc_damage":  ["#4a1606", "#7c2808", "#b84410", "#e8681c", "#ff9a3c", "#ffc884", "#ffeccc"],
    "acc_tool":    ["#1a222c", "#2e3a48", "#4a5a6c", "#7a8ca0", "#d6e4ee", "#e8f0f6", "#f6fafc"],
    "acc_pet":     ["#2e1608", "#52280e", "#7e4018", "#ac6430", "#d8a070", "#ecc8a0", "#f8ead6"],
    "acc_buff":    ["#24123a", "#3c2060", "#5a3488", "#7c4cb4", "#c8a0ff", "#dcc4ff", "#f0e6ff"],
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
    ("buff",    "BUFF / POTENCY",       "#c8a0ff", "the Acrobatics tree / Epic purple family = food + potion effect strength and duration"),
    ("ability", "ABILITY / SENSE",      "#8fc8ff", "the Mining tree colour (SkyyTrees TCOLOR) = actives, their range + cooldowns, senses"),
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


def ore_cube(ic, x0, y0, d, ore="ore"):
    obox(ic, x0, y0, x0 + d, y0 + d, d * 0.55, "stone", base=0.5)
    ic.add(circle(x0 + d * 0.45, y0 + d * 0.5, d * 0.24), ore, mode="sphere", base=0.7, line=True)


# ====================================================================== part library 2 (2026-10-23: the other skill trees). Names + signatures are
# STABLE - the class-tree runner tools/art/make_class_node_icons.py imports them too. Every part: (ic, position..., s = scale, palettes ...).
def crescent(cx, cy, R, a0, a1, th, steps=18):
    """a tapered crescent (scythe blade, claw): outer arc R from a0 to a1 (degrees), thickness th in the middle, 0 at the tips"""
    o, i = [], []
    for k in range(steps + 1):
        t = k / float(steps); a = math.radians(a0 + (a1 - a0) * t)
        o.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        ri = R - th * math.sin(math.pi * t) - 0.3
        i.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
    return poly(o + i[::-1])


def axe(ic, hx0, hy0, cx, cy, s=1.0, head="steel", handle="wood"):
    """a woodcutter's axe: handle from (hx0, hy0) to the head at (cx, cy); the blade sticks out to the handle's left"""
    ux, uy = unit(hx0, hy0, cx, cy); px, py = uy, -ux
    ic.add(capsule(hx0, hy0, cx + ux * 3 * s, cy + uy * 3 * s, 2.4 * s), handle, mode="cyl", axis=(ux, uy), base=0.58, pattern=hstripes(5, 0.05))
    P_ = lambda a, b: (cx + ux * a * s + px * b * s, cy + uy * a * s + py * b * s)
    blade = poly([P_(4, -2), P_(5, 5), P_(10, 13), P_(-10, 13), P_(-5, 5), P_(-4, -2), P_(-3, -5), P_(3, -5)])
    ic.add(blade, head, base=0.6, grad=0.6, bevel=1.1, line=True)
    ic.add(poly([P_(10, 13), P_(-10, 13), P_(-8, 10.5), P_(8, 10.5)]), head, base=0.98, bevel=0, cast=False)


def log(ic, cx, cy, s=1.0, pal="wood"):
    ic.add(rect(cx - 15 * s, cy - 7 * s, cx + 9 * s, cy + 7 * s), pal, mode="cyl", axis=(1, 0), base=0.5, pattern=hstripes(3 * s, 0.06))
    ic.add(ellipse(cx + 9 * s, cy, 4.5 * s, 7 * s), "cream", base=0.62, grad=0.4, bevel=0.6, line=True,
           pattern=lambda x, y: -0.14 if int(math.hypot((x - cx - 9 * s) * 1.55, y - cy) / (2.2 * s)) % 2 else 0)


def tree(ic, cx, by, s=1.0, leaves="green", trunk="wood"):
    ic.add(rect(cx - 3.2 * s, by - 18 * s, cx + 3.2 * s, by), trunk, mode="cyl", axis=(0, 1), base=0.5)
    ic.add(union(circle(cx, by - 27 * s, 11 * s), circle(cx - 9 * s, by - 19 * s, 8 * s), circle(cx + 9 * s, by - 19 * s, 8 * s)), leaves,
           base=0.55, grad=0.6, bevel=1.0, line=True, pattern=lambda x, y: 0.08 * math.sin(x * 0.9) * math.sin(y * 0.9))


def leaf(ic, cx, cy, s=1.0, ang=-45.0, pal="grass"):
    ic.add(rot_ellipse(cx, cy, 9 * s, 4.2 * s, ang), pal, base=0.6, grad=0.6, bevel=0.8, line=True)
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ic.add(capsule(cx - c * 7 * s, cy - sn * 7 * s, cx + c * 7 * s, cy + sn * 7 * s, 0.55 * s), pal, base=0.3, bevel=0, cast=False)


def sapling(ic, cx, by, s=1.0):
    ic.add(ellipse(cx, by, 12 * s, 4 * s), "soil", base=0.5, grad=0.4)
    ic.add(capsule(cx, by - 1 * s, cx, by - 16 * s, 1.3 * s), "green", base=0.5, bevel=0)
    leaf(ic, cx - 6 * s, by - 14 * s, 0.85 * s, -150); leaf(ic, cx + 6 * s, by - 18 * s, 0.85 * s, -30)


def mushroom(ic, cx, by, s=1.0, cap="red"):
    ic.add(rrect(cx - 3.5 * s, by - 13 * s, cx + 3.5 * s, by, 2 * s), "cream", base=0.6, grad=0.5, line=True)
    capsh = inter(ellipse(cx, by - 12 * s, 12 * s, 11 * s), rect(cx - 13 * s, by - 24 * s, cx + 13 * s, by - 11 * s))
    ic.add(capsh, cap, base=0.58, grad=0.6, bevel=1.0, line=True)
    for (x, y, r) in ((-5, -17, 2.0), (3, -20, 1.8), (6, -14, 1.5)):
        ic.add(circle(cx + x * s, by + y * s, r * s), "cream", base=0.85, bevel=0, cast=False)


def berries(ic, cx, cy, s=1.0, pal="red"):
    leaf(ic, cx + 2 * s, cy - 9 * s, 0.7 * s, -20)
    for (x, y) in ((-4, 0), (4, 0), (0, 6), (-7, 7), (7, 7)):
        ic.add(circle(cx + x * s, cy + y * s, 4.2 * s), pal, mode="sphere", base=0.6, line=True)


def wheat(ic, cx, by, s=1.0, lean=0.0):
    tx = cx + lean * s
    ic.add(capsule(cx, by, tx, by - 22 * s, 1.2 * s), "green", base=0.55, bevel=0)
    ic.add(rot_ellipse(tx, by - 26 * s, 3.8 * s, 9 * s, lean * 2), "wheat", base=0.62, grad=0.6, bevel=1.0, line=True,
           pattern=lambda x, y: -0.12 if int(y / s) % 3 == 0 else 0)


def scythe(ic, hx0, hy0, hx1, hy1, s=1.0, blade="steel"):
    """a harvester's scythe: the long handle (hx0, hy0) -> (hx1, hy1) and a crescent blade sweeping out from its top"""
    ux, uy = unit(hx0, hy0, hx1, hy1)
    ic.add(capsule(hx0, hy0, hx1, hy1, 2.0 * s), "wood", mode="cyl", axis=(ux, uy), base=0.58)
    a = math.degrees(math.atan2(uy, ux))
    ccx, ccy = hx1 - math.cos(math.radians(a + 90)) * 20 * s, hy1 - math.sin(math.radians(a + 90)) * 20 * s
    ic.add(crescent(ccx, ccy, 20 * s, a + 90, a + 185, 8 * s), blade, base=0.65, grad=0.6, bevel=1.0, line=True)
    gx, gy = hx0 + ux * 12 * s, hy0 + uy * 12 * s
    ic.add(capsule(gx - uy * 4 * s, gy + ux * 4 * s, gx + uy * 4 * s, gy - ux * 4 * s, 1.5 * s), "wood", base=0.4, bevel=0)


def hoe(ic, hx0, hy0, cx, cy, s=1.0, head="steel"):
    ux, uy = unit(hx0, hy0, cx, cy); px, py = -uy, ux
    ic.add(capsule(hx0, hy0, cx, cy, 2.1 * s), "wood", mode="cyl", axis=(ux, uy), base=0.58)
    ic.add(poly([(cx - px * 2 * s, cy - py * 2 * s), (cx + px * 11 * s - ux * 2 * s, cy + py * 11 * s - uy * 2 * s),
                 (cx + px * 12 * s + ux * 5 * s, cy + py * 12 * s + uy * 5 * s), (cx + px * 1 * s + ux * 3 * s, cy + py * 1 * s + uy * 3 * s)]),
           head, base=0.6, grad=0.6, bevel=1.0, line=True)


def seed(ic, cx, cy, s=1.0, pal="wheat", ang=-30.0):
    ic.add(rot_ellipse(cx, cy, 4.5 * s, 3 * s, ang), pal, base=0.6, grad=0.6, bevel=0.6, line=True)


def egg(ic, cx, cy, s=1.0, pal="cream"):
    ic.add(union(ellipse(cx, cy + 2 * s, 8 * s, 8.5 * s), ellipse(cx, cy - 2 * s, 6.6 * s, 9.5 * s)), pal, base=0.62, grad=0.6, bevel=1.0, line=True)


def bucket(ic, cx, cy, s=1.0, fill="cream", pal="steel"):
    ic.add(diff(ellipse(cx, cy - 9 * s, 11 * s, 9 * s), ellipse(cx, cy - 9 * s, 9.6 * s, 7.6 * s), rect(cx - 12 * s, cy - 9 * s, cx + 12 * s, cy + 1 * s)),
           pal, base=0.55, bevel=0, line=True)
    ic.add(poly([(cx - 10 * s, cy - 7 * s), (cx + 10 * s, cy - 7 * s), (cx + 7.5 * s, cy + 10 * s), (cx - 7.5 * s, cy + 10 * s)]), pal,
           mode="cyl", axis=(0, 1), base=0.55, line=True, pattern=lambda x, y: -0.12 if abs(y - cy - 2 * s) < 1.0 * s else 0)
    ic.add(ellipse(cx, cy - 7 * s, 10 * s, 2.8 * s), fill, base=0.82, grad=0.4, bevel=0)


def sheep(ic, cx, cy, s=1.0, wool="cream"):
    for x in (-7, 6):
        ic.add(rect(cx + x * s - 1.6 * s, cy + 6 * s, cx + x * s + 1.6 * s, cy + 13 * s), "stone", base=0.3, bevel=0)
    ic.add(union(*[circle(cx + x * s, cy + y * s, r * s) for x, y, r in ((-8, 0, 7), (0, -3, 8), (8, 0, 7), (-3, 4, 7), (5, 4, 7))]), wool,
           base=0.62, grad=0.6, bevel=1.0, line=True)
    ic.add(ellipse(cx + 14 * s, cy - 2 * s, 4.5 * s, 5.5 * s), "stone", base=0.35, grad=0.5, line=True)
    ic.px(int(cx + 15.5 * s), int(cy - 3 * s), "#e6dfc8")


def cow_head(ic, cx, cy, s=1.0):
    ic.add(rot_ellipse(cx - 11 * s, cy - 8 * s, 4 * s, 2 * s, -25), "cream", base=0.7, bevel=0)
    ic.add(rot_ellipse(cx + 11 * s, cy - 8 * s, 4 * s, 2 * s, 25), "cream", base=0.7, bevel=0)
    ic.add(rrect(cx - 9 * s, cy - 10 * s, cx + 9 * s, cy + 8 * s, 5 * s), "mahog", base=0.55, grad=0.6, bevel=1.0, line=True)
    ic.add(rrect(cx - 7 * s, cy + 2 * s, cx + 7 * s, cy + 11 * s, 4 * s), "cream", base=0.65, grad=0.4, line=True)
    for x in (-3, 3):
        ic.add(circle(cx + x * s, cy + 6.5 * s, 1.2 * s), "mahog", base=0.25, bevel=0, cast=False)
        ic.add(circle(cx + x * 1.6 * s, cy - 3 * s, 1.4 * s), "navy", base=0.1, bevel=0, cast=False)


def fish(ic, cx, cy, s=1.0, pal="water", flip=False):
    f = -1 if flip else 1
    body = union(ellipse(cx, cy, 13 * s, 7 * s), poly([(cx + f * 10 * s, cy), (cx + f * 19 * s, cy - 8 * s), (cx + f * 17 * s, cy),
                                                       (cx + f * 19 * s, cy + 8 * s)]))
    ic.add(body, pal, base=0.62, grad=0.6, bevel=1.1, line=True, pattern=lambda x, y: 0.12 if y > cy + 2 * s else 0)
    ic.add(poly([(cx - f * 3 * s, cy - 6.5 * s), (cx + f * 5 * s, cy - 10 * s), (cx + f * 5 * s, cy - 5 * s)]), pal, base=0.4, bevel=0)
    ic.add(circle(cx - f * 8 * s, cy - 1.5 * s, 1.6 * s), "navy", base=0.1, bevel=0, cast=False)


def hook(ic, cx, cy, s=1.0, pal="steel"):
    ic.add(capsule(cx + 5 * s, cy - 14 * s, cx + 5 * s, cy + 2 * s, 1.5 * s), pal, base=0.65, bevel=0, line=True)
    ic.add(inter(ering(cx, cy + 2 * s, 6.5 * s, 6.5 * s, 3.6 * s, 3.6 * s), rect(cx - 8 * s, cy + 2 * s, cx + 8 * s, cy + 10 * s)), pal,
           base=0.65, bevel=0, line=True)
    ic.add(poly([(cx - 6.5 * s, cy + 2.5 * s), (cx - 6.5 * s, cy - 4 * s), (cx - 2.5 * s, cy + 1 * s)]), pal, base=0.75, bevel=0, line=True)
    ic.add(ering(cx + 5 * s, cy - 16 * s, 2.6 * s, 2.6 * s, 1.2 * s, 1.2 * s), pal, base=0.6, bevel=0, line=True)


def rod(ic, x0, y0, x1, y1, s=1.0):
    ux, uy = unit(x0, y0, x1, y1)
    ic.add(capsule(x0, y0, x1, y1, 1.8 * s), "wood", mode="cyl", axis=(ux, uy), base=0.6)
    ic.add(circle(x0 + ux * 7 * s, y0 + uy * 7 * s, 3.2 * s), "steel", mode="sphere", base=0.55)


def bobber(ic, cx, cy, s=1.0):
    sp = (cx, cy, 6 * s, 6 * s)
    ic.add(inter(circle(cx, cy, 6 * s), rect(cx - 7 * s, cy - 7 * s, cx + 7 * s, cy)), "red", mode="sphere", base=0.62, sphere=sp, line=True)
    ic.add(inter(circle(cx, cy, 6 * s), rect(cx - 7 * s, cy, cx + 7 * s, cy + 7 * s)), "cream", mode="sphere", base=0.62, sphere=sp, line=True)
    ic.add(capsule(cx, cy - 6 * s, cx, cy - 10 * s, 0.9 * s), "stone", base=0.5, bevel=0)


def boat(ic, cx, cy, s=1.0):
    ic.add(poly([(cx - 22 * s, cy - 4 * s), (cx + 22 * s, cy - 4 * s), (cx + 15 * s, cy + 7 * s), (cx - 15 * s, cy + 7 * s)]), "wood", base=0.52,
           grad=0.6, line=True, pattern=hstripes(3.5 * s, 0.07))
    ic.add(rect(cx - 23 * s, cy - 6 * s, cx + 23 * s, cy - 3 * s), "wood", base=0.78, bevel=0, line=True)


def waves(ic, cx, cy, w, cat="ability", r=1.5, amp=2.5, n=3):
    """a wavy accent line centred on (cx, cy), w wide"""
    pts = [(cx - w / 2 + w * k / (n * 4.0), cy + amp * math.sin(math.pi * k / 2.0)) for k in range(n * 4 + 1)]
    for k in range(len(pts) - 1):
        lines(ic, [(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1])], cat, r)


def water(ic, x0, y0, x1, y1):
    ic.add(rect(x0, y0, x1, y1), "water", base=0.5, grad=0.5, pattern=lambda x, y: 0.12 if int((y - y0) + 1.5 * math.sin(x * 0.5)) % 5 == 0 else 0)


def chest(ic, cx, cy, s=1.0, pal="wood", trim="gold"):
    ic.add(rect(cx - 15 * s, cy - 3 * s, cx + 15 * s, cy + 12 * s), pal, base=0.5, grad=0.5, line=True, pattern=hstripes(4 * s, 0.06))
    ic.add(union(rect(cx - 15 * s, cy - 8 * s, cx + 15 * s, cy - 3 * s), ellipse(cx, cy - 8 * s, 15 * s, 5 * s)), pal, base=0.7, grad=0.5, line=True)
    for x in (-11, 11):
        ic.add(rect(cx + x * s - 2 * s, cy - 12 * s, cx + x * s + 2 * s, cy + 12 * s), trim, base=0.6, grad=0.4, bevel=0.6)
    ic.add(rrect(cx - 3.5 * s, cy - 5 * s, cx + 3.5 * s, cy + 2 * s, 1 * s), trim, base=0.72, grad=0.5, line=True)


def anvil(ic, cx, cy, s=1.0, pal="steel"):
    P_ = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    ic.add(poly(P_([(-26, -8), (-18, -10), (-12, -10), (22, -10), (23, -9), (23, -3), (16, -1), (11, 1), (9, 9), (16, 12), (18, 17), (-16, 17),
                    (-13, 12), (-6, 9), (-8, 1), (-13, -1), (-19, -4)])), pal, base=0.45, grad=0.6, line=True,
           pattern=lambda x, y: 0.26 if y < cy - 7 * s else 0)
    ic.add(rect(cx - 15 * s, cy + 15 * s, cx + 17 * s, cy + 17 * s), pal, base=0.22, bevel=0)


def flask(ic, cx, cy, s=1.0, liquid="red", glass="glass"):
    """a round potion flask: bulb centre (cx, cy)"""
    ic.add(union(circle(cx, cy, 11 * s), rect(cx - 3.6 * s, cy - 18 * s, cx + 3.6 * s, cy - 6 * s)), glass, base=0.55, grad=0.5, line=True)
    ic.add(inter(circle(cx, cy, 9.5 * s), rect(cx - 12 * s, cy - 3 * s, cx + 12 * s, cy + 12 * s)), liquid, mode="sphere", base=0.6,
           sphere=(cx, cy, 9.5 * s, 9.5 * s), rim=False)
    ic.add(rrect(cx - 4.4 * s, cy - 22 * s, cx + 4.4 * s, cy - 17 * s, 1.2 * s), "wood", base=0.55, grad=0.4, line=True)
    ic.add(rot_ellipse(cx - 5 * s, cy - 4 * s, 1.4 * s, 3.2 * s, 30), "glass", base=1.0, bevel=0, cast=False, rim=False)


def vial(ic, cx, cy, s=1.0, liquid="green", glass="glass"):
    ic.add(rrect(cx - 5 * s, cy - 14 * s, cx + 5 * s, cy + 14 * s, 4.5 * s), glass, base=0.55, grad=0.5, line=True)
    ic.add(rrect(cx - 3.8 * s, cy - 2 * s, cx + 3.8 * s, cy + 12.8 * s, 3.5 * s), liquid, mode="cyl", axis=(0, 1), base=0.62, rim=False)
    ic.add(rrect(cx - 5.8 * s, cy - 18 * s, cx + 5.8 * s, cy - 13 * s, 1.2 * s), "wood", base=0.55, grad=0.4, line=True)


def cauldron(ic, cx, cy, s=1.0, liquid="green"):
    for x in (-10, 10):
        ic.add(rect(cx + x * s - 2 * s, cy + 9 * s, cx + x * s + 2 * s, cy + 15 * s), "bat", base=0.4, bevel=0)
    ic.add(inter(ellipse(cx, cy, 17 * s, 15 * s), rect(cx - 18 * s, cy - 6 * s, cx + 18 * s, cy + 16 * s)), "bat", mode="sphere", base=0.55,
           sphere=(cx, cy, 17 * s, 15 * s), line=True)
    ic.add(ellipse(cx, cy - 6 * s, 17 * s, 4.5 * s), "bat", base=0.7, grad=0.4, line=True)
    ic.add(ellipse(cx, cy - 6 * s, 13.5 * s, 3 * s), liquid, base=0.75, grad=0.5, bevel=0, cast=False)
    for (x, y, r) in ((-5, -11, 2.4), (3, -14, 1.8), (7, -10, 1.4)):
        ic.add(circle(cx + x * s, cy + y * s, r * s), liquid, mode="sphere", base=0.8)


def mortar(ic, cx, cy, s=1.0):
    ic.add(capsule(cx + 2 * s, cy - 2 * s, cx + 12 * s, cy - 18 * s, 2.6 * s), "stone", mode="cyl", axis=(0.5, -0.85), base=0.65)
    ic.add(inter(ellipse(cx, cy, 15 * s, 12 * s), rect(cx - 16 * s, cy, cx + 16 * s, cy + 13 * s)), "stone", base=0.52, grad=0.6, line=True)
    ic.add(ellipse(cx, cy, 15 * s, 3.5 * s), "stone", base=0.75, grad=0.4, line=True)
    ic.add(ellipse(cx, cy, 11.5 * s, 2.2 * s), "green", base=0.55, bevel=0, cast=False)


def drop(ic, cx, cy, s=1.0, pal="water"):
    ic.add(union(circle(cx, cy + 3 * s, 7 * s), poly([(cx - 6.7 * s, cy + 1 * s), (cx, cy - 12 * s), (cx + 6.7 * s, cy + 1 * s)])), pal,
           base=0.6, grad=0.6, bevel=1.0, line=True)
    ic.px(int(cx - 3 * s), int(cy + 1 * s), "#eefcf8")


def sword(ic, x0, y0, x1, y1, s=1.0, pal="steel"):
    """a sword: point (x0, y0) -> pommel (x1, y1)"""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; px, py = -uy, ux
    gx, gy = x0 + ux * L * 0.7, y0 + uy * L * 0.7
    ic.add(union(capsule(x0 + ux * 3, y0 + uy * 3, gx, gy, 3.0 * s), poly([(x0, y0), (x0 + ux * 4 + px * 3 * s, y0 + uy * 4 + py * 3 * s),
                                                                         (x0 + ux * 4 - px * 3 * s, y0 + uy * 4 - py * 3 * s)])),
           pal, base=0.62, grad=0.6, bevel=1.0, line=True)
    ic.add(capsule(gx + px * 8 * s, gy + py * 8 * s, gx - px * 8 * s, gy - py * 8 * s, 2.0 * s), "gold", base=0.6, line=True)
    ic.add(capsule(gx, gy, x1 - ux * 2, y1 - uy * 2, 1.8 * s), "leather", base=0.55)
    ic.add(circle(x1, y1, 2.9 * s), "gold", mode="sphere", base=0.62)


def target(ic, cx, cy, r, cat="damage"):
    ic.add(ering(cx, cy, r, r, r - 3, r - 3), acc(cat), base=0.65, bevel=0, line=True)
    ic.add(circle(cx, cy, r * 0.32), acc(cat), base=0.75, bevel=0, line=True)
    for (a, b, c, d) in ((cx - r - 3, cy, cx - r + 4, cy), (cx + r - 4, cy, cx + r + 3, cy), (cx, cy - r - 3, cx, cy - r + 4), (cx, cy + r - 4, cx, cy + r + 3)):
        ic.add(capsule(a, b, c, d, 1.4), acc(cat), base=0.75, bevel=0)


def helmet(ic, cx, cy, s=1.0, pal="copper", lamp=False):
    dome = union(inter(ellipse(cx, cy + 2 * s, 17 * s, 17 * s), rect(0, 0, 64, cy + 2 * s)), rect(cx - 17 * s, cy, cx + 17 * s, cy + 4 * s))
    ic.add(dome, pal, base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(cx - 21 * s, cy + 3 * s, cx + 21 * s, cy + 8 * s), pal, base=0.42, grad=0.4, line=True)
    if lamp:
        ic.add(circle(cx, cy - 6 * s, 4 * s), "lamp", mode="sphere", base=0.85, line=True)


def compass(ic, cx, cy, r):
    ic.add(circle(cx, cy, r), "gold", mode="sphere", base=0.6, line=True)
    ic.add(circle(cx, cy, r * 0.76), "cream", base=0.72, grad=0.4, bevel=0, cast=False)
    ic.add(poly([(cx, cy - r * 0.7), (cx + r * 0.2, cy), (cx - r * 0.2, cy)]), "red", base=0.62, bevel=0)
    ic.add(poly([(cx, cy + r * 0.7), (cx + r * 0.2, cy), (cx - r * 0.2, cy)]), "steel", base=0.62, bevel=0)
    ic.add(circle(cx, cy, r * 0.1), "gold", base=0.8, bevel=0)


def map_scroll(ic, cx, cy, s=1.0):
    ic.add(rect(cx - 15 * s, cy - 11 * s, cx + 15 * s, cy + 11 * s), "cream", base=0.66, grad=0.4, line=True,
           pattern=lambda x, y: -0.12 if int((x - cx + 15 * s) // (10 * s)) % 2 else 0)
    for x in (-16, 16):
        ic.add(rrect(cx + x * s - 2.5 * s, cy - 13 * s, cx + x * s + 2.5 * s, cy + 13 * s, 2 * s), "wood", mode="cyl", axis=(0, 1), base=0.55, line=True)
    for k in range(4):
        ic.add(circle(cx - 10 * s + k * 5 * s, cy + 5 * s - k * 2.5 * s, 1.1 * s), "red", base=0.4, bevel=0, cast=False)
    ic.add(union(capsule(cx + 7 * s, cy - 7 * s, cx + 12 * s, cy - 2 * s, 1.2 * s), capsule(cx + 12 * s, cy - 7 * s, cx + 7 * s, cy - 2 * s, 1.2 * s)),
           "red", base=0.6, bevel=0, cast=False)


def waystone(ic, cx, by, s=1.0, cat="ability"):
    ic.add(poly([(cx - 9 * s, by), (cx - 7 * s, by - 26 * s), (cx, by - 34 * s), (cx + 7 * s, by - 26 * s), (cx + 9 * s, by)]), "stone", base=0.5,
           grad=0.6, line=True)
    ic.add(poly(star_pts(cx, by - 18 * s, 5.5 * s, 2.2 * s, 4)), acc(cat), base=0.85, bevel=0, cast=False)
    ic.add(rect(cx - 12 * s, by - 2 * s, cx + 12 * s, by + 2 * s), "stone", base=0.35, bevel=0)


def campfire(ic, cx, by, s=1.0):
    flame(ic, cx, by - 12 * s, 1.0 * s)
    ic.add(capsule(cx - 12 * s, by - 1 * s, cx + 10 * s, by - 6 * s, 2.6 * s), "wood", mode="cyl", axis=(1, -0.22), base=0.55, line=True)
    ic.add(capsule(cx - 10 * s, by - 6 * s, cx + 12 * s, by - 1 * s, 2.6 * s), "wood", mode="cyl", axis=(1, 0.22), base=0.5, line=True)


def backpack(ic, cx, cy, s=1.0, pal="leather"):
    ic.add(ering(cx, cy - 13 * s, 6 * s, 5 * s, 3.8 * s, 3 * s), pal, base=0.4, bevel=0, line=True)
    ic.add(rrect(cx - 12 * s, cy - 11 * s, cx + 12 * s, cy + 14 * s, 5 * s), pal, base=0.55, grad=0.6, line=True)
    ic.add(rrect(cx - 12 * s, cy - 11 * s, cx + 12 * s, cy - 1 * s, 5 * s), pal, base=0.72, grad=0.5, line=True)
    ic.add(rrect(cx - 7 * s, cy + 3 * s, cx + 7 * s, cy + 11 * s, 2 * s), pal, base=0.45, grad=0.4, line=True)
    ic.add(rect(cx - 1.6 * s, cy - 3 * s, cx + 1.6 * s, cy + 1 * s), "gold", base=0.7, bevel=0)


def pan(ic, cx, cy, s=1.0, food=None):
    ic.add(capsule(cx + 12 * s, cy, cx + 25 * s, cy - 4 * s, 2.0 * s), "wood", base=0.55, bevel=0, line=True)
    ic.add(ellipse(cx, cy + 2 * s, 14 * s, 6 * s), "steel", base=0.4, grad=0.5, line=True)
    ic.add(ellipse(cx, cy, 14 * s, 5 * s), "steel", base=0.62, grad=0.5, line=True)
    ic.add(ellipse(cx, cy, 11.5 * s, 3.6 * s), "steel", base=0.3, bevel=0, cast=False)
    if food:
        ic.add(ellipse(cx, cy - 1 * s, 7 * s, 3 * s), food, base=0.7, grad=0.5, bevel=0.6, line=True)


def plate(ic, cx, cy, s=1.0):
    ic.add(ellipse(cx, cy, 17 * s, 6 * s), "cream", base=0.6, grad=0.5, line=True)
    ic.add(ellipse(cx, cy - 0.5 * s, 12 * s, 3.8 * s), "cream", base=0.8, bevel=0, cast=False)


def bread(ic, cx, cy, s=1.0):
    ic.add(rot_ellipse(cx, cy, 14 * s, 7.5 * s, -10), "wood", base=0.62, grad=0.6, bevel=1.0, line=True,
           pattern=lambda x, y: 0.16 if abs(((x - cx) * 0.8 + (y - cy)) % (6 * s) - 3 * s) < 0.7 * s else 0)


def drumstick(ic, cx, cy, s=1.0):
    ic.add(capsule(cx + 4 * s, cy + 4 * s, cx + 13 * s, cy + 13 * s, 1.8 * s), "cream", base=0.75, bevel=0, line=True)
    for (x, y) in ((13, 15), (15, 12)):
        ic.add(circle(cx + x * s, cy + y * s, 2.4 * s), "cream", base=0.75, bevel=0, line=True)
    ic.add(rot_ellipse(cx - 2 * s, cy - 2 * s, 11 * s, 8 * s, 45), "mahog", base=0.62, grad=0.6, bevel=1.0, line=True)


def cake(ic, cx, cy, s=1.0):
    ic.add(rect(cx - 15 * s, cy - 4 * s, cx + 15 * s, cy + 10 * s), "wood", base=0.62, grad=0.5, line=True,
           pattern=lambda x, y: 0.25 if abs(y - cy - 3 * s) < 1.5 * s else 0)
    ic.add(union(ellipse(cx, cy - 4 * s, 15 * s, 4 * s), *[circle(cx + x * s, cy - 2 * s, 2.4 * s) for x in (-11, -4, 3, 10)]), "cream", base=0.8,
           grad=0.4, line=True)
    ic.add(circle(cx, cy - 9 * s, 3.4 * s), "red", mode="sphere", base=0.62, line=True)


def bottle(ic, cx, cy, s=1.0, pal="ruby", label="cream"):
    ic.add(union(rrect(cx - 7 * s, cy - 6 * s, cx + 7 * s, cy + 16 * s, 3 * s), rect(cx - 2.6 * s, cy - 18 * s, cx + 2.6 * s, cy - 5 * s)), pal,
           mode="cyl", axis=(0, 1), base=0.55, line=True)
    ic.add(rect(cx - 7 * s, cy + 2 * s, cx + 7 * s, cy + 9 * s), label, base=0.68, bevel=0)
    ic.add(rect(cx - 3 * s, cy - 21 * s, cx + 3 * s, cy - 17 * s), "wood", base=0.55, bevel=0, line=True)


def jar(ic, cx, cy, s=1.0, fill="red", glass="glass"):
    ic.add(rrect(cx - 9 * s, cy - 8 * s, cx + 9 * s, cy + 12 * s, 3 * s), glass, base=0.55, grad=0.5, line=True)
    ic.add(rrect(cx - 7.5 * s, cy - 2 * s, cx + 7.5 * s, cy + 10.5 * s, 2.5 * s), fill, base=0.58, grad=0.5, rim=False,
           pattern=lambda x, y: 0.12 if int(x * 1.3 + y * 0.7) % 3 == 0 else 0)
    ic.add(rrect(cx - 10 * s, cy - 13 * s, cx + 10 * s, cy - 7 * s, 1.5 * s), "wood", base=0.55, grad=0.4, line=True)


def table(ic, cx, cy, s=1.0, pal="wood", cloth="red"):
    for x in (-15, 13):
        ic.add(rect(cx + x * s, cy, cx + (x + 3) * s, cy + 14 * s), pal, base=0.35, bevel=0, line=True)
    ic.add(poly([(cx - 20 * s, cy), (cx + 20 * s, cy), (cx + 16 * s, cy - 6 * s), (cx - 16 * s, cy - 6 * s)]), cloth, base=0.7, grad=0.5, line=True)
    ic.add(rect(cx - 20 * s, cy, cx + 20 * s, cy + 4 * s), cloth, base=0.45, bevel=0, line=True)


def whistle(ic, cx, cy, s=1.0, pal="steel"):
    ic.add(rrect(cx - 13 * s, cy - 4 * s, cx + 4 * s, cy + 3 * s, 1.5 * s), pal, mode="cyl", axis=(1, 0), base=0.6, line=True)
    ic.add(circle(cx + 6 * s, cy + 2 * s, 7 * s), pal, mode="sphere", base=0.6, line=True)
    ic.add(rect(cx - 5 * s, cy - 4 * s, cx - 1 * s, cy - 1 * s), "navy", base=0.12, bevel=0, cast=False)
    ic.add(ering(cx + 10 * s, cy - 5 * s, 3 * s, 3 * s, 1.6 * s, 1.6 * s), "gold", base=0.6, bevel=0, line=True)


def fang(ic, cx, cy, s=1.0, pal="bone", ang=0.0):
    pts = [(-5, -10), (5, -10), (4, -2), (1, 8), (-1, 12), (-2, 4), (-5, -4)]
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ic.add(poly([(cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s) for x, y in pts]), pal, base=0.66, grad=0.6, bevel=1.0, line=True)


def wing(ic, cx, cy, s=1.0, flip=False, pal="cloud"):
    f = -1 if flip else 1
    for k, (x, y, rx, ry, a) in enumerate(((0, -4, 13, 4.5, -25), (3, 2, 11, 4, -10), (5, 8, 9, 3.6, 5))):
        ic.add(rot_ellipse(cx + f * x * s, cy + y * s, rx * s, ry * s, a if f > 0 else 180 - a), pal, base=0.7 - 0.1 * k, grad=0.5, bevel=0.8,
               line=True)


def arrows_out(ic, cx, cy, r, cat="ability", s=0.85, angs=(-45, 45, 135, 225)):
    for a in angs:
        arrow(ic, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), s, cat, ang=a)


def clock(ic, cx, cy, r, cat="ability"):
    """the COOLDOWN badge: a clock with an accent rim and a back-turning arrow head (shorter wait)"""
    ic.add(circle(cx, cy, r), acc(cat), mode="sphere", base=0.6, line=True)
    ic.add(circle(cx, cy, r * 0.72), "cream", base=0.75, grad=0.3, bevel=0, cast=False)
    ic.add(capsule(cx, cy, cx, cy - r * 0.55, max(0.9, r * 0.11)), "navy", base=0.15, bevel=0, cast=False)
    ic.add(capsule(cx, cy, cx + r * 0.42, cy + r * 0.1, max(0.9, r * 0.11)), "navy", base=0.15, bevel=0, cast=False)
    ic.add(poly([(cx - r - 3, cy - r * 0.2), (cx - r + 3, cy - r * 0.2), (cx - r, cy + r * 0.45)]), acc(cat), base=0.85, bevel=0, line=True)


def hourglass(ic, cx, cy, s=1.0, cat="ability"):
    """the DURATION badge: wood ends, glass, the sand in the accent colour"""
    ic.add(union(poly([(cx - 7 * s, cy - 10 * s), (cx + 7 * s, cy - 10 * s), (cx + 1.2 * s, cy), (cx - 1.2 * s, cy)]),
                 poly([(cx - 1.2 * s, cy), (cx + 1.2 * s, cy), (cx + 7 * s, cy + 10 * s), (cx - 7 * s, cy + 10 * s)])), "glass", base=0.6, grad=0.4, line=True)
    ic.add(poly([(cx - 5.5 * s, cy + 9 * s), (cx + 5.5 * s, cy + 9 * s), (cx, cy + 3 * s)]), acc(cat), base=0.75, bevel=0, cast=False)
    ic.add(poly([(cx - 3 * s, cy - 5 * s), (cx + 3 * s, cy - 5 * s), (cx, cy - 1 * s)]), acc(cat), base=0.75, bevel=0, cast=False)
    for y in (-11.5, 11.5):
        ic.add(rrect(cx - 9 * s, cy + y * s - 1.8 * s, cx + 9 * s, cy + y * s + 1.8 * s, 1 * s), "wood", base=0.6, grad=0.4, line=True)


def xp_orb(ic, cx, cy, r):
    ic.add(circle(cx, cy, r), acc("xp"), mode="sphere", base=0.62, line=True)
    ic.add(poly(star_pts(cx, cy + r * 0.04, r * 0.6, r * 0.25, 4)), acc("xp"), base=0.95, bevel=0, cast=False)


def stack_badge(ic, cx, cy, s=1.0, pal="cream"):
    """a 'more slots / stack' badge: three stacked rounded tiles"""
    for k in range(3):
        ic.add(rrect(cx - 7 * s + k * 2 * s, cy - 7 * s + k * 3 * s, cx + 5 * s + k * 2 * s, cy + 1 * s + k * 3 * s, 1.6 * s), pal,
               base=0.5 + 0.12 * k, grad=0.4, line=True)


def clover(ic, cx, cy, s=1.0):
    for (dx, dy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ic.add(circle(cx + dx * 4.3 * s, cy + dy * 4.3 * s, 4.8 * s), "green", mode="sphere", base=0.6, line=True)
    ic.add(capsule(cx, cy + 2 * s, cx - 3 * s, cy + 13 * s, 1.2 * s), "green", base=0.45, bevel=0)
    ic.add(circle(cx, cy, 1.8 * s), "green", base=0.85, bevel=0, cast=False)


def feather(ic, cx, cy, s=1.0, ang=-50.0, pal="cream"):
    ic.add(rot_ellipse(cx, cy, 13 * s, 4.2 * s, ang), pal, base=0.68, grad=0.6, bevel=0.8, line=True,
           pattern=lambda x, y: -0.08 if int((x + y) / (2 * s)) % 2 else 0)
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ic.add(capsule(cx - c * 15 * s, cy - sn * 15 * s, cx + c * 11 * s, cy + sn * 11 * s, 0.7 * s), "wood", base=0.45, bevel=0, cast=False)


def bone(ic, x0, y0, x1, y1, s=1.0):
    ux, uy = unit(x0, y0, x1, y1); px, py = -uy, ux
    ic.add(union(capsule(x0, y0, x1, y1, 2.2 * s), *[circle(x + px * d * s, y + py * d * s, 2.7 * s) for x, y in ((x0, y0), (x1, y1)) for d in (-2.2, 2.2)]),
           "bone", base=0.66, grad=0.5, bevel=0.8, line=True)


def gauntlet(ic, cx, cy, s=1.0, pal="steel"):
    ic.add(rrect(cx - 9 * s, cy - 6 * s, cx + 9 * s, cy + 9 * s, 3 * s), pal, base=0.58, grad=0.6, line=True)
    for k in range(4):
        ic.add(rrect(cx - 9 * s + k * 4.6 * s, cy - 13 * s, cx - 5.4 * s + k * 4.6 * s, cy - 4 * s, 1.5 * s), pal, base=0.68, grad=0.5, line=True)
    ic.add(rrect(cx - 8 * s, cy + 8 * s, cx + 8 * s, cy + 15 * s, 1.5 * s), "leather", base=0.5, grad=0.4, line=True)


def turn_arrow(ic, cx, cy, R, a0, a1, cat="ability", w=3.0):
    """a circular arrow (reset / replant / refund): an accent arc from a0 to a1 (degrees) with its head at a1"""
    arc(ic, cx, cy, R, a0, a1, w, cat)
    d = 1 if a1 > a0 else -1
    a = math.radians(a1)
    tx, ty = -math.sin(a) * d, math.cos(a) * d                     # direction of travel at the end
    hx_, hy_ = cx + R * math.cos(a), cy + R * math.sin(a)
    nx, ny = math.cos(a), math.sin(a)
    ic.add(poly([(hx_ + nx * w * 1.5, hy_ + ny * w * 1.5), (hx_ - nx * w * 1.5, hy_ - ny * w * 1.5), (hx_ + tx * w * 1.8, hy_ + ty * w * 1.8)]),
           acc(cat), base=0.75, bevel=0, line=True)


def flower(ic, cx, cy, s=1.0, petal="red", heart_="gold"):
    for k in range(5):
        a = math.radians(-90 + k * 72)
        ic.add(circle(cx + 6 * s * math.cos(a), cy + 6 * s * math.sin(a), 4.6 * s), petal, mode="sphere", base=0.62, line=True)
    ic.add(circle(cx, cy, 3.6 * s), heart_, mode="sphere", base=0.7, line=True)


def bush(ic, cx, cy, s=1.0, pal="green"):
    ic.add(union(*[circle(cx + x * s, cy + y * s, r * s) for x, y, r in ((-10, 3, 9), (0, -4, 11), (10, 3, 9), (0, 6, 9))]), pal, base=0.5, grad=0.6,
           bevel=1.0, line=True, pattern=lambda x, y: 0.08 * math.sin(x * 1.1) * math.sin(y * 1.1))


def cape(ic, cx, cy, s=1.0, pal="green", clasp="gold"):
    ic.add(poly([(cx - 8 * s, cy - 14 * s), (cx + 8 * s, cy - 14 * s), (cx + 18 * s, cy + 16 * s), (cx + 6 * s, cy + 12 * s), (cx, cy + 17 * s),
                 (cx - 6 * s, cy + 12 * s), (cx - 18 * s, cy + 16 * s)]), pal, base=0.55, grad=0.6, line=True, pattern=lambda x, y: 0.06 * math.sin(x * 0.7))
    ic.add(rrect(cx - 10 * s, cy - 17 * s, cx + 10 * s, cy - 12 * s, 2 * s), pal, base=0.75, grad=0.4, line=True)
    ic.add(circle(cx, cy - 14.5 * s, 3.2 * s), clasp, mode="sphere", base=0.7, line=True)


def coil(ic, cx, cy, s=1.0, pal="green"):
    """a coiled rope / vine"""
    for k, r in enumerate((13, 9, 5)):
        ic.add(ering(cx, cy, r * s, r * 0.8 * s, (r - 3) * s, (r - 3) * 0.8 * s), pal, mode="torus",
               torus=(cx, cy, r * s, r * 0.8 * s, (r - 3) * s, (r - 3) * 0.8 * s), base=0.55 + 0.06 * k, bevel=0, line=True)


def podium(ic, x0, by, w=18.0, pals=("copper", "steel", "gold"), steps=(10, 17, 24)):
    """the tool-tier steps (copper / iron / gold)"""
    for k, (pal, h) in enumerate(zip(pals, steps)):
        x = x0 + k * w
        ic.add(rect(x, by - h, x + w, by), pal, base=0.5 + 0.05 * k, grad=0.5, line=True)
        ic.add(rect(x, by - h, x + w, by - h + 2.5), pal, base=0.85, bevel=0)


def bolt(ic, cx, cy, s=1.0, pal="lamp"):
    """a lightning bolt (Stamina, like the vanilla Stamina symbol - Skyy's accessory-icon rule)"""
    ic.add(poly([(cx + 3 * s, cy - 14 * s), (cx - 7 * s, cy + 2 * s), (cx - 0.5 * s, cy + 2 * s), (cx - 4 * s, cy + 14 * s), (cx + 8 * s, cy - 3 * s),
                 (cx + 1.5 * s, cy - 3 * s), (cx + 6 * s, cy - 14 * s)]), pal, base=0.68, grad=0.6, bevel=1.0, line=True)


def bubbles(ic, cx, cy, s=1.0):
    for (x, y, r) in ((0, 6, 6), (8, -4, 4.5), (-5, -9, 3.5), (5, -15, 2.5)):
        ic.add(ering(cx + x * s, cy + y * s, r * s, r * s, (r - 1.4) * s, (r - 1.4) * s), "glass", base=0.75, bevel=0, line=True)
        ic.px(int(cx + (x - r * 0.4) * s), int(cy + (y - r * 0.4) * s), "#eefcf8")


# ====================================================================== the per-tree drawings: tools/art/node_icons/<tree>.py
# Each module does `from make_tree_node_icons import *`, draws with the painter above and defines
#   ROWS = [(node key "<Tree>.b<branch>.<id | r<row>.free>", file stem, category, draw fn, what the icon shows), ...]
# (the class trees' modules node_icons/class_<Class>.py belong to tools/art/make_class_node_icons.py).
SKILL_TREES = ["Mining", "Foraging", "Farming", "Fishing", "Smithing", "Cooking", "Alchemy", "Combat", "Acrobatics", "Exploration",
               "Beastmastery"]


def draw_rows(tree):
    """the ROWS of node_icons/<tree>.py, or None when that tree has no module yet"""
    import importlib
    fn = os.path.join(HERE, "node_icons", tree.lower() + ".py")
    if not os.path.isfile(fn):
        return None
    return importlib.import_module("node_icons." + tree.lower()).ROWS


class _Draw(object):
    def get(self, tree, default=None):
        r = draw_rows(tree)
        return default if r is None else r

    def __contains__(self, tree):
        return draw_rows(tree) is not None


DRAW = _Draw()



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


# the tree colour of each skill tree (SkyyTrees TCOLOR / UI_DATA_COLORS) = the learnt ring on the radial page
TREE_RING = {"Mining": "#8fc8ff", "Foraging": "#8fe08a", "Farming": "#f0d060", "Cooking": "#ffb070", "Acrobatics": "#c8a0ff",
             "Exploration": "#e0a040", "Alchemy": "#7fe0d0", "Smithing": "#c0c8d0", "Fishing": "#6fc0e8", "Combat": "#b8f0a0",
             "Beastmastery": "#d8a070"}
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
    s = s.replace("’", "'").replace("x3", "X3").replace("&", "+")
    return "".join(ch if (ch in P._F or ch.upper() in P._F) else " " for ch in s)


def build_sheet(tree, built):
    RING = hx(TREE_RING.get(tree, "#8fc8ff"))
    COLS, CW, CH = 4, 316, 236
    branches = []
    for n, r, img, data in built:
        if not branches or branches[-1][0] != n[1]:
            branches.append((n[1], []))
        branches[-1][1].append((n, r, img))
    W = 24 + COLS * CW + 8
    hb = sum(44 + ((len(items) + COLS - 1) // COLS) * CH + 14 for _, items in branches)
    strip_h = 60 + len(branches) * (32 + 12) + 30 + len(branches) * (48 + 12) + 40
    H = 170 + hb + strip_h + 40
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "SKYWYNN %s TREE - NODE ICONS - DRAFT V1" % tree.upper(), GOLDT, 4)
    cv.text(24, 60, "ONE 64 PX ICON PER NODE (%d). EACH CELL: 2X ICON, 1X ICON, THE NODE ON ITS DISC AT 100 %% + 150 %%." % len(built), DIM, 2)
    x = 24
    cv.text(24, 84, "ACCENT COLOUR = WHAT THE NODE BOOSTS:", DIM, 2)
    y = 108; x = 24
    for cid, lab, hexc, _why in CATS:
        if x + 20 + 6 * len(lab) > W - 16:
            x = 24; y += 20
        cv.rect(x, y, x + 14, y + 14, hx(hexc)); x2 = cv.text(x + 20, y + 4, lab, INK, 1)
        x = x2 + 22
    y += 32
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
            node_disc(cv, cx + 150, cy + 91, 32, img, ring=RING)
            node_disc(cv, cx + 196, cy + 83, 48, img, ring=RING)
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
            node_disc(cv, 28 + k * 38, yy, 32, img, ring=RING)
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
    for nm in ((sname, "sheet.png") if tree == "Mining" else (sname,)):
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
    print("wrote %d %s node icons + %s%s + manifest.json to %s" % (len(nodes), tree, sname, " + sheet.png" if tree == "Mining" else "", OUT))


def main():
    a = sys.argv[1:]
    tree = a[a.index("--tree") + 1] if "--tree" in a else "Mining"
    trees = [t for t in SKILL_TREES if t in DRAW] if "--all" in a else [tree]
    if "--counts" in a:
        for t, k, b, c in counts():
            print("%-13s %-5s %d branches %3d nodes%s" % (t, k, b, c, "  (icons done)" if t in DRAW else ""))
        return
    if "--check" in a:
        for t in trees:
            one = [d for _, _, _, d in build_icons(t)]
            two = [d for _, _, _, d in build_icons(t)]
            assert one == two, "%s: not deterministic" % t
            print("OK: %d %s icons, two builds byte-identical" % (len(one), t))
        return
    for t in trees:
        write_all(t)


if __name__ == "__main__":
    main()
