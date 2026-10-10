# Special tools - UT + Mythic gathering tools, Vein Mine 1-8, Tree Feller 1-8, Auto Smelt, solo hammers, Multitools

Cloud draft, 2026-10-10. Paper design; nothing built. Turns `research/Tool-Mods-Survey.md` section 5 (the 10 quest / loot-only tools, list
approved by Skyy) into a buildable spec, with Skyy's 2026-10-10 locks on vein mine, hammers, the ability home, Multitools and Mythic tools.
Every number is a placeholder and a Server Setup row (times in seconds). Arithmetic: python3 (method shown next to each table).
Read with: `research/cloud/Untiered-Mythic-Spec.md`, `research/cloud/UT-First-Batch-Build.md`, `research/Tool-Levels-Spec.md`,
`research/cloud/Tool-Levels-Revision.md`, `research/cloud/Mining-Armor-Spec.md`, `research/cloud/Gathering-Armor-Stats.md`,
`research/cloud/SkyyQuests-Zone1-Spec.md`, `research/cloud/Zone-Bosses-Ideas.md`, `research/cloud/Ore-Regrow-Spec.md`.

## 0. Decisions this follows (newest wins; none re-decided)

| Source (line) | Skyy's words (short) / the lock | Used in |
|---|---|---|
| `docs/answered/gear.md` 144 (REQUEST 2026-10-10) | "special pickaxes you cant craft, you can only find and get from quests. (with things like auto smelt, and vein mine.)" | all |
| `docs/answered/gear.md` 145 (LOCKED 2026-10-10) | "hammers wont work great for the server plan, but would be fine for solo. (i wouldnt allow vein mine on a hammer. and id make sure the vein mine have levels to keep it in check. lvl 1 breaks 1 extra block. lvl 2 breaks 2 and so on. capped at 8 so it mines a 3x3 like the hammer. (works on stone, but when breaking ore, only breaks the connected ore of that type. which is its main use.)" | 2, 6 |
| `docs/answered/gear.md` 146 (LOCKED 2026-10-10) | "Build our own (Recommended)"; "Untiered orange (Recommended)" -> special tools are UT, level = drop zone band, ability grows with tool level, each has a downside. Ability home: "a mix of both. i want tools that have these ability's. but i want things like vein mine, and tree feller in the skill tree too. so a pickaxe without vein mine gets a little from your class, that can stack with you pickaxe if you have a pick that has it too. (auto smelt would be a really late game tree upgrade." -> tree levels STACK with the tool's, total capped at 8. Survey defaults: no Mining-perk-only 3x3, hidden recipes, Multitool gated by Mining AND Foraging, magnet = tool ability only, no durability downsides, no PedriJoe message | 1, 4, 5 |
| `docs/answered/gear.md` 147 (LOCKED 2026-10-10) | Multitools: "make it cost a pickaxe, a hatchet and a shovel of the same tier to craft. AND the tradeoff is, its slightly slower mining and chopping than the normal tool of that kind, AND you get less fortune. BUT you get both kinds on the same tool." -> SkyyGear 0.2.18, speed 85 %, Fortune 70 % | 7 |
| `docs/answered/gear.md` 148 (LOCKED 2026-10-10, newest) | "(we might have a few mythic tools too, like a multitool with vein mine 3 and treefeller 3." -> a few MYTHIC tools, boss drops only | 1.3 |
| `docs/answered/gear.md` 142-143 (2026-10-10) | crafted tools roll rarity + tool modifiers, tools reforge (SkyyGear 0.2.17) | 1.1 |
| `docs/answered/gear.md` 123-128, 137 (2026-10-08 / 09) | UT = orange, fixed stats + one trade-off, never crafted, never sold, sources mob / chest / boss / quest; UT tiers = the 6 zone bands; orange Mystery Bag; level-up caps Mythic +2, UT +3; Mythic = bosses only; direct trade OK, never Bazaar / AH | 1, 8 |
| `docs/answered/gear.md` 17 (LOCKED 2026-10-02) | tool gate: pickaxe + shovel = Mining, hatchet = Foraging, hoe + sickle = Farming | 1, 7 |
| `docs/answered/gear.md` 41 (LOCKED 2026-09-30) | durability is OFF by default -> no durability downsides | 1 |
| `docs/answered/gear.md` 65-66 (2026-10-05) | "axes should also get tree feller"; NOTE: reuse the SkyyTrees Tree Feller, never a second felling system | 3, 4 |
| `docs/answered/gear.md` 81 (LOCKED 2026-10-06) | "Those speed tiers only roll on weapons. Not tools" | 1 |
| `docs/answered/skills.md` 51 (LOCKED 2026-09-25) | Tree Feller "same height as the cut. Extra logs 1 / 2 / 4 / 5 / 6 / 10 at levels 1-6 ... Cooldown 3 s" | 3 |
| `docs/answered/world.md` 64 (LOCKED 2026-10-10) | TWO MODES: SOLO pack (vanilla gen masked into islands) and SERVER (hand-placed zones, quests) | 6 |

## 0.1 How the code does it today (read-only, the SET pins SkyyGear 0.2.17, SkyyTrees 0.3.5, SkyySkills 0.4.29)

