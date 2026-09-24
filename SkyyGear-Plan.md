# SkyyGear - plan (draft, 2026-09-24)
*Skyy's direction: every mod in the pack is eventually our own. With Wynncraft-style weapons and SkyBlock-style tools we will make a lot of
our own custom tools, weapons and armor. Nothing here is built yet - this is the starting point for design sessions.*

## Goal
Our own gear line that replaces third-party item mods and carries SkyWynn's core item rules (design lock batch 2):
- **IDs + reforges are core.** Every item has a rarity and stats. A reforge swaps the bonuses.
- **Wynn's five elements + powders.** Powders replace SkyBlock runes. This is gear, not the (still open) magic system.

## What it covers
| Line | Style | Ideas to design |
|---|---|---|
| Weapons | Wynncraft | Class weapons (Archer: shortbow, crossbow; Warrior: sword, longsword, spear; Mage: staff; later Assassin daggers/kunai, Shaman TBD), rolled IDs (damage, strength, crit, element damage), powder slots, rarity tiers, level / skill requirements |
| Tools | Hypixel SkyBlock | Pickaxes, axes, hoes (and later rods) with mining/foraging/farming speed and fortune, reforges, tool tiers tied to the zone islands |
| Armor | Both | Sets with stats, rarity, reforges, element defence; set bonuses later |

## Built foundations we reuse
- **SkyyRolls** (0.1.3): rolled stats stored on the item + shown on the item's own tooltip through the engine's native ItemDisplay metadata
  (reforge name in the rarity colour, one line per stat). This becomes the ID / reforge system of the gear line.
- **SkyyClasses**: weapon ownership by item-id prefix (e.g. every `Weapon_Crossbow_*` is an Archer weapon), so our own weapons slot in by name.
- **SkyySkills Smithing**: reforging and adding powders are Smithing's planned XP sources (smelting already pays).
- **SkyyTrees / SkyySkills perks**: tool bonuses can feed the same gathering hooks (breaking speed, double drops, fortune).
- **SkyySacks /craft Smithing tab**: tools, weapons and armor already have their own crafting tab.
- **SkyyCollections**: gear recipes can be unlocked by collection tiers (e.g. the Copper Pickaxe recipe at Cobblestone I).

## Third-party stopgaps to replace
| Stopgap | Replace with |
|---|---|
| More Crossbow Tiers (Serj) | our own crossbow line (own item ids, stats, recipes) |
| Saplings From Trees (Helios) | our own leaf drops + sapling recipes (or keep until the Foraging rework) |

**Rule:** rebuild each feature ourselves - our own item definitions, stats, recipes and (later) art. Never copy another author's files
(items, models, textures, code) into our mods unless their license allows it; check each mod's license before reusing anything.

## Open design questions
1. Which stats exist (Wynn-style: strength / dexterity / intelligence / defence / agility? SkyBlock-style: strength, crit chance, crit damage,
   speed, fortune?), and how they apply in Hytale combat.
2. Rarity tiers and their colours (SkyyRolls today: Common to Legendary).
3. How reforges are obtained and applied (a reforge bench? reforge stones from Mining/Combat?), and their cost.
4. Powders: elements, tiers, how many slots per item, how they drop.
5. Gear progression per zone island, and level / skill requirements.
6. Whether rolled items can be sold on the bazaar (stackable items only today) or need an auction house.
