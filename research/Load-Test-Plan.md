# Load-test plan - 2026-10-14

How to find out whether the SkyWynn pack stays smooth with many players, without 50 real clients. Read-only research: `tools/smoke_test.py`,
`research/Code-Structure-Audit.md` (the 2026-10-13 lag audit), and a class listing of the cached `HytaleServer.jar` (0.7.1). Nothing was started.
`tools/load_test.py` is NOT written (reason in section 6).

## 0. Short version

1. **Clients cannot be simulated cheaply.** The server speaks QUIC (`--transport QUICHE`); a bot client has to do the handshake and the join packets itself. That is a research
   spike (section 5, phase 3), not a quick tool. Skyy's own 2-player tests stay the only real-client test.
2. **Most of our cost can still be measured without clients**, in three layers: (A) an idle offline server with the full SET (boot time, memory, timers firing on an empty
   server, "Task took N ms" warnings); (B) a synthetic data load - N fake profiles' save files on disk, so every start-up scan, save, interest sweep and leaderboard
   reads real volume; (C) an in-JVM micro-benchmark of our own periodic tasks and save writers with N fake players (the harnesses `test_skyy*.py` already run our classes on
   the real engine in one JVM).
3. The engine already has the metrics we need: `/world tps`, `/server stats` (+ `cpu`, `memory`, `gc`), `/chunk storage stats`, `/entity count`, and the slow-task WARN
   "Task took N ms" that the lag audit counted (24 hits of 34-112 ms in the 10-10 / 10-11 logs, almost all at join). Exact command spellings are UNVERIFIED (class names only):
   `WorldTpsCommand`, `ServerStatsCommand` / `Cpu` / `Memory` / `Gc`, `ChunkStorageStatsCommand`, `EntityCountCommand`, plus `MetricSystem` / `MetricsRegistry` for per-system ECS timings.
4. **The cost to expect is on the world thread at join, not per tick**: 32 periodic timers (Hud, Sacks x4, Coins, Collections, Bank, Skills, Trees, Vault, Merchants ...) loop
   online players with one `world.execute` each, and `PlayerReadyEvent` fires on every world switch (Gear 7 handlers, Menu 12, Classes 4, Islands 4 ...). A bot-less test only sees these
   at N = 0, which is why layer C (fake players) matters.

## 1. What to measure

