# Skill Trees 2: Alchemy, Smithing and class trees (spec for SkyyTrees 0.3)

*Written 2026-10-02. Research and planning only: nothing is built, deployed or committed. Owner: Skyy (they/them).*

**Tags:** **VERIFIED** = seen in a build script, jar or Assets.zip (file:line given). **UNVERIFIED** = not proven yet.

| Short ref | File |
|---|---|
| T | `SkyyTrees/build_skyytrees_0.2.5.py` (the SET pin) |
| S | `SkyySkills/build_skyyskills_0.4.12.py` |
| G | `SkyyGear/build_skyygear_0.2.py` |
| K | `SkyySacks/build_skyysacks_0.7.12.py` |
| Spec1 | `research/Skill-Trees-Spec.md` |
| Runes | `research/Hytale-Runes-Research.md` |
| Audit | `research/PreRelease-Compat-Audit-1002.md` |

Line numbers are the pinned scripts (the SET). SkyyGear 0.2.1 and SkyySkills 0.4.13 are built but not pinned: their line numbers are about 450-1,050 (Gear) and 112 (Skills) higher than cited, and the functions this spec touches are unchanged in them (checked for `smithChance`, `rollMods`, `reforge`, `identify`, `costReforge`, `extraPotion`, `bonusFor`, `treeName`, `treeAvailable`). SkyyGear has no patch scripts (every version is a full copy of the last); SkyyTrees and SkyySkills use `tools/<mod>_<ver>_patch.py`. Critic pass 2026-10-02: every cited line was re-read, corrections are listed in section 16.

## 0. Plain English (for Skyy)

1. **Alchemy and Smithing trees** work exactly like Mining's: 12 nodes, Tokens unlock them, Dust (from that skill's XP) levels them up, tiers open at skill 1 / 10 / 20 / 30 / 45 / 60, respec is free, and the costs match every other tree.
2. **Alchemy tree:** more potions (extra, double and next-tier brews, one node per potion family, extra seeds), potions you drink last longer, ingredients back, Alchemy XP and +Mana.
3. **Smithing tree:** your three locked lines: **better craft rarity** (open from Smithing 1), **better reforge rolls** and **better identify rolls** (open at Smithing 10), and a **chance at a higher rarity when you identify** (open at Smithing 20). It also gives extra bars, faster smelting, fuel saving, cheaper reforges, Smithing XP and +Health. Crafting and identifying gear will start paying Smithing XP.
4. **Every class gets a Wynncraft-style tree:** Archer, Warrior, Mage, Berserker and Priest, plus Assassin and Shaman when they ship.
   - One map of **37 nodes on 2 pages**; you unlock nodes next to ones you own.
   - **Ability Points (AP)** come from your class skill: 1 at level 1, then +1 every 2 levels, up to 50.
   - Nodes cost 1-4 AP. There are 3 archetype lanes and one "pick one of two" choice.
