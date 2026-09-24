# SkyyGear - plan
*Design lock 2026-09-24 (Skyy). Nothing here is built. Change note: `SkyWynn-Decisions.md`. Code follow-ups: `HANDOFF.md`, `DESIGN-STATUS.md`.*

Skyy's direction still holds: every mod in the pack is eventually our own. Combat armor and weapons copy Wynncraft. Gathering gear is SkyBlock-style. We rebuild features ourselves. Never copy another author's files (items, models, textures, code) unless their license allows it.

## Locked (2026-09-24)

1. **Level + rarity, Wynn-style.** Every gear item has a level requirement and a rarity tier. The exact rarity names and colours are not locked (open questions). Which level type the requirement uses (skill vs class vs combat) is still the earlier same-day question; this lock only says every gear item has one.
2. **Smithing rarity.** A higher Smithing level raises a **smithing rarity** stat. That stat increases the chance of crafting a higher-rarity item. Smelting still pays Smithing XP (the existing SkyySkills lock). SkyySkills 0.4 does not have this stat.
3. **Rarity sets reforge quality.** The higher an item's rarity, the better the rolls a reforge can give: a wider and higher roll range. A reforge still swaps the bonuses (batch 2). How you obtain and apply a reforge is still open.
4. **Unidentified drops, Wynn-style.** Mobs drop unidentified weapons and armor. Identifying one reveals its rolled IDs. Where that happens, how, and what it costs are open. SkyyRolls 0.1.3 shows rolls on the item immediately; that is the jar, not this rule.
5. **Combat armor and weapons** basically copy Wynncraft. Class weapons stay the ones already named in `SkyyClasses-Plan.md`. Berserker is still PENDING and has no weapon list.
6. **Gathering gear** is SkyBlock-style: farming armor sets and foraging armor sets. Mining armor is likely the same kind of set. This note does not name the pieces.
7. **Wardrobe + loadouts**, Hypixel SkyBlock style: save a gear set and quick-swap to it. **UI:** placeholders are fine. Nothing on the inventory screen yet (`SkyWynn-Decisions.md` 10.22). What a loadout saves is open.

## What it covers
| Line | Style | Locked shape |
|---|---|---|
| Combat weapons and armor | Wynncraft | Copy Wynn's model. Class weapons: Archer shortbow/crossbow, Warrior sword/longsword/spear, Mage staff; later Assassin daggers/kunai; Shaman TBD; Berserker PENDING with no list. Every piece has a level requirement and a rarity. Mobs drop them unidentified. Rolled IDs show after identify. Powders and Wynn's five elements stay (batch 2); powder slot counts are open |
| Gathering armor | Hypixel SkyBlock | Farming sets and foraging sets. Mining sets are likely the same idea. Proposed stats (not locked): fortune, speed |
| Tools | Hypixel SkyBlock | Pickaxes, axes, hoes (rods later). Reforges, and tiers tied to the zone islands, are still to design. They are gear, so they carry a level requirement and a rarity |

## Built foundations we reuse
- **SkyyRolls** (0.1.3): rolled stats stored on the item and shown on its tooltip (reforge name in the rarity colour, one line per stat). This is the ID / reforge foundation. It does not do unidentified drops, smithing rarity, or a rarity-based roll range.
- **SkyyClasses**: weapon ownership by item-id prefix, so our own weapons slot in by name.
- **SkyySkills Smithing**: smelting pays XP now. Reforging and powders are still the planned later XP sources. Smithing rarity is a new effect of the level, not a new XP source.
- **SkyyTrees / SkyySkills perks**: tool bonuses can feed the same gathering hooks (breaking speed, double drops, fortune).
- **SkyySacks /craft Smithing tab**: tools, weapons and armor already have their own crafting tab.
- **SkyyCollections**: gear recipes can be unlocked by collection tiers (the Copper Pickaxe recipe at Cobblestone I is the pattern).

## Third-party stopgaps to replace
| Stopgap | Replace with |
|---|---|
| More Crossbow Tiers (Serj) | our own crossbow line (own item ids, stats, recipes) |
| Saplings From Trees (Helios) | our own leaf drops + sapling recipes (or keep until the Foraging rework) |

## Proposed, not locked
Awaiting owner confirm. Do not build from this paragraph.

- Combat gear uses Wynn's five skill points (Strength, Dexterity, Intelligence, Defence, Agility).
- Gathering sets use SkyBlock stats (fortune, speed).

## Open questions
1. **Level type.** Every gear item has a level requirement. Which number gates it: skill, class, or combat level?
2. **Rarity list and colours.** Wynn uses Normal / Unique / Rare / Legendary / Fabled / Mythic / Set. SkyyRolls today uses Common through Legendary. The old draft of a 7-tier Common→Divine ladder is not the lock.
3. **Top rarities.** Can mob drops reach the top tiers, or are some tiers craft-only?
4. **Identification.** Where it happens, how the player does it, and what it costs.
5. **Reforge obtain.** A bench, reforge stones, or something else, and the cost. The roll-range rule above is locked either way.
6. **Powders.** Wynn's five elements and "powders replace SkyBlock runes" stay locked. Still open: slots per item, tiers, and how they drop.
7. **Loadout contents.** Armor only, or also weapons, accessories, and HUD?
8. **Where rolled items sell.** Bazaar (stackable commodities today) or the auction house. Separate from that: the late-game wall still pulls some items off both buy and sell (Decisions 1.2). Which gear that hits is open.
9. **Zone pacing.** How gear steps up across the island chain. Not numbered here.
