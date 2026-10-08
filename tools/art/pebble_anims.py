"""Pebble animations (.blockyanim, 60 fps time units, deltas relative to the rest pose).

Channels per node like vanilla: position (delta units, parent space), orientation (delta quaternion),
shapeStretch (multiplies the model stretch), shapeVisible, shapeUvOffset.
Keys are written < duration; Hytale/Blockbench wrap the loop from the last key back to the first.
"""
import json, math, os
from pebble_common import quat_from_euler_zyx, r6

FOOT_X, FOOT_Y_REL, FOOT_BOTTOM_REL = 11.0, 3.0, -4.0   # foot pivot / bottom relative to Body pivot (y=4)

def K(t, v, interp="smooth"):
    return (t, v, interp)

def build(duration, hold, tracks):
    out = {}
    for node, ch in tracks.items():
        nd = {"position": [], "orientation": [], "shapeStretch": [], "shapeVisible": [], "shapeUvOffset": []}
        for (t, v, it) in ch.get("pos", []):
            nd["position"].append({"time": t, "delta": {"x": r6(v[0]), "y": r6(v[1]), "z": r6(v[2])}, "interpolationType": it})
        for (t, v, it) in ch.get("rot", []):
            q = quat_from_euler_zyx(*v)
            nd["orientation"].append({"time": t, "delta": {"x": r6(q[0]), "y": r6(q[1]), "z": r6(q[2]), "w": r6(q[3])}, "interpolationType": it})
        for (t, v, it) in ch.get("scale", []):
            nd["shapeStretch"].append({"time": t, "delta": {"x": r6(v[0]), "y": r6(v[1]), "z": r6(v[2])}, "interpolationType": it})
        for (t, v, it) in ch.get("vis", []):
            nd["shapeVisible"].append({"time": t, "delta": bool(v), "interpolationType": it})
        for k in nd:
            assert all(kf["time"] < duration for kf in nd[k]), (node, k)
            nd[k].sort(key=lambda kf: kf["time"])
        out[node] = nd
    return {"formatVersion": 1, "duration": duration, "holdLastKeyframe": hold, "nodeAnimations": out}

def blink(t0, close=3, opened=6):
    """eyelid keys: vanilla trick - lid quad is stretched to 0.1 at rest, x10 + slide down to close"""
    return {"pos": [K(t0, (0, 0, 0)), K(t0 + close, (0, -3.3, 0)), K(t0 + close + opened - 3, (0, 0, 0))],
            "scale": [K(t0, (1, 1, 1)), K(t0 + close, (1, 10, 1)), K(t0 + close + opened - 3, (1, 1, 1))]}

# --------------------------------------------------------------------------------------------- Idle
def idle():
    D = 180
    lids = blink(128, 4, 9)
    return D, False, {
        "Head": {"pos": [K(0, (0, 0, 0)), K(90, (0, 0.8, 0))],
                 "rot": [K(0, (0, 0, 0)), K(45, (0, 0, 1.6)), K(90, (0, 0, 0)), K(135, (0, 0, -1.6))]},
        "Body": {"rot": [K(0, (0, 0, 0)), K(45, (0, 0, -0.7)), K(90, (0, 0, 0)), K(135, (0, 0, 0.7))]},
        "L-Arm": {"rot": [K(0, (0, 0, 0)), K(90, (0, 0, 5))]},
        "R-Arm": {"rot": [K(0, (0, 0, 0)), K(90, (0, 0, -5))]},
        "Sprout": {"rot": [K(0, (0, 0, 0)), K(60, (0, 0, 6)), K(120, (0, 0, -5))]},
        "L-Brow": {"pos": [K(0, (0, 0, 0)), K(60, (0, 0, 0)), K(72, (0, 0.7, 0)), K(100, (0, 0, 0))]},
        "R-Brow": {"pos": [K(0, (0, 0, 0)), K(60, (0, 0, 0)), K(72, (0, 0.7, 0)), K(100, (0, 0, 0))]},
        "L-Eyelid": lids, "R-Eyelid": lids,
    }

# --------------------------------------------------------------------------------------------- Walk
def foot_keys(side, roll_deg, bob, lift, dz):
    """position/rotation delta (in Body space) that keeps a foot flat and on the ground while the Body rolls"""
    th = math.radians(roll_deg)
    dy = -(bob + side * FOOT_X * math.sin(th) + (-FOOT_BOTTOM_REL) * (1 - math.cos(th))) / math.cos(th) + lift
    return (0, dy, dz), (0, 0, -roll_deg)

