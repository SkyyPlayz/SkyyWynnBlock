# Fish Species Catalog (SkyyFishing)

Cloud draft, 2026-10-06. Paper design; nothing built. Every number is a placeholder and a Server Setup row (times in seconds).
Inputs read: `CLOUD-RESUME.md` task "Fish species catalog"; `research/cloud/SkyyFishing-Spec-Draft.md` (sections 3-8, 11, 13);
`research/cloud/Food-Expansion-Draft.md` section 7; `research/cloud/Outposts-List.md` + `Mob-Levels-Refit.md` (biome names per zone);
`docs/answered/skills.md` (LOCKED 2026-10-06 FISHING, POTIONS "dynamic season ... fishing seasons"); `docs/answered/project.md` (Dynamic Seasons);
`PACK.md` (HyFishing, Dynamic Seasons: no licence in the jars, no copying). All 39 species are our own invention; no name, weight or number comes from
HyFishing, Angler's Almanac or SkyBlock.

**Decisions followed (not re-decided):** our own fishing mod; ROD = max weight / length (a heavier fish never bites - spec default); sell price by weight;
fish collections Pond / Dune / Frost / Lava / Cave (1 per landed fish); fish = Meat family, dish tier set by rarity (Food-Expansion section 7);
seasons come from Dynamic Seasons and must work with ours; no oceans (R5); lava fishing later (Zone 4), caves later (Zone 5); R3 (no shop sells
rods, parts or unlocks); weight / length only change the price, never the food power; Fillets and Bazaar spread rules (buy = base x 1.10,
sell = base x 0.90).

## 1. What this file adds to the spec

| Spec says | This file |
|---|---|
| "Species weighted per zone", 5 working names per zone | 39 species with water type, season, time, rarity, weight, length, bite time, price, dish |
| Grade (Common .. Legendary) is a separate roll on top of the species | **Proposal:** the species' own rarity IS the grade (Normal / Unique / Rare / Legendary / Fabled / Mythic, the pack's rarity names). One roll less; the odds per zone come out Normal 42-69%, Unique 22-46%, Rare 5-14%, Legendary 1.3-3.3%, Fabled + Mythic 0.1-0.3% (section 5; the spec had 62 / 24 / 10 / 3.5 / 0.5). Barbed Hook still scales the non-Normal share. Question 1 |
| Z3 "winter x1.5 for all" | A flat x1.5 on every species changes nothing (odds are relative). Replaced by: each species has its own season list (in season x1.5, off season x0.5) plus **winter bite time x0.67** in Z3 (ice-hole fishing is quicker when it is cold) |
| Price per kg Z1 18 / Z2 20 / Z3 28 / Z4 32 / Z5 40, grade mult 1 / 1.5 / 2.5 / 4 / 8 | Zone base per kg **26 / 28 / 34 / 36 / 36** and rarity mult **1 / 1.5 / 2.5 / 6 / 12 / 25**, fitted so the income per hour still matches the spec (section 5) |

Rarity mult: Normal 1, Unique 1.5, Rare 2.5, Legendary 6, Fabled 12, Mythic 25 (`fish.price.rarityMult`). Weight is rolled as
`w = min + (max - min) x u^2` (spec section 5); a fish heavier than the rod's max is re-rolled. Length = `(100 x grams / K)^(1/3)` cm (spec formula,
K = species shape, eels 0.6, trout 1.0, carp 1.4, rays 2.5, halibut 2.2; the +-5% jitter on top is not shown). **Bite s** = `fish.biteMin` 6 and
`fish.biteMax` 18 times the species' bite factor (0.8 minnow .. 2.2 leviathan: rare fish are shy), before the Fishing Speed divisor.
**Time** = day / night / dawn / dusk / any: in time x1.5, out of time x0.5 (like season). **Weight** column = spawn weight inside the zone.

## 2. How to read the zone tables

- **Season** uses the four vanilla-style seasons (spring / summer / autumn / winter; the real list and names are **UNVERIFIED**, UNVERIFIED 1).
  "any" = never leaned. Z4 and Z5 are season-free (lava and caves; spec), so they only use time of day.
