# Untiered, Mythic and Set gear - design spec (UT weapons, boss loot pools, boss respawn, challenge mode)

Cloud draft, 2026-10-08. Paper design, no code. Everything about the engine is **UNVERIFIED** (no game files in the cloud); every number is a placeholder and a Server Setup row.
Companions: `research/cloud/Own-Specials-Draft.md` (the 21 boss weapons - they become MYTHIC here), `research/Pack-Armor-Plan.md` (The Armory specials + special sets + the fairness table), `research/cloud/Loot-Round-Revision.md` (Mystery Bags, Unclaimed Luggage chests), `research/cloud/Zone-Bosses-Ideas.md`, `research/cloud/Capstone-Dungeon-Spec.md`, `research/cloud/Capstone-Sets.md`, `research/cloud/Slayers-Spec.md` (RNG meter), `research/cloud/Elites-Events-Spec.md`, `research/cloud/SkyyArmory-Roadmap.md` (Lv 50-100 tiers).

## 0. Decisions this follows (`docs/answered/gear.md`, newest wins; not re-decided here)

| Line | Lock | Used here |
|---|---|---|
| 2026-10-08 BIG DIRECTION - UNTIERED + BOSS GEAR (123) | ROTMG-style UT: per level tier one UT weapon of each weapon type + one UT armor set of each armor type, eventually; good in its band but with trade-offs, never strictly better. Boss gear = own tier above the rest, better stats AND a special effect, level can be upgraded LESS; boss-only (a few world drops); fixed loot pools of 3+ weapons and 4-8 armor pieces, often PARTS of sets; full sets early, split later; boss respawn on demand (BL4); optional Challenge mode (x2 difficulty, x2 drop rate) | sections 1, 2, 4, 5 |
| 2026-10-08 RARITY NAMES (124) | UNTIERED = new label, ORANGE; MYTHIC (purple) = all boss gear; SET (green) = normal pieces until ALL 4 are worn, then a full-set buff (e.g. +100 Health), mainly QUEST rewards; many Mythic armor pieces are also sets but STAY purple; Normal -> Fabled stays the random ladder | sections 1.6, 2.1, 3, 7 |
| 2026-10-08 (Skyy, gathering sets) | "yes, gathering armor uses the set label, the full set gives a little bonus gathering fortune (mining foraging ect.) and the higher tiers can give a little more like mining /chopping speed, movement speed, ect." | section 3.2 |
| 2026-10-08 (Skyy, UT sources) | "UT weapons and armor are only mob drops and chest loot (bosses can drop them too.)" + "but you cant craft them." + "they can come from quests, but not shops." | section 1.4 |
| 2026-10-04 (36) | Reforge LEVEL UP cap = +6 over the found / made level, never above the metal's top or your own level, coins per level by level + rarity | section 2.2 lowers it only for Mythic (and UT) |
| 2026-10-08 (121-122) | unidentified items are MYSTERY BAGS, one per rarity (7 bags); loot round defaults all yes (6% mob drop, Unclaimed Luggage chests with coins) | sections 1.5, 5.3 |
| 2026-10-08 (112-119, 122) | Armory specials = boss drops; our own ~18-21 specials; Elementals shelved; Zweihander Warrior, dual swords Assassin | section 2.4 pools |
| 2026-09-30 (47) | "if it's not in the game yet, don't leave it in the reforge list" | every bonus here uses a LIVE stat or is marked (later) |
| 2026-10-05 armor types | Heavy / Light / Cloth, soft rule (anyone wears anything, class bonus on-type) | UT armor sets per type; set bonuses work for everyone |
| `docs/answered/classes.md` 36 + 42 | 2 weapon types per class: Warrior swords + spears, Berserker axes + maces, Assassin daggers + kunai, Mage staffs + spellbooks, Priest wands + soul orb, Archer shortbows + crossbows, Monk Bo + fists | the 14 weapon types of the UT grid |
| Live SkyyGear 0.2.10 (`SkyyGear/build_skyygear_0.2.10.py` RARITIES, ODDS_DEF, RARITY_DEF, LVLUP_CAP_DEF, COST_L_DEF) | 7 rarities Normal #FFFFFF, Unique #FFFF55, Rare #FF55FF, Legendary #55FFFF, Fabled #FF5555, Mythic #CC66CC, Set #55FF55; Mythic today rolls in the random odds (mob 0.5 / chest 0.6 weight) and sits in the Smithing step-up LADDER; `set` document field reserved, no bonus code | section 6.1 lists what changes |

## 0.1 What the research says (web, 2026-10-08; sources after each fact)

