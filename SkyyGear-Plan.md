# SkyyGear - plan
*Design lock 2026-09-24 (Skyy). Nothing here is built. Change note: `SkyWynn-Decisions.md`. Code follow-ups: `HANDOFF.md`, `DESIGN-STATUS.md`.*

## BUILDER / STATUS (2026-09-25)

**SkyGear is planned enough to START BUILDING.** Implement locked systems. Do not block on open tables.

**LOCKED enough to implement.** Themes and rules in this file are the lock. Do not invent the open numbers. Not in any jar yet.

- Gear rules in locks 1–14. Combat, defence, and mana in locks 15 and up. Magical Power is spell damage. Strength is melee or hit damage (lock 102).
- Movement, gathering, loot, and wisdom are locked (change notes 10–14).
- Ferocity: enchant cap 300, total cap 600 (lock 77).
- Accessory craft ladder (locks 63–65). Enrichments (locks 66–70). Ferocity Enrichment is still pending.
- Starters: Tank, Balance, Slayer, Lucky, Fast, Magical (locks 80–86, 104).
- Combat 15: Fortress, Harmony, Glass Cannon, Fortune, Blitz, Arcane (locks 94, 105–109). Amounts scale with Accessory Power. Curves are not locked.
- Accessory Power model (change note 23): each accessory has its own buffs and adds flat +10 to +25 Accessory Power by rarity. Exact table is not set. Total is the sum of equipped accessories. The selected profile scales from that total.
- Default profile is Balance (change note 24). No empty profile. Players can switch to Tank, Slayer, Lucky, Fast, Magical, or the Combat 15 ladder when unlocked.
- Gear pipeline (change note 25, locks 119–126): combat gear first. Rarity drives modifier count and power. Crafted gear rolls on craft. Mob drops stay unidentified until identify.

**STILL OPEN.** Do not block the build on these. Do not invent them.

- Tuning table.
- Stone powers. Do not extend the Hypixel stone list.
- Wynn Major IDs.
- Exact numeric curves. The +10 to +25 Accessory Power range is locked. The table is not.
- Magical Power on enrichments or tuning.
- Gathering gear (mining, farming, foraging). Combat gear is the first build.
- Pets, fishing, and hunting.
- Fortress extra debuff, if any.

Skyy's direction still holds: every mod in the pack is eventually our own. Combat armor and weapons copy Wynncraft. Gathering gear is SkyBlock-style. We rebuild features ourselves. Never copy another author's files (items, models, textures, code) unless their license allows it.

## Locked (2026-09-24)

