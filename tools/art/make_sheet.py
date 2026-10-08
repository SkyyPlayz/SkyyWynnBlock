#!/usr/bin/env python3
"""Review sheet for the Dark Leather set (renders the real output files).
  sheet.png            - full set on a plain grey test body (front / side / back / 3-4), each piece alone, the 4 icons
  sheet_with_refs.png  - the same + small labelled crops of Skyy's 3 reference images (LOCAL ONLY - never commit)
Big plain labels (Atkinson Hyperlegible), plain background, no clutter.
Usage: python3 make_sheet.py [art_root] [refs_dir]
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_render as R
from make_icons import piece_faces

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../art/dark-leather-armor"))
REFS = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "../../refs"))
# previous versions, for the before/after rows of sheet_with_refs.png only (local work/ dirs)
BEFORE = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else
                         os.path.join(HERE, "../../work/before_v12/Common/Items/Armors/SkyyDarkLeather"))
BEFORE_WRAP = os.path.abspath(sys.argv[4] if len(sys.argv) > 4 else
                              os.path.join(HERE, "../../work/before_v13/Common/Items/Armors/SkyyDarkLeather"))
MODELS = os.path.join(ROOT, "Common/Items/Armors/SkyyDarkLeather")
ICONS = os.path.join(ROOT, "Common/Icons/ItemsGenerated")
PIECES = ("Head", "Chest", "Hands", "Legs")

FONT_DIR = "/usr/share/fonts/truetype/sand-box/google/Atkinson Hyperlegible/"
def font(sz, bold=True):
    try:
        return ImageFont.truetype(FONT_DIR + ("AtkinsonHyperlegible-Bold.ttf" if bold else "AtkinsonHyperlegible-Regular.ttf"), sz)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), sz)

BG = (238, 238, 240, 255)
PANEL = (226, 226, 229, 255)
INK = (28, 28, 34)
SUB = (70, 70, 80)
M, GAP = 60, 30
COLW = 540


def text(d, xy, s, sz, bold=True, fill=INK, anchor="la"):
    d.text(xy, s, font=font(sz, bold), fill=fill, anchor=anchor)


def full_set_views(models, texs):
    faces = R.set_faces(models)
    views = [("FRONT", 0, 4), ("SIDE (left)", 90, 4), ("BACK", 180, 4), ("3/4 VIEW", 35, 10)]
    H = 780
    scale = H * 0.9 / 132.0
    out = []
    for label, yaw, pitch in views:
        V = R.view_matrix(-yaw, pitch)
        c = np.array([0, 63.0, 0]) @ V.T
        img, _ = R.render(faces, texs, yaw=yaw, pitch=pitch, size=H, scale=scale, center=c, ss=2, bg=PANEL)
        out.append((label, img.crop(((H - COLW) // 2, 0, (H - COLW) // 2 + COLW, H))))
    return out


SHOULDER = np.array([20.0, 84.5, -1.5])     # world centre of the LEFT pauldron (close-up framing)


def shoulder_view(models, texs, yaw, pitch, size=COLW, ext=36.0):
    faces = R.set_faces(models)
    V = R.view_matrix(-yaw, pitch)
    img, _ = R.render(faces, texs, yaw=yaw, pitch=pitch, size=size, scale=size / ext, center=SHOULDER @ V.T,
                      ss=2, bg=PANEL)
    return img


SHOULDER_VIEWS = [("FRONT", 0, 6), ("SIDE (left)", 90, 6), ("BACK", 180, 6), ("3/4 VIEW", 40, 16)]


def piece_views(models, texs):
    out = []
    S = COLW
    for name, model, tex in zip(PIECES, models, texs):
        faces = piece_faces(name, model)
        img, _ = R.render(faces, [tex], yaw=30, pitch=14, size=S, ss=2, bg=PANEL, fill=0.8)
        out.append((name.upper(), img))
    return out


def build_sheet():
    models, texs = R.load_set(MODELS, PIECES)
    full = full_set_views(models, texs)
    alone = piece_views(models, texs)
    icons = [Image.open(os.path.join(ICONS, "Armor_SkyyDarkLeather_%s.png" % p)).convert("RGBA") for p in PIECES]

    W = M * 2 + COLW * 4 + GAP * 3
    y_title = M
    y_s1 = y_title + 150
    y_full = y_s1 + 70
    y_s2 = y_full + 780 + 70 + 40
    y_alone = y_s2 + 70
    y_s3 = y_alone + COLW + 70 + 40
    y_icons = y_s3 + 70
    y_s4 = y_icons + 256 + 70 + 50
    y_sh = y_s4 + 70
    Ht = y_sh + COLW + 70 + M
    sheet = Image.new("RGBA", (W, Ht), BG)
    d = ImageDraw.Draw(sheet)

    text(d, (M, y_title), "Dark Leather Light Armor", 68)
    text(d, (M, y_title + 84), "SkyWynn  |  light armor  |  4 pieces: Head, Chest, Hands, Legs  |  one shoulder plate (LEFT)", 36, False, SUB)

    def section(y, s):
        text(d, (M, y), s, 46)

    def col_x(i):
        return M + i * (COLW + GAP)

    section(y_s1, "1.  Full set, on a plain grey test body")
    for i, (label, img) in enumerate(full):
        sheet.paste(img, (col_x(i), y_full))
        text(d, (col_x(i) + COLW // 2, y_full + 780 + 14), label, 42, anchor="ma")

    section(y_s2, "2.  Each piece on its own")
    for i, (label, img) in enumerate(alone):
        sheet.paste(img, (col_x(i), y_alone))
        text(d, (col_x(i) + COLW // 2, y_alone + COLW + 14), label, 42, anchor="ma")

    section(y_s3, "3.  Inventory icons (64 x 64, shown 4x bigger)")
    for i, (p, ic) in enumerate(zip(PIECES, icons)):
        x0 = col_x(i) + (COLW - 256) // 2
        d.rectangle((x0, y_icons, x0 + 255, y_icons + 255), fill=PANEL)
        sheet.alpha_composite(ic.resize((256, 256), Image.NEAREST), (x0, y_icons))
        sheet.alpha_composite(ic, (x0 + 256 + 16, y_icons + 256 - 64))      # real size
        text(d, (x0 + 128, y_icons + 256 + 14), p.upper(), 42, anchor="ma")
    text(d, (M, y_icons + 256 + 70), "Small picture next to each icon = real size.", 30, False, SUB)

    section(y_s4, "4.  Left shoulder pad close-up (wraps the front and back of the shoulder)")
    for i, (label, yaw, pitch) in enumerate(SHOULDER_VIEWS):
        sheet.paste(shoulder_view(models, texs, yaw, pitch), (col_x(i), y_sh))
        text(d, (col_x(i) + COLW // 2, y_sh + COLW + 14), label, 42, anchor="ma")
    return sheet


def add_refs(sheet):
    refs = [("1_dark_armor_outfit.jpg", None, "Ref 1: the look"),
            ("2_armor_types_chart_half_plate.jpg", (397, 268, 592, 530), "Ref 2: half plate"),
            ("3_helmet_style.jpg", None, "Ref 3: helmet")]
    RW = 520
    W = sheet.width + RW + M
    out = Image.new("RGBA", (W, sheet.height), BG)
    out.alpha_composite(sheet, (0, 0))
    d = ImageDraw.Draw(out)
    x0 = sheet.width
    text(d, (x0, M), "Skyy's refs", 52)
    text(d, (x0, M + 66), "local only, not in repo", 30, False, SUB)
    y = M + 150
    avail = sheet.height - y - M
    per = avail // 3
    for fn, box, label in refs:
        im = Image.open(os.path.join(REFS, fn)).convert("RGBA")
        if box:
            im = im.crop(box)
        h = per - 70
        s = min(RW / im.width, h / im.height)
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        out.alpha_composite(im, (x0, y))
        text(d, (x0, y + im.height + 10), label, 40)
        y += per
    return out


def add_before_after(img):
    """bottom row: old (heavy) vs new (light) full set, front + 3/4, same scale."""
    H = 700
    out = Image.new("RGBA", (img.width, img.height + H + 190), BG)
    out.alpha_composite(img, (0, 0))
    d = ImageDraw.Draw(out)
    y0 = img.height + 20
    text(d, (M, y0), "5.  Round 2 before vs after  (Skyy: make it slimmer, like light armor)", 46)
    cols = [("BEFORE  front", BEFORE, 0, 4), ("BEFORE  3/4", BEFORE, 35, 10),
            ("AFTER  front", MODELS, 0, 4), ("AFTER  3/4", MODELS, 35, 10)]
    scale = H * 0.9 / 140.0
    for i, (label, md, yaw, pitch) in enumerate(cols):
        models, texs = R.load_set(md, PIECES)
        faces = R.set_faces(models)
        V = R.view_matrix(-yaw, pitch)
        c = np.array([0, 66.0, 0]) @ V.T
        im, _ = R.render(faces, texs, yaw=yaw, pitch=pitch, size=H, scale=scale, center=c, ss=2, bg=PANEL)
        x = M + i * (COLW + GAP)
        out.paste(im.crop(((H - COLW) // 2, 0, (H - COLW) // 2 + COLW, H)), (x, y0 + 70))
        text(d, (x + COLW // 2, y0 + 70 + H + 14), label, 42, anchor="ma")
    return out


def add_wrap_before_after(img):
    """bottom row: LEFT shoulder before vs after the wrap (round 3), front 3/4 and back 3/4 close-ups."""
    S = COLW
    out = Image.new("RGBA", (img.width, img.height + S + 190), BG)
    out.alpha_composite(img, (0, 0))
    d = ImageDraw.Draw(out)
    y0 = img.height + 20
    text(d, (M, y0), "6.  Round 3 shoulder before vs after  (Skyy asked: shoulder pad wraps around the shoulder a little)", 46)
    cols = [("BEFORE  3/4 front", BEFORE_WRAP, 40, 16), ("AFTER  3/4 front", MODELS, 40, 16),
            ("BEFORE  3/4 back", BEFORE_WRAP, 140, 16), ("AFTER  3/4 back", MODELS, 140, 16)]
    for i, (label, md, yaw, pitch) in enumerate(cols):
        models, texs = R.load_set(md, PIECES)
        x = M + i * (COLW + GAP)
        out.paste(shoulder_view(models, texs, yaw, pitch), (x, y0 + 70))
        text(d, (x + COLW // 2, y0 + 70 + S + 14), label, 42, anchor="ma")
    return out


if __name__ == "__main__":
    sheet = build_sheet()
    p = os.path.join(ROOT, "sheet.png")
    sheet.convert("RGB").save(p, optimize=True)
    print("wrote", p, sheet.size)
    refs_out = os.path.join(ROOT, "sheet_with_refs.png")
    if os.path.isdir(REFS):
        r = add_refs(sheet)
        if os.path.isdir(BEFORE):
            r = add_before_after(r)
        if os.path.isdir(BEFORE_WRAP):
            r = add_wrap_before_after(r)
        r.convert("RGB").save(refs_out, optimize=True)
        print("wrote", refs_out, r.size, "(LOCAL ONLY - contains Skyy's refs)")
