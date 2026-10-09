"""SkyWynn pet animations (.blockyanim, 60 fps time units, deltas from the rest pose) - one set per body plan.

quad   (Goat, Warthog, Boar, Tusker, Bear, Wolf, Ram, Mouflon, Horse, Camel): Idle, Walk, Run
rabbit (Rabbit): Idle, Walk (hop), Run (fast hop)
bird   (Chicken, Turkey): Idle, Walk, Run
hawk   (Hawk): Idle, Walk (hop), Fly
flyer  (Skrill): Idle (hover), Walk (hover forward), Fly
Keys are written < duration; the plugin wraps the loop from the last key to the first.
"""
import json, os
from pets_common import quat_from_euler_zyx, r6

def K(t, v, it="smooth"):
    return (t, v, it)

Z = (0, 0, 0)

def build(duration, hold, tracks, have):
    out = {}
    for node, ch in tracks.items():
        if node not in have:
            continue
        nd = {"position": [], "orientation": [], "shapeStretch": [], "shapeVisible": [], "shapeUvOffset": []}
        for (t, v, it) in ch.get("pos", []):
            nd["position"].append({"time": t, "delta": {"x": r6(v[0]), "y": r6(v[1]), "z": r6(v[2])}, "interpolationType": it})
        for (t, v, it) in ch.get("rot", []):
            q = quat_from_euler_zyx(*v)
            nd["orientation"].append({"time": t, "delta": {"x": r6(q[0]), "y": r6(q[1]), "z": r6(q[2]), "w": r6(q[3])}, "interpolationType": it})
        for (t, v, it) in ch.get("scale", []):
            nd["shapeStretch"].append({"time": t, "delta": {"x": r6(v[0]), "y": r6(v[1]), "z": r6(v[2])}, "interpolationType": it})
        for k in nd:
            assert all(kf["time"] < duration for kf in nd[k]), (node, k)
            nd[k].sort(key=lambda kf: kf["time"])
        out[node] = nd
    return {"formatVersion": 1, "duration": duration, "holdLastKeyframe": hold, "nodeAnimations": out}

def blink(t0, eh, close=3, opened=6):
    d = -(eh / 2 + 0.3)
    return {"pos": [K(t0, Z), K(t0 + close, (0, d, 0)), K(t0 + close + opened - 3, Z)],
            "scale": [K(t0, (1, 1, 1)), K(t0 + close, (1, 10, 1)), K(t0 + close + opened - 3, (1, 1, 1))]}

def mirror_rot(keys):
    return [(t, (v[0], -v[1], -v[2]), it) for (t, v, it) in keys]

def lr(tracks, name, ch):
    """add an L- track and its mirrored R- track"""
    tracks["L-" + name] = ch
    m = {}
    for k, keys in ch.items():
        m[k] = mirror_rot(keys) if k == "rot" else ([(t, (-v[0], v[1], v[2]), it) for (t, v, it) in keys] if k == "pos" else keys)
    tracks["R-" + name] = m

def eyes(tracks, eh, t0):
    b = blink(t0, eh)
    tracks["L-Eyelid"] = b; tracks["R-Eyelid"] = b

# ------------------------------------------------------------------ quadruped
def quad_idle(s):
    D = 180; T = {}
    T["Head"] = {"rot": [K(0, Z), K(45, (2, 0, 3)), K(90, (0, 0, 0)), K(135, (-1, 0, -3))]}
    T["Body"] = {"pos": [K(0, Z), K(90, (0, 0.35, 0))]}
    T["Tail"] = {"rot": [K(0, Z), K(100, Z), K(108, (0, 14, 0)), K(116, (0, -14, 0)), K(124, (0, 10, 0)), K(132, Z)]}
    for nk in ("Neck", "Neck-Low"):
        T[nk] = {"rot": [K(0, Z), K(60, (-3, 0, 0)), K(120, (2, 0, 0))]}
    lr(T, "Ear", {"rot": [K(0, Z), K(60, Z), K(64, (-12, 0, -8)), K(70, Z)]})
    eyes(T, s["eh"], 140)
    return D, False, T

