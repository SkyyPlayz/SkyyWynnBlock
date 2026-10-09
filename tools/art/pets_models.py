"""SkyWynn launch pets - geometry + paint definitions (ORIGINAL designs; no vanilla data used).

Units = Hytale character units (64 = 1 block, 1 unit = 1 texel, UVs locked to face size). Pets face +Z, ground = y 0,
L- = the pet's left = +X (vanilla convention). Every box is axis-aligned at rest unless it is a leaf with `rot`.
Style: "cute Hytale" - chunky boxes, big heads (about half the height for small pets), big glinting eyes on the face,
short legs, a soft blush, painted light. Sizes are the Lv 100 / 1.0x size (Pets-Spec 6: 0.6x at Lv 1).
"""
import numpy as np

# ------------------------------------------------------------------ node helpers
def B(name, parent, pivot, size, offset=(0, 0, 0), mat="fur", rot=(0, 0, 0), **kw):
    return dict(name=name, parent=parent, pivot=tuple(pivot), shape=("box", tuple(size), tuple(offset)), mat=mat, rot=tuple(rot), **kw)

def Q(name, parent, pivot, size, mat="eye", rot=(0, 0, 0), **kw):
    return dict(name=name, parent=parent, pivot=tuple(pivot), shape=("quad", tuple(size), (0, 0, 0)), mat=mat, rot=tuple(rot), **kw)

def E(name, parent, pivot):
    return dict(name=name, parent=parent, pivot=tuple(pivot), shape=None, mat=None, rot=(0, 0, 0))

def mir(n):
    """R- copy of an L- node (mirrored on X, shares the L texture mirrored)."""
    m = dict(n)
    m["name"] = n["name"].replace("L-", "R-", 1)
    if n["parent"] and n["parent"].startswith("L-"):
        m["parent"] = n["parent"].replace("L-", "R-", 1)
    px, py, pz = n["pivot"]; m["pivot"] = (-px, py, pz)
    if n["shape"]:
        t, s, (ox, oy, oz) = n["shape"]; m["shape"] = (t, s, (-ox, oy, oz))
    rx, ry, rz = n["rot"]; m["rot"] = (rx, -ry, -rz)
    m.pop("mirror_of", None)
    if n["shape"] and n["shape"][0] == "quad":
        m["share_of"] = n["name"]
    else:
        m["mirror_of"] = n["name"]
    return m

def pair(*nodes):
    out = []
    for n in nodes:
        out += [n, mir(n)]
    return out

def face(head, head_c, head_size, eye_size, eye_dx, eye_y, iris, lid_mat, blush=True):
    """eyes + blink lids on the head's front face (quads 0.1 in front)."""
    zf = head_c[2] + head_size[2] / 2
    ew, eh = eye_size
    L = [Q("L-Eye", head, (eye_dx, eye_y, zf + 0.1), (ew, eh), mat="eye", iris=iris),
         Q("L-Eyelid", head, (eye_dx, eye_y + eh / 2 + 0.3, zf + 0.2), (ew, eh), mat="lid", lid_mat=lid_mat, stretch=(1, 0.1, 1))]
    return pair(*L)

# ------------------------------------------------------------------ zone predicates (world-space, rest pose)
def ell(cx, cy, rx, ry, ax=(0, 1)):
    return lambda P, N, U, V, w, h: (((P[:, ax[0]] - cx) / rx) ** 2 + ((P[:, ax[1]] - cy) / ry) ** 2) < 1

def ell_sym(cx, cy, rx, ry):
    return lambda P, N, U, V, w, h: (((np.abs(P[:, 0]) - cx) / rx) ** 2 + ((P[:, 1] - cy) / ry) ** 2) < 1

def below(y):
    return lambda P, N, U, V, w, h: P[:, 1] < y

def above(y):
    return lambda P, N, U, V, w, h: P[:, 1] > y

def rows_top(n):
    return lambda P, N, U, V, w, h: V < n

def rows_bottom(n):
    return lambda P, N, U, V, w, h: V >= h - n

def AND(*fs):
    def f(*a):
        m = fs[0](*a)
        for g in fs[1:]:
            m = m & g(*a)
        return m
    return f

def rect(x0, x1, y0, y1):
    return lambda P, N, U, V, w, h: (P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1)

def belly_wave(y, amp=1.0, per=5.0):
    """ragged painted edge: true below y (+ a soft wave)"""
    return lambda P, N, U, V, w, h: P[:, 1] < y + amp * np.sin((P[:, 0] + P[:, 2]) / per * 2.1)

def stripes(axis, period, width, phase=0.0):
    return lambda P, N, U, V, w, h: ((P[:, axis] + phase) % period) < width

def edges(n=1):
    return lambda P, N, U, V, w, h: (U < n) | (V < n) | (U >= w - n) | (V >= h - n)

ALL = None

# ------------------------------------------------------------------ shared quadruped builder
def quad(o):
    """o: body(w,h,d), body_y, body_z, leg(w,h,d), leg_x, leg_zf, leg_zb, head(w,h,d), head_c(x,y,z), snout(size,center,mat)|None,
       eye(size,dx,y), iris, ears [nodes], tail node, extras [nodes]"""
    bw, bh, bd = o["body"]; by = o["body_y"]; bz = o.get("body_z", 0)
    nodes = [E("Origin", None, (0, 0, 0)),
             B("Body", "Origin", (0, by + bh / 2, bz), o["body"], mat=o.get("body_mat", "fur"))]
    lw, lh, ld = o["leg"]
    leg_top = lh
    for nm, z in (("L-Front-Leg", o["leg_zf"]), ("L-Back-Leg", o["leg_zb"])):
        nodes += pair(B(nm, "Body", (o["leg_x"], leg_top, z), o["leg"], (0, -lh / 2, 0), mat=o.get("leg_mat", "fur")))
    hw, hh, hd = o["head"]; hc = o["head_c"]
    neck_parent = o.get("neck_parent", "Body")
    nodes.append(B("Head", neck_parent, (0, hc[1] - hh / 2 + 2, hc[2] - hd / 2 + 2),
                   o["head"], (0, hh / 2 - 2, hd / 2 - 2), mat=o.get("head_mat", "fur")))
    if o.get("snout"):
        s_size, s_c, s_mat = o["snout"]
        nodes.append(B("Snout", "Head", s_c, s_size, mat=s_mat))
    (ew, eh), edx, ey = o["eye"]
    nodes += face("Head", hc, o["head"], (ew, eh), edx, ey, o["iris"], o.get("lid_mat", o.get("head_mat", "fur")))
    nodes += o.get("ears", []) + o.get("tail", []) + o.get("extras", [])
    return nodes

def saddle(top_y, z, w=14, d=12, blanket=(18, 16), parent="Body", trim="gold", side_x=None):
    """mount marker (original): blanket + leather seat + horn. The rider seat sits on the `Saddle` node."""
    return [B("Saddle-Blanket", parent, (0, top_y + 0.5, z), (blanket[0], 1, blanket[1]), mat="blanket"),
            B("Saddle", parent, (0, top_y + 2.5, z), (w, 3, d), mat="leather"),
            B("Saddle-Horn", "Saddle", (0, top_y + 5, z + d / 2 - 1.5), (3, 2, 2), mat=trim),
            ] + pair(B("L-Strap", "Saddle", ((side_x or w / 2) + 0.5, top_y - 4, z), (1, 9, 3), mat="leather"),
                     B("L-Stirrup", "L-Strap", ((side_x or w / 2) + 1, top_y - 9.5, z), (1, 2, 4), mat=trim))

# ================================================================== the 15 pets
PETS = {}

def pet(fn):
    PETS[fn.__name__.capitalize()] = fn
    return fn

