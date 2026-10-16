"""Derive SkyyGear/build_skyygear_0.3.14.py from the LIVE 0.3.13 (build_skyygear_0.3.13.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_13_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_14_patch.py      then      python SkyyGear/build_skyygear_0.3.14.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.14.py

0.3.14 (2026-10-16, round "farm01", FULL round: saved data + an item merge; Skyy's popup answers 2026-10-16, docs/answered/gear.md ONE FARMING TOOL
+ SWEEP TIER, SIGILS ON MINING SETS, SIGIL DROPS, MYTHIC SIGIL USE, TILL AREA EVERYWHERE; then "start building the queued answers, biggest
player-facing ones first"):
1. ONE FARMING TOOL (Skyy "lets retire the hoe and sickle, and start with the crude farming multitool and a crude watering can"; Server Setup
   harvester.only, on; needs part.harvester):
   (a) THE STARTING KIT: a profile's one-time lifelong migration gives NO hoe and the CRUDE HARVESTER as its sickle-kind tool (no rebirth gate;
       harvester.rebirthGate only gates the manual Tools-tab button now); a plain hoe / sickle the player carries is still marked first (it
       merges below - nothing rolled is lost); the can kit is unchanged (lifelong.canKit). The next look marks the profile merged
       (harv=1, harvAuto=kit) - no item moves.
   (b) THE ONE-TIME MERGE of an existing lifelong hoe + sickle (GearHarv.auto, at the lifelong look on the world thread, every 2 s at most):
       CRITIC FIX 3: a hoe that is away is fetched; while it is still stored somewhere (Requip, a closed Vault, a chest / window: hoe.locK) or
       lost without a snapshot the merge WAITS (never merged away, never retired) - /hoe brings it or makes a copy, then it merges.
       CRITIC FIX 4: the undo record also keeps the Harvester's fingerprint (id, rarity, lines, reforge / Sigil counts) + its perks right after
       the merge; /gear harvmerge undo refuses a Harvester changed since then (reply names what changed) unless the admin adds "force".
       the sickle must be on the player (else it is fetched from Requip / a CLOSED Vault - wardrobe:fn:fetch / vault:fn:takeLL, the /sickle
       paths - at most once a minute; still away = the player is told "/sickle brings it" and the merge waits); the hoe is fetched the same
       way when it is away; a hoe that still cannot come uses its registry snapshot (hoe.snap = the exact-copy document) and the physical
       one is RETIRED when it turns up (the 0.3.12 rule: harvHoe); no hoe at all = the sickle alone becomes the Harvester. THE RULES (Skyy
       "best tier / rarity / points kept, like the Anvil merge"): tier = the higher of the two (capped at the Harvester's top, Thorium);
       rarity = the better one (Mythic kept); EVERY modifier line of both (the best value of each line key, capped at the Harvester's cap at
       that rarity / level - NO rarity line-count trim, unlike the manual button); reforge count / name and Sigil count = the higher; Upgrade
       Points = the higher level of each perk line, NOT trimmed to the points earned (GearLife.harvPerksAll; free points show 0 until the
       skill catches up; a Reset gives every point back). SAFETY (PROJECT-RULES 4 one-time rules): a verified History copy of the profile's
       registry file FIRST (Skyy_SkyyGear/harvmerge/history/<pk>.properties.<stamp>.bak), then the undo record line (harvmerge/<pk>.log:
       MERGE <stamp> <sickle uid> <Harvester id> <hoe uid> <hoe id> <hoe metadata> <source> <sickle id> <sickle metadata> <history file>
       <hoe durability> <sickle durability>), then the 0.3.12 journal (harv.pend / harv.hoeU / harv.id / harv.doc / harv.at + harv.auto=1,
       harv.src) on disk before anything moves; (a) the hoe leaves (only a physical one), (b) the sickle's slot becomes the Harvester (same
       lifelong uid - Requip / Vault / loadout references to the sickle stay valid, the stack keeps its Requip stamp; a merged-away hoe from
       Requip is reported gone: wardrobe:fn:gone), (c) ONE registry write: the perks, hoe.* gone, harv=1, harvHoe, sickle.id = the Harvester,
       run-once marker harvAuto=1 / harvAutoAt / harvAutoHow; a crash anywhere = harvRecover finishes or drops it at the next look (it knows
       harv.auto: no trim). UNDO (admin): /gear harvmerge undo <player> (online) - at the next look: the History copy's hoe.* / sickle.* keys
       come back + harvAuto=undone (never merged automatically again) in ONE write with the journal harvUndo.pend, the Harvester's slot becomes
       the sickle again (same uid, its record metadata, Requip stamp dropped), the hoe is given back (a hoe merged from its SNAPSHOT comes back
       under a NEW uid in the exact-copy family of the old one, so the old physical hoe stays retired), "UNDONE" in the record. /gear harvmerge
       = the counters.
   (c) /hoe and /sickle EXPLAIN and give the Harvester ("Hoes are retired - your Harvester tills and reaps ..." + /harvester's answer:
       here / fetched / an exact copy); before the merge they fetch the sickle (the /sickle path) and merge at once. /harvester on an
       unmerged profile does the same; the Tools tab's "Make Harvester" runs this automatic merge too (its preview shows these rules). An undone
       profile keeps the 0.3.13 commands and button.
2. SWEEP TIER (Skyy "make sweep respect tier. crude is T1 copper is T2. so a crude tool can break T2 food for half xp, or harvest with F but
   sweep only works on same tier."; Server Setup farm.crudeT1, on): on CROPS a Crude (Wood) tool / bare hands count as their real tier (one
   below Copper) - no longer "Crude counts as Copper" (that 0.3.1 rule stays for ore and logs); the Harvester's family top is its own ladder
   top (Thorium) instead of the vanilla sickle's (Iron). A crop of tier T+1 breaks with half Farming XP and no Fortune and harvests with F
   (unchanged); T+2 and up is refused (unchanged). THE SWEEP: the Harvester's swing selectors run our interaction type SkyyGearHarvest
   (GearHarvCrop = vanilla HarvestCropInteraction, registered in setup() like SkyyGearCan; the Harvester items' Swing_Left / Right_Selector
   vars name the asset SkyyGear_Harvest_Crop in HitBlock): a crop of the tool's tier or lower = vanilla's harvest (the sweep); one tier up =
   only ONE such crop per swing breaks (the ordinary hit: half XP, no Fortune), every other one-up crop in the arc is skipped; two up =
   skipped + the "Too tough" popup. No durability on a swing harvest (Skyy "forever tools have no durability": the vars drop vanilla's
   AdjustHeldItemDurability step). gear:fn:farmTier (SkyySkills' half XP) and the Fortune crop list follow the same rule.
   CRITIC FIX 2 (Skyy 2026-10-16 popup "What should the Crude Harvester do?" -> "Full on starter crops"): a farming TOOL of tier t (Crude 0,
   Copper 1 ...) reaps crops of internal tier t + 1 in full: Crude = Wheat / Lettuce (full XP, Fortune, its sweep), Carrot / Corn one up (half
   XP, one per swing), Cauliflower / Turnip refused; Copper = Carrot / Corn in full, and so on; the family top (+1) still covers every crop
   above it. BARE HANDS keep the 0.3.5 rule (count as tier 1: Wheat full, Carrot half). The rule above that said "Crude = one below Copper" on
   crops is replaced by this.
3. SIGILS: (a) ON MINING SETS (Skyy "allow. (the rarity adjusts what the armor can give on its modifiers. the set bonus is extra on top ...)"):
   a Mining Set piece (Set rarity) takes any Sigil (it counts as Normal); the new rarity's empty modifier slots fill with a Reforge (now
   allowed - only Set-rarity mining pieces refuse it); the set field stays, so the full-set bonus still counts on top; a Mythic piece may still
   tier up. (b) MYTHIC SIGIL USE (Skyy "let it work. drops from any full boss. higher chance at higher zones."): sigil.mythicUse defaults ON.
   (c) DROPS (Skyy "common and uncommon can drop from mobs or loot bags/lost loot. rare and legendary can drop from mini bosses. then full
   bosses drop legendary and mythic."; Sigil ladder = Unique, Rare, Legendary, Fabled, Mythic - Skyy's common / uncommon = our lowest, Unique;
   Fabled sits with the full bosses between Legendary and Mythic) - Server Setup rows, % per roll, one Sigil per kill at most (rolled Mythic
   first): sigil.mob (a player's kill of a LEVELLED mob: Unique 0.2), sigil.bag (each roll of a sigil.bagLists drop list = SkyyExploration's
   Loot Bag / Lost Treasure / Magic Box table + the vanilla encounter prefab chests that use it: Unique 2), sigil.mini (sigil.miniWords
   roles: Rare 4, Legendary 1.5), sigil.boss (sigil.bossWords roles = every full boss: Legendary 6, Fabled 2, Mythic 0.5 at zone 1) x
   sigil.bossZone (zone from the mob level 1-20 / 21-30 / 31-45 / 46+: x1, 1.5, 2, 3). Mob kills: GearDeathMark (the extra-mob-roll point,
   vanilla's own spawn); bags: GearSigBag around the list's container (GearStick / GearNormDrop's way, all three wrappers compose).
   CRITIC FIX 1: the bridge key "gear:sigil:drops" (Boolean, TRUE while sigil.drops + part.sigils are on; published by GearSigDrop.ensure =
   start / every config apply / the 30 s look; removed at shutdown) - SkyyArmory 0.1.30 skips its own boss roll while it is TRUE (one roll
   per boss). DEPLOY TOGETHER: SkyyGear 0.3.14 <-> SkyyArmory 0.1.30.
4. TILL AREA EVERYWHERE (Skyy "everywhere no cost (forever tools have no durability.)"): hoe.areaElsewhere defaults ON (island worlds still ask
   SkyyIslands' build permission); the extra blocks never cost durability (as before). ONE-TIME UPDATE migrate0314 (PROJECT-RULES 4): a
   one-line hoe.areaElsewhere=false / sigil.mythicUse=false (exactly the old default, the entry Properties keeps) -> true, value text only;
   hand-edited values kept + noted; a verified History copy first, atomic write, one config-changes.log row each (status ok = Undo), the
   run-once marker comment at the end (a fresh file carries it), every other byte and line ending kept.
SAVED DATA: registry keys harvAuto (1 / kit / undone) / harvAutoAt / harvAutoHow / harvAutoUndoAt, harv.auto / harv.src (journal), harvUndo.pend /
harvUndo.hoeNew (undo journal); Skyy_SkyyGear/harvmerge/<pk>.log + harvmerge/history/. New Server Setup rows (absent = default): harvester.only,
farm.crudeT1, sigil.drops, sigil.mob, sigil.bag, sigil.mini, sigil.boss, sigil.bossZone, sigil.miniWords, sigil.bossWords, sigil.bagLists.
ROLLBACK 0.3.14 -> 0.3.13: merged profiles stay merged (0.3.13 knows harv=1); profiles born on 0.3.14 have no hoe and 0.3.13 would give a
Crude hoe at /hoe only; the swing sweep returns to vanilla (the Harvester's vars name SkyyGear_Harvest_Crop - an unknown type on 0.3.13: its
items still load from 0.3.14's jar only); the two config lines stay true (Undo in Server Setup's change log). Item-safe.
"""
import os
import re
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.13.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.14.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.13"' in s and "GENERATED by tools/gear_0_3_13_patch.py" in s and "0.3.14" not in s, "not the generated 0.3.13 script"
assert "GearHarv" not in s and "SIGD_" not in s and "HARV_ONLY" not in s and "migrate0314" not in s
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
if _set is not None and _set.get("SkyyGear") != "0.3.13":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.13" % _set.get("SkyyGear"))

