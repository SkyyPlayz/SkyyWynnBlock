# Watering Can Progression - spec (2026-10-27)

Where this sits: `research/` (specs; INDEX.md). Skyy's words: `docs/answered/gear.md` (last line, 2026-10-27). Earlier can spec:
`research/Watering-Can-Harvester-Spec.md`. Answers to the open questions below go to `docs/answered/gear.md` (`python tools/qa_append.py`).
Build: one SkyyGear full round (section 9), then a small SkyyShards round. Status: SPEC, nothing built.

## 1. Goal (Skyy's words)

> "can we figure out a way to get more of a progression feel to the watering can? rais the caps, maybe add more upgrades. reduce how fast
> plants grow a little, and increase how fast the soil goes dry after watering a lot, so you get to water more often. but increase the
> capacity of the starter watering can a bit. and reduce how long fertilizer stays, so you get to water a lot more, and its buffs feel more
> useful as you level it, with it increasing the speed of growth, and leaving fertilizer, is probably swap out the one that makes the
> watering last longer, with more buffs, so watering is more of a manual speedup, with extra buffs/rewards or something."

In one line: watering becomes an active, repeated job. Every time you water dry soil you get a growth push and a chance at rewards. The can's
upgrade caps rise with every tier-up. Lasting Water goes (it made you water less), and better buffs take its place.

## 2. What is there today (gathered read-only, 2026-10-27)

### 2.1 SkyyGear 0.3.48 lifelong watering can (`SkyyGear/build_skyygear_0.3.48.py`)

| Thing | Today | Where |
|---|---|---|
| Ladder | 16 steps: Crude (T1), Copper (T1), Iron T2, Bronze T3, Thorium T4, Lead T5, Dusk T6, Cobalt T7, Chromium T8, Azurvane T9, Adamantite T10, Slag T11, Cinder T12, Mithril T13, Titanium T14, Lumen T15 (`can.ladders`, G23_LADROW["can"]) | ~7349, 8149 |
| Square side | `can.area` 1,3,5,7,9,11: **only 6 values, read by the INTERNAL tier 0-7 clamped to 5**. So Crude 1x1, Copper 3x3, Iron 5x5, Bronze + Thorium 7x7, Lead / Dusk / Cobalt 9x9, Chromium .. Lumen all 11x11 | 8135, GearCan.side |
| Waterings per fill | `can.uses` 20,30,40,60,80,100 (same 6-slot clamp: Chromium .. Lumen all 100) | 8136, GearCan.uses |
| Soil stays wet | `can.waterSec` 86400 game s (vanilla `Watering_Can_Use` Duration) = 1 game day = **48 real min** | 8137 |
| Upgrade lines (LL_PERKS) | Capacity `cap` max 5, cost 1,1,2,2,3; Growth Boost `grow` max 5, cost 1,2,2,3,3; Lasting Water `last` max 5, cost 1,1,1,2,2; Bloom `bloom` max 5, cost 1,2,2,3,3. **Fixed max 5**: not lines, so the tier does not raise them. 38 points maxes everything | 22697 |
| Capacity | +20 % waterings a level (`can.capacityPct`); **Lv 5 = never runs dry** | 24682 |
| Growth Boost | +4 % a level (`can.growPct`): watering a DRY soil pushes the crop's `lastTickGameTime` back by lv x 4 % x 86400 s (max 17,280 s) | 24683, GearCan.grow |
| Lasting Water | soil stays wet +20 % a level (`can.lastPct`, max +100 % = 96 real min) | 24680 |
| Bloom | +6 % a level chance (`can.bloomPct`, max 30 %) that dry soil you water is fertilized (vanilla `setFertilized(true)`) | 24685, GearCan.fert |
| Points | the can's pool = Farming level - 1 + SkyyCollections `coll:fn:toolPts` (lifelong.collPoints). Farming goes to 100, so 99+ points late | header 1478 |
| Pickaxe / hatchet lines (for comparison) | 1 point a level, capped at `lifelong.lineCapPerTier` (10) x (internal tier + 1); the top ladder step is uncapped | 23363 |

### 2.2 Vanilla farming (Assets.zip + HytaleServer.jar, read-only, VERIFIED 2026-10-27)

- Day length `GameplayConfigs/Default.json`: Daytime 1728 + Nighttime 1152 = 2880 real s. So **1 real second = 30 game seconds**, and
  1 game day (86400 s) = 48 real min.
