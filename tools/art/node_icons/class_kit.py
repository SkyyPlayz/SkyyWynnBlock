"""Shared parts for the CLASS tree node icons (node_icons/class_<Class>.py; runner tools/art/make_class_node_icons.py).

Built on the approved Mining painter (make_tree_node_icons.py, imported read-only): same Icon renderer, outline, light, hard alpha.
ORIGINAL pixels only - the class motifs (shields, banners, fists, hoods, bows, meteors ...) are drawn from code here; they echo the
approved ability icons' subjects (art/ability-icons) without copying a pixel of them.

Layout of a class node icon (64 x 64, shown 18 px in a 32 px disc):
  - the SUBJECT (the ability / weapon / body part the node changes) roughly centred, leaving the lower right free
  - one GLYPH at the lower right (or round the subject) = WHAT changes, in the category accent colour (CLASS_CATS)
  - modifier-type nodes (hook 'mod') get the MOD MARK: a small pink rune diamond in the top-left corner (mod_mark)
"""
import math
from make_tree_node_icons import *          # noqa: F401,F403 - the painter + part helpers + accents (read-only)
import make_tree_node_icons as T
import make_menu_icons as M

# ====================================================================== palettes (dark -> light)
_NEW = {
    "linen":   ["#4e3a34", "#7a6252", "#a68e74", "#cbb796", "#e6d8b8", "#f6eedc"],
    "poison":  ["#10260a", "#1e4a10", "#2e7418", "#4ea024", "#7ccc3a", "#b4ec6a", "#e2fbb4"],
    "smoke":   ["#1c1a26", "#2e2b3c", "#454158", "#605b74", "#807a92", "#a6a0b4", "#ccc8d6"],
    "shadow":  ["#100a1c", "#1c1230", "#2a1c48", "#3c2a62", "#53407e", "#70609c", "#9a8cc0"],
    "arcane":  ["#22104a", "#3a1a7e", "#5a2cb4", "#8250e2", "#ab82f6", "#d2bcff", "#f1e8ff"],
    "mana":    ["#0e1f56", "#16378e", "#2356c4", "#2f6fe0", "#5c9af2", "#9cc8fc", "#def0ff"],
    "ice":     ["#173a6e", "#22609e", "#3a8cc6", "#62b6e0", "#98d8f0", "#cdeefa", "#f0fbff"],
    "holy":    ["#5a3e14", "#8a6420", "#bc9234", "#e2be58", "#f6dc86", "#fff0bc", "#fffae6"],
    "rift":    ["#0a3038", "#105060", "#1c7a88", "#30a8b4", "#5ed2d8", "#a2eeee", "#dcfcf8"],
    "blood":   ["#2a0408", "#4e0a12", "#7c121c", "#ac1e28", "#d83a3c", "#f26c62", "#fcaa9a"],
    "bone":    ["#3e3428", "#625644", "#8a7c64", "#b2a486", "#d4c8a8", "#ece4cc", "#f8f4e6"],
    "rock":    ["#1c1222", "#2e1c30", "#47293c", "#653a46", "#865450", "#a8725e", "#c8987a"],
    "feather": ["#4a4050", "#6e6476", "#968c9c", "#bcb4c0", "#dcd6de", "#f2eef2"],
    "bronze":  ["#2e1a08", "#50300e", "#7a4c18", "#a26c26", "#c8903c", "#e4b866", "#f6dca0"],
    "dark":    ["#0c0c14", "#16161f", "#20202c", "#2c2c3a", "#3a3a4a", "#4c4c5e"],
    # ---- class colours (art/ability-icons class_colours = the bright step, index 4)
    "cls_Warrior":    ["#3a2808", "#6a4a12", "#9c7224", "#c4923a", "#e0b060", "#f0d08e", "#faecc8"],
    "cls_Berserker":  ["#300608", "#5a0e12", "#8a1a1e", "#b42c2c", "#d9443f", "#f07868", "#fcb4a4"],
    "cls_Spellblade": ["#062a30", "#0c4a54", "#167680", "#2ca2ac", "#6fd0d8", "#a8ecee", "#e0fcfc"],
    "cls_Monk":       ["#561a0c", "#8c3010", "#c4521a", "#e0702a", "#f08a30", "#f8b462", "#fde0b0"],
    "cls_Assassin":   ["#1c0e36", "#34205e", "#54388e", "#8060c8", "#b58cff", "#d2b8ff", "#eee2ff"],
    "cls_Archer":     ["#0e2a0a", "#1c4a14", "#2c7424", "#4ca040", "#8fd67a", "#bcec9e", "#e6fad2"],
    "cls_Mage":       ["#0e1e40", "#1c386e", "#2e5a9c", "#5486c4", "#7fb0e0", "#b2d4f2", "#e0eefa"],
    "cls_Priest":     ["#4a3416", "#7c6028", "#b39a4c", "#dccb7c", "#f2e6a0", "#fcf5d4", "#fffbe8"],
    # ---- class-tree accent ramps (bright step index 4 = the legend hex)
    "acc_ward":     ["#1a222c", "#2e3a48", "#4a5a6c", "#7a8ca0", "#d6e4ee", "#e8f0f6", "#f6fafc"],
    "acc_control":  ["#3e3006", "#6a520c", "#a07c14", "#d0a824", "#ffd84a", "#ffeb94", "#fff8d4"],
    "acc_resource": ["#1e1440", "#34246e", "#523ca0", "#7a5ecc", "#b496ff", "#d4c2ff", "#efe8ff"],
    "acc_mod":      ["#3e0a2c", "#6a144c", "#a02474", "#d8449e", "#ff8ad0", "#ffbce4", "#ffe6f4"],
}
for _k, _v in _NEW.items():
    T.PALN.setdefault(_k, _v)
    if _k not in M.PAL:
        M.PAL[_k] = _v
        M.PALC[_k] = [hx(c) for c in _v]

# what a class node changes -> its accent (legend of the class sheets; style guide 15 where it has a colour)
CLASS_CATS = [
    ("damage",   "DAMAGE / VULNERABILITY", "#ff9a3c", "style guide 15: the Fire element (orange) - same as the Mining sheet"),
    ("health",   "HEALTH / HEAL / LEECH / LESS DAMAGE TAKEN", "#ff7a7a", "style guide 15: the red stat colour = Health"),
    ("ward",     "WARD / SHIELD",          "#d6e4ee", "style guide 15: the stat-name soft white (defence)"),
    ("speed",    "MOVE SPEED / HASTE",     "#86d8d0", "style guide 15: the Air element (white-teal) - same as Mining"),
    ("ability",  "ABILITY SHAPE (RADIUS / DURATION / COOLDOWN / CHAIN / ECHO)", "#8fc8ff", "the ability blue of the Mining sheet"),
    ("control",  "CROWD CONTROL (SLOW / STUN / ROOT / KNOCKBACK / PULL)", "#ffd84a", "style guide 15: the Thunder element (yellow) = stun stars"),
    ("resource", "MANA / STAMINA / COST",  "#b496ff", "the arcane violet of the Mage / Spellblade mana ramps"),
]
CLASS_CAT_HEX = dict((c[0], c[2]) for c in CLASS_CATS)
MOD_HEX = "#ff8ad0"


class Reuse(object):
    """a free-row ABILITY node: its approved icon in art/ability-icons is reused as is (never redrawn)"""
    def __init__(self, cls, ability):
        self.cls, self.ability = cls, ability
        self.rel = "Common/Icons/Abilities/%s/%s.png" % (cls, ability)


def C(cls):
    return "cls_" + cls


# ====================================================================== small geometry helpers
def rot(pts, cx, cy, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def arcp(ic, cx, cy, R, a0, a1, w, pal, base=0.7, steps=16, line=False, cast=False):
    """a thick arc in ANY palette (T.arc takes a category)"""
    po, pi = [], []
    for k in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * k / steps)
        po.append((cx + (R + w / 2) * math.cos(a), cy + (R + w / 2) * math.sin(a)))
        pi.append((cx + (R - w / 2) * math.cos(a), cy + (R - w / 2) * math.sin(a)))
    ic.add(poly(po + pi[::-1]), pal, base=base, grad=0.3, bevel=0, cast=cast, line=line)