- **Water / biome** uses the world-gen biome names from `Outposts-List.md` where one exists (Forest_Swamp, Desert_Oasis, Desert_Springs,
  Desert_Hotsprings, Oasis_Hidden, Scrub_Tar_Pits, Wastes_Lava). Other water types (pond, river, ice hole, lava lake ...) are the spec's per-zone
  water; exact biome-to-water mapping is UNVERIFIED 2.
- **Sell/kg** = zone base x rarity mult, rounded. Whole fish sell to the Clerk by weight (spec section 6).
- **Dish (tier)** = the signature dish the fish is named in (flavour only: any fish works in any fish dish). Tier = Normal T1, Unique / Rare T2,
  Legendary / Fabled / Mythic T3 (Food-Expansion section 7). Fish Sticks and Cinderfin Jerky are the spec's proposed dishes, the rest are Food-Expansion's
  (Grilled Fish, Fish Skewer, Fish and Chips, Fish Stew, Sushi Roll).
- Every species also fills its zone's collection (Pond Fish Z1, Dune Fish Z2, Frost Fish Z3, Lava Fish Z4, Cave Fish Z5) and the Angler's Ledger page.

## 3. Species by zone

Voice: the Department of Arrivals' waters are where the lost luggage and the unfiled forms wash up - the fish are named for it, sparingly.

### 3.1 Zone 1 - Emerald Wilds (Lv 1-20, collection Pond Fish)

| Species | Water / biome | Season | Time | Rarity | kg | cm | Bite s | Weight | Sell/kg | Dish (tier) |
|---|---|---|---|---|---|---|---|---|---|---|
| Overdue Minnow | pond, river | any | any | Normal | 0.05-0.4 | 18-35 | 4.8-14.4 | 22 | 26 | Fish Sticks (T1) |
| Bluegill of Good Standing | pond | spring, summer | day | Normal | 0.1-1.2 | 20-46 | 5.4-16.2 | 22 | 26 | Grilled Fish (T1) |
| Rustback Trout | river, cold pond | spring, autumn | dawn, dusk | Normal | 0.5-5 | 37-79 | 6-18 | 20 | 26 | Grilled Fish, Fish Skewer (T1) |
| Queue Perch | pond | any | day | Normal | 0.3-2.5 | 30-61 | 6-18 | 16 | 26 | Grilled Fish (T1) |
| Misfiled Carp | pond, swamp | autumn, winter | any | Unique | 2-9 | 52-86 | 6.6-19.8 | 10 | 39 | Fish Skewer (T2) |
| Stamped Catfish | river, pond | summer | night | Unique | 3.5-12 | 73-110 | 7.2-21.6 | 10 | 39 | Fish and Chips (T2) |
| Mirebridge Eel | swamp (Forest_Swamp) | spring, summer | night | Unique | 1-6 | 55-100 | 7.2-21.6 | 9 | 39 | Fish Skewer (T2) |
| Pondering Pike | pond, river | any | day | Rare | 6.5-18 | 93-131 | 7.8-23.4 | 6 | 65 | Fish and Chips (T2) |
| Golden Receipt Koi | pond | spring | day | Legendary | 1.5-7 | 47-79 | 9-27 | 1.6 | 156 | Fish Stew (T3) |
| Departmental Goldfish | any Z1 water | any | night | Fabled | 0.2-1 | 26-44 | 10.8-32.4 | 0.25 | 312 | Sushi Roll (T3) |

### 3.2 Zone 2 - Howling Sands (20-30, Dune Fish)

| Species | Water / biome | Season | Time | Rarity | kg | cm | Bite s | Weight | Sell/kg | Dish (tier) |
|---|---|---|---|---|---|---|---|---|---|---|
| Oasis Carp | oasis, springs | summer | any | Normal | 1-8 | 41-83 | 5.4-16.2 | 20 | 28 | Grilled Fish (T1) |
| Sandskipper | oasis shallows | any | day | Normal | 0.5-4 | 37-74 | 4.8-14.4 | 22 | 28 | Fish Sticks (T1) |
| Dune Piranha | oasis, hot springs | any | dusk, night | Normal | 1-6 | 45-82 | 5.4-16.2 | 16 | 28 | Fish Skewer (T1) |
| Mirage Eel | oasis, hidden oasis | autumn, winter | night | Unique | 2-14 | 69-133 | 7.2-21.6 | 10 | 42 | Fish Skewer (T2) |
| Lost Luggage Grouper | oasis, hot springs | any | any | Rare | 11-25 | 103-136 | 8.4-25.2 | 6 | 70 | Fish and Chips (T2) |
| Tar Pit Gudgeon | tar pits | any | any | Unique | 3-12 | 63-100 | 7.8-23.4 | 8 | 42 | Fish Stew (T2) |
| Mirage Sturgeon | hidden oasis | summer | dawn | Legendary | 17-34 | 129-162 | 9.6-28.8 | 1.4 | 168 | Fish Stew (T3) |
| Customs-Cleared Sandsalmon | hot springs | spring | any | Fabled | 6-16 | 84-117 | 10.8-32.4 | 0.25 | 336 | Sushi Roll (T3) |

