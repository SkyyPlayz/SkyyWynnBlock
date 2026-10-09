"""Player-rig numbers for fitting armor attachments + a plain grey mannequin stand-in for previews.

The bone NAMES, pivots, box offsets and box sizes below are the measured proportions of the Hytale player skeleton
(read from the vanilla Player.blockymodel kept privately on the art box, read-only). They are needed so the armor
attaches to the right bones and fits the body. No vanilla geometry file, texture or pixel is shipped: the mannequin
here is only drawn in our own preview renders, as flat grey boxes.

Units: 64 = 1 block. Character faces +Z. L- = character's left = +X. Ground = y 0.
Attachment rule (Hytale Models plugin 0.10.0, parse(..., {attachment})): an armor node flagged isPiece whose name
matches a player bone is attached to that bone, and its children are positioned relative to the bone's BOX CENTRE
(bone origin + bone shape offset).
"""
import numpy as np
from ga_common import quat_to_mat, mat4

# name, parent, position (rel. parent's origin + parent's shape offset), orientation quat (x,y,z,w), shape offset,
# box size (or None), stretch
BONES = [
    ("Pelvis", None, (0, 51, 0), (0, 0, 0, 1), (0, 0, 0), (26, 12, 18), (0.98, 0.98312, 0.98)),
    ("Belly", "Pelvis", (0, 4, 0), (0, 0, 0, 1), (0, 8, 0), (26, 16, 18), (1, 1, 1)),
    ("Chest", "Belly", (0, 5, -3), (0, 0, 0, 1), (0, 11, 3), (28, 22, 20), (0.98, 0.98, 0.95)),
    ("Head", "Chest", (0, 8, -1), (0, 0, 0, 1), (0, 20, 2), (30, 28, 28), (1, 1, 1)),
    ("Neck", "Head", (0, -16, -1), (0, 0, 0, 1), (0, 3, 0), (15, 13, 11), (1, 1.37788, 1)),
    ("R-Shoulder", "Chest", (-14.50173, 7.59397, -0.93882), (0, 0, 0, 1), (0, 0, 0), None, (1, 1, 1)),
    ("R-Arm", "R-Shoulder", (0, 0, 0), (0.00266, -0.06099, -0.04354, 0.99719), (-1, -8, 0), (8, 20, 12), (0.98, 1, 1)),
    ("R-Forearm", "R-Arm", (0, -10, -1), (0, 0, 0, 1), (0, -8, 1), (8, 16, 12), (1, 1, 1)),
    ("R-Hand", "R-Forearm", (0, -8, 0), (0, 0, 0, 1), (0, -5, 0), (10, 12, 14), (1, 1, 1)),
    ("L-Shoulder", "Chest", (14.50173, 7.59397, -0.93882), (0, 0, 0, 1), (0, 0, 0), None, (1, 1, 1)),
    ("L-Arm", "L-Shoulder", (0, 0, 0), (0.00266, 0.06099, 0.04354, 0.99719), (1, -8, 0), (8, 20, 12), (0.98, 1, 1)),
    ("L-Forearm", "L-Arm", (0, -10, -1), (0, 0, 0, 1), (0, -8, 1), (8, 16, 12), (1, 1, 1)),
    ("L-Hand", "L-Forearm", (0, -8, 0), (0, 0, 0, 1), (0, -5, 0), (10, 12, 14), (1, 1, 1)),
    ("R-Thigh", "Pelvis", (-7.5, -1, 1), (0, -0.0192, 0, 0.99982), (0, -11, 0), (10, 20, 12), (0.98, 1, 1)),
    ("R-Calf", "R-Thigh", (0, -10, 2), (0, 0, 0, 1), (0, -12, -2), (10, 24, 12), (1, 1, 1)),
    ("R-Foot", "R-Calf", (0, -10, -4), (0, 0, 0, 1), (0, -3, 6), (14, 8, 20), (0.95, 0.95, 0.95)),
    ("L-Thigh", "Pelvis", (7.5, -1, 1), (0, 0.0192, 0, 0.99982), (0, -11, 0), (10, 20, 12), (0.98, 1, 1)),
    ("L-Calf", "L-Thigh", (0, -10, 2), (0, 0, 0, 1), (0, -12, -2), (10, 24, 12), (1, 1, 1)),
    ("L-Foot", "L-Calf", (0, -10, -4), (0, 0, 0, 1), (0, -3, 6), (14, 8, 20), (0.95, 0.95, 0.95)),
]
BONE = {b[0]: dict(name=b[0], parent=b[1], pos=b[2], quat=b[3], offset=b[4], size=b[5], stretch=b[6]) for b in BONES}


def bone_matrix(name, pose=None):
    """world matrix of the bone ORIGIN (pivot). pose: optional dict bone -> extra quaternion (local rotation)."""
    b = BONE[name]
    q = b["quat"]
    if pose and name in pose:
        from ga_common import quat_mul
        q = quat_mul(q, pose[name])
    local = mat4(quat_to_mat(q), b["pos"])
    if b["parent"] is None:
        return local
    p = BONE[b["parent"]]
    return bone_matrix(p["name"], pose) @ mat4(None, p["offset"]) @ local


def bone_center_matrix(name, pose=None):
    """world matrix of the bone BOX CENTRE = the frame armor children are placed in."""
    return bone_matrix(name, pose) @ mat4(None, BONE[name]["offset"])


def mannequin_boxes(pose=None):
    """[(name, world matrix of box centre, size*stretch)] for the grey stand-in body."""
    out = []
    for b in BONES:
        if b[5] is None:
            continue
        M = bone_center_matrix(b[0], pose)
        size = np.array(b[5], float) * np.abs(np.array(b[6], float))
        out.append((b[0], M, size))
    return out


if __name__ == "__main__":
    for name, M, size in mannequin_boxes():
        c = M[:3, 3]
        print("%-10s centre (%6.1f %6.1f %6.1f) size %s  y %.1f..%.1f" % (name, *c, size, c[1] - size[1] / 2, c[1] + size[1] / 2))
