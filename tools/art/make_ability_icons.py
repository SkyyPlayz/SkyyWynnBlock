#!/usr/bin/env python3
"""make_ability_icons - SkyWynn class ability icons, Mage + Priest (10 x 64x64 RGBA), our own art drawn from code.

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
