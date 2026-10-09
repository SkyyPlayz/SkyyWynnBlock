# Skyy's Mods folder survey (2026-10-09)

Skyy: "check my mods folder for more mods that will help our pack." 286 entries, 251 manifests read; only our jars + the pack mods are
enabled in the HUD mod world. ~60% of the folder is capped below Hytale 0.7 ("<0.7.0" / "^0.6.x"). All Rights Reserved = ask before
listing in PACK.md; never copy files, runtime ids only.

## Top picks (A)
| # | Mod | Author | Adds / gap | Licence | 0.7 |
|---|---|---|---|---|---|
| 1 | Lootr 0.3.12 | Noobanidus | per-player loot chests (no looting races) - fits UT "chest loot" + luggage | MIT | ok |
| 2 | Dragon Nestkeeper (+ Rare Monsters, Paintings, Farm Decor) | BlackAures | raise dragons (Zone 5 dragons / pet question), rare mob variants, decor | ARR but "made for use in any modpacks" | ok |
| 3 | YUNG's HyDungeons 0.1.1 | YUNGNICKYOUNG | procedural instanced dungeons, no vanilla overrides | ARR, ask | ok |
| 4 | Tower of Shiva 1.5.1 | Adathan | boss dungeon (overrides worldgen Settings.json - check vs SkyyWorldGen) | ARR, ask (with the Adathan message) | ok |
| 5 | Macaw's Hy Carpets / Lights / Paths / Stairs | SketchMacaw | town decor, no overrides | not checked | ok |
| 6 | UltimateBossFight 1.0.5 | HytaleZX | boss NPCs | ARR, ask | EXCLUDES 0.7 |
| 7 | NoCube Undead Warriors 0.1.0 | NoCube | random skeleton warriors (overrides a Zone 1 spawn file) | like Orchard: packs ok, no paid packs | pinned build |
| 8 | MajorDungeons 0.4.13 | MAJOR76 | dungeons, mounts, merchant (own currency clashes) | not found | EXCLUDES 0.7 |
| 9 | Kazzy's Pets & Mounts 2.0.5 | Kazopalooza | 100+ pets / mounts (clashes with our pet design) | ARR, ask | ok |
| 10 | WansWonderWeapon 1.1.0 | wanmine | ability weapons | not found | EXCLUDES 0.7 |

## Maybe (B)
Forgotten Creatures (PedriJoe; vanilla hidden creatures, overrides 21 vanilla drop files, 0.6.0 pin), SlimeMobs, Kami OreGolems,
mounts (Ancient Riders, More Mounts camels, TravelingMounts), Spark Lantern Pets / FPets (cosmetic floating pets), Voidcloak Armory,
SimpleEnchantments, Fullmetal Labyrinth, Skyreach Ravines, Mort's Wandering Merchant, InvasionX / Mob Events / Blood Moon, QoL (Ping,
AutoSort, CarryChest, ItemMagnet, Spyglass, TreeHarvester), ConnectedWindows, Diagonal Fences, Brighter Torches.

## Clash with our mods (C) - keep off
Levelling / skills / classes (EndlessLeveling, RPGLeveling, MMOSkillTree, PJ-HySkills...), mob scaling (MmoMobScaling, PJ-Difficulty,
EndlessEliteMobs), movement (Zephyr, dodges, BetterMovement, grapple / jetpack / glider), magic weapons (Arcane Power, Robes & Spells),
storage / stacks / backpacks, other maps / HUDs, farming overhauls, durability / repair mods, HyperEssentials / Essentials / boards.

## Forgotten Creatures 1.3.1 (Pedrijoe) - Skyy: "this one looks cool too"
- LICENCE: All Rights Reserved, no modpack line -> ask Pedrijoe. ServerVersion "0.6.0" exact (0.7 risk). Disabled in the HUD mod world.
- Enables hidden vanilla-model creatures (recoloured textures): Zone 1 Mushee x4 (38 HP), Bramblekin Shaman (150) + Bramblekin armor;
  swamps Ghoul (250), Zombie Aberrant (400), Golden Reptil Trork; Zone 2 seven Slothians (80-220, made hostile); Zone 3 Blue Shadow
  Knight (750), Grooble + Mannequin (passive); Zone 4 Saurians (250), Rex Cave Blue (400), Golden / Red / Purple Shadow Knights (750),
  Magma / Red Ghouls; Void Necromancers (200).
