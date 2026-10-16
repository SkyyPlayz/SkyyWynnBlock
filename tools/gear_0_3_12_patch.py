"""Derive SkyyGear/build_skyygear_0.3.12.py from the LIVE 0.3.11 (build_skyygear_0.3.11.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_11_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_12_patch.py      then      python SkyyGear/build_skyygear_0.3.12.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.12.py

0.3.12 (2026-10-16, round "gear0312"; Skyy 2026-10-15 "ohh small farming update, we need a watering can too. and i want it to spawn with you and
upgrade like the forever tools. (at least tier up for more watering range. idk what kinds of upgrades we could give a watering can.) and id like
to make a new kind of multitool the combines the hoe and the sickle." + "lets add a T1 crude watering can, (made of wood.) upgrades to a T2
copper T3 iron and so no"; popups: "Harvester (Recommended)", "Capacity / refill,Growth boost,Lasting water,Bloom (fertilize chance)", "Same as
multitool: rebirth 1 (Recommended)"; Skyy 2026-10-16 "watering can first then pet eggs"; spec research/Watering-Can-Harvester-Spec.md):
1. THE LIFELONG WATERING CAN = the 6th lifelong kind "can" (GearLL.CAN = 5, /can). Items Tool_WaterCan_Crude / _Copper / _Iron / _Thorium /
   _Cobalt / _Adamantite (our own ids; Mithril / Onyxium wait for their Enchanted items like the pickaxe ladder), made at BUILD time from the
   vanilla Tool_Watering_Can (its full-can model BY PATH; a per-tier recoloured copy of its texture + icon - Crude = wood, Copper, the vanilla
   iron look for Iron, Thorium, Cobalt, Adamantite; nothing vanilla committed). No BlockType (never placed as a block), no recipe, MaxStack 1,
   MaxDurability 100 = the water bar, Repairable false, no durability loss on death (vanilla's "charges" rules).
   VANILLA FIRST (VERIFIED bytecode 2026-10-16, Hytale 0.7.2): vanilla has the item Tool_Watering_Can (3 Iron Bars at the Farming Bench) and
   the engine interaction UseWateringCanInteraction (FarmingPlugin registers "UseWateringCan"): it waters RadiusX (width, centred) x RadiusZ
   (depth, away from you) tilled soil from the block you look at (soil at y or y-1) by TilledSoilBlock.setWateredUntil(gameTime + Duration s),
   then ticks the soil + the crop above. The vanilla can empties / refills through item STATES (RefillContainer / ModifyInventory BrokenItem)
   which make a NEW stack - our lifelong document would be lost - so our can has no states.
   HOW: GearCanWater extends UseWateringCanInteraction, registered as the interaction type "SkyyGearCan" in setup() the engine's own way
   (getCodecRegistry(Interaction.CODEC).register - what FarmingPlugin does for "UseWateringCan"; BuilderCodec.builder(class, supplier,
   UseWateringCanInteraction.CODEC) = the same JSON keys). Right-click (root SkyyGear_Can_Use: a click, or held = repeated on each new block like the hoe - fix round) runs it:
     - a lifelong can of another profile waters nothing ("Yours: /can"); part.can off = nothing
     - WATER between your eye and the block you look at (or right above it) = REFILL (the bar full; no water used)
     - an empty can (bar at 0) = "empty - right-click water to fill it"
     - else vanilla's own watering with OUR numbers set on the shared interaction for that one call (synchronized: one asset object, many
       world threads): side = can.area by tier (default 1,3,5,7,9,11 = T1 1x1, T2 3x3, T3 5x5, T4 7x7, higher = more), time = can.waterSec
       (86400 game s = vanilla) x Lasting Water. Then, for every soil THIS click made wet that was DRY before (no double dipping): Bloom
       (chance to fertilize = vanilla FertilizeSoilInteraction's setFertilized + ticking) and Growth Boost (the crop above ticks as if X % of
       the water time had passed: FarmingBlock.lastTickGameTime moved back, the engine's own growth math applies it; capped at one water time).
       The water bar goes down by 100 / (can.uses by tier x (1 + Capacity)); Capacity at its top level never runs dry. Nothing watered = no
       water used (vanilla marks the click Failed).
   POINTS (Tools tab, 1 point per Farming level like the other kinds): Capacity (cap, 5 levels: +can.capacityPct % waterings per fill, level 5
   = never runs dry), Growth Boost (grow, 5: can.growPct % of the water time per fresh watering), Lasting Water (last, 5: +can.lastPct %
   wet time), Bloom (bloom, 5: can.bloomPct % fertilize chance per fresh soil). Level = Farming capped by the tier band (like hoe / sickle).
   TIER UP (Tools tab / Upgrade tab / Anvil - GearUp, the same gates: Farming level of the new tier): can.ladders (a NEW row, so no one-time
   update: lifelong.ladders keeps its bytes) Crude > Copper (25 Copper Ingots) > Iron (Enchanted Carrot) > Thorium (Enchanted Cauliflower) >
   Cobalt (2 Enchanted Pumpkin) > Adamantite (2 Enchanted Tomato).
   STARTING KIT: every profile gets its can ONCE (registry canKit=1; the pole kit's code path: a can the registry names counts, a lifelong can
   of this profile is adopted, a plain one carried is marked, else a Crude can is GIVEN through the journalled give - same uid on a retry,
   never two; a give that reached the disk but never the inventory is REDONE once). New profiles: after the four tools + the pole.
   The vanilla Iron Watering Can recipe is refused while can.noVanilla is on (one can per profile, like the tools).
2. THE HARVESTER = the lifelong hoe + sickle merged (Tools tab "Make Harvester" on the hoe / sickle panel; after rebirth 1 when
   harvester.rebirthGate is on - default OFF like multi.rebirthGate "until rebirth is switched on"). Items Tool_Sickle_Harvester_Crude ..
   _Thorium (ids start with Tool_Sickle_ ON PURPOSE: every sickle rule - the swing harvest, GearSickle's plant cut + sweep, the crop tier gate,
   SkyySkills' farming.sickle.items, SkyyTrees' Field Runner - applies unchanged; the hoe's Hoe_Till is its Secondary, GearTill's area works
   for it). Look: the vanilla hoe model of its tier BY PATH + a golden recoloured texture / icon (placeholder - the spec's "our own" model is
   an art round); its animation set = the vanilla Sickle set + the hoe's Till (SkyyGear_Harvester, built at build time).
   The merge (journalled, crash-safe): harv.pend / harv.hoeU / harv.id / harv.doc on disk first -> the hoe leaves -> the SICKLE's slot becomes
   the Harvester (same lifelong uid = the sickle kind's tool; tier = the higher of the two; rarity = the better; lines = both (the best value of
   each sickle-pool line, the rarity's line count); reforge count / name kept; points = the higher level of each perk, trimmed to the points
   you have) -> the registry forgets the hoe (harv=1, harvHoe = its uid). A crash after the hoe left finishes the merge from harv.doc at the
   next look; a crash before changes nothing. After it: /hoe says the hoe is in the Harvester, /harvester (and /sickle) bring it back, rebirth
   resets it to the Crude Harvester, an old hoe that turns up is retired. Ladder harvester.ladders (the hoe's costs).
3. FOLD-INS: (a) a longsword's Ability line says "Crescent Rush" (SkyyArmory 0.1.28's longsword hold, read from armory:blade) instead of
   "Charged Attack 20-28"; (b) Gear's own class -> class skill copy gains Monk -> Zen and Spellblade -> Battlemagic; (c) Raw Health Regen /
   Health Regen % move onto SkyySkills' skill:fn:hpregen (0.4.43: source "SkyyGear", add = HP a second = hpr per regen.periodMs, addpct =
   hprp of the WHOLE regen) - GearFx no longer heals them itself while that bridge exists (no double regen); without SkyySkills the old 2 s
   heal stays.
SAVED DATA: registry keys canKit / canKitAt / canKitHow / canKitUid, can.* (the kind), harv / harvAt / harvHoe, harv.pend / harv.hoeU / harv.id /
harv.doc / harv.at (the journal); per-item documents as every lifelong tool. New Server Setup rows (absent = default; no one-time update):
part.can, lifelong.canKit, can.area, can.uses, can.waterSec, can.capacityPct, can.growPct, can.lastPct, can.bloomPct, can.noVanilla,
can.ladders, part.harvester, harvester.rebirthGate, harvester.ladders.
FIX ROUND (gear0312fix, 2026-10-16): (1) Skyy "the water can currently charges when you click and hold ... id disable that, so you can click and
hold, then as you look around it activates when you look to a new block, like the hoe" -> the can's root is the hoe's shape (Settings + ONE
interaction, repeated while held; no FirstClick / charge); a repeat within GearCan.HOLD_MS (700 ms) on the same block, or over a square with no dry
soil, is skipped (no water); (2) Skyy "rename this craft tab to smithing" -> the Smithing tab; (3) Skyy "so 8 can fit on a page" -> the Upgrade
tab 8 rows a page (70 px rows, 58 px icons); (4) critics: the one-time migration never re-gives a hoe that is in the Harvester and no merge before
migrated=1; an old sickle copy with the Harvester's uid is removed (never the Harvester); the water bar stops at 0.001 (never a 0-durability
tool); Gear heals its regen itself while SkyySkills' hp.regen.enabled is false; a reloaded SkyySkills gets the source again at once.
FIX ROUND 2 (gear0312fix2, 2026-10-16, critics): (A1) "Make Harvester" shows what the merge keeps / loses (rarity, lines kept / lost / lowered, points
that lose a level) and needs a second click within 8 s on the same pair drawn; the result names the lines that did not fit; (A2) the merge sets
sickle.rp=0 / drops sickle.inv (an original sickle that turns up is retired, never restored over the Harvester) and /lifelong refuses a plain sickle
while merged; (B1) GearTill runs the Harvester's till ring only with air above the target soil (a swing at a crop is no till); (B2) GearCan.LAST
is forgotten with the player; (C4) the hold window is the Server Setup row can.holdSec (0.7 s; GearCan.HOLD_MS is a harness seam only).
ROLLBACK 0.3.12 -> 0.3.11: the can items become unknown items (they stay in inventories as unknown stacks until 0.3.12 returns) and the
Harvester the same; a merged profile has no hoe on 0.3.11 (its registry forgot it; 0.3.11 would GIVE a new Crude hoe only through /hoe's
copy path, the Harvester stack is unknown). So: never roll back once players merged; before that it is item-safe except the can.
"""
import os
import ast
import json
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.11.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.12.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.11"' in s and "GENERATED by tools/gear_0_3_11_patch.py" in s and "0.3.12" not in s, "not the generated 0.3.11 script"
assert "GearCanWater" not in s and "Tool_WaterCan_" not in s and "Harvester" not in s
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
if _set is not None and _set.get("SkyyGear") != "0.3.11":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.11" % _set.get("SkyyGear"))

# ---- the vanilla facts this round relies on (the CACHED Assets.zip, read only - nothing is copied into the jar here)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import serverjar
_AZ = zipfile.ZipFile(serverjar.assets_zip())
_AZN = set(_AZ.namelist())


def _azj(path):
    return json.loads(_AZ.read(path).decode("utf-8-sig"))


