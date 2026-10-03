# Elites and world events - spec draft (SkyyMobs stage 3)

Cloud draft, 2026-10-03. Paper design; nothing built. Builds on `research/Mob-Levels-Plan.md` section 11 and the locks in OPEN-QUESTIONS (R5 2026-10-02: **elites later = 3% chance, +3 levels, 2x health, 1.3x damage, a guaranteed gear roll;
no mob armour; no night bonus**; mob difficulty presets Easy 4%/2%, **Normal 6%/3% default**, Hard 8%/4%, caps health x6 / damage x3.5). Master plan lists "World Events: dynamic wave-defense events spawning in the open world" under late side content
(P7), borrowing patterns from the existing mod families PJ-MobEvents / InvasionX / endless-elite-mobs. Nothing here needs game files except where marked UNVERIFIED.

## 1. Elites

### 1.1 The locked numbers

| Rule | Value |
|---|---|
| Chance | **3%** per spawn (seeded by the mob's UUID so a reload keeps it) |
| Level | **+3** over the rolled level (never above the zone's top + 3) |
| Health / damage | **x2 / x1.3** on top of the level scaling (difficulty preset stays) |
| Name | prefix "Elite" ("[Lv 12] Elite Skeleton Fighter"); plate colour one band up |
| Drops | a **guaranteed SkyyGear drop roll** with a rarity shift (above normal mobs) + the normal drop list |
| Excluded | animals, passive mobs, quest bosses, dungeon bosses (those have their own levels) |

### 1.2 Affixes (my proposal - no extra raw stats, only behaviour)

An elite gets **one affix** in Zones 1-3 and **two** in Zones 4-5 (Skyy can lower this). Affixes change *how* the fight plays, not the locked numbers, so balance stays predictable.

| Affix | Behaviour | Counter | Extra loot weight |
|---|---|---|---|
| **Shielded** | Blocks the first 3 hits (a visible glow) | burst it down | +10% |
| **Swift** | +20% move speed, short dash at you | kite, ranged | +10% |
| **Vampiric** | Heals 10% of damage dealt | burst, avoid trades | +10% |
| **Splitting** | At 50% health spawns 2 weaker copies (50% health each, same level -2) | kill the copies first | +15% |
| **Frenzied** | Below 40% health +25% attack speed | CC / dodge | +10% |
| **Explosive** | Explodes when it dies (a telegraphed circle, 2 s) | step back | +5% |
| **Thorned** | Reflects 8% of melee damage taken (not ranged) | ranged / magic | +10% |
| **Voidtouched** | Spawns with a Void hiccup effect: a slow aura around it (ties to the lore) | kill fast | +15% |

Rules: no affix stacks the same twice; elites of passive-ish species (Kweebecs) never roll; the plate shows the affix icon in the name ("[Lv 12] Elite (Thorned) Trork Warrior"). Balance guard: the combined elite stat cap is the existing caps (health x6, damage x3.5).

### 1.3 Rewards
| Drop | Rule |
|---|---|
| **Gear roll** | guaranteed, one unidentified item at the elite's level (+/- `loot.mobSpread`), rarity weights x1.5 |
| **Elite essence** | 1-2 "Elite Essence" items (a per-zone crafting material; ties to pet/shard crafts) |
| XP | follows mob health (x2 health = ~2x XP) automatically (R5) |
| Bonus drop | the +1% per level bonus drop chance applies on top |
| Coins | none (no coins from mobs yet - R5) |

### 1.4 Spawning
- Roll once when a mob first spawns (seeded). A reload does not reroll.
- **No elites during world events' normal waves**; the event has its own elite wave (below).
- A server cap: at most N elites alive per zone world (default 12) so a stray area is not flooded; extra rolls lose their elite status.
- Not in the starter chain, nor in the player's personal island.

## 2. World events

### 2.1 Concept
A world event is a **timed, open-air wave defense** in a zone: a rift opens, creatures pour out, any nearby players can join, a boss wave ends it, everyone who took part gets a reward chest. It is public, group-friendly, and the main way of "something happening" in the open world. In the lore, every event is **a Void hiccup** ("another hiccup" - the same joke as content updates).

### 2.2 The flow

| Phase | What happens | Time |
|---|---|---|
| 1. Warning | Chat and a map marker: "HIC. The Void is about to hiccup near the Everfrost." The Board shows the location. | 60 s before |
| 2. Rift opens | A glowing rift appears at a pre-set spot in the zone (a marker in a ring), creatures spawn in waves around it | - |
| 3. Waves | 5 waves of mobs at the zone's level band (the ring's level), each bigger; wave 3 and 5 include elites | about 8-10 min |
| 4. Boss | A **hiccup boss** (a themed mob at band top + 3, elite-style but x5 health) | about 2 min |
| 5. Close | The rift closes, a chest appears at the site for 5 minutes | - |
| Failure | If every participant dies / leaves, the event ends without a reward and cools down | - |

Participation: you count if you dealt damage / took part within 60 blocks of the rift (a score: damage + kills); minimum score for the reward chest = 10% of the average (so AFK joiners get nothing).
Trigger: a timer per zone world (default **every 45 min**, only if at least 1 player is in the zone, with a random 0-15 min jitter, never two events at once in a zone), plus an admin command `/event start <zone>`.
Scaling: +25% health per extra participant (cap +100%), spawn counts x(1 + 0.15 per participant) so 1 player or 6 players both have a fair fight. Level follows the ring at the rift (SkyyWorldGen / SkyyMobs band).

### 2.3 Event types by zone (themes)

| Zone | Event | Wave mobs | Boss | Rift look |
|---|---|---|---|---|
| 1 Emerald Wilds | **Trork Raid** | Trork Warriors, Fen Stalkers, Skeleton Fighters | Trork Chieftain (vanilla boss) | Trork war banner + fire |
| 2 Howling Sands | **Scarak Swarm** | Scarak larvae, Feran, sand skeletons | Scarak Broodmother (a smaller one) | a cracked dune with eggs |
| 3 Whisperfrost | **Frost Siege** | Outlander warriors/cultists, frost skeletons, Yetis (late wave) | Outlander Chief or Yeti | a ring of ice crystals |
| 4 Devastated Lands | **Ember Surge** | Emberwulf, fire golems, raptors | Fire Golem (Ember Warden mini) | a lava crack |
| 5 Dinosaur caves | **Stampede** | raptors, triceratops, pterodactyls | Cave Rex | a bone ring |
| Any | **Void Hiccup** (rare, 10% of events) | Void creatures (crawlers, void spawn, flying eyes) | a Void Spawn captain | a purple rift; ties to the lore |

Vanilla creature names come from web search lists and the Dragon/boss idea docs; exact spawn roles are UNVERIFIED.

### 2.4 Rewards (event chest)

| Reward | Rule |
|---|---|
| Event chest per participant | one chest, only the owner can open it; items: **1 gear roll** (the zone's level, rarity shift by score), 1-3 **Void Fragments** (see Pocket Shards / Pets / Zone Bosses), event tokens, a chance at a pet egg of the zone (common/uncommon) |
| **Event tokens** | spent at the zone's town "Event Vendor" for cosmetics, a Pet Treat bundle, titles - never recipes or unlocks (R3: coins never skip unlocks; tokens neither) |
| XP | kill XP counts normally; a participation bonus of 5% of the event's total kill XP |
| Cap | the gear roll and Void Fragments reward once per event per profile; at most 12 event rewards per real day per profile (setting) |

### 2.5 Optional later: "mayor" style rotating buffs
SkyBlock's rotating global buffs are a separate small system: every in-game day or real day the Board announces a **zone special** (+10% XP in Zone N for 1 hour, +10% drops, or a double-event). Keep as a later idea. Ties to the Board jokes.

## 3. Exploit and balance check

| Risk | Handling |
|---|---|
| **Elite farming** at a spawner | 3% per spawn, per-zone alive cap; XP follows health; level-gap XP rule (R5) reduces XP from far-below mobs |
| **AFK joining events** | participation score minimum; leaving the 60-block radius pauses credit |
| **Event camping** (waiting for the timer) | jitter on the timer, only fires if players are present; reward cap per day |
| **Alt profiles spawning events** | events need real players; rewards per profile are capped per day |
| **Reward duplication via chests** | chest bound to the profile (owner-only) and removed after 5 min unopened (items go to the owner's mailbox or are lost - decide) |
| **Party-share abuse** (a high-level friend carries a low-level) | level-gap XP rule applies per member; rewards use each member's own score |
| **Boss health scaling griefing** (solo with many alts) | the participant cap on scaling (+100%) |
| **Server load** | one event per zone at a time; spawn rate-limited per tick; waves cap at 60 mobs alive |
| **Players in creative/spectator** | never counted |
| **Elite + event + difficulty stacking** | existing caps (health x6, damage x3.5) apply at the end |

## 4. Server Setup rows (sketch)

Elites (SkyyMobs): `elite.enabled`, `elite.chance` (3), `elite.levels` (3), `elite.hp` (2), `elite.dmg` (1.3), `elite.prefix`, `elite.gearRoll`, `elite.affixes` (count by zone; affix on/off list), `elite.maxAlive` (12).
Events (new mod or SkyyMobs part): `events.enabled`, `events.intervalSeconds` (2700), `events.jitterSeconds` (900), `events.minPlayers` (1), `events.waveCount` (5), `events.timeLimitSeconds`, `events.scaling` (+25% per player, cap 100%),
`events.minScorePercent` (10), `events.rewardChestSeconds` (300), `events.dailyRewardCap` (12), per-zone event table (type, mobs, boss, rift marker positions), `events.tokenShop`. Times in seconds (PROJECT-RULES).

## 5. Build order

1. Elites (small): the seeded 3% roll, the multipliers, the plate prefix, the gear roll. Fits SkyyMobs stage 3 after stage 1/2 (stage 1 is live).
2. Affixes (medium): start with 3 simple ones (Shielded, Swift, Thorned) that need no new engine pieces beyond effects and damage events.
3. One world event (Trork Raid) as the template; then reskin for the other zones.
4. Event vendor and tokens.

## 6. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | SkyyMobs 0.1.1 already live? Confirm the plate and difficulty presets (R5). Elite hooks onto the same spawn listener. |
| 2 | Wave spawning on a zone island: can we spawn NPCs by script at a point (SkyyMobs `mob:fn:setLevel` stage 3), and are spawn markers needed for flying/special mobs? |
| 3 | The event rift marker positions per zone/island (SkyyWorldGen ring data `wg:fn:ring`), and how to pick one in a ring that has players. |
| 4 | A boss bar and map marker API for events (vanilla boss bar, map markers). |
| 5 | Effects needed for affixes (shield, aura, thorns) - check the vanilla EntityEffect set and damage events. |
| 6 | How world threads handle spawning dozens of mobs in one tick (rate limit per tick). |
| 7 | Whether existing mods (PJ-MobEvents / InvasionX / endless-elite-mobs, named in the master plan) allow borrowing ideas - ideas only, never code unless licensed (PROJECT-RULES 2). |

## 7. Questions for Skyy

1. One affix per elite in Zones 1-3 and two in Zones 4-5 - or always one? Recommended: as proposed.
2. Is an event timer of 45 minutes per zone right, or should events be rarer (every 2 hours)? Recommended: 45 min (more social), tune live.
3. Should event rewards include a pet egg chance, or keep eggs for bosses and dungeons only? Recommended: a small common-egg chance only.
4. Do you want the Void Hiccup (purple, rare, any zone) as the headline event type? Recommended: yes, it is the lore joke.
