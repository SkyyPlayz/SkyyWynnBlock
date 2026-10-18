"""Derive SkyyGear/build_skyygear_0.3.26.py from the LIVE 0.3.25 (build_skyygear_0.3.25.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_25_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_26_patch.py      then      python SkyyGear/build_skyygear_0.3.26.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.26.py   (the 0.3.25 chain on this jar + S326 + H326; --static needs no jar)

0.3.26 (2026-10-18) = QUIRK'S MULTITOOL + HARVESTER MODELS (checked; shipped only where they pass) + THE FIVE ARMORY UNTIERED SETS.
  1. QUIRK'S MODELS (Skyy 2026-10-18, docs/answered/gear.md: "what about the multitools? (Quirk is a grok Bot agent like cobb. she made the item
     art for me.)" + "so if its permission that is the issue, just used them. if they need fixed or changed lmk how and ill have it done").
     The build reads Quirk's PRIVATE Multitool + Harvester builds (../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE/<Titanium|Lumen>/, or
     SKYWYNN_PRIVATE_ART) at BUILD time into the jar only - never into this public repo; a missing file stops the build with a clear message.
     Every metal she made (Titanium, Lumen) uses her texture untouched; every other metal = her geometry (ores: the Titanium build, alloys: the
     Lumen build) + a build-time recolour of her texture to the metal's palette card (tools/art/make_metal_items.py tools(), in memory; the 8
     zone metals = the approved files in models-local/art/metals, compared byte for byte when present; Bronze / Cobalt / Adamantite / Mithril /
     Crude / Copper / Iron / Thorium = placeholder cards from the vanilla ingot colours, Crude from the 0.3.12 Harvester ramp). Items: the 9 zone
     multitools (Bronze .. Lumen; the vanilla-tier multitools are InkBlindCat's Multitools items - a pack mod, never touched) + all 16 Harvesters
     (Crude .. Thorium of 0.3.12, Cobalt / Adamantite / Mithril + the 9 zone ones of 0.3.23). Ids unchanged - no item or saved-data change.
     THE HELD-TOOL CHECK (G26_CHECK, every build): one root node R-Attachment (all 229 vanilla right-hand items), the tool standing on the hand
     point, the head along Z like the vanilla pickaxe / hoe, the height against the vanilla tool, texture size (x32) and every face's UV inside
     it, no see-through texel on a single-sided face, the icon render inside the 64 x 64 frame. A model that FAILS keeps the 0.3.25 look for
     just its items (vanilla Mithril pickaxe model / vanilla Thorium hoe model) and the build prints the fix list for Quirk (what to change and
     how); notes print but do not block. TODAY all four builds fail the same three points (built as a 'character'-format attachment on the
     Pelvis bone, 190-290 units to the side, the head along X), so every multitool / Harvester keeps its 0.3.25 look and the jar's art is
     unchanged - the fix list goes to Skyy. A rigid BUILD-TIME RE-PLACEMENT of her geometry (new R-Attachment root, handle moved onto the
     origin, turned 90 degrees around the handle, bottom level with the vanilla tool; her boxes, sizes and UVs untouched) is computed and
     checked on every build but SHIPS ONLY with G26_SHIP_REPOSED = True (off: it would be a fix of her file; Skyy / Quirk decide).
     Contact sheet: SKYWYNN_G26_SHEET=<png path> makes the build also write the icon sheet (today's icons + Quirk's renders); jar unchanged.
  2. THE FIVE ARMORY UNTIERED SETS (Skyy 2026-10-18 "Yes, ship the 5 drafted Armory UTs (Ghost Rook, Ghost Calvary, Battlegrounds, Ghost
     Sword, Hepta Axe) as drafted."): the ut.<id> + utfx.<id> rows of research/UT-Lines-Draft.md section 2.1, exactly as drafted, for the 18 ids
     of tools/pack_drops.py's five role-ut sets - Ghost Rook + its Wraith twins (Helm / Gauntlets / Open helms taken-3, Chest / Boots taken-5,
     all spd-2, Lv 15-29), Ghost Calvary (4 pieces front+10 back-10, Lv 15-29), Battlegrounds (2 pieces heal+25 dmg-15, Lv 15-29), Ghost
     Sword (swing=fast taken+5, Lv 15-29), Hepta Axe (swing=slow dmg+10 taken+10, Lv 45-59 = zone 4). ON by default (part.utLines is on).
     Build checks: every id is in The Armory 1.23.0 jar (Mods folder, read-only; absent = skipped with a line) with no Recipe and no recipe
     output, the slot / weapon template the row text assumes, the existing ASCII / no comma / 110-char asserts, body keys = live stat keys,
     fixed words = the GearUtFx grammar, the Iron rows = the first batch's band (UT_LO-UT_HI 15-29) and Hepta's 45-59 inside the locked zone 4
     band (Lv 45-60). A fresh file carries the block (before the 0.3.22 block); ONE-TIME UPDATE migrate0326 (after migrate0323) appends only
     the missing keys to an existing config.properties: History copy verified first, the run-once marker, one change-log row per added entry
     (ut[<id>] / utfx[<id>], old (none), status ok = Undo in Server Setup removes it), a key already there in ANY case is kept + noted, every
     other byte and line ending kept. GearUt still refuses an id any loaded recipe makes (crafted) at run time.
     POOL DILUTION (the draft's open point b): every row weighs 1 and ut.weight.<key> is not built, so Ghost Rook alone is 10 rows (Ghost +
     Wraith, Open helms) - at an Iron level 17 of the 39 orange rows are the new Armory pieces (about 44 %); per bag type the share differs.
     Skyy said "as drafted", so all 18 ship; trimming = delete rows in Server Setup -> Gear -> Rarity -> Untiered items (Undo-able).
Commands: none new. Classes: none new. Config: + 36 table entries (ut / utfx) via migrate0326. SAVED DATA: none (config.properties only).
ROLLBACK 0.3.26 -> 0.3.25: item-clean (no art or id change shipped while G26_SHIP_REPOSED is off); the 36 rows stay in config.properties and
keep working in 0.3.25 (same table rows, same grammar) - delete them there to take the sets out again.
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.25.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.26.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.25"' in s and "GENERATED by tools/gear_0_3_25_patch.py" in s, "not the generated 0.3.25 script"
assert "G26_" not in s and "U26_" not in s and "migrate0326" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
MK0 = s.count(' = mk("')
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def after(anchor, text):
    rep(anchor, anchor + text)


def before(anchor, text):
    rep(anchor, text + anchor)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.25":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.25" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.26 (2026-10-18)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.25 - build script (javassist via jpype). GENERATED by tools/gear_0_3_25_patch.py from the LIVE 0.3.24 (itself GENERATED by
tools/gear_0_3_24_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.25.py -> SkyyGear/SkyyGear-0.3.25.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.25.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''', '''"""SkyyGear 0.3.26 - build script (javassist via jpype). GENERATED by tools/gear_0_3_26_patch.py from the LIVE 0.3.25 (itself GENERATED by
tools/gear_0_3_25_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.26.py -> SkyyGear/SkyyGear-0.3.26.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.26.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''' + NOTE + '''
--- 0.3.25 notes ---
''')
rep('VERSION = "0.3.25"\n', 'VERSION = "0.3.26"\n')

# ================================================================================================================ 1: Quirk's models (build time)
before('''assert len(G23_ITEMJ) == 49
for _k, _v in list(G23_FILES.items()) + list(G23_ITEMJ.items()):''', r'''# ================================================================= 0.3.26 QUIRK'S MULTITOOL + HARVESTER MODELS (tools/gear_0_3_26_patch.py item 1)
# Read from the PRIVATE folder at build time (never in this repo). Each of her 4 builds is checked as a HELD tool (_g26_check); a build that
# fails keeps the 0.3.25 look for just its items and prints what Quirk should change. G26_SHIP_REPOSED: ship the build-time re-placement.
import copy as _g26copy
import math
G26_SHIP_REPOSED = False          # off: re-placing her geometry is a fix of her file - Skyy / Quirk decide (see the fix list the build prints)
G26_TOOLS = ["Multitool", "Harvester"]
G26_BASES = ["Titanium", "Lumen"]
_g26miss = [os.path.join(_b, _t + _x) for _b in G26_BASES for _t in G26_TOOLS for _x in (".blockymodel", "_Texture.png")
            if not os.path.isfile(os.path.join(G23_PRIV, _b, _t + _x))]
if _g26miss:
    raise SystemExit("SkyyGear 0.3.26 needs Quirk's private multitool + Harvester builds in %s (missing: %s). Put the SkyWynn-PRIVATE-art folder "
                     "next to the project (or set SKYWYNN_PRIVATE_ART to it) - they are never committed to the public repo." % (G23_PRIV, ", ".join(_g26miss)))
G26_VAN = {"Multitool": "Items/Tools/Pickaxe/Mithril.blockymodel", "Harvester": G23_HOE_M}          # the model each item uses today
G26_VNAME = {"Multitool": "the vanilla Mithril pickaxe", "Harvester": "the vanilla Thorium hoe"}
G26_TURN = {"Multitool": -90.0, "Harvester": 90.0}          # re-placement: the axe blade / the hoe blade to +Z (like the vanilla hatchet / hoe)
G26_VIEW = list(MMI.TOOL_VIEW)


def _g26_json(b):
    return json.loads(b.decode("utf-8-sig") if isinstance(b, (bytes, bytearray)) else b)


def _g26_box(mj):
    _p = [c for f in SA.model_faces(mj) for c in f["corners"]]
    return [(min(q[i] for q in _p), max(q[i] for q in _p)) for i in range(3)]


def _g26_check(tool, mj, tex):
    """(fails, notes): one of Quirk's builds as a HELD tool against the vanilla model its items use today"""
    fails, notes = [], []
    vj = _g26_json(AZ.read("Common/" + G26_VAN[tool]))
    nd = mj.get("nodes") or []
    if len(nd) != 1 or nd[0].get("name") != "R-Attachment":
        fails.append("ROOT: the model's root is %s (Blockbench format %r) - a held tool needs ONE root node named 'R-Attachment' (isPiece on), like "
                     "all 229 vanilla right-hand items (e.g. Items/Tools/Pickaxe/Mithril.blockymodel); with an armor bone as root the game hangs it "
                     "on that body bone, not in the hand. Fix: save it in the item / attachment format with the parts under R-Attachment"
                     % ([n.get("name") for n in nd], mj.get("format")))
    b, vb = _g26_box(mj), _g26_box(vj)
    cx, cz = (b[0][0] + b[0][1]) / 2.0, (b[2][0] + b[2][1]) / 2.0
    if abs(cx) > 12 or abs(cz) > 16:
        fails.append("PLACE: the tool is built %d units away from the hand point (x %.0f..%.0f, z %.0f..%.0f) - move every part so the handle "
                     "stands on the origin (x 0, z 0) like %s (x %.0f..%.0f, z %.0f..%.0f), its bottom near y %.0f"
                     % (int(max(abs(cx), abs(cz))), b[0][0], b[0][1], b[2][0], b[2][1], G26_VNAME[tool], vb[0][0], vb[0][1], vb[2][0], vb[2][1], vb[1][0]))
    xs, zs, vzs = b[0][1] - b[0][0], b[2][1] - b[2][0], vb[2][1] - vb[2][0]
    if xs > zs:
        fails.append("TURN: the head lies along X (%.0f wide, %.0f deep) - turn the whole tool 90 degrees around its handle so the head points "
                     "forward / back along Z like %s (%.0f along Z), else it swings side-on" % (xs, zs, G26_VNAME[tool], vzs))
    h, vh = b[1][1] - b[1][0], vb[1][1] - vb[1][0]
    r = h / vh
    if r < 0.6 or r > 1.6:
        fails.append("SIZE: %.0f units tall = %.2fx %s (%.0f) - scale it to about the vanilla height" % (h, r, G26_VNAME[tool], vh))
    elif r < 0.85 or r > 1.2:
        notes.append("SIZE (note): %.0f units tall = %.2fx %s (%.0f) - in the hand it looks %s than the vanilla tool; fine if meant"
                     % (h, r, G26_VNAME[tool], vh, "smaller" if r < 1 else "bigger"))
    img = SA.png_decode(tex)
    if img.w % 32 or img.h % 32:
        fails.append("TEXTURE: %dx%d - Hytale textures are multiples of 32" % (img.w, img.h))
    outs, holes = [], []
    for f in SA.model_faces(mj):
        x0, y0, x1, y1 = SA.face_rect(f)
        if x0 < 0 or y0 < 0 or x1 > img.w or y1 > img.h:
            outs.append("%s %s" % (f["node"], f["face"]))
            continue
        if f["double"] or f["quad"]:
            continue
        n = sum(1 for y in range(y0, y1) for x in range(x0, x1) if img.px[(y * img.w + x) * 4 + 3] == 0)
        if n:
            holes.append("%s %s (%d)" % (f["node"], f["face"], n))
    if outs:
        fails.append("UV: %d faces sample outside the %dx%d texture (%s) - move their UV boxes inside" % (len(outs), img.w, img.h, ", ".join(outs[:4])))
    if holes:
        notes.append("SEE-THROUGH (note): transparent texels on single-sided box faces %s - you can see into the box there; paint them or make "
                     "the face double-sided if the cut corners are meant" % ", ".join(holes))
    return fails, notes


def _g26_repose(tool, mj):
    """the rigid re-placement of one of her builds (NOT shipped unless G26_SHIP_REPOSED): the vanilla tool's R-Attachment root, her parts with the
    handle moved onto the origin, turned G26_TURN degrees around the handle, bottom level with the vanilla tool; every box / size / UV untouched"""
    vj = _g26_json(AZ.read("Common/" + G26_VAN[tool]))
    root = mj["nodes"][0]
    hd = [c for c in root.get("children") or [] if str(c.get("name", "")).endswith("Handle")]
    assert len(mj["nodes"]) == 1 and len(hd) == 1, "0.3.26: Quirk's %s has no single *Handle part to re-place around" % tool
    hp = SA._xyz(hd[0].get("position"))
    rp, vp = SA._xyz(root.get("position")), SA._xyz(vj["nodes"][0].get("position"))
    t = math.radians(G26_TURN[tool])
    q = (0.0, math.sin(t / 2.0), 0.0, math.cos(t / 2.0))
    dy = _g26_box(vj)[1][0] - _g26_box(mj)[1][0]
    kids = []
    for c in root.get("children") or []:
        c2 = _g26copy.deepcopy(c)
        p = SA._xyz(c.get("position"))
        v = SA._qrot(q, (p[0] - hp[0], p[1], p[2] - hp[2]))
        c2["position"] = {"x": round(v[0], 6) + 0.0, "y": round(v[1] + rp[1] + dy - vp[1], 6) + 0.0, "z": round(v[2], 6) + 0.0}
        o = c.get("orientation") or {}
        qo = SA._qmul(q, (float(o.get("x", 0)), float(o.get("y", 0)), float(o.get("z", 0)), float(o.get("w", 1))))
        c2["orientation"] = {"x": round(qo[0], 6) + 0.0, "y": round(qo[1], 6) + 0.0, "z": round(qo[2], 6) + 0.0, "w": round(qo[3], 6) + 0.0}
        kids.append(c2)
    nr = _g26copy.deepcopy(vj["nodes"][0])
    nr["id"] = root.get("id", nr.get("id"))
    nr["children"] = kids
    return {"nodes": [nr], "lod": mj.get("lod", "auto")}


def _g26_view(turn):
    """IconProperties Rotation (skyyart's yxz Euler) that shows a model turned `turn` degrees around Y like MMI.TOOL_VIEW shows the unturned one"""
    t = math.radians(turn)
    want = SA._qmul(SA._euler_yxz(*G26_VIEW), (0.0, -math.sin(t / 2.0), 0.0, math.cos(t / 2.0)))
    x, y, z, w = want
    m02, m12, m22 = 2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)
    m10, m11 = 2 * (x * y + w * z), 1 - 2 * (x * x + z * z)
    rx = math.degrees(math.asin(max(-1.0, min(1.0, -m12))))
    ry, rz = math.degrees(math.atan2(m02, m22)), math.degrees(math.atan2(m10, m11))
    view = [round(rx, 4) + 0.0, round(ry, 4) + 0.0, round(rz, 4) + 0.0]
    got = SA._euler_yxz(*view)
    for _v in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        a, b_ = SA._qrot(got, _v), SA._qrot(want, _v)
        assert all(abs(a[i] - b_[i]) < 1e-3 for i in range(3)), ("0.3.26: icon view", turn, view)
    return view