- Patches 21 vanilla files incl. the Zone 1-4 predator spawn files - the SAME files Better Mob Expansion edits (last loaded wins): test
  them together. Mob Events (in the folder) needs Champions / PJ-Money / PJ-HySkills (missing) - skip.
- FIT: great zone variety (Shadow Knights / Saurians = elites / mini-bosses); PET candidates with vanilla models: Mushee x4 (colour =
  rarity skins), Grooble, Mannequin, Slothian Kid, Rex Cave Blue chibi, Golden Reptil Trork.

## Arcane Power 3.1.1 (Tayko_Dev) - Skyy: "this one looks reallyyy cool! it would help flesh out some of the classes missed by armory."
- LICENCE: All Rights Reserved, no modpack text -> ask Tayko (draft in research/Author-Requests.md). ServerVersion <0.7.0 (needs a 0.7
  update). JSON only; optional Hytalor / Patchly drop patches (skeleton mages, Goblin Duke, Zone 1-4 chests). Disabled in the HUD mod world.
- Items (ArcanePower_*): 9 spellbooks (Ember, Gust, Spark, LifeVeil heal, Shock, Zephyr, Blossomwind, CosmicRuin, Infernal; Rare/Epic
  L40-50), 3 upgrade-chain maces (Event Horizon L50 -> Pulsar Breaker L60 -> Quasar Reaver L80), 2 bows (Stellar Piercer, Nebula Flurry,
  Epic L50), Void Maw mana launcher, 14 Cloth armor pieces (Manathread L30 / Arcaneweave L40 sets), 5 ingredients, Runecrafter's Table;
  mobs Cosmic Eye + 3 Skeleton Wraiths (Fire / Cosmic never spawn - their bug).
- CLASS FIT (Skyy 2026-10-09): maces -> BERSERKER special drops (he already owns maces); LifeVeil healing spellbook -> MAGE UNTIERED
  (healing the Mage lacks); other spellbooks + Void Maw -> Mage; bows -> Archer specials; armor -> Mage / Priest Cloth ladder. SkyyGear must list the ArcanePower_ ids (not Armor_/Weapon_).
- RISKS: flat Mana costs 15-75 and +50..+100 max Mana while held (would triple a Mage pool) -> runtime clamp in our code; Ability1 on
  maces / bows / Infernal clashes with our Q signature; nothing uses Ability2.

## Bio's Kobolds 1.3.2 (Bio_the_LizardWizard) - Skyy: wandering traders / special shops
- LICENCE: CC BY 4.0 (credit + licence link + say what we changed; reuse allowed). ServerVersion pinned to build 2026.03.26 (0.7 check).
  No hard dependencies (Wardrobe / OrbisOrigins optional, not installed). Disabled in the HUD mod world. No vanilla overrides found.
- Zone 1 plains caravans (leader + guard + Treasurer + Artificer merchant + Cargo Drake) using the VANILLA barter shop (gold / treasure
  economy; sells kobold spear, emerald flail, a Cargo Drake crate -> mountable Tamed_Drake_Cargo for 27 gold bars worth). Hostile Kobold
  Marauders + Elites in Zones 1-4, a Marauder boss model. Caravans only wander near their leader - no zone routes.
- PLAN for Skyy's "special shops that move around each zone": build OUR OWN roaming merchants (code-spawned NPC on a vanilla template, a
  mover that relocates it every N minutes per zone, UseEntityEvent opens our shop page: pet eggs + special weapons, never UT / Mythic,
  SkyyCoins prices) - research/Server-Setup-Research.md already recommends spawnNPC + UseEntityEvent. Kobold models / drake mount =
  optional later by role id (CC BY, credit).

## Spawn Manager + [Assets] (ReignInBlood) - Skyy: "these two spawn manger mods might help later"
- MIT (keep the notice). A world-wide on/off switch per mob (operator UI, restart needed) that patches copies of the vanilla spawn files;
  no per-zone control, no boss spawners / timers, no NPC spawning, no API; 124 MB jar with bundled server classes; Assets overlaps
  Forgotten Creatures' spawn files. VERDICT: skip - our own spawn files (SkyyWorldGen) + code-spawned NPCs cover these needs.
