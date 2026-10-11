# Pet eggs v2 (zone eggs by type, species eggs, fusing) - design for SkyyPets 0.3

Cloud draft, 2026-10-10. Paper design; nothing built. Replaces the "one egg per zone" shape of `research/cloud/Pet-Sources.md`
(sections 1-5) for SkyyPets 0.3. Keeps the core rules of `research/cloud/Pet-Core-Spec.md` (pets are records, eggs are items). Roster:
`research/Pets-Roster.md`. Zones: `research/cloud/Zone-Archipelago-Spec.md` section 5. Every number is a placeholder and a Server Setup
row (times in seconds). Arithmetic checked in python3 (method in each section).

## 0. Decisions this follows (LOCKED - not re-decided)

The two egg locks, word for word (`docs/answered/pets.md` lines 41 and 42; newest wins):

> - LOCKED 2026-10-10 (Skyy asked: "are gets spacific pets? or are they types, with raritys? like, do i get a rabbit egg? or a farming egg, that gives me a random farming pet, lower chance for better pets? and how do we do rarity? upgrades like skyblock? or fusing? like merge 4 of the same together to make one of the next rarity?"). EGG TYPES popup answer: "zone + species eggs. BUT zone still come in types. so youll get a Zone 1 mining egg. a zone 1 combat edd, a zone 1 farming egg, a zone 1 mount egg and so on." -> zone eggs are split by TYPE (Zone N Mining / Combat / Farming / Foraging / Mount ... egg = a random pet of that zone + type, better pets rarer) + species eggs (a creature drops its own egg, 0.1% / elites 1%). Changes research/cloud/Pet-Sources.md (one egg per zone) for SkyyPets 0.3.
> - LOCKED 2026-10-10 (Skyy, same question) RARITY popup answer "Stones + fusing (Recommended)": keep the per-skill Upgrade Stones (R9) AND add FUSING: merge 4 of the same pet at the same rarity into 1 of the next rarity (keeps the highest level).

(Lines 43-46 of the same file are newer, but they are about pet roles and the summon slot. They are also followed here: section 1.2 uses
the role flags, and section 7 uses the Skeleton split.)

| Lock | Source | Used in |
|---|---|---|
| Eggs are items: tradeable, sellable on Bazaar / Auction House, sold by merchants. A HATCHED pet is a record bound to the profile (never an item, never traded) | `docs/answered/pets.md` 39 | 6 |
| Creatures drop their own egg 0.1% / elites 1%; no boss pets | `docs/answered/pets.md` 34 | 3 |
| Upgrade Stones per skill / minion type; dragons have their own Dragon Upgrade Stones; eggs can be found at higher rarities | `docs/answered/pets.md` 21 (R9) | 2.3, 5 |
| ONE dragon per profile | `docs/answered/pets.md` 19 (R8) | 4.4, 5 |
| Pet roles: gathering / combat (stat-only) / FIGHTER / MOUNT; only Mount / Fighter kinds go in the summon slot | `docs/answered/pets.md` 43, 45 | 1.2 |
| Pets per profile, they do not transfer | `docs/answered/pets.md` 38 | 4, 6 |
| Roaming merchants: launch stock "Special weapons (Recommended),Mounts,Pet eggs later" (a pet-egg slot filled when pets ship) | `docs/answered/economy.md` 92 | 3.2, 6 |
| Zone 2 Stable quest gives the summon slot + your first mount (Horse) | `docs/answered/pets.md` 12, 17 | 1.3 |

**Superseded by these locks** (notes for the main session, not edited here): `research/cloud/Pet-Sources.md` section 5 "an egg is an
item (bound until hatched)" and section 6 "no NPC sells them" (eggs now trade and merchants sell them); its "second pet, tradable" duplicate
answer (pets are bound now, so duplicates are fusing fodder); `research/cloud/Pet-Core-Spec.md` section 8 phase 6 "Auction House escrow
trading" of pets (pets never trade now; only eggs do).

## 1. Egg kinds and item ids

### 1.1 Two kinds of egg

| Egg | What hatches | Item id (repo style `Skyy_<Thing>_<Variant>`) | Count |
|---|---|---|---|
| **Zone type egg** | a random pet of that zone + type; rarer pets are less likely (section 2) | `Skyy_PetEgg_Z<N>_<Type>`, e.g. `Skyy_PetEgg_Z1_Mining`, `Skyy_PetEgg_Z2_Mount` | up to 5 zones x 7 types = 35; only pools with at least 1 pet ship |
| **Species egg** | that one pet, at its start rarity (plus the small step-up chance) | `Skyy_PetEgg_<Kind>`, e.g. `Skyy_PetEgg_Fox`, `Skyy_PetEgg_VoidEye` (kind ids from `SkyyPets/build_skyypets_0.2.2.py` lines 185-219) | one per kind that has a live creature (not Cat / Dog / Corgi: no vanilla role spawns them, `research/Pets-Roster.md` rows 1-4) |