def arc_arrow(ic, cx, cy, R, a0, a1, w, cat, base=0.72):
    """an arc with an arrow head at a1 (cooldown / repeat / refresh)"""
    arcp(ic, cx, cy, R, a0, a1, w, acc(cat), base=base, line=True)
    a = math.radians(a1); d = 1 if a1 > a0 else -1
    tx, ty = -math.sin(a) * d, math.cos(a) * d
    ex, ey = cx + R * math.cos(a), cy + R * math.sin(a)
    nx, ny = math.cos(a), math.sin(a)
    h = w * 1.9
    ic.add(poly([(ex + nx * h, ey + ny * h), (ex - nx * h, ey - ny * h), (ex + tx * h * 1.5, ey + ty * h * 1.5)]), acc(cat), base=base + 0.1,
           bevel=0.6, line=True)


# ====================================================================== GLYPHS (what changes) - accent colour = category
def mod_mark(ic):
    """the modifier-type node mark (hook 'mod'): a small pink rune diamond, top-left corner, always the same"""
    ic.add(poly([(11, 4), (17.5, 10.5), (11, 17), (4.5, 10.5)]), "acc_mod", base=0.62, grad=0.6, bevel=0.8, line=True)
    ic.add(poly([(11, 8), (13.5, 10.5), (11, 13), (8.5, 10.5)]), "acc_mod", base=0.98, bevel=0, cast=False, rim=False)


def g_plus(ic, cx, cy, s, cat):
    plus(ic, cx, cy, s, cat)


def g_up(ic, cx, cy, s, cat):
    arrow(ic, cx, cy, s, cat, ang=-90)


def g_down(ic, cx, cy, s, cat):
    arrow(ic, cx, cy, s, cat, ang=90)


def g_minus(ic, cx, cy, s, cat):
    ic.add(rrect(cx - 6.5 * s, cy - 2.2 * s, cx + 6.5 * s, cy + 2.2 * s, 1 * s), acc(cat), base=0.72, grad=0.5, bevel=0.8, line=True)


def g_hourglass(ic, cx, cy, s, cat="ability"):
    ic.add(rrect(cx - 7 * s, cy - 10 * s, cx + 7 * s, cy - 7.5 * s, 0.8 * s), "wood", base=0.6, line=True)
    ic.add(rrect(cx - 7 * s, cy + 7.5 * s, cx + 7 * s, cy + 10 * s, 0.8 * s), "wood", base=0.5, line=True)
    glass = union(poly([(cx - 5.5 * s, cy - 7.5 * s), (cx + 5.5 * s, cy - 7.5 * s), (cx + 1.2 * s, cy), (cx - 1.2 * s, cy)]),
                  poly([(cx - 1.2 * s, cy), (cx + 1.2 * s, cy), (cx + 5.5 * s, cy + 7.5 * s), (cx - 5.5 * s, cy + 7.5 * s)]))
    ic.add(glass, "glass", base=0.7, grad=0.4, bevel=0.6, line=True)
    ic.add(poly([(cx - 4.6 * s, cy + 7.5 * s), (cx + 4.6 * s, cy + 7.5 * s), (cx, cy + 3 * s)]), acc(cat), base=0.75, bevel=0, cast=False)
    ic.add(poly([(cx - 2.6 * s, cy - 4.2 * s), (cx + 2.6 * s, cy - 4.2 * s), (cx, cy - 1 * s)]), acc(cat), base=0.85, bevel=0, cast=False)


def g_clock(ic, cx, cy, s, cat="ability"):
    """cooldown: a clock face with a wind-back arrow"""
    ic.add(circle(cx, cy, 8 * s), "cream", mode="sphere", base=0.7, line=True)
    ic.add(capsule(cx, cy, cx, cy - 5.5 * s, 1.1 * s), "navy", base=0.3, bevel=0, cast=False)
    ic.add(capsule(cx, cy, cx + 4 * s, cy, 1.1 * s), "navy", base=0.3, bevel=0, cast=False)
    arc_arrow(ic, cx, cy, 10.5 * s, 300, 150, 2.4 * s, cat)


def g_expand(ic, cx, cy, R, s, cat="ability"):
    for a in (-45, 45, 135, 225):
        arrow(ic, cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)), s, cat, ang=a)


def g_ring(ic, cx, cy, R, w, cat="ability", base=0.62):
    ic.add(ering(cx, cy, R, R, R - w, R - w), acc(cat), base=base, bevel=0, line=True)


def g_stars(ic, cx, cy, s, cat="control"):
    """stun: three little stars on an orbit"""
    arcp(ic, cx, cy, 9 * s, 160, 380, 1.4 * s, acc(cat), base=0.5)
    for (dx, dy, r) in ((-8, -2, 4.2), (4, -7, 3.6), (8, 4, 3.2)):
        burst(ic, cx + dx * s, cy + dy * s, r * s, r * 0.42 * s, 5, acc(cat), base=0.85, line=True)


def g_snail(ic, cx, cy, s, cat="control"):
    """slow: a snail (shell spiral + body)"""
    ic.add(union(rrect(cx - 11 * s, cy + 3 * s, cx + 9 * s, cy + 8 * s, 2.4 * s), circle(cx + 9 * s, cy + 3.5 * s, 3 * s)), "bone",
           base=0.62, grad=0.5, line=True)
    ic.add(capsule(cx + 9 * s, cy + 2 * s, cx + 11 * s, cy - 4 * s, 0.8 * s), "bone", base=0.5, bevel=0)
    ic.add(capsule(cx + 7 * s, cy + 2 * s, cx + 7.5 * s, cy - 4 * s, 0.8 * s), "bone", base=0.5, bevel=0)
    ic.add(circle(cx - 2 * s, cy - 1 * s, 8 * s), acc(cat), mode="sphere", base=0.62, line=True)
    arcp(ic, cx - 2 * s, cy - 1 * s, 4.8 * s, -90, 200, 1.5 * s, acc(cat), base=0.3)
    ic.add(circle(cx - 2 * s, cy - 1 * s, 1.6 * s), acc(cat), base=0.3, bevel=0, cast=False)


def g_push(ic, cx, cy, s, cat="control", ang=0.0):
    """knockback: a fat arrow pushing away + impact lines behind it"""
    arrow(ic, cx, cy, s, cat, ang=ang)
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); px, py = -uy, ux
    for k in (-1, 0, 1):
        bx, by = cx - ux * 10 * s + px * k * 5 * s, cy - uy * 10 * s + py * k * 5 * s
        lines(ic, [(bx, by, bx - ux * 4 * s, by - uy * 4 * s)], cat, 1.2 * s)


def g_pull(ic, cx, cy, s, cat="control", ang=180.0):
    """pull: a hook with an arrow pointing back toward you"""
    arrow(ic, cx, cy, s, cat, ang=ang)
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a)
    hx0, hy0 = cx - ux * 10 * s, cy - uy * 10 * s
    arcp(ic, hx0, hy0 + 3 * s, 4 * s, 180, 360, 2 * s, "steel", base=0.7, line=True)


def g_drop(ic, cx, cy, s, pal="blood"):
    ic.add(union(circle(cx, cy + 2.5 * s, 6 * s), poly([(cx - 5.6 * s, cy + 0.8 * s), (cx, cy - 9 * s), (cx + 5.6 * s, cy + 0.8 * s)])), pal,
           base=0.6, grad=0.6, bevel=0.9, line=True)
    ic.px(int(cx - 2 * s), int(cy + 1 * s), PALN[pal][-1] if pal in PALN else "#fcaa9a")


def g_leech(ic, cx, cy, s):
    """leech: a blood drop flowing into a heart"""
    g_drop(ic, cx - 5 * s, cy - 4 * s, 0.85 * s)
    ic.add(heart(cx + 3 * s, cy + 5 * s, 0.55 * s), acc("health"), base=0.62, grad=0.5, bevel=0.8, line=True)