COMMON_MATS = {"eye": ("#2e2238", "flat"), "nose": ("#5a3040", "flat"), "mouth": ("#4a2a34", "flat"),
               "blush": ("#f0a0a8", "fur"), "leather": ("#7a4a2c", "leather"), "gold": ("#e0b24a", "gold"),
               "blanket": ("#b8483c", "cloth"), "hoof": ("#4a3a36", "smooth"), "claw": ("#e8dcc0", "smooth")}

BLUSH = lambda x, y, rx=2.2, ry=1.1: ("Head", {"front"}, ell_sym(x, y, rx, ry), "blush")

@pet
def rabbit():
    nodes = quad(dict(body=(16, 13, 18), body_y=3, body_z=-3, leg=(4, 6, 4), leg_x=4, leg_zf=5, leg_zb=-7,
        head=(16, 14, 13), head_c=(0, 23, 8), snout=((8, 5, 2), (0, 19.5, 15.5), "cream"),
        eye=((5, 6), 4.5, 24.5), iris="#6a3e22",
        ears=pair(B("L-Ear", "Head", (4, 29.5, 6), (4, 14, 2), (0, 7, 0), rot=(-8, 0, -12), mat="fur")),
        tail=[B("Tail", "Body", (0, 10, -12), (5, 5, 4), mat="cream")],
        extras=pair(B("L-Haunch", "Body", (6.5, 8, -7), (5, 9, 10), mat="fur"))))
    # back legs are big flat feet
    for n in nodes:
        if n["name"] in ("L-Back-Leg", "R-Back-Leg"):
            s = 1 if n["name"][0] == "L" else -1
            n["pivot"] = (s * 6.5, 4, -6); n["shape"] = ("box", (5, 4, 10), (0, -2, 2))
    return dict(nodes=nodes, rig="rabbit", height=30,
        mats={"fur": ("#b98a5c", "fur"), "cream": ("#efe2c8", "fur"), "ear_in": ("#e9a6a4", "smooth"), **COMMON_MATS},
        zones=[("L-Ear", {"front"}, AND(rect(-9, 99, 30.5, 99), lambda P, N, U, V, w, h: (U >= 1) & (U <= 2)), "ear_in"),
               ("Body", ALL, belly_wave(7.5), "cream"), (("L-Front-Leg", "L-Back-Leg"), ALL, below(2.5), "cream"),
               ("Snout", {"front"}, AND(rect(-1.5, 1.5, 20.5, 22.5)), "nose"),
               ("Snout", {"front"}, rect(-0.5, 0.5, 18, 20.5), "mouth"),
               ("Snout", {"top"}, rect(-1.5, 1.5, -99, 99), "nose"),
               BLUSH(5.5, 20.5), ("Head", {"top", "back"}, lambda P, N, U, V, w, h: P[:, 2] < 4, "fur_dk")],
        extra_mats={"fur_dk": ("#9a6e48", "fur")})

@pet
def chicken():
    nodes = [E("Origin", None, (0, 0, 0)), B("Body", "Origin", (0, 13.5, -1), (14, 13, 15), mat="feather"),
             B("Head", "Body", (0, 21, 2), (11, 11, 10), (0, 4, 3), mat="feather"),
             B("Beak", "Head", (0, 24.5, 11.5), (4, 3, 3), mat="beak"),
             B("Wattle", "Beak", (0, 21.5, 10.5), (2, 3, 1), mat="red"),
             B("Comb", "Head", (0, 31.5, 5.5), (2, 3, 6), mat="red"),
             B("Comb-Top", "Comb", (0, 33.5, 4.5), (2, 2, 3), mat="red"),
             B("Tail", "Body", (0, 20, -9), (8, 8, 4), (0, 3, 0), rot=(-22, 0, 0), mat="feather")]
    nodes += pair(B("L-Wing", "Body", (7.5, 18, -1), (2, 8, 11), (0.5, -3.5, 0), mat="feather"),
                  B("L-Leg", "Body", (3, 7.5, 0), (2, 6, 2), (0, -3, 0), mat="beak"))
    nodes += pair(B("L-Foot", "L-Leg", (3, 1.5, 0.5), (4, 1, 5), (0, -0.5, 1), mat="beak"))
    nodes += face("Head", (0, 26, 5), (11, 11, 10), (4, 5), 3.5, 27.5, "#5a3018", "feather")
    return dict(nodes=nodes, rig="bird", height=35,
        mats={"feather": ("#efe6d6", "feather"), "beak": ("#e8a03a", "smooth"), "red": ("#d8463e", "smooth"), **COMMON_MATS},
        zones=[BLUSH(4.0, 24.2, 1.6, 1.0), ("L-Wing", {"left", "right"}, rows_bottom(3), "feather_dk"),
               ("Tail", ALL, rows_top(2), "feather_dk")],
        extra_mats={"feather_dk": ("#d6c8b0", "feather")})

@pet
def goat():
    nodes = quad(dict(body=(14, 12, 20), body_y=12, body_z=-1, leg=(4, 13, 4), leg_x=4.5, leg_zf=6, leg_zb=-8,
        head=(13, 13, 12), head_c=(0, 29, 10), snout=((8, 6, 4), (0, 25, 18), "cream"),
        eye=((4, 5), 3.5, 30), iris="#c88a2a",
        ears=pair(B("L-Ear", "Head", (6.5, 32, 10), (4, 2, 3), (2, 0, 0), rot=(0, 0, -35), mat="fur")),
        tail=[B("Tail", "Body", (0, 23, -11), (3, 4, 2), (0, 2, 0), rot=(25, 0, 0), mat="cream")],
        extras=pair(B("L-Horn", "Head", (3.5, 35.5, 9), (3, 5, 3), (0, 2.5, 0), rot=(-25, 0, -10), mat="horn"),
                    B("L-Horn-Tip", "Head", (4.2, 39.6, 7.3), (2, 3, 2), (0, 1.5, 0), rot=(-60, 0, -10), mat="horn")) +
               [B("Beard", "Snout", (0, 20.5, 18), (3, 4, 2), mat="cream")]))
    return dict(nodes=nodes, rig="quad", height=42,
        mats={"fur": ("#ece2cf", "fur"), "cream": ("#f4eee0", "fur"), "horn": ("#b8a07c", "horn"), "patch": ("#b88a5a", "fur"), **COMMON_MATS},
        zones=[("Body", {"top", "left", "right"}, AND(above(19), lambda P, N, U, V, w, h: P[:, 2] < 3), "patch"),
               (("L-Front-Leg", "L-Back-Leg"), ALL, below(2), "hoof"), (("L-Front-Leg", "L-Back-Leg"), ALL, AND(below(5.5), above(2)), "patch"),
               ("Snout", {"front"}, rect(-2, 2, 26.5, 27.5), "nose"), ("Snout", {"front"}, rect(-1, 1, 24, 24.6), "mouth"),
               BLUSH(4.5, 27), ("Head", {"top"}, ALL, "patch")])