**Eggs carry NO metadata.** A metadata ItemStack crashes the client in an `ItemGridSlot` (`research/cloud/Pet-Core-Spec.md` section 1;
`HANDOFF.md` section 2). So one plain id per egg, the rarity is rolled when the egg goes into the Stable (section 4), and eggs stack.
Because they are plain ids, the Bazaar (trades by item id) and the Auction House can list them.

The dragon egg is not one of these: it stays the bound quest item of `research/cloud/Dragon-Quest-Spec.md` D1 (one per profile).

### 1.2 Types (one rule decides every pet's type)

| Type | Which kinds | Egg id part |
|---|---|---|
| Mount | every kind whose role flags include `mount` (also Mount + Fighter, e.g. Ram) | `Mount` |
| Mining / Foraging / Farming | the kind's skill (all gathering pets are role `gathering`) | `Mining`, `Foraging`, `Farming` |
| Fishing | fish / sea kinds (`research/Pets-Roster.md` rows marked Zone "Fishing") - needs a Fishing pet skill first (section 9) | `Fishing` |
| Combat | the kind's skill is Combat (stat-only combat pets AND Fighters - Fighters are just the rarer, stronger end) | `Combat` |
| Explorer | the kind's skill is Exploration and it is not a mount (today Rat, Gecko) | `Explorer` (Q2) |

Rule order: `mount` flag first, else the skill. The type is derived from data the kinds table already has (`SkyyPets/build_skyypets_0.2.2.py`
lines 185-219 skills, 278-292 role flags; Server Setup > Pets > Pet kinds / Pet roles), so every new roster batch fills the pools with no
extra table. An owner can force a type with a row `pets.<kind>.eggType` (blank = the rule).

### 1.3 Launch pools today (the 30 kinds of `SkyyPets/build_skyypets_0.2.2.py` lines 185-219, home zone = the last column there)

C / U / R / E = start rarity Common / Uncommon / Rare / Epic.

| Zone | Mining | Foraging | Farming | Combat | Mount | Explorer |
|---|---|---|---|---|---|---|
| Z1 Emerald Wilds | Mouse C | Cat C, Squirrel C, Turkey U | Rabbit C, Chicken C, Corgi C, Frog C, Bunny C | Dog C, Boar U, Fox U, Skeleton R | - | Rat C |
| Z2 Howling Sands | Meerkat C, Warthog U | - | - | Tusker R, Hawk E, Mouflon E | Horse U, Camel R | Gecko C |
| Z3 Whisperfrost | Goat U | Bear R | - | Wolf R | Ram E | - |
| Z4 Devastated Lands | - | - | - | VoidLarva U, VoidCrawler R, Skrill E, VoidEye E | - | - |
| Z5 Dinosaur Caves | - | - | - | - | - | - |

Many pools are empty or hold one pet. Proposal (Q3): SkyyPets 0.3 ships with a **first roster batch** (data only, rows) so every Z1-Z4
Mining / Foraging / Farming / Combat pool has at least 3 pets and every zone has a Mount pool from Z2 on. Candidates from
`research/Pets-Roster.md` section 1.2 (zone and start rarity from its table, type is a proposal, zones UNVERIFIED there):

| Pool | Add (start rarity) |
|---|---|
| Z1 Mining | Bat U, Spider U |
| Z1 Combat | Zombie U, Snake U, Spirit R, Werewolf E |
| Z1 Farming / Foraging | Cow C, Pig C, Sheep C / Owl U, Small birds C, Deer U |
| Z2 Mining / Foraging / Farming | Molerat U, Armadillo U, Sand Lizard U / Antelope U, Vulture R / Flamingo U, Cactee U |
| Z2 Combat | Hyena U, Scorpion R, Scarak Fighter R, Sand Skeleton R |
| Z3 Mining / Foraging / Farming | Crystal Golem E / Moose R, Snow Leopard R / Snail C, Penguin U |
| Z3 Combat | Frost Skeleton R, Sabertooth E, Yeti E |
| Z4 Mining / Foraging / Farming | Living Spark R, Magma Slug R / Raven U, Wraith Lantern R / Undead farm animals U |
| Z4 Combat / Mount | Ghoul R, Bleached Hound R, Burnt Skeleton R, Emberwulf E, Void Spawn E / Skeleton Horse E |
| Z5 (when Zone 5 opens) | Combat: Cave Raptor E, Cave Rex E; Foraging: Archaeopteryx R, Tetrabird R; Mining: Trilobite U; Mount: Trillodon R |
| Fishing (all zones, when a Fishing skill exists) | Z1 Small fish C, Crab U; Z2 Pufferfish U, Lobster U, Piranha U; Z3 Jellyfish U, Moray Eel R, Hammerhead E, Humpback Whale E; Z4 Lava Shellfish R, Snapjaw E, Pirate Skeleton E |