| What | Where | What it means here |
|---|---|---|
| Tool families by id prefix `Tool_Pickaxe_`, `Tool_Shovel_`, `Tool_Hatchet_`, `Tool_Hoe_`, `Tool_Sickle_`; any other `Tool_*` (vanilla hammers, watering cans) = no gate, no stats | `SkyyGear/build_skyygear_0.2.17.py` 1676-1677, 4038 | special tool ids KEEP the family word (`Tool_Pickaxe_UT_<Name>`) so gate, level Power and Fortune work; a hammer must NOT use the vanilla `Tool_Hammer_` family |
| Material tier read from the id words (`_tool_tier`, Crude 0 ... Onyxium 7) | `SkyyGear/build_skyygear_0.2.17.py` 4034-4046 | a UT / Mythic id has no metal word -> tier None; the row must carry its base item's tier |
| Level Power curve + Fortune 0.2 x L x (1 + 2 % x tier), tool cap 25; rarity boost 0-25 % | `SkyyGear/build_skyygear_0.2.17.py` 4024-4033, 4093-4100; header 296-336 | special tools get the same level stats as a plain tool of their base |
| Fortune delivery: the held tool posts source "gear" in `skill:bonus:<uuid>` (`dd.<skill>`, `only.<skill>` filter) | `SkyyGear/build_skyygear_0.2.17.py` header 311-317, 335-336 | the ability levels ride the same source (new keys, section 4) |
| SkyySkills Fortune roll: level perk + other sources capped `perk.doubleDropMax`, plus the "gear" part, capped `perk.fortuneMax` 2 | `SkyySkills/build_skyyskills_0.4.29.py` 9395-9426, 4355-4356 | Lucky Pick's streak adds inside the tool's capped part |
| Worn mining armor Fortune capped `armor.fortune.cap` 15 (Onyxium full set = 15) | `SkyyGear/build_skyygear_0.2.17.py` 4421-4422; `research/cloud/Mining-Armor-Spec.md` 104-113 | unchanged; Onyxium "Vein Burst level (later)" becomes Vein Mine +1 (section 4) |
| UT rows `(key, id, base, owner, body, fixed+tricks, orange line, name, kind)`, copies built from the base JSON with Recipe REMOVED (codec check: Recipe is `append`, never inherited), `Variant` hidden, orange placeholder recolour, band fixed `UT_LO, UT_HI = 15, 29` | `SkyyGear/build_skyygear_0.2.17.py` 3728-3775 (rows), 3949-4016 (copies, codec check 3951-3960); header 57-75 | special tools are more UT rows; the band must become PER ROW |
| Gathering-tree nodes: Mining S12 `MVein` "Vein Burst" (max 5, up to 4 + 2 x level same-id touching ore, 40 s cooldown), `MBars` "Prospector" (chance for the ore's bar), Foraging S12 `FFeller` (6 levels, `feller.logs` 1,2,4,5,6,10, 3 s) | `SkyyTrees/build_skyytrees_0.3.5.py` 1255-1262, 1281, 1429-1434, 2949-2955 | Vein Mine and Tree Feller both live in SkyyTrees already - this spec reworks them, never a second system |
| `TreeAbil`: 26-neighbour `flood` (4000 reads cap), `flatFlood` (Feller, one Y level), `breakList` -> `BlockHarvestUtils.performBlockBreak` (real BreakBlockEvent per block: island protection, XP, double drops, Collections), positions remembered 5 s (no chains), one break action per player (`ACTIVE`), never placed blocks (`skill:fn:placed`), never in `ability.disabledWorlds`, radius `ability.maxRadius` 6 | `SkyyTrees/build_skyytrees_0.3.5.py` 4944-5216 | the Vein Mine engine reuses all of it |
| Trigger: on a paid break, `TreeGather.run` fires `vein(...)` for `Ore_` blocks and `feller(...)` for trunks with the node value as the block count | `SkyyTrees/build_skyytrees_0.3.5.py` 5292-5326 | the new count = summed level (section 4) |
| Ore -> bar map `TreeDefs.barOf` (Ore_<Metal>_<Rock> -> Ingredient_Bar_<Metal>, copper to adamantite) | `SkyyTrees/build_skyytrees_0.3.5.py` 925-927, 5306 | Auto Smelt reuses this map |
| Tree tiers I-VI open at skill 1 / 10 / 20 / 30 / 45 / 60; S12 = tier VI, 3 tokens, Dust B 150,000 x n^3 | `SkyyTrees/build_skyytrees_0.3.5.py` 1198-1199, 2232; `research/Skill-Trees-Spec.md` 136-151 | the Vein Mine node change + Auto Smelt node |

## 1. The final list

### 1.1 Rules for all special tools (UT)

| Rule | Value |
|---|---|
| Rarity | `untiered` (orange), fixed lines like the live UT weapons (no random modifiers, no modifier Reforge, Level up +3 at `cost.levelUp.untiered`) - see Question 2 |
| Level | the source level clamped to the row's UT band (UT1 1-14, UT2 15-29, UT3 30-44, UT4 45-59, UT5 60-75, UT6 76-100) |
| Gate | the family's skill (pickaxe / shovel Mining, hatchet Foraging, hoe / sickle Farming); rod = Fishing through SkyyFishing |
| Level stats | the base tool's own level Power + level Fortune (base tier, section 0.1), plus fixed body lines at `utline.power` 70 % (tool stat keys `mpow`, `mfort`, `mwis`, `cpow`, `ffort`, `fwis`, `afort`, `awis`) |
| Ability | ONE ability whose LEVEL grows with the tool level: `a = aLo + floor((L - lo) x (aHi - aLo) / (hi - lo))`, L clamped to the band (a level-up above the band keeps aHi) |
| Downside | one orange line; never durability (off by default); never a weapon speed tier |
| Never | crafted (no recipe on the copy), sold (market wall + SkyyMerchants never-list), in random gear bags (only the orange bag's tool type) |
| Ids | `Tool_<Family>_UT_<Name>` built by SkyyGear from the vanilla base JSON (like `Weapon_Sword_UT_Paperweight`); the rod `SkyyFishing_Rod_UT_<Name>` built by SkyyFishing (the SkyyArmory-builds-its-own pattern) |
| Look | the base model with the orange placeholder recolour (`UT_ART`), real art later per `.claude/skills/skywynn-art/SKILL.md` |

### 1.2 The 10 UT tools (the approved survey list, ids + numbers added)

Ability level per tool level (python3, the formula in 1.1): Veinbreaker Vein Mine 2 at Lv 30, 3 from Lv 37, 4 from Lv 44; Heartwood Tree
Feller 1 / 2 from Lv 22 / 3 from Lv 29; Lode-Lamp radius 4 / 5 from 22 / 6 from 29; Reaper's harvest radius 1 (3x3) to 2 (5x5) at 29; Lucky
Pick +1 Fortune per ore in the streak, +2 from Lv 14.

| # | Tool | Id | Base item (tier) | Gate | UT tier, band, zone | Ability (level by tool level) | Downside (the orange line) | Body lines |
|---|---|---|---|---|---|---|---|---|
| T1 | Veinbreaker Pickaxe | `Tool_Pickaxe_UT_Veinbreaker` | `Tool_Pickaxe_Cobalt` (4) | Mining | UT3, Lv 30-44, Zone 2-3 | **Vein Mine 2-4** (section 2) | "Mining Power -30 %. Extra vein blocks give no Mining XP." | `mfort mwis` |
| T2 | Emberpick | `Tool_Pickaxe_UT_Emberpick` | `Tool_Pickaxe_Adamantite` (5) | Mining | UT4, Lv 45-59, Zone 3-4 | **Auto Smelt** (ore drops become bars, section 5) | "Smelted bars pay half Smithing XP. Ore collections get no credit." | `mpow mfort` |
| T3 | Quarrymaster's Hammer | `Tool_Pickaxe_UT_Quarrymaster` | `Tool_Pickaxe_Adamantite` (5) | Mining | UT4, Lv 45-59, Zone 3-4 | **Area break 3x3** on rock + ore, SOLO ONLY (section 6); never Vein Mine | "Swings cost 3x Stamina. Gem crystal blocks need a normal pick." | `mpow` |
| T4 | Prospector's Lode-Lamp | `Tool_Pickaxe_UT_LodeLamp` | `Tool_Pickaxe_Iron` (2) | Mining | UT2, Lv 15-29, Zone 1-2 | **Magnet** radius 4-6 (ore drops fly to your bag) + held light | "No ground pile: drops that do not fit vanish after 3 s." | `mfort` |
| T5 | Lucky Pick | `Tool_Pickaxe_UT_Lucky` | `Tool_Pickaxe_Copper` (1) | Mining | UT1, Lv 1-14, Zone 1 | **Streak**: +1 / +2 Fortune per ore in a row (3 s window, max 10 ores), inside the tool cap 25 | "Any non-ore block resets the streak." | `mwis` |
| T6 | Heartwood Hatchet | `Tool_Hatchet_UT_Heartwood` | `Tool_Hatchet_Iron` (2) | Foraging | UT2, Lv 15-29, Zone 1-2 | **Tree Feller 1-3** (stacks, section 3-4) | "Felled leaves and saplings drop nothing. Tree Feller waits 6 s." | `ffort fwis` |
| T7 | Sapling's Boon Axe | `Tool_Hatchet_UT_SaplingsBoon` | `Tool_Hatchet_Cobalt` (4) | Foraging | UT3, Lv 30-44, Zone 2-3 | **Bonus loot**: 3 % per log for a sapling, fruit or rare wood piece (runtime ids, incl. pack mods' saplings - no file edits) | "Chops non-tree wood (planks, beams) at half Power." | `cpow ffort` |
| T8 | Reaper's Scythe | `Tool_Sickle_UT_Reaper` | `Tool_Sickle_Iron` (2) | Farming | UT2, Lv 15-29, Zone 1-2 | **Wide harvest** 3x3 -> 5x5 ripe crops per swing, replants | "Unripe crops cannot be harvested at all." | `afort` |
| T9 | Green Thumb Hoe | `Tool_Hoe_UT_GreenThumb` | `Tool_Hoe_Thorium` (3) | Farming | UT3, Lv 30-44, Zone 2-3 | **Wide till** 3x3 + plants the seed in your other hand / hotbar | "Seeds only (no flowers or saplings). Level up costs double." (the survey's "reforge doubled" - UT has no modifier reforge) | `afort awis` |
| T10 | Tidecaller's Rod | `SkyyFishing_Rod_UT_Tidecaller` | `SkyyFishing_Rod_Iron` | Fishing | UT4, Lv 45-59, Zone 3-4 | **Magnet bite**: catches land in your bag, bite wait -25 % | "Cannot catch trophy fish (common to rare only)." | (SkyyFishing lines) |

Row format for SkyyGear (the live `UT_ROWS` shape + a band and an ability field), e.g.
`("veinbreaker", "Tool_Pickaxe_UT_Veinbreaker", "Tool_Pickaxe_Cobalt", "gear", "mfort mwis", "mpow-30 vein=2:4 veinxp=0", "<orange line>", "Veinbreaker Pickaxe", "pickaxe", 30, 44)`.
New tricks: `vein=a:b`, `feller=a:b`, `smelt`, `area=3`, `magnet=a:b`, `streak=a:b`, `reap=a:b`, `till=3`, `boon=3`. A trick whose
code is not live is hidden from the tooltip and does nothing (LOCKED 2026-09-30 "never a stat that does nothing").

### 1.3 Mythic tools (boss drops only, purple)

Mythic rules as the weapons (`research/cloud/Untiered-Mythic-Spec.md` 2.1): level = the boss's level, x1.10 base stats, 6 modifiers from the
Mythic row (rolled, reforgeable), Level up +2, boss pool only, purple Mythic bag, tradable directly, never Bazaar / AH. No downside (Mythic =
better in every way); the ability levels are FIXED (Skyy's example "vein mine 3 and treefeller 3").

| # | Tool | Id | Base / look | Boss (level) | Hooks |
|---|---|---|---|---|---|
| M1 | **The Master Key** (multitool) | `Tool_Pickaxe_Mythic_MasterKey` + row flag `multi` | `Tool_Pickaxe_Adamantite` model, hatchet Woods power merged into its tool data at build (UNVERIFIED P6) | The Everfrost Yeti, Zone 3 guardian (Lv 45) | **Vein Mine 3 + Tree Feller 3**; counts as pickaxe AND hatchet (Multitool rules, section 7: gated by Mining AND Foraging) |
| M2 | **The Burn Notice** (pickaxe) | `Tool_Pickaxe_Mythic_BurnNotice` | `Tool_Pickaxe_Mithril` model (Mithril hidden until 0.7: falls back to Adamantite) | The Ember Warden, Zone 4 guardian (Lv 60) | **Auto Smelt + Vein Mine 4** (no Smithing / collection penalty) |
| M3 | **The Clear-Cut Policy** (hatchet) | `Tool_Hatchet_Mythic_ClearCut` | `Tool_Hatchet_Cobalt` model | The Broodmother, Zone 2 guardian (Lv 30) | **Tree Feller 4** + felled logs go straight to your bag |

Ids: the family word stays first so every SkyyGear reader treats them as their family (the Mythic weapons use `SkyyArmory_Special_<Name>` in
`research/cloud/Own-Specials-Draft.md` 119 because SkyyArmory owns their movesets; tools need the `Tool_<Family>_` prefix). M1 is NOT built on
a Multitools item: copying their JSON would make our jar fail asset validation when Multitools is missing; our flag gives the same rules.

## 2. Vein Mine 1-8 (Skyy's rule, SkyyTrees engine)

| Rule | Value |
|---|---|
| Level N | breaks **N extra blocks** (Skyy: "lvl 1 breaks 1 extra block. lvl 2 breaks 2"), N = the summed level of section 4, **capped at 8** |
| On ORE (`Ore_` id, its main use) | only **connected ore of the SAME id** (Skyy: "only breaks the connected ore of that type"): breadth-first from the broken block over the 26 neighbours (the live `flood`), nearest first, up to N blocks, inside `vein.radius` 3 |
| On STONE (the pickaxe's rock filter: `Rock_` / `Rubble_` ids, gather type Rocks / VolcanicRocks) | the **3x3 window on the face you hit** (perpendicular to that face, centred on the block): the 4 side blocks first (up, down, left, right), then the 4 corners, so N = 4 is a plus and N = 8 is the full 3x3 (python3: 1 + 8 = 9 = 3x3). Only rock blocks in the window break; ore, soil, wood and air in the window are skipped (they are not replaced by others) |
| Which face | the hit face from the break (UNVERIFIED P1); fallback = the axis of the player's look direction |
| Never | placed blocks (`skill:fn:placed`), blocks broken by an ability in the last 5 s (no chains), `ability.disabledWorlds`, a held hammer (section 6), creative |
| Every extra block | a real `performBlockBreak` with the held tool: island / zone protection, Ore-Regrow depletion, Collections, Mining XP all apply (Veinbreaker's downside: no XP on its extras) |
| Fortune on extras | `bonusBlock.fortuneRate` **50 %** (`research/cloud/Tool-Levels-Revision.md` 4 rule 4: extra blocks roll Fortune at half rate) - SkyySkills reads the 5 s ability mark (new `tree:fn:abilityBroken`) |
| Cooldown | none (the levels keep it in check, Skyy's words); `vein.cooldownSec` stays a row, default **0** for Vein Mine |
| Message | none per break (it fires every swing); `/tree quiet` unchanged |

Per-break caps and performance (python3 for the counts):

| Cap | Row | Default | Why |
|---|---|---|---|
| Extra blocks per trigger | `veinmine.cap` | **8** (hard max 8) | Skyy's cap |
| Block reads per trigger | `veinmine.maxReads` | **256** | 9 visited blocks x 26 neighbours = 234 reads worst case (the live flood allows 4000) |
| Search radius | `veinmine.radius` | **3** | a vein of 9 never needs more; the live `ability.maxRadius` 6 stays for Spread / Feller |
| Extra blocks per player per second | `veinmine.budgetPerSec` | **24** | hand speed x 9 = 9 / 18 / 27 / 36 breaks per s at 1-4 hand breaks per s; the budget trims only the 4-per-second case (to 28); the overflow is simply not broken (never queued) |
| One action per player | (code, live `ACTIVE`) | on | no overlap |
| Per world tick | `veinmine.worldPerTick` | **64** extra blocks | 8 players at full Vein Mine in one tick; the rest skip that swing (UNVERIFIED P2 cost per `performBlockBreak`) |

The live Mining S12 node "Vein Burst" becomes the tree's **Vein Mine** node (section 4).

## 3. Tree Feller levels (the one SkyyTrees system)

| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Extra logs on the cut's Y level | 1 | 2 | 4 | 5 | 6 | 10 | **12** | **14** |
| Status | LOCKED 2026-09-25 | | | | | LOCKED | NEW (Question 4) | NEW (Question 4) |

- `feller.logs` grows from 6 to 8 numbers (the live check already accepts up to 20 rising whole numbers, `SkyyTrees/build_skyytrees_0.3.5.py`
  578-580); python3 check: rising and under the `feller.maxPerLayer` safety cap 64.
- Unchanged: same height as the cut only, natural trees with leaves, one shared cooldown `feller.cooldownSec` 3 s (Heartwood's downside
  makes it 6 s while held), Feller logs never trigger Feller, Fortune on Feller logs at 50 %.
- The level used is the summed level of section 4, capped at 8.

## 4. Stacking: tool + gathering tree (+ armor), total capped at 8

Skyy: "a pickaxe without vein mine gets a little from your class, that can stack with you pickaxe". The newest lock (SUM, cap 8) replaces
`research/cloud/Tool-Levels-Revision.md` 8 and `research/cloud/Gathering-Armor-Stats.md` 194-197 (MAX of perk / axe / armor).

| Source | Vein Mine | Tree Feller | How it reaches SkyyTrees |
|---|---|---|---|
| Gathering tree node | Mining S12 **Vein Mine 0-3** (rework of Vein Burst, Question 3) - works with ANY pickaxe (multitool too), never a hammer | Foraging S12 **Tree Feller 0-6** (live, unchanged) - any hatchet or multitool | its own node |
| Held special tool | UT / Mythic ability level (Veinbreaker 2-4, Master Key 3, Burn Notice 4) | Heartwood 1-3, Master Key 3, Clear-Cut 4 | SkyyGear posts `vein.level` / `feller.level` in its "gear" source (the Fortune pattern) |
| Plain crafted axe | 0 | **0 by default** (Question 5: the 2026-10-05 "axes should also get tree feller" as +1 at Cobalt+ tier) | SkyyGear "gear" source |
| Worn gathering set | Onyxium mining full set **+1** (`research/cloud/Mining-Armor-Spec.md` 113 "later") | foraging full sets F4 +1, F5 +2 (Question 6; drafted F2-F5 1-4) | SkyyGear `gear.armor` source |
| Total | sum, **cap 8** (`ability.levelCap` 8) | sum, **cap 8** | SkyyTrees `TreeGather.run` |

Vein Mine stacking (python3: min(8, tool + tree + armor)):

| Tool level | tree 0 | tree 0 + Onyx set | tree 1 | tree 1 + set | tree 2 | tree 2 + set | tree 3 | tree 3 + set |
|---|---|---|---|---|---|---|---|---|
| 0 (any plain pickaxe) | 0 | 1 | 1 | 2 | 2 | 3 | 3 | 4 |
| 2 (Veinbreaker Lv 30) | 2 | 3 | 3 | 4 | 4 | 5 | 5 | 6 |
| 3 (Veinbreaker Lv 37, Master Key) | 3 | 4 | 4 | 5 | 5 | 6 | 6 | 7 |
| 4 (Veinbreaker Lv 44, Burn Notice) | 4 | 5 | 5 | 6 | 6 | 7 | 7 | **8** |

Tree Feller stacking (python3: min(8, tree + tool + armor) -> logs):

| Tree node | no tool, no set | + F5 set (+2) | + Heartwood 2 | + Heartwood 2 + F5 | + Master Key 3 | + Master Key 3 + F5 |
|---|---|---|---|---|---|---|
| 0 | 0 (-) | 2 (2 logs) | 2 (2) | 4 (5) | 3 (4) | 5 (6) |
| 3 | 3 (4) | 5 (6) | 5 (6) | 7 (12) | 6 (10) | **8 (14)** |
| 6 (maxed) | 6 (10) | **8 (14)** | **8 (14)** | 8 (14) | 8 (14) | 8 (14) |

A maxed tree + one helper already reaches 8 - the special tools are how a player gets there BEFORE Foraging 60 (tier VI). The tooltip
shows the total: "Vein Mine 6 (tool 4 + tree 2), max 8".

## 5. Auto Smelt (late tree upgrade + Emberpick + The Burn Notice)

| Part | Rule |
|---|---|
| Tree node (Skyy: "a really late game tree upgrade") | NEW Mining node **Auto Smelt** (`MSmelt`, kind SMELT, 1 level, tier VI + node gate Mining **75**, 3 tokens, 9,600,000 Dust = the S12 last-level cost), on / off with the live node toggle (`<Tree>.off`) so a player can keep raw ore for collections / quests |
| What it does | a paid `Ore_` break: the block's ore drops become the bar (`TreeDefs.barOf`, copper to adamantite; the map grows with Zone 4-5 ores), also the Fortune extras and Vein Mine extras; Prospector's extra-bar roll still rolls on top |
| XP / collections | tree node and Burn Notice: Mining XP as normal, ore collection credited for the ORE broken, Smithing XP 0 (nothing was smelted at a furnace). Emberpick: the same but its downside line (half Smithing XP is paid on its bars - 50 % of the furnace smelt XP - and NO ore collection credit) |
| Never | on non-ore blocks, on placed ore, on ore whose bar does not exist (drops stay raw) |
| How | engine drop swap (UNVERIFIED P3: cancel-and-rebreak, or a drop list hook); SkyySkills' extra drops read a `smelt.mining` flag in the "gear" / "trees" sources and swap by the same map |

## 6. Hammers: solo only (Quarrymaster's Hammer)

Skyy: "hammers wont work great for the server plan, but would be fine for solo. (i wouldnt allow vein mine on a hammer."

| What "solo only" means | How it is enforced |
|---|---|
| The 3x3 area break works only where the hammer setting is ON | Server Setup row `tool.hammers` = **auto** / on / off. auto = ON when the server is a single-player world, OFF on a dedicated server (UNVERIFIED P5; if it cannot tell, the default becomes OFF and the solo pack's ready config sets ON) |
| Never in shared zone worlds even when on | `tool.hammers.offWorlds` (default = the zone worlds + hub, like `ability.disabledWorlds`); Ore-Regrow registry worlds always off (no tunnel-griefing, no 3x3 regen camping) |
| Off = a plain pickaxe | the hammer still mines one block with its level Power / Fortune; tooltip "Area break: solo worlds only (off on this server)" |
| No hammer drops on a server | with `tool.hammers` off the hammer leaves every loot / quest pool; its Mining mastery quest pays the Veinbreaker or coins instead (Question 7) |
| Never Vein Mine on a hammer | the summed Vein Mine level is forced to **0** while a hammer is held (tree node and armor too); no trick, modifier or level-up can add it; the row asserts at build that no hammer row has `vein=` |
| How the 3x3 works | the same face window as Vein Mine stone mode, fixed 8, rock + ore both (no connectivity), real breaks, placed blocks skipped; Walk (Left Alt) held = mine one block (UNVERIFIED P4) |

## 7. Multitools (pack mod, SkyyGear 0.2.18 - already locked)

| Rule (LOCKED 2026-10-10) | Detail for this spec |
|---|---|
| Recipe = 1 pickaxe + 1 hatchet + 1 shovel of the SAME tier (MIT allows our recipe override; credit + licence notice) | crafted multitools roll rarity / reforge like other tools (0.2.17) |
| Both kinds: Mining + Chopping Power, Mining + Foraging Fortune at 85 % speed / 70 % Fortune of the same-tier tool | python3 (0.2 x L x (1 + 2 % x tier) x 70 %): Lv 15 Iron 3.1 -> 2.2; Lv 30 Cobalt 6.5 -> 4.5; Lv 45 Mithril 10.1 -> 7.1 |
| Gate: Mining AND Foraging at the item level | display level = the higher of the two |
| Id detection | their ids start `Tool_Hatchet_Pickaxe_Multitool_` (survey; UNVERIFIED P6) and today match SkyyGear's `Tool_Hatchet_` prefix first = treated as a hatchet only (`SkyyGear/build_skyygear_0.2.17.py` 4038) - 0.2.18 must test `_Multitool_` / the `multi` row flag BEFORE the families |
| Special-tool fit | a multitool is "any pickaxe" AND "any hatchet" for the tree's Vein Mine and Tree Feller nodes; plain multitools carry no tool ability; The Master Key (M1) is the Mythic multitool |

## 8. Where each tool comes from (quest / boss / chest)

Quest ids are proposals in the `research/cloud/SkyyQuests-Zone1-Spec.md` style; bosses from `research/cloud/Zone-Bosses-Ideas.md` and
`research/cloud/Untiered-Mythic-Spec.md` 2.4; the boss UT line = the spec's separate 5 % UT roll next to the Mythic roll.

| Tool | Main source | Extra sources | Server Setup row |
|---|---|---|---|
| T5 Lucky Pick (UT1) | Zone 1 loot chests: the orange bag's TOOL type (vanilla chest extra piece, Unclaimed Luggage I-II) | Job Board weekly reward (later) | `utdrop.toolShare` 15 % of orange bags in a band that has a UT tool |
| T4 Lode-Lamp (UT2) | Rare Monster kills in Zone 1-2 (Aures Rare Monsters pack mod, runtime role ids; the Rusted Drill pattern) | elites' UT roll | `uttool.lodelamp.mobs` |
| T6 Heartwood Hatchet (UT2) | quest `forest2.q01_elder` "The Forest Elder's Request" (Zone 2 edge, Foraging 15) | Unclaimed Luggage II | quest data |
| T8 Reaper's Scythe (UT2) | quest `farm2.q01_festival` "Harvest Festival Paperwork" (Zone 2 farm, Farming 15) | - | quest data |
| T1 Veinbreaker (UT3) | quest `mine2.q01_shaft` "Clear The Collapsed Shaft" (Zone 2 mine, Mining 30) | Goblin Duke (Zone 2 goblin dungeon) UT line 5 % | quest data, `boss.goblin_duke.ut` |
| T7 Sapling's Boon Axe (UT3) | The Broodmother (Zone 2 guardian) UT line 5 % | Zone 2-3 dungeon end chest 8 % (tool type) | `boss.broodmother.ut` |
| T9 Green Thumb Hoe (UT3) | quest `farm3.q01_bench` "Farmer's Workbench Mastery" (Farming 35) | - | quest data |
| T2 Emberpick (UT4) | Zone 3-4 dungeon end chests 8 % (tool type) | quest `mine3.q02_forge` (Zone 3, Mining 45); Ember Warden UT line | `boss.ember_warden.ut` |
| T3 Quarrymaster's Hammer (UT4) | quest `mine3.q05_mastery` (end of the Mining mastery chain) - only while `tool.hammers` is on | none on a server | quest data |
| T10 Tidecaller's Rod (UT4) | fishing quest `dock3.q01_tide` (Zone 3-4 dock) | SkyyFishing treasure catch (UNVERIFIED that a treasure table exists) | quest data |
| M3 The Clear-Cut Policy | The Broodmother Mythic pool (weight 1) | Challenge mode doubles | `boss.broodmother.pool` |
| M1 The Master Key | The Everfrost Yeti Mythic pool (weight 1) | - | `boss.yeti.pool` |
| M2 The Burn Notice | The Ember Warden Mythic pool (weight 1) | - | `boss.ember_warden.pool` |

Quest rewards go through `gear:fn:grant` (grant id + log, `research/cloud/SkyyQuests-Zone1-Spec.md` 330) so a reward is given once per profile.

## 9. Shared rules

- **Tooltip** (vanilla look): "UNTIERED PICKAXE - Lv 37 - Requires Mining 37"; level lines as plain tools; "Vein Mine 3 (total 5 with your
  tree, max 8)"; the orange downside line; Mythic: the purple hook lines.
- **Dupe / loss** (full round - items that could be lost): extras are real engine breaks (one drop roll each, no item copied); ability marks
  stop chains; Lode-Lamp's "vanish after 3 s" is a deliberate loss: the chat warns once per minute when the bag is full (Question 8).
- **Server Setup** (Gear -> Tools, SkyyTrees -> Abilities): `ability.levelCap` 8, `veinmine.*` (section 2), `feller.logs` (8 numbers),
  `tool.hammers`, `tool.hammers.offWorlds`, `bonusBlock.fortuneRate` 50, `utfx.<tool id>`, `uttool.<key>.band`, `utdrop.toolShare`,
  `Mining.MSmelt.*`, `Mining.MVein.max` 3. Times in seconds.

## 10. Build phases + engine probes (all UNVERIFIED)

| Phase | Mods (round size) | Content |
|---|---|---|
| S0 probes | SkyyTreesProbe or a lean probe jar (local) | P1-P9 below |
| S1 Vein Mine + Tree Feller stacking | SkyyTrees 0.3.6 + SkyyGear 0.2.19 + SkyySkills 0.4.31 (FULL round: several mods, saved data) | Vein Mine engine (ore flood + stone window, caps), MVein -> Vein Mine max 3 with a one-time Dust refund of levels 4-5 (python3: B x 3^3 + B x 4^3 = 13,650,000 Dust; the 0.2.4 Sprinter refund pattern), `feller.logs` 8 numbers (one-time migration only if the line still holds the old default), SkyyGear posts `vein.level` / `feller.level`, `bonusBlock.fortuneRate`, `tree:fn:abilityBroken` |
| S2 first UT tools | SkyyGear 0.2.19 (with S1) | T1 Veinbreaker, T6 Heartwood, T5 Lucky Pick rows (per-row band, tool tricks, orange bag tool type), quest grants wait for SkyyQuests |
| S3 Auto Smelt | SkyyTrees + SkyySkills + SkyyGear (full) | Auto Smelt node, T2 Emberpick, drop swap after P3 |
| S4 Multitools | SkyyGear 0.2.18 (already queued, before S1) | section 7; the `multi` flag used by M1 later |
| S5 the rest | SkyyGear + SkyyFishing (+ SkyyTrees for the hammer window) | T3 hammer (after P4 / P5), T4 Lode-Lamp, T7-T10 |
| S6 Mythic tools | SkyyGear + SkyyMobs boss pools (with the boss round) | M1-M3 |

| # | Probe (needs HytaleServer.jar / Assets.zip) | Pass when |
|---|---|---|
| P1 | Does `BreakBlockEvent` / `DamageBlockEvent` carry the hit block FACE? | the stone window can be face-aligned; else the look-axis fallback |
| P2 | Cost of `performBlockBreak` with 8 positions (ms on the world thread, 8 players) | under 1 ms per call; sets `veinmine.worldPerTick` |
| P3 | Swap a block's engine drops (ore -> bar) without a duplicate: cancel + `performBlockBreak` with no drops + give items, or a drop-list hook | one bar per ore, never ore + bar, protection still applies |
| P4 | Read "Walk held" (Left Alt) or crouch on the server for the hammer's single-block mode | readable per swing |
| P5 | Can a plugin tell a single-player (integrated) world from a dedicated server? | `tool.hammers` auto works |
| P6 | Multitools item ids (`Tool_Hatchet_Pickaxe_Multitool_*`, tier names) and whether a pickaxe JSON with a merged Woods tool spec chops at hatchet power | M1 data approach works |
| P7 | A UT tool copy (Recipe removed, `Variant` true) keeps the base pickaxe's gather power and the vanilla swing | breaks rock like its base |
| P8 | How SkyyCollections counts ore (by block or by dropped item) | Auto Smelt credits the ore as section 5 says |
| P9 | Item-entity query + pull for the Lode-Lamp magnet (radius 6, 20 players) | under 0.5 ms per tick |

Note: on Hytale 0.7 block health moves into `BlockHealthSection` (`research/Tool-Levels-Spec.md` 108-109); the extra-break path is unchanged.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is the tool list in 1.2 (zones, abilities, downsides) and the three Mythic tools in 1.3 (Master Key = Yeti, Burn Notice = Ember Warden, Clear-Cut Policy = Broodmother) good to build? | [yes] |
| 2 | Special tools as UT: fixed lines like UT weapons (no modifier reroll), or do they roll and reforge tool modifiers like crafted tools? (the survey said "modifiers still reroll"; the live UT rule says fixed) | [fixed, like every UT] |
| 3 | The tree's Vein Burst (5 levels, 6-14 ore, 40 s cooldown) becomes **Vein Mine 0-3** (N extra blocks, no cooldown), refunding the Dust of levels 4-5 to anyone who has them? | [yes] |
| 4 | Tree Feller levels 7 and 8 (only reachable with tree + tool / armor): 12 and 14 extra logs? | [12 / 14] |
| 5 | Plain crafted axes: no Tree Feller (special tools + tree only), or +1 at Cobalt and up? | [none - special axes + the tree] |
| 6 | Foraging armor Feller: shrink to F4 +1 / F5 +2 now that levels ADD (drafted F2-F5 1-4)? | [yes, F4 +1 / F5 +2] |
| 7 | Hammers: `tool.hammers` = auto (on in single-player, off on a dedicated server); on our server the hammer quest pays the Veinbreaker or coins instead? | [auto; Veinbreaker] |
| 8 | Lode-Lamp downside "drops that do not fit vanish after 3 s" (real item loss) - keep, or change to "drops that do not fit stay where they fell, no magnet"? | [change: no magnet when full] |
| 9 | Auto Smelt node gate: Mining 75 inside tier VI, 9.6 M Dust? | [yes] |
| 10 | Vein Mine on stone: only rock blocks in the 3x3 (ore in the window stays for you to mine)? | [yes] |

## For the local session

| # | Item |
|---|---|
| 1 | Probes P1-P9 (section 10) - one lean probe round before S1. |
| 2 | Check the live player files for `Mining.MVein` levels 4-5 before the S1 refund migration (likely none: tier VI + 15 M Dust). |
| 3 | Confirm in Assets.zip: `Tool_Pickaxe_Cobalt`, `Tool_Pickaxe_Adamantite`, `Tool_Pickaxe_Mithril`, `Tool_Hatchet_Cobalt`, `Tool_Hatchet_Iron`, `Tool_Sickle_Iron`, `Tool_Hoe_Thorium`, and that no vanilla id starts `Tool_Pickaxe_UT_` / `Tool_Pickaxe_Mythic_`. |
| 4 | The boss role ids (Goblin Duke, Broodmother, Everfrost Yeti, Ember Warden) and whether SkyyMobs boss pools accept a tool row. |
| 5 | Aures Rare Monsters role ids for the Lode-Lamp drop (runtime ids only, PACK.md). |
| 6 | SkyyFishing: a treasure loot table for the Tidecaller's Rod, and that `SkyyFishing_Rod_Iron` can be a copy base. |
| 7 | SkyyGear 0.2.18 (Multitools) must test `_Multitool_` before `Tool_Hatchet_` (section 7). |
| 8 | `UT_LO, UT_HI` become per row (`SkyyGear/build_skyygear_0.2.17.py` 3728); `_tool_tier` returns None for special ids - use the base id's tier. |
