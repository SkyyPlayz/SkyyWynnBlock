# Metals build part 2 - Fortune, metal tools, craftable metal weapons (SPEC, nothing built)

Where things go: Skyy's answers to the questions at the end -> `docs/answered/gear.md` (`python tools/qa_append.py gear <file> --close "..."`);
build notes -> each mod's patch script docstring; results -> `docs/log/<YYYY-MM>.md`; queue state -> `LOCAL-RESUME.md` item 3.
Part 1 (ores, spawn, smelting, alloys, Electrum, Furnace Charm - LIVE, TEST-CHECKLIST 177) = `research/Zone-Ores-Alloys-Spec.md`.
Source of truth for the locked rules: Cobb's `SkyWynn-PRIVATE-art\metal-art\skywynn-metals-build-spec.md` (outside the repo, read-only;
sections 2 + 5 used here) + `skywynn-metal-items-inventory.md` + `skywynn-custom-weapons-list.md`. Written 2026-10-17 by a spec agent.
`research/Metal-Art-Manifest.md` did NOT exist yet when this was written (the art agent, queue item 2, is still making it).

## 0. Decision lines this spec follows

- Skyy 2026-10-17: "cobbs que in local resume" -> LOCAL-RESUME item 3: "METALS BUILD ... ores, spawn, smelting, alloys, Fortune, tools/weapons per the spec."
- Cobb spec 2 (LOCKED by Skyy 2026-10-17): one tier per metal in zone order, "this exact order, vanilla metals included":
  T1 Copper (Crude pick), T2 Iron, T3 Bronze, T4 Thorium, T5 Lead, T6 Dusk, T7 Cobalt, T8 Chromium, T9 Azurvane, T10 Adamantite,
  T11 Slag, T12 Cinder, T13 Mithril, T14 Titanium, T15 Lumen. The zone's alloy pick opens the next zone (its base ore at normal speed,
  its new ore at half); the next zone's base pick mines that zone's new ore at normal.
- Cobb spec 2 stats (LOCKED): "keep every existing tier number and its current specs exactly where they are; just add tiers." Lead (T5)
  takes T5's specs of today (Adamantite's), Dusk (T6) Mithril's; Cobalt T7 and up scale with the same step pattern. Block durability
  scales with the picks: a maxed pick of the previous zone one-hits that zone's blocks; in the next zone "normal speed" = about 5 hits.
- Cobb spec 2: every metal gets five tools - hatchet, pickaxe, multitool, harvester, watering can (fertilizing = a can upgrade; vanilla
  fertilizer stays). Forever tools follow this ladder from Crude (T1).
- Cobb spec 2 GENERAL RULE (LOCKED): everything in SkyWynn that uses metal gets a version per new metal AND alloy (Lead, Dusk, Chromium,
  Azurvane, Slag, Cinder, Titanium, Lumen). EXCLUDED: dropped vanilla tools (scythe, hoe), charms, bench accessories (spec 8),
  Foraging / Farming armor (spec 7), fishing (waits for the fishing build).
- Cobb spec 2 weapons (LOCKED): two tracks, both stay - Track 1 craftable metal weapons from bars ("so players never have to rely on drops
  for a weapon"), Track 2 drops unchanged. This REPLACES Zone-Tiers-Idea's "all combat gear is still drops only" for weapons.
  All 9 SkyyArmory metal families (wand, crossbow, spellbook, kunai, Bo, gauntlets, soul cage, great shield, Mage staff) get all 8 metals.
  Recipes: bars as the ingredients. Crossbows = our own from the vanilla crossbow (nothing from More Crossbow Tiers, ARR).
- Cobb spec 5 (LOCKED): Mining Fortune = MAINLY the forever tool + a skill-tree node, added together; Smelting Fortune = only the smelting
  skill tree, only the smelt step; the two never stack; +10% per level; NO CAP; drops = 1 + floor(F/100) + one more with chance (F mod 100)%.
  NOTE: the task text said "cap 100%, max 10 levels" - Cobb's file says both were DROPPED by Skyy ("NO CAP (Skyy 2026-10-17, replaces the
  old 100% cap)", "Old note 'max 10 levels' is dropped. If a level cap is needed per source, builder proposes it"). This spec follows the file.
