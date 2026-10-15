"""Derive SkyyGear/build_skyygear_0.3.6.py from the LIVE 0.3.5 (build_skyygear_0.3.5.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_5_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_6_patch.py      then      python SkyyGear/build_skyygear_0.3.6.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.6.py

0.3.6 (2026-10-14) = GATHERING ARMOR FOR FORAGING / FARMING / FISHING + POLE PERKS + REBIRTH DAMAGE / DEFENCE + GEAR SOUNDS. Skyy's words
(2026-10-14 ~18:30, picking items of the main session's list: "8. Gathering leftovers: ... Foraging, Farming and Fishing armor (only Mining
armor exists); perks for the fishing pole", "7. Rebirth wrap-up: mods start using the tree's stat nodes", "6. Sound pass ... gear"):
  "do 1. 3. 6. 7. 8. and 9. ill start testing soon. hold off on the others till after testing."
  gear.md 2026-10-12 popup "Yes, like the tools (Recommended)": Mining / Foraging / Farming / Fishing armor sets level with their skill (level =
  skill level, capped by tier), tier up on the Upgrade tab with Enchanted materials, keep rarity + rolls, reset to T1 on rebirth keeping rarity.
  gear.md 2026-10-08 GATHERING SETS "yes, gathering armor uses the set label, the full set gives a little bonus gathering fortune".
Built on the LIVE 0.3.5 (the pole, the Vault summon, Sigils, Mining armor and every older system are untouched apart from the hooks below).

1. GATHERING ARMOR (GearGArm; research/cloud/Gathering-Armor-Stats.md 1-3 + research/Gathering-Shards-Spec.md 5.5 / 6.1 + the SkyyFishing
   spec section 9 for the angler numbers). 68 new items, all green SET pieces (no modifiers, like the Mining pieces;
   QUESTION: Gathering-Shards-Spec question 8 defaults to 3 rolled lines from a gathering pool - kept fixed like Mining until Skyy says):
     FORAGING  Armor_Foraging_F<1-5>_<Head|Chest|Hands|Legs> = the bark sets Grove / Autumn / Savanna / Northern / Wastes Bark in the key
               tree's look (Oak, Maple, Gumboab, Redwood, Sallow) - the APPROVED models + icons of art/gathering-armor (our own art, shipped
               as is). The 21 other tree looks wait for the look swap (Wardrobe / Alteration) - question.
     FARMING   Armor_Farming_P<1-7>_<piece> = Wheat / Carrot / Cauliflower / Pumpkin / Chilli / Cotton / Onion Harvest. The crop models are
               not made yet (ART-RESUME #14 "Next"): PLACEHOLDER look = the vanilla Cotton armor model BY PATH + a crop-coloured copy of its
               texture / icon generated at build time (nothing vanilla committed) - a one-line art swap when Quirk's models land.
     FISHING   Armor_Fishing_A<1-5>_<piece> = Copper / Iron / Thorium / Cobalt / Adamantite Angler. No art yet: PLACEHOLDER = the vanilla
               Medium Leather model by path + a metal-coloured texture / icon generated at build time.
   LEVEL = your Foraging / Farming / Fishing level kept inside the tier band (garmor.bands, T1 1-18 ... T7 40-49 = the Mining armor bands);
   the existing 0.3.4 level sync (GearArmLv) rewrites "[Lv N]"; below the band = inactive (no lines, no set count). TIER UP on the Anvil
   (rows garmor.ladders.foraging / farming / fishing, joined to the Anvil ladders): Enchanted key log (Maple, Gumboab, Redwood, Sallow), key
   crop (Carrot, Cauliflower, Pumpkin, Tomato, Cotton, Potato) or ingot (Iron .. Adamantite) of the NEW tier, Head 1 / Chest 2 / Legs 2 /
   Hands 1 for the first two steps and 1 each after (the Mining ladder's rule); needs the skill level the new tier starts at; keeps the
   Set rarity, the set field moves. THE FIRST SET (T1) is CRAFTED at the vanilla Armor Bench (KnowledgeRequired false): Grove Bark from Oak
   logs + Tree Sap + Plant Fiber, Wheat Harvest from Wheat + Plant Fiber, Copper Angler from Copper bars + light leather + fibre (vanilla
   inputs only: a recipe never names another mod's item - the collection unlock is a later SkyyCollections round, question).
   LINES (per piece = the set total x Head 25 / Chest 35 / Legs 25 / Hands 15 %), they count WHILE WORN (spec question 7 default):
     Foraging Fortune 1 / 1.5 / 2.5 / 4 / 5.5 + Wisdom 0 / 0 / 0 / 2 / 4 %; Farming Fortune 1 .. 10 + Wisdom 0 .. 8 % (7 tiers); delivered
     as the skill:bonus source "garmor" (dd.foraging / xp.foraging / dd.farming / xp.farming - the shape SkyySkills sums), capped by the
     existing armor.fortune.cap / armor.wisdom.cap. FISHING: Fishing Speed 6 / 9 / 12 / 16 / 20, Treasure Chance 0.5 .. 2.5, Wisdom 0 / 0 /
     2 / 3 / 4 % - SkyyFishing 0.1.6 asks gear:fn:fishx at each cast (see 2).
   NOT IN 0.3.6 (Gathering-Armor-Stats.md 3 marks them "(later)"): the higher tiers' chopping / harvest speed, move speed, Tree Feller
   (needs SkyyTrees feller.armor), Sickle Range and Green Thumb - a later round. Farming T6 / T7 full sets clip at armor.fortune.cap (15).
   FULL SET (all 4 of one set id): + the set's bonus (Foraging / Farming Fortune 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10; Fishing double catch
   1 / 1.5 / 2.5 / 4 / 5.5 %). The Fishing full-set double catch is OUR placeholder: the SkyyFishing spec section 9 gives
   signatures instead (2 pc Patient Queue chime, 4 pc Steady Hands surge pull -15 %, 4 pc Lost and Found Great treasure x1.5) that need
   SkyyFishing hooks - QUESTION for Skyy, a later round. Tooltip "Set: Grove Bark (3/4)" + "Full set (all 4): +1 Foraging Fortune". Rows garmor.foraging / farming /
   fishing ("tiers | tiers | ..." lists), garmor.foragingOn / farmingOn / fishingOn, garmor.bands, garmor.gatherShare (Health / resistance
   50 % of the level curve - "low Defense").
   MARKET: crafted gathering sets may go on the AH like the Mining sets (GearUtFx.gathering knows the three new set families); never a
   mystery bag, never in the bag pool, never a native drop. REBIRTH (D9): a piece born before your latest rebirth goes back to T1 of its
   family (F1 / P1 / A1, same slot), rarity kept, set field moved - the 0.3.5 Mining reset (GearLife.rbArmor) now covers all four families.
2. POLE PERKS + THE TOOLS TAB ROW (spec 5.4 / 6.3): the pole gets the spec's three perks - Fortune (= double catch +1 % a level, 10 levels,
   1 point), Wisdom (+1 % Fishing XP, 5 levels, 2 points, Iron rod), Steady Line (the fish pulls 10 % slower a level, row
   lifelong.perkSteady, 3 levels, 2 points, Iron rod). Points = 1 per Fishing level (SkyySkills 0.4.38 publishes Fishing), like the other
   tools. The Tools tab of /smithing lists FIVE tools now (rows 106 px; the pole row says "tier up at the Fishing Bench"); /toolpoints with
   the pole in hand opens on it. The perks only show as buyable while SkyyFishing 0.1.6 reads them (bridge "fishing:perks"). gear:fn:fishx
   (Object[] { UUID, ItemStack rod } -> java.util.HashMap speed / treasure / double / wisdom / pull = the worn angler armor + your OWN
   lifelong pole's perks x the rebirth pole node). The pole's "[Lv N]" is drawn by SkyyFishing 0.1.6 from the document's lvl; SkyyGear
   asks fishing:fn:restamp right after it writes a new level on the pole.
3. REBIRTH DAMAGE / DEFENCE (research/cloud/Rebirth-Spec.md 3.1; SkyyRebirth 0.3 rebirth:fn:stat): a player's hit x (1 + (all + damage) %),
   damage a player takes x 100 / (100 + (all + defense)) - "all" = +3 % per rebirth (cap 30) + Void Ascendant, "damage" / "defense" = the
   Might / Guard nodes. NONE while rebirth:n:<uuid> is 0 or absent (or no SkyyRebirth). Read at most every 2 s per player (GearRbSt).
   Row rebirth.stats (on).
4. GEAR SOUNDS (research/Sound-Pass-Plan.md, round 1's pattern - SkyyQuests 0.3.1 QSnd): GSnd, 2D to that player only, category UI, vanilla
   sound events BY ID (nothing shipped), at most one of a kind per player per 0.5 s, never throws, a missing id = one WARN:
     identify        SFX_Chest_Wooden_Open_Player            an item identified (only when SkyyExploration's card page did NOT open - it has its own)
     identify rare   SFX_Chest_Legendary_FirstOpen_Player    the same for a Rare-or-better result
     reforge         SFX_Weapon_Bench_Craft                   a reforge of a weapon / tool
     reforge armor   SFX_Armour_Bench_Craft                   a reforge of armor
     sigil           SFX_Runebinders_Lattice_Unlock_Local     a Sigil raised an item's rarity
     tier up         SFX_Workbench_Upgrade_Complete_Default   an Anvil upgrade (tool / armor / Soul Cage tier up)
     summon          SFX_Portal_Neutral_Teleport_Local        /pickaxe & co. brought your lifelong tool (chest, Requip, Vault, exact copy)
   Server Setup -> Gear -> Sounds (new category): sounds.enabled + one id row each (empty = that sound off; check = the game's SoundEvent map).
   PER PLAYER: bridge key settings:sounds:<uuid> = Boolean FALSE mutes them for that player (absent / TRUE = play).
ROWS: garmor.foragingOn / farmingOn / fishingOn, garmor.bands, garmor.gatherShare, garmor.foraging / farming / fishing, garmor.ladders.foraging /
farming / fishing, lifelong.perkSteady, rebirth.stats, sounds.enabled + 7 sound id rows. Absent = the default; a fresh file gets a 0.3.6 block.
No one-time update, no saved-data rewrite. SAVED DATA: new documents of the 68 ids carry r "set" + set "<family>_<f|p|a><tier>"; the lifelong
registry may hold pole.up.fort / pole.up.wis / pole.up.steady.
ROLLBACK 0.3.6 -> 0.3.5 is NOT item-safe for the new armor: the 68 ids are unknown items in 0.3.5 (keep them in a chest - they come back with
0.3.6). Pole perk levels stay in the registry unused. Rebirth stats / sounds just stop.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.5.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.6.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.5"' in s and "GENERATED by tools/gear_0_3_5_patch.py" in s and "0.3.6" not in s[:400], "not the generated 0.3.5 script"
assert "GearGArm" not in s and "GSnd" not in s and "GearRbSt" not in s
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


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.5":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.5" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.5 - build script (javassist via jpype). GENERATED by tools/gear_0_3_5_patch.py from the LIVE 0.3.4 (itself GENERATED by
tools/gear_0_3_4_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.5.py -> SkyyGear/SkyyGear-0.3.5.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.5.py
''', '''"""SkyyGear 0.3.6 - build script (javassist via jpype). GENERATED by tools/gear_0_3_6_patch.py from the LIVE 0.3.5 (itself GENERATED by
tools/gear_0_3_5_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.6.py -> SkyyGear/SkyyGear-0.3.6.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.6.py

0.3.6 = GATHERING ARMOR (Foraging bark sets, Farming crop sets, Fishing angler sets) + POLE PERKS + REBIRTH DAMAGE / DEFENCE + GEAR SOUNDS
(notes: tools/gear_0_3_6_patch.py): 68 green Set pieces that level with Foraging / Farming / Fishing and tier up on the Anvil, their lines
while worn + full-set bonuses; the fishing pole's Fortune / Wisdom / Steady Line perks on a five-row Tools tab (gear:fn:fishx for SkyyFishing
0.1.6); rebirth:fn:stat damage / defence in the combat pipeline; identify / reforge / Sigil / tier-up / summon sounds (Server Setup -> Sounds).

--- 0.3.5 notes ---
''')
rep('VERSION = "0.3.5"\n', 'VERSION = "0.3.6"\n')

# ================================================================================================================ build-time data (items)
GA2 = r'''
# ================================================================= 0.3.6 GATHERING ARMOR: Foraging (bark), Farming (crop), Fishing (angler) - research/cloud/
# Gathering-Armor-Stats.md 1-3. 68 green Set pieces: tier T1..T5 / T7 / T5; the Foraging looks = the approved models of art/gathering-armor
# (our own art, shipped as is); Farming / Fishing = PLACEHOLDER looks: a vanilla armor model BY PATH + a recoloured copy of its texture and
# icon generated here (nothing vanilla committed; one-line swap GA2_ART when their models land)
GA2_FAMS = ["foraging", "farming", "fishing"]
GA2_SKILL = ["Foraging", "Farming", "Fishing"]
GA2_CODE = ["F", "P", "A"]
GA2_N = [5, 7, 5]
GA2_SLOTS = ["Head", "Chest", "Hands", "Legs"]                       # the engine's ArmorSlot order
GA2_SHARE = [0.25, 0.35, 0.15, 0.25]                                 # Head 25 / Chest 35 / Hands 15 / Legs 25 % of the set total
GA2_LOOK = [["Oak", "Maple", "Gumboab", "Redwood", "Sallow"],
            ["Wheat", "Carrot", "Cauliflower", "Pumpkin", "Chilli", "Cotton", "Onion"],
            ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite"]]
GA2_FTIER = ["F1_Grove", "F2_Autumn", "F3_Savanna", "F4_Northern", "F5_Wastes"]
GA2_SNAME = [["Grove Bark", "Autumn Bark", "Savanna Bark", "Northern Bark", "Wastes Bark"],
             ["Wheat Harvest", "Carrot Harvest", "Cauliflower Harvest", "Pumpkin Harvest", "Chilli Harvest", "Cotton Harvest", "Onion Harvest"],
             ["Copper Angler", "Iron Angler", "Thorium Angler", "Cobalt Angler", "Adamantite Angler"]]
GA2_ROWMETAL = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]     # the row of each tier (Health / durability source)
GA2_SRC = ["Iron", "Cloth_Cotton", "Leather_Medium"]                # the vanilla look family (piece words; the model of the placeholders)
GA2_ART = ["art/gathering-armor", "placeholder", "placeholder"]
GA2_RAMP = {"Wheat": ("#7a5a18", "#d4ae48", "#f4e3a0"), "Carrot": ("#7a3010", "#e07020", "#ffc078"),
            "Cauliflower": ("#4f5a3a", "#cfcdb4", "#f6f4e6"), "Pumpkin": ("#6e3206", "#e0802a", "#ffd28c"),
            "Chilli": ("#5e0e0e", "#c42a1c", "#ff8c70"), "Cotton": ("#6c6c78", "#d8d8e2", "#f4f4fa"), "Onion": ("#4e2442", "#a4608a", "#eec6dc"),
            "Copper": ("#4e2e14", "#b46e36", "#eeb07a"), "Iron": ("#353b42", "#8a939e", "#d4dbe2"), "Thorium": ("#28452f", "#5a9064", "#b0d8b4"),
            "Cobalt": ("#1a285e", "#3d60c0", "#a6beff"), "Adamantite": ("#521212", "#ac3830", "#ff9888")}