### 3.3 Zone 3 - Whisperfrost (30-45, Frost Fish)

| Species | Water / biome | Season | Time | Rarity | kg | cm | Bite s | Weight | Sell/kg | Dish (tier) |
|---|---|---|---|---|---|---|---|---|---|---|
| Frost Cod | ice hole | winter | day | Normal | 2-15 | 58-114 | 5.4-16.2 | 22 | 34 | Grilled Fish (T1) |
| Whisper Char | ice hole, frozen lake | any | dawn, dusk | Normal | 1-10 | 46-100 | 5.4-16.2 | 18 | 34 | Fish Skewer (T1) |
| Icebound Salmon | frozen river | autumn, winter | any | Unique | 3-24 | 67-134 | 6.6-19.8 | 12 | 51 | Fish and Chips (T2) |
| Glass Pike | frozen lake | winter | night | Rare | 26-48 | 148-182 | 7.8-23.4 | 6 | 85 | Fish Stew (T2) |
| Permit Lamprey | frozen river | spring, summer | night | Unique | 4-20 | 93-159 | 7.8-23.4 | 9 | 51 | Fish Stew (T2) |
| Snowmelt Trout | redwood streams | spring | day | Normal | 2-12 | 58-106 | 6-18 | 14 | 34 | Grilled Fish (T1) |
| Whisper Sturgeon | deep ice hole | winter | night | Rare | 41-60 | 166-188 | 9-27 | 4.5 | 85 | Sushi Roll (T2) |
| Blizzard Halibut | frozen lake | winter | any | Legendary | 30-60 | 111-140 | 9.6-28.8 | 1.3 | 204 | Fish Stew (T3) |
| The Sleeper in Aisle 9 | deep ice hole | winter | night | Mythic | 45-60 | 171-188 | 12-36 | 0.06 | 850 | Sushi Roll (T3) |

### 3.4 Zone 4 - Devastated Lands (45-60, Lava Fish; lava rod T7+, stage 3)

| Species | Water / biome | Season | Time | Rarity | kg | cm | Bite s | Weight | Sell/kg | Dish (tier) |
|---|---|---|---|---|---|---|---|---|---|---|
| Cinderfin | lava pool | any | any | Normal | 5-30 | 79-144 | 5.4-16.2 | 22 | 36 | Cinderfin Jerky (T1) |
| Slag Ray | lava lake | any | any | Unique | 10-60 | 74-134 | 6.6-19.8 | 12 | 54 | Cinderfin Jerky (T2) |
| Ashen Eel | lava, geyser pools | any | night | Unique | 8-45 | 110-196 | 6.6-19.8 | 12 | 54 | Fish Skewer (T2) |
| Stamp-Scorched Kingfish | lava lake | any | day | Rare | 45-90 | 165-208 | 8.4-25.2 | 5 | 90 | Fish Stew (T2) |
| Magma Marlin | Wastes_Lava | any | day | Legendary | 62-90 | 190-215 | 10.2-30.6 | 1.2 | 216 | Sushi Roll (T3) |
| Refund-Pending Phoenixfish | lava lake | any | dusk | Mythic | 65-90 | 187-208 | 12-36 | 0.06 | 900 | Fish Stew (T3) |

### 3.5 Zone 5 - Dinosaur Caves (60-75, Cave Fish; rod T8+, stage 4)

