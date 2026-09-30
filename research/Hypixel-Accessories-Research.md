# Hypixel SkyBlock accessories: research

*For Skyy. Written 2026-09-30. Research only, not a decision. It feeds the next pass: booster accessories (+Strength, +% movement speed, +Stamina, +Health, +Mana) with upgrade lines, many of them mob drops and loot-chest finds. How they are made and upgraded is left for later, as Skyy asked.*

Tags: **VERIFIED** = seen in a wiki page or changelog. **UNVERIFIED** = sources disagree or the number may be out of date.

**Sources.** The official wiki (wiki.hypixel.net) **closed in July 2026**. It now redirects to a Hypixel forum post, and Hypixel does not point to a replacement. So this file uses the two community wikis: the Fandom wiki (hypixel-skyblock.fandom.com, item data read through its page API) and the newer community wiki at hypixelskyblock.minecraft.wiki (for changes from 2026). Numbers are as of about September 2026 (SkyBlock 0.26 to 0.27). Hypixel rebalances often; the July 2026 healing rework, for example, cut several Vitality accessories.

**Naming warning.** In July 2026 Hypixel renamed its bag score from **Magical Power** to **Accessory Power**. SkyWynn already uses **Accessory Power** for the bag score and **Magical Power** for spell damage (`SkyyGear-Plan.md` locks 102 and 112). In this file, **AP always means the bag score**, whichever name the wiki used.

**In one breath:** accessories are small, passive items that work from your inventory or your Accessory Bag. Each one belongs to a family. Only the highest tier of a family counts, so you collect *different* families, not copies. Each family climbs Talisman → Ring → Artifact → Relic, and each step is one rarity higher, gives a bigger effect, and adds more AP to the bag. The AP total then powers one stat bundle you choose (a "Power") and a pool of tuning points. There are about **147 families** (0.27). A full, maxed bag is about **2,121 AP**.

---

## 1. The Accessory Bag and the core rules

| Rule | What it means | Tag |
|---|---|---|
| Where they work | In your inventory or in the Accessory Bag. Not in the Ender Chest, backpacks, the vault or island chests | VERIFIED |
| One of each | Two copies of the same accessory do not stack. Neither the effect nor the AP counts twice | VERIFIED |
| Highest tier only | If you hold several tiers of one family (say the Feather Talisman, Ring and Artifact), only the highest counts, for both its effect and its AP. Lower tiers are dead weight | VERIFIED |
| One exception | Personal Compactors and Personal Deletors: every tier's ability runs at once (each has its own settings), but only one of them gives AP | VERIFIED |
| Why the rule exists | Early on, bugs let tiers stack. The Zombie Talisman, Ring and Artifact together gave 30% damage reduction until a fix in October 2021. Now the top tier gives 15% | VERIFIED |
| Worn on the head | An accessory with a head texture can be worn as a hat. That gives its stats but no AP, and not twice if it is also in the bag. "Hatcessories" (party hats) are the one kind that count twice | VERIFIED |
| Bag slots | Since July 2026 everyone starts with **9 slots**. More come from the Redstone collection (cut to 9 tiers in July 2026), an NPC Redstone quest (+4), Community Center account upgrades (+12), buying 2 slots at a time from the NPC Jacobus (up to +198, about 1.76 billion coins to max), and a late-game attribute (+10) | VERIFIED |
| Dungeon accessories | Some accessories are marked "Dungeon Accessory". They give **double AP inside dungeons** | VERIFIED |
| Reforges | Accessories used to take reforges (small stat add-ons). In April 2022 those were switched off and replaced by the Power system (section 4) | VERIFIED |

## 2. Rarity per tier

- The usual line is **Talisman → Ring → Artifact → Relic**, and each step is **one rarity up**. Newer lines go past Relic to **Heirloom**, and one Rift line goes further still (Chronomicon, then Celestial Starstone).
- A line does **not** have to start at Common. It starts where its source sits in the game:
  - Speed, Zombie, Feather: start at Common (early, cheap).
  - Spider, Wolf, Red Claw: start at Uncommon (first slayer levels).
  - Bat, Treasure, Scarf's: start at Rare (rare drop or dungeon loot).
  - Ender, Wither, Tarantula: start at Epic (auction or boss drop), top out at Legendary.