def _g26_frame(png):
    """True when an icon's outer pixel ring is empty (nothing cut off) and it covers a sane share of the 64 x 64 slot"""
    im = SA.png_decode(png)
    ring = [(x, y) for x in range(im.w) for y in (0, im.h - 1)] + [(x, y) for y in range(im.h) for x in (0, im.w - 1)]
    cov = sum(1 for i in range(im.w * im.h) if im.px[i * 4 + 3] > 0) / float(im.w * im.h)
    return (im.w, im.h) == (64, 64) and not any(im.px[(y * im.w + x) * 4 + 3] for x, y in ring) and 0.08 < cov < 0.8


G26_SRC, G26_MODEL, G26_PROPS, G26_OK, G26_FIX, G26_NOTES, G26_REP = {}, {}, {}, {}, [], [], {}
for _t in G26_TOOLS:
    for _b in G26_BASES:
        _mb = open(os.path.join(G23_PRIV, _b, _t + ".blockymodel"), "rb").read()
        _tx = open(os.path.join(G23_PRIV, _b, _t + "_Texture.png"), "rb").read()
        _mj = _g26_json(_mb)
        G26_SRC[(_t, _b)] = (_mj, _tx)
        _f, _n = _g26_check(_t, _mj, _tx)
        _rj = _g26_repose(_t, _mj)
        _rf, _rn = _g26_check(_t, _rj, _tx)
        # the re-placement is rigid: the same faces, sizes and UV boxes, every edge length kept
        _fa, _fb = SA.model_faces(_mj), SA.model_faces(_rj)
        assert [(f["node"], f["face"], f["wh"], SA.face_rect(f)) for f in _fa] == [(f["node"], f["face"], f["wh"], SA.face_rect(f)) for f in _fb], (_t, _b)
        for _x, _y in zip(_fa, _fb):
            for _i in range(4):
                _d1 = math.dist(_x["corners"][_i], _x["corners"][(_i + 1) % 4])
                _d2 = math.dist(_y["corners"][_i], _y["corners"][(_i + 1) % 4])
                assert abs(_d1 - _d2) < 1e-3, ("0.3.26: the re-placement is not rigid", _t, _b, _x["node"])
        assert not _rf, "0.3.26: the re-placed %s %s still fails the held-tool check: %s" % (_b, _t, _rf)
        G26_REP[(_t, _b)] = _rj
        if not _f:
            G26_OK[(_t, _b)] = True
            G26_MODEL[(_t, _b)] = _mj
            G26_PROPS[(_t, _b)] = MMI.MFI.fit_props([_mj], G26_VIEW, fill=58.0)
        elif G26_SHIP_REPOSED:
            G26_OK[(_t, _b)] = True
            G26_MODEL[(_t, _b)] = _rj
            G26_PROPS[(_t, _b)] = MMI.MFI.fit_props([_rj], _g26_view(G26_TURN[_t]), fill=58.0)
        else:
            G26_OK[(_t, _b)] = False
        for _x in _f:
            G26_FIX.append("%s %s: %s" % (_b, _t, _x))
        for _x in _n:
            G26_NOTES.append("%s %s: %s" % (_b, _t, _x))
