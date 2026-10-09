#!/usr/bin/env python3
"""Validate the Pebble files against the Hytale Models plugin rules (and, optionally, key-by-key against a
vanilla model for schema shape - pass --vanilla <dir with Model.blockymodel + Animations/>; nothing is copied).
Prints a report and exits 1 on any failure."""
import json, os, sys, glob, math, itertools
import numpy as np
from PIL import Image

ART = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "../../art/pebble")
VAN = sys.argv[sys.argv.index("--vanilla") + 1] if "--vanilla" in sys.argv else None
NPC = os.path.join(ART, "Common/NPC/SkyyTowns/Pebble")
fails, notes = [], []
def check(cond, msg):
    (notes if cond else fails).append(("OK   " if cond else "FAIL ") + msg)

model = json.load(open(os.path.join(NPC, "Pebble.blockymodel")))
tex = Image.open(os.path.join(NPC, "Pebble_Texture.png"))
TW, TH = tex.size
nodes = []
def walk(n, depth=0):
    nodes.append(n)
    for c in n.get("children", []): walk(c, depth + 1)
for n in model["nodes"]: walk(n)
check(len(nodes) <= 255, f"node count {len(nodes)} <= 255")
check(len({n['name'] for n in nodes}) == len(nodes), "node names unique")
check(len({n['id'] for n in nodes}) == len(nodes), "node ids unique")
check(TW % 32 == 0 and TH % 32 == 0, f"texture {TW}x{TH}: both sides multiples of 32")
check(tex.mode == "RGBA", "texture RGBA")
a = np.asarray(tex.convert("RGBA")).astype(int)
op = a[..., 3] == 255
check(set(np.unique(a[..., 3])) <= {0, 255}, "texture alpha is cut-out only (0/255)")
check(not ((a[..., :3] <= 12).all(-1) & op).any(), "no pure-black texels")
check(not ((a[..., :3] >= 243).all(-1) & op).any(), "no pure-white texels")
for n in nodes:
    q = n["orientation"]
    if abs(math.sqrt(sum(q[k] ** 2 for k in "xyzw")) - 1) > 1e-4: check(False, f"{n['name']}: orientation is a unit quaternion")

# UVs: every face rectangle = face size, inside the texture; overlaps only between identical (shared) rectangles
def face_size(face, s, typ):
    if typ == "quad": return s["x"], s["y"]
    return {"front": (s["x"], s["y"]), "back": (s["x"], s["y"]), "left": (s["z"], s["y"]), "right": (s["z"], s["y"]),
            "top": (s["x"], s["z"]), "bottom": (s["x"], s["z"])}[face]
rects = []
for n in nodes:
    sh = n["shape"]
    if sh["type"] == "none": continue
    want = ["front"] if sh["type"] == "quad" else ["front", "back", "left", "right", "top", "bottom"]
    if sorted(sh["textureLayout"]) != sorted(want): check(False, f"{n['name']}: has UVs for faces {want}")
    for f, tl in sh["textureLayout"].items():
        w, h = face_size(f, sh["settings"]["size"], sh["type"])
        x, y = tl["offset"]["x"], tl["offset"]["y"]
        # mirrored axis: Blockbench reads the offset as the far (right / bottom) edge of the region
        if tl["mirror"]["x"]: x -= w
        if tl["mirror"]["y"]: y -= h
        if not (isinstance(w, int) and isinstance(h, int)): check(False, f"{n['name']}.{f}: integer size {w}x{h}")
        ok = 0 <= x and 0 <= y and x + w <= TW and y + h <= TH
        if not ok: check(False, f"{n['name']}.{f}: UV rect {x},{y} {w}x{h} inside texture")
        check(tl["angle"] == 0, f"{n['name']}.{f}: angle 0") if tl["angle"] != 0 else None
        opaque = (a[y:y + h, x:x + w, 3] == 255).mean()
        if sh["type"] == "box": 
            if opaque < 1: check(False, f"{n['name']}.{f}: box face fully opaque")
        rects.append((x, y, w, h, n["name"], f))
check(all(0 <= r[0] and r[0] + r[2] <= TW and 0 <= r[1] and r[1] + r[3] <= TH for r in rects), f"all {len(rects)} face UV rects fit inside the texture, sized exactly to their faces")
bad_overlap = []
for r1, r2 in itertools.combinations(rects, 2):
    ix = min(r1[0] + r1[2], r2[0] + r2[2]) - max(r1[0], r2[0]); iy = min(r1[1] + r1[3], r2[1] + r2[3]) - max(r1[1], r2[1])
    if ix > 0 and iy > 0 and not (r1[0] == r2[0] and r1[1] == r2[1]):
        bad_overlap.append((r1[4:], r2[4:]))
