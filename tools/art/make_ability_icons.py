#!/usr/bin/env python3
"""make_ability_icons - SkyWynn class ability icons, Mage + Priest + Monk + Assassin + Warrior (5 per class, 64x64 RGBA), our own art drawn from code.

Each icon = a round dark frame with a CLASS-COLOUR RIM (Mage #7fb0e0, Priest #f2e6a0 - the class emblem colours,
research/cloud/class-art/README.md) around a dark field tinted toward the class colour, with one bold bevelled symbol that
reads the ability (research/cloud/Class-Ability-Shapes.md sections 4 + 5). Paint engine: ability_icon_core.py.
No vanilla file is read, copied or traced. numpy + Pillow only. Deterministic: two runs = same bytes.

Run:  python3 make_ability_icons.py [--out DIR] [--only Meteor,FrostNova]
Out:  <out>/Common/Icons/Abilities/<Class>/<AbilityName>.png
"""
import argparse
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ability_icon_core as K  # noqa: E402
from ability_icon_core import (Layer, capsule, circle, ellipse, ering, glow, heart, hx, line, poly, ramp, ring,  # noqa: E402
                               rotpts, rs, star, X, Y)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "art", "ability-icons")

# ------------------------------------------------------------------------------------------------------------------ palettes
# every ramp runs dark -> light; shadows lean cool / violet, lights lean warm; no #000 / #fff
FRAME = ramp("#0e111a", "#171c28", "#212838", "#2d3649", "#3e4a60", "#55627a")          # dark slate frame band
MAGE_RIM = ramp("#1f2f5c", "#2f4f88", "#4f7fba", "#7fb0e0", "#b2d4f2", "#e0eefa")       # from Mage #7fb0e0
PRIEST_RIM = ramp("#4a3416", "#7c6028", "#b39a4c", "#dccb7c", "#f2e6a0", "#fcf5d4")     # from Priest #f2e6a0

FIRE = ramp("#4c1020", "#8a1e1a", "#c8401a", "#ec7424", "#ffaa3c", "#ffd878", "#fff1c0")
ROCK = ramp("#1c1222", "#2e1c30", "#47293c", "#653a46", "#865450", "#a8725e", "#c8987a")
ARCANE = ramp("#22104a", "#3a1a7e", "#5a2cb4", "#8250e2", "#ab82f6", "#d2bcff", "#f1e8ff")
MANA = ramp("#0e1f56", "#16378e", "#2356c4", "#2f6fe0", "#5c9af2", "#9cc8fc", "#def0ff")
ICE = ramp("#173a6e", "#22609e", "#3a8cc6", "#62b6e0", "#98d8f0", "#cdeefa", "#f0fbff")
STARLIGHT = ramp("#3a2c78", "#5e4cae", "#8c80d6", "#bab4ee", "#e2def8", "#fbf6e6")
GOLD = ramp("#3e2208", "#6c4210", "#a06a1c", "#cf9a30", "#ecc458", "#f9e290", "#fff4cc")
HOLY = ramp("#6e4e1c", "#a07a34", "#cfa850", "#ead27e", "#f8ecb4", "#fff9e4")         # ivory-gold light
SOUL = ramp("#0f4a58", "#1c7686", "#2ea8b4", "#5ed2d8", "#a2eeee", "#dcfcf8")         # priest soul cyan (soul cage v2)
ROSE = ramp("#4a0f26", "#801c34", "#b72e44", "#de4c58", "#f47c7c", "#ffb4a8", "#ffe2d6")
FEATHER = ramp("#5a4c64", "#867a8c", "#b2a8b2", "#d6cec8", "#eee6da", "#fbf6ea")
STEEL = ramp("#2a2c40", "#43475e", "#62687e", "#868ca0", "#aeb4c2", "#d6dae2", "#f0f2f4")

MAGE = K.Style("Mage", "#7fb0e0", MAGE_RIM, field_c="#26335e", field_e="#0e1226",
               outline="#090a18", frame=FRAME, glow_c="#7fb0e0")
PRIEST = K.Style("Priest", "#f2e6a0", PRIEST_RIM, field_c="#43381e", field_e="#15100c",
                 outline="#120a06", frame=FRAME, glow_c="#f2e6a0")


def L3():
    return Layer(), Layer(), Layer()


def sparkle(layer, cx, cy, r, col, core=None, w=0.55):
    """4-point twinkle (a thin plus with a soft core) - painted on FRONT"""
    m = (capsule(cx - r, cy, cx + r, cy, w, w) | capsule(cx, cy - r, cx, cy + r, w, w))
    layer.put(m, hx(col))
    if core:
        layer.put(circle(cx, cy, w * 1.4), hx(core))


# ================================================================================================================= MAGE
def meteor():
    """Meteor: a burning rock diving from the top right toward the lower left - the 'pick a spot, it lands' nuke"""
    back, g, front = L3()
    # tail direction (unit) from the rock toward the upper right
    rx, ry = 24.0, 40.0
    ux, uy = 0.62, -0.78
    tail_len = 30.0
    # soft orange glow behind
    glow(back, circle(rx + ux * 8, ry + uy * 8, 13), "#d8501c", 5.0, 0.55)
    glow(back, circle(rx, ry, 9), "#ffb040", 3.0, 0.35)
    # fire trail: a tapered teardrop, three flame tongues; colour by distance along the tail and from its axis
    tx, ty = rx + ux * tail_len, ry + uy * tail_len
    trail = capsule(rx, ry, tx, ty, 10.5, 2.2)
    trail |= capsule(rx - 3.5, ry - 1.5, rx - 3.5 + ux * 21, ry - 1.5 + uy * 21, 4.6, 1.2)
    trail |= capsule(rx + 2.5, ry + 3.5, rx + 2.5 + ux * 22, ry + 3.5 + uy * 22, 4.4, 1.2)
    along = np.clip(((X - rx) * ux + (Y - ry) * uy) / tail_len, 0, 1)
    across = np.abs((X - rx) * (-uy) + (Y - ry) * ux) / (10.5 - 8.3 * along)
    heat = 1.0 - along * 0.95 - np.clip(across, 0, 1.4) * 0.55
    g.put(trail, rs(FIRE, 0.18 + heat * 0.9))
    # arcane fringe at the very tail (Mage fire)
    fringe = trail & (along > 0.62) & (across > 0.55)
    g.put(fringe, rs(ARCANE, 0.45 + (1 - along) * 0.4))
    # the rock: an irregular faceted boulder
    rock_pts = [(rx - 9.0, ry - 1.0), (rx - 6.5, ry - 7.0), (rx - 0.5, ry - 9.2), (rx + 6.0, ry - 7.4), (rx + 9.0, ry - 1.5),
                (rx + 7.4, ry + 5.6), (rx + 1.5, ry + 9.2), (rx - 5.6, ry + 7.8)]
    rock = poly(rock_pts)
    g.bevel(rock, ROCK, face=0.58, bevel=2.0, grad=0.34, gain=1.0)
    # big facet planes: a lit top-left plane + a dark lower-right plane
    plane = poly([(rx - 6.5, ry - 7.0), (rx - 0.5, ry - 9.2), (rx + 2.5, ry - 3.0), (rx - 4.0, ry - 1.5)]) & rock
    g.bevel(plane, ROCK, face=0.88, bevel=0.9, grad=0.1, gain=0.6)
    plane2 = poly([(rx + 2.5, ry - 3.0), (rx + 9.0, ry - 1.5), (rx + 7.4, ry + 5.6), (rx + 1.5, ry + 9.2),
                   (rx - 0.5, ry + 3.0)]) & rock
    g.bevel(plane2, ROCK, face=0.42, bevel=0.9, grad=0.18, gain=0.5)
    # molten cracks (glowing orange lines) on the leading face
    crack = line([(rx - 5.5, ry + 4.5), (rx - 2.0, ry + 2.0), (rx + 0.5, ry + 5.0), (rx + 3.5, ry + 3.0)], 1.3)
    g.put(crack & rock, rs(FIRE, 0.72))
    # embers flying off (front)
    for ex, ey, er in ((44.0, 33.5, 1.0), (37.0, 44.0, 0.9), (46.5, 24.5, 0.8), (14.5, 31.5, 0.8)):
        front.put(circle(ex, ey, er), rs(FIRE, 0.82))
    glints = [(21, 32, "#e8c0a0"), (22, 32, "#d6a88a"), (30, 40, "#fff1c0")]
    return back, g, front, glints


def hex_edges(cx, cy, R, size, w):
    """hexagon cell edges as seen on a sphere of radius R centred (cx, cy): screen -> surface by arcsin, pointy-top hexes"""
    u = R * np.arcsin(np.clip((X - cx) / R, -1, 1))
    v = R * np.arcsin(np.clip((Y - cy) / R, -1, 1))
    q = (math.sqrt(3) / 3 * u - v / 3.0) / size
    r = (2.0 / 3.0 * v) / size
    xq, zq = q, r
    yq = -xq - zq
    rx, ry, rz = np.round(xq), np.round(yq), np.round(zq)
    dx, dy, dz = np.abs(rx - xq), np.abs(ry - yq), np.abs(rz - zq)
    fx = (dx > dy) & (dx > dz)
    fy = ~fx & (dy > dz)
    rx = np.where(fx, -ry - rz, rx)
    ry = np.where(fy, -rx - rz, ry)
    rz = np.where(~fx & ~fy, -rx - ry, rz)
    hcx = size * (math.sqrt(3) * rx + math.sqrt(3) / 2 * rz)
    hcy = size * 1.5 * rz
    lx, ly = u - hcx, v - hcy
    d = np.maximum(np.abs(lx), np.maximum(np.abs(lx * 0.5 + ly * 0.866), np.abs(lx * 0.5 - ly * 0.866)))
    return d > (size * math.sqrt(3) / 2 - w)


def mana_barrier():
    """Mana Barrier: a glassy blue hex-panel dome over a rune ring; a glowing mana crystal inside (damage drains Mana)"""
    back, g, front = L3()
    cx, gy, R = 32.0, 44.5, 21.5
    dome = circle(cx, gy, R) & (Y <= gy)
    rr = np.sqrt((X - cx) ** 2 + (Y - gy) ** 2) / R
    # glassy dome: mostly see-through in the middle, brighter toward the shell (fresnel)
    glow(back, dome, "#2356c4", 3.0, 0.45)
    back.put(dome, rs(MANA, 0.50 + 0.36 * rr ** 2.5), alpha=0.42 + 0.45 * rr ** 3)
    hexm = hex_edges(cx, gy, R, 6.8, 0.75) & dome & ~circle(cx, gy, R - 1.4)
    back.put(hexm, rs(MANA, 0.90), alpha=0.75 + 0.25 * rr)
    # rune ring on the ground (ellipse) - opaque, bevelled
    g.bevel(ering(cx, gy, 23.0, 4.6, 2.2), MANA, face=0.62, bevel=0.8, grad=0.3, gain=0.6)
    # dome shell: bright 2 px arc, lit top-left
    shell = circle(cx, gy, R) & ~circle(cx, gy, R - 2.2) & (Y <= gy + 0.2)
    ang = np.arctan2(Y - gy, X - cx)
    g.put(shell, rs(MANA, 0.66 + 0.30 * np.clip(-np.cos(ang + 0.6), -1, 1)))
    # mana crystal: a tall faceted diamond, glowing
    my = 35.0
    cr = poly([(cx, my - 10.0), (cx + 6.4, my - 1.0), (cx, my + 7.5), (cx - 6.4, my - 1.0)])
    glow(back, cr, "#5c9af2", 4.0, 0.9)
    g.bevel(cr, MANA, face=0.58, bevel=1.3, grad=0.3, gain=0.8)
    left_up = poly([(cx, my - 10.0), (cx, my - 1.0), (cx - 6.4, my - 1.0)]) & cr
    g.bevel(left_up, MANA, face=0.92, bevel=0.0001, grad=0.15, gain=0.0)
    right_up = poly([(cx, my - 10.0), (cx + 6.4, my - 1.0), (cx, my - 1.0)]) & cr
    g.bevel(right_up, MANA, face=0.70, bevel=0.0001, grad=0.15, gain=0.0)
    left_lo = poly([(cx, my - 1.0), (cx, my + 7.5), (cx - 6.4, my - 1.0)]) & cr
    g.bevel(left_lo, MANA, face=0.52, bevel=0.0001, grad=0.2, gain=0.0)
    right_lo = poly([(cx, my - 1.0), (cx + 6.4, my - 1.0), (cx, my + 7.5)]) & cr
    g.bevel(right_lo, MANA, face=0.30, bevel=0.0001, grad=0.15, gain=0.0)
    # dome highlight streak (front), top-left
    hl = circle(cx, gy, R - 3.2) & ~circle(cx, gy, R - 4.6) & (ang < -1.95) & (ang > -2.7)
    front.put(hl, hx("#cfe6ff"), alpha=0.9)
    sparkle(front, 40.5, 30.0, 1.6, "#9cc8fc", None, 0.42)
    sparkle(front, 24.0, 36.0, 1.3, "#9cc8fc", None, 0.42)
    glints = [(31, 28, "#def0ff"), (30, 30, "#def0ff")]
    return back, g, front, glints