A pool with 0 pets has no item. Its sources roll nothing (no fallback egg), so an empty pool never hands out a "dead" egg.

**Z1 Mount egg (Skyy named it):** no Z1 kind is a mount today (the first mount is the Zone 2 Stable Horse, lines 12 / 17). Proposal: the
Z1 Mount egg exists once a Z1 mount kind exists (Bison or Deer Stag, roster "candidate" mounts, need our own mount role in phase 5). Until
then a Z1 player can still hatch it, and the pet sits in the pet slot until the Stable quest opens the summon slot (Q4).

## 2. Rarity odds (zone type eggs)

### 2.1 How a zone type egg rolls

1. **Tier roll** from the zone's weights (table 2.2), using only the tiers that have at least one pet in that pool (the weights of
   the tiers that are left are scaled back up to 100%).
2. **Pet roll:** every pet in that tier of the pool is equally likely (row `pets.<kind>.eggWeight`, default 1, for hand-tuning).
3. **Step-up** ("eggs can be found at higher rarities", R9): with the source's step-up chance the pet hatches one rarity higher than its
   start rarity. Never above Legendary, never Mythic.

Nobody can hatch a Legendary pet straight from an egg except through the step-up (Pet-Sources Q4 default).

### 2.2 Zone weights (rows `egg.zone<N>.weights`)

| Zone egg | Common | Uncommon | Rare | Epic |
|---|---|---|---|---|
| Z1 | 55 | 30 | 12 | 3 |
| Z2 | 35 | 35 | 22 | 8 |
| Z3 | 20 | 35 | 30 | 15 |
| Z4 | 10 | 30 | 35 | 25 |
| Z5 | 0 | 25 | 40 | 35 |

Higher zones give fewer eggs (section 3) but better ones. Z1 Epic at 3% gives Zone 1 players a real "lucky egg" moment (Werewolf, if Q3).

### 2.3 Expected rarity per 100 eggs (python3)

Method: for each pool, P(tier) = weight / sum of weights of the tiers present; then a step-up moves that share one tier up with chance
s. s = 6.5% is the old Pet-Sources average (chest 5, elite 10, event 5, guardian 20, slayer 15); s = 0 shows the raw table.

Full pool (all four tiers present):

| Zone | s = 0: C / U / R / E | s = 6.5%: C / U / R / E / L |
|---|---|---|
| Z1 | 55.0 / 30.0 / 12.0 / 3.0 | 51.4 / 31.6 / 13.2 / 3.6 / 0.2 |
| Z2 | 35.0 / 35.0 / 22.0 / 8.0 | 32.7 / 35.0 / 22.8 / 8.9 / 0.5 |
| Z3 | 20.0 / 35.0 / 30.0 / 15.0 | 18.7 / 34.0 / 30.3 / 16.0 / 1.0 |
| Z4 | 10.0 / 30.0 / 35.0 / 25.0 | 9.4 / 28.7 / 34.7 / 25.7 / 1.6 |
| Z5 | 0 / 25.0 / 40.0 / 35.0 | 0 / 23.4 / 39.0 / 35.3 / 2.3 |

Launch pools (table 1.3, no roster batch), per 100 eggs, s = 6.5%, and each pet's share at s = 0:

| Pool | C / U / R / E / L per 100 | Each pet |
|---|---|---|
| Z1 Combat | 53.0 / 32.6 / 13.6 / 0.8 / 0 | Dog 56.7%, Boar 15.5%, Fox 15.5%, Skeleton 12.4% |
| Z1 Foraging | 60.5 / 37.2 / 2.3 / 0 / 0 | Cat 32.4%, Squirrel 32.4%, Turkey 35.3% |
| Z1 Farming | 93.5 / 6.5 / 0 / 0 / 0 | 5 Commons, 20% each |
| Z1 Mining / Explorer | 93.5 / 6.5 / 0 / 0 / 0 | Mouse / Rat 100% |
| Z2 Mining | 46.8 / 50.0 / 3.2 / 0 / 0 | Meerkat 50%, Warthog 50% |
| Z2 Combat | 0 / 0 / 68.6 / 29.7 / 1.7 | Tusker 73.3%, Hawk 13.3%, Mouflon 13.3% |
| Z2 Mount | 0 / 57.4 / 40.1 / 2.5 / 0 | Horse 61.4%, Camel 38.6% |
| Z3 Mining / Foraging / Combat / Mount | one pet each (Goat / Bear / Wolf / Ram): 93.5% at its start rarity, 6.5% one higher | 100% |
| Z4 Combat | 0 / 31.2 / 38.5 / 28.5 / 1.8 | VoidLarva 33.3%, VoidCrawler 38.9%, Skrill 13.9%, VoidEye 13.9% |

