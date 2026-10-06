# Questions digest 2026-10-06 (every open question from the cloud drafts, one list)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: the "Questions for Skyy" section of the 41 sources in `research/cloud/` that `research/cloud/LOG.md` dates 2026-10-06 (plus `research/cloud/light-armor/README.md`), `RESUME.md` "Next", `OPEN-QUESTIONS.md` and every `docs/answered/*.md` (keyword grep). Skipped (still being written): NoCube-Mods-Survey, SkyyFishing-Spec-Draft, Food-Expansion-Draft. No questions section: `research/cloud/Modifier-Pool-Spec.md`, `research/cloud/SkyBlock-Gathering-Progression.md`.

**How to answer:** reply with the row numbers. Example: `1-14 yes, 15 no (use 8), 20 skip`. "yes" = take the default in the Default column. Silence = default stays as a placeholder (every number is a Server Setup row, so nothing is final). The local session writes each answer word for word into `docs/answered/` with `tools/qa_append.py`.

Merged rows say "also" and list the other files that asked the same thing. Row numbers run 1 to the end across all tables.

Order of the sections: 1 blockers for the next local builds, 2 economy, 3 design taste, 4 later.


## 1. BLOCKERS for the next local builds

`RESUME.md` "Next" queue: traversal (SkyyArmory 0.1.1 + Classes 0.1.12 + Gear 0.2.4), then tool levels, the loot round, the mob curve + armor types round, weapon speed, minimap, Stats page. Hytale 0.7 lands 2026-10-12.


### 1a. Tool levels (SkyyGear tool-levels build) and Fortune

