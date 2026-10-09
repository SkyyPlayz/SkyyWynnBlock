#!/usr/bin/env python3
"""Fit / clipping checks for the Dark Leather set at rest pose.
1) OBB-vs-OBB overlap between boxes of DIFFERENT pieces (e.g. helm vs pauldron) - these would clip in game.
2) Body poke-through: renders front / side / back with the mannequin drawn magenta and reports the visible body pixels.
Usage: python3 check_fit.py <model_dir> <out_png>
"""
import itertools, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_render as R
from dl_common import quat_to_mat, mat4
import dl_rig as RIG


def obbs(model, piece):
    out = []
    def walk(node, frame):
        shp = node["shape"]
        if shp.get("settings", {}).get("isPiece"):
            Fm = RIG.bone_center_matrix(node["name"])
            for c in node.get("children", []):
                walk(c, Fm)
            return
        q = tuple(node["orientation"][k] for k in "xyzw")
        M = frame @ mat4(quat_to_mat(q), [node["position"][k] for k in "xyz"])
        off = np.array([shp["offset"][k] for k in "xyz"], float)
        if shp["type"] == "box":
            st = np.abs(np.array([shp["stretch"][k] for k in "xyz"], float))
            sz = shp["settings"]["size"]
            C = M @ mat4(None, off)
            out.append((piece, node["name"], C[:3, 3], C[:3, :3], np.array([sz["x"], sz["y"], sz["z"]]) * st / 2))
        for c in node.get("children", []):
            walk(c, M @ mat4(None, off))
    for n in model["nodes"]:
        walk(n, np.eye(4))
    return out


def obb_overlap(a, b):
    """separating axis test; returns penetration depth (>0 = overlap) along the best axis."""
    ca, Ra, ha = a[2], a[3], a[4]
    cb, Rb, hb = b[2], b[3], b[4]
    axes = [Ra[:, i] for i in range(3)] + [Rb[:, i] for i in range(3)]
    for i in range(3):
        for j in range(3):
            c = np.cross(Ra[:, i], Rb[:, j])
            if np.linalg.norm(c) > 1e-6:
                axes.append(c / np.linalg.norm(c))
    best = 1e9
    d = cb - ca
    for ax in axes:
        ra = sum(ha[i] * abs(Ra[:, i] @ ax) for i in range(3))
        rb = sum(hb[i] * abs(Rb[:, i] @ ax) for i in range(3))
        pen = ra + rb - abs(d @ ax)
        if pen <= 0:
            return 0.0
        best = min(best, pen)
    return best


if __name__ == "__main__":
    d, out = sys.argv[1], sys.argv[2]
    pieces = ("Head", "Chest", "Hands", "Legs")
    models, texs = R.load_set(d, pieces)
    allb = []
    for p, m in zip(pieces, models):
        allb += obbs(m, p)
    print("== cross-piece box overlaps (penetration > 0.05 units)")
    n = 0
    for a, b in itertools.combinations(allb, 2):
        if a[0] == b[0]:
            continue
        pen = obb_overlap(a, b)
        if pen > 0.05:
            n += 1
            print("  %-5s %-16s x %-5s %-16s  %.2f" % (a[0], a[1], b[0], b[1], pen))
    print("  %d overlaps" % n)
    # body pixels
    faces = R.set_faces(models)
    R.BODY_COL[:] = (255, 0, 255)
    W = 520
    sheet = Image.new("RGBA", (W * 3, W), (40, 40, 44, 255))
    for i, yaw in enumerate((0, 90, 180)):
        img, _ = R.render(faces, texs, yaw=yaw, pitch=0, size=W, bg=(40, 40, 44, 255), light=False, ss=1)
        a = np.asarray(img).astype(int)
        mag = (a[..., 0] > 200) & (a[..., 1] < 60) & (a[..., 2] > 200)
        print("view yaw %4d: visible body pixels %d" % (yaw, mag.sum()))
        sheet.paste(img, (i * W, 0))
    sheet.save(out)
