"""Derive SkyyGear/build_skyygear_0.3.29.py from the LIVE 0.3.28 (build_skyygear_0.3.28.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_28_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_29_patch.py      then      python SkyyGear/build_skyygear_0.3.29.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.29.py   (S329 + H329 on one booted engine; --static needs no jar)

0.3.29 (2026-10-18) = 20 LEVELS PER ZONE + THE BRONZE MINING SET + 15 FORAGING / 15 FARMING TIERS (research/Level-Bands-20-Spec.md 1-6, 8).
Skyy (docs/answered/gear.md 2026-10-18): "where is bronze? bronze is the alloy of iron and copper. its already in the game. so we need to add the
rescipy to smelt iron and copper together to make bronze, and add it to this list. also those levels dont add up at all. we have 3 tiers per zone.
and im changing it so we have 20 levels per zone. so bronze gear would be like 15-23 thorium would start at 20. and dusk armor would end at like 43.
(follow the same patern for all the new metals. ..." + on the table: "perfect! make sure all the gear follows that. tools, weapons, armor. (combat
gear. (make sure the Tiers listed in the items flavor text get updated too, to match the new order.) (this way it takes 5 rebirths to reach lvl
100 ... we have 15 tiers of mining armor sets. we need to update foraging, and farming, to match ..." + "Start the level-bands round now"
(docs/answered/project.md); 15th crop Mushroom, planted from spores ("make sure they use spores, not seeds"). Unanswered spec questions Q2-Q14 =
the spec defaults. Plus (main session, Skyy on the Upgrade page): "you should be able to get your first vein mine and tree feller at lvl 4. second
at lvl 8 3rd at lvl 16 and so on." + popup "+8 after 16: 4,8,16,24,32,40".
  1. THE BANDS (tools/tier_tags.py TT_VERSION 3: METAL_BANDS, the one table): Copper / Crude / Wood / Armor_Copper 1-8, Iron 8-15, Bronze 15-23,
     Thorium 20-28, Lead 28-35, Dusk 35-43, Cobalt 40-48, Chromium 48-55, Azurvane 55-63, Adamantite 60-68, Slag 68-75, Cinder 75-83, Mithril 80-88,
     Titanium 88-95, Lumen 95-103, Onyxium 100-108 - the level.material rows (11 metal + 8 <M>_SkyWynn), garmor.zoneBands, the gathering armor
     bands by ladder T (garmor.bands, now 15 ranges), the Untiered zone bands (Z1 Bronze 15-23 unchanged, Hepta Axe = Cinder 75-83). The 59 family
     rows keep their tag (spec 1.1: starts mapped through the old -> new metal anchors, width 8: Wool 3-10 ... Prisma 91-98); the starter rows
     Armor_Leather_Soft / Armor_Cloth_Wool 1-10, Weapon_Spellbook_Copper / Weapon_Crossbow_Copper 1-8. "Never above 49" is gone: a band may run
     to 200 (level.material Min stays 0-100; item levels still stop at 100 until a rebirth-raised cap exists - spec Q2). loot.levelTop 49 -> 100.
     GearView.tierFor (the combat armor tag) mirrors the new LEVEL_BANDS; GearSigDrop.zoneOf reads tier_tags ZONE_TOPS (20 / 40 / 60 / 80).
     Lifelong tools follow at once (level = min(skill, band top): a Copper tool tops at 8); points are never refunded or taken (free = earned -
     spent, never below 0), saved line / ability levels stay saved (only the working level is capped).
  2. THE BRONZE MINING SET (spec 3.3): GearMine tier 15 (appended - saved indexes stay) = the vanilla Armor_Bronze_<Slot> ids by exact id, ranked
     between Iron and Thorium (/smithing > Mining armor); band level.material.Bronze 15-23; lines garmor.mining.bronze 0.2 0.4 0.2 0.2 / 0 0 0 0 /
     lamp 2, set.mining_bronze mfort+2 mpow+2.5 (full Fortune 3.0); recipes = Iron's at the Armor Bench with Bronze Ingots 1:1 (standalone recipe
     assets SkyyGear_Recipe_Armor_Bronze_<Slot>; the vanilla TODO-bench recipe stays unreachable). Out of the bag pool (a Mining piece).
  3. FORAGING 15 TIERS (spec 5): the 5 old set ids stay at T1 / T3 / T6 / T9 / T12 (same looks); 10 new sets Armor_Foraging_<Tree>_<Slot> (Beech,
     Dry, Bottletree, Fir, Spiral, Burnt, Petrified, Jungle, Banyan, Crystalwood) from the approved art in art/gathering-armor/ (read at build time,
     shipped as is). FARMING 15 TIERS (spec 6): the 7 placeholder ids at T1 Wheat, T3 Carrot, T5 Cauliflower, T7 Pumpkin, T10 Chilli, T11 Cotton,
     T14 Onion + 8 placeholder recolours (Lettuce, Corn, Turnip, Aubergine, Tomato, Rice, Potato, Mushroom). Stats: today's points kept on the
     old sets, straight lines between them (garmor.foraging / garmor.farming = 15 numbers per list). Tier-up = the Enchanted item of the next
     tier's tree / crop. Fishing keeps its 5 sets (bands of T1 / T2 / T4 / T7 / T10). Every gathering armor piece's flavour text starts with its
     tier tag ("T3 Bronze - Autumn Bark set ...", tools/tier_tags.py rows).
  4. VEIN MINE / TREE FELLER (Skyy "4,8,16,24,32,40"): ability level n needs tool level lifelong.abilityLevels[n] (NEW row, default 4,8,16,24,32,40);
     past the list + lifelong.abilityLevelStep (8) each; an EMPTY list = the old rule n x abilityLevelStep. Every tool / multitool side with these
     lines (GearLL.abilCap / pkNeedLv). Levels already bought stay saved (only the working level is capped).
  5. THE MULTITOOL (Skyy 2026-10-18 "the multi tool isnt slower, and has the same fortune. its The exact same as both the tools combined. No
     drawbacks. The only actual drawback is that you can't unlock it till after you rebirth once." + on its tooltip "keep the mining and foraging
     levels separate on the tool. so it would say Pickaxe [lvl 10] (pickaxe stats below) then hatchet [lvl 11] (hatchet stats below.)"):
     multi.speedPct 85 -> 100 and multi.fortunePct 70 -> 100 (each side = its single tool: power, Fortune, Wisdom, Vein Mine / Tree Feller); the
     "slightly slower and less Fortune" line is gone. multi.rebirthGate false -> true: Make multitool (crafted pair and lifelong pair) needs rebirth 1
     (SkyyRebirth's rebirth:n:<uuid>; no SkyyRebirth = refused); the row shows a red requirement line "Rebirth 1 : 0" (Menu-Pattern rule 9). A
     multitool already made stays usable (the gate is on the merge only - nothing is taken away). The tooltip: the tier tag first (lang, unchanged),
     then "Pickaxe [Lv N]" (Mining) + Mining Power / Mining Fortune / Wisdom / its Upgrades (Vein Mine ...), then "Hatchet [Lv M]" (Foraging) +
     Chopping Power / Foraging Fortune / Wisdom / its Upgrades (Tree Feller ...), the numbers = GearTool.mstats (what the hits use); the Lv. Min
     line stays; the NAME drops its single "[Lv N]" ("Crude Multitool": two levels live in the tooltip). The lifelong sweep keeps the hatchet side's
     level in the document (NEW field lvH) so the tooltip refreshes on a Foraging level-up as well as on a Mining one.
  6. NO ENCHANTED BELOW DUSK (Skyy 2026-10-18 on the Mining armor Iron set: "and lets reduce the upgrade cost of the lower tiers a bit. so it doesnt
     cost enchanted till dusk."): every tier-up INTO T1-T5 (Copper, Iron, Bronze, Thorium, Lead) pays plain materials - each Enchanted item of
     the 0.3.28 cost = 75 of its base (tools/skyyench.py RATIO 100 base = 1 Enchanted, x 3/4 = "a bit" less), its Enchanted Sticks = 75 plain
     sticks each (GearUp.stickFor skips those steps; lifelong.stickCost unchanged). garmor.ladders (Mining), the Foraging / Farming / Fishing
     ladders, lifelong.ladders, multi.ladders, can.ladders, harvester.ladders. Dusk (T6) and up unchanged (Enchanted).
  7. THE GATHERING ARMOR BUFF (Skyy 2026-10-18 "buff all the gathering armor to give more fortune, and to also give damage and speed. armor should
     be a big part of the progression" + popup "Breaking power + speed"): a full set at ladder T gives about that tier's tool Fortune line -
     60, 75, 90, 105, 120, 135, 150, 160, 170, 180, 190, 200, 210, 225, 240 (T16 Onyxium 255); never more than 100 from armor before T4 - 70 % on
     the pieces (Head 25 / Chest 35 / Hands 15 / Legs 25 %), 30 % the full-set bonus (Mining: garmor.mining.<tier> + set.mining_<tier> mfort;
     Foraging / Farming: garmor.foraging / garmor.farming). Plus Breaking Power (Mining / Chopping / Farming Power, posted as bp.<skill> in the
     "garmor" skill:bonus source that GearTool.accBp reads) and Breaking Speed (added to gear:swing:<uuid> for the held tool's skill) - full set
     25 % + 10 a tier / 5 % + 2 a tier (NEW rows garmor.powerPct / garmor.swingPct, T1-T16), well below the tool lines. Fishing: full-set double
     catch 60 % of the T value, Fishing Speed x2. armor.fortune.cap 100 -> 0 (= none; the numbers keep the T4 rule). The lifelong hatchet ladder's
     logs follow the new tree tiers (Iron Beech, Bronze Maple, Thorium Dry, Lead Bottletree, Dusk Gumboab, Cobalt Fir ... Lumen Crystal).
  8. CROPS BY TIER, ALLOY GATES (main session 2026-10-18): the watering can / Harvester / hoe / sickle steps cost the key crop of their own T
     (Iron Lettuce, Bronze Carrot, Thorium Corn ... Lumen Mushroom; plain below Dusk). Alloy armor recipes are KnowledgeRequired: the Bronze
     Mining set (SkyyGear_Recipe_Armor_Bronze_<Slot>) + the Dusk / Azurvane / Cinder / Lumen Mining sets (Armor_Mining_<M>_<Slot>_Recipe_Generated_0)
     - SkyyCollections 0.2.28 grants recipe:<id> when BOTH input collections reach V (Skyy "then bronze when both reach 5"). An alloy TOOL tier-up
     (Bronze, Dusk, Azurvane, Cinder, Lumen steps) needs the Furnace Charm that smelts that alloy (I .. V) equipped in Void Charms: SkyyAccessories'
     acc:smelt:<uuid> ("<tier>|..|..|..|<pkey>", the active profile only); refused without it, a red / green row "Furnace Charm I" on the Upgrade
     page. Collections answers an alloy collection token with the LAGGING input collection (one row, unchanged format).
  9. THE SOUL ORB BAND + LEGENDARY FRAMES: Skyy's Soul Orb crafted at Divinity ~14 came out Lv 3 - no level.material row matched
     Weapon_Wand_SoulOrb, so its band was its Hytale ItemLevel 3 exactly (GearLevel.band, the level.vanilla branch). New rows SoulOrb 1-8 (the
     Crude / Wood starter band: made at your class level, cap 8) and Shadoweave 60-67 (SkyyArmory's top cloth wraps had the same exact-level band);
     fresh file + migrate0329 (added when missing). Beta bug 21 "Legendary rarity colour does not stand out": the Legendary quality keeps the
     Wynn aqua text #55FFFF but gets its own tooltip / arrow / slot frames - the vanilla Rare art gradient-mapped onto dark teal -> bright aqua at
     build time (Common/UI/ItemQualities/Tooltips/ItemTooltipSkyyLegendary@2x.png 107x107, ...Arrow@2x.png, Slots/SlotSkyyLegendary@2x.png 148x148;
     Quirk may replace them with hand-drawn art of the same names and sizes).
  10. QUIRK'S 15 FARMING SETS (Skyy 2026-10-18 "looking good!"): the PRIVATE art in ../SkyWynn-PRIVATE-art/farming-armor/<Crop>/ (models, textures,
     icons; built on vanilla armor shapes) is read at BUILD time into the jar only, like the mining-armor textures - never in the repo. It replaces
     the P1-P7 recolours and the 8 placeholders. The item ids stay (Armor_Farming_P1..P7_<Slot> + the 8 crop ids), so saved items and set ids keep
     working; each id points at its crop's Items/Armors/SkyyFarming/<Crop>/<Slot>.blockymodel / _Texture.png / Icons/ItemsGenerated/
     Armor_Farming_<Crop>_<Slot>.png. Hide flags + icon framing = the crop's vanilla base piece (Quirk's README "Vanilla base": Wheat / Lettuce
     Wood ... Mushroom Prisma). The build stops if the private folder is missing.
  FORTUNE RULE PER SOURCE (Skyy 2026-10-18 "Per source is fine"): each source (tool line, armor set, accessories, pets) stays at or under 100 %
     before T4; stacking sources may go higher. Review fix F3: a player who already has the lifelong multitool sees "You already have your
     multitool." on the Tools tab, never the rebirth gate.
  NOT IN GEAR (SkyyCollections owns it - listed for its builder): the collection tier a tool / armor tier-up needs (Skyy "reduce the collection
     level you need to upgrade the tool to like 2" + "you unlock the tools first, then the armor, then the weapons") - SkyyCollections'
     rewards.properties tierup:<kind>:<Metal> tokens; Gear only asks coll:fn:tierup and shows its answer ("Copper Ore collection II 50 : 67").
  ONE-TIME UPDATE migrate0329 (after migrate0328; the migrate0327 machinery, text compare h23Old): every ONE-LINE entry still holding its 0.3.28
  default is rewritten (82 level.material rows, garmor.zoneBands, garmor.bands, garmor.foraging, garmor.farming, garmor.ladders.foraging,
  garmor.ladders.farming, garmor.ladders.fishing, garmor.ladders, lifelong.ladders, multi.ladders, can.ladders, harvester.ladders, loot.levelTop,
  ut.Hepta_Axe, multi.speedPct, multi.fortunePct, multi.rebirthGate, garmor.fishing, armor.fortune.cap, the 15 garmor.mining.<tier> + 15
  set.mining_<tier> rows); a hand-edited value is kept + noted; then a pure addition at the END: garmor.mining.bronze +
  set.mining_bronze when the file lacks them, and lifelong.abilityLevels= (empty = the old n x step rule) when lifelong.abilityLevelStep was hand
  edited; History copy verified first, one change-log row per change (Undo in Server Setup), the run-once marker, bytes + line endings kept.
Commands: none new. Classes: none new. Config: + lifelong.abilityLevels, garmor.powerPct, garmor.swingPct; defaults above (migrate0329). SAVED DATA: one new document field lvH on a
lifelong multitool (its hatchet side's level; older versions ignore it); documents keep their stored level / set field; the old gathering set
ids keep their ids.
ROLLBACK 0.3.29 -> 0.3.28: item-safe ONLY after Undoing the migrate0329 rows in Server Setup's change log (0.3.28 reads bands above 49 as written
but its 7-range garmor.bands / 5- and 7-number gathering lists would reject the 15-entry texts and fall back to its defaults with a WARN). The 40
new gathering armor pieces (10 Foraging + 8 Farming sets) are unknown items to 0.3.28 - take them off first. Bronze pieces become combat armor
again; multitools get 0.3.28's 85 % / 70 % share back unless the migrate0329 rows are kept (0.3.28 reads 100 / 100 fine). Roll back together with the level-bands set (Mobs, Armory, Collections, Bazaar, Auctions).
"""
import os
import sys
import ast
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.28.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.29.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.28"' in s and "GENERATED by tools/gear_0_3_28_patch.py" in s, "not the generated 0.3.28 script"
assert "H29_" not in s and "migrate0329" not in s and "abNeed(" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
MK0 = s.count(' = mk("')
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def after(anchor, text):
    rep(anchor, anchor + text)