| # | Question | Default | Source |
|---|---|---|---|
| 1 | Fortune: keep the hard cap 100 with per-source caps (tool 25, armor 15, accessories / pets / collections 10 each), or let Fortune over 100 give a second extra drop? | keep 100, no overflow | `research/cloud/Tool-Levels-Revision.md` Q1; also `research/cloud/Gathering-Numbers-Reconciled.md` Q1 |
| 2 | One armor Fortune ladder (1 to 12, cap 15) for all three gathering sets, so Goldenwood gives 12, not 40? | yes | `research/cloud/Tool-Levels-Revision.md` Q2; also `research/cloud/Foraging-Armor-Design.md` Q3; also `research/cloud/Gathering-Armor-Mining-Farming.md` Q6 |
| 3 | Axe Tree Feller by tier (Iron 1 to Mithril 5, Legendary+ one more, max 6); the best of perk, axe and armor wins, no adding? | yes, max-of-sources | `research/cloud/Tool-Levels-Revision.md` Q3; also `research/cloud/Foraging-Armor-Design.md` Q5 |
| 4 | Hatchet one-chop from Thorium; "faster" means faster than the same vanilla hatchet (2 hits can never beat vanilla's 1 hit)? | yes | `research/cloud/Tool-Levels-Revision.md` Q4 |
| 5 | Sickle Range hits a row along the swing, or a square (+1 = 3x3)? | row | `research/cloud/Tool-Levels-Revision.md` Q5 |
| 6 | Sickle Range cap by Farming level (2 at 25, 3 at 50, 4 at 75) and armor ladder 0 / 0 / 0 / 1 / 1 / 1 / 2 / 2? | yes | `research/cloud/Gathering-Numbers-Reconciled.md` Q6 |
| 7 | Spare-slot boost: +10% to rolls per empty modifier slot, max +30%? | yes | `research/cloud/Tool-Levels-Revision.md` Q7 |
| 8 | Drop the "Tree Feller I / II" collection rewards (axes give it) and put a Foraging XP lump in those slots? | drop; XP lump | `research/cloud/Tool-Levels-Revision.md` Q8; also `research/cloud/Gathering-Numbers-Reconciled.md` Q9 |
| 9 | Thorium hoe + sickle unlock at Corn IV like every other tool (draft said Corn VII)? | IV | `research/cloud/Tool-Levels-Revision.md` Q9 |
| 10 | Make new Cobalt+ hoes and Thorium+ sickles so Farming tools reach Lv 49? | yes, stage 4 | `research/cloud/Tool-Levels-Revision.md` Q6 |
| 11 | Collection Fortune ladder 1 / 1 / 1.5 / 2 / 2 / 2.5 (10 per skill, same for Farming)? Do collections give Fortune at all? | yes | `research/cloud/Gathering-Numbers-Reconciled.md` Q4; also `research/cloud/Collection-Unlocks-Draft.md` Q3; also `research/cloud/Zone-4-5-Materials.md` Q8 |
| 12 | Normal and Unique Prospector / Woodsman / Harvester accessories: only Wisdom, no Fortune? | only Wisdom | `research/cloud/Gathering-Numbers-Reconciled.md` Q5 |
| 13 | Hoe / sickle Fortune per level 0.3 to 0.25, so rolls still matter past Lv 71? | yes | `research/cloud/Gathering-Numbers-Reconciled.md` Q8 |
| 14 | Mining tree swing +40 fills the whole swing ceiling. Accept that tool / armor / pet swing is then wasted, or turn it into Power (fewer hits)? | accept | `research/cloud/Gathering-Numbers-Reconciled.md` Q2 |
| 15 | Any accessory swing (a "Haste accessory")? | no, relabel as Prospector | `research/cloud/Gathering-Numbers-Reconciled.md` Q3 |
| 16 | One armor set bonus: Fortune x1.15 at 4 pieces in all three gathering sets, Foraging's 2-piece +25% removed? | yes | `research/cloud/Gathering-Numbers-Reconciled.md` Q7 |


### 1b. Gathering ladder spec (collections, Enchanted, tiers) - tool levels hang off it

| # | Question | Default | Source |
|---|---|---|---|
| 17 | Collection gate for "next tool": tier IV, or earlier (III) for a quicker climb? | IV | `research/cloud/Collection-Unlocks-Draft.md` Q1 |
| 18 | Pocket Shard at tier I of every collection: all 159, or only the 30 launch types? | 30 launch types | `research/cloud/Collection-Unlocks-Draft.md` Q2 |
| 19 | Enchanted premium per compression step: 10%, or 15-20% like ingots? | 10% | `research/cloud/Enchanted-Materials-Draft.md` Q1 |
| 20 | Enchanted Wood from any species of the group (5 woods), or one per species (33)? | group | `research/cloud/Enchanted-Materials-Draft.md` Q2 |
| 21 | Enchanted Blocks for every material, or only metals + key logs + wheat / pumpkin? | metals, key logs, wheat / pumpkin | `research/cloud/Enchanted-Materials-Draft.md` Q3 |
| 22 | Five tree tiers (F1 to F5) with only F1 (+ Azure wood) in Zone 1, or four? | 5 | `research/cloud/Gathering-Tiers-Draft.md` Q1 |
| 23 | Ship Mining and Farming armor with the Foraging armor, or one skill at a time? | one at a time: Foraging, Mining, Farming | `research/cloud/Gathering-Tiers-Draft.md` Q2; also `research/cloud/Gathering-Armor-Mining-Farming.md` Q1 |


### 1c. Loot round (SkyyGear loot build)

| # | Question | Default | Source |
|---|---|---|---|
| 24 | Mob loot-box drop rate from 4% up to 6% (1 in 17)? | 6% | `research/cloud/Loot-Round-Revision.md` Q1 |
| 25 | Re-roll costs x5 each time, max 3, keeps rarity, clears reforges? | yes | `research/cloud/Loot-Round-Revision.md` Q2 |
| 26 | Show the armor type (Heavy / Light / Cloth) on armor boxes? | yes | `research/cloud/Loot-Round-Revision.md` Q3 |
| 27 | Loot chests: each player gets their own loot, chest vanishes after 20 s? | yes | `research/cloud/Loot-Round-Revision.md` Q4 |
| 28 | A looted chest returns at the same spot (30 min) plus new random spots? | both | `research/cloud/Loot-Round-Revision.md` Q5 |
| 29 | Name the chests "Unclaimed Luggage"; no coins inside? | name yes, no coins | `research/cloud/Loot-Round-Revision.md` Q6 |
| 30 | Host the loot chests in SkyyExploration (chest XP too)? | yes | `research/cloud/Loot-Round-Revision.md` Q7 |
| 31 | Box art: 126 ids (rarity crate + type badge) or 7 ids (type only in the name)? | 126, fall back to 7 | `research/cloud/Loot-Box-Design.md` Q1 |
| 32 | Level range width 5 (e.g. 41-45), real level random inside it (not the centre)? | yes | `research/cloud/Loot-Box-Design.md` Q2 |


### 1d. Armor types + mob curve round (SkyyGear takes over armor stats)

| # | Question | Default | Source |
|---|---|---|---|
| 33 | Heavy = today's metal numbers; Light 90% Health / 80% Defense; Cloth 90% Health / 60% Defense? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q1 |
| 34 | Full-set speed Heavy -5%, Light +4%, Cloth +8%, never past +-10%? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q2 |
| 35 | Class bonus per tier as in section 4 (Heavy crit damage 5-26%, Light crit chance 2-8%)? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q3 |
| 36 | Cloth Mana regen from Cotton up (+10 / 20 / 30%), and max Mana for anyone in Cloth? | yes, yes | `research/cloud/Armor-Types-Spec-Draft.md` Q4 |
| 37 | A Light upgrade keeps rarity + rolled modifiers and restamps the level to yours? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q7 |
| 38 | Drop the separate Crude armor set; each type's tier 1 replaces it? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q8 |
| 39 | Copper armor band back to 10-18 now Heavy Leather sits below it? | keep 1-18 (your 2026-10-01 lock) | `research/cloud/Armor-Types-Spec-Draft.md` Q9 |
| 40 | Bronze = Heavy at the Iron band, Ancient Steel = Heavy at the Thorium band? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q11 |
| 41 | Light Attack Speed fully hidden until it works, nothing in its place? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q5 |
| 42 | Cindercloth covers Lv 35-49 (no 7th cloth tier until the Lv 50+ tiers)? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q6 |
| 43 | Soft / Medium / Raven leather count as Light tier 1? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q10 |
| 44 | Foraging armor Health / Defense = 50% of Heavy at its level, no speed change? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q12 |
| 45 | Mixed sets per piece, no full-set bonus? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q13 |
| 46 | Crude Robe = 31 Fibre + 4 green crystals (1 per piece)? | yes | `research/cloud/Armor-Types-Spec-Draft.md` Q14 |


### 1e. Weapon speed pass (SkyyGear)

| # | Question | Default | Source |
|---|---|---|---|
| 47 | How is weapon speed set: by weapon type, rolled, or both? | both: type default; Rare+ 5% chance of +-1 tier | `research/cloud/Weapon-Speed-Tiers.md` Q1 |
| 48 | Default tiers in section 3 right (Staff Slow, Spellbook Medium, Dagger Super Fast, Crossbow Slow ...)? | as in section 3 | `research/cloud/Weapon-Speed-Tiers.md` Q2 |
| 49 | Super Fast = 4 hits/s (engine floor 0.25 s) or Wynn's 4.3? | 4.0 | `research/cloud/Weapon-Speed-Tiers.md` Q3 |
| 50 | Flat per-hit extras (flat element lines, True Damage) shrink on fast weapons so DPS stays equal? | yes | `research/cloud/Weapon-Speed-Tiers.md` Q4 |
| 51 | Knockback scales with hit size (Slow far, Super Fast barely)? | yes | `research/cloud/Weapon-Speed-Tiers.md` Q5 |
| 52 | Abilities that deal "one weapon hit" use the speed-neutral hit? | yes (Wynn's rule) | `research/cloud/Weapon-Speed-Tiers.md` Q6 |
| 53 | Attack Speed % on a weapon already at the fastest swing becomes bonus damage? | yes | `research/cloud/Weapon-Speed-Tiers.md` Q7 |
| 54 | Show the tooltip + weights before the swing-speed mechanism works, or wait? | wait | `research/cloud/Weapon-Speed-Tiers.md` Q8 |
| 55 | Staff Slow speed multiplies its Mana by 1.4, or speed is damage-only for casters? | keep x1.4 (`speed.manaScale`) | `research/cloud/Spellbook-Ladder.md` Q4 |


### 1f. Traversal + class builds (physical-class costs)

| # | Question | Default | Source |
|---|---|---|---|
| 56 | Mana for the five physical classes (traversals cost Mana 2 : Stamina 1): +2 Mana per class level, or Stamina costs instead? | +2 Mana per class level | `research/cloud/Class-Ability-Spec-Draft.md` Q1 |
| 57 | Monk-only Stamina row (+0.15 per level) since the Monk pool of about 12 is the limit? | yes | `research/cloud/Monk-Kit-Spec.md` Q3 |
| 58 | Ability level cap 15 and 14 points (two modifiers maxed): right size, or more points? | 15 / 14 | `research/cloud/Class-Ability-Spec-Draft.md` Q2 |
| 59 | Berserker self cap +60%? | yes | `research/cloud/Class-Ability-Spec-Draft.md` Q3 |


### 1g. Minimap + Stats page (items 9 and 10 of the queue)

| # | Question | Default | Source |
|---|---|---|---|
| 60 | Minimap default resolution Normal 24 (sharper, 40 KB first fill) or Low 16 (smallest)? | Normal 24 | `research/cloud/Minimap-Widget-UX.md` Q1 |
| 61 | Minimap on the starter island and in dungeons: show "No map here" or hide itself? | (none written) show "No map here" | `research/cloud/Minimap-Widget-UX.md` Q2 |
| 62 | Heading arrow with 16 steps is enough (36 steps = 36 tiny assets)? | 16 | `research/cloud/Minimap-Widget-UX.md` Q3 |
| 63 | Stats page: Phase 1 first (SkyyMenu only) and the contribution contract later, or both together? | phase 1 first | `research/cloud/Stats-Page-Spec.md` Q1 |
| 64 | Show planned (grey) stats by default, or hide them behind the checkbox? | hidden | `research/cloud/Stats-Page-Spec.md` Q2 |
| 65 | Show Fortune as SkyBlock style (100 = one extra drop) or as % double-drop chance? | SkyBlock style | `research/cloud/Stats-Page-Spec.md` Q3 |
| 66 | Schedule the two dead links (class-tree Strength, Alchemy / Smithing nodes) as small bug fixes? | yes | `research/cloud/Stats-Page-Spec.md` Q4 |


### 1h. Hytale 0.7 (release 2026-10-12)

| # | Question | Default | Source |
|---|---|---|---|
| 67 | Switch the live pack to 0.7 on release day once the "both versions" fixes are deployed, or wait a few days for wave patches? | wait 2-3 days | `research/cloud/Hytale-0.7-Watch.md` Q1 |
| 68 | Keep your test world on 0.6.8 and use the pre-release only on a copy? | yes | `research/cloud/Hytale-0.7-Watch.md` Q4 |
| 69 | Rune ability costs: divide like spells, or keep vanilla cost? | decide after release; keep vanilla | `research/cloud/Hytale-0.7-Watch.md` Q2 |
| 70 | Keep "every class has 100 Mana" now vanilla Max is 100? | keep | `research/cloud/Hytale-0.7-Watch.md` Q3 |


## 2. Economy (bank, Tab, Fortune cap, sinks)

The Fortune cap question is row 1 above (it is also an economy cap: `perk.doubleDropMax`). Bank and Tab rows come from two files that agree; merged.


| # | Question | Default | Source |
|---|---|---|---|
| 71 | Bank: pay interest once per real day with falling brackets (2% to 1M, 1% to 5M, 0.5% to 10M) counted over all profiles? Today a full bank pays 4.8M a day while you sleep. | yes; offline still paid, back-pay kept | `research/cloud/Bank-Tab-Calibration.md` Q1; also `research/cloud/Economy-Audit.md` Q1 |
| 72 | Tab: show it in "Void Marks" (20,000,000 a day) and pay in coins at a posted exchange rate? | yes | `research/cloud/Bank-Tab-Calibration.md` Q2; also `research/cloud/Tab-Prestige-Scripts.md` Q3 |
| 73 | Tab rate about 25% of a good endgame hour (90,000 coins per online hour placeholder; measure first, then 40-50% if you want it harder)? | 25%, 90,000 | `research/cloud/Bank-Tab-Calibration.md` Q3; also `research/cloud/Economy-Audit.md` Q2 |
| 74 | Starter 10,000 coins stay once per profile (your lock): pay over the first hour, and wait 1 day after a delete? Or once per account slot? | vest 1 hour + 1-day wait; lock kept | `research/cloud/Bank-Tab-Calibration.md` Q4; also `research/cloud/Economy-Audit.md` Q4 |
| 75 | Accessory Bag slots: may coins buy them, or only collections / skills / quests (R3)? | no coins | `research/cloud/Economy-Audit.md` Q3 |
| 76 | Zone 5 slayer costs (up to 3M per spawn): lower to about one hour of income? Zone 1 Tier I = 400 a good mid-game sink? | Z5 costs x0.25; 400 ok | `research/cloud/Economy-Audit.md` Q5; also `research/cloud/Slayers-Spec.md` Q3 |
| 77 | Enchanted Blocks +5% on top of the Enchanted form (not +10%), so no buy-craft-sell loop opens? | +5% | `research/cloud/Economy-Audit.md` Q6; also `research/cloud/Zone-4-5-Materials.md` Q5 |
| 78 | Can accessories be traded / sold on the AH? | yes Normal-Rare, bound for Legendary + rare finds | `research/cloud/Accessory-Acquisition.md` Q4 |
| 79 | Can capstone set pieces be traded on the AH, or soulbound to the finder? | tradeable (daily cap limits flooding) | `research/cloud/Capstone-Sets.md` Q8 |
| 80 | Ember Core (hard gate on every Cindersteel piece, 6 per kit): tradable on the AH? | yes, yes | `research/cloud/Zone-4-5-Materials.md` Q3 |
| 81 | Outpost warp: free with a 60 s cooldown, or a small coin fee? | free + 60 s | `research/cloud/Outposts-List.md` Q2 |
| 82 | Later: bank upgrades like SkyBlock (a Gold collection tier unlocks a bigger bank, coins pay the fee)? | later, not first build | `research/cloud/Bank-Tab-Calibration.md` Q5 |


## 3. Design taste (looks, names, feel)

| # | Question | Default | Source |
|---|---|---|---|
| 83 | Light armor sheet `research/cloud/light-armor/light-armor-sheet.png`: which tiers feel right, which need changes? | keep all; tweak what you point at | `research/cloud/light-armor/README.md` Q1 |
| 84 | Metal amount on Light armor (13% Copper up to about 35% Onyxium) right, or plainer at high tiers? | as drawn | `research/cloud/light-armor/README.md` Q2 |
| 85 | Keep the per-tier chest piece on the strap (ring, plate, boss, diamond, shard, gem, onyx gem)? | yes | `research/cloud/light-armor/README.md` Q3 |
| 86 | Buckles in the tier metal on every tier, or brass buckles always? | tier metal | `research/cloud/light-armor/README.md` Q4 |
| 87 | Light helmet: hood, leather cap, or hidden? | leather hood with a metal rim | `research/cloud/light-armor/README.md` Q5 |
| 88 | Colour guesses for Thorium (green), Mithril (pale silver-blue), Onyxium (violet + gold): fix after a local screenshot check? | yes, match vanilla | `research/cloud/light-armor/README.md` Q6 |
| 89 | Do the five names (Cindersteel, Amberite, Drakonite, Voidglass, Aetherium) work, or pick your own? | keep | `research/cloud/SkyyArmory-Roadmap.md` Q1 |
| 90 | Capstone set names (Bailiff / Clerk / Notary) and Aetherium prefixes Chief / Senior / High OK? | yes | `research/cloud/Capstone-Sets.md` Q6 |
| 91 | Foraging armor glowing sap veins: a real light source or just a bright texture? | texture only | `research/cloud/Foraging-Armor-Design.md` Q7 |
| 92 | Mining helmet lamp gives real light, or only a glow? | glow only | `research/cloud/Gathering-Armor-Mining-Farming.md` Q4 |
| 93 | Mining set look: leather body with metal plates, or a full metal set? | leather body + plates | `research/cloud/Gathering-Armor-Mining-Farming.md` Q3 |
| 94 | Name the armor stat "Mining Speed" (swing) or "Mining Power" (fewer hits)? | Mining Speed | `research/cloud/Gathering-Armor-Mining-Farming.md` Q5 |
| 95 | Is "Branch Office" the voice for outposts (Department of Arrivals joke) or plain place names? | Branch Office | `research/cloud/Outposts-List.md` Q3; also `research/cloud/Barks-Signs-Tips.md` Q2 |
| 96 | Tab clerk: a new Kweebec Clerk Penwright, or Clerk Mossby runs the Tab hall too? | Penwright | `research/cloud/Tab-Prestige-Scripts.md` Q2 |
| 97 | Is a Pebble cameo in every Tab milestone line too much (used in two)? | keep two | `research/cloud/Tab-Prestige-Scripts.md` Q5 |
| 98 | Should barks name the working places (Annex, Cold Storage ...) or stay generic? | signs name them, barks generic | `research/cloud/Barks-Signs-Tips.md` Q1 |
| 99 | Are the 8 NPC types right (clerk, banker, smith, guide, guard, shopkeeper, event vendor, outpost keeper)? | yes | `research/cloud/Barks-Signs-Tips.md` Q3 |
| 100 | Keep the wrong-but-cheerful Pebble-style guide in town as well as on the shard? | yes, lightly | `research/cloud/Barks-Signs-Tips.md` Q4 |
| 101 | Tips on loading screens, in chat, or both? | both; chat every 10 min | `research/cloud/Barks-Signs-Tips.md` Q5 |
| 102 | Let server owners add their own bark / tip lines in Server Setup? | yes, appended to the same keys | `research/cloud/Barks-Signs-Tips.md` Q6 |
| 103 | Box art: the ?-crate, or a Wynncraft-like gift box / bag? | chest (engine reasons) | `research/cloud/Loot-Box-Design.md` Q3 |
| 104 | Monk class skill name: Discipline, Zen, Kenpo, Harmony or Focus? | Discipline | `research/cloud/Monk-Kit-Spec.md` Q1 |
| 105 | Capstone name "The Final Audit" (the Void's own office), Landlord as the F3 boss? | yes | `research/cloud/Capstone-Dungeon-Spec.md` Q3 |
| 106 | Capstone department names (Unhatched Claims, Lost Property, Customer Waiting, Internal Audit) and voice samples right? | yes | `research/cloud/Capstone-Floors-4-7.md` Q2 |
| 107 | Is the Page Burst (lobbed orb that bursts in a sphere, group tool, loses to the staff on one target) the right feel for the spellbook? | yes | `research/cloud/Spellbook-Ladder.md` Q1 |
| 108 | Soul Orb: recipe gem count is half the tether count; Mithril essence (wind / Zephyr) and Onyxium (Voidheart + Void) as proposals OK? | yes | `research/cloud/Soul-Orb-Spec.md` Q1; also `research/cloud/Soul-Orb-Spec.md` Q2 |
| 109 | Do you want a Wood book rung (live book 20 Mana stays) or leave the live book as the Wood tier? | leave as is | `research/cloud/Spellbook-Ladder.md` Q9 |
| 110 | Quest NPCs show a `!` / `?` marker over the head (needs an engine check) or only a map marker? | marker if the engine allows | `research/cloud/SkyyQuests-Spec.md` Q3 |
| 111 | Ember Ore as a Prisma-style vanilla block (if files confirm) or all-new ore ids? | new ids | `research/cloud/Zone-4-5-Materials.md` Q7 |


## 4. Later (no build queued yet)

### 4a. Classes and weapons

| # | Question | Default | Source |
|---|---|---|---|
| 112 | Archer: cap 6 up to 10 bolts (+1 at Archery 15 / 30 / 42 / 55) - is that what you meant, since vanilla already holds 6? | yes | `research/cloud/Archer-Bolts-Holster.md` Q1 |
| 113 | Holstered reload at which level (tree draft said 55; you said near the top)? | 75 | `research/cloud/Archer-Bolts-Holster.md` Q2 |
| 114 | Holster refill: the whole magazine after 30 s, or one bolt at a time? | whole, 30 s | `research/cloud/Archer-Bolts-Holster.md` Q3 |
| 115 | Damage per bolt unchanged (about +4% sustained DPS, +67% burst)? | unchanged | `research/cloud/Archer-Bolts-Holster.md` Q4 |
| 116 | Raise the daily Archer arrow refill for the bigger magazine? | leave; revisit after testing | `research/cloud/Archer-Bolts-Holster.md` Q5 |
| 117 | Quiver Craft: 10% chance a loaded arrow is not consumed? | yes | `research/cloud/Archer-Bolts-Holster.md` Q6 |
| 118 | Holster also for a held crossbow that fell to 0 (e.g. while sneaking)? | no, only holstered | `research/cloud/Archer-Bolts-Holster.md` Q7 |
| 119 | Kunai: one reusable kunai (stack 1, nothing dropped or lost) instead of a stack of thrown ones? | yes | `research/cloud/Kunai-Ladder.md` Q1 |
| 120 | Kunai teleport allowed in combat (only locked arenas block it)? | allowed | `research/cloud/Kunai-Ladder.md` Q2 |
| 121 | Charged kunai throw hits like a tap, no extra damage? | like a tap | `research/cloud/Kunai-Ladder.md` Q3 |
| 122 | Vanilla Kunai (Lv 20-27, no teleport) stays a plain loot item? | yes | `research/cloud/Kunai-Ladder.md` Q4 |
| 123 | Kunai range 20 on every metal (class tree adds more), or +1 per metal tier? | stays 20 | `research/cloud/Kunai-Ladder.md` Q5 |
| 124 | Kunai DPS = 80% of the dagger's (range + teleport pay the rest)? | 80% | `research/cloud/Kunai-Ladder.md` Q6 |
| 125 | A Crude Kunai at Lv 1 so a new Assassin can start with one? | yes | `research/cloud/Kunai-Ladder.md` Q7 |
| 126 | Teleport next to another player where PvP is on (a gank tool)? | yes, PvP-on only | `research/cloud/Kunai-Ladder.md` Q8 |
| 127 | Spellbook Mana follows the Mage pool (10 per level, 531 at Lv 50) or the Roadmap's 5 per level (280)? | Mage pool; costs scale to 30% | `research/cloud/Spellbook-Ladder.md` Q2 |
| 128 | Page Burst wins from 3 targets (k = 0.40), or from 2 (k about 0.55)? | 3 | `research/cloud/Spellbook-Ladder.md` Q3 |
| 129 | Flat per-hit gear lines count per target in a burst, or once per cast? | per target | `research/cloud/Spellbook-Ladder.md` Q5 |
| 130 | Levitate scales with metal (8 blocks / 3 s at Copper to 17 blocks / 8 s at Aetherium) or stays 8 / 3? | scales up | `research/cloud/Spellbook-Ladder.md` Q6 |
| 131 | Spellbooks: leather + metal clasp ladder (7 metals), area-based power instead of raw Mana? | yes | `research/cloud/SkyyArmory-Roadmap.md` Q3 |
| 132 | Monk: start with wraps + gauntlets only, claws later? | yes | `research/cloud/Monk-Kit-Spec.md` Q2 |
| 133 | Soul Orb stored healing also works on Sacred Heal, or only Wings of Fate? | (no default written) only Wings of Fate | `research/cloud/Soul-Orb-Spec.md` Q3 |
| 134 | Class tree: 1 point per 3 class levels (25 for trunk + path by Lv 75), or more generous? | 1 per 3 | `research/cloud/Class-Tree-Paths.md` Q1 |
| 135 | Class tree: 3 paths x 5 nodes + 6-node trunk (21 nodes) right size (earlier answer said about 25)? | 21 | `research/cloud/Class-Tree-Paths.md` Q2 |
| 136 | Respec costs coins, a rare item, or is free on a long cooldown? | (no default written) long cooldown | `research/cloud/Class-Tree-Paths.md` Q3 |
| 137 | SkyyArmory first wave: only the main weapon per class plus 3 armor sets? | yes | `research/cloud/SkyyArmory-Roadmap.md` Q4 |
| 138 | Capstone tiers (Voidglass, Aetherium) drop only, or craftable from shards too? | drop only at launch | `research/cloud/SkyyArmory-Roadmap.md` Q2 |


### 4b. Armor sets, gathering armor, accessories

| # | Question | Default | Source |
|---|---|---|---|
| 139 | Foraging armor: Tree Feller from the full set only, or per piece? | full set | `research/cloud/Foraging-Armor-Design.md` Q2 |
| 140 | Foraging armor: each tier eats the previous tier's piece (bench upgrade style), or raw wood + Enchanted only? | raw wood + Enchanted | `research/cloud/Foraging-Armor-Design.md` Q4 |
| 141 | Goldenwood gate 50-59 (later band) or 40-49 with Onyxium? | 50-59 | `research/cloud/Foraging-Armor-Design.md` Q6 |
| 142 | Vanilla Wood armor gives a small Foraging Fortune (4)? | yes | `research/cloud/Foraging-Armor-Design.md` Q8 |
| 143 | Mining / Farming armor: 8 tiers each (starter + 7 metals), or 7 with Crude as T1? | 8 | `research/cloud/Gathering-Armor-Mining-Farming.md` Q2 |
| 144 | Vein Burst on armor reuses the tree perk: armor gives it at T5+, higher level wins? | yes | `research/cloud/Gathering-Armor-Mining-Farming.md` Q7 |
| 145 | Auto-replant (Green Thumb) wanted at all (crops regrow in vanilla)? | yes, T5+, if engine allows | `research/cloud/Gathering-Armor-Mining-Farming.md` Q8 |
| 146 | Rare Onyxium Mining / Farming variant at Lv 50+ now, or wait for Cindersteel+? | wait | `research/cloud/Gathering-Armor-Mining-Farming.md` Q9 |
| 147 | Silver / Gold as an optional luxury tier (jewelry, accessories) outside the tool ladder? | (no default written) later | `research/cloud/Gathering-Tiers-Draft.md` Q3 |
| 148 | Capstone sets: 3 of 4 slots (Heavy no Legs, Light no Boots, Cloth no Helmet) or all 4? | 3 of 4 | `research/cloud/Capstone-Sets.md` Q1 |
| 149 | Set bonus works for every class or only the matching class? | everyone | `research/cloud/Capstone-Sets.md` Q2 |
| 150 | A full set about 105-115% of three Legendary pieces, or should sets beat Mythic? | between Legendary and Mythic | `research/cloud/Capstone-Sets.md` Q3 |
| 151 | Set chance 8% per roll, guaranteed piece after 12 chests? | yes | `research/cloud/Capstone-Sets.md` Q4 |
| 152 | Set pieces from the boss chest only, not secret rooms? | boss chest only | `research/cloud/Capstone-Sets.md` Q5 |
| 153 | Add Thorns (Heavy) and Attack Speed (Light) to set bonuses when they go live? | yes | `research/cloud/Capstone-Sets.md` Q7 |
| 154 | Gift of one Normal Speed + Normal Health accessory at the tutorial? | yes | `research/cloud/Accessory-Acquisition.md` Q1 |
| 155 | Drop/Chest lines: also a craft path to Legendary (Rare + 2 Void Fragments + Hardened Core)? | yes | `research/cloud/Accessory-Acquisition.md` Q2 |
| 156 | Legendary accessories mostly Zone 4-5, or earlier? | Zone 4-5 | `research/cloud/Accessory-Acquisition.md` Q3 |
| 157 | 34 outpost chests as a one-time accessory cache? | yes | `research/cloud/Accessory-Acquisition.md` Q5 |
| 158 | Bad-luck counters (600 kills, 20 elites, 4 bosses): keep? | yes | `research/cloud/Accessory-Acquisition.md` Q6 |


### 4c. World, zones, dungeons, quests, prestige

| # | Question | Default | Source |
|---|---|---|---|
| 159 | Zone islands 3x area (R 1,110-1,440) or 3x radius (9x area)? | 3x area | `research/cloud/Zone-Islands-Layout.md` Q1 |
| 160 | Gap between islands 220 blocks, or 150 / 400? | 220 | `research/cloud/Zone-Islands-Layout.md` Q2 |
| 161 | Dragons later fly the gaps toward unlocked islands only? | yes | `research/cloud/Zone-Islands-Layout.md` Q3 |
| 162 | Zone 5 as a cave layer under Zone 4, or its own island? | cave layer | `research/cloud/Zone-Islands-Layout.md` Q4 |
| 163 | Starter shard box 5 x 5 chunks (about 2.8x area), east side fixed at +80? | yes | `research/cloud/Starter-Shards-Plan-2.md` Q1 |
| 164 | Portal Shard from a chest now, Gumbo later - or Gumbo from the start? | chest now | `research/cloud/Starter-Shards-Plan-2.md` Q2 |
| 165 | Existing islands: option A only, or A + B (an "Add the chain" button)? | (no default written) A only | `research/cloud/Starter-Shards-Plan-2.md` Q3 |
| 166 | Outpost beds set respawn, or respawn always at the zone town? | beds set respawn | `research/cloud/Outposts-List.md` Q1 |
| 167 | Slayer boss fights in a private bounty-arena instance, or in the open world with immunity for others? | instance | `research/cloud/Slayers-Spec.md` Q1 |
| 168 | Slayers: five lines at once, or Zone 1-2 first? | Zone 1-2 first | `research/cloud/Slayers-Spec.md` Q2 |
| 169 | Capstone: 3 floors at launch, each floor runnable alone? | yes | `research/cloud/Capstone-Dungeon-Spec.md` Q1 |
| 170 | Capstone solo allowed (scaled), or party of 2+ only? | solo allowed | `research/cloud/Capstone-Dungeon-Spec.md` Q2 |
| 171 | F7 solo enrage 540 s instead of 480 s, or keep 480 and make F7 party only? | 540 on F7 | `research/cloud/Capstone-Floors-4-7.md` Q1 |
| 172 | Master Mode: clamp mobs at level 100, or raise the cap past 100? | clamp at 100 | `research/cloud/Capstone-Floors-4-7.md` Q3 |
| 173 | A-rank chests for a full Aetherium set: about 13, or pity 20 (slower)? | pity 12 | `research/cloud/Capstone-Floors-4-7.md` Q4 |
| 174 | F5 boss copies abilities, including from fallen players: fun or too nasty for solo? | keep; solo copies only the soloist | `research/cloud/Capstone-Floors-4-7.md` Q5 |
| 175 | F6 / F7 puzzle penalty -2 per failed step, or none on F7? | -2 | `research/cloud/Capstone-Floors-4-7.md` Q6 |
| 176 | Floor access gated by "cleared the floor below"? | no, independent | `research/cloud/Capstone-Floors-4-7.md` Q7 |
| 177 | Prestige: items stay and only the level gate resets you, or the harder "Lost Luggage" reset? | items stay | `research/cloud/Prestige-Spec.md` Q1 |
| 178 | Skill floor 1 or 10 after prestige? | 1 | `research/cloud/Prestige-Spec.md` Q2 |
| 179 | Collections count again from 0 (recipes kept), or counts stay and only skills reset? | reset counts, keep recipes | `research/cloud/Prestige-Spec.md` Q3 |
| 180 | +2% XP per prestige, cap 10 prestiges: good size? | yes | `research/cloud/Prestige-Spec.md` Q4 |
| 181 | Prestige 2+ needs the Re-Audit (Lv 75 + Zone 5 guardian) or just a cooldown? | Re-Audit + 3-day cooldown | `research/cloud/Prestige-Spec.md` Q5 |
| 182 | Pocket Shard slots as a perk at prestige 1, 3, 5, 7, 10, or cosmetics only? | perk | `research/cloud/Prestige-Spec.md` Q6 |
| 183 | Dragon scene "Go home" only points you to the Tab clerk (prestige needs Paid in Full), or gives the first prestige at once? | point to the clerk | `research/cloud/Tab-Prestige-Scripts.md` Q1 |
| 184 | Return Visit quest hands out the starter kit at its end, or the kit arrives on arrival? | at the end | `research/cloud/Tab-Prestige-Scripts.md` Q4 |
| 185 | Zone specials only on the zone's island, or global? | island only | `research/cloud/Zone-Specials-Spec.md` Q1 |
| 186 | Daily zone specials + weekly Clerk (two layers), or one? | both | `research/cloud/Zone-Specials-Spec.md` Q2 |
| 187 | Clerk by a server vote later, or pure rotation? | rotation now, vote later | `research/cloud/Zone-Specials-Spec.md` Q3 |
| 188 | Keep the single Clerk with a drawback (Rush Season)? | yes | `research/cloud/Zone-Specials-Spec.md` Q4 |
| 189 | Zone special rollover at 15:00 UTC or another time? | 15:00 UTC | `research/cloud/Zone-Specials-Spec.md` Q5 |
| 190 | Onyxium has no ore source: skip its slot (Cindersteel ore with a Mithril pickaxe) or add an Onyxium source first? | skip | `research/cloud/Zone-4-5-Materials.md` Q1 |
| 191 | Mined veins ever regrow (timed reset, or an admin command)? | no regrow in profile worlds | `research/cloud/Zone-4-5-Materials.md` Q2 |
| 192 | Dragon Scale also from a Zone 5 deep mini-boss (2%) so a Lv 66 player can start Drakonite early? | yes | `research/cloud/Zone-4-5-Materials.md` Q4 |
| 193 | Drakonite Mining XP 100 (1.75 levels per hour) or 120 (same pace as Ember)? | 100 | `research/cloud/Zone-4-5-Materials.md` Q6 |
| 194 | Quest files as plain text + an in-game editor later, or the editor first? | text files first | `research/cloud/SkyyQuests-Spec.md` Q1 |
| 195 | Max active quests: 5 or unlimited? | 5 | `research/cloud/SkyyQuests-Spec.md` Q2 |


### 4d. Pocket Dimension release and the player guide

| # | Question | Default | Source |
|---|---|---|---|
| 196 | Pocket Dimension licence: All Rights Reserved at first, or permissive? | All Rights Reserved | `research/cloud/PocketDimension-Release-Kit.md` Q1 |
| 197 | Keep jar + config folder name `Skyy_SkyySacks` (no migration) or rename to Pocket Dimension? | keep | `research/cloud/PocketDimension-Release-Kit.md` Q2 |
| 198 | First Normal bag free-craftable in the standalone (no collection to unlock it)? | yes | `research/cloud/PocketDimension-Release-Kit.md` Q3 |
| 199 | Player guide in-game (SkyyMenu "Guide" button) or a wiki page first? | wiki / CurseForge first | `research/cloud/Player-Guide-First-Hour.md` Q1 |
| 200 | Keep lore jokes (ticket number, Pebble) in a guide that appears before the tutorial exists? | yes, short | `research/cloud/Player-Guide-First-Hour.md` Q2 |
| 201 | Guide names the starter coin number? | no, "starter coins" | `research/cloud/Player-Guide-First-Hour.md` Q3 |
| 202 | Show Berserker and Monk in the class table before they are playable? | yes, tagged PLANNED | `research/cloud/Player-Guide-First-Hour.md` Q4 |
| 203 | Update the guide when the starter shard chain lands? | yes | `research/cloud/Player-Guide-First-Hour.md` Q5 |


## Dropped (already answered or pointer-only)

| What | Why dropped |
|---|---|
| `research/cloud/Foraging-Armor-Design.md` Q1 (is vanilla Wood armor its own tier) | `docs/answered/gear.md` LOCKED 2026-10-05: "tier 1 = vanilla WOOD armor" for Foraging armor. |
| `research/cloud/Spellbook-Ladder.md` Q7 (recipe copies the shortbow) | `docs/answered/classes.md` R1 LOCKED: wand / spellbook / staff recipes match vanilla weapons of the same material. |
| `research/cloud/Spellbook-Ladder.md` Q8 (Onyxium book = Mithril recipe) | Same R1 + the 2026-10-02 wand answer (Onyxium wand follows Mithril). |
| `research/cloud/SkyyArmory-Roadmap.md` Q5 | Pointer to the weapon-speed questions (rows in 1e). |
| Starter coins once per profile | Kept as a lock; only the vesting change is asked (economy row 4). |
| Class abilities A2 picks, `OPEN-QUESTIONS.md` | Still waiting on the class-ability spec; no cloud file asks them again. |


## For the local session (UNVERIFIED)

- The "answered" check was a keyword grep over `docs/answered/*.md` and `OPEN-QUESTIONS.md`, not a full read. Re-check a row against the topic file before locking it.
- `research/cloud/Capstone-Dungeon-Spec.md`, `research/cloud/Class-Ability-Spec-Draft.md`, `research/cloud/Class-Tree-Paths.md`, `research/cloud/Soul-Orb-Spec.md` and `research/cloud/Starter-Shards-Plan-2.md` have no default in their question lists; the Default column here is the draft's recommendation or marked "(no default written)".
- When Skyy answers, close rows with `python tools/qa_append.py <topic> <file> --close "<words>"`; many rows (1a, 1d) change numbers in several cloud drafts at once (see `research/cloud/Tool-Levels-Revision.md` and `research/cloud/Gathering-Numbers-Reconciled.md` edit lists).


## Questions for Skyy

| # | Question | Default |
|---|---|---|
| A | Is one numbered list like this the right way to ask, or do you prefer one file per topic? | one list |
| B | If you only have 10 minutes: answer sections 1a, 1c and 1d first (tool levels, loot, armor types)? | yes |

