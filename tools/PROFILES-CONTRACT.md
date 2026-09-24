# SkyWynn profile contract (v1, 2026-09-23)

Skyy's design lock: **profiles are full SkyBlock-style saves and the class selector.** One profile = one class, one island, and its
own everything (coins, bank, bags, skills, collections, accessories). A new class is a **new profile and a new island from zero**.
The class is chosen **when the profile is created** (like creating a Minecraft world) and is **locked** for that profile.

`SkyyProfiles` owns profiles. Every other Skyy mod keeps working without it (zero dependencies) and follows these rules.

## Bridge keys (System.getProperties().get("skyy.bridge"), a ConcurrentHashMap)

| Key | Value | Written by |
|---|---|---|
| `profile:fn:key` | `java.util.function.Function` apply(UUID) -> String storage key of the player's ACTIVE profile | SkyyProfiles |
| `profile:key:<uuid>` | String, same value as `profile:fn:key` (convenience) | SkyyProfiles |
| `profile:<uuid>` | String active profile id: `"1"`, `"2"`, ... | SkyyProfiles |
| `profile:class:<uuid>` | String class of the active profile (`Archer`, `Warrior`, `Mage`, later `Assassin`, `Shaman`); absent = none | SkyyProfiles |
| `profile:epoch:<uuid>` | Long, +1 on every profile switch or creation | SkyyProfiles |
| `profile:name:<uuid>` | String display name of the active profile | SkyyProfiles |

## Storage key

- Profile `"1"` -> key = `uuid.toString()`. **Existing data files are profile 1**, no migration.
- Profile `"N"` (N >= 2) -> key = `uuid.toString() + "-p" + N` (safe in Windows file names).
- Without SkyyProfiles every mod uses `uuid.toString()` (= profile 1).

Every mod embeds the same helper (javassist-safe):

```java
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}
```

## Rules for every mod that stores per-player data

1. Use `pkey(u)` instead of `u.toString()` in every per-player file name (players/<key>.properties, pools/<key>.properties, ...).
2. Key in-memory per-player caches by the **pkey String** (not the UUID), so a switch simply resolves to a different entry.
3. Per-player bridge values you publish (`coins:<uuid>`, `bank:<uuid>`, `skill:<uuid>`, `acc:has:<uuid>`, `acc:tal:<uuid>`,
   `coll:recipes:<uuid>`, `class:<uuid>`, ...) stay keyed by **UUID** (they always describe the ACTIVE profile). Republish them when
   `profile:epoch:<uuid>` changes (check it in your existing 1-5 s tick; remember the last epoch you saw per UUID).
4. Anything applied to the live player (stat modifiers, movement protocol sources) must be recomputed from the new profile's data
   after an epoch change (the existing per-second syncs do this if they read through pkey).
5. Never swap or touch the vanilla inventory for a profile switch - SkyyProfiles does that itself.
6. Bazaar / Party / Essentials / HUD / Menu data is per PLAYER (not per profile) unless noted.

## Per-mod notes

- **SkyyIslands:** island per profile: world name for profile 1 stays as today; new profiles get `skyy-island-<pkey>`. The island file
  is `islands/<pkey>.properties`. On a switch the player is sent to the new profile's island (SkyyProfiles dispatches `/island`).
- **SkyyClasses:** when `profile:class:<uuid>` is present it is AUTHORITATIVE: use it as the player's class, show /class read-only
  ("your class is locked to this profile"), and do not open the first-join class picker (SkyyProfiles runs profile creation).
  Without SkyyProfiles keep today's behaviour (pick once, locked).
- **SkyyCoins:** starter coins per profile (a new profile starts fresh). `coins:fn:*` resolve the active profile.
- **SkyySkills:** XP, per-class combat XP and perks per profile.
- **SkyySacks:** pool, processing queues and crafts.log lines per profile (key in the log line).
- **SkyyAccessories:** bag per profile.
- **SkyyCollections:** counts per profile.
- **SkyyBank:** account per profile (interest keeps paying every account file, including profile files).