def _hog(hide, mane, snout_c, scale_big=False, tusks="small", paint=False, stripes_on=False, floppy=False, extra_zones=()):
    if scale_big:
        o = dict(body=(20, 16, 24), body_y=8, leg=(5, 9, 5), leg_x=6, leg_zf=7, leg_zb=-8, head=(18, 15, 14), head_c=(0, 22.5, 13),
                 snout=((9, 7, 4), (0, 19.5, 22), "snout"), eye=((5, 6), 4.5, 25.5))
    else:
        o = dict(body=(16, 13, 20), body_y=6, leg=(4, 7, 4), leg_x=5, leg_zf=6, leg_zb=-7, head=(15, 13, 12), head_c=(0, 19.5, 11),
                 snout=((8, 6, 4), (0, 16.5, 19), "snout"), eye=((5, 6), 4, 22))
    hw, hh, hd = o["head"]; hc = o["head_c"]; top = hc[1] + hh / 2; fz = hc[2] + hd / 2
    bt = o["body_y"] + o["body"][1]
    if floppy:
        ears = pair(B("L-Ear", "Head", (hw / 2 - 1, top - 1, hc[2] - 1), (5, 2, 4), (2.5, 0, 0.5), rot=(10, 0, -40), mat="fur"))
    else:
        ears = pair(B("L-Ear", "Head", (hw / 2 - 2, top - 0.5, hc[2]), (4, 5, 2), (0, 2.5, 0), rot=(0, 0, -30), mat="fur"))
    sc = o["snout"][1]; ss = o["snout"][0]
    extras = []
    if mane:
        extras.append(B("Mane", "Body", (0, bt + 1.5, -1), (4 if not scale_big else 5, 3, o["body"][2] - 4), mat="mane"))
        extras.append(B("Mane-Head", "Head", (0, top + 1, hc[2] - 1), (4 if not scale_big else 5, 2, hd - 6), mat="mane"))
    if tusks == "small":
        extras += pair(B("L-Tusk", "Snout", (ss[0] / 2 + 0.5, sc[1] - 1.5, sc[2] + 0.5), (2, 3, 2), (0, 1.5, 0), rot=(0, 0, -35), mat="tusk"))
    elif tusks == "big":
        extras += pair(B("L-Tusk", "Snout", (ss[0] / 2 - 0.5, sc[1] - 1.5, sc[2] + 0.5), (2, 5, 2), (0, 2.5, 0), rot=(-15, 0, -22), mat="tusk"),
                       B("L-Tusk-Tip", "Snout", (ss[0] / 2 + 1.3, sc[1] + 2.8, sc[2] - 0.6), (2, 2, 2), (0, 1, 0), rot=(-15, 0, -22), mat="gold"))
    tail = [B("Tail", "Body", (0, bt - 3, -o["body"][2] / 2 - 0.5), (2, 4, 2), (0, -1.5, -0.5), rot=(30, 0, 0), mat="mane" if mane else "fur")]
    o.update(ears=ears, tail=tail, extras=extras, iris="#4a2a1a")
    nodes = quad(o)
    zones = [(("L-Front-Leg", "L-Back-Leg"), ALL, below(2), "hoof"),
             ("Snout", {"front"}, AND(ell_sym(1.6, sc[1] + 0.5, 0.9, 1.3)), "nose"),
             ("Snout", {"front"}, rect(-1.5, 1.5, sc[1] - ss[1] / 2 - 1, sc[1] - ss[1] / 2 + 0.8), "mouth"),
             BLUSH(hw / 2 - 1.8, o["eye"][2] - 4.5), ("L-Ear", {"front"}, lambda P, N, U, V, w, h: (U >= 1) & (U < w - 1) & (V >= 1), "ear_in")]
    if stripes_on:
        zones.append(("Body", {"left", "right", "top"}, AND(stripes(2, 6, 2), above(o["body_y"] + 4)), "stripe"))
        zones.append(("Head", {"top"}, stripes(0, 5, 1.5, 0.75), "stripe"))
    if paint:
        zones.append(("Body", {"left", "right"}, AND(stripes(2, 7, 2, 2), above(13), below(bt - 2)), "paint"))
        zones.append(("Head", {"front"}, AND(rect(-1, 1, top - 5, top), ), "paint"))
        zones.append(("Head", {"front"}, AND(ell_sym(5, top - 0.9, 2.5, 0.6)), "paint"))
    zones += list(extra_zones)
    return nodes, zones, dict(height=top + 6)

@pet
def warthog():
    nodes, zones, info = _hog(hide=None, mane=True, snout_c=None, tusks="small")
    return dict(nodes=nodes, rig="quad", height=info["height"],
        mats={"fur": ("#8e8a94", "fur"), "mane": ("#55505e", "fur"), "snout": ("#c4a0a0", "smooth"), "tusk": ("#efe4c8", "smooth"),
              "ear_in": ("#c49a9c", "smooth"), **COMMON_MATS}, zones=zones)

@pet
def boar():
    nodes, zones, info = _hog(hide=None, mane=False, snout_c=None, tusks=None, stripes_on=True, floppy=True)
    for n in nodes:
        if n["name"] == "Tail":
            n["shape"] = ("box", (2, 3, 2), (0, -1, 0)); n["rot"] = (40, 0, 0)
    return dict(nodes=nodes, rig="quad", height=info["height"],
        mats={"fur": ("#8c5a36", "fur"), "stripe": ("#e0c08c", "fur"), "snout": ("#d39a8a", "smooth"), "ear_in": ("#c9897c", "smooth"),
              **COMMON_MATS}, zones=zones)

@pet
def tusker():
    nodes, zones, info = _hog(hide=None, mane=True, snout_c=None, scale_big=True, tusks="big", paint=True)
    return dict(nodes=nodes, rig="quad", height=info["height"],
        mats={"fur": ("#b45a38", "fur"), "mane": ("#e0782e", "fur"), "snout": ("#d8a08c", "smooth"), "tusk": ("#f0e6cc", "smooth"),
              "paint": ("#f0eadc", "smooth"), "ear_in": ("#d88a78", "smooth"), **COMMON_MATS}, zones=zones)

@pet
def bear():
    nodes = quad(dict(body=(20, 17, 24), body_y=8, body_z=-1, leg=(6, 10, 6), leg_x=6, leg_zf=7, leg_zb=-9,
        head=(18, 16, 15), head_c=(0, 31, 12), snout=((9, 6, 4), (0, 26, 21.5), "tan"),
        eye=((5, 6), 4.5, 32), iris="#3e2414",
        ears=pair(B("L-Ear", "Head", (7, 38.5, 10), (5, 5, 3), (0, 2, 0), rot=(0, 0, -10), mat="fur")),
        tail=[B("Tail", "Body", (0, 21, -13.5), (4, 4, 3), mat="fur")]))
    return dict(nodes=nodes, rig="quad", height=44,
        mats={"fur": ("#8c5a38", "fur"), "tan": ("#d4aa78", "fur"), "fur_dk": ("#6c4228", "fur"), **COMMON_MATS},
        zones=[("Snout", {"front", "top"}, AND(ell(0, 28.3, 2.2, 1.2)), "nose"), ("Snout", {"top"}, rect(-2, 2, -99, 99), "nose"),
               ("Snout", {"front"}, rect(-0.5, 0.5, 24, 27), "mouth"),
               ("L-Ear", {"front"}, lambda P, N, U, V, w, h: (U >= 1) & (U < w - 1) & (V >= 1), "tan"),
               (("L-Front-Leg", "L-Back-Leg"), ALL, below(3), "fur_dk"), ("Body", {"bottom"}, ALL, "tan"), ("Body", {"front"}, AND(belly_wave(12), rect(-6, 6, -99, 99)), "tan"),
               BLUSH(5.5, 27.5)])

