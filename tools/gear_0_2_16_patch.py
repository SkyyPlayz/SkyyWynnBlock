"""Derive SkyyGear/build_skyygear_0.2.16.py from the LIVE 0.2.15 (build_skyygear_0.2.15.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_15_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_16_patch.py      then      python SkyyGear/build_skyygear_0.2.16.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.16.py

0.2.16 = THE FIRST UNTIERED BATCH (phase G2 of research/cloud/UT-First-Batch-Build.md on top of research/cloud/Untiered-Mythic-Spec.md 1.3-1.6;
Skyy's answers docs/answered/gear.md 2026-10-08 / 2026-10-09, newest wins) + GATHERING SETS SELLABLE. Skyy's words: "UT weapons and armor are
only mob drops and chest loot (bosses can drop them too.)" + "but you cant craft them." + "they can come from quests, but not shops."; "all of
those bows sound really cool, id use them all as special / ut items."; 2026-10-09 popup "UT drops -> Orange mystery bag"; after 0.2.15 "Gathering
sets sellable (Recommended)". G1's names win (0.2.14: rarity "untiered", the typed orange bag Skyy_Unid_Bag_Untiered, the ut.<id> table, the
market:veto wall, gear:fn:grant).
  1. THE BATCH (22 Untiered-table rows, all Lv 15-29 = UT2): 16 NEW item ids built by SkyyGear at BUILD time from the vanilla base item's JSON
     (Assets.zip; Recipe REMOVED - the engine's Item codec reads Recipe with append, not appendInherited, so a Parent's recipe is never
     inherited (build-checked by bytecode); Variant true = hidden from the creative list; Quality = the orange Skyy_Gear_Untiered; own name +
     description; the base model with an ORANGE placeholder recolour of its texture + icon generated at build time from Assets.zip, never
     committed - UT_ART, the bag's one-line swap pattern): U2 Weapon_Sword_UT_Paperweight (Iron sword), U3 Weapon_Battleaxe_UT_Overtime,
     U4 Weapon_Daggers_UT_PocketKnife, U5 Weapon_Shortbow_UT_ShortNotice, U8 Armor_UT_FilingCabinet_<Head|Chest|Hands|Legs> (Iron, Heavy),
     U9 Armor_UT_Courier_<slot> (Leather_Medium, Light), U10 Armor_UT_Intern_<slot> (Cloth_Cotton, Cloth); 3 ids SkyyArmory 0.1.15 builds
     from its own Iron items (U1 Weapon_Staff_UT_Loophole, U6 Weapon_Wand_UT_SecondOpinion, U7 Weapon_Bo_UT_Turnstile - an older SkyyArmory
     = no such item: the row is skipped at identify, never handed out); 3 vanilla developer bows on their own ids (Weapon_Shortbow_Ricochet,
     _Combat, _Test_Zoom - no copy). NEVER CRAFTABLE: no copy has a recipe, the build asserts no recipe in Assets.zip / the SET jars makes a UT
     id, G1 ignores a ut row a recipe makes; never in shops (market wall + SkyyMerchants' rarity rule), never in the normal bag pool.
  2. FIXED STAT LINES (Server Setup -> Gear -> Rarity -> "Untiered stat lines": utfx.<item id>=<body lines>,<fixed lines + tricks>; only for an
     identified Untiered document, never stored on the item - a balance change reaches every copy at once, nothing re-rolls):
     body = live stat keys at a fixed utline.power % (70) of the stat max, scaled by the item level like a roll (bounds / factor); fixed =
     constant words: a live stat key + / - N (dmg-30, cc+1, spd+4 - NO slot filter: armor Damage counts), swing=slow (the fixed speed tier,
     a lazy heal in GearSpeed.ensure: any copy whose tier differs is rewritten at its owner's next scan), and the tricks lowhp+30 (damage
     while under half Health), back+50 / front-30 (the 120 degree cone behind / in front of the target's head facing), taken+5 (damage taken,
     after Defense), hp+6.25 (max Health %, one ADDITIVE modifier skyygear_ut_hp = pct x the max without it, recomputed every second, 0 =
     removed; profile:busy removes it), mregen+12.5 (Mana regen % through SkyySkills' skill:fn:manaregen registry, source "SkyyGear
     Untiered"), range+12 (a shot further than N blocks from the shooter deals nothing), kb+100 (knockback x2: the hit's KnockbackComponent
     modifier, the speed-tier way), pierce / heal (read by SkyyArmory 0.1.15 through gear:fn:utfx). Held weapon + worn armor, active only
     (identified, level met); part.utLines off = plain base items (still orange, fixed, walled).
  3. THE ORANGE BAG SOURCES (G1's typed bag): mob extra bags (6 % roll): utdrop.mob 2 % of them become an orange bag when the mob level sits
     inside an Untiered row (no extra roll, the hourly cap counts it); fresh-chest extra bags: utdrop.chest 2 %; Unclaimed Luggage (gear:fn:box
     with tier 1-4, no type asked): utdrop.luggage "1 2 4 8" % per bag; bosses / quests later (gear:fn:grant / gear:fn:box "untiered").
     The bag's type: armor utbag.armorShare 50 %, a weapon type weighted by its row count x utbag.classLean 3 for the killer's / opener's
     class weapons. Counters in /gear loot.
  4. THE BO BAG TYPE (the 0.2.14 builder's missing type, needed by U7): "Weapon_Bo" (Bo Staff) joins the bag types (a bag stores its type KEY,
     so nothing stored moves); no random-bag item has it (only Untiered rows). Wraps / gauntlets are not in this batch - not added.
  5. DEVELOPER BOWS: all 6 leave the random bag pool (build-time filter, next to FAM_DEV); Ricochet / Combat / Test_Zoom are Untiered rows;
     gear.mythicItems (Vampire, Bomb, Pull - Skyy "Mythic is bosses only") = every NEW document of those ids is Mythic (and a plain one is
     stamped Mythic at the first scan), never in random bags; no source but /gear give until the boss round.
  6. MARKET WALL SPLIT (Skyy 2026-10-09 "Gathering sets sellable"): a Set piece whose set id starts with market.gatheringPrefixes
     (mining_, foraging_, farming_) is NOT walled while market.gatheringSets is on - Auctions / Bazaar / merchants may take it; quest / boss
     Sets, Mythic, Untiered and every Mythic / Untiered / Set mystery bag stay walled.
  7. ADMIN: /gear ut (the rows: usable or why not, the drop shares) and /gear ut give <item id or name> [level] (an identified Untiered item).
SAVED DATA: nothing new is stored (the lines live in config); Untiered documents of the new ids are G1's; a Paperweight's spd field is
rewritten to its fixed tier (lazy heal). The hp modifier skyygear_ut_hp is saved WITH THE PLAYER by the engine (like the 0.2.5 locks) and
recomputed within 1 s of every join.
CONFIG (PROJECT-RULES 4): ONE-TIME UPDATE migrate0216 = pure ADDITION (no value rewritten, no change-log row): the block (heading, marker, the
scalar rows with their help lines, the 22 ut.<id> rows, the 22 utfx.<id> rows) at the END of the file, only the keys the file lacks (kept +
noted); verified History copy first, atomic write, ISO-8859-1 bytes, run-once marker, every other byte and line ending kept.
ROLLBACK FLOORS (for tools/deploy_set.py, reported, not edited here): rolling SkyyGear back to 0.2.15 keeps every document (Untiered stays
Untiered) but the 16 SkyyGear copies + the 4 Short Notice arrow configs disappear (unknown items in inventories, the Vault and AH listings -
treat as lost) and the gathering sets are walled again; a player who logged out wearing a hp UT piece keeps that +/- max Health modifier
(skyygear_ut_hp) on 0.2.15 until they join a 0.2.16+ server again. Before a rollback: set part.utLines=false (every online player's modifier
goes within 1 s), keep the orange bags unopened only if the old jar still has the rows (it does: the ut rows stay in the file).
An orange Bo Staff bag (type key Weapon_Bo) cannot be opened on 0.2.15 ("a kind of gear this server does not have") but is kept, not lost;
it opens again on 0.2.16+. NOT IN THIS ROUND (next Untiered round): the per-row drop weight ut.weight.<key> (spec 3.1 / 4.1) - every row is
weight 1 today.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.15.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.16.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.15"' in s and s.startswith('"""SkyyGear 0.2.15 - build script'), "build_skyygear_0.2.15.py is not the live 0.2.15"
assert "GearUtFx" not in s and "utfx" not in s, "0.2.15 already has the 0.2.16 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.15 - build script (javassist via jpype). GENERATED by tools/gear_0_2_15_patch.py from the LIVE 0.2.14 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.15.py -> SkyyGear/SkyyGear-0.2.15.jar (never --deploy).