# the art: the 8 approved zone metals + placeholder cards for the rest (the 0.3.23 recipe; Crude = the 0.3.12 Harvester ramp)
G26_ART = _g23_art(list(MMI.METALS), G26_TOOLS)
assert len(G26_ART) == 16
_g26same = [(k, v[3]) for k, v in sorted(G26_ART.items()) if os.path.isfile(os.path.join(_g23loc, v[3]))]
for _k, _rel in _g26same:
    assert open(os.path.join(_g23loc, _rel), "rb").read() == G26_ART[_k][0], "0.3.26: the generated %s differs from the approved file %s" % (_k, _rel)
    _ip = os.path.join(_g23loc, "tools", "Common", "Icons", "ItemsGenerated", "SkyyMetal_%s_%s.png" % _k)
    assert not os.path.isfile(_ip) or open(_ip, "rb").read() == G26_ART[_k][1], "0.3.26: the generated icon of %s differs from the approved one" % (_k,)
G26_CARDS = dict(G23_CARDS)
G26_CARDS.update({"Copper": _g23_card("Copper", "Iron", 1, "ore", "Copper"), "Iron": _g23_card("Iron", "Copper", 1, "ore", "Iron"),
                  "Thorium": _g23_card("Thorium", "Iron", 2, "ore", "Thorium")})