def frost_nova():
    """Frost Nova: a six-armed ice crystal bursting outward with a frost ring and outward ice shards (freeze around you)"""
    back, g, front = L3()
    cx, cy = 32.0, 32.0
    # frost ring shockwave
    glow(back, circle(cx, cy, 10), "#98d8f0", 7.0, 0.7)
    # outward ice shards between the arms (on the ring)
    shards = np.zeros(X.shape, bool)
    for k in range(6):
        a = math.radians(-60 + k * 60 + 30)
        ca, sa = math.cos(a), math.sin(a)
        r0, r1, w = 13.5, 23.8, 3.3
        px, py = -sa, ca
        shards |= poly([(cx + ca * r0 + px * w, cy + sa * r0 + py * w), (cx + ca * r1, cy + sa * r1),
                        (cx + ca * r0 - px * w, cy + sa * r0 - py * w)])
    g.bevel(shards, ICE, face=0.5, bevel=1.0, grad=0.3, gain=0.9)
    # the snowflake: 6 arms, each a long tapered bar with one V branch
    flake = np.zeros(X.shape, bool)
    for k in range(6):
        a = math.radians(-90 + k * 60)
        ca, sa = math.cos(a), math.sin(a)
        ex, ey = cx + ca * 17.0, cy + sa * 17.0
        flake |= capsule(cx, cy, ex, ey, 2.4, 1.3)
        bx, by = cx + ca * 10.0, cy + sa * 10.0
        for s in (-1, 1):
            b = a + s * math.radians(50)
            flake |= capsule(bx, by, bx + math.cos(b) * 5.0, by + math.sin(b) * 5.0, 1.25, 0.9)
    flake |= poly([(cx + 6.2 * math.cos(math.radians(-90 + k * 60)), cy + 6.2 * math.sin(math.radians(-90 + k * 60)))
                   for k in range(6)])
    g.bevel(flake, ICE, face=0.62, bevel=1.1, grad=0.32, gain=0.85)
    # centre gem
    core = poly([(cx + 3.4 * math.cos(math.radians(-90 + k * 60)), cy + 3.4 * math.sin(math.radians(-90 + k * 60)))
                 for k in range(6)])
    g.bevel(core, ICE, face=0.88, bevel=0.8, grad=0.2, gain=0.5)
    glints = [(31, 30, "#f0fbff"), (31, 16, "#f0fbff")]
    return back, g, front, glints


def starfall():
    """Starfall: a shower of stars streaking down on an area (several stars, cool starlight, violet trails)"""
    back, g, front = L3()
    ux, uy = 0.66, -0.75            # trail direction (up-right)
    stars = [(23.5, 40.0, 11.5, 0.0), (42.0, 27.5, 7.4, 8.0), (40.5, 46.0, 5.4, -6.0)]
    for sx, sy, sr, rot in stars:
        ln = sr * 2.4
        tr = capsule(sx, sy, sx + ux * ln, sy + uy * ln, sr * 0.62, sr * 0.12)
        along = np.clip(((X - sx) * ux + (Y - sy) * uy) / ln, 0, 1)
        glow(back, tr, "#8250e2", 1.2, 0.45)
        back.put(tr, rs(ARCANE, 0.85 - along * 0.55), alpha=np.clip(1.05 - along, 0, 1) * 0.95)
        glow(back, circle(sx, sy, sr * 0.8), "#bab4ee", sr * 0.45, 0.45)
    for sx, sy, sr, rot in stars:
        m = star(sx, sy, sr, sr * 0.47, 5, -90 + rot)
        g.bevel(m, STARLIGHT, face=0.66, bevel=max(0.8, sr * 0.16), grad=0.34, gain=0.95)
    # background star dots + twinkles (deliberate, sparse)
    for px, py in ((16, 26), (31, 15)):
        front.put(circle(px + 0.5, py + 0.5, 0.55), hx("#d2bcff"))
    sparkle(front, 46.5, 17.5, 2.2, "#e2def8", None, 0.5)
    glints = [(21, 36, "#fbf6e6"), (40, 26, "#fbf6e6")]
    return back, g, front, glints


def arcane_beam():
    """Arcane Beam: a violet orb firing a thick channelled beam of light, rune rings round it (a beam that ramps up)"""
    back, g, front = L3()
    ox, oy = 20.0, 44.0
    ux, uy = 0.66, -0.75
    bl = 42.0
    ex, ey = ox + ux * bl, oy + uy * bl
    across = np.abs((X - ox) * (-uy) + (Y - oy) * ux)
    along_raw = ((X - ox) * ux + (Y - oy) * uy) / bl
    along = np.clip(along_raw, 0, 1)
    wid = 3.4 + 3.2 * along                                  # the beam widens as it ramps up
    beam = (across <= wid) & (along_raw >= 0)
    glow(back, beam, "#8250e2", 3.2, 1.0)
    glow(back, beam, "#ab82f6", 1.4, 0.6)
    k = np.clip(across / wid, 0, 1)
    # light: white-lavender core, violet edge; the beam is LIGHT, so it sits in the glyph layer as an opaque band
    back.put(beam, rs(ARCANE, 1.0 - k ** 1.4 * 0.58))
    back.put(beam & (k > 0.82), rs(ARCANE, 0.5))
    # thin dark edge line so the beam has a clean silhouette at 32 px (done by the outline pass)
    # rune rings across the beam
    ang = math.degrees(math.atan2(uy, ux))
    for f, rr in ((0.50, 8.8),):
        cx, cy = ox + ux * bl * f, oy + uy * bl * f
        rg = ering(cx, cy, 2.8, rr, 1.4, rot=ang)
        side = (X - cx) * ux + (Y - cy) * uy
        g.put(rg & (side < 0), rs(ARCANE, 0.66))
        g.put(rg & (side >= 0), rs(ARCANE, 0.86))
    # the orb (focus) in a gold 4-prong cradle
    orb = circle(ox, oy, 7.8)
    glow(back, orb, "#ab82f6", 4.5, 0.8)
    prong = np.zeros(X.shape, bool)
    for a in (105, 165, 235, 30):
        r = math.radians(a)
        prong |= capsule(ox + math.cos(r) * 6.2, oy + math.sin(r) * 6.2, ox + math.cos(r) * 10.0, oy + math.sin(r) * 10.0, 1.4, 1.0)
    g.bevel(prong, GOLD, face=0.58, bevel=0.7, grad=0.2, gain=0.8)
    d = np.sqrt((X - (ox - 2.4)) ** 2 + (Y - (oy - 2.6)) ** 2) / 10.0
    g.put(orb, rs(ARCANE, 0.96 - d * 0.9))
    sparkle(front, 47.0, 37.0, 2.1, "#d2bcff", None, 0.5)
    sparkle(front, 31.0, 22.0, 1.7, "#d2bcff", None, 0.45)
    glints = [(17, 40, "#f1e8ff"), (18, 40, "#d2bcff")]
    return back, g, front, glints


# ================================================================================================================= PRIEST
def sacred_heal():
    """Sacred Heal: a radiant golden healing cross bursting light in a circle (big instant group heal + heal over time)"""
    back, g, front = L3()
    cx, cy = 32.0, 32.0
    # sunburst rays behind (12 rays)
    rays = np.zeros(X.shape, bool)
    for k in range(12):
        a = math.radians(k * 30 + 15)
        r1 = 25.0 if k % 2 == 0 else 20.0
        w = 3.0 if k % 2 == 0 else 2.0
        ca, sa = math.cos(a), math.sin(a)
        rays |= poly([(cx - sa * w, cy + ca * w), (cx + ca * r1, cy + sa * r1), (cx + sa * w, cy - ca * w)])
    glow(back, circle(cx, cy, 11), "#f8e48e", 7.0, 0.65)
    rr = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    back.put(rays, rs(HOLY, 0.95 - rr / 45), alpha=np.clip(1.2 - rr / 26, 0, 1) * 0.85)
    # heal ring
    # the cross: a bold plus with slightly flared ends
    a, w, fl = 17.0, 5.0, 6.6
    cross = poly([(cx - w, cy - a), (cx + w, cy - a), (cx + w, cy - w), (cx + a, cy - w), (cx + a, cy + w), (cx + w, cy + w),
                  (cx + w, cy + a), (cx - w, cy + a), (cx - w, cy + w), (cx - a, cy + w), (cx - a, cy - w), (cx - w, cy - w)])
    for (x0, y0, x1, y1) in ((cx - fl, cy - a, cx + fl, cy - a + 2.2), (cx - fl, cy + a - 2.2, cx + fl, cy + a),
                             (cx - a, cy - fl, cx - a + 2.2, cy + fl), (cx + a - 2.2, cy - fl, cx + a, cy + fl)):
        cross |= poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    g.bevel(cross, GOLD, face=0.64, bevel=1.8, grad=0.34, gain=0.95)
    # inset ivory face (holy light inside the gold)
    inset = poly([(cx - 1.7, cy - a + 3.4), (cx + 1.7, cy - a + 3.4), (cx + 1.7, cy - 1.7), (cx + a - 3.4, cy - 1.7),
                  (cx + a - 3.4, cy + 1.7), (cx + 1.7, cy + 1.7), (cx + 1.7, cy + a - 3.4), (cx - 1.7, cy + a - 3.4),
                  (cx - 1.7, cy + 1.7), (cx - a + 3.4, cy + 1.7), (cx - a + 3.4, cy - 1.7), (cx - 1.7, cy - 1.7)])
    g.bevel(inset, HOLY, face=0.82, bevel=0.6, grad=0.3, gain=-0.6)
    sparkle(front, 47.5, 17.0, 2.6, "#fff4cc", None, 0.55)
    sparkle(front, 16.5, 46.0, 2.0, "#fff4cc", None, 0.5)
    glints = [(28, 17, "#fff4cc"), (17, 28, "#fff4cc")]
    return back, g, front, glints


def shield_bubble():
    """Shield Bubble: a glowing protective bubble with a holy shield inside (a placed bubble that heals as it breaks)"""
    back, g, front = L3()
    cx, cy, R = 32.0, 32.0, 21.0
    bub = circle(cx, cy, R)
    rr = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / R
    # translucent bubble: brighter toward the rim (fresnel), soul-cyan tint with a warm top
    glow(back, ring(cx, cy, R, R - 3), "#5ed2d8", 2.5, 0.45)
    back.put(bub, rs(SOUL, 0.30 + 0.55 * rr ** 3), alpha=0.25 + 0.6 * rr ** 3)
    # rim
    rim = ring(cx, cy, R, R - 1.7)
    ang = np.arctan2(Y - cy, X - cx)
    g.put(rim, rs(SOUL, 0.6 + 0.32 * np.clip(-np.sin(ang) * 0.8 - np.cos(ang) * 0.4, -1, 1)))
    # heater shield inside
    sh = poly([(cx - 9.5, cy - 11.0), (cx + 9.5, cy - 11.0), (cx + 9.5, cy - 1.0), (cx + 7.0, cy + 6.0),
               (cx, cy + 12.5), (cx - 7.0, cy + 6.0), (cx - 9.5, cy - 1.0)])
    g.bevel(sh, GOLD, face=0.6, bevel=1.3, grad=0.35, gain=0.9)
    face = poly([(cx - 7.0, cy - 8.6), (cx + 7.0, cy - 8.6), (cx + 7.0, cy - 1.4), (cx + 5.0, cy + 4.6),
                 (cx, cy + 9.6), (cx - 5.0, cy + 4.6), (cx - 7.0, cy - 1.4)])
    g.bevel(face, STEEL, face=0.68, bevel=0.9, grad=0.45, gain=-0.7)
    # split field: right half darker (heraldic per-pale, like the class crest)
    rh = face & (X > cx)
    g.bevel(rh, STEEL, face=0.50, bevel=0.0001, grad=0.4, gain=0.0)
    # soul gem in the middle of the shield
    gem = poly([(cx, cy - 4.8), (cx + 3.6, cy - 0.8), (cx, cy + 3.6), (cx - 3.6, cy - 0.8)])
    g.bevel(gem, SOUL, face=0.62, bevel=0.9, grad=0.3, gain=0.9)
    glow(back, gem, "#5ed2d8", 2.0, 0.4)
    # bubble highlight (front): curved streak top-left + small dot
    hl = ring(cx, cy, R - 3.0, R - 4.6) & (ang < -1.9) & (ang > -2.85)
    front.put(hl, hx("#e6fbf8"), alpha=0.9)
    front.put(circle(cx - 14.2, cy - 6.0, 0.9), hx("#e6fbf8"), alpha=0.9)
    glints = [(30, 27, "#dcfcf8"), (24, 22, "#fff4cc")]
    return back, g, front, glints


