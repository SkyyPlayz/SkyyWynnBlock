# Accessory acquisition - how players earn the booster accessories

Cloud draft, 2026-10-06. Inputs: `research/Booster-Accessories-Spec.md` (lines, rarities, "source words"), `docs/plans/SkyyAccessories-Plan.md`, `research/Accessory-Table-Spec.md` (the craft table), `research/cloud/` Elites-Events, Zone-Bosses, Slayers, Capstone-Dungeon, Outposts, NPC-Shops, Loot-Box-Design. **Every number is a placeholder** (Server Setup rows, section 8). No web research needed: this is our own design on top of locks. Nothing here was checked in the game: see "For the local session".

## 0. Locks this follows

| Lock | What it forces |
|---|---|
| 2026-09-30 (Booster spec) | 4 rarities per line (Normal, Unique, Rare, Legendary); only the best of a line counts; **Fabled / Mythic are rare finds, never crafted**; "a stat that does nothing never goes on a booster" |
| 2026-09-25 (Plan locks 63-76) | most accessories are **crafted**; some come from mobs or chests; collections unlock the next craft tier; crafting a rarity needs the one below as an ingredient |
| 2026-10-05 (economy) | Lantern line sits behind the **Tree Sap** collection; Legendary Lantern = high tier |
| R3 | coins never skip a collection unlock; **NPC shops never sell an accessory** (NPC-Shops-Spec 4); event tokens never buy recipes or unlocks |
| Booster spec "source words" | per line and rarity: Craft, Drop, Chest, Combine, Boss (already written into `acc:defs`) |

The source words are the skeleton. This file turns them into real rates and a timeline.

## 1. The five ways (one source word each)

| Way | Source word | What it is | Where it lives |
|---|---|---|---|
| **Craft** | Craft | previous rarity + materials at the Accessory Table; gated by collection tier (lock 64) | guaranteed path, any player can finish a line by crafting alone |
| **Drop** | Drop | a normal mob drops a **Normal** piece | kill hook (SkyyCollections `CollKillSys` pattern) |
| **Chest** | Chest | a first-open **world chest** (once per profile per chest) | outposts, ruins, dungeon secrets, event chests |
| **Combine** | Combine | **4 pieces of one rarity = 1 of the next**, at the Accessory Table | turns duplicate drops into progress |
| **Boss** | Boss | a boss, elite or slayer boss drops a **Legendary** piece or the **Hardened Core** for the last craft step | zone guardians, slayer bosses, capstone |

