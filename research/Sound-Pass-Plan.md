# Sound pass plan - 2026-10-14

Which SkyWynn features are silent, and which VANILLA sound event ids fit. Ids were listed from the cached `Assets.zip` (`tools/serverjar.py` cache,
`Server/Audio/SoundEvents/**.json`, 1,569 events, read only; the id is the file name). Which mods already play a sound was found by grepping the build
scripts of the SET pins (`SFX_` ids and `SoundUtil` calls). Nothing here is built.

## 0. Short version

1. Only **6 mods play any sound of their own** today: Exploration (discovery sting, luggage), Skills (jump, crossbow load), Classes (no-ammo click), Armory (bow, dagger, spellbook,
   totem, teleport), Sacks (pickup / craft), Fishing (fish flee, water in / out). Every other mod is silent apart from the shared UI kit's button sounds.
2. **Pages are already covered**: `tools/skyyui.py` gives every button the vanilla `Sounds/Buttons*.ogg` set (light, cancel, save, main, tick, lock). No new work for page clicks.
3. The vanilla pool has **no "level up", "quest done" or "coins" sting** as such. Best fits (verified to exist): `SFX_Discovery_Z1..Z4_Short/Medium` (Exploration already uses
   them), `SFX_Event_Chapter_1_Complete_Sting`, `SFX_Memories_Unlock_Local`, `SFX_Runebinders_Lattice_Unlock_Local`, `SFX_Workbench_Upgrade_Complete_Default`, `SFX_Coffer_Goblin_Reward`,
   `SFX_Coins_Land / Hit / Break`, `SFX_Divine_Respawn`, `SFX_MemoryRestored`, `SFX_Dungeon_Checkpoint_Activate`.
4. **Cast sounds**: vanilla has `SFX_Ability_*` (Chainhook, Charged Shot, Enrage, Ground Slam, Poison Imbue, Wind Strike) and `SFX_Staff_*`, `SFX_Wand_*`, `SFX_Tornado`, which cover most
   class abilities without any custom audio.
5. Anything beyond that (a real level-up fanfare, a rebirth sting) needs custom `.ogg` assets; the repo is public, so only sounds Skyy owns or CC0 ones can be shipped. Out of scope here.

## 1. How a sound is played (copy this, it is already proven in Exploration 0.2.7)

| Need | Call | Notes |
|---|---|---|
| id -> index | `SoundEvent.getAssetMap().getIndex("SFX_...")` (class `com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent`) | check the id exists at build time (Exploration refuses ids missing from the game's asset map) |
| only the player hears it | `SoundUtil.playSoundEvent2dToPlayer(playerRef, idx, SoundCategory.UI)` (`...server.core.universe.world.SoundUtil`, `...protocol.SoundCategory`) | world thread; category UI for stings, SFX for effects |
| everyone nearby | `SoundUtil.playSoundEvent3d(idx, SoundCategory.SFX, x, y, z, componentAccessor)` | the signature is asserted in the Exploration build |
| `_Local` ids | played to the owner's client only (the player's own weapon sound) | use the plain id for 3D, the `_Local` id for 2D |

Rule: one shared helper per mod (try / catch, never throws), a Server Setup switch `sounds.<feature>` (default on), and a per-player switch in `/settings` for stings that repeat.
The kit already has per-player notification switches (`SkillStore.notifyOn`) - reuse them: a muted message class is a muted sound.

## 2. Build checklist, per mod

Legend: **P** = player only (2D, UI category), **W** = world (3D, SFX category). "Have" = already in the SET pin.

### SkyySkills 0.4.35 (have: jump, crossbow load)

| Feature | Sound (vanilla id) | Mode | Priority |
|---|---|---|---|
| Skill level up (gold chat line) | `SFX_Workbench_Upgrade_Complete_Default` (short, positive) | P | HIGH |
| Overall level up | `SFX_Memories_Unlock_Local` | P | MED |
| Level-up coins paid | `SFX_Coins_Land` (very short) played after the level sting only if coins > 0 | P | LOW |
| Perfect roll / dodge | `SFX_Player_Roll` is vanilla already; nothing to add | - | - |
| Tree felled bonus, double drop | `SFX_Crops_Grow_Stage_Complete` (soft pop) behind `skills.doubleDrop` | P | LOW |

### SkyyClasses 0.1.21 + SkyyArmory 0.1.23 + SkyyTrees 0.3.6 (have: no-ammo click, bow, dagger, spellbook charge, totem, teleport)