- Some lines break the pattern: the Master Skull has 7 tiers over 5 rarities (two tiers share Common, two share Uncommon). The Ring of Love quest chain has 10 steps over 5 rarities. A few lines keep the same rarity for every tier.
- Many great items have **no line at all** (single accessories), such as the Night Vision Charm or the Experience Artifact.
- The name tells you the tier. Players read "Artifact" and know it is the third step, before they even check the colour.

## 3. Real upgrade lines, grouped by what they do

Stat names are SkyBlock's. For scale: SkyBlock players start at **100 Health and 100 Speed** (Speed is a percentage of normal walking speed, so **+1 Speed = +1% movement speed**). Strength starts at 0, and each point adds 1% melee damage. Intelligence adds max mana (SkyBlock's mana stat). Crit Damage is a percentage. So an accessory's stat is small on purpose; the bag works because you carry dozens of them.

Tier cells read **Rarity, effect, how you get it**. C/U/R/E/L/M/D = Common, Uncommon, Rare, Epic, Legendary, Mythic, Divine.

### 3a. Stat boosters

| # | Line | Tier 1 | Tier 2 | Tier 3 | Tier 4+ | Tag |
|---|---|---|---|---|---|---|
| 1 | **Speed** | Talisman: C, +1 Speed, craft (Sugar Cane II) | Ring: U, +3, craft (Sugar Cane V) | Artifact: R, +5, craft (Sugar Cane VIII) | Relic (added 2026): E, +7 Speed and +1 each of Attack Speed, Fishing Speed, Mining Speed, craft with a rare crop drop | VERIFIED |
| 2 | **Shark Tooth Necklace** (Strength) | Raggedy: C, +2 Strength | Dull: U, +4 | Honed: R, +6 | Sharp: E, +8. Razor-sharp: L, +10. Every tier also adds 5/10/15/20/25% shark-tooth drop chance in the fishing event. Higher tiers are crafted from teeth of rarer event sharks | VERIFIED |
| 3 | **Red Claw** (Crit Damage) | Talisman: U, +1% Crit Damage, craft (Wolf Slayer 1) | Ring: R, +3%, craft (Wolf Slayer 5) | Artifact: E, +5%, craft (Wolf Slayer 5 plus a boss drop egg) | – | VERIFIED |
| 4 | **Bat** (Health, Intelligence, Speed) | Talisman: R, +1 of each, 1% drop from Bats | Ring: E, +3 Health, +2 Int, +2 Speed, event shop (Halloween candy) | Artifact: L, +5 Health, +3 Int, +3 Speed, event shop | – | VERIFIED |
| 5 | **Lush** (Health) | Talisman: U, +1 Health, craft from a zone plant | Ring: R, +3 Health, craft | Artifact: E, +5 Health and +1 Health Regen, craft | – | VERIFIED |
| 6 | **Draconic** (Health plus dragon damage) | Talisman: U, +1 Health, +2% damage to dragons, craft (End drops) | Ring: R, +2 Health, +3% | Artifact: E, +3 Health, +5% | – | VERIFIED |
| 7 | **Night Crystal / Day Crystal** (Strength and Defense by time of day) | Night Crystal: R, +5 Strength and Defense at night, craft (Nether Quartz VII). Day Crystal: R, same by day | Moonlight Crystal: E, +10 at night (Moonflower VIII). Sunshine Crystal: E, +10 by day (Sunflower VIII) | – | – | VERIFIED |
| 8 | **Crux** (Intelligence; Rift only) | Talisman: C, +10 s Rift time | Ring: U, +2 Int | Artifact: R, +5 Int | Relic: E, +7. Heirloom: L, +10 Int, +1 Speed. Chronomicon: M, +15 Int, +2 Speed. Celestial Starstone: D, +20 Int, +3 Speed. Each tier is crafted from drops of a *new, harder mob type* | VERIFIED |
| 9 | **Cat → Lynx → Cheetah** (Speed) | Cat: U, +1 Speed, race reward | Lynx: R, +2, harder race | Cheetah: E, +3, harder race | – | VERIFIED |
| 10 | **Healing** (Vitality, which boosts healing received) | Talisman: C, +2 Vitality, craft (Lily Pad III) | Ring: U, +4, craft (Lily Pad VIII) | – | – | VERIFIED (cut from 5 and 10 in July 2026) |
| 11 | **Master Skull** (Health % and Strength %, hard mode only) | Tier 1: C, +1% | Tier 2: C, +2%. Tier 3: U, +3% | Tier 4: U, +4%. Tier 5: R, +6% | Tier 6: E, +8%. Tier 7: L, +10%. Drops from hard dungeon floors; **4 of one tier craft the next** | VERIFIED |
| 12 | **Blood God Crest** (Strength that grows) | Crest: C, +1 Strength for every digit of its mob-kill counter, NPC shop | Sigil: U, upgrade | – | – | VERIFIED |
| 13 | **New Year Cake Bag** (Health from collecting) | Single: U, +1 Health per *different* yearly event cake stored inside (54 max), event NPC | – | – | – | VERIFIED |
| 14 | **Melody's Hair** (Intelligence) | Single: E, +6 Int, reward for mastering a music minigame | – | – | – | VERIFIED |

