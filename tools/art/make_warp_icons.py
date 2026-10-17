#!/usr/bin/env python3
"""SkyWynn warp icons - one picture per warp theme for World > Teleport (DRAFT v1, round tp37).

Skyy (2026-10-17, docs/answered/world.md): "give players warp. put it in the teleports page ... (if posible i want a bunch of custom
icons we can set to a warp when making it. for mining fishing foraging farming and what not. probably 1 per zone.)"
Admins pick one of these per warp on the /warpadmin page (SkyyEssentials 0.1.14 stores the pick); SkyyMenu 0.3.37 ships them as the
icon-only items Skyy_Menu_Icon_Warp<Name> and draws a warp's tile with its pick (the old signpost = no pick). Zone homes (/sethome)
wear the Home icon.

Same family look as the approved art/menu-icons + art/menu-icons-2: this script REUSES tools/art/make_menu_icons.py (shape helpers,
Icon painter, palettes, PNG writer - imported, never edited). ORIGINAL pixels only; no game file is read.

Writes:
  art/warp-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_Warp<Name>.png   64 x 64 RGBA, hard alpha, 1 px dark outline
  art/warp-icons/sheet.png                                                   review sheet (1x checker / navy, 2x, 32 px, Teleport mock)
  art/warp-icons/manifest.json                                               icons (id, theme, file, bytes, sha256), palettes

Run:   python tools/art/make_warp_icons.py        (deterministic: two runs = same bytes; --check = build twice, compare, write nothing)
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M
from make_menu_icons import (Icon, circle, ellipse, rect, rrect, poly, capsule, union, diff, inter, ering, star_pts,
                             hstripes, hx, mix, png_bytes, Canvas, half, sha, rot_ellipse)

ROOT = M.ROOT
OUT = os.path.join(ROOT, "art", "warp-icons")
ICON_DIR_REL = M.ICON_DIR_REL
TWO_DIR = os.path.join(ROOT, "art", "menu-icons-2", ICON_DIR_REL)   # the approved Teleport icons (read for the mock only)

PALW = {
    "wheat":  ["#3e2a08", "#664610", "#946a18", "#c2942a", "#e2bc46", "#f4dc82", "#fdf2c2"],
    "bone":   ["#3a3226", "#5c5240", "#83775e", "#ab9f82", "#cdc4a8", "#e6dfc8", "#f6f2e4"],
    "ore":    ["#0d2638", "#14405e", "#1d6290", "#2a8ac0", "#4cb4e4", "#94dcf6", "#d2f2fc"],
    "flame":  ["#5a1a06", "#922e08", "#cc5410", "#f08a1e", "#ffbe46", "#ffe58a", "#fff4cf"],
    "ember":  ["#3c0a08", "#701410", "#a8201a", "#dc3a24", "#f86a3c", "#ffa070", "#ffd2b4"],
    "water":  ["#0a2034", "#10345a", "#18508a", "#2470b8", "#3c94dc", "#78bef0", "#bce2fa"],
}
for _k, _v in PALW.items():
    if _k not in M.PAL:
        M.PAL[_k] = _v
        M.PALC[_k] = [hx(c) for c in _v]
PAL_USED = dict((k, M.PAL[k]) for k in sorted(M.PAL))


def tufts(ic, y=55.0):
    ic.add(ellipse(32, y + 2, 25, 4.5), "grass", base=0.55, grad=0.5)


# ====================================================================== the icons (64 px grid, light from the top left)
def icon_mining():
    ic = Icon("WarpMining")
    rock = poly([(8, 58), (11, 46), (19, 39), (31, 36), (44, 38), (53, 45), (57, 58)])
    ic.add(rock, "stone", base=0.5, grad=0.6, pattern=hstripes(4.5, 0.08, 1))
    for (x, y, r, p) in ((20, 49, 3.2, "ore"), (30, 44, 2.4, "gold"), (41, 51, 3.0, "ore"), (48, 46, 2.0, "gold"), (27, 54, 2.0, "gold")):
        ic.add(circle(x, y, r), p, mode="sphere", base=0.62, line=True)
    ic.add(capsule(13, 47, 43, 17, 2.6), "wood", mode="cyl", axis=(1, -1), base=0.58, pattern=hstripes(5, 0.05))   # the handle
    head = union(capsule(27, 7, 43, 17, 3.4), capsule(43, 17, 55, 33, 3.4))                                        # the iron head
    ic.add(head, "steel", base=0.6, grad=0.6, bevel=1.1, line=True)
    ic.add(circle(43, 17, 3.6), "steel", mode="sphere", base=0.5)
    ic.sparkle(55, 9, 2)
    return ic


def icon_foraging():
    ic = Icon("WarpForaging")
    ic.add(circle(15, 18, 10), "green", mode="sphere", base=0.5)                                                    # leaves behind
    ic.add(circle(25, 12, 8), "green", mode="sphere", base=0.6)
    stump = rect(12, 34, 52, 56)
    ic.add(stump, "wood", mode="cyl", axis=(0, 1), base=0.5, pattern=hstripes(3.5, 0.07, 2))
    ic.add(ellipse(32, 56, 20, 4), "wood", base=0.35, bevel=0)
    ic.add(ellipse(32, 34, 20, 5.5), "cream", base=0.62, grad=0.5, bevel=0.8,
           pattern=lambda x, y: -0.14 if int(math.hypot((x - 32) / 1.0, (y - 34) * 3.6)) % 5 == 0 else 0)            # the rings
    ic.add(capsule(36, 36, 48, 8, 2.4), "wood", mode="cyl", axis=(0.4, -1), base=0.6)                               # the axe handle
    blade = poly([(43, 8), (56, 4), (60, 16), (53, 22), (45, 17)])
    ic.add(blade, "steel", base=0.62, grad=0.6, bevel=1.1, line=True)
    ic.add(poly([(55, 5), (60, 16), (58, 17), (54, 6)]), "steel", base=0.95, bevel=0, cast=False)                  # the edge
    ic.sparkle(8, 34, 1)
    return ic


def icon_farming():
    ic = Icon("WarpFarming")
    ic.add(ellipse(32, 55, 24, 6), "soil", base=0.5, grad=0.5)
    for k, (bx, tx, ty) in enumerate(((24, 14, 14), (32, 32, 8), (40, 50, 14), (28, 22, 18), (36, 42, 18))):
        ic.add(capsule(bx, 52, tx, ty + 10, 1.3), "green", base=0.55, bevel=0)                                      # stalks
        ic.add(rot_ellipse(tx, ty + 4, 4.0, 8.0, math.degrees(math.atan2(tx - bx, 52 - ty)) * 0.6), "wheat",
               base=0.62, grad=0.6, bevel=1.0, line=True,
               pattern=lambda x, y: -0.1 if int(y) % 3 == 0 else 0)                                                 # ears
    ic.add(rrect(23, 38, 41, 43, 2), "mahog", base=0.55, grad=0.4, line=True)                                     # the tie
    ic.sparkle(54, 30, 1)
    return ic


def icon_fishing():
    ic = Icon("WarpFishing")
    ic.add(ering(38, 55, 22, 6, 14, 3.5), "water", base=0.55, bevel=0)                                             # ripples
    ic.add(capsule(8, 58, 42, 6, 1.9), "wood", mode="cyl", axis=(0.55, -0.83), base=0.6)                           # the rod
    ic.add(circle(14, 49, 3.2), "steel", mode="sphere", base=0.55)                                                  # the reel
    ic.add(capsule(42, 6, 50, 28, 0.6), "cream", base=0.7, bevel=0, rim=False, cast=False)                         # the line
    fish = union(ellipse(42, 40, 13, 7), poly([(52, 40), (61, 32), (59, 40), (61, 48)]))
    ic.add(fish, "water", base=0.62, grad=0.6, bevel=1.1, line=True, pattern=lambda x, y: 0.12 if y > 42 else 0)
    ic.add(poly([(38, 33), (46, 30), (46, 35)]), "water", base=0.4, bevel=0)                                        # the fin
    ic.add(circle(34, 38.5, 1.6), "navy", base=0.1, bevel=0, cast=False)                                            # the eye
    ic.add(capsule(48, 28, 50, 33, 0.7), "steel", base=0.8, bevel=0, cast=False)                                    # the hook
    ic.sparkle(55, 12, 2)
    return ic


def sword(ic, x0, y0, x1, y1, pal="steel"):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; px, py = -uy, ux
    gx, gy = x0 + ux * L * 0.72, y0 + uy * L * 0.72
    ic.add(capsule(x0, y0, gx, gy, 2.6), pal, base=0.62, grad=0.6, bevel=1.0, line=True)                            # blade
    ic.add(capsule(gx + px * 8, gy + py * 8, gx - px * 8, gy - py * 8, 1.9), "gold", base=0.6, line=True)           # guard
    ic.add(capsule(gx, gy, x1 - ux * 2, y1 - uy * 2, 1.7), "leather", base=0.55)                                    # grip
    ic.add(circle(x1, y1, 2.8), "gold", mode="sphere", base=0.62)                                                   # pommel


def icon_combat():
    ic = Icon("WarpCombat")
    ic.add(union(rrect(18, 18, 46, 40, 6), poly([(18, 34), (46, 34), (32, 56)])), "red", base=0.5, grad=0.6, bevel=1.1, line=True)
    ic.add(diff(union(rrect(22, 22, 42, 38, 4), poly([(22, 34), (42, 34), (32, 50)])),
                union(rect(30.5, 22, 33.5, 52), rect(22, 31, 42, 34))), "red", base=0.68, bevel=0, cast=False)            # shield face
    sword(ic, 10, 8, 52, 54)
    sword(ic, 54, 8, 12, 54)
    return ic


def icon_dungeon():
    ic = Icon("WarpDungeon")
    def blocks(x, y):
        row = int(y // 6)
        return -0.12 if int(y) % 6 == 0 or int(x + (4 if row % 2 else 0)) % 8 == 0 else 0.0
    gate = diff(union(rect(8, 22, 56, 58), ellipse(32, 22, 24, 14)), union(rect(20, 34, 44, 59), ellipse(32, 34, 12, 12)))
    ic.add(union(rect(20, 34, 44, 58), ellipse(32, 34, 12, 12)), "navy", base=0.25, bevel=0, rim=False)             # the dark inside
    for bx in (24, 29, 34, 39):
        ic.add(rect(bx, 24, bx + 1.8, 58), "steel", base=0.5, bevel=0)                                              # portcullis
    ic.add(union(rect(20, 41, 44, 43), rect(20, 50, 44, 52)), "steel", base=0.45, bevel=0)
    ic.add(gate, "stone", base=0.52, grad=0.6, bevel=1.2, pattern=blocks, line=True)
    for tx in (13, 51):
        ic.add(rect(tx - 1.5, 34, tx + 1.5, 44), "wood", base=0.5, bevel=0)
        ic.add(union(ellipse(tx, 30, 3.6, 5.5), poly([(tx - 2, 27), (tx, 21), (tx + 2, 27)])), "flame", base=0.75, grad=0.7, bevel=0)
    return ic


def icon_boss():
    ic = Icon("WarpBoss")
    hl = poly([(19, 26), (9, 20), (5, 8), (11, 14), (18, 16), (24, 20)])
    hr = poly([(64 - x, y) for x, y in [(19, 26), (9, 20), (5, 8), (11, 14), (18, 16), (24, 20)]])
    ic.add(union(hl, hr), "bone", base=0.5, grad=0.7, bevel=1.0, line=True)                                          # horns
    skull = union(circle(32, 30, 16), rrect(23, 38, 41, 52, 3))
    ic.add(skull, "bone", base=0.62, grad=0.6, bevel=1.2, line=True)
    for ex in (25.5, 38.5):
        ic.add(ellipse(ex, 31, 4.6, 5.0), "navy", base=0.15, bevel=0, cast=False)
        ic.add(circle(ex, 31.5, 1.8), "ember", base=0.85, bevel=0, cast=False)                                       # glowing eyes
    ic.add(poly([(32, 36), (29.5, 41), (34.5, 41)]), "navy", base=0.2, bevel=0, cast=False)                         # nose
    for tx in (26, 30, 34, 38):
        ic.add(rect(tx - 1.2, 46, tx + 1.2, 52), "navy", base=0.25, bevel=0, cast=False)                             # teeth gaps
    ic.add(poly(star_pts(32, 9, 6, 2.6, 4)), "ember", base=0.7, bevel=0)
    return ic


def icon_shop():
    ic = Icon("WarpShop")
    ic.add(rect(12, 26, 15, 54), "wood", base=0.5)                                                                   # posts
    ic.add(rect(49, 26, 52, 54), "wood", base=0.45)
    ic.add(rect(9, 40, 55, 54), "wood", base=0.55, grad=0.5, pattern=hstripes(4.5, 0.08, 1), line=True)               # counter
    aw = poly([(6, 26), (12, 10), (52, 10), (58, 26)])
    ic.add(aw, "red", base=0.58, grad=0.5, bevel=1.0, line=True)
    ic.add(inter(aw, union(*[poly([(6 + 13 * k, 26), (12 + 10 * k, 10), (17 + 10 * k, 10), (12.5 + 13 * k, 26)]) for k in range(0, 4)])),
           "cream", base=0.66, grad=0.5, bevel=0)                                                                     # stripes
    ic.add(union(*[circle(9 + 6.5 * k, 26.5, 3.3) for k in range(8)]), "red", base=0.5, bevel=0.6)                   # scallops
    ic.add(circle(32, 44, 9), "gold", mode="sphere", base=0.62, line=True)                                          # the coin
    ic.add(ering(32, 44, 6.6, 6.6, 5.2, 5.2), "gold", base=0.35, bevel=0, cast=False)
    ic.add(rect(31, 39.5, 33, 48.5), "gold", base=0.35, bevel=0, cast=False)
    ic.sparkle(44, 36, 2)
    return ic


def icon_portal():
    ic = Icon("WarpPortal")
    ic.add(ellipse(32, 56, 22, 5), "stone", base=0.5, grad=0.6)
    def swirl(x, y):
        a = math.atan2(y - 30, x - 32); r = math.hypot((x - 32) / 13.0, (y - 30) / 19.0)
        return 0.25 + 0.55 * (0.5 + 0.5 * math.sin(a * 2 + r * 9))
    ic.add(ellipse(32, 30, 13, 19), "void", tfunc=swirl, bevel=0, rim=False)
    ic.add(ering(32, 30, 18, 24, 13, 19), "violet", mode="torus", base=0.6, torus=(32, 30, 18, 24, 13, 19), bevel=0, line=True)
    for (x, y) in ((32, 6), (14, 30), (50, 30)):
        ic.add(circle(x, y, 2.6), "magic", mode="sphere", base=0.7)
    ic.sparkle(53, 10, 2); ic.sparkle(10, 50, 1)
    return ic


def icon_home():
    ic = Icon("WarpHome")
    tufts(ic)
    ic.add(rect(41, 8, 47, 22), "stone", base=0.55, grad=0.5, line=True)                                            # chimney
    ic.add(rect(14, 30, 50, 56), "wood", base=0.58, grad=0.5, pattern=hstripes(4, 0.07, 1), line=True)              # walls
    ic.add(poly([(8, 32), (32, 10), (56, 32)]), "mahog", base=0.58, grad=0.6, bevel=1.1, line=True,
           pattern=lambda x, y: -0.1 if int(y) % 4 == 0 else 0)                                                      # roof
    ic.add(rrect(27, 40, 37, 56, 2), "mahog", base=0.3, bevel=0.6)                                                  # door
    ic.add(circle(35, 48.5, 0.9), "gold", base=0.8, bevel=0, cast=False)
    ic.add(rect(17.5, 36, 24.5, 43), "glass", base=0.62, grad=0.6, line=True)                                        # windows
    ic.add(rect(39.5, 36, 46.5, 43), "glass", base=0.62, grad=0.6, line=True)
    ic.add(union(circle(29.6, 21, 2.6), circle(34.4, 21, 2.6), poly([(27.2, 22), (36.8, 22), (32, 27)])), "ember", base=0.7, bevel=0)  # heart
    return ic


def icon_cave():
    ic = Icon("WarpCave")
    hill = union(ellipse(32, 46, 30, 22), rect(2, 46, 62, 58))
    ic.add(hill, "stone", base=0.5, grad=0.6, pattern=hstripes(5, 0.08, 3))
    ic.add(union(ellipse(32, 46, 14, 12), rect(18, 46, 46, 58)), "navy", base=0.2, bevel=0, rim=False, cast=False)   # the mouth
    for (x, l) in ((24, 7), (31, 5), (39, 8)):
        ic.add(poly([(x - 2.5, 35), (x + 2.5, 35), (x, 35 + l)]), "stone", base=0.62, bevel=0)                        # stalactites
    ic.add(ellipse(32, 25, 20, 5), "grass", base=0.6, grad=0.5)                                                      # grass cap
    for (x, y) in ((26, 52), (37, 50)):
        ic.add(circle(x, y, 2.2), "ore", mode="sphere", base=0.75)                                                   # glowing crystals
    ic.sparkle(52, 12, 2)
    return ic


# (Name, label, theme id saved with a warp, what it shows)
ICONS = [
    ("WarpMining",   "Mining",   "mining",   icon_mining,   "an iron pickaxe over a stone lump with blue + gold ore"),
    ("WarpForaging", "Foraging", "foraging", icon_foraging, "an axe in a tree stump with its rings, leaves behind"),
    ("WarpFarming",  "Farming",  "farming",  icon_farming,  "a tied bundle of golden wheat on a soil mound"),
    ("WarpFishing",  "Fishing",  "fishing",  icon_fishing,  "a rod with line + hook over a blue fish and ripples"),
    ("WarpCombat",   "Combat",   "combat",   icon_combat,   "two crossed swords over a red shield"),
    ("WarpDungeon",  "Dungeon",  "dungeon",  icon_dungeon,  "a stone gate with a dark portcullis and two torches"),
    ("WarpBoss",     "Boss",     "boss",     icon_boss,     "a horned bone skull with glowing red eyes"),
    ("WarpShop",     "Shop",     "shop",     icon_shop,     "a market stall with a striped red awning and a gold coin"),
    ("WarpPortal",   "Portal",   "portal",   icon_portal,   "a violet ring portal with a swirling void"),
    ("WarpCave",     "Cave",     "cave",     icon_cave,     "a grassy stone hill with a dark cave mouth and glowing crystals"),
    ("WarpHome",     "Home",     "home",     icon_home,     "a little wooden house with a chimney and a heart (also every /sethome home)"),
]
# themes that reuse an approved icon of art/menu-icons-2 (no new picture): theme -> item id
REUSED = [("warp", "Signpost", "Skyy_Menu_Icon_Warp", "the signpost (the default: a warp with no icon picked)"),
          ("hub", "Hub", "Skyy_Menu_Icon_Hub", "the hub gate"),
          ("spawn", "Spawn", "Skyy_Menu_Icon_Spawn", "the spawn portal")]


def icon_rel(name):
    return "%s/Skyy_Menu_Icon_%s.png" % (ICON_DIR_REL, name)


def build_icons():
    out = {}
    for t in ICONS:
        img = t[3]().render()
        out[t[0]] = (img, png_bytes(img))
    return out


BG = (24, 26, 38); PANEL = (34, 37, 52); INK = (226, 228, 236); DIM = (150, 156, 176); GOLDT = hx("#e0b060")
NAVY = (11, 21, 36); SLOT = (22, 38, 58); SLOTF = (44, 66, 96)


def two_icon(name):
    return P.read_png(open(os.path.join(TWO_DIR, "Skyy_Menu_Icon_%s.png" % name), "rb").read())


def build_sheet(icons):
    W, H = 1556, 1180
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "SKYWYNN WARP ICONS - DRAFT V1 (ROUND TP37)", GOLDT, 4)
    cv.text(24, 60, "SKYY 2026-10-17: \"A BUNCH OF CUSTOM ICONS WE CAN SET TO A WARP WHEN MAKING IT ... PROBABLY 1 PER ZONE.\"", DIM, 2)
    cv.text(24, 82, "ADMINS PICK ONE PER WARP ON /WARPADMIN. SAME FAMILY AS ART/MENU-ICONS: 64 PX, HARD ALPHA, LIGHT TOP LEFT, ORIGINAL PIXELS.", DIM, 2)
    y = 116
    CW, CH = 250, 196
    rows = (len(ICONS) + 5) // 6
    h = 40 + rows * CH
    cv.rect(16, y, W - 16, y + h, PANEL)
    cv.rect(16, y, W - 16, y + 3, GOLDT)
    cv.text(28, y + 13, "NEW ICONS  (EACH: 1X ON CHECKER, 1X ON NAVY, 2X)", GOLDT, 2)
    for k, t in enumerate(ICONS):
        cx = 28 + (k % 6) * CW; cy = y + 40 + (k // 6) * CH
        img = icons[t[0]][0]
        cv.checker(cx, cy, 72, 72, (52, 56, 74), (44, 48, 64))
        cv.blit(img, cx + 4, cy + 4, 1)
        cv.rect(cx, cy + 82, cx + 72, cy + 154, NAVY)
        cv.blit(img, cx + 4, cy + 86, 1)
        cv.checker(cx + 82, cy, 144, 144, (52, 56, 74), (44, 48, 64))
        cv.blit(img, cx + 90, cy + 8, 2)
        cv.text(cx, cy + 160, t[1].upper(), INK, 2)
        cv.text(cx, cy + 178, "THEME " + t[2].upper(), DIM, 1)
    y += h + 12
    cv.rect(16, y, W - 16, y + 120, PANEL)
    cv.text(28, y + 12, "ALSO IN THE PICK LIST (APPROVED ART/MENU-ICONS-2, NOT REDRAWN):", INK, 2)
    for k, (th, lab, iid, _w) in enumerate(REUSED):
        sx = 28 + k * 260
        cv.rect(sx, y + 38, sx + 72, y + 110, NAVY)
        cv.blit(two_icon(iid[len("Skyy_Menu_Icon_"):]), sx + 4, y + 42, 1)
        cv.text(sx + 82, y + 60, lab.upper(), INK, 2)
        cv.text(sx + 82, y + 82, "THEME " + th.upper(), DIM, 1)
    y += 132
    cv.rect(16, y, W - 16, y + 96, PANEL)
    cv.text(28, y + 12, "32 PX ON NAVY  +  64 PX ON LIGHT", INK, 2)
    for k, t in enumerate(ICONS):
        sx = 28 + k * 44
        cv.rect(sx, y + 40, sx + 40, y + 80, NAVY)
        cv.blit(half(icons[t[0]][0]), sx + 4, y + 44, 1)
    for k, t in enumerate(ICONS):
        sx = 540 + k * 70
        if sx + 66 > W - 16: break
        cv.rect(sx, y + 24, sx + 66, y + 90, (214, 218, 226))
        cv.blit(icons[t[0]][0], sx + 1, y + 25, 1)
    y += 108
    # a mock of the 5 x 5 Teleport grid: row 3 = the fixed spots, rows 4-5 = island homes, homes and warps
    cv.rect(16, y, W - 16, H - 16, NAVY)
    cv.text(28, y + 12, "TELEPORT PAGE MOCK (NOT THE REAL GAME SCREEN): MY ISLAND, HUB, SPAWN, THEN ISLAND HOMES, HOMES, WARPS", GOLDT, 2)
    grid = {11: two_icon("MyIsland"), 12: two_icon("Hub"), 13: two_icon("Spawn"), 15: two_icon("MyIsland"), 16: icons["WarpHome"][0],
            17: icons["WarpMining"][0], 18: icons["WarpFishing"][0], 19: icons["WarpFarming"][0], 20: icons["WarpForaging"][0],
            21: icons["WarpCombat"][0], 22: icons["WarpShop"][0], 23: two_icon("Warp"), 24: icons["WarpDungeon"][0]}
    gx, gy = (W - 5 * 108) // 2, y + 40
    # draw rows 3-5 only (rows 1-2 are empty slots)
    for s in range(10, 25):
        sx, sy = gx + (s % 5) * 108, gy + (s // 5 - 2) * 108
        cv.rect(sx, sy, sx + 100, sy + 100, SLOT); cv.frame(sx, sy, sx + 100, sy + 100, SLOTF)
        if s in grid:
            cv.blit(grid[s], sx + 18, sy + 18, 1)
    return cv.png()


def build_all():
    icons = build_icons()
    sheet = build_sheet(icons)
    return icons, sheet


def main():
    icons, sheet = build_all()
    if "--check" in sys.argv:
        icons2, sheet2 = build_all()
        assert all(icons[k][1] == icons2[k][1] for k in icons) and sheet == sheet2, "not deterministic"
        assert len(set(v[1] for v in icons.values())) == len(icons), "two icons are the same picture"
        for k, (img, data) in icons.items():
            for row in img:
                for px in row:
                    assert px[3] in (0, 255), "%s: soft alpha" % k
                    if px[3]:
                        assert tuple(px[:3]) not in ((0, 0, 0), (255, 255, 255)), "%s: pure black / white" % k
        print("check OK: %d icons deterministic, hard alpha, all different" % len(icons))
        return
    os.makedirs(os.path.join(OUT, ICON_DIR_REL), exist_ok=True)
    files = []
    for t in ICONS:
        data = icons[t[0]][1]
        with open(os.path.join(OUT, icon_rel(t[0])), "wb") as fh:
            fh.write(data)
        files.append({"path": icon_rel(t[0]), "bytes": len(data), "sha256": sha(data)})
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh:
        fh.write(sheet)
    files.append({"path": "sheet.png", "bytes": len(sheet), "sha256": sha(sheet)})
    man = {
        "what": "SkyWynn warp icons - one per warp theme for World > Teleport (DRAFT v1 until Skyy sees sheet.png)",
        "status": "DRAFT",
        "generator": "tools/art/make_warp_icons.py",
        "reuses": "tools/art/make_menu_icons.py (shape helpers, painter, palettes)",
        "deterministic": True, "original_pixels": True,
        "icon_rules": {"size": [64, 64], "alpha": "hard (0 or 255)", "outline": "1 px #120e1c tinted toward the touching part",
                       "light": "top left", "no_pure_black_or_white": True, "supersample": M.SS},
        "icons": [{"name": t[0], "id": "Skyy_Menu_Icon_" + t[0], "label": t[1], "theme": t[2], "file": icon_rel(t[0]),
                   "bytes": len(icons[t[0]][1]), "sha256": sha(icons[t[0]][1]), "shows": t[4]} for t in ICONS],
        "reused": [{"theme": th, "label": lab, "id": iid, "shows": w} for th, lab, iid, w in REUSED],
        "files": files,
        "palettes": PAL_USED,
    }
    with open(os.path.join(OUT, "manifest.json"), "w", newline="\n") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    print("wrote %d icons + sheet.png + manifest.json to %s" % (len(ICONS), OUT))


if __name__ == "__main__":
    main()
