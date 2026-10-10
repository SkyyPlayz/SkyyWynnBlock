"""Derive SkyyAccessories/build_skyyaccessories_0.5.11.py from the GENERATED 0.5.10 script (build_skyyaccessories_0.5.10.py = the
tools/deploy_set.py SET pin, written by tools/accessories_0_5_10_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.10 script
stays untouched - never re-run accessories_0_5_10_patch.py on top of this).
Run:  python tools/accessories_0_5_11_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.11.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.11.py   (bare JVM -Xverify:all: class compare 0.5.10 -> 0.5.11 = no class change,
      the jar diff = exactly the 4 Lantern JSONs (Texture only) + 4 new textures + manifest, the textures = the vanilla pixels, start twice on
      a live copy; JVM 2: the engine's own asset validators on the whole jar)

0.5.11 = THE LANTERN ITEM TEXTURES (a log-scan fix; Skyy: "after every play session scan server AND client logs (dev error badge = client
WARNs), fix ours"). Every client log since 0.5.4 has 4 lines:
    Cannot use Blocks/Decorative_Sets/{Village,Kweebec,Desert,Temple_Light}/Lantern_Texture.png as texture for item
    Skyy_Talisman_Lantern_{Common,Uncommon,Rare,Epic}
The Lantern items (0.5.4) copied the vanilla lantern BLOCK's look: its block model + its BLOCK texture. The client refuses a texture under
Blocks/ for an item (the block textures live in the block atlas), so the held / dropped Lantern had no usable texture.
  - Fix: at BUILD time the build reads each vanilla lantern texture from Assets.zip (read-only) and ships the same bytes in the jar under
    OUR item path Common/Items/SkyyAccessories/SkyyAccessories_Lantern_<Normal|Unique|Rare|Legendary>_Texture.png (the folder the
    Accessory Bag's own texture already loads from without a warning since 0.5.8). The item's "Texture" points there. Nothing vanilla is
    committed (the PNGs exist only in the built jar) and no vanilla path is overridden (asserted: our paths are not in Assets.zip).
  - The model stays the vanilla lantern blockymodel (the client never complained about the model; a model carries no texture path) and the
    UVs are unchanged because the pixels and the size are byte-identical.
  - Build guard: no item JSON of the jar may point Texture at Blocks/ (the next block-look item fails the build instead of the client log).
  - Note: the task text said "the way 0.5.x fixed the Crystal_Fragment talismans"; there was no such SkyyAccessories change - the ~40
    Crystal_Fragment lines of 2026-10-09 were the texture ATLAS OVERFLOW that went away with The Armory off (docs/log 2026-10-09 07:45).
    Crystal_Fragment_Textures sit under Resources/ (item-usable) and never needed a fix. This round copies the Accessory Bag's pattern.
No class changes (Java untouched; only VERSION constants). Config, saves, bridge keys: unchanged.
UNVERIFIED (in game only): the client log has no "Cannot use ... Skyy_Talisman_Lantern_*" line and the held / dropped Lantern shows the
vanilla lantern texture (the bare JVM has no client renderer).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.10.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.11.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.10"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.10"\n' in s and "public static int helmetTier" in s and "LAN_TEX_REL" not in s, "the source must be the generated 0.5.10 script"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.10 - build script (derived from the generated build_skyyaccessories_0.5.9.py by tools/accessories_0_5_10_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.10.py            -> SkyyAccessories/SkyyAccessories-0.5.10.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.10.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.10.py             (bare JVM -Xverify:all: class compare 0.5.9 -> 0.5.10, the helmet light on a real ECS
       store, Lantern-only traces = 0.5.9, config, start twice on a live copy)
''', '''"""SkyyAccessories 0.5.11 - build script (derived from the generated build_skyyaccessories_0.5.10.py by tools/accessories_0_5_11_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.11.py            -> SkyyAccessories/SkyyAccessories-0.5.11.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.11.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.11.py             (bare JVM -Xverify:all: class compare 0.5.10 -> 0.5.11 = no class change, the jar
       diff = the 4 Lantern textures, start twice on a live copy; JVM 2: the engine asset validators)
0.5.11: THE LANTERN ITEM TEXTURES (client log "Cannot use Blocks/Decorative_Sets/<set>/Lantern_Texture.png as texture for item
     Skyy_Talisman_Lantern_*" x4; full notes in tools/accessories_0_5_11_patch.py): the build copies each vanilla lantern texture from
     Assets.zip into the jar at Common/Items/SkyyAccessories/SkyyAccessories_Lantern_<Rarity>_Texture.png (an item path, never committed,
     no vanilla path overridden) and the Lantern items point there; same model, same pixels. No item texture under Blocks/ (build guard).
''')
rep('VERSION = "0.5.10"\n', 'VERSION = "0.5.11"\n')

# ---------------------------------------------------------------------------------------------------------------- the textures
rep('''    _look = block_visual_of(LAN_LOOKS[_t - 1])
''', '''    _look = block_visual_of(LAN_LOOKS[_t - 1])
    _look["Texture"] = lan_item_texture(_t, _look["Texture"])   # 0.5.11: an item path in OUR jar (the client refuses Blocks/ textures for items)
''')
rep('''LAN_LANG = []
for _t in range(1, 5):
''', '''# 0.5.11 THE LANTERN ITEM TEXTURES (tools/accessories_0_5_11_patch.py): the client logs "Cannot use Blocks/... as texture for item" and
# drops the texture of any item whose Texture is a BLOCK texture. The vanilla lantern texture's bytes (Assets.zip, read at build time,
# never committed) ship under our item folder - the one the Accessory Bag's texture loads from - so the model's UVs see the same pixels.
LAN_TEX_REL = {}   # rarity 1..4 -> (our Common-relative path, the vanilla Common-relative source path)


def lan_item_texture(t, vanilla_rel):
    """0.5.11: copy Common/<vanilla_rel> (a vanilla lantern block texture) into the jar at our item path for rarity t; return that path"""
    assert vanilla_rel.startswith("Blocks/") and vanilla_rel.endswith(".png"), vanilla_rel
    rel = "Items/SkyyAccessories/SkyyAccessories_Lantern_%s_Texture.png" % DISPLAY[t]
    assert "Common/" + rel not in _COMMON, "0.5.11: our Lantern texture would override a vanilla file: " + rel
    assert "Common/" + rel not in files, "0.5.11: two Lanterns share a texture path: " + rel
    png = _ASSETS.read("Common/" + vanilla_rel)
    assert png[:8] == b"\\x89PNG\\r\\n\\x1a\\n", vanilla_rel
    files["Common/" + rel] = png
    LAN_TEX_REL[t] = (rel, vanilla_rel)
    return rel


LAN_LANG = []
for _t in range(1, 5):
''')


def _lan_checks_text():
    return '''

def _item_texture_checks():
    """0.5.11 build check: no item of this jar uses a BLOCK texture (the client refuses it: "Cannot use Blocks/... as texture for item");
    the four Lantern items use our copies - each the vanilla lantern texture byte for byte, at our own item path, the same model as 0.5.10"""
    import struct as _st
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    bad = sorted(i for i, n in items.items() if str(n.get("Texture", "")).startswith("Blocks/"))
    assert not bad, "0.5.11: items with a block texture (the client refuses them): %s" % bad
    assert sorted(LAN_TEX_REL) == [1, 2, 3, 4] and len(set(v[0] for v in LAN_TEX_REL.values())) == 4
    for t, i in enumerate(LAN_IDS, 1):
        n = items[i]
        rel, van = LAN_TEX_REL[t]
        bt = json.loads(_ASSETS.read(_ITEMS[LAN_LOOKS[t - 1]]).decode("utf-8-sig"))["BlockType"]
        assert n["Texture"] == rel and n["Model"] == bt["CustomModel"] and van == bt["CustomModelTexture"][0]["Texture"], (i, n["Texture"], n["Model"])
        assert rel.startswith("Items/SkyyAccessories/") and ("Common/" + rel) not in _COMMON, rel
        assert files["Common/" + rel] == _ASSETS.read("Common/" + van), "0.5.11: %s is not the vanilla pixels of %s" % (rel, van)
        w, h = _st.unpack(">II", files["Common/" + rel][16:24])
        print("lantern texture: %s <- %s (%d x %d, %d bytes)" % (rel, van, w, h, len(files["Common/" + rel])))


_item_texture_checks()
'''


rep('''

_lantern_asset_checks()
''', '''

_lantern_asset_checks()
''' + _lan_checks_text())

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s.index("def lan_item_texture") < s.index("lan_item_texture(_t, _look") < s.index("_item_texture_checks()")
assert s.index("_lantern_asset_checks()\n\n\ndef _item_texture_checks") > 0
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.10 - build script (derived from the generated build_skyyaccessories_0.5.9.py by tools/accessories_0_5_10_patch.py -',
    "Run:   python build_skyyaccessories_0.5.10.py            -> SkyyAccessories/SkyyAccessories-0.5.10.jar   (deploys go through tools/deploy_set.py --yes)",
    "       python build_skyyaccessories_0.5.10.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)",
    "Test:  python test_skyyaccessories_0.5.10.py             (bare JVM -Xverify:all: class compare 0.5.9 -> 0.5.10, the helmet light on a real ECS",
    "       store, Lantern-only traces = 0.5.9, config, start twice on a live copy)",
    'VERSION = "0.5.10"',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.10 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.10 had %d)" % (s.count(LF), OLD.count(LF)))