GA2_IDS, GA2_IFAM, GA2_ITIER, GA2_ISLOT = [], [], [], []
GA2_SETS, GA2_SFAM, GA2_STIER, GA2_SNAMES = [], [], [], []
GA2_FOFF = []
for _f in range(3):
    GA2_FOFF.append(len(GA2_SETS))
    for _t in range(GA2_N[_f]):
        GA2_SETS.append("%s_%s%d" % (GA2_FAMS[_f], GA2_CODE[_f].lower(), _t + 1))
        GA2_SFAM.append(_f)
        GA2_STIER.append(_t)
        GA2_SNAMES.append(GA2_SNAME[_f][_t])
        for _s, _sl in enumerate(GA2_SLOTS):
            GA2_IDS.append("Armor_%s_%s%d_%s" % (GA2_SKILL[_f], GA2_CODE[_f], _t + 1, _sl))
            GA2_IFAM.append(_f)
            GA2_ITIER.append(_t)
            GA2_ISLOT.append(_s)
assert len(GA2_IDS) == 68 and len(GA2_SETS) == 17 and GA2_FOFF == [0, 5, 12] and len(set(GA2_IDS)) == 68
assert not set(GA2_IDS) & AZ_ITEMS, "a gathering armor id is a vanilla item"
assert all(_s.startswith(("foraging_", "farming_", "fishing_")) for _s in GA2_SETS)
# the bands of tiers 1-7 (the Mining armor bands: Copper 1-18 ... Onyxium 40-49)
GA2_BANDS_DEF = "1-18,15-23,20-28,25-38,35-43,40-49,40-49"
# per family, set totals per tier: Foraging / Farming = Fortune | Wisdom % | full-set Fortune; Fishing = Speed | Treasure | Wisdom % | full-set double catch %
GA2_STAT_DEF = ["1,1.5,2.5,4,5.5|0,0,0,2,4|1,1.5,2.5,4,5.5",
                "1,1.5,2.5,4,5.5,7.5,10|0,0,0,2,4,6,8|1,1.5,2.5,4,5.5,7.5,10",
                "6,9,12,16,20|0.5,1,1.5,2,2.5|0,0,2,3,4|1,1.5,2.5,4,5.5"]
for _f in range(3):
    _cols = GA2_STAT_DEF[_f].split("|")
    assert len(_cols) == (4 if _f == 2 else 3) and all(len(_c.split(",")) == GA2_N[_f] for _c in _cols)
# tier-up costs: the Enchanted item of the NEW tier (gathering-shards spec 6.1: Head 1 / Chest 2 / Legs 2 / Hands 1 for the first two steps,
# 1 each after - the Mining ladder's rule, no free step)
GA2_STEPS = [["Maple", "Gumboab", "Redwood", "Sallow"], ["Carrot", "Cauliflower", "Pumpkin", "Tomato", "Cotton", "Potato"],
             ["Iron", "Thorium", "Cobalt", "Adamantite"]]
GA2_CN = {"Head": (1, 1), "Chest": (2, 1), "Hands": (1, 1), "Legs": (2, 1)}
GA2_LAD_DEF = []
for _f in range(3):
    assert len(GA2_STEPS[_f]) == GA2_N[_f] - 1
    _rows = []
    for _sl in GA2_SLOTS:
        _row = "Armor_%s_%s1_%s" % (GA2_SKILL[_f], GA2_CODE[_f], _sl)
        for _j, _k in enumerate(GA2_STEPS[_f]):
            _row += ">Armor_%s_%s%d_%s(%s)" % (GA2_SKILL[_f], GA2_CODE[_f], _j + 2, _sl, _lle(_k, GA2_CN[_sl][0 if _j < 2 else 1]))
        _rows.append(_row)
    GA2_LAD_DEF.append(",".join(_rows))
    assert len(GA2_LAD_DEF[-1]) < 2000 and all(32 <= ord(_c) < 127 for _c in GA2_LAD_DEF[-1])
# the vanilla item JSONs (read only; nothing copied into the repo)
_GA2_P = dict((os.path.basename(_n)[:-5], _n) for _n in AZ_NAMES if _n.startswith("Server/Item/Items/") and _n.endswith(".json"))


def _ga2j(i):
    assert i in _GA2_P, "no vanilla item " + i
    return json.loads(AZ.read(_GA2_P[i]).decode("utf-8-sig"))


_ga2lang = AZ.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")


def _ga2word(i):
    for _l in _ga2lang.splitlines():
        if _l.startswith("items.%s.name = " % i):
            return _l.split(" = ", 1)[1].strip().split(" ")[-1]
    raise AssertionError("no vanilla name for " + i)


def _ga2half(a):
    a = json.loads(json.dumps(a))
    for _h in a.get("StatModifiers", {}).get("Health", []):
        _h["Amount"] = round(float(_h["Amount"]) * 0.5, 2)
    for _k in ("Physical", "Projectile"):
        for _r in a.get("DamageResistance", {}).get(_k, []):
            _r["Amount"] = round(float(_r["Amount"]) * 0.5, 4)
    return a


GA2_INPUTS = [[("Wood_Oak_Trunk", (20, 30, 10, 20)), ("Ingredient_Tree_Sap", (2, 3, 1, 2)), ("Ingredient_Fibre", (3, 5, 2, 3))],
              [("Plant_Crop_Wheat_Item", (20, 30, 10, 20)), ("Ingredient_Fibre", (3, 5, 2, 3))],
              [("Ingredient_Bar_Copper", (3, 5, 2, 4)), ("Ingredient_Leather_Light", (2, 3, 1, 2)), ("Ingredient_Fibre", (2, 3, 1, 2))]]
for _f in range(3):
    for _i, _q in GA2_INPUTS[_f]:
        assert _i in AZ_ITEMS and len(_q) == 4 and all(1 <= _x <= 100 for _x in _q), _i
GA2_ITEMS = {}
GA2_FILES = {}
GA2_LANG = []
GA2_QUAL = QUAL_IDS[R_IDS.index("set")]
GA2_BAND_LO = [int(_b.split("-")[0]) for _b in GA2_BANDS_DEF.split(",")]
_ga2root = os.path.dirname(HERE)
for _k, _id in enumerate(GA2_IDS):
    _f, _t, _s = GA2_IFAM[_k], GA2_ITIER[_k], GA2_ISLOT[_k]
    _sl = GA2_SLOTS[_s]
    _look = GA2_LOOK[_f][_t]
    _bj = _ga2j("Armor_Iron_%s" % _sl)                     # the parent of every vanilla armor piece (no Parent of its own)
    assert "Parent" not in _bj
    _src = _ga2j("Armor_%s_%s" % (GA2_SRC[_f], _sl))
    _row = _ga2j("Armor_%s_%s" % (GA2_ROWMETAL[_t], _sl))
    for _x in ("Recipe", "$Comment", "Tags", "ItemLevel", "Parent"):
        _bj.pop(_x, None)
    _bj["TranslationProperties"] = {"Name": "server.items.%s.name" % _id, "Description": "server.items.%s.description" % _id}
    _bj["Quality"] = GA2_QUAL
    _bj["ItemLevel"] = GA2_BAND_LO[_t]
    _arm = _ga2half(_row["Armor"])
    _arm["CosmeticsToHide"] = list(_src.get("Armor", {}).get("CosmeticsToHide", _bj["Armor"].get("CosmeticsToHide", [])))
    _arm["ArmorSlot"] = _sl
    _bj["Armor"] = _arm
    _bj["MaxDurability"] = _row.get("MaxDurability", _bj.get("MaxDurability"))
    _bj["Tags"] = {"Type": ["Armor"]}
    _bj["ItemSoundSetId"] = _src.get("ItemSoundSetId") or "ISS_Armor_Leather"
    if "IconProperties" in _src:
        _bj["IconProperties"] = _src["IconProperties"]
    if _f == 0:
        _bj["ItemSoundSetId"] = "ISS_Armor_Leather"
        _rel = "Items/Armors/SkyyForaging/%s/%s/%s" % (GA2_FTIER[_t], _look, _sl)
        _adir = os.path.join(_ga2root, *GA2_ART[0].split("/"))
        _bj["Model"] = _rel + ".blockymodel"
        _bj["Texture"] = _rel + "_Texture.png"
        _bj["Icon"] = "Icons/ItemsGenerated/Armor_Foraging_%s_%s.png" % (_look, _sl)
        for _p in (_bj["Model"], _bj["Texture"], _bj["Icon"]):
            GA2_FILES["Common/" + _p] = open(os.path.join(_adir, "Common", *_p.split("/")), "rb").read()
    else:
        _bj["Model"] = _src["Model"]                       # the vanilla model BY PATH (never copied)
        assert ("Common/" + _src["Model"]) in AZ_NAMES and ("Common/" + _src["Texture"]) in AZ_NAMES and ("Common/" + _src["Icon"]) in AZ_NAMES
        _bj["Texture"] = "Items/SkyyGear/GArmor/%s_%s.png" % (_look if _f == 1 else _look + "_Angler", _sl)
        _bj["Icon"] = "Icons/ItemsGenerated/%s.png" % _id
        _rp = _ramp(GA2_RAMP[_look])
        GA2_FILES["Common/" + _bj["Texture"]] = SA.recolor(AZ.read("Common/" + _src["Texture"]), _rp, rank=0.35)
        GA2_FILES["Common/" + _bj["Icon"]] = SA.recolor_icon(AZ.read("Common/" + _src["Icon"]), _rp, rank=0.35)
    if _t == 0:                                            # the first set is crafted (vanilla inputs, the Armor Bench of the piece)
        _cr = _ga2j("Armor_Copper_%s" % _sl)["Recipe"]
        _bj["Recipe"] = {"Input": [{"ItemId": _i, "Quantity": _q[_s]} for _i, _q in GA2_INPUTS[_f]],
                         "BenchRequirement": _cr["BenchRequirement"], "KnowledgeRequired": False, "TimeSeconds": _cr.get("TimeSeconds", 3)}
    GA2_ITEMS["Server/Item/Items/SkyyGear/GArmor/%s.json" % _id] = json.dumps(_bj, indent=2)
    _word = _ga2word("Armor_%s_%s" % (GA2_SRC[_f], _sl))
    _nm = ("%s Bark %s" % (_look, _word)) if _f == 0 else (("%s %s" % (_look, _word)) if _f == 1 else ("%s Angler %s" % (_look, _word)))
    GA2_LANG.append("items.%s.name = %s" % (_id, _nm))
    GA2_LANG.append("items.%s.description = %s set - %s armor. It levels with your %s and tiers up on the Anvil." % (_id, GA2_SNAME[_f][_t], GA2_SKILL[_f], GA2_SKILL[_f]))
for _k in list(GA2_FILES) + list(GA2_ITEMS):
    assert _k not in AZ_NAMES, "a gathering armor file would shadow a vanilla file: " + _k
for _k, _v in GA2_FILES.items():
    if _k.endswith(".png"):
        assert SA.png_size(_v)[0] > 0, _k
EXTRA.update(GA2_FILES)
EXTRA.update(GA2_ITEMS)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\n".join(GA2_LANG) + "\n"
print("0.3.6 gathering armor: %d items (%d sets), %d files (Foraging = the approved art, Farming / Fishing = placeholder recolours)"
      % (len(GA2_ITEMS), len(GA2_SETS), len(GA2_FILES)))
# 0.3.6 GEAR SOUNDS (research/Sound-Pass-Plan.md): the default vanilla sound event ids must be in Assets.zip (played BY ID, nothing shipped)
GSND = [("identify", "Identify", "SND_IDENT", "SFX_Chest_Wooden_Open_Player", "An item identified (no card page)."),
        ("identifyRare", "Identify (Rare or better)", "SND_IDENTR", "SFX_Chest_Legendary_FirstOpen_Player", "The same for a Rare or better result."),
        ("reforge", "Reforge", "SND_REFORGE", "SFX_Weapon_Bench_Craft", "A weapon or tool reforged."),
        ("reforgeArmor", "Reforge (armor)", "SND_REFORGEA", "SFX_Armour_Bench_Craft", "An armor piece reforged."),
        ("sigil", "Sigil", "SND_SIGIL", "SFX_Runebinders_Lattice_Unlock_Local", "A Sigil raised an item's rarity."),
        ("upgrade", "Tier up", "SND_UP", "SFX_Workbench_Upgrade_Complete_Default", "An item tiered up on the Anvil."),
        ("summon", "Lifelong tool summoned", "SND_SUMMON", "SFX_Portal_Neutral_Teleport_Local", "/pickaxe and co. brought a tool back.")]
_GSND_IDS = set(os.path.basename(_n)[:-5] for _n in AZ_NAMES if _n.startswith("Server/Audio/SoundEvents/") and _n.endswith(".json"))
for _g in GSND:
    assert _g[3] in _GSND_IDS and all(_c.isalnum() or _c == "_" for _c in _g[3]), "0.3.6: sound event %s is not in Assets.zip" % _g[3]
'''
before('''# 0.3.4 THE HOE TILL AREA (spec 4.3 + G5 "Yes, as proposed"): the side of the tilled square per hoe tier Crude .. Onyxium
HOE_AREA_DEF = "1,3,3,5,5,7,7,9"''', GA2.lstrip("\n") + "\n")

# ================================================================================================================ rows
CATS_OLD = '''            ("lifelong", "Lifelong tools")]      # 0.3.0'''
rep(CATS_OLD, '''            ("lifelong", "Lifelong tools"),      # 0.3.0
            ("sounds", "Sounds")]                # 0.3.6''')