### 3b. Combat utility (damage against, or protection from, mob types)

| # | Line | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tag |
|---|---|---|---|---|---|---|
| 15 | **Zombie** (Undead) | Talisman: C, −5% damage taken from Undead, NPC shop (500 coins) | Ring: U, −10%, craft (Zombie Slayer 2) | Artifact: R, −15%, craft (Zombie Slayer 7, boss drops) | – | VERIFIED |
| 16 | **Spider** (Arthropods) | Talisman: U, −5% from spiders and silverfish, mini-boss drop | Ring: R, −10% from Arthropods, craft (Spider Slayer 1) | Artifact: E, −15%, craft (Spider Slayer 7; the newer wiki says 6) | – | VERIFIED (level UNVERIFIED) |
| 17 | **Wolf** (Animals) | Talisman: U, −5% from Animal mobs, rare drop from Old Wolves | Ring: R, −10%, craft | – | – | VERIFIED |
| 18 | **Ender** | Artifact: E, −20% from Ender mobs, rare auction | Relic: L, −25%, craft (Enderman Slayer 7) | – | – | VERIFIED |
| 19 | **Wither** | Artifact: E, −20% from Wither mobs, rare auction | Relic: L, −25%, craft | – | – | VERIFIED |
| 20 | **Sea Creature** | Talisman: C, −5% from sea creatures, craft (Sponge IV) | Ring: U, −10% (Sponge VI) | Artifact: R, −15% (Sponge VIII) | – | VERIFIED |
| 21 | **Skeleton Talisman** | Single: C, −5% from Skeletons, NPC shop (500 coins) | – | – | – | VERIFIED |
| 22 | **Runeblade** (axe damage vs forest mobs) | Talisman: C, axes deal +5% to Woodland mobs, **mob drop** (two ice mobs) | Ring: U, +10%, craft | Artifact: R, +15%, craft | – | VERIFIED |
| 23 | **Tarantula** | Talisman: E, every 10th melee hit on the same enemy deals +10%, rare slayer-boss drop | Ring: L, +15%, craft | – | – | VERIFIED |
| 24 | **Burststopper** | Talisman: R, a hit worth at least half your Health is multiplied by 0.95, +1 Strength (Blaze Slayer 3) | Artifact: E, ×0.9, +2 Strength, +3 True Defense (Blaze Slayer 7) | – | – | VERIFIED |
| 25 | **Intimidation** (weak mobs ignore you) | Talisman: C, level 1 monsters stop targeting you, NPC shop (10,000 coins) | Ring: U, level 5 and below | Artifact: R, level 25 and below, event shop | Relic: E, level 30 and below, craft | VERIFIED |

### 3c. Gathering, skills and XP