0.2.15 = ''', '''"""SkyyGear 0.2.16 - build script (javassist via jpype). GENERATED by tools/gear_0_2_16_patch.py from the LIVE 0.2.15 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.16.py -> SkyyGear/SkyyGear-0.2.16.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.16 = "):].strip() + '''

0.2.15 (the base, everything below is still true unless 0.2.16 above says otherwise):
0.2.15 = ''')
rep('VERSION = "0.2.15"', 'VERSION = "0.2.16"')

# ================================================================================================================ 1. the batch table (Python)
rep(r'''LOOT_POOL = []          # (id, type key, armor type 0-3, drop only, band min, band cap)
for _i in _GEAR_AZ:
    if _i.startswith(tuple(FAM_DEV)) or _i.endswith("_NPC") or "_Test" in _i:
        continue''', r'''# ================================================================= 0.2.16 THE FIRST UNTIERED BATCH (tools/gear_0_2_16_patch.py, research/cloud/UT-First-Batch-Build.md)
# (key, item id, base id, owner, body lines, fixed lines + tricks, the one orange trade-off line, name, kind word). owner: gear = SkyyGear builds the
# copy here; armory = SkyyArmory 0.1.15 builds it from its own Iron item; vanilla = the vanilla id itself (the developer bows)
UT_LO, UT_HI = 15, 29
_FC = "Tank set: +6.25%% max Health and %s%% less damage dealt per piece (whole set +25%% / -10%%)."
_CO = "Runner's set: faster and sharper - but you take 5% more damage per piece (whole set +20%)."
_IN = "Spell-spam set: +12.5% Mana regen and 5% less max Health per piece (whole set +50% / -20%)."
UT_ROWS = [
    ("loophole", "Weapon_Staff_UT_Loophole", "Weapon_Staff_Iron", "armory", "mp cc", "dmg-30 pierce+1",
     "Quick shots pierce every enemy in a line. 30% less damage.", "The Loophole", "staff"),
    ("paperweight", "Weapon_Sword_UT_Paperweight", "Weapon_Sword_Iron", "gear", "str cd", "dmg+7 swing=slow",
     "Hits 50% harder. Swings 40% slower.", "The Paperweight", "sword"),
    ("overtime", "Weapon_Battleaxe_UT_Overtime", "Weapon_Battleaxe_Iron", "gear", "str lsteal", "lowhp+30 hp-10",
     "30% more damage while under half Health. 10% less max Health while held.", "Overtime", "battleaxe"),
    ("pocketknife", "Weapon_Daggers_UT_PocketKnife", "Weapon_Daggers_Iron", "gear", "cc cd", "back+50 front-30",
     "Backstabs deal 50% more damage. Hits from the front deal 30% less.", "The Pocket Knife", "daggers"),
    ("shortnotice", "Weapon_Shortbow_UT_ShortNotice", "Weapon_Shortbow_Iron", "gear", "str cc", "dmg-15 range+12",
     "Quick and half-drawn arrows fly twice as fast and flat - but nothing hurts past 12 blocks. 15% less damage.", "Short Notice", "bow"),
    ("secondopinion", "Weapon_Wand_UT_SecondOpinion", "Weapon_Wand_Iron", "armory", "mp hpr", "dmg-40 heal+50",
     "Your heal orb heals 50% more. Wand shots deal 40% less damage.", "The Second Opinion", "wand"),
    ("turnstile", "Weapon_Bo_UT_Turnstile", "Weapon_Bo_Iron", "armory", "str cc", "dmg-25 kb+100",
     "Every hit knocks enemies back twice as far. 25% less damage.", "The Turnstile", "bo staff"),
] + [("filingcabinet_" + _sl.lower(), "Armor_UT_FilingCabinet_" + _sl, "Armor_Iron_" + _sl, "gear", "def",
      "hp+6.25 dmg-%d" % (2 if _sl in ("Head", "Hands") else 3), _FC % (2 if _sl in ("Head", "Hands") else 3),
      "The Filing Cabinet " + {"Head": "Helm", "Chest": "Plate", "Hands": "Gauntlets", "Legs": "Greaves"}[_sl], "heavy armor")
     for _sl in ("Head", "Chest", "Hands", "Legs")] \
  + [("courier_" + _sl.lower(), "Armor_UT_Courier_" + _sl, "Armor_Leather_Medium_" + _sl, "gear", "cd",
      "spd+%d cc+%d taken+5" % (3 if _sl == "Hands" else 4, 2 if _sl == "Chest" else 1), _CO,
      "The Courier's " + {"Head": "Cap", "Chest": "Jacket", "Hands": "Gloves", "Legs": "Trousers"}[_sl], "light armor")
     for _sl in ("Head", "Chest", "Hands", "Legs")] \
  + [("intern_" + _sl.lower(), "Armor_UT_Intern_" + _sl, "Armor_Cloth_Cotton_" + _sl, "gear", "mp", "mregen+12.5 hp-5", _IN,
      "The Intern's " + {"Head": "Hood", "Chest": "Robe", "Hands": "Cuffs", "Legs": "Skirt"}[_sl], "cloth armor")
     for _sl in ("Head", "Chest", "Hands", "Legs")] \
  + [("ricochet", "Weapon_Shortbow_Ricochet", "Weapon_Shortbow_Ricochet", "vanilla", "str cc", "dmg-20",
      "Prototype bow: its signature fires a bouncing triple shot and right click bashes. 20% less damage.", "", "bow"),
     ("combat", "Weapon_Shortbow_Combat", "Weapon_Shortbow_Combat", "vanilla", "str cc", "dmg-20",
      "Prototype bow: fast draw and a triple-shot signature and right click bashes. 20% less damage.", "", "bow"),
     ("testzoom", "Weapon_Shortbow_Test_Zoom", "Weapon_Shortbow_Test_Zoom", "vanilla", "str cc", "dmg-20",
      "Developer bow: zooms in while you draw. 20% less damage.", "", "bow")]
UT_IDS = [_r[1] for _r in UT_ROWS]
UT_COPY = [_r for _r in UT_ROWS if _r[3] == "gear"]
UT_ARMORY = [_r for _r in UT_ROWS if _r[3] == "armory"]
DEV_BOWS = ["Weapon_Shortbow_" + _b for _b in ("Combat", "Bomb", "Pull", "Ricochet", "Vampire", "Test_Zoom")]
MYTHIC_ITEMS_DEF = "Weapon_Shortbow_Vampire,Weapon_Shortbow_Bomb,Weapon_Shortbow_Pull"
assert len(UT_ROWS) == 22 and len(set(UT_IDS)) == 22 and len(UT_COPY) == 16 and len(UT_ARMORY) == 3
for _r in UT_ROWS:
    assert "," not in _r[6] and "=" not in _r[6] and all(32 <= ord(_c) < 127 for _c in _r[6]) and len(_r[6]) <= 110, _r[0]
    assert _r[3] != "vanilla" or _r[1] in DEV_BOWS
    assert _r[3] == "vanilla" or "_UT_" in _r[1]
for _b in DEV_BOWS:
    assert _b in _AZ_JSON, "developer bow gone from Assets.zip: " + _b
# fix round (ut02 review): the re-roll coin loop assert (U3) covers every Untiered id too - no sell / salvage value on the id or its base
# (the copies are their base's JSON; SkyyArmory's bases are not in Assets.zip = None) and no vanilla salvage recipe takes one as input
for _r in UT_ROWS:
    for _k in ("Value", "SellValue", "Price", "SellPrice", "Salvage", "SalvageValue"):
        assert az_get(_r[1], _k) is None and az_get(_r[2], _k) is None, "U3: Untiered %s (base %s) has a %s" % (_r[1], _r[2], _k)
    assert _r[1] not in _SALVAGE_IN, "U3: a vanilla recipe (salvage) takes the Untiered id " + _r[1] + " as input"
print("0.2.16 Untiered batch: %d rows (%d SkyyGear copies, %d SkyyArmory, %d developer bows), Lv %d-%d"
      % (len(UT_ROWS), len(UT_COPY), len(UT_ARMORY), len([_r for _r in UT_ROWS if _r[3] == "vanilla"]), UT_LO, UT_HI))

LOOT_POOL = []          # (id, type key, armor type 0-3, drop only, band min, band cap)
for _i in _GEAR_AZ:
    if _i.startswith(tuple(FAM_DEV)) or _i.endswith("_NPC") or "_Test" in _i:
        continue
    if _i in DEV_BOWS:          # 0.2.16: the six developer / prototype bows are Untiered or Mythic now - never in a random bag
        continue''')
rep(r'''_TNAME = {"Weapon_Shortbow": "Bow", "Armor_Head": "Helmet", "Armor_Chest": "Chestplate", "Armor_Hands": "Gauntlets", "Armor_Legs": "Leggings"}
LOOT_TYPES = sorted(set(_p[1] for _p in LOOT_POOL if _p[1].startswith("Weapon_"))) + ["Armor_Head", "Armor_Chest", "Armor_Hands", "Armor_Legs"]
assert set(LOOT_TYPES) == set(_p[1] for _p in LOOT_POOL), "every pool type has a bag type"''',
    r'''_TNAME = {"Weapon_Shortbow": "Bow", "Armor_Head": "Helmet", "Armor_Chest": "Chestplate", "Armor_Hands": "Gauntlets", "Armor_Legs": "Leggings",
          "Weapon_Bo": "Bo Staff"}      # 0.2.16
# 0.2.16: the Bo bag type (SkyyArmory's Weapon_Bo_* - only Untiered rows use it; no random bag item has it). Bags store the type KEY (mys), so
# a new type in the middle of the sorted list moves nothing stored
LOOT_TYPES = sorted(set([_p[1] for _p in LOOT_POOL if _p[1].startswith("Weapon_")] + ["Weapon_Bo"])) + ["Armor_Head", "Armor_Chest", "Armor_Hands", "Armor_Legs"]
assert set(LOOT_TYPES) == set(_p[1] for _p in LOOT_POOL) | {"Weapon_Bo"} and "Weapon_Bo" not in set(_p[1] for _p in LOOT_POOL), "every pool type has a bag type"
assert not [_p for _p in LOOT_POOL if _p[0] in DEV_BOWS], "a developer bow is still in the bag pool"''')
rep(r'''assert len(LOOT_POOL) >= 250 and len(LOOT_TYPES) == 18, (len(LOOT_POOL), LOOT_TYPES)''',
    r'''assert len(LOOT_POOL) >= 250 and len(LOOT_TYPES) == 19, (len(LOOT_POOL), LOOT_TYPES)       # 0.2.16: + Weapon_Bo''')

# ================================================================================================================ 2. the item copies (assets)
rep(r'''# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
CFG_FILE = "Skyy_SkyyGear/config.properties"''', r'''# ================================================================= 0.2.16 the 16 SkyyGear Untiered copies + the Short Notice arrows (build time,
# from Assets.zip - nothing vanilla is committed). ONE-LINE ART SWAP like BAG_ART: "placeholder" -> a folder of Quirk's / local art later
UT_ART = "placeholder"
UT_QUAL = QUAL_IDS[R_IDS.index("untiered")]
# the engine's Item codec reads "Recipe" with append (NOT appendInherited): a copy without its own Recipe never inherits one from its Parent
_icc = pool.get("com.hypixel.hytale.server.core.asset.type.item.config.Item").getClassInitializer()
import jpype as _jp
_ib = _jp.JClass("java.io.ByteArrayOutputStream")()
_jp.JClass("javassist.bytecode.InstructionPrinter")(_jp.JClass("java.io.PrintStream")(_ib)).print_(_icc.toMethod("clinitx", pool.get("com.hypixel.hytale.server.core.asset.type.item.config.Item")))
_il = str(_ib.toString()).split("\n")
_ri = [_k for _k, _x in enumerate(_il) if '= "Recipe"' in _x]
assert len(_ri) == 1, "the Item codec has no single Recipe key"
_nx = [_x for _x in _il[_ri[0]:_ri[0] + 12] if "AssetBuilderCodec$Builder.append" in _x]
assert _nx and "appendInherited" not in _nx[0], "the Item codec's Recipe is inherited now - a copy without a recipe could inherit its Parent's"
UT_ITEMS = {}
UT_FILES = {}
UT_LANG = []
_utr = _ramp(BAG_RAMP["untiered"])
for _r in UT_COPY:
    _bj = json.loads(json.dumps(_AZ_JSON[_r[2]]))
    for _k in ("Recipe", "$Comment"):
        _bj.pop(_k, None)
    assert az_get(_r[2], "Model") and az_get(_r[2], "Texture") and az_get(_r[2], "Icon"), _r[2]
    _tex = az_get(_r[2], "Texture")
    _ico = az_get(_r[2], "Icon")
    assert ("Common/" + _tex) in AZ_NAMES and ("Common/" + _ico) in AZ_NAMES, (_tex, _ico)
    _bj["TranslationProperties"] = {"Name": "server.items.%s.name" % _r[1], "Description": "server.items.%s.description" % _r[1]}
    _bj["Quality"] = UT_QUAL
    _bj["Variant"] = True
    _bj["ItemLevel"] = UT_LO
    _bj["Texture"] = "Items/SkyyGear/UT/%s.png" % _r[1]
    _bj["Icon"] = "Icons/ItemsGenerated/%s.png" % _r[1]
    if UT_ART == "placeholder":
        UT_FILES["Common/" + _bj["Texture"]] = SA.recolor(AZ.read("Common/" + _tex), _utr, rank=0.35)
        UT_FILES["Common/" + _bj["Icon"]] = SA.recolor_icon(AZ.read("Common/" + _ico), _utr, rank=0.35)
    else:
        _adir = os.path.join(os.path.dirname(HERE), *UT_ART.split("/"))
        UT_FILES["Common/" + _bj["Texture"]] = open(os.path.join(_adir, _r[1] + ".png"), "rb").read()
        UT_FILES["Common/" + _bj["Icon"]] = open(os.path.join(_adir, _r[1] + "_Icon.png"), "rb").read()
    if _r[0] == "shortnotice":
        # U5: the quick and half-drawn shots (Strength_0..3) launch our arrow configs: x2 launch force + air speed cap, no gravity. The full draw
        # (Strength_4) is left alone - it is SkyyArmory's bow leap release (its own interaction override), so the leap keeps working
        _iv = _bj.setdefault("InteractionVars", {})
        for _n in range(4):
            _vp = json.loads(AZ.read("Server/ProjectileConfigs/Weapons/Shortbow/Projectile_Config_Arrow_Shortbow_Strength_%d.json" % _n).decode("utf-8-sig"))
            _ph = dict(_vp["Physics"])
            assert _ph.get("Type") == "Standard" and _vp.get("LaunchForce") and _ph.get("TerminalVelocityAir"), _vp
            _ph["Gravity"] = 0
            _ph["TerminalVelocityAir"] = _ph["TerminalVelocityAir"] * 2
            _cid = "SkyyGear_UT_ShortNotice_Arrow_%d" % _n
            UT_FILES["Server/ProjectileConfigs/SkyyGear/%s.json" % _cid] = json.dumps(
                {"Parent": "Projectile_Config_Arrow_Shortbow_Strength_%d" % _n, "LaunchForce": _vp["LaunchForce"] * 2, "Physics": _ph}, indent=2)
            _vint = json.loads(AZ.read("Server/Item/Interactions/Weapons/Shortbow/Primary/Shoot/Weapon_Shortbow_Primary_Shoot_Strength_%d.json" % _n).decode("utf-8-sig"))
            assert _vint.get("Config") == "Projectile_Config_Arrow_Shortbow_Strength_%d" % _n, _vint
            _iv["Primary_Shoot_Strength_%d" % _n] = {"Interactions": [{"Parent": "Weapon_Shortbow_Primary_Shoot_Strength_%d" % _n, "Config": _cid}]}
    assert "Recipe" not in _bj and _r[1] not in AZ_ITEMS
    UT_ITEMS["Server/Item/Items/SkyyGear/UT/%s.json" % _r[1]] = json.dumps(_bj, indent=2)
for _r in UT_COPY:
    UT_LANG.append("items.%s.name = %s" % (_r[1], _r[7]))
    # fix round (ut02 review): ONE orange trade-off line - it comes from the editable ut.<id> row (GearUt.note), so the baked description
    # only names the kind (a Server Setup edit can never leave a stale copy of the trade-off here)
    UT_LANG.append("items.%s.description = Untiered %s." % (_r[1], _r[8]))
for _k in UT_FILES:
    assert _k not in AZ_NAMES, "an Untiered file would shadow a vanilla file: " + _k
    if _k.endswith(".png"):
        assert SA.png_size(UT_FILES[_k])[0] > 0, _k
# no recipe anywhere makes an Untiered id: Assets.zip (every recipe-carrying item names only ITSELF as output) + the magic recipes
assert not set(UT_IDS) & _RCP_OUT, "a recipe makes an Untiered id: %s" % (set(UT_IDS) & _RCP_OUT)
assert not [_r for _r in UT_ROWS if _r[3] == "vanilla" and az_get(_r[1], "Recipe")], "a developer bow has a recipe"
EXTRA.update(UT_FILES)
EXTRA.update(UT_ITEMS)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\n".join(UT_LANG) + "\n"
print("0.2.16 Untiered copies: %d items (%s art), %d files (%d arrow configs)" % (len(UT_ITEMS), UT_ART, len(UT_FILES),
                                                                                len([_k for _k in UT_FILES if _k.endswith(".json")])))

# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
CFG_FILE = "Skyy_SkyyGear/config.properties"''')

# ================================================================================================================ 3. config rows
rep(r'''    ("set", "Armor sets", "rarity", "table", "", "1", "4", "text|int|text;type;Name|Pieces|Full-set bonus", "", "live,danger",
     "All pieces worn = the bonus, e.g. hp+100 def+10 (hp or an armor stat key). No commas.",
     "reload@%s:set.;check=GearSet.checkSet" % CFG_FILE),''', r'''    ("set", "Armor sets", "rarity", "table", "", "1", "4", "text|int|text;type;Name|Pieces|Full-set bonus", "", "live,danger",
     "All pieces worn = the bonus, e.g. hp+100 def+10 (hp or an armor stat key). No commas.",
     "reload@%s:set.;check=GearSet.checkSet" % CFG_FILE),
    # 0.2.16 the first Untiered batch: the lines, the drop shares, the Mythic ids, the market wall split
    ("part.utLines", "Untiered stat lines and tricks", "rarity", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = Untiered items work like their plain base item (still orange, fixed and walled).", "field:GearCfg.UT_ON"),
    ("utfx", "Untiered stat lines", "rarity", "table", "", "", "300", "text|text;held;Body lines|Fixed lines and tricks", "", "live,danger",
     "Body: stat keys at fixed power (mp cc). Fixed: dmg-30 cc+1 hp+6.25 taken+5 swing=slow back+50 ...",
     "reload@%s:utfx.;entry=item;check=GearUtFx.checkRow" % CFG_FILE),
    ("utline.power", "Untiered body line power", "rarity", "int", "70", "1", "100", "", "%", "live,danger",
     "Body lines roll at this % of the stat max, scaled by level." + PH, "field:GearCfg.UT_POWER"),
    ("gear.mythicItems", "Items that are always Mythic", "rarity", "text", MYTHIC_ITEMS_DEF, "0", "2000", "", "", "live,danger",
     "Comma list of item ids: every new copy is Mythic (boss gear) and never in random bags.", "field:GearCfg.MYTH_IDS"),
    ("market.gatheringSets", "Gathering sets can be sold", "rarity", "bool", "true", "", "", "", "", "live,danger",
     "Crafted gathering Set pieces may go on Auctions / Bazaar / merchants. Quest and boss sets never.", "field:GearCfg.GSELL"),
    ("market.gatheringPrefixes", "Gathering set id prefixes", "rarity", "text", "mining_,foraging_,farming_", "0", "500", "", "", "live,adv,danger",
     "Set ids starting with one of these (comma list) are gathering sets.", "field:GearCfg.GSELL_PRE"),''')
rep(r'''    ("loot.mob.chance", "Extra mob drop chance", "loot", "dec", "6", "0", "100", "", "%", "live,danger",''',
    r'''    # 0.2.16 the orange bag sources (shares of bags that already drop - never an extra roll)
    ("utdrop.mob", "Orange share of extra mob bags", "loot", "dec", "2", "0", "100", "", "%", "live,danger",
     "At Untiered levels this % of extra mob bags are orange." + PH, "field:GearCfg.UT_MOB"),
    ("utdrop.chest", "Orange share of chest bags", "loot", "dec", "2", "0", "100", "", "%", "live,danger",
     "At Untiered levels this % of extra chest bags are orange." + PH, "field:GearCfg.UT_CHEST"),
    ("utdrop.luggage", "Orange bag chance in luggage", "loot", "text", "1 2 4 8", "0", "40", "", "", "live,danger",
     "Orange % per luggage bag, tiers I II III IV." + PH, "field:GearCfg.UT_LUG;check=GearUtFx.checkLug"),
    ("utbag.armorShare", "Orange bags: armor share", "loot", "int", "50", "0", "100", "", "%", "live",
     "Share of orange bags that hold armor (the rest hold a weapon)." + PH, "field:GearCfg.UT_ARMOR"),
    ("utbag.classLean", "Orange bags: own-class weapon weight", "loot", "int", "3", "1", "10", "", "", "live",
     "The finder's class weapon types count this many times." + PH, "field:GearCfg.UT_LEAN"),
    ("loot.mob.chance", "Extra mob drop chance", "loot", "dec", "6", "0", "100", "", "%", "live,danger",''')
rep(r'''           # 0.2.15: the mining armor switch, its per-tier lines, its Health share and the armor Fortune / Wisdom caps (economy)
           "garmor.miningOn", "garmor.mining", "garmor.miningShare", "armor.fortune.cap", "armor.wisdom.cap"}''',
    r'''           # 0.2.15: the mining armor switch, its per-tier lines, its Health share and the armor Fortune / Wisdom caps (economy)
           "garmor.miningOn", "garmor.mining", "garmor.miningShare", "armor.fortune.cap", "armor.wisdom.cap",
           # 0.2.16: the Untiered lines (combat numbers), the orange bag shares (economy), the Mythic ids, the market wall split (economy)
           "part.utLines", "utfx", "utline.power", "gear.mythicItems", "market.gatheringSets", "market.gatheringPrefixes", "utdrop.mob", "utdrop.chest",
           "utdrop.luggage"}''')
rep(r'''              ("GM_ON", "boolean", "true"), ("GM_SHARE", "int", "100"), ("GM_FCAP", "double", repr(MINE_FCAP)), ("GM_WCAP", "double", repr(MINE_WCAP))]''',
    r'''              ("GM_ON", "boolean", "true"), ("GM_SHARE", "int", "100"), ("GM_FCAP", "double", repr(MINE_FCAP)), ("GM_WCAP", "double", repr(MINE_WCAP)),
              # 0.2.16 the Untiered batch + the market wall split
              ("UT_ON", "boolean", "true"), ("UT_POWER", "int", "70"), ("MYTH_IDS", "String", jstr(MYTHIC_ITEMS_DEF)), ("GSELL", "boolean", "true"),
              ("GSELL_PRE", "String", '"mining_,foraging_,farming_"'), ("UT_MOB", "double", "2.0"), ("UT_CHEST", "double", "2.0"),
              ("UT_LUG", "String", '"1 2 4 8"'), ("UT_ARMOR", "int", "50"), ("UT_LEAN", "int", "3")]''')

# the fresh file's 0.2.16 block (= exactly what migrate0216 adds to an older file)
rep(r'''def default_text():''', r'''# 0.2.16: the Untiered batch block at the very end of a fresh file (migrate0216 appends the missing keys of it, group by group, to an older one)
UB_MARK_ID = "SkyyGear 0.2.16 untiered batch"
UB_WHO = "SkyyGear 0.2.16"
UB_HEAD = "# ---- The first Untiered batch + gathering sets on the market (SkyyGear 0.2.16) ----"
UB_MARK = ("# %s (Skyy 2026-10-09): 22 Untiered items from orange bags (mob drops, chests, luggage), never crafted or sold; the developer bows; "
           "crafted gathering Set pieces may be sold" % UB_MARK_ID)
_ubr = dict((_r[0], _r) for _r in CFG_ROWS)
UB_SCAL = ["part.utLines", "utline.power", "gear.mythicItems", "market.gatheringSets", "market.gatheringPrefixes", "utdrop.mob", "utdrop.chest",
           "utdrop.luggage", "utbag.armorShare", "utbag.classLean"]
UB_UTC = "# ---- the first Untiered batch (ut.<item id>=<min level>,<max level>,<trade-off line>) ----"
UB_FXC = "# ---- utfx.<item id>=<body lines: stat keys at utline.power>,<fixed lines: key+N / key-N, swing=slow; tricks lowhp back front taken hp mregen range pierce heal kb> ----"
UB_GROUPS = [("# %s: %s" % (_ubr[_k][1], _ubr[_k][10]), ["%s=%s" % (_k, _ubr[_k][4])]) for _k in UB_SCAL]
UB_GROUPS.append((UB_UTC, ["ut.%s=%d,%d,%s" % (_r[1], UT_LO, UT_HI, _r[6]) for _r in UT_ROWS]))
UB_GROUPS.append((UB_FXC, ["utfx.%s=%s,%s" % (_r[1], _r[4], _r[5]) for _r in UT_ROWS]))
UB_LINES = [UB_HEAD, UB_MARK] + [_x for _c, _ls in UB_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in UB_LINES) and all("=" not in _x for _x in (UB_HEAD, UB_MARK))
assert len(set(UB_LINES)) == len(UB_LINES)


def default_text():''')
rep(r'''    L += [""] + GM_LINES       # 0.2.15: the mining armor block (migrate0215 adds the missing lines of it to an older file)
    return "\n".join(L) + "\n"''', r'''    L += [""] + GM_LINES       # 0.2.15: the mining armor block (migrate0215 adds the missing lines of it to an older file)
    L += [""] + UB_LINES       # 0.2.16: the Untiered batch block (migrate0216 adds the missing lines of it to an older file)
    return "\n".join(L) + "\n"''')
rep(r'''# 0.2.15: the mining armor block once, at the very end, every line unique; the rows read back
assert _DL[-len(GM_LINES) - 1:] == GM_LINES + [""] and all(_DL.count(_x) == 1 for _x in GM_LINES) and DEFAULT_TEXT.count(GM_MARK_ID) == 1''',
    r'''# 0.2.15: the mining armor block once, right before the 0.2.16 block, every line unique; the rows read back
assert _DL[-len(GM_LINES) - len(UB_LINES) - 2:-len(UB_LINES) - 1] == GM_LINES + [""] and all(_DL.count(_x) == 1 for _x in GM_LINES) and DEFAULT_TEXT.count(GM_MARK_ID) == 1
# 0.2.16: the Untiered batch block once, at the very end, every line unique; the rows read back
assert _DL[-len(UB_LINES) - 1:] == UB_LINES + [""] and all(_DL.count(_x) == 1 for _x in UB_LINES) and DEFAULT_TEXT.count(UB_MARK_ID) == 1
for _r in UT_ROWS:
    assert _dp.get("ut." + _r[1]) == "%d,%d,%s" % (UT_LO, UT_HI, _r[6]) and _dp.get("utfx." + _r[1]) == "%s,%s" % (_r[4], _r[5]), _r[1]
assert _dp.get("utdrop.luggage") == "1 2 4 8" and _dp.get("gear.mythicItems") == MYTHIC_ITEMS_DEF''')
rep(r'''assert _DL[-len(GU_LINES) - len(GM_LINES) - 3:-len(GM_LINES) - 1] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - len(GM_LINES) - 3:]''',
    r'''assert _DL[-len(GU_LINES) - len(GM_LINES) - len(UB_LINES) - 4:-len(GM_LINES) - len(UB_LINES) - 2] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - len(GM_LINES) - 3:]''')

# ================================================================================================================ 4. Java: classes, fields
rep(r'''GM_CLASSES = [gmine]''', r'''GM_CLASSES = [gmine]
# 0.2.16 the first Untiered batch (tools/gear_0_2_16_patch.py)
gufx = mk("GearUtFx")           # the Untiered lines + tricks: table, totals, combat, max Health %, Mana regen, gear:fn:utfx
UB_CLASSES = [gufx]''')
rep(r'''F(gcf, "public static final String[] GM_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in GM_GROUPS for _x in _ls]))''',
    r'''F(gcf, "public static final String[] GM_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in GM_GROUPS for _x in _ls]))
# 0.2.16: the Untiered lines table { String[] ids, Object[] rows (GearUtFx.parseRow), java.util.HashMap id -> Integer } - swapped whole
F(gcf, "public static volatile Object[] UTFX = new Object[] { new String[0], new Object[0], new java.util.HashMap() };")
F(gcf, "public static final String UB_MARK = %s;" % jstr(UB_MARK))
F(gcf, "public static final String UB_MARK_ID = %s;" % jstr(UB_MARK_ID))
F(gcf, "public static final String UB_WHO = %s;" % jstr(UB_WHO))
F(gcf, "public static final String UB_HEAD = %s;" % jstr(UB_HEAD))
F(gcf, "public static final String[] UB_GC = %s;" % jarr([_c for _c, _ls in UB_GROUPS]))
F(gcf, "public static final int[] UB_GS = %s;" % jints([len(_ls) for _c, _ls in UB_GROUPS]))
F(gcf, "public static final String[] UB_GL = %s;" % jarr([_x for _c, _ls in UB_GROUPS for _x in _ls]))
F(gcf, "public static final String[] UB_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in UB_GROUPS for _x in _ls]))''')

# ================================================================================================================ 5. GearUtFx (1/4): the table + parse + checks
rep(r'''# ================================================================= 0.2.15 GearMine (1/4): the 28 metal pieces, the per-tier table (GearCfg.GM_TAB), the''',
    r'''# ================================================================= 0.2.16 GearUtFx (1/4): the Untiered lines table (GearCfg.UTFX), the row parser, the checks
# A row = Object[] { int[] body (stat indices), int[] fixed (NS sums), double[] tricks (TK order), Integer swing tier (-1 none) }.
F(gufx, 'public static final String[] TK = new String[] { "lowhp", "back", "front", "taken", "hp", "mregen", "range", "pierce", "heal", "kb" };')
for _k, _n in enumerate(("LOWHP", "BACK", "FRONT", "TAKEN", "HP", "MREGEN", "RANGE", "PIERCE", "HEAL", "KB")):
    F(gufx, "public static final int T_%s = %d;" % (_n, _k))
F(gufx, 'public static final String[] SWING = new String[] { "slow", "medium", "fast", "superfast" };')
F(gufx, "public static final String[] BASE_FROM = %s;" % jarr([_r[1] for _r in UT_ROWS if _r[3] != "vanilla"]))
F(gufx, "public static final String[] BASE_TO = %s;" % jarr([_r[2] for _r in UT_ROWS if _r[3] != "vanilla"]))
F(gufx, 'public static final String MANA_SRC = "SkyyGear Untiered";')
F(gufx, 'public static final String HPKEY = "skyygear_ut_hp";')
F(gufx, "public static final java.util.concurrent.ConcurrentHashMap MREG = new java.util.concurrent.ConcurrentHashMap();")
# 0 hits changed, 1 range zeroed, 2 knockback scaled, 3 damage taken changed, 4 hp modifier writes, 5 mana posts, 6 orange mob swaps, 7 orange chest
# swaps, 8 orange luggage swaps, 9 spd heals
F(gufx, "public static final long[] N = new long[10];")
M(gufx, "public static synchronized void count(int i) { if (i >= 0 && i < N.length) N[i] = N[i] + 1L; }")
# a SkyyGear / SkyyArmory copy -> its base item (damage curve twin, the armory info); anything else -> itself
M(gufx, r"""
public static String baseOf(String id) {
  if (id == null) return null;
  for (int i = 0; i < BASE_FROM.length; i++) if (BASE_FROM[i].equals(id)) return BASE_TO[i];
  return id;
}""")
M(gufx, r"""
public static int trick(String k) {
  if (k == null) return -1;
  String t = k.trim().toLowerCase();
  for (int i = 0; i < TK.length; i++) if (TK[i].equals(t)) return i;
  return -1;
}""")
M(gufx, r"""
public static int swingIdx(String v) {
  if (v == null) return -1;
  String t = v.trim().toLowerCase().replace("_", "").replace(" ", "");
  for (int i = 0; i < SWING.length; i++) if (SWING[i].equals(t)) return i;
  return -1;
}""")
M(gufx, r"""
public static double num(String v) {
  if (v == null) return Double.NaN;
  try { return Double.parseDouble(v.trim()); } catch (Throwable t) { return Double.NaN; }
}""")
M(gufx, r"""
public static void badw(StringBuilder sb, String p) {
  if (sb == null) return;
  if (sb.length() > 0) sb.append(' ');
  sb.append(p);
}""")
# "<body>,<fixed>" (or "<body>" alone) -> the row; null = not one or two cells. Unknown / bad words go to bad and are skipped
M(gufx, r"""
public static Object[] parseRow(String v, StringBuilder bad) {
  if (v == null) return null;
  String[] cs = v.replace('|', ',').split(",", -1);
  if (cs.length < 1 || cs.length > 2) return null;
  int ns = @PKG@.GearDefs.NS;
  java.util.ArrayList body = new java.util.ArrayList();
  String[] bs = cs[0].trim().length() == 0 ? new String[0] : cs[0].trim().split("\\s+");
  for (int i = 0; i < bs.length; i++) {
    int si = @PKG@.GearDefs.sIndex(bs[i].trim());
    if (si < 0 || @PKG@.GearDefs.S_LIVE[si] != 1) { badw(bad, bs[i]); continue; }
    Integer x = Integer.valueOf(si);
    if (!body.contains(x)) body.add(x);
  }
  int[] b = new int[body.size()];
  for (int i = 0; i < b.length; i++) b[i] = ((Integer) body.get(i)).intValue();
  long[] fx = new long[ns];
  double[] tk = new double[TK.length];
  int sw = -1;
  String[] fs = cs.length < 2 || cs[1].trim().length() == 0 ? new String[0] : cs[1].trim().split("\\s+");
  for (int i = 0; i < fs.length; i++) {
    String p = fs[i].trim();
    int op = -1;
    for (int c = 1; c < p.length() && op < 0; c++) { char ch = p.charAt(c); if (ch == '+' || ch == '-' || ch == '=') op = c; }
    if (op < 1 || op >= p.length() - 1) { badw(bad, p); continue; }
    String k = p.substring(0, op).trim();
    char o = p.charAt(op);
    String val = p.substring(op + 1).trim();
    if (k.equalsIgnoreCase("swing")) {
      int t = o == '=' ? swingIdx(val) : -1;
      if (t < 0) { badw(bad, p); continue; }
      sw = t;
      continue;
    }
    double x = num(val);
    if (Double.isNaN(x) || Double.isInfinite(x) || x < 0.0 || x > 1000.0) { badw(bad, p); continue; }
    if (o == '-') x = -x;
    int t = trick(k);
    if (t >= 0) { tk[t] = tk[t] + x; continue; }
    int si = @PKG@.GearDefs.sIndex(k);
    if (si < 0 || @PKG@.GearDefs.S_LIVE[si] != 1 || Math.abs(x - (double) Math.round(x)) > 0.000001) { badw(bad, p); continue; }
    long nv = fx[si] + Math.round(x);
    if (nv > 100000L) nv = 100000L;
    if (nv < -100000L) nv = -100000L;
    fx[si] = nv;
  }
  int[] f = new int[ns];
  for (int i = 0; i < ns; i++) f[i] = (int) fx[i];
  return new Object[] { b, f, tk, Integer.valueOf(sw) };
}""")
# utdrop.luggage "1 2 4 8" -> double[4] (each 0-100), null = bad
M(gufx, r"""
public static double[] lug(String s) {
  if (s == null) return null;
  String[] ps = s.trim().split("\\s+");
  if (ps.length != 4) return null;
  double[] o = new double[4];
  for (int i = 0; i < 4; i++) {
    o[i] = num(ps[i]);
    if (Double.isNaN(o[i]) || o[i] < 0.0 || o[i] > 100.0) return null;
  }
  return o;
}""")
M(gufx, r"""
public static String checkLug(String key, String value) {
  if (value == null || lug(value) == null) return "Write four percents 0-100 for Unclaimed Luggage tiers I II III IV, e.g. 1 2 4 8.";
  return null;
}""")
# the lines row of an id (null = none, or part.utLines off)
M(gufx, r"""
public static Object[] row(String id) {
  if (id == null || !@PKG@.GearCfg.UT_ON) return null;
  Object[] t = @PKG@.GearCfg.UTFX;
  Object o = ((java.util.HashMap) t[2]).get(id);
  if (!(o instanceof Integer)) return null;
  return (Object[]) ((Object[]) t[1])[((Integer) o).intValue()];
}""")
# the fixed speed tier of an Untiered-table id (-1 = none): GearSpeed.ensure writes it (new documents + the lazy heal of old ones)
M(gufx, r"""
public static int swingOf(String id) {
  Object[] r = row(id);
  if (r == null || !@PKG@.GearUt.has(id)) return -1;
  return ((Integer) r[3]).intValue();
}""")
# gear.mythicItems: an exact id in the comma list (Skyy "Mythic is bosses only": every new copy Mythic, never in random bags)
M(gufx, r"""
public static boolean mythicId(String id) {
  if (id == null || id.length() == 0) return false;
  String l = @PKG@.GearCfg.MYTH_IDS;
  if (l == null || l.length() == 0) return false;
  String[] ps = l.split(",");
  for (int i = 0; i < ps.length; i++) if (ps[i].trim().equals(id)) return true;
  return false;
}""")
# market.gatheringPrefixes: a gathering set id (null = not one, or market.gatheringSets off)
M(gufx, r"""
public static boolean gathering(String sid) {
  if (sid == null || !@PKG@.GearCfg.GSELL) return false;
  String s0 = sid.trim().toLowerCase();
  String l = @PKG@.GearCfg.GSELL_PRE;
  if (l == null) return false;
  String[] ps = l.split(",");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim().toLowerCase();
    if (p.length() > 0 && s0.startsWith(p)) return true;
  }
  return false;
}""")

# ================================================================= 0.2.15 GearMine (1/4): the 28 metal pieces, the per-tier table (GearCfg.GM_TAB), the''')

# GearCfg: the table reader, the scalars, the swap
rep(r'''# set.<id>=<name>,<pieces>,<bonus> -> STAB (key order; bad lines skipped / bad bonus words dropped with one WARN each)''',
    r'''# 0.2.16 utfx.<id>=<body>,<fixed> -> UTFX (key order; a bad line skipped / bad words dropped with one WARN each)
M(gcf, r"""
public static Object[] readUtfx(java.util.Properties p) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.HashMap ix = new java.util.HashMap();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("utfx.") || k.length() <= 5) continue;
    String id = k.substring(5).trim();
    String v = p.getProperty(k);
    StringBuilder bad = new StringBuilder();
    Object[] r = @PKG@.GearUtFx.parseRow(v, bad);
    if (id.length() == 0 || r == null) { @PKG@.Gear.warnOnce("utfxrow:" + k + "=" + v, "config.properties: " + k + "=" + v + " is not <body lines>,<fixed lines> - ignored"); continue; }
    if (bad.length() > 0) @PKG@.Gear.warnOnce("utfxbad:" + k + "=" + v, "config.properties: " + k + " - unknown words skipped: " + bad);
    if (ix.containsKey(id)) continue;
    ix.put(id, Integer.valueOf(ids.size()));
    ids.add(id);
    rows.add(r);
  }
  return new Object[] { (String[]) ids.toArray(new String[0]), rows.toArray(new Object[0]), ix };
}""")
# set.<id>=<name>,<pieces>,<bonus> -> STAB (key order; bad lines skipped / bad bonus words dropped with one WARN each)''')
rep(r'''  GM_WCAP = pdec(p, "armor.wisdom.cap", 10.0, 0.0, 100.0);
  PART_LEVELS = pbool(p, "part.levels", true);''', r'''  GM_WCAP = pdec(p, "armor.wisdom.cap", 10.0, 0.0, 100.0);
  // 0.2.16 the Untiered batch + the market wall split
  UT_ON = pbool(p, "part.utLines", true);
  UT_POWER = (int) plong(p, "utline.power", 70L, 1L, 100L);
  MYTH_IDS = ptext(p, "gear.mythicItems", "@MYTHDEF@").trim();
  GSELL = pbool(p, "market.gatheringSets", true);
  GSELL_PRE = ptext(p, "market.gatheringPrefixes", "mining_,foraging_,farming_").trim();
  UT_MOB = pdec(p, "utdrop.mob", 2.0, 0.0, 100.0);
  UT_CHEST = pdec(p, "utdrop.chest", 2.0, 0.0, 100.0);
  String ulg = ptext(p, "utdrop.luggage", "1 2 4 8");
  if (@PKG@.GearUtFx.lug(ulg) == null) { @PKG@.Gear.warnOnce("utlug:" + ulg, "config.properties: utdrop.luggage=" + ulg + " is not four percents 0-100 - the default 1 2 4 8 is used"); ulg = "1 2 4 8"; }
  UT_LUG = ulg.trim();
  UT_ARMOR = (int) plong(p, "utbag.armorShare", 50L, 0L, 100L);
  UT_LEAN = (int) plong(p, "utbag.classLean", 3L, 1L, 10L);
  PART_LEVELS = pbool(p, "part.levels", true);''')
rep(r'''.replace("@CRITTA@", CRIT_TEXT_DEF).replace("@CRITTB@", CRIT_TEXT2_DEF))''',
    r'''.replace("@CRITTA@", CRIT_TEXT_DEF).replace("@CRITTB@", CRIT_TEXT2_DEF).replace("@MYTHDEF@", MYTHIC_ITEMS_DEF))''')
rep(r'''  Object[] gmt = readMine(p);         // 0.2.15
  LV_CAP = lc; UTAB = utab; STAB = stab; GM_TAB = gmt;''', r'''  Object[] gmt = readMine(p);         // 0.2.15
  Object[] ufx = readUtfx(p);         // 0.2.16
  LV_CAP = lc; UTAB = utab; STAB = stab; GM_TAB = gmt; UTFX = ufx;''')

# ================================================================================================================ 6. the one-time update migrate0216
rep(r'''# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO''',
    r'''# ---- 0.2.16 ONE-TIME UPDATE migrate0216 (PROJECT-RULES section 4): a pure ADDITION, the 0.2.15 shape. null = the marker is already in a comment
# line (a fresh 0.2.16 file carries it); else { new text, String[] notes (keys already there - kept), "part.utLines, ..." (what was added) }
M(gcf, r"""
public static Object[] ubUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(UB_MARK_ID) >= 0) return null;
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
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add("");
  blk.add(UB_HEAD);
  blk.add(UB_MARK);
  int at = 0;
  for (int g = 0; g < UB_GC.length; g++) {
    boolean first = true;
    for (int j = 0; j < UB_GS[g]; j++) {
      int x = at + j;
      if (pp.getProperty(UB_GK[x]) != null) { notes.add(UB_GK[x] + " is already in the file - kept"); continue; }
      if (first) { blk.add(UB_GC[g]); first = false; }
      blk.add(UB_GL[x]);
      if (added.length() > 0) added.append(", ");
      added.append(UB_GK[x]);
    }
    at = at + UB_GS[g];
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 8192);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), (String[]) notes.toArray(new String[0]), added.toString() };
}""")
M(gcf, r"""
public static synchronized String migrate0216() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    String otext = new String(old, "ISO-8859-1");
    Object[] r = ubUpdate(otext);
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), UB_WHO, "before the 0.2.16 untiered batch update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated with the 0.2.16 Untiered batch: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (no Untiered rows / lines yet - the orange bags have nothing to give; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] notes = (String[]) r[1];
    String add = (String) r[2];
    int n = add.length() == 0 ? 0 : add.split(", ").length;
    String msg = "config.properties: the 0.2.16 Untiered batch was added at the end (" + n + " lines: the switches, the drop shares, 22 ut rows, 22 utfx rows); no value changed; the old file is kept in config-history";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.16 untiered batch: added " + n + " keys" + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.2.16 Untiered batch to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO''')
