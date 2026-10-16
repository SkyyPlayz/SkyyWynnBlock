#!/usr/bin/env python3
"""make_pet_eggs - SkyWynn PET EGG art, round A0 of research/Pet-Eggs-Spec.md (sections 1.1, 1.2, 8). DRAFT for Skyy's review.

Writes (original pixels drawn from code; no vanilla file, other mod or reference picture is read, copied or traced):
  art/pet-eggs/Common/Icons/ItemsGenerated/Skyy_PetEgg_<Category>_<Rarity>.png   30 item icons, 64 x 64 RGBA
  art/pet-eggs/Common/Items/Pets/Skyy_PetEgg_<Rarity>_Texture.png                  6 world / held textures, 32 x 32 RGBA, laid out
                                                                                 for the vanilla egg model's box UVs (see below)
  art/pet-eggs/sheet.png       review sheet (all 30 at 2x on rarity slots + 64 / 32 px strip, the 6 textures at 8x + a cube preview)
  art/pet-eggs/manifest.json   file list (bytes, sha256), ids, names, palettes

The look (Skyy, docs/answered/pets.md 2026-10-15 PET EGGS + HATCHING: "eggs come in rarities from common to mythic"; spec 1.2: "one
egg silhouette; shell colour by category (Mining slate blue, Farming wheat gold, Foraging bark green, Combat red, Exploration teal);
speckles + rim glow by rarity (quality colours, Mythic = shimmer)"):
  * CATEGORY = the shell colour + a motif on the shell: Mining - ore crystals growing out of a cracked slate shell + gold flecks;
    Farming - a wheat ear with leaves on a golden shell; Foraging - bark grain + a leaf sprout from the top; Combat - two crossed
    swords embossed on a red shell + claw scratches; Exploration - a gold compass star + a dotted trail on a teal shell.
  * RARITY = the approved accessory rarity look (growing gem + metal, docs/answered/gear.md accessory icons "Love them"): the egg
    sits in a metal EGG CUP whose metal climbs Common iron -> Uncommon bronze -> Rare silver -> Epic gold -> Legendary ornate gold
    (milgrain + claws) -> Mythic platinum with a prismatic shimmer; a front GEM in the vanilla quality colour grows (round ->
    faceted diamond -> claws -> milgrain -> star); rarity-coloured SPECKLES on the shell grow in number; a RIM GLOW + soft halo from
    Rare up; sparkles on Legendary / Mythic. Quality colours = tools/skyyui.py QUALITY (vanilla Server/Item/Qualities) + Mythic
    SUI.RARITY["Mythic"] #CC66CC (the Skyy_Pet_Mythic quality).

Model texture (spec 1.1 "vanilla Items/Consumables/Food/Egg.blockymodel by path + our own texture per rarity"): the vanilla egg
model is ONE box 14 x 16 x 14 with a custom UV layout on a 32 x 32 texture (read from Assets.zip on 2026-10-16, numbers only):
front (0,0) 14x16, top (14,0) 14x14, back / left / right all (14,14) 14x16, bottom (0,16) 14x14. Our 6 textures use that layout.

numpy + Pillow; paint engine = tools/art/ability_icon_core.py (8x supersampled masks, bevels, top-left light, hue-shifted ramps).
Deterministic: two runs = same bytes.
Run:  python tools/art/make_pet_eggs.py [--out DIR]
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ability_icon_core as K  # noqa: E402
from ability_icon_core import (Layer, capsule, circle, ellipse, glow, hx, line, poly, ramp, ring, rotpts, rs, star,  # noqa: E402
                               X, Y)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(ROOT, "art", "pet-eggs")
ICON_REL = "Common/Icons/ItemsGenerated/Skyy_PetEgg_%s_%s.png"
TEX_REL = "Common/Items/Pets/Skyy_PetEgg_%s_Texture.png"

CATEGORIES = ["Mining", "Farming", "Foraging", "Combat", "Exploration"]
RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
# vanilla quality colours (tools/skyyui.py QUALITY) + our Mythic (SUI.RARITY["Mythic"])
QCOL = {"Common": "#c9d2dd", "Uncommon": "#3e9049", "Rare": "#2770b7", "Epic": "#8b339e", "Legendary": "#bb8a2c",
        "Mythic": "#cc66cc"}

# ------------------------------------------------------------------------------------------------------------ palettes
# shells (dark -> light; shadows lean cool / violet, lights lean warm; no #000 / #fff)
SHELL = {
    "Mining": ramp("#1a2232", "#28344c", "#3a4c68", "#526a88", "#7090ac", "#9cb8cc", "#d0e2ea"),       # slate blue
    "Farming": ramp("#4a2c10", "#7a4e18", "#a87824", "#d0a23a", "#e8c460", "#f6e094", "#fdf4cc"),      # wheat gold
    "Foraging": ramp("#1a2412", "#2c3a1a", "#425424", "#5a7030", "#7a8e44", "#a2b264", "#d0dca0"),     # bark green
    "Combat": ramp("#2e0c16", "#521420", "#82202a", "#b03434", "#d45a48", "#ee8c6e", "#fcc8a8"),       # red
    "Exploration": ramp("#0c2a30", "#144a50", "#1e6e72", "#2c9894", "#52bcb0", "#8edcc8", "#d0f6ea"),  # teal
}
OUTLINE = {"Mining": "#0a0e18", "Farming": "#1e1006", "Foraging": "#0a1008", "Combat": "#14040a", "Exploration": "#041416"}
CRYSTAL = ramp("#123a58", "#1e5e86", "#2e8cb4", "#52bcd8", "#94e2f0", "#dcfaff")
GOLDF = ramp("#4a2c08", "#7e5414", "#b8862a", "#e2b44a", "#f6d880", "#fff2c4")
LEAF = ramp("#102a12", "#1c4a1c", "#2c6e28", "#47923a", "#70b852", "#a8dc84")
STEEL = ramp("#2a2c40", "#43475e", "#62687e", "#868ca0", "#aeb4c2", "#d6dae2", "#f0f2f4")
DARKW = ramp("#1e1008", "#341c0e", "#4e2c16", "#6a4020")
# rarity metals for the egg cup (accessory look: iron, bronze, silver, gold, ornate gold, prismatic platinum)
METAL = {
    "Common": ramp("#16171c", "#26272e", "#3a3c44", "#52545e", "#6c6e78", "#8c8e96"),
    "Uncommon": ramp("#2a1408", "#4e2a12", "#7a4a20", "#a46a32", "#c88e52", "#e8b884"),
    "Rare": ramp("#262c3c", "#444c62", "#6a748c", "#96a0b6", "#c4cede", "#eaf0f8"),
    "Epic": ramp("#3e2208", "#6c4210", "#a06a1c", "#cf9a30", "#ecc458", "#fae6a0"),
    "Legendary": ramp("#4a2806", "#7e4c0e", "#b8801e", "#e6b03a", "#f8d670", "#fff4c8"),
    "Mythic": ramp("#2e2440", "#4c4466", "#787496", "#a8a8c6", "#d4d8ec", "#f4f4fc"),
}
GEM = {r: None for r in RARITIES}
GEM["Common"] = ramp("#3a3e48", "#6a7280", "#9aa4b2", "#c9d2dd", "#eef2f6")
GEM["Uncommon"] = ramp("#0e2a12", "#1c5424", "#2e7a38", "#3e9049", "#7cc884", "#c8f0cc")
GEM["Rare"] = ramp("#0a1c40", "#143a74", "#1e58a0", "#2770b7", "#6aa4e2", "#c4e0fc")
GEM["Epic"] = ramp("#260a30", "#4a1658", "#6c2480", "#8b339e", "#b872cc", "#ecc4f4")
GEM["Legendary"] = ramp("#3a2206", "#6c440c", "#9a6a1a", "#bb8a2c", "#e8c060", "#fff0b8")
GEM["Mythic"] = ramp("#3a0e3a", "#6a1e68", "#9a3c98", "#cc66cc", "#ec9cec", "#fcdcfc")
PRISM = ["#ff9ad8", "#c49cff", "#8cc8ff", "#8cf0d8", "#fff09c"]          # mythic shimmer hues

RARITY_IDX = {r: i for i, r in enumerate(RARITIES)}

# ------------------------------------------------------------------------------------------------------------ egg geometry
ECX, ECY, ERX, ERY = 32.0, 28.5, 15.0, 21.0          # the egg (64-px units): wider at the bottom, pointed-ish at the top
RIM_Y = 41.0                                          # top edge of the cup


def egg_mask(cx=ECX, cy=ECY, rx=ERX, ry=ERY):
    yn = (Y - cy) / ry
    w = rx * (1.0 + 0.17 * np.clip(yn, -1.2, 1.2))
    return ((X - cx) / w) ** 2 + yn ** 2 <= 1.0


def egg_normal(cx=ECX, cy=ECY, rx=ERX, ry=ERY):
    yn = (Y - cy) / ry
    w = rx * (1.0 + 0.17 * np.clip(yn, -1.2, 1.2))
    xn = (X - cx) / w
    d2 = np.clip(xn ** 2 + yn ** 2, 0, 1)
    nz = np.sqrt(1 - d2)
    lam = xn * K.LIGHT[0] + yn * K.LIGHT[1] + nz * K.LIGHT[2]
    return lam, np.sqrt(d2)


def rng_for(*keys):
    h = hashlib.sha256(("|".join(keys)).encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


def L3():
    return Layer(), Layer(), Layer()


def sparkle(layer, cx, cy, r, col, core=None, w=0.55):
    m = capsule(cx - r, cy, cx + r, cy, w, w) | capsule(cx, cy - r, cx, cy + r, w, w)
    layer.put(m, hx(col))
    if core:
        layer.put(circle(cx, cy, w * 1.4), hx(core))


# ------------------------------------------------------------------------------------------------------------ shell + motifs
def paint_shell(g, cat, egg):
    rmp = SHELL[cat]
    lam, d = egg_normal()
    t = 0.10 + 0.88 * np.clip(lam, 0, 1)
    g.put(egg, rs(rmp, t))
    # soft lower-right reflected light (bounce from the cup) + a crisp highlight
    g.put(egg & (d > 0.86) & (X > ECX + 3) & (Y > ECY + 4), rs(rmp, 0.42), alpha=0.6)
    hl = ellipse(ECX - 5.5, ECY - 9.5, 3.4, 5.0, -25)
    g.put(hl & egg, rs(rmp, 0.97), alpha=0.85)
    return t


def motif_mining(g, front, egg):
    # cracks in the slate shell
    for pts in ([(20.5, 22.0), (24.0, 25.5), (22.5, 29.0), (26.0, 33.0)], [(41.0, 17.0), (38.5, 21.0), (41.5, 24.5)],
                [(36.0, 33.0), (39.5, 36.0), (38.0, 39.0)]):
        g.put(line(pts, 0.9) & egg, rs(SHELL["Mining"], 0.08))
    # ore crystals growing out of the shell (faceted, cyan), the big one breaking the silhouette on the right
    for (cx, cy, h, w, rot) in ((40.5, 30.0, 9.0, 2.6, 28), (37.0, 28.5, 6.0, 2.0, 5), (43.5, 34.5, 5.0, 1.8, 55),
                                (24.5, 36.0, 5.5, 1.9, -30)):
        pts = rotpts([(cx - w, cy + 1.5), (cx - w, cy - h * 0.55), (cx, cy - h), (cx + w, cy - h * 0.55), (cx + w, cy + 1.5)],
                     cx, cy, rot)
        m = poly(pts)
        g.bevel(m, CRYSTAL, face=0.62, bevel=0.55, grad=0.35, gain=0.95)
        half = m & ((X - cx) * math.cos(math.radians(rot)) + (Y - cy) * math.sin(math.radians(rot)) > 0)
        g.bevel(half, CRYSTAL, face=0.42, bevel=0.0001, grad=0.3, gain=0.0)
    # gold ore flecks
    for (fx, fy) in ((25.5, 15.5), (31.0, 20.0), (28.0, 31.5), (33.5, 37.5), (21.0, 28.0)):
        g.bevel(poly([(fx - 1.2, fy), (fx, fy - 1.1), (fx + 1.3, fy + 0.2), (fx, fy + 1.1)]), GOLDF, face=0.7, bevel=0.3,
                grad=0.3, gain=0.8)


def motif_farming(g, front, egg):
    # a soil-brown band of furrows at the bottom of the shell
    for k, yy in enumerate((34.0, 37.0)):
        g.put(capsule(20.0 + k, yy, 44.0 - k, yy, 0.55) & egg, rs(SHELL["Farming"], 0.22))
    # wheat stalk + two leaves + the ear (alternating grains) up the front
    g.put(line([(30.5, 40.0), (31.0, 30.0), (32.5, 21.0)], 1.2) & egg, rs(LEAF, 0.55))
    for (pts, rot) in (([(31.0, 32.0), (24.0, 27.5), (21.5, 29.5), (26.5, 31.5)], 0), ([(31.2, 29.0), (38.0, 25.0), (40.5, 26.5),
                                                                                        (35.5, 29.5)], 0)):
        g.bevel(poly(pts), LEAF, face=0.6, bevel=0.4, grad=0.3, gain=0.8)
    for k in range(5):
        y = 22.5 - k * 2.7
        x = 32.6 + k * 0.25
        for s in (-1, 1):
            gr = ellipse(x + s * 1.5, y + (0.7 if s > 0 else 0.0), 1.25, 1.9, s * 25)
            g.bevel(gr, GOLDF, face=0.72 if s < 0 else 0.55, bevel=0.35, grad=0.3, gain=0.85)
    g.bevel(ellipse(33.8, 9.6, 0.9, 1.6, 10), GOLDF, face=0.75, bevel=0.3, grad=0.3, gain=0.8)
    for s in (-1, 1):                                                      # awns
        g.put(line([(32.8 + s * 1.5, 12.0), (32.8 + s * 4.0, 6.5)], 0.45) & egg, rs(GOLDF, 0.85))


def motif_foraging(g, front, egg):
    # bark grain: wavy vertical ridges
    for k in range(7):
        x0 = 20.0 + k * 4.0
        pts = [(x0 + 0.9 * math.sin(yy * 0.45 + k), yy) for yy in np.arange(10.0, 49.0, 1.5)]
        g.put(line(pts, 0.75) & egg, rs(SHELL["Foraging"], 0.20 + 0.04 * (k % 2)))
    # a knot
    g.put(ring(37.0, 31.0, 2.6, 1.6) & egg, rs(SHELL["Foraging"], 0.15))
    g.put(circle(37.0, 31.0, 1.5) & egg, rs(SHELL["Foraging"], 0.62))
    # moss patch
    rng = rng_for("moss")
    for _ in range(14):
        x, y = 22.0 + rng.random() * 7.0, 33.0 + rng.random() * 6.0
        g.put(circle(x, y, 0.9) & egg, rs(LEAF, 0.45 + rng.random() * 0.3))
    # a leaf sprout from the top of the egg (breaks the silhouette)
    g.put(capsule(32.0, 9.0, 32.6, 4.5, 0.7), rs(LEAF, 0.4))
    g.bevel(poly([(32.4, 5.5), (36.5, 1.8), (41.5, 2.6), (38.5, 6.2)]), LEAF, face=0.7, bevel=0.5, grad=0.3, gain=0.85)
    g.bevel(poly([(32.2, 6.5), (28.0, 3.4), (24.0, 4.6), (27.5, 7.5)]), LEAF, face=0.55, bevel=0.5, grad=0.3, gain=0.85)
    g.put(line([(33.0, 5.0), (39.5, 3.0)], 0.4), rs(LEAF, 0.85))


def motif_combat(g, front, egg):
    # three claw scratches (dark grooves with lit lower lips)
    for k in range(3):
        x0 = 20.0 + k * 2.6
        g.put(line([(x0, 16.0 + k), (x0 + 3.5, 25.0 + k)], 1.0) & egg, rs(SHELL["Combat"], 0.10))
        g.put(line([(x0 + 0.7, 16.4 + k), (x0 + 4.2, 25.4 + k)], 0.4) & egg, rs(SHELL["Combat"], 0.72))
    # two crossed swords embossed on the front
    for s in (-1, 1):
        x0, y0, x1, y1 = 32.0 - s * 8.0, 38.0, 32.0 + s * 6.5, 18.5
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        gx, gy = x0 + ux * 5.5, y0 + uy * 5.5
        blade = poly([(gx + nx * 1.5, gy + ny * 1.5), (x1 - ux * 2.4 + nx * 1.1, y1 - uy * 2.4 + ny * 1.1), (x1, y1),
                      (x1 - ux * 2.4 - nx * 1.1, y1 - uy * 2.4 - ny * 1.1), (gx - nx * 1.5, gy - ny * 1.5)])
        g.bevel(blade, STEEL, face=0.74, bevel=0.6, grad=0.2, gain=0.9)
        g.bevel(capsule(gx + nx * 3.6, gy + ny * 3.6, gx - nx * 3.6, gy - ny * 3.6, 0.9), GOLDF, face=0.62, bevel=0.4, grad=0.3,
                gain=0.8)
        g.bevel(capsule(x0 + ux * 0.8, y0 + uy * 0.8, gx, gy, 0.95), DARKW, face=0.55, bevel=0.3, grad=0.2, gain=0.8)
        g.bevel(circle(x0, y0, 1.25), GOLDF, face=0.65, bevel=0.3, grad=0.3, gain=0.8)


def motif_exploration(g, front, egg):
    # dotted trail winding across the shell to an X
    pts = [(19.0, 37.0), (23.0, 33.5), (21.5, 29.0), (25.5, 25.0), (30.0, 26.0)]
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        for t in (0.25, 0.75):
            g.put(circle(ax + (bx - ax) * t, ay + (by - ay) * t, 0.75) & egg, rs(SHELL["Exploration"], 0.92))
    for s in (-1, 1):
        g.put(capsule(41.0 - 1.6, 37.0 - 1.6 * s, 41.0 + 1.6, 37.0 + 1.6 * s, 0.55) & egg, rs(GOLDF, 0.3))
    # gold compass star (8 points: 4 long, 4 short) with a teal centre
    cx, cy = 34.0, 19.0
    g.bevel(star(cx, cy, 4.5, 1.6, n=4, rot=-45.0), GOLDF, face=0.55, bevel=0.4, grad=0.3, gain=0.85)
    big = star(cx, cy, 8.0, 2.0, n=4, rot=-90.0)
    g.bevel(big, GOLDF, face=0.7, bevel=0.5, grad=0.3, gain=0.9)
    # split each long point into a lit + a shaded half
    for k in range(4):
        a = math.radians(-90 + k * 90)
        tipx, tipy = cx + math.cos(a) * 8.0, cy + math.sin(a) * 8.0
        sx, sy = cx + math.cos(a + math.pi / 4) * 2.0, cy + math.sin(a + math.pi / 4) * 2.0
        g.bevel(poly([(cx, cy), (tipx, tipy), (sx, sy)]) & big, GOLDF, face=0.45, bevel=0.0001, grad=0.2, gain=0.0)
    g.bevel(circle(cx, cy, 1.3), SHELL["Exploration"], face=0.8, bevel=0.3, grad=0.3, gain=0.8)
    g.put(ring(cx, cy, 10.0, 9.2) & egg, rs(GOLDF, 0.45), alpha=0.7)


MOTIF = {"Mining": motif_mining, "Farming": motif_farming, "Foraging": motif_foraging, "Combat": motif_combat,
         "Exploration": motif_exploration}


# ------------------------------------------------------------------------------------------------------------ rarity: cup + gem
def cup_shapes():
    """the egg cup: a bowl hugging the egg's lower part (front), its rim ellipse, a stem and a round foot"""
    big = egg_mask(rx=ERX + 2.4, ry=ERY + 2.2)
    rim_curve = RIM_Y + 1.4 * ((X - ECX) / 18.0) ** 2
    bowl = big & (Y >= rim_curve) & (Y <= 51.0)
    half_w = 17.2
    rim = ellipse(ECX, RIM_Y, half_w, 2.2, 0)
    stem = poly([(ECX - 3.0, 49.5), (ECX + 3.0, 49.5), (ECX + 2.2, 55.0), (ECX - 2.2, 55.0)])
    foot = ellipse(ECX, 56.6, 10.5, 3.0, 0)
    return bowl, rim, stem, foot