@pet
def turkey():
    nodes = [E("Origin", None, (0, 0, 0)), B("Body", "Origin", (0, 14.5, -1), (16, 15, 16), mat="feather"),
             B("Head", "Body", (0, 24, 3), (10, 10, 9), (0, 4, 2.5), mat="feather"),
             B("Neck", "Body", (0, 23, 4), (7, 4, 7), mat="feather"),
             B("Beak", "Head", (0, 27, 11.5), (3, 2, 3), mat="beak"),
             B("Snood", "Beak", (1.5, 26.5, 12.5), (1, 4, 1), (0, -1.5, 0), mat="red"),
             B("Wattle", "Head", (0, 23.5, 10.5), (3, 3, 2), mat="red")]
    for i, a in enumerate((-66, -44, -22, 0, 22, 44, 66)):
        nodes.append(B(f"Fan-{i + 1}", "Body", (a / 16, 17, -8.5 - (66 - abs(a)) / 60), (6, 15, 1), (0, 7.5, 0), rot=(-22, 0, -a), mat="fan"))
    nodes += pair(B("L-Wing", "Body", (8.5, 20, -1), (2, 10, 12), (0.5, -4, 0), mat="feather"),
                  B("L-Leg", "Body", (3.5, 7.5, 0), (2, 6, 2), (0, -3, 0), mat="leg"))
    nodes += pair(B("L-Foot", "L-Leg", (3.5, 1.5, 0.5), (4, 1, 5), (0, -0.5, 1), mat="leg"))
    nodes += face("Head", (0, 28, 5.5), (10, 10, 9), (4, 5), 3, 29, "#3e2414", "feather")
    return dict(nodes=nodes, rig="bird", height=40,
        mats={"feather": ("#80583a", "feather"), "fan": ("#8c6040", "feather"), "skin": ("#9ebcd8", "smooth"), "beak": ("#e0b880", "smooth"),
              "red": ("#d44a42", "smooth"), "leg": ("#d89a7c", "smooth"), "band": ("#f0e2c4", "feather"), "band_dk": ("#3e2a24", "feather"),
              **COMMON_MATS},
        zones=[(tuple(f"Fan-{i}" for i in range(1, 8)), {"front", "back"}, rows_top(2), "band"),
               (tuple(f"Fan-{i}" for i in range(1, 8)), {"front", "back"}, lambda P, N, U, V, w, h: (V >= 2) & (V < 4), "band_dk"),
               ("L-Wing", {"left", "right"}, stripes(1, 3, 1), "band_dk"), BLUSH(3.6, 25.8, 1.5, 0.9), ("Head", {"front"}, ALL, "skin"), ("Head", {"top", "left", "right"}, below(27), "skin")])

@pet
def wolf():
    nodes = quad(dict(body=(14, 13, 22), body_y=10, body_z=-2, leg=(4, 11, 4), leg_x=4.5, leg_zf=6, leg_zb=-9,
        head=(15, 14, 13), head_c=(0, 29, 11), snout=((7, 5, 5), (0, 25, 20), "cream"),
        eye=((5, 6), 4, 30), iris="#d89a34",
        ears=pair(B("L-Ear", "Head", (4.5, 35.5, 9.5), (5, 4, 2), (0, 2, 0), rot=(0, 0, -14), mat="fur"),
                  B("L-Ear-Tip", "Head", (5.4, 39.3, 9.5), (3, 2, 2), (0, 1, 0), rot=(0, 0, -14), mat="fur_dk")),
        tail=[B("Tail", "Body", (0, 20, -13), (5, 5, 12), (0, 0, -5.5), rot=(32, 0, 0), mat="fur")],
        extras=[B("Ruff", "Body", (0, 21.5, 6), (16, 7, 7), mat="cream")]))
    return dict(nodes=nodes, rig="quad", height=44,
        mats={"fur": ("#8e96a4", "fur"), "fur_dk": ("#5e6676", "fur"), "cream": ("#ece4d6", "fur"), "ear_in": ("#e2b4b0", "smooth"), **COMMON_MATS},
        zones=[(("L-Front-Leg", "L-Back-Leg"), ALL, below(3.5), "cream"), ("Body", {"bottom"}, ALL, "cream"),
               ("Tail", ALL, lambda P, N, U, V, w, h: P[:, 1] > 23.5, "cream"),
               ("Head", {"top"}, ALL, "fur_dk"), ("Body", {"top"}, ALL, "fur_dk"),
               ("L-Ear", {"front"}, lambda P, N, U, V, w, h: (U >= 1) & (U < w - 1) & (V >= 2), "ear_in"),
               ("Snout", {"front", "top"}, AND(ell(0, 27.2, 1.8, 1.0)), "nose"), ("Snout", {"front"}, rect(-0.5, 0.5, 24.2, 26.3), "mouth"), ("Snout", {"front"}, rect(-1.5, 1.5, 23, 23.9), "mouth"),
               BLUSH(5, 26)])

@pet
def hawk():
    nodes = [E("Origin", None, (0, 0, 0)), B("Body", "Origin", (0, 13.5, 0), (13, 15, 12), mat="feather"),
             B("Head", "Body", (0, 21, -2), (13, 11, 11), (0, 5.5, 3), mat="feather"),
             B("Beak", "Head", (0, 25.5, 7.5), (3, 3, 3), mat="beak"),
             B("Beak-Tip", "Beak", (0, 24, 8.5), (3, 1, 2), mat="beak_dk"),
             B("Tail", "Body", (0, 8, -5), (8, 2, 9), (0, 0, -4), rot=(-28, 0, 0), mat="feather_dk")]
    nodes += pair(B("L-Wing", "Body", (7.5, 20, 0), (2, 12, 11), (0.5, -5.5, -0.5), mat="feather_dk"),
                  B("L-Leg", "Body", (3, 6.5, 1), (2, 4, 2), (0, -2, 0), mat="beak"),
                  B("L-Tuft", "Head", (5, 32, 0), (3, 2, 3), (0, 1, 0), rot=(0, 0, -20), mat="feather_dk"))
    nodes += pair(B("L-Foot", "L-Leg", (3, 1.5, 1.5), (3, 1, 4), (0, -0.5, 1), mat="beak"))
    nodes += face("Head", (0, 26.5, 1), (13, 11, 11), (5, 6), 3.6, 27.5, "#e0a028", "feather")
    return dict(nodes=nodes, rig="hawk", height=36,
        mats={"feather": ("#9a6c46", "feather"), "feather_dk": ("#6e4a30", "feather"), "cream": ("#efe2c6", "feather"),
              "bar": ("#b08860", "feather"), "beak": ("#eabc3a", "smooth"), "beak_dk": ("#4a3a40", "smooth"), **COMMON_MATS},
        zones=[("Body", {"front", "bottom"}, ALL, "cream"), ("Body", {"front"}, stripes(1, 3, 1), "bar"),
               ("Head", {"front"}, below(25), "cream"), BLUSH(5.0, 24.6, 1.6, 0.9),
               ("L-Wing", {"left", "right"}, AND(stripes(1, 4, 1), lambda P, N, U, V, w, h: V > 3), "feather"),
               ("Tail", {"top"}, stripes(2, 3, 1), "cream")])

def _sheep(o_extra, coat, face_mat, horn, saddle_z=0):
    o = dict(body=(30, 24, 38), body_y=20, body_z=-2, leg=(8, 22, 8), leg_x=8.5, leg_zf=10, leg_zb=-14,
             head=(20, 19, 17), head_c=(0, 52.5, 24), snout=((10, 7, 4), (0, 46.5, 34.5), face_mat),
             eye=((6, 7), 5, 54), iris="#a87a3a", head_mat=face_mat, body_mat=coat, leg_mat=face_mat, lid_mat=face_mat)
    o.update(o_extra)
    hc = o["head_c"]; hw, hh, hd = o["head"]; top = hc[1] + hh / 2
    horns = pair(B("L-Horn", "Head", (hw / 2 - 1, top - 3, hc[2] - 1), (5, 6, 9), (2, 0, -2), mat=horn),
                 B("L-Horn-Back", "Head", (hw / 2 + 1.5, top - 9, hc[2] - 6.5), (5, 9, 5), mat=horn),
                 B("L-Horn-Front", "Head", (hw / 2 + 1.5, top - 14.5, hc[2] - 2), (5, 5, 7), mat=horn),
                 B("L-Horn-Tip", "Head", (hw / 2 + 1.5, top - 12, hc[2] + 3), (4, 4, 3), (0, 1.5, 0), rot=(-30, 0, 0), mat=horn))
    ears = pair(B("L-Ear", "Head", (hw / 2, top - 7, hc[2] + 3), (5, 2, 3), (2.5, 0, 0), rot=(0, 0, -20), mat=face_mat))
    o["ears"] = ears
    bt = o["body_y"] + o["body"][1]
    o["tail"] = [B("Tail", "Body", (0, bt - 4, o["body_z"] - o["body"][2] / 2), (6, 7, 3), (0, -3, -1), mat=coat)]
    o["extras"] = horns + saddle(bt, saddle_z, side_x=o["body"][0] / 2) + o.get("extras", [])
    return quad(o), o

