# SkyyGear - plan
*Design lock 2026-09-24 (Skyy). Nothing here is built. Change note: `SkyWynn-Decisions.md`. Code follow-ups: `HANDOFF.md`, `DESIGN-STATUS.md`.*

Skyy's direction still holds: every mod in the pack is eventually our own. Combat armor and weapons copy Wynncraft. Gathering gear is SkyBlock-style. We rebuild features ourselves. Never copy another author's files (items, models, textures, code) unless their license allows it.

## Locked (2026-09-24)

1. **Level + rarity, Wynn-style.** Every gear item has a level requirement and a rarity tier. The exact rarity names and colours are not locked (open questions). Which level type the requirement uses (skill vs class vs combat) is still the earlier same-day question; this lock only says every gear item has one.
2. **Smithing rarity.** A higher Smithing level raises a **smithing rarity** stat. That stat increases the chance of crafting a higher-rarity item. Smelting still pays Smithing XP (the existing SkyySkills lock). SkyySkills 0.4 does not have this stat.
3. **Rarity sets reforge quality.** The higher an item's rarity, the better the rolls a reforge can give: a wider and higher roll range. A reforge still swaps the bonuses (batch 2). How you obtain and apply a reforge is still open.
4. **Unidentified drops, Wynn-style.** Mobs drop unidentified weapons and armor. Identifying one reveals its rolled IDs. How the player identifies is lock 9. SkyyRolls 0.1.3 shows rolls on the item immediately; that is the jar, not this rule.
5. **Combat armor and weapons** basically copy Wynncraft. Class weapons stay the ones already named in `SkyyClasses-Plan.md`. Berserker is still PENDING and has no weapon list.
6. **Gathering gear** is SkyBlock-style: farming armor sets and foraging armor sets. Mining armor is likely the same kind of set. This note does not name the pieces.
7. **Wardrobe + loadouts**, Hypixel SkyBlock style: save a gear set and quick-swap to it. **UI:** placeholders are fine. Nothing on the inventory screen yet (`SkyWynn-Decisions.md` 10.22). What a loadout saves is lock 12.
8. **Stat mix.** Weapons and armor carry Wynn's five skill points — Strength, Dexterity, Intelligence, Defence, Agility — with SkyBlock-style stats layered on top. Crit chance, crit damage, and fortune are in that layer. The exact list beyond these, and how each one applies in Hytale combat, stay open. This replaces the earlier same-day proposal that split Wynn skill points onto combat gear and fortune/speed onto gathering sets.
9. **Identification.** For now, a menu opened with `/identify`. Later `/identify` is disabled and identification moves to an NPC, Wynncraft-style. Identifying costs coins. The cost scales with the item's rarity and level. The cost formula is open. The menu is one of our pages (placeholders are fine). It does not go on the inventory screen (10.22). SkyyRolls 0.1.3 has no identify step.
10. **Drops and sets.** Mob drops can be any rarity. Some sets are drop-only. Some sets are craft-only. That closes the older question about craft-only tiers.
11. **Set bonuses.** Sets have a bonus for wearing the set, in the vein of Wynncraft set bonuses and Hypixel's Full Set Bonus. Which sets, and the bonus numbers, are not named here.
12. **Loadout contents.** A loadout saves armor, the Equipment bar (lock 13), and the selected Accessory Power buff (lock 14). Pets are saved too, once pets exist. Placeholders stay off the inventory screen.
13. **Equipment bar.** A separate bar next to armor, SkyBlock's Equipment layout: necklace, cloak, ring, and belt. Working name **Equipment**. Skyy was not sure of the name; it is not final. Same UI rule as the wardrobe: placeholders on our pages, nothing on the inventory screen yet. This bar is not the accessory bag (`SkyyAccessories-Plan.md`).
14. **Accessory Power.** Like Hypixel Magical Power plus a selectable Power. Each accessory gives its own buff and also adds accessory power. Total power feeds one selectable buff. More power means a stronger buff. Several buffs to pick from. Locked examples: **Warrior** (strength as a damage modifier, plus a small amount of crit chance, crit damage, health, and defence) and **Elementalist** (boosts all elemental damage types and gives all elemental resistance). More options are TBD. The full list and the numbers are open. The crystal table and the curve in `SkyyAccessories-Plan.md` are the older draft, not this lock. The selected buff is what a loadout saves (lock 12).

