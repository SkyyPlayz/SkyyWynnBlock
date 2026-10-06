# SkyyQuests - design spec

Cloud draft, 2026-10-06. Paper design for the quest system that every story document waits on. Locks: "quest hooks ship with SkyyQuests, not now" (docs/answered/project.md, 2026-09-25); the Server Setup plan lists "NPC quests: quest giver, steps, rewards **in game**" and "the big editors come with their mods" (`docs/plans/SkyWynn-Server-Setup-Plan.md`);
profiles = full saves (`tools/PROFILES-CONTRACT.md`); cross-mod calls only through the shared `skyy.bridge` with plain `java.lang` types; vanilla-look UI (kit `tools/skyyui.py`). It must serve: `Story-Script-Draft.md` (12 starter quests), `Story-Script-Zones-2-5.md`, `Dragon-Quest-Spec.md`, `Slayers-Spec.md` (to come), world events and the Tab.
Engine facts (NPC interaction events, custom pages, markers, position polling) are UNVERIFIED; where an existing mod already proves one, it is named.

## 0. What SkyyQuests is, in plain words

A **small mod** that stores per-profile quest state, watches a handful of game events, shows a **quest log page**, a **dialogue window** for NPCs and a small **tracker widget**, gives **rewards** and exposes **flags** other mods read (portal unlocked, warp unlocked, island open).
Quests are **data files** (not code) with a simple format; an **in-game editor** (later phase) lets a server owner change them. It depends on nothing (zero-dependency rule) but uses the bridge to read levels, collections, class and to pay rewards when the other mods exist.

## 1. Data model

### 1.1 Concepts
| Concept | Meaning |
|---|---|
| **Quest** | an id, a name, a **chain** (line), prerequisites, steps, rewards, flags it sets |
| **Step** | one thing to do: an **objective** + the text shown + optional dialogue and markers |
| **Objective** | a typed condition (section 3) with a target count and a progress counter |
| **Dialogue** | a short script of lines and choices attached to an NPC or a step |
| **Flag** | a named boolean / counter on the **profile** (`starter.portal.unlocked`, `zone2.open`, `dragon.element`) |
| **Chain** | an ordered set of quests (the Zone 1 chain, the dragon line) |
| **Giver / NPC** | a quest NPC entity (named, with a marker); Pebble, Clerk Mossby, ... |
| **Repeatable** | daily / weekly / unlimited quests with a cooldown |