| Species | Water / biome | Season | Time | Rarity | kg | cm | Bite s | Weight | Sell/kg | Dish (tier) |
|---|---|---|---|---|---|---|---|---|---|---|
| Blind Gar | cave lake | any | any | Normal | 20-90 | 136-224 | 6-18 | 20 | 36 | Grilled Fish (T1) |
| Fossil Coelacanth | cave lake | any | any | Unique | 40-130 | 149-221 | 7.2-21.6 | 10 | 54 | Fish Stew (T2) |
| Drake-Eel | lava lake landing | any | night | Rare | 95-180 | 251-311 | 9-27 | 5 | 90 | Fish Stew (T2) |
| Bone Pit Sturgeon | cave lake (bone pit) | any | dawn | Rare | 190-330 | 276-332 | 9-27 | 4 | 90 | Fish Stew (T2) |
| Pondersaur | jungle cave lake | any | dusk | Legendary | 135-260 | 238-296 | 10.2-30.6 | 1.2 | 216 | Sushi Roll (T3) |
| Final Notice Leviathan | dragon-nest lake | any | night | Mythic | 255-450 | 294-356 | 13.2-39.6 | 0.06 | 900 | Fish Stew (T3) |

Winter in Z1: ponds ice over at the edges but still bite; only Misfiled Carp is winter-leaned, the 4 "any" fish carry the season. Season counts
(species leaned to a season, python): Z1 spring 4 / summer 3 / autumn 2 / winter 1, Z2 1 / 2 / 1 / 1, Z3 2 / 1 / 1 / 6 (winter is the Z3 fishing season).
Time of day: 9 species day, 12 night, 4 dawn, 5 dusk, 12 any (some have two).
**Fabled and Mythic finds** (5 species): Departmental Goldfish (Z1), Customs-Cleared Sandsalmon (Z2), The Sleeper in Aisle 9 (Z3), Refund-Pending
Phoenixfish (Z4), Final Notice Leviathan (Z5). They are in-lore "unclaimed" prizes: spawn weight 0.25 / 0.25 / 0.06 / 0.06 / 0.06, so per fish caught in
that zone the chance is 0.21% / 0.30% / 0.07% / 0.12% / 0.15%, i.e. one in 467 / 335 / 1,448 / 871 / 671 fish = about 3.5 / 2.5 / 10.8 / 6.5 / 5.0 hours of
fishing at 134 fish per hour (spec rate). Average sale at the Clerk (python): Goldfish ~150, Sandsalmon ~3,100, Sleeper ~42,500, Phoenixfish ~66,000,
Leviathan ~288,000 - about 0.6 to 1 hour of that zone's income each (Z5 over 20 min), so they feel like a jackpot but never break the economy. A Fabled
or Mythic catch is also **kept as a trophy** option (Ledger gold stamp, record board, hang in a Trophy Case later - question 4).

## 4. Rod tiers: every tier has targets (python check)

Rod max kg from the spec (3 / 6 / 10 / 16 / 25 / 40 / 60 / 90 / 130 / 180 / 250 / 340 / 450). A zone is played from the tier shown (Z1 from T0, Z2 from T2,
Z3 from T4, Z4 lava from T7, Z5 caves from T8; spec). "New" = species whose minimum weight the rod can first reach; "full size" = the rod now lands the
species' top weight. Every rod tier unlocks at least one new species or one full-size ceiling, and every upgrade raises the fish you can land.

