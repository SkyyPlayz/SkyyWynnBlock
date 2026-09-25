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
8. **Stat mix (revised later the same day).** This note put Wynn's five skill points on weapons and armor, with crit chance, crit damage, and fortune layered on. **Change note 9 replaces the five skill points.** Strength is SkyBlock-style. Dexterity, Wynn Defence, Wynn Intelligence, and Wynn Agility are not gear skill points. Crit chance and crit damage stay, with the rules in locks 15 and up. **Gathering fortunes were locked later (change note 11).** Mining Fortune, Farming Fortune, and Foraging Fortune are in. One stat each. Loot and luck was finished later (change notes 12 and 13). XP and wisdom was locked later (change note 14). The Other table was scrapped later as gear IDs (change note 15). Oxygen and water swim speed are accessory effects (change note 16). Accessory progression and enrichments were locked later (change notes 17–18). Starter powers lean Keep, pending confirm (change note 19). Next blank table is the rest of SkyBlock accessory powers.
9. **Identification.** For now, a menu opened with `/identify`. Later `/identify` is disabled and identification moves to an NPC, Wynncraft-style. Identifying costs coins. The cost scales with the item's rarity and level. The cost formula is open. The menu is one of our pages (placeholders are fine). It does not go on the inventory screen (10.22). SkyyRolls 0.1.3 has no identify step.
10. **Drops and sets.** Mob drops can be any rarity. Some sets are drop-only. Some sets are craft-only. That closes the older question about craft-only tiers.
11. **Set bonuses.** Sets have a bonus for wearing the set, in the vein of Wynncraft set bonuses and Hypixel's Full Set Bonus. Which sets, and the bonus numbers, are not named here.
12. **Loadout contents.** A loadout saves armor, the Equipment bar (lock 13), and the selected Accessory Power buff (lock 14). Pets are saved too, once pets exist. Placeholders stay off the inventory screen.
13. **Equipment bar.** A separate bar next to armor, SkyBlock's Equipment layout: necklace, cloak, ring, and belt. Working name **Equipment**. Skyy was not sure of the name; it is not final. Same UI rule as the wardrobe: placeholders on our pages, nothing on the inventory screen yet. This bar is not the accessory bag (`SkyyAccessories-Plan.md`).
14. **Accessory Power.** Like Hypixel Magical Power plus a selectable Power. Each accessory gives its own buff and also adds accessory power. Total power feeds one selectable buff. More power means a stronger buff. Several buffs to pick from. Locked examples: **Warrior** (strength as a damage modifier, plus a small amount of crit chance, crit damage, health, and defence) and **Elementalist** (boosts all elemental damage types and gives all elemental resistance). More options are TBD. The full list and the numbers are open. The crystal table and the curve in `SkyyAccessories-Plan.md` are the older draft, not this lock. The selected buff is what a loadout saves (lock 12).

## Locked later the same day — combat, defence, mana