def guardian_spirit():
    """Guardian Spirit: angel wings and a halo around a glowing soul (passive - saves a dying ally in your aura)"""
    back, g, front = L3()
    cx, cy = 32.0, 33.0
    glow(back, circle(cx, cy, 9), "#5ed2d8", 7.0, 0.6)
    glow(back, circle(cx, cy - 2, 18), "#f2e6a0", 6.0, 0.25)
    # wings: three feather rows each side (long primaries at the bottom, short coverts on top)
    for s in (-1, 1):
        rows = [  # (root x off, root y, tip x off, tip y, root r, tip r)
            (4.0, cy - 2.5, 21.5, cy - 15.5, 3.8, 1.9),
            (4.5, cy + 0.5, 23.0, cy - 7.0, 3.4, 1.7),
            (4.5, cy + 3.5, 21.5, cy + 1.5, 3.1, 1.5),
            (4.0, cy + 6.0, 17.5, cy + 9.0, 2.8, 1.4),
        ]
        wing = np.zeros(X.shape, bool)
        parts = []
        for (rx0, ry0, tx0, ty0, r0, r1) in rows:
            m = capsule(cx + s * rx0, ry0, cx + s * tx0, ty0, r0, r1)
            parts.append(m)
            wing |= m
        # draw bottom row first so upper rows overlap (feather layering)
        for m, f in zip(reversed(parts), (0.48, 0.56, 0.64, 0.72)):
            g.bevel(m, FEATHER, face=f, bevel=1.0, grad=0.25, gain=0.85)
        # covert (shoulder) mass
        cov = capsule(cx + s * 4.0, cy - 2.0, cx + s * 13.0, cy - 7.5, 4.3, 3.2)
        g.bevel(cov, FEATHER, face=0.80, bevel=1.2, grad=0.3, gain=0.8)
    # soul: a cyan teardrop flame rising
    soul = circle(cx, cy + 2.0, 5.6) | poly([(cx - 5.2, cy + 0.6), (cx, cy - 10.5), (cx + 5.2, cy + 0.6)])
    d = np.sqrt((X - (cx - 1.4)) ** 2 + (Y - (cy + 0.4)) ** 2) / 9.0
    g.put(soul, rs(SOUL, 0.98 - d * 0.75))
    inner = circle(cx, cy + 2.4, 2.6) | poly([(cx - 2.4, cy + 1.8), (cx, cy - 4.2), (cx + 2.4, cy + 1.8)])
    g.put(inner, rs(SOUL, 1.0))
    # halo
    halo = ering(cx, cy - 15.5, 9.0, 3.4, 2.2)
    g.bevel(halo, GOLD, face=0.72, bevel=0.6, grad=0.4, gain=0.6)
    glow(back, halo, "#f9e290", 2.0, 0.5)
    glints = [(31, 26, "#dcfcf8"), (26, 18, "#fff4cc")]
    return back, g, front, glints


def sanctuary():
    """Sanctuary: a holy arch of light standing in a glowing rune circle on the ground (a healing zone)"""
    back, g, front = L3()
    cx, gy = 32.0, 45.0
    # ground circle glow + light column inside the arch
    glow(back, ellipse(cx, gy, 20, 6), "#f2e6a0", 3.0, 0.55)
    door = poly([(cx - 7.4, gy + 1.0), (cx - 7.4, gy - 20.0), (cx - 4.8, gy - 25.6), (cx, gy - 29.8), (cx + 4.8, gy - 25.6),
                 (cx + 7.4, gy - 20.0), (cx + 7.4, gy + 1.0)])
    t = np.clip((gy - Y) / 30.0, 0, 1)
    glow(back, door, "#f8ecb4", 3.0, 0.6)
    back.put(door, rs(HOLY, 0.98 - t * 0.38), alpha=0.95 - t * 0.35)
    back.put(ellipse(cx, gy, 19.5, 5.6), rs(HOLY, 0.62), alpha=0.55)
    # rune ring (opaque gold) + inner ring
    g.bevel(ering(cx, gy, 21.5, 6.4, 2.5), GOLD, face=0.62, bevel=0.7, grad=0.4, gain=0.6)
    # small rune ticks on the ring's front
    for k in (-2, -1, 0, 1, 2):
        x = cx + k * 7.0
        yy = gy + 6.4 * math.sqrt(max(0.0, 1 - ((x - cx) / 21.5) ** 2)) - 1.0
        front.put(circle(x, yy, 0.7), hx("#fff4cc"))
    # pointed (gothic) arch: two pillars + a lancet top
    outer = poly([(cx - 12.5, gy - 1.0), (cx - 12.5, gy - 21.0), (cx - 9.0, gy - 29.0), (cx, gy - 35.0), (cx + 9.0, gy - 29.0),
                  (cx + 12.5, gy - 21.0), (cx + 12.5, gy - 1.0)])
    innr = poly([(cx - 7.2, gy - 1.0), (cx - 7.2, gy - 20.0), (cx - 4.8, gy - 25.6), (cx, gy - 29.6), (cx + 4.8, gy - 25.6),
                 (cx + 7.2, gy - 20.0), (cx + 7.2, gy - 1.0)])
    arch = outer & ~innr
    g.bevel(arch, HOLY, face=0.6, bevel=1.4, grad=0.4, gain=0.95)
    # capitals (gold bands) + base plinths
    for yb in (gy - 20.5,):
        band = arch & (np.abs(Y - yb) < 1.1)
        g.bevel(band, GOLD, face=0.66, bevel=0.5, grad=0.2, gain=0.6)
    for s in (-1, 1):
        pl = poly([(cx + s * 7.2, gy - 3.6), (cx + s * 13.6, gy - 3.6), (cx + s * 13.6, gy + 0.4), (cx + s * 7.2, gy + 0.4)])
        g.bevel(pl, GOLD, face=0.55, bevel=0.6, grad=0.3, gain=0.7)
    # keystone gem
    ks = poly([(cx, gy - 34.0), (cx + 2.6, gy - 30.8), (cx, gy - 27.8), (cx - 2.6, gy - 30.8)])
    g.bevel(ks, SOUL, face=0.62, bevel=0.6, grad=0.3, gain=0.8)
    sparkle(front, cx, gy - 13.0, 3.2, "#fff9e4", "#fff9e4", 0.6)
    glints = [(20, 26, "#fff9e4"), (27, 14, "#fff9e4")]
    return back, g, front, glints


def martyrs_grace():
    """Martyr's Grace: a big haloed heart chaining golden light to smaller and smaller hearts (lowest ally first, -15 per jump)"""
    back, g, front = L3()
    hearts = [(23.0, 25.5, 9.4), (42.0, 34.5, 6.6), (27.0, 47.0, 5.0)]
    # chain arcs (zig-zag light bolts) between the hearts
    bolts = [[(28.5, 30.5), (33.0, 28.0), (32.8, 33.6), (37.5, 32.0)],
             [(39.5, 40.0), (37.5, 43.6), (34.4, 42.2), (31.5, 45.5)]]
    bm = np.zeros(X.shape, bool)
    for b in bolts:
        bm |= line(b, 2.4)
    glow(back, bm, "#f9e290", 1.6, 0.8)
    for hx_, hy_, s in hearts:
        glow(back, heart(hx_, hy_, s), "#de4c58", s * 0.35, 0.45)
    g.bevel(bm, GOLD, face=0.82, bevel=0.5, grad=0.1, gain=0.4)
    for (x, y, s), f in zip(hearts, (0.6, 0.55, 0.5)):
        h = heart(x, y, s)
        g.bevel(h, ROSE, face=f, bevel=max(0.9, s * 0.2), grad=0.4, gain=0.95)
    # halo over the big heart (the martyr)
    halo = ering(22.0, 12.6, 7.6, 2.8, 2.0, rot=-8)
    g.bevel(halo, GOLD, face=0.72, bevel=0.5, grad=0.4, gain=0.6)
    glow(back, halo, "#f9e290", 2.0, 0.5)
    # heal plus on the big heart
    plus = (capsule(23.0, 24.5, 23.0, 31.0, 1.2) | capsule(19.8, 27.7, 26.2, 27.7, 1.2))
    g.put(plus, rs(HOLY, 0.95))
    glints = [(18, 21, "#ffe2d6"), (39, 31, "#ffe2d6"), (25, 45, "#ffe2d6")]
    return back, g, front, glints


# ================================================================================================================= MONK
# Monk (class colour Saffron #f08a30, LOCKED): martial / wind / speed - saffron rim, dark rust field, linen hand wraps (the
# class emblem's wrapped fist), teal-white wind, calm water.
MONK_RIM = ramp("#5a2208", "#8e3a10", "#c45c1c", "#f08a30", "#f8b462", "#fde0b0")      # from Monk Saffron #f08a30
SAFFRON = ramp("#561a0c", "#8c3010", "#c4521a", "#f08a30", "#f8b25a", "#fdd890", "#fff2d0")
LINEN = ramp("#4e3a34", "#7a6252", "#a68e74", "#cbb796", "#e6d8b8", "#f8f0dc")        # hand wraps: violet-brown shadows
SKIN = ramp("#4a2220", "#7a3c2e", "#a65e44", "#cc845e", "#e8aa80", "#f8d0aa")
WIND = ramp("#163e4e", "#25687a", "#4498a6", "#78c4c4", "#b4e6dc", "#eafaf2")
WATER = ramp("#10304e", "#1a5078", "#2a78a4", "#4ea4c8", "#88cee0", "#ccf0f4")

MONK = K.Style("Monk", "#f08a30", MONK_RIM, field_c="#4a2416", field_e="#170b09",
               outline="#120706", frame=FRAME, glow_c="#f08a30")


def arc_band(cx, cy, r0, r1, a0, a1):
    """part of a ring (radii r0..r1) between angles a0..a1 (degrees, screen: 0 = right, 90 = down), any span"""
    ang = (np.degrees(np.arctan2(Y - cy, X - cx)) - a0) % 360.0
    return ring(cx, cy, r1, r0) & (ang <= (a1 - a0) % 360.0 + (360.0 if (a1 - a0) >= 360 else 0.0))


def swirl(cx, cy, a_head, span, r_in, r_out, w_head, w_tail):
    """one spiral ribbon: head at angle a_head (radius r_out, width w_head), sweeping BACK span degrees toward the centre
    (radius r_in, width w_tail). Returns (mask, t) where t = 0 at the head .. 1 at the tail."""
    ang = np.degrees(np.arctan2(Y - cy, X - cx))
    back = (a_head - ang) % 360.0                 # degrees behind the head (counter-clockwise on screen = travel clockwise)
    t = back / span
    rr = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    r_mid = r_out + (r_in - r_out) * t
    w = w_head + (w_tail - w_head) * t
    m = (t <= 1.0) & (np.abs(rr - r_mid) <= w / 2.0)
    m |= circle(cx + r_out * math.cos(math.radians(a_head)), cy + r_out * math.sin(math.radians(a_head)), w_head / 2.0)
    return m, np.clip(t, 0, 1)