@pet
def ram():
    nodes, o = _sheep({"extras": [B("Wool-Cap", "Head", (0, 61.5, 23), (21, 5, 13), mat="wool")]}, "wool", "face", "horn")
    return dict(nodes=nodes, rig="quad", height=64, mount=True,
        mats={"wool": ("#ece6da", "wool"), "face": ("#5a4a44", "fur"), "horn": ("#c8ae80", "horn"), "face_lt": ("#7a665c", "fur"), **COMMON_MATS,
              "blanket": ("#3c64a8", "cloth"), "trim": ("#e0b24a", "gold")},
        zones=[(("L-Front-Leg", "L-Back-Leg"), ALL, below(3), "hoof"), ("Snout", {"front"}, AND(ell_sym(2, 48, 1, 1.2)), "nose"),
               ("Snout", {"front"}, rect(-1.5, 1.5, 43.6, 44.4), "mouth"),
               ("Saddle-Blanket", ALL, edges(1), "trim"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "trim"),
               BLUSH(6.2, 49.3, 2.4, 1.2), (("L-Front-Leg", "L-Back-Leg"), ALL, above(18), "wool")])

@pet
def mouflon():
    nodes, o = _sheep({"body": (26, 22, 36), "body_y": 21, "leg": (7, 23, 7), "leg_x": 7.5}, "fur", "fur", "horn_dk")
    return dict(nodes=nodes, rig="quad", height=64, mount=True,
        mats={"fur": ("#a85a38", "fur"), "cream": ("#efe4d0", "fur"), "horn_dk": ("#6a5446", "horn"), **COMMON_MATS,
              "blanket": ("#efe8da", "cloth"), "trim": ("#e0b24a", "gold"), "leather": ("#8a5a34", "leather")},
        zones=[(("L-Front-Leg", "L-Back-Leg"), ALL, below(3), "hoof"), (("L-Front-Leg", "L-Back-Leg"), ALL, AND(below(10), above(3)), "cream"),
               ("Body", ALL, belly_wave(26), "cream"), ("Snout", {"front"}, below(46), "cream"), ("Head", {"front"}, AND(rect(-1.5, 1.5, 50, 60)), "cream"), ("Snout", {"front"}, AND(ell_sym(2, 48, 1, 1.2)), "nose"),
               ("Snout", {"front"}, rect(-1.5, 1.5, 43.6, 44.4), "mouth"), ("Tail", ALL, ALL, "cream"),
               ("Saddle-Blanket", ALL, edges(1), "trim"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "trim"),
               BLUSH(6.2, 49.3, 2.4, 1.2)])

@pet
def horse():
    o = dict(body=(24, 22, 40), body_y=26, body_z=-2, leg=(8, 28, 8), leg_x=7.5, leg_zf=12, leg_zb=-15,
             head=(19, 18, 19), head_c=(0, 70, 24), snout=((13, 10, 6), (0, 64, 36.5), "muzzle"),
             eye=((6, 7), 5, 72.5), iris="#5a3418", neck_parent="Neck")
    o["ears"] = pair(B("L-Ear", "Head", (5.5, 78.5, 20), (4, 6, 3), (0, 3, 0), rot=(0, 0, -12), mat="fur"))
    o["tail"] = [B("Tail", "Body", (0, 45, -22), (6, 20, 6), (0, -9, 0), rot=(22, 0, 0), mat="mane")]
    o["extras"] = [B("Neck", "Body", (0, 54, 15), (14, 18, 13), mat="fur"),
                   B("Mane", "Neck", (0, 62, 8), (4, 26, 5), mat="mane"),
                   B("Forelock", "Head", (0, 79.5, 33), (7, 4, 3), mat="mane")] + saddle(48, -2, w=16, d=14, blanket=(20, 18), side_x=12)
    nodes = quad(o)
    return dict(nodes=nodes, rig="quad", height=84, mount=True,
        mats={"fur": ("#9a5e36", "fur"), "mane": ("#4a3028", "fur"), "muzzle": ("#c49470", "fur"), "sock": ("#efe4d0", "fur"), **COMMON_MATS,
              "blanket": ("#3c8a5c", "cloth")},
        zones=[(("L-Front-Leg", "L-Back-Leg"), ALL, below(3), "hoof"), ("L-Front-Leg", ALL, AND(below(9), above(3)), "sock"),
               ("Head", {"front"}, AND(rect(-1.5, 1.5, 66, 77)), "sock"), ("Snout", {"top"}, rect(-1.5, 1.5, -99, 99), "sock"),
               ("Snout", {"front"}, AND(ell_sym(3.2, 66, 1.1, 1.4)), "nose"), ("Snout", {"front"}, rect(-2, 2, 60.6, 61.4), "mouth"),
               ("Saddle-Blanket", ALL, edges(1), "gold"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "gold"),
               BLUSH(6.6, 67.6, 2.0, 1.0)])

@pet
def camel():
    o = dict(body=(24, 20, 36), body_y=28, body_z=-2, leg=(7, 30, 7), leg_x=7.5, leg_zf=10, leg_zb=-13,
             head=(17, 15, 19), head_c=(0, 70.5, 26), snout=((12, 8, 5), (0, 65, 38), "muzzle"),
             eye=((6, 7), 4.4, 73), iris="#4a2c18", neck_parent="Neck")
    o["ears"] = pair(B("L-Ear", "Head", (7, 77.5, 20), (3, 4, 2), (0, 2, 0), rot=(0, 0, -25), mat="fur"))
    o["tail"] = [B("Tail", "Body", (0, 46, -20), (3, 12, 3), (0, -6, 0), rot=(15, 0, 0), mat="fur_dk")]
    o["extras"] = [B("Neck", "Body", (0, 52, 17), (11, 22, 11), mat="fur"),
                   B("Hump", "Body", (0, 54, -2), (18, 12, 20), mat="fur")] + \
                  [B("Saddle-Blanket", "Hump", (0, 59, -2), (22, 4, 18), mat="blanket"),
                   B("Saddle", "Hump", (0, 62.5, -2), (14, 3, 12), mat="leather"),
                   B("Saddle-Horn", "Saddle", (0, 65, 2.5), (3, 2, 2), mat="gold")] + \
                  pair(B("L-Tassel", "Saddle-Blanket", (11.5, 55, -2), (1, 6, 16), mat="tassel"))
    nodes = quad(o)
    return dict(nodes=nodes, rig="quad", height=80, mount=True,
        mats={"fur": ("#d4aa6c", "fur"), "fur_dk": ("#a07848", "fur"), "muzzle": ("#e6c898", "fur"), "tassel": ("#d8463e", "cloth"),
              "stripe": ("#e8c24a", "cloth"), **COMMON_MATS, "blanket": ("#3a6ab0", "cloth")},
        zones=[(("L-Front-Leg", "L-Back-Leg"), ALL, below(3), "hoof"), (("L-Front-Leg", "L-Back-Leg"), ALL, AND(above(13), below(17)), "fur_dk"),
               ("Saddle-Blanket", ALL, edges(1), "stripe"),
               ("L-Tassel", ALL, rows_bottom(2), "stripe"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "gold"),
               ("Snout", {"front"}, AND(ell_sym(3, 66.5, 1.0, 1.2)), "nose"), ("Snout", {"front"}, rect(-1.5, 1.5, 62, 62.8), "mouth"),
               ("Head", {"top"}, ALL, "fur_dk"), BLUSH(6.2, 68.4, 1.8, 0.9)])

