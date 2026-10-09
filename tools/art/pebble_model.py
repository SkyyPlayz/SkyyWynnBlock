"""Pebble (SkyWynn talking rock NPC) - geometry definition.

All numbers are Hytale character units (64 units = 1 block, 1 unit = 1 texel; UVs are locked to face size).
Character faces +Z.  R- = character's right = -X (vanilla convention).  Ground = y 0.
Every node below is ORIGINAL geometry (no vanilla data used).
"""

# name, parent, pivot (world xyz at rest), rest euler deg (x,y,z, ZYX order), shape
# shape: None (empty node) | ("box", size(w,h,d), offset(local xyz)) | ("quad", size(w,h), offset)
# extra: mirror_of=<node> -> reuse that node's texture regions mirrored on X; share_of=<node> -> reuse unmirrored
NODES = [
    dict(name="Origin", parent=None, pivot=(0, 0, 0), shape=None),
    # main rock mass, pivot near the ground so the whole rock rolls when it waddles
    dict(name="Body", parent="Origin", pivot=(0, 4, 0), shape=("box", (44, 16, 42), (0, 11, 0))),         # y 7..23, z -21..21
    dict(name="Body-Wide", parent="Body", pivot=(0, 15, -1), shape=("box", (50, 14, 32), (0, 0, 0))),      # cross-stack = rounded corners
    dict(name="Body-Base", parent="Body", pivot=(0, 7, 0), shape=("box", (36, 4, 30), (0, 0, 0))),         # y 5..9
    dict(name="L-Foot", parent="Body", pivot=(11, 7, 8), shape=("box", (14, 7, 18), (0, -3.5, 0))),        # y 0..7, front z 17
    dict(name="R-Foot", parent="Body", pivot=(-11, 7, 8), shape=("box", (14, 7, 18), (0, -3.5, 0)), mirror_of="L-Foot"),
    dict(name="L-Arm", parent="Body", pivot=(26, 20, 1), shape=("box", (8, 10, 9), (0.5, -4.5, 0))),
    dict(name="R-Arm", parent="Body", pivot=(-26, 20, 1), shape=("box", (8, 10, 9), (-0.5, -4.5, 0)), mirror_of="L-Arm"),
    # Head = the upper half of the rock, carries the face. Nameplate / chat bubble node.
    dict(name="Head", parent="Body", pivot=(0, 21, 0), shape=("box", (46, 23, 44), (0, 11.5, 0))),         # y 21..44, front z 22 (face)
    dict(name="Head-Wide", parent="Head", pivot=(0, 32.5, -1), shape=("box", (52, 21, 34), (0, 0, 0))),    # y 22..43
    dict(name="Head-Bulge", parent="Head", pivot=(0, 32.5, -1), shape=("box", (56, 13, 26), (0, 0, 0))),   # y 26..39
    dict(name="Head-Top", parent="Head", pivot=(-1, 45.5, -1), shape=("box", (40, 5, 34), (0, 0, 0))),     # y 43..48
    dict(name="Crown", parent="Head-Top", pivot=(-2, 49, -2), shape=("box", (28, 4, 24), (0, 0, 0))),      # y 47..51
    dict(name="Moss-Cap", parent="Crown", pivot=(-5, 51.5, -4), shape=("box", (18, 3, 16), (0, 0, 0))),    # y 50..53
    dict(name="Moss-Tuft", parent="Crown", pivot=(8, 51, 5), shape=("box", (9, 2, 8), (0, 0, 0))),         # y 50..52
    dict(name="Sprout", parent="Moss-Cap", pivot=(-3, 52.5, -3), shape=("box", (2, 7, 2), (0, 3.5, 0))),   # stem y 52.5..59.5
    dict(name="Sprout-Leaf-L", parent="Sprout", pivot=(-2, 59, -3), rot=(0, 0, 28), shape=("box", (7, 2, 4), (3.5, 0, 0))),
    dict(name="Sprout-Leaf-R", parent="Sprout", pivot=(-4, 59, -3), rot=(0, 0, -28), shape=("box", (7, 2, 4), (-3.5, 0, 0)), mirror_of="Sprout-Leaf-L"),
    # face: dot eyes + blink lids (vanilla-style stretched quads), smile, moss eyebrows
    dict(name="L-Eye", parent="Head", pivot=(10, 33, 22.1), shape=("quad", (5, 6), (0, 0, 0))),
    dict(name="R-Eye", parent="Head", pivot=(-10, 33, 22.1), shape=("quad", (5, 6), (0, 0, 0)), share_of="L-Eye"),
    dict(name="L-Eyelid", parent="Head", pivot=(10, 36.3, 22.2), shape=("quad", (5, 6), (0, 0, 0)), stretch=(1, 0.1, 1)),
    dict(name="R-Eyelid", parent="Head", pivot=(-10, 36.3, 22.2), shape=("quad", (5, 6), (0, 0, 0)), stretch=(1, 0.1, 1), share_of="L-Eyelid"),
    dict(name="Mouth", parent="Head", pivot=(0, 27, 22.1), shape=("quad", (10, 3), (0, 0, 0))),
    dict(name="L-Brow", parent="Head", pivot=(10, 39, 22.4), shape=("box", (7, 2, 2), (0, 0, 0))),
    dict(name="R-Brow", parent="Head", pivot=(-10, 39, 22.4), shape=("box", (7, 2, 2), (0, 0, 0)), mirror_of="L-Brow"),
]

# faces that are always buried inside another box reuse another face's pixels (saves texture space)
SHARED_FACES = {
    ("Body", "top"): ("Body", "bottom"),
    ("Body-Base", "top"): ("Body-Base", "bottom"),
    ("Body-Wide", "top"): ("Body-Wide", "bottom"),
    ("Head-Wide", "bottom"): ("Head-Wide", "top"),
    ("Head-Bulge", "bottom"): ("Head-Bulge", "top"),
    ("Crown", "bottom"): ("Crown", "top"),
    ("Moss-Cap", "bottom"): ("Moss-Cap", "top"),
    ("Moss-Tuft", "bottom"): ("Moss-Tuft", "top"),
    ("Sprout", "bottom"): ("Sprout", "top"),
}
