"""Derive SkyyGear/build_skyygear_0.3.11.py from the LIVE 0.3.10 (build_skyygear_0.3.10.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_10_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_11_patch.py      then      python SkyyGear/build_skyygear_0.3.11.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.11.py
(tools/skyyui.py had UNCOMMITTED kit 1.6 edits of another builder while this round was built: the build + harness ran through a scratch runner
that pre-loads `git show HEAD:tools/skyyui.py` as the skyyui module - tools/dev/scratch/gear0311/run_head_kit.py, deleted afterwards. The fix
round (2026-10-16) built with plain python: kit 1.6 was committed by then (b776a8d), so the working-tree kit IS the committed one.)

0.3.11 (2026-10-15, round "gear0311" = Skyy's test of a fresh profile; docs/answered/gear.md 2026-10-15 SICKLE = FIBER / STICK TOOL, FEWER
STICKS, FISHING ROD SPAWNS WITH YOU, NO WOODEN REEL, UPGRADE MENU; with SkyyFishing 0.1.7 + SkyyQuests 0.3.4):
1. THE SICKLE CUTS PLANTS (Skyy: "i had to make a crude sword to cut leave to get fiber because trees dont drop much. but i cant break the
   bushes and grass with it for some reason. lets mke the sickle break bushes, and make it the main tool for fiber / stick collection").
   WHY THE SWORD COULD NOT (VERIFIED bytecode BlockHarvestUtils.damageSingleBlock, Hytale 0.7.2 + Assets.zip): a sword's swing DOES try to
   break the blocks it sweeps (Selector HitBlock -> Block_Break_Adventure -> BreakBlock), but a SOFT block whose Gathering.Soft says
   "IsWeaponBreakable": false refuses every item that has a Weapon section - BEFORE the DamageBlockEvent (no mod can see that hit). 74 plant
   blocks say so: every Plant_Bush*, the brambles, vines, moss and three flowers. The vanilla SICKLE has a Weapon section too ("Weapon": {}),
   so it was refused the same way. Grass, ferns and leaves ARE weapon-breakable, but grass and ferns drop nothing ("DropList": "Empty") and
   leaves only Plant Fiber half the time - so cutting them looked useless.
   FIX (GearSickle): at start (and whenever the list changes) the plants of sickle.cuts (id starts, default bushes, brambles, bushy flowers,
   grass, ferns, leaves, vines, reeds, roots) that refuse weapons are made weapon-breakable on the SERVER (SoftBlockDropType.isWeaponBreakable,
   reflection; the original values are put back at shutdown / when a plant leaves the list), and GearToolHitSys cancels the hit of any OTHER
   weapon on exactly those plants (vanilla's rule for swords, axes, spears; the engine re-sends the block). Only sickles cut them.
   YIELD: each plant a sickle cuts (BreakBlockEvent with a Tool_Sickle_ in hand, checked on the next world tick that the block really went) gives
   EXTRA Plant Fiber (sickle.fiberChance 60 %) and on bushes / brambles extra Sticks (sickle.stickChance 35 %), both + sickle.perLevel
   0.5 % per tool level + sickle.perFortune 2 % per point of the sickle's Farming Fortune (100 % = one sure, the rest a chance; at most 5) -
   storage first, then hotbar / backpack, dropped at the feet when full (SkyySkills' double-drop give). Hands and swords get only the vanilla
   drops. SWEEP: the cut also takes the cut-list plants around it (sickle.sweep reach per tier Crude..Onyxium 1,1,2,2,3,3,4,4 = a 3x3 / 5x5 /
   ... square, sickle.sweepLayers 1 layer up and down, at most sickle.sweepMax 24,24,40,40,60,60,80,80 by tier, soft plants only - never logs, crops or blocks) through the engine's own
   BlockHarvestUtils.performBlockBreak exactly like its soft-block hit (the plant's Soft drop list, quantity 1 - a REAL BreakBlockEvent per
   plant: island protection, drops, Collections, XP apply; each swept plant gets its own bonus roll, but never sweeps again); on island worlds only where SkyyIslands' island:perm:fn says you may build, elsewhere while
   sickle.sweepElsewhere (default on). One sweep per player per 150 ms.
2. FEWER STICKS (Skyy: "id reduce the number of sticks you get a bit. i have more sticks than logs"). WHAT GIVES THEM (Assets.zip, read at build
   time): tree BRANCH blocks (Wood_*_Branch_*, drop list Wood_Branch: 1 stick on average - Oak trees have 1.3 branches per trunk block, so a
   felled oak gave more sticks than logs), ground stick piles (Wood_Sticks: 2-5 each), bushes (Plant_Bush: a stick half the time) and the berry
   bush (Plant_Bush_Berry_Red). Leaves give no sticks; SkyySkills' Fortune doubles only trunks (perk.foraging.doubleDropOnly=_Trunk). FIX
   (GearStick, our own code at runtime - no file overrides anything): the containers of the drop lists in sticks.lists get a wrapper that keeps
   each stick drop with sticks.keepPct 50 % (a 2-5 pile is scaled to 50 % of its amount) - EVERY way those lists roll (hand, hatchet, felled
   tree physics, SkyySkills' Fortune extras, SkyyCollections' felled-tree roll) goes through ItemModule.getRandomItemDrops -> the container
   (VERIFIED bytecode). The sickle's own extra sticks are not cut. Put back at shutdown / when a list leaves the row; 100 = vanilla.
3. THE FISHING POLE IN THE STARTING KIT (Skyy: "lets make the fishing rod spawn with you too. and it works swithout the hook line and sinker,
   so you can mess with it, then the quests later teach you how to use it better."): lifelong.poleKit (default on). Every profile gets its
   lifelong pole ONCE (registry key poleKit=1): a pole it already has (Marlow's, adopted) counts; a lifelong pole of the profile in the
   inventory is adopted; else the best plain rod it carries becomes it (the pickaxe migration's rule); else a Wooden Fishing Rod is GIVEN through
   the journalled give (GearLife.give2 "give": journal first, the same uid on a retry, never a second copy); no free slot = it waits with a line.
   The given pole is redrawn by SkyyFishing (fishing:fn:restamp) like every pole write. Without SkyyFishing nothing is given (asked again later).
   The Tools tab / /pole say it arrives with a free slot (not "from Marlow"). gear:fn:poleRule (Boolean: lifelong tools + poleKit + noCraft
   on) tells SkyyFishing 0.1.7 to refuse the bench's Wooden Fishing Rod (one pole per profile; the Copper / Iron rods are its tier-ups).
4. THE UPGRADE TAB (Skyy: "to make it easier id make the upgrades their own menu since tons of tools and gear upgrade now"): /smithing gets
   UPGRADE next to Craft | Anvil | Identify | Tools (smith.upgradeTab, default on; /upgrade and SkyyMenu's gear:fn:smithing "upgrade" open
   it). ONE list of everything you carry (hotbar, armor worn, tools, utility, storage, backpack - GearUp.rows) that has a next tier: your
   lifelong tools first, then armor, then the rest, then (fix round) your gear IN Requip (the Anvil's rows: "Take out" = wardrobe:fn:fetch, then
   it tiers up like the rest); each row = the item (rarity colour), "T2 Copper -> T3 Iron: Iron Pickaxe", the cost with
   have / need (inventory + Magic Bags; gold when short or why not) and a Tier up button = GearUp.upgrade (the Anvil's own tier-up: check,
   skill gate, materials storage first then the bags, restore on any failure, UPGRADE-BEGIN on disk first, sound, quest event). Lifelong tools
   that are not on you show "Not on you - /pickaxe brings it back"; the pole shows "T1 Crude -> T2 Copper: Copper Fishing Rod" (fix round; it
   tiers up at SkyyFishing's bench - Parts - so it has no button here) or "top tier". 6 rows a page (Prev / Next).
   Each build gives its buttons a new click token (LifePage.nextTok): a click counts only with the current token, used up BEFORE anything is
   spent (a double click tiers up once); every click is answered (the page joins the 0.3.10 always-answer pages). The Anvil keeps Reforge and
   its own Upgrade; the Tools tab keeps its Tier up.
SAVED DATA: registry keys poleKit / poleKitAt / poleKitHow (had|adopt|mark|give) / poleKitUid (the uid the kit gave) per profile (lifelong/<pkey>.properties). New rows (absent = the default; no one-time update
needed - no existing default changed): part.sickle, sickle.cuts, sickle.stickPlants, sickle.fiberChance, sickle.stickChance, sickle.perLevel,
sickle.perFortune, sickle.sweep, sickle.sweepMax, sickle.sweepElsewhere, sticks.keepPct, sticks.lists, lifelong.poleKit, smith.upgradeTab.
ROLLBACK 0.3.11 -> 0.3.10 is item-safe (poles already given stay lifelong poles; bushes refuse sickles again; sticks back to vanilla; the
Upgrade tab goes). Deploy with SkyyFishing 0.1.7 + SkyyQuests 0.3.4 (each also works alone). ROLL SkyyGear 0.3.11 AND SkyyQuests 0.3.4 BACK
TOGETHER (fix round, safety critic 3): Quests 0.3.4's Marlow gives no pole and Gear 0.3.10 has no starting-kit pole, so with only Gear rolled
back a NEW profile gets no lifelong pole (the bench's Wooden rod then crafts again, but only as a plain rod). SkyyFishing may stay on 0.1.7.
FIX ROUND (2026-10-16, critics): the Server Setup rows part.sickle / sickle.cuts / sticks.lists run GearSickle.refresh (after=) - a field: row
never reloads the file, so 0.3.11's first build only flipped / wrapped at a FILE load; an asset hot-reload is caught by the 10 s look on a block
break (new BlockType / ItemDropList objects flipped / wrapped again); leaves give no sickle sticks (sickle.stickPlants = bushes + brambles: a
swept canopy gave dozens); sticks.keepPct 50 (Skyy "a bit"); sickle.sweepMax per tier + sickle.sweepLayers; the Upgrade tab lists the gear IN
Requip (Take out) and the pole's tier; the pole kit's crash REDO (poleKitHow / poleKitUid); no "Marlow gives the pole" text when the kit is off.
FIX ROUND 2 (2026-10-16, second critics): a sword refused on a bush tells the player why ("Bushes, brambles and vines need a sickle", GearLife.tellOnce,
at most once per GearSickle.VETO_GAP 30 s - an anti-spam guard like the 150 ms sweep throttle, not a Server Setup row); every sickle's tooltip says
"Cuts bushes, grass and leaves - sweeps the plants around" while part.sickle is on; the Upgrade tab lists the pole + the lifelong tools not on you
right after the carried lifelong tools (before armor) and its header counts them ("N on you, A not on you, M in Requip").
"""
import os
import ast
import json
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.10.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.11.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.10"' in s and "GENERATED by tools/gear_0_3_10_patch.py" in s and "0.3.11" not in s, "not the generated 0.3.10 script"
assert "GearSickle" not in s and "UpgPage" not in s and "GearStick" not in s
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
if _set is not None and _set.get("SkyyGear") != "0.3.10":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.10" % _set.get("SkyyGear"))

# ---- the vanilla facts this round relies on (the CACHED Assets.zip, read only - nothing is copied into the jar)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import serverjar
_AZ = zipfile.ZipFile(serverjar.assets_zip())
_ITEMS = {}
for _n in _AZ.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        try:
            _ITEMS[os.path.basename(_n)[:-5]] = json.loads(_AZ.read(_n).decode("utf-8-sig"))
        except Exception:
            pass


def _gath(i, seen=0):
    d = _ITEMS.get(i) if isinstance(i, str) else None
    if not d or seen > 8:
        return None
    g = (d.get("BlockType") or {}).get("Gathering")
    if g is not None:
        return g
    return _gath(d.get("Parent"), seen + 1)