def gem(g, front, rarity, cx, cy):
    r = RARITY_IDX[rarity]
    G, M = GEM[rarity], METAL[rarity]
    size = (1.7, 2.2, 2.8, 3.3, 3.8, 4.0)[r]
    if r <= 1:
        stone = circle(cx, cy, size)
    elif r == 5:
        stone = star(cx, cy, size + 0.8, size * 0.55, n=4, rot=-90.0) | circle(cx, cy, size * 0.55)
    else:
        stone = poly([(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)])
    setting = circle(cx, cy, size + 1.1) if r <= 1 else poly([(cx, cy - size - 1.3), (cx + size + 1.3, cy), (cx, cy + size + 1.3),
                                                               (cx - size - 1.3, cy)])
    g.bevel(setting, M, face=0.62, bevel=0.5, grad=0.35, gain=0.9)
    if r >= 4:                                                     # milgrain beads round the setting
        for k in range(12):
            a = math.radians(k * 30)
            g.put(circle(cx + math.cos(a) * (size + 1.9), cy + math.sin(a) * (size + 1.9), 0.55), rs(M, 0.85 if k % 2 else 0.5))
    if r >= 2:                                                     # claws on the diagonals
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            g.bevel(circle(cx + dx * size * 0.62, cy + dy * size * 0.62, 0.75), M, face=0.75, bevel=0.3, grad=0.3, gain=0.8)
    g.bevel(stone, G, face=0.6, bevel=0.8 if r >= 2 else 0.6, grad=0.4, gain=1.0)
    if r >= 2:                                                     # table facet
        tbl = poly([(cx, cy - size * 0.42), (cx + size * 0.42, cy), (cx, cy + size * 0.42), (cx - size * 0.42, cy)])
        g.bevel(tbl, G, face=0.82, bevel=0.0001, grad=0.3, gain=0.0)
    front.put(circle(cx - size * 0.35, cy - size * 0.4, 0.55), rs(G, 1.0))


