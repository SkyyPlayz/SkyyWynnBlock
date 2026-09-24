# SkyyGear stat catalog
*Research list, 2026-09-24. Not a lock. The Decision column is blank on purpose. Write **Keep**, **Scrap**, or **Add later**. Nothing here is marked for you.*

The locked mix still stands (`SkyyGear-Plan.md` lock 8): Wynn's five skill points on weapons and armor, plus crit chance, crit damage, and fortune. This sheet is the menu for everything else.

**Count:** 83 SkyBlock lines and 72 Wynn lines. 6 lines are shared (marked Both), so they sit in both totals. SkyBlock's 81 category stats from the wiki are all here, plus weapon Damage and Mana.

**Game** means where the stat is from. **Both** means one row covers two names. A line that starts with **Clash** means the names match and the effects do not.

Major IDs (Wynn) are unique item effects, not shared stats. They are not in the tables. List: [Identifications § Major Identifications](https://wynncraft.wiki.gg/wiki/Identifications).

Left off the tables, because they are not a line you roll onto gear:

- SkyBlock Effective Health (math from Health and Defense).
- SkyBlock True Damage (a damage type). True Defense is the stat that answers it.
- SkyBlock Overflow Mana, Soulflow, Absorption, Heat, and Cold (pools or meters). Heat Resistance and Cold Resistance are the gear stats.
- Wynn skill-point requirements (a gate on the item, not a bonus).

---

## Combat offense

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Damage | SB | The weapon's own damage number. Strength and crits multiply it. | |
| Strength | SB | Multiplies the damage you deal. **Clash:** Wynn Strength is a skill point (next row). | |
| Strength | Wynn | Adds to the Strength skill point: more damage, and more Earth damage. A gear bonus does not count toward gear requirements. | |
| Dexterity | Wynn | Adds to Dexterity: a chance to crit for +100% damage, and more Thunder damage. SkyBlock uses Crit Chance instead of this. | |
| Crit Chance | SB | Chance a hit is a crit. At 100% or more, every hit crits. | |
| Crit Damage / Critical Damage Bonus | Both | A crit hits harder. SB Crit Damage is the standing multiplier. Wynn's ID is an extra bonus on top of Dexterity crits. | |
| Neutral damage | Wynn | The weapon's own damage with no element, before IDs. | |
| Earth damage (base) | Wynn | The weapon's own Earth damage, before IDs. | |
| Thunder damage (base) | Wynn | The weapon's own Thunder damage, before IDs. | |
| Water damage (base) | Wynn | The weapon's own Water damage, before IDs. | |
| Fire damage (base) | Wynn | The weapon's own Fire damage, before IDs. | |
| Air damage (base) | Wynn | The weapon's own Air damage, before IDs. | |
| Earth Damage % | Wynn | Percent bonus to Earth damage. | |
| Thunder Damage % | Wynn | Percent bonus to Thunder damage. | |
| Water Damage % | Wynn | Percent bonus to Water damage. Healing also scales with this. | |
| Fire Damage % | Wynn | Percent bonus to Fire damage. | |
| Air Damage % | Wynn | Percent bonus to Air damage. | |
| Elemental Damage % | Wynn | Percent bonus to every element's damage at once. | |
| Raw Earth damage | Wynn | Flat Earth damage. Items also split this into main-attack and spell lines. | |
| Raw Thunder damage | Wynn | Flat Thunder damage. Same main-attack and spell split. | |
| Raw Water damage | Wynn | Flat Water damage. Same split. | |
| Raw Fire damage | Wynn | Flat Fire damage. Same split. | |
| Raw Air damage | Wynn | Flat Air damage. Same split. | |
| Raw Elemental damage | Wynn | Flat damage added to every element at once. | |
| Main Attack Damage % | Wynn | Percent bonus to main-attack damage. Also called melee damage %. Does not add to raw damage IDs. | |
| Raw Main Attack Damage | Wynn | Flat bonus to main-attack damage. | |
| Spell Damage % | Wynn | Percent bonus to spell damage. **Clash:** not SkyBlock Ability Damage. | |
| Raw Spell Damage | Wynn | Flat bonus to spell damage. | |
| Raw Neutral Spell Damage | Wynn | Flat spell damage with no element. | |
| Attack Speed | Both | Faster swings. SB is a percent, cap 100. Wynn is a base tier (Super Slow to Super Fast) plus an ID that shifts that tier. | |
| Ferocity | SB | Chance a hit counts as extra hits. Each 100 is one guaranteed extra hit. Cap 500. | |
| Exploding | Wynn | Chance a main-attack hit blows up and hurts nearby mobs. Past 100% does nothing more. | |
| Poison | Wynn | Extra damage over time after you hit. The number is the total over 3 seconds. | |
| Swing Range / Main Attack Range | Both | How far a melee hit reaches. SB is blocks (base 3, cap 15). Wynn is a percent. | |
| Knockback | Wynn | How far a valid hit pushes a mob. Past −100% it pulls them in. Capped at ±300%. | |
| Ability Damage | SB | Multiplies ability and magic damage. **Clash:** not Wynn spell damage. | |

## Combat defense

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Health | Both | Max health. SB Health, and the base Health number on Wynn armour. Wynn's Health ID is the next row. | |
| Health (ID) | Wynn | Flat health on top of base health. The wiki also calls this Raw Health. | |
| Defense | SB | Cuts damage from normal hits. Does not stop True Damage. **Clash:** not the Wynn Defence skill point, and not elemental defence. | |
| Defence | Wynn | Adds to the Defence skill point: less damage taken, and more Fire damage. | |
| Agility | Wynn | Adds to Agility: a chance to dodge (that hit deals 90% less), and more Air damage. | |
| True Defense | SB | Cuts True Damage. Normal Defense does not. | |
| Earth Defence | Wynn | Percent defence against Earth damage. | |
| Thunder Defence | Wynn | Percent defence against Thunder damage. | |
| Water Defence | Wynn | Percent defence against Water damage. | |
| Fire Defence | Wynn | Percent defence against Fire damage. | |
| Air Defence | Wynn | Percent defence against Air damage. | |
| Elemental Defence | Wynn | Percent defence against every element at once. | |
| Health Regen | SB | Faster natural health recovery. **Clash:** Wynn regen is the next two rows, and it does not speed natural regen the same way. | |
| Raw Health Regen | Wynn | Flat health gained or lost on a timer. Negative drains you. | |
| % Health Regen | Wynn | Percent change to Raw Health Regen. Does not change natural regen. | |
| Life Steal | Wynn | Health from landing your main attack. The number is the total over 3 seconds of attacking. | |
| Vitality | SB | A pool that healing abilities spend. Base 100. | |
| Mending / Healing Efficiency | Both | Stronger heals. SB Mending is heals you give other people. Wynn Healing Efficiency is heals on you and others, except potions, regen, and life steal. | |
| Thorns | Wynn | Chance a melee attacker takes damage back. Past 100% does nothing more. | |
| Reflection | Wynn | Same as Thorns, for spells and projectiles. | |
| Slow Enemy | Wynn | A hit mob moves slower. Caps at 50%. | |
| Weaken Enemy | Wynn | A hit mob deals less damage. Caps at 50%. | |

## Mana and abilities

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Intelligence | SB | Bigger mana pool, and more magic damage. **Clash:** Wynn Intelligence is the next row. | |
| Intelligence | Wynn | Adds to Intelligence: cheaper spells (up to 50% off), a bigger mana pool, and more Water damage. | |
| Mana | SB | The mana pool. Base 100. It grows with Intelligence. Gear usually adds Intelligence, not Mana itself. | |
| Max Mana | Wynn | Flat mana. Caps at 400, counting Intelligence and the base 100. | |
| Mana Regen | Wynn | Mana back over time. Shown per 5 seconds. | |
| Mana Steal | Wynn | Mana from landing your main attack. The number is the total over 3 seconds of attacking. | |
| Rift Mana Regen | SB | Mana regen inside the Rift only. | |
| 1st Spell Cost % | Wynn | Percent change to the mana cost of spell 1. A minus is cheaper. | |
| 2nd Spell Cost % | Wynn | Percent change to the mana cost of spell 2. | |
| 3rd Spell Cost % | Wynn | Percent change to the mana cost of spell 3. | |
| 4th Spell Cost % | Wynn | Percent change to the mana cost of spell 4. | |
| Raw 1st Spell Cost | Wynn | Flat mana added or removed from spell 1's cost. | |
| Raw 2nd Spell Cost | Wynn | Flat mana added or removed from spell 2's cost. | |
| Raw 3rd Spell Cost | Wynn | Flat mana added or removed from spell 3's cost. | |
| Raw 4th Spell Cost | Wynn | Flat mana added or removed from spell 4's cost. | |

## Movement

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Speed / Walk Speed | Both | Move faster. SB Speed base is 100, cap 400. Wynn Walk Speed is a percent, and stops helping past +400%. | |
| Sprint | Wynn | How long you can sprint before the bar runs out. | |
| Sprint Regen | Wynn | How fast the sprint bar refills. | |
| Jump Height | Wynn | How high you jump. | |
| Rift Speed | SB | Move speed inside the Rift only. | |

## Gathering

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Breaking Power | SB | Lets you mine harder blocks. | |
| Mining Speed | SB | Mines blocks faster. | |
| Mining Spread | SB | Breaks nearby blocks too. Every 100 is another block. Not gemstones. Off on a private island. | |
| Gemstone Spread | SB | Breaks nearby gemstone blocks. | |
| Pristine | SB | Chance a mined gemstone comes out a higher quality. | |
| Mining Fortune | SB | Chance of extra mining drops. Every 100 is one extra drop. | |
| Ore Fortune | SB | Extra Mining Fortune on ores. | |
| Block Fortune | SB | Extra Mining Fortune on blocks. | |
| Dwarven Metal Fortune | SB | Extra Mining Fortune on dwarven metals. | |
| Gemstone Fortune | SB | Extra Mining Fortune on gemstones. | |
| Farming Fortune | SB | Chance of extra crop drops. Every 100 is one extra drop. | |
| Wheat Fortune | SB | Extra Farming Fortune on wheat. | |
| Carrot Fortune | SB | Extra Farming Fortune on carrots. | |
| Potato Fortune | SB | Extra Farming Fortune on potatoes. | |
| Pumpkin Fortune | SB | Extra Farming Fortune on pumpkins. | |
| Sugar Cane Fortune | SB | Extra Farming Fortune on sugar cane. | |
| Melon Slice Fortune | SB | Extra Farming Fortune on melon slices. | |
| Cactus Fortune | SB | Extra Farming Fortune on cactus. | |
| Cocoa Beans Fortune | SB | Extra Farming Fortune on cocoa beans. | |
| Mushroom Fortune | SB | Extra Farming Fortune on mushrooms. | |
| Nether Wart Fortune | SB | Extra Farming Fortune on nether wart. | |
| Sunflower Fortune | SB | Extra Farming Fortune on sunflowers. | |
| Moonflower Fortune | SB | Extra Farming Fortune on moonflowers. | |
| Wild Rose Fortune | SB | Extra Farming Fortune on wild roses. | |
| Bonus Pest Chance | SB | More pests can spawn at once. | |
| Overbloom | SB | Higher chance of rare crops. | |
| Foraging Fortune | SB | Chance of extra foraging drops. Every 100 is one extra drop. | |
| Fig Fortune | SB | Extra Foraging Fortune on fig logs. | |
| Mangrove Fortune | SB | Extra Foraging Fortune on mangrove logs. | |
| Helix Fortune | SB | Extra Foraging Fortune on helix logs. | |
| Sweep | SB | Lets an axe break more logs. Tougher trees need more Sweep. | |
| Timber | SB | Chance the first axe cut fells the whole tree. | |
| Fishing Speed | SB | How fast a catch lands. The cap depends on the zone. | |
| Sea Creature Chance | SB | Chance a catch is a sea creature. | |
| Double Hook Chance | SB | Chance to hook a second sea creature. Cap 100. | |
| Treasure Chance | SB | Higher chance of a fishing treasure. | |
| Trophy Chance | SB | Higher chance of a trophy fish. Cap 150. | |
| Pull | SB | What a fishing net can grab, and how long it takes. | |
| Hunting Fortune | SB | Chance of extra attribute shards. Every 100 is one extra shard. | |
| Charm Chance | SB | Higher chance a killed mob drops an attribute shard. | |
| Gather Speed | Wynn | Faster gathering. Found on ingredients, not normal armour. | |

## Loot and luck

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Magic Find | SB | Higher chance of rare drops from mobs and bosses. Cap 900. **Clash:** not Wynn Loot Bonus. | |
| Pet Luck | SB | Higher chance a mob or boss drops a pet. | |
| Loot Bonus | Wynn | More items from mobs and loot chests. | |
| Loot Quality | Wynn | Rarer loot, fewer commons. Mostly on ingredients. | |
| Stealing | Wynn | Chance a hit mob drops an emerald. | |
| Fear | SB | During the Great Spook, Primal Fears spawn more often and hurt you less. | |
| Tracking | SB | Higher chance to find elusive mobs. | |

## XP and wisdom

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Combat Wisdom | SB | More Combat XP. | |
| Farming Wisdom | SB | More Farming XP. | |
| Fishing Wisdom | SB | More Fishing XP. | |
| Mining Wisdom | SB | More Mining XP. | |
| Foraging Wisdom | SB | More Foraging XP. | |
| Enchanting Wisdom | SB | More Enchanting XP. | |
| Alchemy Wisdom | SB | More Alchemy XP. | |
| Carpentry Wisdom | SB | More Carpentry XP. | |
| Runecrafting Wisdom | SB | More Runecrafting XP. | |
| Taming Wisdom | SB | More Taming XP. | |
| Social Wisdom | SB | More Social XP. | |
| Hunting Wisdom | SB | More Hunting XP. | |
| XP Bonus | Wynn | More XP from mobs and dungeons. Quests, discoveries, raids, and profession XP are left out. | |
| Gather XP Bonus | Wynn | More gathering XP. On ingredients. | |
| Soul Point Regen | Wynn | Chance of an extra soul point at dawn. Negative can skip the daily point. | |

## Other

| Stat | Game | What it does | Decision |
|---|---|---|---|
| Heat Resistance | SB | Heat builds slower in the Magma Fields. | |
| Cold Resistance | SB | Cold builds slower in the Glacite tunnels and mineshafts. | |
| Respiration | SB | Longer breath underwater. Base 30. | |
| Pressure Resistance | SB | Pressure hurts less while diving. | |
| Rift Time | SB | Longer stay in the Rift before you are sent out. | |
| Rift Damage | SB | More damage dealt inside the Rift. | |
| Rift Intelligence | SB | More mana, and more mana regen, inside the Rift. | |
| Hearts | SB | Extra hits you can take from some Rift creatures. | |

## New SkyWynn stats

Stats we invent. None yet.

| Stat | What it might do | Decision |
|---|---|---|
| | | |
| | | |
| | | |

## Sources

- [Stats](https://hypixelskyblock.minecraft.wiki/w/Stats) — Hypixel SkyBlock Wiki. Player stats, read 2026-09-24. Combat, mining, farming, foraging, fishing, miscellaneous, hunting, wisdom, rift, and other.
- [Identifications](https://wynncraft.wiki.gg/wiki/Identifications) — Official Wynncraft Wiki. The ID list, plus the min/max table for the per-element lines. Major IDs are on that page and are not copied here.
- [Skill Points](https://wynncraft.wiki.gg/wiki/Skill_Points) — what Strength, Dexterity, Intelligence, Defence, and Agility do.
- [Elements](https://wynncraft.wiki.gg/wiki/Elements) — the five elements, and which skill point each one follows.
- [Soul Points](https://wynncraft.wiki.gg/wiki/Soul_Points) — Soul Point Regen.