What this shows: one-pet pools are just species eggs with a different name, which is why Q3 adds the roster batch before 0.3.

## 3. Sources: who drops which egg

### 3.1 Table

Egg chance = per event; zone multiplier on top (Z1 x1.0, Z2 x0.8, Z3 x0.6, Z4 x0.4, Z5 x0.3, row `egg.zoneMult`). The zone is where
the player stands (the zone lookup SkyyMobs already uses; Zone 5 by depth under 4D, `research/cloud/Zone-Archipelago-Spec.md` 6.4).
Rates in eggs per hour are for Zone 1, from placeholder activity numbers (UNVERIFIED, section 9): eggs/h = events per hour x chance.

| Source | Egg | Chance (row) | Step-up | Z1 eggs / h (python3) |
|---|---|---|---|---|
| Natural ore broken (Mining XP award) | Z<N> Mining | 1 in 4,000 awards (`egg.gather.mining`) | 5% | 1,200 awards/h -> 0.30 |
| Natural log broken (Foraging XP award) | Z<N> Foraging | 1 in 4,000 (`egg.gather.foraging`) | 5% | 0.30 |
| Fully grown crop harvested (Farming XP award) | Z<N> Farming | 1 in 4,000 (`egg.gather.farming`) | 5% | 0.30 |
| Fish caught (SkyyFishing) | Z<N> Fishing | 1 in 150 catches (`egg.fish.catch`) + Lost Property treasure (Fish catalog "a pet egg later") | 10% | 40 catches/h -> 0.27 |
| Mob kill (hostile / neutral, not tamed, not a pet) | Z<N> Combat | 1 in 2,500 kills (`egg.kill.chance`) | 5% | 240 kills/h -> 0.096 |
| Elite kill | Z<N> Combat (85%) or Z<N> Mount (15%) | 1.5% (`egg.elite.chance`) | 10% | 240 x 3% x 1.5% -> 0.108 |
| Zone chest | any type of that zone (weights below) | 2% (`egg.chestChance`) | 5% | 8 chests/h -> 0.16 |
| World event chest | any type, Mount weighted up | 8% (`egg.event.chance`) | 5% | -> 0.091 |
| Zone guardian | first kill per profile: one egg of a type YOU pick (a choice page); daily re-fight 25 / 20 / 15 / 12% (Pet-Sources 4) | 20% | per kill |
| Slayer boss | Combat egg, Pet-Sources 4 rates (0.25-4% per kill + RNG meter) | 15% | per kill |
| Roaming merchant | sells zone type eggs (Pet eggs tab) + Mount eggs (Mounts tab), section 3.2 | 0% | bought |
| Creature kill (species egg) | `Skyy_PetEgg_<Kind>` of THAT creature | 0.1% normal, 1% elite (LOCKED) | 5% / 10% | section 3.3 |

Chest / event type weights (row `egg.chest.types`): Combat 30, Mining 15, Foraging 15, Farming 15, Fishing 10, Mount 10, Explorer 5;
empty pools are skipped and the rest scaled back to 100%. Events: Mount x2.

**Gathering rolls ride the existing pet XP hook.** SkyySkills 0.4.29 already calls `pets:fn:onxp` after EVERY award with
`{ UUID, skill, Long xp, "SkyySkills" }` (`SkyySkills/build_skyyskills_0.4.29.py` lines 5-9, 9061-9098), and placed blocks give no
award (`PlacedStore`, same file line 565 / 783 `skill:fn:placed`). So SkyyPets rolls one Mining / Foraging / Farming egg chance per
award (not per XP point) with no new hook. Two gaps for the local session: the offline smelting write also passes through the hook (line 7
"SmeltTask's offline write") - roll only when the player is online and in a zone world, or better SkyySkills adds a 5th element (`block`
/ `crop` / `smelt` / `kill` / `other`) and only `block` / `crop` roll; and a crop award is "StageFinal only" for sickles (line 140) but
UNVERIFIED for hand harvest.