SICKLE_CUTS_DEF = "Plant_Bush,Plant_Bramble,Plant_Flower_Bushy,Plant_Grass,Plant_Fern,Plant_Leaves,Plant_Vine,Plant_Reeds,Plant_Roots"
SICKLE_STICK_DEF = "Plant_Bush,Plant_Bramble"          # fix round (critics): no leaves - a swept canopy gave dozens of sticks
STICK_LISTS_DEF = "Wood_Branch,Wood_Sticks,Plant_Bush,Plant_Bush_Berry_Red"
SICKLE_SWEEP_DEF = "1,1,2,2,3,3,4,4"
SICKLE_MAX_DEF = "24,24,40,40,60,60,80,80"          # fix round (critic 3.4): the cap grows with the reach
STICK_KEEP_DEF = 50          # fix round (critic 3.5): Skyy "reduce ... a bit" - half the branch / pile / bush sticks (oak: ~0.65 sticks per log)
_soft_cut, _flip = [], []
for _p in SICKLE_CUTS_DEF.split(","):
    _m = [i for i in _ITEMS if i.startswith(_p)]
    assert _m, "sickle.cuts: no vanilla item starts with " + _p
    for _i in _m:
        _g = _gath(_i)
        if _g and isinstance(_g.get("Soft"), dict):
            _soft_cut.append(_i)
            if _g["Soft"].get("IsWeaponBreakable") is False:
                _flip.append(_i)
assert len(_flip) >= 20 and "Plant_Bush" in _flip and "Plant_Grass_Lush" in _soft_cut and "Plant_Leaves_Oak" in _soft_cut, (_flip[:5], len(_soft_cut))
assert _ITEMS["Tool_Sickle_Crude"].get("Weapon") is not None, "the vanilla sickle has no Weapon section any more - re-check why bushes refused it"
for _l in STICK_LISTS_DEF.split(","):
    _t = _AZ.read([n for n in _AZ.namelist() if n.startswith("Server/Drops/") and n.endswith("/" + _l + ".json")][0]).decode("utf-8-sig")
    assert "Ingredient_Stick" in _t, "sticks.lists: %s drops no stick" % _l
for _i in ("Ingredient_Fibre", "Ingredient_Stick"):
    assert _i in _ITEMS, _i