def walk():
    D = 40
    # t: (roll, yaw, bob, L(lift,dz), R(lift,dz))
    phases = [(0, 6, 4, 1.0, (2.5, 0), (0, 0)),
              (10, 0, 0, 0.0, (0, 3), (0, -3)),
              (20, -6, -4, 1.0, (0, 0), (2.5, 0)),
              (30, 0, 0, 0.0, (0, -3), (0, 3))]
    body_pos, body_rot, lp, lr, rp, rr = [], [], [], [], [], []
    for t, roll, yaw, bob, (llift, ldz), (rlift, rdz) in phases:
        body_pos.append(K(t, (0, bob, 0)))
        body_rot.append(K(t, (0, yaw, roll)))
        p, r = foot_keys(+1, roll, bob, llift, ldz); lp.append(K(t, p)); lr.append(K(t, r))
        p, r = foot_keys(-1, roll, bob, rlift, rdz); rp.append(K(t, p)); rr.append(K(t, r))
    return D, False, {
        "Body": {"pos": body_pos, "rot": body_rot},
        "L-Foot": {"pos": lp, "rot": lr},
        "R-Foot": {"pos": rp, "rot": rr},
        "Head": {"rot": [K(2, (0, 0, -2)), K(12, (0, 0, 0)), K(22, (0, 0, 2)), K(32, (0, 0, 0))],
                 "pos": [K(4, (0, -0.4, 0)), K(14, (0, 0.3, 0)), K(24, (0, -0.4, 0)), K(34, (0, 0.3, 0))]},
        "L-Arm": {"rot": [K(0, (0, 0, 4)), K(10, (16, 0, 2)), K(20, (0, 0, 4)), K(30, (-16, 0, 2))]},
        "R-Arm": {"rot": [K(0, (0, 0, -4)), K(10, (-16, 0, -2)), K(20, (0, 0, -4)), K(30, (16, 0, -2))]},
        "Sprout": {"rot": [K(0, (0, 0, -7)), K(10, (4, 0, 0)), K(20, (0, 0, 7)), K(30, (4, 0, 0))]},
    }

# --------------------------------------------------------------------------------------------- Talk
def talk():
    D = 40
    return D, False, {
        "Mouth": {"scale": [K(0, (1, 1, 1)), K(6, (0.9, 2.6, 1)), K(13, (1, 1.2, 1)), K(20, (0.92, 2.2, 1)),
                            K(27, (1, 1, 1)), K(33, (0.95, 1.8, 1))]},
        "Head": {"pos": [K(0, (0, 0, 0)), K(6, (0, 1.3, 0)), K(13, (0, 0, 0)), K(20, (0, 1.0, 0)), K(27, (0, 0, 0)), K(33, (0, 0.6, 0))],
                 "rot": [K(0, (0, 0, 0)), K(6, (-3, 0, 0)), K(13, (1, 0, 0)), K(20, (-2, 0, 1)), K(27, (1, 0, 0)), K(33, (-1, 0, -1))]},
        "Body": {"pos": [K(0, (0, 0, 0)), K(6, (0, 0.4, 0)), K(13, (0, 0, 0)), K(20, (0, 0.3, 0)), K(27, (0, 0, 0))]},
        "L-Brow": {"pos": [K(0, (0, 0, 0)), K(6, (0, 1, 0)), K(13, (0, 0, 0)), K(20, (0, 0.8, 0)), K(27, (0, 0, 0))]},
        "R-Brow": {"pos": [K(0, (0, 0, 0)), K(6, (0, 1, 0)), K(13, (0, 0, 0)), K(20, (0, 0.8, 0)), K(27, (0, 0, 0))]},
        "L-Arm": {"rot": [K(0, (0, 0, 0)), K(10, (0, 0, 28)), K(20, (0, 0, 10)), K(30, (-10, 0, 30))]},
        "R-Arm": {"rot": [K(0, (0, 0, 0)), K(14, (0, 0, -12)), K(26, (-8, 0, -24))]},
        "Sprout": {"rot": [K(0, (0, 0, 0)), K(8, (0, 0, -6)), K(20, (0, 0, 5))]},
    }