_g26cr = SA.palette_from([SA._read(_g23z, "Resources/Materials/Ingot_Textures/Copper.png")])
G26_CARDS["Crude"] = {"zone": 1, "kind": "ore", "donor": "Copper", "shade": HARV_RAMP["Crude"][0].upper(), "base": HARV_RAMP["Crude"][1].upper(),
                      "hi": HARV_RAMP["Crude"][2].upper(), "trim": _g23_hex(_g26cr[12]), "glow": None, "pattern": None}
G26_ART.update(_g23_art(["Bronze"], G26_TOOLS, {"Bronze": G26_CARDS["Bronze"]}))
for _m in ("Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril"):
    G26_ART.update(_g23_art([_m], ["Harvester"], {_m: G26_CARDS[_m]}))
G26_IDS = [("Multitool", _i) for _i in G23_MULTI] + [("Harvester", _i) for _i in HARV_IDS + G23_HARV]
assert len(G26_IDS) == 25 and len(G26_ART) == 25 and all((_t, _g23_word(_i)) in G26_ART for _t, _i in G26_IDS)
for (_t, _m), _v in sorted(G26_ART.items()):
    _iw, _ih = SA.png_size(_v[0])
    assert (_iw, _ih) == SA.png_size(G26_SRC[(_t, _v[2])][1]), "0.3.26: the %s %s texture is not the size of Quirk's %s build" % (_m, _t, _v[2])
    assert _g26_frame(_v[1]), "0.3.26: the %s %s icon is cut off by the 64 x 64 frame or (nearly) empty" % (_m, _t)