Anti-farm caps (rows): at most `egg.capPerHour` 3 type eggs per profile per real hour from gathering + kills together (chests, events,
guardians, slayers, merchants not counted); species eggs `egg.species.capPerHour` 2. A capped roll says nothing. Tamed_* roles, babies,
our own `Skyy_Pet_*` roles and other mods' summons never roll.

### 3.2 Roaming merchants (the pet-egg slot)

SkyyMerchants 0.1.1 already has the empty slot: `PETS = []` "filled when pets ship" (`SkyyMerchants/build_skyymerchants_0.1.1.py` line
158), the Server Setup table `merchant.pets` = `pet.<item id>=Zones/Price/Stock` (lines 985-986, 1013), the Mounts table `mount.<id>`
(line 984) and the "Pet eggs" tab (lines 1689, 2350, 2480). SkyyPets 0.3 needs no merchant code, only rows:

| Row | Zones | Price (coins) | Stock per visit |
|---|---|---|---|
| `pet.Skyy_PetEgg_Z1_<Type>` | 1 | 5,000 | 1 |
| `pet.Skyy_PetEgg_Z2_<Type>` | 2 | 15,000 | 1 |
| `pet.Skyy_PetEgg_Z3_<Type>` | 3 | 40,000 | 1 |
| `pet.Skyy_PetEgg_Z4_<Type>` | 4 | 100,000 | 1 |
| `mount.Skyy_PetEgg_Z<N>_Mount` | N | 2x the zone price | 1 |

Merchants never sell species eggs (hunting the creature stays the way to get "that" pet - Q6). The SkyyMerchants restock already picks
"every mount / pet egg of its zone" (line 45), so with 6 types that is 6 egg rows per visit; a row `merchant.pets.perVisit` (2) would limit
it (small SkyyMerchants change, Q6).

**Price floor:** a merchant price must stay above what the Bazaar pays for the same egg (instant sell = base x (1 - 10% spread),
`SkyyBazaar/build_skyybazaar_0.1.7.py` lines 261 / 331), or buy-from-merchant / sell-to-Bazaar is free coins. Rule: merchant price >= 3x
the Bazaar base (checked at build time and in the Server Setup row check).

### 3.3 Species eggs (0.1% / 1%, LOCKED)

- Which creature: the vanilla role killed maps to its roster family (`research/Pets-Roster.md` "Vanilla roles" column: any `Skeleton_*`
  role -> the Skeleton family; after SkyyPets 0.2.3 split the archer roles -> the archer Skeleton, Knight / Soldier -> the melee one).
- Fish families: catching a fish of a pet family (Bluegill, Jellyfish ...) rolls 0.1% for that species egg (proposal; fish are caught,
  not killed).
- How long (python3, P(at least one) = 1 - (1 - p)^n): normal kills: mean 1,000, 50% after 693, 90% after 2,302; elites: mean 100,
  50% after 69, 90% after 230. At 240 kills / h of ONE creature that is about 4 hours on average - a real hunt, as Skyy wanted.
- Elites do not exist yet (SkyyMobs has no elite stage, `SkyyMobs/build_skyymobs_0.1.5.py` line 398 "NOT IN 0.1 ... elites"); the 1%
  waits for them.

## 4. Hatching (the Stable)

The Stable page and the `hatch.<n>` key are in `research/cloud/Pet-Core-Spec.md` 1 and 5. Changes for v2:

| Step | Rule |
|---|---|
| Put an egg in | the egg is removed from the inventory FIRST (`removeItemStackFromSlot` succeeded), then the roll happens (zone type: tier + pet + step-up; species: step-up only) and is saved at once: `hatch.<n>=<item id>|<start ms>|<end ms>|<kind>|<rarity>`. Rolling at put-in means a relog, a crash or a profile switch can never re-roll |
| Timer | by zone, not by rarity (a rarity timer would give the result away): Z1 600 s, Z2 900, Z3 1,800, Z4 2,700, Z5 3,600; species eggs by start rarity 600 / 900 / 1,800 / 2,700 (`pets.hatch.seconds.*`) |
| Hatch slots | 2 at a time per profile (`pets.hatch.slots`) |
| Claim | creates the pet record AND removes the `hatch.<n>` line in ONE file save (tmp + fsync + atomic rename, the 0.1 save path). A crash leaves either the egg line (claim again) or the pet (done), never both, never neither |
| Full collection | `pets.owned.max` reached: the claim waits (the egg stays hatched in the Stable, nothing is lost) |
| Dragon cap | a `Dragon_*` kind never comes from these eggs |
| Busy | refused while `profile:busy` (profile switch in progress) |