rep(r'''  @PKG@.GearCfg.migrate0215();
  @PKG@.GearCfg.load();''', r'''  @PKG@.GearCfg.migrate0215();
  @PKG@.GearCfg.migrate0216();
  @PKG@.GearCfg.load();''')

# ================================================================================================================ 7. levels, base twin, speed, documents, pool
rep(r'''public static int[] band(String id) {
  if (id == null) return new int[] { 0, 0, 3 };
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);''', r'''public static int[] band(String id) {
  if (id == null) return new int[] { 0, 0, 3 };
  // 0.2.16 (spec 4 item 6): an Untiered-table id lives in its row's range (the level-up cap and the band top read it)
  int[] ub = @PKG@.GearUt.band(id);
  if (ub != null) return new int[] { clamp(ub[0]), clamp(ub[1] < ub[0] ? ub[0] : ub[1]), 1 };
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);''')
rep(r'''public static String kunaiTwin(String id) {
  if (id == null) return id;''', r'''public static String kunaiTwin(String id) {
  if (id == null) return id;
  id = @PKG@.GearUtFx.baseOf(id);          // 0.2.16: an Untiered copy scales exactly like its base item (same interactions)''')
rep(r'''    Object r = armoryAsk(kind, id);
    if (!(r instanceof Object[])) return null;''', r'''    Object r = armoryAsk(kind, @PKG@.GearUtFx.baseOf(id));          // 0.2.16: an Armory Untiered copy shoots like its Iron base
    if (!(r instanceof Object[])) return null;''')