### 1.2 Quest files (one per quest, `Skyy_SkyyQuests/quests/<chain>/<id>.properties`)
Plain `key=value` (the project's own style, no JSON dependency). Example, from the starter chain:
```
id=starter.q02_wood
chain=starter
order=2
name=Wood You Believe It
summary=Chop 10 logs from the trees on your shard.
giver=pebble
requires.flag=starter.q01_done
requires.level.skill=none
steps=1
step.1.type=collect
step.1.item=group:logs
step.1.count=10
step.1.text=Chop 10 logs.
step.1.hint=Hit a tree until it falls. Any wood counts.
reward.skillxp=Foraging:50
reward.coins=100
reward.flag=starter.q02_done
dialogue.start=pebble.q02.start
dialogue.done=pebble.q02.done
```
Dialogue files `dialogue/<id>.properties` use numbered lines with speaker, text, optional choices and conditions:
```
id=pebble.q02.start
line.1=Pebble|Trees. They are a type of tall grass. Hit them until they stop being trees.
line.2=Pebble|Ten logs. In four thousand years I have collected zero.
choice.1.text=Where do I find a tree?
choice.1.goto=3
line.3=Pebble|Behind you. Everything is behind you.
end=accept
```
All text is in a **lang file** (`quests.lang`) keyed by id so a server can translate; the file stores the key, not the sentence, in the production form (the example inlines text for readability).
Reload: `/quests reload` (admin) and the in-game editor (phase 3).

### 1.3 Player state (per profile: `players/<pkey>.properties`, keyed by `pkey(u)` from the Profiles contract)
```
v=1
active=starter.q03_table,starter.q04_rocks      (a player can have several; max 5 by default)
done=starter.q01_wake,starter.q02_wood
step.starter.q04_rocks=1
progress.starter.q04_rocks.1=12                 (the counter for the objective)
flag.starter.portal.unlocked=1
cooldown.daily.hunt=1786543200000               (epoch ms)
tracked=starter.q04_rocks
firstSeen=...
```
Atomic writes like the other mods (`.tmp` + move), a dirty set + a saver thread, the 6 s settle window after a profile switch (no progress while `profile:busy`). **Caches keyed by the pkey string**, republished on `profile:epoch:<uuid>` changes.

## 2. Events SkyyQuests listens to (cheap, no per-tick world work)

| Event | Source (UNVERIFIED engine names) | Feeds objective |
|---|---|---|
| Entity killed by a player | the damage / death event (SkyyMobs and SkyySkills already hook it: the kill path) | `kill` |
| Item picked up / harvested by hand | `InteractivelyPickupItemEvent` (used by SkyyCollections) | `collect` (also reads collection counters when they exist) |
| Recipe crafted | `CraftRecipeEvent` (SkyyGear uses it), Workbench / pocket | `craft` |
| Block placed / broken by the player | break / place events (Collections, Islands) | `place`, `break` |
| NPC interacted (F / right-click) | `UseEntityEvent$Pre` (SkyyIslands uses it for farm animals) | `talk`, `deliver` |
| Player position (1 s poll on the world thread, the existing Perks.tick pattern) | a cheap box test per active `reach` / `enter` objective, **only when such an objective is active** | `reach`, `enter` |
| Level up / collection tier / class chosen / zone entered | bridges: `skill:fn:level`, `coll:` functions, `class:fn:get`, `explore:` keys; the mods publish "event" counters we poll every 5 s, or SkyyQuests asks on demand | `level`, `tier`, `class`, `zone` |
| Boss killed | the kill event + a named role id | `kill` with `target=role:...` |
| Command / button | the quest page buttons | `accept`, `abandon`, `track` |
The poll rule: **no work per tick for players without an active quest that needs it**; an inverted index maps event type -> the players with matching active objectives.

## 3. Objective types (v1)

| Type | Fields | Completes when | Notes |
|---|---|---|---|
| `talk` | `npc` | the player interacts with that NPC | advances dialogue |
| `kill` | `target` (role id, group, or any hostile), `count`, optional `level` or `zone` | N kills | respects the level-gap rule: kills of far-below mobs count 0 for quests above the gap (row) |
| `collect` | `item` (id or `group:logs`), `count`, `source=gather|any` | N items **obtained** (gathered, not bought; bag withdrawals never count) | reuses the Collections "obtained" rules |
| `have` | `item`, `count` | the player carries N (inventory + bags) at the check | for "bring X" |
| `deliver` | `npc`, `item`, `count` | the player hands items to the NPC (consumed) | confirm button |
| `craft` | `item`, `count` | N crafted at any bench | uses the craft event |
| `reach` | `world`, `x`,`y`,`z`, `radius` | the player stands inside the sphere | the position poll |
| `enter` | `region` (named box / zone / island world) | the player enters it | |
| `place` / `break` | `block`, `count` | placed / broken (player-made blocks excluded where relevant) | bridge repair: place 24 planks |
| `use` | `item` or `interaction` | the player uses an item / interaction object (place the Portal Shard in the frame) | custom block interaction hook |
| `level` | `skill`, `level` | the skill reaches the level | read via `skill:fn:level` |
| `tier` | `collection`, `tier` | collection tier reached | via the Collections bridge |
| `class` | `class` | the profile's class equals | |
| `flag` | `flag` | a profile flag becomes true | glue between mods |
| `wait` | `seconds` | online time passes | for hatching timers |
| `choice` | `options` | the player picks one (dialogue choice) | for the dragon element |
| `group` | `members` (list of objectives) | all done (any order) | "three stamps" |
| `any` | `members` | one done | alternatives |
A step may use **one** objective or a **group**. Steps run in order; `parallel=true` lets steps of a quest progress together.

## 4. UI

### 4.1 Quest log page (`/quests`, also a SkyyMenu tile "Quests")
A vanilla-look inline page: left list (Active / Available / Done tabs, the vanilla tab rule), right details: name, chain, summary, **steps with a progress bar** per objective (`12 / 20`), rewards preview, **Track** and **Abandon** buttons (abandon asks to confirm; some quests cannot be abandoned).
Rows under 80 characters; the long text wraps in the details box; a footer **Close** button. Opens with one `Function` call from the menu; no periodic refresh (a **Refresh** button).

### 4.2 Dialogue window
Opens when a player interacts with a quest NPC: the **NPC name + portrait icon**, the line text (wrapped), up to 4 **choice buttons**, **Next** / **Accept** / **Decline** / **Close**. Typing speed: instant (no typewriter) to avoid page updates; a **skip all** option. One dialogue at a time per player; a dialogue lock keeps the quest NPC from being used by two players at once only if the dialogue is "private"; otherwise parallel (the page is per player anyway).
**UI rules from the project:** inline page only, no `.ui` files, no underscores in ids, a Close button, dialogue never blocks the world thread, a page guard against the "Loading..." stuck page after world changes (SkyyBank / SkyyMenu already have the guard).

### 4.3 Tracker widget (SkyyHud)
A small HUD widget (own HUD key like the minimap) listing the **tracked quest's current step** (one line) and its progress, with a maximum of 3 lines; hidden when nothing is tracked; update only when progress changes (no polling). The HUD editor places it.

### 4.4 Markers
Quest NPCs show a **marker over their head** (`!` available, `?` ready to turn in) as a nameplate prefix or a floating text (UNVERIFIED which works), and objective locations (`reach`, `enter`, a quest area) show a **map marker** through `WorldMapManager.addMarkerProvider` (the route the Minimap research found), also visible on the compass. Markers are per player.

## 5. Rewards and what they call

| Reward | How |
|---|---|
| Coins | `coins:fn:add` (Object[]{UUID, Long}); R3 rule: quests may give coins, never skip collections |
| Skill XP | `skill:fn:addxp` (Object[]{UUID, skill, amount, source}) with the bridge caps |
| Items | direct to inventory (or a **bag first**), overflow to the mailbox (the same "claim" idea as the Auction House) |
| Gear | `gear:fn:roll` mode 8 (as SkyySacks does) so a quest reward is a rolled / unidentified item |
| Pocket Shard / pet egg / accessory | item grants by id |
| Titles | `explore:title` style; a `title:<uuid>` bridge when it exists (SkyyRanks chat order `[Rank] [Title] Name`) |
| Flags | the quest sets flags (`starter.portal.unlocked`, `zone2.warp`, `unlock.zone2`) which **SkyyIslands / SkyyWorldGen / SkyyExploration read** through `quest:fn:flag` |
| Unlock a warp / portal | a flag, read by the owning mod (they decide what to unlock) |
Rewards are paid **once**, atomically with the "done" mark (state written first; a crash between payment and mark is resolved by marking first and **paying from a ledger**: `ledger.paid.<quest>=1` is written before each payment and cleared when the payment returns true).

## 6. Bridge contract (plain `java.lang` types)

| Key | Shape | Who reads it |
|---|---|---|
| `quest:fn:flag` | `Function(Object[]{UUID, String flag}) -> Boolean` (the **active profile**) | SkyyIslands (portal shard), SkyyWorldGen (`unlock.mode` = quest), SkyyExploration (warps), SkyyClasses |
| `quest:fn:setflag` | `Function(Object[]{UUID, String flag, Object value}) -> Boolean` | trusted mods (rate-limited) |
| `quest:fn:done` | `Function(Object[]{UUID, String questId}) -> Boolean` | menus, NPC shops (unlock lists) |
| `quest:fn:active` | `Function(UUID) -> String` comma list of active ids | HUD, menu |
| `quest:fn:progress` | `Function(Object[]{UUID, String questId}) -> String` "step:progress/target" | HUD |
| `quest:fn:start` | `Function(Object[]{UUID, String questId}) -> Boolean` (another mod starts a quest: a world event, a dungeon) | events, dungeons |
| `quest:fn:event` | `Function(Object[]{UUID, String type, String key, Number amount}) -> Boolean` | **other mods report custom events** (e.g. "boss:ember_warden killed", "event:hiccup completed") without SkyyQuests knowing them |
| `quest:epoch:<uuid>` | Long, +1 on every state change | cache invalidation |
| `config:def/fn/epoch:SkyyQuests` | the config kit | Server Setup rows |
Per-profile values follow the PROFILES rules: `quest:*` answers describe the **active** profile; republish on `profile:epoch`.

## 7. Server Setup rows (config kit)
`quests.enabled`, `quests.maxActive` (5), `quests.trackerLines` (3), `quests.abandonConfirm` (on), `quests.markers` (on), `quests.dialogue.skipAll` (on), `quests.repeatable.dailyResetSeconds` (anchor), `quests.rewardMailbox` (on), `quests.levelGapPercent`, plus the **chain table** (enable / disable a chain; reorder). Quests themselves are files; the later **editor page** edits them (phase 3).

## 8. Anti-exploit and safety
| Risk | Handling |
|---|---|
| Quest item duplication | `deliver` removes items first, pays after; the ledger prevents double rewards on a crash; quest items are **bound** (no trade / AH / vault) and removed on abandon |
| Re-doing a quest for repeated rewards | `done` set + the repeat cooldown; the reward ledger |
| Kill farming for kill quests | the existing kill rules (far-below level counts 0, creative never, pets' kills credit the owner) |
| Gather quests with placed blocks | the Collections "obtained" rules |
| Profile switch mid-quest | state is per pkey; no progress during `profile:busy` or the 6 s settle |
| Alt profiles / sharing | each profile has its own quests; rewards go to the active profile only |
| Cheating with commands (`/give`) | `collect` counts gathered items only; admin gives are flagged |
| Party credit | `kill` and `collect` credit the **killer / gatherer**; party quests (later) credit each member within 48 blocks (like the combat XP share) |
| Mod removed | state files stay; unknown quest ids are ignored and kept |

## 9. Build plan (versions)
| Version | Content | Round |
|---|---|---|
| **0.1** | data files + loader, per-profile state, flags + bridge, objectives `talk collect kill craft reach enter deliver use level flag choice group`, quest log page, dialogue window, rewards (coins, XP, items, gear, flag), `/quests`, tracker widget off; **the starter chain** as content (12 quests) | full round (new mod, saved data, items) |
| **0.2** | NPC placement (`/questnpc create <id>` in game), markers, tracker widget, repeatable quests, map markers, party credit | lean-to-full |
| **0.3** | the **in-game quest editor** (Server Setup page: create a quest, add steps, pick objective types from a dropdown, edit dialogue) | full round |
| **0.4** | Zone 1-5 chains, dragon line, slayers, events through `quest:fn:event` | content rounds |
| Content | the story docs are the content source; each quest is one file; about 60-80 quests for the launch story + slayers | local + cloud (writing) |

## 10. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | NPC entity creation with a custom role/name and an interaction hook: SkyyIslands uses `UseEntityEvent$Pre`; check a custom named NPC (spawn by plugin, persistent across restarts, model choice). |
| 2 | A marker over an NPC's head (`!` / `?`): nameplate text vs a floating entity vs a particle. |
| 3 | `WorldMapManager.addMarkerProvider` works in worlds the quests use (islands without a map?). |
| 4 | Whether the dialogue page can use an item icon as a portrait (the kit supports ItemIcon). |
| 5 | The `use` objective for "place the Portal Shard in the frame": a custom block with an interaction (the Pocket Shards research asks the same block-entity question). |
| 6 | Bag withdrawal vs `collect` / `have` interaction with Magic Bags (the bag pool counts for `have`). |
| 7 | The page guard pattern for the "Loading..." stuck page (SkyyBank 0.1.6 / SkyyMenu 0.3.6). |

## 11. Questions for Skyy
1. Quest files as **plain text files + an in-game editor later** (recommended) or the editor first?
2. Max active quests: 5 (recommended) or unlimited?
3. Should quest NPCs show a `!` / `?` marker above their head (needs the engine check) or only a map marker?
