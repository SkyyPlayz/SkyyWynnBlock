# Capstone dungeon spec - "The Final Audit"

Cloud draft, 2026-10-06. The **one endgame capstone dungeon** after the last island (LOCKED: `docs/plans/SkyWynn-Decisions.md` row 7.5 "floor-style endgame dungeon (Catacombs-like): TAKE as the one capstone"; `docs/plans/SkyyDungeons-Plan.md`: "after the last island there is one endgame capstone dungeon; it is the only dungeon that closes the spine"; extra dungeons, raids and corrupted hard modes stay side content).
Web research (SkyBlock Catacombs, Wynncraft raids) is from search snippets (the wiki pages cannot be fetched here); everything about the engine is UNVERIFIED. Companions: `Zone-Bosses-Ideas.md`, `Story-Script-Zones-2-5.md`, `Slayers-Spec.md`, `Elites-Events-Spec.md`, `Class-Ability-Spec-Draft.md`, `Tab-Economy.md`.

## 0. What the research says

| Source | Facts |
|---|---|
| **SkyBlock Catacombs** (search snippets: [The Catacombs - Floor III](https://hypixel-skyblock.fandom.com/wiki/The_Catacombs_-_Floor_III), [Master Mode](https://hypixelskyblock.minecraft.wiki/w/Master_Mode), [first dungeon patch](https://hypixel.net/threads/2851991)) | a **series of floors** of interconnected **rooms**: combat, **puzzles**, **traps**, **secrets**; parties of **2-5** by default; floors 1-3 beginner, 4-6 intermediate, 7+ hard; **bosses have phases, abilities and minions**; **Secrets** give loot and **dungeon score**; **score uses four categories: Skill / Explore / Speed / Bonus**; class roles (Healer, Mage, Berserk, Archer, Tank); a **Master Mode** harder version of each floor |
| **Wynncraft raids** (snippets: [Raids](https://wynncraft.wiki.gg/wiki/Raids), [Nest of the Grootslangs](https://wynncraft.wiki.gg/wiki/Nest_of_the_Grootslangs), [Canyon Colossus](https://wynncraft.wiki.gg/wiki/The_Canyon_Colossus)) | team challenge of **3-6 players** (3-4 for the first raid, 4 for the third, a combined level cap on the first two); **3 randomly chosen challenge rooms then a strong boss**; **a buff room after each challenge**; rewards: emeralds, accessories, materials, keys, XP |
Lessons: use the **floor + room + score** structure of Catacombs and the **random-challenge + buff-room + boss** rhythm of Wynn raids; keep **party roles** meaningful (our classes: Warrior tank, Priest healer, Mage burst, Archer control, Berserker buffer, Monk disruptor, Assassin priority killer).

## 1. The dungeon in one paragraph

**The Final Audit** is the Void's own headquarters: a floating filing complex that the **Dragon's hiccups** have been tearing from. After the dragon (Zone 5 story), the Department sends you to the **Auditor's Gate**; each **floor** is a short audit of one department (Records, Archives, the Tab Office ...) ending in a boss. It is the **one dungeon that closes the story spine**: the last stamp on Form 27-B/6.
**Not a leveling world**: gear and class skill 70+ are required (our own Lv 50-100 tiers drop here); it never unlocks anything on the island chain.

## 2. Access and party

| Rule | Value |
|---|---|
| Entrance | the **Auditor's Gate** in the Zone 5 town (the Egg Desk), unlocked by the Zone 5 guardian (the dragon) + the quest "The Last Stamp"; **per profile** flag `capstone.open` |
| Level requirement | class skill **70** (floor 1), +5 per floor; a **minimum gear level** hint (Lv 65); no hard gate on gear |
| Party | **1-4 players** (solo allowed); join through a **party gate** (everyone confirms), a **ready check**, a countdown |
| Cap | a **combined level cap** is not used (it creates exclusion); instead the dungeon **scales** to party size and the highest level |
| Class mix | any; a **role hint** shows the roles present ("no healer") |
| Instances | **one instance world per run** (a copy of the floor template), deleted when empty or on the 60 min timer; max 1 active run per player |
| Cooldown | none (the run costs time, not a cooldown); **drop rewards limited per day** (section 9) |
| Keys | **no key items**: access is the flag; a run is **free** (the money sink is repair / reforge and the Tab), an optional cosmetic **ticket** can show a rank |

## 3. Floors (launch with 3, build up to 7)

Levels: floor 1 = Lv **76**, +3 per floor (floor 7 = Lv 94); health scales with level and party size. Each floor takes **20-30 minutes** for a competent party; floors are **independent runs** like Catacombs.

| Floor | Name | Theme / department | Boss | Boss level | Key mechanic | New |
|---|---|---|---|---|---|---|
| **F1** | The Records Hall | rows of shelves, desks, stamp pads | **The Void Clerk** (a giant Kweebec clerk with a stamp) | 79 | **stamp slam**: a telegraphed stamp area + minion queue | launch |
| **F2** | The Archives | frozen file stacks, a flooded basement | **The Archive Golem** (a crystal / ice golem) | 82 | **shelf collapse** + puzzle-gated shield phase | launch |
| **F3** | The Tab Office | gold counters, a vault of coins | **The Landlord** (the Void's rent collector; "your shard owes ...") | 85 | **rent phases**: pay "tokens" (kill adds) to lower his shield | launch |
| F4 | The Dragon's Nest | a cavern of eggs | **The Dragon's Mate** (the lonely dragon quest, Dragon-Quest-Spec section 6) | 88 | flight phase, breath lines | later |
| F5 | The Lost & Found | endless lost items, dimensional doors | **The Unclaimed** (a shapeshifter that copies your class abilities) | 91 | copies abilities | later |
| F6 | The Void Counter | a cosmic waiting room | **Ticket #1** (the first soul in the Void) | 94 | queue mechanic | later |
| **F7** (final) | The Auditor's Chair | the central desk | **The Auditor** (the Void itself with a pen) | 97 | all mechanics | the true final boss |
**Master Mode** (each floor +10 levels, x2 health, tougher mechanics, better score thresholds) is **side content later** (as in Catacombs) and **never** needed for the spine.

## 4. Room types (how a floor is built)

A floor = **a start room + 5-8 chambers + a boss gate + the boss arena**, connected by doors. Types (inspired by Catacombs / Wynn raids):

| Room type | What happens | Count per floor |
|---|---|---|
| **Combat** | waves of themed mobs; doors lock until cleared; one elite sometimes | 2-3 |
| **Puzzle** | a logic task with a reward: **Stamp Order** (step on plates in ticket-number order), **Queue Maze** (follow the ghost line), **Ledger Balance** (put 4 items on the right shelves), **Paper Shredder** (timed hazard crossing), **Index Cards** (match symbols) | 1-2 |
| **Trap** | collapsing floor, filing-cabinet crushers, ink floods; a dexterity room, no combat | 1 |
| **Secret** | a hidden room (a lever, a breakable wall, a hidden key) with a chest: **coins are not given**, instead: gear rolls, Void Fragments, pet eggs, titles | 2-4 (hidden) |
| **Buff room** (Wynn style) | after each puzzle / combat milestone: pick **1 of 3 temporary buffs** for the rest of the run (damage +10%, heal +, speed +, cooldown -, a shield) | 2 |
| **Mini-boss room** | an elite-plus (2x health) with one mechanic | 1 |
| **Boss gate** | the **Red Tape**: kill the 3 marked clerks (the "blood room" analog) to get the **Stamped Key** that opens the boss door | 1 |
| **Boss arena** | the boss, phases, adds, safe corners | 1 |
Rooms come from a **prefab library** assembled by a **seeded layout generator** (a 5 x 5 grid of 24 x 24 cells; room sizes 1 x 1, 1 x 2, 2 x 2): the start is on one edge, the boss on the opposite edge, the path goes through the chambers (a minimum path of 6 rooms). Randomness: the generator picks 3 random challenge rooms from the pool (Wynn's rule) and places the secrets.

## 5. Scoring and rewards

### 5.1 Score (300 points, a clone of the four Catacombs categories)
| Category | Max | How |
|---|---|---|
| **Skill** | 100 | starts at 100; **-10 per death**, -2 per failed puzzle step, -5 per trap hit; partial for unfinished rooms |
| **Explore** | 100 | rooms cleared (% of rooms) x 60 + secrets found (up to 40) |
| **Speed** | 100 | by clear time vs the floor target (20 min = 100, 40 min = 0) |
| **Bonus** | up to 30 | +5 each for: no death, all secrets, a buff room used, no healer needed ... (a few "style" bonuses) |
| Rank | | **S** >= 270, **A** 230-269, **B** 160-229, **C** 100-159, **D** < 100 |
The rank gives the **chest tier** and the "run complete" screen (a vanilla-look summary page).

### 5.2 Rewards
| Reward | Rule |
|---|---|
| **Floor chest** (per player) | opened at the end; contents by **rank**: D 1 roll, C 1 + chance, B 2, A 3, S 4 rolls from the floor's loot table |
| **Gear** | the capstone is where **our own Lv 50-100 tiers** drop, **unidentified** (the loot box design): levels 76 + 3 per floor; **rarity weights shifted +30%** vs normal; the **Set** rarity (green) drops **only here** (the dungeon's set pieces, 3-piece set bonuses: SkyyGear `set` rarity exists) |
| **Audit Tokens** | a guaranteed currency (rank x floor), used for **cosmetics, pet upgrades (dragon stones), titles**, never gear power; tokens are bound |
| **Void Fragments** | 1-6 per run (the crafting currency of Pocket Shards / Pets) |
| **Pet eggs** | a small chance (epic at F5+) |
| **Titles** | "Auditor" (F7 S rank), per-floor titles, "Clean Books" (a run with no deaths) |
| **XP** | combat XP from mobs; a **completion XP** lump (class XP) by floor; **Smithing / secrets XP** none |
| **Coins** | **no coins** (consistent with slayers / mob rules; coins come from selling) |
| Daily limit | **12 floor chests per real day per profile** (anti-grind; extra runs still pay score, no chest) |
| Repeat clears | the first clear of each floor pays a **first-clear bonus** (a title + tokens x 2) |

## 6. Combat and classes

| Rule | Value |
|---|---|
| Death | you become a **ghost** (spectator) and can be **revived** at a **soul altar** by a teammate or at the next room start after **30 s**; each run gives **3 revives total** (solo: 1) so a wipe ends the run (return to the gate; no item loss); a death costs **10 score** |
| Healing / buffs | the Priest's heals and Berserker's party buffs matter: the dungeon has **enemy density** that rewards support |
| Mana / Stamina | restore in **rest alcoves** (a small altar that refills 50% once per room) so Mana-limited classes do not stall |
| Abilities | all class abilities work; **no flying**; traversals (blink, vault, glide) can skip **only** the traps (locked doors stay) |
| Mobs | themed: clerks, golems, shades, void spawn, paper swarms; levels per floor (76+); **elites** appear in the mini-boss rooms only |
| Boss design | 3 phases, one mechanic taught per phase, one **enrage timer** at 8 minutes (a damage ramp), minion waves as the Wynn / Catacombs rhythm |
| Scaling | `health = base x (1 + 0.4 x (players - 1))`, damage +10% per extra player |

## 7. Engine plan (per floor)

| Piece | Approach |
|---|---|
| Instance | `InstancesPlugin.spawnInstance(template, "run-<uuid>")` like SkyyIslands / Slayers; a **template world per floor** (hand-built **once**, copied per run) in v1; the procedural layout generator comes in v2 |
| Rooms | prefab pieces pasted by `PrefabUtil.paste` onto the grid; doors are blocks opened by script; plates / levers use our interaction hooks (UNVERIFIED) |
| Mobs | spawn markers or script spawns on room entry (the SkyyMobs `mob:fn:setLevel` / `scale.role`); all mobs have a **run id** so they despawn with the instance |
| Score | a per-run object held by the SkyyDungeons mod (deaths, secrets, rooms, time); events from the SkyyQuests `quest:fn:event`-style reports and the kill events |
| Party | `party:fn:members` (SkyyParty) lists the group; teleport in together |
| Loot | the floor chest uses `gear:fn:roll` (unidentified boxes) |
| Safety | the run ends with the instance; items taken **stay**; a crash returns players to the gate (the SkyyIslands recovery pattern) |
| Mod | **SkyyDungeons** (the plan's own mod); it also hosts the slayer arenas and the world events (same instance code) |

## 8. Build phases
| Phase | Content |
|---|---|
| 1 | **F1 only**, hand-built, linear (8 rooms), the boss, score, chest, party gate, revive |
| 2 | F2 and F3, the buff rooms, puzzle library, the secret system |
| 3 | the **procedural layout generator** (random challenge rooms), F4-F7, Master Mode |
| 4 | the set bonuses, tokens shop, titles, daily limits |
Needs before phase 1: SkyyQuests (the access quest), our own Lv 50-100 gear tiers (SkyyArmory roadmap), the loot box item system, SkyyMobs bosses.

## 9. Server Setup rows (sketch)
`dungeon.enabled`, `dungeon.floors` (enabled list), `dungeon.partyMax` (4), `dungeon.timerSeconds` (3600), `dungeon.revives` (3), `dungeon.reviveSeconds` (30), `dungeon.scoreRanks` (270,230,160,100), `dungeon.chestDailyLimit` (12), `dungeon.lootBonusPercent` (30), `dungeon.setDropOnly` (on), `dungeon.enrageSeconds` (480), floor tables (level, boss, health multiplier).

## 10. Anti-exploit
| Risk | Handling |
|---|---|
| Carry runs (a high-level friend) | chest rolls are **per player by rank**; the **boss level vs the player's level** gap rule halves XP and token rewards when the player is 15+ levels below the floor (a "carried" flag) |
| Chest farming | the **daily limit 12** per profile |
| Skipping rooms with traversals | doors lock until cleared; only trap rooms skip |
| Duplicating gear | rolls are created in the chest on **open**, not before; no dupes through crashes (the opened state is saved first) |
| Instance exits | leaving = the run counts as failed; loot already taken stays |
| AFK in the dungeon | a 5 minute no-damage idle timer kicks the party to the gate |

## 11. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Procedural prefab assembly speed and block count of a floor instance (24 x 24 cells x 25 = 600 x 600?). Start with hand-built templates. |
| 2 | Spectator / ghost mode and revival altars: is there a vanilla "spectator" game mode usable per player? |
| 3 | Hytale pressure plates / levers / secret door blocks and the interaction hooks for puzzles. |
| 4 | Spawn markers vs script spawning inside copied templates (WorldGen plan stage 0 test 2). |
| 5 | How `SkyyParty` identifies the group for a teleport. |
| 6 | Boss room mechanics like safe zones and area telegraphs: any vanilla "telegraph" effects. |
| 7 | The final boss and the Tab story hook (the Landlord on F3) must match the Tab economy and lore. |

## 12. Questions for Skyy
1. **3 floors at launch** (the rest later) and each floor runnable on its own (Catacombs style)? (Recommended: yes.)
2. **Solo allowed** (scaled), or require a party of 2+? (Recommended: solo allowed.)
3. Is **"The Final Audit"** the right lore name for the capstone (the Void's own office), with the Landlord as the F3 boss?