## Semantics of SkyyProfiles 0.1 (what adopters can rely on)

Pinned down on 2026-09-23 from `SkyyProfiles/build_skyyprofiles_0.1.py` (after the join-window fixes), with the engine side checked
in `HytaleServer.jar` bytecode (tools/dev). "Store lock" = SkyyProfiles' monitor for players files (`ProfStore.class`).

### 1. `profile:fn:key`: when it exists

- Registered in `setup()`, before `start()` and before any player can connect. A second `setup()` replaces the object.
- Never removed: not on disconnect, not in `shutdown()`. Other mods' disconnect and shutdown saves still resolve the right profile.
- Absent means SkyyProfiles is not installed. It can also be absent while other plugins run their own `setup()`, before ours ran,
  but no player is online then. Fall back to `uuid.toString()`.

### 2. What `apply(UUID)` returns

Rule: the storage key of the active profile. Profile `"1"`, or no profile, gives `uuid.toString()`; profile N >= 2 gives
`uuid + "-pN"`. The active profile is the players file's `active` id when that profile exists. Otherwise it is the lowest existing
profile id, which is what the join repair activates a moment later. With no profiles at all there is no active profile.

| Case | Result |
|---|---|
| (a) Not loaded yet. This is the first call for that UUID in this JVM: an offline player, or another mod's PlayerConnectEvent listener that ran before ours. | Reads `players/<uuid>.properties` synchronously in that call, under the store lock. Caches it and returns the correct key. It never guesses profile 1. For online players this path almost never runs: SkyyProfiles re-reads the file at PlayerConnectEvent, before the player is in any world. One caveat: a copy cached in an earlier session in this JVM is used until that re-read. It can only differ from the file if someone hand-edited the file while the player was offline and skipped `/profileadmin reload`. |
| (b) No profile yet | `uuid.toString()`: the legacy files. They become profile 1 when the first profile is created, so creating profile 1 does not change the key. |
| (c) Offline | Same rule, read from disk. The copy stays cached for the JVM's lifetime and is re-read at the player's next connect or on `/profileadmin reload`. An offline player's active profile cannot change: switching needs the player online, and `setclass` never changes the key. |
| (d) Players file unreadable (I/O error, bad hand edit) | Returns the last good copy read in this JVM, if there is one. Profile changes are refused meanwhile. With no good copy it returns `uuid.toString()`; nothing better is known. That result is not cached. The file is re-read at most every 2 s while asked for, at every connect, and on `/profileadmin reload`. The log warns once. |
| (e) Argument is not a UUID | `String.valueOf(arg)` (`null` gives `null`). Always pass a `java.util.UUID`. |

- **Cost and blocking.** A cache hit is one `ConcurrentHashMap` read plus a string concat: no lock, no I/O. A cache miss is one
  small file read under the store lock. SkyyProfiles' players-file writes hold that lock too (tmp write, fsync, atomic rename,
  up to 5 x 20 ms retries on any Windows `FileSystemException`: `AccessDeniedException` or a sharing violation). So a miss can wait a few ms behind another player's write. It never
  waits on a world thread or on another mod.
- **Never throws.** Everything is caught; the worst case is `uuid.toString()`.
- **Never calls out.** It never calls another mod, never writes the bridge, and never touches ECS components or inventories. It is a
  pure read and triggers nothing.
- **Safe from any thread:** world threads, the scheduler, storage or network threads, and inside your own locks. SkyyProfiles
  holds its monitors only around its own file I/O and bridge `put`s, and never calls another mod while holding one, so no lock
  cycle is possible.
- **Authoritative.** `profile:key:<uuid>` mirrors it but is written a moment later (see 3).

### 3. Bridge writes: order and thread