rep(r'''public static @BD@ ensure(String id, @BD@ doc) {
  if (doc == null || id == null || !on()) return doc;
  try {''', r'''public static @BD@ ensure(String id, @BD@ doc) {
  if (doc == null || id == null || !on()) return doc;
  // 0.2.16: an Untiered row with swing=<tier> fixes the tier - new documents get it, an old copy with another tier is healed (lazy heal: every
  // document write and the inventory scan pass through here)
  int fixedT = @PKG@.GearUtFx.swingOf(id);
  if (fixedT >= 0) {
    try {
      if (!@PKG@.GearData.identified(doc) || tierOf(doc) == fixedT) return doc;
      @BD@ c0 = doc.clone();
      c0.put("spd", new org.bson.BsonInt32(fixedT));
      @PKG@.GearUtFx.count(9);
      @PKG@.GearLog.line("SPEED " + id + " " + TIER[fixedT] + " (Untiered fixed tier)");
      return c0;
    } catch (Throwable x0) { return doc; }
  }
  try {''')
rep(r'''  if (@PKG@.GearUt.has(id)) { r = @PKG@.GearDefs.R_UT; if (lvl >= 0) lvl = @PKG@.GearUt.clampLv(id, lvl); }
  else if (r == @PKG@.GearDefs.R_UT) r = 0;''', r'''  if (@PKG@.GearUt.has(id)) { r = @PKG@.GearDefs.R_UT; if (lvl >= 0) lvl = @PKG@.GearUt.clampLv(id, lvl); }
  else if (r == @PKG@.GearDefs.R_UT) r = 0;
  else if (@PKG@.GearUtFx.mythicId(id)) r = @PKG@.GearDefs.R_MY;          // 0.2.16: gear.mythicItems (the Mythic developer bows) are always Mythic''')