def g_heart(ic, cx, cy, s, cat="health", plus_=True):
    ic.add(heart(cx, cy, 0.7 * s), acc(cat), base=0.6, grad=0.6, bevel=0.9, line=True)
    if plus_:
        ic.add(union(rect(cx - 1.1 * s, cy - 4.5 * s, cx + 1.1 * s, cy + 1.5 * s), rect(cx - 4 * s, cy - 2.6 * s, cx + 4 * s, cy - 0.4 * s)),
               "cream", base=0.9, bevel=0, cast=False)


def g_ward(ic, cx, cy, s):
    shield(ic, cx, cy, 0.85 * s, pal=acc("ward"))
    ic.add(poly([(cx - 4 * s, cy - 6 * s), (cx + 4 * s, cy - 6 * s), (cx, cy + 4 * s)]), acc("ward"), base=0.95, bevel=0, cast=False)


def g_echo(ic, cx, cy, s, cat="ability"):
    """echo / repeat: two nested ')' arcs + a small repeat arrow"""
    for R, b in ((7 * s, 0.82), (12 * s, 0.6)):
        arcp(ic, cx - 6 * s, cy, R, -50, 50, 2.4 * s, acc(cat), base=b, line=True)


def g_repeat(ic, cx, cy, s, cat="ability"):
    arc_arrow(ic, cx, cy, 7.5 * s, 200, 470, 2.6 * s, cat)


def g_fork(ic, cx, cy, s, cat="ability"):
    """split / chain to another enemy: a line forking into two arrow heads"""
    lines(ic, [(cx - 9 * s, cy + 6 * s, cx - 1 * s, cy)], cat, 1.6 * s)
    lines(ic, [(cx - 1 * s, cy, cx + 6 * s, cy - 8 * s), (cx - 1 * s, cy, cx + 8 * s, cy + 3 * s)], cat, 1.4 * s)
    arrow(ic, cx + 7 * s, cy - 9 * s, 0.55 * s, cat, ang=-50)
    arrow(ic, cx + 9.5 * s, cy + 3.5 * s, 0.55 * s, cat, ang=15)


def g_zap(ic, cx, cy, s, cat="ability"):
    """chain: a zig-zag bolt between two dots"""
    pts = [(cx - 10 * s, cy + 7 * s), (cx - 3 * s, cy - 1 * s), (cx + 1 * s, cy + 3 * s), (cx + 10 * s, cy - 7 * s)]
    for k in range(3):
        lines(ic, [(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1])], cat, 1.6 * s)
    for (x, y) in (pts[0], pts[-1]):
        ic.add(circle(x, y, 3 * s), acc(cat), mode="sphere", base=0.7, line=True)


def g_bolt(ic, cx, cy, s, cat="resource"):
    """stamina: a lightning bolt (the vanilla Stamina symbol idea)"""
    pts = [(1, -12), (-7, 1), (-1, 1), (-3, 12), (7, -2), (1, -2), (4, -12)]
    ic.add(poly([(cx + x * s, cy + y * s) for x, y in pts]), "acc_control" if cat == "stamina_y" else acc(cat), base=0.7, grad=0.6,
           bevel=0.9, line=True)


def g_crystal(ic, cx, cy, s, pal="mana"):
    """mana: a cut mana crystal"""
    gem(ic, cx, cy, 0.62 * s, pal, line=True)


def g_pierce(ic, cx, cy, s, cat="ability"):
    for dx in (-5, 3):
        ic.add(ering(cx + dx * s, cy, 3 * s, 7 * s, 1.4 * s, 5 * s), acc(cat), base=0.55, bevel=0, line=True)
    lines(ic, [(cx - 12 * s, cy, cx + 8 * s, cy)], cat, 1.4 * s, base=0.9)
    arrow(ic, cx + 9 * s, cy, 0.5 * s, cat, ang=0)


def g_homing(ic, cx, cy, s, cat="ability"):
    """follow / home in: a curved arrow into a target ring"""
    ic.add(ering(cx + 6 * s, cy - 5 * s, 5.5 * s, 5.5 * s, 3.2 * s, 3.2 * s), acc(cat), base=0.6, bevel=0, line=True)
    ic.add(circle(cx + 6 * s, cy - 5 * s, 1.5 * s), acc(cat), base=0.9, bevel=0, cast=False)
    arcp(ic, cx + 6 * s, cy + 6 * s, 11 * s, 180, 250, 2.2 * s, acc(cat), base=0.75, line=True)
    arrow(ic, cx + 1.5 * s, cy - 4.5 * s, 0.5 * s, cat, ang=-20)


def g_target(ic, cx, cy, s, cat="damage"):
    ic.add(ering(cx, cy, 9 * s, 9 * s, 6.6 * s, 6.6 * s), acc(cat), base=0.62, bevel=0, line=True)
    ic.add(circle(cx, cy, 3 * s), acc(cat), mode="sphere", base=0.7, line=True)
    for (a, b, c2, d) in ((0, -12, 0, -7), (0, 7, 0, 12), (-12, 0, -7, 0), (7, 0, 12, 0)):
        lines(ic, [(cx + a * s, cy + b * s, cx + c2 * s, cy + d * s)], cat, 1.1 * s)


def g_crack(ic, cx, cy, s, cat="damage"):
    """vulnerability: a cracked armour plate"""
    ic.add(rrect(cx - 8 * s, cy - 9 * s, cx + 8 * s, cy + 9 * s, 3 * s), "steel", base=0.58, grad=0.6, line=True)
    ic.add(poly([(cx - 1 * s, cy - 9 * s), (cx + 2 * s, cy - 3 * s), (cx - 2 * s, cy + 1 * s), (cx + 3 * s, cy + 9 * s), (cx + 0.5 * s, cy + 1.5 * s),
                 (cx + 4.2 * s, cy - 3 * s)]), acc(cat), base=0.8, bevel=0, cast=False)


def g_lowhp(ic, cx, cy, s):
    """below X % Health: a heart half drained"""
    h = heart(cx, cy, 0.7 * s)
    ic.add(h, "dark", base=0.5, grad=0.3, bevel=0.6, line=True)
    ic.add(inter(h, rect(cx - 10 * s, cy + 1 * s, cx + 10 * s, cy + 10 * s)), acc("health"), base=0.62, grad=0.4, bevel=0.6)


def g_speed(ic, x, y, s, cat="speed", n=3):
    """speed lines (to the left of a subject)"""
    lines(ic, [(x, y + k * 7 * s, x + (10 - 2 * k) * s, y + k * 7 * s) for k in range(n)], cat, 1.5 * s)


def g_wing(ic, cx, cy, s, cat="speed"):
    """haste: a little wing"""
    pts = [(0, 6), (-4, -2), (-2, -8), (4, -11), (12, -10), (8, -6), (13, -5), (8, -1), (11, 1), (4, 3)]
    ic.add(poly([(cx + x * s, cy + y * s) for x, y in pts]), acc(cat), base=0.68, grad=0.6, bevel=0.8, line=True)


def g_two(ic, cx, cy, s, cat="ability"):
    """+1 more / 2 charges: two small pips"""
    for dx in (-4, 4):
        ic.add(circle(cx + dx * s, cy, 3.4 * s), acc(cat), mode="sphere", base=0.7, line=True)


def g_skull(ic, cx, cy, s, pal="bone"):
    """a kill: a small skull"""
    ic.add(union(circle(cx, cy - 1 * s, 7 * s), rrect(cx - 4.5 * s, cy + 2 * s, cx + 4.5 * s, cy + 8 * s, 1.5 * s)), pal, base=0.66, grad=0.5,
           bevel=0.8, line=True)
    ic.add(circle(cx - 2.8 * s, cy - 0.5 * s, 2 * s), "navy", base=0.15, bevel=0, cast=False, rim=False)
    ic.add(circle(cx + 2.8 * s, cy - 0.5 * s, 2 * s), "navy", base=0.15, bevel=0, cast=False, rim=False)
    ic.add(rect(cx - 0.6 * s, cy + 4.5 * s, cx + 0.6 * s, cy + 8 * s), "navy", base=0.2, bevel=0, cast=False, rim=False)