def paint_cup(back, g, front, rarity):
    r = RARITY_IDX[rarity]
    M = METAL[rarity]
    bowl, rim, stem, foot = cup_shapes()
    g.bevel(foot, M, face=0.5, bevel=0.7, grad=0.4, gain=0.9)
    g.bevel(stem, M, face=0.55, bevel=0.6, grad=0.3, gain=0.9)
    # bowl: shaded like a metal surface of revolution (bright band on the left, dark right)
    xn = np.clip((X - ECX) / 18.0, -1, 1)
    tone = -0.32 * xn + 0.18 * np.exp(-((xn + 0.45) / 0.18) ** 2)
    g.bevel(bowl, M, face=0.52, bevel=0.6, grad=0.25, gain=0.75, tone=tone)
    # decoration on the bowl by rarity
    if r >= 1:                                                      # an engraved band
        band = bowl & (np.abs(Y - (RIM_Y + 4.6 + 1.0 * ((X - ECX) / 18.0) ** 2)) < 0.55)
        g.put(band, rs(M, 0.2))
    if r >= 4:                                                      # ornate scrolls (Legendary / Mythic)
        for s in (-1, 1):
            sc = ring(ECX + s * 10.5, 46.5, 2.6, 1.7) & bowl & ((X - (ECX + s * 10.5)) * s < 0.8)
            g.put(sc, rs(M, 0.92))
            g.put(circle(ECX + s * 10.5, 46.5, 0.7) & bowl, rs(M, 0.95))
    # the rim: a thick lip in front of the egg (front half of the rim ellipse)
    lip = rim & (Y >= RIM_Y - 0.2)
    g.bevel(lip | (ellipse(ECX, RIM_Y, 17.2, 2.2, 0) & ~ellipse(ECX, RIM_Y - 0.6, 15.4, 1.4, 0)), M, face=0.75, bevel=0.45,
            grad=0.5, gain=0.85, tone=-0.22 * xn)
    if r == 5:                                                      # mythic: prismatic sheen bands across the platinum
        cupall = bowl | foot | stem
        for k, c in enumerate(PRISM):
            bandk = cupall & (np.abs((X - ECX) * 0.7 + (Y - 48.0) - (-9.0 + k * 4.5)) < 1.0)
            g.put(bandk, hx(c), alpha=0.45)
    gem(g, front, rarity, ECX, 46.8)


