#!/usr/bin/env python3
"""SkyWynn Light Armor - v3 helmets (cloud draft 2026-10-07).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/light-armor/make_helmets_v3.py
Writes helmets-v3.png + light-armor-sheet-v3.png next to this script. Deterministic.
The v1 / v2 scripts and PNGs are not changed: this script imports make_sheets_v2 (painter,
textures, the v2 body) and only swaps its helmet() for the v3 hard metal helms.

Skyy 2026-10-06 (docs/answered/gear.md, "LIGHT ARMOR HELMET references"): HARD METAL helms,
never a cloth hood, no masks. The v3 ladder (proposal, Skyy reviews):
  Copper     engraved Corinthian, almond eye holes, long pointed cheek guards   trim: gold inlay
  Iron       segmented sallet: flared skull, eye slit, 3-lame bevor + breathing slots   trim: brass
  Thorium    closed great helm: flat top, horizontal visor slit + cross bar, side rings + straps   trim: steel
  Cobalt     Spartan: narrow T slit that glows, dark horsehair crest   trim: steel
  Adamantite closed helm, V eye slit, spike ridge + two big horns   trim: blackened steel
  Mithril    winged helm: spectacle eye guard, big feathered wings   trim: gold
  Onyxium    crowned helm: gold crown, glowing forehead gem, hanging chains   trim: gold
Every helm sits on black leather where it meets the body (padded liner edge + neck guard).
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_sheets as ms  # noqa: E402
import make_sheets_v2 as v2  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# more headroom for crests / horns / wings: shift the whole v2 figure down 10 rows
v2.DY = 32
v2.H = 202
W, H = v2.W, v2.H
OUT = HERE

Fig, poly, line, ell, rect = v2.Fig, v2.poly, v2.line, v2.ell, v2.rect
mirror, erode, dil, ring, clip = v2.mirror, v2.erode, v2.dil, v2.ring, v2.clip
top_rim, bottom_rim = v2.top_rim, v2.bottom_rim
grain, quilt, chain, facet, metal_tex = v2.grain, v2.quilt, v2.chain, v2.facet, v2.metal_tex
rivet, buckle, feather = v2.rivet, v2.buckle, v2.feather
LEATHER, LEATHER_IN, STRAP, GOLD = v2.LEATHER, v2.LEATHER_IN, v2.STRAP, v2.GOLD
THREAD, THREAD_DK, TAN = v2.THREAD, v2.THREAD_DK, v2.TAN
TIERS = v2.TIERS
hx, ramp, ramp7, mix = ms.hx, ms.ramp, v2.ramp7, v2.mix
BG, INK = ms.BG, ms.INK
font = ms.font

BRASS = ramp7(ms.BRASS)
STEEL = TIERS[2][2]
BLACK = ramp7(ramp('#09080b', '#1f1d24', '#35323b', '#4f4b57', '#78737f'))     # blackened steel
CREST = ramp7(ramp('#05060c', '#10142a', '#1b2242', '#2a3460', '#41508a'))     # dark navy horsehair
DARK = ramp7(ramp('#030304', '#09080b', '#0f0d12', '#16131a', '#1f1b24'))      # inside an opening
GLOWB = ramp7(ramp('#1a3a9a', '#2f6ae0', '#62a4ff', '#a8d4ff', '#eef8ff'))     # Cobalt eye glow
GLOWR = ramp7(ramp('#4a0a08', '#9a1a10', '#e04a26', '#ff8a4a', '#ffd8b0'))     # Adamantite eye glow
GEM = ramp7(ramp('#3a0838', '#8a1a8a', '#d040d0', '#ff7af0', '#ffe0ff'))       # Onyxium gem
TRIM = {1: GOLD, 2: BRASS, 3: STEEL, 4: STEEL, 5: BLACK, 6: GOLD, 7: GOLD}
NAME = {1: 'engraved Corinthian', 2: 'segmented sallet', 3: 'closed great helm',
        4: 'Spartan + crest', 5: 'horned + spiked', 6: 'winged helm', 7: 'crowned helm'}
NOTE = {1: 'long cheek guards, gold inlay', 2: 'brass edges, breathing slots',
        4: 'glowing T slit, dark crest', 3: 'visor slit, side rings + straps',
        5: 'V slit, black-steel horns', 6: 'feathered wings, gold trim', 7: 'gold crown, forehead gem, chains'}


# ---------------------------------------------------------------- helpers
def hs(pts):
    """symmetric mask from the LEFT half outline (points must reach x >= 64 at the centre)"""
    m = {p for p in poly(pts) if p[0] <= 63}
    return m | mirror(m)


def both(m):
    return m | mirror(m)


def rim(m, w=2):
    return m - erode(m, w)


def inlay(f, pts, rp, w=1):
    """engraved inlay line: bright metal line with a dark groove pixel under it"""
    ln = line(pts, w)
    for (x, y) in ln:
        if (x, y + 1) not in ln:
            f.put(x, y + 1, rp[1], 'metal')
    for (x, y) in ln:
        f.put(x, y, rp[5] if (x + y) % 5 else rp[6], 'metal')


def scroll(cx, cy, r, turns=1.6, flip=False, start=0.0):
    pts = []
    for k in range(40):
        a = start + k / 39 * turns * 2 * math.pi
        rr = r * (1 - k / 46)
        x = cx + (rr * math.cos(a)) * (-1 if flip else 1)
        pts.append((x, cy + rr * math.sin(a)))
    return pts


def specular(f, m, rp, n=6):
    """a short bright streak on the upper-left of a rounded part"""
    xs = [p[0] for p in m]
    ys = [p[1] for p in m]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    cx, cy = x0 + (x1 - x0) * 0.30, y0 + (y1 - y0) * 0.22
    for k in range(n):
        q = (int(cx + k), int(cy - k * 0.5))
        if q in erode(m, 2):
            f.put(*q, rp[6], 'metal')
            f.put(q[0], q[1] + 1, rp[5], 'metal')


def opening(f, m, glow=None):
    """dark inside of an eye hole / slit; darkest under the brow; optional glow core"""
    if not m:
        return
    f.paint(m, DARK, kind='metal', base=0.25, grad=0.35, outline=False, bevel=False)
    ys = [p[1] for p in m]
    top = min(ys)
    for (x, y) in m:
        if y == top:
            f.put(x, y, DARK[0], 'metal')
    if glow:
        core = erode(m, 1) or m
        f.paint(m, glow, kind='metal', base=0.25, grad=0.15, outline=False, bevel=False)
        f.paint(core, glow, kind='metal', base=0.85, grad=0.1, outline=False, bevel=False)


def neck_leather(f, m, seed=1):
    """black leather (quilted) where the helm meets the body"""
    f.paint(m, LEATHER, tex=quilt(8, seed), grad=0.3)
    f.stitch(m, THREAD_DK, d=2, per=3, on=1)


def liner(f, shell, holes):
    """1-px padded black-leather liner edge showing inside every opening"""
    edge = (dil(holes, 1) & holes) - erode(holes, 1)
    for (x, y) in sorted(edge):
        if (x, y - 1) in shell or (x - 1, y) in shell or (x + 1, y) in shell:
            f.put(x, y, LEATHER[3] if (x + y) % 3 else LEATHER[5], 'leather')


def strap(f, m, seed=3):
    f.paint(m, LEATHER, tex=grain(seed, 0.08), base=0.45, grad=0.2)
    f.stitch(m, THREAD, d=1, per=3, on=1)


def ring_shape(cx, cy, r, w=2):
    return ell(cx - r, cy - r, cx + r, cy + r) - ell(cx - r + w, cy - r + w, cx + r - w, cy + r - w)


# ---------------------------------------------------------------- the helmets
# grid: 128 x 202, head box x 44..83, y 32..67, centre x 63.5; 'side' faces right (front at x ~86)
def helm(f, t, view):
    name, band, M = TIERS[t]
    T = TRIM[t]
    {1: copper, 2: iron, 3: thorium, 4: cobalt, 5: adamantite, 6: mithril, 7: onyxium}[t](f, M, T, view)
    wear(f, M, t)


def wear(f, M, seed):
    """small scratches + dents on the helm's metal (pixels in the tier ramp, head area only)"""
    body = set(M[2:7])
    pts = sorted(p for p, k in f.kind.items() if k == 'metal' and p[1] < 74 and f.px[p] in body)
    pset = set(pts)
    for k in range(int(len(pts) * 0.006)):
        x, y = pts[int(v2.hsh(k, seed, 31) * len(pts))]
        dx = 1 if v2.hsh(k, seed, 32) < 0.5 else -1
        seg = [(x + j * dx, y + j // 2) for j in range(3 + int(v2.hsh(k, seed, 33) * 3))]
        if all(q in pset for q in seg):
            for q in seg:
                f.put(*q, M[2], 'metal')
            f.put(seg[0][0], seg[0][1] - 1, M[6], 'metal')


# ---- Copper: engraved Corinthian ---------------------------------------------------------------
def copper(f, M, T, view):
    if view == 'side':
        neck_leather(f, poly([(52, 60), (74, 60), (78, 76), (50, 78)]), 2)
        shell = poly([(62, 25), (72, 26), (80, 30), (85, 36), (87, 42), (87, 55), (84, 58), (82, 64), (81, 72),
                      (78, 82), (74, 79), (71, 68), (68, 63), (62, 65), (52, 68), (45, 68), (42, 60), (41, 48),
                      (43, 37), (48, 30), (54, 26)])
        eye = poly([(78, 42), (88, 41), (88, 48), (81, 48)])
        mouth = poly([(84, 56), (89, 54), (89, 76), (80, 76)])
        holes = eye | mouth
        opening(f, eye & shell)
        f.metal(shell - holes, M, grad=0.4)
        liner(f, shell, eye)
        f.trim(rim(shell - holes, 2) & clip(shell, y0=58), shell - holes, T)
        inlay(f, [(86, 39), (80, 38), (74, 40), (70, 44)], T)                     # brow
        inlay(f, scroll(76, 66, 5, 1.5, start=3.6), T)                            # cheek scroll
        inlay(f, [(46, 50), (60, 52), (70, 50), (76, 46)], T)                     # temple band
        inlay(f, scroll(52, 58, 4, 1.4, flip=True, start=0.5), T)
        for x in (50, 58, 66):
            rivet(f, x, 51, T, small=True)
        specular(f, shell, M, 8)
        return
    neck_leather(f, hs([(64, 60), (54, 60), (50, 64), (48, 76), (64, 76)]), 2)
    shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 52), (41, 62), (44, 70), (47, 78),
                (50, 84), (53, 82), (56, 72), (64, 70)])
    if view == 'back':
        shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 52), (41, 62), (43, 68),
                    (46, 72), (64, 72)])
        f.metal(shell, M, grad=0.4)
        f.trim(bottom_rim(shell, 3), shell, T)
        inlay(f, [(42, 52), (52, 54), (64, 55), (76, 54), (86, 52)], T)
        for side in (0, 1):
            inlay(f, [(v2.MX(x, side), y) for x, y in scroll(50, 62, 4, 1.4, flip=bool(side), start=0.5)], T)
        f.metal(rect(62, 26, 65, 54), M, base=0.62)                              # back ridge
        specular(f, shell, M, 8)
        return
    eyes = hs([(47, 44), (52, 41), (58, 41), (61, 43), (60, 47), (54, 49), (48, 47)]) - rect(61, 0, 66, 99)
    mouth = hs([(64, 54), (61.5, 55), (60, 59), (58, 65), (56.5, 72), (55, 80), (54, 88), (64, 88)])
    holes = eyes | mouth
    opening(f, eyes)
    opening(f, mouth & clip(shell, y1=69))
    sh = shell - holes
    f.metal(sh, M, grad=0.4)
    liner(f, sh, eyes | (mouth & shell))
    f.trim(rim(sh, 2) - clip(sh, y1=60), sh, T)                                   # gold edge on the cheek guards
    for side in (0, 1):
        s = bool(side)
        mx = lambda pts: [(v2.MX(x, side), y) for x, y in pts]
        inlay(f, mx([(45, 41), (49, 38), (55, 37.5), (61, 39)]), T)              # eyebrow arch
        inlay(f, mx(scroll(50, 62, 4.5, 1.5, flip=s, start=0.3)), T)             # cheek scroll
        inlay(f, mx([(44, 52), (47, 55), (49, 57)]), T)
        inlay(f, mx([(52, 30), (48, 33), (46, 37)]), T)                          # crown leaf
    inlay(f, [(63, 28), (63, 36)], T)
    inlay(f, [(64, 28), (64, 36)], T)
    for y in (45, 49):                                                            # nose guard studs
        rivet(f, 63, y, T, small=True)
    specular(f, shell, M, 8)


