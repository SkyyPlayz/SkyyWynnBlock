"""Derive SkyyGear/build_skyygear_0.3.0.py from the LIVE 0.2.26 (build_skyygear_0.2.26.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_26_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_3_0_patch.py      then      python SkyyGear/build_skyygear_0.3.0.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.0.py

0.3.0 = LIFELONG TOOLS + THE TIER GATE (phase 3 of research/Gathering-Shards-Spec.md; Skyy's answers in docs/answered/gear.md 2026-10-11 ..
2026-10-13 WIN over the spec where they differ). Skyy's own words this round follows (word for word):
  "tools dont have XP they just match your skill level. since you spawn with the tool, and cant make more, you can only upgrade them, there
   is no need to add another xp bar. when the skill levels up, it sends something that levels up the tool in your inventory to match. (we
   need inventory protection on items. (make it so you cant drop your tools. they can be placed in chests, backpacks, and what not, but not
   dropped trashed or salvaged. and if users manage to loose it, we need a command like /pickaxe. that will give you a basic common pickaxe
   at your level."  + "1 point per skill level (Recommended)"
  "youll start with the hatchet, the pickaxe, the hoe, and the cycle, but well do a quest at hub to get into fishing."
  G1 "25 Copper Ingots (Recommended)", G4 "0.1 speed (10x hits)", G5 "Yes, as proposed (Recommended)", G6 "yes, for coins. costs more every
  time." (+ the rebirth part, NOT built: rebirth does not exist yet), "the shovel is weird, we can leave it out as a craft item".
Built on the LIVE 0.2.26: GearSnap, the one Anvil tab and every lag fix are untouched.

1. ONE OF EACH, FOR LIFE (GearLL = read side before GearTool, GearLife = write side): every profile owns ONE pickaxe, hatchet, hoe and
   sickle (the shovel stays a plain craftable item; the fishing pole comes with the hub quest later). The tool's SkyyGear document gets
   ll=1, lu=<uid>, lo=<profile key> (+ lrp=1 on a /pickaxe replacement); the per-profile registry Skyy_SkyyGear/lifelong/<pkey>.properties
   names the uid of each kind (the document is the item, the uid is the truth). Read once per join on the scheduler (prefetch), written
   only on the rare events (migration, /pickaxe, a perk, a reset, a restore) with tmp + fsync + atomic move, no sleep-retry.
2. NO TOOL XP BAR: the tool's LEVEL = your skill level (Mining / Foraging / Farming), capped by its tier's band top (level.material - Crude
   13, Copper 18, Iron 23 ... Skyy's live edits apply). GearTool uses that level for every hit (whatever the document says); the sweep
   (each inventory scan, so after every skill level-up) rewrites the document's lvl so "[Lv N]" and the tooltip follow. UPGRADE POINTS:
   1 per skill level (earned = skill level - 1), spent on perks per kind: Speed (+2 % power / level, max 10, pickaxe + hatchet), Fortune
   (+1 / level, max 10, all four), Wisdom (+1 % XP / level, max 5, 2 points, needs an Iron tool), Vein Mine (pickaxe) / Tree Feller
   (hatchet) +1 / level (max 3, 3 / 5 / 8 points, Iron / Thorium / Cobalt) - those two only once SkyyTrees reads them (gear:fn:perk +
   gear:perk:readers; until then the page says "coming with the next SkyyTrees"). Reset for coins: lifelong.resetCoins x spent points x
   (resets so far + 1) - "costs more every time". Page: /toolpoints = the new Tools tab of /smithing.
   NOT BUILT YET from the spec's perk table (G5 "as proposed"): Magnet, Wide Till, Wide Sweep, Green Thumb (replant), Auto-Smelt, Steady Line
   (fishing) - later rounds; Vein Mine / Tree Feller wait for SkyyTrees.
3. PROTECTION: a lifelong tool cannot be DROPPED (GearLLDropSys on DropItemEvent$PlayerRequest - the Drop key / drag out, from your
   inventory or a container window: cancelled before anything is removed; FIX ROUND 2: only YOUR working one - another player's lifelong tool
   and your own retired one may be dropped), never goes on the Auction House / Bazaar (GearWall), is never
   merged into a multitool (rebirth 1, later) and its level is never bought (Reforge Level up refuses). SALVAGE needs nothing new: the
   Salvagebench (ProcessingBenchBlock.updateRecipe -> InternalContainerUtilMaterial.testRemoveMaterialFromSlot -> ItemStack.isEquivalentType,
   VERIFIED bytecode) never takes a stack whose metadata differs from the recipe's (none) - every lifelong tool carries its document.
   TRASH: neither vanilla 0.7 nor any SkyWynn mod has a trash slot (searched) - nothing to block. Chests, Requip, vaults and the backpack
   section stay allowed. NOT covered (no PlayerRequest fires there, cancelling DropItemEvent$Drop would destroy the item): an engine
   add-or-drop into a FULL inventory (another mod's give, a backpack shrink, /inventory backpack) can put a lifelong tool on the ground -
   its owner picks it up again or uses /pickaxe.
   /pickaxe /hatchet /hoe /sickle: a new COMMON tool of that kind at your level, of the tier your skill level fits (FIX ROUND, Skyy G2
   "so lvl 20 mining you get a lvl 20 common iron pickaxe": the first ladder tier whose band holds your level, never below the tier you had;
   row lifelong.reclaimTier off = the tier you had. FIX ROUND 2: the row is OFF by default - on, a tool parked in a chest + /pickaxe skips
   every Anvil tier-up for free; off still gives Skyy's example to anyone whose lost pickaxe was Iron), only when your current one is nowhere in your inventory or Requip (a chest is not
   searched - accepted: the replacement goes once the original is back); lifelong.reclaimSec (600 s) between two. It is a replacement
   (lrp=1, lrpT = the tier it was given at): when the old one turns up again it becomes your lifelong tool again and the replacement
   disappears (the sweep) - UNLESS the replacement was tiered up or reforged (FIX ROUND: then it stays the lifelong tool for good; FIX
   ROUND 2: the old one is RETIRED (lrt=1, keeps its rolls, stays lifelong = never sold, breaks nothing, may be dropped) instead of turning
   plain - a plain rolled tool was a free second tool to sell; /lifelong on your retired one swaps the two any time). Every older lifelong
   stack of yours is retired the same way, except the one /lifelong re-picked away from (it was a plain tool before the migration: K.free).
   Another player's lifelong tool breaks NOTHING for you (FIX ROUND,
   GearLL.hit): handing yours over and typing /pickaxe gives no second working tool. Journal first (crash-safe, the harness crashes every step).
4. THE TIER GATE (GearToolHitSys, DamageBlockEvent): tool tier T (Crude 0 .. Onyxium 7) vs block tier M (ore Copper 1, Iron / Silver /
   Gold 2, Thorium 3, Cobalt 4, Adamantite 5, Mithril 6, Onyxium 7; logs by tree zone - Grove + orchard 1, Maple / Azure 2, Savanna 3,
   Northern 4, Wastes 5; crops by the spec 7.3 pairs): M <= T normal, M = T + 1 x gate.nextFactor (0.1 = Skyy's "10x hits"), M >= T + 2
   cancelled + a popup (FIX ROUND 2: Crude tools - the first hour, Oak logs / copper ore - use their own row gate.crudeFactor, default
   0.1 = G4 as well, so Skyy can soften only the first step). No pickaxe / hatchet in hand (bare hands, a weapon, the wrong tool) on ore / logs = refused (gate.bareHands, the
   Stop-Punching-Trees lock); stone / dirt / sand (M0) never gated. A family's TOP vanilla tool handles every block above it at full speed
   (vanilla hoes end at Thorium, sickles at Iron: a Thorium hoe farms Potatoes normally). FARMING: a crop one tier up gives no Fortune (only.farming lists
   the crops your tier covers + cactus), two up is refused when the hit fires a DamageBlockEvent; HALF XP one tier up needs SkyySkills to
   ask gear:fn:farmTier (Object[] { UUID, block id, held ITEM ID }; published now, read by nobody yet - UNVERIFIED / next SkyySkills round). The hoe's till AREA by tier is NOT built
   (vanilla Hoe_Till is a single-block ChangeBlock interaction; a 3x3..9x9 till needs our own block writes on 0.7 - probe first).
5. NO CRAFTING: CraftRecipeEvent$Pre refuses every bench / /craft recipe whose output is a pickaxe / hatchet / hoe / sickle
   (CraftingManager.craftItem fires it and stops on cancel - VERIFIED bytecode; SkyySacks /craft goes through craftItem); the Smithing Craft
   tab hides them. TIER UP on the Anvil (the 0.2.22 Upgrade core: rarity, lines, reforge name kept; materials inventory then bags) along
   lifelong.ladders: Crude / Wood -> Copper = 25 Copper Ingots (G1), then 1 / 1 / 2 / 2 Enchanted of the new tier (Iron, Thorium, Cobalt,
   Adamantite ingots for pickaxes; the key logs Maple, Gumboab, Redwood, Sallow for hatchets; the key crops Carrot, Cauliflower for hoes /
   sickles). Mithril / Onyxium steps wait for their Enchanted items. Only YOUR lifelong tool climbs a tool ladder, and only with the skill
   level the new tier starts at (Copper: your level.material start, e.g. Mining 5).
6. MIGRATION (once per profile, at the first join after 0.3.0, PROJECT-RULES 4 style: journal + run-once marker migrated=1, nothing
   rewritten twice): per kind the BEST tool in the inventory (highest rarity, then level, then most lines; identified, single) becomes the
   lifelong one keeping its rarity, rolls and reforge name; no tool of a kind = a fresh Crude Common one (storage first; no room = it waits
   and says so). Everything else stays a plain tool. /lifelong (once per kind, lifelong.repickDays 7 days after the migration): make the
   tool in your hand the lifelong one instead (a tool that was in a chest during the migration). NEW PROFILES get their four Common tools
   the same way at their first join - so NO SkyyIslands change (a starter-chest kit would hand out four more on every /island reset).
   No config row changes default (every new row absent = its default): no one-time setting migration is needed. FIX ROUND: the migration
   writes the registry at most 5 times (one journal per marked / given kind + one save; commits ride along), each LL-MARK line carries the
   stack as it was ("undo: <json>"), and a lifelong-kind tool sitting in Requip is named once in chat (pick it with /lifelong).
   LEVEL SYNC (FIX ROUND): GearTool.held (once a second) flags a held lifelong tool whose [Lv N] lags the skill; GearHandSys hands it to the
   stamp task, whose sweep rewrites it. Tools in Requip / the Void / a chest show the new level once they are back in the inventory (their
   hits always use the live level). A cancelled drop from an open chest window marks that window changed (re-sent to the client).
FIX ROUND 2: an unreadable registry is read again after 30 s (was: bad until restart); a failed registry write WARNs once per 30 s and the
every-scan sweep waits 30 s (no WARN / fsync storm); the migration notice also points at chests / the Void / the Vault; LL-MARK logs the old
level + coin-bought levels (lvU) and says so in chat when the level drops; gear:fn:lifelong also answers a bare UUID with the number of kinds
owned (SkyyQuests' tutorial) and quest:caller:gearlife is published.
ROLLBACK: 0.3.0 -> 0.2.26 is safe for items (the extra document fields are ignored; lifelong tools work as plain tools again, tools can be
crafted again). Back on 0.3.0 the registry still holds the uids. FLOOR once deployed: rolling back lets players drop / sell lifelong tools.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.26.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.0.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.2.26"' in s and "GENERATED by tools/gear_0_2_26_patch.py" in s and "0.3.0" not in s[:400], "not the generated 0.2.26 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    """insert text right before the (unique) anchor"""
    rep(anchor, text + anchor)


def after(anchor, text):
    """insert text right after the (unique) anchor"""
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.2.26":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.2.26" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.2.26 - build script (javassist via jpype). GENERATED by tools/gear_0_2_26_patch.py from the LIVE 0.2.25 (itself GENERATED by
tools/gear_0_2_25_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.2.26.py -> SkyyGear/SkyyGear-0.2.26.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.2.26.py --dir <empty folder inside tools/dev/scratch/>
''', '''"""SkyyGear 0.3.0 - build script (javassist via jpype). GENERATED by tools/gear_0_3_0_patch.py from the LIVE 0.2.26 (itself GENERATED by
tools/gear_0_2_26_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.0.py -> SkyyGear/SkyyGear-0.3.0.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.0.py

0.3.0 = LIFELONG TOOLS + THE TIER GATE (phase 3 of research/Gathering-Shards-Spec.md + Skyy's 2026-10-13 answers; notes:
tools/gear_0_3_0_patch.py): one pickaxe, hatchet, hoe and sickle per profile for life (the best one you own becomes it, or a Crude Common
one), its level = your skill level capped by its tier, 1 Upgrade Point per skill level (Speed / Fortune / Wisdom; Vein Mine / Tree Feller
once SkyyTrees reads them; reset for coins, more each time) on the new Tools tab (/toolpoints); never dropped, sold or salvaged; no
crafting - tier up on the Anvil (25 Copper Ingots, then Enchanted materials); /pickaxe /hatchet /hoe /sickle replace a lost one; /lifelong
re-picks once; the tier gate: own tier normal, one up x0.1 (gate.nextFactor), two up refused, no tool = no logs / ore.

--- 0.2.26 notes ---

''')
rep('VERSION = "0.2.26"\n', 'VERSION = "0.3.0"\n')

# ================================================================================================================ settings (13 rows, category lifelong)
after('''ID_TOOL_DEF = "Skyy_Accessory_Appraisal_T1,Skyy_Accessory_Appraisal_T2,Skyy_Accessory_Appraisal_T3"
assert len(ID_TOOL_DEF) < 500 and all(_c.isalnum() or _c in "_," for _c in ID_TOOL_DEF)
''', '''# 0.3.0 LIFELONG TOOLS: the tier-up ladders on the Anvil (Skyy 2026-10-13 G1 "25 Copper Ingots (Recommended)"; 2026-10-11 "it costs a
# enchanted iron ingot to upgrade copper to iron, and so on"; research/Gathering-Shards-Spec.md 6.1): Crude / Wood -> Copper = 25 Copper
# Ingots, then 1 / 1 / 2 / 2 Enchanted of the new tier (hatchets: the zone's key log, hoes / sickles: the key crop). Mithril / Onyxium wait
# for their Enchanted items (tools/skyyench.py has none yet); vanilla hoes end at Thorium, sickles at Iron.
import skyyench as ENCH
_LLB = "Ingredient_Bar_Copper*25"


def _lle(k, n):
    assert k in ENCH.KEYS, "no Enchanted " + k
    return "%s%s*%d" % (ENCH.PREFIX, k, n)


LL_LADDER_ROWS = [
    "Tool_Pickaxe_Crude>Tool_Pickaxe_Copper(%s)>Tool_Pickaxe_Iron(%s)>Tool_Pickaxe_Thorium(%s)>Tool_Pickaxe_Cobalt(%s)>Tool_Pickaxe_Adamantite(%s)"
    % (_LLB, _lle("Iron", 1), _lle("Thorium", 1), _lle("Cobalt", 2), _lle("Adamantite", 2)),
    "Tool_Pickaxe_Wood>Tool_Pickaxe_Copper(%s)" % _LLB,
    "Tool_Pickaxe_Scrap>Tool_Pickaxe_Iron(%s)" % _lle("Iron", 1),
    "Tool_Hatchet_Crude>Tool_Hatchet_Copper(%s)>Tool_Hatchet_Iron(%s)>Tool_Hatchet_Thorium(%s)>Tool_Hatchet_Cobalt(%s)>Tool_Hatchet_Adamantite(%s)"
    % (_LLB, _lle("Maple", 1), _lle("Gumboab", 1), _lle("Redwood", 2), _lle("Sallow", 2)),
    "Tool_Hatchet_Wood>Tool_Hatchet_Copper(%s)" % _LLB,
    "Tool_Hoe_Crude>Tool_Hoe_Copper(%s)>Tool_Hoe_Iron(%s)>Tool_Hoe_Thorium(%s)" % (_LLB, _lle("Carrot", 1), _lle("Cauliflower", 1)),
    "Tool_Sickle_Crude>Tool_Sickle_Copper(%s)>Tool_Sickle_Iron(%s)" % (_LLB, _lle("Carrot", 1)),
]
LL_LADDER_DEF = ",".join(LL_LADDER_ROWS)
assert len(LL_LADDER_DEF) < 2000 and all(32 <= ord(_c) < 127 for _c in LL_LADDER_DEF)
for _i in re.findall(r"(Tool_[A-Za-z]+_[A-Za-z]+)", LL_LADDER_DEF) + ["Ingredient_Bar_Copper"]:
    assert _i in AZ_ITEMS, "lifelong.ladders names %s - not in Assets.zip" % _i
''')
rep('''            ("upgrade", "Upgrades"),             # 0.2.22
            ("smithing", "Smithing")]            # 0.2.23''', '''            ("upgrade", "Upgrades"),             # 0.2.22
            ("smithing", "Smithing"),            # 0.2.23
            ("lifelong", "Lifelong tools")]      # 0.3.0''')
after('''    ("anvil.appraisalIds", "Appraisal Tool accessory ids", "smithing", "text", ID_TOOL_DEF, "0", "500", "", "", "live,adv",
     "Accessory ids that count as an Appraisal Tool, lowest tier first, joined by commas.",
     "field:GearCfg.ID_TOOLS;check=GearCfg.checkIdTools"),
''', '''    # 0.3.0 LIFELONG TOOLS + THE TIER GATE (Skyy 2026-10-12 / 2026-10-13, docs/answered/gear.md; research/Gathering-Shards-Spec.md phase 3)
    ("part.lifelong", "Lifelong tools", "lifelong", "bool", "true", "", "", "", "", "live,part,danger",
     "One pickaxe, hatchet, hoe and sickle per player: level with the skill, upgrade only. Off = plain.", "field:GearCfg.LL_ON"),
    ("lifelong.noCraft", "Tools cannot be crafted", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "No bench or /craft recipe makes a pickaxe, hatchet, hoe or sickle (shovels still craft).", "field:GearCfg.LL_NOCRAFT"),
    ("lifelong.noDrop", "Lifelong tools cannot be dropped", "lifelong", "bool", "true", "", "", "", "", "live",
     "Drop key / drag out do nothing on a lifelong tool (chests and Requip still take it).", "field:GearCfg.LL_NODROP"),
    ("lifelong.ladders", "Tool tier-up costs", "lifelong", "text", LL_LADDER_DEF, "0", "2000", "", "", "live,danger",
     "Lifelong tool tiers on the Anvil, like upgrade.ladders: A>B(Id*25), ladders joined by commas.",
     "field:GearCfg.LL_LADDERS;check=GearUp.checkLadders"),
    ("lifelong.reclaimSec", "Wait between /pickaxe uses", "lifelong", "int", "600", "0", "86400", "", "s", "live",
     "Seconds before /pickaxe, /hatchet, /hoe or /sickle can give that kind of tool again.", "field:GearCfg.LL_RECLAIM"),
    # fix round (Skyy G2 "so lvl 20 mining you get a lvl 20 common iron pickaxe"): /pickaxe gives the tier your skill level fits
    # fix round 2 (safety critic 1): default OFF - on, a tool parked in a chest + /pickaxe skips every Anvil tier-up for free
    ("lifelong.reclaimTier", "/pickaxe gives your skill's tier", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "On: a lost tool comes back at the tier your skill fits (free tier-ups!). Off: the tier it had.", "field:GearCfg.LL_RTIER"),
    ("lifelong.repickDays", "Days to re-pick with /lifelong", "lifelong", "int", "7", "0", "365", "", "", "live",
     "Days after a player's first 0.3.0 join when /lifelong may re-pick a tool (once per kind).", "field:GearCfg.LL_REPICK"),
    ("lifelong.perkSpeed", "Speed per perk level", "lifelong", "dec", "2", "0", "50", "", "%", "live,danger",
     "Each Speed level: this % more Mining / Chopping Power." + PH, "field:GearCfg.LL_PSPD"),
    ("lifelong.perkFortune", "Fortune per perk level", "lifelong", "dec", "1", "0", "25", "", "", "live,danger",
     "Each Fortune level adds this much Fortune (tool cap applies)." + PH, "field:GearCfg.LL_PFORT"),
    ("lifelong.perkWisdom", "Wisdom per perk level", "lifelong", "dec", "1", "0", "25", "", "%", "live,danger",
     "Each Wisdom level: this % more skill XP (tool cap applies)." + PH, "field:GearCfg.LL_PWIS"),
    ("lifelong.resetCoins", "Point reset coins per point", "lifelong", "int", "5000", "0", "10000000", "", "coins", "live,danger",
     "A points reset costs this x spent points x (resets so far + 1)." + PH, "field:GearCfg.LL_RESET"),
    ("gate.on", "Tool tier gate", "lifelong", "bool", "true", "", "", "", "", "live,part,danger",
     "Same tier normal, one tier up slow, two up refused. Off = every tool breaks every block.", "field:GearCfg.GATE_ON"),
    ("gate.nextFactor", "One tier up speed", "lifelong", "dec", "0.1", "0.01", "1", "", "x", "live,danger",
     "A block one tier above your tool breaks at this speed (0.1 = 10x the hits).", "field:GearCfg.GATE_NEXT"),
    # fix round 2 (design critic 1): the first hour (Crude tools on Oak logs / copper ore) gets its own knob; default = Skyy's G4 0.1
    ("gate.crudeFactor", "One tier up speed, Crude tools", "lifelong", "dec", "0.1", "0.01", "1", "", "x", "live,danger",
     "Same, for Crude tools on Oak logs / copper ore (the first hour). 0.25 = 4x the hits.", "field:GearCfg.GATE_NEXT0"),
    ("gate.bareHands", "No tool, no logs or ore", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "Logs need a hatchet and ore a pickaxe; bare hands and other items are refused.", "field:GearCfg.GATE_BARE"),
''')
rep('''           # fix round: the Appraisal Tool rule (on today = nobody can identify: the tool items + the Appraiser NPC are not made yet)
           "anvil.appraisal"}''', '''           # fix round: the Appraisal Tool rule (on today = nobody can identify: the tool items + the Appraiser NPC are not made yet)
           "anvil.appraisal",
           # 0.3.0: lifelong tools + the tier gate (item supply, gathering speed, Fortune, coins = economy) - confirm in Server Setup
           "part.lifelong", "lifelong.noCraft", "lifelong.ladders", "lifelong.perkSpeed", "lifelong.perkFortune", "lifelong.perkWisdom",
           "lifelong.resetCoins", "gate.on", "gate.nextFactor", "gate.bareHands", "lifelong.reclaimTier", "gate.crudeFactor"}''')
