"""Derive SkyyAccessories/build_skyyaccessories_0.5.8.py from the GENERATED 0.5.7 script (build_skyyaccessories_0.5.7.py = the
tools/deploy_set.py SET pin, written by tools/accessories_0_5_7_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.7 script
stays untouched - never re-run accessories_0_5_7_patch.py on top of this).
Run:  python tools/accessories_0_5_8_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.8.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.8.py   (bare JVM -Xverify:all; every 0.5.7 check + the bag look + the ENGINE
      asset validators on the jar)

0.5.8 = THE NEW ACCESSORY BAG LOOK (art only, no gameplay change). Skyy 2026-10-07: "lets make new items for the accessory bag, and the
pocket dimension bags too, the current ones are boring"; 2026-10-08: "the accessory bag is a little too over decorated.  but i love the
bags." + "3. yes 4. yes" (keep the 5 accessory-line gem colours) + "as drawn, violet. start the bag round" (docs/answered/bags.md).
  - The art is GENERATED AT BUILD TIME by the tracked generator tools/art/make_bags.py (the same one SkyySacks 0.7.14 runs), imported and
    run IN MEMORY (its write() fills a dict, clean_old() is a no-op): nothing is written outside the jar, nothing is committed.
  - Only the Accessory Bag item (Skyy_Accessory_Bag) changes, through item(..., visual=): Model = Items/SkyyAccessories/
    SkyyAccessories_Bag.blockymodel, Texture = ..._Bag_Texture.png, Icon = Icons/ItemsGenerated/SkyyAccessories_Bag.png, IconProperties
    from the generator's manifest. No Animation, no PlayerAnimationsId (the vanilla Item hold), no new interaction.
  - The 3 files ship in the jar at those paths (never a vanilla path - build check). The Workbench tab icon stays the vanilla bag icon.
  - Build checks: the bag JSON = the manifest look; the 44 own icons + the bag icon are the only ItemsGenerated files; every other item's
    icon / model is unchanged (0.5.7's checks, the bag excepted); no Parallel with fewer than 2 entries anywhere in the jar.
UNVERIFIED (in game only): how the toned-down bag looks held / dropped / as an icon on a real slot.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.7.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.8.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.7"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.7"\n' in s and "OWN_ICON" in s and "make_bags" not in s, "the source must be the generated 0.5.7 script"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")
_ASSETS_MARK = "# ================= assets: items + lang =================" + LF
assert s.count(_ASSETS_MARK) == 1
CODE057 = s[s.index("import "):s.index(_ASSETS_MARK)]

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.7 - build script (derived from the generated build_skyyaccessories_0.5.6.py by tools/accessories_0_5_7_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.7.py            -> SkyyAccessories/SkyyAccessories-0.5.7.jar
       python build_skyyaccessories_0.5.7.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.7.py             (bare JVM -Xverify:all: every 0.5.6 check + the 0.5.7 icon checks)
''', '''"""SkyyAccessories 0.5.8 - build script (derived from the generated build_skyyaccessories_0.5.7.py by tools/accessories_0_5_8_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.8.py            -> SkyyAccessories/SkyyAccessories-0.5.8.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.8.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.8.py             (bare JVM -Xverify:all: every 0.5.7 check + the bag look + the engine asset validators)
0.5.8: THE NEW ACCESSORY BAG LOOK (Skyy 2026-10-08: "the accessory bag is a little too over decorated.  but i love the bags.", "as drawn,
     violet. start the bag round"; full notes in tools/accessories_0_5_8_patch.py): tools/art/make_bags.py runs IN MEMORY at build time
     and the Accessory Bag item gets its toned-down model / texture / icon / IconProperties through item(..., visual=). Art only:
     classes (version constants only), every other item, recipes, texts and saved data unchanged.
''')
rep('VERSION = "0.5.7"\n', 'VERSION = "0.5.8"\n')

# ---------------------------------------------------------------------------------------------------------------- the bag art
ART = '''# ---- 0.5.8 THE NEW ACCESSORY BAG LOOK: tools/art/make_bags.py (tracked, deterministic) runs IN MEMORY - its write() fills BAG_GEN, its
# clean_old() does nothing; only the Accessory Bag's 3 files ship here (the Pocket Dimension bags' files ship in SkyySacks 0.7.14)
def _bag_art():
    import importlib.util as _ilu2
    _sp = _ilu2.spec_from_file_location("make_bags", os.path.join(os.path.dirname(HERE), "tools", "art", "make_bags.py"))
    _mb = _ilu2.module_from_spec(_sp)
    _sp.loader.exec_module(_mb)
    _got = {}
    def _w(rel, data):
        assert rel not in _got, "make_bags wrote %s twice" % rel
        _got[rel] = bytes(data)
        return rel
    _mb.write = _w
    _mb.clean_old = lambda: None
    _mb.main()
    return _got
BAG_GEN = _bag_art()
BAG_MAN = json.loads(BAG_GEN["manifest.json"].decode("utf-8"))["accessory_bag"]
assert BAG_MAN["item"] == BAG, BAG_MAN["item"]
def _bag_nc(p):
    assert p.startswith("Common/"), p
    return p[len("Common/"):]
BAG_VIS = {"Model": _bag_nc(BAG_MAN["model_path"]), "Texture": _bag_nc(BAG_MAN["texture_path"]), "Icon": _bag_nc(BAG_MAN["icon_path"]),
           "IconProperties": BAG_MAN["icon_properties"]}
BAG_FILES = dict((p, BAG_GEN[p]) for p in (BAG_MAN["model_path"], BAG_MAN["texture_path"], BAG_MAN["icon_path"]))
for _p in BAG_FILES:
    assert _p not in _COMMON, "0.5.8: the bag art would override a vanilla file: " + _p
print("bag art: tools/art/make_bags.py ran in memory (%d files); the Accessory Bag ships %d (%s)" % (
    len(BAG_GEN), len(BAG_FILES), ", ".join(sorted(BAG_FILES))))
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, BAG_VIS["Icon"], QUAL_IDS[2],
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], BAG_REQ, "SkyyAccBag",
    visual=BAG_VIS), indent=2)   # 0.5.8: the new look through visual= (was the vanilla backpack + Utility_Bag_Seed icon)