# --------------------------------------------------------------------------------------------- Wave (hop + pebble-arm wave)
def wave():
    D = 64
    squint_pos, squint_scale = (0, -1.5, 0), (1, 4, 1)
    lids = {"pos": [K(0, (0, 0, 0)), K(14, squint_pos), K(50, squint_pos), K(58, (0, 0, 0))],
            "scale": [K(0, (1, 1, 1)), K(14, squint_scale), K(50, squint_scale), K(58, (1, 1, 1))]}
    brow = {"pos": [K(0, (0, 0, 0)), K(12, (0, 1.1, 0)), K(50, (0, 1.1, 0)), K(58, (0, 0, 0))]}
    return D, False, {
        "Body": {"pos": [K(0, (0, 0, 0)), K(5, (0, -1.6, 0)), K(13, (0, 7, 0)), K(21, (0, 0, 0), "linear"),
                         K(25, (0, -1.4, 0)), K(31, (0, 0, 0))]},
        "L-Foot": {"rot": [K(5, (0, 0, 0)), K(13, (-14, 0, 0)), K(21, (0, 0, 0))]},
        "R-Foot": {"rot": [K(5, (0, 0, 0)), K(13, (-14, 0, 0)), K(21, (0, 0, 0))]},
        "R-Arm": {"pos": [K(0, (0, 0, 0)), K(12, (-4, 2, 4)), K(52, (-4, 2, 4)), K(60, (0, 0, 0))],
                  "rot": [K(0, (0, 0, 0)), K(12, (0, 0, -122)), K(20, (0, 0, -98)), K(28, (0, 0, -126)),
                          K(36, (0, 0, -98)), K(44, (0, 0, -124)), K(52, (0, 0, -104)), K(60, (0, 0, 0))]},
        "L-Arm": {"rot": [K(0, (0, 0, 0)), K(13, (0, 0, 22)), K(30, (0, 0, 6)), K(56, (0, 0, 0))]},
        "Head": {"rot": [K(0, (0, 0, 0)), K(13, (-3, 0, 0)), K(22, (0, 0, 5)), K(40, (0, 0, 3)), K(58, (0, 0, 0))]},
        "Mouth": {"scale": [K(0, (1, 1, 1)), K(14, (1, 1.8, 1)), K(50, (1, 1.8, 1)), K(58, (1, 1, 1))]},
        "L-Eyelid": lids, "R-Eyelid": lids, "L-Brow": brow, "R-Brow": brow,
        "Sprout": {"rot": [K(0, (0, 0, 0)), K(13, (-10, 0, 0)), K(21, (12, 0, 0)), K(28, (-5, 0, 4)), K(36, (0, 0, 0))]},
    }

# --------------------------------------------------------------------------------------------- Hurt (wince)
def hurt():
    D = 24
    lids = {"pos": [K(0, (0, 0, 0)), K(3, (0, -3.3, 0)), K(11, (0, -3.3, 0)), K(18, (0, 0, 0))],
            "scale": [K(0, (1, 1, 1)), K(3, (1, 10, 1)), K(11, (1, 10, 1)), K(18, (1, 1, 1))]}
    return D, False, {
        "Body": {"rot": [K(0, (0, 0, 0)), K(4, (-9, 0, 0)), K(12, (2, 0, 0)), K(19, (0, 0, 0))],
                 "pos": [K(0, (0, 0, 0)), K(4, (0, 0, -1.5)), K(16, (0, 0, 0))]},
        "Head": {"rot": [K(0, (0, 0, 0)), K(4, (-6, 0, 4)), K(16, (0, 0, 0))]},
        "L-Eyelid": lids, "R-Eyelid": lids,
        "Mouth": {"scale": [K(0, (1, 1, 1)), K(4, (0.6, 2.0, 1)), K(18, (1, 1, 1))]},
        "L-Brow": {"pos": [K(0, (0, 0, 0)), K(4, (0, -1, 0)), K(18, (0, 0, 0))], "rot": [K(0, (0, 0, 0)), K(4, (0, 0, 15)), K(18, (0, 0, 0))]},
        "R-Brow": {"pos": [K(0, (0, 0, 0)), K(4, (0, -1, 0)), K(18, (0, 0, 0))], "rot": [K(0, (0, 0, 0)), K(4, (0, 0, -15)), K(18, (0, 0, 0))]},
        "L-Arm": {"rot": [K(0, (0, 0, 0)), K(4, (0, 0, 32)), K(16, (0, 0, 0))]},
        "R-Arm": {"rot": [K(0, (0, 0, 0)), K(4, (0, 0, -32)), K(16, (0, 0, 0))]},
        "Sprout": {"rot": [K(0, (0, 0, 0)), K(4, (0, 0, 14)), K(9, (0, 0, -9)), K(15, (0, 0, 4)), K(20, (0, 0, 0))]},
    }