after('''ANV_ROWK = ["part.anvil", "anvil.appraisal", "anvil.appraisalIds"]
''', '''LL_HEAD = "# ---- lifelong tools + the tool tier gate (SkyyGear 0.3.0) ----"
LL_ROWK = ["part.lifelong", "lifelong.noCraft", "lifelong.noDrop", "lifelong.ladders", "lifelong.reclaimSec", "lifelong.reclaimTier", "lifelong.repickDays",
           "lifelong.perkSpeed", "lifelong.perkFortune", "lifelong.perkWisdom", "lifelong.resetCoins", "gate.on", "gate.nextFactor",
           "gate.crudeFactor", "gate.bareHands"]
assert all(32 <= ord(_c) < 127 for _c in LL_HEAD) and "=" not in LL_HEAD
''')
after('''    L += ["", ANV_HEAD]         # 0.2.26: the Anvil rows (no one-time update adds them; absent = the default)
    for k in ANV_ROWK:
        scal(k)
''', '''    L += ["", LL_HEAD]          # 0.3.0: the lifelong rows (no one-time update adds them; absent = the default)
    for k in LL_ROWK:
        scal(k)
''')
rep('''              ("ANVIL_ON", "boolean", "true"), ("ID_TOOL", "boolean", "false"), ("ID_TOOLS", "String", jstr(ID_TOOL_DEF))]''',
    '''              ("ANVIL_ON", "boolean", "true"), ("ID_TOOL", "boolean", "false"), ("ID_TOOLS", "String", jstr(ID_TOOL_DEF)),
              # 0.3.0 lifelong tools + the tier gate
              ("LL_ON", "boolean", "true"), ("LL_NOCRAFT", "boolean", "true"), ("LL_NODROP", "boolean", "true"),
              ("LL_LADDERS", "String", jstr(LL_LADDER_DEF)), ("LL_RECLAIM", "int", "600"), ("LL_RTIER", "boolean", "false"), ("LL_REPICK", "int", "7"),
              ("LL_PSPD", "double", "2.0"), ("LL_PFORT", "double", "1.0"), ("LL_PWIS", "double", "1.0"), ("LL_RESET", "int", "5000"),
              ("GATE_ON", "boolean", "true"), ("GATE_NEXT", "double", "0.1"), ("GATE_NEXT0", "double", "0.1"), ("GATE_BARE", "boolean", "true")]''')
after('''  ID_TOOLS = ptext(p, "anvil.appraisalIds", "@IDTOOLDEF@").trim();
''', '''  // 0.3.0 lifelong tools + the tier gate (ladders checked where they are used - GearUp.tab skips a bad part with one WARN)
  LL_ON = pbool(p, "part.lifelong", true);
  LL_NOCRAFT = pbool(p, "lifelong.noCraft", true);
  LL_NODROP = pbool(p, "lifelong.noDrop", true);
  LL_LADDERS = ptext(p, "lifelong.ladders", "@LLLADDEF@").trim();
  LL_RECLAIM = (int) plong(p, "lifelong.reclaimSec", 600L, 0L, 86400L);
  LL_RTIER = pbool(p, "lifelong.reclaimTier", false);
  LL_REPICK = (int) plong(p, "lifelong.repickDays", 7L, 0L, 365L);
  LL_PSPD = pdec(p, "lifelong.perkSpeed", 2.0, 0.0, 50.0);
  LL_PFORT = pdec(p, "lifelong.perkFortune", 1.0, 0.0, 25.0);
  LL_PWIS = pdec(p, "lifelong.perkWisdom", 1.0, 0.0, 25.0);
  LL_RESET = (int) plong(p, "lifelong.resetCoins", 5000L, 0L, 10000000L);
  GATE_ON = pbool(p, "gate.on", true);
  GATE_NEXT = pdec(p, "gate.nextFactor", 0.1, 0.01, 1.0);
  GATE_NEXT0 = pdec(p, "gate.crudeFactor", 0.1, 0.01, 1.0);
  GATE_BARE = pbool(p, "gate.bareHands", true);
''')
rep('''.replace("@SMITHARM@", SMITH_ARM_DEF).replace("@IDTOOLDEF@", ID_TOOL_DEF))''',
    '''.replace("@SMITHARM@", SMITH_ARM_DEF).replace("@IDTOOLDEF@", ID_TOOL_DEF).replace("@LLLADDEF@", LL_LADDER_DEF))''')