check(not bad_overlap, f"no accidental UV overlaps (shared faces reuse an identical origin) {bad_overlap[:3]}")
for n in nodes:
    st = n["shape"]["stretch"]
    vals = [abs(st[k]) for k in "xyz"]
    if not all(0.7 <= v <= 1.3 for v in vals):
        notes.append(f"NOTE {n['name']}: stretch {st} outside 0.7-1.3 (hidden blink lid, same trick as vanilla eyelids)")

# rest-pose height (render module does the transforms)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_blocky import collect_faces
P = np.concatenate([f["P"] for f in collect_faces(model)])
lo, hi = P.min(0), P.max(0)
notes.append(f"INFO rest bounds x {lo[0]:.1f}..{hi[0]:.1f}  y {lo[1]:.1f}..{hi[1]:.1f}  z {lo[2]:.1f}..{hi[2]:.1f} units "
             f"-> height {hi[1]-lo[1]:.1f} units = {(hi[1]-lo[1])/64:.2f} blocks, width {(hi[0]-lo[0])/64:.2f}, depth {(hi[2]-lo[2])/64:.2f}")

# animations
names = {n["name"] for n in nodes}
anims = sorted(glob.glob(os.path.join(NPC, "Animations/*/*.blockyanim")))
for p in anims:
    an = json.load(open(p)); rel = os.path.relpath(p, NPC)
    check(set(an) == {"formatVersion", "duration", "holdLastKeyframe", "nodeAnimations"}, f"{rel}: top-level keys")
    for nn, ch in an["nodeAnimations"].items():
        check(nn in names, f"{rel}: node '{nn}' exists in the model") if nn not in names else None
        if set(ch) != {"position", "orientation", "shapeStretch", "shapeVisible", "shapeUvOffset"}:
            check(False, f"{rel}: {nn} channel keys")
        for c, kfs in ch.items():
            for k in kfs:
                if not (0 <= k["time"] < an["duration"]): check(False, f"{rel}: {nn}.{c} time {k['time']} in [0,{an['duration']})")
                if k["interpolationType"] not in ("smooth", "linear"): check(False, f"{rel}: interpolation type")
    notes.append(f"INFO {rel}: {an['duration']} frames = {an['duration']/60:.2f} s, hold={an['holdLastKeyframe']}, nodes {len(an['nodeAnimations'])}")
check(len(anims) == 6, f"{len(anims)} animation files")

if VAN:
    vm = json.load(open(glob.glob(os.path.join(VAN, "**/Model.blockymodel"), recursive=True)[0]))
    vnodes = []
    def vw(n):
        vnodes.append(n); [vw(c) for c in n.get("children", [])]
    [vw(n) for n in vm["nodes"]]
    vkeys = set().union(*[set(n) for n in vnodes]); vshape = set().union(*[set(n["shape"]) for n in vnodes])
    vset = set().union(*[set(n["shape"]["settings"]) for n in vnodes]); vtl = set().union(*[set(f) for n in vnodes for f in n["shape"].get("textureLayout", {}).values()])
    mk = set().union(*[set(n) for n in nodes]); ms = set().union(*[set(n["shape"]) for n in nodes])
    mset = set().union(*[set(n["shape"]["settings"]) for n in nodes]); mtl = set().union(*[set(f) for n in nodes for f in n["shape"].get("textureLayout", {}).values()])
    check(mk <= vkeys, f"node keys {sorted(mk)} are all used by vanilla")
    check(ms <= vshape, f"shape keys {sorted(ms)} are all used by vanilla")
    check(mset <= vset, f"settings keys {sorted(mset)} are all used by vanilla")
    check(mtl <= vtl, f"textureLayout face keys {sorted(mtl)} are all used by vanilla")
    check(set(model) - set(vm) <= {"format"}, f"top-level keys {sorted(model)} (vanilla {sorted(vm)}; 'format' is what the plugin itself writes)")
    vtypes = {n["shape"]["type"] for n in vnodes}; check({n["shape"]["type"] for n in nodes} <= vtypes, "shape types used by vanilla")
    va = json.load(open(glob.glob(os.path.join(VAN, "**/Idle.blockyanim"), recursive=True)[0]))
    check(set(va) == {"formatVersion", "duration", "holdLastKeyframe", "nodeAnimations"}, "vanilla anim top-level keys match ours")
    vch = set(next(iter(va["nodeAnimations"].values())))
    check(vch == {"position", "orientation", "shapeStretch", "shapeVisible", "shapeUvOffset"}, "vanilla anim channel keys match ours")

for line in notes + fails: print(line)
print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