# ---- Iron: segmented sallet ------------------------------------------------------------------------
def iron(f, M, T, view):
    if view == 'side':
        neck_leather(f, poly([(46, 44), (76, 44), (78, 76), (44, 76)]), 4)
        skull = poly([(63, 25), (73, 27), (81, 32), (86, 40), (88, 45), (60, 46), (40, 47), (34, 50), (38, 44),
                      (42, 36), (48, 29), (55, 26)])
        tail = [poly([(36, 47), (58, 46), (56, 55), (32, 56), (30, 52)]),
                poly([(33, 55), (56, 54), (55, 62), (29, 63), (28, 59)])]
        bevor = [poly([(70, 49), (88, 48), (90, 56), (73, 58)]), poly([(68, 57), (89, 55), (88, 64), (70, 66)]),
                 poly([(64, 64), (87, 63), (85, 72), (62, 74)])]
        for k, m in enumerate(reversed(tail)):
            f.metal(m, M, grad=0.3)
            f.trim(bottom_rim(m, 2), m, T)
        opening(f, poly([(70, 45), (89, 45), (89, 48), (70, 49)]))
        for k, m in enumerate(reversed(bevor)):
            f.metal(m, M, grad=0.3)
            f.trim(top_rim(m, 2), m, T)
        for x in (78, 81, 84):
            for y in (50, 52):
                f.put(x, y, DARK[1], 'metal')
                f.put(x, y + 1, DARK[0], 'metal')
        f.metal(skull, M, grad=0.4)
        f.trim(bottom_rim(skull, 2), skull, T)
        f.metal(line([(52, 27), (62, 24), (74, 26), (84, 34)], 2) & dil(skull, 1), M, base=0.7)   # keel
        rivet(f, 62, 42, T)
        rivet(f, 72, 59, T)
        specular(f, skull, M, 8)
        return
    if view == 'back':
        neck_leather(f, hs([(64, 64), (54, 64), (52, 74), (64, 76)]), 4)
        skull = hs([(64, 25), (55, 26), (48, 29), (43, 36), (41, 44), (38, 50), (64, 50)])
        lames = [hs([(64, 49), (40, 49), (37, 58), (64, 58)]), hs([(64, 57), (38, 57), (35, 66), (64, 66)]),
                 hs([(64, 65), (37, 65), (34, 74), (64, 74)])]
        for m in reversed(lames):
            f.metal(m, M, grad=0.3)
            f.trim(bottom_rim(m, 2), m, T)
            for x in (44, 83):
                rivet(f, x, min(y for _, y in m) + 4, T, small=True)
        f.metal(skull, M, grad=0.4)
        f.trim(bottom_rim(skull, 2), skull, T)
        f.metal(rect(62, 25, 65, 48), M, base=0.7)
        specular(f, skull, M, 8)
        return
    neck_leather(f, hs([(64, 62), (54, 62), (50, 66), (48, 76), (64, 76)]), 4)
    skull = hs([(64, 25), (55, 26), (48, 29), (43, 36), (41, 42), (37, 47), (40, 48), (64, 48)])
    slit = hs([(44, 48), (64, 48), (64, 51), (45, 51)])
    bevor = [hs([(64, 51), (45, 51), (44, 59), (64, 60)]), hs([(64, 59), (44, 58), (43, 67), (64, 68)]),
             hs([(64, 67), (43, 66), (40, 76), (64, 77)])]
    opening(f, slit)
    for m in reversed(bevor):
        f.metal(m, M, grad=0.3)
        f.trim(top_rim(m, 2), m, T)
    for side in (0, 1):                                                             # breathing slots
        for x in (47, 50, 53, 56):
            for y0 in (54, 62):
                for y in range(y0, y0 + 3):
                    f.put(v2.MX(x, side), y, DARK[1], 'metal')
                f.put(v2.MX(x, side) + 1, y0 + 1, M[6], 'metal')
        rivet(f, v2.MX(47, side) - side, 71, T)
    f.metal(rect(62, 51, 65, 76), M, base=0.65)                                   # bevor centre ridge
    f.metal(skull, M, grad=0.4)
    f.trim(bottom_rim(skull, 2), skull, T)
    f.metal(rect(62, 25, 65, 46), M, base=0.72)                                   # keel
    for x in (46, 54, 73, 81):
        rivet(f, x, 44, T, small=True)
    specular(f, skull, M, 8)


