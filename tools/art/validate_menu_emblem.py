#!/usr/bin/env python3
"""Check the SkyWynn Menu emblem (art/menu-emblem/) against the vanilla blockymodel format and the vanilla Voidheart's size.

Reads Assets.zip READ ONLY (only to compare keys / sizes - nothing is copied or written). Exit 0 = all checks pass.
  python tools/art/validate_menu_emblem.py [path/to/Assets.zip]
"""
import hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_menu_emblem as M

ASSETS = sys.argv[1] if len(sys.argv) > 1 else os.path.expandvars(
    r"%APPDATA%\Hytale\install\release\package\game\latest\Assets.zip")
VH_MODEL = "Common/Resources/Ingredients/Voidheart.blockymodel"
VH_TEX = "Common/Resources/Ingredients/Voidheart_Texture.png"
VH_ICON = "Common/Icons/ItemsGenerated/Ingredient_Voidheart.png"

fails = []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)


def keyset(node, acc):
    acc["node"].add(tuple(sorted(k for k in node if k != "children")))
    s = node["shape"]
    acc["shape:" + s["type"]].add(tuple(sorted(s)))
    for f, tl in s.get("textureLayout", {}).items():
        acc["layout"].add(tuple(sorted(tl)))
    for c in node.get("children", []):
        keyset(c, acc)


def bounds(model, yawed=True):
    faces = M.collect_faces(model, skip_group_yaw=not yawed)
    pts = [p for f in faces for p in f["P"]]
    mn = [min(p[i] for p in pts) for i in range(3)]; mx = [max(p[i] for p in pts) for i in range(3)]
    return mn, mx


