# Island co-op + settings: build spec (SkyyIslands 0.5, on top of 0.4.5)

*Written 2026-09-24 by the research workflow `skywynn-island-settings` (writer). Research only: no build script, mod folder or game file was changed.*
*Revised 2026-09-24 evening for Skyy's co-op model from the beta test (HANDOFF log 2026-09-24 20:10, BETA BACKLOG item 7), plus `/island reset` and the grass-tint resend. Builds on `SkyyIslands/build_skyyislands_0.4.5.py` (one island per profile, `islands/<pkey>.properties`, GuardDamage/Break/Place/Pickup/Use, starter-kit fix). Owner: Skyy (they/them).*

**Skyy's asks.**
- 2026-09-24 morning: "for island visitors, look into some minecraft skyblock mods. they usually have a settings menu where you can control all of that. (and a lot more, like the island biome. turning on and off visitors and what not.)"
- 2026-09-24 beta: "/is invite <player>: if they join, they are part of my island, like a co-owner; the leader keeps the rights to kick players and disband; when they do /is it takes them to MY island; they can change island settings if made admin". Inviting is **separate** from build permission. An island menu goes in the SkyWynn Menu and on `/island menu`.
- Queued for 0.5.1 (HANDOFF log 06:55): `/island reset` (wipe and rebuild from the template with a fresh starter kit), and resend the re-tinted chunks so grass turns green without re-entering.

**Legend.** VERIFIED = seen in `HytaleServer.jar` bytecode or reflection (`tools/dev/reflect.py`, `bc.py`, `bcfull.py`, `cpgrep.py`), read from `Assets.zip`, an installed mod jar (read-only), or our own scripts. UNVERIFIED = design or inference that still needs the in-game test in section 12. `[SKYY?]` = a choice Skyy should confirm; the spec picks a default so the build is not blocked.

---

## 0. Verdict (plain words)

**All of it can be built now.** The co-op model is pure SkyyIslands logic on top of calls 0.4.5 already uses: the island file, `IslandCmd.go`, the guards, `HubCmd.sendToHub` and the instance calls. The settings menu copies Hytale's own protection rules (the trigger-volume "no use / no door / no harvest / no build / no damage" systems in `com.hypixel.hytale.builtin.triggervolumes.system.TriggerVolumeRuleSystems$*`). Reset reuses island creation. The grass fix is one vanilla call we never made (section 5).

| Skyy asked for | When | How (VERIFIED unless noted) |
|---|---|---|
| `/island invite` = join my island as co-op (with accept) | **Now** | Pending invite + `/island accept`. The member's **active profile** joins. Custom logic, no engine blocker. |
| Member's `/island` goes to MY island | **Now** | "Home island" rule (1.3): `/island` goes to the island you are a member of. `IslandCmd.go` already loads an unloaded island with `Universe.addWorld`, so this works with the owner offline. |
| Leader keeps kick + disband | **Now** | Owner-only `/island kick`, `/island disband`. |
| Admins change settings | **Now** | New Admin role: `/island promote` / `demote` (Owner only). Admins edit every settings tab. |
| Build permission separate from inviting | **Now** | Trusted role: `/island trust` / `untrust`. Build rights only. Not a member, and their `/island` stays their own. |
| Island menu (`/island menu`, SkyWynn Menu button) | **Now** | One big inline page with 5 tabs (section 7). SkyyMenu dispatches `/island menu`. |
| `/island reset` | **Now** (UNVERIFIED in game) | A fresh island world from the `SkyyIsland` template under a new name. Members, trusted, bans and settings are kept. The old world folder stays on disk as a backup (1.7). |
| Grass green without re-entering | **Now** (UNVERIFIED in game) | After each re-tint, call `WorldNotificationHandler.updateChunkTints(index)`, the vanilla `/chunk tint` call (section 5). |
| Per-role permission flags | **Now** | 14 flags on 8 engine events, one click per grid cell (section 3). |
| Visitors on/off, limit, expel, ban, lock | **Now** | Custom logic. Checked at `/island visit`, on arrival, and by a 5 s sweep (4.1). |
| PvP | **Now** | `WorldConfig.setPvpEnabled` per island world. The engine enforces it. |
| Mob spawning | **Now** | `WorldConfig.setSpawningNPC`. What spawns depends on the biome. |
| Visit ping | **Now** | A chat line to the online owner and members. |
| Island biome (11 presets) | **Now, slice B** | Grass tint + Environment asset + live resend (4.4). |
| Weather lock (dry weathers) | **Now, slice B** | Vanilla `/weather set` pattern. Rain and storms are excluded (farm boost). |
| Visitor landing point | **Now, slice B** | 5-argument `teleportPlayerToLoadingInstance`. |
| Time lock, offline visits, island warps, split spawning, leader transfer | **Later** | 4.8. |

"Slice B" = feasible now and independent of the rest. It can ship in 0.5 if the build stays manageable, otherwise in 0.5.1 (section 11).

**What changed from the first draft of this spec:**
1. `/island invite` now makes a **co-op member** and needs `/island accept`. In the draft, and in 0.4.x, invite only gave build rights.
2. Build rights alone are the **Trusted** role (`/island trust`). Trusted players are not members, and their `/island` does not move.
3. New **Admin** rank between Member and Owner.
4. A member's `/island`, `/island home`, the profile-switch teleport and `/island visit <member>` all go to the co-op island.
5. Membership belongs to the member's active profile. Their own island stays saved and comes back when they leave.
6. New commands: `accept`, `decline`, `leave`, `kick`, `promote`, `demote`, `disband`, `trust`, `untrust`, `menu`, `reset`.
7. The page is `/island menu` (`/island settings` is an alias), with an Overview and a Members tab.
8. The Trusted defaults are narrowed to building: harvesting crops and beds moved to Member (3.2).
9. 0.4.x "members" (build-rights invites) migrate to **Trusted**, not to co-op (section 6).
10. Grass-tint resend and `/island reset` added.

---

## 1. The co-op model

### 1.1 Roles

