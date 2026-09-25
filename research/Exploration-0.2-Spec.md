# SkyyExploration 0.2 build spec: server backbones

*For the build agent of SkyyExploration 0.2. Written 2026-09-24. Sources: `SkyyExploration-Plan.md` ("Next (SkyyExploration 0.2): backbones for server content"), HANDOFF section 1 ("Exploration call", "Pack goal", "In-game server setup"), `SkyWynn-Server-Setup-Plan.md`, `research/Exploration-Research.md` (options A1, A2, C2), `research/Exploration-Build-Spec.md` (the 0.1 spec), `research/Settings-Spec.md` 3.12, `tools/PROFILES-CONTRACT.md`, and `SkyyExploration/build_skyyexploration_0.1.py` (the LIVE version, deployed 2026-09-24 22:53). I re-checked every engine name below this pass with `tools/dev` (reflect.py, bc.py, bcfull.py, cpgrep.py) against the release `HytaleServer.jar`, and with python `zipfile` against `Assets.zip`. **VERIFIED** = seen in bytecode, assets or shipped Skyy code. **NEEDS A TEST** = the pieces are verified, but nobody has seen the behaviour in game yet.*

**Skyy's ask (they/them):** build the backbones now and leave the content for the server. That means admin-placed discovery and secret spots, plus an island checklist with a % on `/explore`. Everything a server owner changes must work **in game**, and the files must always match the game. The pack must be 100% usable solo and in private multiplayer.

**Scope:** SkyyExploration 0.2 only. Copy `SkyyExploration/build_skyyexploration_0.1.py` to `build_skyyexploration_0.2.py` and edit the copy. 0.1 uses no patch script, and the 0.1 file stays untouched. Set `VERSION = "0.2"` (display name `"0.2 SkyyExploration"`) and add a `0.2:` docstring block that points here. No other mod changes, and no new dependency.
**Hard rules (from the task):** build with plain `python build_skyyexploration_0.2.py`; the output must end with `assembled ...jar`. Then run `python tools/ci/lint.py` and get 0 fails. Never pass `--deploy`. Never run `tools/deploy_set.py` except with `--check`. Never write inside `AppData`. No git commit. Do not edit HANDOFF, TEST-CHECKLIST, DESIGN-STATUS, `deploy_set.py`, SkyyMenu or any other mod.

**Out of scope (server phase, section 12):** Echo Shards, warps unlocked by discovery, map reveal, finder sense, lootrun camps, several islands inside one world, re-ordering checklist entries, quest content, and the SkyyMenu "Mods" editor adoption.

---

## 0. Verdicts