def main():
    out = M.OUT
    mpath = os.path.join(out, *M.MODEL_REL.split("/"))
    tpath = os.path.join(out, *M.TEX_REL.split("/"))
    ipath = os.path.join(out, *M.ICON_REL.split("/"))
    model = json.load(open(mpath, encoding="utf8"))
    tbytes = open(tpath, "rb").read(); ibytes = open(ipath, "rb").read()
    tex = P.read_png(tbytes); icon = P.read_png(ibytes)

    z = zipfile.ZipFile(ASSETS)
    vh = json.loads(z.read(VH_MODEL))
    vh_tex = P.png_size(z.read(VH_TEX)); vh_icon = P.png_size(z.read(VH_ICON))

    # ---- structure = vanilla keys
    a = {"node": set(), "layout": set()}; b = {"node": set(), "layout": set()}
    from collections import defaultdict
    a = defaultdict(set); b = defaultdict(set)
    for n in vh["nodes"]: keyset(n, a)
    for n in model["nodes"]: keyset(n, b)
    check(set(model) == set(vh), "top-level keys %s = vanilla %s" % (sorted(model), sorted(vh)))
    for k in b:
        check(k in a and b[k] <= a[k], "%s keys match vanilla: %s" % (k, sorted(b[k])))
    check(model["nodes"][0]["name"] == vh["nodes"][0]["name"] == "R-Attachment", "root node is R-Attachment like the Voidheart")

    # ---- every node: unique ids, integer sizes, unit quaternions, UVs inside the texture, no UV overlap
    ids, names, rects = set(), [], {}
    def walk(n):
        check(n["id"] not in ids, "node id %s unique (%s)" % (n["id"], n["name"])); ids.add(n["id"]); names.append(n["name"])
        q = n["orientation"]; ql = (q["x"] ** 2 + q["y"] ** 2 + q["z"] ** 2 + q["w"] ** 2) ** 0.5
        if abs(ql - 1) > 1e-4: check(False, "%s quaternion length %.5f" % (n["name"], ql))
        s = n["shape"]
        if s["shadingMode"] not in ("flat", "standard", "fullbright", "reflective"):
            check(False, "%s shadingMode %s is a vanilla value" % (n["name"], s["shadingMode"]))
        if s["type"] in ("box", "quad"):
            sz = s["settings"]["size"]
            if not all(float(v).is_integer() and v > 0 for v in sz.values()): check(False, "%s integer size %s" % (n["name"], sz))
            defs = M.face_defs(sz["x"], sz["y"], sz.get("z", 0))
            for f, tl in s["textureLayout"].items():
                uw, vh_ = defs[f][1]
                x0, y0 = tl["offset"]["x"], tl["offset"]["y"]
                if not (0 <= x0 and 0 <= y0 and x0 + uw <= len(tex[0]) and y0 + vh_ <= len(tex)):
                    check(False, "%s.%s UV inside the texture" % (n["name"], f))
                rects.setdefault((x0, y0, uw, vh_), []).append(n["name"] + "." + f)
        for c in n.get("children", []): walk(c)
    for n in model["nodes"]: walk(n)
    check(len(ids) <= 255, "%d nodes (limit 255)" % len(ids))
    rl = list(rects)
    over = [(rects[r1], rects[r2]) for i, r1 in enumerate(rl) for r2 in rl[i + 1:]
            if r1[0] < r2[0] + r2[2] and r2[0] < r1[0] + r1[2] and r1[1] < r2[1] + r2[3] and r2[1] < r1[1] + r1[3]]
    check(not over, "no overlapping UV rects (shared star quads use one identical rect)" + ("" if not over else " %s" % over[:3]))
    # every UV texel used by a face is painted (opaque) for boxes
    holes = 0
    for (x0, y0, w, h), who in rects.items():
        if any(".front" in n and ("Star-Ray" in n or "Waterfall" in n) for n in who): continue
        holes += sum(1 for y in range(y0, y0 + h) for x in range(x0, x0 + w) if tex[y][x][3] != 255)
    check(holes == 0, "box faces fully opaque (%d clear texels)" % holes)

    # ---- texture / icon format
    check(P.png_size(tbytes) == (M.TEX_W, M.TEX_H) and M.TEX_W % 32 == 0 and M.TEX_H % 32 == 0,
          "texture %dx%d (multiples of 32; Voidheart %dx%d, same 1 texel / unit)" % (M.TEX_W, M.TEX_H, *vh_tex))
    check(P.png_size(ibytes) == vh_icon == (64, 64) and ibytes[24:26] == b"\x08\x06", "icon 64x64 RGBA8 = vanilla item icon size")
    al = {p[3] for row in icon for p in row}
    check(al <= {0, 255}, "icon hard alpha (values %s)" % sorted(al))
    for nm, img in (("icon", icon), ("texture", tex)):
        bad = sum(1 for row in img for p in row if p[3] and (tuple(p[:3]) == (0, 0, 0) or tuple(p[:3]) == (255, 255, 255)))
        check(bad == 0, "%s has no pure #000000 / #ffffff pixels" % nm)
    used = [(x, y) for y in range(64) for x in range(64) if icon[y][x][3]]
    xs = [p[0] for p in used]; ys = [p[1] for p in used]
    check(min(xs) >= 1 and min(ys) >= 1 and max(xs) <= 62 and max(ys) <= 62, "icon keeps a 1 px margin (bbox x %d..%d y %d..%d)" % (min(xs), max(xs), min(ys), max(ys)))

    # ---- size vs Voidheart (both in the item's R-Attachment space, rotations applied)
    vmn, vmx = bounds(vh, True)
    mn, mx = bounds(model, True)
    vs = [vmx[i] - vmn[i] for i in range(3)]; ms = [mx[i] - mn[i] for i in range(3)]
    vc = [(vmx[i] + vmn[i]) / 2 for i in range(3)]; mc = [(mx[i] + mn[i]) / 2 for i in range(3)]
    print("     Voidheart bbox  %s  centre %s" % ([round(v, 1) for v in vs], [round(v, 1) for v in vc]))
    print("     Skyy_Menu bbox  %s  centre %s" % ([round(v, 1) for v in ms], [round(v, 1) for v in mc]))
    check(max(ms) <= max(vs) * 1.15, "largest side %.1f within 15%% of the Voidheart's %.1f" % (max(ms), max(vs)))
    check(abs(mc[1] - vc[1]) <= 2.0, "vertical centre %.1f within 2 units of the Voidheart's %.1f (sits in the hand the same)" % (mc[1], vc[1]))

    # ---- manifest matches the files
    man = json.load(open(os.path.join(out, "manifest.json"), encoding="utf8"))
    for f in man["files"]:
        data = open(os.path.join(out, *f["path"].split("/")), "rb").read()
        check(hashlib.sha256(data).hexdigest() == f["sha256"] and len(data) == f["bytes"], "manifest sha256 + bytes: " + f["path"])
    print("\n%s (%d fails)" % ("ALL OK" if not fails else "FAILED", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