def g_mob(ic, cx, cy, s, pal="rock", eyes="#ff7a7a"):
    """an enemy: a blocky mob head with red eyes"""
    ic.add(rrect(cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 8 * s, 2 * s), pal, base=0.55, grad=0.6, bevel=0.9, line=True)
    ic.add(rect(cx - 5.5 * s, cy - 2 * s, cx - 1.5 * s, cy + 1 * s), "navy", base=0.15, bevel=0, cast=False, rim=False)
    ic.add(rect(cx + 1.5 * s, cy - 2 * s, cx + 5.5 * s, cy + 1 * s), "navy", base=0.15, bevel=0, cast=False, rim=False)
    ic.px(int(cx - 3.5 * s), int(cy - 0.5 * s), eyes); ic.px(int(cx + 3.5 * s), int(cy - 0.5 * s), eyes)


def g_ally(ic, cx, cy, s, pal="steel"):
    """an ally / party member: a small round-shouldered figure"""
    ic.add(union(circle(cx, cy - 5 * s, 4.6 * s), rrect(cx - 7.5 * s, cy + 0.5 * s, cx + 7.5 * s, cy + 10 * s, 4 * s)), pal, base=0.6, grad=0.6,
           bevel=0.9, line=True)


def g_party(ic, cx, cy, s, pal="cream"):
    """the party: three allies, the middle one in front"""
    g_ally(ic, cx - 8 * s, cy - 1 * s, 0.78 * s, "steel")
    g_ally(ic, cx + 8 * s, cy - 1 * s, 0.78 * s, "leather")
    g_ally(ic, cx, cy + 2 * s, 0.95 * s, pal)


# ====================================================================== SUBJECTS (weapons, bodies, ability motifs)
def sword(ic, x0, y0, x1, y1, w=3.2, blade="steel", hilt="gold", grip="leather", line=True):
    """(x0, y0) = pommel, (x1, y1) = tip"""
    ux, uy = T.unit(x0, y0, x1, y1); px, py = -uy, ux
    L = math.hypot(x1 - x0, y1 - y0)
    gx, gy = x0 + ux * L * 0.24, y0 + uy * L * 0.24
    ic.add(capsule(x0, y0, gx, gy, w * 0.55), grip, mode="cyl", axis=(ux, uy), base=0.55, pattern=hstripes(2.5, 0.08))
    tipb = (x1 - ux * w * 2.2, y1 - uy * w * 2.2)
    bl = poly([(gx + px * w, gy + py * w), (tipb[0] + px * w * 0.9, tipb[1] + py * w * 0.9), (x1, y1), (tipb[0] - px * w * 0.9, tipb[1] - py * w * 0.9),
               (gx - px * w, gy - py * w)])
    ic.add(bl, blade, base=0.62, grad=0.6, bevel=1.0, line=line)
    ic.add(poly([(gx + px * w * 0.1, gy + py * w * 0.1), (tipb[0] + px * w * 0.1, tipb[1] + py * w * 0.1), (x1, y1), (tipb[0] - px * w * 0.8, tipb[1] - py * w * 0.8),
                 (gx - px * w * 0.8, gy - py * w * 0.8)]), blade, base=0.9, grad=0.3, bevel=0, cast=False)
    ic.add(capsule(gx + px * w * 2.6, gy + py * w * 2.6, gx - px * w * 2.6, gy - py * w * 2.6, w * 0.62), hilt, base=0.65, grad=0.5, bevel=0.8,
           line=True)
    ic.add(circle(x0, y0, w * 0.8), hilt, mode="sphere", base=0.65, line=True)


def dagger(ic, x0, y0, x1, y1, w=2.6, blade="steel", hilt="dark"):
    sword(ic, x0, y0, x1, y1, w=w, blade=blade, hilt=hilt, grip="leather")


def kunai(ic, x0, y0, x1, y1, s=1.0, blade="steel"):
    """(x0, y0) = the ring end, (x1, y1) = the tip"""
    ux, uy = T.unit(x0, y0, x1, y1); px, py = -uy, ux
    L = math.hypot(x1 - x0, y1 - y0)
    bx, by = x0 + ux * L * 0.42, y0 + uy * L * 0.42
    ic.add(ering(x0, y0, 3.6 * s, 3.6 * s, 2 * s, 2 * s), blade, base=0.6, bevel=0, line=True)
    ic.add(capsule(x0 + ux * 3 * s, y0 + uy * 3 * s, bx, by, 1.6 * s), "leather", mode="cyl", axis=(ux, uy), base=0.5, pattern=hstripes(2.2, 0.1))
    mx, my = bx + ux * L * 0.18, by + uy * L * 0.18
    ic.add(poly([(bx, by), (mx + px * 5 * s, my + py * 5 * s), (x1, y1), (mx - px * 5 * s, my - py * 5 * s)]), blade, base=0.62, grad=0.6, bevel=1.0,
           line=True)
    ic.add(poly([(bx, by), (mx + px * 5 * s, my + py * 5 * s), (x1, y1)]), blade, base=0.88, bevel=0, cast=False)


def axe(ic, hx0, hy0, cx, cy, s=1.0, double=False, head="steel", handle="wood"):
    """handle from (hx0, hy0) to the head at (cx, cy); the blade opens to the handle's left (and right when double)"""
    ux, uy = T.unit(hx0, hy0, cx, cy); px, py = -uy, ux
    ic.add(capsule(hx0, hy0, cx + ux * 3 * s, cy + uy * 3 * s, 2.3 * s), handle, mode="cyl", axis=(ux, uy), base=0.58, pattern=hstripes(5, 0.05))
    for sg in ((1, -1) if double else (1,)):
        q = lambda a, b: (cx + px * a * s * sg + ux * b * s, cy + py * a * s * sg + uy * b * s)
        ic.add(poly([q(1.5, -5), q(1.5, 5), q(8, 8), q(14, 11), q(16, 4), q(16.5, 0), q(16, -4), q(14, -11), q(8, -8)]), head, base=0.6, grad=0.6,
               bevel=1.1, line=True)
        ic.add(poly([q(14, 11), q(16, 4), q(16.5, 0), q(16, -4), q(14, -11), q(14.5, -4), q(15, 0), q(14.5, 4)]), head, base=0.95, bevel=0, cast=False)
    ic.add(rrect(cx - 3 * s, cy - 3 * s, cx + 3 * s, cy + 3 * s, 1 * s), "steel", base=0.45, line=True)