rep(r'''M(gdt, "public static @BD@ legacy(String id) { return base(kindFor(id), @PKG@.GearUt.has(id) ? @PKG@.GearDefs.R_UT : 0, true, \"legacy\"); }")''',
    r'''M(gdt, "public static @BD@ legacy(String id) { return base(kindFor(id), @PKG@.GearUt.has(id) ? @PKG@.GearDefs.R_UT : (@PKG@.GearUtFx.mythicId(id) ? @PKG@.GearDefs.R_MY : 0), true, \"legacy\"); }")''')
rep(r'''    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id); } catch (Throwable x) { v = false; }''',
    r'''    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id) && !@PKG@.GearUtFx.mythicId(id); } catch (Throwable x) { v = false; }''')

# ================================================================================================================ 8. GearUtFx (2/4): the lines at a level + the totals
rep(r'''# ================================================================= 0.2.15 GearMine (3/4): a metal piece's tooltip lines (under the stat lines)''',
    r'''# ================================================================= 0.2.16 GearUtFx (2/4): a body line's value at a level (a roll at utline.power % of the
# stat max: GearRoll.bounds' formula), the lines of one identified Untiered document, the tricks of one (null = none)
M(gufx, r"""
public static int bodyVal(int si, int lvl) {
  if (si < 0 || si >= @PKG@.GearCfg.S_MAX.length) return 0;
  double f = @PKG@.GearLevel.factor(lvl);
  long v = Math.round((double) @PKG@.GearCfg.S_MAX[si] * (double) @PKG@.GearCfg.UT_POWER / 100.0 * f / 100.0);
  if (v < 1L) v = 1L;
  if (v > 100000L) v = 100000L;
  return (int) v;
}""")
M(gufx, r"""
public static Object[] rowOf(String id, @BD@ d) {
  if (d == null || !@PKG@.GearData.identified(d) || @PKG@.GearData.rarity(d) != @PKG@.GearDefs.R_UT) return null;
  return row(id);
}""")
M(gufx, r"""
public static int[] lines(String id, @BD@ d) {
  Object[] r = rowOf(id, d);
  if (r == null) return null;
  int[] b = (int[]) r[0];
  int[] f = (int[]) r[1];
  int[] t = new int[@PKG@.GearDefs.NS];
  int lv = @PKG@.GearLevel.level(id, d);
  for (int i = 0; i < b.length; i++) t[b[i]] = t[b[i]] + bodyVal(b[i], lv);
  for (int i = 0; i < t.length && i < f.length; i++) t[i] = t[i] + f[i];
  return t;
}""")
M(gufx, r"""
public static double[] tricks(String id, @BD@ d) {
  Object[] r = rowOf(id, d);
  if (r == null) return null;
  return (double[]) r[2];
}""")
# GearStats.totals: an active Untiered item's lines, with NO slot filter (spec 4 item 4: armor Damage counts), never through mods
M(gufx, r"""
public static void addTo(int[] t, String id, @BD@ d) {
  int[] l = lines(id, d);
  if (l == null || t == null) return;
  for (int i = 0; i < t.length && i < l.length; i++) {
    if (l[i] == 0) continue;
    long v = (long) t[i] + (long) l[i];
    if (v > 1000000000L) v = 1000000000L;
    if (v < -1000000000L) v = -1000000000L;
    t[i] = (int) v;
  }
}""")
# Server Setup check of a utfx row (the held item must be gear; every word known)
M(gufx, r"""
public static String checkRow(String key, String value) {
  String e = @PKG@.GearCfg.entryOf(key);
  if (e != null && !@PKG@.GearData.isGear(e)) return e + " is not gear - only Untiered weapons and armor have lines.";
  if (value == null) return null;
  StringBuilder b = new StringBuilder();
  if (parseRow(value, b) == null) return "Write <body lines>,<fixed lines> - e.g. mp cc,dmg-30 pierce+1 (no other commas).";
  if (b.length() > 0) return "Unknown words: " + b + " - body: live stat keys (str mp cc cd lsteal hpr def spd ...); fixed: key+N / key-N, swing=slow|medium|fast|superfast, tricks lowhp back front taken hp mregen range pierce heal kb.";
  return null;
}""")
M(gufx, "public static String pct(double v) { return @PKG@.GearMine.num(v) + \"%\"; }")
# the tooltip's trick lines (plain words; the orange trade-off line under them says the same for players)
M(gufx, r"""
public static String trickText(int k, double v) {
  String sg = v > 0.0 ? "+" : "-";
  double a = Math.abs(v);
  if (k == T_LOWHP) return "Damage " + sg + pct(a) + " while under half Health";
  if (k == T_BACK) return "Hits from behind " + sg + pct(a) + " damage";
  if (k == T_FRONT) return "Hits from the front " + sg + pct(a) + " damage";
  if (k == T_TAKEN) return "Damage taken " + sg + pct(a);
  if (k == T_HP) return "Max Health " + sg + pct(a);
  if (k == T_MREGEN) return "Mana regen " + sg + pct(a);
  if (k == T_RANGE) return "Shots only hurt within " + @PKG@.GearMine.num(a) + " blocks";
  if (k == T_PIERCE) return "Quick shots pierce every enemy in a line";
  if (k == T_HEAL) return "Heal orb heals " + sg + pct(a);
  if (k == T_KB) return "Knockback " + sg + pct(a);
  return TK[k] + " " + v;
}""")

# ================================================================= 0.2.15 GearMine (3/4): a metal piece's tooltip lines (under the stat lines)''')
rep(r'''      if (active(u, id, d)) addMods(t, d, false);
      else good = false;''', r'''      if (active(u, id, d)) { addMods(t, d, false); @PKG@.GearUtFx.addTo(t, id, d); }          // 0.2.16: + an Untiered weapon's lines
      else good = false;''')
rep(r'''      if (active(u, s.getItemId(), d)) addMods(t, d, true);
    }
    @PKG@.GearSet.addTo(t, u, armor);      // 0.2.14: complete armor sets''', r'''      if (active(u, s.getItemId(), d)) { addMods(t, d, true); @PKG@.GearUtFx.addTo(t, s.getItemId(), d); }      // 0.2.16: + Untiered lines
    }
    @PKG@.GearSet.addTo(t, u, armor);      // 0.2.14: complete armor sets''')

# tooltip: the Untiered lines above the orange trade-off line
rep(r'''# 0.2.2: GearView.hints (0.2.1's grey note under the levelled damage / resistance line in the item tooltip) is gone - Skyy: "hide it instead''',
    r'''# 0.2.16: an Untiered item's stat lines (body at its level + fixed) and its tricks, above the orange trade-off line
M(gvw, r"""
public static void utLines(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int[] l = @PKG@.GearUtFx.lines(id, d);
  if (l == null) {
    if (@PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_UT && !@PKG@.GearCfg.UT_ON) add(txt, col, "(Untiered lines are off on this server)", @PKG@.GearDefs.C_GRAY);
    return;
  }
  for (int i = 0; i < l.length; i++) if (l[i] != 0) add(txt, col, modLine(@PKG@.GearDefs.S_KEY[i], l[i]), null);
  double[] tk = @PKG@.GearUtFx.tricks(id, d);
  for (int k = 0; tk != null && k < tk.length; k++) if (tk[k] != 0.0) add(txt, col, @PKG@.GearUtFx.trickText(k, tk[k]), null);
}""")
# 0.2.2: GearView.hints (0.2.1's grey note under the levelled damage / resistance line in the item tooltip) is gone - Skyy: "hide it instead''')
rep(r'''  if (r == @PKG@.GearDefs.R_UT) { String un = @PKG@.GearUt.note(id); add(txt, col, un != null ? un : "Untiered - fixed stats.", hex); }
  @PKG@.GearSet.tipLines(owner, id, d, r, txt, col);''', r'''  if (r == @PKG@.GearDefs.R_UT) utLines(id, d, txt, col);        // 0.2.16
  if (r == @PKG@.GearDefs.R_UT) { String un = @PKG@.GearUt.note(id); add(txt, col, un != null ? un : "Untiered - fixed stats.", hex); }
  @PKG@.GearSet.tipLines(owner, id, d, r, txt, col);''')

