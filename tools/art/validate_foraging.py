#!/usr/bin/env python3
"""Structural checks for a SkyWynn Foraging armor set (default F1_Grove/Oak).
- JSON key-by-key vs the vanilla armor files (read-only reference; only KEY NAMES / value types are compared)
- node count <= 255, unique node ids + names per file, piece nodes named after real player bones
- every box: integer sizes, stretch in [0.7, 1.3] (abs), quaternion unit length
- every UV rect == its face size and inside the texture; no two faces share texels (except intended L/R mirrors)
- textures: sides multiples of 32, alpha only 0/255, no pure #000 / #fff texels
- icons: 64x64 RGBA
- determinism: rebuilding gives byte-identical files
Usage: python3 validate.py [art_root] [vanilla_armor_dir]
"""
import glob, hashlib, json, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = os.path.abspath(ARGS[0] if len(ARGS) > 0 else os.path.join(HERE, "../../art/gathering-armor"))
VAN = ARGS[1] if len(ARGS) > 1 else "/workspace/vanilla-ref/armor/Common/Items/Armors"
TIER, TREE = os.environ.get("GA_TIER", "F1_Grove"), os.environ.get("GA_TREE", "Oak")
MD = os.path.join(ROOT, "Common/Items/Armors/SkyyForaging", TIER, TREE)
PIECES = ("Head", "Chest", "Hands", "Legs")
BONES = {"Pelvis", "Belly", "Chest", "Head", "R-Arm", "L-Arm", "R-Forearm", "L-Forearm", "R-Hand", "L-Hand",
         "R-Thigh", "L-Thigh", "R-Calf", "L-Calf", "R-Foot", "L-Foot"}
FAIL = []

def bad(msg):
    FAIL.append(msg); print("  FAIL", msg)

def walk(nodes, fn, depth=0):
    for n in nodes:
        fn(n, depth)
        walk(n.get("children", []), fn, depth + 1)

def keyset(models):
    ks = {"root": set(), "node": set(), "shape": set(), "settings": set(), "layout": set(), "face": set()}
    def f(n, d):
        ks["node"] |= set(n); s = n["shape"]; ks["shape"] |= set(s); ks["settings"] |= set(s.get("settings", {}))
        ks["layout"] |= set(s.get("textureLayout", {}))
        for v in s.get("textureLayout", {}).values():
            ks["face"] |= set(v)
    for m in models:
        ks["root"] |= set(m); walk(m["nodes"], f)
    return ks

def face_size(sz, face):
    x, y, z = sz["x"], sz["y"], sz.get("z", 0)
    return {"front": (x, y), "back": (x, y), "left": (z, y), "right": (z, y), "top": (x, z), "bottom": (x, z)}[face]