New small items this needs (all placeholder names, items with no stats): **Hardened Core** (one per zone, from elites and bosses; the "drop from a harder mob" the Booster spec's Craft word already mentions) and nothing else. No new currency.

## 2. Per line, per rarity (the table the loot pass builds from)

Matches `acc:defs` source words. "Craft" for a folded line means the existing Workbench-now-Accessory-Table ladder.

| Line | Normal | Unique | Rare | Legendary |
|---|---|---|---|---|
| Health, Stamina, Mana, Speed, Regeneration (folded, 5 lines) | Craft | Craft **or** Drop | Craft **or** Chest | Craft **or** Boss |
| Brawler, Stonehide (Drop lines) | Drop | Combine (4 Normal) | Craft (Unique + Hardened Core) | Boss |
| Runic, Razorfang (Chest lines) | Chest | Combine (4 Normal) | Craft (Unique + Hardened Core) | Boss |
| Feather | Craft | Craft | Chest | Chest |
| Lantern (Tree Sap line) | Craft | Craft | Craft | Craft (collection tier gate only) |
| Wave 2 (Prospector, Woodcutter, Harvester...) | Craft | Craft | Chest | Boss |

Rules that stop it going wrong:

- **Craft is always open.** A player who never finds a drop can still reach Legendary on every line by crafting, as fast as their collections allow. Drops and chests are only a **shortcut and a sidegrade** (R3 spirit: nothing is only luck).
- **Fabled / Mythic never come from any row above.** A separate "rare finds" table (section 7) is the only place.
- **No pity on crafting** (no randomness there). Pity only applies to rolls (section 5).
- **Combine** keeps the lower rarity's stack count at the Accessory Table: 4 identical lower-rarity accessories in the bag/inventory, one click, one higher. It refuses a combine that would give a rarity the line does not have (no Legendary by combining Rares of a Boss-only line? see below).

**Open call (Q2):** for Drop/Chest lines the Booster spec lets Legendary come only from Boss. I propose **Rare + 2 Void Fragments + a Hardened Core -> Legendary** as a second path (Craft, still Boss as the shortcut), so a line is never locked behind a fight. If Skyy wants Boss-only for those four, remove the craft row; the loot table is unchanged.

## 3. Zone ladder (what each zone gives)

Zone level bands from `Mob-Levels-Refit.md`. A drop's rarity is capped by its source, so a Z1 mob never drops a Rare.

| Zone | Mob drop (Normal) | Elite adds | Chests give | Guardian (boss) gives | Slayer |
|---|---|---|---|---|---|
| 1 Emerald Wilds (1-20) | Normal | Unique (rare) | Normal, Unique | Unique + Hardened Core 1 | line I-III: nothing, IV-V: Unique |
| 2 Howling Sands (20-30) | Normal | Unique | Unique, Rare (rare) | Rare + Hardened Core 2 | IV-V: Rare |
| 3 Whisperfrost (30-45) | Normal | Unique, Rare | Rare | Rare + Core 3 | V: Rare, VI+: Legendary chance |
| 4 Devastated Lands (45-60) | Normal | Rare | Rare, Legendary (rare) | Legendary (the "Boss" rarity) + Core 4 | Legendary |
| 5 Dinosaur caves (60-75) | Normal | Rare, Legendary (rare) | Legendary | Legendary | Legendary |
| Capstone (76+) | - | - | secret chests: Legendary | floor boss: Legendary (daily-capped) | - |

(Zone 1-2 players need Legendary through crafting + the folded-line Boss sources in Zone 4-5; this is on purpose: a Legendary accessory is a **late game milestone**, Rare is the mid game.)

## 4. Rates (placeholders; per profile; all Server Setup rows)

| Source | Chance | Notes |
|---|---|---|
| Normal mob kill (any zone) | 0.30% to drop one **Normal** piece of a Drop line | only a mob within 10 levels of you counts (no farming Zone 1 at Lv 60) |
| Elite kill | 4% an accessory piece of the zone's top rarity; 8% a Hardened Core | guaranteed gear roll stays (Elites-Events-Spec 1.3) |
| Outpost cache chest | 1 per outpost (34), first open per profile: 1 piece, rarity by zone (Z1 Normal 80 / Unique 20, ... table in the loot pass) | gives the Exploration page a reason to walk to every outpost |
| World ruin / secret chest | first open per profile, 1 piece | the existing SkyyExploration first-open pattern |
| Event chest (Elites-Events 2.4) | 12% one piece of the zone's top rarity, on top of the gear roll | daily cap 12 events already exists |
| Guardian (zone boss) | 25% a piece of the table rarity; the Hardened Core guaranteed on **first kill** per profile, 40% on re-fight | daily re-fight cooldown (Zone-Bosses Q3) |
| Slayer boss | tier I-V: 1%/3%/6%/12%/25% a piece at the zone's best rarity | Slayers-Spec 2 |
| Capstone floor chest | S rank: 1 Legendary piece guaranteed (per floor, daily cap 12 chests) | no coins; the capstone is where Legendary comes **often** |
| Quest rewards | **Tutorial gift**: one Normal Speed and one Normal Health Accessory | so the bag is not empty at Lv 1; the rest is earned |

What does **not** sell or give accessories: NPC shops (R3), event tokens (cosmetics only), the AH (Magic Bags and the Accessory Bag are blocked; accessories **may** be tradable - Q4).

## 5. Pity and line choice (so the roll feels fair)

A drop picks the **line** by weight, not by rarity table alone.

| Rule | Value |
|---|---|
| Base | each line allowed by that source has weight 100 |
| Lines you already own at this rarity or higher in the bag/inventory | weight x0.35 (fewer duplicates) |
| Lines you own nothing of | weight x2 |
| **Bad-luck counter** (per profile, per source type: mob / chest / boss) | after N rolls with no accessory, the next roll is guaranteed: mob 600 kills, elite 20, chest none, boss 4 (the counter resets on any accessory) |
| Daily accessory cap from drops | 40 pieces per profile per real day (a setting; duplicates beyond are still delivered, just not counted) |

Why the weights: Combine needs duplicates of the *same* line, so a gentle duplicate bias (x0.35 not 0) leaves Combine useful while still guiding new players to unseen lines. Persist the counters per profile (`tools/PROFILES-CONTRACT.md`).

## 6. How long it takes (a simple model, to check in the test world)

Assumptions: 400 kills/hour on a mob farm, 1 elite per 15 min, 1 slayer boss per 20 min, all placeholders.

| Goal | By crafting | By drops only | What gates it |
|---|---|---|---|
| First accessory of any line | quest gift at Lv 1 | - | none |
| A Normal piece of every Drop/Chest line (4 lines) | 0 (craft is for folded lines only) | **about 3.3 h** (0.30% x 400 = 1.2 pieces/h; 4 lines, x2 weight for unseen) | zone 1-2 farming |
| Unique on a Drop line (Combine 4 Normal) | - | about 3.3 h of one line, about 13 h for all four | pity helps the last ones |
| Rare on every line | collections gate (Cobalt tier craft) | Hardened Core (8% elite = about 3 h per core) x 4 lines + 4 Unique | Zone 3 |
| Legendary on every line | Zone 4-5 craft gates (Adamantite tier) | boss/slayer/capstone: the 4 boss-only lines need about 8-12 guardian kills | **late game** |
| Full set of 10 lines at Legendary | about 60-80 h of normal play (shared with leveling) | about the same | an end-game goal, as Hypixel's Accessory Power |

The goal is that nobody reaches a full Legendary bag before Level 60 and almost nobody skips crafting.

## 7. Rare finds (Fabled and Mythic) - the later table

Booster spec 4.1: "mythic and fable are rare finds you can't craft". Proposal for the **later** pass (not in this build, Skyy designs each one):

- Each rare find is **its own line of one** (one-per-line stays simple), a named accessory with a special effect, never a number-only upgrade.
- **Fabled (Accessory Power 22):** sources limited to bosses and the capstone, drop chance 1-3% per kill, never from chests. Ideas: **Void-Touched Compass** (outpost warp cooldown halved), **Chieftain's Banner** (Strength +15 while a party member is within 10 blocks).
- **Mythic (Accessory Power 25):** the Dragon and the capstone final floor, 0.5%; or a multi-step **quest** reward (a story branch), so a Mythic is never pure luck. Each is a story object (the Last Stamp style).
- All are **bound to the profile on first pickup** (no trading) so nobody buys a Mythic with coins (R3).

## 8. Server Setup rows (config kit, times in seconds)

`acc.drop.mobChance` 0.003, `acc.drop.mobLevelGap` 10, `acc.drop.eliteChance` 0.04, `acc.drop.coreEliteChance` 0.08, `acc.drop.eventChance` 0.12, `acc.drop.guardianChance` 0.25, `acc.drop.slayerChances` 0.01/0.03/0.06/0.12/0.25, `acc.drop.dupeWeight` 0.35, `acc.drop.newLineWeight` 2.0, `acc.pity.mob` 600, `acc.pity.elite` 20, `acc.pity.boss` 4, `acc.drop.dailyCap` 40, `acc.combine.count` 4, `acc.tutorialGift` on.

## 9. Build order (when the loot pass is built)

| # | Piece | Needs |
|---|---|---|
| 1 | Accessory Table Combine tab (4 -> 1), Hardened Core item | Accessory Table build (PAUSED in `research/Accessory-Table-Spec.md`) |
| 2 | Kill hook + mob/elite roll with weights and pity (`acc:fn:give` already exists in the Booster spec) | SkyyCollections kill pattern, per-profile storage |
| 3 | First-open chest roll for outposts and ruins | Outposts built, SkyyExploration pattern |
| 4 | Event / guardian / slayer / capstone tables | each system's own build |
| 5 | Rare finds (Fabled / Mythic) | Skyy designs one at a time |

## 10. Exploits and checks

| Risk | Handling |
|---|---|
| Duplicate farming one Zone 1 mob for ever | mob level gap rule + daily cap (40) + weights x0.35 |
| Duplicate via logging out mid-chest | chest first-open flag stored before the item is given (SkyyExploration pattern); item given on the player's world thread via `acc:fn:give` (counts before/after, drops at feet if the bag is full) |
| Combine eating a better item | Combine only consumes **exactly** the 4 lower pieces; confirm click (like Bazaar Sell inventory); never touches the equipped copy |
| Legendary via luck before collections | allowed on purpose: drops are a shortcut, crafting is the gate; R3 is about coins and unlocks, and drops give no unlock |
| Pity cheesing by relogging | counters stored per profile, written on every roll |
| Tutorial gift farmed with alt profiles | one gift per profile; it is a Normal item, worth little |

## For the local session (UNVERIFIED)

- Whether `acc:fn:give` exists with the exact signature the Booster spec describes (it was a design in that spec, not shipped).
- The vanilla mob roles per zone and which can be "elites" (Elites-Events says spawn roles are UNVERIFIED).
- Whether first-open chests (outposts) can be created in worlds the way SkyyExploration does it; whether one chest can be per-profile.
- That the Combine tab fits the Accessory Table's tab system (Accessory-Table-Spec 1.5).
- The real kill pace and elite pace of a normal player (all section 6 times are guesses).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is the gift of one Normal Speed + Normal Health at the tutorial OK? | yes |
| 2 | Drop/Chest lines: allow a craft path to Legendary (Rare + 2 Void Fragments + Hardened Core) as well as Boss? | yes (no line locked behind a fight) |
| 3 | Should Legendary accessories be mostly Zone 4-5 (as in section 3) or earlier? | Zone 4-5 |
| 4 | Can accessories be traded / sold on the AH? (Magic Bags and the Accessory Bag are blocked.) | yes for Normal-Rare, **bound** for Legendary and rare finds |
| 5 | Are 34 outpost chests OK as a one-time cache? | yes |
| 6 | Bad-luck counters (600 kills, 20 elites, 4 bosses): keep? | yes |
