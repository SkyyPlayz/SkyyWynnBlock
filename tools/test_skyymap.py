"""Self-test of tools/skyymap.py (radial node maps, research/Radial-Trees-Spec.md round R1). Pure Python, no game files, no JVM.

    python tools/test_skyymap.py

Checks (every public function EXECUTED):
  LAYOUT  the three skill pages + the eight class trees at the pinned numbers SkyyTrees 0.5.0 uses (tools/trees_0_5_0_patch.py TM_PIN):
          check() passes (in the canvas, discs >= 6 px apart, click squares >= 2 px apart, every node once, the spine never jumps a row,
          lines point outward), the spec's corners (4 trees -> the corners; 3 -> top centre / bottom right / bottom left; the class page's
          banner offset), whole-px boxes, every free perk = a junction, hubs on the inner ring, deterministic (built twice = equal)
  REFUSE  check() raises MapError naming the pair for a crowded layout (44 px Gathering), a missing / extra node (want_ids), a node
          outside the canvas; fit_page() finds a layout for a small tree and raises when nothing fits; scaled() keeps every rule at 150 / 200 %
  ZOOM    scaled(): coordinates x z (rounded), canvas W x z, sizes x z; edge_boxes / scaled_boxes inside the canvas
  ART     png() = a valid PNG (decoded again by tools/skyyart.py), even @2x sizes, deterministic bytes; node_pictures(): every state name,
          no underscore, pips 1-9 only; base / gold pictures of a layout: the gold dots sit exactly on the grey dots (same positions);
          state_name() for every state; colour_name(); rgb() refuses a bad colour
Exit code 1 on a failure; prints "N ok, 0 fail".
"""
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skyymap as SM
import skyyart as A
import trees_v3_data as TD

OKS, FAILS = [0], []
COL = {"Mining": "#8fc8ff", "Foraging": "#8fe08a", "Farming": "#f0d060", "Fishing": "#6fb7e8", "Smithing": "#c0c8d0", "Cooking": "#ffb070",
       "Alchemy": "#7fe0d0", "Combat": "#ff8a7a", "Acrobatics": "#a8f0ff", "Exploration": "#b8e07a", "Beastmastery": "#d68fd0"}
PAGES = [("Gathering", ["Mining", "Foraging", "Farming", "Fishing"], dict(node=32, ring0=0.46, s=40.0, start=40.0)),
         ("Crafting", ["Smithing", "Cooking", "Alchemy"], dict(node=32, ring0=0.42, s=44.0, start=-5.0)),
         ("Adventure", ["Combat", "Acrobatics", "Exploration", "Beastmastery"], dict(node=32, ring0=0.46, s=40.0, start=55.0))]
CLASS_PIN = dict(node=36, ring0=0.38, s=52.0, start=0.0, banner_offset=60.0)
CLASSES = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)


def raises(fn, what, contains=None):
    try:
        fn()
    except SM.MapError as e:
        check(contains is None or contains in str(e), "%s (message: %s)" % (what, e))
        return
    except Exception as e:      # noqa
        FAILS.append("%s: raised %s instead of MapError: %s" % (what, type(e).__name__, e))
        return
    FAILS.append("%s: did not raise" % what)


def groups_of(trees):
    return [(t, COL[t], TD.tree(t)["branches"]) for t in trees]


def class_groups(cn):
    return [("B%d" % i, "#e0b060", [b]) for i, b in enumerate(TD.tree(cn)["branches"])]


def boxes_ok(lay):
    return all(n["l"] == int(n["l"]) and n["t"] == int(n["t"]) for n in lay["nodes"])


# ---------------------------------------------------------------------------------------------------- LAYOUT
LAYS = {}
for name, trees, pin in PAGES:
    g = groups_of(trees)
    lay = SM.build(g, want_ids=SM.want_of(g), what=name, **pin)
    LAYS[name] = lay
    check(lay["info"]["min_gap"] >= SM.GAP and lay["info"]["nodes"] == len(SM.want_of(g)), "%s: check passes (%d nodes, min gap %.2f)" % (name, lay["info"]["nodes"], lay["info"]["min_gap"]))
    check(boxes_ok(lay), "%s: whole-px boxes" % name)
    check(lay == SM.build(g, want_ids=SM.want_of(g), what=name, **pin), "%s: deterministic (built twice = equal)" % name)
    frees = [n["id"] for n in lay["nodes"] if n["kind"] == "free"]
    check(all(any(j.get("node") == f for j in lay["junctions"]) for f in frees), "%s: every free perk diamond is its row's junction" % name)
    hr = [math.hypot(h["cx"] - 420, h["cy"] - 387) for h in lay["hubs"]]
    check(max(hr) - min(hr) < 2 and min(hr) > lay["emb"] / 2.0, "%s: the hubs sit on one ring around the emblem" % name)
    sp = [e for e in lay["edges"] if e[2] == "spine"]
    check(len(sp) == sum(len(b["rows"]) for _k, _c, brs in g for b in brs), "%s: one spine edge per row" % name)