# ---- Thorium: closed great helm ---------------------------------------------------------------------
def thorium(f, M, T, view):
    if view == 'side':
        neck_leather(f, poly([(50, 62), (78, 62), (80, 76), (48, 78)]), 6)
        shell = poly([(46, 27), (82, 27), (86, 31), (87, 70), (44, 70), (42, 31)])
        f.metal(shell, M, grad=0.35, tex=v2.grooves(36, 60))
        f.trim(top_rim(shell, 3), shell, T)
        f.trim(bottom_rim(shell, 2), shell, T)
        sl = poly([(80, 43), (88, 43), (88, 46), (80, 46)])
        opening(f, sl & shell)
        f.metal(rect(76, 39, 87, 42) | rect(76, 47, 87, 50), T)                   # visor bands
        f.metal(rect(84, 27, 87, 70), T, base=0.55)                              # front ridge
        r = ring_shape(62, 52, 5, 2)
        strap(f, poly([(58, 52), (66, 52), (68, 80), (56, 80)]))
        buckle(f, 57, 66, T, w=10, h=9)
        f.metal(rect(59, 46, 65, 50), T)                                         # ring hinge
        f.metal(r, T)
        for y in (34, 64):
            for x in (50, 62, 74):
                rivet(f, x, y, T, small=True)
        return
    neck_leather(f, hs([(64, 62), (52, 62), (48, 70), (46, 78), (64, 78)]), 6)
    shell = hs([(64, 26), (48, 26), (44, 29), (43, 34), (43, 70), (64, 70)])
    for side in (0, 1):                                                            # side straps hanging from rings
        st = both(poly([(41, 56), (47, 56), (48, 84), (40, 84)])) if side == 0 else set()
        if st:
            strap(f, st)
    f.metal(shell, M, grad=0.35, tex=v2.grooves(36, 60))
    f.trim(top_rim(shell, 3), shell, T)
    f.trim(bottom_rim(shell, 2), shell, T)
    if view == 'front':
        sl = hs([(48, 44), (64, 44), (64, 47), (48, 47)])
        opening(f, sl & shell)
        band = hs([(46, 40), (64, 40), (64, 51), (46, 51)]) - sl
        f.metal(band, T)
        f.metal(rect(61, 27, 66, 69), T, base=0.55)                              # cross bar
        f.metal(rect(61, 40, 66, 51), T, base=0.7)
        for side in (0, 1):                                                          # breathing cross
            for (dx, dy) in ((0, 0), (0, -3), (0, 3), (-3, 0), (3, 0)):
                x, y = v2.MX(52, side) + dx, 60 + dy
                f.put(x, y, DARK[1], 'metal')
                f.put(x + 1, y + 1, M[5], 'metal')
        for x in (47, 55, 72, 80):
            rivet(f, x, 34, T, small=True)
    else:
        f.metal(rect(61, 27, 66, 69), T, base=0.55)
        for x in (47, 55, 72, 80):
            rivet(f, x, 34, T, small=True)
            rivet(f, x, 64, T, small=True)
    for side in (0, 1):
        cx = v2.MX(43, side)
        f.metal(ring_shape(cx, 55, 5, 2), T)
        f.metal(rect(cx - 1, 48, cx + 1, 51), T)
        buckle(f, v2.MX(40, side) - (8 if side else 0), 70, T, w=9, h=9)