| # | Line | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tag |
|---|---|---|---|---|---|---|
| 26 | **Titanium** (Mining Speed) | Talisman: U, +15, forged from a refined ore | Ring: R, +30 | Artifact: E, +45 | Relic: L, +60. Each tier gated by the mining skill tree tier | VERIFIED |
| 27 | **Haste** | Ring: R, permanent Haste II, craft (Cobblestone VII) | Artifact: E, craft (Cobblestone IX) | – | – | VERIFIED |
| 28 | **Mineral** (Mining Fortune) | Talisman: R, +3 | Glossy: E, +6 | – | – | VERIFIED |
| 29 | **Anita's** (Farming Fortune) | Talisman: C, +5, bought with farming-contest medals | Ring: U, +15 | Artifact: R, +25 | – | VERIFIED |
| 30 | **Cropie → Squash → Fermento → Helianthus** (crop fortune) | Cropie Talisman: C, +10 fortune on 3 crops | Squash Ring: U, +20 on 6 crops | Fermento Artifact: R, +30 on all crops | Helianthus Relic: E, +40 Farming Fortune. **Each tier needs a rarer crop drop** | VERIFIED |
| 31 | **Agarimoo** (fishing) | Talisman: C, +1 Fishing Speed | Ring: U, +2, +1 Fishing XP bonus | Artifact: R, +3, +1 Fishing and Farming XP bonus | – | VERIFIED |
| 32 | **Emperor's** (Sea Creature Chance) | Talisman: U, +0.5%, **4 skull drops** craft it | Ring: R, +1%, **4 Talismans** craft it | Artifact: E, +1.5% | – | VERIFIED |
| 33 | **Potion Affinity** | Talisman: C, potions last 10% longer (Nether Wart III) | Ring: U, +25% (VII) | Artifact: R, +50% (IX) | – | VERIFIED |
| 34 | **Scarf's** (dungeon class XP) | Studies: R, +2%, **dungeon loot chests** | Thesis: E, +4%, **4 Studies** | Grimoire: L, +6%, **4 Theses** | – | VERIFIED |
| 35 | **Hunter** (combat XP) | Talisman: U, +2 Combat Wisdom | Ring: R, +5 | – | – | VERIFIED |
| 36 | **Personal Compactor** | 4000: U, auto-compacts 1 item type | 5000: R, 3 types | 6000: E, 7 types | 7000: L, 12 types | VERIFIED |
| – | Singles | **Experience Artifact** (E, +25% XP orbs). **Treasure Talisman** (R, +1% extra dungeon chest loot) → Ring (E, +2%, 8 Talismans) → Artifact (L, +3%, 9 Rings) | | | | VERIFIED |

### 3d. Movement and utility

| # | Line | Tiers | Tag |
|---|---|---|---|
| 37 | **Feather** (fall damage) | Talisman: C, fall 5 more blocks safely (Feather IV). Ring: U, 7 blocks, −5% fall damage (VII). Artifact: R, 10 blocks, −15% fall damage (IX) | VERIFIED |
| 38 | **Zone speed talismans** (singles) | Mine Affinity: C, +25 Speed in mining zones, NPC (2,500 coins). Village Affinity: C, +10 Speed in the village, NPC (2,500). Farming Talisman: C, +10 Speed on farm islands (Wheat VII). Wood Affinity: U, +10 Speed in forest zones (Oak Log VII) | VERIFIED |
| 39 | **Race rewards** (Speed singles) | Wolf Paw, Pig's Foot, Grizzly Paw: +1 Speed each, beat a timed race. Frozen Chicken: R, +1 Speed → Fried Frozen Chicken: E, +1 Speed, +1 Heat and Cold Resistance | VERIFIED |
| 40 | **Hazard immunity and comfort** (mostly singles) | Fire Talisman: C, fire immunity (Blaze Rod IV). Lava Talisman: U, immune to most lava. Night Vision Charm: C, permanent Night Vision. Magnetic Talisman: U, 3× pickup range. Vaccine: C/U/R, poison −10/−25/−50%. Respiration and Pressure lines: C/U/R, longer breath and deep-water pressure resistance, bigger each tier (exact Respiration numbers differ between wikis) | VERIFIED (Respiration numbers UNVERIFIED) |

There is **no jump-height accessory** in SkyBlock. Jumping comes from boots and potions there.

### 3e. Starters (the cheap first dozen)

These are what a new player fills the first 9 slots with. Each is 3 to 5 AP and costs almost nothing.

| Accessory | Cost | Effect |
|---|---|---|
| Zombie Talisman, Skeleton Talisman | 500 coins each, NPC | −5% damage from that mob type |
| Mine Affinity, Village Affinity | 2,500 coins each, NPC | +25 / +10 Speed in one zone |
| Intimidation Talisman | 10,000 coins, NPC | Level 1 mobs ignore you |
| Scavenger Talisman → Ring → Artifact | 10,000 coins, NPC | Monsters drop a few coins (0.5 per mob level) |
| Speed Talisman | 108 Sugar Cane | +1 Speed |
| Talisman of Coins → Ring → Artifact → Relic | 20 Emerald + 5 Gold | Coins sometimes pop up around you |
| Healing, Feather, Potion Affinity, Vaccine, Fire, Night Vision, Farmer Orb | Early collection crafts | Small comfort perks |

