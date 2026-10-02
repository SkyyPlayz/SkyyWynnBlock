# Zone boss ideas - guardians for Zones 1-4 and the Zone 5 dragon

Cloud draft, 2026-10-02. Ideas only; nothing built. Bands/guardian levels: OPEN-QUESTIONS LOCKED 2026-10-01 (guardians at **20 / 30 / 45 / 60**),
`research/cloud/Mob-Levels-Refit.md`, `research/SkyyWorldGen-Plan.md` (summit arena + summit portal), `research/Isles-of-the-Void-Lore.md`,
`research/Dragon-Pets-Idea.md`. Attacks, arenas and drops are my proposals; **what each vanilla boss really does (moves, health, role ids) is UNVERIFIED** - I had no game files.

## 0. What vanilla Hytale already has (web search, not verified in game)

| Zone | Vanilla bosses named in guides | Source |
|---|---|---|
| 1 Emerald Wilds | Trork Chieftain (Trork camps), Earthen Golem (Forgotten Temple Gateway, Drifting Plains), Burnt Skeleton Praetorian | [Hytale boss guides](https://allthings.how/hytale-bosses-so-far-and-how-to-track-each-one-down/) |
| 2 Howling Sands | Scarak Broodmother (Scarak nests), Goblin Duke (goblin dungeons), Sandswept Golem | same |
| 3 Frozen / Borea | Yeti, Frost Golem, Outlander Chief / Colossus (Outlander creatures listed) | same + [creature list](https://hytale.fandom.com/wiki/Monsters) |
| 4 Devastated Lands | Fire / Ember / Firesteel Golem, Cave Rex ("in development" in some guides), Emberwulf | same |
| Beyond | Frost Dragon, Fire Dragon (role files per Dragon-Pets-Idea), Void creatures | same + Dragon-Pets-Idea |

Locally seen already (Dragon-Pets-Idea, read in Assets.zip): `Dragon_Fire`, `Dragon_Frost`, `Rex_Cave`, `Raptor_Cave`, `Pterodactyl`, `Trillodon`.

## 1. Design rules (so all five feel like one set)

| Rule | Value |
|---|---|
| One guardian per zone island, in the summit arena next to the summit portal | WorldGen plan 4.x |
| Fixed level from `scale.role` (never random): Zone 1 **20**, Zone 2 **30**, Zone 3 **45**, Zone 4 **60** | LOCKED bands |
| Health | about 12x a normal mob of the same level (a 2-3 minute solo fight at the right gear; a party of 3 about 1 minute). Row `scale.role.<Role>.hpMult` |
| Three phases (100% / 66% / 33%) | each adds one new move so the fight changes; phase change shows a vanilla boss bar message |
| One mechanic the zone taught: Z1 dodge, Z2 positioning, Z3 resist/warmth, Z4 fire/line of sight | tutorial through the zone |
| Beaten once per profile to unlock the next island; can be re-fought on a cooldown for loot (not for unlock) | per-profile unlock flag |
| Never kills items: no item loss on death (Hytale default) - death = "sent back to your seat" (lore) | |

## 2. The guardians

### Zone 1 - "The Second-Page Guardian" (Earthen Golem), Lv 20

| Item | Idea |
|---|---|
| Base | Earthen Golem (vanilla boss at the Forgotten Temple Gateway - fits the Zone 1 temple town). UNVERIFIED role id |
| Story | Guards "page 2" of Form 27-B/6; mildly offended nobody reads it (see Story-Script-Draft) |
| Arena | Overgrown ruined stage on the summit; stone pillars you can hide behind; a ring of mossy rubble |
| Attacks | Slam (telegraphed circle), rock throw, **Root Grab** (phase 2: roots snare you for 2 s unless you jump), phase 3: summons 3 small rock mites |
| Mechanic taught | Reading telegraphs and dodging |
| Drops | Second Page (quest item), Portal Fragment for the summit portal, 1 zone-1 gear drop (Lv 18-22, unidentified), 15% **Cracked Shard Core** (Pocket Shards), 1 Common-Uncommon **Pet Egg** (Pets-Spec) |
| Elite variant | Mid boss: **Trork Chieftain** at Zone 1 dungeon (Lv 20-23) |

### Zone 2 - "The Broodmother" (Scarak Broodmother), Lv 30

| Item | Idea |
|---|---|
| Base | Scarak Broodmother (vanilla Zone 2 boss). UNVERIFIED |
| Story | A huge mother with very organised paperwork: "page 3 is in the nest. Mind the eggs." |
| Arena | Sand nest cavern at the summit of the Howling Sands island, egg clusters you can destroy |
| Attacks | Spit (line damage), burrow-and-emerge (damage circle at your position), call larvae; phase 3 = frenzy (+20% speed) |
| Mechanic taught | Keep moving, destroy eggs before they hatch (priority targets) |
| Drops | Page 3 (quest), Portal Fragment, 1 zone-2 gear drop (Lv 28-32), Scarak chitin + Void Fragment, 20% Rare Pet Egg (Camel-themed mount egg maybe), mount-slot quest hook (Pets-Idea: stable master at Zone 2 town) |
| Elite variant | **Goblin Duke** in the Zone 2 goblin dungeon (Lv 30-33, wide-range mid boss) |

### Zone 3 - "The Everfrost Yeti" (Yeti, with Frost Golem minions), Lv 45

| Item | Idea |
|---|---|
| Base | Yeti (vanilla Zone 3 boss), frost golems as phase adds. UNVERIFIED |
| Story | The archivist's rival; "the records hall is behind me, and I'm very cold" |
| Arena | Frozen records hall, ice patches that slide you, braziers that warm you |
| Attacks | Ground pound + shockwave, ice breath cone, **Whiteout** (phase 2: visibility drop and slow unless you stand by a brazier), phase 3: avalanche from the walls |
| Mechanic taught | Warmth zones (braziers) - the Zone 3 survival layer |
| Drops | Page 4 (quest), Portal Fragment, 1 zone-3 gear drop (Lv 43-47), Frost crystal + Void Fragment, Epic Pet Egg chance, **Void Fragment x2** |
| Elite variant | **Outlander Chief** (with Outlander warriors) as the Zone 3 dungeon boss (Lv 45-48) |

### Zone 4 - "The Ember Warden" (Fire / Ember Golem), Lv 60

| Item | Idea |
|---|---|
| Base | Fire Golem (Zone 4 spawn) or the Firesteel / Ember Golem boss. UNVERIFIED (which exists as a boss role) |
| Story | A furnace that ran out of coal and feelings; "page 5: only I can read it, and I can't" |
| Arena | Caldera lip with lava channels; safe platforms that sink then rise; steam vents |
| Attacks | Magma slam, lava lob (arc), **Heat Pulse** (phase 2: you must stand on a cooled platform), phase 3: detonate (big circle, you must be behind rock) |
| Mechanic taught | Line of sight and standing in the right place |
| Drops | Page 5 / "the Last Stamp", Portal Fragment to the Zone 5 caves, 1 zone-4 gear drop (Lv 58-62), Ember core + Void Fragment x3, Epic-Legendary Pet Egg chance |
| Elite variant | **Cave Rex** as the Zone 4 dungeon boss (Lv 60-63) - and a teaser for Zone 5 |

### Zone 5 - "The Dragon" (Zone 5 caves, dinosaur land), Lv 70+

Lore: the Void's hiccups are caused by a dragon trying to get its egg back (Lore pitch 1); the dragon knows the way home (Zone 5 step of the "where are you from" chain).

| Item | Idea |
|---|---|
| Base | `Dragon_Fire` / `Dragon_Frost` roles exist as bosses (Dragon-Pets-Idea); recolour for other elements later. UNVERIFIED which moves they have |
| Arena | A giant cave with a lava lake, bone ribs and a high ledge for the egg; the dragon flies in circles then lands |
| Attacks | Flame breath cone, tail sweep, dive bomb (telegraphed shadow), phase 2: takes off and drops fire rain, phase 3: lands and calls dinosaur adds (Raptor_Cave, Pterodactyl) |
| Mechanic taught | Everything: dodge, kill adds first, stand right, use cover |
| Drops | **Dragon Egg** (quest item - hatching quest line, see Dragon-Pets-Idea), the final Stamp (quest end), Legendary gear chance, big Void Fragment stack |
| Notes | The dragon is non-hostile after the fight (it gets its egg back - the egg was never yours; you borrow it later) |

## 3. Shared drops and unlocks

| Drop | Used for |
|---|---|
| Portal Fragment (per zone) | Summit portal to the next island (unlock flag; consumed once per profile) |
| Void Fragment | Shard Core, Pet Upgrade Stone, Pocket Shard T11, rarity-boost crafts (see Pocket-Shards-Spec, Pets-Spec) |
| Zone gear drop | Unidentified gear at the guardian's level (Gear-Levels spec stage 4) |
| Pet Egg (rarity by zone) | Pets-Spec |
| Cosmetic / title ("Guardian Slayer: Zone N") | Prestige, shown on the profile |

## 4. Balance / numbers (placeholders)

| Zone | Level | Health x (vs normal mob) | Damage x | Fight time solo (target) |
|---|---|---|---|---|
| 1 | 20 | 12 | 1.2 | 2-3 min |
| 2 | 30 | 12 | 1.2 | 2-3 min |
| 3 | 45 | 14 | 1.3 | 3 min |
| 4 | 60 | 15 | 1.3 | 3-4 min |
| 5 | 70 | 20 | 1.5 | 5 min solo, party recommended |

The normal-mob health is base health x (1 + 0.04 x (L - 1)) from Mob-Levels-Plan section 5 (Lv 20 = x1.76, Lv 60 = x3.36).

## 5. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Which of the listed boss roles exist in the shipped Assets.zip (`Server/NPC/Roles/Boss/*`): Earthen Golem, Scarak Broodmother, Yeti, Fire/Ember Golem, Trork Chieftain, Goblin Duke, Cave Rex, Dragons; their model ids, attacks, health. |
| 2 | Whether bosses can be spawned by plugin at a fixed point with a level (SkyyMobs `mob:fn:setLevel` stage 3) and given a boss bar. |
| 3 | Whether `Env_Zone4_Encounters*` / village envs have spawns (WorldGen plan notes they do not) - the arena should spawn its boss by script, not by environment. |
| 4 | Phase changes: hook on health thresholds (damage event listener on the boss entity). |
| 5 | Arena prefabs: which vanilla arena/temple prefabs can be reused (Earthen Golem's Forgotten Temple Gateway for Zone 1). |
| 6 | Re-fight cooldown and loot-per-profile storage (SkyyProfiles contract). |

## 6. Questions for Skyy

1. Guardian = vanilla boss (as above) or all-new bosses later? (Recommended: vanilla first, re-skin later.)
2. Zone 4 guardian: Fire Golem or Cave Rex (with the Dragon as the only Zone 5 boss)? (Recommended: Fire Golem here, Cave Rex as the dungeon boss.)
3. Should the guardian be re-fightable every day for loot? (Recommended: yes, daily cooldown, reduced loot.)