def wrap_bands(layer, m, x0, y0, x1, y1, step, w, rmp, t_dark=0.18):
    """dark diagonal band lines (hand-wrap layers) across mask m: lines perpendicular to the direction (x0,y0)->(x1,y1)"""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    s = (X - x0) * ux + (Y - y0) * uy
    # slight slant so bands look wrapped (spiral), not stacked
    s = s + ((X - x0) * (-uy) + (Y - y0) * ux) * 0.28
    band = (np.mod(s, step) < w) & m
    layer.put(band, rs(rmp, t_dark))


def flowing_form():
    """Flowing Form: a saffron chi orb inside three teal-white wind ribbons swirling round it (speed aura, combo stacks)"""
    back, g, front = L3()
    cx, cy = 32.0, 32.0
    glow(back, circle(cx, cy, 8), "#f08a30", 6.0, 0.7)
    glow(back, ring(cx, cy, 22, 12), "#4498a6", 4.0, 0.35)
    for k in range(3):
        m, t = swirl(cx, cy, -70 + k * 120, 165, 8.0, 20.5, 5.6, 1.0)
        g.bevel(m, WIND, face=0.80, bevel=0.9, grad=0.25, gain=0.7, tone=-0.55 * t)
    # chi orb: saffron with a lit top-left and a hot core
    orb = circle(cx, cy, 7.0)
    d = np.sqrt((X - (cx - 2.0)) ** 2 + (Y - (cy - 2.2)) ** 2) / 9.0
    g.put(orb, rs(SAFFRON, 0.98 - d * 0.85))
    g.put(ring(cx, cy, 7.0, 6.0) & (Y > cy + 1), rs(SAFFRON, 0.3))
    # three combo pips round the orb (stacks)
    for a in (-90, 30, 150):
        r = math.radians(a)
        front.put(circle(cx + math.cos(r) * 10.2, cy + math.sin(r) * 10.2, 1.05), rs(SAFFRON, 0.9))
    glints = [(29, 28, "#fff2d0"), (30, 28, "#fdd890")]
    return back, g, front, glints


def palm_strike():
    """Palm Strike: an open, wrist-wrapped palm thrust forward with a saffron impact burst behind it (stun + knockback)"""
    back, g, front = L3()
    cx, cy, rot = 31.0, 34.0, -12.0
    # impact: two shock rings + burst rays behind the hand
    glow(back, circle(cx + 1, cy - 4, 12), "#f08a30", 6.0, 0.85)
    rays = np.zeros(X.shape, bool)
    for k in range(10):
        a = math.radians(k * 36 + 8)
        ca, sa = math.cos(a), math.sin(a)
        r0, r1, w = 15.0, 24.5, 1.9
        rays |= poly([(cx + 1 + ca * r0 - sa * w, cy - 4 + sa * r0 + ca * w), (cx + 1 + ca * r1, cy - 4 + sa * r1),
                      (cx + 1 + ca * r0 + sa * w, cy - 4 + sa * r0 - ca * w)])
    back.put(rays, rs(SAFFRON, 0.72), alpha=0.85)

    def R(p):
        return rotpts(p, cx, cy, rot)

    # wrist + wraps (linen)
    wr = R([(cx - 6.4, cy + 7.0), (cx + 6.4, cy + 7.0), (cx + 6.0, cy + 19.0), (cx - 6.0, cy + 19.0)])
    wrist = poly(wr)
    g.bevel(wrist, LINEN, face=0.6, bevel=1.2, grad=0.3, gain=0.8)
    a = math.radians(rot)
    wrap_bands(g, wrist, cx - 6 * math.sin(-a), cy + 7, cx - 6 * math.sin(-a) + math.sin(a) * -1, cy + 19, 3.0, 0.75, LINEN)
    # palm
    palm = poly(R([(cx - 8.2, cy - 3.0), (cx + 8.2, cy - 3.0), (cx + 7.6, cy + 6.0), (cx + 4.5, cy + 9.0), (cx - 4.5, cy + 9.0),
                   (cx - 7.8, cy + 6.0)]))
    # fingers (index .. pinky) and thumb
    fing = np.zeros(X.shape, bool)
    tips = [(-5.8, -16.2), (-1.9, -18.6), (2.0, -17.8), (5.9, -14.4)]
    for fx, ty in tips:
        (x0, y0), (x1, y1) = R([(cx + fx, cy - 2.0), (cx + fx * 1.05, cy + ty)])
        fing |= capsule(x0, y0, x1 + fx * 0.06, y1, 2.1, 1.9)
    (tx0, ty0), (tx1, ty1) = R([(cx - 6.5, cy + 4.5), (cx - 13.0, cy - 2.5)])
    thumb = capsule(tx0, ty0, tx1, ty1, 2.5, 2.1)
    g.bevel(thumb, SKIN, face=0.64, bevel=1.0, grad=0.3, gain=0.8)
    g.bevel(fing, SKIN, face=0.74, bevel=1.0, grad=0.35, gain=0.85)
    g.bevel(palm, SKIN, face=0.70, bevel=1.4, grad=0.3, gain=0.8)
    # palm crease + heel shade
    cr = line(R([(cx - 5.0, cy + 1.0), (cx - 0.5, cy + 3.0), (cx + 5.5, cy + 0.5)]), 0.7)
    g.put(cr & palm, rs(SKIN, 0.3))
    # a linen band across the knuckle line (the palm wrap)
    kb = poly(R([(cx - 8.4, cy + 4.6), (cx + 8.4, cy + 4.6), (cx + 8.3, cy + 7.4), (cx - 8.3, cy + 7.4)])) & palm
    g.bevel(kb, LINEN, face=0.7, bevel=0.6, grad=0.3, gain=0.7)
    glints = [(26, 18, "#f8d0aa"), (30, 16, "#f8d0aa")]
    return back, g, front, glints


SHOE = ramp("#22120e", "#381e14", "#542e1c", "#723f26", "#915433", "#ae6e46", "#c88c62")  # soft warm earth-brown cloth shoe
SOLE = ramp("#3a2818", "#664a2e", "#94764e", "#bea06e", "#e0c896", "#f2e2b8")      # light tan felt / leather sole


def cyclone_kick():
    """Cyclone Kick: a kick with the shoe standing up at the end of a linen-wrapped shin, sole toward the kick, in a saffron whirl"""
    back, g, front = L3()
    cx, cy = 32.0, 33.0
    # whirl: two sweeping arcs (motion trail of the spin) - thick at the head, thin at the tail; placed so they pass above-left
    # and below-right of the leg and never cross the shoe
    # (the shoe fills the upper-right quarter, so one long arc sweeps right -> bottom and a short one sits upper-left)
    for a_head, span, rr in ((118, 135, 20.0), (252, 72, 19.0)):
        m, t = swirl(cx, cy, a_head, span, 15.0, rr, 6.8, 1.6)
        glow(back, m, "#f08a30", 2.5, 0.7)
        g.bevel(m, SAFFRON, face=0.90, bevel=0.8, grad=0.2, gain=0.6, tone=-0.5 * t)
    # v4 (Skyy 2026-10-08: "Use shoes instead, make the foot vertical like the first image"): the FIRST pose again - linen-wrapped
    # shin coming in from the lower left, the foot standing UP at its end (toes up, sole facing the kick, heel at the bottom) -
    # now in a soft dark earth-brown Monk shoe with a light tan sole edge, a padded collar and an instep strap.
    piv, rot = (32.0, 34.0), -16.0

    def F(pts):
        return rotpts(pts, piv[0], piv[1], rot)

    (s0x, s0y), (s1x, s1y) = F([(9.0, 39.0), (29.0, 36.0)])
    shin = capsule(s0x, s0y, s1x, s1y, 4.8, 4.2)
    g.bevel(shin, LINEN, face=0.55, bevel=1.2, grad=0.3, gain=0.8)
    wrap_bands(g, shin, s0x, s0y, s1x, s1y, 3.2, 0.8, LINEN)
    # sole: a thick light tan sole along the kicking face (right) - ball pad at the top, thinner arch, heel block at the bottom
    sole = poly(F([(35.4, 18.2), (38.4, 18.8), (40.8, 21.2), (41.4, 25.0), (41.0, 28.6), (40.0, 31.6), (40.2, 35.0),
                   (41.0, 38.6), (39.8, 42.6), (36.6, 44.8), (31.0, 45.0), (28.6, 43.6), (29.0, 41.4), (33.0, 41.2),
                   (35.8, 39.6), (36.6, 35.0), (37.0, 30.0), (36.8, 22.0), (35.4, 20.0)]))
    g.bevel(sole, SOLE, face=0.72, bevel=1.0, grad=0.35, gain=0.8)
    # arch gap shading + heel-block line on the sole
    g.put(line(F([(36.8, 35.4), (40.6, 35.4)]), 0.7) & sole, rs(SOLE, 0.25))
    # the shoe upper: soft cloth, rounded toe box at the top, heel at the bottom, opening on the left where the shin goes in
    upper = poly(F([(25.2, 32.0), (28.6, 29.4), (30.0, 24.0), (31.6, 20.6), (33.6, 18.8), (35.6, 18.6), (36.8, 20.2),
                    (37.2, 22.0), (37.2, 30.0), (36.6, 35.0), (35.8, 39.6), (33.0, 41.4), (29.0, 41.6), (26.2, 40.6),
                    (25.0, 37.0)]))
    g.bevel(upper, SHOE, face=0.62, bevel=1.4, grad=0.35, gain=0.9)
    # stitched seam just inside the sole (lighter dashes) and a toe-box seam
    seam = line(F([(35.6, 21.6), (35.9, 30.0), (35.2, 36.4), (33.6, 39.4), (29.6, 40.2)]), 0.55)
    dash = np.mod((X + Y) * 0.9, 2.2) < 1.1
    g.put(seam & dash & upper, rs(SOLE, 0.55))
    g.put(line(F([(30.8, 25.0), (33.6, 23.6), (37.2, 23.6)]), 0.6) & upper, rs(SHOE, 0.22))
    # instep strap (tan) with a small knot
    strap = line(F([(28.4, 30.2), (32.6, 28.6), (37.4, 28.2)]), 2.0) & upper
    g.bevel(strap, SOLE, face=0.70, bevel=0.5, grad=0.2, gain=0.7)
    # padded collar at the opening (where the wrapped shin goes in)
    collar = line(F([(26.4, 31.6), (25.4, 34.6), (25.4, 38.6), (26.8, 41.0)]), 2.2) & (upper | shin)
    g.bevel(collar, SHOE, face=0.40, bevel=0.6, grad=0.2, gain=0.7)
    (gx1, gy1), = F([(32.8, 20.6)])
    (gx2, gy2), = F([(39.4, 21.6)])
    glints = [(int(gx1), int(gy1), "#c88c62"), (int(gx2), int(gy2), "#f2e2b8"), (15, 41, "#f8f0dc")]
    return back, g, front, glints


def fist(g, cx, cy, s=1.0, faint=None, tint=None):
    """front view of a linen-wrapped fist (knuckles to the viewer) centred (cx, cy); faint = (layer, alpha) for after-images"""
    def P(dx, dy):
        return cx + dx * s, cy + dy * s
    parts = []
    body = poly([P(-9.5, -5.0), P(9.5, -5.0), P(10.0, 4.0), P(7.0, 9.0), P(-7.0, 9.0), P(-10.0, 4.0)])
    fingers = [capsule(*P(fx, -6.0), *P(fx, 1.5), 2.55 * s) for fx in (-7.0, -2.35, 2.35, 7.0)]
    thumb = capsule(*P(-10.0, 4.4), *P(1.6, 5.4), 2.6 * s)
    wrist = poly([P(-6.6, 8.0), P(6.6, 8.0), P(6.0, 17.0), P(-6.0, 17.0)])
    if faint is not None:
        lay, al = faint
        sil = body | wrist | thumb
        for f in fingers:
            sil |= f
        lay.put(sil, rs(SAFFRON, 0.50), alpha=al)
        edge = sil & ~K._erode(K._erode(sil, True), False)
        lay.put(edge, rs(SAFFRON, 0.80), alpha=min(1.0, al + 0.3))
        return sil
    lin = LINEN if tint is None else tint
    skn = SKIN if tint is None else tint
    g.bevel(wrist, lin, face=0.52, bevel=1.1 * s, grad=0.3, gain=0.8)
    wrap_bands(g, wrist, *P(0, 8.0), *P(0, 17.0), 3.0 * s, 0.75 * s, lin)
    g.bevel(body, lin, face=0.5, bevel=1.2 * s, grad=0.3, gain=0.7)
    for f, fc in zip(fingers, (0.70, 0.74, 0.72, 0.66)):
        g.bevel(f, lin, face=fc, bevel=1.1 * s, grad=0.4, gain=0.85)
    g.bevel(thumb, lin, face=0.60, bevel=1.0 * s, grad=0.3, gain=0.8)
    g.bevel(thumb & circle(*P(1.0, 5.3), 2.7 * s), skn, face=0.62, bevel=0.8 * s, grad=0.3, gain=0.7)
    return None


