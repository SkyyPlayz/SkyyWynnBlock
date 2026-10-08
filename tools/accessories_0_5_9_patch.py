"""Derive SkyyAccessories/build_skyyaccessories_0.5.9.py from the GENERATED 0.5.8 script (build_skyyaccessories_0.5.8.py = the
tools/deploy_set.py SET pin, written by tools/accessories_0_5_8_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.8 script
stays untouched - never re-run accessories_0_5_8_patch.py on top of this).
Run:  python tools/accessories_0_5_9_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.9.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.9.py   (bare JVM -Xverify:all; every 0.5.8 check + the tab icon + the gem order +
      the ENGINE asset validators on the jar)

0.5.9 = THE NEW ACCESSORY BAG ICON ON THE WORKBENCH TAB + THE MODEL'S GEMS MATCH IT (art only, no gameplay change). Skyy 2026-10-08:
"Use Option B gem colors", "Make it a little brighter with a more leather look (still black leather, just lighter", "Yes, the bag icon
looks good, commit it" (the art agent's icon: art/accessory-bag-icon/, ART-RESUME.md Done item 2; original art, committed).
  - The Workbench "Accessories & Bags" tab icon (Common/Icons/CraftingCategories/SkyyAccessories/AccessoriesBags.png, the path
    tools/skyywbtab.py icon_path names) = art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png, byte for byte
    (was Assets.zip's Utility_Bag_Seed.png). Build checks: sha256 = the art folder's manifest.json, a 64 x 64 RGBA PNG like the vanilla
    tab icons, alpha only 0 / 255, never a vanilla path. SkyySacks' fallback copy of the tab (its own Icons/CraftingCategories/SkyySacks/
    path, tools/skyywbtab.py ICON_SRC) is untouched: with both mods the tab is SkyyAccessories' entry (owner rule), so it shows this icon.
  - The Accessory Bag MODEL's 5 clasp gems follow the icon (Option B, left to right Health red #d23a3a, Stamina yellow #d6a800, Mana blue
    #2f6fe0, Regeneration green #2fb34f, Speed cyan #4ac0cc): tools/art/make_bags.py ACC_GEMS (the generator, run in memory by the
    build as in 0.5.8). Only the bag's texture + its own item icon change; the model, IconProperties and every Pocket Dimension bag file
    are byte-identical. The leather stays as in 0.5.8: the icon README's leather tweak is for the icon only (its open question 1 asks the
    model to follow the GEMS only).
  - Build check (new): make_bags ACC_GEMS mid tones, left to right = the art manifest's gems_left_to_right hex_mid list.
UNVERIFIED (in game only): the tab icon at the Workbench's small tab size; the held bag's new gems.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.8.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.9.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.8"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.8"\n' in s and "make_bags" in s and "_bag_look_check()" in s and "TAB_ICON_SRC" not in s, \
    "the source must be the generated 0.5.8 script"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")
_ASSETS_MARK = "# ================= assets: items + lang =================" + LF
assert s.count(_ASSETS_MARK) == 1
CODE058 = s[s.index("import "):s.index(_ASSETS_MARK)]

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.8 - build script (derived from the generated build_skyyaccessories_0.5.7.py by tools/accessories_0_5_8_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.8.py            -> SkyyAccessories/SkyyAccessories-0.5.8.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.8.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.8.py             (bare JVM -Xverify:all: every 0.5.7 check + the bag look + the engine asset validators)
''', '''"""SkyyAccessories 0.5.9 - build script (derived from the generated build_skyyaccessories_0.5.8.py by tools/accessories_0_5_9_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.9.py            -> SkyyAccessories/SkyyAccessories-0.5.9.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.9.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.9.py             (bare JVM -Xverify:all: every 0.5.8 check + the tab icon + the gem order + the engine
       asset validators)
0.5.9: THE NEW ACCESSORY BAG ICON (Skyy 2026-10-08: "Use Option B gem colors", "Yes, the bag icon looks good, commit it"; full notes in
     tools/accessories_0_5_9_patch.py): the Workbench "Accessories & Bags" tab icon = art/accessory-bag-icon/.../SkyyAccessories_Bag_Menu.png
     (original art, committed; was the vanilla Utility_Bag_Seed icon), and the Accessory Bag model's 5 gems follow it (tools/art/make_bags.py
     ACC_GEMS, left to right Health red, Stamina yellow, Mana blue, Regeneration green, Speed cyan). Art only: classes (version constants
     only), every other item, recipes, texts and saved data unchanged.
