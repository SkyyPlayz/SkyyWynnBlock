# Fishing stage 2 - build spec (SkyyFishing 0.2.0: Zone 2-3 fish, rods T3-T6, part tier III)

Cloud draft, 2026-10-23. Paper only: no game files, no build, no test. Anything that needs `Assets.zip`, `HytaleServer.jar`, a pack jar or the
test world is **UNVERIFIED** and listed in "For the local session". Numbers were re-computed in python (closed-form mean of the u^2 weight roll,
the same model as `research/cloud/Fish-Species-Catalog.md` section 4 - it reproduces the catalog's income table to the coin).

Inputs: `research/cloud/Fishing-Rework-Survey.md`, `research/cloud/Fish-Species-Catalog.md`, `research/cloud/Fishing-UI-Mockup.md`,
`research/cloud/SkyyFishing-Spec-Draft.md` (sections 4, 7, 8, 12), `SkyyFishing/build_skyyfishing_0.1.12.py` (read only: what is live),
`tools/deploy_set.py` (read only), `tools/tier_tags.py`, `tools/skyyench.py`, `tools/CONFIG-CONTRACT.md`, `tools/AGENT-BRIEF.md`,
`research/balance/targets.md`, `research/balance/gathering.md`, `research/balance/gear.md`, `research/balance/economy.md`,
`SkyyGear/build_skyygear_0.3.40.py` (pole ladder), `SkyyMobs/build_skyymobs_0.1.18.py` (mob:fn:levelAt), `SkyyShards/build_skyyshards_0.4.py`
(world clock), `SkyySacks/build_skyysacks_0.8.28.py` (fish rule).

## 0. Decisions followed (not re-decided)

| Decision | Where |
|---|---|
| Fishing is our own mod; HyFishing OFF; Angler's Almanac / HyFishing = ideas only | `docs/answered/project.md` line 35 (LOCKED 2026-10-06), `docs/answered/skills.md` line 103 (LOCKED 2026-10-10) |
| Click-bar fight, "!" bite, length + weight, bench with Parts / Rig, all 4 hooks / 4 lines / 4 sinkers x tiers I-IV | `docs/answered/skills.md` lines 82, 88 (LOCKED 2026-10-06) |
| Junk = vanilla items only | `docs/answered/skills.md` line 87 (LOCKED 2026-10-06) |
| 8 rod items, one per rod tier; the fitted reel lives on the rod (reel look stat) | `docs/answered/skills.md` line 90 (LOCKED 2026-10-07) |
| Rod icons = the 3D renders | `docs/answered/gear.md` line 102 (LOCKED 2026-10-07) |
| No bamboo in any recipe; T0 shown as Wooden | `docs/answered/skills.md` line 101 (LOCKED 2026-10-09) |
| Pole = lifelong tool (upgrade only, levels with Fishing); reel / hooks / line / sinkers = crafted parts | `docs/answered/skills.md` line 119, `docs/answered/gear.md` lines 170, 172 (2026-10-12) |
| Pole spawns with you, works without tackle; no Wooden Reel | `docs/answered/gear.md` lines 202, 206 (2026-10-15) |
| Tier tag first in every tiered item's flavor text | `docs/answered/gear.md` line 203 (2026-10-15) + `PROJECT-RULES.md` section 4 |
| Fish go to the Fishing bag; bench reads Void fish | `docs/answered/bags.md` line 108, `docs/answered/skills.md` line 170 (2026-10-16) |
| Bazaar Fishing tab = the fish we actually catch | `docs/answered/economy.md` line 135 (2026-10-16) |
| Fortune uncapped (100 % = guaranteed double) | `docs/answered/gear.md` line 288 (2026-10-18) |
| 20 levels per zone for all gear; fishing waits for its own overhaul (this is it) | `docs/answered/gear.md` line 292 (2026-10-18) |
| Lifelong-tool tier-up needs its collection at tier II | `docs/answered/gear.md` "TOOL TIER-UP COLLECTION GATE -> II" (2026-10-18) |
| Gathering tool / set tier-ups use plain items below Dusk (T6), Enchanted from Dusk on | `docs/answered/gear.md` "CHEAPER LOW-TIER ARMOR UPGRADES" + "All sets: from Dusk" (2026-10-18) |
| Alloys have no collection: alloy gear opens when BOTH parent collections reach V | `docs/answered/gear.md` "COLLECTION UNLOCK LADDER + ALLOYS" (2026-10-18) |
| No oceans; no shop sells rods or parts (R3) | `docs/answered/mobs.md` R5, `docs/answered/economy.md` R3 |
| Sort by tier everywhere; one menu pattern; vanilla look | `PROJECT-RULES.md` section 4, `research/Menu-Pattern.md`, `research/Vanilla-UI-Style-Guide.md` |

Draft defaults taken (nothing in `docs/answered/` overrides them): species rarity IS the grade (live since 0.1.x), a fish heavier than the rod never
bites (re-rolled), sell whole by weight, Clerk demand factor, fillets 1 per 0.5 kg max 40, the 39-species catalog (Zone 2 = 8, Zone 3 = 9 here),
season / time lean x1.5 / x0.5, Zone 3 winter bite x0.67, one full round now with the Angler's Ledger as its own later round (survey Q1).

## 1. Scope

| In this round (SkyyFishing 0.2.0 + SkyyGear next) | Not in this round |
|---|---|
| Zone of the water (Zone 1 / 2 / 3 tables), 17 new species | Angler's Ledger book, Recipes tab (Cooking), fish dishes |
| Rods T3-T6 get recipes (items exist since 0.1), 4 new reels | Lava fishing, sea creatures, T7 Onyxium recipe, part tier IV (stage 3) |
| Part tier III (10 new part items) | Water-type / biome filter inside a zone (all zone water is one table) |
| Dune Fish + Frost Fish counts (per profile), their recipe gates | Per-zone fillet items (fillets stay `Food_Fish_Raw` / `Food_Fish_Raw_Uncommon`) |
| Season + time-of-day lean (with safe fallbacks) | Fishing armor art, accessories I-II |
| Per-zone price per kg + treasure zone mult + zone junk / treasure tables | Cozy-Tales-style fish shadows (survey Q3: no) |
| Tier tags on every rod, reel and fish (Zone 1 fish too) | |
| SkyyGear: pole ladder + level bands for the new rods | |

## 2. The rod ladder vs the 15-step metal ladder (the one real design change)

Since TT_VERSION 3 (`tools/tier_tags.py`), zone z owns three metals: Zone 1 Copper / Iron / Bronze (T1-T3), Zone 2 Thorium / Lead / Dusk (T4-T6),
Zone 3 Cobalt / Chromium / Azurvane (T7-T9), Zone 4 Adamantite / Slag / Cinder, Zone 5 Mithril / Titanium / Lumen. The live rod ids are the old
8-step words (`SkyyFishing/build_skyyfishing_0.1.12.py` line 378: Bamboo, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium). The
catalog plays Zone 3 with rods T4-T6 (Cobalt / Adamantite / Mithril), but Adamantite and Mithril ore only exist in Zones 4 / 5 - a Zone 3 player
could not make them. **Default (question 1):** keep every id and config key (no saved-data change), and show rods T5 / T6 as the Zone 3 metals,
exactly like 0.1.1 showed Bamboo as Wooden (`TIER_SHOWN`):

| Rod id (kept) | Shown name | Max kg | Reel id (new) | Reel Power | Tier tag | Zone | Level band (`tools/tier_tags.py` METAL_BANDS) |
|---|---|---|---|---|---|---|---|
| `SkyyFishing_Rod_Thorium` | Thorium Fishing Rod | 16 | `SkyyFishing_Reel_Thorium` | 6.6 | T4 Thorium | 2 | 20-28 |
| `SkyyFishing_Rod_Cobalt` | Cobalt Fishing Rod | 25 | `SkyyFishing_Reel_Cobalt` | 7.6 | T7 Cobalt | 3 | 40-48 |
| `SkyyFishing_Rod_Adamantite` | Chromium Fishing Rod | 40 | `SkyyFishing_Reel_Adamantite` (shown Chromium Reel) | 8.7 | T8 Chromium | 3 | 48-55 |
| `SkyyFishing_Rod_Mithril` | Azurvane Fishing Rod | 60 | `SkyyFishing_Reel_Mithril` (shown Azurvane Reel) | 9.8 | T9 Azurvane | 3 | 55-63 |
| `SkyyFishing_Rod_Onyxium` | unchanged, no recipe (stage 3) | 90 | - | - | T16 Onyxium (as now; renamed in stage 3, question 8) | - | - |

Max kg = the live `fish.rod.<tier>.maxKg` defaults (`research/balance/gathering.md` lines 1115-1118). Reel Power = spec 4.1 formula
2.88 x maxKg^0.3 (python: 6.6 / 7.6 / 8.7 / 9.8). Reel ids follow the live rule `SkyyFishing_Reel_<TIERS word>` (`FishDefs.reelTier` maps the
word to the look-stat value 4-7, so the rod looks already work). Art: `research/cloud/fishing-art/icons/rod-t3..t6-*.png` and `reel-t3..t6-*.png`
exist; the T5 / T6 renders are Adamantite / Mithril coloured - re-tint them at build time with the Chromium / Azurvane tints in `tools/skyyench.py`
(ART_TINT / ALLOY_TINT), else keep the art (question 1b).

Gap to know about: the pole's level cap follows its rod's band, so between Thorium (cap 28) and Cobalt (from 40) a pole stays at Lv 28 - Lead /
Dusk have no rod (only 8 rod ids, LOCKED). Question 2.

## 3. Exact ids, lang keys, names

All lang keys are `server.items.<id>.name` / `server.items.<id>.description` in SkyyFishing's own lang file (one writer: `tools/ci/langdup.py`).

### 3.1 New fish (17) - `SkyyFishing_Fish_<Key>`, icon `research/cloud/fish-art/icons/<icon>.png` (all 17 exist, 64 x 64 asserted by the build)

| Key | Shown name | Zone | Rarity | kg | cm (catalog) | Bite factor | Spawn weight | Seasons | Times | Tier tag | Vanilla look (UNVERIFIED 3) | Icon |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OasisCarp | Oasis Carp | 2 | Normal | 1-8 | 41-83 | 0.9 | 20 | summer | any | T4 Fish | Fish_Salmon_Item | oasis_carp |
| Sandskipper | Sandskipper | 2 | Normal | 0.5-4 | 37-74 | 0.8 | 22 | any | day | T4 Fish | Fish_Minnow_Item | sandskipper |
| DunePiranha | Dune Piranha | 2 | Normal | 1-6 | 45-82 | 0.9 | 16 | any | dusk, night | T4 Fish | Fish_Piranha_Item | dune_piranha |
| MirageEel | Mirage Eel | 2 | Unique | 2-14 | 69-133 | 1.2 | 10 | autumn, winter | night | T4 Fish | Fish_Eel_Moray_Item | mirage_eel |
| TarPitGudgeon | Tar Pit Gudgeon | 2 | Unique | 3-12 | 63-100 | 1.3 | 8 | any | any | T4 Fish | Fish_Catfish_Item | tar_pit_gudgeon |
| LostLuggageGrouper | Lost Luggage Grouper | 2 | Rare | 11-25 | 103-136 | 1.4 | 6 | any | any | T4 Fish | Fish_Piranha_Black_Item | lost_luggage_grouper |
| MirageSturgeon | Mirage Sturgeon | 2 | Legendary | 17-34 | 129-162 | 1.6 | 1.4 | summer | dawn | T7 Fish | Fish_Pike_Item | mirage_sturgeon |
| Sandsalmon | Customs-Cleared Sandsalmon | 2 | Fabled | 6-16 | 84-117 | 1.8 | 0.25 | spring | any | T4 Fish | Fish_Tang_Sailfin_Item | customs_cleared_sandsalmon |
| FrostCod | Frost Cod | 3 | Normal | 2-15 | 58-114 | 0.9 | 22 | winter | day | T7 Fish | Fish_Frostgill_Item | frost_cod |
| WhisperChar | Whisper Char | 3 | Normal | 1-10 | 46-100 | 0.9 | 18 | any | dawn, dusk | T7 Fish | Fish_Trout_Rainbow_Item | whisper_char |
| SnowmeltTrout | Snowmelt Trout | 3 | Normal | 2-12 | 58-106 | 1.0 | 14 | spring | day | T7 Fish | Fish_Trout_Rainbow_Item | snowmelt_trout |
| IceboundSalmon | Icebound Salmon | 3 | Unique | 3-24 | 67-134 | 1.1 | 12 | autumn, winter | any | T7 Fish | Fish_Salmon_Item | icebound_salmon |
| PermitLamprey | Permit Lamprey | 3 | Unique | 4-20 | 93-159 | 1.3 | 9 | spring, summer | night | T7 Fish | Fish_Eel_Moray_Item | permit_lamprey |
| GlassPike | Glass Pike | 3 | Rare | 26-48 | 148-182 | 1.3 | 6 | winter | night | T8 Fish | Fish_Pike_Item | glass_pike |
| WhisperSturgeon | Whisper Sturgeon | 3 | Rare | 41-60 | 166-188 | 1.5 | 4.5 | winter | night | T9 Fish | Fish_Shark_Hammerhead_Item | whisper_sturgeon |
| BlizzardHalibut | Blizzard Halibut | 3 | Legendary | 30-60 | 111-140 | 1.6 | 1.3 | winter | any | T8 Fish | Fish_Snapjaw_Item | blizzard_halibut |
| SleeperAisle9 | The Sleeper in Aisle 9 | 3 | Mythic | 45-60 | 171-188 | 2.0 | 0.06 | winter | night | T9 Fish | Fish_Whale_Humpback_Item | the_sleeper_in_aisle_9 |

Bite factor = catalog bite s / 6 (live rule, `SkyyFishing/build_skyyfishing_0.1.12.py` line 418). Shape K = live formula from min kg / min cm
(line 431; the build's 12 % max-length assert must hold for all 27 species - harness check H3). Description text:
`"<tag> - <Rarity> fish from Zone <z> (<collection>). Sell it whole or fillet it at a Fishing Bench."`.

### 3.2 Zone 1 fish (10, live ids unchanged) get tags only

Rule (question 3): **a fish's tier = max(its zone's first ladder step, the tier of the lowest rod that can land its minimum weight)**, word `Fish`
(a new own-ladder noun in `tools/tier_tags.py` OWN_LADDERS, so "T4 Fish", not a metal word on a fish). Zone floors: Z1 T1, Z2 T4, Z3 T7.
Zone 1 result: all T1 except `SkyyFishing_Fish_PonderingPike` (6.5 kg needs the Iron rod) = **T2 Fish**. Live lang text changes from
`"Normal fish from Zone 1. ..."` to `"T1 Fish - Normal fish from Zone 1 (Pond Fish). ..."`.

### 3.3 Rods, reels, parts

| Id | Shown name | Tag | Description (after the tag) |
|---|---|---|---|
| `SkyyFishing_Rod_Bamboo` / `_Copper` / `_Iron` | Wooden / Copper / Iron Fishing Rod (live) | T1 Crude / T1 Copper / T2 Iron (new tags) | live text |
| `SkyyFishing_Rod_Thorium` / `_Cobalt` / `_Adamantite` / `_Mithril` | section 2 | section 2 | "Max fish weight N kg. ..." (live wording) |
| `SkyyFishing_Reel_Copper` / `_Iron` (live) | Copper / Iron Reel | T1 Copper / T2 Iron | live text |
| `SkyyFishing_Reel_Thorium` / `_Cobalt` / `_Adamantite` / `_Mithril` (new) | Thorium / Cobalt / Chromium / Azurvane Reel | T4 / T7 / T8 / T9 | "Reel Power X per click. Fit it on a rod at a Fishing Bench." |
| `SkyyFishing_Reel_Bamboo` (live, no recipe) | Wooden Reel | T1 Crude | live text |
| `SkyyFishing_Hook_Barbed_III`, `SkyyFishing_Hook_LostProperty_III`, `SkyyFishing_Hook_Lure_III`, `SkyyFishing_Line_Braided_III`, `SkyyFishing_Line_Steady_III`, `SkyyFishing_Line_Twin_III`, `SkyyFishing_Line_Scholars_III`, `SkyyFishing_Sinker_Weighted_III`, `SkyyFishing_Sinker_Clean_III`, `SkyyFishing_Sinker_Deep_III` | "<Part> III" | none (parts keep their own I-II-III ladder, `research/Tier-Tags-Plan.md` row "Fishing parts": NOT tagged) | live pattern, quality "Rare"; icons `research/cloud/fishing-art/icons/<slug>-III.png` (all 10 exist); model = the live TACKLE_LOOK |

`PART_TIERS` becomes `["I", "II", "III"]`; the 0.1.8 assert "23 tackle models" becomes 37 (3 old reels + 4 new + 30 parts).

## 4. Zone detection, seasons, time

| Piece | Rule | Fallback |
|---|---|---|
| Zone of the water | at the bite roll: `mob:fn:levelAt` {world name, bobber x, y, z} (SkyyMobs 0.1.5+, any thread, never loads a chunk) -> its `hi` level -> the first zone whose top in `fish.zone.tops` (20,40,60,80,100 = `tools/tier_tags.py` ZONE_TOPS) is >= hi | null (islands, no band, Mobs missing) = `fish.zone.default` 1 (the island pond fishes Zone 1, Skyy 2026-10-18 `docs/answered/world.md` line 114) |
| Zones 4 / 5 water | no species yet | uses the highest built zone below (`fish.zone.maxBuilt` 3) until stage 3 |
| Season | Dynamic Seasons (pack mod) current season, read once per 30 s per world, cached | not found / off = no season lean (one INFO line at start) |
| Time of day | the world clock `WorldTimeResource.getGameTime()` hour (pattern: `SkyyShards/build_skyyshards_0.4.py` `clock(w)`); dawn / day / dusk / night by the hour rows | clock missing = `getSunlightFactor() >= 0.25` is day, else night; both missing = "any" (no lean) |
| Lean | species weight x `fish.season.inMult` 1.5 in season, x `fish.season.outMult` 0.5 out of season ("any" = x1); same with `fish.time.*`; Z3 winter: bite time x `fish.z3.winterBite` 0.67 | - |

The zone and season are fixed at the bite (the fish rolled = the fish landed; the catch card and the record use that zone).

## 5. Recipes (bench Parts tab; sorted by tier, then name)

Gate columns: the zone fish count tier (Pond / Dune / Frost, counts `fish.pondTiers` / `fish.duneTiers` / `fish.frostTiers` = 25 / 50 / 100 / 250 /
500 / 1,000 / 2,500 / 5,000) and the metal collection tier via `coll:fn:tier` (live mechanism). Each tier consumes the one below (live rule).

| Output | Inputs | Consumes | Fish gate | Metal gate | Why |
|---|---|---|---|---|---|
| `SkyyFishing_Rod_Thorium` | `Ingredient_Bar_Thorium` x48, `Ingredient_Fabric_Scrap_Linen` x8 | `SkyyFishing_Rod_Iron` | Dune III | Thorium II | T4 < Dusk = plain bars; between the pickaxe's Bronze 32 and Dusk 64 bars (`research/balance/gear.md` line 274) |
| `SkyyFishing_Reel_Thorium` | `Ingredient_Bar_Thorium` x16 | `SkyyFishing_Reel_Iron` | Dune IV | Thorium IV | reels = parts: keep the live reel gate (IV) |
| `SkyyFishing_Rod_Cobalt` | `Skyy_Ench_Cobalt` x2, `Ingredient_Bolt_Silk` x4 | `SkyyFishing_Rod_Thorium` | Frost III | Cobalt II | from Dusk on = Enchanted; = the Cobalt pickaxe (Ench x2, same line) |
| `SkyyFishing_Reel_Cobalt` | `Ingredient_Bar_Cobalt` x24 | `SkyyFishing_Reel_Thorium` | Frost IV | Cobalt IV | |
| `SkyyFishing_Rod_Adamantite` (Chromium) | `Skyy_Ench_Chromium` x2, `Ingredient_Bolt_Silk` x6 | `SkyyFishing_Rod_Cobalt` | Frost V | Chromium II | = the Chromium pickaxe |
| `SkyyFishing_Reel_Adamantite` (Chromium) | `Ingredient_Bar_Chromium_SkyWynn` x24 | `SkyyFishing_Reel_Cobalt` | Frost VI | Chromium IV | |
| `SkyyFishing_Rod_Mithril` (Azurvane) | `Ingredient_Bar_Azurvane_SkyWynn` x128, `Ingredient_Bolt_Silk` x8 | `SkyyFishing_Rod_Adamantite` | Frost VI | Cobalt V AND Chromium V (alloy rule) | = the Azurvane pickaxe (128 alloy bars) |
| `SkyyFishing_Reel_Mithril` (Azurvane) | `Ingredient_Bar_Azurvane_SkyWynn` x32 | `SkyyFishing_Reel_Adamantite` | Frost VII | Cobalt V AND Chromium V | |
| Hooks III (Barbed / Lure / Lost Property) | `Ingredient_Bar_Cobalt` x4 (+ `Food_Fish_Raw` x6 Lure, + `Ingredient_Bar_Gold` x3 Lost Property) | the II | Frost II / II / V | - | live I / II pattern, Zone 3 metal |
| Lines III (Braided / Steady / Twin / Scholar's) | `Ingredient_Bolt_Silk` x6 (+ `Ingredient_Tree_Sap` x3 Steady, + `Food_Fish_Raw` x6 Twin) | the II | Frost V / V / VII / V | - | spec 4.2 fibre ladder (fibre -> linen -> silk) |
| Sinkers III (Weighted / Clean / Deep) | Zone 3 cobble x6 / x6 / x8 (UNVERIFIED 4) | the II | Frost IV | - | spec 4.2 stone ladder |

Live Copper / Iron rods: change their metal gate IV -> II too (lifelong-tool rule; question 4). R3 holds: no recipe has a coin price.
Costs above are GUESSES anchored on the pickaxe ladder in `research/balance/gear.md` line 274 (a P0 dump from 2026-10-18) - the builder re-reads
SkyyGear's live `lifelong.ladders` default and copies the pickaxe step costs if they changed (UNVERIFIED 5).

## 6. Server Setup rows (SkyWynn Menu -> Server Setup -> Fishing; `tools/CONFIG-CONTRACT.md` Object[11] rows, all `live`)

New rows only; every live row keeps its key, default and file line. Labels <= 40 chars, help <= 100 (the live build asserts it).

| Key | Label | Cat | Type | Default | Min-max | Unit | Help |
|---|---|---|---|---|---|---|---|
| `fish.zone.tops` | Zone top levels | general | text | 20,40,60,80,100 | len 60 | - | Water whose level band tops at or below a number is that zone (Zone 1 first). |
| `fish.zone.default` | Zone where no level is known | general | int | 1 | 1-5 | - | Islands and worlds without level bands fish this zone. |
| `fish.zone.maxBuilt` | Highest zone with fish | general | int | 3 | 1-5 | - | Water in a higher zone uses this zone's fish until more are added. |
| `fish.duneTiers` | Dune Fish tier counts | general | text | 25,50,100,250,500,1000,2500,5000 | len 120 | - | 8 counts: Zone 2 fish landed for Dune Fish I to VIII. |
| `fish.frostTiers` | Frost Fish tier counts | general | text | 25,50,100,250,500,1000,2500,5000 | len 120 | - | 8 counts: Zone 3 fish landed for Frost Fish I to VIII. |
| `fish.season.enabled` | Seasons change which fish bite | catch | bool | true | - | - | Uses Dynamic Seasons when it is installed; off or missing = no season lean. |
| `fish.season.inMult` | In season | catch | dec | 1.5 | 0-10 | x | A fish in its season bites this many times as often. |
| `fish.season.outMult` | Out of season | catch | dec | 0.5 | 0-10 | x | A fish out of its season bites this many times as often (0 = never). |
| `fish.time.enabled` | Time of day changes which fish bite | catch | bool | true | - | - | Off = every fish bites at any hour. |
| `fish.time.inMult` | Right time of day | catch | dec | 1.5 | 0-10 | x | A fish at its time of day bites this many times as often. |
| `fish.time.outMult` | Wrong time of day | catch | dec | 0.5 | 0-10 | x | A fish at the wrong time bites this many times as often (0 = never). |
| `fish.time.dawn` | Dawn hours | catch | range | 5-7 | 0-24 | h | Game-clock hours that count as dawn. |
| `fish.time.dusk` | Dusk hours | catch | range | 18-20 | 0-24 | h | Game-clock hours that count as dusk. Day = dawn end to dusk start, night = the rest. |
| `fish.z3.winterBite` | Zone 3 winter bite time | cast | dec | 0.67 | 0.1-5 | x | In winter Zone 3 bite times are this many times as long (ice-hole fishing is quick). |
| `fish.z2.perKg` | Zone 2 price per kg | money | dec | 41 | 0-100000 | coins | A whole Normal Zone 2 fish sells for its weight x this. |
| `fish.z3.perKg` | Zone 3 price per kg | money | dec | 82 | 0-100000 | coins | A whole Normal Zone 3 fish sells for its weight x this. |
| `fish.treasure.zoneMult` | Lost Property coins by zone | treasure | text | 1,4,20 | len 60 | x | Purse coins x this in Zone 1, 2, 3 (more zones: add numbers). |
| `fish.rod.<tier>.maxKg` | (live rows) labels use the SHOWN name | gear | - | live | - | - | e.g. "Chromium rod max fish weight" for `fish.rod.adamantite.maxKg`. |
| `fish.reel.thorium.power` / `.cobalt.` / `.adamantite.` / `.mithril.` | Thorium / Cobalt / Chromium / Azurvane reel power | gear | dec | 6.6 / 7.6 / 8.7 / 9.8 | 0.1-100 | - | live help text |

New tables (`tables` category, `reload@...` binding like the live ones; prefixes never overlap a live prefix):

| Key | Label | Columns | Default entries |
|---|---|---|---|
| `fish.z2.species` | Zone 2 species | dec\|dec\|dec; Spawn weight\|Min kg\|Max kg | the 8 Zone 2 rows of section 3.1 |
| `fish.z3.species` | Zone 3 species | same | the 9 Zone 3 rows |
| `fish.when` | Fish seasons and times | text\|text; Seasons\|Times (`spring summer`, `any`; `dawn dusk`) | all 27 species (Zone 1 from the catalog 3.1) |
| `fish.z2.junk` | Zone 2 junk | int; Weight (`entry=item`) | spec 7.1 Z2 column: Stick 8, Fibre 10, Linen scrap 10, Poop 4, Rubble_Stone 14, Rock_Salt 16, Deco_Coral_Shell 3 + `_Purple` 3 + `_Sanddollar` 3 + `_Swirly` 3, Deco_Starfish 10, Deco_Trash 10, Deco_Trash_Pile_Small 6 (sum 100) |
| `fish.z3.junk` | Zone 3 junk | same | Z3 column: Stick 12, Fibre 10, Linen scrap 14, Plant_Flower_Water_Blue 2 + `_White` 2 + `_Duckweed` 2, Rubble_Stone 22, Rock_Salt 14, Deco_Trash 12, Deco_Trash_Pile_Small 8, Deco_Trash_Pile_Large 2 (sum 100) |
| `fish.parts3` | Part effects, tier III | dec; Tier III | barbed 15, lostproperty 3, lure 15, braided 2, steady 35, twin 6, scholars 6, weighted 15, clean 75, deep 15 (spec 4.2) |

`fish.parts3` is a NEW table on purpose: the live `fish.parts` table has two columns (I, II) and changing its column count would need a one-time
migration of every server's file. Times stay in seconds (`fish.z3.winterBite` is a multiplier). No migration in this round.

Zone treasure contents (data in code, like the live TREASURE table): Zone 2 materials swap `Ore_Copper` / `Ore_Iron` / `Wood_Oak_Trunk` for
`Ore_Thorium` / `Ingredient_Bar_Thorium` / `Wood_Gumboab_Trunk`; Zone 3 for `Ore_Cobalt` / `Ingredient_Bar_Cobalt` / `Wood_Redwood_Trunk`, and the
Zone 3 Great "items" share gives `Skyy_Ench_Cobalt` x1 at 10 % (spec 7: "a few Enchanted at Z3+"). Purse shares unchanged.

## 7. Balance numbers (python, catalog model; 134 fish per hour, u^2 weight roll, heavier-than-rod re-rolled)

| What | Value | Target | Source of the target | OK |
|---|---|---|---|---|
| Z1 income, Copper / Iron rod (unchanged, base 26) | 7,910 / 12,072 per h | 6,863 gathering sales/h, 8,333 target | `research/balance/targets.md` section 3 | yes |
| Z2 income, Iron / Thorium rod (base 41) | 21,760 / 35,135 per h | 35k sales/h, 43k target | same | yes (Thorium = the zone's rod) |
| Z2 income, Cobalt rod (full size) | 48,352 per h | under Z3 entry | - | yes |
| Z3 income, Cobalt / Chromium / Azurvane rod (base 82) | 86,732 / 175,167 / 254,460 per h | 256k sales/h, 307k target | same | yes at the zone's top rod |
| Catalog bases for comparison | Z2 28, Z3 34 gave 24,000 / 105,500 at the same rods | spec targets 24k / 85k (old, pre-P7) | `research/cloud/Fish-Species-Catalog.md` 4 | replaced: P7 raised the targets |
| Fabled / Mythic average sale | Sandsalmon 4,592; Sleeper 102,500 | about 0.1-0.4 h of zone income | catalog 3 "jackpot, never break the economy" | yes |
| Lost Property purse coins per hour | Z1 438, Z2 1,754 (x4), Z3 8,769 (x20) | 5-7 % of income | spec 7 | Z2 5.0 %, Z3 5.0 % at Chromium (10 % Cobalt, 3.4 % Azurvane) |
| Fillet vs whole (Normal, per kg) | fillet 2 x 9 x 0.9 = 16.2 coins; whole Z1 26 / Z2 41 / Z3 82 | fillet < whole, no loop | `research/balance/economy.md` line 486 (`Food_Fish_Raw` base 9) | yes |
| Reel Power T3-T6 | 6.6 / 7.6 / 8.7 / 9.8 | spec 4.1 | `research/cloud/SkyyFishing-Spec-Draft.md` 4.1 | yes |
| Rod max kg T3-T6 | 16 / 25 / 40 / 60 | live rows | `research/balance/gathering.md` lines 1115-1118 | yes |
| Fish caps | speed 100, treasure 15, double 20, bar start 60, time 16 s, surge cut 50 | all part III values fit (bar start 35 + 15 = 50; time 12 + 2 = 14) | `research/balance/gathering.md` lines 1123-1128 | yes |
| Fishing XP | unchanged (`fish.xp.mult` 6 x rarity XP x SkyySkills level factor) | Fishing lag 15 (GUESS) | `research/balance/targets.md` line 10 | measure in game |

Every species at every rod tier: Z2 lands 6 of 8 at Iron, 7 at Thorium, 8 at Cobalt; Z3 lands 5 at Thorium / Cobalt, 7 at Chromium, 9 at Azurvane
(every rod step opens a species or a full-size ceiling - catalog 4 rule holds).
Note: `research/balance/gathering.md` line 1079 shows `fish.xp.mult` 1 (that P0 dump predates 0.1.12's migration to 6).

## 8. Saved data, bridges, other mods

| Item | Change |
|---|---|
| `mods/Skyy_SkyyFishing/players/<pkey>.properties` | + `dune=<n>`, `frost=<n>` (fish landed per zone, active profile, `tools/PROFILES-CONTRACT.md`); missing = 0. The live Pond count key is unchanged. |
| `fishing:fn:pond` | answers the TOTAL fish landed (Pond + Dune + Frost) - SkyySacks 0.8.10+ uses it to level the Fishing bag (`SkyySacks/build_skyysacks_0.8.28.py` line 5414), so Zone 2-3 fish level the bag with no Sacks rebuild (question 6). |
| `fishing:fn:fishOf` / `fishDoc`, the Void bench | unchanged; SkyySacks' rule `SkyyFishing_Fish_*` already takes every new species |
| SkyyGear (builder B) | `LL_POLE_LAD` (`SkyyGear/build_skyygear_0.3.40.py` line 21730) gets `SkyyFishing_Rod_Thorium,_Cobalt,_Adamantite,_Mithril`; the pole's tier word / level band read the SHOWN metal (Rod_Adamantite = Chromium 48-55, Rod_Mithril = Azurvane 55-63; UNVERIFIED 6 how Gear derives it today) |
| `tools/tier_tags.py` (builder A) | + owner `SkyyFishing`, + OWN_LADDERS word `Fish`, + rows for the 8 rods, 7 reels, 27 fish (ids in a `FI_IDS` frozenset, not in Assets.zip, like `WG_IDS`); `tools/test_tier_tags.py` skips FI_IDS in its Assets check |
| SkyyBazaar Fishing tab | must list the 17 new species (economy.md line 135); grep finds no `SkyyFishing_Fish_` in `SkyyBazaar/build_skyybazaar_0.2.1.py` - UNVERIFIED 7 how the tab gets them |

## 9. Builder split (one mod per builder; Full round: new items, saved data, coins, several mods)

| Builder | Model | Files (only these) |
|---|---|---|
| A - SkyyFishing 0.2.0 | Opus | `tools/fishing_0_2_0_patch.py` (reads `SkyyFishing/build_skyyfishing_0.1.12.py`, writes `SkyyFishing/build_skyyfishing_0.2.0.py`), `SkyyFishing/test_skyyfishing_0.2.0.py`, `tools/tier_tags.py`, `tools/test_tier_tags.py` |
| B - SkyyGear next (after the SET pin; the gear041 round is in flight - build on whatever the SET pins then) | Opus | `tools/gear_<ver>_patch.py`, its generated script + test |
| C - SkyyBazaar (only if UNVERIFIED 7 shows a fixed list) | Opus, lean | `tools/bazaar_<ver>_patch.py` + script + test |
| Review / cross-check | Sonnet | `python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python tools/ci/lint.py` (0 fails), `python tools/ci/langdup.py` |

Builders follow `tools/AGENT-BRIEF.md` (no commits, no deploy, javassist limits, COMMAND RULES). New admin sub-commands under `/fishing admin`:
`dune <n>`, `frost <n>` (set the counts, like the live `pond <n>`), `zone` (prints the zone, level band, season and time at your position) -
each `requirePermission(...)` + `setPermissionGroups(new String[0])` (lint perm_group_leaks). `give <species>` takes the new keys.

## 10. Harness checks (SkyyFishing/test_skyyfishing_0.2.0.py, plus the build's own asserts)

| # | Check |
|---|---|
| H1 | 27 species, ids unique, every Zone 2-3 icon file exists and is 64 x 64; every vanilla look id + its model / texture is in Assets.zip |
| H2 | each zone's spawn weights > 0; the zone tables sum to the catalog's totals (Z2 83.65, Z3 86.86); junk tables sum to 100 |
| H3 | the 12 % max-length assert holds for all 27 (K from min kg / min cm) |
| H4 | income model (this file's section 7) re-computed from the build's tables: Z2 Thorium 35,135 +-1 %, Z3 Azurvane 254,460 +-1 % |
| H5 | every rod T3-T6 lands at least one new species or a new full-size ceiling (catalog 4 rule) |
| H6 | zone pick: levelAt hi 15 -> Z1, 25 -> Z2, 45 -> Z3, 70 -> Z3 (maxBuilt), null -> `fish.zone.default`; a broken `fish.zone.tops` text -> the default tops + WARN once |
| H7 | season / time lean on a stand-in clock and season source: in x1.5, out x0.5, "any" x1, source missing = x1; Z3 winter bite x0.67 only in winter and Zone 3 |
| H8 | the rod re-roll never returns a fish heavier than the rod's max, for every rod x zone (10,000 rolls each, seeded) |
| H9 | recipes: every new output has exactly one recipe, consumes the tier below, no bamboo, no coin cost; Rod_Mithril needs Cobalt V AND Chromium V; list sorted by tier then name |
| H10 | tier tags: every rod / reel / fish description starts with `TT.described(...)`'s tag; `tools/ci/langdup.py` clean (no key written by two jars) |
| H11 | saved data: a 0.1.12 players file (no dune / frost) loads as 0 / 0; a 0.2.0 file round-trips; `fishing:fn:pond` = pond + dune + frost |
| H12 | config: every new row label <= 40, help <= 100; `fish.parts3` prefix does not overlap `fish.parts.`; a 0.1.12 config file loads with every new row at its default and no line rewritten |
| H13 | tackle model assert = 37 items; 10 part III items have models + icons |
| H14 | Clerk price uses the fish's zone base (`fish.price.perKg` / `fish.z2.perKg` / `fish.z3.perKg`) x rarity mult x demand; treasure purse x `fish.treasure.zoneMult` |
| H15 | `python tools/smoke_test.py --jar SkyyFishing/SkyyFishing-0.2.0.jar` (+ the Gear jar): `[SkyyFishing] 0.2.0 ready`, no asset-validation failure, no SEVERE |

## 11. Rollback and FLOOR notes (for `tools/deploy_set.py`, main session writes them)

| Note | Text |
|---|---|
| New FLOOR | Once any Zone 2-3 fish, a T3+ reel (`SkyyFishing_Reel_Thorium` .. `_Mithril`) or a part III item exists, never roll SkyyFishing below 0.2.0 - 0.1.12 has no such items (unknown items) |
| Pair | SkyyFishing 0.2.0 + SkyyGear <next> deploy + roll back TOGETHER (an older Gear does not know the T3-T6 poles: no tier / level band after a bench upgrade) - add a STOP check like the fish018 / fishvoid ones |
| Kept floors | SkyyFishing 0.1.12 Balance P3 group (Skills 0.4.57 + Cooking 0.1.15 + Exploration 0.3.2 + Collections 0.2.30 + Pets 0.4.7), 0.1.10 + SkyySacks 0.8.17, 0.1.8 + SkyySacks 0.8.10, the R3b readers (SkyyTrees 0.4.1) - 0.2.0 is above all of them |
| Rolling back to 0.1.12 anyway | the `dune=` / `frost=` lines are ignored by 0.1.12 (UNVERIFIED 8) and come back with 0.2.0; new config rows stay in the file unused |
| Rod gate IV -> II | a pure default change of code (no config row), nothing to undo |

## 12. In-game test steps (numbered, for `docs/tests/<month>.md`)

1. Fishing Bench > Parts: the list is sorted by tier; Thorium rod shows "Dune Fish III + Thorium collection II" when locked; no coin prices anywhere.
2. `/fishing admin dune 100`, have the bars + Thorium collection II, craft the Thorium Fishing Rod from your Iron one: same lifelong pole, name "[Lv N]", tooltip starts "T4 Thorium".
3. `/zone 2`, stand at oasis water, `/fishing admin zone`: says Zone 2, the level band, the season and the time of day.
4. Fish 10 casts in Zone 2: catches are Zone 2 species ("T4 Fish - ... from Zone 2 (Dune Fish)"), no fish over 16 kg with the Thorium rod; `/fishing` shows the Dune Fish count going up.
5. Sell a Zone 2 fish at the bench: price = kg x 41 x rarity (Normal 1, Unique 1.5 ...); the same fish weight from Zone 1 pays x26.
6. Put a Zone 2 fish in the Void: the Fishing bag level counts it; the bench Fillet and Sell list shows it.
7. `/zone 3`, fish at night in winter if you can: Glass Pike / Whisper Sturgeon need the Chromium / Azurvane rod; with Cobalt only 5 species bite. Bites feel quicker in winter.
8. `/fishing admin frost 2500`: craft Cobalt, Chromium and Azurvane rods + their reels in order; Azurvane asks for Cobalt V AND Chromium V; tags T7 / T8 / T9.
9. Craft one part III of each kind (Frost II-VII), fit them on the Rig tab; Rig total shows the III values and no stat over its cap.
10. Server Setup > Fishing: the new rows show (zone tops, seasons, time, Zone 2-3 price, Zone 2-3 species / junk, Part effects III); set Zone 3 price to 100, sell a fish, it pays more at once; Undo in Changes.
11. On your island pond: fish are Zone 1 (the zone default).
12. Bazaar > Fishing tab lists the new species (if builder C ran).
13. After the session: check server + client logs for SkyyFishing / SkyyGear warnings (`skywynn-logs`).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Adamantite and Mithril come from Zones 4 / 5, but the catalog needs two more rods in Zone 3. Show rods T5 / T6 as **Chromium** and **Azurvane** Fishing Rods (Zone 3 metals, same item ids, no data change)? | [yes] |
| 1b | Re-tint their art to Chromium (silver-cyan) / Azurvane (blue) at build time? | [yes, keep the old art if the tint looks bad] |
| 2 | Only 8 rod items exist (locked), so Lead / Dusk have no rod: the pole's level stays capped at 28 until the Cobalt rod (Lv 40). OK, or let the pole's cap reach the next rod's start (39)? | [cap reaches 39] |
| 3 | Fish tier tags: "T4 Fish" = the zone's first tier, or higher when only a bigger rod lands it (Glass Pike T8, Sleeper T9)? | [yes, as written] |
| 4 | Fishing rods follow the lifelong-tool rule (metal collection II, not IV) - also lower the live Copper / Iron rod gates to II? | [yes] |
| 5 | Fish prices: Zone 2 41 coins / kg and Zone 3 82 (the catalog had 28 / 34) so fishing earns about what other gathering earns there after the P7 economy pass? | [yes] |
| 6 | Zone 2-3 fish also level your Fishing bag (the bag counts all fish landed)? | [yes] |
| 7 | In Zone 2-3, does any water in the zone use the zone's fish table, or should some fish need a special water (tar pits, hidden oasis, deep ice hole)? | [any water now; special waters with the Ledger] |
| 8 | The Onyxium rod (no recipe yet) becomes the Zone 4 lava rod in stage 3 - rename it then (Adamantite / Slag / Cinder)? | [decide in stage 3] |
| 9 | If Dynamic Seasons has no readable season, ship without season lean (time of day still works)? | [yes] |

## For the local session (UNVERIFIED)

| # | Item |
|---|---|
| 1 | Dynamic Seasons 7.0.4: a readable current season (public static getter, resource, event or a bridge key) and its season names; map to spring / summer / autumn / winter. Read its jar only (`tools/dev/cpgrep.py`), never copy |
| 2 | `mob:fn:levelAt` answers in the zone world (WorldGen 0.7 `skywynn_zones2`) for water blocks at the bobber, and what it answers on islands (null expected) |
| 3 | The vanilla look ids in section 3.1 exist (`Fish_Piranha_Item`, `Fish_Piranha_Black_Item`, `Fish_Frostgill_Item`, `Fish_Snapjaw_Item`, `Fish_Shark_Hammerhead_Item`, `Fish_Whale_Humpback_Item`, `Fish_Tang_Sailfin_Item` are in `research/balance/economy.md` lines 486-517, models / textures not checked); a whale model may be too big as a held fish - swap if so |
| 4 | Zone 3 cobble id for part III sinkers (spec said Slate; Zone 3's Chromium host is Shale - e.g. `Rock_Shale_Cobble` or `Rock_Slate_Cobble`); and that `Ingredient_Bolt_Silk` is obtainable in Zone 3 (it exists: the live TACKLE_LOOK asserts it) |
| 5 | SkyyGear's current `lifelong.ladders` pickaxe step costs (P0 dump is from 2026-10-18, before "plain until Dusk"); copy them into the rod recipes |
| 6 | How SkyyGear 0.3.40+ derives a pole's tier word / level band (id word, a table, or SkyyFishing's document) - the shown-metal mapping must reach it |
| 7 | How SkyyBazaar's Fishing tab gets SkyyFishing fish (no `SkyyFishing_Fish_` in `SkyyBazaar/build_skyybazaar_0.2.1.py`; maybe bz0115 is not built yet) |
| 8 | SkyyFishing 0.1.12's players-file reader ignores unknown keys (`dune=`, `frost=`) |
| 9 | `WorldTimeResource.getGameTime()`: does hour 0 of the game day = midnight (epoch seconds mod 86400)? Else read the hour another way |
| 10 | Zone 3 water: is there liquid water under the ice (ice-hole fishing works by breaking ice by hand) and does `fish.needWide` still pass in a 1-block hole (else Zone 3 needs open water) |
| 11 | Whether adding default entries to a NEW table (`fish.z2.species` ...) shows them on an existing server whose config file lacks those lines (expected yes: kit defaults) |
| 12 | Income is paper: measure fish per hour and coins per hour in a real Zone 2 / Zone 3 session (catalog UNVERIFIED 5) |
