#!/usr/bin/env python3
"""SkyWynn pets: model icons (128), item icons (64), the review sheet and an animation strip - rendered from the REAL files."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pets_render import render, load, collect_faces, view_matrix

ART = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/pets"))
REVIEW = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.normpath(os.path.join(HERE, "../../review"))
ORDER = ["Rabbit", "Chicken", "Goat", "Warthog", "Bear", "Turkey", "Wolf", "Boar", "Hawk", "Ram", "Skrill", "Tusker", "Mouflon", "Horse", "Camel"]
ROLE = {"Rabbit": "Farming", "Chicken": "Farming", "Goat": "Mining", "Warthog": "Mining", "Bear": "Foraging", "Turkey": "Foraging",
        "Wolf": "Combat", "Boar": "Combat", "Hawk": "Archer", "Ram": "Warrior + ride", "Skrill": "Mage", "Tusker": "Berserker",
        "Mouflon": "Priest + ride", "Horse": "Ride", "Camel": "Ride"}
ROLE_COL = {"Farming": (94, 160, 60), "Mining": (120, 120, 140), "Foraging": (150, 100, 50), "Combat": (200, 70, 60),
            "Archer": (90, 170, 80), "Mage": (80, 110, 210), "Berserker": (190, 60, 60), "Warrior": (210, 160, 70),
            "Priest": (220, 190, 90), "Ride": (70, 140, 170)}
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F = lambda s, b=True: ImageFont.truetype(BOLD if b else REG, s)
BG = (234, 238, 242, 255); CARD = (247, 249, 251, 255); INK = (34, 38, 52); SUB = (84, 90, 106)

def pdir(p): return os.path.join(ART, "Common/NPC/SkyyPets", p)
M, T, A = {}, {}, {}
for p in ORDER:
    M[p] = load(os.path.join(pdir(p), "Models", p + ".blockymodel"))
    T[p] = Image.open(os.path.join(pdir(p), "Models", p + "_Texture.png")).convert("RGBA")
    A[p] = {f[:-11]: load(os.path.join(pdir(p), "Animations/Default", f)) for f in sorted(os.listdir(os.path.join(pdir(p), "Animations/Default")))}

def bounds(p, yaw, pitch, anim=None, t=0):
    R = view_matrix(-yaw, pitch)
    P = np.concatenate([f["P"] for f in collect_faces(M[p], anim, t)]) @ R.T
    return P.min(0), P.max(0)

def icon_pose(p):
    return (A[p]["Idle"], 0) if p == "Skrill" else (None, 0)

def make_icon(p, px):
    yaw, pitch = 32, 16
    an, t = icon_pose(p)
    lo, hi = bounds(p, yaw, pitch, an, t)
    S = 512; ext = max(hi[0] - lo[0], hi[1] - lo[1]); scale = (0.84 * S) / ext
    cen = np.array([(lo[0] + hi[0]) / 2, 0, 0.0]); cen[1] = lo[1] + (S / 2 - 0.04 * S) / scale
    if hi[1] - lo[1] < hi[0] - lo[0]:
        cen[1] = (lo[1] + hi[1]) / 2 + 0.06 * S / scale
    big = render(M[p], T[p], yaw=yaw, pitch=pitch, size=S, scale=scale, center=cen, ss=2, anim=an, time=t)
    ic = big.resize((px, px), Image.LANCZOS)
    a = np.asarray(ic).astype(np.float64); a[..., :3] *= a[..., 3:4] / 255.0
    return Image.fromarray(np.round(a).astype(np.uint8), "RGBA")

ICONS = {}
for p in ORDER:
    i128 = make_icon(p, 128); i64 = make_icon(p, 64); ICONS[p] = i128
    for sub, name, im in (("ModelsGenerated", f"SkyyPets_{p}.png", i128), ("ItemsGenerated", f"SkyyPets_Pet_{p}.png", i64)):
        d = os.path.join(ART, "Common/Icons", sub); os.makedirs(d, exist_ok=True); im.save(os.path.join(d, name))

def text_c(d, cx, y, s, f, fill=INK):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)

def view(p, yaw, pitch, size, scale=None, anim=None, t=0):
    lo, hi = bounds(p, yaw, pitch, anim, t)
    ext = max(hi[0] - lo[0], hi[1] - lo[1])
    sc = scale or 0.86 * size / ext
    cen = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0])
    return render(M[p], T[p], yaw=yaw, pitch=pitch, size=size, scale=sc, center=cen, anim=anim, time=t)

def role_tag(d, x, y, role, f):
    key = role.split(" ")[0]; col = ROLE_COL.get(key, (120, 120, 120))
    w = d.textlength(role, font=f)
    d.rounded_rectangle((x, y, x + w + 36, y + f.size + 18), 16, fill=col)
    d.text((x + 18, y + 7), role, font=f, fill=(250, 250, 246))
    return w + 36

# ------------------------------------------------------------------ review sheet
COLS, CW, CH, GAP, MARG = 5, 720, 640, 30, 50
W = MARG * 2 + COLS * CW + (COLS - 1) * GAP
ROSTER_Y, LINE_Y, GRID_Y = 190, 560, 1180
H = GRID_Y + 3 * (CH + GAP) + 90
sheet = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(sheet)
d.text((MARG, 40), "SKYWYNN PETS  v2", font=F(92), fill=INK)
d.text((MARG + 1110, 70), "15 launch pets  -  DRAFT  -  v2: new Horse, Camel, Ram, Mouflon", font=F(50, False), fill=SUB)
# roster strip
d.text((MARG, ROSTER_Y - 10), "ALL 15", font=F(52), fill=INK)
rw = (W - 2 * MARG) / 15
for i, p in enumerate(ORDER):
    x = MARG + i * rw
    d.rounded_rectangle((x + 4, ROSTER_Y + 60, x + rw - 4, ROSTER_Y + 60 + rw + 56), 18, fill=CARD)
    ic = ICONS[p].resize((int(rw - 30), int(rw - 30)), Image.LANCZOS)
    sheet.alpha_composite(ic, (int(x + 15), ROSTER_Y + 70))
    text_c(d, x + rw / 2, ROSTER_Y + 60 + rw - 8, p, F(34))
# size line-up (same scale, side view)
d.text((MARG, LINE_Y), "SIZE  (all at the same scale)", font=F(52), fill=INK)
sc = 4.0; base = LINE_Y + 560
x = MARG + 150
d.line((MARG + 40, base, MARG + 40, base - 64 * sc), fill=(200, 80, 60), width=8)
for yy in (base, base - 64 * sc):
    d.line((MARG + 20, yy, MARG + 60, yy), fill=(200, 80, 60), width=8)
d.text((MARG + 66, base - 64 * sc - 4), "1 block", font=F(36), fill=(200, 80, 60))
for p in ORDER:
    lo, hi = bounds(p, -90, 0)
    wpx = int((hi[0] - lo[0]) * sc) + 8
    hpx = int((hi[1] - lo[1]) * sc) + 8
    S = max(wpx, hpx) + 20
    cen = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0])
    im = render(M[p], T[p], yaw=-90, pitch=0, size=S, scale=sc, center=cen)
    groundy = lo[1]
    top = int(base - (cen[1] - groundy) * sc - S / 2)
    sheet.alpha_composite(im, (int(x - (S - wpx) / 2), top))
    x += wpx + 10
d.line((MARG, base + 2, W - MARG, base + 2), fill=(170, 176, 186), width=4)
# cards
for i, p in enumerate(ORDER):
    cx = MARG + (i % COLS) * (CW + GAP); cy = GRID_Y + (i // COLS) * (CH + GAP)
    d.rounded_rectangle((cx, cy, cx + CW, cy + CH), 26, fill=CARD)
    d.text((cx + 26, cy + 18), f"{i + 1}. {p.upper()}", font=F(54), fill=INK)
    role_tag(d, cx + 26, cy + 92, ROLE[p], F(30))
    hero = view(p, 32, 16, 420, anim=icon_pose(p)[0])
    sheet.alpha_composite(hero, (cx + 0, cy + 150))
    for j, (lab, yaw, pitch) in enumerate((("FRONT", 0, 6), ("SIDE", -90, 4), ("BACK", 180, 8))):
        sy = cy + 30 + j * 200
        sheet.alpha_composite(view(p, yaw, pitch, 170, anim=icon_pose(p)[0]), (cx + CW - 210, sy))
        text_c(d, cx + CW - 125, sy + 166, lab, F(26), SUB)
sheet.convert("RGB").save(os.path.join(REVIEW, "pets-v2.png"))
sheet.convert("RGB").save(os.path.join(ART, "sheet.png"))

# ------------------------------------------------------------------ animation strip (one row per pet)
FR = 230
rows = []
for p in ORDER:
    names = list(A[p].keys())
    frames = []
    for an in ("Idle", "Walk", "Run", "Fly"):
        if an not in A[p]: continue
        D = A[p][an]["duration"]
        ts = [0, D // 4, D // 2] if an != "Idle" else [0, D // 4]
        frames += [(an, t) for t in ts]
    rows.append((p, frames))
maxf = max(len(f) for _, f in rows)
AW = 300 + maxf * FR + 40; AH = len(rows) * (FR + 20) + 120
strip = Image.new("RGBA", (AW, AH), BG); ds = ImageDraw.Draw(strip)
ds.text((30, 24), "PET ANIMATIONS  (frames from the real .blockyanim files)", font=F(56), fill=INK)
for r, (p, frames) in enumerate(rows):
    y = 110 + r * (FR + 20)
    ds.text((30, y + FR / 2 - 30), p.upper(), font=F(44), fill=INK)
    lo, hi = bounds(p, -30, 14)
    ext = max(hi[0] - lo[0], hi[1] - lo[1]) * 1.25; sc2 = 0.9 * FR / ext
    cen = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2 + 2, 0])
    prev = None
    for c, (an, t) in enumerate(frames):
        x = 300 + c * FR
        ds.rounded_rectangle((x + 4, y, x + FR - 4, y + FR), 16, fill=CARD)
        strip.alpha_composite(render(M[p], T[p], yaw=-30, pitch=14, size=FR, scale=sc2, center=cen, anim=A[p][an], time=t), (x, y))
        if an != prev:
            ds.text((x + 14, y + 8), an.upper(), font=F(30), fill=(200, 80, 60))
        prev = an
strip.convert("RGB").save(os.path.join(REVIEW, "pets-v2-animations.png"))
print("previews done")
