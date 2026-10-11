#!/usr/bin/env python3
"""Check art/ui-kit-sky/ (the SKY WINDOW UI kit). One line per check, ALL OK / N FAILED (exit 1).

Checks: every element of research/Hubs-Spec.md 7.3 (+ the six Frame_<Hub> moods + the hub icons) exists at its spec size and lives
under Common/UI/Custom/SkyyKit/ with markup path "SkyyKit/<Element>.png"; manifest borders equal the spec borders (UI units); the 9-slice
stretch strips are uniform on every axis the manifest names (so a Border never smears corner art); frame centres are 98 % opaque and
every other text area fully opaque; text contrast >= 4.5:1 for every kit text colour a texture must carry (recomputed from the pixels,
manifest table current); the 64 px hub icons use hard alpha only; no two textures are identical; manifest bytes + sha256 match; the
generator is deterministic (a fresh in-memory run gives the same bytes); no path exists in vanilla Assets.zip (read only).
"""
import hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emblem_png as P
import make_ui_kit_sky as M
import make_tooltip_sky as T

ASSETS = r"C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip"
fails = []

# Hubs-Spec 7.3 (+ coordinator: per-hub Frame moods): element -> (w, h @2x, border in UI units or None)
HUBS = ["Character", "Storage", "Market", "Smithing", "World", "Social"]
SPEC = {"Frame": (160, 160, {"Border": 32}), "Header": (600, 76, {"HorizontalBorder": 60, "VerticalBorder": 0}),
        "HeaderOrnament": (472, 44, None), "Close": (64, 64, None), "Close_Hovered": (64, 64, None),
        "Panel": (64, 64, {"Border": 12}), "PanelInset": (48, 48, {"Border": 8}),
        "CheckBox": (44, 44, {"Border": 7}), "CheckMark": (32, 32, None),
        "ScrollTrack": (12, 24, {"Border": 3}), "Separator": (64, 4, {"HorizontalBorder": 8, "VerticalBorder": 0}),
        "SlotEmpty": (148, 148, None), "CardFrame": (160, 160, {"Border": 32})}
for h in HUBS: SPEC["Frame_" + h] = SPEC["Frame"]
for s in ("", "_Hovered", "_Pressed", "_Selected"): SPEC["Tab" + s] = (240, 88, {"HorizontalBorder": 20, "VerticalBorder": 12})
for s in ("", "_Hovered", "_Pressed", "_Disabled"):
    SPEC["Primary" + s] = (440, 88, {"HorizontalBorder": 24, "VerticalBorder": 12})
    SPEC["Secondary" + s] = (440, 88, {"Border": 12})
for s in ("", "_Hovered", "_Pressed", "_Active"): SPEC["Tertiary" + s] = (256, 64, {"Border": 12})
for s in ("", "_Hovered", "_Pressed"): SPEC["Danger" + s] = (440, 88, {"Border": 12})
for s in ("", "_Hovered", "_Selected"):
    SPEC["Row" + s] = (64, 48, {"Border": 8})
    SPEC["InputBox" + s] = (96, 64, {"Border": 16})
for s in ("", "_Hovered", "_Dragged"): SPEC["ScrollHandle" + s] = (12, 24, {"Border": 3})


def check(ok, msg):
    print(("OK    " if ok else "FAIL  ") + msg)
    if not ok: fails.append(msg)


def strip_ok(img, axis, b):
    w, h = P.size(img)
    if axis == "x":
        return all(all(row[x] == row[b] for x in range(b, w - b)) for row in img)
    return all(img[y] == img[b] for y in range(b, h - b))


