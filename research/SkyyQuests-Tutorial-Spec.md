# SkyyQuests + the tutorial - build spec (engine, tutorial line, quest widget, markers, hub board)

Local spec, 2026-10-13 (Fable). Build-ready paper for the NEW mod **SkyyQuests** and the first content in it: the non-linear TUTORIAL.
It replaces the engine part of `research/cloud/SkyyQuests-Spec.md` (cloud, 2026-10-06, written without game files) and keeps
`research/cloud/SkyyQuests-Zone1-Spec.md` (the Zone 1 town line + Job Board) as content that runs on this engine later. Everything
marked VERIFIED was seen in game or in a live build script; UNVERIFIED items have a probe step in section 11. Nothing here is built.

## 0. Skyy's words (they win over everything below)

| Date / topic | Skyy, word for word (`docs/answered/`) | What it fixes here |
|---|---|---|
| 2026-10-12 QUEST WIDGET = ESSENTIAL (ui.md 92) | "but a quest widget is essential, we need a place to quickly and easily tell players what to do next without digging in menus." | an always-on HUD widget with the next 1-3 tasks; it never needs a menu (section 5) |
| 2026-10-12 TUTORIAL (social.md 55) | "you start on your island, pick a class, then we have have some suggestions to guide the player (probably built into the quest widget. no fairy needed (maybe add later.) but players will have a widget suggesting what to do. we can walk them trough basic things like making your first crafting accessory, some of the basics of how the island works, then lead them to build over to the next island where they get into some combat. then to the 3rd isalnd with a little mini boss, who drops a shard to activate the portal to the hub. (make a lost of things we should cover in the tutorial. and the biggest thing, not lock it linear if someone does task 6 before task 4 they dont have to redo 6 when they get there.)" | the tutorial lives in the widget, no fairy now; 3 islands; NON-LINEAR: every task completes the moment its condition is met, in any order (section 2.5) |
| 2026-10-11 QUEST MARKERS + GUIDE (social.md 54) | "We will also want quest markers in the game that appear on more than your map, and if we can id like a trail to follow, or a little guide fairy that always stays within a few blocks of you, in the direction of your quest so you can follow it. (This might be good as a pet function.)" | world markers (! / ? over NPCs), compass + map + minimap markers now; trail / fairy as later options, fairy maybe a pet (section 6) |
| 2026-10-12 STARTER ISLANDS (social.md 56) | "fixed design, but everything there is breakable. so it guides you through the start, but wont restrict you. i want the 3 islands to be big enough to break some bushes, grab some rubble, make crude tools, mine for some blocks, and get to the next island. (old broken structures on the islands.) but still small islands, maybe 4x-5x the starter one we have no" | the islands are SkyyIslands' job (section 3.3); SkyyQuests only reads where you are; nothing is protected |
| 2026-10-12 LIFELONG TOOLS (gear.md, via Gathering-Shards-Spec 3.1) | you spawn with a hatchet, pickaxe, hoe and sickle; the fishing pole comes from a hub quest | tutorial task 5 reads "take your tools from the chest"; the hub FISHING quest hands the pole (section 7.3) |
| 2026-10-11 QUESTLINES SUITE (project.md 53) | "and these questline mods might help us make ours better." + PROJECT-RULES 2 "before making a mod, check if one already exists that does what we want. if it does, include it. if its still better to make our own, learn from how the other was made" | section 1 |
| 2026-09-25 LOCKED (project.md 22) | "quest hooks ship with SkyyQuests, not now" | the one-line `quest:fn:event` calls in other mods come in THIS round's companion bumps (section 4.3) |

Also followed (not re-decided): `research/Tutorial-Plan.md` (the 24 tasks + 23b), `research/cloud/ui-mockups-1013/Layout-Spec.md`
section 2 + 7 (widget look, `quest:fn:hud`, `feed:fn:push`), approved 2026-10-13 (log: "quest widget (5 states)" APPROVED);
`tools/PROFILES-CONTRACT.md`; `tools/CONFIG-CONTRACT.md`; `research/Code-Structure-Audit.md` (no per-tick work for idle players,
private writer thread, lock-free bridge); HANDOFF section 2 (UI) + 3 (commands).

## 1. Existing mods first (PROJECT-RULES 2)

Surveyed: `research/Mod-Database.md` (306 installed, 44 tagged "quest" - the tag is a string hit, most are not quest mods), Skyy's Mods
folder (read-only), `research/Mods-Folder-Survey.md`, `research/cloud/Mod-Survey-0.7.md`. `python tools/mod_check.py quest` finds no
CurseForge page by that slug and no installed file named quest.

