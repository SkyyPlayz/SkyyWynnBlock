"""Harness for SkyyIslands 0.5.24 (bug 4 lag part 5: empty island worlds unload; tools/islands_0_5_24_patch.py).
Build first: python tools/islands_0_5_24_patch.py && python SkyyIslands/build_skyyislands_0.5.24.py

    python SkyyIslands/test_skyyislands_0.5.24.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; real IslandStore files in scratch, -Xverify:all):
  A / C / AA  verify, compare 0.5.23 -> 0.5.24 (exactly the planned members + the new IsleUnload; only the manifest changes), audit
  UNLOAD  IsleUnload.decide: retired worlds after 60 s empty, current islands after islands.unloadEmptySeconds only when no online
          player calls them home, never with players / while created or reset / 120 s after a trip / for a world we do not own /
          NEVER-listed; the setting 0 = nothing; the clock resets when someone comes and is forgotten for unloaded worlds; openSaved:
          busy -> refused before any engine call, a load in flight is SHARED (one future); unload / sweep without an engine = nothing;
          the generated script: removeWorld only in IsleUnload.unload, the DeleteOnRemove guard before it, openSaved = loadWorld (no
          addWorld), loadedWorld hides a world being unloaded, the scheduler 60 s / 30 s, no RemovalConditions / DeleteOnRemove written
  EARLY / IDS / BOSS / CLEAR / TIME  the 0.5.23 harness phases on the 0.5.24 jar (regression)
  LIVE  a scratch COPY of the live Skyy_SkyyIslands + the names of the live world folders (listing only): the retired worlds are
        exactly the reset backups (world.old), every current island unloads only when its owner is not online, nothing changed on disk
Not testable without the game (UNVERIFIED): the real removeWorld / loadWorld (SkyyShards probes S1 / S2 + the smoke test).
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("isl523", os.path.join(HERE, "test_skyyislands_0.5.23.py"))
T23 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T23)          # its phases + its compare wrapper (only the manifest may change among non-class entries)

VERSION = "0.5.24"
OLD = "0.5.23"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "unl", "h")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
LIVE_WORLDS = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "universe", "worlds")
ADDED = ["IsleUnload"]
EXPECT = {
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
    "IslandCfg": ["+f UNLOAD_S", "~<clinit>", "~m load"],
    "IslandStore": ["~m loadedWorld"],
    "IslandCmd": ["~m openSaved", "~m goAt"],
    "SkyyIslandsPlugin": ["+f unloadTicker", "~m setup", "~m shutdown"],
    "IslandJoin": ["~m accept"],
}
KO = "00000000-0000-4000-8000-0000000b0524"
K2 = "00000000-0000-4000-8000-0000000b0525"
KM = "00000000-0000-4000-8000-0000000b0526"     # a co-op member of KO
WOLD = "skyy-island-" + KO
WC = "skyy-island-" + KO + "-r1"
W2 = "skyy-island-" + K2


def gen_src():
    return open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()


def body(gen, start):
    s = gen[gen.index(start):]
    return s[:s.index('}""")')]