def quad_walk(s, D=40, A=24, bob=0.8, run=False):
    T = {}
    h = D // 2; q = D // 4
    for leg, ph in (("L-Front-Leg", 0), ("R-Back-Leg", 0), ("R-Front-Leg", h), ("L-Back-Leg", h)):
        a = A if not run else A * 1.4
        T[leg] = {"rot": [K((0 + ph) % D, (a, 0, 0)), K((h + ph) % D, (-a, 0, 0))]}
    T["Body"] = {"pos": [K(0, Z), K(q, (0, bob, 0)), K(h, Z), K(h + q, (0, bob, 0))],
                 "rot": [K(0, (0, 0, 1.5)), K(h, (0, 0, -1.5))] if not run else [K(0, (-3, 0, 0)), K(h, (3, 0, 0))]}
    T["Head"] = {"rot": [K(0, (2, 0, 0)), K(q, (-2, 0, 0)), K(h, (2, 0, 0)), K(h + q, (-2, 0, 0))]}
    T["Tail"] = {"rot": [K(0, (0, 10, 0)), K(h, (0, -10, 0))]}
    lr(T, "Ear", {"rot": [K(q, (-6, 0, 0)), K(h + q, (4, 0, 0))]})
    return D, False, T

# ------------------------------------------------------------------ rabbit
def rabbit_idle(s):
    D, _, T = quad_idle(s)
    T["Snout"] = {"pos": [K(0, Z), K(20, (0, 0.4, 0)), K(26, Z), K(32, (0, 0.4, 0)), K(38, Z)]}
    return D, False, T

def rabbit_hop(s, D=36, hgt=4.5):
    D0 = D
    T = {}
    T["Body"] = {"pos": [K(0, Z), K(4, (0, -0.6, 0)), K(12, (0, hgt, 0)), K(22, Z, "linear"), K(26, (0, -0.5, 0)), K(31, Z)],
                 "rot": [K(0, Z), K(6, (-10, 0, 0)), K(14, (2, 0, 0)), K(20, (8, 0, 0)), K(28, Z)]}
    T["L-Back-Leg"] = {"rot": [K(0, Z), K(6, (35, 0, 0)), K(16, (-10, 0, 0)), K(26, Z)]}
    T["R-Back-Leg"] = dict(T["L-Back-Leg"])
    T["L-Front-Leg"] = {"rot": [K(0, Z), K(8, (-30, 0, 0)), K(18, (-15, 0, 0)), K(24, Z)]}
    T["R-Front-Leg"] = dict(T["L-Front-Leg"])
    T["L-Leg"] = dict(T["L-Back-Leg"]); T["R-Leg"] = dict(T["L-Back-Leg"])
    lr(T, "Ear", {"rot": [K(0, Z), K(10, (-18, 0, 0)), K(22, (8, 0, 0)), K(30, Z)]})
    T["Tail"] = {"pos": [K(0, Z), K(12, (0, 1, 0)), K(24, Z)]}
    f = D0 / 36.0
    for ch in T.values():
        for k in ch:
            ch[k] = [(min(int(round(t * f)), D0 - 1), v, it) for (t, v, it) in ch[k]]
    return D0, False, T

# ------------------------------------------------------------------ birds
def bird_idle(s):
    D = 160; T = {}
    T["Head"] = {"rot": [K(0, Z), K(30, (0, 0, 10)), K(60, Z), K(96, Z), K(104, (28, 0, 0)), K(110, (8, 0, 0)), K(116, (26, 0, 0)), K(124, Z)]}
    T["Body"] = {"pos": [K(0, Z), K(80, (0, 0.3, 0))]}
    T["Tail"] = {"rot": [K(0, Z), K(40, (-6, 0, 0)), K(46, Z)]}
    T["Fan-4"] = {"rot": [K(0, Z), K(80, (-3, 0, 0))]}
    lr(T, "Wing", {"rot": [K(0, Z), K(130, Z), K(134, (0, 0, 28)), K(138, (0, 0, 6)), K(142, (0, 0, 26)), K(148, Z)]})
    eyes(T, s["eh"], 70)
    return D, False, T

def bird_walk(s, D=30, A=28):
    T = {}; h = D // 2; q = D // 4
    T["L-Leg"] = {"rot": [K(0, (A, 0, 0)), K(h, (-A, 0, 0))]}
    T["R-Leg"] = {"rot": [K(0, (-A, 0, 0)), K(h, (A, 0, 0))]}
    T["Body"] = {"rot": [K(0, (0, 0, 5)), K(h, (0, 0, -5))], "pos": [K(0, Z), K(q, (0, 0.7, 0)), K(h, Z), K(h + q, (0, 0.7, 0))]}
    T["Head"] = {"pos": [K(0, (0, 0, 1.2)), K(q, (0, 0, -0.6)), K(h, (0, 0, 1.2)), K(h + q, (0, 0, -0.6))]}
    lr(T, "Wing", {"rot": [K(0, (0, 0, 4)), K(h, (0, 0, 0))]})
    T["Tail"] = {"rot": [K(0, (0, 6, 0)), K(h, (0, -6, 0))]}
    return D, False, T