# ================================================================================================================ 9. GearUtFx (3/4): Health %, Mana regen, taken
rep(r'''# ================================================================= GearFx: per-player stat effects (spec 3.5 part 2, 4.2), helpers''',
    r'''# ================================================================= 0.2.16 GearUtFx (3/4): the tricks of what a player holds + wears (active only), the max Health %
# modifier, the Mana regen % (SkyySkills' skill:fn:manaregen registry), damage taken; world thread (inventory + stat map)
M(gufx, r"""
public static double[] sum(java.util.UUID u, @IS@ weapon, @IC@ armor) {
  if (!@PKG@.GearCfg.UT_ON) return null;
  double[] o = null;
  if (weapon != null && !weapon.isEmpty()) {
    String id = weapon.getItemId();
    int sl = @PKG@.GearData.slotOf(id);
    if (sl == 0 || sl == 1) {
      @BD@ d = @PKG@.GearData.effective(id, weapon.getMetadata());
      double[] tk = tricks(id, d);
      if (tk != null && @PKG@.GearStats.active(u, id, d)) { o = new double[TK.length]; for (int k = 0; k < o.length; k++) o[k] = o[k] + tk[k]; }
    }
  }
  if (armor != null) {
    for (int i = 0; i < armor.getCapacity(); i++) {
      @IS@ s = armor.getItemStack((short) i);
      if (s == null || s.isEmpty() || @PKG@.GearData.slotOf(s.getItemId()) != 2) continue;
      @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
      double[] tk = tricks(s.getItemId(), d);
      if (tk == null || !@PKG@.GearStats.active(u, s.getItemId(), d)) continue;
      if (o == null) o = new double[TK.length];
      for (int k = 0; k < o.length; k++) o[k] = o[k] + tk[k];
    }
  }
  return o;
}""")
# the max Health % as ONE additive MAX modifier skyygear_ut_hp = pct x (max without it); 0 = removed. Raising never touches the current value;
# lowering clamps it (vanilla's rule when a piece with less Health goes on). Every second while the player is online (GearFx.second).
# Fix round (ut02 review, engine review 1's rule for the armor locks): a change that LOWERS max while the modifier stays (want < have, a
# positive % shrinking or a negative % growing) waits until the engine's own Armor modifier holds the worn armor's full Health sum
# (synced, computed by GearFx.second) - right after a join the saved modifier can sit on a max without the armor's +Health, and
# recomputing then would clamp the current Health; removing it (nothing worn / busy / lines off) stays immediate
M(gufx, r"""
public static float hpWant(float maxNow, float have, double pct) {
  if (pct == 0.0) return 0.0f;
  double base = (double) maxNow - (double) have;
  if (!(base > 0.0)) return 0.0f;
  double w = base * pct / 100.0;
  if (w < -base * 0.9) w = -base * 0.9;
  return (float) w;
}""")
M(gufx, r"""
public static void hpApply(@ESM@ m, double pct, boolean synced) {
  if (m == null) return;
  int hi = @DST@.getHealth();
  @ESV@ v = m.get(hi);
  if (v == null) return;
  @MODF@ cur = m.getModifier(hi, HPKEY);
  float have = cur instanceof @SMO@ ? ((@SMO@) cur).getAmount() : 0.0f;
  float want = hpWant(v.getMax(), have, pct);
  if (want == 0.0f) { if (cur != null) { m.removeModifier(hi, HPKEY); count(4); } return; }
  if (cur != null && Math.abs(want - have) < 0.01f) return;
  if (want < have && !synced) return;          // fix round: lowering max waits for the engine's armor sync (next second)
  m.putModifier(hi, HPKEY, new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, want));
  count(4);
}""")
M(gufx, r"""
public static void manaApply(java.util.UUID u, double pct) {
  if (u == null) return;
  Object o = MREG.get(u);
  if (o == null && pct == 0.0) return;          // fix round (ut02 review): nothing posted, nothing wanted - no bridge lookup, no count
  double last = o instanceof Double ? ((Double) o).doubleValue() : 0.0;
  if (o != null && Math.abs(last - pct) < 0.0001) return;
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:manaregen");
  if (f == null) { if (pct == 0.0) MREG.remove(u); return; }
  try {
    if (pct == 0.0) { if (o != null) f.apply(new Object[] { "remove", u, MANA_SRC }); MREG.remove(u); }
    else { f.apply(new Object[] { "add", u, MANA_SRC, Double.valueOf(pct) }); MREG.put(u, Double.valueOf(pct)); }
    count(5);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("utmana", "Untiered Mana regen: skill:fn:manaregen failed (" + t + ") - the robes' Mana line does nothing"); }
}""")
# GearFx.second (1 s, world thread): busy / part switches off = both gone
M(gufx, r"""
public static void secondPass(java.util.UUID u, @ESM@ m, @IS@ weapon, @IC@ armor, boolean synced) {
  if (u == null) return;
  double hp = 0.0;
  double mr = 0.0;
  if (!@PKG@.Gear.busy(u) && @PKG@.GearCfg.PART_STATS) {
    double[] tk = sum(u, weapon, armor);
    if (tk != null) { hp = tk[T_HP]; mr = tk[T_MREGEN]; }
  }
  try { hpApply(m, hp, synced); } catch (Throwable t) { @PKG@.Gear.warnOnce("uthp", "Untiered max Health line failed: " + t); }
  manaApply(u, mr);
}""")
M(gufx, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  if (MREG.remove(u) == null) return;
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:manaregen");
  try { if (f != null) f.apply(new Object[] { "remove", u, MANA_SRC }); } catch (Throwable t) { }
}""")
# GearArmorSys: the worn Untiered armor's damage taken % (after Defense; entity damage only, like Defense)
M(gufx, r"""
public static double taken(java.util.UUID u, @IC@ armor) {
  if (!@PKG@.GearCfg.PART_STATS) return 0.0;
  double[] tk = sum(u, null, armor);
  return tk == null ? 0.0 : tk[T_TAKEN];
}""")
M(gufx, r"""
public static float takenAmount(float a, double pct) {
  if (pct == 0.0) return a;
  double f = 1.0 + pct / 100.0;
  if (f < 0.0) f = 0.0;
  return (float) ((double) a * f);
}""")

# ================================================================= GearFx: per-player stat effects (spec 3.5 part 2, 4.2), helpers''')
rep(r'''  armorPass(u, pr, cb, ref, inv.getArmor(), true);
  @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  if (m == null) return;
  if (!@PKG@.GearCfg.PART_STATS) { REGEN.remove(u); LEECH.remove(u); MANA.remove(u); return; }''', r'''  armorPass(u, pr, cb, ref, inv.getArmor(), true);
  @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  if (m == null) return;
  // fix round (ut02 review): is the engine's own Armor Health modifier in sync with the worn armor (the armor locks' check)?
  boolean hsy = true;
  try {
    int hix = @DST@.getHealth();
    Object hfo = @PKG@.GearArmor.fullSums(inv.getArmor(), @PKG@.GearArmor.brokenFactor(cb.getExternalData())).get(Integer.valueOf(hix));
    hsy = Math.abs(engineArmor(m, hix) - (hfo instanceof Float ? ((Float) hfo).floatValue() : 0.0f)) <= 0.01f;
  } catch (Throwable t) { hsy = true; }
  @PKG@.GearUtFx.secondPass(u, m, @PKG@.GearStats.hand(inv), inv.getArmor(), hsy);          // 0.2.16: the Untiered max Health % + Mana regen %
  if (!@PKG@.GearCfg.PART_STATS) { REGEN.remove(u); LEECH.remove(u); MANA.remove(u); return; }''')
rep(r'''  @PKG@.GearMine.clear(u);                    // 0.2.15: the lamp key + the mining cache
  @PKG@.GearStats.PCACHE.remove(u);           // 0.2.15: the parsed pets:stats''', r'''  @PKG@.GearMine.clear(u);                    // 0.2.15: the lamp key + the mining cache
  @PKG@.GearStats.PCACHE.remove(u);           // 0.2.15: the parsed pets:stats
  @PKG@.GearUtFx.forget(u);                   // 0.2.16: the Untiered Mana regen source''')
rep(r'''      int def = t[@PKG@.GearHit.I_DEF];
      if (def > 0) {
        double sc = (double) @PKG@.GearCfg.DEF_SCALE;
        d.setAmount((float) ((double) d.getAmount() * sc / (sc + (double) def)));
      }''', r'''      int def = t[@PKG@.GearHit.I_DEF];
      if (def > 0) {
        double sc = (double) @PKG@.GearCfg.DEF_SCALE;
        d.setAmount((float) ((double) d.getAmount() * sc / (sc + (double) def)));
      }
      // 0.2.16: the worn Untiered armor's damage taken % (the Courier's Leathers +5 % a piece), after Defense
      double utk = @PKG@.GearUtFx.taken(vu, full);
      if (utk != 0.0) { d.setAmount(@PKG@.GearUtFx.takenAmount(d.getAmount(), utk)); @PKG@.GearUtFx.count(3); }''')

# ================================================================================================================ 10. GearUtFx (4/4): the hit tricks
rep(r'''# ================================================================= damage systems (spec 4.3 order): GearHitSys -> engine armor ->''',
    r'''# ================================================================= 0.2.16 GearUtFx (4/4): THE HIT TRICKS of a player's weapon hit (GearHitSys, after weaponHit):
# lowhp (attacker Health under half), back / front (the target's head facing: the 120 degree cone behind / in front), range (a shot past N
# blocks from the shooter deals nothing), kb (the hit's knockback modifier x (1 + kb %), the speed-tier way). Pure parts first (harness)
# cone: 1 = the attacker stands behind the target, -1 = in front, 0 = the sides, -2 = unknown (no facing / same spot)
M(gufx, r"""
public static int cone(double fx, double fz, double dx, double dz) {
  double lf = Math.sqrt(fx * fx + fz * fz);
  double ld = Math.sqrt(dx * dx + dz * dz);
  if (!(lf > 0.000001) || !(ld > 0.000001)) return -2;
  double c = (fx * dx + fz * dz) / (lf * ld);
  if (c >= 0.5) return -1;
  if (c <= -0.5) return 1;
  return 0;
}""")
M(gufx, r"""
public static double hitMult(double[] tk, double hpFrac, int cone, double dist, boolean shot) {
  if (tk == null) return 1.0;
  double f = 1.0;
  if (tk[T_LOWHP] != 0.0 && hpFrac >= 0.0 && hpFrac < 0.5) { double x = 1.0 + tk[T_LOWHP] / 100.0; f = f * (x > 0.0 ? x : 0.0); }
  if (cone == 1 && tk[T_BACK] != 0.0) { double x = 1.0 + tk[T_BACK] / 100.0; f = f * (x > 0.0 ? x : 0.0); }
  if (cone == -1 && tk[T_FRONT] != 0.0) { double x = 1.0 + tk[T_FRONT] / 100.0; f = f * (x > 0.0 ? x : 0.0); }
  if (shot && tk[T_RANGE] > 0.0 && dist >= 0.0 && dist > tk[T_RANGE]) f = 0.0;
  return f;
}""")
# FIXER 2: a Short Notice shot past its range is CANCELLED (not just x0), so GearTrueSys adds no True Damage / element damage and
# GearLeechSys pays no Life / Mana Steal on it (the same way GearHitSys cancels a gated hit)
M(gufx, r"""
public static boolean rangeCut(double[] tk, double dist, boolean shot) {
  return tk != null && shot && tk[T_RANGE] > 0.0 && dist >= 0.0 && dist > tk[T_RANGE];
}""")
M(gufx, r"""
public static double hpFrac(@ESM@ m) {
  if (m == null) return -1.0;
  try {
    @ESV@ v = m.get(@DST@.getHealth());
    if (v == null || !(v.getMax() > 0.0f)) return -1.0;
    return (double) v.get() / (double) v.getMax();
  } catch (Throwable t) { return -1.0; }
}""")
M(gufx, r"""
public static @VEC@ pos(@CB@ buf, @REF@ r) {
  if (buf == null || r == null || !r.isValid()) return null;
  @TC@ tc = (@TC@) buf.getComponent(r, @TC@.getComponentType());
  return tc == null ? null : tc.getPosition();
}""")
M(gufx, r"""
public static void onHit(@DMG@ d, @CB@ buf, @REF@ att, @REF@ vic, java.util.UUID u, @IS@ main, @IC@ arm, boolean shot) {
  if (d == null || u == null || buf == null || d.isCancelled() || !@PKG@.GearCfg.PART_STATS || !@PKG@.GearCfg.UT_ON) return;
  try {
    double[] tk = sum(u, main, arm);
    if (tk == null) return;
    double hf = -1.0;
    if (tk[T_LOWHP] != 0.0 && att != null && att.isValid()) hf = hpFrac((@ESM@) buf.getComponent(att, @ESM@.getComponentType()));
    int cn = -2;
    double dist = -1.0;
    if (tk[T_BACK] != 0.0 || tk[T_FRONT] != 0.0 || tk[T_RANGE] != 0.0) {
      @VEC@ pa = pos(buf, att);
      @VEC@ pv = pos(buf, vic);
      if (pa != null && pv != null) {
        double dx = pa.x - pv.x;
        double dz = pa.z - pv.z;
        double dy = pa.y - pv.y;
        dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (tk[T_BACK] != 0.0 || tk[T_FRONT] != 0.0) {
          @HRC@ hr = vic == null || !vic.isValid() ? null : (@HRC@) buf.getComponent(vic, @HRC@.getComponentType());
          @VEC@ fw = hr == null ? null : hr.getDirection();
          if (fw != null) cn = cone(fw.x, fw.z, dx, dz);
        }
      }
    }
    if (rangeCut(tk, dist, shot)) {
      d.setAmount(0.0f);
      d.setCancelled(true);
      count(1);
      try { if (vic != null && vic.isValid()) buf.tryRemoveComponent(vic, @KBC@.getComponentType()); } catch (Throwable t2) { }
      return;
    }
    double f = hitMult(tk, hf, cn, dist, shot);
    if (f != 1.0) {
      d.setAmount((float) ((double) d.getAmount() * f));
      count(f == 0.0 ? 1 : 0);
    }
    if (tk[T_KB] != 0.0 && vic != null && vic.isValid() && !shot) {
      @KBC@ kc = (@KBC@) buf.getComponent(vic, @KBC@.getComponentType());
      double k = 1.0 + tk[T_KB] / 100.0;
      if (kc != null && k >= 0.0) { kc.addModifier(k); count(2); }
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("uthit", "Untiered hit tricks failed (" + t + ") - the hit keeps its amount"); }
}""")

# ================================================================= damage systems (spec 4.3 order): GearHitSys -> engine armor ->''')
rep(r'''        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);
        // 0.2.6 weapon speed tiers: the hit's knockback + stats on hit x the same hit weight (nothing when it was x1)
        @PKG@.GearSpeed.perHit(d, buf, att, vic);''', r'''        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);
        // 0.2.6 weapon speed tiers: the hit's knockback + stats on hit x the same hit weight (nothing when it was x1)
        @PKG@.GearSpeed.perHit(d, buf, att, vic);
        // 0.2.16: the Untiered hit tricks (low Health, backstab cone, shot range, knockback)
        @PKG@.GearUtFx.onHit(d, buf, att, vic, u, main, arm, shot);''')