G26_USED, G26_FALL, G26_SHEET = [], [], {}
for _t, _iid in G26_IDS:
    _m = _g23_word(_iid)
    _tex, _ico, _b, _tp = G26_ART[(_t, _m)]
    _jp = "Server/Item/Items/SkyyGear/Metal/%s.json" % _iid
    _jd = G23_ITEMJ if _jp in G23_ITEMJ else EXTRA
    if _jp not in _jd:
        _jp = "Server/Item/Items/SkyyGear/%s.json" % _iid
    assert _jp in _jd, _iid
    _j = json.loads(_jd[_jp])
    _today = G23_FILES.get("Common/" + _j["Icon"]) or EXTRA.get("Common/" + _j["Icon"]) or AZ.read("Common/" + _j["Icon"])
    if not G26_OK[(_t, _b)]:
        G26_FALL.append(_iid)
        G26_SHEET[(_t, _m)] = (_today, _ico)
        continue
    _mp = "Items/SkyyGear/Metal/Quirk/%s_%s.blockymodel" % (_t, _b)
    G23_FILES["Common/" + _mp] = json.dumps(G26_MODEL[(_t, _b)], indent=1).encode("utf-8")
    _ntx, _nic = "Items/Tools/SkyyMetal/%s/%s_Texture.png" % (_t, _m), "Icons/ItemsGenerated/SkyyMetal_%s_%s.png" % (_t, _m)
    G23_FILES["Common/" + _ntx] = _tex
    if G26_MODEL[(_t, _b)] is G26_REP.get((_t, _b)):
        _err = SA.check_icon(G26_MODEL[(_t, _b)], _tex, G26_PROPS[(_t, _b)], _ico)
        assert _err[1] < 6.0, "0.3.26: the re-placed %s %s renders unlike its icon (%s)" % (_m, _t, _err)
    G23_FILES["Common/" + _nic] = _ico
    if _t == "Harvester":          # the 0.3.12 / 0.3.23 recolour art leaves with the old look
        for _old in ("Common/" + _j["Texture"], "Common/" + _j["Icon"]):
            if _old not in ("Common/" + _ntx, "Common/" + _nic):
                G23_FILES.pop(_old, None)
                EXTRA.pop(_old, None)
    _j.update({"Model": _mp, "Texture": _ntx, "Icon": _nic, "IconProperties": G26_PROPS[(_t, _b)]})
    _jd[_jp] = json.dumps(_j, indent=2)
    G26_USED.append(_iid)
    G26_SHEET[(_t, _m)] = (_ico, _ico)
print("0.3.26 Quirk's multitool / Harvester builds: %d items use her model, %d keep the 0.3.25 look (%d approved textures compared byte for byte)"
      % (len(G26_USED), len(G26_FALL), len(_g26same)))
for _x in G26_FIX:
    print("  FIX for Quirk - " + _x)
for _x in G26_NOTES:
    print("  NOTE for Quirk - " + _x)
if os.environ.get("SKYWYNN_G26_SHEET"):          # the icon contact sheet (side output only; the jar does not change)
    _cols = [_m for _m in ["Crude"] + list(TT.LADDER[:15]) if any((_t, _m) in G26_SHEET for _t in G26_TOOLS)]
    _rows = []
    for _t in G26_TOOLS:
        _rows.append(("%s NOW" % {"Multitool": "MT", "Harvester": "HV"}[_t], dict((_m, G26_SHEET[(_t, _m)][0]) for _m in _cols if (_t, _m) in G26_SHEET)))
        _rows.append(("%s QUIRK" % {"Multitool": "MT", "Harvester": "HV"}[_t], dict((_m, G26_SHEET[(_t, _m)][1]) for _m in _cols if (_t, _m) in G26_SHEET)))
    _sp = os.path.abspath(os.environ["SKYWYNN_G26_SHEET"])
    os.makedirs(os.path.dirname(_sp), exist_ok=True)
    open(_sp, "wb").write(MMI.contact_sheet("Multitools MT and Harvesters HV - now and Quirk", _cols, _rows))
    print("  contact sheet -> %s" % _sp)
''')

# ================================================================================================================ 2: the five Armory UT sets
after('''UB_LINES = [UB_HEAD, UB_MARK] + [_x for _c, _ls in UB_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in UB_LINES) and all("=" not in _x for _x in (UB_HEAD, UB_MARK))
assert len(set(UB_LINES)) == len(UB_LINES)
''', r'''