# ---- Cobalt: Spartan + dark crest -------------------------------------------------------------------------
def crest_hair(f, m, seed=0):
    """dark horsehair: shaded crest with light strands"""
    f.paint(m, CREST, kind='leather', grad=0.35, tex=grain(seed, 0.08))
    xs = sorted({x for x, _ in m})
    for x in xs[1:-1:2]:
        col = sorted(y for xx, y in m if xx == x)
        if len(col) > 6:
            for y in col[2:-2]:
                if v2.hsh(x, y // 4, seed) > 0.45:
                    f.put(x, y, CREST[5], 'leather')


def cobalt(f, M, T, view):
    if view == 'side':
        neck_leather(f, poly([(52, 60), (74, 60), (78, 76), (50, 78)]), 8)
        holder = poly([(46, 30), (60, 22), (76, 23), (86, 32), (84, 34), (74, 27), (60, 26), (48, 34)])
        crest = poly([(88, 28), (86, 16), (78, 8), (66, 5), (52, 7), (42, 14), (36, 24), (34, 36), (33, 48),
                      (38, 40), (42, 32), (50, 26), (62, 22), (76, 23)])
        crest_hair(f, crest, 4)
        for k in range(10):                                                         # strands
            a = math.pi * (0.1 + 0.8 * k / 9)
            for rr in range(16, 25, 2):
                x, y = 62 - 26 * math.cos(a) * rr / 25, 30 - 25 * math.sin(a) * rr / 25
                if (int(x), int(y)) in erode(crest, 1):
                    f.put(int(x), int(y), CREST[6], 'leather')
        shell = poly([(62, 25), (72, 26), (80, 30), (85, 36), (87, 42), (88, 55), (86, 58), (83, 64), (81, 72),
                      (79, 82), (75, 79), (72, 66), (68, 62), (62, 65), (52, 68), (45, 68), (42, 60), (41, 48),
                      (43, 37), (48, 30), (54, 26)])
        sl = poly([(80, 44), (89, 44), (89, 46), (80, 46)])
        f.metal(shell - sl, M, grad=0.4, tex=facet(70))
        opening(f, sl & shell, GLOWB)
        f.trim(rim(shell - sl, 2) & clip(shell, y0=56), shell - sl, T)
        f.metal(line([(86, 38), (80, 36), (74, 38), (64, 48)], 2) & shell, T)     # brow ridge
        f.metal(holder, T)
        rivet(f, 62, 52, T)
        return
    neck_leather(f, hs([(64, 60), (54, 60), (50, 64), (48, 76), (64, 76)]), 8)
    shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 52), (41, 62), (44, 70), (48, 80),
                (52, 85), (56, 82), (60, 72), (64, 72)])
    if view == 'back':
        shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 52), (41, 62), (43, 68), (46, 72), (64, 72)])
    crest = hs([(64, 2), (58, 4), (55, 10), (55, 20), (56, 28), (64, 28)])
    if view == 'back':                                                             # crest hangs down the back
        crest = hs([(64, 2), (58, 4), (55, 10), (55, 24), (57, 40), (59, 52), (64, 56)])
    crest_hair(f, crest, 5)
    for x in (58, 61, 66, 69):
        for y in range(6, 26 if view == 'front' else 50):
            if (x, y) in erode(crest, 1) and v2.hsh(x, y // 5, 7) > 0.3:
                f.put(x, y, CREST[6], 'leather')
    if view == 'back':
        f.metal(shell, M, grad=0.4, tex=facet(64))
        f.trim(bottom_rim(shell, 3), shell, T)
        crest_hair(f, hs([(64, 26), (58, 26), (58, 44), (60, 56), (64, 58)]), 6)
        f.metal(hs([(64, 22), (56, 24), (56, 30), (64, 30)]), T)
        for side in (0, 1):
            f.metal(line([(v2.MX(42, side), 48), (v2.MX(56, side), 50)], 2), T)
        return
    sl = hs([(48, 44), (64, 44), (64, 47), (49, 47)]) | rect(62, 44, 65, 84)
    sh = shell - sl
    f.metal(sh, M, grad=0.4, tex=facet(64))
    opening(f, sl & clip(shell, y1=71), GLOWB)
    f.trim(rim(sh, 2) & clip(sh, y0=60), sh, T)
    for side in (0, 1):
        mx = lambda pts: [(v2.MX(x, side), y) for x, y in pts]
        f.metal(line(mx([(44, 41), (52, 39), (61, 40)]), 2), T)                    # angular brow
        f.metal(line(mx([(46, 54), (54, 56), (59, 62)]), 1), M, base=0.75)        # cheek facet line
        rivet(f, v2.MX(46, side) - side, 60, T, small=True)
    f.metal(hs([(64, 22), (56, 24), (56, 30), (64, 30)]), T)                      # crest holder
    rivet(f, 63, 26, M, small=True)


# ---- Adamantite: horned + spiked closed helm ---------------------------------------------------------
def horn(side_pts):
    return poly(side_pts)


def adamantite(f, M, T, view):
    spike_tex = lambda cx: chain(facet(cx), v2.grooves())
    if view == 'side':
        neck_leather(f, poly([(52, 60), (76, 60), (78, 76), (50, 78)]), 10)
        for k, (sx, sy, h) in enumerate(((46, 30, 9), (54, 26, 12), (63, 24, 15), (72, 26, 12), (80, 30, 9))):
            sp = poly([(sx - 4, sy + 3), (sx - 1, sy - h), (sx + 1, sy - h + 2), (sx + 4, sy + 3)])
            f.metal(sp, T, tex=facet(sx))
        shell = poly([(62, 25), (72, 26), (80, 30), (85, 36), (88, 44), (88, 54), (86, 62), (80, 70), (70, 72),
                      (52, 70), (44, 68), (42, 58), (41, 46), (43, 37), (48, 30), (54, 26)])
        sl = poly([(78, 44), (89, 46), (89, 49), (80, 48)])
        f.metal(shell - sl, M, grad=0.4)
        opening(f, sl & shell, GLOWR)
        f.trim(bottom_rim(shell, 2), shell, T)
        f.metal(line([(86, 52), (84, 66), (80, 70)], 2) & shell, M, base=0.75)
        hn = poly([(56, 44), (64, 38), (70, 30), (74, 18), (72, 6), (78, 14), (80, 26), (76, 38), (66, 48), (58, 50)])
        f.metal(hn, T, tex=v2.grooves(*range(14, 46, 5)))
        f.metal(ell(54, 40, 64, 50), T, base=0.6)
        rivet(f, 59, 45, M)
        return
    neck_leather(f, hs([(64, 60), (54, 60), (50, 64), (48, 76), (64, 76)]), 10)
    spikes = ((63.5, 26, 22), (56, 28, 15), (71, 28, 15), (49, 31, 10), (78, 31, 10))
    if view == 'front':
        spikes = spikes[1:] + spikes[:1]
    for sx, sy, h in spikes:
        sp = poly([(sx - 4, sy + 2), (sx - 0.5, sy - h), (sx + 0.5, sy - h), (sx + 4, sy + 2)])
        f.metal(sp, T, tex=facet(sx))
    for side in (0, 1):                                                            # big curved horns
        hn = poly([(46, 44), (38, 40), (30, 34), (24, 24), (23, 12), (26, 4), (28, 14), (31, 24), (37, 32),
                   (45, 36), (48, 38)])
        hn = hn if side == 0 else mirror(hn)
        f.metal(hn, T, tex=chain(facet(v2.MX(30, side), side == 0), v2.grooves(*range(10, 42, 5))))
    shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 54), (42, 62), (48, 69), (56, 73),
                (64, 76)])
    if view == 'back':
        shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 54), (42, 64), (46, 70), (64, 72)])
        f.metal(shell, M, grad=0.4)
        f.trim(bottom_rim(shell, 3), shell, T)
        f.metal(rect(62, 25, 65, 70), T, base=0.5)
        for side in (0, 1):
            f.metal(both(ell(39, 36, 49, 46)) if side == 0 else set(), T, base=0.6)
        for y in (40, 52, 64):
            rivet(f, 63, y, M, small=True)
        return
    sl = hs([(46, 42), (53, 45), (61, 49), (64, 50), (64, 53), (60, 52), (52, 49), (46, 46)])
    sh = shell - sl
    f.metal(sh, M, grad=0.4)
    opening(f, sl & shell, GLOWR)
    f.trim(bottom_rim(sh, 2), sh, T)
    f.metal(rect(62, 25, 65, 49), T, base=0.5)                                    # forehead ridge
    f.metal(hs([(64, 55), (60, 58), (60, 74), (64, 76)]), T, base=0.5)            # jaw ridge
    for side in (0, 1):
        for y in (58, 62, 66):                                                        # fang vents
            for x in range(v2.MX(54, side) - (4 if side else 0), v2.MX(54, side) + (1 if side else 5)):
                f.put(x, y + (x - 50) // 4 * 0, DARK[1], 'metal')
        f.metal(both(ell(39, 36, 49, 46)) if side == 0 else set(), T, base=0.6)      # horn bases
        rivet(f, v2.MX(44, side) - side, 41, M)
    specular(f, shell, M, 6)


# ---- Mithril: winged helm ---------------------------------------------------------------------------------
def plume(r, t, w):
    """feather: narrow at the root, widest near 2/3, rounded tip"""
    dx, dy = t[0] - r[0], t[1] - r[1]
    ln = math.hypot(dx, dy)
    ux, uy, nx, ny = dx / ln, dy / ln, -dy / ln, dx / ln
    prof = [(0, .25), (.25, .7), (.55, 1), (.78, .95), (.9, .7), (.97, .38), (1, 0)]
    left = [(r[0] + dx * a + nx * w * b * .5, r[1] + dy * a + ny * w * b * .5) for a, b in prof]
    right = [(r[0] + dx * a - nx * w * b * .5, r[1] + dy * a - ny * w * b * .5) for a, b in prof]
    return poly(left + right[::-1]), (ux, uy, nx, ny, ln)


def wing(f, M, T, root, flip, view):
    """big swept feathered wing: 7 primaries fanning up / out from the temple, coverts over the roots"""
    rx, ry = root
    sgn = -1 if not flip else 1
    angs = [186, 171, 156, 141, 127, 114, 102] if view != 'side' else [180, 165, 150, 135, 121, 108, 96]
    lens = [26, 34, 41, 45, 46, 42, 34]
    for k in range(7):
        a = math.radians(angs[k])
        L = lens[k]
        cx = math.cos(a) * L
        if view != 'side' and flip:
            cx = -cx
        tp = (rx + cx, ry - abs(math.sin(a)) * L if angs[k] < 180 else ry + abs(math.sin(a)) * L)
        r0 = (rx + sgn * 2, ry - 1)
        fm, (ux, uy, nx, ny, ln) = plume(r0, tp, 9)
        f.metal(fm, M, base=0.40 + 0.035 * k, grad=0.3)
        for j in range(2, int(ln) - 2):                                              # quill (trim colour)
            q = (int(round(r0[0] + ux * j)), int(round(r0[1] + uy * j)))
            f.put(*q, T[4] if j % 4 else T[6], 'metal')
        for j in range(6, int(ln) - 4, 3):                                            # barbs: angled grooves
            for side in (1, -1):
                for d in (2, 3):
                    q = (int(round(r0[0] + ux * (j - d * .8) + nx * d * side)),
                         int(round(r0[1] + uy * (j - d * .8) + ny * d * side)))
                    if q in erode(fm, 1):
                        f.put(*q, M[2] if side > 0 else M[1], 'metal')
    for k in range(4):                                                               # short covert feathers
        a = math.radians([175, 155, 135, 115][k] if view != 'side' else [165, 145, 125, 105][k])
        cx = math.cos(a) * 15
        if view != 'side' and flip:
            cx = -cx
        tp = (rx + cx, ry - abs(math.sin(a)) * 15)
        fm, _ = plume((rx, ry), tp, 8)
        f.metal(fm, M, base=0.6, grad=0.25)
    mount = poly([(rx - 4, ry), (rx, ry - 5), (rx + 4, ry), (rx, ry + 5)])          # gold diamond mount
    f.metal(mount, T, base=0.6)
    f.put(rx - 1, ry - 2, T[6], 'metal')


def mithril(f, M, T, view):
    if view == 'side':
        neck_leather(f, poly([(52, 60), (74, 60), (78, 76), (50, 78)]), 12)
        shell = poly([(62, 25), (72, 26), (80, 30), (85, 36), (87, 42), (88, 56), (84, 66), (76, 70), (52, 70),
                      (44, 68), (42, 58), (41, 46), (43, 37), (48, 30), (54, 26)])
        eye = poly([(81, 41), (89, 41), (89, 48), (82, 48)])
        opening(f, eye & shell)
        f.metal(shell - eye, M, grad=0.4)
        f.trim(rim(shell - eye, 2) & clip(shell, y0=60), shell - eye, T)
        f.metal(line([(88, 39), (80, 39), (78, 44), (80, 50), (88, 50)], 2) & dil(shell, 1), T)
        f.metal(line([(48, 52), (64, 54), (80, 52)], 2) & shell, T)
        wing(f, M, T, (62, 42), False, 'side')
        specular(f, shell, M, 8)
        return
    neck_leather(f, hs([(64, 60), (54, 60), (50, 64), (48, 76), (64, 76)]), 12)
    shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 54), (42, 63), (48, 70), (64, 72)])
    if view == 'back':
        f.metal(shell, M, grad=0.4)
        f.trim(bottom_rim(shell, 3), shell, T)
        f.metal(hs([(64, 50), (40, 50), (40, 53), (64, 53)]) & shell, T)
        f.metal(rect(62, 25, 65, 50), T, base=0.55)
        for side in (0, 1):
            wing(f, M, T, (v2.MX(42, side), 42), bool(side), 'front')
        specular(f, shell, M, 8)
        return
    eyes = both(ell(47, 40, 60, 49))
    sh = shell - eyes
    f.metal(sh, M, grad=0.4)
    opening(f, eyes)
    liner(f, sh, eyes)
    spec = both(ell(45, 38, 62, 51) - ell(47, 40, 60, 49)) | rect(61, 37, 66, 60)   # spectacle guard + nose
    f.metal(spec, T)
    f.trim(bottom_rim(shell, 2), shell, T)
    f.metal(hs([(64, 30), (61, 33), (61, 37), (64, 38)]), T, base=0.6)           # brow fleur
    for side in (0, 1):
        f.metal(line([(v2.MX(46, side), 58), (v2.MX(58, side), 64)], 1) & shell, M, base=0.75)
        rivet(f, v2.MX(50, side) - side, 66, T, small=True)
        wing(f, M, T, (v2.MX(42, side), 42), bool(side), 'front')
    rivet(f, 63, 34, M, small=True)
    specular(f, shell, M, 8)


