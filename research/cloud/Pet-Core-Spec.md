# Pet core spec (slot pets: data, lifecycle, commands, UI, safety, build phases)

Cloud draft, 2026-10-09. Paper design; nothing built. This is the CORE system every pet uses. The roster (which creatures, scale, zone,
start rarity) is `research/Pets-Roster.md`; sources and egg odds are `research/cloud/Pet-Sources.md`; rarity / XP curve / perk
archetypes are `research/cloud/Pets-Spec.md` (sections 2-3) - this file does not repeat them. New mod: **SkyyPets** (standalone, zero
hard dependencies, bridge only). Every number is a placeholder and a Server Setup row (times in seconds).

## 0. Decisions this follows (LOCKED - not re-decided)

| Lock | Source (`docs/answered/pets.md` line) | Used in |
|---|---|---|
| Slot 2 unlocked by a ZONE 2 STABLE QUEST (stable master gives the slot + your first mount pet) | 12 (R6) | 1, 6 |
| Slot 2 gives buffs at 50%, always (Server Setup row); a later hotkey SWAPS the two slots | 13, 17 (R6, R7) | 4, 6, 9 |
| Pet XP = own skill's XP + 50% of all other XP (editable) | 14 (R6) | 1, 6 |
| A fighting pet at 0 health retreats into its slot, loses nothing, comes back after a cooldown (60 s, editable) | 15 (R6) | 2 |
| That cooldown SHRINKS with pet level (60 s at Lv 1 to about 15 s at Lv 100, editable) | 16 (R6) | 2, 6 |
| ONLY slot 2 fights = the SUMMON SLOT (mounts AND combat pets; fights on foot, ridden when you mount); slot 1 = pet slot, full buffs, never fights | 17 (R7) | 2, 4 |
| One dragon per profile; dragons follow pet rules, grow, fly from Lv 10 | 19, 20 (R8) | 1 (cap), 9 |
| Rarity raised with Upgrade Stones PER SKILL / minion type (dragons: Dragon stones); eggs at higher rarities; pets PER PROFILE | 21 (R9) | 1 |
| Dragon may be Aures' Nestkeeper dragon summoned / linked by our slot 2 (open, OPEN-QUESTIONS.md "pets") | 28 | 9 (not here) |
| Pets look like the mob but smaller + cuter; mounts about normal size or bigger | 31 | 2 |
| Launch every pet as a SHRUNK vanilla model by id at runtime (never copied); chibis by Quirk later; vanilla babies stay as they are | 32 | 2, 8 |
| No Kweebecs, no Trorks (other humanoid races: not pets) | 33, 34 | roster |
| "Yes to all": ~30 pets at launch then zone batches; variants = skins; baby until pet Lv 30; hostile pets use their own attack, damage % of your weapon; mount pets pet-size in slot 1; water pets follow only while swimming; creatures drop their own egg 0.1% / elites 1%; no boss pets; Grooble yes, Bee swarm no | 34 | 1, 2, 4 |
| Tamework: check its design (idea, not a dependency) | 35 + `research/Tamework-Review.md` (borrow ideas, do not depend) | 2, 3 |
| Roaming merchants: launch stock "Special weapons, Mounts, Pet eggs later" (a pet-egg slot filled when pets ship) | `docs/answered/economy.md` 92 (newest; beats `research/cloud/Pet-Sources.md` "no NPC sells eggs") | 5, 8 |

Borrowed from Tamework (ideas only, own words, no code / numbers copied - it is GPL v3): owned cap vs active cap, summon time limit +
resummon cooldown, auto-store on logout, revive cost + cooldown, Follow / Defend / Hold.

## 1. Data model (per profile)

**Pick: pets are RECORDS, not items.** Eggs are items (section 5).

| Why records | |
|---|---|
| Per-pet data | level, XP, rarity, skin, name, cooldowns - an item would need metadata, and metadata ItemStacks crash the client in an `ItemGridSlot` (`HANDOFF.md` section 2, SkyyAuctions 0.1 disconnect) |
| Cannot be lost | a record never drops on death, never despawns on the ground, never falls in the void, never sits in a chest that breaks |
| Cannot be duplicated by item tricks | no stack split, no drop-and-relog, no chest / crafting-grid race, no profile-switch inventory window (`tools/PROFILES-CONTRACT.md` section 5: up to 30 s of items can exist twice after a crash) |
| One owner | each pet has a unique id; one file holds it; moves are logged (section 7) |
| Cost | trading needs our own escrow (section 7) instead of "drop the item" - acceptable, the Auction House already goes through our code |