def hundred_fists():
    """Hundred Fists: a wrapped fist punching forward between two saffron after-image fists, impact sparks round it (a flurry)"""
    back, g, front = L3()
    cx, cy = 32.0, 29.5
    glow(back, circle(cx, cy, 12), "#f08a30", 6.0, 0.6)
    # after-image fists left + right, apart from the real fist so each reads on its own at 32 px
    for fx in (-19.0, 19.0):
        glow(back, circle(cx + fx, cy + 2.0, 5.0), "#f08a30", 2.5, 0.5)
        fist(g, cx + fx, cy - 1.0, 0.47, tint=SAFFRON)
        # motion streaks under each after-image (moving toward the centre)
        for k, dy in enumerate((8.0, 10.6)):
            x0 = cx + fx * (1.12 - 0.1 * k)
            front.put(capsule(x0, cy + dy, x0 - math.copysign(3.5, fx), cy + dy, 0.6), rs(SAFFRON, 0.8))
    fist(g, cx, cy + 0.5, 1.08)
    # impact sparks above the knuckles
    for sx, sy, sr in ((32.0, 15.5, 2.2), (22.5, 19.0, 1.6), (41.5, 19.0, 1.6)):
        sparkle(front, sx, sy, sr, "#fdd890", None, 0.5)
    glints = [(24, 24, "#f8f0dc"), (29, 24, "#f8f0dc"), (34, 24, "#f8f0dc")]
    return back, g, front, glints


def still_water():
    """Still Water: one drop falling on a calm pond - rings spreading - under a saffron sun on the horizon (a calm counter stance)"""
    back, g, front = L3()
    cx, hy = 32.0, 37.0
    # sun on the horizon
    sun = circle(cx, hy, 13.5) & (Y <= hy)
    glow(back, sun, "#f08a30", 5.0, 0.55)
    srays = np.zeros(X.shape, bool)
    for k in range(7):
        a = math.radians(-180 + 15 + k * 25)
        ca, sa = math.cos(a), math.sin(a)
        srays |= poly([(cx + ca * 15.0 - sa * 1.3, hy + sa * 15.0 + ca * 1.3), (cx + ca * 21.5, hy + sa * 21.5),
                       (cx + ca * 15.0 + sa * 1.3, hy + sa * 15.0 - ca * 1.3)])
    back.put(srays & (Y < hy - 0.5), rs(SAFFRON, 0.75), alpha=0.8)
    g.bevel(sun, SAFFRON, face=0.66, bevel=1.4, grad=0.55, gain=0.6)
    # horizon / water surface
    water = (Y > hy) & K.field_disc()
    tw = np.clip((Y - hy) / 14.0, 0, 1)
    back.put(water, rs(WATER, 0.40 - tw * 0.28), alpha=0.9)
    # sun reflection strips
    for k, (wd, yy) in enumerate(((10.5, hy + 2.0), (7.5, hy + 4.4), (4.8, hy + 6.8), (2.6, hy + 9.0))):
        back.put((np.abs(X - cx) < wd) & (np.abs(Y - yy) < 0.6), rs(SAFFRON, 0.78 - k * 0.08), alpha=0.85)
    g.put((Y > hy - 0.6) & (Y < hy + 0.6) & K.field_disc(), rs(SAFFRON, 0.86))
    # ripples spreading from where the drop lands (thin rings, no filled centre)
    for rx, ry, w, t in ((19.0, 5.2, 1.4, 0.80), (10.5, 2.9, 1.4, 0.96)):
        g.put(ering(cx, hy + 7.5, rx, ry, w), rs(WATER, t))
    # the drop, falling
    drop = circle(cx, 25.5, 5.0) | poly([(cx - 4.7, 24.0), (cx, 12.5), (cx + 4.7, 24.0)])
    g.bevel(drop, WATER, face=0.72, bevel=1.1, grad=0.45, gain=0.85)
    glints = [(29, 22, "#ccf0f4"), (29, 23, "#ccf0f4")]
    return back, g, front, glints


# ================================================================================================================= ASSASSIN
# Assassin (class colour #b58cff): stealth / poison / the kill - lilac rim, dark plum field, shadow-violet cloth, toxic green,
# steel blades with violet gems (the class emblem's dagger), gold for the boss crown.
ASSN_RIM = ramp("#2e1c5a", "#4c3290", "#7a5cc8", "#b58cff", "#d4bcff", "#f0e8ff")       # from Assassin #b58cff
SHADE = ramp("#100a1a", "#1c142c", "#2a1f42", "#3c2d5a", "#544076", "#705a94", "#8e7ab0")  # shadow-violet cloth
LILAC = ramp("#3e2478", "#6440b0", "#8e68e0", "#b58cff", "#d4bcff", "#f0e8ff")
POISON = ramp("#123214", "#1e5418", "#327c20", "#56a82e", "#86d24a", "#bff08a", "#ecffd0")
GLASS = ramp("#22303e", "#3a5060", "#5c7884", "#88a6ac", "#bcd6d6", "#e6f6f2")
SMOKE = ramp("#241e30", "#3a3248", "#554c66", "#766e88", "#9c96ac", "#c6c2d2", "#e6e4ee")
IRON = ramp("#12121c", "#1e1e2c", "#2e2e40", "#444458", "#5e5e76", "#7c7c94")
WOOD = ramp("#3a2214", "#5e3a20", "#86582e", "#ae7e48", "#d0a868")

ASSASSIN = K.Style("Assassin", "#b58cff", ASSN_RIM, field_c="#33224e", field_e="#0e0916",
                   outline="#07040c", frame=FRAME, glow_c="#b58cff")


def hood(g, cx, cy, s=1.0, ghost=None):
    """front view of an Assassin's-Creed-style hood (v2, Skyy 2026-10-08): pointed eagle-beak peak that dips down over the
    forehead, draped sides falling to the shoulders, a cloth face mask over nose + mouth, two glowing lilac eyes in the shadow
    between beak and mask; ghost=(layer, alpha) = a shadow copy"""
    def P(dx, dy):
        return cx + dx * s, cy + dy * s
    outer = poly([P(0, -23.4), P(4.4, -19.6), P(9.4, -14.0), P(12.8, -7.0), P(13.8, 1.0), P(14.6, 9.0), P(18.6, 15.0),
                  P(20.0, 24.0), P(-20.0, 24.0), P(-18.6, 15.0), P(-14.6, 9.0), P(-13.8, 1.0), P(-12.8, -7.0), P(-9.4, -14.0),
                  P(-4.4, -19.6)])
    # face opening: the beak comes down to a sharp point between the eyes, the draped sides frame the face
    opening = poly([P(0, -0.6), P(2.6, -6.6), P(6.4, -8.8), P(9.0, -6.2), P(10.0, 0.0), P(9.6, 7.0), P(7.4, 12.0),
                    P(3.6, 14.6), P(-3.6, 14.6), P(-7.4, 12.0), P(-9.6, 7.0), P(-10.0, 0.0), P(-9.0, -6.2), P(-6.4, -8.8),
                    P(-2.6, -6.6)])
    eyes = np.zeros(X.shape, bool)
    for sx in (-1, 1):
        eyes |= poly([P(sx * 2.4, -1.6), P(sx * 7.0, -3.4), P(sx * 6.8, -1.0), P(sx * 3.0, 0.2)])
    # cloth mask over nose + mouth: top edge peaks over the nose, bottom tucked into the hood
    mask = poly([P(-10.4, 2.4), P(-5.0, 2.2), P(0, 0.6), P(5.0, 2.2), P(10.4, 2.4), P(10.2, 8.0), P(7.8, 12.8), P(3.6, 15.4),
                 P(-3.6, 15.4), P(-7.8, 12.8), P(-10.2, 8.0)]) & opening
    if ghost is not None:
        lay, al = ghost
        lay.put(outer, rs(LILAC, 0.36), alpha=al)
        edge = outer & ~K._erode(K._erode(K._erode(outer, True), False), True)
        lay.put(edge, rs(LILAC, 0.72), alpha=min(1.0, al + 0.25))
        lay.put(opening, rs(SHADE, 0.05), alpha=al)
        lay.put(mask, rs(LILAC, 0.22), alpha=al)
        lay.put(line([P(-8.6, 2.5), P(-4.6, 2.3), P(0, 0.7), P(4.6, 2.3), P(8.6, 2.5)], 0.8 * s) & mask, rs(LILAC, 0.6),
                alpha=min(1.0, al + 0.1))
        lay.put(eyes, rs(LILAC, 0.95), alpha=1.0)
        return outer
    g.bevel(outer, SHADE, face=0.80, bevel=1.6 * s, grad=0.45, gain=0.9)
    # beak ridge: a lit centre seam from the peak down to the beak point, with a darker side to give the peak its edge
    g.put(line([P(0.2, -22.4), P(0.2, -1.8)], 0.9 * s) & outer, rs(SHADE, 1.0))
    g.put(poly([P(0.7, -21.4), P(3.4, -7.4), P(0.7, -1.4)]) & outer, rs(SHADE, 0.60))
    # brim edge of the beak: a lit line along each side of the point (so the beak reads against the dark face)
    g.put(line([P(-6.2, -8.6), P(-2.6, -6.4), P(0, -0.8), P(2.6, -6.4), P(6.2, -8.6)], 0.8 * s) & outer, rs(SHADE, 0.92))
    # draped side folds falling from the cheeks to the shoulders
    folds = line([P(-12.2, 2.0), P(-11.6, 12.0), P(-14.0, 23.0)], 0.9 * s) | line([P(12.2, 2.0), P(11.6, 12.0), P(14.0, 23.0)], 0.9 * s) | \
        line([P(-15.2, 13.0), P(-17.4, 23.0)], 0.8 * s) | line([P(15.2, 13.0), P(17.4, 23.0)], 0.8 * s)
    g.put(folds & outer, rs(SHADE, 0.45))
    # face opening: lit inner rim, dark depth under the beak
    rim = opening & ~K._erode(K._erode(opening, True), False)
    d = np.sqrt((X - cx) ** 2 + ((Y - (cy - 4.0 * s)) * 0.8) ** 2) / (11.0 * s)
    g.put(opening, rs(SHADE, 0.02 + d * 0.10))
    g.put(rim & (Y > cy - 2.0 * s), rs(SHADE, 0.30))
    # the mask: grey-violet cloth, bevelled, with two soft creases and a lit top hem
    # the mask: dark grey-violet wrapped cloth, bevelled, diagonal wrap folds meeting under the nose, lit top hem over the nose
    g.bevel(mask, SMOKE, face=0.34, bevel=0.8 * s, grad=0.35, gain=0.8)
    for sx in (-1, 1):
        g.put(line([P(sx * 9.6, 5.0), P(sx * 1.2, 8.6)], 0.6 * s) & mask, rs(SMOKE, 0.14))
        g.put(line([P(sx * 8.8, 10.0), P(sx * 1.6, 13.0)], 0.6 * s) & mask, rs(SMOKE, 0.14))
    g.put(line([P(-9.0, 2.5), P(-4.8, 2.3), P(0, 0.7), P(4.8, 2.3), P(9.0, 2.5)], 0.7 * s) & mask, rs(SMOKE, 0.70))
    g.put(eyes, rs(LILAC, 0.95))
    return outer