def round_shield(ic, cx, cy, r, face="wood", rim="steel", boss="steel"):
    ic.add(circle(cx, cy, r), rim, mode="sphere", base=0.55, line=True)
    ic.add(circle(cx, cy, r * 0.82), face, base=0.58, grad=0.6, bevel=0.8,
           pattern=lambda x, y: -0.08 if int((x - cx + r) // (r * 0.4)) % 2 else 0.0)
    ic.add(circle(cx, cy, r * 0.3), boss, mode="sphere", base=0.7, line=True)


def tower_shield(ic, cx, cy, s=1.0, field="cls_Berserker", trim="gold"):
    """the Warrior bulwark shield: tall, rounded top, gold trim + a vertical bar"""
    outer = union(rrect(cx - 12 * s, cy - 17 * s, cx + 12 * s, cy + 12 * s, 4 * s), poly([(cx - 12 * s, cy + 10 * s), (cx + 12 * s, cy + 10 * s), (cx, cy + 20 * s)]))
    inner = union(rrect(cx - 9 * s, cy - 14 * s, cx + 9 * s, cy + 10 * s, 3 * s), poly([(cx - 9 * s, cy + 9 * s), (cx + 9 * s, cy + 9 * s), (cx, cy + 16.5 * s)]))
    ic.add(outer, trim, base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(inner, field, base=0.55, grad=0.6, bevel=0.8)
    ic.add(inter(inner, rect(cx - 2 * s, cy - 15 * s, cx + 2 * s, cy + 18 * s)), trim, base=0.7, bevel=0.6)
    ic.add(circle(cx, cy - 2 * s, 3.6 * s), trim, mode="sphere", base=0.7, line=True)
    return outer


def heater(ic, cx, cy, s=1.0, field="steel", trim="gold"):
    sh = shield(ic, cx, cy, s * 1.1, pal=trim)
    ic.add(union(rrect(cx - 7.5 * s, cy - 8.5 * s, cx + 7.5 * s, cy + 1 * s, 1.5 * s), poly([(cx - 7.5 * s, cy), (cx + 7.5 * s, cy), (cx, cy + 10.5 * s)])),
           field, base=0.6, grad=0.6, bevel=0.8)
    return sh


def helm(ic, cx, cy, s=1.0, pal="steel", crest="cls_Warrior"):
    """a closed great helm (Guardian's Oath)"""
    ic.add(capsule(cx, cy - 16 * s, cx, cy - 10 * s, 2.6 * s), crest, base=0.6, grad=0.5, line=True)
    dome = union(inter(circle(cx, cy - 2 * s, 13 * s), rect(cx - 14 * s, cy - 16 * s, cx + 14 * s, cy - 2 * s)), rrect(cx - 13 * s, cy - 3 * s, cx + 13 * s, cy + 13 * s, 3 * s))
    ic.add(dome, pal, base=0.58, grad=0.6, bevel=1.1, line=True)
    ic.add(rect(cx - 10 * s, cy - 1 * s, cx + 10 * s, cy + 2 * s), "navy", base=0.15, bevel=0, cast=False, rim=False)
    ic.add(rect(cx - 1.2 * s, cy + 2 * s, cx + 1.2 * s, cy + 12 * s), pal, base=0.85, bevel=0, cast=False)
    for k in range(3):
        ic.add(circle(cx - 6 * s, cy + (5 + 3 * k) * s, 0.9 * s), "navy", base=0.2, bevel=0, cast=False, rim=False)
        ic.add(circle(cx + 6 * s, cy + (5 + 3 * k) * s, 0.9 * s), "navy", base=0.2, bevel=0, cast=False, rim=False)


def banner(ic, px_, top, s=1.0, cloth="cls_Berserker", trim="gold", emblem=None, pole="wood"):
    """a war banner: a pole at x = px_, the cloth hanging to its right with a swallowtail"""
    ic.add(capsule(px_, top, px_, top + 50 * s, 1.9 * s), pole, mode="cyl", axis=(0, 1), base=0.58)
    ic.add(circle(px_, top - 1.5 * s, 2.8 * s), trim, mode="sphere", base=0.7, line=True)
    ic.add(capsule(px_ - 2 * s, top + 4 * s, px_ + 24 * s, top + 4 * s, 1.5 * s), trim, base=0.6, line=True)
    cl = poly([(px_ + 1 * s, top + 5 * s), (px_ + 23 * s, top + 5 * s), (px_ + 23 * s, top + 33 * s), (px_ + 12 * s, top + 26 * s), (px_ + 1 * s, top + 33 * s)])
    ic.add(cl, cloth, base=0.56, grad=0.6, bevel=0.9, line=True, pattern=lambda x, y: 0.06 * math.sin((x - px_) * 0.5))
    ic.add(inter(cl, rect(px_, top + 5 * s, px_ + 24 * s, top + 8 * s)), trim, base=0.65, bevel=0)
    if emblem:
        emblem(ic, px_ + 12 * s, top + 16 * s, 0.55 * s)


def crossed_axes_emblem(ic, cx, cy, s):
    for sg in (1, -1):
        ic.add(capsule(cx - 8 * s * sg, cy + 8 * s, cx + 8 * s * sg, cy - 8 * s, 1.4 * s), "bone", base=0.8, bevel=0, cast=False)
        ic.add(circle(cx + 7 * s * sg, cy - 7 * s, 4 * s), "bone", base=0.9, bevel=0, cast=False)


def cross_emblem(ic, cx, cy, s):
    ic.add(union(rect(cx - 2.4 * s, cy - 9 * s, cx + 2.4 * s, cy + 9 * s), rect(cx - 8 * s, cy - 3.5 * s, cx + 8 * s, cy + 1 * s)), "gold", base=0.8,
           bevel=0, cast=False)


def chain(ic, x0, y0, x1, y1, n=4, s=1.0, pal="steel", hook=True):
    ux, uy = T.unit(x0, y0, x1, y1)
    ang = math.degrees(math.atan2(uy, ux))
    for k in range(n):
        t = k / float(max(1, n - 1))
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        a = ang + (0 if k % 2 == 0 else 0)
        ra, rb = 6.6 * s, (4.6 if k % 2 == 0 else 2.6) * s
        ic.add(diff(rot_ellipse(x, y, ra, rb, a), rot_ellipse(x, y, ra - 2.8 * s, max(0.7, rb - 2.6 * s), a)), pal, base=0.6 + 0.1 * (k % 2), grad=0.5,
               bevel=0.9, line=True)
    if hook:
        hx_, hy_ = x1 + ux * 8 * s, y1 + uy * 8 * s
        arcp(ic, hx_, hy_ + 3 * s, 5 * s, 180, 400, 2.6 * s, pal, base=0.7, line=True)
        ic.add(poly([(hx_ + 5 * s * math.cos(math.radians(400)), hy_ + 3 * s + 5 * s * math.sin(math.radians(400))),
                     (hx_ + 8 * s, hy_ - 1 * s), (hx_ + 3 * s, hy_ + 1 * s)]), pal, base=0.85, bevel=0, line=True)


def bull_skull(ic, cx, cy, s=1.0, glow="#ff7a7a"):
    """Enrage: a horned bull skull with burning eyes"""
    for sg in (1, -1):
        horn = poly([(cx + 6 * s * sg, cy - 6 * s), (cx + 16 * s * sg, cy - 9 * s), (cx + 21 * s * sg, cy - 18 * s), (cx + 19 * s * sg, cy - 8 * s),
                     (cx + 10 * s * sg, cy - 1 * s)])
        ic.add(horn, "bone", base=0.66, grad=0.6, bevel=0.9, line=True)
    sk = union(rrect(cx - 9 * s, cy - 9 * s, cx + 9 * s, cy + 4 * s, 4 * s), poly([(cx - 7 * s, cy + 2 * s), (cx + 7 * s, cy + 2 * s), (cx + 4 * s, cy + 14 * s),
                                                                               (cx - 4 * s, cy + 14 * s)]))
    ic.add(sk, "bone", base=0.62, grad=0.6, bevel=1.0, line=True)
    for sg in (1, -1):
        ic.add(poly([(cx + 2 * s * sg, cy - 3 * s), (cx + 7.5 * s * sg, cy - 5 * s), (cx + 6 * s * sg, cy + 1 * s)]), "blood", base=0.85, bevel=0,
               cast=False, rim=False)
    ic.add(circle(cx - 2 * s, cy + 11 * s, 1.2 * s), "navy", base=0.2, bevel=0, cast=False, rim=False)
    ic.add(circle(cx + 2 * s, cy + 11 * s, 1.2 * s), "navy", base=0.2, bevel=0, cast=False, rim=False)


def claws(ic, cx, cy, s=1.0, pal="blood", n=3):
    """three red slash marks (Blood Frenzy)"""
    for k in range(n):
        dx = (k - (n - 1) / 2.0) * 8 * s
        ic.add(poly([(cx + dx + 8 * s, cy - 16 * s), (cx + dx + 10.5 * s, cy - 14 * s), (cx + dx - 6 * s, cy + 16 * s), (cx + dx - 8.5 * s, cy + 15 * s)]),
               pal, base=0.66, grad=0.6, bevel=0.7, line=True)


def whirl(ic, cx, cy, R, pal, w=3.0, n=3, base=0.72):
    for k in range(n):
        a0 = k * 360.0 / n
        arcp(ic, cx, cy, R, a0, a0 + 360.0 / n * 0.62, w, pal, base=base, line=True)
        a = math.radians(a0 + 360.0 / n * 0.62)
        ex, ey = cx + R * math.cos(a), cy + R * math.sin(a)
        ic.add(circle(ex, ey, w * 0.55), pal, base=base + 0.15, bevel=0, cast=False)


def ground(ic, y0, x0=4, x1=60, pal="rock", crack=True):
    ic.add(rect(x0, y0, x1, y0 + 9), pal, base=0.45, grad=0.5, pattern=hstripes(3.5, 0.06))
    if crack:
        cx = (x0 + x1) / 2.0
        ic.add(poly([(cx - 2, y0), (cx + 3, y0), (cx + 1, y0 + 4), (cx + 5, y0 + 9), (cx - 1, y0 + 9), (cx - 0.5, y0 + 4.5), (cx - 4, y0 + 3)]), "acc_damage",
               base=0.8, bevel=0, cast=False)


def crescent(ic, cx, cy, R, pal, ang=0.0, thick=0.42, base=0.7):
    """a crescent arc (Rift Cleave / Arcane Breach) opening toward ang"""
    a = math.radians(ang)
    off = R * thick
    ic.add(diff(circle(cx, cy, R), circle(cx + math.cos(a) * off, cy + math.sin(a) * off, R * 0.9)), pal, base=base, grad=0.6, bevel=0.9, line=True)


def spiral(ic, cx, cy, R, pal, w=3.0, turns=1.4, base=0.72, steps=40):
    pts = []
    for k in range(steps + 1):
        t = k / float(steps)
        a = math.radians(-90 + 360 * turns * t)
        r = R * (0.2 + 0.8 * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for k in range(steps):
        ic.add(capsule(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], w * (0.6 + 0.4 * k / steps) / 2), pal, base=base + 0.15 * k / steps, bevel=0,
               cast=False, line=(k % 4 == 0))


def swirl_form(ic, cx, cy, s=1.0):
    """Flowing Form: a saffron + teal two-armed swirl round an orb"""
    for k, pal in enumerate(("cls_Monk", "rift")):
        for j in range(18):
            t0, t1 = j / 18.0, (j + 1) / 18.0
            a0 = math.radians(k * 180 + 300 * t0); a1 = math.radians(k * 180 + 300 * t1)
            r0, r1 = (6 + 14 * t0) * s, (6 + 14 * t1) * s
            ic.add(capsule(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0), cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), (1.4 + 2.2 * (1 - t0)) * s), pal,
                   base=0.62 + 0.25 * (1 - t0), bevel=0, cast=False)
    ic.add(circle(cx, cy, 5 * s), "cls_Monk", mode="sphere", base=0.75, line=True)


def palm(ic, cx, cy, s=1.0, skin="linen", wrap="cls_Monk"):
    """an open palm facing out (Palm Strike), wrapped wrist"""
    for k, (dx, h) in enumerate(((-7.5, 13), (-2.5, 16), (2.5, 15.5), (7.5, 12))):
        ic.add(capsule(cx + dx * s, cy - 3 * s, cx + dx * s, cy - (3 + h) * s, 2.4 * s), skin, base=0.62 - 0.03 * k, grad=0.5, bevel=0.8, line=True)
    ic.add(capsule(cx - 10 * s, cy + 4 * s, cx - 16 * s, cy - 5 * s, 2.6 * s), skin, base=0.6, grad=0.5, line=True)
    ic.add(rrect(cx - 10.5 * s, cy - 6 * s, cx + 10.5 * s, cy + 10 * s, 4 * s), skin, base=0.64, grad=0.6, bevel=1.0, line=True)
    ic.add(rrect(cx - 8 * s, cy + 9 * s, cx + 8 * s, cy + 19 * s, 1.5 * s), wrap, base=0.55, grad=0.5, line=True, pattern=hstripes(3 * s, 0.12))


def fist(ic, cx, cy, s=1.0, skin="linen", wrap="cls_Monk"):
    """a closed fist punching forward, knuckles wrapped"""
    ic.add(rrect(cx - 11 * s, cy - 9 * s, cx + 11 * s, cy + 9 * s, 4 * s), skin, base=0.62, grad=0.6, bevel=1.0, line=True)
    for k in range(4):
        x = cx - 8.2 * s + k * 5.5 * s
        ic.add(rrect(x - 2.6 * s, cy - 9 * s, x + 2.6 * s, cy - 1 * s, 1.8 * s), skin, base=0.74, grad=0.4, bevel=0.6, line=True)
    ic.add(rrect(cx - 11 * s, cy + 1 * s, cx + 3 * s, cy + 6 * s, 2.4 * s), skin, base=0.5, grad=0.4, line=True)
    ic.add(rect(cx - 11 * s, cy - 6.5 * s, cx + 11 * s, cy - 4 * s), wrap, base=0.6, bevel=0, cast=False)
    ic.add(rrect(cx - 9 * s, cy + 8 * s, cx + 9 * s, cy + 16 * s, 1.5 * s), wrap, base=0.52, grad=0.5, line=True, pattern=hstripes(2.8 * s, 0.12))


def foot(ic, cx, cy, s=1.0, skin="linen", wrap="cls_Monk"):
    """a wrapped kicking foot pointing right (Cyclone Kick)"""
    ic.add(rrect(cx - 14 * s, cy - 16 * s, cx - 4 * s, cy + 2 * s, 3 * s), wrap, base=0.55, grad=0.5, line=True, pattern=hstripes(3 * s, 0.12))
    sole = union(rrect(cx - 14 * s, cy - 2 * s, cx + 14 * s, cy + 8 * s, 4.5 * s), circle(cx + 12 * s, cy + 2.5 * s, 5.5 * s))
    ic.add(sole, skin, base=0.62, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(cx - 4 * s, cy - 1.5 * s, cx + 4 * s, cy + 8 * s), wrap, base=0.6, bevel=0, cast=False, pattern=hstripes(2.5 * s, 0.1))


def droplet(ic, cx, cy, s=1.0, pal="water"):
    ic.add(union(circle(cx, cy + 4 * s, 9 * s), poly([(cx - 8.6 * s, cy + 1.5 * s), (cx, cy - 14 * s), (cx + 8.6 * s, cy + 1.5 * s)])), pal, base=0.6,
           grad=0.6, bevel=1.0, line=True)
    ic.add(rot_ellipse(cx - 3.5 * s, cy + 2 * s, 1.6 * s, 3.4 * s, 20), pal, base=1.0, bevel=0, cast=False, rim=False)


def ripples(ic, cx, cy, s=1.0, pal="water"):
    for R, b in ((22, 0.45), (15, 0.62)):
        ic.add(ering(cx, cy, R * s, R * 0.32 * s, (R - 2.6) * s, (R - 2.6) * 0.32 * s), pal, base=b, bevel=0, line=True)


def still_water(ic, cx, cy, s=1.0):
    ripples(ic, cx, cy + 14 * s, s)
    droplet(ic, cx, cy - 2 * s, 0.95 * s)


def hood(ic, cx, cy, s=1.0, pal="cls_Assassin", mask="shadow"):
    """the Assassin's beak hood with a face mask"""
    ic.add(poly([(cx - 17 * s, cy + 18 * s), (cx - 14 * s, cy - 2 * s), (cx - 6 * s, cy - 15 * s), (cx + 1 * s, cy - 19 * s), (cx + 8 * s, cy - 14 * s),
                 (cx + 15 * s, cy - 1 * s), (cx + 17 * s, cy + 18 * s)]), pal, base=0.5, grad=0.6, bevel=1.0, line=True)
    face = union(ellipse(cx, cy + 3 * s, 8.5 * s, 10 * s), poly([(cx - 4 * s, cy - 8 * s), (cx + 1 * s, cy - 13 * s), (cx + 5 * s, cy - 6 * s)]))
    ic.add(face, "dark", base=0.25, bevel=0, cast=False)
    ic.add(inter(ellipse(cx, cy + 3 * s, 8.5 * s, 10 * s), rect(cx - 9 * s, cy + 4 * s, cx + 9 * s, cy + 14 * s)), mask, base=0.45, grad=0.4, bevel=0.6)
    ic.add(rect(cx - 5 * s, cy + 0 * s, cx - 1.5 * s, cy + 1.6 * s), "acc_mod" if False else pal, base=0.98, bevel=0, cast=False, rim=False)
    ic.add(rect(cx + 1.5 * s, cy + 0 * s, cx + 5 * s, cy + 1.6 * s), pal, base=0.98, bevel=0, cast=False, rim=False)


def flask(ic, cx, cy, s=1.0, liquid="poison", glass="glass"):
    ic.add(rect(cx - 3 * s, cy - 16 * s, cx + 3 * s, cy - 11 * s), "wood", base=0.55, line=True)
    body = union(circle(cx, cy + 3 * s, 11 * s), rect(cx - 4 * s, cy - 12 * s, cx + 4 * s, cy - 4 * s))
    ic.add(body, glass, base=0.6, grad=0.5, bevel=0.8, line=True)
    ic.add(inter(circle(cx, cy + 3 * s, 9.2 * s), rect(cx - 10 * s, cy - 1 * s, cx + 10 * s, cy + 13 * s)), liquid, base=0.62, grad=0.6, bevel=0.6)
    ic.add(circle(cx - 3 * s, cy + 4 * s, 2 * s), liquid, base=0.95, bevel=0, cast=False, rim=False)
    ic.add(rot_ellipse(cx - 5.5 * s, cy - 2 * s, 1.2 * s, 3 * s, 30), glass, base=1.0, bevel=0, cast=False, rim=False)


def cloud(ic, cx, cy, s=1.0, pal="poison", base=0.6, line=True):
    sh = union(circle(cx - 8 * s, cy + 2 * s, 7 * s), circle(cx, cy - 3 * s, 9 * s), circle(cx + 9 * s, cy + 1 * s, 7.5 * s),
               rrect(cx - 14 * s, cy + 1 * s, cx + 15 * s, cy + 9 * s, 4 * s))
    ic.add(sh, pal, base=base, grad=0.6, bevel=1.0, line=line)
    return sh


def crown(ic, cx, cy, s=1.0, pal="gold"):
    pts = [(-14, 8), (-14, -6), (-8, 1), (-4, -10), (0, -2), (4, -10), (8, 1), (14, -6), (14, 8)]
    ic.add(poly([(cx + x * s, cy + y * s) for x, y in pts]), pal, base=0.62, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(cx - 14 * s, cy + 4 * s, cx + 14 * s, cy + 8 * s), pal, base=0.45, bevel=0, cast=False)
    for (x, p) in ((-7, "ruby"), (0, "emerald"), (7, "ruby")):
        ic.add(circle(cx + x * s, cy + 6 * s, 1.6 * s), p, mode="sphere", base=0.75)


def clone(ic, cx, cy, s=1.0, pal="shadow", base=0.5):
    """a shadow clone: a dark hooded silhouette"""
    sh = union(poly([(cx - 10 * s, cy + 16 * s), (cx - 8 * s, cy - 2 * s), (cx - 3 * s, cy - 13 * s), (cx + 1 * s, cy - 16 * s), (cx + 5 * s, cy - 12 * s),
                     (cx + 9 * s, cy - 1 * s), (cx + 10 * s, cy + 16 * s)]))
    ic.add(sh, pal, base=base, grad=0.6, bevel=0.9, line=True)
    ic.add(rect(cx - 4 * s, cy - 5 * s, cx - 1 * s, cy - 3.8 * s), "cls_Assassin", base=0.98, bevel=0, cast=False, rim=False)
    ic.add(rect(cx + 1 * s, cy - 5 * s, cx + 4 * s, cy - 3.8 * s), "cls_Assassin", base=0.98, bevel=0, cast=False, rim=False)


def bow(ic, cx, cy, s=1.0, wood="wood", string="cream", nock=True):
    """a recurve bow, grip at (cx, cy), opening to the right"""
    arcp(ic, cx + 14 * s, cy, 18 * s, 128, 232, 3.6 * s, wood, base=0.62, line=True, cast=True)
    t = math.radians(128); b = math.radians(232)
    tx, ty = cx + 14 * s + 18 * s * math.cos(t), cy + 18 * s * math.sin(t)
    bx, by = cx + 14 * s + 18 * s * math.cos(b), cy + 18 * s * math.sin(b)
    ic.add(capsule(tx, ty, bx, by, 0.7 * s), string, base=0.7, bevel=0, cast=False)
    ic.add(rrect(cx - 5.5 * s, cy - 4 * s, cx - 1 * s, cy + 4 * s, 1 * s), "leather", base=0.55, line=True)
    return (tx, ty), (bx, by)


def arrow_shaft(ic, x0, y0, x1, y1, s=1.0, head="steel", shaft="wood", fletch="cls_Archer"):
    """an arrow: fletching at (x0, y0), point at (x1, y1)"""
    ux, uy = T.unit(x0, y0, x1, y1); px, py = -uy, ux
    ic.add(capsule(x0, y0, x1 - ux * 5 * s, y1 - uy * 5 * s, 1.1 * s), shaft, base=0.6, bevel=0)
    for sg in (1, -1):
        ic.add(poly([(x0, y0), (x0 + ux * 7 * s, y0 + uy * 7 * s), (x0 + ux * 3 * s + px * 4 * s * sg, y0 + uy * 3 * s + py * 4 * s * sg),
                     (x0 - ux * 1.5 * s + px * 4 * s * sg, y0 - uy * 1.5 * s + py * 4 * s * sg)]), fletch, base=0.62, grad=0.4, bevel=0.6, line=True)
    ic.add(poly([(x1, y1), (x1 - ux * 7 * s + px * 3.6 * s, y1 - uy * 7 * s + py * 3.6 * s), (x1 - ux * 5 * s, y1 - uy * 5 * s),
                 (x1 - ux * 7 * s - px * 3.6 * s, y1 - uy * 7 * s - py * 3.6 * s)]), head, base=0.7, grad=0.6, bevel=0.8, line=True)


def net(ic, cx, cy, R, pal="bronze"):
    """a round rope net with weights"""
    disc_ = circle(cx, cy, R)
    holes = Shape(lambda x, y: abs(((x - cx) + (y - cy)) % 8.0 - 4.0) < 2.6 and abs(((x - cx) - (y - cy)) % 8.0 - 4.0) < 2.6, disc_.bb)
    ic.add(diff(disc_, holes), pal, base=0.62, grad=0.5, bevel=0.6, line=True)
    ic.add(ering(cx, cy, R, R, R - 2.2, R - 2.2), pal, base=0.5, bevel=0, line=True)
    for a in (-45, 45, 135, 225):
        ic.add(circle(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)), 3), "steel", mode="sphere", base=0.6, line=True)