- Crop grow times (game s, `Farming.Stages`): Wheat / Lettuce / Carrot / Corn / Cauliflower / Pumpkin / Rice / Turnip / Aubergine /
  Chilli / Cotton / Tomato 86,400 (regrow after harvest 45,540-75,900); Potato 124,350; Onion 169,200; Health / Mana / Stamina 175,950.
- Growth modifiers (`Server/Farming/Modifiers/`): Water x2.5, Fertilizer x2, LightLevel x2 (sun 5-15 or torch 5+). `FarmingUtil.tickFarming`
  **multiplies** them all together (bytecode: `dmul` loop, then the remaining time is divided by the product). So for Wheat: lit and dry =
  24 real min; lit + watered = 9.6 min; lit + watered + fertilized = 4.8 min.
- **Vanilla fertilizer never runs out.** The only `TilledSoilBlock.setFertilized` call in the engine is `FertilizeSoilInteraction` (true).
  Nothing ever sets it back to false. A fertilized soil stays x2 for good, through every harvest, until the block is broken or decays.
  (SkyyShards 0.4.14's text "x2 until harvested" is wrong. Fix it in the Shards round.)
- **Today's Growth Boost is multiplied too.** Pushing `lastTickGameTime` back by S seconds gives S x (the live modifier product). At Lv 5,
  lit + watered: 17,280 x 5 = 86,400. **One watering of dry soil ripens a whole Wheat crop at once.** It only happens once per 48 min (the wet
  time), and Lasting Water makes that even rarer. That is why the upgrades feel flat: Growth Boost and Lasting Water work against each other.
- Other mods' wet times: Hyfarming's Carlin can 43,200; NoCube cans 86,400; Shards hand-held Rain totem 30 real s, Sun 60 real s.

### 2.3 What else touches crop growth / watering (current pins)

| Source | What | Clash? |
|---|---|---|
| Dynamic Seasons 7.0.8 (pack) | overrides `Server/Farming/Modifiers/Water.json` (adds spring rain weathers) and `.patch`es every crop (quality, season modifier) | we must NOT override Water.json or the crop files |
| Alec's Tamework | own mushroom modifiers (`Tw_Mushroom_*`) | none |
| Nobody | overrides `LightLevel.json` (all ~75 jars in the Mods folder checked) | free to use (section 4.3) |
| SkyyShards 0.4.14 | Rain / Fertilizer / Sun hand-held Totem I (`totem.hand.*`: Rain wets r5 for 30 s, Fertilizer r3 permanent, Sun r5 by day 60 s); Harvest Spirit totems; shard farms | the Fertilizer totem must join the fertilizer clock (section 4.4) |
| SkyyTrees 0.6.6 | Farming tree: Wide Sowing (AOE seed bags), Wide / Swift Sweep, Harvest swing tiers | none (planting / harvesting, not growth) |
| SkyyPets 0.4.20 | Farming pets give Farming Fortune (`fortune.farming`) | Dew Harvest must stay a separate roll (section 3) |
| SkyyAccessories 0.5.33 | no growth or watering stat (Farming Barn Aura not wired) | none yet: room for a can talisman (section 5) |
| SkyySkills 0.4.67 | sells `Tool_Fertilizer_Crystal` (300 coins); Farming XP per crop | Skyy 2026-10-27: "farming levels really fast too". So no XP line here |

### 2.4 Earlier decisions that still hold

- 2026-10-15: the can spawns with you and upgrades like the lifelong tools. Tier-up widens the square (1x1 > 3x3 > 5x5 > 7x7, higher = more).
  The upgrades are Capacity / Growth boost / Lasting water / Bloom. **Lasting water is now replaced by Skyy's 2026-10-27 words.**
- 2026-10-16: hold and sweep like the hoe (`can.holdSec`). 2026-10-18: can tier-up needs the LETTUCE collection II.
- 2026-10-18: the Infinite Water Bucket refills cans (mid-game). 2026-10-16 "Yes, 10 levels per tier" (the lifelong line caps).
- 2026-10-24: shards are the main late-game source; island hand farming must stay below a maxed shard (balance_model `--p11`).

### 2.5 Mod survey (CurseForge + Skyy's Mods folder, 2026-10-27)

| Mod | What it does | Verdict |
|---|---|---|
| [Moar Cans](https://www.curseforge.com/hytale/mods/moar-cans), [Matthews Watering Cans +](https://www.curseforge.com/hytale/mods/matthews-watering-cans), [More Watering Cans](https://www.curseforge.com/hytale/mods/morewateringcans), [Better Watering Can](https://www.curseforge.com/hytale/mods/better-watering-can) | tier ladders that only grow the square (Matthews 3x3 .. 11x11, Moar Cans up to 9x9) | Learn only: our 1 .. 11 square already matches. None has upgrade points |
| [NoCube's Cultivation](https://www.curseforge.com/hytale/mods/nocubes-cultivation-hytale) (in Mods, ARR) | 3 cans (all 86,400 wet), 4 fertilizers (charges 8-50) | Learn: fertilizer as charges. Not packed (licence) |
| Hyfarming 1.0.6 (in Mods) | Carlin can, wet 43,200, 20 uses | Learn: a shorter wet time is normal |
| [Sprinklers](https://www.curseforge.com/hytale/mods/sprinklers), [Andrea's Sprinklers Revived](https://www.curseforge.com/hytale/mods/andreas-sprinklers-revived), [Hydew Sprinklers](https://www.curseforge.com/hytale/mods/hydew-sprinklers), GlymeraIrrigation | automatic watering | Leave out: it duplicates the Shards Rain totem and works against "manual speed-up" |
| [Farming: Tools and Equipment](https://www.curseforge.com/hytale/mods/farming-tools-and-equipment) | composters, composted fertilizer | Leave out: duplicates the Fertilizer totem |

Nothing to pack. Nothing gives a can upgrade points, so we build the missing part in SkyyGear.

## 3. The proposal: current vs proposed

All times are game seconds (vanilla units), with real time in brackets (30 game s = 1 real s). Tooltips show real seconds
(PROJECT-RULES: "Times shown in seconds").

| # | Skyy's point | Today | Proposed default |
|---|---|---|---|
| 1 | Raise the caps | every upgrade fixed at max 5 | every upgrade is a LINE: 1 point a level, cap = `can.lineCapPerStep` (3) x the can's ladder step. Crude 3, Copper 6, Iron 9, Bronze 12, Thorium 15, Lead 18, Dusk 21, Cobalt 24, Chromium 27, Azurvane 30, Adamantite 33, Slag 36, Cinder 39, Mithril 42, Titanium 45, **Lumen uncapped** (like the pickaxe's top step). Each effect also has a ceiling (below) |
| 2 | More upgrades | 4 lines | 6 lines: Capacity, Growth Boost, Bloom, **Rich Soil** (new, takes Lasting Water's slot), **Miracle Grow** (new), **Dew Harvest** (new) |
| 3 | Swap out Lasting Water | +20 % wet time a level | removed. Its points come back automatically (section 6) |
| 4 | Plants grow a little slower | Light x2 | Light x**1.7** (`farm.lightGrowth`): about 15 % slower for every lit crop. Wheat lit + watered 9.6 -> 11.3 real min; dry 24 -> 28.2 min; + fertilizer 4.8 -> 5.6 min |
| 5 | Soil dries much faster | 86,400 (48 min) | **10,800 (6 real min)** `can.waterSec`. You water each patch about twice per crop instead of once per two crops |
| 6 | Starter can holds a bit more | Crude 20 | **Crude 30**. Every step gets its own value (section 4.2) |
| 7 | Fertilizer stays a shorter time | forever (vanilla) | **21,600 (12 real min)** `can.fertSec`, about one watered crop. Rich Soil makes it longer |
| 8 | Buffs feel more useful as you level | +4 % / +6 % steps, max 5 | per-level values sized so the Titanium cap (45) reaches about each ceiling |

### The six lines (all 1 point a level; cap as in row 1)

| Line (saved key) | Per level | Ceiling | What it does |
|---|---|---|---|
| Capacity (`cap`, kept) | +10 % waterings per fill (`can.capacityPct`) | none | more sweeps before a refill. "Never runs dry" moves to the Lumen can (Q3) |
| Growth Boost (`grow`, reworked) | +1 % of a standard crop (`can.growPct`) | 50 % a watering (`can.growMax`) | each DRY soil you water grows its crop by lv % of 86,400 s. **No longer multiplied by water / fertilizer / light** (the push is divided by the live product: see 4.1). The manual speed-up |
| Bloom (`bloom`, kept) | +2 % chance (`can.bloomPct`) | 100 % | dry soil you water gets fertilized, or has its fertilizer timer refreshed |
| Rich Soil (`rich`, NEW) | +5 % fertilizer time (`can.richPct`) | +300 % | fertilizer from your can lasts longer: base 12 min, at Lv 45 39 min |
| Miracle Grow (`mira`, NEW) | +0.5 % chance (`can.miraclePct`) | 25 % (`can.miracleMax`) | a dry crop you water ripens at once (jumps to its final stage) |
| Dew Harvest (`dew`, NEW) | +1 % chance (`can.dewPct`) | 100 % | when your watering makes a crop ripe (Growth Boost or Miracle Grow), one of that crop's items goes straight to you, storage-first (sacks first). A separate roll from Farming Fortune, so it never touches the Fortune numbers (no duplicate) |

Points: about 240 late (Farming 100 + collections). Maxing all six at Titanium costs 270, so the player has to choose until Lumen.
Early on (Farming 4, Crude cap 3) it is the same 1-point feel as today.

## 4. How it works (for the builder)

### 4.1 Growth Boost and Miracle Grow (GearCan.plan / grow)

- Boost seconds `g = lv x can.growPct / 100 x 86400 / M`, where `M` = 2.5 (the soil is wet: we just watered it) x (2 if fertilized) x
  `farm.lightGrowth`. Assume the crop is lit (island crops are). This makes "+12 %" mean 12 % of a Wheat crop whatever the modifiers.
  Clamp `g` at `can.growMax`. Only for dry soil (today's rule, kept: it is what makes faster drying pay off).
- Miracle Grow: roll; on a hit push back by the crop's whole remaining time (or `ChangeFarmingStage` to the final stage if a probe shows the
  push misses stage boundaries; UNVERIFIED). Ripened-by-you = ripe after the push -> roll Dew Harvest.
- Dew Harvest gives the crop's base item (`Plant_Crop_<X>_Item`; Eternal crops their normal item), quantity 1. Count it before and after,
  storage-first. It gives NO Farming XP and does not count as a harvest (no collection credit; Q4).

### 4.2 Per-step lists (16 values, Crude .. Lumen)

- `can.uses` default `30,35,40,50,60,70,80,90,100,110,120,135,150,165,180,200` (Crude +50 %; Copper / Iron keep today's 30 / 40 feel).
- `can.area` default `1,3,5,7,7,9,9,9,11,11,11,11,11,11,11,11` = **exactly today's squares**, now one value per step (Skyy did not ask for
  bigger squares). The parser takes 6 values (old form, mapped by internal tier as today) or 16 (by step).
- Line cap = `can.lineCapPerStep` x step (1 .. 16); the last step is uncapped; 0 = no cap. Points above a cap stay banked (pickaxe rule).

### 4.3 Slower growth: our own LightLevel modifier

- SkyyGear ships `Server/Farming/Modifiers/LightLevel.json`, generated at build time from Assets.zip (vanilla-derived, never committed). It
  changes only `Modifier` 2 -> `farm.lightGrowth` (1.7). Nobody else overrides it (checked). Dynamic Seasons' Water.json and crop patches
  are left alone.
- Server Setup row `farm.lightGrowth` (dec 1.0-3.0, flag `restart`): SkyyGear writes the value into the loaded asset at setup (reflection on
  `LightLevelGrowthModifierAsset`'s modifier field; UNVERIFIED, probe first). If the probe fails, the jar asset's 1.7 stays and the row is
  shown read-only.
- This touches every lit crop in every world (shard worlds too, if their crops are real blocks; the Shards totem output model does not use
  it). Rain, Sun and Rain-totem watering keep their own wet times.

### 4.4 Fertilizer clock (new SAVED data, so this is a full round)

- `Skyy_SkyyGear/can/fert-<world>.properties`: `x,y,z=<game-second it ends>`. Atomic write, kept to 50,000 entries per world (the oldest end
  first). Every 30 real s, on the world thread, any loaded entry past its time gets `setFertilized(false)` + `markBlockNeedsSaving` + ticking,
  and is removed. Entries in unloaded chunks wait.
- A Bloom hit (or a watering of soil already fertilized by Bloom) sets the end to now + `can.fertSec` x (1 + rich x `can.richPct` / 100).
- `can.fertAll` (bool, default **on**, Q1): fertilized soil your can waters that has NO entry (vanilla Fertilizer item, Fertilizer totem,
  old Bloom) gets now + `can.fertSec`. Old permanent fertilizer then fades the first time it is watered after the update.
- Bridge `gear:fn:fertMark` {world name, x, y, z, seconds} -> Boolean, so the SkyyShards hand-held Fertilizer totem registers its soils the
  same way (Shards round).

## 5. The four power sources (tool + gear + accessories + pets)

Every can effect is read as **can line + bonus**. The bonus is a Double per stat the other mods post on `skyy.bridge`:
`can:bonus:<uuid>` -> Map {grow, bloom, rich, mira, dew, cap} in the line's own units, summed, then the line ceilings apply. Planned
sources, each its own later round (numbers are targets, not built):

| Source | Owner | Example | Share at late game |
|---|---|---|---|
| Tool (the can's lines) | SkyyGear | Growth Boost 45 % | ~50 % |
| Gear (Farming armor `garmor.ladders.farming`) | SkyyGear | set bonus "Dewy" +5 Growth Boost, +5 Bloom | ~20 % |
| Accessories | SkyyAccessories | "Dewdrop Talisman" family: +Miracle Grow / +Dew Harvest | ~15 % |
| Pets | SkyyPets | Farming pets (Rabbit): +Bloom / +Rich Soil a level (NOT more Fortune) | ~15 % |

The ceilings (50 % boost, 25 % Miracle, 100 % Bloom / Dew) stop the four sources stacking past the balance in section 7.

## 6. One-time migration (PROJECT-RULES 4: only old defaults, history copy first, log + Undo, run-once marker, bytes kept)

### 6.1 Saved points (per profile registry, GearLife, marker `can2=1`)

- Copy first: `lifelong/history/<pk>.pre-can2.properties` (verified).
- `can.up.last` (Lasting Water) is deleted. Spent points are worked out from the levels, so its points (1 .. 7) are free again by
  themselves, the way t1Mig did it.
- `cap` / `grow` / `bloom` levels are kept as they are. Their cost drops from 1,1,2,2,3 / 1,2,2,3,3 to a flat 1 a level, so the difference
  comes back free too. A saved level above the new cap (only Crude cans with 4-5 levels: cap 3) is lowered to the cap, and its points come back.
- Capacity Lv 5 loses "never runs dry" (Q3). It becomes +50 %.
- One `gear.log` line `LL-CAN2MIG <pk> last=<n> freed=<p>` per profile, and one chat line: "Your watering can changed: Lasting Water is gone,
  its <p> points are free - spend them on the new upgrades (Rich Soil, Miracle Grow, Dew Harvest)."

### 6.2 Server Setup / config.properties (`migrateCan2`, the migrate0317 machinery)

| Key | Old default -> new | Note |
|---|---|---|
| `can.waterSec` | 86400 -> 10800 | |
| `can.uses` | `20,30,40,60,80,100` -> the 16-value list | |
| `can.area` | `1,3,5,7,9,11` -> the 16-value list | same squares |
| `can.capacityPct` | 20 -> 10 | |
| `can.growPct` | 4 -> 1 | the meaning changes (no longer multiplied). A hand-edited value is kept but logged with a warning |
| `can.bloomPct` | 6 -> 2 | |
| `can.lastPct` | row removed | the key is left in the file, ignored, logged once |
| new rows | `can.lineCapPerStep` 3, `can.growMax` 50, `can.fertSec` 21600, `can.fertAll` true, `can.richPct` 5, `can.miraclePct` 0.5, `can.miracleMax` 25, `can.dewPct` 1, `farm.lightGrowth` 1.7 (restart) | category `lifelong` (farm row: `farming`) |

Every row goes through `tools/skyycfg.py` (`tools/CONFIG-CONTRACT.md`): label, unit `s` / `%`, plain-words description; `live,danger` where it
changes economy (growth, uses, Bloom, Dew). The rows are added to G312_ROWK / the danger list.

## 7. Balance check

Model: Wheat on a lit island patch. The player re-waters as soon as the soil is dry (every 6 min). Crops per plot per real hour (before
Fortune):

| Case | Today | Proposed |
|---|---|---|
| Start (Crude, no levels) watered | 6.3 | 5.3 (-15 %: "a little slower") |
| Early (Copper, Growth 6) | ~6.5 | ~6.2 |
| Mid (Cobalt, Growth 24, Bloom 24) | ~7 | ~8.3 |
| Late (Titanium, Growth 45, Miracle 22 %, fertilized) | ~13.8 (Lv 5 boost = 1 instant crop per 48 min + permanent x2 fertilizer) | ~15 (boost once per 6-min dry cycle) |
| Late, no fertilizer | ~7.5 | ~9.8 (+30 %, only with active watering) |

- **Progression:** the payoff goes from -15 % at Crude to about +30 % at Titanium, and only for players who keep watering. That is the
  "manual speed-up" Skyy asked for.
- **vs shards:** `python tools/balance_model.py --p11` (read-only): a maxed Large shard island at Totem V = 23,759 items / h vs 7,793 by
  hand (x3.05). The can's +30 % late leaves the island hand farm well below that. Shards stay the automated main source.
- **vs Farming XP / coins:** XP per crop is unchanged. More crops late (+30 %) means more XP, but Skyy already flagged Farming XP as too fast
  (2026-10-27). The SkyySkills XP fix comes first or in the same batch. No line gives XP. Dew Harvest adds items only (at most +1 per
  ripened crop, below the Fortune budget `P5_GATHER_DD` farming 15.75).
- **Today's hidden spike goes away:** Growth Boost Lv 5 ripening a full crop in one watering (section 2.2) is replaced by a capped,
  modifier-independent push.

## 8. Tooltips (Style Guide section 15 + tier tags + the 2026-10-24 gear tooltip order)

Can tooltip (GearCan.lines -> GearLL.lines), in order:

1. Name in the can's rarity colour.
2. Header: `T4 Thorium - Watering Can` (tier tag first, `tools/tier_tags.py` colour), then `Farming Lv 23`.
3. ABILITIES (label colour): `Waters 7x7 tilled soil (hold right-click and sweep)`.
4. STATS: name soft white `#d6e4ee`, value green `#7ee08a` (bold numbers): `Waterings per fill 50`, `Soil stays wet 360 s`,
   `Fertilizer lasts 720 s`.
5. UPGRADES: one row per line, level gold `#e8c25a`, effect green:
   `Growth Boost  12 / 15  +12% growth each watering of dry soil`. A line at its cap gets a dim `#7f93a6` tail: `(Thorium cap - tier up for 18)`.
6. Minor info, dim: `Right-click water to refill`, `Yours: /can`.

Upgrade page (Tools tab): 6 perk rows (the page already fits 6), each `Lv 12 / 15 (Thorium cap)`, following `research/Menu-Pattern.md`.
Chat lines: "Miracle Grow! 3 crops ripened." and "Dew Harvest: +2 Wheat." (`tellOnce`, 2 s gap), plus today's "Bloom!" line. No new items,
so no new tier-tag ids (the can ids are already in `tools/tier_tags.py`).

## 9. Build rounds

1. **SkyyGear (next free version after 0.3.49), FULL round** (saved data + economy + migration): sections 3-6 and 8, plus the LightLevel
   asset, the fertilizer clock, `gear:fn:fertMark` and `can:bonus:<uuid>` read. Harness: plan() numbers per level, cap per step, the
   migration of a 0.3.48 registry (last=5, cap=5 on Crude), the fertilizer clock (save / expire / unloaded), the 6- and 16-value parsers.
   Probes (one at a time): the LightLevel modifier field write; Miracle Grow push vs `ChangeFarmingStage`.
2. **SkyyShards, LEAN round:** the hand-held Fertilizer totem calls `gear:fn:fertMark`; fix the "until harvested" texts (fertilizer then
   lasts `can.fertSec`).
3. **SkyySkills:** the Farming XP fix already queued (docs/answered/skills.md 2026-10-27). Deploy it in the same batch as round 1.
4. Later, one round each: Farming armor set bonus, an Accessories can talisman, a Farming pet Bloom / Rich Soil perk (section 5).

## 10. Open questions for Skyy (defaults in [brackets])

1. **Which fertilizer gets shorter?** Every fertilizer (the vanilla item, the Fertilizer totem, the can's Bloom), or only the can's?
   [Every fertilizer: 12 real min, Rich Soil makes your can's longer, watering refreshes it.]
2. **How fast should soil dry?** [6 real min after each watering (10,800 game s), the same for every can.] (Alternative reading of "dries
   faster after watering a lot": soil dries faster each time it is re-watered within a short window. Not the default.)
3. **Capacity's "never runs dry" (today's Lv 5)?** [Remove it from Capacity. The Lumen (top) can never runs dry. The Infinite Water Bucket
   still refills any can.]
4. **Should watering give Farming XP or collection credit?** [No: Farming XP is already too fast. The rewards are growth, fertilizer, and
   Dew Harvest crops (sellable, no XP, no collection credit).]