@pet
def skrill():
    """original 'stormwing': a round little storm-bat-bird that hovers (not the vanilla Skrill design)"""
    nodes = [E("Origin", None, (0, 0, 0)), B("Body", "Origin", (0, 22, -1), (14, 12, 14), mat="fur"),
             B("Head", "Body", (0, 27, 1), (14, 13, 12), (0, 6.5, 5), mat="fur"),
             B("Beak", "Head", (0, 30.5, 13), (5, 3, 3), mat="spark"),
             B("Crest-1", "Head", (0, 39.5, 8), (2, 4, 2), (0, 2, 0), rot=(-25, 0, 0), mat="spark"),
             B("Crest-2", "Head", (0, 39.5, 4.5), (2, 5, 2), (0, 2.5, 0), rot=(-40, 0, 0), mat="spark"),
             B("Crest-3", "Head", (0, 39.5, 1), (2, 4, 2), (0, 2, 0), rot=(-58, 0, 0), mat="spark"),
             B("Tail", "Body", (0, 20, -8), (3, 3, 10), (0, 0, -5), mat="fur"),
             B("Tail-Spark", "Tail", (0, 20, -19), (5, 5, 3), mat="spark")]
    nodes += pair(B("L-Wing", "Body", (7, 25, 0), (12, 2, 3), (6, 0, 0), mat="fur_dk"),
                  B("L-Foot", "Body", (3.5, 16, 2), (3, 3, 3), (0, -1.5, 0), mat="spark"))
    nodes += pair(B("L-Wing-Skin", "L-Wing", (8, 25, -1.5), (15, 1, 10), (5.5, 0, -5), mat="membrane"),
                  B("L-Ear", "Head", (6, 39.5, 4), (3, 4, 2), (0, 2, 0), rot=(0, 0, -25), mat="fur_dk"))
    nodes += face("Head", (0, 33.5, 6), (14, 13, 12), (5, 6), 3.8, 34.5, "#3ac8e0", "fur")
    return dict(nodes=nodes, rig="flyer", height=42,
        mats={"fur": ("#4a72b8", "fur"), "fur_dk": ("#34508c", "fur"), "cream": ("#d8e4f2", "fur"), "spark": ("#f2cc4a", "gold"),
              "membrane": ("#8a64c8", "membrane"), **COMMON_MATS, "blush": ("#e89ac8", "fur")},
        zones=[("Body", {"front", "bottom"}, ALL, "cream"), ("Head", {"front"}, below(30), "cream"),
               ("L-Wing-Skin", {"top", "bottom"}, lambda P, N, U, V, w, h: (U % 5 == 2), "fur_dk"), BLUSH(5.0, 31.6, 1.6, 0.9)])


# ================================================================== v2 rideables (Skyy 2026-10-08: "look more like the hytale horses",
# Ram "more tough and aggressive ... more like an actual ram", Camel + Mouflon read better). Real-animal proportions, original art.
def side_eyes(head, x, y, z, size, iris, lid_mat):
    """eyes on the sides of a long head (like real horses / sheep); quads turned to face outward"""
    w, h = size
    return pair(Q("L-Eye", head, (x + 0.1, y, z), size, mat="eye", rot=(0, 90, 0), iris=iris),
                Q("L-Eyelid", head, (x + 0.2, y + h / 2 + 0.3, z), size, mat="lid", rot=(0, 90, 0), lid_mat=lid_mat, stretch=(1, 0.1, 1)))

def hoofed_legs(x, zf, zb, top, leg, cuff=None, hoof=(10, 6, 11), upper_f=None, upper_b=None, leg_mat="fur", cuff_mat="feather_w", hoof_mat="hoof"):
    """one swinging node per leg (named like the small pets so the shared Walk/Run work) + child cuff / hoof / upper muscle"""
    lw, lh, ld = leg
    out = []
    for nm, z, up in (("L-Front-Leg", zf, upper_f), ("L-Back-Leg", zb, upper_b)):
        out.append(B(nm, "Body", (x, top, z), leg, (0, -lh / 2, 0), mat=leg_mat))
        out.append(B(nm.replace("Leg", "Hoof"), nm, (x, hoof[1] / 2, z + 0.5), hoof, mat=hoof_mat))
        if cuff:
            out.append(B(nm.replace("Leg", "Cuff"), nm, (x, hoof[1] + cuff[1] / 2 - 1, z + 0.5), cuff, mat=cuff_mat))
        if up:
            out.append(B(nm.replace("Leg", "Upper"), nm, (x, top - up[1] / 2 + 3, z), up, mat=leg_mat))
    res = []
    for n in out:
        res += [n, mir(n)]
    return res

def tack(top_y, z, side_x, blanket, seat=(14, 3, 14), trim="gold", blanket_mat="blanket"):
    """original saddle: blanket, seat with raised pommel + cantle, girth straps, stirrups"""
    w, h, d = seat
    out = [B("Saddle-Blanket", "Body", (0, top_y + 0.5, z), (blanket[0], 1, blanket[1]), mat=blanket_mat),
           B("Saddle", "Body", (0, top_y + 1 + h / 2, z), seat, mat="leather"),
           B("Saddle-Pommel", "Saddle", (0, top_y + 1 + h + 1.5, z + d / 2 - 1.5), (w - 4, 3, 3), mat="leather"),
           B("Saddle-Horn", "Saddle-Pommel", (0, top_y + 1 + h + 3.5, z + d / 2 - 1.5), (3, 2, 2), mat=trim),
           B("Saddle-Cantle", "Saddle", (0, top_y + 1 + h + 1.5, z - d / 2 + 1.5), (w - 2, 3, 3), mat="leather")]
    out += pair(B("L-Strap", "Saddle", (side_x + 0.5, top_y - 5, z), (1, 12, 3), mat="leather"),
                B("L-Stirrup", "L-Strap", (side_x + 1.2, top_y - 12, z), (2, 2, 5), mat=trim))
    return out

@pet
def horse():
    # bay horse with a dark shaggy mane + tail, white blaze, white feathered fetlocks and dark hooves (vanilla-like blocking)
    n = [E("Origin", None, (0, 0, 0)),
         B("Body", "Origin", (0, 56, 0), (28, 28, 54), mat="fur"),
         B("Chest", "Body", (0, 55, 28), (26, 24, 8), mat="fur"),
         B("Neck", "Body", (0, 62, 26), (16, 32, 17), (0, 15, 1.5), rot=(34, 0, 0), mat="fur"),
         B("Mane", "Neck", (0, 77, 20), (20, 34, 8), mat="mane"),
         B("Head", "Neck", (0, 92, 27), (16, 16, 30), (0, 1, 11), rot=(14, 0, 0), mat="fur"),
         B("Jaw", "Head", (0, 84, 33), (14, 5, 14), mat="fur"),
         B("Muzzle", "Head", (0, 90.5, 57.5), (13, 13, 9), mat="muzzle"),
         B("Noseband", "Muzzle", (0, 93.5, 57), (14, 2, 10), mat="leather"),
         B("Forelock", "Head", (0, 102, 36), (10, 3, 14), mat="mane"),
         B("Forelock-Hang", "Forelock", (0, 99.5, 44), (10, 7, 2), mat="mane"),
         B("Tail", "Body", (0, 68, -28), (11, 36, 9), (0, -16, -2), rot=(18, 0, 0), mat="mane")]
    n += pair(B("L-Ear", "Head", (4.5, 100, 28), (4, 8, 3), (0, 4, 0), rot=(-38, 0, -10), mat="fur"),
              B("L-Cheekstrap", "Head", (8.3, 93.5, 51), (1, 14, 2), mat="leather"))
    n += hoofed_legs(9, 19, -19, 48, (10, 34, 11), cuff=(13, 8, 13), hoof=(12, 7, 13), upper_f=(12, 16, 13), upper_b=(12, 18, 15))
    n += side_eyes("Head", 8, 95.5, 44, (5, 5), "#4a2a16", "fur")
    n += tack(70, 0, 14, (26, 24), seat=(16, 3, 16))
    return dict(nodes=n, rig="quad", height=116, mount=True,
        mats={"fur": ("#94502c", "fur"), "mane": ("#3a2a2c", "fur"), "muzzle": ("#ead8c4", "fur"), "feather_w": ("#ece6dc", "wool"),
              "white": ("#eee6da", "fur"), **COMMON_MATS, "hoof": ("#3e3236", "smooth"), "blanket": ("#3c6e9c", "cloth")},
        zones=[("Head", {"front"}, lambda P, N, U, V, w, h: (U >= 5) & (U <= 9), "white"),
               ("Head", {"top"}, lambda P, N, U, V, w, h: (U >= 5) & (U <= 9) & (V >= 12), "white"),
               ("Muzzle", {"front"}, lambda P, N, U, V, w, h: ((U == 2) | (U == 9)) & (V >= 5) & (V <= 7), "nose"),
               ("Muzzle", {"front"}, lambda P, N, U, V, w, h: (V == 10) & (U >= 3) & (U <= 8), "mouth"),
               ("Muzzle", {"top", "left", "right"}, lambda P, N, U, V, w, h: V < 2, "fur"),
               (("L-Front-Leg", "L-Back-Leg"), ALL, below(18), "white"),
               ("Saddle-Blanket", ALL, edges(1), "gold"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "gold"),
               ("Body", {"bottom"}, ALL, "fur_dk"), ("Mane", {"front"}, ALL, "fur")],
        extra_mats={"fur_dk": ("#7a4024", "fur")})