for _p, _b in BAG_FILES.items():
    assert _p not in files, _p
    files[_p] = _b
'''
rep('''files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, "Icons/ItemsGenerated/Utility_Bag_Seed.png", QUAL_IDS[2],
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], BAG_REQ, "SkyyAccBag"), indent=2)
''', ART)

# ---------------------------------------------------------------------------------------------------------------- 0.5.7's icon audit knows the bag icon
rep('''    own = set("Common/" + r for r in OWN_ICON.values())
    assert sorted(p for p in files if p.startswith("Common/Icons/ItemsGenerated/")) == sorted(own), "0.5.7: exactly our 44 icons in ItemsGenerated"
    for iid, n in items.items():
        if iid not in want:''', '''    own = set("Common/" + r for r in OWN_ICON.values()) | {"Common/" + BAG_VIS["Icon"]}   # 0.5.8: + the Accessory Bag's own icon
    assert sorted(p for p in files if p.startswith("Common/Icons/ItemsGenerated/")) == sorted(own), "0.5.8: exactly our 44 icons + the bag icon in ItemsGenerated"
    for iid, n in items.items():
        if iid not in want and iid != BAG:''')
rep('''    print("own icon audit: %d booster ids (40 line + 4 Lantern + 20 hidden legacy) -> %d distinct own 64x64 icons; %d other items keep "
          "their vanilla icon" % (len(want), len(set(want.values())), len(items) - len(want)))''',
    '''    print("own icon audit: %d booster ids (40 line + 4 Lantern + 20 hidden legacy) -> %d distinct own 64x64 icons; %d other items keep "
          "their vanilla icon; the Accessory Bag has its own" % (len(want), len(set(want.values())), len(items) - len(want) - 1))''')

# ---------------------------------------------------------------------------------------------------------------- the new check
CHECK = '''