File: `<world>/mods/Skyy_SkyyPets/pets/<pkey>.properties` (`pkey` = `tools/PROFILES-CONTRACT.md` helper; profile 1 = `<uuid>`).

| Key | Example | Meaning |
|---|---|---|
| `v` | `1` | file format |
| `seq` | `418` | +1 on every write (newest copy wins in the startup check, section 7) |
| `slot2.unlocked` | `true` | set by the Stable quest (or admin / row `pets.slot2.unlock`) |
| `active.1` / `active.2` | `p7k2m9` / `` | pet id in the pet slot / summon slot ("" = empty) |
| `cmd` | `follow` | summon command: `follow`, `defend`, `hold` |
| `shown.1` | `true` | the player's "show my slot-1 pet" toggle |
| `pet.<id>.kind` | `Fox` | roster id (`research/Pets-Roster.md` family) |
| `pet.<id>.rarity` | `2` | 1 Common .. 5 Legendary, 6 Mythic (dragons only) |
| `pet.<id>.level` / `.xp` | `12` / `345` | level 1-100, XP into the current level (curve: `research/cloud/Pets-Spec.md` 3) |
| `pet.<id>.skin` | `Wolf_White` | chosen skin (model id of the family) |
| `pet.<id>.name` | `Biscuit` | optional, 1-20 chars, sanitized |
| `pet.<id>.got` / `.src` | `1760000000000` / `egg:Z1` | when + how obtained (audit) |
| `pet.<id>.lock` | `true` | favourite: cannot be released / listed |
| `pet.<id>.downUntil` | `1760000123000` | defeat cooldown end (wall clock ms, so a relog does not skip it) |
| `pet.<id>.reviveAt` | `0` | last paid revive (section 2) |
| `album` / `skins` | `Fox,Wolf,...` | kinds / skins ever found (Pet Album, pet score later; never shrinks) |
| `hatch.<n>` | `Skyy_PetEgg_Z1|<start>|<end>` | eggs hatching at the Stable |

- **Pet id:** 8 random base-36 characters + a check on every loaded file (collision = reroll). Global, never reused.
- **Owned cap** (Tamework "MaximumOwned"): row `pets.owned.max` default 120. A full collection blocks new hatches with a clear message
  (eggs stay items, nothing is lost). **Active cap** = the 2 slots (locked); one pet cannot sit in both.
- **Dragon cap:** a second `kind=Dragon_*` record is refused (R8 "one dragon per profile").
- **XP in:** SkyySkills has no XP-gained hook on the bridge today (`SkyySkills/build_skyyskills_0.4.25.py` publishes `skill:fn:addxp`,
  `skill:fn:level`, `skill:bonus:` - nothing that tells another mod about a gain). Needs a small SkyySkills addition: after every award it
  calls `pets:fn:onxp` = `Function apply(Object[] { UUID, String skill, Long amount })` if present (plain types, never throws). SkyyPets
  gives each active pet `amount x 100%` if `skill` = the pet's skill, else `x 50%` (rows). Kills by the pet count as the owner's (below).

## 2. Summon / despawn lifecycle

Both slots spawn a visible creature (slot 1 only when `shown.1` is on). The creature is a **throwaway view** of the record: it holds no
data; killing, unloading or losing it never changes the record except slot 2's defeat cooldown.

### 2.1 States (slot 2; slot 1 uses only HIDDEN / OUT)

| State | Means | Buffs |
|---|---|---|
| EMPTY | no pet in the slot | - |
| HIDDEN | in the slot, not spawned (dismissed, blocked world, swimming-only pet on land, owner dead) | yes (slot 2: 50%) |
| OUT | spawned, obeys `cmd` | yes |
| DOWN | lost all health: despawned, waits `downUntil`, then back to OUT by itself (row `pets.down.autoReturn` on) | yes (R6: "loses nothing") |
| RIDDEN | owner is mounted on it (mount pets only, phase 5) | yes |

