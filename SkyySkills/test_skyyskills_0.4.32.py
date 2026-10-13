"""SkyySkills 0.4.32 - harness for the LAG FIXES (tools/skills_0_4_32_patch.py: lock-free bridges, the leaderboard index, the SkyySkills-IO
writer, PlacedSet, one FellRead per watch + fell.pollMs 500 with PollMig).
Build first: python tools/skills_0_4_32_patch.py && python SkyySkills/build_skyyskills_0.4.32.py

    python SkyySkills/test_skyyskills_0.4.32.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.4.31 -> 0.4.32: exactly the planned members differ (+ PlacedSet, SkillIO, PollMig)
  X  exec     EVERY NEW CODE PATH (-Xverify:all): SkillStore.bridge / MoveSync.bridge lock-free (static + identity); static: SkillTop.all
              reads no file, SkillStore.save only from the writer jobs / the IO-off fallbacks / shutdown, Thread.sleep only in
              SkillStore.moveRetry (+ the config kit), FellWatch.run resets its one FellRead; SkillIO (SkyySkills-IO daemon, one queued job
              per kind); THE LEADERBOARD: 240 player files seeded on SkyySkills-IO, then SkillTop.all for every slot = 0.4.31's
              SkillTop.all (its own class loader, the same folder) row for row - with every player file DELETED first (no disk read);
              not cached before the seed; install / addK / Perk.migrate (the legacy Combat move) keep the index current; OwnCurve.deliver's
              paid marker saved synchronously (write-ahead, fix review);
              flushDirty on the writer; PLACED BLOCKS: PlacedSet vs a Python model over 60,000 random adds / moves / removes /
              contains / evictions (growth + backward-shift deletion); PlacedStore vs 0.4.31's (own loader) over the same 20,000 ops on
              3 worlds incl. file loads with duplicates: every answer equal and the saved files byte-identical; the 400,000 cap evicts
              the oldest; preload on the writer; FELLED TREES: FellRead.reset, POLL_MS 500 (code + file default + Server Setup row);
              POLLMIG.plan on texts (0.4.31's default file: 200 -> 500 + marker under the line; CRLF kept; an admin's 300 kept; a
              continued entry kept; no felled block / marker = nothing; no fell.pollMs line = marker at the end) + run() on a file (History
              copy, one Undo-able change-log line, second run = nothing)
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyySkills, both jars (setup's file path: every migration, load, curves):
              0.4.32 changes exactly what 0.4.31 changes + fell.pollMs 200 -> 500 (+ its marker, History copy, one change-log line);
              start 2 changes nothing; player files untouched; the live leaderboard from the index = 0.4.31's file scan for every slot
  AA engine-access audit
Behaviour regression (separately): python SkyySkills/test_skyyskills_0.4.31.py --dir <scratch> --jar SkyySkills/SkyySkills-0.4.32.jar
--prev SkyySkills/SkyySkills-0.4.31.jar (its H / M / O / MG / ST checks pass on 0.4.32; its controls and class compare expect 0.4.30).
Scratch: tools/dev/scratch/perfworld/skills (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, random, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.31.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "perfworld", "skills")))
PKG = "com.skyy.skills."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")

EXPECT = {
    "SkillStore": ["+f BRIDGE", "+f TOPIDX", "+f TOP_READS", "+f TOP_SEEDED", "+m bridge0", "+m io", "+m seedTop",
                   "+m stopIO", "+m topPut", "+m topXp", "~<clinit>", "~m addK", "~m bridge", "~m install"],
    "MoveSync": ["+f BRIDGE", "+m bridge0", "~m bridge"],
    "SkillTop": ["~m all"],
    "SkillTick": ["~m run"],
    "Perks": ["~m migrate"],      # fix review 2026-10-13: the index follows the legacy Combat move
    "PlacedStore": ["+m add0", "+m contains0", "+m get0", "+m preload", "+m preloadWorlds", "+m put0", "+m read", "+m remove0", "+m set", "-m set",
                    "~m add", "~m contains", "~m remove", "~m snapshot"],
    "FellRead": ["+m reset"],
    "FellWatch": ["+f rd", "~m run"],
    "FellCfg": ["~<clinit>", "~m ensureDefaults", "~m read"],   # POLL_MS 500 + the felled block default text (fell.pollMs=500 + the marker)
    "SkyySkillsPlugin": ["~m setup", "~m shutdown"],
    # version / default-text constants only (inlined strings): the pack name "Skyy:0.4.32 SkyySkills", the xp.properties header + felled block,
    # the config kit's export header
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "SkillCfg": ["~m load"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["PlacedSet", "SkillIO", "PollMig"]


def loader_for(jar, isolated=False):
    """a class loader for one jar; isolated = its own copy of the server jar under the platform loader (the system class path holds the
    NEW jar in the exec phase - a system-parent loader would hand back the new classes for the old jar's names)"""
    from jpype import JClass, JArray
    files = [jar, B.SERVER_JAR] if isolated else [jar]
    arr = JArray(JClass("java.net.URL"))(len(files))
    for i, f in enumerate(files):
        arr[i] = JClass("java.io.File")(f).toURI().toURL()
    CL = JClass("java.lang.ClassLoader")
    return JClass("java.net.URLClassLoader")(arr, CL.getPlatformClassLoader() if isolated else CL.getSystemClassLoader())


def path(p):
    from jpype import JClass
    return JClass("java.nio.file.Paths").get(p, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))