assert "Ingredient_Stick" not in _AZ.read("Server/Drops/Wood/Tree_Leaves.json").decode("utf-8-sig"), "leaves drop sticks now - re-check FEWER STICKS"
print("0.3.11 vanilla: %d soft plants on sickle.cuts, %d refuse weapons (made sickle-breakable at start); stick lists %s"
      % (len(_soft_cut), len(_flip), STICK_LISTS_DEF))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.10 - build script (javassist via jpype). GENERATED by tools/gear_0_3_10_patch.py from the LIVE 0.3.9 (itself GENERATED by
tools/gear_0_3_9_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.10.py -> SkyyGear/SkyyGear-0.3.10.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.10.py
''', '''"""SkyyGear 0.3.11 - build script (javassist via jpype). GENERATED by tools/gear_0_3_11_patch.py from the LIVE 0.3.10 (itself GENERATED by
tools/gear_0_3_10_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.11.py -> SkyyGear/SkyyGear-0.3.11.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.11.py

0.3.11 = THE SICKLE CUTS PLANTS + FEWER STICKS + THE POLE IN THE STARTING KIT + THE UPGRADE TAB (notes: tools/gear_0_3_11_patch.py): bushes,
brambles and vines refused every weapon (the sickle has a Weapon section) - the plants on sickle.cuts are sickle-breakable now (other weapons
still refused), a sickle cut gives extra Plant Fiber / Sticks (level + Fortune) and sweeps the plants around it; stick drop lists (branches,
stick piles, bushes) keep 50 % of their sticks; every profile gets its lifelong fishing pole once; /smithing has an Upgrade tab listing every
item you carry that can tier up (/upgrade opens it).

--- 0.3.10 notes ---
''')
rep('VERSION = "0.3.10"\n', 'VERSION = "0.3.11"\n')

# ================================================================================================================ Server Setup rows
before("CFG_ROWS = [\n", """# 0.3.11 (tools/gear_0_3_11_patch.py): the sickle's plants, its stick plants, the stick-cut drop lists, the sweep reach per tier (defaults)
SICKLE_CUTS_DEF = %r
SICKLE_STICK_DEF = %r
STICK_LISTS_DEF = %r
SICKLE_SWEEP_DEF = %r
SICKLE_MAX_DEF = %r
STICK_KEEP_DEF = %d
""" % (SICKLE_CUTS_DEF, SICKLE_STICK_DEF, STICK_LISTS_DEF, SICKLE_SWEEP_DEF, SICKLE_MAX_DEF, STICK_KEEP_DEF))
before('''    # 0.3.6 POLE PERKS (spec 6.3): Steady Line = the fish pulls this % slower per level
''', '''    # 0.3.11 THE SICKLE CUTS PLANTS + FEWER STICKS + THE POLE IN THE KIT + THE UPGRADE TAB (tools/gear_0_3_11_patch.py)
    ("part.sickle", "Sickle cuts plants", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = sickles cut bushes, grass, leaves (sickle.cuts): extra fiber / sticks + a sweep. Off = vanilla.", "field:GearCfg.SICKLE_ON;after=GearSickle.refresh"),
    ("sickle.cuts", "Plants the sickle cuts", "lifelong", "text", "%s", "0", "800", "", "", "live",
     "Block id starts, joined by commas. Of these, only sickles break the ones vanilla keeps from weapons.", "field:GearCfg.SICKLE_CUTS;after=GearSickle.refresh"),
    ("sickle.stickPlants", "Plants that give sickle sticks", "lifelong", "text", "%s", "0", "400", "", "", "live,danger",
     "Block id starts (joined by commas) whose sickle cut can give extra Sticks.", "field:GearCfg.SICKLE_STK"),
    ("sickle.fiberChance", "Sickle extra Plant Fiber", "lifelong", "dec", "60", "0", "500", "", "%%", "live,danger",
     "Chance per plant a sickle cuts for 1 extra Plant Fiber (150 = 1 sure + a 50%% chance of 2; max 5).", "field:GearCfg.SICKLE_FIB"),
    ("sickle.stickChance", "Sickle extra Sticks", "lifelong", "dec", "35", "0", "500", "", "%%", "live,danger",
     "Chance per bush / bramble a sickle cuts for 1 extra Stick (sickle.stickPlants; at most 5 per plant).", "field:GearCfg.SICKLE_STC"),
    ("sickle.perLevel", "Sickle extra per tool level", "lifelong", "dec", "0.5", "0", "10", "", "%%", "live,danger",
     "Added to both sickle chances for every level of the sickle.", "field:GearCfg.SICKLE_PLV"),
    ("sickle.perFortune", "Sickle extra per Fortune", "lifelong", "dec", "2", "0", "50", "", "%%", "live,danger",
     "Added to both sickle chances for every point of the sickle's Farming Fortune.", "field:GearCfg.SICKLE_PFO"),
    ("sickle.sweep", "Sickle sweep reach per tier", "lifelong", "text", "%s", "1", "40", "", "", "live",
     "Blocks around the cut plant, Crude to Onyxium: 8 numbers 0-6 (1 = 3x3, 2 = 5x5), joined by commas.", "field:GearCfg.SICKLE_SW;check=GearSickle.checkSweep"),
    ("sickle.sweepMax", "Most plants one sweep cuts per tier", "lifelong", "text", "%s", "1", "60", "", "", "live",
     "Crude to Onyxium: 8 numbers 0-200, joined by commas. 0 = that tier cuts one plant per hit.", "field:GearCfg.SICKLE_MAX;check=GearSickle.checkMax"),
    ("sickle.sweepLayers", "Sickle sweep layers up and down", "lifelong", "int", "1", "0", "3", "", "", "live",
     "Layers above and below the cut plant the sweep also takes. 0 = only its own layer.", "field:GearCfg.SICKLE_LAY"),
    ("sickle.sweepElsewhere", "Sickle sweep outside islands", "lifelong", "bool", "true", "", "", "", "", "live",
     "Off = the sweep only works on island worlds where you may build.", "field:GearCfg.SICKLE_ELSE"),
    ("sticks.keepPct", "Sticks kept from branches and bushes", "drops", "int", "%d", "0", "100", "", "%%", "live,danger",
     "Chance each stick of a sticks.lists drop (branches, piles, bushes) is kept. 100 = vanilla.", "field:GearCfg.STICK_KEEP"),
    ("sticks.lists", "Drop lists with fewer sticks", "drops", "text", "%s", "0", "400", "", "", "live,danger",
     "Drop list ids (Server/Drops) joined by commas. The sickle's own extra sticks are never cut.", "field:GearCfg.STICK_LISTS;after=GearSickle.refresh"),
    ("lifelong.poleKit", "Fishing pole in the starting kit", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "Every profile gets its lifelong fishing pole once, like the pickaxe. Off = no pole is handed out.", "field:GearCfg.LL_POLEKIT"),
    ("smith.upgradeTab", "Upgrade tab", "smithing", "bool", "true", "", "", "", "", "live",
     "Smithing tab with every item you carry that can tier up (/upgrade). Off = /upgrade opens the Anvil.", "field:GearCfg.UPG_TAB"),
''' % (SICKLE_CUTS_DEF, SICKLE_STICK_DEF, SICKLE_SWEEP_DEF, SICKLE_MAX_DEF, STICK_KEEP_DEF, STICK_LISTS_DEF))
rep('''"gear.gatherAnvilOnly"}''', '''"gear.gatherAnvilOnly",
           # 0.3.11: the sickle's yield + who may cut (item supply = economy), the stick cut, the pole gift
           "part.sickle", "sickle.stickPlants", "sickle.fiberChance", "sickle.stickChance", "sickle.perLevel", "sickle.perFortune",
           "sticks.keepPct", "sticks.lists", "lifelong.poleKit"}''')
after('''G39_ROWK = ["gear.gatherAnvilOnly"]
assert all(32 <= ord(_c) < 127 for _c in G39_HEAD) and "=" not in G39_HEAD
''', '''G311_HEAD = "# ---- sickle cuts plants, fewer sticks, the pole in the starting kit, the Upgrade tab (SkyyGear 0.3.11) ----"
G311_ROWK = ["part.sickle", "sickle.cuts", "sickle.stickPlants", "sickle.fiberChance", "sickle.stickChance", "sickle.perLevel", "sickle.perFortune",
             "sickle.sweep", "sickle.sweepMax", "sickle.sweepLayers", "sickle.sweepElsewhere", "sticks.keepPct", "sticks.lists", "lifelong.poleKit",
             "smith.upgradeTab"]
assert all(32 <= ord(_c) < 127 for _c in G311_HEAD) and "=" not in G311_HEAD
''')
after('''    L += ["", G39_HEAD]         # 0.3.9: the new row (no one-time update adds it; absent = the default ON)
    for k in G39_ROWK:
        scal(k)
''', '''    L += ["", G311_HEAD]        # 0.3.11: the new rows (no one-time update adds them; absent = the default)
    for k in G311_ROWK:
        scal(k)
''')
rep('''              ("GARM_ANVIL", "boolean", "true")]          # 0.3.9 gear.gatherAnvilOnly''' + " " + '''
''', '''              ("GARM_ANVIL", "boolean", "true"),          # 0.3.9 gear.gatherAnvilOnly
              # 0.3.11 the sickle, the stick cut, the pole in the kit, the Upgrade tab
              ("SICKLE_ON", "boolean", "true"), ("SICKLE_CUTS", "String", jstr(SICKLE_CUTS_DEF)), ("SICKLE_STK", "String", jstr(SICKLE_STICK_DEF)),
              ("SICKLE_FIB", "double", "60.0"), ("SICKLE_STC", "double", "35.0"), ("SICKLE_PLV", "double", "0.5"), ("SICKLE_PFO", "double", "2.0"),
              ("SICKLE_SW", "String", jstr(SICKLE_SWEEP_DEF)), ("SICKLE_MAX", "String", jstr(SICKLE_MAX_DEF)), ("SICKLE_LAY", "int", "1"),
              ("SICKLE_ELSE", "boolean", "true"), ("STICK_KEEP", "int", str(STICK_KEEP_DEF)), ("STICK_LISTS", "String", jstr(STICK_LISTS_DEF)), ("LL_POLEKIT", "boolean", "true"),
              ("UPG_TAB", "boolean", "true")]
''')
after('''  GARM_ANVIL = pbool(p, "gear.gatherAnvilOnly", true);          // 0.3.9 (review F1)
''', '''  SICKLE_ON = pbool(p, "part.sickle", true);          // 0.3.11
  SICKLE_CUTS = ptext(p, "sickle.cuts", "%s").trim();
  SICKLE_STK = ptext(p, "sickle.stickPlants", "%s").trim();
  SICKLE_FIB = pdec(p, "sickle.fiberChance", 60.0, 0.0, 500.0);
  SICKLE_STC = pdec(p, "sickle.stickChance", 35.0, 0.0, 500.0);
  SICKLE_PLV = pdec(p, "sickle.perLevel", 0.5, 0.0, 10.0);
  SICKLE_PFO = pdec(p, "sickle.perFortune", 2.0, 0.0, 50.0);
  SICKLE_SW = ptext(p, "sickle.sweep", "%s").trim();
  SICKLE_MAX = ptext(p, "sickle.sweepMax", "%s").trim();
  SICKLE_LAY = (int) plong(p, "sickle.sweepLayers", 1L, 0L, 3L);
  SICKLE_ELSE = pbool(p, "sickle.sweepElsewhere", true);
  STICK_KEEP = (int) plong(p, "sticks.keepPct", %dL, 0L, 100L);
  STICK_LISTS = ptext(p, "sticks.lists", "%s").trim();
  LL_POLEKIT = pbool(p, "lifelong.poleKit", true) && !Boolean.getBoolean("skyy.harness.noPoleKit");          // HARNESS SEAM ONLY: the older harness children run 0.3.10's flow
  UPG_TAB = pbool(p, "smith.upgradeTab", true);
''' % (SICKLE_CUTS_DEF, SICKLE_STICK_DEF, SICKLE_SWEEP_DEF, SICKLE_MAX_DEF, STICK_KEEP_DEF, STICK_LISTS_DEF))

# ================================================================================================================ 4. the tab row: + Upgrade (mode 6)
rep('''  boolean it = @PKG@.GearCfg.ANVIL_ON && @PKG@.GearCfg.IDENTIFY_CMD;          // 0.3.9: the Identify tab (/identify)
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0) + (lt ? 1 : 0) + (it ? 1 : 0);''',
    '''  boolean it = @PKG@.GearCfg.ANVIL_ON && @PKG@.GearCfg.IDENTIFY_CMD;          // 0.3.9: the Identify tab (/identify)
  boolean ut = @PKG@.GearCfg.UPG_TAB && @PKG@.GearCfg.UP_ON;          // 0.3.11: the Upgrade tab (/upgrade) - every item that can tier up
  if (ut) up = false;          // 0.3.11: never two "Upgrade" tabs (the old Reforge-page Upgrade mode stays reachable from the Anvil)
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0) + (lt ? 1 : 0) + (it ? 1 : 0) + (ut ? 1 : 0);''')
rep('''  int[] order = new int[] { 3, 0, 5, 4, 1, 2 };''', '''  int[] order = new int[] { 3, 0, 5, 4, 6, 1, 2 };          // 0.3.11: Craft | Anvil | Identify | Tools | Upgrade''')
rep('''    if (m == 4 && !lt) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");
    String nm = m == 3 ? "Craft" : (m == 0 ? (@PKG@.GearCfg.ANVIL_ON ? "Anvil" : "Reforge") : (m == 1 ? "Upgrade" : (m == 4 ? "Tools" : (m == 5 ? "Identify" : "Multitool"))));''',
    '''    if (m == 4 && !lt) continue;
    if (m == 6 && !ut) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");
    String nm = m == 3 ? "Craft" : (m == 0 ? (@PKG@.GearCfg.ANVIL_ON ? "Anvil" : "Reforge") : (m == 1 || m == 6 ? "Upgrade" : (m == 4 ? "Tools" : (m == 5 ? "Identify" : "Multitool"))));''')

# ================================================================================================================ 3. the pole in the starting kit
rep('''  return "lifelong tools on (one pickaxe / hatchet / hoe / sickle per profile + the fishing pole from Marlow or /lifelong, level''',
    '''  return "lifelong tools on (one pickaxe / hatchet / hoe / sickle per profile + the fishing pole " + (@PKG@.GearCfg.LL_POLEKIT ? "in the starting kit" : "only from a quest reward - lifelong.poleKit is off") + ", level''')
rep('''  if (cur == null) w = k == @PKG@.GearLL.POLE ? "From Marlow's fishing quest at the hub pier" : "Arrives when you have a free inventory slot";          // 0.3.10: the pole is a quest reward''',
    '''  if (cur == null) w = k == @PKG@.GearLL.POLE && !@PKG@.GearCfg.LL_POLEKIT ? "Not handed out on this server - a pole a quest gives you becomes it" : "Arrives when you have a free inventory slot";          // 0.3.11: the pole is in the starting kit (lifelong.poleKit)''')
rep('''  if (cur == null && k == @PKG@.GearLL.POLE) return "-You have no fishing pole yet''',
    '''  if (cur == null && k == @PKG@.GearLL.POLE && @PKG@.GearCfg.LL_POLEKIT) return "-Your lifelong fishing pole is on its way - free one inventory slot and it arrives.";          // 0.3.11
  if (cur == null && k == @PKG@.GearLL.POLE) return "-You have no fishing pole yet''')
rep('''  if (cur == null && k == @PKG@.GearLL.POLE) return "-You have no fishing pole yet - Marlow at the hub pier gives you one (got his pole before? hold it and type /lifelong).";''',
    '''  if (cur == null && k == @PKG@.GearLL.POLE) return "-You have no lifelong fishing pole - this server hands none out (lifelong.poleKit is off). A pole a quest gave you: hold it and type /lifelong.";          // 0.3.11 fix round: no Marlow pole any more''')
rep('''"-Only the fishing pole from Marlow's quest at the hub pier can become your lifelong pole - this rod is a plain one."''',
    '''"-Only a fishing pole a quest gave you can become your lifelong pole - this rod is a plain one."''')
# the journalled give redraws a pole through SkyyFishing like every other pole write (GearLife.put does it already)
rep('''  try { tx = c.setItemStackForSlot((short) slot, @PKG@.GearData.put(new @IS@(id, 1), nd, u)); } catch (Throwable t) { ex = t; }''',
    '''  try {
    @IS@ gs = @PKG@.GearData.put(new @IS@(id, 1), nd, u);
    if (@PKG@.GearLL.isPole(id)) gs = poleRedraw(gs, nd);          // 0.3.11: the pole of the starting kit gets SkyyFishing's name + rig lines
    tx = c.setItemStackForSlot((short) slot, gs);
  } catch (Throwable t) { ex = t; }''')
# fix round 2 (critic: nothing points the player at the sickle): every sickle's tooltip says what it cuts while part.sickle is on
rep('''  @PKG@.GearLL.lines(owner, id, d, txt, col);          // 0.3.0: lifelong tool lines''',
    '''  if (@PKG@.GearCfg.SICKLE_ON && id != null && id.startsWith("Tool_Sickle_")) { txt.add("Cuts bushes, grass and leaves - sweeps the plants around"); col.add(@PKG@.GearDefs.C_LABEL); }          // 0.3.11 fix round 2
  @PKG@.GearLL.lines(owner, id, d, txt, col);          // 0.3.0: lifelong tool lines''')
before('''# THE SWEEP (world thread; join = force, every stamp scan = at most every 400 ms): journals, the migration (once), the look
''', r'''# 0.3.11 THE POLE IN THE STARTING KIT (lifelong.poleKit; Skyy 2026-10-15 "lets make the fishing rod spawn with you too"): ONCE per profile
# (registry poleKit=1): a pole the registry already names counts; a lifelong pole of this profile in the inventory is adopted; else the best
# plain rod carried becomes it (the migration's rule for the other four); else the Crude pole (Wooden Fishing Rod) is GIVEN through the
# journalled give (journal first, the same uid on a retry - never a second copy). No SkyyFishing item = nothing yet (asked again later).
# Returns true when the registry changed in memory (the sweep's one save writes it, like the migration).
F(glf, "public static final long[] NK = new long[4];")          # 0.3.11: 0 poles given, 1 adopted / marked, 2 already had one, 3 waiting for room
M(glf, r"""
public static boolean poleKit(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  if (!@PKG@.GearCfg.LL_POLEKIT || pr == null || inv == null || P == null) return false;
  int k = @PKG@.GearLL.POLE;
  String K = @PKG@.GearLL.KIND[k];
  java.util.UUID u = pr.getUuid();
  boolean ch = false;
  if ("1".equals(P.getProperty("poleKit"))) {
    // fix round (safety critic 2) = the migration's LL-REDO for the pole: the kit GAVE this uid, the registry reached the disk, the item never
    // did (never seen, no journal, not in the inventory) -> the kit starts over (a later /pole reclaim has another uid = never touched)
    String cu = P.getProperty(K + ".uid");
    if (cu == null || !"give".equals(P.getProperty("poleKitHow")) || !cu.equals(P.getProperty("poleKitUid")) || "1".equals(P.getProperty(K + ".seen"))
        || P.getProperty(K + ".pend") != null || find(inv, pk, cu) != null) return false;
    P.remove(K + ".uid");
    P.remove(K + ".id");
    P.remove(K + ".rp");
    P.remove("poleKit");
    P.remove("poleKitHow");
    P.remove("poleKitUid");
    @PKG@.GearLog.line("LL-POLEKIT-REDO " + u + " " + pk + " " + cu + " (the kit gave it, never seen, not in the inventory)");
    ch = true;
  }
  String cr = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.Gear.item(cr) == null) return ch;          // no SkyyFishing (yet): nothing to give, asked again at the next look
  long now = System.currentTimeMillis();
  if (P.getProperty(K + ".uid") != null && P.getProperty(K + ".pend") == null) {
    P.setProperty("poleKit", "1");
    P.setProperty("poleKitAt", String.valueOf(now));
    P.setProperty("poleKitHow", "had");
    NK[2] = NK[2] + 1L;
    @PKG@.GearLog.line("LL-POLEKIT-HAD " + u + " " + pk + " " + P.getProperty(K + ".uid"));
    return true;
  }
  if (P.getProperty(K + ".pend") == null) {
    int[] ad = findKind(inv, pk, k);
    if (ad != null) {
      @IS@ x = @PKG@.GearStamp.at(inv, ad[0], ad[1]);
      @BD@ d = docOf(x);
      commit(pk, P, k, @PKG@.GearLL.uid(d), x.getItemId(), @PKG@.GearLL.isRp(d), "poleKit", "1", false);
      P.setProperty("poleKitAt", String.valueOf(now));
      P.setProperty("poleKitHow", "adopt");
      NK[1] = NK[1] + 1L;
      @PKG@.GearLog.line("LL-POLEKIT-ADOPT " + u + " " + pk + " " + @PKG@.GearLL.uid(d) + " " + x.getItemId());
      return true;
    }
    int[] b = best(inv, k);
    if (b != null) {
      if (!mark(pr, inv, pk, P, k, b[0], b[1], "mark")) return ch;
      P.setProperty("poleKit", "1");
      P.setProperty("poleKitAt", String.valueOf(now));
      P.setProperty("poleKitHow", "mark");
      NK[1] = NK[1] + 1L;
      tellOnce(pr, "polekit", "The fishing rod you carry is your lifelong fishing pole now - it can't be dropped, and /pole brings it back if you lose it.", 5000L);
      return true;
    }
  }
  int g = give(pr, inv, pk, P, k, cr, "give");
  if (g == 1) {
    P.setProperty("poleKit", "1");
    P.setProperty("poleKitAt", String.valueOf(now));
    P.setProperty("poleKitHow", "give");
    if (P.getProperty(K + ".uid") != null) P.setProperty("poleKitUid", P.getProperty(K + ".uid"));
    NK[0] = NK[0] + 1L;
    tellOnce(pr, "polekit", "You got your lifelong fishing pole - right click deep water to fish. It works as it is; hooks, lines and sinkers from a Fishing Bench make it better. Lost it? /pole", 5000L);
    return true;
  }
  if (g == 0) { NK[3] = NK[3] + 1L; tellOnce(pr, "room" + k, "Your lifelong fishing pole is waiting - free one inventory slot and it arrives.", 60000L); }
  return ch;
}""")
''')
rep('''  pass(pr, inv, pk, P, mg);          // fix round: one save carries the migration's deferred commits + migrated=1''',
    '''  if ("1".equals(P.getProperty("migrated")) && poleKit(pr, inv, pk, P)) mg = true;          // 0.3.11: the pole in the starting kit (after the four)
  pass(pr, inv, pk, P, mg);          // fix round: one save carries the migration's deferred commits + migrated=1''')
# gear:fn:poleRule (SkyyFishing 0.1.7: the bench refuses the Wooden Fishing Rod while every profile gets its one pole)
rep('''  try {
    // fix round 2 (cross-mod critic 1): SkyyQuests' tutorial asks gear:fn:lifelong''', '''  try {
    if (this.mode == 5) return Boolean.valueOf(@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.LL_POLEKIT && @PKG@.GearCfg.LL_NOCRAFT);          // 0.3.11 gear:fn:poleRule
    // fix round 2 (cross-mod critic 1): SkyyQuests' tutorial asks gear:fn:lifelong''')
rep('''  br.put("gear:fn:fishx", new @PKG@.GearLLFn(4));          // 0.3.6: the angler armor + the pole perks for SkyyFishing 0.1.6''',
    '''  br.put("gear:fn:fishx", new @PKG@.GearLLFn(4));          // 0.3.6: the angler armor + the pole perks for SkyyFishing 0.1.6
  br.put("gear:fn:poleRule", new @PKG@.GearLLFn(5));       // 0.3.11: one pole per profile (SkyyFishing 0.1.7 refuses the bench's Wooden rod)''')
rep('''bq.remove("gear:fn:fishx");''', '''bq.remove("gear:fn:fishx"); bq.remove("gear:fn:poleRule");''')

# ================================================================================================================ the manifest
rep('''the fishing pole is the fifth lifelong tool (/pole, from Marlow's quest);''',
    '''the fishing pole is the fifth lifelong tool (/pole, in every starting kit; it fishes without tackle);''')
rep('''Server Setup -> Gear. Replaces SkyyRolls.''', '''SICKLES cut bushes, grass, ferns, leaves and vines (other weapons still bounce off bushes) with extra Plant Fiber and Sticks by level and Fortune, sweeping the plants around; tree branches, stick piles and bushes drop fewer sticks; an Upgrade tab on /smithing lists everything you carry that can tier up (/upgrade); Server Setup -> Gear. Replaces SkyyRolls.''')

# ================================================================================================================ 1, 2, 4: the new classes (before the 0.3.10 always-answer wrapper)
before('''# ####################################################################################################################################
# 0.3.10 ALWAYS ANSWER (tools/gear_0_3_10_patch.py 1A)''', r'''# ####################################################################################################################################
# 0.3.11 (tools/gear_0_3_11_patch.py): GearSickle (the plants a sickle cuts: weapon flip, other-weapon veto, yield, sweep), GearSickleTask
# (the next-tick check + yield + sweep), GearSickleSys (BreakBlockEvent), GearStick (the stick-cut drop container), UpgPage (the Upgrade tab).
# Placed here: everything they call exists (GearTool, GearLL, GearLife, GearUp, LifePage, GearUi, GearTill); the plugin's setup / start /
# shutdown, GearToolHitSys, UpCmd and the other Smithing pages get their hooks below (before the always-answer wrapper copies the handlers).
# ####################################################################################################################################
G311 = {"SBD": "com.hypixel.hytale.server.core.asset.type.blocktype.config.SoftBlockDropType",
        "IDL": "com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList",
        "IDC": "com.hypixel.hytale.server.core.asset.type.item.config.container.ItemDropContainer",
        "IDR": "com.hypixel.hytale.server.core.asset.type.item.config.ItemDrop",
        "BHU": "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils"}
for _k in G311:
    assert _k not in T, "0.3.11 token clashes: " + _k
T.update(G311)
for _c, _m in ((G311["SBD"], "isWeaponBreakable"), (TL["TBGA"], "getSoft"), (TL["TBGA"], "isSoft"), (G311["IDL"], "getAssetMap"),
               (G311["IDL"], "getContainer"), (G311["IDC"], "getWeight"), (G311["IDC"], "getAllDrops"), (G311["IDR"], "getItemId"),
               (G311["IDR"], "getQuantityMin"), (G311["IDR"], "getQuantityMax"), (G311["IDR"], "getMetadata"), (G311["BHU"], "performBlockBreak"),
               (CO["BBE"], "getItemInHand"), (CO["BBE"], "getBlockType"), (CO["BBE"], "getTargetBlock"), (TL["TDBE"], "setCancelled"),
               (ITM, "getWeapon"), (IS, "getItem"), (SIC, "addOrDropItemStack"), (INV, "getCombinedStorageHotbarBackpack"), (INV, "getItemInHand")):
    B.probe(pool, _c, _m)
# the engine shapes this round depends on (VERIFIED bytecode 2026-10-15, Hytale 0.7.2)
_sbdf = pool.get(G311["SBD"]).getDeclaredField("isWeaponBreakable")
assert str(_sbdf.getType().getName()) == "boolean", "SoftBlockDropType.isWeaponBreakable is no boolean field"
_idlf = pool.get(G311["IDL"]).getDeclaredField("container")
assert str(_idlf.getType().getName()) == G311["IDC"], "ItemDropList.container changed"
_idc = pool.get(G311["IDC"])
assert [str(_c.getSignature()) for _c in _idc.getDeclaredConstructors() if str(_c.getSignature()) == "(D)V"], "ItemDropContainer(double) is gone"
_pds = [str(_m.getSignature()) for _m in _idc.getDeclaredMethods() if str(_m.getName()) == "populateDrops"]
assert sorted(_pds) == ["(Ljava/util/List;Ljava/util/function/DoubleSupplier;Ljava/lang/String;)V", "(Ljava/util/List;Ljava/util/function/DoubleSupplier;Ljava/util/Set;)V"], _pds
_pbb = [str(_m.getSignature()) for _m in pool.get(G311["BHU"]).getDeclaredMethods() if str(_m.getName()) == "performBlockBreak"]
assert "(Lorg/joml/Vector3i;Lcom/hypixel/hytale/server/core/asset/type/blocktype/config/BlockType;Lcom/hypixel/hytale/server/core/inventory/ItemStack;ILjava/lang/String;Ljava/lang/String;ILcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/ComponentAccessor;Lcom/hypixel/hytale/component/ComponentAccessor;)V" in _pbb, _pbb
_sic = [str(_m.getSignature()) for _m in pool.get(SIC).getDeclaredMethods() if str(_m.getName()) == "addOrDropItemStack"]
assert "(Lcom/hypixel/hytale/component/ComponentAccessor;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Lcom/hypixel/hytale/server/core/inventory/ItemStack;)Z" in _sic, _sic
G311_CLASSES = []
gsck = mk("GearSickle")
gsct = mk("GearSickleTask")
gsst = mk("GearSickleSys", EES)
gstk = mk("GearStick", G311["IDC"])
upg = mk("UpgPage", PAGE)
G311_CLASSES += [gsck, gsct, gsst, gstk, upg]
# ---- GearSickleTask: one cut, checked on the next world tick (fields only; GearSickle.done does the work)
gsct.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public @WLD@ w;", "public int x;", "public int y;", "public int z;", "public String bid;", "public @IS@ held;",
           "public boolean sweep;"):
    F(gsct, _f)
C(gsct, r"""
public GearSickleTask(@PR@ pr, @WLD@ w, int x, int y, int z, String bid, @IS@ held, boolean sweep) {
  this.pr = pr; this.w = w; this.x = x; this.y = y; this.z = z; this.bid = bid; this.held = held; this.sweep = sweep;
}""")
# ---- GearStick: a drop list's container that keeps each stick with sticks.keepPct (a 2+ pile is scaled instead)
F(gstk, "public @IDC@ inner;")
F(gstk, "public String lid;")
F(gstk, "public static final long[] N = new long[3];")          # 0 rolls, 1 sticks dropped, 2 sticks kept
C(gstk, r"""
public GearStick(@IDC@ in, String lid) {
  super(in == null ? 0.0 : in.getWeight());
  this.inner = in;
  this.lid = lid;
}""")
M(gstk, r"""
public static Object thin(Object o, double r, int keep) {
  if (!(o instanceof @IDR@)) return o;
  @IDR@ d = (@IDR@) o;
  if (!"Ingredient_Stick".equals(d.getItemId())) return o;
  N[1] = N[1] + 1L;
  if (keep >= 100) { N[2] = N[2] + 1L; return o; }
  if (keep <= 0) return null;
  int mx = d.getQuantityMax();
  if (mx >= 2) {
    double k = (double) keep / 100.0;
    int a = (int) Math.round((double) d.getQuantityMin() * k);
    int b = (int) Math.round((double) mx * k);
    if (b < a) b = a;
    if (b <= 0) return r * 100.0 < (double) keep ? o : null;
    N[2] = N[2] + 1L;
    return new @IDR@(d.getItemId(), d.getMetadata(), a, b);
  }
  if (r * 100.0 < (double) keep) { N[2] = N[2] + 1L; return o; }
  return null;
}""")
M(gstk, r"""
protected void populateDrops(java.util.List out, java.util.function.DoubleSupplier ds, java.util.Set seen) {
  if (this.inner == null || out == null) return;
  int n0 = out.size();
  this.inner.populateDrops(out, ds, this.lid);
  N[0] = N[0] + 1L;
  int keep = @PKG@.GearCfg.STICK_KEEP;
  if (keep >= 100) return;
  for (int i = out.size() - 1; i >= n0; i--) {
    Object o = out.get(i);
    double r = ds == null ? java.util.concurrent.ThreadLocalRandom.current().nextDouble() : ds.getAsDouble();
    Object t = thin(o, r, keep);
    if (t == null) out.remove(i);
    else if (t != o) out.set(i, t);
  }
}""")
M(gstk, "public java.util.List getAllDrops(java.util.List out) { return this.inner == null ? out : this.inner.getAllDrops(out); }")
M(gstk, 'public String toString() { return "GearStick{" + this.lid + ", keep " + @PKG@.GearCfg.STICK_KEEP + "% of " + this.inner + "}"; }')
# ---- GearSickle
for _f in ("public static final java.util.concurrent.ConcurrentHashMap FLIP = new java.util.concurrent.ConcurrentHashMap();",   # block id -> SoftBlockDropType made breakable
           "public static final java.util.concurrent.ConcurrentHashMap WRAP = new java.util.concurrent.ConcurrentHashMap();",   # drop list id -> GearStick
           "public static final java.util.concurrent.ConcurrentHashMap SWEEPING = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> TRUE while our break runs
           "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> Long last sweep
           "public static volatile String CUT_SRC = null;", "public static volatile String[] CUTS = new String[0];",
           "public static volatile String STK_SRC = null;", "public static volatile String[] STKS = new String[0];",
           "public static volatile String SW_SRC = null;", "public static volatile int[] SW = new int[] { 1, 1, 2, 2, 3, 3, 4, 4 };",
           # fix round (critic 3.4): the sweep cap per tier (sickle.sweepMax)
           "public static volatile String MX_SRC = null;", "public static volatile int[] MX = new int[] { 24, 24, 40, 40, 60, 60, 80, 80 };",
           # fix round (critic safety 1): one ensure at a time (start, config apply, Server Setup's after= hook, the 10 s look on a break)
           "public static final java.util.concurrent.atomic.AtomicBoolean ENS_BUSY = new java.util.concurrent.atomic.AtomicBoolean(false);",
           "public static volatile String FL_SRC = null;", "public static volatile String WR_SRC = null;", "public static volatile long ENS = 0L;",
           "public static volatile boolean FLIP_BAD = false;", "public static volatile boolean WRAP_BAD = false;",
           # 0 plants made sickle-breakable, 1 weapon hits refused, 2 cuts seen, 3 cuts that did not break, 4 extra fiber, 5 extra sticks,
           # 6 plants swept, 7 sweeps, 8 sweeps refused (protection), 9 drop lists wrapped
           "public static final long[] N = new long[10];",
           # HARNESS SEAMS ONLY (null in the game): block id at Object[]{x,y,z}; break Object[]{UUID, List}; give Object[]{UUID, id, Integer};
           # island:perm stand-in; tasks run here instead of world.execute
           "public static volatile java.util.function.Function BLK = null;", "public static volatile java.util.function.Function BRK = null;",
           "public static volatile java.util.function.Function GIVE = null;", "public static volatile java.util.function.Function PERM = null;",
           "public static volatile java.util.List RUN = null;"):
    F(gsck, _f)
M(gsck, r"""
public static String[] list(String v) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (v != null) {
    String[] p = v.split(",");
    for (int i = 0; i < p.length && out.size() < 64; i++) {
      String t = p[i].trim();
      if (t.length() > 0) out.add(t);
    }
  }
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
M(gsck, r"""
public static String[] cuts() {
  String v = @PKG@.GearCfg.SICKLE_CUTS;
  if (v != null && !v.equals(CUT_SRC)) { CUTS = list(v); CUT_SRC = v; }
  return CUTS;
}""")
M(gsck, r"""
public static String[] stks() {
  String v = @PKG@.GearCfg.SICKLE_STK;
  if (v != null && !v.equals(STK_SRC)) { STKS = list(v); STK_SRC = v; }
  return STKS;
}""")
M(gsck, r"""
public static boolean pre(String[] ps, String id) {
  if (id == null || ps == null) return false;
  String x = id.startsWith("*") ? id.substring(1) : id;
  for (int i = 0; i < ps.length; i++) if (x.startsWith(ps[i])) return true;
  return false;
}""")
M(gsck, "public static boolean cut(String id) { return pre(cuts(), id); }")
M(gsck, "public static boolean stick(String id) { return pre(stks(), id); }")
M(gsck, r"""
public static boolean sickle(@IS@ s) {
  if (s == null || s.isEmpty()) return false;
  String id = s.getItemId();
  return id != null && id.startsWith("Tool_Sickle_");
}""")
# sickle.sweep: 8 numbers 0-6, sickle.sweepMax: 8 numbers 0-200 - Crude .. Onyxium (null = bad; Server Setup check=)
M(gsck, r"""
public static int[] parseNums(String v, int hi) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length != 8) return null;
  int[] a = new int[8];
  for (int i = 0; i < 8; i++) {
    try { a[i] = Integer.parseInt(p[i].trim()); } catch (Throwable t) { return null; }
    if (a[i] < 0 || a[i] > hi) return null;
  }
  return a;
}""")
M(gsck, "public static int[] parseSweep(String v) { return parseNums(v, 6); }")
M(gsck, r"""
public static String checkSweep(String key, String value) {
  return parseSweep(value) == null ? "Sweep reach per sickle tier: 8 numbers from 0 to 6 (Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium), joined by commas." : null;
}""")
M(gsck, r"""
public static String checkMax(String key, String value) {
  return parseNums(value, 200) == null ? "Most plants one sweep cuts per sickle tier: 8 numbers from 0 to 200 (Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium), joined by commas." : null;
}""")
M(gsck, r"""
public static int cap(String sickleId) {
  String v = @PKG@.GearCfg.SICKLE_MAX;
  if (v != null && !v.equals(MX_SRC)) {
    int[] a = parseNums(v, 200);
    if (a == null) @PKG@.Gear.warnOnce("sicklemax:" + v.hashCode(), "config.properties: sickle.sweepMax '" + v + "' is not 8 numbers 0-200 - the default 24,24,40,40,60,60,80,80 applies");
    MX = a == null ? new int[] { 24, 24, 40, 40, 60, 60, 80, 80 } : a;
    MX_SRC = v;
  }
  int t = @PKG@.GearLL.tier(sickleId);
  int[] a2 = MX;
  if (t < 0) t = 0;
  if (t >= a2.length) t = a2.length - 1;
  return a2[t];
}""")
M(gsck, r"""
public static int reach(String sickleId) {
  String v = @PKG@.GearCfg.SICKLE_SW;
  if (v != null && !v.equals(SW_SRC)) {
    int[] a = parseSweep(v);
    if (a == null) @PKG@.Gear.warnOnce("sicklesweep:" + v.hashCode(), "config.properties: sickle.sweep '" + v + "' is not 8 numbers 0-6 - the default 1,1,2,2,3,3,4,4 applies");
    SW = a == null ? new int[] { 1, 1, 2, 2, 3, 3, 4, 4 } : a;
    SW_SRC = v;
  }
  int t = @PKG@.GearLL.tier(sickleId);
  int[] a2 = SW;
  if (t < 0) t = 0;
  if (t >= a2.length) t = a2.length - 1;
  return a2[t];
}""")
# THE FLIP (start, and again when sickle.cuts / part.sickle change - ensure): every soft plant of sickle.cuts that refuses weapons is made
# weapon-breakable on the server; a plant that left the list (or part.sickle off) gets its vanilla value back. Returns the plants now flipped.
M(gsck, r"""
public static int flip() {
  java.lang.reflect.Field f = null;
  try {
    f = @SBD@.class.getDeclaredField("isWeaponBreakable");
    f.setAccessible(true);
  } catch (Throwable t) {
    if (!FLIP_BAD) { FLIP_BAD = true; @PKG@.Gear.warn("sickle: SoftBlockDropType.isWeaponBreakable cannot be set (" + t + ") - bushes keep refusing sickles"); }
    return -1;
  }
  java.util.ArrayList ks = new java.util.ArrayList(FLIP.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String id = (String) ks.get(i);
    if (@PKG@.GearCfg.SICKLE_ON && cut(id)) continue;
    Object sb = FLIP.remove(id);
    if (sb == null || FLIP.containsValue(sb)) continue;
    try { f.setBoolean(sb, false); } catch (Throwable t2) { }
  }
  if (@PKG@.GearCfg.SICKLE_ON) {
    java.util.Map m = null;
    try { m = @BTYP@.getAssetMap().getAssetMap(); } catch (Throwable t3) { m = null; }
    if (m != null) {
      java.util.ArrayList vs = new java.util.ArrayList(m.values());
      for (int i = 0; i < vs.size(); i++) {
        Object o = vs.get(i);
        if (!(o instanceof @BTYP@)) continue;
        @BTYP@ bt = (@BTYP@) o;
        String id = bt.getId();
        if (id == null || !cut(id)) continue;
        @TBGA@ g = bt.getGathering();
        if (g == null || !g.isSoft()) continue;
        @SBD@ sb = g.getSoft();
        if (sb == null) continue;
        Object old = FLIP.get(id);
        if (old == sb) continue;          // fix round (critic safety 1): an asset reload makes NEW objects - those get flipped again
        if (sb.isWeaponBreakable() && !FLIP.containsValue(sb)) { if (old != null) FLIP.remove(id); continue; }
        try { f.setBoolean(sb, true); FLIP.put(id, sb); } catch (Throwable t4) { }
      }
    }
  }
  N[0] = (long) FLIP.size();
  return FLIP.size();
}""")
M(gsck, r"""
public static void unflip() {
  try {
    java.lang.reflect.Field f = @SBD@.class.getDeclaredField("isWeaponBreakable");
    f.setAccessible(true);
    java.util.ArrayList vs = new java.util.ArrayList(FLIP.values());
    for (int i = 0; i < vs.size(); i++) { try { f.setBoolean(vs.get(i), false); } catch (Throwable t2) { } }
  } catch (Throwable t) { }
  FLIP.clear();
  N[0] = 0L;
}""")
# THE STICK CUT: the containers of sticks.lists get a GearStick (reflection: ItemDropList.container); a list that left the row gets its own
# container back. Returns the lists now wrapped.
M(gsck, r"""
public static int wrap() {
  java.lang.reflect.Field f = null;
  try {
    f = @IDL@.class.getDeclaredField("container");
    f.setAccessible(true);
  } catch (Throwable t) {
    if (!WRAP_BAD) { WRAP_BAD = true; @PKG@.Gear.warn("sticks: ItemDropList.container cannot be set (" + t + ") - sticks drop as in vanilla"); }
    return -1;
  }
  String[] want = list(@PKG@.GearCfg.STICK_LISTS);
  java.util.HashSet ws = new java.util.HashSet();
  for (int i = 0; i < want.length; i++) ws.add(want[i]);
  java.util.ArrayList ks = new java.util.ArrayList(WRAP.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String id = (String) ks.get(i);
    if (ws.contains(id)) continue;
    @PKG@.GearStick gs = (@PKG@.GearStick) WRAP.remove(id);
    try {
      @IDL@ l = (@IDL@) @IDL@.getAssetMap().getAsset(id);
      if (l != null && l.getContainer() == gs) f.set(l, gs.inner);
    } catch (Throwable t2) { }
  }
  for (int i = 0; i < want.length; i++) {
    try {
      @IDL@ l = (@IDL@) @IDL@.getAssetMap().getAsset(want[i]);
      if (l == null) { WRAP.remove(want[i]); continue; }
      @IDC@ c = l.getContainer();
      if (c instanceof @PKG@.GearStick) { WRAP.put(want[i], c); continue; }
      if (c == null) continue;
      @PKG@.GearStick gs = new @PKG@.GearStick(c, want[i]);
      f.set(l, gs);
      WRAP.put(want[i], gs);
    } catch (Throwable t3) { @PKG@.Gear.warnOnce("stickwrap:" + want[i], "sticks: the drop list " + want[i] + " could not be wrapped: " + t3); }
  }
  N[9] = (long) WRAP.size();
  return WRAP.size();
}""")
M(gsck, r"""
public static void unwrap() {
  try {
    java.lang.reflect.Field f = @IDL@.class.getDeclaredField("container");
    f.setAccessible(true);
    java.util.ArrayList ks = new java.util.ArrayList(WRAP.keySet());
    for (int i = 0; i < ks.size(); i++) {
      String id = (String) ks.get(i);
      @PKG@.GearStick gs = (@PKG@.GearStick) WRAP.get(id);
      @IDL@ l = (@IDL@) @IDL@.getAssetMap().getAsset(id);
      if (l != null && gs != null && l.getContainer() == gs) f.set(l, gs.inner);
    }
  } catch (Throwable t) { }
  WRAP.clear();
  N[9] = 0L;
}""")
# called at start (forced: the assets exist now), after every config FILE apply (GearCfg.apply), after a Server Setup change of part.sickle /
# sickle.cuts / sticks.lists (fix round, engine critic 1: a field: row only runs its after= hook - refresh) and, at most every 10 s, from the
# BreakBlockEvent system (tick; fix round, safety critic 1: an asset hot-reload makes NEW BlockType / ItemDropList objects - the next look flips
# and wraps those). One at a time (ENS_BUSY); a change seen while another run is busy is caught by the next call (FL_SRC / WR_SRC differ).
M(gsck, r"""
public static void ensure() {
  if (!ENS_BUSY.compareAndSet(false, true)) return;
  try {
    long now = System.currentTimeMillis();
    String fl = (@PKG@.GearCfg.SICKLE_ON ? "1" : "0") + "|" + @PKG@.GearCfg.SICKLE_CUTS;
    String wr = @PKG@.GearCfg.STICK_LISTS;
    boolean due = now - ENS > 10000L || now < ENS;
    if (due || !fl.equals(FL_SRC)) { flip(); FL_SRC = fl; }
    if (due || wr == null || !wr.equals(WR_SRC)) { wrap(); WR_SRC = wr; }
    if (due) ENS = now;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("sickleensure", "sickle / stick setup failed: " + t); }
  finally { ENS_BUSY.set(false); }
}""")
M(gsck, "public static void refresh(String key) { ensure(); }")          # Server Setup after= hook (part.sickle, sickle.cuts, sticks.lists)
M(gsck, r"""
public static void tick() {
  long now = System.currentTimeMillis();
  if (now - ENS > 10000L || now < ENS) ensure();
}""")
# GearToolHitSys (inserted first): another WEAPON on a plant we made weapon-breakable = vanilla's refusal (the engine re-sends the block)
M(gsck, r"""
public static boolean veto(Object ev) {
  if (!(ev instanceof @TDBE@) || FLIP.isEmpty()) return false;
  @TDBE@ e = (@TDBE@) ev;
  if (e.isCancelled()) return false;
  @TBTY@ bt = e.getBlockType();
  if (bt == null || bt.getId() == null || !FLIP.containsKey(bt.getId())) return false;
  @IS@ s = e.getItemInHand();
  if (s == null || s.isEmpty() || sickle(s)) return false;
  @ITM@ it = s.getItem();
  if (it == null || it.getWeapon() == null) return false;
  e.setCancelled(true);
  N[1] = N[1] + 1L;
  return true;
}""")
# fix round 2 (critic: "for some reason"): the refused player is told why, at most once per VETO_GAP ms (anti-spam, like the 150 ms sweep throttle)
F(gsck, "public static final long VETO_GAP = 30000L;")
M(gsck, r"""
public static void vetoTell(@ACH@ chunk, int idx) {
  try {
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.GearLife.tellOnce(pr, "sicklebush", "Bushes, brambles and vines need a sickle - other weapons bounce off." + (@PKG@.GearCfg.LL_ON ? " Lost yours? /sickle" : ""), VETO_GAP);
  } catch (Throwable t) { }
}""")
# the block id at x, y, z of world w (null = unknown / not loaded - never loads anything)
M(gsck, r"""
public static String blockId(@WLD@ w, int x, int y, int z) {
  java.util.function.Function sb = BLK;
  if (sb != null) { Object o = sb.apply(new Object[] { Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) }); return o instanceof String ? (String) o : null; }
  if (w == null) return null;
  int i = @PKG@.GearTill.blockAt(w.getChunkStore(), x, y, z);
  if (i < 0) return null;
  @BTYP@ bt = (@BTYP@) @BTYP@.getAssetMap().getAsset(i);
  return bt == null ? null : bt.getId();
}""")
M(gsck, r"""
public static boolean softCut(String id) {
  if (id == null || !cut(id)) return false;
  try {
    @BTYP@ bt = (@BTYP@) @BTYP@.getAssetMap().getAsset(@BTYP@.getAssetMap().getIndex(id));
    @TBGA@ g = bt == null ? null : bt.getGathering();
    return g != null && g.isSoft();
  } catch (Throwable t) { return false; }
}""")
# 100 = one sure, the rest a chance; at most 5
M(gsck, r"""
public static int roll(double pct) {
  if (Double.isNaN(pct) || !(pct > 0.0)) return 0;
  double x = pct / 100.0;
  if (x > 5.0) x = 5.0;
  int w = (int) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}""")
