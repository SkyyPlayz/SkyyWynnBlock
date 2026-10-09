"""Derive SkyyGear/build_skyygear_0.2.11.py from the LIVE 0.2.10 (build_skyygear_0.2.10.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_10_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_11_patch.py      then      python SkyyGear/build_skyygear_0.2.11.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.11.py

0.2.11 = THE LOOT ROUND, SkyyGear part (research/cloud/Loot-Round-Revision.md all sections, its Questions ANSWERED "yes to all" - Skyy LOCKED
docs/answered/gear.md 2026-10-08; built on research/Loot-Unid-Spec.md + research/cloud/Loot-Box-Design.md; the 2026-10-02 / 10-06 / 10-08
loot lines, newest wins). Skyy's words: "vanilla Hytale already has a ton of weapons and armor you cant craft. we can make them all roll
options from the unidentified gear" and "make the mystery bags unidentified items come in before you identify them. we just need 1 per rarity".
  1. MYSTERY BAGS (Wynncraft unidentified items, Skyy 2026-10-08: ONE look per rarity): 7 item ids Skyy_Unid_Bag_<Rarity> (Normal, Unique,
     Rare, Legendary, Fabled, Mythic, Set; quality = the rarity's Skyy_Gear_* quality, so the frame, name colour AND the drop glow follow
     the rarity), MaxStack 1, hidden from the creative library (Variant), no Weapon / Armor / Utility / Interactions / Recipe = cannot be
     worn, held as a weapon or crafted; never gear (Skyy_Unid_ joins NEVER_GEAR); Magic Bags never pool Skyy_ ids (SkyySacks homeOf).
     The look is a PLACEHOLDER generated at build time (the vanilla Feedbag sack model by path + a rarity-ramp recolour of its texture and
     icon, tools/skyyart.py, nothing vanilla committed) until Quirk's art lands (ART-RESUME item 15) - the swap is ONE line: BAG_ART below
     ("placeholder" -> "art/mystery-bags"; that folder must hold bag.blockymodel, Bag_<Rarity>.png and Bag_<Rarity>_Icon.png).
  2. WHAT A BAG STORES (metadata "SkyyUnid", schema v2 - nothing secret, the item does not exist yet): mys (type key Weapon_Sword /
     Armor_Chest ...), r (rarity, rolled at drop), lo / hi (the shown level range L-2..L+2 around the source level, clamped to
     1..loot.levelTop and trimmed to levels where that type has a candidate), at (armor: Heavy / Light / Cloth from the vanilla sound set
     ISS_Armor_Heavy / _Leather / _Cloth, shown on the bag; "-" for weapons), src / ls / tier (drop / chest / mob / lootchest / admin /
     bridge; where the level came from; Unclaimed Luggage tier 1-4), t, n (a random nonce: every bag has its own fingerprint), id:false.
     The per-stack tooltip: "Unidentified Sword" in the rarity colour, "Lv 41-45 - Rare", "Heavy armor", what identify does, "Cannot be
     used until identified", the identify cost.
  3. THE ITEM IS PICKED AT IDENTIFY (Skyy 2026-10-06 "in wynncraft i dont think its set until you identify it"): level = uniform among the
     levels of lo..hi that have a candidate of that type (+ armor type), item = weighted pick among the candidates whose band holds that
     level (loot.dropOnlyWeight multiplies the drop-only ones), then a fresh identified document (GearRoll.newDoc at that level: modifiers,
     speed tier) carrying box {mys, r, lo, hi, at, n:0}. Same write safety as 0.2 identify (fingerprint + profile checks, coins FIRST,
     ONE setItemStackForSlot in the same slot, refund on failure). No candidate any more = refused before any coin moves.
  4. RE-IDENTIFY (re-roll): an item that came from a bag can be re-identified on the Identify page (two clicks: the first arms, the
     second within 10 s confirms - "it becomes a different item and loses its reforges"): another item of the same type + armor type,
     a new level inside lo..hi, new modifiers; the RARITY never changes; cost = the identify price (rarity, hi) x unid.reroll.mult per
     re-roll (x5: 490 -> 2,450 -> 12,250 -> 61,250), at most unid.reroll.max (3); n is stored in box; reforges (rf / rfN / lvlU) are gone
     because the document is new. No Smithing XP (coins never buy skill XP). Hotbar / storage / backpack only.
  5. DROP-ONLY VANILLA GEAR JOINS THE POOL: the pool = every vanilla gear id (weapons by family word, armor by Armor.ArmorSlot; no ammo,
     shields ..., developer / debug items, *_NPC, test items) = 295 ids in 18 types, each ranked by its LIVE level band (GearLevel.band -
     Skyy's LOCKED 2026-10-01 rows; an admin moves any band in Server Setup -> Gear -> Levels). The 154 that no recipe makes (vanilla or
     SkyyGear's magic recipes) are flagged drop-only. The review list (id, type, slot, armor type, craft / drop, band, method, weight, flag)
     is written LOCALLY to models-local/loot/loot-pool-0.2.11.tsv (git-ignored, ids + levels only); "check" = the band start and the lowest
     vanilla drop-list zone disagree by more than 10 levels (Skyy's own rows were kept, not overridden by a power formula).
  6. MORE MOB DROPS: each kill of a levelled mob (mob:fn:level >= 1) by a player (Damage$EntitySource with a live PlayerRef in the same
     store; projectiles count by shooter; not Creative) rolls loot.mob.chance 6 % (1 in ~17; was the planned 4 % - it never shipped, so no
     live line holds the old default and there is NOTHING to migrate) for one extra bag at the mob's level: armor loot.armorShare 50 %, a
     weapon leans to the killer's class weapons loot.classLean 50 % (class:<uuid> + class:weapons:<Class>, enabled classes only), rarity
     = the Mob odds with the R5 level boost (every rarity above Normal x (1 + loot.levelShift x (L - 1))). At most loot.mob.capPerHour (20)
     per player per rolling hour (staff with skyygear.admin skip it), one roll per death (NPC uuid map + the role flag). Spawned inside
     GearDeathMark (BEFORE NPCDamageSystems$DropDeathItems) with the engine's own calls: ItemComponent.generateItemDrops(store, list, mob
     position + (0, 1, 0), new Rotation3f(HeadRotation)) + CommandBuffer.addEntities(holders, AddReason.SPAWN) - vanilla's exact recipe.
  7. VANILLA GEAR DROPS BECOME BAGS (LOCKED 2026-10-02 "vanilla gear drops become mystery items too"): a single undocumented gear item that
     a mob drops (level = that mob's level, kept with the death mark) or that a fresh loot chest rolls (level = the chest's zone level)
     becomes a bag of ITS type and armor type; a loot-chest stack (spears, spellbooks) is spread into empty slots of the same chest as one
     bag each, the rest stays one 0.2-style unidentified stack; a dropped mob stack stays 0.2-style (no new entities). unid.bags off = 0.2.
     The SkyyExploration chest-luck window and gear:fn:unid keep 0.2-style documents (stacks / slot writes with a count check).
  8. EXTRA BAG IN FRESH WORLD LOOT CHESTS (LOCKED 2026-10-02 "about 1 in 3"): GearChestTag, after the engine's StashSystem filled a chest
     from its drop list AND cleared that list (a real fill, once per chest): loot.chest.chance 33 % for one bag at the zone level
     (mob:fn:levelAt at the chest - SkyyMobs 0.1.5 -, else the drop list's Zone<N> band) into a random EMPTY slot (none = no bag, counted).
     Never on SkyyIslands island worlds.
  9. BRIDGE gear:fn:box (SkyyExploration's Unclaimed Luggage): Object[] { String typeKey | ItemStack vanilla gear | null, Number level,
     String src, Number tier, UUID player | null } -> a bag ItemStack or null. tier 3 / 4 shift the Chest odds by loot.levelShift x 10 / 20.
 10. Admin: /gear box <rarity|random> [level] [type key] (a bag in your inventory), /gear loot (counters, pool, odds), /gear identify on a
     held bag (free). Server Setup -> Gear -> Loot: 16 rows (below); new keys = no one-time update (a missing line means its default).
 11. EXPLOITS (spec section 9): a modded client sees nothing (no item, no seed, no key); no coin loop (re-rolls only take coins, x5 ladder,
     max 3, no XP, the result is a drop that could already have fallen); no rarity fishing (rarity fixed); bags never stack (MaxStack 1 +
     a nonce); identify / re-identify are one in-place write (the bag and the item never exist together); the mob roll is once per death;
     extra chest bags only on a real fill; capped per hour.
 12. REVIEW FIXES (2026-10-08): a loot-chest stack spread writes the SOURCE slot first (checked), then the bags; a refused bag write puts
     the unwritten items back on the source slot - the chest never holds more items than it had (a failed write can only lose, never
     duplicate). The build asserts no pool item has a sell / salvage price (the re-roll coin loop, U3).
 13. ROLLBACK (no floor pinned yet - the main session adds it to tools/deploy_set.py / HANDOFF): before rolling SkyyGear back to 0.2.10,
     set unid.bags=false (no new bags) and ask players to identify every bag they hold (Identify page; staff: /gear identify) - 0.2.10
     has no Skyy_Unid_Bag_* ids, so a bag left in an inventory, the Vault or an Auction listing becomes an unknown item (what the engine
     does with it is UNVERIFIED - treat it as lost). Rolling back SkyyMobs alone is safe (see its patch).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.10.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.11.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.10"' in s and s.startswith('"""SkyyGear 0.2.10 - build script'), "build_skyygear_0.2.10.py is not the live 0.2.10"
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:200])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.10 - build script (javassist via jpype). GENERATED by tools/gear_0_2_10_patch.py from the LIVE 0.2.9 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.10.py -> SkyyGear/SkyyGear-0.2.10.jar (never --deploy).