def bomb(ic, cx, cy, r, pal="dark"):
    ic.add(circle(cx, cy, r), pal, mode="sphere", base=0.7, line=True)
    ic.add(rect(cx - 2.5, cy - r - 3, cx + 2.5, cy - r + 1), "steel", base=0.6, line=True)
    ic.add(capsule(cx, cy - r - 3, cx + 4, cy - r - 8, 0.9), "cream", base=0.5, bevel=0)


def meteor(ic, cx, cy, s=1.0):
    """a burning rock diving to the lower left with a fire tail"""
    for k, (w, b) in enumerate(((9, 0.5), (6, 0.75), (3.4, 0.95))):
        ic.add(poly([(cx + 4 * s, cy - 6 * s - w * 0.2 * s), (cx + 24 * s, cy - 24 * s), (cx + 6 * s + w * 0.3 * s, cy + 4 * s)]) if k == 0 else
               capsule(cx + 3 * s, cy - 3 * s, cx + (22 - 4 * k) * s, cy - (22 - 4 * k) * s, w * s * 0.6), "flame", base=b, bevel=0, cast=False)
    ic.add(poly([(cx - 10 * s, cy - 2 * s), (cx - 5 * s, cy - 10 * s), (cx + 5 * s, cy - 10 * s), (cx + 10 * s, cy - 2 * s), (cx + 7 * s, cy + 8 * s),
                 (cx - 4 * s, cy + 10 * s)]), "rock", base=0.6, grad=0.6, bevel=1.1, line=True)
    ic.add(circle(cx - 2 * s, cy + 1 * s, 2.5 * s), "flame", base=0.85, bevel=0, cast=False, rim=False)
    ic.add(circle(cx + 4 * s, cy - 4 * s, 1.6 * s), "flame", base=0.75, bevel=0, cast=False, rim=False)