# ================================================================================================================ GearLL (before GearTool)
LIFE_A = r'''
# ####################################################################################################################################
# 0.3.0 LIFELONG TOOLS + THE TIER GATE, READ SIDE (tools/gear_0_3_0_patch.py header). GearLL sits right before GearTool: GearTool.gate /
# stats / held / lines, GearToolHitSys, GearCraftPreSys, GearWall, GearForge.lvlInfo, GearMerge.why and GearUp call it. It holds the kinds,
# the per-profile registry (Skyy_SkyyGear/lifelong/<pkey>.properties: read once per join on the scheduler, written only on rare events
# with tmp + fsync + atomic move and no sleep-retry), the level rule, the Upgrade Points + perks and the block tier gate. The write side
# (sweep, migration, /pickaxe, perks, the Tools page) is GearLife further down; joinHook / sweepHook here get their bodies there.
# ####################################################################################################################################
LL_KIND = ["pickaxe", "hatchet", "hoe", "sickle"]
LL_KNAME = ["Pickaxe", "Hatchet", "Hoe", "Sickle"]
LL_KFAM = [1, 3, 4, 5]                              # GearTool.fam: 1 pickaxe, 3 hatchet, 4 hoe, 5 sickle (2 = the shovel stays plain)
LL_KSKILL = ["Mining", "Foraging", "Farming", "Farming"]
LL_KCRUDE = ["Tool_%s_Crude" % _n for _n in LL_KNAME]
assert all(_i in AZ_ITEMS for _i in LL_KCRUDE)
LL_TNAME = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
assert [_t for _w, _t in TOOL_TIERS if _w in LL_TNAME] == list(range(8)), "TOOL_TIERS lost a tier word"
# the top vanilla tier of each GearTool family (index = fam; 6 = multitool): that tool handles every block above it at full speed
LL_FAMMAX = [0] * 7
for _i in _TOOL_AZ_IDS:
    _f = [k + 1 for k, p in enumerate(TOOL_FAMS) if _i.startswith(p)][0]
    LL_FAMMAX[_f] = max(LL_FAMMAX[_f], _tool_tier(_i))
LL_FAMMAX[6] = 7
assert LL_FAMMAX[1] == 7 and LL_FAMMAX[3] == 7 and LL_FAMMAX[4] == 3 and LL_FAMMAX[5] == 2, "vanilla tool tiers changed: %s" % LL_FAMMAX
# BLOCK TIERS (research/Gathering-Shards-Spec.md 7.1-7.3; Assets.zip ids asserted): ore Ore_<Metal>*, logs Wood_<Tree>_Trunk*, crops
# Plant_Crop_<Crop>_*; any other block (stone, dirt, sand, planks, an ore / tree / crop not listed) is never gated
LL_ORE = [("Copper", 1), ("Iron", 2), ("Silver", 2), ("Gold", 2), ("Thorium", 3), ("Cobalt", 4), ("Adamantite", 5), ("Mithril", 6), ("Onyxium", 7)]
for _w, _m in LL_ORE:
    assert ("Ore_" + _w) in AZ_ITEMS, "no vanilla ore Ore_" + _w
_WOOD_SPEC = [("Oak", 1), ("Birch", 1), ("Beech", 1), ("Ash", 1), ("Aspen", 1), ("Apple", 1), ("Amber", 1), ("Wisteria", 1), ("Stormbark", 1),
              ("Windwillow", 1), ("Maple", 2), ("Azure", 2), ("Gumboab", 3), ("Dry", 3), ("Bottletree", 3), ("Palo", 3), ("Redwood", 4), ("Fir", 4),
              ("Cedar", 4), ("Poisoned", 4), ("Spiral", 4), ("Sallow", 5), ("Burnt", 5), ("Petrified", 5), ("Bamboo", 5), ("Camphor", 5),
              ("Banyan", 5), ("Jungle", 5), ("Fig", 5), ("Fire", 5), ("Crystal", 5)]
LL_WOOD = [(_w, _m) for _w, _m in _WOOD_SPEC if [i for i in AZ_ITEMS if i.startswith("Wood_" + _w + "_") and "_Trunk" in i]]
LL_WOOD_GONE = [_w for _w, _m in _WOOD_SPEC if (_w, _m) not in LL_WOOD]
assert all(_k in dict(LL_WOOD) for _k in ("Oak", "Maple", "Gumboab", "Redwood", "Sallow")), "a key log has no trunk: %s" % LL_WOOD_GONE
_CROP_SPEC = [("Wheat", 1), ("Lettuce", 1), ("Carrot", 2), ("Corn", 2), ("Cauliflower", 3), ("Turnip", 3), ("Pumpkin", 4), ("Aubergine", 4),
              ("Tomato", 5), ("Chilli", 5), ("Cotton", 6), ("Rice", 6), ("Potato", 7), ("Onion", 7)]
_CROP_IDS = [i for i in AZ_ITEMS if i.startswith("Plant_Crop_")]
LL_CROP = [(_w, _m) for _w, _m in _CROP_SPEC if [i for i in _CROP_IDS if i.startswith("Plant_Crop_" + _w + "_")]]
LL_CROP_GONE = [_w for _w, _m in _CROP_SPEC if (_w, _m) not in LL_CROP]
assert all(_k in dict(LL_CROP) for _k in ("Wheat", "Carrot", "Cauliflower", "Pumpkin", "Tomato", "Cotton", "Potato")), "a key crop is missing"
# crops outside the tier table (berries, mushrooms, health / mana plants ...): never gated, Fortune always counts on them
LL_CROP_FREE = sorted(set(i.split("_")[2] for i in _CROP_IDS if len(i.split("_")) > 2) - set(_w for _w, _m in _CROP_SPEC))
# fix round (engine critic 5): SkyySkills also counts Plant_Cactus as Farming (prefix.Plant_Cactus=Farming:2) and matches only.farming by
# "id contains" - cactus is no tier-table crop, so a hoe / sickle's Fortune keeps counting on it
assert [i for i in AZ_ITEMS if i.startswith("Plant_Cactus")], "no Plant_Cactus in Assets.zip"
LL_CROP_FREE = LL_CROP_FREE + ["Plant_Cactus"]
print("0.3.0 tier gate: %d ores, %d logs (no trunk: %s), %d crops (missing: %s), %d free crop words; family tops %s"
      % (len(LL_ORE), len(LL_WOOD), LL_WOOD_GONE, len(LL_CROP), LL_CROP_GONE, len(LL_CROP_FREE), LL_FAMMAX))
# UPGRADE POINTS (Skyy 2026-10-13 "1 point per skill level"; perks = research/Gathering-Shards-Spec.md 6.3, the ones built now): key,
# name, max level, kinds bitmask (1 pickaxe, 2 hatchet, 4 hoe, 8 sickle), cost per level (1-based), tool tier needed per level
LL_PERKS = [("spd", "Speed", 10, 1 | 2, [1] * 10, [0] * 10),
            ("fort", "Fortune", 10, 15, [1] * 10, [0] * 10),
            ("wis", "Wisdom", 5, 15, [2] * 5, [2] * 5),
            ("vein", "Vein Mine", 3, 1, [3, 5, 8], [2, 3, 4]),
            ("fell", "Tree Feller", 3, 2, [3, 5, 8], [2, 3, 4])]
for _p in LL_PERKS:
    assert len(_p[4]) == _p[2] == len(_p[5])
gll = mk("GearLL")
LIFE_CLASSES = [gll]
for _c, _m in (("com.hypixel.hytale.server.core.inventory.Inventory", "usingToolsItem"), ("com.hypixel.hytale.server.core.inventory.Inventory", "getToolsItem")):
    B.probe(pool, _c, _m)
F(gll, "public static final String[] KIND = %s;" % jarr(LL_KIND))
F(gll, "public static final String[] KNAME = %s;" % jarr(LL_KNAME))
F(gll, "public static final int[] KFAM = %s;" % jints(LL_KFAM))
F(gll, "public static final String[] KSKILL = %s;" % jarr(LL_KSKILL))
F(gll, "public static final String[] KCRUDE = %s;" % jarr(LL_KCRUDE))
# fix round: each kind's main tier ladder (Crude first) = the tiers /pickaxe may give at your skill level (lifelong.reclaimTier)
LL_KLAD = []
for _n in LL_KNAME:
    _row = [_r for _r in LL_LADDER_ROWS if _r.startswith("Tool_%s_Crude>" % _n)]
    assert len(_row) == 1, "no main ladder for " + _n
    LL_KLAD.append(",".join(re.findall(r"(Tool_[A-Za-z]+_[A-Za-z]+)", _row[0])))
assert LL_KLAD[0].endswith("Tool_Pickaxe_Adamantite") and LL_KLAD[2].endswith("Tool_Hoe_Thorium") and LL_KLAD[3].endswith("Tool_Sickle_Iron")
F(gll, "public static final String[] KLAD = %s;" % jarr(LL_KLAD))
F(gll, "public static final java.util.concurrent.ConcurrentHashMap RESYNC = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Boolean (held tool's level is stale)
F(gll, "public static final String[] TNAME = %s;" % jarr(LL_TNAME))
F(gll, "public static final String[] TW = %s;" % jarr([_w for _w, _t in TOOL_TIERS]))
F(gll, "public static final int[] TN = %s;" % jints([_t for _w, _t in TOOL_TIERS]))
F(gll, "public static final int[] FAMMAX = %s;" % jints(LL_FAMMAX))
F(gll, "public static final String[] ORE_W = %s;" % jarr([_w for _w, _m in LL_ORE]))
F(gll, "public static final int[] ORE_M = %s;" % jints([_m for _w, _m in LL_ORE]))
F(gll, "public static final String[] WOOD_W = %s;" % jarr([_w for _w, _m in LL_WOOD]))
F(gll, "public static final int[] WOOD_M = %s;" % jints([_m for _w, _m in LL_WOOD]))
F(gll, "public static final String[] CROP_W = %s;" % jarr([_w for _w, _m in LL_CROP]))
F(gll, "public static final int[] CROP_M = %s;" % jints([_m for _w, _m in LL_CROP]))
F(gll, "public static final String CROP_FREE = %s;" % jstr(",".join(LL_CROP_FREE)))
F(gll, "public static final String[] PK = %s;" % jarr([_p[0] for _p in LL_PERKS]))
F(gll, "public static final String[] PKN = %s;" % jarr([_p[1] for _p in LL_PERKS]))
F(gll, "public static final int[] PKMAX = %s;" % jints([_p[2] for _p in LL_PERKS]))
F(gll, "public static final int[] PKMASK = %s;" % jints([_p[3] for _p in LL_PERKS]))
# cost / tier need per level, flat: index = perk x 10 + (level - 1) (javassist: no multi-dimensional initializers)
assert all(_p[2] <= 10 for _p in LL_PERKS)
F(gll, "public static final int[] PKCOST = %s;" % jints(sum([(_p[4] + [0] * 10)[:10] for _p in LL_PERKS], [])))
F(gll, "public static final int[] PKNEED = %s;" % jints(sum([(_p[5] + [99] * 10)[:10] for _p in LL_PERKS], [])))
# the registries: profile key -> java.util.Properties (Hashtable, thread safe); "_bad" = 1 when the file could not be read (never written)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap REG = new java.util.concurrent.ConcurrentHashMap();")
F(gll, "public static final java.util.concurrent.ConcurrentHashMap SLOW = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long (slow popup)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap ONLY = new java.util.concurrent.ConcurrentHashMap();")   # "f:t" -> String
# counters: 0 hits refused, 1 hits slowed, 2 hits refused bare-handed, 3 crafts refused, 4 drops refused, 5 registry writes, 6 write fails,
# 7 hits refused with another player's lifelong tool, 8 (fix round 2) hits refused with your own RETIRED / stale lifelong tool
F(gll, "public static final long[] N = new long[9];")
# fix round 2 (safety critic 3 / 4): profile key -> Long: the last failed registry READ (re-read after 30 s - never cached as bad for the
# whole uptime) / the last failed registry WRITE (non-forced sweeps wait 30 s - no WARN + fsync storm)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap BADAT = new java.util.concurrent.ConcurrentHashMap();")
F(gll, "public static final java.util.concurrent.ConcurrentHashMap FAILAT = new java.util.concurrent.ConcurrentHashMap();")
F(gll, "public static volatile boolean FAIL_SAVE = false;")    # harness only: the next registry writes fail
F(gll, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long (last sweep)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();")   # "uuid:key" -> Long (chat lines)
M(gll, r"""
public static int kOfFam(int f) {
  for (int i = 0; i < KFAM.length; i++) if (KFAM[i] == f) return i;
  return -1;
}""")
# the kind of an item id (-1 = not a lifelong kind: shovels, multitools, hammers, Skyy_ items ...)
M(gll, "public static int kOf(String id) { return id == null ? -1 : kOfFam(@PKG@.GearData.toolFam(id)); }")
M(gll, r"""
public static int kOfName(String n) {
  if (n == null) return -1;
  for (int i = 0; i < KIND.length; i++) if (KIND[i].equalsIgnoreCase(n.trim())) return i;
  return -1;
}""")
M(gll, "public static boolean isLL(@BD@ d) { return d != null && @PKG@.GearData.num(d, \"ll\", 0) == 1; }")
M(gll, "public static String uid(@BD@ d) { return @PKG@.GearData.str(d, \"lu\", \"\"); }")
M(gll, "public static String owner(@BD@ d) { return @PKG@.GearData.str(d, \"lo\", \"\"); }")
M(gll, "public static boolean isRp(@BD@ d) { return @PKG@.GearData.num(d, \"lrp\", 0) == 1; }")
# fix round 2 (safety critic 2): a RETIRED lifelong tool (lrt=1: an older one of yours that turned up after its replacement was upgraded, or the
# one you swapped away with /lifelong): still yours + lifelong (never sold), but it breaks nothing until /lifelong swaps it back
M(gll, "public static boolean isRt(@BD@ d) { return d != null && @PKG@.GearData.num(d, \"lrt\", 0) == 1; }")
M(gll, r"""
public static boolean llStack(String id, @BD@ md) {
  if (id == null || md == null) return false;
  try { return isLL(@PKG@.GearData.gearDoc(md)); } catch (Throwable t) { return false; }
}""")
# true = d is a lifelong tool of the player's ACTIVE profile (the switch part.lifelong on)
M(gll, r"""
public static boolean mine(java.util.UUID u, @BD@ d) {
  if (!@PKG@.GearCfg.LL_ON || u == null || !isLL(d) || isRt(d)) return false;          // fix round 2: a retired one is no working tool
  return @PKG@.Gear.pkey(u).equals(owner(d));
}""")
# the material tier of an item id (GearTool.tier's words; unknown = 0)
M(gll, r"""
public static int tier(String id) {
  if (id == null) return 0;
  String[] w = id.split("_");
  for (int i = 2; i < w.length; i++) {
    for (int j = 0; j < TW.length; j++) if (TW[j].equalsIgnoreCase(w[i])) return TN[j];
  }
  return 0;
}""")
M(gll, "public static String tname(int t) { return t >= 0 && t < TNAME.length ? TNAME[t] : String.valueOf(t); }")
M(gll, r"""
public static String an(String w) {
  if (w == null || w.length() == 0) return "a";
  return ("AEIOUaeiou".indexOf(w.charAt(0)) >= 0 ? "an " : "a ") + w;
}""")
M(gll, "public static int cap(String id) { return @PKG@.GearLevel.band(id)[1]; }")
# the gate skill level (-2 = no SkyySkills, -1 unknown skill, else the level)
M(gll, r"""
public static int skill(java.util.UUID u, int k) {
  if (u == null || k < 0 || k >= KSKILL.length) return -2;
  return @PKG@.GearGate.have(u, KSKILL[k]);
}""")
# THE LEVEL RULE (Skyy 2026-10-13 "tools dont have XP they just match your skill level"): min(skill, the tier's band top), at least 1;
# -1 = the skill is unknown (no SkyySkills): the caller keeps the document's level
M(gll, r"""
public static int levelFor(java.util.UUID u, String id) {
  int k = kOf(id);
  if (k < 0) return -1;
  int h = skill(u, k);
  if (h == -2) return -1;
  if (h < 0) h = 0;
  int f = @PKG@.GearLevel.floor(h);
  int c = cap(id);
  int lv = f < c ? f : c;
  return lv < 1 ? 1 : lv;
}""")
# fix round (Skyy G2 "so lvl 20 mining you get a lvl 20 common iron pickaxe"): the tier /pickaxe gives = the FIRST tier on the kind's ladder
# whose level band holds your skill level (so the tool is at your level: Mining 20 -> Iron 15-23), else the highest one you have the level
# for; never below the tier you had (had = the registry's id). No SkyySkills = the tier you had.
M(gll, r"""
public static String tierFor(java.util.UUID u, int k, String had) {
  if (k < 0 || k >= KLAD.length) return had;
  int h = skill(u, k);
  if (h == -2) return had;
  if (h < 1) h = 1;
  int f = @PKG@.GearLevel.floor(h);
  String[] ids = KLAD[k].split(",");
  String hi = null;
  String fit = null;
  for (int i = 0; i < ids.length; i++) {
    if (@PKG@.Gear.item(ids[i]) == null) continue;
    int[] b = @PKG@.GearLevel.band(ids[i]);
    if (b[0] > f && i > 0) continue;
    hi = ids[i];
    if (fit == null && f <= b[1]) fit = ids[i];
  }
  String r = fit != null ? fit : (hi != null ? hi : KCRUDE[k]);
  if (had != null && kOf(had) == k && tier(had) > tier(r)) return had;
  return r;
}""")
# fix round (critic A2): a /pickaxe replacement the player put work into (tiered up on the Anvil past the tier it was given at - lrpT - or
# reforged) is never removed or thrown away when the original turns up
M(gll, r"""
public static boolean invested(String id, @BD@ d) {
  if (!isRp(d)) return false;
  int t = tier(id);
  return t > @PKG@.GearData.num(d, "lrpT", t) || @PKG@.GearData.num(d, "rfN", 0) > 0;
}""")
# fix round (engine critic 2): the held-tool recompute (GearTool.held, once a second) notices a lifelong tool whose document level lags the
# skill (a level-up) - GearHandSys then queues the stamp task, whose sweep rewrites "[Lv N]" (no wait for the next inventory change)
M(gll, r"""
public static void lvlWatch(java.util.UUID u, @IS@ s) {
  try {
    if (!@PKG@.GearCfg.LL_ON || u == null || s == null || s.isEmpty() || kOf(s.getItemId()) < 0) return;
    @BD@ d = @PKG@.GearData.gearDoc(s.getMetadata());
    if (!mine(u, d)) return;
    int lv = levelFor(u, s.getItemId());
    if (lv >= 1 && @PKG@.GearData.num(d, "lvl", -1) != lv) RESYNC.put(u, Boolean.TRUE);
  } catch (Throwable t) { }
}""")
M(gll, "public static String newUid() { return java.util.UUID.randomUUID().toString().replace(\"-\", \"\").substring(0, 16); }")
# ---- the registry
M(gll, r"""
public static java.nio.file.Path file(String pk) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pk == null || pk.length() == 0) return null;
  return d.resolve("lifelong").resolve(pk.replace('/', '_').replace('\\', '_').replace(':', '_').replace('.', '_') + ".properties");
}""")
M(gll, r"""
public static java.util.Properties reg(String pk) {
  String k = pk == null ? "" : pk;
  Object o = REG.get(k);
  if (o instanceof java.util.Properties) return (java.util.Properties) o;
  // fix round 2 (safety critic 3): an unreadable file is NOT cached - it is read again 30 s later (a brief antivirus / backup lock heals)
  long now = System.currentTimeMillis();
  Object ba = BADAT.get(k);
  if (ba instanceof Long && now >= ((Long) ba).longValue() && now - ((Long) ba).longValue() < 30000L) {
    java.util.Properties bp = new java.util.Properties();
    bp.setProperty("_bad", "1");
    return bp;
  }
  java.util.Properties p = new java.util.Properties();
  try {
    java.nio.file.Path f = file(k);
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) p = @PKG@.GearCfg.read(f);
  } catch (Throwable t) {
    p = new java.util.Properties();
    p.setProperty("_bad", "1");
    BADAT.put(k, Long.valueOf(now));
    @PKG@.Gear.warn("lifelong/" + k + ".properties could not be read (" + t + ") - that profile's lifelong tools are left alone; read again in 30 s");
    return p;
  }
  BADAT.remove(k);
  Object prev = REG.putIfAbsent(k, p);
  return prev instanceof java.util.Properties ? (java.util.Properties) prev : p;
}""")
M(gll, "public static boolean bad(java.util.Properties p) { return p == null || \"1\".equals(p.getProperty(\"_bad\")); }")
# the scheduler-side read at join (GearRefreshTask's first hop): the world thread later finds the registry in memory
M(gll, r"""
public static void prefetch(java.util.UUID u) {
  try { if (@PKG@.GearCfg.LL_ON && u != null) reg(@PKG@.Gear.pkey(u)); } catch (Throwable t) { }
}""")
M(gll, "public static String get(java.util.Properties p, String k) { return p == null ? null : p.getProperty(k); }")
M(gll, r"""
public static long getl(java.util.Properties p, String k, long def) {
  String v = get(p, k);
  if (v == null) return def;
  try { return Long.parseLong(v.trim()); } catch (Throwable t) { return def; }
}""")
# write the registry: tmp + fsync + atomic move (no sleep-retry on a world thread); false = not written (the caller changes nothing else)
M(gll, r"""
public static boolean save(String pk, java.util.Properties p) {
  if (bad(p)) return false;
  java.nio.file.Path f = file(pk);
  if (f == null) return false;
  try {
    if (FAIL_SAVE) throw new java.io.IOException("harness: the registry write fails");
    StringBuilder sb = new StringBuilder();
    sb.append("# SkyyGear lifelong tools of profile ").append(pk).append(" (written by the server - do not edit while it runs)\n");
    java.util.TreeSet ks = new java.util.TreeSet();
    java.util.Iterator it0 = p.keySet().iterator();
    while (it0.hasNext()) ks.add(String.valueOf(it0.next()));
    java.util.Iterator it = ks.iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String v = p.getProperty(k);
      if (v == null) continue;
      sb.append(k).append('=').append(v).append('\n');
    }
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try {
      out.write(sb.toString().getBytes("UTF-8"));
      out.flush();
      out.getFD().sync();
    } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    catch (java.nio.file.AtomicMoveNotSupportedException am) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    N[5] = N[5] + 1L;
    FAILAT.remove(pk);
    return true;
  } catch (Throwable t) {
    N[6] = N[6] + 1L;
    // fix round 2 (safety critic 4): one WARN per profile per 30 s (the failures are counted; non-forced sweeps back off - failing())
    long now = System.currentTimeMillis();
    Object lw = TOLD.get("save:" + pk);
    if (!(lw instanceof Long) || now < ((Long) lw).longValue() || now - ((Long) lw).longValue() >= 30000L) {
      TOLD.put("save:" + pk, Long.valueOf(now));
      @PKG@.Gear.warn("lifelong/" + pk + ".properties could not be written: " + t + " (" + N[6] + " failed writes so far; quiet for 30 s)");
    }
    FAILAT.put(pk, Long.valueOf(now));
    return false;
  }
}""")
# fix round 2 (safety critic 4): a registry write of this profile failed in the last 30 s (the every-scan sweep waits; forced ones still try)
M(gll, r"""
public static boolean failing(String pk) {
  Object l = pk == null ? null : FAILAT.get(pk);
  if (!(l instanceof Long)) return false;
  long now = System.currentTimeMillis();
  return now >= ((Long) l).longValue() && now - ((Long) l).longValue() < 30000L;
}""")
# ---- Upgrade Points + perks
M(gll, "public static boolean perkFor(int k, int p) { return k >= 0 && k < 4 && p >= 0 && p < PK.length && (PKMASK[p] & (1 << k)) != 0; }")
# Vein Mine / Tree Feller only once SkyyTrees reads them (it lists "vein" / "fell" in the bridge string gear:perk:readers)
M(gll, r"""
public static boolean perkOn(int p) {
  if (p < 3) return true;
  Object o = @PKG@.Gear.bget("gear:perk:readers");
  return o instanceof String && ("," + ((String) o).replace(" ", "") + ",").indexOf("," + PK[p] + ",") >= 0;
}""")
M(gll, r"""
public static int perkOf(java.util.Properties P, int k, int p) {
  if (!perkFor(k, p)) return 0;
  long v = getl(P, KIND[k] + ".up." + PK[p], 0L);
  if (v < 0L) return 0;
  return v > (long) PKMAX[p] ? PKMAX[p] : (int) v;
}""")
M(gll, "public static int pkCost(int p, int lvl) { return p < 0 || p >= PK.length || lvl < 1 || lvl > PKMAX[p] ? 0 : PKCOST[p * 10 + lvl - 1]; }")
M(gll, "public static int pkNeed(int p, int lvl) { return p < 0 || p >= PK.length || lvl < 1 || lvl > PKMAX[p] ? 99 : PKNEED[p * 10 + lvl - 1]; }")
M(gll, r"""
public static int spent(java.util.Properties P, int k) {
  int n = 0;
  for (int p = 0; p < PK.length; p++) {
    int lv = perkOf(P, k, p);
    for (int l = 1; l <= lv; l++) n = n + pkCost(p, l);
  }
  return n;
}""")
# 1 point per skill level (Skyy 2026-10-13): earned = skill level - 1 (a new player at level 1 has none); no SkyySkills = 0
M(gll, r"""
public static int earned(java.util.UUID u, int k) {
  int h = skill(u, k);
  return h > 1 ? h - 1 : 0;
}""")
M(gll, r"""
public static int free(java.util.UUID u, java.util.Properties P, int k) {
  int f = earned(u, k) - spent(P, k);
  return f < 0 ? 0 : f;
}""")
M(gll, r"""
public static long resetCost(java.util.Properties P, int k) {
  long sp = (long) spent(P, k);
  long n = getl(P, KIND[k] + ".resets", 0L);
  if (n < 0L) n = 0L;
  return (long) @PKG@.GearCfg.LL_RESET * sp * (n + 1L);
}""")
# { power x, Fortune +, Wisdom % + } of the held tool's perks: only a lifelong tool of the holder's own profile (others / off = { 1, 0, 0 })
M(gll, r"""
public static double[] perkFx(java.util.UUID u, int f, @BD@ d) {
  if (!mine(u, d)) return new double[] { 1.0, 0.0, 0.0 };
  int k = kOfFam(f);
  if (k < 0) return new double[] { 1.0, 0.0, 0.0 };
  java.util.Properties P = reg(@PKG@.Gear.pkey(u));
  double pw = 1.0 + (double) perkOf(P, k, 0) * @PKG@.GearCfg.LL_PSPD / 100.0;
  double fo = (double) perkOf(P, k, 1) * @PKG@.GearCfg.LL_PFORT;
  double wi = (double) perkOf(P, k, 2) * @PKG@.GearCfg.LL_PWIS;
  return new double[] { pw, fo, wi };
}""")
# ---- THE TIER GATE: { category (0 none, 1 ore, 3 log, 4 crop), block tier M (-1 = not gated) } of a BlockType
M(gll, r"""
public static int find(String[] w, int[] m, String x) {
  if (x == null) return -1;
  for (int i = 0; i < w.length; i++) if (w[i].equals(x)) return m[i];
  return -1;
}""")
M(gll, r"""
public static int[] catOf(String bid) {
  if (bid == null) return new int[] { 0, -1 };
  String id = bid.startsWith("*") ? bid.substring(1) : bid;
  String[] w = id.split("_");
  if (id.startsWith("Ore_") && w.length > 1) return new int[] { 1, find(ORE_W, ORE_M, w[1]) };
  if (id.startsWith("Wood_") && id.indexOf("_Trunk") > 0 && w.length > 2) return new int[] { 3, find(WOOD_W, WOOD_M, w[1]) };
  if (id.startsWith("Plant_Crop_") && w.length > 3) return new int[] { 4, find(CROP_W, CROP_M, w[2]) };
  return new int[] { 0, -1 };
}""")
M(gll, r"""
public static int[] cat(@TBTY@ bt) {
  String id = null;
  try { id = bt == null ? null : bt.getId(); } catch (Throwable t) { id = null; }
  return catOf(id);
}""")
# THE DECISION for a hit with stack s on a block of (category c, tier m): int[] { result, c, m, tool tier (-1 = no fitting tool), fam }
# result -1 = not gated, 0 normal, 1 one tier up (slow / no Fortune), 2 refused. A family's TOP vanilla tier handles every block above it
# (vanilla hoes end at Thorium, sickles at Iron: a Thorium hoe farms a Potato normally, an Iron hoe one tier up, a Copper hoe not at all).
M(gll, r"""
public static int[] decideI(String id, int c, int m) {
  if (!@PKG@.GearCfg.GATE_ON || c == 0 || m < 1) return new int[] { -1, c, m, -1, 0 };
  int f = id == null ? 0 : @PKG@.GearData.toolFam(id);
  boolean fits = (c == 1 && (f == 1 || f == 6)) || (c == 3 && (f == 3 || f == 6)) || (c == 4 && (f == 4 || f == 5));
  if (!fits) {
    if (c == 4 || !@PKG@.GearCfg.GATE_BARE) return new int[] { -1, c, m, -1, f };
    return new int[] { 2, c, m, -1, f };
  }
  int t = tier(id);
  int fm = f >= 0 && f < FAMMAX.length ? FAMMAX[f] : 7;
  int me = m > fm ? fm : m;
  int d = me - t;
  return new int[] { d <= 0 ? 0 : (d == 1 ? 1 : 2), c, m, t, f };
}""")
M(gll, "public static int[] decideC(@IS@ s, int c, int m) { return decideI((s == null || s.isEmpty()) ? null : s.getItemId(), c, m); }")
M(gll, r"""
public static int[] decide(@IS@ s, @TBTY@ bt) {
  int[] cm = cat(bt);
  return decideC(s, cm[0], cm[1]);
}""")
# fix round 2 (design critic 1): the one-tier-up factor of the tool in hand - Crude (tier 0) tools have their own row (the first hour)
M(gll, "public static double slowF(@IS@ s) { return s != null && !s.isEmpty() && tier(s.getItemId()) == 0 ? @PKG@.GearCfg.GATE_NEXT0 : @PKG@.GearCfg.GATE_NEXT; }")
# fix round 2 (safety critic 2): your own lifelong stack that is not the registry's current one (and no journal names it) - the sweep retires
# it at the next look; until then it breaks nothing either. Memory only (no disk read on a hit): no cached registry = not stale
M(gll, r"""
public static boolean stale(String pk, int k, @BD@ d) {
  Object o = REG.get(pk);
  if (!(o instanceof java.util.Properties) || k < 0 || k >= KIND.length) return false;
  java.util.Properties P = (java.util.Properties) o;
  if (bad(P)) return false;
  String cur = P.getProperty(KIND[k] + ".uid");
  String lu = uid(d);
  return cur != null && !lu.equals(cur) && !lu.equals(P.getProperty(KIND[k] + ".pend"));
}""")
M(gll, "public static String noun(int c) { return c == 1 ? \"pickaxe\" : (c == 3 ? \"hatchet\" : \"hoe or sickle\"); }")
# the block hit (GearToolHitSys, world thread): 0 = go on, 1 = slow (the caller multiplies the damage by gate.nextFactor), 2 = cancelled.
# A popup says why (GearGate.popup: the player switch gear.blockedPopup, 1.5 s throttle); the slow one at most every 30 s per player.
M(gll, r"""
public static int hit(@PR@ pr, @IS@ s, @TBTY@ bt) {
  try {
    java.util.UUID u = pr == null ? null : pr.getUuid();
    // fix round (critic A1 / engine critic 1): another profile's lifelong tool breaks nothing for you (handing yours over and then typing
    // /pickaxe gives no working second tool); llStack + pkey only for a pickaxe / hatchet / hoe / sickle in hand
    if (@PKG@.GearCfg.LL_ON && u != null && s != null && !s.isEmpty()) {
      int lk = kOf(s.getItemId());
      if (lk >= 0 && llStack(s.getItemId(), s.getMetadata())) {
        @BD@ ld = @PKG@.GearData.gearDoc(s.getMetadata());
        String hpk = @PKG@.Gear.pkey(u);
        if (!hpk.equals(owner(ld))) {
          N[0] = N[0] + 1L;
          N[7] = N[7] + 1L;
          if (pr != null) @PKG@.GearGate.popup(pr, u, s.getItemId(), "Not your tool", "This is another player's lifelong " + KIND[lk] + " - it does nothing for you. Yours: /" + KIND[lk] + ".");
          return 2;
        }
        // fix round 2 (safety critic 2): your own RETIRED (or not yet swept, stale) lifelong tool breaks nothing - one working tool per kind
        if (isRt(ld) || stale(hpk, lk, ld)) {
          N[0] = N[0] + 1L;
          N[8] = N[8] + 1L;
          if (pr != null) @PKG@.GearGate.popup(pr, u, s.getItemId(), "Retired " + KIND[lk], "Only your current lifelong " + KIND[lk] + " works. Hold this one and type /lifelong to swap them.");
          return 2;
        }
      }
    }
    int[] d = decide(s, bt);
    if (d[0] < 1) return 0;
    String tn = (s == null || s.isEmpty()) ? null : @PKG@.Gear.itemName(s.getItemId());
    String icon = (s == null || s.isEmpty()) ? null : s.getItemId();
    if (d[0] == 2) {
      N[0] = N[0] + 1L;
      if (d[3] < 0) {
        N[2] = N[2] + 1L;
        if (pr != null) @PKG@.GearGate.popup(pr, u, icon, "You need a " + noun(d[1]), (d[1] == 1 ? "Ore needs a pickaxe" : "Logs need a hatchet") + ". Lost yours? Type /" + (d[1] == 1 ? "pickaxe" : "hatchet") + ".");
      } else if (pr != null) {
        int need = d[2] - 1;
        @PKG@.GearGate.popup(pr, u, icon, "Too tough for your " + tn, "It needs " + an(tname(need)) + " " + noun(d[1]) + " or better. Tier yours up on the Anvil (/smithing).");
      }
      return 2;
    }
    N[1] = N[1] + 1L;
    if (pr != null && u != null) {
      long now = System.currentTimeMillis();
      Object l = SLOW.get(u);
      if (!(l instanceof Long) || now - ((Long) l).longValue() > 30000L) {
        SLOW.put(u, Long.valueOf(now));
        @PKG@.GearGate.popup(pr, u, icon, "Slow going", "This is one tier above your " + tn + ". With " + an(tname(d[2])) + " " + noun(d[1]) + " it breaks at full speed.");
      }
    }
    return 1;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("llhit", "the tool tier gate failed (the hit goes on unchanged): " + t); return 0; }
}""")
# FARMING one tier up = no Fortune (Skyy 2026-10-13 G5): a hoe / sickle posts only.farming = the crops its tier covers + the free crops
M(gll, r"""
public static String onlyFor(int f, int t, String def) {
  if ((f != 4 && f != 5) || !@PKG@.GearCfg.GATE_ON || !@PKG@.GearCfg.LL_ON) return def;
  String key = f + ":" + t;
  Object o = ONLY.get(key);
  if (o instanceof String) return (String) o;
  StringBuilder sb = new StringBuilder();
  int fm = FAMMAX[f];
  for (int i = 0; i < CROP_W.length; i++) {
    int me = CROP_M[i] > fm ? fm : CROP_M[i];
    if (me <= t) { if (sb.length() > 0) sb.append(','); sb.append(CROP_W[i]); }
  }
  if (CROP_FREE.length() > 0) { if (sb.length() > 0) sb.append(','); sb.append(CROP_FREE); }
  String v = sb.toString();
  ONLY.put(key, v);
  return v;
}""")
# gear:fn:farmTier (for SkyySkills: half Farming XP one tier up) - Object[] { UUID, String block id, String held item id } -> Integer
# -1 not gated, 0 normal, 1 one tier up (half XP, no Fortune), 2 refused (fix round, engine critic 6: plain java.lang types only)
M(gll, r"""
public static int farmTier(String bid, String held) {
  int[] cm = catOf(bid);
  if (cm[0] != 4) return -1;
  return decideI(held, cm[0], cm[1])[0];
}""")
# NO CRAFTING (Skyy: "you cant make more, you can only upgrade them"): a pickaxe / hatchet / hoe / sickle output
M(gll, "public static boolean noCraft(String id) { return @PKG@.GearCfg.LL_ON && @PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0; }")
# a tool ladder step is a lifelong-only step (part.lifelong on)
M(gll, "public static boolean ladderTool(String id) { return @PKG@.GearCfg.LL_ON && kOf(id) >= 0; }")
# the Anvil ladders = upgrade.ladders + lifelong.ladders (GearUp.tab re-parses only when the joined text changes)
M(gll, r"""
public static String ladders() {
  String a = @PKG@.GearCfg.UP_LADDERS == null ? "" : @PKG@.GearCfg.UP_LADDERS;
  String b = @PKG@.GearCfg.LL_LADDERS == null ? "" : @PKG@.GearCfg.LL_LADDERS;
  if (!@PKG@.GearCfg.LL_ON || b.trim().length() == 0) return a;
  if (a.trim().length() == 0) return b;
  return a + "," + b;
}""")
# a tier-up needs the skill level the new tier starts at (its level.material start)
M(gll, r"""
public static String tierWhy(java.util.UUID u, String to) {
  int k = kOf(to);
  if (k < 0) return null;
  int h = skill(u, k);
  if (h == -2) return null;
  if (h < 0) h = 0;
  int need = @PKG@.GearLevel.band(to)[0];
  if (@PKG@.GearLevel.floor(h) >= need) return null;
  return "You need " + KSKILL[k] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h + ").";
}""")
# the tooltip lines of a lifelong tool (GearTool.lines, under the tool's numbers); owner null = neutral
M(gll, r"""
public static void lines(java.util.UUID ow, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  if (!@PKG@.GearCfg.LL_ON || !isLL(d)) return;
  int k = kOf(id);
  if (k < 0) return;
  if (ow != null && !@PKG@.Gear.pkey(ow).equals(owner(d))) {
    txt.add("Lifelong tool of another player");
    col.add(@PKG@.GearDefs.C_GRAY);
    return;
  }
  if (isRt(d)) {          // fix round 2
    txt.add("Retired lifelong " + KIND[k] + " - it breaks nothing");
    col.add(@PKG@.GearDefs.C_GRAY);
    txt.add("Hold it and type /lifelong to swap it with your current one");
    col.add(@PKG@.GearDefs.C_GRAY);
    return;
  }
  txt.add("Lifelong " + KIND[k] + ": levels with " + KSKILL[k] + " (max Lv " + cap(id) + ")");
  col.add(@PKG@.GearDefs.C_LABEL);
  if (ow != null) {
    java.util.Properties P = reg(@PKG@.Gear.pkey(ow));
    StringBuilder sb = new StringBuilder();
    for (int p = 0; p < PK.length; p++) {
      int lv = perkOf(P, k, p);
      if (lv <= 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(PKN[p]).append(' ').append(lv);
    }
    if (sb.length() > 0) { txt.add("Upgrades: " + sb.toString()); col.add(null); }
    int fr = free(ow, P, k);
    if (fr > 0) { txt.add(fr + " Upgrade Point" + (fr == 1 ? "" : "s") + " free - /toolpoints"); col.add(@PKG@.GearDefs.C_GOLD); }
  }
  txt.add("Can't be dropped. Lost it? /" + KIND[k]);
  col.add(@PKG@.GearDefs.C_GRAY);
}""")
# the Tools tab click on another Smithing page (mode:4) -> /toolpoints; true = handled
M(gll, r"""
public static boolean tabGo(String data, @PR@ pr) {
  if (data == null || !"mode:4".equals(@PKG@.Gear.jsonStr(data, "a"))) return false;
  if (@PKG@.GearCfg.LL_ON && pr != null) {
    try { @CMGR@.get().handleCommand(pr, "toolpoints"); } catch (Throwable t) { @PKG@.Gear.warn("the Tools tab could not open /toolpoints: " + t); }
  }
  return true;
}""")
M(gll, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  SLOW.remove(u);
  LAST.remove(u);
  String p = u + ":";
  Object[] ks = TOLD.keySet().toArray();
  for (int i = 0; i < ks.length; i++) if (String.valueOf(ks[i]).startsWith(p)) TOLD.remove(ks[i]);
}""")
# the write side hooks (bodies set by GearLife below: GearRefreshTask / GearStampTask are compiled before GearLife exists)
M(gll, "public static void joinHook(@PR@ pr, @INV@ inv) { }")
M(gll, "public static void sweepHook(@PR@ pr, @INV@ inv) { }")
M(gll, r"""
public static String statusText() {
  if (!@PKG@.GearCfg.LL_ON) return "lifelong tools OFF (part.lifelong)" + (@PKG@.GearCfg.GATE_ON ? "; tool tier gate on" : "; tool tier gate OFF");
  return "lifelong tools on (one pickaxe / hatchet / hoe / sickle per profile, level = skill level capped by tier, 1 Upgrade Point per level, crafting " + (@PKG@.GearCfg.LL_NOCRAFT ? "refused" : "allowed") + ", drops " + (@PKG@.GearCfg.LL_NODROP ? "refused" : "allowed") + ", /pickaxe /hatchet /hoe /sickle every " + @PKG@.GearCfg.LL_RECLAIM + " s); tool tier gate " + (@PKG@.GearCfg.GATE_ON ? "on (one tier up x" + @PKG@.Gear.fnum(@PKG@.GearCfg.GATE_NEXT) + ", two up refused, bare hands " + (@PKG@.GearCfg.GATE_BARE ? "no logs / ore" : "allowed") + ")" : "OFF (gate.on)");
}""")
M(gll, r"""
public static String counters() {
  return "gate refused " + N[0] + " (bare hands " + N[2] + ", another player's tool " + N[7] + ", a retired tool " + N[8] + "), slowed " + N[1] + "; crafts refused " + N[3] + "; drops refused " + N[4] + "; registry writes " + N[5] + " (failed " + N[6] + "); profiles cached " + REG.size();
}""")
'''
before('''gtool = mk("GearTool")
TOOL_CLASSES = [gtool]
''', LIFE_A)

