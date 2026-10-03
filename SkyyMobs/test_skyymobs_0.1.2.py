"""SkyyMobs 0.1.2 harness - bare JVM, no game. Run: python SkyyMobs/test_skyymobs_0.1.2.py [--jar <jar>] [--dir <scratch>] [--keep]

Made from test_skyymobs_0.1.1.py (every 0.1 / 0.1.1 check still runs against the 0.1.2 jar; F runs with the floor OFF = the 0.1.1
numbers). -Xverify:all, -XX:-UsePerfData; HytaleServer.jar + tools/javassist.jar + the SkyyMobs 0.1.2 jar + SkyyMenu/SkyyMenu-0.3.5.jar
(the label check draws with it) on the classpath; SkyyMobs-0.1.1.jar (the SET pin) and SkyyMobs-0.1.jar are read through child-first
loaders (O, Q, FL, U, V) and as zip bytes (Z). Nothing is deployed and nothing outside the scratch folder is written (default
tools/dev/scratch/mobs012/harness; TEMP / TMP and java.io.tmpdir point into it). SCRATCH SAFETY (the 2026-10-02 incident): --dir must be
a folder INSIDE a task folder (tools/dev/scratch/<task>/<sub>) - never the scratch root or a top-level task folder - and, if it exists,
this harness's own (its marker file); anything else is refused and NOTHING is deleted; the end-of-run cleanup deletes only that
validated, marked folder (unless --keep). Read-only: Assets.zip, the two HytaleServer.jar files (release + 0.7 pre-release), the client
font tables, the installed Mods folder (X scan, the deployed SkyyMenu.jar hash) and Skyy's live Skyy_SkyyMobs folder - COPIED into the
scratch folder before anything runs on it (U).
0.1.2 sections:
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
  O  SkyyMobs-0.1.1.jar's own header vs 0.1.2: 0.1.1's 25 keys in order + strength.floor after strength.dmgCap, ids, labels, types,
     values, flags, files unchanged; only strength.hp + strength.hpCap help changed; the new row exactly; both jars' multipliers equal
  Z  class byte-compare SkyyMobs-0.1.1.jar vs 0.1.2: MobRefresh added; CfgFn = only its version string; CfgFile = only the two row-count
     array sizes 25 -> 26; CfgRows / MobCfg / MobLevel / MobCmds / SkyyMobsPlugin = exactly the 0.1.2 members and methods; manifest.json
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
VERSION = "0.1.2"
PREVVER = "0.1.1"                 # the SET pin 0.1.2 replaces (O / Z / FL compares; floor 0 = its numbers)
OLDVER = "0.1"                    # still read: its default text (U2: the one-time 0.1 -> 0.1.1 update ships unchanged) and V's proof
PKG = "com.skyy.mobs."
MPKG = "com.skyy.menu."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "mobs012", "harness")))
MARKER = ".skyymobs012-harness"   # written into the scratch folder this harness made; only a folder holding it is ever deleted
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-%s.jar" % OLDVER)                               # 0.1 (read-only)
PREV_JAR = os.path.join(HERE, "SkyyMobs-%s.jar" % PREVVER)                             # the SET pin 0.1.1 (read-only)
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
                                     "SkyyMobsPlugin"))
    check(names == want, "M. exactly the 31 classes (0.1.1's 30 + MobRefresh; no LevelHookU - review F4): %s" % sorted(set(names) ^ set(want)))
    check(not [n for n in z.namelist() if n.endswith(".ui")], "M. no .ui file in the jar")

    Cfg, Lvl, Glob = JClass(PKG + "MobCfg"), JClass(PKG + "MobLevel"), JClass(PKG + "MobGlob")
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
    # max = (100 + the additive sum) x the multiplicative SUM (EntityStatValue.computeModifiers, bytecode-checked)
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
    for f in ("public java.util.HashMap mods;", "public float[] cell;", "public int puts;"):
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
    sm.addMethod(CtNewMethod.make("public float maximizeStatValue(int i) { this.cell[0] = maxNow(); return this.cell[0]; }", sm))
    sm.addMethod(CtNewMethod.make("public float setStatValue(int i, float v) { init(); this.cell[0] = v; clamp(); return this.cell[0]; }", sm))
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
        never mixed with the 0.1.2 classes on the classpath)"""
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

    def prev_cls(name):
        """a class of SkyyMobs-0.1.1.jar, the SET pin (child-first)"""
        return jar_cls(PREV_JAR, name)

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
        check([t for _l, t in tabs] == [["Which mobs"], ["Strength"], ["Level bands"], ["Nameplate"]], "V. the tabs as drawn: %s" % tabs)
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
        """O: SkyyMobs-0.1.1.jar's own published header vs 0.1.2 - everything of 0.1.1 an admin's file / log / code depends on unchanged,
        one new row (strength.floor), only the two intended help texts changed; both jars' level multipliers equal everywhere"""
        oh = jcall(prev_cls("CfgRows"), "header")
        orows = [[str(x) for x in r] for r in oh[7]]
        nrows = [[str(x) for x in r] for r in hdr[7]]
        check(str(oh[3]) == PREVVER and str(hdr[3]) == VERSION, "O. the 0.1.1 header is 0.1.1's (%s), the new one %s" % (oh[3], hdr[3]))
        okeys, nkeys = [r[0] for r in orows], [r[0] for r in nrows]
        at = okeys.index("strength.dmgCap") + 1
        check(len(okeys) == 25 and nkeys == okeys[:at] + ["strength.floor"] + okeys[at:],
              "O. 0.1.1's 25 config KEYS in the same order + strength.floor right after strength.dmgCap: %s" % nkeys)
        check([str(x) for x in oh[5]] == [str(x) for x in hdr[5]] == ["levels", "strength", "bands", "plate"], "O. the same category ids")
        check([str(x) for x in oh[6]] == [str(x) for x in hdr[6]], "O. the same tab labels: %s" % [str(x) for x in hdr[6]])
        check(all(str(oh[k]) == str(hdr[k]) for k in (0, 1, 2, 4, 8, 9)), "O. contract, mod, title, node, files and note unchanged")
        od = dict((r[0], r) for r in orows)
        nd = dict((r[0], r) for r in nrows)
        diffs = set()
        for k in okeys:
            check(len(od[k]) == len(nd[k]), "O. %s: same row length" % k)
            for i in range(len(od[k])):
                if od[k][i] != nd[k][i]:
                    diffs.add((k, i))
        intended = {("strength.hp", 10), ("strength.hpCap", 10)}
        check(diffs == intended, "O. only the intended row elements changed (strength.hp + strength.hpCap help): %s" % sorted(diffs ^ intended))
        check(od["strength.hp"][10] == HP_HELP_011 and nd["strength.hp"][10] == HP_HELP,
              "O. strength.hp help: %r -> %r" % (od["strength.hp"][10], nd["strength.hp"][10]))
        check(nd["strength.hpCap"][10] == HPCAP_HELP, "O. strength.hpCap help: %r -> %r" % (od["strength.hpCap"][10], nd["strength.hpCap"][10]))
        check(nd["strength.floor"] == FLOOR_ROW, "O. the new row: %s" % nd["strength.floor"])
        PCfg = prev_cls("MobCfg")
        for d in ("easy", "normal", "hard", "custom"):
            PCfg.getField("DIFFICULTY").set(None, JStr(d))
            jcall(PCfg, "derive", (JStr.class_, None))
            Cfg.DIFFICULTY = d
            Cfg.derive(None)
            same_ = all(float(jcall(PCfg, "hpMult", (Integer.TYPE, Integer.valueOf(L)))) == float(Cfg.hpMult(L)) and
                        float(jcall(PCfg, "dmgMult", (Integer.TYPE, Integer.valueOf(L)))) == float(Cfg.dmgMult(L)) for L in range(0, 151))
            check(same_, "O. %s: 0.1.1's own hpMult / dmgMult = 0.1.2's at every level 0-150 (the floor never touches them)" % d)
        Cfg.useDefaults()
        print("O. 0.1.1 header vs 0.1.2: 25 keys, ids, labels, values, flags, files unchanged + strength.floor; changed only %s; "
              "level multipliers of both jars equal (4 difficulties x Lv 0-150)" % sorted(intended))

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
        d011 = str(sfield(prev_cls("MobCfg"), "DEF_CFG"))
        want = d011.replace("# SkyyMobs %s settings" % PREVVER, "# SkyyMobs %s settings" % OLDVER, 1)
        check(nt == want and nt == expect_mig(d01), "U2. 0.1's untouched default file -> exactly 0.1.1's default file (SkyyMobs-0.1.1.jar's own text, but "
              "its first line's version): the update 0.1.2 ships is 0.1.1's")
        check(dcfg == d011.replace("# SkyyMobs %s settings" % PREVVER, "# SkyyMobs %s settings" % VERSION, 1).replace(
            "\nstrength.dmgCap=3.5\n", "\nstrength.dmgCap=3.5\n" + FLOOR_LINES[0] + "\n" + FLOOR_LINES[1] + "\n", 1)
            and d011.count("strength.dmgCap=3.5") == 1, "U2. the 0.1.2 default file = 0.1.1's + the two floor lines after the caps (and its version)")
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
        """Z: SkyyMobs-0.1.1.jar (the SET pin) vs 0.1.2, class by class: exactly the 0.1.2 changes, every other class byte-identical"""
        za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
        na_, nb_ = set(za.namelist()), set(zb.namelist())
        check(nb_ - na_ == {"com/skyy/mobs/MobRefresh.class"} and not (na_ - nb_), "Z. one class added (MobRefresh), none removed: %s / %s" % (
            sorted(nb_ - na_), sorted(na_ - nb_)))
        diff = sorted(n_ for n_ in na_ & nb_ if za.read(n_) != zb.read(n_))
        want = ["com/skyy/mobs/CfgFile.class", "com/skyy/mobs/CfgFn.class", "com/skyy/mobs/CfgRows.class", "com/skyy/mobs/MobCfg.class",
                "com/skyy/mobs/MobCmds.class", "com/skyy/mobs/MobLevel.class", "com/skyy/mobs/SkyyMobsPlugin.class", "manifest.json"]
        same = len(na_ & nb_) - len(diff)
        check(diff == want, "Z. every other class is byte-identical to 0.1.1 (%d): the changed ones %s" % (same, diff))
        # CfgFn: only the version constant
        ca, ma, ha = classfile(za.read("com/skyy/mobs/CfgFn.class"))
        cb, mb, hb_ = classfile(zb.read("com/skyy/mobs/CfgFn.class"))
        dif = [(k, ca[k], cb[k]) for k in range(1, len(ca)) if ca[k] != cb[k]]
        check(len(ca) == len(cb) and ma == mb and ha == hb_ and len(dif) == 1 and dif[0][1] == (1, b"0.1.1") and dif[0][2] == (1, b"0.1.2"),
              "Z. CfgFn differs only by its version string 0.1.1 -> 0.1.2: %s" % [(k, a_, b_) for k, a_, b_ in dif][:4])
        IPz = JClass("javassist.bytecode.InstructionPrinter")

        def mtexts(jar, cname):
            pz = JClass("javassist.ClassPool")(False)
            pz.appendClassPath(jar)              # FIRST: the system path holds the 0.1.2 jar (classpath) and would win otherwise
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
        # CfgFile: the same constant pool and members; only <clinit> differs, by the two row-count array sizes 25 -> 26 (the new row)
        ca, ma, ha = classfile(za.read("com/skyy/mobs/CfgFile.class"))
        cb, mb, hb_ = classfile(zb.read("com/skyy/mobs/CfgFile.class"))
        cf_diff = sorted(k for k in ma if ma.get(k) != mb.get(k))
        la, lb = mtexts(PREV_JAR, "CfgFile")["<clinit>()V"].split("\n"), mtexts(JAR, "CfgFile")["<clinit>()V"].split("\n")
        ld = [(x, y) for x, y in zip(la, lb) if x != y]
        check(ca == cb and ha == hb_ and sorted(ma) == sorted(mb) and cf_diff == [("m", "<clinit>", "()V")] and len(la) == len(lb)
              and ld == [("bipush 25", "bipush 26"), ("bipush 25", "bipush 26")],
              "Z. CfgFile differs only in <clinit>: the two row-count arrays 25 -> 26 (the floor row): %s / %s" % (cf_diff, ld))
        consts = [(str(sfield(prev_cls("MobCfg"), "DEF_CFG")), str(Cfg.DEF_CFG)), (str(sfield(prev_cls("MobCfg"), "DEF_BANDS")), str(Cfg.DEF_BANDS)),
                  (str(sfield(prev_cls("CfgRows"), "VERSION")), str(RowsC.VERSION))]
        check(consts[2] == (PREVVER, VERSION) and consts[0][0] != consts[0][1], "Z. (the constants: VERSION %s -> %s, the default files)" % consts[2])

        def same_but_consts(x_, y_):
            for o_, n_ in consts:
                x_ = x_.replace('"%s"' % o_, '"%s"' % n_)
            return x_ == y_
        ESMD = "Lcom/hypixel/hytale/server/core/modules/entitystats/EntityStatMap;"
        CMDA = "(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/universe/world/World;"
        EXPECT = {   # class: (members added, methods whose code changed, methods whose code changed only by an inlined constant)
            "CfgRows": (set(), {"<clinit>()V"}, {"header()[Ljava/lang/Object;"}),
            "MobCfg": ({("f", "HP_FLOOR", "I"), ("f", "HP_SIG", "Ljava/lang/String;"), ("f", "ON_HEALTH", "Ljava/lang/Runnable;"),
                        ("m", "floorFactor", "(D)D"), ("m", "hpAmount", "(ID)F")},
                       {"<clinit>()V", "apply(Ljava/util/Properties;Ljava/util/Properties;)V", "derive(Ljava/lang/String;)V"},
                       {"load()V", "reloadAll()V", "useDefaults()V"}),
            "MobLevel": ({("m", "baseOf", "(%sI)D" % ESMD), ("m", "amountOn", "(%sILjava/lang/String;)F" % ESMD), ("m", "same", "(FF)Z"),
                          ("m", "setMult", "(%sIIZZ)F" % ESMD), ("m", "refreshOne", "(%sII)Z" % ESMD),
                          ("m", "refreshWorld", "(Lcom/hypixel/hytale/server/core/universe/world/World;)I")},
                         {"setMult(%sIIZ)F" % ESMD}, set()),
            "MobCmds": ({("m", "healthLine", "(%sII)Ljava/lang/String;" % ESMD)},
                        {"inspect%s)[Ljava/lang/String;" % CMDA, "set%sLjava/lang/String;)Ljava/lang/String;" % CMDA}, set()),
            "SkyyMobsPlugin": (set(), {"setup()V", "shutdown()V"}, set()),
        }
        summary = []
        for cls_, (add_want, code_want, konst_want) in sorted(EXPECT.items()):
            ca, ma, ha = classfile(za.read("com/skyy/mobs/%s.class" % cls_))
            cb, mb, hb_ = classfile(zb.read("com/skyy/mobs/%s.class" % cls_))
            added, removed = set(mb) - set(ma), set(ma) - set(mb)
            check(added == add_want and not removed, "Z. %s: members added %s, removed %s (want %s)" % (cls_, sorted(added), sorted(removed), sorted(add_want)))
            ta, tb = mtexts(PREV_JAR, cls_), mtexts(JAR, cls_)
            changed = sorted(k for k in ta if k in tb and ta[k] != tb[k])
            konst = set(k for k in changed if same_but_consts(ta[k], tb[k]) and k not in code_want)
            real = set(k for k in changed if k not in konst)
            check(real == code_want and konst == konst_want, "Z. %s: code changed in %s, constant-only in %s (want %s / %s)" % (
                cls_, sorted(real), sorted(konst), sorted(code_want), sorted(konst_want)))
            summary.append("%s +%d members, code %s%s" % (cls_, len(added), " ".join(sorted(x.split("(")[0] for x in real)),
                                                        (" (constant only: %s)" % " ".join(sorted(x.split("(")[0] for x in konst))) if konst else ""))
        tm = mtexts(JAR, "MobCfg")
        check("MobCfg.ON_HEALTH" in tm["derive(Ljava/lang/String;)V"] and "MobCfg.HP_SIG" in tm["derive(Ljava/lang/String;)V"]
              and "strength.floor" in tm["apply(Ljava/util/Properties;Ljava/util/Properties;)V"], "Z. (MobCfg.derive holds the health signature, apply reads strength.floor)")
        print("Z. 0.1.1 -> 0.1.2: %d entries byte-identical, MobRefresh added, CfgFn = only its version string, CfgFile = the row count 25 -> 26; %s; "
              "manifest.json" % (same, "; ".join(summary)))

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
        PCfg = prev_cls("MobCfg")
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
        print("   HP table 0.1.1 -> 0.1.2 (floor 50):")
        for base in (36, 74, 200):
            print("     base %3d HP: %s" % (base, "; ".join("Lv %d %s %.0f -> %.0f" % (l_, d_[0].upper(), o_, h_)
                                                         for b_, l_, d_, o_, h_ in sorted(table, key=lambda t_: (t_[1], ("easy", "normal", "hard").index(t_[2])))
                                                         if b_ == base)))

    def section_fl():
        """FL: floor 0 = 0.1.1 EXACTLY - hpAmount vs SkyyMobs-0.1.1.jar's own hpMult bit for bit; then both jars' setMult on stand-in maps"""
        PCfg, PLvl = prev_cls("MobCfg"), prev_cls("MobLevel")
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
        check(not bad2, "FL. floor 0: 0.1.1's setMult and 0.1.2's on identical stand-in maps give identical amounts, max and health (spawn + "
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
        os.makedirs(lvbase)
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
          and [str(x) for x in hdr[5]] == ["levels", "strength", "bands", "plate"]
          and str(hdr[8]) == "Skyy_SkyyMobs/config.properties,Skyy_SkyyMobs/bands.properties", "K. header: %s" % [str(hdr[i]) for i in (0, 1, 2, 3, 4, 8)])
    keys = [r_[0] for r_ in rows]
    check(len(rows) == 26 and keys[0] == "part.levels", "K. 26 rows (0.1.1's 25 + strength.floor): %s" % keys)
    # 0.1.1: the short labels (Skyy's screenshot) and the Strength page numbers
    RW = dict((r_[0], r_) for r_ in rows)
    check([str(x) for x in hdr[6]] == ["Which mobs", "Strength", "Level bands", "Nameplate"], "K. 0.1.1 tab labels: %s" % [str(x) for x in hdr[6]])
    check(RW["strength.difficulty"][7] == "easy|Easy,normal|Normal,hard|Hard,custom|Custom" and RW["strength.difficulty"][4] == "normal",
          "K. Difficulty choices Easy / Normal / Hard / Custom (values 0.1's), default normal: %s" % RW["strength.difficulty"][7])
    check(RW["strength.difficulty"][10] == "Health / damage per level: Easy 4% / 2%, Normal 6% / 3%, Hard 8% / 4%. Custom = the two rows below.",
          "K. the Difficulty help line carries the numbers: %r" % RW["strength.difficulty"][10])
    check(RW["strength.hpCap"][4] == "6" and RW["strength.dmgCap"][4] == "3.5" and "x6 never clips Hard at Lv 60, which is x5.72" in RW["strength.hpCap"][10]
          and "x3.5 never clips Hard at Lv 60, which is x3.36" in RW["strength.dmgCap"][10], "K. caps x6 / x3.5 + their help: %r / %r" % (
              RW["strength.hpCap"][10], RW["strength.dmgCap"][10]))
    check(RW["strength.hp"][4] == "4" and RW["strength.dmg"][4] == "2", "K. Custom rows unchanged (4 / 2)")
    # 0.1.2: the floor row + the two help texts
    check(RW.get("strength.floor") == FLOOR_ROW, "K. 0.1.2 row strength.floor: %s" % RW.get("strength.floor"))
    check(keys.index("strength.floor") == keys.index("strength.dmgCap") + 1, "K. the floor row sits after the damage cap on the Strength page")
    check(RW["strength.hp"][10] == HP_HELP and RW["strength.hpCap"][10] == HPCAP_HELP, "K. the strength.hp / hpCap help texts: %r / %r" % (
        RW["strength.hp"][10], RW["strength.hpCap"][10]))

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
    r = op("set", "strength.hpCap", "5.5", None, None, "yes", "console")
    check(str(r[0]) == "ok" and float(Cfg.HP_CAP) == 5.5 and float(Cfg.hpMult(60)) == 5.5, "K. a lower health cap through the kit clips Hard Lv 60 at once (x5.5)")
    r = op("set", "strength.hpCap", None, None, None, "yes", "console")
    check(str(r[0]) == "ok" and float(Cfg.HP_CAP) == 6.0 and str(op("get", "strength.hpCap")) == "6", "K. Default puts the health cap back to x6")
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
    print("K. config kit: 26 rows (4 categories), get = defaults, set live + refused + confirm (the floor row too), 5 table ops through the "
          "real kit + the reload routine, hand edit + reload op")

    # ---------------- S. start twice (no churn)
    sd = os.path.join(SCRATCH, "twice", "mods")
    sh = os.path.join(sd, "Skyy_SkyyMobs")
    shutil.rmtree(os.path.dirname(sd), ignore_errors=True)
    os.makedirs(sh)

    S_MG = []

    def start():        # 0.1.1: in setup()'s order - MobMig.run, MobCfg.load, CfgPub.start
        Cfg.DIR = Paths.get(sh)
        Cfg.FILE = Paths.get(os.path.join(sh, "config.properties"))
        Cfg.BANDS = Paths.get(os.path.join(sh, "bands.properties"))
        S_MG.append(str(Mig.run(Cfg.DIR)))
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
    check(S_MG == ["", ""] and MARK.encode("latin-1") in s1[os.path.join("Skyy_SkyyMobs", "config.properties")][0],
          "S. a fresh 0.1.1 folder is never updated (the seeded file carries the marker): %s" % S_MG)
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

    # ---------------- O / U / Z (now 0.1.1 -> 0.1.2) + Q / FL / RA / IN / LV (0.1.2)
    for _nm, _fn, _a in (("O", section_o, (hdr,)), ("U", section_u, ()), ("Z", section_z, ()), ("Q", section_q, ()), ("FL", section_fl, ()),
                         ("RA", section_ra, ()), ("IN", section_in, ()), ("LV", section_lv, ())):
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
    check(sorted(regs) == sorted(PKG + c for c in ("LevelHook", "LevelDamage", "LevelDamageU")) and len(set(regs)) == 3,
          "P. one registerSystem per class (the hook WITHOUT a fallback, the damage system + its unordered fallback): %s" % regs)
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
    check('" (caps x"' in st_c and "MobCmds.f2((F)" in st_c and "String.replace((CC)" in st_c and '"; "' in st_c,
          "P. 0.1.1: the ready line prints the caps and appends the update's lines")
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
    k_sm = [i for i, x in enumerate(rl_) if "MobLevel.setMult((Lcom/hypixel/hytale/server/core/modules/entitystats/EntityStatMap;IIZZ)F)" in x]
    check(len(k_sm) == 1 and "iconst_0" in rl_[k_sm[0] - 1] and "iconst_0" in rl_[k_sm[0] - 2], "P. 0.1.2: refreshOne calls setMult(m, hi, level, false, false) - never full, never heal")
    sm_ = code("MobLevel", "setMult")
    check("MobCfg.HEAL_ON_LOAD" in sm_ and "MobCfg.hpAmount" in sm_ and "MobLevel.baseOf" in sm_, "P. 0.1.2: setMult puts hpAmount(level, baseOf); the 4-argument form passes strength.healOnLoad")
    ins_, hl_ = code("MobCmds", "inspect"), code("MobCmds", "healthLine")
    check("MobCmds.healthLine" in ins_ and "MobCfg.hpMult" not in ins_ and "MobLevel.amountOn" in hl_ and "MobCfg.hpAmount" in hl_,
          "P. 0.1.2: /mobs inspect prints healthLine (the modifier on the mob vs the setting), no longer hpMult")
    check("MobLevel.amountOn" in code("MobCmds", "set"), "P. 0.1.2: /mobs set reports the multiplier it applied")
    oa = code("MobLevel", "onAdd")
    check("savedLevel" in oa and "KEPT" in oa and "whyNot" in oa and "lookupMob" in oa and "levelFor" in oa and "apply" in oa,
          "P. onAdd: save slot, session memory, who-filter, lookup, roll, apply")
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