SIG_MOB_DEF = "0.2,0,0,0,0"
SIG_BAG_DEF = "2,0,0,0,0"
SIG_MINI_DEF = "0,4,1.5,0,0"
SIG_BOSS_DEF = "0,0,6,2,0.5"
SIG_ZONE_DEF = "1,1.5,2,3"
SIG_MINIW_DEF = "Elite,Golem,Yeti,Rex,Ogre"
SIG_BOSSW_DEF = "Boss,Guardian,Duke,Dragon,Chieftain,Hedera"
SIG_BAGS_DEF = "Zone1_Encounters_,Zone2_Encounters_,Zone3_Encounters_,Zone4_Encounters_"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.13 - build script (javassist via jpype). GENERATED by tools/gear_0_3_13_patch.py from the LIVE 0.3.12 (itself GENERATED by
tools/gear_0_3_12_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.13.py -> SkyyGear/SkyyGear-0.3.13.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.13.py
''', '''"""SkyyGear 0.3.14 - build script (javassist via jpype). GENERATED by tools/gear_0_3_14_patch.py from the LIVE 0.3.13 (itself GENERATED by
tools/gear_0_3_13_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.14.py -> SkyyGear/SkyyGear-0.3.14.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.14.py

0.3.14 = ONE FARMING TOOL + SWEEP TIER + SIGILS ON MINING SETS / SIGIL DROPS + TILL AREA EVERYWHERE (notes: tools/gear_0_3_14_patch.py): the
lifelong hoe and sickle retire - every profile starts with a Crude Harvester (+ the can), an existing hoe + sickle merge ONCE into one Harvester
(best tier / rarity, every line, the higher points; History copy + undo record, /gear harvmerge undo); a Crude farming tool is T1 on crops and
the Harvester's swing sweep reaps only crops of its tier or lower (one up: one at a time, half XP); Sigils work on Mining Set armor, the Mythic
Sigil works on the Anvil, Sigils drop from mobs / Loot Bags / mini bosses / bosses (Server Setup rows); the hoe area tills everywhere.

--- 0.3.13 notes ---
''')
rep('VERSION = "0.3.13"\n', 'VERSION = "0.3.14"\n')

# ================================================================================================================ Server Setup rows + GearCfg
after('''    ("lifelong.stickCost", "Enchanted Sticks per tier-up", "lifelong", "text", "0,0,0,2,4,8,16,32", "1", "60", "", "", "live,danger",
     "Crude to Onyxium: Enchanted Sticks a tool tier-up INTO that tier costs extra (8 numbers 0-999).", "field:GearCfg.LL_STICKS;check=GearUp.checkSticks"),
''', '''    # 0.3.14 ONE FARMING TOOL + SWEEP TIER + SIGIL DROPS (tools/gear_0_3_14_patch.py)
    ("harvester.only", "One farming tool: the Harvester", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "No hoe / sickle: new profiles get a Crude Harvester; a hoe + sickle merge once (/gear harvmerge).", "field:GearCfg.HARV_ONLY"),
    ("farm.crudeT1", "Farming tool tiers match the crops", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "Crude reaps Wheat / Lettuce, each tier the next pair; the sweep skips crops above the tool's tier.", "field:GearCfg.FARM_T1"),
    ("sigil.drops", "Sigil drops (mobs, bags, bosses)", "smithing", "bool", "true", "", "", "", "", "live,danger",
     "Sigils drop by the rows below. Off = none from SkyyGear (SkyyArmory's boss roll has its own row).", "field:GearCfg.SIGD_ON"),
    ("sigil.mob", "Sigil %% per mob kill", "smithing", "text", "%(mob)s", "1", "80", "", "", "live,danger",
     "Unique, Rare, Legendary, Fabled, Mythic: %% per kill of a levelled mob (one Sigil at most).", "field:GearCfg.SIGD_MOB;check=GearSigDrop.check"),
    ("sigil.bag", "Sigil %% per Loot Bag roll", "smithing", "text", "%(bag)s", "1", "80", "", "", "live,danger",
     "Unique..Mythic: %% per roll of a sigil.bagLists list (Loot Bag, Lost Treasure, Magic Box).", "field:GearCfg.SIGD_BAG;check=GearSigDrop.check"),
    ("sigil.mini", "Sigil %% per mini boss kill", "smithing", "text", "%(mini)s", "1", "80", "", "", "live,danger",
     "Unique..Mythic: %% per kill of a sigil.miniWords mob (Rare + Legendary).", "field:GearCfg.SIGD_MINI;check=GearSigDrop.check"),
    ("sigil.boss", "Sigil %% per boss kill (zone 1)", "smithing", "text", "%(boss)s", "1", "80", "", "", "live,danger",
     "Unique..Mythic at zone 1, times sigil.bossZone higher up (Legendary + Mythic).", "field:GearCfg.SIGD_BOSS;check=GearSigDrop.check"),
    ("sigil.bossZone", "Boss Sigil chance x by zone", "smithing", "text", "%(zone)s", "1", "60", "", "", "live,danger",
     "Zones 1-4 (mob level 1-20, 21-30, 31-45, 46+): the boss row times this (4 numbers 0-20).", "field:GearCfg.SIGD_ZONE;check=GearSigDrop.check"),
    ("sigil.miniWords", "Mini boss role words", "smithing", "text", "%(miniw)s", "0", "200", "", "", "live,danger",
     "Whole parts of the role name (split at _). Boss words win: Golem_Guardian_Void is a boss.", "field:GearCfg.SIGD_MINIW"),
    ("sigil.bossWords", "Boss role words", "smithing", "text", "%(bossw)s", "0", "200", "", "", "live,danger",
     "Whole parts of the role name: every full boss may drop Legendary, Fabled and Mythic Sigils.", "field:GearCfg.SIGD_BOSSW"),
    ("sigil.bagLists", "Loot Bag drop lists", "smithing", "text", "%(bags)s", "0", "300", "", "", "live,danger",
     "Drop list id starts that may add a Sigil (SkyyExploration's Loot Bags roll these).", "field:GearCfg.SIGD_BAGS;after=GearSigDrop.refresh"),
''' % {"mob": SIG_MOB_DEF, "bag": SIG_BAG_DEF, "mini": SIG_MINI_DEF, "boss": SIG_BOSS_DEF, "zone": SIG_ZONE_DEF, "miniw": SIG_MINIW_DEF,
       "bossw": SIG_BOSSW_DEF, "bags": SIG_BAGS_DEF})
rep('''    ("sigil.mythicUse", "Mythic Sigil works on the Anvil", "smithing", "bool", "false", "", "", "", "", "live,danger",
     "Off = Mythic stays boss-only: a Mythic Sigil cannot make an item Mythic on the Anvil.", "field:GearCfg.SIG_MY"),''',
    '''    ("sigil.mythicUse", "Mythic Sigil works on the Anvil", "smithing", "bool", "true", "", "", "", "", "live,danger",
     "On = a Mythic Sigil (from bosses) makes an item Mythic on the Anvil. Off = it cannot.", "field:GearCfg.SIG_MY"),''')
rep('''    ("hoe.areaElsewhere", "Area tilling outside islands", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "Off = the extra blocks are tilled only on island worlds where you may build.", "field:GearCfg.HOE_ELSE"),''',
    '''    ("hoe.areaElsewhere", "Area tilling outside islands", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "On = the till area works in every world (islands still need build rights). No durability cost.", "field:GearCfg.HOE_ELSE"),''')
rep('''           "normal.off", "normal.removeOwned", "normal.extraIds", "lifelong.stickCost"}''', '''           "normal.off", "normal.removeOwned", "normal.extraIds", "lifelong.stickCost",
           # 0.3.14: one farming tool (a lifelong merge), the crop sweep tier (Farming XP / Fortune), Sigil drops (rarity = economy)
           "harvester.only", "farm.crudeT1", "sigil.drops", "sigil.mob", "sigil.bag", "sigil.mini", "sigil.boss", "sigil.bossZone",
           "sigil.miniWords", "sigil.bossWords", "sigil.bagLists"}''')
after('''assert all(32 <= ord(_c) < 127 for _c in G313_HEAD) and "=" not in G313_HEAD
''', '''G314_HEAD = "# ---- one farming tool, the sweep tier, Sigil drops (SkyyGear 0.3.14) ----"
G314_ROWK = ["harvester.only", "farm.crudeT1", "sigil.drops", "sigil.mob", "sigil.bag", "sigil.mini", "sigil.boss", "sigil.bossZone", "sigil.miniWords",
             "sigil.bossWords", "sigil.bagLists"]
assert all(32 <= ord(_c) < 127 for _c in G314_HEAD) and "=" not in G314_HEAD
# 0.3.14 ONE-TIME UPDATE migrate0314: the run-once marker (a comment line; a fresh file carries it right under G314_HEAD)
H4_MARK_ID = "SkyyGear 0.3.14 default update"
H4_WHO = "SkyyGear 0.3.14"
H4_KEYS = ["hoe.areaElsewhere", "sigil.mythicUse"]
H4_MARK = ("# %s (Skyy 2026-10-16): the hoe / Harvester till area works everywhere and the Mythic Sigil works on the Anvil (both default true)"
           % H4_MARK_ID)
assert all(32 <= ord(_c) < 127 for _c in H4_MARK) and "=" not in H4_MARK and H4_MARK.startswith("# ")
''')
after('''    L += ["", G313_HEAD]        # 0.3.13: the new rows (no one-time update adds them; absent = the default)
    for k in G313_ROWK:
        scal(k)
''', '''    L += ["", G314_HEAD]        # 0.3.14: the new rows (no one-time update adds them; absent = the default) + the migrate0314 marker
    L += [H4_MARK]
    for k in G314_ROWK:
        scal(k)
''')
rep('''("SIG_ON", "boolean", "true"), ("SIG_MY", "boolean", "false"),''', '''("SIG_ON", "boolean", "true"), ("SIG_MY", "boolean", "true"),''')
rep('''("HOE_ELSE", "boolean", "false"),''', '''("HOE_ELSE", "boolean", "true"),''')
rep('''              ("LL_STICKS", "String", jstr("0,0,0,2,4,8,16,32"))]''', '''              ("LL_STICKS", "String", jstr("0,0,0,2,4,8,16,32")),
              # 0.3.14 one farming tool, the sweep tier, Sigil drops
              ("HARV_ONLY", "boolean", "true"), ("FARM_T1", "boolean", "true"), ("SIGD_ON", "boolean", "true"),
              ("SIGD_MOB", "String", jstr("%s")), ("SIGD_BAG", "String", jstr("%s")), ("SIGD_MINI", "String", jstr("%s")),
              ("SIGD_BOSS", "String", jstr("%s")), ("SIGD_ZONE", "String", jstr("%s")), ("SIGD_MINIW", "String", jstr("%s")),
              ("SIGD_BOSSW", "String", jstr("%s")), ("SIGD_BAGS", "String", jstr("%s"))]''' % (SIG_MOB_DEF, SIG_BAG_DEF, SIG_MINI_DEF, SIG_BOSS_DEF,
                                                                                            SIG_ZONE_DEF, SIG_MINIW_DEF, SIG_BOSSW_DEF, SIG_BAGS_DEF))
rep('''  SIG_MY = pbool(p, "sigil.mythicUse", false);          // fixer 2: Mythic is boss-only unless the owner allows the Mythic Sigil''',
    '''  SIG_MY = pbool(p, "sigil.mythicUse", !Boolean.getBoolean("skyy.harness.no314"));          // 0.3.14: default ON (Skyy 2026-10-16 "let it work")''')
rep('''  HOE_ELSE = pbool(p, "hoe.areaElsewhere", false);''',
    '''  HOE_ELSE = pbool(p, "hoe.areaElsewhere", !Boolean.getBoolean("skyy.harness.no314"));          // 0.3.14: default ON (Skyy 2026-10-16 "everywhere")''')
after('''  LL_STICKS = Boolean.getBoolean("skyy.harness.noNormOff") ? "0,0,0,0,0,0,0,0" : ptext(p, "lifelong.stickCost", "0,0,0,2,4,8,16,32").trim();
''', '''  // 0.3.14 (HARNESS SEAM ONLY: -Dskyy.harness.no314=true = the 0.3.13 flow the older harness children were written for)
  HARV_ONLY = pbool(p, "harvester.only", true) && !Boolean.getBoolean("skyy.harness.no314");
  FARM_T1 = pbool(p, "farm.crudeT1", true) && !Boolean.getBoolean("skyy.harness.no314");
  SIGD_ON = pbool(p, "sigil.drops", true) && !Boolean.getBoolean("skyy.harness.no314");
  MINE_SIG = !Boolean.getBoolean("skyy.harness.no314");
  SIGD_MOB = ptext(p, "sigil.mob", "%s").trim();
  SIGD_BAG = ptext(p, "sigil.bag", "%s").trim();
  SIGD_MINI = ptext(p, "sigil.mini", "%s").trim();
  SIGD_BOSS = ptext(p, "sigil.boss", "%s").trim();
  SIGD_ZONE = ptext(p, "sigil.bossZone", "%s").trim();
  SIGD_MINIW = ptext(p, "sigil.miniWords", "%s").trim();
  SIGD_BOSSW = ptext(p, "sigil.bossWords", "%s").trim();
  SIGD_BAGS = ptext(p, "sigil.bagLists", "%s").trim();
''' % (SIG_MOB_DEF, SIG_BAG_DEF, SIG_MINI_DEF, SIG_BOSS_DEF, SIG_ZONE_DEF, SIG_MINIW_DEF, SIG_BOSSW_DEF, SIG_BAGS_DEF))
after('''F(gcf, "public static final String GQ_NEW = %s;" % jstr(GQ_NEW))
''', '''F(gcf, "public static volatile boolean MINE_SIG = true;")          # 0.3.14: Sigils on Mining Set pieces (no row: Skyy's answer; false = the harness seam only)
F(gcf, "public static final String H4_MARK = %s;" % jstr(H4_MARK))          # 0.3.14 migrate0314
F(gcf, "public static final String H4_MARK_ID = %s;" % jstr(H4_MARK_ID))
F(gcf, "public static final String H4_WHO = %s;" % jstr(H4_WHO))
F(gcf, "public static final String[] H4_KEYS = %s;" % jarr(H4_KEYS))
''')

# ================================================================================================================ 4: migrate0314 (the two default flips)
before('''# 0.2.1 ready line part: the base stats in force (live values)
M(gcf, r"""
public static String baseText() {''', r'''# ---- 0.3.14 ONE-TIME UPDATE migrate0314 (PROJECT-RULES section 4; tools/gear_0_3_14_patch.py item 4). Pure text step: null = the marker is
# already in a comment line (a fresh 0.3.14 file carries it). Else { new text, "hoe.areaElsewhere false -> true, ..." ("" = no value changed),
# String[] notes, String[] log rows (key, old, new) }. Per key of H4_KEYS: every ONE-LINE entry holding exactly the old default (false, any case)
# is rewritten when the LAST entry (the one Properties keeps) holds it (value text only: key, separator, CR kept). The marker line goes to the
# END of the file (chEnd: the end-of-file continuation trap). Nothing else is touched.
M(gcf, r"""
public static boolean h4Old(String v) { return v != null && v.trim().equalsIgnoreCase("false"); }""")
M(gcf, r"""
public static Object[] h4Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(H4_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int nk = H4_KEYS.length;
  int[] last = new int[nk];
  boolean[] lastOne = new boolean[nk];
  for (int i = 0; i < nk; i++) last[i] = -1;
  java.util.HashSet cand = new java.util.HashSet();
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    for (int i = 0; key != null && i < nk; i++) {
      if (!key.equals(H4_KEYS[i])) continue;
      last[i] = k;
      lastOne[i] = e == k;
      if (e == k && h4Old(@PKG@.CfgFile.value(l, k))) cand.add(i + ":" + k);
    }
    k = e + 1;
  }
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.HashSet at = new java.util.HashSet();
  for (int i = 0; i < nk; i++) {
    String ov = pp.getProperty(H4_KEYS[i]);
    boolean rw = ov != null && h4Old(ov) && lastOne[i] && last[i] >= 0 && cand.contains(i + ":" + last[i]);
    if (rw) {
      java.util.Iterator it = cand.iterator();
      while (it.hasNext()) {
        String c = (String) it.next();
        if (c.startsWith(i + ":")) at.add(Integer.valueOf(Integer.parseInt(c.substring(c.indexOf(':') + 1))));
      }
      if (chg.length() > 0) chg.append(", ");
      chg.append(H4_KEYS[i]).append(" false -> true");
      rows.add(H4_KEYS[i]);
      rows.add("false");
      rows.add("true");
    } else if (ov != null) {
      notes.add(H4_KEYS[i] + "=" + @PKG@.CfgRows.oneLine(ov.trim()) + " kept (not the 0.3.13 default false, or not one plain line) - the new default would be true");
    }
  }
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(H4_MARK);
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    if (at.contains(Integer.valueOf(i))) {
      String s2 = (String) l.get(i);
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + "true" + (raw[i].endsWith("\r") ? "\r" : ""));
    } else out.add(raw[i]);
  }
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) notes.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
# one config-changes.log line in the kit's row format; status "ok" = SkyyMenu offers Undo (back to false passes the bool row)
M(gcf, r"""
public static String h4Log(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + H4_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(), right after migrate031 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), the
# change-log rows, one INFO line (+ one per note), gear.log; "" = nothing done (no file, marker already there, the harness seam, or a failure - WARN,
# file untouched, the next start tries again; the loader then reads whatever the two lines hold)
M(gcf, r"""
public static synchronized String migrate0314() {
  java.nio.file.Path f = FILE;
  if (f == null || Boolean.getBoolean("skyy.harness.no314")) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = h4Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), H4_WHO, "before the 0.3.14 default update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.3.14 defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(h4Log(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] notes = (String[]) r[2];
    String msg = chg.length() > 0
      ? "config.properties updated to the 0.3.14 defaults: " + chg + " (the till area works everywhere, the Mythic Sigil works on the Anvil; Undo in Server Setup's change log; the old file is kept in config-history)"
      : "config.properties: the 0.3.14 default update marker was added - no value changed";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.3.14 defaults: " + (chg.length() > 0 ? chg : "no value changed") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.3.14 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
''')
rep('''  @PKG@.GearCfg.migrate031();          // 0.3.1: gate.nextFactor 0.1 -> 0.4 (only the old default)
''', '''  @PKG@.GearCfg.migrate031();          // 0.3.1: gate.nextFactor 0.1 -> 0.4 (only the old default)
  @PKG@.GearCfg.migrate0314();          // 0.3.14: hoe.areaElsewhere + sigil.mythicUse false -> true (only the old default)
''')

# ================================================================================================================ 2: the sweep tier rule (GearLL)
after('''F(gll, "public static final String HARV_LAD = %s;" % jstr(",".join(HARV_IDS)))
''', '''F(gll, "public static final int HARV_TOP = %d;" % dict(TOOL_TIERS)[HARV_TIERS[-1]])          # 0.3.14: the Harvester ladder's top tier (Thorium = 3)
assert dict(TOOL_TIERS)[HARV_TIERS[-1]] == 3 and dict(TOOL_TIERS)["Crude"] == 0 and dict(TOOL_TIERS)["Copper"] == 1
''')
rep('''    if (c == 4) {
      int hm = m > FAMMAX[4] ? FAMMAX[4] : m;
      int hd = hm - 1;
      return new int[] { hd <= 0 ? 0 : (hd <= 1 ? 1 : 2), c, m, 0, 4, hd < 0 ? 0 : hd };
    }''', '''    if (c == 4) {
      int hm = m > FAMMAX[4] ? FAMMAX[4] : m;
      int hd = hm - 1;          // 0.3.14 (Skyy 2026-10-16 "Full on starter crops"): bare hands keep the 0.3.5 rule
      return new int[] { hd <= 0 ? 0 : (hd <= 1 ? 1 : 2), c, m, 0, 4, hd < 0 ? 0 : hd, FAMMAX[4] };
    }''')
rep('''  int t = tier(id);
  int te = t < 1 ? 1 : t;
  int fm = f >= 0 && f < FAMMAX.length ? FAMMAX[f] : 7;
  int me = m > fm ? fm : m;
  int d = me - te;
  int lim = c == 4 ? 1 : 2;          // 0.3.3: crops refuse at two up, ore / logs at three up
  return new int[] { d <= 0 ? 0 : (d <= lim ? 1 : 2), c, m, t, f, d < 0 ? 0 : d };''', '''  int t = tier(id);
  int te = t < 1 ? 1 : t;
  int fm = f >= 0 && f < FAMMAX.length ? FAMMAX[f] : 7;
  int sh = 0;
  if (c == 4 && @PKG@.GearCfg.FARM_T1) {          // 0.3.14 (Skyy 2026-10-16 "crude is T1 copper is T2" + "Full on starter crops"): a farming tool's tier
    te = (t < 0 ? 0 : t) + 1;          // = the crops it reaps in full: Crude = Wheat / Lettuce, Copper = Carrot / Corn, Iron = Cauliflower / Turnip ...
    fm = (harv(id) ? HARV_TOP : fm) + 1;          // the family's top (the Harvester's own: Thorium) still covers every crop above it
    sh = 1;
  }
  int me = m > fm ? fm : m;
  int d = me - te;
  int lim = c == 4 ? 1 : 2;          // 0.3.3: crops refuse at two up, ore / logs at three up
  return new int[] { d <= 0 ? 0 : (d <= lim ? 1 : 2), c, m, t, f, d < 0 ? 0 : d, fm, sh };''')
rep('''M(gll, "public static int fullT(int[] d) { int fm = d[4] >= 0 && d[4] < FAMMAX.length ? FAMMAX[d[4]] : 7; return d[2] > fm ? fm : d[2]; }")''',
    '''M(gll, "public static int fullT(int[] d) { int fm = d.length > 6 ? d[6] : (d[4] >= 0 && d[4] < FAMMAX.length ? FAMMAX[d[4]] : 7); return d[2] > fm ? fm : d[2]; }")          # 0.3.14: [6] = the top decideI used''')
rep('''  @PKG@.GearGate.popup(pr, u, icon, "Too tough for your " + tn, "This crop needs at least " + an(tname(fullC - 1)) + " " + (d[4] == 5 ? "sickle" : "hoe") + " (" + tname(fullC) + " for full Farming XP). Tier yours up on the Anvil (/smithing).");''',
    '''  String nn = icon != null && harv(icon) ? "Harvester" : (d[4] == 5 ? "sickle" : "hoe");          // 0.3.14: the Harvester says so
  int sh = d.length > 7 ? d[7] : 0;          // 0.3.14: farm.crudeT1 - a tool of tier t reaps crops of t + 1 in full
  int lo = fullC - 1 - sh;
  int fu = fullC - sh;
  if (lo < 0) lo = 0;
  if (fu < 0) fu = 0;
  @PKG@.GearGate.popup(pr, u, icon, "Too tough for your " + tn, "This crop needs at least " + an(tname(lo)) + " " + nn + " (" + tname(fu) + " for full Farming XP). Tier yours up on the Anvil (/smithing).");''')
rep('''public static String onlyFor(int f, int t, String def) {
  if ((f != 4 && f != 5) || !@PKG@.GearCfg.GATE_ON || !@PKG@.GearCfg.LL_ON) return def;
  String key = f + ":" + t;
  Object o = ONLY.get(key);
  if (o instanceof String) return (String) o;
  StringBuilder sb = new StringBuilder();
  int fm = FAMMAX[f];
  int te = t < 1 ? 1 : t;          // 0.3.1: a Crude / Wood hoe counts as tier 1''', '''public static String onlyFor2(int f, int t, boolean hv, String def) {
  if ((f != 4 && f != 5) || !@PKG@.GearCfg.GATE_ON || !@PKG@.GearCfg.LL_ON) return def;
  boolean t1 = @PKG@.GearCfg.FARM_T1;
  String key = f + ":" + t + ":" + (hv ? "h" : "-") + ":" + (t1 ? "1" : "0");
  Object o = ONLY.get(key);
  if (o instanceof String) return (String) o;
  StringBuilder sb = new StringBuilder();
  int fm = t1 ? (hv ? HARV_TOP : FAMMAX[f]) + 1 : FAMMAX[f];          // 0.3.14: the Harvester's own top (decideI's rule)
  int te = t1 ? (t < 0 ? 0 : t) + 1 : (t < 1 ? 1 : t);          // 0.3.1: a Crude / Wood hoe counts as tier 1; 0.3.14 (farm.crudeT1): tool tier t reaps crops of t + 1''')
after('''  String v = sb.toString();
  ONLY.put(key, v);
  return v;
}""")
''', '''M(gll, "public static String onlyFor(int f, int t, String def) { return onlyFor2(f, t, false, def); }")          # 0.3.14: the old shape (no Harvester)
''')
rep('''  else postX(u, (int) st[1], tf + af, @PKG@.GearLL.onlyFor((int) st[0], (int) st[7], ONLY[(int) st[0]]), aw + tw);     // 0.3.0: a hoe / sickle's crops''',
    '''  else postX(u, (int) st[1], tf + af, @PKG@.GearLL.onlyFor2((int) st[0], (int) st[7], s != null && !s.isEmpty() && @PKG@.GearLL.harv(s.getItemId()), ONLY[(int) st[0]]), aw + tw);     // 0.3.0: a hoe / sickle's crops; 0.3.14: + the Harvester's top''')

# ================================================================================================================ 2: the Harvester's swing = our interaction (assets)
after('''CAN_FILES["Server/Item/Animations/SkyyGear/%s.json" % HARV_ANIM] = json.dumps(_hv_anim, indent=2)
''', '''# 0.3.14 THE SWEEP TIER: the Harvester's swing selectors run OUR HitBlock interaction (type SkyyGearHarvest = vanilla HarvestCrop + the tier rule,
# GearHarvCrop) - no AdjustHeldItemDurability step (Skyy 2026-10-16 "forever tools have no durability"); the vanilla Failed path stays (bushes /
# grass / a one-tier-up crop break the ordinary way)
HARV_INT_ID = "SkyyGear_Harvest_Crop"
_vsel = json.loads(AZ.read("Server/Item/Interactions/Weapons/Sickle/Attacks/Swing_Left/Sickle_Swing_Left_Selector.json").decode("utf-8-sig"))
_vhb = _vsel["HitBlock"]["Interactions"][0]
assert _vhb["Type"] == "HarvestCrop" and _vhb.get("Failed") == "Block_Break_Adventure" and _vhb.get("RequireNotBroken") is True, "vanilla's sickle HitBlock changed: %s" % _vhb
CAN_FILES["Server/Item/Interactions/SkyyGear/Harvester/%s.json" % HARV_INT_ID] = json.dumps({
    "Type": "SkyyGearHarvest", "RequireNotBroken": True, "Failed": _vhb["Failed"]}, indent=2)
''')
rep('''        "Interactions": {"Primary": _prim, "Secondary": "Hoe_Till"},
        "InteractionConfig": dict(az_get("Tool_Hoe_Crude", "InteractionConfig"), UseDistance={"Adventure": 5, "Creative": 6}), "MaxStack": 1}, indent=2)''',
    '''        "Interactions": {"Primary": _prim, "Secondary": "Hoe_Till"}, "InteractionVars": _harv_vars(_sic),          # 0.3.14: the swing's HitBlock = ours
        "InteractionConfig": dict(az_get("Tool_Hoe_Crude", "InteractionConfig"), UseDistance={"Adventure": 5, "Creative": 6}), "MaxStack": 1}, indent=2)''')
before('''HARV_ITEMS = {}
for _t, _hid in zip(HARV_TIERS, HARV_IDS):''', '''def _harv_vars(sic):
    """0.3.14: the base sickle's whole InteractionVars (the item's own map replaces the Parent's) with both swing selectors' HitBlock = ours"""
    iv = json.loads(json.dumps(az_get(sic, "InteractionVars")))
    for side in ("Left", "Right"):
        k = "Swing_%s_Selector" % side
        ent = iv[k]["Interactions"]
        assert len(ent) == 1 and ent[0].get("Parent") == "Sickle_Swing_%s_Selector" % side and "HitBlock" not in ent[0], (sic, k, ent)
        ent[0]["HitBlock"] = {"Interactions": [HARV_INT_ID]}
    return iv


''')
rep('''    CAN_LANG.append("items.%s.description = %s" % (_hid, TT.described(_hid, "Your lifelong hoe and sickle in one: right-click tills soil, a swing reaps crops and cuts plants.")))''',
    '''    CAN_LANG.append("items.%s.description = %s" % (_hid, TT.described(_hid, "Your lifelong farming tool: right-click tills soil; a swing reaps every crop of its tier and lower (Crude: Wheat and Lettuce) and cuts plants - one tier higher breaks one at a time for half Farming XP.")))''')

# ================================================================================================================ 3: Sigils - the Mythic text, Mining Set pieces, the tier-up rule
rep('''        SIG_LANG.append("items.%s.description = A boss treasure. Mythic gear comes from bosses - this Sigil works on the Anvil only where the server allows it. Never sold on the Bazaar." % _sid)''',
    '''        SIG_LANG.append("items.%s.description = A boss treasure: raises an item to Mythic on the Anvil (/smithing) - skips tiers, upward only. Reforge it after to fill the new slots. Never sold on the Bazaar." % _sid)          # 0.3.14: usable (sigil.mythicUse on)''')
rep('''  if (!@PKG@.GearData.identified(d)) return "Identify it first" + @PKG@.GearCfg.idHow() + ".";
  int r = @PKG@.GearData.rarity(d);
  if (r == @PKG@.GearDefs.R_SET || @PKG@.GearSet.of(d) != null) {
    String gsk''', '''  if (!@PKG@.GearData.identified(d)) return "Identify it first" + @PKG@.GearCfg.idHow() + ".";
  int r = @PKG@.GearData.rarity(d);
  if (minePiece(id, d)) { if (r == @PKG@.GearDefs.R_SET) r = 0; }          // 0.3.14 (Skyy 2026-10-16 "allow"): a Mining Set piece takes a Sigil (Set counts as Normal)
  else if (r == @PKG@.GearDefs.R_SET || @PKG@.GearSet.of(d) != null) {
    String gsk''')
before('''# why an item cannot take Sigil rarity R (null = it can); d = its document (GearForge.docOf)
M(gsig, r"""
public static String why(@IS@ it, @BD@ d, int R) {''', r'''# 0.3.14 SIGILS ON MINING SETS: a Mining Set piece (a metal piece of GearMine with no set field or a mining_<tier> one; not Untiered) - its Set rarity
# counts as Normal for a Sigil; the set field stays (the full-set bonus still counts, extra on top). baseR = the rarity a Sigil compares with
M(gsig, r"""
public static boolean minePiece(String id, @BD@ d) {
  if (!@PKG@.GearCfg.MINE_SIG || id == null || d == null || !@PKG@.GearMine.isPiece(id)) return false;
  int r = @PKG@.GearData.rarity(d);
  if (r == @PKG@.GearDefs.R_UT) return false;
  String sid = @PKG@.GearSet.of(d);
  return sid == null || sid.toLowerCase().startsWith("mining_");
}""")
M(gsig, r"""
public static int baseR(String id, @BD@ d) {
  if (d == null) return 0;
  int r = @PKG@.GearData.rarity(d);
  return r == @PKG@.GearDefs.R_SET && minePiece(id, d) ? 0 : r;
}""")
''')
rep('''public void anSigil(@UCB@ b, @UEB@ ev, @IS@ sel, @BD@ d, int[] have) {
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);''', '''public void anSigil(@UCB@ b, @UEB@ ev, @IS@ sel, @BD@ d, int[] have) {
  int r = d == null ? 0 : @PKG@.GearSigil.baseR(sel == null ? null : sel.getItemId(), d);          // 0.3.14: a Mining Set piece counts as Normal''')
rep('''  @BD@ d = @PKG@.GearForge.docOf(this.selId, it.getMetadata());
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  int[] ch = @PKG@.GearSigil.choices(@PKG@.GearSigil.carried(inv), r);''', '''  @BD@ d = @PKG@.GearForge.docOf(this.selId, it.getMetadata());
  int r = d == null ? 0 : @PKG@.GearSigil.baseR(this.selId, d);          // 0.3.14: a Mining Set piece counts as Normal
  int[] ch = @PKG@.GearSigil.choices(@PKG@.GearSigil.carried(inv), r);''')
rep('''  if (skillOf(id) == null || d == null) return false;
  int r = @PKG@.GearData.rarity(d);
  if (r != @PKG@.GearDefs.R_SET && r > 4) return false;''', '''  if (skillOf(id) == null || d == null) return false;
  int r = @PKG@.GearData.rarity(d);
  if (r != @PKG@.GearDefs.R_SET && r > 4 && !(r == @PKG@.GearDefs.R_MY && @PKG@.GearCfg.MINE_SIG && @PKG@.GearMine.isPiece(id))) return false;          // 0.3.14: a Mythic (Sigil) mining piece still tiers up''')

# ================================================================================================================ 1: the kit, the Tools tab, the merge helpers (GearLife)
rep('''    int[] b = best(inv, k);
    if (b != null) { if (mark(pr, inv, pk, P, k, b[0], b[1], "mark")) { done++; ch = true; } continue; }
    int g = give(pr, inv, pk, P, k, @PKG@.GearLL.KCRUDE[k], "give");''', '''    int[] b = best(inv, k);
    if (b != null) { if (mark(pr, inv, pk, P, k, b[0], b[1], "mark")) { done++; ch = true; } continue; }
    // 0.3.14 (harvester.only; Skyy 2026-10-16 "lets retire the hoe and sickle, and start with the crude farming multitool"): no hoe is given, the
    // sickle kind's tool is the Crude Harvester (a hoe / sickle the player carries was marked above - it merges at the next look)
    boolean rt = @PKG@.GearCfg.HARV_ON && @PKG@.GearCfg.HARV_ONLY;
    if (k == 2 && rt) { done++; continue; }
    String gid = k == 3 && rt && @PKG@.Gear.item(@PKG@.GearLL.HARV_PRE + "Crude") != null ? @PKG@.GearLL.HARV_PRE + "Crude" : @PKG@.GearLL.KCRUDE[k];
    int g = give(pr, inv, pk, P, k, gid, "give");''')
rep('''    pr.sendMessage(@MSG@.raw("[Gear] Lifelong tools: you keep ONE pickaxe, hatchet, hoe and sickle for life now. They level with your skills (1 Upgrade Point per level: /toolpoints) and tier up on the Anvil (/smithing). Lost one? /pickaxe, /hatchet, /hoe or /sickle. Wrong tool picked? Hold the right one and type /lifelong (once per kind).").color(@PKG@.GearDefs.C_LABEL));''',
    '''    boolean one = @PKG@.GearCfg.HARV_ON && @PKG@.GearCfg.HARV_ONLY;          // 0.3.14: the Harvester is the farming tool
    pr.sendMessage(@MSG@.raw("[Gear] Lifelong tools: you keep ONE pickaxe, hatchet, " + (one ? "Harvester (hoe + sickle in one)" : "hoe and sickle") + " for life now. They level with your skills (1 Upgrade Point per level: /toolpoints) and tier up on the Anvil (/smithing). Lost one? /pickaxe, /hatchet, " + (one ? "/harvester" : "/hoe or /sickle") + ". Wrong tool picked? Hold the right one and type /lifelong (once per kind).").color(@PKG@.GearDefs.C_LABEL));''')
rep('''public static boolean shown(int k, java.util.Properties P) {
  if (k == @PKG@.GearLL.POLE && @PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) return false;
  if (k == 2 && @PKG@.GearLL.merged(P)) return false;''', '''public static boolean shown(int k, java.util.Properties P) {
  if (k == @PKG@.GearLL.POLE && @PKG@.Gear.item(@PKG@.GearLL.KCRUDE[k]) == null) return false;
  if (k == 2 && @PKG@.GearLL.merged(P)) return false;
  if (k == 2 && @PKG@.GearCfg.HARV_ON && @PKG@.GearCfg.HARV_ONLY && P != null && P.getProperty("hoe.uid") == null) return false;          // 0.3.14: no hoe row without a hoe''')
rep('''  P.remove("harv.at");
}""")''', '''  P.remove("harv.at");
  P.remove("harv.auto");          // 0.3.14: the automatic merge's journal flags
  P.remove("harv.src");
}""")''')
before('''# THE COMMIT of a merge: the points, the hoe kind leaves the registry (every hoe.* key), harv=1 (+ when, + the hoe's uid), the sickle names the''',
       r'''# 0.3.14 THE AUTOMATIC MERGE's points (Skyy 2026-10-16 "best tier / rarity / points kept"): the higher level of each perk line, NOT trimmed to the
# points earned (GearLL.free shows 0 until the skill catches up; a Reset gives every one back); the higher reset count
M(glf, r"""
public static String harvPerksAll(java.util.Properties P) {
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
  long ra = @PKG@.GearLL.getl(P, "hoe.resets", 0L);
  long rb = @PKG@.GearLL.getl(P, "sickle.resets", 0L);
  if (ra > rb) P.setProperty("sickle.resets", String.valueOf(ra));
  return "";
}""")
''')
rep('''  java.util.Properties old = (java.util.Properties) P.clone();
  String trimmed = harvPerks(u, P);''', '''  java.util.Properties old = (java.util.Properties) P.clone();
  boolean au = "1".equals(P.getProperty("harv.auto"));          // 0.3.14: the automatic merge keeps the higher level of each perk (no trim)
  String trimmed = au ? harvPerksAll(P) : harvPerks(u, P);
  if (au) {          // 0.3.14: the run-once marker rides in the same write
    P.setProperty("harvAuto", "1");
    P.setProperty("harvAutoAt", String.valueOf(System.currentTimeMillis()));
    String hs = P.getProperty("harv.src");
    if (hs != null) P.setProperty("harvAutoHow", hs);
  }''')
before('''# a merge the server did not finish (sweep, before the look): the Harvester is there -> commit; the hoe is still there -> nothing happened (the''',
       r'''# 0.3.14 THE AUTOMATIC MERGE (harvester.only; tools/gear_0_3_14_patch.py 1b): the undo record (harvmerge/<pk>.log, one line per merge /
# undo, fsync'd), the verified History copy of the registry file (harvmerge/history/), the merged document (EVERY line of both tools), the merge
F(glf, "public static final long[] HA = new long[6];")          # 0 merged automatically, 1 refused / waiting, 2 failed + restored, 3 from a snapshot, 4 without a hoe, 5 History / record failures
M(glf, r"""
public static java.nio.file.Path harvRecFile(String pk) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pk == null || pk.length() == 0) return null;
  return d.resolve("harvmerge").resolve(@PKG@.GearLL.safeKey(pk) + ".log");
}""")
M(glf, r"""
public static boolean harvRec(String pk, String line) {
  java.nio.file.Path f = harvRecFile(pk);
  if (f == null) return false;
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(f.toFile(), true);
    try {
      out.write((line + "\n").getBytes("UTF-8"));
      out.flush();
      out.getFD().sync();
    } finally { out.close(); }
    return true;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("harvrec:" + pk, "the Harvester undo record harvmerge/" + pk + ".log could not be written (" + t + ") - that profile is not merged yet"); return false; }
}""")
# the verified History copy (null = not made: no merge); the registry is written first when it has no file yet
M(glf, r"""
public static String harvBak(String pk, java.util.Properties P, String stamp) {
  try {
    java.nio.file.Path f = @PKG@.GearLL.file(pk);
    if (f == null || @PKG@.GearCfg.DIR == null) return null;
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]) && !@PKG@.GearLL.save(pk, P)) return null;
    byte[] b = java.nio.file.Files.readAllBytes(f);
    java.nio.file.Path h = @PKG@.GearCfg.DIR.resolve("harvmerge").resolve("history");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    String nm = @PKG@.GearLL.safeKey(pk) + ".properties." + stamp + ".bak";
    java.nio.file.Path c = h.resolve(nm);
    java.nio.file.Files.write(c, b, new java.nio.file.OpenOption[0]);
    byte[] r = java.nio.file.Files.readAllBytes(c);
    if (!java.util.Arrays.equals(b, r)) { @PKG@.Gear.warn("Harvester merge: the History copy of lifelong/" + pk + ".properties did not verify - nothing merged for that profile"); return null; }
    return nm;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("harvbak:" + pk, "Harvester merge: the History copy of lifelong/" + pk + ".properties failed (" + t + ") - nothing merged for that profile yet"); return null; }
}""")
M(glf, r"""
public static String b64(@BD@ d) {
  if (d == null) return "-";
  try { return java.util.Base64.getEncoder().encodeToString(d.toJson().getBytes("UTF-8")); } catch (Throwable t) { return "-"; }
}""")
# critic fix 4: the Harvester's fingerprint (item id = tier, rarity, lines, reforge / Sigil counts, reforge name - not the level, which follows
# the skill) and its perk levels; the undo refuses a Harvester changed since the merge unless the admin says force
M(glf, r"""
public static String harvFp(String id, @BD@ d) {
  if (d == null) return String.valueOf(id) + "|?";
  Object ms = d.get("mods");
  return String.valueOf(id) + "|" + @PKG@.GearData.str(d, "r", "") + "|" + (ms == null ? "" : String.valueOf(ms)) + "|" + @PKG@.GearData.num(d, "rfN", 0) + "|" + @PKG@.GearData.num(d, "sgN", 0) + "|" + @PKG@.GearData.str(d, "rf", "");
}""")
M(glf, r"""
public static String harvPk(java.util.Properties P) {
  StringBuilder sb = new StringBuilder();
  for (int p = 0; p < @PKG@.GearLL.PK.length; p++) {
    if (!@PKG@.GearLL.perkFor(3, p)) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(@PKG@.GearLL.PK[p]).append('=').append(@PKG@.GearLL.perkOf(P, 3, p));
  }
  return sb.toString();
}""")
M(glf, r"""
public static String b64s(String t) {
  try { return java.util.Base64.getEncoder().encodeToString((t == null ? "" : t).getBytes("UTF-8")); } catch (Throwable x) { return "-"; }
}""")
# THE MERGED DOCUMENT of the automatic merge: the sickle's own (uid, owner, rebirth stamps ...), the better rarity (Mythic kept), EVERY line of both
# (the best value of each key, capped at the Harvester's cap at that rarity / level - no line-count trim), the higher reforge / Sigil counts,
# the better tool's reforge name, the Harvester's kind + the level rule. hd may be null (no hoe). info: [0] lines that cannot be on a Harvester,
# [1] lines lowered to the cap, [3] the level
M(glf, r"""
public static @BD@ harvDocAll(@BD@ hd, @BD@ sd, String hid, java.util.UUID u, int[] info) {
  if (sd == null) return null;
  int rs = @PKG@.GearData.rarity(sd);
  if (rs > @PKG@.GearDefs.R_MY) rs = 0;
  int rh = hd == null ? -1 : @PKG@.GearData.rarity(hd);
  if (rh > @PKG@.GearDefs.R_MY) rh = 0;
  int r = rh > rs ? rh : rs;
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
  int dropped = (hd == null ? 0 : harvLines(best, frac, hd, hid, r, L, info)) + harvLines(best, frac, sd, hid, r, L, info);
  @BA@ out = new @BA@();
  for (int i = 0; i < n; i++) if (best[i] > 0) out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], best[i]));
  d.put("mods", out);
  int rf = hd == null ? 0 : @PKG@.GearData.num(hd, "rfN", 0);
  int rf2 = @PKG@.GearData.num(sd, "rfN", 0);
  if (rf2 > rf) rf = rf2;
  if (rf > 0) d.put("rfN", new org.bson.BsonInt32(rf));
  String nm = hd != null && rh > rs ? @PKG@.GearData.str(hd, "rf", null) : @PKG@.GearData.str(sd, "rf", null);
  if (nm == null && hd != null) nm = rh > rs ? @PKG@.GearData.str(sd, "rf", null) : @PKG@.GearData.str(hd, "rf", null);
  if (nm != null) d.put("rf", new org.bson.BsonString(nm));
  int sg = hd == null ? 0 : @PKG@.GearData.num(hd, "sgN", 0);
  int sg2 = @PKG@.GearData.num(sd, "sgN", 0);
  if (sg2 > sg) sg = sg2;
  if (sg > 0) d.put("sgN", new org.bson.BsonInt32(sg));
  info[0] = dropped;
  info[3] = L;
  return d;
}""")
# THE MERGE (world thread; GearHarv.auto checked: not merged, no journal, migrated, the sickle on the player). The hoe: on the player, else its
# snapshot (the physical one is retired when it turns up), else none. "+" merged, "-" why not (nothing changed)
M(glf, r"""
public static String harvAuto(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  if (pr == null || inv == null || P == null) return "-No player.";
  java.util.UUID u = pr.getUuid();
  String siU = P.getProperty("sickle.uid");
  String hoeU = P.getProperty("hoe.uid");
  if (siU == null) return "-Your sickle is not set up yet.";
  int[] sa = find(inv, pk, siU);
  if (sa == null) return "-Carry your sickle (/sickle brings it) - it becomes your Harvester.";
  @IC@ sc = @PKG@.GearStamp.section(inv, sa[0]);
  @IS@ sic = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
  @BD@ sd = docOf(sic);
  if (sc == null || sic == null || sic.isEmpty() || sd == null) return "-Your sickle cannot be read right now.";
  int[] ha = null;
  if (hoeU != null) ha = find(inv, pk, hoeU);
  @IC@ hc = null;
  @IS@ hoe = null;
  @BD@ hd = null;
  if (ha != null) { hc = @PKG@.GearStamp.section(inv, ha[0]); hoe = @PKG@.GearStamp.at(inv, ha[0], ha[1]); }
  if (hoe != null) hd = docOf(hoe);
  if (hoe != null && (hc == null || hd == null)) return "-Your hoe cannot be read right now.";
  String hoeId = hoe != null ? hoe.getItemId() : null;
  String hsrc = hoeU == null ? "none" : (hd != null ? "inventory" : "snapshot");
  if (hd == null && hoeU != null) {
    hd = snapDoc(P, "hoe", hoeU);
    hoeId = P.getProperty("hoe.snapId");
    if (hoeId == null || @PKG@.Gear.item(hoeId) == null || @PKG@.GearLL.kOf(hoeId) != 2) hoeId = P.getProperty("hoe.id");
    if (hd != null && (hoeId == null || @PKG@.GearLL.kOf(hoeId) != 2)) hd = null;
    // critic fix 3: a hoe that is neither on you nor copyable from its snapshot is NEVER merged away (it could be the better one): wait
    if (hd == null) return "-Your lifelong hoe is not on you and has no copy to merge - carry it (/hoe brings it or makes a copy), then both become your Harvester.";
  }
  int ts = @PKG@.GearLL.tier(sic.getItemId());
  int th = hd == null ? -1 : @PKG@.GearLL.tier(hoeId);
  int t = th > ts ? th : ts;
  if (t < 0) t = 0;
  if (t > @PKG@.GearLL.HARV_TOP) t = @PKG@.GearLL.HARV_TOP;
  String hid = @PKG@.GearLL.HARV_PRE + @PKG@.GearLL.tname(t);
  if (@PKG@.Gear.item(hid) == null) return "-The Harvester is not loaded on this server.";
  int[] info = new int[4];
  @BD@ nd = null;
  @IS@ ns = null;
  try {
    nd = harvDocAll(hd, sd, hid, u, info);
    if (nd != null) ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(hid, 1), sic), nd, u);
  } catch (Throwable t0) { nd = null; ns = null; @PKG@.Gear.warn("Harvester merge: the document could not be made for " + pr.getUsername() + ": " + t0); }
  if (nd == null || ns == null || ns.isEmpty() || !hid.equals(ns.getItemId())) return "-The Harvester could not be made - nothing changed.";
  String who = pr.getUsername();
  java.util.Properties Pc = (java.util.Properties) P.clone();          // critic fix 4: what the Harvester is right after the merge (the undo compares)
  harvPerksAll(Pc);
  String mfp = harvFp(hid, nd);
  String mpk = harvPk(Pc);
  // the History copy + the undo record BEFORE anything moves
  String stamp = String.valueOf(System.currentTimeMillis());
  String bak = harvBak(pk, P, stamp);
  if (bak == null) { HA[5] = HA[5] + 1L; return "-Your tools could not be backed up first - nothing changed (an admin can check the server log)."; }
  @BD@ hmd = null;
  if (hoe != null) hmd = hoe.getMetadata();
  else if (hd != null) { try { hmd = @PKG@.GearData.put(new @IS@(hoeId, 1), hd, u).getMetadata(); } catch (Throwable th0) { hmd = null; } }
  String line = "MERGE\t" + stamp + "\t" + siU + "\t" + hid + "\t" + (hoeU == null ? "-" : hoeU) + "\t" + (hd == null || hoeId == null ? "-" : hoeId) + "\t" + b64(hmd)
    + "\t" + hsrc + "\t" + sic.getItemId() + "\t" + b64(sic.getMetadata()) + "\t" + bak + "\t" + (hoe == null ? "-" : String.valueOf(hoe.getDurability())) + "\t" + String.valueOf(sic.getDurability()) + "\t" + b64s(mfp) + "\t" + mpk;
  if (!harvRec(pk, line)) { HA[5] = HA[5] + 1L; return "-The undo record could not be written - nothing changed."; }
  @PKG@.GearLog.line("LL-HARV-AUTO-BEGIN " + who + " " + u + " " + pk + " hoe " + (hoe != null ? hoe.getItemId() + " @" + @PKG@.GearForge.where(ha[0], ha[1]) + " " + @PKG@.GearMerge.json(hoe) : hsrc) + " + sickle " + sic.getItemId() + " @" + @PKG@.GearForge.where(sa[0], sa[1]) + " " + @PKG@.GearMerge.json(sic) + " -> " + hid + " " + nd.toJson() + " (History " + bak + ")");
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }
  String dj = null;
  try { dj = java.util.Base64.getEncoder().encodeToString(nd.toJson().getBytes("UTF-8")); } catch (Throwable tj) { dj = null; }
  P.setProperty("harv.pend", siU);
  if (hoeU != null) P.setProperty("harv.hoeU", hoeU);
  P.setProperty("harv.id", hid);
  if (dj != null) P.setProperty("harv.doc", dj);
  P.setProperty("harv.at", String.valueOf(System.currentTimeMillis()));
  P.setProperty("harv.auto", "1");
  P.setProperty("harv.src", hsrc);
  if (!@PKG@.GearLL.save(pk, P)) { harvDrop(P); return "-Your merge could not be saved - nothing changed."; }
  crash(41);
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int bh = hoe == null ? 0 : @PKG@.GearStamp.countId(all, hoe.getItemId());
  int bs = @PKG@.GearStamp.countId(all, sic.getItemId());
  int bv = @PKG@.GearStamp.countId(all, hid);
  // (a) a hoe on the player leaves first: a crash after it finishes the merge from the journal (harvRecover), never copies anything
  if (hoe != null) {
    Object t1 = null;
    Throwable e1 = null;
    try { t1 = hc.removeItemStackFromSlot((short) ha[1]); } catch (Throwable x1) { e1 = x1; }
    boolean gone = e1 == null && !(t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) && @PKG@.GearMerge.empty(hc, ha[1]);
    if (!gone) {
      if (@PKG@.GearMerge.empty(hc, ha[1])) { try { hc.setItemStackForSlot((short) ha[1], hoe); } catch (Throwable xb) { } }
      harvDrop(P);
      @PKG@.GearLL.save(pk, P);
      HA[2] = HA[2] + 1L;
      @PKG@.GearLog.line("LL-HARV-AUTO-FAILED " + who + " " + u + " (the hoe was not taken: " + (e1 != null ? String.valueOf(e1) : "the inventory refused it") + ") - nothing used");
      return "-The inventory refused the change - nothing was used.";
    }
    @PKG@.GearStamp.selfNote(u, t1);
  }
  crash(42);
  // (b) the sickle's slot gets the Harvester (the same lifelong uid)
  Object t2 = null;
  Throwable e2 = null;
  try { t2 = sc.setItemStackForSlot((short) sa[1], ns); } catch (Throwable x2) { e2 = x2; }
  @IS@ now = sc.getItemStack((short) sa[1]);
  @BD@ bd = docOf(now);
  boolean put = e2 == null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && now != null && hid.equals(now.getItemId()) && bd != null && siU.equals(@PKG@.GearLL.uid(bd));
  if (!put) {
    boolean back = true;
    if (hoe != null) {
      try { hc.setItemStackForSlot((short) ha[1], hoe); } catch (Throwable xr) { }
      back = @PKG@.GearForge.same(hc.getItemStack((short) ha[1]), hoe.getItemId(), @PKG@.GearForge.fp(hoe));
    }
    if (back) {
      harvDrop(P);
      @PKG@.GearLL.save(pk, P);
      HA[2] = HA[2] + 1L;
      @PKG@.GearLog.line("LL-HARV-AUTO-FAILED " + who + " " + u + " (the Harvester was not written: " + (e2 != null ? String.valueOf(e2) : "the inventory refused it") + ") - RESTORED, nothing used");
      return "-The inventory refused the Harvester - nothing was used.";
    }
    @PKG@.Gear.warn("HARVESTER: the hoe of " + who + " (" + u + ") could not be put back - the merge is finished at the next look (the journal stays); both documents are in gear.log");
    @PKG@.GearLog.line("LL-HARV-AUTO-RESTORE-FAILED " + who + " " + u + " " + @PKG@.GearMerge.json(hoe) + " (the journal stays - harvRecover finishes the Harvester)");
    return "-Something went wrong - your Harvester is finished at your next look (an admin can find both tools in the server log).";
  }
  @PKG@.GearStamp.selfNote(u, t2);
  crash(43);
  // (c) ONE registry write: the perks (no trim), the hoe kind forgotten, harv=1, harvAuto=1
  if (!harvFinal(pr, pk, P, "auto")) @PKG@.Gear.warn("lifelong: the Harvester of " + pk + " could not be written to the registry - the next look finishes it");
  try {
    int ah = hoe == null ? 0 : @PKG@.GearStamp.countId(all, hoe.getItemId());
    int as = @PKG@.GearStamp.countId(all, sic.getItemId());
    int av = @PKG@.GearStamp.countId(all, hid);
    if ((hoe != null && ah != bh - 1) || (!sic.getItemId().equals(hid) && as != bs - 1) || (!sic.getItemId().equals(hid) && av != bv + 1)) @PKG@.Gear.warn("HARVESTER AUTO COUNT MISMATCH for " + who + ": hoe " + bh + "->" + ah + ", " + sic.getItemId() + " " + bs + "->" + as + ", " + hid + " " + bv + "->" + av);
    if (hoe != null) @PKG@.GearMerge.rqGone(hoe, u, who);
    @PKG@.GSnd.upgrade(u);
  } catch (Throwable xa) { }
  HA[0] = HA[0] + 1L;
  if ("snapshot".equals(hsrc)) HA[3] = HA[3] + 1L;
  if (hd == null) HA[4] = HA[4] + 1L;
  return "+Hoes and sickles are retired: " + (hd != null ? "your hoe and sickle are one " : "your sickle is now ") + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(nd)] + " " + @PKG@.Gear.itemName(hid) + " (Lv " + @PKG@.GearLevel.level(hid, nd) + ")" + (hd != null ? " - every line and the higher Upgrade Points of both" : "") + (info[0] > 0 ? " (" + info[0] + " line" + (info[0] == 1 ? "" : "s") + " no Harvester can carry)" : "") + ". Right-click tills, a swing reaps. Lost it? /harvester";
}""")
''')

# ================================================================================================================ /gear harvmerge (admin): the class + its constructor early, the body late
after('''gnc = mk("GearNormCmd", APC)          # 0.3.13: /gear normoff [status | undo <player>] (admin; body in the 0.3.13 block)
''', '''ghcmd = mk("GearHarvCmd", APC)          # 0.3.14: /gear harvmerge [status | undo <player>] (admin; body in the 0.3.14 block)
''')
before('''C(subc["loot"], r"""
public GearLootCmd() {''', r'''C(ghcmd, r"""
public GearHarvCmd() {
  super("harvmerge", "The Harvester merge: the counters, or turn a player's merged Harvester back into the hoe + sickle: /gear harvmerge [undo <player> [force]]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
''')
rep('''  addSubCommand(new @PKG@.GearNormCmd());          // 0.3.13
}""")''', '''  addSubCommand(new @PKG@.GearNormCmd());          // 0.3.13
  addSubCommand(new @PKG@.GearHarvCmd());          // 0.3.14
}""")''')

# ================================================================================================================ the 0.3.14 block (late: everything it calls exists)
G314 = r'''# ####################################################################################################################################
# 0.3.14 (tools/gear_0_3_14_patch.py): GearHarv (the one-time merge driver, /hoe /sickle /harvester, the undo, the swing tier rule), GearHarvCrop
# (the interaction type SkyyGearHarvest) + GearHarvSup, GearSigDrop (Sigil drops: mob kills, the bag lists) + GearSigBag (the drop-list
# wrapper), the /gear harvmerge body. Hooks: GearLife.sweep0 (after), GearLife.reclaimW / harvest / harvPreview (before), HarvCmd.execute (before),
# GearDeathMark.tick (after), GearNorm.ensure0 (after), setup / start / shutdown, GearBye.
# ####################################################################################################################################
G314 = {"C3HC": "com.hypixel.hytale.builtin.adventure.farming.interactions.HarvestCropInteraction"}
for _k in G314:
    assert _k not in T, "0.3.14 token clashes: " + _k
T.update(G314)
for _c, _m in ((G314["C3HC"], "interactWithBlock"), (G314["C3HC"], "CODEC"), (PB["NPCE"], "getRoleName"), (G312["C2BCOD"], "builder")):
    B.probe(pool, _c, _m)
# the engine shapes this round depends on (VERIFIED bytecode 2026-10-16, Hytale 0.7.2): HarvestCropInteraction = a SimpleBlockInteraction whose
# interactWithBlock only calls FarmingUtil.harvest (Failed when it harvests nothing); its CODEC is a BuilderCodec; one no-arg constructor
_hc = pool.get(G314["C3HC"])
_hiw = [m for m in _hc.getDeclaredMethods() if str(m.getName()) == "interactWithBlock"]
assert len(_hiw) == 1 and str(_hiw[0].getSignature()) == "(Lcom/hypixel/hytale/server/core/universe/world/World;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/protocol/InteractionType;Lcom/hypixel/hytale/server/core/entity/InteractionContext;Lcom/hypixel/hytale/server/core/inventory/ItemStack;Lorg/joml/Vector3i;Lcom/hypixel/hytale/server/core/modules/interaction/interaction/CooldownHandler;)V", "HarvestCropInteraction.interactWithBlock changed"
assert [str(c.getSignature()) for c in _hc.getDeclaredConstructors()] == ["()V"], "HarvestCropInteraction() changed"
assert str(_hc.getField("CODEC").getType().getName()) == G312["C2BCOD"], "HarvestCropInteraction.CODEC is no BuilderCodec"
_hcw = _calls(G314["C3HC"], "interactWithBlock")
assert "FarmingUtil.harvest" in _hcw and "InteractionSyncData.state" in _hcw, "vanilla HarvestCrop.interactWithBlock changed: %s" % _hcw
assert "HarvestCrop" in _calls("com.hypixel.hytale.builtin.adventure.farming.FarmingPlugin", "setup"), "FarmingPlugin no longer registers HarvestCrop in setup()"
gharv = mk("GearHarv")
ghcrop = mk("GearHarvCrop", G314["C3HC"])
ghsup = mk("GearHarvSup")
gsigd = mk("GearSigDrop")
gsbag = mk("GearSigBag", G311["IDC"])
G314_CLASSES = [gharv, ghcrop, ghsup, gsigd, gsbag, ghcmd]
# ---- GearHarv: fields first
for _f in ("public static final long[] N = new long[10];",          # 0 merged, 1 kit markers, 2 fetches, 3 waits (sickle / hoe away), 4 refusals, 5 undone, 6 /hoe /sickle answers, 7 undo waits, 8 undos refused (changed)
           "public static final long[] SW = new long[4];",          # swing: 0 crops seen, 1 one-up broken (one per swing), 2 two-up skipped, 3 one-up skipped (the rest of the arc)
           "public static final java.util.concurrent.ConcurrentHashMap LASTRUN = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> Long (next look not before)
           "public static final java.util.concurrent.ConcurrentHashMap FETCH = new java.util.concurrent.ConcurrentHashMap();",     # "uuid:kind" -> Long (the last auto fetch)
           "public static final java.util.concurrent.ConcurrentHashMap UNDO = new java.util.concurrent.ConcurrentHashMap();",      # UUID -> admin name
           "public static final java.util.concurrent.ConcurrentHashMap ONEUP = new java.util.concurrent.ConcurrentHashMap();",     # UUID -> Long (the one-up crop a swing broke)
           "public static final ThreadLocal IN = new ThreadLocal();",          # the command wrapper is running (its own reclaimW calls pass through)
           "public static volatile long SWING_MS = 450L;",
           "public static volatile int CRASH_AT = 0;"):          # CRASH_AT: HARNESS SEAM ONLY (44 = after the undo's registry write, 45 = after the sickle is back)
    F(gharv, _f)
M(gharv, "public static boolean on() { return @PKG@.GearCfg.LL_ON && @PKG@.GearCfg.HARV_ON && @PKG@.GearCfg.HARV_ONLY; }")
M(gharv, r"""
public static void crash(int n) {
  if (CRASH_AT == n) throw new IllegalStateException("harness: a crash at Harvester undo step " + n);
}""")
# the swing (GearHarvCrop, world thread): 0 = vanilla's harvest (a crop of the tool's tier or lower, or no crop / no tier), 1 = the ordinary hit
# (the Failed path: one one-tier-up crop per swing - half XP, no Fortune), 2 = nothing (two up, or another one-up crop in the same swing)
M(gharv, r"""
public static int swing(@WLD@ w, @CB@ cb, @ICTX@ ctx, @IS@ item, @VECI@ pos) {
  if (!@PKG@.GearCfg.FARM_T1 || !@PKG@.GearCfg.GATE_ON || pos == null) return 0;
  String bid = @PKG@.GearSickle.blockId(w, pos.x(), pos.y(), pos.z());
  int[] cm = @PKG@.GearLL.catOf(bid);
  if (cm[0] != 4 || cm[1] < 1) return 0;
  @IS@ h = @PKG@.GearCan.held(ctx, item);
  String id = h == null || h.isEmpty() ? null : h.getItemId();
  int[] d = @PKG@.GearLL.decideI(id, 4, cm[1]);
  SW[0] = SW[0] + 1L;
  if (d[0] <= 0) return 0;
  @PR@ pr = @PKG@.GearCan.prOf(cb, ctx);
  java.util.UUID u = pr == null ? null : pr.getUuid();
  String tn = id == null ? "bare hands" : @PKG@.Gear.itemName(id);
  if (d[0] == 2) {
    SW[2] = SW[2] + 1L;
    if (pr != null) @PKG@.GearLL.cropNo(pr, u, id, tn, d);
    return 2;
  }
  long now = System.currentTimeMillis();
  Object l = u == null ? null : ONEUP.get(u);
  if (u != null && !(l instanceof Long && now >= ((Long) l).longValue() && now - ((Long) l).longValue() < SWING_MS)) {
    ONEUP.put(u, Long.valueOf(now));
    SW[1] = SW[1] + 1L;
    if (pr != null) @PKG@.GearLife.tellOnce(pr, "harvoneup", "That crop is one tier above your " + tn + ": a swing breaks one at a time (half Farming XP) - the sweep reaps crops of its tier and lower. Tier it up on the Anvil (/smithing).", 60000L);
    return 1;
  }
  SW[3] = SW[3] + 1L;
  return 2;
}""")
M(gharv, r"""
public static String harvText(String r) {
  if (r == null) return "";
  return r.replace("lifelong sickle", "Harvester").replace("Your sickle", "Your Harvester").replace("your sickle", "your Harvester").replace("/sickle", "/harvester").replace(" sickle", " Harvester");
}""")
M(gharv, "public static String mark(String r) { return r != null && r.length() > 0 && (r.charAt(0) == '+' || r.charAt(0) == '-' || r.charAt(0) == '=') ? r.substring(0, 1) : \"=\"; }")
M(gharv, "public static String body(String r) { return r != null && r.length() > 0 && (r.charAt(0) == '+' || r.charAt(0) == '-' || r.charAt(0) == '=') ? r.substring(1) : (r == null ? \"\" : r); }")
M(gharv, r"""
public static boolean due(java.util.UUID u, String k) {
  long now = System.currentTimeMillis();
  String key = u + ":" + k;
  Object l = FETCH.get(key);
  if (l instanceof Long && now >= ((Long) l).longValue() && now - ((Long) l).longValue() < 60000L) return false;
  if (FETCH.size() > 4096) FETCH.clear();
  FETCH.put(key, Long.valueOf(now));
  return true;
}""")
# a hoe / sickle that is away: out of Requip (wardrobe:fn:fetch) or a CLOSED Vault (vault:fn:takeLL) - the /hoe /sickle paths (never an exact copy
# here); null = nowhere we can reach, "+" fetched, "-" not now
M(gharv, r"""
public static String fetchFor(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String cur) {
  if (@PKG@.GearStamp.firstEmpty(new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() }, null, -1) == null) return "-No room";
  String eid = @PKG@.GearLife.rqFind(pr.getUuid(), cur);
  String r = eid != null ? @PKG@.GearLife.fromRequip(pr, inv, pk, P, k, cur, eid) : @PKG@.GearLife.fromVault(pr, inv, pk, P, k, cur);
  if (r != null) {
    N[2] = N[2] + 1L;
    @PKG@.GearLog.line("LL-HARV-FETCH " + pr.getUuid() + " " + pk + " " + @PKG@.GearLL.KIND[k] + " " + cur + " -> " + r);
  }
  return r;
}""")
# critic fix 3: is the hoe stored somewhere we know of? (Requip, a CLOSED Vault - vault:fn:findLL answers, or an error = assume yes - or a chest /
# window it was put in: hoe.locK)
M(gharv, r"""
public static boolean away(java.util.UUID u, String pk, java.util.Properties P, String cur) {
  if (cur == null) return false;
  if (@PKG@.GearLife.rqFind(u, cur) != null) return true;
  if (P.getProperty("hoe.locK") != null) return true;
  java.util.function.Function ff = @PKG@.Gear.fn("vault:fn:findLL");
  if (ff == null) return false;
  try { return ff.apply(new Object[] { u, pk, cur }) instanceof String; } catch (Throwable t) { return true; }
}""")
# THE DRIVER (from GearHarv.sweepHook; world thread): the kit marker, the fetches, the merge. null = nothing to do
M(gharv, r"""
public static String auto(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  if (@PKG@.GearLL.merged(P) || "undone".equals(P.getProperty("harvAuto")) || P.getProperty("harv.pend") != null) return null;
  if (!"1".equals(P.getProperty("migrated"))) return null;
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) if (P.getProperty(@PKG@.GearLL.KIND[k] + ".pend") != null) return null;
  java.util.UUID u = pr.getUuid();
  if (@PKG@.GearLL.rbWait(u)) return null;
  String siU = P.getProperty("sickle.uid");
  if (siU == null) return null;
  String hoeU = P.getProperty("hoe.uid");
  String sid = P.getProperty("sickle.id");
  if (hoeU == null && sid != null && @PKG@.GearLL.harv(sid)) {          // a profile born with the Crude Harvester: only the marker
    java.util.Properties old = (java.util.Properties) P.clone();
    P.setProperty("harv", "1");
    P.setProperty("harvAt", String.valueOf(System.currentTimeMillis()));
    P.setProperty("harvAuto", "kit");
    if (!@PKG@.GearLL.save(pk, P)) { P.clear(); P.putAll(old); return null; }
    N[1] = N[1] + 1L;
    @PKG@.GearLog.line("LL-HARV-KIT " + u + " " + pk + " " + siU + " " + sid);
    return "=kit";
  }
  int[] sa = @PKG@.GearLife.find(inv, pk, siU);
  if (sa == null) {
    if (due(u, "s")) fetchFor(pr, inv, pk, P, 3, siU);
    sa = @PKG@.GearLife.find(inv, pk, siU);
    if (sa == null) {
      N[3] = N[3] + 1L;
      @PKG@.GearLife.tellOnce(pr, "harvwait", "Hoes and sickles are retired: your lifelong sickle becomes your Harvester (it keeps your hoe's best too). Carry it - /sickle brings it back.", 600000L);
      return "-wait";
    }
  }
  if (hoeU != null && @PKG@.GearLife.find(inv, pk, hoeU) == null) {
    if (due(u, "h")) fetchFor(pr, inv, pk, P, 2, hoeU);
    if (@PKG@.GearLife.find(inv, pk, hoeU) == null) {
      // critic fix 3: the hoe still exists somewhere (Requip, the Vault, a chest / window it was put in) -> wait for it, never merge its snapshot
      if (away(u, pk, P, hoeU)) {
        N[3] = N[3] + 1L;
        @PKG@.GearLife.tellOnce(pr, "harvwaith", "Hoes and sickles are retired: your lifelong hoe is stored away (Requip, the Vault or a chest) - /hoe brings it, then your hoe and sickle become one Harvester.", 600000L);
        return "-wait";
      }
      if (@PKG@.GearLife.snapDoc(P, "hoe", hoeU) == null) {
        N[3] = N[3] + 1L;
        @PKG@.GearLife.tellOnce(pr, "harvwaith", "Hoes and sickles are retired: your lifelong hoe is lost - type /hoe for it, then your hoe and sickle become one Harvester.", 600000L);
        return "-wait";
      }
    }
  }
  String r = @PKG@.GearLife.harvAuto(pr, inv, pk, P);
  if (r.startsWith("+")) {
    N[0] = N[0] + 1L;
    @PKG@.GearLife.tellOnce(pr, "harvauto", r.substring(1), 5000L);
  } else {
    N[4] = N[4] + 1L;
    @PKG@.GearLife.tellOnce(pr, "harvautono", "Your hoe and sickle could not become your Harvester yet: " + r.substring(1), 300000L);
  }
  return r;
}""")
# ---- THE UNDO (an admin queued it: /gear harvmerge undo <player>; or a journal harvUndo.pend left by a crash). The record's newest MERGE row with
# no UNDONE row: fields 0 MERGE 1 stamp 2 sickle uid 3 Harvester id 4 hoe uid 5 hoe id 6 hoe metadata 7 hoe source 8 sickle id 9 sickle metadata
# 10 History file 11 hoe durability 12 sickle durability
M(gharv, r"""
public static String[] lastMerge(String pk) {
  java.nio.file.Path f = @PKG@.GearLife.harvRecFile(pk);
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
  try {
    java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    java.util.HashSet gone = new java.util.HashSet();
    for (int i = 0; i < ls.size(); i++) {
      String[] p = ((String) ls.get(i)).split("\t", -1);
      if (p.length >= 2 && "UNDONE".equals(p[0])) gone.add(p[1]);
    }
    for (int i = ls.size() - 1; i >= 0; i--) {
      String[] p = ((String) ls.get(i)).split("\t", -1);
      if (p.length >= 13 && "MERGE".equals(p[0]) && !gone.contains(p[1])) return p;
    }
  } catch (Throwable t) { @PKG@.Gear.warn("Harvester undo: the record of " + pk + " could not be read: " + t); }
  return null;
}""")
M(gharv, "public static int pending(String pk) { return lastMerge(pk) == null ? 0 : 1; }")
M(gharv, r"""
public static String unb64(String t) {
  try { return t == null || "-".equals(t) ? null : new String(java.util.Base64.getDecoder().decode(t), "UTF-8"); } catch (Throwable x) { return null; }
}""")
# critic fix 4: what changed on the Harvester since the merge (null = nothing / cannot tell): id + document (fp) and the perks (pk) against the record
M(gharv, r"""
public static String diff(String[] rec, String fp, String pk) {
  if (rec == null || rec.length < 15) return null;
  String mf = unb64(rec[13]);
  StringBuilder sb = new StringBuilder();
  if (mf != null && fp != null && !mf.equals(fp)) {
    int a = mf.indexOf('|');
    int b = fp.indexOf('|');
    String ia = a < 0 ? mf : mf.substring(0, a);
    String ib = b < 0 ? fp : fp.substring(0, b);
    if (!ia.equals(ib)) sb.append("tiered up (").append(ia).append(" -> ").append(ib).append(")");
    else sb.append("rerolled / reforged / a Sigil since the merge");
  }
  if (pk != null && !pk.equals(rec[14])) { if (sb.length() > 0) sb.append(", "); sb.append("Upgrade Points changed (").append(rec[14]).append(" -> ").append(pk).append(")"); }
  return sb.length() == 0 ? null : sb.toString();
}""")
# the admin command's check (any thread: the registry's snapshot of the Harvester + its perks, no inventory read)
M(gharv, r"""
public static String undoWhy(String pk) {
  String[] rec = lastMerge(pk);
  if (rec == null) return null;
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "the player's lifelong tool list cannot be read right now";
  @BD@ d = @PKG@.GearLife.snapDoc(P, "sickle", rec[2]);
  String id = P.getProperty("sickle.snapId");
  if (id == null) id = P.getProperty("sickle.id");
  return diff(rec, d == null ? null : @PKG@.GearLife.harvFp(id, d), @PKG@.GearLife.harvPk(P));
}""")
M(gharv, r"""
public static @IS@ rebuild(String id, String mdB64, String dur, String newU, String oldU, java.util.UUID u) {
  try {
    if (id == null || "-".equals(id) || @PKG@.Gear.item(id) == null) return null;
    @BD@ md = null;
    if (mdB64 != null && !"-".equals(mdB64)) md = @BD@.parse(new String(java.util.Base64.getDecoder().decode(mdB64), "UTF-8"));
    if (md != null) md.remove(@PKG@.GearData.stampKey());
    @IS@ s = md == null || md.isEmpty() ? new @IS@(id, 1) : new @IS@(id, 1, md);
    if (dur != null && !"-".equals(dur)) {
      double dv = Double.parseDouble(dur);
      if (dv > 0.0) s = s.withDurability(dv);
    }
    if (newU != null) {
      @BD@ d = @PKG@.GearLife.docOf(s);
      if (d == null) return null;
      @BD@ nd = d.clone();
      nd.put("lu", new org.bson.BsonString(newU));
      if (oldU != null) nd.put("lcu", new org.bson.BsonString(oldU));
      nd.remove("lrt");
      s = @PKG@.GearData.put(s, nd, u);
    }
    return s;
  } catch (Throwable t) { return null; }
}""")
M(gharv, r"""
public static void undo(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  String[] rec = lastMerge(pk);
  if (rec == null) {
    UNDO.remove(u);
    if (P.getProperty("harvUndo.pend") != null) { P.remove("harvUndo.pend"); P.remove("harvUndo.hoeNew"); @PKG@.GearLL.save(pk, P); }
    @PKG@.GearLog.line("LL-HARV-UNDO-NONE " + u + " " + pk + " (no merge record to undo)");
    return;
  }
  String stamp = rec[1];
  String siU = rec[2];
  String hoeU = rec[4];
  String hoeId = rec[5];
  String hsrc = rec[7];
  boolean giveHoe = !"-".equals(hoeU) && !"-".equals(hoeId);
  boolean pend = stamp.equals(P.getProperty("harvUndo.pend"));
  String hu = !giveHoe ? null : ("inventory".equals(hsrc) ? hoeU : P.getProperty("harvUndo.hoeNew"));
  if (!pend) {
    int[] ha = @PKG@.GearLife.find(inv, pk, siU);
    @IS@ hx = ha == null ? null : @PKG@.GearStamp.at(inv, ha[0], ha[1]);
    if (hx == null || !@PKG@.GearLL.harv(hx.getItemId())) {
      N[7] = N[7] + 1L;
      @PKG@.GearLife.tellOnce(pr, "harvundo", "An admin is turning your Harvester back into your hoe and sickle - carry it (/harvester brings it).", 60000L);
      return;
    }
    Object qv = UNDO.get(u);
    if (!(qv instanceof String && ((String) qv).endsWith("|force"))) {          // critic fix 4: the Harvester changed since the merge -> refused (an admin may force)
      String dw = diff(rec, @PKG@.GearLife.harvFp(hx.getItemId(), @PKG@.GearLife.docOf(hx)), @PKG@.GearLife.harvPk(P));
      if (dw != null) {
        UNDO.remove(u);
        N[8] = N[8] + 1L;
        @PKG@.Gear.warn("Harvester undo for " + pr.getUsername() + " (" + pk + ") REFUSED: the Harvester changed since the merge (" + dw + ") - /gear harvmerge undo " + pr.getUsername() + " force undoes it anyway (those changes are lost)");
        @PKG@.GearLog.line("LL-HARV-UNDO-REFUSED " + pr.getUsername() + " " + u + " " + pk + " merge " + stamp + ": " + dw);
        return;
      }
    }
    if (giveHoe && @PKG@.GearStamp.firstEmpty(new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() }, null, -1) == null) {
      N[7] = N[7] + 1L;
      @PKG@.GearLife.tellOnce(pr, "harvundoroom", "An admin is giving your hoe back - free one inventory slot.", 60000L);
      return;
    }
    java.nio.file.Path bf = @PKG@.GearCfg.DIR == null ? null : @PKG@.GearCfg.DIR.resolve("harvmerge").resolve("history").resolve(rec[10]);
    java.util.Properties B = null;
    try { if (bf != null && java.nio.file.Files.exists(bf, new java.nio.file.LinkOption[0])) B = @PKG@.GearCfg.read(bf); } catch (Throwable tb) { B = null; }
    if (B == null) { UNDO.remove(u); @PKG@.Gear.warn("Harvester undo for " + pk + ": the History copy " + rec[10] + " cannot be read - nothing changed"); return; }
    if (giveHoe && !"inventory".equals(hsrc)) hu = @PKG@.GearLL.newUid();
    java.util.Properties old = (java.util.Properties) P.clone();
    java.util.ArrayList ks = new java.util.ArrayList(P.keySet());
    for (int i = 0; i < ks.size(); i++) {
      String k = String.valueOf(ks.get(i));
      if (k.startsWith("hoe.") || k.startsWith("sickle.") || k.equals("harv") || k.equals("harvAt") || k.equals("harvHoe")) P.remove(k);
    }
    java.util.ArrayList bk = new java.util.ArrayList(B.keySet());
    for (int i = 0; i < bk.size(); i++) {
      String k = String.valueOf(bk.get(i));
      if ((k.startsWith("hoe.") && giveHoe) || k.startsWith("sickle.")) P.setProperty(k, B.getProperty(k));
    }
    if (giveHoe && !hu.equals(hoeU)) {          // a hoe merged from its snapshot comes back under a new uid in the old one's exact-copy family
      P.setProperty("hoe.uid", hu);
      P.setProperty("hoe.rp", "0");
      P.remove("hoe.seen");
      @PKG@.GearLife.nswAdd(P, "hoe", hoeU);
    }
    P.setProperty("harvAuto", "undone");
    P.setProperty("harvAutoUndoAt", String.valueOf(System.currentTimeMillis()));
    P.setProperty("harvUndo.pend", stamp);
    if (hu != null) P.setProperty("harvUndo.hoeNew", hu);
    if (!@PKG@.GearLL.save(pk, P)) { P.clear(); P.putAll(old); return; }
    @PKG@.GearLog.line("LL-HARV-UNDO-BEGIN " + pr.getUsername() + " " + u + " " + pk + " merge " + stamp + " (registry from " + rec[10] + ")");
  }
  crash(44);
  // (a) the Harvester's slot -> the sickle (the record's stack, same uid)
  int[] ha2 = @PKG@.GearLife.find(inv, pk, siU);
  if (ha2 != null) {
    @IS@ x = @PKG@.GearStamp.at(inv, ha2[0], ha2[1]);
    if (x != null && @PKG@.GearLL.harv(x.getItemId()) && !@PKG@.GearLL.harv(rec[8])) {
      @IS@ sk = rebuild(rec[8], rec[9], rec[12], null, null, u);
      @IC@ c = @PKG@.GearStamp.section(inv, ha2[0]);
      if (sk == null || c == null) { @PKG@.Gear.warnOnce("harvundo:" + pk, "Harvester undo for " + pk + ": the sickle cannot be made from the record - asked again later"); return; }
      Object tx = null;
      try { tx = c.setItemStackForSlot((short) ha2[1], sk); } catch (Throwable t1) { tx = null; }
      @IS@ now = c.getItemStack((short) ha2[1]);
      if (now == null || !rec[8].equals(now.getItemId())) { @PKG@.Gear.warnOnce("harvundo2:" + pk, "Harvester undo for " + pk + ": the inventory refused the sickle - asked again later"); return; }
      @PKG@.GearStamp.selfNote(u, tx);
    }
  }
  crash(45);
  // (b) the hoe (only when no stack with its uid is here)
  if (giveHoe && hu != null && @PKG@.GearLife.find(inv, pk, hu) == null) {
    @IS@ hs = rebuild(hoeId, rec[6], rec[11], hu.equals(hoeU) ? null : hu, hu.equals(hoeU) ? null : hoeU, u);
    if (hs == null) { @PKG@.Gear.warnOnce("harvundo3:" + pk, "Harvester undo for " + pk + ": the hoe cannot be made from the record"); }
    else if (!@PKG@.GearAdmin.give(inv, hs)) { @PKG@.GearLife.tellOnce(pr, "harvundoroom", "An admin is giving your hoe back - free one inventory slot.", 60000L); return; }
  }
  P.remove("harvUndo.pend");
  P.remove("harvUndo.hoeNew");
  if (!@PKG@.GearLL.save(pk, P)) return;
  @PKG@.GearLife.harvRec(pk, "UNDONE\t" + stamp + "\t" + System.currentTimeMillis());
  Object who = UNDO.remove(u);
  N[5] = N[5] + 1L;
  @PKG@.GearLog.line("LL-HARV-UNDO " + pr.getUsername() + " " + u + " " + pk + " merge " + stamp + " undone (asked by " + who + "): " + rec[8] + " + " + (giveHoe ? hoeId + " " + hu : "no hoe") + "; never merged automatically again");
  @PKG@.GearLife.tellOnce(pr, "harvundone", "An admin turned your Harvester back into your hoe and sickle.", 5000L);
}""")
# THE HOOK (GearLife.sweep0, after - every return): cheap when done
M(gharv, r"""
public static void sweepHook(@PR@ pr, @INV@ inv) {
  if (pr == null || inv == null || !@PKG@.GearCfg.LL_ON) return;
  java.util.UUID u = pr.getUuid();
  if (u == null || @PKG@.Gear.busy(u)) return;
  boolean und = UNDO.containsKey(u);
  String pk = @PKG@.Gear.pkey(u);
  if (@PKG@.GearLL.failing(pk)) return;
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return;
  boolean upend = P.getProperty("harvUndo.pend") != null;
  if (!und && !upend && (!on() || @PKG@.GearLL.merged(P) || "undone".equals(P.getProperty("harvAuto")))) return;
  long now = System.currentTimeMillis();
  Object l = LASTRUN.get(u);
  if (l instanceof Long && now < ((Long) l).longValue() && ((Long) l).longValue() - now <= 2000L) return;
  LASTRUN.put(u, Long.valueOf(now + 2000L));
  if (und || upend) { undo(pr, inv, pk, P); return; }
  auto(pr, inv, pk, P);
}""")
# /hoe /sickle (GearLife.reclaimW, before) and /harvester (HarvCmd, before): null = the old command runs. pre0 null = by kind
M(gharv, r"""
public static String cmd(@PR@ pr, @PLA@ p, int k, @WLD@ w, String pre0) {
  if ((k != 2 && k != 3) || !on() || pr == null || p == null || IN.get() != null) return null;
  java.util.UUID u = pr.getUuid();
  if (@PKG@.Gear.busy(u)) return null;
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P) || "undone".equals(P.getProperty("harvAuto")) || P.getProperty("harvUndo.pend") != null) return null;
  String pre = pre0 != null ? pre0 : (k == 2 ? "Hoes are retired - your Harvester tills (right-click) and reaps (swing). " : "Sickles are retired - your Harvester reaps (swing) and tills (right-click). ");
  @INV@ inv = p.getInventory();
  N[6] = N[6] + 1L;
  IN.set(Boolean.TRUE);
  try {
    LASTRUN.remove(u);
    @PKG@.GearLife.sweep0(pr, inv, true);
    P = @PKG@.GearLL.reg(pk);
    if (!@PKG@.GearLL.merged(P)) {
      String r0 = @PKG@.GearLife.reclaimW(pr, p, 3, w);          // the sickle first (Requip, a window, the Vault, its chest, an exact copy)
      LASTRUN.remove(u);
      FETCH.remove(u + ":h");
      @PKG@.GearLife.sweep0(pr, inv, true);
      P = @PKG@.GearLL.reg(pk);
      if (@PKG@.GearLL.merged(P)) return "+" + pre + "Your hoe and sickle are one Harvester now - it is in your inventory. Lost it later? /harvester";
      String hu0 = P.getProperty("hoe.uid");
      if (hu0 != null && @PKG@.GearLife.find(inv, pk, hu0) == null && @PKG@.GearLife.find(inv, pk, P.getProperty("sickle.uid")) != null) {          // critic fix 3: the hoe too
        String r1 = @PKG@.GearLife.reclaimW(pr, p, 2, w);
        LASTRUN.remove(u);
        @PKG@.GearLife.sweep0(pr, inv, true);
        P = @PKG@.GearLL.reg(pk);
        if (@PKG@.GearLL.merged(P)) return "+" + pre + "Your hoe came back and your hoe and sickle are one Harvester now - it is in your inventory. Lost it later? /harvester";
        return mark(r1) + pre + body(r1) + " Your hoe and sickle become your Harvester as soon as both are in your inventory.";
      }
      return mark(r0) + pre + harvText(body(r0)) + " It becomes your Harvester as soon as it is in your inventory.";
    }
    String r = @PKG@.GearLife.reclaimW(pr, p, 3, w);
    return mark(r) + pre + harvText(body(r));
  } finally { IN.remove(); }
}""")
# the Tools tab's "Make Harvester" (GearLife.harvest, before) while harvester.only is on: the automatic merge's rules (every line, no point trim)
# run now; its preview (GearLife.harvPreview, before) shows those rules. null = the 0.3.12 button (an undone profile)
M(gharv, r"""
public static String button(@PR@ pr, @INV@ inv) {
  if (!on() || pr == null || inv == null) return null;
  java.util.UUID u = pr.getUuid();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P) || "undone".equals(P.getProperty("harvAuto"))) return null;
  if (@PKG@.GearLL.merged(P)) return "-You already have your Harvester.";
  LASTRUN.remove(u);
  FETCH.remove(u + ":h");
  @PKG@.GearLife.sweep0(pr, inv, true);
  P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.merged(P)) return "+Your hoe and sickle are one Harvester now - every line and the higher Upgrade Points of both. Right-click tills, a swing reaps. Lost it? /harvester";
  return "-Your hoe and sickle could not become your Harvester yet - carry your sickle (/sickle brings it).";
}""")
M(gharv, r"""
public static String[] preview(java.util.UUID u, @INV@ inv, java.util.Properties P, Object[] c) {
  if (!on() || c == null || c[0] != null || inv == null || P == null || "undone".equals(P.getProperty("harvAuto"))) return null;
  try {
    int[] ha = (int[]) c[1];
    int[] sa = (int[]) c[2];
    @IS@ h = @PKG@.GearStamp.at(inv, ha[0], ha[1]);
    @IS@ s = @PKG@.GearStamp.at(inv, sa[0], sa[1]);
    int[] info = new int[4];
    @BD@ nd = @PKG@.GearLife.harvDocAll(@PKG@.GearLife.docOf(h), @PKG@.GearLife.docOf(s), (String) c[3], u, info);
    if (nd == null) return null;
    return new String[] { @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(nd)], String.valueOf(@PKG@.GearData.mods(nd).size()), String.valueOf(info[0]), String.valueOf(info[1]), "" };
  } catch (Throwable t) { return null; }
}""")
M(gharv, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  LASTRUN.remove(u);
  ONEUP.remove(u);
  FETCH.remove(u + ":s");
  FETCH.remove(u + ":h");
}""")
# ---- GearHarvCrop: the interaction type SkyyGearHarvest (HarvestCropInteraction's codec keys, vanilla's harvest + the tier rule)
C(ghcrop, "public GearHarvCrop() { super(); }")
F(ghcrop, "public static volatile @C2BCOD@ SKCODEC = null;")
F(ghcrop, "public static volatile boolean REG = false;")
F(ghcrop, "public static volatile String REG_WHY = \"not registered yet\";")
M(ghcrop, r"""
protected void interactWithBlock(@WLD@ w, @CB@ cb, @ITYPE@ type, @ICTX@ ctx, @IS@ item, @VECI@ pos, @C2CD@ cd) {
  int a = 0;
  try { a = @PKG@.GearHarv.swing(w, cb, ctx, item, pos); } catch (Throwable t) { a = 0; @PKG@.Gear.warnOnce("harvswing", "the Harvester sweep tier check failed (vanilla's harvest ran; logged once): " + t); }
  if (a == 0) { super.interactWithBlock(w, cb, type, ctx, item, pos, cd); return; }
  if (a == 1) @PKG@.GearCan.fail(ctx);          // the Failed path = the ordinary hit (Block_Break_Adventure): the tier gate pays half XP
}""")
ghsup.addInterface(pool.get("java.util.function.Supplier"))
C(ghsup, "public GearHarvSup() { }")
M(ghsup, "public Object get() { return new @PKG@.GearHarvCrop(); }")
M(ghcrop, r"""
public static @C2BCOD@ codec() {
  @C2BCOD@ c = SKCODEC;
  if (c != null) return c;
  c = @C2BCOD@.builder(@PKG@.GearHarvCrop.class, new @PKG@.GearHarvSup(), @C3HC@.CODEC).build();
  SKCODEC = c;
  return c;
}""")
# ---- GearSigDrop: Sigil drops (sigil.* rows): mob kills (GearDeathMark), the bag lists (GearSigBag)
for _f in ("public static final long[] N = new long[10];",          # 0 kills looked at, 1 mob Sigils, 2 mini boss Sigils, 3 boss Sigils, 4 bag rolls, 5 bag Sigils, 6 lists wrapped, 7 no item
           "public static final java.util.concurrent.ConcurrentHashMap ROLLED = new java.util.concurrent.ConcurrentHashMap();",   # npc UUID -> Long
           "public static final java.util.concurrent.ConcurrentHashMap PARSE = new java.util.concurrent.ConcurrentHashMap();",    # "n|text" -> double[]
           "public static final java.util.concurrent.ConcurrentHashMap WR = new java.util.concurrent.ConcurrentHashMap();",       # list id -> GearSigBag
           "public static final java.util.concurrent.atomic.AtomicBoolean BUSY = new java.util.concurrent.atomic.AtomicBoolean(false);",
           "public static volatile java.util.Random RNG = null;"):          # HARNESS SEAM ONLY (null = GearRoll.RNG)
    F(gsigd, _f)
M(gsigd, r"""
public static double[] parse(String v, int n, double hi) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length != n) return null;
  double[] a = new double[n];
  for (int i = 0; i < n; i++) {
    try { a[i] = Double.parseDouble(p[i].trim()); } catch (Throwable t) { return null; }
    if (Double.isNaN(a[i]) || a[i] < 0.0 || a[i] > hi) return null;
  }
  return a;
}""")
M(gsigd, r"""
public static String check(String key, String value) {
  if (key != null && key.endsWith("bossZone")) return parse(value, 4, 20.0) == null ? "Four numbers from 0 to 20 (zones 1, 2, 3, 4), joined by commas." : null;
  return parse(value, 5, 100.0) == null ? "Five % numbers from 0 to 100 (Unique, Rare, Legendary, Fabled, Mythic), joined by commas." : null;
}""")
M(gsigd, r"""
public static double[] row(String v, int n, double hi, String def, String key) {
  String k = n + "|" + v;
  Object o = PARSE.get(k);
  if (o instanceof double[]) return (double[]) o;
  double[] a = parse(v, n, hi);
  if (a == null) {
    @PKG@.Gear.warnOnce("sigrow:" + key + ":" + (v == null ? 0 : v.hashCode()), "config.properties: " + key + " '" + v + "' is not " + n + " numbers 0-" + (int) hi + " - the default " + def + " applies");
    a = parse(def, n, hi);
  }
  if (PARSE.size() > 64) PARSE.clear();
  PARSE.put(k, a);
  return a;
}""")
M(gsigd, "public static double[] mobT() { return row(@PKG@.GearCfg.SIGD_MOB, 5, 100.0, \"@@MOB@@\", \"sigil.mob\"); }")
M(gsigd, "public static double[] bagT() { return row(@PKG@.GearCfg.SIGD_BAG, 5, 100.0, \"@@BAG@@\", \"sigil.bag\"); }")
M(gsigd, "public static double[] miniT() { return row(@PKG@.GearCfg.SIGD_MINI, 5, 100.0, \"@@MINI@@\", \"sigil.mini\"); }")
M(gsigd, "public static double[] bossT() { return row(@PKG@.GearCfg.SIGD_BOSS, 5, 100.0, \"@@BOSS@@\", \"sigil.boss\"); }")
M(gsigd, "public static double[] zoneT() { return row(@PKG@.GearCfg.SIGD_ZONE, 4, 20.0, \"@@ZONE@@\", \"sigil.bossZone\"); }")
M(gsigd, "public static boolean on() { return @PKG@.GearCfg.SIGD_ON && @PKG@.GearCfg.SIG_ON; }")
# SkyyArmory's rule (Monk.bossWord): a word must be a whole part of the role name (split at _), any case
M(gsigd, r"""
public static boolean word(String role, String words) {
  if (role == null || words == null) return false;
  String r = "_" + role.trim().toLowerCase() + "_";
  String[] ws = words.split(",");
  for (int i = 0; i < ws.length; i++) {
    String w = ws[i].trim().toLowerCase();
    if (w.length() > 0 && r.indexOf("_" + w + "_") >= 0) return true;
  }
  return false;
}""")
M(gsigd, "public static int kindOf(String role) { return word(role, @PKG@.GearCfg.SIGD_BOSSW) ? 2 : (word(role, @PKG@.GearCfg.SIGD_MINIW) ? 1 : 0); }")
# the zone of a mob level (the chest-level bands: 1-20, 21-30, 31-45, 46+); no level = zone 1
M(gsigd, "public static int zoneOf(int lvl) { return lvl <= 20 ? 1 : (lvl <= 30 ? 2 : (lvl <= 45 ? 3 : 4)); }")
M(gsigd, "public static double rnd() { java.util.Random r = RNG; return r != null ? r.nextDouble() : @PKG@.GearRoll.RNG.nextDouble(); }")
# one roll per rarity, Mythic first: the first hit is the Sigil (null = none); x = the chance multiplier; ds = the drop roll's random source (null = rnd())
M(gsigd, r"""
public static String pick(double[] pct, double x, java.util.function.DoubleSupplier ds) {
  if (pct == null) return null;
  for (int i = pct.length - 1; i >= 0; i--) {
    double c = pct[i] * x;
    if (!(c > 0.0)) continue;
    double r = ds != null ? ds.getAsDouble() : rnd();
    if (r * 100.0 < c) return i < @PKG@.GearSigil.IDS.length ? @PKG@.GearSigil.IDS[i] : null;
  }
  return null;
}""")
M(gsigd, r"""
public static void prune(long now) {
  if (ROLLED.size() < 512) return;
  Object[] ks = ROLLED.keySet().toArray();
  for (int i = 0; i < ks.length; i++) {
    Object v = ROLLED.get(ks[i]);
    if (v instanceof Long && now - ((Long) v).longValue() > 60000L) ROLLED.remove(ks[i]);
  }
}""")
# THE MOB KILL (GearDeathMark.tick, after; world thread): a death DropDeathItems handles now (the same condition), killed by a player (not
# Creative); boss / mini boss by role words, else a LEVELLED mob; at most one Sigil, dropped beside the mob's own loot (vanilla's spawn)
M(gsigd, r"""
public static int mob(@ACH@ chunk, int idx, @ST@ store, @CB@ cb) {
  if (!on() || chunk == null || store == null) return 0;
  @DTHC@ dc = (@DTHC@) chunk.getComponent(idx, @DTHC@.getComponentType());
  if (dc == null || dc.getItemsLossMode() != @ILM@.ALL) return 0;
  @NPCE@ npc = (@NPCE@) chunk.getComponent(idx, @NPCE@.getComponentType());
  if (npc == null) return 0;
  @ROLE@ role = npc.getRole();
  if (role == null || role.hasDroppedDeathItems()) return 0;
  if (!role.isDropDeathItemsInstantly()) {
    @DCR@ dcr = (@DCR@) chunk.getComponent(idx, @DCR@.getComponentType());
    if (dcr != null && !dcr.shouldRemove()) return 0;
  }
  if (chunk.getComponent(idx, @PLA@.getComponentType()) != null) return 0;
  @TC@ tc = (@TC@) chunk.getComponent(idx, @TC@.getComponentType());
  if (tc == null || tc.getPosition() == null) return 0;
  @HRC@ hr = (@HRC@) chunk.getComponent(idx, @HRC@.getComponentType());
  @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
  java.util.UUID nu = uc == null ? null : uc.getUuid();
  if (nu == null) return 0;
  long now = System.currentTimeMillis();
  prune(now);
  if (ROLLED.putIfAbsent(nu, Long.valueOf(now)) != null) return 0;
  @REF@ kr = @PKG@.GearLoot.killer(dc, store);
  if (kr == null) return 0;
  @PR@ kp = (@PR@) store.getComponent(kr, @PR@.getComponentType());
  if (kp == null) return 0;
  @PLA@ pl = (@PLA@) store.getComponent(kr, @PLA@.getComponentType());
  try { if (pl != null && pl.getGameMode() == @GM@.Creative) return 0; } catch (Throwable tg) { }
  String rn = null;
  try { rn = npc.getRoleName(); } catch (Throwable tr) { rn = null; }
  int kd = kindOf(rn);
  String wk = @PKG@.GearTag.key(store.getExternalData());
  int lvl = @PKG@.GearLoot.mobLevel(chunk, idx, wk);
  if (kd == 0 && lvl < 1) return 0;          // ordinary mobs: the levelled fighters only (never a chicken)
  N[0] = N[0] + 1L;
  int z = zoneOf(lvl);
  double[] zt = zoneT();
  double x = kd == 2 && zt != null && z >= 1 && z <= zt.length ? zt[z - 1] : 1.0;
  String sid = pick(kd == 2 ? bossT() : (kd == 1 ? miniT() : mobT()), x, (java.util.function.DoubleSupplier) null);
  if (sid == null) return 0;
  if (@PKG@.Gear.item(sid) == null) { N[7] = N[7] + 1L; return 0; }
  @IS@ st = new @IS@(sid, 1);
  @VEC@ at = new @VEC@(tc.getPosition());
  at = at.add(0.0, 1.0, 0.0);
  java.util.function.BiFunction seam = @PKG@.GearLoot.SPAWN;
  if (seam != null) seam.apply(st, at);
  else {
    if (hr == null) return 0;
    java.util.ArrayList l = new java.util.ArrayList();
    l.add(st);
    @HLDR@[] hs = @ITC@.generateItemDrops(store, l, at, new @RTF@(hr.getRotation()));
    if (hs == null || hs.length == 0) return 0;
    cb.addEntities(hs, @ADDR@.SPAWN);
  }
  N[1 + kd] = N[1 + kd] + 1L;
  @PKG@.GearLog.line("SIGIL-DROP " + (kd == 2 ? "boss" : (kd == 1 ? "mini" : "mob")) + " " + rn + " Lv" + lvl + " zone " + z + " x" + x + " -> " + sid + " (" + kp.getUsername() + " " + kp.getUuid() + " " + wk + ")");
  return 1;
}""")
# one roll of a bag list (GearSigBag.populateDrops): the Sigil to add, or null
M(gsigd, r"""
public static String bagRoll(java.util.function.DoubleSupplier ds) {
  if (!on()) return null;
  N[4] = N[4] + 1L;
  String sid = pick(bagT(), 1.0, ds);
  if (sid == null) return null;
  if (@PKG@.Gear.item(sid) == null) { N[7] = N[7] + 1L; return null; }
  N[5] = N[5] + 1L;
  return sid;
}""")
# ---- GearSigBag: a bag list's container (its own roll, then maybe ONE Sigil); getAllDrops lists the inner list's drops only
F(gsbag, "public @IDC@ inner;")
F(gsbag, "public String lid;")
C(gsbag, r"""
public GearSigBag(@IDC@ in, String lid) {
  super(in == null ? 0.0 : in.getWeight());
  this.inner = in;
  this.lid = lid;
}""")
M(gsbag, r"""
protected void populateDrops(java.util.List out, java.util.function.DoubleSupplier ds, java.util.Set seen) {
  if (this.inner == null || out == null) return;
  this.inner.populateDrops(out, ds, this.lid);
  try {
    String sid = @PKG@.GearSigDrop.bagRoll(ds);
    if (sid != null) {
      out.add(new @IDR@(sid, (org.bson.BsonDocument) null, 1, 1));
      @PKG@.GearLog.line("SIGIL-DROP bag " + this.lid + " -> " + sid);
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("sigbag", "a Loot Bag Sigil roll failed (logged once): " + t); }
}""")
M(gsbag, "public java.util.List getAllDrops(java.util.List out) { return this.inner == null ? out : this.inner.getAllDrops(out); }")
M(gsbag, 'public String toString() { return "GearSigBag{" + this.lid + ", " + this.inner + "}"; }')
# the bag lists get a GearSigBag (outermost when the list has none yet; GearNormDrop / GearStick may wrap around it later - each finds its own);
# a list that left sigil.bagLists (or Sigil drops off) loses ours. Returns the lists wrapped (-1 = the field cannot be set)
M(gsigd, r"""
public static boolean bagList(String id) {
  if (id == null) return false;
  String v = @PKG@.GearCfg.SIGD_BAGS;
  if (v == null || v.trim().length() == 0) return false;
  String[] p = v.split(",");
  for (int i = 0; i < p.length; i++) { String t = p[i].trim(); if (t.length() >= 3 && id.startsWith(t)) return true; }
  return false;
}""")
M(gsigd, r"""
public static void publish() {
  try { @PKG@.Gear.bridge().put("gear:sigil:drops", Boolean.valueOf(on())); } catch (Throwable t) { }
}""")
M(gsigd, r"""
public static int ensure() {
  publish();          // critic fix 1: SkyyArmory 0.1.30 skips its own boss Sigil roll while this is TRUE
  if (!BUSY.compareAndSet(false, true)) return -2;
  try {
    java.lang.reflect.Field f = @PKG@.GearNorm.field();
    if (f == null) return -1;
    java.util.Map m = null;
    try { m = @IDL@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
    if (m == null) return -1;
    boolean on = on();
    java.util.ArrayList es = new java.util.ArrayList(m.entrySet());
    java.util.HashSet ids = new java.util.HashSet();
    int n = 0;
    for (int i = 0; i < es.size(); i++) {
      java.util.Map.Entry e = (java.util.Map.Entry) es.get(i);
      Object o = e.getValue();
      if (!(o instanceof @IDL@)) continue;
      @IDL@ l = (@IDL@) o;
      String id = String.valueOf(e.getKey());
      try {
        @IDC@ c = l.getContainer();
        if (c == null) continue;
        Object par = null;          // the wrapper that holds ours (null = ours is outermost)
        @PKG@.GearSigBag mine = null;
        if (c instanceof @PKG@.GearSigBag) mine = (@PKG@.GearSigBag) c;
        else if (c instanceof @PKG@.GearNormDrop && ((@PKG@.GearNormDrop) c).inner instanceof @PKG@.GearSigBag) { par = c; mine = (@PKG@.GearSigBag) ((@PKG@.GearNormDrop) c).inner; }
        else if (c instanceof @PKG@.GearStick && ((@PKG@.GearStick) c).inner instanceof @PKG@.GearSigBag) { par = c; mine = (@PKG@.GearSigBag) ((@PKG@.GearStick) c).inner; }
        else if (c instanceof @PKG@.GearStick && ((@PKG@.GearStick) c).inner instanceof @PKG@.GearNormDrop && ((@PKG@.GearNormDrop) ((@PKG@.GearStick) c).inner).inner instanceof @PKG@.GearSigBag) {
          par = ((@PKG@.GearStick) c).inner;
          mine = (@PKG@.GearSigBag) ((@PKG@.GearNormDrop) par).inner;
        }
        boolean want = on && bagList(id);
        if (want && mine == null) {
          @PKG@.GearSigBag g = new @PKG@.GearSigBag(c, id);
          f.set(l, g);
          WR.put(id, g);
          n++;
        } else if (!want && mine != null) {
          if (par == null) f.set(l, mine.inner);
          else if (par instanceof @PKG@.GearNormDrop) ((@PKG@.GearNormDrop) par).inner = mine.inner;
          else if (par instanceof @PKG@.GearStick) ((@PKG@.GearStick) par).inner = mine.inner;
          WR.remove(id);
        } else if (mine != null) { WR.put(id, mine); n++; ids.add(id); }
        if (want) ids.add(id);
      } catch (Throwable t2) { @PKG@.Gear.warnOnce("sigbag:" + id, "Sigil drops: the drop list " + id + " could not be wrapped: " + t2); }
    }
    WR.keySet().retainAll(ids);
    N[6] = (long) n;
    return n;
  } finally { BUSY.set(false); }
}""")
M(gsigd, "public static void refresh(String key) { ensure(); }")          # Server Setup after= hook (sigil.bagLists)
M(gsigd, r"""
public static void unwrapAll() {
  boolean was = @PKG@.GearCfg.SIGD_ON;
  @PKG@.GearCfg.SIGD_ON = false;
  try { ensure(); } catch (Throwable t) { }
  @PKG@.GearCfg.SIGD_ON = was;
  WR.clear();
  try { @PKG@.Gear.bridge().remove("gear:sigil:drops"); } catch (Throwable t) { }          // SkyyGear gone: SkyyArmory rolls its boss Sigils again
}""")
M(gsigd, r"""
public static String statusText() {
  if (!on()) return "Sigil drops OFF (sigil.drops" + (@PKG@.GearCfg.SIG_ON ? "" : " / part.sigils") + ")";
  return "Sigil drops on (mob " + @PKG@.GearCfg.SIGD_MOB + ", Loot Bag " + @PKG@.GearCfg.SIGD_BAG + " on " + N[6] + " lists, mini boss " + @PKG@.GearCfg.SIGD_MINI + ", boss " + @PKG@.GearCfg.SIGD_BOSS + " x zone " + @PKG@.GearCfg.SIGD_ZONE + "; dropped: mobs " + N[1] + ", mini bosses " + N[2] + ", bosses " + N[3] + ", bags " + N[5] + " of " + N[4] + " rolls)" + "; Mythic Sigil " + (@PKG@.GearCfg.SIG_MY ? "works on the Anvil" : "refused (sigil.mythicUse)") + "; Sigils on Mining Sets " + (@PKG@.GearCfg.MINE_SIG ? "yes" : "no");
}""")
M(gharv, r"""
public static String statusText() {
  return "one farming tool " + (on() ? "ON (hoe + sickle retired: kit = the Crude Harvester; " + N[0] + " merged this start, " + @PKG@.GearLife.HA[3] + " from a hoe snapshot, " + @PKG@.GearLife.HA[4] + " without a hoe, " + N[1] + " kit markers, " + N[2] + " fetches, " + N[3] + " waiting for the sickle, " + N[4] + " not yet, " + N[5] + " undone)" : "off (harvester.only" + (@PKG@.GearCfg.HARV_ON ? "" : " / part.harvester") + ")")
    + "; sweep tier " + (@PKG@.GearCfg.FARM_T1 ? "on (Crude = T1 on crops; the swing's interaction " + (@PKG@.GearHarvCrop.REG ? "registered" : "NOT registered: " + @PKG@.GearHarvCrop.REG_WHY) + "; crops seen " + SW[0] + ", one-up broken " + SW[1] + ", skipped " + (SW[2] + SW[3]) + ")" : "off (farm.crudeT1)")
    + "; till area " + (@PKG@.GearCfg.HOE_ELSE ? "everywhere" : "islands only") + "; " + @PKG@.GearSigDrop.statusText();
}""")
# ---- /gear harvmerge (admin)
M(ghcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String rest = @PKG@.GearAdmin.rest(ctx, "harvmerge").trim();
    String[] a = rest.length() == 0 ? new String[0] : rest.split("\\s+");
    if (a.length == 0 || a[0].equalsIgnoreCase("status")) { @PKG@.GearAdmin.msg(pr, @PKG@.GearHarv.statusText()); return; }
    if (a[0].equalsIgnoreCase("undo") && a.length >= 2) {
      @PR@ target = null;
      java.util.Iterator it = @UNI@.get().getPlayers().iterator();
      while (it.hasNext()) {
        Object o = it.next();
        if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(a[1])) { target = (@PR@) o; break; }
      }
      if (target == null) { @PKG@.GearAdmin.msg(pr, "no online player called " + a[1] + " (the undo runs on an online player)"); return; }
      String tpk = @PKG@.Gear.pkey(target.getUuid());
      if (@PKG@.GearHarv.pending(tpk) == 0) { @PKG@.GearAdmin.msg(pr, "no Harvester merge on record for " + target.getUsername() + "'s active profile (" + tpk + ") - nothing to undo"); return; }
      boolean force = a.length >= 3 && a[2].equalsIgnoreCase("force");          // critic fix 4
      String why = @PKG@.GearHarv.undoWhy(tpk);
      if (why != null && !force) { @PKG@.GearAdmin.msg(pr, "REFUSED: " + target.getUsername() + "'s Harvester changed since the merge (" + why + "). The undo gives back the hoe + sickle AS THEY WERE and loses those changes - type /gear harvmerge undo " + target.getUsername() + " force to do it anyway."); return; }
      if (why != null) @PKG@.GearAdmin.msg(pr, "WARNING (force): " + target.getUsername() + "'s Harvester changed since the merge (" + why + ") - those changes are lost by the undo.");
      @PKG@.GearHarv.UNDO.put(target.getUuid(), pr.getUsername() + (force ? "|force" : ""));
      @PKG@.GearHarv.LASTRUN.remove(target.getUuid());
      @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " harvmerge undo " + target.getUsername() + " " + target.getUuid());
      @PKG@.GearAdmin.msg(pr, "queued: at " + target.getUsername() + "'s next inventory change their Harvester (carried) turns back into the hoe + sickle of the merge (their active profile; one free slot). That profile is never merged automatically again.");
      return;
    }
    @PKG@.GearAdmin.msg(pr, "usage: /gear harvmerge  (the counters)  |  /gear harvmerge undo <player> [force]");
  } catch (Throwable t) {
    @PKG@.Gear.warn("/gear harvmerge failed: " + t);
    pr.sendMessage(@MSG@.raw("[Gear] That did not work - the server log has the details."));
  }
}""")
# ---- the hooks
glf.getDeclaredMethod("sweep0").insertAfter(J("{ try { @PKG@.GearHarv.sweepHook($1, $2); } catch (Throwable thh) { @PKG@.Gear.warnOnce(\"harvsweep\", \"the Harvester merge look failed: \" + thh); } }"))
_rcw = [m for m in glf.getDeclaredMethods() if str(m.getName()) == "reclaimW"]
assert len(_rcw) == 1 and str(_rcw[0].getSignature()).startswith("(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/entity/entities/Player;I"), [str(m.getSignature()) for m in _rcw]
_rcw[0].insertBefore(J("{ String hr0 = null; try { hr0 = @PKG@.GearHarv.cmd($1, $2, $3, $4, (String) null); } catch (Throwable thr) { hr0 = null; @PKG@.Gear.warnOnce(\"harvcmd\", \"/hoe /sickle: the Harvester answer failed: \" + thr); } if (hr0 != null) return hr0; }"))
_hvb = [m for m in glf.getDeclaredMethods() if str(m.getName()) == "harvest"]
assert len(_hvb) == 1 and str(_hvb[0].getSignature()).startswith("(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/inventory/Inventory;)"), [str(m.getSignature()) for m in _hvb]
_hvb[0].insertBefore(J("{ String r9 = null; try { r9 = @PKG@.GearHarv.button($1, $2); } catch (Throwable t9) { r9 = null; } if (r9 != null) return r9; }"))
_hvp = [m for m in glf.getDeclaredMethods() if str(m.getName()) == "harvPreview"]
assert len(_hvp) == 1
_hvp[0].insertBefore(J("{ String[] p9 = null; try { p9 = @PKG@.GearHarv.preview($1, $2, $3, $4); } catch (Throwable t8) { p9 = null; } if (p9 != null) return p9; }"))
_hvx = [m for m in hvc.getDeclaredMethods() if str(m.getName()) == "execute"]
assert len(_hvx) == 1
_hvx[0].insertBefore(J("""{
  String hr1 = null;
  try {
    @PLA@ p1 = (@PLA@) $2.getComponent($3, @PLA@.getComponentType());
    hr1 = @PKG@.GearHarv.cmd($4, p1, 3, $5, "");
  } catch (Throwable thv) { hr1 = null; }
  if (hr1 != null) { $4.sendMessage(@MSG@.raw("[Gear] " + @PKG@.GearUi.infoText(hr1)).color(@PKG@.GearUi.infoColor(hr1))); return; }
}"""))
_dmt = [m for m in gdm.getDeclaredMethods() if str(m.getName()) == "tick" and str(m.getSignature()).startswith("(FILcom/hypixel/hytale/component/ArchetypeChunk;")]
assert len(_dmt) == 1, [str(m.getSignature()) for m in gdm.getDeclaredMethods() if str(m.getName()) == "tick"]
_dmt[0].insertAfter(J("{ try { @PKG@.GearSigDrop.mob($3, $2, $4, $5); } catch (Throwable tsd) { @PKG@.Gear.warnOnce(\"sigmob\", \"a mob Sigil roll failed: \" + tsd); } }"))
gnorm.getDeclaredMethod("ensure0").insertAfter(J("{ try { @PKG@.GearSigDrop.ensure(); } catch (Throwable tse) { } }"))
pl.getDeclaredMethod("setup").insertAfter(J("""{
  try {
    @C2ACM@ acm2 = @C2INT@.CODEC;
    getCodecRegistry(acm2).register("SkyyGearHarvest", @PKG@.GearHarvCrop.class, @PKG@.GearHarvCrop.codec());
    @PKG@.GearHarvCrop.REG = true;
    @PKG@.GearHarvCrop.REG_WHY = "registered";
  } catch (Throwable thc) {
    @PKG@.GearHarvCrop.REG = false;
    @PKG@.GearHarvCrop.REG_WHY = String.valueOf(thc);
    @PKG@.Gear.warn("the Harvester sweep interaction type SkyyGearHarvest could not be registered (" + thc + ") - the Harvester's swing reaps nothing until it is");
  }
}"""))
pl.getDeclaredMethod("start").insertAfter(J("""{
  try {
    @PKG@.GearSigDrop.ensure();
    @PKG@.Gear.info("[SkyyGear] 0.3.14: " + @PKG@.GearHarv.statusText());
  } catch (Throwable tst4) { @PKG@.Gear.warn("0.3.14 setup failed: " + tst4); }
}"""))
pl.getDeclaredMethod("shutdown").insertBefore(J("{ try { @PKG@.GearSigDrop.unwrapAll(); } catch (Throwable tsu) { } }"))
for _m in _byeM:
    _m.insertBefore(J("{ try { if ($1 instanceof @PDE@) @PKG@.GearHarv.forget(((@PDE@) $1).getPlayerRef().getUuid()); } catch (Throwable thf) { } }".replace("@PDE@", PDE)))
_scl4 = _calls(PKG + ".SkyyGearPlugin", "setup")
assert _scl4.count("CodecMapRegistry$Assets.register") >= 2, "setup() does not register SkyyGearHarvest"
print("0.3.14 one farming tool / sweep tier / Sigil drops: GearHarv / GearHarvCrop (SkyyGearHarvest) / GearHarvSup / GearSigDrop / GearSigBag / GearHarvCmd; hooks in sweep0, reclaimW, HarvCmd, GearDeathMark.tick, GearNorm.ensure0, setup / start / shutdown")
'''
G314 = G314.replace('@@MOB@@', SIG_MOB_DEF).replace('@@BAG@@', SIG_BAG_DEF).replace('@@MINI@@', SIG_MINI_DEF).replace('@@BOSS@@', SIG_BOSS_DEF).replace('@@ZONE@@', SIG_ZONE_DEF)
assert '@@' not in G314
after('''print("0.3.13 normal tools off: GearNorm / GearNormDrop / GearNormL / GearNormFn / GearNormCmd; hooks in sweep0, GearChestOpen.process, GearSickle.tick, GearCfg.apply, GearBoxL, setup / start / shutdown")
''', G314)

# ================================================================================================================ the manifest, the class list
rep('''lifelong tier-ups into Thorium and up also cost Enchanted Sticks; Server Setup -> Gear. Replaces SkyyRolls.''',
    '''lifelong tier-ups into Thorium and up also cost Enchanted Sticks; ONE FARMING TOOL: the lifelong hoe and sickle retire - every profile starts with a Crude Harvester, an existing hoe + sickle merge once into one (logged; /gear harvmerge undo); a Crude farming tool is T1 on crops and the Harvester's sweep reaps only crops of its tier or lower; Sigils work on Mining Set armor, the Mythic Sigil works on the Anvil, Sigils drop from mobs, Loot Bags, mini bosses and bosses; the hoe area tills everywhere; Server Setup -> Gear. Replaces SkyyRolls.''')
rep('''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES + G313_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES + G313_CLASSES + G314_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')

# ================================================================================================================ checks on the result
assert s.index("public static String harvPerksAll(java.util.Properties P) {") < s.index("public static boolean harvFinal(")
assert s.index("public static boolean harvFinal(") < s.index("public static String harvAuto(") < s.index("public static boolean harvRecover(")
assert s.index("public static boolean minePiece(String id, @BD@ d) {") < s.index("public static String why(@IS@ it, @BD@ d, int R) {") < s.index("public void anSigil(")
assert s.index('C(ghcmd, r"""') < s.index('C(gcm, r"""') and s.index('ghcmd = mk("GearHarvCmd", APC)') < s.index('C(ghcmd, r"""')
assert s.index("gharv = mk(\"GearHarv\")") > s.index("gnorm = mk(\"GearNorm\")") and s.index("gharv = mk(\"GearHarv\")") < s.index("0.3.10 ALWAYS ANSWER (tools") < s.index("ALL = [gu, gdf, gcf")
assert s.index("public static String onlyFor2(") < s.index('M(gll, "public static String onlyFor(int f, int t, String def)') < s.index("@PKG@.GearLL.onlyFor2((int) st[0]")
assert s.index("def _harv_vars(sic):") < s.index('"InteractionVars": _harv_vars(_sic)') and s.index('HARV_INT_ID = "SkyyGear_Harvest_Crop"') < s.index("def _harv_vars(sic):")
assert s.count("addSubCommand(new @PKG@.GearHarvCmd())") == 1 and s.count("migrate0314();") == 1
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.13 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.13 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
