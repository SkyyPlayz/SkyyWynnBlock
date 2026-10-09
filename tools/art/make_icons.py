#!/usr/bin/env python3
"""64x64 inventory icons for the Dark Leather set, rendered from the real .blockymodel + _Texture.png files.
Piece alone, 3/4 view from above-left (shows the LEFT pauldron), framing similar to vanilla generated icons
(piece fills ~52-56 px), downsampled 8x with premultiplied-alpha box filtering (soft edges, no dark fringes).
Usage: python3 make_icons.py [out_root]   (default: art/dark-leather-armor)
"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_render as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "../../art/dark-leather-armor"))
MODELS = os.path.join(ROOT, "Common/Items/Armors/SkyyDarkLeather")
ICONS = os.path.join(ROOT, "Common/Icons/ItemsGenerated")
PIECES = ("Head", "Chest", "Hands", "Legs")
YAW, PITCH = 32, 24
BIG, ICON, TARGET = 512, 64, 55          # render size, icon size, longest side of the piece in icon px


def piece_faces(name, model):
    faces = R.armor_faces(model, 0)
    if name == "Hands":
        # bring the two gauntlets together (vanilla icons show the pair side by side), left one set back a bit
        for f in faces:
            if f["name"].startswith("L-"):
                f["P"] = f["P"] + np.array([-25.0, 2.0, -9.0])
    return faces


def downsample_premul(rgba, k):
    a = rgba[..., 3:4] / 255.0
    pm = np.concatenate([rgba[..., :3] * a, a], -1)
    h, w = pm.shape[0] // k, pm.shape[1] // k
    pm = pm[:h * k, :w * k].reshape(h, k, w, k, 4).mean((1, 3))
    al = pm[..., 3:4]
    rgb = np.where(al > 1e-6, pm[..., :3] / np.maximum(al, 1e-6), 0)
    out = np.concatenate([rgb, al * 255.0], -1)
    out[..., 3][out[..., 3] < 6] = 0                       # drop near-invisible dust
    out[..., :3][out[..., 3] == 0] = 0
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def make_icon(name):
    model, tex = R.load_piece(os.path.join(MODELS, name + ".blockymodel"))
    faces = piece_faces(name, model)
    V = R.view_matrix(-YAW, PITCH)
    P = np.concatenate([f["P"] for f in faces]) @ V.T
    ext = (P.max(0) - P.min(0))[:2].max()
    scale = BIG * TARGET / ICON / ext
    img, _ = R.render(faces, [tex], yaw=YAW, pitch=PITCH, size=BIG, scale=scale, ss=1, bg=(0, 0, 0, 0))
    big = np.asarray(img.convert("RGBA"), float)
    return Image.fromarray(downsample_premul(big, BIG // ICON), "RGBA")


if __name__ == "__main__":
    os.makedirs(ICONS, exist_ok=True)
    for p in PIECES:
        im = make_icon(p)
        path = os.path.join(ICONS, "Armor_SkyyDarkLeather_%s.png" % p)
        im.save(path, optimize=True)
        a = np.asarray(im)[..., 3]
        ys, xs = np.nonzero(a)
        print("%-5s %s  bbox x %d-%d y %d-%d" % (p, os.path.relpath(path, ROOT), xs.min(), xs.max(), ys.min(), ys.max()))