_WC = _azj("Server/Item/Items/Tool/Watering_Can/Tool_Watering_Can.json")
assert _WC["State"]["Filled_Water"]["Model"] == "Items/Tools/Watering_Can/Watering_Can.blockymodel", "the vanilla full watering can model moved"
_WU = _azj("Server/Item/Interactions/Tools/Watering_Can_Use.json")
assert _WU["Type"] == "UseWateringCan" and _WU["Duration"] == 86400 and _WU["RefreshModifiers"] == ["Water"], "vanilla Watering_Can_Use changed: %s" % _WU
assert _azj("Server/Item/Interactions/Tools/Watering_Can_Fill.json")["States"]["Filled_Water"]["AllowedFluids"] == ["Water_Source", "Water"]
assert _azj("Server/Item/RootInteractions/Weapons/Hoe/Attacks/Till/Hoe_Till.json")["Interactions"] == ["Hoe_Till"]
assert _azj("Server/Item/RootInteractions/Weapons/Sickle/Variants/Sickle_Attack.json")["Interactions"] == ["Sickle_Attack"]
assert sorted(_azj("Server/Item/Animations/Hoe.json")["Animations"]) == ["SwingLeft", "SwingRight", "Till"]
assert "Till" not in _azj("Server/Item/Animations/Sickle.json")["Animations"]
print("0.3.12 vanilla: Tool_Watering_Can (full model, Watering_Can_Use 86400 s, refill from Water / Water_Source), Hoe_Till + Sickle_Attack roots")

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.11 - build script (javassist via jpype). GENERATED by tools/gear_0_3_11_patch.py from the LIVE 0.3.10 (itself GENERATED by
tools/gear_0_3_10_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.11.py -> SkyyGear/SkyyGear-0.3.11.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.11.py
''', '''"""SkyyGear 0.3.12 - build script (javassist via jpype). GENERATED by tools/gear_0_3_12_patch.py from the LIVE 0.3.11 (itself GENERATED by
tools/gear_0_3_11_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.12.py -> SkyyGear/SkyyGear-0.3.12.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.12.py

0.3.12 = THE LIFELONG WATERING CAN + THE HARVESTER (notes: tools/gear_0_3_12_patch.py): every profile gets a lifelong watering can (/can; T1
Crude .. T6 Adamantite; the tier waters a bigger square; points Capacity / Growth Boost / Lasting Water / Bloom; right-click water to refill);
the lifelong hoe + sickle merge into one Harvester on the Tools tab (tills and reaps; /harvester); a longsword's ability reads Crescent Rush;
Gear's Health regen goes through SkyySkills' skill:fn:hpregen.

--- 0.3.11 notes ---
''')
rep('VERSION = "0.3.11"\n', 'VERSION = "0.3.12"\n')

# ================================================================================================================ 1 + 2: the items (build time)
after('''print("0.3.4 sigils: %d items (%s), approved icons + tinted rune texture, %d files" % (len(SIG_IDS), ", ".join(SIG_IDS), len(SIG_FILES)))
''', r'''
# ================================================================= 0.3.12 THE LIFELONG WATERING CAN + THE HARVESTER (tools/gear_0_3_12_patch.py): the items, made here
# from Assets.zip (vanilla models BY PATH; recoloured copies of vanilla textures / icons generated now - nothing vanilla is committed)
import tier_tags as TT
CAN_TIERS = list(TT.CAN_TIERS)                     # Crude .. Adamantite (the pickaxe ladder's reach; Mithril / Onyxium wait for Enchanted items)
CAN_IDS = ["Tool_WaterCan_" + _t for _t in CAN_TIERS]
HARV_TIERS = list(TT.HARVESTER_TIERS)              # Crude .. Thorium (the hoe ladder's reach)
HARV_PRE = "Tool_Sickle_Harvester_"
HARV_IDS = [HARV_PRE + _t for _t in HARV_TIERS]
assert CAN_TIERS == ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite"] and HARV_TIERS == ["Crude", "Copper", "Iron", "Thorium"]
for _i in CAN_IDS + HARV_IDS:
    assert _i not in AZ_ITEMS, "0.3.12: %s is a vanilla id now - pick another" % _i
    assert TT.tag_for(_i) is not None and TT.owner(_i) == "SkyyGear", _i
_wcj = json.loads(AZ.read("Server/Item/Items/Tool/Watering_Can/Tool_Watering_Can.json").decode("utf-8-sig"))
_wcf = _wcj["State"]["Filled_Water"]
CAN_MODEL = _wcf["Model"]
CAN_TEX_SRC = _wcf["Texture"]
CAN_ICON_SRC = _wcf["Icon"]
for _p in (CAN_MODEL, CAN_TEX_SRC, CAN_ICON_SRC):
    assert ("Common/" + _p) in AZ_NAMES, "the watering can source is gone from Assets.zip: " + _p
CAN_RAMP = {"Crude": ("#3e2612", "#7f5530", "#c89a62"), "Copper": ("#5c2a10", "#b8682e", "#f2a86a"), "Iron": None,
            "Thorium": ("#26401f", "#5c8a48", "#b2dc94"), "Cobalt": ("#16285e", "#3a5ec0", "#9cbcff"),
            "Adamantite": ("#561212", "#aa3838", "#ff9e8c")}          # Iron = the vanilla can's own look (it IS the iron can)
CAN_MAXDUR = 100                                                       # the water bar (can.uses decides how many waterings fill it)
CAN_FILES = {}
CAN_ITEMS = {}
_ctex, _cico = AZ.read("Common/" + CAN_TEX_SRC), AZ.read("Common/" + CAN_ICON_SRC)
_wus = json.loads(AZ.read("Server/Item/Interactions/Tools/Watering_Can_Use.json").decode("utf-8-sig"))
_wur = json.loads(AZ.read("Server/Item/RootInteractions/Tools/Watering_Can_Use.json").decode("utf-8-sig"))
for _t, _cid in zip(CAN_TIERS, CAN_IDS):
    if CAN_RAMP[_t] is None:
        _tex, _ico = CAN_TEX_SRC, CAN_ICON_SRC
    else:
        _tex = "Items/SkyyGear/Can/Can_%s.png" % _t
        _ico = "Icons/ItemsGenerated/%s.png" % _cid
        CAN_FILES["Common/" + _tex] = SA.recolor(_ctex, _ramp(CAN_RAMP[_t]), rank=0.4)
        CAN_FILES["Common/" + _ico] = SA.recolor_icon(_cico, _ramp(CAN_RAMP[_t]), rank=0.4)
    CAN_ITEMS["Server/Item/Items/SkyyGear/%s.json" % _cid] = json.dumps({
        "TranslationProperties": {"Name": "server.items.%s.name" % _cid, "Description": "server.items.%s.description" % _cid},
        "Categories": ["Items.Tools"], "Quality": "Common", "MaxStack": 1, "Tool": {}, "PlayerAnimationsId": "Watering_Can",
        "IconProperties": _wcf["IconProperties"], "Icon": _ico, "Model": CAN_MODEL, "Texture": _tex, "Scale": _wcf.get("Scale", 1),
        "Interactions": {"Primary": {"RequireNewClick": True, "Interactions": [{"Type": "Simple"}]}, "Secondary": "SkyyGear_Can_Use"},
        "MaxDurability": CAN_MAXDUR, "DurabilityLossOnDeath": False, "Repairable": False,
        "Tags": {"Type": ["Tool"]}, "ItemSoundSetId": _wcj.get("ItemSoundSetId", "ISS_Weapons_Wood")}, indent=2)
# the interaction (our type SkyyGearCan = vanilla UseWateringCan's keys; our code sets the area / time per click) + its root (the hoe's shape: repeated while held - fix round)
CAN_INT_ID, CAN_ROOT_ID = "SkyyGear_Can_Water", "SkyyGear_Can_Use"
CAN_FILES["Server/Item/Interactions/SkyyGear/Can/%s.json" % CAN_INT_ID] = json.dumps({
    "Type": "SkyyGearCan", "UseLatestTarget": True, "Duration": _wus["Duration"], "RadiusX": 1, "RadiusZ": 1,
    "RefreshModifiers": _wus["RefreshModifiers"], "Effects": _wus["Effects"], "Failed": _wus["Failed"], "RunTime": _wus["RunTime"],
    "OnItemChangeBehavior": _wus["OnItemChangeBehavior"]}, indent=2)
# FIX ROUND (Skyy 2026-10-16 "id disable that, so you can click and hold, then as you look around it activates when you look to a new block, like
# the hoe"): NO charge / FirstClick - the root is the hoe's own shape (vanilla Hoe_Till: Settings + ONE interaction, repeated while the button is
# held, each run on the block you look at NOW - UseLatestTarget); GearCan.before skips a repeat on the same block / an all-wet square (no water)
_htr = json.loads(AZ.read("Server/Item/RootInteractions/Weapons/Hoe/Attacks/Till/Hoe_Till.json").decode("utf-8-sig"))
assert _htr["Interactions"] == ["Hoe_Till"] and "Settings" in _htr, "vanilla's Hoe_Till root changed shape - re-check the can's hold-and-sweep"
assert _wur["Interactions"][0]["Type"] == "FirstClick" and _wur["Interactions"][0]["Click"]["Next"] == "Watering_Can_Use"
CAN_FILES["Server/Item/RootInteractions/SkyyGear/%s.json" % CAN_ROOT_ID] = json.dumps({
    "Settings": _wur["Settings"], "Interactions": [CAN_INT_ID]}, indent=2)
# THE HARVESTER: the sickle of its tier as Parent (its swing + harvest + Weapon section), the hoe's Hoe_Till as Secondary, the hoe model of its
# tier BY PATH with a golden copy of its texture + icon, an animation set = vanilla Sickle + the hoe's Till
HARV_BASE = {"Crude": "Tool_Sickle_Crude", "Copper": "Tool_Sickle_Copper", "Iron": "Tool_Sickle_Iron", "Thorium": "Tool_Sickle_Iron"}
HARV_RAMP = {"Crude": ("#4a3410", "#9c7a2a", "#e8cc78"), "Copper": ("#5a2a10", "#c0783a", "#ffd090"),
             "Iron": ("#4a4a3a", "#b8b08a", "#fff4c8"), "Thorium": ("#2e4a1e", "#7aa04a", "#e4f0a0")}
HARV_ANIM = "SkyyGear_Harvester"
_sanim = json.loads(AZ.read("Server/Item/Animations/Sickle.json").decode("utf-8-sig"))
_hanim = json.loads(AZ.read("Server/Item/Animations/Hoe.json").decode("utf-8-sig"))
_hv_anim = json.loads(json.dumps(_sanim))
_hv_anim["Animations"]["Till"] = _hanim["Animations"]["Till"]
CAN_FILES["Server/Item/Animations/SkyyGear/%s.json" % HARV_ANIM] = json.dumps(_hv_anim, indent=2)
HARV_ITEMS = {}
for _t, _hid in zip(HARV_TIERS, HARV_IDS):
    _hoe = "Tool_Hoe_" + _t
    _sic = HARV_BASE[_t]
    for _x in (_hoe, _sic):
        assert _x in AZ_ITEMS, _x
    _hm, _ht, _hi = az_get(_hoe, "Model"), az_get(_hoe, "Texture"), az_get(_hoe, "Icon")
    for _p in (_hm, _ht, _hi):
        assert ("Common/" + _p) in AZ_NAMES, "the hoe look of the Harvester is gone: " + _p
    _prim = az_get(_sic, "Interactions")["Primary"]
    assert _prim in ("Sickle_Attack", {"Parent": "Sickle_Attack"}), _prim
    _tex = "Items/SkyyGear/Harvester/Harvester_%s.png" % _t
    _ico = "Icons/ItemsGenerated/%s.png" % _hid
    CAN_FILES["Common/" + _tex] = SA.recolor(AZ.read("Common/" + _ht), _ramp(HARV_RAMP[_t]), rank=0.4)
    CAN_FILES["Common/" + _ico] = SA.recolor_icon(AZ.read("Common/" + _hi), _ramp(HARV_RAMP[_t]), rank=0.4)
    HARV_ITEMS["Server/Item/Items/SkyyGear/%s.json" % _hid] = json.dumps({
        "Parent": _sic,
        "TranslationProperties": {"Name": "server.items.%s.name" % _hid, "Description": "server.items.%s.description" % _hid},
        "PlayerAnimationsId": HARV_ANIM, "Model": _hm, "Texture": _tex, "Icon": _ico, "IconProperties": az_get(_hoe, "IconProperties"),
        "Quality": az_get(_hoe, "Quality") or "Common",
        "MaxDurability": max(int(az_get(_hoe, "MaxDurability") or 100), int(az_get(_sic, "MaxDurability") or 100)),
        "Interactions": {"Primary": _prim, "Secondary": "Hoe_Till"},
        "InteractionConfig": dict(az_get("Tool_Hoe_Crude", "InteractionConfig"), UseDistance={"Adventure": 5, "Creative": 6}), "MaxStack": 1}, indent=2)
    # (no "Recipe" key: the engine's Item codec reads Recipe with append, NOT appendInherited - VERIFIED by the 0.2.16 bytecode check above - so
    # the sickle Parent's Farming Bench recipe is NOT inherited; fix round: asserted, critic 1.3)
    assert "Recipe" not in json.loads(HARV_ITEMS["Server/Item/Items/SkyyGear/%s.json" % _hid])
    # (the hoe's main-hand priority for the till; with a Parent the config inherits field by field from the sickle's NONE - so the engine's own
    # defaults are written out: UseDistance Adventure 5 / Creative 6 = InteractionConfiguration's constants, VERIFIED bytecode 2026-10-16)
assert az_get("Tool_Hoe_Crude", "InteractionConfig") == {"Priorities": {"Secondary": {"MainHand": 1}}}
for _k in list(CAN_FILES) + list(CAN_ITEMS) + list(HARV_ITEMS):
    assert _k not in AZ_NAMES, "a 0.3.12 file would shadow a vanilla file: " + _k
for _k, _v in CAN_FILES.items():
    if _k.endswith(".png"):
        _w, _h = SA.png_size(_v)
        assert _w > 0 and _h > 0, _k
CAN_LANG = []
for _t, _cid in zip(CAN_TIERS, CAN_IDS):
    CAN_LANG.append("items.%s.name = %s Watering Can" % (_cid, _t))
    CAN_LANG.append("items.%s.description = %s" % (_cid, TT.described(_cid, "Your lifelong watering can. Hold right-click and look across tilled soil to water it, right-click water to refill. A higher tier waters a bigger square.")))
for _t, _hid in zip(HARV_TIERS, HARV_IDS):
    CAN_LANG.append("items.%s.name = %s Harvester" % (_hid, _t))
    CAN_LANG.append("items.%s.description = %s" % (_hid, TT.described(_hid, "Your lifelong hoe and sickle in one: right-click tills soil, a swing reaps crops and cuts plants.")))
EXTRA.update(CAN_FILES)
EXTRA.update(CAN_ITEMS)
EXTRA.update(HARV_ITEMS)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\n".join(CAN_LANG) + "\n"
print("0.3.12 items: %d watering cans (%s), %d Harvesters, interaction %s / root %s, %d files"
      % (len(CAN_IDS), ", ".join(CAN_TIERS), len(HARV_IDS), CAN_INT_ID, CAN_ROOT_ID, len(CAN_FILES)))
''')

# ================================================================================================================ 3b: Monk + Spellblade class skills
rep('''CLASS_SKILLS = [("Archer", "Archery"), ("Warrior", "Swordsmanship"), ("Mage", "Sorcery"), ("Berserker", "Fury"),
                ("Priest", "Divinity"), ("Assassin", "Assassination")]''',
    '''CLASS_SKILLS = [("Archer", "Archery"), ("Warrior", "Swordsmanship"), ("Mage", "Sorcery"), ("Berserker", "Fury"),
                ("Priest", "Divinity"), ("Assassin", "Assassination"),
                ("Monk", "Zen"), ("Spellblade", "Battlemagic")]          # 0.3.12: SkyySkills 0.4.43's CLASS_ROWS (Monk = Zen, Spellblade = Battlemagic)''')

# ================================================================================================================ 4: Server Setup rows
before("CFG_ROWS = [\n", r"""# 0.3.12 (tools/gear_0_3_12_patch.py): the watering can + Harvester defaults
CAN_AREA_DEF = "1,3,5,7,9,11"                  # T1 1x1, T2 3x3, T3 5x5, T4 7x7 (Skyy's popup), higher = more
CAN_USES_DEF = "20,30,40,60,80,100"            # waterings per fill by tier (the vanilla iron can holds 50)
CAN_SEC_DEF = 86400                            # vanilla Watering_Can_Use Duration (game seconds)
CAN_LAD_DEF = ("Tool_WaterCan_Crude>Tool_WaterCan_Copper(Ingredient_Bar_Copper*25)>Tool_WaterCan_Iron(Skyy_Ench_Carrot*1)"
               ">Tool_WaterCan_Thorium(Skyy_Ench_Cauliflower*1)>Tool_WaterCan_Cobalt(Skyy_Ench_Pumpkin*2)>Tool_WaterCan_Adamantite(Skyy_Ench_Tomato*2)")
HARV_LAD_DEF = ("Tool_Sickle_Harvester_Crude>Tool_Sickle_Harvester_Copper(Ingredient_Bar_Copper*25)>Tool_Sickle_Harvester_Iron(Skyy_Ench_Carrot*1)"
                ">Tool_Sickle_Harvester_Thorium(Skyy_Ench_Cauliflower*1)")
for _l in (CAN_LAD_DEF, HARV_LAD_DEF):
    assert len(_l) < 2000 and all(32 <= ord(_c) < 127 for _c in _l)
    for _i in re.findall(r"\(([A-Za-z_]+)\*", _l):
        assert _i in AZ_ITEMS or _i in ENCH.IDS, "0.3.12 ladder material %s is no item" % _i
assert [_x.split("(")[0] for _x in CAN_LAD_DEF.split(">")] == CAN_IDS and [_x.split("(")[0] for _x in HARV_LAD_DEF.split(">")] == HARV_IDS
""")
after('''    ("smith.upgradeTab", "Upgrade tab", "smithing", "bool", "true", "", "", "", "", "live",
     "Smithing tab with every item you carry that can tier up (/upgrade). Off = /upgrade opens the Anvil.", "field:GearCfg.UPG_TAB"),
''', '''    # 0.3.12 THE LIFELONG WATERING CAN + THE HARVESTER (tools/gear_0_3_12_patch.py)
    ("part.can", "Lifelong watering can", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = the lifelong watering can waters by its tier and upgrades. Off = it does nothing.", "field:GearCfg.CAN_ON"),
    ("lifelong.canKit", "Watering can in the starting kit", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "Every profile gets its lifelong watering can once, like the pickaxe. Off = no can is handed out.", "field:GearCfg.CAN_KIT"),
    ("can.area", "Watering square per can tier", "lifelong", "text", CAN_AREA_DEF, "1", "60", "", "", "live,danger",
     "Side of the square, Crude to Adamantite: 6 odd numbers 1-15, joined by commas.", "field:GearCfg.CAN_AREA;check=GearCan.checkArea"),
    ("can.uses", "Waterings per fill per can tier", "lifelong", "text", CAN_USES_DEF, "1", "60", "", "", "live,danger",
     "Crude to Adamantite: 6 numbers 1-1000, joined by commas. Right-click water refills.", "field:GearCfg.CAN_USES;check=GearCan.checkUses"),
    ("can.waterSec", "Soil stays wet", "lifelong", "int", str(CAN_SEC_DEF), "60", "2592000", "", "s", "live",
     "Game seconds watered soil stays wet (vanilla 86400 = one game day). Lasting Water adds to it.", "field:GearCfg.CAN_SEC"),
    ("can.holdSec", "Hold-to-water repeat window", "lifelong", "dec", "0.7", "0.2", "3", "", "s", "live",
     "Holding right-click: repeats this close together are one press (the same block is skipped).", "field:GearCfg.CAN_HOLD"),
    ("can.capacityPct", "Capacity: more waterings", "lifelong", "dec", "20", "0", "500", "", "%", "live,danger",
     "Per Capacity level: this % more waterings per fill. The top level never runs dry.", "field:GearCfg.CAN_CAPP"),
    ("can.growPct", "Growth Boost per level", "lifelong", "dec", "4", "0", "50", "", "%", "live,danger",
     "Per level: a crop on dry soil you water grows as if this % of the wet time passed.", "field:GearCfg.CAN_GROW"),
    ("can.lastPct", "Lasting Water per level", "lifelong", "dec", "20", "0", "500", "", "%", "live",
     "Per level: soil you water stays wet this % longer.", "field:GearCfg.CAN_LAST"),
    ("can.bloomPct", "Bloom per level", "lifelong", "dec", "6", "0", "50", "", "%", "live,danger",
     "Per level: chance a dry soil you water is fertilized too (vanilla fertilizer).", "field:GearCfg.CAN_BLOOM"),
    ("can.noVanilla", "No vanilla watering can recipe", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = the vanilla Iron Watering Can can't be crafted (everyone has a lifelong one).", "field:GearCfg.CAN_NOVAN"),
    ("can.ladders", "Watering can tier-up costs", "lifelong", "text", CAN_LAD_DEF, "0", "2000", "", "", "live,danger",
     "Can tiers on the Anvil, like lifelong.ladders: A>B(Id*25), ladders joined by commas.", "field:GearCfg.CAN_LADDERS;check=GearUp.checkLadders"),
    ("part.harvester", "Harvester (hoe + sickle)", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = the Tools tab merges your lifelong hoe and sickle into one Harvester. Off = no new merges.", "field:GearCfg.HARV_ON"),
    ("harvester.rebirthGate", "Harvester after rebirth 1", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "On = the Harvester opens after your first rebirth (like multi.rebirthGate). Off = always.", "field:GearCfg.HARV_RBGATE"),
    ("harvester.ladders", "Harvester tier-up costs", "lifelong", "text", HARV_LAD_DEF, "0", "2000", "", "", "live,danger",
     "Harvester tiers on the Anvil, like lifelong.ladders: A>B(Id*25), ladders joined by commas.", "field:GearCfg.HARV_LADDERS;check=GearUp.checkLadders"),
''')
rep('''           "sticks.keepPct", "sticks.lists", "lifelong.poleKit"}''', '''           "sticks.keepPct", "sticks.lists", "lifelong.poleKit",
           # 0.3.12: the watering can (item supply, crop speed, fertilizer = economy) + the Harvester (a lifelong merge)
           "part.can", "lifelong.canKit", "can.area", "can.uses", "can.capacityPct", "can.growPct", "can.bloomPct", "can.noVanilla", "can.ladders",
           "part.harvester", "harvester.rebirthGate", "harvester.ladders"}''')
after('''assert all(32 <= ord(_c) < 127 for _c in G311_HEAD) and "=" not in G311_HEAD
''', '''G312_HEAD = "# ---- the lifelong watering can, the Harvester (SkyyGear 0.3.12) ----"
G312_ROWK = ["part.can", "lifelong.canKit", "can.area", "can.uses", "can.waterSec", "can.holdSec", "can.capacityPct", "can.growPct", "can.lastPct", "can.bloomPct",
             "can.noVanilla", "can.ladders", "part.harvester", "harvester.rebirthGate", "harvester.ladders"]
assert all(32 <= ord(_c) < 127 for _c in G312_HEAD) and "=" not in G312_HEAD
''')
after('''    L += ["", G311_HEAD]        # 0.3.11: the new rows (no one-time update adds them; absent = the default)
    for k in G311_ROWK:
        scal(k)
''', '''    L += ["", G312_HEAD]        # 0.3.12: the new rows (no one-time update adds them; absent = the default)
    for k in G312_ROWK:
        scal(k)
''')
rep('''              ("UPG_TAB", "boolean", "true")]''', '''              ("UPG_TAB", "boolean", "true"),
              # 0.3.12 the watering can + the Harvester
              ("CAN_ON", "boolean", "true"), ("CAN_KIT", "boolean", "true"), ("CAN_AREA", "String", jstr(CAN_AREA_DEF)),
              ("CAN_USES", "String", jstr(CAN_USES_DEF)), ("CAN_SEC", "int", str(CAN_SEC_DEF)), ("CAN_HOLD", "double", "0.7"), ("CAN_CAPP", "double", "20.0"),
              ("CAN_GROW", "double", "4.0"), ("CAN_LAST", "double", "20.0"), ("CAN_BLOOM", "double", "6.0"), ("CAN_NOVAN", "boolean", "true"),
              ("CAN_LADDERS", "String", jstr(CAN_LAD_DEF)), ("HARV_ON", "boolean", "true"), ("HARV_RBGATE", "boolean", "false"),
              ("HARV_LADDERS", "String", jstr(HARV_LAD_DEF))]''')
after('''  UPG_TAB = pbool(p, "smith.upgradeTab", true);
''', '''  CAN_ON = pbool(p, "part.can", true);          // 0.3.12
  CAN_KIT = pbool(p, "lifelong.canKit", true) && !Boolean.getBoolean("skyy.harness.noCanKit");          // HARNESS SEAM ONLY: the older harness children run 0.3.11's flow
  CAN_AREA = ptext(p, "can.area", "%s").trim();
  CAN_USES = ptext(p, "can.uses", "%s").trim();
  CAN_SEC = (int) plong(p, "can.waterSec", %dL, 60L, 2592000L);
  CAN_HOLD = pdec(p, "can.holdSec", 0.7, 0.2, 3.0);          // fix round 2 (critic C4)
  CAN_CAPP = pdec(p, "can.capacityPct", 20.0, 0.0, 500.0);
  CAN_GROW = pdec(p, "can.growPct", 4.0, 0.0, 50.0);
  CAN_LAST = pdec(p, "can.lastPct", 20.0, 0.0, 500.0);
  CAN_BLOOM = pdec(p, "can.bloomPct", 6.0, 0.0, 50.0);
  CAN_NOVAN = pbool(p, "can.noVanilla", true);
  CAN_LADDERS = ptext(p, "can.ladders", "%s").trim();
  HARV_ON = pbool(p, "part.harvester", true);
  HARV_RBGATE = pbool(p, "harvester.rebirthGate", false);
  HARV_LADDERS = ptext(p, "harvester.ladders", "%s").trim();
''' % ("1,3,5,7,9,11", "20,30,40,60,80,100", 86400,
       "Tool_WaterCan_Crude>Tool_WaterCan_Copper(Ingredient_Bar_Copper*25)>Tool_WaterCan_Iron(Skyy_Ench_Carrot*1)>Tool_WaterCan_Thorium(Skyy_Ench_Cauliflower*1)>Tool_WaterCan_Cobalt(Skyy_Ench_Pumpkin*2)>Tool_WaterCan_Adamantite(Skyy_Ench_Tomato*2)",
       "Tool_Sickle_Harvester_Crude>Tool_Sickle_Harvester_Copper(Ingredient_Bar_Copper*25)>Tool_Sickle_Harvester_Iron(Skyy_Ench_Carrot*1)>Tool_Sickle_Harvester_Thorium(Skyy_Ench_Cauliflower*1)"))

# ================================================================================================================ 5: the kind "can" + the Harvester helpers
after(r'''M(gdt, "public static boolean pole(String id) { return id != null && id.startsWith(\"SkyyFishing_Rod_\"); }")
''', r'''# 0.3.12: a lifelong watering can of ours (Tool_WaterCan_<Tier>; vanilla's Tool_Watering_Can is no lifelong kind)
M(gdt, "public static boolean can(String id) { return id != null && id.startsWith(\"Tool_WaterCan_\"); }")
''')
rep('''assert len(LL_KIND) == len(LL_KNAME) == len(LL_KFAM) == len(LL_KSKILL) == len(LL_KCRUDE) == 5 and 9 not in LL_KFAM[:4]
''', '''assert len(LL_KIND) == len(LL_KNAME) == len(LL_KFAM) == len(LL_KSKILL) == len(LL_KCRUDE) == 5 and 9 not in LL_KFAM[:4]
# 0.3.12 THE WATERING CAN = the 6th lifelong kind (tools/gear_0_3_12_patch.py 1): our Tool_WaterCan_<Tier> items; family 10 is no GearTool family
# (kOf answers CAN by the id prefix - a can never hits with tool power); levels with Farming like the hoe / sickle
LL_CAN = 5
LL_KIND.append("can")
LL_KNAME.append("Watering Can")
LL_KFAM.append(10)
LL_KSKILL.append("Farming")
LL_KCRUDE.append(CAN_IDS[0])
assert len(LL_KIND) == 6 and LL_KIND.index("can") == LL_CAN and LL_KCRUDE[LL_CAN] == "Tool_WaterCan_Crude"
''')
rep('LL_RBNODE = ["Mining", "Foraging", "Farming", "Farming", "Fishing"]\n',
    'LL_RBNODE = ["Mining", "Foraging", "Farming", "Farming", "Fishing", "Farming"]          # 0.3.12: + the can (the Farming arm)\n')
rep('''LL_KLAD.append(LL_POLE_LAD)          # 0.3.5
''', '''LL_KLAD.append(LL_POLE_LAD)          # 0.3.5
LL_KLAD.append(",".join(CAN_IDS))          # 0.3.12: the can's ladder (its costs: can.ladders)
assert len(LL_KLAD) == len(LL_KIND)
''')
after('''F(gll, "public static final int POLE = %d;" % LL_POLE)          # 0.3.5
''', '''F(gll, "public static final int CAN = %d;" % LL_CAN)          # 0.3.12
F(gll, "public static final String HARV_PRE = %s;" % jstr(HARV_PRE))          # 0.3.12: the Harvester ids (the sickle kind's tool after the merge)
F(gll, "public static final String HARV_LAD = %s;" % jstr(",".join(HARV_IDS)))
''')
# 0.3.12 POINTS of the can (Skyy's popup: "Capacity / refill,Growth boost,Lasting water,Bloom (fertilize chance)"): mask bit 1 << CAN = 32
before('''for _p in LL_PERKS:
    assert len(_p[4]) == _p[2] == len(_p[5])
''', '''LL_PERKS += [("cap", "Capacity", 5, 1 << 5, [1, 1, 2, 2, 3], [0] * 5),          # 0.3.12: the watering can (kind 5)
             ("grow", "Growth Boost", 5, 1 << 5, [1, 2, 2, 3, 3], [0] * 5),
             ("last", "Lasting Water", 5, 1 << 5, [1, 1, 1, 2, 2], [0] * 5),
             ("bloom", "Bloom", 5, 1 << 5, [1, 2, 2, 3, 3], [0] * 5)]
assert [_p[0] for _p in LL_PERKS[:6]] == ["spd", "fort", "wis", "vein", "fell", "steady"], "the old perk order moved (saved keys are by name, the UI by index)"
''')
after('''F(gll, "public static final int PK_STEADY = %d;" % [_p[0] for _p in LL_PERKS].index("steady"))          # 0.3.6 the pole's Steady Line
''', '''for _pn in ("cap", "grow", "last", "bloom"):          # 0.3.12 the watering can's points
    F(gll, "public static final int PK_%s = %d;" % (_pn.upper(), [_p[0] for _p in LL_PERKS].index(_pn)))
''')
rep('''M(gll, "public static int kOf(String id) { return id == null ? -1 : (@PKG@.GearData.pole(id) ? POLE : kOfFam(@PKG@.GearData.toolFam(id))); }")          # 0.3.5: + the pole''',
    '''M(gll, "public static int kOf(String id) { return id == null ? -1 : (@PKG@.GearData.pole(id) ? POLE : (@PKG@.GearData.can(id) ? CAN : kOfFam(@PKG@.GearData.toolFam(id)))); }")          # 0.3.5: + the pole; 0.3.12: + the can''')
after('''M(gll, "public static boolean isPole(String id) { return @PKG@.GearData.pole(id); }")
''', r'''# 0.3.12 THE HARVESTER: its ids start with Tool_Sickle_ (the sickle kind - every sickle rule applies); after the merge the sickle kind's tool is
# a Harvester and the hoe kind is gone from the registry (harv=1). The Crude id / ladder / name of kind k for the item id it has now
M(gll, "public static boolean harv(String id) { return id != null && id.startsWith(HARV_PRE); }")
M(gll, "public static boolean merged(java.util.Properties P) { return P != null && \"1\".equals(P.getProperty(\"harv\")); }")
M(gll, r"""
public static String crudeOf(int k, String id) {
  if (k == 3 && harv(id)) return HARV_PRE + "Crude";
  return k >= 0 && k < KCRUDE.length ? KCRUDE[k] : KCRUDE[0];
}""")
M(gll, r"""
public static String ladOf(int k, String id) {
  if (k == 3 && harv(id)) return HARV_LAD;
  return k >= 0 && k < KLAD.length ? KLAD[k] : "";
}""")
M(gll, r"""
public static String kname(int k, String id) {
  if (k == 3 && harv(id)) return "Harvester";
  return k >= 0 && k < KNAME.length ? KNAME[k] : "tool";
}""")
''')
rep('''  if (k != POLE) return perkOn(p);''', '''  if (k == CAN) return true;          // 0.3.12: the watering can's own points work at once (Gear reads them itself)
  if (k != POLE) return perkOn(p);''')
rep('''  String[] ids = KLAD[k].split(",");''', '''  String[] ids = ladOf(k, had).split(",");          // 0.3.12: a Harvester keeps the Harvester ladder''')
rep('''  String r = fit != null ? fit : (hi != null ? hi : KCRUDE[k]);''', '''  String r = fit != null ? fit : (hi != null ? hi : crudeOf(k, had));''')
rep('''  txt.add("Lifelong " + KIND[k] + ": levels with " + KSKILL[k] + " (max Lv " + cap(id) + ")");''',
    '''  txt.add("Lifelong " + kname(k, id).toLowerCase() + ": levels with " + KSKILL[k] + " (max Lv " + cap(id) + ")");          // 0.3.12: "watering can", "harvester"''')
rep('''  txt.add("Can't be dropped. Lost it? /" + KIND[k]);''', '''  txt.add("Can't be dropped. Lost it? /" + (harv(id) ? "harvester" : KIND[k]));''')
after('''  if (@PKG@.GearCfg.LL_ON && b.trim().length() > 0) r = r.trim().length() == 0 ? b : r + "," + b;
''', '''  // 0.3.12: + the watering can ladder and the Harvester ladder (their own rows: lifelong.ladders keeps its bytes - no one-time update)
  String cl = @PKG@.GearCfg.CAN_LADDERS == null ? "" : @PKG@.GearCfg.CAN_LADDERS.trim();
  String hl = @PKG@.GearCfg.HARV_LADDERS == null ? "" : @PKG@.GearCfg.HARV_LADDERS.trim();
  if (@PKG@.GearCfg.LL_ON && cl.length() > 0) r = r.trim().length() == 0 ? cl : r + "," + cl;
  if (@PKG@.GearCfg.LL_ON && hl.length() > 0) r = r.trim().length() == 0 ? hl : r + "," + hl;
''')
rep(r'''M(gll, "public static boolean noCraft(String id) { return @PKG@.GearCfg.LL_ON && @PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0; }")''',
    r'''M(gll, "public static boolean noCraft(String id) { return @PKG@.GearCfg.LL_ON && ((@PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0) || (@PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_NOVAN && \"Tool_Watering_Can\".equals(id))); }")          # 0.3.12: + the vanilla can (can.noVanilla)''')
rep('''        int k0 = @PKG@.GearLL.kOf(id0);
''', '''        int k0 = @PKG@.GearLL.kOf(id0);
        if (k0 < 0) k0 = @PKG@.GearLL.CAN;          // 0.3.12: the vanilla Iron Watering Can (can.noVanilla) -> "one can for life ... /can"
''')

# ---- GearCan (1/2, early: before GearTool, which shows its tooltip lines): the settings, the plan of one watering, the tooltip
before('''gtool = mk("GearTool")
TOOL_CLASSES = [gtool]
''', r'''# 0.3.12 GearCan (1/2): the lifelong watering can's numbers (tools/gear_0_3_12_patch.py 1). 2/2 (the click: before / after the vanilla watering,
# the soil, the refill) sits near the plugin; GearCanWater (the interaction type) after it.
gcan = mk("GearCan")
G312_CLASSES = [gcan]
F(gcan, "public static final long[] N = new long[12];")          # 0 clicks, 1 refills, 2 empty, 3 not yours, 4 soils watered dry, 5 bloomed, 6 grown, 7 never-dry clicks, 8 nothing watered, 9 off, 10 hold: same block skipped, 11 hold: all wet skipped
# fix round (Skyy 2026-10-16 hold-and-sweep): UUID -> long[] { x, y, z, ms } of the last block a click ran on; a run within HOLD_MS of the last
# one = the button is still held (the root repeats like the hoe's): the same block again = skipped, a square with no dry soil = skipped (no water)
F(gcan, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(gcan, "public static volatile long HOLD_MS = -1L;")          # fix round 2: HARNESS SEAM ONLY (>= 0 overrides); the game reads can.holdSec
M(gcan, "public static long holdMs() { long h = HOLD_MS; return h >= 0L ? h : (long) (@PKG@.GearCfg.CAN_HOLD * 1000.0); }")
# fix round (critic 1, UNVERIFIED 0-durability): the water bar never reaches 0 (a 0-durability tool may count as broken to the client) - it
# stops at EMPTY; below EMPTY_AT the can is empty
F(gcan, "public static final double EMPTY = 0.001;")
F(gcan, "public static final double EMPTY_AT = 0.01;")
F(gcan, "public static volatile String AREA_SRC = null;")
F(gcan, "public static volatile int[] AREA = new int[] { 1, 3, 5, 7, 9, 11 };")
F(gcan, "public static volatile String USES_SRC = null;")
F(gcan, "public static volatile int[] USES = new int[] { 20, 30, 40, 60, 80, 100 };")
F(gcan, "public static volatile boolean REG = false;")          # the interaction type SkyyGearCan was registered in setup()
F(gcan, "public static volatile String REG_WHY = \"not registered yet\";")
M(gcan, r"""
public static int[] parseNums(String v, int lo, int hi, boolean odd) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length != 6) return null;
  int[] a = new int[6];
  for (int i = 0; i < 6; i++) {
    try { a[i] = Integer.parseInt(p[i].trim()); } catch (Throwable t) { return null; }
    if (a[i] < lo || a[i] > hi || (odd && a[i] % 2 == 0)) return null;
  }
  return a;
}""")
M(gcan, r"""
public static String checkArea(String key, String value) {
  return parseNums(value, 1, 15, true) == null ? "Watering square per can tier: 6 odd numbers from 1 to 15 (Crude, Copper, Iron, Thorium, Cobalt, Adamantite), joined by commas." : null;
}""")
M(gcan, r"""
public static String checkUses(String key, String value) {
  return parseNums(value, 1, 1000, false) == null ? "Waterings per fill per can tier: 6 numbers from 1 to 1000 (Crude, Copper, Iron, Thorium, Cobalt, Adamantite), joined by commas." : null;
}""")
M(gcan, r"""
public static int side(int tier) {
  String v = @PKG@.GearCfg.CAN_AREA;
  if (v != null && !v.equals(AREA_SRC)) {
    int[] a = parseNums(v, 1, 15, true);
    if (a == null) @PKG@.Gear.warnOnce("canarea:" + v.hashCode(), "config.properties: can.area '" + v + "' is not 6 odd numbers 1-15 - the default 1,3,5,7,9,11 applies");
    AREA = a == null ? new int[] { 1, 3, 5, 7, 9, 11 } : a;
    AREA_SRC = v;
  }
  int[] a2 = AREA;
  if (tier < 0) tier = 0;
  if (tier >= a2.length) tier = a2.length - 1;
  return a2[tier];
}""")
M(gcan, r"""
public static int uses(int tier) {
  String v = @PKG@.GearCfg.CAN_USES;
  if (v != null && !v.equals(USES_SRC)) {
    int[] a = parseNums(v, 1, 1000, false);
    if (a == null) @PKG@.Gear.warnOnce("canuses:" + v.hashCode(), "config.properties: can.uses '" + v + "' is not 6 numbers 1-1000 - the default 20,30,40,60,80,100 applies");
    USES = a == null ? new int[] { 20, 30, 40, 60, 80, 100 } : a;
    USES_SRC = v;
  }
  int[] a2 = USES;
  if (tier < 0) tier = 0;
  if (tier >= a2.length) tier = a2.length - 1;
  return a2[tier];
}""")
# THE PLAN of one watering with can id: double[] { side, wet seconds, water used per watering (bar points; 0 = never runs dry), Growth Boost seconds,
# Bloom %, Capacity / Growth / Lasting / Bloom levels }. Only YOUR lifelong can uses its points (a found / foreign / plain one: none)
M(gcan, r"""
public static double[] plan(java.util.UUID u, String id, @BD@ d, double maxDur) {
  int t = @PKG@.GearLL.tier(id);
  double sd = (double) side(t);
  double us = (double) uses(t);
  java.util.Properties P = null;
  if (u != null && @PKG@.GearCfg.LL_ON && @PKG@.GearLL.mine(u, d) && !@PKG@.GearLL.rbWait(u)) {
    P = @PKG@.GearLL.reg(@PKG@.Gear.pkey(u));
    if (@PKG@.GearLL.bad(P)) P = null;
  }
  int k = @PKG@.GearLL.CAN;
  int cap = P == null ? 0 : @PKG@.GearLL.perkOf(P, k, @PKG@.GearLL.PK_CAP);
  int gro = P == null ? 0 : @PKG@.GearLL.perkOf(P, k, @PKG@.GearLL.PK_GROW);
  int las = P == null ? 0 : @PKG@.GearLL.perkOf(P, k, @PKG@.GearLL.PK_LAST);
  int blo = P == null ? 0 : @PKG@.GearLL.perkOf(P, k, @PKG@.GearLL.PK_BLOOM);
  double sec = (double) @PKG@.GearCfg.CAN_SEC;
  double dur = sec * (1.0 + (double) las * @PKG@.GearCfg.CAN_LAST / 100.0);
  double mx = maxDur > 0.0 ? maxDur : 100.0;
  double use = cap >= @PKG@.GearLL.PKMAX[@PKG@.GearLL.PK_CAP] ? 0.0 : mx / (us * (1.0 + (double) cap * @PKG@.GearCfg.CAN_CAPP / 100.0));
  double g = (double) gro * @PKG@.GearCfg.CAN_GROW / 100.0 * sec;
  if (g > sec) g = sec;
  double b = (double) blo * @PKG@.GearCfg.CAN_BLOOM;
  if (b > 100.0) b = 100.0;
  return new double[] { sd, dur, use, g, b, (double) cap, (double) gro, (double) las, (double) blo };
}""")
# the tooltip rows of a can (GearTool.lines, family 0): the square, the waterings, the lifelong lines
M(gcan, r"""
public static void lines(java.util.UUID owner, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  if (!@PKG@.GearData.can(id)) return;
  int t = @PKG@.GearLL.tier(id);
  int sd = side(t);
  txt.add("Waters " + sd + "x" + sd + " tilled soil (right-click)");
  col.add(null);
  txt.add(uses(t) + " waterings per fill - right-click water to refill");
  col.add(null);
  if (!@PKG@.GearCfg.CAN_ON) { txt.add("Watering cans are switched off on this server"); col.add(@PKG@.GearDefs.C_BAD); }
  @PKG@.GearLL.lines(owner, id, d, txt, col);
}""")
''')
rep('''  if (f == 0 || !@PKG@.GearCfg.PART_TOOLS) return;
  int t = tier(id);
  if (f == 6) { mlines(owner, id, d, t, txt, col); return; }          // 0.2.18: a multitool''',
    '''  if (f == 0) { @PKG@.GearCan.lines(owner, id, d, txt, col); return; }          // 0.3.12: the watering can (no GearTool family)
  if (!@PKG@.GearCfg.PART_TOOLS) return;
  int t = tier(id);
  if (f == 6) { mlines(owner, id, d, t, txt, col); return; }          // 0.2.18: a multitool''')
rep('''  @PKG@.GearLL.lines(owner, id, d, txt, col);          // 0.3.0: lifelong tool lines''',
    '''  if (@PKG@.GearLL.harv(id)) { txt.add("Tills soil (right-click) - your hoe and sickle in one"); col.add(@PKG@.GearDefs.C_LABEL); }          // 0.3.12
  @PKG@.GearLL.lines(owner, id, d, txt, col);          // 0.3.0: lifelong tool lines''')

# ================================================================================================================ 3c: Health regen through skill:fn:hpregen
rep('''  if (s.equals("hprp")) return " (boosts Raw Health Regen)";''', '''  if (s.equals("hprp")) return " (boosts Health Regen)";          // 0.3.12: with SkyySkills it boosts the whole regen (skill:fn:hpregen addpct)''')
before('''# GearTick, once per second per player (world thread): the armor part, then regen / stamina every regen.periodMs, Life Steal payout
''', r'''# 0.3.12 (tools/gear_0_3_12_patch.py 3c): Raw Health Regen / Health Regen % go to SkyySkills' skill:fn:hpregen (0.4.43; source "SkyyGear"):
# add = HP a second (hpr per regen.periodMs), addpct = hprp % of the whole regen. Posted when it changes and every 10 s (the registry is memory
# only: a SkyySkills reload re-learns it); while it is there GearFx does not heal hpr itself (never twice). No SkyySkills = the old 2 s heal.
F(gfx, "public static final java.util.concurrent.ConcurrentHashMap HPR = new java.util.concurrent.ConcurrentHashMap();")          # UUID -> double[] { flat, pct, at }
F(gfx, "public static final long[] HPN = new long[3];")          # 0 posts, 1 drops, 2 failures
# fix round (critic 2.1 / 2.2): HPF = the skill:fn:hpregen object the cache was posted to (a SkyySkills reload makes a new one = post again at
# once); SKON / SKAT = SkyySkills' hp.regen.enabled read over its config kit (config:fn:SkyySkills get, every 5 s): off = Gear heals itself
F(gfx, "public static volatile Object HPF = null;")
F(gfx, "public static volatile boolean SKON = true;")
F(gfx, "public static volatile long SKAT = 0L;")
M(gfx, r"""
public static boolean skillsRegenOn() {
  long now = System.currentTimeMillis();
  if (SKAT != 0L && now >= SKAT && now - SKAT < 5000L) return SKON;
  SKAT = now;
  boolean on = true;
  try {
    java.util.function.Function f = @PKG@.Gear.fn("config:fn:SkyySkills");
    Object v = f == null ? null : f.apply(new Object[] { "get", "hp.regen.enabled" });
    if (v instanceof String && ((String) v).trim().equalsIgnoreCase("false")) on = false;
  } catch (Throwable t) { on = true; }
  SKON = on;
  return on;
}""")
M(gfx, r"""
public static boolean hpPost(java.util.UUID u, int[] t, long per) {
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:hpregen");
  if (f == null || u == null) { if (u != null) HPR.remove(u); return false; }
  long pp = per < 250L ? 250L : per;
  double flat = t == null ? 0.0 : (double) t[@PKG@.GearHit.I_HPR] * 1000.0 / (double) pp;
  double pct = t == null ? 0.0 : (double) t[@PKG@.GearHit.I_HPRP];
  if (flat > 100.0) flat = 100.0;
  if (flat < -100.0) flat = -100.0;
  if (pct > 1000.0) pct = 1000.0;
  if (pct < -100.0) pct = -100.0;
  long now = System.currentTimeMillis();
  if (f != HPF) { HPR.clear(); HPF = f; }          // fix round: a new SkyySkills registry (reload) = everyone posts again now
  Object o = HPR.get(u);
  if (o instanceof double[]) {
    double[] l = (double[]) o;
    if (l[0] == flat && l[1] == pct && (double) now - l[2] < 10000.0 && (double) now >= l[2]) return true;
  }
  try {
    f.apply(new Object[] { "add", u, "SkyyGear", Double.valueOf(flat) });
    f.apply(new Object[] { "addpct", u, "SkyyGear", Double.valueOf(pct) });
  } catch (Throwable x) { HPN[2] = HPN[2] + 1L; @PKG@.Gear.warnOnce("hpregen", "skill:fn:hpregen failed (Gear heals its regen itself; logged once): " + x); HPR.remove(u); return false; }
  HPR.put(u, new double[] { flat, pct, (double) now });
  HPN[0] = HPN[0] + 1L;
  return true;
}""")
M(gfx, "public static boolean hpPosted(java.util.UUID u) { return u != null && HPR.containsKey(u) && @PKG@.Gear.fn(\"skill:fn:hpregen\") != null && skillsRegenOn(); }")          # fix round: + SkyySkills' regen on
M(gfx, r"""
public static void hpDrop(java.util.UUID u) {
  if (u == null) return;
  Object had = HPR.remove(u);
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:hpregen");
  if (f == null || had == null) return;
  try { f.apply(new Object[] { "remove", u, "SkyyGear" }); HPN[1] = HPN[1] + 1L; } catch (Throwable x) { }
}""")
M(gfx, r"""
public static void hpClear() {
  HPR.clear();
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:hpregen");
  if (f == null) return;
  try { f.apply(new Object[] { "clear", "SkyyGear" }); } catch (Throwable x) { }
}""")
''')
rep('''  if (!@PKG@.GearCfg.PART_STATS) { REGEN.remove(u); LEECH.remove(u); MANA.remove(u); return; }''',
    '''  if (!@PKG@.GearCfg.PART_STATS) { REGEN.remove(u); LEECH.remove(u); MANA.remove(u); hpDrop(u); return; }          // 0.3.12: + the hpregen source''')
rep('''  int[] t = @PKG@.GearStats.totalsInv(u, inv, true);
  long[] rg = (long[]) REGEN.get(u);''', '''  int[] t = @PKG@.GearStats.totalsInv(u, inv, true);
  hpPost(u, t, (long) @PKG@.GearCfg.REGEN_MS);          // 0.3.12: hpr / hprp -> skill:fn:hpregen (SkyySkills heals them)
  long[] rg = (long[]) REGEN.get(u);''')
rep('''      if (hp > 0.0) add(m, @DST@.getHealth(), (float) hp, true);''',
    '''      if (hp > 0.0 && !hpPosted(u)) add(m, @DST@.getHealth(), (float) hp, true);          // 0.3.12: only without skill:fn:hpregen (never twice)''')
rep('''  REGEN.remove(u); LEECH.remove(u); MANA.remove(u); WARNED.remove(u); MOVE.remove(u); LOCKED.remove(u); BLOCKED.remove(u); PRIMED.remove(u);''',
    '''  REGEN.remove(u); LEECH.remove(u); MANA.remove(u); WARNED.remove(u); MOVE.remove(u); LOCKED.remove(u); BLOCKED.remove(u); PRIMED.remove(u);
  hpDrop(u);          // 0.3.12
  @PKG@.GearCan.LAST.remove(u);          // 0.3.12 fix round 2 (critic B2): the hold-and-sweep memory goes with the player''')

# ================================================================================================================ 3a: Crescent Rush on the longsword's tooltip
before('''# a weapon's head (speed), base rows and Ability rows. 0.2.2 rules kept: a SkyyArmory wand / staff shows its two shots and never the melee line
''', r'''# 0.3.12 (tools/gear_0_3_12_patch.py 3a): SkyyArmory 0.1.28 turned the longsword's charged stab into the Spellblade's Crescent Rush (its bridge
# string armory:blade starts "Spellblade swords: Crescent Rush on"); a longsword then shows that ability, never the old "Charged Attack" range.
# null = Armory not loaded / the rush off / not a longsword (the old line stays)
M(gvw, r"""
public static String rushText(String id) {
  if (id == null || !id.startsWith("Weapon_Longsword_")) return null;
  Object o = @PKG@.Gear.bget("armory:blade");
  if (!(o instanceof String)) return null;
  String s = (String) o;
  if (!s.startsWith("Spellblade swords: Crescent Rush on")) return null;
  String cost = "";
  try {
    int mi = s.indexOf(" Mana + ");
    int si = mi < 0 ? -1 : s.indexOf(" Stamina", mi);
    int ms = mi < 0 ? -1 : s.lastIndexOf("; ", mi);
    if (mi > 0 && si > mi && ms >= 0) cost = " (" + s.substring(ms + 2, mi).trim() + " Mana + " + s.substring(mi + 8, si).trim() + " Stamina)";
  } catch (Throwable t) { cost = ""; }
  return "Spellblade: hold the attack, then release to dash ahead and sweep the enemies in front" + cost + ".";
}""")
''')
rep('''    if (spd[2] != null) {
      add(at, ac, "Ability: Charged Attack", bold(@PKG@.GearDefs.C_GOLD));
      add(at, ac, "Deals " + spd[2] + " damage at full charge.", @PKG@.GearDefs.C_GRAY);
    }''', '''    String rush = spd[2] != null ? rushText(id) : null;          // 0.3.12: the longsword hold is Crescent Rush with SkyyArmory 0.1.28
    if (rush != null) {
      add(at, ac, "Ability: Crescent Rush", bold(@PKG@.GearDefs.C_GOLD));
      add(at, ac, rush, @PKG@.GearDefs.C_GRAY);
    } else if (spd[2] != null) {
      add(at, ac, "Ability: Charged Attack", bold(@PKG@.GearDefs.C_GOLD));
      add(at, ac, "Deals " + spd[2] + " damage at full charge.", @PKG@.GearDefs.C_GRAY);
    }''')

# ================================================================================================================ 1 + 2: GearLife (the kit, the merge)
before('''# THE SWEEP (world thread; join = force, every stamp scan = at most every 400 ms): journals, the migration (once), the look
''', r'''# 0.3.12 THE WATERING CAN IN THE STARTING KIT (lifelong.canKit; Skyy 2026-10-15 "i want it to spawn with you"): ONCE per profile (registry
# canKit=1) - the pole kit's path: a can the registry names counts; a lifelong can of this profile in the inventory is adopted; a plain one carried
# is marked; else the Crude can is GIVEN through the journalled give (journal first, the same uid on a retry - never a second copy); a give that
# reached the disk but never the inventory (never seen, no journal, not carried) is REDONE once. true = the registry changed in memory.
F(glf, "public static final long[] CK = new long[4];")          # 0.3.12: 0 cans given, 1 adopted / marked, 2 already had one, 3 waiting for room
M(glf, r"""
public static boolean canKit(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  if (!@PKG@.GearCfg.CAN_ON || !@PKG@.GearCfg.CAN_KIT || pr == null || inv == null || P == null) return false;
  int k = @PKG@.GearLL.CAN;
  String K = @PKG@.GearLL.KIND[k];
  java.util.UUID u = pr.getUuid();
  boolean ch = false;
  if ("1".equals(P.getProperty("canKit"))) {
    String cu = P.getProperty(K + ".uid");
    if (cu == null || !"give".equals(P.getProperty("canKitHow")) || !cu.equals(P.getProperty("canKitUid")) || "1".equals(P.getProperty(K + ".seen"))
        || P.getProperty(K + ".pend") != null || find(inv, pk, cu) != null) return false;
    P.remove(K + ".uid");
    P.remove(K + ".id");
    P.remove(K + ".rp");
    P.remove("canKit");
    P.remove("canKitHow");
    P.remove("canKitUid");
    @PKG@.GearLog.line("LL-CANKIT-REDO " + u + " " + pk + " " + cu + " (the kit gave it, never seen, not in the inventory)");
    ch = true;
  }
  String cr = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.Gear.item(cr) == null) return ch;
  long now = System.currentTimeMillis();
  if (P.getProperty(K + ".uid") != null && P.getProperty(K + ".pend") == null) {
    P.setProperty("canKit", "1");
    P.setProperty("canKitAt", String.valueOf(now));
    P.setProperty("canKitHow", "had");
    CK[2] = CK[2] + 1L;
    @PKG@.GearLog.line("LL-CANKIT-HAD " + u + " " + pk + " " + P.getProperty(K + ".uid"));
    return true;
  }
  if (P.getProperty(K + ".pend") == null) {
    int[] ad = findKind(inv, pk, k);
    if (ad != null) {
      @IS@ x = @PKG@.GearStamp.at(inv, ad[0], ad[1]);
      @BD@ d = docOf(x);
      commit(pk, P, k, @PKG@.GearLL.uid(d), x.getItemId(), @PKG@.GearLL.isRp(d), "canKit", "1", false);
      P.setProperty("canKitAt", String.valueOf(now));
      P.setProperty("canKitHow", "adopt");
      CK[1] = CK[1] + 1L;
      @PKG@.GearLog.line("LL-CANKIT-ADOPT " + u + " " + pk + " " + @PKG@.GearLL.uid(d) + " " + x.getItemId());
      return true;
    }
    int[] b = best(inv, k);
    if (b != null) {
      if (!mark(pr, inv, pk, P, k, b[0], b[1], "mark")) return ch;
      P.setProperty("canKit", "1");
      P.setProperty("canKitAt", String.valueOf(now));
      P.setProperty("canKitHow", "mark");
      CK[1] = CK[1] + 1L;
      tellOnce(pr, "cankit", "The watering can you carry is your lifelong watering can now - it can't be dropped, and /can brings it back if you lose it.", 5000L);
      return true;
    }
  }
  int g = give(pr, inv, pk, P, k, cr, "give");
  if (g == 1) {
    P.setProperty("canKit", "1");
    P.setProperty("canKitAt", String.valueOf(now));
    P.setProperty("canKitHow", "give");
    if (P.getProperty(K + ".uid") != null) P.setProperty("canKitUid", P.getProperty(K + ".uid"));
    CK[0] = CK[0] + 1L;
    tellOnce(pr, "cankit", "You got your lifelong watering can - right-click tilled soil to water it, right-click water to fill it. It tiers up like your other tools (a bigger square each tier). Lost it? /can", 5000L);
    return true;
  }
  if (g == 0) { CK[3] = CK[3] + 1L; tellOnce(pr, "room" + k, "Your lifelong watering can is waiting - free one inventory slot and it arrives.", 60000L); }
  return ch;
}""")
# 0.3.12 THE HARVESTER (Skyy 2026-10-15: "id like to make a new kind of multitool the combines the hoe and the sickle"; popups "Harvester",
# "Same as multitool: rebirth 1"): the lifelong hoe + sickle become ONE Harvester = the sickle kind's tool (its uid), the hoe kind leaves the
# registry. Journalled: harv.pend (the sickle's uid) / harv.hoeU / harv.id / harv.doc (the merged document) / harv.at on disk before anything
# moves; the hoe leaves; the sickle's slot gets the Harvester; harvFinal forgets the hoe (harv=1). harvRecover finishes or drops a journal.
F(glf, "public static final long[] HV = new long[6];")          # 0 made, 1 refused, 2 failed + restored, 3 finished by the next look, 4 journals dropped, 5 old hoes retired
M(glf, r"""
public static String harvGate(java.util.UUID u) {
  if (!@PKG@.GearCfg.HARV_RBGATE || u == null || @PKG@.Gear.fn("rebirth:fn:count") == null) return null;
  Object n = @PKG@.Gear.bget("rebirth:n:" + u);
  if (!(n instanceof Integer)) return "Your rebirths are still loading - try again in a moment.";
  if (((Integer) n).intValue() >= 1) return null;
  return "The Harvester comes after your first rebirth.";
}""")
M(glf, r"""
public static void harvDrop(java.util.Properties P) {
  P.remove("harv.pend");
  P.remove("harv.hoeU");
  P.remove("harv.id");
  P.remove("harv.doc");
  P.remove("harv.at");
}""")
# Object[] { String why (null = they can merge), int[] hoe slot, int[] sickle slot, String the Harvester id (tier = the higher of the two) }
M(glf, r"""
public static Object[] harvCheck(java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {
  String w = null;
  if (!@PKG@.GearCfg.LL_ON) w = "Lifelong tools are switched off on this server.";
  else if (!@PKG@.GearCfg.HARV_ON) w = "The Harvester is switched off on this server.";
  else if (u == null || inv == null) w = "Your inventory cannot be read right now.";
  else if (@PKG@.Gear.busy(u)) w = "Your profile is still loading - try again in a moment.";
  else if (P == null || @PKG@.GearLL.bad(P)) w = "Your lifelong tool list cannot be read right now.";
  else if (@PKG@.GearLL.merged(P)) w = "You already have your Harvester.";
  else if (P.getProperty("harv.pend") != null) w = "Your Harvester is still being made - try again in a moment.";
  else if (!"1".equals(P.getProperty("migrated"))) w = "Your starting tools are still arriving - free an inventory slot and try again.";          // fix round (critic 1.1)
  if (w == null) w = harvGate(u);
  if (w == null && @PKG@.GearLL.rbWait(u)) w = "A rebirth is finishing on this profile - try again in a few seconds.";
  if (w != null) return new Object[] { w, null, null, null };
  String hoeU = P.getProperty("hoe.uid");
  String siU = P.getProperty("sickle.uid");
  if (hoeU == null || siU == null) return new Object[] { "You need your lifelong hoe and sickle first.", null, null, null };
  if (P.getProperty("hoe.pend") != null || P.getProperty("sickle.pend") != null) return new Object[] { "Your tools are still being sorted out - try again in a moment.", null, null, null };
  int[] ha = find(inv, pk, hoeU);
  int[] sa = find(inv, pk, siU);
  if (ha == null && sa == null) return new Object[] { "Carry your lifelong hoe and sickle (/hoe and /sickle bring them back).", null, null, null };
  if (ha == null) return new Object[] { "Carry your lifelong hoe too (/hoe brings it back).", null, null, null };
  if (sa == null) return new Object[] { "Carry your lifelong sickle too (/sickle brings it back).", null, null, null };
  @IS@ h = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
  @IS@ s = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
  if (h == null || s == null || h.isEmpty() || s.isEmpty()) return new Object[] { "Your tools moved - try again.", null, null, null };
  @BD@ hd = docOf(h);
  @BD@ sd = docOf(s);
  if (@PKG@.GearLL.isRt(hd) || @PKG@.GearLL.isRt(sd)) return new Object[] { "A retired tool can't be merged - hold it and type /lifelong to swap it back first.", null, null, null };
  if (@PKG@.GearLL.harv(s.getItemId())) return new Object[] { "Your sickle is a Harvester already.", null, null, null };
  if (@PKG@.GearLL.kOf(h.getItemId()) != 2 || @PKG@.GearLL.kOf(s.getItemId()) != 3) return new Object[] { "Those are not your lifelong hoe and sickle.", null, null, null };
  int th = @PKG@.GearLL.tier(h.getItemId());
  int ts = @PKG@.GearLL.tier(s.getItemId());
  int t = th > ts ? th : ts;
  if (t < 0) t = 0;
  if (t > 3) t = 3;
  String hid = @PKG@.GearLL.HARV_PRE + @PKG@.GearLL.tname(t);
  if (@PKG@.Gear.item(hid) == null) return new Object[] { "The Harvester is not loaded on this server.", null, null, null };
  return new Object[] { null, ha, sa, hid };
}""")
# one input's lines into best[] / frac[] - only lines the Harvester (sickle family, bit 5) may roll; the cap = the Harvester's at that rarity / level
M(glf, r"""
public static int harvLines(int[] best, double[] frac, @BD@ d, String hid, int r, int L, int[] info) {
  int dropped = 0;
  if (d == null) return 0;
  @BA@ ms = @PKG@.GearData.mods(d);
  for (int k = 0; k < ms.size(); k++) {
    @BV@ v = ms.get(k);
    if (v == null || !v.isDocument()) { dropped++; continue; }
    @BD@ m = v.asDocument();
    int si = @PKG@.GearDefs.sIndex(@PKG@.GearData.str(m, "s", null));
    int val = @PKG@.GearData.num(m, "v", 0);
    if (si < 0 || (@PKG@.GearDefs.S_TMASK[si] & (1 << 5)) == 0 || val <= 0) { dropped++; continue; }
    int hi = @PKG@.GearMerge.capOf(si, hid, r, L);
    if (val > hi) { val = hi; info[1]++; }
    if (val > best[si]) { best[si] = val; frac[si] = (double) val / (double) (hi < 1 ? 1 : hi); }
  }
  return dropped;
}""")
# THE MERGED DOCUMENT: the sickle's own (its uid, owner, rebirth stamps ... stay; the replacement / retired marks go), the better rarity, both
# tools' lines (the best value of each, the rarity's line count - the multitool rule), the higher reforge count / the better tool's reforge name,
# the Harvester's kind + the level rule. info: [0] lines lost, [1] lines lowered to the cap, [3] the level
M(glf, r"""
public static @BD@ harvDoc(@IS@ hoe, @IS@ sic, String hid, java.util.UUID u, int[] info) {
  @BD@ hd = docOf(hoe);
  @BD@ sd = docOf(sic);
  if (hd == null || sd == null) return null;
  int rh = @PKG@.GearData.rarity(hd);
  int rs = @PKG@.GearData.rarity(sd);
  int r = rh > rs ? rh : rs;
  if (r > 4) r = 4;
  @BD@ d = sd.clone();
  d.remove("lrp");
  d.remove("lrpT");
  d.remove("lrt");
  d.remove("lrpF");
  d.remove("lrpS");
  d.remove("lcu");
  d.remove("lvU");
  String kd = @PKG@.GearData.kindFor(hid);
  d.put("kind", new org.bson.BsonString(kd));
  if (d.containsKey("gate")) d.put("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kd)));
  d.put("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[@PKG@.GearCfg.ri(r)]));
  d.put("tr", new org.bson.BsonInt32(1));
  int lv = @PKG@.GearLL.levelFor(u, hid);
  if (lv >= 1) d.put("lvl", new org.bson.BsonInt32(lv));
  int L = @PKG@.GearLevel.level(hid, d);
  int n = @PKG@.GearDefs.NS;
  int[] best = new int[n];
  double[] frac = new double[n];
  int dropped = harvLines(best, frac, hd, hid, r, L, info) + harvLines(best, frac, sd, hid, r, L, info);
  int cnt = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  boolean[] keep = new boolean[n];
  for (int k = 0; k < cnt; k++) {
    int sel = -1;
    for (int i = 0; i < n; i++) {
      if (keep[i] || best[i] <= 0) continue;
      if (sel < 0 || frac[i] > frac[sel]) sel = i;
    }
    if (sel < 0) break;
    keep[sel] = true;
  }
  @BA@ out = new @BA@();
  for (int i = 0; i < n; i++) {
    if (best[i] <= 0) continue;
    if (keep[i]) out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], best[i]));
    else dropped++;
  }
  d.put("mods", out);
  int rf = @PKG@.GearData.num(hd, "rfN", 0);
  int rf2 = @PKG@.GearData.num(sd, "rfN", 0);
  if (rf2 > rf) rf = rf2;
  if (rf > 0) d.put("rfN", new org.bson.BsonInt32(rf));
  String nm = rh > rs ? @PKG@.GearData.str(hd, "rf", null) : @PKG@.GearData.str(sd, "rf", null);
  if (nm == null) nm = rh > rs ? @PKG@.GearData.str(sd, "rf", null) : @PKG@.GearData.str(hd, "rf", null);
  if (nm != null) d.put("rf", new org.bson.BsonString(nm));
  int sg = @PKG@.GearData.num(hd, "sgN", 0);
  int sg2 = @PKG@.GearData.num(sd, "sgN", 0);
  if (sg2 > sg) sg = sg2;
  if (sg > 0) d.put("sgN", new org.bson.BsonInt32(sg));
  info[0] = dropped;
  info[3] = L;
  return d;
}""")
# the points: the higher level of each perk (they are the same Farming points), trimmed from the last perk down to what you have (no SkyySkills
# = no trim); the higher reset count. Returns the perks that lost a level ("" = none)
M(glf, r"""
public static String harvPerks(java.util.UUID u, java.util.Properties P) {
  StringBuilder sb = new StringBuilder();
  int hk = 2;
  int sk = 3;
  for (int p = 0; p < @PKG@.GearLL.PK.length; p++) {
    if (!@PKG@.GearLL.perkFor(sk, p)) continue;
    int a = @PKG@.GearLL.perkOf(P, hk, p);
    int b = @PKG@.GearLL.perkOf(P, sk, p);
    int m = a > b ? a : b;
    String key = @PKG@.GearLL.KIND[sk] + ".up." + @PKG@.GearLL.PK[p];
    if (m > 0) P.setProperty(key, String.valueOf(m)); else P.remove(key);
  }
  if (@PKG@.GearLL.skill(u, sk) != -2) {
    int er = @PKG@.GearLL.earned(u, sk);
    int guard = 0;
    while (@PKG@.GearLL.spent(P, sk) > er && guard < 200) {
      guard++;
      int sel = -1;
      for (int p = @PKG@.GearLL.PK.length - 1; p >= 0 && sel < 0; p--) if (@PKG@.GearLL.perkFor(sk, p) && @PKG@.GearLL.perkOf(P, sk, p) > 0) sel = p;
      if (sel < 0) break;
      int lv = @PKG@.GearLL.perkOf(P, sk, sel) - 1;
      String key2 = @PKG@.GearLL.KIND[sk] + ".up." + @PKG@.GearLL.PK[sel];
      if (lv > 0) P.setProperty(key2, String.valueOf(lv)); else P.remove(key2);
      if (sb.length() > 0) sb.append(", ");
      sb.append(@PKG@.GearLL.PKN[sel]);
    }
  }
  long ra = @PKG@.GearLL.getl(P, "hoe.resets", 0L);
  long rb = @PKG@.GearLL.getl(P, "sickle.resets", 0L);
  if (ra > rb) P.setProperty("sickle.resets", String.valueOf(ra));
  return sb.toString();
}""")
# THE COMMIT of a merge: the points, the hoe kind leaves the registry (every hoe.* key), harv=1 (+ when, + the hoe's uid), the sickle names the
# Harvester, the journal goes - ONE registry write; a failed write changes nothing in memory (the journal on disk finishes it at the next look)
M(glf, r"""
public static boolean harvFinal(@PR@ pr, String pk, java.util.Properties P, String how) {
  java.util.UUID u = pr.getUuid();
  String hoeU = P.getProperty("harv.hoeU");
  String hid = P.getProperty("harv.id");
  java.util.Properties old = (java.util.Properties) P.clone();
  String trimmed = harvPerks(u, P);
  java.util.ArrayList ks = new java.util.ArrayList(P.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String k = String.valueOf(ks.get(i));
    if (k.startsWith("hoe.")) P.remove(k);
  }
  P.setProperty("harv", "1");
  P.setProperty("harvAt", String.valueOf(System.currentTimeMillis()));
  if (hoeU != null) P.setProperty("harvHoe", hoeU);
  if (hid != null) P.setProperty("sickle.id", hid);
  P.setProperty("sickle.rp", "0");          // fix round 2 (critic A2): the Harvester IS the tool now (its document has no lrp) - an original sickle
  P.remove("sickle.inv");          // that turns up later is retired, never restored over the Harvester
  harvDrop(P);
  if (!@PKG@.GearLL.save(pk, P)) {
    P.clear();
    P.putAll(old);
    return false;
  }
  @PKG@.GearTool.LAST.remove(u);
  @PKG@.GearGate.bump(u);
  @PKG@.GearLog.line("LL-HARV-" + how.toUpperCase().replace(' ', '-') + " " + u + " " + pk + " " + P.getProperty("sickle.uid") + " " + hid + " (hoe " + hoeU + " gone from the registry" + (trimmed.length() > 0 ? "; points trimmed: " + trimmed : "") + ")");
  if (trimmed.length() > 0) tellOnce(pr, "harvtrim", "Your Harvester keeps the best of both tools' points, up to the points you have - " + trimmed + " lost a level (spend it again on the Tools tab).", 5000L);
  return true;
}""")
# fix round 2 (critic A1): THE PREVIEW the Tools tab shows before the (irreversible) merge - the same harvDoc / harvPerks on copies (nothing
# changes): String[] { the Harvester's rarity name, lines kept, lines lost, lines lowered to the cap, perks that lose a level ("" = none) } or null
M(glf, r"""
public static String[] harvPreview(java.util.UUID u, @INV@ inv, java.util.Properties P, Object[] c) {
  if (c == null || c[0] != null || inv == null || P == null) return null;
  try {
    int[] ha = (int[]) c[1];
    int[] sa = (int[]) c[2];
    @IS@ h = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
    @IS@ s = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
    int[] info = new int[4];
    @BD@ nd = harvDoc(h, s, (String) c[3], u, info);
    if (nd == null) return null;
    java.util.Properties Pc = (java.util.Properties) P.clone();
    String tr = harvPerks(u, Pc);
    return new String[] { @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(nd)], String.valueOf(@PKG@.GearData.mods(nd).size()), String.valueOf(info[0]), String.valueOf(info[1]), tr };
  } catch (Throwable t) { return null; }
}""")
M(glf, r"""
public static String harvLoss(String[] pv) {
  if (pv == null) return "";
  StringBuilder sb = new StringBuilder();
  sb.append(pv[0]).append(", keeps ").append(pv[1]).append(" line").append("1".equals(pv[1]) ? "" : "s");
  if (!"0".equals(pv[2])) sb.append(", LOSES ").append(pv[2]).append(" line").append("1".equals(pv[2]) ? "" : "s");
  if (!"0".equals(pv[3])) sb.append(", ").append(pv[3]).append(" lowered to the cap");
  if (pv[4] != null && pv[4].length() > 0) sb.append("; points that lose a level: ").append(pv[4]);
  return sb.toString();
}""")
# THE MERGE (Tools tab "Make Harvester"; world thread): "+" made, "-" why not / what happened
M(glf, r"""
public static String harvest(@PR@ pr, @INV@ inv) {
  if (pr == null || inv == null) return "-Your inventory cannot be read right now - nothing changed.";
  java.util.UUID u = pr.getUuid();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  Object[] c = harvCheck(u, inv, pk, P);
  if (c[0] != null) { HV[1] = HV[1] + 1L; return "-" + (String) c[0]; }
  int[] ha = (int[]) c[1];
  int[] sa = (int[]) c[2];
  String hid = (String) c[3];
  @IC@ hc = @PKG@.GearStamp.section(inv, ha[0]);
  @IC@ sc = @PKG@.GearStamp.section(inv, sa[0]);
  @IS@ hoe = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
  @IS@ sic = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
  if (hc == null || sc == null || hoe == null || sic == null) return "-Your tools moved - try again.";
  int[] info = new int[4];
  @BD@ nd = null;
  @IS@ ns = null;
  try {
    nd = harvDoc(hoe, sic, hid, u, info);
    if (nd != null) ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(hid, 1), sic), nd, u);
  } catch (Throwable t0) { nd = null; ns = null; @PKG@.Gear.warn("Harvester: the document could not be made for " + pr.getUsername() + ": " + t0); }
  if (nd == null || ns == null || ns.isEmpty() || !hid.equals(ns.getItemId())) return "-The Harvester could not be made - nothing was used.";
  String siU = @PKG@.GearLL.uid(docOf(sic));
  String hoeU = @PKG@.GearLL.uid(docOf(hoe));
  String who = pr.getUsername();
  @PKG@.GearLog.line("LL-HARV-BEGIN " + who + " " + u + " " + pk + " hoe " + hoe.getItemId() + " @" + @PKG@.GearForge.where(ha[0], ha[1]) + " " + @PKG@.GearMerge.json(hoe) + " + sickle " + sic.getItemId() + " @" + @PKG@.GearForge.where(sa[0], sa[1]) + " " + @PKG@.GearMerge.json(sic) + " -> " + hid + " " + nd.toJson());
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }
  String dj = null;
  try { dj = java.util.Base64.getEncoder().encodeToString(nd.toJson().getBytes("UTF-8")); } catch (Throwable tj) { dj = null; }
  P.setProperty("harv.pend", siU);
  P.setProperty("harv.hoeU", hoeU);
  P.setProperty("harv.id", hid);
  if (dj != null) P.setProperty("harv.doc", dj);
  P.setProperty("harv.at", String.valueOf(System.currentTimeMillis()));
  if (!@PKG@.GearLL.save(pk, P)) { harvDrop(P); return "-Your choice could not be saved - nothing changed."; }
  crash(31);
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int bh = @PKG@.GearStamp.countId(all, hoe.getItemId());
  int bs = @PKG@.GearStamp.countId(all, sic.getItemId());
  int bv = @PKG@.GearStamp.countId(all, hid);
  // (a) the hoe leaves first: a crash after it finishes the merge from the journal (harvRecover), never copies anything
  Object t1 = null;
  Throwable e1 = null;
  try { t1 = hc.removeItemStackFromSlot((short) ha[1]); } catch (Throwable x1) { e1 = x1; }
  boolean gone = e1 == null && !(t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) && @PKG@.GearMerge.empty(hc, ha[1]);
  if (!gone) {
    if (@PKG@.GearMerge.empty(hc, ha[1])) { try { hc.setItemStackForSlot((short) ha[1], hoe); } catch (Throwable xb) { } }
    harvDrop(P);
    @PKG@.GearLL.save(pk, P);
    HV[2] = HV[2] + 1L;
    @PKG@.GearLog.line("LL-HARV-FAILED " + who + " " + u + " (the hoe was not taken: " + (e1 != null ? String.valueOf(e1) : "the inventory refused it") + ") - nothing used");
    return "-The inventory refused the change - nothing was used.";
  }
  @PKG@.GearStamp.selfNote(u, t1);
  crash(32);
  // (b) the sickle's slot gets the Harvester (the same lifelong uid)
  Object t2 = null;
  Throwable e2 = null;
  try { t2 = sc.setItemStackForSlot((short) sa[1], ns); } catch (Throwable x2) { e2 = x2; }
  @IS@ now = sc.getItemStack((short) sa[1]);
  @BD@ bd = docOf(now);
  boolean put = e2 == null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && now != null && hid.equals(now.getItemId()) && bd != null && siU.equals(@PKG@.GearLL.uid(bd));
  if (!put) {
    try { hc.setItemStackForSlot((short) ha[1], hoe); } catch (Throwable xr) { }
    boolean back = @PKG@.GearForge.same(hc.getItemStack((short) ha[1]), hoe.getItemId(), @PKG@.GearForge.fp(hoe));
    if (back) {
      harvDrop(P);
      @PKG@.GearLL.save(pk, P);
      HV[2] = HV[2] + 1L;
      @PKG@.GearLog.line("LL-HARV-FAILED " + who + " " + u + " (the Harvester was not written: " + (e2 != null ? String.valueOf(e2) : "the inventory refused it") + ") - RESTORED, nothing used");
      return "-The inventory refused the Harvester - nothing was used.";
    }
    @PKG@.Gear.warn("HARVESTER: the hoe of " + who + " (" + u + ") could not be put back - the merge is finished at the next look (the journal stays); both documents are in gear.log");
    @PKG@.GearLog.line("LL-HARV-RESTORE-FAILED " + who + " " + u + " " + @PKG@.GearMerge.json(hoe) + " (the journal stays - harvRecover finishes the Harvester)");
    return "-Something went wrong - your Harvester is finished at your next look (an admin can find both tools in the server log).";
  }
  @PKG@.GearStamp.selfNote(u, t2);
  crash(33);
  // (c) the registry forgets the hoe
  if (!harvFinal(pr, pk, P, "made")) @PKG@.Gear.warn("lifelong: the Harvester of " + pk + " could not be written to the registry - the next look finishes it");
  try {
    int ah = @PKG@.GearStamp.countId(all, hoe.getItemId());
    int as = @PKG@.GearStamp.countId(all, sic.getItemId());
    int av = @PKG@.GearStamp.countId(all, hid);
    if (ah != bh - 1 || as != bs - 1 || av != bv + 1) @PKG@.Gear.warn("HARVESTER COUNT MISMATCH for " + who + ": " + hoe.getItemId() + " " + bh + "->" + ah + ", " + sic.getItemId() + " " + bs + "->" + as + ", " + hid + " " + bv + "->" + av);
    @PKG@.GearMerge.rqGone(hoe, u, who);
    @PKG@.GSnd.upgrade(u);
  } catch (Throwable xa) { }
  HV[0] = HV[0] + 1L;
  return "+Your hoe and sickle are one " + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(nd)] + " " + @PKG@.Gear.itemName(hid) + " now (Lv " + @PKG@.GearLevel.level(hid, nd) + ")" + (info[0] > 0 ? ", " + info[0] + " line" + (info[0] == 1 ? "" : "s") + " did not fit" : "") + "! Right-click tills, a swing reaps. Lost it? /harvester";          // fix round 2: + the lines lost
}""")
# a merge the server did not finish (sweep, before the look): the Harvester is there -> commit; the hoe is still there -> nothing happened (the
# journal goes); the hoe left but the sickle is still a sickle -> the Harvester is written from harv.doc, then committed; the sickle not on the
# player 10 minutes after -> the journal goes (/hoe makes an exact copy if the hoe was lost)
M(glf, r"""
public static boolean harvRecover(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  String pend = P.getProperty("harv.pend");
  if (pend == null || pr == null || inv == null) return false;
  java.util.UUID u = pr.getUuid();
  String hid = P.getProperty("harv.id");
  int[] sa = find(inv, pk, pend);
  if (sa != null) {
    @IS@ x = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
    if (x != null && @PKG@.GearLL.harv(x.getItemId())) {
      boolean ok = harvFinal(pr, pk, P, "recovered");
      if (ok) HV[3] = HV[3] + 1L;
      return ok;
    }
    String hoeU = P.getProperty("harv.hoeU");
    if (hoeU != null && find(inv, pk, hoeU) != null) {
      harvDrop(P);
      @PKG@.GearLL.save(pk, P);
      HV[4] = HV[4] + 1L;
      @PKG@.GearLog.line("LL-HARV-RECOVER " + u + " " + pk + " both tools are still there - nothing happened, the journal goes");
      return true;
    }
    @BD@ nd = null;
    try {
      String dj = P.getProperty("harv.doc");
      if (dj != null) nd = @BD@.parse(new String(java.util.Base64.getDecoder().decode(dj), "UTF-8"));
    } catch (Throwable t) { nd = null; }
    if (nd == null || hid == null || @PKG@.Gear.item(hid) == null || !pend.equals(@PKG@.GearLL.uid(nd)) || x == null) {
      harvDrop(P);
      @PKG@.GearLL.save(pk, P);
      HV[4] = HV[4] + 1L;
      @PKG@.GearLog.line("LL-HARV-RECOVER " + u + " " + pk + " the hoe left but the Harvester cannot be made from the journal - the journal goes (/hoe makes an exact copy)");
      return true;
    }
    @IC@ sc = @PKG@.GearStamp.section(inv, sa[0]);
    @IS@ ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(hid, 1), x), nd, u);
    Object t2 = null;
    try { t2 = sc.setItemStackForSlot((short) sa[1], ns); } catch (Throwable x2) { t2 = null; }
    @IS@ now = sc.getItemStack((short) sa[1]);
    if (now == null || !hid.equals(now.getItemId())) { @PKG@.Gear.warnOnce("harvrec:" + pk, "the Harvester of " + pk + " could not be finished yet (the inventory refused it) - tried again at the next look"); return false; }
    @PKG@.GearStamp.selfNote(u, t2);
    boolean ok2 = harvFinal(pr, pk, P, "finished from the journal");
    if (ok2) { HV[3] = HV[3] + 1L; tellOnce(pr, "harvrec", "Your Harvester is finished.", 5000L); }
    return ok2;
  }
  long at = @PKG@.GearLL.getl(P, "harv.at", 0L);
  long now2 = System.currentTimeMillis();
  if (at > 0L && now2 - at > 600000L) {
    harvDrop(P);
    @PKG@.GearLL.save(pk, P);
    HV[4] = HV[4] + 1L;
    @PKG@.GearLog.line("LL-HARV-RECOVER " + u + " " + pk + " the sickle is not on the player 10 minutes after the merge began - the journal goes");
    return true;
  }
  return false;
}""")
''')
rep('''  rbApply(pr, pk, P);          // 0.3.5 REBIRTH R7: a committed rebirth record -> the registry (once)
''', '''  rbApply(pr, pk, P);          // 0.3.5 REBIRTH R7: a committed rebirth record -> the registry (once)
  harvRecover(pr, inv, pk, P);          // 0.3.12: a Harvester merge the server did not finish
''')
rep('''  if ("1".equals(P.getProperty("migrated")) && poleKit(pr, inv, pk, P)) mg = true;          // 0.3.11: the pole in the starting kit (after the four)
''', '''  if ("1".equals(P.getProperty("migrated")) && poleKit(pr, inv, pk, P)) mg = true;          // 0.3.11: the pole in the starting kit (after the four)
  if ("1".equals(P.getProperty("migrated")) && canKit(pr, inv, pk, P)) mg = true;          // 0.3.12: the watering can in the starting kit
''')
# fix round (critic 1.1): the one-time migration (the four tools) never gives / adopts a hoe once it is in the Harvester (a merge made before
# migrated=1 would otherwise get a free Crude hoe at the next look)
rep('''    if (cu != null) { done++; continue; }
    int[] ad = findKind(inv, pk, k);''', '''    if (cu != null) { done++; continue; }
    if (k == 2 && @PKG@.GearLL.merged(P)) { done++; continue; }          // 0.3.12 fix round: the hoe is part of the Harvester
    int[] ad = findKind(inv, pk, k);''')
# fix round (critic 1.4): after the merge the sickle kind's current uid is the Harvester's; an OLD sickle stack with that uid (an exact copy made
# before the merge, kept in a chest / the Vault / Requip) is removed whatever the scan order - never the Harvester
rep('''        if (lu.equals(cur)) {
          if (!one.add(lu)) {''', '''        if (lu.equals(cur)) {
          if (k == 3 && @PKG@.GearLL.merged(P) && !@PKG@.GearLL.harv(id)) { remove(c, i, x, u, "an old copy of your sickle (" + lu + ") - it is part of your Harvester now"); continue; }          // 0.3.12 fix round
          if (!one.add(lu)) {''')
rep('''        if (@PKG@.GearLL.isRt(d)) continue;          // fix round 2: a retired one stays as it is until /lifelong swaps it back
''', '''        if (@PKG@.GearLL.isRt(d)) continue;          // fix round 2: a retired one stays as it is until /lifelong swaps it back
        if (k == 2 && @PKG@.GearLL.merged(P)) { if (retire(c, i, x, d, u, "your hoe is part of your Harvester now")) dirty = true; continue; }          // 0.3.12
''')
rep('''    String cr = @PKG@.GearLL.KCRUDE[k];
    if (@PKG@.Gear.item(cr) != null) P.setProperty(K + ".id", cr);''', '''    String cr = @PKG@.GearLL.crudeOf(k, P.getProperty(K + ".id"));          // 0.3.12: a Harvester goes back to the Crude Harvester
    if (@PKG@.Gear.item(cr) != null) P.setProperty(K + ".id", cr);''')
rep('''  String to = @PKG@.GearLL.KCRUDE[k];''', '''  String to = @PKG@.GearLL.crudeOf(k, id);          // 0.3.12: a Harvester -> the Crude Harvester''')
rep('''  if (cur == null && k == @PKG@.GearLL.POLE && @PKG@.GearCfg.LL_POLEKIT) return "-Your lifelong fishing pole is on its way''',
    '''  if (k == 2 && @PKG@.GearLL.merged(P)) return "-Your hoe is part of your Harvester now - /harvester brings it back.";          // 0.3.12
  if (cur == null && k == @PKG@.GearLL.CAN) return @PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_KIT ? "-Your lifelong watering can is on its way - free one inventory slot and it arrives." : "-This server hands out no lifelong watering cans (lifelong.canKit is off).";          // 0.3.12
  if (cur == null && k == @PKG@.GearLL.POLE && @PKG@.GearCfg.LL_POLEKIT) return "-Your lifelong fishing pole is on its way''')
rep('''  if (id == null || @PKG@.Gear.item(id) == null || @PKG@.GearLL.kOf(id) != k) id = @PKG@.GearLL.KCRUDE[k];''',
    '''  if (id == null || @PKG@.Gear.item(id) == null || @PKG@.GearLL.kOf(id) != k) id = @PKG@.GearLL.crudeOf(k, P.getProperty(K + ".id"));          // 0.3.12: the Crude Harvester for a Harvester''')
rep('''  if (x.getQuantity() != 1) return "-That is a stack - hold a single tool.";
''', '''  if (x.getQuantity() != 1) return "-That is a stack - hold a single tool.";
  if (k == 2 && @PKG@.GearLL.merged(P)) return "-Your hoe is part of your Harvester now - a hoe can't be your lifelong tool again.";          // 0.3.12
  if (k == 3 && @PKG@.GearLL.merged(P) && !@PKG@.GearLL.harv(x.getItemId())) return "-Your sickle is part of your Harvester now - hold your Harvester (/harvester) instead.";          // 0.3.12 fix round 2
''')

# ================================================================================================================ LifePage (the Tools tab): 6 rows, the Harvester row
before('''# the item id shown for kind k: the stack on you, else the registry's last id, else the Crude one
''', r'''# 0.3.12: the rows the Tools tab shows (the pole only with SkyyFishing's rods; the hoe not after the Harvester merge); 6 rows = the compact look
M(lpg, r"""
public static boolean shown(int k, java.util.Properties P) {
  if (k == @PKG@.GearLL.POLE && @PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) return false;
  if (k == 2 && @PKG@.GearLL.merged(P)) return false;
  return true;
}""")
M(lpg, r"""
public static int rowsShown(java.util.Properties P) {
  int n = 0;
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) if (shown(k, P)) n++;
  return n;
}""")
''')
rep('''public void row(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P, int k) {
  String K = @PKG@.GearLL.KIND[k];''', '''public void row(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P, int k) {
  String K = @PKG@.GearLL.KIND[k];
  boolean cp = rowsShown(P) > 5;          // 0.3.12: six tools (+ the watering can) fit the 662 px list in the compact look
  int rh = cp ? 90 : 106;
  int cw = cp ? 72 : 80;
  int l1 = cp ? 28 : 32;
  int l2 = cp ? 25 : 30;''')
rep('''(Height: 106); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(k == this.sel) + " " + @PKG@.GearUi.cell(80, id)''',
    '''(Height: " + rh + "); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(k == this.sel) + " " + @PKG@.GearUi.cell(cw, id)''')
rep('''Label #SkyyGLRowN" + k + " { Anchor: (Height: 32);''', '''Label #SkyyGLRowN" + k + " { Anchor: (Height: " + l1 + ");''')
rep('''Label #SkyyGLRowA" + k + " { Anchor: (Height: 30);''', '''Label #SkyyGLRowA" + k + " { Anchor: (Height: " + l2 + ");''')
rep('''Label #SkyyGLRowB" + k + " { Anchor: (Height: 30);''', '''Label #SkyyGLRowB" + k + " { Anchor: (Height: " + l2 + ");''')
rep('''  b.set("#SkyyGLRowN" + k + ".Text", x == null ? @PKG@.GearLL.KNAME[k] + " - " + @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));''',
    '''  b.set("#SkyyGLRowN" + k + ".Text", x == null ? @PKG@.GearLL.kname(k, id) + " - " + @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));          // 0.3.12: "Harvester"''')
rep('''  if (cur == null) w = k == @PKG@.GearLL.POLE && !@PKG@.GearCfg.LL_POLEKIT ? "Not handed out on this server - a pole a quest gives you becomes it" : "Arrives when you have a free inventory slot";''',
    '''  if (cur == null) w = k == @PKG@.GearLL.POLE && !@PKG@.GearCfg.LL_POLEKIT ? "Not handed out on this server - a pole a quest gives you becomes it" : (k == @PKG@.GearLL.CAN && !(@PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_KIT) ? "Not handed out on this server (lifelong.canKit)" : "Arrives when you have a free inventory slot");          // 0.3.12: + the can''')
rep('''public static String effect(int k, int p, int lv) {
''', '''public static String effect(int k, int p, int lv) {
  if (k == @PKG@.GearLL.CAN) {          // 0.3.12: the watering can's points
    if (p == @PKG@.GearLL.PK_CAP) return lv >= @PKG@.GearLL.PKMAX[p] ? "never runs dry" : "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.CAN_CAPP) + "% waterings per fill";
    if (p == @PKG@.GearLL.PK_GROW) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.CAN_GROW) + "% growth each time you water dry soil";
    if (p == @PKG@.GearLL.PK_LAST) return "soil stays wet " + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.CAN_LAST) + "% longer";
    if (p == @PKG@.GearLL.PK_BLOOM) return @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.CAN_BLOOM) + "% chance to fertilize dry soil you water";
  }
''')
before('''M(lpg, r"""
public void panel(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {''', r'''# 0.3.12 MAKE HARVESTER on the hoe / sickle panels (the multitool row's shape): before the gate opens greyed with the rebirth line; then your
# lifelong hoe + sickle (both on you) are named and merged by GearLife.harvest (its own checks again)
# fix round 2 (critic A1): the merge is irreversible and may drop lines / points - the row shows what is kept and lost (harvPreview), the pair
# drawn (hvKey = slot / id / fingerprint of both, like the multitool's mtKey), and the FIRST click only arms it ("Click again" within 8 s)
F(lpg, "public String hvKey;")
F(lpg, "public String hvArmKey;")
F(lpg, "public long hvArm;")
M(lpg, r"""
public void hvRow(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {
  String tx;
  String bl = "Make Harvester";
  boolean can = false;
  this.hvKey = null;
  String gate = @PKG@.GearLife.harvGate(u);
  if (gate != null) { tx = "Harvester: " + gate; bl = "Rebirth 1"; }
  else {
    Object[] c = @PKG@.GearLife.harvCheck(u, inv, pk, P);
    if (c[0] != null) tx = "Harvester (your hoe + sickle in one tool): " + (String) c[0];
    else {
      int[] ha = (int[]) c[1];
      int[] sa = (int[]) c[2];
      @IS@ h = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
      @IS@ s = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
      String key = pairKey(inv, new int[] { ha[0], ha[1], sa[0], sa[1] });
      boolean armed = key != null && key.equals(this.hvArmKey) && System.currentTimeMillis() - this.hvArm < 8000L;
      String loss = @PKG@.GearLife.harvLoss(@PKG@.GearLife.harvPreview(u, inv, P, c));
      tx = (armed ? "Click again within 8 s - can't be undone: " : "Harvester: ") + @PKG@.Gear.itemName(h.getItemId()) + " + " + @PKG@.Gear.itemName(s.getItemId()) + " = " + @PKG@.Gear.itemName((String) c[3]) + (loss.length() > 0 ? " (" + loss + ")" : "") + ". Both are used up.";
      if (armed) bl = "Click again";
      this.hvKey = key;
      can = true;
    }
  }
  b.appendInline("#SkyyGPanel", "Group #SkyyGPHvRow { Anchor: (Height: 84); LayoutMode: Left; Label #SkyyGPHv { Anchor: (Width: 392); Text: \"\"; Style: (FontSize: 13, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); } Group { Anchor: (Width: 10); } TextButton #SkyyGPHvB { Anchor: (Width: 160, Height: 44); Text: \"" + bl + "\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set("#SkyyGPHv.Text", tx);
  ev.addEventBinding(@BT@.Activating, "#SkyyGPHvB", @EVD@.of("a", "hv:" + this.tok));
}""")
M(lpg, r"""
public void makeHv(@INV@ inv) {
  java.util.UUID u = this.playerRef.getUuid();
  String gate = @PKG@.GearLife.harvGate(u);
  if (gate != null) { this.info = "-" + gate; this.hvArmKey = null; return; }
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  Object[] c = @PKG@.GearLife.harvCheck(u, inv, pk, P);
  if (c[0] != null) { this.info = "-" + (String) c[0]; this.hvArmKey = null; return; }
  int[] ha = (int[]) c[1];
  int[] sa = (int[]) c[2];
  String key = pairKey(inv, new int[] { ha[0], ha[1], sa[0], sa[1] });
  if (key == null || this.hvKey == null || !key.equals(this.hvKey)) { this.info = "-Your tools changed - check the Harvester line and click again."; this.hvArmKey = null; return; }
  long now = System.currentTimeMillis();
  if (!key.equals(this.hvArmKey) || now - this.hvArm >= 8000L || now < this.hvArm) {          // fix round 2: the first click arms
    this.hvArmKey = key;
    this.hvArm = now;
    this.info = "=Check what the Harvester keeps and loses, then click again within 8 s - the merge can't be undone.";
    return;
  }
  this.hvArmKey = null;
  this.info = @PKG@.GearLife.harvest(this.playerRef, inv);
  if (this.info.startsWith("+")) this.sel = 3;
}""")
''')
rep('''  int k = this.sel < 0 || this.sel >= @PKG@.GearLL.KIND.length ? 0 : this.sel;          // 0.3.6: + the pole
''', '''  int k = this.sel < 0 || this.sel >= @PKG@.GearLL.KIND.length ? 0 : this.sel;          // 0.3.6: + the pole
  if (k == 2 && @PKG@.GearLL.merged(P)) { k = 3; this.sel = 3; }          // 0.3.12: the hoe lives on in the Harvester
''')
rep('''  b.set("#SkyyGPTitle.Text", "Your " + K + " - Upgrade Points");''',
    '''  b.set("#SkyyGPTitle.Text", "Your " + @PKG@.GearLL.kname(k, id).toLowerCase() + " - Upgrade Points");          // 0.3.12: "watering can", "harvester"''')
rep('''  if (k <= 1 && @PKG@.GearCfg.MULTI_ON && @PKG@.GearMerge.loaded()) mtRow(b, ev, u, inv);
''', '''  if (k <= 1 && @PKG@.GearCfg.MULTI_ON && @PKG@.GearMerge.loaded()) mtRow(b, ev, u, inv);
  if ((k == 2 || k == 3) && @PKG@.GearCfg.LL_ON && @PKG@.GearCfg.HARV_ON && !@PKG@.GearLL.merged(P)) hvRow(b, ev, u, inv, pk, P);          // 0.3.12
''')
rep('''  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) { if (k == @PKG@.GearLL.POLE && @PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) continue; row(b, ev, u, inv, pk, P, k); }''',
    '''  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) { if (!shown(k, P)) continue; row(b, ev, u, inv, pk, P, k); }          // 0.3.12: + the can; the hoe not after the Harvester merge''')
rep('''Tier them up with the Tier up button here or on the Anvil (the pole at the Fishing Bench). Lost one? /pickaxe, /hatchet, /hoe, /sickle or /pole.");''',
    '''Tier them up with the Tier up button here or on the Anvil (the pole at the Fishing Bench). Lost one? /pickaxe, /hatchet, /hoe, /sickle, /pole, /can or /harvester.");''')
rep('''    if (!cmd.equals("buy") && !cmd.equals("reset") && !cmd.equals("up") && !cmd.equals("mt")) { rebuild(); return; }''',
    '''    if (!cmd.equals("buy") && !cmd.equals("reset") && !cmd.equals("up") && !cmd.equals("mt") && !cmd.equals("hv")) { rebuild(); return; }''')
rep('''    } else if (cmd.equals("up") || cmd.equals("mt")) { rebuild(); return; }''', '''    } else if (cmd.equals("up") || cmd.equals("mt") || cmd.equals("hv")) { rebuild(); return; }''')
rep('''    if (cmd.equals("up") || cmd.equals("mt")) {''', '''    if (cmd.equals("up") || cmd.equals("mt") || cmd.equals("hv")) {''')
rep('''      else makeMt(inv0);''', '''      else if (cmd.equals("mt")) makeMt(inv0);
      else makeHv(inv0);          // 0.3.12''')
rep('''    nm = "Your lifelong " + @PKG@.GearLL.KNAME[k].toLowerCase() + " - " + @PKG@.Gear.itemName(id);''',
    '''    nm = "Your lifelong " + @PKG@.GearLL.kname(k, id).toLowerCase() + " - " + @PKG@.Gear.itemName(id);          // 0.3.12''')
rep('''      for (int k0 = 0; k0 < 4; k0++) if (P0.getProperty(@PKG@.GearLL.KIND[k0] + ".uid") != null) n0++;
''', '''      for (int k0 = 0; k0 < 4; k0++) if (P0.getProperty(@PKG@.GearLL.KIND[k0] + ".uid") != null) n0++;
      if (@PKG@.GearLL.merged(P0)) n0++;          // 0.3.12: the hoe lives on in the Harvester (still four kinds held)
''')

# ================================================================================================================ the commands: /can, /harvester
rep('''           ("PoleCmd", "pole", 4)]          # 0.3.5: the fishing pole''', '''           ("PoleCmd", "pole", 4),          # 0.3.5: the fishing pole
           ("CanCmd", "can", 5)]          # 0.3.12: the watering can''')
before('''for _cc, (_n, _c, _k) in zip(llcmds, LL_CMDS):''', '''C(llcmds[5], r"""
public CanCmd() {
  super("can", "Lost your lifelong watering can? Brings it back from a chest, the Vault or Requip, or makes an exact copy");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
''')
rep('''  getCommandRegistry().registerCommand(new @PKG@.PoleCmd());          // 0.3.5: the fishing pole''',
    '''  getCommandRegistry().registerCommand(new @PKG@.PoleCmd());          // 0.3.5: the fishing pole
  getCommandRegistry().registerCommand(new @PKG@.CanCmd());          // 0.3.12: the watering can (/harvester is registered further down)''')

# ================================================================================================================ GearTill: the Harvester tills an area too
rep('''  if (@PKG@.GearLL.kOf(id) != 2 || !id.equals(before.getItemId())) return -1;''',
    '''  if ((@PKG@.GearLL.kOf(id) != 2 && !@PKG@.GearLL.harv(id)) || !id.equals(before.getItemId())) return -1;          // 0.3.12: + the Harvester''')
# fix round 2 (critic B1): the Harvester's sickle SWING also costs 1 durability - a swing at a crop can leave the look target on the soil under it.
# A real till always has air above the soil it made; a crop / plant above = a swing, never the till ring
rep('''  if (blockAt(w.getChunkStore(), x, y, z) != TOI) { N[4] = N[4] + 1L; LASTWHY = "the target is no tilled soil"; return -1; }
''', '''  if (blockAt(w.getChunkStore(), x, y, z) != TOI) { N[4] = N[4] + 1L; LASTWHY = "the target is no tilled soil"; return -1; }
  if (@PKG@.GearLL.harv(id)) {          // 0.3.12 fix round 2
    int up0 = blockAt(w.getChunkStore(), x, y + 1, z);
    if (up0 != EMPTY && up0 != 0) { N[4] = N[4] + 1L; LASTWHY = "a Harvester swing (a plant above the soil)"; return -1; }
  }
''')

# ================================================================================================================ 1: the click (GearCan 2/2, GearCanWater) + /harvester
before('''# ####################################################################################################################################
# 0.3.10 ALWAYS ANSWER (tools/gear_0_3_10_patch.py 1A)''', r'''# ####################################################################################################################################
# 0.3.12 (tools/gear_0_3_12_patch.py): GearCan 2/2 (one watering: before / after vanilla's own UseWateringCan code, the soil, the refill),
# GearCanWater (the interaction type SkyyGearCan = a UseWateringCanInteraction with our numbers), GearCanSup (its codec's supplier), HarvCmd
# (/harvester); the plugin registers the type in setup() (FarmingPlugin's own way). Placed here: everything they call exists.
# ####################################################################################################################################
G312 = {"C2UW": "com.hypixel.hytale.builtin.adventure.farming.interactions.UseWateringCanInteraction",
        "C2CD": "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler",
        "C2WT": "com.hypixel.hytale.server.core.modules.time.WorldTimeResource",
        "C2TS": "com.hypixel.hytale.builtin.adventure.farming.states.TilledSoilBlock",
        "C2FB": "com.hypixel.hytale.builtin.adventure.farming.states.FarmingBlock",
        "C2BC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection",
        "C2FS": "com.hypixel.hytale.server.core.universe.world.chunk.section.FluidSection",
        "C2FL": "com.hypixel.hytale.server.core.asset.type.fluid.Fluid",
        "C2BCOD": "com.hypixel.hytale.codec.builder.BuilderCodec",
        "C2INT": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction",
        "C2ACM": "com.hypixel.hytale.assetstore.codec.AssetCodecMapCodec",
        "C2IST": "com.hypixel.hytale.protocol.InteractionState",
        "C2CU": "com.hypixel.hytale.math.util.ChunkUtil",
        "C2BE": "com.hypixel.hytale.server.core.modules.block.BlockEntity"}
for _k in G312:
    assert _k not in T, "0.3.12 token clashes: " + _k
T.update(G312)
for _c, _m in ((G312["C2UW"], "interactWithBlock"), (G312["C2UW"], "CODEC"), (G312["C2WT"], "getResourceType"), (G312["C2WT"], "getGameTime"),
               (G312["C2TS"], "getComponentType"), (G312["C2TS"], "getWateredUntil"), (G312["C2TS"], "isFertilized"), (G312["C2TS"], "setFertilized"),
               (G312["C2FB"], "getComponentType"), (G312["C2FB"], "getLastTickGameTime"), (G312["C2FB"], "setLastTickGameTime"),
               (G312["C2BC"], "getComponentType"), (G312["C2BC"], "getBlockReference"), (G312["C2BC"], "markBlockNeedsSaving"),
               (G312["C2FS"], "getComponentType"), (G312["C2FS"], "getFluidId"), (G312["C2FL"], "getAssetMap"), (G312["C2BCOD"], "builder"),
               (G312["C2INT"], "CODEC"), (G312["C2IST"], "Failed"), (G312["C2CU"], "indexBlock"), (G312["C2CU"], "chunkCoordinate"),
               (G312["C2BE"], "declaresComponent"), (T["ICTX"], "getEntity"), (T["ICTX"], "getHeldItem"), (T["ICTX"], "setHeldItem"),
               (T["ICTX"], "getHeldItemContainer"), (T["ICTX"], "getHeldItemSlot"), (T["ICTX"], "getState"), (T["HRC"], "getHorizontalAxisDirection"),
               (T["TC"], "getPosition"), (T["BSECT"], "setTicking"), (T["BSECT"], "scheduleTick"), (T["BSECT"], "getFiller"),
               (IS, "withDurability"), (CB, "getResource"), (CB, "getComponent"), (JP, "getCodecRegistry")):
    B.probe(pool, _c, _m)
# the engine shapes this round depends on (VERIFIED bytecode 2026-10-16, Hytale 0.7.2)
_uw = pool.get(G312["C2UW"])
for _f, _ty in (("radiusX", "int"), ("radiusZ", "int"), ("duration", "long")):
    _fd = _uw.getDeclaredField(_f)
    assert str(_fd.getType().getName()) == _ty and J0["Modifier"].isProtected(_fd.getModifiers()), "UseWateringCanInteraction.%s is no protected %s" % (_f, _ty)
_iwb = [m for m in _uw.getDeclaredMethods() if str(m.getName()) == "interactWithBlock"]
assert len(_iwb) == 1 and str(_iwb[0].getSignature()) == "(Lcom/hypixel/hytale/server/core/universe/world/World;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/protocol/InteractionType;Lcom/hypixel/hytale/server/core/entity/InteractionContext;Lcom/hypixel/hytale/server/core/inventory/ItemStack;Lorg/joml/Vector3i;Lcom/hypixel/hytale/server/core/modules/interaction/interaction/CooldownHandler;)V", "UseWateringCanInteraction.interactWithBlock changed"
assert [str(c.getSignature()) for c in _uw.getDeclaredConstructors()] == ["()V"], "UseWateringCanInteraction() changed"
_wba = _calls(G312["C2UW"], "waterBlockAt")
assert "TilledSoilBlock.setWateredUntil" in _wba and "BlockSection.setTicking" in _wba and "BlockSection.scheduleTick" in _wba, "vanilla waterBlockAt changed"
_iw = _calls(G312["C2UW"], "interactWithBlock")
assert "HeadRotation.getHorizontalAxisDirection" in _iw and "WorldTimeResource.getGameTime" in _iw and "InteractionSyncData.state" in _iw, "vanilla UseWateringCan.interactWithBlock changed"
assert "UseWateringCan" in _calls("com.hypixel.hytale.builtin.adventure.farming.FarmingPlugin", "setup"), "FarmingPlugin no longer registers UseWateringCan in setup()"
_fsi = _calls("com.hypixel.hytale.builtin.adventure.farming.interactions.FertilizeSoilInteraction", "interactWithBlock")
assert "TilledSoilBlock.setFertilized" in _fsi and "BlockSection.setTicking" in _fsi, "vanilla FertilizeSoil changed"
_tf = _calls("com.hypixel.hytale.builtin.adventure.farming.FarmingUtil", "tickFarming")
assert "FarmingBlock.getLastTickGameTime" in _tf and "FarmingBlock.setGrowthProgress" in _tf, "vanilla tickFarming no longer grows by the time since the last tick"
_cr = [str(m.getSignature()) for m in pool.get(JP).getMethods() if str(m.getName()) == "getCodecRegistry"]
assert "(Lcom/hypixel/hytale/assetstore/codec/AssetCodecMapCodec;)Lcom/hypixel/hytale/server/core/plugin/registry/CodecMapRegistry$Assets;" in _cr, _cr
assert str(pool.get(G312["C2INT"]).getField("CODEC").getType().getName()) == G312["C2ACM"], "Interaction.CODEC is no AssetCodecMapCodec"
# ---- GearCan 2/2: the click
for _f in ("public static final Object[] STOP = new Object[] { \"stop\" };",
           # HARNESS SEAMS ONLY (null in the game): CTX Object[] { "pr" | "held" | "set", IS | "fail" | "failed" | "time" | "axis" | "eye" };
           # SOIL Object[] { "get" | "fert" | "grow", x, y, z(, Long sec) }; FLUID Object[] { x, y, z } -> Boolean; RNG
           "public static volatile java.util.function.Function CTX = null;", "public static volatile java.util.function.Function SOIL = null;",
           "public static volatile java.util.function.Function FLUID = null;", "public static volatile java.util.Random RNG = null;",
           "public static volatile java.util.function.Function SUPER = null;",
           "public static volatile int WAT = -2;", "public static volatile int WSRC = -2;"):
    F(gcan, _f)
M(gcan, r"""
public static @PR@ prOf(@CB@ cb, @ICTX@ ctx) {
  java.util.function.Function f = CTX;
  if (f != null) { Object o = f.apply(new Object[] { "pr" }); return o instanceof @PR@ ? (@PR@) o : null; }
  if (cb == null || ctx == null) return null;
  @REF@ r = ctx.getEntity();
  if (r == null || !r.isValid()) return null;
  return (@PR@) cb.getComponent(r, @PR@.getComponentType());
}""")
M(gcan, r"""
public static @IS@ held(@ICTX@ ctx, @IS@ item) {
  java.util.function.Function f = CTX;
  if (f != null) { Object o = f.apply(new Object[] { "held" }); return o instanceof @IS@ ? (@IS@) o : item; }
  if (ctx == null) return item;
  @IS@ h = ctx.getHeldItem();
  return h != null ? h : item;
}""")
M(gcan, r"""
public static boolean setHeld(@ICTX@ ctx, @IS@ ns) {
  java.util.function.Function f = CTX;
  if (f != null) { f.apply(new Object[] { "set", ns }); return true; }
  if (ctx == null || ns == null) return false;
  @IC@ c = ctx.getHeldItemContainer();
  if (c == null) return false;
  Object tx = c.setItemStackForSlot((short) ctx.getHeldItemSlot(), ns);
  if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) return false;
  ctx.setHeldItem(ns);
  return true;
}""")
M(gcan, r"""
public static void fail(@ICTX@ ctx) {
  java.util.function.Function f = CTX;
  if (f != null) { f.apply(new Object[] { "fail" }); return; }
  if (ctx == null || ctx.getState() == null) return;
  ctx.getState().state = @C2IST@.Failed;
}""")
M(gcan, r"""
public static boolean failed(@ICTX@ ctx) {
  java.util.function.Function f = CTX;
  if (f != null) return Boolean.TRUE.equals(f.apply(new Object[] { "failed" }));
  return ctx != null && ctx.getState() != null && ctx.getState().state == @C2IST@.Failed;
}""")
M(gcan, r"""
public static java.time.Instant gameTime(@CB@ cb) {
  java.util.function.Function f = CTX;
  if (f != null) { Object o = f.apply(new Object[] { "time" }); return o instanceof java.time.Instant ? (java.time.Instant) o : null; }
  if (cb == null) return null;
  @C2WT@ wt = (@C2WT@) cb.getResource(@C2WT@.getResourceType());
  return wt == null ? null : wt.getGameTime();
}""")
# vanilla's facing: the horizontal axis of the head (no head = z -1)
M(gcan, r"""
public static int[] axis(@CB@ cb, @ICTX@ ctx) {
  java.util.function.Function f = CTX;
  if (f != null) { Object o = f.apply(new Object[] { "axis" }); if (o instanceof int[]) return (int[]) o; return new int[] { 0, -1 }; }
  try {
    @HRC@ hr = (@HRC@) cb.getComponent(ctx.getEntity(), @HRC@.getComponentType());
    if (hr != null) {
      @VECI@ v = hr.getHorizontalAxisDirection();
      if (v != null) return new int[] { v.x(), v.z() };
    }
  } catch (Throwable t) { }
  return new int[] { 0, -1 };
}""")
M(gcan, r"""
public static double[] eye(@CB@ cb, @ICTX@ ctx) {
  java.util.function.Function f = CTX;
  if (f != null) { Object o = f.apply(new Object[] { "eye" }); if (o instanceof double[]) return (double[]) o; return null; }
  try {
    @TC@ tc = (@TC@) cb.getComponent(ctx.getEntity(), @TC@.getComponentType());
    if (tc == null) return null;
    @VEC@ p = tc.getPosition();
    return new double[] { p.x, p.y + 1.62, p.z };
  } catch (Throwable t) { return null; }
}""")
M(gcan, r"""
public static int fluidId(String n) {
  try {
    int i = @C2FL@.getAssetMap().getIndex(n);
    return i == Integer.MIN_VALUE ? -1 : i;
  } catch (Throwable t) { return -1; }
}""")
# water (Water / Water_Source, the vanilla can's AllowedFluids) at a block (loaded sections only)
M(gcan, r"""
public static boolean isWater(@WLD@ w, int x, int y, int z) {
  java.util.function.Function f = FLUID;
  if (f != null) return Boolean.TRUE.equals(f.apply(new Object[] { Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) }));
  if (w == null || y < 0 || y >= 320) return false;
  if (WAT == -2) { WAT = fluidId("Water"); WSRC = fluidId("Water_Source"); }
  @CHST@ cs = w.getChunkStore();
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (r == null || !r.isValid()) return false;
  @C2FS@ fs = (@C2FS@) cs.getStore().getComponent(r, @C2FS@.getComponentType());
  if (fs == null) return false;
  int id = fs.getFluidId(x, y, z);
  return id >= 0 && (id == WAT || id == WSRC);
}""")
# THE REFILL CHECK: water right above the block you look at, or between your eye and it (vanilla's fill raycast, in 0.25 block steps)
M(gcan, r"""
public static boolean water(@WLD@ w, @CB@ cb, @ICTX@ ctx, @VECI@ pos) {
  int tx = pos.x();
  int ty = pos.y();
  int tz = pos.z();
  if (isWater(w, tx, ty + 1, tz)) return true;
  double[] e = eye(cb, ctx);
  if (e == null) return false;
  double cx = (double) tx + 0.5 - e[0];
  double cy = (double) ty + 0.5 - e[1];
  double cz = (double) tz + 0.5 - e[2];
  double len = Math.sqrt(cx * cx + cy * cy + cz * cz);
  if (len < 0.01 || len > 12.0) return false;
  int n = (int) (len / 0.25);
  int lx = Integer.MIN_VALUE;
  int ly = Integer.MIN_VALUE;
  int lz = Integer.MIN_VALUE;
  for (int i = 1; i < n; i++) {
    double q = (double) i / (double) n;
    int bx = (int) Math.floor(e[0] + cx * q);
    int by = (int) Math.floor(e[1] + cy * q);
    int bz = (int) Math.floor(e[2] + cz * q);
    if (bx == tx && by == ty && bz == tz) break;
    if (bx == lx && by == ly && bz == lz) continue;
    lx = bx;
    ly = by;
    lz = bz;
    if (isWater(w, bx, by, bz)) return true;
  }
  return false;
}""")
# the tilled soil vanilla waters for x / y / z (at y, else y - 1): Object[] { Instant wateredUntil, Boolean fertilized, Integer soil y,
# TilledSoilBlock, BlockSection, BlockComponentSection, Integer index, Store } or null (no soil / not loaded)
M(gcan, r"""
public static Object[] soil(@WLD@ w, int x, int y, int z) {
  java.util.function.Function f = SOIL;
  if (f != null) { Object o = f.apply(new Object[] { "get", Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) }); if (o instanceof Object[]) return (Object[]) o; return null; }
  if (w == null) return null;
  @CHST@ cs = w.getChunkStore();
  @ST@ store = cs.getStore();
  for (int dy = 0; dy >= -1; dy--) {
    int yy = y + dy;
    if (yy < 0 || yy >= 320) continue;
    @REF@ sec = cs.getChunkSectionReferenceAtBlock(x, yy, z);
    if (sec == null || !sec.isValid()) continue;
    @BSECT@ bs = (@BSECT@) store.getComponent(sec, @BSECT@.getComponentType());
    @C2BC@ bc = (@C2BC@) store.getComponent(sec, @C2BC@.getComponentType());
    if (bs == null || bc == null) continue;
    int idx = @C2CU@.indexBlock(x, yy, z);
    if (bs.getFiller(idx) != 0) continue;
    @BTYP@ bt = (@BTYP@) @BTYP@.getAssetMap().getAsset(bs.get(idx));
    if (bt == null || !@C2BE@.declaresComponent(bt, @C2TS@.getComponentType())) continue;
    @REF@ br = bc.getBlockReference(idx);
    @C2TS@ t = br == null || !br.isValid() ? null : (@C2TS@) store.getComponent(br, @C2TS@.getComponentType());
    return new Object[] { t == null ? null : t.getWateredUntil(), Boolean.valueOf(t != null && t.isFertilized()), Integer.valueOf(yy), t, bs, bc, Integer.valueOf(idx), store };
  }
  return null;
}""")
M(gcan, r"""
public static void tickAbove(@WLD@ w, @BSECT@ bs, int x, int y, int z) {
  if (@C2CU@.chunkCoordinate(y) == @C2CU@.chunkCoordinate(y + 1)) { bs.setTicking(x, y + 1, z, true); return; }
  if (w == null || y + 1 >= 320) return;
  @CHST@ cs = w.getChunkStore();
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y + 1, z);
  if (r == null || !r.isValid()) return;
  @BSECT@ b2 = (@BSECT@) cs.getStore().getComponent(r, @BSECT@.getComponentType());
  if (b2 != null) b2.setTicking(x, y + 1, z, true);
}""")
# BLOOM = vanilla FertilizeSoilInteraction on that soil (setFertilized + the soil and the block above tick)
M(gcan, r"""
public static boolean fert(@WLD@ w, Object[] s, int x, int z) {
  java.util.function.Function f = SOIL;
  if (f != null) return Boolean.TRUE.equals(f.apply(new Object[] { "fert", Integer.valueOf(x), s[2], Integer.valueOf(z) }));
  if (s == null || !(s[3] instanceof @C2TS@)) return false;
  int y = ((Integer) s[2]).intValue();
  @C2TS@ t = (@C2TS@) s[3];
  @BSECT@ bs = (@BSECT@) s[4];
  @C2BC@ bc = (@C2BC@) s[5];
  int idx = ((Integer) s[6]).intValue();
  t.setFertilized(true);
  bc.markBlockNeedsSaving(idx);
  bs.setTicking(x, y, z, true);
  tickAbove(w, bs, x, y, z);
  return true;
}""")
# GROWTH BOOST: the crop above the soil ticks as if sec more game seconds had passed (FarmingBlock.lastTickGameTime back by sec; the engine's own
# tickFarming turns the time into growth, stage by stage) and ticks now
M(gcan, r"""
public static boolean grow(@WLD@ w, Object[] s, int x, int z, long sec, java.time.Instant now) {
  java.util.function.Function f = SOIL;
  if (f != null) return Boolean.TRUE.equals(f.apply(new Object[] { "grow", Integer.valueOf(x), s[2], Integer.valueOf(z), Long.valueOf(sec) }));
  if (w == null || s == null || sec <= 0L) return false;
  int y = ((Integer) s[2]).intValue() + 1;
  if (y >= 320) return false;
  @CHST@ cs = w.getChunkStore();
  @ST@ store = cs.getStore();
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (r == null || !r.isValid()) return false;
  @BSECT@ bs = (@BSECT@) store.getComponent(r, @BSECT@.getComponentType());
  @C2BC@ bc = (@C2BC@) store.getComponent(r, @C2BC@.getComponentType());
  if (bs == null || bc == null) return false;
  int idx = @C2CU@.indexBlock(x, y, z);
  @REF@ br = bc.getBlockReference(idx);
  if (br == null || !br.isValid()) return false;
  @C2FB@ fb = (@C2FB@) store.getComponent(br, @C2FB@.getComponentType());
  if (fb == null) return false;
  java.time.Instant lt = fb.getLastTickGameTime();
  if (lt == null) return false;
  fb.setLastTickGameTime(lt.minusSeconds(sec));
  bc.markBlockNeedsSaving(idx);
  bs.setTicking(x, y, z, true);
  if (now != null) bs.scheduleTick(idx, now);
  return true;
}""")
# the cells vanilla waters for this click (its own loop: width centred, depth away from you), each with "was it wet already"
M(gcan, r"""
public static java.util.ArrayList cells(@WLD@ w, @CB@ cb, @ICTX@ ctx, @VECI@ pos, int side, java.time.Instant now) {
  java.util.ArrayList out = new java.util.ArrayList();
  int[] ax = axis(cb, ctx);
  int ax0 = ax[0];
  int az0 = ax[1];
  if (ax0 != 0 && az0 != 0) ax0 = 0;
  int fx = az0 != 0 ? 1 : 0;
  int fz = ax0 != 0 ? 1 : 0;
  int rx = side < 1 ? 1 : side;
  int lo = (rx - 1) / 2;
  int hi = rx - 1 - lo;
  for (int dz = 0; dz < rx; dz++) {
    for (int dx = -lo; dx <= hi; dx++) {
      int x = pos.x() + dx * fx + dz * ax0;
      int z = pos.z() + dx * fz + dz * az0;
      Object[] s = soil(w, x, pos.y(), z);
      boolean wet = s != null && s[0] instanceof java.time.Instant && now != null && ((java.time.Instant) s[0]).isAfter(now);
      out.add(new Object[] { new int[] { x, pos.y(), z }, Boolean.valueOf(wet), Boolean.valueOf(s != null) });          // fix round: [2] = tilled soil
    }
  }
  return out;
}""")
M(gcan, r"""
public static double roll() {
  java.util.Random r = RNG;
  return r != null ? r.nextDouble() : java.util.concurrent.ThreadLocalRandom.current().nextDouble();
}""")
M(gcan, r"""
public static void tell(@PR@ pr, String key, String text, long gap) {
  if (pr != null) @PKG@.GearLife.tellOnce(pr, key, text, gap);
}""")
# BEFORE vanilla's watering (GearCanWater, world thread): null = not our can (vanilla runs as it is); STOP = handled (a refill or a refusal);
# else Object[] { "water", Integer side, Long wet seconds, Instant now, ArrayList cells, double[] plan, PR, IS held }
M(gcan, r"""
public static Object[] before(@WLD@ w, @CB@ cb, @ICTX@ ctx, @IS@ item, @VECI@ pos) {
  @IS@ held = held(ctx, item);
  if (held == null || held.isEmpty() || !@PKG@.GearData.can(held.getItemId())) return null;
  N[0] = N[0] + 1L;
  @PR@ pr = prOf(cb, ctx);
  if (!@PKG@.GearCfg.CAN_ON) { N[9] = N[9] + 1L; fail(ctx); tell(pr, "canoff", "Watering cans are switched off on this server.", 5000L); return STOP; }
  if (pr == null || pos == null) { fail(ctx); return STOP; }
  java.util.UUID u = pr.getUuid();
  @BD@ d = null;
  try { d = @PKG@.GearData.gearDoc(held.getMetadata()); } catch (Throwable t) { d = null; }
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d) && !@PKG@.GearLL.mine(u, d)) {
    N[3] = N[3] + 1L;
    fail(ctx);
    tell(pr, "cannotyours", @PKG@.GearLL.isRt(d) ? "This watering can is retired - hold it and type /lifelong to swap it back." : "That is another player's watering can - it waters nothing for you. Yours: /can", 3000L);
    return STOP;
  }
  if (water(w, cb, ctx, pos)) {
    double mx = held.getMaxDurability();
    if (held.getDurability() < mx) setHeld(ctx, held.withDurability(mx));
    N[1] = N[1] + 1L;
    tell(pr, "canfull", "Your watering can is full.", 4000L);
    return STOP;
  }
  // fix round (hold-and-sweep): a repeat while the button is held runs only on a NEW block
  long ms = System.currentTimeMillis();
  long[] lt = (long[]) LAST.get(u);
  boolean rep = lt != null && ms >= lt[3] && ms - lt[3] < holdMs();          // fix round 2: can.holdSec (Server Setup)
  boolean same = rep && lt[0] == (long) pos.x() && lt[1] == (long) pos.y() && lt[2] == (long) pos.z();
  LAST.put(u, new long[] { (long) pos.x(), (long) pos.y(), (long) pos.z(), ms });
  if (same) { N[10] = N[10] + 1L; return STOP; }
  double[] pl = @PKG@.GearCan.plan(u, held.getItemId(), d, held.getMaxDurability());
  if (pl[2] > 0.0 && held.getDurability() < EMPTY_AT) {
    N[2] = N[2] + 1L;
    fail(ctx);
    tell(pr, "canempty", "Your watering can is empty - right-click water to fill it.", 3000L);
    return STOP;
  }
  java.time.Instant now = gameTime(cb);
  int sd = (int) pl[0];
  java.util.ArrayList cs = cells(w, cb, ctx, pos, sd, now);
  if (rep) {          // fix round: sweeping over soil this can already wet = nothing to do, no water used
    boolean dry = false;
    for (int i = 0; i < cs.size() && !dry; i++) {
      Object[] e = (Object[]) cs.get(i);
      if (Boolean.TRUE.equals(e[2]) && !Boolean.TRUE.equals(e[1])) dry = true;
    }
    if (!dry) { N[11] = N[11] + 1L; return STOP; }
  }
  return new Object[] { "water", Integer.valueOf(sd), Long.valueOf((long) pl[1]), now, cs, pl, pr, held };
}""")
# AFTER vanilla's watering: nothing watered (Failed) = no water used; every soil THIS click made wet that was dry before gets the Bloom roll and
# the Growth Boost; the water bar goes down (the top Capacity never). int[] { wet now, dry before, bloomed, grown } or null
M(gcan, r"""
public static int[] after(@WLD@ w, @CB@ cb, @ICTX@ ctx, @IS@ item, @VECI@ pos, Object[] st) {
  if (failed(ctx)) { N[8] = N[8] + 1L; return null; }
  java.time.Instant now = (java.time.Instant) st[3];
  long dur = ((Long) st[2]).longValue();
  java.time.Instant until = now == null ? null : now.plusSeconds(dur);
  double[] pl = (double[]) st[5];
  @PR@ pr = (@PR@) st[6];
  @IS@ h0 = (@IS@) st[7];
  java.util.ArrayList cs = (java.util.ArrayList) st[4];
  int wet = 0;
  int fresh = 0;
  int bl = 0;
  int gr = 0;
  for (int i = 0; i < cs.size(); i++) {
    Object[] e = (Object[]) cs.get(i);
    int[] c = (int[]) e[0];
    Object[] s = soil(w, c[0], c[1], c[2]);
    if (s == null || until == null || !(s[0] instanceof java.time.Instant) || !until.equals(s[0])) continue;
    wet++;
    if (Boolean.TRUE.equals(e[1])) continue;
    fresh++;
    if (pl[4] > 0.0 && !Boolean.TRUE.equals(s[1]) && roll() * 100.0 < pl[4] && fert(w, s, c[0], c[2])) bl++;
    if (pl[3] >= 1.0 && grow(w, s, c[0], c[2], (long) pl[3], now)) gr++;
  }
  @IS@ h = held(ctx, item);
  if (pl[2] > 0.0) {
    if (h != null && h0 != null && h.getItemId().equals(h0.getItemId())) {
      double left = h.getDurability() - pl[2];
      if (left < EMPTY_AT) left = EMPTY;          // fix round: never 0 (EMPTY = empty, still refillable)
      setHeld(ctx, h.withDurability(left));
      if (left < EMPTY_AT) tell(pr, "candry", "Your watering can is empty now - right-click water to fill it.", 3000L);
    }
  } else N[7] = N[7] + 1L;
  N[4] = N[4] + (long) fresh;
  N[5] = N[5] + (long) bl;
  N[6] = N[6] + (long) gr;
  if (bl > 0) tell(pr, "canbloom", "Bloom! Your watering can fertilized " + bl + " soil block" + (bl == 1 ? "" : "s") + ".", 2000L);
  return new int[] { wet, fresh, bl, gr };
}""")
M(gcan, r"""
public static String statusText() {
  return "watering can " + (@PKG@.GearCfg.CAN_ON ? "on" : "OFF (part.can)") + " (interaction type SkyyGearCan " + (REG ? "registered" : "NOT registered: " + REG_WHY) + "; kit " + (@PKG@.GearCfg.CAN_KIT ? "on" : "off") + ", squares " + @PKG@.GearCfg.CAN_AREA + ", waterings " + @PKG@.GearCfg.CAN_USES + ", wet " + @PKG@.GearCfg.CAN_SEC + " s, vanilla recipe " + (@PKG@.GearCfg.CAN_NOVAN ? "refused" : "allowed") + "; clicks " + N[0] + ", refills " + N[1] + ", empty " + N[2] + ", dry soils watered " + N[4] + ", bloomed " + N[5] + ", grown " + N[6] + ", hold repeats skipped " + (N[10] + N[11]) + "); Harvester " + (@PKG@.GearCfg.HARV_ON ? "on" + (@PKG@.GearCfg.HARV_RBGATE ? " after rebirth 1" : " (no rebirth gate)") : "OFF (part.harvester)") + " (made " + @PKG@.GearLife.HV[0] + ", finished at a look " + @PKG@.GearLife.HV[3] + "); cans given " + @PKG@.GearLife.CK[0] + "; Health regen via skill:fn:hpregen " + (@PKG@.Gear.fn("skill:fn:hpregen") != null ? "on" : "not loaded (Gear heals it)");
}""")
# ---- GearCanWater: the interaction type (UseWateringCanInteraction's codec keys, vanilla's watering code)
gcw = mk("GearCanWater", G312["C2UW"])
gcs = mk("GearCanSup")
hvc = mk("HarvCmd", APC)
G312_CLASSES += [gcw, gcs, hvc]
C(gcw, "public GearCanWater() { super(); }")
F(gcw, "public static volatile @C2BCOD@ SKCODEC = null;")
F(gcw, "public static final long[] N = new long[3];")          # 0 waterings run, 1 vanilla fallbacks (not our can / a failure before), 2 failures after
# vanilla's watering with OUR numbers for this one call: the interaction asset is ONE object shared by every world thread - synchronized, the
# fields put back in finally
M(gcw, r"""
public synchronized void waterAs(@WLD@ w, @CB@ cb, @ITYPE@ type, @ICTX@ ctx, @IS@ item, @VECI@ pos, @C2CD@ cd, int side, long dur) {
  java.util.function.Function sf = @PKG@.GearCan.SUPER;
  if (sf != null) { sf.apply(new Object[] { pos, Integer.valueOf(side), Long.valueOf(dur) }); return; }
  int ox = this.radiusX;
  int oz = this.radiusZ;
  long od = this.duration;
  this.radiusX = side;
  this.radiusZ = side;
  this.duration = dur;
  try { super.interactWithBlock(w, cb, type, ctx, item, pos, cd); }
  finally { this.radiusX = ox; this.radiusZ = oz; this.duration = od; }
}""")
M(gcw, r"""
protected void interactWithBlock(@WLD@ w, @CB@ cb, @ITYPE@ type, @ICTX@ ctx, @IS@ item, @VECI@ pos, @C2CD@ cd) {
  Object[] st = null;
  try { st = @PKG@.GearCan.before(w, cb, ctx, item, pos); } catch (Throwable t) { st = null; @PKG@.Gear.warnOnce("canbefore", "watering can: the click could not be read (vanilla's own watering ran; logged once): " + t); }
  if (st == null) { N[1] = N[1] + 1L; super.interactWithBlock(w, cb, type, ctx, item, pos, cd); return; }
  if (!"water".equals(st[0])) return;
  N[0] = N[0] + 1L;
  waterAs(w, cb, type, ctx, item, pos, cd, ((Integer) st[1]).intValue(), ((Long) st[2]).longValue());
  try { @PKG@.GearCan.after(w, cb, ctx, item, pos, st); } catch (Throwable t2) { N[2] = N[2] + 1L; @PKG@.Gear.warnOnce("canafter", "watering can: after the watering (logged once): " + t2); }
}""")
gcs.addInterface(pool.get("java.util.function.Supplier"))
C(gcs, "public GearCanSup() { }")
M(gcs, "public Object get() { return new @PKG@.GearCanWater(); }")
M(gcw, r"""
public static @C2BCOD@ codec() {
  @C2BCOD@ c = SKCODEC;
  if (c != null) return c;
  c = @C2BCOD@.builder(@PKG@.GearCanWater.class, new @PKG@.GearCanSup(), @C2UW@.CODEC).build();
  SKCODEC = c;
  return c;
}""")
C(hvc, r"""
public HarvCmd() {
  super("harvester", "Lost your Harvester? Brings it back from a chest, the Vault or Requip, or makes an exact copy");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hvc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Gear] no player found")); return; }
    java.util.Properties P = @PKG@.GearLL.reg(@PKG@.Gear.pkey(pr.getUuid()));
    String r;
    if (!@PKG@.GearCfg.LL_ON) r = "-Lifelong tools are switched off on this server.";
    else if (!@PKG@.GearLL.merged(P)) r = "-You have no Harvester yet - make it on the Tools tab (/toolpoints) from your lifelong hoe and sickle" + (@PKG@.GearCfg.HARV_RBGATE ? " after your first rebirth" : "") + ".";
    else r = @PKG@.GearLife.reclaimW(pr, p, 3, world);
    pr.sendMessage(@MSG@.raw("[Gear] " + @PKG@.GearUi.infoText(r)).color(@PKG@.GearUi.infoColor(r)));
  } catch (Throwable t) {
    @PKG@.Gear.warn("/harvester failed: " + t);
    pr.sendMessage(@MSG@.raw("[Gear] That did not work - the server log has the details."));
  }
}""")
# the plugin: the interaction type in setup() (before the asset packs load - FarmingPlugin registers "UseWateringCan" the same way), the
# status at start, the hpregen source dropped at shutdown
pl.getDeclaredMethod("setup").insertAfter(J("""{
  try {
    @C2ACM@ acm = @C2INT@.CODEC;
    getCodecRegistry(acm).register("SkyyGearCan", @PKG@.GearCanWater.class, @PKG@.GearCanWater.codec());
    @PKG@.GearCan.REG = true;
    @PKG@.GearCan.REG_WHY = "registered";
  } catch (Throwable tcw) {
    @PKG@.GearCan.REG = false;
    @PKG@.GearCan.REG_WHY = String.valueOf(tcw);
    @PKG@.Gear.warn("the watering can interaction type SkyyGearCan could not be registered (" + tcw + ") - lifelong watering cans water nothing");
  }
}"""))
pl.getDeclaredMethod("setup").insertAfter(J("{ try { getCommandRegistry().registerCommand(new @PKG@.HarvCmd()); } catch (Throwable thv) { @PKG@.Gear.warn(\"/harvester could not be registered: \" + thv); } }"))          # 0.3.12
pl.getDeclaredMethod("start").insertAfter(J("""{
  try { @PKG@.Gear.info("[SkyyGear] 0.3.12: " + @PKG@.GearCan.statusText()); } catch (Throwable tst) { }
}"""))
pl.getDeclaredMethod("shutdown").insertBefore(J("{ try { @PKG@.GearFx.hpClear(); } catch (Throwable thc) { } }"))
_scl = _calls(PKG + ".SkyyGearPlugin", "setup")
assert "getCodecRegistry((Lcom/hypixel/hytale/assetstore/codec/AssetCodecMapCodec;)Lcom/hypixel/hytale/server/core/plugin/registry/CodecMapRegistry$Assets;)" in _scl and "CodecMapRegistry$Assets.register" in _scl, "setup() does not register SkyyGearCan through getCodecRegistry(AssetCodecMapCodec)"
print("0.3.12 watering can: GearCan / GearCanWater (SkyyGearCan) / GearCanSup, /can, /harvester, the Harvester merge on the Tools tab")
''')

# ================================================================================================================ fix round: SMITHING tab + Upgrade 8 a page
# Skyy 2026-10-16 "to avoid confusion, lets rename this craft tab to smithing." -> the /smithing CRAFT tab is the SMITHING tab (its tab label, the
# side heading, the one-tab title, the chat line and the Server Setup / player setting texts that name it); behaviour unchanged (the "Craft"
# BUTTON on a card still crafts)
rep('''    String nm = m == 3 ? "Craft" : (m == 0 ?''', '''    String nm = m == 3 ? "Smithing" : (m == 0 ?''')          # 0.3.12: Craft -> Smithing (Skyy 2026-10-16)
rep('''  @PKG@.GearUi.st(b, "#SkyyGCatH.Text", "Craft");''', '''  @PKG@.GearUi.st(b, "#SkyyGCatH.Text", "Smithing");          // 0.3.12 (Skyy 2026-10-16)''')
rep('''  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 3, 1066, "Craft");''', '''  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 3, 1066, "Smithing");''')
rep('''"[Smithing] The Craft tab is switched off on this server - opening Reforge."''', '''"[Smithing] The Smithing tab is switched off on this server - opening Reforge."''')
rep('''"Smithing Craft tab (/smithing)"''', '''"Smithing tab (/smithing)"''')
rep("""(the Craft tab's My class filter).""", """(the Smithing tab's My class filter).""")
rep('''"The Smithing Craft tab shows gear for every class, not only yours"''', '''"The Smithing tab shows gear for every class, not only yours"''')
# Skyy 2026-10-16 "scale these idons down just a little so 8 can fit on a page." -> the Upgrade tab: 8 rows a page (was 6) - row 70 (was 96) +
# gap 6 = 76 x 8 = 608 <= the 612 px list; icon cell 58 (was 84), the three lines 22 / 18 / 18 (fonts 16 / 13 / 13, shrink to 10), button 40
# high; the row keeps its width (58 + 14 + 786 = 84 + 14 + 760) and the page its height (fits 1080: the list box is unchanged)
rep('''      nrq++;
    }
  }
  int per = 6;
  int pages = (this.rows.size() + per - 1) / per;''', '''      nrq++;
    }
  }
  int per = 8;          // 0.3.12: 8 rows a page (Skyy 2026-10-16; was 6)
  int pages = (this.rows.size() + per - 1) / per;''')
_UR_OLD = r'''  b.appendInline("#SkyyGUList", "Group " + rid + " { Anchor: (Height: 96); LayoutMode: Left; Padding: (Full: 6); Background: #000000(0.25); " + @PKG@.GearUi.cell(84, id) + " Group { Anchor: (Width: 14); } Group { Anchor: (Width: 760); LayoutMode: Top; Label " + rid + "N { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); } Label " + rid + "A { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff(0.8), VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label " + rid + "B { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (can ? "#ffffff" : @PKG@.GearDefs.C_GOLD) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } Group { Anchor: (Width: 10); }" + (btn ? " TextButton " + rid + "U { Anchor: (Width: 170, Height: 44, Top: 20); Text: \"'''
_UR_NEW = r'''  b.appendInline("#SkyyGUList", "Group " + rid + " { Anchor: (Height: 70); LayoutMode: Left; Padding: (Full: 6); Background: #000000(0.25); " + @PKG@.GearUi.cell(58, id) + " Group { Anchor: (Width: 14); } Group { Anchor: (Width: 786); LayoutMode: Top; Label " + rid + "N { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label " + rid + "A { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 13, TextColor: #ffffff(0.8), VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); } Label " + rid + "B { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 13, RenderBold: true, TextColor: " + (can ? "#ffffff" : @PKG@.GearDefs.C_GOLD) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); } } Group { Anchor: (Width: 10); }" + (btn ? " TextButton " + rid + "U { Anchor: (Width: 170, Height: 40, Top: 9); Text: \"'''
rep(_UR_OLD, _UR_NEW)          # 0.3.12: 8 a page
assert 8 * (70 + 6) <= 612 and 22 + 18 + 18 <= 70 - 12 and 9 + 40 <= 70 - 12 and 58 + 14 + 786 == 84 + 14 + 760
print("0.3.12 fix round: the Smithing tab (was Craft), the Upgrade tab 8 rows a page (70 px rows)")

# ================================================================================================================ the manifest, the class list, the jar checks
rep('''can tier up (/upgrade); Server Setup -> Gear. Replaces SkyyRolls.''',
    '''can tier up (/upgrade); every profile gets a LIFELONG WATERING CAN (/can; Crude to Adamantite, each tier waters a bigger square of tilled soil - 1x1, 3x3, 5x5, 7x7 ...; right-click water to refill; its points: Capacity, Growth Boost, Lasting Water, Bloom); the lifelong hoe and sickle merge into one HARVESTER on the Tools tab (it tills and reaps; /harvester); a longsword shows SkyyArmory's Crescent Rush; Gear's Health regen runs through SkyySkills' skill:fn:hpregen; Server Setup -> Gear. Replaces SkyyRolls.''')
rep('''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')
rep('''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS)), "SkyyGear 0.3.6 ships the 8 mystery bags + the 16 Untiered copies + the 5 Sigils + the 68 gathering armor pieces"''',
    '''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS) + list(GA2_ITEMS) + list(CAN_ITEMS) + list(HARV_ITEMS)), "SkyyGear 0.3.12 ships the 8 mystery bags + the 16 Untiered copies + the 5 Sigils + the 68 gathering armor pieces + 6 watering cans + 4 Harvesters"
    for _k, _v in list(CAN_ITEMS.items()) + list(HARV_ITEMS.items()) + list(CAN_FILES.items()):          # 0.3.12
        assert _jz.read(_k) == (_v.encode("utf-8") if isinstance(_v, str) else _v), "watering can / Harvester file missing from the jar: " + _k''')

# ================================================================================================================ checks on the result
assert s.index("public static boolean canKit(") < s.index("public static void sweep0(")
assert s.index("public static boolean harvRecover(") < s.index("public static void sweep0(")
assert s.index("public static Object[] harvCheck(") < s.index("public void hvRow(")
assert s.index('gcan = mk("GearCan")') < s.index('gtool = mk("GearTool")')
assert s.index('G312 = {"C2UW"') < s.index("0.3.10 ALWAYS ANSWER (tools") < s.index("ALL = [gu, gdf, gcf")
assert s.count("registerCommand(new @PKG@.CanCmd())") == 1 and s.count("registerCommand(new @PKG@.HarvCmd())") == 1
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.11 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.11 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
