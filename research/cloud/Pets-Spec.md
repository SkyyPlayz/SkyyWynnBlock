# Pets spec draft (launch list)

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 6, 7 and 9.

Cloud draft, 2026-10-02. Paper design; nothing built. Direction: `research/Pets-Idea.md` (agreed 2026-10-01) and `research/Dragon-Pets-Idea.md`
(dragons are the top tier, later). Creature model ids are **UNVERIFIED** (no game files in the cloud).

## 0. What I could check on the web

| Fact | Source |
|---|---|
| SkyBlock pet rarities: Common, Uncommon, Rare, Epic, Legendary, Mythic = pet score 1-6 | search snippet, [SkyBlock pets](https://hypixelskyblock.minecraft.wiki/w/Wolf_Pet) |
| Pets level from skill XP; most XP when you gain XP in the pet's own skill | same snippet |
| Legendary pets usually have 3 perks (some 4-5); Mythic 4 perks; higher rarity = bigger stats and better perks | same snippet |
| Pet score from unique pets gives Magic Find at 10 / 25 / 50 / 75 / 100 / 130 / 175 | same snippet |
| Pet skills in SkyBlock: Combat, Mining, Fishing, Foraging, Farming, Enchanting, Alchemy, Taming | same snippet |
| SkyBlock pet level cap 100 (some 200), exact XP tables per rarity | memory, **UNVERIFIED** (page fetches were blocked) |
| Vanilla Hytale (Update 3, 2026): tameable Bison, Warthog, Boar, Rabbit, Camel, Chicken, Cow, Goat, Horse, Turkey, Skrill, Ram, Mouflon; mountable Horse, Camel, Ram, Mouflon; feed once to tame | search snippet, [Hytale taming guide](https://www.dtgre.com/2026/02/hytale-animal-taming-guide-update-3.html?m=0) |

## 1. Rules (from the locks)

| Rule | Value |
|---|---|
| One pet system | buffs for all, combat for better pets, some are mounts |
| Slots | 1 **active** pet; 1 **mount** slot, unlocked by a quest; only mount pets fit; its buffs work at **50%** (row `pets.mountSlot.buffPercent`) |
| Per profile | yes (PROFILES-CONTRACT) |
| Buff strength | from **rarity and level only**. Fighting/riding are bonuses on top |
| Pet XP | 100% of the XP you gain in the pet's own skill, 20% of XP in other skills (rows). Class pets use your class skill |

## 2. Rarity

| Rarity | Pet score | Stat factor | Perks | Fights? | Notes |
|---|---|---|---|---|---|
| Common | 1 | 0.30 | 1 | no | |
| Uncommon | 2 | 0.45 | 1 | no | |
| Rare | 3 | 0.60 | 2 | from Lv 40 (weak) | |
| Epic | 4 | 0.80 | 2 | from Lv 25 | |
| Legendary | 5 | 1.00 | 3 | from Lv 10 | |
| Mythic | 6 | 1.25 | 4 | from Lv 1, can be flying mount | dragons only |

Stat at level L = (value listed for Legendary Lv 100) x rarity factor x L / 100. Linear, easy to explain and to put in a Server Setup row.
Target (placeholder, balance in a playtest): a Legendary Lv 100 pet adds about as much power as one mid-tier armor piece (10-12% of total). A level-1 pet gives about 1% of that.

Rarity is **bought, not levelled**: a Pet Upgrade Stone raises the rarity by one step (no XP loss), crafted from zone Void Fragments.

## 3. Levels and XP (1-100)

XP to go from level L-1 to L = round(60 x L + 0.04 x L^3), rounded to a nice step. Total to 100 is about **1.28 million pet XP**.
Rarity does not change the XP need (it changes stats); rarer pets simply come with more of the power.

| Level | XP for that level | Total |
|---|---|---|
| 2 | 60 | 60 |
| 5 | 240 | 600 |
| 10 | 570 | 2,770 |
| 15 | 950 | 6,730 |
| 20 | 1,400 | 12,780 |
| 25 | 2,000 | 21,530 |
| 30 | 2,700 | 33,530 |
| 40 | 4,700 | 70,980 |
| 50 | 7,650 | 133,330 |
| 60 | 12,000 | 232,080 |
| 70 | 17,500 | 379,080 |
| 80 | 24,500 | 589,580 |
| 90 | 33,500 | 882,080 |
| 100 | 45,000 | 1,277,580 |

Pacing (assumption, **UNVERIFIED**): class kill XP at x3 is about 5,400 an hour in Zone 1 and 15-36k an hour in Zone 3-4 (see Class-Skill-Curve-Proposal),
so a class pet reaches Lv 100 in roughly 40-90 hours of late-game fighting. Gathering XP per hour is not known in the cloud: the local session should time it,
then change the 60 and 0.04 numbers (both rows). **Treats**: a cooked Pet Treat (Cooking skill gives it a use) gives a lump of pet XP - a use for Cooking, like SkyBlock's pet candy.

## 4. How you get a pet

| Source | What | Rarity |
|---|---|---|
| Starter | one Common Rabbit/Wolf-type pet from the starter shard chain (lore) so everyone has the system | Common |
| Wild taming | vanilla animals are tamed by feeding (works in vanilla). At a **Stable NPC** you can bond a tamed animal as a pet, once per kind | Common / Uncommon |
| Pet Eggs | found in zone chests, dungeon rewards and boss drops; hatch in the Stable (a timer) | rolled by source, up to Epic |
| Legendary | boss/guardian drops, quests | Legendary |
| Dragons | dragon egg quest line (Dragon-Pets-Idea) | Mythic |

Pets are items (like Accessories) stored in a Pet bag/tab; one pet cannot be duplicated; pets can be traded/sold on the AH after Lv 1 (rows). Pet score (unique pets, weighted by rarity) gives small bonuses (placeholder: +1 max Health per 10 score) - optional, can be dropped.

## 5. Launch list (14 pets)

Level 100 Legendary values; the lists are **placeholders** to tune. Stat names follow the SkyyGear catalog (Strength, Crit Chance, Crit Damage, Magical Power) plus Mining / Foraging / Farming Fortune and Defence/Health/Mana already used in SkyySkills.

### 5.1 Skill pets

| Pet | Model (UNVERIFIED) | Skill | Perks at Legendary Lv 100 | Mount? |
|---|---|---|---|---|
| Rabbit | `Rabbit` | Farming | +60 Farming Fortune; +5% crop double-drop; fast crops | no |
| Chicken | `Chicken` | Farming | +40 Farming Fortune; eggs (a small item drop every few minutes, capped); +10 Stamina | no |
| Goat | `Goat` | Mining | +60 Mining Fortune; +10% Mining Speed; no fall damage from ledges | no |
| Warthog | `Warthog` | Mining | +40 Mining Fortune; +15 Defence while below ground; ore finder (shows ore through walls briefly - UI risk, optional) | no |
| Bear (grizzly) | `Bear_Grizzly` | Foraging | +60 Foraging Fortune; trees fall faster; +5 Strength while in forests | no |
| Turkey | `Turkey` | Foraging | +40 Foraging Fortune; +5% sapling chance (works with Saplings From Trees) | no |

### 5.2 General combat pets

| Pet | Model | Perks | Mount? |
|---|---|---|---|
| Wolf | `Wolf` | +20 Strength; +15 Crit Damage; +5% Crit Chance | no |
| Boar | `Boar` | +60 Health; +20 Defence; knockback resistance | no |

### 5.3 Class pets (at least one per class)

| Class | Pet | Model | Perks (Legendary Lv 100) | Mount? |
|---|---|---|---|---|
| Archer | Hawk | `Avian/Raptor/Hawk` (named in Pets-Idea, UNVERIFIED) | +20 Crit Chance; +25 Crit Damage with bows/crossbows; marks one enemy (extra damage) | no |
| Warrior | Ram | `Ram` (vanilla mountable) | +50 Defence; +80 Health; shield-bash blocks reduce 15% more | **yes** |
| Mage | Skrill | `Skrill` | +40 Magical Power; +40 Mana; +10% Mana regen (see Mana-Cost-And-Regen-Research) | no |
| Berserker | Warthog-tusker (use Warthog model, recoloured) | `Warthog` | +30 Strength; +10% attack speed at low health | no |
| Priest | Mouflon | `Mouflon` (vanilla mountable) | +30 Magical Power; healing done +10%; +50 Health | **yes** |
| Assassin / Shaman | later (those classes are not live) | | | |

Note: Warthog appears twice (Mining + Berserker). Use a recoloured Warthog or replace the Mining one with a Bison (`Bison`) if Skyy prefers.

### 5.4 Mount pets (the unlockable slot)

| Pet | Model | Mount perk | Buffs |
|---|---|---|---|
| Horse | `Horse` | +speed; +stamina | +20 Stamina; +5% movement speed |
| Camel | `Camel` | +speed in sand, no desert damage | +30 Stamina; Zone 2 theme |
| Ram | see Warrior | | |
| Mouflon | see Priest | | |

Mount slot unlock: a quest at the Zone 2 town (stable master gives the slot and the first mount pet) - the default in Pets-Idea. Dragons join later as flying mounts.

## 6. Combat rules (engine questions below)

- A fighting pet follows you, attacks the target you hit, does **X% of your weapon damage** (placeholder 10% at Rare Lv 40 up to 30% at Mythic Lv 100), never takes damage and cannot die (it "retreats" on 0 Health for 10 s). That avoids lost-pet frustration and exploits.
- Size grows with level: 0.6x at Lv 1 to 1.0x at Lv 100 (Mythic up to 1.6x).
- A pet's kills count as **your** kills (XP, collections, loot to you); party members' pets never steal credit.
- The mount slot pet only gives its buffs (50%) unless you summon and ride it; it does not fight.
- Pets use no mana or stamina. Hidden in creative/spectator; unsummoned during dungeons only if a dungeon says so.

## 7. Server Setup rows (sketch)

`pets.enabled`, `pets.xp.matchPercent` (100), `pets.xp.otherPercent` (20), `pets.curve.linear` (60), `pets.curve.cubic` (0.04), `pets.rarity.*` (factor / perks / fights-from-level),
`pets.mountSlot.buffPercent` (50), `pets.fight.damagePercent`, per-pet rows (id, model, skill, perks), `pets.trade.minLevel`. Everything editable (PROJECT-RULES 4).

## 8. Build order (matches Pets-Idea)

1. Stat pets (items + active slot + XP + buffs + a vanilla-looking Pets window) - uses the same modifier tricks as SkyyGear/Accessories.
2. Visible follower pet (cosmetic NPC that follows).
3. Combat help. 4. Mount slot + ground mounts. 5. Dragons / flying.

## 9. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Model/role ids for every creature above (Assets.zip, `Server/Models` and `Server/NPC/Roles`); which have friendly (non-hostile) roles. |
| 2 | How vanilla Update-3 taming stores the tamed state, and whether a mod can read "this animal is tamed by player X" to offer the Stable bonding. |
| 3 | An NPC follow behaviour (owner follow) and a "never attack the owner" role we can spawn per player; does the vanilla taming already give a follow behaviour we can reuse? |
| 4 | Ground mount API (vanilla Horse/Camel/Ram/Mouflon mounting) - can a mod grant/summon a rideable creature on demand? |
| 5 | Model scale per entity at runtime (growth with level). |
| 6 | Real XP per hour for each skill, to set the pet XP curve rows. |

## 10. Questions for Skyy

1. Should rarity be bought only with Upgrade Stones (my proposal) or also found as different-rarity eggs? (Proposal covers both.)
2. Pet XP for non-matching skills: 20% OK, or 0 so pets stay skill-specific?
3. Is losing nothing when a fighting pet "dies" (it just retreats) what you want?
4. Do you want pet score bonuses (small global buff for collecting many pets) at launch?