# ---- Onyxium: crowned helm + forehead gem ------------------------------------------------------------
def chain_links(f, pts, rp):
    for k, (x, y) in enumerate(pts):
        if k % 2 == 0:
            f.stamp(int(x) - 1, int(y) - 1, [".1.", "1.1", ".1."], rp)
            f.put(int(x) - 1, int(y) - 1, rp[5], 'metal')
        else:
            f.stamp(int(x), int(y) - 1, ["5", "3", "1"], rp)


def onyxium(f, M, T, view):
    if view == 'side':
        neck_leather(f, poly([(52, 60), (74, 60), (78, 76), (50, 78)]), 14)
        shell = poly([(62, 25), (72, 26), (80, 30), (85, 36), (88, 42), (88, 56), (85, 64), (78, 70), (52, 70),
                      (44, 68), (42, 58), (41, 46), (43, 37), (48, 30), (54, 26)])
        sl = poly([(80, 46), (89, 45), (89, 48), (81, 49)])
        f.metal(shell - sl, M, grad=0.4)
        opening(f, sl & shell, GEM)
        f.trim(bottom_rim(shell, 2), shell, T)
        crown = poly([(42, 34), (44, 26), (47, 30), (52, 18), (56, 26), (62, 14), (68, 25), (74, 16), (78, 27),
                      (84, 22), (86, 34)]) | poly([(42, 30), (87, 30), (87, 36), (42, 37)])
        f.metal(crown, T, tex=facet(64))
        f.metal(ell(84, 36, 91, 44), T, base=0.6)
        f.paint(ell(86, 37, 90, 42), GEM, kind='metal', base=0.6)
        f.put(87, 38, GEM[6], 'metal')
        for x in (50, 62, 74):
            f.paint(ell(x - 2, 31, x + 2, 35), GEM, kind='metal', base=0.5)
        chain_links(f, [(52, 38 + k * 3) for k in range(9)], T)
        f.metal(line([(86, 52), (84, 64), (78, 70)], 2) & shell, T)
        return
    neck_leather(f, hs([(64, 60), (54, 60), (50, 64), (48, 76), (64, 76)]), 14)
    shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 54), (42, 63), (48, 70), (56, 74), (64, 76)])
    if view == 'back':
        shell = hs([(64, 25), (55, 26), (48, 29), (44, 35), (41, 42), (40, 54), (42, 64), (46, 70), (64, 72)])
    sl = set()
    if view == 'front':
        sl = hs([(46, 48), (52, 46), (59, 47), (61, 50), (54, 51), (47, 51)])
    sh = shell - sl
    f.metal(sh, M, grad=0.4)
    if sl:
        opening(f, sl & shell, GEM)
    f.trim(bottom_rim(sh, 2), sh, T)
    # crown: band + 5 points with round finials and small gems
    band = hs([(64, 30), (43, 32), (42, 39), (64, 37)])
    pts = hs([(64, 6), (61, 18), (58, 24), (56, 12), (53, 22), (50, 26), (47, 16), (45, 30), (64, 31)])
    f.metal(pts | band, T, tex=facet(64))
    for (x, y) in ((63.5, 5), (56, 11), (47, 15), (71, 11), (80, 15)):
        f.metal(ell(x - 2, y - 2, x + 2, y + 2), T, base=0.7)
    for x in (48, 56, 71, 79):
        f.paint(ell(x - 2, 33, x + 2, 36), GEM if view == 'front' else T, kind='metal', base=0.5)
    for side in (0, 1):                                                            # hanging chains
        x = v2.MX(43, side)
        chain_links(f, [(x, 39 + k * 3) for k in range(10)], T)
    if view == 'front':
        f.metal(ell(57, 36, 70, 47), T, base=0.6)                                 # gem mount
        f.paint(ell(59, 37, 68, 45), GEM, kind='metal', base=0.62, grad=0.35)
        f.stamp(61, 38, ["66", "6."], GEM)
        f.put(63, 46, T[6], 'metal')
        f.metal(hs([(64, 47), (62, 50), (62, 72), (64, 74)]), T, base=0.55)       # face ridge
        for side in (0, 1):
            f.metal(line([(v2.MX(46, side), 56), (v2.MX(57, side), 62)], 1) & shell, T)
            rivet(f, v2.MX(50, side) - side, 66, T, small=True)
    else:
        f.metal(rect(62, 38, 65, 70), T, base=0.5)
    specular(f, shell, M, 6)