# 0.3.26 (tools/gear_0_3_26_patch.py item 2): the five Armory UT sets, research/UT-Lines-Draft.md section 2.1 AS DRAFTED (Skyy 2026-10-18 "Yes, ship
# the 5 drafted Armory UTs (Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword, Hepta Axe) as drafted."). (id, min, max, trade-off, utfx)
_U26_RK = "Hollow guard: take %d%% less damage per piece (set 16%%) but you move slower."
_U26_RV = {"Helm": 3, "Gauntlets": 3, "Chest": 5, "Boots": 5}
U26_ROWS = []
for _c in ("Ghost", "Wraith"):
    for _p in ("Helm", "Chest", "Gauntlets", "Boots"):
        U26_ROWS.append(("Rook%s%s" % (_p, _c), 15, 29, _U26_RK % _U26_RV[_p], "def hprp,taken-%d spd-2" % _U26_RV[_p]))
    U26_ROWS.append(("RookHelm%sOpen" % _c, 15, 29, _U26_RK % 3, "def hprp,taken-3 spd-2"))
for _p in ("Helm", "Chest", "Gauntlets", "Leggings"):
    U26_ROWS.append(("GhostCalvary" + _p, 15, 29, "Lancer's set: 10% more damage to enemies you face and 10% less from behind per piece (set 40%).",
                     "str spd,front+10 back-10"))
for _i in ("TarnishedCrown", "VerdantAmulet"):
    U26_ROWS.append((_i, 15, 29, "Healer's set: heal orb heals 25% more per piece (set 50%) but spells deal 15% less (set 30%).", "mp hpr,heal+25 dmg-15"))
U26_ROWS.append(("GhostSword", 15, 29, "Swings one tier faster. You take 5% more damage while held.", "str lsteal,swing=fast taken+5"))
U26_ROWS.append(("Hepta_Axe", 45, 59, "Hits 54% harder. Swings 40% slower. You take 10% more damage while held.", "str tdmg,swing=slow dmg+10 taken+10"))
U26_IDS = [_r[0] for _r in U26_ROWS]
_u26sets = [_s for _s in PACK_SETS if _s["role"] == "ut"]
assert sorted(_s["name"] for _s in _u26sets) == ["Battlegrounds", "Ghost Calvary", "Ghost Rook", "Ghost Sword", "Hepta Axe"], [_s["name"] for _s in _u26sets]
assert len(U26_IDS) == len(set(U26_IDS)) == 18 and sorted(U26_IDS) == sorted(_i for _s in _u26sets for _i in _s["ids"]), "0.3.26: the rows = the 18 ids of tools/pack_drops.py's five role-ut sets"
assert not set(U26_IDS) & set(UT_IDS) and not set(U26_IDS) & set(AZ_ITEMS)
_U26_TRICK = ("lowhp", "back", "front", "taken", "hp", "mregen", "range", "pierce", "heal", "kb")
_U26_ZONE = {1: (1, 20), 2: (20, 30), 3: (30, 45), 4: (45, 60), 5: (60, 75)}          # LOCKED 2026-10-01 zone bands (docs/answered/mobs.md)
_u26row = dict((_r[0], _r) for _r in PACK_ROWS)
for _i, _a, _b, _tx, _fx in U26_ROWS:
    assert "," not in _tx and "=" not in _tx and all(32 <= ord(_c) < 127 for _c in _tx) and len(_tx) <= 110, _i
    _bd, _fd = _fx.split(",")
    assert _bd.split() and all(_k in S_KEYS for _k in _bd.split()), "0.3.26 %s: a body key is no live stat key: %s" % (_i, _bd)
    for _w in _fd.split():
        assert re.match(r"^swing=(slow|medium|fast|superfast)$", _w) or (re.match(r"^([a-z]+)[+-][0-9.]+$", _w) and re.match(r"^([a-z]+)", _w).group(1) in set(S_KEYS) | set(_U26_TRICK)), \
            "0.3.26 %s: a fixed word outside the GearUtFx grammar: %s" % (_i, _w)
    assert all(32 <= ord(_c) < 127 for _c in _fx) and len(_fx) <= 300
    _pz = PKD.zone_of(_u26row[_i][4])
    assert _u26row[_i][6] == 1 and (_a, _b) == ((UT_LO, UT_HI) if _pz == 1 else (45, 59)), (_i, _pz, _a, _b)
    assert _pz in (1, 4) and (_pz == 1 or _U26_ZONE[_pz][0] <= _a <= _b <= _U26_ZONE[_pz][1]), "0.3.26 %s: Lv %d-%d is not inside zone %d" % (_i, _a, _b, _pz)