_srows = ['''    ("sounds.enabled", "Sounds", "sounds", "bool", "true", "", "", "", "", "live",
     "Off = SkyyGear plays no sound. Try any sound id in game with /soundtest.", "field:GearCfg.SND_ON"),''']
_GSND_PY = [("identify", "Identify", "SND_IDENT", "SFX_Chest_Wooden_Open_Player", "An item identified (no card page)."),
            ("identifyRare", "Identify (Rare or better)", "SND_IDENTR", "SFX_Chest_Legendary_FirstOpen_Player", "The same for a Rare or better result."),
            ("reforge", "Reforge", "SND_REFORGE", "SFX_Weapon_Bench_Craft", "A weapon or tool reforged."),
            ("reforgeArmor", "Reforge (armor)", "SND_REFORGEA", "SFX_Armour_Bench_Craft", "An armor piece reforged."),
            ("sigil", "Sigil", "SND_SIGIL", "SFX_Runebinders_Lattice_Unlock_Local", "A Sigil raised an item's rarity."),
            ("upgrade", "Tier up", "SND_UP", "SFX_Workbench_Upgrade_Complete_Default", "An item tiered up on the Anvil."),
            ("summon", "Lifelong tool summoned", "SND_SUMMON", "SFX_Portal_Neutral_Teleport_Local", "/pickaxe and co. brought a tool back.")]
for _g in _GSND_PY:
    _srows.append('''    ("sound.%s.id", "%s sound", "sounds", "text", "%s", "0", "120", "", "", "live",
     "%s Empty = silent (try ids with /soundtest).", "field:GearCfg.%s;check=GSnd.check"),''' % (_g[0], _g[1], _g[3], _g[4], _g[2]))
after('''    ("multi.rebirthGate", "Multitools after rebirth 1", "tools", "bool", "false", "", "", "", "", "live,danger",
     "On = multitools open after your first rebirth. Switch on with rebirth.on. Off = always.", "field:GearCfg.MULTI_RBGATE"),
''', '''    # 0.3.6 GATHERING ARMOR for Foraging / Farming / Fishing (research/cloud/Gathering-Armor-Stats.md; Skyy 2026-10-12 "Yes, like the tools")
    ("garmor.foragingOn", "Foraging armor (bark sets)", "garmor", "bool", "true", "", "", "", "", "live,part,danger",
     "The bark sets: Foraging gate, Foraging lines while worn, tier up on the Anvil.", "field:GearCfg.GA_FOR_ON"),
    ("garmor.farmingOn", "Farming armor (crop sets)", "garmor", "bool", "true", "", "", "", "", "live,part,danger",
     "The crop sets: Farming gate, Farming lines while worn, tier up on the Anvil.", "field:GearCfg.GA_FAR_ON"),
    ("garmor.fishingOn", "Fishing armor (angler sets)", "garmor", "bool", "true", "", "", "", "", "live,part,danger",
     "The angler sets: Fishing gate, Speed / Treasure / Wisdom while you fish, tier up on the Anvil.", "field:GearCfg.GA_FIS_ON"),
    ("garmor.bands", "Gathering armor levels per tier", "garmor", "text", GA2_BANDS_DEF, "0", "200", "", "", "live,danger",
     "Level band of tiers 1-7 of the Foraging, Farming and Fishing sets: 7 min-max pairs.", "field:GearCfg.GA_BANDS;check=GearGArm.checkBands"),
    ("garmor.gatherShare", "Gathering armor Health / resistance", "garmor", "int", "50", "0", "100", "", "%", "live,danger",
     "Share of the normal armor Health and resistance the Foraging, Farming and Fishing sets give.", "field:GearCfg.GA_SHARE"),
    ("garmor.foraging", "Foraging armor numbers", "garmor", "text", GA2_STAT_DEF[0], "0", "300", "", "", "live,danger",
     "Full set per tier 1-5: Fortune | Wisdom % | full-set bonus Fortune.", "field:GearCfg.GA_STAT0;check=GearGArm.checkStats"),
    ("garmor.farming", "Farming armor numbers", "garmor", "text", GA2_STAT_DEF[1], "0", "300", "", "", "live,danger",
     "Full set per tier 1-7: Fortune | Wisdom % | full-set bonus Fortune.", "field:GearCfg.GA_STAT1;check=GearGArm.checkStats"),
    ("garmor.fishing", "Fishing armor numbers", "garmor", "text", GA2_STAT_DEF[2], "0", "300", "", "", "live,danger",
     "Full set per tier 1-5: Fishing Speed | Treasure | Wisdom % | full-set double catch %.", "field:GearCfg.GA_STAT2;check=GearGArm.checkStats"),
    ("garmor.ladders.foraging", "Foraging armor tier-up costs", "garmor", "text", GA2_LAD_DEF[0], "0", "2000", "", "", "live,danger",
     "Bark set tiers on the Anvil, like garmor.ladders: A>B(Id*2), ladders joined by commas.", "field:GearCfg.GA_LAD0;check=GearUp.checkLadders"),
    ("garmor.ladders.farming", "Farming armor tier-up costs", "garmor", "text", GA2_LAD_DEF[1], "0", "2000", "", "", "live,danger",
     "Crop set tiers on the Anvil, like garmor.ladders: A>B(Id*2), ladders joined by commas.", "field:GearCfg.GA_LAD1;check=GearUp.checkLadders"),
    ("garmor.ladders.fishing", "Fishing armor tier-up costs", "garmor", "text", GA2_LAD_DEF[2], "0", "2000", "", "", "live,danger",
     "Angler set tiers on the Anvil, like garmor.ladders: A>B(Id*2), ladders joined by commas.", "field:GearCfg.GA_LAD2;check=GearUp.checkLadders"),
    # 0.3.6 POLE PERKS (spec 6.3): Steady Line = the fish pulls this % slower per level
    ("lifelong.perkSteady", "Steady Line per perk level", "lifelong", "dec", "10", "0", "30", "", "%", "live,danger",
     "Each Steady Line level on your fishing pole: the fish pulls the bar down this % slower.", "field:GearCfg.LL_PSTEADY"),
    # 0.3.6 REBIRTH DAMAGE / DEFENCE (SkyyRebirth rebirth:fn:stat: +3 % per rebirth, the Might / Guard nodes)
    ("rebirth.stats", "Rebirth damage and defence", "combat", "bool", "true", "", "", "", "", "live,danger",
     "Your rebirths' damage and defence % (per rebirth + Might / Guard). Off = none.", "field:GearCfg.RB_STATS"),
    # 0.3.6 GEAR SOUNDS (research/Sound-Pass-Plan.md)
''' + "\n".join(_srows) + "\n")
rep('''           # 0.3.5: the rebirth tool modifier (gathering power = economy) + the multitool gate (Skyy's rebirth lock)
           "lifelong.rebirthPct", "multi.rebirthGate"}''',
    '''           # 0.3.5: the rebirth tool modifier (gathering power = economy) + the multitool gate (Skyy's rebirth lock)
           "lifelong.rebirthPct", "multi.rebirthGate",
           # 0.3.6: the gathering armor sets (item supply, Fortune, Wisdom, tier-up costs = economy), the pole perk, rebirth combat stats
           "garmor.foragingOn", "garmor.farmingOn", "garmor.fishingOn", "garmor.bands", "garmor.gatherShare", "garmor.foraging",
           "garmor.farming", "garmor.fishing", "garmor.ladders.foraging", "garmor.ladders.farming", "garmor.ladders.fishing",
           "lifelong.perkSteady", "rebirth.stats"}''')
after('''G35_HEAD = "# ---- the fishing pole, rebirth (SkyyGear 0.3.5) ----"
G35_ROWK = ["lifelong.rebirthPct", "multi.rebirthGate"]
assert all(32 <= ord(_c) < 127 for _c in G35_HEAD) and "=" not in G35_HEAD
''', '''G36_HEAD = "# ---- gathering armor (Foraging / Farming / Fishing), pole perks, rebirth stats, sounds (SkyyGear 0.3.6) ----"
G36_ROWK = ["garmor.foragingOn", "garmor.farmingOn", "garmor.fishingOn", "garmor.bands", "garmor.gatherShare", "garmor.foraging", "garmor.farming",
            "garmor.fishing", "garmor.ladders.foraging", "garmor.ladders.farming", "garmor.ladders.fishing", "lifelong.perkSteady", "rebirth.stats",
            "sounds.enabled"] + ["sound.%s.id" % _g[0] for _g in GSND]
assert all(32 <= ord(_c) < 127 for _c in G36_HEAD) and "=" not in G36_HEAD
''')
rep('''    L += ["", G35_HEAD]         # 0.3.5: the new rows (no one-time update adds them; absent = the default)
    for k in G35_ROWK:
        scal(k)
''', '''    L += ["", G35_HEAD]         # 0.3.5: the new rows (no one-time update adds them; absent = the default)
    for k in G35_ROWK:
        scal(k)
    L += ["", G36_HEAD]         # 0.3.6: the new rows (no one-time update adds them; absent = the default)
    for k in G36_ROWK:
        scal(k)
''')
rep('''              # 0.3.5 the rebirth tool modifier + the multitool gate
              ("LL_RBPCT", "int", "5"), ("MULTI_RBGATE", "boolean", "false")]''',
    '''              # 0.3.5 the rebirth tool modifier + the multitool gate
              ("LL_RBPCT", "int", "5"), ("MULTI_RBGATE", "boolean", "false"),
              # 0.3.6 gathering armor, the pole's Steady Line, rebirth combat stats, sounds
              ("GA_FOR_ON", "boolean", "true"), ("GA_FAR_ON", "boolean", "true"), ("GA_FIS_ON", "boolean", "true"),
              ("GA_BANDS", "String", jstr(GA2_BANDS_DEF)), ("GA_SHARE", "int", "50"),
              ("GA_STAT0", "String", jstr(GA2_STAT_DEF[0])), ("GA_STAT1", "String", jstr(GA2_STAT_DEF[1])), ("GA_STAT2", "String", jstr(GA2_STAT_DEF[2])),
              ("GA_LAD0", "String", jstr(GA2_LAD_DEF[0])), ("GA_LAD1", "String", jstr(GA2_LAD_DEF[1])), ("GA_LAD2", "String", jstr(GA2_LAD_DEF[2])),
              ("LL_PSTEADY", "double", "10.0"), ("RB_STATS", "boolean", "true"), ("SND_ON", "boolean", "true")]
CFG_FIELDS += [(_g[2], "String", jstr(_g[3])) for _g in GSND]          # 0.3.6 the sound ids''')
_loads = ['''  // 0.3.6 gathering armor (lists checked where they are used - a bad list = one WARN + the default), the Steady Line, rebirth stats, sounds''',
          '''  GA_FOR_ON = pbool(p, "garmor.foragingOn", true);''',
          '''  GA_FAR_ON = pbool(p, "garmor.farmingOn", true);''',
          '''  GA_FIS_ON = pbool(p, "garmor.fishingOn", true);''',
          '''  GA_BANDS = ptext(p, "garmor.bands", "@GA2BANDS@").trim();''',
          '''  GA_SHARE = (int) plong(p, "garmor.gatherShare", 50L, 0L, 100L);''',
          '''  GA_STAT0 = ptext(p, "garmor.foraging", "@GA2STAT0@").trim();''',
          '''  GA_STAT1 = ptext(p, "garmor.farming", "@GA2STAT1@").trim();''',
          '''  GA_STAT2 = ptext(p, "garmor.fishing", "@GA2STAT2@").trim();''',
          '''  GA_LAD0 = ptext(p, "garmor.ladders.foraging", "@GA2LAD0@").trim();''',
          '''  GA_LAD1 = ptext(p, "garmor.ladders.farming", "@GA2LAD1@").trim();''',
          '''  GA_LAD2 = ptext(p, "garmor.ladders.fishing", "@GA2LAD2@").trim();''',
          '''  LL_PSTEADY = pdec(p, "lifelong.perkSteady", 10.0, 0.0, 30.0);''',
          '''  RB_STATS = pbool(p, "rebirth.stats", true);''',
          '''  SND_ON = pbool(p, "sounds.enabled", true);'''] + \
         ['''  %s = ptext(p, "sound.%s.id", "%s").trim();''' % (_g[2], _g[0], _g[3]) for _g in _GSND_PY]
after('''  MULTI_RBGATE = pbool(p, "multi.rebirthGate", false);          // fix round 2 (critic B1): OFF until rebirth is switched on
''', "\n".join(_loads) + "\n")
rep('''   .replace("@GALADDEF@", GA_LADDER_DEF).replace("@HOEAREADEF@", HOE_AREA_DEF))''',
    '''   .replace("@GALADDEF@", GA_LADDER_DEF).replace("@HOEAREADEF@", HOE_AREA_DEF)
   .replace("@GA2BANDS@", GA2_BANDS_DEF).replace("@GA2STAT0@", GA2_STAT_DEF[0]).replace("@GA2STAT1@", GA2_STAT_DEF[1]).replace("@GA2STAT2@", GA2_STAT_DEF[2])
   .replace("@GA2LAD0@", GA2_LAD_DEF[0]).replace("@GA2LAD1@", GA2_LAD_DEF[1]).replace("@GA2LAD2@", GA2_LAD_DEF[2]))          # 0.3.6''')