def guard_scratch():
    """None when --dir may be used (and deleted): a folder INSIDE a task folder of tools/dev/scratch (tools/dev/scratch/<task>/<sub>) -
    never the scratch root or a top-level task folder (other agents' live work sits there) - that is missing, empty or this harness's
    own (its MARKER file). Else the reason it is refused (nothing is deleted then)."""
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
    if os.path.lexists(SCRATCH):
        if os.path.islink(SCRATCH) or not os.path.isdir(SCRATCH):
            return "exists and is not a plain folder"
        if os.listdir(SCRATCH) and not os.path.isfile(os.path.join(SCRATCH, MARKER)):
            return "exists, is not empty and is not this harness's folder (no %s)" % MARKER
    return None


def main():
    if not os.path.isfile(JAR):
        print("no jar at", JAR, "- build it first")
        return 1
    for p_, what in ((PREV_JAR, "the 0.1.1 jar (SET pin) for O / Q / FL / U / Z"), (OLD_JAR, "the 0.1 jar for U / V"), (MENU_JAR, "SkyyMenu 0.3.5 (SET pin) for V")):
        if not os.path.isfile(p_):
            print("missing %s: %s" % (what, p_))
            return 1
    why = guard_scratch()
    if why:
        print("--dir refused (%s): %s - nothing was deleted" % (why, SCRATCH))
        return 1
    SCRATCH_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)          # start clean: missing, empty or this harness's own (marker checked above)
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
    if not KEEP and SCRATCH_OK[0] and os.path.isfile(os.path.join(SCRATCH, MARKER)):
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code_)