def dagger(g, x0, y0, x1, y1, w=2.6, guard=5.5, grip=7.0, rmp_gem=None):
    """a straight dagger, pommel at (x0, y0), point at (x1, y1): wrapped grip, gold guard, bevelled steel blade with ridge"""
    rmp_gem = LILAC if rmp_gem is None else rmp_gem
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    gx, gy = x0 + ux * (grip + 2.0), y0 + uy * (grip + 2.0)          # guard centre
    blade = poly([(gx + nx * w, gy + ny * w), (x1 - ux * w * 2.2 + nx * w * 0.8, y1 - uy * w * 2.2 + ny * w * 0.8), (x1, y1),
                  (x1 - ux * w * 2.2 - nx * w * 0.8, y1 - uy * w * 2.2 - ny * w * 0.8), (gx - nx * w, gy - ny * w)])
    g.bevel(blade, STEEL, face=0.74, bevel=0.9, grad=0.2, gain=0.9)
    half = blade & (((X - gx) * nx + (Y - gy) * ny) > 0)
    g.bevel(half, STEEL, face=0.50, bevel=0.0001, grad=0.15, gain=0.0)
    gp = capsule(x0 + ux * 1.5, y0 + uy * 1.5, gx, gy, w * 0.62)
    g.bevel(gp, IRON, face=0.55, bevel=0.6, grad=0.2, gain=0.8)
    # criss-cross wrap lines on the grip
    wrap_bands(g, gp, x0, y0, gx, gy, 2.0, 0.6, IRON, t_dark=0.05)
    gd = capsule(gx + nx * guard, gy + ny * guard, gx - nx * guard, gy - ny * guard, 1.35)
    g.bevel(gd, GOLD, face=0.62, bevel=0.6, grad=0.3, gain=0.8)
    pm = circle(x0, y0, w * 0.95)
    g.bevel(pm, rmp_gem, face=0.6, bevel=0.6, grad=0.4, gain=0.8)
    return blade | gp | gd | pm


def cloak_first_strike():
    """Cloak + First Strike: a hooded assassin fading into the shadows (lower half dissolving), a bright crit star = the first hit"""
    back, g, front = L3()
    cx, cy = 31.0, 31.0
    glow(back, circle(cx, cy + 2, 15), "#8e68e0", 7.0, 0.85)
    full = hood(None, cx, cy, 1.0, ghost=(Layer(), 0.0))           # silhouette only
    solid = full & (Y < cy + 15.0)          # (v2: lower so the face mask stays solid)
    # the solid upper hood (glyph) ...
    tmp = Layer()
    hood(tmp, cx, cy, 1.0)
    g.rgb = g.rgb * (1 - solid[..., None]) + tmp.rgb * solid[..., None]
    g.a = np.where(solid, 1.0, g.a)
    # ... and the lower part fading out into the field (back layer, no outline): invisibility
    fade = full & ~solid
    al = np.clip(1.0 - (Y - (cy + 15.0)) / 10.0, 0, 1) ** 1.3
    back.rgb = back.rgb * (1 - (fade * al)[..., None]) + tmp.rgb / np.maximum(tmp.a[..., None], 1e-6) * (fade * al)[..., None]
    back.a = np.clip(back.a + fade * al, 0, 1)
    # wisps rising off the fade
    for wx, wy, wr in ((19.0, 46.0, 1.3), (44.0, 44.5, 1.1), (25.0, 50.5, 0.9), (39.0, 51.0, 0.9)):
        back.put(circle(wx, wy, wr), rs(LILAC, 0.55), alpha=0.7)
    # crit star (First Strike: next hit is a sure crit)
    glow(back, circle(46.0, 18.0, 3.5), "#ecc458", 3.5, 0.8)
    cs = star(46.0, 18.0, 8.2, 2.5, 4, -90)
    g.bevel(cs, GOLD, face=0.82, bevel=0.8, grad=0.2, gain=0.6)
    glints = [(28, 15, "#8e7ab0"), (45, 14, "#fff4cc")]
    return back, g, front, glints


def toxin():
    """Toxin: a corked glass vial of bubbling green poison, a toxic green cloud spilling out behind it"""
    back, g, front = L3()
    # poison cloud (behind, upper right)
    puffs = [(38.0, 24.0, 8.0), (46.0, 30.0, 6.4), (30.5, 19.0, 5.6), (44.0, 18.5, 5.2), (40.5, 35.5, 5.2)]
    cloud = np.zeros(X.shape, bool)
    for px, py, pr in puffs:
        cloud |= circle(px, py, pr)
    glow(back, cloud, "#56a82e", 3.5, 0.55)
    g.bevel(cloud, POISON, face=0.52, bevel=2.2, grad=0.5, gain=0.8)
    for px, py, pr in puffs[:3]:
        g.put(circle(px - pr * 0.3, py - pr * 0.35, pr * 0.42) & cloud, rs(POISON, 0.72))
    # the vial: round flask + neck + cork, tilted
    cx, cy, rot = 25.0, 39.0, 28.0

    def R(p):
        return rotpts(p, cx, cy, rot)
    body = circle(cx, cy, 10.0)
    neck = poly(R([(cx - 3.4, cy - 8.0), (cx + 3.4, cy - 8.0), (cx + 3.4, cy - 15.5), (cx - 3.4, cy - 15.5)]))
    lip = poly(R([(cx - 4.6, cy - 15.0), (cx + 4.6, cy - 15.0), (cx + 4.6, cy - 17.0), (cx - 4.6, cy - 17.0)]))
    cork = poly(R([(cx - 3.0, cy - 16.5), (cx + 3.0, cy - 16.5), (cx + 2.6, cy - 21.5), (cx - 2.6, cy - 21.5)]))
    g.bevel(body | neck, GLASS, face=0.55, bevel=1.4, grad=0.4, gain=0.8)
    # poison liquid inside (level tilts with the vial: stays horizontal)
    liq = circle(cx, cy, 8.4) & (Y > cy - 2.0)
    d = np.sqrt((X - (cx - 2.5)) ** 2 + (Y - (cy + 1.0)) ** 2) / 10.0
    g.put(liq, rs(POISON, 0.88 - d * 0.6))
    g.put(liq & (Y < cy - 0.8), rs(POISON, 0.95))
    for bx, by, br in ((cx + 2.5, cy + 3.0, 1.2), (cx - 1.5, cy + 5.5, 0.9), (cx + 4.5, cy + 0.5, 0.8)):
        g.put(ring(bx, by, br + 0.5, br - 0.2), rs(POISON, 1.0))
    g.bevel(lip, GLASS, face=0.75, bevel=0.6, grad=0.3, gain=0.7)
    g.bevel(cork, WOOD, face=0.6, bevel=0.8, grad=0.4, gain=0.8)
    # glass highlight streak (front)
    hl = ring(cx, cy, 7.8, 6.6) & (np.degrees(np.arctan2(Y - cy, X - cx)) > -170) & (np.degrees(np.arctan2(Y - cy, X - cx)) < -110)
    front.put(hl, hx("#e6f6f2"), alpha=0.9)
    # drips falling from the cloud
    for dx_, dy_ in ((48.0, 41.0), (36.0, 46.0)):
        front.put(circle(dx_, dy_, 1.1) | poly([(dx_ - 1.0, dy_ - 0.3), (dx_, dy_ - 2.8), (dx_ + 1.0, dy_ - 0.3)]), rs(POISON, 0.8))
    glints = [(36, 19, "#ecffd0"), (21, 36, "#e6f6f2")]
    return back, g, front, glints


def god_killer():
    """God Killer: a dagger stabbing down through a gold boss crown (2x on bosses, 3x from behind)"""
    back, g, front = L3()
    cx, cy = 32.0, 40.0
    glow(back, circle(cx, cy - 2, 12), "#ecc458", 6.0, 0.45)
    # crown: band + 5 points with gem tips
    band = poly([(cx - 15.0, cy + 1.0), (cx + 15.0, cy + 1.0), (cx + 14.0, cy + 8.5), (cx - 14.0, cy + 8.5)])
    pts = [(cx - 15.5, cy + 1.5), (cx - 17.0, cy - 11.0), (cx - 9.0, cy - 3.0), (cx - 6.0, cy - 15.0), (cx, cy - 5.0),
           (cx + 6.0, cy - 15.0), (cx + 9.0, cy - 3.0), (cx + 17.0, cy - 11.0), (cx + 15.5, cy + 1.5)]
    crown = poly(pts) | band
    g.bevel(crown, GOLD, face=0.6, bevel=1.5, grad=0.45, gain=0.9)
    g.bevel(band, GOLD, face=0.48, bevel=1.0, grad=0.3, gain=0.8)
    for gx_, gy_, gr, rmp in ((cx - 17.0, cy - 11.5, 2.0, ROSE), (cx - 6.0, cy - 15.5, 2.0, LILAC),
                              (cx + 6.0, cy - 15.5, 2.0, LILAC), (cx + 17.0, cy - 11.5, 2.0, ROSE)):
        g.bevel(circle(gx_, gy_, gr), rmp, face=0.62, bevel=0.6, grad=0.4, gain=0.8)
    for gx_ in (cx - 8.0, cx + 8.0):
        g.bevel(poly([(gx_, cy + 2.4), (gx_ + 2.4, cy + 4.8), (gx_, cy + 7.2), (gx_ - 2.4, cy + 4.8)]), ROSE, face=0.6, bevel=0.6,
                grad=0.3, gain=0.8)
    # crack where the blade goes in
    crk = line([(cx + 1.0, cy - 2.0), (cx - 1.5, cy + 2.5), (cx + 1.5, cy + 5.5)], 0.9)
    g.put(crk & crown, rs(GOLD, 0.15))
    # the dagger: point down through the crown's centre, pommel up-right
    dagger(g, cx + 13.5, cy - 33.0, cx - 1.0, cy + 4.5, w=3.8, guard=6.6, grip=8.0)
    glow(back, circle(cx + 13.5, cy - 33.0, 2.0), "#b58cff", 2.5, 0.6)
    # kill sparks round the strike point
    sparkle(front, cx - 9.5, cy - 7.0, 2.0, "#fff4cc", None, 0.5)
    sparkle(front, cx + 10.5, cy - 4.5, 1.6, "#fff4cc", None, 0.45)
    glints = [(26, 31, "#fff4cc"), (24, 47, "#fff4cc")]
    return back, g, front, glints


def shadow_clone():
    """Shadow Clone: the hooded assassin with a glowing shadow copy of themselves beside it (the decoy that bursts)"""
    back, g, front = L3()
    glow(back, circle(22.0, 30.0, 10), "#8e68e0", 6.0, 0.8)
    glow(back, circle(38.0, 36.0, 10), "#7a5cc8", 6.0, 0.5)
    # the clone (behind, left): a lilac-edged shadow copy
    hood(None, 22.5, 28.0, 0.78, ghost=(back, 0.85))
    # the real assassin (front, right)
    hood(g, 38.0, 33.5, 0.86)
    # burst sparks off the clone (it explodes when hit)
    for sx, sy, sr in ((11.5, 21.0, 1.8), (14.5, 40.5, 1.4), (27.5, 12.0, 1.4)):
        sparkle(front, sx, sy, sr, "#d4bcff", None, 0.45)
    glints = [(36, 18, "#8e7ab0")]
    return back, g, front, glints


def vanishing_act():
    """Vanishing Act: a smoke bomb with a lit fuse bursting into a big cloud of violet-grey smoke (cloak + smoke screen)"""
    back, g, front = L3()
    puffs = [(36.0, 26.0, 9.0), (25.0, 23.0, 7.4), (46.0, 31.0, 6.6), (30.5, 14.5, 6.0), (43.5, 18.0, 6.2), (38.0, 37.0, 6.6),
             (19.0, 31.5, 5.6)]
    cloud = np.zeros(X.shape, bool)
    for px, py, pr in puffs:
        cloud |= circle(px, py, pr)
    glow(back, cloud, "#766e88", 3.0, 0.5)
    g.bevel(cloud, SMOKE, face=0.55, bevel=2.4, grad=0.55, gain=0.85)
    for px, py, pr in puffs:
        g.put(circle(px - pr * 0.3, py - pr * 0.35, pr * 0.40) & cloud, rs(SMOKE, 0.76))
    # puff separation lines (shade where puffs overlap)
    for (ax, ay, ar), (bx, by, br) in ((puffs[0], puffs[1]), (puffs[0], puffs[2]), (puffs[0], puffs[5]), (puffs[3], puffs[1])):
        g.put(ring(ax, ay, ar + 0.6, ar - 0.4) & circle(bx, by, br) & cloud, rs(SMOKE, 0.30))
    # the bomb, lower left, in front of the smoke
    bx, by = 21.5, 43.0
    bomb = circle(bx, by, 8.6)
    glow(back, bomb, "#8e68e0", 2.5, 0.6)
    g.bevel(bomb, IRON, face=0.66, bevel=1.6, grad=0.5, gain=0.9)
    g.put(ellipse(bx, by + 0.5, 8.6, 2.0) & bomb, rs(LILAC, 0.72))         # violet band
    cap = poly([(bx + 3.0, by - 8.8), (bx + 7.6, by - 5.8), (bx + 5.8, by - 3.0), (bx + 1.6, by - 5.8)])
    g.bevel(cap, IRON, face=0.7, bevel=0.6, grad=0.3, gain=0.7)
    fuse = line([(bx + 5.8, by - 7.0), (bx + 8.6, by - 10.0), (bx + 8.2, by - 12.6)], 1.4)
    g.put(fuse, rs(WOOD, 0.75))
    glow(back, circle(bx + 8.2, by - 13.2, 2.2), "#ffaa3c", 2.5, 1.0)
    sparkle(front, bx + 8.2, by - 13.4, 3.2, "#ffd878", "#fff1c0", 0.7)
    glints = [(17, 38, "#7c7c94"), (33, 19, "#e6e4ee")]
    return back, g, front, glints


