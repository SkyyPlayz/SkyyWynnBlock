# Balance pass P6 - Gathering + crafting: collection sizes, tier-up / armor costs, hits per block, crops / totems, smelting / cooking / alchemy, F-pickup tier lock + zone spawns (BUILD-READY spec, 2026-10-21)

Phase P6 of research/Balance-Pass-Spec.md section 8 ("Gathering + crafting: collection sizes, tier-up / armor costs, hits per block, crops /
totems, smelting / cooking / alchemy, F-pickup tier lock + zone spawns"). Mods: SkyyCollections, SkyyGear, SkyySacks, SkyyWorldGen, SkyyCooking
(+ SkyyShards for the totems, see Part 7; SkyySkills: no build, section 8.1). Skyy 2026-10-20/21: "keep going down the list. dont stop until the
entire list is done" + "just go with the recommended on all of them. i need to go to bed." + "run whatever you can in parallel to speed up the
build". Spec only - nothing built, nothing committed. Where answers go: docs/answered/skills.md (gathering / collections / cooking lines),
docs/answered/world.md (zone spawns), docs/answered/gear.md (costs, F-pickup lock); this file holds the plan (the main session adds it to
INDEX.md under research/). Builds ON research/Balance-P3-XP-Spec.md (XP per block / crop / log / dish / brew - NOT changed here) and
research/Balance-P5-Power-Spec.md 1.1 (the Fortune budget per skill - used here as the input, not redone). P5 must be pinned first
(Gear 0.3.35, Trees 0.4.5 ...) and the Cooking 0.1.16 ING_TIER fix.

**Goals used (Skyy's words):** collections "II 10 min, V 1-2 h" + armor craft "about 45 min -1.5 hours" + "mostly idle. late game can be 100%
idle all you have to do manually is upgrade totem poles." (docs/answered/skills.md:191 Q21-Q23); "id never let a player go more than an hour
without at least 1 level up somewhere and some sort of gear upgrade" + "all the gathering skills make money pretty equally, so no one skill is
really better than the other. the further you level it the more money it can make you" (skills.md:187 Q2 / Q4); "lock gathering. your tool wont
let you break much higher than your tier, so lock collecting with F to the same limits as your tool. (and we have 3 tiers per zone, we can
adjust where things spawn, so they really only spawn in their zone. (with leeway on both sides. so in zone 1 you can find crops and trees up to
T5. but no higher. ... the soonest you would see mushrooms is zone 4. (leave ore generation how we set it.)" + "in zone 5 you can find every
crop type, but mostly just the 3 for zone 5" (docs/answered/world.md:118-119); "there isnt a cap on any of the fortunes" (gear.md:288);
Enchanted "Always 100" (tools/skyyench.py:44); no Enchanted costs below Dusk (Skyy 2026-10-18, Gear B:190-195); collection ladder I Enchanted /
II tools / III armor / IV weapons, alloy gear at both V, Enchanted alloys at both VI (RESUME 196, Collections 0.2.28); totem tiers 1 / 1.25 /
1.5 / 1.75 / 2x + "the cost isnt always wheat" (skills.md:159); 12 items a minute "a good starting point ... scale as you upgrade it"
(skills.md:155).

**Legend.** VERIFIED = read in code / live config / Assets.zip (cited; B = SkyyGear/build_skyygear_0.3.34.py, COL =
SkyyCollections/build_skyycollections_0.2.30.py, SAC = SkyySacks/build_skyysacks_0.8.24.py, WG = SkyyWorldGen/build_skyyworldgen_0.7.7.py,
S = SkyySkills/build_skyyskills_0.4.58.py, C = SkyyCooking/build_skyycooking_0.1.15.py, H = SkyyShards/build_skyyshards_0.4.3.py, TT =
tools/tier_tags.py; LIVE = UserData/Saves/NewBetaTest/mods/Skyy_<Mod>/, read only). DERIVED = the scratch model (copy of tools/balance_model.py +
p6_gather.py in tools/dev/scratch/p6spec/, deleted after; its `p6_*` functions go into tools/balance_model.py `--gather`, section 8.6).
PROPOSED = a default this spec picks. UNVERIFIED = needs the game. W = checked on the web 2026-10-21, K = my knowledge, not checked.

---

## 0. For Skyy (plain words)

1. **Collections get about 3x faster** (the main gap the model found: tier II took 27 min of mining, V 4.4 h). New ladder: tier II in
   ~10 min, III ~27 min, IV ~47 min, V ~1.1 h of focused gathering. Every skill gets the same TIME per tier: logs and crops come faster than
   ore, so their collections are a bit bigger to match.
2. **Armor sets cost 45 min of materials in Zone 1, rising to 1.5 h in Zone 5** (longer zones = longer goals). Tool tier-ups cost a third
   of that. Costs now grow with your Fortune - today a Mithril armor set is 4 Enchanted Mithril (minutes at Zone 5 Fortune); after P6 it is
   33. Still plain items below Dusk, Enchanted from Dusk up.
3. **Alloy tiers from Dusk up are paid in Enchanted alloys**, and Enchanted alloys unlock together with the alloy gear (both collections V,
   was VI). Otherwise a Lumen set would need ~3,700 bars and ~8 hours in the Furnace.
4. **The Furnace smelts 4x faster** (a quarter of the vanilla time; the Furnace Charm still cuts more) and holds 1,000 bars in its queue.
   A Zone 1-2 armor set's bars finish while you gather the next ones.
5. **Hits per block:** a fresh tool on its own tier = 3-4 hits, the best kit = 2 hits. Own-tier ore never drops under 2 hits (like
   SkyBlock's soft cap); lower-tier blocks (stone, old ores) can break in one hit.
6. **F pick-up is tier-locked** like breaking: you cannot F-pick a mushroom / F-harvest a crop more than 1 tier above your best hoe or
   sickle (logs / fruit 2 tiers above your hatchet). It uses your best tool of that kind, held or not.
7. **Zone spawns (new land only):** crops, herbs and trees above "zone top + 2 tiers" become one of that zone's own kinds (Zone 1 up to T5,
   Zone 2 T8, Zone 3 T11, Zone 4 T14). Wild mushrooms appear only from Zone 4 (in Zones 1-3 they are removed). Zone 5 keeps every crop, but
   7 in 10 wild crop patches are its own Potato / Onion / Mushroom. Ores unchanged. Already explored land stays as it is.
8. **Money is even per skill - in TIME, not yet in coins.** Every gathering skill now gets the same collection time and the same armor time.
   Coins per hour still differ (Mining ~2-6x the others in Zones 3-5 at today's prices); P7 re-prices logs and crops (table 6.2 gives P7 the
   prices that make them equal).
9. **Totems (farming shard):** idle production climbs with the totem tier: Totem I = 20 % of an active farming hour of its zone ... Totem
   V = 100 %, so late game farming can be fully idle (you only upgrade the totems).
10. **Cooking / alchemy / crop growth:** crop growth stays vanilla; cooking reads every ingredient's tier from the one tier table (the
    queued "ING_TIER v3"); alchemy herbs follow the zone spawn rule; Smithing XP for crafted gear follows the P3 tier factor (Lv 25 unchanged,
    Lv 100 about 4x today).

---

## Research (short; W / K marked)

| Game | What it does | What we take |
|---|---|---|
| Hypixel SkyBlock mining (W: hypixelskyblock.minecraft.wiki/w/Mining_Speed) | ticks to break = round(30 x block strength / Mining Speed), a soft cap of 4 ticks (0.2 s) unless the block breaks in one tick (needs 30x - ores 60x - strength) | **own-tier ore: never under 2 hits** (`gate.minHitsOwn`); lower-tier blocks may insta-break |
| Hypixel SkyBlock collections (K) | per-item ladders (Cobblestone ~50 / 100 / 250 / 1k / 2.5k / 5k / 10k / 25k / 40k / 70k), rare items much shorter ladders; early tiers in minutes, late tiers weeks; Fortune drops DO count | our B / S / R / E letters already copy this; early tiers in minutes; Fortune does NOT count for us (Skills `collections.doubleDrops` false, VERIFIED S:6645) so our ladders can stay short |
| Hypixel SkyBlock minions / Garden (K) | idle production grows with the minion tier and upgrades; late game farming is mostly idle; active farming stays the fastest per hour until the very end | **totem tier -> idle share 20 / 40 / 60 / 80 / 100 %** |
| Wynncraft professions (K) | gathering tiers by profession level, a node's tier needs the matching tool; nodes only in their region | the **zone window + F-pickup lock** |
| Diablo / WoW crafting (K) | crafting costs grow with item level so a fresh set stays a goal at every tier | **costs scale with Fortune** (drops per block), so the time stays 45 min-1.5 h |

Sources (W): https://hypixelskyblock.minecraft.wiki/w/Mining_Speed .

Survey (PROJECT-RULES 2): nothing new is added - every part tunes our own systems. Reference already recorded: GlymeraFarmer (auto plant /
harvest, totem reference, project.md:100), MoreTotems removed (skills.md:160), Farming_Overhaul 2.4.0 in the pack overrides 16 crop blocks
(Zone-Gathering-Spec 2) - our code still reacts by id only; its growth stages may differ from the vanilla numbers below (UNVERIFIED).

---

## Part 1 - Fortune while gathering + drops per block (DERIVED; input from P5 1.1)

The player pays tier T's costs with materials gathered while wearing tier T-1's kit. Expected Fortune = tool 30 x (T-1) (the lifelong +3 a
level, 10 levels a tier, VERIFIED B:7924 / 7955) + the T-1 armor set (P5 1.1: today's 60 / 75 / 90 / 105 at T1-T4, then 25.7 x T) + half of
the T-1 Void Charm and pet budget (17.1 / 12.9 x T) + 20 tree (half of TREE_FORT_MAX 40). 1 Fortune = +1 % of one extra drop (B:1706-1713).

| T | 1 Copper | 2 Iron | 3 Bronze | 4 Thorium | 5 Lead | 6 Dusk | 7 Cobalt | 8 Chromium | 9 Azurvane | 10 Adamantite | 11 Slag | 12 Cinder | 13 Mithril | 14 Titanium | 15 Lumen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| expected Fortune | 0 | 125 | 185 | 245 | 305 | 373 | 444 | 514 | 585 | 656 | 727 | 797 | 868 | 939 | 1009 |
| drops / block D(T) | 1.00 | 2.25 | 2.85 | 3.45 | 4.05 | 4.73 | 5.44 | 6.15 | 6.86 | 7.56 | 8.27 | 8.98 | 9.68 | 10.39 | 11.10 |
| best at end of T (P5) | 160 | 235 | 310 | 385 | 468 | 554 | 639 | 725 | 811 | 897 | 982 | 1068 | 1154 | 1239 | 1325 |

Rates (model GUESS, the same as P3's XP model so XP and costs agree): Mining 900 blocks / h, 25 % ore = **225 ore / h**; Foraging **400 logs
/ h** (Tree Feller); Farming **500 harvests / h** x the crop's mean harvest quantity q (VERIFIED Assets `Drops_Plant_Crop_<X>_StageFinal_Harvest`:
Wheat 1-2, Corn 2-4, Cotton / Rice 1-3, Potato / Onion 2-4, Lettuce / Carrot / Cauliflower / Turnip / Pumpkin / Aubergine 1; the build reads q).
Fortune extras are real items (materials) but NOT collection credit (S:6645 `collections.doubleDrops` false, VERIFIED).

---

## Part 2 - Tier-up + armor costs (SkyyGear ladders)

### 2.1 Today (VERIFIED, LIVE SkyyGear config.properties + B)
- One ladder text per family, "A>B(Id*n+Id*n)>C(...)", paid on the Anvil Upgrade: `lifelong.ladders` (B:7909, pickaxe / hatchet / hoe /
  sickle), `multi.ladders` (B:8089), `can.ladders` (B:8071), `harvester.ladders` (B:8086), `garmor.ladders` (Mining armor, B:7972),
  `garmor.ladders.foraging` / `.farming` / `.fishing` (B:8008 / 8010 / 8012). Gathering armor: only the first set is crafted, every later tier is
  an Anvil tier-up of the previous piece (B:28542).
- Pickaxe (LIVE:453): Copper 25 bars, Iron 75, Bronze 32 + 150 Stick, Thorium 75 + 150 Stick, Lead 75 + 300 Stick, Dusk 64 Dusk bars, Cobalt /
  Chromium / Adamantite / Slag 2 Ench, Azurvane 128 bars, Cinder 192 bars, Mithril / Titanium 3 Ench, Lumen 256 bars.
- Mining armor (LIVE:487): plain tiers 75 bars Head / Hands, 150 Chest / Legs = **450 a set**; Enchanted tiers **1 Ench a piece = 4 a set**.
  Foraging / Farming the same shape with logs / crops (LIVE:519 / 521).
- Rule PLAIN29 (B:7169-7271): tier-ups INTO T1-T5 pay 75 plain base items per Enchanted item; an assert forbids Ench below T6. Ench = 100 base
  (tools/skyyench.py:44). `lifelong.stickCost` 0,0,0,2,4,8,16,32 Enchanted Sticks (B:8100) stays.
- DERIVED: at the expected Fortune a Mithril set (4 Ench = 400 ore) takes **0.18 h** at Zone 5 drops; the model's "one armor set" row
  (targets.md 4) said 2.84 h because it counted no Fortune at all. Both are off target.

### 2.2 THE RULE (PROPOSED)
- **Armor set time by zone:** 0.75 / 0.94 / 1.1 / 1.3 / 1.5 h (Zones 1-5) of focused gathering of that tier's material (Q1). Base items =
  hours x rate x D(T). Split by the P5 slot shares Head 20 / Chest 35 / Legs 30 / Hands 15 %.
- **Tool tier-up** = 1/3 of the armor time (Q2), same rule (pickaxe: the tier's bar / Ench; hatchet: the tier's log part - its bar part stays
  as today; hoe / sickle / harvester / can: the tier's crop part; multitool: its pick + hatchet rows' sum x `multi` as today).
- **Pay:** T1-T5 plain (rounded to 5; PLAIN29 kept), T6+ Enchanted (round(base / 100), at least 1). **Alloy tiers T6+ (Dusk, Azurvane, Cinder,
  Lumen) pay Enchanted ALLOY** (Skyy_Ench_<Alloy>, tools/skyyench.py TABLE_ALLOYS) and the Enchanted alloy unlock moves from VI+VI to V+V
  (Part 3.3; Q5). Bronze (T3) stays plain bars.
- The build computes every ladder text from `p6_armor` / `p6_tool` (section 8.6) and prints the 4 ladders; numbers below are the defaults.
- Combat armor is NOT ours to cost: vanilla / SkyyArmory recipes (Gear only scales stats, B:23026); it comes mostly from bags (P5) - stays
  (Q12).

### 2.3 Result (DERIVED, p6_gather.py)

Mining (225 ore / h; bars for T2-T5 and Bronze; furnace hours at the Part 4 25 % rule, no charm):

| T | metal | set h | set base items | Head / Chest / Legs / Hands | pickaxe | furnace h | today set |
|---|---|---|---|---|---|---|---|
| 2 | Iron | 0.75 | 379 | 75 / 135 / 115 / 55 bars | 125 bars | 0.37 | 450 bars |
| 3 | Bronze | 0.75 | 480 | 95 / 170 / 145 / 70 bars | 160 bars | 0.40 | 450 bars |
| 4 | Thorium | 0.94 | 729 | 145 / 255 / 220 / 110 bars | 245 bars | 0.91 | 450 bars |
| 5 | Lead | 0.94 | 856 | 170 / 300 / 255 / 130 bars | 285 bars | 1.07 | 450 bars |
| 6 | Dusk | 0.94 | 1001 | 2 / 4 / 3 / 2 Ench Dusk | 3 Ench | ~0 (Ench alloy) | 4 Ench |
| 7 | Cobalt | 1.10 | 1346 | 3 / 5 / 4 / 2 Ench | 4 Ench | - | 4 Ench |
| 8 | Chromium | 1.10 | 1521 | 3 / 5 / 5 / 2 | 5 | - | 4 |
| 9 | Azurvane | 1.10 | 1696 | 3 / 6 / 5 / 3 Ench Azurvane | 6 | ~0 | 4 |
| 10 | Adamantite | 1.30 | 2212 | 4 / 8 / 7 / 3 | 7 | - | 4 |
| 11 | Slag | 1.30 | 2418 | 5 / 8 / 7 / 4 | 8 | - | 4 |
| 12 | Cinder | 1.30 | 2625 | 5 / 9 / 8 / 4 Ench Cinder | 9 | ~0 | 4 |
| 13 | Mithril | 1.50 | 3268 | 7 / 11 / 10 / 5 | 11 | - | 4 |
| 14 | Titanium | 1.50 | 3506 | 7 / 12 / 11 / 5 | 12 | - | 4 |
| 15 | Lumen | 1.50 | 3745 | 7 / 13 / 11 / 6 Ench Lumen | 12 | ~0 (was 7.7 h in bars) | 4 |

Foraging (400 logs / h) and Farming (500 harvests / h, q = 1; the build multiplies Farming by the crop's q):

| T | Foraging set (H / C / L / Hd) | hatchet log part | Farming set (H / C / L / Hd) | hoe / sickle crop part |
|---|---|---|---|---|
| 2 | 135 / 235 / 200 / 100 logs | 225 | 170 / 295 / 255 / 125 crops | 280 |
| 3 | 170 / 300 / 255 / 130 | 285 | 215 / 375 / 320 / 160 | 355 |
| 4 | 260 / 455 / 390 / 195 | 430 | 325 / 570 / 485 / 245 | 540 |
| 5 | 305 / 535 / 455 / 230 | 510 | 380 / 665 / 570 / 285 | 635 |
| 6 | 4 / 6 / 5 / 3 Ench | 6 Ench | 4 / 8 / 7 / 3 Ench | 7 Ench |
| 8 | 5 / 9 / 8 / 4 | 9 | 7 / 12 / 10 / 5 | 11 |
| 10 | 8 / 14 / 12 / 6 | 13 | 10 / 17 / 15 / 7 | 16 |
| 12 | 9 / 16 / 14 / 7 | 16 | 12 / 20 / 18 / 9 | 19 |
| 14 | 12 / 22 / 19 / 9 | 21 | 16 / 27 / 23 / 12 | 26 |
| 15 | 13 / 23 / 20 / 10 | 22 | 17 / 29 / 25 / 12 | 28 |

Fishing armor + Fishing tools: unchanged (fishing rework pending, skills.md:187). Soul Cage `upgrade.ladders`: unchanged (combat, P5).

### 2.4 Smithing XP for crafted gear (P3 left it to P6; SkyyGear `xp.craft*`, VERIFIED LIVE:294-304)
Today `xp.craftCurve=1:0.05,10:0.25,15:0.5,20:0.75,25:1.0,35:1.5,40:2.0` (flat after Lv 40), `xp.craft.normal=500 ... mythic=16000, set=4000`.
PROPOSED: `xp.craftCurve` = the P3 tier factor at the band starts `1:1,8:2.11,15:3.6,20:4.91,28:7.43,35:10.04,40:12.15,48:15.95,55:19.68,60:22.59,68:27.67,75:32.52,80:36.23,88:42.59,95:48.56,100:53.07`
and the rarity bases / 6.4 (so Lv 25 pays today's): `xp.craft.normal=80, unique=160, rare=320, legendary=640, fabled=1280, mythic=2560,
set=640` (Q14). Lv 1 Normal 80 (was 25), Lv 40 ~970 (was 1000), Lv 100 ~4,250 (was 1,000).

---

## Part 3 - Collection sizes (SkyyCollections)

### 3.1 Today (VERIFIED COL:1200-1203, LIVE collections.properties:7-10 = the defaults)
`curve.B=50,100,250,500,1000,2500,5000,10000,25000,50000`, `curve.S=50,100,250,500,1000,2500,5000,10000,20000`, `curve.R=25,50,100,250,500,1000,2500,5000`,
`curve.E=10,25,50,100,250,500,1000`. 105 collections (live): Mining B 8 / S 8 / R 5 / E 4, Foraging B 3 / S 24 / R 9, Farming B 2 / S 22 / R 2,
Combat S 7 / R 8 / E 2, Fishing S 1. Rule letters: Copper / Iron S, Thorium / Cobalt / Silver / Gold R, Adamantite / Mithril / Onyxium E
(COL:1147), Oak B, rare woods R (COL:1121). Counting: the exact stacks of a break / F-harvest / F-pickup (COL:753-770), Tree Feller logs
(skills:felled), not Fortune extras. Ladder (0.2.28, COL:1736-1800): I Enchanted, II tool, III armor, IV weapons; alloy tokens on both parents:
III+III Furnace Charm + alloy pickaxe, V+V alloy armor + weapons, VI+VI Enchanted alloy. Server Setup rows `curve.<B|S|R|E>` (COL:8912-8915).
DERIVED at 225 / h: S tier II 27 min, V 4.4 h (targets.md 4: !! x2.1 / x1.8).

### 3.2 THE RULE (PROPOSED) - ~3-4x shorter ladders + one time per skill
New defaults (all collections - Skyy's Q21 answer covers every collection; Q4):

| Letter | I | II | III | IV | V | VI | VII | VIII | IX | X |
|---|---|---|---|---|---|---|---|---|---|---|
| S (was) | 15 (50) | 40 (100) | 100 (250) | 175 (500) | 250 (1000) | 500 (2500) | 1000 (5000) | 2000 (10000) | 4000 (20000) | - |
| B | 15 | 40 | 100 | 175 | 250 | 500 | 1000 | 2000 | 4000 | 8000 (50000) |
| R (half of S) | 8 | 20 | 50 | 90 | 125 | 250 | 500 | 1000 | - | - |
| E (quarter of S) | 4 | 10 | 25 | 45 | 60 | 125 | 250 | - | - | - |

Minutes at 225 items / h (S): I 4, **II 11**, III 27, IV 47, **V 67 (1.1 h)**, VI 2.2 h, VII 4.4 h, VIII 8.9 h, IX 17.8 h. V sits at the low end
of "1-2 h" on purpose: an alloy needs BOTH parents at V, and a balanced player mines ~2.2 h per Zone 1 (12 h x 18 %): 2 x 1.1 h fits.

**NEW row `curve.scale`** (text, "<Category or CollectionId>:<percent>,..."; a collection's tier size = round5(curve[i] x scale / 100), a
CollectionId entry wins over its Category; 100 = absent): default
`Foraging:180,Farming:220,Cobblestone:300,Sandstone:300,Shale:300,Slate:300,Basalt:300,Volcanic:300,Sand:300,Rubble:300` + one entry per crop
collection with q > 1 = round(220 x q) (build-time, from Assets drop lists: Wheat 330, Corn 660, Cotton 440, Rice 440, Potato 660, Onion 660;
the build prints them). Why: logs come ~1.8x and crops ~2.2q x faster than ore, stone ~3x (900 blocks / h, 75 % stone), so the SAME minutes
per tier in every skill (the "all gathering skills equal" goal, in time). Combat / Fishing stay 100.

### 3.3 Ladder change (PROPOSED, Q5)
The Enchanted-alloy tokens (`Skyy_Ench_<Alloy>` recipes, both parents VI) move to V+V for Dusk / Azurvane / Cinder / Lumen (Bronze + Electrum
stay VI+VI). The rewards.properties lines that hold them (`<Parent>.6=...recipe:...Ench_<Alloy>...`) move to `.5` - migrated per line only when
the line still equals the 0.2.30 default (CollRw28Mig kit clone). Reason: Part 2.2 (Dusk+ alloy tiers pay Enchanted alloy).

### 3.4 What a curve change does to saved players (VERIFIED machinery, COL:385-389, 5099, 5436-5549)
A tier is read from the count, so lower curves raise players' tiers at once. Item rewards pay through the normal loop from `_paiditem` up
(never twice); coins / XP / tool points of every newly reached tier are paid on the next credit. The harness proves a 1,000-Copper profile
gets tiers II-V paid exactly once (8.4). Expected one-time windfall for Skyy's test profile: a few tiers per collection (coins 25-400 each).
Enchanted gifts in rewards.properties (tools/skyyench.py GIFT_SHARE 10 % of the step) are NOT re-sized (written lines; P7 may retune).

---

## Part 4 - Smelting (SkyySacks Furnace)

### 4.1 Today (VERIFIED)
Time per unit = vanilla recipe TimeSeconds x (1 - bench tier CraftingTimeReductionModifier) x (1 - Furnace Charm timePct) (SAC:4087-4107
`unitMs`, charm SAC:4619). Vanilla bars (Assets `Ingredient_Bar_*`): Copper 10 s, Iron 14, Gold 10, Thorium 18, Cobalt 18, Adamantite 20,
Mithril 30 (zone metals: SkyyWorldGen recipes, GUESS = their pair; an alloy = both parents' times for 2 bars, WG:1667). Furnace Charm
(SkyyAccessories) 10-50 % time, 15-75 % fuel; Eternal Flame at Charcoal VII. Caps `bench.queueCap` 256, `bench.fuelCap` 1000,
`bench.outputCap` 20000 (SAC:1628-1630). Runs on the wall clock (offline too).
DERIVED: a Thorium set at Part 2 numbers = 729 bars x 18 s = 3.6 h in the Furnace, and the queue holds only 256.

### 4.2 PROPOSED (Q6)
- NEW row `bench.furnacePct` (int 1-100 %, default **25**): Furnace unit time x pct / 100 (Tannery untouched). Applied in `unitMs` before the
  charm.
- `bench.queueCap` default 256 -> **1000** (migrate only if still 256).
- Result (no charm): Iron set 0.37 h, Bronze 0.40, Thorium 0.91, Lead 1.07 h - always under the set's own gathering time, in the background.
  Dusk+ alloy tiers pay Enchanted alloys (one smelt of Ench + Ench), so late furnace time is ~0.
- Smelting Fortune (SAC:661-690, the tree's Smithing.SSmelt) unchanged.

---

## Part 5 - Hits per block (SkyyGear hit gate)

### 5.1 Today (VERIFIED B:21023-21145, 28296-28313, 7292-7295, 6934)
Own-tier hit = max(vanilla, ORE_BASE 0.25 x 1.4^(tool T - ore T)) x (1 + Breaking Power) (tool lines `lifelong.perkSpeed` 5 % a level, cap
10 x (internal tier + 1) levels; gathering armor `garmor.powerPct` 25 + 10 a tier %; accessories; tree), x slowF when under-tier (one pick
step below 0.4, two 0.1; ore is never refused, logs refused 3+ up, crops 2+ up: `GearLL.decideI` B:21060-21093). Power clamp `tool.power.max`
1000 (a sanity guard only).

### 5.2 Result + PROPOSED cap (DERIVED p6_hits; blocks / h = 3600 / (2.4 s walk + hits x 0.4 s swing), GUESS timings)

| T | fresh tool (armor only) | +5 line levels | best (all lines) | uncapped best | blocks / h fresh / best |
|---|---|---|---|---|---|
| 1 | 4 | 3 | 3 | 3 | 900 / 1000 |
| 3 | 3 | 3 | 2 | 2 | 1000 / 1125 |
| 6 | 3 | 2 | 2 | 1 | 1000 / 1125 |
| 9 | 2 | 2 | 2 | 1 | 1125 / 1125 |
| 15 | 2 | 2 | 2 | 1 | 1125 / 1125 |

NEW row `gate.minHitsOwn` (int 0-10, default **2**, 0 = off): on the pickaxe path, a block at or above the tool's tier never takes fewer
hits (the hit damage is clamped to 1 / minHitsOwn x the block's health share - the builder clamps `d1` in GearToolHitSys after the slowF line).
Lower-tier blocks (stone, old ores) may insta-break. Keeps Mining at 900-1,125 blocks / h, the P3 XP model's 900 (+25 % at best kit is the
reward for Breaking Power); uncapped late game would be ~1,300 / h (+45 % XP and coins). Logs / crops: no cap (Tree Feller / soft blocks).
Q7.

---

## Part 6 - Money per skill + the coin warning for P7 (DERIVED)

### 6.1 Equal in TIME (this phase)
Collections (3.2 scale), armor + tool costs (2.2: per-skill rate) and XP (P3) all use the same per-skill rates, so an hour of Mining, Foraging
or Farming gives the same collection progress and the same share of a gear tier.

### 6.2 Coins per hour at TODAY's prices (model ZONE_GATHER, x D(T) at the zone's middle tier, Bazaar sell x 0.9)

| Zone | Mining | Foraging | Farming (q 1.5) | log price that equals Mining | crop price that equals Mining | target coins / h (targets.md 3) |
|---|---|---|---|---|---|---|
| 1 | 27.6k | 16.2k | 18.2k | 34 (today 20) | 18 (12) | 833 |
| 2 | 188k | 131k | 98k | 129 (90) | 69 (36) | 4.3k |
| 3 | 824k | 478k | 299k | 372 (216) | 198 (72) | 31k |
| 4 | 3.6M | 1.7M | 0.8M | 1223 (576) | 652 (144) | 109k |
| 5 | 13.7M | 2.2M | 2.8M | 3653 (576) | 1948 (400) | 388k |

**For P7 (not done here):** with P5's Fortune every raw item is worth ~D(T) x less per hour of work; coins per hour at today's prices are
x25-35 over the targets. P7 prices raw items ~ target coins / h / (items / h x D(T)) per skill, logs and crops at the ratio columns above.
The collection tier coins (`tier.coins`) are also P7's.

---

## Part 7 - Crops, totems, idle farming (SkyyShards 0.4.4 - added to P6 because the P6 row names "crops / totems")

### 7.1 Today (VERIFIED)
- Crop growth = vanilla (Assets `BlockType.Farming.Stages`, game-time units): Wheat ... Rice 86,400 to ripe, 75,900 to regrow; Chilli regrow
  56,925; Tomato regrow 45,540; Potato 124,350 / 113,850; Onion 252,000 / 241,500. No mod has a growth key (Islands catch-up only). Farming_Overhaul
  (pack) overrides these blocks (its numbers UNVERIFIED).
- Totems (H): `totem.rate1..5` 1 / 1.25 / 1.5 / 1.75 / 2 items / min (H:650), range 3-11, `totem.workerMax` 12 / min (H:651), support 5-25 %,
  `totem.upCost=1:10,2:25,3:50,5:100` (H:660), island factor 1 / 1.6 / 2.4, pads 3 / 4 / 5, `shard.xpPercent` 50, offline 3 days, storage caps.
  DERIVED: one Totem I worker on a Small island = 60 items / h vs an active Zone 1 farming hour of ~1,700 crop items (500 x q 1.5 x D 2.25) = ~3.5 %.

### 7.2 THE RULE (PROPOSED, Q13)
A full farming shard (every slot island at its largest size, every pad filled) with all totems at tier k produces **20 / 40 / 60 / 80 / 100 %**
(k = I..V) of an active farming hour of the zone that totem tier matches (Totem k ~ Zone k: 500 x q x D(3k-1)), per crop. The Shards builder
measures today's full-shard production in its harness (the real `ShProd` maths) and scales `totem.rate1..5` and makes `totem.workerMax` a
per-tier list `12,24,48,96,192` (12 = Skyy's starting point, "scale as you upgrade"). `shard.xpPercent` 50 stays (idle XP at half). Totem
tier-up costs follow Skyy's "not always wheat": `totem.upCost` counts stay, paid in the Enchanted crop of the island's crop (already the
fitting-item rule, skills.md:159 - the builder checks).
Growth times stay vanilla (Q15). Active farming stays the fastest per hour until Totem V.

---

## Part 8 - F-pickup tier lock + zone spawns

### 8.1 F-pickup tier lock (SkyyGear; Q8)
Today (VERIFIED): breaking is gated in `GearToolHitSys` (DamageBlockEvent) and crop F-harvest in `GearLL.useNo` (UseBlockEvent$Pre,
B:21276-21291 - by the HELD item, hands = Crude); the F-pickup of a loose block (mushrooms, rubble, fruit, herbs) builds `BreakBlockEvent(null
item)` (`BlockHarvestUtils.performPickupByInteraction`, research/Tool-Levels-Spec.md 341-349) and nothing gates it (no handler in B, SAC, COL).
PROPOSED:
- NEW `GearPickLockSys` (one registerSystem) on BreakBlockEvent with a null item: block tier from the same table `decideI` uses + tier_tags for
  loose items (Mushroom caps T15, herbs Health / Mana / Stamina 1-2-3 = T2 / T5 / T8, wild fruit by its log tier); family -> the player's BEST
  owned lifelong tool of that family (held, hotbar, inventory, Void: Farming = hoe / sickle / harvester / multitool hoe, Foraging = hatchet /
  multitool, Mining = pickaxe / multitool); refuse with the same rule (crops / mushrooms / herbs 2+ tiers up, logs / fruit 3+ up) = cancel +
  the hit gate's popup text ("Needs a T14 hoe or better").
- `useNo` reads the same best-owned tier (max of held and owned) instead of the held item only (a T10 hoe in the bag lets bare hands harvest T11).
- NEW row `gate.pickup` (bool, default true). No tier = never refused. Creative skipped. A refused pickup gives nothing (Sacks / Collections see
  no event).
- SkyySkills: no build - its F-harvest XP only follows a successful event; `collections.doubleDrops` stays false (crosscheck asserts).

### 8.2 Zone spawns (SkyyWorldGen 0.7.8; Q9-Q11)
Today (VERIFIED WG): the zone world = the vanilla Default generator, masked into islands (`WgZ2Isles.maskWith` WG:5322, per new chunk);
Zone 1-4 = vanilla land classes 1-4, **Zone 5 = class 4 again** (WG:1245-1250); no own crop / tree / mushroom placement; decoration
`decorate` WG:4949 (flowers / deco only); ores = `ores` + `mirror` (unchanged, Skyy). Vanilla world-gen files reference (Assets
`Server/World/Default/**/Zone<n>`, reference counts, VERIFIED): Zone1 Wheat, Carrot, Corn (T4), Pumpkin (T7), Potato (T13), Mushroom (T15, 195
refs), herbs; Zone 2-4 Wheat ... Chilli / Cotton / Aubergine + many Mushroom; trees Zone2 Dry, Zone3 Spiral / Fir, Zone4 Jungle / Banyan /
Camphor (T13-14), Petrified, Crystal (T15), Oak / Aspen. Which trees vanilla Zone 1 spawns: UNVERIFIED (prefab refs).

PROPOSED - one block-id remap pass in `maskWith` right after `decorate` (new chunks only, chunk-local, deterministic):
- **Window:** zone z may hold tiers up to `3z + 2` (Z1 T5, Z2 T8, Z3 T11, Z4 T14; Z5 all). Lower tiers stay ("leeway on both sides").
- **Crops + herbs above the window** -> one of the zone's own 3 crops (`hash(x >> 3, z >> 3)` picks per 8x8 patch so a patch stays one
  crop; herbs -> the same herb's in-window grade). The remap maps every state variant id of the crop (Stage1 .. StageFinal) to the same state of
  the target (UNVERIFIED that wild crops are separate state ids - probe P6-0).
- **Mushrooms** (every id of the Mushroom collection: Cap / Common / Flatcap / Glowing / Shelve, COL Mushroom line) in Zones 1-3 -> air
  (Q9; giant mushroom-tree blocks `Plant_Crop_Mushroom_Block_*` are not collectable and stay). Zone 4-5 keep them.
- **Zone 5:** 7 in 10 wild crop patches -> Potato / Onion / Mushroom (by the patch hash); the rest stay as generated (every crop type).
- **Trees above the window** (Zone 4 Crystal T15; any Zone 1-3 tree found by the probe) -> the zone's top own species: every
  `Wood_<X>_Trunk / _Trunk_Full / _Branch_* / _Roots` and `Plant_Leaves_<X>*` id to the target's same suffix (the build asserts every target id
  exists in Assets; shapes stay, textures change; chunk-local because each block maps alone).
- **Table:** built at build time from tier_tags (LOGS, CROP_LADDER, MUSHROOM_ROWS, herbs) + Assets ids, written as Server Setup rows
  `zones.remap.<1-5>` (text "from:to,..."; empty = off) and `zones.spawnWindow` (int 0-15, default 2 = the +2 leeway; -1 = off),
  `zones.z5OwnPct` (0-100, default 70). The build prints the table.
- **Probe P6-0 (builder, harness):** run the zone generator's chunk path in the harness on 64 chunks a zone (the 0.7.x harness already
  generates masked chunks) and print id counts per zone before / after the remap; if the bare-JVM harness cannot run vanilla generation, an
  admin `/wg spawns` (setPermissionGroups(new String[0]) + requirePermission) prints the counts of loaded chunks for Skyy's test.
- Explored chunks are never rewritten (Q11); there the F-pickup lock (8.1) keeps out-of-tier items out of reach.

---

## Part 9 - Cooking + alchemy

### 9.1 Cooking (SkyyCooking 0.1.17 on 0.1.16)
Today (VERIFIED C): `ING_TIER` (C:2185) is a 4-entry legacy dict feeding only `DIFF_TIER`; P3's dish tier already reads tier_tags
(`_TT15.tier(i) or 1`, C:2330-2337); 0.1.16 adds Mango / Coconut / Tomato / Turnip. PROPOSED = the queued **ING_TIER v3**: delete the dict,
`DIFF_TIER` and the P3 tier read the same tier_tags lookup; the build asserts every dish ingredient has a tier or sits in an explicit
`T1_INGREDIENTS` list (Salt, Flour, Dough, Spices, Milk, Egg, Cheese, Fish_Raw ...), printing the dish -> tier table. Dish XP rows = P3
(`xp.<dish>`, unchanged); buff numbers unchanged (Strength cap 20 %, 10 min cap, OVER_CAP C:1081). Cook times stay vanilla (1 / 2 / 5 s).
No migration (code-only change; the P3 rows stand).

### 9.2 Alchemy (SkyySkills - no build)
Brew times vanilla (0.5-1 s queued), effects vanilla (Assets), XP = P3 `alchemy.tierXp` + rows. P6 only: herbs follow the zone window (8.2) and
the F-pickup lock (8.1). Potion numbers stay for the Wynn-elements / food-vs-potion work (skills.md:84).

---

## Part 10 - The 1-hour rule (DERIVED)

Per tier (Zone 1 = 4 h of play) a gatherer meets in each skill: collection tiers I-V (5 level-ups in 67 min of that skill), 4 armor pieces
(each its own upgrade: Head 20 % of 45 min = 9 min ... Chest 16 min) and 1 tool tier-up (15 min). A balanced player (Mining 18 % / Foraging
15 % / Farming 10 %) spends ~43 / 36 / 24 min a tier in them, so at least one gathering upgrade (piece, tool or collection tier) lands every
~15-20 min of gathering; with P5's gear checks (0.72 h p90) and P3's levels the rule holds. Zones 4-5 tiers are longer (5.3 / 6.7 h) and the
armor goal grows with them (1.3 / 1.5 h) - still a piece every 20-25 min of that skill.

---

## Part 11 - Files, keys, Server Setup rows, migrations, checks

One FULL round (saved data via config migrations, several mods, costs that could lose items). Build -> adversarial review (lenses: lost /
duplicated items in the ladder + reward catch-up; migrations; world-gen safety: no saved chunk rewritten, chunk-local remap) -> fix ->
crosscheck -> pin -> deploy, all TOGETHER (no FLOOR: each rolls back alone - migrated config lines keep the P6 numbers and Server Setup ->
Changes has Undo; Collections 0.2.31 + Gear 0.3.36 should still roll back together because the Enchanted-alloy V tokens and the Enchanted-alloy
ladder costs belong together - add a go-together comment in tools/deploy_set.py).

### 11.1 Versions + patches (derive from the SET pin; new patch script each; never edit generated scripts)

| Mod | From -> to | Patch | Changes | Anchors to grep |
|---|---|---|---|---|
| SkyyCollections | 0.2.30 -> **0.2.31** | `tools/collections_0_2_31_patch.py` | 3.2 curves + `curve.scale` (tier-size lookup + Server Setup row + CollKit check), 3.3 Ench-alloy tokens V+V | `CURVES = {` COL:1200, curve rows COL:8912-8915, `CollKit.checkCurve` COL:9110, ladder `A28` / `CHARM28` COL:1741-1752, `_g28(` COL:1759, `RW_MARK9` COL:1928, `CollRw28Mig`, tier lookup near COL:5099 |
| SkyyGear | 0.3.35 -> **0.3.36** (rebase on P5's 0.3.35; anchors exist in 0.3.34) | `tools/gear_0_3_36_patch.py` | 2.2 ladder texts from p6 rules (pickaxe / hatchet / hoe / sickle / multi / can / harvester / garmor Mining / Foraging / Farming), Ench-alloy pay for Dusk+, 2.4 craft XP, 5.2 `gate.minHitsOwn`, 8.1 `GearPickLockSys` + `useNo` best-owned + `gate.pickup` | `LL_LADDER_DEF` / `lifelong.ladders` B:7909, `MT_LAD_DEF` B:8089, `CAN_LAD_DEF` B:8071, `HARV_LAD_DEF` B:8086, `GA_LADDER_DEF` B:7972, `garmor.ladders.foraging` B:8008, `PLAIN29` B:7169-7271, `_lle(` B:6440-6540, `XC_MARK` B:3494, `xp.craftCurve`, `GearToolHitSys` B:28296, `GearLL.decideI` B:21060, `GearLL.useNo` B:21276, `migrateP4` B:15512 (clone for `migrateP6`) |
| SkyySacks | 0.8.24 -> **0.8.26** (0.8.25 = the parked off-hand refill, Skyy "skip for now" - not included) | `tools/sacks_0_8_26_patch.py` reading build_skyysacks_0.8.24.py | 4.2 `bench.furnacePct`, `bench.queueCap` 1000 | `unitMs(` SAC:4087, caps SAC:1628-1630, `SackMig0824` SAC:12773 (clone `SackMig0826`) |
| SkyyWorldGen | 0.7.7 -> **0.7.8** | `tools/worldgen_0_7_8_patch.py` | 8.2 remap pass + rows + probe | `maskWith` WG:5322, `decorate` WG:4949 / call WG:5559, `Z6_GROUND` WG:1282, `CFG_TEXT` WG:6064-6110, rows ~WG:7536, `decProp(` WG:6299 |
| SkyyCooking | 0.1.16 -> **0.1.17** | `tools/cooking_0_1_17_patch.py` | 9.1 ING_TIER v3 | `ING_TIER` C:2185 (0.1.16 line moves), `DIFF_TIER`, `p3_tier` C:2330 |
| SkyyShards | 0.4.3 -> **0.4.4** | `tools/shards_0_4_4_patch.py` (or the mod's own pattern - read the header) | 7.2 rates + workerMax per tier | `RATE_DEF` H:650, `totem.workerMax` H:651 / 925, rows H:1246-1250, `UP_DEF` H:660 |
| SkyySkills | 0.4.58 (no build) | - | crosscheck asserts `collections.doubleDrops` false and the P3 rows | S:6645 |

### 11.2 Server Setup rows (tools/skyycfg.py, KEEP=10; Menu-Pattern pages; times in seconds)

| Mod -> page | Row (key) | Type / range | Default |
|---|---|---|---|
| Collections -> Curves | Bulk / Standard / Rare / Elite curve (existing `curve.B/S/R/E`) | text | 3.2 |
| Collections -> Curves | Collection size by skill / collection (`curve.scale`) | text "Id:%" | 3.2 |
| Gear -> Tools | Tool / armor ladders (existing rows) | text | 2.3 (built) |
| Gear -> Tools | Fewest hits on own-tier ore (`gate.minHitsOwn`) | int 0-10 | 2 |
| Gear -> Tools | F pick-up follows your best tool (`gate.pickup`) | bool | true |
| Gear -> XP | Craft XP curve / per rarity (existing `xp.craftCurve`, `xp.craft.*`) | text / int | 2.4 |
| Sacks -> SkyyVoid and Crafting | Furnace time % (`bench.furnacePct`) | int 1-100 | 25 |
| Sacks -> SkyyVoid and Crafting | Bench queue size (existing `bench.queueCap`) | int 1-10000 | 1000 |
| WorldGen -> Zones | Spawn leeway tiers (`zones.spawnWindow`), Zone 5 own-crop % (`zones.z5OwnPct`), remap per zone (`zones.remap.1`..`5`) | int -1-15 / int 0-100 / text | 2 / 70 / built |
| Shards -> Totems | Totem speed per tier (existing `totem.rate1..5`), worker cap per tier (`totem.workerMax`, now a list) | dec / text | measured (7.2) / 12,24,48,96,192 |

### 11.3 One-time migrations (PROJECT-RULES 4; clone the reviewed kits: Collections `CollRw28Mig` / `CollEnch28Mig`, Gear `migrateP4`, Sacks `SackMig0824`, Shards' newest)
- Only lines still holding the EXACT previous default change (a ladder / table text only when its whole old default matches); a hand-edited
  value is kept + one INFO line; History copy verified first; one config-changes.log line each (Undo in Server Setup -> Changes); bytes + line
  endings kept; a java.util.Properties check that only the planned keys differ; run-once marker written LAST (`Balance P6 gathering
  (SkyyCollections 0.2.31)` / `(SkyyGear 0.3.36)` / `(SkyySacks 0.8.26)` / `(SkyyShards 0.4.4)`); a fresh file carries it; new keys appended
  (absent = default). WorldGen: new keys only (its live file is still the 0.6 shape, missing keys default in code - no migration).
- Collections: the 4 `curve.*` lines (LIVE = the defaults -> migrate), `curve.scale` appended; rewards.properties: the Ench-alloy recipe
  tokens `.6` -> `.5` per matching default line. Gear: every ladder row above (LIVE lifelong.ladders = the 0.3.29 plain-below-Dusk default ->
  migrate; any row P5's migrateP5 touched is compared against 0.3.35's default), `xp.craftCurve` + 7 `xp.craft.*`. Sacks: `bench.queueCap` 256.
  Shards: `totem.rate1..5`, `totem.workerMax` 12 -> the list.
- Copy the live files to `tools/dev/scratch/p6b/` and run each migration in the harness there (LIVE check).
- **Saved data:** nothing rewritten. Collection counts stay; tiers re-read (3.4). Gear items unchanged (a tier-up already paid stays paid).
  Saved world chunks unchanged (8.2: new chunks only).

### 11.4 Harness checks (each mod's bare-JVM test, -Xverify:all, then all jars in one JVM)
1. Collections: tier sizes = round5(curve x scale) for Copper / OakLog / Corn / Cobblestone / Thorium; a profile with 1,000 Copper and
   `_paiditem` 2 gets tiers III-V items + coins + tool points ONCE (re-settle pays 0); `curve.scale` bad text -> WARN + default; Ench-alloy V token
   needs both parents at V.
2. Gear: the ladder texts parse (GearUp) and match table 2.3 +-5 %; no Ench below T6 (PLAIN29 assert kept); Dusk+ alloy rows name
   `Skyy_Ench_<Alloy>`; a tier-up with the exact items consumes them once (count before / after); `gate.minHitsOwn` 2: own-tier ore at
   best kit needs 2 hits, a 2-tiers-lower ore 1; `GearPickLockSys`: a null-item BreakBlockEvent on a T15 mushroom with a best-owned T10 hoe
   is cancelled, with a T14 hoe in the Void it passes; creative skipped; `gate.pickup` false = passes.
3. Sacks: unitMs x 0.25 (Copper bar 2.5 s, charm 50 % -> 1.25 s); queue of 1,000 accepted, 1,001 refused with the cap text; offline replay of
   1,000 Thorium bars = 1.25 h.
4. WorldGen: the remap table (printed) only maps above-window ids; every target id exists; a masked chunk of each zone: no crop / tree id above
   the window, no Mushroom-collection id in Zones 1-3, Zone 5 own-crop share 70 % +-10 over 64 chunks; the same seed gives the same chunk twice
   (deterministic); ore counts identical to 0.7.7 (Skyy: ores unchanged).
5. Cooking: every graded dish's tier = max ingredient tier (table printed); 0.1.16's four ids tagged.
6. Shards: full-shard production at tier I..V = 20 / 40 / 60 / 80 / 100 % +-10 % of 500 x q x D(3k-1) for Wheat and Corn.
7. Migrations on fresh / live copy / hand-edited / half-migrated files (marker last).
8. Crosscheck: no lang key written twice (`tools/ci/langdup.py`), tier tags for any new id (none expected), SkyySkills `collections.doubleDrops`.

### 11.5 Model check (DERIVED - the numbers hit the targets)

| Target (source) | Today (model) | P6 | OK |
|---|---|---|---|
| Collection II ~10 min (A:191 Q21) | 27 min | 11 min (every skill, via `curve.scale`) | yes |
| Collection V 1-2 h (A:191 Q21) | 4.4 h | 1.1 h | yes |
| One armor set 45 min-1.5 h (A:191 Q22) | 2.84 h model / 0.18-1.2 h with Fortune | 0.75 h (Z1) .. 1.5 h (Z5), every skill | yes |
| No hour without a gear upgrade (A:187 Q2) | P5 0.72 h | + a gathering upgrade every ~15-25 min of gathering | yes |
| All gathering skills equal (A:187 Q4) | Mining 1.7-6x others | equal in time (collections, costs, XP); coins -> P7 (6.2) | time yes / coins P7 |
| Late game farming fully idle (A:191 Q23) | ~3.5 % at Totem I, flat | 20 .. 100 % by totem tier | yes |
| Zone spawns (world.md:118-119) | Zone 1 has T7 / T13 / T15 crops | window +2, mushrooms Zone 4+, Z5 70 % own 3 | yes (new land) |
| F pick-up locked like breaking (world.md:118) | not gated | gated, best-owned tool | yes |
| Furnace never the bottleneck | Thorium set 3.6 h, queue 256 | <= 1.07 h, queue 1000, Dusk+ ~0 | yes |
| Blocks / h stays near the P3 model (900) | ~1,300 uncapped late | 900-1,125 | yes |

### 11.6 balance_model.py (the P6 builder adds `--gather`, AFTER the P5 commit - P5 is editing it now; never in parallel)
Port from the scratch file (deleted with tools/dev/scratch/p6spec/; rebuild from this spec): `P6_ZONE_H`, `P6_RATE`, `P6_ARMOR_H`,
`P6_TOOL_SHARE`, `P6_SLOT`, `P6_ARMOR_TODAY`, `P6_ALLOY`, `P6_SMELT_S`, `P6_FURNACE_PCT`, `P6_CURVE_NEW`, and the functions
`p6_zone(t)`, `p6_best_fortune(t)`, `p6_exp_fortune(t)`, `p6_drops(t)`, `p6_items(skill, t, hours)`, `p6_pay(t, base)` (T<=5 plain round-5, T6+
Ench round(base/100) >= 1), `p6_armor(skill, t)`, `p6_tool(skill, t)`, `p6_coll_minutes(curve, tier, rate=225, scale=100)`,
`p6_furnace_h(t, bars, pct, charm)`, `p6_hits(t_tool, t_block, bp_pct, min_own=2)` (= ceil(1 / (0.25 x 1.4^(tool-block) x (1 + bp/100))),
min_own on own-or-higher tier), `p6_blocks_h(hits, swing=0.4, overhead=2.4)`, `p6_md()` (prints Parts 1, 2.3, 3.2, 5.2, 6.2). Hook them into
`build()` section 4: "Collection tier II" / "V" use `p6_coll_minutes(P6_CURVE_NEW["S"], ...)`, "One armor set" uses `P6_ARMOR_H` (target
per zone) vs the built ladder; `--gather` writes "### 8. Gathering + crafting" into research/balance/targets.md; `--check` exits 1 when a
row fails. The Gear build imports nothing from the model (it re-computes the same numbers itself and asserts them against 2.3).

### 11.7 In-game test steps (TEST-CHECKLIST after deploy)
1. `/collections`: Copper (or any started collection) shows the new sizes (II = 40); mine Copper for 10 min with a stopwatch: tier II.
2. Oak Log II = 70 logs, Wheat II = 130 (scale); Server Setup -> Collections -> Curves shows `curve.scale`.
3. Anvil Upgrade: Iron Mining armor Chest asks 135 Iron bars; a Cobalt piece asks 3-5 Enchanted Cobalt; the Dusk pickaxe asks 3
   Enchanted Dusk (and Dusk V+V shows the Enchanted Dusk recipe).
4. `/craft` Furnace: 100 Copper bars finish in ~4 min (was ~17); queue 1,000 accepted.
5. Own-tier ore with a full gathering set: never 1 hit; stone breaks in 1.
6. Hold a sword, F a ripe crop your best hoe allows: it harvests. F a Zone 4 mushroom with a Zone 1 hoe: refused with the popup.
7. Fly to NEW land in Zone 1: no pumpkins / potatoes / mushrooms; Zone 5 new land mostly Potato / Onion / Mushroom. (`/wg spawns` if built.)
8. Farming shard: Collect after 1 h shows the Totem tier's share (Totem I ~20 % of what an hour of hand farming gives).
9. Server Setup -> Changes lists every migrated line with Undo.

### 11.8 UNVERIFIED
Real rates (ore / logs / crops per hour, Vein Mine extras, swing time, walking) - every time number rests on the model's 225 / 400 / 500 GUESS;
whether vanilla wild crops are separate block-state ids (remap); which trees vanilla Zone 1-3 land spawns; whether the null-item
BreakBlockEvent can be cancelled cleanly (no ghost item, no client desync); real-time length of a game day (crop growth in real minutes);
Farming_Overhaul's growth numbers; zone metals' smelt times (Lead / Chromium / Slag / Titanium); full-shard production today (7.1 is one
worker); whether each Vein Mine / Tree Feller block counts for collections (Trees credit felled logs: yes; Vein Mine: not checked); whether
the hit gate's `d1` clamp sees block health in the same units as ORE_BASE.

---

## Questions for Skyy (each with today's default in [brackets])

1. **Armor set = 45 min of materials in Zone 1, growing to 1.5 h in Zone 5** (your 45 min-1.5 h range spread over the zones)? [yes]
2. **Tool tier-ups cost a third of the armor set** (15-30 min of materials)? [yes]
3. **Costs grow with Fortune** (a Mithril set goes from 4 to ~33 Enchanted Mithril, so it stays ~1.5 h)? [yes]
4. **Shorter collection ladders for EVERY collection** (II ~10 min, V ~1.1 h), with logs / crops / stone sized to take the same time as ore? [yes]
5. **Enchanted alloys unlock at V+V** (with the alloy gear, was VI+VI) and Dusk / Azurvane / Cinder / Lumen tier-ups cost Enchanted alloys? [yes]
6. **Furnace 4x faster** (25 % of vanilla time, the charm still on top) and a 1,000-bar queue? [yes]
7. **Own-tier ore always needs at least 2 hits** (lower tiers can be one-hit)? [yes]
8. **F pick-up / F-harvest uses your BEST owned tool of that kind** (held or not), same tier limits as breaking? [yes]
9. **Wild mushrooms in Zones 1-3:** removed in new land (they appear from Zone 4)? [removed] (alternative: swap them for flowers)
10. **Zone window = zone top + 2 tiers** (Z1 T5, Z2 T8, Z3 T11, Z4 T14), lower tiers allowed, Zone 5 = 70 % its own 3 crops? [yes]
11. **Already explored land stays as it is** (only new land follows the zone rules; the F lock covers the rest)? [yes]
12. **Combat armor recipes stay vanilla** (combat armor mostly from bags / buying; only gathering armor follows the 45 min-1.5 h rule)? [yes]
13. **Totem idle share 20 / 40 / 60 / 80 / 100 %** of an active farming hour by totem tier (fully idle at Totem V), idle XP at half? [yes]
14. **Smithing XP for crafted gear follows the tier factor** (Lv 25 the same, Lv 1 x3, Lv 100 ~x4)? [yes]
15. **Crop growth times stay vanilla** (Onion ~3 game days; totems / islands handle idle)? [yes]