The community guide says to start with the comfort ones (Lava, Fire, Night Vision), then buy by **coins per AP** rather than by rarity.

### 3f. Progressive accessories (one item that levels up in place)

- **Campfire Badge:** 5 rarities (Initiate → God) earned by repeating a trial. Heals you while you burn.
- **Ring of Love:** a quest chain of 10 steps, from a Common rock to a Legendary ring. Each step needs a different odd task.
- **Beastmaster Crest:** C → L, grows with kills of one event mob type.
- **Pesthunter line:** Badge U → Ring R → Artifact E → Relic L. Bought with 25/50/100/200 of a pest-kill currency for +20/40/60/80 bonus pest chance.
- **Gift Talismans:** White C → Green U → Blue R → Purple E → Gold L. +5/10/15/20/25% rewards from winter gifts. Bought with event currency.

## 4. How AP scales with rarity (short)

| Rarity | C | U | R | E | L | M | D | Special | Very Special |
|---|---|---|---|---|---|---|---|---|---|
| AP | 3 | 5 | 8 | 12 | 16 | 22 | 28 | 3 | 5 |

- A Legendary is worth about **5×** a Common. So a Common talisman is cheap AP, and upgrading a line pays twice: a better effect **and** more AP.
- AP turns into a multiplier: `29.97 × (ln(0.0019 × AP + 1))^1.2`. It rises fast, then flattens:

| AP | 100 | 250 | 500 | 1,000 | 1,500 | 2,000 |
|---|---|---|---|---|---|---|
| Multiplier | 3.7 | 9.6 | 18.5 | 32.3 | 42.9 | 51.4 |

- That multiplier scales your chosen **Power** (a fixed stat bundle picked at the NPC Maxwell; more Powers unlock at Combat 15 or by handing in 9 of one Power Stone). Stone Powers also have a small bonus that does not scale.
- **Tuning:** every 10 AP gives 1 tuning point. You spend points on Health, Defense, Speed, Strength, Crit Damage, Crit Chance, Attack Speed or Intelligence, and you can refund them for free.
- Special cases: the Hegemony Artifact gives double its own AP. The Rift Prism gives 11. Phone-case accessories give +1 AP per 2 phone contacts. Each point of AP also gives 1 SkyBlock XP.
- For comparison, SkyWynn's lock 112 is a flat **+10 to +25** AP by rarity. That is a ratio of 2.5× rather than Hypixel's 5×, so commons would matter more in SkyWynn.

## 5. Enrichments and the Recombobulator (one paragraph)

The **Recombobulator 3000** is a rare dungeon-chest item (about 6 million coins to claim) that raises one item's rarity by one step, once per item. On an accessory it only means more AP: C→U +2, U→R +3, R→E +4, E→L +4, L→M +6. Recombobulating the whole bag is a classic late-game coin sink. **Enrichments** go on Legendary-or-higher accessories only, one per accessory, and cost 5,000 Bits each (a shop currency). Each adds one small stat: Speed +1, Intelligence +2, Crit Damage +1, Crit Chance +1, Strength +1, Defense +1, Health +3, Magic Find +0.5, Ferocity +0.3, Sea Creature Chance +0.3, Attack Speed +0.5. An Enrichment Swapper changes every enrichment in the bag at once, so players can respec without buying new ones. About 63 accessories can be enriched.

## 6. What makes the system fun

1. **Collecting.** "One of each" means breadth, not grinding copies. Every new family is a small win. Players chase "missing accessories" lists, and community tools show which ones you lack.
2. **Every system feeds the bag.** Collections, slayers, dungeons, races, events, quests, NPC shops, the forge and fishing all hand out accessories. Whatever you like doing, it moves your bag forward.
3. **Cheap early tiers.** A 500-coin talisman is a real upgrade on day one. The first 9 slots fill in an hour.
4. **Visible upgrades.** The name changes (Talisman → Ring → Artifact → Relic), the rarity colour changes, the number goes up, and the AP total goes up. Four signals for one craft.
5. **Upgrade = double reward.** A better effect *and* more AP, so even a niche line (Candy, Feather) is worth climbing.
6. **Small numbers, big total.** +1 Speed is nothing, but 50 small items plus the Power multiplier are a large part of a late player's stats.
7. **Long goals.** Top tiers (Relics, Master Skull 7, Razor-sharp) are weeks of play. They double as trade goods on the auction house.
8. **Choice on top of collection.** The Power and tuning let two players with the same bag play differently.
9. **Surprise drops.** Some tier 1s drop from mobs (Wolf Talisman, Bat Talisman, Runeblade, Tarantula), so a normal fight can suddenly start a new line.