# ================================================================================================================ GearGArm (1/5) + GSnd
P0 = r'''# ================================================================= 0.3.6 GearGArm (1/5): the Foraging / Farming / Fishing gathering armor - ids, sets, bands and the
# per-tier number lists (GearCfg.GA_STAT0-2 / GA_BANDS, parsed lazily, re-parsed when the text changes; a bad text = one WARN + the default)
gga = mk("GearGArm")
gsnd = mk("GSnd")
G36_CLASSES = [gga, gsnd]
F(gga, "public static final String[] FAM = %s;" % jarr(GA2_FAMS))
F(gga, "public static final String[] FSK = %s;" % jarr(GA2_SKILL))
F(gga, "public static final int[] FN = %s;" % jints(GA2_N))
F(gga, "public static final int[] FOFF = %s;" % jints(GA2_FOFF))
F(gga, "public static final String[] IDS = %s;" % jarr(GA2_IDS))
F(gga, "public static final int[] IFAM = %s;" % jints(GA2_IFAM))
F(gga, "public static final int[] ITIER = %s;" % jints(GA2_ITIER))
F(gga, "public static final int[] ISLOT = %s;" % jints(GA2_ISLOT))
F(gga, "public static final String[] SETS = %s;" % jarr(GA2_SETS))
F(gga, "public static final int[] SFAM = %s;" % jints(GA2_SFAM))
F(gga, "public static final int[] STIER = %s;" % jints(GA2_STIER))
F(gga, "public static final String[] SNAME = %s;" % jarr(GA2_SNAMES))
F(gga, "public static final double[] SHARE = new double[] { 0.25, 0.35, 0.15, 0.25 };")
F(gga, "public static final String[] DEF = %s;" % jarr(GA2_STAT_DEF))
F(gga, "public static final String BANDS_DEF = %s;" % jstr(GA2_BANDS_DEF))
F(gga, 'public static final String SRC = "garmor";')
F(gga, "public static final java.util.concurrent.ConcurrentHashMap ARM = new java.util.concurrent.ConcurrentHashMap();")    # UUID -> double[8]
F(gga, "public static final java.util.concurrent.ConcurrentHashMap WORN = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> HashMap set -> Integer
F(gga, "public static final Object[] PC = new Object[4];")          # per family / the bands: Object[] { source text, parsed }
F(gga, "public static final long[] N = new long[5];")              # 0 armor passes, 1 bridge posts, 2 bridge removes, 3 gear:fn:fishx, 4 bad lists
M(gga, r"""
public static int index(String id) {
  if (id == null || !id.startsWith("Armor_")) return -1;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return i;
  return -1;
}""")
M(gga, r"""
public static boolean famOn(int f) {
  if (f == 0) return @PKG@.GearCfg.GA_FOR_ON;
  if (f == 1) return @PKG@.GearCfg.GA_FAR_ON;
  if (f == 2) return @PKG@.GearCfg.GA_FIS_ON;
  return false;
}""")
M(gga, "public static boolean anyOn() { return @PKG@.GearCfg.GA_FOR_ON || @PKG@.GearCfg.GA_FAR_ON || @PKG@.GearCfg.GA_FIS_ON; }")
M(gga, r"""
public static boolean isPiece(String id) {
  int i = index(id);
  return i >= 0 && famOn(IFAM[i]);
}""")
# the gate skill of a piece (Foraging / Farming / Fishing; null = not one, or its family is off)
M(gga, r"""
public static String gateOf(String id) {
  int i = index(id);
  return i < 0 || !famOn(IFAM[i]) ? null : FSK[IFAM[i]];
}""")
M(gga, r"""
public static int setIdx(String sid) {
  if (sid == null) return -1;
  String s = sid.trim();
  for (int i = 0; i < SETS.length; i++) if (SETS[i].equalsIgnoreCase(s)) return i;
  return -1;
}""")
M(gga, r"""
public static int setFam(String sid) {
  int i = setIdx(sid);
  return i < 0 ? -1 : SFAM[i];
}""")
# the set a piece counts for BY ID (the ids are grouped four per set); null = not a piece / its family off
M(gga, r"""
public static String setFor(String id) {
  int i = index(id);
  return i < 0 || !famOn(IFAM[i]) ? null : SETS[i / 4];
}""")
# the tier-1 piece of the same family and slot (the rebirth reset); null = none / already tier 1
M(gga, r"""
public static String t1Of(String id) {
  int i = index(id);
  if (i < 0 || !famOn(IFAM[i]) || ITIER[i] == 0) return null;
  return IDS[FOFF[IFAM[i]] * 4 + ISLOT[i]];
}""")
M(gga, r"""
public static String num(double v) {
  double r = (double) Math.round(v * 100.0) / 100.0;
  long l = Math.round(r);
  if (Math.abs(r - (double) l) < 0.000001) return String.valueOf(l);
  return String.valueOf(r);
}""")
# "1,1.5,2.5" -> exactly n numbers 0-1000 (null = bad)
M(gga, r"""
public static double[] list(String s, int n) {
  if (s == null) return null;
  String[] ps = s.trim().split(",", -1);
  if (ps.length != n) return null;
  double[] o = new double[n];
  for (int i = 0; i < n; i++) {
    try { o[i] = Double.parseDouble(ps[i].trim()); } catch (Throwable t) { return null; }
    if (Double.isNaN(o[i]) || o[i] < 0.0 || o[i] > 1000.0) return null;
  }
  return o;
}""")
# a family's text "list | list | list" -> Object[] of double[] (3 columns, Fishing 4); null = bad
M(gga, r"""
public static Object[] parse(int f, String s) {
  if (s == null || f < 0 || f > 2) return null;
  String[] cs = s.trim().split("[|]", -1);
  int nc = f == 2 ? 4 : 3;
  if (cs.length != nc) return null;
  Object[] o = new Object[nc];
  for (int c = 0; c < nc; c++) {
    double[] l = list(cs[c], FN[f]);
    if (l == null) return null;
    o[c] = l;
  }
  return o;
}""")
M(gga, r"""
public static String src(int f) {
  if (f == 0) return @PKG@.GearCfg.GA_STAT0;
  if (f == 1) return @PKG@.GearCfg.GA_STAT1;
  return @PKG@.GearCfg.GA_STAT2;
}""")
M(gga, r"""
public static Object[] cols(int f) {
  String s = src(f);
  Object e = PC[f];
  if (e instanceof Object[] && s != null && s.equals(((Object[]) e)[0])) return (Object[]) ((Object[]) e)[1];
  Object[] o = parse(f, s);
  if (o == null) {
    N[4] = N[4] + 1L;
    @PKG@.Gear.warnOnce("garmor:" + f + ":" + s, "config.properties: garmor." + FAM[f] + "=" + s + " is not a valid list - the default " + DEF[f] + " is used");
    o = parse(f, DEF[f]);
  }
  PC[f] = new Object[] { s, o };
  return o;
}""")
M(gga, r"""
public static double col(int f, int c, int t) {
  if (f < 0 || f > 2) return 0.0;
  Object[] o = cols(f);
  if (o == null || c < 0 || c >= o.length) return 0.0;
  double[] l = (double[]) o[c];
  return t >= 0 && t < l.length ? l[t] : 0.0;
}""")
# "1-18,15-23,..." -> int[14] (min, max of tiers 1-7); null = bad
M(gga, r"""
public static int[] bandsOf(String s) {
  if (s == null) return null;
  String[] ps = s.trim().split(",", -1);
  if (ps.length != 7) return null;
  int[] o = new int[14];
  for (int i = 0; i < 7; i++) {
    String[] ab = ps[i].trim().split("-", -1);
    if (ab.length != 2) return null;
    try { o[i * 2] = Integer.parseInt(ab[0].trim()); o[i * 2 + 1] = Integer.parseInt(ab[1].trim()); } catch (Throwable t) { return null; }
    if (o[i * 2] < 1 || o[i * 2 + 1] < o[i * 2] || o[i * 2 + 1] > 200) return null;
  }
  return o;
}""")
M(gga, r"""
public static int[] bands() {
  String s = @PKG@.GearCfg.GA_BANDS;
  Object e = PC[3];
  if (e instanceof Object[] && s != null && s.equals(((Object[]) e)[0])) return (int[]) ((Object[]) e)[1];
  int[] b = bandsOf(s);
  if (b == null) {
    N[4] = N[4] + 1L;
    @PKG@.Gear.warnOnce("garmorb:" + s, "config.properties: garmor.bands=" + s + " is not 7 level ranges - the default " + BANDS_DEF + " is used");
    b = bandsOf(BANDS_DEF);
  }
  PC[3] = new Object[] { s, b };
  return b;
}""")
# the level band of a piece (its family on or off - an off family still reads sensible levels); null = not a piece
M(gga, r"""
public static int[] band(String id) {
  int i = index(id);
  if (i < 0) return null;
  int[] b = bands();
  int t = ITIER[i];
  return new int[] { b[t * 2], b[t * 2 + 1] };
}""")
M(gga, r"""
public static String checkBands(String key, String value) {
  if (bandsOf(value) == null) return "Write 7 level ranges min-max for tiers 1-7, e.g. " + BANDS_DEF + ".";
  return null;
}""")
M(gga, r"""
public static String checkStats(String key, String value) {
  String k = key == null ? "" : key.trim();
  int f = k.endsWith("foraging") ? 0 : (k.endsWith("farming") ? 1 : (k.endsWith("fishing") ? 2 : -1));
  if (f < 0 || parse(f, value) != null) return null;
  if (f == 2) return "Write 4 lists of 5 numbers 0-1000 joined by | (Speed | Treasure | Wisdom % | full-set double catch %), e.g. " + DEF[2] + ".";
  return "Write 3 lists of " + FN[f] + " numbers 0-1000 joined by | (Fortune | Wisdom % | full-set Fortune), e.g. " + DEF[f] + ".";
}""")
# one piece's lines = its tier's set totals x its slot share: Foraging / Farming { Fortune, Wisdom % }, Fishing { Speed, Treasure, Wisdom % }
M(gga, r"""
public static double[] piece(int i) {
  if (i < 0 || i >= IDS.length) return new double[3];
  int f = IFAM[i];
  int t = ITIER[i];
  double sh = SHARE[ISLOT[i]];
  if (f == 2) return new double[] { col(2, 0, t) * sh, col(2, 1, t) * sh, col(2, 2, t) * sh };
  return new double[] { col(f, 0, t) * sh, col(f, 1, t) * sh, 0.0 };
}""")

# ================================================================= 0.3.6 GSnd: the ONE sound helper (research/Sound-Pass-Plan.md; SkyyQuests 0.3.1 QSnd's recipe). 2D to
# one player, category UI (SoundUtil.playSoundEvent2dToPlayer). Never throws. pick() = the configured id while sounds.enabled is on (else null =
# silent); the id is looked up in the game's SoundEvent map each time (a missing id = one WARN, nothing played); at most one of the same sound
# per player per GAP_MS; a player whose bridge key settings:sounds:<uuid> is Boolean FALSE hears none (absent / TRUE = play)
F(gsnd, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(gsnd, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")
F(gsnd, "public static final long[] N = new long[3];")          # 0 played, 1 muted by the player, 2 failed
F(gsnd, "public static final long GAP_MS = 500L;")
M(gsnd, r"""
public static int idx(String id) {
  if (id == null) return Integer.MIN_VALUE;
  String v = id.trim();
  if (v.length() == 0) return Integer.MIN_VALUE;
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(v);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
M(gsnd, r"""
public static String err(String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.length() == 0) return null;
  if (v.length() > 120) return "A sound id is at most 120 characters.";
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "A sound id is letters, digits and _ only (like SFX_Weapon_Bench_Craft).";
  }
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    if (m != null && m.getIndex(v) == Integer.MIN_VALUE) return "The game has no sound event '" + v + "' - find ids with /soundtest list, or leave it empty for no sound.";
  } catch (Throwable t) { }
  return null;
}""")
M(gsnd, "public static String check(String key, String value) { return err(value); }")
M(gsnd, r"""
public static String pick(String id) {
  if (!@PKG@.GearCfg.SND_ON || id == null) return null;
  String v = id.trim();
  return v.length() == 0 ? null : v;
}""")
M(gsnd, r"""
public static boolean muted(java.util.UUID u) {
  if (u == null) return false;
  return Boolean.FALSE.equals(@PKG@.Gear.bget("settings:sounds:" + u.toString()));
}""")
M(gsnd, r"""
public static boolean gate(String key, long now) {
  Object o = LAST.get(key);
  if (o instanceof Long) { long d = now - ((Long) o).longValue(); if (d >= 0L && d < GAP_MS) return false; }
  if (LAST.size() > 4096) LAST.clear();
  LAST.put(key, Long.valueOf(now));
  return true;
}""")
M(gsnd, r"""
public static boolean playTo(@PR@ pr, String id, String tag) {
  if (pr == null || id == null) return false;
  try {
    if (!pr.isValid()) return false;
    if (muted(pr.getUuid())) { N[1] = N[1] + 1L; return false; }
    int i = idx(id);
    if (i == Integer.MIN_VALUE || i == 0) {
      if (WARNED.putIfAbsent(id, Boolean.TRUE) == null) @PKG@.Gear.warn("sound event '" + id + "' is not in the game assets - it is not played (Server Setup -> Gear -> Sounds)");
      return false;
    }
    if (!gate(String.valueOf(pr.getUuid()) + "|" + tag, System.currentTimeMillis())) return false;
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    N[0] = N[0] + 1L;
    return true;
  } catch (Throwable t) { N[2] = N[2] + 1L; @PKG@.Gear.warnOnce("gsnd", "could not play a sound (logged once): " + t); return false; }
}""")
M(gsnd, r"""
public static boolean play(java.util.UUID u, String id, String tag) {
  if (u == null || id == null) return false;
  try { return playTo(@UNI@.get().getPlayer(u), id, tag); } catch (Throwable t) { return false; }
}""")
# the identify sting: rank of the best card (0 plain, 1 Rare / Set, 2 Legendary +) - only called when the card page did NOT open
M(gsnd, r"""
public static boolean identify(java.util.UUID u, java.util.ArrayList cards) {
  int best = 0;
  try {
    for (int i = 0; cards != null && i < cards.size(); i++) {
      Object[] c = (Object[]) cards.get(i);
      int rk = c[0] instanceof Integer ? ((Integer) c[0]).intValue() : 0;
      if (rk > best) best = rk;
    }
  } catch (Throwable t) { best = 0; }
  return play(u, pick(best >= 1 ? @PKG@.GearCfg.SND_IDENTR : @PKG@.GearCfg.SND_IDENT), "identify");
}""")
M(gsnd, r"""
public static boolean reforge(java.util.UUID u, String id) {
  boolean arm = id != null && id.startsWith("Armor_");
  return play(u, pick(arm ? @PKG@.GearCfg.SND_REFORGEA : @PKG@.GearCfg.SND_REFORGE), "reforge");
}""")
M(gsnd, "public static boolean sigil(java.util.UUID u) { return play(u, pick(@PKG@.GearCfg.SND_SIGIL), \"sigil\"); }")
M(gsnd, "public static boolean upgrade(java.util.UUID u) { return play(u, pick(@PKG@.GearCfg.SND_UP), \"upgrade\"); }")
M(gsnd, "public static boolean summon(java.util.UUID u) { return play(u, pick(@PKG@.GearCfg.SND_SUMMON), \"summon\"); }")
M(gsnd, r"""
public static String statusText() {
  return "sounds " + (@PKG@.GearCfg.SND_ON ? "on" : "OFF") + " (played " + N[0] + ", muted by players " + N[1] + ", failed " + N[2] + "; per player: settings:sounds:<uuid>)";
}""")

'''
before('''# market.gatheringPrefixes: a gathering set id (null = not one, or market.gatheringSets off)''', P0)
rep('''  if (sid == null || !@PKG@.GearCfg.GSELL) return false;
  String s0 = sid.trim().toLowerCase();
''', '''  if (sid == null || !@PKG@.GearCfg.GSELL) return false;
  String s0 = sid.trim().toLowerCase();
  if (@PKG@.GearGArm.setFam(s0) >= 0) return true;          // 0.3.6: the Foraging / Farming / Fishing sets (fishing_ is no default prefix)
''')

