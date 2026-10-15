#!/usr/bin/env python3
"""SkyWynn Menu icons, sheet 2 - the Teleport page, the shared buttons and the Shards tile (DRAFT v1).

Skyy (2026-10-15, looking at the Teleport page's vanilla icons): "lets do our own icons in every menu too." This is the FIRST sheet of
that job. Same family look as the approved art/menu-icons/ (Skyy 2026-10-10: "beautiful! i love it"): this script REUSES that
generator (tools/art/make_menu_icons.py - imported, never edited) for the shape helpers, the Icon painter, the palettes and the PNG
writer, and only adds a few palettes of its own.

Writes (all ORIGINAL pixels; no game file is read):
  art/menu-icons-2/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png   64 x 64 RGBA, hard alpha, 1 px dark outline
  art/menu-icons-2/sheet.png                                               review sheet (1x + 2x, 32 px, light, Teleport + main mocks)
  art/menu-icons-2/manifest.json                                           icons (id, file, bytes, sha256, category, replaces), palettes

Run:   python tools/art/make_menu_icons_2.py        (deterministic: two runs = same bytes)
Check: python tools/art/validate_menu_icons_2.py
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_icons as M
from make_menu_icons import (Icon, circle, ellipse, rect, rrect, poly, capsule, union, diff, inter, ering, star_pts, obox,
                             hstripes, folds, hx, mix, png_bytes, Canvas, half, sha)

ROOT = M.ROOT
OUT = os.path.join(ROOT, "art", "menu-icons-2")
ICON_DIR_REL = M.ICON_DIR_REL
SHEET1_DIR = os.path.join(ROOT, "art", "menu-icons")       # the approved sheet-1 icons (read for the main-menu mock only)

# ====================================================================== our extra palettes (dark -> light, same rules as sheet 1)
PAL2 = {
    "ruby":     ["#2e0910", "#561420", "#86202e", "#b8303a", "#de5248", "#f48a72", "#fcc6ad"],
    "skin":     ["#3b2018", "#5e3424", "#8a5236", "#b4744c", "#d39a6c", "#ecc293", "#f8e2c4"],
    "hair":     ["#1e100c", "#331b12", "#4c2a18", "#683c20", "#86522c", "#a46d3e"],
    "wooddim":  ["#1f1714", "#2f2420", "#41342e", "#55463d", "#6a594d", "#806d5f", "#9a887a"],
    "golddim":  ["#2a2318", "#433826", "#5f4f33", "#7d6942", "#9a8452", "#b5a06a", "#d2c08e"],
    "stonedim": ["#1c1b24", "#2a2933", "#3a3945", "#4d4b58", "#625f6c", "#7a7783", "#94919c"],
    "beam":     ["#6a2c0a", "#a24a10", "#d8761c", "#f5a332", "#ffcf6a", "#ffe9a8", "#fff4cf"],
}
for _k, _v in PAL2.items():
    assert _k not in M.PAL, _k
    M.PAL[_k] = _v
    M.PALC[_k] = [hx(c) for c in _v]
PAL_USED = dict(M.PAL)


# ====================================================================== shared parts
def island_base(ic, cx, top, rw, depth, grass_ry=5.0, seed=0):
    """a small floating island: grey rock wedge + soil band + grass cap (sheet-1 island look, smaller)"""
    rock = poly([(cx - rw, top), (cx + rw, top), (cx + rw * 0.82, top + depth * 0.35), (cx + rw * 0.45, top + depth * 0.6),
                 (cx + rw * 0.15, top + depth), (cx - rw * 0.2, top + depth * 0.82), (cx - rw * 0.55, top + depth * 0.5),
                 (cx - rw * 0.85, top + depth * 0.3)])
    ic.add(rock, "stone", base=0.42, grad=0.6, pattern=hstripes(4, 0.1, 1 + seed))
    ic.add(inter(rock, rect(0, top - 1, 64, top + 3.5)), "soil", base=0.5, grad=0.4, bevel=0,
           pattern=lambda x, y: -0.12 if (int(x) * 7 + int(y) * 3) % 11 == 0 else 0)
    ic.add(union(ellipse(cx, top - 1, rw + 1, grass_ry), *[circle(cx - rw + 3 + 5.5 * k, top + 3.2, 1.5) for k in range(0, int(2 * rw / 5.5)) if k % 2 == 0]),
           "grass", base=0.6, grad=0.6)


def hexagon(cx, cy, w, h, k=0.32):
    """an upright crystal hex (pointed top and bottom): w wide, h tall"""
    a = w * k
    return [(cx, cy - h / 2), (cx + w / 2, cy - h / 2 + a), (cx + w / 2, cy + h / 2 - a), (cx, cy + h / 2), (cx - w / 2, cy + h / 2 - a),
            (cx - w / 2, cy - h / 2 + a)]


def sign_arrow(x0, y0, x1, y1, head):
    """an arrow-shaped sign board pointing right: body x0..x1-head, point at x1"""
    my = (y0 + y1) / 2
    return [(x0, y0), (x1 - head, y0), (x1, my), (x1 - head, y1), (x0, y1)]


def signpost(ic, wood="wood", gold="gold", stone="stone", grass="grass", board=True):
    ic.add(ellipse(32, 57, 15, 4.2), stone, base=0.5, grad=0.6)                               # stone foot
    ic.add(union(ellipse(22, 54.5, 3.2, 2.2), ellipse(42.5, 54.8, 3.6, 2.0)), grass, base=0.55, bevel=0.6)   # grass tufts
    ic.add(rect(28.5, 9, 35.5, 57), wood, mode="cyl", axis=(0, 1), base=0.55, pattern=hstripes(7, 0.05))  # the post
    ic.add(circle(32, 8.5, 4.2), gold, mode="sphere", base=0.68)                               # gold cap
    if not board:
        return
    up = sign_arrow(7, 14, 58, 31, 11)                                                          # main board -> right
    ic.add(poly(up), wood, base=0.6, grad=0.45, pattern=hstripes(4.25, 0.09, 2), line=True)
    ic.add(poly(sign_arrow(13, 19.5, 50, 25.5, 7)), gold, base=0.62, grad=0.6, bevel=0.6)     # the painted gold arrow
    lo = [(64 - x, y) for x, y in sign_arrow(14, 35, 50, 46, 7)]                               # small board <- left
    ic.add(poly(lo), wood, base=0.42, grad=0.45, pattern=hstripes(5.5, 0.08, 1), line=True)
    for (nx, ny) in ((11, 22.5), (46.5, 40.5)):                                                # nails
        ic.add(circle(nx, ny, 1.2), "steel", base=0.75, bevel=0, cast=False)


def padlock(ic, x, y, pal="steel", s=1.0):
    ic.add(ering(x, y - 5.5 * s, 6.2 * s, 6.8 * s, 3.4 * s, 4.0 * s), pal, mode="torus", base=0.6,
           torus=(x, y - 5.5 * s, 6.2 * s, 6.8 * s, 3.4 * s, 4.0 * s), bevel=0)
    ic.add(rrect(x - 9 * s, y - 4 * s, x + 9 * s, y + 10 * s, 2 * s), "gold", base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(union(circle(x, y + 1.5 * s, 2.2 * s), rect(x - 1.0 * s, y + 1.5 * s, x + 1.0 * s, y + 6.5 * s)), "navy", base=0.2, bevel=0, cast=False)


def chevron(cx, cy, w, h, t, d):
    """a thick chevron pointing right (d=1) or left (d=-1)"""
    pts = [(cx - w / 2, cy - h / 2), (cx - w / 2 + t, cy - h / 2), (cx + w / 2, cy), (cx - w / 2 + t, cy + h / 2), (cx - w / 2, cy + h / 2),
           (cx + w / 2 - t, cy)]
    if d < 0:
        pts = [(2 * cx - x, y) for x, y in pts]
    return poly(pts)


# ====================================================================== the icons
def icon_my_island():
    ic = Icon("MyIsland")
    island_base(ic, 32, 46, 23, 16)
    ic.add(circle(15, 41.5, 4.0), "grass", mode="sphere", base=0.5)                            # bushes
    ic.add(circle(49.5, 42, 3.3), "grass", mode="sphere", base=0.45)
    ic.add(ellipse(32, 44.3, 6.5, 1.8), "grass", base=0.15, bevel=0, rim=False, cast=False)     # the pin's shadow on the grass
    pin = union(circle(32, 19, 14), poly([(20.5, 26), (43.5, 26), (32, 44)]))                  # a gold map-pin home marker
    ic.add(pin, "gold", base=0.6, grad=0.6, bevel=1.2, bev=0.2, line=True)
    ic.add(circle(32, 19, 9.6), "cream", base=0.72, grad=0.4, bevel=0)                         # its face
    ic.add(poly([(23.5, 19.5), (32, 11.5), (40.5, 19.5)]), "mahog", base=0.55, grad=0.5, bevel=0.6, line=True)   # house: roof
    ic.add(rect(25.5, 19, 38.5, 26.5), "wood", base=0.6, grad=0.4, bevel=0.6)                  # house: walls
    ic.add(rect(30, 21.5, 34, 26.5), "mahog", base=0.25, bevel=0, cast=False)                  # door
    ic.sparkle(54, 9, 2); ic.sparkle(9, 13, 1)
    return ic


def icon_hub():
    ic = Icon("Hub")
    def tiles(x, y):
        return -0.12 if (int((x + 2 * y) // 5) + int(y // 2.5)) % 2 else 0.0
    ic.add(ellipse(32, 55, 28.5, 6), "stone", base=0.55, grad=0.5, pattern=tiles)            # the plaza
    def glow(x, y):
        return 0.2 + 0.75 * (y - 22) / 32 - 0.25 * abs(x - 32) / 9
    ic.add(rect(22, 20, 42, 54), "beam", tfunc=glow, bevel=0, rim=False)                       # warm town light through the gate
    ic.add(poly([(29.5, 54), (34.5, 54), (33.2, 40), (30.8, 40)]), "cream", base=0.75, bevel=0, rim=False, cast=False)  # the road in
    def blocks(x, y):
        row = int(y // 5)
        return -0.11 if int(y) % 5 == 0 or int(x + (3.5 if row % 2 else 0)) % 7 == 0 else 0.0
    wall = diff(rect(18, 19, 46, 54), union(rect(24.5, 31, 39.5, 55), ellipse(32, 31, 7.5, 8)))
    ic.add(wall, "stone", base=0.5, grad=0.5, bevel=1.1, pattern=blocks)                        # gate wall with the arch
    for x0 in (5, 43):                                                                          # two towers with battlements
        tower = union(rect(x0, 15, x0 + 16, 55), *[rect(x0 + k * 6, 9, x0 + k * 6 + 4, 16) for k in range(3)])
        ic.add(tower, "stone", base=0.66 if x0 < 30 else 0.5, grad=0.55, bevel=1.2, bev=0.2, pattern=blocks, line=True)
        bx = x0 + 8
        ic.add(poly([(bx - 4.5, 24), (bx + 4.5, 24), (bx + 4.5, 42), (bx, 38.5), (bx - 4.5, 42)]), "amber",
               base=0.62 if x0 < 30 else 0.48, grad=0.5, pattern=folds(1.2, 0.06, bx), line=True)   # amber banners
        ic.add(rect(bx - 5.5, 22.5, bx + 5.5, 25), "gold", base=0.6, bevel=0)
        ic.add(poly(star_pts(bx, 31, 2.6, 1.0, 4)), "gold", base=0.85, bevel=0, cast=False)
    ic.add(poly([(28.5, 19), (35.5, 19), (36.5, 26), (27.5, 26)]), "gold", base=0.62, grad=0.6, bevel=0.8, line=True)  # keystone
    ic.add(circle(32, 22.3, 1.6), "amber", mode="sphere", base=0.75, bevel=0)
    ic.sparkle(32, 6, 2); ic.sparkle(58, 4, 1)
    return ic


def icon_spawn():
    ic = Icon("Spawn")
    ic.add(ellipse(32, 53, 25, 7.5), "stone", base=0.32, grad=0.4)                             # pad: side
    ic.add(rect(7, 47, 57, 53), "stone", base=0.36, grad=0.5)
    ic.add(ellipse(32, 47, 25, 7.5), "stone", base=0.68, grad=0.5, line=True)                  # pad: top
    ic.add(ering(32, 47, 19.5, 5.6, 15, 4.0), "gold", base=0.62, bevel=0, cast=False)          # gold inlay ring
    def beam(x, y):
        return 0.98 - 0.5 * abs(x - 32) / 8 - 0.15 * (47 - y) / 36
    ic.add(union(poly([(24, 47), (40, 47), (36.5, 14), (27.5, 14)]), ellipse(32, 47, 8, 2.4)), "beam", tfunc=beam, bevel=0, rim=False)
    ic.add(poly(star_pts(32, 15, 12.5, 5.2, 5)), "gold", base=0.66, grad=0.6, bevel=0.9, line=True)   # the spawn star
    ic.add(poly(star_pts(32, 15.5, 5.2, 2.2, 5)), "gold", base=0.92, bevel=0, cast=False)
    ic.sparkle(52, 30, 2); ic.sparkle(11, 34, 1); ic.sparkle(49, 8, 1)
    return ic


def icon_warp():
    ic = Icon("Warp")
    signpost(ic)
    ic.sparkle(56, 44, 1)
    return ic


def icon_warp_locked():
    ic = Icon("WarpLocked")
    signpost(ic, wood="wooddim", gold="golddim", stone="stonedim", grass="stonedim")
    padlock(ic, 47, 46, s=1.0)
    return ic


def icon_no_warps():
    ic = Icon("NoWarps")
    signpost(ic, wood="stonedim", gold="stonedim", stone="stonedim", grass="stonedim", board=False)
    # a dashed board outline where the sign would be: "nothing here yet"
    pts = sign_arrow(8, 15, 57, 31, 11)
    segs = list(zip(pts, pts[1:] + pts[:1]))
    dash, gap = 5.0, 3.4
    caps = []
    for (a, b) in segs:
        L = math.hypot(b[0] - a[0], b[1] - a[1]); t = 0.0
        while t < L - 0.5:
            e = min(L, t + dash)
            caps.append(capsule(a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L,
                                a[0] + (b[0] - a[0]) * e / L, a[1] + (b[1] - a[1]) * e / L, 1.45))
            t = e + gap
    for c in caps:
        ic.add(c, "stone", base=0.72, bevel=0)
    return ic


def icon_back():
    ic = Icon("Back")
    body = union(rect(21, 16, 38, 27.5), diff(ering(38, 36, 20, 20, 8.5, 8.5), rect(0, 0, 38, 64)), rect(25, 44.5, 38, 56))
    ic.add(body, "steel", base=0.66, grad=0.55, bevel=1.3, bev=0.2)
    ic.add(poly([(5, 21.8), (24, 6.5), (24, 37)]), "steel", base=0.74, grad=0.5, bevel=1.3, bev=0.2, line=True)
    ic.add(capsule(29, 50.2, 37, 50.2, 1.2), "gold", base=0.6, bevel=0, cast=False)           # a gold tip on the tail
    return ic


def nav_pair(name, d):
    ic = Icon(name)
    back_x, front_x = (24, 40) if d > 0 else (40, 24)
    ic.add(chevron(back_x, 32, 22, 44, 11, d), "steel", base=0.4, grad=0.5, bevel=1.1)
    ic.add(chevron(front_x, 32, 22, 44, 11, d), "steel", base=0.7, grad=0.55, bevel=1.3, bev=0.2, line=True)
    return ic


def icon_close():
    ic = Icon("Close")
    ic.add(rrect(6, 6, 58, 58, 7), "steel", base=0.58, grad=0.55, bevel=1.4, bev=0.2)        # steel plate
    ic.add(rrect(12, 12, 52, 52, 3.5), "steel", base=0.22, grad=-0.3, bevel=0, cast=False)    # recessed field
    for (rx, ry) in ((9.5, 9.5), (54.5, 9.5), (9.5, 54.5), (54.5, 54.5)):
        ic.add(circle(rx, ry, 1.6), "steel", mode="sphere", base=0.7, bevel=0)
    x = union(capsule(20, 20, 44, 44, 5.2), capsule(44, 20, 20, 44, 5.2))
    ic.add(x, "ruby", base=0.62, grad=0.6, bevel=1.1, bev=0.2, line=True)
    return ic


def disc_button(name, gem, mark):
    ic = Icon(name)
    ic.add(ering(32, 32, 28, 28, 22.5, 22.5), "steel", mode="torus", torus=(32, 32, 28, 28, 22.5, 22.5), base=0.62, bevel=0)
    ic.add(circle(32, 32, 23), gem, mode="sphere", sphere=(30, 29, 26, 26), base=0.5, bevel=0)
    ic.add(mark, "cream", base=0.82, grad=0.4, bevel=1.0, bev=0.2, line=True)
    ic.px(19, 18, "#fff4cf"); ic.px(20, 17, "#fff4cf"); ic.px(18, 19, "#efe2c0")
    return ic


def icon_accept():
    return disc_button("Accept", "emerald", union(capsule(19, 33, 28, 42, 3.9), capsule(28, 42, 45, 22, 3.9)))


def icon_deny():
    return disc_button("Deny", "ruby", union(capsule(22, 22, 42, 42, 3.9), capsule(42, 22, 22, 42, 3.9)))


def icon_player():
    ic = Icon("Player")
    ic.add(poly([(13, 62), (15, 52), (22, 48.5), (42, 48.5), (49, 52), (51, 62)]), "violet", base=0.5, grad=0.5)   # shirt
    ic.add(rect(26, 46, 38, 51), "skin", base=0.3, bevel=0)                                    # neck
    obox(ic, 14, 19, 44, 48, 15, "skin", base=0.55, line=False)                                # the head cube
    d = 15; ox, oy = d * 0.55, d * 0.6
    ic.add(poly([(14, 19), (44, 19), (44 + ox, 19 - oy), (14 + ox, 19 - oy)]), "hair", base=0.72, grad=0.4)  # hair: top
    ic.add(union(rect(14, 19, 44, 25.5), rect(14, 19, 18, 33)), "hair", base=0.5, grad=0.4, cast=True)       # hair: fringe + sideburn
    ic.add(poly([(44, 19), (44 + ox, 19 - oy), (44 + ox, 34 - oy), (44, 34)]), "hair", base=0.28, grad=0.3)  # hair: side
    for ex in (22, 33):                                                                         # eyes
        ic.add(rect(ex, 30, ex + 5, 35), "cream", base=0.85, bevel=0, cast=False)
        ic.add(rect(ex + 2.5, 30, ex + 5, 35), "navy", base=0.4, bevel=0, cast=False)
    ic.add(rect(26, 40, 34, 42.5), "skin", base=0.18, bevel=0, cast=False)                    # mouth
    return ic


def icon_shards():
    ic = Icon("Shards")
    island_base(ic, 32, 50, 20, 11, grass_ry=4.5, seed=2)
    for pts, b in (([(13, 49), (11, 41), (15.5, 35), (20, 41), (19.5, 49)], 0.45),               # small crystals growing on it
                   ([(44.5, 49), (45, 42.5), (49.5, 38), (53, 43), (51.5, 49)], 0.35)):
        ic.add(poly(pts), "amber", base=b, grad=0.6, bevel=0.8, line=True)
    ic.add(ellipse(32, 48.3, 7, 1.7), "grass", base=0.15, bevel=0, rim=False, cast=False)       # the floating shard's shadow
    hx_ = hexagon(32, 24, 25, 38)
    ic.add(poly(hx_), "amber", base=0.62, grad=0.6, bevel=1.3, bev=0.22, line=True)            # the shard
    ic.add(poly([hx_[0], hx_[1], hx_[2], hx_[3], (32, 24)]), "amber", base=0.36, grad=0.4, bevel=0, cast=False)  # right facet
    win = hexagon(32, 24, 14.5, 23)
    def swirl(x, y):
        dx, dy = (x - 32) / 7.5, (y - 24) / 11.5; r = math.hypot(dx, dy); a = math.atan2(dy, dx)
        return 0.25 + 0.55 * (1 - r) + 0.2 * math.sin(3 * a + r * 8.0)
    ic.add(poly(win), "void", tfunc=swirl, bevel=0, line=True)                                 # its portal window
    ic.add(poly(star_pts(32, 24, 4.6, 1.6, 4)), "gold", base=0.9, bevel=0, cast=False)
    ic.sparkle(52, 10, 2); ic.sparkle(11, 18, 1); ic.sparkle(55, 30, 1)
    return ic


# ====================================================================== the icon list
# (Name, label, group, category, builder, replaces (vanilla id now shown), where in SkyyMenu, what it shows)
ICONS = [
    ("MyIsland",   "My Island",   "tp",      "travel", icon_my_island,   "Soil_Grass",               'ENTRIES ("tp", 11) + PLAYER_ACTIONS 31',
     "a small floating island (grass, soil, rock, two bushes) with a big gold map-pin home marker planted in it; the pin shows a little house"),
    ("Hub",        "Hub",         "tp",      "travel", icon_hub,         "Hub_Portal_Default",       'ENTRIES ("tp", 13) + PLAYER_ACTIONS 29',
     "a stone town gate (arch, gold keystone, two amber banners) glowing warm inside, over a tiled plaza with a gold inlay ring"),
    ("Spawn",      "Spawn",       "tp",      "travel", icon_spawn,       "Spawn_Portal",             'ENTRIES ("tp", 15) + PLAYER_ACTIONS 30',
     "a round stone spawn pad with a gold inlay ring and a beam of warm light rising to a gold star"),
    ("Warp",       "Warp",        "tp",      "travel", icon_warp,        "Tool_Map",                 "ICON_WARP (every unlocked warp)",
     "a wooden signpost (gold cap, stone foot): a big board pointing right with a painted gold arrow, a small board pointing left"),
    ("WarpLocked", "Warp (locked)", "tp",    "travel", icon_warp_locked, "Tool_Map",                 "new ICON_WARP_LOCKED (warps not unlocked)",
     "the same signpost in dim grey-brown, with a gold padlock in front"),
    ("NoWarps",    "No warps yet", "tp",     "travel", icon_no_warps,    "Tool_Map",                 "new ICON_NO_WARPS (NO_WARPS_SLOT 31)",
     "a bare grey signpost with a dashed outline where the board would be"),
    ("Shards",     "Shards",      "main",    "travel", icon_shards,      "Portal_Device",            'ENTRIES ("main", 11)',
     "an amber hex shard crystal with a violet portal window and gold star, floating over a tiny island with two small crystals"),
    ("Back",       "Go Back",     "nav",     "admin",  icon_back,        "Weapon_Arrow_Iron",        "ICON_BACK (slot 45)",
     "a thick steel return arrow: points left, its tail curls round on the right (gold tip)"),
    ("Prev",       "Previous Page", "nav",   "admin",  lambda: nav_pair("Prev", -1), "Weapon_Arrow_Crude", "ICON_PREV (slot 48)",
     "a steel double chevron pointing left (front one bright, back one dark); the mirror of Next"),
    ("Next",       "Next Page",   "nav",     "admin",  lambda: nav_pair("Next", 1),  "Weapon_Arrow_Iron",  "ICON_NEXT (slot 50)",
     "a steel double chevron pointing right; the mirror of Previous"),
    ("Close",      "Close",       "nav",     "admin",  icon_close,       "Furniture_Flag_Small_Red", "ICON_CLOSE (slot 49)",
     "a square steel plate with 4 rivets and a recessed field holding a big red X"),
    ("Player",     "Player",      "players", "social", icon_player,      "Armor_Leather_Light_Head", "ICON_PLAYER (fallback when no head is shown)",
     "a generic blocky player head in 3/4 view (brown hair, two eyes) on violet shoulders"),
    ("Accept",     "Accept Request", "players", "admin", icon_accept, "Ingredient_Crystal_Green", 'ENTRIES ("players", 47)',
     "a round emerald button in a steel ring with a cream check mark"),
    ("Deny",       "Deny Request",   "players", "admin", icon_deny,   "Ingredient_Crystal_Red",   'ENTRIES ("players", 51)',
     "a round ruby button in a steel ring with a cream X (the round shape keeps it apart from the square Close plate)"),
]
GROUPS = [("tp", "TELEPORT PAGE  (TRAVEL - GOLD / AMBER)", "#f5a332"),
          ("main", "MAIN MENU TILE  (TRAVEL - GOLD / AMBER)", "#f5a332"),
          ("nav", "BUTTONS ON EVERY PAGE  (ADMIN - STEEL, RED CLOSE)", "#a1aaba"),
          ("players", "PLAYERS PAGE  (SOCIAL VIOLET HEAD, STEEL ACCEPT / DENY)", "#8355b5")]
CATS = {"travel": "#f5a332", "admin": "#a1aaba", "social": "#8355b5"}


def icon_rel(name):
    return "%s/Skyy_Menu_Icon_%s.png" % (ICON_DIR_REL, name)


def build_icons():
    """name -> (image, png bytes) - pure, no file writes (the validator uses this for the determinism check)"""
    out = {}
    for t in ICONS:
        img = t[4]().render()
        out[t[0]] = (img, png_bytes(img))
    return out


# ====================================================================== sheet
BG = (24, 26, 38); PANEL = (34, 37, 52); INK = (226, 228, 236); DIM = (150, 156, 176); GOLDT = hx("#e0b060")
NAVY = (11, 21, 36); SLOT = (22, 38, 58); SLOTF = (44, 66, 96)

# SkyyMenu 0.3.25 main view: slot -> sheet-1 icon name (ENTRIES "main" rows); Shards = this sheet; Wardrobe + Edit stay vanilla for now
MAIN_SLOTS = {33: "YourProfile", 3: "Pets", 8: "HoverTooltips", 13: "Teleport", 32: "PocketDimension", 5: "AccessoryBag", 26: "HudEditor",
              14: "Crafting", 4: "Skills", 40: "Collections", 12: "IslandMenu", 21: "Bank", 29: "Vault", 22: "Bazaar", 23: "AuctionHouse",
              30: "Reforge", 31: "Identify", 0: "Players", 9: "Party", 18: "Guild", 35: "Mods", 44: "ServerSetup", 17: "Settings"}
MAIN_VANILLA = {36: "WARDROBE", 53: "EDIT"}


def sheet1_icon(name):
    return P.read_png(open(os.path.join(SHEET1_DIR, ICON_DIR_REL, "Skyy_Menu_Icon_%s.png" % name), "rb").read())


def menu_mock(cv, x0, top, title, note, slots, vanilla, icons_new):
    pw, ph = 9 * 78 + 44, 6 * 78 + 108
    cv.rect(x0, top, x0 + pw, top + ph, NAVY)
    cv.rect(x0 + 22, top + 14, x0 + pw - 22, top + 17, GOLDT)
    cv.text(x0 + 22, top + 26, title, GOLDT, 3)
    cv.text(x0 + 22 + len(title) * 18 + 14, top + 33, "(MOCK - NOT THE REAL GAME SCREEN)", DIM, 1)
    gx, gy = x0 + 22, top + 56
    for s in range(54):
        sx, sy = gx + (s % 9) * 78, gy + (s // 9) * 78
        cv.rect(sx, sy, sx + 74, sy + 74, SLOT); cv.frame(sx, sy, sx + 74, sy + 74, SLOTF)
        if s in slots:
            img, new = slots[s]
            if new:
                cv.frame(sx - 2, sy - 2, sx + 76, sy + 76, GOLDT, 2)
            cv.blit(img, sx + 5, sy + 5, 1)
        elif s in vanilla:
            cv.text(sx + 6, sy + 30, vanilla[s], DIM, 1)
            cv.text(sx + 6, sy + 42, "(VANILLA)", DIM, 1)
    cv.text(x0 + 22, gy + 6 * 78 + 10, note, DIM, 1)
    cv.text(x0 + 22, gy + 6 * 78 + 24, "GOLD FRAME = A NEW ICON FROM THIS SHEET.", DIM, 1)
    return ph


def build_sheet(icons):
    W, H = 1556, 1908
    cv = Canvas(W, H, BG)
    cv.text(24, 20, "SKYWYNN MENU ICONS 2 - TELEPORT + BUTTONS - DRAFT V1", GOLDT, 4)
    cv.text(24, 60, "SKYY 2026-10-15: \"LETS DO OUR OWN ICONS IN EVERY MENU TOO.\" SAME FAMILY LOOK AS SHEET 1 (ART/MENU-ICONS).", DIM, 2)
    cv.text(24, 82, "64 PX, HARD ALPHA, 1 PX OUTLINE, LIGHT FROM THE TOP LEFT, ORIGINAL PIXELS. EACH CELL: 1X ON CHECKER, 1X ON NAVY, 2X.", DIM, 2)
    y = 116
    CW, CH = 250, 196
    for g, title, col in GROUPS:
        items = [t for t in ICONS if t[2] == g]
        rows = (len(items) + 5) // 6
        h = 40 + rows * CH
        cv.rect(16, y, W - 16, y + h, PANEL)
        cv.rect(16, y, W - 16, y + 3, hx(col))
        cv.text(28, y + 13, title, hx(col), 2)
        for k, t in enumerate(items):
            cx = 28 + (k % 6) * CW; cy = y + 40 + (k // 6) * CH
            img = icons[t[0]][0]
            cv.checker(cx, cy, 72, 72, (52, 56, 74), (44, 48, 64))
            cv.blit(img, cx + 4, cy + 4, 1)
            cv.rect(cx, cy + 82, cx + 72, cy + 154, NAVY)
            cv.blit(img, cx + 4, cy + 86, 1)
            cv.checker(cx + 82, cy, 144, 144, (52, 56, 74), (44, 48, 64))
            cv.blit(img, cx + 90, cy + 8, 2)
            cv.text(cx, cy + 160, t[1].upper()[:20], INK, 2)
            cv.text(cx, cy + 178, "WAS " + t[5].upper(), DIM, 1)
        y += h + 12
    # small views: 32 px on navy + 64 px on light
    cv.rect(16, y, W - 16, y + 196, PANEL)
    cv.text(28, y + 12, "32 PX (HALF SIZE) ON THE MENU NAVY", INK, 2)
    for k, t in enumerate(ICONS):
        sx = 28 + k * 44; sy = y + 38
        cv.rect(sx, sy, sx + 40, sy + 40, NAVY)
        cv.blit(half(icons[t[0]][0]), sx + 4, sy + 4, 1)
    cv.text(28, y + 92, "64 PX ON A LIGHT BACKGROUND", INK, 2)
    for k, t in enumerate(ICONS):
        sx = 28 + k * 70; sy = y + 116
        if sx + 66 > W - 16: break
        cv.rect(sx, sy, sx + 66, sy + 66, (214, 218, 226))
        cv.blit(icons[t[0]][0], sx + 1, sy + 1, 1)
    y += 196 + 12
    # mocks: Teleport page (left) + main view (right)
    ic = lambda n: icons[n][0]
    tp_slots = {11: (ic("MyIsland"), True), 13: (ic("Hub"), True), 15: (ic("Spawn"), True),
                19: (ic("Warp"), True), 20: (ic("Warp"), True), 21: (ic("WarpLocked"), True),
                45: (ic("Back"), True), 49: (ic("Close"), True)}
    menu_mock(cv, 16, y, "TELEPORT", "TELEPORT PAGE (VIEW TP): ISLAND 11, HUB 13, SPAWN 15, WARPS FROM SLOT 19 (THE THIRD ONE LOCKED), BACK 45, CLOSE 49.",
              tp_slots, {}, icons)
    main_slots = dict((s, (sheet1_icon(n), False)) for s, n in MAIN_SLOTS.items())
    main_slots[11] = (ic("Shards"), True)
    main_slots[49] = (ic("Close"), True)
    menu_mock(cv, 16 + 9 * 78 + 44 + 20, y, "SKYWYNN MENU",
              "MAIN VIEW, SLOTS AS IN SKYYMENU 0.3.25. SHARDS 11 + CLOSE 49 ARE NEW; THE REST IS SHEET 1. PETS = THE FALLBACK.",
              main_slots, MAIN_VANILLA, icons)
    return cv.png()


def main():
    icons = build_icons()
    os.makedirs(os.path.join(OUT, ICON_DIR_REL), exist_ok=True)
    files = []
    for t in ICONS:
        data = icons[t[0]][1]
        with open(os.path.join(OUT, icon_rel(t[0])), "wb") as fh:
            fh.write(data)
        files.append({"path": icon_rel(t[0]), "bytes": len(data), "sha256": sha(data)})
    sheet = build_sheet(icons)
    with open(os.path.join(OUT, "sheet.png"), "wb") as fh:
        fh.write(sheet)
    files.append({"path": "sheet.png", "bytes": len(sheet), "sha256": sha(sheet)})
    man = {
        "what": "SkyWynn Menu icons sheet 2 - Teleport page, shared buttons, Players page Accept / Deny, main Shards tile (DRAFT v1)",
        "generator": "tools/art/make_menu_icons_2.py", "validator": "tools/art/validate_menu_icons_2.py",
        "reuses": "tools/art/make_menu_icons.py (shape helpers, painter, palettes)",
        "deterministic": True, "original_pixels": True,
        "icon_rules": {"size": [64, 64], "alpha": "hard (0 or 255)", "outline": "1 px #120e1c tinted toward the touching part",
                       "light": "top left", "no_pure_black_or_white": True, "supersample": M.SS},
        "icons": [{"name": t[0], "id": "Skyy_Menu_Icon_" + t[0], "label": t[1], "group": t[2], "category": t[3], "file": icon_rel(t[0]),
                   "bytes": len(icons[t[0]][1]), "sha256": sha(icons[t[0]][1]),
                   "replaces_vanilla_id": t[5], "skyymenu": t[6], "shows": t[7]} for t in ICONS],
        "files": files,
        "palettes": PAL_USED,
    }
    with open(os.path.join(OUT, "manifest.json"), "w", newline="\n") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    print("wrote %d icons + sheet.png + manifest.json to %s" % (len(ICONS), OUT))


if __name__ == "__main__":
    main()
