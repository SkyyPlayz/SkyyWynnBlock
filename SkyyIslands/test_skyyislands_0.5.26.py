"""Harness for SkyyIslands 0.5.26 (blocked archipelago islands move out + /island archipelago retry; tools/islands_0_5_26_patch.py).
Build first: python tools/islands_0_5_26_patch.py && python SkyyIslands/build_skyyislands_0.5.26.py

    python SkyyIslands/test_skyyislands_0.5.26.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the 0.5.25 harness's stand-in IsleApi over a BLOCK MAP, real IslandStore files in scratch,
-Xverify:all):
  S      static  the patch re-runs to identical bytes; no new system / command / listener; no shift = the 0.5.25 layout cell for cell; 42 moved
                 bridges; every moved island = the island moved as one piece along its spoke
  A / C / AA  verify, compare 0.5.25 -> 0.5.26 (exactly the planned members + the 3 command classes), audit
  DATA   ArchiIsles.runsFor (Java) for every element x every spot of its islands = the build-time cells (the moved bridges' VI index too)
  SHIFT  a player's block on the Foraging island's spot -> built 12 further out (bridges planned for it, the door / chest at the moved
         cells, done+12); blocked at 0 and 12 -> 24; blocked at all three -> skipped, the item once; Farming / Mining / Ranching moved: the
         farm water, the cave copper regrow and the pen animals at the moved spots (nothing at the old spot); START TWICE changes nothing
  RETRY  /island archipelago retry (IsleLife.archiRetry + the RETRY queue run by archiOnce): the blocker gone -> the skipped island +
         its bridges build at their own spot, the door is recorded, the shard item is NOT given again; still blocked -> tries 12 / 24 again,
         stays skipped, no second item; nothing skipped / not started / switched off / bad file answers; a queued retry waits for the
         owner's current world; the status line
  PLACE  island:fn:place with Object[]{UUID, id} answers a moved island's place where it stands; the String form + island:places unchanged
  FIX    the critic fixes: shiftOf trusts a "done" value over a stale marker; a moved spot's unloaded chunk counts as blocked after
         ARCHI_WAIT (a normal spot still waits); a queued retry survives another world; one pending relight per world
  CMD    the 3 command classes: hytale:Adventurer on all of them, no requirePermission (admin checks in execute), 2 usage variants
  REG    the 0.5.25 phases (archi, door, fix2, life, cfg) + the 0.5.24 ones (unload, early, ids, boss, clear, time) on the 0.5.26 jar
  LIVE   a scratch COPY of the live Skyy_SkyyIslands: every island file reads, archiStatus answers for each, nothing changed on disk;
         LIVE2 start twice (the 0.5.25 one-time update path on the copy)
Not testable without the game (UNVERIFIED): chunk loading at a moved island's far spot (cx -3), the client look of the moved bridges, the
real command dispatch (/island archipelago retry <player> picking the 2-argument variant).
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("isl525", os.path.join(HERE, "test_skyyislands_0.5.25.py"))
T25 = importlib.util.module_from_spec(_spec)
_argv = list(sys.argv)
_spec.loader.exec_module(T25)
sys.argv[:] = _argv
T24, T23 = T25.T24, T25.T23

VERSION = "0.5.26"
OLD = "0.5.25"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "isl026", "ih")))
GEN = os.path.join(HERE, "build_skyyislands_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyislands_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "islands_0_5_26_patch.py")
LIVE_DIR = T25.LIVE_DIR
ADDED = ["IslandArchiCmd", "IslandArchiRetryCmd", "IslandArchiRetryForCmd"]
EXPECT = {   # checked by hand 2026-10-24: the version texts (CfgFile / CfgFn / CfgRows), ArchiIsles (spots, moved bridges, runsFor, places),
            # IsleLife (shift, retry, moved door / pen / cave, the texts), IsleState.archiSh, PlaceFn (UUID form), the chunk ranges, /island's sub list
    "IslandCfg": ["~m load"], "RelightNow": ["~m run"], "RelightTask": ["+f PENDING", "+<clinit>", "~m run", "~m schedule"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "ArchiIsles": ["+f BA", "+f BB", "+f PRETTY", "+f SDX", "+f SDZ", "+f SHIFT", "+f VDATA", "+f VI", "+f VRUNS", "+m dx", "+m dz", "+m isDone",
                   "+m moved", "+m placeFor", "+m runsFor", "+m shiftOf", "~<clinit>"] + ["+f V%d" % i for i in range(42)],
    "IsleLife": ["+f ARCHI_RETRIED", "+f ARCHI_SHIFTED", "+f ARCHI_WAIT", "+f RETRY", "+m archiRetry", "+m archiRetryDue", "+m archiRetryNow", "+m archiStatus", "~<clinit>", "~m archiDoor",
                 "~m archiOnce", "~m archiTick", "+m caveRegrow", "-m caveRegrow", "~m ranchSpawn"],
    "IsleState": ["+f archiMv", "+f archiNullAt", "+f archiSh"], "PlaceFn": ["~m apply"], "TintFix": ["+f R", "~m fix"],
    "IslandCmd": ["~c "], "SkyyIslandsPlugin": ["~m setup"], "IslandHomes": ["~<clinit>"],
}
KO = T25.KO
WC = T25.WC


def layout():
    """the 0.5.26 generated script's layout (S3_ONLY: no JVM, no build) - + the moved islands / bridges"""
    os.environ["S3_ONLY"] = "1"
    spec = importlib.util.spec_from_file_location("gen526", GEN)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except ImportError:
        pass
    del os.environ["S3_ONLY"]
    return m


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    for w in ("registerSystem(", "registerCommand(", "registerGlobal("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    m = layout()
    m0 = T25.layout()
    K.check([e["cells"] for e in m.ARCHI] == [e["cells"] for e in m0.ARCHI] and [e["name"] for e in m.ARCHI] == [e["name"] for e in m0.ARCHI],
            "S no shift = the 0.5.25 layout cell for cell")
    K.eq(len(m.ARCHI_BV), 42, "S 42 moved bridges (5 spokes x 2 + 4 ring bridges x 8)")
    import math
    for nm in m.ARCHI_ISL:
        c0 = m.ARCHI[m.ARCHI_IDX[nm]]["centre"]
        for s in (1, 2):
            dx, dz = m.archi_vec(nm, s)
            e = m.ARCHI_ISV[(nm, s)]
            ok = e["cells"] == dict(((x + dx, y, z + dz), b) for (x, y, z), b in m.ARCHI[m.ARCHI_IDX[nm]]["cells"].items())
            out_ = math.hypot(c0[0] + dx - 8, c0[1] + dz - 8) - math.hypot(c0[0] - 8, c0[1] - 8)
            K.check(ok and abs(out_ - m.ARCHI_SHIFTS[s]) < 1.0, "S %s spot %d = moved as one piece %s, %.1f blocks further from the spawn" % (nm, s, (dx, dz), out_))
    # every moved bridge starts and ends at its islands (a deck cell next to each end's column at its spot)
    bad = []
    for (bn, sa, sb), cells in sorted(m.ARCHI_BV.items()):
        pa, pb = m.ARCHI_BENDS[bn]
        for p_, s_ in ((pa, sa), (pb, sb)):
            tops = m.S3_TOPS if p_ is None else m.ARCHI_ISV[(p_, s_)]["tops"]
            if not any((x + a, z + b) in tops for (x, y, z) in cells for a in (-1, 0, 1) for b in (-1, 0, 1)):
                bad.append((bn, sa, sb, p_))
    K.check(not bad, "S every moved bridge reaches both of its islands: %s" % bad[:4])
    K.check("ArchiIsles.runsFor(owner, e)" in g and "archipelago retry" in g and "public IslandArchiCmd()" in g, "S the new code is in the script")
    K.save()


def cells_of(Arc, runs):
    out = {}
    pal = [str(x) for x in Arc.PAL]
    r = list(runs)
    for i in range(0, len(r), 5):
        for k in range(r[i + 4]):
            out[(r[i + 1] + k, r[i + 2], r[i + 3])] = pal[r[i]]
    return out


def run_data(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    m = layout()
    E = T25.env(scratch, jar, "data")
    Life, Arc = E.Life, E.P("ArchiIsles")
    import itertools
    n = 0
    bad = []
    for asg in [(0,) * 5, (1,) * 5, (2,) * 5, (1, 2, 0, 2, 1), (2, 0, 1, 0, 2), (0, 1, 2, 1, 0), (2, 2, 1, 1, 0), (1, 0, 0, 2, 2), (0, 2, 2, 0, 1)]:
        a = dict(zip(m.ARCHI_ISL, asg))
        Life.archiSet(JString(KO), [JString("archi.shift." + k) for k in m.ARCHI_ISL], [JString(str(m.ARCHI_SHIFTS[a[k]]) if a[k] else "") for k in m.ARCHI_ISL])
        want = m.archi_at(a)
        for e in range(int(Arc.N)):
            got = cells_of(Arc, Arc.runsFor(JString(KO), e))
            n += 1
            if got != want[e]:
                bad.append((asg, m.ARCHI[e]["name"], len(got), len(want[e])))
    # every (bridge, sa, sb) at least once
    seen = set()
    for (bn, sa, sb) in m.ARCHI_BV:
        pa, pb = m.ARCHI_BENDS[bn]
        a = dict((k, 0) for k in m.ARCHI_ISL)
        if pa:
            a[pa] = sa
        a[pb] = sb
        Life.archiSet(JString(KO), [JString("archi.shift." + k) for k in m.ARCHI_ISL], [JString(str(m.ARCHI_SHIFTS[a[k]]) if a[k] else "") for k in m.ARCHI_ISL])
        e = m.ARCHI_IDX[bn]
        got = cells_of(Arc, Arc.runsFor(JString(KO), e))
        n += 1
        seen.add((bn, sa, sb))
        if got != m.ARCHI_BV[(bn, sa, sb)]:
            bad.append(("bv", bn, sa, sb))
    K.check(not bad and len(seen) == 42, "DATA runsFor = the build-time cells for %d element x spot cases (all 42 moved bridges): %s" % (n, bad[:4]))
    Life.archiSet1(JString(KO), JString("archi.shift.forage"), JString("junk"))
    K.eq(int(Arc.shiftOf(JString(KO), m.ARCHI_IDX["forage"])), 0, "DATA a junk archi.shift value = its own spot")
    K.check(bool(Arc.isDone("done")) and bool(Arc.isDone("done+12")) and not bool(Arc.isDone("skip:built")) and not bool(Arc.isDone(None)) and not bool(Arc.isDone("doneX")),
            "DATA isDone: done / done+12 yes, skip / null / doneX no")
    K.save()


def blocker(m, nm, spots):
    """a grass cell of island nm at each spot in `spots` that no other part (any spot) ever uses"""
    other = set()
    for (n2, s2), e in m.ARCHI_ISV.items():
        if not (n2 == nm and s2 in spots):
            other.update(e["cells"])
    for c in m.ARCHI_BV.values():
        other.update(c)
    for e in m.ARCHI:
        if e["kind"] != "island":
            other.update(e["cells"])
    out = []
    for s in spots:
        e = m.ARCHI_ISV[(nm, s)]
        cs = sorted(c for c, b in e["cells"].items() if b == "Soil_Grass" and c not in other)
        out.append(cs[len(cs) // 2])
    return out


def expected_map(m, asg, extra=None):
    want = dict(m.S3_L)
    for c in m.archi_at(asg):
        want.update(c)
    want.update(extra or {})
    return want


def run_shift(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    zero = dict((k, 0) for k in m.ARCHI_ISL)
    # ---- 1. Foraging blocked at its own spot -> 12 further out
    E = T25.env(scratch, jar, "sh1")
    rows = T25.rows_with_owner()
    Life, IS = E.Life, E.P("IsleState")
    A = T25.fresh(m)
    b0 = blocker(m, "forage", [0])[0]
    A["B"][b0] = "Furniture_Village_Bench"
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    T25.drive(Life, IS, st, A, rows)
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    a1 = dict(zero, forage=1)
    want = expected_map(m, a1, {b0: "Furniture_Village_Bench"})
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(str(get("archi")) == "1" and str(get("archi.forage")) == "done+12" and str(get("archi.shift.forage")) == "12" and not diff,
            "SHIFT 1 Foraging blocked: built 12 further out, its 3 bridges planned for it, everything else normal, the bench untouched: %s %s" % (get("archi.forage"), diff[:3]))
    K.check(all(str(get("archi." + e["name"])) == "done" for e in m.ARCHI if e["name"] != "forage"), "SHIFT 1 every other part done at its own spot")
    fd = m.ARCHI_ISV[("forage", 1)]["door"]
    doors = dict((k, c) for k, c, pk in A["doors"])
    K.check(doors.get("foraging") == tuple(fd) and len(A["doors"]) == 6, "SHIFT 1 the Foraging door recorded at the moved cell %s: %s" % (fd, doors.get("foraging")))
    fch = m.ARCHI_ISV[("forage", 1)]["chests"][0][:3]
    K.check(any(c == fch for c, s in A["chests"]) and len(A["chests"]) == 4, "SHIFT 1 the saplings chest filled at the moved cell %s" % (fch,))
    K.check(int(Life.ARCHI_SHIFTED.get()) >= 1 and not A["given"], "SHIFT 1 counted, no shard item (the island is there)")
    st_ = str(Life.archiStatus(JString(KO)))
    K.check("15 of 15 parts built" in st_ and "The Foraging island 12 blocks further out" in st_, "SHIFT 1 the status line: %s" % st_)
    s0, bm = A["sets"], dict(A["B"])
    T25.drive(Life, IS, IS(JString(WC)), A, rows, limit=50)
    mem = JClass("java.util.ArrayList")()
    Life.archiTick(JString(WC), JString(KO), IS(JString(WC)), mem, rows, JLong(10 ** 9))
    K.check(A["sets"] == s0 and A["B"] == bm and len(A["doors"]) == 6 and not A["given"], "SHIFT 1 start twice: nothing changes, nothing given")
    # ---- 2. blocked at 0 and 12 -> 24
    E = T25.env(scratch, jar, "sh2")
    Life = E.Life
    A = T25.fresh(m)
    bl = blocker(m, "forage", [0, 1])
    for c in bl:
        A["B"][c] = "Furniture_Village_Bench"
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    T25.drive(Life, IS, IS(JString(WC)), A, rows)
    want = expected_map(m, dict(zero, forage=2), dict((c, "Furniture_Village_Bench") for c in bl))
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(str(get("archi.forage")) == "done+24" and not diff, "SHIFT 2 blocked at 0 and 12: built 24 further out: %s %s" % (get("archi.forage"), diff[:3]))
    # ---- 3. blocked at all three -> skipped, the item once
    E = T25.env(scratch, jar, "sh3")
    Life = E.Life
    A = T25.fresh(m)
    bl = blocker(m, "forage", [0, 1, 2])
    for c in bl:
        A["B"][c] = "Furniture_Village_Bench"
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    T25.drive(Life, IS, st, A, rows)
    sk = sorted(e["name"] for e in m.ARCHI if str(get("archi." + e["name"])).startswith("skip"))
    K.eq(sk, sorted(["forage", "b_spawn_forage", "b_farm_forage", "b_forage_minecave"]), "SHIFT 3 blocked at all three spots: Foraging + its 3 bridges skipped")
    K.check(get("archi.shift.forage") is None and all(A["B"][c] == "Furniture_Village_Bench" for c in bl)
            and not any(c in A["B"] for s in (0, 1, 2) for c in m.ARCHI_ISV[("forage", s)]["cells"] if c not in bl),
            "SHIFT 3 nothing of the island placed at any spot, the 3 benches untouched, archi.shift cleared")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9))
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 60000))
    K.eq(A["given"], ["foraging"], "SHIFT 3 the Foraging shard comes as the item, once")
    # ---- 4. Farming + Mining + Ranching moved: water, cave copper, pen animals at the moved spots
    E = T25.env(scratch, jar, "sh4")
    Life = E.Life
    A = T25.fresh(m)
    for nm in ("farm", "minecave", "ranch"):
        A["B"][blocker(m, nm, [0])[0]] = "Furniture_Village_Bench"
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    T25.drive(Life, IS, st, A, rows)
    K.check(all(str(get("archi." + n)) == "done+12" for n in ("farm", "minecave", "ranch")), "SHIFT 4 Farming, Mining, Ranching built 12 further out")
    K.check(A["W"] == set(m.ARCHI_ISV[("farm", 1)]["water"]), "SHIFT 4 the farm channel's water at the moved cells")
    rv = m.archi_vec("ranch", 1)
    want_sp = sorted((round(a[1], 3), round(a[3], 3)) for a in m.ARCHI_ISV[("ranch", 1)]["animals"])
    got_sp = sorted((round(x, 3), round(z, 3)) for r, x, z in A["spawned"])
    K.check(len(A["spawned"]) == 11 and set(got_sp) <= set(want_sp), "SHIFT 4 the 11 pen animals at the moved Ranching island's spots (moved %s)" % (rv,))
    bl4 = dict((c, b) for c, b in A["B"].items() if b == "Furniture_Village_Bench")
    want = expected_map(m, dict(zero, farm=1, minecave=1, ranch=1), bl4)
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(not diff, "SHIFT 4 the block map = the 3 moved islands + their re-planned bridges + the rest: %s" % diff[:3])
    ores1 = m.ARCHI_ISV[("minecave", 1)]["ores"]
    A["B"].pop(ores1[0])
    A["B"][ores1[1]] = "Rock_Stone"
    Life.archiTick(JString(WC), JString(KO), st, T23.member(-53.0, 3.0), rows, JLong(10 ** 9))
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(A["B"].get(ores1[0]) == "Ore_Copper_Stone" and A["B"].get(ores1[1]) == "Ore_Copper_Stone" and not diff,
            "SHIFT 4 the moved cave's copper regrows (AIR / stone); nothing placed at the old cave's cells: %s" % diff[:3])
    ids = str(get("ranch.ids"))
    wild = [e.split("|")[2] for e in ids.split(";") if e.startswith("w|")]
    A["alive"].discard(wild[0])
    n0 = len(A["spawned"])
    Life.archiTick(JString(WC), JString(KO), st, T23.member(-53.0, 3.0), rows, JLong(10 ** 9 + 700000))
    Life.archiTick(JString(WC), JString(KO), st, T23.member(-53.0, 3.0), rows, JLong(10 ** 9 + 1400000))
    K.check(len(A["spawned"]) == n0 + 1 and (round(A["spawned"][-1][1], 3), round(A["spawned"][-1][2], 3)) in set(want_sp),
            "SHIFT 4 a caught wild animal comes back at the moved pen")
    K.save()


def drive_retry(Life, IS, st, A, rows):
    """the island tick calls archiOnce every second, finished or not (the queued retry is checked before the finished check)"""
    from jpype import JString, JLong
    Life.archiOnce(JString(WC), JString(KO), st, JLong(900), rows)
    return T25.drive(Life, IS, st, A, rows)


def run_retry(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    E = T25.env(scratch, jar, "rt")
    rows = T25.rows_with_owner()
    Life, IS, Cfg = E.Life, E.P("IsleState"), E.Cfg
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    K.check(str(Life.archiRetry(JString(KO), JString("Skyy"))).startswith("=The archipelago has not started"), "RETRY before the archipelago started: says so")
    K.check(str(Life.archiStatus(JString(KO))).startswith("=The archipelago has not started"), "RETRY status before the start: says so")
    A = T25.fresh(m)
    bl = blocker(m, "forage", [0, 1, 2])
    for c in bl:
        A["B"][c] = "Furniture_Village_Bench"
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    T25.drive(Life, IS, st, A, rows)
    mem = JClass("java.util.ArrayList")()
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9))
    K.eq(A["given"], ["foraging"], "RETRY setup: Foraging skipped at all 3 spots, the item given")
    st_ = str(Life.archiStatus(JString(KO)))
    K.check("11 of 15 parts built" in st_ and "The Foraging island" in st_ and "retry" in st_, "RETRY the status names the skipped parts: %s" % st_)
    # still blocked: tries 0 / 12 / 24 again, stays skipped, no second item
    sh0 = int(Life.ARCHI_SHIFTED.get())
    r = str(Life.archiRetry(JString(KO), JString("Skyy")))
    K.check(r.startswith("+Trying 4 skipped parts again") and bool(Life.RETRY.containsKey(JString(KO))), "RETRY asked: %s" % r[:160])
    drive_retry(Life, IS, st, A, rows)
    K.check(not bool(Life.RETRY.containsKey(JString(KO))) and int(Life.ARCHI_SHIFTED.get()) == sh0 + 2 and str(get("archi.forage")) == "skip:built"
            and str(get("archi")) == "1", "RETRY still blocked: tried 12 and 24 again, skipped again")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(2 * 10 ** 9))
    K.eq(A["given"], ["foraging"], "RETRY still blocked: the item is NOT given a second time")
    # the blocker on the island's own spot removed: retry -> built at its own spot, the door recorded, no item
    own = set(m.ARCHI_ISV[("forage", 0)]["cells"])
    left = [c for c in bl if c not in own]           # the benches on the island's own spot are taken away; the others stay
    for c in bl:
        if c in own:
            del A["B"][c]
    nd = len(A["doors"])
    r = str(Life.archiRetry(JString(KO), JString("Skyy")))
    K.eq(int(Life.archiRetryNow(JString("skyy-island-oldworld"), JString(KO), IS(JString("skyy-island-oldworld")))), 0,
         "RETRY run on another world of the owner (not the archipelago's): nothing cleared there")
    drive_retry(Life, IS, st, A, rows)
    want = expected_map(m, dict((k, 0) for k in m.ARCHI_ISL), dict((c, "Furniture_Village_Bench") for c in left))
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(str(get("archi.forage")) == "done" and str(get("archi")) == "1" and all(str(get("archi." + n)) == "done" for n in ("b_spawn_forage", "b_farm_forage", "b_forage_minecave")) and not diff,
            "RETRY the blocker gone: Foraging + its 3 bridges built at their own spot, the rest unchanged: %s" % diff[:3])
    K.check(len(A["doors"]) == nd + 1 and A["doors"][-1][0] == "foraging" and str(get("archi.door.foraging")) == "+" and str(get("archi.item.foraging")) == "given",
            "RETRY the Foraging door recorded (SkyyShards keeps the item's portal if one was placed), archi.item.foraging stays given")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(3 * 10 ** 9))
    K.eq(A["given"], ["foraging"], "RETRY ... and no second shard item, ever")
    K.check(str(Life.archiRetry(JString(KO), JString("Skyy"))).startswith("=Nothing to retry"), "RETRY nothing skipped: says so")
    K.check(int(Life.ARCHI_RETRIED.get()) == 8, "RETRY counted 4 + 4 parts (%d)" % int(Life.ARCHI_RETRIED.get()))
    # a fresh state after a restart: nothing runs again
    s0 = A["sets"]
    T25.drive(Life, IS, IS(JString(WC)), A, rows, limit=50)
    K.check(A["sets"] == s0, "RETRY start twice afterwards: nothing changes")
    # switched off / a bad file
    Cfg.ARCHI_EXISTING = "off"
    K.check(str(Life.archiRetry(JString(KO), JString("Skyy"))).startswith("-The starter archipelago is off"), "RETRY archi.existing off: refused")
    Cfg.ARCHI_EXISTING = "add"
    s = E.St.settings(JString(KO))
    s.bad = True
    s.badAt = JLong(int(JClass("java.lang.System").currentTimeMillis()) + 10 ** 9)
    K.check(str(Life.archiRetry(JString(KO), JString("Skyy"))).startswith("-That island's file cannot be read"), "RETRY a bad island file: refused")
    s.bad = False
    K.check(str(Life.archiRetry(None, JString("Skyy"))).startswith("-No island"), "RETRY no island: refused")
    K.save()