''')
rep('VERSION = "0.5.8"\n', 'VERSION = "0.5.9"\n')

# ---------------------------------------------------------------------------------------------------------------- the tab icon
rep('''# 0.5.2: the tab icon = Assets.zip's Utility_Bag_Seed.png (the Accessory Bag's own icon), copied into the jar where tab icons live
files["Common/" + WB.icon_path("SkyyAccessories")] = WB.icon_png(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
''', '''# 0.5.9: the tab icon = OUR Accessory Bag icon (art/accessory-bag-icon/, original art, committed - Skyy 2026-10-08 "Yes, the bag icon looks
# good, commit it"), copied byte for byte into the jar where tab icons live (0.5.2 - 0.5.8: Assets.zip's Utility_Bag_Seed.png). SkyySacks'
# fallback copy (tools/skyywbtab.py ICON_SRC, its own path) is untouched.
TAB_ICON_DIR = os.path.join(os.path.dirname(HERE), "art", "accessory-bag-icon")
TAB_ICON_REL = "Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png"
TAB_ICON_SRC = os.path.join(TAB_ICON_DIR, *TAB_ICON_REL.split("/"))


def _tab_icon():
    """0.5.9: the art folder's icon, checked: sha256 + size = its manifest.json, a 64 x 64 RGBA PNG (8-bit) like the vanilla tab icons
    (Assets.zip Workbench/Processing.png size), alpha only 0 or 255, the jar path is no vanilla file"""
    import hashlib as _hl, struct as _st, zlib as _zl
    data = open(TAB_ICON_SRC, "rb").read()
    man = json.load(open(os.path.join(TAB_ICON_DIR, "manifest.json"), encoding="utf8"))
    ent = [f for f in man["files"] if f["path"] == TAB_ICON_REL]
    assert len(ent) == 1, "0.5.9: the art manifest lists %s once" % TAB_ICON_REL
    assert _hl.sha256(data).hexdigest() == ent[0]["sha256"] and len(data) == ent[0]["bytes"], "0.5.9: the icon is not the art manifest's"
    assert data[:8] == b"\\x89PNG\\r\\n\\x1a\\n" and data[12:16] == b"IHDR", "0.5.9: the tab icon is not a PNG"
    w, h = _st.unpack(">II", data[16:24])
    ref = _ASSETS.read("Common/Icons/CraftingCategories/Workbench/Processing.png")
    assert (w, h) == _st.unpack(">II", ref[16:24]) == (64, 64) and data[24:26] == b"\\x08\\x06", "0.5.9: not 64 x 64 RGBA8 like the vanilla tab icons"
    # alpha only 0 / 255 (straight or premultiplied is then the same): inflate the IDAT stream, undo the PNG row filters
    i, idat = 8, b""
    while i < len(data):
        ln = _st.unpack(">I", data[i:i + 4])[0]
        if data[i + 4:i + 8] == b"IDAT":
            idat += data[i + 8:i + 8 + ln]
        i += 12 + ln
    raw_ = _zl.decompress(idat)
    bpp, stride, prev, alphas = 4, w * 4, bytearray(w * 4), set()
    for y in range(h):
        ft, row = raw_[y * (stride + 1)], bytearray(raw_[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = row[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ft == 1:
                row[x] = (row[x] + a) & 255
            elif ft == 2:
                row[x] = (row[x] + b) & 255
            elif ft == 3:
                row[x] = (row[x] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[x] = (row[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            else:
                assert ft == 0, "0.5.9: PNG filter %d" % ft
        alphas.update(row[3::4])
        prev = row
    assert alphas <= {0, 255} and alphas == {0, 255}, "0.5.9: the tab icon must have hard alpha (0 / 255): %s" % sorted(alphas)[:8]
    return data


files["Common/" + WB.icon_path("SkyyAccessories")] = _tab_icon()
assert "Common/" + WB.icon_path("SkyyAccessories") not in _COMMON, "0.5.9: the tab icon path would override a vanilla file"
print("Workbench tab icon: %s (%d bytes, art/accessory-bag-icon) -> %s" % (TAB_ICON_REL.split("/")[-1], len(files["Common/" + WB.icon_path("SkyyAccessories")]),
                                                                           WB.icon_path("SkyyAccessories")))
''')

# ---------------------------------------------------------------------------------------------------------------- the new check
CHECK = '''

def _gem_order_check():
    """0.5.9 build check: the Accessory Bag model's 5 gems (tools/art/make_bags.py ACC_GEMS, left to right) = the approved icon's gems
    (art/accessory-bag-icon/manifest.json gems_left_to_right hex_mid): Option B - Health red, Stamina yellow, Mana blue, Regeneration
    green, Speed cyan; the tab icon is the art folder's file byte for byte"""
    import importlib.util as _ilu3
    _sp = _ilu3.spec_from_file_location("make_bags_gems", os.path.join(os.path.dirname(HERE), "tools", "art", "make_bags.py"))
    _mb = _ilu3.module_from_spec(_sp)
    _sp.loader.exec_module(_mb)
    mids = ["#%02x%02x%02x" % tuple(g[2]) for g in _mb.ACC_GEMS]
    man = json.load(open(os.path.join(TAB_ICON_DIR, "manifest.json"), encoding="utf8"))
    ent = [f for f in man["files"] if f["path"] == TAB_ICON_REL][0]
    want = [g["hex_mid"].lower() for g in ent["gems_left_to_right"]]
    assert [g["line"] for g in ent["gems_left_to_right"]] == ["Health", "Stamina", "Mana", "Regeneration", "Speed"], ent["gems_left_to_right"]
    assert mids == want == ["#d23a3a", "#d6a800", "#2f6fe0", "#2fb34f", "#4ac0cc"], (mids, want)   # ui-data: the gem art colours, no UI
    assert files["Common/" + WB.icon_path("SkyyAccessories")] == open(TAB_ICON_SRC, "rb").read()
    print("gem order checked: the bag model's gems = the icon's, left to right %s" % ", ".join(mids))


_gem_order_check()
'''
rep('''

_bag_look_check()
''', '''

_bag_look_check()
''' + CHECK)

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s[s.index("import "):s.index(_ASSETS_MARK)] == CODE058.replace('VERSION = "0.5.8"\n', 'VERSION = "0.5.9"\n'), \
    "every line before the assets = 0.5.8's (only the version)"
assert s.index("_bag_look_check()\n\n\ndef _gem_order_check") < s.index("B.assemble(")
assert s.index("def _tab_icon") > s.index("_ASSETS = zipfile.ZipFile(") and s.index("def _tab_icon") > s.index("_COMMON")
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.8 - build script (derived from the generated build_skyyaccessories_0.5.7.py by tools/accessories_0_5_8_patch.py -',
    "Run:   python build_skyyaccessories_0.5.8.py            -> SkyyAccessories/SkyyAccessories-0.5.8.jar   (deploys go through tools/deploy_set.py --yes)",
    "       python build_skyyaccessories_0.5.8.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)",
    "Test:  python test_skyyaccessories_0.5.8.py             (bare JVM -Xverify:all: every 0.5.7 check + the bag look + the engine asset validators)",
    'VERSION = "0.5.8"',
    "# 0.5.2: the tab icon = Assets.zip's Utility_Bag_Seed.png (the Accessory Bag's own icon), copied into the jar where tab icons live",
    'files["Common/" + WB.icon_path("SkyyAccessories")] = WB.icon_png(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.8 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.8 had %d)" % (s.count(LF), OLD.count(LF)))