| Feature | Sound (vanilla id) | Mode | Priority |
|---|---|---|---|
| Ability cast (generic confirm) | `SFX_Ability_Wind_Strike_Imbue` / `_Local` | P (+ W copy) | HIGH |
| Warrior / Berserker rage ability | `SFX_Ability_Enrage` / `_Local` | W | HIGH |
| Ground slam / shockwave abilities | `SFX_Ability_Ground_Slam_Impact`, `_Wave`, `_Spike_Erupt` | W | HIGH |
| Archer charged / power shot | `SFX_Ability_Charged_Shot_Charge_Local`, `_Launch_Local`, `_Impact` | P + W | HIGH |
| Assassin poison / imbue | `SFX_Ability_Poison_Imbue` / `_Local` | P | MED |
| Grapple / hook | `SFX_Ability_Chainhook_Shot_Local`, `_Hit`; `SFX_Tool_Hookshot_Reel_Local` | P + W | MED |
| Mage wand shot | have `SFX_Wand_Ice_Shoot`; add `SFX_Wand_Fire_Shoot` for a fire variant | W | MED |
| Mage staff / blink | `SFX_Staff_Ice_Shoot`, `SFX_Staff_Fire_Shoot`; blink = `SFX_Portal_Neutral_Teleport_Local` (have) | W | MED |
| Priest heal / aura | `SFX_Deployable_Totem_Heal_Spawn` (have), `SFX_Divine_Respawn` for a big heal | W | MED |
| Monk gauntlet burst | `SFX_Tornado` | W | LOW |
| Ability on cooldown / no Mana | `SFX_Generic_Crafting_Failed` (short fail), `SFX_Incorrect_Tool` | P | HIGH (feedback) |
| Class tree node bought | `SFX_Runebinders_Lattice_Unlock_Local` | P | MED |
| Class chosen | `SFX_Memories_Unlock_Local` | P | LOW |

### SkyyHud 0.3.22 (feed cards, widgets) - silent

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Feed card appears (reward, quest done) | `SFX_Discovery_Z1_Short` only for quest done and rewards; NOT for XP / chat noise (the feed is meant to be quiet) | P | MED, default OFF per card class |
| Party invite card | `SFX_Mug_Fill_Local` or `SFX_Drag_Items_Paper` (soft) | P | LOW |
| Warning (low Mana, low durability) | `SFX_Item_Break` is too harsh - use `SFX_Generic_Crafting_Failed` | P | LOW |

### SkyyQuests 0.2 - silent

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Task done | `SFX_Dungeon_Checkpoint_Activate` | P | HIGH |
| Quest line / tutorial finished | `SFX_Event_Chapter_1_Complete_Sting` | P | HIGH |
| Reward claimed (`/quests claim`) | `SFX_Coins_Land` + `SFX_Chest_Wooden_Open_Player` | P | MED |
| Quest skipped / abandoned | `SFX_Drop_Items_Paper` | P | LOW |

### SkyyCollections 0.2.12 - silent

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Collection tier reached | `SFX_Memories_Unlock_Local` | P | HIGH |
| Recipe unlocked | `SFX_Runebinders_Lattice_Unlock_Local` | P | MED |
| Max tier | `SFX_Event_Chapter_1_Complete_Sting` | P | LOW |

### SkyyBank 0.1.10 / SkyyBazaar 0.1.10 / SkyyAuctions 0.1.4 / SkyyCoins 0.1.6 / SkyyMerchants 0.1.3 - silent

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Bank deposit / withdraw | `SFX_Coins_Land` (small), `SFX_Coins_Hit` | P | MED |
| Bank interest paid (daily line) | `SFX_Coffer_Goblin_Reward` | P | LOW |
| Bazaar buy / sell | `SFX_Coins_Land`; big sell (above a Server Setup limit) `SFX_Coffer_Goblin_Reward` | P | MED |
| AH listed / sold / claimed | listed `SFX_Drop_Items_Paper`, sold `SFX_Coins_Land`, claim `SFX_Chest_Wooden_Open_Player` | P | MED |
| Death coin loss | `SFX_Coins_Break` | P | LOW |
| Merchant appears near you | `SFX_Discovery_Z1_Short` once per visit | P | LOW |
| Merchant buy | `SFX_Coins_Land` | P | MED |
| Merchant rumour in chat | none (chat only) | - | - |

### SkyyGear 0.3.3 / SkyySacks 0.8.4 / SkyyAccessories 0.5.13 / SkyyVault 0.1.5 / SkyyWardrobe 0.2.1

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Identify gear | `SFX_Chest_Legendary_FirstOpen_Player` (big) for rare+, `SFX_Chest_Wooden_Open_Player` below | P | HIGH (feeds the planned identify animation) |
| Reforge | `SFX_Weapon_Bench_Craft` / `SFX_Armour_Bench_Craft` by item kind | P | MED |
| Reforge / level up failed | `SFX_Generic_Crafting_Failed` | P | MED |
| Tool tier gate refuse | `SFX_Incorrect_Tool` (vanilla, may already play) | P | LOW |
| Bag craft / open page | have `SFX_Player_Craft_Item_Inventory`, `SFX_Player_Pickup_Item` | - | done |
| Accessory equip / slot unlock | `SFX_Drag_Items_Gems` (equip), `SFX_Runebinders_Lattice_Unlock_Local` (slot) | P | LOW |
| Vault page bought | `SFX_Chest_Wooden_Open_Player` | P | LOW |
| Wardrobe loadout swap | `SFX_Drag_Armor_Cloth` / `SFX_Drag_Armor_Heavy` by armour type | P | LOW |

### SkyyPets 0.2.4

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Pet summon / dismiss | `SFX_Deployable_Totem_Heal_Spawn` / `_Despawn` | W | MED |
| Pet level / new pet | `SFX_Memories_Unlock_Local` | P | LOW |
| Pet buff proc | none | - | - |