# ---------------------------------------------------------------- hook into the v2 body
def helmet_v3(f, t, back):
    helm(f, t, 'back' if back else 'front')


v2.helmet = helmet_v3


def side_bust(t):
    """profile head + shoulders (facing right): black leather collar + layered shoulder cap, tier rim"""
    name, band, M = TIERS[t]
    c = ms.cfg_for(t)
    f = Fig()
    lg = grain(t, 0.10)
    f.paint(poly([(46, 72), (80, 72), (90, 86), (90, 104), (40, 104), (42, 84)]), LEATHER, tex=quilt(12, t), grad=0.3)
    f.paint(poly([(54, 62), (76, 62), (80, 80), (50, 80)]), LEATHER_IN, tex=grain(17, 0.06))           # collar
    col = poly([(50, 66), (80, 64), (84, 80), (48, 80)])
    f.paint(col, LEATHER, tex=chain(lg, v2.grooves(73)), grad=0.35)
    f.stitch(col, THREAD, d=2, per=3, on=1)
    if c['collar']:
        f.trim(top_rim(col, 2 * c['collar']), col, M)
    for k, m in ((3, ell(46, 86, 80, 106)), (2, ell(42, 80, 84, 102)), (1, ell(40, 74, 86, 96))):
        f.paint(m, LEATHER, tex=lg, grad=0.35)
        f.stitch(m, THREAD, d=2, per=3, on=1)
        if k in c['rims']:
            f.trim(bottom_rim(m, 2 * c['rim_w']), m, M)
    rivet(f, 63, 82, M)
    helm(f, t, 'side')
    return f


