"""Derive SkyyAccessories/build_skyyaccessories_0.5.7.py from the GENERATED 0.5.6 script (build_skyyaccessories_0.5.6.py = the
tools/deploy_set.py SET pin, written by tools/acc_0_5_6_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.6 script stays
untouched - never re-run acc_0_5_6_patch.py on top of this).
Run:  python tools/accessories_0_5_7_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.7.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.7.py   (bare JVM -Xverify:all; every 0.5.6 check + the icon checks)

0.5.7 = OUR OWN ACCESSORY ICONS (art only, no gameplay change). Skyy 2026-10-07: "all of the items look beautiful. are they deployed in
game?" + "Amber works." (the Stamina enamel stays amber, models-local/art/accessories/README.md open issue 1).
  - The build imports tools/art/make_accessory_icons.py (tracked, our own art drawn by code, never reads Assets.zip) and draws the 44
    icons at BUILD time in memory (11 lines x Normal / Unique / Rare / Legendary, 64 x 64 RGBA, premultiplied, deterministic): the
    generator's own make() + to_img() + skyyart.png_encode, exactly what its main() writes. Nothing is committed but the generator.
  - Each PNG ships in the jar at Common/Icons/ItemsGenerated/SkyyAccessories_<Line>_<Rarity>.png (new names - never a vanilla path),
    and every booster item's "Icon" points at its own: the 40 line ids (Health=Vitality, Stamina=Endurance, Mana=Intelligence,
    Regeneration, Speed, Brawler=Strength, Runic=MagicPower, Stonehide=Defense, Razorfang=Crit, Feather; Common/Uncommon/Rare/Epic or
    T1..T4), the 4 Lantern ids, and the 20 hidden legacy ids of the 5 old lines (the icon of the tier they count as - unchanged rule).
  - Unchanged: the 3D held / dropped model (visual_of / block_visual_of), IconProperties, Quality, recipes, names, texts, every class
    (version constants only), the bench accessories, the Accessory Bag, the Omni accessory and the retired Night Vision (vanilla icons).
  - Build checks: the generator's ids = the build's ids, 2 px clear margin, 64 x 64 RGBA, premultiplied (no colour above alpha), 44
    distinct PNGs, no vanilla path overridden, every other item's icon still a vanilla file.
UNVERIFIED (in game only): how the icons look on a real slot (Legendary halo, alpha-110 edge pixels, premultiplied alpha handling).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.6.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.7.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.6"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.6"\n' in s and "AccKnow" in s and "OWN_ICON" not in s, "the source must be the generated 0.5.6 script"

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.6 - build script (derived from the generated build_skyyaccessories_0.5.5.py by tools/acc_0_5_6_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.6.py            -> SkyyAccessories/SkyyAccessories-0.5.6.jar
       python build_skyyaccessories_0.5.6.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.6.py             (bare JVM -Xverify:all: the 0.5.6 changes; test_skyyaccessories_0.5.5.py still
                                                         covers every class 0.5.6 leaves unchanged)
''', '''"""SkyyAccessories 0.5.7 - build script (derived from the generated build_skyyaccessories_0.5.6.py by tools/accessories_0_5_7_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.7.py            -> SkyyAccessories/SkyyAccessories-0.5.7.jar
       python build_skyyaccessories_0.5.7.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.7.py             (bare JVM -Xverify:all: every 0.5.6 check + the 0.5.7 icon checks)
0.5.7: OUR OWN ACCESSORY ICONS (Skyy 2026-10-07: "all of the items look beautiful. are they deployed in game?", "Amber works."; full
     notes in tools/accessories_0_5_7_patch.py): the build draws the 44 icons with tools/art/make_accessory_icons.py (our own art, at
     build time, nothing vanilla), ships them at Common/Icons/ItemsGenerated/SkyyAccessories_<Line>_<Rarity>.png and points every
     booster item's Icon at its own (40 line ids + 4 Lantern + the 20 hidden legacy ids at their tier). Art only: models, recipes,
     texts, classes and every other item unchanged.
''')
rep('VERSION = "0.5.6"\n', 'VERSION = "0.5.7"\n')

# ---------------------------------------------------------------------------------------------------------------- the icons
rep('''tal_count = 0
legacy_count = 0
ICONS = {}
''', '''# ---- 0.5.7 OUR OWN BOOSTER ICONS (Skyy 2026-10-07): drawn at BUILD time by the tracked generator tools/art/make_accessory_icons.py
# (pure Python, our own art, never opens Assets.zip, deterministic) - its make() + to_img() + skyyart.png_encode, the bytes its main()
# writes - shipped in the jar at Common/Icons/ItemsGenerated/SkyyAccessories_<Line>_<Rarity>.png. Every booster item (40 line ids,
# 4 Lantern ids, the 20 hidden legacy ids at their tier) points its Icon there; the 3D model stays the vanilla look (visual_of).
import importlib.util as _ilu
_ART = os.path.join(os.path.dirname(HERE), "tools", "art", "make_accessory_icons.py")
_spec = _ilu.spec_from_file_location("make_accessory_icons", _ART)
MAI = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(MAI)
import skyyart as _SA   # the generator's own PNG codec (tools/skyyart.py)
OWN_RARITY = [None] + [_r[0] for _r in MAI.RARITIES]
assert OWN_RARITY == [None, "Normal", "Unique", "Rare", "Legendary"], OWN_RARITY
assert sorted(_l[1] for _l in MAI.LINES) == sorted([_b[0] for _b in BOOSTERS] + [LAN_FAM]), [_l[1] for _l in MAI.LINES]
OWN_ICON = {}   # (family key, tier 1..4) -> the item's Icon path (relative to Common/, like vanilla)
OWN_PNG = {}    # the same key -> PNG bytes
for _name, _fam, _what, _fn in MAI.LINES:
    for _t in range(1, 5):
        _cur, _leg = MAI.item_ids(_fam, _t)
        if _fam == LAN_FAM:
            assert _cur == LAN_IDS[_t - 1] and _leg == [], (_cur, _leg)
        else:
            _b = BOOSTERS[[_x[0] for _x in BOOSTERS].index(_fam)]
            assert _cur == booster_id(_b, _t), ("0.5.7: the generator's id differs from the build's", _cur, booster_id(_b, _t))
            assert _leg == (["Skyy_Talisman_%s_%s" % (_fam, _w) for _w, _lt in LEGACY_WORDS if _lt == _t] if _b[9] == "word" else []), _leg
        _px = MAI.make(_fn, _t - 1)
        assert len(_px) == 64 and all(len(_row) == 64 for _row in _px), (_name, _t)
        assert all(_px[_y][_x][3] == 0 for _y in range(64) for _x in range(64)
                   if _x < MAI.MARGIN or _y < MAI.MARGIN or _x >= 64 - MAI.MARGIN or _y >= 64 - MAI.MARGIN), ("2 px clear margin", _name, _t)
        _png = _SA.png_encode(MAI.to_img(_px))
        _rel = "Icons/ItemsGenerated/SkyyAccessories_%s_%s.png" % (_name, OWN_RARITY[_t])
        assert "Common/" + _rel not in _COMMON, "0.5.7: our icon would override a vanilla file: " + _rel
        OWN_ICON[(_fam, _t)] = _rel
        OWN_PNG[(_fam, _t)] = _png
        files["Common/" + _rel] = _png
assert len(OWN_ICON) == 44 and len(set(OWN_ICON.values())) == 44 and len(set(OWN_PNG.values())) == 44, "0.5.7: 44 distinct icons"
print("own icons: %d drawn by tools/art/make_accessory_icons.py (%d bytes), shipped under Common/Icons/ItemsGenerated/" % (
    len(OWN_PNG), sum(len(_v) for _v in OWN_PNG.values())))
tal_count = 0
legacy_count = 0
ICONS = {}
''')
rep('''    assert len(set(icons[1:])) == 4, "0.5: two rarities of the %s line share an icon: %s" % (adm, icons)
    ICONS[adm] = icons
''', '''    assert len(set(icons[1:])) == 4, "0.5: two rarities of the %s line share an icon: %s" % (adm, icons)
    icons = [None] + [OWN_ICON[(fam, _t)] for _t in range(1, 5)]   # 0.5.7: our own icons (the vanilla ones above stay checked, unused)
    ICONS[adm] = icons
''')
rep('''    _node = item(_iid, icon_of(LAN_LOOKS[_t - 1]), QUAL_IDS[_t], _rin, WB_REQ, visual=_look)''',
    '''    _node = item(_iid, OWN_ICON[(LAN_FAM, _t)], QUAL_IDS[_t], _rin, WB_REQ, visual=_look)   # 0.5.7: our own icon''')
rep('''        assert n["Icon"] == icon_of(LAN_LOOKS[t - 1]) and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)''',
    '''        assert n["Icon"] == OWN_ICON[(LAN_FAM, t)] and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)   # 0.5.7''')

# ---------------------------------------------------------------------------------------------------------------- the icon check
rep('''

_ladder_audit()
''', '''

_ladder_audit()


def _own_icon_checks():
    """0.5.7 build check: every booster id (40 line + 4 Lantern + 20 hidden legacy) shows our own icon of its line and tier, the PNG is in
    the jar at Common/<Icon>, 64 x 64 RGBA, premultiplied; 44 distinct icons; every other item keeps a vanilla icon (or the bag's)"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    want = {}
    for li, b in enumerate(BOOSTERS):
        for t in range(1, 5):
            want[LINE_IDS[li * 4 + t - 1]] = OWN_ICON[(b[0], t)]
        if b[9] == "word":
            for w, t in LEGACY_WORDS:
                want["Skyy_Talisman_%s_%s" % (b[0], w)] = OWN_ICON[(b[0], t)]
    for t in range(1, 5):
        want[LAN_IDS[t - 1]] = OWN_ICON[(LAN_FAM, t)]
    assert len(want) == 64 and len(set(want.values())) == 44, (len(want), len(set(want.values())))
    for iid, rel in want.items():
        assert items[iid]["Icon"] == rel, (iid, items[iid]["Icon"], rel)
        png = files["Common/" + rel]
        img = _SA.png_decode(png)
        assert (img.w, img.h) == (64, 64) and png[24] == 8 and png[25] == 6, ("64x64 RGBA8", rel)
        px = img.px
        assert all(px[k] <= px[k - (k % 4) + 3] for k in range(len(px)) if k % 4 != 3), ("premultiplied", rel)
    own = set("Common/" + r for r in OWN_ICON.values())
    assert sorted(p for p in files if p.startswith("Common/Icons/ItemsGenerated/")) == sorted(own), "0.5.7: exactly our 44 icons in ItemsGenerated"
    for iid, n in items.items():
        if iid not in want:
            assert "Common/" + n["Icon"] in _COMMON and not n["Icon"].startswith("Icons/ItemsGenerated/SkyyAccessories_"), (iid, n["Icon"])
    print("own icon audit: %d booster ids (40 line + 4 Lantern + 20 hidden legacy) -> %d distinct own 64x64 icons; %d other items keep "
          "their vanilla icon" % (len(want), len(set(want.values())), len(items) - len(want)))


_own_icon_checks()
''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("OWN_ICON = {}") < s.index("ICONS = {}") < s.index("OWN_ICON[(fam, _t)]") < s.index("OWN_ICON[(LAN_FAM, _t)]")
assert s.index("files = {}") < s.index("OWN_ICON = {}") and s.index("_COMMON = set(") < s.index("OWN_ICON = {}")
assert s.index("def booster_id(") < s.index("OWN_ICON = {}")
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.6 - build script (derived from the generated build_skyyaccessories_0.5.5.py by tools/acc_0_5_6_patch.py - edit',
    "the patch, not this file)",
    "Run:   python build_skyyaccessories_0.5.6.py            -> SkyyAccessories/SkyyAccessories-0.5.6.jar",
    "       python build_skyyaccessories_0.5.6.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world",
    "Test:  python test_skyyaccessories_0.5.6.py             (bare JVM -Xverify:all: the 0.5.6 changes; test_skyyaccessories_0.5.5.py still",
    "                                                         covers every class 0.5.6 leaves unchanged)",
    'VERSION = "0.5.6"',
    '    _node = item(_iid, icon_of(LAN_LOOKS[_t - 1]), QUAL_IDS[_t], _rin, WB_REQ, visual=_look)',
    '        assert n["Icon"] == icon_of(LAN_LOOKS[t - 1]) and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.6 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.6 had %d)" % (s.count(LF), OLD.count(LF)))