assert [PKD.zone_of(_u26row[_i][4]) for _i in U26_IDS if _i == "Hepta_Axe"] == [4] and _u26row["Hepta_Axe"][4] == "adamantite"
# The Armory 1.23.0 (read-only): every id is there with no Recipe, no recipe in the jar makes it, the slot / weapon the row text assumes
_u26aj = [_p for _p in _ARMJ if os.path.basename(_p) == "TheArmoryMod-1.23.0.jar"]
if _u26aj:
    with zipfile.ZipFile(_u26aj[0]) as _z:
        _u26it = PKD._items(_z)
        _u26out = set()
        for _n in _z.namelist():
            if _n.endswith(".json"):
                try:
                    _txt = _z.read(_n).decode("utf-8-sig")
                except Exception:
                    continue
                for _i in U26_IDS:
                    if ('"%s"' % _i) in _txt and re.search(r'"(Output|PrimaryOutput|Outputs|Result)"\s*:', _txt) and not _n.endswith("/%s.json" % _i):
                        _u26out.add((_i, _n))
    _u26sc = dict((_x[0], _x) for _x in PKD.scan(_u26aj[0]))
    _miss = [_i for _i in U26_IDS if _i not in _u26it]
    assert not _miss, "0.3.26: not in The Armory 1.23.0: %s" % _miss
    assert not [_i for _i in U26_IDS if "Recipe" in _u26it[_i]], "0.3.26: an Untiered id has a Recipe in The Armory 1.23.0"
    assert not _u26out, "0.3.26: a recipe file in The Armory 1.23.0 names an Untiered id: %s" % sorted(_u26out)[:4]
    _slot = {"Helm": "Head", "Open": "Head", "Chest": "Chest", "Gauntlets": "Hands", "Boots": "Legs", "Leggings": "Legs", "Crown": "Head", "Amulet": "Chest"}
    for _i in U26_IDS:
        if _i in ("GhostSword", "Hepta_Axe"):
            assert _u26sc[_i][3] and _u26sc[_i][4] == {"GhostSword": "Template_Weapon_Sword", "Hepta_Axe": "Template_Weapon_Battleaxe"}[_i], _u26sc[_i]
        else:
            _w = [_v for _k, _v in sorted(_slot.items()) if _k in _i.replace("Ghost", "").replace("Wraith", "").replace("Calvary", "").replace("Rook", "").replace("Tarnished", "").replace("Verdant", "")]
            assert not _u26sc[_i][3] and _w and _u26sc[_i][1] in _w, "0.3.26 %s: slot %s, the row text assumes %s" % (_i, _u26sc[_i][1], _w)
    print("0.3.26 Armory UT ids: all 18 in %s, no Recipe, no recipe output, slots / weapon templates as the rows assume" % os.path.basename(_u26aj[0]))
else:
    print("0.3.26 Armory UT ids: The Armory 1.23.0 is not in the Mods folder - the jar checks are SKIPPED (GearUt still refuses crafted ids at run time)")
U26_MARK_ID = "SkyyGear 0.3.26 armory untiered"
U26_WHO = "SkyyGear 0.3.26"
U26_HEAD = "# ---- The five Armory Untiered sets (SkyyGear 0.3.26; needs The Armory by LadyPaladra) ----"
U26_MARK = ("# %s (Skyy 2026-10-18): Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword and Hepta Axe drop as Untiered items "
            "(research/UT-Lines-Draft.md 2.1)" % U26_MARK_ID)
U26_GROUPS = [("# ---- the Armory Untiered rows (ut.<item id>=<min level>,<max level>,<trade-off line>) ----",
               ["ut.%s=%d,%d,%s" % (_r[0], _r[1], _r[2], _r[3]) for _r in U26_ROWS]),
              ("# ---- their lines (utfx.<item id>=<body stat keys>,<fixed lines + tricks>) ----", ["utfx.%s=%s" % (_r[0], _r[4]) for _r in U26_ROWS])]
U26_LINES = [U26_HEAD, U26_MARK] + [_x for _c, _ls in U26_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in U26_LINES) and all("=" not in _x for _x in (U26_HEAD, U26_MARK))
assert len(set(U26_LINES)) == len(U26_LINES) and not set(U26_LINES) & set(UB_LINES) and U26_MARK_ID not in UB_MARK
# the change-log rows (CONFIG-CONTRACT 1.4.6): table key[entry], old (none), new = the columns joined by |
U26_LK = [("ut[%s]" % _r[0], "%d|%d|%s" % (_r[1], _r[2], _r[3])) for _r in U26_ROWS] + [("utfx[%s]" % _r[0], _r[4].replace(",", "|")) for _r in U26_ROWS]
assert len(U26_LK) == 36 and all("\t" not in _k + _v for _k, _v in U26_LK)
''')
rep('''    L += [""] + M22_LINES      # 0.3.22: the new metals' level bands (migrate0322 adds the missing rows of it to an older file)''',
    '''    L += [""] + U26_LINES      # 0.3.26: the five Armory Untiered sets (migrate0326 adds the missing rows of it to an older file)
    L += [""] + M22_LINES      # 0.3.22: the new metals' level bands (migrate0322 adds the missing rows of it to an older file)''')
