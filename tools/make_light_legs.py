"""make_light_legs - our own legs for the Ornate Bronze light-armor base (Copper / Iron tiers), 2026-10-07.

Skyy chose "Build our own" legs (vanilla Bronze_Ornate has none). Look matches the re-leathered Ornate Bronze set: light black leather
trousers, a dark strap + metal buckle round each thigh, a metal thigh guard, knee cop with a small side flare, front shin greave, a metal
boot rim, dark leather boots with a metal toe cap. Metal is painted in a bronze ramp so make_light_bases.tier_metal re-hues it per tier
like the vanilla pieces; leather pixels are returned so the re-hue skips them.

The rig = the vanilla Cobalt Legs root nodes (bone anchors, read-only from Assets.zip); every box is placed relative to the PLAYER bone
centre (Common/Characters/Player.blockymodel, measured in Blockbench 2026-10-07), so the root's own offset does not matter.
Used by make_light_bases.py; not run on its own.
"""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import make_light_chest as LC  # noqa: E402  (box / pack / Face / paint helpers)

TEX_W = 128
# player bone centres (x, y, z) + sizes, unposed
BONES = {
    "Pelvis": ((0, 51, 0), (26, 12, 18)),
    "R-Thigh": ((-7.5, 39, 1), (10, 20, 12)), "L-Thigh": ((7.5, 39, 1), (10, 20, 12)),
    "R-Calf": ((-7.5, 17, 1), (10, 24, 12)), "L-Calf": ((7.5, 17, 1), (10, 24, 12)),
    "R-Foot": ((-7.6, 4, 3), (14, 8, 20)), "L-Foot": ((7.6, 4, 3), (14, 8, 20)),
}
BRONZE = [LC.hx(c) for c in ("#3a220c", "#6e4618", "#a87228", "#d9a748", "#f6d98a")]


def root_nodes(rig):
    """The vanilla root nodes named like the bones, children cleared; returns {bone: (node, (dx, dy, dz))} where d = bone centre
    minus the node's anchor (position + offset)."""
    out = {}
    for n in rig["nodes"]:
        if n["name"] in BONES and n["name"] not in out:
            node = copy.deepcopy(n)
            node["children"] = []
            p, o = node["position"], (node.get("shape") or {}).get("offset") or {"x": 0, "y": 0, "z": 0}
            c = BONES[n["name"]][0]
            out[n["name"]] = (node, (c[0] - p["x"] - o["x"], c[1] - p["y"] - o["y"], c[2] - p["z"] - o["z"]))
    return out


def build(rig):
    roots = root_nodes(rig)
    box = LC.box

    def add(bone, name, size, pos, rot_z=0.0):
        node, d = roots[bone]
        node["children"].append(box(name, size, (pos[0] + d[0], pos[1] + d[1], pos[2] + d[2]), rot_z=rot_z))

    add("Pelvis", "PantsBase", (27, 12, 19), (0, 0, 0))
    for side, sx in (("R", -1), ("L", 1)):
        t, c, f = side + "-Thigh", side + "-Calf", side + "-Foot"
        add(t, side + "-Trouser", (11, 20, 13), (0, 0, 0))
        add(t, side + "-ThighStrap", (12, 2, 14), (0, -2, 0))
        add(t, side + "-ThighBuckle", (3, 3, 1), (sx * 1.5, -2, 7.2))
        add(t, side + "-ThighGuard", (8, 9, 2), (sx * 0.5, 4, 7))
        add(c, side + "-Shin", (11, 12, 13), (0, 6, 0))
        add(c, side + "-KneeCop", (8, 6, 3), (0, 10, 7))
        add(c, side + "-KneeFlare", (1, 5, 6), (sx * 5.5, 10, 3), rot_z=-sx * 10)
        add(c, side + "-BootShaft", (12, 13, 14), (0, -5.5, 0))
        add(c, side + "-BootRim", (13, 2, 15), (0, 1.5, 0))
        add(c, side + "-Greave", (8, 11, 2), (0, -4.5, 7.5))
        add(f, side + "-Boot", (15, 8, 21), (0, 0.5, 0))
        add(f, side + "-Sole", (16, 2, 22), (0, -3.5, 0))
        add(f, side + "-ToeCap", (15, 4, 4), (0, -1, 9.2))
    return {"nodes": [roots[b][0] for b in BONES], "lod": rig.get("lod", "auto")}