def _bag_look_check():
    """0.5.8 build check: the Accessory Bag = the manifest look (model / texture / icon / IconProperties), its 3 files ship (bytes, never a
    vanilla path), no animation / player set; the PNGs have the manifest sizes; no Parallel with fewer than 2 entries in the jar"""
    import struct as _st
    n = json.loads(files["Server/Item/Items/Utility/%s.json" % BAG])
    for k, v in BAG_VIS.items():
        assert n[k] == v, (k, n[k], v)
    assert "Animation" not in n and "PlayerAnimationsId" not in n and "Particles" not in n, "the bag keeps the vanilla Item hold"
    assert n["Interactions"] == {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyyAccBag"}}]}}, n["Interactions"]
    for k in ("Model", "Texture", "Icon"):
        assert isinstance(files["Common/" + n[k]], bytes) and ("Common/" + n[k]) not in _COMMON, k
    tw, th = _st.unpack(">II", files["Common/" + n["Texture"]][16:24])
    iw, ih = _st.unpack(">II", files["Common/" + n["Icon"]][16:24])
    assert [tw, th] == BAG_MAN["texture_size"] and (iw, ih) == (64, 64), (tw, th, iw, ih)
    bad = []
    def walk(p, x):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                bad.append(p)
            for v in x.values():
                walk(p, v)
        elif isinstance(x, list):
            for v in x:
                walk(p, v)
    nj = 0
    for p, t in files.items():
        if p.startswith("Server/") and p.endswith(".json"):
            walk(p, json.loads(t))
            nj += 1
    assert not bad, "a Parallel with fewer than 2 entries (the engine refuses the whole pack): %s" % bad
    print("bag look checked: %s = %s (texture %d x %d, icon 64 x 64), %d JSON files without a short Parallel" % (BAG, n["Model"], tw, th, nj))


_bag_look_check()
'''
rep('''

_own_icon_checks()
''', '''

_own_icon_checks()
''' + CHECK)

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s[s.index("import "):s.index(_ASSETS_MARK)] == CODE057.replace('VERSION = "0.5.7"\n', 'VERSION = "0.5.8"\n'), \
    "every line before the assets = 0.5.7's (only the version)"
assert s.index("BAG_REQ = FIELD_REQ") < s.index("BAG_VIS = {") and s.index("files = {}") < s.index("BAG_FILES = dict(")
assert s.index("_own_icon_checks()\n\n\ndef _bag_look_check") < s.index("B.assemble(")
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.7 - build script (derived from the generated build_skyyaccessories_0.5.6.py by tools/accessories_0_5_7_patch.py -',
    "Run:   python build_skyyaccessories_0.5.7.py            -> SkyyAccessories/SkyyAccessories-0.5.7.jar",
    "       python build_skyyaccessories_0.5.7.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world",
    "Test:  python test_skyyaccessories_0.5.7.py             (bare JVM -Xverify:all: every 0.5.6 check + the 0.5.7 icon checks)",
    'VERSION = "0.5.7"',
    'files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, "Icons/ItemsGenerated/Utility_Bag_Seed.png", QUAL_IDS[2],',
    '    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], BAG_REQ, "SkyyAccBag"), indent=2)',
    '    own = set("Common/" + r for r in OWN_ICON.values())',
    '    assert sorted(p for p in files if p.startswith("Common/Icons/ItemsGenerated/")) == sorted(own), "0.5.7: exactly our 44 icons in ItemsGenerated"',
    '        if iid not in want:',
    '          "their vanilla icon" % (len(want), len(set(want.values())), len(items) - len(want)))',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.7 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.7 had %d)" % (s.count(LF), OLD.count(LF)))