# ================================================================================================================ GearTool: the level rule, perks, Fortune filter, lines
rep('''  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });''', '''  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });
  @PKG@.GearLL.lvlWatch(u, s);          // 0.3.0 fix round: a lifelong tool's stale [Lv N] after a skill level-up (GearHandSys queues the sweep)''')
# fix round (engine critic 2): GearHandSys (every tick) hands a stale level to the stamp task (one map look while nothing is stale)
rep('''    @PKG@.GearTool.held(pr.getUuid(), held);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }''', '''    @PKG@.GearTool.held(pr.getUuid(), held);
    if (!@PKG@.GearLL.RESYNC.isEmpty() && @PKG@.GearLL.RESYNC.remove(pr.getUuid()) != null) @PKG@.GearStamp.dirtyIn(pr, 0L);     // 0.3.0 fix round
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }''')
rep('''public static int[] gate(java.util.UUID u, int f, String id, @BD@ d) {
  int need = @PKG@.GearLevel.level(id, d);''', '''public static int[] gate(java.util.UUID u, int f, String id, @BD@ d) {
  // 0.3.0 (Skyy 2026-10-13 "tools dont have XP they just match your skill level"): YOUR lifelong tool works at min(skill, its tier's
  // band top) whatever its document says (the sweep rewrites the document's level for the name + tooltip)
  if (u != null && @PKG@.GearLL.mine(u, d)) {
    int ll = @PKG@.GearLL.levelFor(u, id);
    if (ll >= 1) return new int[] { ll, ll, 1, -1 };
  }
  int need = @PKG@.GearLevel.level(id, d);''')
rep('''    wi = ef[2];
  }
  return new double[] { (double) f, (double) row(f), (double) g[1], on ? 1.0 : 0.0, pw, fo, (double) g[0], (double) t, wi };''', '''    wi = ef[2];
    double[] px = @PKG@.GearLL.perkFx(u, f, d);          // 0.3.0: a lifelong tool's Speed / Fortune / Wisdom perks (the caps still hold)
    if (px[0] > 1.0 && f <= 3) { pw = pw * px[0]; if (pw > 100.0) pw = 100.0; }
    if (px[1] > 0.0) { fo = fo + px[1]; if (fo > @PKG@.GearCfg.TOOL_FCAP) fo = @PKG@.GearCfg.TOOL_FCAP; fo = (double) Math.round(fo * 10.0) / 10.0; }
    if (px[2] > 0.0) { wi = wi + px[2]; if (wi > @PKG@.GearCfg.TOOL_WCAP) wi = @PKG@.GearCfg.TOOL_WCAP; }
  }
  return new double[] { (double) f, (double) row(f), (double) g[1], on ? 1.0 : 0.0, pw, fo, (double) g[0], (double) t, wi };''')
rep('''  else postX(u, (int) st[1], tf + af, ONLY[(int) st[0]], aw + tw);''',
    '''  else postX(u, (int) st[1], tf + af, @PKG@.GearLL.onlyFor((int) st[0], (int) st[7], ONLY[(int) st[0]]), aw + tw);     // 0.3.0: a hoe / sickle's crops''')
rep('''    txt.add("Tree Feller unlocks in the Foraging tree");   // fix round 2: the SkyyTrees perk, not a hatchet stat
    col.add(@PKG@.GearDefs.C_GRAY);
  }
}""")''', '''    txt.add("Tree Feller unlocks in the Foraging tree");   // fix round 2: the SkyyTrees perk, not a hatchet stat
    col.add(@PKG@.GearDefs.C_GRAY);
  }
  @PKG@.GearLL.lines(owner, id, d, txt, col);          // 0.3.0: lifelong tool lines
}""")''')

# ================================================================================================================ the block hit: the tier gate first
rep('''    float d0 = e.getDamage();
    float d1 = @PKG@.GearTool.onDamage(pr.getUuid(), e.getItemInHand(), e.getBlockType(), d0);
    if (d1 != d0) e.setDamage(d1);""")''', '''    float d0 = e.getDamage();
    // 0.3.0 THE TIER GATE: two tiers up (or no pickaxe / hatchet on ore / logs) = cancelled: no damage, no drop, no XP; one tier up = the
    // hit x gate.nextFactor (after the tool's own power, so a strong tool is still faster one tier up than a weak one)
    int gq = @PKG@.GearLL.hit(pr, e.getItemInHand(), e.getBlockType());
    if (gq == 2) { e.setCancelled(true); return; }
    float d1 = @PKG@.GearTool.onDamage(pr.getUuid(), e.getItemInHand(), e.getBlockType(), d0);
    if (gq == 1) d1 = (float) ((double) d1 * @PKG@.GearLL.slowF(e.getItemInHand()));          // fix round 2: Crude tools have their own row
    if (d1 != d0) e.setDamage(d1);""")''')

# ================================================================================================================ no crafting of the four kinds
rep('''    @CREPRE@ e = (@CREPRE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CRAFT || !@PKG@.GearCfg.PART_LEVELS || !"block".equals(@PKG@.GearCfg.CRAFT_BELOW)) return;''',
    '''    @CREPRE@ e = (@CREPRE@) ev;
    if (e.isCancelled()) return;
    // 0.3.0 (Skyy: "since you spawn with the tool, and cant make more, you can only upgrade them"): no bench / /craft recipe makes a pickaxe,
    // hatchet, hoe or sickle (CraftingManager.craftItem stops on a cancelled Pre - VERIFIED bytecode); Creative still crafts
    @CRR@ rc0 = e.getCraftedRecipe();
    @MQ@ po0 = rc0 == null ? null : rc0.getPrimaryOutput();
    String id0 = po0 == null ? null : po0.getItemId();
    if (id0 != null && @PKG@.GearLL.noCraft(id0)) {
      @REF@ r0 = chunk.getReferenceTo(idx);
      @PR@ pr0 = r0 == null ? null : (@PR@) st.getComponent(r0, @PR@.getComponentType());
      @PLA@ p0 = r0 == null ? null : (@PLA@) st.getComponent(r0, @PLA@.getComponentType());
      if (p0 == null || p0.getGameMode() != @GM@.Creative) {
        e.setCancelled(true);
        @PKG@.GearLL.N[3] = @PKG@.GearLL.N[3] + 1L;
        int k0 = @PKG@.GearLL.kOf(id0);
        if (pr0 != null) pr0.sendMessage(@MSG@.raw("[Gear] Tools are not crafted any more - you keep one " + @PKG@.GearLL.KIND[k0] + " for life. Tier it up on the Anvil (/smithing); lost it? /" + @PKG@.GearLL.KIND[k0]).color(@PKG@.GearDefs.C_BAD));
        @PKG@.GearLog.line("CRAFT-BLOCK-LIFELONG " + (pr0 == null ? "?" : pr0.getUsername() + " " + pr0.getUuid()) + " " + id0 + " recipe " + rc0.getId());
        return;
      }
    }
    if (!@PKG@.GearCfg.PART_CRAFT || !@PKG@.GearCfg.PART_LEVELS || !"block".equals(@PKG@.GearCfg.CRAFT_BELOW)) return;''')
rep('''  if (!@PKG@.GearRoll.craftable(out) || cat(out) < 0 || @PKG@.GearUtFx.mythicId(out)) return false;''',
    '''  if (!@PKG@.GearRoll.craftable(out) || cat(out) < 0 || @PKG@.GearUtFx.mythicId(out) || @PKG@.GearLL.noCraft(out)) return false;     // 0.3.0''')

# ================================================================================================================ never on the market, never bought levels, never merged
rep('''public static String why(String id, @BD@ md) {
  if (id == null) return null;
  if (@PKG@.GearUnid.isBox(id)) {''', '''public static String why(String id, @BD@ md) {
  if (id == null) return null;
  // 0.3.0: a lifelong tool is yours for life - never on the Auction House / Bazaar
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.llStack(id, md)) return "Lifelong tools stay with their owner - they never go on the market.";
  if (@PKG@.GearUnid.isBox(id)) {''')
rep('''  if (d == null) return lvOut(7, cur, max, org, "The gear data on this item is unreadable.");''',
    '''  if (d == null) return lvOut(7, cur, max, org, "The gear data on this item is unreadable.");
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return lvOut(8, cur, cur, org, "a lifelong tool follows your skill level.");     // 0.3.0''')
rep('''  if (d == null) return null;
  if (!@PKG@.GearData.identified(d)) return "Identify that " + w + " first" + @PKG@.GearCfg.idHow() + ".";''',
    '''  if (d == null) return null;
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return "Your lifelong " + w + " cannot be merged (multitools come after your first rebirth).";     // 0.3.0
  if (!@PKG@.GearData.identified(d)) return "Identify that " + w + " first" + @PKG@.GearCfg.idHow() + ".";''')

# ================================================================================================================ the Anvil tier-up
rep('''  String s = @PKG@.GearCfg.UP_LADDERS;
  if (s == null) s = "";
  Object[] cur = TAB;''', '''  String s = @PKG@.GearLL.ladders();          // 0.3.0: upgrade.ladders + lifelong.ladders
  if (s == null) s = "";
  Object[] cur = TAB;''')
rep('''    if (@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null) return new Object[] { special(id), to, null };
  }
  if (@PKG@.Gear.item(to) == null) return new Object[] { "There is no " + to + " on this server (its mod is not loaded).", to, null };''',
    '''    if (@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null) return new Object[] { special(id), to, null };
  }
  // 0.3.0: only YOUR lifelong tool climbs a tool ladder (found / old tools stay plain), and only with the skill level the new tier starts at
  if (@PKG@.GearLL.ladderTool(id)) {
    int lk = @PKG@.GearLL.kOf(id);
    if (!@PKG@.GearLL.mine(u, d)) return new Object[] { "Only your lifelong " + @PKG@.GearLL.KIND[lk] + " can be tiered up - this one is a plain tool.", to, null };
    String lw = @PKG@.GearLL.tierWhy(u, to);
    if (lw != null) return new Object[] { lw, to, null };
  }
  if (@PKG@.Gear.item(to) == null) return new Object[] { "There is no " + to + " on this server (its mod is not loaded).", to, null };''')
rep('''  nd.put("mods", out);
  return nd;
}""")
M(gup, r"""
public static String lossText(int[] info) {''', '''  nd.put("mods", out);
  // 0.3.0: a lifelong tool stays at your skill level on the new tier (its band top caps it); the ll / uid fields come along with the copy
  if (u != null && @PKG@.GearLL.isLL(nd)) {
    int ll = @PKG@.GearLL.levelFor(u, to);
    if (ll >= 1) { nd.put("lvl", new org.bson.BsonInt32(ll)); info[3] = ll; }
  }
  return nd;
}""")
M(gup, r"""
public static String lossText(int[] info) {''')

# ================================================================================================================ the Tools tab
rep('''  boolean mt = multiTab();
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0);''', '''  boolean mt = multiTab();
  boolean lt = @PKG@.GearCfg.LL_ON;          // 0.3.0: the Tools tab (/toolpoints)
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0) + (lt ? 1 : 0);''')
rep('''  int[] order = new int[] { 3, 0, 1, 2 };''', '''  int[] order = new int[] { 3, 0, 4, 1, 2 };''')
rep('''    if (m == 2 && !mt) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");''', '''    if (m == 2 && !mt) continue;
    if (m == 4 && !lt) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");''')
rep('''    String nm = m == 3 ? "Craft" : (m == 0 ? (@PKG@.GearCfg.ANVIL_ON ? "Anvil" : "Reforge") : (m == 1 ? "Upgrade" : "Multitool"));''',
    '''    String nm = m == 3 ? "Craft" : (m == 0 ? (@PKG@.GearCfg.ANVIL_ON ? "Anvil" : "Reforge") : (m == 1 ? "Upgrade" : (m == 4 ? "Tools" : "Multitool")));''')