def bronze(f, rivets=True):
    """Metal in the bronze ramp: lit top, dark bottom, a raised border line and corner rivets (ornate look)."""
    for v in range(f.h):
        t = 1.0 - v / max(1, f.h - 1)
        for u in range(f.w):
            c = LC.mix(BRONZE[1], BRONZE[3], 0.15 + 0.7 * t + 0.1 * f.n(u, v))
            f.put(u, v, c)
    for u in range(f.w):
        f.put(u, 0, BRONZE[4])
        f.put(u, f.h - 1, BRONZE[0])
    for v in range(f.h):
        f.put(0, v, BRONZE[2])
        f.put(f.w - 1, v, BRONZE[0])
    if f.w >= 6 and f.h >= 6:
        for u in range(2, f.w - 2):
            f.put(u, 2, BRONZE[4])
            f.put(u, f.h - 3, BRONZE[1])
        if rivets:
            for u, v in ((1, 1), (f.w - 2, 1), (1, f.h - 2), (f.w - 2, f.h - 2)):
                f.put(u, v, BRONZE[4])


def leather_face(f, pal, stitch=True, seams=0):
    for v in range(f.h):
        g = 1.05 - 0.25 * (v / max(1, f.h - 1))
        for u in range(f.w):
            c = LC.mix(pal[2], pal[3], f.n(u, v) * 0.45)
            f.put(u, v, LC.mul(c, g))
    for u in range(f.w):
        f.put(u, f.h - 1, pal[0])
    for v in range(f.h):
        f.put(0, v, pal[1])
        f.put(f.w - 1, v, pal[1])
    if seams:
        for v in range(f.h):
            f.put(f.w // 2, v, pal[1])
    if stitch and f.w >= 5 and f.h >= 5:
        for v in range(2, f.h - 1, 2):
            f.put(2, v, pal[4])


def paint(model, place, height, light, dark):
    img = LC.SA.Img(TEX_W, height)
    leather_px = set()
    for i, ((name, face), rect) in enumerate(sorted(place.items())):
        f = LC.Face(img, rect, i * 11 + 5)
        part = name.split("-", 1)[-1]
        if part in ("PantsBase", "Trouser", "Shin"):
            leather_face(f, light, seams=(part == "Trouser" and face in ("front", "back")))
        elif part in ("ThighStrap", "BootShaft", "Boot", "Sole"):
            leather_face(f, dark, stitch=(part == "BootShaft"))
            if part == "Sole":
                for u in range(f.w):
                    for v in range(f.h):
                        f.put(u, v, dark[0] if (u + v) % 3 else dark[1])
        else:                                                  # ThighBuckle, ThighGuard, KneeCop, KneeFlare, BootRim, Greave, ToeCap
            bronze(f, rivets=part in ("ThighGuard", "Greave", "KneeCop"))
            if part == "ThighBuckle" and face == "front" and f.w >= 3:
                f.put(1, 1, dark[1])
            continue
        x0, y0, w, h = rect
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                leather_px.add((xx, yy))
    return img, leather_px


def make(rig, light, dark):
    """-> (model, texture Img, leather pixel set)"""
    model = build(rig)
    LC.TEX_W = TEX_W
    place, height = LC.pack(model)
    img, leather_px = paint(model, place, height, light, dark)
    return model, img, leather_px


if __name__ == "__main__":
    sys.exit("used by make_light_bases.py")