| Question | Verdict |
|---|---|
| Banner + sound on first arrival | Use **the engine's own zone-discovery path** (`WorldMapTracker.onZoneDiscovered`, bytecode). It calls `EventTitleUtil.showEventTitleToPlayer(pr, title, subtitle, major, icon, duration, fadeIn, fadeOut)`, then `SoundEvent.getAssetMap().getIndex(id)`, where `Integer.MIN_VALUE` means the sound is missing, then `SoundUtil.playSoundEvent2d(ref, idx, SoundCategory.UI, accessor)`. We call the PlayerRef twin `SoundUtil.playSoundEvent2dToPlayer(pr, idx, SoundCategory.UI)`. It sends the same `PlaySoundEvent2D` packet without touching any component. Sounds are the engine's `SFX_Discovery_Z1..Z4_Short/Medium` (the same events `Zone.json` `Discovery.SoundEventId` uses). |
| Cheap arrival detection | **No new system.** `ExpTick` (0.1, Player query, world thread) adds its own accumulator and runs a spot check every `spots.checkMs` (default 333 ms, 3 times a second, clamped 250..500). Each world has an **immutable `WorldDef` snapshot**. Its chunk index is a fastutil `Long2ObjectOpenHashMap`: key `ChunkUtil.indexChunk(cx, cz)`, value a `SpotDef[]` of the spots whose sphere touches that 32x32 column. One check = one `TransformComponent` read, one primitive-key `get`, a few double multiplies and **zero allocations**. `pkey()` is only called on a hit. |
| Where spots and checklists live | **`worlds/<worldFile>.properties`, one file per world.** The game rewrites it atomically after every in-game change. `/exploreadmin reload` re-reads hand edits. Global numbers stay in `config.properties`, and 0.2 adds `/exploreadmin set|get <key>` so every key can be changed in game. That is the file-in-sync rule of the Server-Setup plan. |
| Per-profile records | **Three NEW append-only files** next to 0.1's `chests.txt`: `spots.txt`, `ticks.txt`, `done.txt`. The 0.1 properties keys are unchanged. So going 0.1 -> 0.2 needs no migration, and rolling back 0.2 -> 0.1 loses nothing (0.1 ignores those files). |
| Ids | Spot = `s<n>`, checklist entry = `<n>`. One global counter in `worlds/ids.properties`, never reused, so a deleted spot's old finds can never count for a new spot. |
| Checklist shape | Every spot with `checklist=yes` is an entry automatically, removed with the spot. The other entry types are `chest` (one recorded loot chest), `chests` (open N loot chests in this world), `zone` (a Hytale region, 0.1's record) and `custom` (admin text, ticked by command, admin page or the bridge). The % is per profile per world. An optional reward at 100% pays XP + coins (default 0 = off). |
| Commands with optional numbers | **Usage variants keyed by token count.** `AbstractCommand.checkForExecutingSubcommands` does `variantCommands.get(tokenCount)` at every command level (bytecode). Variants must be added in the constructor and may not share the parent's required count. A spot name is one token: `_` becomes a space, and quotes NEED A TEST. Free text uses `GREEDY_STRING` as the last argument (the SkyyGuilds 0.1.1 pattern). |
| Admin page | One inline page, `/exploreadmin`, 1120 x 900, three tabs: **Spots, Checklist, Island**. A list on the left, the selected item's editor on the right. Text boxes use the verified SkyyGuilds/SkyySacks pattern. Several boxes on one button are VERIFIED in vanilla `LaunchPad$LaunchPadSettingsPage`, which chains four `EventData.append` calls. Rebuilds happen only after clicks, at most once a second. The permission is re-checked on every click. |

---

## 1. Engine facts used (VERIFIED 2026-09-24)

| Piece | Exact name | How verified |
|---|---|---|
| Banner | `server.core.util.EventTitleUtil.showEventTitleToPlayer(PlayerRef, Message, Message, boolean)`: icon null, duration 4.0, fades 1.5, 1.5. The long form is `(PlayerRef, Message primary, Message secondary, boolean major, String icon, float duration, float fadeIn, float fadeOut)`. Both only write a `ShowEventTitle` packet (`writeNoCache`). | reflect + bcfull |
| Sound index | `server.core.asset.type.soundevent.config.SoundEvent.getAssetMap()` returns `IndexedLookupTableAssetMap`; `.getIndex(Object)` returns an int. The engine compares it with `Integer.MIN_VALUE` (ldc -2147483648) before playing. | bc `WorldMapTracker#onZoneDiscovered` |
| Sound play | `server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(PlayerRef, int, SoundCategory)` builds `PlaySoundEvent2D` and calls `PacketHandler.write`, with no component access. `protocol.SoundCategory.UI`. | reflect + bc |
| Sound ids | `SFX_Discovery_Z1_Short`, `SFX_Discovery_Z1_Medium` ... `Z4_*` (8 files under `Server/Audio/SoundEvents/SFX/UI/Discovery/`). Zone1 regions use `SFX_Discovery_Z1_Medium` with `Major: true`. | Assets.zip |
| Chunk key | `math.util.ChunkUtil.indexChunk(int,int)`, `chunkCoordinate(int)` (= x >> 5), `indexChunkFromBlock(double,double)` (= `indexChunk(floor(x) >> 5, floor(z) >> 5)`), `SIZE = 32` | bcfull + reflect |
| Primitive map | `it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap.get(long)` / `put(long, Object)`. It ships in HytaleServer.jar, and 0.1 already uses fastutil `LongOpenHashSet`. | reflect |
| Teleport | `server.core.modules.entity.teleport.Teleport.createForPlayer(World, Transform)` + `getComponentType()`; `math.vector.Transform(Vector3d, Rotation3f)`; `HeadRotation.getRotation()`; `builtin.teleport.components.TeleportHistory.append(World, Vector3d, Rotation3f, String)`; `Store.addComponent` / `ensureAndGetComponent` | shipped SkyyEssentials 0.1.1 (MoveTask) + SkyyMenu 0.1.3 (`teleport()`) |
| Close page after teleport | `PageManager.setPage(ref, store, protocol.packets.interface_.Page.None)` | shipped SkyyMenu 0.1.3 `closePage` |
| Text boxes | `TextField #Id { Anchor: (Full: 0); Padding: (...); MaxLength: n; PlaceholderText: "..."; PlaceholderStyle: (...); Style: (...); }` inside a Group box; prefill with `b.set("#Id.Value", s)`; read with `EventData.of("a", act).append("@Key", "#Id.Value")` + `jsonStr(data, "@Key")` | shipped SkyyGuilds 0.1.1 + SkyySacks 0.7.3 (verified in game) |
| Several boxes on one button | `EventData.append(String, String)` returns `EventData` (chainable). Vanilla `LaunchPad$LaunchPadSettingsPage#build` chains `@X`, `@Y`, `@Z`, `@PlayersOnly` on one `#SaveButton`. | reflect + bc |
| Usage variants | `AbstractCommand.addUsageVariant` refuses after registration, refuses named variants and refuses reused variants, and keys `Int2ObjectMap` by required count. `checkForExecutingSubcommands` runs `getSubCommand(token)` then `variantCommands.get(count)`, and then `acceptCall0` at each level. | bc |
| Arg types | `ArgTypes.STRING`, `GREEDY_STRING` (allows extra tokens, must be the last required arg), `PLAYER_REF` (online player; SkyyEssentials) | reflect + shipped code |
| Current zone | `Player.getWorldMapTracker().getCurrentZone().regionName()` (0.1). It returns null on Void, Flat and hand-built worlds. | 0.1 spec |

**NEEDS A TEST (in game):**
1. How a non-major banner (`major=false`) looks next to a major one. Both are config switches.
2. `/exploreadmin spot add "Old Watchtower" 8`. The tokenizer treats quotes specially (SkyyCoins 0.1.4 notes), but a quoted multi-word token has not been seen in game. Underscores always work: `Old_Watchtower` becomes "Old Watchtower".
3. Three `@Key` values on one button of an INLINE page. The same thing is verified in vanilla (see the table) and with one key in SkyyGuilds.
4. The spot-check cost with many players. `/exploreadmin stats` prints the check count and the time per second (section 3.7).

---

## 2. Files, ids and data model

### 2.1 Folder `<world save>/mods/Skyy_SkyyExploration/`
| Path | 0.1 | 0.2 |
|---|---|---|
| `config.properties` | yes | The same file. At setup, 0.2 **appends its block once** (2.5) when no line starts with `spots.enabled=`. A missing file gets the full 0.1 + 0.2 defaults. |
| `chests/<wf>.log` | yes | unchanged |
| `players/<pkey>.properties` | yes | unchanged keys; `v=2` written |
| `players/<pkey>/chests.txt`, `chunks/<wf>.bin` | yes | unchanged |
| `players/<pkey>/spots.txt` | - | **NEW**, append-only, lines `<wf> <spotId> <d|s>` (d = discovery, s = secret when found) |
| `players/<pkey>/ticks.txt` | - | **NEW**, append-only, lines `+ <entryId>` / `- <entryId>`, replayed in order (custom entries) |
| `players/<pkey>/done.txt` | - | **NEW**, append-only, lines `<wf>` (the checklist completion reward was paid for that world) |
| `worlds/<wf>.properties` | - | **NEW**, one per world that has spots or checklist entries (2.3) |
| `worlds/ids.properties` | - | **NEW**, `next=<n>`, the global id counter (2.2) |
| `admin.log` | - | **NEW**, append-only; one line per in-game admin change (2.6) |

`<wf>` is 0.1's `ChestReg.wf(worldName)`: characters outside `[A-Za-z0-9.-]` become `-`, then `-` + `Integer.toHexString(name.hashCode())` is added. Every append goes through 0.1's ordered `ExpIO` queue, written by `ExpSaver` every 2 s and in `shutdown()`. Player files are only READ on world threads (0.1 rule).

### 2.2 Ids
- **Spot id** `s<n>`, **checklist entry id** `<n>` (digits only). Both come from ONE global counter `SpotReg.NEXT`, stored in `worlds/ids.properties` (`next=`). A new id is `NEXT++`, taken inside the synchronized mutation. The world save task (6.5 step 6) writes `ids.properties` first and then the world file, both atomically, so a file never holds an id above the stored counter.
- At load, `NEXT = max(file value, highest n seen in any world file + 1)`. So a lost counter file can never cause reuse while any world file still exists.
- A token that starts with `s` + digits is a spot, and plain digits are an entry. Commands also accept a spot **name**: case-insensitive, spaces ignored, an exact match or a unique 3+ letter prefix (0.1 `resolveTitle` style). Several matches reply `"'old' fits Old Watchtower (s3), Old Mill (s9) - type more letters or use the id"`.
- Names are unique per world, case-insensitive.

### 2.3 World file `worlds/<wf>.properties` (UTF-8, read with `Properties.load(Reader)`)
```
# SkyyExploration 0.2 - discovery spots and the island checklist of the world "fens".
# Set this up IN GAME: /exploreadmin (admin page) or /exploreadmin spot|check|island ... - the game rewrites this file after every change.
# Hand edits: stop the server first, or run /exploreadmin reload right after saving (in-game changes are refused while this file differs
# from what the game last read or wrote).
world=fens
name=Fens Island
checklist=true
reward.xp=0
reward.coins=0
# default XP for NEW spots on this island (-1 = config spots.defaultXp / spots.secretXp)
spotXp=-1
secretXp=-1
# spot.<id>=<x> <y> <z>|<radius>|<xp>|<secret true/false>|<on checklist true/false>|<name>
spot.s3=120 64 -45|6|500|false|true|Old Watchtower
spot.s4=88 91 12|3|1500|true|true|Hidden Grotto
# check.<id>=<type>|<arg>|<text>   type = chest (arg "x y z") | chests (arg N) | zone (arg region id) | custom (arg empty)
check.7=chest|130 70 -60|Hidden loot chest
check.8=chests|10|Open 10 loot chests on this island
check.9=zone|Zone1_Tier3|The Fens
check.10=custom||Help the fisherman
```
- **Parse:** `split("\\|", 6)` for spots and `split("\\|", 3)` for entries, so the name or text is last and whole. A bad line is skipped with one WARN naming the file and key, and the rest loads. Clamp: radius 1..`spots.maxRadius`, XP 0..400000, N 1..100000. An unknown region id in a `zone` entry is kept, with a WARN.
- **`world=` is authoritative, not the file name.** A copied file from another server works as long as the world name matches. A file whose name is not `<wf>.properties` is renamed at setup when the target does not exist. If two files claim one world, the newer (lastModified) wins, with a WARN. An entry id used twice across files: the first file read keeps it, the other line is dropped, with a WARN. Duplicate spot names are loaded, but the admin page flags them.
- **Write:** our own text writer, not `Properties.store`, so the order and comments stay stable. The header lines above come first, then `world`, `name`, `checklist`, `reward.*`, `spotXp`, `secretXp`, then spots by n, then entries by n. Values are written raw, and names and texts are sanitized (2.4), so no escaping is needed. Write to `.tmp` and then `ExpIO.moveRetry` (0.1's ATOMIC_MOVE with 5 x 20 ms retries). A world with no spots and no entries, and every other value at its default, has its file deleted.
- **Hand-edit guard:** after every read and write, `SpotReg.STAMP[wf] = {lastModifiedMillis, size}`. Before any in-game change to that world, the op compares the stamp with the file on disk (a tiny stat on the admin's world thread). If they differ, the change is refused: `"-worlds/fens-1a2b.properties was edited outside the game - run /exploreadmin reload first (nothing changed)"`. A world file that fails to parse at all is `bad`: its old in-memory copy stays active if there is one, edits to it are refused, and the file is **never overwritten**.

### 2.4 Text rules
- **Spot name:** 1..40 characters. **Entry text and island name:** 1..80. Control characters, `|` and `\` are dropped, `_` becomes a space, and the value is trimmed. An empty result is refused.
- Everything dynamic reaches the UI only through `b.set("#Id.Text"/".Value", ...)`, so any character is safe there. Button labels are literals.

### 2.5 config.properties: the 0.2 block (appended once; the defaults Python builds it from and asserts ASCII)
```
# ---------- SkyyExploration 0.2: discovery spots, secret spots, island checklists ----------
# Spots and checklists are set up IN GAME: /exploreadmin (admin page) or /exploreadmin spot|check|island ... (perm skyyexploration.admin).
# Each world's list lives in worlds/<world>.properties. Any key in this file: /exploreadmin set <key> <value> (writes this file).
spots.enabled=true
# how often each player is checked against the spots of their world (ms): 250..500 = 4 to 2 times a second
spots.checkMs=333
spots.defaultRadius=6
spots.maxRadius=64
spots.defaultXp=500
spots.secretXp=1500
spots.maxPerWorld=500
# banner (title in the middle of the screen) + sound on the first arrival; at most one banner per bannerGapMs per player
spots.banner=true
spots.bannerGapMs=5000
spots.major=false
spots.secretMajor=true
spots.sound=SFX_Discovery_Z1_Short
spots.secretSound=SFX_Discovery_Z1_Medium
checklist.enabled=true
checklist.maxEntries=300
# "Add loot chest here" takes the nearest recorded loot chest within this many blocks
checklist.chestRadius=8
checklist.sound=SFX_Discovery_Z2_Medium
# loot chests (the only item reward) wait this long after a profile switch (SkyyVault rule: SkyyProfiles keeps its switch marker 30 s)
profile.afterSwitchSeconds=30
# every in-game admin change is written to admin.log (who, when, what)
admin.log=true
```
New `ExpCfg` volatile fields (clamped in `apply()`, all live on reload): `SPOTS_ON`, `SPOT_MS` (250..500) + `SPOT_S = SPOT_MS / 1000.0`, `SPOT_R` (1..`SPOT_RMAX`), `SPOT_RMAX` (4..128), `SPOT_XP`, `SECRET_XP` (0..400000), `SPOT_MAX` (1..5000), `SPOT_BANNER`, `BANNER_GAP` (0..600000), `MAJOR`, `SECRET_MAJOR`, `SOUND`, `SECRET_SOUND`, `CHECK_ON`, `CHECK_MAX` (1..2000), `CHEST_R` (1..64), `CHECK_SOUND`, `AFTER_SWITCH_MS` (0..120 s), `ADMIN_LOG`. The name `BANNER` already belongs to `zones.banner`, so do not reuse it. Sound indexes are resolved lazily and cached in `SND_IDX = new int[3]`, reset to 0 (= unresolved) by every `load()`. A missing sound logs one WARN and plays nothing. The build asserts that each default sound id exists as `Server/Audio/SoundEvents/**/<id>.json`.

### 2.6 admin.log
`2026-09-24 22:10:03 | Skyy 3f2a...-... | fens | spot add s3 name=Old Watchtower pos=120 64 -45 r=6 xp=500 secret=no check=yes`
Time: `java.time.LocalDateTime.now().withNano(0).toString().replace('T', ' ')`. One line per successful change, including every `set` (`set chests.base 400 -> 600`), each written as `old -> new`. Appended through the `ExpIO` queue. `admin.log=false` stops it.

### 2.7 Memory model (new classes: fields + constructor only)
- **`SpotDef`**: `String id; long n; String name; int x, y, z, r; double cx, cy, cz, r2; long xp; boolean secret, check;` with `cx = x + 0.5`, `cy = y`, `cz = z + 0.5`, `r2 = r * r`.
- **`EntryDef`**: `String id; long n; int type` (1 chest, 2 chests, 3 zone, 4 custom)`; String arg, text; int x, y, z; long cnt;`
- **`WorldDef`** (an immutable snapshot; changes build a NEW one): `String wf, world, name; boolean checklist, bad; long rewardXp, rewardCoins, spotXp, secretXp; SpotDef[] spots; EntryDef[] entries; Long2ObjectOpenHashMap index` (null when there are no spots)`; int secrets;`
- **`SpotReg`** (static):
  - `W` = CHM wf -> WorldDef
  - `ENTRY` = CHM entryId -> wf
  - `STAMP` = CHM wf -> long[2]
  - `DIRTY` = CHM wf -> TRUE
  - `volatile long GEN`, +1 on every change and reload
  - `long NEXT`
  - Every mutation is a `public static synchronized` method that builds the new `WorldDef` and then does `W.put`. Readers never lock (copy-on-write).
- **`ExpData`** (0.1) gains:
  - `found` = CHM wf -> CHM(spotId -> TRUE)
  - `ticks` = CHM entryId -> TRUE
  - `doneW` = CHM wf -> TRUE
  - `volatile long spots, secrets` (found counts, all worlds)
  - `volatile boolean checkDirty`
- **`ExpState`** (0.1) gains `double spotAcc; String inside, insideWf; long lastBanner; String pctWf; long pctGen; String pctStr; boolean wasBusy; int[] tmp = new int[4]`.
- **`ExpTick`** gains `SWITCHED` = CHM UUID -> Long (the last profile switch or busy-cleared time).

**Index build** (`SpotReg.index(SpotDef[])`, javassist-safe, no key iteration needed):
```java
public static it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap index(@PKG@.SpotDef[] sp) {
  if (sp == null || sp.length == 0) return null;
  it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap m = new it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap();
  for (int i = 0; i < sp.length; i++) {
    @PKG@.SpotDef s = sp[i];
    int x0 = @CHU@.chunkCoordinate(s.x - s.r), x1 = @CHU@.chunkCoordinate(s.x + s.r + 1);
    int z0 = @CHU@.chunkCoordinate(s.z - s.r), z1 = @CHU@.chunkCoordinate(s.z + s.r + 1);
    for (int cx = x0; cx <= x1; cx++) {
      for (int cz = z0; cz <= z1; cz++) {
        long k = @CHU@.indexChunk(cx, cz);
        @PKG@.SpotDef[] a = (@PKG@.SpotDef[]) m.get(k);
        int n = a == null ? 0 : a.length;
        @PKG@.SpotDef[] b = new @PKG@.SpotDef[n + 1];
        for (int j = 0; j < n; j++) b[j] = a[j];
        b[n] = s;
        m.put(k, b);
      }
    }
  }
  return m;
}
```
(javassist: declare `int x0`, `int x1` ... one per statement if the combined declaration does not compile.) The largest radius of 128 touches at most 81 columns per spot, and 500 spots build in well under a millisecond.

### 2.8 Migration from 0.1 (nothing lost)
- **Config:** 0.1 lines stay byte for byte. The 0.2 block (2.5) is appended once. 0.1's `apply()` ignores the new keys on a rollback.
- **Player records:** the 0.1 keys are read and written as before, plus `v=2`. `chests.txt` and `chunks/` are untouched. Spot finds, ticks and completion flags live only in the new files, which 0.1 never opens.
- **Chest registry:** unchanged. The loot chests recorded under 0.1 can be used as checklist `chest` entries at once.
- **Rollback 0.2 -> 0.1** is safe: 0.1 ignores `worlds/`, the new player files, `admin.log` and the new config lines. XP already paid to SkyySkills stays, and a later re-upgrade finds everything again. **No "never go back" rule is needed** (tell the orchestrator).
- **Deploy pairing:** none. 0.2 works with the live SkyySkills 0.4.2, SkyyTrees 0.2.1, SkyyCoins 0.1.5 and SkyyProfiles 0.1, and alone.

---

## 3. Discovery spots and secret spots (A1/A2)

### 3.1 Placement (admin, world thread)
- **Add here:** the position is the admin's `TransformComponent.getPosition()` floored (`(int) Math.floor(x)`, the same for y and z; the feet block).
  - The world must not be excluded: `ExpCfg.excluded(name)`. Otherwise: `"-This world never pays exploration (exploration.excludeWorldPrefixes / excludeWorlds) - spots only work in shared worlds"`. Private islands and instances are excluded by default; a new copy of those worlds exists per profile or per run.
  - Refused when the world already has `spots.maxPerWorld` spots or its file is `bad` / hand-edited (2.3).
  - Radius: the typed value, else `spots.defaultRadius`. XP: the typed value, else the island's `secretXp` / `spotXp` when >= 0, else `spots.secretXp` / `spots.defaultXp`.
- **Move here:** same position rule; the id and every find stay.
- **Remove:** a second click or command within 10 s confirms. The spot and its automatic checklist entry go. Profile records keep the old id, which is harmless, because ids are never reused.
- **Edit:** name, radius, XP, secret yes/no, checklist yes/no. Rename keeps the id, so finds stay valid.
- **Teleport:** `Teleport.createForPlayer(currentWorld, new Transform(new Vector3d(x + 0.5, y, z + 0.5), <admin head rotation or new Rotation3f()>))`. It follows the SkyyMenu 0.1.3 `teleport()` order: refuse if a `Teleport` component is already present, append to TeleportHistory first so `/tp back` works, then `addComponent`. The page closes itself afterwards with `setPage(None)`; closing after an action that opens nothing else is fine. Same world only.
- **Admin self-trigger:** after add or move, set the admin's `ExpState.inside = id` and `insideWf = wf`, so the new spot does not fire in their face. They discover it after walking out and back in, unless they are in creative. The admin page hint says: "Admins in adventure mode discover spots like anyone - build in creative, or use /exploreadmin resetme."

### 3.2 Detection (in `ExpTick.tick`, world thread, no allocation)
0.1's `tick()` becomes:
```java
s.acc = s.acc + (double) dt;
s.spotAcc = s.spotAcc + (double) dt;
if (s.spotAcc >= @PKG@.ExpCfg.SPOT_S) { s.spotAcc = 0.0; spotCheck(pr, p, ref, store, u, s); }
if (s.acc < 1.0) return;
s.acc = 0.0;
second(pr, p, ref, store, u, s);
```
`spotCheck` (add it before `tick`, after `second`'s helpers):
1. Return at once when `!SPOTS_ON`. Get the world from `store.getExternalData()`. Return when `excluded(name)`. Then `WorldDef wd = SpotReg.byName(name)`: `ChestReg.wf(name)` is already cached in a CHM, then `W.get(wf)`. Return when `wd == null || wd.index == null`, and set `s.inside = null`.
2. `pos = TransformComponent.getPosition()`. `Object o = wd.index.get(ChunkUtil.indexChunkFromBlock(pos.x(), pos.z()))`. When it is null: `s.inside = null` and return.
3. Loop the `SpotDef[]`. The first spot with `dx*dx + dy*dy + dz*dz <= r2` (dx = px - cx, and so on) that is not `(s.inside, s.insideWf)` is the hit. No hit at all: `s.inside = null` and return. Only the remembered spot hit: return.
4. Blocked states record nothing, so walking in later still pays: creative (unless `creativeXp=true`) and `MovementStates.flying` (unless `noFlyingXp=false`). Gliding and mounting are allowed. Blocked: return without setting `inside`.
5. `String k = ExpIO.pkey(u)` (the only pkey call, on a hit). `d = ExpStore.dataK(k, u)`; return if `d.bad`. Then set `s.inside = hit.id` and `s.insideWf = wd.wf`. If `ExpStore.hasSpot(d, wd.wf, hit.id)`, return (already found). Otherwise `ExpSpot.found(pr, u, k, d, wd, hit, s)`.

`s.inside` is reset on an epoch change and on `resetme`. The per-player cost with no spot nearby is one component read and one map lookup, three times a second.

### 3.3 Award, `ExpSpot.found` (world thread, inside the tick: packets, files and the ledger only; no component writes)
1. `ExpStore.addSpot(d, wf, id, secret)` (synchronized). It returns false when the spot was already found. Otherwise: `found[wf].put(id)`, `spots++`, `secrets++` when secret, `checkDirty = true`, append `spots.txt` `<wf> <id> <d|s>`, dirty.
2. `ExpStore.addOwed(d, xp)`, `saveSoon(k)`, `ExpXp.flush(u, k, d)`. This is 0.1's ledger to `skill:fn:addxp`, with no boosters (SkyySkills bypasses them for Exploration).
3. **Banner:** when `SPOT_BANNER` and `now - s.lastBanner >= BANNER_GAP`, set `s.lastBanner = now` and call `EventTitleUtil.showEventTitleToPlayer(pr, Message.raw(name), Message.raw(sub), secret ? SECRET_MAJOR : MAJOR)`, with sub `Discovery - +500 Exploration XP` or `Secret - +1,500 Exploration XP`.
4. **Sound:** `idx = ExpCfg.sound(secret ? 1 : 0)` (cached getIndex). Skip when `Integer.MIN_VALUE`. Otherwise `SoundUtil.playSoundEvent2dToPlayer(pr, idx, SoundCategory.UI)`. The sound plays even when the banner gap suppressed the banner.
5. **Chat** (gated by the `explore.finds` setting, section 9):
   - `[Exploration] Discovered Old Watchtower - +500 Exploration XP (3 of 12 spots on Fens Island)` in `#ffb070`
   - `[Exploration] Secret found: Hidden Grotto - +1,500 Exploration XP (1 of 3 secrets on Fens Island)` in `#d890ff`
6. `ExpTitles.check(pr, k, d, lvl)` and `ExpTitles.publish(u, d, lvl)`.

### 3.4 Rules
- One find per spot per profile, pays once, no boosters. Skyy Q1-Q3 hold.
- **Secret spots are hidden on `/explore` until found:** "??? Secret spot", with no name, XP or position. Only counts are shown ("2 secrets left on Fens Island"). The bridge never leaks names either.
- A spot added where a player already stands is found on the next check (at most 333 ms later), except by the admin who placed it (3.1).
- Teleporting into a spot counts (Skyy Q8), including an admin's `spot tp` in adventure mode.
- Several spots overlapping: one is handled per check, and the next check gets the next one.
- **Server-phase A3, "first arrival on an island",** already works with this backbone: a spot with a large radius at the island's arrival point.

---

## 4. Island checklist (C2)

### 4.1 Entries
| Type | Added by | Done for a profile when | Default text |
|---|---|---|---|
| spot (discovery or secret) | automatic for every spot with `checklist=yes`; the toggle takes it off | `found[wf]` holds the spot id | the spot name (secret and not found: `??? Secret spot`) |
| `chest` | "Add loot chest here": the **nearest recorded loot chest** (`ChestReg`) within `checklist.chestRadius` of the admin. Refused if there is none: "stand next to a loot chest - a hand-placed chest counts when an admin made it a loot chest with /stash set <droplist>" | 0.1 `isOpened(d, wf, x, y, z)` | `Hidden loot chest` |
| `chests` N | "Add open-N-chests" + a number | `openedCount(d, wf) >= N`, where `openedCount` = size of `opened[wf]` (synchronized) | `Open N loot chests on this island` |
| `zone` | "Add region here" (current region, refused when null: "Hand-built worlds report no Hytale region - use a big discovery spot instead") or "Add all 13 regions" (the 13 named ones, skipping existing) or `check add zone <regionId>` | `d.zones` holds the region (0.1's record; global per profile) | the region name (`ExpDefs.regionName`) |
| `custom` | text, by command or page | `d.ticks` holds the entry id | the admin's text |

- Chest positions are found by walking `ChestReg.W.get(wf)` once per click, using the `compact()` unpack math `x = (int)(k >> 38)`, `z = (int)((k << 26) >> 38)`, `y = (int)((k << 52) >> 52)`.
- A chest entry whose chest has left the registry (broken) stays: done for everyone who opened it, impossible for others. The admin page marks it `(chest gone - remove this entry?)`.
- With `chests.enabled=false`, chest entries cannot complete, and the admin page says so.
- `checklist.maxEntries` counts spot entries too.
- **Display order:** spot entries by n, then the others by n. Re-ordering is left for the server phase.

### 4.2 Progress (one synchronized call, reuses `ExpState.tmp`)
`ExpStore.progress(ExpData d, WorldDef wd, int[] out)` fills `out = {done, total, secretsFound, secretsTotal}`. It returns zeros when `!CHECK_ON || wd == null || !wd.checklist`. `pct = total == 0 ? 0 : done * 100 / total`, rounded down, so 100 only when everything is done. Nested synchronized calls (`isOpened`) re-enter the same class lock.

### 4.3 Completion (in `second()`, world thread)
- `boolean dirty = ExpStore.takeDirty(d)` (a synchronized read-and-clear of `checkDirty`, set by `addSpot`, `addChest`, `addZone`, tick and untick).
- When `dirty && CHECK_ON`: for every `WorldDef wd` in `SpotReg.W.values()` with `checklist` on, run `progress`. When `total > 0 && done == total && !doneW.containsKey(wf)`, run `ExpCheck.complete(...)`:
  - `ExpStore.markDone(d, wf)`: append `done.txt`; if the world was already marked, return.
  - `rewardXp > 0`: owed + flush.
  - `rewardCoins > 0`: pay through `coins:fn:add` `Object[]{UUID, Long}` **only if the function is present** and `ExpIO.pkey(u).equals(k)` (the key resolved at the start of this `second()`; a switch cannot interleave on this thread). No SkyyCoins: the line adds `(coins need SkyyCoins - not paid)`. There is no coin ledger. That matches 0.1's Scavenger rule.
  - Banner title `Fens Island`, sub `Checklist complete - 100%`, major; sound `checklist.sound`; chat `[Exploration] Fens Island checklist complete (100%)! +2,000 Exploration XP, +5,000 coins` in `#ffe08a`.
- **Rules:**
  - Paid once per profile per world. Entries added later lower the % again, but `done.txt` keeps the reward from repeating.
  - An admin removing the last open entry pays nobody by itself. The next progress anywhere triggers the check, which is fair: the player did everything left.
  - A custom tick for an offline or inactive profile is evaluated when that profile next ticks.

### 4.4 `explore:pct:<uuid>` and the current world
In `second()`, the pct is recomputed only when `dirty`, when `s.pctWf != wf`, or when `s.pctGen != SpotReg.GEN`:
- When the current world has a checklist with `total > 0`: `explore:pct:<uuid>` = `"<pct>|<done>|<total>|<island name>"`, written when it changed.
- Otherwise the key is removed.
- Removed also in `retainOnline` and `clearAll` (0.1 cleanup).

### 4.5 Bridge keys (new or changed)
| Key | Shape | Dir |
|---|---|---|
| `explore:<uuid>` | 0.1 string + `,spots:<n>,secrets:<n>,island:<done>/<total>`. The island part comes from `ExpTitles.ISLAND` (CHM UUID -> `"done/total"`), which `second()` sets whenever it recomputes the current world's pct (4.4), and is `0/0` when there is none. `summary()` reads it, so `publish()` keeps its 0.1 signature. | writes |
| `explore:pct:<uuid>` | String `"73|11|15|Fens Island"`; absent = no checklist here | writes |
| `explore:fn:complete` | `Function apply(Object[]{UUID u, String pkey or null, Object entryId (String or Number), Boolean value (optional, default TRUE)}) -> Boolean` | writes (setup; removed in shutdown) |
| `explore:fn:pct` | `Function apply(Object[]{UUID u, String worldName}) -> String` in the pct shape, or null (cached profiles only, never reads files) | writes |
| `skill:stats:Exploration` | 0.1 lines + `"Discoveries - 14 spots found (3 secret) - island checklist 58%"` | writes |
| `settings:def:explore.chunkXp`, `settings:def:explore.finds` + `settings:fn:register` call | Settings-Spec 1.2 | writes |
| `settings:fn:get`, `settings:fn:set`, `coins:fn:add` | contracts | reads |

**`explore:fn:complete` semantics** (a later quest mod's hook; any thread; never throws; never calls another mod; never touches ECS):
1. `u` must be a UUID. The pkey must be null (then `pkey(u)`), or equal `u.toString()`, or be `u.toString() + "-p" + digits`. Anything else gives FALSE, so no junk file names.
2. `SpotReg.ENTRY.get(id)` must exist, and that entry must be `custom`. Otherwise FALSE: spots, chests and zones come from real play, never from the bridge.
3. `ExpStore.complete(k, id, value)` (synchronized, the same lock as `install`):
   - If the profile is cached: update `ticks` and set `checkDirty`.
   - Else: add `"+id"`/`"-id"` to `PENDING_TICKS[k]`, which `install()` merges when that profile loads.
   - Always append the `ticks.txt` line. Replaying it is idempotent.
   - Returns TRUE, including "already ticked".

---

## 5. Admin commands (HANDOFF COMMAND RULES)
Every named command and subcommand is an `AbstractPlayerCommand` with `requirePermission("skyyexploration.admin")` + `setPermissionGroups(new String[0])` (0.1's admin pattern). **Usage variants** use the description-only constructor. Each carries its own `requirePermission("skyyexploration.admin")` and no permission groups, because a variant's own `hasPermission()` is what runs and a variant without groups also re-checks its parent (SkyyCoins 0.1.4 / SkyyBank 0.1.1 notes). **The engine tokenizer treats `[`, `,`, `]`, quotes and backslash specially** (SkyyCoins 0.1.4), so every value that may contain a comma or spaces is a `GREEDY_STRING` last argument, which is read from the raw input tail. That covers `set` values such as `1,2,4,8` or `instance-,skyy-island-`, edit values, custom texts and island names. Spot names typed as one `STRING` token may not contain commas; the page has no such limit, except that 2.4 sanitizing applies everywhere. Generate them with a Python `cmd()` helper (the SkyyGuilds 0.1.1 style). Each constructor must be added before the group constructor that calls `addSubCommand` / `addUsageVariant` (javassist order), and all of them before `ExploreAdminCmd`. Every command body calls one `ExAdminOps` method (section 6.5) and prints its result: `+` green `#9adf86`, `-` orange `#ffb080`, `=` light blue `#9fd0ff`, with the prefix removed and `[Exploration] ` in front.

| Command | Class | Args |
|---|---|---|
| `/exploreadmin` | `ExploreAdminCmd` (execute **opens the admin page**, Spots tab; the 0.1 usage line moves to `help`) | - |
| `/exploreadmin reload` / `stats` / `resetme` | 0.1 classes, extended (below) | - |
| `/exploreadmin help` | `ExAdminHelpCmd`, every line of this table in chat | - |
| `/exploreadmin set <key> <value>` / `get <key>` | `ExAdminSetCmd` / `ExAdminGetCmd` | STRING, GREEDY_STRING / STRING |
| `/exploreadmin spot` | `ExSpotCmd`: usage lines | - |
| `... spot add <name>` | `ExSpotAddCmd` + variants `ExSpotAdd2Cmd` (name radius), `ExSpotAdd3Cmd` (+ xp), `ExSpotAdd4Cmd` (+ secret: `secret|yes|true|1` or `open|no|false|0`) | STRING x1..4 |
| `... spot move <spot>` / `remove <spot>` / `tp <spot>` | `ExSpotMoveCmd` / `ExSpotRemoveCmd` (repeat within 10 s) / `ExSpotTpCmd` | STRING |
| `... spot list` | `ExSpotListCmd`: up to 25 lines `s3 Old Watchtower - 120 64 -45 - r6 - 500 XP - secret - on checklist - 12 m`, sorted by distance | - |
| `... spot edit <spot> <field> <value>` | `ExSpotEditCmd`; field `name|radius|xp|secret|checklist` | STRING, STRING, GREEDY_STRING |
| `/exploreadmin check` | `ExCheckCmd`: usage | - |
| `... check list` | `ExCheckListCmd`: id, type, text, `(n players online have it)` | - |
| `... check add` | `ExCkAddCmd`: usage | - |
| `... check add chest` / `add chests <n>` | `ExCkAddChestCmd` / `ExCkAddChestsCmd` | - / STRING |
| `... check add zone` (+ variant `<region|all>`) | `ExCkAddZoneCmd` + `ExCkAddZoneIdCmd` | - / STRING |
| `... check add custom <text>` | `ExCkAddCustomCmd` | GREEDY_STRING |
| `... check remove <id>` | `ExCheckRemoveCmd` (repeat within 10 s; a spot id means "take off the checklist") | STRING |
| `... check text <id> <text>` | `ExCheckTextCmd` (label of any non-spot entry) | STRING, GREEDY_STRING |
| `... check tick <player> <id>` / `untick <player> <id>` | `ExCheckTickCmd` / `ExCheckUntickCmd` (the player's ACTIVE profile, through `ExpStore.complete`) | PLAYER_REF, STRING |
| `/exploreadmin island` | `ExIslandCmd`: prints name, checklist on/off, rewards, defaults, counts | - |
| `... island name <text>` | `ExIslandNameCmd` | GREEDY_STRING |
| `... island checklist <on|off>` | `ExIslandCheckCmd` | STRING |
| `... island reward <xp> <coins>` | `ExIslandRewardCmd` | STRING, STRING |
| `... island defaults <spotXp> <secretXp>` | `ExIslandDefaultsCmd` (`-1` = config) | STRING, STRING |

- **`set <key> <value>`:** `ExpCfg.setKey`, synchronized.
  - The key must be in `ExpCfg.KEYS`, generated at build time from every `key=` and `# key=` line of the full DEFAULTS (0.1 + 0.2, including the `chest.xp.*` and `zone.xp.*` lines).
  - The value is at most 200 characters and has no line breaks.
  - Rewrite the file in place: the first `key=` line is replaced, else the first commented `#<spaces>key=` line is replaced (un-commented), else the line is appended. Then tmp + move, then `load()`, then the admin log.
  - Reply `"+chests.base = 600 (was 400) - applied now"`. For `titles.chatPriority` the reply ends `" - needs a restart"`. Out-of-range numbers are clamped by `apply()`, which the reply says.
  - **This is the hook the future SkyyMenu admin editor calls** (section 9).
- **`get <key>`:** the file value, or `(not in the file - default <v>)`.
- **`reload`:** first `SpotReg.flushDirty()` (pending in-game world writes), then config, then every world file. Reply: `"...; 4 worlds, 37 spots (9 secret), 22 checklist entries"`.
- **`stats`:** adds per world `fens: 12 spots (3 secret), 18 checklist entries, file ok|bad|edited` and a line `spot checks: <n> in the last 10 s, <avg> us each` (two AtomicLongs updated by `spotCheck`, sampled with `System.nanoTime()` on 1 check in 16 so the timing itself stays cheap).
- **`resetme`:**
  - In memory: also clears `found`, `ticks`, `doneW`, `spots` and `secrets`, and resets `s.inside`.
  - On disk: `deleteLater` for `spots.txt`, `ticks.txt` and `done.txt`.
  - Also drops `PENDING_TICKS[k]`.

---

## 6. Admin page `/exploreadmin` (UI RULES)

### 6.1 Rules
- Inline only, ids without underscores, root anchor Width/Height only, `TextButton` + `EventData.of("a", payload)`, payloads compared exactly (`jsonStr(data, "a").equals("xadd")`).
- Dynamic text only through `b.set`. Button labels are literals: toggles pick one of two fixed strings.
- **No periodic updates, no timers, no hover handlers.** `handleDataEvent` starts with `if (now - this.lastBuild < 1000L) return;`. The engine drops clicks anyway while an update is unacknowledged, and a double click can never remove twice. `build()` sets `lastBuild`.
- **Every click re-checks** `this.playerRef.hasPermission("skyyexploration.admin")`. Otherwise: msg `"You are no longer an admin (skyyexploration.admin)"` + rebuild, nothing else.
- Never close before opening another page. The only close is after a teleport (3.1).
- Lifetime `CanDismiss` (Esc closes).
- Styles: 0.1's `tbs()` at **FontSize 16**. Add a red `BRED` (`#6a2626` / `#8a3434` / `#401616`, text `#ffe0e0`) for Remove and Sure. Text boxes use the SkyyGuilds box: Group `Background: #16263a` + `TextField { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: n; PlaceholderText: "..."; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }`.
- **Excluded world:** the page still opens with the Spots tab showing `"This world never pays exploration (<reason>) - spots and checklists only work in shared worlds."`, with no Add buttons.

### 6.2 Frame (1120 x 900; Python asserts the height sum <= 900 and each row's width sum <= 1080)
```
#SkyyXaRoot  Group  Anchor (Width 1120, Height 900)  Background #0b1524(0.97)  Padding (Horizontal 20, Vertical 12)  LayoutMode Top
  Group (Height 3, Background #e0a040)
  #SkyyXaHead Group Height 52 LayoutMode Left
    Label #SkyyXaTitle (Width 580, 24 bold #ffe08a)   "Exploration admin - Fens Island"
    TextButton #SkyyXaTab0 "Spots" | #SkyyXaTab1 "Checklist" | #SkyyXaTab2 "Island"   (150 x 44, 8 px gaps; active tab = gold "on" style)
  Label #SkyyXaSub (Height 28, 15, #9fb8cc)   "World fens - 12 spots (3 secret) - 18 checklist entries - you stand at 120 64 -45"
  #SkyyXaBody Group Height 690 LayoutMode Left      (tab content: list Width 600 | gap 20 | detail Width 460)
  Label #SkyyXaMsg (Height 34, 17 bold #ffe08a, centred)   status line (the op result without its prefix)
  #SkyyXaFoot Group Height 52 LayoutMode Left: TextButton #SkyyXaRefresh "Refresh" (170 x 44) + Label hint (15, #9fb8cc)
     "Changes save at once to worlds/<file>.properties - admin.log keeps who changed what"
```
Height: 24 + 3 + 52 + 28 + 690 + 34 + 52 = 883.

### 6.3 Tabs
**Spots** (list left, `#SkyyXaList`, LayoutMode Top):
- Header Label (Height 32, 18 bold): `Spots in this world - 12 (3 secret) - page 1 of 2`.
- 8 rows x 70 px. `Group #SkyyXaRow<i>` (Height 66, LayoutMode Left, Background `#142030`, or `#24405c` when selected):
  - Group (Width 470, LayoutMode Top) with Label `#SkyyXaRowN<i>` (Height 34, 18 bold, `#ffb070` for discovery or `#d890ff` for secret): the name.
  - Label `#SkyyXaRowS<i>` (Height 28, 14, `#c8d6e4`): `s3 - discovery - r 6 - 500 XP - 12 m away - on checklist`.
  - Then `TextButton #SkyyXaEdit<i> "Edit"` (110 x 48), or Label "Editing" when selected.
- Pager row (Height 52): `#SkyyXaPrev "< Prev"`, `#SkyyXaNext "Next >"`, `#SkyyXaSort "Order: newest"` / `"Order: nearest"` (160 x 44).
- The row ids are stored in `this.rowIds[]` at build time. `xedit<i>` resolves through it; a vanished id replies `"-That spot was removed - Refresh"`.

**Spots** (detail right, `#SkyyXaDet`, LayoutMode Top):
- Every detail row is at most 460 wide: widths below include 10 px spacer Labels between items.
- `New spot where you stand` (20 bold). Rows of 52:
  - Label `Name` (90) + box `#SkyyXaNName` (MaxLength 40, placeholder `Spot name`, 350 x 44)
  - Label `Radius` (90) + `#SkyyXaNRad` (100, placeholder the default), Label `XP` (60) + `#SkyyXaNXp` (140, placeholder the default)
  - `#SkyyXaNSec "Secret: No"` / `"Secret: Yes"` (200 x 44, page field `newSecret`) + `#SkyyXaAdd "Add here"` (230 x 44, green)
- Hint (Height 26, 14): `Blank radius / XP = 6 / 500 (secret 1,500). Admins in adventure mode discover spots too.`
- Separator Group (Height 2, `#2c4258`), then `Selected: Old Watchtower (s3)` (20 bold) or `Click Edit on a spot`. Rows of 52:
  - box `#SkyyXaEName` (300) prefilled + `#SkyyXaRen "Rename"` (140)
  - `#SkyyXaERad` (90) + `#SkyyXaEXp` (130) prefilled + `#SkyyXaSave "Save radius + XP"` (200)
  - `#SkyyXaESec "Secret: Yes"` / `"Secret: No"` + `#SkyyXaEChk "On checklist: Yes"` / `"On checklist: No"` (220 each)
  - `#SkyyXaMove "Move here"` + `#SkyyXaTp "Teleport"` + `#SkyyXaRm "Remove"` / `"Sure? Remove"` (BRED, 10 s) (140 each)
  - Label `#SkyyXaEInfo` (Height 30, 14): `at 120 64 -45 - found by 3 of 5 online players`
- The found count reads cached records only: `ExpStore.cached(pkey(p))` for online players in this world.

**Checklist:**
- List left: same row shape. `#SkyyXaCRow<i>`, text `#SkyyXaCRowN<i>` / `#SkyyXaCRowS<i>` (`7 - loot chest - 130 70 -60 - 2 online players have it`, or `s3 - spot (edit on the Spots tab)`), `TextButton #SkyyXaCEdit<i> "Edit"`, 8 per page, the same pager (no sort). Header: `Checklist - 18 entries (12 spots) - checklist ON`, with OFF in `#ff9a70`.
- Detail right, `Add to the checklist`:
  - `#SkyyXaCAddChest "Add loot chest here"` (440 x 44)
  - `#SkyyXaCAddZone "Add region here"` + `#SkyyXaCAddAll "Add all 13 regions"` (215 each)
  - box `#SkyyXaCText` (290, MaxLength 80, placeholder `Task text`) + `#SkyyXaCAddCustom "Add custom"` (140)
  - box `#SkyyXaCNum` (210, placeholder `10`) + `#SkyyXaCAddCount "Add open-N-chests"` (220)
- Separator, `Selected: 10 - custom`:
  - box `#SkyyXaCEText` (290) prefilled + `#SkyyXaCSave "Save text"` (140)
  - box `#SkyyXaCPlayer` (200, placeholder `Player name (online)`) + `#SkyyXaCTick "Tick"` + `#SkyyXaCUntick "Untick"` (115 each; custom only)
  - `#SkyyXaCRm "Remove"` / `"Sure? Remove"`. For a spot entry the detail says `This is a spot - edit it on the Spots tab` + `#SkyyXaCOff "Take off the checklist"`.

**Island:**
- box `#SkyyXaIName` prefilled + `#SkyyXaISaveName "Save name"`
- `#SkyyXaIChk "Checklist: ON"` / `"Checklist: OFF"` (this world)
- `Reward at 100%`: `#SkyyXaIRwXp` + `#SkyyXaIRwCo` (placeholders `XP`, `coins`) + `#SkyyXaISaveRw "Save rewards"`, with a note `coins need SkyyCoins` when `coins:fn:add` is absent
- `Default XP for new spots here`: `#SkyyXaIDefSp` + `#SkyyXaIDefSe` + `#SkyyXaISaveDef "Save defaults"` (blank or `-1` = config)
- Server-wide switches (write config via `setKey`): `#SkyyXaISpots "All spots: ON"` / `"OFF"` (`spots.enabled`), `#SkyyXaIChecks "All checklists: ON"` / `"OFF"` (`checklist.enabled`)
- Left column: `Players in this world` - up to 10 Labels `#SkyyXaIP<i>`: `Skyy (profile 2) - 7 of 12 (58%) - 5 spots found`, from cached records only
- Note Label: `Every other number: /exploreadmin set <key> <value> (see config.properties)`

### 6.4 Payloads and text keys
- **Payloads:**
  - Navigation: `xtab0..2`, `xrefresh`, `xprev`, `xnext`, `xsort`
  - Spots: `xedit0..7`, `xnsec`, `xadd`, `xren`, `xsave`, `xesec`, `xechk`, `xmove`, `xtp`, `xrm`
  - Checklist: `xcedit0..7`, `xcchest`, `xczone`, `xczall`, `xccustom`, `xccount`, `xcsave`, `xcrm`, `xctick`, `xcuntick`, `xcoff`
  - Island: `xiname`, `xichk`, `xirw`, `xidef`, `xispots`, `xichecks`
- **Text keys** (`.append` on the buttons that need them): `@XNName @XNRad @XNXp` (xadd), `@XEName` (xren), `@XERad @XEXp` (xsave), `@XCText` (xccustom), `@XCNum` (xccount), `@XCEText` (xcsave), `@XCPlayer` (xctick, xcuntick), `@XIName` (xiname), `@XIRwXp @XIRwCo` (xirw), `@XIDefSp @XIDefSe` (xidef).
- No `Validating` (Enter) bindings: Enter does nothing, so nothing is ever added by accident.
- A refused op keeps what the admin typed. The page field `keep<Key>` is set back into `.Value` on rebuild (the Guilds keep pattern). A successful op clears it.
- Page fields: `tab, page, sort, sel, newSecret, confirm, confirmAt, msg, lastBuild, rowIds[]`, plus the keep strings.

### 6.5 `ExAdminOps` (shared by page and commands, world thread of the admin)
- Every method is `static`. Its first arguments are `(PlayerRef pr, Ref ref, Store st, World w, ...)`, and it returns a String prefixed `+`, `-` or `=`.
- Order inside each op:
  1. permission
  2. excluded world
  3. `SpotReg` bad or edited file (2.3)
  4. argument parse + sanitize (2.4)
  5. the `SpotReg` synchronized mutation (new snapshot, `GEN++`, `ENTRY` map updated, `DIRTY[wf]`)
  6. `SpotReg.saveSoon(wf)`: scheduler task, atomic write, stamp updated, `DIRTY` cleared; a failure stays dirty, `ExpSaver` retries every 2 s and warns once a minute
  7. the admin log line
  8. `ExpState.inside` for add and move
- Remove confirm: `CONFIRM` = CHM adminUuid -> `"rm|<wf>|<id>|<millis>"`. The second call within 10 s with the same key executes.
- **Two admins:** mutations are serialized by the lock. A page listing a spot another admin removed answers `"-That spot was removed - Refresh"`. Last write wins per field.

---

## 7. `/explore` changes (player page, still inline, rebuilt only on clicks, 1 s click guard added)

### 7.1 Bigger page (UI rule "BIG readable pages")
- **Root** `#SkyyExRoot` 1120 x 800, Padding (Horizontal 20, Vertical 12).
- **Head** Height 48: 4 tabs `Overview | Zones | Titles | Checklist` (150 x 42, 8 px gaps). `#SkyyExLvl` Width 440, 17 bold, End.
- **Note** Height 24, font 13. **Accent** 2. **Body** Height 640. **Foot** Height 52: buttons 170 / 230 x 42, and `#SkyyExMsg` Width 600, font 15.
- **Every body font +2** from 0.1.
- 0.1's tab loop in `build()` and `handleDataEvent` (`i < 3`) and the clamp (`t > 2`) become 4 tabs (`i < 4`, `t > 3`). `/title` still opens tab 2.
- **Build assert:** 24 + 48 + 24 + 2 + 640 + 52 <= 800.
- The NOTE text gains `- discoveries`.

### 7.2 Overview: 2 rows x 4 cards
- Card size 258 x 150, gaps 16 (4 x 258 + 3 x 16 = 1080). Icon group 72 with a 60 px `ItemIcon`. Text group 170: head 13 (Height 24), value 20 bold (Height 36), sub 13 wrap (Height 78). Row Height 158, Padding Top 8.
- Cards 0-5 keep 0.1's content in the same order. New cards:
  - **6 Discoveries**, icon `Furniture_Flag_Orange` (`must()`), color `#ffb070`. Value `14 spots found`, sub `3 secrets - 5 spots left here (2 secret)`, or `No spots in this world` / `Spots are off on this server`.
  - **7 Island**, icon `Deco_Book_Pile_Small`, color `#9adf86`. Value `Fens Island 58%`, sub `7 of 12 done - Checklist tab`, or `No checklist in this world`.
- Info lines: the 0.1 lines at font 15 (Height 28), plus `Discoveries - admins place named spots (and hidden secret spots) on islands - the first visit pays XP`.

### 7.3 Checklist tab (`extab3`)
- **Island switcher** (Height 48): `TextButton #SkyyExCkPrevW "< Island"`, Label `#SkyyExCkName` (Width 620, 20 bold, centred) `Fens Island (you are here) - 1 of 3`, `TextButton #SkyyExCkNextW "Island >"`.
  - Islands = every WorldDef with the checklist on and total > 0, the current world first, then by name. The page field `ckWorld` holds the world file; the start is the current world, else the first.
  - No islands at all: one centred Label `No island checklists on this server yet - admins set them up with /exploreadmin`.
- **Header** Label `#SkyyExCkHead` (Height 30, 17 bold): `7 of 12 done - 58% - secrets 1 of 3`. Progress bar Group `#SkyyExCkBar` (Width 1080, Height 16, `#1d2c3c`, LayoutMode Left) with Group `#SkyyExCkFill` (inline `Anchor: (Width: <pct x 1080 / 100>, Height: 16)`, `#9adf86`; omitted at 0).
- **Rows:** two columns `#SkyyExCkL` / `#SkyyExCkR` (Width 530), 9 rows each (Height 46) = 18 per page. Each row is `Group #SkyyExCkRow<i>` LayoutMode Left:
  - Label `#SkyyExCkS<i>` (Width 80, 15 bold): `Done` (`#9adf86`) / `-` (`#7f94a8`)
  - Label `#SkyyExCkT<i>` (Width 330, 15, wrap): the entry text; `??? Secret spot` in `#d890ff` when secret and not found
  - Label `#SkyyExCkV<i>` (Width 110, 14, End): `+500 XP` for a spot, `3/10` for chests N, `region` for a zone, empty for custom and chest
- **Pager** (Height 48): `#SkyyExCkPrev "< Prev"` / `#SkyyExCkNext "Next >"` + Label `page 1 of 2`.
- **Footer** Label (13, `#9fb8cc`): `Reward at 100%: +2,000 Exploration XP, +5,000 coins` or `No reward set for this island`.
- **Payloads:** `extab3`, `exwp`, `exwn`, `excp`, `excn`, matched with the trailing quote like 0.1.
- The tab never reveals secret names, positions or chest coordinates.

### 7.4 Titles (+2, derived like 0.1)
| id | Name | kind | Requirement |
|---|---|---|---|
| `discoverer` | Discoverer | 4 (spots found, all worlds, `d.spots`) | 25 |
| `secretkeeper` | Secret Keeper | 5 (secrets found, `d.secrets`; the flag at find time from `spots.txt`) | 10 |

- `KIND_COLOR += ["#ffb070", "#d890ff"]`. `earned()` gains kinds 4 and 5. `assert len(TITLES) == 23` and ids unique, lowercase, one word.
- The mask stays a `long` (23 < 64).
- Text: `Find 25 discovery spots` / `Find 10 secret spots`.
- The Titles tab gets 12 rows per column at Height 44, which fits 640.

### 7.5 Zones tab
It keeps its content. The columns grow to 530, rows are 24 px at font 15, and headers 30 px at font 17.

---

## 8. Profiles, multiplayer, threads, safety

| Piece | Thread | Lock / key |
|---|---|---|
| Spot check + award | the player's world thread (inside `ExpTick`) | `pkey(u)` once per hit; `ExpStore` class lock for `addSpot` |
| Checklist progress / completion | the player's world thread (`second()`) | `ExpStore` lock; key resolved at the start of `second()`, re-checked before coins |
| Admin ops | the admin's world thread (page click / command) | `SpotReg` class lock; file writes on the scheduler |
| `explore:fn:complete` | any thread | `ExpStore` lock; `PENDING_TICKS` + `ticks.txt` for uncached profiles |
| `explore:fn:pct`, the page's "found by N" | any / world thread | cached records only, never file reads |
| World file writes | `HytaleServer.SCHEDULED_EXECUTOR` | snapshot read under the `SpotReg` lock, I/O outside it (a synchronized block holds one call: `snapWorld(wf)` returns the text) |

- **Per profile (contract rules 1-4):**
  - Every new file is under `players/<pkey>/`, and caches are keyed by the pkey String.
  - On an epoch change (0.1 `epochChanged`, first sight = baseline), reset `s.inside`, `s.pctWf`, `s.pctStr` and `s.lastBanner`, and republish `explore:*` within 1 s.
  - No data ever moves between keys.
  - Spot finds, ticks and completions are separate per profile, as Skyy Q1 wants.
  - Private island worlds are excluded, so no island-per-profile spot confusion is possible.
- **`profile:busy` and the afterSwitch window (SkyyVault idea):**
  - 0.2 adds **no new item moves.** Spots, ticks and completions give XP and coins through the ledger or bridge only.
  - The one item move is 0.1's **chest luck roll** into the inventory. So `ExpAward.chestOpened` step 1 now also refuses (no record, retry on the next open) while `now - SWITCHED[u] < AFTER_SWITCH_MS`.
  - `SWITCHED[u]` is set in `second()` when the epoch changes (not at the baseline) and when `profile:busy:<uuid>` goes from present to absent (`s.wasBusy`). It is removed in `retainOnline` with the other per-UUID maps.
  - Chat, at most once per 10 s: `[Exploration] Loot chests count again in 23 s (your profile just switched)`.
  - Reason: a crash inside SkyyProfiles' 30 s marker window rolls the inventory back, which would lose the luck item while the chest stayed recorded as opened.
- **Several players in one shared world:** each profile has its own found set, and one spot pays each profile once. A chest entry is done per profile (0.1's per-profile opened set). Two admins are covered in 6.5.
- **Anti-exploit:**
  - Flying or creative records nothing (Skyy's rule, applied to every source).
  - Teleports count (Q8).
  - A hacked client can spoof `flying` (0.1 known limit).
  - Spot XP comes only from config and world files an admin controls.
  - `explore:fn:complete` only ticks custom entries.
  - The 1 s click guard + 10 s confirm stops double removes.
- **Hot-path budget:** zero allocations per spot check without a hit (a primitive `long` key, snapshot arrays, the cached world-file-name map). The `ExpState.tmp` int[] is reused for progress. Strings are built only for chat, banners and admin output.

---

## 9. Settings registry adoption (small) and the future admin editor
- **Player settings (research/Settings-Spec.md 3.12; no SkyyMenu = today's behaviour):**
  - Add `notifyOn(u, key)` and `regSetting(...)` from Settings-Spec 1.3 to `ExpIO` (it has the creating `bridge()`).
  - In `setup()`, register:
    - `regSetting("explore.chunkXp", "Exploration map XP", "skills", true, "+1,240 Exploration XP from 18 new chunks - at most every 30 s")`
    - `regSetting("explore.finds", "Exploration finds", "skills", true, "Loot chests, chest luck, new zones, discoveries, checklists and new titles")`
  - **Gate only the `sendMessage` calls:**
    - The chunk line is shown when `!d.quiet && notifyOn(u, "explore.chunkXp")`.
    - The chest, luck, Scavenger, zone, spot, secret, checklist-complete and new-title lines need `notifyOn(u, "explore.finds")`.
    - Banners, sounds, XP and records are never gated.
  - **`/explore quiet`:**
    - With `settings:fn:set` present: when the line is shown, set `explore.chunkXp` false. When it is hidden, set it true and clear `d.quiet`. Reply `"(also in /settings)"`.
    - Without it: flip `d.quiet` (0.1).
- **Admin editor (SkyWynn-Server-Setup-Plan.md; research/Server-Setup-Spec.md is being written by another workflow):**
  - 0.2 does not guess that contract.
  - Every config write already goes through `ExpCfg.setKey(key, value)`, and every island value through `ExAdminOps`, both logged. When the shared editor's register-on-the-bridge contract lands, SkyyExploration 0.2.x registers its keys and hands the editor `setKey` as the setter.
  - Until then: the admin page covers spots, checklists, island values and the two master switches; `/exploreadmin set|get` covers every other key; and the file always matches.

---

## 10. Build notes (for the agent)
- **Classes** (`pool.makeClass` up front, like 0.1; add members in this order, methods before callers):
  - `ExpDefs`, `ExpCfg` (+ `ensureDefaults`, `KEYS`, `setKey` after `load`, `sound(int)`), `SpotDef`, `EntryDef`, `WorldDef` (fields + ctor)
  - `ExpData` (+ fields), `ExpState` (+ fields), `ExpIO` (+ `notifyOn`, `regSetting`, `adminLog`), `ChestReg` (+ `nearest(wf, x, y, z, r)`)
  - **`SpotReg`** (load, parse, index, `snapWorld`, `saveSoon`, `flushDirty`, `byName`, `byWf`, `resolveSpot`, the mutations, the counter)
  - `ExpStore` (+ `spotsFile`, `ticksFile`, `doneFile`, `readFile` reading them, `install` merging `PENDING_TICKS`, `addSpot`, `hasSpot`, `foundHere`, `openedCount`, `complete`, `markDone`, `isDone`, `takeDirty`, `progress`, reset extension), `SaveTask`, **`WorldSaveTask`** (Runnable)
  - `ExpSkill`, `ExpXp`, `ExpTitles` (+ kinds 4 and 5, summary), **`ExpSpot`** (found, banner, sound), **`ExpCheck`** (complete, pct string, entry labels)
  - `ExpAward` (+ afterSwitch), `OpenCheck`, `ChestSpawnSys`, `ChestSpawnLateSys`, `ChestOpenSys`, `ExpTick` (+ `spotCheck`, `SWITCHED`, pct publish, completion), `ExpSaver` (+ `SpotReg.flushDirty` every run)
  - `TitleFormatter`, `ChatWrap`, `ChatHook`, `ExpStatsFn` (+ line), `ExpTitleFn`, **`ExpCompleteFn`**, **`ExpPctFn`**
  - `ExplorePage` (bigger + Checklist tab), **`ExAdminOps`**, **`AdminPage`**
  - the command classes (section 5, subcommands and variants before their groups, groups before `ExploreAdminCmd`)
  - the plugin
- **Plugin `setup()`:**
  - `SpotReg.DIR = base.resolve("worlds")` and `SpotReg.loadAll()` right after `ChestReg.loadAll()`, before any system registers.
  - `ExpCfg.ensureDefaults()` inside `load()`.
  - Register the two settings; put `explore:fn:complete` and `explore:fn:pct`.
  - The log line gains `; N worlds, M spots (S secret), E checklist entries`.
  - **No new `registerSystem`** (one per class, unchanged: ChestSpawnSys or its fallback, ChestOpenSys, ExpTick).
- **`shutdown()`:** `SpotReg.flushDirty()` before 0.1's flushes, then remove both new functions with `b.remove(key, fn)`.
- **Tokens and probes** (add to `T` and the `B.probe` list):
  - `ETU#showEventTitleToPlayer`
  - `com.hypixel.hytale.server.core.universe.world.SoundUtil#playSoundEvent2dToPlayer`
  - `com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent#getAssetMap`
  - `com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap#getIndex`
  - `com.hypixel.hytale.protocol.SoundCategory#UI`
  - `com.hypixel.hytale.server.core.modules.entity.teleport.Teleport#createForPlayer`, `#getComponentType`
  - `com.hypixel.hytale.math.vector.Transform`, `com.hypixel.hytale.math.vector.Rotation3f`
  - `com.hypixel.hytale.server.core.modules.entity.component.HeadRotation#getRotation`, `#getComponentType`
  - `com.hypixel.hytale.builtin.teleport.components.TeleportHistory#append`, `#getComponentType`
  - `PGM#setPage`, `com.hypixel.hytale.protocol.packets.interface_.Page#None`
  - `it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap#get`, `#put`
  - `CHU#indexChunk`, `CHU#chunkCoordinate`
  - `ATY#GREEDY_STRING`, `ATY#PLAYER_REF`
  - `EVD#append`, `UEB#addEventBinding`
  - `ST#addComponent`, `ST#ensureAndGetComponent`
  - `PR#getWorldUuid`, `UNI#getWorld`
- **Build-time asserts:**
  - the 5 sound ids and 2 new icons exist
  - `len(TITLES) == 23`
  - DEFAULTS ASCII, and every 0.2 key appears exactly once in DEFAULTS
  - `ExpCfg.KEYS` has no duplicates
  - the admin page height sum <= 900 and each row width <= 1080
  - `/explore` height <= 800
  - the explore card row = 1080
  - every UI id matches `#[A-Za-z0-9]+`: lint also fails on underscores
- **Manifest description:** add discovery and secret spots, island checklists, and `/exploreadmin` in-game setup. `IncludesAssetPack` stays False.

---

## 11. Test plan

### 11.1 Static (before any deploy)
1. `python build_skyyexploration_0.2.py` ends with `assembled ...SkyyExploration-0.2.jar`. The classes-written count is printed.
2. `python tools/ci/lint.py`: 0 fails, and no new command WARN (every admin class has `requirePermission`).
3. `python tools/deploy_set.py --check` only (the orchestrator pins 0.2 later).
4. **Scratch only**, in `tools/dev/scratch/r2/` and deleted afterwards: load the jar in jpype with `-Xverify:all` next to HytaleServer.jar and check that every class verifies. Then, with `ExpStore.DIR` / `SpotReg.DIR` pointed at the scratch folder:
   - `SpotReg.index` on 3 fake spots: r 6 at a chunk corner touches 4 columns, r 64 in a chunk middle touches 25.
   - `ExpStore.progress` on a fake `WorldDef` with each entry type.
   - Parse the 2.3 example file, write it, parse again: the same data, and a second write is byte-identical to the first.
   - `ExpCompleteFn` on an uncached pkey queues a `ticks.txt` line (after `ExpIO.drain()`), and a following `install` merges `PENDING_TICKS`.
   - Bad pkeys, spot ids and unknown ids return FALSE.

### 11.2 In game, one account (Skyy; admin; adventure mode unless noted)
1. **Server log:** `[SkyyExploration] 0.2 ready ... 0 worlds, 0 spots`. No errors. The 0.2 config block is appended once, and a restart does not add it again. 0.1 records (zones, chests, title) are all still on `/explore`.
2. `/explore`: the bigger page, 4 tabs, 8 cards. Nothing is clipped at 1080 high. Checklist tab: `No island checklists on this server yet`.
3. **Creative:** `/exploreadmin`, Spots tab, name `Old Watchtower`, Add here. The list shows it, `worlds/<wf>.properties` has the `spot.s1` line, and `admin.log` has one line. Add `Hidden Grotto` with Secret: Yes.
4. **Adventure:** walk into the watchtower radius. Banner `Old Watchtower` / `Discovery - +500 Exploration XP` + sound + chat. `/skills` shows Exploration +500 (exact, no boosters). Walk out and in again: nothing. Relog: still found.
5. Fly (`/fly`) into the grotto: nothing. Land and walk in: a big banner, the Medium sound, the purple chat line. Standing inside a spot 30 s: no repeats (`/exploreadmin stats` shows a low per-check time).
6. **Page edits:**
   - Rename with a new name: the file updates and the id stays s1, still found.
   - Save radius 12 + XP 800.
   - Secret toggles, checklist toggle.
   - Move here moves the spot.
   - Teleport lands at the spot and the page closes. `/tp back` returns.
   - Remove: the button turns into `Sure? Remove`, the second click removes.
   - A double click within 1 s does not act twice.
7. **Commands:** `/exploreadmin spot add Old_Mill 5 300 secret` (4 tokens) makes a secret "Old Mill". `spot add "Tall Tree" 8` (quotes, NEEDS A TEST). `spot list`, `spot edit s3 name Miller's Hut`, `spot tp mill` (prefix), `spot remove s3` twice.
8. **Checklist tab:**
   - Stand at a recorded loot chest (new terrain, `/exploreadmin stats` captures > 0), Add loot chest here.
   - Add region here, Add all 13 regions, a custom `Help the fisherman`, open-N-chests with 2.
   - `/explore` Checklist shows the rows. Secret spots show `??? Secret spot`. The % matches.
9. **Completion:** set the island reward to 2000 XP + 500 coins. Open the chest, find the spots, then `/exploreadmin check tick <me> <custom id>`. At 100%: banner `Fens Island` / `Checklist complete - 100%`, +2,000 XP, +500 coins (`/balance`). Untick and re-tick: no second reward.
10. **Hand edit:** change a spot's XP in the file while the server runs, then try Rename in game: refused (edited file). `/exploreadmin reload`, and the new XP shows. Break the file syntax, reload: a WARN, the old copy is kept, and edits are refused until it is fixed.
11. `/exploreadmin set spots.defaultXp 700`: the file line changes and the Add hint shows 700. `get spots.defaultXp`. `set titles.chatPriority 1` says it needs a restart.
12. `/exploreadmin` in your private island world: `This world never pays exploration ...`, no Add buttons.

### 11.3 Two accounts (A = Skyy admin, B = player)
1. B walks into A's spot: B gets their own banner and XP. A's record is unchanged.
2. B on the admin page: `/exploreadmin` is refused (no permission). A revokes their own `skyyexploration.admin` while the page is open, and the next click says `no longer an admin`.
3. Both admins (give B the node) edit the same world. B removes a spot A has selected; A's next click on it says `removed - Refresh`. The file holds both changes.
4. A ticks B's custom entry from the page (the player box `B`). B's `/explore` shows `Done` within 1 s. The Island tab shows B's %.
5. B completes the island and gets the reward. A (not complete) does not.

### 11.4 Profiles (SkyyProfiles)
1. B creates profile 2: `/explore` Checklist shows 0%, and the spots can be found again (banner, XP to profile 2). Switch back: profile 1's finds are there.
2. Right after a switch, open a new loot chest: `Loot chests count again in N s`. After 30 s it pays.
3. A runs `/exploreadmin check tick B <custom id>` while B is on profile 2. It is ticked on profile 2 only; B switches to profile 1 and it is open there. Ticks for an inactive or offline profile through `explore:fn:complete` are covered by the 11.1 scratch test.

### 11.5 Fallbacks
1. Without SkyySkills: the spot XP waits in the owed ledger, the page says so, and it is paid after install.
2. Without SkyyCoins: the completion says `(coins need SkyyCoins - not paid)` and the XP is still paid.
3. **Rollback:** deploy 0.1 again (test world only), and 0.1 runs normally. Deploy 0.2 again: spots, finds, ticks and completions are all back.

---

## 12. Left for the server phase (not in 0.2)
- **Content:** the actual spots, secrets and checklists of the hub and every chain island (builders fill them in with this page).
- **Several islands in one world:** a `group` per spot and entry, with one checklist per group. The file format ignores unknown keys, so it can be added later.
- **Checklist entry re-ordering** (Up / Down) and per-entry rewards.
- **Echo Shards (C1)** as a new entry type (a clickable block + hand-in NPC). Quest-driven entries through `explore:fn:complete` once SkyyQuests exists. A "mark spot found" bridge call for cutscenes.
- **Rewards beyond XP and coins at 100%:** island titles, cosmetics, accessory slots, bag boosts (Skyy Q4), and the lootrun camp (D4).
- **D1/D2 warps** unlocked by discovering a town spot (per-profile warp list, vanilla warp points) and scroll unlocks.
- **D5 map reveal** (POIs after discovery) and **B3 finder sense** (compass or HUD hint to the nearest unfound spot); they need the map / HUD widget.
- **Admin visual aids:** particles or markers showing spot radii in the world, spot shapes other than spheres (box, cylinder), and per-spot level requirements.
- **Undo and history** for admin changes (admin.log has the data), and export / import of an island setup (copying the world file already works when the world name matches).
- **SkyyMenu "Mods" admin editor adoption** (register the config keys, `ExpCfg.setKey` as the setter), plus a SkyyMenu admin entry that opens `/exploreadmin`.
- **SkyyWorldGen islands** (solo): whether generated zone regions or auto-placed spots are used there is open research.
- **Read SkyySkills' live `perk.exploration.staminaPerLevel`** instead of the duplicated `display.staminaPerLevel` (Server-Setup-Research note).

## 13. For the orchestrator (not the builder)
- **Deploy:** SkyyExploration 0.2 alone (`("SkyyExploration", "0.2")` in `tools/deploy_set.py` once reviewed). It needs no other version change, and rollback to 0.1 is safe (2.8).
- **TEST-CHECKLIST:** a new section from 11.2-11.5, riskiest first: arrival detection + banner, hand-edit guard, two-admin edits, completion reward, afterSwitch chest gate.
- **HANDOFF:** the 0.2 row once built. Open question for Skyy: default XP for discovery (500) and secret (1,500) spots, and whether finishing an island should pay coins by default (it is 0 now).