1. **Level + rarity, Wynn-style.** Every gear item has a level requirement and a rarity tier. The exact rarity names and colours are not locked (open questions). Which level type the requirement uses (skill vs class vs combat) is still the earlier same-day question; this lock only says every gear item has one. **Change note 25:** craft and drop both have a rarity. Rarity drives modifier count and power.
2. **Smithing rarity.** A higher Smithing level raises a **smithing rarity** stat. That stat increases the chance of crafting a higher-rarity item. Smelting still pays Smithing XP (the existing SkyySkills lock). SkyySkills 0.4 does not have this stat.
3. **Rarity sets reforge quality.** The higher an item's rarity, the better the rolls a reforge can give: a wider and higher roll range. A reforge still swaps the bonuses (batch 2). How you obtain and apply a reforge is still open.
4. **Unidentified drops, Wynn-style.** Mobs drop unidentified weapons and armor. Identifying one reveals its rolled IDs. How the player identifies is lock 9. SkyyRolls 0.1.3 shows rolls on the item immediately; that is the jar, not this rule. **Change note 25:** rarity is set before identify. Identify reveals what the item is and its roll. Crafted gear gets rarity and the roll on craft.
5. **Combat armor and weapons** basically copy Wynncraft. Class weapons stay the ones already named in `SkyyClasses-Plan.md`. Berserker is still PENDING and has no weapon list.
6. **Gathering gear** is SkyBlock-style: farming armor sets and foraging armor sets. Mining armor is likely the same kind of set. This note does not name the pieces. **Change note 25:** those pieces come later. Combat gear is the first build.
7. **Wardrobe + loadouts**, Hypixel SkyBlock style: save a gear set and quick-swap to it. **UI:** placeholders are fine. Nothing on the inventory screen yet (`SkyWynn-Decisions.md` 10.22). What a loadout saves is lock 12.
8. **Stat mix (revised later the same day).** This note put Wynn's five skill points on weapons and armor, with crit chance, crit damage, and fortune layered on. **Change note 9 replaces the five skill points.** Strength is SkyBlock-style. Dexterity, Wynn Defence, Wynn Intelligence, and Wynn Agility are not gear skill points. Crit chance and crit damage stay, with the rules in locks 15 and up. **Gathering fortunes were locked later (change note 11).** Mining Fortune, Farming Fortune, and Foraging Fortune are in. One stat each. Loot and luck was finished later (change notes 12 and 13). XP and wisdom was locked later (change note 14). The Other table was scrapped later as gear IDs (change note 15). Oxygen and water swim speed are accessory effects (change note 16). Accessory progression and enrichments were locked later (change notes 17–18). Change note 19 leaned Keep on Hypixel starter names. Change note 20 replaces that list with Tank, Balance, Slayer, Lucky, Fast, and Magical. Change note 21 is the Combat 15 ladder. Change note 22 confirms Fortress, Harmony, Fortune, Blitz, and Arcane, and adds Magical Power. Change note 23 is the Accessory Power sum: flat +10 to +25 by rarity, total is the sum, the selected profile scales from that total. Next blank table is stone powers. No Power is scrap (change note 24). The default profile is Balance. Change note 25 is the gear pipeline. Combat gear is the first build. Gathering gear is later.
9. **Identification.** For now, a menu opened with `/identify`. Later `/identify` is disabled and identification moves to an NPC, Wynncraft-style. Identifying costs coins. The cost scales with the item's rarity and level. The cost formula is open. The menu is one of our pages (placeholders are fine). It does not go on the inventory screen (10.22). SkyyRolls 0.1.3 has no identify step.
10. **Drops and sets.** Mob drops can be any rarity. Some sets are drop-only. Some sets are craft-only. That closes the older question about craft-only tiers.
11. **Set bonuses.** Sets have a bonus for wearing the set, in the vein of Wynncraft set bonuses and Hypixel's Full Set Bonus. Which sets, and the bonus numbers, are not named here.
12. **Loadout contents.** A loadout saves armor, the Equipment bar (lock 13), and the selected Accessory Power buff (lock 14). Pets are saved too, once pets exist. Placeholders stay off the inventory screen.
13. **Equipment bar.** A separate bar next to armor, SkyBlock's Equipment layout: necklace, cloak, ring, and belt. Working name **Equipment**. Skyy was not sure of the name; it is not final. Same UI rule as the wardrobe: placeholders on our pages, nothing on the inventory screen yet. This bar is not the accessory bag (`SkyyAccessories-Plan.md`).
14. **Accessory Power.** Like Hypixel Magical Power plus a selectable Power. Each accessory gives its own buff and also adds accessory power. Total power feeds one selectable buff. More power means a stronger buff. Several buffs to pick from. Locked examples at this note: **Warrior** and **Elementalist**. The Warrior name was scrapped later as a power name (change note 20). The crystal table and the curve in `SkyyAccessories-Plan.md` are the older draft, not this lock. The selected buff is what a loadout saves (lock 12). **Tightened later (change note 23):** each accessory adds flat +10 to +25 Accessory Power by rarity. The exact table is not set. Total Accessory Power is the sum across equipped accessories. The selected profile scales from that total.

## Locked later the same day — combat, defence, mana