## 5. Fusing (4 of the same pet + same rarity -> 1 of the next rarity)

### 5.1 Rules

| Rule | Default |
|---|---|
| Input | 4 pets of the same KIND and the same RARITY in the same profile (skins and names may differ) |
| Output | 1 pet of that kind, rarity + 1 |
| Which one survives | the **base** = the highest level of the four (tie: more XP into the level, then the oldest `got`). It keeps its id, level, XP, skin, name, bond, favourite flag and slot. The other 3 (the **fodder**) are gone |
| Steps | Common -> Uncommon -> Rare -> Epic -> Legendary. Legendary never fuses (Q8) |
| Mythic | never by fusing. Mythic is the dragon tier only (`research/cloud/Pets-Spec.md` 2) |
| Dragons | never fuse (one per profile, R8 - there can never be 4); Dragon Upgrade Stones are their only path |
| Gathering pets | stop at Legendary like everything else (Fortune / swing caps hold, `research/cloud/Pets-Spec.md` 1) |
| Fodder may not be | in a slot, a favourite (`lock`), hatching, or the starter pet while it is your only pet. The base may be slotted (its creature changes look next second) |
| Cost | no coins (Q9: a small fee as a coin sink is one row `pets.fuse.fee` per step) |
| Album / skins | unchanged; skins the fodder unlocked stay unlocked (the `skins` list never shrinks) |
| Where | Pets page > Details > **Fuse** (picks the 3 lowest-level fodder automatically, shows all 4 and the result, confirm twice); Stable page lists "fusable sets". No chat command for players; admin `/petadmin fuse <player> <id>` for support |

How many pets per step up (python3, 4^n): +1 step = 4 pets, +2 = 16, +3 = 64, Common -> Legendary = 256 Commons. Fusing is meant for
the DUPLICATES that type eggs give, not as the main road to Legendary - that is the stones (5.3).

### 5.2 Dupe and loss safety (all four pets live in ONE profile file)

Pets of one profile are one file (`<world>/mods/Skyy_SkyyPets/pets/<pkey>.properties`, `SkyyPets/build_skyypets_0.2.2.py` lines 93-96),
and every save is tmp + fsync + atomic rename. So "consume the 3, then upgrade the base" is written as ONE save - the rename is the single
commit point.

| Step | What | If it fails / crashes here |
|---|---|---|
| 1 | Under the profile record's lock, re-check everything at the moment of Confirm (4 distinct ids still there, same kind + rarity, below the cap, fodder rules, file readable, not `profile:busy`, kind enabled) | refused, nothing changed |
| 2 | Ledger line `fuse-intent <fuseId> base=<id> fodder=<a,b,c> <rarity> -> <rarity+1>` (`fuseId` = 8 random characters) | nothing changed yet |
| 3 | In memory: remove the 3 fodder records (consume), set base `rarity+1` (create the result), `seq + 1`, then save | save fails: the in-memory copy is put back from a snapshot, ledger `fuse-abort`, "nothing was changed" |
| 4 | Save OK: remove the 3 ids from the global id index; ledger `fuse-take` x3 + `fuse-up` + `fuse-done <fuseId>` | - |
| Crash between 2 and the rename | file unchanged: all 4 pets still there | startup finds `fuse-intent` with no `fuse-done`, sees the fodder still in the file, writes `fuse-abort (crash)` |
| Crash after the rename, before 4 | file has the fused pet, fodder gone | startup sees fodder gone + base at the new rarity, writes `fuse-done (recovered)` |

The file is always the truth; the ledger explains it. No state ever has "4 pets AND the upgraded one" (dupe) or "fodder gone, base not
upgraded" (loss). Extra guards:

- **Admin restore cannot re-create fodder by accident:** `/petadmin restore` (0.1, `SkyyPets/build_skyypets_0.1.py` lines 1752-1754)
  rebuilds "a pet nobody owns from its newest ledger line" - a fused-away pet IS nobody's. 0.3 refuses ids whose newest line is
  `fuse-take` unless the admin adds `force` (and the ledger notes it).
- **Double click / two pages:** the button greys out after one click; a second Confirm fails step 1 (fodder gone).
- **XP flush, slot change, hatch claim** use the same record lock, so they cannot interleave with a fuse.
- The startup duplicate check (an id in two files, 0.1 item 2) is unchanged.

### 5.3 Fusing next to the per-skill Upgrade Stones