### 2.2 Events

| Event | What happens |
|---|---|
| Join (first PlayerReadyEvent) | load the record through `pkey`; after `pets.spawn.delay` (2 s) spawn slot 1 (if shown) + slot 2 (if it was OUT or DOWN-expired) next to the player |
| Logout (PlayerDisconnectEvent) | **auto-store** (Tamework idea): despawn both, flush the file. Nothing to lose: the record was already saved |
| World change | despawn when the player leaves the world; respawn on the next PlayerReadyEvent in the new world (`tools/PROFILES-CONTRACT.md` 3: later PlayerReadyEvents = world switches) |
| Profile switch (`profile:epoch:<uuid>` changes) | despawn both, flush under the OLD key, re-resolve `pkey`, load, respawn (contract section 4 pattern) |
| Owner dies | both despawn (HIDDEN); respawn with the owner. No cooldown (the pet did not lose) |
| Pet at 0 health (slot 2) | it never really dies: on lethal damage despawn it (a puff), set `downUntil = now + cooldown(level)` |
| Too far away (> `pets.follow.teleport` 24 blocks, or a different height band) | teleport next to the owner (vanilla Test_Pet role does the same) |
| Blocked world (`pets.worlds.blocked`, e.g. dungeon instances) | stay HIDDEN; buffs still work unless `pets.worlds.noBuffs` lists the world |
| Water pet on land | HIDDEN until the owner swims (locked) |
| Server stop / crash | nothing saved on the entity matters; the startup ghost sweep (section 7) removes any leftover pet creature |

Defeat cooldown (R6 ADDED, linear between two rows `pets.down.lv1` 60 s and `pets.down.lv100` 15 s):
`cooldown(L) = lv1 - (lv1 - lv100) x (L - 1) / 99` -> Lv 1 60 s, Lv 10 55.9 s, Lv 25 49.1 s, Lv 50 37.7 s, Lv 75 26.4 s, Lv 100 15 s (python3).

### 2.3 Tamework ideas, fitted to the locks

| Idea | Our rule | Row (default) |
|---|---|---|
| Summon duration | slot pets stay out as long as you like; an owner MAY set a limit (then the pet goes HIDDEN, buffs stay) | `pets.summon.maxSeconds` 0 = no limit |
| Resummon cooldown | after YOU dismiss slot 2, wait before summoning again (stops dismiss-spam to drop aggro / reset the pet) | `pets.summon.recall` 5 s |
| Auto-store on logout | yes (2.2) | - |
| Revive cost + cooldown | optional early return from DOWN for coins; the lock says a defeat costs nothing, so this is a SHORTCUT, never a penalty; off by default | `pets.revive.cost` 0 coins (0 = off), `pets.revive.cooldown` 300 s |
| Follow / Defend / Hold | section 3 | `pets.cmd.default` follow |

## 3. Commands for the summon (slot 2 only)

| Command | Pet does | Notes |
|---|---|---|
| **Follow** (default) | follows (stops at 3 blocks); attacks only what YOU hit (assist) | the vanilla Template_Summoned_Ally idea: turn on what the leader hits (`research/Pets-Roster.md` 2.2) |
| **Defend** | follows; also attacks anything that hits you, or any hostile that comes within `pets.defend.radius` 12 blocks | never starts on neutral animals or players |
| **Hold** | stays where it was told; fights anything hostile within 8 blocks of that spot; teleports back to you if you go past `pets.hold.leash` 48 blocks | not saved across logout: next spawn is Follow |

- Never: hit its owner, the owner's party, other players' pets, or players at all unless `pets.pvp` is on (default off).
- A combat pet's hit = its own vanilla attack animation, damage = % of the owner's weapon (locked; % per rarity + level in
  `research/cloud/Pets-Spec.md` 6, row `pets.fight.damagePercent`). Kills credit the owner (XP, collections, drops).
- Slot 1 has no commands: it follows (or sits when you stand still), is invulnerable, ignored by mobs, and never fights (R7).