CORNERS4 = [(SM.MARGIN + 0, SM.MARGIN)]
g4 = LAYS["Gathering"]
spots = sorted((b["l"], b["t"]) for b in g4["banners"])
check(spots == sorted([(SM.MARGIN, SM.MARGIN), (840 - SM.MARGIN - SM.BANNER_W, SM.MARGIN), (SM.MARGIN, 774 - SM.MARGIN - SM.BANNER_H),
                       (840 - SM.MARGIN - SM.BANNER_W, 774 - SM.MARGIN - SM.BANNER_H)]), "Gathering: 4 trees -> the 4 corners")
g3 = LAYS["Crafting"]
check([b["align"] for b in g3["banners"]] == ["Center", "End", "Start"], "Crafting: 3 trees -> top centre, bottom right, bottom left")
mining = [h for h in g4["hubs"] if h["key"] == "Mining"][0]
check(mining["cx"] > 420 and mining["cy"] < 387, "Gathering: Mining top right (spec 3.4 step 1)")
fishing = [h for h in g4["hubs"] if h["key"] == "Fishing"][0]
check(fishing["cx"] < 420 and fishing["cy"] < 387, "Gathering: Fishing top left")
for cn in CLASSES:
    g = class_groups(cn)
    lay = SM.build(g, want_ids=SM.want_of(g), what=cn, **CLASS_PIN)
    check(lay["info"]["min_gap"] >= SM.GAP and len(lay["hubs"]) == 3, "%s: the class page passes (%d nodes, gap %.1f)" % (cn, lay["info"]["nodes"], lay["info"]["min_gap"]))
    check([b["align"] for b in lay["banners"]] == ["End", "Center", "Start"], "%s: banners between the branches (top right, bottom, top left)" % cn)
    LAYS[cn] = lay

# ---------------------------------------------------------------------------------------------------- REFUSE
gG = groups_of(PAGES[0][1])
raises(lambda: SM.build(gG, node=44, ring0=0.46, s=40.0, start=40.0, what="crowded"), "a 44 px Gathering is refused", "apart")
raises(lambda: SM.build(gG, want_ids=SM.want_of(gG)[1:], what="extra", **PAGES[0][2]), "an extra node is refused", "extra")
raises(lambda: SM.build(gG, want_ids=SM.want_of(gG) + [("Mining", 0, 0, "zz")], what="missing", **PAGES[0][2]), "a missing node is refused", "missing")
lay_bad = dict(LAYS["Crafting"])
lay_bad["nodes"] = [dict(n) for n in LAYS["Crafting"]["nodes"]]
lay_bad["nodes"][0]["l"] = -3
raises(lambda: SM.check(lay_bad, what="outside"), "a node outside the canvas is refused", "outside")
small = [("Fishing", COL["Fishing"], TD.tree("Fishing")["branches"])]
fit = SM.fit_page(small, sizes=(36, 32), ring0s=(0.46,), spacing=(12,), starts=(0,), what="fit")
check(fit["node"] in (36, 32) and fit["info"]["min_gap"] >= SM.GAP, "fit_page finds a layout for one light tree (%d px)" % fit["node"])
raises(lambda: SM.fit_page(gG, sizes=(60,), ring0s=(0.46,), spacing=(8,), starts=(0,), what="nofit"), "fit_page raises when nothing fits", "nothing fits")
raises(lambda: SM.rgb("red"), "rgb refuses a colour name")
raises(lambda: SM.node_pictures(["#123456"], [10]), "node_pictures refuses a rank max above 9 (pips)")

# ---------------------------------------------------------------------------------------------------- ZOOM
for name in ("Gathering", "Crafting", "Adventure", "Mage"):
    lay = LAYS[name]
    for z in (1.5, 2.0):
        lz = SM.scaled(lay, z, name)
        check(lz["W"] == int(round(840 * z)) and lz["H"] == int(round(774 * z)) and lz["info"]["nodes"] == len(lay["nodes"]),
              "%s at %d %%: the canvas x z, every node kept, check passes" % (name, z * 100))
        check(all(abs(a["cx"] - b["cx"] * z) <= 1 and abs(a["cy"] - b["cy"] * z) <= 1 and a["size"] == int(round(b["size"] * z))
                  for a, b in zip(lz["nodes"], lay["nodes"])), "%s at %d %%: centres x z (rounded), sizes x z" % (name, z * 100))
        bx = SM.scaled_boxes(SM.edge_boxes(lay), z, lz["W"], lz["H"])
        check(all(l >= 0 and t >= 0 and l + w <= lz["W"] and t + h <= lz["H"] and w > 0 and h > 0 for l, t, w, h in bx.values()),
              "%s at %d %%: every gold line box inside the canvas" % (name, z * 100))
    bx1 = SM.edge_boxes(lay)
    check(set(bx1) == set(k for k, d in enumerate(lay["edge_dots"]) if d), "%s: one box per drawn edge" % name)