def rows_of(Top, n_slots):
    out = []
    for s in range(n_slots):
        rows = Top.all(s)
        out.append([(str(r[0]), int(r[1]), str(r[2])) for r in rows])
    return out


def write_players(d, n, slots, names, rnd):
    os.makedirs(d, exist_ok=True)
    for i in range(n):
        k = "%08x-0000-4000-8000-%012d" % (i + 1, i) + ("-p2" if i % 7 == 3 else "")
        lines = ["#SkyySkills"]
        if i % 5 != 2:
            lines.append("name=Player%d" % i)
        for j, nm in enumerate(names):
            if rnd.random() < 0.8:
                lines.append("%s=%d" % (nm, rnd.randrange(0, 200000)))
        if i % 11 == 4:
            lines.append("%s=notanumber" % names[0])
        open(os.path.join(d, k + ".properties"), "w", encoding="latin-1").write("\n".join(lines) + "\n")


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, synchronized
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Sto, Top, SIO, Plc, PSet, MS, FRd, FCfg, PM, Defs, Cfg = (P("SkillStore"), P("SkillTop"), P("SkillIO"), P("PlacedStore"), P("PlacedSet"),
                                                               P("MoveSync"), P("FellRead"), P("FellCfg"), P("PollMig"), P("SkillDefs"), P("SkillCfg"))
    Sys, Executors, Thread, UUID = JClass("java.lang.System"), JClass("java.util.concurrent.Executors"), JClass("java.lang.Thread"), JClass("java.util.UUID")
    me = str(Thread.currentThread().getName())
    # ---- A: bridges
    K.check(Sto.BRIDGE is None and MS.BRIDGE is None, "X bridge: both caches empty before the first call")
    m1 = Sto.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1) and Sys.identityHashCode(MS.bridge()) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(Sto.BRIDGE) == Sys.identityHashCode(m1) and Sys.identityHashCode(MS.BRIDGE) == Sys.identityHashCode(m1),
            "X bridge: SkillStore + MoveSync share the one map, cached in their BRIDGE")
    found = PW.bridge_static(K, jar)
    K.check("SkillStore" in found and "MoveSync" in found, "X bridge: SkillStore + MoveSync checked (%s)" % found)
    g = PW.calls(jar)
    K.check(PKG + "SkillStore.readLocked" not in g["SkillTop.all"] and not any(c.startswith("java.nio.file.Files") for c in g["SkillTop.all"]),
            "X static: SkillTop.all reads no file (the index)")
    K.eq(PW.callers(g, "SkillStore.save", PKG), ["ClassCurve.flush", "OwnCurve.deliver", "OwnCurve.flush", "SkillStore.flushDirty"],
         "X static: SkillStore.save only from the flushes (writer jobs) and OwnCurve.deliver's paid marker (write-ahead)")
    K.check(PKG + "SkillStore.save" in g["OwnCurve.deliver"]
            and not any(c.endswith(".saveSoon") for c in g["OwnCurve.deliver"]),
            "X FIX 2: OwnCurve.deliver saves the new paid marker synchronously (0.4.31 F1), nothing queued")
    K.check(PKG + "SkillStore.topPut" in g["Perks.migrate"] and PKG + "SkillStore.moveLegacy" in g["Perks.migrate"],
            "X FIX 3 static: Perk.migrate updates the leaderboard index after moveLegacy")
    K.eq(PW.callers(g, "SkillStore.flushDirty", PKG), ["SkillIO.run", "SkillTick.run", "SkyySkillsPlugin.shutdown"],
         "X static: flushDirty = the writer, the ticker's IO-off fallback, shutdown")
    K.eq([m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")], ["SkillStore.moveRetry"], "X static: Thread.sleep only in SkillStore.moveRetry")
    K.check(PKG + "FellRead.reset" in g["FellWatch.run"], "X static: FellWatch.run resets its one FellRead")
    Mod = JClass("java.lang.reflect.Modifier")
    K.check(not Mod.isSynchronized(Plc.class_.getMethod("read", JClass("java.lang.String").class_).getModifiers())
            and not Mod.isSynchronized(Plc.class_.getMethod("set", JClass("java.lang.String").class_).getModifiers()),
            "X static: PlacedStore.read / set hold no lock (the file read is outside the lock)")
    t = SIO(9, None).newThread(SIO(1, None))
    K.check(str(t.getName()) == "SkyySkills-IO" and t.isDaemon(), "X SkillIO.newThread: SkyySkills-IO, daemon")
    # ---- the leaderboard index vs 0.4.31's file scan
    rnd = random.Random(32)
    n_slots = int(Defs.N)
    names = [str(x) for x in Defs.NAMES]
    pd = os.path.join(scratch, "x", "players")
    write_players(pd, 240, n_slots, names, rnd)
    Lo = loader_for(OLD_JAR, isolated=True)
    OSto, OTop = JClass(PKG + "SkillStore", loader=Lo), JClass(PKG + "SkillTop", loader=Lo)
    OSto.DIR = JClass("java.nio.file.Paths", loader=Lo).get(pd, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))
    old_rows = rows_of(OTop, n_slots)
    Sto.DIR = path(pd)
    SIO.IO = Executors.newSingleThreadExecutor(SIO(9, None))
    part = Top.all(0)
    K.check(not Sto.TOP_SEEDED and Top.CACHE[0] is None and part.size() == 0, "X before the seed: the list is built from what is known, NOT cached")
    K.check(Sto.io(5, None), "X io(5): the seed is queued on the writer")
    K.check(PW.wait_until(lambda: Sto.TOP_SEEDED) and str(SIO.LAST) == "SkyySkills-IO" and Sto.TOP_READS.get() == 240,
            "X the seed read the 240 files on SkyySkills-IO (%d)" % Sto.TOP_READS.get())
    shutil.rmtree(pd)
    new_rows = rows_of(Top, n_slots)
    K.check(new_rows == old_rows, "X SAME LEADERBOARD: every slot's rows = 0.4.31's file scan, with every player file deleted first (no read): %s"
            % [s for s in range(n_slots) if new_rows[s] != old_rows[s]][:5])
    K.check(Top.CACHE[0] is not None, "X after the seed the list is cached (30 s, as 0.4.31)")
    # the 5 min refresh: a file changed on disk is re-read, a file gone (not loaded) leaves the index, a loaded profile is never re-read
    os.makedirs(pd, exist_ok=True)
    kk1 = "%08x-0000-4000-8000-%012d" % (2, 1)
    open(os.path.join(pd, kk1 + ".properties"), "w", encoding="latin-1").write("name=Edited" + chr(10) + "%s=777" % names[0] + chr(10))
    r0 = Sto.TOP_READS.get()
    Sto.seedTop()
    e1 = Sto.TOPIDX.get(kk1)
    K.check(e1 is not None and str(e1[0]) == "Edited" and int(e1[1][0]) == 777 and Sto.TOPIDX.size() == 1 and Sto.TOP_READS.get() == r0 + 1,
            "X the refresh: an edited file re-read, the deleted files' entries gone (index %d)" % Sto.TOPIDX.size())
    os.remove(os.path.join(pd, kk1 + ".properties"))
    Sto.seedTop()
    K.check(Sto.TOPIDX.size() == 0, "X the refresh: the last file deleted = an empty index")
    # install / addK keep it current
    write_players(pd, 3, n_slots, names, random.Random(5))
    u = UUID.fromString("00000001-0000-4000-8000-000000000000")
    k = "00000001-0000-4000-8000-000000000000"
    d = Sto.dataK(k, u)
    e = Sto.TOPIDX.get(k)
    K.check(e is not None and list(e[1]) == [int(x) for x in d][:n_slots], "X install puts the loaded profile into the index")
    Sto.addK(k, u, "Renamed", 2, 1234)
    e = Sto.TOPIDX.get(k)
    K.check(int(e[1][2]) == int(d[2]) and str(e[0]) == "Renamed", "X addK updates the index (xp + name)")
    # FIX 3: the legacy Combat move (Perk.migrate -> moveLegacy) updates the index of a loaded profile
    cs = int(Defs.CLASS_SLOT[0])
    cb = int(Defs.COMBAT)
    for j in range(len(Defs.CLASS_SLOT)):
        Sto.wr(d, int(Defs.CLASS_SLOT[j]), 0)
    Sto.wr(d, cb, 4321)
    Sto.topPut(k, None, d)
    K.check(int(Sto.TOPIDX.get(k)[1][cb]) == 4321 and int(Sto.TOPIDX.get(k)[1][cs]) == 0, "X FIX 3 setup: the index holds legacy Combat 4321, class slot 0")
    try:
        P("Perks").migrate(None, u, cs)   # pr = None: the chat line after the move throws here; the move + index come first
    except Exception:
        pass
    e = Sto.TOPIDX.get(k)
    K.check(int(d[cs]) == 4321 and int(d[cb]) == 0 and int(e[1][cs]) == 4321 and int(e[1][cb]) == 0 and str(e[0]) == "Renamed",
            "X FIX 3: after Perk.migrate the index shows the class slot 4321 and Combat 0 at once (name kept)")
    Top.CACHE[cs] = None
    Top.CACHE[cb] = None
    rc, rb = [(str(r[2]), int(r[1])) for r in Top.all(cs)], [(str(r[2]), int(r[1])) for r in Top.all(cb)]
    K.check((k, 4321) in rc and (k, 4321) not in rb, "X FIX 3: the class Top list shows the moved XP, the Combat list no longer does")
    # flushDirty on the writer
    Sto.DIRTY.put(k, True)
    K.check(Sto.io(1, None) and PW.wait_until(lambda: Sto.DIRTY.isEmpty() and SIO.Q.get(1) == 0), "X io(1): flushDirty on the writer")
    K.check(PW.wait_until(lambda: "name=Renamed" in open(os.path.join(pd, k + ".properties"), encoding="latin-1").read()) and str(SIO.LAST) == "SkyySkills-IO",
            "X flushDirty written by SkyySkills-IO (the profile file holds the change)")
    # ---- PlacedSet vs a Python model
    from collections import OrderedDict
    ps = PSet()
    model = OrderedDict()
    rnd = random.Random(7)
    bad = 0
    for i in range(60000):
        op = rnd.random()
        kk = rnd.randrange(0, 3000) * 1000003 - 1500000000
        if op < 0.45:
            ps.addLast(kk)
            model.pop(kk, None)
            model[kk] = True
        elif op < 0.55:
            r1 = bool(ps.addIfAbsent(kk))
            r2 = kk not in model
            if r2:
                model[kk] = True
            bad += r1 != r2
        elif op < 0.8:
            r1 = bool(ps.remove(kk))
            r2 = model.pop(kk, None) is not None
            bad += r1 != r2
        elif op < 0.95:
            bad += bool(ps.contains(kk)) != (kk in model)
        elif model:
            ps.removeFirst()
            model.popitem(last=False)
        if i % 5000 == 0:
            bad += [int(x) for x in ps.toArray()] != list(model.keys())
    K.check(bad == 0 and [int(x) for x in ps.toArray()] == list(model.keys()) and ps.size == len(model),
            "X PlacedSet = an insertion-ordered set model over 60,000 random ops (%d mismatches, %d keys, table %d)" % (bad, ps.size, len(ps.tab)))
    # ---- PlacedStore vs 0.4.31's
    OPlc = JClass(PKG + "PlacedStore", loader=Lo)
    da, db = os.path.join(scratch, "x", "placed-old"), os.path.join(scratch, "x", "placed-new")
    os.makedirs(da)
    os.makedirs(db)
    import struct
    seedf = struct.pack(">i", 6) + b"".join(struct.pack(">q", v) for v in (5, 9, 5, 7, 9, 11))
    for dd in (da, db):
        open(os.path.join(dd, "w_one.bin"), "wb").write(seedf)
    OPlc.DIR, Plc.DIR = path(da), path(db)
    K.check(Sys.identityHashCode(OPlc) != Sys.identityHashCode(Plc), "X the 0.4.31 classes are its own (isolated loader)")
    rnd = random.Random(11)
    diff = 0
    worlds = ["w one", "w2", "w3"]
    for i in range(20000):
        w = rnd.choice(worlds)
        kk = rnd.randrange(0, 2000)
        op = rnd.random()
        if op < 0.5:
            OPlc.add(w, kk)
            Plc.add(w, kk)
        elif op < 0.8:
            diff += bool(OPlc.remove(w, kk)) != bool(Plc.remove(w, kk))
        else:
            diff += bool(OPlc.contains(w, kk)) != bool(Plc.contains(w, kk))
        if i % 4000 == 3999:
            OPlc.flush()
            Plc.flush()
    OPlc.flush()
    Plc.flush()
    fa = sorted(os.listdir(da))
    same = fa == sorted(os.listdir(db)) and all(open(os.path.join(da, f), "rb").read() == open(os.path.join(db, f), "rb").read() for f in fa)
    K.check(diff == 0 and same, "X PlacedStore = 0.4.31's over 20,000 ops on 3 worlds (a file with duplicates loaded): answers equal %s, files byte-identical %s (%s)"
            % (diff == 0, same, fa))
    # the cap
    cs = PSet()
    for i in range(400005):
        Plc.add0("capw", cs, i)
    a = cs.toArray()
    K.check(cs.size == 400000 and int(a[0]) == 5 and int(a[len(a) - 1]) == 400004, "X the 400,000 cap evicts the oldest (size %d, first %d)" % (cs.size, int(a[0])))
    # preload on the writer
    open(os.path.join(db, "w9.bin"), "wb").write(struct.pack(">i", 2) + struct.pack(">q", 42) + struct.pack(">q", 43))
    SIO.LOADING.put("w9", True)
    K.check(Sto.io(6, "w9") and PW.wait_until(lambda: SIO.LOADING.isEmpty() and Plc.get0("w9") is not None), "X io(6): the world's placed file read on the writer")
    K.check(Plc.contains("w9", 42) and Plc.contains("w9", 43) and not Plc.contains("w9", 44), "X ... with its positions")
    # ---- FellRead.reset + the 500 ms poll
    fr = FRd(None, 5)
    for i in range(7):
        fr.idx(0, -1 if i == 0 else 5, 0)
    fr.secs.put(JClass("java.lang.Long")(1), JClass("java.lang.Object")())
    fr.reset()
    K.check(fr.reads == 0 and not fr.over and fr.err is None and fr.secs.isEmpty(), "X FellRead.reset: reads / over / err / section cache cleared")
    K.check(int(FCfg.POLL_MS) == 500, "X FellCfg.POLL_MS default 500")
    FCfg.read(JClass("java.util.Properties")())
    K.check(int(FCfg.POLL_MS) == 500, "X FellCfg.read: a file without fell.pollMs = 500")
    K.check("\nfell.pollMs=500\n" + str(PM.MARK) + "\n" in "\n" + str(FCfg.DEFAULTS) and str(PM.MARK_ID) in str(PM.MARK),
            "X the felled block default: fell.pollMs=500 + PollMig's marker under it")
    # ---- PollMig.plan
    OFCfg = JClass(PKG + "FellCfg", loader=Lo)
    old_def = str(JClass(PKG + "SkillCfg", loader=Lo).DEFAULTS) if hasattr(JClass(PKG + "SkillCfg", loader=Lo), "DEFAULTS") else str(OFCfg.DEFAULTS)
    r = PM.plan(old_def)
    body = str(r[0]) if r is not None else ""
    K.check(r is not None and bool(r[2]) and "fell.pollMs=500\n" + str(PM.MARK) + "\n" in body and body.replace("fell.pollMs=500\n" + str(PM.MARK) + "\n", "fell.pollMs=200\n") == old_def
            and list(r[1]) == ["fell.pollMs", "200", "500"], "X plan(0.4.31 default): 200 -> 500 + the marker under the line, nothing else")
    crlf = old_def.replace("\n", "\r\n")
    r = PM.plan(crlf)
    K.check(r is not None and str(r[0]) == crlf.replace("fell.pollMs=200\r\n", "fell.pollMs=500\r\n" + str(PM.MARK) + "\r\n"), "X plan(CRLF): line endings kept")
    r = PM.plan(old_def.replace("fell.pollMs=200", "fell.pollMs = 300"))
    K.check(r is not None and not bool(r[2]) and "kept" in str(r[3]) and "fell.pollMs = 300\n" + str(PM.MARK) in str(r[0]), "X plan(admin 300): kept + marker")
    r = PM.plan(old_def.replace("fell.pollMs=200", "fell.pollMs=2\\\n00"))
    K.check(r is not None and not bool(r[2]) and "fell.pollMs=2\\\n00\n" + str(PM.MARK) in str(r[0]), "X plan(a continued entry): kept")
    K.check(PM.plan("a=1\nb=2\n") is None, "X plan(no felled block): nothing (FellCfg.ensureDefaults appends the 0.4.32 block)")
    K.check(PM.plan(str(r[0])) is None, "X plan(marker present): nothing")
    r = PM.plan("fell.enabled=true\nx=1")
    K.check(r is not None and str(r[0]) == "fell.enabled=true\nx=1\n" + str(PM.MARK) + "\n", "X plan(no fell.pollMs line): marker at the end")
    # run() on a file
    mf = os.path.join(scratch, "x", "mig", "xp.properties")
    os.makedirs(os.path.dirname(mf))
    open(mf, "wb").write(old_def.encode("latin-1"))
    Cfg.FILE = path(mf)
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    msg = str(PM.run())
    after = open(mf, "rb").read().decode("latin-1")
    hist = os.path.join(os.path.dirname(mf), "config-history")
    log = os.path.join(os.path.dirname(mf), "config-changes.log")
    K.check("200 -> 500" in msg and "fell.pollMs=500" in after and os.path.isdir(hist)
            and any(open(os.path.join(hr, f_), "rb").read() == old_def.encode("latin-1") for hr, _d, fs_ in os.walk(hist) for f_ in fs_),
            "X run(): updated, the old file kept in config-history: %s" % msg[:200])
    K.check(os.path.isfile(log) and "fell.pollMs\t200\t500\tok" in open(log, encoding="latin-1").read(), "X run(): one Undo-able change-log line")
    K.check(str(PM.run()) == "" and open(mf, "rb").read().decode("latin-1") == after, "X run() again: nothing")
    # ---- stop
    SIO.STOPPING = True
    Sto.stopIO()
    K.check(SIO.IO is None and not Sto.io(1, None), "X stopIO: the writer stopped; io() answers false (the caller writes, 0.4.31)")
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    migs_old = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig", "PerkMig"]
    res = {}
    lc_root = os.path.dirname(home)

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)
    for tag, jr, migs in (("old", OLD_JAR, migs_old), ("new", jar, migs_old + ["PollMig"])):
        lc = os.path.join(lc_root, "copy-" + tag)
        shutil.copytree(home, lc)
        L = loader_for(jr)
        J = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto, Hist, CLog, Rows = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")

        def start():
            Cfg.FILE = path(os.path.join(lc, "xp.properties"))
            Sto.DATA.clear()
            Sto.DIRTY.clear()
            Sto.DIR = path(os.path.join(lc, "players"))
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            r = {}
            for nm in migs:
                v = J(nm).run()
                r[nm] = str(v)
            r["load"] = str(Cfg.load())
            J("ClassCurve").start(path(lc))
            J("OwnCurve").start(path(lc))
            return r
        s0 = snap(lc)
        r1 = start()
        s1 = snap(lc)
        r2 = start()
        s2 = snap(lc)
        res[tag] = {"r1": r1, "s0": s0, "s1": s1, "s2": s2,
                    "rows": rows_of(J("SkillTop"), int(J("SkillDefs").N))}
    o, n = res["old"], res["new"]
    ch_o = sorted(k for k in set(o["s0"]) | set(o["s1"]) if o["s0"].get(k) != o["s1"].get(k))
    ch_n = sorted(k for k in set(n["s0"]) | set(n["s1"]) if n["s0"].get(k) != n["s1"].get(k))
    extra = sorted(set(ch_n) - set(ch_o))
    K.notes.append("D: 0.4.31 start 1 changed %s; 0.4.32 changed %s; PollMig: %s" % (ch_o, ch_n, n["r1"].get("PollMig", "")[:300]))
    xp0 = n["s0"].get("xp.properties", b"").decode("latin-1")
    xp1 = n["s1"].get("xp.properties", b"").decode("latin-1")
    had200 = "\nfell.pollMs=200" in "\n" + xp0
    K.check(set(extra) <= {"xp.properties", "config-changes.log"} | set(k for k in extra if k.startswith("config-history/")),
            "D: 0.4.32 start 1 changes what 0.4.31 changes + only xp.properties / its History copy / the change log: %s" % extra)
    if had200:
        mark = str(JClass(PKG + "PollMig", loader=loader_for(jar)).MARK)
        nl = "\r\n" if "\r\n" in xp0 else "\n"
        K.check(xp1 == xp0.replace("fell.pollMs=200" + nl, "fell.pollMs=500" + nl + mark + nl, 1), "D: the live xp.properties: fell.pollMs 200 -> 500 + the marker, every other byte kept")
        K.check(any(k.startswith("config-history/") and v == n["s0"]["xp.properties"] for k, v in n["s1"].items() if k not in n["s0"]),
                "D: the live xp.properties before the update is in config-history")
    else:
        K.notes.append("D: the live xp.properties has no fell.pollMs=200 line (kept / marker only)")
    K.check(all(n["s1"].get(k) == n["s2"].get(k) for k in set(n["s1"]) | set(n["s2"])), "D: 0.4.32 start 2 changes nothing")
    K.check(all(n["s0"].get(k) == n["s1"].get(k) for k in n["s0"] if k.startswith("players/")), "D: player files untouched")
    K.check(n["rows"] == o["rows"], "D: the live leaderboard (index) = 0.4.31's file scan for every slot (%d rows in slot 0)" % len(o["rows"][0]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