def hawk_idle(s):
    D = 200; T = {}
    T["Head"] = {"rot": [K(0, Z), K(30, (0, 35, 0)), K(70, (0, 35, 0)), K(90, (0, 0, 12)), K(120, Z), K(150, (0, -30, 0)), K(185, Z)]}
    T["Body"] = {"pos": [K(0, Z), K(100, (0, 0.3, 0))]}
    lr(T, "Wing", {"rot": [K(0, Z), K(160, Z), K(166, (0, 0, 40)), K(172, (0, 0, 10)), K(176, Z)]})
    lr(T, "Tuft", {"rot": [K(0, Z), K(90, (0, 0, -10)), K(120, Z)]})
    eyes(T, s["eh"], 110)
    return D, False, T

def hawk_fly(s, D=30):
    T = {}; h = D // 2
    T["Body"] = {"rot": [K(0, (22, 0, 0))], "pos": [K(0, (0, 6, 0)), K(h, (0, 7.5, 0))]}
    lr(T, "Wing", {"rot": [K(0, (0, 0, 135)), K(h, (0, 0, 62))]})
    lr(T, "Leg", {"rot": [K(0, (55, 0, 0))]})
    T["Head"] = {"rot": [K(0, (-18, 0, 0))]}
    T["Tail"] = {"rot": [K(0, (10, 0, 0)), K(h, (16, 0, 0))]}
    return D, False, T

# ------------------------------------------------------------------ hovering flyer (Skrill)
def flyer(s, D=24, up=38, down=-22, bob=1.5, tilt=0):
    T = {}; h = D // 2
    T["Body"] = {"pos": [K(0, (0, -bob, 0)), K(h, (0, bob, 0))], "rot": [K(0, (tilt, 0, 0))]}
    lr(T, "Wing", {"rot": [K(0, (0, 0, up)), K(h, (0, 0, down))]})
    lr(T, "Wing-Skin", {"rot": [K(0, (0, 0, -8)), K(h, (0, 0, 10))]})
    T["Tail"] = {"rot": [K(0, (8, 6, 0)), K(h, (-6, -6, 0))]}
    T["Head"] = {"rot": [K(0, (3, 0, 0)), K(h, (-3, 0, 0))]}
    for i in (1, 2, 3):
        T[f"Crest-{i}"] = {"rot": [K(0, (0, 0, 0)), K(h, (-8, 0, 0))]}
    lr(T, "Foot", {"rot": [K(0, (30, 0, 0))]})
    return D, False, T

def flyer_idle(s):
    D, _, T = flyer(s, D=36, up=34, down=-18, bob=1.2)
    # blink inside the loop length
    eyes(T, s["eh"], 20)
    return D, False, T

RIGS = {
    "quad": [("Default", "Idle", quad_idle), ("Default", "Walk", lambda s: quad_walk(s)),
             ("Default", "Run", lambda s: quad_walk(s, D=24, A=30, bob=1.4, run=True))],
    "rabbit": [("Default", "Idle", rabbit_idle), ("Default", "Walk", lambda s: rabbit_hop(s)),
               ("Default", "Run", lambda s: rabbit_hop(s, D=26, hgt=6))],
    "bird": [("Default", "Idle", bird_idle), ("Default", "Walk", lambda s: bird_walk(s)),
             ("Default", "Run", lambda s: bird_walk(s, D=18, A=36))],
    "hawk": [("Default", "Idle", hawk_idle), ("Default", "Walk", lambda s: rabbit_hop(s, D=30, hgt=3)), ("Default", "Fly", hawk_fly)],
    "flyer": [("Default", "Idle", flyer_idle), ("Default", "Walk", lambda s: flyer(s, tilt=12)), ("Default", "Fly", lambda s: flyer(s, D=18, up=44, down=-28, tilt=18))],
}

def write_all(pdir, spec, by_name):
    eh = by_name["L-Eye"]["shape"][1][1]
    s = dict(eh=eh)
    have = set(by_name)
    files = []
    for folder, name, fn in RIGS[spec["rig"]]:
        D, hold, tracks = fn(s)
        data = build(D, hold, tracks, have)
        path = os.path.join(pdir, "Animations", folder, name + ".blockyanim")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2); fh.write("\n")
        files.append({"folder": folder, "name": name, "duration_frames": D, "seconds": round(D / 60.0, 3),
                      "holdLastKeyframe": hold, "nodes": sorted(data["nodeAnimations"].keys())})
    return files
