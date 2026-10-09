# SkyyQuests - the Zone 1 town quest line, the Job Board and how it is built

Cloud draft, 2026-10-09. Paper design, no code. It fills the engine in `research/cloud/SkyyQuests-Spec.md` (the earlier cloud draft; this file does not repeat its object types, bridge or UI sections - it uses them) with the **first real content**: 9 quests in the Zone 1 town, a daily Job Board, and the plan to build both in small versions. Everything about the engine is **UNVERIFIED** (no game files in the cloud); every number is a placeholder and a Server Setup row.

## 0. Decisions this follows (newest wins; none re-decided)

| Source (file + line) | Lock | Used here |
|---|---|---|
| `docs/answered/project.md` 22 | "quest hooks ship with SkyyQuests, not now" | the line is built in SkyyQuests, not in older mods |
| `docs/answered/gear.md` 124 (RARITY NAMES) | a **Set** = normal pieces until ALL 4 are worn, then one buff (e.g. +100 Health); "sets will primarily be quest items, special versions of armor you can already get" | the 4-piece quest Set (section 2.2) |
| `docs/answered/gear.md` 125 (GATHERING SETS) | gathering armor also uses the Set label | not used here (this Set is a combat/general set) |
| `docs/answered/gear.md` 127 (UT sources corrected) | UT sources = mob drops, chests, bosses **and quests**; never crafted, never sold in NPC shops | the one UT reward (section 2.3) |
| `docs/answered/world.md` 52-54 | Zone 1 town = the vanilla spawn temple (door to the sea, spawn at the foot of the causeway), organic v2 layout, crypt stays vanilla, plain halls restyled later | NPC positions come from `research/cloud/Zone-1-Town-Layout.md` section 8 |
| `docs/answered/world.md` 57 | Aetherhaven (Hexvane) is a **design reference**, not a dependency | the Job Board is our idea of its quest board (idea only, no code, no data) - `research/Mods-Folder-Survey.md` lines 82-90 |
| `docs/answered/world.md` 13 (R8) | starter shard gaps: first a repair, later a build | the starter chain stays in `research/cloud/Story-Script-Draft.md` part 1; this line starts when the player arrives in town |
| `docs/answered/economy.md` 91 | our own roaming merchants (NPC spawn route proven in `SkyyMerchants`) | NPC pattern, section 5 |
| `research/cloud/SkyyQuests-Spec.md` 5 | rewards: coins `coins:fn:add`, XP `skill:fn:addxp`, items, `gear:fn:roll`, flags; R3 rule: quests may give coins, never skip collections | all rewards below |
| `research/cloud/Story-Script-Draft.md` 2.3-2.6 | Z1.1-Z1.5 (Take A Number, Form 27-B/6, Which Game, What Is A Game, The Guardian's Paperwork) + running jokes | quests 1, 5, 7, 9 here are those, merged (no story re-decided) |
| `research/cloud/Untiered-Mythic-Spec.md` 1.4 + 3 | UT may come from quests (never shops); the Zone 1 town line hands out one Set piece per step | sections 2.2, 2.3 |

## 1. In plain words

- Nine quests teach the town, one by one: the Waiting Room, the Bank, the Bazaar, the Forge, a stamp hunt, a hermit, the Zone 1 guardian. They are the **Department of Arrivals paperwork**, so every errand is silly and every number is a little wrong.
- Four of them each hand over **one piece of a Copper armor Set** ("Clerk's Copper"). Wear all four and you get the full-set buff. The last quest hands over **one Untiered weapon** for your class.
- Once you have done the first two, the **Job Board** by the spawn steps gives you **3 small daily jobs** (hunt, gather, deliver, explore). They pay coins and skill XP, never gear.
- Pebble gives the first errand and then wanders off to be found; Clerk Mossby runs the paperwork. Both stand in the town and talk when you press **F**.

## 2. The quest line: "The Department of Arrivals - Zone 1" (chain `town1`)

Level = recommended Overall Level, shown on the quest; only quest 9 is gated by a hard check. Order is fixed 1 to 9 (a quest needs the one before it, `requires.flag`), except that **quest 2 can run next to quest 1** and the Job Board opens after quest 2.

### 2.1 The table

| # | Id | Name | Giver (where, `Zone-1-Town-Layout.md` 8) | Lv | Objectives | Rewards |
|---|---|---|---|---|---|---|
| 1 | `town1.q01_number` | **Take A Number** (Z1.1) | Clerk Mossby (desk, temple hall, (0, -8)) | 1 | `talk` Mossby; the ticket is handed over | 100 coins, quest item **Ticket #4,000,000,001** (bound), flag `town1.q01_done` |
| 2 | `town1.q02_wait` | **Waiting Is An Activity** | Pebble (Waiting Square, (-8, 50)) | 1 | `reach` the Warp Pad (-24, 44) and the Door Home (26, 44), radius 3 (a short walk that shows the player the town) | 50 coins, 50 Exploration XP, opens the Job Board |
| 3 | `town1.q03_change` | **Pocket Change** | Banker (Bank, (-80, -56)) | 3 | `bridge` `bank:<uuid>` >= 200 (put 200 coins in the Bank through the live Bank page) | 150 coins, **Set piece 1: Copper Cap** |
| 4 | `town1.q04_sell` | **Buy Low, Sell Lower** | Bazaar broker (Bazaar hall, (78, -52)) | 5 | `event` `bazaar:sell` count 10 items (sell any 10 items on the live Bazaar page) | 200 coins, **Set piece 2: Copper Gloves** |
| 5 | `town1.q05_form` | **Form 27-B/6** (Z1.2) | Clerk Mossby | 7 | `group` of 3 `reach` stamps: the Kweebec homes (district 13, (75, -95)), the Trork camp sign at Birchwood Bureau (outpost Z1-2), and Pebble (found at Greenfield Annex, outpost Z1-1; he "walked off") | 250 coins, 150 Exploration XP, quest item **Proof of Existence (Form 27-B/6, stage 1)** |
| 6 | `town1.q06_mail` | **Return To Sender** | Clerk Mossby (mail box (-27, -16)) | 9 | `deliver` 3 letters (3 quest items, bound, handed out on accept): to the Smith, the Guild clerk, the Auction clerk; a `use` on each NPC | 150 coins, 100 Smithing XP |
| 7 | `town1.q07_game` (Z1.3 + Z1.4) | **Which Game?** | the Hermit (outpost Z1-3 Gorge Gate Post, Lv 7-14) | 11 | bring the form (`have` Proof of Existence), then `choice` x3 (the hermit's questions; any answer passes) | 300 coins, **Set piece 3: Copper Greaves**, quest item **Stamp 1: GAME - Hytale (probably)** |
| 8 | `town1.q08_forge` | **Reforge Of Passage** | Smith (Forge, (-104, 48)) | 14 | `event` `gear:identify` count 1 (identify one unidentified item on the live Identify page) | 250 coins, 150 Smithing XP, **Set piece 4: Copper Chestplate** (the set is complete) |
| 9 | `town1.q09_guardian` (Z1.5) | **The Guardian's Paperwork** | Clerk Mossby | 20 | `kill` the Zone 1 guardian (Earthen Golem, Lv 20, summit arena; boss kill by role id) | 600 coins, 300 Combat XP, **one Untiered weapon (section 2.3)**, quest item **Page 2 of Form 27-B/6**, flags `zone2.portal` (Zone 2 opens), `town1.q09_done` |

Totals (python3: coins 100+50+150+200+250+150+300+250+600 = 2,050; XP 50+150+100+150+300 = 750): **2,050 coins, 750 skill XP** over the whole line. That is 20.5% of the 10,000 test starter coins (`research/cloud/Player-Guide-First-Hour.md` section 6): a nudge, not an income.

Notes on the table:
- Quest 5: the three stamps are **three `reach` points** (no custom block needed): (a) a stamp post in the Kweebec homes lane, (b) the Trork camp warning sign at Birchwood Bureau (outpost Z1-2, `research/cloud/Outposts-List.md`), (c) Pebble himself, standing at Greenfield Annex (Z1-1). Reaching one point stamps the form on the quest page (a line turns green).
- Quest 7: the hermit is placed at **Gorge Gate Post (Z1-3)** because the story says "a Drifting Plains hermit" and Gorge Gate is the wide-range (Lv 7-14) outpost; question 4.
- A player who already finished a later part by other means is not skipped; the town line is **not** a tutorial (the starter shards are), so no skip flag. Existing profiles just start at quest 1.

### 2.2 The Set: "Clerk's Copper" (set id `copper_quest`)

| Piece | Vanilla base id (these ids exist: used in SkyyGear / Armory scripts) | Quest | Level of the piece |
|---|---|---|---|
| Head | `Armor_Copper_Head` | 3 | 3 |
| Hands | `Armor_Copper_Hands` | 4 | 5 |
| Legs | `Armor_Copper_Legs` | 7 | 11 |
| Chest | `Armor_Copper_Chest` | 8 | 14 |

- The piece is the **vanilla Copper item** with the document fields `rarity=set`, `set=copper_quest`, `id:true` (identified, "you know your reward"), as in `research/cloud/Untiered-Mythic-Spec.md` 3.1; a crafted Copper chest never counts, because its document has no `set` field.
- Level of a piece = the quest's level (that spec, section 3). The pieces therefore have different levels and a player wears all four at about Lv 14. Reforge level-up is +6 on a Set piece (same spec).
- Full set (4 of 4 worn): one extra buff block. Placeholder: **+40 Health** (a scaled-down take on Skyy's "Cobalt + 100 Health" example, because Copper is a Lv 1-18 metal). Nothing at 1-3 pieces (Skyy: "the same as vanilla until you put on all 4"). Number lives in the Set table `set.copper_quest` in Server Setup -> Gear -> Sets (not built yet; `research/cloud/Untiered-Mythic-Spec.md` 3.1).
- Set quests as a whole depend on SkyyGear's set support (phase 3 below). Until then the claim ledger (section 6) holds the piece as **owed** and pays it the moment the grant bridge appears.

### 2.3 The one Untiered reward (quest 9)

| Class | Reward (first-batch UT2 name from `research/cloud/Untiered-Mythic-Spec.md` 1.3) | Trade-off line |
|---|---|---|
| Mage | **The Loophole** (staff, U1) | quick shots pierce a line, 30% less damage |
| Warrior | **The Paperweight** (sword, U2) | +50% damage per hit, two speed tiers slower |
| Berserker | **Overtime** (axe, U3) | +30% damage under half Health, -10% max Health |
| Assassin | **The Pocket Knife** (dagger, U4) | backstab +50%, front hits -30% |
| Archer | **Short Notice** (shortbow, U5) | arrows twice as fast, range 12, -15% damage |
| Priest | **The Second Opinion** (wand, U6) | heal orb x1.5, wand shots -40% |
| Monk | **The Turnstile** (Bo staff, U7) | hits knock back x2, -25% damage |

- **No UT item ids exist yet** (the UT round is not built; the first batch has names only). The quest data holds a `reward.ut=<utId>` key that SkyyGear resolves at grant time (`gear:fn:grant`, proposed in `research/cloud/Untiered-Mythic-Spec.md` section 6 item 7). Proposed ids: `ut.u1_loophole` ... `ut.u7_turnstile` (table keys, not Hytale item ids). Until they exist, quest 9 pays everything else and keeps the UT **owed**.
- The UT2 band is Lv 15-29; the quest's Lv 20 sits inside it, so the item is Lv 20 (clamp rule, same spec 1.1). Identified, fixed stats, no Mystery Bag.
- Sources rule respected: a quest reward, never a shop, never crafted. Quest 9 repeats on no profile twice (the `done` set, section 6).

### 2.4 Dialogue (short, in tone)

Voice rules (`research/cloud/Barks-Signs-Tips.md`, `research/cloud/Story-Script-Draft.md` 2.6): lines under 90 characters, numbers slightly wrong, "waiting is an activity", the Void hiccups (*HIC.*), Pebble is cheerful and wrong, Mossby is slow and yawns.

**Q1 Take A Number** (Mossby)
> **Mossby:** Next. ...oh, you are new. Take a ticket. *(hands #4,000,000,001)*
> **Mossby:** Four billion and one. Busy day. Sit anywhere. They are all yours.
> *HIC. The Board: NOW SERVING #-7.* **Mossby:** That is not a number. I will check the manual. *(falls asleep)*

**Q2 Waiting Is An Activity** (Pebble)
> **Pebble:** Ticket number two! Been next for four thousand years. I let others go ahead. Out of respect.
> **Pebble:** Walk to the glowing ring, then the stone arch. Standing in places is how you learn them.
> *(done)* **Pebble:** Two places! You are practically local. I have seen eleven. Twelve. Whatever comes after twelve.

**Q3 Pocket Change** (Banker)
> **Banker:** Money in your pocket is just weather. Put two hundred in the Bank. It sits still, politely.
> *(done)* **Banker:** It earns interest at the speed of rock. Take this cap, it was never worn by anyone. Probably.

**Q4 Buy Low, Sell Lower** (broker)
> **Broker:** I buy at ninety, I sell at one-ten. It is called "a service". Sell me ten things, any things.
> *(done)* **Broker:** Ten! You lost twenty percent doing it. That is how you know it was real commerce. Gloves.

**Q5 Form 27-B/6** (Mossby, then Pebble at the end)
> **Mossby:** The form needs three stamps. Kweebecs, Trorks, and... Pebble. Where did he go? ...where was I.
> *(at Pebble)* **Pebble:** I am not lost. The town moved. Stamp me. Gently, I am load-bearing.
> *(back)* **Mossby:** Three stamps. Proof of Existence. I did not think you would manage. Congratulations.

**Q6 Return To Sender** (Mossby, mail box)
> **Mossby:** Three letters. Sorted by a method. The method is lost. Smith, Guild clerk, Auction clerk. Do not read them.
> *(done)* **Mossby:** You read them. I can tell. Everybody does. Take some coins for the guilt.

**Q7 Which Game?** (Hermit; the questions are from `Story-Script-Draft.md` 2.4)
> **Hermit:** Q1. When you hit a tree, what happens? *(it gives wood / it explodes / it files a complaint)*
> **Hermit:** Wood. Obviously. Q2. When you die? *(you respawn / you wake in a waiting room / a ghost with a tiny hat)*
> **Hermit:** Q3. A dragon? *(yes, great / only myths / I am allergic)* ... Allergic. Classic Orbis. Your game is Hytale. Probably.

**Q8 Reforge Of Passage** (Smith)
> **Smith:** Unidentified gear is a surprise nobody ordered. Identify one. I will watch. I will not help.
> *(done)* **Smith:** Fine work. A chestplate for your trouble. Wear the whole set. It hums.

**Q9 The Guardian's Paperwork** (Mossby; the guardian lines are in `Story-Script-Draft.md` 2.5)
> **Mossby:** Page two is held by the Guardian of Page Two. He protects it. Page one is not his problem.
> *(done)* **Mossby:** Page two. Nobody has ever read it. It says "SEE PAGE 3 (ZONE 2)". The portal is yours. *HIC.*

## 3. The Job Board ("Odd Jobs", Form 11-J)

A separate sign beside the Zone 1 town map sign at the spawn steps (the layout's `town.2` Board is the **NOW SERVING** board, which announces zone specials in `research/cloud/Barks-Signs-Tips.md` section 4; the Job Board sits next to it so the two are not confused).

| Topic | Design |
|---|---|
| What | an invulnerable **board NPC** with a Use (F) interaction that opens a page (the same NPC route as Mossby; the build is not a block, because NPC Use is the proven path, section 5) |
| Opens | after quest 2 (before that the page shows "Ask Pebble first.") |
| Jobs per day | **3 per profile**: Easy (Lv-band mob hunt or gather), Medium (deliver or craft), Hard (a named mob / far outpost) |
| Pool | about 12 Zone 1 jobs at launch (section 3.1); picked by a seed = hash(profile key + day number) so a restart or relog shows the same 3 and cannot be rerolled by logging out |
| Refresh | **daily**: the reset moment is `board.anchorSeconds` after UTC midnight (default 0); jobs not done are simply replaced. Done jobs are paid once. Nothing carries over (no streak in 0.2; question 3) |
| Reroll | none by default (`board.rerolls` = 0); one coin-priced reroll per day can be switched on |
| Rewards | coins (40 / 80 / 140 = **260 a day**, 1,820 a week) + small skill XP; **never gear**, never a UT, never a collection tier (R3). Rewards scale with the job level, not the player's |
| Level fit | a job's mob/outpost must be inside the player's Zone 1 band (the Overall Level 1-20); the level-gap rule from `research/cloud/SkyyQuests-Spec.md` 3 applies (far-below kills count 0) |
| Party | each member gets their own board; kills credit the killer (spec section 8) |
| Remote | off: the board is read at the board (`board.remote` row, default off) |

### 3.1 The first job pool (placeholders; mobs and levels from `research/cloud/Mob-Levels-Refit.md`, UNVERIFIED role ids)

| Kind | Job | Count | Lv band | Reward (coins / XP) |
|---|---|---|---|---|
| hunt | Clear out the Plains (any hostile in Zone 1 plains) | 10 | 1-8 | 40 / 20 Combat |
| hunt | Trork notice (Trork camp mobs, Birchwood Bureau area) | 8 | 5-10 | 80 / 40 Combat |
| hunt | The blue forest complaint (Azure forest mobs) | 6 | 18-20 | 140 / 70 Combat |
| gather | Bundle of logs (any log, obtained) | 32 | 1-20 | 40 / 20 Foraging |
| gather | Copper for the forge (Copper ore, obtained) | 20 | 1-20 | 80 / 40 Mining |
| gather | Wheat for the stalls (Wheat, obtained) | 24 | 1-20 | 40 / 20 Farming |
| deliver | Parcel for the Smith / Bank / Guild (a bound parcel item) | 1 | 1-20 | 80 / 30 Exploration |
| craft | Make a Workbench item (one craft event) | 1 | 1-6 | 40 / 20 Smithing |
| craft | Make 4 Torches (craft event) | 4 | 1-20 | 40 / 20 Smithing |
| explore | Visit an outpost you have not found (`explore:` warp not unlocked) | 1 | 1-20 | 140 / 70 Exploration |
| explore | Stand at the Promenade headland viewpoint ((124, 60)) | 1 | 1-20 | 80 / 30 Exploration |
| hunt | A named mob, once a day (the Zone 1 elite) | 1 | 15-20 | 140 / 70 Combat |

All `gather` jobs count **obtained** items (not bought, not bag withdrawals), exactly the Collections "obtained" rule (`research/cloud/SkyyQuests-Spec.md` 3 and 8).

## 4. Data model (per profile: `tools/PROFILES-CONTRACT.md`)

Quest/dialogue file formats, flag names and objective types are exactly `research/cloud/SkyyQuests-Spec.md` sections 1-3. This section adds only what the Zone 1 line needs.

| Item | Where | Notes |
|---|---|---|
| Quest files | `Skyy_SkyyQuests/quests/town1/<id>.properties` (shipped defaults in the jar, copied once; edits survive) | `id, chain, order, name, giver, level, requires.flag, steps, step.N.type, reward.coins, reward.skillxp, reward.gear (set id + piece), reward.ut, reward.item, reward.flag` |
| Dialogue | `.../dialogue/town1.q0N.properties` + `quests.lang` keys | text in the lang file (translatable) |
| Player state | `Skyy_SkyyQuests/players/<pkey>.properties`, **`pkey(u)` from the Profiles contract, never `u.toString()`** | atomic `.tmp` + move, dirty set + saver thread; a profile switch settles 6 s (no progress while `profile:busy:<uuid>`); caches keyed by the pkey String and republished on `profile:epoch:<uuid>` (contract rules 1-3) |
| Board state | same player file: `board.day=<epoch day>`, `board.seed`, `board.slot.1=jobId|progress|state` (state `open/done/paid`), `board.done.<day>=N` | derived jobs can always be re-computed from the seed; only progress and `paid` are stored |
| Claims (rewards waiting to be paid) | same file: `claim.<n>=<type>|<payload>|<grantId>` | section 6 |
| Town NPC registry | owned by **SkyyTowns** (`npcs.json`, `research/Zone-1-Town-Build-Plan.md` section 6): `id, role, x, z, facing, page id, bark key`; **new key `quest=<npcId>`** | SkyyQuests never spawns a town NPC; it asks the bridge |
| Per-player vs per-profile | quest state, board state and flags = **per profile** (a new class is a new profile and starts at quest 1); the town and NPCs are shared | alt profiles each earn their own Set / UT (see question 8) |

Flags read by other mods through the bridge (`quest:fn:flag`, spec section 6): `town1.q01_done` ... `town1.q09_done`, `zone2.portal` (read by SkyyWorldGen/SkyyIslands `unlock.mode=quest`; the owning mod decides what it unlocks), `board.open`.

New bridge functions this line needs (plain `java.lang` types, the existing `skyy.bridge` map):

| Key | Shape | Who calls it |
|---|---|---|
| `quest:fn:hasoffer` | `Function(Object[]{UUID, String npcId}) -> Boolean` (a quest to start or turn in with that NPC) | SkyyTowns, in its NPC Use handler |
| `quest:fn:talk` | `Function(Object[]{UUID, String npcId}) -> Boolean` (opens the dialogue next tick on the world thread; false = nothing to say) | SkyyTowns, in its NPC Use handler |
| `quest:fn:event` | already in the spec: `{UUID, "bazaar:sell"/"gear:identify"/"bank:deposit", key, amount}` | SkyyBazaar, SkyyGear, SkyyBank (a one-line call each at their next versions) |
| `gear:fn:grant` | proposed in `research/cloud/Untiered-Mythic-Spec.md` section 6 item 7: `{UUID, id, level, rarity, set, pool, String grantId}` -> Boolean | SkyyQuests (new: the `grantId` makes it idempotent, section 6) |

Without SkyyBank / SkyyBazaar / SkyyGear present, a quest that needs one is hidden from the log (zero-dependency rule); with the mod present but without its `quest:fn:event` call (older version) the objective just never moves, so build SkyyQuests only after those calls exist, or use the polled `bridge` objective for quest 3 (reads `bank:<uuid>`, no change to the Bank).

## 5. NPCs: the SkyyMerchants spawn + Use pattern (read-only reference)

Read: `SkyyMerchants/build_skyymerchants_0.1.py` (the newest and only SkyyMerchants build script, commit d861ff9; READ-ONLY).

| What | File + lines | Fact |
|---|---|---|
| Role by name, no vanilla shop | `SkyyMerchants/build_skyymerchants_0.1.py` 13-16 and 89 | a vanilla role chosen by name (`Temple_Klops`: a Variant of `Template_Temple`, so Invulnerable + MotionStatic, no `InteractionInstruction`); a role with no vanilla instruction means no vanilla barter shop opens |
| Use root and hint | same file 90-91 and 637-640 | every NPC gets the vanilla `*UseNPC` root; `Interactions.setInteractionId(InteractionType.Use, "*UseNPC")` + `setInteractionHint("server.interactionHints.trade")`; the engine's hint key says "Press [F] to trade" - a talk hint key is **UNVERIFIED** |
| Name | same file 626-636 (`prepare`) | `Nameplate`, `DisplayName`, `PersistentDisplayName` set from a plain string; `Interactable` ensured |
| Spawn | same file 645-655 (`spawn`) and 26-27 | `NPCPlugin.get().spawnNPC(store, role, null, new Vector3d(x,y,z), rot)` returns a Pair; on the world thread (`World.execute`, line 526); a failed UUID read removes the entity again |
| Use hook | same file 2395-2420 (`MerchUseSys`) and 35-38 | an ECS event system on `UseEntityEvent$Pre`, fired on the PLAYER; it cancels the vanilla use only for registered NPC UUIDs (`e.setCancelled(true)`, line 2413) and opens the page on the next tick via `World.execute`, never inside the handler |
| No duplicates | same file 54-62 | the registry lists each NPC's UUID; a `RefSystem` on `NPCEntity` removes ghosts / orphans (our role AND our nameplate that is not registered); a missing NPC is re-spawned at the same spot after a 15 s grace; atomic `.tsv` write, an unreadable file is never overwritten |

Town plan: SkyyTowns (`research/Zone-1-Town-Build-Plan.md` sections 4 and 6) spawns and keeps **all** town NPCs with this pattern. Two mods must not both cancel Use for one NPC, so:

- SkyyTowns owns the Use hook for the town NPCs. When an NPC has `quest=<npcId>`, its Use handler first asks `quest:fn:hasoffer`; if true it calls `quest:fn:talk` (dialogue), else it opens the NPC's page (Bank, Bazaar...). Pebble, Mossby, the Hermit and the Job Board have no page, so they always go to `quest:fn:talk`.
- Look: Mossby = a vanilla Kweebec variant (`Temple_Kweebec_Static`, as `SkyyTownProbe/build_skyytownprobe_0.1.py` line 38 probes). **Pebble** = our own art, `art/pebble/` (`Pebble/Pebble.blockymodel`, 256x192 texture, 128x128 icon, Idle / Walk / Talk / Wave animations, about 0.99 blocks tall, nameplate on the `Head` node; Skyy 2026-10-08: "Pebble looks great, keep it as is"; `ART-RESUME.md` "Done" section 1). Not yet tested in game; the probe `/townprobe pebble` (build plan section 9) decides model vs the vanilla `Rubble_Stone_Mossy` fallback.
- Pebble stays invulnerable (art note), and "walks off" in quest 5 by moving between two registered spots (Waiting Square then Greenfield Annex); the second spot is a second registry line for the same NPC id with `phase=after_q04`.

## 6. Dupe safety for rewards

| Reward | Failure to prevent | Rule |
|---|---|---|
| Any reward | paid twice (relog, crash, double click) | the quest is marked `done` and every reward becomes a **claim line** in ONE atomic file write; paying a claim removes its line. Each claim has a `grantId` = `<pkey>:<questId>:<n>` |
| Set piece / UT / items from SkyyGear | duplicate item after a crash between grant and line removal | the grant carries `grantId`; SkyyGear keeps a `grants.log` and answers "already granted" (true, no item) for a repeated id. The claim line is then removed. Never trust the transaction: count before/after like SkyyMerchants (`build_skyymerchants_0.1.py` 38-45) |
| Coins / XP | a crash between pay and removal pays again | **at-most-once**: remove the claim line first, then pay, log `quests.log` (`PAID`/`LOST?`). A rare lost payout beats a duplicate; the admin command `/questadmin claim <player>` re-pays logged losses |
| Full inventory | reward dropped or lost | the claim stays; "Reward waiting" shows on the quest page; claim by button (`Claim` in the log page), one at a time. Never dropped on the ground |
| Quest items (Ticket, letters, Proof, Stamp, Page 2) | traded, listed, stored or duplicated | **bound**: refused by `/trade`, the Auction House, the Vault and bag deposit; removed on abandon; `deliver` removes items first, pays after |
| Mailbox letters (quest 6) | player drops and re-gets letters | the three letters are re-issued only while the objective is open; a re-issue replaces, never adds (count capped at 3) |
| Set pieces / UT tradable | an alt profile farms the line and sells pieces | each profile earns its own pieces (by design), so the Set is tradable per `research/cloud/Untiered-Mythic-Spec.md` question 12; question 8 asks if quest pieces should be bound instead |
| Board jobs | farm by reroll, relog, or clock change | seed = hash(pkey, day number); `paid` stored per slot; a job is paid once per day; progress is stored, not the clock |
| `gather` objectives | placed-block / bag-withdraw / `/give` farming | the existing Collections "obtained" rules; admin gives are flagged and never count |
| Profile switch mid-quest | progress credited to the wrong profile | no progress while `profile:busy:<uuid>` or the 6 s settle after an epoch change |
| NPC duplicates | two Mossbys give the quest twice | quest start is guarded by the profile's state, not the NPC, so a duplicate NPC can never double a reward (and SkyyTowns removes orphans) |

## 7. UI (HANDOFF section 2: vanilla look, inline pages, no underscores)

Page rules for every UI below (`HANDOFF.md` section 2 and `tools/skyyui.py`): look and feel **vanilla** through the shared kit (`SUI.page_shell`, `SUI.button`, `SUI.panel_row`); build everything inline, **never ship `.ui` files**; element ids letters + digits only (`#SkyyQLogRow0`); page roots with Anchor Width/Height only; fits a 1080 px screen; inline Text uses only `[A-Za-z0-9 <>/-]`, everything else goes through `b.set`; **no page update from a MouseEntered/MouseExited handler**; never put a metadata ItemStack into an `ItemGridSlot` (reward previews of Set pieces and UTs use `new ItemGridSlot(new ItemStack(id, qty))` plus text via `setName`/`setDescription`); a Close button on every page; the "Loading..." page guard.

| Page | Design (all vanilla-kit) |
|---|---|
| **Quest log** (`/quests`, a SkyyMenu tile "Quests") | tabs Active / Available / Done; left list (name + `Lv N`), right details: summary, steps with a progress bar (`12 / 20`), reward preview (coins, XP, the Set piece with its set progress "Clerk's Copper 2/4", the UT), buttons **Track**, **Abandon** (asks to confirm; quests 1, 5, 9 cannot be abandoned), **Claim** (when a reward waits). Footer Close. A Refresh button, no periodic refresh |
| **Dialogue** | opens on Use; NPC name + Pebble/Mossby icon (`ItemIcon` portrait **UNVERIFIED**, else text), wrapped line, up to 3 choice buttons, Next / Accept / Decline / Close; "skip all" row; instant text (no typewriter) |
| **Job Board** | 3 job cards (kind icon, text, `4 / 10` bar, reward line, state Done/Paid); header "Odd Jobs - refresh in 6 h 12 m"; no buttons that change jobs; Close. Never shows gear |
| **Tracker** | a SkyyHud widget (spec 4.3) with the tracked step, 3 lines max; later phase |

## 8. Commands (HANDOFF section 3)

Rule 1: any command without `requirePermission()` gets an auto node ordinary players lack, so **player commands set `setPermissionGroups(new String[]{"hytale:Adventurer"})` on the command AND every subcommand / usage variant; admin commands use `requirePermission` and no groups.** Rule 2: optional args are not positional, so every documented positional form is a usage variant or a subcommand with `withRequiredArg`.

| Command | Who | Form |
|---|---|---|
| `/quests` (alias `/quest`) | player | opens the log |
| `/quests track <id>` | player | subcommand with required arg (a usage variant, not an optional arg) |
| `/quests abandon <id>` | player | same |
| `/quests board` | player | opens the Job Board only when `board.remote` is on or the player stands within 8 blocks of the board; else a chat line "The board is at the spawn steps" |
| `/questadmin list <player>` | `skyyquests.admin` | quests, claims, board of a player's active profile |
| `/questadmin set <player> <questId> <state>` | admin | start / complete / reset (a reset also removes its claims) |
| `/questadmin claim <player>` | admin | pay logged losses and owed rewards |
| `/questadmin board <player>` | admin | show / reroll the player's board for today |
| `/questadmin reload` | admin | re-read quest files |
| `/questadmin npc` | admin | list quest NPC ids from the SkyyTowns registry and which have offers |

## 9. Server Setup rows (config kit, `tools/CONFIG-CONTRACT.md`; times shown in seconds)

| Row | Default | Meaning |
|---|---|---|
| `quests.enabled` | on | whole mod |
| `quests.maxActive` | 5 | active quests |
| `quests.abandonConfirm` | on | confirm before abandon |
| `quests.markers` | on | `!` / `?` over NPCs (when the engine allows) |
| `quests.rewardMailbox` | on | hold rewards as claims when the bag is full |
| `town1.enabled` | on | the Zone 1 chain |
| `town1.coinScalePercent` | 100 | multiplies every coin reward in the chain |
| `town1.xpScalePercent` | 100 | same for XP |
| `town1.set.enabled` | on | Set piece rewards (off = coins only) |
| `town1.ut.enabled` | on | the quest 9 UT |
| `town1.set.fullBonus` | `maxHealth=40` | the Set buff (later moves to Gear -> Sets) |
| `town1.q05.stamps` | table | the three stamp points (x, y, z, radius) |
| `board.enabled` | on | the Job Board |
| `board.jobsPerDay` | 3 | slots |
| `board.resetSeconds` | 86400 | length of a board day |
| `board.anchorSeconds` | 0 | seconds after UTC midnight when the day starts |
| `board.rerolls` | 0 | rerolls per day (0 = none) |
| `board.rerollCost` | 500 | coins per reroll when rerolls > 0 |
| `board.coinScalePercent` | 100 | board coin rewards |
| `board.remote` | off | open the board from anywhere |
| `board.jobs` | table | the job pool: id, kind, target, count, level range, coins, XP |
| `board.dailyCoinCap` | 1000 | stop paying board coins after this much a day per profile |

## 10. Phases (small versions)

| Round | Content | Size (PROJECT-RULES 4) | Depends on | Done when (Skyy tests) |
|---|---|---|---|---|
| **Q0 probe** | one admin-only probe round, appended to SkyyTownProbe 0.1 (it already has `/townprobe npc` and `/townprobe pebble`): section 11 | lean | the T0 probe round (`research/Zone-1-Town-Build-Plan.md` section 9) | the answers are in `docs/log/` |
| **SkyyQuests 0.1** | engine from `research/cloud/SkyyQuests-Spec.md` section 9 (loader, per-profile state, flags, claims ledger), objectives `talk reach deliver have choice group bridge event`, log page, dialogue, `/quests`, and **quests 1, 2, 3 (bridge), 5, 7, 9 with coins/XP/flag/plain-item rewards only** | **full** (new mod, saved data, items, new commands) | SkyyTowns 0.1 (P0: Mossby, Pebble, the square) | the line plays quest 1 to 3 and 5 at the real NPCs |
| **SkyyQuests 0.2** | the Job Board (page, seed, pool of 12, claims) + quests 4, 6, 8 once SkyyBazaar / SkyyGear / SkyyBank add their `quest:fn:event` call (each is a one-line change in a lean round) | **full** (several mods) | SkyyTowns 0.2 (Bank / Bazaar / Forge NPCs), the event calls | each NPC offers its quest; the board refreshes at the anchor |
| **SkyyQuests 0.3** | Set + UT rewards (`gear:fn:grant`, idempotent `grantId`), the owed claims paid retroactively | **full** (items that could be lost or duplicated) | the SkyyGear set + UT round (`research/cloud/Untiered-Mythic-Spec.md` G1/G2/S1) | the four pieces make the full-set buff; the UT arrives identified |
| **SkyyQuests 0.4** | `!` / `?` markers, tracker widget, map markers | lean | probes 3, 9, 10 | markers show |
| later | the in-game quest editor (Server Setup), Zone 2-4 lines | per `research/cloud/SkyyQuests-Spec.md` | | |

## 11. Engine probes for the local session (all UNVERIFIED)

| # | Probe | Pass |
|---|---|---|
| 1 | Town NPC Use (F) -> bridge call -> dialogue page opens on the next tick, with the SkyyMerchants pattern, for a Kweebec variant and for Pebble's model | the page opens once per press, no vanilla trade window |
| 2 | Pebble as an NPC: `Pebble/Pebble.blockymodel` loads as a role model; Idle/Talk animations play; nameplate on the `Head` node | Pebble stands and talks; else the `Rubble_Stone_Mossy` fallback |
| 3 | A talk hint key: is there a vanilla `server.interactionHints.*` key that reads "Press [F] to talk"? | the hint says talk, or we use our own string |
| 4 | `!` / `?` over the head: nameplate prefix vs a floating text vs a particle | one of them works per player |
| 5 | Two NPC systems: SkyyTowns and SkyyQuests both on `UseEntityEvent$Pre` - the cancelled-early return | confirms why SkyyTowns alone owns the Use hook |
| 6 | The 1 s position poll for `reach`, 20 players, 3 active reach objectives | under 0.5 ms per tick on the world thread |
| 7 | Moving one NPC between two registered spots (Pebble in quest 5) without a duplicate after a restart | one Pebble, always |
| 8 | Dialogue portrait via `ItemIcon` (the Pebble icon from `art/pebble/`) | icon shows, or text only |
| 9 | A stamp post as `reach` (no custom block); `WorldMapManager.addMarkerProvider` for the three stamp points | markers show for the quest owner only |
| 10 | `quest:fn:event` calls from SkyyBank, SkyyBazaar, SkyyGear: the Bazaar sell button, the Identify button | the event reaches the quest with the right count |
| 11 | The Earthen Golem (Lv 20, summit) kill reaches the quest as a boss kill by role id (`research/cloud/Zone-Bosses-Ideas.md`) | the objective completes on the kill |
| 12 | The daily anchor math across a server restart and a world change | same 3 jobs for a given profile and day |
| 13 | Copper pieces: `Armor_Copper_Head/Hands/Legs/Chest` document fields `set=copper_quest` survive a death, a Vault deposit and the Wardrobe | the Set check counts 4 of 4 |
| 14 | `ItemGridSlot` with a plain `ItemStack` of a Set piece shows in the reward preview (no metadata) | no client disconnect |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Pebble: the guide in **every** town (a different errand line each), or only Zone 1? (open since `research/cloud/Story-Script-Draft.md` question 1) | [every town] |
| 2 | The Zone 1 quest Set = vanilla **Copper armor** "Clerk's Copper", one piece from each of quests 3, 4, 7, 8, full-set buff +40 Health? | [yes; the +40 is a placeholder for the Gear -> Sets table] |
| 3 | The Job Board: 3 daily jobs, refresh at 00:00 UTC, no reroll, no streak, rewards 260 coins a day? | [yes] |
| 4 | The Hermit lives at Gorge Gate Post (outpost Z1-3)? | [yes] |
| 5 | Quest 9's UT: a **fixed** UT2 weapon of your class (the table in 2.3), or a **pick one of three** (your class's weapon, or the chest piece of a Heavy / Light / Cloth UT2 set)? | [fixed: your class's weapon] |
| 6 | Set piece level = the level of the quest that gives it (3, 5, 11, 14), or one fixed level (say 12) for all four? | [the quest's level - the Untiered-Mythic spec rule] |
| 7 | Should the town line be hidden from profiles that already killed the Zone 1 guardian? | [no - everyone starts at quest 1; quests are cheap] |
| 8 | Quest-earned Set and UT pieces: **tradable** (spec question 12 default) or **bound** to the earning profile? | [tradable, per question 12] |
| 9 | The Job Board as a separate sign beside the NOW SERVING board (not the same board)? | [yes, separate "Form 11-J"] |
| 10 | Quest coin and XP numbers (2,050 coins, 750 XP over the line): too little, fine, or too much? | [fine; tune with the two scale rows] |

## For the local session (everything UNVERIFIED needs Assets.zip / HytaleServer.jar)

| # | Item |
|---|---|
| 1 | The 14 probes of section 11, as one lean probe round on SkyyTownProbe 0.1 (npc + pebble are already there). |
| 2 | `gear:fn:grant` with a `grantId` and a `grants.log` in SkyyGear, and the `set` / `ut` fields (Untiered-Mythic-Spec section 6 item 7). Without them quests 3, 4, 7, 8, 9 pay coins/XP and keep the item owed. |
| 3 | A one-line `quest:fn:event` call in SkyyBank (`bank:deposit`), SkyyBazaar (`bazaar:sell`) and SkyyGear (`gear:identify`) at their next versions; or use the `bridge` objective for quest 3 only. |
| 4 | The exact vanilla role for Mossby (Kweebec) and the hermit (an Outlander/Feran-style role); the hint key for "talk"; confirm the ids `Armor_Copper_Head/Hands/Legs/Chest` in `Assets.zip` (they are used throughout the SkyyGear / Armory scripts). |
| 5 | The boss role id and level of the Zone 1 guardian ("Earthen Golem", Lv 20) and a `kill target=role:...` hook; the zone 1 mob role ids for the Board jobs. |
| 6 | SkyyTowns 0.1 must reserve the `quest=` key in `npcs.json` and call `quest:fn:hasoffer` / `quest:fn:talk` (the build plan, section 6, does not mention it yet). |
| 7 | A talk hint string and `Talk` animation on the Pebble role; the Pebble art is not tested in game (`ART-RESUME.md`). |
| 8 | After Skyy answers: add the answers to `docs/answered/`, then SkyyQuests 0.1 as a full round with `.claude/workflows/skywynn-round.js`, Skyy's own words in `quotes`. |