# ================================================================================================================ GearGArm (2/5): helpers that need GearMine
after('''public static double[] bonus(java.util.UUID u) {
  if (u == null || !@PKG@.GearCfg.GM_ON) return null;
  return (double[]) ARM.get(u);
}""")
''', r'''# 0.3.6 GearGArm (2/5): the gate skill of ANY gathering armor piece (Mining metal pieces first) and the set a piece moves to on a tier change
M(gga, r"""
public static String gateAny(String id) {
  if (@PKG@.GearMine.isPiece(id)) return "Mining";
  return gateOf(id);
}""")
M(gga, r"""
public static String setForAny(String id) {
  String s = @PKG@.GearMine.setFor(id);
  return s != null ? s : setFor(id);
}""")
# fix: is sid a gathering set (Mining / Foraging / Farming / Fishing)? Not tied to market.gatheringSets (the tier-up / rebirth set move)
M(gga, r"""
public static boolean isGatherSet(String sid) {
  if (sid == null) return false;
  if (setIdx(sid) >= 0) return true;
  String s0 = sid.trim();
  for (int i = 0; i < @PKG@.GearMine.SET_IDS.length; i++) if (@PKG@.GearMine.SET_IDS[i].equalsIgnoreCase(s0)) return true;
  return @PKG@.GearUtFx.gathering(sid);
}""")
''')

# ================================================================================================================ GearGArm (3/5): the document of a new piece
before('''
# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded''', r'''
# ================================================================= 0.3.6 GearGArm (3/5): the document of a NEW piece - rarity Set, identified, no modifiers,
# level kept inside the tier band (lvl < 0 = no stamp: part.levels off), set field <family>_<f|p|a><tier> (the GearMine.doc shape)
M(gga, r"""
public static @BD@ doc(String id, String src, int lvl) {
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), @PKG@.GearDefs.R_SET, true, src);
  if (lvl >= 0) {
    int[] b = band(id);
    int L = lvl;
    if (b != null) {
      if (L < b[0]) L = b[0];
      if (L > b[1]) L = b[1];
    }
    d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(L)));
  }
  int ix = index(id);          // fix: by id, not setFor - a family switched off still gets its Set document (the switch gates lines / bonuses)
  String sid = ix < 0 ? null : SETS[ix / 4];
  if (sid != null) d.put("set", new org.bson.BsonString(sid));
  return d;
}""")
''')

# ================================================================================================================ GearGArm (4/5): tooltip lines + the set block
before('''# 0.2.15: the set a piece counts for - its document's set field, else (a metal piece without one: old pieces) its Mining Set by id''', r'''# 0.3.6 GearGArm (4/5): the tooltip. A piece's own lines (under the stat lines) and the green set block "Set: Grove Bark (3/4)" + the full-set
# bonus (the count of the owner's last armor pass - GearGArm.WORN; -1 = unknown: "(4 pieces)")
M(gga, r"""
public static String bonusText(int f, int t) {
  double v = col(f, f == 2 ? 3 : 2, t);
  if (!(v > 0.0)) return "no bonus set up";
  if (f == 2) return "+" + num(v) + "% double catch when you fish";
  return "+" + num(v) + " " + FSK[f] + " Fortune";
}""")
M(gga, r"""
public static int worn(java.util.UUID u, String sid) {
  if (u == null || sid == null) return -1;
  Object m = WORN.get(u);
  if (!(m instanceof java.util.HashMap)) return -1;
  Object c = ((java.util.HashMap) m).get(sid.trim().toLowerCase());
  return c instanceof Integer ? ((Integer) c).intValue() : 0;
}""")
M(gga, r"""
public static void lines(java.util.UUID owner, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int i = index(id);
  if (i < 0 || !famOn(IFAM[i])) return;
  int f = IFAM[i];
  double[] v = piece(i);
  if (f == 2) {
    if (v[0] > 0.0) { txt.add("Fishing Speed +" + num(v[0])); col.add(null); }
    if (v[1] > 0.0) { txt.add("Treasure Chance +" + num(v[1])); col.add(null); }
    if (v[2] > 0.0) { txt.add("Fishing Wisdom +" + num(v[2]) + "%"); col.add(null); }
    txt.add("Works while you fish"); col.add(@PKG@.GearDefs.C_GRAY);
    return;
  }
  if (v[0] > 0.0) { txt.add(FSK[f] + " Fortune +" + num(v[0])); col.add(null); }
  if (v[1] > 0.0) { txt.add(FSK[f] + " Wisdom +" + num(v[1]) + "%"); col.add(null); }
  txt.add("Works while you wear it"); col.add(@PKG@.GearDefs.C_GRAY);
}""")
M(gga, r"""
public static boolean tipLines(java.util.UUID owner, String sid, int r, java.util.ArrayList txt, java.util.ArrayList col) {
  int s = setIdx(sid);
  if (s < 0) return false;
  String hex = @PKG@.GearDefs.R_HEX[r == @PKG@.GearDefs.R_MY ? @PKG@.GearDefs.R_MY : @PKG@.GearDefs.R_SET];
  int w = worn(owner, SETS[s]);
  txt.add("Set: " + SNAME[s] + (w >= 0 ? " (" + (w > 4 ? 4 : w) + "/4)" : " (4 pieces)"));
  col.add(hex);
  boolean on = w >= 4;
  txt.add((on ? "Full set bonus: " : "Full set (all 4): ") + bonusText(SFAM[s], STIER[s]));
  col.add(on ? hex : @PKG@.GearDefs.C_GRAY);
  return true;
}""")
''')

# ================================================================================================================ GearGArm (5/5) + GearRbSt: delivery
before('''# ================================================================= GearNotice: players/<pkey>.properties noticeShown (spec 8.2)''', r'''# ================================================================= 0.3.6 GearGArm (5/5): THE DELIVERY. compute = the worn ACTIVE pieces' lines + every complete set's bonus
# (all 4 of one set id; a piece whose document names another set - a quest / boss set - counts only there), capped by armor.fortune.cap /
# armor.wisdom.cap. note (the armor pass: 1 s + every armor change) keeps { Foraging Fortune, Foraging Wisdom %, Farming Fortune, Farming
# Wisdom %, Fishing Speed, Treasure, Fishing Wisdom %, double catch % } in ARM, the set counts in WORN, and posts the skill:bonus source
# "garmor" (dd.foraging / xp.foraging / dd.farming / xp.farming, fractions - WHILE WORN, spec question 7); Fishing goes to gear:fn:fishx
M(gga, r"""
public static double[] compute0(java.util.UUID u, @IC@ armor, java.util.HashMap cnt) {
  double[] o = new double[8];
  if (armor == null || !anyOn()) return o;
  for (int k = 0; k < armor.getCapacity(); k++) {
    @IS@ s = armor.getItemStack((short) k);
    if (s == null || s.isEmpty()) continue;
    String id = s.getItemId();
    int i = index(id);
    if (i < 0 || !famOn(IFAM[i])) continue;
    @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
    if (!@PKG@.GearStats.active(u, id, d)) continue;
    double[] p = piece(i);
    int f = IFAM[i];
    if (f == 0) { o[0] = o[0] + p[0]; o[1] = o[1] + p[1]; }
    else if (f == 1) { o[2] = o[2] + p[0]; o[3] = o[3] + p[1]; }
    else { o[4] = o[4] + p[0]; o[5] = o[5] + p[1]; o[6] = o[6] + p[2]; }
    String sid = d == null ? null : @PKG@.GearSet.of(d);
    if (sid != null && setIdx(sid) < 0) continue;
    String key = (sid == null ? SETS[i / 4] : sid).trim().toLowerCase();
    Object c = cnt == null ? null : cnt.get(key);
    if (cnt != null) cnt.put(key, Integer.valueOf((c instanceof Integer ? ((Integer) c).intValue() : 0) + 1));
  }
  if (cnt != null) {
    java.util.Iterator it = cnt.keySet().iterator();
    while (it.hasNext()) {
      String key = (String) it.next();
      Object c = cnt.get(key);
      if (!(c instanceof Integer) || ((Integer) c).intValue() < 4) continue;
      int si = setIdx(key);
      if (si < 0 || !famOn(SFAM[si])) continue;
      int f = SFAM[si];
      double b = col(f, f == 2 ? 3 : 2, STIER[si]);
      if (f == 0) o[0] = o[0] + b;
      else if (f == 1) o[2] = o[2] + b;
      else o[7] = o[7] + b;
    }
  }
  double fc = @PKG@.GearCfg.GM_FCAP;
  double wc = @PKG@.GearCfg.GM_WCAP;
  o[0] = @PKG@.GearMine.r2(o[0] > fc ? fc : o[0]);
  o[2] = @PKG@.GearMine.r2(o[2] > fc ? fc : o[2]);
  o[7] = @PKG@.GearMine.r2(o[7] > fc ? fc : o[7]);
  o[1] = @PKG@.GearMine.r2(o[1] > wc ? wc : o[1]);
  o[3] = @PKG@.GearMine.r2(o[3] > wc ? wc : o[3]);
  o[6] = @PKG@.GearMine.r2(o[6] > wc ? wc : o[6]);
  o[4] = @PKG@.GearMine.r2(o[4]);
  o[5] = @PKG@.GearMine.r2(o[5]);
  return o;
}""")
# the skill:bonus source "garmor" (the GearTool.postX shape): removed when there is nothing to post, while the profile swaps, or o == null
M(gga, r"""
public static void post(java.util.UUID u, double[] o) {
  if (u == null) return;
  try {
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "skill:bonus:" + u.toString();
    Object cur = b.get(key);
    java.util.HashMap m = new java.util.HashMap();
    if (o != null && !@PKG@.Gear.busy(u)) {
      if (o[0] > 0.0) m.put("dd.foraging", Double.valueOf(o[0] / 100.0));
      if (o[1] > 0.0) m.put("xp.foraging", Double.valueOf(o[1] / 100.0));
      if (o[2] > 0.0) m.put("dd.farming", Double.valueOf(o[2] / 100.0));
      if (o[3] > 0.0) m.put("xp.farming", Double.valueOf(o[3] / 100.0));
    }
    if (m.isEmpty()) {
      if (cur instanceof java.util.Map && ((java.util.Map) cur).remove(SRC) != null) N[2] = N[2] + 1L;
      return;
    }
    java.util.Map src = null;
    if (cur instanceof java.util.Map) src = (java.util.Map) cur;
    else {
      java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
      Object prev = b.putIfAbsent(key, n);
      src = prev instanceof java.util.Map ? (java.util.Map) prev : n;
    }
    if (m.equals(src.get(SRC))) return;
    src.put(SRC, java.util.Collections.unmodifiableMap(m));
    N[1] = N[1] + 1L;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("garmorpost", "gathering armor bridge post failed: " + t); }
}""")
M(gga, r"""
public static void clear(java.util.UUID u) {
  if (u == null) return;
  ARM.remove(u);
  WORN.remove(u);
  post(u, null);
}""")
# fix: shutdown removes every player's "garmor" skill:bonus source (the shared bridge map outlives a SkyyGear reload)
M(gga, r"""
public static void clearAll() {
  Object[] ks = ARM.keySet().toArray();
  for (int i = 0; i < ks.length; i++) if (ks[i] instanceof java.util.UUID) clear((java.util.UUID) ks[i]);
  ARM.clear();
  WORN.clear();
}""")
M(gga, r"""
public static double[] note(java.util.UUID u, @IC@ armor) {
  if (u == null) return null;
  if (@PKG@.GearTool.GONE.containsKey(u)) { clear(u); return null; }
  java.util.HashMap cnt = new java.util.HashMap();
  double[] o = compute0(u, armor, cnt);
  ARM.put(u, o);
  WORN.put(u, cnt);
  post(u, o);
  N[0] = N[0] + 1L;
  return o;
}""")
# gear:fn:fishx (SkyyFishing 0.1.6, at each cast): the worn angler armor (the last armor pass) + YOUR OWN lifelong pole's perks (Fortune =
# double catch %, Wisdom = Fishing XP %, both x the rebirth pole node; Steady Line = the fish pulls this % slower) -> a HashMap of Doubles
# speed / treasure / double / wisdom / pull (java.lang only); never throws
M(gga, r"""
public static java.util.HashMap fishx(java.util.UUID u, @IS@ rod) {
  double sp = 0.0;
  double tr = 0.0;
  double dc = 0.0;
  double wi = 0.0;
  double pc = 0.0;
  try {
    Object o = u == null ? null : ARM.get(u);
    if (o instanceof double[] && @PKG@.GearCfg.GA_FIS_ON) { double[] a = (double[]) o; sp = a[4]; tr = a[5]; wi = a[6]; dc = a[7]; }
    if (u != null && rod != null && !rod.isEmpty() && @PKG@.GearCfg.LL_ON && @PKG@.GearLL.isPole(rod.getItemId()) && !@PKG@.GearLL.rbWait(u)) {
      @BD@ d = @PKG@.GearData.gearDoc(rod.getMetadata());
      if (d != null && @PKG@.GearLL.mine(u, d)) {
        java.util.Properties P = @PKG@.GearLL.reg(@PKG@.Gear.pkey(u));
        int k = @PKG@.GearLL.POLE;
        double rb = @PKG@.GearLL.rbMult(u, k);
        dc = dc + (double) @PKG@.GearLL.perkOf(P, k, 1) * @PKG@.GearCfg.LL_PFORT * rb;
        wi = wi + (double) @PKG@.GearLL.perkOf(P, k, 2) * @PKG@.GearCfg.LL_PWIS * rb;
        pc = pc + (double) @PKG@.GearLL.perkOf(P, k, @PKG@.GearLL.PK_STEADY) * @PKG@.GearCfg.LL_PSTEADY;
      }
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("fishx", "gear:fn:fishx could not read the pole perks (logged once): " + t); }
  if (pc > 90.0) pc = 90.0;
  java.util.HashMap m = new java.util.HashMap();
  m.put("speed", Double.valueOf(sp));
  m.put("treasure", Double.valueOf(tr));
  m.put("double", Double.valueOf(dc));
  m.put("wisdom", Double.valueOf(wi));
  m.put("pull", Double.valueOf(pc));
  N[3] = N[3] + 1L;
  return m;
}""")
M(gga, r"""
public static String meText(java.util.UUID u, @IC@ armor) {
  if (!anyOn()) return "off on this server";
  if (@PKG@.Gear.busy(u)) return "paused while your profile switches";
  double[] a = note(u, armor);
  if (a == null) return "none worn";
  StringBuilder sb = new StringBuilder();
  if (a[0] > 0.0 || a[1] > 0.0) sb.append("Foraging Fortune +").append(num(a[0])).append(", Wisdom +").append(num(a[1])).append("%");
  if (a[2] > 0.0 || a[3] > 0.0) { if (sb.length() > 0) sb.append("; "); sb.append("Farming Fortune +").append(num(a[2])).append(", Wisdom +").append(num(a[3])).append("%"); }
  if (a[4] > 0.0 || a[5] > 0.0 || a[6] > 0.0 || a[7] > 0.0) { if (sb.length() > 0) sb.append("; "); sb.append("Fishing Speed +").append(num(a[4])).append(", Treasure +").append(num(a[5])).append(", Wisdom +").append(num(a[6])).append("%, double catch +").append(num(a[7])).append("%"); }
  return sb.length() > 0 ? sb.toString() : "none worn (or under your skill level)";
}""")
M(gga, r"""
public static String statusText() {
  return "gathering armor (Foraging " + (@PKG@.GearCfg.GA_FOR_ON ? "on" : "OFF") + ", Farming " + (@PKG@.GearCfg.GA_FAR_ON ? "on" : "OFF") + ", Fishing " + (@PKG@.GearCfg.GA_FIS_ON ? "on" : "OFF") + ": " + IDS.length + " green Set pieces, levels with the skill, lines while worn, Health " + @PKG@.GearCfg.GA_SHARE + "%; passes " + N[0] + ", skill:bonus garmor posts " + N[1] + ", gear:fn:fishx " + N[3] + ")";
}""")
# ================================================================= 0.3.6 GearRbSt: REBIRTH DAMAGE / DEFENCE (SkyyRebirth 0.3 rebirth:fn:stat apply(Object[] { UUID, name }) -> Double %):
# damage % = "all" (+3 % per rebirth, cap 30, + the Void Ascendant) + "damage" (the Might nodes); defence % = "all" + "defense" (Guard). NONE
# while rebirth:n:<uuid> is absent / 0, without SkyyRebirth or with rebirth.stats off. Read at most every 2 s per player (any thread)
grst = mk("GearRbSt")
G36_CLASSES.append(grst)
F(grst, "public static final java.util.concurrent.ConcurrentHashMap C = new java.util.concurrent.ConcurrentHashMap();")
F(grst, "public static final long[] N = new long[3];")          # 0 hits raised, 1 hits taken lowered, 2 reads
M(grst, r"""
public static double ask(java.util.function.Function f, java.util.UUID u, String s) {
  try {
    Object r = f.apply(new Object[] { u, s });
    if (r instanceof Number) {
      double d = ((Number) r).doubleValue();
      if (!Double.isNaN(d) && !Double.isInfinite(d) && d > 0.0) return d > 1000.0 ? 1000.0 : d;
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("rbstat", "rebirth:fn:stat failed (logged once): " + t); }
  return 0.0;
}""")
M(grst, r"""
public static double[] get(java.util.UUID u) {
  if (u == null || !@PKG@.GearCfg.RB_STATS) return null;
  long now = System.currentTimeMillis();
  Object o = C.get(u);
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    long at = ((Long) e[0]).longValue();
    if (now >= at && now - at < 2000L) return (double[]) e[1];
  }
  double[] v = new double[2];
  Object n = @PKG@.Gear.bget("rebirth:n:" + u.toString());
  java.util.function.Function f = @PKG@.Gear.fn("rebirth:fn:stat");
  if (n instanceof Integer && ((Integer) n).intValue() > 0 && f != null) {
    double all = ask(f, u, "all");
    v[0] = all + ask(f, u, "damage");
    v[1] = all + ask(f, u, "defense");
  }
  N[2] = N[2] + 1L;
  C.put(u, new Object[] { Long.valueOf(now), v });
  return v;
}""")
M(grst, r"""
public static float dmg(java.util.UUID u, float amt) {
  double[] v = get(u);
  if (v == null || !(v[0] > 0.0) || !(amt > 0.0f)) return amt;
  N[0] = N[0] + 1L;
  return (float) ((double) amt * (1.0 + v[0] / 100.0));
}""")
M(grst, r"""
public static float taken(java.util.UUID u, float amt) {
  double[] v = get(u);
  if (v == null || !(v[1] > 0.0) || !(amt > 0.0f)) return amt;
  N[1] = N[1] + 1L;
  return (float) ((double) amt * 100.0 / (100.0 + v[1]));
}""")
M(grst, "public static void forget(java.util.UUID u) { if (u != null) C.remove(u); }")
M(grst, r"""
public static String statusText() {
  return "rebirth damage / defence " + (@PKG@.GearCfg.RB_STATS ? "on" : "OFF") + " (rebirth:fn:stat " + (@PKG@.Gear.fn("rebirth:fn:stat") != null ? "found" : "not loaded") + "; hits raised " + N[0] + ", hits taken lowered " + N[1] + ")";
}""")

''')
rep('''F(gll, "public static final int[] PKNEED = %s;" % jints(sum([(_p[5] + [99] * 10)[:10] for _p in LL_PERKS], [])))''',
    '''F(gll, "public static final int[] PKNEED = %s;" % jints(sum([(_p[5] + [99] * 10)[:10] for _p in LL_PERKS], [])))
F(gll, "public static final int PK_STEADY = %d;" % [_p[0] for _p in LL_PERKS].index("steady"))          # 0.3.6 the pole's Steady Line''')
# ================================================================================================================ the pole perks (spec 6.3)
rep('''LL_PERKS = [("spd", "Speed", 10, 1 | 2, [1] * 10, [0] * 10),
            ("fort", "Fortune", 10, 15, [1] * 10, [0] * 10),
            ("wis", "Wisdom", 5, 15, [2] * 5, [2] * 5),
            ("vein", "Vein Mine", 3, 1, [3, 5, 8], [2, 3, 4]),
            ("fell", "Tree Feller", 3, 2, [3, 5, 8], [2, 3, 4])]''',
    '''LL_PERKS = [("spd", "Speed", 10, 1 | 2, [1] * 10, [0] * 10),
            ("fort", "Fortune", 10, 15 | 16, [1] * 10, [0] * 10),          # 0.3.6: + the pole (Fishing Fortune = double catch %)
            ("wis", "Wisdom", 5, 15 | 16, [2] * 5, [2] * 5),               # 0.3.6: + the pole (Fishing XP %)
            ("vein", "Vein Mine", 3, 1, [3, 5, 8], [2, 3, 4]),
            ("fell", "Tree Feller", 3, 2, [3, 5, 8], [2, 3, 4]),
            ("steady", "Steady Line", 3, 16, [2, 2, 2], [2, 2, 2])]       # 0.3.6 (spec 6.3): pole only, the fish pulls slower''')