Change note 9 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md` (collapsed section). Movement was locked later (change note 10). Does not change any jar.

15. **Damage and crits.** Use Hytale's damage and build on it, unless a custom system is easier later. Damage is a weapon-only modifier. Neutral damage uses the same name: Damage.
    - **Crit Chance.** No cap. 100% is a guaranteed crit. Over 100% is overcrit chance. 120% crit means a 20% chance to overcrit.
    - **Crit Damage.** SkyBlock-style. 0 crit damage means a crit is double a normal hit. +100% crit damage means double a normal crit, which is 4x a normal hit.
    - **Overcrit.** Always double whatever the crit hit is.
    - **True Damage** ignores enemy Defence. Mobs will almost never deal it. **True Defense is scrap.**
16. **Strength.** SkyBlock-style. Weapons, armor, and Equipment. Class skill trees can raise base Strength. The Wynn Strength skill point is out. **Dexterity is out** as a skill point. Crit Chance replaces it. **Tightened later (change note 22):** Strength boosts physical damage from a melee or hit. Magical Power is the spell counterpart. Also on accessories.
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
    - **Ferocity.** Keep. SkyBlock-style. Combat, gear, and accessories. **Tightened later (change note 20):** enchant cap **300**. Total cap **600**.
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

Change note 10 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md` (same collapsed section). Gathering was locked later (change note 11). Change note 25: movement modifiers can roll on any gear, except where a lock below already names a tighter slot. Does not change any jar.

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

Change notes 17–19 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. The Hypixel starter lean in locks 72–74 was replaced later (change note 20). Does not change any jar.

63. **Where accessories come from.** Most are crafted. Some come from mobs or chests.
64. **Craft tiers.** Leveling a collection unlocks the next accessory craft tier.
65. **Rarity ladder.** Crafting the next rarity needs the previous rarity as an ingredient. SkyBlock-style ladder.
66. **Enrichments to keep.** Speed, Crit Damage, Crit Chance, Strength, Defense, Health, Attack Speed. Same rulings as gear. Attack Speed cap stays 150%.
67. **Mana % enrichment.** Was Intelligence Enrichment. +% mana on a dedicated mana accessory. No Intelligence ID. Powers use flat mana (change note 20).
68. **Sea Creature Chance Enrichment.** Add later. With fishing.
69. **Magic Find Enrichment.** Scrap. Magic Find is not the name.
70. **Ferocity Enrichment.** Pending. Not locked. Ferocity the stat stays (change note 20). Do not scrap that stat.
71. **Accessory Power system.** Keep. You pick one power. More power makes that power's stats bigger.
72. **Starter powers at this note.** Leaning Keep. Pending confirm. No Power, Fortuitous, Pretty, Protected, Simple, Warrior. Replaced later (change note 20).
73. **Warrior name at this note.** Rename TBD. Replaced later (change note 20). The name is scrap.
74. **Pretty at this note.** Multi-stat blend. Replaced later by Balance (change note 20).
75. **Same rulings.** Gear modifier rulings apply to accessories and Equipment the same way. Powers use flat mana (change note 20). Dedicated mana accessories use +% mana.
76. **Wiki numbers.** Amounts at 250 Accessory Power, and the enrichment amounts, are research. They are not our numbers.

## Locked 2026-09-25 — Ferocity caps and custom starters

Change note 20 in `SkyWynn-Decisions.md`. Replaces the Hypixel starter lean in change note 19. Marked in `SkyyGear-Stat-Catalog.md`. Next blank table is the rest of SkyBlock accessory powers. No Power was scrapped later (change note 24). The default profile is Balance. Does not change any jar.

