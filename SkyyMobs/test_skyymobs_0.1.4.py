"""SkyyMobs 0.1.4 harness - bare JVM, no game. Run: python SkyyMobs/test_skyymobs_0.1.4.py [--jar <jar>] [--dir <scratch>] [--keep]
                                                                                       [--sweep <changes, default 3000>]

Made from test_skyymobs_0.1.3.py: every 0.1 / 0.1.1 / 0.1.2 / 0.1.3 check still runs against the 0.1.4 jar - in Per level shape (strength.shape
=linear, the shape that is 0.1.3 byte for byte): MobCfg sits behind a proxy whose useDefaults / apply load the defaults with
strength.shape=linear; the LV scratch file says linear; K switches the shape through the real kit. -Xverify:all, -XX:-UsePerfData;
HytaleServer.jar + tools/javassist.jar + the SkyyMobs 0.1.4 jar + SkyyMenu/SkyyMenu-0.3.5.jar (the label check draws with it) on the
classpath; SkyyMobs-0.1.3.jar (the SET pin: O / Z / CU), SkyyMobs-0.1.2.jar (NQ: the 0.1.3 fix's reference), SkyyMobs-0.1.1.jar (Q / FL / U2)
and SkyyMobs-0.1.jar (U2 / V / MIG) are read through child-first loaders and as zip bytes (Z). The SET section runs the 0.1.4 build script
with --set-file <scratch copy> --check-set (the pairing guard only; nothing is built). Nothing is deployed and nothing outside the scratch
folder is written (default tools/dev/scratch/mc-mobs/harness; TEMP / TMP and java.io.tmpdir point into it). SCRATCH SAFETY (the 2026-10-02
incident): --dir must be a folder INSIDE a task folder (tools/dev/scratch/<task>/<sub>) - never the scratch root or a top-level task folder,
no '..' in the argument, no link / junction on its path - and, if it exists, empty or this harness's own (its marker file); anything else is
refused and NOTHING is deleted; the end-of-run cleanup deletes only that validated, marked folder (unless --keep). Read-only: Assets.zip, the
two HytaleServer.jar files (release + 0.7 pre-release), the client font tables, the installed Mods folder (X scan, the deployed SkyyMenu.jar
hash) and Skyy's live Skyy_SkyyMobs folder - COPIED into the scratch folder before anything runs on it (U, MIG).
0.1.4 sections (research/Mob-Curve-Spec.md, accepted 2026-10-05; the 0.1.3 sections below are kept):
  O  SkyyMobs-0.1.3.jar's own header vs 0.1.4: the 26 rows kept (5 help texts reworded only), the 18 new rows of spec 6.1 in display order,
     the tabs Level curve / Level gap; in Per level shape both jars' hpMult / dmgMult / hpAmount equal everywhere (3 floors x 5 strengths x
     Lv 0-150 x 7 bases, Skyy's Custom 20 / 8 included) and hardRef = Hard's own line
  Z  class compare 0.1.3 -> 0.1.4: the 5 new classes, the 20 untouched classes byte-identical, exactly the changed entries, hpMult / dmgMult
     = the curve branch + 0.1.3's code instruction for instruction, LevelDamage.handle unchanged up to the level multiplier, the members
     added per class, the manifest text
  CU the Level curve: the 8 tables = the spec's 1.3 block; hpMult / dmgMult / hardRef = the straight lines (Python mirror, float32 bit for
     bit) for 4 difficulties x Lv 0-110; the spec's 1.4 table; Lv 0-20 = SkyyMobs-0.1.3.jar's own presets float-exact; THE 1.2 RULE
     (health = 0.1.3's preset x F_new / F_old at every level 21-60, damage = x the spec 2.3 player HP ratio) and the same-level Warrior
     swings within 1 at Lv 1-60; hand-edited / empty / one-point tables; files without strength.shape (custom -> Per level); the live
     re-apply trigger (11 cases: the active health table, shape, difficulty, scale.role re-apply; damage tables, caps in curve shape,
     gap rows do not)
  CU-K the tables + scale.role through the REAL kit: tset / add / remove + every check hook (level, factor, the last entry, *, health x),
     the reload routine re-reads the file, a loaded Lv 40 Yeti gets its new max and keeps its health percent
  GP the level gap: dealt / taken = a mirror for d = -50 ... +100 with 4 settings, the spec's named values (Skyy's +13 Yeti: 80 % / 112 %),
     the class level cache (2 s; no class = no gap; 0 = unknown; a cached good level never overwritten by a 0 or a throwing read - F6)
  DM GapDamage + LevelDamage.handle on REAL engine Damage objects (EntitySource / ProjectileSource) through a stand-in CommandBuffer /
     ArchetypeChunk and the engine's own getComponentType calls: player -> mob scaled, a projectile by its shooter, free levels, unlevelled,
     player -> player, pets, mob -> mob, no class, cancelled, gone refs, F6, part off; LevelDamage: mob -> player x level x taken, mob ->
     mob / pet / no class = 0.1.3's multiplier, knobs off = 0.1.3's float product, the damage floor (Lv 20 none, 25 half, 30 full, the
     health floor base, unknown base, mob -> mob never), one hit at most; the gap and another multiplier in both orders
  SR scale.role: rows (exact any case, a hand-typed Prefix*, level 0 off, bad lines, levels.max), whyNotRole; MobLevel.onAdd through a
     stand-in Holder: the EXCLUDED Goblin_Duke with a row -> Lv 30 + health x2 on top of the curve + plate; the factor through the live
     re-apply; a changed row re-stamps the save slot; the row removed -> stripped; part off; the inspect line
  IF mob:fn:info: the Object[6] contract on 4 difficulties (xpMult Hard 1, Easy 0.62 at Lv 40, Normal 0.81, Custom 1), xpBase with the
     floor, Per level Custom 20 / 8 = 1, the role factor in hpMult only, a table edit, null cases, 16,000 threaded calls
  WN the 15 s gear-curve WARN both ways (missing / flat / steep x curve / Per level, a throwing gear:fn:curve)
  CMD the /mobs texts: inspect's health line (curve + Per level = 0.1.3's), the gap line, /mobs info's band line with the gap
  MIG MobMig14: the block = spec 6.1's rows + the 80 curve entries; 0.1.3's default -> exactly 0.1.4's default; Skyy's live folder (a
     scratch COPY) started twice in setup()'s order (the mirror's bytes, every old value kept, History, 1 Undo line, Undo -> 0.1.3's
     Hard, the second start changes nothing); 16 synthetic files (custom, CRLF, no final newline, keys already there in any case, no
     strength lines, empty, marker, the 0.1 default through both updates) = an independent Python mirror; a blocked config-history
  SET the build's pairing STOP on scratch copies of tools/deploy_set.py
  S  (0.1.4) start twice in setup()'s new order: a fresh folder is never updated by either update
  P  + GapDamage / GapDamageU registration + ordering, MobMig14 in setup between MobMig and MobCfg.load, mob:fn:info on / off the
     bridge, refreshOne passes the role factor, onAdd reads scale.role first
  (U1 still starts Skyy's live copy in 0.1.3's order - the 0.1.1 update touches nothing there; MIG runs 0.1.4's order on it)

THE 0.1.3 HARNESS NOTES (kept; read "0.1.3" there as the version they were written for):
Made from test_skyymobs_0.1.2.py: every 0.1 / 0.1.1 / 0.1.2 check still runs against the 0.1.3 jar (F runs with the floor OFF = the 0.1.1
numbers; Q / FL still compare the floor with SkyyMobs-0.1.1.jar). -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar
+ the SkyyMobs 0.1.3 jar + SkyyMenu/SkyyMenu-0.3.5.jar (the label check draws with it) on the classpath; SkyyMobs-0.1.2.jar (the SET pin:
NQ / O / Z), SkyyMobs-0.1.1.jar (Q / FL / U2) and SkyyMobs-0.1.jar (U2 / V) are read through child-first loaders and as zip bytes (Z).
Nothing is deployed and nothing outside the scratch folder is written (default tools/dev/scratch/mobs013/harness; TEMP / TMP and
java.io.tmpdir point into it). SCRATCH SAFETY (the 2026-10-02 incident): --dir must be a folder INSIDE a task folder
(tools/dev/scratch/<task>/<sub>) - never the scratch root or a top-level task folder, no '..' in the argument, no link / junction on its
path - and, if it exists, empty or this harness's own (its marker file); anything else is refused and NOTHING is deleted; the
end-of-run cleanup deletes only that validated, marked folder (unless --keep). Read-only: Assets.zip, the two HytaleServer.jar files
(release + 0.7 pre-release), the client font tables, the installed Mods folder (X scan, the deployed SkyyMenu.jar hash) and Skyy's live
Skyy_SkyyMobs folder - COPIED into the scratch folder before anything runs on it (U).
0.1.3 sections (F1 of the 0.1.2 cross-check: after a modifier change the health goes out as Min / Max, never as Set / Maximize):
  NQ the network queue on REAL engine objects: all 12 vanilla stats (Assets.zip Server/Entity/Stats, Health Shared like the game) through
     the real asset codec into the engine's own IndexedLookupTableAssetMap, reached the engine's way (EntityStatType.getAssetMap ->
     AssetRegistry); a mob = a real EntityStatMap + NPC_Max (BalancingInitialisationSystem's recipe) + our spawn modifier + a wound;
     every change runs through the jar's own code (refreshOne = the live re-apply, apply 'set' = /mobs set N, strip = /mobs set 0, the
     heal path) and, on an identical map, through SkyyMobs-0.1.2.jar's; then the REAL EntityStatsSystems$EntityTrackerUpdate.tick on a
     stand-in ArchetypeChunk (player A already sees the mob, player B starts seeing it) queues into the REAL EntityViewer, the
     EntityUpdates packet (as SendPackets builds it) goes through the real wire format and back, the REAL ClearChanges.tick empties the
     queue; a client mirror (the client code is not in the server jar: the server's own EntityStatValue rules) replays what each player
     got. Named: max up, max down (also below the old health), unchanged, the same max with a new key, a 1-HP mob (up, then down), a
     0-HP mob (refresh: untouched; /mobs set: the same queue as 0.1.2; the heal path: 12b below), full health up / down, /mobs set 32 ->
     40, /mobs set 0, the heal path, spawns; SKYY'S CASE (2026-10-03): a loaded Lv 32 Yeti (base 226) seen by a player, Hard x3.48 -> Custom 20% / 8% (caps 20 /
     6) x7.2 = 1627 HP: with 0.1.2 the player kept the 786 max and the bar was empty at hit 4 of the 8 that kill it, with 0.1.3 the
     player gets 1627 at once (+ the Lv 33 Yeti x3.56 = 805 -> x7.4, a hurt one, and back to Hard); a damage hit in the same tick after
     the change; a seeded sweep (every path, both jars, --sweep); end to end through MobRefresh.dispatch -> the real World.execute ->
     the world task. Checks: the server ends bit for bit where 0.1.2 put it, every PutModifier / RemoveModifier entry survives next to
     at most one Min / Max entry (last), player A gets exactly the queue, player B the new state, both client copies = the server, the
     health percent exact, nothing healed or killed (the engine's death rule on the self queue). The one difference the death rule can
     see (12b, pinned + counted): a mob at exactly 0 HP given the heal path (healOnLoad ON / spawn) with the same key - 0.1.2's merge
     hid its PutModifier entry at 0 HP, so it came back at full health; 0.1.3 heals it the same, and the engine lets it die (as 0.1.2
     already did when the level changed or healOnLoad was off)
  AX engine-access audit with the JVM's own rules: every class / field / method / constructor reference in the jar's bytecode looked up
     with MethodHandles.Lookup IN its referencing class (privateLookupIn: a protected engine member only from a subclass) - 0 refused;
     control: a class calling the protected EntityStatValue.set is refused AND throws IllegalAccessError when run
  O  SkyyMobs-0.1.2.jar's own header vs 0.1.3: identical but the version; both jars' multipliers / health amounts equal everywhere
  Z  class byte-compare SkyyMobs-0.1.2.jar vs 0.1.3: only MobLevel's code (writeValue added; setMult's two health writes and stripStats'
     one go through it, instruction by instruction) and the version constants (CfgFn, CfgRows, MobCfg's default texts, the ready line),
     manifest.json Name / Version; every other entry byte-identical
  U1 (as 0.1.2's) start twice on a scratch COPY of Skyy's live folder as it is now: no byte / time changed, kit ok, the floor row works
  P  + 0.1.3: no class calls setStatValue / maximizeStatValue (or any other Set-like write); writeValue = minStatValue / maxStatValue
  (the stand-in stat maps of F / Q / FL / RA / IN / LV answer minStatValue / maxStatValue the engine's way: min / max, then the clamp)
0.1.2 sections (kept):
  Q  the level health floor numbers: bases 36 / 74 / 200 at Lv 1 / 32 / 60 on Easy / Normal / Hard through the jar's own setMult on
     stand-in stat maps (spawn = full) = the mirror typed here (task: Lv 32 cobra 143 HP Normal / 174 Hard, Lv 1 50 HP); the caps hold
     the level multiplier only (Lv 100 Hard, a cap of x3); edge bases 10 / 49.99 / 50 / 50.01; the 0.1.1 -> 0.1.2 HP table
  FL floor 0 = 0.1.1 EXACTLY: hpAmount == SkyyMobs-0.1.1.jar's own hpMult (bit for bit) for 4 difficulties x Lv 0-150 x 7 bases, also
     with floor 50 for every base at or above it; the whole setMult of both jars on identical stand-in maps (spawn, then a wounded
     reload after a difficulty change) -> identical amounts, max and health
  RA the re-apply on a chunk load (0.1.1's path, MobLevel.apply with a saved level): a mob saved by 0.1.1 (x2.86, 103 HP, 50% hurt)
     loads as x3.97 / 143 HP at 50% (health PERCENT kept, never healed); a second load re-puts nothing (no churn); floor 0 gives x2.86
     back; strength.healOnLoad still heals on a load; baseOf next to another mod's multiplicative modifier, a 0 sum, no stat, rounding
  IN /mobs inspect's health line (MobCmds.healthLine) on stand-in maps: Skyy's 0.1.1 case (Lv 20 Goblin Scrapper made on Normal, then
     Hard: "applied x2.14 (setting x2.52 - updates on reload or /mobs set) (81 / 81 HP)"), floor applied / not needed / off, a raised
     floor before the re-apply, no modifier at all, level 0
  LV the LIVE re-apply END TO END: the real config kit (set ops + a hand edit + the reload op) -> after=MobCfg.derive -> the health
     signature -> MobCfg.ON_HEALTH = MobRefresh(null) (as setup() sets it) -> MobLevel.liveWorlds() via a stand-in Universe -> the
     REAL World.execute on stand-in worlds (acceptingTasks + taskQueue) -> each queued task run as its world's thread -> refreshWorld ->
     EntityStore.getRefFromUUID / getStore -> Store.getComponent (stand-in Store) -> refreshOne -> setMult: Difficulty, floor 0 / 80,
     health cap, Custom % each re-apply every loaded levelled mob of each world (health PERCENT kept, tiny-HP mob alive, dead mob and
     unloaded / gone mobs untouched, one task per world, nothing touched before the world thread runs, other worlds untouched);
     damage-only / nameplate / healOnLoad changes re-apply nothing; healOnLoad ON still never heals here; a world that stops taking
     tasks; ON_HEALTH null (shutdown) = no re-apply; no levelled mob = nothing queued
  (0.1.2's O / Z compared 0.1.1 -> 0.1.2; they compare 0.1.2 -> 0.1.3 now, see above)
  U  (0.1.1's update still ships) U1 Skyy's live folder AS IT IS NOW (0.1.1 updated it at 22:41, Skyy changed the difficulty since),
     copied: start twice = no byte / time changed, floor 50 from the code default (no file line), kit status ok, the new row works on
     Skyy's real file and a third start reads it; U1b Skyy's real pre-update bytes (the config-history copy "before the 0.1.1
     difficulty update") -> exactly the 0.1.1 update; U2 the synthetic files (0.1's default -> exactly 0.1.1's default, ...)
  P  + derive runs ON_HEALTH, setup sets / shutdown clears it, the dispatcher only queues World.execute, refreshOne = setMult(..., false,
     false), setMult puts hpAmount(level, baseOf), inspect prints healthLine
0.1.1 section (kept, now with the floor row):
  V  every SkyyMobs tab, row name, help line, choice button and table button drawn by the REAL SkyyMenu 0.3.5 AdminPage (tabRow +
     drawRow, every row with and without a search hit and a draft) fits its box with 8 px to spare (client glyph advances,
     skyyui.text_width) - the new floor row included; the same drawing of the 0.1 header flags exactly what Skyy saw (the tab "Who gets
     le", the Easy / Normal / Hard choices); the project's SkyyMenu-0.3.5.jar = the deployed SkyyMenu.jar
0.1 sections (kept):
  A  every class of the jar loads, verifies (-Xverify:all) and initialises; M  the manifest + the class list
  B  the default band tables (the jar's own default bands.properties through its real loader) = the refit, typed here independently
     from research/cloud/Mob-Levels-Refit.md (every biome / environment / zone row, zone floors + tops, the documented additions)
  R  the lookup chain (MobLevel.resolve) = a Python mirror for every region x biome of Assets.zip x a set of environments, every
     environment on a non-classic world, world rows, islands, the lava-cave rule (zone tops 18-20 / 28-30 / 43-45 / 58-60), passThrough
  C  difficulty presets (0.1.1: Easy 4/2, Normal 6/3 = default, Hard 8/4, Custom 4/2); D  health / damage maths per level (float32
     exact, caps x6 / x3.5; Lv 1 / 20 / 60 of every preset named, Hard Lv 60 = x5.72 / x3.36 not capped, first capped at Lv 64)
  E  who gets a level: every vanilla role (attitude resolved from Assets.zip) through MobCfg.whyNot = the classification; named cases
     (hostile, neutral fighter, animal, player, trader, tamed, summon, boss, neutral switch off); review F1: other mods' roles that
     share a vanilla prefix (mounts, pets, NPCs, bosses) get no level, the extra row + its guard patterns, a blank extra row (F10), the
     exclude-all uninstall trick (F5), the neutral animals left out by default (F2); X: every role of the installed mods (read-only
     scan of UserData/Mods) that is not a vanilla role gets no level
  W  the worldgen cache (review F3) through a stand-in World / ChunkStore: no generator yet and a throwing ChunkGenerator are NOT
     cached, a non-classic generator is, one entry per exact block column
  N  the prune (review F6): pruneWith (removed / collected worlds, by name without a reference, the 60 s grace), pruneWorld through a
     stand-in EntityStore (gone and invalid refs), MobPruneTask without a Universe
  T  /mobs platetest (review F11): one claim per mob, a stale claim is taken over, every end path releases it
  G  nameplate text: colours off, each markup, the colour ladder, plain() / isOurs(), names without I18n
  F  persistence: the save-slot key, pick / forget / KEPT (chunk reload), the deterministic roll = a Python mirror, a stand-in stat map
     driving the jar's own setMult / apply / strip (spawn = full, reload = same key, curve change = health share kept), and the real
     EntityStatValue codec carrying the modifier key through BSON
  I  mob:fn:level contract (java.lang types, -1 cases, never throws, 8 threads)
  H  command permissions with the engine's own code (Adventurer: /mobs + /mobs info only; admin subs skyymobs.admin, empty groups)
  K  the config kit (Server Setup): header, every row, set / refuse, table ops through the real kit, the reload routine, hand edit
  S  start twice on a scratch folder the way setup() starts (MobMig.run, MobCfg.load, CfgPub.start): no churn - files byte-identical,
     no history version, no change log, the fresh file carries the update marker
  L  link check: every engine member the jar references exists in the release AND the 0.7 pre-release HytaleServer.jar
  P  bytecode facts: the hook's query + ordering, the damage system's group + ordering, one registerSystem per class, no unordered
     hook fallback (review F4), the prune scheduled + cancelled (F6), the worldgen cache key (F3); 0.1.1: setup() runs MobMig.run
     before MobCfg.load and CfgPub.start and puts its answer + the caps on the ready line
Exit code 1 on any FAIL.
"""
import os, sys, re, json, shutil, struct, zipfile, random, collections, time, threading, hashlib, difflib, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1.4"
PINVER = "0.1.3"                  # the SET pin 0.1.4 replaces (O / Z / LIN compares, linear shape = 0.1.3 bit for bit)
PREVVER = "0.1.2"                 # the 0.1.3 fix's reference (NQ: 0.1.2's network queue bug)
V011 = "0.1.1"                    # floor 0 = its numbers (Q / FL), its default text (U2: the one-time 0.1 -> 0.1.1 update)
OLDVER = "0.1"                    # still read: its default text (U2: the one-time 0.1 -> 0.1.1 update ships unchanged) and V's proof
PKG = "com.skyy.mobs."
MPKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


DIR_ARG = arg("--dir")
SCRATCH = os.path.abspath(DIR_ARG or os.path.join(TOOLS, "dev", "scratch", "mc-mobs", "harness"))
MARKER = ".skyymobs014-harness"   # written into the scratch folder this harness made; only a folder holding it is ever deleted
SWEEP = int(arg("--sweep", "3000"))   # NQ: seeded random changes, each on both jars' real stat maps
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-%s.jar" % OLDVER)                               # 0.1 (read-only)
PREV_JAR = os.path.join(HERE, "SkyyMobs-%s.jar" % PREVVER)                             # 0.1.2 (read-only, NQ)
PIN_JAR = os.path.join(HERE, "SkyyMobs-%s.jar" % PINVER)                               # the SET pin 0.1.3 (read-only: O / Z / LIN)
V011_JAR = os.path.join(HERE, "SkyyMobs-%s.jar" % V011)                                # 0.1.1 (read-only)
MENU_JAR = os.path.join(ROOT, "SkyyMenu", "SkyyMenu-0.3.5.jar")                         # the SET pin of SkyyMenu (read-only)
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
SCRATCH_OK = [False]          # set by main() only after --dir passed the guard: nothing is ever deleted before that
COUNT = collections.Counter()
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
HY = os.path.join(APPDATA, "Hytale", "install")
AZ_PATH = os.path.join(HY, "release", "package", "game", "latest", "Assets.zip")
PRE_JAR = os.path.join(HY, "pre-release", "package", "game", "latest", "Server", "HytaleServer.jar")
# Skyy's live data (READ-ONLY: copied into the scratch folder before anything runs on it) and the deployed jars (hashes only)
LIVE_DIR = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyMobs")
DEPLOYED = os.path.join(APPDATA, "Hytale", "UserData", "Mods")

# ================================================================= 0.1.1: the difficulty ladder, typed here independently of the build
# (OPEN-QUESTIONS LOCKED 2026-10-02: Easy 4% / 2%, NORMAL 6% / 3% (default), HARD 8% / 4%; caps health x6 / damage x3.5; Custom unchanged)
LADDER = {"easy": (4.0, 2.0), "normal": (6.0, 3.0), "hard": (8.0, 4.0)}
LADDER_01 = {"easy": (3.0, 1.5), "normal": (4.0, 2.0), "hard": (6.0, 3.0)}
CAPS, CAPS_01 = (6.0, 3.5), (5.0, 3.0)
CUSTOM = (4.0, 2.0)
# multipliers at Lv 1 / 20 / 60 (health, damage), worked out by hand: 1 + pct x (L - 1)
MULT = {("easy", 1): (1.0, 1.0), ("easy", 20): (1.76, 1.38), ("easy", 60): (3.36, 2.18),
         ("normal", 1): (1.0, 1.0), ("normal", 20): (2.14, 1.57), ("normal", 60): (4.54, 2.77),
         ("hard", 1): (1.0, 1.0), ("hard", 20): (2.52, 1.76), ("hard", 60): (5.72, 3.36)}
MULT_01 = {("easy", 20): (1.57, 1.285), ("easy", 60): (2.77, 1.885), ("normal", 20): (1.76, 1.38), ("normal", 60): (3.36, 2.18),
            ("hard", 20): (2.14, 1.57), ("hard", 60): (4.54, 2.77)}
FIT_PAD = 8                                    # px a Server Setup text must leave free in its box (as the build's menu_fit)
# 0.1.2: the level health floor (OPEN-QUESTIONS LOCKED 2026-10-02: "no leveled mob has less health than a 50-HP mob of its level"),
# typed here independently of the build
FLOOR = 50
FLOOR_LINES = ("# Health floor (Skyy 2026-10-02): no levelled mob has less health than a mob of this base HP at its level (0 turns it off).",
               "strength.floor=50")
FLOOR_ROW = ["strength.floor", "Health floor (base HP)", "strength", "int", "50", "0", "1000", "", "", "live",
             "No levelled mob has less health than a mob of this base HP at its level. 0 = off."]
HP_HELP_011 = "Difficulty Custom only: max health +this % per level above 1 (mobs that spawn or reload)."
HP_HELP = "Difficulty Custom only: max health +this % per level above 1. Applies at once (health % kept)."
HPCAP_HELP = "Health per level never goes above this multiple (x6 never clips Hard at Lv 60, which is x5.72)."


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


# ================================================================= the refit, typed independently (research/cloud/Mob-Levels-Refit.md)
# section 3 (Zones 1-3) + plan 4.5 (Zone 4, unchanged). Exact biome rows: (region, biome) -> (lo, hi)
REFIT_BIOMES = {
    ("Zone1_Tier1", "Plains_Smooth"): (1, 3), ("Zone1_Tier1", "Plains_Birch"): (3, 5),
    ("Zone1_Tier1", "Forest_Birch"): (5, 7), ("Zone1_Tier1", "Forest_Flower"): (5, 7), ("Zone1_Tier1", "Mountain_Tier1"): (5, 7),
    ("Zone1_Tier2", "Plains_Gorge"): (7, 9), ("Zone1_Tier2", "Plains_Tallgrass"): (9, 11),
    ("Zone1_Tier2", "Forest_Aspen"): (10, 12), ("Zone1_Tier2", "Forest_Gully"): (10, 12), ("Zone1_Tier2", "Mountain_Tier2"): (10, 12),
    ("Zone1_Tier3", "Plains_Gorge"): (12, 14), ("Zone1_Tier3", "Forest_Swamp"): (16, 18), ("Zone1_Tier3", "Mountain_Tier3"): (16, 18),
    ("Zone1_Tier3", "Forest_Autumn"): (18, 20), ("Zone1_Tier3", "Forest_Moss"): (18, 20), ("Zone1_Tier3", "Forest_Azure"): (18, 20),
    ("Zone2_Tier1", "Savannah_Forest"): (20, 22), ("Zone2_Tier1", "Savannah_Plains"): (20, 22), ("Zone2_Tier1", "Savannah_Boab"): (20, 22),
    ("Zone2_Tier1", "Savannah_Rock"): (20, 22), ("Zone2_Tier1", "Savannah_Mudflats"): (20, 22), ("Zone2_Tier1", "Scrub_Bushland"): (22, 24),
    ("Zone2_Tier2", "Desert_Oasis"): (25, 27), ("Zone2_Tier2", "Desert_Rock"): (25, 27), ("Zone2_Tier2", "Desert_Springs"): (25, 27),
    ("Zone2_Tier2", "Desert_Red"): (25, 27),
    ("Zone2_Tier3", "Desert_Barren"): (27, 29), ("Zone2_Tier3", "Desert_Mushroom"): (27, 29),
    ("Zone2_Tier3", "Scrub_Tar_Pits"): (28, 30), ("Zone2_Tier3", "Desert_Mushroom_Foot"): (28, 30),
    ("Zone3_Tier1", "Forest_Redwood"): (30, 32), ("Zone3_Tier1", "Plains_Shire"): (30, 32), ("Zone3_Tier1", "Forest_Fir"): (32, 34),
    ("Zone3_Tier1", "Forest_Tundra"): (32, 34), ("Zone3_Tier1", "Plains_Hotsprings"): (32, 34),
    ("Zone3_Tier2", "Forest_Cedar"): (36, 38), ("Zone3_Tier2", "Plains_Frozen"): (37, 39), ("Zone3_Tier2", "Forest_Cedar_Mixed"): (37, 39),
    ("Zone3_Tier2", "Plains_Tundra"): (37, 39),
    ("Zone3_Tier3", "Forest_Frozen"): (41, 43), ("Zone3_Tier3", "Forest_Frozen_Light"): (41, 43), ("Zone3_Tier3", "Plains_Frozen_Frost"): (41, 43),
    ("Zone4_Tier4", "Wastes_Grasslands"): (45, 47), ("Zone4_Tier4", "Wastes_Geysers"): (48, 50), ("Zone4_Tier4", "Forest_Ghost"): (48, 50),
    ("Zone4_Tier4", "Desert_Dunes"): (48, 50), ("Zone4_Tier4", "Forest_Swamp"): (48, 50),
    ("Zone4_Tier5", "Desert_Ash"): (53, 55), ("Zone4_Tier5", "Wastes_Ash"): (53, 55), ("Zone4_Tier5", "Wastes_Lava"): (55, 57),
    ("Zone4_Tier5", "Forest_Burned"): (58, 60), ("Zone4_Tier5", "Forest_Roots"): (58, 60),
}
# patterned refit rows (Trork camps, plateaus, overlays by region tier) and the region fallbacks (refit "Fallback rows")
REFIT_PATTERNS = {
    "Zone1_Tier1.*_Trork": (5, 7), "Zone1_Tier2.*_Trork": (10, 12), "Zone1_Tier3.*_Trork": (16, 18),
    "Zone2_Tier1.Plateau_*": (21, 23), "Zone2_Tier3.Plateau_Desert_*": (28, 30), "Zone2_Tier3.Desert_Oasis_Hidden*": (28, 30),
    "Zone3_Tier1.Mountain_*": (32, 34), "Zone3_Tier2.Mountain_*": (37, 39), "Zone3_Tier3.Mountain_*": (43, 45),
    "Zone1_Tier1.*": (1, 7), "Zone1_Tier2.*": (7, 12), "Zone1_Tier3.*": (12, 20),
    "Zone2_Tier1.*": (20, 24), "Zone2_Tier2.*": (25, 27), "Zone2_Tier3.*": (27, 30),
    "Zone3_Tier1.*": (30, 34), "Zone3_Tier2.*": (36, 39), "Zone3_Tier3.*": (41, 45),
    "Zone1_Spawn.*": (1, 3),        # refit: Zone1_Spawn Plains_Spawn 1-3 (fixed start area)
}
# rows the build adds where the refit is silent (each a documented decision in the build script header)
ADDED = {
    "Zone1_Temple": (1, 3),                                                          # the start-area temple = like the spawn
    "Zone4_Tier4": (45, 50), "Zone4_Tier5": (53, 60),                                # plan 4.1 region bands
    "Zone1_Shore": (1, 3), "Zone2_Shore": (20, 22),                                  # plan 4.1: shores = lowest band of the land region
    "Zone3_Shore_Tier1": (30, 32), "Zone3_Shore_Tier2": (36, 38), "Zone3_Shore_Tier3": (41, 43),
    "Zone4_Shore_Tier4": (45, 47), "Zone4_Shore_Tier5": (53, 55),
}
# refit 4.2 (Zones 1-3) + plan 4.6 (Zone 4 + the 0.7 portal shards, unchanged): env -> (lo, hi, bonus)
REFIT_ENV = {
    "Env_Zone1_Plains": (1, 3, 0), "Env_Zone1_Shores": (1, 3, 0), "Env_Zone1_Kweebec": (1, 3, 0), "Env_Zone1_Forests": (5, 9, 0),
    "Env_Zone1_Mountains": (5, 14, 0), "Env_Zone1_Trork": (5, 16, 0), "Env_Zone1_Swamps": (14, 20, 0), "Env_Zone1_Autumn": (16, 20, 0),
    "Env_Zone1_Azure": (16, 20, 0), "Env_Zone1_Caves*": (5, 14, 0), "Env_Zone1_Caves_Volcanic_T1": (5, 9, 0),
    "Env_Zone1_Caves_Volcanic_T2": (9, 14, 0), "Env_Zone1_Caves_Volcanic_T3": (14, 18, 0), "Env_Zone1_Caves_Goblins": (5, 16, 1),
    "Env_Zone1_Mineshafts": (5, 16, 1), "Env_Zone1_Encounters": (9, 18, 2), "Env_Zone1_Graveyard": (9, 18, 2),
    "Env_Zone1_Mage_Towers": (9, 18, 2), "Env_Zone1_Dungeons": (14, 20, 2),
    "Env_Zone2_Savanna": (20, 22, 0), "Env_Zone2_Shores": (20, 22, 0), "Env_Zone2_Scrub": (22, 24, 0), "Env_Zone2_Plateaus": (21, 27, 0),
    "Env_Zone2_Deserts": (25, 29, 0), "Env_Zone2_Oasis": (25, 30, 0), "Env_Zone2_Feran": (23, 28, 1), "Env_Zone2_Scarak": (23, 28, 1),
    "Env_Zone2_Caves*": (21, 27, 0), "Env_Zone2_Caves_Volcanic_T1": (21, 23, 0), "Env_Zone2_Caves_Volcanic_T2": (25, 27, 0),
    "Env_Zone2_Caves_Volcanic_T3": (28, 30, 0), "Env_Zone2_Mineshafts": (23, 27, 1), "Env_Zone2_Caves_Goblins": (23, 27, 1),
    "Env_Zone2_Encounters": (25, 29, 2), "Env_Zone2_Mage_Towers": (25, 29, 2), "Env_Zone2_Dungeons": (27, 30, 2),
    "Env_Zone3_Tundra": (30, 35, 0), "Env_Zone3_Shores": (30, 33, 0), "Env_Zone3_Forests": (30, 38, 0), "Env_Zone3_Mountains": (35, 41, 0),
    "Env_Zone3_Glacial": (38, 45, 0), "Env_Zone3_Caves*": (32, 41, 0), "Env_Zone3_Trork": (35, 42, 1),
    "Env_Zone3_Outlander*": (39, 45, 2), "Env_Zone3_Encounters": (39, 45, 2),
    "Env_Zone4_Wastes": (45, 50, 0), "Env_Zone4_Shores": (45, 47, 0), "Env_Zone4_Crucible": (48, 50, 0), "Env_Zone4_Volcanoes": (48, 57, 0),
    "Env_Zone4_Forests": (48, 60, 0), "Env_Zone4_Jungles": (50, 58, 0), "Env_Zone4_Encounters*": (53, 60, 2),
    "Env_Zone4_Villages*": (55, 60, 2),
    "Env_Portal_Goblin_Surface": (5, 8, 0), "Env_Portal_Goblin_Cave": (7, 10, 0), "Env_Portal_Goblin_Cave_Deep": (9, 11, 0),
    "Env_Portal_Goblin_Cave_Void": (10, 12, 0),
}
REFIT_ZONE = {"Zone1": (1, 7), "Zone2": (20, 24), "Zone3": (30, 34), "Zone4": (45, 50)}
LOCKED = {1: (1, 20), 2: (20, 30), 3: (30, 45), 4: (45, 60)}          # OPEN-QUESTIONS LOCKED 2026-10-01
LAVA_TOPS = {1: (18, 20), 2: (28, 30), 3: (43, 45), 4: (58, 60)}      # Skyy R5: the zone's hardest biome (Zone 1 "about 17-20")
PASS = "River_*,Lake*,Dunes_*,*_Mudflats,*_Kweebec,Valley_*,Canyon_*,Caldera_*,Hills_*,Volcano_*,Village_*,*_Village,*_Town,Town_*"


def pglob(p, s):
    return re.fullmatch(re.escape(p.lower()).replace(r"\*", ".*"), s.lower()) is not None


def spec(p):
    return sum(1 for c in p if c != "*")


class PyTable(object):
    """mirror of MobBands: keys sorted, exact (case-insensitive) first, else the highest literal count, ties = the first sorted key"""
    def __init__(self, rows):
        self.rows = sorted(rows.items(), key=lambda kv: kv[0])

    def find(self, key):
        if key is None:
            return None
        k = key.lower()
        for rk, v in self.rows:
            if "*" not in rk and rk.lower() == k:
                return rk, v
        best, bs = None, -1
        for rk, v in self.rows:
            if "*" in rk and spec(rk.lower()) > bs and pglob(rk, k):
                best, bs = (rk, v), spec(rk.lower())
        return best

    def find_prefix(self, key):
        hit = self.find(key)
        if hit or key is None:
            return hit
        best, bl = None, 0
        for rk, v in self.rows:
            if "*" not in rk and len(rk) > bl and key.lower().startswith(rk.lower()):
                best, bl = (rk, v), len(rk)
        return best


def zone_of_region(region):
    m = re.match(r"^Zone(\d+)(?:_|$)", region or "")
    return "Zone" + m.group(1) if m else None


def zone_of_env(env):
    return zone_of_region(env[4:]) if env and env.startswith("Env_Zone") else None


def volcanic_zone(env):
    z = zone_of_env(env)
    return int(z[4:]) if z and env.startswith("Env_%s_Caves_Volcanic" % z) else 0


def py_resolve(T, wn, island, classic, region, biome, tile, env, volcanic=True, isl=(0, 0), dflt=(0, 0)):
    w = T["world"].find_prefix(wn)
    if w:
        return (w[1][0], w[1][1], 0, "world", w[0])
    if island:
        return (isl[0], isl[1], 0, "island", "bands.islands")
    e = T["env"].find(env) if env else None
    eb = e[1][2] if e else 0
    vz = volcanic_zone(env)
    if volcanic and vz and T["tops"].get(vz):
        a, b, k = T["tops"][vz]
        return (a, b, eb, "lava", "Zone%d top %s" % (vz, k))
    if classic and region is not None:
        used = tile if (biome and tile and any(pglob(p, biome) for p in PASS.split(","))) else biome
        hit = T["biome"].find("%s.%s" % (region, used)) if used else None
        if hit is None and used != biome and biome:
            hit = T["biome"].find("%s.%s" % (region, biome))
        if hit is None:
            hit = T["biome"].find(region)
        if hit is None:
            hit = T["biome"].find(region + ".*")
        if hit:
            return (hit[1][0], hit[1][1], eb, "biome", hit[0])
    if e:
        return (e[1][0], e[1][1], 0, "env", e[0])
    z = zone_of_region(region) or zone_of_env(env)
    zz = T["zone"].find(z) if z else None
    if zz:
        return (zz[1][0], zz[1][1], 0, "zone", zz[0])
    return (dflt[0], dflt[1], 0, "default", "bands.default")


# Java's String.hashCode and the SplitMix64 roll (MobLevel.roll)
M64 = (1 << 64) - 1


def jhash(s):
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return h - (1 << 32) if h >= (1 << 31) else h


def mix(z):
    z &= M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def py_roll(seed, msb, lsb, role, a, b):
    if b <= a:
        return a
    h = mix((seed + 0x9E3779B97F4A7C15) & M64)
    h = mix(h ^ (msb & M64))
    h = mix(h ^ (lsb & M64))
    h = mix(h ^ (jhash(role or "") & M64))
    return a + h % (b - a + 1)


# vanilla role attitudes (the engine's default attitude is HOSTILE when a role sets none - SupportConfigBuilder bytecode)
def lenient(t):
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r",\s*([}\]])", r"\1", t)
    return json.loads(t)


def vanilla_roles():
    z = zipfile.ZipFile(AZ_PATH)
    roles, path = {}, {}
    for n in z.namelist():
        if n.startswith("Server/NPC/Roles/") and n.endswith(".json"):
            nm = n.rsplit("/", 1)[1][:-5]
            roles[nm] = lenient(z.read(n).decode("utf-8-sig", "replace"))
            path[nm] = n[len("Server/NPC/Roles/"):]

    def params(name, d=0):
        r = roles.get(name)
        if r is None or d > 12:
            return {}, None
        if r.get("Type") == "Variant":
            p, root = params(r.get("Reference"), d + 1)
            p = dict(p)
            p.update(r.get("Modify") or {})
            return p, root
        return dict((k, v["Value"]) for k, v in (r.get("Parameters") or {}).items() if isinstance(v, dict) and "Value" in v), name

    out = {}
    for nm, r in roles.items():
        if r.get("Type") in ("Abstract", "Component") or path[nm].startswith("_Core/") or nm == "Empty_Role":
            continue
        p, root = params(nm)
        rr = roles.get(root) or {}
        a = rr.get("DefaultPlayerAttitude")
        if isinstance(a, dict) and "Compute" in a:
            a = p.get(a["Compute"])
        if isinstance(a, dict):
            a = a.get("Value")
        if isinstance(p.get("DefaultPlayerAttitude"), str):
            a = p["DefaultPlayerAttitude"]
        out[nm] = ((a or "Hostile").upper(), root, path[nm])
    return out, z


PASSIVE_ROOTS = {"Template_Birds_Passive", "Template_Swimming_Passive", "Template_Beasts_Passive_Critter", "Template_Edible_Critter",
                 "Template_Placeholder", "Template_Livestock", "Template_Temple", "Template_Summoned_Ally", "Template_Animal_Neutral"}
NEUTRAL_OK = {"Boar", "Warthog", "Feran_Sharptooth", "Feran_Longtooth", "Feran_Burrower", "Feran_Windwalker"}
BOSS = ("Goblin_Duke", "Trork_Chieftain", "Dragon_", "Skeleton_Elite")


def expected_level(nm, att, root):
    if nm.startswith(BOSS):
        return False
    if att == "HOSTILE":
        return root not in PASSIVE_ROOTS
    if att == "NEUTRAL":
        return nm in NEUTRAL_OK or nm.startswith(("Scarak_", "Dungeon_Scarak_"))
    return False


def run():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JInt, JFloat, JLong, JString
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    # 0.1.1: + SkyyMenu-0.3.5.jar (section V draws the Server Setup rows with its real AdminPage; its classes load only there)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST, JAR, MENU_JAR], convertStrings=True)
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    HashMap = JClass("java.util.HashMap")

    # ---------------- A. load + verify + init
    z = zipfile.ZipFile(JAR)
    names = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    for n in names:
        try:
            Cls.forName(n, True, sysl)
            COUNT["A"] += 1
        except Exception as e:
            check(False, "A. load %s: %s" % (n, e))
    OKS[0] += COUNT["A"]
    print("A. loaded + verified + initialised (-Xverify:all): %d classes" % COUNT["A"])
    if FAILS:
        return
    # ---------------- M. manifest + class list
    man = json.loads(z.read("manifest.json").decode("utf-8"))
    check(man.get("Main") == PKG + "SkyyMobsPlugin" and man.get("Name") == VERSION + " SkyyMobs" and man.get("Group") == "Skyy"
          and str(man.get("Version")) == VERSION and man.get("IncludesAssetPack") is False, "M. manifest: %s" % man)
    want = sorted(PKG + c for c in ("CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask", "LevelDamage",
                                     "LevelDamageU", "LevelHook", "MobBands", "MobCfg", "MobCmds", "MobGlob", "MobHooks",
                                     "MobInfo", "MobLevel", "MobLevelFn", "MobLog", "MobMig", "MobPlateStep", "MobPruneTask", "MobRefresh",
                                     "MobScanTask", "MobsCmd", "MobsInfoCmd", "MobsInspectCmd", "MobsPlateCmd", "MobsReloadCmd", "MobsSetCmd",
                                     "SkyyMobsPlugin", "GapDamage", "GapDamageU", "MobGap", "MobInfoFn", "MobMig14"))
    check(names == want, "M. exactly the 36 classes (0.1.3's 31 + GapDamage, GapDamageU, MobGap, MobInfoFn, MobMig14; no LevelHookU - review F4): %s"
          % sorted(set(names) ^ set(want)))
    check(not [n for n in z.namelist() if n.endswith(".ui")], "M. no .ui file in the jar")

    Cfg0, Lvl, Glob = JClass(PKG + "MobCfg"), JClass(PKG + "MobLevel"), JClass(PKG + "MobGlob")

    class LinearCfg(object):
        """0.1.4: the 0.1.3 sections (every number of 0.1.1 - 0.1.3) run on the 0.1.4 jar in Per level shape: useDefaults / apply load the
        defaults with strength.shape=linear when the given properties do not name a shape; everything else goes straight to MobCfg"""
        def __getattr__(self, n):
            return getattr(Cfg0, n)

        def __setattr__(self, n, v):
            setattr(Cfg0, n, v)

        def useDefaults(self):
            c_ = Cfg0.props(Cfg0.DEF_CFG)
            c_.setProperty("strength.shape", "linear")
            Cfg0.apply(c_, Cfg0.props(Cfg0.DEF_BANDS))

        def apply(self, c_, b_):
            if c_.getProperty("strength.shape") is None or str(c_.getProperty("strength.shape")) == "curve":
                c_.setProperty("strength.shape", "linear")
            Cfg0.apply(c_, b_)
    Cfg = LinearCfg()
    Cfg.useDefaults()

    # ---------------- B. default tables = the refit
    def table(t):
        return dict((str(t.raw[i]), (int(t.a[i]), int(t.b[i]), int(t.c[i]))) for i in range(int(t.n)))
    BI, EN, WO, ZO = table(Cfg.BIOME), table(Cfg.ENV), table(Cfg.WORLD), table(Cfg.ZONE)
    jb = dict((k, v[:2]) for k, v in BI.items())
    azb = zipfile.ZipFile(AZ_PATH)
    reg_bio = collections.defaultdict(set)
    for n_ in azb.namelist():
        m_ = re.match(r"^Server/World/Default/Zones/([^/]+)/(?:Tile|Custom)\.([^/]+)\.json$", n_)
        if m_:
            reg_bio[m_.group(1)].add(m_.group(2))
    env_all = set(n_.rsplit("/", 1)[1][:-5] for n_ in azb.namelist() if n_.startswith("Server/Environments/") and n_.endswith(".json"))
    exact_refit = set("%s.%s" % rb for rb in REFIT_BIOMES)
    want_b = dict(("%s.%s" % rb, band) for rb, band in REFIT_BIOMES.items())
    for k, band in REFIT_PATTERNS.items():
        reg, _, pat = k.partition(".")
        if pat == "*":
            want_b[reg] = band
        else:
            for b_ in reg_bio[reg]:
                if pglob(pat, b_) and "%s.%s" % (reg, b_) not in exact_refit:
                    want_b["%s.%s" % (reg, b_)] = band
    want_b.update(ADDED)
    want_e = dict((k, v) for k, v in REFIT_ENV.items() if "*" not in k)
    for k, v in REFIT_ENV.items():
        if "*" in k:
            for e_ in env_all:
                if pglob(k, e_) and e_ not in REFIT_ENV:
                    want_e[e_] = v
    for (reg, bio), band in sorted(REFIT_BIOMES.items()):
        check(jb.get("%s.%s" % (reg, bio)) == band, "B. biome %s.%s = %s (refit), jar %s" % (reg, bio, band, jb.get("%s.%s" % (reg, bio))))
    for k, band in sorted(want_b.items()):
        check(jb.get(k) == band, "B. biome %s = %s (refit, patterns expanded with Assets.zip), jar %s" % (k, band, jb.get(k)))
    check(set(jb) == set(want_b), "B. the biome rows are exactly the refit (expanded) + the documented additions: %s" % sorted(set(jb) ^ set(want_b)))
    check(not [k for k in list(jb) + list(EN) if "*" in k], "B. no * key in the shipped tables (the kit refuses it in Server Setup)")
    check(EN == want_e, "B. environment rows = the refit / plan 4.6 (patterns expanded): %s" % sorted(set(EN.items()) ^ set(want_e.items())))
    check(dict((k, v[:2]) for k, v in ZO.items()) == REFIT_ZONE and not WO, "B. zone rows %s, no world rows %s" % (ZO, WO))
    for zz, (lo, hi) in LOCKED.items():
        rows = [v for k, v in jb.items() if k.startswith("Zone%d_" % zz)]
        check(min(r[0] for r in rows) == lo and max(r[1] for r in rows) == hi, "B. Zone %d biome rows span the LOCKED %d-%d" % (zz, lo, hi))
        check((int(Cfg.ZTOP_A[zz]), int(Cfg.ZTOP_B[zz])) == LAVA_TOPS[zz], "B. Zone %d top (hardest biome) = %s: %s %d-%d" % (
            zz, LAVA_TOPS[zz], Cfg.ZTOP_KEY[zz], Cfg.ZTOP_A[zz], Cfg.ZTOP_B[zz]))
    check(str(Cfg.ZTOP_KEY[1]).startswith("Zone1_Tier3.Forest_"), "B. Zone 1 top is a Tier 3 forest (Autumn / Moss / Azure): %s" % Cfg.ZTOP_KEY[1])
    check(jb["Zone1_Tier3.Forest_Azure"] == (18, 20), "B. the blue forest is the top of Zone 1 (18-20)")
    print("B. tables = refit: %d biome rows (%d refit exact, %d refit patterns expanded, %d added), %d env rows (%d refit), %d zone rows; zone tops %s" % (
        len(jb), len(REFIT_BIOMES), len(REFIT_PATTERNS), len(ADDED), len(EN), len(REFIT_ENV), len(ZO),
        dict((zz, (int(Cfg.ZTOP_A[zz]), int(Cfg.ZTOP_B[zz]))) for zz in LAVA_TOPS)))

    # ---------------- R. the lookup chain = the Python mirror
    PT = {"biome": PyTable(jb), "env": PyTable(EN), "world": PyTable({}), "zone": PyTable(dict((k, v[:2]) for k, v in ZO.items())),
          "tops": dict((zz, (int(Cfg.ZTOP_A[zz]), int(Cfg.ZTOP_B[zz]), str(Cfg.ZTOP_KEY[zz]))) for zz in LAVA_TOPS)}
    azz = zipfile.ZipFile(AZ_PATH)
    regions = collections.defaultdict(set)
    for n in azz.namelist():
        m = re.match(r"^Server/World/Default/Zones/([^/]+)/(Tile|Custom)\.([^/]+)\.json$", n)
        if m:
            regions[m.group(1)].add((m.group(2), m.group(3)))
    env_ids = sorted(set(n.rsplit("/", 1)[1][:-5] for n in azz.namelist() if n.startswith("Server/Environments/") and n.endswith(".json")))
    tiles = dict((r, sorted(b for t, b in s if t == "Tile")) for r, s in regions.items())
    ENVS = [None, "Env_Zone1_Azure", "Env_Zone1_Encounters", "Env_Zone1_Caves_Volcanic_T2", "Env_Zone2_Feran", "Env_Zone2_Caves_Volcanic_T3",
            "Env_Zone3_Outlander_Village", "Env_Zone3_Caves_Volcanic_T1", "Env_Zone4_Villages_Swamp", "Env_Zone4_Caves_Volcanic",
            "Env_Default_Void", "Env_Zone0_Cold"]

    def jres(wn, isl, cls_, reg, bio, til, env):
        r = Lvl.resolve(wn, isl, cls_, reg, bio, til, env)
        return (int(r[0]), int(r[1]), int(r[2]), str(r[3]), str(r[4]))
    n_cmp = 0
    for reg in sorted(regions):
        for typ, bio in sorted(regions[reg]):
            til = tiles[reg][0] if (typ == "Custom" and tiles.get(reg)) else bio
            for env in ENVS:
                got = jres("default", False, True, reg, bio, til, env)
                exp = py_resolve(PT, "default", False, True, reg, bio, til, env)
                n_cmp += 1
                if got != exp:
                    check(False, "R. resolve(%s, %s, tile %s, env %s) = %s, mirror %s" % (reg, bio, til, env, got, exp))
    for env in env_ids + ["Env_Portal_Goblin_Cave", "Env_Unknown_Thing", None]:
        for cls_ in (False,):
            got = jres("islandchain", False, cls_, None, None, None, env)
            exp = py_resolve(PT, "islandchain", False, cls_, None, None, None, env)
            n_cmp += 1
            if got != exp:
                check(False, "R. non-classic resolve(env %s) = %s, mirror %s" % (env, got, exp))
    OKS[0] += n_cmp
    # named cases (the plan's / refit's in-game tests as lookups)
    NAMED = [
        (("default", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", "Env_Zone1_Plains"), (1, 3, 0, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", "Env_Zone1_Azure"), (18, 20, 0, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Moss_Trork", "Forest_Moss", "Env_Zone1_Trork"), (16, 18, 0, "biome")),
        (("default", False, True, "Zone1_Tier1", "River_Plains_Smooth", "Plains_Smooth", None), (1, 3, 0, "biome")),
        (("default", False, True, "Zone1_Tier1", "Plains_Smooth_Kweebec", "Plains_Smooth", "Env_Zone1_Kweebec"), (1, 3, 0, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", "Env_Zone1_Caves_Goblins"), (18, 20, 1, "biome")),
        (("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", "Env_Zone1_Caves_Spiders"), (18, 20, 0, "biome")),
        (("default", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", "Env_Zone1_Caves_Volcanic_T1"), (18, 20, 0, "lava")),
        (("default", False, True, "Zone2_Tier1", "Savannah_Plains", "Savannah_Plains", "Env_Zone2_Caves_Volcanic_T2"), (28, 30, 0, "lava")),
        (("default", False, True, "Zone3_Tier1", "Forest_Fir", "Forest_Fir", "Env_Zone3_Caves_Volcanic_T3"), (43, 45, 0, "lava")),
        (("default", False, True, "Zone4_Tier4", "Wastes_Grasslands", "Wastes_Grasslands", "Env_Zone4_Caves_Volcanic"), (58, 60, 0, "lava")),
        (("default", False, True, "Zone2_Tier3", "Desert_Oasis_Hidden", "Desert_Barren", "Env_Zone2_Oasis"), (28, 30, 0, "biome")),
        (("default", False, True, "Zone3_Tier3", "Village_Outlander", "Forest_Frozen", "Env_Zone3_Outlander_Village"), (41, 43, 2, "biome")),
        (("default", False, True, "Zone4_Tier5", "Volcano_Wastes_Lava", "Wastes_Lava", "Env_Zone4_Volcanoes"), (55, 57, 0, "biome")),
        (("default", False, True, "Zone1_Shallow_Ocean", "Shore", "Shore", None), (1, 7, 0, "zone")),
        (("default", False, True, "Oceans", "Temperate_Kelp", "Temperate_Kelp", "Env_Zone0_Temperate"), (0, 0, 0, "default")),
        (("skywynn_z1", False, False, None, None, None, "Env_Zone1_Azure"), (16, 20, 0, "env")),
        (("skywynn_z1", False, False, None, None, None, "Env_Zone2_Somewhere"), (20, 24, 0, "zone")),
        (("island-abc", True, False, None, None, None, "Env_Default_Void"), (0, 0, 0, "island")),
        (("island-abc", False, False, None, None, None, "Env_Default_Void"), (0, 0, 0, "default")),
    ]
    for a, (lo, hi, bo, step) in NAMED:
        got = jres(*a)
        check(got[:4] == (lo, hi, bo, step), "R. %s -> %s, want %s" % (a, got, (lo, hi, bo, step)))
    Cfg.VOLCANIC = False
    got = jres("default", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", "Env_Zone1_Caves_Volcanic_T1")
    check(got[:4] == (1, 3, 0, "biome"), "R. lava rule off -> the ground above (1-3): %s" % (got,))
    got = jres("skywynn_z1", False, False, None, None, None, "Env_Zone1_Caves_Volcanic_T3")
    check(got[:4] == (14, 18, 0, "env"), "R. lava rule off on a non-classic world -> the env row 14-18: %s" % (got,))
    Cfg.VOLCANIC = True
    print("R. lookup chain = Python mirror: %d cases (every region x biome x %d envs, %d envs non-classic) + %d named" % (
        n_cmp, len(ENVS), len(env_ids) + 3, len(NAMED)))

    # world rows + islands through the real loader (a hand-made bands file)
    P = JClass("java.util.Properties")
    cp, bp = Cfg.props(Cfg.DEF_CFG), Cfg.props(Cfg.DEF_BANDS)
    bp.setProperty("world.dungeon_", "20,23")
    bp.setProperty("world.hub", "0,0")
    bp.setProperty("world.bad", "abc")
    cp.setProperty("bands.islands", "1-3")
    Cfg.apply(cp, bp)
    check(jres("dungeon_1", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", None)[:4] == (20, 23, 0, "world"), "R. world row dungeon_ (a name start) wins")
    check(jres("dungeon", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", None)[:4] == (1, 3, 0, "biome"), "R. ... but not for the shorter name dungeon")
    check(jres("hub", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", None)[:4] == (0, 0, 0, "world"), "R. world row 0,0 = no levels")
    check(jres("myisland", True, False, None, None, None, None)[:4] == (1, 3, 0, "island"), "R. bands.islands 1-3 on an island world")
    check("bad" not in [str(x) for x in Cfg.WORLD.raw], "R. a bad hand line (world.bad=abc) is skipped")
    bp2 = Cfg.props(Cfg.DEF_BANDS)
    bp2.setProperty("biome.Zone1_Tier1.*_Trork", "9,9")
    Cfg.apply(Cfg.props(Cfg.DEF_CFG), bp2)
    check(jres("default", False, True, "Zone1_Tier1", "Plains_Birch_Trork", "Plains_Birch", None)[:2] == (5, 7)
          and jres("default", False, True, "Zone1_Tier1", "Plains_Birch_Kweebec_Trork", "Plains_Birch", None)[:2] == (9, 9),
          "R. a hand-typed * key works at runtime; an exact row still beats it")
    Cfg.useDefaults()

    # ---------------- C. difficulty presets (0.1.1 ladder)
    PRE = dict((d, (h, m, "%s %s%% / %s%%" % (d.capitalize(), ("%g" % h), ("%g" % m)))) for d, (h, m) in LADDER.items())
    check(PRE["easy"][2] == "Easy 4% / 2%" and PRE["normal"][2] == "Normal 6% / 3%" and PRE["hard"][2] == "Hard 8% / 4%", "C. (the expected texts)")
    for d, (hp, dmg, txt) in PRE.items():
        Cfg.DIFFICULTY = d
        Cfg.derive(None)
        check(abs(float(Cfg.HP_STEP) - hp / 100) < 1e-12 and abs(float(Cfg.DMG_STEP) - dmg / 100) < 1e-12 and str(Cfg.difficultyText()) == txt,
              "C. %s = %s%% / %s%% (%s)" % (d, hp, dmg, Cfg.difficultyText()))
    Cfg.DIFFICULTY = "custom"
    Cfg.HP_PCT, Cfg.DMG_PCT = 5.5, 0.5
    Cfg.derive(None)
    check(abs(float(Cfg.HP_STEP) - 0.055) < 1e-12 and abs(float(Cfg.DMG_STEP) - 0.005) < 1e-12 and str(Cfg.difficultyText()) == "Custom 5.5% / 0.5%",
          "C. custom = the two rows (5.5 / 0.5): %s" % Cfg.difficultyText())
    Cfg.useDefaults()
    check(str(Cfg.DIFFICULTY) == "normal" and str(Cfg.difficultyText()) == "Normal 6% / 3%", "C. the default is Normal 6%% / 3%% (0.1's Hard): %s" % Cfg.difficultyText())
    check((float(Cfg.HP_PCT), float(Cfg.DMG_PCT)) == CUSTOM, "C. Custom's rows keep 0.1's defaults 4 / 2: %s / %s" % (Cfg.HP_PCT, Cfg.DMG_PCT))
    check((float(Cfg.HP_CAP), float(Cfg.DMG_CAP)) == CAPS, "C. caps x6 / x3.5 by default: %s / %s" % (Cfg.HP_CAP, Cfg.DMG_CAP))
    Cfg.DIFFICULTY = "Hard "          # a hand-typed word: derive trims + lower-cases (apply() already refuses an unknown word)
    Cfg.derive(None)
    check(abs(float(Cfg.HP_STEP) - 0.08) < 1e-12, "C. 'Hard ' (case / space) = hard")
    Cfg.DIFFICULTY = "nightmare"
    Cfg.derive(None)
    check(abs(float(Cfg.HP_STEP) - 0.06) < 1e-12 and abs(float(Cfg.DMG_STEP) - 0.03) < 1e-12, "C. an unknown word set directly falls back to Normal 6% / 3%")
    cp_ = Cfg.props(Cfg.DEF_CFG)
    cp_.setProperty("strength.difficulty", "brutal")
    cp_.remove("strength.hpCap")
    cp_.setProperty("strength.dmgCap", "x")
    Cfg.apply(cp_, Cfg.props(Cfg.DEF_BANDS))
    check(str(Cfg.DIFFICULTY) == "normal" and (float(Cfg.HP_CAP), float(Cfg.DMG_CAP)) == CAPS,
          "C. the loader: an unknown word -> normal, a missing / bad cap line -> the 0.1.1 default caps x6 / x3.5")
    Cfg.useDefaults()

    # ---------------- D. health / damage maths
    n = 0
    for d, (hp, dmg, _t) in list(PRE.items()) + [("custom", (12.0, 7.0, ""))]:
        Cfg.DIFFICULTY = d
        if d == "custom":
            Cfg.HP_PCT, Cfg.DMG_PCT = hp, dmg
        Cfg.derive(None)
        for L in range(0, 151):
            eh = 1.0 if L <= 1 else f32(min(CAPS[0], max(1.0, 1.0 + (hp / 100) * (L - 1))))
            ed = 1.0 if L <= 1 else f32(min(CAPS[1], max(1.0, 1.0 + (dmg / 100) * (L - 1))))
            if float(Cfg.hpMult(L)) != eh or float(Cfg.dmgMult(L)) != ed:
                check(False, "D. %s Lv %d: health x%s (want %s), damage x%s (want %s)" % (d, L, Cfg.hpMult(L), eh, Cfg.dmgMult(L), ed))
            n += 2
    OKS[0] += n
    Cfg.useDefaults()
    # the named numbers (Lv 1 / 20 / 60 of every preset, typed by hand above) through the jar's own code
    TABLE_D = []
    for (d, L), (h, dd) in sorted(MULT.items()):
        Cfg.DIFFICULTY = d
        Cfg.derive(None)
        gh, gd = float(Cfg.hpMult(L)), float(Cfg.dmgMult(L))
        check(abs(gh - h) < 1e-5 and abs(gd - dd) < 1e-5, "D. %s Lv %d = health x%s, damage x%s: %s / %s" % (d, L, h, dd, gh, gd))
        TABLE_D.append("%s Lv %d x%s / x%s" % (d.capitalize(), L, round(gh, 3), round(gd, 3)))
    Cfg.useDefaults()
    for L, h, dd in ((10, 1.54, 1.27), (30, 2.74, 1.87), (45, 3.64, 2.32)):        # the default (Normal 6% / 3% = 0.1's Hard) between
        check(abs(float(Cfg.hpMult(L)) - h) < 1e-5 and abs(float(Cfg.dmgMult(L)) - dd) < 1e-5,
              "D. default Normal Lv %d = health x%s, damage x%s: %s / %s" % (L, h, dd, Cfg.hpMult(L), Cfg.dmgMult(L)))
    Cfg.DIFFICULTY = "hard"
    Cfg.derive(None)
    check(float(Cfg.hpMult(60)) < CAPS[0] and float(Cfg.dmgMult(60)) < CAPS[1], "D. Hard Lv 60 = x5.72 / x3.36 is below the caps x6 / x3.5")
    first_cap = [L for L in range(1, 200) if float(Cfg.hpMult(L)) == CAPS[0] or float(Cfg.dmgMult(L)) == CAPS[1]]
    check(first_cap and first_cap[0] == 64, "D. Hard meets a cap first at Lv 64 (no zone band reaches it): %s" % first_cap[:1])
    check(float(Cfg.hpMult(100)) == 6.0 and float(Cfg.dmgMult(100)) == 3.5, "D. Hard Lv 100 is capped at x6 / x3.5")
    for d in ("easy", "normal"):
        Cfg.DIFFICULTY = d
        Cfg.derive(None)
        check(float(Cfg.hpMult(60)) < CAPS[0] and float(Cfg.dmgMult(60)) < CAPS[1], "D. %s Lv 60 is not capped" % d)
    Cfg.DIFFICULTY = "hard"
    Cfg.derive(None)
    Cfg.HP_CAP, Cfg.DMG_CAP = 5.0, 3.0
    check(float(Cfg.hpMult(60)) == 5.0 and float(Cfg.dmgMult(60)) == 3.0, "D. 0.1's caps x5 / x3 WOULD clip the new Hard at Lv 60 (why they moved)")
    Cfg.HP_CAP = 2.0
    check(float(Cfg.hpMult(60)) == 2.0, "D. a lower cap clips (x2)")
    Cfg.useDefaults()
    print("D. maths: %d multipliers (4 difficulties x Lv 0-150, float32 exact, caps x6 / x3.5) + %d named: %s" % (n, len(MULT), "; ".join(TABLE_D)))

    # ---------------- E. who gets a level
    roles, _z = vanilla_roles()
    nE = 0
    for nm, (att, root, path) in sorted(roles.items()):
        why = Cfg.whyNot(att, nm)
        got = why is None
        if got != expected_level(nm, att, root):
            check(False, "E. %s (%s, %s): whyNot = %s, expected %s" % (nm, att, root, why, "level" if expected_level(nm, att, root) else "none"))
        nE += 1
    OKS[0] += nE
    NAMED_E = [("HOSTILE", "Skeleton_Fighter", True), ("HOSTILE", "Trork_Warrior", True), ("NEUTRAL", "Boar", True),
               ("NEUTRAL", "Scarak_Defender", True), ("HOSTILE", "Scarak_Fighter", True), ("NEUTRAL", "Feran_Sharptooth", True),
               ("NEUTRAL", "Cow", False), ("NEUTRAL", "Sheep", False), ("HOSTILE", "Bluebird", False), ("HOSTILE", "Frog_Green", False),
               ("HOSTILE", "Mouse", False), ("NEUTRAL", "Kweebec_Merchant", False), ("NEUTRAL", "Klops_Merchant", False),
               ("NEUTRAL", "Kweebec_Razorleaf", False), ("NEUTRAL", "Feran_Civilian", False), ("REVERED", "Tamed_Boar", False),
               ("IGNORE", "Risen_Knight", False), ("HOSTILE", "Goblin_Duke", False), ("HOSTILE", "Trork_Chieftain", False),
               ("FRIENDLY", "Skeleton_Fighter", False), ("HOSTILE", "Floating_Pet_Blue", False), ("HOSTILE", "KazzyPets_Mount_Boar", False),
               ("HOSTILE", "KazzyPets_Mount_Cow_Undead", False), ("HOSTILE", "KazzyPets_Mount_Crawler_Void", False),
               ("HOSTILE", "Cow_Undead", True), ("HOSTILE", "Spectre_Void", True)]
    for att, nm, yes in NAMED_E:
        why = Cfg.whyNot(att, nm)
        check((why is None) == yes, "E. %s %s -> %s" % (att, nm, why))
    check(Cfg.whyNot("HOSTILE", None) is not None and Cfg.whyNot("HOSTILE", "") is not None, "E. no role (a player / not an NPC) -> no level")
    Cfg.NEUTRAL = False
    Cfg.derive(None)
    check(Cfg.whyNot("NEUTRAL", "Boar") is not None and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None,
          "E. neutral fighters off: Boar refused, skeletons still levelled")
    Cfg.useDefaults()
    check(sum(1 for nm, v in roles.items() if expected_level(nm, v[0], v[1])) > 200, "E. (more than 200 vanilla roles get levels)")
    OTHER, LEFT = (), ()
    try:
        # review F1: other mods' roles that share a vanilla prefix (the old Bear_* / Wolf_* / Spider* / Wraith* / Dungeon_* patterns
        # levelled them in the reviewer's real-hook run and 193 roles of Skyy's Mods folder) - the built-in list is exact vanilla ids now
        OTHER = ("Bear_Grizzly_Mount", "Wolf_Pet", "Spider_Mount", "Wraith_Trader", "Dungeon_BlacksmithNPCRole", "Dungeon_Hub_NPC_Role",
                 "Dungeon_ArcaneNPCRole", "Dungeon_Crypt_Boss", "Skeleton_Pet_Knight", "Zombie_Mount", "Trork_Boss_Warlord", "Goblin_Trader")
        for nm in OTHER:
            check(nm not in roles, "E. (the sample %s is not a vanilla role)" % nm)
            for att in ("HOSTILE", "NEUTRAL"):
                check(Cfg.whyNot(att, nm) is not None, "E. F1: another mod's %s %s gets no level: %s" % (att, nm, Cfg.whyNot(att, nm)))
        check(str(Cfg.ROLES) == "" and len(Cfg.P_ROLES) == 0, "E. F1: Extra mobs that get levels is empty by default: %r" % str(Cfg.ROLES))
        built = set(str(x) for x in str(Cfg.VANILLA).split(","))
        want_built = set(nm for nm, v in roles.items() if expected_level(nm, v[0], v[1]))
        check(built == want_built, "E. F1: the built-in list = exactly the vanilla role ids that get levels (%d): %s" % (len(built), sorted(built ^ want_built)[:8]))
        check(not [x for x in built if "*" in x], "E. F1: the built-in list holds no * pattern")
        check(Cfg.whyNot("HOSTILE", "skeleton_FIGHTER") is None and Cfg.whyNot("HOSTILE", "Trork_Sentry") is None,
              "E. F1: built-in ids match in any case; Trork_Sentry stays levelled (no *_Sentry* guard)")
        # the extra row + its guard patterns (an admin pattern never catches other mods' mounts / pets / NPCs / bosses)
        Cfg.ROLES = "Mosshorn*, Bear_*, Dungeon_*"
        Cfg.derive(None)
        check(Cfg.whyNot("NEUTRAL", "Mosshorn") is None and Cfg.whyNot("NEUTRAL", "Mosshorn_Plain") is None and Cfg.whyNot("HOSTILE", "Dungeon_Ghoul") is None,
              "E. an extra pattern levels its mobs (Mosshorn*, Dungeon_Ghoul)")
        for nm in ("Bear_Grizzly_Mount", "Dungeon_Crypt_Boss", "Dungeon_Hub_NPC_Role", "Dungeon_BlacksmithNPCRole"):
            check(Cfg.whyNot("HOSTILE", nm) == "in Never level these", "E. F1: the guard patterns keep %s out under an extra pattern: %s" % (nm, Cfg.whyNot("HOSTILE", nm)))
        Cfg.NEUTRAL = False
        Cfg.derive(None)
        check(Cfg.whyNot("NEUTRAL", "Mosshorn") is not None, "E. an extra NEUTRAL mob also follows Neutral fighters get levels")
        Cfg.useDefaults()
        # review F10: a blank extra row no longer switches levelling off
        Cfg.ROLES = "  "
        Cfg.derive(None)
        check(Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None and Cfg.whyNot("NEUTRAL", "Boar") is None, "E. F10: a blank Extra mobs row keeps the vanilla mobs levelled")
        Cfg.useDefaults()
        # review F2 (question for Skyy, the safe default kept): the neutral animals with an attack stay unlevelled by default
        LEFT = ("Mosshorn", "Mosshorn_Plain", "Cow", "Horse", "Moose_Bull", "Moose_Cow", "Bison", "Ram", "Camel", "Antelope", "Goat", "Deer_Stag",
                "Horse_Skeleton", "Horse_Skeleton_Armored", "Kweebec_Razorleaf", "Kweebec_Razorleaf_Patrol")
        for nm in LEFT:
            check(roles.get(nm, ("",))[0] == "NEUTRAL" and Cfg.whyNot("NEUTRAL", nm) is not None, "E. F2: %s (neutral animal / guard) gets no level by default" % nm)
        # review F5: levels.exclude = * strips every level (the uninstall step)
        Cfg.EXCLUDE = "*"
        Cfg.derive(None)
        refused = [nm for nm, v in roles.items() if Cfg.whyNot(v[0], nm) is None]
        check(not refused and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") == "in Never level these", "E. F5: Never level these = * -> no vanilla role gets a level: %s" % refused[:5])
        Cfg.useDefaults()
    except Exception as ex:
        check(False, "E. the review F1 / F2 / F5 / F10 checks could not run: %s" % ex)
        Cfg.useDefaults()
    print("E. who gets a level: %d vanilla roles = the classification, %d named cases; F1 %d other-mod roles, extras + guards, F10 blank "
          "extras, F2 %d neutral animals left out, F5 exclude *" % (nE, len(NAMED_E), len(OTHER), len(LEFT)))

    # ---------------- X. every role of the installed mods (read-only) that is not a vanilla role gets no level (review F1)
    mods_dir = B.MODS_DIR
    if os.path.isdir(mods_dir):
        other_roles, n_zip = set(), 0
        for fn_ in sorted(os.listdir(mods_dir)):
            if not fn_.lower().endswith((".jar", ".zip")):
                continue
            try:
                with zipfile.ZipFile(os.path.join(mods_dir, fn_)) as zz:
                    n_zip += 1
                    for e_ in zz.namelist():
                        m_ = re.search(r"(?:^|/)Server/NPC/Roles/(?:.*/)?([^/]+)\.json$", e_)
                        if m_ and m_.group(1) not in roles and not m_.group(1).startswith("_"):
                            other_roles.add(m_.group(1))
            except Exception:
                continue
        lev = sorted(nm for nm in other_roles if Cfg.whyNot("HOSTILE", nm) is None or Cfg.whyNot("NEUTRAL", nm) is None)
        check(not lev, "X. no role of another installed mod gets a level (%d roles in %d archives): %s" % (len(other_roles), n_zip, lev[:10]))
        print("X. installed mods: %d non-vanilla roles in %d archives, %d levelled" % (len(other_roles), n_zip, len(lev)))
    else:
        print("X. no Mods folder at %s - skipped" % mods_dir)

    # ---------------- G. nameplate text
    check(str(Lvl.plateText(9, "Trork Warrior")) == "[Lv 9] Trork Warrior", "G. colours off: [Lv 9] Trork Warrior")
    Cfg.COLOR_ON = True
    SEC = chr(167)
    exp = {"tag": "<color=#d6e4ee>[Lv 9] Trork Warrior</color>", "section": SEC + "f[Lv 9] Trork Warrior" + SEC + "r",
           "brace": "{#d6e4ee}[Lv 9] Trork Warrior"}
    for mk, e in exp.items():
        Cfg.MARKUP = mk
        got = str(Lvl.plateText(9, "Trork Warrior"))
        check(got == e, "G. %s markup: %r" % (mk, got))
        check(str(Lvl.plain(got)) == "[Lv 9] Trork Warrior" and bool(Lvl.isOurs(got)), "G. %s: plain() strips it back, isOurs" % mk)
    LAD = [(1, "#d6e4ee", "f"), (19, "#d6e4ee", "f"), (20, "#ffcc00", "6"), (29, "#ffcc00", "6"), (30, "#e8a93b", "6"),
           (45, "#ff6b6b", "c"), (60, "#ff6b6b", "c"), (61, "#cc66cc", "d"), (100, "#cc66cc", "d")]
    for L, hx, code in LAD:
        check(str(Lvl.hexFor(L)).lower() == hx and str(Lvl.legacy(hx)) == code, "G. Lv %d colour %s (section code %s): %s %s" % (
            L, hx, code, Lvl.hexFor(L), Lvl.legacy(hx)))
    Cfg.COLOR_ON = False
    Cfg.MARKUP = "tag"
    for t in ("1: <color=#ff6b6b>[Lv 9] Trork Warrior</color>", "2: " + SEC + "c[Lv 9] Trork Warrior" + SEC + "r", "3: {#ff6b6b}[Lv 9] Trork Warrior"):
        check(str(Lvl.plain(t)) == "[Lv 9] Trork Warrior" and bool(Lvl.isOurs(t)), "G. the platetest text %r is ours" % t[:12])
    check(not bool(Lvl.isOurs("Kweebec Merchant")) and not bool(Lvl.isOurs(None)), "G. a vanilla display name is not ours")
    for role, tk, nm in (("Skeleton_Fighter_Wander", None, "Skeleton Fighter"), ("Trork_Warrior", "server.npcRoles.Trork_Warrior.name", "Trork Warrior"),
                         ("Skeleton_Sand_Guard_Patrol", None, "Skeleton Sand Guard"), ("Boar", None, "Boar"), ("Bear_Grizzly_Sleep", None, "Bear Grizzly")):
        check(str(Lvl.nameOf(role, tk)) == nm, "G. name of %s without I18n = %r: %r" % (role, nm, Lvl.nameOf(role, tk)))
    Cfg.FORMAT = "{name} Lv.{level}"
    check(str(Lvl.plateText(12, "Hyena")) == "Hyena Lv.12" and bool(Lvl.isOurs("Hyena Lv.12")) and not bool(Lvl.isOurs("Hyena")),
          "G. a custom format {name} Lv.{level} renders and is recognised as ours")
    try:
        # review F7: after plate.format changes, a plate made with the default format or an earlier format of this run is still ours
        # (a mob that stops qualifying loses it); a vanilla / other mod's plate is not
        Cfg.useDefaults()
        Cfg.FORMAT = "<{level}> {name}"
        Cfg.derive(None)
        Cfg.FORMAT = "{name} Lv.{level}"
        Cfg.derive(None)
        check(bool(Lvl.isOurs("[Lv 9] Trork Warrior")), "G. F7: the default-format plate [Lv 9] Trork Warrior is still ours under {name} Lv.{level}")
        check(bool(Lvl.isOurs("<9> Boar")) and bool(Lvl.isOurs("Boar Lv.4")), "G. F7: a plate of a format used earlier this run is ours, and the current one")
        check(not bool(Lvl.isOurs("Kweebec Merchant")) and not bool(Lvl.isOurs("Bob")), "G. F7: a vanilla / hand-set name is still not ours")
        check(bool(Lvl.isOursFor("[Lv 9] Trork Warrior", "[Lv {level}] {name}")) and not bool(Lvl.isOursFor("[Lv 9] Trork Warrior", "{name} Lv.{level}"))
              and not bool(Lvl.isOursFor("x", None)), "G. F7: isOursFor checks one format")
        Cfg.useDefaults()
    except Exception as ex:
        check(False, "G. the review F7 checks could not run: %s" % ex)
        Cfg.useDefaults()
    print("G. nameplate: colours off, 3 markups, %d ladder colours, plain / isOurs, 5 names, F7 old formats" % len(LAD))

    # ---------------- F. persistence
    KP = str(Lvl.KEY_PREFIX)
    check(KP == "skyymobs_lv", "F. the save-slot key prefix is skyymobs_lv")
    for L in (1, 9, 17, 20, 60, 100, 999):
        check(int(Lvl.levelOfKey(str(Lvl.keyOf(L)))) == L, "F. key round trip %d" % L)
    for bad in ("NPC_Max", "skyymobs_lv", "skyymobs_lvx", "skyymobs_lv0", "skyymobs_lv12345", "Skyymobs_lv5", "skyymobs_level"):
        check(int(Lvl.levelOfKey(bad)) == -1, "F. %r is not a save slot" % bad)
    keys = JArray(JObject)(4)
    for i, k in enumerate(("NPC_Max", "Armor_Additive", "skyymobs_lv17", "junk")):
        keys[i] = JString(k)
    check(int(Lvl.savedFromKeys(keys)) == 17, "F. the saved level is read from the modifier keys (17)")
    check(Lvl.pick(-1, None) is None and str(Lvl.pick(17, JInt(5))[1]) == "saved" and int(Lvl.pick(-1, JInt(5))[0]) == 5
          and str(Lvl.pick(-1, JInt(5))[1]) == "kept", "F. pick: the save slot beats the session memory, else roll")
    MOBS, KEPT = Lvl.MOBS, Lvl.KEPT
    MI = JClass(PKG + "MobInfo")
    u1 = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    info = MI()
    info.level = 23
    info.world = "default"
    info.uuid = u1
    MOBS.put(u1, info)
    Lvl.forget(u1, True)
    check(MOBS.get(u1) is None and int(KEPT.get(u1)) == 23, "F. UNLOAD keeps the level in the session map (KEPT 23)")
    pk = Lvl.pick(-1, KEPT.remove(u1))
    check(int(pk[0]) == 23 and str(pk[1]) == "kept", "F. the reload (no save slot) gets 23 back from KEPT")
    MOBS.put(u1, info)
    Lvl.forget(u1, False)
    check(MOBS.get(u1) is None and KEPT.get(u1) is None, "F. REMOVE (death / despawn) forgets it everywhere")
    # deterministic roll = the Python mirror (layer 3)
    rnd = random.Random(7)
    nr = 0
    for _ in range(4000):
        seed = rnd.randrange(-(1 << 63), 1 << 63)
        msb, lsb = rnd.randrange(-(1 << 63), 1 << 63), rnd.randrange(-(1 << 63), 1 << 63)
        role = rnd.choice(["Skeleton_Fighter", "Trork_Warrior", "Boar", "", "Zombie_Aberrant_Big"])
        a = rnd.randrange(1, 60)
        b = a + rnd.randrange(0, 8)
        u = UUID(JLong(msb), JLong(lsb))
        got = int(Lvl.roll(JLong(seed), u, role, a, b))
        exp = py_roll(seed, msb, lsb, role, a, b)
        if got != exp:
            check(False, "F. roll(%d, %s, %s, %d, %d) = %d, mirror %d" % (seed, u, role, a, b, got, exp))
        if got != int(Lvl.roll(JLong(seed), u, role, a, b)):
            check(False, "F. roll is not deterministic")
        nr += 1
    OKS[0] += nr
    hist = collections.Counter(int(Lvl.roll(JLong(12345), UUID.randomUUID(), "Skeleton_Fighter", 18, 20)) for _ in range(3000))
    check(set(hist) == {18, 19, 20} and min(hist.values()) > 850, "F. the roll covers the band evenly (18-20: %s)" % dict(hist))
    res = Lvl.res(18, 20, 2, "biome", "Zone1_Tier3.Forest_Azure")
    check(20 <= int(Lvl.levelFor(res, JLong(1), u1, "Skeleton_Fighter")) <= 22, "F. levelFor adds the env bonus (18-20 +2)")
    Cfg.MAX_LEVEL = 21
    check(int(Lvl.levelFor(Lvl.res(30, 30, 0, "x", "y"), JLong(1), u1, "R")) == 21, "F. levelFor caps at levels.max")
    Cfg.useDefaults()
    check(int(Lvl.levelFor(Lvl.res(0, 0, 0, "default", "bands.default"), JLong(1), u1, "R")) == 0, "F. a 0-0 band = no level")
    for ov, om, nm_, want in ((50.0, 100.0, 164.0, 82.0), (100.0, 100.0, 164.0, 164.0), (0.0, 100.0, 164.0, 0.0), (150.0, 100.0, 50.0, 50.0)):
        check(abs(float(Lvl.share(ov, om, nm_)) - want) < 1e-4, "F. share(%s / %s -> max %s) = %s" % (ov, om, nm_, want))

    # a stand-in EntityStatMap / EntityStatValue (defined next to the engine classes, never in the jar) driving the jar's own code:
    # max = (100 + the additive sum) x the multiplicative SUM (EntityStatValue.computeModifiers, bytecode-checked). 0.1.3: it answers
    # minStatValue / maxStatValue the engine's way (EntityStatMap.minStatValue / maxStatValue bytecode: Math.min / Math.max of the current
    # value and the target, then EntityStatValue.set's clamp); sets counts setStatValue + maximizeStatValue (0.1.1's code on these maps
    # in FL), mms counts minStatValue + maxStatValue (0.1.3's writeValue) - the real engine queue is section NQ's
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")
    ESMN, ESVN = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap", "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
    SMON = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
    MODN = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
    sv = CP.makeClass(ESVN.rsplit(".", 1)[0] + ".SkyyMobsTestValue", CP.get(ESVN))
    for f in ("public java.util.HashMap mods;", "public float[] cell;"):
        sv.addField(CtField.make(f, sv))
    sv.addConstructor(CtNewConstructor.make("public SkyyMobsTestValue(java.util.HashMap m, float[] c) { super(); this.mods = m; this.cell = c; }", sv))
    sv.addMethod(CtNewMethod.make(r"""
public static float maxOf(java.util.HashMap mods, float base) {
  float add = 0.0f, mul = 0.0f; boolean any = false;
  java.util.Iterator it = mods.values().iterator();
  while (it.hasNext()) {
    %s m = (%s) it.next();
    if (m.getCalculationType() == %s$CalculationType.ADDITIVE) add += m.getAmount(); else { mul += m.getAmount(); any = true; }
  }
  float mx = base + add;
  return any ? mx * mul : mx;
}""" % (SMON, SMON, SMON), sv))
    sv.addMethod(CtNewMethod.make("public float get() { return this.cell[0]; }", sv))
    sv.addMethod(CtNewMethod.make("public float getMax() { return maxOf(this.mods, this.cell[1]); }", sv))
    sv.addMethod(CtNewMethod.make("public java.util.Map getModifiers() { return this.mods; }", sv))
    sv.toClass(JClass(ESVN).class_)
    sm = CP.makeClass(ESMN.rsplit(".", 1)[0] + ".SkyyMobsTestMap", CP.get(ESMN))
    for f in ("public java.util.HashMap mods;", "public float[] cell;", "public int puts;", "public int sets;", "public int mms;"):
        sm.addField(CtField.make(f, sm))
    SVN = sv.getName()
    sm.addMethod(CtNewMethod.make("public void init() { if (this.mods == null) { this.mods = new java.util.HashMap(); this.cell = new float[] { 100.0f, 100.0f }; } }", sm))
    sm.addMethod(CtNewMethod.make("public float maxNow() { init(); return %s.maxOf(this.mods, this.cell[1]); }" % SVN, sm))
    sm.addMethod(CtNewMethod.make("public float val() { init(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public void setVal(float v) { init(); this.cell[0] = v; }", sm))
    sm.addMethod(CtNewMethod.make("public void clamp() { float mx = maxNow(); if (this.cell[0] > mx) this.cell[0] = mx; if (this.cell[0] < 0.0f) this.cell[0] = 0.0f; }", sm))
    sm.addMethod(CtNewMethod.make("public %s get(int i) { init(); return new %s(this.mods, this.cell); }" % (ESVN, SVN), sm))
    sm.addMethod(CtNewMethod.make("public %s putModifier(int i, String k, %s m) { init(); this.puts++; Object o = this.mods.put(k, m); clamp(); return (%s) o; }" % (MODN, MODN, MODN), sm))
    sm.addMethod(CtNewMethod.make("public %s getModifier(int i, String k) { init(); return (%s) this.mods.get(k); }" % (MODN, MODN), sm))
    sm.addMethod(CtNewMethod.make("public %s removeModifier(int i, String k) { init(); Object o = this.mods.remove(k); clamp(); return (%s) o; }" % (MODN, MODN), sm))
    sm.addMethod(CtNewMethod.make("public float maximizeStatValue(int i) { this.sets++; this.cell[0] = maxNow(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public float setStatValue(int i, float v) { init(); this.sets++; this.cell[0] = v; clamp(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public float minStatValue(int i, float v) { init(); this.mms++; this.cell[0] = Math.min(this.cell[0], v); clamp(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public float maxStatValue(int i, float v) { init(); this.mms++; this.cell[0] = Math.max(this.cell[0], v); clamp(); return this.cell[0]; }", sm))
    ESMc = JClass(ESMN)
    TM = sm.toClass(ESMc.class_)
    TMc = JClass(TM.getName())
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def newmap():
        try:
            mm_ = TMc()
        except Exception:
            mm_ = U.allocateInstance(TM)
        mm_.init()
        return mm_
    SMOc, MTG = JClass(SMON), JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass(SMON + "$CalculationType")

    def fresh(npc_max=36.0):
        m = newmap()
        m.mods.put("NPC_Max", SMOc(MTG.MAX, CAL.ADDITIVE, JFloat(npc_max - 100.0)))
        m.setVal(JFloat(npc_max))
        return m
    # 0.1.2: these persistence checks are 0.1.1's with the floor OFF (floor 0 = the 0.1.1 numbers; Q / FL / RA / LV check the floor)
    Cfg.HP_FLOOR = 0
    Cfg.derive(None)
    m = fresh(36.0)
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000000b2")
    i2 = Lvl.apply(None, None, None, None, m, u2, None, "default", "Skeleton_Fighter", 20, True, "biome", Lvl.res(18, 20, 0, "biome", "Zone1_Tier3.Forest_Azure"))
    mod = m.mods.get("skyymobs_lv20")
    # 0.1.1: the default difficulty Normal = 6% a level (0.1's Hard): Lv 20 = x2.14 -> 36 x 2.14 = 77 HP (0.1's Normal gave x1.76 = 63)
    MX20 = 36.0 * f32(2.14)
    check(mod is not None and abs(float(mod.getAmount()) - f32(2.14)) < 1e-5 and abs(float(m.maxNow()) - MX20) < 1e-2 and abs(float(m.val()) - MX20) < 1e-2,
          "F. spawn: Skeleton Fighter (36 HP) Lv 20 -> modifier skyymobs_lv20 x2.14 (Normal 6%%), 77 / 77 HP: %s / %s" % (m.val(), m.maxNow()))
    check(int(Lvl.savedLevel(m, 0)) == 20 and MOBS.get(u2) is not None and int(MOBS.get(u2).level) == 20 and str(i2.name) == "Skeleton Fighter",
          "F. the save slot reads 20; MOBS has the mob; name Skeleton Fighter")
    # the reload: a copy of the saved modifiers (what the entity codec stores) -> same key, nothing changes
    m2 = newmap()
    m2.mods.putAll(m.mods)
    m2.setVal(JFloat(40.0))
    saved = int(Lvl.savedLevel(m2, 0))
    puts = int(m2.puts)
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", saved, False, "saved", None)
    check(saved == 20 and int(m2.puts) == puts and abs(float(m2.val()) - 40.0) < 1e-4, "F. reload: level 20 from the save slot, modifier untouched, wounded 40 HP stays 40")
    # a curve change (Hard 8%) before the reload: new amount, health share kept (40 / 77.04 -> same share of the new max)
    Cfg.DIFFICULTY = "hard"
    Cfg.derive(None)
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", saved, False, "saved", None)
    nm2 = 36.0 * f32(1.0 + 0.08 * 19)
    check(abs(float(m2.mods.get("skyymobs_lv20").getAmount()) - f32(2.52)) < 1e-5 and abs(float(m2.val()) - 40.0 / MX20 * nm2) < 1e-2,
          "F. a curve change (Hard 8%%) re-applies x2.52 and keeps the health share (%s HP of %s)" % (m2.val(), m2.maxNow()))
    Cfg.HEAL_ON_LOAD = True
    m2.setVal(JFloat(10.0))
    Cfg.DIFFICULTY = "normal"
    Cfg.derive(None)
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", saved, False, "saved", None)
    check(abs(float(m2.val()) - float(m2.maxNow())) < 1e-3, "F. healOnLoad on = full health after the reload")
    Cfg.useDefaults()
    # /mobs set 30 then strip
    Lvl.apply(None, None, None, None, m2, u2, None, "default", "Skeleton_Fighter", 30, False, "set", None)
    ks = sorted(str(k) for k in m2.mods.keySet())
    check(ks == ["NPC_Max", "skyymobs_lv30"] and int(MOBS.get(u2).level) == 30, "F. a new level replaces the old key (one save slot): %s" % ks)
    full = float(m2.val()) == float(m2.maxNow())
    Lvl.strip(None, None, None, m2, u2)
    ks = sorted(str(k) for k in m2.mods.keySet())
    check(ks == ["NPC_Max"] and MOBS.get(u2) is None and abs(float(m2.maxNow()) - 36.0) < 1e-4 and (not full or abs(float(m2.val()) - 36.0) < 1e-4),
          "F. strip: only NPC_Max left, 36 max, MOBS forgets the mob: %s" % ks)
    check(int(m.sets) == 0 and int(m2.sets) == 0 and int(m.mms) >= 1 and int(m2.mms) >= 3,
          "F. 0.1.3: the jar's spawn / reload / curve change / heal / set / strip wrote the health only through minStatValue / maxStatValue "
          "(min / max calls %d + %d, setStatValue / maximizeStatValue calls %d + %d)" % (int(m.mms), int(m2.mms), int(m.sets), int(m2.sets)))
    # the real EntityStatValue codec: the modifier key travels through BSON (the save path of every entity's stats)
    codec_note = ""
    try:
        ESV = JClass(ESVN)
        v = U.allocateInstance(ESV.class_)

        def setf(o, name, val):
            fld = ESV.class_.getDeclaredField(name)
            fld.setAccessible(True)
            fld.set(o, val)
        mods = HashMap()
        mods.put("skyymobs_lv17", SMOc(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(1.64)))
        mods.put("NPC_Max", SMOc(MTG.MAX, CAL.ADDITIVE, JFloat(-64.0)))
        setf(v, "id", JString("Health"))
        setf(v, "value", JFloat(50.0))
        setf(v, "modifiers", mods)
        # what EntityStatsModule.setup registers; EntityStatMap.CODEC is codecVersion(5) + legacyVersioned, so its nested values are
        # written / read with a VersionedExtraInfo (the plain ExtraInfo.getVersion() is always Integer.MAX_VALUE and would skip the
        # version-ranged CalculationType field of StaticModifier.ENTITY_CODEC)
        MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
        MODc.CODEC.register("Boost", SMOc.class_, SMOc.ENTITY_CODEC)
        MODc.CODEC.register("Static", SMOc.class_, SMOc.ENTITY_CODEC)
        VEI = JClass("com.hypixel.hytale.codec.VersionedExtraInfo")
        EMPTY = JClass("com.hypixel.hytale.codec.EmptyExtraInfo").EMPTY
        bson = ESV.CODEC.encode(v, VEI(5, EMPTY))
        v2 = ESV.CODEC.decode(bson, VEI(5, EMPTY))
        mm = v2.getModifiers()
        got = mm.get("skyymobs_lv17") if mm is not None else None
        ok = got is not None and abs(float(got.getAmount()) - 1.64) < 1e-5 and str(got.getCalculationType().name()) == "MULTIPLICATIVE" \
            and str(got.getTarget().name()) == "MAX"
        check(ok, "F. the entity stat codec (version 5) keeps skyymobs_lv17 = MAX MULTIPLICATIVE x1.64 through BSON: %s" % str(bson.toJson())[:300])
        check(int(Lvl.savedFromKeys(mm.keySet().toArray())) == 17, "F. ... and the jar reads level 17 back from the decoded map")
        codec_note = str(bson.toJson())
    except Exception as ex:
        check(False, "F. the EntityStatValue codec round trip could not run: %s" % ex)
    print("F. persistence (floor off = 0.1.1): key round trip, pick / forget / KEPT, %d rolls = mirror, stand-in stat map (spawn 77 / 77 HP at Normal 6%%, reload "
          "untouched, Hard 8%% curve change keeps the share, healOnLoad, set 30, strip), codec %s" % (nr, codec_note[:160]))

    # ---------------- I. mob:fn:level
    Fn = JClass(PKG + "MobLevelFn")()
    MOBS.clear()
    u3 = UUID.fromString("00000000-0000-0000-0000-0000000000c3")
    i3 = MI()
    i3.level, i3.world, i3.uuid = 14, "default", u3

    def call(*a):
        arr = JArray(JObject)(len(a))
        for k, x in enumerate(a):
            arr[k] = x
        return Fn.apply(arr)
    check(int(call("default", u3)) == -1, "I. unknown mob -> -1")
    MOBS.put(u3, i3)
    r = call("default", u3)
    check(str(r.getClass().getName()) == "java.lang.Integer" and int(r) == 14, "I. Object[]{world, uuid} -> Integer 14 (%s)" % r.getClass().getName())
    check(int(call("other_world", u3)) == -1 and int(call(None, u3)) == 14 and int(Fn.apply(u3)) == 14 and int(call(u3)) == 14,
          "I. wrong world -> -1; null world / bare UUID / Object[]{uuid} -> 14")
    for bad in (None, "x", JInt(5)):
        check(int(Fn.apply(bad)) == -1, "I. bad input %r -> -1" % (bad,))
    check(int(call()) == -1 and int(call("default", "not-a-uuid")) == -1 and int(call("default")) == -1, "I. short / wrong arrays -> -1")
    errs = []

    def hammer(k):
        try:
            for j in range(3000):
                uu = UUID(JLong(k), JLong(j))
                if j % 3 == 0:
                    ii = MI()
                    ii.level, ii.world, ii.uuid = j % 60 + 1, "default", uu
                    MOBS.put(uu, ii)
                rr = call("default", uu)
                if not (int(rr) == -1 or 1 <= int(rr) <= 60):
                    errs.append(int(rr))
                MOBS.remove(uu)
        except Exception as ex:
            errs.append(str(ex))
    ths = [threading.Thread(target=hammer, args=(k,)) for k in range(8)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    check(not errs, "I. 8 threads x 3000 calls while the map changes: no error / bad value (%s)" % errs[:3])
    br = Lvl.bridge()
    SysC = JClass("java.lang.System")
    check(int(SysC.identityHashCode(br)) == int(SysC.identityHashCode(SysC.getProperties().get("skyy.bridge"))),
          "I. the bridge map is System.getProperties().get(skyy.bridge)")
    MOBS.clear()
    print("I. mob:fn:level: Integer level, -1 for unknown / wrong world / bad input, 24,000 threaded calls")

    # stand-in engine objects (Unsafe.allocateInstance + their real fields; plain getters, bytecode-checked: World.getName / getChunkStore /
    # getWorldConfig / getEntityStore, ChunkStore.getGenerator (generatorLock + generator), EntityStore.getRefFromUUID (entitiesByUuid),
    # Ref.isValid (index != MIN_VALUE)) - never a real world
    def setfield(o, cls_name, name, val):
        c_ = JClass(cls_name).class_
        while c_ is not None:
            try:
                f_ = c_.getDeclaredField(name)
            except Exception:
                c_ = c_.getSuperclass()
                continue
            f_.setAccessible(True)
            f_.set(o, val)
            return
        raise KeyError(name)
    WN = "com.hypixel.hytale.server.core.universe.world.World"
    CSN = "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore"
    ESN = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
    REFN = "com.hypixel.hytale.component.Ref"
    AL = JClass("java.util.ArrayList")
    SysJ = JClass("java.lang.System")

    # ---------------- W. the worldgen cache (review F3)
    try:
        # (no WorldConfig: its static init needs the asset stores, so the classic branch below throws at the seed read - the same
        # try / not-cached path as the generator cache that is not ready, which is checked to throw on its own)
        w_ = U.allocateInstance(JClass(WN).class_)
        cs_ = U.allocateInstance(JClass(CSN).class_)
        setfield(w_, WN, "name", "wgtest")
        setfield(w_, WN, "chunkStore", cs_)
        setfield(cs_, CSN, "generatorLock", JClass("java.util.concurrent.locks.StampedLock")())
        WGm = Lvl.WG
        WGm.clear()
        r_ = Lvl.worldgen(w_, 5, 9)
        check(str(r_[4]) == "0" and int(WGm.size()) == 0, "W. F3: no generator attached yet -> no classic data, NOT cached: %s" % sorted(str(k) for k in WGm.keySet()))
        setfield(cs_, CSN, "generator", U.allocateInstance(JClass("com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator").class_))
        try:
            w_.getChunkStore().getGenerator().getZoneBiomeResultAt(1, 5, 9)
            threw = False
        except Exception:
            threw = True
        r_ = Lvl.worldgen(w_, 5, 9)
        check(threw and str(r_[4]) == "0" and int(WGm.size()) == 0,
              "W. F3: a ChunkGenerator world whose lookup throws (generator cache / world config not ready) -> the fallback rows, NOT cached: %s" % sorted(str(k) for k in WGm.keySet()))

        @JImplements("com.hypixel.hytale.server.core.universe.world.worldgen.IWorldGen")
        class FlatGen(object):
            @JOverride
            def shutdown(self): pass
            @JOverride
            def generate(self, *a): return None
            @JOverride
            def getTimings(self): return None
            @JOverride
            def getSpawnPoints(self, *a): return None
            @JOverride
            def getDefaultSpawnProvider(self, *a): return None
        setfield(cs_, CSN, "generator", FlatGen())
        r_ = Lvl.worldgen(w_, 5, 9)
        Lvl.worldgen(w_, 6, 9)
        Lvl.worldgen(w_, 5, 9)
        keys_ = sorted(str(k) for k in WGm.keySet())
        check(str(r_[4]) == "0" and keys_ == ["wgtest:5:9", "wgtest:6:9"],
              "W. F3: a non-classic generator (void / flat world) IS cached, one entry per exact block column (no 8x8 cell): %s" % keys_)
        check(int(Lvl.WG_MAX) == 10000, "W. the cache is bounded (WG_MAX 10000, cleared when full)")
        WGm.clear()
        print("W. worldgen cache: missing generator + throwing ChunkGenerator not cached, non-classic cached per exact column")
    except Exception as ex:
        check(False, "W. the worldgen cache section could not run: %s" % ex)

    # ---------------- N. the prune (review F6)
    try:
        WeakRef = JClass("java.lang.ref.WeakReference")
        now = int(SysJ.currentTimeMillis())
        wa, wb = JClass("java.lang.Object")(), JClass("java.lang.Object")()

        def mob(i, wref, world, age):
            ii = MI()
            ii.uuid = UUID.fromString("00000000-0000-0000-0002-%012d" % i)
            ii.wref, ii.world, ii.level, ii.at = wref, world, 5, JLong(now - age)
            MOBS.put(ii.uuid, ii)
            return ii.uuid
        MOBS.clear()
        ua = mob(1, WeakRef(wa), "a", 120000)          # its world is loaded -> kept
        mob(2, WeakRef(wb), "b", 120000)               # its world was removed -> pruned
        mob(3, WeakRef(None), "c", 120000)             # its world object was collected -> pruned
        ud = mob(4, None, "w1", 120000)                # no reference, a loaded world name -> kept
        mob(5, None, "gone", 120000)                   # no reference, no such world -> pruned
        uf = mob(6, WeakRef(wb), "b", 1000)            # removed world, but added 1 s ago (60 s grace) -> kept
        MOBS.put(UUID.fromString("00000000-0000-0000-0002-000000000007"), "junk")   # not a MobInfo -> pruned
        lw, ln = AL(), AL()
        lw.add(wa)
        ln.add("w1")
        ln.add("a")
        n_ = int(Lvl.pruneWith(lw, ln, JLong(now)))
        left = sorted(str(k) for k in MOBS.keySet())
        check(n_ == 4 and left == sorted(str(x) for x in (ua, ud, uf)), "N. F6: pruneWith forgets removed / collected worlds' mobs (4), keeps loaded, by-name and young ones: %d, %s" % (n_, left))
        uh = mob(8, None, "zzz", 120000)
        check(int(Lvl.pruneWith(lw, None, JLong(now))) == 0 and MOBS.get(uh) is not None, "N. names unknown -> a mob without a world reference is kept")
        # pruneWorld on a stand-in world: gone and invalid refs are forgotten, live / young / other-world entries stay
        es_ = U.allocateInstance(JClass(ESN).class_)
        byu = HashMap()
        setfield(es_, ESN, "entitiesByUuid", byu)
        wp = U.allocateInstance(JClass(WN).class_)
        setfield(wp, WN, "name", "prunetest")
        setfield(wp, WN, "entityStore", es_)
        good, bad = U.allocateInstance(JClass(REFN).class_), U.allocateInstance(JClass(REFN).class_)
        setfield(bad, REFN, "index", JInt(-2147483648))
        check(bool(good.isValid()) and not bool(bad.isValid()), "N. (stand-in refs: one valid, one invalid)")
        MOBS.clear()
        p1 = mob(11, WeakRef(wp), "prunetest", 120000)
        byu.put(p1, good)
        mob(12, WeakRef(wp), "prunetest", 120000)
        p3 = mob(13, WeakRef(wp), "prunetest", 120000)
        byu.put(p3, bad)
        p4 = mob(14, WeakRef(wp), "prunetest", 1000)
        p5 = mob(15, WeakRef(wa), "a", 120000)
        k_ = int(Lvl.pruneWorld(wp, JLong(now)))
        left = sorted(str(k) for k in MOBS.keySet())
        check(k_ == 2 and left == sorted(str(x) for x in (p1, p4, p5)), "N. F6: pruneWorld forgets the mobs whose entity is gone / invalid (2): %d, %s" % (k_, left))
        check(bool(Lvl.hasMobsIn(wp)) and not bool(Lvl.hasMobsIn(wb)), "N. hasMobsIn finds the world of a levelled mob by identity")
        p6 = mob(16, WeakRef(wp), "prunetest", 120000)
        PT_ = JClass(PKG + "MobPruneTask")
        PT_(wp).run()
        check(MOBS.get(p6) is None and MOBS.get(p1) is not None, "N. MobPruneTask(world) runs pruneWorld")
        before = int(MOBS.size())
        PT_(None).run()
        check(Lvl.liveWorlds() is None and int(MOBS.size()) == before, "N. MobPruneTask(null) without a Universe (bare JVM) changes nothing")
        # apply() keeps a WEAK reference to the mob's world
        m9 = fresh(36.0)
        u9 = UUID.fromString("00000000-0000-0000-0002-000000000099")
        i9 = Lvl.apply(None, None, None, None, m9, u9, wp, "prunetest", "Skeleton_Fighter", 5, True, "biome", None)
        check(i9.wref is not None and int(SysJ.identityHashCode(i9.wref.get())) == int(SysJ.identityHashCode(wp)) and str(i9.world) == "prunetest",
              "N. apply() stores a weak reference to the World")
        MOBS.clear()
        print("N. prune: pruneWith (removed, collected, by name, grace, junk), pruneWorld (gone / invalid refs), MobPruneTask both modes, apply wref")
    except Exception as ex:
        check(False, "N. the prune section could not run: %s" % ex)

    # ---------------- T. /mobs platetest: one test per mob (review F11)
    try:
        PSt = JClass(PKG + "MobPlateStep")
        RUN = PSt.RUNNING
        RUN.clear()
        ut = UUID.fromString("00000000-0000-0000-0003-000000000001")
        check(bool(PSt.claim(ut, JLong(1000))) and not bool(PSt.claim(ut, JLong(2000))), "T. F11: a second plate test on the same mob is refused while one runs")
        check(bool(PSt.claim(ut, JLong(40000))), "T. F11: a claim older than 30 s (the world stopped mid-test) is taken over")
        check(not bool(PSt.claim(None, JLong(1))), "T. no uuid -> no claim")
        tx = JArray(JString)(1)
        tx[0] = "1: x"
        PSt(None, ut, tx, None, None, "Boar").run()          # no world: the step fails at once -> the finally releases the claim
        check(RUN.get(ut) is None and bool(PSt.claim(ut, JLong(50000))), "T. F11: a plate test that stops releases its claim; the mob can be tested again")
        RUN.clear()
        print("T. platetest claims: one per mob, stale takeover, released on every end path")
    except Exception as ex:
        check(False, "T. the platetest section could not run: %s" % ex)

    # ---------------- H. permissions (the engine's own code)
    root = JClass(PKG + "MobsCmd")()
    subs = root.getSubCommands()
    SUBS = dict((str(k), subs.get(k)) for k in subs.keySet())
    check(sorted(SUBS) == ["info", "inspect", "platetest", "reload", "set"], "H. /mobs sub-commands: %s" % sorted(SUBS))
    check([str(x) for x in root.getPermissionGroups()] == ["hytale:Adventurer"], "H. /mobs gives its node to hytale:Adventurer")
    check([str(x) for x in SUBS["info"].getPermissionGroups()] == ["hytale:Adventurer"], "H. /mobs info gives its node to hytale:Adventurer")
    for k in ("inspect", "set", "platetest", "reload"):
        c = SUBS[k]
        g = c.getPermissionGroups()
        check(str(c.getPermission()) == "skyymobs.admin" and g is not None and len(g) == 0, "H. /mobs %s: requirePermission skyymobs.admin + no groups (%s, %s)" % (
            k, c.getPermission(), g))
    try:
        fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        fu.setAccessible(True)
        U = fu.get(None)
        own = U.allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
        root.setOwner(own)
    except Exception as ex:
        print("   no CommandManager owner (%s)" % ex)
    rec = root.getPermissionGroupsRecursive()
    grp = dict((str(k), sorted(str(x) for x in rec.get(k))) for k in rec.keySet())
    allnodes = [n for v in grp.values() for n in v]
    check(list(grp) == ["hytale:Adventurer"] and len(grp["hytale:Adventurer"]) == 2 and "skyymobs.admin" not in allnodes,
          "H. the virtual groups: only hytale:Adventurer, holding exactly the two player nodes (/mobs, /mobs info), never skyymobs.admin: %s" % grp)
    PM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    HashSet, ArrayList = JClass("java.util.HashSet"), JClass("java.util.ArrayList")

    def jset(*xs):
        s = HashSet()
        for x in xs:
            s.add(x)
        return s
    USERS = {"plain": ([], ["hytale:Adventurer"]), "op": ([], ["hytale:Admin"]), "holder": (["skyymobs.admin"], ["hytale:Adventurer"]),
             "skyystar": (["skyy.*"], ["hytale:Adventurer"])}
    IDS = dict((k, UUID.fromString("00000000-0000-0000-0001-%012d" % (i + 1))) for i, k in enumerate(sorted(USERS)))
    BY = dict((str(v), k) for k, v in IDS.items())
    GROUPS = {"hytale:Admin": ["*"], "hytale:Adventurer": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "mobs-test"
        @JOverride
        def getUserPermissions(self, u): return jset(*USERS.get(BY.get(str(u)), ([], []))[0])
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(BY.get(str(u)), ([], []))[1])
        @JOverride
        def getGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getEffectiveGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset(*GROUPS.keys())
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
        @JOverride
        def addUserPermissions(self, *a): return None
        @JOverride
        def removeUserPermissions(self, *a): return None
        @JOverride
        def addUserToGroup(self, *a): return None
        @JOverride
        def addGroupPermissions(self, *a): return None
        @JOverride
        def removeGroupPermissions(self, *a): return None
        @JOverride
        def removeUserFromGroup(self, *a): return None
        @JOverride
        def setUserGroup(self, *a): return None

    def jfield(cls, name):
        c = cls.class_
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    perm_ok = True
    try:
        pm = U.allocateInstance(PM.class_)
        provs = ArrayList()
        provs.add(Prov())
        jfield(PM, "providers").set(pm, provs)
        virt = HashMap()
        for k in rec.keySet():
            virt.put(k, HashSet(rec.get(k)))
        jfield(PM, "virtualGroups").set(pm, virt)
        f_inst = jfield(PM, "instance")
        old_pm = f_inst.get(None)
        f_inst.set(None, pm)
    except Exception as ex:
        perm_ok = False
        check(False, "H. could not set up a PermissionsModule stand-in: %s" % ex)
    if perm_ok:
        @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
        class Sender(object):
            def __init__(self, who):
                self.who = who

            @JOverride
            def hasPermission(self, *a):
                q = a[0]
                nn = str(q) if isinstance(q, str) else str(q.getId())
                return bool(PM.get().hasPermission(IDS[self.who], nn))

            @JOverride
            def getUsername(self):
                return self.who

            @JOverride
            def getUuid(self):
                return IDS[self.who]

            @JOverride
            def sendMessage(self, msg):
                pass
        try:
            for who, admin in (("plain", False), ("skyystar", False), ("op", True), ("holder", True)):
                s = Sender(who)
                check(bool(root.hasPermission(s)) and bool(SUBS["info"].hasPermission(s)), "H. %s may run /mobs and /mobs info" % who)
                for k in ("inspect", "set", "platetest", "reload"):
                    check(bool(SUBS[k].hasPermission(s)) == admin, "H. /mobs %s %s for %s" % (k, "allowed" if admin else "refused", who))
        finally:
            f_inst.set(None, old_pm)
    print("H. permissions: /mobs + /mobs info for every player; inspect / set / platetest / reload only with skyymobs.admin or op")

    # ================================================================================================ 0.1.1 helpers + sections O / U / V / Z
    Integer = JClass("java.lang.Integer")
    JStr = JClass("java.lang.String")
    Pub = JClass(PKG + "CfgPub")
    Mig = JClass(PKG + "MobMig")
    LogC, HistC, RowsC = JClass(PKG + "CfgLog"), JClass(PKG + "CfgHist"), JClass(PKG + "CfgRows")
    OLD = {}

    def jar_cls(jar, name):
        """a class of an earlier SkyyMobs jar through a child-first loader (one loader per jar; the loader class is made once here;
        never mixed with the 0.1.3 classes on the classpath)"""
        if "loaderclass" not in OLD:
            CPo = JClass("javassist.ClassPool")(False)
            CPo.appendSystemPath()
            ldr = CPo.makeClass(PKG + "SkyyMobsOldJarLoader", CPo.get("java.net.URLClassLoader"))
            ldr.addConstructor(CtNewConstructor.make("public SkyyMobsOldJarLoader(java.net.URL[] u, ClassLoader p) { super(u, p); }", ldr))
            ldr.addMethod(CtNewMethod.make(r"""
protected Class loadClass(String n, boolean r) throws ClassNotFoundException {
  Class c = findLoadedClass(n);
  if (c == null && n.startsWith("com.skyy.mobs.")) {
    try { c = findClass(n); } catch (ClassNotFoundException e) { c = null; }
  }
  if (c == null) return super.loadClass(n, r);
  if (r) resolveClass(c);
  return c;
}""", ldr))
            lc = ldr.toClass(JClass(PKG + "MobLog").class_)
            OLD["loaderclass"] = JClass(str(lc.getName()))
        if jar not in OLD:
            urls = JArray(JClass("java.net.URL"))(1)
            urls[0] = JClass("java.io.File")(jar).toURI().toURL()
            OLD[jar] = OLD["loaderclass"](urls, sysl)
        c = Cls.forName(PKG + name, True, OLD[jar])
        check(c.getClassLoader() == OLD[jar] or c.getClassLoader().equals(OLD[jar]), "(the %s %s comes from %s)" % (
            os.path.basename(jar), name, os.path.basename(jar)))
        return c

    def old_cls(name):
        """a class of SkyyMobs-0.1.jar (child-first)"""
        return jar_cls(OLD_JAR, name)

    def pin_cls(name):
        """a class of SkyyMobs-0.1.3.jar, the SET pin (child-first)"""
        return jar_cls(PIN_JAR, name)

    def prev_cls(name):
        """a class of SkyyMobs-0.1.2.jar, the SET pin (child-first)"""
        return jar_cls(PREV_JAR, name)

    def v011_cls(name):
        """a class of SkyyMobs-0.1.1.jar (child-first): floor 0 = its numbers (Q / FL), its default text (U2)"""
        return jar_cls(V011_JAR, name)

    def jcall(cls, name, *args):
        """a static method of an isolated class by reflection; args = (Java type, value) pairs"""
        ts, vs = JArray(Cls)(len(args)), JArray(JObject)(len(args))
        for k, (t, v) in enumerate(args):
            ts[k] = t
            vs[k] = v
        return cls.getMethod(name, ts).invoke(None, vs)

    def sfield(cls, name):
        return cls.getField(name).get(None)

    DOC01 = "# Difficulty: easy (3% health / 1.5% damage per level), normal (4% / 2%), hard (6% / 3%) or custom (the two values below)."
    DOC011 = "# Difficulty: easy (4% health / 2% damage per level), normal (6% / 3%), hard (8% / 4%) or custom (the two values below)."
    MARK = str(Mig.MG_MARK)

    def expect_mig(text, caps=True):
        """an independent mirror of the update for a file laid out like the 0.1 default (the difficulty block): the marker on its own
        line above the comment run on top of strength.difficulty, the 0.1 comment line swapped, untouched caps moved; CR kept per line"""
        ls = text.split("\n")
        body = [x[:-1] if x.endswith("\r") else x for x in ls]
        out = []
        for k, (raw, b) in enumerate(zip(ls, body)):
            cr = "\r" if raw.endswith("\r") else ""
            if b == DOC01:
                out.append(DOC011 + cr)
            elif caps and b == "strength.hpCap=5":
                out.append("strength.hpCap=6" + cr)
            elif caps and b == "strength.dmgCap=3":
                out.append("strength.dmgCap=3.5" + cr)
            else:
                out.append(raw)
        at = [k for k, b in enumerate(body) if b.startswith("strength.difficulty=")][0]
        while at > 0 and body[at - 1].startswith("#"):
            at -= 1
        out.insert(at, MARK + ("\r" if ls[at].endswith("\r") else ""))
        return "\n".join(out)

    def snapdir(d):
        out = {}
        for dp, _dn, fns in os.walk(d):
            for f_ in fns:
                p_ = os.path.join(dp, f_)
                out[os.path.relpath(p_, d)] = (open(p_, "rb").read(), os.path.getmtime(p_))
        return out

    def section_v(hdr, rows):
        """V: draw every tab and row of a header with SkyyMenu 0.3.5's own AdminPage and measure what it sends"""
        import skyyui as SUI
        SUI.verify(quiet=True)
        check(SUI.font_table("Default", True) is not None and SUI.font_table("Default", False) is not None,
              "V. the client's font tables are readable (Client/Data/Shared/UI/Fonts) - the widths are the client's own glyph advances")
        mh = hashlib.sha256(open(MENU_JAR, "rb").read()).hexdigest()
        dep = os.path.join(DEPLOYED, "SkyyMenu.jar")
        if os.path.isfile(dep):
            dv = json.loads(zipfile.ZipFile(dep).read("manifest.json").decode("utf-8")).get("Version")
            dh = hashlib.sha256(open(dep, "rb").read()).hexdigest()
            if str(dv) == "0.3.5":
                check(dh == mh, "V. the deployed SkyyMenu.jar (0.3.5) = SkyyMenu/SkyyMenu-0.3.5.jar (%s / %s)" % (dh[:12], mh[:12]))
            else:
                print("   note: the deployed SkyyMenu is %s - this check measured 0.3.5 (the SET pin when 0.1.1 was built)" % dv)
        UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
        UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
        AP = JClass(MPKG + "AdminPage")
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        pr_ = U.allocateInstance(PRc.class_)
        setfield(pr_, "com.hypixel.hytale.server.core.universe.PlayerRef", "uuid", UUID.fromString("00000000-0000-0000-0000-0000000000ad"))
        BTN = re.compile(r'TextButton #(\w+) \{ Anchor: \(Width: (\d+), Height: (\d+)\); Text: "([^"]*)"; (.*)\}\s*$', re.S)
        LAB = re.compile(r'Label #(\w+) \{ Anchor: \((?:Width: (\d+), )?Height: (\d+)\); Text: "([^"]*)"; Style: \((.*?)\); \}', re.S)

        def cmds(b):
            out = []
            for c in list(b.getCommands()):
                out.append((str(c.selector) if c.selector is not None else "", str(c.text) if c.text is not None else "",
                            str(c.data) if c.data is not None else ""))
            return out

        def measure(mod, what, cl):
            """[(what, id, text, px, box, fs, bold)] for every TextButton and every sized Label with a text in one command list"""
            labs, sets, got = {}, {}, []
            for sel, txt, data in cl:
                if sel.endswith(".Text") and data:
                    try:
                        sets[sel[1:-5]] = json.loads(data)["0"]
                    except Exception:
                        sets[sel[1:-5]] = data
                m_ = BTN.match(txt.strip())
                if m_:
                    fs = int(re.search(r"FontSize: (\d+)", m_.group(5)).group(1))
                    bold = "RenderBold: true" in m_.group(5)
                    t = m_.group(4)
                    got.append((what, m_.group(1), t, SUI.text_width(t, fs, bold), int(m_.group(2)), fs, bold))
                for m2 in LAB.finditer(txt):
                    if m2.group(2):
                        st = m2.group(5)
                        labs[m2.group(1)] = (int(m2.group(2)), int(re.search(r"FontSize: (\d+)", st).group(1)), "RenderBold: true" in st)
            for i_, (w_, fs, bold) in labs.items():
                if i_ in sets and sets[i_]:
                    got.append((what, i_, sets[i_], SUI.text_width(sets[i_], fs, bold), w_, fs, bold))
            return got

        def draw(mod, h, rws):
            page = AP(pr_, "mod", mod)
            allm = []
            tabs = []
            for i in range(len(h[5])):
                b, ev = UCB(), UEB()
                lab = str(AP.catLabel(h, i))
                page.tabRow(b, ev, i, lab, i == 0, "atab")
                ms = measure(mod, "tab " + str(h[5][i]), cmds(b))
                tabs.append((lab, [m_[2] for m_ in ms if m_[1].startswith("SkyyAdmTab")]))
                allm.extend(ms)
            choices = {}
            for i, r in enumerate(rws):
                typed = r[3] in ("int", "dec", "text", "range", "color")
                for q in ("", r[1]):
                    for dr in ((False, True) if typed else (False,)):
                        page.drafts.clear()
                        if dr:
                            page.drafts.put(r[0], "123456")
                        b, ev = UCB(), UEB()
                        page.drawRow(b, ev, h, i, 0, True, True, q)
                        cl = cmds(b)
                        ms = measure(mod, "row %s%s%s" % (r[0], " (search hit)" if q else "", " (draft)" if dr else ""), cl)
                        allm.extend(ms)
                        if r[3] == "choice" and not q and not dr:
                            choices[r[0]] = [m_[2] for m_ in ms if m_[1].startswith("SkyyAdmCh")]
            page.drafts.clear()
            return allm, tabs, choices

        def problems(allm, tabs, choices, rws):
            """what does not fit (one line per text, whichever row variant drew it) + tabs / choices drawn differently from their labels"""
            bad = []
            for what, i_, t, px, box, fs, bold in allm:
                if px > box - FIT_PAD:
                    s_ = "%s #%s %r: %.1f px in %d px (FontSize %d%s)" % (what.split(" (")[0], i_, t, px, box, fs, " bold" if bold else "")
                    if s_ not in bad:
                        bad.append(s_)
            for lab, drawn in tabs:
                if drawn != [lab]:
                    bad.append("tab %r drawn as %r" % (lab, drawn))
            for r in rws:
                if r[3] == "choice":
                    want = [(p.split("|", 1)[1] if "|" in p else p).strip() for p in r[7].split(",")]
                    if choices.get(r[0]) != want:
                        bad.append("choices of %s drawn as %r, labels %r" % (r[0], choices.get(r[0]), want))
            return bad

        hm = AP.hdr("SkyyMobs")
        if not check(hm is not None and str(hm[3]) == VERSION, "V. SkyyMenu's AdminPage.hdr reads the published SkyyMobs %s header" % VERSION):
            return
        allm, tabs, choices = draw("SkyyMobs", hm, rows)
        bad = problems(allm, tabs, choices, rows)
        check(not bad, "V. every SkyyMobs Server Setup text drawn by SkyyMenu 0.3.5 fits (%d px to spare): %s" % (FIT_PAD, bad[:6]))
        n_btn = len([m_ for m_ in allm if m_[1].startswith(("SkyyAdmTab", "SkyyAdmCh", "SkyyAdmEdit", "SkyyAdmOn", "SkyyAdmOff", "SkyyAdmSet",
                                                            "SkyyAdmMinus", "SkyyAdmPlus", "SkyyAdmDef"))])
        names = [m_ for m_ in allm if m_[1].startswith("SkyyAdmName")]
        helps = [m_ for m_ in allm if m_[1].startswith("SkyyAdmDesc")]
        check(len(names) == len(helps) and len(names) >= 2 * len(rows), "V. a name + a help line for every drawn row variant (%d)" % len(names))
        check([t for _l, t in tabs] == [["Which mobs"], ["Strength"], ["Level curve"], ["Level gap"], ["Level bands"], ["Nameplate"]], "V. the tabs as drawn: %s" % tabs)
        check(choices.get("strength.difficulty") == ["Easy", "Normal", "Hard", "Custom"], "V. the Difficulty buttons as drawn: %s" % choices.get("strength.difficulty"))
        tight = sorted(allm, key=lambda m_: m_[4] - m_[3])[:3]
        OKS[0] += len(allm)
        # the same drawing of the 0.1 header (SkyyMobs-0.1.jar's own CfgRows.header(), published under a test name) flags what Skyy saw
        oh = jcall(old_cls("CfgRows"), "header")
        orows = [[str(x) for x in r] for r in oh[7]]
        dflt = dict((r[0], r[4]) for r in orows)

        @JImplements("java.util.function.Function")
        class OldFn(object):
            @JOverride
            def apply(self, a):
                if a is not None and len(a) >= 2 and str(a[0]) == "get":
                    return JStr(dflt.get(str(a[1]), ""))
                if a is not None and len(a) >= 2 and str(a[0]) == "keys":
                    res = JArray(JObject)(3)
                    res[0], res[1], res[2] = JArray(JStr)(0), JArray(JStr)(0), JArray(JStr)(0)
                    return res
                return None
        br_ = Lvl.bridge()
        br_.put("config:def:SkyyMobsOld", oh)
        br_.put("config:fn:SkyyMobsOld", OldFn())
        try:
            oallm, otabs, ochoices = draw("SkyyMobsOld", AP.hdr("SkyyMobsOld"), orows)
            obad = problems(oallm, otabs, ochoices, orows)
        finally:
            br_.remove("config:def:SkyyMobsOld")
            br_.remove("config:fn:SkyyMobsOld")
        what_bad = sorted(set(re.sub(r" #SkyyAdmCh0x\d", "", b_.split(":")[0]) for b_ in obad))
        check(any("Who gets levels" in b_ and "['Who gets le']" in b_ for b_ in obad), "V. the 0.1 tab is drawn 'Who gets le' (SkyyMenu clips a tab at 14 characters and its inline filter drops the dots - Skyy's screenshot): %s" % obad[:4])
        check(any("'Easy 3  / 1 5'" in b_ for b_ in obad) and any("'Normal 4  / 2'" in b_ for b_ in obad)
              and any("choices of strength.difficulty" in b_ for b_ in obad), "V. the 0.1 Easy / Normal choices are too wide for their 90 px buttons and the choice "
              "texts lose their %% and . (Skyy's screenshot): %s" % obad[:6])
        check(len(obad) == 4, "V. ... and nothing else of the 0.1 page is flagged (tab, Easy, Normal, the changed choice texts): %s" % obad)
        print("V. Server Setup fit through SkyyMenu 0.3.5's AdminPage: %d texts (%d buttons, %d names, %d help lines) fit with %d px to spare; "
              "tightest: %s; the 0.1 header is flagged for: %s" % (len(allm), n_btn, len(names), len(helps), FIT_PAD,
                                                                   ", ".join("%r %.1f/%d" % (m_[2], m_[3], m_[4]) for m_ in tight), what_bad))
        print("   labels before -> after (as SkyyMenu draws them): tab %r -> %r; Difficulty %s -> %s (numbers now in the help line)" % (
            otabs[0][1][0], tabs[0][1][0], ochoices.get("strength.difficulty"), choices.get("strength.difficulty")))

    def section_o(hdr):
        """O (0.1.4): SkyyMobs-0.1.3.jar's own published header vs 0.1.4 - every 0.1.3 row kept (key, label, category, type, default, range,
        choices, unit, flags) with only five help texts reworded (spec 6.1 'help only'), + the 18 new rows of spec 6.1, + the tabs Level curve /
        Level gap; in Per level shape both jars' level multipliers, health amounts AND hardRef's line equal everywhere (Skyy's Custom 20% / 8%,
        caps 20 / 6 included) - Per level = 0.1.3 bit for bit"""
        oh = jcall(pin_cls("CfgRows"), "header")
        check(str(oh[3]) == PINVER and str(hdr[3]) == VERSION, "O. the 0.1.3 header is 0.1.3's (%s), the new one %s" % (oh[3], hdr[3]))
        orows = dict((str(r[0]), [str(x) for x in r]) for r in oh[7])
        nrows = [[str(x) for x in r] for r in hdr[7]]
        nmap = dict((r[0], r) for r in nrows)
        HELP_ONLY = {"strength.difficulty", "strength.hp", "strength.dmg", "strength.hpCap", "strength.dmgCap"}
        diff_ = []
        for k_, r_ in orows.items():
            n_ = nmap.get(k_)
            if n_ is None:
                diff_.append((k_, "missing"))
            elif k_ in HELP_ONLY:
                if n_[:10] != r_[:10] or n_[10] == r_[10]:
                    diff_.append((k_, "help-only row changed elsewhere"))
            elif n_ != r_:
                diff_.append((k_, [i for i in range(11) if n_[i] != r_[i]]))
        check(len(orows) == 26 and not diff_, "O. the 26 rows of 0.1.3 are kept element by element (5 help texts reworded only): %s" % diff_[:5])
        new_keys = [r[0] for r in nrows if r[0] not in orows]
        want_new = (["scale.role", "strength.shape", "strength.dmgFloor", "strength.hitCap"]
                    + ["curve.%s.%s" % (k_, d_) for k_ in ("hp", "dmg") for d_ in ("easy", "normal", "hard", "custom")]
                    + ["part.gap", "gap.free", "gap.dealtStep", "gap.dealtMin", "gap.takenStep", "gap.takenMax"])
        check(new_keys == want_new, "O. exactly the 18 new rows of spec 6.1, in display order: %s" % new_keys)
        check(len(oh) == len(hdr) and all(str(oh[k]) == str(hdr[k]) for k in (0, 1, 2, 4, 8, 9))
              and [str(x) for x in hdr[5]] == ["levels", "strength", "curve", "gap", "bands", "plate"]
              and [str(x) for x in hdr[6]] == ["Which mobs", "Strength", "Level curve", "Level gap", "Level bands", "Nameplate"]
              and [str(x) for x in oh[5]] == ["levels", "strength", "bands", "plate"],
              "O. contract, mod, title, node, files, note unchanged; tabs = 0.1.3's + Level curve / Level gap")
        PCfg = pin_cls("MobCfg")
        JDoubleC = JClass("java.lang.Double")
        bad_, n_ = [], 0
        SETS = [(d, 4.0, 2.0, 6.0, 3.5) for d in ("easy", "normal", "hard", "custom")] + [("custom", 20.0, 8.0, 20.0, 6.0)]
        Cfg0.SHAPE = "linear"
        for floor_ in (0, FLOOR, 80):
            for d, hp_, dm_, hc_, dc_ in SETS:
                Cfg.HP_FLOOR, Cfg.DIFFICULTY, Cfg.HP_PCT, Cfg.DMG_PCT, Cfg.HP_CAP, Cfg.DMG_CAP = floor_, d, hp_, dm_, hc_, dc_
                Cfg.derive(None)
                for f_, v_ in (("HP_FLOOR", Integer.valueOf(floor_)), ("DIFFICULTY", JStr(d)), ("HP_PCT", JDoubleC.valueOf(hp_)),
                               ("DMG_PCT", JDoubleC.valueOf(dm_)), ("HP_CAP", JDoubleC.valueOf(hc_)), ("DMG_CAP", JDoubleC.valueOf(dc_))):
                    PCfg.getField(f_).set(None, v_)
                jcall(PCfg, "derive", (JStr.class_, None))
                for L in range(0, 151):
                    if float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L)))) != float(Cfg.hpMult(L)) or \
                            float(jcall(PCfg, "dmgMult", (Integer.TYPE, Integer.valueOf(L)))) != float(Cfg.dmgMult(L)):
                        bad_.append((floor_, d, hp_, L, "mult"))
                    for base in (10.0, 36.0, 49.99, 74.0, 200.0, 226.0, -1.0):
                        a13 = float(jcall(PCfg, "hpAmount", (Integer.TYPE, Integer.valueOf(L)), (JDoubleC.TYPE, JDoubleC.valueOf(base))))
                        if a13 != float(Cfg.hpAmount(L, base)) or a13 != float(Cfg.hpAmount(L, base, 1.0)):
                            bad_.append((floor_, d, hp_, L, base))
                        n_ += 1
                    # hardRef in Per level = 0.1.3's own Hard line with these caps (kill XP share)
                    if d == "hard" and float(Cfg.hardRef(L)) != float(Cfg.hpMult(L)):
                        bad_.append((floor_, d, L, "hardRef"))
        check(not bad_, "O. Per level shape: 0.1.3's own hpMult / dmgMult / hpAmount = 0.1.4's (3 floors x 5 strengths x Lv 0-150 x 7 bases, %d amounts; "
              "hpAmount with role factor 1 the same; hardRef = Hard's own line): %s" % (n_, bad_[:5]))
        jcall(PCfg, "useDefaults")
        Cfg.useDefaults()
        print("O. 0.1.3 header vs 0.1.4: 26 rows kept (5 help texts reworded), 18 new rows, 2 new tabs; Per level shape: %d health amounts + every "
              "multiplier of both jars equal" % n_)


    def start_like_setup(base):
        """what SkyyMobsPlugin.setup() does with the files, in its order: MobMig.run(dir), MobCfg.load(), CfgPub.start(mods) -> the update answer"""
        home = os.path.join(base, "Skyy_SkyyMobs")
        Cfg.DIR = Paths.get(home)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = Paths.get(os.path.join(home, "bands.properties"))
        check(int(LogC.snap().size()) == 0, "(no change-log line is still queued from an earlier start)")
        mg_ = str(Mig.run(Cfg.DIR))
        Cfg.load()
        Pub.start(Paths.get(base), None)
        return mg_

    def stop_kit():
        Pub.flush()
        time.sleep(0.7)
        Pub.flush()
        time.sleep(0.3)
        Pub.shutdown()

    def kit_op(*a):
        f_ = Lvl.bridge().get("config:fn:SkyyMobs")
        arr = JArray(JObject)(len(a))
        for k, x in enumerate(a):
            arr[k] = x
        return f_.apply(arr)

    def logfields(text):
        return [ln.split("\t") for ln in text.split("\n") if ln.strip()]

    def section_u():
        """U: the one-time update on a scratch COPY of Skyy's live Skyy_SkyyMobs folder + synthetic files"""
        check(str(Mig.MG_MARK_ID) == "SkyyMobs 0.1.1 difficulty update" and str(Mig.MG_MARK_ID) in MARK and "=" not in MARK and MARK.startswith("# "),
              "U. the marker is a doc comment holding its id, no '=' (never a template line): %r" % MARK)
        check(str(Mig.DOC_OLD) == DOC01 and str(Mig.DOC_NEW) == DOC011, "U. the comment lines it swaps (0.1's exact line -> the 0.1.1 one)")
        check([str(x) for x in Mig.MG_KEY] == ["strength.hpCap", "strength.dmgCap"] and [str(x) for x in Mig.MG_OLD] == ["5", "3"]
              and [str(x) for x in Mig.MG_NEW] == ["6", "3.5"], "U. it moves only the two caps 5 / 3 -> 6 / 3.5 (never the difficulty word, never Custom)")
        dcfg = str(Cfg.DEF_CFG)
        check(MARK in dcfg and DOC011 in dcfg and DOC01 not in dcfg and Mig.mgUpdate(dcfg) is None,
              "U. the 0.1.1 default file carries the marker, so a fresh file is never updated")
        # ---- U1: Skyy's live folder AS IT IS NOW, copied (the source is only read). 0.1.1 is deployed: it ran its one-time update on
        # this file (22:41) and Skyy changed the difficulty in game since. Start twice on the copy = once; the floor needs no file line
        # (the code default 50 applies); the new row works on Skyy's real file
        PRE = [None]
        if not os.path.isdir(LIVE_DIR):
            print("   note: no live folder at %s - U1 skipped" % LIVE_DIR)
        else:
            base = os.path.join(SCRATCH, "live", "mods")
            home = os.path.join(base, "Skyy_SkyyMobs")
            shutil.rmtree(os.path.dirname(base), ignore_errors=True)
            shutil.copytree(LIVE_DIR, home)
            cfgp = os.path.join(home, "config.properties")
            hdir, logp = os.path.join(home, "config-history"), os.path.join(home, "config-changes.log")
            old = open(cfgp, "rb").read()
            otext = old.decode("latin-1")
            P0 = JClass("java.util.Properties")()
            P0.load(JClass("java.io.ByteArrayInputStream")(old))
            word = str(P0.getProperty("strength.difficulty", "normal")).strip().lower()
            capsl = (str(P0.getProperty("strength.hpCap")), str(P0.getProperty("strength.dmgCap")))
            migrated = MARK in otext
            print("   live copy: %d bytes, %s line endings, strength.difficulty=%s, caps %s / %s, 0.1.1 update marker %s, floor line %s, %d History "
                  "versions, %d change-log lines" % (len(old), "CRLF" if b"\r\n" in old else "LF", word, capsl[0], capsl[1],
                                                     "present" if migrated else "MISSING", "present" if "strength.floor" in otext else "none",
                                                     len([f_ for f_ in os.listdir(hdir) if f_.endswith(".bak")]) if os.path.isdir(hdir) else 0,
                                                     len(logfields(open(logp, "rb").read().decode("utf-8"))) if os.path.isfile(logp) else 0))
            # Skyy's real pre-update bytes (U1b below): the config-history copy the 0.1.1 update made of the file before it touched it
            idxp = os.path.join(hdir, "index.log")
            if os.path.isfile(idxp):
                for ln in open(idxp, "rb").read().decode("utf-8").split("\n"):
                    f_ = ln.split("\t")
                    if len(f_) >= 5 and f_[4] == "before the 0.1.1 difficulty update" and "#" in f_[0]:
                        fid, stamp = f_[0].split("#", 1)
                        bp = os.path.join(hdir, "%s.%s.bak" % (fid, stamp))
                        if os.path.isfile(bp):
                            PRE[0] = open(bp, "rb").read().decode("latin-1")
            log0 = open(logp, "rb").read().decode("utf-8") if os.path.isfile(logp) else ""
            before = snapdir(home)
            mg1 = start_like_setup(base)
            st = kit_op("status")
            lg0 = [str(x).split("\t") for x in kit_op("log", Integer.valueOf(200))]
            stop_kit()
            s1 = snapdir(home)
            if migrated:
                check(mg1 == "" and sorted(s1) == sorted(before) and all(s1[k] == before[k] for k in before),
                      "U1. start 1 on the live copy: the update answers nothing (marker), no file changes (bytes + times) - the floor needs no file line: %r" % mg1)
            else:
                check(mg1 != "" and MARK in open(cfgp, "rb").read().decode("latin-1"), "U1. start 1 on an un-updated live copy runs the 0.1.1 update: %r" % mg1)
            check(int(Cfg.HP_FLOOR) == FLOOR and "strength.floor" not in otext, "U1. memory: health floor %s HP (no line in Skyy's file -> the code default 50)" % Cfg.HP_FLOOR)
            lw = LADDER.get(word) if word in LADDER else None
            check(str(Cfg.DIFFICULTY) == word and (lw is None or abs(float(Cfg.HP_STEP) - lw[0] / 100) < 1e-12),
                  "U1. memory: difficulty %s = %s (Skyy's word kept), caps x%s / x%s" % (Cfg.DIFFICULTY, Cfg.difficultyText(), Cfg.HP_CAP, Cfg.DMG_CAP))
            check(st is not None and str(st[0]) == "ok", "U1. kit status ok on the live copy: %s" % (None if st is None else [str(x) for x in st]))
            log1 = open(logp, "rb").read().decode("utf-8") if os.path.isfile(logp) else ""
            check(log1 == log0 and not [f_ for f_ in lg0 if len(f_) > 7 and f_[4] == "strength.floor"],
                  "U1. no change-log line for the missing floor line (no clamped / invalid / file entry)")
            time.sleep(1.1)
            mg2 = start_like_setup(base)
            stop_kit()
            s2 = snapdir(home)
            check(mg2 == "" and sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "U1. start 2 = start 1: no byte and no time changed (%r)" % mg2)
            # the new row on Skyy's real file (the copy): Server Setup -> Mobs -> Strength -> Health floor 60
            t0 = open(cfgp, "rb").read().decode("latin-1")
            start_like_setup(base)
            r_ = kit_op("set", "strength.floor", "60", None, None, "yes", "console")
            stop_kit()
            t1 = open(cfgp, "rb").read().decode("latin-1")
            nl_ = logfields(open(logp, "rb").read().decode("utf-8")[len(log1):]) if os.path.isfile(logp) else []
            check(r_ is not None and str(r_[0]) == "ok" and int(Cfg.HP_FLOOR) == 60 and t1.startswith(t0.rstrip("\n")) and "\nstrength.floor=60\n" in t1
                  and len(t1.split("\n")) - len(t0.split("\n")) in (1, 2, 3),
                  "U1. Health floor 60 on Skyy's real file: every old line kept, the line appended (%s)" % [x for x in t1[len(t0.rstrip("\n")):].split("\n") if x])
            check([(f_[4], f_[5], f_[6], f_[7]) for f_ in nl_] == [("strength.floor", "50", "60", "ok")], "U1. one Undo-able change-log line: %s" % nl_)
            mg3 = start_like_setup(base)
            stop_kit()
            check(mg3 == "" and int(Cfg.HP_FLOOR) == 60, "U1. a third start reads the floor 60 from the file")
            print("U1. live copy (as it is now): start 1 + 2 change nothing, floor 50 by default, kit ok; the floor row writes / reads Skyy's file")

        # ---- U2: synthetic files (each in its own scratch folder, MobMig.run alone)
        def case(name, text, blocked=False):
            h_ = os.path.join(SCRATCH, "mig", name, "Skyy_SkyyMobs")
            shutil.rmtree(os.path.dirname(h_), ignore_errors=True)
            os.makedirs(h_)
            p_ = os.path.join(h_, "config.properties")
            if text is not None:
                open(p_, "wb").write(text.encode("latin-1"))
            if blocked:
                open(os.path.join(h_, "config-history"), "wb").write(b"a file where the folder should be")
            msg_ = str(Mig.run(Paths.get(h_)))
            nt = open(p_, "rb").read().decode("latin-1") if os.path.exists(p_) else None
            hd = os.path.join(h_, "config-history")
            hist_ = sorted(f_ for f_ in os.listdir(hd) if f_.endswith(".bak")) if os.path.isdir(hd) else []
            lp = os.path.join(h_, "config-changes.log")
            lines_ = logfields(open(lp, "rb").read().decode("utf-8")) if os.path.isfile(lp) else []
            hb = [open(os.path.join(hd, f_), "rb").read().decode("latin-1") for f_ in hist_]
            return msg_, nt, hist_, lines_, hb, sorted(os.listdir(h_))
        # 0.1.2: the live file is already updated (0.1.1 is deployed), so the synthetic cases start from Skyy's real PRE-update bytes (its
        # config-history copy) when U1 found them, else from 0.1's default text with Skyy's hard
        live = PRE[0]
        d01 = str(sfield(old_cls("MobCfg"), "DEF_CFG"))
        check(d01.startswith("# SkyyMobs 0.1 settings") and DOC01 in d01 and "strength.hpCap=5\n" in d01, "U2. (0.1's own default text, from SkyyMobs-0.1.jar)")
        # the untouched 0.1 default -> exactly the 0.1.1 default (but the version in the first comment line)
        msg_, nt, hist_, lines_, hb, _f = case("default01", d01)
        d011 = str(sfield(v011_cls("MobCfg"), "DEF_CFG"))
        want = d011.replace("# SkyyMobs %s settings" % V011, "# SkyyMobs %s settings" % OLDVER, 1)
        check(nt == want and nt == expect_mig(d01), "U2. 0.1's untouched default file -> exactly 0.1.1's default file (SkyyMobs-0.1.1.jar's own text, but "
              "its first line's version): the update 0.1.3 ships is 0.1.1's")
        M14_ = JClass(PKG + "MobMig14")
        blk_ = "\n".join([str(M14_.MARK)] + [str(t_).replace("{shape}", "curve") for t_ in M14_.G_TEXT])
        check(dcfg == d011.replace("# SkyyMobs %s settings" % V011, "# SkyyMobs %s settings" % VERSION, 1).replace(
            "\nstrength.dmgCap=3.5\n", "\nstrength.dmgCap=3.5\n" + FLOOR_LINES[0] + "\n" + FLOOR_LINES[1] + "\n", 1).replace(
            "\nlevels.max=100\n", "\nlevels.max=100\n" + str(M14_.ROLE_DOC) + "\n", 1).replace(
            "\nstrength.healOnLoad=false\n", "\nstrength.healOnLoad=false\n" + blk_ + "\n", 1)
            and d011.count("strength.dmgCap=3.5") == 1, "U2. the 0.1.4 default file = 0.1.1's + the two floor lines after the caps + the scale.role line "
            "after levels.max + the level curve block after healOnLoad (and its version)")
        check(len(hist_) == 1 and hb == [d01] and [(f_[4], f_[5], f_[6], f_[7]) for f_ in lines_] == [("strength.hpCap", "5", "6", "ok"), ("strength.dmgCap", "3", "3.5", "ok")]
              and "Difficulty kept (normal): Normal is now 6% health / 3% damage per level (= 0.1's Hard; 0.1's Normal is Easy now)" in msg_,
              "U2. ... History = the old bytes, 2 Undo lines, the INFO line names the new Normal: %r" % msg_)
        if PRE[0] is not None:
            # U1b: Skyy's real pre-update bytes -> exactly the 0.1.1 update (marker, comment line, caps), 2 Undo lines, History = the old bytes
            msg_, nt, hist_, lines_, hb, _f = case("livepre", PRE[0])
            check(nt == expect_mig(PRE[0]) and hb == [PRE[0]] and [(f_[4], f_[5], f_[6]) for f_ in lines_] == [("strength.hpCap", "5", "6"), ("strength.dmgCap", "3", "3.5")],
                  "U1b. Skyy's real pre-update file (config-history) -> exactly the 0.1.1 update, 2 Undo lines: %r" % msg_)
            print("U1b. Skyy's pre-update bytes (%d) -> the 0.1.1 update: %s" % (len(PRE[0]), msg_.replace("\n", " | ")))
        else:
            print("   note: no 'before the 0.1.1 difficulty update' copy in the live config-history - U1b skipped")
        base_t = live if live is not None else d01.replace("strength.difficulty=normal", "strength.difficulty=hard")
        # CRLF
        crlf = base_t.replace("\n", "\r\n")
        msg_, nt, hist_, lines_, hb, _f = case("crlf", crlf)
        check(nt == expect_mig(crlf) and nt.count("\r\n") == nt.count("\n") and len(lines_) == 2, "U2. a CRLF file keeps CRLF on every line, the marker line too")
        # an admin's caps are kept (and named), the marker + comment line still go in, nothing to undo
        t_ = base_t.replace("strength.hpCap=5", "strength.hpCap=4").replace("strength.dmgCap=3", "strength.dmgCap=2.5")
        msg_, nt, hist_, lines_, hb, _f = case("admincaps", t_)
        check(nt == expect_mig(t_, caps=False) and not lines_ and len(hist_) == 1 and "no cap line still had its 0.1 default" in msg_
              and "strength.hpCap=4 kept (an admin's value) - the 0.1.1 default is 6" in msg_ and "strength.dmgCap=2.5 kept (an admin's value) - the 0.1.1 default is 3.5" in msg_,
              "U2. admin caps 4 / 2.5 kept and named, no Undo line: %r" % msg_)
        # caps already at the new defaults: silent
        t_ = base_t.replace("strength.hpCap=5", "strength.hpCap=6").replace("strength.dmgCap=3", "strength.dmgCap=3.5")
        msg_, nt, hist_, lines_, hb, _f = case("capsnew", t_)
        check(nt == expect_mig(t_, caps=False) and not lines_ and "an admin's value" not in msg_, "U2. caps already 6 / 3.5: no kept note, no Undo line: %r" % msg_)
        # one moved, one kept
        t_ = base_t.replace("strength.dmgCap=3", "strength.dmgCap=2")
        msg_, nt, hist_, lines_, hb, _f = case("mixed", t_)
        check("strength.hpCap=6" in nt and "\nstrength.dmgCap=2\n" in nt and [(f_[4], f_[6]) for f_ in lines_] == [("strength.hpCap", "6")]
              and "strength.dmgCap=2 kept" in msg_, "U2. hpCap 5 moves, an admin's dmgCap 2 stays: %r" % msg_)
        # the marker already there (a 0.1.1 file): nothing at all
        msg_, nt, hist_, lines_, hb, files_ = case("marker", dcfg)
        check(msg_ == "" and nt == dcfg and files_ == ["config.properties"], "U2. a file with the marker is never touched (no History, no log): %s" % files_)
        # no file: nothing (MobCfg.load seeds the 0.1.1 default, which carries the marker)
        msg_, nt, hist_, lines_, hb, files_ = case("nofile", None)
        check(msg_ == "" and nt is None and files_ == [], "U2. no config.properties: nothing written by the update")
        # a continued entry is an admin's value (kept), a duplicate key moves only the lines holding the old text, other separators keep theirs
        t_ = base_t.replace("strength.hpCap=5", "strength.hpCap=\\\n  5")
        msg_, nt, hist_, lines_, hb, _f = case("continued", t_)
        check("strength.hpCap=\\\n  5" in nt and "strength.hpCap=5 kept" in msg_ and [(f_[4]) for f_ in lines_] == ["strength.dmgCap"],
              "U2. a continued strength.hpCap line is kept (noted): %r" % msg_)
        t_ = base_t.replace("strength.hpCap=5", "strength.hpCap=7\nstrength.hpCap=5")
        msg_, nt, hist_, lines_, hb, _f = case("duplicate", t_)
        check("\nstrength.hpCap=7\nstrength.hpCap=6\n" in nt and ("strength.hpCap", "5", "6") in [(f_[4], f_[5], f_[6]) for f_ in lines_],
              "U2. duplicate keys: the effective (last) line held 5 -> it moves, the earlier 7 stays")
        t_ = base_t.replace("strength.hpCap=5", "strength.hpCap = 5").replace("strength.dmgCap=3", "strength.dmgCap:3")
        msg_, nt, hist_, lines_, hb, _f = case("separators", t_)
        check("\nstrength.hpCap = 6\n" in nt and "\nstrength.dmgCap:3.5\n" in nt and len(lines_) == 2, "U2. other separators ( = and :) are kept, only the value text changes")
        # every difficulty word: kept, and the INFO line says what it means now
        for w_, want_ in (("easy", "Easy is now 4% health / 2% damage per level (= 0.1's Normal; 0.1's Easy was 3% / 1.5%)"),
                          ("normal", "Normal is now 6% health / 3% damage per level (= 0.1's Hard; 0.1's Normal is Easy now)"),
                          ("hard", "Hard is now 8% health / 4% damage per level (new; 0.1's Hard is Normal now)"),
                          ("custom", "Custom keeps your own strength.hp / strength.dmg values (unchanged)"),
                          (" HARD ", "Hard is now 8% health / 4% damage per level")):
            t_ = re.sub(r"(?m)^strength\.difficulty=.*$", "strength.difficulty=" + w_, base_t)
            msg_, nt, hist_, lines_, hb, _f = case("word-" + w_.strip().lower() + ("-odd" if w_ != w_.strip() else ""), t_)
            check(("strength.difficulty=" + w_) in nt and want_ in msg_, "U2. difficulty %r kept, INFO: %r" % (w_, msg_))
        t_ = re.sub(r"(?m)^strength\.difficulty=.*\n", "", base_t)
        msg_, nt, hist_, lines_, hb, _f = case("word-missing", t_)
        check("Difficulty kept (normal, the default): Normal is now 6%" in msg_ and "strength.difficulty" not in nt.replace(MARK, "").split("# Custom")[0].split("levels.max=100")[1].replace(DOC011, ""),
              "U2. no difficulty line: nothing added, the INFO line names the default: %r" % msg_)
        # config-history cannot be written: nothing is written at all (the next start tries again)
        msg_, nt, hist_, lines_, hb, files_ = case("blocked", base_t, blocked=True)
        check(msg_ == "" and nt == base_t and not lines_, "U2. config-history blocked (a file in its place): the file is used as it is, no log line")
        # no strength keys at all: the marker goes on top
        msg_, nt, hist_, lines_, hb, _f = case("nokeys", "part.levels=true\n")
        check(nt == MARK + "\npart.levels=true\n" and not lines_, "U2. a file without any strength key: the marker on line 0: %r" % nt)
        # no final newline + a non-ASCII byte in a comment: kept byte for byte
        t_ = "# caf\xe9 \xfc\n" + base_t.rstrip("\n")
        msg_, nt, hist_, lines_, hb, _f = case("bytes", t_)
        check(nt == expect_mig(t_) and not nt.endswith("\n") and nt.startswith("# caf\xe9 \xfc\n") and hb == [t_], "U2. a missing final newline and ISO-8859-1 bytes are kept")
        # mgUpdate is pure and never throws
        for t_ in ("", "\n", "\\", "strength.hpCap", "=5", "#" + MARK, "strength.hpCap=5\\", "\r\n\r\n", "strength.difficulty=hard\r"):
            try:
                Mig.mgUpdate(t_)
                ok_ = True
            except Exception:
                ok_ = False
            check(ok_, "U2. mgUpdate never throws (%r)" % t_)
        print("U2. synthetic files: 0.1 default -> the 0.1.1 default, CRLF, admin caps kept, caps already new, mixed, marker, no file, continued, "
              "duplicate, separators, 6 difficulty words, blocked History, no keys, bytes")

    def classfile(b):
        """(constant pool [(tag, bytes)], members {('f'|'m', name, desc): bytes}, head bytes) of a class file"""
        i = 8
        n_ = struct.unpack(">H", b[i:i + 2])[0]
        i += 2
        cp = [None]
        k = 1
        while k < n_:
            tag = b[i]
            i += 1
            if tag == 1:
                ln = struct.unpack(">H", b[i:i + 2])[0]
                cp.append((1, b[i + 2:i + 2 + ln]))
                i += 2 + ln
            elif tag in (3, 4):
                cp.append((tag, b[i:i + 4]))
                i += 4
            elif tag in (5, 6):
                cp.append((tag, b[i:i + 8]))
                cp.append(None)
                i += 8
                k += 1
            elif tag in (7, 8, 16, 19, 20):
                cp.append((tag, b[i:i + 2]))
                i += 2
            elif tag in (9, 10, 11, 12, 17, 18):
                cp.append((tag, b[i:i + 4]))
                i += 4
            elif tag == 15:
                cp.append((tag, b[i:i + 3]))
                i += 3
            else:
                raise ValueError("constant tag %d" % tag)
            k += 1
        rest = b[i:]
        j = 6
        ni = struct.unpack(">H", rest[j:j + 2])[0]
        j += 2 + 2 * ni
        u = lambda ix: cp[ix][1].decode("utf-8", "replace")
        members = {}
        for kind in ("f", "m"):
            cnt = struct.unpack(">H", rest[j:j + 2])[0]
            j += 2
            for _ in range(cnt):
                s0 = j
                _acc, ni_, di_, na = struct.unpack(">HHHH", rest[j:j + 8])
                j += 8
                for _a in range(na):
                    al = struct.unpack(">I", rest[j + 2:j + 6])[0]
                    j += 6 + al
                members[(kind, u(ni_), u(di_))] = rest[s0:j]
        return cp, members, rest[:6]

    def section_z():
        """Z (0.1.4): SkyyMobs-0.1.3.jar (the SET pin) vs 0.1.4, class by class: 5 classes added, the classes 0.1.4 does not touch are
        byte-identical, hpMult / dmgMult = 0.1.3's code with the Level curve branch in front (the Per level branch instruction for
        instruction), the members added per class; manifest.json Name / Version / Description"""
        za, zb = zipfile.ZipFile(PIN_JAR), zipfile.ZipFile(JAR)
        na_, nb_ = set(za.namelist()), set(zb.namelist())
        added_e = sorted(nb_ - na_)
        check(added_e == ["com/skyy/mobs/%s.class" % c for c in ("GapDamage", "GapDamageU", "MobGap", "MobInfoFn", "MobMig14")] and not (na_ - nb_),
              "Z. the 0.1.3 entries + exactly the 5 new classes: %s / removed %s" % (added_e, sorted(na_ - nb_)))
        diff = sorted(n_ for n_ in na_ & nb_ if za.read(n_) != zb.read(n_))
        SAME = ["com/skyy/mobs/%s.class" % c for c in ("CfgHist", "CfgLog", "CfgPub", "CfgSaveTask", "LevelDamageU", "LevelHook", "MobBands",
                                                         "MobGlob", "MobLevelFn", "MobLog", "MobMig", "MobPlateStep", "MobPruneTask", "MobRefresh",
                                                         "MobsCmd", "MobsInfoCmd", "MobsInspectCmd", "MobsPlateCmd", "MobsReloadCmd", "MobsSetCmd")]
        check(not [x for x in SAME if x in diff], "Z. the classes 0.1.4 does not touch are byte-identical to 0.1.3 (%d): changed anyway %s" % (
            len(SAME), [x for x in SAME if x in diff]))
        WANT_DIFF = sorted(["com/skyy/mobs/%s.class" % c for c in ("CfgFile", "CfgFn", "CfgRows", "LevelDamage", "MobCfg", "MobCmds", "MobHooks",
                                                                   "MobInfo", "MobLevel", "MobScanTask", "SkyyMobsPlugin")] + ["manifest.json"])
        check(diff == WANT_DIFF, "Z. exactly these entries changed: %s (want %s)" % (diff, WANT_DIFF))
        ma_ = json.loads(za.read("manifest.json").decode("utf-8"))
        mb_ = json.loads(zb.read("manifest.json").decode("utf-8"))
        md_ = sorted(k for k in set(ma_) | set(mb_) if ma_.get(k) != mb_.get(k))
        check(md_ == ["Description", "Name", "Version"] and mb_["Version"] == VERSION and "No dependencies (the Level curve is made for SkyyGear's gear curves" in mb_["Description"]
              and "Zero dependencies" not in mb_["Description"], "Z. manifest.json: Name / Version / Description (spec 6.4: 'No dependencies ...'): %s" % md_)
        IPz = JClass("javassist.bytecode.InstructionPrinter")

        def mtexts(jar, cname):
            pz = JClass("javassist.ClassPool")(False)
            pz.appendClassPath(jar)              # FIRST: the system path holds the 0.1.4 jar (classpath) and would win otherwise
            pz.appendClassPath(B.SERVER_JAR)
            pz.appendSystemPath()
            cc = pz.get(PKG + cname)
            beh = list(cc.getDeclaredBehaviors())
            if cc.getClassInitializer() is not None:
                beh.append(cc.getClassInitializer())
            out = {}
            for mth in beh:
                mi = mth.getMethodInfo()
                ca_ = mi.getCodeAttribute()
                lines = []
                if ca_ is not None:
                    it = ca_.iterator()
                    while it.hasNext():
                        pos = it.next()
                        s_ = re.sub(r"#\d+ = ", "", str(IPz.instructionString(it, pos, mi.getConstPool()))).replace("ldc_w", "ldc")
                        s_ = re.sub(r"^((?:if|goto|jsr)\w*) -?\d+$", r"\1", s_)
                        lines.append(s_)
                out[str(mi.getName()) + str(mi.getDescriptor())] = "\n".join(lines)
            return out
        # the Per level branch of hpMult / dmgMult = 0.1.3's whole method, instruction for instruction (after the new curve branch)
        ta, tb = mtexts(PIN_JAR, "MobCfg"), mtexts(JAR, "MobCfg")
        for m_ in ("hpMult(I)F", "dmgMult(I)F"):
            a_, b_ = ta[m_].split("\n"), tb[m_].split("\n")
            check(len(b_) > len(a_) and b_[-len(a_):] == a_ and "MobCfg.CURVE_ON" in tb[m_] and "MobCfg.curveMult" in tb[m_],
                  "Z. MobCfg.%s = the Level curve branch + 0.1.3's code unchanged (%d of %d instructions are 0.1.3's, in order)" % (m_, len(a_), len(b_)))
        tl3, tl4 = mtexts(PIN_JAR, "LevelDamage"), mtexts(JAR, "LevelDamage")
        h3, h4 = tl3["handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"], \
            tl4["handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"]
        k3 = h3.split("\n").index([x for x in h3.split("\n") if "MobCfg.dmgMult" in x][0])
        check(h4.split("\n")[:k3 + 2] == h3.split("\n")[:k3 + 2], "Z. LevelDamage.handle: 0.1.3's code up to the level multiplier unchanged (the attacker test, Lv <= 1 early return)")
        EXPECT_ADD = {
            "MobCfg": {"eval", "curveMult", "parsePts", "defPts", "pts", "curves", "ptsText", "curveOf", "diffIdx", "shapeFor", "roles", "roleIdx", "roleLevel", "roleX",
                       "roleKey", "whyNotRole", "hpAmount", "hardRef", "num2", "strengthText", "SHAPE", "CURVE_ON", "DMG_FLOOR", "HIT_CAP", "GAP_ON",
                       "GAP_FREE", "GAP_DSTEP", "GAP_DMIN", "GAP_TSTEP", "GAP_TMAX", "CURVES", "CURVE_DEF", "CURVE_KEY", "ROLES_TAB", "ROLE_SIG"},
            "MobLevel": {"setMult", "refreshOne"},
            "MobInfo": {"base", "rx"},
            "MobHooks": {"checkCurvePoint", "checkScaleRole"},
            "MobCmds": {"healthLine", "gapLine"},
            "MobScanTask": {"curveWarn"},
        }
        summary = []
        for cls_, want_add in sorted(EXPECT_ADD.items()):
            ca, ma, ha = classfile(za.read("com/skyy/mobs/%s.class" % cls_))
            cb, mb, hb_ = classfile(zb.read("com/skyy/mobs/%s.class" % cls_))
            added, removed = set(mb) - set(ma), set(ma) - set(mb)
            check(set(x[1] for x in added) == want_add and not removed, "Z. %s: members added %s, removed %s (want %s)" % (
                cls_, sorted(x[1] for x in added), sorted(removed), sorted(want_add)))
            summary.append("%s +%d" % (cls_, len(added)))
        print("Z. 0.1.3 -> 0.1.4: %d entries byte-identical, %d changed, 5 classes added; hpMult / dmgMult keep 0.1.3's code as the Per level branch; %s" % (
            len(na_ & nb_) - len(diff), len(diff), "; ".join(summary)))


    # ================================================================================================ 0.1.2 sections Q / FL / RA / IN / LV
    Mcmd = JClass(PKG + "MobCmds")
    RFc = JClass(PKG + "MobRefresh")
    JBool = JClass("java.lang.Boolean")
    ESMcls = JClass(ESMN).class_

    def jround(x):
        """Math.round of a float / double (ties up)"""
        return int(math.floor(float(x) + 0.5))

    def jf2(v):
        """MobCmds.f2: Math.round(v * 100.0f) / 100.0 printed by String.valueOf(double), a trailing .0 dropped"""
        s_ = repr(jround(f32(f32(v) * f32(100.0))) / 100.0)
        return s_[:-2] if s_.endswith(".0") else s_

    def py_amount(base, pct, L, cap=6.0, floor=FLOOR):
        """0.1.2's health amount typed here: the 0.1.1 level multiplier (float, capped) x max(1, floor / base), base rounded to 0.01 HP"""
        m_ = 1.0 if L <= 1 else f32(min(cap, max(1.0, 1.0 + (pct / 100.0) * (L - 1))))
        b_ = math.floor(base * 100.0 + 0.5) / 100.0
        ff = 1.0 if floor <= 0 or b_ <= 0 else max(1.0, floor / b_)
        return m_ if ff <= 1.0 else f32(m_ * ff)

    def spawn(base, L, uidx=1, role="Test_Role"):
        """a fresh stand-in mob of this base HP that spawns at level L through the jar's own apply (spawn = full health)"""
        m_ = fresh(float(base))
        u_ = UUID.fromString("00000000-0000-0000-0006-%012d" % uidx)
        Lvl.apply(None, None, None, None, m_, u_, None, "default", role, L, True, "biome", None)
        MOBS.remove(u_)
        return m_

    def amt(m_, L):
        mod_ = m_.mods.get("skyymobs_lv%d" % L)
        return None if mod_ is None else float(mod_.getAmount())

    def section_q():
        """Q: the floor numbers through the jar's own setMult (spawn = full) = the mirror typed here + the task's own numbers"""
        PCfg = v011_cls("MobCfg")
        table, n_ = [], 0
        for d in ("easy", "normal", "hard"):
            Cfg.DIFFICULTY = d
            Cfg.derive(None)
            PCfg.getField("DIFFICULTY").set(None, JStr(d))
            jcall(PCfg, "derive", (JStr.class_, None))
            pct = LADDER[d][0]
            for base in (36, 74, 200):
                for L in (1, 32, 60):
                    m_ = spawn(base, L)
                    a_ = amt(m_, L)
                    hp = float(m_.maxNow())
                    lm = 1.0 if L <= 1 else min(CAPS[0], 1.0 + pct / 100.0 * (L - 1))
                    hp_want = max(base, FLOOR) * lm
                    hp_old = base * float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L))))
                    check(a_ == py_amount(base, pct, L) and abs(hp - hp_want) < 0.01 and float(m_.val()) == hp,
                          "Q. %s base %d HP Lv %d: amount x%s (mirror x%s), %.2f / %.2f HP (want max(base, 50) x %.4f = %.2f, full)" % (
                              d, base, L, a_, py_amount(base, pct, L), float(m_.val()), hp, lm, hp_want))
                    if base >= FLOOR:
                        check(a_ == float(Cfg.hpMult(L)) and abs(hp - hp_old) < 0.01, "Q. %s base %d HP Lv %d is at or above the floor: exactly 0.1.1's x%s (%.2f HP)" % (
                            d, base, L, a_, hp))
                    table.append((base, L, d, hp_old, hp))
                    n_ += 1
        named = {(36, 32, "normal"): 143.0, (36, 32, "hard"): 174.0, (36, 1, "normal"): 50.0, (36, 60, "hard"): 286.0, (36, 32, "easy"): 112.0,
                 (74, 1, "hard"): 74.0, (74, 32, "normal"): 211.64, (200, 32, "normal"): 572.0}
        got = dict(((b_, l_, d_), h_) for b_, l_, d_, _o, h_ in table)
        for k, v in sorted(named.items()):
            check(abs(got[k] - v) < 0.01, "Q. task number: base %d HP Lv %d %s = %s HP: %.2f" % (k[0], k[1], k[2], v, got[k]))
        check(abs([o_ for b_, l_, d_, o_, h_ in table if (b_, l_, d_) == (36, 32, "normal")][0] - 102.96) < 0.01,
              "Q. ... and 0.1.1 gave that Lv 32 cobra 102.96 HP on Normal (the live log's ~100)")
        # the caps hold the LEVEL multiplier only; the floor goes on top (task: "Caps still apply to the level multiplier as today")
        Cfg.DIFFICULTY = "hard"
        Cfg.derive(None)
        for base, L, cap, hp_want in ((36, 100, 6.0, 300.0), (74, 100, 6.0, 444.0), (36, 60, 3.0, 150.0), (74, 60, 3.0, 222.0), (36, 32, 3.0, 150.0),
                                      (200, 60, 3.0, 600.0), (36, 64, 6.0, 300.0)):
            Cfg.HP_CAP = cap
            m_ = spawn(base, L)
            check(abs(float(m_.maxNow()) - hp_want) < 0.01 and amt(m_, L) == py_amount(base, 8.0, L, cap),
                  "Q. caps: Hard base %d HP Lv %d with the health cap x%s = %s HP (cap on the level multiplier, floor on top): %.2f" % (
                      base, L, cap, hp_want, float(m_.maxNow())))
        Cfg.useDefaults()
        # edge bases around the floor (Normal Lv 20 = x2.14): lifted up to 50 x 2.14 = 107, never lowered
        for base, hp_want in ((10, 107.0), (49.99, 107.0), (50, 107.0), (50.01, 50.01 * 2.14), (36.5, 107.0)):
            m_ = spawn(base, 20)
            check(abs(float(m_.maxNow()) - hp_want) < 0.01 and amt(m_, 20) == py_amount(base, 6.0, 20),
                  "Q. edge: base %s HP Lv 20 Normal = %.2f HP: %.2f" % (base, hp_want, float(m_.maxNow())))
        check(float(Cfg.floorFactor(-1.0)) == 1.0 and float(Cfg.floorFactor(0.0)) == 1.0 and float(Cfg.floorFactor(float("nan"))) == 1.0
              and float(Cfg.floorFactor(25.0)) == 2.0 and float(Cfg.floorFactor(80.0)) == 1.0, "Q. floorFactor: unknown / 0 / NaN base = 1, 25 HP = 2, 80 HP = 1")
        print("Q. floor numbers: %d mobs (bases 36 / 74 / 200 x Lv 1 / 32 / 60 x Easy / Normal / Hard) = mirror, %d task numbers, 7 cap cases, "
              "5 edge bases" % (n_, len(named)))
        print("   HP table 0.1.1 -> 0.1.3 (= 0.1.2, floor 50):")
        for base in (36, 74, 200):
            print("     base %3d HP: %s" % (base, "; ".join("Lv %d %s %.0f -> %.0f" % (l_, d_[0].upper(), o_, h_)
                                                         for b_, l_, d_, o_, h_ in sorted(table, key=lambda t_: (t_[1], ("easy", "normal", "hard").index(t_[2])))
                                                         if b_ == base)))

    def section_fl():
        """FL: floor 0 = 0.1.1 EXACTLY - hpAmount vs SkyyMobs-0.1.1.jar's own hpMult bit for bit; then both jars' setMult on stand-in maps"""
        PCfg, PLvl = v011_cls("MobCfg"), v011_cls("MobLevel")
        bad, n_ = [], 0
        for floor_ in (0, FLOOR):
            Cfg.HP_FLOOR = floor_
            for d in ("easy", "normal", "hard", "custom"):
                Cfg.DIFFICULTY = d
                Cfg.derive(None)
                PCfg.getField("DIFFICULTY").set(None, JStr(d))
                jcall(PCfg, "derive", (JStr.class_, None))
                bases = (10.0, 36.0, 49.5, 50.0, 74.0, 200.0, 1000.0) if floor_ == 0 else (50.0, 50.01, 61.0, 74.0, 200.0, 1000.0)
                for L in range(0, 151):
                    pm = float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L))))
                    for base in bases:
                        a_ = float(Cfg.hpAmount(L, base))
                        if a_ != pm:
                            bad.append((floor_, d, L, base, a_, pm))
                        n_ += 1
        check(not bad, "FL. hpAmount == SkyyMobs-0.1.1.jar's hpMult bit for bit (floor 0: every base; floor 50: every base at or above it): %s" % bad[:5])
        # the whole setMult of both jars on identical stand-in maps: spawn full, wound to 37%, change the difficulty, reload (keep share)
        n2, bad2 = 0, []
        Cfg.HP_FLOOR = 0
        for d, d2 in (("normal", "hard"), ("easy", "normal"), ("hard", "custom")):
            for base in (36.0, 74.0, 200.0):
                for L in (1, 2, 20, 32, 60, 100):
                    Cfg.DIFFICULTY = d
                    Cfg.derive(None)
                    PCfg.getField("DIFFICULTY").set(None, JStr(d))
                    jcall(PCfg, "derive", (JStr.class_, None))
                    ma_, mb_ = fresh(base), fresh(base)
                    jcall(PLvl, "setMult", (ESMcls, ma_), (Integer.TYPE, Integer.valueOf(0)), (Integer.TYPE, Integer.valueOf(L)), (JBool.TYPE, JBool.TRUE))
                    Lvl.setMult(mb_, 0, L, True)
                    s1_ = (amt(ma_, L), float(ma_.maxNow()), float(ma_.val()))
                    s2_ = (amt(mb_, L), float(mb_.maxNow()), float(mb_.val()))
                    ma_.setVal(JFloat(f32(s1_[1] * 0.37)))
                    mb_.setVal(JFloat(f32(s2_[1] * 0.37)))
                    Cfg.DIFFICULTY = d2
                    Cfg.derive(None)
                    PCfg.getField("DIFFICULTY").set(None, JStr(d2))
                    jcall(PCfg, "derive", (JStr.class_, None))
                    jcall(PLvl, "setMult", (ESMcls, ma_), (Integer.TYPE, Integer.valueOf(0)), (Integer.TYPE, Integer.valueOf(L)), (JBool.TYPE, JBool.FALSE))
                    Lvl.setMult(mb_, 0, L, False)
                    t1_ = (amt(ma_, L), float(ma_.maxNow()), float(ma_.val()), int(ma_.puts))
                    t2_ = (amt(mb_, L), float(mb_.maxNow()), float(mb_.val()), int(mb_.puts))
                    if s1_ != s2_ or t1_ != t2_:
                        bad2.append((d, d2, base, L, s1_, s2_, t1_, t2_))
                    n2 += 1
        check(not bad2, "FL. floor 0: 0.1.1's setMult (setStatValue / maximizeStatValue) and 0.1.3's (minStatValue / maxStatValue) on identical "
              "stand-in maps give identical amounts, max and health (spawn + "
              "a wounded reload after a difficulty change): %s" % bad2[:3])
        Cfg.useDefaults()
        print("FL. floor 0 = 0.1.1 exactly: %d amounts = SkyyMobs-0.1.1.jar's hpMult bit for bit (4 difficulties x Lv 0-150, floor 0 and floor 50 "
              "at or above it); %d spawn + reload runs of both jars' setMult identical" % (n_, n2))

    def section_ra():
        """RA: the re-apply on a chunk load (0.1.1's path: apply with the saved level, full = false) keeps the health PERCENT"""
        Cfg.useDefaults()
        u_ = UUID.fromString("00000000-0000-0000-0007-000000000001")
        # a mob 0.1.1 saved: a Lv 32 cobra (base 36) on Normal = modifier x2.86 = 102.96 HP, hurt to 50%
        m_ = fresh(36.0)
        m_.mods.put("skyymobs_lv32", SMOc(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(f32(2.86))))
        m_.setVal(JFloat(f32(float(m_.maxNow()) * 0.5)))
        check(abs(float(m_.maxNow()) - 102.96) < 0.01 and float(Lvl.baseOf(m_, 0)) == 36.0, "RA. (0.1.1's saved mob: 102.96 HP; baseOf reads 36 through its x2.86)")
        p0 = float(m_.val()) / float(m_.maxNow())
        saved = int(Lvl.savedLevel(m_, 0))
        Lvl.apply(None, None, None, None, m_, u_, None, "default", "Snake_Cobra", saved, False, "saved", None)
        check(saved == 32 and amt(m_, 32) == py_amount(36, 6.0, 32) and abs(float(m_.maxNow()) - 143.0) < 0.01,
              "RA. the chunk load re-applies x%s: 143 HP (0.1.1: 102.96): %s" % (amt(m_, 32), float(m_.maxNow())))
        check(abs(float(m_.val()) / float(m_.maxNow()) - p0) < 1e-6 and float(m_.val()) < float(m_.maxNow()) - 1.0,
              "RA. ... the health PERCENT is kept (%.1f%% -> %.1f / %.1f HP), not healed" % (p0 * 100, float(m_.val()), float(m_.maxNow())))
        puts = int(m_.puts)
        v0 = float(m_.val())
        Lvl.apply(None, None, None, None, m_, u_, None, "default", "Snake_Cobra", 32, False, "saved", None)
        check(int(m_.puts) == puts and float(m_.val()) == v0 and float(Lvl.baseOf(m_, 0)) == 36.0,
              "RA. a second load re-puts nothing and changes no health (the base reads 36 again: no churn)")
        Cfg.HP_FLOOR = 0
        Cfg.derive(None)
        Lvl.apply(None, None, None, None, m_, u_, None, "default", "Snake_Cobra", 32, False, "saved", None)
        check(amt(m_, 32) == f32(2.86) and abs(float(m_.val()) / float(m_.maxNow()) - p0) < 1e-6, "RA. floor 0 on the next load gives 0.1.1's x2.86 back, percent kept")
        Cfg.useDefaults()
        Cfg.HEAL_ON_LOAD = True
        Lvl.apply(None, None, None, None, m_, u_, None, "default", "Snake_Cobra", 32, False, "saved", None)
        check(float(m_.val()) == float(m_.maxNow()) and abs(float(m_.maxNow()) - 143.0) < 0.01, "RA. strength.healOnLoad ON still heals on a chunk load (0.1.1's option)")
        Cfg.useDefaults()
        # /mobs set (apply, full = false) keeps the percent too
        m_.setVal(JFloat(f32(float(m_.maxNow()) * 0.25)))
        Lvl.apply(None, None, None, None, m_, u_, None, "default", "Snake_Cobra", 40, False, "set", None)
        check(amt(m_, 40) == py_amount(36, 6.0, 40) and abs(float(m_.val()) / float(m_.maxNow()) - 0.25) < 1e-6 and amt(m_, 32) is None,
              "RA. /mobs set 40: one save slot, x%s, 25%% kept" % amt(m_, 40))
        MOBS.remove(u_)
        # baseOf: next to another mod's multiplicative modifier (the engine SUMS them - review F9) it still reads the mob's own base
        m2 = fresh(36.0)
        m2.mods.put("othermod_boost", SMOc(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(0.5)))
        check(float(Lvl.baseOf(m2, 0)) == 36.0 and abs(float(m2.maxNow()) - 18.0) < 1e-4, "RA. baseOf with another mod's x0.5 alone: 36 (max 18)")
        Lvl.setMult(m2, 0, 32, True)
        check(float(Lvl.baseOf(m2, 0)) == 36.0 and amt(m2, 32) == py_amount(36, 6.0, 32), "RA. ... and next to ours: still 36, our amount = the floor amount")
        m3 = fresh(36.0)
        m3.mods.put("skyymobs_lv5", SMOc(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(1.0)))
        m3.mods.put("othermod_cancel", SMOc(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(-1.0)))
        check(float(Lvl.baseOf(m3, 0)) == -1.0 and float(Lvl.baseOf(None, 0)) == -1.0 and float(Cfg.hpAmount(5, -1.0)) == float(Cfg.hpMult(5)),
              "RA. a 0 multiplicative sum or no stat map = unknown base (-1) -> no floor, the plain level multiplier")
        m4 = fresh(49.996)
        check(float(Lvl.baseOf(m4, 0)) == 50.0, "RA. the base is rounded to 0.01 HP (49.996 -> 50.0): %s" % Lvl.baseOf(m4, 0))
        check(bool(Lvl.same(JFloat(3.9722223), JFloat(3.9722226))) and not bool(Lvl.same(JFloat(2.86), JFloat(2.87))) and bool(Lvl.same(JFloat(1.0), JFloat(1.0000009))),
              "RA. same(): one part in a million")
        print("RA. chunk-load re-apply: 0.1.1's x2.86 / 103 HP mob at 50%% -> x%s / 143 HP at 50%%, no churn on the next load, floor 0 back to x2.86, "
              "healOnLoad heals on loads only, /mobs set keeps the percent; baseOf next to other mods / 0 sum / no map / rounding" % ("%.4f" % py_amount(36, 6.0, 32)))

    def section_in():
        """IN: /mobs inspect's health line (MobCmds.healthLine) - the multiplier ON the mob, the setting when it differs, base + floor"""
        def mirror(m_, L):
            """an independent mirror of healthLine for a stand-in map"""
            mod_ = m_.mods.get("skyymobs_lv%d" % L)
            applied = None if mod_ is None else float(mod_.getAmount())
            b_ = float(Lvl.baseOf(m_, 0))
            want = float(Cfg.hpAmount(L, b_))
            fl_ = int(Cfg.HP_FLOOR)
            ff = 1.0 if fl_ <= 0 or b_ <= 0 else max(1.0, fl_ / b_)
            ok = applied is not None and abs(applied - want) <= 1e-6 * max(1.0, abs(applied), abs(want))
            s_ = "=Health "
            if applied is None:
                s_ += "NOT applied (no skyymobs_lv%d modifier on the mob; setting x%s - it gets it on reload or /mobs set)" % (L, jf2(want))
            elif not ok:
                s_ += "applied x%s (setting x%s - updates on reload or /mobs set)" % (jf2(applied), jf2(want))
            else:
                s_ += "x" + jf2(applied)
            s_ += " (%d / %d HP)" % (jround(m_.val()), jround(m_.maxNow()))
            if ff > 1.0:
                if ok:
                    s_ += " = level x%s x floor %s: floor %d HP applied (base %d HP)" % (jf2(float(Cfg.hpMult(L))), jf2(ff), fl_, jround(b_))
                else:
                    s_ += "; the setting = level x%s x floor %s (floor %d HP, base %d HP)" % (jf2(float(Cfg.hpMult(L))), jf2(ff), fl_, jround(b_))
            elif fl_ <= 0:
                s_ += ", floor off"
            elif b_ > 0:
                s_ += ", base %d HP (at or above the %d HP floor)" % (jround(b_), fl_)
            s_ += ", damage x%s - %s, caps x%s / x%s" % (jf2(float(Cfg.dmgMult(L))), str(Cfg.difficultyText()), jf2(float(Cfg.HP_CAP)), jf2(float(Cfg.DMG_CAP)))
            return s_
        lines = []

        def line(m_, L, literal=None, what=""):
            got = Mcmd.healthLine(m_, 0, L)
            got = None if got is None else str(got)
            exp = mirror(m_, L)
            check(got == exp and (literal is None or got == literal), "IN. %s: %r (mirror %r%s)" % (what, got, exp, "" if literal is None else ", literal %r" % literal))
            lines.append(got)
            return got
        # Skyy's 0.1.1 test (floor off = the 0.1.1 numbers): Lv 20 Goblin Scrapper (base 38) made on Normal, then Server Setup -> Hard
        Cfg.useDefaults()
        Cfg.HP_FLOOR = 0
        Cfg.derive(None)
        m_ = spawn(38, 20)
        line(m_, 20, "=Health x2.14 (81 / 81 HP), floor off, damage x1.57 - Normal 6% / 3%, caps x6 / x3.5", "Skyy's Lv 20 Goblin Scrapper on Normal")
        Cfg.DIFFICULTY = "hard"
        Cfg.derive(None)         # ON_HEALTH is null here: nothing re-applies the loaded mob - the line must say so
        line(m_, 20, "=Health applied x2.14 (setting x2.52 - updates on reload or /mobs set) (81 / 81 HP), floor off, damage x1.76 - Hard 8% / 4%, caps x6 / x3.5",
             "... after Normal -> Hard: the multiplier ON the mob, the setting next to it (Skyy's report: inspect said x2.52 while the mob kept 81 HP)")
        Lvl.setMult(m_, 0, 20, False)
        line(m_, 20, "=Health x2.52 (96 / 96 HP), floor off, damage x1.76 - Hard 8% / 4%, caps x6 / x3.5", "... re-applied: x2.52, 96 HP, no note")
        # the floor (default 50)
        Cfg.useDefaults()
        m_ = spawn(36, 32)
        line(m_, 32, "=Health x3.97 (143 / 143 HP) = level x2.86 x floor 1.39: floor 50 HP applied (base 36 HP), damage x1.93 - Normal 6% / 3%, caps x6 / x3.5",
             "a Lv 32 cobra (base 36): floor 50 HP applied")
        m74 = spawn(74, 20)
        line(m74, 20, "=Health x2.14 (158 / 158 HP), base 74 HP (at or above the 50 HP floor), damage x1.57 - Normal 6% / 3%, caps x6 / x3.5",
             "a 74-HP mob: base above the floor")
        Cfg.HP_FLOOR = 80
        Cfg.derive(None)
        line(m74, 20, None, "the floor raised to 80 before the re-apply: applied x2.14, setting x2.31 = level x2.14 x floor 1.08")
        check("applied x2.14 (setting x2.31" in lines[-1] and "; the setting = level x2.14 x floor 1.08 (floor 80 HP, base 74 HP)" in lines[-1], "IN. (that line names both)")
        Cfg.useDefaults()
        bare = fresh(38.0)
        line(bare, 20, None, "a mob without our modifier")
        check(lines[-1].startswith("=Health NOT applied (no skyymobs_lv20 modifier on the mob; setting x2.82 - it gets it on reload or /mobs set) (38 / 38 HP); the setting = level x2.14 x floor 1.32"),
              "IN. (no modifier: NOT applied + the setting) %r" % lines[-1])
        check(Mcmd.healthLine(m_, 0, 0) is None and Mcmd.healthLine(None, 0, 0) is None, "IN. level 0 -> no health line")
        Cfg.useDefaults()
        print("IN. inspect health line: %d lines = mirror (+ literals), e.g. %r" % (len(lines), lines[1]))

    def section_lv():
        """LV: the live re-apply END TO END through the real kit, the REAL World.execute on stand-in worlds and the world-thread tasks"""
        AtomicBoolean = JClass("java.util.concurrent.atomic.AtomicBoolean")
        CLD = JClass("java.util.concurrent.ConcurrentLinkedDeque")
        IdM = JClass("java.util.IdentityHashMap")
        STN = "com.hypixel.hytale.component.Store"
        CP2 = JClass("javassist.ClassPool")(False)
        CP2.appendSystemPath()
        CP2.appendClassPath(B.SERVER_JAR)
        ss = CP2.makeClass("com.hypixel.hytale.component.SkyyMobsTestStore", CP2.get(STN))
        ss.addField(CtField.make("public java.util.IdentityHashMap comps;", ss))
        ss.addField(CtField.make("public int gets;", ss))
        ss.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                                      "com.hypixel.hytale.component.ComponentType t) { this.gets++; return this.comps == null ? null : "
                                      "(com.hypixel.hytale.component.Component) this.comps.get(r); }", ss))
        TS = ss.toClass(JClass(STN).class_)

        def getf(o, cls_name, name):
            c_ = JClass(cls_name).class_
            while c_ is not None:
                try:
                    f_ = c_.getDeclaredField(name)
                except Exception:
                    c_ = c_.getSuperclass()
                    continue
                f_.setAccessible(True)
                return f_.get(o)
            raise KeyError(name)
        ESMod = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
        UV = JClass("com.hypixel.hytale.server.core.universe.Universe")
        f_mod, f_uv = jfield(ESMod, "instance"), jfield(UV, "instance")
        old_mod, old_uv = f_mod.get(None), f_uv.get(None)
        lvbase = os.path.join(SCRATCH, "lv", "mods")
        shutil.rmtree(os.path.dirname(lvbase), ignore_errors=True)
        os.makedirs(os.path.join(lvbase, "Skyy_SkyyMobs"))
        # 0.1.4: the 0.1.2 / 0.1.3 live re-apply numbers are Per level shape (= 0.1.3); section CU runs the Level curve tables through the kit
        open(os.path.join(lvbase, "Skyy_SkyyMobs", "config.properties"), "wb").write(
            str(Cfg.DEF_CFG).replace("\nstrength.shape=curve\n", "\nstrength.shape=linear\n").encode("latin-1"))
        start_like_setup(lvbase)
        try:
            mod_ = U.allocateInstance(ESMod.class_)
            ctype = U.allocateInstance(JClass("com.hypixel.hytale.component.ComponentType").class_)
            jfield(ESMod, "entityStatMapComponentType").set(mod_, ctype)
            f_mod.set(None, mod_)
            check(int(SysJ.identityHashCode(ESMc.getComponentType())) == int(SysJ.identityHashCode(ctype)), "LV. (stand-in: EntityStatMap.getComponentType() answers)")
            uv = U.allocateInstance(UV.class_)
            wmap = JClass("java.util.LinkedHashMap")()
            jfield(UV, "unmodifiableWorlds").set(uv, wmap)
            f_uv.set(None, uv)
            W = {}

            def mkworld(name):
                w_ = U.allocateInstance(JClass(WN).class_)
                es_ = U.allocateInstance(JClass(ESN).class_)
                st_ = U.allocateInstance(TS)
                st_.comps = IdM()
                setfield(es_, ESN, "entitiesByUuid", HashMap())
                setfield(es_, ESN, "store", st_)
                setfield(w_, WN, "name", name)
                setfield(w_, WN, "entityStore", es_)
                setfield(w_, WN, "acceptingTasks", AtomicBoolean(True))
                setfield(w_, WN, "taskQueue", CLD())
                wmap.put(name, w_)
                W[name] = (w_, es_, st_)
                return w_
            for nm_ in ("lvA", "lvB", "lvC"):
                mkworld(nm_)
            check(len(Lvl.liveWorlds()) == 3, "LV. (stand-in: Universe.get().getWorlds() lists the three worlds)")
            SPEC = {}

            def mkmob(key, wname, idx, base, L, frac, ref="valid"):
                w_, es_, st_ = W[wname]
                m_ = fresh(float(base))
                u_ = UUID.fromString("00000000-0000-0000-0008-%012d" % idx)
                Lvl.apply(None, None, None, None, m_, u_, w_, wname, "Test_Role", L, True, "biome", None)
                m_.setVal(JFloat(f32(float(m_.maxNow()) * frac)))
                if ref != "gone":
                    r_ = U.allocateInstance(JClass(REFN).class_)
                    if ref == "invalid":
                        setfield(r_, REFN, "index", JInt(-2147483648))
                    getf(es_, ESN, "entitiesByUuid").put(u_, r_)
                    st_.comps.put(r_, m_)
                SPEC[key] = (m_, base, L, frac, ref == "valid" and frac > 0)
            mkmob("A1 cobra full", "lvA", 1, 36, 32, 1.0)
            mkmob("A2 cobra 50%", "lvA", 2, 36, 32, 0.5)
            mkmob("A3 200 HP 25%", "lvA", 3, 200, 32, 0.25)
            mkmob("A4 scrapper 0.05%", "lvA", 4, 38, 20, 0.0005)
            mkmob("A5 dead", "lvA", 5, 36, 20, 0.0)
            mkmob("A6 unloaded (invalid ref)", "lvA", 6, 74, 60, 0.6, "invalid")
            mkmob("A7 gone (no ref)", "lvA", 7, 36, 32, 0.5, "gone")
            mkmob("B1 74 HP 60%", "lvB", 8, 74, 60, 0.6)
            check(int(MOBS.size()) == 8, "LV. (8 levelled mobs in MOBS)")

            def snapm():
                return dict((k, (amt(v[0], v[2]), float(v[0].val()), float(v[0].maxNow()), int(v[0].puts))) for k, v in SPEC.items())

            def qsize(w):
                return int(getf(W[w][0], WN, "taskQueue").size())

            def drain(w):
                q_ = getf(W[w][0], WN, "taskQueue")
                k_ = 0
                while not q_.isEmpty():
                    q_.poll().run()
                    k_ += 1
                return k_

            def expect(tag, pct, floor_, cap=6.0, only=None, prev=None):
                """every live mob (in world `only` when given) = the mirror amount with its health percent kept; the rest untouched"""
                for k, (m_, base, L, frac, live) in sorted(SPEC.items()):
                    a_, v_, mx = amt(m_, L), float(m_.val()), float(m_.maxNow())
                    if live and (only is None or k.startswith(only)):
                        w_ = py_amount(base, pct, L, cap, floor_)
                        check(a_ == w_ and abs(v_ / mx - frac) < 1e-5 and v_ > 0.0,
                              "LV. %s: %s x%s (want x%s), %.4f / %.2f HP = %.5f (kept %.5f), alive" % (tag, k, a_, w_, v_, mx, v_ / mx, frac))
                    elif prev is not None:
                        check((a_, v_) == prev[k][:2], "LV. %s: %s not touched (%s -> %s)" % (tag, k, prev[k][:2], (a_, v_)))
            Cfg.ON_HEALTH = RFc(None)                          # what setup() does after MobCfg.load()
            check(str(Cfg.difficultyText()) == "Normal 6% / 3%" and int(Cfg.HP_FLOOR) == FLOOR, "LV. (start: Normal, floor 50)")
            expect("spawned", 6.0, FLOOR)

            def change(tag, args, worlds_q, runs_delta=1):
                r0 = int(RFc.RUNS.get())
                prev = snapm()
                r_ = kit_op(*args)
                check(r_ is not None and str(r_[0]) == "ok", "LV. %s: the kit answers ok: %s" % (tag, None if r_ is None else [str(x) for x in r_]))
                got = dict((w, qsize(w)) for w in ("lvA", "lvB", "lvC"))
                check(int(RFc.RUNS.get()) - r0 == runs_delta and got == worlds_q, "LV. %s: ON_HEALTH ran %d time(s), tasks queued %s (want %s)" % (
                    tag, int(RFc.RUNS.get()) - r0, got, worlds_q))
                now = snapm()
                check(now == prev, "LV. %s: nothing changes before the world threads run their tasks (no component touched on the setting thread)" % tag)
                return prev
            # 1) Server Setup -> Difficulty Normal -> Hard (Skyy's test): lvB's task first - only its mob changes - then lvA's
            prev = change("Normal -> Hard", ("set", "strength.difficulty", "hard", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            check(drain("lvB") == 1, "LV. (lvB ran its one task)")
            expect("Hard, lvB's thread only", 8.0, FLOOR, only="B")
            for k in SPEC:
                if k.startswith("A"):
                    check(snapm()[k][:2] == prev[k][:2], "LV. lvB's task left lvA's %s alone" % k)
            check(drain("lvA") == 1, "LV. (lvA ran its one task)")
            expect("Hard", 8.0, FLOOR, prev=prev)
            check(abs(float(SPEC["A1 cobra full"][0].maxNow()) - 174.0) < 0.01 and abs(float(SPEC["A2 cobra 50%"][0].val()) - 87.0) < 0.01,
                  "LV. the Lv 32 cobra is 174 / 174 HP on Hard at once; the hurt one 87 / 174 (50%%)")
            # 2) floor 50 -> 0: exactly 0.1.1's amounts; the 200-HP mob's modifier is not even re-put
            p3 = snapm()["A3 200 HP 25%"][3]
            prev = change("floor 0", ("set", "strength.floor", "0", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("floor 0", 8.0, 0, prev=prev)
            check(amt(SPEC["A1 cobra full"][0], 32) == float(Cfg.hpMult(32)) == f32(3.48) and snapm()["A3 200 HP 25%"][3] == p3,
                  "LV. floor 0 = 0.1.1's x3.48 on Hard Lv 32; the 200-HP mob (above any floor) was not re-put")
            # 3) floor 0 -> 80: the 74-HP mob is lifted too
            prev = change("floor 80", ("set", "strength.floor", "80", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("floor 80", 8.0, 80, prev=prev)
            # 4) the health cap (its row runs derive since 0.1.2)
            prev = change("health cap x3", ("set", "strength.hpCap", "3", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("cap x3", 8.0, 80, 3.0, prev=prev)
            # 5) Custom, then the Custom health %
            prev = change("Custom (4%)", ("set", "strength.difficulty", "custom", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("Custom 4%", 4.0, 80, 3.0, prev=prev)
            prev = change("Custom health 10%", ("set", "strength.hp", "10", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("Custom 10%", 10.0, 80, 3.0, prev=prev)
            # 6) damage only, the nameplate, healOnLoad: the health signature is the same -> no re-apply
            for tag, args in (("Custom damage 3%", ("set", "strength.dmg", "3", None, None, "yes", "console")),
                              ("plate format", ("set", "plate.format", "{name} [{level}]", None, None, "yes", "console")),
                              ("healOnLoad ON", ("set", "strength.healOnLoad", "true", None, None, "yes", "console")),
                              ("damage cap", ("set", "strength.dmgCap", "2", None, None, "yes", "console"))):
                change(tag, args, {"lvA": 0, "lvB": 0, "lvC": 0}, runs_delta=0)
            # 7) healOnLoad is ON now: the live re-apply still never heals (it is for chunk loads)
            prev = change("floor 60 with healOnLoad ON", ("set", "strength.floor", "60", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("floor 60, healOnLoad ON (never heals here)", 10.0, 60, 3.0, prev=prev)
            # 8) a hand edit + the reload op (Server Setup -> Reload / /mobs reload): the kit's reload routine -> derive -> re-apply
            settle()
            cfgp_ = os.path.join(lvbase, "Skyy_SkyyMobs", "config.properties")
            t_ = open(cfgp_, "rb").read().decode("latin-1")
            check("\nstrength.floor=60\n" in t_, "LV. (the file holds the floor 60 the kit wrote)")
            open(cfgp_, "wb").write(t_.replace("\nstrength.floor=60\n", "\nstrength.floor=70\n").encode("latin-1"))
            r0 = int(RFc.RUNS.get())
            prev = snapm()
            r_ = kit_op("reload", None, None, "console")
            for _i in range(60):
                if int(RFc.RUNS.get()) > r0 and qsize("lvA") and qsize("lvB"):
                    break
                time.sleep(0.1)
            check(r_ is not None and str(r_[0]) == "ok" and int(Cfg.HP_FLOOR) == 70 and int(RFc.RUNS.get()) == r0 + 1 and qsize("lvA") == 1 and qsize("lvB") == 1,
                  "LV. hand edit strength.floor=70 + reload: the reload routine re-applies (runs %d, queues %d / %d, floor %s)" % (
                      int(RFc.RUNS.get()) - r0, qsize("lvA"), qsize("lvB"), Cfg.HP_FLOOR))
            drain("lvA")
            drain("lvB")
            expect("hand edit + reload: floor 70", 10.0, 70, 3.0, prev=prev)
            # 9) a world that stopped taking tasks (World.execute throws): the other world still gets its task, the kit answers ok
            setfield(W["lvB"][0], WN, "acceptingTasks", AtomicBoolean(False))
            prev = change("floor 50, lvB not accepting tasks", ("set", "strength.floor", "50", None, None, "yes", "console"), {"lvA": 1, "lvB": 0, "lvC": 0})
            drain("lvA")
            expect("floor 50 (lvA)", 10.0, 50, 3.0, only="A")
            check(snapm()["B1 74 HP 60%"][:2] == prev["B1 74 HP 60%"][:2], "LV. lvB (not accepting tasks) kept its mob as it was - no error")
            setfield(W["lvB"][0], WN, "acceptingTasks", AtomicBoolean(True))
            prev = change("floor 52", ("set", "strength.floor", "52", None, None, "yes", "console"), {"lvA": 1, "lvB": 1, "lvC": 0})
            drain("lvA")
            drain("lvB")
            expect("floor 52 (lvB catches up)", 10.0, 52, 3.0, prev=prev)
            # 10) shutdown clears ON_HEALTH: a change re-applies nothing
            Cfg.ON_HEALTH = None
            change("after shutdown (ON_HEALTH null)", ("set", "strength.floor", "55", None, None, "yes", "console"), {"lvA": 0, "lvB": 0, "lvC": 0}, runs_delta=0)
            # 11) the dispatcher alone: no Universe / no levelled mob / no world -> nothing queued, never throws
            check(int(RFc.dispatch(wmap.values())) == 2 and drain("lvA") == 1 and drain("lvB") == 1, "LV. dispatch(worlds) queues one task per world with levelled mobs (2)")
            check(int(Lvl.refreshWorld(None)) == 0 and int(RFc.dispatch(None)) == 0, "LV. refreshWorld(null) / dispatch(null) do nothing")
            f_uv.set(None, old_uv)
            r0 = int(RFc.RUNS.get())
            RFc(None).run()
            check(int(RFc.RUNS.get()) == r0 + 1 and qsize("lvA") == 0 and qsize("lvB") == 0, "LV. MobRefresh(null) without a Universe (bare JVM) queues nothing, no error")
            MOBS.clear()
            check(int(RFc.dispatch(wmap.values())) == 0, "LV. no levelled mob loaded -> nothing queued")
            print("LV. live re-apply end to end: Difficulty, floor 0 / 80 / 60 / 70 / 52, health cap, Custom % each queued one task per world with "
                  "levelled mobs and re-applied every loaded mob on that world's thread (percent kept, tiny-HP alive, dead / unloaded / gone "
                  "untouched); damage / plate / healOnLoad / damage-cap changes re-applied nothing; hand edit + reload; a world not taking "
                  "tasks; ON_HEALTH null; the dispatcher alone")
        finally:
            f_mod.set(None, old_mod)
            f_uv.set(None, old_uv)
            Cfg.ON_HEALTH = None
            MOBS.clear()
            try:
                stop_kit()
            except Exception as ex:
                check(False, "LV. the kit did not stop: %s" % ex)

    # ================================================================================================ 0.1.3 section NQ (F1 of the 0.1.2 cross-check)
    def section_nq():
        """NQ: the network queue on REAL engine objects. All 12 vanilla stats (Assets.zip Server/Entity/Stats) through the real asset
        codec (Regenerating / *Effects left out: their condition and interaction types register with the stats module at server start,
        and neither takes part in a stat change) into the engine's IndexedLookupTableAssetMap, filled by its own putAll and reached the
        engine's way (EntityStatType.getAssetMap() -> AssetRegistry.getAssetStore - a stand-in store object holding it);
        DefaultEntityStatTypes.update() finds Health. A mob = a real EntityStatMap (update(): a real EntityStatValue per stat) + the
        NPC_Max modifier and full health (BalancingInitialisationSystem.onEntityAdd's recipe) + our spawn modifier (the jar's own
        setMult) + a wound; every tick ends with the real tracker update + clear. The change runs through the jar's own code (refreshOne
        = the live re-apply on the world thread, apply 'set' = /mobs set N, strip = /mobs set 0) and, on an identical map, through
        SkyyMobs-0.1.2.jar's; then: the server state, the queue (otherUpdates), the REAL EntityStatsSystems$EntityTrackerUpdate.tick on a
        stand-in ArchetypeChunk (player A already sees the mob, player B starts seeing it this tick) -> the REAL EntityViewer.queueUpdate
        -> the EntityUpdates packet as EntityTrackerSystems$SendPackets builds it, through the real wire format and back -> the REAL
        ClearChanges.tick; the self queue under the engine's death rule; a client mirror (the client code is not in the server jar)."""
        from jpype import JByte
        EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
        ILTc = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
        ARc = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
        DSTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
        DataC = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
        AEIc = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
        RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
        ESU = JClass("com.hypixel.hytale.protocol.EntityStatsUpdate")
        EUp = JClass("com.hypixel.hytale.protocol.EntityUpdate")
        EUs = JClass("com.hypixel.hytale.protocol.packets.entities.EntityUpdates")
        MSeg = JClass("java.lang.foreign.MemorySegment")
        ReflArray = JClass("java.lang.reflect.Array")
        JDoubleC = JClass("java.lang.Double")
        ESMod = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
        ETU = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$EntityTrackerUpdate")
        CLR = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$ClearChanges")
        VIS = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$Visible")
        EVW = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$EntityViewer")
        CTc = JClass("com.hypixel.hytale.component.ComponentType")
        REFc = JClass(REFN)
        RModn = JClass("java.lang.reflect.Modifier")
        PCfg, PLvl = prev_cls("MobCfg"), prev_cls("MobLevel")
        PMOBS = sfield(PLvl, "MOBS")
        azs = zipfile.ZipFile(AZ_PATH)
        STATS = sorted(n_.rsplit("/", 1)[1][:-5] for n_ in azs.namelist() if n_.startswith("Server/Entity/Stats/") and n_.endswith(".json"))
        raw = dict((nm, json.loads(azs.read("Server/Entity/Stats/%s.json" % nm).decode("utf-8-sig"))) for nm in STATS)
        hj = raw.get("Health", {})
        check(len(STATS) >= 4 and hj.get("Shared") is True and hj.get("Min") == 0 and hj.get("Max") == 100
              and not [k for k in hj if k.endswith("Effects")],
              "NQ. vanilla Health.json: Shared (its changes are queued for the players who see the mob), Min 0, Max 100, no min / max value "
              "effects (%d vanilla stats: %s)" % (len(STATS), ", ".join(STATS)))
        DST_INTS = [f_ for f_ in DSTc.class_.getDeclaredFields() if RModn.isStatic(f_.getModifiers()) and not RModn.isFinal(f_.getModifiers())
                    and str(f_.getType().getName()) == "int"]
        for f_ in DST_INTS:
            f_.setAccessible(True)
        old_dst = [(f_, int(f_.getInt(None))) for f_ in DST_INTS]
        f_store, f_mod = jfield(EST, "ASSET_STORE"), jfield(ESMod, "instance")
        smap = jfield(ARc, "storeMap").get(None)
        old_store, old_mod = f_store.get(None), f_mod.get(None)
        added = [False]
        try:
            @JImplements("java.util.function.IntFunction")
            class StatArray(object):
                @JOverride
                def apply(self, n):
                    return ReflArray.newInstance(EST.class_, int(n))
            amap = ILTc(StatArray())
            loaded = JClass("java.util.LinkedHashMap")()
            for nm in STATS:
                j_ = dict((k, v) for k, v in raw[nm].items() if k != "Regenerating" and not k.endswith("Effects"))
                loaded.put(JString(nm), EST.CODEC.decodeJsonAsset(RJR.fromJsonString(json.dumps(j_)), AEIc(DataC(EST.class_, JString(nm), None))))
            m_put = [x for x in ILTc.class_.getDeclaredMethods() if str(x.getName()) == "putAll" and len(x.getParameterTypes()) == 5][0]
            m_put.setAccessible(True)
            pa = JArray(JObject)(5)
            pa[0], pa[1], pa[2], pa[3], pa[4] = JString("Hytale:Hytale"), EST.CODEC, loaded, HashMap(), HashMap()
            m_put.invoke(amap, pa)
            ASN = "com.hypixel.hytale.assetstore.AssetStore"
            CPn = JClass("javassist.ClassPool")(False)
            CPn.appendSystemPath()
            CPn.appendClassPath(B.SERVER_JAR)
            TSC = CPn.makeClass("com.hypixel.hytale.assetstore.SkyyMobsTestAssetStore", CPn.get(ASN)).toClass(JClass(ASN).class_)
            store = U.allocateInstance(TSC)
            setfield(store, ASN, "tClass", EST.class_)
            setfield(store, ASN, "kClass", JClass("java.lang.String").class_)
            setfield(store, ASN, "assetMap", amap)
            check(smap.get(EST.class_) is None, "NQ. (no EntityStatType store was registered in this bare JVM)")
            f_store.set(None, None)
            smap.put(EST.class_, store)
            added[0] = True
            DSTc.update()
            hi = int(DSTc.getHealth())
            ht = EST.getAssetMap().getAsset(JInt(hi))
            check(EST.getAssetMap().equals(amap) and hi == int(amap.getIndex(JString("Health"))) and str(ht.getId()) == "Health" and bool(ht.isShared())
                  and float(ht.getMin()) == 0.0 and float(ht.getMax()) == 100.0 and ht.getMinValueEffects() is None and ht.getMaxValueEffects() is None,
                  "NQ. the engine's path EntityStatType.getAssetMap() -> AssetRegistry finds the %d vanilla stats; DefaultEntityStatTypes.update() -> "
                  "Health = index %d, Shared, 0-100, no min / max value effects (EntityStatsSystems$Changes runs no interaction for it)" % (len(STATS), hi))
            HMIN, HMAX = float(ht.getMin()), float(ht.getMax())
            mod_ = U.allocateInstance(ESMod.class_)              # EntityStatMap.getComponentType() (refreshWorld only, NQ-E) - as in LV
            jfield(ESMod, "entityStatMapComponentType").set(mod_, U.allocateInstance(CTc.class_))
            f_mod.set(None, mod_)
            B_I, B_T, B_F = Integer.valueOf(hi), JBool.TRUE, JBool.FALSE

            # ---- the tracker (real systems, stand-in archetype chunk: one mob; its Visible holds the players)
            ACN = "com.hypixel.hytale.component.ArchetypeChunk"
            CPc_ = JClass("javassist.ClassPool")(False)
            CPc_.appendSystemPath()
            CPc_.appendClassPath(B.SERVER_JAR)
            chx = CPc_.makeClass("com.hypixel.hytale.component.SkyyMobsNqChunk", CPc_.get(ACN))
            for f_ in ("public com.hypixel.hytale.component.Ref ref;", "public com.hypixel.hytale.component.Component vis;",
                       "public com.hypixel.hytale.component.Component map;", "public com.hypixel.hytale.component.ComponentType visType;",
                       "public com.hypixel.hytale.component.ComponentType mapType;"):
                chx.addField(CtField.make(f_, chx))
            chx.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return this.ref; }", chx))
            chx.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(int i, com.hypixel.hytale.component.ComponentType t) {"
                                           " if (t == this.visType) return this.vis; if (t == this.mapType) return this.map; return null; }", chx))
            CHK = chx.toClass(JClass(ACN).class_)
            t_map, t_vis = U.allocateInstance(CTc.class_), U.allocateInstance(CTc.class_)
            etu = U.allocateInstance(ETU.class_)
            jfield(ETU, "componentType").set(etu, t_map)
            jfield(ETU, "visibleComponentType").set(etu, t_vis)
            clr = U.allocateInstance(CLR.class_)
            jfield(CLR, "componentType").set(clr, t_map)
            f_out = jfield(ESMc, "isNetworkOutdated")
            WIRE = collections.Counter()

            def qlist(lst):
                out = []
                if lst is not None:
                    for u_ in lst:
                        md = u_.modifier
                        out.append((str(u_.op.name()), bool(u_.predictable), float(u_.value), None if u_.modifierKey is None else str(u_.modifierKey),
                                    None if md is None else (str(md.target.name()).upper(), str(md.calculationType.name()).upper(), float(md.amount))))
                return out

            def initof(u_):
                """an Init entry (createInitUpdate / the wire) -> {'op', 'value', 'mods': {key: (TARGET, CALC, amount)}}"""
                mods_ = {}
                if u_.modifiers is not None:
                    for k_ in u_.modifiers.keySet():
                        md = u_.modifiers.get(k_)
                        mods_[str(k_)] = (str(md.target.name()).upper(), str(md.calculationType.name()).upper(), float(md.amount))
                return {"op": str(u_.op.name()), "value": float(u_.value), "mods": mods_}

            def initstate(m_):
                """what a player who starts seeing the mob gets for Health (createInitUpdate(false), as queueUpdatesForNewlyVisible)"""
                return initof(m_.createInitUpdate(False).get(JInt(hi))[0])

            def unwire(viewer, mob):
                """the viewer's queued entity update as SendPackets sends it (EntityUpdates { EntityUpdate { networkId, removed,
                updates } }) through the real wire format and back -> (bytes, [Health entries of each EntityStatsUpdate])"""
                eu = viewer.updates.get(mob)
                if eu is None:
                    return 0, None
                pe = EUp()
                pe.networkId = 4242
                pe.removed = eu.toRemovedArray()
                pe.updates = eu.toUpdatesArray()
                arr = JArray(EUp)(1)
                arr[0] = pe
                pk = EUs(None, arr)
                buf = MSeg.ofArray(JArray(JByte)(1 << 16))
                n_ = int(pk.serialize(buf, 0))
                back = EUs.toObject(buf, 0)
                got = []
                if back.updates is None or len(back.updates) != 1 or int(back.updates[0].networkId) != 4242:
                    return n_, ["bad packet"]
                for cu in back.updates[0].updates:
                    if str(cu.getClass().getName()) == "com.hypixel.hytale.protocol.EntityStatsUpdate":
                        a_ = cu.entityStatUpdates.get(Integer.valueOf(hi))
                        got.append(list(a_) if a_ is not None else [])
                    else:
                        got.append("other %s" % cu.getClass().getName())
                return n_, got

            def tick(m_, seen=True, newly=True):
                """one tick's tracker update on the mob's real stat map, then the clear: the real EntityTrackerUpdate.tick sends player A
                (already sees the mob) the queue and player B (starts seeing it now) the Init; the real ClearChanges.tick empties the queue.
                -> {"A": (bytes, entries) or None, "B": (bytes, init) or None, "left": the queue after the clear, "outdated": the flag}"""
                mob = U.allocateInstance(REFc.class_)
                ra, rb = U.allocateInstance(REFc.class_), U.allocateInstance(REFc.class_)
                va, vb = EVW(64, None), EVW(64, None)
                vis = VIS()
                if seen:
                    va.visible.add(mob)
                    vis.visibleTo.put(ra, va)
                if newly:
                    vb.visible.add(mob)
                    vis.visibleTo.put(rb, vb)
                    vis.newlyVisibleTo.put(rb, vb)
                c_ = U.allocateInstance(CHK)
                c_.ref, c_.vis, c_.map, c_.visType, c_.mapType = mob, vis, m_, t_vis, t_map
                etu.tick(JFloat(0.05), 0, c_, None, None)
                clr.tick(JFloat(0.05), 0, c_, None, None)
                out = {"left": qlist(m_.otherUpdates.get(JInt(hi))), "outdated": bool(f_out.get(m_))}
                na, ga = unwire(va, mob)
                out["A"] = None if ga is None else (na, [qlist(x) if isinstance(x, list) else x for x in ga])
                nb, gb = unwire(vb, mob)
                if gb is None:
                    out["B"] = None
                else:
                    ib = [initof(x[0]) if isinstance(x, list) and len(x) == 1 else x for x in gb]
                    out["B"] = (nb, ib)
                WIRE["ticks"] += 1
                WIRE["bytes"] += na + nb
                return out

            def rcall(cls_, name, *vals):
                """a public static method of the isolated 0.1.2 class by name + arity (reflection; the JVM unboxes)"""
                ms_ = [mm for mm in cls_.getMethods() if str(mm.getName()) == name and len(mm.getParameterTypes()) == len(vals)]
                arr = JArray(JObject)(len(vals))
                for k_, x_ in enumerate(vals):
                    arr[k_] = x_
                return ms_[0].invoke(None, arr)

            def cfg(diff="normal", floor=FLOOR, cap=6.0, heal=False, hp=4.0, dmg=2.0, dcap=3.5):
                """the same settings in 0.1.3's MobCfg and 0.1.2's (each derives; ON_HEALTH is null in both: nothing re-applies by itself)"""
                Cfg.DIFFICULTY, Cfg.HP_FLOOR, Cfg.HP_CAP, Cfg.HEAL_ON_LOAD = diff, floor, float(cap), bool(heal)
                Cfg.HP_PCT, Cfg.DMG_PCT, Cfg.DMG_CAP = float(hp), float(dmg), float(dcap)
                Cfg.derive(None)
                PCfg.getField("DIFFICULTY").set(None, JStr(diff))
                PCfg.getField("HP_FLOOR").set(None, Integer.valueOf(floor))
                PCfg.getField("HP_CAP").set(None, JDoubleC.valueOf(float(cap)))
                PCfg.getField("HEAL_ON_LOAD").set(None, JBool.valueOf(bool(heal)))
                PCfg.getField("HP_PCT").set(None, JDoubleC.valueOf(float(hp)))
                PCfg.getField("DMG_PCT").set(None, JDoubleC.valueOf(float(dmg)))
                PCfg.getField("DMG_CAP").set(None, JDoubleC.valueOf(float(dcap)))
                jcall(PCfg, "derive", (JStr.class_, None))

            def spawnmob(base, L, old, frac=1.0, hp=None):
                """a real map: the NPC setup (NPC_Max = base - 100 additive, maximize), our spawn (full), one tick; then a wound, one tick"""
                m_ = ESMc()
                m_.update()
                m_.putModifier(hi, "NPC_Max", SMOc(MTG.MAX, CAL.ADDITIVE, JFloat(f32(base - HMAX))))
                m_.maximizeStatValue(hi)
                if old:
                    rcall(PLvl, "setMult", m_, B_I, Integer.valueOf(L), B_T)
                else:
                    Lvl.setMult(m_, hi, L, True)
                tick(m_)
                m_.setStatValue(hi, JFloat(f32(hp if hp is not None else float(m_.get(hi).getMax()) * frac)))
                tick(m_)
                return m_

            U13 = UUID.fromString("00000000-0000-0000-0013-000000000001")

            def change(kind, m_, L, old, L2=0):
                if kind == "refresh":
                    return bool(rcall(PLvl, "refreshOne", m_, B_I, Integer.valueOf(L))) if old else bool(Lvl.refreshOne(m_, hi, L))
                if kind == "set":
                    if old:
                        rcall(PLvl, "apply", None, None, None, None, m_, U13, None, JStr("default"), JStr("Test_Role"), Integer.valueOf(L2), B_F, JStr("set"), None)
                        PMOBS.remove(U13)
                    else:
                        Lvl.apply(None, None, None, None, m_, U13, None, "default", "Test_Role", L2, False, "set", None)
                        MOBS.remove(U13)
                    return True
                if old:
                    rcall(PLvl, "strip", None, None, None, m_, U13)
                else:
                    Lvl.strip(None, None, None, m_, U13)
                return True

            def snap(m_):
                v_ = m_.get(hi)
                mods_ = v_.getModifiers()
                ms_ = []
                if mods_ is not None:
                    for k_ in mods_.keySet():
                        x_ = mods_.get(k_)
                        ms_.append((str(k_), str(x_.getTarget().name()), str(x_.getCalculationType().name()), float(x_.getAmount())))
                return (float(v_.get()), float(v_.getMax()), tuple(sorted(ms_)))

            def queue(m_):
                return qlist(m_.otherUpdates.get(JInt(hi)))

            def selfq(m_):
                sl, sv = m_.selfUpdates.get(JInt(hi)), m_.selfStatValues.get(JInt(hi))
                out = []
                if sl is not None:
                    for j_ in range(int(sl.size())):
                        u_ = sl.get(j_)
                        out.append((str(u_.op.name()), float(u_.value), float(sv.getFloat(2 * j_)), float(sv.getFloat(2 * j_ + 1))))
                return out

            def deaths(m_):
                """EntityStatsSystems$Changes.tick's health rule (bytecode; release = 0.7 pre-release) on the self queue: an entry whose value is
                not above 0 and whose new health is at or below the minimum adds a DeathComponent (Damage COMMAND) when the mob has none yet"""
                mn_ = float(m_.get(hi).getMin())
                return [e for e in selfq(m_) if not (e[1] > 0.0) and e[3] <= mn_]

            def cstate(init, q):
                """the client's copy, mirrored: the Init state, then each entry in order with the server's own EntityStatValue rules (max =
                (stat max + the additive MAX amounts) x the SUM of the multiplicative ones, when there is one; min the same; the value is
                clamped to [min, max] after every change - what vanilla relies on when armor puts / removes a Health modifier with no value
                entry; Set / Min / Max / Maximize / Minimize / Add as EntityStatMap applies them). Returns the new state (an Init-like dict
                + its max), so it chains over ticks."""
                mods_ = dict(init["mods"])
                val = init["value"]

                def lims():
                    out = {}
                    for tgt, b_ in (("MIN", HMIN), ("MAX", HMAX)):
                        add_, mul_, ha, hm = 0.0, 0.0, False, False
                        for t_, c_, a_ in mods_.values():
                            if t_.upper() != tgt:
                                continue
                            if c_.upper() == "ADDITIVE":
                                ha, add_ = True, f32(add_ + a_)
                            else:
                                hm, mul_ = True, f32(mul_ + a_)
                        if ha:
                            b_ = f32(b_ + add_)
                        if hm:
                            b_ = f32(b_ * mul_)
                        out[tgt] = b_
                    return out["MIN"], out["MAX"]

                def clamp(x, lo_, hi_):
                    return lo_ if x < lo_ else (hi_ if x > hi_ else x)
                lo, mx = lims()
                val = clamp(val, lo, mx)
                for op, _p, v, k, md in q:
                    if op == "PutModifier":
                        mods_[k] = md
                        lo, mx = lims()
                        val = clamp(val, lo, mx)
                    elif op == "RemoveModifier":
                        mods_.pop(k, None)
                        lo, mx = lims()
                        val = clamp(val, lo, mx)
                    elif op == "Set":
                        val = clamp(v, lo, mx)
                    elif op == "Min":
                        val = clamp(min(val, v), lo, mx)
                    elif op == "Max":
                        val = clamp(max(val, v), lo, mx)
                    elif op == "Maximize":
                        val = mx
                    elif op == "Minimize":
                        val = lo
                    elif op == "Add":
                        val = clamp(f32(val + v), lo, mx)
                    else:
                        raise ValueError("unexpected op %s" % op)
                return {"op": "Init", "value": val, "mods": mods_, "max": mx}

            def client(init, q):
                """(health, max) of the client's copy after the entries q (cstate)"""
                s_ = cstate(init, q)
                return (s_["value"], s_["max"])

            def got_a(r_tk):
                """the Health entries player A got in one tick ([] when nothing was sent)"""
                ga = r_tk["A"]
                return ga[1][0] if ga is not None and ga[1] and isinstance(ga[1][0], list) else []

            def jshare(ov, om, nm_):
                """MobLevel.share in Java float maths"""
                if om <= 0.0:
                    return nm_
                s_ = f32(ov / om)
                s_ = 1.0 if s_ > 1.0 else (0.0 if s_ < 0.0 else s_)
                return f32(s_ * nm_)

            def ops(q):
                return [e[0] for e in q]

            def expect_mods(s0, s1):
                """the modifier entries a change must queue: a RemoveModifier for each of our keys gone, then a PutModifier for each key added
                or whose amount changed (removeOurs runs before putModifier)"""
                d0, d1 = dict((m_[0], m_) for m_ in s0[2]), dict((m_[0], m_) for m_ in s1[2])
                out = [("RemoveModifier", k_) for k_ in sorted(d0) if k_ not in d1]
                out += [("PutModifier", k_) for k_ in sorted(d1) if d0.get(k_) != d1[k_]]
                return out

            def invariants(tag, s0, s1, q, sq, tk, cl, dn, heal):
                """the 0.1.3 queue rules for one change; [] = all hold"""
                bad_ = []
                if [e for e in q if e[0] not in ("PutModifier", "RemoveModifier", "Min", "Max")]:
                    bad_.append("%s: a Set / Maximize / other entry in the queue %s" % (tag, q))
                modq = [(e[0], e[3]) for e in q if e[0] in ("PutModifier", "RemoveModifier")]
                if modq != expect_mods(s0, s1):
                    bad_.append("%s: modifier entries %s, want %s" % (tag, modq, expect_mods(s0, s1)))
                for e in q:
                    if e[0] == "PutModifier":
                        on = [m_ for m_ in s1[2] if m_[0] == e[3]]
                        if not on or e[4] != ("MAX", "MULTIPLICATIVE", on[0][3]) or e[1]:
                            bad_.append("%s: the PutModifier %s does not carry the server's modifier %s" % (tag, e, on))
                vq = [e for e in q if e[0] in ("Min", "Max")]
                after_mods = sq[-1 - len(vq)][3] if len(sq) > len(vq) else s0[0]
                if len(vq) > 1 or (vq and q[-1] is not vq[-1]):
                    bad_.append("%s: more than one value entry or not last: %s" % (tag, q))
                if vq and (vq[-1][2] != s1[0] or vq[-1][1]):
                    bad_.append("%s: the value entry %s does not carry the server's new health %r" % (tag, vq[-1], s1[0]))
                if bool(vq) != (s1[0] != after_mods):
                    bad_.append("%s: a value entry %s but the health after the modifier change %r -> %r" % (tag, vq, after_mods, s1[0]))
                ga = tk["A"]
                if (q and (ga is None or ga[1] != [q])) or (not q and ga is not None):
                    bad_.append("%s: player A (already sees the mob) got %s, the queue was %s" % (tag, ga, q))
                gb = tk["B"]
                if gb is None or len(gb[1]) != 1 or not isinstance(gb[1][0], dict) or gb[1][0]["op"] != "Init" or gb[1][0]["value"] != s1[0] \
                        or sorted((k_,) + v_ for k_, v_ in gb[1][0]["mods"].items()) != [tuple(x_) for x_ in s1[2]]:
                    bad_.append("%s: player B (starts seeing the mob) got %s, the server is %s" % (tag, gb, s1))
                elif client(gb[1][0], []) != (s1[0], s1[1]):
                    bad_.append("%s: player B's client mirror %s, the server %s" % (tag, client(gb[1][0], []), s1[:2]))
                if tk["left"] or tk["outdated"]:
                    bad_.append("%s: the queue was not emptied by ClearChanges: %s %s" % (tag, tk["left"], tk["outdated"]))
                if cl != (s1[0], s1[1]):
                    bad_.append("%s: player A's client mirror ends at %s, the server at %s" % (tag, cl, s1[:2]))
                if s0[0] > 0.0 and (not (s1[0] > 0.0) or dn):
                    bad_.append("%s: a living mob was killed (%r -> %r, deaths %s)" % (tag, s0[0], s1[0], dn))
                if heal:
                    if s1[0] != s1[1]:
                        bad_.append("%s: heal did not give full health %s" % (tag, s1[:2]))
                elif s0[0] > 0.0 and s1[2] != s0[2] and s1[0] != jshare(s0[0], s0[1], s1[1]):
                    bad_.append("%s: the health %r is not the share %r of the new max (percent %r -> %r)" % (
                        tag, s1[0], jshare(s0[0], s0[1], s1[1]), s0[0] / s0[1], s1[0] / s1[1]))
                elif s1[2] == s0[2] and s1[:2] != s0[:2]:
                    bad_.append("%s: nothing changed on the mob but its health moved %s -> %s" % (tag, s0[:2], s1[:2]))
                return bad_

            def run_pair(mn, mo, kind, L, L2=0, heal=False, extra=None):
                """one change on both jars' maps (+ an optional same-tick extra step on both), then one tick: everything the checks need"""
                r = {"s0": snap(mn), "s0o": snap(mo), "i0": initstate(mn), "i0o": initstate(mo)}
                r["rn"], r["ro"] = change(kind, mn, L, False, L2), change(kind, mo, L, True, L2)
                r["s1c"] = snap(mn)
                if extra is not None:
                    extra(mn)
                    extra(mo)
                r["q"], r["qo"] = queue(mn), queue(mo)
                r["sq"], r["sqo"] = selfq(mn), selfq(mo)
                r["dn"], r["do"] = deaths(mn), deaths(mo)
                r["s1"], r["s1o"] = snap(mn), snap(mo)
                r["tk"], r["tko"] = tick(mn), tick(mo)
                r["csn"], r["cso"] = cstate(r["i0"], got_a(r["tk"])), cstate(r["i0o"], got_a(r["tko"]))
                r["cl"], r["clo"] = (r["csn"]["value"], r["csn"]["max"]), (r["cso"]["value"], r["cso"]["max"])
                if extra is None:
                    r["bad"] = invariants(kind, r["s0"], r["s1"], r["q"], r["sq"], r["tk"], r["cl"], r["dn"], heal)
                else:
                    r["bad"] = []
                return r
            LINES = []

            def named(name, base, L, before, after, kind="refresh", frac=1.0, hp=None, L2=0, want=(), want_old=(), old_bug=True, maps=None):
                cfg(**before)
                mn, mo = maps if maps is not None else (spawnmob(base, L, False, frac, hp), spawnmob(base, L, True, frac, hp))
                cfg(**after)
                r = run_pair(mn, mo, kind, L, L2, after.get("heal", False))
                s0, s1 = r["s0"], r["s1"]
                check(r["s0"] == r["s0o"], "NQ. %s: (both jars made the same mob: %.4f / %.4f HP)" % (name, s0[0], s0[1]))
                check(r["s1"] == r["s1o"] and r["rn"] == r["ro"], "NQ. %s: the server ends bit for bit where 0.1.2 put it: %.4f / %.4f HP, %s (0.1.2 %.4f / %.4f)" % (
                    name, s1[0], s1[1], [(m_[0], m_[3]) for m_ in s1[2]], r["s1o"][0], r["s1o"][1]))
                check(ops(r["q"]) == list(want) and not r["bad"], "NQ. %s: 0.1.3 queues %s for the players who see the mob - %s%s" % (
                    name, list(want), r["q"], ("; " + "; ".join(r["bad"])) if r["bad"] else ""))
                check(ops(r["qo"]) == list(want_old), "NQ. %s: 0.1.2 queued %s: %s" % (name, list(want_old), r["qo"]))
                if old_bug:
                    check(r["clo"][1] != s1[1] and r["cl"] == (s1[0], s1[1]), "NQ. %s: F1 reproduced - the player who saw the mob keeps max %.4f with 0.1.2 "
                          "while the server has %.4f; with 0.1.3 the player gets %.4f / %.4f = the server" % (name, r["clo"][1], s1[1], r["cl"][0], r["cl"][1]))
                else:
                    check(r["clo"] == r["cl"] == (s1[0], s1[1]), "NQ. %s: no F1 here - both players' copies = the server %.4f / %.4f" % (name, s1[0], s1[1]))
                if s0[0] > 0.0 and s0[1] > 0.0:
                    LINES.append("%s: %.2f/%.2f -> %.2f/%.2f (%.4f%% -> %.4f%%) 0.1.3 %s / 0.1.2 %s" % (
                        name, s0[0], s0[1], s1[0], s1[1], 100 * s0[0] / s0[1], 100 * s1[0] / max(s1[1], 1e-9), "+".join(ops(r["q"])) or "-",
                        "+".join(ops(r["qo"])) or "-"))
                return r, mn, mo
            N_ = dict(diff="normal")
            H_ = dict(diff="hard")
            E_ = dict(diff="easy")
            SKYY = dict(diff="custom", hp=20.0, dmg=8.0, cap=20.0, dcap=6.0)      # Skyy's Server Setup 2026-10-03 21:40 (config-changes.log)
            # 0) the tracker itself: a fresh mob (one tick after the spawn) - player B gets the whole state, player A nothing
            cfg(**N_)
            m0 = spawnmob(36.0, 32, False)
            t0 = tick(m0)
            check(t0["A"] is None and t0["B"] is not None and t0["B"][1][0]["op"] == "Init" and t0["B"][1][0]["value"] == snap(m0)[0] and not t0["left"],
                  "NQ. the real tracker: nothing changed -> the player who sees the mob gets nothing, a new viewer gets the Init (%s)" % (t0["B"],))
            # 1) the live re-apply, max UP (Normal -> Hard): a Lv 32 cobra (base 36) at 50%
            r, mn, mo = named("max up (Normal -> Hard, Lv 32 cobra 50%)", 36.0, 32, N_, H_, frac=0.5, want=("PutModifier", "Max"), want_old=("Set",))
            check(abs(r["s1"][1] - 174.0) < 0.01 and abs(r["s1"][0] - 87.0) < 0.01 and r["q"][0][3] == "skyymobs_lv32", "NQ. (the cobra: 87 / 174 HP on Hard, our modifier key)")
            check(r["qo"][0][3] == "skyymobs_lv32" and r["qo"][0][4] is not None, "NQ. (0.1.2's Set entry still holds the modifier fields - the op was rewritten, "
                  "the old PutModifier entry: %s)" % (r["qo"][0],))
            # 2) max DOWN (Hard -> Easy) at 60%
            named("max down (Hard -> Easy, Lv 32 cobra 60%)", 36.0, 32, H_, E_, frac=0.6, want=("PutModifier", "Min"), want_old=("Set",))
            # 3) max down BELOW the old health (Hard -> Easy, a 200-HP mob Lv 60 at 95%): the put clamps the health, then the Min entry
            r, mn, mo = named("max down below the old health (Hard -> Easy, base 200 Lv 60 95%)", 200.0, 60, H_, E_, frac=0.95,
                              want=("PutModifier", "Min"), want_old=("Set",))
            check(r["sq"][0][2] > r["s1"][1] and r["sq"][0][3] == r["s1"][1], "NQ. (the self queue shows the clamp: %.2f -> %.2f at the put, then the share)" % (
                r["sq"][0][2], r["sq"][0][3]))
            # 4) unchanged: the same settings -> refreshOne puts nothing, queues nothing (both)
            r, mn, mo = named("unchanged (Hard -> Hard)", 36.0, 32, H_, H_, frac=0.5, want=(), want_old=(), old_bug=False)
            check(not r["rn"] and not r["ro"] and not r["q"] and r["s1"] == r["s0"], "NQ. (unchanged: refreshOne answers false, nothing queued, nothing moved)")
            # 5) the same max with a new key: /mobs set 100 -> 120 on Hard (both capped at x6, base 200, 50%): removeOurs takes the old key
            # off first, so the max drops to 200 for a moment and the health is clamped to it; the put brings the max back -> a Max entry
            # restores the share. 0.1.2's Set merged into the PutModifier: its player lost OUR modifier (max = the 200 base)
            r, mn, mo = named("same max, new key (/mobs set 100 -> 120, both x6)", 200.0, 100, H_, H_, kind="set", L2=120, frac=0.5,
                              want=("RemoveModifier", "PutModifier", "Max"), want_old=("RemoveModifier", "Set"))
            check(r["s0"][1] == r["s1"][1] == 1200.0 and r["sq"][0][3] == 200.0 and r["clo"] == (200.0, 200.0),
                  "NQ. (same max 1200: the removal clamps the health to the 200 base, the Max entry brings back 600; 0.1.2's player: %s)" % (r["clo"],))
            # 6) a 1-HP mob: max up, then max down (two ticks on the same maps): alive, percent exact
            cfg(**N_)
            m1n, m1o = spawnmob(38.0, 20, False, hp=1.0), spawnmob(38.0, 20, True, hp=1.0)
            check(snap(m1n)[0] == 1.0, "NQ. (the 1-HP mob has exactly 1 HP)")
            r, mn, mo = named("1-HP mob, max up (Normal -> Hard)", 38.0, 20, N_, H_, want=("PutModifier", "Max"), want_old=("Set",), maps=(m1n, m1o))
            r2, mn, mo = named("1-HP mob, then max down (Hard -> Easy)", 38.0, 20, H_, E_, want=("PutModifier", "Min"), want_old=("Set",), maps=(m1n, m1o))
            check(r["s1"][0] > 1.0 and 0.0 < r2["s1"][0] < 1.0 and not r["dn"] and not r2["dn"], "NQ. (1 HP -> %.4f -> %.4f HP: never killed, never healed beyond its share)" % (
                r["s1"][0], r2["s1"][0]))
            # 7) a 0-HP mob: the live re-apply never touches it (both)
            r, mn, mo = named("0-HP mob (refresh, Normal -> Hard)", 36.0, 32, N_, H_, hp=0.0, want=(), want_old=(), old_bug=False)
            check(not r["rn"] and r["s1"] == r["s0"] and r["s1"][0] == 0.0 and not r["dn"] and not r["q"],
                  "NQ. (0 HP: refreshOne answers false, the old modifier stays, nothing queued, no death entry - nothing healed or killed)")
            # 7b) /mobs set on a 0-HP mob: the same queue + self queue as 0.1.2 (an admin pointing at a dead mob; the engine's death system
            # skips a mob that already has its DeathComponent)
            cfg(**N_)
            m0n, m0o = spawnmob(36.0, 32, False, hp=0.0), spawnmob(36.0, 32, True, hp=0.0)
            r = run_pair(m0n, m0o, "set", 32, 40)
            check(r["q"] == r["qo"] and r["sq"] == r["sqo"] and r["s1"] == r["s1o"] and ops(r["q"]) == ["RemoveModifier", "PutModifier"] and r["s1"][0] == 0.0,
                  "NQ. 0-HP mob + /mobs set 40: the same queue, self queue and server state as 0.1.2 (%s), health stays 0" % ops(r["q"]))
            # 8) full health, max up: 0.1.2's Set was clamped to the client's OLD max (full bar, wrong max)
            named("full health, max up (Normal -> Hard, Lv 32 cobra)", 36.0, 32, N_, H_, frac=1.0, want=("PutModifier", "Max"), want_old=("Set",))
            # 9) full health, max down: the put's clamp lands exactly on the new max - no value entry in either version (the client clamps
            # on the modifier entry itself, as vanilla's armor modifiers need: StatModifiersManager puts / removes them with no value entry)
            named("full health, max down (Hard -> Easy)", 36.0, 32, H_, E_, frac=1.0, want=("PutModifier",), want_old=("PutModifier",), old_bug=False)
            # 10) /mobs set 40 on a Lv 32 cobra at 50% (healOnLoad off)
            named("/mobs set 32 -> 40 (50%)", 36.0, 32, N_, N_, kind="set", L2=40, frac=0.5, want=("RemoveModifier", "PutModifier", "Max"),
                  want_old=("RemoveModifier", "Set"))
            # 11) /mobs set 0 (strip) at 50%
            named("/mobs set 0 (strip, 50%)", 36.0, 32, N_, N_, kind="strip", frac=0.5, want=("RemoveModifier", "Min"), want_old=("Set",))
            # 12) /mobs set 40 with strength.healOnLoad on (the heal path: 0.1.2's maximizeStatValue)
            r, mn, mo = named("/mobs set 32 -> 40 with healOnLoad on (50%)", 36.0, 32, N_, dict(diff="normal", heal=True), kind="set", L2=40, frac=0.5,
                              want=("RemoveModifier", "PutModifier", "Max"), want_old=("RemoveModifier", "Maximize"))
            check(r["s1"][0] == r["s1"][1] and r["q"][-1][2] == r["s1"][1], "NQ. (heal: full health %.2f, the Max entry carries the new max)" % r["s1"][1])
            # 12b) the ONE place where the engine's own death rule (EntityStatsSystems$Changes, self queue) can see a difference: a mob whose
            # health is exactly 0 (normally it already has its DeathComponent - then the rule is skipped and nothing differs) given the heal
            # path (strength.healOnLoad ON - default off, off on Skyy's server - or a spawn) with the same key re-put: 0.1.2's Maximize merged
            # into the PutModifier entry and so hid the entry at 0 HP (the mob came back at full health); 0.1.3 heals it to the same full
            # health, but the PutModifier entry at 0 HP stays visible, so the engine's rule lets it die - as 0.1.2 already did whenever the
            # level changed (its RemoveModifier entry at 0 HP) or healOnLoad was off. Counted in the sweep as the only allowed difference.
            cfg(**N_)
            mzn, mzo = spawnmob(36.0, 32, False, hp=0.0), spawnmob(36.0, 32, True, hp=0.0)
            cfg(diff="hard", heal=True)
            r = r12 = run_pair(mzn, mzo, "set", 32, 32, True)
            check(r["s1"] == r["s1o"] and r["s1"][0] == r["s1"][1] > 0.0 and ops(r["q"]) == ["PutModifier", "Max"] and ops(r["qo"]) == ["Maximize"]
                  and [e[0] for e in r["dn"]] == ["PutModifier"] and not r["do"] and not r["bad"],
                  "NQ. 0-HP mob + the heal path, same key (healOnLoad ON): both servers end at full health %.1f; 0.1.3 queues %s (the player gets "
                  "the new max), 0.1.2 %s; the engine's death rule sees 0.1.3's PutModifier entry at 0 HP %s, 0.1.2's merge hid it %s" % (
                      r["s1"][0], ops(r["q"]), ops(r["qo"]), r["dn"], r["do"]))
            cfg(**N_)
            mzn, mzo = spawnmob(36.0, 32, False, hp=0.0), spawnmob(36.0, 32, True, hp=0.0)
            cfg(diff="normal", heal=True)
            r = run_pair(mzn, mzo, "set", 32, 40, True)
            check(r["s1"] == r["s1o"] and bool(r["dn"]) and bool(r["do"]) and not r["bad"],
                  "NQ. ... with a level change (/mobs set 32 -> 40) the rule sees a 0-HP entry in BOTH versions (0.1.2: %s, 0.1.3: %s)" % (r["do"], r["dn"]))
            LINES.append("0-HP mob + heal path, same key: both servers full; death rule 0.1.3 %s / 0.1.2 %s (the only difference, documented)" % (
                [e[0] for e in r12["dn"]], [e[0] for e in r12["do"]]))
            # 13) SKYY'S CASE (2026-10-03, TEST): Yetis loaded nearby, Server Setup -> Mobs -> Strength Hard -> Custom 20% / 8%, caps 20 / 6;
            # /mobs inspect then: "[Lv 32] Yeti - Health x7.2 (1627 / 1627 HP), base 226 HP, damage x3.48". Yeti.json MaxHealth 226.
            yt = [n_ for n_ in azs.namelist() if n_.endswith("/Yeti.json") and n_.startswith("Server/NPC/Roles/")]
            ym_ = re.search(r'"MaxHealth"\s*:\s*(\d+)', azs.read(yt[0]).decode("utf-8-sig")) if yt else None
            ymax = int(ym_.group(1)) if ym_ else -1
            check(ymax == 226, "NQ. (Assets.zip %s: MaxHealth %s - Skyy's 'base 226 HP')" % (yt[:1], ymax))
            r, ymn, ymo = named("SKYY'S CASE: a loaded Lv 32 Yeti seen by a player, Hard -> Custom 20% / 8% (caps 20 / 6)", 226.0, 32, H_, SKYY,
                                frac=1.0, want=("PutModifier", "Max"), want_old=("Set",))
            check(abs(r["s0"][1] - 786.48) < 0.01 and abs(r["s1"][1] - 1627.2) < 0.01 and r["s1"][0] == r["s1"][1] and r["q"][0][4][2] == f32(7.2)
                  and abs(r["clo"][1] - 786.48) < 0.01 and r["clo"][0] == r["clo"][1],
                  "NQ. Skyy's Yeti: Hard x3.48 = %.2f HP -> Custom x7.2 = %.2f HP on the server (inspect's 1627 / 1627); 0.1.2 left the player's "
                  "copy at %.2f / %.2f (a full bar of the OLD max), 0.1.3 sends PutModifier x%s + Max %.2f" % (
                      r["s0"][1], r["s1"][1], r["clo"][0], r["clo"][1], r["q"][0][4][2], r["q"][1][2]))
            # ... then the fight (Skyy: "the second one i tried took like 8 hits, but its hp bar looked empty long before it died"): 8 equal hits,
            # one per tick, through the real damage write (DamageSystems$ApplyDamage = subtractStatValue = an Add entry) and the real tracker
            hit = f32(r["s1"][1] / 8.0 + 0.01)
            csn_, cso_ = r["csn"], r["cso"]
            empty_old, empty_new, dead_at = None, None, None
            fight = []
            for k_ in range(1, 9):
                ymn.subtractStatValue(hi, JFloat(hit))
                ymo.subtractStatValue(hi, JFloat(hit))
                csn_, cso_ = cstate(csn_, got_a(tick(ymn))), cstate(cso_, got_a(tick(ymo)))
                sv_, svo_ = float(ymn.get(hi).get()), float(ymo.get(hi).get())
                fight.append("hit %d: server %.0f HP, 0.1.3 bar %.0f%% of %.0f, 0.1.2 bar %.0f%% of %.0f" % (
                    k_, sv_, 100 * csn_["value"] / csn_["max"], csn_["max"], 100 * cso_["value"] / cso_["max"], cso_["max"]))
                if cso_["value"] <= 0.0 and empty_old is None:
                    empty_old = k_
                if csn_["value"] <= 0.0 and empty_new is None:
                    empty_new = k_
                if sv_ <= 0.0 and dead_at is None:
                    dead_at = k_
                if (csn_["value"], csn_["max"]) != (sv_, float(ymn.get(hi).getMax())) or sv_ != svo_:
                    check(False, "NQ. Skyy's Yeti, hit %d: the 0.1.3 player's copy %s, the server %.4f (0.1.2's server %.4f)" % (k_, csn_, sv_, svo_))
            check(dead_at == 8 and empty_new == 8 and empty_old == 4, "NQ. Skyy's fight: 8 hits of %.1f kill the Yeti at hit %s; with 0.1.2 the player's bar is "
                  "empty at hit %s (the old max), with 0.1.3 at hit %s, the hit that kills it: %s" % (hit, dead_at, empty_old, empty_new, "; ".join(fight)))
            LINES.append("Skyy's fight (8 hits of %.1f): %s" % (hit, "; ".join(fight[2:5])))
            # the Lv 33 Yeti (Hard x3.56 = 804.56 HP, the '~805' of the report) and a hurt one (60%)
            r, mn, mo = named("Skyy's case, a Lv 33 Yeti (Hard x3.56 -> Custom x7.4)", 226.0, 33, H_, SKYY, frac=1.0, want=("PutModifier", "Max"), want_old=("Set",))
            check(abs(r["s0"][1] - 804.56) < 0.01 and abs(r["s1"][1] - 1672.4) < 0.01 and abs(r["clo"][1] - 804.56) < 0.01,
                  "NQ. (the Lv 33 Yeti: %.2f -> %.2f HP; 0.1.2's player kept %.2f)" % (r["s0"][1], r["s1"][1], r["clo"][1]))
            named("Skyy's case, a hurt Lv 32 Yeti (60%)", 226.0, 32, H_, SKYY, frac=0.6, want=("PutModifier", "Max"), want_old=("Set",))
            named("Skyy's case back (Custom 20% -> Hard, a Yeti at 30%)", 226.0, 32, SKYY, H_, frac=0.3, want=("PutModifier", "Min"), want_old=("Set",))
            # 14) a damage hit in the SAME tick after the change (DamageSystems$ApplyDamage = subtractStatValue = an Add entry): appended,
            # never merged into the modifier / value entries - the player still gets the new max, then the hit
            for tag_, before_, after_, fr_, want_ in (("max up + a hit", N_, H_, 0.5, ["PutModifier", "Max", "Add"]),
                                                      ("max down at full health + a hit", H_, E_, 1.0, ["PutModifier", "Add"])):
                cfg(**before_)
                mn, mo = spawnmob(36.0, 32, False, fr_), spawnmob(36.0, 32, True, fr_)
                cfg(**after_)
                r = run_pair(mn, mo, "refresh", 32, extra=lambda m_: m_.subtractStatValue(hi, JFloat(5.0)))
                ga = r["tk"]["A"]
                check(ops(r["q"]) == want_ and r["s1"] == r["s1o"] and ga is not None and ga[1] == [r["q"]] and r["cl"] == (r["s1"][0], r["s1"][1])
                      and abs(r["s1"][0] - (r["s1c"][0] - 5.0)) < 1e-3,
                      "NQ. %s in the same tick: 0.1.3 queues %s (the hit appended), the player's copy %s = the server %s; 0.1.2 %s" % (
                          tag_, ops(r["q"]), r["cl"], r["s1"][:2], ops(r["qo"])))
            # 15) the spawn path (setMult full): the same server state as 0.1.2 (no player sees a mob that is being added: the tracker sends
            # newly visible players the whole state, the queue only goes to players who already saw it)
            cfg(**N_)
            sp_bad = []
            for base in (10.0, 36.0, 74.0, 200.0, 226.0):
                for L in (1, 20, 32, 60):
                    a_, b_ = spawnmob(base, L, False), spawnmob(base, L, True)
                    if snap(a_) != snap(b_) or snap(a_)[0] != snap(a_)[1]:
                        sp_bad.append((base, L, snap(a_), snap(b_)))
            check(not sp_bad, "NQ. spawn (setMult full): 20 mobs, both jars give the same full-health state: %s" % sp_bad[:3])

            # ---- the seeded sweep: every path on both jars' real maps, the 0.1.3 queue rules on each
            rnd = random.Random(20261003)
            BASES = (10.0, 36.0, 38.0, 49.99, 50.0, 74.0, 200.0, 226.0, 1000.0)
            LVS = (1, 2, 20, 32, 33, 60, 100)
            FRACS = (1.0, 0.999, 0.5, 0.37, 0.01, None, 0.0005, 0.0)       # None = exactly 1 HP
            CFGS = [dict(diff=d, floor=f, cap=c) for d in ("easy", "normal", "hard", "custom") for f in (0, FLOOR, 80) for c in (6.0, 3.0)]
            CFGS += [dict(SKYY), dict(SKYY, floor=0)]
            sw_bad, n_sw, n_f1, n_put, kinds, n_corner = [], 0, 0, 0, collections.Counter(), 0
            for i_ in range(SWEEP):
                base, L, fr, L2 = rnd.choice(BASES), rnd.choice(LVS), rnd.choice(FRACS), rnd.choice(LVS)
                c0, c1 = rnd.choice(CFGS), rnd.choice(CFGS)
                kind = rnd.choice(("refresh", "refresh", "refresh", "set", "strip", "heal"))
                cfg(**c0)
                mn, mo = spawnmob(base, L, False, 1.0 if fr is None else fr, 1.0 if fr is None else None), \
                    spawnmob(base, L, True, 1.0 if fr is None else fr, 1.0 if fr is None else None)
                c1_ = dict(c1)
                c1_["heal"] = kind == "heal"
                cfg(**c1_)
                r = run_pair(mn, mo, "set" if kind == "heal" else kind, L, L2, kind == "heal")
                tag = "#%d %s base %s Lv %d -> %d %s %s -> %s" % (i_, kind, base, L, L2, fr, c0, c1_)
                if r["s0"] != r["s0o"] or r["s1"] != r["s1o"] or r["rn"] != r["ro"]:
                    sw_bad.append("%s: the server differs from 0.1.2: %s / %s" % (tag, r["s1"], r["s1o"]))
                if bool(r["dn"]) != bool(r["do"]):
                    # the one documented corner (12b): the heal path on a mob at exactly 0 HP, the same key re-put (no RemoveModifier)
                    if kind == "heal" and r["s0"][0] <= 0.0 and r["dn"] and not r["do"] and ops(r["q"])[:1] == ["PutModifier"] \
                            and "RemoveModifier" not in ops(r["q"]) and r["s1"][0] == r["s1"][1]:
                        n_corner += 1
                    else:
                        sw_bad.append("%s: the death rule's outcome differs from 0.1.2: %s / %s" % (tag, r["dn"], r["do"]))
                sw_bad += [tag + " " + x for x in r["bad"]]
                if r["clo"] != (r["s1"][0], r["s1"][1]):
                    n_f1 += 1
                n_put += sum(1 for e in r["q"] if e[0] in ("PutModifier", "RemoveModifier"))
                kinds[kind] += 1
                n_sw += 1
            check(not sw_bad and n_sw == SWEEP, "NQ. sweep: %d changes on both jars' real maps - the server bit for bit = 0.1.2, every 0.1.3 queue keeps its "
                  "modifier entries next to at most one Min / Max entry (last), player A gets exactly the queue through the real tracker + wire, "
                  "player B the new state, both client copies = the server, percent exact, nothing healed or killed: %s" % (n_sw, sw_bad[:4]))
            check(n_f1 > 0, "NQ. sweep: 0.1.2's player copy missed the server's health / max in %d of %d changes (F1); 0.1.3's in 0" % (n_f1, n_sw))
            print("   sweep: the death rule's outcome = 0.1.2's in every change but %d of the documented corner (12b: heal path, 0 HP, same key)" % n_corner)
            OKS[0] += n_sw

            # ---- NQ-E: the live re-apply end to end on REAL maps: MobRefresh.dispatch -> the real World.execute -> the world's task (run here
            # as the world thread) -> refreshWorld -> EntityStore.getRefFromUUID / getStore -> Store.getComponent (a stand-in store holding the
            # real maps) -> refreshOne -> setMult -> writeValue -> one tick of the real tracker
            STN = "com.hypixel.hytale.component.Store"
            CP3 = JClass("javassist.ClassPool")(False)
            CP3.appendSystemPath()
            CP3.appendClassPath(B.SERVER_JAR)
            ss_ = CP3.makeClass("com.hypixel.hytale.component.SkyyMobsNqStore", CP3.get(STN))
            ss_.addField(CtField.make("public java.util.IdentityHashMap comps;", ss_))
            ss_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                                           "com.hypixel.hytale.component.ComponentType t) { return this.comps == null ? null : "
                                           "(com.hypixel.hytale.component.Component) this.comps.get(r); }", ss_))
            TSn = ss_.toClass(JClass(STN).class_)
            w_ = U.allocateInstance(JClass(WN).class_)
            es_ = U.allocateInstance(JClass(ESN).class_)
            st_ = U.allocateInstance(TSn)
            st_.comps = JClass("java.util.IdentityHashMap")()
            byu = HashMap()
            setfield(es_, ESN, "entitiesByUuid", byu)
            setfield(es_, ESN, "store", st_)
            setfield(w_, WN, "name", "nqWorld")
            setfield(w_, WN, "entityStore", es_)
            setfield(w_, WN, "acceptingTasks", JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
            tq = JClass("java.util.concurrent.ConcurrentLinkedDeque")()
            setfield(w_, WN, "taskQueue", tq)
            MOBS.clear()
            cfg(**H_)
            E2E = []
            for k_, (base, L, fr, hp) in enumerate(((226.0, 32, 1.0, None), (36.0, 32, 0.5, None), (200.0, 60, 0.9, None), (38.0, 20, 1.0, 1.0),
                                                    (36.0, 32, 1.0, 0.0), (74.0, 20, 1.0, None))):
                m_ = spawnmob(base, L, False, fr, hp)
                u_ = UUID.fromString("00000000-0000-0000-0013-%012d" % (100 + k_))
                Lvl.apply(None, None, None, None, m_, u_, w_, "nqWorld", "Test_Role", L, False, "saved", None)
                check(not queue(m_), "NQ-E. (the chunk-load style apply with the same settings changes nothing on mob %d)" % k_)
                tick(m_)
                r_ = U.allocateInstance(JClass(REFN).class_)
                byu.put(u_, r_)
                st_.comps.put(r_, m_)
                E2E.append((m_, snap(m_), initstate(m_)))
            cfg(**SKYY)
            lst_ = JClass("java.util.ArrayList")()
            lst_.add(w_)
            n_q = int(RFc.dispatch(lst_))
            check(n_q == 1 and int(tq.size()) == 1 and all(snap(m_) == s0 and not queue(m_) for m_, s0, _i in E2E),
                  "NQ-E. MobRefresh.dispatch queued ONE task on the world (World.execute); nothing touched before it runs")
            tq.poll().run()
            e_bad = []
            for k_, (m_, s0, i0) in enumerate(E2E):
                q_, sq_, dn_ = queue(m_), selfq(m_), deaths(m_)
                s1 = snap(m_)
                tk_ = tick(m_)
                cl = client(i0, got_a(tk_))
                b_ = invariants("NQ-E mob %d" % k_, s0, s1, q_, sq_, tk_, cl, dn_, False)
                want = [] if s0[0] == 0.0 else ["PutModifier", "Max"]
                if ops(q_) != want:
                    b_.append("mob %d: queue %s, want %s" % (k_, ops(q_), want))
                e_bad += b_
            check(not e_bad, "NQ-E. the world task re-applied the 6 real-map mobs (Hard -> Skyy's Custom 20%%): PutModifier + Max for the 5 living ones "
                  "(the Lv 32 Yeti -> %.1f HP), nothing for the 0-HP one; what each player got = the queue, client copies = the server, percent "
                  "kept: %s" % (float(E2E[0][0].get(hi).getMax()), e_bad[:3]))
            MOBS.clear()
            print("NQ. network queue on real engine objects (Health index %d of %d stats): %d named lines, %d sweep changes (%s), end to end through "
                  "the world task; %d ticks of the real tracker + clear (%d packet bytes); 0.1.3 keeps every PutModifier / RemoveModifier entry "
                  "(%d in the sweep) next to a Min / Max entry, server = 0.1.2 bit for bit; 0.1.2's player copy missed %d of them (F1)" % (
                      hi, len(STATS), len(LINES), n_sw, dict(kinds), WIRE["ticks"], WIRE["bytes"], n_put, n_f1))
            for ln_ in LINES:
                print("   " + ln_)
        finally:
            if added[0]:
                smap.remove(EST.class_)
            f_store.set(None, old_store)
            for f_, v_ in old_dst:
                f_.setInt(None, v_)
            f_mod.set(None, old_mod)
            MOBS.clear()
            PMOBS.clear()
            jcall(PCfg, "useDefaults")
            Cfg.useDefaults()

    # ================================================================================================ 0.1.3 section AX (engine-access audit)
    def section_ax():
        """AX: the engine-access audit with the JVM's own rules (the SkyyUiProbe 0.3.1 / SkyyMenu 0.3.6 audit): every class / field / method /
        constructor reference in the jar's bytecode is looked up with a MethodHandles.Lookup IN its referencing class (privateLookupIn: a
        protected engine member only from a subclass, no package-private / private member of another class, public classes only). The
        receiver rule for protected members (only on this / a reference of the subclass) is the verifier's - section A loads every class
        under -Xverify:all. Control: a class that is no EntityStatValue calling its protected set(float) is refused by the same audit and,
        run, throws the game's IllegalAccessError."""
        CPa = JClass("javassist.ClassPool")(False)
        CPa.appendClassPath(JAR)
        CPa.appendClassPath(B.SERVER_JAR)
        CPa.appendSystemPath()
        hx = CPa.makeClass(PKG + "SkyyMobsLookupIn")
        hx.addMethod(CtNewMethod.make("public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
                                      "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", hx))
        LIN = JClass(str(hx.toClass(JClass(PKG + "MobLog").class_).getName()))
        bsx = CPa.makeClass(PKG + "SkyyMobsBadSetter")
        bsx.addMethod(CtNewMethod.make("public static float bad(com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue v, float f) {\n"
                                       "  return v.set(f);\n}", bsx))
        BSX = JClass(str(bsx.toClass(JClass(PKG + "MobLog").class_).getName()))
        MTc = JClass("java.lang.invoke.MethodType")
        CPoolc = JClass("javassist.bytecode.ConstPool")
        RModx = JClass("java.lang.reflect.Modifier")
        XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
                0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
                0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}
        CS = collections.Counter()

        def jvm_class(name):
            n_ = name.replace("/", ".")
            if n_.endswith("[]"):
                dims = n_.count("[]")
                elem = n_[:-2 * dims]
                prim = {"int": "I", "long": "J", "float": "F", "double": "D", "boolean": "Z", "char": "C", "byte": "B", "short": "S"}
                n_ = "[" * dims + (prim[elem] if elem in prim else "L" + elem + ";")
            return Cls.forName(n_, False, sysl)

        def lookup_audit(cn):
            """(refused references, references checked, protected engine members used) of class cn"""
            D = jvm_class(cn)
            lk = LIN.lookupIn(D)
            cc = CPa.get(cn)
            sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
            refused, n_, prot = [], 0, set()
            for mi in cc.getClassFile2().getMethods():
                ca_ = mi.getCodeAttribute()
                if ca_ is None:
                    continue
                cp, it_ = mi.getConstPool(), ca_.iterator()
                in_ctor = str(mi.getName()) == "<init>"
                while it_.hasNext():
                    p_ = it_.next()
                    op = it_.byteAt(p_)
                    if op not in XOPS:
                        continue
                    where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                    if op == 0xba:
                        refused.append(where + ": invokedynamic (javassist never writes one)")
                        continue
                    idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                    tag = cp.getTag(idx)
                    if op in (0x12, 0x13) and tag != CPoolc.CONST_Class:
                        continue
                    n_ += 1
                    C_, name, mt = None, None, None
                    try:
                        if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                            lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                        elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                            C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                            ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", sysl).parameterType(0)
                            if op in (0xb2, 0xb3):
                                lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                            else:
                                lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            if tag == CPoolc.CONST_InterfaceMethodref:
                                cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                     str(cp.getInterfaceMethodrefType(idx)))
                            else:
                                cname, name, desc = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx))
                            C_ = jvm_class(cname)
                            mt = MTc.fromMethodDescriptorString(desc, sysl)
                            if name == "<init>" and in_ctor and cname in (sup, cn):
                                md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                                if not (RModx.isPublic(md) or RModx.isProtected(md) or cname == cn
                                        or (not RModx.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                    raise ValueError("constructor %s %s%s is not accessible from %s" % (RModx.toString(md), cname, desc, cn))
                            elif name == "<init>":
                                lk.findConstructor(C_, mt)
                            elif op == 0xb8:
                                lk.findStatic(C_, name, mt)
                            elif op == 0xb7:
                                lk.findSpecial(C_, name, mt, D)
                            else:
                                lk.findVirtual(C_, name, mt)
                            if cname.startswith("com.hypixel.") and name != "<init>":
                                c_ = C_
                                while c_ is not None:
                                    try:
                                        x_ = c_.getDeclaredMethod(name, mt.parameterArray())
                                    except Exception:
                                        c_ = c_.getSuperclass()
                                        continue
                                    if RModx.isProtected(x_.getModifiers()):
                                        prot.add("%s.%s (from %s)" % (str(c_.getSimpleName()), name, cn.rsplit(".", 1)[-1]))
                                    break
                    except Exception as ex_:
                        # MethodHandles refuses caller-sensitive JDK methods (Field.get, Method.invoke, Class.forName - the config kit's
                        # reflection) to a privateLookupIn lookup whatever their access; for those the JVM's own rule is checked directly:
                        # a public member of a public class is accessible from anywhere (as the SkyyMenu 0.3.6 audit)
                        if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb9, 0xb8) and C_ is not None and mt is not None:
                            try:
                                m_ = C_.getMethod(name, mt.parameterArray())
                                if RModx.isPublic(int(m_.getModifiers())) and RModx.isPublic(int(m_.getDeclaringClass().getModifiers())):
                                    CS["%s.%s" % (str(C_.getSimpleName()), name)] += 1
                                    continue
                            except Exception:
                                pass
                        refused.append("%s: %s" % (where, ex_))
            return refused, n_, prot

        xref, xn, xprot = [], 0, set()
        for cn in names:
            r_, n_, p_ = lookup_audit(cn)
            xref += r_
            xn += n_
            xprot |= p_
        check(not xref and xn > 1000, "AX. all %d class / field / method / constructor references in the jar's %d classes pass MethodHandles.Lookup in "
                                      "their own class (the JVM's access rules): refused %s" % (xn, len(names), xref[:5]))
        lv_r, lv_n, _lp = lookup_audit(PKG + "MobLevel")
        check(not lv_r and lv_n > 300, "AX. MobLevel (the class 0.1.3 changes, writeValue's minStatValue / maxStatValue calls included): %d references, "
                                       "0 refused (%s)" % (lv_n, lv_r[:3]))
        br, bn, _bp = lookup_audit(PKG + "SkyyMobsBadSetter")
        check(len(br) == 1 and "SkyyMobsBadSetter.bad" in br[0] and "invokevirtual" in br[0] and "set" in br[0],
              "AX. control: the protected EntityStatValue.set call from a class that is no EntityStatValue is refused by the same audit: %s" % br)
        try:
            BSX.bad(U.allocateInstance(JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue").class_), JFloat(1.0))
            xmsg = ""
        except Exception as ex_:
            try:
                xmsg = "%s: %s" % (ex_.getClass().getName(), ex_.getMessage())
            except Exception:
                xmsg = str(ex_)
        check(xmsg.startswith("java.lang.IllegalAccessError: ") and "protected" in xmsg and "EntityStatValue.set" in xmsg,
              "AX. control: running that call throws the game's IllegalAccessError - this JVM enforces the rule the audit relies on: %s" % xmsg[:220])
        print("AX. engine-access audit: %d references in %d classes, 0 refused (%d caller-sensitive JDK calls checked as public members: %s; "
              "control refused %d and threw IllegalAccessError); protected engine members the jar calls (each from its own subclass): %s" % (
                  xn, len(names), sum(CS.values()), dict(CS), len(br), ", ".join(sorted(xprot)) or "none"))

    # ---------------- K. the config kit (Server Setup > Mobs)
    mods = os.path.join(SCRATCH, "kit", "mods")
    home = os.path.join(mods, "Skyy_SkyyMobs")
    shutil.rmtree(os.path.dirname(mods), ignore_errors=True)
    os.makedirs(home)
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.BANDS = Paths.get(os.path.join(home, "bands.properties"))
    Cfg.load()
    cfgf, bandf = os.path.join(home, "config.properties"), os.path.join(home, "bands.properties")
    check(os.path.isfile(cfgf) and os.path.isfile(bandf), "K. load() seeds config.properties + bands.properties")
    check(open(cfgf, "rb").read() == str(Cfg.DEF_CFG).encode("latin-1") and open(bandf, "rb").read() == str(Cfg.DEF_BANDS).encode("latin-1"),
          "K. the seeded files are exactly the default texts")
    Pub = JClass(PKG + "CfgPub")
    Pub.start(Paths.get(mods), None)
    BR = Lvl.bridge()
    hdr, fn = BR.get("config:def:SkyyMobs"), BR.get("config:fn:SkyyMobs")
    if not check(hdr is not None and fn is not None, "K. config:def + config:fn:SkyyMobs published"):
        return
    rows = [[str(x) for x in row] for row in hdr[7]]
    check(str(hdr[0]) == "1" and str(hdr[1]) == "SkyyMobs" and str(hdr[2]) == "Mobs" and str(hdr[3]) == VERSION and str(hdr[4]) == "skyymobs.admin"
          and [str(x) for x in hdr[5]] == ["levels", "strength", "curve", "gap", "bands", "plate"]
          and str(hdr[8]) == "Skyy_SkyyMobs/config.properties,Skyy_SkyyMobs/bands.properties", "K. header: %s" % [str(hdr[i]) for i in (0, 1, 2, 3, 4, 8)])
    keys = [r_[0] for r_ in rows]
    check(len(rows) == 44 and keys[0] == "part.levels", "K. 44 rows (0.1.3's 26 + the 18 rows of spec 6.1): %s" % keys)
    # 0.1.1: the short labels (Skyy's screenshot) and the Strength page numbers
    RW = dict((r_[0], r_) for r_ in rows)
    check([str(x) for x in hdr[6]] == ["Which mobs", "Strength", "Level curve", "Level gap", "Level bands", "Nameplate"], "K. tab labels (0.1.1's + 0.1.4's Level curve / Level gap): %s" % [str(x) for x in hdr[6]])
    check(RW["strength.difficulty"][7] == "easy|Easy,normal|Normal,hard|Hard,custom|Custom" and RW["strength.difficulty"][4] == "normal",
          "K. Difficulty choices Easy / Normal / Hard / Custom (values 0.1's), default normal: %s" % RW["strength.difficulty"][7])
    check(RW["strength.difficulty"][10] == "Picks the curve tables (Per level: Easy 4/2, Normal 6/3, Hard 8/4 %). Custom = your own.",
          "K. 0.1.4: the Difficulty help line (spec 6.1) still carries the Per level numbers: %r" % RW["strength.difficulty"][10])
    check(RW["strength.hpCap"][4] == "6" and RW["strength.dmgCap"][4] == "3.5" and RW["strength.hpCap"][10].startswith("Per level shape only:")
          and "x6: Hard at Lv 60 unclipped" in RW["strength.hpCap"][10] and "x3.5: Hard at Lv 60 unclipped" in RW["strength.dmgCap"][10],
          "K. caps x6 / x3.5 + their 0.1.4 help (Per level shape only): %r / %r" % (RW["strength.hpCap"][10], RW["strength.dmgCap"][10]))
    check(RW["strength.hp"][4] == "4" and RW["strength.dmg"][4] == "2", "K. Custom rows unchanged (4 / 2)")
    # 0.1.2: the floor row + the two help texts
    check(RW.get("strength.floor") == FLOOR_ROW, "K. 0.1.2 row strength.floor: %s" % RW.get("strength.floor"))
    check(keys.index("strength.floor") == keys.index("strength.dmgCap") + 1, "K. the floor row sits after the damage cap on the Strength page")
    check(RW["strength.hp"][10] == "Per level shape, Custom only: max health +this % per level above 1. Applies at once (health % kept)."
          and RW["strength.dmg"][10] == "Per level shape, Custom only: damage +this % per level above 1, before armour. Applies at once.",
          "K. 0.1.4: the strength.hp / dmg help texts name the shape: %r / %r" % (RW["strength.hp"][10], RW["strength.dmg"][10]))

    def op(*a):
        arr = JArray(JObject)(len(a))
        for k, x in enumerate(a):
            arr[k] = x
        return fn.apply(arr)

    # ---------------- V. every Server Setup text fits, drawn by the REAL SkyyMenu 0.3.5 AdminPage (tabRow + drawRow)
    try:
        section_v(hdr, rows)
    except Exception as ex:
        import traceback
        traceback.print_exc()
        check(False, "V. the Server Setup fit section could not run: %s" % ex)

    def settle():
        Pub.flush()
        time.sleep(0.7)
        Pub.flush()
        time.sleep(0.3)
    dfl = dict((r_[0], r_[4]) for r_ in rows)
    for r_ in rows:
        if r_[3] not in ("table",):
            check(str(op("get", r_[0])) == r_[4], "K. get %s = its default %r" % (r_[0], r_[4]))
    r = op("set", "strength.difficulty", "hard", None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(Cfg.DIFFICULTY) == "hard" and abs(float(Cfg.HP_STEP) - 0.08) < 1e-12 and abs(float(Cfg.DMG_STEP) - 0.04) < 1e-12,
          "K. Difficulty = Hard (8%% / 4%%) through the kit: live at once (after= derive): %s" % [str(x) for x in r])
    r = op("set", "strength.difficulty", "Easy", None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(Cfg.DIFFICULTY) == "easy" and abs(float(Cfg.HP_STEP) - 0.04) < 1e-12,
          "K. the choice LABEL 'Easy' is accepted too (typed label, any case) -> easy 4%%: %s" % [str(x) for x in r])
    r = op("set", "strength.difficulty", "hard", None, None, "yes", "console")
    # 0.1.4: the seeded file is Level curve (caps unused there); the cap check runs after Strength shape -> Per level through the kit
    check(str(op("get", "strength.shape")) == "curve" and bool(Cfg.CURVE_ON) and float(Cfg.hpMult(60)) == f32(28.98),
          "K. 0.1.4: the fresh file is Level curve (Hard Lv 60 = x28.98 from the table, the caps unused)")
    r = op("set", "strength.shape", "linear", None, None, "", "console")
    check(str(r[0]) == "confirm" and bool(Cfg.CURVE_ON), "K. 0.1.4: changing Strength shape asks first (danger): %s" % [str(x) for x in r])
    r = op("set", "strength.shape", "Per level", None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(Cfg.SHAPE) == "linear" and not bool(Cfg.CURVE_ON) and abs(float(Cfg.hpMult(60)) - f32(5.72)) < 1e-6,
          "K. 0.1.4: Strength shape = Per level (the typed label) through the kit -> 0.1.3's Hard x5.72 at Lv 60 at once: %s" % [str(x) for x in r])
    r = op("set", "strength.hpCap", "5.5", None, None, "yes", "console")
    check(str(r[0]) == "ok" and float(Cfg.HP_CAP) == 5.5 and float(Cfg.hpMult(60)) == 5.5, "K. a lower health cap through the kit clips Hard Lv 60 at once (x5.5)")
    r = op("set", "strength.hpCap", None, None, None, "yes", "console")
    check(str(r[0]) == "ok" and float(Cfg.HP_CAP) == 6.0 and str(op("get", "strength.hpCap")) == "6", "K. Default puts the health cap back to x6")
    r = op("set", "strength.shape", None, None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(op("get", "strength.shape")) == "curve" and bool(Cfg.CURVE_ON), "K. 0.1.4: Default puts Strength shape back to Level curve")
    r = op("set", "strength.hp", "101", None, None, "yes", "console")
    check(str(r[0]) == "bad", "K. Custom health 101%% refused: %s" % [str(x) for x in r])
    r = op("set", "plate.format", "Lv {lvl} {name}", None, None, "yes", "console")
    check(str(r[0]) == "bad" and str(Cfg.FORMAT) == "[Lv {level}] {name}", "K. a plate format without {level} refused (check hook): %s" % [str(x) for x in r])
    r = op("set", "plate.format", "{name} [{level}]", None, None, "yes", "console")
    check(str(r[0]) == "ok" and str(Lvl.plateText(4, "Boar")) == "Boar [4]", "K. a new plate format applies: %s" % Lvl.plateText(4, "Boar"))
    try:
        check(bool(Cfg.FORMATS.containsKey("{name} [{level}]")) and bool(Lvl.isOurs("[Lv 4] Boar")) and bool(Lvl.isOurs("Boar [4]")),
              "K. F7: plate.format runs derive (after=): the new format is remembered, a default-format plate is still ours")
    except Exception as ex:
        check(False, "K. F7 check could not run: %s" % ex)
    # review F1 / F5 / F10 through the real kit: the extra row takes patterns and a blank, Never level these takes *
    check(str(op("get", "levels.roles")) == "", "K. F1: Extra mobs that get levels is empty by default")
    r = op("set", "levels.roles", "Mosshorn*", None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("NEUTRAL", "Mosshorn") is None, "K. F1: levels.roles = Mosshorn* levels Mosshorn: %s" % [str(x) for x in r])
    r = op("set", "levels.roles", "", None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("NEUTRAL", "Mosshorn") is not None and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None,
          "K. F10: a blank levels.roles keeps the vanilla mobs levelled: %s" % [str(x) for x in r])
    r = op("set", "levels.exclude", "*", None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") == "in Never level these", "K. F5: levels.exclude = * (uninstall) is accepted and strips all: %s" % [str(x) for x in r])
    r = op("set", "levels.exclude", str(dfl["levels.exclude"]), None, None, "yes", "console")
    check(str(r[0]) == "ok" and Cfg.whyNot("HOSTILE", "Skeleton_Fighter") is None, "K. levels.exclude back to its default")
    r = op("set", "bands.islands", "1-3", None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.ISL_A) == 1 and int(Cfg.ISL_B) == 3, "K. Private islands 1-3 (range) live")
    r = op("set", "levels.max", "0", None, None, "yes", "console")
    check(str(r[0]) == "bad" and int(Cfg.MAX_LEVEL) == 100, "K. Highest mob level 0 refused")
    # 0.1.2: the Health floor row through the real kit
    check(str(op("get", "strength.floor")) == "50" and int(Cfg.HP_FLOOR) == 50, "K. Health floor = 50 by default")
    r = op("set", "strength.floor", "80", None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.HP_FLOOR) == 80 and float(Cfg.floorFactor(40.0)) == 2.0, "K. Health floor 80 through the kit: live at once: %s" % [str(x) for x in r])
    for bad_ in ("-1", "1001", "abc", "12.5"):
        r = op("set", "strength.floor", bad_, None, None, "yes", "console")
        check(str(r[0]) == "bad" and int(Cfg.HP_FLOOR) == 80, "K. Health floor %r refused: %s" % (bad_, [str(x) for x in r]))
    r = op("set", "strength.floor", "0", None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.HP_FLOOR) == 0 and float(Cfg.floorFactor(10.0)) == 1.0, "K. Health floor 0 = off: %s" % [str(x) for x in r])
    r = op("set", "strength.floor", None, None, None, "yes", "console")
    check(str(r[0]) == "ok" and int(Cfg.HP_FLOOR) == 50 and str(op("get", "strength.floor")) == "50", "K. Default puts the floor back to 50")
    r = op("set", "strength.floor", "80", None, None, "yes", "console")
    r = op("set", "part.levels", "false", None, None, "", "console")
    check(str(r[0]) == "confirm" and bool(Cfg.ON), "K. switching Mob levels OFF asks first (part, danger)")
    r = op("set", "part.levels", "false", None, None, "yes", "console")
    check(str(r[0]) == "ok" and not bool(Cfg.ON), "K. ... and applies after yes")
    op("set", "part.levels", "true", None, None, "yes", "console")
    settle()
    txt = open(cfgf, "rb").read().decode("latin-1")
    check("\nstrength.difficulty=hard\n" in txt and "\nplate.format={name} [{level}]\n" in txt and "\nbands.islands=1-3\n" in txt
          and "\nstrength.shape=curve\n" in txt and txt.count("strength.shape=") == 1
          and txt.count("strength.difficulty=") == 1 and "\nstrength.floor=80\n" in txt and txt.count("strength.floor=") == 1,
          "K. the file lines changed in place (the floor too)")
    ks = op("keys", "bands.biome", "")
    ents = [str(x) for x in ks[0]]
    vals = dict(zip(ents, [str(x) for x in ks[2]]))
    check(len(ents) == int(Cfg.BIOME.n) and vals.get("Zone1_Tier3.Forest_Azure") == "18|20" and vals.get("Zone1_Tier3") == "12|20",
          "K. bands.biome lists every row (%d), Forest_Azure 18|20, the region row Zone1_Tier3 12|20" % len(ents))
    r = op("tset", "bands.biome", "Zone1_Tier3.Forest_Azure", "17|20", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. tset Forest_Azure 17|20: %s" % [str(x) for x in r])
    r = op("tset", "bands.biome", "Zone1_Tier3.Forest_Azure", "21|20", None, None, "yes", "console")
    check(str(r[0]) == "bad", "K. Min above Max refused (checkBand): %s" % [str(x) for x in r])
    r = op("add", "bands.world", "dungeon_*", "20|23", None, None, "yes", "console")
    check(str(r[0]) == "bad", "K. a * in a table entry is refused by the kit (why the tables ship without patterns): %s" % [str(x) for x in r])
    r = op("add", "bands.world", "dungeon_", "20|23", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. add a world row dungeon_ 20|23: %s" % [str(x) for x in r])
    r = op("tset", "bands.biome", "Zone1_Tier3", "13|20", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. the region row Zone1_Tier3 is editable in game: %s" % [str(x) for x in r])
    r = op("add", "bands.env", "Env_Zone1_Test", "3|4|1", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. add an env row with a bonus: %s" % [str(x) for x in r])
    r = op("tset", "plate.colors", "20", "#123456", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. plate.colors 20 = #123456: %s" % [str(x) for x in r])
    for e_, v_ in (("20", "red"), ("abc", "#ffffff"), ("0", "#ffffff")):
        r = op("tset", "plate.colors", e_, v_, None, None, "yes", "console")
        check(str(r[0]) == "bad", "K. plate.colors %s = %s refused: %s" % (e_, v_, [str(x) for x in r]))
    settle()
    bt = open(bandf, "rb").read().decode("latin-1")
    check("\nbiome.Zone1_Tier3.Forest_Azure=17,20\n" in bt and "world.dungeon_=20,23" in bt and "env.Env_Zone1_Test=3,4,1" in bt
          and "\nbiome.Zone1_Tier3=13,20\n" in bt,
          "K. bands.properties lines written (17,20 in place; the new rows appended)")
    check(jres("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", None)[:2] == (17, 20)
          and jres("dungeon_7", False, True, "Zone1_Tier1", "Plains_Smooth", "Plains_Smooth", None)[:4] == (20, 23, 0, "world")
          and str(Lvl.hexFor(25)) == "#123456", "K. the reload routine (MobCfg.reloadAll) applied the table changes: %s / %s / %s" % (
              jres("default", False, True, "Zone1_Tier3", "Forest_Azure", "Forest_Azure", None)[:2], jres("dungeon_7", False, True, None, None, None, None)[:4], Lvl.hexFor(25)))
    r = op("remove", "bands.world", "dungeon_", None, None, "yes", "console")
    check(str(r[0]) == "ok", "K. remove the world row: %s" % [str(x) for x in r])
    settle()
    check(int(Cfg.WORLD.n) == 0, "K. the world row is gone after the reload routine")
    # a hand edit + the reload op
    open(bandf, "ab").write(b"zone.Zone5=60,75\n")
    r = op("reload", None, None, "console")
    settle()
    check(str(r[0]) == "ok" and Cfg.ZONE.find("Zone5") >= 0, "K. a hand-edited line + reload -> zone.Zone5 60-75 in memory: %s" % [str(x) for x in r])
    r = op("set", "strength.difficulty", "normal", None, None, "yes", "console")
    Pub.shutdown()
    print("K. config kit: 44 rows (6 categories), get = defaults, set live + refused + confirm (the floor row too), 5 table ops through the "
          "real kit + the reload routine, hand edit + reload op")

    # ---------------- S. start twice (no churn)
    sd = os.path.join(SCRATCH, "twice", "mods")
    sh = os.path.join(sd, "Skyy_SkyyMobs")
    shutil.rmtree(os.path.dirname(sd), ignore_errors=True)
    os.makedirs(sh)

    S_MG = []

    def start():        # 0.1.4: in setup()'s order - MobMig.run, MobMig14.run, MobCfg.load, CfgPub.start
        Cfg.DIR = Paths.get(sh)
        Cfg.FILE = Paths.get(os.path.join(sh, "config.properties"))
        Cfg.BANDS = Paths.get(os.path.join(sh, "bands.properties"))
        S_MG.append(str(Mig.run(Cfg.DIR)) + str(JClass(PKG + "MobMig14").run(Cfg.DIR)))
        Cfg.load()
        Pub.start(Paths.get(sd), None)
        Pub.flush()
        time.sleep(0.6)
        Pub.shutdown()

    def snap():
        out = {}
        for dp, _dn, fns in os.walk(sd):
            for f_ in fns:
                p_ = os.path.join(dp, f_)
                out[os.path.relpath(p_, sd)] = (open(p_, "rb").read(), os.path.getmtime(p_))
        return out
    start()
    s1 = snap()
    time.sleep(1.1)
    start()
    s2 = snap()
    check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "S. the second start changes nothing (files + mtimes): %s" % sorted(set(s1) ^ set(s2)))
    check(sorted(s1) == [os.path.join("Skyy_SkyyMobs", "bands.properties"), os.path.join("Skyy_SkyyMobs", "config.properties")],
          "S. only the two files exist (no history version, no change log): %s" % sorted(s1))
    check(S_MG == ["", ""] and MARK.encode("latin-1") in s1[os.path.join("Skyy_SkyyMobs", "config.properties")][0]
          and JClass(PKG + "MobMig14").MARK_ID.encode("latin-1") in s1[os.path.join("Skyy_SkyyMobs", "config.properties")][0],
          "S. a fresh 0.1.4 folder is never updated by either update (the seeded file carries both markers): %s" % S_MG)
    # a scratch copy of the started folder, started again
    cp_ = os.path.join(SCRATCH, "twice-copy", "mods")
    shutil.rmtree(os.path.dirname(cp_), ignore_errors=True)
    shutil.copytree(sd, cp_)
    sd0 = sd
    sd = cp_
    sh = os.path.join(cp_, "Skyy_SkyyMobs")
    c1 = snap()
    time.sleep(1.1)
    start()
    c2 = snap()
    check(all(c1[k][0] == c2[k][0] for k in c1) and sorted(c1) == sorted(c2), "S. a copy started again: byte-identical")
    sd = sd0
    Cfg.useDefaults()
    print("S. start twice: no churn (fresh folder + a copy)")

    # ================================================================================================ 0.1.4 sections (research/Mob-Curve-Spec.md)
    # CU the Level curve tables  GP the gap maths + the class level cache  DM GapDamage / LevelDamage on real engine Damage objects
    # SR scale.role (onAdd through a stand-in Holder)  IF mob:fn:info  WN the gear-curve WARN  CMD the /mobs texts  MIG MobMig14
    # SET the build's pairing STOP
    Cfg14 = Cfg0                      # the real MobCfg (no Per level proxy) for the 0.1.4 sections
    M14 = JClass(PKG + "MobMig14")
    GapC = JClass(PKG + "MobGap")
    InfoFnC = JClass(PKG + "MobInfoFn")
    ScanC = JClass(PKG + "MobScanTask")
    HooksC = JClass(PKG + "MobHooks")
    MInfo = JClass(PKG + "MobInfo")
    JDouble = JClass("java.lang.Double")
    # the spec's section 1.3 tables, typed here independently of the build
    SPEC13 = {
        ("hp", "hard"): [(1, 1.0), (20, 2.52), (25, 3.62), (30, 5.6), (35, 8.53), (40, 13.18), (45, 19.41), (49, 24.52), (55, 26.95), (60, 28.98)],
        ("hp", "normal"): [(1, 1.0), (20, 2.14), (25, 3.03), (30, 4.62), (35, 6.97), (40, 10.69), (45, 15.63), (49, 19.66), (55, 21.48), (60, 23.0)],
        ("hp", "easy"): [(1, 1.0), (20, 1.76), (25, 2.43), (30, 3.65), (35, 5.41), (40, 8.19), (45, 11.85), (49, 14.79), (55, 16.01), (60, 17.02)],
        ("dmg", "hard"): [(1, 1.0), (20, 1.76), (25, 2.32), (30, 3.03), (35, 3.89), (40, 4.95), (45, 6.41), (49, 7.72), (55, 8.31), (60, 8.78)],
        ("dmg", "normal"): [(1, 1.0), (20, 1.57), (25, 2.04), (30, 2.62), (35, 3.33), (40, 4.2), (45, 5.39), (49, 6.45), (55, 6.89), (60, 7.24)],
        ("dmg", "easy"): [(1, 1.0), (20, 1.38), (25, 1.75), (30, 2.22), (35, 2.77), (40, 3.44), (45, 4.36), (49, 5.19), (55, 5.47), (60, 5.7)],
    }
    SPEC13[("hp", "custom")] = SPEC13[("hp", "hard")]
    SPEC13[("dmg", "custom")] = SPEC13[("dmg", "hard")]
    DIFFS4 = ["easy", "normal", "hard", "custom"]
    # spec 1.4 (health / damage, DERIVED in the spec from 1.3): (level) -> {difficulty: (hp, dmg)}
    SPEC14 = {1: {"easy": (1.0, 1.0), "normal": (1.0, 1.0), "hard": (1.0, 1.0)}, 5: {"easy": (1.16, 1.08), "normal": (1.24, 1.12), "hard": (1.32, 1.16)},
              10: {"easy": (1.36, 1.18), "normal": (1.54, 1.27), "hard": (1.72, 1.36)}, 15: {"easy": (1.56, 1.28), "normal": (1.84, 1.42), "hard": (2.12, 1.56)},
              20: {"easy": (1.76, 1.38), "normal": (2.14, 1.57), "hard": (2.52, 1.76)}, 21: {"easy": (1.89, 1.45), "normal": (2.32, 1.66), "hard": (2.74, 1.87)},
              25: {"easy": (2.43, 1.75), "normal": (3.03, 2.04), "hard": (3.62, 2.32)}, 30: {"easy": (3.65, 2.22), "normal": (4.62, 2.62), "hard": (5.60, 3.03)},
              33: {"easy": (4.71, 2.55), "normal": (6.03, 3.05), "hard": (7.36, 3.55)}, 34: {"easy": (5.06, 2.66), "normal": (6.50, 3.19), "hard": (7.94, 3.72)},
              35: {"easy": (5.41, 2.77), "normal": (6.97, 3.33), "hard": (8.53, 3.89)}, 40: {"easy": (8.19, 3.44), "normal": (10.69, 4.20), "hard": (13.18, 4.95)},
              45: {"easy": (11.85, 4.36), "normal": (15.63, 5.39), "hard": (19.41, 6.41)}, 49: {"easy": (14.79, 5.19), "normal": (19.66, 6.45), "hard": (24.52, 7.72)},
              50: {"easy": (14.99, 5.24), "normal": (19.96, 6.52), "hard": (24.93, 7.82)}, 55: {"easy": (16.01, 5.47), "normal": (21.48, 6.89), "hard": (26.95, 8.31)},
              60: {"easy": (17.02, 5.70), "normal": (23.00, 7.24), "hard": (28.98, 8.78)}}
    F_OLD14 = [(1, 1.0), (4, 1.6), (10, 2.0), (40, 3.0), (100, 5.0)]
    F_NEW14 = [(1, 1.0), (4, 1.6), (10, 2.0), (20, 2.333333), (25, 3.1), (30, 4.5), (35, 6.5), (40, 9.6), (45, 13.6), (50, 17.5), (60, 22.5),
               (70, 36.0), (80, 57.0), (90, 90.0)]
    # spec 2.3: player max HP today -> new at the listed levels (the damage half of the 1.2 rule)
    HP23 = {25: (176, 208), 30: (182, 256), 33: (186, 287), 35: (190, 314), 40: (198, 383), 45: (204, 474), 49: (209, 554), 60: (213, 558)}

    def py_eval(pts, x):
        """the spec's 'straight lines between points, flat outside them' in Java's double order of operations"""
        x = float(x)
        if x <= pts[0][0]:
            return pts[0][1]
        if x >= pts[-1][0]:
            return pts[-1][1]
        for i in range(1, len(pts)):
            if x <= pts[i][0]:
                l0, v0 = float(pts[i - 1][0]), pts[i - 1][1]
                l1, v1 = float(pts[i][0]), pts[i][1]
                return v0 + (v1 - v0) * (x - l0) / (l1 - l0)
        return pts[-1][1]

    def curve_state(shape, diff, extra=None, drop=()):
        """apply the jar's own default file with this shape / difficulty (+ extra lines, - dropped prefixes) through the real loader"""
        c_ = Cfg14.props(Cfg14.DEF_CFG)
        c_.setProperty("strength.shape", shape)
        c_.setProperty("strength.difficulty", diff)
        for k_ in [str(x) for x in c_.stringPropertyNames()]:
            if any(k_.startswith(d_) for d_ in drop):
                c_.remove(k_)
        for k_, v_ in (extra or {}).items():
            c_.setProperty(k_, v_)
        Cfg14.apply(c_, Cfg14.props(Cfg14.DEF_BANDS))

    @JImplements("java.lang.Runnable")
    class CountRun(object):
        def __init__(self):
            self.n = 0

        @JOverride
        def run(self):
            self.n += 1

    def section_cu():
        """CU: the Level curve tables (spec 1.2 / 1.3 / 1.4 / 6.1) through the jar's own loader, eval, hpMult / dmgMult / hardRef; the 1.2 rule;
        Lv 1-20 = 0.1.3's presets float-exact; hand-edited lines; the health signature (the live re-apply trigger); the tables through the kit"""
        Cfg14.ON_HEALTH = None
        curve_state("curve", "hard")
        check(bool(Cfg14.CURVE_ON) and str(Cfg14.SHAPE) == "curve" and str(Cfg14.difficultyText()) == "Hard curve", "CU. strength.shape=curve -> Level curve, 'Hard curve'")
        # the parsed tables = the spec's 1.3 block (index = kind x 4 + difficulty)
        bad_ = []
        for ki, k_ in enumerate(("hp", "dmg")):
            for di, d_ in enumerate(DIFFS4):
                q_ = Cfg14.curveOf(ki * 4 + di)
                got = [(int(a), float(b)) for a, b in zip(q_[0], q_[1])]
                if got != SPEC13[(k_, d_)]:
                    bad_.append((k_, d_, got))
                if str(Cfg14.CURVE_KEY[ki * 4 + di]) != "curve.%s.%s" % (k_, d_):
                    bad_.append(("key", ki * 4 + di, str(Cfg14.CURVE_KEY[ki * 4 + di])))
        check(not bad_, "CU. the 8 default tables = the spec's section 1.3 block exactly (custom = Hard's copies): %s" % bad_[:3])
        # every level 0-110: hpMult / dmgMult = float(eval) bit for bit, for every difficulty
        n_ = 0
        bad_ = []
        for d_ in DIFFS4:
            curve_state("curve", d_)
            for L in range(0, 111):
                eh, ed = f32(max(0.1, py_eval(SPEC13[("hp", d_)], L))), f32(max(0.1, py_eval(SPEC13[("dmg", d_)], L)))
                gh, gd = float(Cfg14.hpMult(L)), float(Cfg14.dmgMult(L))
                n_ += 2
                if gh != eh or gd != ed:
                    bad_.append((d_, L, gh, eh, gd, ed))
                if float(Cfg14.hardRef(L)) != f32(max(0.1, py_eval(SPEC13[("hp", "hard")], L))):
                    bad_.append((d_, L, "hardRef"))
        check(not bad_, "CU. hpMult / dmgMult / hardRef = the tables' straight lines (Python mirror, float32 bit for bit) for 4 difficulties x Lv 0-110 (%d): %s" % (n_, bad_[:4]))
        # spec 1.4's table (DERIVED from 1.3 - rounded to 2 decimals)
        bad_ = []
        for L, row in SPEC14.items():
            for d_, (h_, m_) in row.items():
                curve_state("curve", d_)
                if abs(float(Cfg14.hpMult(L)) - h_) > 0.0051 or abs(float(Cfg14.dmgMult(L)) - m_) > 0.0051:
                    bad_.append((L, d_, float(Cfg14.hpMult(L)), h_, float(Cfg14.dmgMult(L)), m_))
            for L2 in range(61, 101):
                if float(Cfg14.hpMult(L2)) != float(Cfg14.hpMult(60)):
                    bad_.append((L2, "flat after 60"))
        check(not bad_, "CU. the spec's section 1.4 table (Lv 1-60, %d entries, within 0.005) and flat after Lv 60: %s" % (
            sum(len(r) for r in SPEC14.values()), bad_[:4]))
        # Lv 1-20 of every table = 0.1.3's preset (SkyyMobs-0.1.3.jar's own hpMult / dmgMult), float-exact; Custom curve = 0.1.3's Hard
        PCfg = pin_cls("MobCfg")
        bad_ = []
        for d_ in DIFFS4:
            curve_state("curve", d_)
            PCfg.getField("DIFFICULTY").set(None, JStr("hard" if d_ == "custom" else d_))
            jcall(PCfg, "derive", (JStr.class_, None))
            for L in range(0, 21):
                o_h = float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L))))
                o_d = float(jcall(PCfg, "dmgMult", (Integer.TYPE, Integer.valueOf(L))))
                if o_h != float(Cfg14.hpMult(L)) or o_d != float(Cfg14.dmgMult(L)):
                    bad_.append((d_, L, o_h, float(Cfg14.hpMult(L)), o_d, float(Cfg14.dmgMult(L))))
        check(not bad_, "CU. Lv 0-20 of every table = SkyyMobs-0.1.3.jar's own preset multipliers float-exact (Custom = 0.1.3's Hard): %s" % bad_[:4])
        # THE RULE (spec 1.2): health = 0.1.3's preset x F_new(g) / F_old(g); damage = 0.1.3's preset x max HP_new / max HP_old (spec 2.3).
        # At the table points the rule holds to the table's 2 decimals; between two points the table is a straight line while the rule is a
        # product of two straight lines (F_new / F_old), so it bends a little - checked within 1.5 % (the swing check below is the game effect)
        bad_ = []
        worst_rule = [0.0]
        for d_ in ("easy", "normal", "hard"):
            curve_state("curve", d_)
            PCfg.getField("DIFFICULTY").set(None, JStr(d_))
            jcall(PCfg, "derive", (JStr.class_, None))
            for L in range(21, 61):
                g = min(L, 49)
                want = float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L)))) * py_eval(F_NEW14, g) / py_eval(F_OLD14, g)
                rel = abs(float(Cfg14.hpMult(L)) / want - 1.0)
                worst_rule[0] = max(worst_rule[0], rel)
                if (L in (25, 30, 35, 40, 45, 49, 55, 60) and abs(float(Cfg14.hpMult(L)) - want) > 0.0051) or rel > 0.015:
                    bad_.append((d_, L, float(Cfg14.hpMult(L)), round(want, 4)))
            for L, (ho, hn) in HP23.items():
                want = float(jcall(PCfg, "dmgMult", (Integer.TYPE, Integer.valueOf(L)))) * hn / ho
                if abs(float(Cfg14.dmgMult(L)) / want - 1.0) > 0.01:
                    bad_.append((d_, L, "dmg", float(Cfg14.dmgMult(L)), round(want, 4)))
        jcall(PCfg, "useDefaults")
        check(not bad_, "CU. the 1.2 rule on Easy / Normal / Hard: health = 0.1.3's preset x F_new / F_old (g = min(L, 49)) - at the table points to 0.005, "
              "between them within 1.5%% (worst %.2f%%); damage = 0.1.3's preset x the spec 2.3 player HP ratio (within 1%%): %s" % (100 * worst_rule[0], bad_[:4]))
        # the same-level pace (spec 1.2 / 5.2): ungeared Warrior swings on a wolf-class mob (103 HP) = 0.1.3's within 1 swing at every level 1-60
        bad_ = []
        PCfg.getField("DIFFICULTY").set(None, JStr("hard"))
        jcall(PCfg, "derive", (JStr.class_, None))
        curve_state("curve", "hard")
        for L in range(1, 61):
            g = min(L, 49)
            old_sw = math.ceil(103.0 * float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L)))) / (6.0 * py_eval(F_OLD14, g)) - 1e-9)
            new_sw = math.ceil(103.0 * float(Cfg14.hpMult(L)) / (6.0 * py_eval(F_NEW14, g)) - 1e-9)
            if abs(new_sw - old_sw) > 1:
                bad_.append((L, old_sw, new_sw))
        jcall(PCfg, "useDefaults")
        check(not bad_, "CU. same-level pace (Hard, 6-damage sword, 103-HP wolf class): swings with the new curves = 0.1.3's within 1 at Lv 1-60: %s" % bad_[:4])
        # hand-edited lines: bad ones skipped (warned once), a table with no valid line -> its defaults, an extra point counts
        curve_state("curve", "hard", extra={"curve.hp.hard.abc": "2", "curve.hp.hard.101": "2", "curve.hp.hard.42": "0.05", "curve.hp.hard.43": "x"})
        got = [(int(a), float(b)) for a, b in zip(Cfg14.curveOf(2)[0], Cfg14.curveOf(2)[1])]
        check(got == SPEC13[("hp", "hard")], "CU. bad hand lines (abc, 101, factor 0.05, x) are skipped: %s" % got)
        curve_state("curve", "hard", extra={"curve.hp.hard.70": "40"})
        check(abs(float(Cfg14.hpMult(65)) - f32(28.98 + (40 - 28.98) * 5 / 10.0)) < 1e-4 and float(Cfg14.hpMult(80)) == 40.0,
              "CU. an added point (70 = 40) extends the line and is flat after it")
        curve_state("curve", "hard", drop=("curve.hp.hard.",))
        got = [(int(a), float(b)) for a, b in zip(Cfg14.curveOf(2)[0], Cfg14.curveOf(2)[1])]
        check(got == SPEC13[("hp", "hard")] and float(Cfg14.hpMult(40)) == f32(13.18), "CU. an emptied table falls back to its default points (one WARN)")
        curve_state("curve", "hard", drop=("curve.hp.hard.",), extra={"curve.hp.hard.30": "2"})
        check(float(Cfg14.hpMult(1)) == 2.0 and float(Cfg14.hpMult(60)) == 2.0, "CU. a one-point table is flat everywhere (x2)")
        # a file WITHOUT strength.shape (0.1.3's, or the update failed): Custom -> Per level, every other difficulty -> Level curve
        for d_, want in (("custom", False), ("hard", True), ("normal", True), ("weird", True)):
            c_ = Cfg14.props(Cfg14.DEF_CFG)
            c_.remove("strength.shape")
            c_.setProperty("strength.difficulty", d_)
            Cfg14.apply(c_, Cfg14.props(Cfg14.DEF_BANDS))
            check(bool(Cfg14.CURVE_ON) == want, "CU. a file without strength.shape and difficulty %s -> %s" % (d_, "Level curve" if want else "Per level"))
        # the health signature: a change of the ACTIVE health table, the shape, the difficulty, the floor or a scale.role row re-applies
        # (ON_HEALTH runs); damage tables, caps (in curve shape) and the gap rows do not
        cr = CountRun()
        curve_state("curve", "hard")
        Cfg14.ON_HEALTH = cr
        steps = [("active health table", {"curve.hp.hard.40": "14"}, "hard", "curve", 1), ("same again", {"curve.hp.hard.40": "14"}, "hard", "curve", 0),
                 ("another difficulty's health table", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9"}, "hard", "curve", 0),
                 ("a damage table", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6"}, "hard", "curve", 0),
                 ("the health cap (unused in curve shape)", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "3"}, "hard", "curve", 0),
                 ("the gap rows", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "3", "gap.free": "9"}, "hard", "curve", 0),
                 ("the difficulty", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "3", "gap.free": "9"}, "easy", "curve", 1),
                 ("a scale.role row", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "3", "gap.free": "9", "scale.role.Yeti": "30,2"}, "easy", "curve", 1),
                 ("the shape", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "3", "gap.free": "9", "scale.role.Yeti": "30,2"}, "easy", "linear", 1),
                 ("the health cap (Per level)", {"curve.hp.hard.40": "14", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "2", "gap.free": "9", "scale.role.Yeti": "30,2"}, "easy", "linear", 1),
                 ("a health table in Per level shape", {"curve.hp.hard.40": "15", "curve.hp.easy.40": "9", "curve.dmg.hard.40": "6", "strength.hpCap": "2", "gap.free": "9", "scale.role.Yeti": "30,2"}, "easy", "linear", 0)]
        for what, extra, d_, sh_, want_n in steps:
            n0 = cr.n
            curve_state(sh_, d_, extra=extra)
            check(cr.n - n0 == want_n, "CU. the live re-apply trigger: %s -> ON_HEALTH ran %d time(s) (want %d)" % (what, cr.n - n0, want_n))
        Cfg14.ON_HEALTH = None
        curve_state("curve", "hard")
        print("CU. Level curve: 8 tables = spec 1.3; %d multipliers = the straight lines bit for bit; spec 1.4 table; Lv 0-20 = 0.1.3's presets; the "
              "1.2 rule (health + damage) and the same-level swings; hand lines / empty / one-point tables; no-shape files; %d re-apply trigger cases" % (n_, len(steps)))

    def section_cuk():
        """CU-K: the curve tables and scale.role through the REAL config kit: tset / add / remove + the check hooks, the reload routine
        re-reads the file (hpMult at once), the last entry cannot be removed; on a stand-in mob the re-apply keeps the health percent"""
        mods_ = os.path.join(SCRATCH, "cukit", "mods")
        home_ = os.path.join(mods_, "Skyy_SkyyMobs")
        shutil.rmtree(os.path.dirname(mods_), ignore_errors=True)
        os.makedirs(home_)
        start_like_setup(mods_)
        try:
            cr = CountRun()
            Cfg14.ON_HEALTH = cr
            r = kit_op("set", "strength.difficulty", "hard", None, None, "yes", "console")
            check(str(r[0]) == "ok" and str(Cfg14.difficultyText()) == "Hard curve", "CU-K. Difficulty Hard through the kit -> 'Hard curve': %s" % [str(x) for x in r])
            ks = kit_op("keys", "curve.hp.hard", "")
            ents = [str(x) for x in ks[0]]
            check(sorted(ents, key=int) == ["1", "20", "25", "30", "35", "40", "45", "49", "55", "60"] and dict(zip(ents, [str(x) for x in ks[2]])).get("40") == "13.18",
                  "CU-K. Health curve: Hard lists its 10 entries (40 = 13.18): %s" % ents)
            # a stand-in levelled mob (Lv 40 Yeti, base 226, hurt to 40%)
            m_ = fresh(226.0)
            Lvl.setMult(m_, 0, 40, True, False, 1.0)
            m_.setVal(JFloat(float(m_.maxNow()) * 0.4))
            check(abs(float(m_.maxNow()) - 226.0 * f32(13.18)) < 0.05, "CU-K. (a Lv 40 Yeti: 226 x 13.18 = %.1f HP)" % float(m_.maxNow()))
            n0 = cr.n
            r = kit_op("tset", "curve.hp.hard", "40", "14", None, None, "yes", "console")
            check(str(r[0]) == "ok", "CU-K. tset Health curve: Hard [40] = 14: %s" % [str(x) for x in r])
            for _w in range(40):
                if float(Cfg14.hpMult(40)) == 14.0:
                    break
                time.sleep(0.1)
            check(float(Cfg14.hpMult(40)) == 14.0 and cr.n - n0 == 1, "CU-K. the reload routine re-read the table: Hard Lv 40 = x14 at once, the live re-apply "
                  "ran once (%d)" % (cr.n - n0))
            ch_ = bool(Lvl.refreshOne(m_, 0, 40, 1.0))
            check(ch_ and abs(float(m_.maxNow()) - 226.0 * 14.0) < 0.05 and abs(float(m_.val()) / float(m_.maxNow()) - 0.4) < 1e-5,
                  "CU-K. the loaded Lv 40 mob gets 226 x 14 = 3164 HP and keeps 40%% (%.1f / %.1f)" % (float(m_.val()), float(m_.maxNow())))
            for e_, v_, why in (("101", "5", "level 101"), ("abc", "5", "entry abc"), ("40", "0.05", "factor 0.05"), ("40", "2000", "factor 2000"), ("-1", "5", "level -1")):
                r = kit_op("tset", "curve.hp.hard", e_, v_, None, None, "yes", "console")
                check(str(r[0]) == "bad", "CU-K. %s refused: %s" % (why, [str(x) for x in r]))
            r = kit_op("add", "curve.dmg.easy", "70", "6", None, None, "yes", "console")
            check(str(r[0]) == "ok", "CU-K. add Damage curve: Easy [70] = 6: %s" % [str(x) for x in r])
            # remove every entry of one table: the last one is refused (check hook)
            ents = sorted([str(x) for x in kit_op("keys", "curve.dmg.custom", "")[0]], key=int)
            oks = []
            for e_ in ents:
                oks.append(str(kit_op("remove", "curve.dmg.custom", e_, None, None, "yes", "console")[0]))
                for _w in range(30):
                    if len(Cfg14.curveOf(7)[0]) <= len(ents) - len(oks):
                        break
                    time.sleep(0.1)
            check(oks[:-1] == ["ok"] * (len(ents) - 1) and oks[-1] == "bad" and len(Cfg14.curveOf(7)[0]) == 1,
                  "CU-K. removing every entry of Damage curve: Custom - the last one is refused (a curve keeps one point): %s" % oks)
            # scale.role through the kit: exact ids only (the kit refuses *), the hook bounds level / health x
            r = kit_op("add", "scale.role", "Goblin_Duke", "30|2", None, None, "yes", "console")
            check(str(r[0]) == "ok", "CU-K. add Fixed level by role Goblin_Duke = 30 | 2: %s" % [str(x) for x in r])
            for e_, v_, why in (("Goblin_Duke*", "30|1", "a * entry (kit)"), ("Trork_Chieftain", "101|1", "level 101"), ("Trork_Chieftain", "20|200", "health x 200"),
                                ("Trork_Chieftain", "20|0.05", "health x 0.05"), ("Trork_Chieftain", "x|1", "level x")):
                r = kit_op("add", "scale.role", e_, v_, None, None, "yes", "console")
                check(str(r[0]) == "bad", "CU-K. scale.role %s refused: %s" % (why, [str(x) for x in r]))
            for _w in range(30):
                if int(Cfg14.roleLevel("Goblin_Duke")) == 30:
                    break
                time.sleep(0.1)
            check(int(Cfg14.roleLevel("Goblin_Duke")) == 30 and float(Cfg14.roleX("goblin_duke")) == 2.0 and str(Cfg14.roleKey("GOBLIN_DUKE")) == "scale.role.Goblin_Duke",
                  "CU-K. the row is live: Goblin_Duke Lv 30, health x2 (any case)")
            stop_kit()
            txt_ = open(os.path.join(home_, "config.properties"), "rb").read().decode("latin-1")
            check("\ncurve.hp.hard.40=14\n" in txt_ and "\ncurve.dmg.easy.70=6\n" in txt_ and "\nscale.role.Goblin_Duke=30,2\n" in txt_
                  and txt_.count("\ncurve.dmg.custom.") == 1, "CU-K. the file lines: 40=14 in place, 70=6 added, scale.role.Goblin_Duke=30,2, one Damage curve: Custom line left: %s" % (
                      [l_ for l_ in txt_.split("\n") if l_.startswith(("curve.hp.hard.40", "curve.dmg.easy.7", "scale.role", "curve.dmg.custom"))]))
        finally:
            Cfg14.ON_HEALTH = None
            try:
                Pub.shutdown()
            except Exception:
                pass
            curve_state("curve", "hard")
        print("CU-K. the curve tables + scale.role through the real kit: tset / add / remove, check hooks (entry, factor, last entry, *, level, health x), "
              "the reload routine + the live re-apply (Lv 40 Yeti 2979 -> 3164 HP at 40%)")

    def section_gp():
        """GP: the level gap (spec 3.1) = a Python mirror for d = -50 ... +100 with the defaults and two other settings; the class level cache
        (2 s, no class = no gap, 0 = unknown, a cached good level never overwritten by a 0, a failing read)"""
        def mirror(d, free, ds, dm, ts, tm):
            if d <= free:
                return 1.0, 1.0
            return max(dm / 100.0, min(1.0, 1.0 - ds / 100.0 * (d - free))), max(1.0, min(tm, 1.0 + ts / 100.0 * (d - free)))
        bad_, n_ = [], 0
        for st_ in ((5, 2.5, 40.0, 1.5, 1.5), (0, 10.0, 1.0, 50.0, 100.0), (100, 2.5, 40.0, 1.5, 1.5), (3, 0.0, 100.0, 0.0, 1.0)):
            Cfg14.GAP_FREE, Cfg14.GAP_DSTEP, Cfg14.GAP_DMIN, Cfg14.GAP_TSTEP, Cfg14.GAP_TMAX = st_
            for d in range(-50, 101):
                w_ = mirror(d, *st_)
                g_ = (float(GapC.dealt(d)), float(GapC.taken(d)))
                n_ += 1
                if abs(g_[0] - w_[0]) > 1e-12 or abs(g_[1] - w_[1]) > 1e-12:
                    bad_.append((st_, d, g_, w_))
        curve_state("curve", "hard")
        check(not bad_, "GP. dealt(d) / taken(d) = the mirror for d = -50 ... +100 with 4 settings (%d): %s" % (n_, bad_[:3]))
        named = {0: (1.0, 1.0), 5: (1.0, 1.0), 10: (0.875, 1.075), 13: (0.8, 1.12), 20: (0.625, 1.225), 29: (0.4, 1.36), 40: (0.4, 1.5), 100: (0.4, 1.5), -20: (1.0, 1.0)}
        check(all(abs(float(GapC.dealt(d)) - a) < 1e-12 and abs(float(GapC.taken(d)) - b) < 1e-12 for d, (a, b) in named.items()),
              "GP. spec 3.1 named values: +10 x0.875 / x1.075, +13 (Skyy's Yeti) x0.80 / x1.12, +20 x0.625 / x1.225, +29 x0.40 (floor), cap x1.5 from +39, below = x1")
        # the class level cache
        BR = Lvl.bridge()
        LEV = {}
        CALLS = [0]

        @JImplements("java.util.function.Function")
        class SkillFn(object):
            @JOverride
            def apply(self, o):
                CALLS[0] += 1
                v = LEV.get(str(o[0]))
                if v == "throw":
                    raise RuntimeError("boom")
                return None if v is None else Integer.valueOf(v)
        old_f, old_k = BR.get("skill:fn:level"), None
        u1, u2, u3 = UUID.fromString("00000000-0000-0000-0000-00000000c001"), UUID.fromString("00000000-0000-0000-0000-00000000c002"), UUID.fromString("00000000-0000-0000-0000-00000000c003")
        try:
            GapC.CACHE.clear()
            BR.remove("skill:fn:level")
            BR.put("class:skill:" + str(u1), "Divinity")
            check(int(GapC.readLevel(u1)) == 0 and int(GapC.readLevel(u2)) == -1, "GP. readLevel: no skill:fn:level = 0 (unknown); no class:skill = -1 (no class)")
            BR.put("skill:fn:level", SkillFn())
            LEV[str(u1)] = 21
            t0 = 1000000
            check(int(GapC.level(u1, JLong(t0))) == 21 and CALLS[0] == 1, "GP. a class level read (Divinity 21)")
            LEV[str(u1)] = 25
            check(int(GapC.level(u1, JLong(t0 + 1999))) == 21 and CALLS[0] == 1, "GP. cached for 2 s (a level-up counts within 2 s, no read per hit)")
            check(int(GapC.level(u1, JLong(t0 + 2000))) == 25 and CALLS[0] == 2, "GP. re-read after 2 s -> 25")
            LEV[str(u1)] = 0
            check(int(GapC.level(u1, JLong(t0 + 4100))) == 25, "GP. a 0 read (unknown) never overwrites a cached good level (F6)")
            LEV[str(u1)] = "throw"
            check(int(GapC.level(u1, JLong(t0 + 6200))) == 25, "GP. a failing read (the function throws) keeps the good level too")
            check(int(GapC.gapOf(40, u1, JLong(t0 + 6300))) == 15, "GP. gapOf(Lv 40 mob, a level-25 player) = +15")
            LEV[str(u2)] = 30
            check(int(GapC.level(u2, JLong(t0))) == -1 and int(GapC.gapOf(60, u2, JLong(t0 + 5000))) == -2147483648,
                  "GP. a player with no class (no class:skill) -> no gap, whatever skill:fn:level says")
            BR.put("class:skill:" + str(u3), "Sorcery")
            LEV[str(u3)] = 0
            check(int(GapC.gapOf(60, u3, JLong(t0))) == -2147483648, "GP. a class level of 0 with nothing cached = unknown = no gap")
            Cfg14.GAP_ON = False
            check(int(GapC.gapOf(60, u1, JLong(t0 + 9000))) == -2147483648, "GP. part.gap off -> no gap")
            Cfg14.GAP_ON = True
            check(int(GapC.gapOf(0, u1, JLong(t0 + 9000))) == -2147483648, "GP. a mob without a level -> no gap")
            # the /mobs info text for a band 8-12 above a Divinity 21 player (spec 7.6 step 5)
            check(str(GapC.bandText(8, 12)) == " - level gap: you deal 83-93%, they hit you for 105-111%" and str(GapC.bandText(2, 5)) == ""
                  and str(GapC.bandText(3, 9)) == " - level gap: you deal 90-98%, they hit you for 101-106%",
                  "GP. the band text: 8-12 above -> %r; 2-5 above (free) -> ''; 3-9 above (from +6) -> %r" % (str(GapC.bandText(8, 12)), str(GapC.bandText(3, 9))))
        finally:
            BR.remove("class:skill:" + str(u1))
            BR.remove("class:skill:" + str(u3))
            if old_f is not None:
                BR.put("skill:fn:level", old_f)
            else:
                BR.remove("skill:fn:level")
            GapC.CACHE.clear()
        print("GP. level gap: %d dealt / taken = mirror, the spec's named values; class level cache (2 s, unknown 0, no class, F6, throwing read), band text" % n_)

    # ---- stand-in engine plumbing for DM / SR: module singletons with our own component types, refs, a CommandBuffer, an ArchetypeChunk
    PLUMB = {}

    def plumbing():
        """module singletons pointed at fresh component types (put back by unplumb); the stand-in classes are made once per JVM"""
        CTc = JClass("com.hypixel.hytale.component.ComponentType")
        EMod = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        UVc = JClass("com.hypixel.hytale.server.core.universe.Universe")
        ESModc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
        CPp = JClass("javassist.ClassPool")(False)
        CPp.appendSystemPath()
        CPp.appendClassPath(B.SERVER_JAR)
        P = {"saved": [(jfield(EMod, "instance"), jfield(EMod, "instance").get(None)), (jfield(UVc, "instance"), jfield(UVc, "instance").get(None)),
                       (jfield(ESModc, "instance"), jfield(ESModc, "instance").get(None))]}
        T_ = dict((k, U.allocateInstance(CTc.class_)) for k in ("uuid", "player", "esm", "npc", "plate", "wsup"))
        # EntityModule: getComponentType(NPCEntity.class) answers our npc type (a subclass; everything else = the real fields)
        if "EMT" not in PLUMB:
            em = CPp.makeClass("com.hypixel.hytale.server.core.modules.entity.SkyyMobsTestEntityModule", CPp.get(EMod.class_.getName()))
            em.addField(CtField.make("public com.hypixel.hytale.component.ComponentType npcT;", em))
            em.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.ComponentType getComponentType(Class c) { return this.npcT; }", em))
            PLUMB["EMT"] = em.toClass(EMod.class_)
        EMT = PLUMB["EMT"]
        emi = U.allocateInstance(EMT)
        jfield(EMod, "uuidComponentType").set(emi, T_["uuid"])
        jfield(EMod, "nameplateComponentType").set(emi, T_["plate"])
        jfield(JClass(EMT.getName()), "npcT").set(emi, T_["npc"])
        jfield(EMod, "instance").set(None, emi)
        uv = U.allocateInstance(UVc.class_)
        jfield(UVc, "playerRefComponentType").set(uv, T_["player"])
        jfield(UVc, "instance").set(None, uv)
        esm_ = U.allocateInstance(ESModc.class_)
        jfield(ESModc, "entityStatMapComponentType").set(esm_, T_["esm"])
        jfield(ESModc, "instance").set(None, esm_)
        # CommandBuffer.getComponent(ref, type) / ArchetypeChunk.getReferenceTo(i) / Holder.getComponent(type) stand-ins
        if "BUF" in PLUMB:
            P.update(BUF=PLUMB["BUF"], CHK=PLUMB["CHK"], HOLD=PLUMB["HOLD"], T=T_)
            return P
        cb = CPp.makeClass("com.hypixel.hytale.component.SkyyMobsTestBuffer", CPp.get("com.hypixel.hytale.component.CommandBuffer"))
        cb.addField(CtField.make("public java.util.IdentityHashMap comps;", cb))
        cb.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {"
                                      " java.util.IdentityHashMap m = (java.util.IdentityHashMap) this.comps.get(r); return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t); }", cb))
        P["BUF"] = JClass(cb.toClass(JClass("com.hypixel.hytale.component.CommandBuffer").class_).getName())
        ch = CPp.makeClass("com.hypixel.hytale.component.SkyyMobsTestChunk", CPp.get("com.hypixel.hytale.component.ArchetypeChunk"))
        ch.addField(CtField.make("public com.hypixel.hytale.component.Ref ref;", ch))
        ch.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return this.ref; }", ch))
        P["CHK"] = JClass(ch.toClass(JClass("com.hypixel.hytale.component.ArchetypeChunk").class_).getName())
        hd = CPp.makeClass("com.hypixel.hytale.component.SkyyMobsTestHolder", CPp.get("com.hypixel.hytale.component.Holder"))
        hd.addField(CtField.make("public java.util.IdentityHashMap comps;", hd))
        hd.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) this.comps.get(t); }", hd))
        hd.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component ensureAndGetComponent(com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) this.comps.get(t); }", hd))
        hd.addMethod(CtNewMethod.make("public boolean tryRemoveComponent(com.hypixel.hytale.component.ComponentType t) { return this.comps.remove(t) != null; }", hd))
        P["HOLD"] = JClass(hd.toClass(JClass("com.hypixel.hytale.component.Holder").class_).getName())
        P["T"] = T_
        PLUMB.update(BUF=P["BUF"], CHK=P["CHK"], HOLD=P["HOLD"])
        return P

    def unplumb(P):
        for f_, v_ in P["saved"]:
            f_.set(None, v_)

    REFc = JClass("com.hypixel.hytale.component.Ref")
    IdHM = JClass("java.util.IdentityHashMap")

    def mkref(i):
        r_ = U.allocateInstance(REFc.class_)
        jfield(REFc, "index").setInt(r_, i)
        return r_

    def mk_uuidc(u):
        UC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
        o = U.allocateInstance(UC.class_)
        jfield(UC, "uuid").set(o, u)
        return o

    def mk_player(u):
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        o = U.allocateInstance(PRc.class_)
        jfield(PRc, "uuid").set(o, u)
        return o

    def section_dm():
        """DM: GapDamage + LevelDamage.handle on REAL engine Damage objects (Damage + Damage$EntitySource / Damage$ProjectileSource), through a
        stand-in CommandBuffer / ArchetypeChunk and the engine's own getComponentType calls (module singletons pointed at our types)"""
        P = plumbing()
        try:
            T_ = P["T"]
            DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
            ESRC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
            PSRC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
            buf = U.allocateInstance(P["BUF"].class_)
            buf.comps = IdHM()
            chunk = U.allocateInstance(P["CHK"].class_)
            ents = {}

            def ent(name, idx, uuid=None, player=False, statmap=None):
                r_ = mkref(idx)
                m_ = IdHM()
                if uuid is not None:
                    m_.put(T_["uuid"], mk_uuidc(uuid))
                if player:
                    m_.put(T_["player"], mk_player(uuid))
                if statmap is not None:
                    m_.put(T_["esm"], statmap)
                buf.comps.put(r_, m_)
                ents[name] = r_
                return r_
            uP, uP2, uNoC = UUID.fromString("00000000-0000-0000-0000-0000000d0001"), UUID.fromString("00000000-0000-0000-0000-0000000d0002"), UUID.fromString("00000000-0000-0000-0000-0000000d0003")
            uM30, uM24, uM1, uMun, uPet, uM25, uM20 = [UUID.fromString("00000000-0000-0000-0000-0000000e00%02d" % i) for i in range(1, 8)]
            pmap = newmap()
            pmap.mods.put("Base", SMOc(MTG.MAX, CAL.ADDITIVE, JFloat(100.0)))           # a player with 200 max Health
            pmap.setVal(JFloat(200.0))
            ent("player", 1, uP, player=True, statmap=pmap)
            ent("player2", 2, uP2, player=True, statmap=pmap)
            ent("noclass", 3, uNoC, player=True, statmap=pmap)
            for nm_, i_, u_ in (("m30", 10, uM30), ("m24", 11, uM24), ("m1", 12, uM1), ("mun", 13, uMun), ("pet", 14, uPet), ("m25", 15, uM25), ("m20", 16, uM20)):
                ent(nm_, i_, u_)
            ent("arrow", 20)
            ent("gone", -2147483648)
            MOBS_ = Lvl.MOBS
            MOBS_.clear()
            for u_, L_, base_ in ((uM30, 30, 226.0), (uM24, 24, 103.0), (uM1, 1, 103.0), (uM25, 25, 226.0), (uM20, 20, 226.0)):
                i_ = MInfo()
                i_.uuid, i_.level, i_.world, i_.role = u_, L_, "default", "Yeti"
                i_.base = base_
                MOBS_.put(u_, i_)
            BR = Lvl.bridge()
            LEV = {str(uP): 20, str(uP2): 20}

            @JImplements("java.util.function.Function")
            class SkillFn(object):
                @JOverride
                def apply(self, o):
                    return Integer.valueOf(LEV.get(str(o[0]), 0))
            old_f = BR.get("skill:fn:level")
            BR.put("skill:fn:level", SkillFn())
            BR.put("class:skill:" + str(uP), "Divinity")
            BR.put("class:skill:" + str(uP2), "Sorcery")
            GapC.CACHE.clear()
            curve_state("curve", "hard")
            gd = JClass(PKG + "GapDamage")(False)
            ld = JClass(PKG + "LevelDamage")(False)

            def hit(system, att, vic, amount, proj=False, cancel=False):
                src = PSRC(ents[att], ents["arrow"]) if proj else ESRC(ents[att])
                d_ = DMGc(src, JInt(0), JFloat(amount))
                if cancel:
                    d_.setCancelled(True)
                chunk.ref = ents[vic]
                system.handle(0, chunk, None, buf, d_)
                return float(d_.getAmount())
            # ---- GapDamage: a player's hits on levelled mobs (player Lv 20)
            A = 100.0
            cases = [("player Lv 20 -> Lv 30 mob (+10)", "player", "m30", False, False, f32(A * 0.875)),
                     ("arrow (ProjectileSource: the shooter) -> Lv 30 mob", "player", "m30", True, False, f32(A * 0.875)),
                     ("player -> Lv 24 mob (+4, free)", "player", "m24", False, False, A),
                     ("player -> Lv 25 mob (+5, free)", "player", "m25", False, False, A),
                     ("player -> an unlevelled mob", "player", "mun", False, False, A),
                     ("player -> player", "player", "player2", False, False, A),
                     ("a pet / summon (no PlayerRef) -> Lv 30 mob", "pet", "m30", False, False, A),
                     ("a levelled mob -> another mob", "m30", "m24", False, False, A),
                     ("a player with no class -> Lv 30 mob", "noclass", "m30", False, False, A),
                     ("a cancelled hit (DamageLock)", "player", "m30", False, True, A),
                     ("an attacker ref that is gone", "gone", "m30", False, False, A)]
            for what, att, vic, proj, canc, want in cases:
                got = hit(gd, att, vic, A, proj, canc)
                check(got == want, "DM. GapDamage: %s: %s -> %s (want %s)" % (what, A, got, want))
            LEV[str(uP)] = 0          # a 0 read now: the cached 20 stays (and the 2 s cache holds it anyway)
            GapC.CACHE.clear()
            check(hit(gd, "player", "m30", A) == A, "DM. GapDamage: class level 0 with nothing cached = unknown = full damage")
            LEV[str(uP)] = 20
            GapC.CACHE.clear()
            hit(gd, "player", "m30", A)
            LEV[str(uP)] = 0
            for k_ in list(GapC.CACHE.keySet()):
                v_ = GapC.CACHE.get(k_)
                v_[1] = v_[1] - 5000
            check(hit(gd, "player", "m30", A) == f32(A * 0.875), "DM. GapDamage: a 0 read after the cache ran out keeps the good level 20 (F6)")
            LEV[str(uP)] = 20
            GapC.CACHE.clear()
            Cfg14.GAP_ON = False
            check(hit(gd, "player", "m30", A) == A, "DM. GapDamage: part.gap off -> full damage")
            Cfg14.GAP_ON = True
            check(hit(gd, "player", "m30", 0.0) == 0.0, "DM. GapDamage: a 0 hit stays 0")
            # ---- LevelDamage: a levelled mob's hits (Hard curve: Lv 30 x3.03 damage)
            dm30, dm25, dm20 = float(Cfg14.dmgMult(30)), float(Cfg14.dmgMult(25)), float(Cfg14.dmgMult(20))
            check(dm30 == f32(3.03), "DM. (Hard curve: Lv 30 damage x3.03)")
            got = hit(ld, "m30", "player", 10.0)
            check(got == f32(10.0 * f32(3.03) * 1.075), "DM. LevelDamage: Lv 30 mob -> a Lv 20 player: x3.03 x taken(+10) 1.075 = %s" % got)
            got = hit(ld, "m30", "m24", 10.0)
            check(got == f32(f32(10.0) * f32(3.03)), "DM. LevelDamage: mob -> mob: 0.1.3's level multiplier only (%s)" % got)
            got = hit(ld, "m30", "pet", 10.0)
            check(got == f32(f32(10.0) * f32(3.03)), "DM. LevelDamage: mob -> a pet (no PlayerRef): 0.1.3's level multiplier only")
            got = hit(ld, "m30", "noclass", 10.0)
            check(got == f32(f32(10.0) * f32(3.03)), "DM. LevelDamage: mob -> a player with no class: the level multiplier, no gap (%s)" % got)
            got = hit(ld, "m24", "player", 10.0)
            check(got == f32(f32(10.0) * f32(float(Cfg14.dmgMult(24)))), "DM. LevelDamage: a mob +4 above the player: no gap")
            check(hit(ld, "m1", "player", 10.0) == 10.0 and hit(ld, "player", "m30", 10.0) == 10.0 and hit(ld, "m30", "player", 10.0, cancel=True) == 10.0,
                  "DM. LevelDamage: a Lv 1 mob (early return), a player attacker, a cancelled hit: untouched")
            # all 0.1.4 knobs off for a player victim = 0.1.3's float product exactly
            Cfg14.GAP_ON = False
            for a_ in (1.0, 7.3, 10.0, 26.999, 1234.5):
                if hit(ld, "m30", "player", a_) != f32(f32(a_) * f32(3.03)):
                    check(False, "DM. LevelDamage: knobs off, %s -> not 0.1.3's float product" % a_)
            OKS[0] += 1
            Cfg14.GAP_ON = True
            # the damage floor (spec 1.6; players only, mobs above Lv 20, ramped Lv 21-29, full from 30); base 226 (Yeti)
            Cfg14.DMG_FLOOR = 15
            got30 = hit(ld, "m30", "player", 10.0)
            check(got30 == f32(0.15 * 226.0 * dm30 * 1.075), "DM. damage floor 15%%: Lv 30 Yeti (226) hit 10 -> at least 33.9 before x3.03 x1.075 = %s" % got30)
            got25 = hit(ld, "m25", "player", 10.0)
            check(got25 == f32(0.15 * 226.0 * 0.5 * dm25), "DM. damage floor: Lv 25 = half ramp (16.95), no gap (+5): %s" % got25)
            check(hit(ld, "m20", "player", 10.0) == f32(f32(10.0) * f32(dm20)), "DM. damage floor: Lv 20 -> no floor (the Lv 1-20 part stays today's)")
            check(hit(ld, "m30", "player", 50.0) == f32(50.0 * dm30 * 1.075), "DM. damage floor: a hit above the floor is unchanged")
            check(hit(ld, "m30", "m24", 10.0) == f32(f32(10.0) * f32(dm30)), "DM. damage floor: never on mob -> mob")
            check(hit(ld, "m30", "player", 0.0) == 0.0, "DM. damage floor: a 0 hit stays 0")
            MOBS_.get(uM30).base = 36.0
            check(hit(ld, "m30", "player", 1.0) == f32(0.15 * 50.0 * dm30 * 1.075), "DM. damage floor: a 36-HP mob uses its Lv 1 health 50 (the health floor)")
            MOBS_.get(uM30).base = -1.0
            check(hit(ld, "m30", "player", 1.0) == f32(1.0 * dm30 * 1.075), "DM. damage floor: an unknown base -> no floor")
            MOBS_.get(uM30).base = 226.0
            Cfg14.DMG_FLOOR = 0
            # one hit at most (spec 1.6): the player's max Health 200 -> 60% = 120
            Cfg14.HIT_CAP = 60
            check(hit(ld, "m30", "player", 100.0) == 120.0 and hit(ld, "m30", "player", 10.0) == f32(10.0 * dm30 * 1.075),
                  "DM. one hit at most 60%%: a 100 hit (-> 325.7) is capped at 120 (60%% of 200); a small hit untouched")
            check(hit(ld, "m30", "m24", 100.0) == f32(f32(100.0) * f32(dm30)), "DM. one hit at most: never on mob -> mob")
            Cfg14.HIT_CAP = 0
            # GapDamage + another Filter multiplier in both orders (SkyyGear / SkyySkills / SkyyArmory are multipliers too): same within 1 ulp
            worst = 0
            for a_ in (3.0, 10.0, 17.7, 123.4):
                x1 = f32(hit(gd, "player", "m30", a_) * f32(1.3))
                x2 = hit(gd, "player", "m30", f32(f32(a_) * f32(1.3)))
                worst = max(worst, abs(x1 - x2) / max(1e-9, abs(x1)))
            check(worst < 2e-7, "DM. the gap and another multiplier in either order give the same hit (worst relative difference %.2g)" % worst)
            print("DM. damage on real engine Damage objects: GapDamage %d cases + F6 / part off / 0 hits; LevelDamage: gap, mob -> mob / pet / no class, "
                  "early returns, knobs off = 0.1.3, damage floor (Lv 20 / 25 / 30, floor base, unknown base), one hit at most, both orders" % len(cases))
        finally:
            try:
                Lvl.MOBS.clear()
                BR_ = Lvl.bridge()
                for u_ in ("00000000-0000-0000-0000-0000000d0001", "00000000-0000-0000-0000-0000000d0002"):
                    BR_.remove("class:skill:" + u_)
                BR_.remove("skill:fn:level")
                GapC.CACHE.clear()
                Cfg14.DMG_FLOOR, Cfg14.HIT_CAP, Cfg14.GAP_ON = 0, 0, True
            finally:
                unplumb(P)

    def section_sr():
        """SR: scale.role (spec 1.6) - the loader (exact id, a hand-typed Prefix* line, level 0 = off, bad lines), roleLevel / roleX / roleKey,
        whyNotRole; MobLevel.onAdd through a stand-in Holder: an EXCLUDED boss with a row gets that level + health x on top of the curve +
        its plate; the row removed -> stripped on the next add; refreshOne keeps the factor"""
        curve_state("curve", "hard", extra={"scale.role.Goblin_Duke": "30,2", "scale.role.Trork_Chief*": "25", "scale.role.Dragon_Fire": "0,3",
                                            "scale.role.Bad_One": "abc", "scale.role.Skeleton_Elite": "120,1"})
        check(int(Cfg14.roleLevel("Goblin_Duke")) == 30 and float(Cfg14.roleX("Goblin_Duke")) == 2.0 and int(Cfg14.roleLevel("goblin_duke")) == 30
              and int(Cfg14.roleLevel("Trork_Chieftain")) == 25 and float(Cfg14.roleX("Trork_Chieftain")) == 1.0
              and int(Cfg14.roleLevel("Dragon_Fire")) == 0 and int(Cfg14.roleLevel("Bad_One")) == 0 and int(Cfg14.roleLevel("Skeleton_Elite")) == 0
              and int(Cfg14.roleLevel("Goblin_Duke_Phase2")) == 0, "SR. rows: exact id (any case) 30 x2, a hand-typed Trork_Chief* 25 (health x 1), level 0 = off, "
              "bad lines skipped (abc, level 120)")
        check(Cfg14.whyNot("HOSTILE", "Goblin_Duke") is not None and Cfg14.whyNotRole("HOSTILE", "Goblin_Duke") is None and Cfg14.whyNotRole("", "Goblin_Duke") is None
              and Cfg14.whyNotRole("HOSTILE", "Dragon_Fire") is not None, "SR. a row wins over Never level these (and an unknown attitude); a level-0 row does not")
        Cfg14.MAX_LEVEL = 20
        check(int(Cfg14.roleLevel("Goblin_Duke")) == 20, "SR. levels.max still caps a fixed level")
        Cfg14.MAX_LEVEL = 100
        P = plumbing()
        try:
            T_ = P["T"]
            NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
            NPLc = JClass("com.hypixel.hytale.server.core.entity.nameplate.Nameplate")

            def holder(role, uuid, base):
                h_ = U.allocateInstance(P["HOLD"].class_)
                h_.comps = IdHM()
                npc = U.allocateInstance(NPCc.class_)
                jfield(NPCc, "roleName").set(npc, role)
                m_ = fresh(base)
                pl_ = U.allocateInstance(NPLc.class_)
                jfield(NPLc, "text").set(pl_, "")
                h_.comps.put(T_["npc"], npc)
                h_.comps.put(T_["esm"], m_)
                h_.comps.put(T_["uuid"], mk_uuidc(uuid))
                h_.comps.put(T_["plate"], pl_)
                return h_, m_, pl_
            uD = UUID.fromString("00000000-0000-0000-0000-0000000f0001")
            h_, m_, pl_ = holder("Goblin_Duke", uD, 226.0)
            Lvl.onAdd(h_, True, None)
            i_ = Lvl.MOBS.get(uD)
            want = f32(float(Cfg14.hpMult(30)) * 2.0)
            check(i_ is not None and int(i_.level) == 30 and str(i_.step) == "role" and str(i_.key) == "scale.role.Goblin_Duke" and float(i_.rx) == 2.0
                  and float(i_.base) == 226.0, "SR. onAdd: the EXCLUDED Goblin_Duke with a row -> Lv 30, step role, key scale.role.Goblin_Duke, rx 2, base 226")
            mod_ = m_.mods.get("skyymobs_lv30")
            check(mod_ is not None and float(mod_.getAmount()) == want and abs(float(m_.maxNow()) - 226.0 * want) < 0.05 and float(m_.val()) == float(m_.maxNow()),
                  "SR. its health = 226 x the Hard curve x5.6 x 2 = %.0f HP (spawn: full)" % float(m_.maxNow()))
            check(str(pl_.getText()) == "[Lv 30] Goblin Duke", "SR. its plate: %r" % str(pl_.getText()))
            check(bool(Lvl.refreshOne(m_, 0, 30, float(Cfg14.roleX("Goblin_Duke")))) is False and float(m_.mods.get("skyymobs_lv30").getAmount()) == want,
                  "SR. the live re-apply keeps the role factor (no change)")
            m_.setVal(JFloat(float(m_.maxNow()) * 0.5))
            curve_state("curve", "hard", extra={"scale.role.Goblin_Duke": "30,3"})
            check(bool(Lvl.refreshOne(m_, 0, 30, float(Cfg14.roleX("Goblin_Duke")))) and abs(float(m_.val()) / float(m_.maxNow()) - 0.5) < 1e-5
                  and abs(float(m_.maxNow()) - 226.0 * f32(float(Cfg14.hpMult(30)) * 3.0)) < 0.05, "SR. a new health x (3) re-applies, the health percent kept")
            # the row changes the level: the next add re-stamps the save slot
            curve_state("curve", "hard", extra={"scale.role.Goblin_Duke": "35,1"})
            h2, m2, pl2 = holder("Goblin_Duke", uD, 226.0)
            m2.mods.putAll(m_.mods)
            Lvl.onAdd(h2, False, None)
            check(int(Lvl.savedLevel(m2, 0)) == 35 and m2.mods.get("skyymobs_lv30") is None and int(Lvl.MOBS.get(uD).level) == 35,
                  "SR. a changed row (35) re-stamps the saved level on the next add (skyymobs_lv30 -> skyymobs_lv35)")
            # the row removed: the boss is in Never level these again -> stripped (modifier + plate) on the next add
            curve_state("curve", "hard")
            h3, m3, pl3 = holder("Goblin_Duke", uD, 226.0)
            m3.mods.putAll(m2.mods)
            pl3.setText("[Lv 35] Goblin Duke")
            Lvl.onAdd(h3, False, None)
            check(int(Lvl.savedLevel(m3, 0)) == -1 and Lvl.MOBS.get(uD) is None and h3.comps.get(T_["plate"]) is None,
                  "SR. the row removed -> the excluded boss loses its level, modifier and plate on the next add")
            # part.levels off: a fixed role with no saved level gets none; with a saved level it keeps the row's
            curve_state("curve", "hard", extra={"scale.role.Goblin_Duke": "30,1", "part.levels": "false"})
            h4, m4, pl4 = holder("Goblin_Duke", UUID.fromString("00000000-0000-0000-0000-0000000f0002"), 226.0)
            Lvl.onAdd(h4, True, None)
            check(int(Lvl.savedLevel(m4, 0)) == -1, "SR. Mob levels off: a fixed role with no saved level gets none")
            # inspect's health line with the role factor
            curve_state("curve", "hard", extra={"scale.role.Goblin_Duke": "30,2"})
            m5 = fresh(226.0)
            Lvl.setMult(m5, 0, 30, True, False, 2.0)
            hl_ = str(JClass(PKG + "MobCmds").healthLine(m5, 0, 30, 2.0))
            check(hl_.startswith("=Health x11.2 (2531 / 2531 HP)") and "Fixed level by role health x2" in hl_ and hl_.endswith("damage x3.03 - Hard curve, Lv 30"),
                  "SR. /mobs inspect health line: %r" % hl_)
            print("SR. scale.role: rows (exact, Prefix*, off, bad), whyNotRole, onAdd through a stand-in Holder (excluded boss levelled + x2 + plate, "
                  "re-apply, re-stamp, strip, part off), the inspect line")
        finally:
            Lvl.MOBS.clear()
            unplumb(P)
            curve_state("curve", "hard")

    def section_if():
        """IF: mob:fn:info (spec 7.3) - shape, values, null cases, thread safety; xpMult Hard 1, Easy 0.62 at Lv 40, Custom 20/8 Per level 1"""
        fn_ = InfoFnC()
        MOBS_ = Lvl.MOBS
        MOBS_.clear()

        def mob(u_, L_, base_, world="default", role="Yeti", rx=1.0):
            m_ = fresh(base_) if base_ > 0 else newmap()
            i_ = Lvl.apply(None, None, None, None, m_, u_, None, world, role, L_, True, "biome", None) if base_ > 0 else None
            if i_ is None:
                i_ = MInfo()
                i_.uuid, i_.level, i_.world, i_.role = u_, L_, world, role
                MOBS_.put(u_, i_)
            if rx != 1.0:
                i_.rx = rx
            return i_, m_

        def call(o):
            return fn_.apply(o)
        uY, uC, uZ = UUID.fromString("00000000-0000-0000-0000-000000100001"), UUID.fromString("00000000-0000-0000-0000-000000100002"), UUID.fromString("00000000-0000-0000-0000-000000100003")
        res_ = {}
        for d_, want_xm in (("hard", 1.0), ("easy", 8.19 / 13.18), ("normal", 10.69 / 13.18), ("custom", 1.0)):
            curve_state("curve", d_)
            MOBS_.clear()
            mob(uY, 40, 226.0)
            mob(uC, 40, 36.0)
            r_ = call(JArray(JObject)([JStr("default"), uY]))
            vals = [int(r_[0])] + [float(x) for x in r_[1:]]
            res_[d_] = vals
            check(len(r_) == 6 and isinstance(r_[0], JClass("java.lang.Integer")) and all(isinstance(x, JClass("java.lang.Double")) for x in r_[1:]),
                  "IF. %s: Object[6] {Integer, Double x5}" % d_)
            check(vals[0] == 40 and vals[1] == 226.0 and vals[2] == 226.0 and vals[3] == float(Cfg14.hpMult(40)) and vals[4] == float(Cfg14.dmgMult(40))
                  and abs(vals[5] - want_xm) < 1e-6, "IF. %s curve, Lv 40 Yeti: level 40, base 226, xpBase 226, hpMult %.4f, dmgMult %.4f, xpMult %.4f (want %.4f)" % (
                      d_, vals[3], vals[4], vals[5], want_xm))
            r2 = call(uC)
            check(float(r2[1]) == 36.0 and float(r2[2]) == 50.0, "IF. %s: a 36-HP mob: base 36, xpBase 50 (the health floor = its Lv 1 health)" % d_)
        check(abs(res_["easy"][5] - 0.62) < 0.005, "IF. the spec's 'Easy x0.62 at Lv 40': %.4f" % res_["easy"][5])
        # Per level: Skyy's old Custom 20 / 8 (caps 20 / 6) never pays more than Hard; Easy Lv 20 = 1.76 / 2.52
        curve_state("linear", "custom", extra={"strength.hp": "20", "strength.dmg": "8", "strength.hpCap": "20", "strength.dmgCap": "6"})
        MOBS_.clear()
        mob(uY, 32, 226.0)
        r_ = call(uY)
        check(abs(float(r_[3]) - f32(7.2)) < 1e-6 and float(r_[5]) == 1.0, "IF. Per level Custom 20%% / 8%% (caps 20 / 6), Lv 32: hpMult x7.2, xpMult 1 (never above Hard)")
        curve_state("linear", "easy")
        MOBS_.clear()
        mob(uY, 20, 226.0)
        check(abs(float(call(uY)[5]) - f32(1.76) / f32(2.52)) < 1e-6, "IF. Per level Easy Lv 20: xpMult 1.76 / 2.52")
        # the scale.role factor is in hpMult, not in xpMult
        curve_state("curve", "hard")
        MOBS_.clear()
        mob(uY, 30, 226.0, rx=2.0)
        r_ = call(uY)
        check(float(r_[3]) == float(Cfg14.hpMult(30)) * 2.0 and float(r_[5]) == 1.0, "IF. a scale.role x2 mob: hpMult x2 on top, xpMult still 1")
        # after a live re-apply (a table edit) the answer follows the settings now
        curve_state("curve", "hard", extra={"curve.hp.hard.30": "6"})
        check(float(call(uY)[3]) == 12.0, "IF. after a table edit hpMult follows the setting now (6 x 2)")
        curve_state("curve", "hard")
        # null cases
        mob(uZ, 7, -1.0)
        nulls = [("unknown uuid", UUID.randomUUID()), ("wrong world", JArray(JObject)([JStr("other"), uY])), ("a String", "x"), ("null", None),
                 ("an empty array", JArray(JObject)(0)), ("base unknown", uZ)]
        for what, o in nulls:
            check(call(o) is None, "IF. null for %s" % what)
        MOBS_.get(uZ).level = 0
        check(call(uZ) is None, "IF. null for level 0")
        check(call(JArray(JObject)([uY])) is not None and call(JArray(JObject)([None, uY])) is not None, "IF. a bare UUID in a 1-element array / a null world: answered")
        # 8 threads x 2000 calls while the map changes
        errs = []

        def hammer(k):
            try:
                for i in range(2000):
                    r = fn_.apply(uY if i % 3 else UUID.randomUUID())
                    if r is not None and int(r[0]) != 30:
                        errs.append(("bad", int(r[0])))
                    if i % 50 == 0:
                        MOBS_.put(UUID.randomUUID(), MInfo())
            except Exception as ex:
                errs.append(str(ex))
        ths = [threading.Thread(target=hammer, args=(k,)) for k in range(8)]
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        check(not errs, "IF. 8 threads x 2000 calls while MOBS changes: no error / bad value (%s)" % errs[:3])
        MOBS_.clear()
        print("IF. mob:fn:info: Object[6] contract on 4 difficulties (xpMult Hard 1, Easy %.3f, Normal %.3f, Custom 1), floor xpBase, Per level Custom 20/8 = 1, "
              "role factor in hpMult only, follows a table edit, %d null cases, 16,000 threaded calls" % (res_["easy"][5], res_["normal"][5], len(nulls) + 1))

    def section_wn():
        """WN: the 15 s WARN (MobScanTask.curveWarn) both ways through stand-in gear:fn:curve functions"""
        BR = Lvl.bridge()
        old_g = BR.get("gear:fn:curve")
        CUR = {}

        @JImplements("java.util.function.Function")
        class GearFn(object):
            @JOverride
            def apply(self, o):
                if CUR.get("throw"):
                    raise RuntimeError("boom")
                if str(o[0]) != "F":
                    return None
                return JDouble.valueOf(py_eval(CUR["F"], int(o[1])))
        try:
            BR.remove("gear:fn:curve")
            curve_state("curve", "hard")
            w1 = ScanC.curveWarn()
            check(w1 is not None and "gear:fn:curve is missing" in str(w1) and "Strength shape to Per level" in str(w1), "WN. curve + no SkyyGear curve -> WARN: %s" % w1)
            BR.put("gear:fn:curve", GearFn())
            CUR["F"] = F_OLD14
            w2 = ScanC.curveWarn()
            check(w2 is not None and "flat" in str(w2) and "F(40) 3 vs F(20) 2.33" in str(w2), "WN. curve + the old flat F (3 vs 2.33) -> WARN: %s" % w2)
            CUR["F"] = F_NEW14
            check(ScanC.curveWarn() is None, "WN. curve + the new steep F (9.6 vs 2.33) -> no WARN")
            curve_state("linear", "hard")
            w3 = ScanC.curveWarn()
            check(w3 is not None and "Per level" in str(w3) and "Strength shape to Level curve" in str(w3), "WN. Per level + the steep F -> WARN: %s" % w3)
            CUR["F"] = F_OLD14
            check(ScanC.curveWarn() is None, "WN. Per level + the flat F -> no WARN")
            CUR["throw"] = True
            curve_state("curve", "hard")
            w4 = ScanC.curveWarn()
            check(w4 is not None, "WN. a throwing gear:fn:curve never throws here (it counts as flat): %s" % w4)
            CUR["throw"] = False
            ScanC().run()
            OKS[0] += 1
        finally:
            BR.remove("gear:fn:curve")
            if old_g is not None:
                BR.put("gear:fn:curve", old_g)
            curve_state("curve", "hard")
        print("WN. the gear-curve WARN: missing / flat / steep x curve / Per level, a throwing function; MobScanTask.run runs it")

    def section_cmd():
        """CMD: the /mobs texts - the inspect health line in curve shape, the gap line, /mobs info's band line (skillLine) with the gap"""
        MC = JClass(PKG + "MobCmds")
        curve_state("curve", "hard")
        m_ = fresh(226.0)
        Lvl.setMult(m_, 0, 34, True, False, 1.0)
        hl_ = str(MC.healthLine(m_, 0, 34))
        check(hl_ == "=Health x7.94 (1795 / 1795 HP), base 226 HP (at or above the 50 HP floor), damage x3.72 - Hard curve, Lv 34",
              "CMD. inspect: Skyy's Lv 34 Yeti on the Hard curve: %r" % hl_)
        curve_state("linear", "hard")
        m2 = fresh(226.0)
        Lvl.setMult(m2, 0, 34, True, False, 1.0)
        check(str(MC.healthLine(m2, 0, 34)).endswith("damage x2.32 - Hard 8% / 4%, caps x6 / x3.5") and "(823 / 823 HP)" in str(MC.healthLine(m2, 0, 34)),
              "CMD. inspect in Per level shape = 0.1.3's text (the same Yeti 823 HP): %r" % str(MC.healthLine(m2, 0, 34)))
        curve_state("curve", "hard")
        BR = Lvl.bridge()
        u_ = UUID.fromString("00000000-0000-0000-0000-000000110001")
        LEV = {"n": 21}

        @JImplements("java.util.function.Function")
        class SkillFn(object):
            @JOverride
            def apply(self, o):
                return Integer.valueOf(LEV["n"])
        old_f = BR.get("skill:fn:level")
        try:
            BR.put("skill:fn:level", SkillFn())
            BR.put("class:skill:" + str(u_), "Divinity")
            GapC.CACHE.clear()
            gl = MC.gapLine(u_, 34)
            check(str(gl) == "=Level gap vs you +13: you deal 80%, it deals 112%", "CMD. inspect gap line (spec 7.2 / test step 4): %r" % gl)
            check(MC.gapLine(u_, 26) is None and MC.gapLine(u_, 10) is None, "CMD. no gap line within the free levels or below you")
            sl = str(MC.skillLine(u_, 29, 33))
            check(sl == "=Your Divinity is 21: these mobs are 8 to 12 levels above you - level gap: you deal 83-93%, they hit you for 105-111%.",
                  "CMD. /mobs info band line with the gap (spec test step 5): %r" % sl)
            check(str(MC.skillLine(u_, 22, 24)) == "=Your Divinity is 21: these mobs are 1 to 3 levels above you.", "CMD. no gap text for a band within the free levels")
            check(str(MC.skillLine(u_, 18, 30)) == "=Your Divinity is 21: your level is inside this range - level gap: you deal 90-98%, they hit you for 101-106%.",
                  "CMD. a band around you whose top is past the free levels: %r" % str(MC.skillLine(u_, 18, 30)))
            check(str(MC.skillLine(u_, 5, 9)) == "=Your Divinity is 21: these mobs are 12 to 16 levels below you.", "CMD. below you: 0.1.3's text")
            Cfg14.GAP_ON = False
            check(str(MC.skillLine(u_, 29, 33)) == "=Your Divinity is 21: these mobs are 8 to 12 levels above you." and MC.gapLine(u_, 34) is None,
                  "CMD. part.gap off: no gap texts (0.1.3's line)")
            Cfg14.GAP_ON = True
        finally:
            BR.remove("class:skill:" + str(u_))
            BR.remove("skill:fn:level")
            if old_f is not None:
                BR.put("skill:fn:level", old_f)
            GapC.CACHE.clear()
        print("CMD. /mobs texts: inspect health line (curve + Per level), the gap line, /mobs info's band line with / without the gap")

    # ---- MobMig14: an independent Python mirror of the spec 6.4 update (files without continued lines)
    def py_m14(text):
        mark, mark_id, role_doc = str(M14.MARK), str(M14.MARK_ID), str(M14.ROLE_DOC)
        groups = [(str(k_), str(t_).split("\n")) for k_, t_ in zip(M14.G_KEY, M14.G_TEXT)]
        raw = text.split("\n")
        body = [x[:-1] if x.endswith("\r") else x for x in raw]
        keys, last_str, lv_max, role_doc_in, diff = set(), -1, -1, False, None
        for i, b_ in enumerate(body):
            t_ = b_.lstrip()
            if t_ == "" or t_[0] in "#!":
                if mark_id in b_:
                    return None
                if b_ == role_doc:
                    role_doc_in = True
                continue
            k_ = re.split(r"\s*[=:]\s*|\s+", t_, 1)[0]
            lk = k_.lower()
            keys.add(lk)
            if lk.startswith("strength."):
                last_str = i
            if lk == "levels.max":
                lv_max = i
            if k_ == "strength.difficulty":
                diff = re.split(r"\s*[=:]\s*|\s+", t_, 1)[1].strip() if len(re.split(r"\s*[=:]\s*|\s+", t_, 1)) > 1 else ""
        shape = None if "strength.shape" in keys else ("linear" if (diff or "").strip().lower() == "custom" else "curve")
        block, added = [mark], {}
        for k_, lines in groups:
            lk = k_.lower()
            if any((x.startswith(lk) if lk.endswith(".") else x == lk) for x in keys):
                continue
            for ln in lines:
                ln = ln.replace("{shape}", shape or "curve")
                block.append(ln)
                if not ln.startswith("#"):
                    a_, b_ = ln.split("=", 1)
                    added[a_] = b_
        if not role_doc_in and lv_max < 0:
            block.append(role_doc)
        crlf = "\r\n" in text
        end_nl = raw[-1] == ""
        xb = (last_str + 1 if last_str >= 0 else (len(raw) - 1 if end_nl else len(raw))) - 1
        out = list(raw)

        def ins(x, lines):
            n = len(out)
            at_end = x >= 0 and x == n - 1
            if x < 0:
                cr = "\r" if crlf else ""
            elif at_end:
                cr = "\r" if crlf else ""
                if crlf and not out[x].endswith("\r"):
                    out[x] = out[x] + "\r"
            else:
                cr = "\r" if out[x].endswith("\r") else ""
            out[x + 1:x + 1] = [ln + ("" if (at_end and j == len(lines) - 1) else cr) for j, ln in enumerate(lines)]
        role_after = not role_doc_in and lv_max >= 0
        if role_after and lv_max > xb:
            ins(lv_max, [role_doc])
        ins(xb, block)
        if role_after and lv_max <= xb:
            ins(lv_max, [role_doc])
        return "\n".join(out), shape, added

    def start14(base):
        """setup()'s order in 0.1.4: MobMig.run, MobMig14.run, MobCfg.load, CfgPub.start -> the two answers"""
        home = os.path.join(base, "Skyy_SkyyMobs")
        Cfg14.DIR = Paths.get(home)
        Cfg14.FILE = Paths.get(os.path.join(home, "config.properties"))
        Cfg14.BANDS = Paths.get(os.path.join(home, "bands.properties"))
        LogC.drop(int(LogC.snap().size()))
        a_ = str(Mig.run(Cfg14.DIR))
        b_ = str(M14.run(Cfg14.DIR))
        Cfg14.load()
        Pub.start(Paths.get(base), None)
        return a_, b_

    def section_mig():
        """MIG: MobMig14 (spec 6.4) - the block contents vs the spec, Skyy's live folder (a scratch COPY) started twice, synthetic files"""
        # the groups = the spec's rows and defaults (typed here), each with one comment line first
        want_add = {"strength.shape": "curve", "strength.dmgFloor": "0", "strength.hitCap": "0", "part.gap": "true", "gap.free": "5", "gap.dealtStep": "2.5",
                    "gap.dealtMin": "40", "gap.takenStep": "1.5", "gap.takenMax": "1.5"}
        for (k_, d_), pts in SPEC13.items():
            for L, v in pts:
                want_add["curve.%s.%s.%d" % (k_, d_, L)] = ("%r" % v)[:-2] if ("%r" % v).endswith(".0") else "%r" % v
        got_add = {}
        for t_ in M14.G_TEXT:
            ls_ = str(t_).split("\n")
            check(ls_[0].startswith("# ") and "=" not in ls_[0] and all(not x.startswith("#") for x in ls_[1:]), "MIG. a group = one comment line + its entries: %r" % ls_[0])
            for x in ls_[1:]:
                a_, b_ = x.split("=", 1)
                got_add[a_] = b_.replace("{shape}", "curve")
        check(got_add == want_add and len(got_add) == 89, "MIG. the block = the spec's 9 rows + 80 curve entries, with the spec's defaults: %s" % sorted(set(got_add.items()) ^ set(want_add.items()))[:4])
        check(str(M14.MARK_ID) == "SkyyMobs 0.1.4 level curve" and str(M14.MARK_ID) in str(M14.MARK) and "=" not in str(M14.MARK) and str(M14.WHAT) == "before the 0.1.4 level curve",
              "MIG. marker / History title")
        # the fresh 0.1.4 default file carries the marker (never updated); 0.1.3's default -> exactly 0.1.4's default (but line 1)
        dcfg = str(Cfg14.DEF_CFG)
        check(M14.update(dcfg) is None, "MIG. the 0.1.4 default file carries the marker -> never updated")
        d13 = str(sfield(pin_cls("MobCfg"), "DEF_CFG"))
        r_ = M14.update(d13)
        check(r_ is not None and str(r_[0]) == dcfg.replace("# SkyyMobs %s settings" % VERSION, "# SkyyMobs %s settings" % PINVER, 1) and str(r_[1]) == "curve",
              "MIG. 0.1.3's default file -> exactly 0.1.4's default (but its first line): the fresh file = an updated old one")
        # ---- Skyy's live folder (a scratch COPY; read-only source), started twice in setup()'s order
        if os.path.isdir(LIVE_DIR):
            base = os.path.join(SCRATCH, "mig14live", "mods")
            shutil.rmtree(os.path.dirname(base), ignore_errors=True)
            os.makedirs(base)
            shutil.copytree(LIVE_DIR, os.path.join(base, "Skyy_SkyyMobs"))
            home = os.path.join(base, "Skyy_SkyyMobs")
            cfgp = os.path.join(home, "config.properties")
            old_b = open(cfgp, "rb").read()
            old_t = old_b.decode("latin-1")
            hist0 = sorted(f_ for f_ in os.listdir(os.path.join(home, "config-history")) if f_.endswith(".bak"))
            log0 = open(os.path.join(home, "config-changes.log"), "rb").read()
            exp_t, exp_shape, exp_add = py_m14(old_t)
            a_, b_ = start14(base)
            new_t = open(cfgp, "rb").read().decode("latin-1")
            check(new_t == exp_t and exp_shape == "curve", "MIG. Skyy's live file (hard, hp 20 / dmg 8, caps 20 / 6, LF) -> exactly the mirror's text (marker + block "
                  "after strength.healOnLoad, the scale.role line after levels.max)")
            check("\r" not in new_t and new_t.endswith("\n"), "MIG. LF line endings kept")
            po, pn = JClass("java.util.Properties")(), JClass("java.util.Properties")()
            po.load(JClass("java.io.StringReader")(old_t))
            pn.load(JClass("java.io.StringReader")(new_t))
            kept_ = all(str(pn.getProperty(k_)) == str(po.getProperty(k_)) for k_ in [str(x) for x in po.stringPropertyNames()])
            check(kept_ and int(pn.size()) == int(po.size()) + 89 and str(pn.getProperty("strength.difficulty")) == "hard"
                  and str(pn.getProperty("strength.hp")) == "20" and str(pn.getProperty("strength.hpCap")) == "20" and str(pn.getProperty("strength.dmgCap")) == "6"
                  and str(pn.getProperty("strength.shape")) == "curve", "MIG. every old value kept (difficulty hard, hp 20, caps 20 / 6 - hand-set), + 89 new keys, strength.shape=curve")
            hist1 = sorted(f_ for f_ in os.listdir(os.path.join(home, "config-history")) if f_.endswith(".bak"))
            newest = os.path.join(home, "config-history", hist1[-1])
            idx_ = open(os.path.join(home, "config-history", "index.log"), "rb").read().decode("utf-8", "replace")
            check(len(hist1) == min(10, len(hist0) + 1) and open(newest, "rb").read() == old_b and "before the 0.1.4 level curve" in idx_,
                  "MIG. History: the old bytes kept as the newest version 'before the 0.1.4 level curve' (KEEP 10: %d -> %d)" % (len(hist0), len(hist1)))
            stop_kit()
            log1 = open(os.path.join(home, "config-changes.log"), "rb").read()
            new_lines = logfields(log1[len(log0):].decode("utf-8")) if log1.startswith(log0) else None
            check(new_lines is not None and len(new_lines) == 1 and new_lines[0][1:] == ["SkyyMobs 0.1.4", "-", "update", "strength.shape", "linear", "curve", "ok"],
                  "MIG. one config-changes.log line strength.shape linear -> curve (SkyyMobs 0.1.4, update, ok) - Undo puts back 0.1.3's numbers: %s" % new_lines)
            check("strength.shape=curve" in b_ and "strength.hpCap=20 / strength.dmgCap=6 kept (hand-set)" in b_ and a_ == "",
                  "MIG. the INFO lines name the shape and the hand-set caps; the 0.1.1 update does nothing (marker): %r" % b_[:200])
            check(bool(Cfg14.CURVE_ON) and str(Cfg14.difficultyText()) == "Hard curve", "MIG. after the update the loader runs the Hard curve")
            check(abs(float(Cfg14.hpMult(34)) - 7.944) < 0.001, "MIG. Skyy's Lv 34 Yeti: x%.3f (spec 7.94)" % float(Cfg14.hpMult(34)))
            # Undo through the kit's own log + set (what Server Setup -> Changes -> Undo does): Per level = 0.1.3's numbers
            r_ = kit_op("set", "strength.shape", "linear", None, None, "yes", "console")
            check(str(r_[0]) == "ok" and not bool(Cfg14.CURVE_ON) and float(Cfg14.hpMult(34)) == f32(1.0 + 0.08 * 33),
                  "MIG. Undo (strength.shape back to linear through the kit) -> 0.1.3's Hard x3.64 at Lv 34 (Skyy's caps 20 do not clip): x%.2f" % float(Cfg14.hpMult(34)))
            kit_op("set", "strength.shape", "curve", None, None, "yes", "console")
            stop_kit()
            snap1 = snapdir(home)
            time.sleep(1.1)
            a2, b2 = start14(base)
            stop_kit()
            snap2 = snapdir(home)
            check(a2 == "" and b2 == "" and snap1 == snap2, "MIG. second start: nothing to do, no byte / time changed in the folder (%s)" % sorted(
                k_ for k_ in set(snap1) | set(snap2) if snap1.get(k_) != snap2.get(k_))[:4])
        else:
            check(False, "MIG. Skyy's live Skyy_SkyyMobs folder not found: %s" % LIVE_DIR)

        # ---- synthetic files through MobMig14.run (History, log, INFO), each = the mirror
        def case(name, text, blocked=False):
            h_ = os.path.join(SCRATCH, "mig14", name, "Skyy_SkyyMobs")
            shutil.rmtree(os.path.dirname(h_), ignore_errors=True)
            os.makedirs(h_)
            p_ = os.path.join(h_, "config.properties")
            if text is not None:
                open(p_, "wb").write(text.encode("latin-1"))
            if blocked:
                open(os.path.join(h_, "config-history"), "wb").write(b"a file where the folder should be")
            LogC.drop(int(LogC.snap().size()))
            msg_ = str(M14.run(Paths.get(h_)))
            Pub.flush()
            nt = open(p_, "rb").read().decode("latin-1") if os.path.exists(p_) else None
            hd = os.path.join(h_, "config-history")
            hist_ = sorted(f_ for f_ in os.listdir(hd) if f_.endswith(".bak")) if os.path.isdir(hd) else []
            lp = os.path.join(h_, "config-changes.log")
            lines_ = logfields(open(lp, "rb").read().decode("utf-8")) if os.path.isfile(lp) else []
            return msg_, nt, hist_, lines_
        base13 = d13
        CASES = [("hard LF", base13.replace("strength.difficulty=normal", "strength.difficulty=hard"), "curve", 1),
                 ("custom", base13.replace("strength.difficulty=normal", "strength.difficulty=custom"), "linear", 0),
                 ("CRLF", base13.replace("\n", "\r\n"), "curve", 1),
                 ("no final newline", base13.rstrip("\n"), "curve", 1),
                 ("CRLF, no final newline", base13.replace("\n", "\r\n").rstrip("\r\n"), "curve", 1),
                 ("Easy, odd case word", base13.replace("strength.difficulty=normal", "strength.difficulty= EASY "), "curve", 1),
                 ("no difficulty line", base13.replace("strength.difficulty=normal\n", ""), "curve", 1),
                 ("shape already there (any case)", base13.replace("strength.healOnLoad=false", "strength.healOnLoad=false\nStrength.Shape=linear"), None, 0),
                 ("a curve table family already there", base13.replace("strength.floor=50", "strength.floor=50\ncurve.hp.hard.40=9"), "curve", 1),
                 ("a gap row already there", base13 + "gap.free=3\n", "curve", 1),
                 ("no strength lines at all", "# a file\nlevels.max=60\nplate.mode=off\n", "curve", 1),
                 ("strength last, no levels.max", "strength.difficulty=hard\n", "curve", 1),
                 ("levels.max last without newline", "strength.difficulty=hard\nlevels.max=60", "curve", 1),
                 ("empty file", "", "curve", 1),
                 ("marker already there", base13 + "# " + str(M14.MARK_ID) + " (already)\n", "same", 0),
                 ("the 0.1 default (MobMig 0.1.1 first, then this)", str(sfield(old_cls("MobCfg"), "DEF_CFG")), "curve", 1)]
        for name, text, shape, logn in CASES:
            if name.startswith("the 0.1 default"):
                h_ = os.path.join(SCRATCH, "mig14", "v01", "Skyy_SkyyMobs")
                shutil.rmtree(os.path.dirname(h_), ignore_errors=True)
                os.makedirs(h_)
                open(os.path.join(h_, "config.properties"), "wb").write(text.encode("latin-1"))
                LogC.drop(int(LogC.snap().size()))
                Mig.run(Paths.get(h_))
                Pub.flush()
                text = open(os.path.join(h_, "config.properties"), "rb").read().decode("latin-1")
            exp = py_m14(text)
            msg_, nt, hist_, lines_ = case(name.replace(" ", "_").replace(",", "").replace("(", "").replace(")", "").replace("/", "")[:40], text)
            if shape == "same":
                check(exp is None and nt == text and not hist_ and not lines_ and msg_ == "", "MIG. %s: untouched, no History, no log" % name)
                continue
            mlines = [l_ for l_ in lines_ if len(l_) >= 8 and l_[1] == "SkyyMobs 0.1.4"]
            check(exp is not None and nt == exp[0] and exp[1] == shape and len(hist_) == 1 and len(mlines) == logn,
                  "MIG. %s -> the mirror's text, shape %s, History 1, %d log line(s): got shape %s, %d log, text %s" % (
                      name, shape, logn, exp[1] if exp else None, len(mlines), "ok" if exp and nt == exp[0] else "DIFFERENT"))
            if exp is not None and nt is not None:
                po, pn = JClass("java.util.Properties")(), JClass("java.util.Properties")()
                po.load(JClass("java.io.StringReader")(text))
                pn.load(JClass("java.io.StringReader")(nt))
                ok_ = all(str(pn.getProperty(k_)) == str(po.getProperty(k_)) for k_ in [str(x) for x in po.stringPropertyNames()])
                ok_ = ok_ and all(str(pn.getProperty(k_)) == v_ for k_, v_ in exp[2].items()) and int(pn.size()) == int(po.size()) + len(exp[2])
                check(ok_, "MIG. %s: every old value kept + exactly the added keys" % name)
                if "\r\n" in text:
                    check(nt.count("\r\n") == nt.count("\n") or (not nt.endswith("\n") and nt.count("\r\n") == nt.count("\n")), "MIG. %s: CRLF on every line" % name)
                if name.startswith("shape already"):
                    check("strength.shape kept (already in the file)" in msg_, "MIG. %s: the INFO line names the kept key: %r" % (name, msg_[:160]))
        # a blocked config-history: nothing written
        msg_, nt, hist_, lines_ = case("blocked", base13, blocked=True)
        check(nt == base13 and not lines_ and msg_ == "", "MIG. config-history blocked (a file in its place): the file is NOT updated, no log line")
        # ---- MIG-OPEN (FIXER 2, recheck finding 1): an anchor entry that reaches the file's last line still open (odd trailing
        # backslashes / the final newline swallowed as its continuation) - the new lines go BEFORE it, the update is written, values kept
        def props(t_):
            pp_ = JClass("java.util.Properties")()
            pp_.load(JClass("java.io.StringReader")(t_))
            return dict((str(k_), str(pp_.getProperty(k_))) for k_ in pp_.stringPropertyNames())
        # negative control: appending the block after an open last line really changes its value (the trap is real)
        trap = "strength.hp = 3\\"
        check(props(trap + "\n" + str(M14.MARK) + "\nstrength.shape=curve").get("strength.hp") != "3",
              "MIG-OPEN. negative control: lines appended after an open last line become its continuation")
        OPEN = [("critic exact (open, no final newline)", trap, "before"),
                ("open last strength entry", "strength.difficulty=hard\nstrength.hp = 3\\", "before"),
                ("open last strength entry CRLF", "strength.difficulty=hard\r\nstrength.hp = 3\\", "before"),
                ("multi-line open entry", "strength.difficulty=hard\nstrength.hp = 3\\\n   4\\", "before"),
                ("final newline swallowed", "strength.difficulty=hard\nstrength.hp = 3\\\n", "before"),
                ("final newline swallowed CRLF", "strength.difficulty=hard\r\nstrength.hp = 3\\\r\n", "before"),
                ("even backslashes = closed", "strength.difficulty=hard\nstrength.hp=3\\\\", "after"),
                ("levels.max last and open", "strength.difficulty=hard\nlevels.max=60\\", "after"),
                ("levels.max last and open CRLF", "strength.difficulty=hard\r\nlevels.max=60\\", "after"),
                ("no strength entry, last entry open", "# a file\nplate.mode=off\nlevels.max=60\nfoo=a\\", "nostr"),
                ("no strength entry, last entry open CRLF", "# a file\r\nlevels.max=60\r\nfoo=a\\", "nostr")]
        for name, text, where in OPEN:
            po_ = props(text)
            msg_, nt, hist_, lines_ = case("open " + re.sub(r"[^a-z]", "", name.lower())[:30], text)
            ok_ = nt is not None and nt != text and msg_ != "" and len(hist_) == 1
            pn_ = props(nt) if ok_ else {}
            r_ = M14.update(text)
            added_ = dict(zip([str(x) for x in r_[3]], [str(x) for x in r_[4]])) if r_ is not None else {}
            ok_ = ok_ and all(pn_.get(k_) == v_ for k_, v_ in po_.items()) and all(pn_.get(k_) == v_ for k_, v_ in added_.items()) \
                and len(pn_) == len(po_) + len(added_) and len(added_) == 89 and str(r_[0]) == nt and M14.update(nt) is None
            if "\r\n" in text and nt is not None:
                ok_ = ok_ and nt.count("\r\n") == nt.count("\n")
            elif nt is not None:
                ok_ = ok_ and "\r" not in nt
            if ok_ and where == "before":
                ok_ = nt.index(str(M14.MARK)) < nt.index("strength.hp")
            if ok_ and where == "nostr":
                ok_ = nt.index(str(M14.MARK)) < nt.index("foo=a") and nt.endswith("foo=a\\")
            if ok_ and where == "after" and "levels.max" in text:
                ok_ = nt.index(str(M14.ROLE_DOC)) < nt.index("levels.max=60") and nt.endswith("levels.max=60\\")
            check(ok_, "MIG-OPEN. %s: written (History 1, INFO), every old value kept + the 89 new keys, line endings kept, second run nothing: %r" % (
                name, (nt or "")[:80]))
        # fuzz: random small files ending in an open / closed entry, LF / CRLF, with / without the final newline - update() never
        # changes an old value (sameAfter would refuse) and every file is updated
        rnd_ = random.Random(20261006)
        pieces = ["strength.difficulty=hard", "strength.hp = 3\\", "strength.dmg=4", "  4\\", "levels.max=60", "levels.max=60\\",
                  "plate.mode=off", "# note \\", "", "foo=a\\\\", "bar = b\\", "strength.floor=50", "Strength.Shape=linear"]
        bad_, n_ = [], 0
        for i_ in range(1500):
            ls_ = [rnd_.choice(pieces) for _ in range(rnd_.randint(1, 7))]
            t_ = ("\r\n" if rnd_.random() < 0.5 else "\n").join(ls_)
            if rnd_.random() < 0.5:
                t_ += "\r\n" if "\r\n" in t_ or rnd_.random() < 0.5 else "\n"
            r_ = M14.update(t_)
            if r_ is None:
                bad_.append(("null", t_))
                continue
            n_ += 1
            po_, pn_ = props(t_), props(str(r_[0]))
            added_ = dict(zip([str(x) for x in r_[3]], [str(x) for x in r_[4]]))
            if not (all(pn_.get(k_) == v_ for k_, v_ in po_.items()) and all(pn_.get(k_) == v_ and k_ not in po_ for k_, v_ in added_.items())
                    and len(pn_) == len(po_) + len(added_)):
                bad_.append(("changed", t_))
        check(not bad_ and n_ == 1500, "MIG-OPEN. fuzz: 1500 random files with open / closed last entries (LF / CRLF, +- final newline) - every one "
              "updated, no old value changed, exactly the added keys: %d bad %r" % (len(bad_), bad_[:2]))
        print("MIG-OPEN. %d open-last-line files through MobMig14.run + negative control + 1500-file fuzz" % len(OPEN))
        # the loader on a not-updated (0.1.3) file: Custom -> Per level, else Level curve (the same decision)
        print("MIG. MobMig14: the block = spec 6.1 rows + 80 curve entries; 0.1.3 default -> 0.1.4 default; Skyy's live copy started twice (mirror text, "
              "values kept, History, 1 Undo line, Undo -> 0.1.3's Hard, second start no change); %d synthetic files + blocked History" % len(CASES))

    def section_set():
        """SET: the build's pairing STOP (spec 7.1) on scratch copies of tools/deploy_set.py (--set-file + --check-set: the guard only, no build)"""
        import subprocess
        real = open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read()
        d_ = os.path.join(SCRATCH, "setcheck")
        os.makedirs(d_, exist_ok=True)
        env = dict(os.environ)
        env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")

        def run_with(text, name):
            p_ = os.path.join(d_, name + ".py")
            open(p_, "w", encoding="utf-8").write(text)
            r = subprocess.run([sys.executable, os.path.join(HERE, "build_skyymobs_%s.py" % VERSION), "--set-file", p_, "--check-set"],
                               capture_output=True, text=True, env=env, timeout=300)
            return r.returncode, (r.stdout + r.stderr)
        pin = re.search(r'\("SkyyMobs", "([0-9.]+)"\)', real).group(1)

        def pinned(mobs, gear, skills):
            t_ = real.replace('("SkyyMobs", "%s")' % pin, '("SkyyMobs", "%s")' % mobs)
            t_ = re.sub(r'\("SkyyGear", "[0-9.]+"\)', '("SkyyGear", "%s")' % gear, t_)
            t_ = re.sub(r'\("SkyySkills", "[0-9.]+"\)', '("SkyySkills", "%s")' % skills, t_)
            return t_
        cases = [("today's SET (SkyyMobs %s)" % pin, real, 0, "SET pairing ok"),
                 ("0.1.4 + Gear 0.2.5 + Skills 0.4.17", pinned("0.1.4", "0.2.5", "0.4.17"), 0, "SET pairing ok"),
                 ("0.1.4 + Gear 0.2.4", pinned("0.1.4", "0.2.4", "0.4.17"), 1, "STOP: SkyyMobs 0.1.4 is pinned with SkyyGear 0.2.4"),
                 ("0.1.4 + Skills 0.4.16", pinned("0.1.4", "0.2.5", "0.4.16"), 1, "STOP: SkyyMobs 0.1.4 is pinned with SkyySkills 0.4.16"),
                 ("0.1.4 + newer partners", pinned("0.1.4", "0.2.6", "0.4.18"), 0, "SET pairing ok")]
        for what, text, rc_want, out_want in cases:
            rc, out = run_with(text, "case%d" % cases.index((what, text, rc_want, out_want)))
            check((rc == 0) == (rc_want == 0) and out_want in out, "SET. %s -> %s: rc %d, %r" % (what, out_want, rc, out.strip().splitlines()[-1:] if out.strip() else ""))
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_skyymobs_%s.py" % VERSION), "--set-file", os.path.join(TOOLS, "deploy_set.py"), "--check-set"],
                           capture_output=True, text=True, env=env, timeout=300)
        check(r.returncode != 0 and "--set-file must be a file inside tools/dev/scratch" in (r.stdout + r.stderr), "SET. --set-file outside the scratch is refused")
        print("SET. the build's pairing STOP: %d SET variants + the --set-file guard" % len(cases))

    # ---------------- O / U / Z (now 0.1.3 -> 0.1.4) + Q / FL / RA / IN / LV (0.1.2) + NQ / AX (0.1.3) + the 0.1.4 sections
    for _nm, _fn, _a in (("O", section_o, (hdr,)), ("U", section_u, ()), ("Z", section_z, ()), ("Q", section_q, ()), ("FL", section_fl, ()),
                         ("RA", section_ra, ()), ("IN", section_in, ()), ("LV", section_lv, ()), ("NQ", section_nq, ()), ("AX", section_ax, ()),
                         ("CU", section_cu, ()), ("CU-K", section_cuk, ()), ("GP", section_gp, ()), ("DM", section_dm, ()), ("SR", section_sr, ()),
                         ("IF", section_if, ()), ("WN", section_wn, ()), ("CMD", section_cmd, ()), ("MIG", section_mig, ()), ("SET", section_set, ())):
        try:
            _fn(*_a)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            check(False, "%s. the section could not run: %s" % (_nm, ex))
        Cfg.useDefaults()

    # ---------------- P. bytecode facts
    CPj = JClass("javassist.ClassPool")(False)
    CPj.appendSystemPath()
    CPj.appendClassPath(B.SERVER_JAR)
    CPj.appendClassPath(JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cls, meth):
        out = ""
        cc = CPj.get(PKG + cls)
        for mm in list(cc.getDeclaredMethods()):
            if str(mm.getName()) == meth:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out += str(bos.toString())
        return out

    def ctor(cls):
        cc = CPj.get(PKG + cls)
        out = ""
        for k in cc.getDeclaredConstructors():
            mi = k.getMethodInfo()
            it = mi.getCodeAttribute().iterator()
            while it.hasNext():
                pos = it.next()
                out += str(IP.instructionString(it, pos, mi.getConstPool())) + "\n"
        return out
    q = code("LevelHook", "getQuery")
    check("NPCEntity.getComponentType" in q and "EntityStatMap.getComponentType" in q and "Query.and" in q,
          "P. the hook only sees NPCEntity + EntityStatMap holders (players never)")
    sys_ = code("SkyyMobsPlugin", "systems")
    check(all(x in sys_ for x in ("RoleBuilderSystem", "EntityStatsSystems$Setup", "BalancingInitialisationSystem", "DamageSystems$ArmorDamageReduction")),
          "P. the plugin resolves the 4 classes it orders against")
    hc = ctor("LevelHook")
    check(hc.count("Order.AFTER") == 3 and "BEFORE" not in hc, "P. the hook is ordered AFTER RoleBuilderSystem, Setup, BalancingInitialisationSystem")
    dc = ctor("LevelDamage")
    check("Order.BEFORE" in dc and "AFTER" not in dc and "getFilterDamageGroup" in code("LevelDamage", "getGroup"),
          "P. the damage system: Filter group, BEFORE ArmorDamageReduction")
    regs = re.findall(r"new #\d+ = Class (com\.skyy\.mobs\.\w+)", sys_)
    check(sorted(regs) == sorted(PKG + c for c in ("LevelHook", "LevelDamage", "LevelDamageU", "GapDamage", "GapDamageU")) and len(set(regs)) == 5,
          "P. one registerSystem per class (the hook WITHOUT a fallback, the damage system + its unordered fallback, 0.1.4: the gap system + its "
          "unordered fallback): %s" % regs)
    gdc = ctor("GapDamage")
    check("Order.BEFORE" in gdc and "AFTER" not in gdc and "getFilterDamageGroup" in code("GapDamage", "getGroup") and "Query.any" in code("GapDamage", "getQuery"),
          "P. 0.1.4: the gap system: Filter group, BEFORE ArmorDamageReduction, Query.any (the victim is a mob)")
    check(sys_.find("LevelDamage") < sys_.find("GapDamage.ADR") and "putstatic" in sys_, "P. 0.1.4: GapDamage orders against the same ArmorDamageReduction class")
    # review F4: a refused hook registration logs an ERROR and leaves MobLevel.HOOK false (no unordered hook that could level nothing or
    # strip saved levels); /mobs inspect and /mobs info read the flag
    check("LevelHookU" not in sys_ and "MobLog.error" in sys_ and sys_.count("putstatic") >= 2 and "MobLevel.HOOK" in sys_,
          "P. F4: no unordered hook fallback; the hook registration sets MobLevel.HOOK, a failure logs an ERROR")
    check("MobLevel.HOOK" in code("MobCmds", "inspect") and "MobLevel.HOOK" in code("MobCmds", "infoLines"),
          "P. F4: /mobs inspect and /mobs info tell when the hook is not running")
    check(not bool(Lvl.HOOK), "P. F4: HOOK is false until the plugin registers the hook (bare JVM)")
    # review F6: the prune is scheduled every 5 minutes and cancelled on shutdown
    st_c, sd_c = code("SkyyMobsPlugin", "setup"), code("SkyyMobsPlugin", "shutdown")
    check("scheduleWithFixedDelay" in st_c and "MobPruneTask" in st_c and "MobLevel.PRUNE" in st_c and "cancel" in sd_c,
          "P. F6: setup schedules MobPruneTask (scheduleWithFixedDelay), shutdown cancels it")
    # 0.1.1: setup runs the update first (on the Skyy_SkyyMobs folder), then the loader, then the config kit; the ready line carries the
    # update's answer and the caps
    i_mig, i_load, i_pub = st_c.find("MobMig.run((Ljava/nio/file/Path;)"), st_c.find("MobCfg.load(()V)"), st_c.find("CfgPub.start(")
    check(0 <= i_mig < i_load < i_pub, "P. 0.1.1: setup() calls MobMig.run(dir) before MobCfg.load() and CfgPub.start (%d / %d / %d)" % (i_mig, i_load, i_pub))
    stt_ = code("MobCfg", "strengthText")
    check("MobCfg.strengthText" in st_c and '" (Per level shape, caps x"' in stt_ and "MobCfg.HP_CAP" in stt_ and "String.replace((CC)" in st_c and '"; "' in st_c,
          "P. 0.1.1 / 0.1.4: the ready line prints the strength (Per level: the caps, MobCfg.strengthText) and appends the update's lines")
    i_m14 = st_c.find("MobMig14.run((Ljava/nio/file/Path;)")
    check(0 <= i_mig < i_m14 < i_load, "P. 0.1.4: setup() runs MobMig.run, then MobMig14.run, then MobCfg.load (%d / %d / %d)" % (i_mig, i_m14, i_load))
    m14r = code("MobMig14", "run")
    check(m14r.find("CfgHist.snapshot") < m14r.find("mgSaved") < m14r.find("CfgRows.atomicWrite") < m14r.find("CfgLog.enqueue") and m14r.find("MobMig14.sameAfter") < m14r.find("CfgHist.snapshot"),
          "P. 0.1.4: MobMig14.run - the Properties check, History snapshot, verified, then the atomic write, then the Undo line")
    check('"mob:fn:info"' in st_c and "MobInfoFn" in st_c and '"mob:fn:info"' in sd_c and "MobGap.CACHE" in sd_c,
          "P. 0.1.4: setup puts mob:fn:info on the bridge, shutdown removes it and clears the class level cache")
    mrun = code("MobMig", "run")
    check(mrun.find("CfgHist.snapshot") < mrun.find("mgSaved") < mrun.find("CfgRows.atomicWrite") < mrun.find("CfgLog.enqueue"),
          "P. 0.1.1: MobMig.run - History snapshot, verified, then the atomic write, then the Undo lines")
    # review F3: the worldgen cache key has no >> 3 cell any more
    wgc = code("MobLevel", "worldgen")
    check("ishr" not in wgc and wgc.count("ConcurrentHashMap.put") == 1, "P. F3: the worldgen cache keys the exact column (no >> shift), one put")
    # every abstract engine method of the two system classes has a concrete implementation (an AbstractMethodError would only show
    # when the world ticks): HolderSystem.onEntityAdd / onEntityRemoved / QuerySystem.getQuery, EntityEventSystem.handle / getQuery
    RMod = JClass("java.lang.reflect.Modifier")
    for cname in ("LevelHook", "LevelDamage", "LevelDamageU", "MobLevelFn", "MobPlateStep", "MobScanTask", "MobPruneTask", "MobRefresh"):
        jc_ = Cls.forName(PKG + cname, False, sysl)
        abstract_left = []
        for mth in jc_.getMethods():
            if RMod.isAbstract(mth.getModifiers()):
                abstract_left.append(str(mth))
        check(not RMod.isAbstract(jc_.getModifiers()) and not abstract_left, "P. %s implements every abstract engine method: %s" % (cname, abstract_left))
    # 0.1.2: the floor + the live re-apply
    dv = code("MobCfg", "derive")
    check("MobCfg.HP_SIG" in dv and "MobCfg.ON_HEALTH" in dv and "java.lang.Runnable.run" in dv, "P. 0.1.2: derive runs ON_HEALTH when the health signature changes")
    i_on = st_c.find("MobCfg.ON_HEALTH(")
    check(0 <= i_load < i_on < i_pub and "Class com.skyy.mobs.MobRefresh" in st_c, "P. 0.1.2: setup() sets ON_HEALTH = new MobRefresh(null) after MobCfg.load, before CfgPub.start (%d / %d / %d)" % (
        i_load, i_on, i_pub))
    check(0 <= sd_c.find("aconst_null") < sd_c.find("MobCfg.ON_HEALTH(") < sd_c.find("cancel"), "P. 0.1.2: shutdown clears ON_HEALTH first")
    dp_, rn_ = code("MobRefresh", "dispatch"), code("MobRefresh", "run")
    check("World.execute((Ljava/lang/Runnable;)V)" in dp_ and "MobLevel.hasMobsIn" in dp_ and "getComponent" not in dp_ and "EntityStatMap" not in dp_,
          "P. 0.1.2: the dispatcher only queues World.execute tasks (no component is touched off the world thread)")
    check("MobLevel.refreshWorld" in rn_ and "MobLevel.liveWorlds" in rn_ and "MobRefresh.dispatch" in rn_, "P. 0.1.2: MobRefresh.run - null world = dispatch(liveWorlds), else refreshWorld")
    rw_, ro_ = code("MobLevel", "refreshWorld"), code("MobLevel", "refreshOne")
    check(all(x in rw_ for x in ("EntityStore.getRefFromUUID", "EntityStore.getStore", "component.Store.getComponent", "Ref.isValid", "MobLevel.refreshOne")),
          "P. 0.1.2: refreshWorld - its own world's store, valid refs only, refreshOne")
    rl_ = ro_.split("\n")
    k_sm = [i for i, x in enumerate(rl_) if "MobLevel.setMult((Lcom/hypixel/hytale/server/core/modules/entitystats/EntityStatMap;IIZZD)F)" in x]
    check(len(k_sm) == 1 and "dload" in rl_[k_sm[0] - 1] and "iconst_0" in rl_[k_sm[0] - 2] and "iconst_0" in rl_[k_sm[0] - 3],
          "P. 0.1.2 / 0.1.4: refreshOne calls setMult(m, hi, level, false, false, rx) - never full, never heal (rx = the scale.role Health x)")
    check("MobCfg.roleX" in rw_ and "MobLevel.refreshOne((Lcom/hypixel/hytale/server/core/modules/entitystats/EntityStatMap;IID)Z)" in rw_,
          "P. 0.1.4: refreshWorld re-applies with each mob's scale.role factor (MobCfg.roleX of its role)")
    sm_ = code("MobLevel", "setMult")
    check("MobCfg.HEAL_ON_LOAD" in sm_ and "MobCfg.hpAmount" in sm_ and "MobLevel.baseOf" in sm_, "P. 0.1.2: setMult puts hpAmount(level, baseOf); the 4-argument form passes strength.healOnLoad")
    ins_, hl_ = code("MobCmds", "inspect"), code("MobCmds", "healthLine")
    check("MobCmds.healthLine" in ins_ and "MobCfg.hpMult" not in ins_ and "MobLevel.amountOn" in hl_ and "MobCfg.hpAmount" in hl_,
          "P. 0.1.2: /mobs inspect prints healthLine (the modifier on the mob vs the setting), no longer hpMult")
    check("MobLevel.amountOn" in code("MobCmds", "set"), "P. 0.1.2: /mobs set reports the multiplier it applied")
    # 0.1.3 (F1): the health after a modifier change is written only through writeValue = minStatValue / maxStatValue
    wv_ = code("MobLevel", "writeValue")
    check("EntityStatMap.minStatValue((IF)F)" in wv_ and "EntityStatMap.maxStatValue((IF)F)" in wv_ and "EntityStatValue.get(()F)" in wv_
          and "setStatValue" not in wv_ and "maximizeStatValue" not in wv_, "P. 0.1.3: writeValue = minStatValue / maxStatValue against the current health")
    st2_ = code("MobLevel", "stripStats")
    check(sm_.count("MobLevel.writeValue") == 2 and "setStatValue" not in sm_ and "maximizeStatValue" not in sm_ and st2_.count("MobLevel.writeValue") == 1
          and "setStatValue" not in st2_, "P. 0.1.3: setMult writes its heal / share health and stripStats its share only through writeValue")
    esm_calls = collections.Counter()
    for nm in names:
        cpool_ = CPj.get(nm).getClassFile().getConstPool()
        for i in range(1, cpool_.getSize()):
            try:
                if cpool_.getTag(i) == 10 and str(cpool_.getMethodrefClassName(i)) == ESMN:
                    esm_calls[str(cpool_.getMethodrefName(i))] += 1
            except Exception:
                continue
    check(not [k for k in esm_calls if k in ("setStatValue", "maximizeStatValue", "minimizeStatValue", "resetStatValue", "addStatValue", "subtractStatValue")]
          and esm_calls.get("minStatValue") == 1 and esm_calls.get("maxStatValue") == 1,
          "P. 0.1.3: the jar's EntityStatMap calls %s - no Set / Maximize / Minimize / Reset / Add write anywhere" % dict(esm_calls))
    oa = code("MobLevel", "onAdd")
    check("savedLevel" in oa and "KEPT" in oa and "whyNot" in oa and "lookupMob" in oa and "levelFor" in oa and "apply" in oa,
          "P. onAdd: save slot, session memory, who-filter, lookup, roll, apply")
    check(oa.find("MobCfg.roleLevel") < oa.find("MobCfg.whyNot") and "MobCfg.roleKey" in oa, "P. 0.1.4: onAdd reads the scale.role row first (before the who-filter)")
    print("P. bytecode facts done")

    # ---------------- L. link check (release + 0.7 pre-release)
    def link(server):
        cpl = JClass("javassist.ClassPool")(False)
        cpl.appendSystemPath()
        cpl.appendClassPath(server)
        cpl.appendClassPath(JAR)
        missing, n_ = [], 0
        for nm in names:
            cc = cpl.get(nm)
            cpool = cc.getClassFile().getConstPool()
            for i in range(1, cpool.getSize()):
                try:
                    tag = cpool.getTag(i)
                except Exception:
                    continue
                if tag not in (9, 10, 11):    # Fieldref, Methodref, InterfaceMethodref
                    continue
                if tag == 9:
                    owner, mn, desc = str(cpool.getFieldrefClassName(i)), str(cpool.getFieldrefName(i)), str(cpool.getFieldrefType(i))
                elif tag == 10:
                    owner, mn, desc = str(cpool.getMethodrefClassName(i)), str(cpool.getMethodrefName(i)), str(cpool.getMethodrefType(i))
                else:
                    owner, mn, desc = str(cpool.getInterfaceMethodrefClassName(i)), str(cpool.getInterfaceMethodrefName(i)), str(cpool.getInterfaceMethodrefType(i))
                if not owner.startswith(("com.hypixel.", "org.joml.")):
                    continue
                n_ += 1
                try:
                    oc = cpl.get(owner)
                    if tag == 9:
                        f_ = oc.getField(mn, desc)
                    elif mn == "<init>":
                        oc.getConstructor(desc)
                    else:
                        oc.getMethod(mn, desc)
                except Exception:
                    missing.append("%s.%s%s (from %s)" % (owner, mn, desc, nm.rsplit(".", 1)[1]))
        return n_, sorted(set(missing))
    n_rel, miss_rel = link(B.SERVER_JAR)
    check(not miss_rel, "L. release jar: every referenced engine member exists (%d refs): %s" % (n_rel, miss_rel[:8]))
    if os.path.isfile(PRE_JAR):
        n_pre, miss_pre = link(PRE_JAR)
        check(not miss_pre, "L. 0.7 pre-release jar: every referenced engine member exists (%d refs): %s" % (n_pre, miss_pre[:12]))
        print("L. link check: release %d refs, 0 missing; 0.7 pre-release %d refs, %d missing" % (n_rel, n_pre, len(miss_pre)))
    else:
        print("L. link check: release %d refs; no pre-release jar at %s" % (n_rel, PRE_JAR))


def is_link(p):
    """True for a symbolic link or a Windows junction / mount point (any reparse point): never followed, never deleted through"""
    try:
        if os.path.islink(p):
            return True
        isj = getattr(os.path, "isjunction", None)
        if isj is not None and isj(p):
            return True
        return bool(getattr(os.lstat(p), "st_file_attributes", 0) & 0x400)     # FILE_ATTRIBUTE_REPARSE_POINT
    except OSError:
        return False


def guard_scratch():
    """None when --dir may be used (and deleted): a folder INSIDE a task folder of tools/dev/scratch (tools/dev/scratch/<task>/<sub>) -
    never the scratch root or a top-level task folder (other agents' live work sits there), no '..' in the argument, no link / junction
    on its path (it or a folder above it, up to the scratch root) - that is missing, empty or this harness's own (its MARKER file).
    Else the reason it is refused (nothing is deleted then)."""
    if DIR_ARG is not None and ".." in re.split(r"[\\/]+", DIR_ARG):
        return "'..' in the --dir argument"
    root_ = os.path.normcase(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")))
    s_ = os.path.normcase(os.path.realpath(SCRATCH))
    try:
        rel = os.path.relpath(s_, root_)
    except ValueError:
        return "not on the drive of tools/dev/scratch"
    parts = [p for p in rel.replace("\\", "/").split("/") if p]
    if os.path.isabs(rel) or not parts or parts[0] in (".", ".."):
        return "outside tools/dev/scratch (or the scratch root itself)"
    if len(parts) < 2:
        return "a top-level folder of tools/dev/scratch - use tools/dev/scratch/<task>/<sub>"
    # the path as given must be the real one: no link / junction on it (realpath above already resolved any, so compare and check each level)
    a_ = os.path.normcase(os.path.abspath(SCRATCH))
    if a_ != s_:
        return "a link / junction on its path (it resolves to %s)" % s_
    p_ = os.path.abspath(SCRATCH)
    while os.path.normcase(p_) != root_ and len(p_) > len(root_):
        if os.path.lexists(p_) and is_link(p_):
            return "%s is a link / junction" % p_
        p_ = os.path.dirname(p_)
    if os.path.lexists(SCRATCH):
        if is_link(SCRATCH) or not os.path.isdir(SCRATCH):
            return "exists and is not a plain folder"
        if os.listdir(SCRATCH) and not os.path.isfile(os.path.join(SCRATCH, MARKER)):
            return "exists, is not empty and is not this harness's folder (no %s)" % MARKER
    return None


def empty_dir(d, keep=None):
    """delete everything inside the validated folder d but the file `keep`: files, then the emptied sub-folders; a link / junction inside
    is never followed (only the link itself goes); a file this process still holds is left where it is"""
    for e_ in list(os.scandir(d)):
        p_ = e_.path
        try:
            if is_link(p_):
                if os.path.islink(p_):
                    os.unlink(p_)
                else:
                    os.rmdir(p_)
            elif e_.is_dir(follow_symlinks=False):
                empty_dir(p_, keep)
                os.rmdir(p_)
            elif keep is None or os.path.normcase(p_) != os.path.normcase(keep):
                os.remove(p_)
        except OSError:
            pass


def cleanup_scratch():
    """the end-of-run delete of the validated, marked folder; a file this process still holds (the zstd-jni library the JVM unpacked into
    java.io.tmpdir) cannot go before os._exit - then the marker stays with it, so the next run knows the folder as its own and empties it
    (the guard refuses an unmarked, non-empty folder)"""
    mk_ = os.path.join(SCRATCH, MARKER)
    empty_dir(SCRATCH, mk_)
    left = [x for x in os.listdir(SCRATCH) if x != MARKER]
    if left:
        print("scratch: %s kept with its marker (still held by this process: %s) - the next run empties it" % (SCRATCH, left))
        return
    try:
        os.remove(mk_)
        os.rmdir(SCRATCH)
    except OSError:
        pass


def main():
    if not os.path.isfile(JAR):
        print("no jar at", JAR, "- build it first")
        return 1
    for p_, what in ((PREV_JAR, "the 0.1.2 jar (SET pin) for NQ / O / Z"), (V011_JAR, "the 0.1.1 jar for Q / FL / U2"), (OLD_JAR, "the 0.1 jar for U / V"),
                     (MENU_JAR, "SkyyMenu 0.3.5 (SET pin) for V")):
        if not os.path.isfile(p_):
            print("missing %s: %s" % (what, p_))
            return 1
    why = guard_scratch()
    if why:
        print("--dir refused (%s): %s - nothing was deleted" % (why, SCRATCH))
        return 1
    SCRATCH_OK[0] = True
    if os.path.isdir(SCRATCH):                          # start clean: missing, empty or this harness's own (marker checked above)
        empty_dir(SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    open(os.path.join(SCRATCH, MARKER), "w").write("SkyyMobs %s harness scratch - deleted at the end of the run (unless --keep)\n" % VERSION)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    print("SkyyMobs %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAIL", f[:600])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code_ = main()
    # only the folder main() validated AND marked is deleted (0.1's harness deleted --dir even after refusing it - a --dir naming the
    # scratch ROOT wiped every builder's scratch folder on 2026-10-02)
    if not KEEP and SCRATCH_OK[0] and os.path.isfile(os.path.join(SCRATCH, MARKER)) and guard_scratch() is None:
        cleanup_scratch()
    sys.stdout.flush()
    os._exit(code_)