def before(anchor, text):
    rep(anchor, text + anchor)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.28":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.28" % _set.get("SkyyGear"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import tier_tags as _T          # noqa: E402
assert _T.TT_VERSION == "3", "tools/tier_tags.py must be TT_VERSION 3 (step 1 of this round)"

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.29 (2026-10-18)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.28 - build script (javassist via jpype). GENERATED by tools/gear_0_3_28_patch.py from the LIVE 0.3.27 (itself GENERATED by
tools/gear_0_3_27_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.28.py -> SkyyGear/SkyyGear-0.3.28.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.28.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE).

''', '''"""SkyyGear 0.3.29 - build script (javassist via jpype). GENERATED by tools/gear_0_3_29_patch.py from the LIVE 0.3.28 (itself GENERATED by
tools/gear_0_3_28_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.29.py -> SkyyGear/SkyyGear-0.3.29.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.29.py. Needs Quirk's private art (../SkyWynn-PRIVATE-art/mining-armor and
../SkyWynn-PRIVATE-art/metal-art/Tools-PRIVATE) and our own art/gathering-armor (the Foraging sets).

''' + NOTE + '''
--- 0.3.28 notes ---
''')
rep('VERSION = "0.3.28"\n', 'VERSION = "0.3.29"\n')

# ================================================================================================================ 1: the metal bands
# the 0.3.28 table stays computed (BANDS_V28 / FAM_BANDS_V28: migrate0329's old defaults); the live bands = tools/tier_tags.py METAL_BANDS
rep('''assert all(_s >= 1 and _s <= _c <= VANILLA_TOP for _t, _s, _c in BANDS)
FAM_BANDS = [(t, l, min(l + BAND_W_DEF - 1, VANILLA_TOP)) for t, l, _w in FAMILIES]
assert dict((t, (s, c)) for t, s, c in FAM_BANDS)["Prisma"] == (45, 49) and dict((t, (s, c)) for t, s, c in FAM_BANDS)["Wool"] == (5, 12)
assert all(c - s == BAND_W_DEF - 1 or c == VANILLA_TOP for t, s, c in FAM_BANDS), "families: start..start+7, never above 49"
''', '''assert all(_s >= 1 and _s <= _c <= VANILLA_TOP for _t, _s, _c in BANDS)
FAM_BANDS = [(t, l, min(l + BAND_W_DEF - 1, VANILLA_TOP)) for t, l, _w in FAMILIES]
assert dict((t, (s, c)) for t, s, c in FAM_BANDS)["Prisma"] == (45, 49) and dict((t, (s, c)) for t, s, c in FAM_BANDS)["Wool"] == (5, 12)
assert all(c - s == BAND_W_DEF - 1 or c == VANILLA_TOP for t, s, c in FAM_BANDS), "families: start..start+7, never above 49"
# ---- 0.3.29 (tools/gear_0_3_29_patch.py item 1; Skyy 2026-10-18 "20 levels per zone"): THE bands = tools/tier_tags.py METAL_BANDS; the 59 family
# starts mapped through the old -> new metal anchors (spec 1.1, TT.remap_family_start), width 8; no "never above 49" (a band may run to LEVEL_TOP)
import tier_tags as TT          # (imported again below; pure Python)
assert TT.TT_VERSION == "3", "tools/tier_tags.py TT_VERSION 3 (20 levels per zone)"
LEVEL_TOP = 200          # the level.material row limit (item levels still stop at GearLevel.clamp 100)
BANDS_V28, FAM_BANDS_V28 = list(BANDS), list(FAM_BANDS)
BANDS = [(t, TT.band(t)[0], TT.band(t)[1]) for t, _s, _c in BANDS_V28]
assert BANDS == [("Crude", 1, 8), ("Wood", 1, 8), ("Copper", 1, 8), ("Armor_Copper", 1, 8), ("Bronze", 15, 23), ("Iron", 8, 15),
                 ("Thorium", 20, 28), ("Cobalt", 40, 48), ("Adamantite", 60, 68), ("Mithril", 80, 88), ("Onyxium", 100, 108)], BANDS
FAM_BANDS = [(t, TT.remap_family_start(s), TT.remap_family_start(s) + BAND_W_DEF - 1) for t, s, _c in FAM_BANDS_V28]
_fb29 = dict((t, (s, c)) for t, s, c in FAM_BANDS)
assert _fb29["Prisma"] == (91, 98) and _fb29["Wool"] == (3, 10) and _fb29["Linen"] == (6, 13) and _fb29["Cotton"] == (8, 15) and _fb29["Doomed"] == (40, 47)
assert _fb29["Ancient"] == (50, 57) and _fb29["Scarab"] == (60, 67) and _fb29["Crystal_Flame"] == (80, 87) and _fb29["Silk"] == (20, 27)
def _lt29(lv, bands, crude):
    _t = next((x for l_, x in bands if lv >= l_), 1)
    return (_t, _t == 1 and lv < crude)


assert all(_lt29(s0, TT.LEVEL_BANDS_V2, TT.LEVEL_CRUDE_V2) == _lt29(_fb29[t][0], TT.LEVEL_BANDS, TT.LEVEL_CRUDE) for t, s0, _c in FAM_BANDS_V28),     "spec 1.1: every family keeps the tier tag (and its Crude word) it shows"
assert all(_c - _s == BAND_W_DEF - 1 for _t, _s, _c in FAM_BANDS)
''')
rep('''BD_ALL = BANDS + FAM_BANDS          # entry, min, cap in default-file order (the metals with Armor_Copper, then the 59 family rows)
''', '''BD_ALL = BANDS + FAM_BANDS          # entry, min, cap in default-file order (the metals with Armor_Copper, then the 59 family rows)
BD_ALL_V28 = BANDS_V28 + FAM_BANDS_V28          # 0.3.29: the 0.2 - 0.3.28 bands (proofs of the older rounds below)
''')
rep('''def cap_of(s, w=BAND_W_DEF):
    """what one number N means in 0.2 (GearCfg.capOf): N to N + width - 1, never past 49 while N is a vanilla level (<= 49), never past 100"""
    c = s + max(1, w) - 1
    if s <= VANILLA_TOP and c > VANILLA_TOP:
        c = VANILLA_TOP
    return min(c, 100)


assert cap_of(10) == 17 and cap_of(45) == 49 and cap_of(49) == 49 and cap_of(60) == 67 and cap_of(98) == 100 and cap_of(0) == 7''',
    '''def cap_of(s, w=BAND_W_DEF):
    """what one number N means (GearCfg.capOf): N to N + width - 1, never past LEVEL_TOP (0.3.29: the 0.2 "never past 49" rule is gone)"""
    c = s + max(1, w) - 1
    return min(c, LEVEL_TOP)


assert cap_of(10) == 17 and cap_of(45) == 52 and cap_of(49) == 56 and cap_of(60) == 67 and cap_of(98) == 105 and cap_of(0) == 7''')
# the 0.2 id table proofs keep proving the 0.2 bands (BD_ALL_V28); the new bands are proved right after
rep('''_B02 = dict((i, band_lookup(BD_ALL, i)) for i in _GEAR_AZ + _TOOL_AZ)''', '''_B02 = dict((i, band_lookup(BD_ALL_V28, i)) for i in _GEAR_AZ + _TOOL_AZ)          # 0.3.29: the 0.2 - 0.3.28 proof''')
rep('''assert all(e_ in ("crude", "wood", "armor_copper") for e_ in (_B02[i][0] for i, _a, _b in _chg02)), "0.2 changes a start level: %s" % _chg02
''', '''assert all(e_ in ("crude", "wood", "armor_copper") for e_ in (_B02[i][0] for i, _a, _b in _chg02)), "0.2 changes a start level: %s" % _chg02
# 0.3.29: the same ids on the new bands - the kits Lv 1-8, copper armor 1-8, Copper 1-8, Iron 8-15, Mithril 80-88, Stone (family) 3-10
_B29 = dict((i, band_lookup(BD_ALL, i)) for i in _GEAR_AZ + _TOOL_AZ)
assert all(_B29[_k][1:] == (1, 8) for _k in ("Weapon_Shortbow_Crude", "Weapon_Sword_Crude", "Weapon_Staff_Wood", "Weapon_Wand_Wood"))
assert all(_B29[i][:3] == ("armor_copper", 1, 8) for i in _GEAR_AZ if i.startswith("Armor_Copper_"))
assert _B29["Weapon_Sword_Copper"][1:] == (1, 8) and _B29["Tool_Pickaxe_Copper"][1:] == (1, 8) and _B29["Weapon_Sword_Iron"][1:] == (8, 15)
assert _B29["Weapon_Staff_Mithril"][1:] == (80, 88) and _B29["Weapon_Daggers_Stone_Trork"][1:] == (3, 10) and _B29["Weapon_Sword_Onyxium"][1:] == (100, 108)
assert set(i for i in _B02 if _B02[i][0] is None) == set(i for i in _B29 if _B29[i][0] is None), "0.3.29 changes which ids have a band"
''')

# the new metals' bands (G22_BANDS = METAL_BANDS); 0.3.28's kept for migrate0329
rep('''G22_BANDS = [("Lead", 22, 30), ("Dusk", 24, 32), ("Chromium", 28, 40), ("Azurvane", 31, 41), ("Slag", 37, 45), ("Cinder", 39, 47),
             ("Titanium", 45, 55), ("Lumen", 50, 60)]
''', '''G22_BANDS = [("Lead", 22, 30), ("Dusk", 24, 32), ("Chromium", 28, 40), ("Azurvane", 31, 41), ("Slag", 37, 45), ("Cinder", 39, 47),
             ("Titanium", 45, 55), ("Lumen", 50, 60)]
G22_BANDS_V28 = list(G22_BANDS)          # 0.3.29: migrate0329's old defaults; the live bands = tools/tier_tags.py METAL_BANDS (20 levels per zone)
G22_BANDS = [(_w, TT.band(_w)[0], TT.band(_w)[1]) for _w, _a, _b in G22_BANDS_V28]
assert G22_BANDS == [("Lead", 28, 35), ("Dusk", 35, 43), ("Chromium", 48, 55), ("Azurvane", 55, 63), ("Slag", 68, 75), ("Cinder", 75, 83),
                     ("Titanium", 88, 95), ("Lumen", 95, 103)], G22_BANDS
''')
# the zone Mining sets' bands (garmor.zoneBands) = the same rows
rep('''ZM_BANDS_DEF = ",".join("%d-%d" % _r[8] for _r in ZM_ROWS)
assert ZM_BANDS_DEF == "22-27,24-28,28-34,31-38,37-42,39-43,43-49,46-49"
for _r in ZM_ROWS:          # 0.3.22: the bands climb the 15-step ladder with their ingot's tag (tools/tier_tags.py TT_VERSION 2), never above 49
    assert _r[8][1] <= VANILLA_TOP and''', '''ZM_BANDS_V28 = ",".join("%d-%d" % _r[8] for _r in ZM_ROWS)
assert ZM_BANDS_V28 == "22-27,24-28,28-34,31-38,37-42,39-43,43-49,46-49"          # 0.3.21 - 0.3.28 (migrate0329's old default)
ZM_ROWS = [tuple(_r[:8]) + (TT.band(_r[1]),) for _r in ZM_ROWS]          # 0.3.29: ONE band per metal (tools/tier_tags.py METAL_BANDS)
ZM_BANDS_DEF = ",".join("%d-%d" % _r[8] for _r in ZM_ROWS)
assert ZM_BANDS_DEF == "28-35,35-43,48-55,55-63,68-75,75-83,88-95,95-103", ZM_BANDS_DEF
for _r in ZM_ROWS:          # 0.3.22: the bands climb the 15-step ladder with their ingot's tag (0.3.29: tools/tier_tags.py TT_VERSION 3 bands)
    assert _r[8][1] <= LEVEL_TOP and''')
# the starter rows (spec 1.1: 1-12 -> 1-10, 1-18 -> 1-8)
rep('''ST_BANDS = [("Armor_Leather_Soft", 1, 12), ("Armor_Cloth_Wool", 1, 12), ("Weapon_Spellbook_Copper", 1, 18), ("Weapon_Crossbow_Copper", 1, 18)]
''', '''ST_BANDS = [("Armor_Leather_Soft", 1, 12), ("Armor_Cloth_Wool", 1, 12), ("Weapon_Spellbook_Copper", 1, 18), ("Weapon_Crossbow_Copper", 1, 18)]
ST_BANDS_V28 = list(ST_BANDS)          # 0.3.29 (spec 1.1): the starter rows on the new bands - cloth / leather 1-10 (the Wool family's cap), Copper 1-8
ST_BANDS = [("Armor_Leather_Soft", 1, 10), ("Armor_Cloth_Wool", 1, 10), ("Weapon_Spellbook_Copper", 1, 8), ("Weapon_Crossbow_Copper", 1, 8)]
assert [_t for _t, _s, _c in ST_BANDS] == [_t for _t, _s, _c in ST_BANDS_V28] and dict((t, c) for t, s, c in FAM_BANDS)["Wool"] == 10 and TT.band("Copper") == (1, 8)
''')
# the Untiered zone bands (the zone's alloy): Z1 Bronze 15-23 (unchanged), Z2 Dusk 35-43, Z3 Azurvane 55-63, Z4 Cinder 75-83, Z5 Lumen 95-103
rep('''assert UT_BANDS == {1: (15, 23), 2: (24, 32), 3: (31, 41), 4: (39, 47), 5: (50, 60)} and UT_BANDS[1] == (UT_LO, UT_HI), UT_BANDS''',
    '''assert UT_BANDS == {1: (15, 23), 2: (35, 43), 3: (55, 63), 4: (75, 83), 5: (95, 103)} and UT_BANDS[1] == (UT_LO, UT_HI), UT_BANDS          # 0.3.29
UT_BANDS_V28 = {1: (15, 23), 2: (24, 32), 3: (31, 41), 4: (39, 47), 5: (50, 60)}          # 0.3.27 - 0.3.28 (migrate0327's new values, migrate0329's old)''')
# migrate0327 keeps rewriting to ITS (0.3.27) values; migrate0329 moves the Hepta Axe on
rep('''    [("ut." + _r[0], "%d,%d,%s" % (U26_OLD[_r[0]] + (_r[3],)), "%d,%d,%s" % _r[1:4], "ut[%s]" % _r[0]) for _r in U26_ROWS] + ''',
    '''    [("ut." + _r[0], "%d,%d,%s" % (U26_OLD[_r[0]] + (_r[3],)), "%d,%d,%s" % ((UT_BANDS_V28[4] if _r[0] == "Hepta_Axe" else _r[1:3]) + (_r[3],)), "ut[%s]" % _r[0]) for _r in U26_ROWS] + ''')
rep('''assert [_dp.get(_k) for _k in H27_KEYS] == H27_NEW and DEFAULT_TEXT.count(H27_MARK_ID) == 1 and _dp.get("utdrop.dungeon") == UT_DUNG_DEF
assert _dp.get("ut.Weapon_Sword_UT_Paperweight") == "15,23,Hits 50% harder. Swings 40% slower." and _dp.get("ut.Hepta_Axe").startswith("39,47,Hits 54%")''',
    '''assert [_dp.get(_k) for _k in H27_KEYS if _k != "ut.Hepta_Axe"] == [_n for _k, _n in zip(H27_KEYS, H27_NEW) if _k != "ut.Hepta_Axe"] and DEFAULT_TEXT.count(H27_MARK_ID) == 1 and _dp.get("utdrop.dungeon") == UT_DUNG_DEF
assert _dp.get("ut.Weapon_Sword_UT_Paperweight") == "15,23,Hits 50% harder. Swings 40% slower." and _dp.get("ut.Hepta_Axe").startswith("75,83,Hits 54%")          # 0.3.29: Cinder 75-83''')
# loot.levelTop: the bags follow the bands up to 100 (49 was the top of the vanilla bands)
rep('''LOOT_TOP_DEF = VANILLA_TOP''', '''LOOT_TOP_DEF = 100          # 0.3.29: the bands run to 100+ (0.2.11 - 0.3.28: VANILLA_TOP 49)''')
rep('''    ("loot.levelTop", "Highest bag level", "loot", "int", "49", "1", "100", "", "", "live",
     "Bags never go above this level (49 = the top of the vanilla bands).", "field:GearCfg.LOOT_TOP"),''',
    '''    ("loot.levelTop", "Highest bag level", "loot", "int", str(LOOT_TOP_DEF), "1", "100", "", "", "live",
     "Bags never go above this level (100 = the top item level; 0.3.28 and older: 49).", "field:GearCfg.LOOT_TOP"),''')
# the level.material rows may run past 100 now (Lumen 95-103, Onyxium 100-108): the table limit 100 -> 200, one-number rows never past it
rep('''    ("level.material", "Level by material", "levels", "table", "", "0", "100", "int;type;Min|Cap", "", "live",''',
    '''    ("level.material", "Level by material", "levels", "table", "", "0", "200", "int;type;Min|Cap", "", "live",''')
rep('''     "A row with one number covers N to N+width-1 (8 = 5 levels + 3 overlap), never past 49.", "field:GearCfg.BAND_W"),''',
    '''     "A row with one number covers N to N+width-1 (8 = 5 levels + 3 overlap), never past 200.", "field:GearCfg.BAND_W"),''')
rep('''F(gcf, "public static final int VTOP = %d;" % VANILLA_TOP)''', '''F(gcf, "public static final int VTOP = %d;" % LEVEL_TOP)          # 0.3.29: the row limit (0.2 - 0.3.28: 49 = the vanilla top)''')
rep('''public static int capOf(int min, int w) {
  int c = min + (w < 1 ? 1 : w) - 1;
  if (min <= VTOP && c > VTOP) c = VTOP;
  if (c > 100) c = 100;
  return c < min ? min : c;
}""")''', '''public static int capOf(int min, int w) {
  int c = min + (w < 1 ? 1 : w) - 1;
  if (c > VTOP) c = VTOP;          // 0.3.29: never past the row limit (0.2 - 0.3.28: never past 49 while min <= 49, never past 100)
  return c < min ? min : c;
}""")''')
rep('''      int mn = (int) clampd(v0, 0.0, 100.0);
      int cp = mn;
      if (c != null) cp = capOf(mn, bw);
      else cp = (int) clampd(v1, 0.0, 100.0);''', '''      int mn = (int) clampd(v0, 0.0, 100.0);
      int cp = mn;
      if (c != null) cp = capOf(mn, bw);
      else cp = (int) clampd(v1, 0.0, (double) VTOP);          // 0.3.29: a cap may run past 100 (Lumen 95-103; item levels still stop at 100)''')
# the combat armor tag mirror (GearView.tierFor = tools/tier_tags.py LEVEL_BANDS) - proved over Lv 0-150
rep('''# tools/tier_tags.py tier_for_level (0.3.22: LEVEL_BANDS of the 15-step ladder - Lv 15 T2, 17 T3, 20 T4, 22 T5 ... 45 T14, 50 T15; Onyxium ids T16)''',
    '''# tools/tier_tags.py tier_for_level (0.3.29 TT_VERSION 3: Lv 8 T2, 15 T3, 20 T4, 28 T5 ... 88 T14, 95 T15; Onyxium ids T16; Crude word below Lv 5)''')
rep('''assert all(TT.tier_for_level(_lv) == next((_t for _l, _t in TT.LEVEL_BANDS if _lv >= _l), 1) for _lv in range(0, 101))''',
    '''assert all(TT.tier_for_level(_lv) == next((_t for _l, _t in TT.LEVEL_BANDS if _lv >= _l), 1) for _lv in range(0, 151))
assert TT.LEVEL_BANDS[0] == (95, 15) and TT.LEVEL_BANDS[-1] == (8, 2) and TT.LEVEL_CRUDE == 5, "0.3.29: the TT_VERSION 3 bands"''')
# the Sigil drop zone of a mob level = tools/tier_tags.py ZONE_TOPS (20 / 40 / 60; above = the Sigil table's last column, zone 4)
rep('''# the zone of a mob level (the chest-level bands: 1-20, 21-30, 31-45, 46+); no level = zone 1
M(gsigd, "public static int zoneOf(int lvl) { return lvl <= 20 ? 1 : (lvl <= 30 ? 2 : (lvl <= 45 ? 3 : 4)); }")''',
    '''# the zone of a mob level (0.3.29: tools/tier_tags.py ZONE_TOPS - 1-20, 21-40, 41-60, 61+ = zone 4, the Sigil table's last column; 0.3.28: 1-20,
# 21-30, 31-45, 46+); no level = zone 1
assert TT.ZONE_TOPS[:3] == (20, 40, 60)
M(gsigd, "public static int zoneOf(int lvl) { return lvl <= %d ? 1 : (lvl <= %d ? 2 : (lvl <= %d ? 3 : 4)); }" % TT.ZONE_TOPS[:3])''')

# ================================================================================================================ 2: the Bronze Mining set
rep('''ZM_LADDER = ["Copper", "Iron", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril", "Titanium",
             "Lumen", "Onyxium"]
MINE_ALL_TIERS = MINE_TIERS + ZM_TIERS
MINE_RANK = [ZM_LADDER.index(_t) for _t in MINE_ALL_TIERS]
assert sorted(ZM_LADDER) == sorted(MINE_ALL_TIERS) and ZM_BASE == 7 and len(ZM_IDS) == 32 and len(set(ZM_IDS)) == 32
''', '''# 0.3.29 (spec 3.3; Skyy 2026-10-18 "where is bronze? ... add it to this list"): the vanilla Bronze armor = Mining tier 15 (APPENDED: the saved tier
# indexes 0-14 stay), by exact id like the 7 vanilla sets, ranked between Iron and Thorium; band = level.material.Bronze (15-23, a vanilla tier:
# never garmor.zoneBands). (tier key, Fortune Head Chest Legs Hands, Wisdom %, lamp, full-set bonus): full Fortune 3.0 (Iron 2.3 < 3.0 < Thorium 3.8)
BZ_ROW = ("bronze", "0.2 0.4 0.2 0.2", "0 0 0 0", 2, "mfort+2 mpow+2.5")
BZ_IDS = ["Armor_Bronze_%s" % _s for _s in MINE_SLOTS]
ZM_N = len(ZM_TIERS)
BZ_BASE = len(MINE_TIERS) + ZM_N
for _k, _i in enumerate(BZ_IDS):
    _a = az_get(_i, "Armor")
    assert _i in AZ_ITEMS and isinstance(_a, dict) and _a.get("ArmorSlot") == MINE_SLOTS[_k], "Bronze mining armor %s: %s" % (_i, _a)
    assert az_get(_i, "ItemSoundSetId") == "ISS_Armor_Heavy", _i
    assert [_b.get("Id") for _b in (az_get(_i, "Recipe") or {}).get("BenchRequirement") or []] == ["TODO"], "vanilla Bronze armor got a real bench: " + _i
BZ_F, BZ_W, BZ_L = _slot_order(BZ_ROW[1]), _slot_order(BZ_ROW[2]), [BZ_ROW[3]]
ZM_LADDER = ["Copper", "Iron", "Bronze", "Thorium", "Lead", "Dusk", "Cobalt", "Chromium", "Azurvane", "Adamantite", "Slag", "Cinder", "Mithril", "Titanium",
             "Lumen", "Onyxium"]          # 0.3.29: + Bronze (T3) between Iron and Thorium
MINE_ALL_TIERS = MINE_TIERS + ZM_TIERS + ["Bronze"]
MINE_RANK = [ZM_LADDER.index(_t) for _t in MINE_ALL_TIERS]
assert sorted(ZM_LADDER) == sorted(MINE_ALL_TIERS) and ZM_BASE == 7 and len(ZM_IDS) == 32 and len(set(ZM_IDS)) == 32 and BZ_BASE == 15
assert [TT.metal_tier(_t) for _t in ZM_LADDER[:15]] == list(range(1, 16)) and MINE_ALL_TIERS.index("Bronze") == BZ_BASE
''')
rep('''_zall.update(dict((_r[1], (_slot_order(_r[4]), _slot_order(_r[5]), _mine_words(_r[7]))) for _r in ZM_ROWS))
''', '''_zall.update(dict((_r[1], (_slot_order(_r[4]), _slot_order(_r[5]), _mine_words(_r[7]))) for _r in ZM_ROWS))
_zall["Bronze"] = (BZ_F, BZ_W, _mine_words(BZ_ROW[4]))          # 0.3.29: the Bronze set climbs between Iron and Thorium
assert round(sum(BZ_F) + _mine_words(BZ_ROW[4])["mfort"], 2) == 3.0
''')
# the Heavy bags keep Steel / Heavy Leather / Ornate Bronze once the plain Bronze pieces are Mining pieces too
rep('''print("0.2.15 mining armor: %d pieces (%s); full-set Fortune %s (cap %g)" % (len(MINE_IDS), ", ".join(MINE_TIERS), _full, MINE_FCAP))''',
    '''print("0.2.15 mining armor: %d pieces (%s); full-set Fortune %s (cap %g)" % (len(MINE_IDS), ", ".join(MINE_TIERS), _full, MINE_FCAP))
for _s in MINE_SLOTS:          # 0.3.29: Armor_Bronze_<Slot> leaves the bags (GearMine.isPiece); the Heavy bags keep Steel / Heavy Leather / Ornate Bronze
    assert [_p[0] for _p in LOOT_POOL if _p[1] == "Armor_" + _s and _p[2] == 1 and _p[0] not in MINE_IDS and not _p[0].startswith("Armor_Bronze_" + _s)], \\
        "0.3.29: no Heavy %s left without the mining pieces + plain Bronze" % _s''')
rep('''F(gmine, "public static final String[] IDS = %s;" % jarr(MINE_IDS + ZM_IDS))          # 0.3.21: + the 32 zone pieces (tiers 7-14)''',
    '''F(gmine, "public static final String[] IDS = %s;" % jarr(MINE_IDS + ZM_IDS + BZ_IDS))          # 0.3.21: + the 32 zone pieces (tiers 7-14); 0.3.29: + Bronze (tier 15)''')
rep('''F(gmine, "public static final int ZBASE = %d;" % ZM_BASE)          # 0.3.21: the first zone tier''',
    '''F(gmine, "public static final int ZBASE = %d;" % ZM_BASE)          # 0.3.21: the first zone tier
F(gmine, "public static final int ZN = %d;" % ZM_N)          # 0.3.29: the zone tiers = ZBASE .. ZBASE + ZN - 1 (Bronze, tier 15, is a vanilla tier: level.material)''')
rep('''public static int[] zbandsOf(String s) {
  if (s == null) return null;
  int n = TIER.length - ZBASE;''', '''public static int[] zbandsOf(String s) {
  if (s == null) return null;
  int n = ZN;          // 0.3.29: Bronze (appended after the zone tiers) has no zone band''')
rep('''  if (i < 0 || i / 4 < ZBASE) return null;
  int[] b = zbands();''', '''  if (i < 0 || i / 4 < ZBASE || i / 4 >= ZBASE + ZN) return null;          // 0.3.29: Bronze keeps level.material
  int[] b = zbands();''')
rep('''F(gcf, "public static final double[] DGM_F = %s;" % _jd(MINE_F + ZM_F))
F(gcf, "public static final double[] DGM_W = %s;" % _jd(MINE_W + ZM_W))
F(gcf, "public static final int[] DGM_L = %s;" % jints(MINE_L + ZM_L))
F(gcf, "public static volatile Object[] GM_TAB = new Object[] { %s, %s, %s };" % (_jd(MINE_F + ZM_F), _jd(MINE_W + ZM_W), "new int[] { %s }" % ", ".join(str(x) for x in MINE_L + ZM_L)))''',
    '''F(gcf, "public static final double[] DGM_F = %s;" % _jd(MINE_F + ZM_F + BZ_F))          # 0.3.29: + Bronze (tier 15)
F(gcf, "public static final double[] DGM_W = %s;" % _jd(MINE_W + ZM_W + BZ_W))
F(gcf, "public static final int[] DGM_L = %s;" % jints(MINE_L + ZM_L + BZ_L))
F(gcf, "public static volatile Object[] GM_TAB = new Object[] { %s, %s, %s };" % (_jd(MINE_F + ZM_F + BZ_F), _jd(MINE_W + ZM_W + BZ_W), "new int[] { %s }" % ", ".join(str(x) for x in MINE_L + ZM_L + BZ_L)))''')
# the recipes: Iron's at the Armor Bench with Bronze Ingots 1:1 (spec Q5 default "Iron's amounts"), standalone assets like the 0.2 magic recipes
rep('''assert not [k for k in EXTRA if k.startswith("Server/Item/Items/")], "no vanilla item file is ever overridden (0.2.11: the bag items are added later)"
''', '''assert not [k for k in EXTRA if k.startswith("Server/Item/Items/")], "no vanilla item file is ever overridden (0.2.11: the bag items are added later)"
# 0.3.29 (spec 3.3, Q5 default): the Bronze Mining set is crafted at the Armor Bench with Iron's recipe, the Iron bar swapped 1:1 for the Bronze one
# (9 / 16 / 7 / 13 Bronze Ingots + Light Leather + Linen scraps); the vanilla TODO-bench recipe of Armor_Bronze_* stays unreachable
BZ_RECIPES = []
for _sl in ("Head", "Chest", "Hands", "Legs"):
    _ir = az_get("Armor_Iron_" + _sl, "Recipe")
    assert isinstance(_ir, dict) and set(_ir) <= set(RECIPE_KEYS) and [_x.get("ItemId") for _x in _ir["Input"]].count("Ingredient_Bar_Iron") == 1, _sl
    _out = "Armor_Bronze_" + _sl
    _r = {"Input": [{"ItemId": "Ingredient_Bar_Bronze" if _x.get("ItemId") == "Ingredient_Bar_Iron" else _x["ItemId"], "Quantity": _x["Quantity"]} for _x in _ir["Input"]],
          "PrimaryOutput": {"ItemId": _out, "Quantity": 1}, "Output": [{"ItemId": _out, "Quantity": 1}],
          "BenchRequirement": json.loads(json.dumps(_ir["BenchRequirement"])), "KnowledgeRequired": False, "TimeSeconds": _ir.get("TimeSeconds", 3)}
    assert [(_b["Id"], _b["Type"]) for _b in _r["BenchRequirement"]] == [("Armor_Bench", "Crafting")] and "Armor_Bench" in _BENCHES
    assert all(_c in _BENCHES["Armor_Bench"]["cats"] for _b in _r["BenchRequirement"] for _c in _b.get("Categories") or [])
    assert RECIPE_PREFIX + _out not in _ALL_RECIPE_IDS and _out in AZ_ITEMS and "Ingredient_Bar_Bronze" in AZ_ITEMS
    BZ_RECIPES.append((RECIPE_PREFIX + _out, _out, _r))
    EXTRA[RECIPE_DIR + RECIPE_PREFIX + _out + ".json"] = json.dumps(_r, indent=2)
assert [[_x["Quantity"] for _x in _r["Input"]] for _rid, _o, _r in BZ_RECIPES] == [[9, 4, 3], [16, 7, 6], [7, 3, 3], [13, 6, 4]], "spec 3.3: Iron's amounts"
print("0.3.29 Bronze Mining recipes: %s" % "; ".join("%s <- %s" % (_o, ", ".join("%s x%d" % (_x["ItemId"], _x["Quantity"]) for _x in _r["Input"])) for _rid, _o, _r in BZ_RECIPES))
''')

# ================================================================================================================ 3: 15 Foraging + 15 Farming tiers
# the 0.3.6 - 0.3.28 tables stay computed above (their asserts); right after them they are kept as _V28 (migrate0329's old defaults) and rebuilt
# from tools/tier_tags.py FORAGING_ARMOR / FARMING_ARMOR / FISHING_ARMOR (one table: ids, ladder T, looks, set names)
rep('''    GA2_LAD_DEF.append(",".join(_rows))
    assert len(GA2_LAD_DEF[-1]) < 2000 and all(32 <= ord(_c) < 127 for _c in GA2_LAD_DEF[-1])
''', '''    GA2_LAD_DEF.append(",".join(_rows))
    assert len(GA2_LAD_DEF[-1]) < 2000 and all(32 <= ord(_c) < 127 for _c in GA2_LAD_DEF[-1])
# ---- 0.3.29 (tools/gear_0_3_29_patch.py item 3; Skyy 2026-10-18 "we have 15 tiers of mining armor sets. we need to update foraging, and farming, to
# match"): Foraging + Farming = 15 sets at T1 .. T15, Fishing keeps 5 (T1 / T2 / T4 / T7 / T10). A set's family tier index t (0-based) = its place
# in its family; GA2_LT = its ladder T (the band = tools/tier_tags.py METAL_BANDS of that T). Old ids + set ids (stored in documents) unchanged.
GA2_BANDS_V28, GA2_STAT_V28, GA2_LAD_V28 = GA2_BANDS_DEF, list(GA2_STAT_DEF), list(GA2_LAD_DEF)
GA2_IDS_V28 = list(GA2_IDS)
_ga2rows = [TT.FORAGING_ARMOR, TT.FARMING_ARMOR, TT.FISHING_ARMOR]
GA2_N = [len(_r) for _r in _ga2rows]
GA2_LT = [[_x[0] for _x in _r] for _r in _ga2rows]
GA2_IDC = [[_x[1] for _x in _r] for _r in _ga2rows]
GA2_LOOK = [[_x[2] for _x in _r] for _r in _ga2rows]
GA2_SNAME = [[_x[3] for _x in _r] for _r in _ga2rows]
assert GA2_N == [15, 15, 5] and GA2_LT[0] == GA2_LT[1] == list(range(1, 16)) and GA2_LT[2] == [1, 2, 4, 7, 10]
# the Health / durability row of a set = the highest vanilla armor metal at or below its T (T3 = Iron; Bronze armor is Iron's numbers anyway)
_GA2_VM = [("Copper", 1), ("Iron", 2), ("Thorium", 4), ("Cobalt", 7), ("Adamantite", 10), ("Mithril", 13), ("Onyxium", 16)]
GA2_RMET = [[[_m for _m, _t in _GA2_VM if _t <= _lt][-1] for _lt in _l] for _l in GA2_LT]
assert GA2_RMET[2] == ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite"] and GA2_RMET[0][2] == "Iron" and GA2_RMET[1][13] == "Mithril"
GA2_IDS, GA2_IFAM, GA2_ITIER, GA2_ISLOT = [], [], [], []
GA2_SETS, GA2_SFAM, GA2_STIER, GA2_SNAMES = [], [], [], []
GA2_FOFF, GA2_ILT = [], []
for _f in range(3):
    GA2_FOFF.append(len(GA2_SETS))
    for _t in range(GA2_N[_f]):
        GA2_SETS.append("%s_%s" % (GA2_FAMS[_f], GA2_IDC[_f][_t].lower()))          # foraging_f1 .. f5 / farming_p1 .. p7 / fishing_a1 .. a5 kept
        GA2_SFAM.append(_f)
        GA2_STIER.append(_t)
        GA2_SNAMES.append(GA2_SNAME[_f][_t])
        for _s, _sl in enumerate(GA2_SLOTS):
            GA2_IDS.append(TT.gather_armor_id(GA2_SKILL[_f], GA2_IDC[_f][_t], _sl))
            GA2_IFAM.append(_f)
            GA2_ITIER.append(_t)
            GA2_ISLOT.append(_s)
            GA2_ILT.append(GA2_LT[_f][_t])
assert len(GA2_IDS) == 140 and len(GA2_SETS) == 35 and GA2_FOFF == [0, 15, 30] and len(set(GA2_IDS)) == 140 and set(GA2_IDS_V28) < set(GA2_IDS)
assert sorted(GA2_IDS) == sorted(TT.GA_IDS) and all(TT.tier(_i) == _lt and TT.owner(_i) == "SkyyGear" for _i, _lt in zip(GA2_IDS, GA2_ILT))
assert not set(GA2_IDS) & AZ_ITEMS, "a gathering armor id is a vanilla item"
assert [GA2_LT[0][GA2_IDC[0].index("F%d" % _k)] for _k in range(1, 6)] == [1, 3, 6, 9, 12]
assert [GA2_LT[1][GA2_IDC[1].index("P%d" % _k)] for _k in range(1, 8)] == [1, 3, 5, 7, 10, 11, 14]
assert [_s for _s in GA2_SETS if _s[-1].isdigit()] == ["foraging_f%d" % _k for _k in range(1, 6)] + ["farming_p%d" % _k for _k in range(1, 8)] + ["fishing_a%d" % _k for _k in range(1, 6)]
# the bands = METAL_BANDS by ladder T (15 ranges; Fishing reads its tiers' T)
GA2_BANDS_DEF = ",".join("%d-%d" % TT.band(TT.noun(_t)) for _t in range(1, 16))
assert GA2_BANDS_DEF == "1-8,8-15,15-23,20-28,28-35,35-43,40-48,48-55,55-63,60-68,68-75,75-83,80-88,88-95,95-103", GA2_BANDS_DEF


# the per-tier numbers: today's points stay on the old sets (their new T), straight lines between them, the slope of the last step past the end
def _ga2line(pts, n):
    xs = sorted(pts)
    out = []
    for _x in range(1, n + 1):
        if _x in pts:
            out.append(float(pts[_x]))
            continue
        lo = [_p for _p in xs if _p < _x]
        hi = [_p for _p in xs if _p > _x]
        if lo and hi:
            a, b = lo[-1], hi[0]
        else:
            a, b = (xs[-2], xs[-1]) if not hi else (xs[0], xs[1])
        out.append(round(pts[a] + (pts[b] - pts[a]) * float(_x - a) / (b - a), 1))
    return out


def _ga2fmt(v):
    return ("%g" % round(v, 2))


_ga2old = [[[float(_v) for _v in _c.split(",")] for _c in _x.split("|")] for _x in GA2_STAT_V28]
_ga2oldT = [[1, 3, 6, 9, 12], [1, 3, 5, 7, 10, 11, 14]]          # the old sets' new T (Foraging F1-F5, Farming P1-P7)
GA2_STAT_DEF = []
for _f in range(2):
    _cols = [_ga2line(dict(zip(_ga2oldT[_f], _col)), 15) for _col in _ga2old[_f]]
    for _col in _cols:
        assert all(_b >= _a for _a, _b in zip(_col, _col[1:])), "0.3.29 gathering numbers go down: %s" % _col
    GA2_STAT_DEF.append("|".join(",".join(_ga2fmt(_v) for _v in _col) for _col in _cols))
GA2_STAT_DEF.append(GA2_STAT_V28[2])          # Fishing: unchanged (5 sets)
for _f in range(2):
    _new = [[float(_v) for _v in _c.split(",")] for _c in GA2_STAT_DEF[_f].split("|")]
    assert all(_new[_c][_t - 1] == _ga2old[_f][_c][_k] for _c in range(3) for _k, _t in enumerate(_ga2oldT[_f])), "0.3.29: an old set's numbers moved"
for _f in range(3):
    _cols = GA2_STAT_DEF[_f].split("|")
    assert len(_cols) == (4 if _f == 2 else 3) and all(len(_c.split(",")) == GA2_N[_f] for _c in _cols)
print("0.3.29 gathering armor numbers: Foraging %s | Farming %s" % (GA2_STAT_DEF[0], GA2_STAT_DEF[1]))
# tier-up costs: the Enchanted item of the NEW tier's tree / crop (round C1 made every collection's own Enchanted item)
_GA2_EK = {"Crystalwood": "CrystalLog"}
GA2_STEPS = [[_GA2_EK.get(_l, _l) for _l in GA2_LOOK[0][1:]], [_GA2_EK.get(_l, _l) for _l in GA2_LOOK[1][1:]], ["Iron", "Thorium", "Cobalt", "Adamantite"]]
GA2_LAD_DEF = []
for _f in range(3):
    assert len(GA2_STEPS[_f]) == GA2_N[_f] - 1
    _rows = []
    for _sl in GA2_SLOTS:
        _row = TT.gather_armor_id(GA2_SKILL[_f], GA2_IDC[_f][0], _sl)
        for _j, _k in enumerate(GA2_STEPS[_f]):
            _row += ">%s(%s)" % (TT.gather_armor_id(GA2_SKILL[_f], GA2_IDC[_f][_j + 1], _sl), _lle(_k, GA2_CN[_sl][0 if _j < 2 else 1]))
        _rows.append(_row)
    GA2_LAD_DEF.append(",".join(_rows))
    assert len(GA2_LAD_DEF[-1]) < 4000 and all(32 <= ord(_c) < 127 for _c in GA2_LAD_DEF[-1])
assert GA2_LAD_DEF[2] == GA2_LAD_V28[2], "0.3.29: the Fishing ladder is unchanged"
# the art of every Foraging set: our approved per-tree models (art/gathering-armor/manifest.json, folder <F tier>/<tree>)
_ga2man = json.load(open(os.path.join(os.path.dirname(HERE), "art", "gathering-armor", "manifest.json"), encoding="utf-8"))
GA2_ARTDIR = dict((_v["tree"], _v["tier"]) for _k, _v in _ga2man["sets"].items())
assert all(_l in GA2_ARTDIR for _l in GA2_LOOK[0]), "art/gathering-armor has no set for %s" % [_l for _l in GA2_LOOK[0] if _l not in GA2_ARTDIR]
# the 8 new Farming placeholder recolours (Quirk draws the real crop sets later - spec Q14)
GA2_RAMP.update({"Lettuce": ("#2e5a1c", "#6fb43c", "#c8f0a0"), "Corn": ("#7a5a10", "#e8c030", "#fff0a0"), "Turnip": ("#5a2a5a", "#c890c8", "#f4e4f0"),
                 "Aubergine": ("#2a1238", "#6a2c8c", "#c49ae0"), "Tomato": ("#6a1008", "#e03a24", "#ffb0a0"), "Rice": ("#6a6450", "#e0dcc4", "#fbf8ec"),
                 "Potato": ("#5a3e1e", "#b08850", "#ecd6a8"), "Mushroom": ("#4a2a1a", "#a86a44", "#ecc8a8")})
assert all(_l in GA2_RAMP for _l in GA2_LOOK[1] + GA2_LOOK[2])
''')
rep('''GA2_BAND_LO = [int(_b.split("-")[0]) for _b in GA2_BANDS_DEF.split(",")]''',
    '''GA2_BAND_LO = [int(_b.split("-")[0]) for _b in GA2_BANDS_DEF.split(",")]          # 0.3.29: by ladder T - 1''')
rep('''    _row = _ga2j("Armor_%s_%s" % (GA2_ROWMETAL[_t], _sl))''', '''    _row = _ga2j("Armor_%s_%s" % (GA2_RMET[_f][_t], _sl))          # 0.3.29: the metal row of the set's ladder T''')
rep('''    _bj["ItemLevel"] = GA2_BAND_LO[_t]''', '''    _bj["ItemLevel"] = GA2_BAND_LO[GA2_LT[_f][_t] - 1]''')
rep('''        _rel = "Items/Armors/SkyyForaging/%s/%s/%s" % (GA2_FTIER[_t], _look, _sl)''', '''        _rel = "Items/Armors/SkyyForaging/%s/%s/%s" % (GA2_ARTDIR[_look], _look, _sl)          # 0.3.29: the tree's own art folder''')
rep('''    GA2_LANG.append("items.%s.description = %s set - %s armor. It levels with your %s and tiers up on the Anvil." % (_id, GA2_SNAME[_f][_t], GA2_SKILL[_f], GA2_SKILL[_f]))''',
    '''    GA2_LANG.append("items.%s.description = %s" % (_id, TT.described(_id, "%s set - %s armor. It levels with your %s and tiers up on the Anvil." % (GA2_SNAME[_f][_t], GA2_SKILL[_f], GA2_SKILL[_f]))))          # 0.3.29: the tier tag first''')
# the Server Setup rows: 15 ranges, longer ladder texts
rep('''    ("garmor.bands", "Gathering armor levels per tier", "garmor", "text", GA2_BANDS_DEF, "0", "200", "", "", "live,danger",
     "Level band of tiers 1-7 of the Foraging, Farming and Fishing sets: 7 min-max pairs.", "field:GearCfg.GA_BANDS;check=GearGArm.checkBands"),''',
    '''    ("garmor.bands", "Gathering armor levels per tier", "garmor", "text", GA2_BANDS_DEF, "0", "300", "", "", "live,danger",
     "Level band of T1-T15 for the Foraging, Farming and Fishing sets: 15 min-max pairs.", "field:GearCfg.GA_BANDS;check=GearGArm.checkBands"),''')
rep('''    ("garmor.ladders.foraging", "Foraging armor tier-up costs", "garmor", "text", GA2_LAD_DEF[0], "0", "2000", "", "", "live,danger",''',
    '''    ("garmor.ladders.foraging", "Foraging armor tier-up costs", "garmor", "text", GA2_LAD_DEF[0], "0", "4000", "", "", "live,danger",''')
rep('''    ("garmor.ladders.farming", "Farming armor tier-up costs", "garmor", "text", GA2_LAD_DEF[1], "0", "2000", "", "", "live,danger",''',
    '''    ("garmor.ladders.farming", "Farming armor tier-up costs", "garmor", "text", GA2_LAD_DEF[1], "0", "4000", "", "", "live,danger",''')
# GearGArm: the ladder T per piece, 15 bands
rep('''F(gga, "public static final int[] ISLOT = %s;" % jints(GA2_ISLOT))''', '''F(gga, "public static final int[] ISLOT = %s;" % jints(GA2_ISLOT))
F(gga, "public static final int[] ILT = %s;" % jints(GA2_ILT))          # 0.3.29: the ladder T of each piece (the band row)
F(gga, "public static final int NB = 15;")          # 0.3.29: garmor.bands = T1 .. T15''')
rep('''# "1-18,15-23,..." -> int[14] (min, max of tiers 1-7); null = bad
M(gga, r"""
public static int[] bandsOf(String s) {
  if (s == null) return null;
  String[] ps = s.trim().split(",", -1);
  if (ps.length != 7) return null;
  int[] o = new int[14];
  for (int i = 0; i < 7; i++) {''', '''# "1-8,8-15,..." -> int[30] (min, max of T1-T15; 0.3.6 - 0.3.28: 7 tiers); null = bad
M(gga, r"""
public static int[] bandsOf(String s) {
  if (s == null) return null;
  String[] ps = s.trim().split(",", -1);
  if (ps.length != NB) return null;
  int[] o = new int[NB * 2];
  for (int i = 0; i < NB; i++) {''')
rep('''    @PKG@.Gear.warnOnce("garmorb:" + s, "config.properties: garmor.bands=" + s + " is not 7 level ranges - the default " + BANDS_DEF + " is used");''',
    '''    @PKG@.Gear.warnOnce("garmorb:" + s, "config.properties: garmor.bands=" + s + " is not " + NB + " level ranges - the default " + BANDS_DEF + " is used");''')
rep('''  int[] b = bands();
  int t = ITIER[i];
  return new int[] { b[t * 2], b[t * 2 + 1] };''', '''  int[] b = bands();
  int t = ILT[i] - 1;          // 0.3.29: the piece's ladder T (Fishing: T1 / T2 / T4 / T7 / T10)
  return new int[] { b[t * 2], b[t * 2 + 1] };''')
rep('''  if (bandsOf(value) == null) return "Write 7 level ranges min-max for tiers 1-7, e.g. " + BANDS_DEF + ".";''',
    '''  if (bandsOf(value) == null) return "Write " + NB + " level ranges min-max for T1-T" + NB + ", e.g. " + BANDS_DEF + ".";''')

# ================================================================================================================ 4: Vein Mine / Tree Feller tool levels 4, 8, 16, 24, 32, 40
AB_LV_DEF = "4,8,16,24,32,40"
rep('''    ("lifelong.abilityLevelStep", "Tool levels per ability level", "lifelong", "int", "8", "1", "49", "", "", "live,danger",
     "Vein Mine / Tree Feller level n needs tool level n x this (8: Lv 8, 16, 24 ...).", "field:GearCfg.LL_ABSTEP"),''',
    '''    ("lifelong.abilityLevelStep", "Tool levels per ability level", "lifelong", "int", "8", "1", "49", "", "", "live,danger",
     "Tool levels per Vein Mine / Tree Feller level past lifelong.abilityLevels (empty list: n x this).", "field:GearCfg.LL_ABSTEP"),
    # 0.3.29 (Skyy 2026-10-18 "first vein mine and tree feller at lvl 4. second at lvl 8 3rd at lvl 16 and so on" + "+8 after 16: 4,8,16,24,32,40")
    ("lifelong.abilityLevels", "Tool level for each ability level", "lifelong", "text", AB_LV_DEF, "0", "200", "", "", "live,danger",
     "Tool level for Vein Mine / Tree Feller level 1, 2, 3 ... (4,8,16,24,32,40). Empty = n x the step.",
     "field:GearCfg.LL_ABLV;check=GearLL.checkAbLv"),''')
rep('''           "unid.typeAtIdentify"}          # 0.3.28: what a weapon bag turns into (items)''',
    '''           "unid.typeAtIdentify",          # 0.3.28: what a weapon bag turns into (items)
           "lifelong.abilityLevels"}          # 0.3.29: when Vein Mine / Tree Feller open (gathering speed = economy)''')
rep('''("LL_ABSTEP", "int", "8"),''', '''("LL_ABSTEP", "int", "8"), ("LL_ABLV", "String", jstr(AB_LV_DEF)),''')
rep('''  LL_ABSTEP = (int) plong(p, "lifelong.abilityLevelStep", 8L, 1L, 49L);''', '''  LL_ABSTEP = (int) plong(p, "lifelong.abilityLevelStep", 8L, 1L, 49L);
  LL_ABLV = ptext(p, "lifelong.abilityLevels", "%s").trim();          // 0.3.29 (checked where it is used: a bad text = one WARN + the default)''' % AB_LV_DEF)
rep('''M(gll, r"""
public static int abilCap(java.util.UUID u, java.util.Properties P, int k) {''', '''# 0.3.29 (Skyy "4,8,16,24,32,40"): the tool level ability level n needs = lifelong.abilityLevels[n - 1]; past the list + lifelong.abilityLevelStep
# each; an empty list = the 0.3.17 rule n x lifelong.abilityLevelStep. Parsed lazily (re-parsed when the text changes; bad = one WARN + the default)
F(gll, "public static volatile Object[] ABLC = null;")
M(gll, r"""
public static int[] abParse(String s) {
  if (s == null) return new int[0];
  String t = s.trim();
  if (t.length() == 0) return new int[0];
  String[] ps = t.split(",", -1);
  if (ps.length > 20) return null;
  int[] o = new int[ps.length];
  for (int i = 0; i < ps.length; i++) {
    try { o[i] = Integer.parseInt(ps[i].trim()); } catch (Throwable x) { return null; }
    if (o[i] < 1 || o[i] > 200 || (i > 0 && o[i] <= o[i - 1])) return null;
  }
  return o;
}""")
M(gll, r"""
public static int[] abLv() {
  String s = @PKG@.GearCfg.LL_ABLV;
  Object[] e = ABLC;
  if (e != null && s != null && s.equals(e[0])) return (int[]) e[1];
  int[] a = abParse(s);
  if (a == null) {
    @PKG@.Gear.warnOnce("ablv:" + s, "config.properties: lifelong.abilityLevels=" + s + " is not rising tool levels 1-200 - the default %s is used");
    a = abParse("%s");
  }
  ABLC = new Object[] { s, a };
  return a;
}""" % (AB_LV_DEF, AB_LV_DEF))
M(gll, r"""
public static int abNeed(int n) {
  if (n < 1) return 0;
  int st = @PKG@.GearCfg.LL_ABSTEP < 1 ? 1 : @PKG@.GearCfg.LL_ABSTEP;
  int[] a = abLv();
  if (a.length == 0) return n * st;
  if (n <= a.length) return a[n - 1];
  return a[a.length - 1] + (n - a.length) * st;
}""")
M(gll, r"""
public static int abilCapLv(int lv, int mx) {
  int c = 0;
  while (c < mx && abNeed(c + 1) <= lv) c++;
  return c;
}""")
M(gll, "public static String checkAbLv(String key, String value) { return abParse(value) == null ? \\"Write rising tool levels 1-200 joined by commas (like %s), or leave it empty for level n x lifelong.abilityLevelStep.\\" : null; }" % AB_LV_DEF)
M(gll, r"""
public static int abilCap(java.util.UUID u, java.util.Properties P, int k) {''')
rep('''  int lv = u == null ? -1 : levelK(u, k, id);
  if (lv < 0) return mx;
  int st = @PKG@.GearCfg.LL_ABSTEP < 1 ? 1 : @PKG@.GearCfg.LL_ABSTEP;
  int c = lv / st;
  return c < mx ? c : mx;
}""")''', '''  int lv = u == null ? -1 : levelK(u, k, id);
  if (lv < 0) return mx;
  return abilCapLv(lv, mx);          // 0.3.29: lifelong.abilityLevels (0.3.17 - 0.3.28: lv / lifelong.abilityLevelStep)
}""")''')
rep('''M(gll, "public static int pkNeedLv(int p, int lvl) { return isAbil(p) && lvl >= 1 ? lvl * (@PKG@.GearCfg.LL_ABSTEP < 1 ? 1 : @PKG@.GearCfg.LL_ABSTEP) : 0; }")''',
    '''M(gll, "public static int pkNeedLv(int p, int lvl) { return isAbil(p) && lvl >= 1 ? abNeed(lvl) : 0; }")          # 0.3.29: lifelong.abilityLevels''')

# ================================================================================================================ migrate0329
after('''assert all(32 <= ord(_c) < 127 for _c in H28_MARK) and "=" not in H28_MARK and H28_MARK.startswith("# ")
''', '''# 0.3.29 ONE-TIME UPDATE migrate0329 (tools/gear_0_3_29_patch.py): the 0.3.28 defaults -> 20 levels per zone, 15 Foraging / Farming tiers, bags to 100;
# then a pure addition at the END (the Bronze Mining rows a file lacks; lifelong.abilityLevels empty when lifelong.abilityLevelStep was hand edited)
G329_HEAD = "# ---- 20 levels per zone, the Bronze Mining set, 15 Foraging / Farming tiers, Vein Mine / Tree Feller at tool Lv 4, 8, 16 ... (SkyyGear 0.3.29) ----"
G329_ROWK = ["lifelong.abilityLevels"]
H29_MARK_ID = "SkyyGear 0.3.29 level bands update"
H29_WHO = "SkyyGear 0.3.29"
H29_MARK = ("# %s (Skyy 2026-10-18): 20 levels per zone - Copper 1-8, Iron 8-15, Bronze 15-23, Thorium 20-28 ... Lumen 95-103 on every tool, weapon and "
            "armor band; the Bronze Mining set; 15 Foraging and 15 Farming armor tiers; bags up to Lv 100" % H29_MARK_ID)
assert all(32 <= ord(_c) < 127 for _c in G329_HEAD + H29_MARK) and "=" not in G329_HEAD + H29_MARK and H29_MARK.startswith("# ")
H29_ROWS = []          # (key, old text, new text, change-log key, log old, log new)
for (_t0, _s0, _c0), (_t1, _s1, _c1) in zip(BANDS_V28 + FAM_BANDS_V28 + ST_BANDS_V28, BANDS + FAM_BANDS + ST_BANDS):
    assert _t0 == _t1
    if (_s0, _c0) != (_s1, _c1):
        H29_ROWS.append(("level.material." + _t0, band_text(_s0, _c0), band_text(_s1, _c1), "level.material[%s]" % _t0, "%d|%d" % (_s0, _c0), "%d|%d" % (_s1, _c1)))
for (_t0, _s0, _c0), (_t1, _s1, _c1) in zip(G22_BANDS_V28, G22_BANDS):
    assert _t0 == _t1 and (_s0, _c0) != (_s1, _c1)
    H29_ROWS.append(("level.material.%s_SkyWynn" % _t0, band_text(_s0, _c0), band_text(_s1, _c1), "level.material[%s_SkyWynn]" % _t0, "%d|%d" % (_s0, _c0), "%d|%d" % (_s1, _c1)))
_hepta = [_r for _r in U26_ROWS if _r[0] == "Hepta_Axe"][0]
for _k, _o, _n in (("garmor.zoneBands", ZM_BANDS_V28, ZM_BANDS_DEF), ("garmor.bands", GA2_BANDS_V28, GA2_BANDS_DEF),
                   ("garmor.foraging", GA2_STAT_V28[0], GA2_STAT_DEF[0]), ("garmor.farming", GA2_STAT_V28[1], GA2_STAT_DEF[1]),
                   ("garmor.ladders.foraging", GA2_LAD_V28[0], GA2_LAD_DEF[0]), ("garmor.ladders.farming", GA2_LAD_V28[1], GA2_LAD_DEF[1]),
                   ("loot.levelTop", "49", str(LOOT_TOP_DEF))):
    H29_ROWS.append((_k, _o, _n, _k, _o, _n))
H29_ROWS.append(("ut.Hepta_Axe", "%d,%d,%s" % (UT_BANDS_V28[4] + (_hepta[3],)), "%d,%d,%s" % _hepta[1:4], "ut[Hepta_Axe]",
                 "%d|%d|%s" % (UT_BANDS_V28[4] + (_hepta[3],)), "%d|%d|%s" % _hepta[1:4]))
H29_KEYS = [_r[0] for _r in H29_ROWS]
H29_OLD = [_r[1] for _r in H29_ROWS]
H29_NEW = [_r[2] for _r in H29_ROWS]
H29_LK = [_r[3] for _r in H29_ROWS]
H29_LO = [_r[4] for _r in H29_ROWS]
H29_LN = [_r[5] for _r in H29_ROWS]
H29_SAME = sorted(_t0 for (_t0, _s0, _c0), (_t1, _s1, _c1) in zip(BANDS_V28 + FAM_BANDS_V28 + ST_BANDS_V28, BANDS + FAM_BANDS + ST_BANDS) if (_s0, _c0) == (_s1, _c1))
assert H29_SAME == sorted(["Bronze", "Thorium", "Silk", "Leather_Heavy", "Leather_Raven", "Steel", "Incandescent", "Zombie", "Katana", "Nexus", "Runic",
                           "Kunai", "Grimoire", "Wizard"]), H29_SAME          # Bronze 15-23, Thorium 20-28 and the 20-27 families keep their band
assert len(set(H29_KEYS)) == len(H29_KEYS) and all(_o != _n for _o, _n in zip(H29_OLD, H29_NEW))
assert sum(1 for _k in H29_KEYS if _k.startswith("level.material.")) == 82 - len(H29_SAME), "11 metal + 59 family + 4 starter + 8 zone metal rows, minus the unchanged ones"
assert all(32 <= ord(_c) < 127 for _x in H29_OLD + H29_NEW + H29_LK + H29_LO + H29_LN for _c in _x)
assert all("\\\\" not in _x and "\\n" not in _x and "\\t" not in _x for _x in H29_OLD + H29_NEW + H29_LK + H29_LO + H29_LN)
assert H29_OLD[H29_KEYS.index("level.material.Copper")] == "10,18" and H29_NEW[H29_KEYS.index("level.material.Copper")] == "1,8"
# the pure addition: (key, comment, line, only when this key ..., ... holds something else than this)
H29_ADD = [("garmor.mining.bronze", "# 0.3.29 the Bronze Mining set (Fortune Head Chest Legs Hands, Wisdom %, lamp): between Iron and Thorium",
            "garmor.mining.bronze=%s,%s,%d" % BZ_ROW[1:4], "", ""),
           ("set.mining_bronze", "# 0.3.29 the Bronze Mining Set: all 4 pieces worn give the bonus, pickaxe or shovel in hand",
            "set.mining_bronze=Bronze Mining Set,4,%s" % BZ_ROW[4], "", ""),
           ("lifelong.abilityLevels", "# 0.3.29: empty, so Vein Mine / Tree Feller keep your lifelong.abilityLevelStep rule (level n x the step)",
            "lifelong.abilityLevels=", "lifelong.abilityLevelStep", "8")]
H29_ADDK = [_a[0] for _a in H29_ADD]
H29_ADDC = [_a[1] for _a in H29_ADD]
H29_ADDL = [_a[2] for _a in H29_ADD]
H29_ADDIF = [_a[3] for _a in H29_ADD]
H29_ADDIFV = [_a[4] for _a in H29_ADD]
assert all(32 <= ord(_c) < 127 for _x in H29_ADDC + H29_ADDL for _c in _x) and all(_c.startswith("# ") and "=" not in _c for _c in H29_ADDC)
_rowdef = dict((r[0], r[4]) for r in CFG_ROWS)
assert _rowdef["loot.levelTop"] == "100" and _rowdef["garmor.bands"] == GA2_BANDS_DEF and _rowdef["garmor.zoneBands"] == ZM_BANDS_DEF and _rowdef["lifelong.abilityLevels"] == AB_LV_DEF
''')
after('''F(gcf, "public static final String[] H28_NEW = %s;" % jarr(H28_NEW))
''', '''F(gcf, "public static final String H29_MARK = %s;" % jstr(H29_MARK))          # 0.3.29 migrate0329
F(gcf, "public static final String H29_MARK_ID = %s;" % jstr(H29_MARK_ID))
F(gcf, "public static final String H29_WHO = %s;" % jstr(H29_WHO))
for _n29, _v29 in (("KEYS", H29_KEYS), ("OLD", H29_OLD), ("NEW", H29_NEW), ("LK", H29_LK), ("LO", H29_LO), ("LN", H29_LN), ("ADDK", H29_ADDK),
                   ("ADDC", H29_ADDC), ("ADDL", H29_ADDL), ("ADDIF", H29_ADDIF), ("ADDIFV", H29_ADDIFV)):
    F(gcf, "public static final String[] H29_%s = %s;" % (_n29, jarr(_v29)))
''')
# the fresh file: the 0.3.29 block (marker, the new row, the Bronze Mining rows) after the 0.3.28 one
rep('''    L += ["", G328_HEAD, H28_MARK]        # 0.3.28: the migrate0328 marker (the three Fortune rows keep their places above) + the new row
    for k in G328_ROWK:
        scal(k)''', '''    L += ["", G328_HEAD, H28_MARK]        # 0.3.28: the migrate0328 marker (the three Fortune rows keep their places above) + the new row
    for k in G328_ROWK:
        scal(k)
    L += ["", G329_HEAD, H29_MARK]        # 0.3.29: the migrate0329 marker (the re-banded rows keep their places above) + the new row + Bronze
    for k in G329_ROWK:
        scal(k)
    for _a in H29_ADD[:2]:
        L += [_a[1], _a[2]]''')
after('''assert _dp.get("unid.typeAtIdentify") == "true", "0.3.28: the fresh file's unid.typeAtIdentify row"
''', '''assert [_dp.get(_k) for _k in H29_KEYS] == H29_NEW and DEFAULT_TEXT.count(H29_MARK_ID) == 1, "0.3.29: the fresh file holds the new bands + the marker once"
assert _dp.get("lifelong.abilityLevels") == AB_LV_DEF and _dp.get("garmor.mining.bronze") == "0.2 0.4 0.2 0.2,0 0 0 0,2" and _dp.get("set.mining_bronze") == "Bronze Mining Set,4,mfort+2 mpow+2.5"
assert _dp.get("level.material.Onyxium") == "100,108" and _dp.get("level.material.Lumen_SkyWynn") == "95,103" and _dp.get("level.material.Prisma") == "91,98"
''')
rep('''assert DEFAULT_TEXT.count(FM_MARK_ID) == 1 and _DL[_DL.index("level.material.Onyxium=40,49") + 1] == FM_MARK''',
    '''assert DEFAULT_TEXT.count(FM_MARK_ID) == 1 and _DL[_DL.index("level.material.Onyxium=100,108") + 1] == FM_MARK          # 0.3.29: the new Onyxium band''')
rep('''assert _DL[_DL.index("level.material.Copper=10,18") + 1] == "level.material.Armor_Copper=1,18"''',
    '''assert _DL[_DL.index("level.material.Copper=1,8") + 1] == "level.material.Armor_Copper=1,8"          # 0.3.29''')

# Java: h29Update / h29Log / migrate0329 = the migrate0327 machinery (copied from THIS script: text compare h23Old, table change-log keys) + the addition
_a = s.index('M(gcf, r"""\npublic static Object[] h27Update(String text) {')
_b = s.index('public static synchronized String migrate0327() {')
_b = s.index('}""")\n', _b) + len('}""")\n')
J27 = s[_a:_b]
J29 = J27.replace("H27_", "H29_").replace("h27Update", "h29Update").replace("h27Log", "h29Log").replace("migrate0327", "migrate0329")
for _o, _n in [
        ('''  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(H29_MARK);''', '''  java.util.ArrayList blk = new java.util.ArrayList();
  int nad = 0;
  for (int i = 0; i < H29_ADDK.length; i++) {
    if (pp.getProperty(H29_ADDK[i]) != null) continue;
    if (H29_ADDIF[i].length() > 0) {
      String cv = pp.getProperty(H29_ADDIF[i]);
      if (cv == null || h23Old(cv, H29_ADDIFV[i])) continue;
      notes.add(H29_ADDIF[i] + "=" + @PKG@.CfgRows.oneLine(cv.trim()) + " is a hand edit - " + H29_ADDK[i] + " was added empty, so Vein Mine / Tree Feller keep level n x " + @PKG@.CfgRows.oneLine(cv.trim()) + " (the new default is 4,8,16,24,32,40)");
    }
    blk.add(H29_ADDC[i]);
    blk.add(H29_ADDL[i]);
    nad++;
  }
  blk.add(H29_MARK);'''),
        ('''  String chg = nch == 0 ? "" : nch + " rows (Untiered level bands" + (at.containsValue(H29_NEW[nk - 1]) ? ", luggage share" : "") + ")";''',
         '''  String chg = (nch == 0 ? "" : nch + " rows (20 levels per zone: level bands, gathering armor tiers, bag top)") + (nad == 0 ? "" : (nch == 0 ? "" : "; ") + nad + " rows added (the Bronze Mining set" + (nad > 2 ? ", the old Vein Mine step" : "") + ")");'''),
        ('" kept (not the 0.3.26 default, or not one plain line) - the new default is "', '" kept (not the 0.3.28 default, or not one plain line) - the new default is "'),
        ("(Undo puts the 0.3.26 value back)", "(Undo puts the 0.3.28 value back)"),
        ("# setup(), right after migrate0326 and BEFORE load()", "# setup(), right after migrate0328 and BEFORE load()"),
        ('"before the 0.3.27 Untiered sources update"', '"before the 0.3.29 level bands update"'),
        ('"config.properties NOT updated to the 0.3.27 Untiered bands: the old file', '"config.properties NOT updated to the 0.3.29 level bands: the old file'),
        ('''"config.properties updated to the 0.3.27 defaults: " + chg + " (each zone's Untiered items at its alloy band, no orange luggage; Undo''',
         '''"config.properties updated to the 0.3.29 defaults: " + chg + " (20 levels per zone, the Bronze Mining set, 15 Foraging / Farming tiers; Undo'''),
        ('"config.properties: the 0.3.27 Untiered update marker was added - no value changed"', '"config.properties: the 0.3.29 level bands update marker was added - no value changed"'),
        ('"CONFIG 0.3.27 Untiered sources: "', '"CONFIG 0.3.29 level bands: "'),
        ('"could not update config.properties to the 0.3.27 Untiered bands (the file', '"could not update config.properties to the 0.3.29 level bands (the file'),
]:
    assert J29.count(_o) == 1, _o[:120]
    J29 = J29.replace(_o, _n)
assert "0.3.26" not in J29 and "0.3.27" not in J29 and "H27" not in J29 and "Untiered" not in J29, "the copied machinery names only 0.3.29"
_c28 = s.index('public static synchronized String migrate0328() {')
_c28 = s.index('}""")\n', _c28) + len('}""")\n')
assert "public static boolean h23Old(" in s and s.index("public static boolean h23Old(") < _c28
rep(s[s.index('# ---- 0.3.28 ONE-TIME UPDATE migrate0328'):_c28], s[s.index('# ---- 0.3.28 ONE-TIME UPDATE migrate0328'):_c28] + '''# ---- 0.3.29 ONE-TIME UPDATE migrate0329 (PROJECT-RULES section 4; tools/gear_0_3_29_patch.py): the migrate0327 machinery (copied; text compare h23Old,
# table rows logged as level.material[<entry>] / ut[<id>] with | columns) + a pure addition at the END (the rows a file lacks, before the marker)
''' + J29)
rep('''  @PKG@.GearCfg.migrate0328();          // 0.3.28: Fortune 3 a level everywhere + no armor Fortune cap (only the untouched 0.3.27 defaults)''',
    '''  @PKG@.GearCfg.migrate0328();          // 0.3.28: Fortune 3 a level everywhere + no armor Fortune cap (only the untouched 0.3.27 defaults)
  @PKG@.GearCfg.migrate0329();          // 0.3.29: 20 levels per zone + 15 gathering armor tiers + bags to 100 (only the untouched 0.3.28 defaults) + Bronze rows''')

# ================================================================================================================ manifest
rep('''Replaces SkyyRolls. FORTUNE: every lifelong tool's Fortune line''',
    '''Replaces SkyyRolls. LEVEL BANDS: 20 levels per zone on every tool, weapon and armor (Copper 1-8, Iron 8-15, Bronze 15-23, Thorium 20-28 ... Lumen 95-103); the Bronze Mining set (crafted at the Armor Bench with Bronze Ingots); 15 Foraging and 15 Farming armor tiers; Vein Mine / Tree Feller open at tool Lv 4, 8, 16, 24, 32, 40. FORTUNE: every lifelong tool's Fortune line''')


# ================================================================================================================ build fixes: the older rounds' proofs on TT_VERSION 3
rep('''assert TT.TT_VERSION == "2" and len(TT.LADDER) == 16 and TT.LADDER[2] == "Bronze" and TT.LADDER[-1] == "Onyxium", "tools/tier_tags.py: the 15-step ladder"''',
    '''assert TT.TT_VERSION in ("2", "3") and len(TT.LADDER) == 16 and TT.LADDER[2] == "Bronze" and TT.LADDER[-1] == "Onyxium", "tools/tier_tags.py: the 15-step ladder"          # 0.3.29: TT 3 keeps the ladder''')

after('''G328_ROWK = ["unid.typeAtIdentify"]
''', '''AB_LV_DEF = "4,8,16,24,32,40"          # 0.3.29: lifelong.abilityLevels (Skyy "+8 after 16: 4,8,16,24,32,40")
''')

rep('''_XT = []
for _t, _s, _c in BANDS + FAM_BANDS:
    _st = _MSTART[_t[6:]] if _t.startswith("Armor_") and _t[6:] in _MSTART else _s''', '''_XT = []
for _t, _s, _c in BANDS_V28 + FAM_BANDS_V28:          # 0.3.29: the craft XP tier levels stay the 0.3.28 ones (the re-band moves who may use an item, not its XP)
    _st = _MSTART[_t[6:]] if _t.startswith("Armor_") and _t[6:] in _MSTART else _s''')


# ================================================================================================================ 5: the multitool = both tools, no drawback; after rebirth 1
# Skyy 2026-10-18: "and the multi tool isnt slower, and has the same fortune. its The exact same as both the tools combined. No drawbacks. The only
# actual drawback is that you can't unlock it till after you rebirth once." + (the tooltip) "keep the mining and foraging levels separate on the
# tool. so it would say Pickaxe [lvl 10] (pickaxe stats below) then hatchet [lvl 11] (hatchet stats below.) in the flavor text."
rep('''MULTI_SPD_DEF, MULTI_FORT_DEF = 85, 70''', '''MULTI_SPD_DEF, MULTI_FORT_DEF = 100, 100          # 0.3.29 (Skyy "No drawbacks"): 0.2.18 - 0.3.28: 85, 70 (migrate0329)''')
rep('''  MULTI_SPD = (int) plong(p, "multi.speedPct", 85L, 1L, 100L);
  MULTI_FORT = (int) plong(p, "multi.fortunePct", 70L, 0L, 100L);''', '''  MULTI_SPD = (int) plong(p, "multi.speedPct", 100L, 1L, 100L);          // 0.3.29: no drawback (0.2.18 - 0.3.28: 85)
  MULTI_FORT = (int) plong(p, "multi.fortunePct", 100L, 0L, 100L);          // 0.3.29 (0.2.18 - 0.3.28: 70)''')
rep('''    ("multi.rebirthGate", "Multitools after rebirth 1", "tools", "bool", "false", "", "", "", "", "live,danger",
     "On = multitools open after your first rebirth. Switch on with rebirth.on. Off = always.", "field:GearCfg.MULTI_RBGATE"),''',
    '''    ("multi.rebirthGate", "Multitools after rebirth 1", "tools", "bool", "true", "", "", "", "", "live,danger",
     "On = Make multitool needs rebirth 1 (refused without SkyyRebirth). Off = always. Made ones stay.", "field:GearCfg.MULTI_RBGATE"),''')
rep('''("MULTI_RBGATE", "boolean", "false")''', '''("MULTI_RBGATE", "boolean", "true")''')
rep('''  MULTI_RBGATE = pbool(p, "multi.rebirthGate", false);          // fix round 2 (critic B1): OFF until rebirth is switched on''',
    '''  MULTI_RBGATE = pbool(p, "multi.rebirthGate", true);          // 0.3.29 (Skyy "you can't unlock it till after you rebirth once"; 0.3.5 fix round 2 - 0.3.28: off)''')
rep('''H29_KEYS = [_r[0] for _r in H29_ROWS]
''', '''for _k, _o, _n in (("multi.speedPct", "85", str(MULTI_SPD_DEF)), ("multi.fortunePct", "70", str(MULTI_FORT_DEF)), ("multi.rebirthGate", "false", "true")):
    H29_ROWS.append((_k, _o, _n, _k, _o, _n))          # the multitool: no drawback, after rebirth 1
H29_KEYS = [_r[0] for _r in H29_ROWS]
''')
# the gate: with the gate on, no SkyyRebirth = refused; the count read from rebirth:n:<uuid> (SkyyRebirth 0.3.5); a made multitool stays usable
rep('''public static String rbGate(java.util.UUID u) {
  if (!@PKG@.GearCfg.MULTI_RBGATE || u == null || @PKG@.Gear.fn("rebirth:fn:count") == null) return null;
  Object n = @PKG@.Gear.bget("rebirth:n:" + u);
  if (!(n instanceof Integer)) return "Your rebirths are still loading - try again in a moment.";
  if (((Integer) n).intValue() >= 1) return null;
  return "Multitools come after your first rebirth.";
}""")''', '''public static String rbGate(java.util.UUID u) {
  if (!@PKG@.GearCfg.MULTI_RBGATE || u == null) return null;
  if (@PKG@.Gear.fn("rebirth:fn:count") == null) return "Multitools come after your first rebirth - this server has no SkyyRebirth.";          // 0.3.29: refused
  Object n = @PKG@.Gear.bget("rebirth:n:" + u);
  if (!(n instanceof Integer)) return "Your rebirths are still loading - try again in a moment.";
  if (((Integer) n).intValue() >= 1) return null;
  return "Multitools come after your first rebirth (Rebirth 1 : " + ((Integer) n).intValue() + ").";
}""")
# 0.3.29: the rebirths the gate sees (0 = none / still loading / no SkyyRebirth) - the red requirement row "Rebirth 1 : 0"
M(gll, r"""
public static int rbHave(java.util.UUID u) {
  if (u == null) return 0;
  Object n = @PKG@.Gear.bget("rebirth:n:" + u);
  return n instanceof Integer && ((Integer) n).intValue() > 0 ? ((Integer) n).intValue() : 0;
}""")''')
rep('''  if (gate != null) { tx = "Multitool: " + gate; bl = "Rebirth 1"; }
  else {
    int[] pr = mtPair(inv);''', '''  if (gate != null) { tx = "Rebirth 1 : " + @PKG@.GearLL.rbHave(u); bl = "Rebirth 1"; }          // 0.3.29: the red requirement row (Menu-Pattern rule 9)
  else {
    int[] pr = mtPair(inv);''')
rep('''Label #SkyyGPMt { Anchor: (Width: 392); Text: \\"\\"; Style: (FontSize: 14, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); }''',
    '''Label #SkyyGPMt { Anchor: (Width: 392); Text: \\"\\"; Style: (FontSize: 14, RenderBold: " + (gate != null) + ", TextColor: " + (gate != null ? @PKG@.GearReq.col(0) : "#ffffff(0.8)") + ", VerticalAlignment: Center, Wrap: true); }''')
rep('''  this.mlKey = null;
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { tx = "Multitool: " + gate; bl = "Rebirth 1"; }''', '''  this.mlKey = null;
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { tx = "Rebirth 1 : " + @PKG@.GearLL.rbHave(u); bl = "Rebirth 1"; }          // 0.3.29: the red requirement row (Menu-Pattern rule 9)''')
rep('''Label #SkyyGPMl { Anchor: (Width: 392); Text: \\"\\"; Style: (FontSize: 13, TextColor: #ffffff(0.8), VerticalAlignment: Center, Wrap: true); }''',
    '''Label #SkyyGPMl { Anchor: (Width: 392); Text: \\"\\"; Style: (FontSize: 13, RenderBold: " + (gate != null) + ", TextColor: " + (gate != null ? @PKG@.GearReq.col(0) : "#ffffff(0.8)") + ", VerticalAlignment: Center, Wrap: true); }''')
# the tooltip: two sections, each side at ITS skill level with its real numbers (GearTool.mstats = what the hits use), no trade-off line
rep('''public static void mlines(java.util.UUID owner, String id, @BD@ d, int t, java.util.ArrayList txt, java.util.ArrayList col) {
  int[] g = gate(owner, 6, id, d);
  int lv = g[0];
  double sp = (double) @PKG@.GearCfg.MULTI_SPD / 100.0;
  double fp = (double) @PKG@.GearCfg.MULTI_FORT / 100.0;
  double[] a = eff(1, lv, t, d);
  double[] b = eff(3, lv, t, d);
  String tw = id.substring(id.lastIndexOf('_') + 1);
  mpowLine(txt, col, "Mining Power", a[0] * sp, refPower("Tool_Pickaxe_" + tw), "stone", "pickaxe", "rock and ore");
  mpowLine(txt, col, "Chopping Power", b[0] * sp, refPower("Tool_Hatchet_" + tw), "log", "hatchet", "logs");
  double fm = r1(a[1] * fp);
  double fc = r1(b[1] * fp);
  txt.add("Mining Fortune +" + @PKG@.Gear.fnum(fm) + "% = " + fdrops(fm) + " (rock / ore)");          // 0.3.28
  col.add(null);
  txt.add("Foraging Fortune +" + @PKG@.Gear.fnum(fc) + "% = " + fdrops(fc) + " (log)");          // 0.3.28
  col.add(null);
  if (a[2] > 0.0) { txt.add("Mining Wisdom +" + @PKG@.Gear.fnum(a[2]) + "% (more Mining XP)"); col.add(null); }
  if (b[2] > 0.0) { txt.add("Foraging Wisdom +" + @PKG@.Gear.fnum(b[2]) + "% (more Foraging XP)"); col.add(null); }
  if (owner != null && g[2] == 0) {
    txt.add("No bonus until Mining + Foraging " + lv);
    col.add(@PKG@.GearDefs.C_BAD);
  }
  txt.add("Multitool: slightly slower and less Fortune than a single tool");
  col.add(@PKG@.GearDefs.C_GRAY);
  txt.add("Tree Feller unlocks in the Foraging tree");
  col.add(@PKG@.GearDefs.C_GRAY);
}""")''', '''public static void mlines(java.util.UUID owner, String id, @BD@ d, int t, java.util.ArrayList txt, java.util.ArrayList col) {
  int[] g = gate(owner, 6, id, d);
  double[] m = mstats(owner, id, d);          // 0.3.29: the numbers the hits really use (each side = its single tool; no multitool share)
  boolean ll = owner != null && @PKG@.GearLL.mine(owner, d);
  int lp = g[0];
  int lh = g[0];
  if (ll) {
    int a0 = @PKG@.GearLL.levelK(owner, 0, id);          // the pickaxe side levels with Mining
    int b0 = @PKG@.GearLL.levelK(owner, 1, id);          // the hatchet side with Foraging
    if (a0 >= 1) lp = a0;
    if (b0 >= 1) lh = b0;
  }
  String tw = id.substring(id.lastIndexOf('_') + 1);
  txt.add("Pickaxe [Lv " + lp + "]");
  col.add(@PKG@.GearDefs.C_LABEL);
  mpowLine(txt, col, "Mining Power", m[4], refPower("Tool_Pickaxe_" + tw), "stone", "pickaxe", "rock and ore");
  txt.add("Mining Fortune +" + @PKG@.Gear.fnum(m[5]) + "% = " + fdrops(m[5]) + " (rock / ore)");
  col.add(null);
  if (m[8] > 0.0) { txt.add("Mining Wisdom +" + @PKG@.Gear.fnum(m[8]) + "% (more Mining XP)"); col.add(null); }
  if (ll) mupl(owner, d, 0, txt, col);
  txt.add("Hatchet [Lv " + lh + "]");
  col.add(@PKG@.GearDefs.C_LABEL);
  mpowLine(txt, col, "Chopping Power", m[9], refPower("Tool_Hatchet_" + tw), "log", "hatchet", "logs");
  txt.add("Foraging Fortune +" + @PKG@.Gear.fnum(m[10]) + "% = " + fdrops(m[10]) + " (log)");
  col.add(null);
  if (m[11] > 0.0) { txt.add("Foraging Wisdom +" + @PKG@.Gear.fnum(m[11]) + "% (more Foraging XP)"); col.add(null); }
  if (ll) mupl(owner, d, 1, txt, col);
  if (owner != null && g[2] == 0) {
    txt.add("No bonus until Mining + Foraging " + g[0]);
    col.add(@PKG@.GearDefs.C_BAD);
  }
  txt.add("Multitool: a pickaxe and a hatchet in one");
  col.add(@PKG@.GearDefs.C_GRAY);
}""")''')
before('''# 0.2.18: the multitool's lines (both stat sets, the trade-off line); the tier word = the id's last word''', '''# 0.3.29: one side's upgrade levels (pickaxe set k 0: Breaking Power, Fortune, Vein Mine ...; hatchet set k 1: ... Tree Feller) at the level they work at
M(gtool, r"""
public static void mupl(java.util.UUID ow, @BD@ d, int k, java.util.ArrayList txt, java.util.ArrayList col) {
  try {
    java.util.Properties P = @PKG@.GearLL.reg(@PKG@.Gear.pkey(ow));
    StringBuilder sb = new StringBuilder();
    for (int p = 0; p < @PKG@.GearLL.PK.length; p++) {
      int lv = @PKG@.GearLL.perkEff(ow, P, k, p);
      if (lv <= 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(@PKG@.GearLL.PKN[p]).append(' ').append(lv);
    }
    if (sb.length() > 0) { txt.add("Upgrades: " + sb.toString()); col.add(null); }
  } catch (Throwable t) { }
}""")
''')
# the name: a multitool has two levels (the tooltip's two headers), so its name carries none ("Crude Multitool")
rep('''public static String lvTag(String id, @BD@ d) {
  if (!@PKG@.GearCfg.NAME_LV || id == null || d == null) return "";''', '''public static String lvTag(String id, @BD@ d) {
  if (!@PKG@.GearCfg.NAME_LV || id == null || d == null) return "";
  if (@PKG@.GearData.multiId(id)) return "";          // 0.3.29: Pickaxe [Lv N] / Hatchet [Lv M] in the tooltip instead''')
# the tooltip refreshes on a Foraging level-up too: the sweep keeps the hatchet side's level in the document (lvH) like lvl for the pickaxe side
rep('''    int lv = levelFor(u, s.getItemId());
    if (lv >= 1 && @PKG@.GearData.num(d, "lvl", -1) != lv) RESYNC.put(u, Boolean.TRUE);''', '''    int lv = levelFor(u, s.getItemId());
    if (lv >= 1 && @PKG@.GearData.num(d, "lvl", -1) != lv) RESYNC.put(u, Boolean.TRUE);
    if (@PKG@.GearData.multiId(s.getItemId())) {          // 0.3.29: the hatchet side's level (Foraging) - its tooltip header
      int lh = levelK(u, 1, s.getItemId());
      if (lh >= 1 && @PKG@.GearData.num(d, "lvH", -1) != lh) RESYNC.put(u, Boolean.TRUE);
    }''')
rep('''  int lv = @PKG@.GearLL.levelFor(u, id);
  boolean lw = lv >= 1 && @PKG@.GearData.num(d, "lvl", -1) != lv;
  boolean rw = @PKG@.GearLL.isRp(d) && "0".equals(P.getProperty(K + ".rp"));          // fix round: a replacement that became THE tool
  boolean tw = @PKG@.GearLL.isRt(d);          // fix round 2: swapped back with /lifelong (or a crash between the swap and this look)
  if (lw || rw || tw) {
    @BD@ nd = d.clone();
    if (lw) nd.put("lvl", new org.bson.BsonInt32(lv));''', '''  int lv = @PKG@.GearLL.levelFor(u, id);
  boolean lw = lv >= 1 && @PKG@.GearData.num(d, "lvl", -1) != lv;
  int lh = @PKG@.GearData.multiId(id) ? @PKG@.GearLL.levelK(u, 1, id) : -1;          // 0.3.29: a multitool's hatchet side (Foraging) - its tooltip header
  boolean hw = lh >= 1 && @PKG@.GearData.num(d, "lvH", -1) != lh;
  boolean rw = @PKG@.GearLL.isRp(d) && "0".equals(P.getProperty(K + ".rp"));          // fix round: a replacement that became THE tool
  boolean tw = @PKG@.GearLL.isRt(d);          // fix round 2: swapped back with /lifelong (or a crash between the swap and this look)
  if (lw || hw || rw || tw) {
    @BD@ nd = d.clone();
    if (lw) nd.put("lvl", new org.bson.BsonInt32(lv));
    if (hw) nd.put("lvH", new org.bson.BsonInt32(lh));''')
rep('''Tools (your lifelong pickaxe, hatchet, hoe and sickle: their Upgrade Points, Tier up and - after rebirth 1 - Make multitool; /toolpoints, /multitool) tabs (every click answered), a bit slower and with less Fortune (Mining + Foraging gate);''',
    '''Tools (your lifelong pickaxe, hatchet, hoe and sickle: their Upgrade Points, Tier up and - after rebirth 1 - Make multitool; /toolpoints, /multitool) tabs (every click answered), exactly both tools in one (Mining + Foraging gate);''')


# ================================================================================================================ 6: no Enchanted cost below Dusk
# Skyy 2026-10-18 (Smithing > Mining armor, Iron set): "and lets reduce the upgrade cost of the lower tiers a bit. so it doesnt cost enchanted till
# dusk." -> every tier-up INTO a tier below Dusk (T1-T5: Copper, Iron, Bronze, Thorium, Lead) pays PLAIN materials: each Enchanted item = PLAIN29 of
# its base (tools/skyyench.py RATIO 100 base = 1 Enchanted, x 3/4 = "a bit" less: 75); the Enchanted Sticks of those steps become plain sticks the
# same way (lifelong.stickCost stays; GearUp.stickFor skips the steps that carry them in the ladder text). Gathering armor (Mining, Foraging,
# Farming, Fishing sets) and every lifelong tool / multitool / Harvester / can ladder. Dusk (T6) and up keep their Enchanted costs.
rep('''assert set(HARV_IDS) <= set(G23_HARV_LAD) and set(G23_HARV) <= set(G23_HARV_LAD) and len(G23_CAN_LAD) == len(G23_HARV_LAD) == 16
for _l in (CAN_LAD_DEF, HARV_LAD_DEF):
    assert len(_l) < 2000 and all(32 <= ord(_c) < 127 for _c in _l)
''', '''assert set(HARV_IDS) <= set(G23_HARV_LAD) and set(G23_HARV) <= set(G23_HARV_LAD) and len(G23_CAN_LAD) == len(G23_HARV_LAD) == 16
for _l in (CAN_LAD_DEF, HARV_LAD_DEF):
    assert len(_l) < 2000 and all(32 <= ord(_c) < 127 for _c in _l)
# ---- 0.3.29 (tools/gear_0_3_29_patch.py item 6; Skyy "so it doesnt cost enchanted till dusk"): plain materials below Dusk
PLAIN29 = 75          # plain items per Enchanted item (tools/skyyench.py RATIO 100 x 3/4 - Skyy "reduce the upgrade cost of the lower tiers a bit")
DUSK29 = TT.metal_tier("Dusk")
assert ENCH.RATIO == 100 and DUSK29 == 6
_EB29 = dict((ENCH.PREFIX + _t[0], _t[2]) for _t in list(ENCH.TABLE) + list(ENCH.TABLE_C1) if _t[1] == "I")
_STK29 = [0, 0, 0, 2, 4, 8, 16, 32]          # lifelong.stickCost's default (Crude .. Onyxium, Gear's internal tier)
_TINT29 = dict(TOOL_TIERS_ALL)


def _lt29t(i):
    """the ladder T of a tier-up's target (tools/tier_tags.py row, else the first metal word of the id)"""
    if TT.tier(i):
        return TT.tier(i)
    for _w in i.split("_")[1:]:
        if TT.metal_tier(_w):
            return TT.metal_tier(_w)
    return None


def plain29(text, tools):
    """a ladder text with every step INTO a tier below Dusk paid in plain materials; tools = lifelong tool ladders (+ their sticks)"""
    out, stk = [], []
    for _row in text.split(","):
        _ps = _row.split(">")
        _np = [_ps[0]]
        for _st in _ps[1:]:
            _m = re.match(r"^([^()]+)\\((.*)\\)$", _st)
            _t = _lt29t(_m.group(1)) if _m else None
            if _m is None or _t is None or _t >= DUSK29:
                _np.append(_st)
                continue
            _it = []
            for _c in _m.group(2).split("+"):
                _i, _n = _c.rsplit("*", 1)
                if _i.startswith(ENCH.PREFIX):
                    _i, _n = _EB29[_i], str(int(_n) * PLAIN29)
                _it.append("%s*%s" % (_i, _n))
            if tools:
                _k = next((_TINT29[_w] for _w in _m.group(1).split("_")[1:] if _w in _TINT29), None)
                if _k is not None and _STK29[_k] > 0:
                    _it.append("Ingredient_Stick*%d" % (_STK29[_k] * PLAIN29))
                    stk.append(_m.group(1))
            _np.append("%s(%s)" % (_m.group(1), "+".join(_it)))
        out.append(">".join(_np))
    _o = ",".join(out)
    for _x in re.findall(r"\\(([^()]*)\\)", _o):
        assert all(32 <= ord(_c) < 127 for _c in _x)
    return _o, stk


LL_LADDER_V28, CAN_LAD_V28, HARV_LAD_V28, MT_LAD_V28, GA_LADDER_V28 = LL_LADDER_DEF, CAN_LAD_DEF, HARV_LAD_DEF, MT_LAD_DEF, GA_LADDER_DEF
GA2_LAD_V29E = list(GA2_LAD_DEF)          # the 15-tier ladders before the plain rule (proof only)
STK_PLAIN29 = []
LL_LADDER_DEF, _s1 = plain29(LL_LADDER_DEF, True)
CAN_LAD_DEF, _s2 = plain29(CAN_LAD_DEF, True)
HARV_LAD_DEF, _s3 = plain29(HARV_LAD_DEF, True)
MT_LAD_DEF, _s4 = plain29(MT_LAD_DEF, True)
STK_PLAIN29 = sorted(set(_s1 + _s2 + _s3 + _s4))
GA_LADDER_DEF = plain29(GA_LADDER_DEF, False)[0]
GA2_LAD_DEF = [plain29(_l, False)[0] for _l in GA2_LAD_DEF]
for _l in [LL_LADDER_DEF, CAN_LAD_DEF, HARV_LAD_DEF, MT_LAD_DEF, GA_LADDER_DEF] + GA2_LAD_DEF:
    for _st in re.findall(r">([A-Za-z0-9_]+)\\(([^()]*)\\)", _l):
        _t = _lt29t(_st[0])
        assert not (ENCH.PREFIX in _st[1] and _t is not None and _t < DUSK29), "0.3.29: an Enchanted cost below Dusk: %s" % (_st,)
assert "Armor_Iron_Head(Ingredient_Bar_Iron*75)" in GA_LADDER_DEF and "Armor_Cobalt_Head(Skyy_Ench_Cobalt*1)" in GA_LADDER_DEF
assert "Tool_Pickaxe_Iron(Ingredient_Bar_Iron*75)" in LL_LADDER_DEF and "Tool_Pickaxe_Dusk_SkyWynn(Ingredient_Bar_Dusk_SkyWynn*64)" in LL_LADDER_DEF
assert "Tool_Pickaxe_Thorium(Ingredient_Bar_Thorium*75+Ingredient_Stick*150)" in LL_LADDER_DEF and "Tool_Pickaxe_Cobalt(Skyy_Ench_Cobalt*2)" in LL_LADDER_DEF
assert len(LL_LADDER_DEF) < 4000 and len(MT_LAD_DEF) < 2000 and len(GA_LADDER_DEF) < 2000 and len(GA2_LAD_DEF[2]) < 2000 and len(CAN_LAD_DEF) < 2000 and len(HARV_LAD_DEF) < 2000 and all(len(_l) < 4000 for _l in GA2_LAD_DEF)
print("0.3.29 plain below Dusk (x%d per Enchanted): %d tool steps carry their sticks as plain sticks; Mining armor %s" % (
    PLAIN29, len(STK_PLAIN29), ", ".join(re.findall(r">(Armor_[A-Za-z]+_Head\\([^()]*\\))", GA_LADDER_DEF))))
''')
# migrate0323 keeps rewriting to ITS values (0.3.23 - 0.3.28 ladders); migrate0329 moves them on
rep('''H23_NEW = [LL_LADDER_DEF, CAN_LAD_DEF, HARV_LAD_DEF, ORE_FLOOR_DEF, UP_LADDER_DEF]''',
    '''H23_NEW = [LL_LADDER_V28, CAN_LAD_V28, HARV_LAD_V28, ORE_FLOOR_DEF, UP_LADDER_DEF]          # 0.3.29: migrate0323 keeps its own new values''')
rep('''for _k, _o, _n in (("multi.speedPct", "85", str(MULTI_SPD_DEF)), ("multi.fortunePct", "70", str(MULTI_FORT_DEF)), ("multi.rebirthGate", "false", "true")):''',
    '''for _k, _o, _n in (("lifelong.ladders", LL_LADDER_V28, LL_LADDER_DEF), ("can.ladders", CAN_LAD_V28, CAN_LAD_DEF), ("harvester.ladders", HARV_LAD_V28, HARV_LAD_DEF),
                   ("multi.ladders", MT_LAD_V28, MT_LAD_DEF), ("garmor.ladders", GA_LADDER_V28, GA_LADDER_DEF), ("garmor.ladders.fishing", GA2_LAD_V28[2], GA2_LAD_DEF[2])):
    H29_ROWS.append((_k, _o, _n, _k, _o, _n))          # plain materials below Dusk (item 6)
for _k, _o, _n in (("multi.speedPct", "85", str(MULTI_SPD_DEF)), ("multi.fortunePct", "70", str(MULTI_FORT_DEF)), ("multi.rebirthGate", "false", "true")):''')
# the sticks of a step that pays them in its text are not asked again
rep('''  int t = @PKG@.GearLL.tier(to);
  int[] a = sticks();
  if (t < 0 || t >= a.length) return 0;
  return a[t];
}""")''', '''  for (int i = 0; i < STK_PLAIN.length; i++) if (STK_PLAIN[i].equals(to)) return 0;          // 0.3.29: below Dusk the sticks are plain, in the ladder text
  int t = @PKG@.GearLL.tier(to);
  int[] a = sticks();
  if (t < 0 || t >= a.length) return 0;
  return a[t];
}""")''')
rep('''M(gup, r"""
public static int stickFor(String from, String to) {''', '''F(gup, "public static final String[] STK_PLAIN = %s;" % jarr(STK_PLAIN29))          # 0.3.29: the steps whose sticks are plain (below Dusk)
M(gup, r"""
public static int stickFor(String from, String to) {''')

rep('''assert [_dp.get(_k) for _k in H23_KEYS] == H23_NEW and DEFAULT_TEXT.count(H23_MARK_ID) == 1''',
    '''assert [_dp.get(_k) for _k in H23_KEYS[3:]] == H23_NEW[3:] and [_dp.get(_k) for _k in H23_KEYS[:3]] == [LL_LADDER_DEF, CAN_LAD_DEF, HARV_LAD_DEF] and DEFAULT_TEXT.count(H23_MARK_ID) == 1          # 0.3.29: the ladders moved on (plain below Dusk)''')


# ================================================================================================================ 7: THE GATHERING ARMOR BUFF
# Skyy 2026-10-18 (docs/answered/gear.md GATHERING ARMOR BUFF; screenshot Oak Bark Cuirass Lv 15 "Foraging Fortune +0.35"): "and buff all the gathering
# armor to give more fortune, and to also give damage and speed. armor should be a big part of the progression" + popup "Breaking power + speed (Rec.)".
# Every Mining / Foraging / Farming piece: much more Fortune for its skill + that skill's Breaking Power + Breaking Speed, by its ladder T (one of the
# four power sources: tool + gear + accessories + pets). A FULL SET at T ~ that tier's tool Fortune line (Copper 60 ... Lumen 240; no more than 100 %
# from armor before T4): 70 % on the pieces (Head 25 / Chest 35 / Hands 15 / Legs 25 %), 30 % the full-set bonus. Power + speed well below the
# tool's lines (garmor.powerPct / garmor.swingPct, full set by T). Fishing: double catch (its Fortune) + Fishing Speed (no breaking).
rep('''ZM_FULL = [round(sum(_slot_order(_r[4])) + _mine_words(_r[7])["mfort"], 2) for _r in ZM_ROWS]
assert ZM_FULL == [4.5, 5.2, 6.7, 7.5, 9.3, 10.3, 12.5, 13.7], ZM_FULL
''', '''ZM_FULL = [round(sum(_slot_order(_r[4])) + _mine_words(_r[7])["mfort"], 2) for _r in ZM_ROWS]
assert ZM_FULL == [4.5, 5.2, 6.7, 7.5, 9.3, 10.3, 12.5, 13.7], ZM_FULL
# ---- 0.3.29 (tools/gear_0_3_29_patch.py item 7; Skyy "buff all the gathering armor to give more fortune, and to also give damage and speed")
GB_FT = [60, 75, 90, 105, 120, 135, 150, 160, 170, 180, 190, 200, 210, 225, 240, 255]          # full-set Fortune by ladder T (T16 = Onyxium)
GB_PW = [25 + 10 * _k for _k in range(16)]          # full-set Breaking Power % by T (25 .. 175)
GB_SW = [5 + 2 * _k for _k in range(16)]            # full-set Breaking Speed % by T (5 .. 35)
GB_PIECE, GB_SET = 0.7, 0.3          # the Fortune split: pieces / full-set bonus
assert all(GB_FT[_t - 1] <= 100 for _t in (1, 2, 3)) and GB_FT[3] > 100, "Skyy: no more than 100 % Fortune from armor before T4"
assert all(_b > _a for _a, _b in zip(GB_FT, GB_FT[1:])) and GB_PW[0] == 25 and GB_SW[-1] == 35
GB_POW_DEF = ",".join("%g" % _x for _x in GB_PW)
GB_SWG_DEF = ",".join("%g" % _x for _x in GB_SW)
_GBSH = (0.25, 0.35, 0.25, 0.15)          # ROW order Head Chest Legs Hands (the garmor.mining columns)


def _gbr(v):
    return float("%g" % round(v, 2))


def _gb_row(t):
    return " ".join("%g" % _gbr(GB_FT[t - 1] * GB_PIECE * _s) for _s in _GBSH)


def _gb_words(words, t):
    _o = [_w for _w in words.split() if not _w.startswith("mfort+")]
    return " ".join(["mfort+%g" % _gbr(GB_FT[t - 1] * GB_SET)] + _o)


MINE_ROWS_V28, ZM_ROWS_V28, BZ_ROW_V28 = list(MINE_ROWS), list(ZM_ROWS), BZ_ROW
MINE_ROWS = [(_r[0], _gb_row(TT.metal_tier(_r[0].capitalize())), _r[2], _r[3], _gb_words(_r[4], TT.metal_tier(_r[0].capitalize()))) for _r in MINE_ROWS_V28]
ZM_ROWS = [tuple(_r[:4]) + (_gb_row(TT.metal_tier(_r[1])),) + tuple(_r[5:7]) + (_gb_words(_r[7], TT.metal_tier(_r[1])), _r[8]) for _r in ZM_ROWS_V28]
BZ_ROW = (BZ_ROW_V28[0], _gb_row(3), BZ_ROW_V28[2], BZ_ROW_V28[3], _gb_words(BZ_ROW_V28[4], 3))
MINE_F = [_x for _r in MINE_ROWS for _x in _slot_order(_r[1])]
ZM_F = [_x for _r in ZM_ROWS for _x in _slot_order(_r[4])]
BZ_F = _slot_order(BZ_ROW[1])
_gbfull = dict([(_r[0].capitalize(), round(sum(_slot_order(_r[1])) + _mine_words(_r[4])["mfort"], 1)) for _r in MINE_ROWS] +
               [(_r[1], round(sum(_slot_order(_r[4])) + _mine_words(_r[7])["mfort"], 1)) for _r in ZM_ROWS] + [("Bronze", round(sum(BZ_F) + _mine_words(BZ_ROW[4])["mfort"], 1))])
assert all(_gbfull[_m] == GB_FT[TT.metal_tier(_m) - 1] for _m in _gbfull), _gbfull
assert all(max(_slot_order(_r[1])) <= 100 for _r in MINE_ROWS) and all(max(_slot_order(_r[4])) <= 100 for _r in ZM_ROWS)
print("0.3.29 gathering armor buff: full-set Fortune by T %s; Breaking Power %% %s; Breaking Speed %% %s" % (GB_FT, GB_POW_DEF, GB_SWG_DEF))
# Foraging / Farming: col 0 (pieces' set total) = 70 %, col 2 (full-set bonus) = 30 %, Wisdom kept; Fishing: double catch 60 % of T, Speed x2
GA2_STAT_V29E = list(GA2_STAT_DEF)
for _f in range(2):
    _c = GA2_STAT_DEF[_f].split("|")
    GA2_STAT_DEF[_f] = "|".join([",".join("%g" % _gbr(GB_FT[_t - 1] * GB_PIECE) for _t in GA2_LT[_f]), _c[1],
                                 ",".join("%g" % _gbr(GB_FT[_t - 1] * GB_SET) for _t in GA2_LT[_f])])
_c = GA2_STAT_DEF[2].split("|")
GA2_STAT_DEF[2] = "|".join([",".join("%g" % (2 * float(_x)) for _x in _c[0].split(",")), _c[1], _c[2],
                            ",".join("%g" % _gbr(GB_FT[_t - 1] * 0.6) for _t in GA2_LT[2])])
assert all(len(_x) < 300 for _x in GA2_STAT_DEF) and all(len(_x.split("|")) == (4 if _k == 2 else 3) for _k, _x in enumerate(GA2_STAT_DEF))
assert sum(float(_x) for _x in GA2_STAT_DEF[0].split("|")[0].split(",")[:1]) == 42.0          # T1 Oak: 42 on the pieces + 18 full set = 60
''')
# the per-tier power / speed rows (Server Setup, absent = the default), the mining tiers' ladder T, the cap: armor Fortune no cap (the numbers keep the rule)
rep('''G329_ROWK = ["lifelong.abilityLevels"]''', '''G329_ROWK = ["lifelong.abilityLevels", "garmor.powerPct", "garmor.swingPct"]''')
rep('''    ("garmor.fishing", "Fishing armor numbers", "garmor", "text", GA2_STAT_DEF[2], "0", "300", "", "", "live,danger",''',
    '''    # 0.3.29 (Skyy "buff all the gathering armor ... also give damage and speed"): full-set Breaking Power / Breaking Speed by ladder T
    ("garmor.powerPct", "Gathering armor Breaking Power", "garmor", "text", GB_POW_DEF, "0", "300", "", "%", "live,danger",
     "Full set T1-T16: Mining / Chopping / Farming Power % (pieces 25/35/15/25 %), with that skill's tool.", "field:GearCfg.GA_POW;check=GearGArm.checkT16"),
    ("garmor.swingPct", "Gathering armor Breaking Speed", "garmor", "text", GB_SWG_DEF, "0", "300", "", "%", "live,danger",
     "Full set T1-T16: Breaking Speed % (pieces 25/35/15/25 %), with that skill's tool.", "field:GearCfg.GA_SWG;check=GearGArm.checkT16"),
    ("garmor.fishing", "Fishing armor numbers", "garmor", "text", GA2_STAT_DEF[2], "0", "300", "", "", "live,danger",''')
rep('''     "Full set per tier 1-5: Fortune | Wisdom % | full-set bonus Fortune.", "field:GearCfg.GA_STAT0;check=GearGArm.checkStats"),''',
    '''     "Set per tier T1-T15: pieces' Fortune | Wisdom % | full-set bonus Fortune.", "field:GearCfg.GA_STAT0;check=GearGArm.checkStats"),''')
rep('''     "Full set per tier 1-7: Fortune | Wisdom % | full-set bonus Fortune.", "field:GearCfg.GA_STAT1;check=GearGArm.checkStats"),''',
    '''     "Set per tier T1-T15: pieces' Fortune | Wisdom % | full-set bonus Fortune.", "field:GearCfg.GA_STAT1;check=GearGArm.checkStats"),''')
rep('''           "lifelong.abilityLevels"}          # 0.3.29: when Vein Mine / Tree Feller open (gathering speed = economy)''',
    '''           "lifelong.abilityLevels",          # 0.3.29: when Vein Mine / Tree Feller open (gathering speed = economy)
           "garmor.powerPct", "garmor.swingPct"}          # 0.3.29: the gathering armor buff (gathering speed = economy)''')
rep('''("GA_STAT2", "String", jstr(GA2_STAT_DEF[2])),''', '''("GA_STAT2", "String", jstr(GA2_STAT_DEF[2])), ("GA_POW", "String", jstr(GB_POW_DEF)), ("GA_SWG", "String", jstr(GB_SWG_DEF)),''')
rep('''  GA_STAT2 = ptext(p, "garmor.fishing", "@GA2STAT2@").trim();''', '''  GA_STAT2 = ptext(p, "garmor.fishing", "@GA2STAT2@").trim();
  GA_POW = ptext(p, "garmor.powerPct", "%s").trim();          // 0.3.29 (bad = one WARN + the default, GearGArm.t16)
  GA_SWG = ptext(p, "garmor.swingPct", "%s").trim();''' % ("@GBPOW@", "@GBSWG@"))
rep('''   .replace("@ZMBANDS@", ZM_BANDS_DEF)          # 0.3.21''', '''   .replace("@ZMBANDS@", ZM_BANDS_DEF)          # 0.3.21
   .replace("@GBPOW@", GB_POW_DEF).replace("@GBSWG@", GB_SWG_DEF)          # 0.3.29''')
rep('''    ("armor.fortune.cap", "Most Fortune from armor", "garmor", "dec", "100", "0", "100000", "", "", "live,danger",
     "Most Fortune worn armor gives (pieces + full set); 0 = no cap (Onyxium full set = 15).", "field:GearCfg.GM_FCAP"),''',
    '''    ("armor.fortune.cap", "Most Fortune from armor", "garmor", "dec", "0", "0", "100000", "", "", "live,danger",
     "Most Fortune worn armor gives (pieces + full set); 0 = no cap (a full set: 60 at T1 .. 255).", "field:GearCfg.GM_FCAP"),''')
rep('''("GM_FCAP", "double", "100.0")''', '''("GM_FCAP", "double", "0.0")''')
rep('''  GM_FCAP = pdec(p, "armor.fortune.cap", 100.0, 0.0, 100000.0);          // 0.3.28: 100 (0.3.27: 15); 0 = no cap (fcapA)''',
    '''  GM_FCAP = pdec(p, "armor.fortune.cap", 0.0, 0.0, 100000.0);          // 0.3.29: 0 = no cap (0.3.28: 100, 0.3.27: 15) - the buffed sets keep Skyy's rule by their numbers''')
rep('''assert [_dp.get(_k) for _k in H28_KEYS] == H28_NEW and DEFAULT_TEXT.count(H28_MARK_ID) == 1, "0.3.28: the fresh file's Fortune rows + marker"''',
    '''assert [_dp.get(_k) for _k in H28_KEYS[:2]] == H28_NEW[:2] and _dp.get("armor.fortune.cap") == "0" and DEFAULT_TEXT.count(H28_MARK_ID) == 1, "0.3.28: the fresh file's Fortune rows + marker (0.3.29: armor cap 0 = none)"''')
rep('''F(gmine, "public static final int ZN = %d;" % ZM_N)''', '''F(gmine, "public static final int ZN = %d;" % ZM_N)
F(gmine, "public static final int[] LT = %s;" % jints([TT.metal_tier(_t) for _t in MINE_ALL_TIERS]))          # 0.3.29: each tier's ladder T (the armor buff rows)''')
# GearGArm: the T1-T16 lists (parsed lazily), a piece's share, the swing for the held tool family
rep('''# one piece's lines = its tier's set totals x its slot share: Foraging / Farming { Fortune, Wisdom % }, Fishing { Speed, Treasure, Wisdom % }''',
    '''# 0.3.29 the armor buff: garmor.powerPct / garmor.swingPct = 16 numbers 0-1000 (full set by ladder T1-T16); a piece = its slot share of its T
F(gga, "public static final Object[] TPC = new Object[2];")
M(gga, r"""
public static double[] t16(int w) {
  String s = w == 0 ? @PKG@.GearCfg.GA_POW : @PKG@.GearCfg.GA_SWG;
  Object e = TPC[w];
  if (e instanceof Object[] && s != null && s.equals(((Object[]) e)[0])) return (double[]) ((Object[]) e)[1];
  double[] l = list(s, 16);
  if (l == null) {
    N[4] = N[4] + 1L;
    @PKG@.Gear.warnOnce("garmort16:" + w + ":" + s, "config.properties: garmor." + (w == 0 ? "powerPct" : "swingPct") + "=" + s + " is not 16 numbers - the default is used");
    l = list(w == 0 ? "%s" : "%s", 16);
  }
  TPC[w] = new Object[] { s, l };
  return l;
}""" % (GB_POW_DEF, GB_SWG_DEF))
M(gga, "public static String checkT16(String key, String value) { return list(value, 16) == null ? \\"Write 16 numbers 0-1000 joined by commas (the full set at T1 .. T16).\\" : null; }")
M(gga, r"""
public static double tval(int w, int t, int slot) {
  if (t < 1 || slot < 0 || slot > 3) return 0.0;
  double[] l = t16(w);
  return l[(t > 16 ? 16 : t) - 1] * SHARE[slot];
}""")
# the worn armor's Breaking Speed % for a held tool family (1 pickaxe, 2 shovel = Mining; 3 hatchet = Foraging; 4 hoe, 5 sickle = Farming; 6 the multitool = the higher)
M(gga, r"""
public static double swingFor(java.util.UUID u, int fam) {
  if (u == null) return 0.0;
  Object o = ARM.get(u);
  if (!(o instanceof double[]) || ((double[]) o).length < 14) return 0.0;
  double[] a = (double[]) o;
  if (fam == 1 || fam == 2) return a[11];
  if (fam == 3) return a[12];
  if (fam == 4 || fam == 5) return a[13];
  if (fam == 6) return a[11] > a[12] ? a[11] : a[12];
  return 0.0;
}""")
# one piece's lines = its tier's set totals x its slot share: Foraging / Farming { Fortune, Wisdom % }, Fishing { Speed, Treasure, Wisdom % }''')
# compute0: + the Breaking Power / Speed of every worn Mining / Foraging / Farming piece (o[8..10] power mining / foraging / farming, o[11..13] speed)
rep('''  double[] o = new double[8];
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
    else if (f == 1) { o[2] = o[2] + p[0]; o[3] = o[3] + p[1]; }''', '''  double[] o = new double[14];          // 0.3.29: + [8..10] Breaking Power % (Mining, Foraging, Farming), [11..13] Breaking Speed %
  if (armor == null || !anyOn()) return o;
  for (int k = 0; k < armor.getCapacity(); k++) {
    @IS@ s = armor.getItemStack((short) k);
    if (s == null || s.isEmpty()) continue;
    String id = s.getItemId();
    int mi = @PKG@.GearMine.index(id);
    if (mi >= 0) {          // 0.3.29: a Mining piece's power + speed (its Fortune / Wisdom stay GearMine's)
      if (!@PKG@.GearCfg.GM_ON) continue;
      @BD@ dm = @PKG@.GearData.effective(id, s.getMetadata());
      if (!@PKG@.GearStats.active(u, id, dm)) continue;
      int tm = @PKG@.GearMine.LT[mi / 4];
      o[8] = o[8] + tval(0, tm, mi % 4);
      o[11] = o[11] + tval(1, tm, mi % 4);
      continue;
    }
    int i = index(id);
    if (i < 0 || !famOn(IFAM[i])) continue;
    @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
    if (!@PKG@.GearStats.active(u, id, d)) continue;
    double[] p = piece(i);
    int f = IFAM[i];
    if (f == 0) { o[0] = o[0] + p[0]; o[1] = o[1] + p[1]; o[9] = o[9] + tval(0, ILT[i], ISLOT[i]); o[12] = o[12] + tval(1, ILT[i], ISLOT[i]); }
    else if (f == 1) { o[2] = o[2] + p[0]; o[3] = o[3] + p[1]; o[10] = o[10] + tval(0, ILT[i], ISLOT[i]); o[13] = o[13] + tval(1, ILT[i], ISLOT[i]); }''')
rep('''  o[4] = @PKG@.GearMine.r2(o[4]);
  o[5] = @PKG@.GearMine.r2(o[5]);
  return o;''', '''  o[4] = @PKG@.GearMine.r2(o[4]);
  o[5] = @PKG@.GearMine.r2(o[5]);
  for (int q = 8; q < 14; q++) o[q] = @PKG@.GearMine.r2(o[q]);          // 0.3.29
  return o;''')
rep('''      if (o[3] > 0.0) m.put("xp.farming", Double.valueOf(o[3] / 100.0));''', '''      if (o[3] > 0.0) m.put("xp.farming", Double.valueOf(o[3] / 100.0));
      if (o.length > 13) {          // 0.3.29: Breaking Power (GearTool.accBp reads bp.<skill> of every source but "gear")
        if (o[8] > 0.0) m.put("bp.mining", Double.valueOf(o[8] / 100.0));
        if (o[9] > 0.0) m.put("bp.foraging", Double.valueOf(o[9] / 100.0));
        if (o[10] > 0.0) m.put("bp.farming", Double.valueOf(o[10] / 100.0));
      }''')
# the swing: the held tool's own Breaking Speed + the worn armor's for that tool's skill
rep('''    double v = swingOf(u, s);
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "gear:swing:" + u.toString();''', '''    double v = swingOf(u, s) + (s == null || s.isEmpty() ? 0.0 : @PKG@.GearGArm.swingFor(u, @PKG@.GearData.toolFam(s.getItemId())));          // 0.3.29: + the armor
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "gear:swing:" + u.toString();''')
# the tooltips: power + speed lines on every Foraging / Farming / Mining piece
rep('''  if (v[0] > 0.0) { txt.add(FSK[f] + " Fortune +" + num(v[0])); col.add(null); }
  if (v[1] > 0.0) { txt.add(FSK[f] + " Wisdom +" + num(v[1]) + "%"); col.add(null); }''', '''  if (v[0] > 0.0) { txt.add(FSK[f] + " Fortune +" + num(v[0])); col.add(null); }
  if (v[1] > 0.0) { txt.add(FSK[f] + " Wisdom +" + num(v[1]) + "%"); col.add(null); }
  double pw = tval(0, ILT[i], ISLOT[i]);          // 0.3.29: the armor buff
  double sw = tval(1, ILT[i], ISLOT[i]);
  if (pw > 0.0) { txt.add((f == 0 ? "Chopping" : "Farming") + " Power +" + num(pw) + "%"); col.add(null); }
  if (sw > 0.0) { txt.add("Breaking Speed +" + num(sw) + "%"); col.add(null); }''')
rep('''  if (f > 0.0) { txt.add("Mining Fortune +" + num(f)); col.add(null); }
  if (w > 0.0) { txt.add("Mining Wisdom +" + num(w) + "%"); col.add(null); }''', '''  if (f > 0.0) { txt.add("Mining Fortune +" + num(f)); col.add(null); }
  if (w > 0.0) { txt.add("Mining Wisdom +" + num(w) + "%"); col.add(null); }
  double pw = @PKG@.GearGArm.tval(0, LT[i / 4], i % 4);          // 0.3.29: the armor buff
  double sw = @PKG@.GearGArm.tval(1, LT[i / 4], i % 4);
  if (pw > 0.0) { txt.add("Mining Power +" + num(pw) + "%"); col.add(null); }
  if (sw > 0.0) { txt.add("Breaking Speed +" + num(sw) + "%"); col.add(null); }''')
rep('''  if (f > 0.0 || w > 0.0) { txt.add("Mining lines work with a pickaxe or shovel in hand"); col.add(@PKG@.GearDefs.C_GRAY); }''',
    '''  if (f > 0.0 || w > 0.0 || pw > 0.0) { txt.add("Mining lines work with a pickaxe or shovel in hand"); col.add(@PKG@.GearDefs.C_GRAY); }''')
# migrate0329: the old buff rows (still at 0.3.28's defaults) + the armor cap
rep('''for _k, _o, _n in (("multi.speedPct", "85", str(MULTI_SPD_DEF)),''', '''H29_ROWS.append(("garmor.fishing", GA2_STAT_V28[2], GA2_STAT_DEF[2], "garmor.fishing", GA2_STAT_V28[2], GA2_STAT_DEF[2]))
H29_ROWS.append(("armor.fortune.cap", "100", "0", "armor.fortune.cap", "100", "0"))
for _ro, _rn in zip(MINE_ROWS_V28, MINE_ROWS):
    H29_ROWS.append(("garmor.mining." + _ro[0], "%s,%s,%d" % _ro[1:4], "%s,%s,%d" % _rn[1:4], "garmor.mining[%s]" % _ro[0], "%s|%s|%d" % _ro[1:4], "%s|%s|%d" % _rn[1:4]))
    H29_ROWS.append(("set.mining_" + _ro[0], "%s Mining Set,4,%s" % (_ro[0].capitalize(), _ro[4]), "%s Mining Set,4,%s" % (_rn[0].capitalize(), _rn[4]), "set[mining_%s]" % _ro[0],
                     "%s Mining Set|4|%s" % (_ro[0].capitalize(), _ro[4]), "%s Mining Set|4|%s" % (_rn[0].capitalize(), _rn[4])))
for _ro, _rn in zip(ZM_ROWS_V28, ZM_ROWS):
    H29_ROWS.append(("garmor.mining." + _ro[0], "%s,%s,%d" % (_ro[4], _ro[5], _ro[6]), "%s,%s,%d" % (_rn[4], _rn[5], _rn[6]), "garmor.mining[%s]" % _ro[0],
                     "%s|%s|%d" % (_ro[4], _ro[5], _ro[6]), "%s|%s|%d" % (_rn[4], _rn[5], _rn[6])))
    H29_ROWS.append(("set.mining_" + _ro[0], "%s Mining Set,4,%s" % (_ro[1], _ro[7]), "%s Mining Set,4,%s" % (_rn[1], _rn[7]), "set[mining_%s]" % _ro[0],
                     "%s Mining Set|4|%s" % (_ro[1], _ro[7]), "%s Mining Set|4|%s" % (_rn[1], _rn[7])))
for _k, _o, _n in (("multi.speedPct", "85", str(MULTI_SPD_DEF)),''')
rep('''assert _dp.get("lifelong.abilityLevels") == AB_LV_DEF and _dp.get("garmor.mining.bronze") == "0.2 0.4 0.2 0.2,0 0 0 0,2" and _dp.get("set.mining_bronze") == "Bronze Mining Set,4,mfort+2 mpow+2.5"''',
    '''assert _dp.get("lifelong.abilityLevels") == AB_LV_DEF and _dp.get("garmor.mining.bronze") == "%s,%s,%d" % BZ_ROW[1:4] and _dp.get("set.mining_bronze") == "Bronze Mining Set,4,%s" % BZ_ROW[4]
assert _dp.get("garmor.powerPct") == GB_POW_DEF and _dp.get("garmor.swingPct") == GB_SWG_DEF and _dp.get("garmor.mining.copper") == "%s,%s,%d" % MINE_ROWS[0][1:4]''')
# the hatchet ladder's log costs follow the NEW tree tiers (the key tree of the step's T: Iron T2 Beech, Bronze T3 Maple, Thorium T4 Dry, Lead T5 Bottletree ...)
rep('''GA2_LAD_V29E = list(GA2_LAD_DEF)          # the 15-tier ladders before the plain rule (proof only)
''', '''GA2_LAD_V29E = list(GA2_LAD_DEF)          # the 15-tier ladders before the plain rule (proof only)
_LOGK29 = dict((ENCH.PREFIX + _t[0], _t[2]) for _t in list(ENCH.TABLE) + list(ENCH.TABLE_C1) if _t[1] == "I" and _t[2].startswith("Wood_") and _t[2].endswith("_Trunk"))
_KEYT29 = dict((_t, [_k for _k, _b in _LOGK29.items() if _b == "Wood_%s_Trunk" % TT.LOGS[_t][0]][0]) for _t in TT.LOGS)          # T -> its key tree's Enchanted log


def retree29(text):
    """every hatchet / multitool step's Enchanted log = the key tree of the step's T (tools/tier_tags.py LOGS[T][0])"""
    def _one(m):
        _t = _lt29t(m.group(1))
        if _t is None or not ("Hatchet" in m.group(1)):
            return m.group(0)
        _c = "+".join((_KEYT29[min(_t, 15)] + "*" + _x.rsplit("*", 1)[1]) if _x.rsplit("*", 1)[0] in _LOGK29 else _x for _x in m.group(2).split("+"))
        return "%s(%s)" % (m.group(1), _c)
    return re.sub(r"([A-Za-z0-9_]+)\\(([^()]*)\\)", _one, text)


LL_LADDER_DEF, MT_LAD_DEF = retree29(LL_LADDER_DEF), retree29(MT_LAD_DEF)
assert "Tool_Hatchet_Iron(Skyy_Ench_Iron*1+Skyy_Ench_Beech*1)" in LL_LADDER_DEF and "Tool_Hatchet_Lumen_SkyWynn(Ingredient_Bar_Lumen_SkyWynn*256+Skyy_Ench_CrystalLog*4)" in LL_LADDER_DEF
''')

rep('''assert [_rowdef[_k] for _k in H28_KEYS] == H28_NEW, "0.3.28: the Server Setup rows hold the new defaults"''',
    '''assert [_rowdef[_k] for _k in H28_KEYS[:2]] == H28_NEW[:2] and _rowdef["armor.fortune.cap"] == "0", "0.3.28: the Server Setup rows hold the new defaults (0.3.29: armor cap 0)"''')


# ================================================================================================================ 8: crops by tier, alloy recipes by knowledge, alloy tools by Furnace Charm
# (main session 2026-10-18: the watering can + Harvester steps cost the key crop of their own T; alloy armor recipes KnowledgeRequired (SkyyCollections
# 0.2.28 grants recipe:<id> when BOTH input collections reach V - Skyy "then bronze when both reach 5"); an alloy tool tier-up needs the Furnace Charm
# tier that smelts the alloy (Skyy: the charm tier that smelts the alloy also unlocks the alloy's tools) - SkyyAccessories' acc:smelt:<uuid>)
rep('''LL_LADDER_DEF, MT_LAD_DEF = retree29(LL_LADDER_DEF), retree29(MT_LAD_DEF)
''', '''LL_LADDER_DEF, MT_LAD_DEF = retree29(LL_LADDER_DEF), retree29(MT_LAD_DEF)
# the watering can / Harvester / hoe / sickle steps: the key crop of the step's T on the 15-crop ladder (tools/tier_tags.py CROP_LADDER)
_CROPK29 = dict((ENCH.PREFIX + _t[0], _t[2]) for _t in list(ENCH.TABLE) + list(ENCH.TABLE_C1) if _t[1] == "I" and _t[2].startswith("Plant_Crop_"))
_KEYC29 = dict((_k + 1, ENCH.PREFIX + _c) for _k, _c in enumerate(TT.CROP_LADDER))
assert all(_v in _CROPK29 for _v in _KEYC29.values()), "an Enchanted crop of the 15-crop ladder is missing"


def recrop29(text):
    """every can / Harvester / hoe / sickle step's Enchanted crop = the key crop of the step's T"""
    def _one(m):
        _t = _lt29t(m.group(1))
        if _t is None or not any(_w in m.group(1) for _w in ("WaterCan", "Sickle", "Hoe")):
            return m.group(0)
        _c = "+".join((_KEYC29[min(_t, 15)] + "*" + _x.rsplit("*", 1)[1]) if _x.rsplit("*", 1)[0] in _CROPK29 else _x for _x in m.group(2).split("+"))
        return "%s(%s)" % (m.group(1), _c)
    return re.sub(r"([A-Za-z0-9_]+)\\(([^()]*)\\)", _one, text)


LL_LADDER_DEF, CAN_LAD_DEF, HARV_LAD_DEF = recrop29(LL_LADDER_DEF), recrop29(CAN_LAD_DEF), recrop29(HARV_LAD_DEF)
assert "Tool_WaterCan_Iron(Skyy_Ench_Iron*1+Skyy_Ench_Lettuce*1)" in CAN_LAD_DEF and "Tool_Sickle_Harvester_Lumen_SkyWynn(Ingredient_Bar_Lumen_SkyWynn*256+Skyy_Ench_Mushroom*3)" in HARV_LAD_DEF
''')
# alloy armor recipes need knowledge (SkyyCollections grants them): the Bronze Mining set + the zone ALLOY Mining sets (Dusk, Azurvane, Cinder, Lumen)
ALLOY29 = ("Bronze", "Dusk", "Azurvane", "Cinder", "Lumen")
rep('''          "BenchRequirement": json.loads(json.dumps(_ir["BenchRequirement"])), "KnowledgeRequired": False, "TimeSeconds": _ir.get("TimeSeconds", 3)}''',
    '''          "BenchRequirement": json.loads(json.dumps(_ir["BenchRequirement"])), "KnowledgeRequired": True, "TimeSeconds": _ir.get("TimeSeconds", 3)}          # 0.3.29 item 8: SkyyCollections grants it''')
rep('''                     "BenchRequirement": json.loads(json.dumps(_vr0["BenchRequirement"])), "KnowledgeRequired": False,''',
    '''                     "BenchRequirement": json.loads(json.dumps(_vr0["BenchRequirement"])), "KnowledgeRequired": _metal in ("Dusk", "Azurvane", "Cinder", "Lumen"),          # 0.3.29: alloy sets by knowledge''')
rep('''assert [[_x["Quantity"] for _x in _r["Input"]] for _rid, _o, _r in BZ_RECIPES] == [[9, 4, 3], [16, 7, 6], [7, 3, 3], [13, 6, 4]], "spec 3.3: Iron's amounts"''',
    '''assert [[_x["Quantity"] for _x in _r["Input"]] for _rid, _o, _r in BZ_RECIPES] == [[9, 4, 3], [16, 7, 6], [7, 3, 3], [13, 6, 4]], "spec 3.3: Iron's amounts"
assert all(_r["KnowledgeRequired"] is True for _rid, _o, _r in BZ_RECIPES)''')
rep('''for _n in ZM_MODEL_NOTES:
    print("  NOTE Quirk's model " + _n)''', '''for _n in ZM_MODEL_NOTES:
    print("  NOTE Quirk's model " + _n)
# 0.3.29 item 8: the recipe ids SkyyCollections 0.2.28 grants (recipe:<id>) when BOTH input collections of the alloy reach V
ALLOY_RECIPES29 = [_rid for _rid, _o, _r in BZ_RECIPES] + ["%s_Recipe_Generated_0" % _i for _i in ZM_IDS if _i.split("_")[2] in ("Dusk", "Azurvane", "Cinder", "Lumen")]
for _k, _v in ZM_ITEMS.items():
    _j = json.loads(_v)
    assert _j["Recipe"]["KnowledgeRequired"] == (_k.split("/")[-1].split("_")[2] in ("Dusk", "Azurvane", "Cinder", "Lumen")), _k
assert len(ALLOY_RECIPES29) == 20 and not set(ALLOY_RECIPES29) & _ALL_RECIPE_IDS
print("0.3.29 alloy armor recipes by knowledge (SkyyCollections grants recipe:<id>): %s" % ", ".join(ALLOY_RECIPES29))''')
# the Furnace Charm gate of an alloy tool tier-up (SkyyAccessories 0.5.26: acc:smelt:<uuid> = "<tier 0-5>|time|fuel|eternal|<pkey>", the ACTIVE
# profile's equipped Void Charm; charm I smelts Bronze, II Dusk, III Azurvane, IV Cinder, V / Eternal Flame Lumen). No SkyyAccessories = refused.
rep('''# a tier-up needs the skill level the new tier starts at (its level.material start)
M(gll, r"""
public static String tierWhy(java.util.UUID u, String to) {''', '''# 0.3.29 item 8: the Furnace Charm tier an alloy tool tier-up needs (0 = none: not an alloy step)
F(gll, "public static final String[] CH_ALLOY = %s;" % jarr(["Bronze", "Dusk", "Azurvane", "Cinder", "Lumen"]))
M(gll, r"""
public static int charmNeed(String to) {
  if (to == null) return 0;
  String[] ps = to.split("_");
  for (int i = 1; i < ps.length; i++) for (int k = 0; k < CH_ALLOY.length; k++) if (CH_ALLOY[k].equals(ps[i])) return k + 1;
  return 0;
}""")
# the equipped Furnace Charm tier (acc:smelt:<uuid> of the ACTIVE profile: its pkey must be ours); 0 = none / another profile / no SkyyAccessories
M(gll, r"""
public static int charmHave(java.util.UUID u) {
  if (u == null) return 0;
  try {
    Object o = @PKG@.Gear.bget("acc:smelt:" + u.toString());
    if (!(o instanceof String)) return 0;
    String[] a = ((String) o).split("\\\\|", -1);
    if (a.length < 5 || !a[4].equals(@PKG@.Gear.pkey(u))) return 0;
    int t = Integer.parseInt(a[0].trim());
    return t < 0 ? 0 : t;
  } catch (Throwable t) { return 0; }
}""")
M(gll, r"""
public static String charmWhy(java.util.UUID u, String to) {
  int n = charmNeed(to);
  if (n <= 0 || u == null || charmHave(u) >= n) return null;
  return "Needs the Furnace Charm " + roman(n) + " in your Void Charms to tier up to " + an(@PKG@.Gear.itemName(to)) + ".";
}""")
# a tier-up needs the skill level the new tier starts at (its level.material start)
M(gll, r"""
public static String tierWhy(java.util.UUID u, String to) {''')
rep('''      if (@PKG@.GearLevel.floor(h1) < need) return "You need " + KSKILL[1] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h1 + ").";
    }
  }
  return collWhy(u, to);          // 0.3.17: + the collection gate''', '''      if (@PKG@.GearLevel.floor(h1) < need) return "You need " + KSKILL[1] + " " + need + " to tier up to " + an(@PKG@.Gear.itemName(to)) + " (you: " + h1 + ").";
    }
  }
  String cw = charmWhy(u, to);          // 0.3.29: an alloy step needs its Furnace Charm
  if (cw != null) return cw;
  return collWhy(u, to);          // 0.3.17: + the collection gate''')
rep('''# 0.3.25: the multitool asks both tools' tokens (GearLL.collWhy)
M(gq, r"""
public static void collRow(java.util.UUID u, String from, String to, java.util.ArrayList rows) {
  collRow0(u, from, to, rows, to == null ? null : @PKG@.GearLL.collKind(to));
  if (to != null && @PKG@.GearData.multiId(to)) collRow0(u, from, to, rows, "hatchet");
}""")''', '''# 0.3.29: the Furnace Charm row of an alloy tool tier-up ("Furnace Charm I", green when equipped in Void Charms)
M(gq, r"""
public static void charmRow(java.util.UUID u, String from, String to, java.util.ArrayList rows) {
  if (u == null || to == null || from == null || !@PKG@.GearLL.ladderTool(from)) return;
  int n = @PKG@.GearLL.charmNeed(to);
  if (n <= 0) return;
  add(rows, "Furnace Charm " + @PKG@.GearLL.roman(n), @PKG@.GearLL.charmHave(u) >= n ? 1 : 0);
}""")
# 0.3.25: the multitool asks both tools' tokens (GearLL.collWhy); 0.3.29: + the Furnace Charm row
M(gq, r"""
public static void collRow(java.util.UUID u, String from, String to, java.util.ArrayList rows) {
  collRow0(u, from, to, rows, to == null ? null : @PKG@.GearLL.collKind(to));
  if (to != null && @PKG@.GearData.multiId(to)) collRow0(u, from, to, rows, "hatchet");
  charmRow(u, from, to, rows);
}""")''')
rep('''    if (why.equals(@PKG@.GearLL.tierWhy(u, to)) || why.equals(@PKG@.GearArmLv.tierWhy(u, to))) return true;''',
    '''    if (why.equals(@PKG@.GearLL.tierWhy(u, to)) || why.equals(@PKG@.GearArmLv.tierWhy(u, to)) || why.equals(@PKG@.GearLL.charmWhy(u, to))) return true;''')


# ================================================================================================================ 9: the Soul Orb craft level + Legendary frames (beta bug 21)
# Skyy's test: a Soul Orb (SkyyArmory's Weapon_Wand_SoulOrb, ItemLevel 3) crafted at Divinity ~14 came out [Lv 3] ("i crafted it at lvl 14").
# ROOT CAUSE: no level.material row matches any word of Weapon_Wand_SoulOrb, so GearLevel.band falls to its Hytale ItemLevel (level.vanilla: an
# EXACT band 3-3) and GearRoll.craftLevel clamps the crafter's class level (Divinity) into it. The craft does read the class skill. Same for
# SkyyArmory's Weapon_Fist_Wraps_Shadoweave (the cloth wraps' top step). Fix: two level.material rows - SoulOrb 1-8 (the Crude / Wood starter
# wand band: made at your Divinity, cap 8 under the new bands) and Shadoweave 60-67 (the cloth ladder's next step after Cindercloth 50-57, T10)
# - in the fresh file's 0.3.29 block and added by migrate0329 to a file that lacks them. Stored levels stay.
rep('''H29_ADD = [("garmor.mining.bronze",''', '''H29_ADD = [("level.material.SoulOrb", "# 0.3.29 the Soul Orb (the Priest's starter wand): made at your class level inside the Crude / Wood band",
            "level.material.SoulOrb=%s" % band_text(*TT.band("Crude")), "", ""),
           ("level.material.Shadoweave", "# 0.3.29 Shadoweave (the cloth wraps' top step, after Cindercloth): its own band",
            "level.material.Shadoweave=%s" % band_text(TT.remap_family_start(35), TT.remap_family_start(35) + BAND_W_DEF - 1), "", ""),
           ("garmor.mining.bronze",''')
rep('''    for _a in H29_ADD[:2]:
        L += [_a[1], _a[2]]''', '''    for _a in H29_ADD[:4]:          # SoulOrb, Shadoweave, the two Bronze Mining rows (not the conditional abilityLevels line)
        L += [_a[1], _a[2]]''')
rep('''assert _dp.get("garmor.powerPct") == GB_POW_DEF and''', '''assert _dp.get("level.material.SoulOrb") == "1,8" and _dp.get("level.material.Shadoweave") == "60,67", "0.3.29: the Soul Orb + Shadoweave bands"
assert _dp.get("garmor.powerPct") == GB_POW_DEF and''')
# beta bug 21 (Skyy 2026-10-18 "Legendary rarity colour does not stand out"): Legendary (Wynn aqua #55FFFF, unchanged) wore the vanilla RARE frames
# (dark blue, near Common in the inventory). Its tooltip, arrow and slot frames are now the vanilla Rare art gradient-mapped onto a bright saturated
# aqua at build time (tools/skyyart.py recolor; generated into the jar, nothing vanilla committed) - Common grey, Set green, Rare (Epic frame)
# purple, Fabled red, Untiered gold stay; Quirk may replace the three PNGs with hand-drawn ones of the same names / sizes later.
rep('''# ================================================================= spec 2.1: the 7 quality assets + lang lines (jar asset pack)
EXTRA = {}
LANG = []''', '''# ================================================================= spec 2.1: the 7 quality assets + lang lines (jar asset pack)
EXTRA = {}
LANG = []
# 0.3.29 (beta bug 21): Legendary's own aqua frames (generated below from the vanilla Rare art; the @2x files are the ones Assets.zip has)
LEG29_TEX = {"ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltipSkyyLegendary.png",
             "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltipSkyyLegendaryArrow.png",
             "SlotTexture": "UI/ItemQualities/Slots/SlotSkyyLegendary.png", "BlockSlotTexture": "UI/ItemQualities/Slots/SlotSkyyLegendary.png",
             "SpecialSlotTexture": "UI/ItemQualities/Slots/SlotSkyyLegendary.png"}
LEG29_SRC = [("Tooltips/ItemTooltipRare@2x.png", "Tooltips/ItemTooltipSkyyLegendary@2x.png"), ("Tooltips/ItemTooltipRareArrow@2x.png", "Tooltips/ItemTooltipSkyyLegendaryArrow@2x.png"),
             ("Slots/SlotRare@2x.png", "Slots/SlotSkyyLegendary@2x.png")]
LEG29_RAMP = ("#04262d", "#0b6d7d", "#2ee8ff", "#d8feff")          # dark teal body -> bright saturated aqua rim -> near-white glint (the Rare art's own contrast)''')
rep('''    _vanilla_fields = set(json.loads(AZ.read("Server/Item/Qualities/Common.json").decode("utf-8")).keys())
    assert set(_q.keys()) == _vanilla_fields, "quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _vanilla_fields)
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert az_texture(_q[_k]), "texture missing: " + _q[_k]''', '''    if _rid == "legendary":          # 0.3.29 (beta bug 21): its own aqua frames
        _q.update(LEG29_TEX)
    _vanilla_fields = set(json.loads(AZ.read("Server/Item/Qualities/Common.json").decode("utf-8")).keys())
    assert set(_q.keys()) == _vanilla_fields, "quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _vanilla_fields)
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert az_texture(_q[_k]) or (_rid == "legendary" and _q[_k] in LEG29_TEX.values()), "texture missing: " + _q[_k]''')
rep('''EXTRA.update(GA2_ITEMS)
''', '''EXTRA.update(GA2_ITEMS)
# 0.3.29 (beta bug 21): the Legendary frames - the vanilla Rare tooltip / arrow / slot art gradient-mapped onto LEG29_RAMP (same sizes, alpha kept)
LEG29_FILES = {}
for _s29, _d29 in LEG29_SRC:
    _src29 = AZ.read("Common/UI/ItemQualities/" + _s29)
    _out29 = SA.recolor(_src29, _ramp(LEG29_RAMP), rank=0.0)          # rank 0: keeps the vanilla art's own light / dark spread
    assert SA.png_size(_out29) == SA.png_size(_src29) and ("Common/UI/ItemQualities/" + _d29) not in AZ_NAMES
    LEG29_FILES["Common/UI/ItemQualities/" + _d29] = _out29
assert sorted("UI/ItemQualities/" + _d[:-7] + ".png" for _s, _d in LEG29_SRC) == sorted(set(LEG29_TEX.values()))
EXTRA.update(LEG29_FILES)
''')


# ================================================================================================================ 10: Quirk's 15 Farming armor sets (PRIVATE art)
# Quirk's real Farming sets (Skyy 2026-10-18 "looking good!"; ../SkyWynn-PRIVATE-art/farming-armor/TASK-farming-armor.md) replace the P1-P7
# recolours and the 8 0.3.29 placeholders. PRIVATE (built on vanilla armor shapes): read at BUILD time into the jar only, like the mining-armor
# textures - never copied into the repo. The item ids stay (P1 .. P7 + the 8 crop ids: saved items and their set ids keep working); each id
# points at its crop's model / texture / icon. Hide flags (hair, ears, head accessory) + icon framing = the crop's vanilla base piece (Quirk's
# README "Vanilla base"), so the cut-away hat brims show hair like that base. Mushroom's glow lives in its model (fullbright shading).
rep('''GA2_ART = ["art/gathering-armor", "placeholder", "placeholder"]''', '''GA2_ART = ["art/gathering-armor", "private:farming-armor", "placeholder"]          # 0.3.29: Quirk's Farming sets (private, build time)''')
rep('''    if _f == 0:
        _bj["ItemSoundSetId"] = "ISS_Armor_Leather"
        _rel = "Items/Armors/SkyyForaging/%s/%s/%s" % (GA2_ARTDIR[_look], _look, _sl)          # 0.3.29: the tree's own art folder''',
    '''    if _f == 1:          # 0.3.29: Quirk's Farming set of this crop (PRIVATE, read at build time; the base piece's hide flags + icon framing)
        _rel = "Items/Armors/SkyyFarming/%s/%s" % (_look, _sl)
        _bj["Model"] = _rel + ".blockymodel"
        _bj["Texture"] = _rel + "_Texture.png"
        _bj["Icon"] = "Icons/ItemsGenerated/Armor_Farming_%s_%s.png" % (_look, _sl)
        _fbase = "Armor_%s_%s" % (FARM_BASE29[_look], _sl)
        _bj["Armor"]["CosmeticsToHide"] = list((az_get(_fbase, "Armor") or {}).get("CosmeticsToHide") or [])
        if az_get(_fbase, "IconProperties"):
            _bj["IconProperties"] = json.loads(json.dumps(az_get(_fbase, "IconProperties")))
        for _p in (_bj["Model"], _bj["Texture"], _bj["Icon"]):
            _fp = os.path.join(FARM_ART29, _look, "Common", *_p.split("/"))
            if not os.path.isfile(_fp):
                raise SystemExit("SkyyGear 0.3.29: Quirk's Farming armor file %s is missing (private art folder %s)" % (_fp, FARM_ART29))
            GA2_FILES["Common/" + _p] = open(_fp, "rb").read()
        FARM_FILES29.append("Common/" + _bj["Model"])
    elif _f == 0:
        _bj["ItemSoundSetId"] = "ISS_Armor_Leather"
        _rel = "Items/Armors/SkyyForaging/%s/%s/%s" % (GA2_ARTDIR[_look], _look, _sl)          # 0.3.29: the tree's own art folder''')
rep('''GA2_BAND_LO = [int(_b.split("-")[0]) for _b in GA2_BANDS_DEF.split(",")]          # 0.3.29: by ladder T - 1''',
    '''GA2_BAND_LO = [int(_b.split("-")[0]) for _b in GA2_BANDS_DEF.split(",")]          # 0.3.29: by ladder T - 1
# 0.3.29 item 10: Quirk's Farming art (PRIVATE: SKYWYNN_PRIVATE_ART or ../SkyWynn-PRIVATE-art next to the project) + each crop's vanilla base
FARM_ART29 = os.path.join(os.environ.get("SKYWYNN_PRIVATE_ART") or os.path.join(os.path.dirname(os.path.dirname(HERE)), "SkyWynn-PRIVATE-art"), "farming-armor")
if not os.path.isdir(FARM_ART29):
    raise SystemExit("SkyyGear 0.3.29 needs Quirk's private Farming armor: %s is missing. Put the SkyWynn-PRIVATE-art folder next to the project "
                     "(or set SKYWYNN_PRIVATE_ART) - the files are never committed to the public repo." % FARM_ART29)
FARM_BASE29 = {"Wheat": "Wood", "Lettuce": "Wood", "Carrot": "Leather_Soft", "Corn": "Leather_Light", "Cauliflower": "Leather_Medium",
               "Turnip": "Leather_Heavy", "Pumpkin": "Copper", "Aubergine": "Bronze", "Tomato": "Iron", "Chilli": "Thorium", "Cotton": "Cloth_Silk",
               "Rice": "Cloth_Linen", "Potato": "Adamantite", "Onion": "Cobalt", "Mushroom": "Prisma"}          # Quirk's README "Vanilla base" per crop
assert sorted(FARM_BASE29) == sorted(GA2_LOOK[1])
for _c29, _b29 in FARM_BASE29.items():
    _rm29 = open(os.path.join(FARM_ART29, _c29, "README.md"), encoding="utf-8").read()
    assert ("`%s`" % _b29.replace("Cloth_", "")) in _rm29 or ("**%s**" % _b29) in _rm29, "Quirk's README of %s names another base than %s" % (_c29, _b29)
    assert all(("Armor_%s_%s" % (_b29, _s)) in AZ_ITEMS for _s in ("Head", "Chest", "Hands", "Legs")), _b29
FARM_FILES29 = []''')
rep('''print("0.3.6 gathering armor: %d items (%d sets), %d files (Foraging = the approved art, Farming / Fishing = placeholder recolours)"''',
    '''assert len(FARM_FILES29) == 60, "0.3.29: the 15 Farming sets from Quirk's art"
print("0.3.6 gathering armor: %d items (%d sets), %d files (Foraging = the approved art, Farming = Quirk's private sets, Fishing = placeholder recolours)"''')


# ================================================================================================================ review fix F3: a made multitool is never shown the rebirth gate
rep('''  this.mlKey = null;
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { tx = "Rebirth 1 : " + @PKG@.GearLL.rbHave(u); bl = "Rebirth 1"; }          // 0.3.29: the red requirement row (Menu-Pattern rule 9)''',
    '''  this.mlKey = null;
  String gate = @PKG@.GearLL.mtm(P) ? null : @PKG@.GearLL.rbGate(u);          // review F3: a player who already HAS the multitool sees mtCheck's line, not the gate
  if (gate != null) { tx = "Rebirth 1 : " + @PKG@.GearLL.rbHave(u); bl = "Rebirth 1"; }          // 0.3.29: the red requirement row (Menu-Pattern rule 9)''')
rep('''public void makeLlMt(@INV@ inv) {
  java.util.UUID u = this.playerRef.getUuid();
  String gate = @PKG@.GearLL.rbGate(u);
  if (gate != null) { this.info = "-" + gate; this.mlArmKey = null; return; }
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);''', '''public void makeLlMt(@INV@ inv) {
  java.util.UUID u = this.playerRef.getUuid();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  String gate = @PKG@.GearLL.mtm(P) ? null : @PKG@.GearLL.rbGate(u);          // review F3: mtCheck answers "You already have your multitool." first
  if (gate != null) { this.info = "-" + gate; this.mlArmKey = null; return; }''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i("public static boolean h23Old(") < _i("public static Object[] h29Update(") < _i("public static String h29Log(") < _i("public static synchronized String migrate0329()")
assert _i("public static synchronized String migrate0328()") < _i("public static Object[] h29Update(") and _i("  @PKG@.GearCfg.migrate0328();") < _i("  @PKG@.GearCfg.migrate0329();")
assert _i("public static int[] abParse(") < _i("public static int[] abLv()") < _i("public static int abNeed(int n)") < _i("public static int abilCapLv(") < _i("public static int abilCap(") < _i("public static int pkNeedLv(")
assert _i("H29_KEYS = [") < _i("def default_text():") and _i("G329_HEAD = ") < _i("def default_text():") and _i("GA2_LT = [") < _i('F(gga, "public static final int[] ILT')
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count(' = mk("') == MK0, "no new class"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) >= _cnt
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.28 outside the recorded changes"

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.28 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
