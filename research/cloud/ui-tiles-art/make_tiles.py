#!/usr/bin/env python3
"""SkyWynn Menu picture tiles - phase 1 (the 8 Home tiles), CONCEPT v1, cloud art 2026-10-22.

Run:  python research/cloud/ui-tiles-art/make_tiles.py
Writes next to this script:
  tiles/<file>@2x.png  232 x 232 (the picture the SkyyMenu tile slot shows; @2x of the 116 px picture)
  tiles/<file>.png     116 x 116 (the 1x copy, a 2 x 2 box filter of the @2x)
  sheet.png            the review sheet: all 8 at 2x and 1x with the label bar + gold frame mock, and the default Home grid at 1x
  manifest.json        every file: path, size, bytes, sha256
Pure Python (skyypaint.py / skyyitems.py next to this script; zlib only, no Pillow). Our own drawings of real game things - no vanilla
file, other mod or reference picture is read. Deterministic: two runs = the same bytes (checked by --check).

Look learnt from Skyy's reference (Hylterium hub, described in research/UI-Ideas.md 2026-10-22 MENU TILE PICTURES - never copied):
each button = a small busy scene, close-up hero object, bright saturated colours, depth behind, sparkles; a blue label bar + a gold frame.
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skyypaint as P      # noqa: E402
import skyyitems as I      # noqa: E402

S = 232                     # @2x picture
BAR = 44                    # @2x label bar the page draws over the picture's bottom (22 px at 1x, UI-Queue-Spec 8)
LABEL_BLUE = P.hx("#4274a5")
FRAME_GOLD = P.hx("#E8A93B")
INK = I.INK

# the 8 tiles: (file stem, label, the SkyyMenu shortcut key, default Home slot (5 x 5, row * 5 + col) or None)
TILES = [
    ("tab_world_teleport", "Teleport", "tab:world:teleport", 12),
    ("hub_character", "Character", "hub:character", 7),
    ("hub_storage", "Storage", "hub:storage", 11),
    ("hub_market", "Market", "hub:market", 17),
    ("hub_smithing", "Crafting", "hub:smithing", 13),
    ("hub_world", "World", "hub:world", None),
    ("hub_social", "Social", "hub:social", 6),
    ("hub_settings", "Settings", "hub:settings", 8),
]

GRASS = P.hx("#6cbf48")
GRASS_D = P.hx("#4f9a36")
DIRT = P.hx("#8a5d3b")
STONE = P.hx("#8d949b")
SKIN = P.hx("#e8b48a")


# ------------------------------------------------------------------ shared scene pieces
def sky(cv, top="#7cc4f2", mid="#bfe3f7", low="#ffe0b8"):
    cv.vgrad(0, 0, S, S, [(0.0, P.hx(top)), (0.55, P.hx(mid)), (1.0, P.hx(low))])


def island(cv, ox, oy, s, R, seed, depth=1.4, haze=0.0, trees=(), grass=GRASS):
    """a floating sky island of 2:1 iso blocks: grass top, dirt, stone, a hanging point underneath"""
    cells = []
    for i in range(-R, R + 1):
        for j in range(-R, R + 1):
            d = math.hypot(i, j)
            if d <= R + 0.35 - 0.5 * P.hsh(seed, i, j):
                dep = 1 + int((R + 0.6 - d) * depth + P.hsh(seed, i, j, 3) * 1.5)
                for k in range(-dep, 1):
                    cells.append((i + j, k, i, j, dep))
    cells.sort()
    hz = P.hx("#cfe6f6")

    def tint(c):
        return P.mix(c, hz, haze)
    for _, k, i, j, dep in cells:
        tx = ox + (i - j) * s
        ty = oy + (i + j) * s / 2.0 - k * s
        sd = seed * 97 + i * 13 + j * 7 + k
        if k == 0:
            def side(iu, iv):
                return tint(grass if iv == 0 else (GRASS_D if (iv == 1 and P.hsh(sd, iu) < 0.4) else DIRT))
            cv.cube(tx, ty, s, tint(grass), tint(DIRT), tint(DIRT), sd, 4, 0.12, None, side, side)
        else:
            col = DIRT if k > -2 else STONE
            cv.cube(tx, ty, s, tint(col), tint(col), tint(col), sd, 4, 0.14)
    for (i, j, kind) in trees:
        tx = ox + (i - j) * s
        ty = oy + (i + j) * s / 2.0 - s
        tree(cv, tx, ty, s * 0.62, seed + i * 5 + j, kind, haze)


def tree(cv, tx, ty, s, seed, kind="oak", haze=0.0):
    hz = P.hx("#cfe6f6")
    trunk = P.mix(P.hx("#7a5232"), hz, haze)
    leaf = P.mix(P.hx("#3f9a3c") if kind == "oak" else P.hx("#e88aa8"), hz, haze)
    for k in range(3):
        cv.cube(tx, ty + s / 2.0 - k * s, s * 0.5, trunk, trunk, trunk, seed + k, 2, 0.1)
    top = ty + s / 2.0 - 3 * s
    for (di, dj, dk) in ((0, 0, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)):
        x = tx + (di - dj) * s * 0.75
        y = top + (di + dj) * s * 0.375 - dk * s * 0.75
        cv.cube(x, y, s * 0.75, leaf, leaf, leaf, seed + 31 + di * 3 + dj * 5 + dk * 7, 3, 0.16)


def humanoid(cv, x, y, sc, pal, wave=None, seed=1, face="front"):
    """a chunky voxel adventurer, feet on (x, y); sc = px per voxel unit. pal: skin, hair, shirt, trim, pants, boots, eyes"""
    d = 2.2 * sc
    lw, lh = 3.4 * sc, 6.0 * sc
    tw, th = 8.0 * sc, 7.0 * sc
    aw, ah = 2.8 * sc, 6.6 * sc
    hw, hh = 9.0 * sc, 8.2 * sc
    left = x - tw / 2.0
    ly = y - lh
    ty = ly - th
    # legs
    cv.box(left + 0.4 * sc, ly, lw, lh, d, pal["pants"], seed, (2, 4))
    cv.box(left + tw - lw - 0.4 * sc, ly, lw, lh, d, pal["pants"], seed + 1, (2, 4))
    cv.box(left + 0.2 * sc, y - 1.8 * sc, lw + 0.4 * sc, 1.8 * sc, d, pal["boots"], seed + 2, (2, 1))
    cv.box(left + tw - lw - 0.6 * sc, y - 1.8 * sc, lw + 0.4 * sc, 1.8 * sc, d, pal["boots"], seed + 3, (2, 1))
    # arms (the waving one goes up)
    for side in (0, 1):
        ax = left - aw if side == 0 else left + tw
        up = (wave == "left" and side == 0) or (wave == "right" and side == 1)
        if up:
            cv.box(ax, ty - ah + 1.4 * sc, aw, ah, d, pal["shirt"], seed + 5 + side, (2, 4), top=pal["trim"])
            cv.box(ax, ty - ah - 0.8 * sc, aw, 2.4 * sc, d * 0.8, pal["skin"], seed + 7 + side, (2, 2))
        else:
            cv.box(ax, ty + 0.3 * sc, aw, ah, d, pal["shirt"], seed + 5 + side, (2, 4), top=pal["trim"])
            cv.box(ax, ty + ah - 1.6 * sc, aw, 2.2 * sc, d * 0.8, pal["skin"], seed + 7 + side, (2, 2))
    # torso + trim
    def torso(iu, iv):
        if iv == 0 or iu in (0, 5):
            return pal["trim"]
        if iv == 4:
            return P.hx("#3a2a1e")
        return pal["shirt"]
    cv.box(left, ty, tw, th, d, pal["shirt"], seed + 9, (6, 6), pick_front=torso)
    cv.rect(x - 0.9 * sc, ty + 4.15 * sc, 1.8 * sc, 1.2 * sc, I.GOLD)                       # belt buckle
    # head
    hx0 = x - hw / 2.0
    hy = ty - hh
    def head(iu, iv):
        if iv <= 1 or (iv <= 3 and iu in (0, 7)):
            return pal["hair"]
        return pal["skin"]
    cv.box(hx0, hy, hw, hh, d * 1.1, pal["skin"], seed + 11, (8, 8), top=pal["hair"], side=pal["hair"], pick_front=head)
    cv.box(hx0 - 0.4 * sc, hy - 1.2 * sc, hw + 0.8 * sc, 1.8 * sc, d * 1.15, pal["hair"], seed + 13, (6, 1))
    # eyes: big Hytale-style eyes
    ey = hy + 4.2 * sc
    for ex in (x - 2.4 * sc, x + 1.2 * sc):
        cv.rect(ex, ey, 1.6 * sc, 2.0 * sc, (250, 250, 250))
        cv.rect(ex + 0.6 * sc, ey + 0.4 * sc, 1.0 * sc, 1.6 * sc, pal["eyes"])
        cv.rect(ex + 0.6 * sc, ey + 0.4 * sc, 0.45 * sc, 0.45 * sc, (255, 255, 255))
    cv.rect(x - 0.9 * sc, hy + 6.8 * sc, 1.8 * sc, 0.5 * sc, P.mul(pal["skin"], 0.7))     # mouth


def badge(cv, cx, cy, r, draw, ring=FRAME_GOLD):
    cv.glow(cx, cy, r * 1.5, P.hx("#fff2c0"), 0.5)
    cv.circle(cx, cy, r, P.hx("#14284a"))
    cv.ring(cx, cy, r * 0.80, r, ring)
    cv.ring(cx, cy, r * 0.80, r * 0.86, P.mul(ring, 0.6))
    cv.stroke(P.circ_pts(cx, cy, r, r, 32), 1.4, INK, 0.8)
    draw(cv, cx, cy, r * 1.25)


def gear(cv, cx, cy, ro, ri, teeth, rot, col, hole=0.3, ext=5):
    pts = P.gear_pts(cx, cy, ro, ri, teeth, rot)
    cv.poly([(x + ext, y + ext * 0.6) for x, y in pts], P.mul(col, 0.45))
    lo, hi = P.mul(col, 0.8), P.mul(col, 1.25)

    def sh(x, y):
        t = ((x - cx) * -0.6 + (y - cy) * -0.8) / ro
        return P.mix(lo, hi, max(0.0, min(1.0, 0.5 + 0.5 * t)))
    cv.poly(pts, sh)
    cv.stroke(pts, 1.8, INK, 0.8)
    cv.ring(cx, cy, ri * 0.62, ri * 0.74, P.mul(col, 0.7))
    cv.circle(cx, cy, ri * hole + ext * 0.0, P.hx("#1a2436"))
    cv.stroke(P.circ_pts(cx, cy, ri * hole, ri * hole, 24), 1.6, INK, 0.8)
    for k in range(teeth // 2):
        a = rot + k * 4 * math.pi / teeth + 0.3
        bx, by = cx + ri * 0.5 * math.cos(a), cy + ri * 0.5 * math.sin(a)
        cv.circle(bx, by, max(1.6, ri * 0.06), P.mul(col, 1.35))


# ------------------------------------------------------------------ the 8 scenes
def scene_teleport(cv):
    sky(cv, "#5aa8e6", "#a9dcf6", "#ffd9b0")
    cv.glow(116, 70, 120, P.hx("#ffe9b0"), 0.5)
    cv.cloud(28, 52, 34, seed=1, a=0.9)
    cv.cloud(206, 36, 30, seed=2, a=0.85)
    island(cv, 196, 92, 4, 2, 41, haze=0.55, trees=((0, -1, "oak"),))
    island(cv, 34, 120, 5, 2, 42, haze=0.4)
    island(cv, 116, 126, 12, 3, 7, trees=((-2, 1, "oak"), (2, -1, "oak")))
    # the portal arch: two stone-brick pillars + a lintel, a swirling shard portal inside
    brick = P.hx("#9aa3ad")

    def bricks(iu, iv):
        return P.mul(brick, 0.86 if (iu + iv) % 3 == 0 else 1.0)
    cx, base = 116, 140
    sw = P.hx("#6fe3ff")
    vi = P.hx("#9a5cff")

    def swirl(x, y):
        dx, dy = (x - cx) / 24.0, (y - 96) / 40.0
        r = math.hypot(dx, dy)
        if r > 1.0:
            return None
        th = math.atan2(dy, dx)
        v = 0.5 + 0.5 * math.sin(3.0 * th + r * 9.0)
        c = P.mix(vi, sw, v)
        c = P.mix(c, (255, 255, 255), max(0.0, 1.0 - r * 2.2) ** 1.5)
        return (c[0], c[1], c[2], 1.0)
    cv.glow(cx, 96, 70, sw, 0.55)
    cv.poly(P.circ_pts(cx, 96, 24, 40, 48), swirl)
    cv.box(cx - 46, 46, 18, base - 46, 9, brick, 61, (2, 9), pick_front=bricks)
    cv.box(cx + 26, 46, 18, base - 46, 9, brick, 62, (2, 9), pick_front=bricks)
    cv.box(cx - 54, 32, 106, 16, 9, brick, 63, (9, 2), pick_front=bricks)
    cv.circle(cx - 0.5, 40, 6.5, P.hx("#6fe3ff"))                                        # keystone gem
    cv.stroke(P.circ_pts(cx - 0.5, 40, 6.5, 6.5, 20), 1.6, INK, 0.8)
    cv.sparkle(cx - 0.5 - 2, 38, 3, (255, 255, 255), 0.9)
    for i in range(9):
        a = i * 0.7 + 0.4
        rr = 34 + 14 * P.hsh(9, i)
        cv.sparkle(cx + rr * math.cos(a) * 0.9, 96 + rr * math.sin(a) * 1.25, 2.2 + 2.6 * P.hsh(8, i), (200, 250, 255), 0.9)


def scene_character(cv):
    sky(cv, "#3d6fb0", "#86b9e8", "#ffd49a")
    cv.glow(116, 104, 110, P.hx("#fff0b8"), 0.65)
    cv.ring(116, 104, 74, 77, P.hx("#ffe9a8"), 0.55)
    cv.ring(116, 104, 86, 87.5, P.hx("#ffe9a8"), 0.35)
    # ground: a few grass blocks under the feet
    for i in range(-2, 3):
        cv.cube(116 + i * 22 - 0, 176 + abs(i) * 2, 22, GRASS, DIRT, DIRT, 70 + i, 4, 0.12,
                None, lambda iu, iv: GRASS if iv == 0 else DIRT, lambda iu, iv: GRASS if iv == 0 else DIRT)
    pal = {"skin": SKIN, "hair": P.hx("#5a3a22"), "shirt": P.hx("#2b2a2e"), "trim": P.hx("#d4824a"),
           "pants": P.hx("#3a3236"), "boots": P.hx("#5a3a24"), "eyes": P.hx("#2f6fb0")}
    humanoid(cv, 112, 186, 6.6, pal, seed=5)
    # skill badges orbiting (Mining, Combat, Farming, Fishing, Foraging, Alchemy)
    spots = [(34, 50, lambda c, x, y, s: I.pickaxe(c, x, y, s, -0.6)), (198, 50, lambda c, x, y, s: I.sword(c, x, y, s, 0.6)),
             (24, 112, lambda c, x, y, s: I.wheat(c, x, y, s)), (208, 112, lambda c, x, y, s: I.fish(c, x, y, s, -0.4)),
             (40, 166, lambda c, x, y, s: I.hatchet(c, x, y, s, -0.5)), (192, 166, lambda c, x, y, s: I.flask(c, x, y, s * 0.9))]
    for bx, by, fn in spots:
        badge(cv, bx, by, 19, fn)
    for i in range(6):
        cv.sparkle(70 + 92 * P.hsh(3, i), 30 + 60 * P.hsh(4, i), 2 + 2 * P.hsh(5, i), (255, 246, 200), 0.85)


def scene_storage(cv):
    cv.vgrad(0, 0, S, S, [(0.0, P.hx("#22334a")), (0.6, P.hx("#35506e")), (1.0, P.hx("#1c2a3c"))])
    # stone wall
    for row in range(8):
        for col in range(6):
            off = 20 if row % 2 else 0
            x, y = col * 44 - off, row * 22
            c = P.mul(P.hx("#4a5a6c"), 0.85 + 0.25 * P.hsh(row, col))
            cv.rect(x + 1, y + 1, 42, 20, c)
            cv.rect(x + 1, y + 1, 42, 3, P.mul(c, 1.18))
    # the round vault door (iron), a spoked wheel, bolts
    vx, vy, vr = 130, 86, 76
    cv.circle(vx + 6, vy + 6, vr, (12, 16, 24), 0.6)
    def iron(x, y):
        t = ((x - vx) * -0.6 + (y - vy) * -0.8) / vr
        return P.mix(P.hx("#5d6874"), P.hx("#b9c4cf"), max(0.0, min(1.0, 0.45 + 0.5 * t)))
    cv.poly(P.circ_pts(vx, vy, vr, vr, 96), iron)
    cv.ring(vx, vy, vr - 12, vr - 8, P.hx("#4a5560"))
    cv.stroke(P.circ_pts(vx, vy, vr, vr, 96), 2.2, INK, 0.85)
    for k in range(16):
        a = k * math.pi / 8.0
        cv.circle(vx + (vr - 5) * math.cos(a), vy + (vr - 5) * math.sin(a), 2.6, P.hx("#e0e6ec"))
        cv.circle(vx + (vr - 5) * math.cos(a) + 0.6, vy + (vr - 5) * math.sin(a) + 0.6, 1.2, P.hx("#5d6874"))
    cv.ring(vx, vy, 30, 36, I.GOLD)
    cv.stroke(P.circ_pts(vx, vy, 36, 36, 48), 1.6, INK, 0.8)
    for k in range(6):
        a = k * math.pi / 3.0 + 0.25
        cv.line(vx, vy, vx + 33 * math.cos(a), vy + 33 * math.sin(a), 5, P.hx("#c9a24a"))
        cv.circle(vx + 40 * math.cos(a), vy + 40 * math.sin(a), 4.2, I.GOLD_L)
        cv.stroke(P.circ_pts(vx + 40 * math.cos(a), vy + 40 * math.sin(a), 4.2, 4.2, 12), 1.2, INK, 0.7)
    cv.circle(vx, vy, 9, I.GOLD_L)
    cv.stroke(P.circ_pts(vx, vy, 9, 9, 20), 1.4, INK, 0.8)
    # floor
    cv.vgrad(0, 168, S, 64, [(0.0, P.hx("#3e4b5a")), (1.0, P.hx("#262f3a"))])
    # a wooden chest (iron bands, gold lock) left, the Pocket Dimension pouch right
    wood = P.hx("#9b6a3c")

    def planks(iu, iv):
        if iu in (0, 7):
            return P.hx("#6c7680")
        return P.mul(wood, 0.82 if iv % 2 else 1.0)
    cv.box(12, 132, 88, 52, 22, wood, 81, (8, 4), pick_front=planks, top=P.hx("#a8743f"))
    cv.box(12, 120, 88, 14, 22, P.hx("#8a5c33"), 82, (8, 1), top=P.hx("#b58049"))
    cv.rect(48, 126, 16, 20, I.GOLD)
    cv.rect(53, 134, 6, 7, P.hx("#3a2a1a"))
    cv.stroke([(48, 126), (64, 126), (64, 146), (48, 146)], 1.4, INK, 0.8)
    for i in range(5):
        I.coin(cv, 20 + i * 15, 192 + (i % 2) * 4, 8)
    # pouch: soft leather sack, drawstring, violet sparkles
    px, py = 176, 150
    lea = P.hx("#7a4b2a")

    def sack(x, y):
        t = ((x - px) * -0.5 + (y - py) * -0.7) / 40.0
        return P.mix(P.mul(lea, 0.75), P.mul(lea, 1.3), max(0.0, min(1.0, 0.5 + t)))
    body = [(px - 30, py + 6), (px - 24, py - 18), (px - 10, py - 26), (px + 10, py - 26), (px + 24, py - 18), (px + 32, py + 6),
            (px + 28, py + 30), (px + 12, py + 38), (px - 12, py + 38), (px - 28, py + 30)]
    cv.poly(body, sack)
    cv.stroke(body, 2, INK, 0.85)
    neck = [(px - 12, py - 26), (px + 12, py - 26), (px + 16, py - 40), (px + 6, py - 36), (px, py - 42), (px - 6, py - 36), (px - 16, py - 40)]
    cv.poly(neck, P.mul(lea, 1.1))
    cv.stroke(neck, 1.8, INK, 0.85)
    cv.rect(px - 14, py - 28, 28, 5, P.hx("#e8d7b0"))
    cv.stroke([(px - 14, py - 28), (px + 14, py - 28), (px + 14, py - 23), (px - 14, py - 23)], 1.2, INK, 0.7)
    cv.circle(px, py + 4, 10, P.hx("#9a5cff"))
    cv.circle(px - 2, py + 2, 5, P.hx("#d6b8ff"))
    cv.stroke(P.circ_pts(px, py + 4, 10, 10, 20), 1.6, INK, 0.8)
    cv.glow(px, py - 34, 40, P.hx("#b48cff"), 0.6)
    for i in range(8):
        cv.sparkle(px - 30 + 60 * P.hsh(21, i), py - 70 + 46 * P.hsh(22, i), 2 + 2.5 * P.hsh(23, i), P.hx("#e6d4ff"), 0.95)


def scene_market(cv):
    sky(cv, "#58a9ea", "#a6daf7", "#ffe6bf")
    cv.cloud(40, 40, 30, seed=5)
    cv.cloud(196, 28, 26, seed=6, a=0.8)
    # cobblestone ground
    for row in range(5):
        for col in range(9):
            x = col * 28 - (14 if row % 2 else 0)
            y = 150 + row * 18
            c = P.mul(P.hx("#9aa0a6"), 0.8 + 0.3 * P.hsh(row, col, 5))
            cv.poly([(x + 2, y + 2), (x + 26, y + 2), (x + 26, y + 16), (x + 2, y + 16)], c)
            cv.rect(x + 2, y + 2, 24, 3, P.mul(c, 1.15))
    # stall posts + striped awning
    wood = P.hx("#8a5a34")
    cv.box(28, 54, 9, 110, 6, wood, 11, (1, 8))
    cv.box(192, 54, 9, 110, 6, wood, 12, (1, 8))
    red, cream = P.hx("#d9443f"), P.hx("#fff1d6")
    for k in range(8):
        x0 = 14 + k * 26
        col = red if k % 2 == 0 else cream
        pts = [(x0 + 6, 26), (x0 + 32, 26), (x0 + 26, 70), (x0, 70)]
        cv.poly(pts, col)
        cv.poly([(x0, 70), (x0 + 26, 70), (x0 + 13, 80)], P.mul(col, 0.92))
        cv.poly([(x0 + 6, 26), (x0 + 32, 26), (x0 + 31, 32), (x0 + 5, 32)], P.mul(col, 1.08))
    cv.stroke([(20, 26), (222, 26), (222, 70), (14, 70)], 1.6, INK, 0.7, closed=False)
    cv.rect(14, 22, 210, 6, P.hx("#6b4428"))
    # hanging sign with a coin
    cv.line(100, 28, 100, 40, 1.6, INK)
    cv.line(132, 28, 132, 40, 1.6, INK)
    cv.box(92, 40, 48, 20, 4, P.hx("#c8925a"), 14, (4, 2))
    I.coin(cv, 116, 50, 7, tilt=1.0)
    # the counter
    def boards(iu, iv):
        return P.mul(P.hx("#a06a3a"), 0.85 if iu % 2 else 1.0)
    cv.box(22, 120, 180, 46, 16, P.hx("#a06a3a"), 15, (9, 3), pick_front=boards, top=P.hx("#c8925a"))
    # crates of goods on the counter: wheat, apples, carrots, fish
    crate = P.hx("#b0844f")
    for n, (cx, goods) in enumerate(((32, "wheat"), (78, "apple"), (124, "carrot"), (166, "fish"))):
        cv.box(cx, 98, 38, 22, 10, crate, 30 + n, (4, 2))
        if goods == "wheat":
            I.wheat(cv, cx + 19, 86, 34)
        elif goods == "apple":
            for k in range(5):
                ax, ay = cx + 7 + (k % 3) * 11 + (5 if k > 2 else 0), 96 - (8 if k > 2 else 0)
                cv.circle(ax, ay, 6, P.hx("#d8352d"))
                cv.circle(ax - 2, ay - 2, 2, P.hx("#ff9a8a"))
                cv.stroke(P.circ_pts(ax, ay, 6, 6, 16), 1.2, INK, 0.7)
                cv.line(ax, ay - 6, ax + 1, ay - 9, 1.5, P.hx("#5a3a1a"))
        elif goods == "carrot":
            for k in range(4):
                bx = cx + 6 + k * 8
                cv.poly([(bx - 3, 96), (bx + 3, 96), (bx, 108)], P.hx("#f08a30"))
                cv.stroke([(bx - 3, 96), (bx + 3, 96), (bx, 108)], 1.0, INK, 0.6)
                cv.poly([(bx - 3, 96), (bx, 86), (bx + 3, 96)], P.hx("#4f9a36"))
        else:
            I.fish(cv, cx + 19, 92, 30, -0.2)
    # coins in front: two stacks + loose coins + sparkle
    for k in range(6):
        I.coin(cv, 164, 196 - k * 5, 16)
    for k in range(4):
        I.coin(cv, 196, 200 - k * 5, 14)
    for k, (x, y) in enumerate(((40, 196), (64, 204), (90, 198), (124, 206))):
        I.coin(cv, x, y, 11 + (k % 2) * 2)
    for i in range(6):
        cv.sparkle(140 + 80 * P.hsh(41, i), 150 + 30 * P.hsh(42, i), 2 + 2.5 * P.hsh(43, i), (255, 245, 200), 0.95)


def scene_crafting(cv):
    cv.vgrad(0, 0, S, S, [(0.0, P.hx("#2a1c22")), (0.5, P.hx("#5a2f22")), (1.0, P.hx("#2a1a16"))])
    cv.glow(70, 120, 120, P.hx("#ff9a3a"), 0.55)
    # back wall planks
    for k in range(9):
        c = P.mul(P.hx("#5a3a26"), 0.8 + 0.3 * P.hsh(51, k))
        cv.rect(k * 26, 0, 25, 110, c, 0.85)
        cv.rect(k * 26, 0, 3, 110, P.mul(c, 1.25), 0.6)
    # tools hanging on the wall
    I.pickaxe(cv, 196, 40, 46, 0.5)
    I.hatchet(cv, 30, 36, 40, -0.4)
    # the workbench (right back)
    def top_wood(iu, iv):
        return P.mul(P.hx("#b8834e"), 0.9 if iu % 2 else 1.05)
    cv.box(150, 92, 72, 14, 18, P.hx("#9b6a3c"), 52, (6, 1), pick_top=top_wood, top=P.hx("#b8834e"))
    cv.box(154, 106, 8, 48, 4, P.hx("#7a5232"), 53, (1, 4))
    cv.box(210, 106, 8, 48, 4, P.hx("#7a5232"), 54, (1, 4))
    I.flask(cv, 170, 80, 26)
    cv.box(188, 76, 22, 14, 8, P.hx("#6c7680"), 55, (2, 1))                                 # an ingot pile
    # a cooking pot on the floor (left) + a finished sword leaning on the bench leg (right)
    cv.glow(30, 160, 40, P.hx("#ff7a2a"), 0.5)
    I.pot(cv, 30, 158, 52)
    I.sword(cv, 200, 150, 66, 0.25)
    # the anvil (front, centre)
    I.anvil(cv, 104, 140, 150)
    # the hot ingot on the anvil + hammer
    cv.glow(104, 106, 46, P.hx("#ffb040"), 0.85)
    cv.box(84, 98, 40, 10, 10, P.hx("#ff8a2a"), 56, (5, 1), top=P.hx("#ffd36b"), outline=(80, 20, 10))
    I.GOLD  # noqa
    from skyyitems import Glyph
    g = Glyph(cv, 150, 92, 64, 0.85)
    g.bar(0, 16, 0, -6, 3.6, I.WOOD)
    g.fill([(-8, -12), (8, -12), (8, -4), (-8, -4)], P.hx("#7d8892"))
    g.hl([(-8, -12), (8, -12), (8, -10), (-8, -10)], (255, 255, 255), 0.4)
    # sparks
    for i in range(14):
        a = -math.pi * (0.15 + 0.7 * P.hsh(61, i))
        r = 18 + 50 * P.hsh(62, i)
        x, y = 104 + r * math.cos(a), 100 + r * math.sin(a)
        cv.line(x, y, x + 3 * math.cos(a), y + 3 * math.sin(a), 1.6, P.hx("#ffd36b"))
        if i % 3 == 0:
            cv.sparkle(x, y, 2.5 + 2 * P.hsh(63, i), P.hx("#ffe6a0"), 0.95)


def scene_world(cv):
    sky(cv, "#4d97dc", "#9fd2f2", "#ffe2bb")
    cv.glow(180, 40, 60, P.hx("#fff4cc"), 0.8)
    cv.circle(180, 40, 14, P.hx("#fff4cc"))
    cv.cloud(60, 34, 30, seed=11, a=0.8)
    cv.cloud(130, 150, 46, seed=12, a=0.75)
    island(cv, 196, 30, 3.5, 2, 21, haze=0.6, trees=((0, 0, "oak"),))
    island(cv, 56, 70, 7, 2, 22, haze=0.35, trees=((0, -1, "blossom"),))
    island(cv, 150, 92, 11, 3, 23, trees=((-2, 0, "oak"), (1, -2, "oak"), (2, 1, "blossom")))
    # a waterfall pouring off the big island's front edge
    def water(x, y):
        v = 0.5 + 0.5 * math.sin(y * 0.5 + x * 0.9)
        return P.mix(P.hx("#5ab6e8"), P.hx("#d6f2ff"), v)
    cv.poly([(170, 130), (182, 130), (184, 232), (168, 232)], water, 0.92)
    cv.glow(176, 200, 22, (255, 255, 255), 0.5)
    I.compass_rose(cv, 58, 160, 44, 0.0)


def scene_social(cv):
    sky(cv, "#5aa7e8", "#ade0f7", "#ffe8c4")
    cv.cloud(42, 40, 28, seed=31, a=0.85)
    cv.cloud(190, 52, 32, seed=32, a=0.8)
    # a grass hill
    cv.poly([(0, 180), (40, 160), (116, 150), (190, 158), (232, 172), (232, 232), (0, 232)], GRASS_D)
    cv.poly([(0, 186), (40, 166), (116, 156), (190, 164), (232, 178), (232, 232), (0, 232)], GRASS)
    for i in range(18):
        x = 6 + i * 13
        cv.poly([(x, 172 - 6 * math.sin(i)), (x + 2, 164 - 6 * math.sin(i)), (x + 4, 172 - 6 * math.sin(i))], P.hx("#8ad65a"))
    blue = {"skin": SKIN, "hair": P.hx("#2a1e1a"), "shirt": P.hx("#3b6fb0"), "trim": P.hx("#c9d8e6"), "pants": P.hx("#3a3a48"),
            "boots": P.hx("#4a3424"), "eyes": P.hx("#3a8a4a")}
    green = {"skin": P.hx("#c98d63"), "hair": P.hx("#e8c25a"), "shirt": P.hx("#4f9a36"), "trim": P.hx("#d4824a"),
             "pants": P.hx("#5a4636"), "boots": P.hx("#3a2a1e"), "eyes": P.hx("#2f6fb0")}
    red = {"skin": P.hx("#f0c49e"), "hair": P.hx("#b8452e"), "shirt": P.hx("#c0392b"), "trim": I.GOLD, "pants": P.hx("#2f2f3a"),
           "boots": P.hx("#5a3a24"), "eyes": P.hx("#6a3aa0")}
    humanoid(cv, 46, 182, 4.2, blue, wave="left", seed=71)
    humanoid(cv, 186, 182, 4.2, green, wave="right", seed=72)
    humanoid(cv, 116, 192, 5.0, red, wave="right", seed=73)
    # a chat bubble with a heart + a gold party star
    bx, by = 70, 30
    cv.poly([(bx, by), (bx + 44, by), (bx + 44, by + 28), (bx + 18, by + 28), (bx + 10, by + 38), (bx + 10, by + 28), (bx, by + 28)],
            (255, 255, 255))
    cv.stroke([(bx, by), (bx + 44, by), (bx + 44, by + 28), (bx + 18, by + 28), (bx + 10, by + 38), (bx + 10, by + 28), (bx, by + 28)],
              1.8, INK, 0.8)
    hxc, hyc = bx + 22, by + 13
    cv.circle(hxc - 5, hyc - 2, 5.5, P.hx("#e0475a"))
    cv.circle(hxc + 5, hyc - 2, 5.5, P.hx("#e0475a"))
    cv.poly([(hxc - 10.4, hyc), (hxc + 10.4, hyc), (hxc, hyc + 11)], P.hx("#e0475a"))
    cv.circle(hxc - 6.5, hyc - 3.5, 1.8, (255, 200, 210))
    cv.poly(P.star_pts(170, 34, 16, 0.45, 5), I.GOLD_L)
    cv.stroke(P.star_pts(170, 34, 16, 0.45, 5), 1.6, INK, 0.8)
    cv.sparkle(194, 22, 4, (255, 246, 200))
    cv.sparkle(150, 18, 3, (255, 246, 200))


def scene_settings(cv):
    cv.vgrad(0, 0, S, S, [(0.0, P.hx("#1d3554")), (0.6, P.hx("#2d5480")), (1.0, P.hx("#18283e"))])
    for k in range(12):                                                     # a faint blueprint grid
        cv.rect(k * 20, 0, 1, S, P.hx("#6fa8dc"), 0.18)
        cv.rect(0, k * 20, S, 1, P.hx("#6fa8dc"), 0.18)
    cv.glow(100, 90, 110, P.hx("#8fd0ff"), 0.35)
    gear(cv, 90, 92, 66, 54, 12, 0.12, P.hx("#a8b4c0"))
    gear(cv, 176, 52, 40, 31, 9, 0.35, I.GOLD)
    gear(cv, 182, 128, 26, 20, 8, 0.1, P.hx("#d4824a"))
    # the key cap: ALT (the SkyWynn Menu key)
    kx, ky, kw, kh, kd = 104, 150, 92, 40, 14
    cv.box(kx - 6, ky + 4, kw + 12, kh + 6, kd, P.hx("#3a4250"), 91, (6, 2))                 # the switch housing
    cap = P.hx("#e8edf2")
    cv.box(kx, ky - 4, kw, kh, kd, cap, 92, (6, 3), top=P.hx("#ffffff"), jit=0.03)
    tw = P.text_w("ALT", 4)
    cv.text(kx + (kw - tw) / 2.0 + kd * 0.25, ky + 7 - kd * 0.12, "ALT", P.hx("#2d5480"), 4)
    cv.sparkle(kx + kw + 8, ky - 14, 4, (255, 255, 255))
    for i in range(5):
        cv.sparkle(30 + 180 * P.hsh(81, i), 20 + 30 * P.hsh(82, i), 1.6 + 1.6 * P.hsh(83, i), (220, 240, 255), 0.8)


SCENES = {"tab_world_teleport": scene_teleport, "hub_character": scene_character, "hub_storage": scene_storage,
          "hub_market": scene_market, "hub_smithing": scene_crafting, "hub_world": scene_world, "hub_social": scene_social,
          "hub_settings": scene_settings}


def render_tile(stem):
    cv = P.Canvas(S, S, (0, 0, 0))
    SCENES[stem](cv)
    cv.vignette(0.45, 0.30, BAR + 12)
    cv.round_mask(6)
    return cv


# ------------------------------------------------------------------ the review sheet
def tile_mock(pic, label, k, hover=False):
    """the in-game look: picture + the blue label bar (bottom, kit blue at 0.9) + label + the gold edge (hover / selected)"""
    w = pic.w
    cv = P.Canvas(w + 4 * k, w + 4 * k)
    cv.rect(0, 0, w + 4 * k, w + 4 * k, P.hx("#0c1626"))
    cv.paste(pic, 2 * k, 2 * k)
    bar = BAR // 2 * k
    cv.rect(2 * k, 2 * k + w - bar, w, bar, LABEL_BLUE, 0.9)
    cv.rect(2 * k, 2 * k + w - bar, w, k, P.hx("#8fb8e0"), 0.8)
    cv.poly(P.star_pts(2 * k + w / 2.0, 2 * k + w - bar, 3.2 * k, 0.4, 4), I.GOLD_L)
    sc = 2 if k == 2 else 1
    tw = P.text_w(label, sc)
    cv.text(2 * k + (w - tw) / 2.0, 2 * k + w - bar + (bar - 7 * sc) / 2.0 + 1, label, (255, 255, 255), sc,
            shadow=(16, 30, 50) if sc > 1 else None)
    edge = FRAME_GOLD if hover else P.hx("#2a4a6a")
    cv.stroke([(k, k), (w + 3 * k, k), (w + 3 * k, w + 3 * k), (k, w + 3 * k)], 2 * k if hover else k, edge, 1.0)
    return cv


def build_sheet(pics):
    pad = 24
    tw2 = S + 8
    W = pad + 8 * (tw2 + pad)
    H = 1250
    cv = P.Canvas(W, H, P.hx("#0e1a2b"))
    cv.text(pad, 18, "SKYWYNN MENU - PICTURE TILES, PHASE 1 (THE 8 HOME TILES) - CONCEPT V1, CLOUD 2026-10-22", P.hx("#ffd36b"), 3)
    cv.text(pad, 50, "ORIGINAL ART: CHUNKY VOXEL SCENES OF REAL GAME THINGS. PNG = 232 X 232 (@2X) + 116 X 116. THE PAGE DRAWS THE BLUE "
                     "LABEL BAR (22 PX) + GOLD EDGE ON HOVER.", P.hx("#c9d8e6"), 2)
    y = 84
    cv.text(pad, y, "@2X (232 PX) WITH THE LABEL BAR - FIRST ONE SHOWS THE GOLD HOVER EDGE", P.hx("#8fb8e0"), 2)
    y += 24
    for n, (stem, label, key, slot) in enumerate(TILES):
        m = tile_mock(pics[stem], label, 2, hover=(n == 0))
        x = pad + n * (tw2 + pad)
        cv.paste(m, x, y)
        cv.text(x, y + m.h + 8, stem + "@2X.PNG", P.hx("#9fb3c8"), 1)
        cv.text(x, y + m.h + 20, key + ("  HOME SLOT %d" % slot if slot is not None else "  (NOT ON THE DEFAULT HOME)"),
                P.hx("#9fb3c8"), 1)
    y += tw2 + 50
    cv.text(pad, y, "1X (116 PX, THE REAL SIZE ON A 1080 SCREEN) WITH THE LABEL BAR", P.hx("#8fb8e0"), 2)
    y += 24
    small = {}
    for n, (stem, label, key, slot) in enumerate(TILES):
        sm = P.downscale2(pics[stem])
        small[stem] = sm
        m = tile_mock(sm, label, 1, hover=(n == 0))
        cv.paste(m, pad + n * (m.w + 18), y)
    y += 150
    cv.text(pad, y, "THE DEFAULT HOME GRID AT 1X (5 X 5 SLOTS OF 120 PX; WORLD IS NOT PINNED BY DEFAULT SINCE 0.3.30)",
            P.hx("#8fb8e0"), 2)
    y += 24
    slot_of = dict((t[3], t) for t in TILES if t[3] is not None)
    gx = pad
    for r in range(5):
        for c in range(5):
            s = r * 5 + c
            x0, y0 = gx + c * 124, y + r * 124
            if s in slot_of:
                stem, label = slot_of[s][0], slot_of[s][1]
                cv.paste(tile_mock(small[stem], label, 1, hover=(s == 12)), x0, y0)
            else:
                cv.rect(x0, y0, 120, 120, P.hx("#13233a"))
                cv.stroke([(x0 + 1, y0 + 1), (x0 + 119, y0 + 1), (x0 + 119, y0 + 119), (x0 + 1, y0 + 119)], 1, P.hx("#2a4a6a"), 1.0)
    # notes next to the grid
    nx = gx + 5 * 124 + 40
    notes = ["WHAT EACH PICTURE SAYS:",
             "TELEPORT - A SKY ISLAND WITH A STONE ARCH + SWIRLING SHARD PORTAL",
             "CHARACTER - AN ADVENTURER IN BLACK LEATHER + COPPER TRIM (OUR T1 LIGHT ARMOR)",
             "            RINGED BY SKILL BADGES: MINING, COMBAT, FARMING, FISHING, FORAGING, ALCHEMY",
             "STORAGE - THE BANK VAULT DOOR, A CHEST, THE POCKET DIMENSION POUCH (VIOLET SPARKLES)",
             "MARKET - A BAZAAR STALL: STRIPED AWNING, CRATES OF WHEAT / APPLES / CARROTS / FISH, COIN STACKS",
             "CRAFTING - THE ANVIL WITH A GLOWING INGOT + HAMMER, THE WORKBENCH, TOOLS ON THE WALL, SPARKS",
             "WORLD - FLOATING ISLANDS (ONE WITH A WATERFALL) + A GOLD COMPASS ROSE",
             "SOCIAL - THREE PLAYERS WAVING, A HEART CHAT BUBBLE, A PARTY STAR",
             "SETTINGS - STEEL / GOLD / COPPER GEARS + THE ALT KEY CAP (THE MENU KEY)",
             "",
             "KEEP CLEAR: THE BOTTOM 22 PX (1X) SIT UNDER THE LABEL BAR.",
             "PHASE 2 (31 HUB TABS + 3 TELEPORTS) FOLLOWS THE SAME LOOK AFTER YOUR OK."]
    for k, line in enumerate(notes):
        cv.text(nx, y + 6 + k * 22, line, P.hx("#ffd36b") if k == 0 else P.hx("#c9d8e6"), 2)
    return cv, small


def main():
    check = "--check" in sys.argv
    outdir = os.path.join(HERE, "tiles")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    pics = {}
    files = {}
    for stem, label, key, slot in TILES:
        pics[stem] = render_tile(stem)
    sheet, small = build_sheet(pics)
    for stem, label, key, slot in TILES:
        files["tiles/%s@2x.png" % stem] = P.png_bytes(pics[stem])
        files["tiles/%s.png" % stem] = P.png_bytes(small[stem])
    files["sheet.png"] = P.png_bytes(sheet)
    man = []
    for rel in sorted(files):
        data = files[rel]
        w, h = P.struct.unpack(">II", data[16:24])
        man.append({"path": rel, "w": w, "h": h, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if check:
        old = json.load(open(os.path.join(HERE, "manifest.json")))
        same = [m["sha256"] for m in old["files"]] == [m["sha256"] for m in man]
        print("deterministic: %s" % ("SAME BYTES" if same else "DIFFERENT"))
        sys.exit(0 if same else 1)
    for rel, data in files.items():
        with open(os.path.join(HERE, rel), "wb") as f:
            f.write(data)
    meta = {"what": "SkyWynn Menu picture tiles phase 1 (concept v1)", "generator": "make_tiles.py",
            "tiles": [{"file": t[0], "label": t[1], "key": t[2], "home_slot": t[3]} for t in TILES], "files": man}
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
        f.write("\n")
    for m in man:
        print("%-36s %4d x %-4d %7d bytes" % (m["path"], m["w"], m["h"], m["bytes"]))


if __name__ == "__main__":
    main()
