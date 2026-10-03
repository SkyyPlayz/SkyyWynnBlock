# Dragon hatching quest line - spec draft

Cloud draft, 2026-10-03. Paper design; nothing built. Sources: `research/Dragon-Pets-Idea.md` (Skyy's ideas), OPEN-QUESTIONS Q&A 2026-10-02 R8 / R9, `research/cloud/Pets-Spec.md`,
`research/cloud/Zone-Bosses-Ideas.md`, `research/cloud/Story-Script-Zones-2-5.md`. Creature models, flight and mount APIs are **UNVERIFIED** (no game files in the cloud).

## 0. Locks I am building on (Skyy)

| Lock | Source |
|---|---|
| Zone 5 = the dinosaur caves under Zone 4, Lv 60-75, dragon boss at 75 | R8 |
| **One dragon per profile** for now; later a much harder "find your lonely dragon a mate" quest gives a second egg | R8 |
| Dragons follow pet rules: combat XP + 50% of other XP; grow at set levels; **can be flown from Lv 10** (growth steps and flight level are settings) | R8 |
| Hatching by **quest line with a chosen element** (the stronger path in the idea doc); 5 quest elements + 4 secret ones (Blood, Void, Light, Crystal) | Dragon idea, items 4-5 |
| Dragons are Mythic pets with buffs + combat + flying mount; the summon slot rules from Pets (second slot = Summon slot, 50% buffs) | R6/R7 |
| **Dragon Upgrade Stones** (their own, not the general ones) raise a dragon | R9 |
| Dragon-only islands later; no `/fly` on zone islands, you only fly on a dragon | Dragon idea 7 |

## 1. The quest line (chosen element)

Total length target: about 2-3 hours for a Zone 5 player (one big trip + one mini dungeon). Everything is per profile and safe: the egg is bound and can be re-issued; dying never loses it.

| # | Quest | Where | The player does | Checks | Reward |
|---|---|---|---|---|---|
| D1 | **The Borrowed Egg** | Zone 5 dragon's nest | Finish the Zone 5 story fight; the dragon gives you its egg to look after ("you borrow it"). | story flag | **Dragon Egg** (bound, one per profile) |
| D2 | **Blank Check** | The Observatory of Almost (Zone 4) - **Dr. Voidwright** is the specialist | He scans the egg: "it has no element yet. I can make it any of five. Choose carefully, or don't." | egg delivered | scan result |
| D3 | **Pick An Element** | Observatory | The player chooses Earth / Thunder / Water / Fire / Air (a confirm; the choice sets the last item and the hatching place). Changeable only via a rare "Elemental Reset" item (see 5). | choice flag | element locked |
| D4 | **Four Pieces Of A Pie** | Zones 1-4 | Collect four **Essences**, one from each zone, themed to the element (table 2). Each is an item dropped by a zone elite or a harvest. | 4 items | 4 Essences |
| D5 | **The Last Ingredient** | per element (table 2) | One element-specific item from a place you only reach by solving the clue. Its location is also where the egg hatches. | item + position flag | Last Ingredient + clue to the Hatch Site |
| D6 | **Mini Dungeon** | Hatch Site (per element) | Fight through a short dungeon (about 10 minutes; 4 rooms + a mini boss, Lv 66-70) to the Nest Room. | boss kill | Nest Key |
| D7 | **Hatching** | Nest Room | Place the egg on the pedestal; set the Last Ingredient and the 4 Essences; a short hatch scene (rumble, crack, flash); the hatchling picks you. Name it. | all items placed | **Dragon pet (Mythic, Lv 1, hatchling)** + title "Hatchwright" |
| D8 | **First Flight** | any open area | Reach dragon Lv 10 (the flight level): the dragon's first rides. | level 10 | flight enabled, a "Rider" cosmetic |

Quest text uses the lore voice: Dr. Voidwright is the "mad scientist"; the Camp Clerk logs the egg ("Egg #2: please do not drop"); Pebble appears at the hatching: "I was here when the egg hatched. Was I? I'm a rock."

## 2. Elements, items and hatch sites (the 5 quest elements)

Models (UNVERIFIED): vanilla has `Dragon_Fire` and `Dragon_Frost` boss roles (Dragon-Pets-Idea). Plan: Fire = the Fire dragon, **Water = the Frost dragon recoloured to teal/blue** (frost is not Water, so recolour), the other three are recolours/retextures of the same rig generated at build time (never commit vanilla assets).

| Element | Zone theme for Essences (D4) | Last Ingredient (D5) | Hatch Site | Mini dungeon theme | Element boost (SkyyGear's Earth/Thunder/Water/Fire/Air Damage %) |
|---|---|---|---|---|---|
| **Earth** | Zone 1 ancient bark, Zone 2 sandstone core, Zone 3 permafrost root, Zone 4 ash-wood heart | **Heartstone** (a gem hidden in a Zone 1 Fens cave) | Overgrown temple vault under Zone 1's summit | roots and golems, vines, rock traps | +Earth damage %, Earth defence |
| **Thunder** | storm-struck wood, desert glass, lightning crystal, charged ash | **Stormglass** (Zone 3 Everfrost peak during a storm) | A lightning-struck spire in Zone 3 | lightning coils, outlander cultists | +Thunder damage %, Thunder defence |
| **Water** | spring water, oasis pearl, ice bloom, steam bloom | **Tide Pearl** (a Zone 2 Oasis grotto, requires a dive) | A sunken cavern in Zone 2's Oasis | water currents, crocodiles, drowned skeletons | +Water damage %, Water defence |
| **Fire** | ember bark, magma glass, frozen ember, ash heart | **Phoenix Cinder** (Zone 4 caldera) | The caldera rim (Zone 4) | lava rooms, fire golems | +Fire damage %, Fire defence |
| **Air** | wind-sung leaf, dune whisper, snow breath, ash cloud | **Cloud Feather** (a hidden shrine reached by a climb in Zone 2 plateaus) | A floating shard above Zone 2's plateau | wind tunnels, fall hazards (safe: no fall death, you respawn at the shard edge), raptor packs | +Air damage %, Air defence |

Element effect on the dragon: its breath attack is of that element (damage type) and it gives that element's damage/defence % as a pet perk. Models and dungeons are different **dressings** of one shared dungeon template to keep the build cost low (5 skins of one mini dungeon, not 5 dungeons).

## 3. Secret elements (Blood, Void, Light, Crystal)

Skyy: no quest or explanation; players should discover them. Proposals (all hidden, none listed in the quest text; hints only in lore books and a few odd NPC lines):

| Secret | Trigger idea | Why it fits |
|---|---|---|
| **Blood** | At D3, instead of choosing, feed the egg a Heart (a rare drop from a boss) at night in the Zone 4 caldera; the Observatory's machine "reads" the heart | life-steal dragon; the "darkest" egg |
| **Void** | Hatch the egg at the Void edge of your own personal shard (the starter shard) with a Void Fragment stack | the Void is the setting |
| **Light** | Hatch during daytime at the Zone 1 temple using a "Light Shard" gained from beating all four zone guardians without dying (a no-death run) | reward for skill |
| **Crystal** | Use eight different Crystal Shards (SkyyCollections: all eight crystal colours) as the Last Ingredient | collectible-based |

The hatch ceremony shows nothing different until the reveal; the Dragon's name card shows the element. A server can hide or disable secrets (`dragon.secretElements`).
Secrets get the same stats shape as normal elements plus one signature perk (Blood = life steal %, Void = pulls in enemies, Light = heals you, Crystal = reflect %). Balance: a secret is a sidegrade, not stronger (no power creep).

## 4. Growth, levels and flight

| Stage | Dragon level | Size | Notes |
|---|---|---|---|
| Hatchling | 1 | 0.4x | follows you, fights from Lv 1 (Mythic rule), cannot be ridden |
| Whelp | 10 | 0.7x | **flight unlocked** (setting `dragon.flightLevel`), short flights |
| Juvenile | 30 | 1.0x | longer flights, breath attack |
| Adult | 60 | 1.3x | full speed, passenger? (no) |
| Elder | 100 | 1.6x | dragon-only islands, mounted fighting |

(All steps are settings, per Skyy's lock.) Pet XP rules: dragon gets 100% of its own skill XP (combat) and 50% of all other XP (R6 lock).

### Flight rules (proposals; engine UNVERIFIED)
| Rule | Value |
|---|---|
| Where | any world except where blocked; on zone islands `/fly` stays off, dragon flight is the only flight |
| Stamina | flight drains the dragon's "wing stamina" (not yours); refills on the ground |
| Max altitude | 150 blocks above ground (setting) |
| Combat while riding | none at Whelp; breath attack from Juvenile (hold shoot) |
| Safety | dismount over void or lava: the dragon catches you (a short hover) |

## 5. Dragon Upgrade Stones and the "Elemental Reset"

| Item | Use | Source |
|---|---|---|
| **Dragon Upgrade Stone** (R9: dragons have their own) | raises the dragon's stat factor in steps (1.25 -> 1.35 -> 1.45 -> 1.55 ...; placeholder) | crafted from Void Fragments + the matching Essence; a cap of 5 steps |
| **Elemental Reset** (rare) | lets you change the element once (answer to the open "can the element be changed later?" - default: **no, except with this rare item**) | zone 5 elite drop, very rare |
| **Egg replacement** | re-issues a lost egg (bound item) | the Egg Desk clerk, free |

## 6. The "mate" quest (later; Skyy's idea)

When the dragon reaches Elder (Lv 100) it gets lonely. A much harder quest (an elite zone 5 dungeon + a rare ingredient) finds a mate, then gives a second egg. Outline only:
1. The dragon becomes restless (a flavour message at Lv 100).
2. Dr. Voidwright: "it needs company. I know a rumor." A chain of 3 clues across zones.
3. A Mythic boss fight in Zone 5 (Lv 75-80).
4. A second egg; it may be a **different element** (a mix) - leaves the element-choice for later.
Raises the cap to 2 dragons per profile (setting `dragon.maxPerProfile`, default 1).

## 7. Server Setup rows (sketch)

`dragon.enabled`, `dragon.maxPerProfile` (1), `dragon.flightLevel` (10), `dragon.growthLevels` (1,10,30,60,100), `dragon.growthSizes`, `dragon.secretElements` (on), `dragon.elementResetEnabled`,
`dragon.upgrade.maxSteps` (5), `dragon.flight.maxAltitude`, per-element rows (essence ids, last ingredient id, hatch site), dungeon level (66-70), cooldown after a dragon defeat (60 s down to 15 s with level - R6/R7).

## 8. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Can a mod add a flying rideable creature? Check the vanilla mount system (horses/camels are ground mounts) and the flying creatures (Dragon bosses, pterodactyl) for a rider seat. If not, fallback: a glide/boost (no free flight) or a wing item. |
| 2 | Can the model scale at runtime per level (growth stages)? |
| 3 | Recolours of the Dragon rig at build time (texture swap) without committing vanilla assets. |
| 4 | Where the mini dungeon instances live (SkyyDungeons plan, instance worlds) and how an instance is entered with a key. |
| 5 | A per-profile quest/flag store (the same quest system the story needs). |
| 6 | The Zone 5 world does not exist yet; hatch sites for Earth/Water/Air sit in Zones 1-3 and need prefab/placement work. |

## 9. Questions for Skyy

1. Element changes: never, or only with the rare Elemental Reset item (my default)?
2. Should a dragon be tradeable/sellable? (Recommended: never - it is bound to the profile.)
3. Secret elements: are my four triggers (Blood at night with a Heart, Void on your shard, Light on a no-death run, Crystal with 8 shards) the right spirit, or do you want to design them?
4. Is "the mini dungeon is one template with 5 skins" fine, or should each element have its own dungeon?