## What it covers
| Line | Style | Locked shape |
|---|---|---|
| Combat weapons and armor | Wynncraft | Copy Wynn's model. Class weapons: Archer shortbow/crossbow, Warrior sword/longsword/spear, Mage staff; later Assassin daggers/kunai; Shaman TBD; Berserker PENDING with no list. Every piece has a level requirement and a rarity. Mobs can drop any rarity. Rolled IDs show after identify (lock 9). Stats are the mix in lock 8. Sets can be drop-only or craft-only, and a worn set has a set bonus (locks 10–11). Powders and Wynn's five elements stay (batch 2); powder slot counts are open |
| Gathering armor | Hypixel SkyBlock | Farming sets and foraging sets. Mining sets are likely the same idea. They are armor, so they use the same stat mix (lock 8). A worn set has a set bonus |
| Equipment | Hypixel SkyBlock | Separate bar next to armor. Slots: necklace, cloak, ring, belt. Working name Equipment (not final). Saved in a loadout |
| Tools | Hypixel SkyBlock | Pickaxes, axes, hoes (rods later). Reforges, and tiers tied to the zone islands, are still to design. They are gear, so they carry a level requirement and a rarity |

## Built foundations we reuse
- **SkyyRolls** (0.1.3): rolled stats stored on the item and shown on its tooltip (reforge name in the rarity colour, one line per stat). This is the ID / reforge foundation. It does not do unidentified drops, smithing rarity, a rarity-based roll range, or the stat mix.
- **SkyyClasses**: weapon ownership by item-id prefix, so our own weapons slot in by name.
- **SkyySkills Smithing**: smelting pays XP now. Reforging and powders are still the planned later XP sources. Smithing rarity is a new effect of the level, not a new XP source.
- **SkyyTrees / SkyySkills perks**: tool bonuses can feed the same gathering hooks (breaking speed, double drops, fortune).
- **SkyySacks /craft Smithing tab**: tools, weapons and armor already have their own crafting tab.
- **SkyyCollections**: gear recipes can be unlocked by collection tiers (the Copper Pickaxe recipe at Cobblestone I is the pattern). Craft-only sets use that path. Drop-only sets do not.
- **SkyyAccessories**: the bag and per-item talisman bonuses exist in the jar. The selectable Accessory Power buff (lock 14) and saving it in a loadout do not. Detail and the still-draft numbers live in `SkyyAccessories-Plan.md`.

## Third-party stopgaps to replace
| Stopgap | Replace with |
|---|---|
| More Crossbow Tiers (Serj) | our own crossbow line (own item ids, stats, recipes) |
| Saplings From Trees (Helios) | our own leaf drops + sapling recipes (or keep until the Foraging rework) |

## Open questions
1. **Level type.** Every gear item has a level requirement. Which number gates it: skill, class, or combat level? Identify cost scales with rarity and level; that does not pick the type.
2. **Rarity list and colours.** Wynn uses Normal / Unique / Rare / Legendary / Fabled / Mythic / Set. SkyyRolls today uses Common through Legendary. The old draft of a 7-tier Common→Divine ladder is not the lock.
3. **Equipment name.** Working name is Equipment. The final name is open.
4. **Identify cost formula.** Coins, scaling with rarity and level, is locked. The formula is open.
5. **Reforge obtain.** A bench, reforge stones, or something else, and the cost. The roll-range rule above is locked either way.
6. **Powders.** Wynn's five elements and "powders replace SkyBlock runes" stay locked. Still open: slots per item, tiers, and how they drop.
7. **Where rolled items sell.** Bazaar (stackable commodities today) or the auction house. Separate from that: the late-game wall still pulls some items off both buy and sell (Decisions 1.2). Which gear that hits is open.
8. **Zone pacing.** How gear steps up across the island chain. Not numbered here.
9. **Stat list and combat application.** The mix is locked (five skill points, plus crit chance, crit damage, and fortune). The full menu is `SkyyGear-Stat-Catalog.md` (decision column blank): SkyBlock gear stats, Wynn skill points, elemental damage and defence, every combat identification, and every Major ID. Anything past the locked mix is still open until Skyy marks that sheet. How each stat applies in Hytale combat is open. Do not invent formulas or extra stats from this plan.
10. **Accessory Power list and numbers.** Warrior and Elementalist are locked examples. The rest of the buff list, and every number, stay open. The Hypixel power menu (every selectable power, enrichments, and tuning) is in that same catalog, decision column blank. It is research. Do not treat the crystal table in `SkyyAccessories-Plan.md` as the lock.