def speckles(g, egg, cat, rarity):
    r = RARITY_IDX[rarity]
    n = (5, 7, 9, 12, 14, 18)[r]
    rng = rng_for("speck", cat, rarity)
    G = GEM[rarity]
    for _ in range(n):
        for _try in range(20):
            x = ECX + (rng.random() * 2 - 1) * 12.5
            y = ECY + (rng.random() * 2 - 1) * 15.0 - 3.0
            if egg[int(y * K.SS), int(x * K.SS)] and y < RIM_Y - 1.5:
                break
        rr = 0.55 + rng.random() * 0.55
        if rarity == "Mythic":
            col = hx(PRISM[int(rng.random() * len(PRISM))])
        else:
            col = rs(G, 0.75 if r else 0.35)
        g.put(circle(x, y, rr) & egg, col, alpha=0.95)


def rim_glow(back, front, egg, rarity):
    r = RARITY_IDX[rarity]
    if r < 2:
        return
    col = hx(QCOL[rarity])
    strength = (0, 0, 0.45, 0.6, 0.8, 0.9)[r]
    if rarity == "Mythic":
        for k, c in enumerate(PRISM):
            a = math.radians(k * 72 - 90)
            glow(back, circle(ECX + math.cos(a) * 9.0, ECY + math.sin(a) * 12.0, 8.0), c, 4.0, 0.35)
    glow(back, egg, col, 3.2, strength)
    # rim light on the shell edge (inside the silhouette)
    lam, d = egg_normal()
    edge = egg & (d > 0.84) & (Y < RIM_Y)
    front.put(edge, col if rarity != "Legendary" else hx("#f8d670"), alpha=np.clip((d - 0.84) / 0.16, 0, 1) * 0.55 * strength / 0.9)