| Tier | Rod | Max kg | Zones in play (species the rod can land) | New species at this tier | Full-size ceilings |
|---|---|---|---|---|---|
| T0 | Bamboo | 3 | Z1: 8 of 10 | Minnow, Bluegill, Trout, Perch, Carp, Eel, Koi, Goldfish | Minnow, Bluegill, Perch, Goldfish |
| T1 | Copper | 6 | Z1: 9 | Stamped Catfish | Trout, Mirebridge Eel |
| T2 | Iron | 10 | Z1: 10, Z2: 6 | Pondering Pike + 6 Z2 fish (Oasis Carp, Sandskipper, Piranha, Mirage Eel, Gudgeon, Sandsalmon) | Misfiled Carp, Koi, Oasis Carp, Sandskipper, Piranha |
| T3 | Thorium | 16 | Z1: 10, Z2: 7 | Lost Luggage Grouper | Catfish, Mirage Eel, Gudgeon, Sandsalmon |
| T4 | Cobalt | 25 | Z2: 8, Z3: 5 | Mirage Sturgeon + 5 Z3 fish (Frost Cod, Char, Icebound Salmon, Lamprey, Snowmelt Trout) | Pike, Grouper + all 5 Z3 small fish |
| T5 | Adamantite | 40 | Z3: 7 | Glass Pike, Blizzard Halibut | Mirage Sturgeon |
| T6 | Mithril | 60 | Z3: 9 | Whisper Sturgeon, The Sleeper | Glass Pike, Whisper Sturgeon, Halibut, Sleeper |
| T7 | Onyxium | 90 | Z4: 6 (lava) | all 6 lava fish (Cinderfin .. Phoenixfish) | all 6 (Z4 tops at 90 kg on purpose) |
| T8 | Cindersteel | 130 | Z5: 3 | Blind Gar, Coelacanth, Drake-Eel | Blind Gar, Coelacanth |
| T9 | Amberite | 180 | Z5: 4 | Pondersaur | Drake-Eel |
| T10 | Drakonite | 250 | Z5: 5 | Bone Pit Sturgeon | none (a heavy-fish tier: the bigger ones of T11-T12) |
| T11 | Voidglass | 340 | Z5: 6 | Final Notice Leviathan | Bone Pit Sturgeon, Pondersaur |
| T12 | Aetherium | 450 | Z5: 6 | none | Leviathan (the whole table) |

Income per hour with the zone's own rod (python, 134 fish/h, average weight from the u^2 roll, rarity mult and zone base above):

| Zone | Rod tier: income per hour | Spec target (reference rod) | Result at the reference rod |
|---|---|---|---|
| Z1 | T0 4,700 / T1 7,900 / T2 12,100 / T3 13,300 / T4+ 13,600 | 8,200 (T1) | 7,900 (-4%) |
| Z2 | T2 14,900 / T3 24,000 / T4 33,000 / T5+ 34,200 | 24,000 (T3) | 24,000 (0%) |
| Z3 | T4 36,000 / T5 72,600 / T6+ 105,500 | 85,000 (T5) | 72,600 (-15%) |
| Z4 | T7 232,000 | 218,000 (T7) | 232,000 (+6%) |
| Z5 | T8 448,000 / T9 605,000 / T10 817,000 / T11 901,000 / T12 908,000 | 393,000 (T8) | 448,000 (+14%) |

Reading it: an upgrade inside a zone is worth +30% to +100% until the zone's top fish are full size, then the next zone takes over. Z3 is a little low
at T5 and Z5 a little high at T8; both are one number (zone base per kg) - question 5. Z5 keeps growing to T12 because its fish are huge (that is the
late-game money, but still below the Economy-Audit end-game active income only if the Z5 base stays at 36). The Z4 table has no growth after T7 until the
cave lakes open; that is intended (lava is a one-rod zone).

## 5. Rarity mix per zone (python, share of fish caught at a rod that lands all species)

| Zone | Normal | Unique | Rare | Legendary | Fabled | Mythic |
|---|---|---|---|---|---|---|
| Z1 | 68.5% | 24.8% | 5.1% | 1.4% | 0.21% | - |
| Z2 | 69.3% | 21.5% | 7.2% | 1.7% | 0.30% | - |
| Z3 | 62.2% | 24.2% | 12.1% | 1.5% | - | 0.07% |
| Z4 | 42.1% | 45.9% | 9.6% | 2.3% | - | 0.11% |
| Z5 | 55.2% | 27.6% | 13.8% | 3.3% | - | 0.17% |

Rod tier changes what can be landed, so lower rods see these shares with the too-heavy species removed. Hooks (Barbed Hook +5-20% grade luck) scale
Unique and above; Deep Sinker raises the weight inside the species' range.

## 6. Fillets and the Bazaar (same loop rule as the spec)

Fillet = 1 per 0.5 kg, max 40 (spec). Three fillet products per zone, by band: **Raw Fillet** (Normal), **Fine Fillet** (Unique / Rare),
**Prime Fillet** (Legendary / Fabled / Mythic). Bazaar base set so instant sell is **70% of selling the same fish whole** per 0.5 kg at the band's
lowest rarity (Normal 1, Unique 1.5, Legendary 6) - so filleting never beats the Clerk and a buy-craft-sell loop cannot form (buy = base x 1.10,
sell = base x 0.90; 70% sits far below the 22.2% spread limit and dishes follow `bazaar.maxChainPremium` 15%):

