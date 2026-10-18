# Beta bugs triage - 2026-10-17 video (19 bugs)

Triage of `docs/tests/2026-10-17-beta-bugs.md` (Skyy's 62 min beta video, 2026-10-17 ~10:51). Written 2026-10-18 by a read-only
triage agent: code reading of the PINNED build scripts (`tools/deploy_set.py` SET on 2026-10-18 08:00) + the game logs still on disk.
Where this goes next: the main session launches the fix rounds in section 3 (one mod per builder); each fix ticks its box in the bug
list and gets a `docs/log/2026-10.md` line. Questions for Skyy go to `OPEN-QUESTIONS.md`.

Limits of this triage:
- The server / client logs of the 10:51 session were already recycled; only the 10-17 21:23 / 22:15 and 10-18 07:38 logs are left
  (`python tools/log_scan.py --ours`: only 4 known WARN kinds, nothing about these bugs). Nothing was run in game.
- What deployed AFTER the video (10:51): ores round 16:08 (TEST 177), Gear 0.3.19 + Mobs 0.1.10 18:31, Gear 0.3.20 19:24, Armory
  0.1.31 22:04, Gear 0.3.21 + Quests 0.4.1 22:20, Trees 0.3.23 + Skills 0.4.50 + Sacks 0.8.21 22:43, Hud 0.3.32 22:50, renumber set
  23:48, metals 00:58, Movement 2 (Core 1.0.1 / Gear 0.3.24 / Skills 0.4.51 / Accessories 0.5.26) 01:44, Armory 0.1.34 01:53,
  Collections 0.2.27 + Menu 0.3.39 02:14, Gear 0.3.25 02:49, Gear 0.3.26 07:35. Gear 0.3.27 is pinned, not deployed (game open).
  Running now: Skills 0.4.52 (mana round) - a Skills fix goes on 0.4.53 after it.
- Pack mods ON in NewBetaTest (world config.json): Dragon Nestkeeper, Perfect Parries, BetterMap, ZipLine, WeaponCustomHUD,
  NoCube Orchard, The Armory, ZoneViewControl, Dynamic Seasons, More Crossbow Tiers, Multitools.

Short names: I: = `SkyyIslands/build_skyyislands_0.5.19.py`, C: = `SkyyClasses/build_skyyclasses_0.1.38.py`,
A: = `SkyyArmory/build_skyyarmory_0.1.34.py`, G: = `SkyyGear/build_skyygear_0.3.27.py`, S: = `SkyySkills/build_skyyskills_0.4.51.py`,
H: = `SkyyHud/build_skyyhud_0.3.32.py`, T: = `SkyyTrees/build_skyytrees_0.3.23.py`, K: = `SkyySacks/build_skyysacks_0.8.22.py`,
Co: = `SkyyCollections/build_skyycollections_0.2.27.py`, Q: = `SkyyQuests/build_skyyquests_0.4.1.py`, M: = `SkyyMobs/build_skyymobs_0.1.10.py`.

## 1. Per bug

### 1. Invincible after dying on the island - OPEN, ours (SkyyIslands), cause likely, not proven
- No pinned mod ever adds Invulnerable / Intangible / spawn protection to a player (grep of all pinned scripts: only Classes READS
  Invulnerable, C:10992, C:18320). So it is not a component left on.
- Path: I:10159-10173 IsleRespawn (OnRespawnSystem, DeathComponent removed) -> IsleLife.respawnLater (I:9857-9863, 1.8 s delay since
  0.5.16, I:2206 / I:2280) -> mode 5 / mode 4 (I:10075-10095) -> IsleLife.respawn (I:9824-9848) -> route() I:9805-9815 (died on own
  island = 3) -> goHome I:8963-9010 adds a same-world Teleport component (I:9004) 1.8 s after the engine already respawned the player,
  unless within 2 blocks (I:8986-8996).
- Likely mechanism: the late Teleport resets the client's position / prediction while mobs are already hitting the freshly respawned
  player; damage / stat updates are then mis-predicted or queued and land together (the 2026-10-15 log already notes unexplained
  EntityStatUpdate mis-predictions). Mobs may also keep the old Ref target until the teleport.
- Fix (Islands, lean): when the death was on the player's OWN island (route 3) do no second trip - set the respawn point BEFORE the
  engine respawns (bed / island spawn as the world's respawn for that player) instead of teleporting after; keep the trip only for the
  cross-world case; add a debug line "respawn: route N, teleported yes/no, ms". A/B row: islands.respawnHome=false.
- Test: die to a mob on the island, stand still after respawn, watch health: you must take each hit as it lands; repeat 3 times;
  then with the Server Setup row off.

### 2. Respawn at the ruins, not the island + bed spawn glitch - OPEN, ours (SkyyIslands)
- Causes found (in likelihood order):
  1. goHome's "spawn not ready" (-2) retries only ONCE after 1 s (I:9850-9856), then gives up silently -> the engine default = world
     spawn / ruins. Fits a lagging server (bug 4).
  2. route() returns 0 (engine decides) whenever a bed exists in the DEATH world (I:9810) - a stale bed in a zone / hub world blocks
     the island trip; zone deaths are skipped by keepWorld for skywynn_z* (I:9829) although 2026-10-15 says deaths go home.
  3. The 0.5.15 ruins bed (I:2612-2614, notes I:140-148) is a vanilla RespawnBlock - sleeping in it makes the ruins the respawn.
  4. Bed glitch: the bed's raw getRespawnPosition() is used as Teleport coordinates (I:8976-8979) with no +1 y / safe-ground check
     -> spawn inside / under blocks, "had to move the bed".
- Fix (Islands, same round as bug 1): retry up to 4 times with back-off, then a visible WARN; a safe-ground offset for bed targets;
  zones follow the 10-15 decision (ask Skyy only if zone deaths should stay in the zone - default: go home); stale beds in other
  worlds no longer block route 1.
- Test: die on the island, in Zone 1 and in the hub (each 2x); sleep in the island bed and die; move the bed next to a wall and die.

### 3. Golem one-shots with no attack animation - see section 1b (SkyyMobs)

### 4. Lag (chunks wait, 3 s black screen, freeze on respawn) - OPEN, not proven
- Top suspects: (a) the respawn trip of bug 1/2 - a second Teleport and, when the island world is unloaded, a world + chunk load on
  respawn (I:98-107, I:130-138; WorldGen zone load W:217-246, 6435) = the respawn freeze; (b) SkyyWorldGen zone chunk masking
  (W:3862, 5899) on first visits - WorldGen 0.7.3 (16:08, after the video) already cut mirror() 2.3 -> 1.2 ms per active chunk;
  (c) Islands time sync every 5 s per world with saveProps file writes when time.held changes.
- Fix: bugs 1/2 round removes (a); then ONE lag pass with numbers: a server-side tick timer per Skyy system (Core helper) logging any
  system > 5 ms, and the Islands sync made cheap (no file write on a steady state). Do not guess - measure first.
- Test: respawn on the island 5x (no freeze), first trip into Zone 1 and Zone 2 (time to land), 10 min play: the new timing lines.

### 5. Skip / mid-air jump does not fire - OPEN, ours (SkyyArmory Monk; same root in SkyySkills Double Jump)
- Detection: A:~13595 `jEdge = ms.jumping && !s.prevJump`; edges() A:13345-13370, bound() A:13297; window bound.before 0.25 s /
  bound.after 0.1 s; Double Jump S:1312-1330, 2596-2603 (trigger `jump`).
- Root cause: the 2026-10-08 Monk probe (docs/log/2026-10.md:217) found the jump key in MID-AIR is not seen by the server
  (MovementStates.jumping is the client's jump physics state, not the key). A tap pressed before landing gives no edge; holding
  space keeps jumping true so the ground jump after landing works = exactly "holding works, skip does not".
- Movement 2 (01:44) changed only the jumpForce / speed writers, not input -> NOT fixed. The Armory's per-tick jumpForce reset only
  lowers the height.
- Fix (Armory, lean): make the velocity-spike "landing hidden" path (vy > 0.5 x jumpForce after falling) the main trigger for a
  skip, widen bound.after to 0.25-0.3 s, keep airPress only as a bonus. Add Skyy's design notes in the same round: less Stamina regen
  and no Mana regen while skipping, jump-off-and-crouch stays allowed. (Double Jump: offer trigger `both` with crouch - Skills, later.)
- Test: chain 10 skips by tapping space on landing; held space; `/armory debug monk on` and read the "Bound ... (how)" lines.

### 6. Hit through blocks - OPEN, ours in part (SkyyClasses / SkyyArmory), source not confirmed
- Our area hits with NO line-of-sight test: Whirlwind / spin spinTick C:12807-12855 (radius only - Skyy plays Monk and "spin works",
  but check Armory's Monk moves too), blastAt C:13643, rayHits C:13367 (Piercing Shot C:13477, Rapid Fire C:13558), novaRun C:17322;
  Armory Rising Strike cone A:13418, Pole-Vault kick sweep A:13260 / kickTest A:12911. LOS helpers already exist: Classes arcClear
  C:15115, Armory TravMath.clear (A:11617, 12543, 14035, 14579).
- "Broke after an update" may also be a vanilla / The Armory weapon selector without TestLineOfSight - not read.
- Fix (two builders): Classes - arcClear on spin / blast / nova / rayHits targets; Armory - TravMath.clear on the cone + kick, and a
  scan of Bo / fist Raycast selectors for TestLineOfSight. Ask Skyy which attack it was (plain swing or an ability) if it stays.
- Test: a mob behind a 1-block wall: plain swing, spin, Rising Strike, Pole-Vault kick, Explosive Arrow, Rapid Fire; must miss.

### 7. Red chat "No handler for skill exp received with name 'Exploring'" - NOT OURS (source not found)
- Searched every archive in UserData\Mods (all ~250, nested jars too), HytaleServer.jar, Assets.zip text files and the client exe
  (UTF-8 + UTF-16): no "No handler for skill", "skill exp ... received with name" anywhere. SkyyExploration only uses
  skill:fn:addxp / skill:stats:Exploration (name "Exploration"). Only EndlessLeveling (NOT enabled) has the word "Exploring".
- Status: can't fix from here. Ask Skyy for a screenshot of the line (or whether it repeats); the wording in the bug list came from
  Cobb's transcript and may not be exact.

### 8. "Scaring 10 fishes!" chat text - NOT OURS (source not found)
- Same search: no "Scaring" in any installed file, SkyyFishing 0.1.10 included. Likely a debug line sent by the engine / client at
  runtime or an inexact transcript. Status: can't fix; low pain. Ask for a screenshot if it repeats.

### 9. Sky snaps from day to night - OPEN, ours (SkyyIslands time sync)
- I:180-200 (0.5.13 "island time = hub time", islands.syncTime default on) + I:9955-9987 syncTime: setGameTime jumps an island /
  shard world to the hub clock (up to almost a full day) on arrival (within 1 s) and every ~5 s. Zone worlds are NOT synced (WorldGen
  only reads WorldTimeResource W:1843), so island <-> zone trips cross two clocks. SkyyHud only reads time (H:1403).
- Fix (Islands, in the bugs 1/2 round): sync zone worlds to the hub clock too (one clock everywhere) and never jump while a player is
  in the world - only move the clock while the world is empty, or ease it. Dynamic Seasons stays a suspect if it still snaps.
- Test: `/time` day in the hub, night on the island, then go to the island, then to Zone 1: no snap.

### 10. Void Dragon in the Hub frozen in the ground, no aggro - see section 1b

### 11. Torch does not refill from the off-hand - OPEN, not built (SkyySacks)
- The stack auto-refill sweep (K:9263) and its container lists (K:5327, 5558, 6280, 12716) cover hotbar / storage / backpack only
  and refill from the Void bag pool only; no utility (off-hand) container anywhere.
- Existing mod (PROJECT-RULES 2): `OffhandAutofill_v0.1.0.jar` is in Skyy's Mods folder (not enabled, licence unknown) - run
  skywynn-mod-check on it first; if it fits and does not clash with Sacks' refill, pack it; else learn from it.
- Fix (Sacks, lean): when a hotbar stack empties, also pull the same id from the utility container (verify Inventory.getUtility()
  in the jar), and refill the off-hand torch from hotbar / bags.
- Test: torches in off-hand + hotbar; place the hotbar ones to 0 -> refilled from the off-hand; with the Void bag holding torches.

### 12. Unidentified drops already show the weapon type (mace) - OPEN, ours (SkyyGear), by design until now
- G:1467-1478 (mystery bags, 0.2.x spec): a bag stores `mys` (type key Weapon_Mace ...) at DROP and the tooltip says
  "Unidentified Sword"; only the item, level and stats are picked at identify (G:1474). Skyy now: "they shouldn't decide what the
  item is until it's identified."
- Fix (Gear, FULL round - identify / saved item data): new bags store only the group (weapon / armor + armor type for armor, or class
  lean); the type is picked at identify; the name / tooltip say "Unidentified Weapon" / "Unidentified Heavy Armor"; old bags keep
  their stored type (no migration of items). Needs one Skyy answer first: should a weapon bag still lean to your class's weapons
  (today 50 %)? [default: yes, the lean stays, applied at identify].
- Test: kill mobs until 3 bags drop: no type shown; identify each: a weapon / armor of any type (class lean); an old bag still works.

### 13. Text cut off - OPEN, ours (three mods)
- Quest widget = SkyyHud, not Quests: H:3709 fitText + questPairs H:3717-3741 cut every line to one row with "...". Fix: word-wrap
  long task / where lines into extra rows (textW), within the widget's row cap.
- Zen tree panel = SkyyTrees: detail labels fixed heights T:9184-9193 (Now / Next / Need 44 px, How 66 px; T:1397 already raised How
  once). Fix: size each label from its wrapped line count; check node names in grid cells.
- Collections grid = SkyyCollections: fitPx Co:6871-6908 and util.clip Co:2594 cut reward / craft text. Fix: wrap to a second row
  or widen the columns (research/Menu-Pattern.md sizes).
- Test: the longest quest task at small and large HUD scale; every Zen node; the longest Collections rewards (new metals).

### 14. Log break shows chest-GUI texture particles; leaves float after a chop - OPEN, cause not proven
- We do not remove tree blocks without the engine: Skills Fell (S:1245-1300) only watches; Trees' Tree Feller breaks logs with
  BHU.performBlockBreak (T:7406) = normal particles; BOP.setBlock (T:8041) only replants saplings. So the bad particle is a block
  whose particle texture is missing (a zone / pack wood or leaf block - SkyyWorldGen zone trees are suspects).
- Floating leaves: vanilla physics leaves them; we never decay leaves. Skills 0.4.50's cap raise (22:43) does NOT change this.
- Fix: first find the block id (ask Skyy which tree / zone, or `fell.debug=true` lines); then (a) if it is a SkyyWorldGen block, give
  it a particle texture; (b) leaf clean-up after a felled tree (break unsupported claimed leaves with the engine break) - a design
  call for Skyy [default: yes, like SkyBlock]. Owner of (b): SkyyTrees.
- Test: chop a vanilla tree and a Zone 1 tree with fell.debug on: particles and leaves.

### 15. Quest still says "accessory bag" - OPEN, ours (SkyyQuests) - NOT fixed by any deploy
- Q:487 first_accessory hint "Craft one at a bench, then put it in your Accessory Bag"; Q:1850-1851 (0.4.0) rewrites the old hint
  to "Craft one in your Accessory Bag's Craft tab" - still the old name. The Void Charms rename (TEST 176) skipped Quests.
- Fix (Quests, lean): hint -> "Craft one in your Void Charms' Craft tab"; the load-time rewrite also catches both shipped old
  hints (owner-edited text kept); grep Quests for any other "Accessory Bag".
- Test: tutorial quest list: the first_accessory line names Void Charms.

### 16. Charcoal from the furnace does not count for collections - PARTLY FIXED (TEST 177, 16:08)
- At the video time no Charcoal collection existed. Since Collections 0.2.25 + Sacks 0.8.20 it counts, but ONLY Charcoal made in the
  /craft Furnace (SkyySacks ledger -> coll:fn:add source sacks:furnace, Co:51-55, Co:1059, K:652-656). A PLACED world Furnace still
  gives no credit.
- Fix (Skills, lean, after 0.4.52): Skills already sees take-outs from a placed Furnace's output slot (SmeltXp handle S:~18598-18640,
  output container 2); when the id is Ingredient_Charcoal, call coll:fn:add {UUID, "Ingredient_Charcoal", got, "skills:furnace",
  pkey}. Collections must accept the new source (one line in its default bridge.add.sources + "accepted even when missing" like
  sacks:furnace) - a 2-line Collections change; ship together.
- Test: burn wood in a placed Furnace, take the Charcoal out: the Charcoal collection rises by that amount, once.

### 17. "Wooden Hoe" in the Anvil upgrade list - OPEN, ours (SkyyGear), not on purpose
- Hoes and sickles are retired since Gear 0.3.14 (G:666, G:37467 harvester.only), but the Upgrade tab lists "every item you carry
  that can tier up" (G:686-690, G:30704) and the lifelong ladders still hold the hoe + sickle rows (G:6032-6033). A hoe still carried
  (a lifelong hoe waiting to merge into the Harvester, G:44775-44790, or any crafted hoe) shows up. "Wooden" = our ladder word for
  Crude (G:43069).
- Fix (Gear, lean): with harvester.only on, leave Tool_Hoe_* / Tool_Sickle_* out of the Upgrade tab (and the ladder rows) and show
  "Hoes are retired - your Harvester" instead; check why the hoe did not merge (it should merge once both are carried).
- Test: carry a Crude Hoe: not in the Upgrade list; the merge message shows.

### 18. "Altar of Summoning" cart / kit does nothing - UNKNOWN item
- No item or block named "Altar of Summoning" (or "Summoning Altar") in Assets.zip, any enabled pack mod or our jars. Closest:
  Nestkeeper's "Saurian Trader Statue" (Nestkeeper_Saurian_Spawner, "A merchant summoning statue", left click summons a Trader).
- Status: needs Skyy's screenshot / item id (hover the item; or which structure it sat in). Low pain - after the others.

### 19. Mobs do not despawn after the island boss; three "blue guys" together - see section 1b

## 1b. Mob bugs (3, 10, 19)

### 3. Golem one-shots with no attack animation - OPEN, cause not proven; missing safety is ours (SkyyMobs)
- Likely golem: the island-3 Shardkeeper = vanilla Golem_Crystal_Earth, spawned by SkyyIslands at boss.level=10 (I:250-251,
  I:1647-1648; 21:23 log "Golem_Crystal_Earth max health 246.4"). Kami OreGolems is disabled.
- Damage: LevelDamage M:3570-3618, dmgMult M:2577. Vanilla Golem_Crystal hits are Physical 5-10; live config strength.shape=curve
  (~x1.3 at Lv 10, x1.57 at Lv 20, no dmgCap on the curve path, up to x7.24 at Lv 60) x level-gap takenMax 1.5 -> ~20 per hit at Lv 10.
  So SkyyMobs math alone does not one-shot at Lv 10; a higher-level golem, a low-HP player, or several queued hits landing at once
  during lag (bugs 1 / 4 - no animation seen) can.
- Missing safety: strength.hitCap ("one hit at most N % of max HP", M:3607-3616) exists but is 0 = OFF in the live config
  (Skyy_SkyyMobs/config.properties line 35).
- Fix: NOW (no agent) Skyy can set Server Setup -> Mobs -> one hit at most = 35. Mobs lean round: default hitCap 35 with a one-time
  migration (only a line still at the old 0), apply the cap on the curve path too, a `[Mobs] dmg` debug line for any hit > 30 % max HP
  (role, level, raw, final, victim max HP).
- Test: fight the Shardkeeper at full HP with the debug on: no hit above 35 % of max HP; a Zone 1 golem too.

### 10. Void Dragon in the Hub frozen in the ground, no aggro - OWNER UNKNOWN (not ours by any code)
- No pinned script names Dragon_Void / Void_Dragon. Vanilla has the Dragon_Void model but no NPC role; real Void Dragon roles are only
  in EndgameAndQoL (Endgame_Dragon_Void) and VoidAsylum - both DISABLED in config.json. Nestkeeper (ON since 09:53) has Plain / Tundra
  dragons and stationary nest NPCs (Nestkeeper_Dragon_*_Nest_Live / _Old, WanderRadius 1) spawning in Env_Zone1_Forests / Plains -
  the Hub is in Zone 1, so a nest NPC fits "frozen, no aggro".
- Fix: get the role id first (Skyy: look at it with the NPC inspect / entity info, or a screenshot). If a Nestkeeper nest: keep nests
  out of the Hub (SkyyMobs levels.exclude + a no-spawn area for the hub town) - a SkyyMobs / WorldGen lean change; if a vanilla
  Fire / Frost dragon: find the prefab placing it.
- Test: stand in the Hub after a restart: no stuck dragon.

### 19. Mobs do not despawn after the island boss; three "blue guys" - OPEN, ours (SkyyIslands), by design so far
- SkyyIslands never despawns: "A living Shardkeeper is left alone (no despawn)" (I:125), "Skeletons already alive are left to die
  normally" (I:215). camp.stopAfterQuest / boss.stopAfterQuest (I:120-129) stop NEW spawns only. The island-2 camp spawns
  camp.count=3 together (Skeleton_Fighter x2 + Skeleton_Soldier, up to camp.max=5, respawn 60 s; I:242-245, I:1636-1640) = the
  three together.
- Fix (Islands, in round R1): on boss kill / quest done, remove the camp + boss NPCs that Islands spawned (already tracked for the
  camp.max check) on the world thread; a Server Setup row "Clear the camp when the quest is done" (default ON).
- Test: kill the boss / finish the quest: camp mobs gone within ~10 s; leave and come back: none respawn.

## 2. Status table

| # | Bug | Owner | Status | Round |
|---|-----|-------|--------|-------|
| 1 | Invincible after island death | SkyyIslands | open (likely the 1.8 s same-world teleport) | R1 |
| 2 | Respawn at ruins + bed glitch | SkyyIslands | open | R1 |
| 3 | Golem one-shot | SkyyMobs (safety off) | open; Skyy can set hitCap now | R2 |
| 4 | Lag | Islands first, then measure | open, unproven | R1 + R12 |
| 5 | Skip does not fire | SkyyArmory | open (Movement 2 did not fix input) | R3 |
| 6 | Hit through blocks | SkyyClasses + SkyyArmory | open, source unconfirmed | R3 + R4 |
| 7 | 'Exploring' skill exp error | not ours (not found) | can't fix - need screenshot | ask |
| 8 | "Scaring 10 fishes!" | not ours (not found) | can't fix - need screenshot | ask |
| 9 | Sky snaps day -> night | SkyyIslands time sync | open | R1 |
| 10 | Frozen Void Dragon in Hub | unknown (Nestkeeper nest?) | need role id | ask, then R2 |
| 11 | Off-hand refill | SkyySacks (or pack OffhandAutofill) | open, not built | R10 |
| 12 | Unid shows weapon type | SkyyGear (by design) | open, design change | R5 |
| 13 | Text cut off | Hud / Trees / Collections | open | R6, R7, R8 |
| 14 | Chest-texture particles, floating leaves | unknown block / SkyyTrees | need tree id | ask, then R7 |
| 15 | Quest says accessory bag | SkyyQuests | open (rename missed Quests) | R11 |
| 16 | Furnace charcoal not counted | Skills + Collections | partly fixed by TEST 177 (/craft Furnace); placed Furnace open | R8 + R9 |
| 17 | Wooden Hoe in Upgrade list | SkyyGear | open | R5 |
| 18 | Altar of Summoning does nothing | unknown item | need screenshot / id | ask |
| 19 | Mobs stay after island boss | SkyyIslands | open (no despawn by design) | R1 |

## 3. Fix rounds (ONE MOD PER BUILDER, by player pain)

1. R1 SkyyIslands 0.5.20 - FULL round (death / respawn, several bugs): bugs 1, 2, 19, 9 + the respawn part of 4 (no second teleport
   on own-island deaths, 4 retries + WARN, bed safe-ground offset, stale beds elsewhere do not block, camp / boss cleanup, one clock).
2. R2 SkyyMobs 0.1.11 - lean: bug 3 (hitCap default 35 + migration, cap on the curve path, dmg debug line); bug 10 nest exclusion
   once the role id is known. NOTE: Wynn elements wave 1 plans Mobs 0.1.11 - land this first, elements take 0.1.12.
3. R3 SkyyArmory 0.1.35 - lean: bug 5 (velocity-spike skip trigger, wider window, Skyy's skip stamina / Mana notes) + bug 6 Armory
   part (TravMath.clear on Rising Strike cone + Pole-Vault kick; check Bo / fist selectors for TestLineOfSight).
4. R4 SkyyClasses 0.1.39 - lean: bug 6 Classes part (arcClear on spin / blast / nova / rayHits). Elements wave 1 also wants Classes
   0.1.39 - bugs first, elements 0.1.40.
5. R5 SkyyGear 0.3.28 - FULL round (identify path): bug 12 (type picked at identify, "Unidentified Weapon" names, old bags unchanged)
   + bug 17 (retired hoe / sickle out of the Upgrade tab). After Gear 0.3.27 deploys; elements B2 moves to 0.3.29.
6. R6 SkyyHud - lean: bug 13 quest widget word-wrap.
7. R7 SkyyTrees - lean: bug 13 Zen label heights; bug 14 leaf clean-up once Skyy says yes + the block id is known.
8. R8 SkyyCollections - lean: bug 13 grid wrap + bug 16 accept source skills:furnace (ships with R9).
9. R9 SkyySkills 0.4.53 - lean, after 0.4.52: bug 16 placed-Furnace Charcoal -> coll:fn:add skills:furnace.
10. R10 SkyySacks - lean: bug 11 off-hand refill (after skywynn-mod-check on OffhandAutofill_v0.1.0.jar).
11. R11 SkyyQuests 0.4.2 - lean: bug 15 Void Charms hint text.
12. R12 lag pass (bug 4) - after R1 is tested: measure first (per-system tick timer), then fix the top offender.

Ask Skyy (one popup each): screenshots / item ids for 7, 8, 18; the Hub dragon's role id (10); which tree + zone for 14 and "clear
floating leaves after a chop?" [yes]; "weapon bags still lean to your class at identify?" [yes]. Now, no agent: Server Setup ->
Mobs -> one hit at most 35 %.