| | Upgrade Stone (R9) | Fusing (new) |
|---|---|---|
| What it costs | one stone of the pet's type (Mining, Foraging, Farming, Fishing, Combat, Mount, Explorer; Dragon stones for dragons) | 3 copies of the same pet at the same rarity |
| Item ids | `Skyy_PetStone_<Type>`, e.g. `Skyy_PetStone_Mining`, `Skyy_PetStone_Dragon` (tradeable items like eggs, Q10) | - |
| Best for | the one pet you love, without luck | duplicates from type eggs; a free use for them |
| Step | +1 rarity | +1 rarity |
| Cap | Legendary (Mythic = dragons with Dragon stones) | Legendary; never dragons |
| Level | kept | the highest of the four kept |

They stack freely: a stoned Rare Fox can be fused with three other Rare Foxes. Balance aim: one stone should cost about what 3
same-rarity duplicates are worth on the Bazaar, so neither road is a trap. Stone type = egg type (one mapping table, section 1.2) - that
is how "per skill / minion type" reads for pets (Q10). Stone recipes (Void Fragments, `research/cloud/Pets-Spec.md` 2) are a later round.

## 6. Trading

| Thing | Bazaar | Auction House | Merchant | Notes |
|---|---|---|---|---|
| Zone type eggs | yes (commodities, plain ids) | yes | sells them (3.2) | Bazaar base price row per egg: Z1 1,000 / Z2 3,000 / Z3 8,000 / Z4 20,000 / Z5 40,000, Mount x2 (placeholders, merchant price >= 3x) |
| Species eggs | no (Q7) | yes | no | ~100 ids would flood the Bazaar list |
| Upgrade Stones | yes | yes | no | later round |
| Hatched pets | never | never | never | bound records (LOCKED line 39) |
| Dragon egg | never | never | never | bound quest item |

**Bazaar note:** SkyyBazaar is a market maker with endless stock (`SkyyBazaar/build_skyybazaar_0.1.7.py` lines 1-2, 261-266), so a
listed egg can be BOUGHT for coins at any time, its price rising with demand. That is a coin sink, but it also means coins buy eggs
without limit. Options (Q7): list zone eggs normally [default, price impact keeps it costly]; or a Bazaar "sell-only" flag for eggs
(SkyyBazaar change); or Auction House only.

Eggs are ordinary items, so the item-level rules apply: the `profile:busy` window (`tools/PROFILES-CONTRACT.md` 5) and the hatch
consume-first rule (section 4). No egg carries data that can be forged.

## 7. Server Setup rows (SkyWynn Menu -> Server Setup -> Pets -> Eggs; `tools/CONFIG-CONTRACT.md`; times in seconds)

`egg.zone<N>.weights` (C/U/R/E, table 2.2), `egg.zoneMult` 1 / 0.8 / 0.6 / 0.4 / 0.3, `egg.gather.mining|foraging|farming` 4000 (1 in N),
`egg.fish.catch` 150, `egg.kill.chance` 2500, `egg.elite.chance` 1.5, `egg.elite.mountShare` 15, `egg.chestChance` 2, `egg.event.chance` 8,
`egg.chest.types` (weights), `egg.species.normal` 0.1, `egg.species.elite` 1, `egg.stepUp.*` (gather 5, fish 10, kill 5, elite 10,
chest 5, event 5, guardian 20, slayer 15, species 5 / 10), `egg.capPerHour` 3, `egg.species.capPerHour` 2, `pets.hatch.seconds.z1..z5`
600 / 900 / 1800 / 2700 / 3600, `pets.hatch.seconds.species.*`, `pets.hatch.slots` 2, `pets.fuse.enabled` true, `pets.fuse.fee.*` 0,
`pets.fuse.maxRarity` Legendary, per kind `pets.<kind>.eggType` / `.eggWeight` / `.speciesEgg` (on), merchant rows in SkyyMerchants
(3.2), Bazaar rows in SkyyBazaar (6).

New ledger reasons: `hatch-in`, `hatch-claim`, `fuse-intent`, `fuse-take`, `fuse-up`, `fuse-done`, `fuse-abort`, `egg-drop` (optional
audit, off by default: `pets.ledger.eggDrops`).

## 8. What SkyyPets 0.1 / 0.2 already do (read-only check)