def egg_icon(cat, rarity):
    back, g, front = L3()
    egg = egg_mask()
    rim_glow(back, front, egg, rarity)
    paint_shell(g, cat, egg)
    MOTIF[cat](g, front, egg)
    speckles(g, egg, cat, rarity)
    paint_cup(back, g, front, rarity)
    # sparkles (Legendary / Mythic)
    r = RARITY_IDX[rarity]
    if r >= 4:
        sp = [(13.0, 15.0, 2.6), (51.0, 21.0, 2.0), (50.0, 44.0, 1.6)] if r == 5 else [(13.5, 16.0, 2.4), (51.0, 22.0, 1.8)]
        for k, (sx, sy, rr) in enumerate(sp):
            c = PRISM[(k * 2) % len(PRISM)] if r == 5 else "#fff0b8"
            sparkle(front, sx, sy, rr, c, "#fffaf0", 0.5)
    return compose(back, g, front, OUTLINE[cat])


def compose(back, glyph, front, outline_hex):
    """item icon: soft halo (partial alpha) behind; the opaque egg + cup with a 1 px dark outline; front light over it"""
    brgb, ba = K.down(back)
    grgb, ga = K.down(glyph)
    frgb, fa = K.down(front)
    gm = ga >= 0.5
    ol = K.dilate64(gm) & ~gm
    gcol = grgb / np.maximum(ga[..., None], 1e-6)
    bcol = brgb / np.maximum(ba[..., None], 1e-6)
    fcol = frgb / np.maximum(fa[..., None], 1e-6)
    out = np.zeros((64, 64, 3))
    alpha = np.clip(ba, 0, 1) * 0.85
    out[:] = bcol
    out[ol] = hx(outline_hex)
    alpha[ol] = 1.0
    out[gm] = gcol[gm]
    alpha[gm] = 1.0
    # front light: over the glyph only where it is opaque; free-standing sparkles become opaque pixels
    fm = fa > 0.05
    out[fm] = out[fm] * (1 - fa[fm][..., None]) + fcol[fm] * fa[fm][..., None]
    alpha[fm & ~gm] = np.maximum(alpha[fm & ~gm], np.where(fa[fm & ~gm] >= 0.5, 1.0, fa[fm & ~gm]))
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    allw = (out >= 252).all(axis=-1)
    out[allw] = (250, 248, 240)
    allb = (out <= 4).all(axis=-1)
    out[allb] = (10, 8, 16)
    a8 = np.clip(np.round(alpha * 255), 0, 255).astype(np.uint8)
    a8[a8 < 8] = 0
    rgba = np.dstack([out, a8])
    rgba[a8 == 0] = 0
    return Image.fromarray(rgba, "RGBA")