# ================================================================================================ UNLOAD
def run_unload(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong, JInt
    K = HK.Child(out)
    E = T23.Env(scratch, jar, "unl")
    Cfg, St, U = E.Cfg, E.St, E.P("IsleUnload")
    HashSet, Long, System = JClass("java.util.HashSet"), JClass("java.lang.Long"), JClass("java.lang.System")
    E.files({KO: {"v": "5", "world": WC, "world.prev": WOLD, "world.old": WOLD, "resets": "1", "members": KM},
             K2: {"v": "5", "world": W2}})
    K.check(bool(St.isIslandWorld(JString(WOLD))) and bool(St.isRetired(JString(WOLD))) and not bool(St.isRetired(JString(WC)))
            and not bool(St.isRetired(JString(W2))), "UNLOAD the fixture: the reset backup is retired, both current islands are not")
    K.eq(int(Cfg.UNLOAD_S), 600, "UNLOAD islands.unloadEmptySeconds defaults to 600 s (a file without the line)")
    none = HashSet()
    now = int(System.currentTimeMillis()) - 10 * 3600 * 1000   # far from any touch()

    def d(wn, players=0, homes=None, t=0):
        return int(U.decide(JString(wn) if wn is not None else None, JInt(players), homes if homes is not None else none, JLong(now + t)))
    # retired: 60 s
    K.check(d(WOLD) == 1 and d(WOLD, t=59999) == 1 and d(WOLD, t=60000) == 2, "UNLOAD a retired world: the clock starts, unload at 60 s empty")
    K.check(d(WOLD, players=1, t=61000) == 0 and not U.EMPTY.containsKey(JString(WOLD)), "UNLOAD ... a player there -> kept, the clock reset")
    U.SEEN.clear()   # (review fix 2 keeps a world a player was in for the setting - tested below)
    K.check(d(WOLD, t=62000) == 1, "UNLOAD ... empty again -> the clock starts over")
    homes = HashSet()
    homes.add(JString(KO))
    U.EMPTY.clear()
    K.check(d(WOLD, homes=homes) == 1 and d(WOLD, homes=homes, t=60000) == 2, "UNLOAD a retired world unloads even while its owner is online")
    # current islands: the setting, and only when no online player calls it home
    U.EMPTY.clear()
    K.check(d(WC) == 1 and d(WC, t=599999) == 1 and d(WC, t=600000) == 2, "UNLOAD a current island, owner offline: unload at 600 s empty")
    K.check(d(WC, homes=homes, t=600001) == 0 and not U.EMPTY.containsKey(JString(WC)), "UNLOAD ... its owner (or a co-op member on it) online -> kept, clock reset")
    hk = str(St.homeKey(JClass("java.util.UUID").fromString(KM)))
    K.check(hk == KO, "UNLOAD a co-op member's home key = the owner's island (the sweep's homes set): %s" % hk)
    h2 = HashSet()
    h2.add(JString(K2))
    U.EMPTY.clear()
    K.check(d(WC, homes=h2) == 1 and d(WC, homes=h2, t=600000) == 2, "UNLOAD ... another island's owner online does not keep it")
    # the setting
    Cfg.UNLOAD_S = 30
    U.EMPTY.clear()
    K.check(d(WOLD) == 1 and d(WOLD, t=30000) == 2 and d(WC, t=30000) == 1 and d(WC, t=60000) == 2,
            "UNLOAD the setting 30 s: retired ones at min(60, setting), current ones at the setting")
    Cfg.UNLOAD_S = 0
    U.EMPTY.clear()
    K.check(d(WOLD) == 0 and d(WOLD, t=999999) == 0 and d(WC, t=999999) == 0 and U.EMPTY.isEmpty() and int(U.limitMs(True)) < 0,
            "UNLOAD the setting 0 = never (retired worlds included), no clock kept")
    K.check(int(U.sweep()) == 0, "UNLOAD sweep with the setting 0 does nothing")
    Cfg.UNLOAD_S = 600
    # never
    for wn, why in (("default", "the default world"), ("skywynn_zones2", "a zone world"), ("skyy-island-unknown", "an unregistered island name"), (None, "null")):
        K.check(d(wn) == 0 and d(wn, t=10 ** 7) == 0, "UNLOAD never: %s" % why)
    St.CREATING.put(JString(KO), Long(1))
    K.check(d(WC) == 0 and d(WOLD) == 0, "UNLOAD never while the owner's island is being created")
    St.CREATING.clear()
    St.RESETTING.put(JString(KO), Long(1))
    K.check(d(WC) == 0 and d(WOLD) == 0, "UNLOAD never while the owner's island is being reset")
    St.RESETTING.clear()
    U.NEVER.put(JString(W2), JClass("java.lang.Boolean").TRUE)
    K.check(d(W2) == 0 and d(W2, t=10 ** 7) == 0, "UNLOAD never a world on the NEVER list (its config said delete on remove)")
    U.NEVER.clear()
    U.EMPTY.clear()
    U.touch(JString(W2))
    real = int(System.currentTimeMillis())
    K.check(int(U.decide(JString(W2), JInt(0), none, JLong(real + 119000))) == 0, "UNLOAD never within 120 s after a trip to it (touch)")
    K.check(int(U.decide(JString(W2), JInt(0), none, JLong(real + 121000))) == 1, "UNLOAD ... after 120 s the empty clock starts")
    U.USED.clear()
    # review fix 2: ANY player inside within the setting keeps it (visitors / admins), retired worlds too; arrivals count
    U.EMPTY.clear(); U.SEEN.clear()
    K.check(d(WOLD, players=1) == 0 and U.SEEN.containsKey(JString(WOLD)), "UNLOAD review 2: a player counted inside -> seen")
    K.check(d(WOLD, t=60000) == 0 and d(WOLD, t=599999) == 0, "UNLOAD review 2: a retired world a visitor was in stays for the full setting (600 s), not 60 s")
    K.check(d(WOLD, t=600000) == 1 and d(WOLD, t=660000) == 2, "UNLOAD review 2: ... then the normal empty clock")
    U.EMPTY.clear(); U.SEEN.clear()
    U.arrive(JString(W2))
    real2 = int(System.currentTimeMillis())
    K.check(U.USED.containsKey(JString(W2)) and int(U.decide(JString(W2), JInt(0), none, JLong(real2 + 300000))) == 0,
            "UNLOAD review 2: an arrival (AddPlayerToWorldEvent: /tp, return point, other mods) keeps it for the setting")
    K.check(int(U.decide(JString(W2), JInt(0), none, JLong(real2 + 601000))) == 1, "UNLOAD review 2: ... after the setting the empty clock starts")
    jb = gen_src()
    jb = jb[jb.index("M(ijoin, r"):][:600]
    K.check("@PKG@.IsleUnload.arrive(w.getName())" in jb, "UNLOAD review 2: the AddPlayerToWorldEvent hook calls arrive()")
    U.EMPTY.clear(); U.SEEN.clear(); U.USED.clear()
    # busy / openSaved / loadedWorld
    U.BUSY.put(JString(WC), JClass("java.lang.Boolean").TRUE)
    K.check(bool(U.busy(JString(WC))) and St.loadedWorld(JString(WC)) is None, "UNLOAD busy() + loadedWorld hides a world being unloaded")
    Cmd = E.P("IslandCmd")
    try:
        Cmd.openSaved(JString(WC))
        K.check(False, "UNLOAD openSaved while busy must refuse")
    except Exception as e:
        K.check("being saved" in str(e), "UNLOAD openSaved while the world is being saved: refused (try again): %s" % str(e)[:80])
    K.check(U.USED.containsKey(JString(WC)), "UNLOAD openSaved touches the world (the sweep leaves it alone)")
    U.BUSY.clear()
    f = JClass("java.util.concurrent.CompletableFuture")()
    U.LOADING.put(JString(W2), f)
    K.check(Cmd.openSaved(JString(W2)) == f and Cmd.openSaved(JString(W2)) == f, "UNLOAD a load in flight is SHARED: two /island calls get the same future")
    U.LOADING.clear()
    U.LOADING.put(JString(W2), JClass("java.util.concurrent.CompletableFuture").completedFuture(None))
    U.LOADING.put(JString(WC), JClass("java.util.concurrent.CompletableFuture")())
    U.sweep()
    K.check(not U.LOADING.containsKey(JString(W2)) and U.LOADING.containsKey(JString(WC)),
            "UNLOAD review 1: the sweep drops a finished load future (no pinned World), keeps a running one")
    U.LOADING.clear()
    ob1 = body(gen_src(), "public static synchronized java.util.concurrent.CompletableFuture openSaved(String name)")
    K.check("if (pf != null) @PKG@.IsleUnload.LOADING.remove(name);" in ob1 and "if (r == 1) LOADING.remove(wn);" in body(gen_src(), "public static int unload(String wn)"),
            "UNLOAD review 1: openSaved and a successful unload forget a finished load future")
    K.check(int(U.unload(None)) == 0, "UNLOAD unload(null) = nothing")
    U.BUSY.put(JString(WC), JClass("java.lang.Boolean").TRUE)
    K.check(int(U.unload(JString(WC))) == 0 and U.BUSY.containsKey(JString(WC)), "UNLOAD unload while another unload of it runs = nothing")
    U.BUSY.clear()
    U.EMPTY.put(JString(WC), Long(1))
    r = int(U.unload(JString(WC)))
    K.check(r in (0, -1) and not U.BUSY.containsKey(JString(WC)) and not U.EMPTY.containsKey(JString(WC)),
            "UNLOAD unload without an engine: nothing removed, busy + clock cleared (%d)" % r)
    try:
        n = int(U.sweep())
        K.check(n == 0, "UNLOAD sweep without an engine: nothing")
    except Exception as e:
        K.check(False, "UNLOAD sweep without an engine threw: %s" % e)
    U(JInt(0), None).run()
    K.check(True, "UNLOAD the scheduled task's run() never throws")
    # the generated script
    gen = gen_src()
    K.check(gen.count("removeWorld(") == 1 and "uni.removeWorld(wn)" in body(gen, "public static int unload(String wn)"),
            "UNLOAD Universe.removeWorld is called in IsleUnload.unload only")
    ub = body(gen, "public static int unload(String wn)")
    K.check(ub.index("c.isDeleteOnRemove() || c.isDeleteOnUniverseStart()") < ub.index("uni.removeWorld(wn)"),
            "UNLOAD the DeleteOnRemove / DeleteOnUniverseStart guard runs before removeWorld (never a deleting removal)")
    K.check(ub.index("w.getPlayerCount() > 0") < ub.index("uni.removeWorld(wn)"), "UNLOAD the player count is checked again right before removeWorld")
    ob = body(gen, "public static synchronized java.util.concurrent.CompletableFuture openSaved(String name)")
    K.check("uni.loadWorld(name)" in ob and "uni.addWorld" not in ob, "UNLOAD openSaved reopens with Universe.loadWorld (no addWorld)")
    K.check("setDeleteOnRemove" not in gen and "setRemovalConditions" not in gen and "safeRemoveInstance" not in gen,
            "UNLOAD nothing sets DeleteOnRemove / RemovalConditions (the engine's deleting removal is never used)")
    K.check("new @PKG@.IsleUnload(0, null), 60L, 30L" in gen and "this.unloadTicker.cancel(false)" in gen, "UNLOAD the sweep: first after 60 s, every 30 s, cancelled at shutdown")
    K.check("islands.unloadEmptySeconds=600" in gen and "'field:IslandCfg.UNLOAD_S@config.properties:islands.unloadEmptySeconds'" in gen,
            "UNLOAD the Server Setup row + the default config line")
    sb = body(gen, "public static int sweep()")
    K.check("n >= PER_SWEEP" in sb and "EMPTY.remove(ks[i])" in sb, "UNLOAD sweep: at most PER_SWEEP unloads, forgets clocks of unloaded worlds")
    K.save()


# ================================================================================================ LIVE
def run_live(out, jar, scratch, home):
    from jpype import JClass, JString, JLong, JInt
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    St, Cfg, U = P("IslandStore"), P("IslandCfg"), P("IsleUnload")
    Paths = JClass("java.nio.file.Paths")
    St.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.load("")
    K.check(int(Cfg.UNLOAD_S) == 600, "LIVE the live config (no unloadEmptySeconds line yet) -> 600 s: %s" % Cfg.UNLOAD_S)
    St.DIR = Paths.get(os.path.join(home, "islands"))
    St.IO = None
    St.STOPPING = False
    St.loadIslandWorlds()
    d = os.path.join(home, "islands")
    props = {}
    for f in sorted(os.listdir(d)):
        if f.endswith(".properties"):
            kv = {}
            for line in open(os.path.join(d, f), encoding="latin-1"):
                if "=" in line and not line.startswith("#"):
                    a, b = line.rstrip("\n").split("=", 1)
                    kv[a] = b
            props[f[:-11]] = kv
    want_retired = set()
    current = {}
    for k, kv in props.items():
        if kv.get("world"):
            current[kv["world"]] = k
        for w in kv.get("world.old", "").split(","):
            if w.strip():
                want_retired.add(w.strip())
    names = sorted(os.listdir(LIVE_WORLDS)) if os.path.isdir(LIVE_WORLDS) else []
    isl = [n for n in names if n.startswith("skyy-island-")]
    K.notes.append("live: %d island files, %d world folders (%d island), retired %s" % (len(props), len(names), len(isl), sorted(want_retired)))
    for n in isl:
        K.check(bool(St.isIslandWorld(JString(n))), "LIVE %s is a registered island world" % n[-20:])
        K.check(bool(St.isRetired(JString(n))) == (n in want_retired), "LIVE %s retired = %s (world.old)" % (n[-20:], n in want_retired))
    for n in ("default", "skywynn_zones", "skywynn_zones2"):
        K.check(not bool(St.isIslandWorld(JString(n))), "LIVE %s is not ours (never unloaded by SkyyIslands)" % n)
    # Skyy online on profile 3: their p3 island stays; every other island unloads (retired after 60 s, others after 600 s)
    homes = JClass("java.util.HashSet")()
    active = [k for k in props if k.endswith("-p3")]
    for k in active:
        homes.add(JString(k))
    now = 10 ** 12
    for n in isl:
        U.EMPTY.clear()
        first = int(U.decide(JString(n), JInt(0), homes, JLong(now)))
        if n in want_retired:
            K.check(first == 1 and int(U.decide(JString(n), JInt(0), homes, JLong(now + 60000))) == 2, "LIVE retired %s unloads after 60 s empty" % n[-20:])
        elif current.get(n) in active:
            K.check(first == 0, "LIVE %s = the online player's active island -> stays loaded" % n[-20:])
        else:
            K.check(first == 1 and int(U.decide(JString(n), JInt(0), homes, JLong(now + 599000))) == 1
                    and int(U.decide(JString(n), JInt(0), homes, JLong(now + 600000))) == 2, "LIVE %s (owner offline / other profile) unloads after 600 s empty" % n[-20:])
    K.check(HK.tree_hash(home) == h0, "LIVE no file of the copy changed")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("unload", run_unload), ("early", T23.run_early), ("ids", T23.run_ids), ("boss", T23.run_boss), ("clear", T23.run_clear),
                   ("time", T23.run_time), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