def dome(ic, cx, by, R, pal="mana"):
    d = inter(circle(cx, by, R), rect(cx - R - 1, by - R - 1, cx + R + 1, by))
    ic.add(d, pal, base=0.5, grad=0.6, bevel=1.0, line=True,
           pattern=lambda x, y: 0.18 if (abs(((x - cx) * 0.5 + (y - by)) % 8) < 1.0 or abs(((x - cx) * 0.5 - (y - by)) % 8) < 1.0) else 0.0)
    ic.add(rrect(cx - R - 2, by - 1, cx + R + 2, by + 3, 1.5), "arcane", base=0.55, line=True)
    ic.add(rot_ellipse(cx - R * 0.45, by - R * 0.55, 2, 5, 40), pal, base=1.0, bevel=0, cast=False, rim=False)


def snowflake(ic, cx, cy, R, pal="ice"):
    for k in range(6):
        a = math.radians(-90 + k * 60)
        ex, ey = cx + R * math.cos(a), cy + R * math.sin(a)
        ic.add(capsule(cx, cy, ex, ey, R * 0.1), pal, base=0.75, grad=0.4, bevel=0.6, line=True)
        for t, l in ((0.55, 0.34), (0.8, 0.22)):
            mx, my = cx + R * t * math.cos(a), cy + R * t * math.sin(a)
            for d in (-50, 50):
                b = a + math.radians(d)
                ic.add(capsule(mx, my, mx + R * l * math.cos(b), my + R * l * math.sin(b), R * 0.07), pal, base=0.85, bevel=0, line=True)
    ic.add(poly(star_pts(cx, cy, R * 0.3, R * 0.17, 6)), pal, base=0.95, bevel=0.6, line=True)


