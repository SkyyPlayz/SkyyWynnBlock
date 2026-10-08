#!/usr/bin/env python3
"""Pebble: model icon (128x128), review sheet and extra preview PNGs, rendered from the REAL exported files."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from render_blocky import render, load, collect_faces

ART = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "../../art/pebble"))
PREV = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.normpath(os.path.join(HERE, "../../previews"))
NPC = os.path.join(ART, "Common/NPC/SkyyTowns/Pebble")
model = load(os.path.join(NPC, "Pebble.blockymodel"))
tex = Image.open(os.path.join(NPC, "Pebble_Texture.png")).convert("RGBA")
anims = {n: load(os.path.join(NPC, "Animations", f, n + ".blockyanim")) for f, n in
         [("Default", "Idle"), ("Default", "Walk"), ("Default", "Talk"), ("Default", "Wave"), ("Damage", "Hurt"), ("Damage", "Death")]}
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG = (232, 236, 240, 255); INK = (34, 38, 52); SUB = (70, 76, 92)
font = lambda s, b=True: ImageFont.truetype(BOLD if b else REG, s)
os.makedirs(PREV, exist_ok=True)

def bounds(yaw, pitch, anim=None, t=0):
    from render_blocky import view_matrix
    R = view_matrix(-yaw, pitch)
    P = np.concatenate([f["P"] for f in collect_faces(model, anim, t)]) @ R.T
    return P.min(0), P.max(0)

# ------------------------------------------------------------------ icon (vanilla model-icon framing: 3/4 view, bottom-anchored)
def make_icon():
    yaw, pitch = 32, 16
    lo, hi = bounds(yaw, pitch)
    S = 512
    ext = max(hi[0] - lo[0], hi[1] - lo[1])
    scale = (106 / 128 * S) / ext
    cen = np.array([(lo[0] + hi[0]) / 2, 0, 0.0])
    # bottom of the model 4 px above the icon's bottom edge
    cen[1] = lo[1] + (S / 2 - 4 / 128 * S) / scale
    big = render(model, tex, yaw=yaw, pitch=pitch, size=S, scale=scale, center=cen, ss=2)
    icon = big.resize((128, 128), Image.LANCZOS)
    a = np.asarray(icon).astype(np.float64)
    a[..., :3] *= a[..., 3:4] / 255.0                                        # premultiplied alpha edges (like vanilla icons)
    icon = Image.fromarray(np.round(a).astype(np.uint8), "RGBA")
    p = os.path.join(ART, "Common/Icons/ModelsGenerated/Pebble.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    icon.save(p)
    return icon

def text_c(d, xy, s, f, fill=INK):
    w = d.textlength(s, font=f); d.text((xy[0] - w / 2, xy[1]), s, font=f, fill=fill)

# ------------------------------------------------------------------ review sheet
def make_sheet(icon):
    W, H = 2400, 1640
    sheet = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(sheet)
    d.text((60, 36), "PEBBLE  -  the talking rock", font=font(72), fill=INK)
    d.text((62, 128), "About 1 block tall (knee to hip on a player).  Texture 256 x 192.  25 nodes.", font=font(38, False), fill=SUB)
    # row 1: views share one scale so sizes compare
    cell = 520; scale = 7.4
    views = [("FRONT", 0, 6), ("SIDE", 90, 4), ("BACK", 180, 6)]
    y0 = 210
    for i, (label, yaw, pitch) in enumerate(views):
        lo, hi = bounds(yaw, pitch)
        cen = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0])
        im = render(model, tex, yaw=yaw, pitch=pitch, size=cell, scale=scale * cell / 520 * 0.92, center=cen)
        x = 60 + i * (cell + 40)
        d.rounded_rectangle((x, y0, x + cell, y0 + cell), 24, fill=(246, 248, 250, 255))
        sheet.alpha_composite(im, (x, y0))
        text_c(d, (x + cell / 2, y0 + cell + 12), label, font(56))
    # 1-block ruler next to FRONT
    lo, hi = bounds(0, 6)
    px_per_unit = scale * 0.92
    base_y = y0 + cell / 2 + (hi[1] - lo[1]) / 2 * px_per_unit
    top_y = base_y - 64 * px_per_unit
    rx = 60 + cell - 34
    d.line((rx, base_y, rx, top_y), fill=(200, 80, 60), width=6)
    d.line((rx - 14, base_y, rx + 14, base_y), fill=(200, 80, 60), width=6)
    d.line((rx - 14, top_y, rx + 14, top_y), fill=(200, 80, 60), width=6)
    d.text((rx - 150, top_y - 46), "1 block", font=font(36), fill=(200, 80, 60))
    # icon
    x = 60 + 3 * (cell + 40)
    d.rounded_rectangle((x, y0, x + cell, y0 + cell), 24, fill=(246, 248, 250, 255))
    big = icon.resize((384, 384), Image.NEAREST)
    sheet.alpha_composite(big, (x + (cell - 384) // 2, y0 + (cell - 384) // 2))
    text_c(d, (x + cell / 2, y0 + cell + 12), "ICON", font(56))
    # row 2: one frame per animation, same scale + framing
    frames = [("IDLE", "Idle", 131, "blink"), ("WALK", "Walk", 0, "waddle"), ("TALK", "Talk", 6, "mouth open"),
              ("WAVE", "Wave", 28, "arm wave + hop"), ("HURT", "Hurt", 4, "wince"), ("DEATH", "Death", 40, "crumbles, pops back")]
    fc = 360; y1 = 880; yaw = -28; pitch = 14
    lo, hi = bounds(yaw, pitch)
    cen = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2 + 4, 0])
    for i, (label, an, t, note) in enumerate(frames):
        flo, fhi = bounds(yaw, pitch, anims[an], t)
        sc = min(4.3, 0.9 * fc / (fhi[0] - flo[0]))
        fcen = np.array([(flo[0] + fhi[0]) / 2, cen[1], 0])
        im = render(model, tex, yaw=yaw, pitch=pitch, size=fc, anim=anims[an], time=t, scale=sc, center=fcen)
        x = 60 + i * (fc + 28)
        d.rounded_rectangle((x, y1, x + fc, y1 + fc), 22, fill=(246, 248, 250, 255))
        sheet.alpha_composite(im, (x, y1))
        text_c(d, (x + fc / 2, y1 + fc + 12), label, font(52))
        text_c(d, (x + fc / 2, y1 + fc + 78), note, font(32, False), SUB)
    d.text((60, H - 70), "Preview renders of the real files (lighting approximate). Original art for SkyWynn.", font=font(30, False), fill=SUB)
    sheet.convert("RGB").save(os.path.join(ART, "sheet.png"))

# ------------------------------------------------------------------ extra previews
def make_turnaround():
    W = Image.new("RGBA", (6 * 400, 470), BG); d = ImageDraw.Draw(W)
    for i, (lab, yaw, pitch) in enumerate([("FRONT", 0, 8), ("3/4 LEFT", 35, 16), ("LEFT SIDE", 90, 5), ("BACK", 180, 8), ("3/4 RIGHT", -35, 16), ("TOP", 0, 70)]):
        W.alpha_composite(render(model, tex, yaw=yaw, pitch=pitch, size=400, scale=4.6), (i * 400, 0))
        text_c(d, (i * 400 + 200, 405), lab, font(44))
    W.convert("RGB").save(os.path.join(PREV, "Pebble_turnaround.png"))

def make_anim_strips():
    rows = [("IDLE (3.0 s loop)", "Idle", [0, 45, 90, 131, 135]), ("WALK (0.67 s loop)", "Walk", [0, 10, 20, 30]),
            ("TALK (0.67 s loop)", "Talk", [0, 6, 13, 20, 33]), ("WAVE (1.07 s)", "Wave", [0, 5, 13, 28, 44]),
            ("HURT (0.4 s)", "Hurt", [0, 4, 10, 18]), ("DEATH (1.6 s, holds last)", "Death", [0, 12, 40, 66, 74, 95])]
    S = 300; yaw, pitch = -28, 14
    lo, hi = bounds(yaw, pitch)
    cen = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2 + 6, 0])
    W = Image.new("RGBA", (6 * S + 40, len(rows) * (S + 70) + 20), BG); d = ImageDraw.Draw(W)
    for r, (lab, an, ts) in enumerate(rows):
        y = 10 + r * (S + 70)
        d.text((20, y), lab, font=font(40), fill=INK)
        for c, t in enumerate(ts):
            flo, fhi = bounds(yaw, pitch, anims[an], t)
            fcen = np.array([(flo[0] + fhi[0]) / 2, cen[1], 0])
            W.alpha_composite(render(model, tex, yaw=yaw, pitch=pitch, size=S, anim=anims[an], time=t, scale=min(3.2, 0.9 * S / (fhi[0] - flo[0])), center=fcen), (20 + c * S, y + 56))
            d.text((30 + c * S, y + 56 + S - 40), f"frame {t}", font=font(26, False), fill=SUB)
    W.convert("RGB").save(os.path.join(PREV, "Pebble_animation_frames.png"))

def make_texture_view():
    t = tex
    k = 4
    chk = Image.new("RGBA", (t.width * k, t.height * k), (255, 255, 255, 255)); d = ImageDraw.Draw(chk)
    for y in range(0, chk.height, 16):
        for x in range(0, chk.width, 16):
            if (x // 16 + y // 16) % 2: d.rectangle((x, y, x + 15, y + 15), fill=(220, 220, 224, 255))
    chk.alpha_composite(t.resize(chk.size, Image.NEAREST))
    chk.convert("RGB").save(os.path.join(PREV, "Pebble_texture_x4.png"))

def make_hero():
    W = Image.new("RGBA", (1400, 700), BG)
    W.alpha_composite(render(model, tex, yaw=30, pitch=15, size=700), (0, 0))
    W.alpha_composite(render(model, tex, yaw=-150, pitch=22, size=700), (700, 0))
    W.convert("RGB").save(os.path.join(PREV, "Pebble_hero.png"))

icon = make_icon()
make_sheet(icon)
make_turnaround(); make_anim_strips(); make_texture_view(); make_hero()
print("previews done")