van_models = [json.load(open(p, encoding="utf-8-sig")) for p in glob.glob(os.path.join(VAN, "*/*.blockymodel"))]
vk = keyset(van_models)
print("vanilla reference files:", len(van_models))
summary = {}
for p in PIECES:
    print("==", p)
    m = json.load(open(os.path.join(MD, p + ".blockymodel"), encoding="utf-8"))
    tex = np.asarray(Image.open(os.path.join(MD, p + "_Texture.png")).convert("RGBA"))
    th, tw = tex.shape[:2]
    ok = keyset([m])
    for k in ok:
        extra = ok[k] - vk[k]
        if extra:
            bad("%s: %s keys not used by vanilla: %s" % (p, k, sorted(extra)))
    if m.get("format") != "character":
        bad("%s: format %r" % (p, m.get("format")))
    nodes, ids, names = [], [], []
    walk(m["nodes"], lambda n, d: nodes.append((n, d)))
    for n, d in nodes:
        ids.append(n["id"]); names.append(n["name"])
    if len(nodes) > 255: bad("%s: %d nodes" % (p, len(nodes)))
    if len(set(ids)) != len(ids): bad("%s: duplicate ids" % p)
    if len(set(names)) != len(names): bad("%s: duplicate names" % p)
    used = np.zeros((th, tw), int); owners = {}
    boxes = 0
    for n, d in nodes:
        s = n["shape"]; q = n["orientation"]
        if abs(sum(q[k] ** 2 for k in "xyzw") - 1) > 1e-4: bad("%s/%s quaternion not unit" % (p, n["name"]))
        if s.get("settings", {}).get("isPiece"):
            if n["name"] not in BONES: bad("%s: piece node %s is not a player bone" % (p, n["name"]))
            continue
        if s["type"] == "none":
            continue
        boxes += s["type"] == "box"
        sz = s["settings"]["size"]
        if any(float(v) != int(v) for v in sz.values()): bad("%s/%s non-integer size" % (p, n["name"]))
        for k, v in s["stretch"].items():
            if not 0.7 <= abs(v) <= 1.3: bad("%s/%s stretch %s=%s" % (p, n["name"], k, v))
        for face, tl in s["textureLayout"].items():
            fw, fh = face_size(sz, face)
            if tl.get("angle", 0) in (90, 270): fw, fh = fh, fw
            ox, oy = tl["offset"]["x"], tl["offset"]["y"]
            if ox < 0 or oy < 0 or ox + fw > tw or oy + fh > th:
                bad("%s/%s %s UV out of texture" % (p, n["name"], face)); continue
            rect = (ox, oy, fw, fh)
            nm = n["name"]
            if nm[:2] in ("L-", "R-"):
                twin = {"L-": "R-", "R-": "L-"}[nm[:2]] + nm[2:]
            else:                                          # Head uses a suffix: CheekR / CheekL
                twin = nm[:-1] + {"L": "R", "R": "L"}.get(nm[-1:], "?")
            if owners.get(rect) == twin:
                continue                                   # mirrored twin reuses the same texels on purpose
            owners[rect] = n["name"]
            region = used[oy:oy + fh, ox:ox + fw]
            if region.any():
                bad("%s/%s %s UV overlaps another face" % (p, n["name"], face))
            region += 1
    # mirrored L- nodes intentionally share their R- node's texels; they must point at identical rects
    if tw % 32 or th % 32: bad("%s: texture %dx%d not multiple of 32" % (p, tw, th))
    a = tex[..., 3]
    if not set(np.unique(a)) <= {0, 255}: bad("%s: alpha has partial values" % p)
    vis = tex[a > 0][:, :3]
    if (vis.max(1) == 0).any() or (vis.min(1) == 255).any(): bad("%s: pure black/white texels" % p)
    tris = boxes * 12
    summary[p] = dict(nodes=len(nodes), boxes=boxes, tris=tris, texture="%dx%d" % (tw, th),
                      uv_coverage="%.0f%%" % (100 * (used > 0).mean()))
    print("  ", summary[p])
for p in PIECES:
    ic = Image.open(os.path.join(ROOT, "Common/Icons/ItemsGenerated/Armor_Foraging_%s_%s.png" % (TREE, p)))
    if ic.size != (64, 64) or ic.mode != "RGBA": bad("icon %s %s %s" % (p, ic.size, ic.mode))

def digest():
    h = {}
    for f in sorted(glob.glob(os.path.join(MD, "*"))) + sorted(glob.glob(os.path.join(ROOT, "Common/Icons/ItemsGenerated/*"))):
        h[os.path.relpath(f, ROOT)] = hashlib.sha256(open(f, "rb").read()).hexdigest()
    return h
if "--no-rebuild" not in sys.argv:
    before = digest()
    subprocess.run([sys.executable, os.path.join(HERE, "make_foraging_armor.py"), ROOT], check=True, capture_output=True,
                   env=dict(os.environ, GA_DESIGN="ga_" + TREE.lower()))
    subprocess.run([sys.executable, os.path.join(HERE, "make_foraging_icons.py"), ROOT, TIER, TREE], check=True, capture_output=True)
    after = digest()
    diff = [k for k in before if before[k] != after.get(k)]
    print("determinism:", "OK (byte-identical rebuild)" if not diff else "CHANGED: %s" % diff)
    if diff: bad("non-deterministic: %s" % diff)
print("total: %d boxes, %d tris" % (sum(s["boxes"] for s in summary.values()), sum(s["tris"] for s in summary.values())))
print("RESULT:", "PASS" if not FAIL else "%d FAIL" % len(FAIL))
json.dump(summary, open(os.path.join(HERE, "../../work/validate_summary.json"), "w"), indent=1)
sys.exit(1 if FAIL else 0)