def run_place(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    m = layout()
    E = T25.env(scratch, jar, "pl")
    Life, Pl = E.Life, E.P("PlaceFn")()
    U = JClass("java.util.UUID").fromString(KO)
    arr = lambda i: JClass("java.lang.Object")[:]([U, JString(i)])
    p0 = str(Pl.apply(JString("forage")))
    K.eq(str(Pl.apply(arr("forage"))), p0, "PLACE no move: the UUID form = the String form")
    Life.archiSet1(JString(KO), JString("archi.shift.forage"), JString("24"))
    p = str(Pl.apply(arr("forage")))
    want = [pp for pp in m.ARCHI_ISV[("forage", 2)]["places"] if pp[0] == "forage"][0]
    f = p.split("|")
    K.check(f[0] == "island" and abs(float(f[1]) - want[1]) < 1e-6 and abs(float(f[3]) - want[3]) < 1e-6 and f[2] == p0.split("|")[2] and f[4] == p0.split("|")[4],
            "PLACE moved 24: island:fn:place {UUID, forage} = the moved place %s (%s)" % (p, want))
    K.eq(str(Pl.apply(JString("forage"))), p0, "PLACE the String form (no player) keeps the normal spot")
    K.eq(str(Pl.apply(arr("island1"))), str(Pl.apply(JString("island1"))), "PLACE a starter island place is unchanged")
    K.save()


def run_fix(out, jar, scratch, _home):
    """the fix round (critics): one check per fix"""
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    zero = dict((k, 0) for k in m.ARCHI_ISL)
    # ---- FIX 1: a "done" island sits at its own spot whatever archi.shift.<island> says (a 0.5.25 rollback mid-shift)
    E = T25.env(scratch, jar, "fx1")
    rows = T25.rows_with_owner()
    Life, Arc = E.Life, E.P("ArchiIsles")
    fi = m.ARCHI_IDX["forage"]
    put = lambda k, v: Life.archiSet1(JString(KO), JString(k), JString(v))
    put("archi.shift.forage", "12")
    put("archi.forage", "done")
    K.check(int(Arc.shiftOf(JString(KO), fi)) == 0 and int(Arc.dx(JString(KO), fi)) == 0 and int(Arc.dz(JString(KO), fi)) == 0,
            "FIX 1 done + a stale shift marker 12: the island counts at its own spot (door / cave / pen / place not moved)")
    put("archi.forage", "done+24")
    K.eq(int(Arc.shiftOf(JString(KO), fi)), 2, "FIX 1 done+24 (marker 12): the done value decides - 24 out")
    put("archi.forage", "")
    K.eq(int(Arc.shiftOf(JString(KO), fi)), 1, "FIX 1 still being built: the marker decides (12 out)")
    # ---- FIX 2: a moved spot whose chunk stays unloaded counts as blocked after ARCHI_WAIT; the parts after it go on
    E = T25.env(scratch, jar, "fx2")
    Life, IS = E.Life, E.P("IsleState")
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    A = T25.fresh(m)
    b0 = blocker(m, "forage", [0])[0]
    u1 = blocker(m, "forage", [1])[0]
    A["B"][b0] = "Furniture_Village_Bench"
    A["unloaded"].add(u1)
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    n = 0
    while n < 6000 and not bool(st.archiOff):
        Life.archiOnce(JString(WC), JString(KO), st, JLong(1000 + n * 1000), rows)
        n += 1
    want = expected_map(m, dict(zero, forage=2), {b0: "Furniture_Village_Bench"})
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(int(Life.ARCHI_WAIT) == 60000 and str(get("archi.forage")) == "done+24" and str(get("archi")) == "1" and not diff
            and all(str(get("archi." + e["name"])) == "done" for e in m.ARCHI if e["name"] != "forage"),
            "FIX 2 Foraging blocked at 0, its 12 spot unloaded: after 60 s it counts as blocked, built 24 out, every later part built: %s %s (%d ticks)" % (get("archi.forage"), diff[:3], n))
    K.check(n > 60, "FIX 2 it waited the 60 s first (%d one-second ticks)" % n)
    E = T25.env(scratch, jar, "fx2b")
    Life = E.Life
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    A = T25.fresh(m)
    A["unloaded"].add(blocker(m, "forage", [0])[0])
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    for n in range(300):
        Life.archiOnce(JString(WC), JString(KO), st, JLong(1000 + n * 1000), rows)
    K.check(get("archi.forage") is None and get("archi.shift.forage") is None and not bool(st.archiOff),
            "FIX 2 an unloaded cell at the island's OWN spot still waits (300 s, as in 0.5.25): %s" % get("archi.forage"))
    # ---- FIX 3: a queued retry is not eaten by another world of the owner
    E = T25.env(scratch, jar, "fx3")
    Life = E.Life
    A = T25.fresh(m)
    for c in blocker(m, "forage", [0, 1, 2]):
        A["B"][c] = "Furniture_Village_Bench"
    Life.API = T23.stand_in(PKG + "IsleApi", T25.Api(A))
    st = IS(JString(WC))
    T25.drive(Life, IS, st, A, rows)
    r = str(Life.archiRetry(JString(KO), JString("Skyy")))
    ow = JString("skyy-island-oldworld")
    K.check(r.startswith("+Trying 4") and int(Life.archiRetryDue(ow, JString(KO), IS(ow))) == 0 and bool(Life.RETRY.containsKey(JString(KO))),
            "FIX 3 another world of the owner leaves the queued retry waiting")
    K.check(int(Life.archiRetryDue(JString(WC), JString(KO), st)) == 4 and not bool(Life.RETRY.containsKey(JString(KO))),
            "FIX 3 the archipelago's own world uses it (4 parts tried again)")
    # ---- FIX 4: one pending relight per world
    RT = E.P("RelightTask")
    RT.PENDING.clear()
    RT.PENDING.put(JString("w1"), JClass("java.lang.Boolean").TRUE)
    RT.schedule(JString("w1"))
    K.check(int(RT.PENDING.size()) == 1, "FIX 4 a relight already waits for w1: the second request is merged into it")
    RT(JString("w1")).run()
    K.check(not bool(RT.PENDING.containsKey(JString("w1"))), "FIX 4 the waiting relight runs: w1 can be asked again")
    K.save()


def run_cmd(out, jar, scratch, _home):
    """the real /island tree (the 0.5.19 harness's tree walk): /island archipelago + its 2 usage variants carry hytale:Adventurer, no new
    admin-only node; the word is no home name"""
    from jpype import JClass, JString
    K = HK.Child(out)
    T25.env(scratch, jar, "cmd")
    import hub_tab_kit as HT
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fg = HT.jf(AC.class_, "permissionGroups")
    fr = HT.jf(AC.class_, "requiredArguments")
    ic = JClass(PKG + "IslandCmd")()
    t = {}

    def walk(c, path):
        g = fg.get(c)
        t[path] = (None if g is None else [str(x) for x in g], int(fr.get(c).size()), bool(c.isVariant()))
        for v in c.getVariantCommands():
            g = fg.get(v)
            t[path + " <%d args>" % int(fr.get(v).size())] = (None if g is None else [str(x) for x in g], int(fr.get(v).size()), bool(v.isVariant()))
        subs = c.getSubCommands()
        for k in sorted(str(x) for x in subs.keySet()):
            walk(subs.get(k), path + " " + k)
    walk(ic, "/island")
    ADV = ["hytale:Adventurer"]
    for p, w in (("/island archipelago", (ADV, 0, False)), ("/island archipelago <1 args>", (ADV, 1, True)), ("/island archipelago <2 args>", (ADV, 2, True))):
        K.eq(t.get(p), w, "CMD %s (groups, required args, variant)" % p)
    K.eq(t.get("/island reload"), ([], 0, False), "CMD /island reload stays admin-only (no groups)")
    bad = [p for p, v in t.items() if p != "/island reload" and v[0] != ADV]
    K.check(not bad, "CMD every player node / variant carries hytale:Adventurer: %s" % bad)
    K.eq(len([p for p in t if p.count(" ") == 1 and "<" not in p]), 26, "CMD 26 sub-commands under /island (0.5.25's 25 + archipelago)")
    IH = JClass(PKG + "IslandHomes")
    K.check("archipelago" in [str(w) for w in IH.WORDS] and IH.bad(JString("Archipelago")) is not None, "CMD archipelago is no home name: %s" % IH.bad(JString("Archipelago")))
    K.save()


def run_live26(out, jar, scratch, home):
    from jpype import JString
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    E = T23.Env(scratch, jar, "lv")
    Cfg, St, Life = E.Cfg, E.St, E.Life
    Cfg.FILE = E.Paths.get(os.path.join(home, "config.properties"))
    Cfg.load("")
    isl = os.path.join(home, "islands")
    St.DIR = E.Paths.get(isl)
    St.IO = None
    St.SETTINGS.clear()
    St.loadIslandWorlds()
    keys = [f[:-11] for f in os.listdir(isl) if f.endswith(".properties")] if os.path.isdir(isl) else []
    bad = [k for k in keys if St.settings(JString(k)) is None]
    sts = dict((k, str(Life.archiStatus(JString(k)))) for k in keys)
    K.check(keys and not bad and all(v[:1] in "=-" for v in sts.values()), "LIVE every island file reads + answers /island archipelago (%d)" % len(keys))
    sk = dict((k, v) for k, v in sts.items() if "skipped" in v)
    print("LIVE archipelago status per island: %s" % dict((k, v[:200]) for k, v in sts.items()))
    print("LIVE islands with skipped parts (a /island archipelago retry candidate): %d %s" % (len(sk), list(sk)[:5]))
    K.check(HK.tree_hash(home) == h0, "LIVE nothing changed on disk")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("data", run_data), ("shift", run_shift), ("retry", run_retry), ("place", run_place), ("fix", run_fix), ("cmd", run_cmd),
                   ("archi", T25.run_archi), ("door", T25.run_door), ("fix2", T25.run_fix2), ("life", T25.run_life), ("cfg", T25.run_cfg),
                   ("unload", T24.run_unload), ("early", T23.run_early), ("ids", T23.run_ids), ("boss", T23.run_boss), ("clear", T23.run_clear),
                   ("time", T23.run_time), ("live", run_live26), ("live2", T25.run_live2)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