# ================================================================================================================ the join + scan hooks
rep('''    if (!this.onWorld) {
      java.util.UUID wu = this.pr.getWorldUuid();
      if (wu == null) { again("player is in no world"); return; }''', '''    if (!this.onWorld) {
      @PKG@.GearLL.prefetch(this.pr.getUuid());          // 0.3.0: the lifelong registry is read here, on the scheduler
      java.util.UUID wu = this.pr.getWorldUuid();
      if (wu == null) { again("player is in no world"); return; }''')
rep('''    rollsWarn(this.pr);
  } catch (Throwable t) { @PKG@.Gear.warn("gear refresh failed: " + t); }''', '''    rollsWarn(this.pr);
    @PKG@.GearLL.joinHook(this.pr, inv);          // 0.3.0: the lifelong migration (once) + the sweep
  } catch (Throwable t) { @PKG@.Gear.warn("gear refresh failed: " + t); }''')
rep('''    @PKG@.GearStamp.scanSome(this.pr, @PKG@.GearStamp.invOf(this.pr), @PKG@.GearStamp.SLOTS_PER_TASK);      // 0.2.25: 12 gear slots a task
    @PKG@.GearStamp.follow(this.pr);''', '''    @PKG@.GearStamp.scanSome(this.pr, @PKG@.GearStamp.invOf(this.pr), @PKG@.GearStamp.SLOTS_PER_TASK);      // 0.2.25: 12 gear slots a task
    @PKG@.GearStamp.follow(this.pr);
    @PKG@.GearLL.sweepHook(this.pr, @PKG@.GearStamp.invOf(this.pr));          // 0.3.0: lifelong levels / copies (throttled inside)''')