after('''for _r in UT_ROWS:
    assert _dp.get("ut." + _r[1]) == "%d,%d,%s" % (UT_LO, UT_HI, _r[6]) and _dp.get("utfx." + _r[1]) == "%s,%s" % (_r[4], _r[5]), _r[1]
''', '''for _r in U26_ROWS:          # 0.3.26: the Armory Untiered block once, right before the 0.3.22 block; its rows read back
    assert _dp.get("ut." + _r[0]) == "%d,%d,%s" % _r[1:4] and _dp.get("utfx." + _r[0]) == _r[4], _r[0]
assert DEFAULT_TEXT.count(U26_MARK_ID) == 1 and all(_DL.count(_x) == 1 for _x in U26_LINES)
assert _DL[_DL.index(U26_HEAD) - 1:_DL.index(U26_HEAD) + len(U26_LINES) + 1] == [""] + U26_LINES + [""] and _DL[_DL.index(U26_HEAD) + len(U26_LINES) + 1] == M22_HEAD
''')
after('''F(gcf, "public static final String[] M22_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in M22_GROUPS for _x in _ls]))
''', '''F(gcf, "public static final String U26_MARK = %s;" % jstr(U26_MARK))          # 0.3.26 migrate0326
F(gcf, "public static final String U26_MARK_ID = %s;" % jstr(U26_MARK_ID))
F(gcf, "public static final String U26_WHO = %s;" % jstr(U26_WHO))
F(gcf, "public static final String U26_HEAD = %s;" % jstr(U26_HEAD))
F(gcf, "public static final String[] U26_GC = %s;" % jarr([_c for _c, _ls in U26_GROUPS]))
F(gcf, "public static final int[] U26_GS = %s;" % jints([len(_ls) for _c, _ls in U26_GROUPS]))
F(gcf, "public static final String[] U26_GL = %s;" % jarr([_x for _c, _ls in U26_GROUPS for _x in _ls]))
F(gcf, "public static final String[] U26_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in U26_GROUPS for _x in _ls]))
F(gcf, "public static final String[] U26_LK = %s;" % jarr([_k for _k, _v in U26_LK]))
F(gcf, "public static final String[] U26_LV = %s;" % jarr([_v for _k, _v in U26_LK]))
assert [_x.split("=", 1)[0] for _c, _ls in U26_GROUPS for _x in _ls] == ["ut." + _r[0] for _r in U26_ROWS] + ["utfx." + _r[0] for _r in U26_ROWS]
''')
after('''    @PKG@.Gear.warn("could not update config.properties to the 0.3.23 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
''', r'''# ---- 0.3.26 ONE-TIME UPDATE migrate0326 (PROJECT-RULES section 4; tools/gear_0_3_26_patch.py item 2): the migrate0322 shape (m22Update ->
# u26Update on the U26_ block): a pure ADDITION at the END of the file, only the ut / utfx rows the file lacks (in ANY case - kept + noted, never
# doubled); null = the marker is already in a comment line. Else { new text, notes, "ut.X, ..." (added), String[] log rows (key, new) }.
M(gcf, r"""
public static Object[] u26Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(U26_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    k = e + 1;
  }
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add("");
  blk.add(U26_HEAD);
  blk.add(U26_MARK);
  int at = 0;
  for (int g = 0; g < U26_GC.length; g++) {
    boolean first = true;
    for (int j = 0; j < U26_GS[g]; j++) {
      int x = at + j;
      if (has22(pp, U26_GK[x])) { notes.add(U26_GK[x] + " is already in the file - kept"); continue; }
      if (first) { blk.add(U26_GC[g]); first = false; }
      blk.add(U26_GL[x]);
      rows.add(U26_LK[x]);
      rows.add(U26_LV[x]);
      if (added.length() > 0) added.append(", ");
      added.append(U26_GK[x]);
    }
    at = at + U26_GS[g];
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 8192);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), (String[]) notes.toArray(new String[0]), added.toString(), (String[]) rows.toArray(new String[0]) };
}""")
M(gcf, r"""
public static String u26Log(String k, String n) {
  return @PKG@.CfgLog.now() + "\t" + U26_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t(none)\t" + @PKG@.CfgRows.oneLine(n) + "\tok";
}""")
# setup(), right after migrate0323 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one
# change-log row per added entry (Undo removes it), one INFO line (+ one per note), gear.log; "" = nothing done (no file, marker there, a failure)
M(gcf, r"""
public static synchronized String migrate0326() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = u26Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), U26_WHO, "before the 0.3.26 Armory Untiered update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated with the 0.3.26 Armory Untiered rows: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the five Armory sets stay plain drops-off until then; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 1 < rows.length; i += 2) @PKG@.CfgLog.enqueue(u26Log(rows[i], rows[i + 1]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String[] notes = (String[]) r[1];
    String add = (String) r[2];
    String msg = "config.properties: the 0.3.26 Armory Untiered rows were added at the end (" + (rows.length / 2) + " rows" + (add.length() > 0 ? "" : " - only the marker, every key was there") + "; Undo in Server Setup's change log); no value changed; the old file is kept in config-history";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.3.26 Armory Untiered: added " + (add.length() > 0 ? add : "the marker only") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.3.26 Armory Untiered rows to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
''')
rep('''  @PKG@.GearCfg.migrate0323();          // 0.3.23: the 15-step tool ladders + no ore floor (only the untouched 0.3.22 defaults)''',
    '''  @PKG@.GearCfg.migrate0323();          // 0.3.23: the 15-step tool ladders + no ore floor (only the untouched 0.3.22 defaults)
  @PKG@.GearCfg.migrate0326();          // 0.3.26: the five Armory Untiered sets (a pure addition of the missing rows)''')

# ================================================================================================================ manifest
rep('''LIFELONG MULTITOOL: merge your lifelong pickaxe + hatchet of one tier''',
    '''ARMORY UNTIERED: Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword and Hepta Axe (The Armory) drop as Untiered items with their own trade-off. LIFELONG MULTITOOL: merge your lifelong pickaxe + hatchet of one tier''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("public static boolean has22(") < _i("public static Object[] u26Update(") < _i("public static String u26Log(") < _i("public static synchronized String migrate0326()")
assert _i("public static synchronized String migrate0326()") < _i("  @PKG@.GearCfg.migrate0326();")
assert _i("def _g23_art(") < _i("G26_ART = _g23_art(") < _i("assert len(G23_ITEMJ) == 49") < _i("EXTRA.update(G23_FILES)")
assert _i("HARV_ITEMS = {}") < _i("G26_IDS = ") and _i("UB_LINES = [UB_HEAD") < _i("U26_ROWS = []") < _i("def default_text():")
assert _i("_ARMJ = sorted(") < _i("_u26aj = ")
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count(' = mk("') == MK0, "no new class"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.25 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.25 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