**publish(uuid)** writes these keys in this order: `profile:key:<uuid>`, `profile:<uuid>`, `profile:class:<uuid>`,
`profile:name:<uuid>`, `profile:list:<uuid>`, and `profile:epoch:<uuid>` last. Class and name are removed when empty. With no
profile, the key is still written and id, class, name and list are removed. All publishes share one monitor (`ProfPub.class`, never
held across disk I/O) and read the current state inside it. Two publishes never interleave, so values never go backwards. Nothing is
published when no state is known (case 2(d) with no good copy).

**Key flip timing.** The Function flips when the players file is committed, which is before `publish`. For the length of one method
call, the Function can already return the new key while `profile:key:<uuid>`, `profile:<uuid>` and the epoch still show the old
ones. The reverse never happens: when you see a new epoch, the Function already returns the new key.

| Event | Thread | What happens, in order |
|---|---|---|
| Plugin start | plugin `setup()` | `profile:fn:key` is put. No per-player keys yet. |
| Join: PlayerConnectEvent | Engine join thread (storage or network thread, never a world thread). The player is not in any world yet. | Players file re-read (the cached copy is replaced, never dropped). Username noted (file write only if it changed). A missing or invalid active id is repaired to the lowest profile (epoch +1). If a crash marker needs recovery: `profile:busy:<uuid>` = TRUE. Then publish. |
| Crash recovery applies | The player's world thread, as soon as the entity is in a world. It polls every 250 ms for up to 60 s and does not wait for PlayerReadyEvent. | Inventory cleared and the active profile's snapshot loaded. Marker kept 30 s. Publish (same key and epoch as at connect: recovery never changes the active profile). `profile:busy` removed. |
| First PlayerReadyEvent of the session | scheduler | Normally chat only, no bridge writes. Fallback: if the connect handler did not run, it does the whole join row now. It also retries a recovery that gave up. |
| Later PlayerReadyEvents (world switches) | - | Nothing. |
| First profile created (page) | world thread | Players file gets `p.1.*`, `active=1`, epoch +1. The Function's key is unchanged (it was already `uuid`). Publish: same key, id `1`, class, name, list, new epoch. |
| Profile N created (page) | world thread | Players file gets `p.N.*` and epoch +1; active is unchanged. Publish (only list and epoch change). Then a switch follows (next row): a second epoch +1, this time with the new key. If that switch is refused or fails, profile N exists but is not active. |
| Switch | World thread, one uninterrupted task | `profile:busy` = TRUE. Current inventory captured and written to `inventories/<fromKey>.json`. Marker written. Inventory cleared and the target loaded. Players file committed (`active=to`, epoch +1): the Function flips here. Marker kept 30 s (not deleted). Publish. `profile:busy` removed. Then page closed, chat sent, `/island` dispatched. A failure before the commit rolls back: no bridge change except busy on then off. |
| `/profileadmin setclass` | The admin's world thread (the target may be in another world or offline) | Players file class changed; epoch +1 only if it is the target's active profile. Publish for the target, even if offline. The key never changes. |
| `/profileadmin reload` | admin's world thread | Every cached players file re-read in place, then every online player published. |
| Disconnect (PlayerDisconnectEvent) | Network thread, fired before the entity leaves its world | No bridge writes. `lastPlayed` is written to the players file on the scheduler. Per-player keys stay. |
| Plugin shutdown | plugin `shutdown()` | No bridge writes; `profile:fn:key` stays. Markers still waiting out their 30 s are deleted (on a graceful stop the engine saves every online player). |

- **Per-player keys are not removed on disconnect.** They keep describing the active profile, which cannot change while the player
  is offline. The only offline change is `setclass`, and it republishes.
- **Epoch.** A `Long` stored in the players file, so it only goes up, across restarts too. It rises by 1 on:
  - every profile creation, active or not;
  - every switch;
  - `setclass` of the active profile;
  - the join repair.

  `0` means no profile yet. The epoch key is absent until SkyyProfiles has published for that player in this JVM, which normally
  happens at their connect. It stays absent if the file is unreadable and there is no good copy.