# ---------------------------------------------------------------- output
def cell(f, box, s):
    im = f.im.crop(box)
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, BG)
    base.alpha_composite(im)
    return base


def save(im, name):
    im = im.convert('RGB').quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    p = os.path.join(OUT, name)
    im.save(p, optimize=True)
    return os.path.getsize(p)


SUB = (60, 64, 70, 255)


def main():
    sizes = {}
    # ---- helmets-v3: rows = front / side / back, columns = tiers
    S = 4
    box = (8, 0, 120, 100)
    cw, chh = (box[2] - box[0]) * S, (box[3] - box[1]) * S
    left, gap, top, labh = 120, 14, 100, 60
    n = len(TIERS) - 1
    hw = left + n * (cw + gap)
    hh = top + 3 * (chh + labh) + 10
    hs_ = Image.new('RGBA', (hw, hh), BG)
    d = ImageDraw.Draw(hs_)
    d.text((hw // 2, 14), 'SkyWynn Light Armor - hard metal helmets v3 (cloud draft)', font=font(40), fill=INK, anchor='mt')
    d.text((hw // 2, 62), 'no cloth hood, no masks  |  each helm in its tier metal + a contrasting trim  |  black leather '
           'where it meets the body  |  128 x 202 figure grid (2x), shown x4', font=font(18), fill=SUB, anchor='mt')
    for r, view in enumerate(('front', 'side', 'back')):
        y = top + r * (chh + labh)
        d.text((left // 2, y + chh // 2), view, font=font(28), fill=INK, anchor='mm')
        for i in range(1, len(TIERS)):
            name, band, M = TIERS[i]
            x = left + (i - 1) * (cw + gap)
            f = side_bust(i) if view == 'side' else v2.draw_figure(i, back=(view == 'back'))
            hs_.paste(cell(f, box, S), (x, y))
            if r == 0:
                d.text((x + cw // 2, y + chh + 4), f'{name} - {NAME[i]}', font=font(24), fill=INK, anchor='mt')
                d.text((x + cw // 2, y + chh + 32), f'{NOTE[i]}  |  trim: {TRIMN[i]}', font=font(15), fill=SUB, anchor='mt')
            else:
                d.text((x + cw // 2, y + chh + 6), f'{name} - {view}', font=font(20), fill=SUB, anchor='mt')
    sizes['helmets-v3.png'] = save(hs_, 'helmets-v3.png')

    # ---- light-armor-sheet-v3: the v2 bodies wearing the v3 helmets (same layout as v2)
    SS = 3
    fronts = [None] + [v2.scaled(v2.draw_figure(i), SS) for i in range(1, len(TIERS))]
    backs = [None] + [v2.scaled(v2.draw_figure(i, back=True), SS) for i in range(1, len(TIERS))]
    fw, fh = fronts[1].size
    gap, top, labh = 16, 92, 54
    sw = len(TIERS) * fw + (len(TIERS) + 1) * gap
    sh = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sw, sh), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sw // 2, 16), 'SkyWynn Light Armor - v3 concept (cloud draft)', font=font(40), fill=INK, anchor='mt')
    d.text((sw // 2, 62), 'v2 bodies (approved)  |  v3 hard metal helmets: Corinthian, sallet, great helm, Spartan, horned, '
           'winged, crowned  |  vanilla shapes UNVERIFIED', font=font(18), fill=SUB, anchor='mt')
    grey = (110, 114, 120, 255)
    for i, (name, band, M) in enumerate(TIERS):
        x = gap + i * (fw + gap)
        y2 = top + fh + labh + gap
        if fronts[i] is None:
            d.rectangle((x, top, x + fw - 1, y2 + fh - 1), fill=(166, 171, 177, 255), outline=(140, 145, 151, 255), width=3)
            for k, ln in enumerate(['Tier 1', 'vanilla leather', 'armor', '', '(no new design)']):
                d.text((x + fw // 2, top + 200 + k * 34), ln, font=font(26 if k < 3 else 20), fill=grey, anchor='mt')
            d.text((x + fw // 2, top + fh + 6), 'Leather', font=font(26), fill=grey, anchor='mt')
            d.text((x + fw // 2, top + fh + 34), band + '  (vanilla)', font=font(15), fill=grey, anchor='mt')
            continue
        sheet.paste(fronts[i], (x, top))
        d.text((x + fw // 2, top + fh + 6), name, font=font(26), fill=INK, anchor='mt')
        d.text((x + fw // 2, top + fh + 34), f'{band}  (front)  |  {NAME[i]}', font=font(15), fill=SUB, anchor='mt')
        for j, col in enumerate([M[5], M[3], M[1]]):
            d.rectangle((x + 8 + j * 18, top + 8, x + 22 + j * 18, top + 22), fill=col, outline=M[0])
        T = TRIM[i]
        d.rectangle((x + 8 + 3 * 18 + 6, top + 8, x + 22 + 3 * 18 + 6, top + 22), fill=T[4], outline=T[0])
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), name + ' (back)', font=font(18), fill=SUB, anchor='mt')
    sizes['light-armor-sheet-v3.png'] = save(sheet, 'light-armor-sheet-v3.png')
    for k, v in sizes.items():
        print(f'{k:28s} {v // 1024:5d} KB  {Image.open(os.path.join(OUT, k)).size}')


TRIMN = {1: 'gold inlay', 2: 'brass', 3: 'steel', 4: 'steel', 5: 'black steel', 6: 'gold', 7: 'gold'}

if __name__ == '__main__':
    main()