@pet
def camel():
    # two-hump (Bactrian) camel: the saddle sits BETWEEN the humps; S-curved neck, droopy lip, knobby knees, wide padded feet
    n = [E("Origin", None, (0, 0, 0)),
         B("Body", "Origin", (0, 64, 0), (24, 22, 46), mat="fur"),
         B("Hump-Front", "Body", (0, 79, 11.5), (18, 8, 16), mat="fur"),
         B("Hump-Front-Mid", "Hump-Front", (0, 86, 11.5), (14, 6, 11), mat="fur"),
         B("Hump-Front-Top", "Hump-Front", (0, 90.5, 11.5), (9, 3, 7), mat="wool"),
         B("Hump-Back", "Body", (0, 78.5, -13.5), (18, 7, 15), mat="fur"),
         B("Hump-Back-Mid", "Hump-Back", (0, 85, -13.5), (13, 6, 10), mat="fur"),
         B("Hump-Back-Top", "Hump-Back", (0, 89.5, -13.5), (8, 3, 6), mat="wool"),
         B("Neck-Low", "Body", (0, 66, 21), (13, 24, 13), (0, 10, 2), rot=(68, 0, 0), mat="fur"),
         B("Neck-Shag", "Neck-Low", (0, 76, 29.5), (14, 18, 4), mat="wool"),
         B("Neck", "Neck-Low", (0, 86, 23), (10, 24, 10), (0, 10, 0), rot=(-74, 0, 0), mat="fur"),
         B("Head", "Neck", (0, 106, 23), (13, 13, 22), (0, 2, 8), rot=(14, 0, 0), mat="fur"),
         B("Muzzle", "Head", (0, 105, 46), (11, 9, 8), mat="muzzle"),
         B("Lip", "Muzzle", (0, 100.5, 45.5), (9, 3, 7), (0, 0, 2), rot=(16, 0, 0), mat="muzzle"),
         B("Tail", "Body", (0, 72, -23.5), (3, 16, 3), (0, -8, 0), rot=(12, 0, 0), mat="fur"),
         B("Tail-Tuft", "Tail", (0, 57, -23.5), (5, 6, 4), mat="wool")]
    n += pair(B("L-Ear", "Head", (5.5, 114.5, 26), (3, 5, 2), (0, 2.5, 0), rot=(-20, 0, -30), mat="fur"))
    # long thin legs: upper + knobby knee + lower + wide pad
    for nm, z in (("L-Front-Leg", 16), ("L-Back-Leg", -16)):
        x = 8
        leg = [B(nm, "Body", (x, 56, z), (8, 26, 9), (0, -12, 0), mat="fur"),
               B(nm.replace("Leg", "Knee"), nm, (x, 30, z), (10, 6, 10), mat="fur_dk"),
               B(nm.replace("Leg", "Shin"), nm, (x, 17, z), (7, 22, 8), mat="fur"),
               B(nm.replace("Leg", "Foot"), nm, (x, 2.5, z + 1), (11, 5, 13), mat="pad")]
        for q in leg:
            n += [q, mir(q)]
    n += side_eyes("Head", 6.5, 110.5, 36, (5, 4), "#3a2414", "fur_dk")
    n += [B("Saddle-Blanket", "Body", (0, 75.5, -1), (26, 1, 12), mat="blanket"),
          B("Saddle", "Body", (0, 77.5, -1), (14, 3, 9), mat="leather"),
          B("Saddle-Horn", "Saddle", (0, 80, 2.5), (3, 2, 2), mat="gold")]
    n += pair(B("L-Blanket-Side", "Saddle-Blanket", (13.5, 70, -1), (1, 10, 12), mat="blanket"),
              B("L-Tassel", "L-Blanket-Side", (13.5, 63.5, -1), (1, 3, 12), mat="tassel"),
              B("L-Stirrup", "L-Blanket-Side", (14.6, 62, -1), (2, 2, 5), mat="gold"))
    return dict(nodes=n, rig="quad", height=118, mount=True,
        mats={"fur": ("#d2a464", "fur"), "fur_dk": ("#a87840", "fur"), "wool": ("#8a5a34", "wool"), "muzzle": ("#e4c494", "fur"),
              "pad": ("#6a5040", "smooth"), "tassel": ("#d8463e", "cloth"), "stripe": ("#e8c24a", "cloth"), **COMMON_MATS,
              "blanket": ("#3a6ab0", "cloth")},
        zones=[("Muzzle", {"front"}, lambda P, N, U, V, w, h: ((U == 2) | (U == 7)) & (V >= 2) & (V <= 4), "nose"),
               ("Lip", {"front"}, rows_top(1), "mouth"),
               ("Saddle-Blanket", ALL, edges(1), "stripe"), ("L-Blanket-Side", ALL, lambda P, N, U, V, w, h: (V % 4) == 1, "stripe"),
               ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "gold"),
               ("Hump-Front-Mid", {"left", "right", "front", "back"}, rows_top(3), "wool"), ("Hump-Back-Mid", {"left", "right", "front", "back"}, rows_top(3), "wool"), (("Hump-Front-Mid", "Hump-Back-Mid"), {"top"}, ALL, "wool"),
               ("Head", {"top"}, lambda P, N, U, V, w, h: V < 6, "wool")])