# ------------------------------------------------------------------------------------------------------------ textures (32x32)
FACES = {"front": (0, 0, 14, 16), "top": (14, 0, 14, 14), "side": (14, 14, 14, 16), "bottom": (0, 16, 14, 14)}
TEX_SHELL = ramp("#5a4636", "#8a705a", "#b49c82", "#d4c0a4", "#eadcc4", "#f8f0e2")   # warm ivory shell (all rarities)


def egg_texture(rarity):
    """32 x 32, the vanilla egg box's UV layout. Ivory shell with soft round shading per face (like a rounded egg on a box),
    rarity-coloured speckles growing with the rarity, a rarity-metal band round the bottom of the sides + front, Mythic shimmer"""
    r = RARITY_IDX[rarity]
    rng = rng_for("tex", rarity)
    img = np.zeros((32, 32, 4), np.uint8)
    G, M = GEM[rarity], METAL[rarity]
    tint = hx(QCOL[rarity])
    for name, (x0, y0, w, h) in FACES.items():
        yy, xx = np.mgrid[0:h, 0:w]
        u = (xx + 0.5) / w * 2 - 1
        v = (yy + 0.5) / h * 2 - 1
        d = np.sqrt(u ** 2 + v ** 2)
        light = {"top": 0.86, "front": 0.66, "side": 0.56, "bottom": 0.36}[name]
        t = light + 0.18 * (1 - np.clip(d, 0, 1.4)) - 0.10 * u - 0.10 * v
        col = rs(TEX_SHELL, t)
        col = col * (1 - 0.10 * min(r, 4) / 4) + tint * (0.10 * min(r, 4) / 4)      # a faint rarity tint from Uncommon up
        if rarity == "Mythic":
            hue = (u + v + 2) / 4 * (len(PRISM) - 1)
            i0 = np.clip(hue.astype(int), 0, len(PRISM) - 2)
            f = (hue - i0)[..., None]
            pr = np.array([hx(c) for c in PRISM])
            col = col * 0.72 + (pr[i0] * (1 - f) + pr[i0 + 1] * f) * 0.28
        # speckles
        n = (3, 4, 5, 6, 7, 9)[r] if name != "bottom" else 2
        for _ in range(n):
            sx, sy = int(rng.random() * w), int(rng.random() * h)
            c = hx(PRISM[int(rng.random() * len(PRISM))]) if rarity == "Mythic" else rs(G, 0.62 if r else 0.3)
            col[sy, sx] = c
            if r >= 3 and sx + 1 < w and rng.random() < 0.5:
                col[sy, sx + 1] = rs(G, 0.45) if rarity != "Mythic" else c
        # metal band (front + sides): 3 rows near the bottom, a bright top line, a gem dot in the middle of the front
        if name in ("front", "side"):
            by = h - 5
            for k in range(3):
                bt = 0.75 - 0.18 * k - 0.15 * (xx[0] / w)
                col[by + k, :] = rs(M, bt)
            if name == "front" and r >= 1:
                col[by:by + 3, w // 2 - 1:w // 2 + 1] = rs(G, 0.7)
                col[by, w // 2 - 1] = rs(G, 0.95)
        img[y0:y0 + h, x0:x0 + w, :3] = np.clip(np.round(col), 0, 255).astype(np.uint8)
        img[y0:y0 + h, x0:x0 + w, 3] = 255
    return Image.fromarray(img, "RGBA")


def cube_preview(tex, s=8):
    """a simple isometric preview of the textured box (top, front = left face, side = right face), for the review sheet only"""
    W = 14 * s
    face = {k: tex.crop((x, y, x + w, y + h)).resize((w * s, h * s), Image.NEAREST) for k, (x, y, w, h) in FACES.items()}
    out = Image.new("RGBA", (int(W * 1.8) + 8, int(W * 1.9) + 8), (0, 0, 0, 0))
    cx = out.width // 2
    hw, hh = W * 0.866 / 1.0 * 0.95, W * 0.5 * 0.95
    top_y = 4

    def put(img, a, b, c, d, e, f):
        # x_out = a*x + b*y + c, y_out = d*x + e*y + f   ->  PIL needs the inverse map
        m = np.array([[a, b, c], [d, e, f], [0, 0, 1]], float)
        inv = np.linalg.inv(m)
        t = img.transform(out.size, Image.AFFINE, tuple(inv[:2].reshape(-1)), resample=Image.NEAREST)
        out.alpha_composite(t)
    tw, th = face["top"].size
    put(face["top"], hw / tw, -hw / th, cx, hh / tw, hh / th, top_y)
    fw, fh = face["front"].size
    H = 16 * s * 0.95
    put(face["front"], hw / fw, 0, cx - hw, hh / fw, H / fh, top_y + hh)
    sw, sh = face["side"].size
    put(face["side"], hw / sw, 0, cx, -hh / sw, H / sh, top_y + 2 * hh)
    return out


# ------------------------------------------------------------------------------------------------------------ sheet
FONT_PATHS = {True: ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/segoeuib.ttf"],
              False: ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/segoeui.ttf"]}
PAGE = (246, 244, 239)
INK = (28, 28, 34)
SUB = (84, 86, 96)
SLOT = (30, 36, 48)


def font(sz, bold=True):
    for p in FONT_PATHS[bold]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def build_sheet(icons, texes):
    COLW, PADX, LABW = 176, 40, 220
    W = PADX * 2 + LABW + 6 * COLW
    TOP = 210
    ROWH = 176
    H = TOP + 5 * ROWH + 170 + 470
    im = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(im)
    d.text((PADX, 24), "SkyWynn pet eggs - DRAFT for review", font=font(50), fill=INK)
    d.text((PADX, 88), "Rows = egg type (shell colour + motif).  Columns = rarity (egg cup metal, gem, speckles, glow).",
           font=font(24, False), fill=SUB)
    d.text((PADX, 120), "Each egg at 2x on a dark slot with its rarity colour.  Below: actual 64 px + 32 px, and the 6 world textures.",
           font=font(24, False), fill=SUB)
    for j, r in enumerate(RARITIES):
        cx = PADX + LABW + j * COLW + COLW // 2
        tw = d.textlength(r, font=font(28))
        d.text((cx - tw / 2, TOP - 46), r, font=font(28), fill=tuple(int(v) for v in hx(QCOL[r]) * 0.75))
    for i, c in enumerate(CATEGORIES):
        y = TOP + i * ROWH
        d.text((PADX, y + 60), c, font=font(32), fill=INK)
        d.rounded_rectangle([PADX, y + 104, PADX + 60, y + 124], 6, fill=tuple(int(v) for v in SHELL[c][3]), outline=INK, width=2)
        for j, r in enumerate(RARITIES):
            x = PADX + LABW + j * COLW + (COLW - 148) // 2
            q = tuple(int(v) for v in hx(QCOL[r]))
            d.rounded_rectangle([x, y + 4, x + 148, y + 152], 12, fill=SLOT, outline=q, width=4)
            im.alpha_composite(icons[(c, r)].resize((128, 128), Image.NEAREST), (x + 10, y + 14))
    # actual size strip
    y0 = TOP + 5 * ROWH + 10
    d.text((PADX, y0), "Actual size (64 px, then 32 px) on a dark inventory - Common, Epic, Mythic of each type", font=font(28),
           fill=INK)
    d.rounded_rectangle([PADX, y0 + 44, W - PADX, y0 + 44 + 110], 14, fill=SLOT)
    x = PADX + 16
    for c in CATEGORIES:
        for r in RARITIES:
            ic = icons[(c, r)]
            if r in ("Common", "Epic", "Mythic"):
                im.alpha_composite(ic, (x, y0 + 54))
                im.alpha_composite(ic.resize((32, 32), Image.BOX), (x + 16, y0 + 120))
                x += 68
        x += 40
    # textures
    y1 = y0 + 175
    d.text((PADX, y1), "World / held textures (32 x 32, vanilla egg box UVs; shown at 6x and on the box)", font=font(28), fill=INK)
    for j, r in enumerate(RARITIES):
        x = PADX + j * 222
        t = texes[r]
        im.alpha_composite(t.resize((192, 192), Image.NEAREST), (x, y1 + 50))
        cube = cube_preview(t, 6)
        im.alpha_composite(cube, (x + 96 - cube.width // 2, y1 + 252))
        d.text((x, y1 + 250 + cube.height), r, font=font(24), fill=INK)
    return im.convert("RGB")


# ------------------------------------------------------------------------------------------------------------ main
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()
    icons, texes, files = {}, {}, []
    for c in CATEGORIES:
        for r in RARITIES:
            im = egg_icon(c, r)
            icons[(c, r)] = im
            p = os.path.join(a.out, ICON_REL % (c, r))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            im.save(p, optimize=True)
    for r in RARITIES:
        t = egg_texture(r)
        texes[r] = t
        p = os.path.join(a.out, TEX_REL % r)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        t.save(p, optimize=True)
    sp = os.path.join(a.out, "sheet.png")
    build_sheet(icons, texes).save(sp, optimize=True)
    for c in CATEGORIES:
        for r in RARITIES:
            rel = ICON_REL % (c, r)
            p = os.path.join(a.out, rel)
            files.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha(p), "image_size": [64, 64],
                          "item_id": "Skyy_PetEgg_%s_%s" % (c, r), "name": "%s %s Egg" % (r, c), "category": c, "rarity": r,
                          "quality_colour": QCOL[r], "what": "64x64 RGBA item icon (egg in a rarity egg cup)"})
    for r in RARITIES:
        rel = TEX_REL % r
        p = os.path.join(a.out, rel)
        files.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha(p), "image_size": [32, 32], "rarity": r,
                      "what": "32x32 RGBA texture for vanilla Items/Consumables/Food/Egg.blockymodel (by path), one per rarity",
                      "uv_layout": {k: list(v) for k, v in FACES.items()}})
    files.append({"path": "sheet.png", "bytes": os.path.getsize(sp), "sha256": sha(sp), "what": "review sheet"})
    man = {
        "item": "Pet eggs - 5 categories x 6 rarities (30 icons) + 6 world textures",
        "status": "DRAFT - waiting for Skyy's review, NOT committed, NOT wired in",
        "spec": "research/Pet-Eggs-Spec.md sections 1.1, 1.2, 8 (round A0)",
        "generator": ["tools/art/make_pet_eggs.py", "tools/art/ability_icon_core.py"],
        "deterministic": True,
        "categories": {c: {"shell": [K.hexs(v) for v in SHELL[c]]} for c in CATEGORIES},
        "rarities": {r: {"quality_colour": QCOL[r], "cup_metal": [K.hexs(v) for v in METAL[r]],
                         "gem": [K.hexs(v) for v in GEM[r]]} for r in RARITIES},
        "vanilla_model": {"path": "Items/Consumables/Food/Egg.blockymodel", "box": [14, 16, 14], "texture_size": [32, 32],
                          "uv": {"front": [0, 0], "top": [14, 0], "back/left/right": [14, 14], "bottom": [0, 16]},
                          "read_from": "Assets.zip 2026-10-16 (numbers only, no pixels used)"},
        "files": files,
    }
    mp = os.path.join(a.out, "manifest.json")
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2)
        f.write("\n")
    print("wrote %d icons, %d textures, sheet, manifest -> %s" % (len(icons), len(texes), a.out))


if __name__ == "__main__":
    main()