How to give a command (vanilla-look, no new keybind yet): the Pets page buttons, `/pet follow|defend|hold`, and right-click (use) your
own summon -> cycles Follow -> Defend -> Hold with a chat line. Other players using your pet are cancelled (UseEntityEvent$Pre
`setCancelled`, the same call `SkyyTownProbe/build_skyytownprobe_0.1.py` line 267 probes). The slot-swap hotkey is "later" (R6).

### 3.1 Chat commands (HANDOFF section 3 rules)

| Command | Who | Notes |
|---|---|---|
| `/pets` (alias `/pet`) | Adventurer (`setPermissionGroups(new String[] { "hytale:Adventurer" })` on the command AND each subcommand) | opens the Pets page |
| `/pet summon`, `/pet dismiss`, `/pet follow`, `/pet defend`, `/pet hold`, `/pet show`, `/pet hide` | Adventurer | each a subcommand (no positional optional args) |
| `/petadmin give <player> <kind> [rarity] [level]`, `take <player> <id>`, `list <player>`, `setlevel`, `unlock <player>` (slot 2), `restore <player> <id>` (from the ledger), `sweep` | `requirePermission("skyypets.admin")` | usage variants for every documented form; admin-only, never Adventurer |

## 4. Slot 1 passive vs slot 2 combat

| | Slot 1 - pet slot | Slot 2 - summon slot |
|---|---|---|
| Unlock | from the start (starter Rabbit) | Zone 2 Stable quest (R6) |
| Buffs | 100% | 50% (`pets.slot2.buffPercent`, R6) |
| Fights | never (R7) | yes, if the pet's archetype fights (Pets-Spec rarity "fights from level"); a pet that cannot fight just follows |
| Takes damage | no (invulnerable, ignored) | yes (role health from level); DOWN at 0 |
| Mount | a mount pet shows at PET size (locked) and is never ridden | shown at mount size; you can ride it (phase 5) |
| AI role | `SkyyPet_Follow` (Variant of vanilla template by name: invulnerable, seek owner, teleport when far) | `SkyyPet_Fight` (Template_Summoned_Ally idea: owner flock, assist), `SkyyPet_Fly`, `SkyyPet_Swim`, later `SkyyPet_Mount` |
| Per tick | buffs only (1 s) | buffs + target pick for Defend / Hold (1 s) |

**Buff feed paths** (`research/Accessory-Pack-Inventory.md` 3.4, all bridge, active profile, republish on epoch, remove on leave):

| Buff | Path | Blocker |
|---|---|---|
| Strength, Crit, Defence, Damage % ... | `gear:extra:<uuid>` | **one String per player** today (`SkyyGear/build_skyygear_0.2.11.py` line 11147 reads a single value; gap G4). SkyyGear must accept a source -> string map first, or pets overwrite accessories |
| Wisdom (XP %), Fortune | `skill:bonus:<uuid>` map, source `pets` | none (a map already) |
| Speed / jump | `move:<uuid>` map, source `pets` | none |
| Max Health / Stamina / Mana | `EntityStatMap.putModifier(..., "skyypet_<key>", ADDITIVE)` | none (remove keys when unused) |

## 5. UI pages (vanilla look, inline only)

Rules: vanilla colours / frames / buttons from Assets.zip (`research/Vanilla-UI-Style-Guide.md`, shared kit `tools/skyyui.py`); inline
pages, no `.ui` files; element ids without underscores (`#SkyyPetRow0`); never a metadata ItemStack in an `ItemGridSlot`
(icons = `new ItemStack(iconItemId, 1)` of a plain icon item per kind); never update a page from MouseEntered / MouseExited.

| Page | Opens from | Shows | Buttons |
|---|---|---|---|
| **Pets** | `/pets`, SkyyMenu tile | top: two slot cards (icon, name, rarity colour, Lv + XP bar text, state OUT / HIDDEN / DOWN 37 s); below: owned list, 8 rows a page, sort (rarity / level / kind), filter (skill) | per row: To slot 1, To slot 2, Details; slot 2 card: Summon / Dismiss, Follow / Defend / Hold, (Revive N coins when on); page arrows |
| **Pet details** | Details | kind, rarity, level, XP to next, perks at this level (archetype text), skin list (owned skins only), name | Rename, Skin, Favourite, Release (confirm twice; refused if `lock` or in a slot) |
| **Stable** | Stable NPC (UseEntityEvent) | eggs in your inventory you can hatch; hatching list with time left (seconds) | Hatch (moves 1 egg in), Claim; Bond (phase 3); quest dialogue for slot 2 is SkyyQuests' / the NPC's job |
| **Pet Album** (later) | Pets page tab | per zone: found kinds, silhouettes for missing, skin dots | none |

