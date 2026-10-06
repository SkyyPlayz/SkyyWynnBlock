# Slayers spec - repeatable boss bounties (the core loop, not the spine)

Cloud draft, 2026-10-06. `docs/plans/SkyyDungeons-Plan.md`: slayers are a **core loop, not side content**, they start with combat (phase P4) and are **not the leveling spine**: a slayer **never unlocks the next zone island**. This spec proposes five slayer lines (one per zone), five tiers each, rewards and anti-farm rules.
Web research (SkyBlock Slayers) is from search snippets (the wiki pages cannot be fetched here); engine questions are UNVERIFIED. Companion docs: `SkyyQuests-Spec.md` (slayers are repeatable quests with a bounty objective), `Elites-Events-Spec.md`, `Zone-Bosses-Ideas.md`, `NPC-Shops-Spec.md`, `Mob-Levels-Refit.md`.

## 0. What SkyBlock does (research)

| Fact | Source |
|---|---|
| A Slayer quest = **kill a specific mob family to earn Combat XP, then the Slayer boss spawns**; bosses have **5 tiers (I-V)**; Tier III+ also spawns **mini-bosses** that give much more Combat XP | search snippets, [Slayer](https://hypixelskyblock.minecraft.wiki/w/Slayer), [Zombie Slayer](https://hypixelskyblock.minecraft.wiki/w/Zombie_Slayer) |
| Tiers cost coins and need Combat XP: **Revenant Horror** T1 2,000 coins / 150 XP, T2 7.5k / 1,440, T3 20k / 2,400, T4 50k / 4,800, T5 100k / 6,000; boss Slayer XP **5 / 25 / 100 / 500 / 1,500** (Wolf T1-T4 confirm 5 / 25 / 100 / 500) | snippets |
| Boss health ranges from **500 (T1, Lv 10) to 10M (T5, Lv 1580)**; Tier V bosses (2 exist) have unique abilities | snippet, [Revenant Horror](https://hypixelskyblock.minecraft.wiki/w/Revenant_Horror) |
| Defeating a boss gives **Slayer XP -> Slayer levels**, which unlock **recipes and permanent stat boosts**; bosses drop **guaranteed tokens** used in those recipes | snippets |
| **Combat Wisdom** for each unique boss tier slain (max +36) | snippet |
| An **RNG meter** (unlocked after Tier III) guarantees a rare drop after many bosses without one | snippet, [Drop Chance](https://hypixelskyblock.minecraft.wiki/w/Drop_Chance) |
| Slayer level thresholds for the Zombie line (5 / 15 / 200 / 1,000 / 5,000 / 20,000 / 100,000 / 400,000 / 1,000,000 XP) | memory (UNVERIFIED) |
Lessons taken: **cost + XP-to-spawn + boss tiers + token drops + level perks + RNG meter**; SkyBlock's boss is visible only to its owner (not possible for us, see 2.2).

## 1. The five lines

One per zone, built from vanilla creature families (names from the vanilla creature lists in the Zone boss research); bosses are re-themed and scaled by `scale.role`:

| Zone | Slayer line (working name) | Mob family (the grind) | Boss (vanilla base, UNVERIFIED role ids) | Town board |
|---|---|---|---|---|
| 1 Emerald Wilds | **Skeleton Slayer** "The Late Fee" | Skeleton Fighter, Skeleton Archer, Burnt skeletons | **Burnt Skeleton Praetorian** (vanilla Zone 1 mini-boss) | Department of Arrivals |
| 2 Howling Sands | **Scarak Slayer** "The Exterminator" | Scarak fighters / larvae, Feran | **Scarak Overseer** (the Broodmother's lieutenant; a scaled Scarak) | Annex of Revisions |
| 3 Whisperfrost | **Outlander Slayer** "The Repo Man" | Outlander warriors, cultists, rangers | **Outlander Colossus** (listed in Zone 3 creature lists) | Cold Storage |
| 4 Devastated Lands | **Ember Slayer** "The Fire Marshal" | Emberwolves, fire golems, raptors | **Emberwulf Alpha** (a scaled Emberwulf) | Observatory of Almost |
| 5 Dinosaur Caves | **Dino Slayer** "The Paleontologist" | raptors, triceratops, cave rexes | **Raptor Matriarch** / Cave Rex | the Egg Desk |
Each line is a repeatable **bounty** posted at the zone's **Bounty Clerk NPC** (the lore voice: "Wanted: one skeleton, overdue").

## 2. The quest flow

### 2.1 Steps
1. **Start** at the Bounty Clerk: choose the line (only the zone's line is offered; lines of earlier zones stay available) and the **tier**; pay the coins; one active slayer quest per profile (SkyyQuests `maxActive` rule: slayers count toward 1 of the 5 slots).
2. **Bounty phase:** kill the family's mobs **in the zone's levelled areas**; each kill of a mob **within 3 levels of the zone band** fills the **bounty bar** (a HUD line "Bounty 12 / 25"). Tier III+ spawns **mini-bosses** at 33% and 66% of the bar (more XP, a token each).
3. **Boss phase:** when the bar fills, the boss **spawns** at your position (open world: see 2.2).
4. **Win:** kill the boss: Slayer XP + tokens + a drop roll; the quest closes; you can immediately start another.
5. **Fail:** you die, leave the area (more than 80 blocks from the boss), or the **20-minute timer** ends: the quest fails, **coins are not refunded**, there is no item or level loss beyond the normal coin death penalty (the 10-25% coin loss applies on death as usual; a row can waive it for slayer deaths).

### 2.2 Where the boss fights (the engine problem)
SkyBlock's boss is visible and attackable only by its owner; **we cannot hide an entity per player** (UNVERIFIED; no known per-player visibility in the engine). Options:
| Option | What | Verdict |
|---|---|---|
| **A. Bounty arena instance** (recommended) | after the bounty phase the board teleports you (and your party) into a small **instance world** (like the dungeon / island instances: a copied template), the boss spawns there, **only your group** is inside; the world is deleted when empty | clean, supports parties, no stealing; costs an instance load (about 3-5 s) |
| B. Open-world boss with a private marker | the boss spawns near you with a tag and **damage from non-owners is cancelled** (an immune flag, "not your bounty") | no instance load, but others see it and cannot hurt it (confusing); boss kill by a party member counts for the owner only |
| C. Open-world shared boss | anyone can hit it, loot to the top damage | steals, griefing: rejected |
Recommended **A**; fall back to **B** if instance loads hurt. Arena size 40 x 40, one **arena template per line** (5 templates, reskinned), a safe return portal.

### 2.3 Party rules
Up to **4 players** in the arena; the boss health scales **+50% per extra player** (cap +150%); **only the quest owner** gets the Slayer XP, tokens and the RNG meter progress; **helpers** get normal combat XP, a **consolation chest** (a gear roll) and the title credit "Helped"; helpers need no slayer quest. A helper may be a different class (healers welcome).

## 3. Tiers, bosses and costs

Boss level uses the zone band; health multiplier is vs a normal mob of the same level (Mob-Levels-Plan scaling already applies); XP numbers follow SkyBlock's 5 / 25 / 100 / 500 / 1,500.

| Tier | Bounty kills | Boss level (Zone 1 / 2 / 3 / 4 / 5) | Health x | Target solo time at the zone's gear | Slayer XP | Mini-bosses |
|---|---|---|---|---|---|---|
| I | 15 | 4 / 22 / 32 / 47 / 62 | x6 | 40 s | 5 | no |
| II | 25 | 8 / 24 / 35 / 50 / 65 | x12 | 90 s | 25 | no |
| III | 40 | 11 / 26 / 38 / 53 / 68 | x24 | 2.5 min | 100 | 2 |
| IV | 60 | 16 / 28 / 42 / 57 / 72 | x48 | 4 min | 500 | 3 |
| V | 80 | 21 / 30 / 46 / 61 / 76 | x96 | 6 min (a party recommended) | 1,500 | 4 + a unique mechanic |
(Boss level = band floor + span x 0.15 / 0.35 / 0.55 / 0.8 / 1.05; Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60, Zone 5 60-75.)

### 3.1 Coin cost (a sink; SkyBlock multipliers x1 / 3.75 / 10 / 25 / 50 on a per-zone base)
| Tier | Zone 1 | Zone 2 | Zone 3 | Zone 4 | Zone 5 |
|---|---|---|---|---|---|
| I | 400 | 1,500 | 5,000 | 18,000 | 60,000 |
| II | 1,500 | 5,600 | 18,750 | 67,500 | 225,000 |
| III | 4,000 | 15,000 | 50,000 | 180,000 | 600,000 |
| IV | 10,000 | 37,500 | 125,000 | 450,000 | 1,500,000 |
| V | 20,000 | 75,000 | 250,000 | 900,000 | 3,000,000 |
(For scale: the Bazaar's Copper Ore is 5 coins and Iron 16, so Zone 1 Tier I = about 80 copper ore; the **Tab** is the endgame sink, slayers are the mid-game sink.) Rows editable.

### 3.2 What a boss does (one mechanic per tier step)
Bosses are **the zone's creature but with the zone's mechanic** (Zone-Bosses-Ideas): Zone 1 dodge telegraphs, Zone 2 positioning, Zone 3 warmth, Zone 4 line of sight, Zone 5 everything. Tier V adds **one unique ability** (like SkyBlock's two unique T5 bosses): Skeleton T5 "Overdue Notice" (a delayed area stamp), Scarak T5 "Egg Clutch", Outlander T5 "Ice Auction", Ember T5 "Meltdown", Dino T5 "Stampede Call".

## 4. Slayer levels and perks

| Level | Slayer XP (total) | Perks (per line; placeholders) |
|---|---|---|
| 1 | 5 | +2% damage to the family; unlocks the line's first recipe |
| 2 | 25 | +3% damage; +2 max Health |
| 3 | 150 | +5% damage; recipe 2 (weapon) |
| 4 | 750 | +7% damage; +4 max Health; the RNG meter appears at Tier III |
| 5 | 3,000 | +9% damage; recipe 3 (armor piece) |
| 6 | 10,000 | +12% damage; +6 max Health |
| 7 | 30,000 | +15% damage; recipe 4 (accessory); the line title |
(7 levels instead of SkyBlock's 9 because we have 5 lines; thresholds are placeholders: about 20 Tier V kills for level 7.)
**Combat Wisdom**: each unique boss tier slain gives +1 (T I-III) or +2 (T IV-V) combat XP bonus, max +20 per line (a stat the Stats page shows when XP Bonus exists).
Perks apply only vs the line's mob family and to **max Health**; no global stat inflation.

## 5. Drops and recipes

| Reward | Detail |
|---|---|
| **Tokens** (guaranteed): "Praetorian Tokens", "Scarak Plates", "Outlander Seals", "Ember Cores", "Raptor Claws" | the recipe currency; amount by tier (T I 1, II 3, III 8, IV 20, V 50); they **count for a collection** (a slayer collection, no coin bypass: R3) |
| **Recipes unlocked by Slayer level** (4 per line) | a weapon, an armor piece, a pet-like **trinket / accessory** each, at the zone's level band (Zone 1 Lv 15-20, Zone 2 25-30, ...), gear rolls through SkyyGear (so they are real gear with rarity, not fixed items) |
| **Boss drop roll** (rare) | the line's **signature drop** (a unique weapon variant or a pet egg of the zone), chance by tier T I 0.5%, II 1%, III 2%, IV 4%, V 8% |
| **RNG meter** (after Tier III) | every boss without the signature drop adds meter; at **100%** the drop is guaranteed (SkyBlock's RNGesus meter); the meter fills by tier (T III +1, IV +3, V +8 per kill) |
| Coins | none (no coin faucet from bosses) |
| Pets | the Zone line gives a **pet egg chance** (common-uncommon, T V rare): ties to Pets-Spec |
| Combat XP | the boss's XP follows health (large) and mini-bosses give extra |
| Elite drops | the existing elite rule: a guaranteed gear roll on the boss |

## 6. UI and tooling

| Piece | Design |
|---|---|
| Bounty Clerk NPC | a dialogue window (SkyyQuests) with tier buttons showing cost, XP, boss level, your requirement ("needs Swordsmanship 16") |
| Bounty bar | a one-line **HUD tracker widget** (SkyyQuests tracker): "Skeleton Bounty T III  18 / 40" |
| Slayer page (`/slayer`) | per line: level, XP bar, perks list, the **RNG meter**, recipes (locked / unlocked), best time |
| Chat | boss spawn / win / fail lines in the lore voice ("The Late Fee has come due.") |
| Quest integration | a slayer is a **repeatable SkyyQuests quest** with the new objective `bounty` (family, kills) and `boss` (role, tier) |

## 7. Anti-farm and balance

| Risk | Handling |
|---|---|
| **Spamming Tier I for XP** | cost grows; XP per tier is small; level-gap rule: a tier whose boss level is **more than 8 below** your class skill gives **25% XP** |
| **Level-boost carries** (a high-level friend kills for a low player) | only the **owner's XP** is paid; the **boss level shown vs the owner's level** sets the rewards; helper damage over 80% of the total sets the quest to "carried": XP halved |
| **Bounty farming with AFK mobs** | kills in a spawner area are rare; the per-kill counting rule (mob within 3 levels of the zone band) + a **cap of 4 bounty kills per 10 seconds** |
| **Token market flips** | tokens are **bound to the profile** (no AH / trade) but can be spent only through recipes |
| **Death-loop** | a failed quest has a **60 s cooldown** before the next bounty |
| **Alts** | each profile separate; coins are the cost |
| **Boss stuck** | arena instance has a timeout and a **leave** portal |
| **Elite + slayer stacking** | no elites inside bounty arenas |
| **Dungeon progression** | slayers are optional; they never gate a zone or the capstone (spine rule) |

## 8. Server Setup rows (sketch)
`slayer.enabled`, per-line enable, `slayer.tierCosts` (a 5 x 5 table), `slayer.bountyKills` (15,25,40,60,80), `slayer.bossHealthMult` (6,12,24,48,96), `slayer.xpPerTier` (5,25,100,500,1500), `slayer.levelXp` (7 numbers), `slayer.timerSeconds` (1200), `slayer.partyMax` (4), `slayer.partyHealthPercent` (50), `slayer.rngMeter` (on), `slayer.failCooldownSeconds` (60), `slayer.instance` (on; off = option B).

## 9. Build plan
| Phase | Content |
|---|---|
| 1 | the Bounty Clerk + quest objective `bounty` + boss spawn + the arena template (Zone 1 line only), the tiers I-III, tokens, level 1-3 |
| 2 | the other four lines, tiers IV-V, the slayer page, the RNG meter, mini-bosses |
| 3 | the signature drops, recipes (gear rolls), accessories, titles, pets eggs |
| Needs | SkyyQuests (objectives), SkyyMobs (`mob:fn:setLevel`, `scale.role`), SkyyGear (recipes), instance templates (SkyyIslands / Dungeons plan) |

## 10. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Per-player entity visibility: any way to hide an NPC from other players (or to make it invulnerable to others)? If not, instance option A. |
| 2 | Cost of spawning an instance world per bounty (3-5 s?) and cleanup. |
| 3 | The vanilla role ids for the five bosses (Burnt Praetorian, a Scarak, Outlander Colossus, Emberwulf, Raptor) and their moves for the scaled versions. |
| 4 | Whether the kill event can attribute kills to the **owner** when a pet or a party member lands the hit (Pets: the owner gets the kill; party: killer's credit). |
| 5 | The existing combat-XP share rule (party combat XP 50% within 48 blocks) vs bounty counting. |

## 11. Questions for Skyy
1. Boss fights in a **bounty arena instance** (recommended) or in the open world with immunity for others?
2. Five lines (one per zone) or fewer for launch (e.g. Zone 1 and 2 first)? (Recommended: Zone 1-2 first.)
3. Coins: are the costs (Zone 1 Tier I = 400) a sensible mid-game sink, or should they be higher?