Change note 9 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md` (collapsed section). Movement was locked later (change note 10). Does not change any jar.

15. **Damage and crits.** Use Hytale's damage and build on it, unless a custom system is easier later. Damage is a weapon-only modifier. Neutral damage uses the same name: Damage.
    - **Crit Chance.** No cap. 100% is a guaranteed crit. Over 100% is overcrit chance. 120% crit means a 20% chance to overcrit.
    - **Crit Damage.** SkyBlock-style. 0 crit damage means a crit is double a normal hit. +100% crit damage means double a normal crit, which is 4x a normal hit.
    - **Overcrit.** Always double whatever the crit hit is.
    - **True Damage** ignores enemy Defence. Mobs will almost never deal it. **True Defense is scrap.**
16. **Strength.** SkyBlock-style. Weapons, armor, and Equipment. Class skill trees can raise base Strength. The Wynn Strength skill point is out. **Dexterity is out** as a skill point. Crit Chance replaces it.
17. **Elements.** Earth, Thunder, Water, Fire, and Air are weapon modifiers only. A flat amount on the weapon (example: 40 Damage + 6 Fire). Base Damage is cut by the target's Defence. Element damage is applied on its own, then cut or raised by the target's element affinity and elemental defence. Same model as Wynncraft.
    - Single-element damage % (Fire Damage %, and the rest) is **Equipment only**.
    - Single-element defence (Fire Defence, and the rest) is **armor only**. Wynn-style.
    - **Elemental Damage %** and **Elemental Defence** (all elements) are **class skill trees only**.
    - **Percent Damage is scrap.**
    - Per-element main-attack lines are **open**, leaning skip. Prefer flat element on the weapon, on every attack.
    - Per-element spell % is **open**, leaning skip. Wynn spells are SkyWynn class skills. On every class except Mage and Shaman, those skills are mana abilities. Their element is set in the skill tree, not on weapons or armor.
    - Raw elemental spell damage is **skill trees and accessories**. An accessory can be specific (Archer arrow spam +10 Earth). A bonus on every skill is rare (every skill +10 Fire).
18. **Attack extras.**
    - **Attack Speed.** The weapon has a built-in swing speed, Wynn-style. +Attack Speed % can roll on weapons, armor, Equipment, and accessories. Cap **150%**.
    - **Ferocity.** Keep. SkyBlock-style. Cap **300** for now.
    - **Exploding** and **Poison.** Keep. Wynn-style.
    - **Reach.** Swing Range is renamed Reach. It is a % stat. Gathering skill trees only: Mining, Farming, and Gathering. Small upgrades. Total max **+50%**.
    - **Knockback.** Keep. Wynn-style.
    - **Ability Damage.** Keep. Skill trees, accessories, and Equipment. Not on weapons or armor.
19. **Health, Defence, dodge.**
    - **Health.** Every armor piece has base Health. Use Hytale's armor health unless we must make our own. Also on Equipment and accessories. Not on weapons. +Health % can be a gathering skill-tree upgrade.
    - **Defence.** SkyBlock-style, unless Hytale already has Defence we can use. The Wynn Defence skill point is out.
    - **Dodge Chance** replaces Wynn Agility as a gear skill point. It is part of the Acrobatics skill. A small % per Acrobatics level. Bigger upgrades in the Acrobatics skill tree. Also on dodge accessories. This does not redesign the rest of that tree.
20. **Regen and healing.**
    - **Raw Health Regen** and **Health Regen %** are in, Wynn-style. Hytale has no natural flat regen. The SkyBlock "faster natural regen" stat is scrap.
    - **Life Steal.** Keep. Heal from all damage you deal. Preferred shape to research: 10% Life Steal heals you every 3 seconds for 10% of the damage dealt in those 3 seconds. The numbers are open.
    - **Vitality is scrap** for now. Healing is Hytale food, the Cooking skill, and Alchemy health potions. Weak food and pots are a soft gate. Cooking and Alchemy are not hard-locked.
    - **Mending and Healing Efficiency are scrap.** Crowd healing comes later from a **Priest** class (healing spells and some damage, a support role). Class roles are an open item.
21. **Thorns, slow, weaken.** Thorns is armor only. Slow Enemy is weapon only (some skills will also slow). Weaken Enemy is weapons only. **Reflection was not called. It stays Open.**
22. **Mana.** Use Hytale's built-in mana. Our modifiers add to it. The Wynn Intelligence skill point is out.
    - **+Max Mana** is Wynn-style. On gear, Equipment only.
    - **Overall Level** is the average of all skill levels. Each Overall Level raises base Health and base Mana. The amount per level is open.
    - Class skill trees can add flat Health and flat Mana.
    - Gathering skill trees can add a small +% Health and +% Mana.
23. **Mana flow and spell cost.**
    - **Mana Regen.** Equipment and accessories. Also class skill trees, only for magic-using classes. Which classes those are is open.
    - **Mana Steal.** Weapons and accessories only.
    - **Rift Mana is scrap.**
    - Every per-spell cost ID is scrap. One flat **−% Spell Cost** covers all spells and skills. Accessory only.
    - Raw cost lives on the skill. **Skill-upgrade points** come every 5 levels. An upgrade raises damage, or range on a traversal skill, and lowers raw cost. How big that change is stays open.
24. **Class skill trees.** Borderlands-style, not a straight line. Research Borderlands 4 before any tree is designed. This note does not design the trees. The old "~25 nodes" draft is not this lock.

## Locked 2026-09-25 — Movement

Change note 10 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md` (same collapsed section). Gathering was locked later (change note 11). Does not change any jar.