| Zone | Raw base (instant sell) | Fine base (instant sell) | Prime base (instant sell) |
|---|---|---|---|
| Z1 | 10.1 (9.1) | 15.2 (13.7) | 60.7 (54.6) |
| Z2 | 10.9 (9.8) | 16.3 (14.7) | 65.3 (58.8) |
| Z3 | 13.2 (11.9) | 19.8 (17.9) | 79.3 (71.4) |
| Z4 | 14.0 (12.6) | 21.0 (18.9) | 84.0 (75.6) |
| Z5 | 14.0 (12.6) | 21.0 (18.9) | 84.0 (75.6) |

(Round to 0.1 coin in the Bazaar; the formula is `0.7 x zoneBase x bandMult x 0.5 / 0.9`, row `fish.fillet.bazaarRatio` 0.7.)

## 7. Junk and Lost Property in voice

Junk (10% of catches; spec) is **vanilla items** (updated 2026-10-06: vanilla junk - Skyy: "junk draws sticks and fiber and stuff thats already in the
game"). The 7 invented junk items (Soggy Boot, Form 27-B, Wet Queue Ticket, Rubber Stamp, Clump of Seaweed, Scorched Complaint Letter, Gnawed Bone) are
**retired**: none has a use beyond the joke. Junk is never a collection count; the Clerk pays each item its vanilla sell value, capped by
`fish.junk.<id>.price` (a joke, not an income). The per-zone weights are in spec section 7.1. **Lost Property** items are the wrappers for the spec's
treasure table (section 7): the contents (coin purse, materials, unidentified gear, part scrap, now also vanilla Water Essence / Deco_Treasure /
Fishbone Spear) are listed there, only the item the player lands is named in voice, and opens on use. The wrappers stay because they are containers.

| Kind | Item | Where | Sells / role |
|---|---|---|---|
| Junk (vanilla) | `Ingredient_Stick`, `Ingredient_Fibre`, `Ingredient_Fabric_Scrap_Linen` | any | most common (Z1 52%, Z5 30%); real crafting uses (lines, cloth) |
| Junk (vanilla) | `Plant_Flower_Water_*` (Blue / Green / Purple / Red / White / Duckweed) | Z1, Z3 (3 kinds) | ponds and ice holes |
| Junk (vanilla) | `Ingredient_Poop` | Z1, Z2, Z5 | the joke item, fertiliser use |
| Junk (vanilla) | `Rubble_Stone`, `Rock_Salt` | Z2-Z5 (rubble Z1 too) | rubble grows with depth (10% -> 30%) |
| Junk (vanilla) | `Deco_Coral_Shell` (+ `_Purple` / `_Sanddollar` / `_Swirly`), `Deco_Starfish` | Z2 oasis | decor |
| Junk (vanilla) | `Deco_Trash`, `Deco_Trash_Pile_Small`, `Deco_Trash_Pile_Large` | any (large Z3+) | generic junk, bigger deeper |
| Good treasure | Lost Property Envelope | any | opens to a coin purse (spec Good table) |
| Good treasure | Damp Parcel | any | zone materials (Z1-Z2 may include 1-3 `Ore_Gold`) |
| Good treasure | Unclaimed Parcel | any | an unidentified gear box, Normal or Unique |
| Good treasure | Bait Tin | any | bait / part scrap, or (5%) vanilla `Ingredient_Water_Essence` x1-3 |
| Great treasure | Locked Luggage Case | any | a bigger purse, or a Rare+ gear box, or Enchanted materials, or (5% each) vanilla Water Essence x4-8, a `Deco_Treasure*`, a `Weapon_Spear_Fishbone` |
| Great treasure | Clerk's Lucky Hook (drop-only part) | any | the spec's drop-only part |
| Outstanding treasure | Diplomatic Pouch (Do Not Open) | any | huge purse, a Legendary+ gear box, a fishing accessory (bound) or a pet egg later |
| Outstanding treasure | Sealed Envelope from the Director | Z3+ | same table, purely the name |

Treasure coins stay at about 5-7% of fishing income (spec; python 8.6 treasures per hour; purse shares unchanged by the vanilla contents).

## 8. Server Setup note (the species table is data)

The species table is **data, not code**: a JSON file in the mod's data folder (one row per species) with an edit page under SkyWynn Menu -> Server
Setup -> Fishing -> Species (the config kit `tools/skyycfg.py`; `tools/CONFIG-CONTRACT.md`). A server owner can change, add, remove or disable a species,
change its season / time lists, weights, rarity or price without a rebuild, and Reset to defaults restores this file's table. Rows:

`fish.species.<id>.{name,zone,water,seasons,times,rarity,minKg,maxKg,k,biteFactor,spawnWeight,dish,enabled}`, `fish.price.zoneBase.<zone>`
26 / 28 / 34 / 36 / 36, `fish.price.rarityMult` 1 / 1.5 / 2.5 / 6 / 12 / 25, `fish.season.inMult` 1.5, `fish.season.outMult` 0.5,
`fish.time.inMult` 1.5, `fish.time.outMult` 0.5, `fish.z3.winterBiteMult` 0.67 (seconds mult), `fish.fillet.bazaarRatio` 0.7,
`fish.junk.<id>.price` (vanilla item ids; weights `fish.junk.<zone>.<id>.weight`, spec 7.1), `fish.trophy.enabled` on. The Ledger reads this table, so a changed species shows in the book. Times in seconds.

## For the local session (UNVERIFIED)

| # | Item |
|---|---|
| 1 | Dynamic Seasons 6.1.2: season names, how many, and its API / event for the current season (spec UNVERIFIED 5). If it has more than four seasons or custom ones, map them to the four here |
| 2 | World-gen: which of our zone biomes really have water / lava, pond vs river vs oasis vs ice-hole placement, and biome ids; the table's "water" column is a design, not a map |
| 3 | The vanilla fish model / item / role ids to reuse as looks (vanilla fish tiers Common..Legendary, minnow, bluegill, trout, catfish, tropical, lobster; spec UNVERIFIED 6); species without a vanilla look need our own look or a recolour |
| 4 | Seaweed, rice and similar ids for the Sushi Roll (Food-Expansion item "seaweed?"); seaweed is no longer a junk catch (updated 2026-10-06: vanilla junk), so Sushi needs its own source. Proposed 2026-10-07 in `research/cloud/Food-Expansion-Draft.md` section 7: vanilla `Plant_Seaweed_*` (gathered) or Azure Kelp `Plant_Crop_Mana3` (farmed); ids to confirm |
| 5 | A python Monte Carlo of the whole rolled table (this file used the closed-form mean for the u^2 weight and ignored the +-5% length jitter) - re-measure income in a real session (Economy-Audit measure 1) |
| 6 | Per-stack metadata for weight / length on a fish item (spec UNVERIFIED 4) - the whole table depends on it |
| 7 | Whether lava can hold fish in the engine at all (spec stage 3); if not, Z4 species become "magma pool" water blocks |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is a fish's **rarity** (Normal / Unique / Rare / Legendary / Fabled / Mythic, a property of the species) the whole grade, replacing the spec's separate Common..Legendary roll? | [yes: one roll less, the pack's own rarity names] |
| 2 | Are 39 species enough to start (Z1 10, Z2 8, Z3 9, Z4 6, Z5 6; lava and cave ones come later), or should each zone get more? | [as is; more can be added in Server Setup] |
| 3 | Five Fabled / Mythic "unclaimed" fish (one per zone, hours of fishing to find one, average sale 150 up to 288,000 coins): fun, or too rare / too rich? | [as is] |
| 4 | Keep a Fabled / Mythic fish as a trophy (Ledger stamp, later a Trophy Case) instead of selling it? | [yes, sell or keep] |
| 5 | Zone prices: Z3 is 15% under and Z5 14% over the spec's income targets. Nudge Z3 base 34 -> 40 and Z5 36 -> 32 later? | [leave until measured] |
| 6 | Fillets by band (Raw / Fine / Prime) so rare fish give better food, or one fillet per zone (plain Meat, Food-Expansion question 8)? | [by band, since dish tier follows rarity] |
| 7 | Joke level in the names (Sleeper in Aisle 9, Final Notice Leviathan): keep, or plainer names for some? | [keep, sparing] |