# ================================================================================================================ GearLife + the Tools page + the commands
LIFE_B = r'''
# ####################################################################################################################################
# 0.3.0 LIFELONG TOOLS, WRITE SIDE (tools/gear_0_3_0_patch.py header): GearLife (the sweep on every inventory scan: journal recovery, the
# one-time migration, level sync, returned / stale copies; /pickaxe /hatchet /hoe /sickle; /lifelong; perks + reset), LifePage (the Tools
# tab, /toolpoints), the commands, GearLLDropSys (DropItemEvent$PlayerRequest) and GearLLFn (gear:fn:lifelong / perk / farmTier). Placed
# after /identify: it calls GearStamp, GearData, GearView, GearForge (coins), GearMerge.json, GearSmith.rqList (Requip), GearUi, GearTool.
# Every item write: the journal line is on disk FIRST (GearLL.save), the slot write is read back, the commit comes last; a crash at any
# step leaves either nothing done or a journal the next sweep finishes (never a second item, never a lost one).
# ####################################################################################################################################
LT = {"DIRQ": "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest",
      "IUT": "com.hypixel.hytale.server.core.inventory.InventoryUtils"}
for _k in LT:
    assert _k not in T, "0.3.0 token clashes: " + _k
T.update(LT)
for _c, _m in (("com.hypixel.hytale.server.core.entity.entities.Player", "getWindowManager"), (T["WMGR"], "markWindowChanged"),
               (LT["DIRQ"], "getInventorySectionId"), (LT["DIRQ"], "getSlotId"), (LT["DIRQ"], "setCancelled"), (LT["DIRQ"], "isCancelled"),
               (LT["IUT"], "getSectionById"), (IC, "removeItemStackFromSlot"), (INV, "getActiveToolsSlot"), (INV, "getActiveHotbarSlot")):
    B.probe(pool, _c, _m)
_gsb = [m_ for m_ in pool.get(LT["IUT"]).getDeclaredMethods() if str(m_.getName()) == "getSectionById"]
assert len(_gsb) == 1 and str(_gsb[0].getSignature()) == ("(Lcom/hypixel/hytale/component/Ref;ILcom/hypixel/hytale/component/ComponentAccessor;)"
                                                         "Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;"), \
    "InventoryUtils.getSectionById changed: %s" % [str(m_.getSignature()) for m_ in _gsb]
assert J0["Modifier"].isStatic(_gsb[0].getModifiers()) and J0["Modifier"].isPublic(_gsb[0].getModifiers())
glf = mk("GearLife")
lpg = mk("LifePage", PAGE)
LL_CMDS = [("PickaxeCmd", "pickaxe", 0), ("HatchetCmd", "hatchet", 1), ("HoeCmd", "hoe", 2), ("SickleCmd", "sickle", 3)]
llcmds = [mk(_n, APC) for _n, _c, _k in LL_CMDS]
tpc = mk("ToolPtsCmd", APC)
llc = mk("LifelongCmd", APC)
gdrop = mk("GearLLDropSys", EES)
gllfn = mk("GearLLFn")
LIFE_CLASSES += [glf, lpg] + llcmds + [tpc, llc, gdrop, gllfn]
# counters: 0 sweeps, 1 level writes, 2 marked, 3 given, 4 restored, 5 demoted, 6 copies removed, 7 /pickaxe given, 8 perks bought,
# 9 resets, 10 adopted, 11 journals finished, 12 retired (fix round 2), 13 swapped back with /lifelong (fix round 2)
F(glf, "public static final long[] N = new long[14];")
F(glf, "public static volatile int CRASH_AT = 0;")             # harness only: throw at that step (a crash)
M(glf, r"""
public static void crash(int n) {
  if (CRASH_AT == n) throw new IllegalStateException("harness: a crash at lifelong step " + n);
}""")
M(glf, r"""
public static @BD@ docOf(@IS@ x) {
  if (x == null || x.isEmpty()) return null;
  try { return @PKG@.GearData.gearDoc(x.getMetadata()); } catch (Throwable t) { return null; }
}""")
# int[] { section, slot } of the lifelong stack lu of profile pk in this inventory (null = not here)
M(glf, r"""
public static int[] find(@INV@ inv, String pk, String lu) {
  if (inv == null || lu == null || lu.length() == 0) return null;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || @PKG@.GearLL.kOf(x.getItemId()) < 0) continue;
      @BD@ d = docOf(x);
      if (@PKG@.GearLL.isLL(d) && lu.equals(@PKG@.GearLL.uid(d)) && pk.equals(@PKG@.GearLL.owner(d))) return new int[] { @PKG@.GearStamp.SCAN[a], i };
    }
  }
  return null;
}""")
# a lifelong stack of this profile and kind already in the inventory (a registry line that was lost): the first non-replacement wins
M(glf, r"""
public static int[] findKind(@INV@ inv, String pk, int k) {
  int[] rp = null;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || @PKG@.GearLL.kOf(x.getItemId()) != k) continue;
      @BD@ d = docOf(x);
      if (!@PKG@.GearLL.isLL(d) || !pk.equals(@PKG@.GearLL.owner(d))) continue;
      if (!@PKG@.GearLL.isRp(d) && !@PKG@.GearLL.isRt(d)) return new int[] { @PKG@.GearStamp.SCAN[a], i };          // fix round 2: retired = fallback
      if (rp == null) rp = new int[] { @PKG@.GearStamp.SCAN[a], i };
    }
  }
  return rp;
}""")
# THE MIGRATION PICK (spec 12.1): the best single, identified, not-yet-lifelong tool of kind k: highest rarity, then level, then lines
M(glf, r"""
public static int[] best(@INV@ inv, int k) {
  int bs = -1;
  int bi = -1;
  int br = -1;
  int bl = -1;
  int bm = -1;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || x.getQuantity() != 1) continue;
      String id = x.getItemId();
      if (@PKG@.GearLL.kOf(id) != k) continue;
      @BD@ md = x.getMetadata();
      int st = @PKG@.GearData.state(md);
      if (st == 3 || st == 4) continue;
      @BD@ d = null;
      try { d = @PKG@.GearData.effective(id, md); } catch (Throwable t) { d = null; }
      if (st != 0 && d == null) continue;
      if (d != null && (!@PKG@.GearData.identified(d) || @PKG@.GearLL.isLL(d))) continue;
      int r = d == null ? 0 : @PKG@.GearData.rarity(d);
      if (r > 4) continue;
      int lv = @PKG@.GearLevel.level(id, d);
      int m = d == null ? 0 : @PKG@.GearData.mods(d).size();
      if (r > br || (r == br && (lv > bl || (lv == bl && m > bm)))) { br = r; bl = lv; bm = m; bs = @PKG@.GearStamp.SCAN[a]; bi = i; }
    }
  }
  if (bs < 0) return null;
  return new int[] { bs, bi };
}""")
# the document that makes a stack lifelong: its own (rarity, lines, reforge name kept) or a fresh Normal one; the bought level ups go
M(glf, r"""
public static @BD@ llDoc(@BD@ d0, String id, java.util.UUID u, String pk, String lu, boolean rp) {
  @BD@ nd = d0 == null ? @PKG@.GearData.base(@PKG@.GearData.kindFor(id), 0, true, "lifelong") : d0.clone();
  nd.put("ll", new org.bson.BsonInt32(1));
  nd.put("lu", new org.bson.BsonString(lu));
  nd.put("lo", new org.bson.BsonString(pk));
  if (rp) { nd.put("lrp", new org.bson.BsonInt32(1)); nd.put("lrpT", new org.bson.BsonInt32(@PKG@.GearLL.tier(id))); }
  else { nd.remove("lrp"); nd.remove("lrpT"); }
  if (@PKG@.GearData.mods(nd).size() == 0) nd.put("tr", new org.bson.BsonInt32(1));
  nd.remove("lvU");
  int lv = @PKG@.GearLL.levelFor(u, id);
  if (lv >= 1) nd.put("lvl", new org.bson.BsonInt32(lv));
  return nd;
}""")
# one slot write, read back: true = the slot now carries exactly that lifelong state (uid + ll flag)
M(glf, r"""
public static boolean put(@IC@ c, int slot, @IS@ x, @BD@ nd, java.util.UUID u) {
  try {
    @IS@ ns = @PKG@.GearData.put(x, nd, u);
    Object tx = c.setItemStackForSlot((short) slot, ns);
    if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) return false;
    @PKG@.GearStamp.selfNote(u, tx);
    @BD@ back = docOf(c.getItemStack((short) slot));
    return back != null && @PKG@.GearLL.uid(back).equals(@PKG@.GearLL.uid(nd)) && @PKG@.GearData.num(back, "ll", 0) == @PKG@.GearData.num(nd, "ll", 0);
  } catch (Throwable t) { @PKG@.Gear.warn("lifelong: a slot write failed: " + t); return false; }
}""")
M(glf, r"""
public static void clearPend(java.util.Properties P, String K) {
  P.remove(K + ".pend");
  P.remove(K + ".pendMode");
  P.remove(K + ".pendId");
}""")
# THE JOURNAL: on disk before the item is touched; false = not written (nothing is done)
M(glf, r"""
public static boolean journal(String pk, java.util.Properties P, int k, String lu, String mode, String id) {
  String K = @PKG@.GearLL.KIND[k];
  P.setProperty(K + ".pend", lu);
  P.setProperty(K + ".pendMode", mode);
  P.setProperty(K + ".pendId", id);
  if (@PKG@.GearLL.save(pk, P)) return true;
  clearPend(P, K);
  return false;
}""")
# THE COMMIT: the registry names the new uid (memory first - the item already carries it; a failed write leaves the journal on disk, which the
# next sweep finishes the same way). wr false (fix round, engine critic 3: the migration) = memory only: the next journal write or the
# sweep's single save carries it; a crash before that leaves the journal on disk = the same path as a failed commit write
M(glf, r"""
public static boolean commit(String pk, java.util.Properties P, int k, String lu, String id, boolean rp, String xk, String xv, boolean wr) {
  String K = @PKG@.GearLL.KIND[k];
  P.setProperty(K + ".uid", lu);
  P.setProperty(K + ".id", id);
  P.setProperty(K + ".rp", rp ? "1" : "0");
  P.remove(K + ".seen");
  P.remove(K + ".inv");
  if (xk != null) P.setProperty(xk, xv);
  clearPend(P, K);
  if (!wr) return true;
  return @PKG@.GearLL.save(pk, P);
}""")
M(glf, r"""
public static void tellOnce(@PR@ pr, String key, String text, long gapMs) {
  if (pr == null) return;
  try {
    long now = System.currentTimeMillis();
    String k = pr.getUuid() + ":" + key;
    Object l = @PKG@.GearLL.TOLD.get(k);
    if (l instanceof Long && now - ((Long) l).longValue() < gapMs && now >= ((Long) l).longValue()) return;
    @PKG@.GearLL.TOLD.put(k, Long.valueOf(now));
    pr.sendMessage(@MSG@.raw("[Gear] " + text).color(@PKG@.GearDefs.C_GOLD));
  } catch (Throwable t) { }
}""")
# a journalled step the server did not finish (a crash): the item carries the uid -> commit; a give with no item yet -> kept (the
# migration gives again with the SAME uid); any other step that never reached its item -> the journal goes
M(glf, r"""
public static void recover(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  for (int k = 0; k < 4; k++) {
    String K = @PKG@.GearLL.KIND[k];
    String lu = P.getProperty(K + ".pend");
    if (lu == null) continue;
    String mode = P.getProperty(K + ".pendMode");
    int[] at = find(inv, pk, lu);
    if (at != null) {
      @IS@ x = @PKG@.GearStamp.at(inv, at[0], at[1]);
      boolean rc = "reclaim".equals(mode);
      String xk = rc ? K + ".reclaimAt" : ("repick".equals(mode) ? K + ".repick" : null);
      String xv = rc ? String.valueOf(System.currentTimeMillis()) : "1";
      commit(pk, P, k, lu, x.getItemId(), rc, xk, xv, true);
      N[11] = N[11] + 1L;
      @PKG@.GearLog.line("LL-RECOVER " + pr.getUuid() + " " + pk + " " + K + " " + mode + " " + lu + " found " + x.getItemId() + " -> committed");
      continue;
    }
    if ("give".equals(mode)) continue;
    clearPend(P, K);
    if ("repick".equals(mode)) P.remove(K + ".free");          // fix round 2: the re-pick never happened - the current one is no "old" one
    @PKG@.GearLL.save(pk, P);
    @PKG@.GearLog.line("LL-RECOVER " + pr.getUuid() + " " + pk + " " + K + " " + mode + " " + lu + " not in the inventory -> journal dropped (nothing was done)");
  }
}""")
# make the stack at (s, slot) the lifelong tool of kind k (mode "mark" = migration, "repick" = /lifelong)
M(glf, r"""
public static boolean mark(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, int s, int slot, String mode) {
  java.util.UUID u = pr.getUuid();
  String K = @PKG@.GearLL.KIND[k];
  @IC@ c = @PKG@.GearStamp.section(inv, s);
  @IS@ x = c == null ? null : c.getItemStack((short) slot);
  if (x == null || x.isEmpty()) return false;
  String id = x.getItemId();
  @BD@ d = null;
  try { d = @PKG@.GearData.effective(id, x.getMetadata()); } catch (Throwable t0) { d = null; }
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int before = @PKG@.GearStamp.countId(all, id);
  String undo = @PKG@.GearMerge.json(x);          // fix round: the stack as it was (gear.log - an admin can put it back)
  int olv = d == null ? -1 : @PKG@.GearData.num(d, "lvl", -1);          // fix round 2 (safety critic 5): the level it had + the coin-bought level ups
  int olu = d == null ? 0 : @PKG@.GearData.num(d, "lvU", 0);
  String lu = @PKG@.GearLL.newUid();
  if (!journal(pk, P, k, lu, mode, id)) return false;
  crash(1);
  @BD@ nd = llDoc(d, id, u, pk, lu, false);
  if (!put(c, slot, x, nd, u)) {
    @PKG@.GearLog.line("LL-MARK-FAILED " + u + " " + pk + " " + K + " " + id + " @" + @PKG@.GearForge.where(s, slot) + " (the next sweep drops the journal)");
    return false;
  }
  crash(2);
  if (!commit(pk, P, k, lu, id, false, "repick".equals(mode) ? K + ".repick" : null, "1", !"mark".equals(mode))) @PKG@.Gear.warn("lifelong: the commit of " + K + " " + lu + " could not be written - the next sweep finishes it");
  crash(3);
  int after = @PKG@.GearStamp.countId(all, id);
  if (after != before) @PKG@.Gear.warn("LIFELONG COUNT MISMATCH " + id + ": " + before + " before, " + after + " after (mark)");
  N[2] = N[2] + 1L;
  int nlv = @PKG@.GearLevel.level(id, nd);
  @PKG@.GearLog.line("LL-" + ("repick".equals(mode) ? "REPICK " : "MARK ") + u + " " + pk + " " + K + " " + lu + " " + id + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)] + " lv" + nlv + " (was lv" + olv + ", bought lvU " + olu + ") [" + @PKG@.GearView.modSummary(nd) + "] @" + @PKG@.GearForge.where(s, slot) + " undo: " + undo);
  if (olu > 0 || olv > nlv) tellOnce(pr, "lvu" + k, "Your " + K + " was Lv " + olv + (olu > 0 ? " (" + olu + " of it bought with coins)" : "") + ". Lifelong tools follow your " + @PKG@.GearLL.KSKILL[k] + " level, so it is Lv " + nlv + " now - an admin has the record.", 5000L);
  return true;
}""")
# give a NEW lifelong tool (mode "give" = the migration's Crude Common one, "reclaim" = /pickaxe ...): 1 given, 0 no free slot, -1 failed
M(glf, r"""
public static int give(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String id, String mode) {
  java.util.UUID u = pr.getUuid();
  String K = @PKG@.GearLL.KIND[k];
  @IC@[] gv = new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() };
  Object[] fe = @PKG@.GearStamp.firstEmpty(gv, null, -1);
  if (fe == null) return 0;
  @IC@ c = (@IC@) fe[0];
  int slot = ((Integer) fe[1]).intValue();
  String pend = P.getProperty(K + ".pend");
  String lu = pend != null && "give".equals(mode) && "give".equals(P.getProperty(K + ".pendMode")) ? pend : @PKG@.GearLL.newUid();
  boolean rp = "reclaim".equals(mode);
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int before = @PKG@.GearStamp.countId(all, id);
  if (!journal(pk, P, k, lu, mode, id)) return -1;
  crash(4);
  @BD@ nd = llDoc(null, id, u, pk, lu, rp);
  Object tx = null;
  Throwable ex = null;
  try { tx = c.setItemStackForSlot((short) slot, @PKG@.GearData.put(new @IS@(id, 1), nd, u)); } catch (Throwable t) { ex = t; }
  @IS@ now = c.getItemStack((short) slot);
  boolean ok = ex == null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) && now != null && !now.isEmpty() && id.equals(now.getItemId());
  if (!ok) {
    @PKG@.GearLog.line("LL-GIVE-FAILED " + u + " " + pk + " " + K + " " + id + " (" + (ex != null ? String.valueOf(ex) : "the inventory refused it") + ")");
    return -1;
  }
  @PKG@.GearStamp.selfNote(u, tx);
  crash(5);
  if (!commit(pk, P, k, lu, id, rp, rp ? K + ".reclaimAt" : null, String.valueOf(System.currentTimeMillis()), !"give".equals(mode))) @PKG@.Gear.warn("lifelong: the commit of " + K + " " + lu + " could not be written - the next sweep finishes it");
  crash(6);
  int after = @PKG@.GearStamp.countId(all, id);
  if (after != before + 1) @PKG@.Gear.warn("LIFELONG COUNT MISMATCH " + id + ": " + before + " before, " + after + " after (give)");
  if (rp) N[7] = N[7] + 1L;
  else N[3] = N[3] + 1L;
  @PKG@.GearLog.line("LL-" + (rp ? "RECLAIM " : "GIVE ") + u + " " + pk + " " + K + " " + lu + " " + id + " lv" + @PKG@.GearLevel.level(id, nd));
  return 1;
}""")
# fix round (critic A3): the migration picks from the inventory only (a Requip / chest tool cannot be written from here) - a tool of a
# lifelong kind sitting in Requip is named once, with the way to pick it (/lifelong, repickDays)
M(glf, r"""
public static String rqKinds(java.util.UUID u) {
  boolean[] has = new boolean[4];
  java.util.ArrayList l = @PKG@.GearSmith.rqList(u, "items");
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    int k = @PKG@.GearLL.kOf((String) e[1]);
    if (k >= 0) has[k] = true;
  }
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < 4; k++) if (has[k]) { if (sb.length() > 0) sb.append(", "); sb.append(@PKG@.GearLL.KIND[k]); }
  return sb.toString();
}""")
M(glf, r"""
public static void notice(@PR@ pr) {
  try {
    pr.sendMessage(@MSG@.raw("[Gear] Lifelong tools: you keep ONE pickaxe, hatchet, hoe and sickle for life now. They level with your skills (1 Upgrade Point per level: /toolpoints) and tier up on the Anvil (/smithing). Lost one? /pickaxe, /hatchet, /hoe or /sickle. Wrong tool picked? Hold the right one and type /lifelong (once per kind).").color(@PKG@.GearDefs.C_LABEL));
    // fix round 2 (design critic 6): only the inventory was checked - say so for chests, the Void and the Vault too
    pr.sendMessage(@MSG@.raw("[Gear] Only your inventory was checked. Is a better tool in a chest, the Void or your Vault? Take it out, hold it and type /lifelong (within " + @PKG@.GearCfg.LL_REPICK + " days).").color(@PKG@.GearDefs.C_GOLD));
    String rq = rqKinds(pr.getUuid());
    if (rq.length() > 0) pr.sendMessage(@MSG@.raw("[Gear] Your Requip holds a " + rq + " that was not checked. If it is better, take it out, hold it and type /lifelong (within " + @PKG@.GearCfg.LL_REPICK + " days).").color(@PKG@.GearDefs.C_GOLD));
  } catch (Throwable t) { }
}""")
# THE ONE-TIME MIGRATION (also a new profile's first join): per kind adopt / mark the best / give a Crude Common one; migrated=1 once all four.
# Returns true when the registry changed in memory (the sweep saves it once - fix round, engine critic 3)
M(glf, r"""
public static boolean migrate(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  int done = 0;
  boolean ch = false;          // fix round: true = the registry changed in memory (the sweep's one save writes it)
  for (int k = 0; k < 4; k++) {
    String K = @PKG@.GearLL.KIND[k];
    String cu = P.getProperty(K + ".uid");
    if (cu != null && !"1".equals(P.getProperty(K + ".seen")) && P.getProperty(K + ".pend") == null && find(inv, pk, cu) == null) {
      // the commit reached the disk but the item never did (a crash before the engine saved the inventory): this kind starts over
      P.remove(K + ".uid");
      P.remove(K + ".id");
      P.remove(K + ".rp");
      @PKG@.GearLog.line("LL-REDO " + u + " " + pk + " " + K + " " + cu + " (committed, never seen, not in the inventory)");
      cu = null;
      ch = true;
    }
    if (cu != null) { done++; continue; }
    int[] ad = findKind(inv, pk, k);
    if (ad != null) {
      @IS@ x = @PKG@.GearStamp.at(inv, ad[0], ad[1]);
      @BD@ d = docOf(x);
      commit(pk, P, k, @PKG@.GearLL.uid(d), x.getItemId(), @PKG@.GearLL.isRp(d), null, null, false);
      N[10] = N[10] + 1L;
      @PKG@.GearLog.line("LL-ADOPT " + u + " " + pk + " " + K + " " + @PKG@.GearLL.uid(d) + " " + x.getItemId());
      done++;
      ch = true;
      continue;
    }
    int[] b = best(inv, k);
    if (b != null) { if (mark(pr, inv, pk, P, k, b[0], b[1], "mark")) { done++; ch = true; } continue; }
    int g = give(pr, inv, pk, P, k, @PKG@.GearLL.KCRUDE[k], "give");
    if (g == 1) { done++; ch = true; }
    else if (g == 0) tellOnce(pr, "room" + k, "Your lifelong " + K + " is waiting - free one inventory slot and it arrives.", 60000L);
  }
  if (done < 4) return ch;
  P.setProperty("migrated", "1");
  P.setProperty("migratedAt", String.valueOf(System.currentTimeMillis()));
  // fix round (engine critic 3): no write here - the sweep's one save (pass) carries migrated=1 + every deferred commit; if that write
  // fails the next restart re-runs this (every kind is then adopted from its uid: nothing is given twice)
  @PKG@.GearLog.line("LL-MIGRATED " + u + " " + pk);
  notice(pr);
  return true;
}""")
M(glf, r"""
public static void remove(@IC@ c, int i, @IS@ x, java.util.UUID u, String why) {
  try {
    Object tx = c.removeItemStackFromSlot((short) i);
    if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) return;
    @PKG@.GearStamp.selfNote(u, tx);
  } catch (Throwable t) { @PKG@.Gear.warn("lifelong: a stale copy could not be removed: " + t); return; }
  N[6] = N[6] + 1L;
  @PKG@.GearLog.line("LL-REMOVE " + u + " " + x.getItemId() + " " + @PKG@.GearMerge.json(x) + " (" + why + ")");
}""")
M(glf, r"""
public static boolean demote(@IC@ c, int i, @IS@ x, @BD@ d, java.util.UUID u) {
  @BD@ nd = d.clone();
  nd.remove("ll");
  nd.remove("lu");
  nd.remove("lo");
  nd.remove("lrp");
  nd.remove("lrpT");
  if (!put(c, i, x, nd, u)) return false;
  N[5] = N[5] + 1L;
  @PKG@.GearLog.line("LL-DEMOTE " + u + " " + x.getItemId() + " " + @PKG@.GearLL.uid(d) + " (the tool /lifelong re-picked away from - a plain tool again)");
  return true;
}""")
# fix round 2 (safety critic 2): an older lifelong stack of yours is RETIRED, never turned plain (a plain rolled tool could be sold / used as a
# second tool - "you cant make more"): lrt=1, still lifelong (never on the market), breaks nothing (GearLL.hit), may be dropped (useless to
# anyone), swapped back with /lifelong
M(glf, r"""
public static boolean retire(@IC@ c, int i, @IS@ x, @BD@ d, java.util.UUID u, String why) {
  @BD@ nd = d.clone();
  nd.put("lrt", new org.bson.BsonInt32(1));
  nd.remove("lrp");
  nd.remove("lrpT");
  if (!put(c, i, x, nd, u)) return false;
  N[12] = N[12] + 1L;
  @PKG@.GearLog.line("LL-RETIRE " + u + " " + x.getItemId() + " " + @PKG@.GearLL.uid(d) + " (" + why + ")");
  return true;
}""")
# the original came back while a /pickaxe replacement is the lifelong one: the registry names the original again (no item is written here;
# the replacement goes at the next look); false = the registry could not be written (nothing changed)
M(glf, r"""
public static boolean restore(@PR@ pr, String pk, java.util.Properties P, int k, String lu, String id) {
  String K = @PKG@.GearLL.KIND[k];
  String ou = P.getProperty(K + ".uid");
  String orp = P.getProperty(K + ".rp");
  String oid = P.getProperty(K + ".id");
  String oinv = P.getProperty(K + ".inv");
  P.setProperty(K + ".uid", lu);
  P.setProperty(K + ".rp", "0");
  P.setProperty(K + ".id", id);
  P.remove(K + ".inv");
  if (!@PKG@.GearLL.save(pk, P)) {
    if (oinv != null) P.setProperty(K + ".inv", oinv);
    if (ou == null) P.remove(K + ".uid"); else P.setProperty(K + ".uid", ou);
    if (orp == null) P.remove(K + ".rp"); else P.setProperty(K + ".rp", orp);
    if (oid == null) P.remove(K + ".id"); else P.setProperty(K + ".id", oid);
    return false;
  }
  N[4] = N[4] + 1L;
  @PKG@.GearLog.line("LL-RESTORE " + pr.getUuid() + " " + pk + " " + K + " " + lu + " " + id + " (was " + ou + ")");
  tellOnce(pr, "back" + k, "Your old lifelong " + K + " is back - the replacement from /" + K + " is gone.", 5000L);
  return true;
}""")
# fix round (critic A2): an original (or an invested older replacement) turned up while the CURRENT replacement is invested (tiered up /
# reforged): nothing is thrown away - that stack turns plain (keeps rarity + rolls), the replacement becomes the lifelong tool for good
# (rp=0); true = the registry changed (pass saves)
M(glf, r"""
public static boolean settle(@PR@ pr, java.util.Properties P, int k, @IC@ c, int i, @IS@ x, @BD@ d) {
  String K = @PKG@.GearLL.KIND[k];
  if (!retire(c, i, x, d, pr.getUuid(), "turned up after its replacement was upgraded")) return false;          // fix round 2: retired, not plain
  P.setProperty(K + ".rp", "0");
  P.remove(K + ".inv");
  @PKG@.GearLog.line("LL-SETTLE " + pr.getUuid() + " " + K + " " + P.getProperty(K + ".uid") + " stays (tiered up / reforged); " + x.getItemId() + " " + @PKG@.GearLL.uid(d) + " is retired now");
  tellOnce(pr, "settle" + k, "Your old " + K + " turned up, but you upgraded its replacement - that one stays your lifelong " + K + ". The old one is retired (it keeps its rolls but breaks nothing): hold it and type /lifelong to swap them.", 5000L);
  return true;
}""")
# the current lifelong stack: its level follows the skill; the registry remembers its item id (the tier /pickaxe gives back) and that it
# was SEEN in the inventory (the migration redoes a kind whose committed item never showed up - a crash before the engine saved the
# inventory); true = the registry changed (pass saves once)
M(glf, r"""
public static boolean keep(@IC@ c, int i, @IS@ x, @BD@ d, int k, java.util.UUID u, String pk, java.util.Properties P) {
  String id = x.getItemId();
  String K = @PKG@.GearLL.KIND[k];
  int lv = @PKG@.GearLL.levelFor(u, id);
  boolean lw = lv >= 1 && @PKG@.GearData.num(d, "lvl", -1) != lv;
  boolean rw = @PKG@.GearLL.isRp(d) && "0".equals(P.getProperty(K + ".rp"));          // fix round: a replacement that became THE tool
  boolean tw = @PKG@.GearLL.isRt(d);          // fix round 2: swapped back with /lifelong (or a crash between the swap and this look)
  if (lw || rw || tw) {
    @BD@ nd = d.clone();
    if (lw) nd.put("lvl", new org.bson.BsonInt32(lv));
    if (rw) { nd.remove("lrp"); nd.remove("lrpT"); }
    if (tw) nd.remove("lrt");
    if (put(c, i, x, nd, u) && lw) N[1] = N[1] + 1L;
  }
  boolean ch = false;
  if ("1".equals(P.getProperty(K + ".rp")) && !"1".equals(P.getProperty(K + ".inv")) && @PKG@.GearLL.invested(id, d)) { P.setProperty(K + ".inv", "1"); ch = true; }
  if (!id.equals(P.getProperty(K + ".id"))) { P.setProperty(K + ".id", id); ch = true; }
  if (!"1".equals(P.getProperty(K + ".seen"))) { P.setProperty(K + ".seen", "1"); ch = true; }
  return ch;
}""")
# someone else's lifelong tool in this inventory: only a /pickaxe REPLACEMENT that is no longer its owner's lifelong one goes (a free copy)
M(glf, r"""
public static void foreign(@IC@ c, int i, @IS@ x, @BD@ d, int k, java.util.UUID u, String lo, String lu) {
  if (!@PKG@.GearLL.isRp(d) || lo == null || lo.length() == 0 || @PKG@.GearLL.invested(x.getItemId(), d)) return;
  java.util.Properties P2 = @PKG@.GearLL.reg(lo);
  if (@PKG@.GearLL.bad(P2)) return;
  String cur = P2.getProperty(@PKG@.GearLL.KIND[k] + ".uid");
  if (cur != null && !cur.equals(lu)) remove(c, i, x, u, "a replacement " + @PKG@.GearLL.KIND[k] + " of profile " + lo + " that is not its lifelong one any more");
}""")
# one look over the inventory: level sync, the registry's item id, returned originals, stale copies, others' stale replacements
M(glf, r"""
public static void pass(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, boolean dirty0) {
  java.util.UUID u = pr.getUuid();
  boolean again = true;
  boolean dirty = dirty0;
  int rounds = 0;
  while (again && rounds < 2) {
    again = false;
    rounds++;
    java.util.HashSet one = new java.util.HashSet();          // the current uids met in this round (a 2nd stack with one = a copy)
    for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
      @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
      if (c == null) continue;
      for (int i = 0; i < c.getCapacity(); i++) {
        @IS@ x = c.getItemStack((short) i);
        if (x == null || x.isEmpty()) continue;
        String id = x.getItemId();
        int k = @PKG@.GearLL.kOf(id);
        if (k < 0) continue;
        @BD@ d = docOf(x);
        if (!@PKG@.GearLL.isLL(d)) continue;
        String lo = @PKG@.GearLL.owner(d);
        String lu = @PKG@.GearLL.uid(d);
        String K = @PKG@.GearLL.KIND[k];
        if (!pk.equals(lo)) { foreign(c, i, x, d, k, u, lo, lu); continue; }
        String cur = P.getProperty(K + ".uid");
        if (lu.equals(cur)) {
          if (!one.add(lu)) { remove(c, i, x, u, "a second stack of your lifelong " + K + " (" + lu + ") - only one exists"); continue; }
          if (keep(c, i, x, d, k, u, pk, P)) dirty = true;
          continue;
        }
        if (lu.equals(P.getProperty(K + ".pend"))) continue;
        if (@PKG@.GearLL.isRt(d)) continue;          // fix round 2: a retired one stays as it is until /lifelong swaps it back
        // fix round (critic A2): a replacement the player tiered up / reforged counts like an original - never removed
        boolean rpS = @PKG@.GearLL.isRp(d);
        if (rpS && !@PKG@.GearLL.invested(id, d)) { remove(c, i, x, u, "a replacement " + K + " - the lifelong one is back"); continue; }
        boolean curRp = "1".equals(P.getProperty(K + ".rp"));
        if (cur == null || (curRp && !"1".equals(P.getProperty(K + ".inv")))) { if (restore(pr, pk, P, k, lu, id)) again = true; continue; }
        if (curRp) { if (settle(pr, P, k, c, i, x, d)) dirty = true; continue; }
        // fix round 2 (safety critic 2): only the tool /lifelong re-picked away from turns plain (both were plain tools before the
        // migration); any other older lifelong stack is retired - never a second plain rolled tool for free
        if (lu.equals(P.getProperty(K + ".free"))) { if (demote(c, i, x, d, u)) { P.remove(K + ".free"); dirty = true; } continue; }
        retire(c, i, x, d, u, "an older lifelong " + K + " - the current one is " + cur);
      }
    }
  }
  if (dirty) @PKG@.GearLL.save(pk, P);
}""")
# THE SWEEP (world thread; join = force, every stamp scan = at most every 400 ms): journals, the migration (once), the look
M(glf, r"""
public static void sweep0(@PR@ pr, @INV@ inv, boolean force) {
  if (!@PKG@.GearCfg.LL_ON || pr == null || inv == null) return;
  java.util.UUID u = pr.getUuid();
  if (@PKG@.Gear.busy(u)) return;
  long now = System.currentTimeMillis();
  if (!force) {
    Object l = @PKG@.GearLL.LAST.get(u);
    if (l instanceof Long && now >= ((Long) l).longValue() && now - ((Long) l).longValue() < 400L) return;
  }
  @PKG@.GearLL.LAST.put(u, Long.valueOf(now));
  String pk = @PKG@.Gear.pkey(u);
  if (!force && @PKG@.GearLL.failing(pk)) return;          // fix round 2 (safety critic 4): a failed registry write waits 30 s here
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return;
  recover(pr, inv, pk, P);
  boolean mg = false;
  if (!"1".equals(P.getProperty("migrated"))) mg = migrate(pr, inv, pk, P);
  pass(pr, inv, pk, P, mg);          // fix round: one save carries the migration's deferred commits + migrated=1
  N[0] = N[0] + 1L;
}""")
M(glf, r"""
public static void sweep(@PR@ pr, @INV@ inv, boolean force) {
  try { sweep0(pr, inv, force); } catch (Throwable t) { @PKG@.Gear.warnOnce("llsweep", "the lifelong tool look failed: " + t); }
}""")
M(glf, r"""
public static int[] held(@INV@ inv) {
  if (inv == null) return null;
  try {
    if (inv.usingToolsItem()) return new int[] { 5, (int) inv.getActiveToolsSlot() };
    return new int[] { 0, (int) inv.getActiveHotbarSlot() };
  } catch (Throwable t) { return null; }
}""")
# the lifelong uid lu in this player's Requip (wardrobe:fn:list, both spaces; no SkyyWardrobe = false)
M(glf, r"""
public static boolean inRequip(java.util.UUID u, String lu) {
  String[] sp = new String[] { "armor", "items" };
  for (int k = 0; k < sp.length; k++) {
    java.util.ArrayList l = @PKG@.GearSmith.rqList(u, sp[k]);
    for (int i = 0; i < l.size(); i++) {
      Object[] e = (Object[]) l.get(i);
      if (!(e[2] instanceof @BD@)) continue;
      @BD@ d = null;
      try { d = @PKG@.GearData.gearDoc((@BD@) e[2]); } catch (Throwable t) { d = null; }
      if (@PKG@.GearLL.isLL(d) && lu.equals(@PKG@.GearLL.uid(d))) return true;
    }
  }
  return false;
}""")
# /pickaxe /hatchet /hoe /sickle (world thread): "+" given, "-" refused (why). The tier: lifelong.reclaimTier off (the default since fix round
# 2) = the tier you had; on (Skyy G2's literal reading) = the first tier whose band holds your skill level, never below the one you had
M(glf, r"""
public static String reclaim(@PR@ pr, @PLA@ p, int k) {
  if (!@PKG@.GearCfg.LL_ON) return "-Lifelong tools are switched off on this server.";
  if (pr == null || p == null || k < 0 || k > 3) return "-No player.";
  java.util.UUID u = pr.getUuid();
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  @INV@ inv = p.getInventory();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now - an admin can check the server log.";
  sweep0(pr, inv, true);
  String K = @PKG@.GearLL.KIND[k];
  String cur = P.getProperty(K + ".uid");
  if (cur == null) return "-Your lifelong " + K + " is still waiting for a free inventory slot - make room and it arrives.";
  int[] at = find(inv, pk, cur);
  if (at != null) return "-You still have your lifelong " + K + " (" + @PKG@.GearForge.where(at[0], at[1]) + ").";
  if (inRequip(u, cur)) return "-Your lifelong " + K + " is in your Requip - take it out there.";
  long now = System.currentTimeMillis();
  long last = @PKG@.GearLL.getl(P, K + ".reclaimAt", 0L);
  long wait = (long) @PKG@.GearCfg.LL_RECLAIM * 1000L - (now - last);
  if (last > 0L && now >= last && wait > 0L) return "-You can get a new " + K + " in " + ((wait + 999L) / 1000L) + " s.";
  String id = P.getProperty(K + ".id");
  if (id == null || @PKG@.Gear.item(id) == null || @PKG@.GearLL.kOf(id) != k) id = @PKG@.GearLL.KCRUDE[k];
  if (@PKG@.GearCfg.LL_RTIER) id = @PKG@.GearLL.tierFor(u, k, id);          // fix round: Skyy G2 "lvl 20 mining ... a lvl 20 common iron pickaxe"
  int g = give(pr, inv, pk, P, k, id, "reclaim");
  if (g == 0) return "-No room - free one inventory slot and try again.";
  if (g < 0) return "-That did not work - nothing was given. Try again in a moment.";
  int lv = @PKG@.GearLL.levelFor(u, id);
  return "+Here is a new Common " + @PKG@.Gear.itemName(id) + (lv >= 1 ? " [Lv " + lv + "]" : "") + ". If your old one turns up again, it becomes your lifelong " + K + " again and this one disappears.";
}""")
# fix round 2 (safety critic 2): /lifelong on your own RETIRED tool swaps it back (any time): ONE registry write names it; the sweep then
# un-retires it (keep) and retires the old current one wherever it next turns up. Never two working tools, never a plain one
M(glf, r"""
public static String swap(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String lu, String id) {
  String K = @PKG@.GearLL.KIND[k];
  String ou = P.getProperty(K + ".uid");
  String orp = P.getProperty(K + ".rp");
  String oid = P.getProperty(K + ".id");
  String oinv = P.getProperty(K + ".inv");
  P.setProperty(K + ".uid", lu);
  P.setProperty(K + ".id", id);
  P.setProperty(K + ".rp", "0");
  P.remove(K + ".inv");
  if (!@PKG@.GearLL.save(pk, P)) {
    if (ou == null) P.remove(K + ".uid"); else P.setProperty(K + ".uid", ou);
    if (oid == null) P.remove(K + ".id"); else P.setProperty(K + ".id", oid);
    if (orp == null) P.remove(K + ".rp"); else P.setProperty(K + ".rp", orp);
    if (oinv != null) P.setProperty(K + ".inv", oinv);
    return "-That did not work - nothing changed. Try again in a moment.";
  }
  N[13] = N[13] + 1L;
  @PKG@.GearLog.line("LL-SWAP " + pr.getUuid() + " " + pk + " " + K + " " + lu + " " + id + " (was " + ou + " - retired now)");
  sweep0(pr, inv, true);
  return "+" + @PKG@.Gear.itemName(id) + " is your lifelong " + K + " again. The other one is retired now (swap back the same way).";
}""")
# /lifelong: make the tool in your hand the lifelong one (once per kind, lifelong.repickDays after the migration)
M(glf, r"""
public static String repick(@PR@ pr, @PLA@ p) {
  if (!@PKG@.GearCfg.LL_ON) return "-Lifelong tools are switched off on this server.";
  java.util.UUID u = pr.getUuid();
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  @INV@ inv = p.getInventory();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now - an admin can check the server log.";
  sweep0(pr, inv, true);
  int[] h = held(inv);
  @IS@ x = h == null ? null : @PKG@.GearStamp.at(inv, h[0], h[1]);
  if (x == null || x.isEmpty()) return "-Hold the tool you want as your lifelong one, then type /lifelong.";
  String id = x.getItemId();
  int k = @PKG@.GearLL.kOf(id);
  if (k < 0) return "-Only a pickaxe, hatchet, hoe or sickle can be a lifelong tool.";
  String K = @PKG@.GearLL.KIND[k];
  if (x.getQuantity() != 1) return "-That is a stack - hold a single tool.";
  int st = @PKG@.GearData.state(x.getMetadata());
  if (st == 3 || st == 4) return "-The gear data on that tool cannot be read.";
  @BD@ d = null;
  try { d = @PKG@.GearData.effective(id, x.getMetadata()); } catch (Throwable t) { d = null; }
  if (@PKG@.GearLL.isLL(d)) {
    if (!pk.equals(@PKG@.GearLL.owner(d))) return "-That is another player's lifelong tool.";
    String hu = @PKG@.GearLL.uid(d);
    if (hu.equals(P.getProperty(K + ".uid"))) return "-That already is your lifelong " + K + ".";
    if (!@PKG@.GearLL.isRt(d)) return "-That " + K + " is still being sorted out - try again in a moment.";
    return swap(pr, inv, pk, P, k, hu, id);          // fix round 2: your retired one back (any time, no limit: one works at a time)
  }
  if (d != null && !@PKG@.GearData.identified(d)) return "-Identify that tool first.";
  if (d != null && @PKG@.GearData.rarity(d) > 4) return "-That tool cannot be a lifelong tool.";
  if (!"1".equals(P.getProperty("migrated"))) return "-Your lifelong tools are still being set up - try again in a moment.";
  if ("1".equals(P.getProperty(K + ".repick"))) return "-You already re-picked your lifelong " + K + ".";
  long at = @PKG@.GearLL.getl(P, "migratedAt", 0L);
  long win = (long) @PKG@.GearCfg.LL_REPICK * 86400000L;
  if (win <= 0L || System.currentTimeMillis() - at > win) return "-Re-picking was open for " + @PKG@.GearCfg.LL_REPICK + " days after your first join with lifelong tools.";
  String fu = P.getProperty(K + ".uid");          // fix round 2: the one re-picked away from turns plain at the next look (pass), no other
  if (fu != null) P.setProperty(K + ".free", fu);
  if (!mark(pr, inv, pk, P, k, h[0], h[1], "repick")) { P.remove(K + ".free"); return "-That did not work - nothing changed. Try again in a moment."; }
  sweep0(pr, inv, true);
  return "+" + @PKG@.Gear.itemName(id) + " is your lifelong " + K + " now. The old one became a plain tool.";
}""")
# a perk level (the Tools page): "+" bought, "-" why not
M(glf, r"""
public static String buy(java.util.UUID u, int k, int p) {
  if (!@PKG@.GearCfg.LL_ON) return "-Lifelong tools are switched off on this server.";
  if (u == null || k < 0 || k > 3 || p < 0 || p >= @PKG@.GearLL.PK.length) return "-Pick a tool first.";
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now.";
  String K = @PKG@.GearLL.KIND[k];
  String nm = @PKG@.GearLL.PKN[p];
  if (!@PKG@.GearLL.perkFor(k, p)) return "-" + nm + " is not an upgrade for a " + K + ".";
  if (!@PKG@.GearLL.perkOn(p)) return "-" + nm + " comes with the next SkyyTrees update - not yet.";
  int lv = @PKG@.GearLL.perkOf(P, k, p);
  if (lv >= @PKG@.GearLL.PKMAX[p]) return "-" + nm + " is already at its top level (" + @PKG@.GearLL.PKMAX[p] + ").";
  int need = @PKG@.GearLL.pkNeed(p, lv + 1);
  String id = P.getProperty(K + ".id");
  int t = id == null ? 0 : @PKG@.GearLL.tier(id);
  if (t < need) return "-" + nm + " " + (lv + 1) + " needs " + @PKG@.GearLL.an(@PKG@.GearLL.tname(need)) + " " + K + " or better - tier yours up on the Anvil.";
  int cost = @PKG@.GearLL.pkCost(p, lv + 1);
  int fr = @PKG@.GearLL.free(u, P, k);
  if (fr < cost) return "-" + nm + " " + (lv + 1) + " costs " + cost + " point" + (cost == 1 ? "" : "s") + " - you have " + fr + " free.";
  String key = K + ".up." + @PKG@.GearLL.PK[p];
  P.setProperty(key, String.valueOf(lv + 1));
  if (!@PKG@.GearLL.save(pk, P)) {
    if (lv == 0) P.remove(key); else P.setProperty(key, String.valueOf(lv));
    return "-Your choice could not be saved - nothing changed.";
  }
  @PKG@.GearTool.LAST.remove(u);
  @PKG@.GearGate.bump(u);
  N[8] = N[8] + 1L;
  @PKG@.GearLog.line("LL-PERK " + u + " " + pk + " " + K + " " + @PKG@.GearLL.PK[p] + " " + lv + " -> " + (lv + 1) + " cost " + cost);
  return "+" + nm + " is level " + (lv + 1) + " now (" + (fr - cost) + " point" + (fr - cost == 1 ? "" : "s") + " left).";
}""")
# the points reset for coins (Skyy 2026-10-13 G6 "yes, for coins. costs more every time."): coins first, refund when the write fails
M(glf, r"""
public static String reset(java.util.UUID u, String who, int k) {
  if (!@PKG@.GearCfg.LL_ON) return "-Lifelong tools are switched off on this server.";
  if (u == null || k < 0 || k > 3) return "-Pick a tool first.";
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now.";
  String K = @PKG@.GearLL.KIND[k];
  int sp = @PKG@.GearLL.spent(P, k);
  if (sp <= 0) return "-No points are spent on your " + K + ".";
  long cost = @PKG@.GearLL.resetCost(P, k);
  if (cost > 0L) {
    int t = @PKG@.GearForge.take(u, cost);
    if (t < 0) return "-Coins are not available right now (SkyyCoins) - nothing changed.";
    if (t == 0) { long have = @PKG@.GearForge.purse(u); return "-A reset costs " + @PKG@.Gear.fmt(cost) + " coins" + (have >= 0L ? " - you have " + @PKG@.Gear.fmt(have) : "") + "."; }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " lifelong reset " + K);
  }
  java.util.Properties old = new java.util.Properties();
  for (int p = 0; p < @PKG@.GearLL.PK.length; p++) {
    String key = K + ".up." + @PKG@.GearLL.PK[p];
    String v = P.getProperty(key);
    if (v != null) { old.setProperty(key, v); P.remove(key); }
  }
  String rk = K + ".resets";
  String ov = P.getProperty(rk);
  P.setProperty(rk, String.valueOf(@PKG@.GearLL.getl(P, rk, 0L) + 1L));
  if (!@PKG@.GearLL.save(pk, P)) {
    java.util.Iterator it = old.keySet().iterator();
    while (it.hasNext()) { String key2 = (String) it.next(); P.setProperty(key2, old.getProperty(key2)); }
    if (ov == null) P.remove(rk); else P.setProperty(rk, ov);
    boolean back = cost <= 0L || @PKG@.GearForge.refund(u, cost);
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " lifelong reset " + K);
    return back ? "-The reset could not be saved - nothing changed" + (cost > 0L ? " and your coins were refunded." : ".") : "-The reset could not be saved and the refund failed - an admin can find it in the server log.";
  }
  @PKG@.GearTool.LAST.remove(u);
  @PKG@.GearGate.bump(u);
  N[9] = N[9] + 1L;
  @PKG@.GearLog.line("LL-RESET " + who + " " + u + " " + pk + " " + K + " points " + sp + " cost " + cost + " resets " + P.getProperty(rk));
  return "+All " + sp + " points of your " + K + " are back" + (cost > 0L ? " (-" + @PKG@.Gear.fmt(cost) + " coins)" : "") + ". The next reset costs more.";
}""")
M(glf, r"""
public static String counters() {
  return "sweeps " + N[0] + ", levels written " + N[1] + ", marked " + N[2] + ", given " + N[3] + ", restored " + N[4] + ", demoted " + N[5] + ", copies removed " + N[6] + ", /pickaxe " + N[7] + ", perks " + N[8] + ", resets " + N[9] + ", adopted " + N[10] + ", journals finished " + N[11] + ", retired " + N[12] + ", swapped back " + N[13];
}""")
'''