0.2.10 = ''', '''"""SkyyGear 0.2.11 - build script (javassist via jpype). GENERATED by tools/gear_0_2_11_patch.py from the LIVE 0.2.10 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.11.py -> SkyyGear/SkyyGear-0.2.11.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.11 = "):].strip() + '''

0.2.10 (the base, everything below is still true unless 0.2.11 above says otherwise):
0.2.10 = ''')
rep('VERSION = "0.2.10"', 'VERSION = "0.2.11"')

# ================================================================================================================ never gear
rep('''NEVER_GEAR = ["Skyy_Sack_", "Skyy_Bag_", "Skyy_Accessory_Bag"]     # Magic Bags, bag upgrade items, the Accessory Bag''',
    '''NEVER_GEAR = ["Skyy_Sack_", "Skyy_Bag_", "Skyy_Accessory_Bag", "Skyy_Unid_"]     # Magic Bags, bag upgrade items, the Accessory Bag, 0.2.11 mystery bags''')

# ================================================================================================================ build time: pool + bag assets
POOL_PY = r'''
# ================================================================= 0.2.11 LOOT ROUND (see the header): the bag pool + the mystery bag assets
import skyyart as SA
LOOT_TOP_DEF = VANILLA_TOP
_RCP_OUT = set(_RECIPE_OUTS) | set(_o for _rid, _o, _m, _r in MAGIC_RECIPES)


def _ltype(i):
    if i.startswith("Weapon_"):
        return "Weapon_" + i.split("_")[1]
    _a = az_get(i, "Armor")
    _sl = _a.get("ArmorSlot") if isinstance(_a, dict) else None
    return ("Armor_" + str(_sl)) if _sl in ("Head", "Chest", "Hands", "Legs") else None


def _lat(i):
    if not i.startswith("Armor_"):
        return 0
    _ss = str(az_get(i, "ItemSoundSetId") or "")
    return 3 if "Cloth" in _ss else (2 if "Leather" in _ss else 1)


LOOT_POOL = []          # (id, type key, armor type 0-3, drop only, band min, band cap)
for _i in _GEAR_AZ:
    if _i.startswith(tuple(FAM_DEV)) or _i.endswith("_NPC") or "_Test" in _i:
        continue
    if str(az_get(_i, "Quality")) in ("Developer", "Debug", "Template", "Technical", "Tool"):
        continue
    _t = _ltype(_i)
    _e, _mn, _cp = band_lookup(BD_ALL, _i)
    assert _t is not None, "a vanilla gear id has no bag type: " + _i
    assert _e is not None, "a vanilla gear id has no level band: " + _i
    LOOT_POOL.append((_i, _t, _lat(_i), _i not in _RCP_OUT, max(1, _mn), max(max(1, _mn), _cp)))
# review (Loot-Round-Revision section 2 / U3, the re-roll coin loop): no pool item carries a sell / salvage price (vanilla gear has no NPC
# value), so no re-roll (>= the identify price x 5) can be paid back by selling its result to an NPC - gear only trades player to player
for _p in LOOT_POOL:
    for _k in ("Value", "SellValue", "Price", "SellPrice", "Salvage", "SalvageValue"):
        assert az_get(_p[0], _k) is None, "U3: %s has a %s - check it against the cheapest re-roll before shipping" % (_p[0], _k)
_TNAME = {"Weapon_Shortbow": "Bow", "Armor_Head": "Helmet", "Armor_Chest": "Chestplate", "Armor_Hands": "Gauntlets", "Armor_Legs": "Leggings"}
LOOT_TYPES = sorted(set(_p[1] for _p in LOOT_POOL if _p[1].startswith("Weapon_"))) + ["Armor_Head", "Armor_Chest", "Armor_Hands", "Armor_Legs"]
assert set(LOOT_TYPES) == set(_p[1] for _p in LOOT_POOL), "every pool type has a bag type"
LOOT_TNAME = [_TNAME.get(_k, _k.split("_", 1)[1]) for _k in LOOT_TYPES]
assert len(LOOT_POOL) >= 250 and len(LOOT_TYPES) == 18, (len(LOOT_POOL), LOOT_TYPES)
assert sum(1 for _p in LOOT_POOL if _p[3]) >= 100, "the drop-only scan found too few ids"
assert all(_p[2] > 0 for _p in LOOT_POOL if _p[1].startswith("Armor_")) and all(_p[2] == 0 for _p in LOOT_POOL if _p[1].startswith("Weapon_"))
# the review list (LOCAL only: models-local/ is git-ignored): the lowest vanilla drop-list zone of every id vs its band start
_ZLOW = {1: 1, 2: 20, 3: 30, 4: 45}
_DZ = {}
for _n in AZ_NAMES:
    if _n.startswith("Server/Drops/") and _n.endswith(".json"):
        _dl = os.path.basename(_n)[:-5]
        _zm = re.match(r"Zone(\d)_", _dl)
        if not _zm:
            continue
        for _m in re.finditer(r'"ItemId"\s*:\s*"([^"]+)"', AZ.read(_n).decode("utf-8-sig")):
            _DZ[_m.group(1)] = min(_DZ.get(_m.group(1), 9), int(_zm.group(1)))
_TSV = ["id\ttype\tslot\tarmorType\tsource\tlo\thi\tmethod\tweight\tflag"]
_chk = 0
for _i, _t, _at, _dro, _mn, _cp in LOOT_POOL:
    _z = _DZ.get(_i)
    _flag = ""
    if _z in _ZLOW and abs(_ZLOW[_z] - _mn) > 10:
        _flag = "check (drop list zone %d = Lv %d+)" % (_z, _ZLOW[_z])
        _chk += 1
    _TSV.append("\t".join([_i, _t, _t.split("_", 1)[1] if _t.startswith("Armor_") else "-", ["-", "Heavy", "Light", "Cloth"][_at],
                           "drop" if _dro else "craft", str(_mn), str(_cp), "band", "1", _flag]))
_LDIR = os.path.join(os.path.dirname(HERE), "models-local", "loot")
os.makedirs(_LDIR, exist_ok=True)
with open(os.path.join(_LDIR, "loot-pool-%s.tsv" % VERSION), "w", encoding="utf-8", newline="\n") as _f:
    _f.write("\n".join(_TSV) + "\n")
print("0.2.11 bag pool: %d vanilla gear ids in %d types (%d drop-only, %d flagged 'check'); review list models-local/loot/loot-pool-%s.tsv (local, git-ignored)"
      % (len(LOOT_POOL), len(LOOT_TYPES), sum(1 for _p in LOOT_POOL if _p[3]), _chk, VERSION))

# ---- the 7 mystery bags (one per rarity). ONE-LINE ART SWAP: "placeholder" -> "art/mystery-bags" once Quirk's art lands (ART-RESUME 15)
BAG_ART = "placeholder"
BAG_IDS = ["Skyy_Unid_Bag_" + _n for _n in R_NAMES]
BAG_RAMP = {"normal": ("#8a7a63", "#c9b896", "#f1e6cf"), "unique": ("#8a6d1f", "#d4af37", "#fff2a8"), "rare": ("#6f2a6f", "#b04ab0", "#ff9bff"),
            "legendary": ("#1f5f78", "#3fb4d4", "#a8f4ff"), "fabled": ("#6e1b1b", "#c43a3a", "#ff9a9a"),
            "mythic": ("#4a2a6a", "#9a56c8", "#e6b8ff"), "set": ("#1f5a2a", "#4cae5a", "#b8ffbf")}     # research/cloud/Loot-Box-Design.md 4.1
assert sorted(BAG_RAMP) == sorted(R_IDS)
_BAG_SRC = "Server/Item/Items/Tool/Feedbag/Tool_Feedbag.json"
_bj = json.loads(AZ.read(_BAG_SRC).decode("utf-8-sig"))
BAG_MODEL = _bj["BlockType"]["CustomModel"]
BAG_TEX_SRC = _bj["BlockType"]["CustomModelTexture"][0]["Texture"]
BAG_ICON_SRC = _bj.get("Icon") or "Icons/ItemsGenerated/Tool_Feedbag.png"
BAG_ICONPROPS = _bj["IconProperties"]
for _p in (BAG_MODEL, BAG_TEX_SRC, BAG_ICON_SRC):
    assert ("Common/" + _p) in AZ_NAMES, "the placeholder bag source is gone from Assets.zip: " + _p


def _ramp(hx):
    return tuple(tuple(int(h[k:k + 2], 16) for k in (1, 3, 5)) for h in hx)


BAG_FILES = {}
if BAG_ART == "placeholder":
    _btex, _bico = AZ.read("Common/" + BAG_TEX_SRC), AZ.read("Common/" + BAG_ICON_SRC)
    _bag_model = BAG_MODEL                                   # the vanilla sack model, referenced by path (never copied)
    for _ri, _rid in enumerate(R_IDS):
        BAG_FILES["Common/Items/SkyyGear/Unid/Bag_%s.png" % R_NAMES[_ri]] = SA.recolor(_btex, _ramp(BAG_RAMP[_rid]), rank=0.35)
        BAG_FILES["Common/Icons/ItemsGenerated/%s.png" % BAG_IDS[_ri]] = SA.recolor_icon(_bico, _ramp(BAG_RAMP[_rid]), rank=0.35)
else:
    _adir = os.path.join(os.path.dirname(HERE), *BAG_ART.split("/"))
    _bag_model = "Items/SkyyGear/Unid/Bag.blockymodel"
    BAG_FILES["Common/" + _bag_model] = open(os.path.join(_adir, "bag.blockymodel"), "rb").read()
    for _ri, _rid in enumerate(R_IDS):
        BAG_FILES["Common/Items/SkyyGear/Unid/Bag_%s.png" % R_NAMES[_ri]] = open(os.path.join(_adir, "Bag_%s.png" % R_NAMES[_ri]), "rb").read()
        BAG_FILES["Common/Icons/ItemsGenerated/%s.png" % BAG_IDS[_ri]] = open(os.path.join(_adir, "Bag_%s_Icon.png" % R_NAMES[_ri]), "rb").read()
for _k, _v in BAG_FILES.items():
    assert _k not in AZ_NAMES, "a bag file would shadow a vanilla file: " + _k
    if _k.endswith(".png"):
        _w, _h = SA.png_size(_v)
        assert _w > 0 and _h > 0, _k
BAG_ITEMS = {}
for _ri, _bid in enumerate(BAG_IDS):
    BAG_ITEMS["Server/Item/Items/SkyyGear/%s.json" % _bid] = json.dumps({
        "TranslationProperties": {"Name": "server.items.%s.name" % _bid, "Description": "server.items.%s.description" % _bid},
        "Quality": QUAL_IDS[_ri], "MaxStack": 1, "Variant": True,
        "Icon": "Icons/ItemsGenerated/%s.png" % _bid, "IconProperties": BAG_ICONPROPS,
        "Model": _bag_model, "Texture": "Items/SkyyGear/Unid/Bag_%s.png" % R_NAMES[_ri], "Scale": 1.2,
        "PlayerAnimationsId": "Item", "Tags": {"Type": ["Unidentified"]}}, indent=2)
    assert _bid not in AZ_ITEMS, _bid
BAG_LANG = []
for _ri, _bid in enumerate(BAG_IDS):
    BAG_LANG.append("items.%s.name = %s Mystery Bag" % (_bid, R_NAMES[_ri]))
    BAG_LANG.append("items.%s.description = Unidentified gear - identify it (/identify) to find out what is inside." % _bid)
EXTRA.update(BAG_FILES)
EXTRA.update(BAG_ITEMS)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\n".join(BAG_LANG) + "\n"
print("0.2.11 mystery bags: %d items (%s art), %d files" % (len(BAG_IDS), BAG_ART, len(BAG_FILES)))

'''
rep('''# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
''', POOL_PY + '''# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
''')
rep('''assert not [k for k in EXTRA if k.startswith("Server/Item/Items/")], "no vanilla item file is ever overridden"''',
    '''assert not [k for k in EXTRA if k.startswith("Server/Item/Items/")], "no vanilla item file is ever overridden (0.2.11: the bag items are added later)"''')

# ================================================================================================================ config rows
rep('''CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("combat", "Combat"), ("migrate", "Migration")]''',
    '''CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("combat", "Combat"), ("migrate", "Migration")]''')
LT_ROWS = '''    # 0.2.11 THE LOOT ROUND (Skyy LOCKED 2026-10-08 "yes to all"). New keys: a missing line means its default (no one-time update)
    ("part.lootMob", "Extra mob drops", "loot", "bool", "true", "", "", "", "", "live,part,danger",
     "Each kill of a levelled mob may drop one extra mystery bag. Off = no extra drops.", "field:GearCfg.LOOT_MOB"),
    ("loot.mob.chance", "Extra mob drop chance", "loot", "dec", "6", "0", "100", "", "%", "live,danger",
     "Chance per levelled kill (6 = 1 in 17) of one extra bag." + PH, "field:GearCfg.LOOT_MOB_PCT"),
    ("loot.mob.capPerHour", "Extra mob drops per hour", "loot", "int", "20", "0", "1000", "", "", "live",
     "At most this many extra bags per player in any hour (a safety net).", "field:GearCfg.LOOT_CAP"),
    ("part.lootChest", "Extra bag in loot chests", "loot", "bool", "true", "", "", "", "", "live,part,danger",
     "Fresh world loot chests may get one extra mystery bag at the zone level.", "field:GearCfg.LOOT_CHEST"),
    ("loot.chest.chance", "Extra chest bag chance", "loot", "dec", "33", "0", "100", "", "%", "live,danger",
     "Chance a freshly filled world loot chest gets one extra bag." + PH, "field:GearCfg.LOOT_CHEST_PCT"),
    ("unid.bags", "Gear drops as mystery bags", "loot", "bool", "true", "", "", "", "", "live,part,danger",
     "Single weapons and armor from mobs and fresh chests become bags. Off = the old style.", "field:GearCfg.UNID_BAGS"),
    ("unid.rangeHalf", "Bag level range half width", "loot", "int", "2", "0", "10", "", "", "live",
     "A bag shows Lv L-2 to L+2 around its source level (2 = 5 levels wide).", "field:GearCfg.RANGE_HALF"),
    ("unid.showArmorType", "Show armor type on bags", "loot", "bool", "true", "", "", "", "", "live",
     "Armor bags say Heavy, Light or Cloth armor.", "field:GearCfg.SHOW_AT"),
    ("unid.reroll.max", "Re-identify limit", "loot", "int", "3", "0", "10", "", "", "live",
     "How often an item from a bag can be re-identified (re-rolled).", "field:GearCfg.REROLL_MAX"),
    ("unid.reroll.mult", "Re-identify cost multiplier", "loot", "dec", "5", "1", "100", "", "x", "live,danger",
     "A re-identify costs the identify price x this, per re-roll." + PH, "field:GearCfg.REROLL_MULT"),
    ("loot.armorShare", "Armor share of extra bags", "loot", "int", "50", "0", "100", "", "%", "live",
     "Share of extra bags that are armor; the rest are weapons.", "field:GearCfg.ARMOR_SHARE"),
    ("loot.classLean", "Class weapon lean", "loot", "int", "50", "0", "100", "", "%", "live",
     "Chance an extra weapon bag from a kill is one of the killer's class weapons.", "field:GearCfg.CLASS_LEAN"),
    ("loot.levelTop", "Highest bag level", "loot", "int", "49", "1", "100", "", "", "live",
     "Bags never go above this level (49 = the top of the vanilla bands).", "field:GearCfg.LOOT_TOP"),
    ("loot.dropOnlyWeight", "Drop-only gear weight", "loot", "dec", "1", "0", "100", "", "x", "live",
     "Weight of vanilla gear you cannot craft when a bag picks its item (1 = same).", "field:GearCfg.DROPONLY_W"),
    ("loot.exclude", "Never inside a bag", "loot", "text", "", "0", "2000", "", "", "live,adv",
     "Comma list of item ids (or Prefix*) a bag never turns into.", "field:GearCfg.LOOT_EXCLUDE"),
    ("loot.levelShift", "Mob level rarity boost", "loot", "dec", "0.02", "0", "1", "", "", "live,danger",
     "Mob bags: rarities above Normal weigh x(1 + this x (level - 1))." + PH, "field:GearCfg.LEVEL_SHIFT"),
'''
rep('''    ("gear.signatureKeep", "Keep signature charge on weapon swap", "combat", "bool", "true", "", "", "", "", "live",
     "A weapon keeps its signature (Ability 1) charge when you switch away and back. Off = vanilla reset.", "field:GearCfg.SIG_KEEP"),
''', '''    ("gear.signatureKeep", "Keep signature charge on weapon swap", "combat", "bool", "true", "", "", "", "", "live",
     "A weapon keeps its signature (Ability 1) charge when you switch away and back. Off = vanilla reset.", "field:GearCfg.SIG_KEEP"),
''' + LT_ROWS)
rep('''SG_ROWK = ["gear.signatureKeep"]
''', '''SG_ROWK = ["gear.signatureKeep"]
# 0.2.11: the loot rows of a fresh file (an existing file gets each the first time it is changed in Server Setup)
LT_HEAD = "# ---- loot: mystery bags, extra mob / chest bags, re-identify (SkyyGear 0.2.11) ----"
LT_ROWK = ["part.lootMob", "loot.mob.chance", "loot.mob.capPerHour", "part.lootChest", "loot.chest.chance", "unid.bags", "unid.rangeHalf",
           "unid.showArmorType", "unid.reroll.max", "unid.reroll.mult", "loot.armorShare", "loot.classLean", "loot.levelTop",
           "loot.dropOnlyWeight", "loot.exclude", "loot.levelShift"]
assert all(32 <= ord(_c) < 127 for _c in LT_HEAD) and "=" not in LT_HEAD
''')
rep('''    L += ["", SG_HEAD]         # 0.2.10: the signature-charge row at the very end of a fresh file (no one-time update adds it)
    for k in SG_ROWK:
        scal(k)
''', '''    L += ["", SG_HEAD]         # 0.2.10: the signature-charge row at the very end of a fresh file (no one-time update adds it)
    for k in SG_ROWK:
        scal(k)
    L += ["", LT_HEAD]         # 0.2.11: the loot rows at the very end of a fresh file (no one-time update adds them)
    for k in LT_ROWK:
        scal(k)
''')
rep('''              # 0.2.10 the signature charge kept on a weapon swap
              ("SIG_KEEP", "boolean", "true")]''',
    '''              # 0.2.10 the signature charge kept on a weapon swap
              ("SIG_KEEP", "boolean", "true"),
              # 0.2.11 the loot round
              ("LOOT_MOB", "boolean", "true"), ("LOOT_MOB_PCT", "double", "6.0"), ("LOOT_CAP", "int", "20"),
              ("LOOT_CHEST", "boolean", "true"), ("LOOT_CHEST_PCT", "double", "33.0"), ("UNID_BAGS", "boolean", "true"),
              ("RANGE_HALF", "int", "2"), ("SHOW_AT", "boolean", "true"), ("REROLL_MAX", "int", "3"), ("REROLL_MULT", "double", "5.0"),
              ("ARMOR_SHARE", "int", "50"), ("CLASS_LEAN", "int", "50"), ("LOOT_TOP", "int", str(LOOT_TOP_DEF)),
              ("DROPONLY_W", "double", "1.0"), ("LOOT_EXCLUDE", "String", '""'), ("LEVEL_SHIFT", "double", "0.02")]''')
rep('''  SIG_KEEP = pbool(p, "gear.signatureKeep", true);
''', '''  SIG_KEEP = pbool(p, "gear.signatureKeep", true);
  // 0.2.11 the loot round (Server Setup -> Gear -> Loot)
  LOOT_MOB = pbool(p, "part.lootMob", true);
  LOOT_MOB_PCT = pdec(p, "loot.mob.chance", 6.0, 0.0, 100.0);
  LOOT_CAP = (int) plong(p, "loot.mob.capPerHour", 20L, 0L, 1000L);
  LOOT_CHEST = pbool(p, "part.lootChest", true);
  LOOT_CHEST_PCT = pdec(p, "loot.chest.chance", 33.0, 0.0, 100.0);
  UNID_BAGS = pbool(p, "unid.bags", true);
  RANGE_HALF = (int) plong(p, "unid.rangeHalf", 2L, 0L, 10L);
  SHOW_AT = pbool(p, "unid.showArmorType", true);
  REROLL_MAX = (int) plong(p, "unid.reroll.max", 3L, 0L, 10L);
  REROLL_MULT = pdec(p, "unid.reroll.mult", 5.0, 1.0, 100.0);
  ARMOR_SHARE = (int) plong(p, "loot.armorShare", 50L, 0L, 100L);
  CLASS_LEAN = (int) plong(p, "loot.classLean", 50L, 0L, 100L);
  LOOT_TOP = (int) plong(p, "loot.levelTop", @LOOTTOP@L, 1L, 100L);
  DROPONLY_W = pdec(p, "loot.dropOnlyWeight", 1.0, 0.0, 100.0);
  LOOT_EXCLUDE = ptext(p, "loot.exclude", "").trim();
  LEVEL_SHIFT = pdec(p, "loot.levelShift", 0.02, 0.0, 1.0);
''')
# the apply() source is a template with @...@ tokens filled by .replace in the build; LOOTTOP is filled next to SWODDSDEF
rep('''.replace("@SWODDSDEF@", ''', '''.replace("@LOOTTOP@", str(LOOT_TOP_DEF)).replace("@SWODDSDEF@", ''')

rep('''           # 0.2.6: the weapon speed switch + the tier odds (both change combat numbers / item data)
           "swing.tiers", "swing.odds"}''', '''           # 0.2.6: the weapon speed switch + the tier odds (both change combat numbers / item data)
           "swing.tiers", "swing.odds",
           # 0.2.11: the loot part switches + the numbers that change how many / how good bags are (economy) - confirm in Server Setup
           "part.lootMob", "loot.mob.chance", "part.lootChest", "loot.chest.chance", "unid.bags", "unid.reroll.mult", "loot.levelShift"}''')

# ================================================================================================================ the Java (before GearForge)
LOOT_JAVA = r'''
# ####################################################################################################################################
# 0.2.11 THE LOOT ROUND (see the header): GearPool (the bag candidates), GearUnid (the bags: make / view / identify / re-roll), GearLoot
# (the extra mob roll, the chest level + extra bag, counters), GearBoxFn (gear:fn:box). Methods before callers: everything here only
# calls classes defined above (GearData.put, GearRoll.newDoc, GearLevel.band, GearCfg, GearView) and is called from below.
# ####################################################################################################################################
LT = {"HRC": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
      "RTF": "com.hypixel.hytale.math.vector.Rotation3f",
      "HLDR": "com.hypixel.hytale.component.Holder",
      "ARSL": "com.hypixel.hytale.protocol.ItemArmorSlot"}
for _k in LT:
    assert _k not in T, "0.2.11 token clashes: " + _k
T.update(LT)
for c, m in ((LT["HRC"], "getComponentType"), (LT["HRC"], "getRotation"), (PB["ITC"], "generateItemDrops"), (CB, "addEntities"),
             (PB["DTHC"], "getDeathInfo"), (PB["DMG"], "getSource"), (PB["DENT"], "getRef"), (PB["UUIDC"], "getUuid"), (IAR, "getArmorSlot"),
             (IS, "withMetadata"), (IC, "setItemStackForSlot"), (PLA, "getGameMode"), (ACH, "getComponent")):
    B.probe(pool, c, m)
assert str(pool.get(IAR).getDeclaredMethod("getArmorSlot").getReturnType().getName()) == LT["ARSL"], "ItemArmor.getArmorSlot changed type"
_gid = [m_ for m_ in pool.get(PB["ITC"]).getDeclaredMethods() if str(m_.getName()) == "generateItemDrops"]
assert len(_gid) == 1 and str(_gid[0].getSignature()) == ("(Lcom/hypixel/hytale/component/ComponentAccessor;Ljava/util/List;Lorg/joml/Vector3d;"
                                                          "Lcom/hypixel/hytale/math/vector/Rotation3fc;)[Lcom/hypixel/hytale/component/Holder;"), \
    "ItemComponent.generateItemDrops changed: %s" % [str(m_.getSignature()) for m_ in _gid]
pool.get(LT["RTF"]).getConstructor("(Lcom/hypixel/hytale/math/vector/Rotation3fc;)V")
pool.get("org.joml.Vector3d").getConstructor("(Lorg/joml/Vector3dc;)V")
assert str(pool.get(LT["HRC"]).getDeclaredMethod("getRotation").getReturnType().getName()) == LT["RTF"]

gpool = mk("GearPool")     # the bag candidates (build-time table) + the live bands
gunid = mk("GearUnid")     # the mystery bags
gloot = mk("GearLoot")     # the extra mob roll, the chest level + extra bag, counters
gboxf = mk("GearBoxFn")    # gear:fn:box
LOOT_CLASSES = [gpool, gunid, gloot, gboxf]

# ---------------------------------------------------------------- GearPool
F(gpool, "public static final String[] P_ID = %s;" % jarr([p[0] for p in LOOT_POOL]))
F(gpool, "public static final int[] P_T = %s;" % jints([LOOT_TYPES.index(p[1]) for p in LOOT_POOL]))
F(gpool, "public static final int[] P_AT = %s;" % jints([p[2] for p in LOOT_POOL]))
F(gpool, "public static final boolean[] P_DROP = new boolean[] { %s };" % ", ".join("true" if p[3] else "false" for p in LOOT_POOL))
F(gpool, "public static final String[] T_KEY = %s;" % jarr(LOOT_TYPES))
F(gpool, "public static final String[] T_NAME = %s;" % jarr(LOOT_TNAME))
F(gpool, "public static final boolean[] T_ARM = new boolean[] { %s };" % ", ".join("true" if k.startswith("Armor_") else "false" for k in LOOT_TYPES))
F(gpool, 'public static final String[] AT_NAME = new String[] { "-", "Heavy", "Light", "Cloth" };')
# TAB = { Long cfg epoch, Long built at, boolean[] ok, int[] lo, int[] hi, Integer top, String exclude } (rebuilt after a config change or 60 s)
F(gpool, "public static volatile Object[] TAB = null;")
M(gpool, r"""
public static boolean excluded(String id, String ex) {
  if (id == null || ex == null || ex.length() == 0) return false;
  String[] ps = ex.split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    if (t.endsWith("*")) { if (id.startsWith(t.substring(0, t.length() - 1))) return true; }
    else if (id.equals(t)) return true;
  }
  return false;
}""")
M(gpool, r"""
public static Object[] table() {
  Object[] t = TAB;
  long ep = @PKG@.GearCfg.cfgEpoch();
  long now = System.currentTimeMillis();
  int top = @PKG@.GearCfg.LOOT_TOP;
  String ex = String.valueOf(@PKG@.GearCfg.LOOT_EXCLUDE);
  if (t != null && ((Long) t[0]).longValue() == ep && now - ((Long) t[1]).longValue() < 60000L && now >= ((Long) t[1]).longValue()
      && ((Integer) t[5]).intValue() == top && ex.equals(t[6])) return t;
  int n = P_ID.length;
  boolean[] ok = new boolean[n];
  int[] lo = new int[n];
  int[] hi = new int[n];
  for (int i = 0; i < n; i++) {
    String id = P_ID[i];
    boolean v = false;
    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex); } catch (Throwable x) { v = false; }
    int[] b = @PKG@.GearLevel.band(id);
    int a = b[0] < 1 ? 1 : b[0];
    int c = b[1] < a ? a : b[1];
    if (c > top) c = top;
    if (a > top) v = false;
    ok[i] = v;
    lo[i] = a;
    hi[i] = c;
  }
  t = new Object[] { Long.valueOf(ep), Long.valueOf(now), ok, lo, hi, Integer.valueOf(top), ex };
  TAB = t;
  return t;
}""")
M(gpool, "public static double w(int i) { return P_DROP[i] ? @PKG@.GearCfg.DROPONLY_W : 1.0; }")
# candidate i fits type ty, armor type at (0 = any) and level L (-1 = any level)
M(gpool, r"""
public static boolean match(Object[] t, int i, int ty, int at, int L) {
  if (!((boolean[]) t[2])[i] || P_T[i] != ty || !(w(i) > 0.0)) return false;
  if (at > 0 && P_AT[i] != at) return false;
  return L < 0 || (((int[]) t[3])[i] <= L && L <= ((int[]) t[4])[i]);
}""")
M(gpool, r"""
public static boolean[] levels(int ty, int at) {
  boolean[] out = new boolean[102];
  if (ty < 0 || ty >= T_KEY.length) return out;
  Object[] t = table();
  int[] lo = (int[]) t[3];
  int[] hi = (int[]) t[4];
  for (int i = 0; i < P_ID.length; i++) {
    if (!match(t, i, ty, at, -1)) continue;
    for (int L = lo[i]; L <= hi[i] && L <= 101; L++) if (L >= 0) out[L] = true;
  }
  return out;
}""")
M(gpool, r"""
public static boolean has(int ty, int at, int L) {
  if (L < 1 || L > 101) return false;
  return levels(ty, at)[L];
}""")
M(gpool, r"""
public static int typeIdx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < T_KEY.length; i++) if (T_KEY[i].equals(key)) return i;
  return -1;
}""")
M(gpool, r"""
public static int atIdx(String n) {
  if (n == null) return 0;
  for (int i = 1; i < AT_NAME.length; i++) if (AT_NAME[i].equalsIgnoreCase(n)) return i;
  return 0;
}""")
M(gpool, r"""
public static int idIdx(String id) {
  if (id == null) return -1;
  for (int i = 0; i < P_ID.length; i++) if (P_ID[i].equals(id)) return i;
  return -1;
}""")
# the bag type of a gear id: the pool's own entry, else the family word / the item's armor slot (other mods' gear of a known type)
M(gpool, r"""
public static int typeOfId(String id) {
  int k = idIdx(id);
  if (k >= 0) return P_T[k];
  if (id == null) return -1;
  if (id.startsWith("Weapon_")) {
    String[] p = id.split("_");
    return p.length > 1 ? typeIdx("Weapon_" + p[1]) : -1;
  }
  if (id.startsWith("Armor_")) {
    try {
      @ITM@ it = @PKG@.Gear.item(id);
      @IAR@ a = it == null ? null : it.getArmor();
      @ARSL@ sl = a == null ? null : a.getArmorSlot();
      if (sl != null) return typeIdx("Armor_" + sl.name());
    } catch (Throwable t) { }
  }
  return -1;
}""")
M(gpool, r"""
public static int atOfId(String id) {
  int k = idIdx(id);
  if (k >= 0) return P_AT[k];
  return id != null && id.startsWith("Armor_") ? 1 : 0;
}""")
# { lo, hi, centre }: the nearest level to L (L itself first) with a candidate, the range +-half around it, the ends trimmed inward to
# levels with a candidate; null = the type has no candidate at all
M(gpool, r"""
public static int[] range(int ty, int at, int L, int half) {
  int top = @PKG@.GearCfg.LOOT_TOP;
  if (top > 100) top = 100;
  if (L < 1) L = 1;
  if (L > top) L = top;
  if (half < 0) half = 0;
  boolean[] lv = levels(ty, at);
  int best = -1;
  for (int d = 0; d <= 100 && best < 0; d++) {
    if (L - d >= 1 && lv[L - d]) best = L - d;
    else if (L + d <= top && lv[L + d]) best = L + d;
  }
  if (best < 0) return null;
  int lo = best - half;
  int hi = best + half;
  if (lo < 1) lo = 1;
  if (hi > top) hi = top;
  while (lo < best && !lv[lo]) lo++;
  while (hi > best && !lv[hi]) hi--;
  return new int[] { lo, hi, best };
}""")
M(gpool, r"""
public static int levelCount(int ty, int at, int lo, int hi) {
  boolean[] lv = levels(ty, at);
  int n = 0;
  for (int L = lo; L <= hi; L++) if (L >= 1 && L <= 101 && lv[L]) n++;
  return n;
}""")
M(gpool, r"""
public static int pickLevel(int ty, int at, int lo, int hi) {
  boolean[] lv = levels(ty, at);
  int n = 0;
  for (int L = lo; L <= hi; L++) if (L >= 1 && L <= 101 && lv[L]) n++;
  if (n == 0) return -1;
  int k = @PKG@.GearRoll.RNG.nextInt(n);
  for (int L = lo; L <= hi; L++) {
    if (L < 1 || L > 101 || !lv[L]) continue;
    if (k == 0) return L;
    k--;
  }
  return -1;
}""")
M(gpool, r"""
public static int candidates(int ty, int at, int L) {
  Object[] t = table();
  int n = 0;
  for (int i = 0; i < P_ID.length; i++) if (match(t, i, ty, at, L)) n++;
  return n;
}""")
M(gpool, r"""
public static String pickItem(int ty, int at, int L) {
  Object[] t = table();
  double sum = 0.0;
  int last = -1;
  for (int i = 0; i < P_ID.length; i++) if (match(t, i, ty, at, L)) { sum = sum + w(i); last = i; }
  if (last < 0 || !(sum > 0.0)) return null;
  double r = @PKG@.GearRoll.RNG.nextDouble() * sum;
  for (int i = 0; i < P_ID.length; i++) {
    if (!match(t, i, ty, at, L)) continue;
    r = r - w(i);
    if (r < 0.0) return P_ID[i];
  }
  return P_ID[last];
}""")
M(gpool, r"""
public static int pickAt(int ty, int L) {
  if (ty < 0 || ty >= T_KEY.length) return -1;
  if (!T_ARM[ty]) return 0;
  boolean[] got = new boolean[4];
  int n = 0;
  for (int at = 1; at <= 3; at++) if (candidates(ty, at, L) > 0) { got[at] = true; n++; }
  if (n == 0) return -1;
  int k = @PKG@.GearRoll.RNG.nextInt(n);
  for (int at = 1; at <= 3; at++) {
    if (!got[at]) continue;
    if (k == 0) return at;
    k--;
  }
  return -1;
}""")
M(gpool, r"""
public static boolean leanHit(String key, String[] lean) {
  if (key == null || lean == null) return false;
  String k = key + "_";
  for (int i = 0; i < lean.length; i++) {
    String q = lean[i] == null ? "" : lean[i].trim();
    if (q.length() > 0 && (k.startsWith(q) || q.startsWith(k))) return true;
  }
  return false;
}""")
M(gpool, r"""
public static int pickType(boolean armor, int L, String[] lean) {
  int[] el = new int[T_KEY.length];
  int n = 0;
  for (int ty = 0; ty < T_KEY.length; ty++) if (T_ARM[ty] == armor && candidates(ty, 0, L) > 0) { el[n] = ty; n++; }
  if (n == 0) return -1;
  if (!armor && lean != null && lean.length > 0 && @PKG@.GearRoll.RNG.nextDouble() * 100.0 < (double) @PKG@.GearCfg.CLASS_LEAN) {
    int[] le = new int[n];
    int m = 0;
    for (int k = 0; k < n; k++) if (leanHit(T_KEY[el[k]], lean)) { le[m] = el[k]; m++; }
    if (m > 0) return le[@PKG@.GearRoll.RNG.nextInt(m)];
  }
  return el[@PKG@.GearRoll.RNG.nextInt(n)];
}""")
M(gpool, r"""
public static String statusText() {
  Object[] t = table();
  boolean[] ok = (boolean[]) t[2];
  int n = 0;
  int d = 0;
  for (int i = 0; i < ok.length; i++) if (ok[i]) { n++; if (P_DROP[i]) d++; }
  return "bag pool " + n + " / " + P_ID.length + " items (" + d + " drop-only) in " + T_KEY.length + " types";
}""")

# ---------------------------------------------------------------- GearUnid (the mystery bags)
F(gunid, 'public static final String KEY = "SkyyUnid";')
F(gunid, 'public static final String PREFIX = "Skyy_Unid_Bag_";')
F(gunid, "public static final String[] BAG = %s;" % jarr(BAG_IDS))
F(gunid, "public static final java.util.concurrent.atomic.AtomicLong MADE = new java.util.concurrent.atomic.AtomicLong();")
F(gunid, "public static final java.util.concurrent.atomic.AtomicLong OPENED = new java.util.concurrent.atomic.AtomicLong();")
F(gunid, "public static final java.util.concurrent.atomic.AtomicLong REROLLED = new java.util.concurrent.atomic.AtomicLong();")
M(gunid, "public static boolean isBox(String id) { return id != null && id.startsWith(PREFIX); }")
M(gunid, r"""
public static @BD@ doc(@IS@ s) {
  if (s == null || s.isEmpty() || !isBox(s.getItemId())) return null;
  @BD@ md = s.getMetadata();
  if (md == null) return null;
  @BV@ v = md.get(KEY);
  return v != null && v.isDocument() ? v.asDocument() : null;
}""")
M(gunid, r"""
public static int rar(@BD@ d) {
  int r = d == null ? 0 : @PKG@.GearDefs.rIndex(@PKG@.GearData.str(d, "r", "normal"));
  return r < 0 ? 0 : r;
}""")
M(gunid, "public static int type(@BD@ d) { return d == null ? -1 : @PKG@.GearPool.typeIdx(@PKG@.GearData.str(d, \"mys\", \"\")); }")
M(gunid, "public static int at(@BD@ d) { return d == null ? 0 : @PKG@.GearPool.atIdx(@PKG@.GearData.str(d, \"at\", \"-\")); }")
M(gunid, "public static int lo(@BD@ d) { return d == null ? 1 : @PKG@.GearData.num(d, \"lo\", 1); }")
M(gunid, "public static int hi(@BD@ d) { int l = lo(d); int h = d == null ? l : @PKG@.GearData.num(d, \"hi\", l); return h < l ? l : h; }")
M(gunid, "public static String typeName(int ty) { return ty < 0 || ty >= @PKG@.GearPool.T_NAME.length ? \"Gear\" : @PKG@.GearPool.T_NAME[ty]; }")
M(gunid, "public static String rangeText(int lo, int hi) { return lo == hi ? \"Lv \" + lo : \"Lv \" + lo + \"-\" + hi; }")
M(gunid, "public static String title(@BD@ d) { return \"Unidentified \" + typeName(type(d)); }")
M(gunid, r"""
public static String titleOf(@IS@ s) {
  @BD@ d = doc(s);
  return d == null ? @PKG@.Gear.itemName(s == null ? null : s.getItemId()) : title(d);
}""")
M(gunid, "public static long cost(@BD@ d) { return d == null ? 0L : @PKG@.GearCfg.costIdentify(rar(d), hi(d)); }")
# the price of re-roll number n + 1 (n done): identify price x mult^(n + 1), capped
M(gunid, r"""
public static long rerollCost(int r, int hi, int n) {
  double c = (double) @PKG@.GearCfg.costIdentify(r, hi);
  for (int i = 0; i <= n && i < 64; i++) c = c * @PKG@.GearCfg.REROLL_MULT;
  if (c > 1.0E15) c = 1.0E15;
  if (c < 0.0) c = 0.0;
  return Math.round(c);
}""")
M(gunid, r"""
public static @MSG@ descMsg(@BD@ d) {
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  int r = rar(d);
  int ty = type(d);
  int at = at(d);
  boolean arm = ty >= 0 && @PKG@.GearPool.T_ARM[ty];
  txt.add(rangeText(lo(d), hi(d)) + "  -  " + @PKG@.GearDefs.R_NAME[r]); col.add(@PKG@.GearDefs.R_HEX[r]);
  if (arm && at > 0 && @PKG@.GearCfg.SHOW_AT) { txt.add(@PKG@.GearPool.AT_NAME[at] + " armor"); col.add(@PKG@.GearDefs.C_LABEL); }
  txt.add("Unidentified - which " + typeName(ty).toLowerCase() + " it is, its exact level and its modifiers are decided when you identify it."); col.add(@PKG@.GearDefs.C_GRAY);
  txt.add(arm ? "Cannot be worn until identified." : "Cannot be used until identified."); col.add(@PKG@.GearDefs.C_BAD);
  txt.add("Identify: " + (@PKG@.GearCfg.IDENTIFY_CMD ? "/identify" : "at an identifier") + " - " + @PKG@.Gear.fmt(cost(d)) + " coins"); col.add(@PKG@.GearDefs.C_GOLD);
  @MSG@ m = @MSG@.empty();
  for (int i = 0; i < txt.size(); i++) {
    if (i > 0) m.insert(@MSG@.raw("\n"));
    m.insert(@MSG@.raw((String) txt.get(i)).color((String) col.get(i)));
  }
  return m;
}""")
M(gunid, r"""
public static @IS@ view(@IS@ s, @BD@ d) {
  int r = rar(d);
  return s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(@MSG@.raw(title(d)).color(@PKG@.GearDefs.R_HEX[r]), descMsg(d)));
}""")
# a new bag: type ty, armor type at (0 for weapons), rarity r, range lo..hi
M(gunid, r"""
public static @IS@ make(int ty, int at, int r, int lo, int hi, String src, String ls, int tier) {
  if (ty < 0 || ty >= @PKG@.GearPool.T_KEY.length || r < 0 || r >= BAG.length) return null;
  if (lo < 1) lo = 1;
  if (hi < lo) hi = lo;
  @BD@ d = new @BD@();
  d.append("v", new org.bson.BsonInt32(2));
  d.append("mys", new org.bson.BsonString(@PKG@.GearPool.T_KEY[ty]));
  d.append("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[r]));
  d.append("lo", new org.bson.BsonInt32(lo));
  d.append("hi", new org.bson.BsonInt32(hi));
  d.append("at", new org.bson.BsonString(@PKG@.GearPool.T_ARM[ty] && at > 0 && at < 4 ? @PKG@.GearPool.AT_NAME[at] : "-"));
  d.append("src", new org.bson.BsonString(src == null ? "?" : src));
  d.append("ls", new org.bson.BsonString(ls == null ? "?" : ls));
  d.append("tier", new org.bson.BsonInt32(tier));
  d.append("t", new org.bson.BsonInt64(System.currentTimeMillis()));
  d.append("n", new org.bson.BsonInt64(@PKG@.GearRoll.RNG.nextLong()));
  d.append("id", new org.bson.BsonBoolean(false));
  @IS@ s = new @IS@(BAG[r], 1);
  s = s.withMetadata(KEY, (@BV@) d);
  MADE.incrementAndGet();
  return view(s, d);
}""")
# rarity from the odds column (1 mob, 2 chest, 0 craft) with the level boost: every weight above Normal x (1 + levelShift x (shift - 1))
M(gunid, r"""
public static int rarity(int col, int shift) {
  double[] base = col == 1 ? @PKG@.GearCfg.O_MOB : (col == 2 ? @PKG@.GearCfg.O_CHEST : @PKG@.GearCfg.O_CRAFT);
  if (base == null || base.length == 0) return 0;
  double f = 1.0 + @PKG@.GearCfg.LEVEL_SHIFT * (double) (shift > 1 ? shift - 1 : 0);
  double[] w = new double[base.length];
  for (int i = 0; i < base.length; i++) w[i] = i == 0 ? base[i] : base[i] * f;
  int r = @PKG@.GearRoll.pickWeighted(w);
  return r < 0 || r >= BAG.length ? 0 : r;
}""")
# a random bag at level L: type forced (>= 0) or armor / weapon by loot.armorShare (+ the class lean for weapons), armor type by the
# candidates at L, range around L; null = nothing fits
M(gunid, r"""
public static @IS@ roll(int L, int forceType, String src, String ls, int tier, String[] lean, int col, int shift) {
  int top = @PKG@.GearCfg.LOOT_TOP;
  if (L < 1) L = 1;
  if (L > top) L = top;
  int ty = forceType;
  if (ty < 0) {
    boolean armor = @PKG@.GearRoll.RNG.nextDouble() * 100.0 < (double) @PKG@.GearCfg.ARMOR_SHARE;
    ty = @PKG@.GearPool.pickType(armor, L, lean);
    if (ty < 0) ty = @PKG@.GearPool.pickType(!armor, L, lean);
    if (ty < 0) return null;
  }
  int at = @PKG@.GearPool.pickAt(ty, L);
  if (at < 0) at = 0;
  int[] rg = @PKG@.GearPool.range(ty, at, L, @PKG@.GearCfg.RANGE_HALF);
  if (rg == null && at > 0) { at = 0; rg = @PKG@.GearPool.range(ty, 0, L, @PKG@.GearCfg.RANGE_HALF); }
  if (rg == null) return null;
  return make(ty, at, rarity(col, shift), rg[0], rg[1], src, ls, tier);
}""")
# a single undocumented vanilla gear item -> a bag of ITS type + armor type (col 1 mob drop, 2 chest; L < 1 = the item's band start)
M(gunid, r"""
public static @IS@ fromItem(@IS@ s, int col, int L, String ls) {
  if (s == null || s.isEmpty() || s.getQuantity() != 1 || !@PKG@.GearCfg.UNID_BAGS) return null;
  String id = s.getItemId();
  if (!@PKG@.GearData.isGear(id) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return null;
  int ty = @PKG@.GearPool.typeOfId(id);
  if (ty < 0) return null;
  int at = @PKG@.GearPool.atOfId(id);
  int lv = L;
  String src = ls;
  if (lv < 1) {
    int[] b = @PKG@.GearLevel.band(id);
    lv = b[0] < 1 ? 1 : b[0];
    src = "band";
  }
  int[] rg = @PKG@.GearPool.range(ty, at, lv, @PKG@.GearCfg.RANGE_HALF);
  if (rg == null && at > 0) { at = 0; rg = @PKG@.GearPool.range(ty, 0, lv, @PKG@.GearCfg.RANGE_HALF); }
  if (rg == null) return null;
  return make(ty, at, rarity(col, col == 1 ? lv : 0), rg[0], rg[1], col == 1 ? "drop" : "chest", src, 0);
}""")
# why a bag cannot be opened now (null = it can): unreadable, newer schema, unknown type, no candidate in its range
M(gunid, r"""
public static String why(@BD@ d) {
  if (d == null) return "This bag's data is unreadable - an admin can check it with /gear read.";
  if (@PKG@.GearData.num(d, "v", 2) > 2) return "This bag comes from a newer SkyyGear - it cannot be opened here.";
  int ty = type(d);
  if (ty < 0) return "This bag holds a kind of gear this server does not have any more - an admin can help.";
  if (@PKG@.GearPool.levelCount(ty, at(d), lo(d), hi(d)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";
  return null;
}""")
M(gunid, r"""
public static @BD@ boxSub(int ty, int at, int r, int lo, int hi, int n) {
  @BD@ b = new @BD@();
  b.append("mys", new org.bson.BsonString(@PKG@.GearPool.T_KEY[ty]));
  b.append("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[r]));
  b.append("lo", new org.bson.BsonInt32(lo));
  b.append("hi", new org.bson.BsonInt32(hi));
  b.append("at", new org.bson.BsonString(at > 0 && at < 4 ? @PKG@.GearPool.AT_NAME[at] : "-"));
  b.append("n", new org.bson.BsonInt32(n));
  return b;
}""")
# the item behind a bag / a re-roll: { String id, Integer level, BD document, IS stack } or null (no candidate)
M(gunid, r"""
public static Object[] pick(int ty, int at, int r, int lo, int hi, int n, java.util.UUID by) {
  if (ty < 0) return null;
  int L = @PKG@.GearPool.pickLevel(ty, at, lo, hi);
  if (L < 0) return null;
  String id = @PKG@.GearPool.pickItem(ty, at, L);
  if (id == null) return null;
  @BD@ nd = @PKG@.GearRoll.newDoc(id, r, true, "box", L);
  long now = System.currentTimeMillis();
  nd.put("idAt", new org.bson.BsonInt64(now));
  if (by != null) nd.put("idBy", new org.bson.BsonString(by.toString()));
  nd.put("box", boxSub(ty, at, r, lo, hi, n));
  @IS@ ns = @PKG@.GearData.put(new @IS@(id, 1), nd, by);
  return new Object[] { id, Integer.valueOf(L), nd, ns };
}""")
M(gunid, "public static Object[] open(@BD@ d, java.util.UUID by) { if (d == null) return null; return pick(type(d), at(d), rar(d), lo(d), hi(d), 0, by); }")
# re-roll: the box sub-document of an identified item from a bag
M(gunid, r"""
public static @BD@ boxOf(@BD@ gearDoc) {
  if (gearDoc == null) return null;
  @BV@ v = gearDoc.get("box");
  return v != null && v.isDocument() ? v.asDocument() : null;
}""")
M(gunid, r"""
public static @BD@ rerollDoc(@IS@ s) {
  if (s == null || s.isEmpty()) return null;
  String id = s.getItemId();
  if (!@PKG@.GearData.isGear(id)) return null;
  @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
  if (d == null || !@PKG@.GearData.identified(d)) return null;
  return boxOf(d) == null ? null : d;
}""")
M(gunid, "public static boolean rerollable(@IS@ s) { return rerollDoc(s) != null; }")
M(gunid, "public static int rerolls(@BD@ b) { return b == null ? 0 : @PKG@.GearData.num(b, \"n\", 0); }")
M(gunid, r"""
public static long rerollCostOf(@BD@ gearDoc) {
  @BD@ b = boxOf(gearDoc);
  if (b == null) return 0L;
  return rerollCost(rar(b), hi(b), rerolls(b));
}""")
M(gunid, r"""
public static String rerollWhy(@BD@ gearDoc) {
  @BD@ b = boxOf(gearDoc);
  if (b == null) return "Only items that came out of a mystery bag can be re-identified.";
  if (rerolls(b) >= @PKG@.GearCfg.REROLL_MAX) return "This item was re-identified " + rerolls(b) + " times - that is the limit (" + @PKG@.GearCfg.REROLL_MAX + ").";
  int ty = type(b);
  if (ty < 0) return "This kind of gear does not exist here any more.";
  if (@PKG@.GearPool.levelCount(ty, at(b), lo(b), hi(b)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";
  return null;
}""")
M(gunid, r"""
public static Object[] reroll(@BD@ gearDoc, java.util.UUID by) {
  @BD@ b = boxOf(gearDoc);
  if (b == null) return null;
  return pick(type(b), at(b), rar(b), lo(b), hi(b), rerolls(b) + 1, by);
}""")
# gear:fn:describe / rollsLine / rarity / level / identified / sig for a bag (the AH and other mods read bags through them)
M(gunid, r"""
public static Object fnBox(int m, String id, @BD@ md) {
  @BV@ v = md == null ? null : md.get(KEY);
  @BD@ d = v != null && v.isDocument() ? v.asDocument() : null;
  if (d == null) return null;
  int r = rar(d);
  if (m == 0) return new String[] { title(d), rangeText(lo(d), hi(d)) + " - " + @PKG@.GearDefs.R_NAME[r] + " - unidentified" };
  if (m == 1) return @PKG@.GearDefs.R_NAME[r] + " - " + rangeText(lo(d), hi(d)) + " - unidentified";
  if (m == 2) return @PKG@.GearDefs.R_ID[r];
  if (m == 3) return Integer.valueOf(lo(d));
  if (m == 4) return Boolean.FALSE;
  if (m == 5) return id + "|bag|" + @PKG@.GearDefs.R_ID[r] + "|" + @PKG@.GearData.str(d, "mys", "?") + "|" + lo(d) + "-" + hi(d) + "|" + @PKG@.GearData.str(d, "at", "-");
  return null;
}""")
M(gunid, r"""
public static String logText(@IS@ s) {
  @BD@ d = doc(s);
  if (d == null) return s == null ? "?" : s.getItemId();
  return s.getItemId() + " " + @PKG@.GearData.str(d, "mys", "?") + " " + @PKG@.GearData.str(d, "r", "?") + " lv" + lo(d) + "-" + hi(d) + " " + @PKG@.GearData.str(d, "at", "-") + " " + @PKG@.GearData.str(d, "src", "?") + "/" + @PKG@.GearData.str(d, "ls", "?");
}""")

# ---------------------------------------------------------------- GearLoot (extra mob roll, chest level + extra bag, counters)
F(gloot, "public static final java.util.concurrent.ConcurrentHashMap ROLLED = new java.util.concurrent.ConcurrentHashMap();")
F(gloot, "public static final java.util.concurrent.ConcurrentHashMap HOUR = new java.util.concurrent.ConcurrentHashMap();")
# 0 kills seen, 1 rolls won, 2 dropped, 3 cap reached, 4 nothing fits, 5 chest extras, 6 chest full, 7 bags converted (mob), 8 (chest)
F(gloot, "public static final long[] N = new long[9];")
# the harness seam (null in the game): when set, the extra mob bag is handed to it instead of the engine's generateItemDrops + addEntities
# (the real lines are checked by bytecode against NPCDamageSystems$DropDeathItems in the harness)
F(gloot, "public static volatile java.util.function.BiFunction SPAWN = null;")
M(gloot, "public static synchronized void count(int i) { if (i >= 0 && i < N.length) N[i] = N[i] + 1L; }")
M(gloot, r"""
public static int mobLevel(@ACH@ chunk, int idx, String wk) {
  try {
    @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return -1;
    java.util.function.Function f = @PKG@.Gear.fn("mob:fn:level");
    if (f == null) return -1;
    Object r = f.apply(new Object[] { wk, uc.getUuid() });
    return r instanceof Integer ? ((Integer) r).intValue() : -1;
  } catch (Throwable t) { return -1; }
}""")
# the killer: Damage$EntitySource (projectiles by their shooter) whose Ref is live and in the SAME store
M(gloot, r"""
public static @REF@ killer(@DTHC@ dc, @ST@ store) {
  try {
    @DMG@ d = dc == null ? null : dc.getDeathInfo();
    if (d == null) return null;
    Object src = d.getSource();
    if (!(src instanceof @DENT@)) return null;
    @REF@ r = ((@DENT@) src).getRef();
    if (r == null || !r.isValid() || r.getStore() != store) return null;
    return r;
  } catch (Throwable t) { return null; }
}""")
M(gloot, r"""
public static boolean capOk(java.util.UUID u, long now) {
  if (u == null) return false;
  if (@PKG@.Gear.admin(u)) return true;
  int cap = @PKG@.GearCfg.LOOT_CAP;
  if (cap <= 0) return false;
  java.util.ArrayList l = (java.util.ArrayList) HOUR.get(u);
  if (l == null) {
    l = new java.util.ArrayList();
    Object prev = HOUR.putIfAbsent(u, l);
    if (prev != null) l = (java.util.ArrayList) prev;
  }
  synchronized (l) {
    for (int i = l.size() - 1; i >= 0; i--) if (now - ((Long) l.get(i)).longValue() >= 3600000L || ((Long) l.get(i)).longValue() > now) l.remove(i);
    if (l.size() >= cap) return false;
    l.add(Long.valueOf(now));
  }
  return true;
}""")
M(gloot, r"""
public static void prune(long now) {
  if (ROLLED.size() < 256) return;
  Object[] ks = ROLLED.keySet().toArray();
  for (int i = 0; i < ks.length; i++) {
    Object v = ROLLED.get(ks[i]);
    if (v instanceof Long && now - ((Long) v).longValue() > 60000L) ROLLED.remove(ks[i]);
  }
  if (HOUR.size() > 4096) HOUR.clear();
}""")
# the killer's class weapon prefixes (enabled classes only: class:list), null = no lean
M(gloot, r"""
public static String[] lean(java.util.UUID u) {
  try {
    Object c = @PKG@.Gear.bget("class:" + u);
    if (!(c instanceof String) || ((String) c).length() == 0) return null;
    Object list = @PKG@.Gear.bget("class:list");
    if (list instanceof String && ("," + (String) list + ",").indexOf("," + (String) c + ":") < 0) return null;
    Object w = @PKG@.Gear.bget("class:weapons:" + (String) c);
    if (!(w instanceof String) || ((String) w).trim().length() == 0) return null;
    return ((String) w).split(",");
  } catch (Throwable t) { return null; }
}""")
# the extra mob roll (spec 3.1-3.4): called from GearDeathMark for a death DropDeathItems handles this tick (its condition is checked
# there); the spawn is vanilla's own recipe, so the bag drops beside the mob's own loot
M(gloot, r"""
public static int mobRoll(@ACH@ chunk, int idx, @ST@ store, @CB@ cb, @DTHC@ dc, @VEC@ p, int lvl, String wk) {
  if (!@PKG@.GearCfg.LOOT_MOB || lvl < 1 || p == null) return 0;
  if (chunk.getComponent(idx, @PLA@.getComponentType()) != null) return 0;
  @HRC@ hr = (@HRC@) chunk.getComponent(idx, @HRC@.getComponentType());
  if (hr == null) return 0;
  @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
  java.util.UUID nu = uc == null ? null : uc.getUuid();
  if (nu == null) return 0;
  long now = System.currentTimeMillis();
  prune(now);
  if (ROLLED.putIfAbsent(nu, Long.valueOf(now)) != null) return 0;
  @REF@ kr = killer(dc, store);
  if (kr == null) return 0;
  @PR@ kp = (@PR@) store.getComponent(kr, @PR@.getComponentType());
  if (kp == null) return 0;
  @PLA@ pl = (@PLA@) store.getComponent(kr, @PLA@.getComponentType());
  try { if (pl != null && pl.getGameMode() == @GM@.Creative) return 0; } catch (Throwable tg) { }
  java.util.UUID ku = kp.getUuid();
  count(0);
  if (!(@PKG@.GearRoll.RNG.nextDouble() * 100.0 < @PKG@.GearCfg.LOOT_MOB_PCT)) return 0;
  count(1);
  if (!capOk(ku, now)) {
    count(3);
    @PKG@.GearLog.line("LOOT xmob-cap " + kp.getUsername() + " " + ku + " Lv" + lvl + " (cap " + @PKG@.GearCfg.LOOT_CAP + " an hour reached)");
    return 0;
  }
  @IS@ box = @PKG@.GearUnid.roll(lvl, -1, "mob", "mob", 0, lean(ku), 1, lvl);
  if (box == null) { count(4); return 0; }
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(box);
  @VEC@ at = new @VEC@(p);
  at = at.add(0.0, 1.0, 0.0);
  java.util.function.BiFunction seam = SPAWN;
  if (seam != null) {
    seam.apply(box, at);
    count(2);
    @PKG@.GearLog.line("LOOT xmob " + kp.getUsername() + " " + ku + " Lv" + lvl + " -> " + @PKG@.GearUnid.logText(box) + " (test seam)");
    return 1;
  }
  @HLDR@[] hs = @ITC@.generateItemDrops(store, l, at, new @RTF@(hr.getRotation()));
  if (hs == null || hs.length == 0) { count(4); return 0; }
  cb.addEntities(hs, @ADDR@.SPAWN);
  count(2);
  @PKG@.GearLog.line("LOOT xmob " + kp.getUsername() + " " + ku + " Lv" + lvl + " -> " + @PKG@.GearUnid.logText(box) + " " + wk + " " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z));
  return 1;
}""")
# the zone level of a chest: { level, source 1 = mob:fn:levelAt, 2 = the drop list's Zone<N> band } or null
M(gloot, r"""
public static int[] chestLevel(String wk, int x, int y, int z, String dl) {
  int top = @PKG@.GearCfg.LOOT_TOP;
  try {
    java.util.function.Function f = @PKG@.Gear.fn("mob:fn:levelAt");
    if (f != null && wk != null) {
      Object r = f.apply(new Object[] { wk, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) });
      if (r instanceof Object[] && ((Object[]) r).length >= 2 && ((Object[]) r)[0] instanceof Integer && ((Object[]) r)[1] instanceof Integer) {
        int a = ((Integer) ((Object[]) r)[0]).intValue();
        int b = ((Integer) ((Object[]) r)[1]).intValue();
        if (b < a) b = a;
        if (a >= 1) {
          int L = a + @PKG@.GearRoll.RNG.nextInt(b - a + 1);
          return new int[] { L > top ? top : L, 1 };
        }
      }
    }
  } catch (Throwable t) { }
  if (dl != null && dl.length() > 5 && dl.startsWith("Zone") && dl.charAt(4) >= '1' && dl.charAt(4) <= '4' && (dl.length() == 5 || dl.charAt(5) == '_')) {
    int zn = dl.charAt(4) - '0';
    int a = zn == 1 ? 1 : (zn == 2 ? 20 : (zn == 3 ? 30 : 45));
    int b = zn == 1 ? 20 : (zn == 2 ? 30 : (zn == 3 ? 45 : 60));
    int L = a + @PKG@.GearRoll.RNG.nextInt(b - a + 1);
    return new int[] { L > top ? top : L, 2 };
  }
  return null;
}""")
# the extra bag of a freshly filled world loot chest (into a random EMPTY slot; none = no bag)
M(gloot, r"""
public static int chestExtra(@IC@ c, int L, String where) {
  if (!@PKG@.GearCfg.LOOT_CHEST || c == null || L < 1) return 0;
  if (!(@PKG@.GearRoll.RNG.nextDouble() * 100.0 < @PKG@.GearCfg.LOOT_CHEST_PCT)) return 0;
  int cap = c.getCapacity();
  int[] em = new int[cap > 0 ? cap : 1];
  int n = 0;
  for (int i = 0; i < cap; i++) {
    @IS@ s = c.getItemStack((short) i);
    if (s == null || s.isEmpty()) { em[n] = i; n++; }
  }
  if (n == 0) { count(6); @PKG@.GearLog.line("LOOT xchest-full " + where + " Lv" + L); return 0; }
  @IS@ box = @PKG@.GearUnid.roll(L, -1, "chest", "zone", 0, null, 2, 0);
  if (box == null) { count(4); return 0; }
  int slot = em[@PKG@.GearRoll.RNG.nextInt(n)];
  Object tx = c.setItemStackForSlot((short) slot, box);
  if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) return 0;
  count(5);
  @PKG@.GearLog.line("LOOT xchest " + where + " Lv" + L + " -> " + @PKG@.GearUnid.logText(box));
  return 1;
}""")
M(gloot, r"""
public static String statusText() {
  return "loot: extra mob bags " + (@PKG@.GearCfg.LOOT_MOB ? @PKG@.GearCfg.LOOT_MOB_PCT + "%" : "off") + " (cap " + @PKG@.GearCfg.LOOT_CAP + "/h), extra chest bags "
    + (@PKG@.GearCfg.LOOT_CHEST ? @PKG@.GearCfg.LOOT_CHEST_PCT + "%" : "off") + ", drops as bags " + (@PKG@.GearCfg.UNID_BAGS ? "on" : "off") + ", re-identify x"
    + @PKG@.GearCfg.REROLL_MULT + " max " + @PKG@.GearCfg.REROLL_MAX + "; " + @PKG@.GearPool.statusText();
}""")
M(gloot, r"""
public static synchronized String countsText() {
  return "kills seen " + N[0] + ", rolls won " + N[1] + ", bags dropped " + N[2] + ", hourly cap hits " + N[3] + ", nothing fit " + N[4]
    + "; chest extras " + N[5] + " (full: " + N[6] + "); vanilla gear turned into bags: mobs " + N[7] + ", chests " + N[8]
    + "; bags made " + @PKG@.GearUnid.MADE.get() + ", identified " + @PKG@.GearUnid.OPENED.get() + ", re-identified " + @PKG@.GearUnid.REROLLED.get();
}""")

# ---------------------------------------------------------------- GearBoxFn: gear:fn:box (never throws, never touches ECS)
# Object[] { String typeKey | ItemStack (a single undocumented vanilla gear item) | null, Number level, String src, Number tier, UUID player | null }
gboxf.addInterface(pool.get("java.util.function.Function"))
C(gboxf, "public GearBoxFn() { }")
M(gboxf, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[1] instanceof Number)) return null;
    int L = ((Number) a[1]).intValue();
    String src = a.length > 2 && a[2] instanceof String ? (String) a[2] : "bridge";
    int tier = a.length > 3 && a[3] instanceof Number ? ((Number) a[3]).intValue() : 0;
    if (tier < 0) tier = 0;
    if (tier > 4) tier = 4;
    if (L < 1) return null;
    int shift = tier >= 4 ? 21 : (tier >= 3 ? 11 : 0);
    if (a[0] instanceof @IS@) {
      @IS@ s = (@IS@) a[0];
      if (s.isEmpty() || s.getQuantity() != 1 || !@PKG@.GearData.isGear(s.getItemId()) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return null;
      int ty0 = @PKG@.GearPool.typeOfId(s.getItemId());
      if (ty0 < 0) return null;
      int at0 = @PKG@.GearPool.atOfId(s.getItemId());
      int[] rg = @PKG@.GearPool.range(ty0, at0, L, @PKG@.GearCfg.RANGE_HALF);
      if (rg == null) return null;
      return @PKG@.GearUnid.make(ty0, at0, @PKG@.GearUnid.rarity(2, shift), rg[0], rg[1], src, "bridge", tier);
    }
    int ty = a[0] instanceof String ? @PKG@.GearPool.typeIdx((String) a[0]) : -1;
    if (a[0] instanceof String && ty < 0) return null;
    return @PKG@.GearUnid.roll(L, ty, src, "bridge", tier, null, 2, shift);
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("boxfn", "gear:fn:box failed: " + t);
    return null;
  }
}""")

'''
rep('''# ================================================================= GearForge: the reforge core (spec 5.4 + write safety 1.7)
''', LOOT_JAVA + '''# ================================================================= GearForge: the reforge core (spec 5.4 + write safety 1.7)
''')

# ================================================================================================================ fingerprint: bags too
rep('''  String dj = g != null && g.isDocument() ? g.asDocument().toJson() : (r != null && r.isDocument() ? "R" + r.asDocument().toJson() : "none");''',
    '''  String dj = g != null && g.isDocument() ? g.asDocument().toJson() : (r != null && r.isDocument() ? "R" + r.asDocument().toJson() : "none");
  // 0.2.11: a mystery bag's own document (its nonce makes every bag's fingerprint unique)
  if (g == null && r == null) { @BV@ ub = @PKG@.GearData.getv(md, @PKG@.GearUnid.KEY); if (ub != null && ub.isDocument()) dj = "U" + ub.asDocument().toJson(); }''')

# ================================================================================================================ gear:fn:* answer for bags
rep('''    Object[] xs = x(o);
    @BD@ d = docOf(xs);
    if (d == null) {
      if (m == 0 && xs != null''', '''    Object[] xs = x(o);
    // 0.2.11: a mystery bag answers describe / rollsLine / rarity / level / identified / sig from its own document
    if (m <= 5 && xs != null && @PKG@.GearUnid.isBox((String) xs[0])) return @PKG@.GearUnid.fnBox(m, (String) xs[0], (@BD@) xs[1]);
    @BD@ d = docOf(xs);
    if (d == null) {
      if (m == 0 && xs != null''')

# ================================================================================================================ GearTag: levels on the marks, bags
rep('''M(gtag, r"""
public static void mark(String k, double x, double y, double z) {
  if (k == null) return;
  java.util.ArrayList l = (java.util.ArrayList) MARKS.get(k);
  if (l == null) { l = new java.util.ArrayList(); MARKS.put(k, l); }
  if (l.size() < 4096) l.add(new double[] { x, y, z });
}""")''', '''# 0.2.11: a mark carries the dying mob's level (mob:fn:level, -1 = none) for the bag its own gear becomes
M(gtag, r"""
public static void mark(String k, double x, double y, double z, int lvl) {
  if (k == null) return;
  java.util.ArrayList l = (java.util.ArrayList) MARKS.get(k);
  if (l == null) { l = new java.util.ArrayList(); MARKS.put(k, l); }
  if (l.size() < 4096) l.add(new double[] { x, y, z, (double) lvl });
}""")
M(gtag, "public static void mark(String k, double x, double y, double z) { mark(k, x, y, z, -1); }")''')
rep('''    if (dx * dx + dy * dy + dz * dz <= 4.0) return true;
  }
  return false;
}""")''', '''    if (dx * dx + dy * dy + dz * dz <= 4.0) return true;
  }
  return false;
}""")
# 0.2.11: the level of the nearest mark within 2 blocks (-1 = none / no level)
M(gtag, r"""
public static int levelNear(String k, double x, double y, double z) {
  Object o = k == null ? null : MARKS.get(k);
  if (!(o instanceof java.util.ArrayList)) return -1;
  java.util.ArrayList l = (java.util.ArrayList) o;
  int best = -1;
  double bd = 5.0;
  for (int i = 0; i < l.size(); i++) {
    double[] p = (double[]) l.get(i);
    double dx = p[0] - x;
    double dy = p[1] - y;
    double dz = p[2] - z;
    double d2 = dx * dx + dy * dy + dz * dz;
    if (d2 <= 4.0 && d2 < bd && p.length > 3) { bd = d2; best = (int) p[3]; }
  }
  return best;
}""")''')
rep('''M(gtag, r"""
public static @IS@ unid(@IS@ s, int col) {
  if (s == null || s.isEmpty()) return s;
  String id = s.getItemId();
  if (!@PKG@.GearData.isGear(id) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return s;
  if (col == 1 && !@PKG@.GearCfg.PART_DROPS) return s;
  if (col == 2 && !@PKG@.GearCfg.PART_CHESTS) return s;
  if (col != 1 && col != 2) return s;
  return @PKG@.GearData.put(s, @PKG@.GearRoll.unidDoc(id, col, col == 1 ? "drop" : "chest"), null);
}""")''', '''# 0.2.11: a single item becomes a MYSTERY BAG of its type at level lvl (unid.bags on; lvl < 1 = its band start); a stack keeps 0.2's doc
M(gtag, r"""
public static @IS@ unid(@IS@ s, int col, int lvl, String ls) {
  if (s == null || s.isEmpty()) return s;
  String id = s.getItemId();
  if (!@PKG@.GearData.isGear(id) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return s;
  if (col == 1 && !@PKG@.GearCfg.PART_DROPS) return s;
  if (col == 2 && !@PKG@.GearCfg.PART_CHESTS) return s;
  if (col != 1 && col != 2) return s;
  if (@PKG@.GearCfg.UNID_BAGS && s.getQuantity() == 1) {
    @IS@ b = @PKG@.GearUnid.fromItem(s, col, lvl, ls);
    if (b != null) { @PKG@.GearLoot.count(col == 1 ? 7 : 8); return b; }
  }
  return @PKG@.GearData.put(s, @PKG@.GearRoll.unidDoc(id, col, col == 1 ? "drop" : "chest"), null);
}""")
M(gtag, "public static @IS@ unid(@IS@ s, int col) { return unid(s, col, -1, null); }")
# 0.2.11: a loot-chest stack of N undocumented gear items -> one bag per item into EMPTY slots of the same chest (the rest stays the stack)
M(gtag, r"""
public static int spread(@IC@ c, int slot, int lvl, String ls) {
  if (c == null || !@PKG@.GearCfg.UNID_BAGS) return 0;
  @IS@ s0 = c.getItemStack((short) slot);
  if (s0 == null || s0.isEmpty() || s0.getQuantity() <= 1 || !@PKG@.GearData.isGear(s0.getItemId()) || @PKG@.GearData.hasAnyDoc(s0.getMetadata())) return 0;
  if (@PKG@.GearPool.typeOfId(s0.getItemId()) < 0) return 0;
  int q = s0.getQuantity();
  String gid = s0.getItemId();
  // review fix: the SOURCE slot is written first (checked) and holds what is left; a bag write that fails puts the unwritten items back
  // on it - the chest never holds more than the q items it had (a failed write can only lose, never add)
  int[] tg = new int[q - 1];
  int m = 0;
  for (int i = 0; i < c.getCapacity() && m < q - 1; i++) {
    if (i == slot) continue;
    @IS@ e = c.getItemStack((short) i);
    if (e != null && !e.isEmpty()) continue;
    tg[m] = i;
    m++;
  }
  if (m == 0) return 0;
  int rest = q - m;
  @IS@ head = rest == 1 ? @PKG@.GearUnid.fromItem(new @IS@(gid, 1), 2, lvl, ls) : null;
  boolean headBag = head != null;
  Object t0 = c.setItemStackForSlot((short) slot, headBag ? head : new @IS@(gid, rest));
  if (t0 instanceof @TXN@ && !((@TXN@) t0).succeeded()) return 0;
  int done = 0;
  for (int k = 0; k < m; k++) {
    @IS@ b = @PKG@.GearUnid.fromItem(new @IS@(gid, 1), 2, lvl, ls);
    if (b == null) break;
    Object tx = c.setItemStackForSlot((short) tg[k], b);
    if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) break;
    done++;
  }
  if (done < m) {
    Object t2 = c.setItemStackForSlot((short) slot, new @IS@(gid, rest + (m - done)));
    if (t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) @PKG@.Gear.warn("a loot chest stack of " + gid + " could not be put back after a refused slot write (items lost, never duplicated)");
    headBag = false;
  }
  int bags = done + (headBag ? 1 : 0);
  for (int k = 0; k < bags; k++) @PKG@.GearLoot.count(8);
  return bags;
}""")''')
rep('''M(gtag, r"""
public static int tagContainer(@IC@ c, String where) {
  if (c == null) return 0;
  int n = 0;
  @IC@[] self = new @IC@[] { c };
  for (int i = 0; i < c.getCapacity(); i++) {
    @IS@ s0 = c.getItemStack((short) i);''', '''M(gtag, r"""
public static int tagContainer(@IC@ c, String where, int lvl, String ls) {
  if (c == null) return 0;
  int n = 0;
  @IC@[] self = new @IC@[] { c };
  for (int i = 0; i < c.getCapacity(); i++) {
    if (@PKG@.GearCfg.PART_CHESTS) {
      try { n = n + spread(c, i, lvl, ls); }
      catch (Throwable tsp) { @PKG@.Gear.warnOnce("bagspread", "loot chest bag spread failed (the stack is tagged as before): " + tsp); }
    }
    @IS@ s0 = c.getItemStack((short) i);''')
rep('''    @IS@ s = c.getItemStack((short) i);
    @IS@ ns = unid(s, 2);
    if (ns == s || ns == null) continue;
    c.setItemStackForSlot((short) i, ns);
    n++;
    @BD@ d = @PKG@.GearData.gearDoc(ns.getMetadata());
    @PKG@.GearLog.line("UNID chest " + ns.getItemId() + " " + (d == null ? "?" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]) + " " + where);
  }
  if (n > 0) CHEST_TAGS.addAndGet((long) n);
  return n;
}""")''', '''    @IS@ s = c.getItemStack((short) i);
    @IS@ ns = unid(s, 2, lvl, ls);
    if (ns == s || ns == null) continue;
    c.setItemStackForSlot((short) i, ns);
    n++;
    @BD@ d = @PKG@.GearData.gearDoc(ns.getMetadata());
    @PKG@.GearLog.line("UNID chest " + (@PKG@.GearUnid.isBox(ns.getItemId()) ? "bag " + @PKG@.GearUnid.logText(ns) : ns.getItemId() + " " + (d == null ? "?" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)])) + " " + where);
  }
  if (n > 0) CHEST_TAGS.addAndGet((long) n);
  return n;
}""")
M(gtag, "public static int tagContainer(@IC@ c, String where) { return tagContainer(c, where, -1, null); }")''')

# ================================================================================================================ GearDeathMark + GearDropSys
rep('''public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!@PKG@.GearCfg.PART_DROPS) return;
    @DTHC@ dc = (@DTHC@) chunk.getComponent(idx, @DTHC@.getComponentType());''', '''public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!@PKG@.GearCfg.PART_DROPS && !@PKG@.GearCfg.LOOT_MOB) return;
    @DTHC@ dc = (@DTHC@) chunk.getComponent(idx, @DTHC@.getComponentType());''')
rep('''    @VEC@ p = tc.getPosition();
    @PKG@.GearTag.mark(@PKG@.GearTag.key(store.getExternalData()), p.x, p.y + 1.0, p.z);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("deathmark", "death drop mark failed: " + t); }''', '''    @VEC@ p = tc.getPosition();
    // 0.2.11: the mark carries the mob's level (its own gear becomes a bag at that level); the extra mob roll (part.lootMob)
    String wk = @PKG@.GearTag.key(store.getExternalData());
    int lvl = @PKG@.GearLoot.mobLevel(chunk, idx, wk);
    if (@PKG@.GearCfg.PART_DROPS) @PKG@.GearTag.mark(wk, p.x, p.y + 1.0, p.z, lvl);
    if (@PKG@.GearCfg.LOOT_MOB) {
      try { @PKG@.GearLoot.mobRoll(chunk, idx, store, cb, dc, p, lvl, wk); }
      catch (Throwable tl) { @PKG@.Gear.warnOnce("mobroll", "extra mob drop failed: " + tl); }
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("deathmark", "death drop mark failed: " + t); }''')
rep('''    if (!@PKG@.GearTag.near(k, p.x, p.y, p.z)) return;
    @IS@ ns = @PKG@.GearTag.unid(s, 1);
    if (ns == s || ns == null) return;
    ic.setItemStack(ns);
    @PKG@.GearTag.MOB_TAGS.incrementAndGet();
    @BD@ d = @PKG@.GearData.gearDoc(ns.getMetadata());
    @PKG@.GearLog.line("UNID mob " + ns.getItemId() + " " + (d == null ? "?" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]) + " " + k + " " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z));''',
    '''    if (!@PKG@.GearTag.near(k, p.x, p.y, p.z)) return;
    @IS@ ns = @PKG@.GearTag.unid(s, 1, @PKG@.GearTag.levelNear(k, p.x, p.y, p.z), "mob");
    if (ns == s || ns == null) return;
    ic.setItemStack(ns);
    @PKG@.GearTag.MOB_TAGS.incrementAndGet();
    @BD@ d = @PKG@.GearData.gearDoc(ns.getMetadata());
    @PKG@.GearLog.line("UNID mob " + (@PKG@.GearUnid.isBox(ns.getItemId()) ? "bag " + @PKG@.GearUnid.logText(ns) : ns.getItemId() + " " + (d == null ? "?" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)])) + " " + k + " " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z));''')

# ================================================================================================================ GearChestTag: level + extra bag
rep('''chest_system(gcm2, "GearChestTag", "AFTER", r"""
    String dl = @PKG@.GearTag.chestTake(ref);
    if (dl == null || !@PKG@.GearCfg.PART_CHESTS) return;
    @ICB@ icb = (@ICB@) store.getComponent(ref, @ICB@.getComponentType());
    if (icb == null) return;
    @PKG@.GearTag.tagContainer(icb.getItemContainer(), "droplist " + dl + " in " + @PKG@.GearTag.key(store.getExternalData()));""")''',
    '''chest_system(gcm2, "GearChestTag", "AFTER", r"""
    String dl = @PKG@.GearTag.chestTake(ref);
    if (dl == null || !@PKG@.GearCfg.PART_CHESTS) return;
    @ICB@ icb = (@ICB@) store.getComponent(ref, @ICB@.getComponentType());
    if (icb == null) return;
    // 0.2.11: the chest's zone level (mob:fn:levelAt at its block, else its drop list's zone) for its bags; the extra bag only after a
    // REAL fill (the engine cleared the drop list = once per chest) and never on SkyyIslands island worlds
    String wk = @PKG@.GearTag.key(store.getExternalData());
    int[] pos = null;
    try { pos = @PKG@.GearChestOpen.posOf(store, (@BSI@) store.getComponent(ref, @BSI@.getComponentType())); } catch (Throwable tp) { pos = null; }
    int[] cl = pos == null ? @PKG@.GearLoot.chestLevel(null, 0, 0, 0, dl) : @PKG@.GearLoot.chestLevel(wk, pos[0], pos[1], pos[2], dl);
    int lvl = cl == null ? -1 : cl[0];
    String ls = cl == null ? null : (cl[1] == 1 ? "zone" : "droplist");
    String where = "droplist " + dl + " in " + wk + (pos == null ? "" : " " + pos[0] + " " + pos[1] + " " + pos[2]);
    @PKG@.GearTag.tagContainer(icb.getItemContainer(), where, lvl, ls);
    String after = icb.getDroplist();
    if ((after == null || after.length() == 0) && !@PKG@.GearChestOpen.island(wk)) @PKG@.GearLoot.chestExtra(icb.getItemContainer(), lvl, where);""")''')

# ================================================================================================================ GearIdent: bags + re-identify
IDENT_JAVA = r'''# ---- 0.2.11: bags + re-identify in the identify core (see the header). A bag is identified with the same write safety as gear: same
# fingerprint in the same slot, profile checks, coins FIRST, ONE setItemStackForSlot, refund on failure. Object[] shape = identify()'s.
M(gidn, r"""
public static Object[] identifyBox(@IC@ c, int slot, @IS@ it, java.util.UUID u, String who, boolean free) {
  @BD@ d = @PKG@.GearUnid.doc(it);
  String why = @PKG@.GearUnid.why(d);
  if (why != null) return new Object[] { Integer.valueOf(0), why, null, null, null, Long.valueOf(0L), null };
  if (it.getQuantity() != 1) return new Object[] { Integer.valueOf(0), "Bags never stack - this one is broken; an admin can check it with /gear read.", null, null, null, Long.valueOf(0L), null };
  String id = it.getItemId();
  long cost = free ? 0L : @PKG@.GearUnid.cost(d);
  if (cost > 0L) {
    int t = @PKG@.GearForge.take(u, cost);
    if (t < 0) return new Object[] { Integer.valueOf(0), "Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken.", null, null, null, Long.valueOf(0L), null };
    if (t == 0) {
      long have = @PKG@.GearForge.purse(u);
      return new Object[] { Integer.valueOf(0), "Not enough coins: identifying it costs " + @PKG@.Gear.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Gear.fmt(have) : "") + ".", null, null, null, Long.valueOf(0L), null };
    }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " identify " + @PKG@.GearUnid.logText(it));
  }
  Object[] got = null;
  Object tx = null;
  Throwable err = null;
  try {
    got = @PKG@.GearUnid.open(d, u);
    if (got == null) throw new IllegalStateException("no item fits the bag any more");
    tx = c.setItemStackForSlot((short) slot, (@IS@) got[3]);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && got != null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || @PKG@.GearForge.refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Gear.warn("IDENTIFY FAILED for " + who + " (" + u + ") on " + @PKG@.GearUnid.logText(it) + ": " + what + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " identify " + id + ": " + what);
    return new Object[] { Integer.valueOf(-1), back ? "Identifying failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Gear.fmt(cost) + " coins were refunded." : ".") : "Identifying failed and the refund did not go through - an admin can find it in the server log.", null, null, null, Long.valueOf(cost), null };
  }
  @BD@ nd = (@BD@) got[2];
  @PKG@.GearUnid.OPENED.incrementAndGet();
  @PKG@.GearLog.line("IDENTIFY bag " + who + " " + u + " " + @PKG@.GearUnid.logText(it) + " -> " + got[0] + " lv" + got[1] + " [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost + (free ? " (free)" : ""));
  return new Object[] { Integer.valueOf(1), "Identified!", got[3], null, nd, Long.valueOf(cost), null };
}""")
# re-identify (hotbar / storage / backpack only): the same safety; the rarity stays, the item, level and modifiers are new, n + 1
M(gidn, r"""
public static Object[] reroll(@IC@ c, int slot, String expId, String expFp, java.util.UUID u, String who) {
  @IS@ it = null;
  try { if (c != null && slot >= 0 && slot < c.getCapacity()) it = c.getItemStack((short) slot); } catch (Throwable t0) { it = null; }
  if (!@PKG@.GearForge.same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L), null };
  @BD@ d = @PKG@.GearUnid.rerollDoc(it);
  if (d == null) return new Object[] { Integer.valueOf(0), "Only identified items that came out of a mystery bag can be re-identified.", null, null, null, Long.valueOf(0L), null };
  String why = @PKG@.GearUnid.rerollWhy(d);
  if (why == null && it.getQuantity() != 1) why = "Pick a single item.";
  if (why != null) return new Object[] { Integer.valueOf(0), why, null, null, null, Long.valueOf(0L), null };
  String id = it.getItemId();
  long cost = @PKG@.GearUnid.rerollCostOf(d);
  if (cost > 0L) {
    int t = @PKG@.GearForge.take(u, cost);
    if (t < 0) return new Object[] { Integer.valueOf(0), "Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken.", null, null, null, Long.valueOf(0L), null };
    if (t == 0) {
      long have = @PKG@.GearForge.purse(u);
      return new Object[] { Integer.valueOf(0), "Not enough coins: re-identifying it costs " + @PKG@.Gear.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Gear.fmt(have) : "") + ".", null, null, null, Long.valueOf(0L), null };
    }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " reidentify " + id);
  }
  Object[] got = null;
  Object tx = null;
  Throwable err = null;
  try {
    got = @PKG@.GearUnid.reroll(d, u);
    if (got == null) throw new IllegalStateException("no item fits any more");
    tx = c.setItemStackForSlot((short) slot, (@IS@) got[3]);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && got != null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || @PKG@.GearForge.refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Gear.warn("RE-IDENTIFY FAILED for " + who + " (" + u + ") on " + id + ": " + what + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " reidentify " + id + ": " + what);
    return new Object[] { Integer.valueOf(-1), back ? "Re-identifying failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Gear.fmt(cost) + " coins were refunded." : ".") : "Re-identifying failed and the refund did not go through - an admin can find it in the server log.", null, d, null, Long.valueOf(cost), null };
  }
  @BD@ nd = (@BD@) got[2];
  @PKG@.GearUnid.REROLLED.incrementAndGet();
  @PKG@.GearLog.line("REIDENTIFY " + who + " " + u + " " + id + " -> " + got[0] + " lv" + got[1] + " " + @PKG@.GearData.str(nd, "r", "?") + " re-roll " + @PKG@.GearUnid.rerolls(@PKG@.GearUnid.boxOf(nd)) + " [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost);
  return new Object[] { Integer.valueOf(1), "Re-identified!", got[3], d, nd, Long.valueOf(cost), null };
}""")
# re-identifiable items on the player (hotbar, storage, backpack - never worn armor or tools)
M(gidn, r"""
public static java.util.ArrayList rerollRows(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  int[] secs = new int[] { 0, 1, 2 };
  for (int k = 0; k < secs.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, secs[k]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it != null && !it.isEmpty() && @PKG@.GearUnid.rerollable(it)) out.add(new int[] { secs[k], i });
    }
  }
  return out;
}""")
M(gidn, r"""
public static int rowRarity(@IS@ it, @BD@ d) {
  if (it != null && @PKG@.GearUnid.isBox(it.getItemId())) return @PKG@.GearUnid.rar(@PKG@.GearUnid.doc(it));
  return d == null ? 0 : @PKG@.GearData.rarity(d);
}""")
M(gidn, r"""
public static String rowName(@IS@ it, @BD@ d) {
  String id = it.getItemId();
  if (@PKG@.GearUnid.isBox(id)) return @PKG@.GearUnid.titleOf(it);
  return d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d);
}""")
M(gidn, r"""
public static String rowSub(@IS@ it, @BD@ d, int r, int lvl) {
  if (@PKG@.GearUnid.isBox(it.getItemId())) {
    @BD@ b = @PKG@.GearUnid.doc(it);
    return @PKG@.GearDefs.R_NAME[r] + " - " + @PKG@.GearUnid.rangeText(@PKG@.GearUnid.lo(b), @PKG@.GearUnid.hi(b));
  }
  if (d != null && @PKG@.GearData.identified(d) && @PKG@.GearUnid.boxOf(d) != null)
    return "Re-identify " + @PKG@.GearUnid.rerolls(@PKG@.GearUnid.boxOf(d)) + "/" + @PKG@.GearCfg.REROLL_MAX + " - Lv " + lvl;
  return @PKG@.GearDefs.R_NAME[r] + " - Lv " + lvl;
}""")
'''
rep('''# unidentified gear on the player, in the SCAN order (spec 5.7 page left side)
M(gidn, r"""''', IDENT_JAVA + '''# unidentified gear on the player, in the SCAN order (spec 5.7 page left side)
M(gidn, r"""''')
rep('''      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) continue;
      @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
      if (d == null || @PKG@.GearData.identified(d)) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });''', '''      @IS@ it = c.getItemStack((short) i);
      // 0.2.11: mystery bags are listed with the unidentified gear (bags can only sit in the hotbar, storage and backpack)
      if (it != null && !it.isEmpty() && @PKG@.GearUnid.isBox(it.getItemId())) { out.add(new int[] { @PKG@.GearStamp.SCAN[k], i }); continue; }
      if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) continue;
      @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
      if (d == null || @PKG@.GearData.identified(d)) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });''')
rep('''public static long costOf(@IS@ it) {
  if (it == null || it.isEmpty()) return 0L;
  @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());''', '''public static long costOf(@IS@ it) {
  if (it == null || it.isEmpty()) return 0L;
  if (@PKG@.GearUnid.isBox(it.getItemId())) return @PKG@.GearUnid.cost(@PKG@.GearUnid.doc(it));
  @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());''')
rep('''public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick an unidentified weapon or armor piece first.";
  String id = it.getItemId();''', '''public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick an unidentified weapon or armor piece first.";
  if (@PKG@.GearUnid.isBox(it.getItemId())) return @PKG@.GearUnid.why(@PKG@.GearUnid.doc(it));
  String id = it.getItemId();''')
rep('''  if (!@PKG@.GearForge.same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L), null };
  String id = it.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);''', '''  if (!@PKG@.GearForge.same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L), null };
  if (@PKG@.GearUnid.isBox(it.getItemId())) return identifyBox(c, slot, it, u, who, free);   // 0.2.11: a mystery bag
  String id = it.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);''')
rep('''    String sum = @PKG@.GearView.modSummary((@BD@) res[4]);
    if (recent != null) recent.add(name + ": " + (sum.length() > 0 ? sum : "no modifiers"));''', '''    String sum = @PKG@.GearView.modSummary((@BD@) res[4]);
    // 0.2.11: a bag reveals what it was
    if (res[2] instanceof @IS@ && res[4] instanceof @BD@ && !((@IS@) res[2]).getItemId().equals(it.getItemId())) name = @PKG@.GearView.nameText(((@IS@) res[2]).getItemId(), (@BD@) res[4]);
    if (recent != null) recent.add(name + ": " + (sum.length() > 0 ? sum : "no modifiers"));''')

# ================================================================================================================ IdentifyPage
rep('''for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
           "public String selFp;", "public String info;", "public String epoch;", "public long lastClick;", "public @BD@ revealed;",
           "public java.util.ArrayList recent;"):''', '''for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
           "public String selFp;", "public String info;", "public String epoch;", "public long lastClick;", "public @BD@ revealed;",
           "public java.util.ArrayList recent;",
           # 0.2.11 re-identify: the first click arms (time + fingerprint), the second within 10 s confirms
           "public long rrArm;", "public String rrFp;"):''')
rep('''public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) return false;
  @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
  if (d == null || @PKG@.GearData.identified(d)) return false;''', '''public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  this.rrArm = 0L;
  // 0.2.11: a mystery bag, or an identified item from a bag (re-identify; hotbar / storage / backpack)
  if (it != null && !it.isEmpty() && @PKG@.GearUnid.isBox(it.getItemId())) {
    this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = @PKG@.GearForge.fp(it);
    this.revealed = null;
    this.info = "=" + @PKG@.GearUnid.titleOf(it) + " is selected.";
    return true;
  }
  if (it != null && !it.isEmpty() && (s == 0 || s == 1 || s == 2) && @PKG@.GearUnid.rerollable(it)) {
    @BD@ rd = @PKG@.GearUnid.rerollDoc(it);
    this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = @PKG@.GearForge.fp(it);
    this.revealed = null;
    this.info = "=" + @PKG@.GearView.nameText(it.getItemId(), rd) + " is selected - it came from a mystery bag and can be re-identified.";
    return true;
  }
  if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) return false;
  @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
  if (d == null || @PKG@.GearData.identified(d)) return false;''')
PAGE_JAVA = r'''# 0.2.11: the detail panel of a selected mystery bag (the gear panel's layout and styles, the bag's texts)
M(ipg, r"""
public void detailBox(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  @BD@ d = @PKG@.GearUnid.doc(sel);
  int r = @PKG@.GearUnid.rar(d);
  int ty = @PKG@.GearUnid.type(d);
  int at = @PKG@.GearUnid.at(d);
  int lo = @PKG@.GearUnid.lo(d);
  int hi = @PKG@.GearUnid.hi(d);
  String tn = @PKG@.GearUnid.typeName(ty);
  boolean arm = ty >= 0 && @PKG@.GearPool.T_ARM[ty];
  b.appendInline("#SkyyGMain", "Group #SkyyGDet { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGDet", "Label #SkyyGDetT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGDetT.Text", "Identify");
  b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  b.appendInline("#SkyyGDet", "Group #SkyyGSel { Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 12); }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelIcon { Anchor: (Width: 72, Height: 72); Background: #000000(0.25); }");
  b.appendInline("#SkyyGSelIcon", "ItemIcon { Anchor: (Width: 64, Height: 64, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(sel.getItemId()) + "\"; }");
  b.appendInline("#SkyyGSel", "Label { Anchor: (Width: 14, Height: 72); Text: \"\"; }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelTxt { Anchor: (Width: 470, Height: 76); LayoutMode: Top; }");
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelName.Text", @PKG@.GearUnid.title(d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelSub.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + tn.toUpperCase() + "   -   " + @PKG@.GearUnid.rangeText(lo, hi));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelWhere { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  b.set("#SkyyGSelWhere.Text", "In your " + @PKG@.GearForge.where(this.selSec, this.selSlot) + " - it stays there while you identify it.");
  b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  b.appendInline("#SkyyGDet", "Group #SkyyGCols { Anchor: (Height: 330); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyGCols", "Group #SkyyGColU { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGColU", "Label #SkyyGColUH { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGColUH.Text", "Mystery bag");
  b.appendInline("#SkyyGColU", "Label #SkyyGColU1 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
  b.set("#SkyyGColU1.Text", "Which " + tn.toLowerCase() + " it is, its exact level and its modifiers");
  b.appendInline("#SkyyGColU", "Label #SkyyGColU2 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
  b.set("#SkyyGColU2.Text", "are decided the moment you pay. The rarity is already set.");
  b.appendInline("#SkyyGColU", "Label #SkyyGColU3 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: " + (arm && at > 0 ? @PKG@.GearDefs.C_LABEL : @PKG@.GearDefs.C_BAD) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGColU3.Text", arm && at > 0 ? @PKG@.GearPool.AT_NAME[at] + " armor - cannot be worn until identified." : "Cannot be used until identified.");
  b.appendInline("#SkyyGColU", "Label #SkyyGColU4 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
  b.set("#SkyyGColU4.Text", @PKG@.GearCfg.REROLL_MAX > 0 ? "Not happy? Re-identify it later (up to " + @PKG@.GearCfg.REROLL_MAX + " times, x" + @PKG@.Gear.fnum(@PKG@.GearCfg.REROLL_MULT) + " cost each)." : "");
  long cost = @PKG@.GearUnid.cost(d);
  long have = @PKG@.GearForge.purse(u);
  String why = @PKG@.GearUnid.why(d);
  b.appendInline("#SkyyGDet", "Label #SkyyGCostTxt { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }");
  b.set("#SkyyGCostTxt.Text", cost > 0L ? "Cost: " + @PKG@.Gear.fmt(cost) + " coins (" + @PKG@.GearDefs.R_NAME[r] + ", " + @PKG@.GearUnid.rangeText(lo, hi) + ")" : "Cost: free");
  b.appendInline("#SkyyGDet", "Label #SkyyGPurse { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGPurse.Text", have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  boolean off = why != null || poor;
  String bt = why != null ? "Cannot identify" : (poor ? "Not enough coins" : "Identify");
  b.appendInline("#SkyyGDet", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 111, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnId { Anchor: (Width: 340, Height: 44); Text: \"" + @PKG@.Gear.safe(bt) + "\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnId", @EVD@.of("a", "id"));
}""")
# 0.2.11: the detail panel of an identified item from a bag - its current lines + the re-identify offer (two clicks)
M(ipg, r"""
public void detailReroll(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  String id = sel.getItemId();
  @BD@ d = @PKG@.GearUnid.rerollDoc(sel);
  @BD@ bx = @PKG@.GearUnid.boxOf(d);
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  int n = @PKG@.GearUnid.rerolls(bx);
  b.appendInline("#SkyyGMain", "Group #SkyyGDet { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGDet", "Label #SkyyGDetT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGDetT.Text", "Re-identify");
  b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  b.appendInline("#SkyyGDet", "Group #SkyyGSel { Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 12); }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelIcon { Anchor: (Width: 72, Height: 72); Background: #000000(0.25); }");
  b.appendInline("#SkyyGSelIcon", "ItemIcon { Anchor: (Width: 64, Height: 64, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; }");
  b.appendInline("#SkyyGSel", "Label { Anchor: (Width: 14, Height: 72); Text: \"\"; }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelTxt { Anchor: (Width: 470, Height: 76); LayoutMode: Top; }");
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelName.Text", @PKG@.GearView.nameText(id, d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelSub.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + @PKG@.GearView.slotWord(id) + "   -   Level " + lvl + "   -   from a bag (" + @PKG@.GearUnid.rangeText(@PKG@.GearUnid.lo(bx), @PKG@.GearUnid.hi(bx)) + ")");
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelWhere { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  b.set("#SkyyGSelWhere.Text", "In your " + @PKG@.GearForge.where(this.selSec, this.selSlot) + " - re-identified " + n + " of " + @PKG@.GearCfg.REROLL_MAX + " times.");
  b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  b.appendInline("#SkyyGDet", "Group #SkyyGCols { Anchor: (Height: 330); LayoutMode: Left; Padding: (Top: 6); }");
  @PKG@.ReforgePage.column(b, "#SkyyGCols", "#SkyyGColR", this.revealed != null ? "Revealed" : "Current", "#ffffff", id, this.revealed != null ? this.revealed : d, 562);
  String why = @PKG@.GearUnid.rerollWhy(d);
  long cost = why == null ? @PKG@.GearUnid.rerollCostOf(d) : 0L;
  long have = @PKG@.GearForge.purse(u);
  b.appendInline("#SkyyGDet", "Label #SkyyGCostTxt { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }");
  b.set("#SkyyGCostTxt.Text", why != null ? why : "Re-identify: " + @PKG@.Gear.fmt(cost) + " coins (re-roll " + (n + 1) + " of " + @PKG@.GearCfg.REROLL_MAX + ")");
  b.appendInline("#SkyyGDet", "Label #SkyyGPurse { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGPurse.Text", "Becomes another " + @PKG@.GearView.slotWord(id).toLowerCase() + " (same rarity, new level + modifiers); reforges are lost.");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  boolean armed = this.rrArm > 0L && System.currentTimeMillis() - this.rrArm <= 10000L && this.rrFp != null && this.rrFp.equals(this.selFp);
  boolean off = why != null || poor;
  String bt = why != null ? "Cannot re-identify" : (poor ? "Not enough coins" : (armed ? "Confirm re-identify" : "Re-identify"));
  b.appendInline("#SkyyGDet", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 111, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnId { Anchor: (Width: 340, Height: 44); Text: \"" + @PKG@.Gear.safe(bt) + "\"; " + @PKG@.GearUi.btn(off ? 3 : (armed ? 2 : 0)) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnId", @EVD@.of("a", "rr"));
}""")
'''
rep('''M(ipg, r"""
public void detail(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  b.appendInline("#SkyyGMain", "Group #SkyyGDet { Anchor: (Width: 562); LayoutMode: Top; }");''', PAGE_JAVA + '''M(ipg, r"""
public void detail(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  if (sel != null && @PKG@.GearUnid.isBox(sel.getItemId())) { detailBox(b, ev, u, sel, inv); return; }      // 0.2.11
  if (sel != null && (this.selSec == 0 || this.selSec == 1 || this.selSec == 2) && @PKG@.GearUnid.rerollable(sel)) { detailReroll(b, ev, u, sel, inv); return; }
  b.appendInline("#SkyyGMain", "Group #SkyyGDet { Anchor: (Width: 562); LayoutMode: Top; }");''')
rep('''    String id = it.getItemId();
    @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    int lvl = @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \\"" + @PKG@.Gear.safe(id) + "\\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \\"\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \\"\\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", (d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d)) + (it.getQuantity() > 1 ? " x" + it.getQuantity() : "") + (on ? "  (selected)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", @PKG@.GearDefs.R_NAME[r] + " - Lv " + lvl);''', '''    String id = it.getItemId();
    @BD@ d = @PKG@.GearUnid.isBox(id) ? null : @PKG@.GearData.effective(id, it.getMetadata());
    int r = @PKG@.GearIdent.rowRarity(it, d);
    int lvl = d == null ? 0 : @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \\"" + @PKG@.Gear.safe(id) + "\\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \\"\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \\"\\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", @PKG@.GearIdent.rowName(it, d) + (it.getQuantity() > 1 ? " x" + it.getQuantity() : "") + (on ? "  (selected)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", @PKG@.GearIdent.rowSub(it, d, r, lvl));''')
rep('''  this.rows = @PKG@.GearIdent.rows(inv);
  long all = total(inv);
  long have = @PKG@.GearForge.purse(u);''', '''  this.rows = @PKG@.GearIdent.rows(inv);
  long all = total(inv);
  int nUnid = @PKG@.GearIdent.items(inv, this.rows);
  this.rows.addAll(@PKG@.GearIdent.rerollRows(inv));       // 0.2.11: re-identifiable items after the unidentified ones (never in Identify all)
  long have = @PKG@.GearForge.purse(u);''')
rep('''  int n = @PKG@.GearIdent.items(inv, this.rows);
  boolean allOff = n == 0 || (have >= 0L && have < all && n == 1);''', '''  int n = nUnid;
  boolean allOff = n == 0 || (have >= 0L && have < all && n == 1);''')
rep('''  b.set("#SkyyGHeadItem.Text", "Unidentified gear (" + this.rows.size() + ")");''',
    '''  b.set("#SkyyGHeadItem.Text", "Unidentified gear + bags (" + this.rows.size() + ")");''')
rep('''  Object[] res = @PKG@.GearIdent.identify(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    this.selFp = @PKG@.GearForge.fp((@IS@) res[2]);
    this.revealed = (@BD@) res[4];''', '''  Object[] res = @PKG@.GearIdent.identify(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();
  if (code == 1 && @PKG@.GearUnid.isBox(this.selId) && res[2] instanceof @IS@) {
    // 0.2.11: the bag became its item in the same slot - select that item (it can be re-identified from here)
    @IS@ got = (@IS@) res[2];
    this.selId = got.getItemId();
    this.selFp = @PKG@.GearForge.fp(got);
    this.revealed = (@BD@) res[4];
    long cost0 = ((Long) res[5]).longValue();
    String sum0 = @PKG@.GearView.modSummary(this.revealed);
    this.info = "+It was " + @PKG@.GearView.nameText(got.getItemId(), this.revealed) + " - Lv " + @PKG@.GearLevel.level(got.getItemId(), this.revealed) + (sum0.length() > 0 ? " - " + sum0 : "") + (cost0 > 0L ? " (-" + @PKG@.Gear.fmt(cost0) + " coins)" : "");
    return;
  }
  if (code == 1) {
    this.selFp = @PKG@.GearForge.fp((@IS@) res[2]);
    this.revealed = (@BD@) res[4];''')
rep('''# spec 5.7 "Identify all": one by one, each paid on its own; refused rows are skipped (exploit review 2), a failed write stops
M(ipg, r"""''', '''# 0.2.11 re-identify: the first click arms (10 s, this exact item), the second does it (same safety as identify)
M(ipg, r"""
public void reroll(@INV@ inv) {
  if (!guard()) return;
  if (this.selSec < 0) { this.info = "-Pick an item first."; return; }
  long now = System.currentTimeMillis();
  if (this.rrArm <= 0L || now - this.rrArm > 10000L || this.rrFp == null || !this.rrFp.equals(this.selFp)) {
    this.rrArm = now;
    this.rrFp = this.selFp;
    this.info = "=Click Confirm re-identify to roll it again - it becomes a different item and loses its reforges.";
    return;
  }
  this.rrArm = 0L;
  java.util.UUID u = this.playerRef.getUuid();
  @IC@ c = @PKG@.GearStamp.section(inv, this.selSec);
  if (this.selSec != 0 && this.selSec != 1 && this.selSec != 2) c = null;
  Object[] res = @PKG@.GearIdent.reroll(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername());
  int code = ((Integer) res[0]).intValue();
  if (code == 1 && res[2] instanceof @IS@) {
    @IS@ got = (@IS@) res[2];
    this.selId = got.getItemId();
    this.selFp = @PKG@.GearForge.fp(got);
    this.revealed = (@BD@) res[4];
    long cost = ((Long) res[5]).longValue();
    String sum = @PKG@.GearView.modSummary(this.revealed);
    this.info = "+It is now " + @PKG@.GearView.nameText(got.getItemId(), this.revealed) + " - Lv " + @PKG@.GearLevel.level(got.getItemId(), this.revealed) + (sum.length() > 0 ? " - " + sum : "") + (cost > 0L ? " (-" + @PKG@.Gear.fmt(cost) + " coins)" : "");
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("That item moved")) clearSel();
  this.info = "-" + msg;
}""")
# spec 5.7 "Identify all": one by one, each paid on its own; refused rows are skipped (exploit review 2), a failed write stops
M(ipg, r"""''')
rep('''    if (a.equals("id")) { one(inv); rebuild(); return; }''', '''    if (a.equals("id")) { one(inv); rebuild(); return; }
    if (a.equals("rr")) { reroll(inv); rebuild(); return; }      // 0.2.11 re-identify''')
rep('''    b.set("#SkyyGEmpty2.Text", "Weapons and armor from mobs and loot chests arrive unidentified.");''',
    '''    b.set("#SkyyGEmpty2.Text", "Mystery bags and unidentified gear from mobs and loot chests show up here.");''')

# ================================================================================================================ /gear box + /gear loot
rep('''        ("relevel", "GearRelevelCmd", "Re-stamp gear levels into today's bands: /gear relevel [player]", True)]''',
    '''        ("relevel", "GearRelevelCmd", "Re-stamp gear levels into today's bands: /gear relevel [player]", True),
        # 0.2.11 the loot round
        ("box", "GearBoxCmd", "Give a mystery bag: /gear box <rarity|random> [level] [type]", True),
        ("loot", "GearLootCmd", "Loot round counters, the bag pool and the odds", False)]''')
rep('''C(subc["relevel"], r"""
public GearRelevelCmd() {
  super("relevel", "Re-stamp gear levels into today's bands: /gear relevel [player]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")''', '''C(subc["relevel"], r"""
public GearRelevelCmd() {
  super("relevel", "Re-stamp gear levels into today's bands: /gear relevel [player]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["box"], r"""
public GearBoxCmd() {
  super("box", "Give a mystery bag: /gear box <rarity|random> [level] [type]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["loot"], r"""
public GearLootCmd() {
  super("loot", "Loot round counters, the bag pool and the odds");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")''')
rep('''  addSubCommand(new @PKG@.GearRelevelCmd());
}""")''', '''  addSubCommand(new @PKG@.GearRelevelCmd());
  addSubCommand(new @PKG@.GearBoxCmd());
  addSubCommand(new @PKG@.GearLootCmd());
}""")''')
rep('''    if (action.equals("relevel")) { relevelCmd(pr, inv, rest); return; }
''', '''    if (action.equals("relevel")) { relevelCmd(pr, inv, rest); return; }
    if (action.equals("box")) { boxCmd(pr, inv, rest); return; }        // 0.2.11
    if (action.equals("loot")) { lootCmd(pr); return; }
''')
rep('''    if (action.equals("read")) { read(pr, h); return; }
    if (!@PKG@.GearData.gearish(id, md)) { msg(pr, @PKG@.Gear.itemName(id) + " is not gear"); return; }''', '''    if (action.equals("read")) { read(pr, h); return; }
    // 0.2.11: /gear identify on a held mystery bag = a free identify through the same core
    if (action.equals("identify") && @PKG@.GearUnid.isBox(id)) {
      Object[] rb = @PKG@.GearIdent.identify(handC(inv), handS(inv), id, @PKG@.GearForge.fp(h), u, who, true, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
      msg(pr, (String) rb[1] + (((Integer) rb[0]).intValue() == 1 && rb[2] instanceof @IS@ ? " It was " + @PKG@.GearView.nameText(((@IS@) rb[2]).getItemId(), (@BD@) rb[4]) + " - " + @PKG@.GearView.modSummary((@BD@) rb[4]) : ""));
      return;
    }
    if (!@PKG@.GearData.gearish(id, md)) { msg(pr, @PKG@.Gear.itemName(id) + " is not gear"); return; }''')
rep('''M(gad, r"""
public static void giveCmd(@PR@ pr, @INV@ inv, String rest) {''', '''# 0.2.11 /gear box <rarity|random> [level] [type key or name]: a bag in your inventory (storage first); /gear loot: counters + pool
M(gad, r"""
public static void boxCmd(@PR@ pr, @INV@ inv, String rest) {
  String[] tk = rest.trim().length() == 0 ? new String[0] : rest.trim().split("\\\\s+");
  if (tk.length == 0) { msg(pr, "usage: /gear box <normal|unique|rare|legendary|fabled|mythic|set|random> [level 1-" + @PKG@.GearCfg.LOOT_TOP + "] [type: sword, bow, chestplate ...]"); return; }
  int r = tk[0].equalsIgnoreCase("random") ? @PKG@.GearUnid.rarity(1, 0) : @PKG@.GearDefs.rIndex(tk[0]);
  if (r < 0) { msg(pr, "unknown rarity '" + tk[0] + "' - normal, unique, rare, legendary, fabled, mythic, set or random"); return; }
  int L = 10;
  if (tk.length > 1) { try { L = Integer.parseInt(tk[1]); } catch (Throwable t) { msg(pr, "the level must be a number"); return; } }
  int ty = -1;
  if (tk.length > 2) {
    String w = tk[2];
    for (int i = 0; i < @PKG@.GearPool.T_KEY.length && ty < 0; i++)
      if (@PKG@.GearPool.T_KEY[i].equalsIgnoreCase(w) || @PKG@.GearPool.T_NAME[i].equalsIgnoreCase(w) || @PKG@.GearPool.T_KEY[i].equalsIgnoreCase("Weapon_" + w) || @PKG@.GearPool.T_KEY[i].equalsIgnoreCase("Armor_" + w)) ty = i;
    if (ty < 0) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.GearPool.T_NAME.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.GearPool.T_NAME[i].toLowerCase()); }
      msg(pr, "unknown type '" + w + "' - " + sb);
      return;
    }
  }
  @IS@ s = null;
  for (int k = 0; k < 8 && s == null; k++) {
    s = @PKG@.GearUnid.roll(L, ty, "admin", "admin", 0, null, 1, 0);
    if (s != null && @PKG@.GearUnid.rar(@PKG@.GearUnid.doc(s)) != r) {
      @BD@ d = @PKG@.GearUnid.doc(s);
      s = @PKG@.GearUnid.make(@PKG@.GearUnid.type(d), @PKG@.GearUnid.at(d), r, @PKG@.GearUnid.lo(d), @PKG@.GearUnid.hi(d), "admin", "admin", 0);
    }
  }
  if (s == null) { msg(pr, "no bag fits level " + L + (ty >= 0 ? " for " + @PKG@.GearPool.T_NAME[ty] : "") + " (no candidate)"); return; }
  boolean in = give(inv, s);
  @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " box " + @PKG@.GearUnid.logText(s) + (in ? "" : " (inventory full)"));
  msg(pr, (in ? "gave " : "NOT given (inventory full): ") + @PKG@.GearUnid.titleOf(s) + " - " + @PKG@.GearDefs.R_NAME[r] + ", " + @PKG@.GearUnid.rangeText(@PKG@.GearUnid.lo(@PKG@.GearUnid.doc(s)), @PKG@.GearUnid.hi(@PKG@.GearUnid.doc(s))));
}""")
M(gad, r"""
public static void lootCmd(@PR@ pr) {
  msg(pr, @PKG@.GearLoot.statusText());
  msg(pr, @PKG@.GearLoot.countsText());
  msg(pr, "mob:fn:level " + (@PKG@.Gear.fn("mob:fn:level") != null ? "yes" : "NO (no extra mob bags without SkyyMobs)") + ", mob:fn:levelAt " + (@PKG@.Gear.fn("mob:fn:levelAt") != null ? "yes" : "no (chest bags use the drop list's zone)") + ", death order " + (@PKG@.GearDeathMark.DDI != null ? "before DropDeathItems" : "FALLBACK (extra bags may not drop)"));
}""")
M(gad, r"""
public static void giveCmd(@PR@ pr, @INV@ inv, String rest) {''')

# ================================================================================================================ setup / bridge / ready / classes
rep('''  br.put("gear:gates", @PKG@.GearDefs.GATES);
''', '''  br.put("gear:gates", @PKG@.GearDefs.GATES);
  br.put("gear:fn:box", new @PKG@.GearBoxFn());        // 0.2.11: a mystery bag for SkyyExploration's Unclaimed Luggage
''')
rep('''protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.GearLog.flush(); } catch (Throwable t2) { }''', '''protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }
  try { @PKG@.GearLog.flush(); } catch (Throwable t2) { }''')
rep('''+ @PKG@.GearSpeed.readyText() + "; " + @PKG@.GearSig.statusText() + "; Reforge level up "''',
    '''+ @PKG@.GearSpeed.readyText() + "; " + @PKG@.GearSig.statusText() + "; " + @PKG@.GearLoot.statusText() + "; Reforge level up "''')
rep('''(admin: /gear give | read | reroll | clear | rarity | unid | identify | level | gate | migrate | charged | relevel, node skyygear.admin)''',
    '''(admin: /gear give | read | reroll | clear | rarity | unid | identify | level | gate | migrate | charged | relevel | box | loot, node skyygear.admin)''')
rep('''CRIT_CLASSES + [gspd] + SIG_CLASSES
''', '''CRIT_CLASSES + [gspd] + SIG_CLASSES + LOOT_CLASSES
''')
rep('''print("0.2.10: signature charge kept on a weapon swap - %s (row gear.signatureKeep, default on)" % ", ".join(str(c.getName()).rsplit(".", 1)[1] for c in SIG_CLASSES))''',
    '''print("0.2.10: signature charge kept on a weapon swap - %s (row gear.signatureKeep, default on)" % ", ".join(str(c.getName()).rsplit(".", 1)[1] for c in SIG_CLASSES))
print("0.2.11: the loot round - %s; %d bag pool ids, %d types; %d loot rows (Server Setup -> Gear -> Loot); /gear box + /gear loot; gear:fn:box"
      % (", ".join(str(c.getName()).rsplit(".", 1)[1] for c in LOOT_CLASSES), len(LOOT_POOL), len(LOOT_TYPES), len(LT_ROWK)))''')
# the jar: the bag items are the ONLY Server/Item/Items entries (new ids, in no vanilla / SET file)
rep('''    assert not [n for n in _names if n.startswith("Server/Item/Items/")], "SkyyGear 0.2.2 overrides no item file (the box is hidden at run time)"''',
    '''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(BAG_ITEMS), "SkyyGear 0.2.11 ships only the 7 mystery bag items"
    for _k, _v in BAG_ITEMS.items():
        assert _jz.read(_k).decode("utf-8") == _v, "bag item missing from the jar: " + _k
    for _k, _v in BAG_FILES.items():
        assert _jz.read(_k) == _v, "bag art missing from the jar: " + _k''')
rep('''B.assemble(jar, man, OUT, extra_files=EXTRA)
''', '''EXTRA.update(BAG_ITEMS)          # 0.2.11: the 7 mystery bag items (new ids; the old 'no item file' build check is narrowed to them)
B.assemble(jar, man, OUT, extra_files=EXTRA)
''')
rep('''Life Steal is capped; melee weapons roll a speed tier''', '''Life Steal is capped; unidentified loot comes as Wynncraft-style mystery bags (one look per rarity) whose item is picked when you identify it, with re-identify for coins; levelled mobs drop extra bags; melee weapons roll a speed tier''')

# ================================================================================================================ write
assert s.count("registerSystem(") == SYS0 and s.count("registerCommand(") == CMD0, "0.2.11 registers no new system / command (two /gear sub-commands)"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))