# ================================================================================================================ 11. orange bags: the type pick + the three swaps
rep(r'''# ---------------------------------------------------------------- GearLoot (extra mob roll, chest level + extra bag, counters)''',
    r'''# ---------------------------------------------------------------- 0.2.16 GearUt: an orange bag at level L for a finder (spec 3.2): only when an
# Untiered row covers L itself; the type = armor (utbag.armorShare %) or a weapon type weighted by its rows covering L x utbag.classLean for the
# finder's class weapons (lean prefixes); null = nothing fits
M(gut, r"""
public static boolean covers(int L) {
  if (L < 1 || L > 101) return false;
  return levels(-1)[L];
}""")
M(gut, r"""
public static int rowsOf(int ty, int L) {
  Object[] t = @PKG@.GearCfg.UTAB;
  String[] ids = (String[]) t[0];
  int n = 0;
  for (int i = 0; i < ids.length; i++) if (match(t, i, ty, L)) n++;
  return n;
}""")
M(gut, r"""
public static int pickTypeFor(int L, String[] lean) {
  int nt = @PKG@.GearPool.T_KEY.length;
  double[] wa = new double[nt];
  double[] ww = new double[nt];
  double sa = 0.0;
  double sw = 0.0;
  for (int ty = 0; ty < nt; ty++) {
    int n = rowsOf(ty, L);
    if (n <= 0) continue;
    if (@PKG@.GearPool.T_ARM[ty]) { wa[ty] = (double) n; sa = sa + wa[ty]; }
    else {
      ww[ty] = (double) n * (@PKG@.GearPool.leanHit(@PKG@.GearPool.T_KEY[ty], lean) ? (double) @PKG@.GearCfg.UT_LEAN : 1.0);
      sw = sw + ww[ty];
    }
  }
  if (!(sa > 0.0) && !(sw > 0.0)) return -1;
  boolean armor = !(sw > 0.0) || (sa > 0.0 && @PKG@.GearRoll.RNG.nextDouble() * 100.0 < (double) @PKG@.GearCfg.UT_ARMOR);
  double[] w = armor ? wa : ww;
  double r = @PKG@.GearRoll.RNG.nextDouble() * (armor ? sa : sw);
  int last = -1;
  for (int ty = 0; ty < nt; ty++) {
    if (!(w[ty] > 0.0)) continue;
    last = ty;
    r = r - w[ty];
    if (r < 0.0) return ty;
  }
  return last;
}""")
M(gut, r"""
public static @IS@ bagFor(int L, String[] lean, String src, String ls, int tier) {
  if (!covers(L)) return null;
  int ty = pickTypeFor(L, lean);
  if (ty < 0) return null;
  return bag(L, ty, src, ls, tier);
}""")
# the swap: a bag that already dropped becomes an orange one with share % (never an extra roll); the same bag otherwise
M(gut, r"""
public static @IS@ swap(@IS@ box, int L, double share, String[] lean, String src, String ls, int tier, int cnt) {
  if (box == null || !(share > 0.0) || !covers(L)) return box;
  if (!(@PKG@.GearRoll.RNG.nextDouble() * 100.0 < share)) return box;
  @IS@ ub = bagFor(L, lean, src, ls, tier);
  if (ub == null) return box;
  @PKG@.GearUtFx.count(cnt);
  return ub;
}""")
M(gut, r"""
public static String dropsText() {
  double[] lg = @PKG@.GearUtFx.lug(@PKG@.GearCfg.UT_LUG);
  return "orange bags: " + @PKG@.GearMine.num(@PKG@.GearCfg.UT_MOB) + "% of extra mob bags, " + @PKG@.GearMine.num(@PKG@.GearCfg.UT_CHEST) + "% of extra chest bags, luggage "
    + (lg == null ? "?" : @PKG@.GearMine.num(lg[0]) + " / " + @PKG@.GearMine.num(lg[1]) + " / " + @PKG@.GearMine.num(lg[2]) + " / " + @PKG@.GearMine.num(lg[3]) + "%")
    + " (only at Untiered levels; armor " + @PKG@.GearCfg.UT_ARMOR + "%, own-class weapons x" + @PKG@.GearCfg.UT_LEAN + "); swapped so far: mobs " + @PKG@.GearUtFx.N[6] + ", chests " + @PKG@.GearUtFx.N[7] + ", luggage " + @PKG@.GearUtFx.N[8];
}""")

# ---------------------------------------------------------------- GearLoot (extra mob roll, chest level + extra bag, counters)''')
rep(r'''  @IS@ box = @PKG@.GearUnid.roll(lvl, -1, "mob", "mob", 0, lean(ku), 1, lvl);
  if (box == null) { count(4); return 0; }''', r'''  String[] lk = lean(ku);
  @IS@ box = @PKG@.GearUnid.roll(lvl, -1, "mob", "mob", 0, lk, 1, lvl);
  if (box == null) { count(4); return 0; }
  box = @PKG@.GearUt.swap(box, lvl, @PKG@.GearCfg.UT_MOB, lk, "mob", "mob", 0, 6);          // 0.2.16: utdrop.mob % of them orange''')
rep(r'''  @IS@ box = @PKG@.GearUnid.roll(L, -1, "chest", "zone", 0, null, 2, 0);
  if (box == null) { count(4); return 0; }''', r'''  @IS@ box = @PKG@.GearUnid.roll(L, -1, "chest", "zone", 0, null, 2, 0);
  if (box == null) { count(4); return 0; }
  box = @PKG@.GearUt.swap(box, L, @PKG@.GearCfg.UT_CHEST, null, "chest", "zone", 0, 7);          // 0.2.16: utdrop.chest % of them orange''')
rep(r'''    int ty = a[0] instanceof String ? @PKG@.GearPool.typeIdx((String) a[0]) : -1;
    if (a[0] instanceof String && ty < 0) return null;
    return @PKG@.GearUnid.roll(L, ty, src, "bridge", tier, null, 2, shift);''', r'''    int ty = a[0] instanceof String ? @PKG@.GearPool.typeIdx((String) a[0]) : -1;
    if (a[0] instanceof String && ty < 0) return null;
    @IS@ nb = @PKG@.GearUnid.roll(L, ty, src, "bridge", tier, null, 2, shift);
    // 0.2.16: Unclaimed Luggage (a tier 1-4 and no type asked): utdrop.luggage % per bag of that tier become orange
    if (a[0] == null && tier >= 1 && nb != null) {
      double[] lg = @PKG@.GearUtFx.lug(@PKG@.GearCfg.UT_LUG);
      java.util.UUID fu = a.length > 4 && a[4] instanceof java.util.UUID ? (java.util.UUID) a[4] : null;
      String[] fl = null;
      if (fu != null) fl = @PKG@.GearLoot.lean(fu);
      if (lg != null) nb = @PKG@.GearUt.swap(nb, L, lg[tier - 1], fl, src, "bridge", tier, 8);
    }
    return nb;''')
rep(r'''M(gloot, r"""
public static synchronized String countsText() {''', r'''M(gloot, r"""
public static synchronized String countsText0() {''')
rep(r'''# ---------------------------------------------------------------- GearBoxFn: gear:fn:box (never throws, never touches ECS)''',
    r'''M(gloot, r"""
public static synchronized String countsText() {
  return countsText0() + "; " + @PKG@.GearUt.dropsText();          // 0.2.16
}""")

# ---------------------------------------------------------------- GearBoxFn: gear:fn:box (never throws, never touches ECS)''')

# ================================================================================================================ 12. the market wall split
rep(r'''F(gwall, 'public static final String REASON = "Mythic, Untiered and Set gear never goes on the market - trade it directly with another player.";')''',
    r'''F(gwall, 'public static final String REASON = "Mythic, Untiered and quest / boss Set gear never goes on the market - trade it directly with another player.";')''')
rep(r'''  if (!@PKG@.GearData.gearish(id, md)) return null;
  @BD@ d = @PKG@.GearData.effective(id, md);
  if (d == null) return UNREAD;
  if (fixed(@PKG@.GearData.rarity(d)) || @PKG@.GearSet.of(d) != null) return REASON;
  return null;''', r'''  if (!@PKG@.GearData.gearish(id, md)) return null;
  @BD@ d = @PKG@.GearData.effective(id, md);
  if (d == null) return UNREAD;
  int r = @PKG@.GearData.rarity(d);
  if (r == @PKG@.GearDefs.R_MY || r == @PKG@.GearDefs.R_UT) return REASON;
  if (r == @PKG@.GearDefs.R_SET || @PKG@.GearSet.of(d) != null) {
    // 0.2.16 (Skyy 2026-10-09 "Gathering sets sellable"): a crafted gathering Set piece (mining_ / foraging_ / farming_ set) may be sold.
    // Fix round (ut02 review): ONLY the document's own set field counts - never the by-id Mining Set fallback (GearSet.sidOf), so a quest /
    // boss Set piece on a metal id whose set field was cleared (/gear set clear keeps the rarity) stays walled. Every new mining piece
    // carries its set field (GearMine.doc); an old metal piece of a plain rarity never reaches this branch (it sells as before)
    if (@PKG@.GearUtFx.gathering(@PKG@.GearSet.of(d))) return null;
    return REASON;
  }
  return null;''')

# ================================================================================================================ 13. gear:fn:utfx (SkyyArmory reads pierce / heal / dmg)
rep(r'''_fns = "\n".join('  br.put("gear:fn:%s", new @PKG@.GearFn(%d));' % (n, i) for i, n in enumerate(
    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve", "speed", "grant", "tradeable")))''',
    r'''_fns = "\n".join('  br.put("gear:fn:%s", new @PKG@.GearFn(%d));' % (n, i) for i, n in enumerate(
    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve", "speed", "grant", "tradeable",
     "utfx")))       # 0.2.16''')
rep(r'''M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 12) return grant(o);          // 0.2.14''', r'''# 0.2.16 gear:fn:utfx (SkyyArmory 0.1.15): Object[] { String item id, String word } -> Double (the item's Untiered value of that word: a trick
# name or a fixed stat key such as "dmg"; 0 = none / not Untiered / part.utLines off), or null for bad input. By ID: a held Untiered copy
# always carries an Untiered document (G1), so the id answers what its lines do.
M(gfn, r"""
public static Object utfx(Object o) {
  if (!(o instanceof Object[])) return null;
  Object[] a = (Object[]) o;
  if (a.length < 2 || !(a[0] instanceof String) || !(a[1] instanceof String)) return null;
  String id = (String) a[0];
  if (!@PKG@.GearUt.has(id)) return Double.valueOf(0.0);
  Object[] r = @PKG@.GearUtFx.row(id);
  if (r == null) return Double.valueOf(0.0);
  int t = @PKG@.GearUtFx.trick((String) a[1]);
  if (t >= 0) return Double.valueOf(((double[]) r[2])[t]);
  int si = @PKG@.GearDefs.sIndex(((String) a[1]).trim());
  if (si >= 0) return Double.valueOf((double) ((int[]) r[1])[si]);
  return Double.valueOf(0.0);
}""")
M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 14) return utfx(o);           // 0.2.16
    if (m == 12) return grant(o);          // 0.2.14''')

# ================================================================================================================ 14. /gear ut
rep(r'''        ("set", "GearSetCmd", "Put the held armor in a set: /gear set <set id|clear>", True)]''',
    r'''        ("set", "GearSetCmd", "Put the held armor in a set: /gear set <set id|clear>", True),
        # 0.2.16 the Untiered batch
        ("ut", "GearUtCmd", "Untiered items: /gear ut (the list) or /gear ut give <item> [level]", True)]''')
