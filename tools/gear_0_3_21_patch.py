"""Derive SkyyGear/build_skyygear_0.3.21.py from the LIVE 0.3.20 (build_skyygear_0.3.20.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_20_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_21_patch.py      then      python SkyyGear/build_skyygear_0.3.21.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.21.py   (--static runs without jars / Assets.zip)
The build reads Quirk's textures from the PRIVATE art folder (..\\SkyWynn-PRIVATE-art\\mining-armor, or env SKYWYNN_PRIVATE_ART = the
SkyWynn-PRIVATE-art folder) and stops with a clear message when it is missing. Nothing from that folder is ever copied into this repo.

0.3.21 (2026-10-17) = ZONE MINING SETS + ARMOR WEIGHT IN THE FLAVOUR TEXT.
Skyy's words: "cobbs que in local resume" (LOCAL-RESUME.md "Local build queue" item 1: "MINING ARMOR Z2-Z5 ... Quirk's approved sets (Skyy
2026-10-17): Z2 Lead/Dusk, Z3 Chromium/Azurvane, Z4 Slag/Cinder, Z5 Titanium/Lumen ... each set retextures that zone's vanilla base armor.
Ship our textures + item defs that point at the vanilla models."); docs/answered/gear.md 2026-10-17 ZONE TIERS CORRECTION: "the metals you
mine and their alloys will be used for mining sets, and upgrading tools. not combat gear." And (main session, same version): "make sure the
flavor text lists if the armor is robe/ cloth. light or heavy armor".
  1. EIGHT NEW MINING SETS (GearMine tiers 7-14, appended after the 7 vanilla ones so every saved index stays): Lead + Dusk (Zone 2, the
     Thorium armor model), Chromium + Azurvane (Zone 3, Cobalt), Slag + Cinder (Zone 4, Adamantite), Titanium + Lumen (Zone 5, Mithril).
     Ids Armor_Mining_<Metal>_<Head|Chest|Hands|Legs> (Armor_Lead_* belongs to TerrariaToolsWeapons; the slot stays the last id word -
     GearSmith.setKey / the rebirth read it there). Item defs = the zone's vanilla piece (Armor, durability, sounds, icon view, the vanilla
     MODEL BY PATH) + Quirk's texture + an icon rendered from that model and texture at build time; recipe = the vanilla piece's recipe with
     its bar swapped 1:1 for the zone bar (Ingredient_Bar_<Metal>_SkyWynn, SkyyWorldGen 0.7.3), same bench / tier / other inputs.
     Ladder order (sort key everywhere, GearMine.RANK): Copper, Iron, Thorium, Lead, Dusk, Cobalt, Chromium, Azurvane, Adamantite, Slag,
     Cinder, Mithril, Titanium, Lumen, Onyxium.
  2. NUMBERS (extrapolated between the neighbouring vanilla sets - research/cloud/Mining-Armor-Spec.md 2.3 / 2.4 shape; per piece Head
     Chest Legs Hands; full set = pieces + mfort):
        set       band   Fortune/piece    Wisdom %/piece   lamp  full-set bonus                    full Fortune  Wisdom
        Lead      22-27  .4 .5 .4 .2      .2 .2 .2 .1      2     mfort+3   mpow+6                  4.5          0.7
        Dusk      24-28  .4 .6 .4 .3      .4 .4 .4 .2      3     mfort+3.5 mpow+7                  5.2          1.4
        Chromium  28-34  .5 .8 .5 .3      .7 .9 .7 .4      3     mfort+4.6 mpow+8.5                6.7          2.7
        Azurvane  31-38  .6 .8 .6 .4      .8 1.2 .8 .5     3     mfort+5.1 mpow+9                  7.5          3.3
        Slag      37-42  .8 1.1 .8 .5     1.1 1.6 1.1 .7   3     mfort+6.1 mpow+10.5 spd+6         9.3          4.5
        Cinder    39-43  .9 1.2 .8 .5     1.3 1.8 1.3 .8   4     mfort+6.9 mpow+11 spd+7           10.3         5.2
        Titanium  43-49  1.1 1.5 1.0 .6   1.7 2.3 1.6 1.0  4     mfort+8.3 mpow+13 spd+9           12.5         6.6
        Lumen     46-49  1.2 1.6 1.1 .7   1.8 2.6 1.8 1.1  4     mfort+9.1 mpow+14 spd+9           13.7         7.3
     (vanilla neighbours unchanged: Thorium 3.8 / 0, Cobalt 6.0 / 2, Adamantite 8.3 / 4, Mithril 11.3 / 6, Onyxium 15 / 8; caps 15 / 10).
     Bands = Skyy's band rule (start .. next start + 3; never above 49), the start inside the tier tag's level range (T4 Lead / Dusk ...
     T7 Titanium / Lumen = tools/tier_tags.py, the ingots' tags). Every number is a Server Setup row: garmor.mining.<tier> (Mining armor by
     tier), set.mining_<tier> (Armor sets), garmor.zoneBands (NEW scalar, "Zone mining armor levels"). Everything else = the 0.2.15 / 0.3.4
     Mining armor rules unchanged (Mining level gate, lines + bonus only with a pickaxe / shovel / multitool in hand, levels with Mining
     inside the band, Sigils allowed, rebirth -> Copper of the slot, never in bags / random drops).
  3. ONE-TIME UPDATE migrate0321 (PROJECT-RULES 4, the migrate0215 shape): pure ADDITION of a marked block at the END of config.properties
     (garmor.zoneBands, the 8 garmor.mining rows, the 8 set.mining_* rows) - only the keys the file lacks (kept + noted), verified History
     copy first, atomic ISO-8859-1 write, run-once marker, every other byte and line ending kept. A fresh file carries the block (before
     the 0.2.14 block). A set row deleted later never comes back by itself: one INFO line per start names it with its default.
  4. /smithing > Smithing > Mining armor: the set cards sort by the ladder (GearMine.rank) - Onyxium last, Lumen before it (Skyy 2026-10-16
     "sort everything by tier in all shops and crafting."); other categories unchanged (band start, then name).
  5. NOT CHANGED ON PURPOSE: garmor.ladders (the Anvil tier-up ladder Copper > Iron > Thorium > Cobalt > Adamantite) - the zone sets are
     crafted, not tiered into (no Enchanted alloy items exist; question for Skyy). Quirk's .blockymodel files: never shipped (the build
     compares them with the vanilla models and prints the differences; 5 of 32 are vanilla with a few stretch / visibility tweaks).
  6. ARMOR WEIGHT IN THE FLAVOUR TEXT: every COMBAT armor piece (vanilla, ours, pack) starts its flavour slot with its tier tag + weight:
     "T1 Crude Heavy - <its description>", robes "Cloth", leather "Light". Weight = GearView.weightOf (the rule GearSmith.armorType used:
     the pack table weight first, else the vanilla sound set Cloth / Leather / Heavy) - GearSmith.armorType now CALLS it, so the class armor
     rules, the Smithing filter and this text read one source (the bag pools use the same rule at build time). Tier = the pack table tag,
     else tools/tier_tags.py tier_for_level on the item's level band start (Onyxium ids T8). Rendered in our tooltip path only (no lang
     key written, no pack lang touched). Mining / gathering sets keep their own text (their lang descriptions carry "T4 Lead - ...").
  7. STARTER QUEST GEAR (main session for Quests 0.4.1; Skyy: the starter skeleton quest gives a full class armor set + the class's secondary
     weapon as unidentified bags "so you can use both in the tutorial"): bag types - vanilla Weapon_Staff_Bo_* open from the Weapon_Bo bag
     (never a Mage Staff bag); SkyyArmory's class weapon ladders join the bag pool by id (43 rows: Weapon_Bo_<7 metals>,
     Weapon_Fist_Gauntlets_<7>, Weapon_Fist_Wraps_<5 cloths> = the NEW bag type Weapon_Fist "Fist Weapon", Weapon_Kunai_Crude + <7>,
     Weapon_Spellbook_<7>, Weapon_Crossbow_Copper_Wynn / _Onyxium_Wynn, Weapon_GreatShield_<7> = the NEW bag type Weapon_GreatShield
     "Great Shield", the Spellblade's secondary); a row only counts while its item is loaded (no SkyyArmory = no change).
     Stored bags keep their type KEY, so the new type moves nothing saved.
  8 + 9. Lv 1 STARTS (pure addition rows in the migrate0321 block, the Armor_Copper rule LOCKED 2026-10-01): level.material.Armor_Leather_Soft
     =1,12 (Light), Armor_Cloth_Wool=1,12 (Cloth), Weapon_Spellbook_Copper=1,18, Weapon_Crossbow_Copper=1,18 (Copper_Wynn). Kunai_Crude is
     already 1-13 (Crude). Heavy has Copper armor at 1 already.
  10. FREE IDENTIFY FOR QUEST BAGS: GearUnid.cost = 0 for a bag whose document src is "quest" while unid.questFree (NEW Server Setup row,
     Gear -> Loot, default ON; absent line = the default). Re-identify still costs.
  11. CRITIC FIXES: the tooltip signature carries flavTag (old items re-render once with their weight); Smithing card titles "Lead Set" (not
     "Mining Lead Set"); the manifest names the soft need on SkyyWorldGen 0.7.3+ (the zone set recipes use its bars).
Commands: none new. Config: + garmor.zoneBands, + 8 garmor.mining.<tier>, + 8 set.mining_<tier>, + 4 level.material starter rows (migrate0321),
+ unid.questFree. Classes: none new (GearMine, GearCfg, GearLevel, GearSmith, GearView, GearPool, GearUnid + the plugin's setup call change).
SAVED DATA: new documents of the 32 ids (set field mining_<metal>); nothing existing is rewritten.
ROLLBACK 0.3.21 -> 0.3.20: the 32 items disappear (unknown items in inventories - treat as lost; nobody has them before this deploy);
config.properties keeps the 17 new rows (0.3.20 ignores garmor.zoneBands / the garmor.mining rows it does not know; the 8 set.mining_*
rows become plain sets nobody can complete; edit out their spd+N words first if Skyy wants zero side effects). Rolling forward again re-reads
everything.
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.20.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.21.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.20"' in s and "GENERATED by tools/gear_0_3_20_patch.py" in s, "not the generated 0.3.20 script"
assert "Armor_Mining_" not in s and "migrate0321" not in s and "weightOf" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def method(anchor_start):
    """the full text of one M(...) block starting at anchor_start (up to its closing triple quote + paren)"""
    i = s.index(anchor_start)
    j = s.index('}""")', i)
    return s[i:j + len('}""")')]


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.20":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.20" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.21 (2026-10-17)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.20 - build script (javassist via jpype). GENERATED by tools/gear_0_3_20_patch.py from the LIVE 0.3.19 (itself GENERATED by
tools/gear_0_3_19_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.20.py -> SkyyGear/SkyyGear-0.3.20.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.20.py

''', '''"""SkyyGear 0.3.21 - build script (javassist via jpype). GENERATED by tools/gear_0_3_21_patch.py from the LIVE 0.3.20 (itself GENERATED by
tools/gear_0_3_20_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.21.py -> SkyyGear/SkyyGear-0.3.21.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.21.py. Needs Quirk's private textures (../SkyWynn-PRIVATE-art/mining-armor).

''' + NOTE + '''
--- 0.3.20 notes ---
''')
rep('VERSION = "0.3.20"\n', 'VERSION = "0.3.21"\n')

# ================================================================================================================ 1: the data + the items (after 0.3.6)
ZM_PY = r'''# ================================================================= 0.3.21 ZONE MINING SETS (tools/gear_0_3_21_patch.py): Quirk's approved sets (Skyy 2026-10-17)
# - each zone's metal + alloy retextures that zone's vanilla base armor. GearMine tiers 7-14 (appended: the 7 vanilla tiers keep their index).
# ZM_ROWS: tier key, metal word, the vanilla base metal, Quirk's zone folder, Fortune / Wisdom % per piece (ROW order Head Chest Legs Hands),
# helmet lamp, the full-set bonus, the level band
ZM_ROWS = [("lead", "Lead", "Thorium", "Z2_Thorium", "0.4 0.5 0.4 0.2", "0.2 0.2 0.2 0.1", 2, "mfort+3 mpow+6", (22, 27)),
           ("dusk", "Dusk", "Thorium", "Z2_Thorium", "0.4 0.6 0.4 0.3", "0.4 0.4 0.4 0.2", 3, "mfort+3.5 mpow+7", (24, 28)),
           ("chromium", "Chromium", "Cobalt", "Z3_Cobalt", "0.5 0.8 0.5 0.3", "0.7 0.9 0.7 0.4", 3, "mfort+4.6 mpow+8.5", (28, 34)),
           ("azurvane", "Azurvane", "Cobalt", "Z3_Cobalt", "0.6 0.8 0.6 0.4", "0.8 1.2 0.8 0.5", 3, "mfort+5.1 mpow+9", (31, 38)),
           ("slag", "Slag", "Adamantite", "Z4_Adamantite", "0.8 1.1 0.8 0.5", "1.1 1.6 1.1 0.7", 3, "mfort+6.1 mpow+10.5 spd+6", (37, 42)),
           ("cinder", "Cinder", "Adamantite", "Z4_Adamantite", "0.9 1.2 0.8 0.5", "1.3 1.8 1.3 0.8", 4, "mfort+6.9 mpow+11 spd+7", (39, 43)),
           ("titanium", "Titanium", "Mithril", "Z5_Mithril", "1.1 1.5 1.0 0.6", "1.7 2.3 1.6 1.0", 4, "mfort+8.3 mpow+13 spd+9", (43, 49)),
           ("lumen", "Lumen", "Mithril", "Z5_Mithril", "1.2 1.6 1.1 0.7", "1.8 2.6 1.8 1.1", 4, "mfort+9.1 mpow+14 spd+9", (46, 49))]
ZM_TIERS = [_r[1] for _r in ZM_ROWS]
ZM_BASE = len(MINE_TIERS)
ZM_IDS = ["Armor_Mining_%s_%s" % (_t, _s) for _t in ZM_TIERS for _s in MINE_SLOTS]
ZM_LADDER = ["Copper", "Iron", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril", "Titanium",
             "Lumen", "Onyxium"]
MINE_ALL_TIERS = MINE_TIERS + ZM_TIERS
MINE_RANK = [ZM_LADDER.index(_t) for _t in MINE_ALL_TIERS]
assert sorted(ZM_LADDER) == sorted(MINE_ALL_TIERS) and ZM_BASE == 7 and len(ZM_IDS) == 32 and len(set(ZM_IDS)) == 32
assert not set(ZM_IDS) & AZ_ITEMS, "a zone mining armor id is a vanilla item"
assert all(TT.tag_for(_i) == "T%d %s" % (TT.tier("Ingredient_Bar_%s_SkyWynn" % _i.split("_")[2]), _i.split("_")[2]) and TT.owner(_i) == "SkyyGear"
           for _i in ZM_IDS), "tools/tier_tags.py: the zone mining armor rows (the ingot's tier + word)"
ZM_F = [_x for _r in ZM_ROWS for _x in _slot_order(_r[4])]
ZM_W = [_x for _r in ZM_ROWS for _x in _slot_order(_r[5])]
ZM_L = [_r[6] for _r in ZM_ROWS]
ZM_BANDS_DEF = ",".join("%d-%d" % _r[8] for _r in ZM_ROWS)
assert ZM_BANDS_DEF == "22-27,24-28,28-34,31-38,37-42,39-43,43-49,46-49"
for _r in ZM_ROWS:          # the band start sits in the tier tag's level range (tier_for_level) and the band rule (start .. next start + 3, <= 49)
    assert TT.tier_for_level(_r[8][0]) == TT.tier("Ingredient_Bar_%s_SkyWynn" % _r[1]) and _r[8][1] <= VANILLA_TOP, _r
# the whole ladder: per piece Fortune / Wisdom and the full-set Fortune / Wisdom / Mining Power never go down, all under the caps
_zall = dict((_r[0].capitalize(), (_slot_order(_r[1]), _slot_order(_r[2]), _mine_words(_r[4]))) for _r in MINE_ROWS)
_zall.update(dict((_r[1], (_slot_order(_r[4]), _slot_order(_r[5]), _mine_words(_r[7]))) for _r in ZM_ROWS))
_zprev = None
for _t in ZM_LADDER:
    _f, _w, _b = _zall[_t]
    _cur = (_f, _w, round(sum(_f) + _b.get("mfort", 0), 2), round(sum(_w) + _b.get("mwis", 0), 2), _b.get("mpow", 0), _b.get("spd", 0))
    assert set(_b) <= {"mfort", "mwis", "mpow", "spd"} and _cur[2] <= MINE_FCAP and _cur[3] <= MINE_WCAP, _t
    assert float(_b.get("spd", 0)) == int(_b.get("spd", 0)), "spd is whole points: " + _t
    if _zprev is not None:
        assert all(a >= b for a, b in zip(_cur[0], _zprev[0])) and all(a >= b for a, b in zip(_cur[1], _zprev[1])) and all(
            _cur[k] >= _zprev[k] for k in (2, 3, 4, 5)), "the mining ladder goes down at %s" % _t
    _zprev = _cur
ZM_FULL = [round(sum(_slot_order(_r[4])) + _mine_words(_r[7])["mfort"], 2) for _r in ZM_ROWS]
assert ZM_FULL == [4.5, 5.2, 6.7, 7.5, 9.3, 10.3, 12.5, 13.7], ZM_FULL
# THE ART: Quirk's textures from the PRIVATE folder (never in this repo); the model = the vanilla one BY PATH
_zpa = os.environ.get("SKYWYNN_PRIVATE_ART") or os.path.join(os.path.dirname(os.path.dirname(HERE)), "SkyWynn-PRIVATE-art")
ZM_ART = os.path.join(_zpa, "mining-armor")
if not os.path.isdir(ZM_ART):
    raise SystemExit("SkyyGear 0.3.21 needs Quirk's private mining armor textures: %s is missing. Put the SkyWynn-PRIVATE-art folder next to "
                     "the project (or set SKYWYNN_PRIVATE_ART to it) - the textures are never committed to the public repo." % ZM_ART)


def _zm_png(path):
    if not os.path.isfile(path):
        raise SystemExit("SkyyGear 0.3.21: Quirk's texture %s is missing (private art folder %s)" % (path, ZM_ART))
    return open(path, "rb").read()


def _zm_jdiff(a, b, path="", out=None):
    out = [] if out is None else out
    if type(a) != type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append(path)
    elif isinstance(a, dict):
        for _k in sorted(set(a) | set(b)):
            if _k not in a or _k not in b:
                out.append(path + "/" + _k)
            else:
                _zm_jdiff(a[_k], b[_k], path + "/" + _k, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(path)
        for _k, (_x, _y) in enumerate(zip(a, b)):
            _zm_jdiff(_x, _y, "%s[%d]" % (path, _k), out)
    elif a != b:
        out.append(path)
    return out


def _zm_shift(img, dx, dy):
    o = SA.Img(img.w, img.h)
    for _y in range(img.h):
        for _x in range(img.w):
            _sx, _sy = _x - dx, _y - dy
            if 0 <= _sx < img.w and 0 <= _sy < img.h:
                o.px[(_y * img.w + _x) * 4:(_y * img.w + _x) * 4 + 4] = img.px[(_sy * img.w + _sx) * 4:(_sy * img.w + _sx) * 4 + 4]
    return o


def _zm_adiff(a, b):
    return sum(abs(a.px[_i * 4 + 3] - b.px[_i * 4 + 3]) for _i in range(a.w * a.h))


ZM_ITEMS, ZM_FILES, ZM_LANG, ZM_MODEL_NOTES = {}, {}, [], []
_ga2name = dict((_l.split(" = ", 1)[0], _l.split(" = ", 1)[1].strip()) for _l in _ga2lang.splitlines() if " = " in _l)
_zshift = {}
for _k, _id in enumerate(ZM_IDS):
    _r = ZM_ROWS[_k // 4]
    _sl = MINE_SLOTS[_k % 4]
    _metal, _base = _r[1], _r[2]
    _vid = "Armor_%s_%s" % (_base, _sl)
    _bj = _ga2j("Armor_Iron_%s" % _sl)                     # the parent of every vanilla armor piece (no Parent of its own)
    assert "Parent" not in _bj
    _vj = _ga2j(_vid)
    for _x in ("Recipe", "$Comment", "Tags", "ItemLevel", "Parent"):
        _bj.pop(_x, None)
    for _x in ("Quality", "IconProperties", "Model", "Armor", "MaxDurability", "DurabilityLossOnHit", "ItemSoundSetId"):
        if _x in _vj:
            _bj[_x] = json.loads(json.dumps(_vj[_x]))
    assert _bj["Armor"]["ArmorSlot"] == _sl and _bj["Model"] == "Items/Armors/%s/%s.blockymodel" % (_base, _sl), _vid
    _vtex = AZ.read("Common/" + _vj["Texture"])
    _qdir = os.path.join(ZM_ART, _r[3], _metal)
    _qtex = _zm_png(os.path.join(_qdir, "%s_Texture.png" % _sl))
    _qi, _vi = SA.png_decode(_qtex), SA.png_decode(_vtex)
    assert (_qi.w, _qi.h) == (_vi.w, _vi.h), "Quirk's %s %s texture is %dx%d, the vanilla UV layout is %dx%d" % (_metal, _sl, _qi.w, _qi.h, _vi.w, _vi.h)
    assert all((_qi.px[_i * 4 + 3] > 0) == (_vi.px[_i * 4 + 3] > 0) for _i in range(_qi.w * _qi.h)), \
        "Quirk's %s %s texture does not cover the vanilla UV layout exactly (the vanilla model would show holes / stray texels)" % (_metal, _sl)
    _qm = os.path.join(_qdir, "%s.blockymodel" % _sl)
    if os.path.isfile(_qm):          # read only: compared, never shipped
        _dd = _zm_jdiff(json.loads(open(_qm, "rb").read().decode("utf-8-sig")), json.loads(AZ.read("Common/" + _vj["Model"]).decode("utf-8-sig")))
        if _dd:
            ZM_MODEL_NOTES.append("%s %s: %d values differ from vanilla %s (e.g. %s) - the VANILLA model is used" % (_metal, _sl, len(_dd), _vj["Model"], _dd[0]))
    _tex = "Items/SkyyGear/MiningArmor/%s/%s_Texture.png" % (_metal, _sl)
    _ico = "Icons/ItemsGenerated/%s.png" % _id
    ZM_FILES["Common/" + _tex] = _qtex
    _props = _bj.get("IconProperties")
    _vmodel = AZ.read("Common/" + _vj["Model"])
    if _vid not in _zshift:          # the render's pixel offset against the vanilla icon (some vanilla icons sit a pixel or two off)
        _vr = SA.render_icon(_vmodel, _vtex, _props, as_img=True)
        _vic = SA.png_decode(AZ.read("Common/" + _vj["Icon"]))
        _zshift[_vid] = min(((_dx, _dy) for _dx in range(-3, 4) for _dy in range(-3, 4)), key=lambda _d: (_zm_adiff(_zm_shift(_vr, _d[0], _d[1]), _vic), abs(_d[0]) + abs(_d[1]), _d))
    ZM_FILES["Common/" + _ico] = SA.png_encode(_zm_shift(SA.render_icon(_vmodel, _qtex, _props, as_img=True), *_zshift[_vid]))
    _bj["TranslationProperties"] = {"Name": "server.items.%s.name" % _id, "Description": "server.items.%s.description" % _id}
    _bj["ItemLevel"] = _r[8][0]
    _bj["Texture"] = _tex
    _bj["Icon"] = _ico
    _bj["Tags"] = {"Type": ["Armor"], "Family": [_metal]}
    _vr0 = _vj["Recipe"]
    _bar = "Ingredient_Bar_%s" % _base
    assert [_i["ItemId"] for _i in _vr0["Input"]].count(_bar) == 1, _vid
    _bj["Recipe"] = {"Input": [{"ItemId": ("Ingredient_Bar_%s_SkyWynn" % _metal) if _i["ItemId"] == _bar else _i["ItemId"], "Quantity": _i["Quantity"]}
                               for _i in _vr0["Input"]],
                     "BenchRequirement": json.loads(json.dumps(_vr0["BenchRequirement"])), "KnowledgeRequired": False,
                     "TimeSeconds": _vr0.get("TimeSeconds", 3)}
    ZM_ITEMS["Server/Item/Items/SkyyGear/MiningArmor/%s.json" % _id] = json.dumps(_bj, indent=2)
    _word = _ga2name["items.%s.name" % _vid].split(" ")[-1]
    ZM_LANG.append("items.%s.name = %s %s" % (_id, _metal, _word))
    ZM_LANG.append("items.%s.description = %s" % (_id, TT.described(_id, "%s Mining Set - mining armor from %s bars. Needs your Mining level; its "
                                                                          "mining lines work with a pickaxe or shovel in hand." % (_metal, _metal))))
for _k in list(ZM_FILES) + list(ZM_ITEMS):
    assert _k not in AZ_NAMES and _k not in EXTRA, "a zone mining armor file would shadow another file: " + _k
EXTRA.update(ZM_FILES)
EXTRA.update(ZM_ITEMS)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\n".join(ZM_LANG) + "\n"
print("0.3.21 zone mining sets: %d items (%s), %d files (Quirk's textures from %s + rendered icons; vanilla models by path)"
      % (len(ZM_ITEMS), ", ".join(ZM_TIERS), len(ZM_FILES), ZM_ART))
for _n in ZM_MODEL_NOTES:
    print("  NOTE Quirk's model " + _n)
'''
after('''print("0.3.6 gathering armor: %d items (%d sets), %d files (Foraging = the approved art, Farming / Fishing = placeholder recolours)"
      % (len(GA2_ITEMS), len(GA2_SETS), len(GA2_FILES)))
''', ZM_PY)

# ================================================================================================================ 2: Server Setup row + config block
after('''    ("armor.wisdom.cap", "Most Wisdom % from armor", "garmor", "dec", "10", "0", "100", "", "%", "live,danger",
     "Mining Wisdom % from worn armor stops here.", "field:GearCfg.GM_WCAP"),
''', '''    # 0.3.21 zone mining sets (tools/gear_0_3_21_patch.py; migrate0321 adds the row to an older file)
    ("garmor.zoneBands", "Zone mining armor levels", "garmor", "text", ZM_BANDS_DEF, "0", "200", "", "", "live,danger",
     "Level band of Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen armor: 8 min-max pairs.", "field:GearCfg.ZM_BANDS;check=GearMine.checkZBands"),
''')
rep('''           "part.packDrops", "loot.boss.mythic"}''', '''           "part.packDrops", "loot.boss.mythic",
           # 0.3.21: the zone mining armor levels (who may wear them = economy)
           "garmor.zoneBands"}''')
after('''GM_LINES = [GM_HEAD, GM_MARK] + [_x for _c, _ls in GM_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in GM_LINES) and all("=" not in _x for _x in (GM_HEAD, GM_MARK))
assert len(set(GM_LINES)) == len(GM_LINES)
''', '''# 0.3.21: the zone mining armor block (a fresh file carries it before the 0.2.14 block; migrate0321 appends the missing keys of it, group by
# group, to the END of an older file - the migrate0215 shape)
ZM_MARK_ID = "SkyyGear 0.3.21 zone mining armor"
ZM_WHO = "SkyyGear 0.3.21"
ZM_HEAD = "# ---- Zone mining armor: Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen (SkyyGear 0.3.21) ----"
ZM_MARK = ("# %s (Skyy 2026-10-17): each zone's metal + alloy is a Mining Set on the vanilla armor model of that zone - Mining level gate, mining "
           "lines and the full-set bonus only with a pickaxe or shovel in hand" % ZM_MARK_ID)
ZM_TBLC = "# ---- garmor.mining.<zone tier>: the same columns as above (Fortune x4, Wisdom % x4, lamp) ----"
ZM_SETC = "# ---- the eight zone Mining Sets (Armor sets): all 4 pieces worn = the bonus, pickaxe or shovel in hand ----"
ZM_GROUPS = [("# %s: %s" % (_gmr["garmor.zoneBands"][1], _gmr["garmor.zoneBands"][10]), ["garmor.zoneBands=" + ZM_BANDS_DEF])]
ZM_GROUPS.append((ZM_TBLC, ["garmor.mining.%s=%s,%s,%d" % (_r[0], _r[4], _r[5], _r[6]) for _r in ZM_ROWS]))
ZM_GROUPS.append((ZM_SETC, ["set.mining_%s=%s Mining Set,4,%s" % (_r[0], _r[1], _r[7]) for _r in ZM_ROWS]))
ZM_LINES = [ZM_HEAD, ZM_MARK] + [_x for _c, _ls in ZM_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in ZM_LINES) and all("=" not in _x for _x in (ZM_HEAD, ZM_MARK))
assert len(set(ZM_LINES)) == len(ZM_LINES) and not set(ZM_LINES) & set(GM_LINES) and ZM_MARK_ID not in GM_MARK and GM_MARK_ID not in ZM_MARK
''')
rep('''    L += [""] + GU_LINES       # 0.2.14: the Untiered / Mythic / Set block (migrate0214 adds exactly these lines to an older file)
''', '''    L += [""] + ZM_LINES       # 0.3.21: the zone mining armor block (migrate0321 adds the missing lines of it to an older file)
    L += [""] + GU_LINES       # 0.2.14: the Untiered / Mythic / Set block (migrate0214 adds exactly these lines to an older file)
''')
after('''for _r in MINE_ROWS:
    assert _dp.get("garmor.mining." + _r[0]) == "%s,%s,%d" % _r[1:4] and _dp.get("set.mining_" + _r[0]) == "%s Mining Set,4,%s" % (_r[0].capitalize(), _r[4])
''', '''# 0.3.21: the zone mining armor block once (every line unique), right before the 0.2.14 block; its rows read back
for _r in ZM_ROWS:
    assert _dp.get("garmor.mining." + _r[0]) == "%s,%s,%d" % (_r[4], _r[5], _r[6]) and _dp.get("set.mining_" + _r[0]) == "%s Mining Set,4,%s" % (_r[1], _r[7])
assert _dp.get("garmor.zoneBands") == ZM_BANDS_DEF and DEFAULT_TEXT.count(ZM_MARK_ID) == 1 and all(_DL.count(_x) == 1 for _x in ZM_LINES)
assert _DL[_DL.index(ZM_HEAD) - 1:_DL.index(ZM_HEAD) + len(ZM_LINES) + 1] == [""] + ZM_LINES + [""] and _DL[_DL.index(ZM_HEAD) + len(ZM_LINES) + 1] == GU_LINES[0]
''')
# GearCfg: the field, its apply line, the tables of all 15 tiers, the block constants
rep('''              ("BOSS_LEAN", "int", "3"), ("BOSS_ARMOR", "int", "50")]''', '''              ("BOSS_LEAN", "int", "3"), ("BOSS_ARMOR", "int", "50"),
              # 0.3.21 the zone mining armor levels
              ("ZM_BANDS", "String", jstr(ZM_BANDS_DEF))]''')
after('''  BOSS_ARMOR = (int) plong(p, "loot.boss.armorShare", 50L, 0L, 100L);
''', '''  ZM_BANDS = ptext(p, "garmor.zoneBands", "@ZMBANDS@").trim();          // 0.3.21 (checked where it is used: a bad text = one WARN + the default)
''')
rep('''   .replace("@GA2LAD0@", GA2_LAD_DEF[0]).replace("@GA2LAD1@", GA2_LAD_DEF[1]).replace("@GA2LAD2@", GA2_LAD_DEF[2]))          # 0.3.6''',
    '''   .replace("@GA2LAD0@", GA2_LAD_DEF[0]).replace("@GA2LAD1@", GA2_LAD_DEF[1]).replace("@GA2LAD2@", GA2_LAD_DEF[2])          # 0.3.6
   .replace("@ZMBANDS@", ZM_BANDS_DEF))          # 0.3.21''')
rep('''# 0.2.15: the mining armor table { double[28] Fortune, double[28] Wisdom % (slot order Head Chest Hands Legs per tier), int[7] lamp } - swapped whole
_jd = lambda xs: "new double[] { %s }" % ", ".join(repr(float(x)) for x in xs)
F(gcf, "public static final double[] DGM_F = %s;" % _jd(MINE_F))
F(gcf, "public static final double[] DGM_W = %s;" % _jd(MINE_W))
F(gcf, "public static final int[] DGM_L = %s;" % jints(MINE_L))
F(gcf, "public static volatile Object[] GM_TAB = new Object[] { %s, %s, %s };" % (_jd(MINE_F), _jd(MINE_W), "new int[] { %s }" % ", ".join(str(x) for x in MINE_L)))
''', '''# 0.2.15: the mining armor table { double[60] Fortune, double[60] Wisdom % (slot order Head Chest Hands Legs per tier), int[15] lamp } - swapped
# whole (0.3.21: the 7 vanilla tiers, then the 8 zone tiers)
_jd = lambda xs: "new double[] { %s }" % ", ".join(repr(float(x)) for x in xs)
F(gcf, "public static final double[] DGM_F = %s;" % _jd(MINE_F + ZM_F))
F(gcf, "public static final double[] DGM_W = %s;" % _jd(MINE_W + ZM_W))
F(gcf, "public static final int[] DGM_L = %s;" % jints(MINE_L + ZM_L))
F(gcf, "public static volatile Object[] GM_TAB = new Object[] { %s, %s, %s };" % (_jd(MINE_F + ZM_F), _jd(MINE_W + ZM_W), "new int[] { %s }" % ", ".join(str(x) for x in MINE_L + ZM_L)))
''')
after('''F(gcf, "public static final String[] GM_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in GM_GROUPS for _x in _ls]))
''', '''F(gcf, "public static final String ZM_MARK = %s;" % jstr(ZM_MARK))          # 0.3.21 migrate0321
F(gcf, "public static final String ZM_MARK_ID = %s;" % jstr(ZM_MARK_ID))
F(gcf, "public static final String ZM_WHO = %s;" % jstr(ZM_WHO))
F(gcf, "public static final String ZM_HEAD = %s;" % jstr(ZM_HEAD))
F(gcf, "public static final String[] ZM_GC = %s;" % jarr([_c for _c, _ls in ZM_GROUPS]))
F(gcf, "public static final int[] ZM_GS = %s;" % jints([len(_ls) for _c, _ls in ZM_GROUPS]))
F(gcf, "public static final String[] ZM_GL = %s;" % jarr([_x for _c, _ls in ZM_GROUPS for _x in _ls]))
F(gcf, "public static final String[] ZM_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in ZM_GROUPS for _x in _ls]))
''')

# ================================================================================================================ 3: migrate0321 (copies of the 0.2.15 steps)
_gmu = method('''public static Object[] gmUpdate(String text) {''')
_gmm = method('''public static String gmMissing(String text) {''')
_gmd = method('''public static String gmDefaults(String text) {''')
for _t in (_gmu, _gmm, _gmd):
    assert _t.count("GM_") >= 1 and "ZM_" not in _t
_zmu = _gmu.replace("gmUpdate", "zmUpdate").replace("GM_", "ZM_")
_zmm = _gmm.replace("gmMissing", "zmMissing").replace("GM_", "ZM_")
_zmd = _gmd.replace("gmDefaults", "zmDefaults").replace("GM_", "ZM_")
MIG = ('''# ---- 0.3.21 ONE-TIME UPDATE migrate0321 (PROJECT-RULES section 4; tools/gear_0_3_21_patch.py item 3): the 0.2.15 shape exactly (gmUpdate ->
# zmUpdate on the ZM_ block): a pure ADDITION at the END of the file, only the keys the file lacks; null = the marker is already in a comment line
M(gcf, r"""
''' + _zmu + '''
# the set.mining_* keys of the zone block a file lacks ("" = none), and their default lines ("; "-joined)
M(gcf, r"""
''' + _zmm + '''
M(gcf, r"""
''' + _zmd + '''
# setup(), right after migrate0317 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO
# line (+ one per note), gear.log; "" = nothing done (no file, marker already there, or a failure - WARN, file untouched, the next start tries
# again; the loader then runs on the built-in zone rows, and the zone Mining Sets stay off until their set rows are in the file)
M(gcf, r"""
public static synchronized String migrate0321() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    String otext = new String(old, "ISO-8859-1");
    Object[] r = zmUpdate(otext);
    if (r == null) {
      String miss = zmMissing(otext);
      if (miss.length() > 0) @PKG@.Gear.info("config.properties has no " + miss + " - those zone Mining Sets give no full-set bonus. Add them back in Server Setup -> Gear -> Rarity -> Armor sets (defaults: " + zmDefaults(otext) + ")");
      return "";
    }
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), ZM_WHO, "before the 0.3.21 zone mining armor update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated with the 0.3.21 zone mining armor settings: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the built-in zone rows are used, the zone Mining Sets stay off; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] notes = (String[]) r[1];
    String add = (String) r[2];
    String msg = "config.properties: the 0.3.21 zone mining armor settings were added at the end (" + (add.length() > 0 ? add : "only the marker - every key was there") + "); no value changed; the old file is kept in config-history";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.3.21 zone mining armor: added " + (add.length() > 0 ? add : "the marker only") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.3.21 zone mining armor settings to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
''')
before('''# ---- 0.2.16 ONE-TIME UPDATE migrate0216 (PROJECT-RULES section 4): a pure ADDITION, the 0.2.15 shape. null = the marker is already in a comment
''', MIG)
rep('''  @PKG@.GearCfg.migrate0317();          // 0.3.17: perkSpeed 2 -> 5, perkFortune 1 -> 2, tool.fortune.cap 25 -> 0 (only the old defaults)
''', '''  @PKG@.GearCfg.migrate0317();          // 0.3.17: perkSpeed 2 -> 5, perkFortune 1 -> 2, tool.fortune.cap 25 -> 0 (only the old defaults)
  @PKG@.GearCfg.migrate0321();          // 0.3.21: the zone mining armor block (a pure addition of the missing keys)
''')

# ================================================================================================================ 4: GearMine - 15 tiers, the ladder rank, the zone bands
rep('''F(gmine, "public static final String[] IDS = %s;" % jarr(MINE_IDS))
F(gmine, "public static final String[] TIER = %s;" % jarr([_t.lower() for _t in MINE_TIERS]))
F(gmine, "public static final String[] TNAME = %s;" % jarr(MINE_TIERS))
F(gmine, "public static final String[] SET_IDS = %s;" % jarr(["mining_" + _t.lower() for _t in MINE_TIERS]))
''', '''F(gmine, "public static final String[] IDS = %s;" % jarr(MINE_IDS + ZM_IDS))          # 0.3.21: + the 32 zone pieces (tiers 7-14)
F(gmine, "public static final String[] TIER = %s;" % jarr([_t.lower() for _t in MINE_ALL_TIERS]))
F(gmine, "public static final String[] TNAME = %s;" % jarr(MINE_ALL_TIERS))
F(gmine, "public static final String[] SET_IDS = %s;" % jarr(["mining_" + _t.lower() for _t in MINE_ALL_TIERS]))
F(gmine, "public static final int[] RANK = %s;" % jints(MINE_RANK))          # 0.3.21: tier index -> place on the ladder (Copper 0 .. Onyxium 14)
F(gmine, "public static final int ZBASE = %d;" % ZM_BASE)          # 0.3.21: the first zone tier
F(gmine, "public static final String DZB = %s;" % jstr(ZM_BANDS_DEF))
F(gmine, "public static volatile Object[] ZBC = null;")          # { String text, int[16] } the parsed garmor.zoneBands
''')
ZMJ = r'''# 0.3.21: a piece's place on the mining ladder (Copper 0 .. Onyxium 14; -1 = not a piece) - the Smithing sort key (by id, mining on or off)
M(gmine, r"""
public static int rank(String id) {
  int i = index(id);
  return i < 0 || i / 4 >= RANK.length ? -1 : RANK[i / 4];
}""")
# "22-27,24-28,..." -> int[16] (min, max of the 8 zone tiers); null = bad
M(gmine, r"""
public static int[] zbandsOf(String s) {
  if (s == null) return null;
  int n = TIER.length - ZBASE;
  String[] ps = s.trim().split(",", -1);
  if (ps.length != n) return null;
  int[] o = new int[n * 2];
  for (int i = 0; i < n; i++) {
    String[] ab = ps[i].trim().split("-", -1);
    if (ab.length != 2) return null;
    try { o[i * 2] = Integer.parseInt(ab[0].trim()); o[i * 2 + 1] = Integer.parseInt(ab[1].trim()); } catch (Throwable t) { return null; }
    if (o[i * 2] < 1 || o[i * 2 + 1] < o[i * 2] || o[i * 2 + 1] > 200) return null;
  }
  return o;
}""")
M(gmine, r"""
public static int[] zbands() {
  String s = @PKG@.GearCfg.ZM_BANDS;
  Object[] e = ZBC;
  if (e != null && s != null && s.equals(e[0])) return (int[]) e[1];
  int[] b = zbandsOf(s);
  if (b == null) {
    @PKG@.Gear.warnOnce("zmbands:" + s, "config.properties: garmor.zoneBands=" + s + " is not 8 level ranges - the default " + DZB + " is used");
    b = zbandsOf(DZB);
  }
  ZBC = new Object[] { s, b };
  return b;
}""")
# the level band of a zone piece (by id, mining on or off - like the 0.3.6 sets); null = not a zone piece (the vanilla tiers keep level.material)
M(gmine, r"""
public static int[] zband(String id) {
  int i = index(id);
  if (i < 0 || i / 4 < ZBASE) return null;
  int[] b = zbands();
  int t = i / 4 - ZBASE;
  return new int[] { b[t * 2], b[t * 2 + 1] };
}""")
M(gmine, r"""
public static String checkZBands(String key, String value) {
  if (zbandsOf(value) == null) return "Write 8 level ranges min-max for Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen, e.g. " + DZB + ".";
  return null;
}""")
'''
before('''# the set a piece counts for BY ID (old pieces have no set field): null = not a mining piece / mining armor off
''', ZMJ)
rep('''    if (!ok) return "The mining armor tiers are copper, iron, thorium, cobalt, adamantite, mithril and onyxium.";
  }
  if (value == null) return "The seven tiers always stay - write 0 0 0 0,0 0 0 0,0 to give a tier nothing.";''',
    '''    if (!ok) return "The mining armor tiers are copper, iron, thorium, lead, dusk, cobalt, chromium, azurvane, adamantite, slag, cinder, mithril, titanium, lumen and onyxium.";
  }
  if (value == null) return "The fifteen tiers always stay - write 0 0 0 0,0 0 0 0,0 to give a tier nothing.";''')
rep('''  return "mining armor on: " + IDS.length + " metal pieces (Copper..Onyxium) are green Mining Set pieces''',
    '''  return "mining armor on: " + IDS.length + " metal pieces (Copper..Onyxium + the zone sets Lead..Lumen) are green Mining Set pieces''')
rep('''  int[] gb0 = @PKG@.GearGArm.band(id);          // 0.3.6: a Foraging / Farming / Fishing piece starts at its tier band (garmor.bands)
  if (gb0 != null) return clamp(gb0[0]);
''', '''  int[] gb0 = @PKG@.GearGArm.band(id);          // 0.3.6: a Foraging / Farming / Fishing piece starts at its tier band (garmor.bands)
  if (gb0 != null) return clamp(gb0[0]);
  int[] zb0 = @PKG@.GearMine.zband(id);          // 0.3.21: a zone mining piece starts at its band (garmor.zoneBands)
  if (zb0 != null) return clamp(zb0[0]);
''')
rep('''  int[] gb = @PKG@.GearGArm.band(id);          // 0.3.6: the gathering armor tier bands (never the id-word material match)
  if (gb != null) return new int[] { clamp(gb[0]), clamp(gb[1] < gb[0] ? gb[0] : gb[1]), 1 };
''', '''  int[] gb = @PKG@.GearGArm.band(id);          // 0.3.6: the gathering armor tier bands (never the id-word material match)
  if (gb != null) return new int[] { clamp(gb[0]), clamp(gb[1] < gb[0] ? gb[0] : gb[1]), 1 };
  int[] zb = @PKG@.GearMine.zband(id);          // 0.3.21: the zone mining armor bands (garmor.zoneBands; never the id-word material match)
  if (zb != null) return new int[] { clamp(zb[0]), clamp(zb[1] < zb[0] ? zb[0] : zb[1]), 1 };
''')

# ================================================================================================================ 5: the Smithing Mining armor cards by the ladder
rep('''  for (int i = 0; i < ga.length; i++) { gk[i] = ((Integer) ((Object[]) ga[i])[3]).intValue(); gt[i] = (String) ((Object[]) ga[i])[0]; }
  sortBy(ga, gk, gt);''', '''  for (int i = 0; i < ga.length; i++) {
    gk[i] = ((Integer) ((Object[]) ga[i])[3]).intValue();
    gt[i] = (String) ((Object[]) ga[i])[0];
    String[] o0 = (String[]) ((Object[]) ga[i])[1];
    int rk = c == 1 && o0.length > 0 ? @PKG@.GearMine.rank(o0[0]) : -1;          // 0.3.21: Mining armor = the ladder (Onyxium last)
    gk[i] = rk >= 0 ? rk : 1000 + gk[i];
  }
  sortBy(ga, gk, gt);''')

# ================================================================================================================ 6: the armor weight in the flavour text
WGT = r'''# 0.3.21 (Skyy 2026-10-17 "make sure the flavor text lists if the armor is robe/ cloth. light or heavy armor"): THE armor weight rule - 1 Heavy,
# 2 Light, 3 Cloth: the pack table weight first (The Armory gives robes Heavy sounds), else the vanilla sound set (Cloth / Leather / else
# Heavy; no such item = Heavy). GearSmith.armorType (class armor rules, the Smithing filter) calls this - one source with the tooltip.
F(gvw, 'public static final String[] WT_NAME = new String[] { "", "Heavy", "Light", "Cloth" };')
F(gvw, 'public static final String[] TT_NOUN = %s;' % jarr(list(TT.LADDER)))
M(gvw, r"""
public static int weightOf(String id) {
  int pa = @PKG@.GearPackId.at(id);
  if (pa > 0) return pa;
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return 1;
    Object o = com.hypixel.hytale.server.core.asset.type.itemsound.config.ItemSoundSet.getAssetMap().getAsset(it.getItemSoundSetIndex());
    String n = o instanceof com.hypixel.hytale.server.core.asset.type.itemsound.config.ItemSoundSet ? String.valueOf(((com.hypixel.hytale.server.core.asset.type.itemsound.config.ItemSoundSet) o).getId()) : "";
    if (n.indexOf("Cloth") >= 0) return 3;
    if (n.indexOf("Leather") >= 0) return 2;
  } catch (Throwable t) { }
  return 1;
}""")
# tools/tier_tags.py tier_for_level (weapon / armor band: Lv 0-9 T1, 10-14 T2, 15-19 T3, 20-24 T4, 25-34 T5, 35-39 T6, 40+ T7; Onyxium ids T8)
M(gvw, r"""
public static int tierFor(int lv, String id) {
  if (id != null && id.indexOf("Onyxium") >= 0) return 8;
  if (lv >= 40) return 7;
  if (lv >= 35) return 6;
  if (lv >= 25) return 5;
  if (lv >= 20) return 4;
  if (lv >= 15) return 3;
  if (lv >= 10) return 2;
  return 1;
}""")
# a COMBAT armor piece (not a Mining / Foraging / Farming / Fishing set piece, by id - a switched-off family is still not combat armor)
M(gvw, r"""
public static boolean combatArmor(String id) {
  if (id == null || @PKG@.GearData.slotOf(id) != 2) return false;
  if (@PKG@.GearMine.index(id) >= 0 || @PKG@.GearGArm.index(id) >= 0) return false;
  return "combat".equals(@PKG@.GearData.kindFor(id));
}""")
# the flavour slot's first phrase: a pack item's table tag ("T3 Iron"), a combat armor piece + its weight ("T3 Iron Heavy"); null = none
M(gvw, r"""
public static String flavTag(String id) {
  String tg = @PKG@.GearPackId.tag(id);
  try {
    if (!combatArmor(id)) return tg;
    if (tg == null) {
      int t = tierFor(@PKG@.GearLevel.band(id)[0], id);
      tg = "T" + t + " " + TT_NOUN[t - 1];
    }
    return tg + " " + WT_NAME[weightOf(id)];
  } catch (Throwable x) { return tg; }
}""")
'''
before('''# the item has its own description (the flavour slot; moved up from below nameMsg in 0.2.19 - lines() calls it)
''', WGT)
rep('''      String tg = @PKG@.GearPackId.tag(id);          // 0.3.19: "T3 Iron - " first (tools/tier_tags.py numbering)''',
    '''      String tg = flavTag(id);          // 0.3.19: "T3 Iron - " first (tools/tier_tags.py numbering); 0.3.21: + the combat armor weight''')
rep('''    if (hasDesc(id) || @PKG@.GearPackId.tag(id) != null) add(lt, lc, FLAVOR, null);          // 0.3.19: + a pack item's tier tag''',
    '''    if (hasDesc(id) || flavTag(id) != null) add(lt, lc, FLAVOR, null);          // 0.3.19: + a pack item's tier tag (0.3.21: + combat armor)''')
rep('''public static int armorType(String id) {
  int pa = @PKG@.GearPackId.at(id);          // 0.3.19: a pack piece's weight from the table (The Armory gives robes Heavy sounds)
  if (pa > 0) return pa;
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return 1;
    Object o = @ISS@.getAssetMap().getAsset(it.getItemSoundSetIndex());
    String n = o instanceof @ISS@ ? String.valueOf(((@ISS@) o).getId()) : "";
    if (n.indexOf("Cloth") >= 0) return 3;
    if (n.indexOf("Leather") >= 0) return 2;
  } catch (Throwable t) { }
  return 1;
}""")''', '''public static int armorType(String id) {
  return @PKG@.GearView.weightOf(id);          // 0.3.21: the one weight rule (the tooltip's flavour text reads it too)
}""")''')

# ================================================================================================================ 7: the jar checks + summary
rep('''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS) + list(CAN_ITEMS) + list(HARV_ITEMS)), "SkyyGear 0.3.12 ships''',
    '''    for _k, _v in list(ZM_ITEMS.items()) + list(ZM_FILES.items()):          # 0.3.21
        assert _jz.read(_k) == (_v.encode("utf-8") if isinstance(_v, str) else _v), "zone mining armor file missing from the jar: " + _k
    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS) + list(CAN_ITEMS) + list(HARV_ITEMS) + list(ZM_ITEMS)), "SkyyGear 0.3.21 ships the 32 zone mining pieces +''')
after('''      "armor.wisdom.cap + the 7 set.mining_* rows; migrate0215 block %d lines; pets:stats read" % (len(MINE_IDS), len(GM_LINES)))
''', '''print("0.3.21: zone mining sets - %d pieces (%s), ladder %s; full-set Fortune %s; bands %s; migrate0321 block %d lines; armor weight in the flavour text"
      % (len(ZM_IDS), ", ".join(ZM_TIERS), " > ".join(ZM_LADDER), ZM_FULL, ZM_BANDS_DEF, len(ZM_LINES)))
''')

# ================================================================================================================ 7: bag types for the class weapons
# Quests 0.4.1 (Skyy: the starter skeleton quest gives a full class armor set + the class's secondary weapon as unidentified bags "so you can use
# both in the tutorial"): Weapon_Staff_Bo_* -> the Weapon_Bo bag; SkyyArmory's class weapon ladders join the pool (Weapon_Bo_*, Weapon_Fist_*
# = the NEW bag type Weapon_Fist, Weapon_Kunai_* incl. Crude, Weapon_Spellbook_*, Weapon_Crossbow_*_Wynn) - a row is a candidate only while its
# item is loaded (GearPool.table: Gear.item != null), so without SkyyArmory nothing changes
rep('''# review (Loot-Round-Revision section 2 / U3, the re-roll coin loop): no pool item carries a sell / salvage price (vanilla gear has no NPC
''', '''# 0.3.21 (the starter quest gear; tools/gear_0_3_21_patch.py item 7): the Monk's bo staves are their own bag type (never in a Mage staff bag)
LOOT_POOL = [((_p[0], "Weapon_Bo") + tuple(_p[2:])) if _p[0].startswith("Weapon_Staff_Bo_") else _p for _p in LOOT_POOL]
# SkyyArmory's class weapon ladders (ids only - its jar is not read): crafted at its benches (drop-only false); levels = the material rows
_AM7 = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
ARMORY_POOL = (["Weapon_Bo_" + _m for _m in _AM7] + ["Weapon_Fist_Gauntlets_" + _m for _m in _AM7]
               + ["Weapon_Fist_Wraps_" + _c for _c in ("Linen", "Cotton", "Silk", "Cindercloth", "Shadoweave")]
               + ["Weapon_Kunai_" + _m for _m in ["Crude"] + _AM7] + ["Weapon_Spellbook_" + _m for _m in _AM7]
               + ["Weapon_Crossbow_Copper_Wynn", "Weapon_Crossbow_Onyxium_Wynn"]
               + ["Weapon_GreatShield_" + _m for _m in _AM7])          # review: the Spellblade's secondary weapon (the GS twin rules map them)
assert not [_i for _i in ARMORY_POOL if _i in AZ_ITEMS or _i in set(_p[0] for _p in LOOT_POOL)], "an Armory pool id is vanilla / already pooled"
for _i in ARMORY_POOL:
    _e, _mn, _cp = band_lookup(BD_ALL, _i)
    LOOT_POOL.append((_i, _ltype(_i), 0, False, max(1, _mn or 1), max(max(1, _mn or 1), _cp or 1)))
assert set(_ltype(_i) for _i in ARMORY_POOL) == {"Weapon_Bo", "Weapon_Fist", "Weapon_Kunai", "Weapon_Spellbook", "Weapon_Crossbow",
                                                    "Weapon_GreatShield"}
assert [_p for _p in LOOT_POOL if _p[0] == "Weapon_Kunai_Crude"][0][4] == 1
# review (Loot-Round-Revision section 2 / U3, the re-roll coin loop): no pool item carries a sell / salvage price (vanilla gear has no NPC
''')
rep('''          "Weapon_Bo": "Bo Staff"}      # 0.2.16''', '''          "Weapon_Bo": "Bo Staff", "Weapon_Fist": "Fist Weapon",
          "Weapon_GreatShield": "Great Shield"}      # 0.2.16 (0.3.21: + Fist, Great Shield)''')
rep('''assert set(LOOT_TYPES) == set(_p[1] for _p in LOOT_POOL) | {"Weapon_Bo"} and "Weapon_Bo" not in set(_p[1] for _p in LOOT_POOL), "every pool type has a bag type"''',
    '''assert set(LOOT_TYPES) == set(_p[1] for _p in LOOT_POOL) and "Weapon_Fist" in LOOT_TYPES and "Weapon_GreatShield" in LOOT_TYPES, "every pool type has a bag type"          # 0.3.21: Bo + Fist rows
assert not [_p for _p in LOOT_POOL if _p[1] == "Weapon_Staff" and _p[0].startswith("Weapon_Staff_Bo_")], "0.3.21: a bo staff in the Staff bag"''')
rep('''assert len(LOOT_POOL) >= 250 and len(LOOT_TYPES) == 19, (len(LOOT_POOL), LOOT_TYPES)       # 0.2.16: + Weapon_Bo''',
    '''assert len(LOOT_POOL) >= 250 and len(LOOT_TYPES) == 21, (len(LOOT_POOL), LOOT_TYPES)       # 0.2.16: + Weapon_Bo (0.3.21: + Weapon_Fist, Weapon_GreatShield)
assert sum(1 for _p in LOOT_POOL if _p[0] in ARMORY_POOL) == len(ARMORY_POOL) == 43          # 0.3.21''')

# ================================================================================================================ 8 + 9: Lv 1 starts (migrate0321 rows)
# Light (Leather_Soft) + Cloth (Cloth_Wool) armor, the Copper spellbook and the Copper crossbows start at Lv 1 - the Armor_Copper rule (LOCKED
# 2026-10-01 "lower copper armors minimum level to 1, since there is no lower tier armor"). Pure ADDITION level.material rows (an id-start entry
# beats the material word), so nothing an owner edited is rewritten; Kunai_Crude is already 1-13 (Crude)
rep('''ZM_GROUPS.append((ZM_SETC, ["set.mining_%s=%s Mining Set,4,%s" % (_r[0], _r[1], _r[7]) for _r in ZM_ROWS]))
''', '''ZM_GROUPS.append((ZM_SETC, ["set.mining_%s=%s Mining Set,4,%s" % (_r[0], _r[1], _r[7]) for _r in ZM_ROWS]))
ST_BANDS = [("Armor_Leather_Soft", 1, 12), ("Armor_Cloth_Wool", 1, 12), ("Weapon_Spellbook_Copper", 1, 18), ("Weapon_Crossbow_Copper", 1, 18)]
ST_C = ("# ---- starter levels (SkyyGear 0.3.21, the Armor_Copper rule): the lowest Light / Cloth armor, spellbook and crossbows start at Lv 1, so "
        "a new player's class gear exists from Lv 1 ----")
assert not [_t for _t, _s, _c in ST_BANDS if _t.lower() in set(_x.lower() for _x, _a, _b in BD_ALL)] and all(len(_t.split("_")) <= 3 for _t, _s, _c in ST_BANDS)
ZM_GROUPS.append((ST_C, ["level.material.%s=%s" % (_t, band_text(_s, _c)) for _t, _s, _c in ST_BANDS]))
''')
rep('''ZM_HEAD = "# ---- Zone mining armor: Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen (SkyyGear 0.3.21) ----"''',
    '''ZM_HEAD = "# ---- Zone mining armor (Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen) + starter levels (SkyyGear 0.3.21) ----"''')

# ================================================================================================================ 10: free identify for quest bags
before('''    ("unid.reroll.max", "Re-identify limit", "loot", "int", "3", "0", "10", "", "", "live",
''', '''    # 0.3.21: quest bags identify free (absent line = the default ON; no one-time update)
    ("unid.questFree", "Quest bags identify free", "loot", "bool", "true", "", "", "", "", "live,danger",
     "Mystery bags a quest gives (source quest) identify for free, so new players can use them at once.", "field:GearCfg.UNID_QFREE"),
''')
rep('''           "garmor.zoneBands"}''', '''           "garmor.zoneBands", "unid.questFree"}''')
rep('''              ("ZM_BANDS", "String", jstr(ZM_BANDS_DEF))]''', '''              ("ZM_BANDS", "String", jstr(ZM_BANDS_DEF)), ("UNID_QFREE", "boolean", "true")]''')
after('''  ZM_BANDS = ptext(p, "garmor.zoneBands", "@ZMBANDS@").trim();          // 0.3.21 (checked where it is used: a bad text = one WARN + the default)
''', '''  UNID_QFREE = pbool(p, "unid.questFree", true);          // 0.3.21: quest bags identify free
''')
rep('''G319_ROWK = ["part.packDrops", "loot.packWeight", "loot.boss.mythic", "loot.boss.credit", "loot.boss.classLean", "loot.boss.armorShare"]
''', '''G319_ROWK = ["part.packDrops", "loot.packWeight", "loot.boss.mythic", "loot.boss.credit", "loot.boss.classLean", "loot.boss.armorShare"]
G321_HEAD = "# ---- quest bags (SkyyGear 0.3.21) ----"
G321_ROWK = ["unid.questFree"]
''')
rep('''    for k in G319_ROWK:
        scal(k)
''', '''    for k in G319_ROWK:
        scal(k)
    L += ["", G321_HEAD]        # 0.3.21: the new row (absent = the default; no one-time update)
    for k in G321_ROWK:
        scal(k)
''')
rep('''M(gunid, "public static long cost(@BD@ d) { return d == null ? 0L : @PKG@.GearCfg.costIdentify(rar(d), hi(d)); }")''',
    '''M(gunid, "public static long cost(@BD@ d) { return d == null || (@PKG@.GearCfg.UNID_QFREE && \\"quest\\".equals(@PKG@.GearData.str(d, \\"src\\", \\"\\"))) ? 0L : @PKG@.GearCfg.costIdentify(rar(d), hi(d)); }")          # 0.3.21: quest bags free (unid.questFree)''')

# ================================================================================================================ 11: critic fixes
# M1 the tooltip signature carries the flavour tag, so items already in inventories re-render with their weight
rep('''    + (@PKG@.GearCfg.NAME_LV ? ":n1" : ":n0");          // 0.2.22: the level in the name''',
    '''    + (@PKG@.GearCfg.NAME_LV ? ":n1" : ":n0")          // 0.2.22: the level in the name
    + ":" + flavTag(id);          // 0.3.21 critic M1: the flavour tag + armor weight (old tooltips re-render once)''')
# L1 Smithing card titles: "Lead Set", not "Mining Lead Set"
rep('''  if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Weapon_")) s = s.substring(7);''', '''  if (s.startsWith("Armor_Mining_")) s = s.substring(13);          // 0.3.21 critic L1: the zone sets read "Lead Set" like "Copper Set"
  else if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Weapon_")) s = s.substring(7);''')
# L2 the manifest names the soft need on SkyyWorldGen (the zone sets' recipes use its bars)
rep('''No hard dependencies (deploy with SkyyMobs 0.1.4 + SkyySkills 0.4.17).", PKG + ".SkyyGearPlugin")''',
    '''ZONE MINING SETS: Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium and Lumen Mining Sets on the vanilla armor models (crafted from SkyyWorldGen 0.7.3's zone bars - without SkyyWorldGen they cannot be crafted); combat armor shows its weight (Heavy / Light / Cloth) in the flavour text; quest bags identify free. No hard dependencies (deploy with SkyyMobs 0.1.4 + SkyySkills 0.4.17; soft: SkyyWorldGen 0.7.3+ for the zone set recipes).", PKG + ".SkyyGearPlugin")''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("ZM_ROWS = [") > _i("GA2_ITEMS = {}") and _i("ZM_ROWS = [") < _i("ZM_MARK_ID = ") < _i("def default_text():")
assert _i("public static int weightOf(String id)") < _i("public static boolean hasDesc(String id)") < _i("public static @MSG@ descMsg(") < _i("public static int armorType(String id)")
assert _i("public static int[] zband(String id)") < _i("public static int[] band(String id) {\n  if (id == null) return new int[] { 0, 0, 3 };")
assert _i("public static Object[] zmUpdate(String text)") < _i("public static synchronized String migrate0321()") < _i("@PKG@.GearCfg.migrate0321();")
assert _i("public static int rank(String id)") < _i("public static java.util.ArrayList groups(java.util.UUID u, int c, boolean all)")
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.20 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.20 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
