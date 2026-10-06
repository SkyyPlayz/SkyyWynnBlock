"""Zone 1 town v2 map (organic). Deterministic. Usage: python3 town_v2.py OUT.png"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

random.seed(1006)
W, H = 1600, 1112
X0, X1, Z0, Z1 = -142, 142, -128, 110       # world box shown (blocks)
S = 4.35                                      # px per block
OX, OY = 18, 58                               # map origin on canvas
MW, MH = int((X1 - X0) * S), int((Z1 - Z0) * S)

def P(x, z):
    return (OX + (x - X0) * S, OY + (z - Z0) * S)

F = "/usr/share/fonts/truetype/dejavu/"
fT = ImageFont.truetype(F + "DejaVuSerif-Bold.ttf", 26)
fD = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 15)
fS = ImageFont.truetype(F + "DejaVuSans.ttf", 12)
fSB = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 12)
fN = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 10)
fL = ImageFont.truetype(F + "DejaVuSans.ttf", 13)
fLB = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 14)

# ---------- geometry helpers ----------
def catmull(pts, n=16):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out

def closed_spline(pts, n=14):
    p = pts[-1:] + pts + pts[:2]
    return catmull(p, n)[n:-n - 1]

def plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))

def blob(cx, cz, radii, rot=0.0):
    k = len(radii)
    pts = [(cx + r * math.cos(rot + 2 * math.pi * i / k), cz + r * math.sin(rot + 2 * math.pi * i / k)) for i, r in enumerate(radii)]
    return closed_spline(pts)

def rrect(cx, cz, w, h, ang):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    return [(cx + dx * c - dz * s, cz + dx * s + dz * c) for dx, dz in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))]

def lshape(cx, cz, w, h, cw, ch, ang):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    loc = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2 - ch), (w/2 - cw, h/2 - ch), (w/2 - cw, h/2), (-w/2, h/2)]
    return [(cx + dx * c - dz * s, cz + dx * s + dz * c) for dx, dz in loc]

def ngon(cx, cz, r, n, rot=0):
    return [(cx + r * math.cos(rot + 2 * math.pi * i / n), cz + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]

def px(poly):
    return [P(*q) for q in poly]

# ---------- terrain ----------
def coast_z(x):
    z = 93 + 7 * math.sin(x / 37.0 + 0.6) + 4 * math.sin(x / 13.0 + 1.9)
    if x > 100:                     # the east headland bends north: the Zone 2 viewpoint
        z -= 26 * ((x - 100) / 42) ** 1.5
    return z

def height(x, z):
    h = 148 - 0.075 * z                                   # rises north toward the mountain
    h += 4.0 * math.exp(-((x) ** 2 + (z + 2) ** 2) / 900)  # the temple knoll
    h += 2.2 * math.sin(x / 29.0) * math.cos(z / 41.0)
    h += 1.6 * math.sin((x + z) / 23.0 + 1.3)
    return h

# ---------- the plan (blocks, x east, z south; temple centre = 0,0) ----------
TEMPLE = (-20, -20, 20, 20)
SPAWN = (0, 27)

ROADS = {  # name: (control points, width blocks)
    "summit":  ([(0, -24), (-5, -40), (4, -56), (-3, -72), (6, -88), (5, -106), (2, -126)], 8),
    "market":  ([(26, -4), (40, -12), (54, -13), (68, -20)], 7),
    "bank":    ([(-26, -6), (-40, -15), (-54, -28), (-70, -33)], 7),
    "forge":   ([(-24, 34), (-38, 42), (-52, 41), (-66, 47)], 6),
    "event":   ([(24, 40), (38, 50), (52, 49), (64, 54)], 6),
    "homes":   ([(4, -78), (24, -88), (46, -96), (70, -94), (92, -80), (100, -62), (110, -50)], 5),
    "orchard": ([(-3, -60), (-20, -70), (-42, -78), (-62, -84)], 5),
    "tab":     ([(-92, -20), (-100, -6), (-104, 6)], 4),
    "kiln":    ([(-84, 54), (-82, 66), (-74, 77)], 4),
    "promen":  ([(x, coast_z(x) - 11) for x in range(-134, 133, 14)], 9),
    "stairW":  ([(-14, 54), (-22, 66), (-28, coast_z(-28) - 12)], 4),
    "stairE":  ([(16, 56), (24, 68), (32, coast_z(32) - 12)], 4),
    "mktup":   ([(96, -36), (104, -46), (110, -50)], 4),
    "evtup":   ([(92, 34), (90, 10), (88, 2)], 4),
}

PLAZAS = {  # name: (cx, cz, radii, rot, fill)
    "square":  (0, 10, [44, 40, 38, 46, 50, 54, 50, 46, 42, 48, 52, 44], 0.2),
    "market":  (86, -16, [24, 20, 22, 26, 21, 19, 23, 18, 22], 0.4),
    "bank":    (-84, -32, [19, 16, 18, 20, 15, 17, 19], 1.0),
    "forge":   (-80, 48, [16, 14, 17, 15, 13, 16], 0.3),
    "event":   (86, 52, [22, 23, 21, 22, 24, 22, 21, 23], 0.0),
    "gate":    (4, -102, [11, 9, 10, 12, 9, 10], 0.0),
    "view":    (124, 60, [12, 10, 11, 13, 10], 0.5),
}

# buildings: (district no, label, polygon, roof colour, kind)
STALL_A = [28, 62, 96, 130]
stalls = []
for i, a in enumerate(STALL_A):
    r = math.radians(a)
    cx, cz = 86 + 33 * math.cos(r), -16 + 30 * math.sin(r)
    stalls.append((6, ["General", "Forager", "Miner", "Farmer"][i], rrect(cx, cz, 12, 10, a + 90), (205, 112, 72), "stall"))

BUILD = [
    (4, "Bazaar hall", lshape(80, -50, 34, 26, 12, 10, -10), (226, 160, 66), "hall"),
    (5, "Auction House", ngon(118, -24, 14, 8, math.pi / 8), (232, 196, 92), "dome"),
    (7, "Bank", rrect(-80, -60, 28, 22, 7), (98, 140, 200), "hall"),
    (7, "Vault + Guild", lshape(-116, -34, 26, 26, 10, 11, -16), (128, 168, 214), "hall"),
    (9, "Tab Hall (reserved)", rrect(-112, 22, 40, 22, 14), (122, 112, 132), "plot"),
    (8, "Forge", lshape(-104, 50, 28, 24, 10, 9, -22), (160, 70, 58), "hall"),
    (8, "Crafting Hall", rrect(-52, 60, 22, 17, 18), (180, 104, 80), "hall"),
    (12, "North Gate", rrect(4, -110, 26, 7, -4), (150, 150, 150), "gate"),
] + stalls

# homes: small varied houses along the homes lane + a few along the orchard path
homes_spots = [(30, -100, 25), (44, -84, 10), (58, -108, -5), (72, -82, -12), (86, -98, 30), (104, -76, 55), (114, -96, 40),
               (36, -118, 15), (124, -56, 70)]
HOMES = []
for (cx, cz, a) in homes_spots:
    w, h = random.choice([(10, 8), (9, 9), (12, 8), (8, 11)])
    if random.random() < 0.35:
        HOMES.append(ngon(cx, cz, 5.5, 7, random.random()))
    else:
        HOMES.append(rrect(cx, cz, w, h, a))

# filler houses lining the roads (future shops / homes; the Hub packs buildings along its lanes)
FILLER = [rrect(-50, -2, 11, 8, -30), lshape(46, -32, 12, 11, 5, 5, -20), rrect(-58, 28, 10, 8, 25),
          rrect(-18, -48, 9, 8, 12), rrect(20, -42, 10, 8, -15), rrect(-30, -32, 8, 7, -40),
          rrect(-72, 16, 9, 8, -10), rrect(14, -64, 9, 8, -25)]

# trees
TREES = []
def add_trees(cx, cz, rx, rz, n, avoid=()):
    t = 0
    while t < n:
        x, z = cx + random.uniform(-rx, rx), cz + random.uniform(-rz, rz)
        if ((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2 > 1: continue
        TREES.append((x, z, random.uniform(2.6, 4.6), random.random() < 0.7)); t += 1
# orchard: loose rows bent along a curve
for row in range(6):
    for k in range(9):
        x = -120 + k * 9 + 4 * math.sin(row * 0.9) + random.uniform(-1.2, 1.2)
        z = -118 + row * 9 + 5 * math.sin(k / 2.2 + row) + random.uniform(-1.2, 1.2)
        if z > -72 + (x + 120) * 0.15 or z > -76: continue
        TREES.append((x, z, random.uniform(2.6, 3.4), False))
add_trees(-30, -100, 18, 14, 14)
add_trees(130, 8, 9, 30, 9)
add_trees(-128, -6, 8, 14, 6)
add_trees(48, 20, 9, 7, 4)
add_trees(-46, 16, 8, 8, 4)
add_trees(-40, -48, 8, 8, 4)
add_trees(40, -50, 9, 8, 5)
add_trees(-130, 70, 7, 9, 4)

# points of interest (marker colour, map number)
POI = [
    ("Spawn / Arrival Pad", SPAWN, (255, 140, 0)),
    ("Clerk Mossby (desk)", (0, -8), (220, 40, 60)),
    ("The Board", (0, -15), (40, 200, 220)),
    ("Mail box", (-27, -16), (245, 245, 235)),
    ("Warp Pad", (-24, 44), (40, 200, 220)),
    ("Door Home (shard arch)", (26, 44), (255, 140, 0)),
    ("Pebble's rock", (-8, 50), (245, 245, 235)),
    ("Banker", (-80, -56), (220, 40, 60)),
    ("Vault keeper", (-118, -38), (220, 40, 60)),
    ("Guild clerk", (-112, -28), (220, 40, 60)),
    ("Bazaar broker", (78, -52), (220, 40, 60)),
    ("Auction clerk", (118, -24), (220, 40, 60)),
    ("Smith", (-104, 48), (220, 40, 60)),
    ("Event Vendor", (86, 52), (220, 40, 60)),
    ("Guard (North Gate)", (4, -100), (120, 40, 160)),
    ("Guard (Square NW)", (-34, -26), (120, 40, 160)),
    ("Guard (Promenade W)", (-64, coast_z(-64) - 11), (120, 40, 160)),
    ("Guard (Promenade E)", (64, coast_z(64) - 11), (120, 40, 160)),
    ("Zone 2 viewpoint", (126, 60), (40, 200, 220)),
]

DISTRICT_LABELS = [  # (text, x, z)
    ("1 Temple", 0, -27), ("2 Waiting Square", -3, 64), ("3 Market Row", 86, -2), ("6 Stalls", 62, 20),
    ("7 Bank Row", -84, -16), ("8 Forge Quarter", -82, 34), ("10 Event Square", 86, 78),
    ("11 Promenade", -100, 84), ("12 North Gate", 30, -112), ("13 Orchard park", -84, -122),
    ("13 Kweebec homes", 80, -124), ("Summit Road", 18, -66), ("to the summit (about 1,015 b)", 2, -128 + 6),
]

def route(points):
    """walk length: straight hops between waypoints; road splines expanded."""
    pts = []
    for p in points:
        if isinstance(p, str):
            pts += catmull(ROADS[p][0])
        elif isinstance(p, tuple) and len(p) == 3:   # reversed road
            pts += list(reversed(catmull(ROADS[p[0]][0])))
        else:
            pts.append(p)
    return plen(pts)

# temple door is at (0,20); spawn just outside it. Routes go round the temple via the square.
WALKS = {
    "Mossby desk (inside, via south door)": [SPAWN, (0, 20), (0, -6)],
    "Warp Pad": [SPAWN, (-24, 44)],
    "Door Home arch": [SPAWN, (26, 44)],
    "Bazaar door": [SPAWN, (24, 18), "market", (78, -26), (80, -37)],
    "Auction House door": [SPAWN, (24, 18), "market", (90, -16), (106, -22)],
    "General stall": [SPAWN, (24, 18), "market", (90, -2)],
    "Farmer stall": [SPAWN, (24, 18), "market", (68, 6)],
    "Bank door": [SPAWN, (-24, 18), "bank", (-82, -40), (-81, -49)],
    "Vault + Guild door": [SPAWN, (-24, 18), "bank", (-100, -32)],
    "Forge door": [SPAWN, "forge", (-90, 50)],
    "Crafting Hall door": [SPAWN, "forge", (-62, 56)],
    "Event Vendor": [SPAWN, "event", (86, 52)],
    "Tab Hall plot": [SPAWN, (-24, 18), "bank", "tab", (-108, 12)],
    "North Gate": [SPAWN, (24, 18), (26, -4), (0, -24), "summit"],
}

def walk_table():
    rows = []
    for k, v in WALKS.items():
        if k == "North Gate":
            pts = [SPAWN, (24, 18), (26, -4), (0, -24)] + catmull(ROADS["summit"][0])
            pts = [p for p in pts if p[1] >= -104] + [(5, -104)]
            d = plen(pts)
        else:
            d = route(v)
        rows.append((k, round(d), round(d / 5.5, 1)))
    return rows

# ---------- drawing ----------
def draw(out):
    img = Image.new("RGB", (W, H), (30, 36, 30))
    mapimg = Image.new("RGB", (MW, MH), (98, 150, 78))
    # grass noise
    noise = Image.effect_noise((MW // 3, MH // 3), 26).resize((MW, MH), Image.BILINEAR)
    g = Image.merge("RGB", (noise.point(lambda v: 60 + v * 0.25), noise.point(lambda v: 110 + v * 0.30), noise.point(lambda v: 50 + v * 0.18)))
    mapimg = Image.blend(mapimg, g, 0.55)
    # terrain shading + contours (per block)
    bw, bh = X1 - X0, Z1 - Z0
    band = Image.new("L", (bw, bh)); shade = Image.new("L", (bw, bh))
    for j in range(bh):
        for i in range(bw):
            h = height(X0 + i, Z0 + j)
            band.putpixel((i, j), int(h // 2.0) * 23 % 256)
            shade.putpixel((i, j), max(0, min(255, int((h - 146) * 14))))
    band = band.resize((MW, MH), Image.NEAREST)
    shade = shade.resize((MW, MH), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
    light = Image.merge("RGB", (shade, shade, shade))
    mapimg = ImageChops.add(mapimg, light.point(lambda v: v // 7))
    edges = band.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.GaussianBlur(0.8))
    cont = Image.new("RGB", (MW, MH), (58, 92, 44))
    mapimg = Image.composite(cont, mapimg, edges.point(lambda v: int(v * 0.85)))
    img.paste(mapimg, (OX, OY))
    d = ImageDraw.Draw(img, "RGBA")
    # void + cliff
    coast = [(x, coast_z(x)) for x in range(X0, X1 + 1, 2)]
    void = px(coast) + [P(X1, Z1), P(X0, Z1)]
    d.polygon(void, fill=(26, 28, 58))
    for k in range(40):  # stars in the void
        x, z = random.uniform(X0, X1), random.uniform(98, Z1)
        if z > coast_z(x) + 4:
            d.ellipse([P(x, z)[0] - 1, P(x, z)[1] - 1, P(x, z)[0] + 1, P(x, z)[1] + 1], fill=(200, 200, 255, 160))
    for off, col in ((3.5, (88, 78, 62)), (1.6, (124, 110, 88))):
        d.line(px([(x, z - 0) for x, z in coast]), fill=col, width=int(off * S))
    d.line(px([(x, z - 1.8) for x, z in coast]), fill=(70, 60, 48), width=2)
    # town limit (dashed, organic)
    lim = blob(0, -8, [134, 128, 126, 118, 112, 120, 132, 138, 136, 128, 124, 130], 0.0)
    for i in range(0, len(lim) - 1, 2):
        if lim[i][1] > coast_z(lim[i][0]) - 14 or lim[i + 1][1] > coast_z(lim[i + 1][0]) - 14: continue
        d.line([P(*lim[i]), P(*lim[i + 1])], fill=(240, 240, 210, 110), width=2)
    # plazas
    pc = {"square": (196, 190, 168), "market": (204, 186, 150), "bank": (184, 188, 196), "forge": (170, 150, 132),
          "event": (186, 210, 190), "gate": (176, 170, 156), "view": (196, 190, 168)}
    for n, (cx, cz, rr, rot) in PLAZAS.items():
        b = px(blob(cx, cz, rr, rot))
        d.polygon(b, fill=pc[n] + (255,), outline=(110, 96, 78), width=3)
    # paving texture on the main square: concentric rings around the temple
    for r in range(28, 58, 6):
        ring = [(r * 1.0 * math.cos(t / 30 * math.pi), 2 + r * 0.95 * math.sin(t / 30 * math.pi)) for t in range(61)]
        d.line(px(ring), fill=(170, 162, 140, 120), width=1)
    # roads: edge then fill
    for n, (pts, w) in ROADS.items():
        sp = px(catmull(pts))
        d.line(sp, fill=(104, 86, 62), width=int(w * S) + 4, joint="curve")
    for n, (pts, w) in ROADS.items():
        sp = px(catmull(pts))
        col = (196, 178, 140) if n not in ("promen",) else (206, 200, 178)
        d.line(sp, fill=col, width=int(w * S), joint="curve")
        for q in sp[::1]:
            r = w * S / 2
            d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)
    # cobble specks on roads
    for n, (pts, w) in ROADS.items():
        for q in catmull(pts, 30):
            for _ in range(2):
                a = random.uniform(-w / 2.5, w / 2.5)
                x, y = P(q[0] + a, q[1] + random.uniform(-1, 1))
                d.rectangle([x, y, x + 2, y + 2], fill=(150, 132, 100, 140))
    # promenade fence + lanterns
    d.line(px([(x, z - 4.5) for x, z in coast]), fill=(92, 64, 40), width=3)
    for x in range(-130, 131, 20):
        cx, cy = P(x, coast_z(x) - 6)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 120), outline=(90, 70, 30))
    # trees
    for (x, z, r, round_) in sorted(TREES, key=lambda t: t[1]):
        cx, cy = P(x, z); rp = r * S
        d.ellipse([cx - rp + 3, cy - rp + 4, cx + rp + 3, cy + rp + 4], fill=(30, 50, 25, 90))
        base = (58, 112, 50) if round_ else (84, 128, 44)
        d.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], fill=base, outline=(32, 60, 28))
        d.ellipse([cx - rp * 0.6, cy - rp * 0.7, cx + rp * 0.1, cy - rp * 0.0], fill=tuple(min(255, c + 34) for c in base))
        if not round_:
            d.ellipse([cx + 1, cy + 1, cx + 4, cy + 4], fill=(220, 70, 60))
    # buildings with shadow, roof, ridge
    def building(poly, roof, kind):
        sh = [(x + 5, y + 6) for x, y in px(poly)]
        d.polygon(sh, fill=(20, 30, 18, 110))
        d.polygon(px(poly), fill=roof, outline=(40, 32, 26), width=2)
        pp = px(poly)
        cx = sum(p[0] for p in pp) / len(pp); cy = sum(p[1] for p in pp) / len(pp)
        if kind in ("hall", "stall", "home"):
            # ridge along the long side of the first edge
            a, b = pp[0], pp[1]
            mid1 = ((pp[0][0] + pp[-1][0]) / 2, (pp[0][1] + pp[-1][1]) / 2)
            mid2 = ((pp[1][0] + pp[2][0]) / 2, (pp[1][1] + pp[2][1]) / 2)
            d.polygon([pp[0], pp[1], mid2, mid1], fill=tuple(min(255, c + 26) for c in roof))
            d.line([mid1, mid2], fill=tuple(max(0, c - 60) for c in roof), width=2)
        elif kind == "dome":
            r = math.dist(pp[0], (cx, cy))
            for k, f in ((0.75, 18), (0.45, 36)):
                d.ellipse([cx - r * k, cy - r * k, cx + r * k, cy + r * k], fill=tuple(min(255, c + f) for c in roof), outline=(120, 90, 40))
        elif kind == "plot":
            for i in range(len(pp)):
                d.line([pp[i], pp[(i + 1) % len(pp)]], fill=(240, 220, 120), width=2)
            d.line([pp[0], pp[2]], fill=(90, 80, 100), width=1); d.line([pp[1], pp[3]], fill=(90, 80, 100), width=1)
        elif kind == "gate":
            for q in (pp[0], pp[1]):
                d.rectangle([q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6], fill=(120, 120, 120), outline=(40, 40, 40), width=2)
    for poly in HOMES:
        building(poly, random.choice([(150, 92, 60), (122, 150, 80), (170, 120, 70), (110, 130, 96)]), "home")
    for poly in FILLER:
        building(poly, (156, 136, 112), "home")
    for (_, _, poly, roof, kind) in BUILD:
        building(poly, roof, kind)
    # event square: amphitheatre rings + stage
    for r in (10, 14, 18):
        x0, y0 = P(86 - r, 52 - r); x1, y1 = P(86 + r, 52 + r)
        d.arc([x0, y0, x1, y1], 200, 340, fill=(120, 140, 120), width=3)
    d.rectangle([*P(80, 58), *P(92, 64)], fill=(150, 110, 80), outline=(60, 40, 30), width=2)
    # warp ring + home arch + pebble
    cx, cy = P(-24, 44); r = 5 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 80, 90), width=5)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], fill=(120, 220, 230, 140))
    cx, cy = P(26, 44)
    d.arc([cx - 14, cy - 14, cx + 14, cy + 14], 180, 360, fill=(110, 105, 100), width=6)
    cx, cy = P(-8, 50)
    d.polygon([(cx - 9, cy + 6), (cx - 7, cy - 5), (cx + 2, cy - 9), (cx + 9, cy - 2), (cx + 8, cy + 7)], fill=(140, 140, 136), outline=(50, 50, 50))
    # temple (the vanilla prefab placeholder): stepped, mossy, ancient
    t = TEMPLE
    for k, (inset, col) in enumerate(((0, (150, 140, 112)), (4, (170, 160, 128)), (9, (186, 176, 140)), (14, (200, 188, 150)))):
        x0, y0 = P(t[0] + inset, t[1] + inset); x1, y1 = P(t[2] - inset, t[3] - inset)
        if k == 0:
            d.rectangle([x0 + 6, y0 + 7, x1 + 6, y1 + 7], fill=(20, 30, 18, 120))
        d.rectangle([x0, y0, x1, y1], fill=col, outline=(70, 62, 46), width=2)
    for i in range(18):  # moss patches
        x, z = random.uniform(-19, 19), random.uniform(-19, 19)
        cx, cy = P(x, z); r = random.uniform(3, 8)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 130, 70, 120))
    for (x, z) in ((-17, -17), (17, -17), (-17, 17), (17, 17), (-17, 0), (17, 0)):  # pillars
        cx, cy = P(x, z); d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(214, 204, 170), outline=(70, 62, 46), width=2)
    # steps out the south door toward spawn
    for k in range(4):
        x0, y0 = P(-6 + k * 0.0, 20 + k * 1.2); x1, y1 = P(6, 21 + k * 1.2)
        d.rectangle([x0, y0, x1, y1], fill=(206, 196, 160), outline=(110, 100, 80))
    # spawn star
    cx, cy = P(*SPAWN)
    star = [(cx + (11 if i % 2 == 0 else 5) * math.cos(-math.pi / 2 + i * math.pi / 5),
             cy + (11 if i % 2 == 0 else 5) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    d.polygon(star, fill=(255, 170, 30), outline=(90, 50, 0))
    # POI markers (numbered)
    for i, (name, (x, z), col) in enumerate(POI, start=1):
        cx, cy = P(x, z)
        if name.startswith("Spawn"):
            cx, cy = cx + 16, cy + 2
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=col, outline=(20, 20, 20), width=2)
        s = str(i); tw = d.textlength(s, font=fN)
        d.text((cx - tw / 2, cy - 6), s, font=fN, fill=(0, 0, 0) if sum(col) > 400 else (255, 255, 255))
    # building labels (small) + district labels (bold), with halo; avoid overlaps
    placed = []
    def label(text, x, z, font, fill=(255, 255, 255), halo=(30, 30, 30), dy=0):
        cx, cy = P(x, z); cy += dy
        bb = d.textbbox((0, 0), text, font=font); w, h = bb[2] - bb[0], bb[3] - bb[1]
        for nud in (0, -14, 14, -26, 26, -38, 38):
            box = (cx - w / 2 - 2, cy - h / 2 + nud - 2, cx + w / 2 + 2, cy + h / 2 + nud + 3)
            if not any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in placed):
                break
        placed.append(box)
        d.text((box[0] + 2, box[1] + 2), text, font=font, fill=fill, stroke_width=3, stroke_fill=halo)
    for (_, name, poly, _, _) in BUILD:
        if name in ("General", "Forager", "Miner", "Farmer", "North Gate"): continue
        xs = [p[0] for p in poly]; zs = [p[1] for p in poly]
        label(name, sum(xs) / len(xs), min(zs) - 3.5, fSB)
    for (_, name, poly, _, _) in stalls:
        xs = [p[0] for p in poly]; zs = [p[1] for p in poly]
        label(name, sum(xs) / len(xs), max(zs) + 3.5, fS)
    for text, x, z in DISTRICT_LABELS:
        label(text, x, z, fD, fill=(255, 236, 170), halo=(40, 30, 10))
    label("THE VOID", -20, 104, fD, fill=(170, 170, 230), halo=(10, 10, 30))
    label("Department of Arrivals", 0, 8, fSB, fill=(60, 40, 10), halo=(230, 220, 190))
    # frame
    d.rectangle([OX - 2, OY - 2, OX + MW + 2, OY + MH + 2], outline=(220, 210, 170), width=3)
    # title
    d.text((OX, 14), "Zone 1 town v2 - the Department of Arrivals (organic layout)", font=fT, fill=(250, 240, 210))
    # compass + scale
    cx, cy = OX + MW - 40, OY + 46
    d.polygon([(cx, cy - 26), (cx - 9, cy), (cx + 9, cy)], fill=(240, 230, 200), outline=(30, 30, 30))
    d.polygon([(cx, cy + 22), (cx - 9, cy), (cx + 9, cy)], fill=(90, 90, 90), outline=(30, 30, 30))
    d.text((cx - 5, cy - 44), "N", font=fD, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    sx, sy = OX + 20, OY + MH - 26
    for k in range(5):
        d.rectangle([sx + k * 10 * S, sy, sx + (k + 1) * 10 * S, sy + 7], fill=(240, 240, 240) if k % 2 == 0 else (40, 40, 40), outline=(0, 0, 0))
    d.text((sx, sy - 18), "50 blocks = 9 s walk", font=fSB, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    # legend panel
    LX = OX + MW + 16
    d.rectangle([LX - 6, OY - 2, W - 10, H - 12], fill=(42, 48, 40), outline=(220, 210, 170), width=2)
    y = OY + 8
    d.text((LX + 4, y), "Legend", font=fT, fill=(250, 240, 210)); y += 38
    sw = [((196, 190, 168), "plaza (irregular, paved)"), ((196, 178, 140), "road / lane (follows the slope)"),
          ((206, 200, 178), "Promenade (cliff walk)"), ((70, 110, 55), "contour line (2 blocks)"),
          ((122, 112, 132), "reserved plot (sealed)"), ((156, 136, 112), "filler house (future use)"), ((26, 28, 58), "the void")]
    for col, t in sw:
        d.rectangle([LX + 4, y + 2, LX + 24, y + 16], fill=col, outline=(0, 0, 0)); d.text((LX + 32, y), t, font=fL, fill=(235, 235, 225)); y += 22
    d.polygon([(LX + 14, y), (LX + 9, y + 16), (LX + 22, y + 6), (LX + 6, y + 6), (LX + 19, y + 16)], fill=(255, 170, 30))
    d.text((LX + 32, y), "spawn: temple right behind you", font=fL, fill=(235, 235, 225)); y += 26
    d.text((LX + 4, y), "Numbered points", font=fLB, fill=(250, 240, 210)); y += 22
    for i, (name, _, col) in enumerate(POI, start=1):
        d.ellipse([LX + 6, y + 1, LX + 22, y + 17], fill=col, outline=(0, 0, 0), width=1)
        s = str(i); tw = d.textlength(s, font=fN)
        d.text((LX + 14 - tw / 2, y + 3), s, font=fN, fill=(0, 0, 0) if sum(col) > 400 else (255, 255, 255))
        d.text((LX + 32, y + 1), name, font=fL, fill=(235, 235, 225)); y += 21
    y += 6
    d.text((LX + 4, y), "Marker colours", font=fLB, fill=(250, 240, 210)); y += 20
    for col, t in (((220, 40, 60), "NPC (talker)"), ((120, 40, 160), "guard"), ((40, 200, 220), "board / pad / view"), ((255, 140, 0), "portal / door"), ((245, 245, 235), "object")):
        d.ellipse([LX + 8, y + 3, LX + 20, y + 15], fill=col, outline=(0, 0, 0)); d.text((LX + 32, y), t, font=fL, fill=(235, 235, 225)); y += 20
    y += 8
    for line in ["Districts keep their v1 numbers.", "Roads curve with the contours;", "the town grew outward from", "the ancient (vanilla) temple.",
                 "All sizes UNVERIFIED placeholders."]:
        d.text((LX + 4, y), line, font=fS, fill=(200, 200, 185)); y += 17
    img = img.quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    img.save(out, optimize=True)

if __name__ == "__main__":
    draw(sys.argv[1])
    for r in walk_table():
        print(r)
    def area(p): return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2
    for n,(cx,cz,rr,rot) in PLAZAS.items():
        b=blob(cx,cz,rr,rot); xs=[q[0] for q in b]; zs=[q[1] for q in b]
        print('plaza',n,round(area(b)),'span',round(max(xs)-min(xs)),'x',round(max(zs)-min(zs)))
    lim=blob(0,-8,[134,128,126,118,112,120,132,138,136,128,124,130],0.0)
    # clip limit at the coast for area: sample grid
    inside=0
    import itertools
    def pin(x,z,poly):
        c=False
        for i in range(len(poly)):
            (x1,z1),(x2,z2)=poly[i],poly[(i+1)%len(poly)]
            if (z1>z)!=(z2>z) and x < x1+(z-z1)*(x2-x1)/(z2-z1): c=not c
        return c
    for x in range(-150,151):
        for z in range(-150,120):
            if z < coast_z(x) and pin(x,z,lim): inside+=1
    print('town area (limit, land only)', inside)
    for (_,name,poly,_,_) in BUILD: print('bld',name,round(area(poly)))
    print('coast z at x=0', round(coast_z(0),1), 'min/max', round(min(coast_z(x) for x in range(-140,100)),1), round(max(coast_z(x) for x in range(-140,141)),1))
    print('summit road length', round(plen(catmull(ROADS['summit'][0]))))
    print('promenade length', round(plen(catmull(ROADS['promen'][0]))))