rep('''M(gll, "public static boolean perkFor(int k, int p) { return k >= 0 && k < 4 && p >= 0 && p < PK.length && (PKMASK[p] & (1 << k)) != 0; }")''',
    '''M(gll, "public static boolean perkFor(int k, int p) { return k >= 0 && k < KIND.length && p >= 0 && p < PK.length && (PKMASK[p] & (1 << k)) != 0; }")          # 0.3.6: + the pole''')
after('''M(gll, r"""
public static boolean perkOn(int p) {
  if (p < 3) return true;
  Object o = @PKG@.Gear.bget("gear:perk:readers");
  return o instanceof String && ("," + ((String) o).replace(" ", "") + ",").indexOf("," + PK[p] + ",") >= 0;
}""")
''', '''# 0.3.6: a pole perk works only once SkyyFishing reads it (0.1.6 publishes the bridge string "fishing:perks" = "fort,wis,steady"); the other
# tools keep perkOn (Vein Mine / Tree Feller wait for SkyyTrees' "gear:perk:readers")
M(gll, r"""
public static boolean perkOn2(int k, int p) {
  if (k != POLE) return perkOn(p);
  Object o = @PKG@.Gear.bget("fishing:perks");
  return p >= 0 && p < PK.length && o instanceof String && ("," + ((String) o).replace(" ", "") + ",").indexOf("," + PK[p] + ",") >= 0;
}""")
''')
rep('''  if (!@PKG@.GearLL.perkOn(p)) return "-" + nm + " comes with the next SkyyTrees update - not yet.";''',
    '''  if (!@PKG@.GearLL.perkOn2(k, p)) return "-" + nm + (k == @PKG@.GearLL.POLE ? " needs SkyyFishing 0.1.6 or newer - not yet." : " comes with the next SkyyTrees update - not yet.");          // 0.3.6''')
rep('''  if (u == null || k < 0 || k > 3 || p < 0 || p >= @PKG@.GearLL.PK.length) return "-Pick a tool first.";''',
    '''  if (u == null || k < 0 || k >= @PKG@.GearLL.KIND.length || p < 0 || p >= @PKG@.GearLL.PK.length) return "-Pick a tool first.";          // 0.3.6: + the pole''')
rep('''  if (u == null || k < 0 || k > 3) return "-Pick a tool first.";''',
    '''  if (u == null || k < 0 || k >= @PKG@.GearLL.KIND.length) return "-Pick a tool first.";          // 0.3.6: + the pole''')
# the Tools tab: five rows (106 px each - the 0.3.5 page had four of 130; same 662 px body)
rep('''  b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 130); LayoutMode: Left; Padding: (Full: 8); " + @PKG@.GearUi.rowStyle(k == this.sel) + " " + @PKG@.GearUi.cell(80, id) + " Group { Anchor: (Width: 14); } Group { Anchor: (Width: 340); LayoutMode: Top; Label #SkyyGLRowN" + k + " { Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); } Label #SkyyGLRowA" + k + " { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 15, TextColor: #ffffff(0.7), VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label #SkyyGLRowB" + k + " { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } }");''',
    '''  b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 106); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(k == this.sel) + " " + @PKG@.GearUi.cell(80, id) + " Group { Anchor: (Width: 14); } Group { Anchor: (Width: 340); LayoutMode: Top; Label #SkyyGLRowN" + k + " { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); } Label #SkyyGLRowA" + k + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 15, TextColor: #ffffff(0.7), VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label #SkyyGLRowB" + k + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } }");          // 0.3.6: 5 rows''')
rep('''  if (p == 0) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSPD) + "% " + (k == 1 ? "Chopping" : "Mining") + " Power";''',
    '''  if (p == 0) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSPD) + "% " + (k == 1 ? "Chopping" : "Mining") + " Power";
  if (k == @PKG@.GearLL.POLE && p == 1) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PFORT) + "% double catch";          // 0.3.6 the pole
  if (k == @PKG@.GearLL.POLE && p == @PKG@.GearLL.PK_STEADY) return "the fish pulls " + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSTEADY) + "% slower";''')
rep('''  boolean on = @PKG@.GearLL.perkOn(p);''', '''  boolean on = @PKG@.GearLL.perkOn2(k, p);          // 0.3.6''')
rep('''  if (!on) nx = "Comes with the next SkyyTrees update";''', '''  if (!on) nx = k == @PKG@.GearLL.POLE ? "Needs SkyyFishing 0.1.6 or newer" : "Comes with the next SkyyTrees update";          // 0.3.6''')
rep('''  int k = this.sel < 0 || this.sel > 3 ? 0 : this.sel;''', '''  int k = this.sel < 0 || this.sel >= @PKG@.GearLL.KIND.length ? 0 : this.sel;          // 0.3.6: + the pole''')
rep('''  if (to == null) tl = tl + "Top tier for now.";''', '''  if (k == @PKG@.GearLL.POLE) tl = tl + "Tier it up at the Fishing Bench (the rod recipes keep it your pole).";          // 0.3.6
  else if (to == null) tl = tl + "Top tier for now.";''')
rep('''  for (int k = 0; k < 4; k++) row(b, ev, u, inv, pk, P, k);
  b.appendInline("#SkyyGList", "Label #SkyyGLHelp { Anchor: (Height: 58); Text: \\"\\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGLHelp.Text", "They level with your skills and can't be dropped. Tier them up on the Anvil. Lost one? /pickaxe, /hatchet, /hoe or /sickle.");''',
    '''  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) { if (k == @PKG@.GearLL.POLE && @PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) continue; row(b, ev, u, inv, pk, P, k); }          // 0.3.6: + the fishing pole (5 rows; no SkyyFishing = no pole row)
  b.appendInline("#SkyyGList", "Label #SkyyGLHelp { Anchor: (Height: 58); Text: \\"\\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGLHelp.Text", "They level with your skills and can't be dropped. Tier them up on the Anvil (the pole at the Fishing Bench). Lost one? /pickaxe, /hatchet, /hoe, /sickle or /pole.");''')
rep('''      if (k >= 0 && k < 4) { this.sel = k; this.armK = -1; this.info = ""; }''',
    '''      if (k >= 0 && k < @PKG@.GearLL.KIND.length) { this.sel = k; this.armK = -1; this.info = ""; }          // 0.3.6: + the pole''')
rep('''    if (k >= 0 && k < 4) page.sel = k;          // 0.3.5: the pole is not on the four-row Tools tab''',
    '''    if (k >= 0 && k < @PKG@.GearLL.KIND.length) page.sel = k;          // 0.3.6: the pole has its row on the Tools tab''')
# the pole's level on its own tooltip: SkyyFishing 0.1.6 draws "[Lv N]" from the document - ask it to redraw right after a new level is written
rep('''public static boolean put(@IC@ c, int slot, @IS@ x, @BD@ nd, java.util.UUID u) {
  try {
    @IS@ ns = @PKG@.GearData.put(x, nd, u);''', '''public static boolean put(@IC@ c, int slot, @IS@ x, @BD@ nd, java.util.UUID u) {
  try {
    @IS@ ns = @PKG@.GearData.put(x, nd, u);
    if (@PKG@.GearLL.isPole(ns.getItemId())) ns = poleRedraw(ns, nd);          // 0.3.6: SkyyFishing redraws the pole's name ("[Lv N]") + rig lines''')