- Standing rules used: PROJECT-RULES 2 (survey, no duplicates), 4 (tier tags from `tools/tier_tags.py`, sort by tier, four power sources,
  everything editable in Server Setup, one-time migrations), gear.md 2026-10-12 LIFELONG TOOLS ("tools can't be crafted, only upgraded"),
  2026-10-16 FLAT LINE COSTS (1 point = 1 level, the 10 x tier cap stays), 2026-10-16 MULTITOOL = TWO STAT SETS, 2026-10-16 ONE FARMING TOOL
  (Harvester + watering can replace hoe + sickle).

## 1. What already exists (VERIFIED in the pinned build scripts, tools/deploy_set.py SET)

| Piece | Where (pin) | Today |
|---|---|---|
| Tool Fortune line `fort` | SkyyGear 0.3.20 `LL_PERKS`, `lifelong.perkFortune` | +2 Fortune a level (100 Fortune = one extra drop), 1 point a level, works up to `lifelong.lineCapPerTier` (10) x tier; above the cap levels stay saved but inactive |
| Tool base Fortune | SkyyGear `tool.fortune.perLevel` 0.2 x tool level x material bonus; rarity 0-25 %; rolled modifiers | posted as `skill:bonus:<uuid>` source `"gear"`, key `dd.mining` (= Fortune / 100) |
| Fortune roll | SkyySkills 0.4.49 `Perks.fortune` / `Perks.extras` | whole part = sure extra drops, rest = chance (exactly Cobb's formula); the `"gear"` part is UNCAPPED (`perk.fortuneMax` 0); every other source (level perk, trees, accessories, pets) is still capped at `perk.doubleDropMax` 1.0; `perk.fortuneGuard` 100 extra drops max; placed blocks never double (PlacedStore); extras never count for collections |
| Tree node Mining Fortune `MFortune` | SkyyTrees 0.3.22 NODES Mining | 20 levels x 0.01, kind DD -> `skill:bonus` source `"trees"` `dd.mining` |
| Tree node Smelter's Luck `SSmelt` | SkyyTrees 0.3.22 NODES Smithing | 20 levels x 0.01 "chance per bar of one extra bar"; declared `tree:reads:SkyySacks` + SkyySkills, but **no reader implements it** (grep: 0 hits in Sacks 0.8.20 / Skills 0.4.49) - the node is bought and stored but does nothing |
| Other ore-doubling nodes | SkyyTrees Mining | `MVeins` Rich Veins (15 x 2 % an ore drops once more), `MBars` Prospector (10 x 1 % an ore also gives its bar) |
| /craft Furnace smelt | SkyySacks 0.8.20 `ProcBench.finishUnit` | ore -> bar 1:1, `SkyyAlloy` 1 + 1 -> 1 rows (Furnace Charm tier lock), Smithing XP via `skill:fn:craftxp` |
| Lifelong ladder | SkyyGear `LL_LADDER_ROWS` (`lifelong.ladders` row) | pickaxe / hatchet Crude > Copper > Iron > Thorium > Cobalt > Adamantite; costs 25 Copper bars, then Enchanted ingots (hatchet: Enchanted logs); + collection tier-up gate |
| Can / Harvester | SkyyGear, `tools/tier_tags.py` `CAN_TIERS` / `HARVESTER_TIERS` | `Tool_WaterCan_<Crude..Adamantite>` (6), `Tool_Sickle_Harvester_<Crude..Thorium>` (4) |
| Tier gate | SkyyGear `LL_ORE` (+ `gate.nextFactor` 0.4 = 2.5x hits one tier up, 10x two up) | knows Copper..Onyxium (+ Silver / Gold); NOT Lead / Chromium / Slag / Titanium (queued round `gear-ores`, Zone-Ores spec 2.5) |
| Tier tags | `tools/tier_tags.py` | internal ladder 0-7 shown T1-T8 (Crude T1, Copper T2, Iron T3, ...); zone metals share the partner's number ("T4 Lead") |
| Vanilla item gaps (Assets.zip) | - | NO vanilla `Tool_Pickaxe_Bronze`, `Tool_Hatchet_Bronze`; vanilla metal weapon families with a Copper..Onyxium ladder: Sword, Longsword, Axe, Battleaxe, Mace, Club, Daggers, Spear, Shortbow, Shield, Staff; Crossbow only Iron + Ancient Steel |

## 2. Fortune

### 2.1 Mining Fortune (tool + tree, added together, no cap)

| Source | Lives in | Change | Bridge |
|---|---|---|---|
| Forever tool line `fort` | SkyyGear (pickaxe; the multitool's pickaxe stat set) | new row `lifelong.perkFortune.mining` = 10 (+10 Fortune = +10 % a level); hatchet / Harvester / pole keep `lifelong.perkFortune` 2 until Skyy says (Q4) | unchanged: `skill:bonus:<uuid>` source `"gear"` `dd.mining` |
| Skill-tree node `MFortune` | SkyyTrees | per level 0.01 -> 0.10; max 20 -> 10 (Q3); text "+%V Mining Fortune (100% = one sure extra drop)" | unchanged: source `"trees"` `dd.mining` |
| Add together, no cap | SkyySkills `Perks.fortune` | the `"trees"` part joins the UNCAPPED part with `"gear"` (Mining row only); level perk + accessories + pets + armor keep their own caps (`perk.doubleDropMax`, `accessories.fortune.cap` 10, pet cap) - those are the other power sources, not "Fortune upgrades" | none new |

- Example: tool line Lv 15 (+150) + tree Lv 5 (+50) = 200 % -> always 3 drops. 250 % -> 3 + 50 % for a 4th.
- Scope unchanged: the blocks the Mining Fortune already rolls on (tool part only on SkyyGear's `only.mining` blocks: rock / ore).
- Saved data: none (levels saved by key). Migrations (PROJECT-RULES 4): SkyyTrees `nodes.Mining` MFortune line 0.01/20 -> 0.10/10 only when
  untouched; a player above the new max keeps the levels SAVED and gets the extra tokens refunded on next login (`TreeMig` marker, log line)
  - never silently lost. Gear: new key only (no migration). Skills: no config change (a source list is code).
- Rollback: older SkyyTrees reads the new line as 0.10 a level (a big buff) -> Undo the row first (Server Setup change log).

### 2.2 Smelting Fortune (smelting tree only, smelt step only)

| Piece | Lives in | Rule |
|---|---|---|
| Node | SkyyTrees `SSmelt` (rename "Smelting Fortune") | 0.01 -> 0.10 a level, max 20 -> 10 (Q3), same migration / refund as MFortune; text "+%V Smelting Fortune - extra bars when YOU smelt in /craft Furnace" |
| Roll | SkyySacks `ProcBench.finishUnit` (Furnace bench only) | F = the owner's `tree:fn:bonus("Smithing.SSmelt")`, SNAPSHOT when the unit is QUEUED (stored on the job, new key `sf`; older Sacks ignores it) - respec after queuing changes nothing; extras = `floor(F) + (r < F mod 1)`, given as ONE stack into the same output; clamp `smelt.fortune.guard` 100 |
| Which smelts | Sacks | output `Ingredient_Bar_*` from (a) a raw `Ore_*` input (1:1) and (b) `SkyyAlloy` rows (Q5). NEVER Salvagebench, Enchanted un-compress, Skyy_Ench_* inputs, charcoal, cooking, or the SkyyShards Auto-Smelt Pole |
| Placed vanilla furnace | SkyySkills take-out path | OFF by default (`smelt.fortune.placed` false) - same as the Furnace Charm (/craft only; the placed furnace has no per-player job and take-out can be repeated) |
| Feed | Sacks -> the 0.4.42 Fortune indicator | "Smelting Fortune! Iron Ingot x3" (reuse SkyySkills' feed bridge if exposed - UNVERIFIED; else one chat line) |

- Never stacks with Mining Fortune: Mining Fortune is read only on block break (SkyySkills), Smelting Fortune only in finishUnit (Sacks);
  the Prospector bar (MBars) and Auto-Smelt totem bars are NOT smelts and get no Smelting Fortune.

### 2.3 Exploits

| Risk | Guard |
|---|---|
| Place ore, mine it again | Ore blocks drop raw ore, never the block; PlacedStore already denies Fortune + XP on placed blocks (kept). Shard / zone worlds unchanged |
| Respec loop (buy Fortune, queue, respec) | Smelting Fortune snapshot at queue time; respec gives tokens back, not bars |
| Smelt / unsmelt loop | No bar -> ore recipe exists; Salvage (bars back from gear) is not a smelt; un-compress (Enchanted -> 100 bars) is not a smelt; alloys cannot be split. Build check: Sacks refuses Fortune on any recipe whose input is an `Ingredient_Bar_*` other than the alloy rows, or any `Skyy_Ench_*` |
| Bazaar loop: buy ore -> smelt with 300 % -> sell 4 bars | REAL (bars are priced from their ore). Default guard `smelt.fortune.minedOnly` = true: Fortune bars only for ore the player MINED - SkyySkills keeps a per-profile counter per ore id (+1 per raw ore paid Mining XP, incl. Mining Fortune extras), Sacks takes from it at queue time via a new bridge `skill:fn:oreBudget` apply(Object[]{UUID, String oreId, Integer n}) -> Integer granted; units beyond the budget smelt at 1:1. Saved per profile (PROFILES-CONTRACT), capped `smelt.fortune.budgetMax` 100000 |
| Mining Fortune floods the Bazaar | Intended income, but x10 per level is a big jump from +2: SkyyBazaar sell caps unchanged; flag for Skyy (Q4) and watch the coin log after the deploy |
| Trading Fortune bars | fine - they were earned |
| Multitool double Fortune | multitool keeps two stat sets (gear.md 2026-10-16): mining uses ONLY the pickaxe set |

### 2.4 Server Setup rows (skyycfg, `tools/CONFIG-CONTRACT.md`)

| Mod | Key | Default | Label |
|---|---|---|---|
| SkyyGear | `lifelong.perkFortune.mining` | 10 | Mining Fortune per tool level |
| SkyyTrees | `nodes.Mining` MFortune / `nodes.Smithing` SSmelt (existing table rows) | 0.10 / max 10 | Mining / Smelting Fortune per level, max level |
| SkyySkills | `perk.treeFortuneUncapped` | true | Tree Mining Fortune adds with the tool, no cap |
| SkyySkills | `smelt.fortune.placed` | false | Smelting Fortune at placed furnaces |
| SkyySkills | `smelt.fortune.budgetMax` | 100000 | Most mined ore remembered for Smelting Fortune |
| SkyySacks | `smelt.fortune.enabled` / `.alloys` / `.minedOnly` / `.guard` | true / true / true / 100 | Smelting Fortune on, on alloys, only on ore you mined, most extra bars per unit |

## 3. Metal tools (forever tools on the 15-step ladder)

### 3.1 The ladder - OPEN QUESTION (Q1) with a default

Cobb's file says the 15-step order is LOCKED. Still open for Skyy: how the renumber lands on what exists. Default:
- Tier tags renumber to Cobb's T1-T15 in ONE table (`tools/tier_tags.py` LADDER / TOOL_METALS / ZONE_METALS / ALLOYS): Crude + Copper T1,
  Iron T2, Bronze T3, Thorium T4, Lead T5, Dusk T6, Cobalt T7, Chromium T8, Azurvane T9, Adamantite T10, Slag T11, Cinder T12, Mithril T13,
  Titanium T14, Lumen T15. Onyxium (parked, Zone 6) = T16, Scrap / Wood = T1, Steel = T2. Every owner mod's lang must be rebuilt
  (SkyyCollections, SkyyGear, SkyyArmory, SkyyWorldGen) - `tools/ci/langdup.py` + `test_tier_tags.py` updated in the same round.
- Crude and Copper are both T1: the Crude > Copper tier-up stays (cheap, 25 Copper bars) as the T1 finish - no saved tool changes tier.
- Level bands (`level.material`): existing metals keep their bands (Zone-Tiers: "dont change now"); new metals slot between neighbours:
  Bronze 17-25, Lead 22-30, Dusk 24-32, Chromium 28-40, Azurvane 31-41, Slag 37-45, Cinder 39-47, Titanium 45-55, Lumen 50-60 (post-rebirth).
  The full 3-tiers-per-zone re-band stays a separate decision.

### 3.2 Mining reach + power (SkyyGear tier gate, runtime only - no vanilla pickaxe file overridden)

Ore tier = its metal's T. New row `gate.oreTiers` (text) = ore word : normal from tool T : half from tool T; anything lower = the existing
two-up factor (10x hits), never locked out (Tool-Levels 7):

| Ore | Copper | Iron | Thorium | Lead | Cobalt | Chromium | Adamantite | Slag | Mithril | Titanium |
|---|---|---|---|---|---|---|---|---|---|---|
| normal from | T1 | T2 | T3 | T4 | T6 | T7 | T9 | T10 | T12 | T13 |
| half speed at | - | T1 | - | T3 | - | T6 | - | T9 | - | T12 |

- "Half speed" = new row `gate.halfFactor` 0.5 (2x hits); `gate.nextFactor` 0.4 stays for other one-up cases.
- New-ore picks (Lead T5, Chromium T8, Slag T11, Titanium T14): same reach as the pick below + the next power step (Cobb's proposal).
- Power per tier: new row `tool.tierPower` (T1..T15 multiplier on the vanilla Power, read in `GearToolHitSys`). Today's internal rows keep
  their numbers at their index (T1 = today's Crude/Copper row, T2 Iron, T3 Thorium-row ... per Cobb "Lead takes Adamantite's, Dusk Mithril's");
  T7+ = the same step ratio continued. The builder prints the table (vanilla Power x multiplier = hits on each zone's ore) in the PR.
  INTERPRETATION UNVERIFIED (Q2): "specs T5 has today" read as Gear's internal tier index 5 (Adamantite), not the shown tag "T5 Cobalt".
- Block durability goal (maxed previous-zone pick one-hits; next zone ~5 hits at normal): reached with the hit maths of Collections-Tools
  6.2 by tuning `tool.tierPower` + the ore's tier; rock / stone of a zone world is NOT tiered in this round (needs the zone of the world -
  later, Q8).

### 3.3 The five tools per metal

| Tool | Ids (new, SkyyGear items; Parent = the nearest vanilla tool) | Metals added | Notes |
|---|---|---|---|
| Pickaxe | `Tool_Pickaxe_<Metal>_SkyWynn` | Bronze, Lead, Dusk, Chromium, Azurvane, Slag, Cinder, Titanium, Lumen (vanilla Copper/Iron/Thorium/Cobalt/Adamantite/Mithril kept) | vanilla model + our texture |
| Hatchet | `Tool_Hatchet_<Metal>_SkyWynn` | same 9 | Foraging Fortune line unchanged |
| Multitool (after rebirth 1) | `Tool_Hatchet_Pickaxe_Multitool_<Metal>_SkyWynn` | same 9 | two stat sets; model = Multitools' (MIT, credit InkBlindCat) by path if loadable, else vanilla pickaxe + hatchet boxes (UNVERIFIED) |
| Harvester | `Tool_Sickle_Harvester_<Metal>` (existing pattern) | Cobalt, Adamantite, Mithril + the 9 | sweep respects tier (gear.md 2026-10-16) |
| Watering can | `Tool_WaterCan_<Metal>` (existing pattern) | Mithril + the 9 | area grows with tier; fertilize = a can upgrade line |

- ~55 new items. Shovel is not in Cobb's five -> stays on its vanilla ladder (Q6).
- Lifelong rule: tools are NOT crafted (gear.md 2026-10-12); Cobb's "one tool per metal, bars as the ingredients" = the TIER-UP cost.
  `lifelong.ladders` rows extended: each step costs that metal's bars (Enchanted bar where `tools/skyyench.py` has one; alloys = plain
  alloy bars, alloys have no Enchanted form), plus the hatchet / Harvester / can keep their skill material as a second ingredient (Q7);
  the collection tier-up gate (Collections IV of the base metal; alloys gate on BOTH parent collections).
- Bronze needs our own pickaxe + hatchet items (no vanilla ones); vanilla Bronze is already T3 in the tags.
- Mining armor ladders (Queue 1, Gear 0.3.21) tier up on the same ladder - the same `tools/tier_tags.py` table.

## 4. Craftable metal weapons (Track 1) next to drops (Track 2)

### 4.1 Families

| Group | Families | Metals | Mod | Count |
|---|---|---|---|---|
| A. SkyyArmory metal families | Wand, Crossbow, Spellbook, Kunai, Bo, Gauntlets, Soul Cage, Great Shield, Mage staff (`Weapon_Staff_<Metal>_SkyWynn` new custom ids) | the 8 new (+ Crossbow fills Iron..Mithril, which it lacks) | SkyyArmory | 72 + ~5 |
| B. Vanilla-style metal weapons | Sword, Longsword, Axe, Battleaxe, Mace, Club, Daggers, Spear, Shortbow, Shield (`Weapon_<Family>_<Metal>_SkyWynn`) | the 8 new | SkyyArmory (the weapon mod; Gear only needs table rows) | 80 |

- Group B is a DEFAULT (Q9): Cobb's exclusion "rule covers custom SkyWynn items only" could exclude vanilla families, but then Warrior /
  Berserker / Assassin / Archer would stop at Mithril while Mage / Priest / Monk reach Lumen; LOCAL-RESUME's art scope says "Metal weapons,
  matching the vanilla metal weapon set". Hand wraps (cloth), UT and Mythic weapons get no metal versions.
- Ids end `_SkyWynn` (TerrariaToolsWeapons owns Lead ids; word 3 stays the metal for Gear's id parsing); class mapping keeps working through
  the `Weapon_<Family>_*` prefixes (`PP_WEAPONS`, SkyyClasses).
- Duplicate check (PROJECT-RULES 2): builder lists The Armory 1.23.0 ids for these metal names (`tools/pack_drops.py`) - none expected.

### 4.2 Recipes (bars)

- Copy the zone partner's VANILLA recipe of the same family (Lead/Dusk <- Thorium, Chromium/Azurvane <- Cobalt, Slag/Cinder <- Adamantite,
  Titanium/Lumen <- Mithril), swap the bar for the new metal's bar, keep the partner's other inputs, bench + RequiredTierLevel. Alloy weapons
  use the same COUNT of alloy bars (an alloy bar already costs two bars). Armory families copy their own Copper..Mithril recipe rows.
  (Vanilla e.g. `Weapon_Sword_Mithril` = 6 Mithril bars + 3 Storm leather + 1 Voidheart, Weapon_Bench.)
- A recipe UNLOCK per metal = the base metal's collection tier (Collections recipe rewards, like tools); alloys = both parents.
- Standalone recipe files are NOT needed: the items are ours, the recipe sits in the item JSON (vanilla pattern).

### 4.3 Stats on our curves

- Damage = asset damage (metal multiplier) x SkyyGear F(level) x band bonus (SkyyArmory-Spec 3.2) - no second scaling.
- New metal multipliers are INTERPOLATED (geometric) between the existing neighbours on Cobb's order (Bronze between Iron and Thorium; Lead,
  Dusk between Thorium and Cobalt; ... Titanium, Lumen above Mithril by the Adamantite -> Mithril step). Existing weapons keep every number
  (no live rebalance). Mana costs (wands, staffs, books) follow the same rule. Builder prints the table in the PR (Cobb: "exact numbers
  aren't important"). Gear needs only rows: metal word -> band (3.1) + material bonus.
- Wynn rarity + identify: crafted = rolled at craft at your level (`craft.levelFrom`), rarity Normal..Fabled by `odds` + Smithing step-up,
  capped by `craft.maxRarity` (Fabled), identified at once; ID ranges = Gear's normal stat-roll ranges. Drops (Track 2) stay unidentified,
  can be Mythic / UT / Set (never craftable - gear.md 2026-10-17), and keep their own drop tables. So drops stay the top end; crafting is
  the floor that never fails you.
- Salvage: crafted 25-50 % of the recipe (`gear:fn:salvage`, live) - never more bars than went in, so no Fortune loop (2.3).
- Lists sort by tier (tier tags) then name in /craft, Weapon_Bench pages and shops.

## 5. Builders (one mod per builder; models: builders Opus, critics / cross-check Sonnet)

| # | Mod (pin -> next) | Job | Waits on | Round |
|---|---|---|---|---|
| F1 | SkyyTrees 0.3.22 -> 0.3.23 | MFortune / SSmelt numbers, texts, max, migration + token refund | nothing | full (saved tree levels) |
| F2 | SkyySkills 0.4.49 -> 0.4.50 | trees part uncapped for Mining, mined-ore budget + `skill:fn:oreBudget`, placed-furnace switch, feed bridge | nothing | full (economy, per-profile data) |
| F3 | SkyySacks 0.8.20 -> 0.8.21 | Smelting Fortune in `finishUnit`, queue-time snapshot + budget, rows, logs `SMELT-FORTUNE` | F2's bridge name (fixed here, so parallel) | full (items could be duped) |
| G1 | SkyyGear 0.3.21 -> 0.3.22 + `tools/tier_tags.py` | 15-tier renumber, `gate.oreTiers` / `halfFactor` / `tool.tierPower` (= the queued `gear-ores` round), Mining Fortune row, `level.material` bands, weapon metal rows | Queue 1 (Gear 0.3.21 mining armor) pinned - Gear is LOCKED to it now | full (several mods' tags, saved caps) |
| G2 | SkyyGear 0.3.22 -> 0.3.23 | ~55 tool items + ladder rows + art hook (placeholder recolours if art is missing) | G1; art (Q2 queue) optional | full |
| A1 | SkyyArmory 0.1.30 -> 0.1.31 | Group A (72 + crossbow gaps) | G1 (metal rows + bands) | full (new system, many items) |
| A2 | SkyyArmory 0.1.31 -> 0.1.32 | Group B (80) | A1; Skyy Q9 | full |
| L1 | SkyyCollections 0.2.25 + SkyyWorldGen 0.7.3 (+ SkyyBazaar text) | lang rebuild for the renumbered tags + recipe unlock rewards for new weapons / tool tier-ups | G1 | lean each |

Order: F1 + F2 + F3 in parallel now (no lock, no art) -> deploy "Fortune" set. G1 after Queue 1 pins -> L1 -> G2 + A1 (parallel, different
mods) -> A2. Art: G2 / A1 / A2 ship build-time recolours of vanilla textures (ores01 precedent) when `models-local/art/metals/` or
`research/Metal-Art-Manifest.md` has nothing yet; the real art swaps in later with no id change. Smoke + cross-check per deploy (PROJECT-RULES 3).

## Questions for Skyy (today's default in [brackets])

1. The 15-step ladder Copper, Iron, Bronze, Thorium, Lead, Dusk, Cobalt, Chromium, Azurvane, Adamantite, Slag, Cinder, Mithril, Titanium,
   Lumen: renumber every tier tag now (T1-T15, Onyxium T16), with Crude and Copper both T1? [yes - one table, both T1, Crude > Copper stays]
2. "Lead takes T5's specs of today (Adamantite's)" = Gear's internal tier row 5, so Thorium / Cobalt / Adamantite / Mithril forever tools
   get STRONGER than vanilla at their new numbers? [yes, forever tools only, runtime - vanilla files untouched]
3. Fortune levels per source with +10 % a level and no total cap: tool line keeps its 10-x-tier level cap; tree nodes max 10 levels (100 %)? [yes]
4. +10 % a level only for Mining Fortune on the pickaxe (5x today's +2), hatchet / Harvester / pole Fortune unchanged for now? [yes]
5. Smelting Fortune on alloys too? [yes]
6. Shovel: not in the five tools - stays on its vanilla ladder (Copper..Cobalt)? [yes]
7. Tier-up cost for the hatchet / Harvester / can: the metal's bars PLUS today's log / crop item? [yes]
8. Rock and stone in higher zones harder to break (zone-tiered blocks), or ore only for now? [ore only now; rock later]
9. Vanilla-style metal weapons (sword, axe, daggers, bow, ...) in the 8 new metals too, so every class can craft to Lumen? [yes, in SkyyArmory]
10. Smelting Fortune only on ore you mined yourself (blocks the buy-ore-smelt-sell Bazaar loop)? [yes]
11. Rich Veins (MVeins) is a second ore double-drop next to Mining Fortune: keep both? [keep - separate small roll]

## UNVERIFIED

- That nothing reads `Smithing.SSmelt` today (grep of Sacks 0.8.20 / Skills 0.4.49 found none; a dynamic key build could hide it).
- `ProcJob` save format accepts a new key (`sf`) that older Sacks ignores; the job owner UUID is known in `finishUnit`.
- SkyySkills' Fortune feed indicator is reachable from another mod (bridge name).
- Multitools' model can be referenced by path from our items while the pack mod is loaded.
- The tier-gate hit counts for the "about 5 hits" goal (builder's python table in the PR, then a Skyy test).
- Gear's lifelong cap `lifelong.lineCapPerTier x tier` uses the internal tier index; the renumber must never LOWER a held tool's cap
  (build check: cap(new) >= cap(old) for every ladder item).
- Recipe unlock rewards for weapons in SkyyCollections (the reward token for "recipe" exists for tools - UNVERIFIED for weapons).
- New-ore collections exist in SkyyCollections 0.2.25 (Zone-Ores B4 says yes; the id `Lead_SkyWynn` did not grep - generated names?).