# ---------------------------------------------------------------------------------------------------- ART
lay = LAYS["Crafting"]
base = SM.base_picture(lay)
pb = SM.png(base)
check(SM.png_size(pb) == (1680, 1548) and pb == SM.png(SM.base_picture(lay)), "base picture @2x 1680 x 1548, deterministic")
im = A.png_decode(pb)
check((im.w, im.h) == (1680, 1548) and any(im.px[i] for i in range(3, len(im.px), 4 * 97)), "base picture decodes (skyyart) and holds dots")
gold = SM.gold_pictures(lay)
bxs = SM.edge_boxes(lay)
check(set(gold) == set(bxs), "a gold picture per drawn edge")
k0 = sorted(gold)[3]
l, t, w, h = bxs[k0]
g0 = gold[k0]
check((g0.w, g0.h) == (2 * w, 2 * h) and g0.w % 2 == 0, "a gold picture = its box at @2x")
x, y = lay["edge_dots"][k0][0]
gi = (int(2 * (y - t)) * g0.w + int(2 * (x - l))) * 4 + 3
bi = (int(2 * y) * base.w + int(2 * x)) * 4 + 3
check(g0.px[gi] > 0 and base.px[bi] > 0, "the gold dot sits exactly on the grey dot (same positions)")
pics = SM.node_pictures(["#8fc8ff", "#e0b060"], [1, 2, 3, 5])
names = sorted(pics)
check(all("_" not in n for n in names) and "Locked" in pics and "Ready" in pics and "Soon" in pics and "Open" in pics and "FreeLocked" in pics,
      "node pictures: the shared states, no underscore")
cn = SM.colour_name("#8fc8ff")
check(cn == "C8fc8ff" and ("%sL25" % cn) in pics and ("%sMax5" % cn) in pics and ("%sCapMax" % cn) in pics and ("%sFree" % cn) in pics
      and ("%sL15" % cn) in pics and ("%sL45" % cn) in pics and ("%sL04" % cn) not in pics, "node pictures: learnt k / m, max, capstone, free per colour")
check(all(SM.png_size(SM.png(p))[0] in (64, 44) for p in pics.values()), "node pictures are 64 px (discs) / 44 px (diamonds) at @2x")
check(SM.png(pics["Ready"]) == SM.png(SM.node_picture(64, "ready")), "node pictures deterministic")
for args, want in (((("up", "#8fc8ff", False, 0, 5, 1)), "Ready"), (("up", "#8fc8ff", True, 0, 1, 0), "CapLocked"),
                   (("up", "#8fc8ff", False, 2, 5, 2), "C8fc8ffL25"), (("up", "#8fc8ff", False, 5, 5, 3), "C8fc8ffMax5"),
                   (("up", "#8fc8ff", True, 1, 1, 3), "C8fc8ffCapMax"), (("up", "#8fc8ff", False, 0, 3, 4), "Soon"),
                   (("up", "#8fc8ff", False, 0, 3, 5), "Open"), (("free", "#8fc8ff", False, 0, 0, 1), "C8fc8ffFree"),
                   (("free", "#8fc8ff", False, 0, 0, 0), "FreeLocked")):
    check(SM.state_name(*args) == want and (want in pics or want.replace("C8fc8ff", cn) in pics), "state_name%s = %s (a shipped picture)" % (args, want))
for p in (SM.hub_picture("#8fc8ff"), SM.halo_picture(), SM.emblem_picture()):
    d = SM.png(p)
    check(SM.png_size(d)[0] % 2 == 0 and A.png_decode(d).w == p.w, "hub / halo / emblem pictures decode, even sizes")
prev = SM.preview_picture(LAYS["Gathering"])
check((prev.w, prev.h) == (840, 774), "preview_picture draws a whole page")
print("skyymap %s self-test: %d ok, %d fail" % (SM.MAP_VERSION, OKS[0], len(FAILS)))
for f in FAILS:
    print("FAIL:", f)
sys.exit(1 if FAILS else 0)