- **Extra keys** (not in the v1 table):
  - `profile:list:<uuid>` = `"1:Apple:Archer,2:Banana:Mage"`.
  - `profile:busy:<uuid>` = `Boolean.TRUE` while the live vanilla inventory may not belong to the active profile.

### 4. Recommended adopter pattern

1. **One key per operation.** Resolve `pkey(u)` when the operation starts and use that one key for all of it. Do not re-resolve
   halfway (the SkyyBank 0.1.2 pattern). Key in-memory per-player caches by the key string. Do not carry a resolved key across ticks
   in off-thread code; the Function is cheap.
2. **First sight is a baseline, not a change.** The first non-null `profile:epoch:<uuid>` you see for a UUID is the baseline:
   remember it and load through `pkey`. Do nothing switch-like: no flush-and-reload, no settle window, no "profile changed" message.
   Only a later, different value is a change. An absent epoch carries no information: going from absent to a value is a baseline too.
   You may forget or keep the remembered epoch at disconnect; both are fine.
3. **On a change:** flush pending writes under the key they were made for. Then re-resolve `pkey`, republish your UUID-keyed bridge
   values, and recompute effects on the live player. Never move data from the old key to the new one.
4. **Writes made before the first epoch is seen are correct as they are.** The Function reads the players file itself, so `pkey(u)`
   is right from its very first call, and for offline players too. Write through `pkey` and never "fix" earlier writes when the
   epoch appears. In 0.1 the epoch is published at PlayerConnectEvent, before the player is in any world. So an online player with
   no epoch means SkyyProfiles is missing, or that player's players file is unreadable. Before the first epoch, a coin payout or a
   bag save through `pkey` already goes to the right profile's file.
5. **Respect `profile:busy:<uuid>`.** Skip item moves between the live vanilla inventory and per-profile storage while it is
   present: sweeps, bag equip or unequip, bench mirrors, and pickups into bags. Code on the player's own world thread can only ever
   see it during a pending crash recovery at join, because a switch runs inside one task on that thread. A sweep in that window would duplicate items,
   since the recovery reloads the snapshot afterwards. Nothing else needs to check it.
6. **Prefer the Function.** Do not use `profile:key:<uuid>` for writes: it is absent before the first publish and lags one method
   call behind at a switch.

### 5. Known limits of 0.1

- **Unreadable players file with no good copy:** the Function returns profile 1's key, and no bridge values are published for that
  player until the file reads.
- **Recovery window for mods that ignore `profile:busy`:** from the moment the player entity enters a world until the recovery task
  runs, about 250 ms plus one world task. Before this pass the window ran until PlayerReadyEvent plus a scheduler hop: seconds.
- **The 30 s marker is an estimate.** SkyyProfiles cannot observe the engine's player save, so it keeps each marker for 30 s:
  three periods of the engine's 10 s save tick, in worlds that save players. It does not help in a world with `isSavingPlayers`
  off, or when a world thread dies while the JVM lives on. A crash within 30 s after a switch or recovery rolls that player forward
  at the next join. Up to 30 s of their inventory changes are then reverted, and items they moved into mod storage in those seconds
  exist twice. That is still far better than before this pass, when one profile was duplicated and the other lost.
  Engine fact (cross-mod timeline pass, HytaleServer.jar bytecode): the engine also saves a player whenever the entity leaves a
  world (`PlayerSavingSystems$EntityRemovedSystem` -> `Player.saveConfig`, in worlds with `isSavingPlayers`; island instances have it
  on). With `islandOnSwitch=true` the `/island` dispatched right after the switch starts a cross-world transfer
  (`Universe.transferPlayerAsync` -> `PlayerRef.removeFromStore`), so the switched inventory is normally on disk within about a second.
  The 30 s window mostly matters with `islandOnSwitch=false`, or when the player is already on the target island.
- **Hand edits of a players file while the player is online bypass everything.** The file header says so.