# --------------------------------------------------------------------------------------------- Death (crumble, then pop back)
def death():
    D = 96
    L = "linear"
    def held(rest, mid, settle, pop, end=None, pop_t=66):
        # rest@0 -> crumble@22 -> settle@28 -> hold -> pop@pop_t -> rest
        keys = [K(0, rest), K(10, tuple((a + b) / 2 for a, b in zip(rest, mid))), K(22, mid), K(28, settle, L), K(60, settle, L), K(pop_t, pop)]
        keys.append(K(76, end if end is not None else rest))
        return keys
    Z = (0, 0, 0)
    lids = {"pos": [K(0, Z), K(8, (0, -3.3, 0), L), K(64, (0, -3.3, 0), L), K(70, Z)],
            "scale": [K(0, (1, 1, 1)), K(8, (1, 10, 1), L), K(64, (1, 10, 1), L), K(70, (1, 1, 1))]}
    return D, True, {
        "Body": {"pos": [K(0, Z), K(6, (0, -2, 0)), K(22, (0, -2.5, 0)), K(28, (0, -2.5, 0), L), K(60, (0, -2.5, 0), L),
                         K(66, (0, 5, 0)), K(74, (0, -1.5, 0)), K(82, Z)],
                 "rot": held(Z, (0, 0, 6), (0, 0, 5), (0, 0, -3))},
        "Head": {"pos": held(Z, (9, -7, 7), (10, -8, 7.5), (0, 2.5, 0)),
                 "rot": held(Z, (28, 0, -22), (31, 0, -24), (-4, 0, 3))},
        "Head-Top": {"pos": held(Z, (-7, 1, -5), (-8, 0, -6), (0, 2, 0)),
                     "rot": held(Z, (0, 0, 24), (0, 0, 27), (0, 0, -4))},
        "Moss-Cap": {"pos": held(Z, (-5, 1.5, -3), (-6, 0.5, -3), (0, 1.5, 0)),
                     "rot": held(Z, (0, 0, 16), (0, 0, 18), Z)},
        "L-Arm": {"pos": held(Z, (6, -11, 3), (6.5, -11.5, 3), (0, 1, 0)),
                  "rot": held(Z, (0, 0, 80), (0, 0, 88), (0, 0, 40))},
        "R-Arm": {"pos": held(Z, (-6, -11, 2), (-6.5, -11.5, 2), (0, 1, 0)),
                  "rot": held(Z, (0, 0, -80), (0, 0, -88), (0, 0, -40))},
        "L-Foot": {"pos": held(Z, (3, 2.5, 1), (3, 2.5, 1), (0, -3, 0))},
        "R-Foot": {"pos": held(Z, (-3, 2.5, -1), (-3, 2.5, -1), (0, -3, 0))},
        "Mouth": {"scale": held((1, 1, 1), (1.1, 0.5, 1), (1.1, 0.5, 1), (0.9, 2.4, 1))},
        "L-Eyelid": lids, "R-Eyelid": lids,
        "Sprout": {"rot": held(Z, (0, 0, 30), (0, 0, 36), (0, 0, -15))},
    }

ANIMS = [("Default", "Idle", idle), ("Default", "Walk", walk), ("Default", "Talk", talk), ("Default", "Wave", wave),
         ("Damage", "Hurt", hurt), ("Damage", "Death", death)]

def write_all(npc_dir):
    files = []
    for folder, name, fn in ANIMS:
        D, hold, tracks = fn()
        data = build(D, hold, tracks)
        path = os.path.join(npc_dir, "Animations", folder, name + ".blockyanim")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        files.append({"folder": folder, "name": name, "duration_frames": D, "seconds": round(D / 60.0, 3),
                      "holdLastKeyframe": hold, "nodes": sorted(tracks.keys())})
    return files