# ================================================================================================================= WARRIOR
# Warrior (class colour #e0b060 - the class emblem colour): tank + crowd control - amber-gold rim, dark gunmetal field (cool
# steel-teal, so the warm gold rim is not the Priest's gold-on-umber or the Monk's saffron-on-rust), steel + iron, oak wood,
# crimson banner cloth, warm amber light for shouts / shockwaves.
WAR_RIM = ramp("#4a2a10", "#7e5220", "#b4823a", "#e0b060", "#f2d08c", "#fbeccc")         # from Warrior #e0b060
AMBER = ramp("#5a2c0e", "#8e521a", "#c4842c", "#e0b060", "#f4d48c", "#fff0cc")          # shout / shockwave light
CRIMSON = ramp("#2e0c18", "#561424", "#86202c", "#b23634", "#d65a44", "#f08c66")        # banner + tabard cloth
OAK = ramp("#2c1a14", "#4a2c1c", "#6e4426", "#94643a", "#b88a56", "#d8b47e")            # shield planks, spear shaft

WARRIOR = K.Style("Warrior", "#e0b060", WAR_RIM, field_c="#2a3a44", field_e="#0b1216",
                  outline="#05090c", frame=FRAME, glow_c="#e0b060")


def rallying_guard():
    """Rallying Guard: a crimson war banner on a spear with a steel guard-shield emblem, rally-cry arcs off the spear tip
    (you + party take less damage, mobs turn to you)"""
    back, g, front = L3()
    glow(back, circle(34.0, 32.0, 13), "#e0b060", 7.0, 0.55)
    # rally-cry arcs either side of the spear head (the shout that turns mobs to you)
    hx_, hy_ = 21.0, 19.0
    for r0, r1, al in ((5.4, 7.0, 1.0), (8.6, 10.2, 0.8)):
        for a0, a1 in ((150.0, 215.0), (-35.0, 30.0)):
            back.put(arc_band(hx_, hy_, r0, r1, a0, a1), rs(AMBER, 0.86), alpha=al)
    # spear shaft (oak), slightly leaning
    sx0, sy0, sx1, sy1 = 19.2, 56.0, 21.0, 23.0
    shaft = capsule(sx0, sy0, sx1, sy1, 1.55)
    g.bevel(shaft, OAK, face=0.62, bevel=0.7, grad=0.3, gain=0.85)
    # banner cloth: swallow-tailed, gentle wave, hanging from a crossbar
    top, bot, x0, x1 = 24.5, 47.0, 21.5, 46.5
    pts_top = [(x0 + (x1 - x0) * k / 8.0, top + 1.2 * math.sin(k / 8.0 * math.pi * 1.4)) for k in range(9)]
    pts_bot = [(x0 + (x1 - 4.0 - x0) * k / 8.0, bot + 1.6 * math.sin(k / 8.0 * math.pi * 1.4 + 0.4) - 3.0 * (k / 8.0))
               for k in range(9)]
    notch = (x1 - 8.0, (top + bot) / 2.0 + 0.6)
    cloth_pts = pts_top + [(x1 + 0.5, bot - 5.5), notch, pts_bot[-1]] + pts_bot[::-1][1:]
    cloth = poly(cloth_pts)
    wave = np.sin((X - x0) / (x1 - x0) * math.pi * 1.4) * 0.12
    g.bevel(cloth, CRIMSON, face=0.58, bevel=1.3, grad=0.4, gain=0.85, tone=wave)
    # gold trim band along the cloth's top + bottom edge
    trim = cloth & ~K._erode(K._erode(K._erode(K._erode(K._erode(K._erode(K._erode(K._erode(cloth, True), False), True), False),
                                                         True), False), True), False)
    g.put(trim, rs(GOLD, 0.62))
    # crossbar (gold) and the steel guard-shield emblem on the banner
    bar = capsule(19.8, 24.6, 44.0, 24.6 + 1.2 * math.sin(1.4 * math.pi) * 0.5, 1.15)
    g.bevel(bar, GOLD, face=0.62, bevel=0.6, grad=0.3, gain=0.8)
    ex, ey = 32.0, 35.0
    sh = poly([(ex - 6.0, ey - 6.5), (ex + 6.0, ey - 6.5), (ex + 6.0, ey + 0.5), (ex + 3.6, ey + 5.0), (ex, ey + 7.6),
               (ex - 3.6, ey + 5.0), (ex - 6.0, ey + 0.5)])
    g.bevel(sh, GOLD, face=0.62, bevel=0.8, grad=0.3, gain=0.85)
    shf = poly([(ex - 4.4, ey - 5.0), (ex + 4.4, ey - 5.0), (ex + 4.4, ey + 0.2), (ex + 2.6, ey + 3.8), (ex, ey + 5.8),
                (ex - 2.6, ey + 3.8), (ex - 4.4, ey + 0.2)])
    g.bevel(shf, STEEL, face=0.72, bevel=0.7, grad=0.4, gain=0.8)
    g.bevel(shf & (X > ex), STEEL, face=0.52, bevel=0.0001, grad=0.3, gain=0.0)
    # spear head (leaf blade) + gold socket ring
    head = poly([(hx_, hy_ - 9.0), (hx_ + 3.2, hy_ - 2.0), (hx_ + 1.4, hy_ + 3.6), (hx_ - 1.4, hy_ + 3.6), (hx_ - 3.2, hy_ - 2.0)])
    g.bevel(head, STEEL, face=0.74, bevel=0.9, grad=0.25, gain=0.95)
    g.bevel(head & (X > hx_), STEEL, face=0.52, bevel=0.0001, grad=0.2, gain=0.0)
    g.bevel(capsule(hx_ - 2.2, hy_ + 4.6, hx_ + 2.2, hy_ + 4.6, 1.2), GOLD, face=0.65, bevel=0.5, grad=0.3, gain=0.8)
    glints = [(20, 12, "#f0f2f4"), (28, 30, "#f0f2f4")]
    return back, g, front, glints


def shield_shockwave():
    """Shield Shockwave: a round oak shield (iron rim, steel boss) slamming forward, three amber shock arcs fanning out in a
    cone, stun stars (cone stun)"""
    back, g, front = L3()
    cx, cy, R = 22.5, 33.0, 12.6
    glow(back, circle(cx + 10, cy, 10), "#e0b060", 6.0, 0.6)
    # shock arcs (cone to the right), getting wider + fainter
    for r0, w, al, half in ((15.2, 2.6, 1.0, 38.0), (19.8, 2.3, 0.85, 34.0), (24.2, 2.0, 0.7, 30.0)):
        back.put(arc_band(cx, cy, r0, r0 + w, -half, half), rs(AMBER, 0.88), alpha=al)
    # speed lines behind the shield (the slam)
    for dy in (-7.0, 0.0, 7.0):
        front.put(capsule(cx - R - 1.0, cy + dy, cx - R - 5.0, cy + dy, 0.55), rs(AMBER, 0.75), alpha=0.9)
    sh = circle(cx, cy, R)
    # oak planks with dark seams
    g.bevel(sh, OAK, face=0.62, bevel=1.4, grad=0.4, gain=0.8)
    for k in (-6.2, -2.0, 2.2, 6.4):
        g.put((np.abs(X - (cx + k)) < 0.38) & sh, rs(OAK, 0.18))
    # iron rim + rivets
    rim = ring(cx, cy, R, R - 2.2)
    ang = np.arctan2(Y - cy, X - cx)
    g.put(rim, rs(STEEL, 0.52 + 0.30 * np.clip(-np.sin(ang) * 0.8 - np.cos(ang) * 0.45, -1, 1)))
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        g.bevel(circle(cx + math.cos(a) * (R - 1.1), cy + math.sin(a) * (R - 1.1), 0.75), STEEL, face=0.85, bevel=0.3,
                grad=0.2, gain=0.6)
    # steel boss (dome) + its flange
    g.bevel(circle(cx, cy, 5.6), IRON, face=0.55, bevel=0.6, grad=0.3, gain=0.8)
    boss = circle(cx, cy, 4.3)
    d = np.sqrt((X - (cx - 1.4)) ** 2 + (Y - (cy - 1.6)) ** 2) / 4.6
    g.put(boss, rs(STEEL, 0.92 - d * 0.62))
    # stun stars ahead of the shield
    for sx, sy, ro in ((45.0, 22.0, 3.6), (47.5, 40.0, 3.0)):
        st = star(sx, sy, ro, ro * 0.42, 5, -90)
        g.bevel(st, GOLD, face=0.82, bevel=0.5, grad=0.2, gain=0.6)
    glints = [(20, 30, "#f0f2f4"), (15, 23, "#d6dae2")]
    return back, g, front, glints


def chain_link(g, cx, cy, ang, face_on, L=8.4, W=5.8):
    """one iron chain link centred (cx, cy) along direction ang (deg); face_on = ring with a hole, else an edge-on bar"""
    a = math.radians(ang)
    if face_on:
        outer = ellipse(cx, cy, L / 2.0, W / 2.0, ang)
        hole = ellipse(cx, cy, L / 2.0 - 2.0, W / 2.0 - 1.9, ang)
        m = outer & ~hole
        g.bevel(m, STEEL, face=0.62, bevel=0.6, grad=0.35, gain=0.95)
        return outer
    ux, uy = math.cos(a), math.sin(a)
    m = capsule(cx - ux * L / 2.0, cy - uy * L / 2.0, cx + ux * L / 2.0, cy + uy * L / 2.0, 1.25)
    g.bevel(m, IRON, face=0.78, bevel=0.5, grad=0.3, gain=0.9)
    return m


def iron_chain():
    """Iron Chain: a heavy iron hook flying out on a chain, amber pull streaks along the chain (hook one enemy, drag it in)"""
    back, g, front = L3()
    # chain path: from the lower left (you) up to the hook (upper right)
    p0, p1 = (13.0, 48.5), (36.0, 26.0)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    Lc = math.hypot(dx, dy)
    ux, uy = dx / Lc, dy / Lc
    ang = math.degrees(math.atan2(dy, dx))
    glow(back, circle(41.0, 22.0, 9), "#e0b060", 5.0, 0.75)
    # pull streaks either side of the chain, pointing back toward you
    nx, ny = -uy, ux
    for off, t0, t1 in ((7.6, 0.18, 0.55), (-7.6, 0.40, 0.80)):
        a0 = (p0[0] + dx * t0 + nx * off, p0[1] + dy * t0 + ny * off)
        a1 = (p0[0] + dx * t1 + nx * off, p0[1] + dy * t1 + ny * off)
        back.put(capsule(a0[0], a0[1], a1[0], a1[1], 0.9), rs(AMBER, 0.8), alpha=0.85)
    n = 5
    step = 6.4
    for k in range(n):
        c = (p0[0] + ux * step * k, p0[1] + uy * step * k)
        if k % 2 == 1:
            chain_link(g, c[0], c[1], ang, face_on=False)
    for k in range(0, n, 2):
        c = (p0[0] + ux * step * k, p0[1] + uy * step * k)
        chain_link(g, c[0], c[1], ang, face_on=True)
    # hook: eye ring at the chain end, shank, J curve + barb (built in a local frame, shank along +y, then rotated)
    ex, ey = p0[0] + ux * step * n - ux * 0.8, p0[1] + uy * step * n - uy * 0.8
    rot = ang - 90.0                     # local +y -> chain direction

    def T(pts):
        return rotpts([(ex + x, ey + y) for x, y in pts], ex, ey, rot)
    eye = ring(ex, ey, 3.3, 1.6)
    shank = poly(T([(-2.5, 2.4), (2.5, 2.4), (2.7, 11.5), (-2.3, 11.5)]))
    jc = (-5.2, 11.5)
    outer, inner = [], []
    for k in range(13):
        a = math.radians(0 + k * 15.0)
        outer.append((jc[0] + math.cos(a) * 7.7, jc[1] + math.sin(a) * 7.7))
        inner.append((jc[0] + math.cos(a) * 2.8, jc[1] + math.sin(a) * 2.8))
    curve = poly(T(outer + inner[::-1]))
    barb = poly(T([(-13.2, 12.0), (-7.6, 12.0), (-10.0, 2.0)]))
    hook = shank | curve | barb
    g.bevel(hook, STEEL, face=0.68, bevel=1.0, grad=0.3, gain=0.95)
    g.bevel(eye, STEEL, face=0.62, bevel=0.5, grad=0.3, gain=0.9)
    glints = [(40, 25, "#f0f2f4")]
    return back, g, front, glints