LIFE_C = r'''
# ---- LifePage: the Tools tab of /smithing (/toolpoints) - the Anvil's frame + tab row; left your four tools, right the picked tool's points
for _f in ("public int sel;", "public String info;", "public long lastClick;", "public String epoch;", "public int armK;", "public long armAt;"):
    F(lpg, _f)
C(lpg, r"""
public LifePage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.sel = 0;
  this.info = "";
  this.lastClick = 0L;
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
  this.armK = -1;
  this.armAt = 0L;
}""")
# the item id shown for kind k: the stack on you, else the registry's last id, else the Crude one
M(lpg, r"""
public static String idOf(@IS@ x, java.util.Properties P, int k) {
  if (x != null && !x.isEmpty()) return x.getItemId();
  String id = P == null ? null : P.getProperty(@PKG@.GearLL.KIND[k] + ".id");
  if (id != null && @PKG@.Gear.item(id) != null) return id;
  return @PKG@.GearLL.KCRUDE[k];
}""")
M(lpg, r"""
public void row(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P, int k) {
  String K = @PKG@.GearLL.KIND[k];
  String cur = P.getProperty(K + ".uid");
  int[] at = null;
  if (cur != null) at = @PKG@.GearLife.find(inv, pk, cur);
  @IS@ x = at == null ? null : @PKG@.GearStamp.at(inv, at[0], at[1]);
  @BD@ d = x == null ? null : @PKG@.GearLife.docOf(x);
  String id = idOf(x, P, k);
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  String rid = "#SkyyGLRow" + k;
  b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 130); LayoutMode: Left; Padding: (Full: 8); " + @PKG@.GearUi.rowStyle(k == this.sel) + " " + @PKG@.GearUi.cell(80, id) + " Group { Anchor: (Width: 14); } Group { Anchor: (Width: 340); LayoutMode: Top; Label #SkyyGLRowN" + k + " { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); } Label #SkyyGLRowA" + k + " { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff(0.7), VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } Label #SkyyGLRowB" + k + " { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } }");
  b.set("#SkyyGLRowN" + k + ".Text", x == null ? @PKG@.GearLL.KNAME[k] + " - " + @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
  int h = @PKG@.GearLL.skill(u, k);
  int lv = @PKG@.GearLL.levelFor(u, id);
  String sk = @PKG@.GearLL.KSKILL[k] + (h >= 0 ? " " + h : "");
  b.set("#SkyyGLRowA" + k + ".Text", sk + " - tool Lv " + (lv >= 1 ? String.valueOf(lv) : "?") + " (" + @PKG@.GearLL.tname(@PKG@.GearLL.tier(id)) + " tops out at " + @PKG@.GearLL.cap(id) + ")");
  String w;
  if (cur == null) w = "Arrives when you have a free inventory slot";
  else if (x == null) w = "Not on you - in a chest or Requip? Lost: /" + K;
  else {
    int fr = @PKG@.GearLL.free(u, P, k);
    w = fr + " Upgrade Point" + (fr == 1 ? "" : "s") + " free";
  }
  b.set("#SkyyGLRowB" + k + ".Text", w);
  b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
  ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "sel:" + k));
}""")
M(lpg, r"""
public static String effect(int k, int p, int lv) {
  if (p == 0) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PSPD) + "% " + (k == 1 ? "Chopping" : "Mining") + " Power";
  if (p == 1) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PFORT) + " " + @PKG@.GearLL.KSKILL[k] + " Fortune";
  if (p == 2) return "+" + @PKG@.Gear.fnum((double) lv * @PKG@.GearCfg.LL_PWIS) + "% " + @PKG@.GearLL.KSKILL[k] + " XP";
  return "+" + lv + " " + @PKG@.GearLL.PKN[p] + " level" + (lv == 1 ? "" : "s");
}""")
M(lpg, r"""
public void perkRow(@UCB@ b, @UEB@ ev, java.util.UUID u, java.util.Properties P, int k, int p, String id) {
  int lv = @PKG@.GearLL.perkOf(P, k, p);
  int mx = @PKG@.GearLL.PKMAX[p];
  int t = @PKG@.GearLL.tier(id);
  boolean on = @PKG@.GearLL.perkOn(p);
  int cost = @PKG@.GearLL.pkCost(p, lv + 1);
  int need = @PKG@.GearLL.pkNeed(p, lv + 1);
  int fr = @PKG@.GearLL.free(u, P, k);
  String nx;
  boolean can = false;
  if (!on) nx = "Comes with the next SkyyTrees update";
  else if (lv >= mx) nx = "Top level";
  else if (t < need) nx = "Next level needs " + @PKG@.GearLL.an(@PKG@.GearLL.tname(need)) + " " + @PKG@.GearLL.KIND[k];
  else { nx = "Next: " + effect(k, p, lv + 1) + " for " + cost + " point" + (cost == 1 ? "" : "s"); can = fr >= cost; }
  String g = "#SkyyGPk" + p;
  b.appendInline("#SkyyGPanel", "Group " + g + " { Anchor: (Height: 76); LayoutMode: Left; Padding: (Full: 8); Background: #000000(0.25); Group { Anchor: (Width: 366); LayoutMode: Top; Label " + g + "N { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); } Label " + g + "D { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); } } Group { Anchor: (Width: 10); } TextButton " + g + "B { Anchor: (Width: 160, Height: 44); Text: \"" + (lv >= mx ? "Max" : "+1 (" + cost + " pt)") + "\"; " + @PKG@.GearUi.btn(can ? 0 : 3) + " } }");
  b.set(g + "N.Text", @PKG@.GearLL.PKN[p] + "   Lv " + lv + " / " + mx + (lv > 0 ? "   (" + effect(k, p, lv) + ")" : ""));
  b.set(g + "D.Text", nx);
  b.appendInline("#SkyyGPanel", "Group { Anchor: (Height: 6); }");
  ev.addEventBinding(@BT@.Activating, g + "B", @EVD@.of("a", "buy:" + p));
}""")
M(lpg, r"""
public void panel(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv, String pk, java.util.Properties P) {
  int k = this.sel < 0 || this.sel > 3 ? 0 : this.sel;
  String K = @PKG@.GearLL.KIND[k];
  String cur = P.getProperty(K + ".uid");
  int[] at = null;
  if (cur != null) at = @PKG@.GearLife.find(inv, pk, cur);
  @IS@ x = at == null ? null : @PKG@.GearStamp.at(inv, at[0], at[1]);
  String id = idOf(x, P, k);
  b.appendInline("#SkyyGMain", "Group #SkyyGPanel { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGPanel", "Label #SkyyGPTitle { Anchor: (Height: 36); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGPTitle.Text", "Your " + K + " - Upgrade Points");
  int fr = @PKG@.GearLL.free(u, P, k);
  int er = @PKG@.GearLL.earned(u, k);
  b.appendInline("#SkyyGPanel", "Label #SkyyGPSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGPSub.Text", fr + " of " + er + " points free - you get 1 point for every " + @PKG@.GearLL.KSKILL[k] + " level");
  b.appendInline("#SkyyGPanel", "Group { Anchor: (Height: 8); }");
  for (int p = 0; p < @PKG@.GearLL.PK.length; p++) if (@PKG@.GearLL.perkFor(k, p)) perkRow(b, ev, u, P, k, p, id);
  int sp = @PKG@.GearLL.spent(P, k);
  long rc = @PKG@.GearLL.resetCost(P, k);
  b.appendInline("#SkyyGPanel", "Label #SkyyGPReT { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGPReT.Text", sp > 0 ? "Reset: all " + sp + " spent points back for " + @PKG@.Gear.fmt(rc) + " coins (more each time)" : "Reset: nothing spent yet");
  boolean armed = this.armK == k && System.currentTimeMillis() - this.armAt < 8000L;
  b.appendInline("#SkyyGPanel", "TextButton #SkyyGPReset { Anchor: (Width: 300, Height: 44); Text: \"" + (armed ? "Click again to pay" : "Reset points") + "\"; " + @PKG@.GearUi.btn(sp > 0 ? 2 : 3) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGPReset", @EVD@.of("a", "reset"));
  String to = @PKG@.GearUp.next(id);
  String tl = "Tier: " + @PKG@.GearLL.tname(@PKG@.GearLL.tier(id)) + ". ";
  if (to == null) tl = tl + "Top tier for now.";
  else {
    Object[] co = @PKG@.GearUp.cost(id, to);
    StringBuilder sb = new StringBuilder();
    if (co != null) {
      String[] ci = (String[]) co[0];
      int[] cq = (int[]) co[1];
      for (int i = 0; i < ci.length; i++) { if (sb.length() > 0) sb.append(" + "); sb.append(cq[i]).append(' ').append(@PKG@.Gear.itemName(ci[i])); }
    }
    tl = tl + "Next: " + @PKG@.Gear.itemName(to) + " on the Anvil" + (sb.length() > 0 ? " for " + sb.toString() : "") + " (" + @PKG@.GearLL.KSKILL[k] + " " + @PKG@.GearLevel.band(to)[0] + ").";
  }
  b.appendInline("#SkyyGPanel", "Label #SkyyGPTier { Anchor: (Height: 52); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGPTier.Text", tl);
}""")
M(lpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ pl = null;
  try { pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { pl = null; }
  @INV@ inv = pl == null ? null : pl.getInventory();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 4, 1066, "Tools");
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 662); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyGMain", "Group #SkyyGList { Anchor: (Width: 470); LayoutMode: Top; }");
  b.appendInline("#SkyyGList", "Label #SkyyGLHead { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGLHead.Text", "Your lifelong tools");
  for (int k = 0; k < 4; k++) row(b, ev, u, inv, pk, P, k);
  b.appendInline("#SkyyGList", "Label #SkyyGLHelp { Anchor: (Height: 58); Text: \"\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGLHelp.Text", "They level with your skills and can't be dropped. Tier them up on the Anvil. Lost one? /pickaxe, /hatchet, /hoe or /sickle.");
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  b.appendInline("#SkyyGMain", @PKG@.GearUi.vsep());
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  panel(b, ev, u, inv, pk, P);
  long have = @PKG@.GearForge.purse(u);
  b.appendInline("#SkyyGBody", "Label #SkyyGFoot { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGFoot.Text", (have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)") + "   -   Tier up: Anvil tab   -   Wrong tool picked? Hold the right one and type /lifelong");
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
M(lpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.startsWith("mode:")) {
      String c = a.equals("mode:3") ? (@PKG@.GearCfg.SMITH_ON ? "smithing" : null) : (a.equals("mode:0") ? "reforge" : (a.equals("mode:1") && @PKG@.GearCfg.UP_ON ? "upgrade" : (a.equals("mode:2") && @PKG@.GearUi.multiTab() ? "multitool" : null)));
      if (c == null) { rebuild(); return; }
      try { @CMGR@.get().handleCommand(this.playerRef, c); } catch (Throwable t1) { @PKG@.Gear.warn("tools page: the " + c + " tab failed: " + t1); }
      return;
    }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t2) { }
      }
      close();
      return;
    }
    if (a.equals("refresh")) { this.info = ""; this.armK = -1; rebuild(); return; }
    java.util.UUID u = this.playerRef.getUuid();
    String ep = @PKG@.Gear.epoch(u);
    if (!ep.equals(this.epoch)) { this.epoch = ep; this.armK = -1; this.info = "-Your profile changed - check the page and click again."; rebuild(); return; }
    if (a.startsWith("sel:")) {
      int k = -1;
      try { k = Integer.parseInt(a.substring(4)); } catch (Throwable t3) { k = -1; }
      if (k >= 0 && k < 4) { this.sel = k; this.armK = -1; this.info = ""; }
      rebuild();
      return;
    }
    long now = System.currentTimeMillis();
    if (now - this.lastClick < 400L && now >= this.lastClick) return;
    this.lastClick = now;
    if (a.startsWith("buy:")) {
      int p = -1;
      try { p = Integer.parseInt(a.substring(4)); } catch (Throwable t4) { p = -1; }
      this.armK = -1;
      this.info = @PKG@.GearLife.buy(u, this.sel, p);
      rebuild();
      return;
    }
    if (a.equals("reset")) {
      if (this.armK == this.sel && now - this.armAt < 8000L) {
        this.armK = -1;
        this.info = @PKG@.GearLife.reset(u, this.playerRef.getUsername(), this.sel);
      } else {
        java.util.Properties P = @PKG@.GearLL.reg(@PKG@.Gear.pkey(u));
        if (@PKG@.GearLL.spent(P, this.sel) <= 0) this.info = "-No points are spent on your " + @PKG@.GearLL.KIND[this.sel] + ".";
        else {
          this.armK = this.sel;
          this.armAt = now;
          this.info = "=Click Reset again within 8 s to pay " + @PKG@.Gear.fmt(@PKG@.GearLL.resetCost(P, this.sel)) + " coins and get every point back.";
        }
      }
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.Gear.warn("tools page click failed: " + t); }
}""")
# ---- the commands (world thread; COMMAND RULES: every player command sets hytale:Adventurer)
C(llcmds[0], r"""
public PickaxeCmd() {
  super("pickaxe", "Lost your lifelong pickaxe? Get a new Common one at your level and tier (only when you have none)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
C(llcmds[1], r"""
public HatchetCmd() {
  super("hatchet", "Lost your lifelong hatchet? Get a new Common one at your level and tier (only when you have none)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
C(llcmds[2], r"""
public HoeCmd() {
  super("hoe", "Lost your lifelong hoe? Get a new Common one at your level and tier (only when you have none)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
C(llcmds[3], r"""
public SickleCmd() {
  super("sickle", "Lost your lifelong sickle? Get a new Common one at your level and tier (only when you have none)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
for _cc, (_n, _c, _k) in zip(llcmds, LL_CMDS):
    M(_cc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    String r = @PKG@.GearLife.reclaim(pr, p, %d);
    pr.sendMessage(@MSG@.raw("[Gear] " + @PKG@.GearUi.infoText(r)).color(@PKG@.GearUi.infoColor(r)));
  } catch (Throwable t) {
    @PKG@.Gear.warn("/%s failed: " + t);
    pr.sendMessage(@MSG@.raw("[Gear] That did not work - the server log has the details."));
  }
}""" % (_k, _c))
C(tpc, r"""
public ToolPtsCmd() {
  super("toolpoints", "Your lifelong tools and their Upgrade Points (the Tools tab of /smithing)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(tpc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!@PKG@.GearCfg.LL_ON) { pr.sendMessage(@MSG@.raw("[Gear] Lifelong tools are switched off on this server.").color(@PKG@.GearDefs.C_GOLD)); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Gear] no player found")); return; }
    @PKG@.GearLife.sweep(pr, p.getInventory(), true);
    @PKG@.LifePage page = new @PKG@.LifePage(pr);
    int[] h = @PKG@.GearLife.held(p.getInventory());
    @IS@ x = h == null ? null : @PKG@.GearStamp.at(p.getInventory(), h[0], h[1]);
    int k = x == null || x.isEmpty() ? -1 : @PKG@.GearLL.kOf(x.getItemId());
    if (k >= 0) page.sel = k;
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/toolpoints failed: " + t);
    pr.sendMessage(@MSG@.raw("[Gear] could not open the Tools page - the server log has the details"));
  }
}""")
C(llc, r"""
public LifelongCmd() {
  super("lifelong", "Make the tool in your hand your lifelong one instead (once per kind, in the first days)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(llc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Gear] no player found")); return; }
    String r = @PKG@.GearLife.repick(pr, p);
    pr.sendMessage(@MSG@.raw("[Gear] " + @PKG@.GearUi.infoText(r)).color(@PKG@.GearUi.infoColor(r)));
  } catch (Throwable t) {
    @PKG@.Gear.warn("/lifelong failed: " + t);
    pr.sendMessage(@MSG@.raw("[Gear] That did not work - the server log has the details."));
  }
}""")
# ---- GearLLDropSys: the Drop key / dragging out on a lifelong tool is cancelled BEFORE the engine removes anything (InventoryPacketHandler
# fires DropItemEvent$PlayerRequest, then resolves the section with InventoryUtils.getSectionById and removes the stack only when the
# request was not cancelled - VERIFIED bytecode). The player's own sections (negative ids) and an open container window (positive) alike.
event_system(gdrop, "GearLLDropSys", "@DIRQ@", PLAYER_Q, r"""
    if (!(ev instanceof @DIRQ@)) return;
    @DIRQ@ e = (@DIRQ@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.LL_ON || !@PKG@.GearCfg.LL_NODROP) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @IC@ c = @IUT@.getSectionById(r, e.getInventorySectionId(), st);
    if (c == null) return;
    int sl = (int) e.getSlotId();
    if (sl < 0 || sl >= c.getCapacity()) return;
    @IS@ x = c.getItemStack((short) sl);
    if (x == null || x.isEmpty() || !@PKG@.GearLL.llStack(x.getItemId(), x.getMetadata())) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    // fix round 2 (cross-mod critic 2): only YOUR working lifelong tool is kept - another player's (useless to you: GearLL.hit) or your own
    // RETIRED one may be dropped, so nobody is stuck with a tool they can't use
    try {
      @BD@ dd = @PKG@.GearData.gearDoc(x.getMetadata());
      if (pr != null && (!@PKG@.Gear.pkey(pr.getUuid()).equals(@PKG@.GearLL.owner(dd)) || @PKG@.GearLL.isRt(dd))) return;
    } catch (Throwable td) { }
    e.setCancelled(true);
    @PKG@.GearLL.N[4] = @PKG@.GearLL.N[4] + 1L;
    // fix round (engine critic 4): InventoryPacketHandler re-sends only the player's own sections after a cancelled drop (a window id has no
    // InventoryComponent type - VERIFIED bytecode); an open chest window is marked changed the engine's own way (InventoryUtils does the
    // same) so PlayerSendInventorySystem re-sends it and the client shows the tool back in the chest
    if (e.getInventorySectionId() >= 0) {
      try {
        @PLA@ wp = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
        @WMGR@ wm = wp == null ? null : wp.getWindowManager();
        if (wm != null) wm.markWindowChanged(e.getInventorySectionId());
      } catch (Throwable tw) { }
    }
    if (pr != null) @PKG@.GearGate.popup(pr, pr.getUuid(), x.getItemId(), "Lifelong tools stay with you", "They can't be dropped. Put yours in a chest, Requip or your backpack instead.");""")
# ---- GearLLFn: gear:fn:lifelong (0) Object[] { UUID, String kind } -> String uid or null, or (fix round 2) a bare UUID -> Integer kinds owned; gear:fn:perk (1) Object[] { UUID, String kind,
# String perk key } -> Integer level (SkyyTrees reads vein / fell, and lists them in gear:perk:readers); gear:fn:farmTier (2) Object[] { UUID,
# String block id, String held item id } -> Integer (-1 not gated, 0 normal, 1 one tier up = half XP + no Fortune, 2 refused). Never throws.
gllfn.addInterface(pool.get("java.util.function.Function"))
F(gllfn, "public int mode;")
C(gllfn, "public GearLLFn(int m) { this.mode = m; }")
M(gllfn, r"""
public Object apply(Object o) {
  try {
    // fix round 2 (cross-mod critic 1): SkyyQuests' tutorial asks gear:fn:lifelong with a bare UUID (research/SkyyQuests-Tutorial-Spec.md:
    // "apply(UUID) -> Integer kinds held") = how many of the four kinds your profile owns (0-4); null = unknown (off / unreadable)
    if (o instanceof java.util.UUID) {
      if (this.mode != 0 || !@PKG@.GearCfg.LL_ON) return null;
      java.util.Properties P0 = @PKG@.GearLL.reg(@PKG@.Gear.pkey((java.util.UUID) o));
      if (@PKG@.GearLL.bad(P0)) return null;
      int n0 = 0;
      for (int k0 = 0; k0 < 4; k0++) if (P0.getProperty(@PKG@.GearLL.KIND[k0] + ".uid") != null) n0++;
      return Integer.valueOf(n0);
    }
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2) return null;
    java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
    if (this.mode == 2) {
      String h = a.length > 2 && a[2] instanceof String ? (String) a[2] : null;          // fix round: the held item id (java.lang only)
      return Integer.valueOf(@PKG@.GearLL.farmTier(a[1] instanceof String ? (String) a[1] : null, h));
    }
    if (u == null || !@PKG@.GearCfg.LL_ON) return null;
    int k = @PKG@.GearLL.kOfName(a[1] instanceof String ? (String) a[1] : null);
    if (k < 0) return null;
    java.util.Properties P = @PKG@.GearLL.reg(@PKG@.Gear.pkey(u));
    if (this.mode == 0) return P.getProperty(@PKG@.GearLL.KIND[k] + ".uid");
    if (this.mode == 1 && a.length > 2 && a[2] instanceof String) {
      for (int p = 0; p < @PKG@.GearLL.PK.length; p++) if (@PKG@.GearLL.PK[p].equals(a[2])) return Integer.valueOf(@PKG@.GearLL.perkOf(P, k, p));
      return Integer.valueOf(0);
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("llfn" + this.mode, "gear:fn lifelong bridge failed: " + t); }
  return null;
}""")
# ---- the hooks: the join + scan hooks get their bodies now (GearLife exists); the Tools tab click on the other Smithing pages
gll.getDeclaredMethod("joinHook").setBody(J("{ @PKG@.GearLife.sweep($1, $2, true); }"))
gll.getDeclaredMethod("sweepHook").setBody(J("{ @PKG@.GearLife.sweep($1, $2, false); }"))
for _pg in (rpg, mpg, spg):
    _pg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearLL.tabGo($3, this.playerRef)) return; }"))
print("0.3.0 lifelong tools: %s; %d perks; ladders %d chars; commands /toolpoints /pickaxe /hatchet /hoe /sickle /lifelong"
      % (", ".join(str(c.getName()).rsplit(".", 1)[1] for c in LIFE_CLASSES), len(LL_PERKS), len(LL_LADDER_DEF)))

'''
before('''# ================================================================= GearAdmin: /gear bodies (world thread; admin writes are logged)
''', LIFE_B + LIFE_C)