77. **Ferocity.** Keep. Combat, gear, and accessories. Enchant cap 300. Total cap 600.
78. **Ferocity Enrichment.** Still pending. Do not scrap the Ferocity stat.
79. **Hypixel starter names.** Scrap. Fortuitous, Pretty, Protected, Simple, Warrior.
80. **Starter baseline.** Every starter power grants a little Health and Defense. That baseline is the same on each starter.
81. **Tank.** Keep. Bonus Health and Defense only. No other stats.
82. **Balance.** Keep. Even boost to Health, Defense, Speed, Strength, flat mana, Crit Chance, and Crit Damage.
83. **Slayer.** Keep. More Strength and Crit Damage. Less Health and Defense. The name is Slayer.
84. **Lucky.** Keep. Normal Health and Defense. High Crit Chance.
85. **Fast.** Keep. Normal Health and Defense. High Speed and Attack Speed.
86. **Magical.** Keep. Normal Health. Less Defense than the others. Flat mana and mana regen. Also boosts Magical Power (change note 22).
87. **Mana on powers.** Flat mana. Not Intelligence. Not mana %.
88. **Mana on dedicated accessories.** +% mana. The Mana % enrichment stays that rule.
89. **No Power at this note.** Pending. Scrapped later (change note 24).
90. **Later powers at this note.** Combat 15+ Hypixel powers and stone powers are not locked. Hypixel Combat 15 names were scrapped later (change note 21). Stone powers stay pending.

## Locked 2026-09-25 — Combat 15 power ladder

Change note 21 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Next blank table is stone powers. No Power was scrapped later (change note 24). The default profile is Balance. Does not change any jar.

91. **Combat 15 shape.** These powers mirror the starter themes. They are more extreme.
92. **Buffs and debuffs.** SkyBlock style. A Combat 15 power can raise some stats and cut others.
93. **Scaling.** Stat amounts still scale with total Accessory Power.
94. **Glass Cannon.** Keep. Combat 15 form of Slayer. −Health. −Defense. Much more Strength and Crit Damage. Solid Crit Chance.
95. **Fortress at this note.** Draft. Confirmed later (change note 22).
96. **Harmony at this note.** Draft. Confirmed later (change note 22). Magical Power stays off this spread.
97. **Fortune at this note.** Draft. The debuff picks here were replaced later (change note 22).
98. **Blitz at this note.** Draft. Confirmed later (change note 22). −Health and −Defense.
99. **Arcane at this note.** Draft. Confirmed later (change note 22). It boosts Magical Power. −Defense and −Strength.
100. **Hypixel Combat 15 names.** Scrap as copy-paste. Commando, Disciplined, Inspired, Ominous, Prepared.
101. **Still pending at this note.** Stone powers. The exact debuff on the drafts. Confirmed later for the five names (change note 22). Fortress's extra debuff stays optional. No Power was scrapped later (change note 24).

## Locked 2026-09-25 — Magical Power and Combat 15 confirm

Change note 22 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Next blank table is stone powers. No Power was scrapped later (change note 24). The default profile is Balance. Does not change any jar.

102. **Magical Power.** Keep. Spell-damage stat. Strength boosts a melee or hit. Magical Power does that job for spells. A Mage can melee with a staff and also cast. Staff melee uses Strength. Spells use Magical Power.
103. **Where it rolls.** Weapons, armor, Equipment, and accessories. Same gear rulings as Strength. This is not the bag score. The bag score is Accessory Power.
104. **Starter Magical.** Normal Health. Less Defense than the others. Flat mana, mana regen, and a Magical Power boost.
105. **Fortress.** Keep. Combat 15 form of Tank. Large Health and Defense. A Speed or Strength debuff is optional. Not picked.
106. **Harmony.** Keep. Combat 15 form of Balance. Larger even spread: Health, Defense, Speed, Strength, flat mana, Crit Chance, Crit Damage. Magical Power is not in this spread unless added later.
107. **Fortune.** Keep. Combat 15 form of Lucky. Much higher Crit Chance. Good Crit Damage. Slight Strength. −Health. −Defense.
108. **Blitz.** Keep. Combat 15 form of Fast. High Speed and Attack Speed. −Health. −Defense.
109. **Arcane.** Keep. Combat 15 form of Magical. More Magical Power than the starter. −Defense. −Strength. Flat mana and mana regen.
110. **Still pending at this note.** Stone powers. Fortress's extra debuff, if any. Whether Magical Power is an enrichment or a tuning stat. No Power was scrapped later (change note 24).