25. **Speed.** SkyBlock-style flat +Speed. Can roll on armor, Equipment, and accessories. The Acrobatics skill tree still grants +% movement speed on its own.
26. **Sprint.** Scrap as a gear stat and as a sprint bar. Use Hytale stamina.
27. **Stamina Regen.** Sprint Regen, renamed. Armor only. Also grantable in the Acrobatics and Exploration skill trees. Not on weapons, Equipment, or accessories unless Skyy says later.
28. **Jump Height.** Skill trees and accessories only. Not on armor, Equipment, or weapons.
29. **Rift Speed.** Scrap.
30. **Reach stays.** Already locked (lock 18). Gathering trees only: Mining, Farming, and Gathering. Max +50%. Not re-opened.

## Locked 2026-09-25 — Gathering

Change note 11 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md` (same collapsed section). Loot and luck was partly locked later (change note 12). Does not change any jar.

31. **Breaking Power.** Add. Hytale may already have this under another name. That check is open.
32. **Mining Speed.** Yes. It increases pick swing speed. That is the main limit in Hytale.
33. **Pick Breaking Damage.** New SkyWynn name. Damage to blocks only. Not mobs. Open: how Hytale decides pick damage vs hits-to-break a block.
34. **Mining Spread.** Yes.
35. **Mining Fortune.** Yes. Ore Fortune, Block Fortune, Dwarven Metal Fortune, and Gemstone Fortune fold into it. One stat covers all.
36. **Auto Smelt.** Add. SkyBlock Smelting Touch. Ores auto-smelt to ingots.
37. **Farming Fortune.** Yes. Per-crop Farming Fortunes are scrap.
38. **Foraging Fortune.** Yes. Per-tree Foraging Fortunes are out for now.
39. **Timber.** Keep the name Timber. Not Treefeller. Not Sweep. Sweep is scrap. Extra breaks are on a horizontal plane only. Breaking the base already fells the whole tree in Hytale.
40. **Later.** Gemstone Spread and Pristine only if we add gemstones. Fishing and hunting stats stay parked until those mods exist.
41. **Skip for now.** Bonus Pest Chance (unsure about pests and the Garden). Overbloom. Gather Speed.

## Locked 2026-09-25 — Loot and luck (part)

Change note 12 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Pet Luck, Fear, and Tracking were locked later (change note 13). Does not change any jar.

42. **Loot Bonus.** Keep. Wynn. More items from mobs and loot chests.
43. **Loot Quality.** Keep. Wynn. Rarer loot, fewer commons.
44. **Stealing.** Keep. Wynn. Chance a hit mob drops an emerald.
45. **Trophy Hunter.** New name. Replaces the Magic Find name. Higher chance at unique drops and drop-only sets. Bosses and normal mobs. Mob drop-only armor sets, not only boss legendaries. Borderlands-style unique loot.
46. **Magic Find.** Scrap as the player-facing name. The idea lives on as Trophy Hunter.
47. **Still open at this note.** Pet Luck, Fear, and Tracking. Locked later (change note 13).

## Locked 2026-09-25 — Loot and luck (rest)

Change note 13 in `SkyWynn-Decisions.md`. Loot and luck is finished. XP and wisdom was locked later (change note 14). Does not change any jar.

48. **Pet Luck.** Keep later. Build when pets exist.
49. **Fear.** Scrap.
50. **Tracking.** Scrap.

## Locked 2026-09-25 — XP and wisdom

Change note 14 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. The Other table was scrapped later as gear IDs (change note 15). Oxygen and water swim speed are accessory effects (change note 16). Does not change any jar.

51. **Wisdom per skill we have.** One Wisdom stat for each skill we have.
52. **Combat Wisdom.** Keep. One modifier for every class. Combat XP levels the class.
53. **Keep now.** Farming, Mining, Foraging, Enchanting, Alchemy, and Carpentry Wisdom. Also Cooking, Smithing, Exploration, and Acrobatics Wisdom, because we have those skills.
54. **Social Wisdom.** Add later. Social is shelved. Not a skill we have now.
55. **Later.** Fishing Wisdom with fishing. Hunting Wisdom with hunting. Taming Wisdom with pets.
56. **Runecrafting Wisdom.** Scrap. No Runecrafting skill unless we add one.
57. **XP Bonus.** Keep. Wynn. A flat small % boost to all XP. Not a large boost.
58. **Gather XP Bonus.** Scrap. Wisdom covers gathering XP.
59. **Soul Point Regen.** Scrap. No soul points.

## Locked 2026-09-25 — Other

Change notes 15 and 16 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Next blank table is SkyBlock accessory powers. Does not change any jar.

60. **Other table.** Scrap all of it as gear IDs. Heat Resistance. Cold Resistance. Respiration. Pressure Resistance. Rift Time. Rift Damage. Rift Intelligence. Hearts.
61. **Oxygen.** Use Hytale's native oxygen. Do not add a Respiration stat ID. Accessories can raise oxygen. A max-level oxygen accessory line allows full underwater breathing.
62. **Water swim speed.** A separate accessory. It boosts swim speed in water. Not a gear ID.

## Locked 2026-09-25 — Accessory progression, enrichments, starters

Change notes 17–19 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Next blank table is the rest of SkyBlock accessory powers. Does not change any jar.

63. **Where accessories come from.** Most are crafted. Some come from mobs or chests.
64. **Craft tiers.** Leveling a collection unlocks the next accessory craft tier.
65. **Rarity ladder.** Crafting the next rarity needs the previous rarity as an ingredient. SkyBlock-style ladder.
66. **Enrichments to keep.** Speed, Crit Damage, Crit Chance, Strength, Defense, Health, Attack Speed. Same rulings as gear. Attack Speed cap stays 150%.
67. **Mana % enrichment.** Was Intelligence Enrichment. Mana %. No Intelligence ID. Accessories and Equipment follow the gear mana ruling.
68. **Sea Creature Chance Enrichment.** Add later. With fishing.
69. **Magic Find Enrichment.** Scrap. Magic Find is not the name.
70. **Ferocity Enrichment.** Pending captain. They said "not in the pack". Ferocity the combat stat stays. Cap 300. Do not scrap that stat.
71. **Accessory Power system.** Keep. You pick one power. More power makes that power's stats bigger.
72. **Starter powers.** Leaning Keep. Pending confirm. No Power, Fortuitous, Pretty, Protected, Simple, Warrior.
73. **Warrior name.** Rename TBD. It clashes with the Warrior class. This is the change note 8 example, pending that rename. Not a second power.
74. **Pretty.** Multi-stat blend. Health, Defense, Speed, Strength, mana, Crit Chance, Crit Damage. Not one theme.
75. **Same rulings.** Gear modifier rulings apply to accessories and Equipment the same way. A SkyBlock Intelligence line on an accessory is mana %.
76. **Wiki numbers.** Amounts at 250 Accessory Power, and the enrichment amounts, are research. They are not our numbers.

## Open research — Borderlands 4 skill trees

Public notes only. Not a SkyWynn design.

- Each Vault Hunter has **three skill trees**. Each tree starts from an Action Skill. Only one Action Skill is equipped at a time. ([Vex, official 2K page](https://borderlands.2k.com/borderlands-4/game-info/vault-hunters/vex/))
- Spend **5** skill points in a row to open the next row. After **15** points in that tree, **three branches** open. Each branch ends in a Capstone.
- Augments and Capstones have to be equipped. One of each at a time. They only work with that tree's Action Skill. Points can still be spent in the other trees.
- Respec is a Respec Machine in a settlement. Reset one tree or all points. It costs a percent of your cash, and you can do it again. ([PC Gamer](https://www.pcgamer.com/games/fps/borderlands-4-respec-reset-skill-point-tree/))

## What it covers
| Line | Style | Locked shape |
|---|---|---|
| Combat weapons and armor | Wynncraft | Copy Wynn's model. Class weapons: Archer shortbow/crossbow, Warrior sword/longsword/spear, Mage staff; later Assassin daggers/kunai; Shaman TBD; Berserker PENDING with no list. Every piece has a level requirement and a rarity. Mobs can drop any rarity. Rolled IDs show after identify (lock 9). Stats follow locks 15 and up (change notes 9–19), not the five Wynn skill points. Sets can be drop-only or craft-only, and a worn set has a set bonus (locks 10–11). Powders and Wynn's five elements stay (batch 2); powder slot counts are open |
| Gathering armor | Hypixel SkyBlock | Farming sets and foraging sets. Mining sets are likely the same idea. They are armor, so they follow the armor placement in locks 15 and up. Speed and Stamina Regen can sit on armor. Jump Height does not. Mining Fortune, Farming Fortune, and Foraging Fortune are in (change note 11). One stat each. A worn set has a set bonus |
| Equipment | Hypixel SkyBlock | Separate bar next to armor. Slots: necklace, cloak, ring, belt. Working name Equipment (not final). Saved in a loadout |
| Tools | Hypixel SkyBlock | Pickaxes, axes, hoes (rods later). Reforges, and tiers tied to the zone islands, are still to design. They are gear, so they carry a level requirement and a rarity. Gathering stats follow locks 31–41 |

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
9. **Stat list from accessory powers down.** Gathering is locked (change note 11). Loot and luck is finished (change notes 12 and 13). XP and wisdom is locked (change note 14). The Other table is scrap as gear IDs (change note 15, lock 60). Oxygen and swim speed are accessory effects (change note 16, locks 61–62). Accessory progression, enrichments, and starter powers are change notes 17–19 (locks 63–76). Next blank table is the rest of SkyBlock accessory powers, then tuning. Reach stays lock 18. Still open: the Breaking Power name in Hytale; how pick damage vs hits-to-break works; per-element main-attack lines and per-element spell % (leaning skip); Reflection; life-steal numbers; which classes count as magic-using for Mana Regen; Health and Mana per Overall Level; how big a skill upgrade is. Do not invent those numbers.
10. **Accessory Power list and numbers.** The system stays (lock 71). Starters lean Keep, pending confirm (lock 72): No Power, Fortuitous, Pretty, Protected, Simple, Warrior. Warrior's name is TBD (lock 73). Pretty is a multi-stat blend (lock 74). Elementalist stays the other change note 8 example. The rest of the power list, and every number, stay open. Enrichments are lock 66–70. Tuning is still blank. Do not treat the crystal table in `SkyyAccessories-Plan.md` as the lock. The craft ladder in locks 63–65 is the lock for how accessories are obtained. Bag-slot prices in that file stay a draft.
11. **Class skill trees.** Borderlands-style, not a straight line. The Borderlands 4 notes above are research. Do not design the trees yet. Decisions 6.3 (~25 nodes) is the older draft, not this lock.
12. **Class roles.** A Priest class is the later idea for crowd healing (healing spells and some damage). Roles are not defined yet.

## Tooltip style (Skyy, 2026-09-24)
SkyBlock style: each stat line shows the item's BASE value followed by what the roll / reforge adds in brackets, e.g. `Damage: 11-48 (+24%)`, `Strength: 12 (+3)`. First step: SkyyRolls 0.1.4 (0.1.3 lists the rolls as separate lines).