before('''M(glf, r"""
public static boolean put(@IC@ c, int slot, @IS@ x, @BD@ nd, java.util.UUID u) {''', '''# 0.3.6: fishing:fn:restamp (SkyyFishing 0.1.5+, ItemStack -> ItemStack: its name + rig lines; 0.1.6 adds "[Lv N]" from our document) after a
# pole write; kept only when the answer is the same rod carrying the same document (uid + level); no SkyyFishing / an error = the stack as written
M(glf, r"""
public static @IS@ poleRedraw(@IS@ ns, @BD@ nd) {
  java.util.function.Function f = @PKG@.Gear.fn("fishing:fn:restamp");
  if (f == null || ns == null || nd == null) return ns;
  try {
    Object r = f.apply(ns);
    if (r instanceof @IS@) {
      @IS@ s2 = (@IS@) r;
      @BD@ d2 = @PKG@.GearData.gearDoc(s2.getMetadata());
      if (ns.getItemId().equals(s2.getItemId()) && s2.getQuantity() == ns.getQuantity() && d2 != null
          && @PKG@.GearLL.uid(d2).equals(@PKG@.GearLL.uid(nd)) && @PKG@.GearData.num(d2, "lvl", -1) == @PKG@.GearData.num(nd, "lvl", -1)) return s2;
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("poleredraw", "fishing:fn:restamp failed - the pole keeps its old name (logged once): " + t); }
  return ns;
}""")
''')
# gear:fn:fishx (mode 4)
rep('''    if (this.mode == 3) return a[1] instanceof @IS@ ? @PKG@.GearLife.poleStamp(u, (@IS@) a[1], a.length > 2 && a[2] instanceof String ? (String) a[2] : null) : a[1];          // 0.3.5 gear:fn:pole''',
    '''    if (this.mode == 3) return a[1] instanceof @IS@ ? @PKG@.GearLife.poleStamp(u, (@IS@) a[1], a.length > 2 && a[2] instanceof String ? (String) a[2] : null) : a[1];          // 0.3.5 gear:fn:pole
    if (this.mode == 4) return @PKG@.GearGArm.fishx(u, a[1] instanceof @IS@ ? (@IS@) a[1] : null);          // 0.3.6 gear:fn:fishx (SkyyFishing 0.1.6, each cast)''')
rep('''  br.put("gear:fn:pole", new @PKG@.GearLLFn(3));           // 0.3.5: SkyyFishing 0.1.5 stamps Marlow's quest pole lifelong''',
    '''  br.put("gear:fn:pole", new @PKG@.GearLLFn(3));           // 0.3.5: SkyyFishing 0.1.5 stamps Marlow's quest pole lifelong
  br.put("gear:fn:fishx", new @PKG@.GearLLFn(4));          // 0.3.6: the angler armor + the pole perks for SkyyFishing 0.1.6''')
rep('''bq.remove("gear:fn:pole"); bq.remove("rebirth:part:gear"); }''', '''bq.remove("gear:fn:pole"); bq.remove("rebirth:part:gear"); bq.remove("gear:fn:fishx"); }''')

# ================================================================================================================ hooks: levels, gate, docs, crafts
rep('''    if (v != null && v.isNumber()) return clamp(v.asNumber().intValue());
  } catch (Throwable t) { }
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);
  if (o instanceof Integer) return clamp(((Integer) o).intValue());
  java.util.HashMap mat = @PKG@.GearCfg.MAT;''', '''    if (v != null && v.isNumber()) return clamp(v.asNumber().intValue());
  } catch (Throwable t) { }
  int[] gb0 = @PKG@.GearGArm.band(id);          // 0.3.6: a Foraging / Farming / Fishing piece starts at its tier band (garmor.bands)
  if (gb0 != null) return clamp(gb0[0]);
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);
  if (o instanceof Integer) return clamp(((Integer) o).intValue());
  java.util.HashMap mat = @PKG@.GearCfg.MAT;''')
rep('''  if (ub != null) return new int[] { clamp(ub[0]), clamp(ub[1] < ub[0] ? ub[0] : ub[1]), 1 };
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);''', '''  if (ub != null) return new int[] { clamp(ub[0]), clamp(ub[1] < ub[0] ? ub[0] : ub[1]), 1 };
  int[] gb = @PKG@.GearGArm.band(id);          // 0.3.6: the gathering armor tier bands (never the id-word material match)
  if (gb != null) return new int[] { clamp(gb[0]), clamp(gb[1] < gb[0] ? gb[0] : gb[1]), 1 };
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);''')
rep('''  if (@PKG@.GearMine.isPiece(id)) { gate = "Mining"; enforced = true; }
  if (@PKG@.GearData.isMulti(id)) return checkMulti(u, need);          // 0.2.18: Mining AND Foraging''',
    '''  if (@PKG@.GearMine.isPiece(id)) { gate = "Mining"; enforced = true; }
  String gg36 = @PKG@.GearGArm.gateOf(id);          // 0.3.6: the Foraging / Farming / Fishing pieces need that skill's level
  if (gg36 != null) { gate = gg36; enforced = true; }
  if (@PKG@.GearData.isMulti(id)) return checkMulti(u, need);          // 0.2.18: Mining AND Foraging''')
rep('''  if (@PKG@.GearMine.isPiece(id)) return @PKG@.GearMine.doc(id, src, lvl);''',
    '''  if (@PKG@.GearMine.isPiece(id)) return @PKG@.GearMine.doc(id, src, lvl);
  if (@PKG@.GearGArm.index(id) >= 0) return @PKG@.GearGArm.doc(id, src, lvl);          // 0.3.6: the same for the Foraging / Farming / Fishing pieces (by id: a family switched off still gets the Set document)''')
rep('''  if (@PKG@.GearMine.isPiece(id)) return "Mining";      // 0.2.15: metal armor is made at your Mining level''',
    '''  if (@PKG@.GearMine.isPiece(id)) return "Mining";      // 0.2.15: metal armor is made at your Mining level
  String g36 = @PKG@.GearGArm.gateOf(id);          // 0.3.6: the bark / crop / angler sets at your Foraging / Farming / Fishing level
  if (g36 != null) return g36;''')
rep('''  if (@PKG@.GearMine.isPiece(id)) return "Mining";      // 0.2.15
  String w = weaponSkill(id);''', '''  if (@PKG@.GearMine.isPiece(id)) return "Mining";      // 0.2.15
  String g36 = @PKG@.GearGArm.gateOf(id);          // 0.3.6
  if (g36 != null) return g36;
  String w = weaponSkill(id);''')
rep('''  if (r == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) r = 0;
  double v = (double) @PKG@.GearCfg.xpCraft(r) * xpTier(xpStart(id));''', '''  if (r == @PKG@.GearDefs.R_SET && (@PKG@.GearMine.isPiece(id) || @PKG@.GearGArm.index(id) >= 0)) r = 0;          // 0.3.6: + the new sets (by id: a family switched off still pays the normal row)
  double v = (double) @PKG@.GearCfg.xpCraft(r) * xpTier(xpStart(id));''')
rep('''  if (@PKG@.GearCfg.GM_SHARE != 100 && @PKG@.GearMine.isPiece(id)) {
    double sh = (double) @PKG@.GearCfg.GM_SHARE / 100.0;
    h = h * sh;
    r = r * sh;
  }''', '''  if (@PKG@.GearCfg.GM_SHARE != 100 && @PKG@.GearMine.isPiece(id)) {
    double sh = (double) @PKG@.GearCfg.GM_SHARE / 100.0;
    h = h * sh;
    r = r * sh;
  }
  // 0.3.6: the Foraging / Farming / Fishing pieces give garmor.gatherShare % ("low Defense", default 50)
  if (@PKG@.GearCfg.GA_SHARE != 100 && @PKG@.GearGArm.index(id) >= 0) {
    double sg = (double) @PKG@.GearCfg.GA_SHARE / 100.0;
    h = h * sg;
    r = r * sg;
  }''')
rep('''  if (r == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) return false;
  return true;''', '''  if (r == @PKG@.GearDefs.R_SET && (@PKG@.GearMine.isPiece(id) || @PKG@.GearGArm.index(id) >= 0)) return false;          // 0.3.6 (by id: never reforgeable, even with the family off)
  return true;''')
rep('''  boolean mine = @PKG@.GearMine.isPiece(id);       // 0.2.15: a mining piece is enforced with the Mining gate
  if (mine) gate = "Mining";''', '''  String ga36 = @PKG@.GearGArm.gateAny(id);       // 0.2.15: a mining piece is enforced with the Mining gate (0.3.6: + Foraging / Farming / Fishing)
  boolean mine = ga36 != null;
  if (mine) gate = ga36;''')
rep('''  boolean mine = @PKG@.GearMine.isPiece(id);
  if (mine) gate = "Mining";''', '''  String ga36 = @PKG@.GearGArm.gateAny(id);          // 0.3.6
  boolean mine = ga36 != null;
  if (mine) gate = ga36;''')
rep('''    if (slot == 2) @PKG@.GearMine.lines(owner, id, d, bt, bc);   // 0.2.15: a metal piece's mining lines''',
    '''    if (slot == 2) @PKG@.GearMine.lines(owner, id, d, bt, bc);   // 0.2.15: a metal piece's mining lines
    if (slot == 2) @PKG@.GearGArm.lines(owner, id, d, bt, bc);   // 0.3.6: a bark / crop / angler piece's lines''')
rep('''  String s = of(d);
  if (s != null) return s;
  return @PKG@.GearMine.setFor(id);''', '''  String s = of(d);
  if (s != null) return s;
  return @PKG@.GearGArm.setForAny(id);          // 0.3.6: + the Foraging / Farming / Fishing sets''')
rep('''  String sid = sidOf(id, d);       // 0.2.15: a metal piece without a set field shows its Mining Set
  if (sid == null) return;''', '''  String sid = sidOf(id, d);       // 0.2.15: a metal piece without a set field shows its Mining Set
  if (sid == null) return;
  if (@PKG@.GearGArm.tipLines(owner, sid, r, txt, col)) return;          // 0.3.6: the bark / crop / angler sets have their own block''')
rep('''!@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id) && !@PKG@.GearUtFx.mythicId(id); } catch (Throwable x) { v = false; }''',
    '''!@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id) && @PKG@.GearGArm.index(id) < 0 && !@PKG@.GearUtFx.mythicId(id); } catch (Throwable x) { v = false; }''')
rep('''  if (@PKG@.GearMine.isPiece(id)) return null;        // 0.2.15: gathering armor never drops unidentified''',
    '''  if (@PKG@.GearMine.isPiece(id) || @PKG@.GearGArm.index(id) >= 0) return null;        // 0.2.15: gathering armor never drops unidentified (0.3.6: + the new sets)''')
rep('''      if (@PKG@.GearMine.isPiece(s.getItemId())) return null;      // 0.2.15: a mining piece is never a bag''',
    '''      if (@PKG@.GearMine.isPiece(s.getItemId()) || @PKG@.GearGArm.index(s.getItemId()) >= 0) return null;      // 0.2.15: a mining piece is never a bag (0.3.6: + the new sets)''')
rep('''  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) why = "Mining Set pieces have fixed mining lines - they cannot be reforged (Level up still works).";''',
    '''  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) why = "Mining Set pieces have fixed mining lines - they cannot be reforged (Level up still works).";
  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_SET && @PKG@.GearGArm.index(id) >= 0) why = "Gathering Set pieces have fixed lines - they cannot be reforged.";          // 0.3.6''')
rep('''  if (@PKG@.GearMine.isPiece(s0.getItemId())) return 0;      // 0.2.15''',
    '''  if (@PKG@.GearMine.isPiece(s0.getItemId()) || @PKG@.GearGArm.index(s0.getItemId()) >= 0) return 0;      // 0.2.15 (0.3.6: + the new sets)''')
# the armor pass
rep('''  if (busy) { @PKG@.GearMine.clear(u); return; }      // 0.2.15: no mining lines / lamp while the profile swaps
  warnLines(pr, u, armor);
  double[] mine = @PKG@.GearMine.note(u, armor);        // 0.2.15: the worn mining armor (+ the helmet lamp)''',
    '''  if (busy) { @PKG@.GearMine.clear(u); @PKG@.GearGArm.clear(u); return; }      // 0.2.15: no mining lines / lamp while the profile swaps (0.3.6: + garmor)
  warnLines(pr, u, armor);
  double[] mine = @PKG@.GearMine.note(u, armor);        // 0.2.15: the worn mining armor (+ the helmet lamp)
  @PKG@.GearGArm.note(u, armor);        // 0.3.6: the worn Foraging / Farming / Fishing armor (skill:bonus source garmor + gear:fn:fishx)''')
rep('''    @PKG@.GearArmLv.forget(u);     // 0.3.4
    @PKG@.GearTill.forget(u);     // 0.3.4''', '''    @PKG@.GearArmLv.forget(u);     // 0.3.4
    @PKG@.GearTill.forget(u);     // 0.3.4
    @PKG@.GearGArm.clear(u);     // 0.3.6: the garmor skill:bonus source
    @PKG@.GearRbSt.forget(u);     // 0.3.6''')
rep('''    msg(pr, "Mining armor: " + @PKG@.GearMine.meText(u, inv.getArmor()));        // 0.2.15''',
    '''    msg(pr, "Mining armor: " + @PKG@.GearMine.meText(u, inv.getArmor()));        // 0.2.15
    msg(pr, "Gathering armor: " + @PKG@.GearGArm.meText(u, inv.getArmor()));        // 0.3.6''')
# GearArmLv: every gathering skill
rep('''  if (!@PKG@.GearCfg.GARM_LV || id == null) return null;
  return @PKG@.GearMine.isPiece(id) ? "Mining" : null;''', '''  if (!@PKG@.GearCfg.GARM_LV || id == null) return null;
  return @PKG@.GearGArm.gateAny(id);          // 0.3.6: Mining metal pieces + the Foraging / Farming / Fishing sets''')
rep('''    int h = @PKG@.GearGate.have(u, "Mining");
    Object o = LV.get(u);''', '''    int h = @PKG@.GearGate.have(u, "Mining");
    if (@PKG@.GearGArm.anyOn()) h = ((h * 211 + @PKG@.GearGate.have(u, "Foraging")) * 211 + @PKG@.GearGate.have(u, "Farming")) * 211 + @PKG@.GearGate.have(u, "Fishing");          // 0.3.6
    Object o = LV.get(u);''')