5. **Works today:** Health, Mana and Mana Regen (Mage and Priest); Strength as soon as SkyyGear reads it; and your two approved Archer crossbow upgrades (bigger magazine, holstered reload) if the engine check passes. That is 27 AP of nodes (21 for an Archer if the crossbow check fails), all yours by about class skill 52.
6. **Greyed "Coming with runes" until 0.7:**
   - 4 ability slots, each with its own 2 modifier slots. That is exactly one Runebinder's bench line: 1 ability + 2 modifiers.
   - 1 capstone ability per lane (not called "signature", because vanilla's Signature is the weapon's own special attack).
   - 3 element nodes (these wait for SkyyGear's elements, not for runes).

   In 0.7 you equip 2 unlocked abilities at a time (Hytale's limit). Until then they do nothing.
7. **Pages:** /tree gets a second tab row (row 1 MINING to SMITHING, row 2 ACROBATICS, EXPLORATION and your class), a page 1 / 2 switch on the class page and a "Rune slots" strip. /skills gets TREE buttons on Alchemy, Smithing and the class row.
8. **0.7:** you chose to wait for the release (LOCKED 2026-10-02). On release day we work through the audit's fix list (section 11), then fill the ability slots.
9. **Other mods:** SkyySkills, SkyyGear and SkyySacks apply most of the Alchemy and Smithing effects. They get small updates and ship **together** with SkyyTrees 0.3 in one full round. SkyyGear's update has to ride on its own queue (0.2.1 now, then 0.2.2 tool levels and 0.2.3 loot), see section 12. Until a reader ships, its nodes can be bought but do nothing (like the "needs SkyySkills 0.4" nodes today).
10. **Placeholders:** all names and numbers can change, and every number is a Server Setup row. Section 14 has seven questions for you and two planning calls for the main session.

## 1. Facts this spec builds on (VERIFIED unless marked)

**Template trees** (T:703-715): 6 trees x 12 nodes. The tree list is append-only.

| Per slot | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tier | 1 | 1 | 1 | 2 | 2 | 3 | 3 | 4 | 4 | 5 | 5 | 6 |
| Max level | 25 | 20 | 15 | 10 | 10 | 15 | 10 | 10 | 10 | 20 | 10 | 5 |
| B | 5 | 5 | 5 | 150 | 150 | 100 | 500 | 1000 | 1000 | 200 | 4000 | 150000 |
| Tokens | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 3 |

- **Costs:** Tokens = 1 + floor(level / 5) at level 1 or more, 0 below (`tokensEarned`, T:2301-2305). Dust = XP / rate (10; Acrobatics 2, Exploration 5; T:711). **Mining becomes 5 in 0.3** (LOCKED 2026-10-02, OPEN-QUESTIONS l.194-198: a file with no `dust.xpPerDust.Mining` line gets 5, a hand-set value is kept; Skyy can already add it in Server Setup). Level n to n+1 costs B x n^3 (T:2321). A template tree costs 37,778,125 Dust to max (T:877 checks Mining's 12 rows); Foraging costs 56,528,125 because Tree Feller has 6 levels since 0.2.4 (T:839, T:865). The two new trees use the plain template (all S12 = 5 levels).
- **Hooks:** `tree:fn:level` / `tree:fn:bonus` take Object[]{UUID, "Tree.Id"} (T:3188-3214). SkyyCooking and SkyyExploration already read them.
- **Stat modifiers:** SkyyTrees sets `skyytree_health` and `skyytree_stamina` (T:2574-2585). SkyySkills sets `skyyskill_mana` the same way (code S:6796 `mod(m, getMana(), "skyyskill_mana", ...)`; S:674 is only the header note), so `skyytree_mana` follows a proven pattern. The build's API probe list (T:623, the `DST` token is T:595) must gain `("DST", "getMana")`.
- **Tree buttons on /skills:** `treeName()` hard-codes 6 trees (S:5755-5765). `treeAvailable()` also checks `tree:names` (S:5767-5779).
- **Alchemy (slot 10):** 50-18,000 XP per brewed item. Level perks: drunk potions last +1%/level, cap +100% (`Brew.bonusFor` S:6448, stored once a second by `Brew.setBonus` S:6460; `Brew.tick` extends each fresh drink once by base x bonus, S:6420-6520); +0.2 Mana/level; 0.2%/level (cap 25%) chance of an extra `Potion_*` / `Weapon_Bomb_*` (`Brew.extraChance` S:6454). The extra-potion roll is `Brew.extraPotion` (S:6955): one roll per finished unit, on the recipe's primary output, allowed by an id-prefix list (`AlchCfg.extraOk` S:3311: only `Potion_`, `Weapon_Bomb_`, never `Potion_Empty`). It is called from the vanilla-bench `CraftTask` (S:9304) and from the bridge task (S:9360).
- **Smithing (slot 11):** XP comes from Furnace take-outs (`SmeltSys` S:9812), the /craft Furnace (`drainXp` K:6075) and reforges (5-160, G:7259-7267). Identifying and crafting gear pay **no** XP (G:10126, G:5900). Smithing rarity = level x 0.5%, cap 50% (`smithChance` G:5640).
- **Wisdom:** boosts only skills in `bridge.bonus.xpSkills` (Mining, Foraging, Farming, Cooking; S:1286). XP granted by other mods also needs `addxpSkills` (Cooking; S:1287). Both are Server Setup rows (S:11149-11151).
- **Class skills:** the class rows are S:2726-2735 (Archery, Swordsmanship, Sorcery, Fury, Divinity; Assassin and Shaman exist as stubs). Their own XP table is `CLASS_LEVELS` (S:1079-1096; asserted there: 21,540 XP at skill 20, 209,090 at 40, 6,627,590 at 100) = the `levels.class` line (S:1713), and an admin can change it with `levels.class.scale`, `levels.class.max` (1-100) and `levels.class.sameAsOthers` (S:2866-2871). AP follows whatever those say. `skill:fn:level` accepts class names (docs S:700, code `SkillDefs.indexOf` S:2947). The class is in `class:<uuid>` ("Archer", SkyyClasses 0.1.10 l.1639) and `class:skill:<uuid>` ("Archery"). Mana Regen registry: `skill:fn:manaregen` {"add", UUID, source, %} (S:8019-8057; the source shows as `trees=+5` in `/skills mana`, S:7825), unused so far.
- **Kill XP is live-tuned:** SkyyMobs 0.1 (live) raises mob health per level and kill XP follows mob health (OPEN-QUESTIONS R5), and the new lock "level bonus + gap rule" (l.218, next SkyySkills: kill XP x (1 + 5% per mob level), up to +250% for mobs far above your class skill) adds more, so the class pace below is an upper bound.
- **Strength:** a live SkyyGear stat (G:657; 1 point = +1% physical damage by default, `combat.strPer` G:1917, G:7696; a weapon roll tops out at 25, so the Warrior's tree +25 equals a top roll). Its only outside input is `gear:extra:<uuid>`, one String owned by SkyyAccessories; any second writer backs off (`SkyyAccessories/build_skyyaccessories_0.5.2.py`:37-38, G:6544-6581). **So tree Strength needs a small SkyyGear change.**
- **Locked class-tree stats** (SkyyGear-Plan locks 16-18, 22, 23; Stat-Catalog l.36, 62, 68, 87-94, 106, 137-138):
  - Allowed: base Strength, flat Health and Mana, Mana Regen (magic classes only), Elemental Damage % and Elemental Defence (class trees only), raw spell damage and Ability Damage.
  - Not allowed: Percent Damage (scrapped). Magical Power, Crit, Defense and Speed have no class-tree placement in the catalog ("placement is the lock", Stat-Catalog l.28).
- **0.7 runes** (Runes 0 and 2.2-2.4, re-checked on 0.7.0-pre.4):
  - A rune is an item with an `Ability` block.
  - Each player gets 2 ability lines of 1 ability + 2 modifier slots (section -11) and a 50-slot rune bag (section -12).
  - Use Ability 2 / 3 casts line 1 / 2.
  - A modifier only fits next to an ability that matches its `AppliesTo`.
  - 0.6.8 has none of these classes.

## 2. Alchemy tree (template slots and costs)

Ids start with P. "SS" = applied by the next SkyySkills (section 12). Every icon exists in both the 0.6.8 and the 0.7 pre-release Assets.zip (checked read-only on 2026-10-02).

| Slot | Node (id) | Icon | Max | Per level (total at max) | Applied by |
|---|---|---|---|---|---|
| S1 | Extra Brew (PExtra) | Potion_Health_Small | 25 | +0.4% extra-potion chance (+10%), on top of the level perk and its cap | SS `Brew.extraPotion` |
| S2 | Long Brew (PDur) | Potion_Regen_Health (was Potion_Stamina: Stamina potions are instant) | 20 | +1% duration of the potion effects that can grow (+20%): Health and Signature regen, Morph, Antidote (`perk.alchemy.extend`, `ALCH_EXTEND` S:1278); instant effects cannot. Added after the level perk's +100% cap | SS `Brew.setBonus` |
| S3 | Alchemy Wisdom (PWisdom) | Bench_Alchemy | 15 | +1% Alchemy XP (+15%) | SkyyTrees posts `xp.alchemy`; SS needs Alchemy in `xpSkills` |
| S4 | Deep Reserves (PMana) | Potion_Mana | 10 | +1 max Mana (+10), like Forest Vigor's +1 Health | SkyyTrees `skyytree_mana` (new kind) |
| S5 | Frugal Brewer (PFrugal) | Potion_Empty | 10 | 2% chance to get back one random item input (20%); never a `Potion_Empty*` bottle or a resource type | SS: `rc.getInput()` + SkyyCooking's `frugalPick` rule (`SkyyCooking/build_skyycooking_0.1.3.py`:1734) |
| S6 | Health Brews (PHealth) | Potion_Health | 15 | +2% extra chance on `Potion_Health*` (+30%) | SS |
| S7 | Signature Brews (PSig) | Potion_Signature | 10 | +3% extra chance on `Potion_Signature*` (+30%) | SS |
| S8 | Stamina Brews (PStam) | Potion_Stamina_Small | 10 | +3% extra chance on `Potion_Stamina*` (+30%) | SS |
| S9 | Seed Brews (PSeed) | Plant_Seeds_Health1 | 10 | 3% chance of one extra brewed `Plant_Seeds_Health/Mana/Stamina1-3` (30%); today's perk skips seeds | SS |
| S10 | Long Brew II (PDur2) | Potion_Regen_Health_Large (was Potion_Stamina_Greater) | 20 | +1% duration, adds to S2 (+20%) | SS |
| S11 | Double Brew (PDouble) | Potion_Health_Large | 10 | 1.5% chance a brew gives two extra potions (15%) | SS |
| S12 | Master Brewer (PMaster) | Potion_Health_Greater | 5 | 5% chance of one bonus potion of the next tier (25%): Lesser > Small > plain > Greater, and a Greater gives another Greater. Health, Signature and Stamina only | SS |

- **At max (Alchemy 100):** a Health potion has 20% + 10% + 30% = 60% extra-potion chance, and the potion effects that can grow last +140% (a Health regen of 5 s becomes 12 s, a Signature regen of 30 s becomes 72 s: `HPR_DUR` / `SIG_DUR`, S:1345-1346). Stamina potions apply `Potion_Stamina_Instant_*` plus a cooldown (checked in Assets.zip), so they never last longer.
- **Where brewing happens:** only at the vanilla bench. /craft has had no Alchemy tab since SkyySacks 0.7.3.
- **Build check:** the build asserts every id in the tier chain.
- **Verified 2026-10-02 (read-only, both Assets.zip files):** the brewable chain of each family is Lesser, Small, plain, Greater: a Small eats a Lesser (+ a tier-1 crop), a Greater eats a plain potion (+ a tier-3 crop). The `Potion_*_Large` items (the S11 icon) have no recipe and `Potion_Mana*` are decorative, so Master Brewer stops at Greater and never touches them. `Plant_Seeds_Health/Mana/Stamina1-3` are Alchemy-bench recipes (category `Alchemy_Seeds`, 2 / 4 / 8 `Ingredient_Void_Essence`), so Seed Brews has something to roll on.
- **How the nodes plug into `Brew` (SkyySkills):**
  - S1 and S6-S8 add to the chance inside `Brew.extraPotion`, by the id prefix of `rc.getPrimaryOutput()`. Extras pay no XP.
  - S9, S11 and S12 are separate rolls in the same method. Seeds fail `extraOk` today, so Seed Brews needs its own prefix entry (`Plant_Seeds_`) and a roll that only the tree feeds (the level perk stays potion-only); Double Brew (two more of the same output) and Master Brewer (one of the next tier) roll after it.
  - Long Brew I / II: `Brew.setBonus` adds the tree total after `bonusFor`'s cap.
  - Frugal Brewer: `rc.getInput()`, the stack comes back through `Perks.give`.
- **Loop check:** the build's craft-loop assert (S:1334-1340) is about salvage give-backs and is unaffected. Frugal and the extras only lower the material cost (every chance stays below 1 per unit); re-run the pace table of `research/Alchemy-Skill-Spec.md` section 4 with 60% extras before the numbers are called final.

## 3. Smithing tree (template slots and costs)

Ids start with S. Skyy's three lines (LOCKED 2026-10-02, OPEN-QUESTIONS l.122-127, and the identify-rarity line l.178-182): craft rarity = S1 + S10; reforge = S4 (+ S12); identify = S5 + S7 (+ S12).

**Slot order changed in the critic pass (pace).** The first draft had reforge and identify rolls in tier III (Smithing 20) and the rarity step-up in tier V (Smithing 45). At the proposed XP rows Smithing 20 is about 5,300 crafts away (see Pace below), so Skyy's headline lines would have stayed locked for ages. Now the two roll nodes sit in tier II (S4, S5: Smithing 10, about 100 crafts), the rarity step-up in tier III (S7), and the plain utilities (Forge Hardened, Haggler) moved to the later slots. Per-level numbers are unchanged except Keen Eye and Forge Hardened (see their rows: both had to fit their new slot's max level).

| Slot | Node (id) | Icon | Max | Per level (total at max) | Applied by |
|---|---|---|---|---|---|
| S1 | Fine Craft (SRarity) | Bench_Weapon | 25 | +0.4% chance a crafted gear item steps up one rarity (+10%). Added on top of the level part, above `smith.cap`; never above `craft.maxRarity` | SkyyGear `smithChance` |
| S2 | Smelter's Luck (SSmelt) | Ingredient_Bar_Iron | 20 | 1% chance per bar of one extra bar (20%); `Ingredient_Bar_*` only | placed Furnace: SS `SmeltSys` on take-out (behind the XP guard); /craft Furnace: SkyySacks, per finished unit |
| S3 | Smithing Wisdom (SWisdom) | Tool_Hammer_Iron | 15 | +1% Smithing XP (+15%) | SkyyTrees posts `xp.smithing`; SS needs Smithing in `xpSkills` **and** `addxpSkills` |
| S4 | Steady Hand (SReforge) | Weapon_Sword_Iron | 10 | On reforge: 4% chance per modifier to roll twice and keep the higher (40%) | SkyyGear `GearRoll.reforge` (G:5917; no UUID today, its caller `GearForge.reforge` G:7215 has `u`: pass it in) |
| S5 | Keen Eye (SIdent) | Rock_Gem_Sapphire | 10 | On identify: 4% chance per modifier to roll twice and keep the higher (40%; the draft had 3% x 15 levels in tier III) | SkyyGear `GearRoll.identify` (has the UUID `by`, G:5931) |
| S6 | Forge Hardened (SHealth) | Armor_Iron_Chest | 15 | +1 max Health (+15; the draft had +10 in S4) | SkyyTrees `skyytree_health` |
| S7 | Appraiser (SAppraise) | Rock_Gem_Diamond | 10 | On identify: 1% chance the item steps up one rarity (10%); never above Fabled, never Mythic or Set | SkyyGear `GearRoll.identify`: write the next rarity id into the doc's `r` key (`GearData.rarity` reads it, G:4741) before `rollMods` |
| S8 | Quick Forge (SQuick) | Bench_Furnace | 10 | -3% smelt time in the /craft Furnace (-30%) | SkyySacks `unitMs` (K:1945), when the job is queued |
| S9 | Fuel Saver (SFuel) | Ingredient_Charcoal | 10 | 3% chance a fuel item is not used up in the /craft Furnace (30%) | SkyySacks `burnOne` (K:2094) |
| S10 | Fine Craft II (SRarity2) | Bench_Armory | 20 | +0.5% rarity-step chance, adds to S1 (+10%) | SkyyGear |
| S11 | Haggler (SHaggle) | Ingredient_Bar_Gold | 10 | -2% reforge and identify coin cost (-20%) | SkyyGear `costReforge` / `costIdentify`: 7 sites, all must apply it or the pages lie (G:4293 and 4299 the functions; charged at G:7226 and G:10137; shown at G:6234 tooltip (has `owner`), G:9892 reforge page, G:10343 identify page, G:10104 `GearIdent.costOf(it)` which has no UUID today) |
| S12 | Masterwork (SMaster) | Ingredient_Bar_Adamantite | 5 | On reforge or identify: 1% chance every modifier rolls its best value (5%) | SkyyGear |

- **Roll twice, keep the higher:** with the node's chance, today's `randInt(lo, hi)` in `rollMods` (G:5708-5741; `rollMods(id, slot, r, lvl)` gets the chance as one more argument) rolls a second time and the higher value is kept. It never goes above the rarity's top value and never changes which stats are picked. "Better picks" (choosing between two rerolls) needs a reforge-page change, so it comes later. `reforge` re-rolls the whole modifier set (G:5917), so Steady Hand applies to every modifier of the new set.
- **Smithing XP (Skyy's lock, item 4):** what pays today is reforge only (`xp.reforge.<rarity>` rows 5/10/20/40/80/160/40 for normal to set: defaults G:638, file lines G:2034, read by `xpReforge` G:4304, paid at G:7259-7267 only when the reforge was not free). Identify says "No Smithing XP (none is designed)" (G:10126 comment) and crafting pays nothing (G:5900). SkyyGear pays the new XP through `skill:fn:addxp` (sources `gear:craft` / `gear:identify`), the same call reforge uses, only after the change succeeded. New placeholder rows (tables like `xp.reforge`): `xp.craft.<rarity>` = 50/100/200/400/800/1600 and `xp.identify.<rarity>` = 25/50/100/200/400/800. Admin and free actions pay nothing. Loop check: salvage returns ore at a median 0.25-0.3 bars per bar spent (`research/Smithing-Smelting-Spec.md` 2.4), so craft, salvage, smelt, craft loses most of its material every turn. The one exception that spec found is `Tool_Sickle_Copper` (1 copper bar + 2 trunks; salvage returns 1 ore + fibre), a tool. `research/Loot-Unid-Spec.md` 2.4 (the parallel 0.2.3 spec) also pays craft XP for tools while 0.2.2 rolls them a rarity (`tool.craftRolls`), which would make that sickle a loop worth about 55 XP per turn for 2 trunks. So craft XP gets an exclude list (`xp.craft.exclude`, default `Tool_Sickle_Copper`), or tools are left out.
- **Limits:** Quick Forge and Fuel Saver only work in the per-player /craft Furnace, because the placed Furnace is shared. `unitMs` (K:1945) is static and takes the player's value where the job is queued; `ProcBench.burnOne` (K:2094) has no UUID, so the bench needs a per-run value set when a job is queued. Smelter's Luck works in both Furnaces. UNVERIFIED: that Furnace output slots refuse put-back items (the placed-Furnace extra bar rolls on take-out only).
- **Pace (numbers):** an iron bar pays 8 XP. Smithing 10 = 9,925 XP and Smithing 20 = 522,425 XP (the shared curve). With the default craft odds (60 / 25 / 10 / 4 / 1 / 0, OPEN-QUESTIONS l.126-127) a craft pays 99 XP on average, so Smithing 10 is about 100 crafts and **Smithing 20 about 5,300 crafts**; smelting alone needs about 1,241 iron bars for 10 and 29,000 thorium bars for 20 (`Smithing-Smelting-Spec` 2.2). Alchemy has no such gap (one Greater potion pays 18,000 XP). That is why the two roll nodes moved into tier II; Appraiser (tier III, Smithing 20) and tiers IV-VI (S8-S12) stay long goals. The levers are Server Setup rows: `xp.craft.*`, `xp.identify.*`, `xp.reforge.*` (x10 puts Smithing 20 near 500 crafts, but Smithing XP also feeds the 0.5%-per-level craft rarity chance, so faster levels mean better rarity sooner). Dust and tiers are separate: Dust (the 5 XP per Dust rate of question 6) only levels owned nodes faster, the tier gate is the skill level.

## 4. Code changes for the two template trees (SkyyTrees)

- **Trees:** `TREES += ["Alchemy", "Smithing"]` gives nodes 72-95 (T:703; `TCOLOR` T:704 needs two more colours; the tree list is append-only). Only T:845 hard-codes 72 (`assert len(ROWS) == 72 and ... == 72` becomes 96); T:1291-1292 are `len(TREES)` / `len(ROWS)`, and the per-tree arrays (T:1883, 1886), the saved-file loop (T:2043) and `postTree` follow by themselves. The T:4172 assert (`len(_exact) == 19 and len(CFG_ROWS) == 20 + len(TREES)`) is rewritten for 26 exact rows and 41 in all (section 13). Node ids must stay unique across all trees (T:845): none of the 24 new ids collides, and none has an underscore, a comma or a colon (T:840).
- **Tabs:** with 8 template trees the tab row stops fitting: `TR_LVL_W` (T:3695) = 1406 - 8 x 172 - 7 x 5 = -5, and the build asserts it is at least 240 (T:3801). Section 10's two rows replace it.
- **Kinds:** `KINDS += ["MANA", "ALCH", "SMITH"]` = 24-26; old numbers stay frozen (T:716-726). MANA = `skyytree_mana`. ALCH and SMITH are "read" kinds like COOK: SkyyTrees stores and shows them, and other mods read them through `tree:fn:bonus`. Wisdom uses XP; Forge Hardened uses HP.
- **Effects:** `TreeFx.bonusMap` is hard-coded per node id (T:2448-2458): add `xp.alchemy` = `v[I_PWISDOM]` and `xp.smithing` = `v[I_SWISDOM]`. `TreeFx.stats` (T:2574) adds SHealth to Health, and PMana plus class Mana to `skyytree_mana`. `tree:names` (`NAMES_CSV`, T:1294) gains `Alchemy,Smithing,Class`.
- **Config:** Dust defaults in 0.3: Mining 5 (locked), Acrobatics 2, Exploration 5, Smithing 5 only if question 6 says yes, Alchemy the global 10. `DUST_DEF` (T:711) gets the entries (code default), and the `dust.perTree` help text ("Removed: Acrobatics 2, Exploration 5 ...") follows. New config lines are appended once with the ADD02 pattern (T:1188-1199; a `has03` check like `TreeCfg.has02`, T:1629): the node lines of the two new trees and, only when the file has no such line, `dust.xpPerDust.Mining=5` (and `.Smithing=5`) so Server Setup lists them; a hand-set value is kept.
- **Icons:** the both-versions fix ships in 0.3 (`Glider` becomes `Template_Glider`, T:813, 822; Audit 7 item 10; `Template_Glider` and its generated icon PNG exist in both Assets.zip, checked 2026-10-02). `must()` (T:666) reads only the 0.6.8 Assets.zip today (`ASSETS`, T:663); 0.3 adds the 0.7 pre-release one, when installed (read-only). All 24 new tree icons and the class-tree icons of section 6 exist in both.

## 5. Class trees: the rules

- **Scope:** one tree per class, per profile (a profile is one class), following `class:<uuid>` (a profile's file keeps a separate `Class.<Class>` line per class, so an admin class change never mixes trees). With no class, the tab says "Choose a class with /class" (the words `/skills` already shows, S:10665; with SkyyProfiles the class is picked when the profile is created and `/class` is read-only, SkyyClasses 0.1.10 l.87-106, so the page may add "or create a profile").
- **Supersedes (the main session records these):** Skyy's "wynncraft" request replaces the older class-tree notes: "Borderlands-style, research Borderlands 4, do not design yet" (SkyyGear-Plan l.96 and l.308, SkyWynn-Decisions l.85) and the open rows 6.2 / 6.3 (1-2 archetypes first, about 25 nodes). It also reverses "Class Level (1.5) stays separate" (Decisions 2.5, SkyyClasses-Plan l.38: a separate Class Level that spends into the ability tree, never built): AP now come from the class skill (question 1).
- **AP:** AP = (level >= 1 ? min(`class.ap.max`, `class.ap.first` + floor(level / `class.ap.every`)) : 0) + `class.debug.extraAp`, which is 1 + floor(L / 2) capped at 50 (so 0 AP at level 0, exactly like Tokens, T:2301-2305: ROOT opens with the first 50 class XP). `level` = `skill:fn:level(uuid, "<Class>")`. AP is computed and never stored. Spent AP = the costs of the nodes you own. The admin rows `levels.class.max` and `levels.class.sameAsOthers` (S:2866-2871) move AP with them (class max 60 gives at most 31 AP), and a lower result makes the balance negative (section 9).

| Class skill | 1 | 10 | 20 | 30 | 40 | 52 | 60 | 80 | 100 |
|---|---|---|---|---|---|---|---|---|---|
| Fighting hours to reach it (`research/cloud/Class-Skill-Curve-Proposal.md`, today's kill XP; UNVERIFIED pace) | 0 | 0.6 | 4 | 8 | 17 | 31 | 41 | 93 | 200 |
| AP | 1 | 6 | 11 | 16 | 21 | 27 | 31 | 41 | 50 |

(The hours row is the proposal's "today's kill XP" column, checked against its per-level table; its "with SkyyMobs level bonus" column gives 2.9 h / 8.8 h / 13.8 h / 69 h at skill 20 / 40 / 52 / 100, and SkyyMobs 0.1 is live, so the real pace lies between the two. The AP row was recomputed: 1 + floor(L / 2), capped at 50, which is reached at skill 98.)

- **Size:** the tree costs **64 AP**, and **27 AP works today** (21 for an Archer if the crossbow nodes stay "coming"). At 0.7 a level-100 player has 50 AP (78%): the spine (6 AP) + all four ability lines (16) + two full lanes (28), or fewer ability lines and a start on the third lane. Each lane to its element and capstone costs 14 AP, so one whole lane is never reachable at the default cap: that is the build choice.
- **Unlock rule** (the server re-checks every point on each click). A node can be unlocked when:
  1. it is the root, or a parent is owned;
  2. all of its Needs are owned (a modifier needs its ability);
  3. none of its Locks is owned (the pick-one pair);
  4. its lane count is met ("lane n" = at least n owned nodes of that lane; the parent chain already forces it for the cores, elements and capstones, the field is there for Wynn-style meshes later);
  5. the class skill meets its Min level (the `class.minLevel` table, today only the Archer crossbow nodes);
  6. there is enough AP;
  7. it is not a "coming" slot.
- **Integrity:** spent AP and effects count only owned nodes whose chain is intact (the root or an owned parent, every Need owned, no Lock owned, node switched on). A hand-edited file, a node an admin switched off or a changed map therefore refunds itself instead of leaving orphans, and the page shows such a node as Locked.
- **Single buy, Wynn style:** a node is owned or not. No levels, no Dust, no toggles.
- **Wynn for comparison** (`wynncraft.wiki.gg/wiki/Ability_Tree`, fetched 2026-10-02, VERIFIED): "70+ total upgrades for each class", nodes cost 1 or 2 AP, "a maximum of 50 points at Combat Level 120", resetting or editing costs 3 Ability Shards, right-click undoes recent picks until the menu closes, 3 archetypes per class. The research brief's finer counts (88-97 nodes in `api.wynncraft.com/v3/ability/tree/<class>`, about 86% of nodes touching spells, exclusive pairs) are UNVERIFIED: a re-fetch of the Archer API was summarised as 67 nodes on 5 pages (38 at 1 AP, 29 at 2 AP). We copy the rules and shape at roughly half the size (37 nodes), with 1-4 AP because our capstones are bigger than Wynn's 2 AP top nodes; the spell part waits for runes.

## 6. The class tree template (one map for every class)

Each page is 9 columns x 6 rows; there are 2 pages. `--` and `|` are straight bars between cells and `+` is a corner or junction cell with no node. Every link is drawn as axis-aligned bars from node centre to node centre, and a link whose two ends differ in both row and column goes through a `+`: the map never needs a diagonal, which the UI cannot draw. Nodes next to each other are linked only when the table says so. P3 and P4 are linked across the page break: no bar is drawn there (page 1 has 4 px spare under row 6), and the detail panel of P3 and P4 says "continues on page 2" / "continues on page 1".

```
 page 1 (core)                                        page 2 (lanes)
      c1   c2   c3   c4   c5   c6   c7   c8   c9          c1   c2   c3   c4   c5   c6   c7   c8   c9
 r1   .    .    .    .   ROOT  .    .    .    .      r7   .    +    --   --   P4   --   --   +    .
 r2  M1B  M1A   A1   --   P1   --   A2  M2A  M2B     r8   .    L1   .    .    C1   .    .    R1   .
 r3   .    .    .    .    |    .    .    .    .      r9   .    L2   .    .    C2   .    .    R2   .
 r4  M3B  M3A   A3   --   P2   --   A4  M4A  M4B     r10  LE   L3   .    .    C3   CE   .    R3   RE
 r5   .    .    .    X1   +    X2   .    .    .      r11  .    L4   .    .    C4   .    .    R4   .
 r6   .    .    .    +    P3   +    .    .    .      r12  .    LS   .    .    CS   .    .    RS   .
```

The pick-one pair is a diamond: P2 goes down to the `+` in r5 and sideways to X1 and X2, and X1 and X2 each go down to the `+` in r6 and sideways into P3, so P3 is reached through the pair and never straight from P2 (the draft drew a straight stub from the r5 junction to P3, which read as "P3 hangs off P2"). **Draw order:** all grey bars first, then all gold bars (both ends owned), then the cells, so a shared stub is gold when any link through it is owned. **Bars:** 21 on page 1 and 20 on page 2 (reserve `#SkyyTrSeg1-24`).

**Units:** H = +4 Health, S = +2 Strength, M = +5 Mana, R = +5% Mana Regen. Every amount is the `Amount` cell of its node in the `class.nodes.<Class>` table (section 13). **Physical classes:** Archer, Warrior, Berserker. **Magic classes:** Mage, Priest. Mana on a physical class is idle until the abilities (0.7), when every class casts with Mana (Class-Abilities-Draft section 1); it is kept so the tree does not change shape at 0.7.

| Id | Type | AP | Parents (any one) | Needs / Locks / Lane | Physical | Magic |
|---|---|---|---|---|---|---|
| ROOT | passive | 1 | - | - | 1 H | 1 H |
| P1 | passive | 1 | ROOT | | 1 S | 1 M |
| P2 | passive | 1 | P1 | | 1 H | 1 R |
| X1 | passive, pick one | 1 | P2 | locks X2 | +3 Strength | +8 Mana |
| X2 | passive, pick one | 1 | P2 | locks X1 | 2 H | 2 H |
| P3 | passive | 1 | X1, X2 | | 1 M | 1 H |
| P4 | passive | 1 | P3 | | 1 S | 1 R |
| A1, A2 / A3, A4 | ability slot (runes) | 1 | P1 / P2 | coming | - | - |
| M1A-M4A | modifier slot (runes) | 1 | its ability | needs its ability; coming | - | - |
| M1B-M4B | modifier slot (runes) | 2 | the M_A of that ability | needs its ability; coming | - | - |
| L1, C1, R1 | lane entry | 1 | P4 | | 1 unit of the lane stat | same |
| L2, C2, R2 | lane | 1 | L1 / C1 / R1 | | 1 unit | |
| L3, C3, R3 | lane | 2 | L2 / C2 / R2 | | 2 units | |
| L4, C4, R4 | lane core | 3 | L3 / C3 / R3 | lane 3 | 3 units | |
| LE, CE, RE | element (later) | 3 | L3 / C3 / R3 | lane 3; coming | element stat (section 7) | |
| LS, CS, RS | capstone ability (runes; S = summit) | 4 | L4 / C4 / R4 | lane 4; coming | - | |

**Totals:** 37 nodes, 64 AP (the pick-one pair counts once; one lane to its element and capstone is 1 + 1 + 2 + 3 + 3 + 4 = 14). **Live now:** ROOT, P1-P4, X1 or X2, L1-L4, C1-C4, R1-R4 = 27 AP.

**Icons** (item ids, all present in both Assets.zip, checked 2026-10-02). The "coming" cells use `Deco_Scroll`, the icon of the Exploration "Coming later" slots, because the rune items exist only in 0.7 (`Rune_*` and `Ingredient_Rune_Shard` are missing from the 0.6.8 Assets.zip).

| Node | Icon |
|---|---|
| ROOT | the class icon (`CLASS_ROWS`, S:2726): Archer `Weapon_Shortbow_Iron`, Warrior `Weapon_Sword_Iron`, Mage `Weapon_Staff_Iron`, Berserker `Weapon_Battleaxe_Iron`, Priest `Weapon_Wand_Wood` |
| H, S, M, R units | `Plant_Fruit_Apple`, `Weapon_Sword_Iron`, `Potion_Mana`, `Potion_Regen_Mana` |
| Archer R2, R3 (Bolt Rack) and R4 (Holstered Reload) | `Weapon_Crossbow_Iron` and `Weapon_Arrow_Crude` |
| A1-A4, M1A-M4B, LS / CS / RS (coming with runes) | `Deco_Scroll` (the real rune icon from 0.7) |
| LE / CE / RE (coming later) | `Rock_Gem_Ruby` |

## 7. Classes, archetypes and who applies each stat

| Class (skill) | Type | Left lane (direction. stat. element) | Centre lane | Right lane |
|---|---|---|---|---|
| Archer (Archery) | physical | **Boltslinger**: rapid volleys, close burst. S. Elemental Damage % | **Trapper**: traps, slows, control. H. Raw Spell Damage | **Sharpshooter**: long range, crossbows. R1 S; R2-R4 crossbow nodes. Elemental Damage % |
| Warrior (Swordsmanship) | physical | **Fallen**: risk for damage. S. Elemental Damage % | **Battle Monk**: fast combos, mobility. S, S, H, H. Raw Spell Damage | **Paladin**: tank, protect allies. H. Elemental Defence |
| Mage (Sorcery) | magic | **Riftwalker**: teleports, chained spells. R. Raw Spell Damage | **Light Bender**: light, heals, support. H. Elemental Defence | **Arcanist**: big bursts, deep Mana. M. Elemental Damage % |
| Berserker (Fury) | physical | **Bloodbound**: tougher and stronger when hurt. H. Elemental Defence | **Smasher**: heavy slams, stuns. S. Elemental Damage % | **Warbringer**: war cries for the party. S, S, H, H. Raw Spell Damage |
| Priest (Divinity) | magic | **Smiter**: holy damage that heals. M. Elemental Damage % | **Healer**: big group heals. R. Raw Spell Damage | **Guardian**: shields, protection. H. Elemental Defence |

- **Names:** Archer, Warrior and Mage use Wynn's names, but not Wynn's lane order (UNVERIFIED). Berserker and Priest come from `research/cloud/Class-Abilities-Draft.md` sections 5-6. Assassin (Shadestepper / Acrobat / Trickster) and Shaman (Summoner / Acolyte / Ritualist) fit the same map later.
- **Archer crossbow nodes** (approved 2026-09-25; OPEN-QUESTIONS section "Crossbows stay loaded", the two APPROVED lines, l.484-485 at 22:57 on 2026-10-02 (the file grows, so line numbers into it drift); `research/Crossbow-Loaded-Spec.md` 6.1):
  - R2 **Bolt Rack I**: +2 bolts, needs Archery 15.
  - R3 **Bolt Rack II**: +2 more, which is the approved +4 cap.
  - R4 **Holstered Reload** (core, Archery 50): a hotbar crossbow reloads in 30 s.
  - The next SkyySkills applies them (`tree:fn:bonus` "Class.Archer.R2/R3/R4" answers the node's `Amount`: 2, 2 and 30).
  - UNVERIFIED: whether a per-player Ammo MAX modifier lifts the 6-bolt cap (vanilla's `Ammo.json` max is 0 and the crossbow adds +6 only while held, Crossbow-Loaded-Spec 1.1), and whether vanilla reloads past 6. Two more 6s sit in our own code: the loaded-crossbow perk clamps what it remembers at 6 (S:7640 `if (k > 6) k = 6`) and vanilla's SwapFrom refund ladder has exactly 6 steps (Crossbow-Loaded-Spec 1.3). Bolt Rack means changing the clamp too. If the check fails, R2-R4 stay "coming" and the Archer's live total is 21 AP.
  - Timing: the locks were written against the old XP table. With the flat class curve Archery 15 is about 2 hours (and AP puts R3 at about Archery 18), so "level 15+" is early now: question 7.
- **Full live totals (with X1):** Warrior and Berserker: +25 Strength, +56 Health, +5 Mana. Archer: +23 Strength, +36 Health, +5 Mana, plus the crossbow perks (its right lane has one stat node). Mage and Priest: +48 Mana, +45% Mana Regen, +36 Health. Balance note: 1 Strength = +1% physical damage (section 1) on top of the class perk's +0.2% per class level, so tune the S unit first.

| Live stat | Applied by | How | Status |
|---|---|---|---|
| Health | SkyyTrees | `skyytree_health` (T:2574-2585) | live code |
| Mana | SkyyTrees | new `skyytree_mana`, the same `mod()` call on `DefaultEntityStatTypes.getMana()` | proven pattern |
| Strength | SkyyGear | SkyyTrees posts "str:N" (source `trees`) into a new map `gear:extras:<uuid>` (ConcurrentHashMap source -> String). SkyyGear adds it next to `gear:extra` in `GearStats.extra` (G:6544-6581) and in the `/gear` "From other mods" line (G:10964). Until then the node shows "needs SkyyGear" | needs the next SkyyGear |
| Mana Regen % | SkyySkills 0.4.12 | `skill:fn:manaregen` {"add", uuid, "trees", pct}. Setting 0 removes it; it is re-added after a profile switch. `/skills mana` lists it as `trees=+5` | live |
| Crossbow nodes | SkyySkills | `tree:fn:bonus` | needs SkyySkills; engine UNVERIFIED |

## 8. Ability slots: what they become with 0.7

| Tree slot | Rune shape at 0.7 (Runes 2.1-2.4) | Today |
|---|---|---|
| A1-A4 | Ability runestone: Slot Primary, `Weapons` = the class weapon families, tag `class.<name>`. Cast with Use Ability 2 / 3 | "Coming with runes" |
| M1A-M4B | Modifier runestone: Slot Support, `AppliesTo` = that one ability's private tag (for example `class.archer.arrowstorm`, so it fits no other ability); its `AttributeModifiers` change the ability's named numbers (Damage, AoeScale, Duration, Cost, Cooldown, Fork, Ricochet ...; those are attribute names, not tags) | "Coming with runes" |
| LS / CS / RS | Archetype capstone ability rune, slotted like any ability (Hytale has no ultimate key). Hytale's own "Signature" is the weapon's Ability 1 meter (and there are Signature potions), so the name is ours | "Coming with runes" |
| LE / CE / RE | Elemental Damage %, Elemental Defence or Raw Spell Damage (needs SkyyGear elements) | "Coming later" |

- **The bench:** you equip any 2 unlocked abilities, each with up to 2 matching modifiers. The client fixes this at 2 lines of 1 + 2 slots. With 4 + 3 abilities to choose from, which 2 you pick is a real build choice.
- **Recommended:** the tree *permits* runes and does not hand out items, so a respec never takes items back.
- **Left for the rune round:**
  - how class runes are obtained;
  - the slot guard (send runes back to the bag on InventoryChangeEvent, or cancel the cast on InteractionChainStartEvent; Runes 3);
  - whether vanilla runes stay;
  - capstone abilities have no modifier nodes in this map, so on the bench their 2 modifier slots would only take modifiers whose `AppliesTo` matches (vanilla ones, if vanilla runes stay): add modifier nodes for them in the "grow at 0.7" round, or accept capstones without modifiers;
  - the one-time free class respec on flip day (section 9).
- **Icons at 0.7:** the rune strip and the tree cells show a rune by `ItemIcon { ItemId }` only, never an item grid slot holding the real stack (client disconnect with metadata stacks, AGENT-BRIEF UI rules).
- **Until then:** "coming" slots cannot be bought and never count for AP, lanes or effects. Nothing references a rune class, because the builds compile against 0.6.8 (`tools/skyybuild.py`; `Rune_*`, `Ingredient_Rune_Shard` and `Bench_Abilities` exist only in the 0.7 Assets.zip, and the `InventoryComponent$AbilitySlots` classes only in the 0.7 jar, so even the SkyyProfiles snapshot of sections -11 / -12 can only be built on 0.7). **Before any player gets runes, SkyyProfiles must save sections -11 / -12** (Runes 4.4).

## 9. Respec

- **Alchemy and Smithing:** unchanged (Spec1 8.1; T:3603-3630).
- **Class tree:** click Respec twice within 10 s; every node resets and all AP comes back.
  - Cooldown: `respec.cooldownMinutes` (10).
  - Price: `class.respec.coins` (0).
  - A negative balance blocks buying but keeps effects, and makes respec free and immediate.
- **Undo** (row `class.undo`, Wynn's right-click undo): while the page is open, Undo refunds the newest unlock if nothing you own still needs it. The list clears when the page closes or after a respec.
- **Flip day:** when the "coming" slots go live (rune round step 5) a player who spent all 27 AP on passives has no AP for them. Do what the swing-speed change did (OPEN-QUESTIONS l.476, "one-time chat notice ... plus a free respec"): a one-time chat notice and a free class respec (cooldown cleared), once per profile, marked in the player file.
- Wynn charges 3 Ability Shards for a reset (`wynncraft.wiki.gg/wiki/Ability_Tree`); our default is free (question 4).

## 10. The /tree page (vanilla kit, fits 1080)

- **Window:** 1440 x 941. This is 0.2.5's 1440 x 892 (T:3692-3694: 38 title + 2 x 17 padding + 820 of parts) plus one 49 px tab row (a 44 px button row, `SUI.BTN_H`, + the 5 px tab gap); the kit cap is 1600 x 980 (`MAX_PAGE_W` / `MAX_PAGE_H`, skyyui.py:297-298), so 941 fits. The window is the same for every tab of /tree.
- **Tabs:** nine 172 px tabs cannot fit one 1406 px row (T:3668, 3695: 9 x 172 + 8 x 5 = 1588; even 8 tabs need 1411), so there are two rows of vanilla EntitySpawnPage tabs.
  - Row 1: MINING FORAGING FARMING COOKING ALCHEMY SMITHING (6 x 172 + 5 x 5 = 1057), plus the level label in the 349 px that are left.
  - Row 2: ACROBATICS EXPLORATION and the class tab, labelled with the class name in capitals (ARCHER, BERSERKER = 101 px of the 124 px a tab has; CLASS when the profile has none).
  - Ids stay `#SkyyTrTab<tree index>` (Alchemy 6, Smithing 7, class 8); the left margin restarts at the first tab of each row.
  - Fallback: a dropdown. It worked in Skyy's probe (HANDOFF:549) but is not in `skyyui.PROBED`.
- **Template trees** keep the 0.2.5 layout (Alchemy and Smithing use the same tier rows, cells and detail well; their node names all fit the 168 px cell text, widest "Smithing Wisdom" 153 px at 18 px bold, measured with the kit font table).

```
+-- list well 950 x 608 (inner 942 x 600) ------------------------------------+  +-- detail well 440 x 608 --+
| RUNE SLOTS - coming with 0.7  [A][m][m] [A][m][m]       [<] Page 1 of 2 [>] |  | icon  Name                |
| 9 x 6 grid: node cells 100 x 84 (48 px item icon + one state line)          |  | state line (colour)       |
| connector bars 6 px between cell centres (grey; gold when both ends owned), |  | TYPE: Passive - Trapper   |
| drawn first; node cells on top                                              |  | EFFECT / COST / NEEDS     |
|                                                                             |  | HOW IT WORKS (who applies)|
|                                                                             |  | [Unlock]  [Undo]          |
+-----------------------------------------------------------------------------+  +---------------------------+
```

- **Info row** (the same three fields as the template page, T:3696-3697): "Ability Points 6 of 12" (gold, bold, in the 230 px Dust field: the widest, "Ability Points 50 of 50", is 192 px at 18 px bold) | "Archery 23" (the 190 px Tokens field: "Swordsmanship 100" is 174 px) | "Boltslinger 2 - Trapper 0 - Sharpshooter 1" in the note field (287 px of 986). "6 of 12" = AP free of AP earned, like "Tokens N of M".
- **Rune strip** (64 px high inside the well): Line 1 = Use Ability 2, Line 2 = Use Ability 3. Today it shows disabled cells. At 0.7 it shows the slotted icons plus a RUNES button that opens the bench (Runes 3). Width budget: label "RUNE SLOTS - COMING WITH 0.7" 245 px at 15 px bold + 24 + two lines of [A 56][m 44][m 44] with 4 px gaps (152 each, 24 between) + 24 + pager [<] 44, "Page 1 of 2" 92, [>] 44 with 8 px gaps = 817 of 942. Use fixed Anchor margins, not LayoutMode Right.
- **Sizes:** height 64 + 8 + 6 x 84 + 5 x 4 = 596 of 600. Width 9 x 100 + 8 x 4 = 932 of 942. A cell is 6 px top, the 48 px icon, 4 px, one 15 px line (about 21 px), 5 px = 84.
- **Cell states** (the state line is the only text in a cell and must stay under about 92 px at 15 px; the detail well gives the full reason): Locked grey = "Locked", "Needs A1", "Need 3 AP", "Archery 15" or "Pick one" (X2 while X1 is owned); Unlockable green = "Unlock 2 AP" (84 px; "Unlock - 4 AP" is 95 px and does not fit); Owned blue = "Owned"; Coming = the kit's disabled cell with "Coming". The selected cell uses the vanilla selected row. A gold bar means both ends are owned.
- **Events:** `trtab0-7` as today, `trtab8` (the class tab), `trpgp` / `trpgn`, `trc1`-`trc37`, `trbuy`, `trundo`, `trrespec`, `trback`. The class page keeps its selection and page in the page object (nothing is stored), and a page switch moves the selection to the first node of that page.
- **Element ids:** `#SkyyTrC<n>`, `#SkyyTrSeg<k>`, `#SkyyTrRs1-6` and `#SkyyTrPgP/N/L`. No underscores; none collides with the 0.2.5 ids (`TR_OLD_IDS`, T:3701). Keep the trailing-quote match (`trc1` vs `trc10`).
- **New kit pieces:** a graph cell, a connector bar, and absolutely anchored children in a Group (added to the kit's `UNVERIFIED` trial list with new keys; `PROBED` is empty today, skyyui.py:486). They go into `tools/skyyui.py`, `skyyui_test.py` and the guide, as trial until Skyy has seen a probe page. A trial feature stays off in a shipped page, so the class page itself ships only after Skyy has opened the probe (Alchemy and Smithing do not wait for it).
- UNVERIFIED, the probe page checks these four: (1) a 6 px Group with a colour Background renders as a bar and bars added before the cells show under them (child order = draw order); (2) a click on a cell is not taken by a bar under it; (3) clicks through the kit's disabled cell (the 0.2.5 Exploration "Coming later" cells are bound Buttons with a cover, T:52-55: if that fails the fallback is `TR_DRAFT_CELL = "normal"`, T:3680); (4) the look of the two tab rows. Absolute Anchor Left / Top for children inside a Button is already proven by the live node cells (ItemIcon and Labels).

## 11. 0.7: wait for the release (LOCKED 2026-10-02), and the release-day fix list

**Why wait:**
- Only the passives (27 of 64 AP) are rune-free.
- On pre.4, new islands come out empty, Menu Spawn and the Profiles fallback break, and the kit check stops 15 UI builds.
- Runes are still `[TMP]` in the lang file, with `_Debug` runes and Developer-quality modifiers (Runes 2.5 and 4.6), and nothing has run on 0.7 in game (Audit 9).

**The fix list** is Audit section 7. Line numbers will shift.

| # | Mod / file | Fix | When |
|---|---|---|---|
| 1 | SkyyIslands 0.5.6 | `FillTask.put` l.2785: 8-arg `setBlock`. `RelightNow` l.2841: `invalidateLoadedChunks()`. `sendToHub` l.2891: `getSpawnPoints()` stopgap, later `SpawnUtil.teleportToSpawn` | both versions now; SpawnUtil on 0.7 |
| 2 | SkyyMenu 0.3.6 | `doSpawn` l.3984 (as 1); probe l.1770; icon `Furniture_Ancient_Chest_Large_Treasure` -> `Furniture_Ancient_Chest_Large` (l.226, 479) | both versions now |
| 3 | `tools/skyyui.py` l.2612 | Anchor the close-X check on the text before `@PageOverlay`, run `skyyui_test.py`, bump KIT_VERSION. Otherwise 15 UI builds stop | both versions now |
| 4 | SkyySkills | Spell-cost generator: 0.7 shapes (l.2039, 2257, 2365/2481, 2439, 2490-2491). **Skyy decides** rune Mana costs and Base Mana (vanilla is 100) | release day |
| 5 | SkyyCooking | EXPECT table l.475-482 (buffs 360 s, bread heals Percent 10); balance look | release day |
| 6 | SkyyGear | Level rules for `Weapon_Bangstick` and `Weapon_Longsword_Ruined_Giant` (+ NPC variants); stackable rule l.797; CHG_FAMILIES l.1665-1668 | release day |
| 7 | SkyyCollections | Counts 20 / 34 (l.249, 267); Sadwillow log collection and reward row | release day |
| 8 | SkyyClasses | `Flamethrower_` -> `Weapon_Flamethrower_` (l.278); decide the Bangstick's owner | release day |
| 9 | SkyyExploration | `Objective_Treasure_Map` -> `Deco_Treasure` (l.597); 9 portal chest lists (l.548, 560) and their XP | icon now; lists on release day |
| 10 | SkyyTrees | `Template_Glider` (**in 0.3**); `Trigger_Explosion_State_Generic` in `Skyy_Tree_Chop.json` | icon now; trigger on release day |
| 11 | SkyyMobs | `Spectre_Void` -> `Void_Spectre` (l.290-292); review the 37 new auto-levelled roles | release day |
| 12 | SkyyProfiles | `travel` l.2213 (as 1); test the async `PlayerConnectEvent`; **add sections -11 / -12 before any rune** | now / 0.7 |
| - | Housekeeping | Saplings From Trees update; SkyyUiProbe probe 24; a permanent `tools/dev/linkcheck.py` | any time |

**Ship early:** the both-versions fixes (rows 1-3, the icon swaps, the Profiles fallback). Release day then holds only the data fixes and the rune round.

**Rune round order** (Runes 4.5):
1. Throwaway-world probe (`kit abilities`, `/abilities`).
2. Skyy's Mana and vanilla-rune calls.
3. SkyyProfiles sections -11 / -12.
4. Class runes.
5. Flip the "coming" slots live, with the one-time free class respec and chat notice (section 9).

## 12. Other mods that read the new nodes (same round as SkyyTrees 0.3)

| Mod (next version) | Change | Reads |
|---|---|---|
| SkyySkills (the next free version after 0.4.13 and the queued roll-landing / x3 gathering boost / Mana-while-charging / kill-XP gap rule build; may bundle with it) | (a) TREE buttons: `treeName()` (S:5755) adds alchemy and smithing; for the five class slots it answers `class`, and `treeAvailable()` (S:5767) needs its own class branch (today it compares the `tree:names` entries with the slot's label, "Archery", and would never see "Class"). The `/skills` row (S:10679) and the Stats page (S:10977) already call them. (b) `Brew` reads PExtra, PDur(2), PFrugal, PHealth / PSig / PStam / PSeed, PDouble, PMaster. (c) `SmeltSys` extra bar. (d) Archer crossbow nodes (and the `Xbow` 6-bolt clamp, S:7640). (e) `xpSkills` += Alchemy, Smithing and `addxpSkills` += Smithing (S:1286-1287, rows S:11149-11151), as a one-time migration of untouched default lines (PROJECT-RULES 4: History snapshot first, a marker, hand-set lists kept and logged, line endings kept) | `tree:fn:bonus` |
| SkyyGear (see the planning call below) | (a) `gear:extras:<uuid>` input. (b) `smithChance` + SRarity(2). (c) `rollMods` best-of-two (SIdent, SReforge) + SMaster. (d) SAppraise in `identify`. (e) SHaggle at all 7 cost sites. (f) `xp.craft` / `xp.identify` rows | `tree:fn:bonus`, `gear:extras` |
| SkyySacks (0.7.13 is queued for the Accessory Table and the Memories check; the readers can ride on it or on the next) | /craft Furnace: SQuick (`unitMs` when queued), SFuel (`burnOne`, needs a per-run value on the bench), SSmelt (an extra bar per unit) | `tree:fn:bonus` |

**SkyyGear planning call.** SkyyGear has no patch scripts: every version is a full copy of the last (0.2.1 header), so the readers can only go into the next free version. The queue is 0.2.1 (stages 2-3, running), 0.2.2 tool levels (`research/Tool-Levels-Spec.md`), 0.2.3 loot round (`research/Loot-Unid-Spec.md`, OPEN-QUESTIONS l.174-189), and the locks disagree about where the tree readers go: l.181 says 0.2.2 reads the tree bonuses at craft / identify / reforge, l.188 puts the identify-rarity hook in 0.2.3. 0.2.3 rewrites identify (mystery items), and 0.2.2 touches craft and reforge for tools, so putting the readers in 0.2.2 and again in 0.2.3 edits the same functions twice. The loot spec (written in parallel, its section 6) already carries all the Smithing readers in 0.2.3, by node id (`Smithing.SRarity` ... `Smithing.SMaster`), so the slot reorder of section 3 changes only its S-number labels, not its code. Its scope says `gear:extras:<uuid>` (tree Strength) is "a separate SkyyGear item of the trees round": nothing in the queue carries it yet, so either add it to 0.2.3 (a small merge in `GearStats.extra`) or the class Strength nodes show "needs SkyyGear" until another SkyyGear build. SkyyTrees 0.3 does not wait for any of it: nodes can be bought and do nothing until their reader ships.

**Reading channel:** `tree:fn:bonus`, not the `skill:bonus` map that l.181 mentions: SkyyGear and SkyySacks have no `skill:bonus` reader, `tree:fn:*` is what SkyyCooking (l.1581, 1626) and SkyyExploration (l.3597) already read, and without SkyyTrees every reader gets 0, so nothing changes.

## 13. Server Setup rows, commands, bridge, storage, build stages

Today there are 26 rows: 19 settings, `dust.perTree` and 6 node tables (T:4172).

| Key | Name | Type, default | Notes |
|---|---|---|---|
| `nodes.Alchemy`, `nodes.Smithing` | Alchemy / Smithing tree nodes | key-family tables like the six existing ones (entry = node id + field: max, per, B, tokens, enabled; T:4165-4166 builds them from `TREES`, `NODE_HELP` T:4120) | automatic; `TreeKit.checkNode` |
| `dust.perTree` (existing) | Dust rate per tree | built-in defaults Mining 5 (locked), Smithing 5 (question 6), Acrobatics 2, Exploration 5; Alchemy follows `dust.xpPerDust` (10) | no new row; the row's help text changes |
| `class.enabled` | Class trees | switch, **off at the first deploy**, on once Skyy has opened the probe page and it worked (Server Setup, no build) | off = no class tab, no class effects, no TREE button on the class row |
| `class.ap.first` | AP at class skill 1 | int 0-10, 1 | live |
| `class.ap.every` | +1 AP every N class levels | int 1-20, 2 | live, danger |
| `class.ap.max` | AP cap | int 1-200, 50 | live, danger |
| `class.respec.coins` | Class respec price | coins, 0 | cooldown = `respec.cooldownMinutes` |
| `class.undo` | Undo while the page is open | switch, on | |
| `class.debug.extraAp` | Extra AP (testing) | int 0-1000, 0 | adv |
| `class.nodes.<Class>` x 5 | <Class> tree nodes | key-family table of 3 columns On, Amount, AP (`bool\|int\|int`, joined with `sep=,` in the file; the contract allows 2-3 column tables, CONFIG-CONTRACT l.109-114, so a 4th column "Min level" does not fit; at most 37 entries, the kit lists 500) | `ClassKit.checkNode`: Amount 0-1000, AP 0-10 |
| `class.minLevel` | Class level needed per node | key-family table, 1 int column 0-100 (entry `<Class>.<Id>`; defaults Archer.R2 15, Archer.R3 15, Archer.R4 50; no entry = no requirement) | `ClassKit.checkLevel` |

New total: 26 + 2 + 7 + 5 + 1 = **41 rows**; the T:4172 assert becomes 26 exact rows and 41 in all, and `CFG_CATS` (T:4119) gets a "Class trees" tab for the `class.*` rows.

- **Commands** (each usage variant gets `setPermissionGroups(new String[] {"hytale:Adventurer"})`): `/tree alchemy`, `/tree smithing`, `/tree class`, and `/tree <your class>`. Another class name answers "Your class is Archer". Never use `/abilities`, which is a vanilla 0.7 command (Audit 5; the other new 0.7 commands are beam, ephemeral, wilderness, height, position and two marker debug commands, so `/tree` is safe).
- **Bridge:** `tree:names` + Alchemy, Smithing, Class. `tree:fn:level` / `tree:fn:bonus` answer "Alchemy.PExtra", "Smithing.SIdent" and "Class.Archer.R2" (a new branch for the `Class.` prefix: `TreeDefs.idx`, T:1331, only knows the template ids). New: `gear:extras:<uuid>`. `skill:fn:manaregen` gets the source "trees". `tree:<uuid>` adds "Class:<owned>/<AP>" (`postTree`, T:2480, builds the string from `TREES`).
- **Storage** (`players/<pkey>.properties`, per profile):
  - `Alchemy.<Id>=n` and `Smithing.<Id>=n` (plus `<Tree>.off` and `.respecAt` like the others).
  - `Class.<Class>=ROOT,P1,X1` (owned ids). Unknown ids are ignored, so a removed node refunds itself.
  - `Class.<Class>.respecAt=<ms>`.
  - AP, Tokens and Dust stay computed; the file stays v=2.
  - **Rollback floor:** never return to 0.2.5 after 0.3 has saved. 0.2.5 rewrites the whole player file from memory and writes only the trees it knows (`TreeStore.snap`, T:2043-2064), so the new picks would drop. No currency is lost. Older SkyySkills / SkyyGear builds just ignore the new lines and rows (add the floor to `tools/deploy_set.py` when 0.3 deploys).
- **Build stages:**
  1. **Round A (full round).** SkyyTrees 0.3 (`tools/trees_0_3_patch.py` over the generated 0.2.5) plus the three reader bumps (section 12). One SkyyUiProbe page first (graph cell, bars, two tab rows). The class page is built on those trial features behind `class.enabled`, which ships off; Skyy turns it on in Server Setup once the probe worked. Alchemy and Smithing use only proven kit pieces and do not wait for the probe. Cross-check all SET jars (`-Xverify:all`), run the Adventurer audit and lint (0 fails), then deploy all four together. It touches coins (Haggler, craft / identify XP), saved data (new player-file lines), commands and four mods, so it is a full round (PROJECT-RULES 4).
  2. **0.7 release day.** Section 11, then the rune round: class runes as JSON (+ `Common/Icons/Abilities/<id>.png`), the "coming" slots go live, the slot guard, SkyyProfiles -11 / -12, the Mana scale, and the real rune strip.
  3. **Later.** Element nodes (once SkyyGear has Elemental Damage % / Defence), Assassin and Shaman tables, page 3 / meshes, and skill-upgrade points (Decisions 6.12, separate from AP).
- **First in-game checks:**
  1. TREE buttons show on /skills.
  2. Deep Reserves gives +1 Mana.
  3. Extra Brew (`debug.extraDust`) shows "Extra potion!".
  4. Steady Hand rolls lean high.
  5. Identify pays Smithing XP.
  6. AP = 1 + skill / 2.
  7. ROOT gives +4 Health.
  8. X1 greys out X2.
  9. Strength shows in /gear.
  10. Mage P2 shows "trees=+5" in /skills mana.
  11. Pager, Respec and Undo all work.
  12. A relog or profile switch keeps the picks.
  13. Mining Dust is Mining XP / 5 (the Dust line doubles; spent Dust stays spent).
  14. Smithing: Steady Hand and Keen Eye open at Smithing 10, Appraiser at 20; crafting and identifying gear show Smithing XP (admin and free actions pay nothing).
  15. With `class.enabled` off there is no class tab and no TREE button on the class row.

## 14. Questions for Skyy (recommended default in brackets)

1. **Ability Points:** taken from your class skill, 1 at skill 1, +1 every 2 levels, max 50 (reached at skill 98; 11 AP at skill 20, about 4 hours)? This replaces the older "separate Class Level that spends into the ability tree" (Decisions 1.5 and 2.5, SkyyClasses-Plan l.38), which was never built. **[yes]**
2. **Tree size:** 37 nodes / 64 AP on 2 pages for now (a level-100 player has 50 AP = 78%, so one lane stays out of reach), growing when runes come? Or nearer Wynn's 70+ nodes per class? **[37 now, grow at 0.7]**
3. **Ability shape:** 4 ability slots, each with its own 2 modifier slots, plus 1 capstone ability per lane (3 more), with any 2 equipped at the bench (Hytale's limit); the capstones get no modifier nodes yet? **[yes]**
4. **Class respec:** free with the 10-minute cooldown like every tree, plus Undo while the page is open (Wynn charges 3 Ability Shards, and the cloud draft suggested coins)? Or charge coins? **[free]**
5. **Mana Regen nodes:** only Mage and Priest (lock 23), or every class once runes cost Mana in 0.7? **[Mage + Priest now; ask again at 0.7]**
6. **Smithing pace:** pay Smithing XP for every gear craft and identify (new rows, 50-1600 and 25-800), give the Smithing tree the 5-XP-per-Dust rate (like Mining and Exploration), and accept that Smithing 20 is about 5,300 crafts away (the reforge and identify roll nodes open at Smithing 10)? Or raise the rows x10 now? **[yes, rows as written; tune them live in Server Setup]**
7. **Archer crossbow levels:** the locks say "Archery 15+" for the bigger magazine and "late game" for the holstered reload, but with the flat class curve Archery 15 is about 2 hours. Keep Bolt Rack I and II at Archery 15 and Holstered Reload at 50 as locked, or move the magazine nodes later (for example 15 and 30)? **[keep as locked]**

**Planning calls for the main session** (not Skyy's):
- **M1. Which SkyyGear build carries the Smithing readers and the Strength input?** The locks disagree (OPEN-QUESTIONS l.181 says 0.2.2, l.188 says 0.2.3); the loot spec already takes the Smithing readers into 0.2.3 but leaves `gear:extras` out. **[Smithing readers in the 0.2.3 loot build (which rewrites identify anyway), plus the small `gear:extras` merge there; SkyyTrees 0.3 does not wait for it]**
- **M2. One round or two?** One SkyyTrees 0.3 round with `class.enabled` shipped off until Skyy has opened the probe page, or split Alchemy and Smithing (0.3) from the class tree (0.4)? **[one round, class tab off until the probe worked]**
- Also record in OPEN-QUESTIONS (docs pass, not an agent task): Skyy's "wynncraft" class tree supersedes the Borderlands-style lock, and the 0.7 wait lock already covers the pre-release question.

## 15. UNVERIFIED and sources

**UNVERIFIED:**
- the look of the two tab rows, the 100 x 84 cells and the bars (the probe page checks them);
- absolute children in a Group (bars under cells, clicks not stolen);
- clicks through the disabled cell;
- the crossbow Ammo cap, our own 6-bolt clamp and vanilla's 6-step refund ladder, and the holstered reload;
- Furnace output slots refusing put-back items;
- Appraiser setting the doc's `r` key before `rollMods` (read from G:4741 and G:5931, not run);
- Alchemy pace with 60% extras, and the Smithing XP rows (5,300 crafts to Smithing 20);
- class pace hours (kill-rate guesses; SkyyMobs shortens them);
- Strength balance (1 Strength = +1% damage);
- all rune facts (0.7.0-pre.4 only, never seen in game);
- Wynn's lane order, and Wynn's node counts (wiki "70+", brief 88-97, API summary 67).

**Verified in the critic pass (2026-10-02):** every T / S / G / K / Cooking / Accessories line cited above was re-read; every Alchemy, Smithing and class-tree icon, the potion chain and the seed recipes were checked against both Assets.zip files (read-only); node names were measured with the kit font table; the AP table, the 64 / 27 AP totals and the class live totals were recomputed; the Wynn facts marked VERIFIED come from `wynncraft.wiki.gg/wiki/Ability_Tree`.

**Files read:**
- `tools/AGENT-BRIEF.md`; T, S, G (0.2 and the 0.2.1 header), K; `SkyyClasses/build_skyyclasses_0.1.10.py` (bridge keys, no-class text); `SkyyCooking/build_skyycooking_0.1.3.py`; `SkyyAccessories/build_skyyaccessories_0.5.2.py`.
- Spec1, Runes, Audit; `research/PreRelease-Compat-Report.md`; `research/Crossbow-Loaded-Spec.md`; `research/Smithing-Smelting-Spec.md`; `research/Alchemy-Skill-Spec.md`; `research/Gear-Levels-Wynn-Spec.md` (grep); the parallel `research/Loot-Unid-Spec.md` (SkyyGear 0.2.3) and `research/Tool-Levels-Spec.md` (0.2.2), read for overlaps with sections 3 and 12.
- `research/cloud/Class-Skill-Curve-Proposal.md`; `research/cloud/Class-Abilities-Draft.md`.
- `OPEN-QUESTIONS.md`; `SkyWynn-Decisions.md`; `SkyyGear-Plan.md` and `SkyyGear-Stat-Catalog.md` (read-only); `SkyyClasses-Plan.md`; `RESUME.md`; `tools/CONFIG-CONTRACT.md` (tables).
- `tools/skyyui.py`; `tools/deploy_set.py`; both `Assets.zip` files (read-only id check); the Wynncraft wiki page and API (fetched 2026-10-02).

## 16. Critic pass 2026-10-02: what was corrected

**Wrong or loose code facts (fixed in place):**
1. Only T:845 hard-codes 72 (T:1291-1292 are `len()`); the T:4172 assert (`len(_exact) == 19`), `TR_LVL_W` (T:3695, negative at 8 trees) and its `>= 240` assert (T:3801) were missing from the change list (sections 4, 13).
2. `skyyskill_mana` is coded at S:6796 (S:674 is a header note); the class XP table is S:1079-1096 and the `levels.class*` rows S:2866-2871 (S:2726-2735 are the class rows); S:6454 is `extraChance` (sections 1, 2).
3. The crossbow locks are in OPEN-QUESTIONS "Crossbows stay loaded" (l.484-485 now), not at l.390-391; the loaded-crossbow perk clamps at 6 bolts (S:7640) and vanilla's refund ladder has 6 steps (section 7).
4. A modifier rune's `AppliesTo` holds ability tags; Damage, AoeScale, Duration ... are attribute names (section 8).
5. `/skills mana` lists the source as `trees=+5` (S:7825), not "trees +5%" (section 13 checks).
6. Section 0 put Alchemy and Smithing on the second tab row; section 10 has them on row 1 (section 0 fixed).
7. The Runes "[TMP]" citation pointed at Audit 1 and 8, which do not say it (section 11).
8. Wynn: the wiki says 70+ upgrades per class, 1-2 AP, 50 AP at level 120, 3 Ability Shards to reset; the brief's 88-97 nodes is now marked UNVERIFIED (section 5).
9. The Appraiser did not need the `/gear rarity` path: `GearRoll.identify` can write the doc's `r` key before `rollMods` (section 3).
10. Haggler touches 7 call sites, not 2 functions (section 3).
11. The `class.nodes` table is a 3-column key-family table (the contract allows 3 columns at most), so the Min level of the crossbow nodes needs its own `class.minLevel` row (section 13).
12. Long Brew only grows the effects in `perk.alchemy.extend` (Health and Signature regen, Morph, Antidote); Stamina potions are instant (`Potion_Stamina_Instant_*` + a cooldown), so the two Long Brew nodes now say so and use regen-potion icons instead of Stamina ones (section 2).

**Missing locks and conflicts (added):** the Mining Dust rate 5 (OPEN-QUESTIONS l.194-198); the identify-rarity lock l.178-182; "Class Level stays separate" (Decisions 2.5) and the Borderlands-style lock are now named as superseded (section 5); the SkyyGear 0.2.2 / 0.2.3 disagreement (l.181 vs l.188) and the fact that SkyyGear has no patch scripts (section 12, M1).

**Maths and layout:** AP is 0 at class level 0 like Tokens; the "78%" line now says what a level-100 player owns; the pick-one diamond no longer shows P3 hanging off P2 and every link is axis-aligned (no diagonals; 21 + 20 bars); the class cell text, info row, rune strip and tab rows got width budgets measured with the kit font table; the window is 892 + 44 + 5 = 941.

**Design changes (revert any in one edit):**
- Smithing slots: Steady Hand S4, Keen Eye S5 (tier II), Appraiser S7 (tier III); Forge Hardened S6, Haggler S11 (pace: Smithing 20 is about 5,300 crafts, Smithing 10 about 100). The ids are unchanged, so code that reads `Smithing.<Id>` is unaffected, but `research/Loot-Unid-Spec.md` section 6 (written in parallel) still labels the old slots (S5 Haggler, S6 Keen Eye, S7 Steady Hand, S11 Appraiser, Keen Eye 3% / 45%) and needs relabelling.
- "Signature ability" renamed "capstone ability" (vanilla Signature is the weapon meter; there are Signature potions).
- `class.enabled` ships off until the probe page worked; a one-time free class respec on flip day.
- Craft XP gets an exclude list (`xp.craft.exclude`, default `Tool_Sickle_Copper`) because the parallel loot spec also pays crafted tools.
- Questions 7, M1 and M2 added; question 6 now states the pace.

**Checked and left as written:** the Alchemy and Smithing per-level totals and the slot table (max level, tier, B, tokens), all 24 tree icons and the potion chain, the 64 AP / 27 AP maths, the five class live totals, the Wynn-lane names against the cloud draft, the 0.7 rune facts against Runes 2.1-2.4, the fix list against Audit section 7, and that nothing in the build stages references a rune class before 0.7.
