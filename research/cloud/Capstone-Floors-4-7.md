# Capstone floors 4-7 - the later audits

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/cloud/Capstone-Dungeon-Spec.md` (whole file), `research/cloud/Capstone-Sets.md` (whole), `research/cloud/SkyyArmory-Roadmap.md` (tiers T11 Voidglass 76-88, T12 Aetherium 86-100), `research/cloud/Zone-Bosses-Ideas.md` (boss health rule), `research/cloud/Mob-Levels-Refit.md` (health x1 + 0.04 per level, cap x4; damage cap x2.5), `research/Gear-Levels-Wynn-Spec.md` (level curve F(L)), `research/cloud/Class-Ability-Spec-Draft.md` (unit H = one full hit), `research/cloud/Dragon-Quest-Spec.md` (section 6, the mate), `research/cloud/Elites-Events-Spec.md` (Void creatures). Every number is a placeholder and a Server Setup row (section 11); times in seconds. Every game fact is UNVERIFIED (no game files here).

## 0. Decisions followed (not re-decided)

| Decision | Source |
|---|---|
| One capstone dungeon "The Final Audit", 7 floors, **3 at launch** (F1-F3), F4-F7 are phase 3 | `research/cloud/Capstone-Dungeon-Spec.md` sections 3, 8 |
| Floor level 76 + 3 per floor (F4 = 85, F5 = 88, F6 = 91, F7 = 94); boss = floor + 3 (88 / 91 / 94 / 97) | same, section 3 |
| Floor names and bosses F4 The Dragon's Nest / Dragon's Mate, F5 The Lost & Found / The Unclaimed, F6 The Void Counter / Ticket #1, F7 The Auditor's Chair / The Auditor | same, section 3 (kept; they are also used by `research/cloud/Capstone-Sets.md` section 5) |
| Party 1-4, health `base x (1 + 0.4 x (players - 1))`, damage +10% per extra player, 3 revives (solo 1), 3 phases, enrage 480, no flying, doors lock until cleared | same, sections 2, 6 |
| 300-point score, ranks S 270 / A 230 / B 160 / C 100, chest rolls D 1, C 1+, B 2, A 3, S 4, 12 chests a day, **no coins** | same, sections 5, 10 |
| Set rarity drops only here; sets drop from the boss chest only; Voidglass F1-F4, Aetherium F5-F7; chance 8% a roll, pity 12 chests | `research/cloud/Capstone-Sets.md` sections 5, 6 |
| Floor = start room + 5-8 chambers + Red Tape boss gate + arena; secrets and buff rooms come on top; floors are independent runs; Master Mode is side content, never needed for the spine | spec sections 3, 4 |

Gaps this file fills (my proposals): themes, rooms, puzzles, mobs, boss moves, numbers, build order. The ten puzzle/room names below are new; the five old puzzles (Stamp Order, Queue Maze, Ledger Balance, Paper Shredder, Index Cards) stay F1-F3 only.

## 1. Floor overview

| | F4 | F5 | F6 | F7 |
|---|---|---|---|---|
| Name | The Dragon's Nest | The Lost & Found | The Void Counter | The Auditor's Chair |
| Department | **Unhatched Claims** (the Egg Registry) | **Lost Property** | **Customer Waiting** | **Internal Audit** |
| Mob / boss level | 85 / 88 | 88 / 91 | 91 / 94 | 94 / 97 |
| Class skill needed | 85 | 90 | 95 | 100 |
| Gear that drops | Voidglass 85, any piece | Aetherium 88, piece 1 | Aetherium 91, piece 2 | Aetherium 94, piece 3 + any |
| Boss | The Dragon's Mate | The Unclaimed | Ticket #1 | The Auditor |
| Taught mechanic | flight + lines | copies | queue + numbers | all of them |
| Target time (100 speed points) | 22 min | 24 min | 26 min | 28 min |

Voice samples (Department of Arrivals): F4 door sign "Unhatched claims are processed in the order they hatch. Please do not rush the egg." F5 "Item not found? It is probably found. Ask at another counter." F6 "Your number is 1. There is nobody ahead of you. There never was." F7 "This audit is a formality. The formality is you."

## 2. F4 - The Dragon's Nest (Unhatched Claims)

A cavern registry: rows of nest-shelves with labelled eggs, warm lava vents, a mother-dragon mural. The Dragon's Mate is the lonely dragon's partner (`research/cloud/Dragon-Quest-Spec.md` section 6): not evil, a very tired clerk on the night shift.

| Rooms (chambers = combat + puzzle + trap + mini-boss, 5-8) | Count |
|---|---|
| Combat | 3 (Hatchery, Ash Gallery, Roost Stairs) |
| Puzzle | 2 (Warm Nest, Egg Run) |
| Trap | 1 (**Ember Crawl**: floor tiles heat in a pattern, 3 s warning, -5 score per scorch) |
| Mini-boss | 1 (a Cave Rex elite, 2x health, tail sweep) |
| Buff rooms / secrets (on top) | 2 / 3 |
| Red Tape gate | kill 3 marked Registry Clerks (tiny hatchlings in glasses) |

**Puzzle F4-A "Warm Nest"** (Lights Out). 9 egg plates in a 3 x 3 grid, each warm (lit) or cold. Stepping on a plate flips it and its 4 side neighbours (diagonals no). Goal: all 9 warm. A random start from a seeded list is always solvable (python check: all 512 states reachable, worst case 9 presses). Each press beyond **12** = a cold snap, -2 score; reward when solved: a buff room opens. Party play: the plates take only one player at a time; players may split the grid.
**Puzzle F4-B "Egg Run"** (timing carry). Three "Cold Egg" blocks lie at one end of a 3-lane corridor; the party carries them to three heat nests at the other end within **45 s** per egg. A dragon-shadow patrol sweeps the lanes in the order left, middle, right, each lane flashing red for **1 s**, then burning for **1 s**, every 3 s cycle; carrying an egg slows movement by 30% and blocks abilities. A burn hit breaks the egg (it respawns at the start) and costs -5 (trap rule). Solo carries one egg at a time; each extra player may carry one more.

**Mobs (UNVERIFIED role ids):** `Raptor_Cave` (hatchlings, fast), `Rex_Cave` (the elite), `Pterodactyl` (dives from the ceiling), `Trillodon` (burrower), `Scarak_Fighter` (nest guards), `Emberwulf` (ash hounds). The first four are named in `research/cloud/Zone-Bosses-Ideas.md` as seen in the files (Dragon-Pets-Idea); the other two come from web guides.

### 2.1 Boss - The Dragon's Mate (Lv 88; base `Dragon_Fire` or `Dragon_Frost`, recoloured: UNVERIFIED)

| Phase | Health | Moves (telegraph) | Adds | Safe play |
|---|---|---|---|---|
| 1 "Night Shift" | 100-70% | **Flame line**: red ground line, 3 s, 2 blocks wide, 20 long. **Tail sweep**: 270 degree arc, 1.5 s wind-up, safe directly behind the dragon. | every 40 s, 4 eggs hatch into `Raptor_Cave`; a hatchling alive 15 s heals the boss 2% | kill the eggs while they glow |
| 2 "Overtime" | 70-35% | boss takes off (untargetable for 8 s, twice): **fire rain** circles (radius 3, 2 s, 12 a wave), **dive bomb** (shadow grows, 2.5 s, lands with a 6 block shockwave), then lands for a **10 s damage window** | 4 `Pterodactyl` per flight | stand at the edge of rain circles, bait the shadow |
| 3 "Lonely" | 35-0% | double flame line (a cross), tail sweep + breath combo, ground cracks (3 s) | 1 `Rex_Cave` + 6 `Pterodactyl`; no egg heals now | focus the Rex first, then the boss |
| Enrage | 480 s | damage +10% every 10 s until a wipe | | |

## 3. F5 - The Lost & Found (Lost Property)

A warehouse of heaps: odd luggage, floating umbrellas, dimensional doors to counters that do not exist. The Aetherium sets start here.

| Rooms | Count |
|---|---|
| Combat | 2 (Luggage Hall, Counter Row) |
| Puzzle | 2 (Claim Check, Wrong Door) |
| Trap | 1 (**Baggage Belt**: conveyor floors push toward a shredder every 4 s; a lever stops each belt, -5 per fall) |
| Mini-boss | 1 (a Mimic-style chest elite, 2x health, swaps places with a decoy) |
| Buff rooms / secrets | 2 / 4 (the most hidden floor: "lost" is the point) |
| Red Tape gate | kill 3 clerks hiding as items (they stand still until hit) |

**Puzzle F5-A "Claim Check"** (logic grid). Four lost items (Umbrella, Key, Lantern, Book) lie on a heap; four counters numbered 1-4. A clerk NPC gives the clues; the party places each item on a counter plate. Clues: the Umbrella's counter number is higher than the Key's; the Lantern and the Book are on neighbouring counters; the Key is not at counter 1; the Lantern is at an even counter; the Book is not at counter 4. Exactly **one** solution (python check: Umbrella 4, Key 3, Lantern 2, Book 1). The clue set is a seeded template (shuffle names and numbers, unique solution rechecked at build). A wrong placement: -2, the item returns to the heap.
**Puzzle F5-B "Wrong Door"** (rule-following). A chain of 4 rooms, each with 3 numbered doors (1, 2, 3) and a row of lanterns, 0-3 lit. The correct door is the **number of lit lanterns** (a room with 0 lit lanterns: door 3, "nothing is the most paperwork"). A wrong door sends the party back to room 1 of the chain with a new lantern pattern and costs -2. The lanterns hide the hint in the Department voice on a sign ("Door equals lights").

**Mobs (UNVERIFIED):** `Goblin_Thief` and `Goblin_Scrapper` (thieves of lost things), `Crawler_Void`, `Spawn_Void` (Elites-Events says Void creatures: crawlers, void spawn, flying eyes), `Eye_Void` (floating, shoots a slow beam), a golem for the mini-boss (`Golem_Crystal`?). Spawn the dimensional-door ambushes from the door blocks.

### 3.1 Boss - The Unclaimed (Lv 91; a shapeshifter; base a Void Spawn or `Golem_Void` model, UNVERIFIED)

| Phase | Health | Moves (telegraph) | Adds | Safe play |
|---|---|---|---|---|
| 1 "Lost Property" | 100-65% | every 20 s he **copies one player's class ability** (an outline in that class colour, 3 s, then casts a boss version at 1.2 H, three casts) | none | the copied player stays out of the middle, so the copy hits air |
| 2 "Claim Tickets" | 65-30% | splits into **3 forms** with a ticket number each (1-3); only the form whose ticket matches the next called number takes damage (the call shows on the arena board, 2 s); the rest reflect 50% | 2 `Eye_Void` a minute | hit the called form |
| 3 "Reclaimed" | 30-0% | casts the copied abilities of **fallen** players too (a ghost's class works for him), a short stun 1 s every 25 s | 4 `Crawler_Void` a wave | stay alive, kill adds first |
| Enrage | 480 s | damage +10% every 10 s | | |

Solo: the copy is always the soloist's own class; the ghost copy in phase 3 uses the class of the last revived player. UNVERIFIED: whether a mod can call another class's ability on a mob (see section 12).

## 4. F6 - The Void Counter (Customer Waiting)

A cosmic waiting room: endless rows of chairs, a ticket dispenser, a glowing "NOW SERVING" board, ghost queues. The longest floor to read.

| Rooms | Count |
|---|---|
| Combat | 3 (Queue Hall, Complaint Counter, Chair Maze) |
| Puzzle | 2 (Take a Number, Form Relay) |
| Trap | 1 (**Closing Time**: shutters slam across the room every 6 s, pattern shown on the floor, -5 per hit) |
| Mini-boss | 1 (a Grand Queue Ghost: summons 3 queue ghosts that walk to a pillar; 2x health) |
| Buff rooms / secrets | 2 / 3 |
| Red Tape gate | kill 3 marked "Priority Customers" who skip the queue |

**Puzzle F6-A "Take a Number"** (memory + movement). Each player takes a ticket from the dispenser (1 to the number of players; **solo draws 3 tickets**). The board calls a number (3 s, a chime) and a matching **numbered desk** lights for **6 s**; the holder (or anyone for solo) must stand on it before the light ends. **5 calls**, one new number each time; a missed call: -2 and the call repeats. No kill needed.
**Puzzle F6-B "Form Relay"** (linked levers). Three desks A, B, C each show a stamp colour (Red, Blue, Green) from a 3-state lever. Pulling lever A cycles desk A **and** desk B; lever B cycles B and C; lever C cycles C and A (order Red -> Blue -> Green -> Red). Start state: all Green. Goal on the form: **A Red, B Blue, C Green**. Python check: solvable in a minimum of **3 pulls** (27 states reachable); a pull count over **9** = ink spill, -2 (so brute force is allowed but penalised).

**Mobs (UNVERIFIED):** `Zombie_Aberrant`, `Zombie_Burnt`, `Zombie_Frost`, `Zombie_Sand` (the waiting queue shambles; four variants for four counters), `Wraith` (the "ghost customers": if a role exists), `Skeleton_Mage` (clerks that cast), `Eye_Void`. The mini-boss uses a `Zombie_*` elite.

### 4.1 Boss - Ticket #1 (Lv 94; the first soul in the Void; humanoid, base a `Wraith` or `Skeleton_Praetorian`, UNVERIFIED)

| Phase | Health | Moves (telegraph) | Adds | Safe play |
|---|---|---|---|---|
| 1 "Now Serving" | 100-65% | 4 numbered circles on the floor; he calls numbers 1-4 in order, each circle bursts after 3 s (radius 4); on every 4th call the circle chain **ends on the party**; a 5 block ground slam (2 s) | a queue of **6 ghosts** walks to him (8 s apart); each that arrives gives him a "Served" stack (+10% damage, 6 stacks cap) | kill ghosts, stay off the called circle |
| 2 "Take a Number" | 65-30% | each player gets a number (solo: 3); he fires a beam at a number, 2 s, from **behind a pillar** safe spot; the numbered player holds the line, others free-hit | 2 `Wraith` at a time | pillar is the safe spot |
| 3 "Closing Time" | 30-0% | the arena **shrinks** row by row from the back (a row vanishes every 20 s), shutters slam in lines (6 s pattern), chain bursts every 3 calls | 6 ghosts + 1 elite | stay forward, kill fast |
| Enrage | 480 s | damage +10% every 10 s | | |

## 5. F7 - The Auditor's Chair (Internal Audit)

The central desk: a hall of columns showing every earlier floor's doors, a huge desk, a red pen. The only floor with **no new theme**: it is a review of the others ("Reviewing... reviewing... you have been reviewed.").

| Rooms | Count |
|---|---|
| Combat | 3 (a mixed wave from each of F4-F6 in turn) |
| Puzzle | 2 (Balance the Books, Cross-Reference) |
| Trap | 1 (**Red Ink Flood**: ink rises 1 block every 8 s from the floor; the exit lever is on the far side, -5 per ink touch) |
| Mini-boss | 1 (an Audit Assistant: copies the last boss mechanic, 2x health) |
| Buff rooms / secrets | 2 / 4 (all four give the "All Secrets" bonus) |
| Red Tape gate | kill 3 marked "Auditors in Training" |

**Puzzle F7-A "Balance the Books"** (partition). Five weights (a seeded set whose total is even and has a split; sample 2, 3, 4, 6, 9) are placed on two trays; the scale must show equal totals within **0** difference. Sample solves (3, 9) against (2, 4, 6) (python check). A wrong lock: -2, the weights reset. A mixed puzzle: weights are carried one at a time (the carrier moves slower, 30%).
**Puzzle F7-B "Cross-Reference"** (recall). Six pillars each show the icon of a floor boss F1-F6 with its level (79, 82, 85, 88, 91, 94) etched small. The party must strike them **ascending by level** within **40 s** from the first strike; a wrong pillar resets the sequence (-2). Players are never required to have met the bosses (the numbers carry the answer).

**Mobs (UNVERIFIED):** reuse the F4-F6 rosters (`Rex_Cave`, `Pterodactyl`, `Crawler_Void`, `Eye_Void`, `Zombie_*`, `Wraith`) at level 94, plus one new `Golem_Void` or `Shadow_Knight` (if a role exists) as the "audit clerk" mace-bearer.

### 5.1 Boss - The Auditor (Lv 97; the Void with a pen; a large Void entity, base UNVERIFIED)

| Phase | Health | Moves (telegraph) | Adds | Safe play |
|---|---|---|---|---|
| 1 "Records" | 100-65% | **stamp slam** (F1; a giant circle, 3 s), **shelf collapse** (F2; two rows of shelves fall in lines, 2.5 s), the **flame line** from F4 (3 s) | clerk queue: 4 `Zombie_*` every 40 s | step out of the circle, stand between shelf rows |
| 2 "Rent and Copies" | 65-30% | a **shield** (F3 rent): kill 5 "token" adds to drop it (30 s limit or the pen strikes the party), **copies** one player's ability (F5, 3 s outline) | 5 tokens a cycle | token kills first |
| 3 "The Final Stamp" | 30-0% | all of it: numbered circles (F6), shrinking arena (one row per 25 s), a **Red Pen** line across the arena (2 s, 1 block wide) every 15 s, **Take a Number** beams every 45 s | 2 `Eye_Void` | the whole run's skills |
| Enrage | 540 s (a F7 override; see Q1) | damage +10% every 10 s | | |

## 6. Health and time-to-kill (python-checked)

Method (placeholders: the real numbers are for the local session): player hit `H = 6 x F(gear level) x (1 + 0.003 x tier band start)` (6 = the Lv 1 martial base from `research/Gear-Levels-Wynn-Spec.md`, F(L) the straight-line curve 1:1.0 4:1.6 10:2.0 40:3.0 100:5.0, material bonus 0.3% per start level); weapon DPS = 1 H a second (`research/cloud/Class-Ability-Spec-Draft.md` section 1.1) x 1.5 (abilities add half) x a **gear-mod factor** (set bonus + rolled Legendary lines: F4 2.2, F5 2.4, F6 2.6, F7 2.8) x 0.7 uptime (dodging). Players arrive in the **previous floor's** gear (item level = floor level - 3). Boss health = `200 base x 4.0 (level cap x4, reached at Lv 76) x hpMult` (200 is between the 124 Grizzly and the 400 Rex_Cave in `research/cloud/Mob-Levels-Refit.md`), then x `(1 + 0.4 x (players - 1))`.

| Floor | Gear Lv worn | H | DPS (1 player) | hpMult | Boss HP, 1 player | TTK p=1 | p=2 | p=3 | p=4 (HP 2.2x) |
|---|---|---|---|---|---|---|---|---|---|
| F4 | 82 | 32.4 | 74.9 | **28** | 22,400 | **299 s** | 209 s | 179 s | **165 s** |
| F5 | 85 | 34.0 | 85.6 | **34** | 27,200 | **318 s** | 222 s | 191 s | **175 s** |
| F6 | 88 | 34.7 | 94.8 | **40** | 32,000 | **338 s** | 236 s | 203 s | **186 s** |
| F7 | 91 | 35.5 | 104.3 | **47** | 37,600 | **361 s** | 252 s | 216 s | **198 s** |

Totals with phase downtime (untargetable flights, shield windows; placeholder 50 / 60 / 70 / 90 s): solo 349 / 378 / 408 / **451 s** against the 480 s enrage (margin 131 / 102 / 72 / **29 s**). A party of four: 215 / 235 / 256 / 288 s, so a four-player run is about 40-60% of the solo time but the **mechanics do the fighting**, not the health: party health grows 2.2x for 4x the damage, so four players are strictly faster (by design; `research/cloud/Capstone-Dungeon-Spec.md` section 6). The 29 s solo margin on F7 is too tight; that is why F7 proposes 540 s (margin 89 s) - see question 1. A Priest or Mage solo has less sustained DPS than the 1.0 H a second martial budget, so F4-F7 are "party recommended" in the gate text. Adds use `base x level mult` (800 HP at the cap), elites 2x.

## 7. Score targets (speed from the 100-at-target, 0-at-double rule)

Speed points = `100 x (2T - minutes) / T`, capped 0-100 (python-checked). Skill, Explore and Bonus follow `research/cloud/Capstone-Dungeon-Spec.md` section 5.1 with the extra bonus lines: F4 "no egg lost", F5 "found every lost item", F6 "no missed call", F7 "audit passed" (no wipe).

| Floor | Speed at T | at T+4 | at T+8 | Par run (1 death, 75 explore, T+6 min) | S needs |
|---|---|---|---|---|---|
| F4 (T = 22) | 100 | 82 | 64 | 238 (A) | all secrets, T+4 or better |
| F5 (T = 24) | 100 | 83 | 67 | 240 (A) | all 4 secrets (hard) + a bonus |
| F6 (T = 26) | 100 | 85 | 69 | 242 (A) | no missed call + T+4 |
| F7 (T = 28) | 100 | 86 | 71 | 244 (A) | everything: S on F7 = the "Auditor" title |

Par = skill 90 + explore 75 + speed at T+6 (73 / 75 / 77 / 79) = 238 / 240 / 242 / 244 (python-checked). S needs skill 100 + explore 100 + speed 70 or more (= 270), so every secret is required: S is a full-clear rank, T+8 is still enough. A flawless run at T+2 reaches about 291-293 with no bonus. The ranks stay S 270 / A 230 / B 160 / C 100.

## 8. Rewards and set pieces

| Floor | Gear rolls (item Lv) | Set piece (8% a roll) | Extra |
|---|---|---|---|
| F4 | Voidglass 85 | **any** Voidglass piece, the slot the player owns least of ("makeup exam") | dragon-themed title "Egg Registrar" |
| F5 | Aetherium 88 | **piece 1** of the Aetherium set | Epic pet egg chance (spec: epic at F5+), title "Lost and Found" |
| F6 | Aetherium 91 | **piece 2** | title "Number One"; Audit Tokens x floor |
| F7 | Aetherium 94 | **piece 3 + any missing piece** | title "Auditor" at S |

Per-chest odds for a set piece (python-checked, 8% a roll): 1 roll 8.0%, 2 15.4%, 3 22.1%, 4 28.4%; with the 12-chest pity, the expected chests per piece are about 7.9 (D), 5.6 (B), 4.3 (A), 3.5 (S) - so a full 3-piece Aetherium set takes about **13 A-rank chests**, a little more than the daily cap of 12; no set is gated by anything else. Audit Tokens = rank points (D 1, C 2, B 4, A 6, S 9) x floor number; first clear x2. No coins anywhere.

## 9. Master Mode (note only; side content, never on the spine)

Spec section 3: each floor +10 levels, x2 health, tougher mechanics. The mob/boss level cap and gear cap is **100**, so F4-F7 Master would be 98 / 101 / 104 / 107: clamp at 100 or raise the cap (question 3). Proposal: a Master floor adds **one mechanic per phase** (F4 flame lines come in pairs; F5 two copies; F6 queue 8 ghosts; F7 the Red Pen every 10 s), an enrage of 420, and drops with the Set bonus **tier 4** (a rune upgrade) only if Skyy wants; the chest otherwise uses the same tables. Nothing is built until the base floors are tested.

## 10. Build order (phase 3 of the spec)

| Step | What | Needs |
|---|---|---|
| 1 | puzzle kit: the 8 new puzzle modules (plates, levers, counters, timers) as small scripted rooms, tested on F1-F3 first | the phase 2 puzzle library |
| 2 | **F4** (Dragon's Nest): fewest new systems; completes the "makeup exam" Voidglass drop | flight / untargetable phase (UNVERIFIED), dragon rig |
| 3 | **F5**: Aetherium starts; the hardest boss (copy ability) | a `class:fn:cast` style bridge call (UNVERIFIED) |
| 4 | **F6**: shrinking arena + numbered circles | arena floor edit script |
| 5 | **F7** and the title / token shop wiring | every above |
| 6 | Master Mode after the base floors are tested | question 3 |
Each floor ships alone (item ids stay stable) and uses the same room and score engine; a **lean round** per floor, **full round** for F5 (item drop rule + ability calls) and for F7 (final loot).

## 11. Server Setup rows

`dungeon.floor.4.enabled` ... `dungeon.floor.7.enabled`, `dungeon.floor.<n>.level` (85 / 88 / 91 / 94), `dungeon.floor.<n>.bossLevel`, `dungeon.floor.<n>.hpMult` (28 / 34 / 40 / 47), `dungeon.floor.<n>.baseHp` (200), `dungeon.floor.<n>.enrageSeconds` (480; F7 540), `dungeon.floor.<n>.speedTargetMinutes` (22 / 24 / 26 / 28), `dungeon.floor.<n>.classSkillMin` (85 / 90 / 95 / 100), `dungeon.puzzle.warmNest.pressLimit` (12), `.eggRun.seconds` (45), `.wrongDoor.penalty` (2), `.takeANumber.callSeconds` (6), `.formRelay.pullLimit` (9), `.crossRef.seconds` (40), `dungeon.boss.mate.adds` (4), `dungeon.boss.unclaimed.copySeconds` (20), `dungeon.boss.ticket1.rowSeconds` (20), `dungeon.boss.auditor.penSeconds` (15), `dungeon.tokens.rankPoints` (1,2,4,6,9), `dungeon.master.enabled` (off).

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Every role id marked UNVERIFIED: `Raptor_Cave`, `Rex_Cave`, `Pterodactyl`, `Trillodon` (seen in Dragon-Pets-Idea), `Scarak_Fighter`, `Emberwulf`, `Goblin_Thief`, `Goblin_Scrapper`, `Crawler_Void`, `Spawn_Void`, `Eye_Void`, `Golem_Void`, `Golem_Crystal`, `Zombie_Aberrant/Burnt/Frost/Sand`, `Wraith`, `Skeleton_Mage`, `Shadow_Knight`. Read `Server/NPC/Roles/*` and pick the nearest. |
| 2 | Boss bases: `Dragon_Fire` / `Dragon_Frost` (flight, moves), any Void entity model for F5 / F7, Wraith for F6. Which attacks exist and whether the attack set can be replaced by script. |
| 3 | Untargetable / airborne phase for the Mate; ground telegraph shapes (lines, rings, cones) as vanilla effects or particles. |
| 4 | Calling another class's ability on a mob (F5 copy): through SkyyClasses via the `skyy.bridge` map with plain java.lang types. |
| 5 | Shrinking arena: removing floor blocks in a copied template at runtime (F6, F7). |
| 6 | Pressure plates / levers / counters / numbered desks (plate-step events) for the eight puzzles. |
| 7 | The real hit `H`, boss base health, and whether Priest / Mage solo DPS reaches the martial 1.0 H a second budget; re-run section 6 with SkyyGear numbers. |
| 8 | Whether the mob and boss level cap is really 100 (the `scale.role` hook range) for Master Mode. |
| 9 | Whether `gear:fn:roll` can force "slot = piece N of the set" for the floor-by-floor Aetherium rule. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | F7 solo enrage 540 s instead of 480 s (margin 89 s)? Or keep 480 and make F7 "party only"? | 540 on F7 only |
| 2 | Are the department names (Unhatched Claims, Lost Property, Customer Waiting, Internal Audit) and the voice samples right? | yes |
| 3 | Master Mode: clamp mobs at level 100, or raise the cap past 100 for the Master floors? | clamp at 100 |
| 4 | Is about 13 A-rank chests for a full Aetherium set fast enough, or should the pity be 20 (slower)? | pity 12 |
| 5 | The F5 boss copies abilities, including from fallen players: fun, or too nasty for solo? | keep, solo copies only the soloist |
| 6 | F6 and F7 puzzle penalty -2 per failed step as in the spec, or none on F7? | -2 (the spec rule) |
| 7 | Should floor access be gated by "cleared the floor below" (F5 needs F4)? | no, independent (spec) |