| Already there | Where |
|---|---|
| Records per profile, `src` / `got` keys, global id index, 8-char ids | `SkyyPets/build_skyypets_0.1.py` lines 18-19, 1201 (`newId`); 0.2.2 line 1953 |
| One-write create (`create`: index, record, save, roll back on a failed save, ledger line) - the model for hatch-claim and fuse | 0.1 lines 1644-1658; 0.2.2 line 3422 |
| Append-only ledger + `ledgerFind` + startup duplicate check / quarantine | 0.1 lines 24-28, 1211-1259; 0.2.2 line 1992 |
| Admin restore (needs the `fuse-take` guard, 5.2) | 0.1 lines 1752-1754 |
| Role flags (decide the Mount type) | 0.2.2 lines 273-304 |
| Kind table with skill + zone (decide type + zone pool) | 0.2.2 lines 179-219 |
| Rarity 1-5, 6 = Mythic for dragons; give refuses Mythic | 0.1 lines 18, 1722 |
| "Pets come from eggs, the Stable and quests" text, "Eggs ... come in later versions" | 0.2.2 lines 3817, 4141 |
| NOT there: egg items, the Stable page, hatching, drops, fusing, stones | grep of all four build scripts |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Zone type egg odds as in table 2.2 (Z1 55 / 30 / 12 / 3 Common / Uncommon / Rare / Epic, getting better each zone)? | [yes] |
| 2 | Exploration pets that are not mounts (Rat, Gecko): their own "Explorer" egg, or put them in the Farming egg? | [own Explorer egg] |
| 3 | Ship SkyyPets 0.3 together with a first roster batch (table 1.3) so each zone egg has at least 3 pets? | [yes] |
| 4 | Zone 1 Mount egg: only once a Zone 1 mount pet exists (Bison / Deer Stag), and its pet waits in the pet slot until the Stable quest? | [yes] |
| 5 | Gathering eggs: 1 in 4,000 natural ores / logs / grown crops, and max 3 type eggs per hour from gathering + kills? | [yes, tune live] |
| 6 | Merchants sell zone type eggs (1 of each, about 5,000 coins in Zone 1) but never species eggs? | [yes; max 2 egg rows per visit] |
| 7 | Bazaar: list zone type eggs (coins can buy them, price climbs with demand), species eggs only on the Auction House? | [yes] |
| 8 | Fusing stops at Legendary (4 Epics -> 1 Legendary; no Legendary fusing, never Mythic)? | [yes] |
| 9 | Fusing cost: free, or a small coin fee per step? | [free] |
| 10 | Upgrade Stones: one per egg type (Mining, Foraging, Farming, Fishing, Combat, Mount, Explorer) + Dragon stones, and tradeable? | [yes] |
| 11 | Guardian first kill: you PICK which type of that zone's egg you get? | [yes] |

## For the local session

1. **Real rates (UNVERIFIED):** natural ore / log / crop XP awards per hour, kills per hour, fish per hour, chests per hour per zone -
   every egg rate in 3.1 is linear in them. Also confirm a hand-harvested crop only awards XP at its final stage.
2. **SkyySkills (small patch):** a 5th element on `pets:fn:onxp` (`block` / `crop` / `smelt` / `kill` / `other`) so offline smelting
   never rolls a Mining egg (`SkyySkills/build_skyyskills_0.4.29.py` line 7). Until then SkyyPets rolls only for online players.
3. **Kill hook:** how SkyyPets learns of a kill (role id + killer + elite flag) - a death event listener of its own, or a SkyyMobs bridge;
   UNVERIFIED which death event carries the killer. Exclude `Tamed_*`, baby roles, `Skyy_Pet_*`, other mods' summons.
4. **Zone lookup:** which bridge entry gives the zone at a position (SkyyMobs / SkyyWorldGen `wg:fn:ring`) and the Zone 5 depth rule.
5. **Egg items as assets:** a plain item per egg id needs an item JSON + icon in the jar (IncludesAssetPack is already true since 0.2).
   No vanilla texture may be copied into the repo: an original icon (skywynn-art rules) or one generated into the jar at build time.
   Check whether a vanilla egg item exists to use as a Parent by id (UNVERIFIED).
6. **Fishing pets:** no Fishing pet skill exists (`SkyyPets/build_skyypets_0.2.2.py` lines 232-233 skill icons: Farming, Mining,
   Foraging, Combat, Exploration) and SkyySkills has no Fishing row; Fishing eggs wait for a fishing XP source (SkyyFishing) or count
   as Exploration XP meanwhile.
7. **Merchants:** fill `merchant.pets` / `mount.` rows when 0.3 ships; optional `merchant.pets.perVisit`.
8. **Bazaar:** add the egg products; decide the sell-only flag (Q7).
9. Notes for other drafts (main session): `research/cloud/Pet-Sources.md` sections 1-6 and `research/cloud/Pet-Core-Spec.md` section 8
   phase 6 are superseded as listed in section 0.