## Locked 2026-09-25 — Accessory Power model

Change note 23 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Does not change any jar.

111. **Inherent buffs.** Each accessory has its own buffs. Those buffs stay on with whichever profile is selected. There is no empty profile (change note 24).
112. **Flat Accessory Power.** Each accessory also adds a flat amount by rarity. The range is +10 to +25. The exact table is not set. The old 3/5/8/12/16 draft is not the lock.
113. **Total.** Accessory Power is the sum across equipped accessories.
114. **Selected profile.** Tank, Balance, Slayer, and the Combat 15 ladder scale their stats from that total.
115. **No Power at this note.** Pending. Scrapped later (change note 24). There is no empty profile.

## Locked 2026-09-25 — No empty profile

Change note 24 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Next blank table is stone powers. Does not change any jar.

116. **No Power.** Scrap. No selectable empty profile.
117. **Default profile.** Balance. It is the starter default.
118. **Switch list.** Players can switch to Tank, Slayer, Lucky, Fast, or Magical. They can also switch to the Combat 15 ladder when unlocked: Fortress, Harmony, Glass Cannon, Fortune, Blitz, Arcane.

## Locked 2026-09-25 — Gear pipeline

Change note 25 in `SkyWynn-Decisions.md`. Marked in `SkyyGear-Stat-Catalog.md`. Combat gear is the first build. Does not change any jar.

119. **Rarity on every piece.** Craft or drop. Wynn-style. Rarity drives modifier count and power. Exact names and colours stay open.
120. **Combat gear first.** Mob-dropped gear is combat gear. Default Hytale gear is combat gear for now.
121. **Gathering gear later.** Mining, farming, and foraging gear come later, with that skill's modifiers. Do not block combat gear on them.
122. **Crafted gear.** It gets its rarity and its roll on craft. No identify step.
123. **Mob drops.** They start unidentified. The player must identify them. Rarity is set before identify. Identify reveals what the item is and its roll.
124. **Roll system.** Stays as designed now (locks 1–14 and the tooltip note). The modifier pool is every Keep modifier from this catalog pass, filtered by lock 125.
125. **Placement.** Combat modifiers only on combat gear. Movement modifiers on any gear. Skill-specific modifiers only on that skill's gear. A catalog row that already names a tighter slot still uses that slot.
126. **Default profile.** Balance. No empty profile. No Power stays scrap (change note 24).

## Open research — Borderlands 4 skill trees

Public notes only. Not a SkyWynn design.