| Game | Fact | Source |
|---|---|---|
| ROTMG UT | Untiered items sit outside the T1-T14 ladder: no tier number, fixed stats, mostly **soulbound** (cannot be traded or dropped for others); soulbound loot bags are visible only to the player who earned them | [Steam post on soulbound](https://steamcommunity.com/app/200210/discussions/0/3335371283872775477), [Mad God Mayhem](https://www.realmeye.com/wiki/mad-god-mayhem) |
| ROTMG UT | The classic UT trade-off: the Doom Bow fires ONE slow, very hard shot - bad DPS, great against high-defense targets, long range | [Archer class guide](https://www.realmeye.com/wiki/archer-class-guide/5) (snippet only; numbers UNVERIFIED) |
| ROTMG UT | UTs are dungeon-specific (a dungeon's bosses drop that dungeon's UTs); drop rates are not published (players guess ~1 in 100 for the Doom Bow) | [Mad God Mayhem](https://www.realmeye.com/wiki/mad-god-mayhem), [Steam thread on UT rates](https://steamcommunity.com/app/200210/discussions/0/1470840994962797096) |
| ROTMG ST | A Set Tiered set gives growing bonuses: Mad God's Messenger (Priest) 2 pieces +4 DEX +4 ATT, 3 pieces +5 / +5, **4 pieces +100 HP +6 / +6**; pieces drop from DIFFERENT bosses (wand + robe-ish from Janus / Oryx, armor from the Stone Guardians, ring from the Brute / Commander) and whole sets come from Mystery ST Chests | [Mad God's Messenger Set](https://www.realmeye.com/wiki/mad-god-s-messenger-set) |
| Borderlands 4 | **Moxxi's Big Encore**: after the first kill a machine appears by the arena; pay and the boss respawns on the spot | [Insider Gaming](https://insider-gaming.com/replay-bosses-borderlands-4/) |
| Borderlands 4 | The fee rises with level (about 40,000 at level 50 per one guide); the farming loop = kill, sell junk at the vendor next to it, pay again; a rotating **Weekly Encore boss** has a much higher drop rate and costs Eridium | [KeenGamer farming guide](https://www.keengamer.com/articles/guides/borderlands-4-how-to-farm-legendary-weapons/) |
| Borderlands 4 | Bosses have DEDICATED drops (Splashzone -> Firewerks, Driller Hole -> Fuse + Katagawa's Revenge); other Legendary sources: Rift events, Ripper Drill Sites, Order Bunkers, the Primordial Vault; fan sample of 3,000+ kills: about **5% per dedicated item**, about 4% world drop | same + [GamePro drop-rate article](https://www.gamepro.de/artikel/borderlands-4-niedrig-drop-raten-legendaere-waffen,3440999.html) |
| Borderlands 4 | Patch notes: a permanent Legendary drop-rate increase (2026-01-15); all base, Invincible and Bounty Pack bosses set to the same dedicated drop rate (2026-03-05); Ultimate Vault Hunter mode = much tougher with better loot | [Jan 15 notes](https://support.borderlands.com/hc/en-us/articles/48082786161171-Borderlands-4-Minor-Update-Notes-January-15-2026), [Mar 5 notes](https://support.borderlands.com/hc/en-us/articles/49625933704723-Borderlands-4-Minor-Update-Notes-March-5-2026), [Endgame overview](https://borderlands.2k.com/borderlands-4/news/endgame-overview/) |
| Borderlands 3 (memory, UNVERIFIED) | named bosses ~10% dedicated drop; Mayhem levels raised Legendary rates | - |
| Diablo 4 | Uber bosses are SUMMONED at an altar with materials (e.g. 6 Shards of Agony + 2 Stygian Stones); they have the best Uber Unique odds | [Prima Games](https://primagames.com/?p=263233), [Mobalytics](https://mobalytics.gg/blog/diablo-4/how-to-farm-uber-uniques-season-4/) |
| Path of Exile | Maven's Invitations are crafted keys to a boss arena; only after you were "witnessed" beating the required bosses | [Maxroll](https://maxroll.gg/poe/resources/mavens-invitations) |

Lessons taken: UT = fixed stats + one clear trade-off + a known source (ROTMG); set bonus only at full set, pieces split across bosses (ROTMG ST + Skyy's rule); boss respawn = a paid machine at the arena after the first kill, cost rising with level (BL4); dedicated drops around 5-10% per kill with a harder mode that raises them (BL3 / BL4); a summon that needs a prior "witnessed" kill (PoE / D4) = our Challenge unlock.

## 1. UNTIERED (orange)

### 1.1 What makes a UT

| Rule | Value |
|---|---|
| Fixed stats | no rarity roll, no random modifiers, no Identify, no modifier Reforge. The item is always the same item |
| One clear trade-off | ONE thing much better, ONE thing clearly worse, written in the tooltip in one orange line ("Pierces every enemy in a line. 30% less damage.") |
| Situational | at its level it beats a Fabled of its band in its niche and loses outside it; never strictly better than the random ladder |
| Level | the item level comes from the source (mob / chest / quest level) clamped to the UT's tier band, like all loot; stats scale by level as all gear does (SkyyGear curves) |
| Level up | Reforge LEVEL UP allowed but capped at **+3** (section 2.2) so a UT stays in its band |
| Class gate | its weapon type's class (SkyyClasses weapon table), armor soft rule as usual |
| Trade | tradable and AH-listed (we do not copy ROTMG's soulbound; question 2) |
| Label | rarity "Untiered", ORANGE; shown where the rarity word goes ("UNTIERED STAFF") |

Stat baseline (placeholder): a UT's hidden stat block = the band's **Legendary** baseline (base stats + the fixed trade-off lines). So a lucky Fabled roll can still out-stat it in raw numbers; the UT wins by its trick.

### 1.2 Target grid (types x tiers) - "eventually"

Tiers = the six zone level bands (not the 12 metal bands, which overlap too much for one UT each - question 1). Per tier: **14 UT weapons** (one per weapon type) + **3 UT armor sets** (one per armor type, 4 pieces each) = 26 items; 6 tiers = **156 items eventually**.

| Tier | Band | Zone | Metal bands inside | Weapons (14) | Armor sets (3) |
|---|---|---|---|---|---|
| UT1 | Lv 1-14 | Zone 1 early | Crude / Wood / Leather / Copper | sword, spear, axe, mace, dagger, kunai, staff, spellbook, wand, soul orb, shortbow, crossbow, Bo, fists | Heavy, Light, Cloth |
| UT2 | Lv 15-29 | Zone 1-2 | Iron / Thorium / Cobalt | same 14 | same 3 |
| UT3 | Lv 30-44 | Zone 2-3 | Cobalt / Adamantite / Mithril | same | same |
| UT4 | Lv 45-59 | Zone 3-4 | Mithril / Onyxium / Cindersteel | same | same |
| UT5 | Lv 60-75 | Zone 5 + dragon | Amberite / Drakonite | same | same |
| UT6 | Lv 76-100 | capstone | Voidglass / Aetherium | same | same |

Build order: UT2 first (the first batch below), then UT1 and UT3, then one tier per zone as the zones ship. A tier is "complete" when all 17 slots exist; until then the grid shows gaps (a `/gear ut` admin list).

### 1.3 First batch - 10 concrete UTs (all UT2, Lv 15-29; names in the Department voice)

| # | Item | Type (class) | The trade-off (one line, as the tooltip says it) | Why it is situational | Engine risk |
|---|---|---|---|---|---|
| U1 | **The Loophole** | staff (Mage) | Quick shots pierce every enemy in a line. **30% less damage.** (Skyy's example) | corridors and swarms: yes; a lone boss: no | LOW - the wand pierce shot exists (SkyyArmory), reuse on a staff id |
| U2 | **The Paperweight** | sword (Warrior) | **+50% damage per hit**, two speed tiers slower | armoured single targets: yes; crowds and kiting mobs: no | LOW - speed tiers exist (Weapon-Speed-Tiers) |
| U3 | **Overtime** | axe (Berserker) | **+30% damage while under half Health**; **-10% max Health** | the reckless all-in; a healed party makes it a plain weaker axe | LOW - damage event + a Health check |
| U4 | **The Pocket Knife** | dagger (Assassin) | backstabs **+50%**; hits from the front **-30%** | stealth openers; a face-to-face duel: no | LOW-MEDIUM - reuses the vanilla backstab test |
| U5 | **Short Notice** | shortbow (Archer) | arrows fly **twice as fast and flat**; **range 12 blocks**, -15% damage | close brawls and fast mobs; sniping: no | MEDIUM - arrow speed / gravity per item (UNVERIFIED) |
| U6 | **The Second Opinion** | wand (Priest) | the heal orb heals **x1.5**; wand shots do **-40% damage** | the party healer's wand; solo levelling: no | LOW - heal orb number per item |
| U7 | **The Turnstile** | Bo staff (Monk) | every hit knocks back **x2**; **-25% damage** | crowd control, ledges, keeping adds off the healer; DPS: no | LOW - knockback per hit |
| U8 | **The Filing Cabinet** (4 pieces) | Heavy set | **+25% Health**; **-10% damage dealt** | the tank set; a damage dealer loses | LOW - set-level lock modifiers |
| U9 | **The Courier's Leathers** (4 pieces) | Light set | **+15% move speed, +5% crit chance**; **-20% Defense** | runners, kiters, lootrunners; standing fights: no | LOW |
| U10 | **The Intern's Robes** (4 pieces) | Cloth set | **+50% Mana regen**; **-20% max Health** | spell spam; anything that hits you: no | LOW |

Spare ideas for the empty UT2 slots (spear "The Long Reach": +1 block reach, -20% damage - reach UNVERIFIED; crossbow "The Rubber Band": bolts return as ammo, -25% damage; soul orb "The Short Fuse": Bindings fill twice as fast, half the stored healing cap; spellbook "The Pamphlet": spells cost half Mana, -35% spell damage; kunai "The Boomerang": thrown kunai always return, -30% damage; fists "The Soft Touch": combo gaps halved, -30% damage; mace "The Gavel": every 5th hit stuns 1 s, -20% damage).

### 1.4 Where UTs drop (LOCKED 2026-10-08: mob drops, chest loot, bosses, quests; never crafted, never shops)

Skyy: "UT weapons and armor are only mob drops and chest loot (bosses can drop them too.)" + "but you cant craft them." + "they can come from quests, but not shops." So: **never** crafted, never sold in an NPC shop (the AH / player trade is fine - question 2). Each UT names which mobs, chests, bosses or quests carry it (ROTMG: you know where to farm it); the table `ut.<id>.sources` lists mob families / zones, chest kinds, boss roles and quest ids. A UT drops **identified** (orange name, no bag - there is nothing to roll; question 3).

| Source | Rule | Server Setup row |
|---|---|---|
| **Mob drops** (levelled kills whose level is inside the UT's tier band) | the extra drop roll (6%, loot round) is a UT instead of a bag at **1%** of those rolls (about 1 UT per 1,700 kills); the UT's own mob list leans it (e.g. The Pocket Knife from Zone 1 bandits / Trorks x4 weight) | `ut.mob.share` |
| **Elites** (3% spawns, guaranteed gear roll) | the elite's gear roll is a UT of the zone's tier at **3%** (two-affix elites 6%) | `ut.elite.chance` |
| **Loot chests**: vanilla world chests (the LOCKED 1-in-3 extra piece), **Unclaimed Luggage** I-IV, dungeon end chests, event chests | the extra piece / a box is a UT at: vanilla chest 1%, Luggage I 0.5% / II 1% / III 3% / IV 8%, dungeon end chest 8%, event chest 2% (the chest's zone tier) | `ut.chest.<kind>` |
| **Bosses** (guardians, dungeon bosses, slayer bosses) | a boss pool may carry 1-2 UTs of its tier as a separate **5%** line next to the Mythic roll (a cheap consolation drop) | `boss.<role>.ut` |
| **Quests** | a quest may hand out a UT as a fixed reward (identified): proposal ONE per zone, a "pick one of three" step (a UT weapon of your class or a UT armor piece) | quest data (SkyyQuests) |

A UT is never a Mystery Bag, never a recipe and never in an NPC shop; the hourly mob-loot cap (20) counts UT drops too.

### 1.5 No rarity roll - how the item is made

The UT id is in a table `ut.<id>` = `type, class, tier, lo, hi, tradeoff lines, sources`. When a source grants it, SkyyGear writes the document with rarity `untiered`, level = source level clamped to `lo..hi`, the fixed lock modifiers from the table, `id:true`. Appraiser step-up, the Smithing craft rarity, migrate and craft odds never produce `untiered` (ODDS row = 0 everywhere). `/gear rarity untiered` only works on ids in the table.

### 1.6 How SkyyGear shows them

| Place | Shown |
|---|---|
| Rarity colour | an **8th quality asset** "Untiered", TextColor orange (**#FFAA00**; check contrast on the tooltip panel like Mythic's #CC66CC fix - UNVERIFIED), tooltip frame = the vanilla Legendary (gold) frame set, slot texture Legendary, drop particle Drop_Legendary |
| Name line | "UNTIERED STAFF - Lv 20 - Requires Sorcery 20" |
| Body | base stats as usual; then ONE orange line with the trade-off; no "unidentified", no modifier list |
| Identify page | never lists a UT |
| Reforge page | modifiers tab greyed ("Fixed stats"); Level up tab works, cap +3, cost row `cost.levelUp.untiered` (1,500 + 300 per level, placeholder) |
| AH | category "Untiered" |
| Stats page / Wardrobe | orange name as everywhere |

## 2. MYTHIC (purple) - boss gear

### 2.1 What a Mythic is

| Rule | Value |
|---|---|
| Who | all boss gear: The Armory specials (Hepta Axe, Lahat Chereb, Rune Blade stages, Dual Rune Blade, Ghost Sword, Zweihander; the 4 Elementals when the element system exists), our 21 drafted specials (`Own-Specials-Draft.md`), the Armory special sets (Pack-Armor-Plan 3.2 item 3), the capstone uniforms (question 11) |
| Stats | **above Fabled**: base stats x1.10 of a Fabled at the same level, modifiers from the live Mythic row (6 modifiers rolled 60-130%; Fabled = 5 at 50-110%) |
| Special effect | every Mythic has ONE hook (the "special": a weapon twist or an armor set buff) - never a class ability or a signature |
| Level | = the boss's level (Lv 20 / 30 / 45 / 60 / 70 / 79-97) |
| Rarity | fixed `mythic`; never from the random ladder (section 6.1 removes Mythic from ODDS and from the Smithing step-up LADDER) |
| Drop | boss-only (section 2.3 pools) + a few world drops (2.5); arrives as the purple **Mythic Mystery Bag** tagged with the boss pool; identify picks the item from that pool (lean, section 5.1) and rolls the modifiers |
| Re-roll | the bag re-roll (Loot-Round-Revision 2) works inside the same boss pool (x5 cost, max 3) - a coin dial for "I want the other piece" |
| Trade | tradable, AH category "Mythic" |

### 2.2 The lower level-up cap

Today: LVLUP_CAP_DEF = 6 for every rarity. Make it a per-rarity row `levelUp.cap.<rarity>`:

| Rarity | Cap | Cost per level (live COST_L_DEF; UT new) |
|---|---|---|
| Normal, Unique, Rare, Legendary, Fabled | **+6** (LOCKED 2026-10-04, unchanged) | as live |
| Set | **+6** (a quest Cobalt set should age like Cobalt) | live (1,000 + 200) |
| Untiered | **+3** | 1,500 + 300 (new) |
| **Mythic** | **+2** | live (4,000 + 800) |

Why +2: a Lv 20 Mythic is already a Lv 22 item's worth of stats (x1.10 + the hook); at +2 it carries to the next band's start and then you farm the next boss - Skyy's "cannot have their level upgraded as much". Still "never above the metal's top or your own level".

### 2.3 Boss loot pools - the rules

| Rule | Value |
|---|---|
| Pool size | **3+ weapons** and **4-8 armor pieces** per boss (Skyy). Early bosses that have fewer named weapons today carry "TBD" slots filled by the next specials draft (about 20 more weapons are needed for 14 bosses x 3; until then a weapon may sit in TWO neighbouring pools) |
| Armor pieces | often PARTS of different sets: e.g. the Hands + Legs of a Cloth, a Light and a Heavy set in one boss, the rest in another |
| Early / late | Zone 1 bosses carry FULL sets; Zone 2 half-and-half; Zone 3+ a set is split over 2-3 bosses (+ the weapon on a third) |
| Full set = all pieces the set defines | 4 slots normally (Head / Chest / Hands / Legs - vanilla has no boots, UNVERIFIED); an Armory set with 3 slots (Jester: no Hands) is full at 3 |
| Mythic set bonus | applies only with the full set; the pieces stay PURPLE (rarity `mythic`, `set` field = the set id); partial bonuses: none (question 10) |
| Looks | Armory pieces = their models (CC BY-NC, credited, their files untouched); the item's level / stats / rarity are ours at runtime |
| Config | `boss.<role>.pool` = list of `id:weight`; `boss.<role>.ut`; one Server Setup table per boss |

### 2.4 Sample pools - the first six bosses

Levels from Zone-Bosses-Ideas / Slayers-Spec; weapons from Own-Specials-Draft section 9 + Pack-Armor-Plan 3.3 b; Armory sets from Pack-Armor-Plan 1.2 (their "Lv" is ignored - a Mythic's level is the boss's). "TBD" = a weapon for the next specials draft. Set buffs use live stats only.

| Boss | Lv | Weapons (3+) | Armor pieces (4-8) | Set rule |
|---|---|---|---|---|
| **The Second-Page Guardian** (Zone 1 guardian, Earthen Golem) | 20 | P1 The Courtesy Copy (wand), R1 The Filing Spike (shortbow), TBD Warrior sword | **Rook set FULL 4** (Heavy): Helm, Chest, Hands, Legs; **Warden set FULL 4** (Light) | full sets early. Rook 4/4: +100 Health. Warden 4/4: +10% projectile resist, +8% crit chance |
| **Burnt Skeleton Praetorian** (Zone 1 slayer "The Late Fee") | 20 | A1 The Fine Print (daggers), Ghost Sword (Warrior), Rune Blade stage 1 (Berserker) | **Ghost Rook pieces FULL 4** (Heavy, no recipe in The Armory - the natural undead drop), Skull Mask (Light head, loose piece) | Ghost Rook 4/4: +12% Health regen at night (night = later stat; until then +80 Health) |
| **Trork Chieftain** (Zone 1 dungeon boss) | 20-23 | Hepta Axe (Berserker), TBD Monk fists, TBD Priest soul orb | **Jester set FULL 3** (Light: Head, Chest, Legs - no Hands in their set), Tribal Mask (Cloth head), Scarecrow (Cloth head) | Jester 3/3: +10% move speed, +4% crit chance |
| **The Broodmother** (Zone 2 guardian) | 30 | M1 The Long Form (staff - see question 6), K1 The Long Queue (Bo), TBD Archer crossbow | **Cobalt Dragon Head + Chest** (Heavy, half), **Priest set Chest + Legs** (Cloth, half), Potion Bandolier (Cloth chest, loose) | split starts: the other halves are at Goblin Duke / Scarak Overseer |
| **Goblin Duke** (Zone 2 goblin dungeon) | 30-33 | Lahat Chereb (Berserker), TBD Assassin kunai, TBD Mage spellbook | **Calvary set FULL 4** (Heavy), **Cobalt Dragon Hands + Legs** (Heavy, the other half) | Calvary 4/4: +120 Health, +5% crit damage. Cobalt Dragon 4/4 (needs Broodmother + Duke): +150 Health, +10% Defense |
| **Scarak Overseer** (Zone 2 slayer "The Exterminator") | 30 | R2 The Rubber Stamp (crossbow), TBD Warrior spear, TBD Priest wand | **Priest set Head + Hands** (Cloth, the other half), Scorpion Helm (Heavy head, loose), Crown (Heavy head, loose), Amulet (Cloth chest, loose) | Priest set 4/4 (Broodmother + Overseer): +60 Mana, +25% Mana regen |

Later pools (sketch, same rules): Everfrost Yeti Lv 45 = Dual Rune Blade, M2, P2 + Academy Chest + Hands, Daemon Head + Legs; Outlander Chief = A2, K2 + Academy Head + Legs, Grand Lich Hood; Outlander Colossus (slayer) = W1 + Daemon Chest + Hands; Ember Warden Lv 60 = M3, P3, K3 + Cindersteel-tier Mythic sets (ours, 2 of 3 types split with Cave Rex); Cave Rex = R3, W2, Zweihander (moved from Golem_Firesteel if that boss is not used); the Dragon Lv 70 = A3 + Drakonite Mythic set pieces; Final Audit F1-F3 = K4, M4, R4 + the Bailiff / Clerk / Notary uniforms split across floors (question 11).

### 2.5 World drops (the "few exceptions")

| Item | Source | Chance |
|---|---|---|
| Ghost Sword (Warrior) | any undead ELITE at night, Zone 1-3 | 1% of the elite roll |
| Skull Mask (Light head) | any Skeleton_* kill Lv 15+ | 0.05% |
| Tarnished Crown + Verdant Amulet (the Armory Battlegrounds pair, Legendary no recipe) | Unclaimed Luggage tier IV, any zone | 1% of a tier IV box |
| One of ours per 20 levels (first: R1 The Filing Spike) | any levelled kill in Lv 15-29 | 0.02% (1 in 5,000) |

Rows: `mythic.world.<id>` = source + chance. A world-drop Mythic arrives as the purple bag tagged with its own one-item pool.

## 3. SET (green)

| Rule | Value |
|---|---|
| What | an armor set of EXISTING armor (vanilla Cobalt, Armory Calvary, our Cindersteel ...) whose pieces are the same as normal until ALL pieces are worn - then one full-set buff (Skyy: Cobalt + 100 Health) |
| Source | mainly QUEST rewards: the zone story quests and the Zone 1 town quest line hand out one Set piece per step (4 steps = the set), or a whole set at a chapter end; also: slayer level recipes may output Set pieces (Slayers-Spec 5) |
| Rarity | `set` (green #55FF55, live); stats = the live Set row (3 modifiers 45-95%); no random rarity on a Set piece |
| Level | the quest's level (a quest Cobalt set at Lv 25); level-up +6 |
| Trade | tradable (question 12) |
| Partial | nothing at 1-3 pieces (Skyy: "the same as vanilla until you put on all 4") |
| Mythic sets | the SAME mechanism, but rarity stays `mythic` - the set check reads the `set` field, not the rarity |

### 3.1 Set membership and the full-set check in SkyyGear

| Piece | Design |
|---|---|
| Set table | `set.<setId>` = `name, pieces (4 ids or an id prefix + slots), bonus lines (stat=value, live stats only), rarity (set / mythic)`. Editable in Server Setup -> Gear -> Sets |
| Membership | in the item's **document** (`set` field = setId), written when the piece is made (quest reward, boss bag identify, admin `/gear set <id>`). A quest "Cobalt Chestplate" is the vanilla id `Armor_Cobalt_Chest` with `set=cobalt_quest` and rarity `set` - so a crafted Cobalt chest never counts |
| Check | on every armor change (the existing armor pass that applies SkyyGear's armor stats - `GearABox` / lock-modifier path): count worn pieces whose `set` field equals setId; if count == pieces the set defines, apply the bonus lines as ONE extra lock-modifier block on the chest piece (or a player effect if the pass cannot add to a piece - UNVERIFIED); else remove it |
| Mixed | two different sets: no bonus; 3 of set A + 1 of set B: no bonus |
| Tooltip | every piece: a green (or purple for Mythic) block "Set: Calvary (3/4) - +120 Health, +5% crit damage when all 4 are worn" |
| Wardrobe | swapping a set in / out triggers the same pass |
| Stats page | lists the active set bonus by name |

### 3.2 Gathering armor = green Sets (LOCKED 2026-10-08)

Skyy (docs/answered/gear.md 2026-10-08): "yes, gathering armor uses the set label, the full set gives a little bonus gathering fortune (mining foraging ect.) and the higher tiers can give a little more like mining /chopping speed, movement speed, ect." So the farming crop sets (`Crop-Armor-Spec.md`), the foraging tree sets (`Foraging-Armor-Design.md`) and the vanilla metal MINING sets (`Gathering-Armor-Mining-Farming.md`) are rarity `set` (green), `set` field = family + tier, no random rarity ladder on them (the planned x1 / 1.1 / 1.2 / 1.3 Fortune-by-rarity multiplier goes away; tier + full set only). Pieces are as the tier says until all 4 are worn.

Proposed full-set bonus per tier (placeholders; one table per family in Server Setup -> Gear -> Sets; "Fortune" = that family's skill Fortune in the same unit as tools / trees; speed stats marked (later) stay hidden until they are live, per the 2026-09-30 rule):

| Tier | Mining (vanilla metal sets) | Farming (crop sets) | Foraging (tree sets) | Full-set bonus |
|---|---|---|---|---|
| T1 | Copper | Wheat-tier | Softwood (Oak-tier) | +1 Fortune |
| T2 | Iron | Carrot / Potato-tier | Birch-tier | +1.5 Fortune |
| T3 | Thorium | Pumpkin-tier | Spruce-tier | +2.5 Fortune, +5% Mining / Harvest / Chopping speed (later) |
| T4 | Cobalt | Melon-tier | Jungle-tier | +4 Fortune, +8% speed (later) |
| T5 | Adamantite | Cocoa / Cactus-tier | Goldenwood-tier | +5.5 Fortune, +10% speed (later), +5% move speed |
| T6 | Mithril | Mushroom / Sugar-tier | Ancient-tier | +7.5 Fortune, +12% speed (later), +8% move speed |
| T7 | Onyxium | Nether-wart-tier (top crop) | Voidwood-tier (top tree) | +10 Fortune, +15% speed (later), +10% move speed, + the family's special (Vein Burst / Tree Feller level as already designed) |

The crop and tree names per tier are the families' own ladders (crops: Crop-Armor-Spec; trees: F1-F5 designs - fewer tiers than 7, map them onto the rows that exist). The Fortune numbers are the Crop-Armor-Spec ladder reused as the SET bonus (instead of x1.15 of the pieces), so a full set is worth about one tool tier; the armor Fortune cap 15 still applies after the bonus. Mixed tiers: no bonus (all 4 must be the same set id).

## 4. Boss respawn on demand + Challenge mode

### 4.1 The Appeals Desk (BL4's Big Encore)

| Rule | Value |
|---|---|
| What | a desk block (lore: "Appeals") in the boss arena. It appears after the boss's STORY kill on this profile (BL4: the machine appears after the first kill; PoE: witnessed first). Use = a small page: "File an appeal: fight <boss> again - N coins" and the Challenge toggle |
| Cost | coins: **boss level x 25** (Lv 20 = 500, Lv 30 = 750, Lv 45 = 1,125, Lv 60 = 1,500, Lv 70 = 1,750); scale: slayer Zone 1 Tier I = 400. A coin sink, like BL4's fee. Alternative: a **Boss Token** item (1 guaranteed per kill) - rejected as default because it makes farming free after the first kill (question 14) |
| Cooldown | 60 s after the boss dies (arena reset: adds despawn, loot vanish timer); one boss alive per arena |
| Party | the payer summons; everyone inside the arena ring (48 blocks) fights; boss Health +50% per extra player (cap +150%, Slayers rule); every participant with >= 15% damage OR healing credit gets their own drop roll (BL co-op loot; question 15) |
| Which bosses | zone guardians (summit arena) and dungeon bosses (desk in the boss room): yes. Slayer bosses: no (the bounty IS the respawn). Capstone floors: no (the run is the respawn). World-event bosses: no. The Dragon: yes after the story (lore: "a re-enactment"; the dragon stays friendly outside the fight) |
| Limits | none by default beyond coins + cooldown; row `boss.summon.perHour` (0 = none) for admins; AFK: the summoned boss despawns after 15 min with no damage |
| Story | the story kill never uses the desk (free, once per profile, unlocks the island); desk kills never re-grant Portal Fragments / quest items |

### 4.2 Challenge mode ("Formal Complaint")

| Rule | Value |
|---|---|
| How chosen | a toggle on the desk page before paying; cost **x2** coins |
| Difficulty | boss Health **x2**, damage **x2**, plus ONE elite affix (Elites-Events-Spec 1.2: Shielded / Swift / Frenzied ...) on the boss; adds +50% count. Boss caps are separate from the normal-mob caps (health x6 / damage x3.5) - UNVERIFIED how `scale.role` stacks |
| Drops | Mythic chance **x2** (section 5.1), the RNG meter fills **x2**, UT line x2 |
| Unlock | only after one NORMAL desk kill of that boss on this profile |
| Limits | same as normal summons; a title "Formal Complaint: <boss>" on the first Challenge kill; the boss page shows normal / challenge kill counts |
| Not for | story kills, slayers (they have tiers), the capstone (Master Mode is its hard mode) |

## 5. Drop rules

### 5.1 Mythic chance per kill

| Rule | Value |
|---|---|
| One roll per kill per participant | `mythic.chance` **10%** normal, **20%** Challenge (BL4 fan sample ~5% per dedicated item; our pool pick below makes a specific item 1-3% per kill). Zone-Bosses "re-fight on a cooldown" reduced loot is replaced by the desk cost |
| Pool pick | weighted pick from `boss.<role>.pool`; **own-class lean**: weapons of your class x3 weight, armor of your class's type x3 (Loot-Unid-Spec class lean idea; Own-Specials Q8) |
| Bag | the purple Mythic Mystery Bag with `pool=<role>`; the pick happens at IDENTIFY with the identifier's lean (so the bag is a fair trade; the lean follows whoever opens it) |
| Guaranteed lines | besides the Mythic roll a boss always drops: its normal gear roll (unidentified, boss level), Void Fragments / cores, quest items on the story kill |
| Appraiser | the Smithing step-up never steps INTO Mythic (LADDER ends at Fabled) and never touches a Mythic bag |

### 5.2 RNG meter (SkyBlock, Slayers-Spec 5)

One meter per boss per profile, on the boss page: pick the pool item you want; every kill without a Mythic adds +1 (Challenge +2); at `mythic.meter.size` **40** the next Mythic bag is guaranteed to BE that item (the pick is forced, the roll still rolls modifiers). The meter resets on that drop. Slayer bosses keep the Slayers-Spec meter (signature drop) - same code, two tables.

### 5.3 Mystery Bags

| Bag | Rarity shown | Inside |
|---|---|---|
| purple Mythic bag | "Mythic - <boss name>" | one item of the boss pool (lean at identify), modifiers rolled from the Mythic row; re-roll stays in the pool |
| green Set bag | not used: quest Set pieces are handed over identified (you know your reward) |
| Untiered | no bag - drops identified (question 3; alternative: an 8th orange bag by Quirk) |
| Normal-Fabled bags | unchanged (Loot-Round-Revision) |

### 5.4 Anti-farm

| Risk | Answer |
|---|---|
| Desk spam with alts in the party | each participant needs >= 15% damage / healing credit; boss Health scales with party size |
| Coin loop (sell Mythics to NPC for more than the desk costs) | NPC sell value of any Mythic < the cheapest desk fee (local check, like the re-roll check U3) |
| Challenge carry | Challenge drops use each participant's own roll; a participant 15+ levels under the boss gets the "carried" flag (Capstone rule): half chance |
| Meter + re-roll stacking | the forced meter item is written into the bag; a re-roll of a meter bag is refused ("guaranteed drops cannot be re-rolled") |
| UT dupes through chest sharing | UTs are created on the give, per player, like all chest loot |

## 6. Which mods change

### 6.1 SkyyGear (rarity + caps + set check + UT path)

1. 8th quality asset `untiered` (orange), RARITIES row, lang line, AH category, `/gear rarity untiered` (table ids only).
2. Mythic OUT of the random ladder: ODDS_DEF mythic -> 0 / 0 / 0 (today mob 0.5 / chest 0.6 - columns craft | mob | chest, UNVERIFIED), LADDER = Normal..Fabled (today it includes Mythic), craft.maxRarity choices end at Fabled; one-time setting migration only for rows still at the old default.
3. Per-rarity level-up cap row `levelUp.cap.<rarity>` (6,6,6,6,6 / set 6 / untiered 3 / mythic 2) replacing the single LVLUP_CAP_DEF; `cost.levelUp.untiered`.
4. UT table + fixed-stat document path (1.5); Reforge page modifiers tab disabled for UT; Identify never lists UT.
5. Set table + membership field + full-set check on the armor pass (3.1); tooltip set block; Stats page line.
6. Mythic bag `pool` tag + identify pick with lean + re-roll inside the pool; the Appraiser rule.
7. Bridge: `gear:fn:grant` (id, level, rarity, set, pool) for quests / bosses / chests; `gear:fn:bag` gets a `pool` argument.

### 6.2 SkyyMobs (boss stage) - pools, drops, desk, challenge, meter

`scale.role` filled for the bosses; boss spawn by script at the arena with a boss bar; `boss.<role>.pool` / `.ut` / `.world` tables; the Mythic roll + lean + bag give; the Appeals Desk block + page + cost + cooldown + party credit; Challenge scaling + affix; the RNG meter data (per profile, SkyyProfiles contract) + bridge `mob:fn:bossPage`. Recommended: the desk lives HERE (one mod owns a boss from spawn to loot); SkyyDungeons later hosts instances and calls `mob:fn:bossSpawn` (question 16). Alternative: SkyyExploration (it owns chests and spots, not mobs) - not recommended.

### 6.3 Others

| Mod | Change |
|---|---|
| SkyyArmory | the UT weapon items (our art) + their hooks (pierce, speed tier, knockback ...); the 21 Mythic hooks (Own-Specials) |
| SkyyClasses | class weapon table rows for every new id |
| SkyyExploration | Unclaimed Luggage UT chance rows (tiers I-IV); dungeon end chests call `gear:fn:grant` |
| SkyyQuests (spec only, `research/cloud/SkyyQuests-Spec.md`) | SET rewards per step + the one UT reward per zone (1.4); until it exists Set pieces come from an admin command and the Zone 1 town NPC quest line prototype |
| SkyyMenu | a `/bosses` page (pools, kill counts, RNG meter pick, Challenge titles) through `mob:fn:bossPage`; Stats page set-bonus line |
| SkyySlayers (Slayers-Spec) | slayer bosses are bosses: the `boss.<role>.ut` line applies; the meter shares code |
| Art (Quirk / local) | UT weapon looks (one odd detail per item, orange tint accent), 3 UT2 armor sets, the desk block, optionally an 8th orange bag |

### 6.4 Phases and round sizes (PROJECT-RULES 4)

| Phase | What | Mods | Round | Needs first |
|---|---|---|---|---|
| G1 Rarity round | 6.1 items 1-3 + 5 (Untiered label, Mythic off the ladder, per-rarity caps, set table + check) | SkyyGear | **Full round** (saved data per stack, migration) | nothing (can go before the loot round) |
| G2 UT first batch | 1.3 items U1-U10 + UT table + sources (mob drops, elites, chests, luggage, boss line; quest UTs when SkyyQuests exists) | SkyyArmory + SkyyGear + SkyyExploration | **Full round**, art proof first | G1, the loot round (Unclaimed Luggage), elites |
| B1 Boss stage | scale.role bosses, arenas, pools, Mythic roll + bag pool, world drops, the 6 sample pools | SkyyMobs + SkyyGear | **Ultracode** (new system, loot, dupes, several mods) | G1, the loot round (bags), The Armory on 0.7, Own-Specials hooks (SkyyArmory, built per level band) |
| B2 Appeals Desk + Challenge | 4.1 + 4.2 | SkyyMobs (+ SkyyMenu page) | **Full round** (coins, permissions) | B1 |
| B3 RNG meter + boss page | 5.2, `/bosses` | SkyyMobs + SkyyMenu + SkyyProfiles | Full round (saved data) | B2 |
| S1 Set quests | Set rewards in the Zone 1 quest line | SkyyQuests (or the town NPC prototype) | Lean rounds per quest | G1, SkyyQuests |
| later | UT1 / UT3 batches, capstone Mythic uniforms, Mythic sets of our Lv 50+ tiers | per tier | Full rounds | the zone / tier ships |

## 7. Questions for Skyy (each with a recommended default)

1. UT tiers = the 6 zone bands (14 weapons + 3 sets each, 156 eventually), not the 12 metal bands? [yes]
2. UTs tradable (no ROTMG soulbound)? [yes - the AH is part of the game]
3. UTs drop identified (orange name, no bag)? [yes; an 8th orange bag only if you want the surprise]
4. Level-up caps: Mythic +2, Untiered +3, everything else +6? [yes]
5. First batch U1-U10 as listed (swap any)? [keep]
6. The pierce staff: the UT "The Loophole" takes pierce / -30% damage (your example) and the Mythic M1 "The Long Form" keeps pierce at full damage **plus +5% per enemy the shot passes** - so the Mythic is better in every way, not just "the UT without the downside"? [yes]
7. Mythic removed from the random drop / chest odds and from the Smithing step-up (boss-only from now)? [yes]
8. Mythic chance 10% per kill (20% Challenge), one roll per participant, own-class / own-type lean x3? [yes]
9. The six sample pools (2.4) - approve or swap pieces? [approve; TBD weapon slots filled by the next specials draft]
10. Mythic sets: bonus only at the full set, no 2-piece bonus (ROTMG ST has 2 / 3 / 4)? [full set only - your rule]
11. The capstone uniforms (Bailiff / Clerk / Notary, `Capstone-Sets.md`) become MYTHIC 4-piece sets split across floors F1-F4 / F5-F7; the green Set label is for quest versions of existing armor only? [yes]
12. Set pieces tradable? [yes]
13. Gathering sets (3.2): the per-tier Fortune + speed + move-speed numbers, and dropping their random rarity ladder? [as tabled]
14. Appeals Desk cost = boss level x 25 coins (x2 Challenge), 60 s cooldown, no daily cap - not a Boss Token? [coins]
15. Every participant with 15% credit rolls their own drop (BL co-op), not the payer only? [everyone]
16. The desk + pools + meter live in SkyyMobs (no new mod)? [yes]
17. World drops: Ghost Sword (night undead elites), Skull Mask, the Battlegrounds Crown + Amulet (luggage IV), one of ours per 20 levels? [yes]
18. Names: "Appeals Desk", "Formal Complaint" (Challenge), "Untiered" label text? [keep]

## For the local session (UNVERIFIED)

- An 8th item quality asset next to the 7 (vanilla has 6; any cap on quality assets / QualityValue); orange text contrast on the tooltip panel.
- The armor-change hook for the set check (the pass that applies armor stats today) and whether a bonus can sit on one piece as a lock block or needs a player effect.
- Vanilla armor slots = Head / Chest / Hands / Legs (no boots) - and each Armory set's real slot list (Jester 3 slots).
- ODDS_DEF column order (craft | mob | chest) and LADDER including Mythic in 0.2.10 - confirm before the migration.
- Boss spawn by script with a level + boss bar; `scale.role` stacking with the Challenge x2 and the normal-mob caps.
- Per-item arrow speed / gravity (U5), staff pierce on a second id (U1), knockback per hit (U7), reach (spare spear idea).
- NPC sell values of Mythics vs the desk fee (coin loop check).
- Whether SkyyProfiles can hold the per-boss meter + kill counts (PROFILES-CONTRACT).
- `python tools/docs_check.py` printed FAIL on main before this file (pre-existing broken links, see the Own-Specials note); this file adds none.
