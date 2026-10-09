#!/usr/bin/env python3
"""Validate every pet against the Hytale Models plugin rules + the SkyWynn art rules. Exit 1 on any failure."""
import json, math, os, sys
import numpy as np
from PIL import Image
ART = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../../art/pets")
FS = {"front": lambda s: (s["x"], s["y"]), "back": lambda s: (s["x"], s["y"]), "left": lambda s: (s["z"], s["y"]),
      "right": lambda s: (s["z"], s["y"]), "top": lambda s: (s["x"], s["z"]), "bottom": lambda s: (s["x"], s["z"])}
fails = []; total = 0
root = os.path.join(ART, "Common/NPC/SkyyPets")
for pet in sorted(os.listdir(root)):
    m = json.load(open(os.path.join(root, pet, "Models", pet + ".blockymodel")))
    tex = Image.open(os.path.join(root, pet, "Models", pet + "_Texture.png")); TW, TH = tex.size
    a = np.asarray(tex.convert("RGBA")).astype(int); op = a[..., 3] == 255
    nodes = []
    def walk(n):
        nodes.append(n); [walk(c) for c in n.get("children", [])]
    [walk(n) for n in m["nodes"]]
    def chk(c, msg):
        global total
        total += 1
        if not c: fails.append(f"{pet}: {msg}")
    chk(len(nodes) <= 255, "<= 255 nodes"); chk(len({n["name"] for n in nodes}) == len(nodes), "unique names")
    chk(TW % 32 == 0 and TH % 32 == 0, "texture multiple of 32"); chk(set(np.unique(a[..., 3])) <= {0, 255}, "cut-out alpha")
    chk(not ((a[..., :3] <= 12).all(-1) & op).any(), "no pure black"); chk(not ((a[..., :3] >= 243).all(-1) & op).any(), "no pure white")
    for n in nodes:
        q = n["orientation"]; chk(abs(math.sqrt(sum(q[k] ** 2 for k in "xyzw")) - 1) < 1e-4, n["name"] + " unit quat")
        sh = n["shape"]
        if sh["type"] == "none": continue
        s = dict(sh["settings"]["size"]); s.setdefault("z", 0)
        for f, tl in sh["textureLayout"].items():
            w, h = FS[f](s); ox, oy = tl["offset"]["x"], tl["offset"]["y"]
            u0, u1 = (ox - w, ox) if tl["mirror"]["x"] else (ox, ox + w)
            chk(0 <= u0 and u1 <= TW and 0 <= oy and oy + h <= TH, f"{n['name']}.{f} UV inside texture")
            reg = a[oy:oy + h, u0:u1, 3]
            if sh["type"] == "box": chk((reg == 255).all(), f"{n['name']}.{f} region fully painted")
    for d in ("Default",):
        for fn in os.listdir(os.path.join(root, pet, "Animations", d)):
            an = json.load(open(os.path.join(root, pet, "Animations", d, fn)))
            names = {n["name"] for n in nodes}
            chk(set(an["nodeAnimations"]) <= names, f"{fn} animates real nodes only")
            chk(all(k["time"] < an["duration"] for ch in an["nodeAnimations"].values() for v in ch.values() for k in v), f"{fn} keys < duration")
    for sub, nm, px in (("ModelsGenerated", f"SkyyPets_{pet}.png", 128), ("ItemsGenerated", f"SkyyPets_Pet_{pet}.png", 64)):
        ic = Image.open(os.path.join(ART, "Common/Icons", sub, nm)); chk(ic.size == (px, px) and ic.mode == "RGBA", f"icon {nm} {px}px RGBA")
print(f"{total} checks, {len(fails)} failures"); [print("FAIL", f) for f in fails]
sys.exit(1 if fails else 0)
