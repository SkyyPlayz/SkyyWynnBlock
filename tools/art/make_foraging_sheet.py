#!/usr/bin/env python3
"""Review sheet for one SkyWynn Foraging armor set (renders the real output files): sheet-<tree>.png
  1 full set on a plain grey test body (front / side / back / 3-4)   2 each piece alone
  3 the 4 inventory icons   4 helmet close-up
Big plain labels (Atkinson Hyperlegible), little text (Skyy is dyslexic).
Usage: python3 make_foraging_sheet.py [art_root] [Tier] [Tree]   (default: art/gathering-armor F1_Grove Oak)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ga_render as R
from make_foraging_icons import piece_faces

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../art/gathering-armor"))
TIER = sys.argv[2] if len(sys.argv) > 2 else "F1_Grove"
TREE = sys.argv[3] if len(sys.argv) > 3 else "Oak"
MODELS = os.path.join(ROOT, "Common/Items/Armors/SkyyForaging", TIER, TREE)
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
    views = [("FRONT", 0, 4), ("SIDE", 90, 4), ("BACK", 180, 4), ("3/4", 35, 10)]
    H = 780
    scale = H * 0.9 / 140.0
    out = []
    for label, yaw, pitch in views:
        V = R.view_matrix(-yaw, pitch)
        c = np.array([0, 66.0, 0]) @ V.T
        img, _ = R.render(faces, texs, yaw=yaw, pitch=pitch, size=H, scale=scale, center=c, ss=2, bg=PANEL)
        out.append((label, img.crop(((H - COLW) // 2, 0, (H - COLW) // 2 + COLW, H))))
    return out


HEADC = np.array([0.0, 112.0, 1.0])


def head_view(models, texs, yaw, pitch, size=COLW, ext=48.0):
    faces = R.set_faces(models)
    V = R.view_matrix(-yaw, pitch)
    img, _ = R.render(faces, texs, yaw=yaw, pitch=pitch, size=size, scale=size / ext, center=HEADC @ V.T,
                      ss=2, bg=PANEL)
    return img


HEAD_VIEWS = [("FRONT", 0, 6), ("3/4", 35, 14), ("SIDE", 90, 6), ("BACK", 180, 10)]


def piece_views(models, texs):
    out = []
    for name, model, tex in zip(PIECES, models, texs):
        faces = piece_faces(name, model)
        img, _ = R.render(faces, [tex], yaw=30, pitch=14, size=COLW, ss=2, bg=PANEL, fill=0.8)
        out.append((name.upper(), img))
    return out


def build_sheet():
    models, texs = R.load_set(MODELS, PIECES)
    full = full_set_views(models, texs)
    alone = piece_views(models, texs)
    icons = [Image.open(os.path.join(ICONS, "Armor_Foraging_%s_%s.png" % (TREE, p))).convert("RGBA") for p in PIECES]

    W = M * 2 + COLW * 4 + GAP * 3
    y_title = M
    y_s1 = y_title + 150
    y_full = y_s1 + 70
    y_s2 = y_full + 780 + 70 + 40
    y_alone = y_s2 + 70
    y_s3 = y_alone + COLW + 70 + 40
    y_icons = y_s3 + 70
    y_s4 = y_icons + 256 + 70 + 50
    y_hd = y_s4 + 70
    Ht = y_hd + COLW + 70 + M
    sheet = Image.new("RGBA", (W, Ht), BG)
    d = ImageDraw.Draw(sheet)

    text(d, (M, y_title), "%s  -  Foraging Armor" % TREE.upper(), 68)
    look = {"Oak": "oak bark + oak leaves", "Birch": "birch bark + birch leaves + catkins", "Beech": "beech wood + beech leaves + beechnut husk", "Ash": "ash wood + ash leaves + seed keys", "Aspen": "aspen wood + golden aspen leaves"}.get(TREE, TREE.lower() + " bark")
    text(d, (M, y_title + 84), "Tier 1: Grove  |  Head, Chest, Hands, Legs  |  " + look, 36, False, SUB)

    def col_x(i):
        return M + i * (COLW + GAP)

    text(d, (M, y_s1), "1.  Full set", 46)
    for i, (label, img) in enumerate(full):
        sheet.paste(img, (col_x(i), y_full))
        text(d, (col_x(i) + COLW // 2, y_full + 780 + 14), label, 42, anchor="ma")

    text(d, (M, y_s2), "2.  Each piece", 46)
    for i, (label, img) in enumerate(alone):
        sheet.paste(img, (col_x(i), y_alone))
        text(d, (col_x(i) + COLW // 2, y_alone + COLW + 14), label, 42, anchor="ma")

    text(d, (M, y_s3), "3.  Icons", 46)
    for i, (p, ic) in enumerate(zip(PIECES, icons)):
        x0 = col_x(i) + (COLW - 256) // 2
        d.rectangle((x0, y_icons, x0 + 255, y_icons + 255), fill=PANEL)
        sheet.alpha_composite(ic.resize((256, 256), Image.NEAREST), (x0, y_icons))
        sheet.alpha_composite(ic, (x0 + 256 + 16, y_icons + 256 - 64))
        text(d, (x0 + 128, y_icons + 256 + 14), p.upper(), 42, anchor="ma")
    text(d, (M, y_icons + 256 + 70), "Small one = real size.", 30, False, SUB)

    text(d, (M, y_s4), "4.  Helmet close-up", 46)
    for i, (label, yaw, pitch) in enumerate(HEAD_VIEWS):
        sheet.paste(head_view(models, texs, yaw, pitch), (col_x(i), y_hd))
        text(d, (col_x(i) + COLW // 2, y_hd + COLW + 14), label, 42, anchor="ma")
    return sheet


if __name__ == "__main__":
    sheet = build_sheet()
    p = os.path.join(ROOT, "sheet-%s.png" % TREE.lower())
    sheet.convert("RGB").save(p, optimize=True)
    print("wrote", p, sheet.size)