**What goes wrong in Hypixel (worth avoiding):**

- Many accessories are only AP sticks, with an effect nobody cares about (candy drop chance outside the event, 1-in-a-trillion damage rolls). Players feel they are buying numbers, not items.
- The late game is a coin wall: bag slots cost about 1.76 billion coins, the Hegemony Artifact at least 100 million, and every Recombobulator millions more.
- Old stacking bugs forced later fixes that felt like nerfs.
- Mob-specific protection lines (Zombie, Spider, Wolf) become forgettable once the numbers are small next to armor.

## 7. Patterns worth copying

1. **Talisman → Ring → Artifact → Relic naming**, one rarity step per tier. It fits SkyWynn locks 63 to 65 (the next rarity needs the previous one as an ingredient) as it stands.
2. **Highest tier of a family counts, copies never stack.** Build it into the bag code from day one, so no stacking bug ever needs a nerf later.
3. **Start each line at the rarity of its source.** Starter crafts at Common, slayer and boss lines at Uncommon or Rare, rare chest finds at Epic. Not every line needs to reach Legendary.
4. **Simple stat ramps** players can guess: +1/+3/+5/+7 (Speed), +2/+4/+6/+8/+10 (Strength), 5/10/15% (protection). Give the top tier a small bonus stat (like the Speed Relic's Attack Speed or the Lush Artifact's regen).
5. **Stat mapping for SkyWynn:** SkyBlock Speed is already a percentage (+1 Speed = +1% move speed), so Skyy's "+% movement speed" and lock 25's flat Speed are the same idea. SkyBlock Intelligence maps to SkyWynn mana (+% mana on dedicated mana accessories, lock 88). Health, Strength, Crit Chance, Crit Damage, Ferocity and Attack Speed map one to one. **Check first:** lock 27 keeps Stamina Regen off accessories "unless Skyy says later". Skyy's "+stamina" request may be that say-so, or it may mean max stamina, which no lock covers yet.
6. **"Combine 4 (or 8, or 9) copies to make the next tier"** (Master Skull, Scarf's, Emperor's, Treasure). This is perfect for mob drops and loot chests, and it turns duplicate drops into progress instead of junk.
7. **Each tier needs a drop from a new, harder mob or zone** (Crux line, Cropie line, Shark Tooth). The line becomes a map of the world and pulls players into new areas.
8. **Tier 1 as a rare mob drop, higher tiers crafted** (Wolf, Spider, Bat, Runeblade). The lucky drop hooks the player, and the crafting gives them a goal.
9. **Cheap zone-limited talismans** (+25 Speed only in mines, +10 only on farms). They make great starters and loot-chest fillers without breaking combat balance.
10. **Mob-type protection or damage lines** tied to SkyWynn's own mob families (undead, spiders, beasts, void). Keep the numbers big enough to feel (15 to 25% at the top) or they get ignored.
11. **Growing accessories** (Blood God Crest: +1 Strength per digit of your kill count; the Campfire Badge; the New Year Cake Bag's +1 Health per different cake). They reward long play, and one item can hold a whole mini collection.
12. **Time-of-day or conditional pairs** (Night Crystal and Day Crystal). Hytale has a day and night cycle, so this is an easy, flavourful pair.
13. **Hazard and comfort singles** match existing SkyWynn locks: oxygen and swim speed accessories (locks 61 to 62, like Hypixel's Respiration and Pressure lines), fall damage (Feather), fire and lava immunity, night vision. Jump Height is allowed on accessories (lock 28), and Hypixel has no jump accessory, so there is room for a SkyWynn original.
14. **Every accessory should do something you notice.** Avoid Hypixel's pure AP sticks. Even a starter should give a real stat or a comfort perk.
15. **Show the progress:** the AP value on each item (Hypixel added this in July 2026), a "missing accessories" view in the bag, and the next tier's stats in the lore. The Vanilla-UI rules still apply.