def star5(ic, cx, cy, R, pal="holy", base=0.75, line=True):
    ic.add(poly(star_pts(cx, cy, R, R * 0.45, 5)), pal, base=base, grad=0.5, bevel=0.9, line=line)


def falling_star(ic, cx, cy, R, pal="feather", trail="arcane"):
    ic.add(capsule(cx + R * 0.6, cy - R * 0.6, cx + R * 2.2, cy - R * 2.2, R * 0.35), trail, base=0.6, bevel=0, cast=False)
    star5(ic, cx, cy, R, pal)


def beam(ic, x0, y0, x1, y1, w=5.0, pal="arcane"):
    ic.add(capsule(x0, y0, x1, y1, w), pal, base=0.6, grad=0.3, bevel=0, line=True)
    ic.add(capsule(x0, y0, x1, y1, w * 0.45), pal, base=1.0, bevel=0, cast=False)


def orb_staff(ic, x0, y0, x1, y1, orb="arcane", r=5.0):
    ic.add(capsule(x0, y0, x1, y1, 2.0), "wood", mode="cyl", axis=T.unit(x0, y0, x1, y1), base=0.58)
    ic.add(circle(x1, y1, r), orb, mode="sphere", base=0.75, line=True)


def wand(ic, x0, y0, x1, y1, tip="holy"):
    ic.add(capsule(x0, y0, x1, y1, 1.8), "wood", mode="cyl", axis=T.unit(x0, y0, x1, y1), base=0.6)
    star5(ic, x1, y1, 5.5, tip)


def holy_cross(ic, cx, cy, s=1.0, pal="holy"):
    ic.add(union(rrect(cx - 4 * s, cy - 16 * s, cx + 4 * s, cy + 16 * s, 1.5 * s), rrect(cx - 13 * s, cy - 7 * s, cx + 13 * s, cy + 1 * s, 1.5 * s)), pal,
           base=0.66, grad=0.6, bevel=1.1, line=True)
    ic.add(circle(cx, cy - 3 * s, 2.6 * s), pal, base=1.0, bevel=0, cast=False, rim=False)


def bubble(ic, cx, cy, R, pal="rift"):
    ic.add(ering(cx, cy, R, R, R - 3, R - 3), pal, base=0.66, bevel=0, line=True)
    ic.add(rot_ellipse(cx - R * 0.5, cy - R * 0.5, 2, R * 0.3, 45), pal, base=1.0, bevel=0, cast=False, rim=False)


def bubble_shield(ic, cx, cy, s=1.0):
    bubble(ic, cx, cy, 20 * s)
    heater(ic, cx, cy - 1 * s, 0.9 * s, field="rift", trim="holy")


def wings_halo(ic, cx, cy, s=1.0, pal="feather"):
    """Guardian Spirit: spread angel wings, a gold halo, a soul flame"""
    for sg in (1, -1):
        for k in range(4):
            a0 = math.radians(-150 + k * 28) if sg < 0 else math.radians(-30 - k * 28)
            L = (22 - k * 3.5) * s
            ex, ey = cx + 3 * s * sg + L * math.cos(a0), cy + L * math.sin(a0) * 0.75
            ic.add(capsule(cx + 3 * s * sg, cy + 1 * s, ex, ey, (3.6 - 0.3 * k) * s), pal, base=0.5 + 0.12 * k, grad=0.5, bevel=0.8, line=True)
    ic.add(ering(cx, cy - 13 * s, 7.5 * s, 2.8 * s, 5 * s, 1.3 * s), "holy", base=0.8, bevel=0, line=True)
    ic.add(union(circle(cx, cy + 4 * s, 5 * s), poly([(cx - 4.6 * s, cy + 3 * s), (cx, cy - 7 * s), (cx + 4.6 * s, cy + 3 * s)])), "rift", base=0.75, line=True)


def shrine(ic, cx, by, s=1.0, pal="holy"):
    """Sanctuary: a gold arch shrine on a glowing floor ring"""
    ic.add(ering(cx, by, 22 * s, 6 * s, 18 * s, 4 * s), pal, base=0.6, bevel=0, line=True)
    arch = diff(union(rrect(cx - 11 * s, by - 26 * s, cx + 11 * s, by, 9 * s), rect(cx - 11 * s, by - 14 * s, cx + 11 * s, by)),
                union(rrect(cx - 6 * s, by - 21 * s, cx + 6 * s, by + 1, 6 * s)))
    ic.add(arch, pal, base=0.6, grad=0.6, bevel=1.0, line=True)
    ic.add(rrect(cx - 6 * s, by - 21 * s, cx + 6 * s, by, 6 * s), pal, base=0.95, bevel=0, cast=False)


def mob_group(ic, pts, s=0.7, pal="rock"):
    for (x, y) in pts:
        g_mob(ic, x, y, s, pal)


def anchor(ic, cx, cy, s=1.0, pal="steel"):
    ic.add(ering(cx, cy - 16 * s, 4 * s, 4 * s, 2 * s, 2 * s), pal, base=0.6, bevel=0, line=True)
    ic.add(capsule(cx, cy - 12 * s, cx, cy + 14 * s, 2.4 * s), pal, mode="cyl", axis=(0, 1), base=0.58, line=True)
    ic.add(capsule(cx - 8 * s, cy - 7 * s, cx + 8 * s, cy - 7 * s, 1.8 * s), pal, base=0.6, line=True)
    arcp(ic, cx, cy + 2 * s, 13 * s, 20, 160, 3.2 * s, pal, base=0.62, line=True, cast=True)
    for sg in (1, -1):
        ex, ey = cx + 13 * s * math.cos(math.radians(90 - 70 * sg)), cy + 2 * s + 13 * s * math.sin(math.radians(90 - 70 * sg))
        ic.add(poly([(ex - 3.5 * s * sg, ey + 1 * s), (ex + 3 * s * sg, ey - 6 * s), (ex + 2 * s * sg, ey + 3 * s)]), pal, base=0.75, line=True)


def shock_rings(ic, cx, cy, s=1.0, cat="control", n=2):
    for k in range(n):
        R = (22 + 6 * k) * s
        arcp(ic, cx, cy, R, 200, 340, 2.4 * s, acc(cat), base=0.75 - 0.15 * k, line=True)


# ====================================================================== row helpers
def stem_of(key):
    """'Warrior.b1.r1a' -> 'B1R1a', 'Warrior.b1.r2.free' -> 'B1R2Free', 'Warrior.b1.r6' -> 'B1R6' (the Mining key scheme)"""
    return key.split(".", 1)[1].replace(".free", "Free").replace(".r", "R").replace("b", "B", 1).replace(".", "")


def R(key, cat, fn, shows):
    return (key, stem_of(key), cat, fn, shows)


def D(name, f):
    """a drawing from a lambda: D('IronSkin', lambda ic: (...))"""
    def g():
        ic = Icon(name)
        f(ic)
        return ic
    g.__name__ = name
    return g