@pet
def ram():
    # Warrior's war-ram: heavy horns spiralling round the sides of the head, a heavy brow, narrow determined eyes,
    # a big wool chest, sturdy legs with wool cuffs, a steel chest plate + face strip, a red saddle cloth with gold trim
    n = [E("Origin", None, (0, 0, 0)),
         B("Body", "Origin", (0, 42, -2), (30, 26, 44), mat="wool"),
         B("Wool-Front", "Body", (0, 44, 18), (34, 28, 14), mat="wool"),
         B("Wool-Back", "Body", (0, 45, -20), (32, 24, 8), mat="wool"),
         B("Chest-Plate", "Wool-Front", (0, 40, 25.5), (22, 16, 2), mat="steel"),
         B("Neck", "Body", (0, 50, 25), (16, 14, 12), (0, 5, 1), rot=(22, 0, 0), mat="wool"),
         B("Head", "Neck", (0, 57, 27), (18, 17, 20), (0, 2.5, 9), rot=(14, 0, 0), mat="face"),
         B("Muzzle", "Head", (0, 54, 50), (13, 10, 9), mat="face_lt"),
         B("Brow", "Head", (0, 63.5, 41.5), (20, 4, 10), mat="face"),
         B("Topknot", "Head", (0, 69.5, 33), (10, 4, 9), mat="wool"),
         B("Tail", "Body", (0, 50, -24), (9, 9, 4), (0, -3, -1), mat="wool")]
    n += pair(B("L-Horn-Base", "Head", (10.5, 66, 31), (10, 9, 14), mat="horn"),
              B("L-Horn-Back", "Head", (14, 57.5, 21.5), (9, 15, 8), mat="horn"),
              B("L-Horn-Curl", "Head", (15, 48, 28.5), (8, 8, 13), mat="horn"),
              B("L-Horn-Tip", "Head", (15, 51.5, 37), (6, 6, 7), rot=(-35, -20, 0), mat="horn_tip"),
              B("L-Ear", "Head", (9, 59, 33), (5, 2, 4), (2, 0, 0), rot=(0, 0, -30), mat="face"))
    n += side_eyes("Head", 9, 60.5, 41.5, (6, 4), "#e09a2a", "face")
    n += tack(55, -3, 15, (24, 24), seat=(14, 3, 14))
    # lower, heavier stance: everything above the legs drops 4 units, legs are shorter + thicker
    for q in n:
        if q["name"] != "Origin":
            q["pivot"] = (q["pivot"][0], q["pivot"][1] - 4, q["pivot"][2])
    n += hoofed_legs(9.5, 14, -16, 28, (10, 20, 10), cuff=(13, 7, 13), hoof=(11, 6, 11), leg_mat="leg", cuff_mat="wool")
    return dict(nodes=n, rig="quad", height=68, mount=True,
        mats={"wool": ("#e2dccc", "wool"), "face": ("#4c4246", "fur"), "face_lt": ("#62565a", "fur"), "leg": ("#45393c", "fur"),
              "horn": ("#b08a5a", "smooth"), "horn_tip": ("#c8a676", "smooth"), "horn_dk": ("#7a5a3c", "smooth"), "steel": ("#6e7884", "gold"), "stud": ("#e0b24a", "gold"),
              **COMMON_MATS, "blanket": ("#a8382e", "cloth"), "leather": ("#5c3a26", "leather")},
        zones=[("Muzzle", {"front"}, lambda P, N, U, V, w, h: ((U == 2) | (U == 10)) & (V >= 3) & (V <= 4), "nose"),
               ("Muzzle", {"front"}, lambda P, N, U, V, w, h: (V == 7) & (U >= 3) & (U <= 9), "mouth"),
               ("Chest-Plate", {"front"}, lambda P, N, U, V, w, h: ((U == 2) | (U == w - 3)) & (V % 4 == 2), "stud"),
               ("Chest-Plate", {"front"}, lambda P, N, U, V, w, h: (V == 0) | (V == h - 1), "stud"),
               ("Chamfron", {"front"}, lambda P, N, U, V, w, h: (U >= 2) & (U <= 3) & (V >= 2) & (V <= 3), "stud"),
               ("Saddle-Blanket", ALL, edges(1), "gold"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "gold"),
               ("L-Horn-Base", {"left", "right", "top", "bottom"}, stripes(2, 3, 1), "horn_dk"),
               ("L-Horn-Curl", {"left", "right", "top", "bottom"}, stripes(2, 3, 1), "horn_dk"),
               ("L-Horn-Back", {"left", "right", "front", "back"}, stripes(1, 3, 1), "horn_dk"),
               ("L-Horn-Tip", ALL, lambda P, N, U, V, w, h: V % 3 == 0, "horn_dk")])

@pet
def mouflon():
    # wild mountain sheep: short sleek red-brown coat, pale saddle patch, white belly / legs / muzzle / rump, dark chest + flank line,
    # big dark crescent horns sweeping back and round; slim and agile. Priest tack: cream cloth, gold trim, gold browband
    n = [E("Origin", None, (0, 0, 0)),
         B("Body", "Origin", (0, 44, -1), (20, 18, 38), mat="fur"),
         B("Chest", "Body", (0, 44.5, 19.5), (18, 14, 5), mat="dark"),
         B("Neck", "Body", (0, 48, 18), (11, 18, 11), (0, 7, 2), rot=(22, 0, 0), mat="fur"),
         B("Head", "Neck", (0, 62, 21), (12, 12, 18), (0, 1, 7), rot=(10, 0, 0), mat="fur"),
         B("Muzzle", "Head", (0, 60, 40), (9, 8, 6), mat="white"),
         B("Browband", "Head", (0, 66.5, 31), (13, 2, 2), mat="gold"),
         B("Tail", "Body", (0, 51, -20.5), (4, 7, 3), (0, -3, 0), rot=(15, 0, 0), mat="dark")]
    n += pair(B("L-Horn-Base", "Head", (4.5, 70.5, 26), (5, 6, 6), mat="horn"),
              B("L-Horn-Up", "Head", (6, 73.5, 20.5), (5, 5, 9), rot=(-15, 0, 0), mat="horn"),
              B("L-Horn-Back", "Head", (8, 69, 14), (5, 11, 5), rot=(15, 0, 0), mat="horn"),
              B("L-Horn-Low", "Head", (9.5, 60.5, 15.5), (5, 5, 9), rot=(25, 0, 0), mat="horn"),
              B("L-Horn-Tip", "Head", (10.5, 59.5, 22.5), (4, 4, 5), rot=(-20, -15, 0), mat="horn"),
              B("L-Ear", "Head", (6, 65.5, 25), (6, 3, 2), (3, 0, 0), rot=(0, 0, -25), mat="fur"))
    n += hoofed_legs(6.5, 13, -14, 38, (6, 32, 7), hoof=(7, 5, 8), leg_mat="fur", hoof_mat="hoof")
    n += side_eyes("Head", 6, 64.5, 31, (5, 5), "#b07a2a", "fur")
    n += tack(53, -2, 10, (20, 20), seat=(12, 3, 12))
    return dict(nodes=n, rig="quad", height=78, mount=True,
        mats={"fur": ("#a8582e", "fur"), "dark": ("#4a3026", "fur"), "white": ("#ece4d6", "fur"), "patch": ("#e6d2b2", "fur"),
              "horn": ("#6a5244", "horn"), **COMMON_MATS, "blanket": ("#efe6d2", "cloth"), "leather": ("#9a6a3c", "leather")},
        zones=[("Body", ALL, below(39.5), "white"), ("Body", {"left", "right"}, AND(above(39.5), below(41.5)), "dark"),
               ("Body", {"left", "right"}, ell(-11, 46.5, 6, 3.2, ax=(2, 1)), "patch"),
               ("Body", {"back"}, ell(0, 44, 6, 6), "white"),
               (("L-Front-Leg", "L-Back-Leg"), ALL, below(24), "white"),
               (("L-Front-Leg", "L-Back-Leg"), {"front"}, AND(below(24), above(8)), "dark"),
               ("Muzzle", {"front"}, lambda P, N, U, V, w, h: ((U == 2) | (U == 6)) & (V >= 2) & (V <= 3), "nose"),
               ("Muzzle", {"front"}, lambda P, N, U, V, w, h: (V == 6) & (U >= 2) & (U <= 6), "mouth"),
               ("Head", {"left", "right"}, lambda P, N, U, V, w, h: V >= h - 3, "white"),
               ("Saddle-Blanket", ALL, edges(1), "gold"), ("Saddle", {"left", "right", "front", "back"}, rows_top(1), "gold")])