## 6. Server Setup rows (SkyWynn Menu -> Server Setup -> Pets; `tools/CONFIG-CONTRACT.md`; times in seconds)

| Key | Type | Default | Flags | Help |
|---|---|---|---|---|
| `pets.enabled` | bool | true | part, danger | whole pet system (records kept when off) |
| `pets.owned.max` | int 1-1000 | 120 | live | pets one profile may own |
| `pets.slot2.unlock` | choice quest / always / off | quest | live | how the summon slot unlocks |
| `pets.slot2.buffPercent` | int 0-100 % | 50 | live | R6 lock default |
| `pets.xp.ownPercent` / `pets.xp.otherPercent` | int 0-500 % | 100 / 50 | live | R6 lock defaults |
| `pets.down.lv1` / `pets.down.lv100` | int 0-3600 s | 60 / 15 | live | defeat cooldown at Lv 1 / Lv 100 |
| `pets.down.autoReturn` | bool | true | live | come back by itself after DOWN |
| `pets.summon.maxSeconds` | int 0-86400 s | 0 | live | 0 = no limit |
| `pets.summon.recall` | int 0-600 s | 5 | live | wait after dismissing slot 2 |
| `pets.revive.cost` | int 0-1,000,000 coins | 0 | live | 0 = no paid revive |
| `pets.revive.cooldown` | int 0-86400 s | 300 | live | between paid revives |
| `pets.cmd.default` | choice follow / defend / hold | follow | live | command a new summon starts with |
| `pets.follow.stop` / `pets.follow.teleport` | int blocks | 3 / 24 | live | |
| `pets.defend.radius` / `pets.hold.leash` | int blocks | 12 / 48 | live | |
| `pets.fight.damagePercent` | range % | 10-30 | live | weapon % by rarity + level (Pets-Spec 6) |
| `pets.pvp` | bool | false | live, danger | pets may hit players |
| `pets.spawn.delay` | int 0-30 s | 2 | live | after join / world change |
| `pets.worlds.blocked` / `pets.worlds.noBuffs` | text (world names, comma) | "" / "" | live | |
| `pets.scale.min` | dec | 0.3 | live | smallest pet scale (Roster 2.3 test) |
| `pets.babyUntil` | int 1-100 | 30 | live | locked default (Lv) |
| `pets.sweep.seconds` | int 5-600 s | 10 | adv | ghost-creature sweep |
| `pets.xp.flushSeconds` | int 5-600 s | 30 | adv | XP save interval |
| per pet (`pets.<kind>.enabled / model / skins / scale / zone / rarity / archetype`) | table | from the roster | live | `research/Pets-Roster.md` 3.2 |

## 7. Dupe / loss safety