| Metric | Why | How to read it | Target (placeholder, set from the first run) |
|---|---|---|---|
| Boot time to "Hytale Server Booted!" with the SET | slow start = bad restarts | smoke_test already waits for it | under 60 s on Skyy's PC |
| Heap after boot + after 10 min idle | leaks (SkyyProfiles' DATA cache never drops entries) | `/server stats memory`, or jcmd-free: `-Xlog:gc` to the log | flat after boot |
| Tick time / TPS per world | the headline | `/world tps` (sample every 30 s) | 20 TPS, 95th percentile tick under 30 ms |
| "Task took N ms" WARNs naming `com.skyy` | our world-thread stalls | grep the log (`chat_digest` style) | zero over 25 ms |
| Our per-tick systems | ECS systems that run every tick (the `registerSystem` classes, one per mod class) | `MetricSystem` / engine metrics if exposed; else count by a stopwatch counter in the harness | each under 0.2 ms at 50 players |
| Periodic timers | the ~32 poll loops | harness (layer C): time one pass of each with N fake players | each under 2 ms at 50 players |
| File I/O per save | Bank interest sweep reads every account file; Coins / Skills / Collections flush dirty files; Profiles | measure bytes + wall time of one save of N players on scratch | whole save under 100 ms off the world thread |
| Files per player | disk and handle count | count files under every `Skyy_*` folder per profile | listed, nothing target |
| Join burst | PlayerReadyEvent handlers | layer C: fire the same handler set N times | under 50 ms per player on the world thread |
| Bridge call cost | the old `System.class` lock | micro-benchmark `bridge()` x 1M calls, 1 vs 8 threads | after the Core fix: lock-free |

## 2. Layer A - idle offline server (exists, one extra step)

`tools/smoke_test.py` already starts the SET offline on a scratch COPY of the world (`tools/dev/scratch/smoke/run-<stamp>/`), TEMP / TMP / `java.io.tmpdir` = scratch,
`-XX:-UsePerfData`, deletes it afterwards. Add to it (or to the new tool): after "Booted" run a 3-minute observation window sending the stats commands on stdin every 30 s
and keep the "Task took" lines. No change to what is started, so it stays safe.

## 3. Layer B - synthetic data volume (new, simple, Python only)

Goal: N fake profiles = what a 50-100 player server looks like on disk, so every scan has real size. The generator writes ONLY into the scratch copy.

| Folder (under the scratch world `mods/`) | Fake data per profile |
|---|---|
| `Skyy_SkyyCoins/balances/<uuid>-pN.properties` | a balance |
| `Skyy_SkyyBank/` account files | a balance, `paidThrough` |
| `Skyy_SkyySkills/players/` | XP for 9 skills, `paid` markers |
| `Skyy_SkyyCollections/`, `SkyyQuests/players/`, `SkyyGear/`, `SkyyProfiles/` | copies of Skyy's own files with the UUID changed (a real profile is the best template) |

Rule: the generator copies Skyy's real profile files (from the scratch copy, never from UserData directly) and rewrites the UUID in the file name and any `uuid=` line; it never
invents formats. N = 10 / 50 / 200. Then start, wait for boot and the first save cycle, and read: boot time, heap, the Bank interest sweep time (set `intervalSeconds` low in
the SCRATCH config only), "Task took" warnings, and the leaderboards (`/skills top`). This finds the O(N) problems (full-folder scans on the world thread, unbounded caches)
without a single client.

## 4. Layer C - in-JVM harness with fake players (exists as a pattern)

`SkyyXxx/test_skyyxxx_<ver>.py` already load the built jar on the real engine classes in one `-Xverify:all` JVM. A load harness reuses that for a chosen group:

| Group | Fake-player loop | Reads |
|---|---|---|
| Timers | call each mod's periodic task once with N fake `PlayerRef` stand-ins (the harnesses already fake them) | time per pass, allocations |
| Saves | call the flush / save of Coins, Bank, Skills, Collections with N dirty players | time + bytes written |
| Join | run the PlayerReadyEvent handler list N times | time per join |
| Bridge | 1M `bridge().get("coins:fn:get")` on 1 and 8 threads | lock contention |

Needs a shared helper in `tools/` (`loadharness.py`) that builds the JVM exactly like the existing harnesses; it must set TEMP to scratch and `-XX:-UsePerfData`.

## 5. Phases

| Phase | What | Effort | Needs Skyy |
|---|---|---|---|
| 1 | Layer A: stats commands during smoke (a flag `--observe 180`) + parse "Task took" | small | no (game closed) |
| 2 | Layer B: `tools/load_test.py --profiles 50` (generator + start + observe + report + cleanup) | small to medium | no |
| 3 | Bot client spike: can the 0.7.1 server jar's own protocol classes (`com.hypixel.hytale.protocol`, the Netty QUIC codec shipped inside the jar) drive an offline-mode join (`--auth-mode offline`)? Feasibility note only; if yes, a Java headless client that joins N times and idles | large, uncertain | no |
| 4 | Layer C harnesses, group by group, as the Core merge replaces timers (measure BEFORE and AFTER the SkyyCore ticker) | medium | no |
| 5 | A real 4-6 person test with `/world tps` + `/server stats` read every 5 minutes (Skyy's friends) | - | yes |

## 6. Tool design: `tools/load_test.py` (not written)

Why not written: it must reuse the smoke test's scratch-world builder, config rewrite and process handling, and `smoke_test.py` keeps those inside one long `main()`.
Copying 200 lines would fork the safety rules (game-running check, scratch paths, kill only own process). The safe first step is to split `smoke_test.py` into functions
(`build_scratch(run_dir, jars)`, `start_server(...)`, `stop_server(...)`) in a small refactor round, then the load tool is about 120 lines on top. The console commands also need one
real check of their spelling.

```
usage: python tools/load_test.py [--profiles 50] [--observe 180] [--xmx 4G] [--light] [--json out.json]
  1. refuse if any HytaleServer java process runs (deploy_set.server_running()); exit 2
  2. run = tools/dev/scratch/loadtest/run-<stamp>/   (the ONLY place it writes)
       - build_scratch(...) from smoke_test: world copy, Mods = SET jars + pack mods, config.json like deploy_set --yes
       - gen_profiles(run/world/mods, N): copy real profile files from the scratch copy with new UUIDs (layer B)
       - scratch config only: bank.intervalSeconds = 60 so the sweep runs in the window
  3. start_server(...): Skyy's java, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir = run/tmp, --auth-mode offline,
       --bind 127.0.0.1:<free port>, cwd = run/world (the smoke command line, unchanged)
  4. wait "Hytale Server Booted!" (record boot seconds); then every 30 s for --observe seconds send on stdin:
       world tps, server stats memory, server stats cpu, entity count   (spellings checked once, UNVERIFIED)
  5. stop: "stop" on stdin; kill ONLY its own pid after 60 s
  6. parse: boot time, heap, tps series, every "Task took" line (flag com.skyy), SEVERE lines naming Skyy, files + bytes per Skyy_* folder
  7. report: tools/dev/scratch/loadtest/<stamp>.txt (+ --json); delete run/ (keep with --keep)
  exit 0 = no com.skyy WARN over 25 ms and TPS >= 19.5, 1 = fail, 2 = not run
```

Safety (same as the smoke test): never touches UserData except reading to copy, never the real world, never the game folder, own scratch folder only
(never cleans other folders under `tools/dev/scratch/`), ~4 GB RAM, never run next to a smoke run or the game.

## UNVERIFIED

| # | Item |
|---|---|
| 1 | The exact console spelling and output of the stats commands (found as class names only). |
| 2 | Whether the engine exposes a per-ECS-system time through `MetricSystem` / `MetricsRegistry` to a console command or only internally. |
| 3 | That an offline server accepts a protocol client written from the jar's classes (phase 3 spike). |
| 4 | That copied profile files with a new UUID are accepted by every mod (some also key by profile id inside the file). |
| 5 | All targets are placeholders until the first run on Skyy's PC. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | OK to refactor `smoke_test.py` into reusable functions (no behaviour change) so the load tool can share its safety checks? | [yes, small lean round] |
| 2 | Spend a day on the bot-client spike (phase 3), or rely on layers A-C and a real friends test? | [layers A-C first, spike only if they miss something] |
| 3 | How many players should the public server handle at release (sets N)? | [50 online, 200 profiles on disk] |
| 4 | Make "no com.skyy Task-took over 25 ms" a release gate in the smoke test? | [yes, warn only until the Core ticker lands] |