# ================================================================================================================ GearBye forgets the per-player maps
rep('''    @PKG@.GearTool.forget(u);   // 0.2.12: our skill:bonus source''', '''    @PKG@.GearTool.forget(u);   // 0.2.12: our skill:bonus source
    @PKG@.GearLL.forget(u);     // 0.3.0: the slow popup / sweep / chat-line clocks''')

# ================================================================================================================ the plugin
rep('''                                                        "GearToolHitSys")))''', '''                                                        "GearToolHitSys",
                                                        # 0.3.0 lifelong tools: the Drop key on a lifelong tool
                                                        "GearLLDropSys")))''')
rep('''  getCommandRegistry().registerCommand(new @PKG@.SmithCmd());          // 0.2.23: /smithing (/smith) = the hub on its Craft tab''',
    '''  getCommandRegistry().registerCommand(new @PKG@.SmithCmd());          // 0.2.23: /smithing (/smith) = the hub on its Craft tab
  // 0.3.0 lifelong tools: the Tools tab, the four replacement commands, the re-pick
  getCommandRegistry().registerCommand(new @PKG@.ToolPtsCmd());
  getCommandRegistry().registerCommand(new @PKG@.PickaxeCmd());
  getCommandRegistry().registerCommand(new @PKG@.HatchetCmd());
  getCommandRegistry().registerCommand(new @PKG@.HoeCmd());
  getCommandRegistry().registerCommand(new @PKG@.SickleCmd());
  getCommandRegistry().registerCommand(new @PKG@.LifelongCmd());''')
rep('''  br.put("gear:fn:classShow", new @PKG@.SmithFn(1));       // 0.2.23: the Craft tab's class filter (SkyySacks /craft Smithing tab)''',
    '''  br.put("gear:fn:classShow", new @PKG@.SmithFn(1));       // 0.2.23: the Craft tab's class filter (SkyySacks /craft Smithing tab)
  br.put("gear:fn:lifelong", new @PKG@.GearLLFn(0));       // 0.3.0: a profile's lifelong tool uid per kind
  br.put("gear:fn:perk", new @PKG@.GearLLFn(1));           // 0.3.0: a lifelong tool's perk level (SkyyTrees: vein / fell)
  br.put("gear:fn:farmTier", new @PKG@.GearLLFn(2));       // 0.3.0: crop vs hoe / sickle tier (SkyySkills: half XP one tier up)
  br.put("quest:caller:gearlife", Boolean.TRUE);            // 0.3.0 fix round 2: SkyyQuests' "lifelong 4/4" tutorial part may count now''')
rep('''[SkyyGear] @VER@ ready - /smithing, /reforge, /identify, /multitool, /upgrade, /gear''',
    '''[SkyyGear] @VER@ ready - /smithing, /reforge, /identify, /multitool, /upgrade, /toolpoints, /pickaxe, /hatchet, /hoe, /sickle, /lifelong, /gear''')
rep('''"; " + @PKG@.GearSmith.statusText() + "; gear:fn:curve''', '''"; " + @PKG@.GearSmith.statusText() + "; " + @PKG@.GearLL.statusText() + "; gear:fn:curve''')
rep('''gear:fn:smithing, gear:fn:classShow; wand / staff''', '''gear:fn:smithing, gear:fn:classShow, gear:fn:lifelong, gear:fn:perk, gear:fn:farmTier; wand / staff''')
rep('''  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }''', '''  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }
  try { java.util.Map bq = @PKG@.Gear.bridge(); bq.remove("gear:fn:lifelong"); bq.remove("gear:fn:perk"); bq.remove("gear:fn:farmTier"); bq.remove("quest:caller:gearlife"); } catch (Throwable t7) { }''')

# ================================================================================================================ the class list + the manifest
rep(''' + MERGE_CLASSES + UP_CLASSES + SMITH_CLASSES + ANVIL_CLASSES''', ''' + MERGE_CLASSES + UP_CLASSES + SMITH_CLASSES + ANVIL_CLASSES + LIFE_CLASSES''')
rep('''/identify open it) and Multitool tabs,''', '''/identify open it), Tools (your lifelong pickaxe, hatchet, hoe and sickle and their Upgrade Points; /toolpoints) and Multitool tabs,''')
rep('''Server Setup -> Gear. Replaces SkyyRolls.''', '''LIFELONG TOOLS: one pickaxe, hatchet, hoe and sickle per player for life (never crafted, dropped, sold or salvaged; /pickaxe, /hatchet, /hoe, /sickle replace a lost one) that level with your skills and tier up on the Anvil with Copper Ingots and Enchanted materials; a tool tier gate (one tier up is slow, two up is refused, no tool no logs or ore); Server Setup -> Gear. Replaces SkyyRolls.''')

# ================================================================================================================ checks on the result
_code = s[s.index('VERSION = "0.3.0"'):]
assert _code.count("LIFE_CLASSES") >= 4 and _code.count("joinHook") >= 2 and _code.count("sweepHook") >= 2
# javassist order: definitions before their callers
for a_, b_ in (("public static int[] decideC(", "public static int[] decide("),
               ("public static int[] decide(", "public static int hit("),
               ("public static int hit(", 'event_system(gtoolh, "GearToolHitSys"'),
               ("public static double[] perkFx(", "public static double[] stats(java.util.UUID u, @IS@ s)"),
               ("public static int levelFor(", "public static int[] gate(java.util.UUID u, int f, String id, @BD@ d)"),
               ("public static void lines(java.util.UUID ow, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {\n  if (!@PKG@.GearCfg.LL_ON",
                "public static void lines(java.util.UUID owner, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {\n  int f = fam(id);"),
               ("public static String onlyFor(", "public static double[] held("),
               ("public static boolean noCraft(", 'event_system(gcrp, "GearCraftPreSys"'),
               ("public static boolean llStack(", "public static String why(String id, @BD@ md)"),
               ("public static String ladders(", "public static Object[] tab()"),
               ("public static String tierWhy(", "public static Object[] check(@IS@ s, java.util.UUID u)"),
               ("public static void joinHook(", "public void run() {\n  try {\n    if (this.pr == null || !this.pr.isValid()) return;"),
               ("public static void sweepHook(", "@PKG@.GearLL.sweepHook(this.pr"),
               ("public static void prefetch(", "@PKG@.GearLL.prefetch(this.pr.getUuid());"),
               ("public static void forget(java.util.UUID u) {\n  if (u == null) return;\n  SLOW.remove(u);", "@PKG@.GearLL.forget(u);"),
               ("public static int[] find(@INV@ inv, String pk, String lu)", "public void row(@UCB@ b"),
               ("public static void sweep(@PR@ pr, @INV@ inv, boolean force)", "public ToolPtsCmd()"),
               ("public static String reclaim(", "public PickaxeCmd()"),
               ("public static String repick(", "public LifelongCmd()"),
               ("public static void recover(", "public static void sweep0("),
               ("public static boolean migrate(", "public static void sweep0("),
               ("public static void pass(", "public static void sweep0("),
               ("public static boolean mark(", "public static boolean migrate("),
               ("public static int give(", "public static boolean migrate("),
               ("public static boolean restore(", "public static void pass("),
               ("public static void keep(", "public static void pass("),
               ("public static boolean settle(", "public static void pass("),
               ("public static boolean demote(", "public static boolean settle("),
               ("public static boolean retire(", "public static boolean settle("),
               ("public static String swap(", "public static String repick("),
               ("public static boolean failing(", "public static void sweep0("),
               ("public static boolean stale(", "public static int hit("),
               ("public static double slowF(", 'event_system(gtoolh, "GearToolHitSys"'),
               ("public static boolean isRt(", "public static boolean mine("),
               ("public static String rqKinds(", "String rq = rqKinds("),
               ("public static String tierFor(", "public static String reclaim("),
               ("public static boolean invested(", "public static void foreign("),
               ("public static void lvlWatch(", "@PKG@.GearLL.lvlWatch(u, s);"),
               ("public static int[] decideI(", "public static int[] decideC("),
               ("public static void foreign(", "public static void pass("),
               ("public static void remove(", "public static void foreign("),
               ("public static boolean demote(", "public static void pass("),
               ("public static boolean journal(", "public static boolean mark("),
               ("public static boolean commit(", "public static void recover("),
               ("public static void tellOnce(", "public static boolean restore(")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_[:60], b_[:60])
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.2.26 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.2.26 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
