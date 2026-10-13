"""SkyyWorldGen 0.5.1 - bare-JVM harness for THE HYTALE 0.7.0 PORT (tools/worldgen_0_5_1_patch.py). Child JVM: the game's own JRE, the 0.7.0
HytaleServer.jar, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The 0.7.0 engine stand-ins (packet
sink, store, worlds with a task queue, Universe, an async spawn provider) come from SkyyProfiles/test_skyyprofiles_0.1.10.py (engine()).
The live Skyy_SkyyWorldGen folder is only READ (copied into scratch) and checked afterwards.

    python SkyyWorldGen/test_skyyworldgen_0.5.1.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyWorldGen-0.5.1.jar] [--prev SkyyWorldGen-0.5.jar]

SECTIONS
  CC  CLASS COMPARE 0.5 -> 0.5.1: + exactly WgSpawnTask; structural changes only WgOpen.safeReturn / go / sendDefault + the new spawnNow /
      spawnTeleport, arrival gone; everything else = version constants
  JT  jar entries: 0.5's classes + WgSpawnTask; every non-class entry byte-identical but the manifest (version)
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7.0 engine
  Z   WgOpen EXECUTED:
        Z1 /zone proof while ON the proof island (decide = 2, no landing point): an instant provider -> ONE WgSpawnTask on the player's world,
           no teleport before it runs; then Teleport to the island's spawn point + "Back to the landing point" after it
        Z2 the same with an ASYNC provider finished on ANOTHER thread (that thread queues the task)     Z3 no spawn point -> (0, 100, 0) as 0.5
        Z4 Zone 1 while on it (a landing point): the immediate Teleport at the landing, no task (0.5's path)
        Z5 sendDefault (/zone leave's fallback): true, the task teleports to the main world's spawn; the future fails -> no teleport + "There
           is no world to send you to - try /hub."; the default world is a zone island -> false
        Z6 leave() on the proof island: the engine's exitInstance is not running -> the fallback line + the async teleport
        Z7 safeReturn: a given return point kept; none + an instant provider -> a copy of the spawn point; + a pending async provider -> the
           provider's first spawn point (getSpawnPoints); + no point at all -> (0, 100, 0); a failed future -> getSpawnPoints
        Z8 the player left the world before the answer -> nothing
        Z9 CONTROL: 0.5's sendDefault throws NoSuchMethodError on 0.7.0; 0.5's safeReturn swallows it and returns (0, 100, 0) (the wrong
           return point a new island would have stored)
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyWorldGen (WgCfg.load, WgStore.read, the config kit): no file changed
  AA  python tools/ci/crosscheck.py --jar <0.5.1> --baseline: no FAIL for SkyyWorldGen on 0.7.0, the command tree identical to 0.5
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.5.1", "0.5"
PKG = "com.skyy.worldgen."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pages07", "worldgen")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyWorldGen-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyWorldGen")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")     # the shared JVM helpers (read only)
PROF_HARNESS = os.path.join(ROOT, "SkyyProfiles", "test_skyyprofiles_0.1.10.py")   # engine() - the 0.7.0 stand-ins
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass
    import skyybuild as B
    S = mod(SKILLS_HARNESS, "ts0427")
    TP = mod(PROF_HARNESS, "tp0110")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    S.jvm_start([hcls])
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR)):
        L[tag] = S.loader(j)
        R["load"][tag] = S.load_all(j, L[tag])
    try:
        N = TP.engine(S, B, hcls, "skyywg07")
        jf, U = N["jf"], N["U"]
        UUID, Paths, Thread = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Thread")
        TRF = JClass("com.hypixel.hytale.math.vector.Transform")
        GSP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider")
        WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
        WCFGc = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
        UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        AB = JClass("java.util.concurrent.atomic.AtomicBoolean")
        HLB, HL = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend"), JClass("com.hypixel.hytale.logger.HytaleLogger")
        RECS = JClass("java.util.concurrent.CopyOnWriteArrayList")()
        HLB.subscribe(RECS)

        def logs():
            out_ = []
            for i in range(int(RECS.size())):
                r = RECS.get(i)
                try:
                    out_.append("%s %s" % (r.getLevel(), r.getMessage()))
                except Exception:
                    out_.append(str(r))
            return out_

        def jc(k, n):
            return JClass(PKG + n, loader=L[k])
        for k in ("new", "prev"):
            jc(k, "WgLog").LOG = HL.get("SkyyWorldGenHarness" + k)
        WN = dict((k, [str(x) for x in jc(k, "WgZones").WORLDS]) for k in ("new", "prev"))
        uni = UniC.get()
        byname = jf(UniC.class_, "worlds").get(uni)

        def world(name, gen=None):
            w, wu, cfg = N["mkworld"](name)
            jf(WLDc.class_, "alive").set(w, AB(True))
            byname.put(name.lower(), w)
            if gen is not None:
                jf(WCFGc.class_, "worldGenProvider").set(cfg, gen)
            return w, wu, cfg
        HUB, HUBU, HUBC = world("harness_main")
        PROOF, PROOFU, PROOFC = world(WN["new"][1], U.allocateInstance(jc("new", "WgIsleProvider").class_))
        HPc = JClass("com.hypixel.hytale.builtin.hytalegenerator.plugin.HandleProvider")
        hp = U.allocateInstance(HPc.class_)
        hp.setWorldStructureName(str(jc("new", "WgZones").STRUCTURES[0]))
        Z1, Z1U, Z1C = world(WN["new"][0], hp)
        N["UniH"].DEF = HUB
        HUB_SP = TRF(0.5, 120.0, 0.5, 0.0, 0.0, 0.0)
        PROOF_SP = TRF(33.5, 140.0, -12.5, 0.0, 90.0, 0.0)
        HUBC.setSpawnProvider(GSP(HUB_SP))
        PROOFC.setSpawnProvider(GSP(PROOF_SP))
        for k in ("new", "prev"):
            jc(k, "WgCheck").OK[0] = True
            jc(k, "WgCheck").OK[1] = True
        Open = jc("new", "WgOpen")
        U1 = UUID.fromString("00000000-0000-0000-0000-0000000000e1")
        E = {}

        def on(w, wu):
            return N["player"](U1, w, wu)

        def tasks(w):
            return 0 if w.tasks is None else int(w.tasks.size())
        lab1 = str(jc("new", "WgZones").label(1))
        # Z1 decide 2 on the proof island, instant provider
        P = on(PROOF, PROOFU)
        d = int(Open.decide(1, PROOF))
        Open.go(P.st, P.ref, P.pr, PROOF, 1)
        q, b = tasks(PROOF), N["tp_of"](P)
        ran = N["run_world"](PROOF)
        E["z1"] = [d, q, b, ran, N["tp_of"](P), ("Back to the landing point of " + lab1) in N["chat"](P)]
        # Z2 async
        LS = N["LaterSpawn"]()
        PROOFC.setSpawnProvider(LS)
        P = on(PROOF, PROOFU)
        Open.go(P.st, P.ref, P.pr, PROOF, 1)
        q0, said0 = tasks(PROOF), N["chat"](P)
        PROOF.by.clear()
        th = Thread(N["Finish"](LS.f, TRF(30.0, 150.0, -10.0, 0.0, 0.0, 0.0), None), "harness-spawn-io")
        th.start()
        th.join()
        q1, who = tasks(PROOF), [str(x) for x in PROOF.by]
        N["run_world"](PROOF)
        E["z2"] = [q0, said0 == "", q1, who, N["tp_of"](P), "Back to the landing point" in N["chat"](P)]
        # Z3 no spawn point -> (0, 100, 0)
        P = on(PROOF, PROOFU)
        Open.go(P.st, P.ref, P.pr, PROOF, 1)
        LS.f.complete(None)
        N["run_world"](PROOF)
        E["z3"] = [N["tp_of"](P), "Back to the landing point" in N["chat"](P)]
        # Z4 Zone 1 with its landing point: immediate
        P = on(Z1, Z1U)
        d4 = int(Open.decide(0, Z1))
        Open.go(P.st, P.ref, P.pr, Z1, 0)
        land = [float(x) for x in jc("new", "WgCfg").landing(0)]
        E["z4"] = [d4, tasks(Z1), N["tp_of"](P), land, "Back to the landing point" in N["chat"](P)]
        # Z5 sendDefault
        P = on(PROOF, PROOFU)
        r5 = bool(Open.sendDefault(P.st, P.ref, P.pr))
        q5 = tasks(PROOF)
        N["run_world"](PROOF)
        z5a = [r5, q5, N["tp_of"](P)]
        LH = N["LaterSpawn"]()
        HUBC.setSpawnProvider(LH)
        P = on(PROOF, PROOFU)
        r5b = bool(Open.sendDefault(P.st, P.ref, P.pr))
        RECS.clear()
        LH.f.completeExceptionally(JClass("java.lang.IllegalStateException")("harness: chunk load failed"))
        N["run_world"](PROOF)
        z5b = [r5b, N["tp_of"](P), "There is no world to send you to - try /hub." in N["chat"](P), [x for x in logs() if "could not be found" in x][:1]]
        N["UniH"].DEF = PROOF
        P = on(PROOF, PROOFU)
        z5c = [bool(Open.sendDefault(P.st, P.ref, P.pr)), tasks(PROOF)]
        N["UniH"].DEF = HUB
        HUBC.setSpawnProvider(GSP(HUB_SP))
        E["z5"] = [z5a, z5b, z5c]
        # Z6 leave() (the engine's exitInstance is not running)
        P = on(PROOF, PROOFU)
        RECS.clear()
        Open.leave(P.st, P.ref, P.pr, PROOF)
        q6 = tasks(PROOF)
        N["run_world"](PROOF)
        E["z6"] = [q6, N["tp_of"](P), "Leaving the island - to the main world spawn..." in N["chat"](P), [x for x in logs() if "exitInstance failed" in x][:1]]
        # Z7 safeReturn + spawnNow
        P = on(HUB, HUBU)
        given = TRF(1.0, 2.0, 3.0, 0.0, 0.0, 0.0)

        def pos(t):
            if t is None:
                return None
            p_ = t.getPosition()
            return [round(float(p_.x()), 2), round(float(p_.y()), 2), round(float(p_.z()), 2)]
        z7 = [Open.safeReturn(HUB, P.pr, given) == given]
        sr = Open.safeReturn(HUB, P.pr, None)
        z7.append([pos(sr), int(JClass("java.lang.System").identityHashCode(sr)) != int(JClass("java.lang.System").identityHashCode(HUB_SP))])
        HUBC.setSpawnProvider(N["LaterSpawn"]())
        z7.append(pos(Open.safeReturn(HUB, P.pr, None)))
        hclsW = JClass("skyywg07.LaterSpawn")
        jf(WCFGc.class_, "spawnProvider").set(HUBC, None)
        jf(WCFGc.class_, "defaultSpawnProvider").set(HUBC, None)
        z7.append(pos(Open.safeReturn(HUB, P.pr, None)))
        z7.append(pos(Open.safeReturn(None, P.pr, None)))
        LF = N["LaterSpawn"]()
        HUBC.setSpawnProvider(LF)
        LF.getSpawnPointAsync(HUB, U1)
        LF.f.completeExceptionally(JClass("java.lang.IllegalStateException")("x"))
        jf(JClass("skyywg07.LaterSpawn").class_, "f")
        z7.append(pos(Open.spawnNow(HUB, P.pr)))
        HUBC.setSpawnProvider(GSP(HUB_SP))
        E["z7"] = z7
        # Z8 the player left the world
        PROOFC.setSpawnProvider(LS)
        P = on(PROOF, PROOFU)
        Open.go(P.st, P.ref, P.pr, PROOF, 1)
        jf(PRc.class_, "worldUuid").set(P.pr, HUBU)
        LS.f.complete(TRF(9.0, 9.0, 9.0, 0.0, 0.0, 0.0))
        E["z8"] = [N["run_world"](PROOF), N["tp_of"](P), N["chat"](P) == ""]
        # Z9 control
        Old = jc("prev", "WgOpen")
        P = on(PROOF, PROOFU)
        try:
            Old.sendDefault(P.st, P.ref, P.pr)
            ctl = "no error"
        except Exception as e_:
            ctl = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
        E["z9"] = [ctl, pos(Old.safeReturn(HUB, P.pr, None))]
        # ================================================================================ ST: two starts on a COPY of the live data
        home = os.path.join(SCRATCH, "st", "mods", "Skyy_SkyyWorldGen")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        Cfg, Store, Pub = jc("new", "WgCfg"), jc("new", "WgStore"), jc("new", "CfgPub")
        starts = []
        for n_ in range(2):
            b0 = snap(home)
            Cfg.DIR = Paths.get(home)
            Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
            Store.FILE = Paths.get(os.path.join(home, "worlds.properties"))
            Cfg.load()
            Store.read()
            Pub.start(Paths.get(os.path.dirname(home)), None)
            Pub.flush()
            time.sleep(0.4)
            Pub.flush()
            made = Store.createdText(jc("new", "WgZones").WORLDS[0])
            Pub.shutdown()
            a0 = snap(home)
            starts.append([sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)), None if made is None else str(made), str(Cfg.LOADED)[:80]])
        E["st"] = [starts, len(snap(home))]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    z1 = E["z1"]
    check(z1 == [2, 1, None, 1, [z1[4][0], 33.5, 140.0, -12.5], True] and z1[4][0].startswith("skywynn_proof"),
          "Z1: /zone proof on the proof island (decide 2, no landing): ONE WgSpawnTask, no teleport before it runs, then Teleport to the island's "
          "spawn + the 'Back to the landing point' line: %s" % z1)
    z2 = E["z2"]
    check(z2[0] == 0 and z2[1] and z2[2] == 1 and z2[3] == ["harness-spawn-io"] and z2[4][1:] == [30.0, 150.0, -10.0] and z2[5],
          "Z2: async provider - nothing queued / said until the future finishes on ANOTHER thread, which queues the task; it teleports: %s" % z2)
    check(E["z3"][0][1:] == [0.0, 100.0, 0.0] and E["z3"][1], "Z3: no spawn point -> (0, 100, 0) as 0.5: %s" % E["z3"])
    z4 = E["z4"]
    check(z4[0] == 2 and z4[1] == 0 and z4[2] is not None and z4[2][1:] == [round(z4[3][0], 2), round(z4[3][1], 2), round(z4[3][2], 2)] and z4[4],
          "Z4: Zone 1 with its landing point - the immediate Teleport at the landing, no task (0.5's path): %s" % z4)
    a, b, c = E["z5"]
    check(a == [True, 1, ["harness_main", 0.5, 120.0, 0.5]], "Z5: sendDefault - true, the task teleports to the main world's spawn: %s" % a)
    check(b[0] and b[1] is None and b[2] and b[3], "Z5: the future fails - no teleport, 'There is no world to send you to - try /hub.', a warning: %s" % b)
    check(c == [False, 0], "Z5: the default world is a zone island - false, nothing asked: %s" % c)
    z6 = E["z6"]
    check(z6[0] == 1 and z6[1] == ["harness_main", 0.5, 120.0, 0.5] and z6[2] and z6[3], "Z6: leave() - exitInstance fails here, the fallback "
          "line + the async teleport to the main world's spawn: %s" % z6)
    z7 = E["z7"]
    check(z7 == [True, [[0.5, 120.0, 0.5], True], [7.0, 77.0, 7.0], [0.0, 100.0, 0.0], [0.0, 100.0, 0.0], [7.0, 77.0, 7.0]],
          "Z7: safeReturn - a given point kept; a copy of an instant spawn point; a pending async provider -> its first spawn point; nothing -> "
          "(0, 100, 0); spawnNow on a failed future -> getSpawnPoints: %s" % z7)
    check(E["z8"] == [1, None, True], "Z8: the player left the world - nothing: %s" % E["z8"])
    check(E["z9"] == ["java.lang.NoSuchMethodError", [0.0, 100.0, 0.0]], "Z9: CONTROL - 0.5's sendDefault throws on 0.7.0, its safeReturn falls "
          "back to (0, 100, 0) instead of the spawn point: %s" % E["z9"])
    st, nfiles = E["st"]
    check(len(st) == 2 and all(s_[0] == [] for s_ in st) and st[0][1:] == st[1][1:], "ST: two starts on a COPY of the live Skyy_SkyyWorldGen (%d "
          "files): no file changed, the same state read: %s" % (nfiles, st))


# ============================================================================================ parent
def main():
    if "--e" in sys.argv:
        return run_e(arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)
    try:
        # ---- CC
        # the 0.7.0 engine declares getGenerator on ChunkGrid (ChunkStore's superclass): the same source line compiles to a method ref on
        # ChunkGrid (WgIsle.genOf) - mapped back so only real changes count as structural
        rules = [[r"worldgen_0_5_1_patch", "worldgen_0_5_patch"],
                 [r"storage\.ChunkGrid\.getGenerator", "storage.ChunkStore.getGenerator"]]
        kid = [re.search(rb"skyyui \d+\.\d+ [0-9a-f]{12}", b"".join(zipfile.ZipFile(j_).read(n) for n in zipfile.ZipFile(j_).namelist() if n.endswith("Plugin.class")))
               for j_ in (JAR, PREV_JAR)]
        if kid[0] and kid[1]:
            rules.append([re.escape(kid[0].group(0).decode()), kid[1].group(0).decode()])
        out_cc = os.path.join(SCRATCH, "cc.json")
        with open(out_cc + ".log", "wb") as lf:
            subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import importlib.util as u; "
                            "s = u.spec_from_file_location('ts', %r); m = u.module_from_spec(s); sys.argv = ['x', '--dir', %r]; "
                            "s.loader.exec_module(m); m.SCRATCH = %r; m.run_cc(%r, %r, %r, %r)" % (
                                TOOLS, SKILLS_HARNESS, SCRATCH, SCRATCH, JAR, PREV_JAR, out_cc,
                                json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules}))],
                           env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
        cc = json.load(open(out_cc)) if os.path.isfile(out_cc) else None
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            check(cc["added"] == ["WgSpawnTask"] and cc["gone"] == [], "CC: + exactly WgSpawnTask, none gone: %s %s" % (cc["added"], cc["gone"]))
            check(not [c for c, v in cls_.items() if v["fields_new"] or v["fields_gone"]] and all(v["same_shape"] for v in cls_.values()),
                  "CC: no field added / removed, same supers / interfaces")
            struct = dict((c, sorted(x.split("(")[0] + (" (new)" if x.endswith("(new)") else " (gone)" if x.endswith("(gone)") else "") for x in v["structural"]))
                          for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(v["const_only"])) for c, v in cls_.items() if v["const_only"])
            print("CC. 0.5 -> 0.5.1 structural %s; constants only %s" % (struct, const))
            check(struct == {"WgOpen": ["arrival (gone)", "go", "safeReturn", "sendDefault", "spawnNow (new)", "spawnTeleport (new)"]},
                  "CC: the only structural changes = WgOpen go / safeReturn / sendDefault + spawnNow / spawnTeleport, arrival gone: %s" % struct)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        cn, cp_ = set(n for n in zj.namelist() if n.endswith(".class")), set(n for n in zp.namelist() if n.endswith(".class"))
        check(cn - cp_ == {"com/skyy/worldgen/WgSpawnTask.class"} and not (cp_ - cn), "JT: class files = 0.5's + WgSpawnTask: %s %s"
              % (sorted(cn - cp_), sorted(cp_ - cn)))
        nn = set(n for n in zj.namelist() if not n.endswith(".class"))
        # the proof template's $Comment names the version that built it ("(SkyyWorldGen 0.5.1)")
        norm = lambda b_: b_.replace(b"(SkyyWorldGen %s)" % VERSION.encode(), b"(SkyyWorldGen %s)" % PREV_VERSION.encode())
        diff = sorted(n for n in nn if n != "manifest.json" and (n not in zp.namelist() or norm(zj.read(n)) != zp.read(n)))
        vdiff = sorted(n for n in nn if n != "manifest.json" and n in zp.namelist() and zj.read(n) != zp.read(n))
        check(nn == set(n for n in zp.namelist() if not n.endswith(".class")) and not diff and vdiff == ["Server/Instances/SkyWynn_Proof2/instance.bson"],
              "JT: every non-class entry byte-identical but the manifest and the version in the proof template's comment: %s %s" % (diff[:4], vdiff))
        mn, mpn = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mpn, sort_keys=True).replace('"%s"' % PREV_VERSION, '"%s"' % VERSION).replace("%s SkyyWorldGen" % PREV_VERSION, "%s SkyyWorldGen" % VERSION),
              "JT: manifest = 0.5's but the version")
        # ---- A + Z + ST
        out_e = os.path.join(SCRATCH, "e.json")
        with open(out_e + ".log", "wb") as lf:
            subprocess.run([sys.executable, me, "--e", "--out", out_e, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env, stdout=lf, stderr=subprocess.STDOUT)
        r = json.load(open(out_e)) if os.path.isfile(out_e) else None
        if r is None:
            print(open(out_e + ".log", encoding="utf8", errors="replace").read()[-3000:])
        check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-3000:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 20, "A (%s): %d classes load, verify (-Xverify:all), initialise on 0.7.0 %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check_e(r["E"])
        # ---- AA
        out_aa = os.path.join(SCRATCH, "aa.log")
        with open(out_aa, "wb") as lf:
            subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                           stderr=subprocess.STDOUT, cwd=ROOT)
        aa = open(out_aa, encoding="utf8", errors="replace").read()
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyWorldGen " in ln]
        check("access:" in aa and not mine, "AA: crosscheck --jar 0.5.1: no FAIL for SkyyWorldGen on 0.7.0: %s" % mine[:3])
        check("baseline SkyyWorldGen %s -> %s: command / permission tree identical" % (PREV_VERSION, VERSION) in aa, "AA: the command / permission tree = 0.5's")
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        check(not chg, "the live Skyy_SkyyWorldGen folder is unchanged: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyWorldGen %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
