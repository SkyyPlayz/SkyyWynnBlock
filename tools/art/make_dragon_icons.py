#!/usr/bin/env python3
"""make_dragon_icons - SkyWynn DRAGON art, round D4 of research/Dragon-Pet-Spec.md (sections 8 + 9). DRAFT for Skyy's review.

Writes (ORIGINAL pixels drawn from code - no vanilla file, no Dragon Nestkeeper file, no reference picture is read, copied, traced
or recoloured; the shapes below are our own box model and our own 2D egg painting):
  art/dragons/Common/Icons/ItemsGenerated/Skyy_PetIcon_Dragon<Kind>.png   6 dragon pet icons, 64 x 64 RGBA
  art/dragons/Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_<Elem>.png   4 dragon egg icons, 64 x 64 RGBA
  art/dragons/sheet.png      review sheet (all 10 at 2x on element-coloured slots + an actual-size 64 / 32 px strip)
  art/dragons/manifest.json  every file: path, bytes, sha256, item id, existing / new id, element, colours

Look:
  * DRAGONS = a chunky Hytale-style box model (like our pet icons in art/pets and the game's 3/4 model icons) of a young dragon:
    big head + snout, big glinting eyes, horns, back spikes, four stubby legs with claws, a curling tail, two raised wings.
    One model, six looks: Plain (Earth, mossy green + rock spikes + leaf tail), Tundra (Water, ice blue + glowing ice crystals),
    Fire (red + ember belly + flame tail), Storm (Thunder, indigo + gold horns + lightning stripes + bolt tail), Sky (Air,
    white-teal + feathered wings + feather tail), Void (secret; near-black violet, glowing eyes, star-specked wings, void aura).
  * EGGS = the approved pet egg look (art/pet-eggs, tools/art/make_pet_eggs.py: same egg silhouette, Legendary ornate gold egg cup
    with scrolls + milgrain, halo, rim light, sparkles) with an ELEMENT shell, dragon-scale rows and the element emblem on the front
    (flame / bolt / wind swirl / void star); the cup's gem + halo + speckles are the element colour (Style Guide section 15:
    Fire orange, Water blue, Earth green, Thunder yellow, Air white-teal; Void #b58cff = tools/skyyui.py).

Pure Python standard library (zlib PNG writer) - no numpy / Pillow needed. 4x4 supersampling, z-buffered flat-shaded boxes,
1 px dark outline, soft element glow. Deterministic: two runs = same bytes.
Run:  python tools/art/make_dragon_icons.py [--out DIR] [--only NAME ...]
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys
import zlib

sys.dont_write_bytecode = True

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(ROOT, "art", "dragons")
ICON_DIR = "Common/Icons/ItemsGenerated"
SIZE = 64
SS = 4
N = SIZE * SS


# ------------------------------------------------------------------------------------------------------------ colour helpers
def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def ramp(*cols):
    return [hx(c) for c in cols]


def rs(r, t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    f = t * (len(r) - 1)
    i = min(int(f), len(r) - 2)
    f -= i
    a, b = r[i], r[i + 1]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f)


def mix(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f)


def hash3(a, b, c):
    h = (a * 73856093) ^ (b * 19349663) ^ (c * 83492791)
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


# ------------------------------------------------------------------------------------------------------------ PNG writer
def png_bytes(w, h, rgba):
    """rgba: flat list of (r, g, b, a) ints, row-major"""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw.extend(rgba[y * w + x])
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# ------------------------------------------------------------------------------------------------------------ 3D maths
def mm(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def mv(A, v):
    return (A[0][0] * v[0] + A[0][1] * v[1] + A[0][2] * v[2], A[1][0] * v[0] + A[1][1] * v[1] + A[1][2] * v[2],
            A[2][0] * v[0] + A[2][1] * v[1] + A[2][2] * v[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def scl(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    L = math.sqrt(dot(a, a)) or 1.0
    return (a[0] / L, a[1] / L, a[2] / L)


I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def rx(d):
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return ((1, 0, 0), (0, c, -s), (0, s, c))


def ry(d):
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return ((c, 0, s), (0, 1, 0), (-s, 0, c))


def rz(d):
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def cols(x, y, z):
    return ((x[0], y[0], z[0]), (x[1], y[1], z[1]), (x[2], y[2], z[2]))


class Frame:
    """a local frame of the box model: world = o + R . p (units = texels / model pixels)"""

    def __init__(self, model, o=(0.0, 0.0, 0.0), R=I3):
        self.m, self.o, self.R = model, o, R

    def child(self, p, R=I3):
        return Frame(self.m, self.pt(p), mm(self.R, R))

    def pt(self, p):
        return add(self.o, mv(self.R, p))

    def box(self, part, c, size, R=I3):
        self.m.boxes.append((part, self.pt(c), mm(self.R, R), size))

    def beam(self, part, p0, p1, w, d=None):
        d = w if d is None else d
        ax = sub(p1, p0)
        L = math.sqrt(dot(ax, ax))
        yv = scl(ax, 1.0 / L)
        ref = (0.0, 0.0, 1.0) if abs(yv[2]) < 0.9 else (1.0, 0.0, 0.0)
        xv = norm(cross(yv, ref))
        zv = cross(xv, yv)
        self.box(part, scl(add(p0, p1), 0.5), (w, L, d), cols(xv, yv, zv))

    def tri(self, part, pts):
        """a double-sided flat polygon (wing membranes, fins); uv = its local x, y"""
        self.m.polys.append((part, [self.pt(p) for p in pts], [(p[0], p[1]) for p in pts]))


class Model:
    def __init__(self):
        self.boxes, self.polys = [], []


# ------------------------------------------------------------------------------------------------------------ element looks
#  every ramp = dark -> light; shadows lean violet / cool, lights lean warm (the pet + egg paint rules)
ELEMENTS = {
    "Earth": dict(
        kind="DragonPlain", name="Plain Dragon", elem="Earth", accent="#7ed957",
        scale=ramp("#1a220e", "#2e3c16", "#47591f", "#64792c", "#88a03e", "#b8cc6e"),
        belly=ramp("#3e2c14", "#644622", "#8e6a36", "#b49050", "#d4b676", "#eedcac"),
        bone=ramp("#2c241c", "#4a3e30", "#70604a", "#988668", "#bcae8e", "#e2d8bc"),
        mem=ramp("#2a1e0e", "#46341a", "#665028", "#86703a", "#a69050", "#c6b276"),
        spike=ramp("#262422", "#3e3a34", "#5a544a", "#7a7262", "#9c947e", "#c2baa0"),
        glow=ramp("#2c6a1c", "#46962a", "#64ba3a", "#7ed957", "#b0f08a", "#e2ffc8"),
        eye=ramp("#6a4006", "#a8700e", "#e0a420", "#ffd257", "#ffe896", "#fff8d8"),
        outline="#0e1208", aura=None),
    "Water": dict(
        kind="DragonTundra", name="Tundra Dragon", elem="Water", accent="#4aa8ff",
        scale=ramp("#0e1c34", "#1a3660", "#2c5a92", "#4a86c0", "#80b6e2", "#c8e6fa"),
        belly=ramp("#2e3c4e", "#56687e", "#8498ae", "#b0c4d6", "#d4e4f0", "#f0f8ff"),
        bone=ramp("#38485e", "#5c7088", "#8aa0b8", "#b6cadc", "#dceaf4", "#f6fbff"),
        mem=ramp("#0a1434", "#142c64", "#204c98", "#346ec2", "#5c98e0", "#9cc6f4"),
        spike=ramp("#0c3c58", "#16648a", "#2696bc", "#4cc8e4", "#8ff0ff", "#e0ffff"),
        glow=ramp("#0c3c58", "#16648a", "#2696bc", "#4cc8e4", "#8ff0ff", "#e0ffff"),
        eye=ramp("#0a3c5e", "#145e8a", "#2a90c4", "#56c4f0", "#a6ecff", "#e8fcff"),
        outline="#060c1c", aura=None),
    "Fire": dict(
        kind="DragonFire", name="Fire Dragon", elem="Fire", accent="#ff8a2a",
        scale=ramp("#2a0808", "#541210", "#862016", "#b8341c", "#e0602a", "#f89a4e"),
        belly=ramp("#562606", "#8a440e", "#c06e18", "#e89a2c", "#fac456", "#ffeca4"),
        bone=ramp("#141016", "#241e28", "#3a323c", "#544a54", "#74686e", "#9a8c8c"),
        mem=ramp("#2a0606", "#521010", "#7e1c12", "#a83218", "#d05422", "#ee8a40"),
        spike=ramp("#141016", "#241e28", "#3a323c", "#544a54", "#74686e", "#9a8c8c"),
        glow=ramp("#a0280a", "#d8500e", "#ff8a2a", "#ffb84a", "#ffe08a", "#fff6d0"),
        eye=ramp("#7a3a04", "#b8640a", "#f0a018", "#ffd64d", "#fff09a", "#fffbe0"),
        outline="#140404", aura=None),
    "Thunder": dict(
        kind="DragonStorm", name="Storm Dragon", elem="Thunder", accent="#ffd64d",
        scale=ramp("#100a26", "#1e1646", "#32266c", "#4a3a94", "#6a5aba", "#9c8ede"),
        belly=ramp("#262040", "#423a64", "#64598a", "#8a80ae", "#b2aace", "#dcd6ee"),
        bone=ramp("#3a2a08", "#6a4e12", "#a07a22", "#d0a834", "#f0d060", "#fff2b0"),
        mem=ramp("#0c0820", "#18123c", "#28205c", "#3a3080", "#5246a2", "#7466c4"),
        spike=ramp("#3a2a08", "#6a4e12", "#a07a22", "#d0a834", "#f0d060", "#fff2b0"),
        glow=ramp("#8a6406", "#c09010", "#f0c02a", "#ffd64d", "#fff08a", "#fffbe0"),
        eye=ramp("#8a6406", "#c09010", "#f0c02a", "#ffd64d", "#fff08a", "#fffbe0"),
        outline="#07041a", aura=None),
    "Air": dict(
        kind="DragonSky", name="Sky Dragon", elem="Air", accent="#bdf5ea",
        scale=ramp("#1a3a40", "#2c5a60", "#468888", "#6cb2ae", "#a2dcd4", "#e2faf4"),
        belly=ramp("#4e6066", "#7a9096", "#a6bcc0", "#cadcdc", "#e8f4f2", "#fafffe"),
        bone=ramp("#3a4452", "#5e6a7a", "#8692a2", "#aeb8c6", "#d2dae4", "#f0f4f8"),
        mem=ramp("#3a4e6a", "#56709a", "#7c98c0", "#a4bede", "#cadcf0", "#eef6fe"),
        spike=ramp("#3a4452", "#5e6a7a", "#8692a2", "#aeb8c6", "#d2dae4", "#f0f4f8"),
        glow=ramp("#2a8a80", "#46b0a4", "#74d2c4", "#a6ece0", "#d4fbf2", "#f6fffc"),
        eye=ramp("#0e5a58", "#168482", "#22aca8", "#4ad2cc", "#9cf0ea", "#e4fffc"),
        outline="#0a1a1e", aura=None),
    "Void": dict(
        kind="DragonVoid", name="Void Dragon", elem="Void", accent="#b58cff",
        scale=ramp("#120a1e", "#22143a", "#342256", "#4a3276", "#664a9e", "#8a6cc4"),
        belly=ramp("#2a1648", "#422470", "#5e3896", "#7e52bc", "#a07ade", "#c8acf4"),
        bone=ramp("#08060c", "#141018", "#221c28", "#342a3c", "#4a3e56", "#685a78"),
        mem=ramp("#06040c", "#100a1c", "#1c122e", "#2a1c44", "#3c2a5e", "#56407e"),
        spike=ramp("#4a1e7a", "#6a30a8", "#8c4ed4", "#b58cff", "#d8c0ff", "#f4ecff"),
        glow=ramp("#4a1e7a", "#6a30a8", "#8c4ed4", "#b58cff", "#d8c0ff", "#f4ecff"),
        eye=ramp("#7a1e7a", "#a83aa8", "#d860d8", "#f09aff", "#fcd0ff", "#fff4ff"),
        outline="#040208", aura="#b58cff"),
}
ORDER = ["Earth", "Water", "Fire", "Thunder", "Air", "Void"]
FIXED = {"pupil": hx("#120a10"), "white": hx("#fbf6ea"), "dark": hx("#1a1418")}
EMISSIVE = ("glow", "eye", "spike_glow")


# ------------------------------------------------------------------------------------------------------------ the dragon model
def dragon(E):
    """one young dragon (texel units; feet on y = 0, head toward -x, its right side = +z faces the camera)"""
    el = E["elem"]
    m = Model()
    root = Frame(m)
    body = root.child((0.0, 9.6, 0.0), rz(-7))
    body.box("scale", (0, 0, 0), (14, 8.6, 9))
    body.box("belly", (-1.0, -4.35, 0), (11, 1.0, 7))
    body.box("belly", (-7.05, -0.8, 0), (1.0, 6.2, 6.6))
    # back spikes / ridge
    spike_part = "spike_glow" if el in ("Water", "Void") else "spike"
    for k, x in enumerate((-4.0, -0.8, 2.4, 5.4)):
        h = (2.4, 2.8, 2.4, 1.9)[k] * (1.35 if el in ("Water", "Void") else 1.0)
        body.box(spike_part, (x, 4.3 + h / 2, 0), (1.8, h, 1.4), rz(-22))
    if el == "Earth":                                   # moss + small rocks on the back
        for (x, z, w) in ((-2.4, 2.2, 3.0), (3.6, -1.8, 2.6), (1.0, 3.4, 2.0)):
            body.box("glow", (x, 4.45, z), (w, 0.5, 1.8))
    if el == "Thunder":                                 # lightning stripes on both flanks
        for s in (1, -1):
            for (a, b) in (((-3.5, 2.5), (-1.5, -0.5)), ((-1.5, -0.5), (0.5, 1.5)), ((0.5, 1.5), (3.0, -2.0))):
                body.beam("glow", (a[0], a[1], s * 4.55), (b[0], b[1], s * 4.55), 0.9, 0.3)
    if el == "Void":                                    # star specks on the flanks
        for (x, y) in ((-3.0, 1.8), (1.5, -1.0), (4.6, 2.2), (-0.5, 3.0)):
            body.box("glow", (x, y, 4.55), (0.7, 0.7, 0.2))
    # legs
    for s in (1, -1):
        leg = body.child((-4.2, -3.4, s * 3.7), rz(8))
        leg.box("scale", (0, -2.2, 0), (3.2, 5.4, 3.0))
        root.box("scale", (-5.4, 0.8, s * 3.7), (4.6, 1.6, 3.6))
        for d in (-1.1, 0.0, 1.1):
            root.box("bone", (-7.95, 0.55, s * 3.7 + d), (0.9, 0.9, 0.7))
        body.box("scale", (4.4, -1.6, s * 4.0), (6.0, 6.0, 2.6))
        root.box("scale", (5.6, 2.4, s * 3.9), (3.0, 3.8, 3.0))
        root.box("scale", (4.6, 0.8, s * 3.9), (5.0, 1.6, 3.6))
        for d in (-1.1, 0.0, 1.1):
            root.box("bone", (1.85, 0.55, s * 3.9 + d), (0.9, 0.9, 0.7))
    # tail (a chain of shrinking boxes curling toward the camera)
    tail = [((7.0, 9.6, 0.0), 4.6), ((11.0, 8.4, 1.0), 3.8), ((14.6, 8.8, 2.8), 3.0), ((17.2, 10.8, 4.4), 2.3),
            ((18.4, 13.6, 5.6), 1.7)]
    for (p0, w0), (p1, w1) in zip(tail[:-1], tail[1:]):
        root.beam("scale", p0, p1, w0, w0)
    for k, ((p0, w0), (p1, w1)) in enumerate(zip(tail[:-1], tail[1:])):    # small tail ridge spikes
        mid = scl(add(p0, p1), 0.5)
        root.box(spike_part if k < 3 else spike_part, add(mid, (0, w0 / 2 + 0.5, 0)), (1.0, 1.2, 0.8), rz(-30))
    tip = Frame(m, (18.5, 14.0, 5.8), mm(ry(-35), rz(62)))
    tail_tip(tip, el)
    # neck + head
    neck = body.child((-6.2, 3.0, 0), rz(32))
    neck.box("scale", (0, 3.4, 0), (5.0, 8.0, 5.0))
    neck.box("belly", (-2.65, 3.0, 0), (0.6, 7.0, 3.6))
    for k in range(3):
        neck.box(spike_part, (2.75, 1.8 + k * 2.4, 0), (1.3, 1.6, 1.0), rz(-35))
    head = neck.child((0, 7.6, 0), rz(-27))
    head.box("scale", (-1.6, 1.6, 0), (8.0, 6.0, 7.0))
    head.box("scale", (-7.3, 0.6, 0), (4.4, 4.0, 5.4))
    head.box("belly", (-5.9, -2.0, 0), (7.0, 1.4, 4.8))
    head.box("scaled", (-1.6, 4.85, 0), (6.0, 0.5, 5.0))
    for s in (1, -1):
        head.box("dark", (-9.35, 1.9, s * 1.3), (0.5, 0.8, 0.9))
        head.box("white", (-8.4, -1.05, s * 1.7), (0.6, 0.9, 0.6))
        head.box("eye", (-3.0, 2.1, s * 3.55), (3.2, 3.2, 0.3))
        head.box("pupil", (-3.6, 1.9, s * 3.75), (1.3, 2.7, 0.2))
        head.box("white", (-2.2, 3.1, s * 3.86), (0.9, 0.9, 0.1))
        head.box("scaled", (-3.0, 4.15, s * 3.15), (3.8, 1.0, 1.4))
        horns(head, el, s)
    # wings (raised, behind the shoulders, tilted outward)
    for s in (1, -1):
        wing = body.child((-2.4, 4.4, s * 3.6), mm(mm(rx(s * 22), rz(22)), ((1.1, 0, 0), (0, 1.1, 0), (0, 0, 1.0))))
        wing_parts(wing, el)
    return m


def horns(head, el, s):
    z = s * 2.4
    if el == "Earth":            # short curved bone horns + a small nose horn
        head.beam("bone", (0.2, 4.0, z), (2.6, 6.2, z * 1.12), 1.7)
        head.beam("bone", (2.6, 6.2, z * 1.12), (4.6, 6.0, z * 1.2), 1.2)
        if s == 1:
            head.beam("bone", (-8.0, 2.6, 0), (-8.6, 4.0, 0), 1.0)
    elif el == "Water":          # long straight ice horns swept back + frost cheek fins
        head.beam("bone", (0.4, 4.0, z), (5.2, 7.4, z * 1.15), 1.6)
        head.beam("spike_glow", (1.0, 0.6, s * 3.6), (3.6, 1.6, s * 4.6), 1.0, 0.4)
    elif el == "Fire":           # dark ram-like horns curving back and down
        head.beam("bone", (0.2, 4.0, z), (3.0, 6.4, z * 1.1), 1.9)
        head.beam("bone", (3.0, 6.4, z * 1.1), (5.4, 5.2, z * 1.2), 1.4)
        head.beam("bone", (5.4, 5.2, z * 1.2), (5.6, 3.6, z * 1.25), 1.0)
    elif el == "Thunder":        # jagged gold horns (zig-zag)
        head.beam("bone", (0.2, 4.0, z), (1.6, 6.6, z * 1.1), 1.6)
        head.beam("bone", (1.6, 6.6, z * 1.1), (3.4, 6.4, z * 1.15), 1.2)
        head.beam("bone", (3.4, 6.4, z * 1.15), (4.6, 8.6, z * 1.2), 0.9)
    elif el == "Air":            # long swept-back silver horns + feather cheek tufts
        head.beam("bone", (0.4, 4.0, z), (6.2, 6.4, z * 1.1), 1.4)
        head.beam("glow", (1.2, 1.0, s * 3.6), (3.8, 2.6, s * 4.2), 1.2, 0.4)
        head.beam("glow", (1.2, 0.0, s * 3.6), (3.6, 0.6, s * 4.3), 1.0, 0.4)
    else:                        # Void: tall obsidian horns with glowing tips
        head.beam("bone", (0.2, 4.0, z), (2.8, 8.0, z * 1.1), 1.7)
        head.beam("spike_glow", (2.8, 8.0, z * 1.1), (3.6, 9.6, z * 1.12), 1.0)


def wing_parts(w, el):
    sh, el1, wr = (0.0, 0.0, 0.0), (2.8, 6.6, 0.0), (7.6, 11.6, 0.0)
    tips = [(15.8, 7.0, 0.0), (14.2, 3.4, 0.0), (10.4, 1.4, 0.0)]
    scal = [(12.4, 5.0, 0.0), (11.0, 2.8, 0.0), (6.0, 1.2, 0.0)]
    part = "mem"
    w.tri(part, [sh, el1, wr])
    w.tri(part, [sh, wr, tips[0]])
    w.tri(part, [sh, tips[0], scal[0]])
    w.tri(part, [sh, scal[0], tips[1]])
    w.tri(part, [sh, tips[1], scal[1]])
    w.tri(part, [sh, scal[1], tips[2]])
    w.tri(part, [sh, tips[2], scal[2]])
    bone = "spike" if el in ("Thunder",) else "scale"
    w.beam(bone, sh, el1, 1.6, 1.2)
    w.beam(bone, el1, wr, 1.3, 1.0)
    w.beam("bone", wr, add(wr, (0.4, 1.8, 0)), 0.8, 0.7)
    for t in tips:
        w.beam(bone, wr, t, 0.7, 0.5)
    if el == "Void":
        for (x, y) in ((7.0, 5.0), (10.6, 3.4), (4.6, 2.2), (9.0, 7.6), (12.4, 5.6)):
            w.box("glow", (x, y, 0.35), (0.6, 0.6, 0.15))
    if el == "Water":
        for (x, y) in ((8.0, 4.4), (5.2, 2.0)):
            w.box("spike_glow", (x, y, 0.35), (0.6, 0.6, 0.15))


def tail_tip(f, el):
    if el == "Earth":            # a leaf spade
        f.box("glow", (2.2, 0.0, 0), (4.6, 2.8, 0.7))
        f.box("glow", (4.6, 0.0, 0), (1.8, 1.6, 0.7))
        f.box("scaled", (2.2, 0.0, 0.4), (4.4, 0.4, 0.3))
    elif el == "Water":          # an ice crystal cluster
        f.beam("spike_glow", (0, 0, 0), (2.2, 3.0, 0.4), 1.4)
        f.beam("spike_glow", (0, 0, 0), (3.0, 0.8, -0.6), 1.1)
        f.beam("spike_glow", (0, 0, 0), (1.0, 2.0, 1.6), 0.9)
    elif el == "Fire":           # a flame
        f.box("glow", (0.6, 0.6, 0), (2.4, 2.2, 2.4))
        f.box("glow", (1.0, 2.4, 0), (1.6, 2.0, 1.6))
        f.box("eye", (1.2, 3.9, 0), (1.0, 1.4, 1.0))
        f.box("eye", (0.8, 1.0, 1.25), (1.2, 1.2, 0.2))
    elif el == "Thunder":        # a lightning bolt fin
        f.beam("glow", (0, 0, 0), (1.6, 2.4, 0), 1.0, 0.6)
        f.beam("glow", (1.6, 2.4, 0), (0.4, 2.9, 0), 0.9, 0.6)
        f.beam("glow", (0.4, 2.9, 0), (2.2, 5.4, 0), 0.8, 0.6)
    elif el == "Air":            # a feather fan
        for a in (-35, 0, 35):
            c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
            f.beam("glow", (0, 0, 0), (3.6 * c, 3.6 * s_ + 0.6, 0.0), 1.3, 0.4)
    else:                        # Void: a floating void shard
        f.beam("spike_glow", (0.4, 0.0, 0), (2.4, 2.6, 0), 1.4)
        f.box("spike_glow", (3.4, 3.8, 0), (0.8, 0.8, 0.8), rz(45))


# ------------------------------------------------------------------------------------------------------------ the renderer
YAW, PITCH = 31.0, 24.0
LIGHT = norm((-0.45, 0.78, 0.55))     # camera space: from the top-left, toward the viewer


def cam(p):
    a, b = math.radians(YAW), math.radians(PITCH)
    x = p[0] * math.cos(a) + p[2] * math.sin(a)
    z = -p[0] * math.sin(a) + p[2] * math.cos(a)
    y = p[1]
    return (x, y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b))


def faces_of(model):
    out = []
    for (part, c, R, size) in model.boxes:
        ax = [(R[0][i], R[1][i], R[2][i]) for i in range(3)]
        for a in range(3):
            b, cc = [i for i in range(3) if i != a]
            for sg in (1, -1):
                def corner(db, dc):
                    p = add(c, scl(ax[a], sg * size[a] / 2.0))
                    p = add(p, scl(ax[b], db * size[b] / 2.0))
                    return add(p, scl(ax[cc], dc * size[cc] / 2.0))
                vs = [corner(-1, -1), corner(1, -1), corner(1, 1), corner(-1, 1)]
                uv = [(0, 0), (size[b], 0), (size[b], size[cc]), (0, size[cc])]
                out.append((part, vs, uv, scl(norm(ax[a]), sg), a))
    for (part, vs, uv) in model.polys:
        out.append((part, vs, uv, None, 3))
    return out


def shade(E, part, lam, u, v, axis, key):
    """colour of one sample: the part's ramp at a light-driven t + a texel pattern"""
    if part in FIXED:
        base = FIXED[part]
        return mix(scl(base, 0.72), base, max(0.0, min(1.0, 0.4 + lam)))
    iu, iv = int(math.floor(u)), int(math.floor(v))
    n = hash3(iu, iv, key) - 0.5
    if part in EMISSIVE:
        rmp = E["eye" if part == "eye" else ("spike" if part == "spike_glow" else "glow")]
        return rs(rmp, 0.62 + 0.30 * lam + 0.10 * n)
    rmp = E["scale" if part == "scaled" else part]
    t = 0.30 + 0.62 * lam + 0.045 * n
    if part == "scaled":
        t -= 0.16
    if part == "scale":
        t += -0.07 if (iv + (iu // 2)) % 3 == 0 else 0.02
    elif part == "belly":
        t += 0.06 if iv % 2 == 0 else -0.04
    elif part == "mem":
        t = 0.16 + 0.48 * lam + 0.04 * n + 0.035 * ((iu + iv) % 3) - 0.012 * max(0.0, 6 - v)
        if E["elem"] == "Air":
            t += 0.10 if (iu + 2 * iv) % 4 == 0 else 0.0       # feather barbs
    return rs(rmp, t)


def render_dragon(E, fit=59.0):
    model = dragon(E)
    faces = faces_of(model)
    allv = [cam(p) for f in faces for p in f[1]]
    x0, x1 = min(p[0] for p in allv), max(p[0] for p in allv)
    y0, y1 = min(p[1] for p in allv), max(p[1] for p in allv)
    S = fit / max(x1 - x0, y1 - y0)
    cx = SIZE / 2.0 - (x0 + x1) / 2.0 * S
    cy = SIZE / 2.0 + (y0 + y1) / 2.0 * S + (fit - (y1 - y0) * S) * 0.0
    depth = [-1e9] * (N * N)
    colr = [None] * (N * N)
    emis = [False] * (N * N)
    for fi, (part, vs, uv, nrm, axis) in enumerate(faces):
        cv = [cam(p) for p in vs]
        if nrm is None:
            nn = norm(cross(sub(cv[1], cv[0]), sub(cv[2], cv[0])))
            if nn[2] < 0:
                nn = scl(nn, -1)
        else:
            nn = cam(nrm)
            if nn[2] <= 1e-4:
                continue
        if abs(nn[2]) < 1e-4:
            continue
        lam = max(0.0, dot(nn, LIGHT))
        sp = [((cx + p[0] * S) * SS, (cy - p[1] * S) * SS) for p in cv]
        # affine uv from the first three verts
        (ax_, ay_), (bx_, by_), (qx_, qy_) = sp[0], sp[1], sp[2]
        e1, e2 = (bx_ - ax_, by_ - ay_), (qx_ - ax_, qy_ - ay_)
        det = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(det) < 1e-9:
            continue
        area = 0.0
        for i in range(len(sp)):
            j = (i + 1) % len(sp)
            area += sp[i][0] * sp[j][1] - sp[j][0] * sp[i][1]
        sgn = 1.0 if area > 0 else -1.0
        bx0 = max(0, int(math.floor(min(p[0] for p in sp))))
        bx1 = min(N - 1, int(math.ceil(max(p[0] for p in sp))))
        by0 = max(0, int(math.floor(min(p[1] for p in sp))))
        by1 = min(N - 1, int(math.ceil(max(p[1] for p in sp))))
        edges = [(sp[i], sp[(i + 1) % len(sp)]) for i in range(len(sp))]
        p0 = cv[0]
        key = fi * 7 + 3
        for py in range(by0, by1 + 1):
            fy = py + 0.5
            for px in range(bx0, bx1 + 1):
                fx = px + 0.5
                ok = True
                for (a_, b_) in edges:
                    if ((b_[0] - a_[0]) * (fy - a_[1]) - (b_[1] - a_[1]) * (fx - a_[0])) * sgn < 0:
                        ok = False
                        break
                if not ok:
                    continue
                X = (fx / SS - cx) / S
                Yc = (cy - fy / SS) / S
                z = p0[2] - (nn[0] * (X - p0[0]) + nn[1] * (Yc - p0[1])) / nn[2]
                idx = py * N + px
                if z <= depth[idx]:
                    continue
                dx, dy = fx - ax_, fy - ay_
                s_ = (dx * e2[1] - dy * e2[0]) / det
                t_ = (e1[0] * dy - e1[1] * dx) / det
                u = uv[0][0] + s_ * (uv[1][0] - uv[0][0]) + t_ * (uv[2][0] - uv[0][0])
                v = uv[0][1] + s_ * (uv[1][1] - uv[0][1]) + t_ * (uv[2][1] - uv[0][1])
                depth[idx] = z
                colr[idx] = shade(E, part, lam, u, v, axis, key)
                emis[idx] = part in EMISSIVE
    # contact lines: a sample next to a clearly nearer surface gets darker (reads the box edges at 64 px)
    out = list(colr)
    thr = 1.1 / 1.0
    for py in range(N):
        for px in range(N):
            idx = py * N + px
            if colr[idx] is None or emis[idx]:
                continue
            d = depth[idx]
            for (ox, oy) in ((3, 0), (-3, 0), (0, 3), (0, -3)):
                qx, qy = px + ox, py + oy
                if 0 <= qx < N and 0 <= qy < N:
                    j = qy * N + qx
                    if colr[j] is not None and depth[j] > d + thr:
                        out[idx] = scl(colr[idx], 0.74)
                        break
    return finish(out, emis, E["outline"], E["accent"], E["aura"])


def blur64(a, r):
    k = [math.exp(-(i / r) ** 2) for i in range(-int(r * 2.5), int(r * 2.5) + 1)]
    sk = sum(k)
    k = [x / sk for x in k]
    h = len(k) // 2
    tmp = [0.0] * (SIZE * SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            s = 0.0
            for i, w in enumerate(k):
                xx = x + i - h
                if 0 <= xx < SIZE:
                    s += a[y * SIZE + xx] * w
            tmp[y * SIZE + x] = s
    out = [0.0] * (SIZE * SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            s = 0.0
            for i, w in enumerate(k):
                yy = y + i - h
                if 0 <= yy < SIZE:
                    s += tmp[yy * SIZE + x] * w
            out[y * SIZE + x] = s
    return out


def finish(colr, emis, outline, accent, aura, halo=None, front=None):
    """SS samples -> 64 px: hard-alpha body (>= half covered), 1 px dark outline, soft glow behind (partial alpha)"""
    pix = [None] * (SIZE * SIZE)
    em = [0.0] * (SIZE * SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            r = g = b = 0.0
            c = e = 0
            for sy in range(SS):
                row = (y * SS + sy) * N + x * SS
                for sx in range(SS):
                    v = colr[row + sx]
                    if v is not None:
                        r += v[0]
                        g += v[1]
                        b += v[2]
                        c += 1
                        if emis[row + sx]:
                            e += 1
            if c * 2 >= SS * SS:
                pix[y * SIZE + x] = (r / c, g / c, b / c)
            em[y * SIZE + x] = e / float(SS * SS)
    solid = [p is not None for p in pix]
    ol = [False] * (SIZE * SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            if solid[y * SIZE + x]:
                continue
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    xx, yy = x + ox, y + oy
                    if 0 <= xx < SIZE and 0 <= yy < SIZE and solid[yy * SIZE + xx]:
                        ol[y * SIZE + x] = True
    glow_a = blur64(em, 2.2)
    glow_a = [min(1.0, g * 2.4) for g in glow_a]
    if aura:
        au = blur64([1.0 if s else 0.0 for s in solid], 2.6)
        glow_a = [max(g, min(1.0, a * 0.95)) for g, a in zip(glow_a, au)]
    if halo is not None:
        glow_a = [max(g, h) for g, h in zip(glow_a, halo)]
    gcol = hx(aura or accent)
    olc = hx(outline)
    rgba = []
    for i in range(SIZE * SIZE):
        if solid[i]:
            p = pix[i]
            if front is not None and front[i] is not None:
                fc, fa = front[i]
                p = mix(p, fc, fa)
            c = tuple(max(0, min(255, int(round(v)))) for v in p)
            if min(c) >= 252:
                c = (250, 248, 240)
            if max(c) <= 4:
                c = (10, 8, 16)
            rgba.append(c + (255,))
        elif ol[i]:
            rgba.append(olc + (255,))
        else:
            a = int(round(min(0.85, glow_a[i] * 0.85) * 255))
            if front is not None and front[i] is not None and front[i][1] >= 0.5:
                fc = tuple(max(0, min(255, int(round(v)))) for v in front[i][0])
                rgba.append(fc + (255,))
            elif a >= 8:
                rgba.append(gcol + (a,))
            else:
                rgba.append((0, 0, 0, 0))
    return rgba


# ------------------------------------------------------------------------------------------------------------ dragon eggs (2D)
#  the egg geometry, cup and Legendary rarity look follow tools/art/make_pet_eggs.py (our approved pet egg art)
ECX, ECY, ERX, ERY = 32.0, 28.5, 15.0, 21.0
RIM_Y = 41.0
ELIGHT = norm((-0.42, -0.80, 0.62))
GOLD = ramp("#4a2806", "#7e4c0e", "#b8801e", "#e6b03a", "#f8d670", "#fff4c8")
EGGS = {
    "Fire": dict(id="Skyy_PetEgg_Dragon_Fire", kind="DragonFire", name="Fire Dragon Egg", status="existing",
                 shell=ramp("#2e0a06", "#5a1608", "#8e2a0e", "#c44a16", "#e8782a", "#fcac50", "#fde0a0"),
                 emb=ramp("#7a2a04", "#c0500a", "#ff8a2a", "#ffb84a", "#ffe08a", "#fff6d0"), accent="#ff8a2a",
                 outline="#160404"),
    "Thunder": dict(id="Skyy_PetEgg_Dragon_Thunder", kind="DragonStorm", name="Storm Dragon Egg", status="existing",
                    shell=ramp("#120c2c", "#221a4e", "#362e76", "#50469c", "#7266c0", "#a296de", "#d6d0f4"),
                    emb=ramp("#7a5404", "#b88a0e", "#f0c02a", "#ffd64d", "#fff08a", "#fffbe0"), accent="#ffd64d",
                    outline="#07041a"),
    "Air": dict(id="Skyy_PetEgg_Dragon_Air", kind="DragonSky", name="Sky Dragon Egg", status="existing",
                shell=ramp("#123036", "#1e4a50", "#2e7272", "#469a96", "#74c4bc", "#a8e6dc", "#e2fbf6"),
                emb=ramp("#1e6c66", "#2e9a90", "#5ac8ba", "#a6ece0", "#dafcf4", "#ffffff"), accent="#bdf5ea",
                outline="#0a1a1e"),
    "Void": dict(id="Skyy_PetEgg_Dragon_Void", kind="DragonVoid", name="Void Dragon Egg", status="new",
                 shell=ramp("#0a0612", "#160c24", "#241638", "#362252", "#4e3274", "#6e4c9c", "#a088cc"),
                 emb=ramp("#4a1e7a", "#6a30a8", "#8c4ed4", "#b58cff", "#d8c0ff", "#f4ecff"), accent="#b58cff",
                 outline="#040208"),
}
EGG_ORDER = ["Fire", "Thunder", "Air", "Void"]


def egg_in(x, y, rx=ERX, ry=ERY):
    yn = (y - ECY) / ry
    w = rx * (1.0 + 0.17 * max(-1.2, min(1.2, yn)))
    return ((x - ECX) / w) ** 2 + yn ** 2 <= 1.0


def egg_q(x, y, rx=ERX, ry=ERY):
    yn = (y - ECY) / ry
    w = rx * (1.0 + 0.17 * max(-1.2, min(1.2, yn)))
    return math.sqrt(((x - ECX) / w) ** 2 + yn ** 2), (x - ECX) / w, yn


def pip(x, y, pts):
    ins = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def seg_d(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
    return math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)


def stroke(pts, w):
    def f(x, y):
        return any(seg_d(x, y, a, b) <= w / 2 for a, b in zip(pts[:-1], pts[1:]))
    return f


def bevel(fn, x, y, d=0.7):
    """cheap 2D bevel: + where the upper-left neighbour is outside (lit edge), - where the lower-right one is"""
    t = 0.0
    if not fn(x - d, y - d):
        t += 0.16
    if not fn(x + d, y + d):
        t -= 0.22
    return t


def emblem_shape(el):
    cx, cy = 32.0, 24.5
    if el == "Fire":
        outer = [(32.6, 13.0), (35.6, 17.6), (38.2, 21.6), (38.6, 26.0), (36.8, 30.2), (33.4, 32.6), (30.0, 32.4),
                 (27.0, 30.0), (25.8, 26.0), (26.8, 21.8), (28.8, 19.4), (29.6, 22.6), (31.0, 18.6)]
        inner = [(32.4, 21.0), (34.6, 24.4), (35.0, 27.6), (33.6, 30.4), (31.0, 30.6), (29.2, 28.4), (29.6, 25.6),
                 (31.0, 26.6)]
        return (lambda x, y: pip(x, y, outer)), (lambda x, y: pip(x, y, inner))
    if el == "Thunder":
        bolt = [(35.6, 12.6), (27.0, 25.4), (31.4, 25.4), (28.4, 35.2), (37.8, 21.8), (33.2, 21.8), (36.8, 12.6)]
        core = [(34.4, 15.6), (29.6, 23.8), (33.0, 23.8), (31.4, 29.8)]
        return (lambda x, y: pip(x, y, bolt)), (lambda x, y: pip(x, y, core) and False)
    if el == "Air":
        sp = []
        for k in range(46):
            th = k * 0.16
            r = 0.6 + 0.95 * th
            sp.append((cx + 0.4 + r * math.cos(th + 2.6), cy + 0.4 + r * math.sin(th + 2.6) * 0.95))
        f1 = stroke(sp, 1.9)
        w1 = stroke([(20.5, 33.4), (25.0, 33.0), (29.0, 34.0)], 1.5)
        w2 = stroke([(35.0, 15.0), (39.5, 14.0), (43.0, 15.4)], 1.4)
        return (lambda x, y: f1(x, y) or w1(x, y) or w2(x, y)), (lambda x, y: False)
    # Void: a four-point star in a ring + two small stars
    st = []
    for k in range(8):
        a = math.radians(-90 + k * 45)
        r = 8.6 if k % 2 == 0 else 2.1
        st.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    def f(x, y):
        d = math.hypot(x - cx, y - cy)
        return pip(x, y, st) or (5.6 <= d <= 6.6)
    return f, (lambda x, y: math.hypot(x - cx, y - cy) <= 1.4)


def paint_egg(D, el):
    shell, emb = D["shell"], D["emb"]
    acc = hx(D["accent"])
    colr = [None] * (N * N)
    emis = [False] * (N * N)
    fill, inner = emblem_shape(el)
    # cup shapes
    def rim_curve(x):
        return RIM_Y + 1.4 * ((x - ECX) / 18.0) ** 2
    def bowl(x, y):
        return egg_in(x, y, ERX + 2.4, ERY + 2.2) and rim_curve(x) <= y <= 51.0
    def rim(x, y):
        return ((x - ECX) / 17.2) ** 2 + ((y - RIM_Y) / 2.2) ** 2 <= 1.0 and y >= RIM_Y - 0.2
    stem_p = [(ECX - 3.0, 49.5), (ECX + 3.0, 49.5), (ECX + 2.2, 55.0), (ECX - 2.2, 55.0)]
    def stem(x, y):
        return pip(x, y, stem_p)
    def foot(x, y):
        return ((x - ECX) / 10.5) ** 2 + ((y - 56.6) / 3.0) ** 2 <= 1.0
    def cup(x, y):
        return bowl(x, y) or rim(x, y) or stem(x, y) or foot(x, y)
    gcx, gcy, gs = ECX, 46.8, 3.8
    def gem(x, y):
        return abs(x - gcx) + abs(y - gcy) <= gs
    def setting(x, y):
        return abs(x - gcx) + abs(y - gcy) <= gs + 1.3
    rng_specks = [(ECX + (hash3(i, 1, 99) * 2 - 1) * 12.0, ECY - 3 + (hash3(i, 2, 99) * 2 - 1) * 14.5,
                   0.55 + hash3(i, 3, 99) * 0.5) for i in range(14)]
    for py in range(N):
        y = (py + 0.5) / SS
        for px in range(N):
            x = (px + 0.5) / SS
            idx = py * N + px
            c = None
            e = False
            if egg_in(x, y):
                q, xn, yn = egg_q(x, y)
                nz = math.sqrt(max(0.0, 1 - min(1.0, q * q)))
                lam = xn * ELIGHT[0] + yn * ELIGHT[1] + nz * ELIGHT[2]
                t = 0.10 + 0.88 * max(0.0, min(1.0, lam))
                # dragon-scale rows (U-shaped scale edges) over the shell
                row = int(math.floor((y - 6.0) / 3.4))
                off = 2.1 if row % 2 else 0.0
                col_ = int(math.floor((x - 14.0 + off) / 4.2))
                scx, scy = 14.0 - off + (col_ + 0.5) * 4.2, 6.0 + row * 3.4
                d = math.hypot((x - scx) / 2.5, (y - scy) / 2.5)
                if y > scy and 0.82 <= d <= 1.12:
                    t -= 0.17
                elif d < 0.8 and y > scy - 1.0:
                    t += 0.05 * (1 - d)
                if q > 0.86 and x > ECX + 3 and y > ECY + 4:
                    t = t * 0.4 + 0.42 * 0.6
                c = rs(shell, t)
                hl = ((x - (ECX - 5.5)) * math.cos(math.radians(25)) + (y - (ECY - 9.5)) * math.sin(math.radians(25))) ** 2 / 3.4 ** 2 \
                    + (-(x - (ECX - 5.5)) * math.sin(math.radians(25)) + (y - (ECY - 9.5)) * math.cos(math.radians(25))) ** 2 / 5.0 ** 2
                if hl <= 1.0:
                    c = mix(c, rs(shell, 0.97), 0.75)
                # rim light in the element colour
                if q > 0.84 and y < RIM_Y:
                    c = mix(c, acc, min(1.0, (q - 0.84) / 0.16) * 0.5)
                for (sx, sy, sr) in rng_specks:
                    if (x - sx) ** 2 + (y - sy) ** 2 <= sr * sr and y < RIM_Y - 1.5:
                        c = rs(emb, 0.72)
                # the emblem: a dark rim, then the shaded fill
                if fill(x, y):
                    tt = 0.55 + 0.22 * (-(x - 32.0) / 8.0 * 0.4 - (y - 24.5) / 10.0 * 0.6) + bevel(fill, x, y)
                    if inner(x, y):
                        tt += 0.3
                    c = rs(emb, tt)
                    e = True
                elif any(fill(x + ox, y + oy) for ox, oy in ((0.75, 0), (-0.75, 0), (0, 0.75), (0, -0.75))):
                    c = rs(shell, 0.04)
            if cup(x, y):
                xn = max(-1.0, min(1.0, (x - ECX) / 18.0))
                tone = -0.32 * xn + 0.18 * math.exp(-((xn + 0.45) / 0.18) ** 2)
                if rim(x, y):
                    t = 0.75 - 0.22 * xn + bevel(rim, x, y, 0.5)
                elif bowl(x, y):
                    t = 0.52 + tone + bevel(bowl, x, y)
                    if abs(y - (RIM_Y + 4.6 + ((x - ECX) / 18.0) ** 2)) < 0.55:
                        t = 0.2
                    for s in (-1, 1):                         # ornate scrolls
                        sd = math.hypot(x - (ECX + s * 10.5), y - 46.5)
                        if (1.7 < sd <= 2.6 and (x - (ECX + s * 10.5)) * s < 0.8) or sd <= 0.7:
                            t = 0.93
                elif stem(x, y):
                    t = 0.55 - 0.2 * xn * 1.6 + bevel(stem, x, y, 0.5)
                else:
                    t = 0.5 - 0.25 * xn + bevel(foot, x, y)
                c = rs(GOLD, t)
                e = False
                # the front gem in the element colour, milgrain + claws
                if setting(x, y):
                    c = rs(GOLD, 0.62 + bevel(setting, x, y, 0.5))
                for k in range(12):
                    a = math.radians(k * 30)
                    if math.hypot(x - (gcx + math.cos(a) * (gs + 1.9)), y - (gcy + math.sin(a) * (gs + 1.9))) <= 0.55:
                        c = rs(GOLD, 0.85 if k % 2 else 0.5)
                if gem(x, y):
                    c = rs(emb, 0.6 + bevel(gem, x, y, 0.6) * 1.4)
                    if abs(x - gcx) + abs(y - gcy) <= gs * 0.42:
                        c = rs(emb, 0.84)
                    e = True
                for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                    if math.hypot(x - (gcx + dx * gs * 0.62), y - (gcy + dy * gs * 0.62)) <= 0.75:
                        c = rs(GOLD, 0.8)
                if math.hypot(x - (gcx - gs * 0.35), y - (gcy - gs * 0.4)) <= 0.55:
                    c = rs(emb, 1.0)
            colr[idx] = c
            emis[idx] = e
    # halo (element colour) behind the egg + sparkles in front
    halo = [0.0] * (SIZE * SIZE)
    front = [None] * (SIZE * SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            fx, fy = x + 0.5, y + 0.5
            q, _, _ = egg_q(fx, fy)
            if q > 1.0:
                dist = (q - 1.0) * ERX * 1.1
                halo[y * SIZE + x] = 0.8 * math.exp(-(dist / 3.2) ** 2)
            for (sx, sy, r) in ((13.5, 16.0, 2.6), (51.0, 22.0, 2.0), (50.5, 44.0, 1.4)):
                if (abs(fx - sx) <= 0.6 and abs(fy - sy) <= r) or (abs(fy - sy) <= 0.6 and abs(fx - sx) <= r):
                    cc = (255, 250, 240) if abs(fx - sx) <= 0.6 and abs(fy - sy) <= 0.6 else rs(D["emb"], 0.9)
                    front[y * SIZE + x] = (cc, 1.0)
    if el == "Void":                                       # tiny stars round the void egg
        for (sx, sy) in ((10.5, 33.5), (54.5, 31.5), (17.5, 6.5)):
            front[int(sy) * SIZE + int(sx)] = (rs(D["emb"], 0.95), 1.0)
    return finish(colr, emis, D["outline"], D["accent"], None, halo=halo, front=front)


# ------------------------------------------------------------------------------------------------------------ review sheet
FONT = {
    "A": "01110100011000111111100011000110001", "B": "11110100011111010001100011000111110",
    "C": "01110100011000010000100001000101110", "D": "11110100011000110001100011000111110",
    "E": "11111100001111010000100001000011111", "F": "11111100001111010000100001000010000",
    "G": "01110100011000010111100011000101111", "H": "10001100011111110001100011000110001",
    "I": "01110001000010000100001000010001110", "J": "00111000100001000010100101001001100",
    "K": "10001100101010011000101001001010001", "L": "10000100001000010000100001000011111",
    "M": "10001110111010110101100011000110001", "N": "10001110011010110011100011000110001",
    "O": "01110100011000110001100011000101110", "P": "11110100011000111110100001000010000",
    "Q": "01110100011000110001101011001001101", "R": "11110100011000111110101001001010001",
    "S": "01111100001000001110000010000111110", "T": "11111001000010000100001000010000100",
    "U": "10001100011000110001100011000101110", "V": "10001100011000110001100010101000100",
    "W": "10001100011000110101101011101110001", "X": "10001100010101000100010101000110001",
    "Y": "10001100010101000100001000010000100", "Z": "11111000010001000100010001000011111",
    "0": "01110100011001110101110011000101110", "1": "00100011000010000100001000010001110",
    "2": "01110100010000100010001000100011111", "3": "11110000010000101110000010000111110",
    "4": "00010001100101010010111110001000010", "5": "11111100001111000001000011000101110",
    "6": "00110010001000011110100011000101110", "7": "11111000010001000100010000100001000",
    "8": "01110100011000101110100011000101110", "9": "01110100011000101111000010001001100",
    " ": "00000000000000000000000000000000000", "-": "00000000000000011111000000000000000",
    ".": "00000000000000000000000000110001100", ",": "00000000000000000000001100010001000",
    "(": "00010001000100001000010000010000010", ")": "01000001000001000010000100010001000",
    "/": "00001000010001000100010001000010000", ":": "00000011000110000000011000110000000",
    "+": "00000001000010011111001000010000000", "_": "00000000000000000000000000000011111",
    "=": "00000000001111100000111110000000000", "'": "00100001000100000000000000000000000",
    "?": "01110100010000100010001000000000100",
}


class Sheet:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [bg] * (w * h)

    def rect(self, x0, y0, x1, y1, col):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.px[y * self.w + x] = col

    def frame(self, x0, y0, x1, y1, col, t=3):
        self.rect(x0, y0, x1, y0 + t, col)
        self.rect(x0, y1 - t, x1, y1, col)
        self.rect(x0, y0, x0 + t, y1, col)
        self.rect(x1 - t, y0, x1, y1, col)

    def blit(self, icon, iw, x0, y0, k):
        ih = len(icon) // iw
        for y in range(ih * k):
            for x in range(iw * k):
                r, g, b, a = icon[(y // k) * iw + x // k]
                if a == 0:
                    continue
                X, Y = x0 + x, y0 + y
                if 0 <= X < self.w and 0 <= Y < self.h:
                    bg = self.px[Y * self.w + X]
                    f = a / 255.0
                    self.px[Y * self.w + X] = (int(round(bg[0] + (r - bg[0]) * f)), int(round(bg[1] + (g - bg[1]) * f)),
                                               int(round(bg[2] + (b - bg[2]) * f)))

    def text(self, s, x, y, k, col):
        for ch in s.upper():
            g = FONT.get(ch, FONT["?"])
            for i, bit in enumerate(g):
                if bit == "1":
                    self.rect(x + (i % 5) * k, y + (i // 5) * k, x + (i % 5) * k + k, y + (i // 5) * k + k, col)
            x += 6 * k
        return x

    def png(self):
        return png_bytes(self.w, self.h, [p + (255,) for p in self.px])


def half(icon):
    """64 -> 32 box filter (premultiplied), for the actual-size strip"""
    out = []
    for y in range(32):
        for x in range(32):
            r = g = b = a = 0.0
            for oy in (0, 1):
                for ox in (0, 1):
                    p = icon[(2 * y + oy) * 64 + 2 * x + ox]
                    f = p[3] / 255.0
                    r += p[0] * f
                    g += p[1] * f
                    b += p[2] * f
                    a += f
            if a > 0:
                out.append((int(round(r / a)), int(round(g / a)), int(round(b / a)), int(round(a / 4 * 255))))
            else:
                out.append((0, 0, 0, 0))
    return out


def build_sheet(items):
    """items: list of (label, sub, element hex, icon)"""
    PAGE, INK, SUB, SLOT = (246, 244, 239), (28, 28, 34), (84, 86, 96), (30, 36, 48)
    W = 40 + 6 * 200 + 20
    H = 820
    sh = Sheet(W, H, PAGE)
    sh.text("SKYWYNN DRAGONS - DRAFT FOR REVIEW", 40, 24, 4, INK)
    sh.text("ROUND D4: 6 DRAGON PET ICONS + 4 DRAGON EGG ICONS. ORIGINAL ART, 64 X 64, SHOWN AT 2X.", 40, 66, 2, SUB)
    sh.text("SLOT BORDER = ELEMENT COLOUR (STYLE GUIDE 15). BOTTOM: ACTUAL SIZE 64 + 32 PX.", 40, 86, 2, SUB)
    def cell(i, row, it):
        label, sub, colh, icon = it
        x0, y0 = 40 + i * 200, 120 + row * 250
        col = hx(colh)
        sh.rect(x0, y0, x0 + 148, y0 + 148, SLOT)
        sh.frame(x0, y0, x0 + 148, y0 + 148, col, 4)
        sh.blit(icon, 64, x0 + 10, y0 + 10, 2)
        sh.text(label, x0, y0 + 158, 2, INK)
        sh.text(sub, x0, y0 + 178, 1, SUB)
        sh.rect(x0, y0 + 192, x0 + 40, y0 + 200, col)
    for i, it in enumerate(items[:6]):
        cell(i, 0, it)
    for i, it in enumerate(items[6:]):
        cell(i, 1, it)
    y0 = 640
    sh.text("ACTUAL SIZE ON A DARK INVENTORY", 40, y0 - 20, 2, INK)
    sh.rect(40, y0, W - 20, y0 + 150, SLOT)
    for i, it in enumerate(items):
        x = 60 + i * 120
        sh.blit(it[3], 64, x, y0 + 14, 1)
        sh.blit(half(it[3]), 32, x + 16, y0 + 100, 1)
    return sh.png()


# ------------------------------------------------------------------------------------------------------------ main
def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", nargs="*", help="element names (Earth Water Fire Thunder Air Void) / egg_<Elem>; no sheet")
    a = ap.parse_args()
    out = a.out
    files, items = [], []
    for el in ORDER:
        E = ELEMENTS[el]
        if a.only and el not in a.only:
            continue
        iid = "Skyy_PetIcon_" + E["kind"]
        rel = "%s/%s.png" % (ICON_DIR, iid)
        icon = render_dragon(E, 56.0 if E["aura"] else 59.0)
        data = png_bytes(64, 64, icon)
        write(os.path.join(out, rel), data)
        status = "new" if E["kind"] == "DragonVoid" else "existing"
        files.append(dict(path=rel, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), what="dragon pet icon 64x64 RGBA",
                          item_id=iid, kind=E["kind"], name=E["name"], element=el, element_colour=E["accent"], id_status=status))
        items.append((E["name"].upper(), iid, E["accent"], icon))
        print("dragon", el, rel, len(data))
    for el in EGG_ORDER:
        D = EGGS[el]
        if a.only and ("egg_" + el) not in a.only:
            continue
        rel = "%s/%s.png" % (ICON_DIR, D["id"])
        icon = paint_egg(D, el)
        data = png_bytes(64, 64, icon)
        write(os.path.join(out, rel), data)
        files.append(dict(path=rel, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), what="dragon egg icon 64x64 RGBA",
                          item_id=D["id"], hatches=D["kind"], name=D["name"], element=el, element_colour=D["accent"],
                          id_status=D["status"]))
        items.append((D["name"].upper(), D["id"], D["accent"], icon))
        print("egg", el, rel, len(data))
    if a.only:
        return
    sheet = build_sheet(items)
    write(os.path.join(out, "sheet.png"), sheet)
    files.append(dict(path="sheet.png", bytes=len(sheet), sha256=hashlib.sha256(sheet).hexdigest(),
                      what="review sheet: all 10 icons at 2x + actual 64 / 32 px strip"))
    files.append(dict(path="README.md", what="hand-written notes: ids, look, wiring, UNVERIFIED, questions (not generated)"))
    man = {
        "item": "Dragons - 6 dragon pet icons + 4 dragon egg icons (round D4, research/Dragon-Pet-Spec.md sections 8 + 9)",
        "status": "DRAFT - waiting for Skyy's review, NOT committed, NOT wired in",
        "generator": ["tools/art/make_dragon_icons.py"],
        "deterministic": True,
        "original": "own pixels from code; no vanilla / Dragon Nestkeeper / reference file read, copied, traced or recoloured",
        "files": files,
    }
    write(os.path.join(out, "manifest.json"), (json.dumps(man, indent=2) + "\n").encode())
    print("sheet + manifest written to", out)


if __name__ == "__main__":
    main()