| Risk | Guard |
|---|---|
| Two copies of one pet | ids are global; at startup SkyyPets scans every `pets/*.properties` into a `petId -> pkey` index; an id in two files keeps the higher `seq`, moves the other line to `quarantine/` and logs it (admin decides) |
| Lost write / crash mid-write | tmp file + fsync + atomic rename, 5 retries on Windows `FileSystemException` (the SkyyProfiles pattern); create / release / move / hatch flush at once, XP every 30 s and on logout (a crash loses at most 30 s of pet XP, never a pet) |
| Audit + undo | append-only `Skyy_SkyyPets/ledger.log`: one line per create / release / slot change / escrow move (`time id kind rarity level from-pkey to-pkey reason`); `/petadmin restore` rebuilds a pet from it |
| Ghost creatures (pet entity saved in a chunk, then the server restarts) | pet creatures use our own role names `SkyyPet_*`; a live map `entity UUID -> owner`; any `SkyyPet_*` entity not in the map is removed on sight (sweep every 10 s + on chunk load). Also try to spawn them non-persistent (UNVERIFIED P5) |
| Killing a pet for loot / XP | pet roles have no drop list and give no kill XP; slot-1 pets are invulnerable |
| SkyyMobs levelling our pets | SkyyMobs excludes `Test_*`, `Tamed_*`, `Risen_*` ... (`SkyyMobs/build_skyymobs_0.1.5.py` line 775) and passive roots incl. Template_Summoned_Ally (line 734); `SkyyPet_*` must be excluded too (add to its list or confirm it only touches vanilla roles - UNVERIFIED P8) |
| Profile switch | pets despawn before the new profile loads; no item crosses, so `profile:busy` matters only for egg items (hatch refuses while busy) |
| Eggs (items) | an egg is consumed FIRST (`removeItemStackFromSlot` succeeded), then the hatch line is written; a write failure gives the egg back; a crash in between is in the ledger ("hatch-intent") for `/petadmin restore` |
| Trading (later) | never as items: the Auction House calls `pets:fn:escrow` (record moves to `escrow/<id>.properties`, out of the seller's file, ledger line); a sale moves it into the buyer's file; a cancel moves it back. One file holds the pet at every moment |
| Releasing | confirm twice, refused for favourites and slotted pets; `/petadmin restore` can bring it back from the ledger |

## 8. Build phases (small versions) + engine probes first

| # | Version | What | Round (PROJECT-RULES 4) | Needs |
|---|---|---|---|---|
| P | SkyyPetProbe 0.1 (test-only, never in SET) or Skyy's creative `/npc spawn` test | probes P1-P10 below | lean | - |
| 1 | SkyyPets 0.1 | records + file + ledger + startup check; `/pets` page (slots, owned list, details); slot 1 + slot 2 buffs (no creatures); XP via `pets:fn:onxp`; admin give / take / unlock; Server Setup rows; ~30 launch kinds as data | **Ultracode** (new system, saved data) | SkyySkills hook, SkyyGear `gear:extra` map |
| 2 | SkyyPets 0.2 | visible pets: shrunk vanilla model, `SkyyPet_Follow`, lifecycle 2.2, ghost sweep, teleport-when-far, babies until Lv 30 | Full | P1-P5 |
| 3 | SkyyPets 0.3 | eggs (items) + Stable page + hatching + creature-egg drops (0.1% / 1%) + bond | Full (items, economy) | Stable NPC (roaming merchant code is the same spawn + UseEntityEvent idea) |
| 4 | SkyyPets 0.4 | summon slot fights: `SkyyPet_Fight` / `_Fly` / `_Swim`, Follow / Defend / Hold, DOWN + level cooldown, optional revive, kill credit | Full | P6, P7, P9 |
| 5 | SkyyPets 0.5 | mount pets in slot 2 (Horse, Camel, Ram first) | Full | P10 |
| 6 | SkyyPets 0.6 | Auction House escrow trading | Full (economy) | SkyyAuctions change |
| later | - | Pet Album + pet score, skins, Upgrade Stones per skill, slot-swap hotkey, roaming-merchant egg slot (`docs/answered/economy.md` 92), dragons, chibi model ids, optional Tamework bridge, pack-mod pets (below) | lean each | - |

**Pack-mod pet candidates** (later, by id at runtime only, PACK.md rules): Better Mob Expansion (GPLv3, credit required): tortoises, fairy,
butterfly, leopard, panther, bigfoot, imp, slimes, sharks (`research/Boss-Mods-Review.md`). Forgotten Creatures (All Rights Reserved -
ask Pedrijoe first): its recoloured Mushee x4, Rex Cave Blue, Slothian Kid (`research/Mods-Folder-Survey.md`); Mushee / Grooble are
vanilla models we can use without it. A pack-mod pet row names the model id; if the model is missing at startup the kind is disabled,
owned records are kept and shown "needs <mod>". Kazzy's Pets & Mounts stays off (clashes with this design).

### Engine probes (UNVERIFIED until the local session checks HytaleServer.jar / plays)

| # | Probe | What we already know |
|---|---|---|
| P1 | Look at small scales (0.2-0.35) and walk "skating" | `Model.createScaledModel(ModelAsset, float)` + `NPCPlugin.spawnEntity(store, role, pos, rot, Model, null)` VERIFIED in the jar (`research/Pets-Roster.md` 2.1); our code already calls them: `SkyyFishing/build_skyyfishing_0.1.py` line 2212 (`createScaledModel` for the bobber), `SkyyTownProbe/build_skyytownprobe_0.1.py` lines 846 / 856 (`spawnNPC`, `spawnEntity` with a Model) and 1055 (`createStaticScaledModel`) |
| P2 | Our role (Variant of a vanilla template by name) + a different Model passed at spawn shows the passed Model | Roster 2.2 says it should |
| P3 | Owner link for a non-flock follower; seek + teleport like Test_Pet | test role data only |
| P4 | Scale change at runtime (growth, baby -> adult at Lv 30) via `NPCEntity.setAppearance` or `EntityScaleComponent` | methods exist; SkyyArmory already sets `EntityScaleComponent` on projectiles (`SkyyArmory/build_skyyarmory_0.1.9.py` lines 480, 3833) |
| P5 | Spawn an NPC that is NOT saved with the chunk (or detect ours on chunk load) | unknown |
| P6 | Join the owner's flock from code; assist / defend targeting | Template_Summoned_Ally does it in data |
| P7 | Damage source of a pet hit -> credit the owner (SkyySkills kill XP, SkyyCollections, drops) | unknown |
| P8 | SkyyMobs ignores `SkyyPet_*` roles | exclude list exists (line 775) |
| P9 | Detect lethal damage and cancel it (DOWN instead of death) | unknown |
| P10 | Start a mount from code on our creature; anchor at scale; `MountedComponent` | SkyyArmory reads `MountedComponent` (`SkyyArmory/build_skyyarmory_0.1.9.py` lines 3912, 6964); starting a mount UNVERIFIED |

No existing pet or mount code in any build script (grep for `SkyyPet`, `NPCMountComponent`, `setAppearance`, `Tamework` in build
scripts: only the art tools under `tools/art/` name SkyyPet).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Pets are records in your pet list (never items you can drop or lose); eggs are items. OK? | [yes] |
| 2 | Paid revive: may a player pay coins to bring a defeated summon back early? (A defeat already costs nothing.) | [off; owners can turn it on] |
| 3 | Summon time limit: should slot 2 ever go back in by itself after a while? | [no limit (0); a row for owners] |
| 4 | Summon commands Follow / Defend / Hold as in section 3, changed on the Pets page, `/pet ...`, or by using your pet? | [yes, all three ways] |
| 5 | Show your slot-1 pet walking with you by default (players can hide it)? | [shown] |
| 6 | Pets in dungeons / instances: hidden but buffs still on? | [hidden, buffs on] |
| 7 | How many pets can one profile own? | [120, Server Setup row] |
| 8 | Pets fighting other players (PvP)? | [never; a row for owners] |
| 9 | Better Mob Expansion creatures as pets later (credit needed), and ask Pedrijoe for Forgotten Creatures recolours? | [BME yes later with credit; FC only after Pedrijoe says yes] |

## For the local session

1. Run probes P1-P10 (section 8) - P1-P5 before SkyyPets 0.2, P6-P9 before 0.4, P10 before 0.5. Skyy's creative `/npc spawn` scale test
   (`research/Pets-Roster.md` 2.3) covers P1.
2. SkyySkills: add the `pets:fn:onxp` call after every XP award (small patch, its own round or with SkyyPets 0.1).
3. SkyyGear: `gear:extra` must accept a source -> string map (gap G4, `research/Accessory-Pack-Inventory.md`) before pets publish stats.
4. SkyyMobs: confirm or add `SkyyPet_*` to its exclude list (`SkyyMobs/build_skyymobs_0.1.5.py` line 775).
5. Model ids / roles for the ~30 launch kinds: already read in `research/Pets-Roster.md`; re-check against the 0.7 Assets.zip.
6. Whether a mod asset pack may add a `Server/Models` entry with a vanilla `Parent` (chibis / anti-skating, Roster Option B).