| Mod | Licence | What it does | Verdict for SkyyQuests |
|---|---|---|---|
| **QuestLines suite** (Core = dialogue / quests / requirements / actions, Icons, Dialog builder, Denizens NPCs, Hooks, MMO, ...) | **ARR** | dialogue trees + quests on any NPC, branching, multi-stage boss fights (`Mod-Survey-0.7.md` 143) | **NOT installed in Skyy's Mods folder** - cannot be studied from files here (UNVERIFIED; probe U1 = Skyy installs it once for a read-only look, or the cloud reads its CurseForge pages). ARR = no code, no data copied; pack by id only if ever used. What we take from its page: the SHAPE - quests are data (requirements + actions), NPC dialogue is a tree with choices, markers are a separate "Icons" add-on. Our data format (section 2.2) keeps that split. |
| Aetherhaven 3.2.1 (Hexvane) | ARR, <0.7 | whole town game with a quest board + story quests | design reference only (`Mods-Folder-Survey.md` 82-90): a BOARD with daily jobs, shops / NPCs with schedules. Not in the pack (own economy, 0.7 cap). |
| Hexvane Pathfinder | CC BY 4.0 | biome-finder MAP MARKERS | idea reused: server-side `WorldMapManager` marker providers (we already proved our own: TownProbe #9) |
| ZiggfreedCommon 2.2.0 (`Ziggfreed_Objective_Book`) + MMOSkillBountyPack (`MMO_Bounty_Board*`) | ARR (CurseForge) | an objective-book item, bounty boards (bi-hourly / weekly) | learn: a BOARD as a placed item with a page; we build ours as an NPC board (TownProbe-proven Use route) |
| Beacon 2.0.3, Ping-Point 1.0.0, x3Dev Wayfinder 1.8.0 | ARR / ARR / ARR (broken on 0.6.8+) | beacons, a ping-point UI, a 40x40 colour-cell minimap | nothing to reuse by code; Ping-Point confirms "a marker the player sets" is wanted later (/quests ping idea, section 6.5) |
| starter_kit 1.0.0 | - | one class: a starter kit | duplicate of SkyyIslands `starter.kit` - keep ours (no-duplicates rule) |
| Perfect Parries 0.9.6 (pack mod), Perfect Dodges 0.5.16 | ARR | parry / dodge mechanics | the tutorial's "perfect parry" / "dodge roll" tasks need a way to SEE them (UNVERIFIED, probe U4) |
| **Our own probes (VERIFIED in game 2026-10-10, TownProbe 0.2 Q0, all 17 PASS)** | ours | NPC Use -> bridge -> page next tick; floating ! / ??? nameplate markers; "Press [F] to talk" lang key; map marker provider per player; 1 s reach poll 10 us avg; claim ledger; boss kill by role id; Pebble art as an NPC; daily board seed | **REUSE ALL OF IT** - the SkyyQuests 0.1 code is the TownProbe 0.2 patterns made permanent (section 2.1) |
| SkyyMerchants 0.1.3 (ours) | ours | NPC spawn / registry / orphan removal / Use hook | the NPC kit for the board + fishing NPCs (section 7) |
| SkyyHud 0.3.19 minimap (ours) | ours | reads the engine's `MapMarker` stream, draws marker dots by `markerImage` kind | our quest markers appear on it for free once they are real map markers (section 6.3) |

Decision: **build our own** (nothing installed does data-driven quests on 0.7 with per-profile state, our bridge and our HUD), reusing
our probe-proven code. What we learned from QuestLines / Aetherhaven is written into the data shape and the board.

## 2. The quest engine

### 2.1 What SkyyQuests is

One small standalone mod (zero dependencies, like every Skyy mod): quest DEFINITIONS are data files; it watches a few engine events and a
few bridge events; keeps PER-PROFILE progress; pays each reward ONCE; feeds the HUD widget, the markers and a quest log page; owns its
own NPCs (board, fishing NPC) and answers town NPCs through the bridge. Code it carries forward from `SkyyTownProbe/build_skyytownprobe_0.2.py`
(VERIFIED): the Use-hook system (TpUseSys), the dialogue page (`TpDialog*`, kit pages), the marker modes (nameplate prefix / floating
nameplate prop / emote particles), the map marker provider, the reach poll, the claim ledger (TpClaims), the daily board seed, the
NPC spawn + registry (`SkyyMerchants` MerchReg pattern). `tools/skyynpc.py` (planned in `Server-Setup-Spec.md` 5.3) = that NPC code
as a generator so the board, fishing NPC and later shop NPCs share one copy.

### 2.2 Data: quest definitions (files, not code)

`Skyy_SkyyQuests/quests/<line>.properties` - ONE file per quest LINE (the tutorial is one line, Zone 1 town is one, the hub fishing
quest is one), plain `key=value` in the project's own style (no JSON dependency). Shipped defaults sit in the jar and are copied once;
an owner's edits survive (the SkyyMerchants / Islands "copy once" rule). Grammar:

```
line=tutorial                      # id, [a-z][a-z0-9_]*
name=Getting Started               # widget header
mode=open                          # open = every task live at once (NON-LINEAR, the tutorial); chain = one task after another
hide.setting=tutorial.hide         # a player Settings switch that hides this line's tasks from the widget (rewards still paid)
task.1.id=pick_class
task.1.name=Pick a class
task.1.where=                      # optional: a named place (section 5.4) or an NPC id
task.1.type=bridge                 # objective type (2.3)
task.1.key=profile:class
task.1.count=1
task.1.hint=Open the Profiles page and pick a class.
task.1.reward=coins:25,xp:Combat:20
task.1.needs=                      # optional hard requirement (task ids) - only for REAL physical needs
...
```

Per-task fields: `id name where type key|item|block|role|skill|coll|place|npc|page (one per type) count hint reward needs any (a|b|c)`.
Rewards: `coins:N`, `xp:<Skill>:N`, `item:<id>:N`, `gear:<id>:<level>` (a rolled SkyyGear item), `flag:<name>`, `title:<id>`.
`/questadmin reload` re-reads files; `/questadmin check` prints every bad line. Text goes through our own `server.lang` keys later
(the `quests.lang` idea); 0.1 inlines the English.

### 2.3 Objective types and exactly what feeds them

Counting is EVENT-DRIVEN. Every event handler starts with one `ConcurrentHashMap` read: `want.get(uuid)` = a small bit-set of objective
types this player has ACTIVE and UNDONE (rebuilt when progress changes, at join and at a profile switch). No bit set = return at once.
Players with nothing to count cost one map read per event and nothing per tick.

| Type | Completes when | Counted from (VERIFIED = used by a live script today) | Notes |
|---|---|---|---|
| `break` | N blocks of `block` (id or `Group:*` prefix) broken by the player | engine `BreakBlockEvent` (ECS, on the player; used by SkyySkills 0.4.32, SkyyCollections 0.2.10, SkyyIslands 0.5.7 - VERIFIED) | player-placed blocks: Skills' `skill:fn:placed` (key VERIFIED in SkyySkills 0.4.32 - its PlacedStore; the `apply` shape is UNVERIFIED, read it in the build round) answers "placed by a player" - ask it only when the objective says `natural=true` |
| `felled` | N logs felled | `skill:on:felled` registry map (SkyySkills 0.4.32 calls every registered Function on a tree fall; SkyyTrees registers "trees" with `putIfAbsent` - VERIFIED) -> SkyyQuests registers "quests" | task 3 "Chop 10 logs" = `felled` OR `break Wood_*_Log` (`any`) |
| `gather` | N of `item` OBTAINED (picked up / harvested) | `InteractivelyPickupItemEvent` (ECS; SkyyCollections / Islands / Skills use it - VERIFIED) + the Collections "obtained" rule later through `quest:fn:event` `collect` (one line in SkyyCollections' `coll:fn:add` path, section 4.3) | bag withdrawals / `/give` never count (they are not pickups) |
| `craft` | N of `item` crafted | `CraftRecipeEvent$Post` (ECS; SkyyGear + SkyySkills use `CraftRecipeEvent` - VERIFIED) + `quest:fn:event` `craft` from SkyySacks' bag crafting (`sacks:fn:craftCommit`) | `item=Group:Accessory_Bench_*` style prefixes allowed |
| `kill` | N NPCs of `role` (id, prefix, `any`, `boss`) killed by the player | our own `DeathSystems$OnDeathSystem` subclass on `DeathComponent` whose `getDeathInfo().getSource()` is a `Damage.EntitySource` resolving to the player (SkyySkills 0.4.32 Combat path + TownProbe #11 PASS by role id `Golem_Crystal_Earth` - VERIFIED) | level from `mob:fn:info` {world, npcUUID} -> Object[]{level,...} (SkyyMobs 0.1.6, answers at the DeathComponent - VERIFIED); `minLevel` optional; pet kills credit the owner (SkyySkills' pet rule, later) |
| `reach` | the player stands within `radius` of `place` (world + x,y,z, or a named place, section 5.4) | 1 s poll on the player's world thread, ONLY for players with an active `reach` (TownProbe #6: 20 players x 3 objectives = 10 us avg / 29 us max - VERIFIED) | one `world.execute` per world per second, only for worlds that hold such a player |
| `enter` | the player's world changes to `world` (`hub`, `island:own`, `island:2`, `island:3`, a zone world) | `PlayerReadyEvent` (fires on every world switch - AGENT-BRIEF) + `AddPlayerToWorldEvent` (SkyyExploration - VERIFIED); world names from `island:hubWorld` (SkyyIslands bridge key - VERIFIED exists) and the island world naming `skyy-island-<key>[-rN]` | no polling |
| `talk` | the player used (F) NPC `npc` | our own `UseEntityEvent$Pre` system for OUR NPCs (SkyyMerchants / TownProbe #1 - VERIFIED, one page per press); town NPCs owned by SkyyTowns call `quest:fn:hasoffer` / `quest:fn:talk` (Zone1 spec 4; TownProbe #5 proved ONE mod must own an NPC's Use hook) | |
| `page` | the player opened page / ran command `page` (`collections`, `pd`, `requip`, `bank`, `bazaar`, `auction`, `party`, `skills`, `pets`, `anvil`) | `quest:fn:event` type `page` - ONE call in SkyyMenu's tile runner (MenuPage runs the tile's command after `hasPermission` - every hub button goes through it) + one call in each owning command (`/collections`, `/pd`, `/bank` ...) for players who type it | SkyyMenu 0.3.20 + the owners' next versions (section 4.3). Until a caller exists the task shows "(soon)" and never blocks |
| `event` | `quest:fn:event` with `key` reaches `count` | the shared hook (section 4.2): `bank:deposit`, `bazaar:sell`, `bazaar:buy`, `gear:identify`, `gear:reforge`, `gear:upgrade`, `requip:save`, `sacks:deposit`, `sacks:take`, `explore:luggage`, `pets:equip`, `class:ability`, `class:pick`, `fishing:catch`, `island:portal`, `island:bridge`, `party:open`, `party:invite`, `combat:parry`, `combat:dodge`, `food:eat` | each is a one-line call in the owning mod next to a hook it already has |
| `tier` | collection `coll` reaches `tier` | lazy: when `coll:epoch:<uuid>` (Long, SkyyCollections 0.2.10 - VERIFIED key) changes, ask `coll:fn:tier` (Function - VERIFIED exists; its `apply` shape is `{UUID, collId}` -> Integer in SkyySacks' reading, UNVERIFIED exact, probe U6) | epoch checked on our 5 s profile tick for players with a `tier` objective only |
| `level` | `skill` reaches `level` | `skill:fn:level` apply(Object[]{UUID, String skill}) -> Integer (SkyySkills 0.4.32 - VERIFIED shape); triggered by `quest:fn:event` `level` from SkyySkills' level-up line (one line) or, until then, the 5 s tick for players with a `level` objective | `Overall` via `skill:fn:overall` apply(UUID) -> Object[]{Integer level, ...} (VERIFIED) |
| `bridge` | a bridge VALUE meets a test: `key` `op` `n` | read on the 5 s tick for players with such an objective: `profile:class:<uuid>` (String, exists = class picked), `bank:<uuid>` (Long - VERIFIED key), `coins:fn:get` apply(UUID) -> Long, `pets:fn:loadoutGet` apply(UUID) -> "petId|summonId" (VERIFIED), `acc:has:<uuid>` (bench accessory ids - VERIFIED) | the fallback for everything that has no event yet |
| `any` | one of `a|b|c` sub-objectives done | composition | task 13's three parts |
| `all` | every sub-objective done | composition | |

Progress for `break / gather / craft / kill / event` is a counter; the rest are booleans. `count` defaults to 1.

### 2.4 Per-profile state (`tools/PROFILES-CONTRACT.md`)

- File `Skyy_SkyyQuests/players/<pkey>.properties`, key = `pkey(u)` (the contract's helper, `profile:fn:key`), never `u.toString()`.
- In-memory cache keyed by the pkey STRING; first `profile:epoch:<uuid>` seen = baseline; a later different value = flush under the old
  key, re-resolve, republish `quest:*` UUID-keyed values, rebuild `want`. No counting while `profile:busy:<uuid>` is present.
- Lines: `v=1`, `done.<line>.<task>=<epochMs>`, `prog.<line>.<task>=<n>`, `flag.<name>=1`, `claim.<n>=<type>|<payload>|<grantId>`,
  `issued=<grantId>` (never removed), `hide.<line>=1` (the "I know how to play" choice is ALSO a Settings switch - the file line is the
  cache), `seen.<line>=1` (the first-time welcome shown).
- Writes: a dirty set + ONE private single-thread writer ("SkyyQuestsIO"): tmp + fsync + atomic move, debounced 1 s, flushed at
  `PlayerDisconnectEvent` and shutdown. NEVER a file write or a sleep-retry on a world thread (audit finding 3 / 9).
- Without SkyyProfiles everything is profile 1 (= `uuid.toString()`), per the contract.

### 2.5 The NON-LINEAR rule (Skyy's "biggest thing")

- A line with `mode=open` has EVERY task live from the first join. Each task completes the moment its condition is met, in ANY order,
  whether or not the widget is showing it. Task 6 done before task 4 stays done.
- `bridge` / `tier` / `level` tasks are also checked at JOIN and at a profile switch, so a task whose condition was met before the mod
  existed (an old profile with a class, coins in the Bank) ticks at once - rewards paid once, like any other.
- `needs=` is only for REAL physical needs: the Hub portal needs the Hub Shard (that is enforced by SkyyIslands' portal, not by us);
  SkyyQuests never hides or blocks a task because an earlier one is undone.
- Widget order = file order; it shows the first 1-3 UNDONE tasks (player setting "Tasks shown" 1 / 2 / 3, default 3).
- "I know how to play" (Settings > Quests, and a button on the widget's first-time welcome page): sets `tutorial.hide` ON -> the
  tutorial tasks leave the widget; they keep ticking quietly and rewards are still paid (`Tutorial-Plan.md`). Switching it OFF brings the
  undone ones back. The widget itself stays for quests.

### 2.6 Rewards once (dupe-proof)

TownProbe #17 PASS (claim ledger 4/4, fix round) is the model:
1. Done + every reward of the task become `claim.` lines in ONE atomic write (`done` first, then claims, same file, same write).
2. Paying a claim: remove its line FIRST (write), then pay (coins `coins:fn:add` {UUID, Long} -> Long; XP `skill:fn:addxp`
   {UUID, skill, Number, "quests"} -> Boolean; items storage-first with a count before / after; `gear:` through SkyyGear's roll /
   grant bridge with the `grantId`); log `PAID` / `LOST?`. At-most-once: a rare lost payout beats a duplicate; `/questadmin repay` re-pays
   logged losses.
3. An item claim whose `grantId` is already on an item in the player's inventory / bags / Vault / Requip (TownProbe #13 proved the
   metadata survives death, Vault, Wardrobe) is dropped without a second item. `issued=` lines make a task NEVER issue twice.
4. A full inventory keeps the claim: the widget "where" line says "Reward waiting - /quests claim"; never dropped on the ground.
5. The reward is paid even when the line is hidden (Tutorial-Plan).

## 3. The TUTORIAL line (`quests/tutorial.properties`, `mode=open`)

Rewards are placeholders: small, "coins / skill XP / a starter item" (Tutorial-Plan); every number is a Server Setup table cell
(`tutorial.rewards`, section 8). Total below: 1,200 coins + 1,180 skill XP + 4 items. `where` names come from section 5.4.

| # | Task (widget name) | Type -> counted from (2.3) | Reward | Where / hint |
|---|---|---|---|---|
| 1 | Pick a class | `bridge profile:class exists` (SkyyProfiles writes it at creation; `class:fn:kitnew` is the moment - SkyyClasses may send `class:pick` as the event) | 25 coins | "Profiles page - your weapon + first ability" |
| 2 | Open the hub buttons | `page hub` (SkyyMenu's hub hotkey / hub icon panel on 0.7 - `research/Inventory-Offhand-0.7.md`) | 25 coins | "Press the hub key" |
| 3 | Chop 10 logs | `any(felled 10, break Wood_*_Log 10)` | 50 Foraging XP | "Trees are behind you" (island 1 grove) |
| 4 | Craft your first crafting accessory and equip it | `all(craft Group:<bench accessory ids> 1, bridge acc:has:<uuid> contains a bench id)` (the ids = SkyyAccessories `acc:defs`) | 50 coins, 40 Smithing XP | "Workbench on the island" |
| 5 | Take your tools and mine stone + copper | `all(bridge gear lifelong 4/4 (gear:fn:lifelong, section 4.3; until it exists: gather Tool_Pickaxe_Crude 1), break Rock_Stone 10, break Ore_Copper 5)` (block ids per Assets.zip, build-checked) | 50 Mining XP | "Starter chest; the cave on island 1" |
| 6 | See your first collection rank-up | `all(tier <any coll> 1 - lazy via coll:epoch, page collections)` | 25 coins | "Collections page" |
| 7 | Farm: till, plant, water, harvest | `all(break Crop_Wheat* 3 (harvest), gather Food_Wheat 3)`; till / water need `UseBlockEvent` on soil + water-can (UNVERIFIED probe U5) - 0.1 counts harvest only | 50 Farming XP | the starter plot |
| 8 | Put items in your SkyyVoid bag and take them out | `all(event sacks:deposit 1, event sacks:take 1)` (SkyySacks 0.8.0 = SkyyVoid, `research/Bags-v2-Spec.md`) | 25 coins | "/pd" |
| 9 | Save a Requip loadout | `event requip:save 1` (SkyyWardrobe 0.2.x) | 25 coins | "/requip" |
| 10 | Deposit coins in the Bank | `bridge bank:<uuid> >= 50` (VERIFIED key) or `event bank:deposit` | 50 coins (yes, it pays more than it asks: the point is the habit) | "Bank page" |
| 11 | Bridge to island 2 | `enter island:2` (the island-2 world or region, section 3.3) | 50 Exploration XP | ARROW + distance to island 2's landing (section 5.3) |
| 12 | Equip your class weapon and use ability 1 | `all(bridge class:fn:loadoutGet has a weapon, event class:ability 1)` (SkyyClasses 0.1.19 `class:fn:abil` / `/cast`) | 25 coins | "Hold your weapon; press ability 1" |
| 13 | Defeat 5 mobs (+ dodge, + perfect parry) | `kill any 5` + optional `event combat:dodge`, `event combat:parry` (UNVERIFIED probe U4; shipped as `any` so the kill alone completes it until they exist) | 50 Combat XP | island 2 camp |
| 14 | Identify an unidentified drop | `event gear:identify 1` (SkyyGear Anvil / Identify tab) | 25 coins | "Anvil: Identify" |
| 15 | Reforge or upgrade one item | `any(event gear:reforge, event gear:upgrade)` | 25 coins | "Anvil" |
| 16 | Eat food / heal up | `event food:eat 1` (UNVERIFIED probe U5: `InteractionChainStartEvent` of a consumable, or SkyyCooking's hook) - fallback `bridge` Health rose from <50% to full (world-thread read on the reach poll) | 25 coins | hint text carries the death-cost note |
| 17 | Hatch / equip your first pet | `bridge pets:fn:loadoutGet != null` or `event pets:equip` | 25 coins | "/pets" (hidden when SkyyPets is absent) |
| 18 | Open Unclaimed Luggage | `event explore:luggage 1` (SkyyExploration 0.2.7 LgEng claim) | 50 Exploration XP | island 2 |
| 19 | Bridge to island 3 | `enter island:3` | 50 Exploration XP | ARROW to island 3 |
| 20 | Defeat the mini boss | `kill role:<miniboss> 1` (role id = Skyy's pick, section 12 Q3; placeholder `Golem_Crystal_Earth` - TownProbe #11 VERIFIED) | 100 coins, 100 Combat XP, item Hub Shard is the BOSS's drop (SkyyIslands / SkyyMobs), not ours | island 3 summit |
| 21 | Place the shard in the portal -> travel to the hub | `all(event island:portal 1, enter hub)` | 100 coins | ARROW to the portal |
| 22 | Visit the Bazaar, Auction House, Bank NPC and quest board | `all(any(event bazaar:buy, event bazaar:sell), page auction, page bank, talk board)` | 100 coins, 100 Exploration XP | hub markers (section 6) |
| 23 | Party intro (open the party menu; invite a friend - optional) | `page party` (the invite is hint text only) | 25 coins | "/party" |
| 23b | Fishing: the hub fishing quest | `talk fisher` -> its own line `fishing_intro` (section 7.3): catch 1 fish | the lifelong Crude Fishing Pole + reel (the line's reward) | hub pier NPC |
| 24 | Your first shard | `event island:shard 1` (Gathering-Shards-Spec phase 2; hidden until SkyyIslands publishes `island:fn:shards`) | item Farming Shard (`research/Gathering-Shards-Spec.md` 3.1 step 4) | "/island" |

Notes: tasks 8, 9, 17, 24 depend on mods not yet at the needed version - the loader HIDES a task whose source mod is absent (bridge key
missing) and shows it the moment the key appears (zero-dependency rule). Order in the widget = this order; Skyy trims / reorders by
editing the file or the Server Setup table.

### 3.1 First join flow
PlayerReadyEvent in the player's OWN island world + `seen.tutorial` absent -> a one-time welcome page (kit, inline): "Welcome to
SkyWynn" + the first 3 tasks + buttons **Show me** (default) / **I know how to play** (sets `tutorial.hide`). Never on a world switch
(`seen` line written first). Co-op joiners (another player's island) get the same page; their tasks count in that world too
(Tutorial-Plan "tutorial for joining an existing island" stays OPEN - Q7).

### 3.2 Chat + feed lines
Task done: ONE chat line "Task done: Chop 10 logs (+50 Foraging XP)" routed by `settings:fn:route` type `quest` (Layout-Spec: Quest
progress default Feed; done lines Chat) - never a toast per count. Progress ("Chop logs 7/10") goes to the FEED card key `quest:<task>`
(merges). The widget itself shows the live count, so a player with the feed off loses nothing.

### 3.3 What SkyyIslands must provide (not SkyyQuests' job; `research/Island-Settings-Spec.md` / the islands round)
The 3 fixed starter islands (Skyy: 4-5x today's, nothing protected, old broken structures) as ONE prefab set; a cave with stone + copper;
a starter plot; island 2 with a mob camp + an Unclaimed Luggage; island 3 with the mini-boss spawn and the portal frame; the Hub Shard
drop + the portal "use" (`island:portal` event); the named places (section 5.4) published as `island:fn:place` {UUID, "island2"} ->
"world|x|y|z" so the widget arrow has targets. Until the big islands exist, the current starter island counts as island 1-3 (tasks
11 / 19 use a `reach` on two marked spots the admin sets with `/questadmin place set island2`).

## 4. Bridge contract (plain `java.lang` types; the lock-free `bridge()` form SkyyIslands / Hud use - audit quick win 1)

### 4.1 Published by SkyyQuests (in `setup()`, never removed)
| Key | Shape | Reader |
|---|---|---|
| `quest:fn:hud` | apply(UUID) -> Object[] {String title, String count ("3 / 24"), then per shown task: String name, String progress ("6/10" or ""), Double frac or null, String where, Integer dir 0-7 or -1, Boolean done} (Layout-Spec 7, EXACTLY) | SkyyHud Quest widget |
| `quest:epoch:<uuid>` | Long, +1 on every change that alters the widget (progress, done, hide, tracked line) | SkyyHud: skips the call when unchanged |
| `quest:fn:event` | apply(Object[]{UUID player, String type, String key, Number amount [, String world]}) -> Boolean (accepted) - the `Server-Setup-Spec.md` 5.3 shape, types = section 2.3 | every mod with a hook |
| `quest:fn:hasoffer` / `quest:fn:talk` | apply(Object[]{UUID, String npcId}) -> Boolean (Zone1 spec 4; TownProbe #1 proved the shape) | SkyyTowns |
| `quest:fn:flag` / `quest:fn:done` | apply(Object[]{UUID, String}) -> Boolean | SkyyIslands (portal / zone unlocks), SkyyMenu tile `unlock` rules (0.3.16 TILE_RULES take a bridge key - VERIFIED) |
| `quest:fn:markers` | apply(Object[]{UUID, String world}) -> Object[] of Object[]{String id, String kind "!"/"?"/"place", Double x, y, z, String label} | SkyyHud (compass bar / minimap extras), later the trail / fairy |
| `quest:fn:start` | apply(Object[]{UUID, String lineId}) -> Boolean | NPCs, events, dungeons |
| `config:def/fn/epoch:SkyyQuests`, `settings:def:*` | the config kit + player settings registry | SkyyMenu |

### 4.2 Read by SkyyQuests (all exist today unless marked)
`profile:fn:key`, `profile:epoch:<uuid>`, `profile:busy:<uuid>`, `profile:class:<uuid>` (SkyyProfiles 0.1.11); `skill:fn:level`,
`skill:fn:overall`, `skill:fn:addxp`, `skill:fn:placed`, `skill:on:felled` (SkyySkills 0.4.32); `coll:fn:tier`, `coll:epoch:<uuid>`
(SkyyCollections 0.2.10); `coins:fn:add` / `coins:fn:get` (SkyyCoins 0.1.6); `bank:<uuid>` (SkyyBank 0.1.9); `pets:fn:loadoutGet`
(SkyyPets 0.2.3); `acc:has:<uuid>`, `acc:defs` (SkyyAccessories 0.5.12); `class:fn:loadoutGet`, `class:fn:get` (SkyyClasses 0.1.19);
`mob:fn:info` (SkyyMobs 0.1.6); `island:hubWorld`, `island:owner:fn` (SkyyIslands 0.5.7); `settings:fn:register/get/set`,
`settings:fn:route` (SkyyMenu 0.3.19 / 0.3.20); `feed:fn:push` (SkyyHud 0.3.20, Layout-Spec 7 shape); `gear:fn:box` / the grant
bridge (SkyyGear 0.2.25; `gear:fn:grant` with `grantId` = NEW, section 4.3).

### 4.3 One-line companion calls (each a lean bump at the owner's next version; `notifyOn`-style cached lookup, one map read when
SkyyQuests is absent)
| Mod | Call | Where in its code |
|---|---|---|
| SkyyMenu | `page <tile>` | the tile runner after `hasPermission`; `hub` on the hub hotkey |
| SkyyBank | `bank:deposit` n | `BankStore.deposit` success path |
| SkyyBazaar | `bazaar:buy` / `bazaar:sell` n | the order fill |
| SkyyGear | `gear:identify` / `gear:reforge` / `gear:upgrade`; NEW `gear:fn:grant` {UUID, id, level, rarity, pool, String grantId} -> Boolean + `gear:fn:lifelong` apply(UUID) -> Integer kinds held | Anvil tabs; the grant = Untiered-Mythic-Spec 6.7 |
| SkyyWardrobe | `requip:save` | loadout save |
| SkyySacks | `sacks:deposit` / `sacks:take` / `craft` | pool moves + `craftCommit` |
| SkyyExploration | `explore:luggage` | LgEng claim |
| SkyyPets | `pets:equip` | loadout set |
| SkyyClasses | `class:pick`, `class:ability` | kitnew; `/cast` success |
| SkyyFishing | `fishing:catch` item | the catch path |
| SkyyIslands | `island:portal`, `island:bridge` (first block placed in the gap region), `island:shard`; `island:fn:place` | portal use; `PlaceBlockEvent` it already has |
| SkyyParty | `party:open`, `party:invite` | page open, invite send |
| SkyySkills | `level` skill n (on SKILL LEVEL UP), `collect` later | the level-up line |
| SkyyCollections | `collect` item n | `coll:fn:add` accept path |
Order of deploy: SkyyQuests 0.1 first (it ignores missing callers), companions after - no floor either way.

## 5. The QUEST WIDGET (drawn by SkyyHud, data from SkyyQuests)

### 5.1 Look (approved mockup `research/cloud/ui-mockups-1013/a_quest_*`, Layout-Spec section 2 - repeated only where the build needs it)
300 wide; height 149 / 124 / 99 for 3 / 2 / 1 tasks; default spot tl 8,42 (under Coords; Party / Guild move to tl 8,200 / 8,324 in
SkyyHud's built-in defaults, saved layouts never move); SkyyHud box `#0b1524(0.72)` + gold hairline; padding 10; header = gold diamond +
line name Bold 13 `#E8A93B` + "3 / 24" right; task 1 = diamond + name Bold 14 + "6/10" + a 6 px vanilla ProgressBar + the WHERE line
(`#7caacc`): 8-way arrow picture + "NE  42 m  -  Island 2"; tasks 2-3 hollow diamond 13 `#96a9be`. Kit colours / textures from
`tools/skyyui.py` (add the 8 arrow pictures + the diamond to the kit, `SUI.verify`).

### 5.2 The 5 states
| # | State | Trigger |
|---|---|---|
| 1 | Default | next 1-3 undone tasks of the TRACKED line (tutorial by default; `/quests track <line>` or the log page changes it) |
| 2 | Task done | tick + green for 2.5 s with "Done!  +25 coins  +40 Foraging XP", then the list moves up (SkyyQuests publishes `done=TRUE` for that task and bumps the epoch again 2.5 s later from its own thread) |
| 3 | Quest (not tutorial) | same layout, the line's name in the header |
| 4 | Compact | player setting `quests.tasksShown` = 1 / 2 / 3 |
| 5 | Nothing to do | "No active quests" + "Pick one at the quest board in the hub"; player setting `quests.hideEmpty` ON by default (Layout-Spec Q8 default = hide) |

### 5.3 Refresh and direction (no polling for idle players)
- SkyyHud's TickTask (1 s, its OWN thread since 0.3.19) reads `quest:epoch:<uuid>`; unchanged = nothing. Changed = `quest:fn:hud`
  (a pure memory read in SkyyQuests, never a file) -> shape unchanged = set texts + bar Value only; shape changed (done / count /
  task-count) = the shape re-send, at most once per 1.5 s (the 0.3.8 rule).
- Direction + distance: SkyyQuests computes them on ITS side only for players whose shown task 1 has a `where` target, from the
  position it already reads for the reach poll (same 1 s world hop, same players) or, when no reach objective is active, from a cheap
  position read it adds to the hop for that player only. North-up 8-way: `dir = round(atan2(dx, -dz) / 45 deg) mod 8`, distance
  rounded to 1 below 100 and to 10 above; the result changes the epoch only when the shown text changes (so standing still costs
  nothing). Different world than the target = text only "Island 2" (no arrow, dir -1).
- Hidden widget / player offline / no SkyyHud: SkyyQuests still counts; the chat / feed lines carry the progress.

### 5.4 Named places (`Skyy_SkyyQuests/places.properties`)
`<id>=<world>|<x>|<y>|<z>|<label>` - `island2`, `island3`, `portal`, `hub`, `hub.board`, `hub.fisher`, `hub.bank`, `hub.bazaar`,
`hub.auction`. For island worlds the x/y/z are RELATIVE to the island's origin (the fixed design is the same for everyone), resolved
through `island:fn:place` when SkyyIslands publishes it, else from this file with world `island:own`. `/questadmin place set <id>`
writes the admin's spot. The hub places are set once in the hub world.

### 5.5 Quest log page (`/quests`; SkyyMenu social-bar tile "Quests", 0.3.16 free slot - VERIFIED the slot plan)
Kit page (Sky Window), inline, no underscores, BIG text: left = lines (Tutorial, Fishing, Zone 1 town ...) with "12 / 24"; right = every
task of the picked line (done = green tick, undone = diamond, hidden = grey), reward preview (`ItemGridSlot(new ItemStack(id, qty))`
only - never a metadata stack), buttons **Track**, **Claim** (when a reward waits), **Hide tutorial** / **Show tutorial**, footer Close.
No periodic refresh; click handlers may rebuild. The "Loading..." page guard (SkyyBank / SkyyMenu pattern).

## 6. World MARKERS (Skyy: "markers in the game that appear on more than your map")

| Marker | How (VERIFIED where marked) | Round |
|---|---|---|
| **! / ? over quest NPCs** | TownProbe #4 PASS: floating "!" / "???" NAMEPLATE PROP over the NPC (mode 2: a tiny intangible prop with a Nameplate, undo-recorded) is what Skyy saw; mode 1 (nameplate prefix) also showed. PER PLAYER is the catch: a nameplate is the same for everyone (UNVERIFIED U2: a per-player prop = spawn / hide per viewer, or the emote particle route mode 3 `ParticleUtil` with a player list - sent every 3 s only to players within 24 blocks who have an offer: an event-driven "you came near" check on the reach hop, no per-tick work) | 0.2 |
| **Map markers** | `WorldMapManager.addMarkerProvider(key, provider)`; `update(World, Player, MarkersCollector)` is called by the ENGINE per player, so markers are per player by construction (TownProbe #9 PASS: owner only). RULE from the probe log: "the probe re-sent map markers 8077x in ~25 min - the real mod must send markers once / on change" -> the provider answers from a per-player cached list rebuilt only when `quest:epoch` changes. `withCustomName` for the label; `markerImage` kind picked from the vanilla set the HUD already classifies (waypoint = gold) | 0.2 |
| **Compass bar** | the VANILLA compass shows map markers (`research/Minimap-Research.md` 238 "the native compass already shows map markers") -> the map markers above appear on the compass for free (UNVERIFIED U3 that quest-kind markers do; the TownProbe stamps were on the map, nobody looked at the compass) | 0.2 |
| **Minimap dots** | SkyyHud 0.3.19 already draws the engine's `MapMarker` stream as dots by `markerImage` kind (VERIFIED) -> free; add a "quest" kind colour (gold diamond) to its kind table | SkyyHud bump |
| **The widget arrow** | section 5.3 | 0.1 |
| **Trail** (later option) | a line of particles from the player toward the target, sent to that player only every 2 s while they MOVE toward a `where` target farther than 8 m (`ParticleUtil` with a player list - the TownProbe mode-3 route) | 0.4 |
| **Guide fairy** (later option; Skyy: "maybe add later", "might be good as a pet function") | a SkyyPets flying pet (the proven fly-follow of SkyyPets 0.2: "hawk flies around me") whose follow target is offset 4 blocks from the player toward the quest target, read from `quest:fn:markers` - a PET ability, not a SkyyQuests entity | SkyyPets 0.4 / pets spec |
| **/quests ping** (idea) | the player drops a personal map marker (Ping-Point's idea) | later |

## 7. Hub quest board + NPC dialogue

### 7.1 NPCs SkyyQuests owns (board, fisher) - the SkyyMerchants / TownProbe pattern (VERIFIED)
Vanilla role picked by name (`Temple_Kweebec_Static`-style: Invulnerable, MotionStatic, no vanilla shop); `*UseNPC` root + OUR lang key
`server.skyyquests.talkHint` = "Press [{key}] to talk" (TownProbe #3: mode 1 shows the real key glyph - VERIFIED); Nameplate /
DisplayName / PersistentDisplayName; registry `Skyy_SkyyQuests/npcs.tsv` (uuid, id, world, x,y,z, facing); orphan + ghost removal,
re-spawn after 15 s grace; placed by `/questadmin npc add <id>` at the admin's spot (hub world only by default). Pebble art
(`art/pebble`, TownProbe #2 PASS: Talk + Wave) is the quest-giver model where no vanilla NPC fits; per-town alias + hat (TownProbe #15).

### 7.2 The hub QUEST BOARD
An NPC "Quest Board" (the vanilla board prop as the model, UNVERIFIED U7 - fallback: a Kweebec clerk beside the vanilla sign) at the hub
spawn steps. F -> the board page: the lines you can start (Zone 1 town line, side lines), the DAILY JOBS (3 per profile, seed =
FNV-1a(pkey | day) - TownProbe #12 PASS across restart + world change - VERIFIED), your claims. Job pool + rows = Zone1 spec section 3
(reused as is; its numbers are placeholders in the `board.jobs` table). Opens after tutorial task 21 (you are in the hub) - never
gated on earlier tasks.

### 7.3 The FISHING quest (`quests/fishing_intro.properties`, `mode=chain`)
NPC "Marlow" (fisher, hub pier; vanilla role + our hint) - talk -> dialogue (3 lines) -> task 1 "Take the pole" (reward paid on accept:
Crude Fishing Pole lifelong `ll=1` + Wooden Reel + T1 hook / line / sinker through `gear:fn:grant` with `grantId`, exactly
`research/Gathering-Shards-Spec.md` 3.1 step 3; ids `SkyyFishing_Rod_*` / `SkyyFishing_Reel_*` exist in SkyyFishing 0.1.3 - VERIFIED;
the Crude tier id is the Gathering round's) -> task 2 "Catch a fish" (`event fishing:catch 1`) -> task 3 "Show Marlow" (`talk marlow`)
-> 50 Fishing XP + 50 coins. Repeat-proof by `issued=`. Without SkyyFishing the line is hidden.

### 7.4 Dialogue page
TownProbe's page made permanent: NPC name + portrait (ItemIcon OR our png - BOTH render, TownProbe #8 VERIFIED), wrapped line, up to 3
choice buttons, Next / Accept / Decline / Close / Esc (TownProbe #16 VERIFIED), instant text, one dialogue at a time per player; opens
on the NEXT tick via `World.execute`, never inside the Use handler (one page per press, 7.4 ms - VERIFIED). Dialogue files
`dialogue/<id>.properties` = the cloud spec 1.2 grammar (lines, choices, goto, end=accept).

## 8. Server Setup rows (config kit, `tools/CONFIG-CONTRACT.md`; page title "Quests", node `skyyquests.admin`, times in seconds)

| Key | Type | Default | Flags | Meaning |
|---|---|---|---|---|
| `quests.enabled` | bool | on | part,danger | the whole mod (off = no counting, widget empty) |
| `quests.tutorial.enabled` | bool | on | live | the tutorial line |
| `quests.tutorial.welcome` | bool | on | live | the first-join welcome page |
| `quests.tutorial.rewards` | table `text\|int\|text;none;Task\|Coins\|XP` | section 3 values | live | per task: coins + "Skill:N" |
| `quests.widget.tasks` | int 1-3 | 3 | live | server default for "Tasks shown" |
| `quests.widget.doneSeconds` | dec 0-10 s | 2.5 | live | the green "Done!" hold |
| `quests.markers.npc` | choice `off\|prop\|particle` | prop | live | the ! / ? style |
| `quests.markers.map` | bool | on | live | map / compass markers |
| `quests.markers.trail` | bool | off | live | the particle trail (0.4) |
| `quests.poll.seconds` | int 1-10 | 1 | live | the reach / direction hop |
| `quests.lazy.seconds` | int 2-60 | 5 | live | the bridge / tier / level check |
| `quests.claim.retrySeconds` | int 10-600 | 60 | live | re-try waiting claims (full inventory) |
| `quests.event.rate` | int 1-100 | 20 | live | `quest:fn:event` calls per player per second before extra ones are dropped (logged once) |
| `board.*` | Zone1 spec section 9 as is | | | jobs per day 3, reset 86400 s, anchor 0, rerolls 0, dailyCoinCap 1000, `board.jobs` table |
| `npcs.world` | text | the hub world | restart | where `/questadmin npc add` is allowed |

Player settings (`settings:fn:register`, category `general` -> a "Quests" tab when SkyyMenu adds categories): `quests.tasksShown`
(choice 1/2/3 - needs the Settings-Spec v2 choice row; until then two bools `quests.compact`, `quests.hideEmpty`), `tutorial.hide`
("I know how to play"), `quests.chat` (task-done lines) - routed by the Messages page as type `quest`.

## 9. Commands (HANDOFF section 3), permissions, saved data, lag rules

| Command | Who | Notes |
|---|---|---|
| `/quests` (alias `/quest`) | player (`hytale:Adventurer` on the command AND every sub / usage variant) | the log page |
| `/quests track <line>`, `/quests hide`, `/quests show`, `/quests claim`, `/quests board` | player | subcommands with required args (no optional positionals) |
| `/questadmin reload \| check \| list <player> \| set <player> <line> <task> done\|undo \| repay <player> \| place set <id> \| npc add <id> \| npc remove <id> \| npc list \| board <player> [reroll]` | `skyyquests.admin`, `setPermissionGroups(new String[0])` (lint perm_group_leaks) | every change through `CfgFn.cmdSet` where it is a row |

Saved data (all under `Skyy_SkyyQuests/`): `config.properties` (+ kit history / log), `quests/*.properties`, `dialogue/*.properties`,
`places.properties`, `npcs.tsv`, `players/<pkey>.properties`, `quests.log` (PAID / LOST? / issued lines, rolled at 5 MB). Removal /
rollback: state files stay; unknown task ids are kept, not dropped; removing the mod loses nothing but quest progress (no items live
in it - the pole / shard are SkyyGear / SkyyIslands items). No floor.

Lag rules (`research/Code-Structure-Audit.md`): event handlers = one `want` map read for players without objectives; NO per-tick work
for idle players; one world hop per world per second ONLY while a player there has a reach / direction need; the 5 s lazy check only
for players with bridge / tier / level objectives; files only on the private SkyyQuestsIO thread (tmp + fsync + move, no sleeps);
the bridge map cached in a `static volatile` field (no `System.class` lock); `quest:fn:hud` is a memory read; map markers from a
cached per-player list; particles only near NPCs with an offer; `quest:fn:event` rate-capped per player. The smoke test's
"Task took" gate applies.

## 10. Build phases (rounds) + Skyy's test plan

| Round | Content | Size | Done when (Skyy tests) |
|---|---|---|---|
| **Q1 - SkyyQuests 0.1 + SkyyHud 0.3.21** (after Hud 0.3.20's feed lands) | engine (loader, per-profile state, claims, `want` index, all objective types with the VERIFIED sources, lazy checks), the TUTORIAL line with today's sources (tasks whose caller is missing show "(soon)"), welcome page, `/quests` log page, `quest:fn:hud` + the Quest widget (5 states, arrow, distance), places file, chat / feed lines, Server Setup rows, player settings, `print "[SkyyQuests] 0.1 ready"` | ULTRACODE full round (new system, saved data, rewards, permissions, 2 mods) | T1 new profile: welcome page; chop 10 logs ticks + "Done!" green; task 6 before 4 stays done; reward paid once after a relog; widget arrow points at island 2; "I know how to play" hides the tasks and a hidden task still pays |
| **Q2 - companions** | the one-line `quest:fn:event` / `page` calls (section 4.3) in Menu, Bank, Bazaar, Gear (+ `gear:fn:grant`, `gear:fn:lifelong`), Wardrobe, Sacks, Exploration, Pets, Classes, Fishing, Islands (+ `island:fn:place`, portal event), Party, Skills, Collections | one full round, several lean bumps cross-checked together | T2 every tutorial task 1-24 completes from its real action; `/questadmin list` shows the counts |
| **Q3 - SkyyQuests 0.2** | markers (NPC ! / ?, map, compass check, minimap kind), hub board NPC + daily jobs, fishing NPC + line, dialogue pages, `/questadmin npc` | full round (NPCs, items) | T3 hub: board + Marlow show "Press [F] to talk", ! over them, map + compass markers; the pole arrives once; 3 daily jobs survive a restart |
| **Q4 - content** | Zone 1 town line (Zone1 spec), later lines; SkyyIslands' 3-island prefab round feeds tasks 11 / 19 / 20 / 21 | content + islands round | T4 play the first hour start to hub |
| **Q5 - 0.3 / 0.4** | trail, guide fairy (SkyyPets), in-game quest editor (Server Setup page), party credit, repeatable quests | later | |

Harness per round (the TownProbe test style): every objective type fed by a stand-in event; a profile switch mid-count; the claim
ledger crash points (kill between write and pay); `want` index rebuild; the hud Object[] shape against SkyyHud's reader; a bare-JVM
smoke of the loader on the shipped files; lint 0 fails; crosscheck 0 fails.

## 11. Risks and UNVERIFIED items (with probe steps)

| # | Item | Why it matters | Probe |
|---|---|---|---|
| U1 | QuestLines suite not in the Mods folder | PROJECT-RULES 2 asks for a study | Skyy installs it once (or the cloud reads its pages); 30-min read-only look at its quest data shape; note in `research/Mods-Folder-Survey.md`. Nothing in this spec waits on it |
| U2 | Per-player ! / ? over an NPC | a prop nameplate is world-wide; a player with no offer would still see "!" | SkyyUiProbe-style: spawn the prop only for viewers with an offer (entity visibility per player: UNVERIFIED) vs the emote-particle route (mode 3, per player list - the probe sent it, Skyy saw mode 2); pick the one that is per player, else accept a shared "!" (the board always has offers anyway) |
| U3 | Quest map markers on the vanilla COMPASS | Skyy asked for "more than your map" | after Q3, look at the compass with a stamp marker active; if absent, SkyyHud's compass widget (Layout-Spec combat / compass row) draws them from `quest:fn:markers` |
| U4 | Detecting a PERFECT PARRY (Perfect Parries, ARR) and a DODGE ROLL (0.7 / Perfect Dodges) | tutorial task 13 | `tools/dev/cpgrep.py` + reflect on the installed jars for an event / component they add; `InteractionChainStartEvent` (engine, cancellable ECS - exists) for a dodge chain; until found, task 13 = kills only |
| U5 | EAT and TILL / WATER events | tasks 7 and 16 | `InteractionChainStartEvent` for a consumable chain (SkyyCooking may already hook eating - read its script); `UseBlockEvent` on soil with a hoe (SkyySkills' Farming XP path already credits tilling - reuse its rule); else fallbacks in section 3 |
| U6 | `coll:fn:tier` exact `apply` shape | task 6 | read `SkyyCollections/build_skyycollections_0.2.10.py` CollTierFn in the build round (5 min) |
| U7 | A board PROP as an NPC model | look of the hub board | the TownProbe `pebble` route with a vanilla furniture model; fallback clerk NPC + the vanilla sign |
| U8 | Island 2 / 3 as regions of ONE world vs separate worlds | `enter` vs `reach` | SkyyIslands' 3-island design decides; the spec supports both (`enter island:2` or `reach island2 radius 12`) |
| U9 | Hub hotkey / hub icon panel on 0.7 (task 2) | SkyyMenu's 0.7 inventory work (perfmenu round) | task 2's `page hub` fires from whatever the hub opener becomes |
| R1 | Reward dupes | coins / items | the claim ledger (2.6), `issued=`, grantId on items, count before / after |
| R2 | Two mods cancelling one NPC's Use | TownProbe #5 | SkyyQuests owns only ITS NPCs; town NPCs through `quest:fn:talk` |
| R3 | Marker re-send storms | TownProbe sent 8077x | cached per-player marker list; providers answer from memory; send on epoch change only |
| R4 | World-thread stalls | audit | no file I/O or sleeps on world threads; event handlers return in one map read for idle players |
| R5 | Old profiles | the tutorial appears on every existing profile | the welcome page offers "I know how to play"; bridge-type tasks tick at once (class, bank) |
| R6 | Companion versions lag | tasks never complete | the widget marks "(soon)" per task whose caller is absent; nothing blocks |

## 12. Questions for Skyy (each with a recommended default)

| # | Question | Default |
|---|---|---|
| 1 | Tutorial rewards: the small placeholder numbers in section 3 (1,200 coins + 1,180 XP in all) - fine to start? | [yes; tune in the Server Setup table] |
| 2 | Trim / reorder the 24 tasks? Any to drop for launch (e.g. 17 pets, 23 party)? | [keep all; hidden until their mod is ready] |
| 3 | The island 3 MINI BOSS: which creature? | [a Lv 10 Earth Crystal Golem variant (TownProbe-proven role), renamed "Shardkeeper"] |
| 4 | Task 13: keep "dodge roll" + "perfect parry" as parts of the task, or hint text only? | [parts, if probe U4 finds them; else hint text] |
| 5 | Widget when nothing is left: hide (Layout-Spec default) or show "No active quests"? | [hide] |
| 6 | NPC markers: a shared "!" prop (everyone sees it) is fine, or must it be per player? | [shared on the board / fisher; per player where the probe allows] |
| 7 | Co-op joiners: the same tutorial on a friend's island, or a shorter "visitor" line? | [same tutorial; it counts anywhere] |
| 8 | The fishing NPC's name and look: "Marlow", a vanilla fisher-style NPC at the hub pier? | [yes] |
| 9 | Chat line on each task done (one line) + progress in the feed - or feed only? | [done = chat, progress = feed, both switchable] |
| 10 | The Zone 1 town line (Zone1 spec, 9 quests + daily board): build right after the tutorial (Q4) or after the islands round? | [after the 3-island round, so the hub exists] |