- Each Vault Hunter has **three skill trees**. Each tree starts from an Action Skill. Only one Action Skill is equipped at a time. ([Vex, official 2K page](https://borderlands.2k.com/borderlands-4/game-info/vault-hunters/vex/))
- Spend **5** skill points in a row to open the next row. After **15** points in that tree, **three branches** open. Each branch ends in a Capstone.
- Augments and Capstones have to be equipped. One of each at a time. They only work with that tree's Action Skill. Points can still be spent in the other trees.
- Respec is a Respec Machine in a settlement. Reset one tree or all points. It costs a percent of your cash, and you can do it again. ([PC Gamer](https://www.pcgamer.com/games/fps/borderlands-4-respec-reset-skill-point-tree/))

## What it covers
| Line | Style | Locked shape |
|---|---|---|
| Combat weapons and armor | Wynncraft | Copy Wynn's model. Class weapons: Archer shortbow/crossbow, Warrior sword/longsword/spear, Mage staff; later Assassin daggers/kunai; Shaman TBD; Berserker PENDING with no list. Every piece has a level requirement and a rarity. Mobs can drop any rarity. Rolled IDs show after identify (lock 9). Stats follow locks 15 and up (change notes 9–22), not the five Wynn skill points. Change note 25: this is the first build. Rarity drives modifier count and power. Crafted pieces roll on craft. Mob drops identify to reveal the item and the roll. Sets can be drop-only or craft-only, and a worn set has a set bonus (locks 10–11). Powders and Wynn's five elements stay (batch 2); powder slot counts are open |
| Gathering armor | Hypixel SkyBlock | Later (change note 25). Combat gear is the first build. When built: farming sets and foraging sets. Mining sets are likely the same idea. Mining Fortune, Farming Fortune, and Foraging Fortune are in (change note 11). One stat each. Skill modifiers sit on that skill's gear. A worn set has a set bonus |
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
9. **Stat list from accessory powers down.** Gathering is locked (change note 11). Loot and luck is finished (change notes 12 and 13). XP and wisdom is locked (change note 14). The Other table is scrap as gear IDs (change note 15, lock 60). Oxygen and swim speed are accessory effects (change note 16, locks 61–62). Accessory progression and enrichments are change notes 17–18 (locks 63–70). Custom starters and Ferocity caps are change note 20 (locks 77–90). The Combat 15 ladder is change note 21 (locks 91–101). Magical Power and the Combat 15 confirm are change note 22 (locks 102–110). Next blank table is stone powers, then tuning. No Power is scrap (change note 24). The default profile is Balance. Whether Magical Power joins enrichments or tuning is open. Reach stays lock 18. Still open: the Breaking Power name in Hytale; how pick damage vs hits-to-break works; per-element main-attack lines and per-element spell % (leaning skip); Reflection; life-steal numbers; which classes count as magic-using for Mana Regen; Health and Mana per Overall Level; how big a skill upgrade is. Do not invent those numbers. Change note 25: start the combat-gear build. Gathering gear is later. Do not block on the blank tables.
10. **Accessory Power list and numbers.** The system stays (lock 71). Custom starters are locks 80–86: Tank, Balance, Slayer, Lucky, Fast, Magical. Hypixel names Fortuitous, Pretty, Protected, Simple, and Warrior are scrap (lock 79). The change note 8 example named Warrior is that scrap name. Elementalist is not in the starter list. It is not re-opened here. The model is change note 23 (locks 111–115): own buffs, flat +10 to +25 Accessory Power by rarity, exact table not set, total is the sum, the selected profile scales from that total. No Power is scrap (lock 116). The default profile is Balance (lock 117). Glass Cannon is Keep (lock 94). Fortress, Harmony, Fortune, Blitz, and Arcane are Keep (locks 105–109). Hypixel Combat 15 names are scrap (lock 100). Stone powers are not locked (lock 110). Magical Power is the spell-damage stat (lock 102). It is not the bag score. Numbers stay open. Powers use flat mana (lock 87). Dedicated mana accessories use +% mana (lock 88). Enrichments are locks 66–70. Ferocity Enrichment is still pending (lock 78). Tuning is still blank. Do not treat the crystal table in `SkyyAccessories-Plan.md` as the lock. The craft ladder in locks 63–65 is the lock for how accessories are obtained. Bag-slot prices in that file stay a draft.
11. **Class skill trees.** Borderlands-style, not a straight line. The Borderlands 4 notes above are research. Do not design the trees yet. Decisions 6.3 (~25 nodes) is the older draft, not this lock.
12. **Class roles.** A Priest class is the later idea for crowd healing (healing spells and some damage). Roles are not defined yet.

## Tooltip style (Skyy, 2026-09-24)
SkyBlock style: each stat line shows the item's BASE value followed by what the roll / reforge adds in brackets, e.g. `Damage: 11-48 (+24%)`, `Strength: 12 (+3)`. First step: SkyyRolls 0.1.4 (0.1.3 lists the rolls as separate lines).