def arrow(g, x0, y0, x1, y1, broken=False):
    """an arrow, tail (x0, y0) -> tip (x1, y1); the tip is buried in the shield (not drawn); fletching at the tail"""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    shaft = capsule(x0, y0, x1, y1, 0.85)
    g.bevel(shaft, OAK, face=0.75, bevel=0.4, grad=0.2, gain=0.7)
    for s in (1, -1):
        fl = poly([(x0 + ux * 0.5, y0 + uy * 0.5), (x0 + ux * 5.0, y0 + uy * 5.0),
                   (x0 + ux * 1.0 + nx * 2.6 * s, y0 + uy * 1.0 + ny * 2.6 * s), (x0 - ux * 0.8 + nx * 2.4 * s, y0 - uy * 0.8 + ny * 2.4 * s)])
        g.bevel(fl, CRIMSON, face=0.66, bevel=0.4, grad=0.2, gain=0.7)
    if broken:
        g.bevel(poly([(x1 - ux * 0.5 + nx * 1.6, y1 - uy * 0.5 + ny * 1.6), (x1 + ux * 3.6, y1 + uy * 3.6),
                      (x1 - ux * 0.5 - nx * 1.6, y1 - uy * 0.5 - ny * 1.6)]), STEEL, face=0.7, bevel=0.4, grad=0.2, gain=0.7)


def bulwark_stance():
    """Bulwark Stance: a tall tower shield planted in the ground, arrows stuck in its face and one glancing off (front
    projectiles blocked, allies behind you safe)"""
    back, g, front = L3()
    cx = 29.0
    top, bot, hw = 13.0, 50.5, 10.8
    glow(back, circle(cx + 4, 32.0, 14), "#e0b060", 7.0, 0.5)
    # ground shadow where it is planted
    back.put(ellipse(cx, 52.0, 14.0, 2.4), rs(IRON, 0.05), alpha=0.75)
    outline_pts = [(cx - hw, top + 4.0), (cx - hw + 2.5, top + 0.6), (cx, top - 1.6), (cx + hw - 2.5, top + 0.6), (cx + hw, top + 4.0),
                   (cx + hw, bot - 6.0), (cx + hw - 3.5, bot - 1.5), (cx, bot + 0.8), (cx - hw + 3.5, bot - 1.5), (cx - hw, bot - 6.0)]
    shield = poly(outline_pts)
    g.bevel(shield, GOLD, face=0.62, bevel=1.2, grad=0.45, gain=0.9)
    inset = shield & K._erode(shield, True)
    for _ in range(14):
        inset = K._erode(inset, _ % 2 == 0)
    g.bevel(inset, STEEL, face=0.66, bevel=1.0, grad=0.5, gain=0.8)
    g.bevel(inset & (X > cx), STEEL, face=0.48, bevel=0.0001, grad=0.45, gain=0.0)
    # crimson pale (vertical stripe) + a gold boss on it
    pale = inset & (np.abs(X - cx) < 3.0)
    g.bevel(pale, CRIMSON, face=0.6, bevel=0.5, grad=0.45, gain=0.6)
    g.bevel(circle(cx, 31.0, 3.6), GOLD, face=0.66, bevel=0.8, grad=0.4, gain=0.9)
    # rivets down both sides
    for yy in (19.0, 27.0, 35.0, 43.0):
        for xx in (cx - hw + 2.6, cx + hw - 2.6):
            g.bevel(circle(xx, yy, 0.8), GOLD, face=0.8, bevel=0.3, grad=0.2, gain=0.6)
    # arrows from the right, stuck in the face (front projectiles blocked)
    arrow(g, 53.0, 30.0, cx + 6.0, 30.5)
    arrow(g, 51.0, 44.5, cx + 6.0, 41.0)
    arrow(g, 50.0, 15.5, cx + 7.0, 18.0)
    sparkle(front, cx + 7.4, 31.5, 2.4, "#fff0cc", None, 0.55)
    glints = [(22, 15, "#f0f2f4")]
    return back, g, front, glints


def unbreakable():
    """Unbreakable: a closed great helm, cracked all over but held together - the cracks glow amber (you cannot drop below
    1 HP), chips flying off"""
    back, g, front = L3()
    cx, cy = 32.0, 33.0
    glow(back, circle(cx, cy, 14), "#e0b060", 7.0, 0.8)
    # helm silhouette: flat-ish top, straight sides, flared lower edge
    helm = poly([(cx - 12.0, cy - 9.0), (cx - 8.5, cy - 15.5), (cx, cy - 17.0), (cx + 8.5, cy - 15.5), (cx + 12.0, cy - 9.0),
                 (cx + 12.5, cy + 9.0), (cx + 14.0, cy + 15.0), (cx, cy + 17.0), (cx - 14.0, cy + 15.0), (cx - 12.5, cy + 9.0)])
    g.bevel(helm, STEEL, face=0.63, bevel=1.6, grad=0.55, gain=0.95)
    # shading: right half darker (rounded barrel)
    g.bevel(helm & (X > cx + 2.0), STEEL, face=0.45, bevel=0.0001, grad=0.5, gain=0.0, tone=None)
    g.bevel(helm & (X > cx + 2.0) & (X < cx + 3.2), STEEL, face=0.55, bevel=0.0001, grad=0.4, gain=0.0)
    # riveted iron bands (vertical brow-to-chin band + brow band)
    vband = helm & (np.abs(X - cx) < 1.9) & (Y < cy + 16.5)
    brow = helm & (np.abs(Y - (cy - 6.5)) < 1.6)
    g.bevel(vband | brow, IRON, face=0.62, bevel=0.6, grad=0.4, gain=0.85)
    for rx_, ry_ in ((cx, cy - 13.0), (cx, cy + 3.0), (cx, cy + 10.0), (cx - 8.0, cy - 6.5), (cx + 8.0, cy - 6.5)):
        g.bevel(circle(rx_, ry_, 0.8), STEEL, face=0.85, bevel=0.3, grad=0.2, gain=0.6)
    # eye slits (dark) either side of the band
    for s in (-1, 1):
        slit = poly([(cx + s * 2.6, cy - 3.4), (cx + s * 10.6, cy - 3.4), (cx + s * 10.2, cy - 1.0), (cx + s * 2.6, cy - 1.0)])
        g.put(slit, rs(IRON, 0.06))
    # breath holes (lower right)
    for bx, by in ((cx + 5.0, cy + 6.0), (cx + 8.0, cy + 6.0), (cx + 5.0, cy + 9.0), (cx + 8.0, cy + 9.0), (cx + 6.5, cy + 12.0)):
        g.put(circle(bx, by, 0.75), rs(IRON, 0.1))
    # glowing cracks (kintsugi): jagged lines held together with gold light
    cracks = line([(cx - 11.0, cy - 12.0), (cx - 7.0, cy - 9.0), (cx - 8.5, cy - 4.5), (cx - 5.0, cy + 1.0), (cx - 8.0, cy + 6.0),
                   (cx - 6.0, cy + 11.0)], 2.0)
    cracks |= line([(cx + 12.0, cy - 6.0), (cx + 9.0, cy - 9.5), (cx + 6.0, cy - 12.0), (cx + 4.0, cy - 16.5)], 2.0)
    cracks |= line([(cx + 13.5, cy + 13.0), (cx + 10.0, cy + 10.0), (cx + 11.0, cy + 4.5)], 1.8)
    cracks &= helm
    edge = cracks.copy()
    for _ in range(6):
        edge = ~K._erode(~edge, _ % 2 == 0)
    g.put(edge & helm, rs(IRON, 0.10))
    g.put(cracks, rs(AMBER, 0.66))
    core = cracks.copy()
    for _ in range(3):
        core = K._erode(core, _ % 2 == 0)
    g.put(core, rs(AMBER, 0.93))
    glow(front, cracks, "#f4d48c", 0.9, 0.35)
    # chips flying off
    for px, py, pr in ((15.0, 18.0, 1.4), (49.0, 22.0, 1.2), (47.5, 45.0, 1.1)):
        g.bevel(poly([(px - pr, py), (px, py - pr * 1.3), (px + pr, py + 0.2), (px + 0.2, py + pr)]), STEEL, face=0.7, bevel=0.3,
                grad=0.2, gain=0.6)
    sparkle(front, 46.0, 14.5, 2.4, "#fff0cc", None, 0.55)
    glints = [(25, 18, "#f0f2f4"), (26, 19, "#d6dae2")]
    return back, g, front, glints


ICONS = [
    # (class style, file name, display name, painter)
    (MAGE, "Meteor", "Meteor", meteor),
    (MAGE, "ManaBarrier", "Mana Barrier", mana_barrier),
    (MAGE, "FrostNova", "Frost Nova", frost_nova),
    (MAGE, "Starfall", "Starfall", starfall),
    (MAGE, "ArcaneBeam", "Arcane Beam", arcane_beam),
    (PRIEST, "SacredHeal", "Sacred Heal", sacred_heal),
    (PRIEST, "ShieldBubble", "Shield Bubble", shield_bubble),
    (PRIEST, "GuardianSpirit", "Guardian Spirit", guardian_spirit),
    (PRIEST, "Sanctuary", "Sanctuary", sanctuary),
    (PRIEST, "MartyrsGrace", "Martyr's Grace", martyrs_grace),
    (MONK, "FlowingForm", "Flowing Form", flowing_form),
    (MONK, "PalmStrike", "Palm Strike", palm_strike),
    (MONK, "CycloneKick", "Cyclone Kick", cyclone_kick),
    (MONK, "HundredFists", "Hundred Fists", hundred_fists),
    (MONK, "StillWater", "Still Water", still_water),
    (ASSASSIN, "CloakFirstStrike", "Cloak + First Strike", cloak_first_strike),
    (ASSASSIN, "Toxin", "Toxin", toxin),
    (ASSASSIN, "GodKiller", "God Killer", god_killer),
    (ASSASSIN, "ShadowClone", "Shadow Clone", shadow_clone),
    (ASSASSIN, "VanishingAct", "Vanishing Act", vanishing_act),
    (WARRIOR, "RallyingGuard", "Rallying Guard", rallying_guard),
    (WARRIOR, "ShieldShockwave", "Shield Shockwave", shield_shockwave),
    (WARRIOR, "IronChain", "Iron Chain", iron_chain),
    (WARRIOR, "BulwarkStance", "Bulwark Stance", bulwark_stance),
    (WARRIOR, "Unbreakable", "Unbreakable", unbreakable),
]


def rel_path(style, fname):
    return "Common/Icons/Abilities/%s/%s.png" % (style.name, fname)


def render(painter, style):
    back, g, front, glints = painter()
    return K.compose(style, back, g, front, glints=glints)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = set(s for s in a.only.split(",") if s)
    for style, fname, _disp, painter in ICONS:
        if only and fname not in only:
            continue
        im = render(painter, style)
        p = os.path.join(a.out, rel_path(style, fname))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p, optimize=True)
        print("wrote", p)


if __name__ == "__main__":
    main()