rep(r'''C(subc["loot"], r"""
public GearLootCmd() {''', r'''C(subc["ut"], r"""
public GearUtCmd() {
  super("ut", "Untiered items: /gear ut (the list) or /gear ut give <item> [level]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["loot"], r"""
public GearLootCmd() {''')
rep(r'''  addSubCommand(new @PKG@.GearSetCmd());
}""")''', r'''  addSubCommand(new @PKG@.GearSetCmd());
  addSubCommand(new @PKG@.GearUtCmd());
}""")''')
rep(r'''# 0.2.11 /gear box <rarity|random> [level] [type key or name]: a bag in your inventory (storage first); /gear loot: counters + pool''',
    r'''# 0.2.16 /gear ut: every Untiered row (usable or why not, its lines) + the drop shares; /gear ut give <item id or name> [level]: an identified Untiered
# item through gear:fn:grant's core (level kept in the row's range), storage first
M(gad, r"""
public static void utCmd(@PR@ pr, @INV@ inv, String rest) {
  String[] tk = rest.trim().length() == 0 ? new String[0] : rest.trim().split("\\s+");
  if (tk.length == 0) {
    Object[] t = @PKG@.GearCfg.UTAB;
    String[] ids = (String[]) t[0];
    msg(pr, @PKG@.GearUt.statusText() + " - " + (@PKG@.GearCfg.UT_ON ? "lines on" : "lines OFF (part.utLines)") + "; " + @PKG@.GearUt.dropsText());
    for (int i = 0; i < ids.length; i++) {
      boolean ok = @PKG@.GearUt.ok(t, i);
      String why = ok ? "" : (@PKG@.Gear.item(ids[i]) == null ? " - NOT on this server (missing item)" : " - not usable (no bag type / a recipe makes it)");
      Object[] r = @PKG@.GearUtFx.row(ids[i]);
      int ty = @PKG@.GearPool.typeOfId(ids[i]);
      msg(pr, ids[i] + " Lv " + ((int[]) t[1])[i] + "-" + ((int[]) t[2])[i] + " " + (ty >= 0 ? @PKG@.GearPool.T_NAME[ty] : "?") + (r == null ? " (no utfx lines)" : "") + why);
    }
    msg(pr, "Mythic items: " + @PKG@.GearCfg.MYTH_IDS + "; gathering sets " + (@PKG@.GearCfg.GSELL ? "sellable (" + @PKG@.GearCfg.GSELL_PRE + ")" : "walled"));
    return;
  }
  if (!tk[0].equalsIgnoreCase("give") || tk.length < 2) { msg(pr, "usage: /gear ut  or  /gear ut give <item id or name> [level]"); return; }
  StringBuilder sugg = new StringBuilder();
  String id = resolve(tk[1], sugg);
  if (id == null) { msg(pr, "no single item matches '" + tk[1] + "'" + (sugg.length() > 0 ? " - " + sugg : "")); return; }
  if (!@PKG@.GearUt.has(id)) { msg(pr, id + " is not in the Untiered table - /gear ut lists them"); return; }
  int L = -1;
  if (tk.length > 2) { try { L = Integer.parseInt(tk[2]); } catch (Throwable t) { msg(pr, "the level must be a number"); return; } }
  Object g = @PKG@.GearFn.grant(new Object[] { id, Integer.valueOf(L), "untiered", "", "", pr.getUuid(), "admin" });
  if (!(g instanceof @IS@)) { msg(pr, "could not make " + id + " (see the log)"); return; }
  @IS@ s = (@IS@) g;
  boolean in = give(inv, s);
  @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
  @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " ut give " + id + " lv" + @PKG@.GearLevel.level(id, d) + (in ? "" : " (inventory full)"));
  msg(pr, (in ? "gave " : "NOT given (inventory full): ") + id + " - Untiered, Lv " + @PKG@.GearLevel.level(id, d));
}""")
# 0.2.11 /gear box <rarity|random> [level] [type key or name]: a bag in your inventory (storage first); /gear loot: counters + pool''')
rep(r'''    if (action.equals("loot")) { lootCmd(pr); return; }''', r'''    if (action.equals("loot")) { lootCmd(pr); return; }
    if (action.equals("ut")) { utCmd(pr, inv, rest); return; }          // 0.2.16''')

# ================================================================================================================ 15. ready line, class list, jar checks
rep("| box | loot | set, node skyygear.admin", "| box | loot | set | ut, node skyygear.admin")          # 0.2.16: /gear ut
rep(r'''(" + @PKG@.GearUt.statusText() + "); " + @PKG@.GearMine.statusText() + "; gear:fn:curve, gear:fn:speed, gear:fn:grant, gear:fn:tradeable;''',
    r'''(" + @PKG@.GearUt.statusText() + ", Untiered lines " + (@PKG@.GearCfg.UT_ON ? "on" : "OFF") + ", gathering sets " + (@PKG@.GearCfg.GSELL ? "sellable" : "walled") + "); " + @PKG@.GearMine.statusText() + "; gear:fn:curve, gear:fn:speed, gear:fn:grant, gear:fn:tradeable, gear:fn:utfx;''')
rep(r'''SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES + G1_CLASSES + GM_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''', r'''SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES + G1_CLASSES + GM_CLASSES + UB_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')
rep(r'''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(BAG_ITEMS), "SkyyGear 0.2.11 ships only the 7 mystery bag items"''',
    r'''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS)), "SkyyGear 0.2.16 ships the 8 mystery bags + the 16 Untiered copies"
    for _k, _v in list(UT_ITEMS.items()) + list(UT_FILES.items()):          # 0.2.16
        assert _jz.read(_k) == (_v.encode("utf-8") if isinstance(_v, str) else _v), "Untiered file missing from the jar: " + _k''')
rep(r'''print("0.2.15: mining armor - GearMine; %d pieces out of the bag pool; rows garmor.miningOn / garmor.mining (7) / garmor.miningShare / armor.fortune.cap / "''',
    r'''print("0.2.16: the Untiered batch - GearUtFx; %d ut rows + %d utfx rows, %d copies, Bo bag type, %d developer bows out of the pool, gear:fn:utfx; "
      "migrate0216 block %d lines" % (len(UT_ROWS), len(UT_ROWS), len(UT_ITEMS), len(DEV_BOWS), len(UB_LINES)))
print("0.2.15: mining armor - GearMine; %d pieces out of the bag pool; rows garmor.miningOn / garmor.mining (7) / garmor.miningShare / armor.fortune.cap / "''')

# ================================================================================================================ 16. fix round (ut02 review): the Untiered re-roll
# UT-First-Batch-Build 3.1: an Untiered item re-rolls into ANOTHER Untiered item - a weapon into any other Untiered weapon row (own-class
# weapons x utbag.classLean), an armor piece into another piece of its own Untiered set (same id family, any other slot) - never into
# itself. Level uniform inside the bag's range AND the new row's range; the box keeps the bag's range, its type becomes the new item's.
# Nothing else to roll = refused BEFORE any coin is taken (rerollWhy(id, d)).
rep(r'''# a random bag type among the usable rows covering L (L < 0 = any level); -1 = none''', r'''# fix round (ut02 review): the re-roll family of an Untiered id - weapons share one ("W"), an armor piece's family is its id up to the last
# "_" (Armor_UT_FilingCabinet_Head -> Armor_UT_FilingCabinet = its set)
M(gut, r"""
public static String family(String id) {
  if (id == null) return "";
  if (!id.startsWith("Armor_")) return "W";
  int k = id.lastIndexOf('_');
  return k > 0 ? id.substring(0, k) : id;
}""")
M(gut, r"""
public static boolean rerollFits(Object[] t, int i, String cur, int lo, int hi) {
  if (!ok(t, i)) return false;
  String id = ((String[]) t[0])[i];
  if (cur == null || id.equals(cur) || !family(id).equals(family(cur))) return false;
  return ((int[]) t[1])[i] <= hi && lo <= ((int[]) t[2])[i];
}""")
M(gut, r"""
public static int rerollCount(String cur, int lo, int hi) {
  Object[] t = @PKG@.GearCfg.UTAB;
  String[] ids = (String[]) t[0];
  int n = 0;
  for (int i = 0; i < ids.length; i++) if (rerollFits(t, i, cur, lo, hi)) n++;
  return n;
}""")
M(gut, r"""
public static String rerollItem(String cur, int lo, int hi, String[] lean) {
  Object[] t = @PKG@.GearCfg.UTAB;
  String[] ids = (String[]) t[0];
  double[] w = new double[ids.length];
  double sum = 0.0;
  for (int i = 0; i < ids.length; i++) {
    if (!rerollFits(t, i, cur, lo, hi)) continue;
    int ty = @PKG@.GearPool.typeOfId(ids[i]);
    boolean ln = ty >= 0 && !@PKG@.GearPool.T_ARM[ty] && @PKG@.GearPool.leanHit(@PKG@.GearPool.T_KEY[ty], lean);
    w[i] = ln ? (double) @PKG@.GearCfg.UT_LEAN : 1.0;
    sum = sum + w[i];
  }
  if (!(sum > 0.0)) return null;
  double r = @PKG@.GearRoll.RNG.nextDouble() * sum;
  String last = null;
  for (int i = 0; i < ids.length; i++) {
    if (!(w[i] > 0.0)) continue;
    last = ids[i];
    r = r - w[i];
    if (r < 0.0) return ids[i];
  }
  return last;
}""")
M(gut, r"""
public static int rerollLevel(String id, int lo, int hi) {
  int[] b = band(id);
  if (b == null) return -1;
  int a = lo > b[0] ? lo : b[0];
  int c = hi < b[1] ? hi : b[1];
  if (a < 1) a = 1;
  if (c > 100) c = 100;
  if (c < a) return -1;
  return a + @PKG@.GearRoll.RNG.nextInt(c - a + 1);
}""")
# a random bag type among the usable rows covering L (L < 0 = any level); -1 = none''')
rep(r'''  if (rar(b) == @PKG@.GearDefs.R_UT) return @PKG@.GearUt.why(ty, lo(b), hi(b));       // 0.2.14''',
    r'''  if (rar(b) == @PKG@.GearDefs.R_UT) return null;       // fix round (ut02 review): rerollWhy(id, d) decides (another Untiered item?)''')
rep(r'''# gear:fn:describe / rollsLine / rarity / level / identified / sig for a bag (the AH and other mods read bags through them)''', r'''M(gunid, r"""
public static Object[] utReroll(@BD@ b, String cur, String[] lean, java.util.UUID by) {
  String id = @PKG@.GearUt.rerollItem(cur, lo(b), hi(b), lean);
  if (id == null) return null;
  int L = @PKG@.GearUt.rerollLevel(id, lo(b), hi(b));
  int ty = @PKG@.GearPool.typeOfId(id);
  if (L < 0 || ty < 0) return null;
  @BD@ nd = @PKG@.GearRoll.newDoc(id, @PKG@.GearDefs.R_UT, true, "box", L);
  nd.put("idAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  if (by != null) nd.put("idBy", new org.bson.BsonString(by.toString()));
  nd.put("box", boxSub(ty, at(b), rar(b), lo(b), hi(b), rerolls(b) + 1));
  @IS@ ns = @PKG@.GearData.put(new @IS@(id, 1), nd, by);
  return new Object[] { id, Integer.valueOf(L), nd, ns };
}""")
M(gunid, r"""
public static Object[] reroll(@BD@ gearDoc, java.util.UUID by, String cur, String[] lean) {
  @BD@ b = boxOf(gearDoc);
  if (b == null) return null;
  if (rar(b) == @PKG@.GearDefs.R_UT) return utReroll(b, cur, lean, by);
  return pick(type(b), at(b), rar(b), lo(b), hi(b), rerolls(b) + 1, by);
}""")
M(gunid, r"""
public static String rerollWhy(String cur, @BD@ gearDoc) {
  String w = rerollWhy(gearDoc);
  if (w != null) return w;
  @BD@ b = boxOf(gearDoc);
  if (b != null && rar(b) == @PKG@.GearDefs.R_UT && @PKG@.GearUt.rerollCount(cur, lo(b), hi(b)) == 0)
    return "No other Untiered " + (@PKG@.GearData.slotOf(cur) == 2 ? "piece of this set" : "weapon") + " exists for " + rangeText(lo(b), hi(b)) + " yet - re-identifying could only give the same item back.";
  return null;
}""")
# gear:fn:describe / rollsLine / rarity / level / identified / sig for a bag (the AH and other mods read bags through them)''')
rep(r'''  String why = @PKG@.GearUnid.rerollWhy(d);
  if (why == null && it.getQuantity() != 1)''', r'''  String why = @PKG@.GearUnid.rerollWhy(it.getItemId(), d);          // fix round (ut02 review): + an Untiered item needs another to become
  if (why == null && it.getQuantity() != 1)''')
rep(r'''    got = @PKG@.GearUnid.reroll(d, u);''', r'''    got = @PKG@.GearUnid.reroll(d, u, id, @PKG@.GearLoot.lean(u));          // fix round (ut02 review): Untiered -> another Untiered item''')
rep(r'''  String why = @PKG@.GearUnid.rerollWhy(d);
  long cost = why == null''', r'''  String why = @PKG@.GearUnid.rerollWhy(id, d);          // fix round (ut02 review)
  long cost = why == null''')
rep(r'''  b.set("#SkyyGPurse.Text", "Becomes another " + @PKG@.GearView.slotWord(id).toLowerCase() + " (same rarity, new level + modifiers); reforges are lost.");''',
    r'''  b.set("#SkyyGPurse.Text", r == @PKG@.GearDefs.R_UT ? (@PKG@.GearData.slotOf(id) == 2 ? "Becomes another piece of the same Untiered set" : "Becomes another Untiered weapon") + " (new level, fixed lines); reforges are lost."
    : "Becomes another " + @PKG@.GearView.slotWord(id).toLowerCase() + " (same rarity, new level + modifiers); reforges are lost.");''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