rep('''  return "gathering armor " + (@PKG@.GearCfg.GARM_LV ? "levels with the skill (Mining pieces: Mining level kept inside the tier band; Anvil tier-up "''',
    '''  return "gathering armor " + (@PKG@.GearCfg.GARM_LV ? "levels with the skill (Mining / Foraging / Farming / Fishing pieces: the skill level kept inside the tier band; Anvil tier-up "''')
# the Anvil ladders + the tier-up set field
rep('''  String c = @PKG@.GearCfg.GARM_LADDERS == null || !@PKG@.GearCfg.GARM_LV ? "" : @PKG@.GearCfg.GARM_LADDERS;          // 0.3.4: gathering armor''',
    '''  String c = @PKG@.GearCfg.GARM_LADDERS == null || !@PKG@.GearCfg.GARM_LV ? "" : @PKG@.GearCfg.GARM_LADDERS;          // 0.3.4: gathering armor
  if (@PKG@.GearCfg.GARM_LV) {          // 0.3.6: + the Foraging / Farming / Fishing ladders of the families that are on
    if (@PKG@.GearCfg.GA_FOR_ON && @PKG@.GearCfg.GA_LAD0 != null && @PKG@.GearCfg.GA_LAD0.trim().length() > 0) c = c.trim().length() == 0 ? @PKG@.GearCfg.GA_LAD0 : c + "," + @PKG@.GearCfg.GA_LAD0;
    if (@PKG@.GearCfg.GA_FAR_ON && @PKG@.GearCfg.GA_LAD1 != null && @PKG@.GearCfg.GA_LAD1.trim().length() > 0) c = c.trim().length() == 0 ? @PKG@.GearCfg.GA_LAD1 : c + "," + @PKG@.GearCfg.GA_LAD1;
    if (@PKG@.GearCfg.GA_FIS_ON && @PKG@.GearCfg.GA_LAD2 != null && @PKG@.GearCfg.GA_LAD2.trim().length() > 0) c = c.trim().length() == 0 ? @PKG@.GearCfg.GA_LAD2 : c + "," + @PKG@.GearCfg.GA_LAD2;
  }''')
rep('''    String os = @PKG@.GearSet.of(nd);
    String ns = @PKG@.GearMine.setFor(to);
    if (os != null && ns != null && @PKG@.GearUtFx.gathering(os)) nd.put("set", new org.bson.BsonString(ns));''',
    '''    String os = @PKG@.GearSet.of(nd);
    String ns = @PKG@.GearGArm.setForAny(to);          // 0.3.6: + the Foraging / Farming / Fishing sets
    if (os != null && ns != null && @PKG@.GearGArm.isGatherSet(os)) nd.put("set", new org.bson.BsonString(ns));          // fix: not tied to market.gatheringSets''')
# rebirth (D9): every gathering family goes back to its tier 1
rep('''public static String rbArmorTo(String id) {
  if (id == null || !id.startsWith("Armor_") || !@PKG@.GearMine.isPiece(id)) return null;''', '''public static String rbArmorTo(String id) {
  String g36 = @PKG@.GearGArm.t1Of(id);          // 0.3.6: a Foraging / Farming / Fishing piece -> its family's tier 1, same slot
  if (g36 != null) return @PKG@.Gear.item(g36) != null ? g36 : null;
  if (id == null || !id.startsWith("Armor_") || !@PKG@.GearMine.isPiece(id)) return null;''')
rep('''      String ns2 = @PKG@.GearMine.setFor(to);
      if (os != null && ns2 != null && @PKG@.GearUtFx.gathering(os)) nd.put("set", new org.bson.BsonString(ns2));''', '''      String ns2 = @PKG@.GearGArm.setForAny(to);          // 0.3.6
      if (os != null && ns2 != null && @PKG@.GearGArm.isGatherSet(os)) nd.put("set", new org.bson.BsonString(ns2));          // fix: not tied to market.gatheringSets''')
rep('''their rarity and rolls stay. Your Mining armor goes back to Copper.", 5000L);''', '''their rarity and rolls stay. Your gathering armor goes back to its first tier.", 5000L);''')

# ================================================================================================================ rebirth damage / defence
rep('''        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);''',
    '''        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);
        // 0.3.6 REBIRTH DAMAGE (rebirth:fn:stat all + damage; none while rebirth n = 0)
        if (!d.isCancelled()) { float rbd = @PKG@.GearRbSt.dmg(u, d.getAmount()); if (rbd != d.getAmount()) d.setAmount(rbd); }''')
rep('''      double utk = @PKG@.GearUtFx.taken(vu, full);
      if (utk != 0.0) { d.setAmount(@PKG@.GearUtFx.takenAmount(d.getAmount(), utk)); @PKG@.GearUtFx.count(3); }
    }''', '''      double utk = @PKG@.GearUtFx.taken(vu, full);
      if (utk != 0.0) { d.setAmount(@PKG@.GearUtFx.takenAmount(d.getAmount(), utk)); @PKG@.GearUtFx.count(3); }
    }
    // 0.3.6 REBIRTH DEFENCE (rebirth:fn:stat all + defense): damage with an entity source x 100 / (100 + %); none while rebirth n = 0
    if (d.getSource() instanceof @DENT@) { float rbv = @PKG@.GearRbSt.taken(vu, d.getAmount()); if (rbv != d.getAmount()) d.setAmount(rbv); }''')

# ================================================================================================================ sounds
rep('''  if (u == null || cards == null || cards.isEmpty() || f == null) { RV[2] = RV[2] + 1L; return false; }''',
    '''  if (u == null || cards == null || cards.isEmpty() || f == null) { RV[2] = RV[2] + 1L; @PKG@.GSnd.identify(u, cards); return false; }          // 0.3.6: no card page = our sting''')
rep('''  boolean ok = Boolean.TRUE.equals(r);
  if (ok) RV[1] = RV[1] + 1L; else RV[2] = RV[2] + 1L;
  return ok;''', '''  boolean ok = Boolean.TRUE.equals(r);
  if (ok) RV[1] = RV[1] + 1L; else { RV[2] = RV[2] + 1L; @PKG@.GSnd.identify(u, l); }          // 0.3.6: the card page plays its own stings
  return ok;''')
rep('''  @PKG@.GearLog.line("REFORGE " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r] + " lv" + lvl + " [" + @PKG@.GearView.modSummary(d) + "] -> [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost + " rfN " + @PKG@.GearData.num(nd, "rfN", 0) + (free ? " (admin, free)" : ""));''',
    '''  @PKG@.GearLog.line("REFORGE " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r] + " lv" + lvl + " [" + @PKG@.GearView.modSummary(d) + "] -> [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost + " rfN " + @PKG@.GearData.num(nd, "rfN", 0) + (free ? " (admin, free)" : ""));
  @PKG@.GSnd.reforge(u, id);          // 0.3.6''')
rep('''  @PKG@.GearLog.line("UPGRADE " + who + " " + u + " " + id + " -> " + to + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)] + " lv" + @PKG@.GearLevel.level(to, nd) + " [" + @PKG@.GearView.modSummary(nd) + "] lowered " + info[1] + " @" + @PKG@.GearForge.where(s, slot));''',
    '''  @PKG@.GearLog.line("UPGRADE " + who + " " + u + " " + id + " -> " + to + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)] + " lv" + @PKG@.GearLevel.level(to, nd) + " [" + @PKG@.GearView.modSummary(nd) + "] lowered " + info[1] + " @" + @PKG@.GearForge.where(s, slot));
  @PKG@.GSnd.upgrade(u);          // 0.3.6''')
rep('''  @PKG@.GearLog.line("SIGIL " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r0] + " -> " + @PKG@.GearDefs.R_ID[R] + " [" + @PKG@.GearView.modSummary(nd) + "] sgN " + @PKG@.GearData.num(nd, "sgN", 0) + " @" + @PKG@.GearForge.where(s, slot));''',
    '''  @PKG@.GearLog.line("SIGIL " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r0] + " -> " + @PKG@.GearDefs.R_ID[R] + " [" + @PKG@.GearView.modSummary(nd) + "] sgN " + @PKG@.GearData.num(nd, "sgN", 0) + " @" + @PKG@.GearForge.where(s, slot));
  @PKG@.GSnd.sigil(u);          // 0.3.6''')
rep('''  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from " + from + " -> " + wh);''',
    '''  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from " + from + " -> " + wh);
  @PKG@.GSnd.summon(u);          // 0.3.6''')
rep('''  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from Requip " + eid + " -> " + wh);''',
    '''  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from Requip " + eid + " -> " + wh);
  @PKG@.GSnd.summon(u);          // 0.3.6''')
rep('''  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from the Vault " + at + " -> " + wh);''',
    '''  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from the Vault " + at + " -> " + wh);
  @PKG@.GSnd.summon(u);          // 0.3.6''')
rep('''  @PKG@.GearLog.line("LL-" + (src != null ? "COPY " : (rp ? "RECLAIM " : "GIVE ")) + u + " " + pk + " " + K + " " + lu + " " + id + " lv" + @PKG@.GearLevel.level(id, nd) + (cu != null ? " exact copy of " + cu + " [" + @PKG@.GearView.modSummary(nd) + "]" : ""));''',
    '''  @PKG@.GearLog.line("LL-" + (src != null ? "COPY " : (rp ? "RECLAIM " : "GIVE ")) + u + " " + pk + " " + K + " " + lu + " " + id + " lv" + @PKG@.GearLevel.level(id, nd) + (cu != null ? " exact copy of " + cu + " [" + @PKG@.GearView.modSummary(nd) + "]" : ""));
  if (src != null || rp) @PKG@.GSnd.summon(u);          // 0.3.6: an exact copy / a reclaim (never the first gift)''')

# fix (critic: set field / market switch): a gathering set climbs its Anvil ladder whatever market.gatheringSets says (that row is about selling)
rep('''  return sid == null || @PKG@.GearUtFx.gathering(sid);
}""")''',
    '''  return sid == null || @PKG@.GearGArm.isGatherSet(sid);          // fix: not tied to market.gatheringSets
}""")''')
# fix (shutdown): the "garmor" skill:bonus sources go with the "gear" ones
rep('''  try { @PKG@.GearTool.clearAll(); } catch (Throwable t5) { }   // 0.2.12: our skill:bonus sources''',
    '''  try { @PKG@.GearTool.clearAll(); } catch (Throwable t5) { }   // 0.2.12: our skill:bonus sources
  try { @PKG@.GearGArm.clearAll(); } catch (Throwable t5b) { }   // 0.3.6: + the gathering armor source "garmor"''')
# fix (Tools tab): the pole row only while SkyyFishing's rods exist; the icon fallback is always a registered item
rep('''  if (id != null && @PKG@.Gear.item(id) != null) return id;
  return @PKG@.GearLL.KCRUDE[k];
}""")''', '''  if (id != null && @PKG@.Gear.item(id) != null) return id;
  if (@PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) return @PKG@.GearLL.KCRUDE[0];          // 0.3.6: no SkyyFishing = no rod item - never send an unknown ItemIcon
  return @PKG@.GearLL.KCRUDE[k];
}""")''')

# ================================================================================================================ the class list, ready line, manifest, jar checks
rep('''+ LIFE_CLASSES + G34_CLASSES''', '''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES''')
rep('''@PKG@.GearRb.statusText() + "; identify reveal "''',
    '''@PKG@.GearRb.statusText() + "; " + @PKG@.GearGArm.statusText() + "; " + @PKG@.GearRbSt.statusText() + "; " + @PKG@.GSnd.statusText() + "; identify reveal "''')
rep('''gear:fn:farmTier, gear:fn:pole, rebirth:part:gear; wand / staff tooltips''', '''gear:fn:farmTier, gear:fn:pole, gear:fn:fishx, rebirth:part:gear; wand / staff tooltips''')
rep('''rebirths reset lifelong tools to Crude and Mining armor to Copper (rebirth:part:gear) and open multitools; Server Setup -> Gear.''',
    '''rebirths reset lifelong tools to Crude and gathering armor to its first tier (rebirth:part:gear) and open multitools; GATHERING ARMOR for Foraging (bark sets), Farming (crop sets) and Fishing (angler sets): green Set pieces that level with their skill, give Fortune / Wisdom (Fishing Speed, Treasure, double catch) while worn, tier up on the Anvil and give a full-set bonus; the fishing pole's Fortune, Wisdom and Steady Line perks (with SkyyFishing 0.1.6); rebirth damage and defence from SkyyRebirth; identify, reforge, Sigil, tier-up and summon sounds; Server Setup -> Gear.''')
rep('''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS)), "SkyyGear 0.3.4 ships the 8 mystery bags + the 16 Untiered copies + the 5 Sigils"''',
    '''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS)), "SkyyGear 0.3.6 ships the 8 mystery bags + the 16 Untiered copies + the 5 Sigils + the 68 gathering armor pieces"
    for _k, _v in list(GA2_ITEMS.items()) + list(GA2_FILES.items()):          # 0.3.6
        assert _jz.read(_k) == (_v.encode("utf-8") if isinstance(_v, str) else _v), "gathering armor file missing from the jar: " + _k''')

# ================================================================================================================ checks on the result
print("counts", s.count("@PKG@.GSnd."), s.count("@PKG@.GearGArm."), s.count("G36_CLASSES"))
assert s.count("@PKG@.GSnd.") == 10 and s.count("@PKG@.GearGArm.") >= 30 and s.count("G36_CLASSES") == 3
assert s.count("@PSTEADY@") == 0 and s.count('"steady", "Steady Line"') == 1
assert s.index('gga = mk("GearGArm")') < s.index("public static boolean gathering(String sid)") < s.index('F(gmine, "public static final String[] IDS')
assert s.index("public static String gateAny(String id)") < s.index("public static Object[] check(java.util.UUID u, String id, @BD@ d, int need)")
assert s.index("public static @BD@ doc(String id, String src, int lvl) {\n  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), @PKG@.GearDefs.R_SET, true, src);\n  if (lvl >= 0) {\n    int[] b = band(id);") < s.index("public static @BD@ newDoc(")
assert s.index("public static boolean tipLines(java.util.UUID owner, String sid, int r") < s.index("public static String sidOf(String id, @BD@ d)")
assert s.index("public static java.util.HashMap fishx(") < s.index('br.put("gear:fn:fishx"') and s.index('grst = mk("GearRbSt")') < s.index("dmg_system(ghsy")
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.5 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.5 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