# the extra % of this sickle: level x sickle.perLevel + Farming Fortune x sickle.perFortune (GearTool.stats: { fam, row, level, active, power,
# Fortune, ... }; a sickle above your skill works like a plain one - no Fortune)
M(gsck, r"""
public static double extra(java.util.UUID u, @IS@ s) {
  double[] st = null;
  try { st = @PKG@.GearTool.stats(u, s); } catch (Throwable t) { st = null; }
  if (st == null || st.length < 6) return 0.0;
  double lv = st[2] > 0.0 ? st[2] : 0.0;
  double fo = st[3] > 0.5 && st[5] > 0.0 ? st[5] : 0.0;
  return lv * @PKG@.GearCfg.SICKLE_PLV + fo * @PKG@.GearCfg.SICKLE_PFO;
}""")
M(gsck, r"""
public static void giveTo(@PR@ pr, @REF@ r, @ST@ st, String id, int n) {
  if (n <= 0) return;
  java.util.function.Function g = GIVE;
  if (g != null) { g.apply(new Object[] { pr.getUuid(), id, Integer.valueOf(n) }); return; }
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (p == null) return;
  @SIC@.addOrDropItemStack(st, r, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, n));
}""")
# island worlds: SkyyIslands' island:perm:fn "build"; any other world: sickle.sweepElsewhere
M(gsck, r"""
public static boolean allowed(java.util.UUID u, String world) {
  java.util.function.Function f = PERM != null ? PERM : @PKG@.Gear.fn("island:perm:fn");
  Object r = null;
  if (f != null && u != null && world != null) {
    try { r = f.apply(new Object[] { u, world, "build" }); } catch (Throwable t) { r = Boolean.FALSE; }
  }
  if (r instanceof Boolean) return ((Boolean) r).booleanValue();
  return @PKG@.GearCfg.SICKLE_ELSE;
}""")
# GearSickleSys (BreakBlockEvent, world thread): a sickle in hand + a plant of sickle.cuts -> one task on the next world tick
M(gsck, r"""
public static boolean onBreak(@PR@ pr, @ST@ st, @BBE@ e) {
  if (!@PKG@.GearCfg.SICKLE_ON || pr == null || st == null || e == null || e.isCancelled()) return false;
  @IS@ s = e.getItemInHand();
  if (!sickle(s)) return false;
  @TBTY@ bt = e.getBlockType();
  String bid = bt == null ? null : bt.getId();
  if (!cut(bid)) return false;
  @VECI@ tb = e.getTargetBlock();
  if (tb == null) return false;
  @WLD@ w = null;
  Object ext = st.getExternalData();
  if (ext instanceof @EST@) w = ((@EST@) ext).getWorld();
  if (w == null && RUN == null) return false;
  N[2] = N[2] + 1L;
  @PKG@.GearSickleTask t = new @PKG@.GearSickleTask(pr, w, tb.x(), tb.y(), tb.z(), bid, s, !SWEEPING.containsKey(pr.getUuid()));
  java.util.List q = RUN;
  if (q != null) { q.add(t); return true; }
  w.execute(t);
  return true;
}""")
# the sweep: the cut plants of sickle.cuts around (x, y, z) - reach by the sickle's tier, sickle.sweepLayers up and down, soft only, at most
# sickle.sweepMax (per tier) - broken by the engine (a real BreakBlockEvent each: protection, drops, XP, Collections; each gets its own yield task)
M(gsck, r"""
public static int sweep(@PR@ pr, @REF@ r, @ST@ st, @PKG@.GearSickleTask t) {
  String hid = t.held == null ? null : t.held.getItemId();
  int max = cap(hid);          // fix round (critic 3.4): sickle.sweepMax per tier
  int rr = reach(hid);
  int lay = @PKG@.GearCfg.SICKLE_LAY;          // fix round (critic 3.7): sickle.sweepLayers
  if (lay < 0) lay = 0;
  if (lay > 3) lay = 3;
  if (max <= 0 || rr <= 0) return 0;
  java.util.UUID u = pr.getUuid();
  long now = System.currentTimeMillis();
  Object l = LAST.get(u);
  if (l instanceof Long && now >= ((Long) l).longValue() && now - ((Long) l).longValue() < 150L) return 0;
  LAST.put(u, Long.valueOf(now));
  String wn = t.w == null ? "harness" : t.w.getName();
  if (!allowed(u, wn)) { N[8] = N[8] + 1L; return 0; }
  java.util.ArrayList list = new java.util.ArrayList();
  for (int d = 1; d <= rr && list.size() < max; d++) {          // nearest ring first
    for (int dy = -lay; dy <= lay && list.size() < max; dy++) {
      for (int dx = -d; dx <= d && list.size() < max; dx++) {
        for (int dz = -d; dz <= d && list.size() < max; dz++) {
          if (Math.abs(dx) != d && Math.abs(dz) != d) continue;
          int x = t.x + dx;
          int y = t.y + dy;
          int z = t.z + dz;
          if (!softCut(blockId(t.w, x, y, z))) continue;
          list.add(new @VECI@(x, y, z));
        }
      }
    }
  }
  for (int dy = -lay; dy <= lay && list.size() < max; dy++) {          // straight above / below the cut plant
    if (dy != 0 && softCut(blockId(t.w, t.x, t.y + dy, t.z))) list.add(new @VECI@(t.x, t.y + dy, t.z));
  }
  if (list.isEmpty()) return 0;
  int n = 0;
  SWEEPING.put(u, Boolean.TRUE);
  try {
    java.util.function.Function b = BRK;
    if (b != null) {
      Object o = b.apply(new Object[] { u, list });
      n = o instanceof Integer ? ((Integer) o).intValue() : 0;
    } else {
      @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
      @IS@ h = null;
      if (p != null) h = p.getInventory().getItemInHand();
      if (sickle(h)) {
        // each plant like the engine's own soft-block hit (damageSingleBlock -> performBlockBreak with the Soft drop list, quantity 1, the
        // player twice): a real BreakBlockEvent (protection, XP, Collections), the plant's own drops (VERIFIED bytecode 2026-10-15; the
        // List variant passes no drop list = the block's item)
        @CHST@ cs = t.w.getChunkStore();
        for (int i = 0; i < list.size(); i++) {
          @VECI@ v = (@VECI@) list.get(i);
          try {
            int bi = @PKG@.GearTill.blockAt(cs, v.x(), v.y(), v.z());
            if (bi < 0) continue;
            @BTYP@ bt = (@BTYP@) @BTYP@.getAssetMap().getAsset(bi);
            if (bt == null || bt.getGathering() == null) continue;
            @SBD@ so = bt.getGathering().getSoft();
            if (so == null) continue;
            @REF@ sec = cs.getChunkSectionReferenceAtBlock(v.x(), v.y(), v.z());
            if (sec == null || !sec.isValid()) continue;
            @BHU@.performBlockBreak(v, bt, h, 1, so.getItemId(), so.getDropListId(), 4096, r, sec, st, cs.getStore());
            if (@PKG@.GearTill.blockAt(cs, v.x(), v.y(), v.z()) != bi) n++;
          } catch (Throwable x1) { @PKG@.Gear.warnOnce("sicklesweep1", "a swept plant could not be cut (logged once): " + x1); }
        }
      }
    }
  } catch (Throwable x) { @PKG@.Gear.warnOnce("sicklesweep", "the sickle sweep failed (logged once): " + x); }
  SWEEPING.remove(u);
  N[6] = N[6] + (long) n;
  N[7] = N[7] + 1L;
  return n;
}""")
# THE CUT (GearSickleTask.run, world thread, one tick later): still the player of this world, the plant really went -> the extra fiber /
# sticks, then (a hit, not a swept plant) the sweep
M(gsck, r"""
public static int[] done(@PKG@.GearSickleTask t) {
  if (t == null || t.pr == null) return null;
  @PR@ pr = t.pr;
  if (RUN == null) {
    if (!pr.isValid() || t.w == null) return null;
    java.util.UUID wu = pr.getWorldUuid();
    java.util.UUID mine = t.w.getWorldConfig() == null ? null : t.w.getWorldConfig().getUuid();
    if (wu == null || mine == null || !wu.equals(mine)) return null;
  }
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @ST@ st = r.getStore();
  if (st == null) return null;
  String now = blockId(t.w, t.x, t.y, t.z);
  if (now == null || now.equals(t.bid)) { N[3] = N[3] + 1L; return null; }
  java.util.UUID u = pr.getUuid();
  double ex = extra(u, t.held);
  int fi = roll(@PKG@.GearCfg.SICKLE_FIB + ex);
  int sk = stick(t.bid) ? roll(@PKG@.GearCfg.SICKLE_STC + ex) : 0;
  giveTo(pr, r, st, "Ingredient_Fibre", fi);
  giveTo(pr, r, st, "Ingredient_Stick", sk);
  N[4] = N[4] + (long) fi;
  N[5] = N[5] + (long) sk;
  int sw = t.sweep ? sweep(pr, r, st, t) : 0;
  return new int[] { fi, sk, sw };
}""")
M(gsck, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  LAST.remove(u);
  SWEEPING.remove(u);
}""")
M(gsck, r"""
public static String statusText() {
  return "sickle " + (@PKG@.GearCfg.SICKLE_ON ? "cuts plants (" + N[0] + " made sickle-breakable, other weapons refused " + N[1] + ", cuts " + N[2] + ", extra fiber " + N[4] + " / sticks " + N[5] + ", swept " + N[6] + " in " + N[7] + " sweeps)" : "OFF (part.sickle)") + "; sticks kept " + @PKG@.GearCfg.STICK_KEEP + "% on " + N[9] + " drop list(s) (" + @PKG@.GearStick.N[2] + " of " + @PKG@.GearStick.N[1] + " stick rolls kept)";
}""")
gsct.addMethod(CtNewMethod.make(J(r"""
public void run() {
  try { @PKG@.GearSickle.done(this); } catch (Throwable t) { @PKG@.Gear.warnOnce("sickletask", "a sickle cut could not be finished: " + t); }
}"""), gsct))
event_system(gsst, "GearSickleSys", CO["BBE"], PLAYER_Q, r"""
    if (!(ev instanceof @BBE@)) return;
    @PKG@.GearSickle.tick();          // fix round: at most every 10 s - flips / wraps the new objects of an asset hot-reload
    if (!@PKG@.GearCfg.SICKLE_ON) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.GearSickle.onBreak(pr, st, (@BBE@) ev);""")
# ---- the hooks: GearToolHitSys (first: the veto), GearCfg.load (ensure), the plugin (register, start, shutdown), logout
gtoolh.getDeclaredMethod("handle").insertBefore(J("{ try { if (@PKG@.GearSickle.veto($5)) { @PKG@.GearSickle.vetoTell($2, $1); return; } } catch (Throwable tsv) { } }"))
_ldM = [m for m in gcf.getDeclaredMethods() if str(m.getName()) == "apply" and str(m.getSignature()) == "(Ljava/util/Properties;Z)V"]
assert len(_ldM) == 1, "GearCfg.apply(Properties, boolean) changed"
_ldM[0].insertAfter(J("{ try { @PKG@.GearSickle.ensure(); } catch (Throwable tse) { } }"))          # every config FILE apply (Server Setup: the rows' after=GearSickle.refresh)
pl.getDeclaredMethod("setup").insertAfter(J("""{
  try { getEntityStoreRegistry().registerSystem(new @PKG@.GearSickleSys()); } catch (Throwable tss) { @PKG@.Gear.warn("GearSickleSys could not be registered (" + tss + ") - sickle cuts give no extra fiber / sticks and do not sweep"); }
}"""))
pl.getDeclaredMethod("start").insertAfter(J("""{
  try { @PKG@.GearSickle.ENS = 0L; @PKG@.GearSickle.FL_SRC = null; @PKG@.GearSickle.WR_SRC = null; @PKG@.GearSickle.ensure(); @PKG@.Gear.info("[SkyyGear] 0.3.11: " + @PKG@.GearSickle.statusText() + "; fishing pole in the starting kit " + (@PKG@.GearCfg.LL_POLEKIT ? "on" : "off (lifelong.poleKit)") + "; Upgrade tab " + (@PKG@.GearCfg.UPG_TAB ? "on" : "off (smith.upgradeTab)")); }
  catch (Throwable tsk) { @PKG@.Gear.warn("sickle / stick setup failed: " + tsk); }
}"""))
pl.getDeclaredMethod("shutdown").insertBefore(J("{ try { @PKG@.GearSickle.unflip(); @PKG@.GearSickle.unwrap(); } catch (Throwable tsd) { } }"))
_byeM = [m for m in pool.get(PKG + ".GearBye").getDeclaredMethods() if str(m.getName()) == "accept"]
assert _byeM, "GearBye.accept is gone"
for _m in _byeM:
    _m.insertBefore(J("{ try { if ($1 instanceof @PDE@) @PKG@.GearSickle.forget(((@PDE@) $1).getPlayerRef().getUuid()); } catch (Throwable tsf) { } }".replace("@PDE@", PDE)))
print("0.3.11 sickle: GearSickle / GearSickleTask / GearSickleSys / GearStick; the veto in GearToolHitSys; ensure() at start + every config load")

# ---- UpgPage: the Upgrade tab (header 4)
for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public String info;", "public String epoch;", "public int tok;",
           "public java.util.ArrayList rq;", "public long rqAt;"):          # fix round (critic 3.1): the IN Requip rows (re-read at most every RQ_MS)
    F(upg, _f)
C(upg, r"""
public UpgPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.pageNo = 0;
  this.info = "";
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
  this.tok = 0;
}""")
# fix round (critic 3.2): the pole's place on its ladder (GearLL.KLAD[POLE] = the SkyyFishing bench's rods; -1 = no pole id)
M(upg, r"""
public static int poleIdx(String id) {
  if (id == null || !@PKG@.GearLL.isPole(id)) return -1;
  String[] l = @PKG@.GearLL.KLAD[@PKG@.GearLL.POLE].split(",");
  for (int i = 0; i < l.length; i++) if (l[i].equals(id)) return i;
  return -1;
}""")
M(upg, r"""
public static String poleNext(String id) {
  int i = poleIdx(id);
  String[] l = @PKG@.GearLL.KLAD[@PKG@.GearLL.POLE].split(",");
  return i >= 0 && i + 1 < l.length ? l[i + 1] : null;
}""")
# "T3 Iron" from an id's tier word (the tool ladder words), "" = no tier word
M(upg, r"""
public static String tierTag(String id) {
  if (id == null) return "";
  int pi = poleIdx(id);
  if (pi >= 0) return "T" + (pi + 1) + " " + @PKG@.GearLL.tname(pi);          // fix round (critic 3.2): Wooden = T1 Crude, Copper = T2, Iron = T3
  String[] w = id.split("_");
  for (int i = 1; i < w.length; i++) {
    for (int j = 0; j < @PKG@.GearLL.TW.length; j++) {
      if (!@PKG@.GearLL.TW[j].equalsIgnoreCase(w[i])) continue;
      int t = @PKG@.GearLL.TN[j];
      return "T" + (t + 1) + " " + @PKG@.GearLL.tname(t);
    }
  }
  return "";
}""")
# sort key: 0 your lifelong tools (kind order), 1 armor, 2 the rest
M(upg, r"""
public static int group(@IS@ x, String pk) {
  @BD@ d = @PKG@.GearLife.docOf(x);
  if (@PKG@.GearLL.isLL(d) && pk.equals(@PKG@.GearLL.owner(d))) return 0;
  String id = x.getItemId();
  if (id.indexOf("Armor") >= 0 || (d != null && @PKG@.GearSet.of(d) != null)) return 1;
  return 2;
}""")
# THE LIST: Object[] { Integer section, Integer slot, String id, String fp, Integer group, String name } for every carried item with a next tier
# (GearUp.rows), lifelong first, then (fix round 2: before armor) Object[] { null, Integer kind } rows for lifelong tools that are not on you (and the pole), then armor, the rest
M(upg, r"""
public static java.util.ArrayList listOf(@INV@ inv, String pk, java.util.Properties P) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  java.util.ArrayList rs = @PKG@.GearUp.rows(inv);
  for (int g = 0; g < 3; g++) {
    for (int i = 0; i < rs.size(); i++) {
      int[] a = (int[]) rs.get(i);
      @IS@ x = @PKG@.GearStamp.at(inv, a[0], a[1]);
      if (x == null || x.isEmpty() || group(x, pk) != g) continue;
      out.add(new Object[] { Integer.valueOf(a[0]), Integer.valueOf(a[1]), x.getItemId(), @PKG@.GearForge.fp(x), Integer.valueOf(g), null });
    }
    if (g == 0 && P != null && !@PKG@.GearLL.bad(P)) {          // fix round 2: the pole + the lifelong tools not on you right after the carried ones (before armor)
      for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) {
        String cur = P.getProperty(@PKG@.GearLL.KIND[k] + ".uid");
        if (cur == null) continue;
        int[] at = @PKG@.GearLife.find(inv, pk, cur);
        if (at != null && k != @PKG@.GearLL.POLE) continue;
        if (k == @PKG@.GearLL.POLE && @PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) continue;
        out.add(new Object[] { null, Integer.valueOf(k), at == null ? "" : "here" });
      }
    }
  }
  return out;
}""")
M(upg, r"""
public void row(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P, int i, Object[] e) {
  String rid = "#SkyyGURow" + i;
  String id;
  String nm;
  String l1;
  String l2;
  int r = 0;
  boolean btn = false;
  boolean can = false;
  String btxt = "Tier up";
  String bev = "up:";
  if ("rq".equals(e[0])) {          // fix round (critic 3.1): gear IN Requip - Take out (wardrobe:fn:fetch), then it tiers up like the rest
    id = (String) e[2];
    @BD@ d0 = null;
    try { d0 = @PKG@.GearData.effective(id, (@BD@) e[3]); } catch (Throwable x0) { d0 = null; }
    r = d0 == null ? 0 : @PKG@.GearData.rarity(d0);
    nm = d0 == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d0);
    String to0 = @PKG@.GearUp.next(id);
    String tf0 = tierTag(id);
    String tt0 = to0 == null ? "" : tierTag(to0);
    l1 = (tf0.length() > 0 && tt0.length() > 0 ? tf0 + " -> " + tt0 + ": " : "Next: ") + (to0 == null ? "top tier" : @PKG@.Gear.itemName(to0));
    String ct0 = to0 == null ? "" : @PKG@.LifePage.costHave(inv, u, @PKG@.GearUp.cost(id, to0));
    l2 = (ct0.length() > 0 ? ct0 + " - " : "") + "In Requip: take it out to tier it up";
    btn = true;
    can = @PKG@.Gear.fn("wardrobe:fn:fetch") != null;
    btxt = "Take out";
    bev = "rq:";
  } else if (e[0] == null) {
    int k = ((Integer) e[1]).intValue();
    String K = @PKG@.GearLL.KIND[k];
    id = P.getProperty(K + ".id");
    if (id == null || @PKG@.Gear.item(id) == null) id = @PKG@.GearLL.KCRUDE[k];
    nm = "Your lifelong " + @PKG@.GearLL.KNAME[k].toLowerCase() + " - " + @PKG@.Gear.itemName(id);
    String tt = tierTag(id);
    if (k == @PKG@.GearLL.POLE) {          // fix round (critic 3.2): its tier, the next rod, the top; the tier-up is SkyyFishing's bench craft (no button here)
      String pn = poleNext(id);
      l1 = (tt.length() > 0 ? tt : "Tier") + (pn == null ? " - top tier" : " -> " + tierTag(pn) + ": " + @PKG@.Gear.itemName(pn));
      if (!"here".equals(e[2])) l2 = "Not on you - /pole brings it back";
      else l2 = pn == null ? "Your pole is the best rod there is." : "Tiers up at a Fishing Bench (Parts > " + @PKG@.Gear.itemName(pn) + ") - it takes your pole and keeps its level";
    } else {
      l1 = (tt.length() > 0 ? tt : "Tier") + " - tiers up here when it is on you";
      l2 = "Not on you - /" + K + " brings it back";
    }
  } else {
    int sec = ((Integer) e[0]).intValue();
    int sl = ((Integer) e[1]).intValue();
    id = (String) e[2];
    @IS@ x = @PKG@.GearStamp.at(inv, sec, sl);
    @BD@ d = x == null ? null : @PKG@.GearLife.docOf(x);
    r = d == null ? 0 : @PKG@.GearData.rarity(d);
    nm = x == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d);
    String to = @PKG@.GearUp.next(id);
    String tf = tierTag(id);
    String tt = to == null ? "" : tierTag(to);
    l1 = (tf.length() > 0 && tt.length() > 0 ? tf + " -> " + tt + ": " : "Next: ") + (to == null ? "top tier" : @PKG@.Gear.itemName(to));
    Object[] c = null;
    if (x != null) c = @PKG@.GearUp.check(x, u);
    String why = "The item moved - click Refresh.";
    Object[] co = null;
    if (c != null) { why = (String) c[0]; co = (Object[]) c[2]; }
    if (co == null && to != null) co = @PKG@.GearUp.cost(id, to);
    String ct = @PKG@.LifePage.costHave(inv, u, co);
    if (why == null) why = @PKG@.GearUp.shortOfU(inv, u, co);
    l2 = why == null ? "Cost: " + (ct.length() > 0 ? ct : "nothing") : (ct.length() > 0 ? ct + " - " : "") + why;
    btn = true;
    can = why == null && to != null;
  }
  b.appendInline("#SkyyGUList", "Group " + rid + " { Anchor: (Height: 96); LayoutMode: Left; Padding: (Full: 6); Background: #000000(0.25); " + @PKG@.GearUi.cell(84, id) + " Group { Anchor: (Width: 14); } Group { Anchor: (Width: 760); LayoutMode: Top; Label " + rid + "N { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); } Label " + rid + "A { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff(0.8), VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label " + rid + "B { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (can ? "#ffffff" : @PKG@.GearDefs.C_GOLD) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } Group { Anchor: (Width: 10); }" + (btn ? " TextButton " + rid + "U { Anchor: (Width: 170, Height: 44, Top: 20); Text: \"" + btxt + "\"; " + @PKG@.GearUi.btn(can ? ("rq:".equals(bev) ? 1 : 0) : 3) + " }" : "") + " }");
  b.set(rid + "N.Text", nm);
  b.set(rid + "A.Text", l1);
  b.set(rid + "B.Text", l2);
  b.appendInline("#SkyyGUList", "Group { Anchor: (Height: 6); }");
  if (btn) @PKG@.GearUi.on(b, ev, @BT@.Activating, rid + "U", @EVD@.of("a", bev + i + ":" + this.tok));
}""")
M(upg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ pl = null;
  try { pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { pl = null; }
  @INV@ inv = pl == null ? null : pl.getInventory();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearCfg.LL_ON ? @PKG@.GearLL.reg(pk) : null;
  this.tok = @PKG@.LifePage.nextTok();          // a new click token on every Tier up button of this build
  this.rows = listOf(inv, pk, P);
  int nrq = 0;
  if (@PKG@.GearCfg.UP_ON) {          // fix round (critic 3.1): + the gear IN Requip that can tier up (the Anvil's rows, ReforgePage.rqRows mode 1)
    long nw = System.currentTimeMillis();
    if (this.rq == null || nw - this.rqAt >= @PKG@.GearSmith.RQ_MS || nw < this.rqAt) {
      try { this.rq = @PKG@.ReforgePage.rqRows(u, 1); } catch (Throwable tq) { this.rq = new java.util.ArrayList(); }
      this.rqAt = nw;
    }
    for (int i = 0; i < this.rq.size(); i++) {
      Object[] q = (Object[]) this.rq.get(i);
      this.rows.add(new Object[] { "rq", q[0], q[1], q[2] });
      nrq++;
    }
  }
  int per = 6;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 6, 1066, "Upgrade");
  b.appendInline("#SkyyGBody", "Group #SkyyGUMain { Anchor: (Height: 662); LayoutMode: Top; Padding: (Top: 6); }");
  b.appendInline("#SkyyGUMain", "Label #SkyyGUHead { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  int items = 0;
  int away = 0;          // fix round 2: the lifelong rows count too (the pole on you = on you; a lifelong tool not on you = not on you)
  for (int i = 0; i < this.rows.size(); i++) {
    Object[] e0 = (Object[]) this.rows.get(i);
    if (e0[0] instanceof Integer) items++;
    else if (e0[0] == null) { if ("here".equals(e0[2])) items++; else away++; }
  }
  b.set("#SkyyGUHead.Text", (items == 0 && nrq == 0 && away == 0 ? "Nothing you carry can tier up right now" : "Everything you own that can tier up (" + items + " on you" + (away > 0 ? ", " + away + " not on you" : "") + (nrq > 0 ? ", " + nrq + " in Requip" : "") + ")") + (pages > 1 ? "  -  page " + (this.pageNo + 1) + " of " + pages : ""));
  b.appendInline("#SkyyGUMain", "Group #SkyyGUList { Anchor: (Height: 612); LayoutMode: Top; }");
  if (inv == null) {
    b.appendInline("#SkyyGUList", "Label { Anchor: (Height: 40); Text: \"Your inventory cannot be read right now - click Refresh.\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  } else {
    for (int i = this.pageNo * per; i < this.rows.size() && i < (this.pageNo + 1) * per; i++) row(b, ev, u, inv, pk, P, i, (Object[]) this.rows.get(i));
    if (this.rows.isEmpty()) b.appendInline("#SkyyGUList", "Label { Anchor: (Height: 60); Text: \"Tools, gathering armor and gear with a next tier show up here while you carry them or keep them in Requip. Your lifelong tools tier up here too.\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, Wrap: true); }");
  }
  b.appendInline("#SkyyGBody", "Label #SkyyGFoot { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGFoot.Text", "Costs count your inventory and your Magic Bags. Tiering up keeps rarity and rolls. Reforge on the Anvil, Upgrade Points on Tools.");
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 360, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnPrev { Anchor: (Width: 160, Height: 44); Text: \"Prev\"; " + @PKG@.GearUi.btn(this.pageNo > 0 ? 1 : 3) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 8, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnNext { Anchor: (Width: 160, Height: 44); Text: \"Next\"; " + @PKG@.GearUi.btn(this.pageNo + 1 < pages ? 1 : 3) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 8, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 8, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  @PKG@.GearUi.on(b, ev, @BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "pg:-1"));
  @PKG@.GearUi.on(b, ev, @BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "pg:1"));
  @PKG@.GearUi.on(b, ev, @BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  @PKG@.GearUi.on(b, ev, @BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
# the Tier up click: GearUp.upgrade = the Anvil's tier-up (same check, cost, skill gate, inventory + bags, restore on failure, log, sound)
M(upg, r"""
public void doUp(@INV@ inv, int i) {
  java.util.UUID u = this.playerRef.getUuid();
  if (!@PKG@.GearCfg.UP_ON) { this.info = "-Tiering up is switched off on this server."; return; }
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was tiered up. Try again in a moment."; return; }
  if (inv == null) { this.info = "-Your inventory cannot be read right now - nothing changed."; return; }
  if (i < 0 || i >= this.rows.size()) { this.info = "-That row is gone - here is the list again."; return; }
  Object[] e = (Object[]) this.rows.get(i);
  if (!(e[0] instanceof Integer)) { this.info = "-" + ("rq".equals(e[0]) ? "Take it out of Requip first." : "That one cannot tier up here."); return; }
  int sec = ((Integer) e[0]).intValue();
  int sl = ((Integer) e[1]).intValue();
  String id = (String) e[2];
  Object[] res = @PKG@.GearUp.upgrade(inv, sec, sl, id, (String) e[3], u, this.playerRef.getUsername());
  if (((Integer) res[0]).intValue() == 1) {
    @BD@ d = (@BD@) res[3];
    String to = ((@IS@) res[2]).getItemId();
    this.info = "+" + @PKG@.Gear.itemName(id) + " -> " + @PKG@.Gear.itemName(to) + " (" + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + ", Lv " + @PKG@.GearLevel.level(to, d) + ")!";
    return;
  }
  this.info = "-" + (String) res[1];
}""")
# fix round (critic 3.1): Take out = the Anvil's Requip fetch (wardrobe:fn:fetch: it becomes OUT, its stamp and every loadout pick stay)
M(upg, r"""
public void doRq(int i) {
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was taken out. Try again in a moment."; return; }
  if (i < 0 || i >= this.rows.size()) { this.info = "-That row is gone - here is the list again."; return; }
  Object[] e = (Object[]) this.rows.get(i);
  if (!"rq".equals(e[0])) { this.info = "-That one is not in Requip."; return; }
  java.util.function.Function f = @PKG@.Gear.fn("wardrobe:fn:fetch");
  if (f == null) { this.info = "-Requip is not loaded on this server."; return; }
  Object res = null;
  try { res = f.apply(new Object[] { u, (String) e[1] }); } catch (Throwable t) { res = "Requip did not answer (" + t + ")"; }
  this.rqAt = 0L;
  this.rq = null;
  if (!"ok".equals(res)) { this.info = "-" + (res == null ? "Requip did not answer." : String.valueOf(res)); return; }
  this.info = "=" + @PKG@.Gear.itemName((String) e[2]) + " was taken out of Requip (your loadouts still point at it) - Tier up is ready in the list.";
}""")
M(upg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.startsWith("mode:")) {
      String c = a.equals("mode:3") ? (@PKG@.GearCfg.SMITH_ON ? "smithing" : null) : (a.equals("mode:0") || a.equals("mode:1") ? "reforge" : (a.equals("mode:2") && @PKG@.GearUi.multiTab() ? "multitool" : null));
      if (c == null) { rebuild(); return; }
      try { @CMGR@.get().handleCommand(this.playerRef, c); } catch (Throwable t1) { @PKG@.Gear.warn("upgrade page: the " + c + " tab failed: " + t1); }
      return;
    }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t2) { }
      }
      close();
      return;
    }
    if (a.equals("refresh")) { this.info = ""; rebuild(); return; }
    if (a.startsWith("pg:")) {
      this.pageNo = this.pageNo + (a.equals("pg:-1") ? -1 : 1);
      rebuild();
      return;
    }
    java.util.UUID u = this.playerRef.getUuid();
    String ep = @PKG@.Gear.epoch(u);
    if (!ep.equals(this.epoch)) { this.epoch = ep; this.info = "-Your profile changed - check the list and click again."; rebuild(); return; }
    if (!a.startsWith("up:") && !a.startsWith("rq:")) { rebuild(); return; }
    String[] pa = a.split(":");
    if (pa.length < 3) { rebuild(); return; }
    int i = -1;
    int ct = -1;
    try { i = Integer.parseInt(pa[1]); ct = Integer.parseInt(pa[2]); } catch (Throwable t3) { i = -1; ct = -1; }
    if (ct != this.tok) return;          // an older copy / a repeat of the same click: nothing spent (the always-answer wrapper answers it)
    this.tok = @PKG@.LifePage.nextTok();          // used up BEFORE anything is spent
    if (a.startsWith("rq:")) { doRq(i); rebuild(); return; }
    @PLA@ pl0 = null;
    try { pl0 = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t4) { pl0 = null; }
    doUp(pl0 == null ? null : pl0.getInventory(), i);
    rebuild();
  } catch (Throwable t) {
    @PKG@.Gear.warn("upgrade page click failed: " + t);
    this.info = "-Something went wrong - nothing was changed. Click Refresh.";
    try { rebuild(); } catch (Throwable t9) { }
  }
}""")
# the Upgrade tab click (mode:6) on the other Smithing pages -> /upgrade; true = handled
M(upg, r"""
public static boolean tabGo(String data, @PR@ pr) {
  if (data == null || !"mode:6".equals(@PKG@.Gear.jsonStr(data, "a"))) return false;
  if (@PKG@.GearCfg.UPG_TAB && pr != null) {
    try { @CMGR@.get().handleCommand(pr, "upgrade"); } catch (Throwable t) { @PKG@.Gear.warn("the Upgrade tab could not open /upgrade: " + t); }
  }
  return true;
}""")
for _pg in (rpg, mpg, spg, ipg, lpg):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.UpgPage.tabGo($3, this.playerRef)) return; }"))
upg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearLL.tabGo($3, this.playerRef)) return; if (@PKG@.GearAnvil.idTabGo($3, this.playerRef)) return; }"))
# /upgrade opens the Upgrade tab while it is on (part.upgrade + smith.upgradeTab); off = the Anvil / Reforge page as before
upc.getDeclaredMethod("execute").insertBefore(J(r"""{
  if (@PKG@.GearCfg.UPG_TAB && @PKG@.GearCfg.UP_ON) {
    try {
      @PLA@ p0 = (@PLA@) $2.getComponent($3, @PLA@.getComponentType());
      if (p0 != null) {
        @PKG@.GearStamp.scan($4, p0.getInventory());
        if (@PKG@.GearCfg.LL_ON) @PKG@.GearLife.sweep($4, p0.getInventory(), true);
        p0.getPageManager().openCustomPage($3, $2, new @PKG@.UpgPage($4));
        return;
      }
    } catch (Throwable tu) { @PKG@.Gear.warn("/upgrade -> the Upgrade tab failed (the old page opens): " + tu); }
  }
}"""))
print("0.3.11 Upgrade tab: UpgPage (6 rows a page, click tokens), the mode:6 tab on Craft / Anvil / Multitool / Identify / Tools, /upgrade opens it")
''')
rep('''ANSWER_PAGES = [(rpg, "anvil page"), (mpg, "multitool page"), (spg, "smithing page"), (ipg, "identify page"), (lpg, "tools page")]''',
    '''ANSWER_PAGES = [(rpg, "anvil page"), (mpg, "multitool page"), (spg, "smithing page"), (ipg, "identify page"), (lpg, "tools page"),
                (upg, "upgrade page")]          # 0.3.11: + the Upgrade tab''')
rep('''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')

# ================================================================================================================ checks on the result
assert s.index("public static boolean poleKit(") < s.index("public static void sweep0(")
assert s.index("G311 = {\"SBD\"") < s.index("0.3.10 ALWAYS ANSWER (tools") < s.index("ALL = [gu, gdf, gcf")
assert s.count("registerSystem(new @PKG@.GearSickleSys())") == 1
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.10 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.10 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
