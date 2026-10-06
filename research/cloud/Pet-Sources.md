# Pet Sources (zone, starting rarity, drops and odds)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/cloud/pet-art/README.md` (section 3, the gaps this fills), `research/cloud/Pets-Spec.md` (sections 1 to 5, 7), `docs/answered/pets.md` (R6 to R9 and the 2026-10-06 notes), `research/cloud/Zone-Bosses-Ideas.md` (guardian drops), `research/cloud/Elites-Events-Spec.md` (elites, event chests), `research/cloud/Slayers-Spec.md` (section 5, the signature drop), `research/cloud/Dragon-Quest-Spec.md` (D1 to D7), `research/cloud/Capstone-Dungeon-Spec.md` (pet egg chance). Every number is a placeholder and a Server Setup row (times in seconds). Arithmetic checked in python3.

## 0. Decisions followed (LOCKED, not re-decided)

| Lock | Source | Used here |
|---|---|---|
| Pets = one system; slot 1 = pet slot (full buffs, never fights); slot 2 = SUMMON slot (mounts AND combat pets, buffs at 50%), unlocked by a ZONE 2 STABLE QUEST that also gives your first mount pet | `docs/answered/pets.md` R6, R7 | Horse source (section 3) |
| Rarity is raised with Upgrade Stones, **per skill / minion type**; eggs can be found at higher rarities; dragons have their own Dragon Upgrade Stones | R9 | Starting rarity vs bumped eggs (section 2); Legendary / Mythic by stone |
| Zone 5 = dinosaur caves Lv 60-75, dragon boss at 75; ONE dragon per profile for now | R8 | Dragon row |
| Dragon plan may adapt to Aures' Dragon Nestkeeper (default: our summon slot summons their dragon, else we only link it) | `docs/answered/pets.md` 2026-10-06 note | Dragon row marked UNVERIFIED |
| Pet XP = own skill XP + 50% of other XP (R6; Pets-Spec's older "20%" is superseded) | R6 | not changed here (note in section 8) |
| R3: coins never skip a collection unlock; NPC shops never sell unlocks or accessories; pets sold on the Auction House after Lv 1 (rows) | economy rules, Pets-Spec section 4 | No shop sells a pet or an egg (section 6) |
| Fortune and swing from pets are capped (`pets.fortune.cap` 10, `pets.swing.cap` 5); no Mythic gathering pet | `Gathering-Numbers-Reconciled.md` | Gathering pets never start above Legendary after stones |
| Pet art: the zone and "found at" rarity labels of the concept sheet were proposals only | `pet-art/README.md` section 3 | Confirmed or corrected below |

## 1. The shape of the system (proposal)

1. **Every pet has a home zone and a starting rarity** (the rarity of a fresh pet from its normal source). Stones raise it later.
2. **Three kinds of source:** *Bond* (tame the animal, the Stable NPC bonds it, Common and Uncommon pets only, once per kind, no RNG), *Quest* (fixed reward), *Egg* (zone eggs from chests, elites, events, guardians, slayers; hatched at the Stable on a timer).
3. **An egg belongs to a zone** and rolls a rarity from that zone's table, then a pet of that zone and rarity. About 6.5% of passive eggs hatch **one rarity step higher** (R9: "eggs at higher rarities"), never above Legendary, never for dragons.
4. Rare and Epic pets are **egg only** (no bond), so they need real play, not a shop.

## 2. Pet table: zone, starting rarity, sources, odds

"Eggs" odds are per zone egg. Hours = expected hours of normal play in that zone from the passive sources of section 4 (python3: 0.359 eggs per hour in Zone 1, less higher up). Add about 7% for the exact starting rarity (the bumped eggs). The art sheet's labels are kept except where marked **changed**.

| Pet | Home zone | Starting rarity | Sources (best first) | Odds | Expected hours |
|---|---|---|---|---|---|
| Rabbit | Z1 Emerald Wilds | Common | Starter shard chain (quest, fixed); Z1 eggs | 100%; 22.5% of Z1 eggs | 0.1 (about 6 minutes) |
| Chicken | Z1 | Common | Bond (tame + Stable); Z1 eggs | 100%; 22.5% | 0.3 to bond; 12.4 by egg |
| Turkey | Z1 | Uncommon | Bond; Z1 eggs | 100%; 27.5% | 0.3; 10.1 |
| Boar | Z1 | Uncommon | Bond; Z1 eggs | 100%; 27.5% | 0.3; 10.1 |
| Warthog | Z2 Howling Sands | Uncommon | Bond; Z2 eggs | 100%; 27.5% | 0.3; 12.6 |
| Horse | Z2 | Uncommon | **Stable quest** (first mount, R6); Z2 eggs | 100%; 27.5% | 0.5 after reaching Z2; 12.6 |
| Camel | Z2 | Rare | Z2 eggs only (no bond) | 25.0% of Z2 eggs | 13.9 |
| Hawk | Z2 (Archer pet) | Epic | Z2 eggs; Z4 eggs | 10.0%; 20.0% | 34.8; 34.8 (Z4) |
| Mouflon | Z2 (Priest pet) | Epic | Z2 eggs; Z4 eggs | 10.0%; 20.0% | 34.8; 34.8 (Z4) |
| Goat | Z3 Whisperfrost | Uncommon | Bond; Z3 eggs | 100%; 55.0% | 0.3; 8.4 |
| Bear | Z3 | Rare | Z3 eggs only | 16.5% | 28.1 |
| Wolf | Z3 | Rare | Z3 eggs only | 16.5% | 28.1 |
| Ram | Z3 (Warrior pet) | Epic | Z3 eggs; Z4 eggs | 12.0%; 20.0% | 38.6; 34.8 (Z4) |
| Skrill | Z4 Devastated Lands (Mage pet) | Epic | Z4 eggs only | 20.0% | 34.8 |
| Tusker | Z4 (Berserker pet) | Epic | Z4 eggs only | 20.0% | 34.8 |
| Dragon Hatchling | Z5 dinosaur caves | Mythic | Dragon quest line D1 to D7 (a borrowed egg after the Zone 5 fight) | 100%, one per profile | about 2 to 3 h of quests after Zone 5 (Dragon-Quest-Spec) |

Changes against the art sheet (section 3 of its README): **Warthog** stays Uncommon but is **bondable**; **Horse** is **Uncommon, quest-first** (the sheet put it in Z2 as Uncommon, same); **Hawk, Mouflon, Ram, Skrill, Tusker** keep Epic; Z4 gets the other Epic pets too so that Zone 4 is the best place to farm Epic eggs (five pets share 100% of its eggs, each 20%). No pet starts Legendary; Legendary is by Upgrade Stone (Q4).

Rarity tables per zone (python3 sums = 100%):

| Zone egg | Common | Uncommon | Rare | Epic | Pets in the pool |
|---|---|---|---|---|---|
| Z1 | 45% | 55% | - | - | Rabbit, Chicken / Turkey, Boar |
| Z2 | - | 55% | 25% | 20% | Warthog, Horse / Camel / Hawk, Mouflon |
| Z3 | - | 55% | 33% | 12% | Goat / Bear, Wolf / Ram |
| Z4 | - | - | - | 100% | Skrill, Tusker, Ram, Hawk, Mouflon |
| Z5 | no eggs; the Dragon is quest only | | | | |

Within a rarity every pet of the zone is equally likely (so Rare in Z3 is Bear 16.5% / Wolf 16.5%).

## 3. Quest and bond sources

| Source | What | Notes |
|---|---|---|
| **Starter** | Common Rabbit from the starter shard chain (Pets-Spec section 4) | every profile has the system from minute one |
| **Bond (Stable NPC)** | tame the vanilla animal by feeding it (vanilla taming, UNVERIFIED), the Stable bonds it as a pet at its starting rarity, once per kind per profile | Common and Uncommon pets only (Rabbit, Chicken, Turkey, Boar, Warthog, Goat); a row `pets.bond.enabled`; a small bond fee is allowed, it is not an unlock, so R3 holds (Q5) |
| **Zone 2 Stable quest** | gives the Summon slot and your first mount pet, the **Horse** | `docs/answered/pets.md` R6; Camel is the egg-only second mount |
| **Dragon quest line** | D1 "The Borrowed Egg" (Zone 5 story fight) to D7 "Hatching", ends in the Mythic hatchling | element chosen at D3; the Nestkeeper question may replace the pet with a linked dragon (UNVERIFIED) |

## 4. Egg sources and odds (the passive rate, python3)

All rows are per profile. "Egg chance" is the chance of a **zone egg**, before the per-zone multiplier (Z1 x1.0, Z2 x0.8, Z3 x0.6, Z4 x0.4: higher zones give fewer eggs, but richer tables).

| Source | Rule | Egg chance | Eggs per hour (Z1, python3) | Step up chance |
|---|---|---|---|---|
| Zone chests | 8 world chests opened per hour (placeholder `egg.chestsPerHour`) | 2% each | 0.160 | 5% |
| Elites (3% of spawns, Elites-Events-Spec 1.1) | 240 kills per hour (`egg.killsPerHour`); an elite drops an egg 1.5% | 0.03 x 0.015 per kill | 0.108 | 10% |
| World events | one event per 52.5 min (45 min + mean jitter 7.5), you take part in all; egg in the event chest 8% (Elites-Events-Spec Q3: small, Common / Uncommon only; here the zone table applies, Q6) | 8% | 0.091 | 5% |
| **Passive total** | chests + elites + events | | **0.359** | 6.5% overall |

Per zone: Z1 0.359, Z2 0.288, Z3 0.216, Z4 0.144 eggs per hour. These feed the "Expected hours" column: hours = 1 / (eggs per hour x chance of that pet per egg), e.g. Camel = 1 / (0.288 x 0.25) = 13.9 h.

Boss and slayer sources are **per kill or per day**, not per hour:

| Source | Odds | Expected |
|---|---|---|
| Zone guardian (Lv 20 / 30 / 45 / 60, `Zone-Bosses-Ideas.md`) | **first kill per profile always drops that zone's egg** (new, Q2); re-fights (one a day, reduced loot) drop one at 25% / 20% / 15% / 12% for Z1 to Z4; step up 20% | 4.0 / 5.0 / 6.7 / 8.3 re-fight days per extra egg |
| Slayer boss (Slayers-Spec 5: signature drop at 0.5 / 1 / 2 / 4 / 8% for tiers I to V, "a weapon variant or a pet egg of the zone") | half of the signature rolls are eggs: 0.25 / 0.5 / 1 / 2 / 4% per kill; the RNG meter (+1 at III, +3 at IV, +8 at V per kill, 100% = guaranteed) | python3: kills for an egg about 400 / 200 / 63 / 25 / 10 (tier I to V); step up 15% |
| Capstone dungeon floors F5+ (Capstone-Dungeon-Spec 5.2) | "a small chance, epic at F5+" | Zone 4 or 5 style Epic egg; not counted here |
| Fishing treasure (Fish catalog) | later, "a pet egg later" | not counted here |

A guardian first-kill egg is a free draw from the zone's table (so a Zone 3 first kill gives Goat 55%, Bear 16.5% ...), so most players already own a pet or two per zone before they farm.

## 5. Hatching and duplicates

- An egg is an item (bound until hatched); the Stable hatches it with a timer (`pets.hatch.seconds`, placeholder 600 s for Common, up to 3600 s for Epic) and shows the result with the rarity colour.
- A second copy of a pet you already have: **allowed** (a second Chicken, tradable after Lv 1 on the Auction House by the existing rows); a Pet Treat consolation is a cheap alternative (Q7). Pets are not dupable items (one id, one owner).
- Step-up eggs (6.5%) hatch the same pet one rarity higher: a Turkey from Uncommon to Rare. Gathering pets stop at Legendary (no Mythic, cap rows).

## 6. Exploit and balance check

| Risk | Handling |
|---|---|
| Buying pets or eggs with coins | no NPC sells them (R3); the Auction House allows pets (existing row), eggs are bound until hatched |
| Elite farming for eggs | per-zone elite cap (12 alive, Elites-Events-Spec), egg chance 1.5% and the zone multiplier; the table shows 0.108 eggs / h in Z1 and less higher |
| Alt profiles running events | events need real players; rewards capped per profile and day (12 chests) |
| Daily guardian farm | one reward attempt per real day per profile |
| Slayer coin sink | slayer cost climbs 400 to 3,000,000 coins per tier; slayer eggs are a bonus, not the main path |
| Legendary / Mythic skipping | none starts Legendary; Upgrade Stones are per skill and come from Void Fragments (R9) |
| Pet bonuses | one pet slot (plus the 50% summon slot); gathering caps hold the Fortune / swing |

## 7. Server Setup rows (SkyWynn Menu -> Server Setup -> Pets -> Sources; times in seconds)

`pets.source.<pet>` (bond / quest / egg flags per pet), `egg.chestChance` 2, `egg.chestsPerHour` 8 (info), `egg.elite.chance` 1.5, `egg.event.chance` 8, `egg.guardian.first` on, `egg.guardian.refight` 25 / 20 / 15 / 12, `egg.slayer.share` 50, `egg.zoneMult` 1 / 0.8 / 0.6 / 0.4, `egg.stepUp` 5 / 10 / 5 / 20 / 15 (chest / elite / event / guardian / slayer), per-zone rarity tables (section 2), per-zone pet weights, `pets.bond.enabled`, `pets.bond.fee`, `pets.hatch.seconds` per rarity (600 / 900 / 1800 / 3600), `pets.dupes` (allow / treat).

## 8. Notes for other drafts (not edited here)

- `Pets-Spec.md` still says "mount slot" (renamed SUMMON slot, R7) and "20% of other skills" (R6 locks 50%); its section 4 sources become this file.
- `Zone-Bosses-Ideas.md` guardian drops ("1 Common-Uncommon Pet Egg", "20% Rare Pet Egg", "Epic chance", "Epic-Legendary") are replaced by the table in section 4 (egg rarity comes from the zone table, not the guardian).
- `Elites-Events-Spec.md` Q3 (a small Common egg chance only) differs from the zone-table egg here; elites gain a 1.5% egg chance.

## For the local session (UNVERIFIED)

1. How vanilla taming works (how many feeds, how a tamed state is stored) and which of the animals (Chicken, Turkey, Boar, Warthog, Goat, Rabbit) can be tamed at all; whether the Stable can read "tamed by player X".
2. Model / role ids for every pet and which are friendly; whether Wolf or Camel are tameable (we do not bond them).
3. The real rates: chests per hour, kills per hour (class XP is about 5,400 per hour in Zone 1, Elites-Events-Spec), events per hour, to replace the 8 / 240 / 52.5 min placeholders; the table is linear in those rows.
4. Whether eggs can be items that carry a zone and rolled rarity as item data (an egg item with metadata), and a hatch timer in the Stable.
5. Whether Aures' Dragon Nestkeeper can be used for the dragon row; the Zone 5 boss and egg flow.
6. Slayer signature drop details (Slayers-Spec: whether the egg is a separate roll).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Zone and starting rarity per pet as in section 2 (the art sheet's labels with Warthog bondable, Hawk / Mouflon / Ram also in Zone 4 eggs)? | [yes] |
| 2 | Always give one zone egg on the first kill of each guardian (a free draw), then 25 / 20 / 15 / 12% on daily re-fights? | [yes] |
| 3 | About 35 hours of passive play per Epic pet and 8 to 14 hours per Rare / Uncommon egg pet: too slow or too fast? (all linear in the egg rows) | [keep, tune live] |
| 4 | No pet starts Legendary; Legendary and Mythic only by Upgrade Stones (and the dragon)? | [yes] |
| 5 | Bonding at the Stable: free, or a small coin fee (a sink, not an unlock)? | [free] |
| 6 | World event eggs: use the zone table (as here), or Common / Uncommon only as Elites-Events-Spec suggests? | [zone table] |
| 7 | A duplicate hatch: a second pet you can trade, or a Pet Treat instead? | [second pet, tradable] |