| Rank | Role (UI name) | Who | How you get it | How you lose it | Their `/island` goes to | Stored (owner's island file) |
|---|---|---|---|---|---|---|
| 4 | **Owner** (leader) | The profile that created the island | Created it | Never (profile delete is SkyyProfiles' business; 0.1 has none) | This island (unless they are a member elsewhere, 1.4) | File name = owner pkey |
| 3 | **Admin** | A member the Owner promoted | `/island promote <name>` (Owner) | `/island demote` (back to Member), kick, leave, disband | The co-op island | `admins=` (pkeys, subset of `members=`) |
| 2 | **Member** (co-op) | Shares the island like a co-owner: builds, chests, farm, animals | `/island invite <player>` + their `/island accept` | `/island leave`, `/island kick` (Owner), `/island disband` (Owner) | **The co-op island** (the owner's) | `members=` (pkeys) |
| 1 | **Trusted** | A helper who may build. Not a member | `/island trust <player>` (Owner or Admin) | `/island untrust <name>` | Their own island (unchanged) | `trusted=` (pkeys) |
| 0 | **Visitor** | Everyone else, including you and your members on another profile | Being there | n/a | their own island | n/a |
| -1 | **Banned** | Can't enter; denied everything, even doors | `/island ban <player>` (Owner or Admin) | `/island unban <name>` | their own island | `banned=` (player UUIDs: a ban hits the person, every profile) |

Server admins (`skyyislands.admin`) pass every flag and entry check, as in 0.4.x. They cannot edit someone else's settings in 0.5 (an admin settings command is "later").

### 1.2 Who may do what

| Action | Owner | Admin | Member | Trusted | Visitor |
|---|---|---|---|---|---|
| Invite a co-op member | yes | yes (`coop.adminsInvite` default `true`) | no | no | no |
| Kick a member, promote, demote | yes | no | no | no | no |
| Disband the co-op, reset the island | yes | no | no | no | no |
| Leave the co-op | no (disband instead) | yes | yes | n/a | n/a |
| Trust / untrust | yes | yes | no | no | no |
| Change settings (permission grid, visitors tab, PvP, spawning, biome, weather, landing point) | yes | yes | no, but sees them read-only | no | no |
| Ban / unban, lock / unlock | yes | yes (not members: "ask the owner to kick first") | no | no | no |
| Expel a visitor or trusted player standing on the island | yes | yes | yes (so someone can deal with a griefer while the owner is away) | no | no |
| Build, chests, farm... | always | by the flags (3.2) | by the flags | by the flags | by the flags |
| Go to the island with `/island` | yes | yes | yes | no (`/island visit`) | no |

LOCKED 2026-09-25 (Skyy): Island Admins may invite co-op members. `coop.adminsInvite` defaults to `true`. Was: `false`, Owner only. SkyyIslands 0.5.2 still defaults the row and `config.properties` to `false`. A file already on `false` keeps owner-only invites until that line is set to `true`.

LOCKED 2026-09-25 (Skyy): Admins may expel, ban and untrust visitors and helpers. Only the Owner kicks co-op members. That was already the default.

### 1.3 The home island rule

`homeKey(uuid)`: take `k = pkey(uuid)` (the active profile). If `MEMBER_OF[k]` names an island whose file still lists `k` in `members=`, the home island is that island's owner key. Otherwise it is `k` (your own island). A stale index entry heals itself: it simply does not match.

Everything that means "my island" uses `homeKey`:
- `/island` and `/island home` (alias `go`): `go(homeKey, own = homeKey.equals(k))`. `own=false` never creates an island. A member whose co-op island is somehow missing from disk gets "That island is not available - ask the owner", and nothing is created.
- The profile-switch teleport: SkyyProfiles 0.1 dispatches the player's own `/island` after a switch (`islandOnSwitch=true`), so a switch lands on the new profile's home island. No SkyyProfiles change is needed.
- `/island visit <player>` goes to the **target's** home island. Visiting a co-op member takes you to the island they live on, as on Hypixel. The line says "Visiting Skyy's island (Wesley is a co-op member there)".
- `/island info` and `/island menu` describe the home island and your role on it.
- Bridge `island:<uuid>` = the home island's world name (9.3). SkyyHud 0.3.8's Zone widget already shows "Your Island" when the world equals `island:<uuid>`, so members see "Your Island" on the co-op island with no HUD change (VERIFIED in `build_skyyhud_0.3.8.py` `zoneText`).
- Login still routes to the hub first (0.2).

### 1.4 Membership belongs to the active profile

- **Accept binds the profile that is active when the player accepts.** The invite goes to a player; the pkey is resolved once at accept (contract pattern 4.1: one key per operation). The invite text names that profile: "Joining uses your current profile (Strawberry)".
- **Switching profile switches island.** On another profile the player's home is that profile's own island, and on the co-op island they are a visitor. Switching back makes them a member again. Nothing is rewritten.
- **Their own island stays.** The member's own island file, world, chests and trusted list are untouched while they are in a co-op. That island is dormant: `/island` does not go there. `/island leave` (or kick or disband) makes it their home again. `[SKYY?]` Should a member be able to visit their own dormant island? Default **no**, to keep one home per profile. Tell players to move items before they accept.
- **One co-op per profile.** A profile is a member of at most one island (`MEMBER_OF`). Accepting a second invite is refused: "/island leave first".
- **A leader can't join someone else.** A profile whose own island has members can't accept an invite ("You lead a co-op island - /island disband first"). An owner without members may join a co-op; their island goes dormant like any member's.
- **One role per player per island (anti-transfer).** Across all their profiles, a player holds at most one entry on an island: member, admin or trusted. Otherwise a player could drop items there as Trusted on profile 1, switch, and pick them up as a Member on profile 2. Accept is refused while another of their profiles has a role there. Trusting a player whose other profile is already trusted **moves** the entry to the current profile and says so. Inviting yourself or your own other profile is refused (the owner UUID check).
- **Commands act on the home island.** A member running `/island invite`, `trust`, `promote` and so on acts on the co-op island and is checked against their rank there. They can't manage their dormant island while they are a member.

### 1.5 Invite and accept (SkyyParty 0.1.3 pattern)

`/island invite <player>` (PLAYER_REF, online only). Checks, in order:
1. You are the Owner of your home island, or an Admin (`coop.adminsInvite` default `true`). Otherwise: "Only the island owner can invite (you are a member of Skyy's island)".
2. The island exists (`worldName(ownerKey) != null`). Otherwise: "Create your island first: /island".
3. The target is online and not you (the UUID, which also covers your other profiles).
4. The target is not banned here ("/island unban them first") and not already a member or admin here on any profile.
5. The co-op is not full: owner + members < `coop.maxPlayers` (default 5 = owner + 4). LOCKED 2026-09-25 (Skyy): co-op size stays 5, including the owner. That was already the default.
6. Store `INVITES[targetUuid] = Object[] { ownerKey, inviterUuid, Long expiryMs, inviterName, ownerName }`. A newer island invite to the same player replaces the older one.
7. Chat to the target: `[Island] Skyy invited you to join their island as a co-op member. Type /island accept (or /island decline) within 60 s. Joining uses your current profile (Strawberry). Your own island stays saved and comes back if you leave.` The inviter gets "Invited Wesley - they have 60 s". The invite also shows on the target's Overview tab with Accept / Decline.

A Trusted player may be invited. Accepting upgrades them and removes the trusted entry.

`/island accept`:
1. A pending invite that has not run out. Otherwise: "You have no island invite (or it ran out)".
2. `profile:busy:<uuid>` present → "Try again in a moment". Then resolve `k = pkey(uuid)` once.
3. `k` is already a member somewhere → "/island leave first". `k`'s own island has members → "/island disband first".
4. Another of your profiles has a role on that island → refused, naming the profile to switch to. The same pkey as Trusted is fine (it gets upgraded).
5. You are banned there now, or the co-op filled up in the meantime → refused.
6. Write the owner's file (IslandStore lock): `members += k`, `trusted -= k`, `name.<k>`, `coopSince.<k>`. Then `MEMBER_OF[k] = ownerKey`, remove the invite, `island:epoch` +1, and publish `island:<uuid>`.
7. Chat: "You joined Skyy's island! /island now takes you there. /island leave brings you back to your own island." The owner and online members get "Wesley joined the island co-op." Accept does **not** teleport: the player may be busy, and the page offers "Go to island".

`/island decline` drops the invite and tells the inviter. Expired invites are pruned by `SeenTick` (5 s) and both sides are told. `invite.seconds` = 60.

### 1.6 Leave, kick, promote, demote, disband

- **`/island leave`** (Member or Admin; the Owner is told to disband instead). Removes `k` from `members` and `admins`, drops `MEMBER_OF[k]`, and notifies the owner and members. A player standing on the co-op island is sent to their own island right away: `IslandCmd.go(..., k, true)` on their thread, which is the command thread. It is created from the template if they never had one.
- **`/island kick <name>`** (Owner). A `STRING` name matched against the members' stored names (case-insensitive), or a UUID or pkey, so it works while the member is offline. Same removal as leave. The kicked player gets "You were removed from Skyy's island co-op. /island takes you to your own island." If they stand on the island, `SendHomeTask` on the island's world thread sends them to their own island (UNVERIFIED: `go()` from a world-thread task instead of a command; the same components as the proven `RouteTask` path). Kicking a Trusted player → "Not a co-op member - use /island untrust".
- **`/island promote <name>` / `/island demote <name>`** (Owner). Member ↔ Admin (`admins=`). Both sides get a chat line.
- **`/island disband`** (Owner, repeat within 10 s: the SkyyGuilds disband pattern, proven in the beta). Only when the co-op has members. Clears `members` and `admins` and drops their `MEMBER_OF` entries. **Trusted, bans and settings stay.** Members standing on the island are sent to their own islands (`SendHomeTask`); the others get a chat line. Every former member's `island:<uuid>` is republished.

### 1.7 `/island reset` (Owner)

**Confirm twice.** `/island reset` prints the warning: "This deletes every block and chest on your island, including your co-op members' things. Members, trusted players, bans and settings are kept. Type /island reset again within 20 s to continue." The second run gives the final warning, and the third run resets. On the page, the button reads "Reset island" → "Delete everything?" → "Really? Last click". The state lives in `CONFIRM[uuid] = { step, millis }`, and the 20 s window is `reset.confirmSeconds`.

**Refused when:** you are not the Owner of your home island; the island is being created (`CREATING`); `profile:busy:<uuid>` is set; or the cooldown `reset.cooldownHours` (default 24, `[SKYY?]`) has not passed. The cooldown stops repeated resets from farming starter kits.

**How (a new world, not a wipe in place):**
1. `newName = "skyy-island-" + ownerKey + "-r" + (resets + 1)`. Bump N while `Universe.isWorldLoadable(newName)` is true.
2. If the old world is loaded: `oldWorld.execute(EvacTask)`. The owner's own command thread runs it inline when the owner stands there. It sends every player on the old island except the owner to the hub with `HubCmd.sendToHub`, with the line "Skyy reset this island - /island takes members to the new one".
3. On the owner's thread: `CREATING.put(ownerKey)`. Write `world.prev=<old name>`, `resets=N`, `resetAt=<millis>`, and remove `kit`. Then `InstancesPlugin.get().spawnInstance("SkyyIsland", newName, from, ret).thenCompose(new IslandBuild(ownerKey))`. This is the exact 0.4.5 creation chain: `setWorldName` writes `world=newName`, then the starter island blocks, the tint and the **fresh starter kit** (FillTask), and a publish. Finish with `teleportPlayerToLoadingInstance(ref, store, f, ret, null)` for the owner.
4. Republish `island:<uuid>` for the owner and every online member, and message the members ("the island was reset - /island takes you there").
5. **The old world** empties and is unloaded by the template's `WorldEmpty` removal condition (`DeleteOnRemove=false`). Its folder stays in the universe worlds folder as a backup: an admin can restore it by putting the old name back into `world=`. `world.prev` stays in `ISLAND_WORLDS` / `WORLD_OWNER`, so the old world stays protected if it is ever loaded. An `ArrivalTask` in a `world.prev` world sends the player to the hub ("This island was reset"). That covers someone who was mid-teleport during a reset.
6. The island file's settings re-apply to the new world on arrival (PvP, spawning; biome and weather in slice B). The same idempotent arrival apply is used after an unload.

**Why a new name instead of deleting the old world first:** `spawnInstance` copies the template only into a path that has no loaded world (0.1 bytecode notes). Deleting a loaded world's region files on Windows risks file locks. Clients cache chunks per world (the black-grass episode), and a new world name sidesteps that too. The old world doubles as a backup. Engine facts, VERIFIED this pass: `Universe.removeWorld(name)` dispatches a cancellable `RemoveWorldEvent`, stops the world, drops it from the maps, then `World.validateDeleteOnRemove()` → `deleteWorldFromDisk()` only when `WorldConfig.isDeleteOnRemove()`. That call moves the folder to `Universe.getWorldsDeletedPath()/<name>-<random>` and deletes it. The optional "delete the old world" setting is **Later** (4.8).

### 1.8 Example (Skyy + Wesley)

1. Skyy (profile Strawberry) runs `/island invite Wesley`. Wesley (profile Apple) runs `/island accept`. From now on Wesley's `/island` goes to Skyy's island, and Wesley can open Skyy's chests.
2. Skyy runs `/island promote Wesley`. Wesley opens `/island menu` and turns Visitors to Friends only. Wesley has no Kick, Disband or Reset buttons.
3. Wesley switches to profile Banana and lands on Banana's own island. On Skyy's island Wesley-Banana is a visitor. Wesley switches back to Apple, and `/island` goes to Skyy's island again.
4. Skyy runs `/island trust Kai`. Kai may build on Skyy's island, but Kai's `/island` still goes to Kai's own island, and Kai can't open chests.
5. Wesley runs `/island leave`. Wesley is back on Apple's own island, and everything Wesley had there is still in place.

---

## 2. What the SkyBlock plugins do

My own summary of the plugin docs (sources in section 13).

| Plugin | Roles | Team flow | Settings menu | Visitor control | Biome |
|---|---|---|---|---|---|
| **BentoBox / BSkyBlock** | Banned < Visitor < Coop (session, ends when the granter logs off) < Trusted (persistent) < Member < Sub-owner < Owner | `team invite` + `team accept`, `team leave`, `team kick`, `team setowner`; members share one island | `/island settings`: the owner edits and others see it read-only. Each flag icon **cycles the minimum rank** on click. On/off "settings flags" (PvP, spawning) sit apart from the rank flags. | `ALLOW_VISITS_FLAG`, `LOCK`, `/island ban/unban/banlist`, visit ping to members | Biomes addon, with unlock and use costs |
| **SuperiorSkyblock2** | Guest < Coop < Member < Moderator < Admin < Leader, plus per-player overrides | invite/accept, promote/demote, kick, disband | Separate menus for Settings, Permissions (role x privilege grid), Biomes, Warps, Members, Bank, Bans, Visitors | `/island open`/`close`, `expel`, `ban`/`pardon`; turning PvP on sends visitors away first | Biome menu |
| **IridiumSkyblock** | A "trust" tier below members | invite/join | Bank, upgrades | Trust / untrust | Biome shop |
| **Hypixel SkyBlock** | Owner, co-op members (removing one needs a vote), guests | co-op invite + accept; every member's island **is** the co-op island | Island Settings page | Visits by Anyone / Friends / Guild; guest cap; guest kick; `/guestlocation` | Biome customisation as a reward |

**Common flag defaults** (BentoBox shipped defaults, SuperiorSkyblock2 privileges): place / break / chests / furnaces / beds / animals = Member; doors = Visitor; hostile mobs = Visitor; PvP off; visits on; settings = Owner.

**Five things every system agrees on:**
1. Visitors look but don't touch by default.
2. "Can anyone visit" is its own switch, separate from build rights.
3. An owner can see who is on the island now and remove one person in one click.
4. Expel (temporary) and ban (persistent) are two separate actions.
5. The biome is a reward or cost, not a free base setting.

The two team systems (BentoBox, Hypixel) also agree that **joining a team changes which island is "yours"**, and that a lighter "trusted/coop" tier exists for helpers. That is exactly Skyy's split between Member and Trusted.

---

## 3. Permission flags

### 3.1 Semantics (BentoBox "minimum rank")
Each flag stores one **minimum role**: `visitor | trusted | member | admin | owner`. A role may do it when `rank >= min`, and the Owner is always allowed. The grid (7.4) shows YES/NO cells for Visitor, Trusted, Member and Admin. **Clicking a cell for role R:** if R is allowed now, set `min = R + 1` (denies R and every rank below it). If R is denied now, set `min = R` (allows R and every rank above it). It is always one click, and the grid can never reach an impossible state like "visitors may but members may not".

### 3.2 The 14 flags, defaults and hooks

| # | id | Grid label (hint line) | Default min | Visitor / Trusted / Member / Admin | 0.4.5 behaviour | Engine hook (all VERIFIED) |
|---|---|---|---|---|---|---|
| 0 | `build` | Place blocks | trusted | no / yes / yes / yes | members only | `PlaceBlockEvent` (CancellableEcsEvent) |
| 1 | `break` | Break blocks (hitting and breaking) | trusted | no / yes / yes / yes | members only | `BreakBlockEvent`, `DamageBlockEvent`, `UseBlockEvent$Pre` with `InteractionType.Primary` |
| 2 | `containers` | Chests & barrels (also breaking them) | member | no / no / yes / yes | members only | `UseBlockEvent$Pre` (ICancellableEcsEvent), block classified CONTAINER |
| 3 | `doors` | Doors, trapdoors, fence gates | visitor | yes / yes / yes / yes | everyone | `UseBlockEvent$Pre`, `BlockType.isDoor()` |
| 4 | `crafting` | Crafting benches (Workbench, Armory, Builder's...) | trusted | no / yes / yes / yes | members only | `UseBlockEvent$Pre`, `getBench().getType() != Processing` |
| 5 | `processing` | Furnace, campfire, tannery, salvager (also breaking them) | member | no / no / yes / yes | members only | `UseBlockEvent$Pre`, `BenchType.Processing` |
| 6 | `beds` | Beds (sleep, set respawn) | **member** | no / no / yes / yes | members only | `UseBlockEvent$Pre`, `getBeds() != null` |
| 7 | `seats` | Chairs & benches (sit) | **visitor** | yes / yes / yes / yes | members only (**loosened**) | `UseBlockEvent$Pre`, `getSeats() != null` |
| 8 | `harvest` | Crops & plants (F-harvest, hitting crops) | **member** | no / no / yes / yes | members only | `UseBlockEvent$Pre` + `BreakBlockEvent` + `DamageBlockEvent` on crop/plant blocks |
| 9 | `animals` | Farm animals (hurt, interact, coops) | member | no / no / yes / yes | **not guarded** | `Damage` (DamageEventSystem, filter group) with an NPC victim in the animal list; `UseEntityEvent$Pre` on that NPC; coop block use |
| 10 | `mobs` | Fight hostile mobs | visitor | yes / yes / yes / yes | not guarded (same) | `Damage` with any other NPC victim |
| 11 | `pickup` | Pick up items | trusted | no / yes / yes / yes | members only | `InteractivelyPickupItemEvent` |
| 12 | `drop` | Drop items | trusted | no / yes / yes / yes | **not guarded** | `DropItemEvent$PlayerRequest` (CancellableEcsEvent, `Store.invoke(ref, ev)` on the dropper) |
| 13 | `other` | Lanterns, coffins, teleporters, other blocks | trusted | no / yes / yes / yes | members only | `UseBlockEvent$Pre`, anything not matched above |

**Trusted = a builder** (Skyy: "build permission only"): place, break, crafting benches, pickup and drop (needed to build), toggle blocks, doors, seats and mobs. They can't open chests or furnaces, harvest the farm, sleep, or touch animals. The first draft allowed Trusted to harvest and sleep; this revision moves both to Member. The owner can widen or narrow any of it in the grid.

Two pseudo-flags exist for the bridge only (not in the grid): `enter` (may this player be on the island now, 4.1) and `settings` (Owner or Admin, fixed).

### 3.3 Block classifier (exact, first match wins; javassist-safe)
Class `IslandPerms`, static methods. The type names are the fully qualified ones in 0.4.5's `BTY` and friends.
```java
// flag ids: BUILD=0 BREAK=1 CONTAINERS=2 DOORS=3 CRAFTING=4 PROCESSING=5 BEDS=6 SEATS=7 HARVEST=8 ANIMALS=9 MOBS=10 PICKUP=11 DROP=12 OTHER=13
public static boolean isCrop(BlockType bt) {                 // the engine's own NoHarvestUse test
  FarmingData f = bt.getFarming();
  return f != null && f.getStages() != null;                 // tilled soil has FarmingData but no stages -> not a crop
}
public static boolean isHarvestPlant(BlockType bt) {         // Aetherhaven isHarvestStyleBreak + a Plant_ filter
  if (isCrop(bt)) return true;
  BlockGathering g = bt.getGathering();
  return g != null && g.getHarvest() != null && String.valueOf(bt.getId()).startsWith("Plant_");
}
public static int containerKind(BlockType bt) {              // -1, CONTAINERS or PROCESSING
  Bench b = bt.getBench();
  if (b != null && b.getType() == BenchType.Processing) return PROCESSING;
  java.util.Map im = bt.getInteractions();
  Object rid = im == null ? null : im.get(InteractionType.Use);
  if (rid != null && String.valueOf(rid).indexOf("Container") >= 0) return CONTAINERS;   // Open_Container, Open_Treasure_Container
  return -1;
}
public static int useFlag(BlockType bt, InteractionType t) { // UseBlockEvent$Pre
  if (t == InteractionType.Primary) return BREAK;            // hitting a bed/treasure chest = breaking it
  if (t != InteractionType.Use && t != InteractionType.Secondary) return -1;   // collisions, pick: not guarded
  if (bt.isDoor()) return DOORS;                             // the engine's own NoDoorOpen test
  Bench b = bt.getBench();
  if (b != null) return b.getType() == BenchType.Processing ? PROCESSING : CRAFTING;
  if (bt.getBeds() != null) return BEDS;
  if (isCrop(bt)) return HARVEST;
  if (containerKind(bt) == CONTAINERS) return CONTAINERS;
  if (bt.getSeats() != null) return SEATS;
  if (String.valueOf(bt.getId()).startsWith("Coop_")) return ANIMALS;
  return OTHER;
}
public static int breakFlag(BlockType bt) { return isHarvestPlant(bt) ? HARVEST : BREAK; }   // Break + DamageBlock
```
**Extra rule (anti-loot):** a break, damage-block or Primary-use on a block with `containerKind(bt) >= 0` needs **both** `break` **and** that container flag. Breaking a chest drops its contents, so this stops a trusted builder from looting by breaking.

**Why this is exact (Assets.zip scan of every block item, parents resolved, VERIFIED):**
- 46 doors, trapdoors and fence gates carry `IsDoor: true` (`Use` = `Door` / `Door_Horizontal`).
- 46 containers have `Use` = `Open_Container`, plus 1 `Open_Treasure_Container`.
- Benches: `Bench.Type` is Crafting (Alchemy, Arcane, Armour, Cooking, Farming, Furniture, Loom, Trough, Weapon, WorkBench), DiagramCrafting (Armory), StructuralCrafting (Builders) or Processing (Campfire, Furnace, Salvage, Tannery). `BlockType.processConfig` puts the bench's root interaction under `InteractionType.Use`, so bench use goes through `UseBlockEvent$Pre` (bytecode).
- 15 beds have `Beds` + `Use` → inline `Bed` (and `Primary` → `Check_Can_Break_Respawn`).
- 31 seats have `Seats` + `Use` → `Block_Seat`.
- 103 blocks have `Farming`, 97 of them crops/saplings/cactus with stages. `Soil_Dirt_Tilled` has only a `SoilConfig`.
- 47 blocks have `Use` → inline `ChangeState` (lanterns, trophies). Coffins, `OpenCustomUI` blocks (Teleporter, Launchpad, spawner block), `Coop_Chicken` (`UseCoop`) and `Deco_Kweebec_Plush` are the rest. All of them go to OTHER, except the coop, which is ANIMALS.
- `UseBlockInteraction.doInteraction` fires the event only when `getInteractions().get(type)` exists (bytecode), so plain blocks never reach GuardUse.

**Harvest paths (VERIFIED):** the unarmed Use chain in `Server/Item/Unarmed/Interactions/Empty.json` is `UseBlock → (fail) UseEntity → (fail) BreakBlock {Harvest: true}`.
- Crops **with** a Use interaction fire `UseBlockEvent$Pre`. The engine's `NoHarvestUse` checks exactly `getFarming().getStages()`.
- Crops **without** one reach `BlockHarvestUtils.performPickupByInteraction`, which fires `BreakBlockEvent`.
- Hitting fires `DamageBlockEvent` and then `BreakBlockEvent` (`performBlockBreak`).

All three paths are covered.

### 3.4 Entity flags (animals / mobs)
- **Hurt:** a new class `GuardHurt extends com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem` (no-arg constructor), copied from the engine's `TriggerVolumeRuleSystems$DamageRuleFilter`:
  - `getGroup()` returns `DamageModule.get().getFilterDamageGroup()`, so it runs before the damage is applied.
  - `getQuery()` returns `NPCEntity.getComponentType()`.
  - `handle(int, ArchetypeChunk, Store, CommandBuffer, EcsEvent)` casts to `Damage`. If `getSource()` is a `Damage$EntitySource` (arrows count too: `Damage$ProjectileSource` extends it), it takes `getRef()` and reads the `PlayerRef` through `buf.getComponent(ref, PlayerRef.getComponentType())`. For a player it checks `animals` or `mobs` for that player's role and calls `d.setCancelled(true)` on a deny.
  - Victim class: `NPCEntity.getRoleName()`. It is an **animal** when it is in `ANIMALS`, a comma list the build script reads from `Assets.zip` at build time: every role under `Server/NPC/Roles/Creature/Livestock/` (70, including all `Tamed_*`) and `Creature/Critter/` (7), plus config `animals.extra=`. Everything else is a mob.
- **Use (interact with an animal):** `GuardUseEntity` on `UseEntityEvent$Pre` (ICancellableEcsEvent, invoked on the **player** by `UseEntityInteraction.firstRun`, bytecode). The target is `getTargetEntity()`. An animal needs `animals`; any other NPC needs `other`.
- **Not guardable (VERIFIED gap):** milking and shearing with a bucket or shears run `ContextualUseNPCInteraction`, which fires **no** event. Harmless, and documented.
- **PvP** is not a flag. The engine's `DamageSystems$PlayerDamageFilterSystem` reads `WorldConfig.isPvpEnabled()` (4.2).

### 3.5 "Levers and buttons": not a thing in this Hytale build (VERIFIED)
`Deco_Lever` and `Deco_Plate` have **no BlockType interactions**. The lever's `"Secondary": "Block_Secondary"` sits on the *item* (placing it), and there is no redstone-style mechanism. The toggle blocks (`ChangeState`) fall under `other`. If a later Hytale update adds working switches, they land in `other` automatically.

### 3.6 Guard classes (ONE registerSystem per class)
The 0.4.5 base `GuardSystem` loses `exempt()` and gains `int flagFor(EcsEvent)` (-1 = not guarded) and `int extraFlag(EcsEvent)` (-1 = none). `handle()` computes `rank = IslandPerms.rank(ownerKey, uuid)` and allows when `rank >= min[flag] && (extra < 0 || rank >= min[extra])`. On a deny it cancels through `ICancellableEcsEvent.setCancelled(true)` (covers both base types) and sends a throttled message (the existing WARNED map, 3 s) naming the rule, e.g. `[Island] Chests & barrels on Skyy's island: members only.` The other-profile text stays ("This island belongs to another of your profiles" for the owner; "You are a co-op member here on your profile Apple - switch to it" for a member on the wrong profile).

| Class | Event | flagFor / extraFlag |
|---|---|---|
| GuardDamage (0.3) | DamageBlockEvent | `breakFlag(bt)` / `containerKind(bt)` |
| GuardBreak (0.3) | BreakBlockEvent | `breakFlag(bt)` / `containerKind(bt)` |
| GuardPlace (0.3) | PlaceBlockEvent | BUILD / -1 |
| GuardPickup (0.3) | InteractivelyPickupItemEvent | PICKUP / -1 |
| GuardUse (0.4.4) | UseBlockEvent$Pre | `useFlag(bt, type)` / Primary: `containerKind(bt)` |
| **GuardDrop** (new) | DropItemEvent$PlayerRequest | DROP / -1. **Hard deny** for the owner on another profile (10.2) |
| **GuardUseEntity** (new) | UseEntityEvent$Pre | ANIMALS or OTHER / -1 |
| **GuardHurt** (new, extends DamageEventSystem) | Damage (filter group) | ANIMALS or MOBS |

`IslandPerms.rank(String ownerKey, UUID who)`, in this order:
1. -1 if the UUID is in `banned`.
2. 4 if `pkey(who)` equals the owner key.
3. 0 (visitor) when `who` is the owner on another profile (hard-deny drop, own message).
4. 3 if the pkey is in `admins`.
5. 2 if it is in `members`.
6. 1 if it is in `trusted`.
7. Otherwise 0.

It reads only the settings cache (9.1).

---

## 4. Island settings

Who changes them: Owner and Admin. Members see them read-only.

| Setting | Values | Default | Hook | When |
|---|---|---|---|---|
| Who may visit | Public / Friends only (members + trusted) / Closed (members only) | Public (= 0.4.x) | custom: `/island visit`, arrival check, 5 s sweep | **Now** |
| Visitor limit | 1..`visit.limitMax` (config, default 10) | 5 `[SKYY?]` | `World.getPlayerRefs()` (thread-safe) | **Now** |
| Expel | one visitor or trusted player to the hub + a 60 s re-entry block | n/a | `HubCmd.sendToHub` on the island's world thread | **Now** |
| Ban list | UUIDs, max 100 | empty | custom | **Now** |
| Lock / unlock | lock = Closed, and remember the previous mode | n/a | alias of "Who may visit" | **Now** |
| Visit ping | on/off | on | chat to the online owner + members | **Now** |
| PvP | on/off | off (= template) | `WorldConfig.setPvpEnabled` + `markChanged` | **Now** |
| Mob spawning | on/off | off (= template) | `WorldConfig.setSpawningNPC` + `markChanged` | **Now** |
| Biome | 11 presets | Void Sky (= today) | tint + Environment + live resend | **Now, slice B** |
| Weather lock | biome default + 7 dry weathers | biome default | WeatherResource + WorldConfig | **Now, slice B** |
| Visitor landing point | island spawn / a point you set | island spawn | 5-arg teleport | **Now, slice B** |
| Time lock | n/a | n/a | exists, see 4.8 | **Later** |

### 4.1 Visitors: mode, limit, expel, ban, lock (all custom, no engine blocker)
- **Entry rule** `mayEnter(settings, rank, uuid, world)` is false when any of these holds:
  - the player is banned;
  - the mode is Closed and `rank < member`;
  - the mode is Friends and `rank < trusted`;
  - the player was expelled from this island less than 60 s ago (memory map `EXPELLED`, key `worldName|uuid`);
  - `rank == visitor` and the current visitor count is already at the limit.

  Server admins always pass. Members and admins always pass (they can't be banned; kick first).
- **Where it is checked:**
  1. **`IslandCmd.visit()`**, before calling `go()`, so a refused player never even loads the world.
  2. **Arrival:** `IslandReady` already hears `PlayerReadyEvent` on **every** world switch (0.2.1 fact). 0.5 keeps login routing for the first ready of a session. Every later ready schedules `ArrivalTask` (1.5 s, the RouteTask/RouteDispatch pattern onto the player's world thread). There:
     - a `world.prev` world (reset backup, 1.7) sends the player to the hub;
     - `!mayEnter` → `HubCmd.sendToHub(...)` plus a reason;
     - a visitor gets the welcome line (`Visiting Skyy's island - PvP off - you may: doors, seats, hostile mobs`) and the visit ping goes out;
     - the arrival re-tint + resend runs (section 5);
     - the island's WorldConfig settings are re-applied idempotently.
  3. **Sweep:** `SeenTick` (already every 5 s) dispatches `SweepTask` with `w.execute(...)` to each loaded island world that has players. On that world thread it walks `w.getPlayerRefs()` and expels anyone who fails `mayEnter` without the limit clause. This catches `/tpa`, vanilla `/teleport`, respawns, profile switches while standing on the island, kicks, and ban/lock changes.
- **Visitor count** = players in `w.getPlayerRefs()` with rank visitor. VERIFIED: `World.playerRefs = Collections.unmodifiableCollection(ConcurrentHashMap.values())`, readable from any thread. The limit is enforced on arrival, give or take one on simultaneous arrivals. Lowering it never expels anyone already there (SkyBlock norm).
- **Expel** uses the proven login-routing call `HubCmd.sendToHub(store, ref, pr, world)` (adds a `Teleport` component on the target's world thread). `InstancesPlugin.exitInstance` is not used: it throws when there is no return point, and its return point may be another island.
- **Ban** of someone inside → immediate expel. **Lock / Closed / Friends** while visitors are inside → the same sweep runs at once.

### 4.2 PvP (VERIFIED engine flag)
The vanilla `WorldConfigSetPvpCommand` pattern: `w.getWorldConfig().setPvpEnabled(b); w.getWorldConfig().markChanged();`. `WorldConfigSaveSystem` persists it to the island world's own `config.json`. It is per world, so per island. **Turning PvP on expels current visitors** (rank 0) with a message, as SuperiorSkyblock2 does to stop PvP traps. Trusted players and members stay and get a warning. Visitors arriving later see "PvP is ON here" in the welcome line. The island file keeps `pvp=` too, so a reset world gets it back on arrival.

### 4.3 Mob spawning (VERIFIED engine flag, biome-dependent)
`setSpawningNPC(b)` + `markChanged()` (vanilla `SpawnCommand$DisableCommand`). It is read by `WorldSpawningSystem`, `SpawnJobSystem`, `SpawnControllerSystem` and `SpawnMarkerSystems$Ticking`. **What spawns comes from the Environment:** `Env_Default_Void` (today's biome) appears in **zero** spawn rules, so spawning ON does nothing on a Void Sky island. The UI says "needs a biome with wildlife" (slice B). Turning it off does not remove mobs already spawned. One switch covers animals and monsters together.

### 4.4 Biome (slice B, feasible now): presets, how it is applied, persistence

**Presets** (tint = `Default.Colors[0/1]` of the matching Orbis tile in `Server/World/Default/Zones/*`; wildlife = NPC ids whose `Server/NPC/Spawn/World/*.json` lists that environment; all VERIFIED from Assets.zip):

| key | Label | Grass tint (ARGB int) | Environment | Weather pool | Wildlife when spawning is on |
|---|---|---|---|---|---|
| `void` | Void Sky (default) | #5b9e28 (-10772952, 0.4.2 GRASS) | Env_Default_Void | Default_Void only | none (0 rules) |
| `plains` | Plains | #5b9e28 | Env_Zone1_Plains | Zone1 sunny, fireflies, cloudy, fog, rain, storm | cows, sheep, pigs, chickens, horses, deer, foxes, rabbits; wolves; void larvae at night (28 ids) |
| `forest` | Forest | #3b8e32 (-12874190) | Env_Zone1_Forests | inherits Env_Zone1 | boars, bunnies, bears, owls, birds (22) |
| `autumn` | Autumn | #c07321 (-4164831) | Env_Zone1_Autumn | autumn windy, rain, sunny | Zone1 forest set (22) |
| `azure` | Azure Forest | #2f868a (-13662582) | Env_Zone1_Azure | inherits Env_Zone1 | 26 ids |
| `swamp` | Swamp | #445f0f (-12296433) | Env_Zone1_Swamps | swamp, swamp fog/rain, fireflies | wild pigs, frogs, fen stalker, skeletons (20) |
| `savanna` | Savanna | #d7be35 (-2638283) | Env_Zone2_Savanna | inherits Env_Zone2 (sunny, blazing, cloudy, thunder) | antelope, hyenas, meerkats, sand skeletons (17) |
| `oasis` | Desert Oasis | #b9b828 (-4605912) | Env_Zone2_Oasis | sunny, blazing, haze, cloudy | crocodiles, flamingos, sand lizards, sand skeletons (19) |
| `tundra` | Tundra | #487e4d (-12026291) | Env_Zone3_Tundra | inherits Env_Zone3 | cows, moose, wild pigs, skeleton scouts (14) |
| `glacial` | Glacial | #699587 (-9857657) | Env_Zone3_Glacial | snow, snow storm, northern lights | polar bears, bison, penguins, frost skeletons (21) |
| `wastes` | Ash Wastes | #786133 (-8888013) | Env_Zone4_Wastes | inherits Env_Zone4 | undead cows, skeleton horses, burnt skeletons, wraiths (7) |

The engine keeps colour and "biome" apart. **Colour** is a per-column tint (`BlockChunk.setTint`). The **Environment** is a per-block index (`BlockChunk.setEnvironment` / `EnvironmentChunk.setColumn`). The Environment drives the weather forecast, the water tint, the AmbienceFX conditions (48 ambience files key on `EnvironmentIds`) and the NPC spawn rules (96 `Server/NPC/Spawn/World/*.json` files list `Environments`). **Not possible:** Minecraft-style terrain per biome (the island's blocks stay as built), or authoring new Environment assets at runtime. We only pick from the 122 shipped ones. Natural (not forced) rain in Plains, Swamp and others waters crops the normal vanilla way, which is fine; only a *locked* rain would be an exploit.

**Apply (world thread; `BiomeApply.apply(World w, String key)`). Every call is VERIFIED; the sequence is the vanilla builder-tools `BuilderState.environment` plus `ChunkTintCommand`:**
```java
int idx = Environment.getAssetMap().getIndex(envId);      // Integer.MIN_VALUE = missing -> refuse (EnvironmentCommand does this check)
for (int cx = -R; cx <= R; cx++) for (int cz = -R; cz <= R; cz++) {        // R = config biome.radiusChunks, default 4
  WorldChunk c = w.getChunkIfLoaded(ChunkUtil.indexChunk(cx, cz));
  if (c == null) continue;
  BlockChunk bc = c.getBlockChunk();
  EnvironmentChunk ec = bc.getEnvironmentChunk();
  for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) { bc.setTint(x, z, argb); ec.setColumn(x, z, idx); }
  bc.setEnvironment(0, 0, 0, idx);   // nulls cachedEnvironmentsPacket + markNeedsSaving (bytecode); setTint nulls the tint/column packets
  c.markNeedsSaving();
  w.getNotificationHandler().updateChunkTints(c.getIndex());          // vanilla /chunk tint (section 5)
  w.getNotificationHandler().updateChunkEnvironments(c.getIndex());   // vanilla builder-tools /environment
}
WorldConfig cfg = w.getWorldConfig();                                  // future chunks of THIS island
cfg.setWorldGenProvider(new VoidWorldGenProvider(new com.hypixel.hytale.protocol.Color((byte) r, (byte) g, (byte) b), envId));
cfg.markChanged();
```
- `EnvironmentChunk.setColumn(x, z, idx)` rewrites a whole 320-block column in one call: 1,024 calls per chunk, about 80k for R=4. It keeps its own block counts (bytecode). **Fallback** if the in-game test shows stale columns: the builder-tools per-block loop `bc.setEnvironment(x, y, z, idx)`, restricted to y 64..255.
- The world's live generator is not swapped. New chunks generated before the next reload use the old values; the arrival re-apply fixes them.
- **Arrival re-apply:** section 5's `TintFix` generalises to `BiomeApply.fixChunk(chunk, argb, idx)`. For each loaded chunk within R, when `bc.getTint(8, 8) != argb` or `bc.getEnvironment(8, 128, 8) != idx`, it applies to that chunk and resends. `FillTask` uses the island's biome tint instead of the `GRASS` constant.
- **Cost / gating** (every plugin treats the biome as a reward): ship `biome.cost=0` (coins via the SkyyCoins bridge `coins:fn:take`; a refusal means no change) and `biome.cooldownSeconds=60`. Admins trim the list with `biomes=`. Tying unlocks to Exploration zone discovery is `[SKYY?]`, later.

### 4.5 Weather lock (slice B; dry weathers only)
The vanilla `WeatherSetCommand.setForcedWeather(World, String, ComponentAccessor)` sequence (VERIFIED), on the island world thread with `store = w.getEntityStore().getStore()`:
`((WeatherResource) store.getResource(WeatherResource.getResourceType())).setForcedWeather(id); cfg.setForcedWeather(id); cfg.markChanged();`
- `id = null` means biome default (vanilla `WeatherResetCommand` passes null).
- `WeatherSystem$WorldAddedSystem` copies `getForcedWeather()` back into the resource when the world loads, so the lock survives an unload.

Choices (ids VERIFIED in `Server/Weathers/`): Biome default, Clear `Zone1_Sunny`, Fireflies `Zone1_Sunny_Fireflies`, Cloudy `Zone1_Cloudy_Medium`, Fog `Zone1_Foggy_Light`, Snow `Zone3_Snow`, Northern Lights `Zone3_Northern_Lights`, Skylands `Skylands_Sunny`.

**Excluded:** `Zone1_Rain`, `Zone1_Rain_Light`, `Zone1_Storm`, `Zone3_Rain`. `Server/Farming/Modifiers/Water.json` lists them as watering weathers (x2.5 growth), and `WaterGrowthModifierAsset.checkIfRaining` reads `WeatherResource.getForcedWeatherIndex()` (bytecode). A locked rain would be a permanent farm boost.

### 4.6 Visitor landing point (slice B; Hypixel `/guestlocation`)
"Set to where I stand" works only while the setter stands on the island world. It stores `visit.spawn=x,y,z,rx,ry,rz` (same format as `hub.properties`). In `IslandCmd.go()` for a visitor or trusted player, it calls `InstancesPlugin.teleportPlayerToLoadingInstance(ref, store, future, ret, spawnTransform)`. The 5-arg overload is VERIFIED. For an already loaded world, `future = CompletableFuture.completedFuture(w)` (UNVERIFIED in game; fallback = keep today's `teleportPlayerToInstance` and follow it with a `Teleport` component to the point). Members always land at the island spawn.

### 4.7 Visit ping
On a visitor's arrival, if `visit.notify=1`: message the owner (`Universe.get().getPlayer(ownerUuid)`, VERIFIED) and the online members: `[Island] Steve is visiting your island. /island menu to expel or ban.` At most one ping per visitor per 60 s.

### 4.8 Later (with the reason)
- **Time lock (always day or night).** The APIs are VERIFIED: `WorldTimeResource.setDayTime(hour/24.0, world, store)` + `WorldConfig.setGameTimePaused(true)` + `markChanged()`, the vanilla `/time` + `/pausetime` pattern. **But** `FarmingSystems$Ticking` (soil, coops), `BenchSystems$ProcessingBenchTick` (furnaces) and `WaterGrowthModifierAsset` read `WorldTimeResource.getGameTime()` (bytecode). Pausing probably freezes furnaces, crops and coops on that island. A night skip speeds them up instead. Skyy picks one first. Day *length* has no live setter, so it is **not possible**.
- **Visits while the owner is offline, island warps list, "visit a random public island".** `/island visit` takes `PLAYER_REF` (online only). Members don't need this: their `/island` loads the co-op island while the owner is offline.
- **Leader transfer** (`/island transfer`). An island is one profile's file, so a transfer means moving the file to another pkey and re-keying `WORLD_OWNER`. It is possible, but not asked for.
- **Delete the old world on reset** (`reset.deleteOldWorld`). `WorldConfig.setDeleteOnRemove(true)` + `markChanged()` before the old world empties makes the engine move it to `worlds-deleted/` and delete it (bytecode, 1.7). The default keeps it as a backup; add the switch when disk space matters.
- **A member vote to kick** (Hypixel), **party / guild visit sources** (SkyyParty 0.1.3 publishes `party:fn:members`; SkyyGuilds publishes `guild:<uuid>`: a "Friends" mode that includes the party and guild is a small follow-up), **visitor keep-inventory** (world-wide `setDeathConfigOverride`, touches the death-penalty design), **split animal/monster spawning** (one engine boolean), **fire spread**, **custom roles / per-player overrides**, **admin `/island admin settings <player>`**, **island size border** (belongs with the size tiers).

---

## 5. Grass colour without re-entering (tint resend)

**The bug** (HANDOFF log 2026-09-24 06:50): the arrival re-tint ran ("re-tinted 25600 columns"), but the client kept showing black grass until `/hub` then `/island`.

**Cause (0.4.5 script + bytecode, VERIFIED):** `RelightNow` → `FillTask.tintChunk` only calls `BlockChunk.setTint(x, z, GRASS)` and `markNeedsSaving()`. `setTint` nulls the chunk's `cachedColumnPacket` and `cachedTintmapPacket` (bytecode), so a client that loads the chunk **later** gets green. Nothing is sent to a client that **already has** the chunk. Re-entering makes the client load the chunks again, which is why it fixed the grass.

**Fix (VERIFIED calls; the vanilla `/chunk tint` pattern):** after re-tinting a chunk (`tintChunk` returned > 0), call
```java
world.getNotificationHandler().updateChunkTints(chunk.getIndex());
```
Bytecode: `WorldNotificationHandler.updateChunkTints(long)` copies `world.getPlayerRefs()`, takes `BlockChunk.getCachedTintsPacket()` (rebuilt, because `setTint` nulled it), and in `lambda$updateChunkTints$0` writes it to every player whose `ChunkTracker.isLoaded(index)`. `ChunkTintCommand` calls `setTint` and then `updateChunkTints` (constant pool). Cost: one small packet per re-tinted chunk per player in that world. Nothing is sent when no column changed.

**Timing fix:** 0.4.5 `RelightTask` runs 4 s after the `/island` **command** and looks the world up by name. When the island was unloaded and still loading, `getWorld` returns null and that arrival's re-tint is skipped. 0.5 runs `TintFix` from `ArrivalTask`, when `PlayerReadyEvent` says the player is in the island world: +1.5 s on the world thread, then a second pass at +6 s for chunks that loaded late. Each pass touches only chunks within 2 chunks whose tint is wrong, so the second pass costs nothing when all is green. The relight call (`invalidateLightInChunk`) and the late starter-kit check stay in `RelightNow` as today.

**Fallback (VERIFIED, heavier), config `tint.resend=tints|chunk|off` (default `tints`):**
- `chunk`: `world.getNotificationHandler().updateChunk(index)`, which calls `pr.getChunkTracker().removeForReload(index)` for every player in the world (bytecode). The whole chunk column is sent again, which is what re-entering does, one chunk at a time.
- A manual check for the test: vanilla `/chunk resend` (`ChunkResendCommand`: `ChunkTracker.clear()` + a `ClearChunks` packet, so every chunk is re-sent to the caller; operator command). If it makes the grass green, `tint.resend=chunk` will too.

The same resend goes into `FillTask` (harmless at creation) and `BiomeApply` (with `updateChunkEnvironments`). **UNVERIFIED in game:** that the client repaints already-rendered grass from the tint packet alone. Vanilla `/chunk tint` relies on it, so it is expected.

---

## 6. Defaults and migration

**A new island starts with:** Public visits, limit 5, visit ping on, PvP off, spawning off, biome Void Sky, weather biome default, no landing point, and the flags from 3.2. Visitors may walk around, open doors, sit and fight hostile mobs. Trusted players build (place, break, benches, pickup, drop, toggle blocks). Members and admins do everything, including chests, furnaces, crops, beds and animals.

**All defaults live in `Skyy_SkyyIslands/config.properties`** (`defaults.perm.<id>=`, `defaults.visit.mode=` ...). The file is written with these values on first run, as SkyySkills does with `xp.properties`. A key missing from an island file means "use the config default". A server builder can therefore fix a bad default for every island that never touched that setting.

**Migration of 0.4.x islands (at plugin setup, before any player can connect):**
- `loadIslandWorlds()` reads each island file. If the file has no `v=5`, it copies the file to `<key>.properties.v4bak`, then moves every `members=` entry into `trusted=` and writes `v=5`. It logs "migrated N build-rights entries to Trusted in <key>". Reason: in 0.4.x, `/island invite` meant **build rights**, which is Trusted now. Turning those entries into co-op members would silently move their `/island` to someone else's island and make their own island dormant. Example: the beta's "F: /island invite S" would take Skyy's `/island` to Wesley's island.
- Entries are bare UUIDs, which are each player's profile-1 key (`tools/PROFILES-CONTRACT.md`). They stay valid as profile-1 Trusted entries. In 0.4.x membership covered all of that player's profiles; now it covers profile 1 only. That is the anti-transfer rule, and the owner can re-trust them on another profile.
- The in-game changelog line: "Island 0.5: /island invite now asks your friend to JOIN your island as a co-op member (/island accept). Old build-rights invites are now Trusted (build only). Use /island trust for helpers."
- Flag behaviour changes for visitors versus 0.4.5: **seats** allowed; **animals** guarded; **drop** guarded (trusted+). Old build-rights players become Trusted, so they lose chests, furnaces, crops and beds until the owner invites them as members `[SKYY?]`.
- The world `config.json` of old islands already has `IsPvpEnabled: false`, `IsSpawningNPC: false` and the Void environment. Nothing to change.
- Nobody is Member, Admin or Banned after the upgrade.

---

## 7. UI: the island menu page (`/island menu`)

### 7.1 Frame (inline only; SkyyGuilds / SkyyProfiles page pattern; HANDOFF section 2)
- Class `IslandMenuPage extends com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage`, constructor `super(pr, CustomPageLifetime.CanDismiss)`, `public void build(Ref, UICommandBuilder, UIEventBuilder, Store)`, `public void handleDataEvent(Ref, Store, String)`. Opened with `player.getPageManager().openCustomPage(ref, store, page)` from the `/island menu` command (the player's world thread). SkyyMenu's island button dispatches `/island menu` (shared contract), and the page opens directly: SkyyMenu 0.1.2 does not close itself before a page command.
- Root: `Group #SkyyIsRoot { Anchor: (Width: 1240, Height: 860); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }`. Only Width/Height in the root anchor. **Big and readable:** title FontSize 24, section heads 18 bold, row text 16, hints 13, buttons 44-56 px tall.
- Header: `Skyy's Island` + profile label (`IslandStore.profileLabel`) + `Your role: Owner` (coloured: Owner gold, Admin purple, Member green, Trusted blue).
- **Tab row:** five `TextButton`s of 228 x 46: `#SkyyIsTabOv` "Overview", `#SkyyIsTabMem` "Members", `#SkyyIsTabPerm` "Permissions", `#SkyyIsTabVis` "Visitors", `#SkyyIsTabIsl` "Island". Payloads `tabov`, `tabmem`, `tabperm`, `tabvis`, `tabisl`. The active tab uses the gold style.
- Body `#SkyyIsBody` (Height 640). Footer: `Label #SkyyIsInfo` (status line for results and errors) and `TextButton #SkyyIsClose`.
- **Rules:**
  - No underscores in ids (`#SkyyIsPc03v`).
  - Every click is `ev.addEventBinding(CustomUIEventBindingType.Activating, "#Id", EventData.of("a", "payload"))`, matched in `handleDataEvent` with `data.indexOf("payload\"")`. Payloads are letters and digits only.
  - Every click ends in `rebuild()`. No MouseEntered/MouseExited handlers, no timers, no periodic updates: lists refresh on a click or the `Refresh` button.
  - Never close the page right before opening another page. "Go" buttons (Go to island, Create my island) run `IslandCmd.go(...)` first and then close the page with `getPageManager().setPage(ref, store, Page.None)`, the SkyyMenu 0.1.2 order ("act, then close"), which is verified in game.
  - **Every click re-checks the clicker's rank** on the current file state. The page shows only the buttons the rank allows, but state may have changed since the build.
  - Names pass through the `safe()` sanitiser (SkyyProfiles).
  - Destructive buttons take extra clicks (page field `confirm`, cleared on any other click): Kick, Disband, Leave, Ban and Reset to defaults need 2; Reset island needs 3 (1.7).

### 7.2 Overview tab
- **No island and no co-op:** "You have no island yet" + a big `#SkyyIsCreate` "Create my island" (runs `go(k, true)`, then closes).
- **Island box:** owner name, the co-op size `Members 2/5`, `Trusted 3`, `Visitors now 1` (when loaded), `Visits: Public`, `PvP: off`, `Biome: Void Sky` (slice B), and the world loaded or not.
- `#SkyyIsGo` "Go to island" (Owner, Admin, Member).
- **Pending invite box** (when the viewer has one): "Skyy invited you to join their island - 42 s left" + `#SkyyIsAcc` Accept + `#SkyyIsDec` Decline. When accept would be refused (1.5 checks), the box shows the reason instead of Accept, and Decline still works.
- **Owner danger box:** `#SkyyIsDisb` "Disband co-op" (2 clicks, only with members) and `#SkyyIsReset` "Reset island" (3 clicks, with the cooldown shown when it applies).
- **Member / Admin:** `#SkyyIsLeave` "Leave island" (2 clicks) and the line "Your own island stays saved and comes back when you leave."
- A help box with the command equivalents.

### 7.3 Members tab
- **Name box** (SkyySacks 0.7.3 / SkyyGuilds pattern, verified in game): `TextField #SkyyIsName { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 32; PlaceholderText: "Player name"; ... FontSize: 16 }` inside a 420 x 46 box.
  - `#SkyyIsInvBtn` "Invite to co-op": Owner, or an Admin (`coop.adminsInvite` default `true`).
  - `#SkyyIsTrustBtn` "Trust (build only)": Owner and Admin.
  - Both buttons send `EventData.of("a", "invite" | "trust").append("@IsName", "#SkyyIsName.Value")`, read back with SkyyGuilds' `jsonStr`.
  - **Enter** (`Validating` binding with `EventData.of("a", "name").append(...)`) only keeps the typed name (`keepName`) and says "Click Invite or Trust". A box with two actions must not guess, the same rule as the guild Amount box.
  - The name is matched against online players: exact (ignoring case) first, then prefix (SkyyParty 0.1.3).
  - Members, Trusted players and Visitors don't see the box.
- **Co-op roster** (owner first, up to `coop.maxPlayers` rows of 48 px): an online dot, name, "(you)", the role, and "since <date>". The Owner sees `#SkyyIsPr<n>` Promote / `#SkyyIsDm<n>` Demote and `#SkyyIsKk<n>` Kick (2 clicks) on each member row.
- **Pending invites** (Owner, and an Admin): "Invited: Wesley (38 s)".
- **Trusted:** 2 columns x 6 rows per page, name + `#SkyyIsUt<n>` Untrust (Owner/Admin), with `#SkyyIsTp` / `#SkyyIsTn` Prev/Next.

### 7.4 Permissions tab (the grid)
- Header row: `What` (440 px) | `Visitor` | `Trusted` | `Member` | `Admin` (150 px each) | `Owner` (100 px, grey `always`).
- 14 rows x 40 px. The left cell stacks the label (16 bold) over its hint (12). The cells are `TextButton #SkyyIsPc<nn><r>` (`nn` = 00..13, `r` = v/t/m/a), with text `YES` (green `#2f6a3a`) or `NO` (red `#6a2f2f`) and payload `pc<nn><r>`. For a Member viewer the cells are plain labels (read-only) with the line "Only the owner and island admins can change these".
- The click rule is 3.1.
- Top right: `#SkyyIsPdef` "Reset to defaults" (2 clicks) and the legend "Click to allow or deny. Allowing a role also allows every role to its right."

### 7.5 Visitors tab
- "Who may visit": three 340 x 56 buttons: `#SkyyIsVm0` Public (anyone), `#SkyyIsVm1` Friends only (members + trusted), `#SkyyIsVm2` Closed (members only). Closing expels at once (4.1).
- Visitor limit: `#SkyyIsVlm` [-], a label with N, `#SkyyIsVlp` [+].
- Visit ping: toggle `#SkyyIsVn`.
- Landing point (slice B): `#SkyyIsVs1` "Set to where I stand" (greyed with an info line when you are not on the island) and `#SkyyIsVs0` "Use island spawn".
- "On the island now": up to 8 rows (name, role) with `#SkyyIsVe<n>` Expel, `#SkyyIsVt<n>` Trust and `#SkyyIsVb<n>` Ban (2 clicks). The page keeps the snapshot of UUIDs taken at build time. `#SkyyIsVr` Refresh.
- "Banned": up to 8 names with `#SkyyIsVu<n>` Unban, plus `#SkyyIsBp`/`#SkyyIsBn` paging.
- A Member viewer sees the lists with Expel only.

### 7.6 Island tab
- **PvP:** toggle `#SkyyIsIp`, hint "Turning PvP on sends visitors to the hub".
- **Mob spawning:** toggle `#SkyyIsIs`, hint "Needs a biome with wildlife - Void Sky has none".
- **Biome** (slice B): 11 cards in 2 rows. Each card is a 40 x 40 swatch `Group` (`Background: #rrggbb`) plus a 150 x 40 `TextButton #SkyyIsBi<nn>`; the current biome is highlighted, payload `bi<nn>`. Hint: "Changes grass colour, sky and weather, water colour, ambient sound and wildlife (when mob spawning is on). 60 s cooldown."
- **Weather** (slice B): cycle button `#SkyyIsIw`, hint "Rain and storms can't be locked (they water crops)".
- Slice B items are simply not added to the page until slice B is built.

---

## 8. Commands

All are subcommands of `/island` (alias `/is`). Each is an `AbstractPlayerCommand` with `setPermissionGroups(new String[] { "hytale:Adventurer" })`, and so is every usage variant. They take required arguments only, because optional args are flags, not positional. The constructors are added before the `IslandCmd` constructor that calls `addSubCommand(new ...)` (javassist order, as in 0.4.5). `STRING` names match the island's stored `name.<key>` entries case-insensitively, and a UUID or pkey works too. That is how an offline player can be kicked, promoted, untrusted or unbanned without a network lookup. "Home island" = 1.3.

| Command | Args | Who (on the home island) | Does |
|---|---|---|---|
| `/island` | none | anyone | go to your home island (creates your own the first time) |
| `/island home` (alias `go`) | none | anyone | same |
| `/island info` | none | anyone | home island, owner, your role, members n/max, trusted n, world loaded, the world you are in |
| `/island menu` (aliases `settings`, `options`) | none | anyone | opens the island page (section 7) |
| `/island visit <player>` (alias `warp`) | `PLAYER_REF` | anyone | the target's home island, with the entry check (4.1) and the landing point (slice B) |
| `/island invite <player>` (alias `add`) | `PLAYER_REF` | Owner, and Admin (`coop.adminsInvite` default `true`) | co-op invite, 60 s (1.5) |
| `/island accept` | none | the invited player | join with the active profile (1.5) |
| `/island decline` | none | the invited player | refuse |
| `/island leave` | none | Member, Admin | leave the co-op; you go back to your own island (1.6) |
| `/island kick <name>` (alias `remove`) | `STRING` | Owner | remove a member or admin (1.6) |
| `/island promote <name>` | `STRING` | Owner | Member → Admin |
| `/island demote <name>` | `STRING` | Owner | Admin → Member |
| `/island disband` | none | Owner, repeat within 10 s | end the co-op; members go back to their own islands (1.6) |
| `/island trust <player>` | `PLAYER_REF` | Owner, Admin | build rights (Trusted), max 20; refuses members, banned players and yourself |
| `/island untrust <name>` | `STRING` | Owner, Admin | |
| `/island reset` | none | Owner, 3 runs within 20 s each | wipe + rebuild from the template with a fresh starter kit (1.7) |
| `/island expel <player>` | `PLAYER_REF` | Owner, Admin, Member (of the island you stand on, else your home island) | a visitor or trusted player standing there → hub + 60 s block |
| `/island ban <player>` | `PLAYER_REF` | Owner, Admin | refuses members ("the owner must kick first") and yourself; removes trust; expels |
| `/island unban <name>` | `STRING` | Owner, Admin | |
| `/island bans` (alias `banlist`) | none | Owner, Admin, Member | lists bans in chat |
| `/island lock` / `/island unlock` | none | Owner, Admin | mode → Closed (saves the previous mode) + sweep / restore it |

The old flag form `/island --action invite|visit|info|home --player X` keeps working; invite now sends a co-op invite. `/hub` and `/sethub` are unchanged. The `/island` root description lists the subcommands, and `/island help` is not needed (the page has the help box).

**Follow-ups for other mods** (each its own build, none needed for 0.5 to work):
- **SkyyMenu** (shared contract): an "Island" button that dispatches `/island menu`. In the Players view, the 0.1.2 "Give Island Build Rights" action dispatches `island invite %P`: change it to `island trust %P` and add "Invite to your island (co-op)" = `island invite %P`. Until then a click sends a co-op invite, which is harmless because it needs `/island accept`. The Mods-list text for SkyyIslands needs the new command list.
- **SkyyEssentials 0.1.1:** `/tpa` and `/tpahere` into an island world should ask `island:perm:fn` for `enter` before teleporting. Until then the arrival check and the sweep expel within about 5 s.
- **SkyyMinions** (future): asks `containers`. **SkyyHud** (later): "Visiting X - PvP off" from `island:role:fn`.

---

## 9. Storage and bridge

### 9.1 `Skyy_SkyyIslands/islands/<pkey>.properties` (0.4.x keys `world`, `created`, `kit` stay)
```
v=5                                      # 0.5 format; absent = 0.4.x file -> migrated at setup (section 6)
members=<pkey>,<pkey>                    # co-op members incl. admins (each = the member's profile key at accept)
admins=<pkey>                            # subset of members
trusted=<pkey>,...
banned=<uuid>,...
name.<pkey or uuid>=Wesley               # display names, refreshed whenever the player is seen
coopSince.<pkey>=<millis>
ownerName=Skyy
resets=0                                 # /island reset counter (new world = skyy-island-<key>-r<resets>)
resetAt=<millis>                         # cooldown
world.prev=<old world name>              # last reset's backup world (still protected if loaded)
settings=1                               # written on the first settings change; absent = pure config defaults
perm.build=trusted                       # one per flag id; values visitor|trusted|member|admin|owner
visit.mode=public                        # public|friends|closed
visit.prev=public                        # restored by /island unlock
visit.limit=5
visit.notify=1
visit.spawn=8.5,129.0,8.5,0,0,0          # slice B; absent = island SpawnProvider
pvp=0
spawning=0
biome=void                               # slice B
biome.changed=<millis>
weather=                                 # slice B; empty = biome default
```
- The file stays per profile (`IslandStore.read/write(key)`, atomic tmp + move, as in 0.4.x). **The owner's file is the only authority for membership.** A member's own file is never touched by joining or leaving.
- **Caches (memory):**
  - `IslandStore.SETTINGS` (ConcurrentHashMap, pkey → parsed `IslandSettings`: `int[] perm`, the mode, and the lists as comma strings). `write()` refreshes the entry, and the guards, bridge and page read only the cache. 0.4.5 `isMember` reads the file from disk on every guarded event, and 0.5 adds hurt, use-entity and drop events.
  - `MEMBER_OF` (member pkey → owner key), built in `loadIslandWorlds()` from every v5 file and kept current by accept, leave, kick and disband. Hand-edit conflicts (one pkey in two islands) → the first file in name order wins, with a log warning.
  - `INVITES` (target UUID → invite), `CONFIRM` (UUID → step + time), `EXPELLED` (`world|uuid` → time).
  - `ISLAND_WORLDS` / `WORLD_OWNER` also hold `world.prev`.

### 9.2 `Skyy_SkyyIslands/config.properties` (admin, new; written with defaults on first run)
```
defaults.perm.build=trusted ... (all 14, section 3.2)
defaults.visit.mode=public
defaults.visit.limit=5
visit.limitMax=10
coop.maxPlayers=5                         # owner + 4. LOCKED 2026-09-25 (Skyy): 5 including the owner.
coop.adminsInvite=true                    # LOCKED 2026-09-25 (Skyy): Admins may invite. Was: false. SkyyIslands 0.5.2 still writes false.
invite.seconds=60
trusted.max=20
bans.max=100
expel.cooldownSeconds=60
reset.cooldownHours=24
reset.confirmSeconds=20
tint.resend=tints                         # tints | chunk | off (section 5)
biomes=void,plains,forest,autumn,azure,swamp,savanna,oasis,tundra,glacial,wastes
biome.cost=0
biome.cooldownSeconds=60
biome.radiusChunks=4
weathers=clear,fireflies,cloudy,fog,snow,aurora,skylands
animals.extra=                            # extra NPC role names that count as farm animals (pet mods)
```

### 9.3 Bridge (`System.getProperties().get("skyy.bridge")`, UUID-keyed per contract rule 3; the Functions are plain classes, no lambdas)
| Key | Value | Use |
|---|---|---|
| `island:<uuid>` | world name of the player's **home** island (the co-op island when they are a member; changed from "own island") | SkyyHud Zone widget ("Your Island"). Republished on accept, leave, kick, disband, reset and profile epoch changes |
| `island:perm:fn` | `Function` apply(`Object[] { UUID player, String worldName, String flag }`) → `Boolean`, or `null` when the world is not an island or the flag is unknown. Flags: the 14 ids + `enter` + `settings`. Server admins → TRUE. | "may this player do X here" |
| `island:role:fn` | `Function` apply(`Object[] { UUID, String worldName }`) → `"owner" | "admin" | "member" | "trusted" | "visitor" | "banned"` or null | HUD label, other mods |
| `island:owner:fn` | `Function` apply(`String worldName`) → owner pkey String (the owner UUID = its first 36 chars) or null | |
| `island:coop:fn` | `Function` apply(`UUID`) → `String[]` UUID strings of that player's home-island co-op, owner first (just the owner when solo; empty when they have no island) | minions, HUD, party-style features |
| `island:epoch` | `Long`, +1 on every membership or settings change of any island | cache invalidation for other mods |

---

## 10. Anti-exploit and edge cases

1. **Profiles stay separate.** Membership and trust are profile keys, and a player holds at most one role per island across all their profiles (1.4). A member on another profile is a visitor, just like the owner on another profile. That closes the "put it in a shared chest on profile A, take it out on profile B" route, and the drop-and-pickup variant through Trusted.
2. **Owner on another profile** is a visitor, and the `drop` flag is **hard-denied** for them whatever the grid says (no dropping on the profile-B island and picking up on A).
3. **Breaking a container or furnace needs break AND containers/processing** (3.3), because breaking drops the contents.
4. **One co-op per profile; a leader can't join another co-op** (1.4). Accept resolves the pkey once and refuses while `profile:busy` is set.
5. **Reset spam:** 24 h cooldown `[SKYY?]` and 3 runs to confirm. The starter kit is the only thing a reset gives.
6. **Reset with players on the island:** everyone but the owner goes to the hub first. Late arrivals in the old world are sent to the hub by `ArrivalTask` and the sweep. The old world unloads when empty and is kept as a backup.
7. **Kick/leave/disband while standing on the island:** the player goes to their own island. If that fails, they stay as a visitor and the sweep applies the visit mode.
8. **Visitors inside when settings change:** Closed, Friends or a ban → immediate sweep and expel. PvP on → visitors expelled. A lower limit only affects new arrivals. Flag changes apply on the next event (cache).
9. **Other ways in** (`/tpa`, vanilla `/teleport`, a respawn, logging in on the island): the arrival check on every `PlayerReadyEvent` plus the 5 s sweep. A login inside an island still routes to the hub first (0.2).
10. **Offline owners:** guards and settings come from the file and cache. Members reach the island through `/island`, which loads it with `addWorld` (the same path as your own island, proven). WorldConfig values persist in the island's own `config.json`; the arrival hook re-applies them.
11. **Expel is temporary** (60 s, memory). **Ban** is persistent and per person. Members can't be banned (kick first). Banning removes trust.
12. **Server admins** bypass everything and are never expelled.
13. **Farming boosts:** rain can't be locked, and the time lock is deferred.
14. **Milking and shearing** can't be guarded (no event). Pets from third-party mods count as hostile unless listed in `animals.extra`.
15. **Third-party remote-storage mods** (e.g. AutoStorage, whose `ClaimProtectionProvider` only knows SimpleClaims) could bypass the container guard. The pack should not ship them without an `island:perm:fn` compat.
16. **Names:** `name.<key>` is refreshed whenever the player is seen, so renamed players show their new name, and STRING commands match any stored name.
17. **Performance:** guards read the cache. The sweep touches only loaded islands with players. The tint fix touches at most 25 chunks per arrival and only resends changed ones.

---

## 11. Feasibility summary, build slices, UNVERIFIED

**Slice A (SkyyIslands 0.5, from 0.4.5):**
- the co-op model (1.1-1.6) and its commands;
- `/island reset` (1.7);
- the tint resend (section 5);
- the guards rework + GuardDrop / GuardUseEntity / GuardHurt (section 3);
- visitors (4.1), PvP, spawning and the visit ping;
- the island menu page with all five tabs, minus the slice B controls;
- storage, migration and the bridge.

**Slice B (same version if the build stays manageable, else 0.5.1):** biome presets (4.4), weather lock (4.5), visitor landing point (4.6). They are independent: slice A leaves the tint colour as the `GRASS` constant.

**Engine status:** every engine call in this spec is VERIFIED (bytecode, reflection, or already used by 0.4.5). The co-op model itself needs no new engine call.

**UNVERIFIED in game (test in section 12):**
1. The tint packet repaints already-rendered grass live (vanilla `/chunk tint` relies on it).
2. Reset: `spawnInstance` under a new name while the old world is loaded; teleporting the owner off the old island; the old world unloading when empty with its folder kept.
3. `SendHomeTask`: `IslandCmd.go()` run from a world-thread task (disband/kick) instead of a command.
4. The five-tab page on the client; one TextField with two action buttons, and Enter only keeping the name.
5. The arrival check and sweep for `/tpa` arrivals, and the `world.prev` redirect.
6. GuardHurt, GuardUseEntity and GuardDrop firing as the bytecode says.
7. Slice B: the biome live resend (`updateChunkEnvironments`), the weather lock surviving a restart, the 5-arg landing teleport with `completedFuture`.

**`[SKYY?]` choices (defaults picked):**
- LOCKED 2026-09-25 (Skyy): co-op size 5 including the owner. That was already the default;
- LOCKED 2026-09-25 (Skyy): Island Admins may invite co-op members. `coop.adminsInvite` defaults to `true`. Was: `false`. SkyyIslands 0.5.2 still writes `false`;
- LOCKED 2026-09-25 (Skyy): Admins may expel, ban and untrust visitors and helpers. Only the Owner kicks co-op members. That was already the default;
- Trusted = builder (no harvest or beds);
- no visits to your own dormant island while you are in a co-op;
- old build-rights invites become Trusted;
- reset cooldown 24 h;
- visitor limit 5;
- biome cost 0 and unlock gating later.

---

## 12. In-game test checklist (append to TEST-CHECKLIST.md when built; A = Skyy (owner), B = Wesley, C optional)

1. Deploy only with Skyy's OK (never `--deploy` from a build script). The server log shows `SkyyIslands 0.5 ready`, the migration lines (`migrated N build-rights entries to Trusted`), no "already registered", and no guard errors on first join.
2. **Migration:** B had build rights on A's island from the beta. B is now Trusted: B builds, breaks, crafts and picks up, but can't open A's chest. B's `/island` still goes to B's own island. `/island menu` → Members tab shows B under Trusted.
3. **Invite + accept:** A `/island invite B` → B gets the chat line with the profile name. B `/island accept` → both get "joined". B `/island` → lands on A's island, and B's Zone widget says "Your Island". B opens A's chest and furnace and harvests a crop.
4. **Own island kept:** B `/island leave` → B lands on B's own island with B's things in place. Re-invite, and B accepts again.
5. **Admin:** A `/island promote B`. B's `/island menu` → B can change the Permissions grid, Visitors mode and PvP, but has no Kick, Disband or Reset. B `/island kick A` / `/island disband` → refused. A `/island demote B` → B's page is read-only.
6. **Profiles:** B switches to profile 2 → B lands on B-p2's own island. On A's island B-p2 is a visitor (chest refused, with the "switch to your profile Apple" message). B switches back → `/island` goes to A's island.
7. **One role per player:** while B-p1 is a member, A invites B again while B is on profile 2 → B `/island accept` → refused, naming profile 1.
8. **Trusted is separate:** A `/island trust C` → C builds on A's island, but C's `/island` goes to C's own island, and C can't open chests or harvest. A `/island untrust C` → visitor.
9. **Kick:** A `/island kick B` while B stands on A's island → B is sent to B's own island with a message. `/island kick C` (trusted) → "use /island untrust".
10. **Disband:** B re-joins. A `/island disband`, then again within 10 s → B (on the island) goes to B's own island. C stays Trusted.
11. **Owner offline:** B re-joins. A logs off. B `/island` → A's island loads, B arrives, builds and uses chests.
12. **Reset:** B is on A's island. A runs `/island reset` three times → B lands in the hub with a message, and A lands on a fresh island with the starter chest filled. The Members tab still lists B and C. B `/island` → the fresh island. A fourth `/island reset` → cooldown message. On disk, the old `skyy-island-<key>` folder is still there next to `...-r1`.
13. **Tint:** an old island that still shows black grass → `/island` → the grass turns green within about 2-6 s without `/hub`. If not, note it, try vanilla `/chunk resend` (op) and see whether that turns it green, then set `tint.resend=chunk`, restart, and retest.
14. **Grid:** A sets Chests → Visitor YES; a visitor opens the chest; set it back → refused. Clicking Member NO on Chests makes it admin/owner only (a Member is refused).
15. **Visitors mode:** Friends → a stranger is refused at `/island visit`; a stranger inside via `/tpa` is sent to the hub within about 5 s. Closed, then `/island lock` and `/island unlock` restore the previous mode. Limit 1 with one visitor inside → a second visitor is refused ("island is full").
16. **Expel / ban:** B (member) `/island expel C` → C in the hub and refused for 60 s. A `/island ban C` → refused at visit and via tpa. C logs off, and `/island unban <C's name>` works offline.
17. **PvP / spawning:** PvP on → visitors expelled, and members can hit each other. Spawning on with Void Sky → nothing spawns.
18. **Page:** every tab switch rebuilds without a client error. The name box + "Invite to co-op" works, Enter only keeps the name, and "Go to island" teleports and closes the page.
19. **Persistence:** restart → members, admins, trusted, bans and settings are unchanged, and B still goes to A's island. The island file shows `v=5`.
20. **Bridge:** `island:role:fn` for B on A's island = `member` / `admin`; `island:coop:fn` for A lists A then B.
21. **Slice B:** Autumn biome → the grass turns orange-brown without re-entering, and it survives a restart and reaches new far chunks. Snow weather lock → snow on the island only; rain is not offered. Landing point → visitors land there, members at the spawn.

---

## 13. Build notes and sources

**Build (`build_skyyislands_0.5.py`, copied from 0.4.5 and edited, since SkyyIslands' recent versions are full scripts; about +1,800 lines):**
- Class order for javassist (a method before its callers):
  1. IslandSettings;
  2. the IslandStore additions (cache, MEMBER_OF, INVITES, CONFIRM, lists, names, `migrate`);
  3. IslandPerms (constants, classifier, `rank`, `homeKey`, `mayEnter`);
  4. the GuardSystem rework + GuardUse/Break/Damage/Place/Pickup, then GuardDrop, GuardUseEntity, GuardHurt;
  5. TintFix, SendHomeTask, EvacTask, ArrivalTask, SweepTask, WorldApply (PvP, spawning; biome and weather in slice B);
  6. IslandCmd static `go` / `info` / `visit` (as in 0.4.5);
  7. IslandCoop (static invite, accept, decline, leave, kick, promote, demote, disband, trust, untrust, reset, expel, ban, unban, lock);
  8. PermFn, RoleFn, OwnerFn, CoopFn;
  9. IslandMenuPage;
  10. the subcommand classes;
  11. the IslandCmd constructor;
  12. plugin setup.
- Plugin setup: one `registerSystem` per new guard class, the migration + `MEMBER_OF` build inside `loadIslandWorlds()`, the 4 bridge functions, and the `config.properties` defaults.
- The script reads `Assets.zip` at build time (Python zipfile, read-only, in memory) for the animal role list.
- Add `B.probe` lines for every new engine call: `WorldNotificationHandler.updateChunkTints/updateChunk`, `World.getNotificationHandler`, `WorldChunk.getIndex`, `PageManager.setPage`, the guard events, `DamageModule.getFilterDamageGroup`, `NPCEntity.getRoleName`, and the WorldConfig setters.
- The javassist limits hold throughout: no lambdas, generics, varargs, autoboxing (`Boolean.valueOf`, `Long.valueOf`), enhanced-for, inner classes (all helpers are top-level), String switch (if/else on int ids) or try-with-resources. Synchronized blocks hold a single call. f-string braces are doubled.
- Engine rules: the world thread for components, teleports and chunk edits; PlayerReadyEvent fires on every world switch; ONE registerSystem per class.

**Engine evidence (VERIFIED):**
- **This revision:**
  - `WorldNotificationHandler.updateChunkTints` and `lambda$updateChunkTints$0` (`getCachedTintsPacket`, `ChunkTracker.isLoaded`, `PacketHandler.write`);
  - `WorldNotificationHandler.updateChunk` (`ChunkTracker.removeForReload` per player);
  - `BlockChunk.setTint` (nulls `cachedColumnPacket` + `cachedTintmapPacket`, `markNeedsSaving`) and `BlockChunk.getCachedTintsPacket`;
  - `ChunkTintCommand` (`setTint`, `updateChunkTints` in its constant pool);
  - `ChunkResendCommand.execute` (`invalidateChunkSection`, `ChunkTracker.clear`, `ClearChunks`);
  - `World.getNotificationHandler`, `WorldChunk.getIndex`;
  - `Universe.removeWorld` (`RemoveWorldEvent`, `stopIndividualWorld`, `validateDeleteOnRemove`), `World.deleteWorldFromDisk` (`getWorldsDeletedPath`, `FileUtil.atomicMove`, `deleteDirectory`), `Universe.isWorldLoadable`, `InstancesPlugin.spawnInstance/safeRemoveInstance`;
  - our scripts: 0.4.5 `RelightNow`/`RelightTask`/`FillTask`/`IslandBuild`/`go`, SkyyHud 0.3.8 `zoneText`, SkyyMenu 0.1.2 `closePage` + CloseTask, SkyyGuilds 0.1 `#SkyyGInvite` TextField bindings, SkyyParty 0.1.3 invites, SkyyProfiles 0.1 `/island` dispatch after a switch.
- **First draft:**
  - engine protection rules `TriggerVolumeRuleSystems$NoDoorOpen/NoHarvestUse/NoUseBlock/NoUseEntity/NoBuild/NoDestroyBlockBreak/NoDestroyBlockDamage/DamageRuleFilter`;
  - event dispatch: `UseBlockInteraction.doInteraction`, `UseEntityInteraction.firstRun`, `BlockHarvestUtils.performBlockBreak/performPickupByInteraction`, `InventoryPacketHandler` (DropItemEvent$PlayerRequest), `ContextualUseNPCInteraction` (no event);
  - `BlockType` getBench/getBeds/getSeats/getFarming/getGathering/getInteractions/isDoor/processConfig; `Bench.getType()`, `BenchType`;
  - `Damage`, `Damage$EntitySource`, `Damage$ProjectileSource`, `DamageModule.getFilterDamageGroup`, `NPCEntity.getRoleName`;
  - `WorldConfig` setters + `markChanged` + `WorldConfigSaveSystem`; vanilla `WorldConfigSetPvpCommand`, `SpawnCommand$DisableCommand`, `WeatherSetCommand/WeatherResetCommand`, `WeatherSystem$WorldAddedSystem`, `TimeCommand`, `WorldConfigPauseTimeCommand`, `WorldTimeResource.setDayTime`;
  - `BlockChunk.setEnvironment/getEnvironmentChunk`, `EnvironmentChunk.setColumn`, `WorldNotificationHandler.updateChunkEnvironments`, `Environment.getAssetMap().getIndex`, `VoidWorldGenProvider(Color, String)`;
  - `World.getPlayerRefs` (concurrent), `Universe.getPlayer(UUID)`, `InstancesPlugin.teleportPlayerToLoadingInstance` 5-arg, `ArgTypes.GAME_PROFILE_LOOKUP`;
  - `FarmingSystems$Ticking`, `BenchSystems$ProcessingBenchTick`, `WaterGrowthModifierAsset.checkIfRaining`.
- **Assets:** `Server/Environments/*` (122), `Server/Weathers/*` (87), `Server/NPC/Spawn/World/*` (96), `Server/Audio/AmbienceFX/*` (48), `Server/World/Default/Zones/*/Tile.*.json` tints, `Server/Farming/Modifiers/Water.json`, `Server/Item/Unarmed/Interactions/Empty.json`, every `Server/Item/Items/**` BlockType.
- **Installed mod (read-only):** `Aetherhaven-3.1.3.jar` `TownTerritoryGuard.classifyUseBlock/isHarvestStyleBreak`, `TownMemberPermissions`, `TownMemberPermissionsPage`.

**Web sources (summarised in my own words in section 2):**
- BentoBox: https://docs.bentobox.world/en/latest/BentoBox/Island-Protection,-Flags-%26-Ranks/ · https://docs.bentobox.world/en/latest/BentoBox/Flags/ · https://docs.bentobox.world/en/latest/BentoBox/About/Teams/ · https://docs.bentobox.world/en/latest/gamemodes/BSkyBlock/Commands/ · https://docs.bentobox.world/en/latest/addons/Visit/ · https://docs.bentobox.world/en/latest/addons/Biomes/ · https://github.com/BentoBoxWorld/BentoBox/blob/develop/src/main/java/world/bentobox/bentobox/lists/Flags.java
- SuperiorSkyblock2: https://wiki.bg-software.com/superiorskyblock/overview/island-privileges · https://wiki.bg-software.com/superiorskyblock/overview/island-flags · https://wiki.bg-software.com/superiorskyblock/overview/menus · https://wiki.bg-software.com/superiorskyblock/overview/commands-and-permissions/player-commands · https://github.com/BG-Software-LLC/SuperiorSkyblock2/issues/2412
- IridiumSkyblock: https://iridium-development.gitbook.io/iridiumskyblock/general/features · https://iridium-development.gitbook.io/iridiumskyblock/general/permissions
- ASkyBlock: https://github.com/tastybento/askyblock/wiki/Permissions
- Hypixel SkyBlock (wiki mirrors): https://hypixelskyblock.minecraft.wiki/w/Private_Island · https://hypixelskyblock.minecraft.wiki/w/Settings · https://hypixelskyblock.minecraft.wiki/w/Guests_Management · https://hypixel-skyblock.fandom.com/wiki/Co-op