### SkyyRebirth 0.1 (R3+ not built) and SkyyProfiles / SkyyIslands

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Rebirth confirm (before reset) | `SFX_Portal_Void` or `SFX_Void_Encroaching` (dark, fits "Void-Touched") | P | HIGH |
| Rebirth done | `SFX_Divine_Respawn` | P + W | HIGH |
| Rebirth title / cosmetic every 3rd | `SFX_Event_Chapter_1_Complete_Sting` | P | MED |
| Profile switch | `SFX_Portal_Neutral_Open` | P | LOW |
| Island enter / hub teleport | `SFX_Portal_Neutral_Teleport_Local` | P | MED |
| New zone entered | Exploration already plays `SFX_Discovery_Z*_*`; Mobs zone banners could reuse them | P | LOW |

### Shards and totems (Gathering-Shards-Spec phases 4-8, not built)

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Place a shard / portal activates | `SFX_Portal_Neutral_Open`, `SFX_Gem_Emit_Loop` (ambient loop, check volume) | W | MED |
| Collect from shard | `SFX_Crystal_Hit`, `SFX_Coins_Land` | P | MED |
| Shard upgrade / totem upgrade | `SFX_Workbench_Upgrade_Complete_Default` | P + W | MED |
| Totem tick (harvest spirit works) | `SFX_Crops_Grow_Stage_Complete` (rare, rate limited) | W | LOW |
| Totem placed / picked up | `SFX_Deployable_Totem_Heal_Spawn` / `_Despawn` | W | LOW |
| Auto-compactor, time compressor | `SFX_Furnace_Bench_Processing_Complete` | W | LOW |

### Mobs 0.1.8, World, events

| Feature | Sound | Mode | Priority |
|---|---|---|---|
| Elite / mini boss spawn | `SFX_Gobliterator_Arena_Horn` (goblin themed, use only in goblin zones) or `SFX_Void_Eviction` | W | MED |
| Lost Loot pile / airdrop lands | `SFX_Chest_Legendary_Loop` (loop while unopened, short) + `SFX_Stone_Coffin_Open_Close` on open | W | MED |
| Identify animation | `SFX_Chest_Legendary_FirstOpen_Player` then `SFX_Coffer_Goblin_Reward` | P | HIGH |

## 3. Rules for the build round

| Rule | Why |
|---|---|
| One helper `Snd.play(pr, id, mode)` per mod, copy of the Exploration pattern (id checked at build time, try / catch, world thread) | no mod can crash on a missing sound |
| Server Setup row `sounds.enabled` per mod (default on) + per-player `/settings` switch for repeating ones | Skyy's rule: everything editable in game; some players hate repeated stings |
| Rate limit: at most 1 sting per player per 0.5 s, never in a loop | level-up bursts (rebirth pays many levels) would stack |
| Never play a 3D sound inside a tick loop | tick cost; stings only on events |
| Volumes: only the engine's own sound config is used (we cannot change volume of a vanilla event) | custom volume needs our own sound event assets (not allowed in a UI-less build without an asset pack) |
| Test: a `/soundtest <id>` admin command that plays any id (also useful for Skyy to audition) | Skyy can pick by ear; one tiny command in SkyyEssentials or SkyyMenu admin page |

## 4. Suggested build order (one lean round per group)

| Round | Mods | Items |
|---|---|---|
| S1 | SkyySkills, SkyyCollections, SkyyQuests | level up, tier, task done, quest done (the most heard sounds) |
| S2 | SkyyClasses, SkyyArmory | ability casts, cooldown / no Mana fail |
| S3 | SkyyBank, SkyyBazaar, SkyyAuctions, SkyyMerchants, SkyyGear | coins, identify, reforge |
| S4 | SkyyRebirth (with R3), SkyyPets, shards (with their phases) | built inside those rounds, not separately |

## UNVERIFIED

| # | Item |
|---|---|
| 1 | Every id above exists in the cached 0.7.1 `Assets.zip` (they were taken from the file list); whether each one SOUNDS right can only be heard in game. `/soundtest` solves that. |
| 2 | That `_Local` variants only reach the owner (name pattern, same as the vanilla weapon files). |
| 3 | Which of the existing silent mods already play a vanilla sound through the engine itself (item pickup, bench craft, chest open do) - those must not be doubled. |
| 4 | Whether the client mixes `SoundCategory.UI` at the same volume as the vanilla stings. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Build a `/soundtest <id>` admin command first so you can audition ids by ear before the sounds are wired in? | [yes, in the SkyyMenu admin page] |
| 2 | Should quiet things (feed cards, XP gains, double drops) stay silent, with sounds only on level ups, quest done, rewards and casts? | [yes] |
| 3 | A real custom level-up / rebirth fanfare needs audio files we own or CC0 ones: want that later, or vanilla-only for release? | [vanilla-only for release] |
| 4 | Ability casts: each class gets its own vanilla sound (table above), or one shared cast sound for all? | [own per ability where a vanilla one fits, shared fallback] |