def main():
    man = json.load(open(os.path.join(M.OUT, "manifest.json"), encoding="utf-8"))
    mf = {f["path"]: f for f in man["files"]}
    me = {e["element"]: e for e in man["elements"]}
    check(set(me) == set(SPEC), "element list = Hubs-Spec 7.3 + Frame_<Hub> (missing %s, extra %s)" % (
        sorted(set(SPEC) - set(me)), sorted(set(me) - set(SPEC))))
    seen = {}
    imgs = {}
    for stem, (w, h, border) in sorted(SPEC.items()):
        e = me.get(stem)
        if not e: continue
        rel = "Common/UI/Custom/SkyyKit/%s@2x.png" % stem
        check(e["file"] == rel and e["markup_path"] == "SkyyKit/%s.png" % stem, stem + " path + markup path")
        p = os.path.join(M.OUT, rel)
        if not os.path.exists(p):
            check(False, rel + " exists"); continue
        data = open(p, "rb").read(); img = P.read_png(data); imgs[stem] = img
        check(P.size(img) == (w, h) and e["w"] == w and e["h"] == h, "%s is %dx%d" % (stem, w, h))
        check(e["border"] == border, "%s border %s" % (stem, border))
        sha = hashlib.sha256(data).hexdigest()
        check(rel in mf and mf[rel]["bytes"] == len(data) and mf[rel]["sha256"] == sha and e["sha256"] == sha, stem + " matches the manifest")
        check(sha not in seen, stem + " differs from every other texture" + (" (same as %s)" % seen.get(sha) if sha in seen else ""))
        seen[sha] = stem
        if border:
            hb = 2 * border.get("Border", border.get("HorizontalBorder", 0))
            vb = 2 * border.get("Border", border.get("VerticalBorder", 0))
            for ax in e["strip_uniform"]:
                b = hb if ax == "x" else vb
                check(b > 0 and strip_ok(img, ax, b), "%s stretch strip uniform along %s (%d..%d px)" % (stem, ax, b, (w if ax == "x" else h) - b - 1))
            check(("x" in e["strip_uniform"]) == (hb > 0), stem + " every horizontally stretched texture is column-uniform")
        cx, cy = w // 2, h // 2
        if stem.startswith(("Frame", "CardFrame")):
            check(abs(img[cy][cx][3] - 250) <= 1, "%s centre 98%% opaque (alpha %d)" % (stem, img[cy][cx][3]))
        elif stem in ("Header", "Panel", "PanelInset", "SlotEmpty") or stem.startswith(("Row", "InputBox", "Tab", "Primary", "Secondary",
                                                                                         "Tertiary", "Danger", "CheckBox")):
            check(img[cy][cx][3] == 255, stem + " text area fully opaque")
    # contrast, recomputed
    for stem, ((x, y0, y1), need, extra) in M.CONTRAST.items():
        img = imgs.get(stem)
        if img is None: continue
        px = [tuple(img[y][x][:3]) for y in range(y0, y1 + 1)]
        worst = None
        for k in need:
            r = min(T.contrast(T.hx(M.TXT[k]), p) for p in px)
            if worst is None or r < worst[1]: worst = (k, r)
        if worst:
            check(worst[1] >= 4.5, "%s text contrast >= 4.5 (worst %s %.2f)" % (stem, worst[0], worst[1]))
            check(abs(man["contrast"][stem]["min_required"] - round(worst[1], 2)) < 0.011, stem + " manifest contrast table current")
    # hub icons
    hi = {h["file"]: h for h in man["hub_icons"]}
    for h in HUBS:
        for sfx, size in (("@2x", 128), ("", 64)):
            rel = "Common/UI/Custom/SkyyKit/HubIcon_%s%s.png" % (h, sfx)
            p = os.path.join(M.OUT, rel)
            if not os.path.exists(p):
                check(False, rel + " exists"); continue
            data = open(p, "rb").read(); img = P.read_png(data)
            check(P.size(img) == (size, size), "%s is %dx%d" % (rel, size, size))
            check(rel in hi and hi[rel]["sha256"] == hashlib.sha256(data).hexdigest() == mf[rel]["sha256"], rel + " matches the manifest")
            if size == 64:
                check(all(px[3] in (0, 255) for row in img for px in row), rel + " hard alpha (0 / 255)")
            check(img[0][0][3] == 0 and img[size // 2][size // 2][3] == 255, rel + " round badge (transparent corner, opaque centre)")
    check(len(man["files"]) == len(SPEC) + 12, "manifest lists %d files" % (len(SPEC) + 12))
    sp = os.path.join(M.OUT, "sheet.png")
    check(os.path.exists(sp) and man["sheet"]["sha256"] == hashlib.sha256(open(sp, "rb").read()).hexdigest(), "sheet.png exists + matches the manifest")
    check(os.path.exists(os.path.join(M.OUT, "README.md")), "README.md exists")
    fresh = M.build_all()
    check(all(open(os.path.join(M.OUT, rel), "rb").read() == v[1] for rel, v in fresh.items()), "generator deterministic (fresh run = files on disk)")
    if os.path.exists(ASSETS):
        names = set(zipfile.ZipFile(ASSETS).namelist())
        check(not any(rel in names for rel in fresh), "no path collides with vanilla Assets.zip")
    else:
        print("SKIP  Assets.zip not found (collision check)")
    print("ALL OK" if not fails else "%d FAILED" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
