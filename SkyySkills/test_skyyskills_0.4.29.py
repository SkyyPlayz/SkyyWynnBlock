"""SkyySkills 0.4.29 - bare-JVM harness for THE PET XP HOOK (tools/skills_0_4_29_patch.py; research/cloud/Pet-Core-Spec.md 1 "XP in").
Every child JVM runs the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP /
java.io.tmpdir in the scratch folder. Live save data is only ever READ and copied into scratch (checked: the live files are unchanged).

    python SkyySkills/test_skyyskills_0.4.29.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyySkills-0.4.29.jar] [--prev SkyySkills-0.4.28.jar] [--pets SkyyPets/SkyyPets-0.1.jar] [--live <Skyy_SkyySkills folder>]

SECTIONS
  A   every class of the new jar loads, verifies (-Xverify:all) and initialises
  CC  CLASS COMPARE 0.4.28 -> 0.4.29 (javassist instruction text, version strings normalised): only SkillXp (gain4 + the new petXp + field
      PET_WARNED), SmeltTask.run and the plugin's setup (ready line) differ; no class added / removed
  CL  CALLERS (bytecode): the only methods calling SkillStore.addK are SkillXp.gain4 and SmeltTask.run, and both call SkillXp.petXp;
      every gain / gain2 / gain3 / gain4 caller in the jar listed (all award paths funnel into gain4)
  H   EXECUTED on the REAL classes with a stub pets:fn:onxp (records every call + its thread): gain (gathering), gain2 (Acrobatics style,
      no note), gain3 raw (admin /skills xp + bridge style), gain4 with a party name (party share), a class skill award (Archery), a
      level-up award (chat lines through a stand-in PacketHandler), the REAL BridgeXp.offerX -> BridgeTask (cross-mod grants: Exploration,
      Fishing, Cooking, heal XP all come this way), SmeltTask online + OFFLINE (addK straight), amount 0 / refused bridge offer (no call);
      each award = exactly ONE call { UUID (the player's), NAMES[slot], Long = the XP really added, "SkyySkills" } on the award's thread.
      ABSENT bridge entry, a non-Function value, a THROWING function (award still stored, no exception, one WARN per JVM),
      PROFILE SWITCH (profile:fn:key -> <uuid>-p2: XP lands in the -p2 data, the hook still gets the player UUID; a BridgeTask / SmeltTask
      queued for the old profile pays nothing and calls nothing). The 0.4.28 jar run the same way = 0 calls (control).
  PT  the REAL SkyyPets 0.1 PetXpFn (own class loader, shared bridge): a 3-element call leaves its fallback poll ON (PetXp.HOOKED false);
      the first SkyySkills 0.4.29 award switches it OFF (HOOKED true; PetXp.poll() = 0)
  ST  START TWICE on a scratch COPY of the live Skyy_SkyySkills (the 0.4.25 harness's start routine: every one-time migration, SkillCfg.load,
      ClassCurve / OwnCurve), both jars: 0.4.29 changes exactly what 0.4.28 changes; start 2 changes nothing; player files untouched
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.29", "0.4.28"
PKG = "com.skyy.skills."
MINING, FORAGING, COMBAT, ACRO, ARCHERY, ALCHEMY, SMITHING, COOKING, EXPLORATION = 0, 1, 3, 4, 5, 10, 11, 12, 13


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0429", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
PETS_JAR = os.path.abspath(arg("--pets", os.path.join(ROOT, "SkyyPets", "SkyyPets-0.1.jar")))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


def t15():
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs)


# ============================================================================================ child: CL (callers, javassist text)
def run_callers(jar, out):
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    R = {"addK": [], "petXp": [], "gain": {}, "onxp_ldc": []}
    for n in [x[:-6].replace("/", ".") for x in zipfile.ZipFile(jar).namelist() if x.endswith(".class")]:
        cc = cp.get(n)
        for m in list(cc.getDeclaredMethods()) + list(cc.getDeclaredConstructors()):
            mi = m.getMethodInfo()
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            it, pool, lines = ca.iterator(), mi.getConstPool(), []
            while it.hasNext():
                lines.append(str(IP.instructionString(it, it.next(), pool)))
            t = "\n".join(lines)
            where = "%s.%s" % (n.rsplit(".", 1)[-1], m.getName())
            if "SkillStore.addK(" in t:
                R["addK"].append(where)
            if "SkillXp.petXp(" in t:
                R["petXp"].append(where)
            if "pets:fn:onxp" in t:
                R["onxp_ldc"].append(where)
            for g in ("gain(", "gain2(", "gain3(", "gain4("):
                if ("SkillXp." + g) in t:
                    R["gain"].setdefault(g[:-1], []).append(where)
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ child: H + PT (one Skills jar)
def run_hook(jar, fake, pets_jar, home, out):
    from jpype import JClass, JArray, JImplements, JOverride, JLong
    T = t15()
    res, path = T.common(jar, [fake])
    R = {"loaded": res["loaded"], "classes": res["classes"], "load_fails": res["load_fails"]}
    if res["load_fails"]:
        json.dump(R, open(out, "w"), indent=1)
        return
    UUID, CHM = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap")
    JObj, JStr, JLongC, Thread = JClass("java.lang.Object"), JClass("java.lang.String"), JClass("java.lang.Long"), JClass("java.lang.Thread")
    J = lambda n: JClass(PKG + n)
    Cfg, Xp, Store, Defs, Bx = J("SkillCfg"), J("SkillXp"), J("SkillStore"), J("SkillDefs"), J("BridgeXp")
    Smelt = J("SmeltTask")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    FakeH, FakeW = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def getf(obj, cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f.get(obj)

    def alloc(cls):
        return U.allocateInstance(cls.class_)
    D = {}
    try:
        Cfg.LOG = HL.get("SkyySkills")
        Cfg.FILE = path(os.path.join(home, "xp.properties"))
        D["cfg"] = str(Cfg.load())[:200]
        players = os.path.join(home, "players")
        Store.DIR = path(players)
        Store.DATA.clear()
        bridge = Store.bridge()
        uni = alloc(Universe)
        PLAYERS, WORLDS = CHM(), CHM()
        setf(uni, Universe, "playersByUuid", PLAYERS)
        setf(uni, Universe, "players", PLAYERS.values())
        setf(uni, Universe, "worldsByUuid", WORLDS)
        setf(None, Universe, "instance", uni)
        wuid = UUID(0x3029D, 1)
        WORLDS.put(wuid, alloc(FakeW))
        handler, holder = alloc(FakeH), alloc(Holder)
        TEXTS = getf(None, FakeH, "TEXTS")

        def mkpr(u, name):
            pr = alloc(PRef)
            setf(pr, PRef, "uuid", u)
            setf(pr, PRef, "username", name)
            setf(pr, PRef, "packetHandler", handler)
            setf(pr, PRef, "worldUuid", wuid)
            setf(pr, PRef, "holder", holder)
            PLAYERS.put(u, pr)
            return pr
        CALLS = []
        ACTIVE = {}

        @JImplements("java.util.function.Function")
        class PetStub(object):
            @JOverride
            def apply(self, o):
                a = list(o)
                CALLS.append({"n": len(a), "u_cls": str(a[0].getClass().getName()) if a and a[0] is not None else None, "u": str(a[0]),
                              "skill": str(a[1]) if len(a) > 1 else None, "amt_cls": str(a[2].getClass().getName()) if len(a) > 2 else None,
                              "amt": int(a[2].longValue()) if len(a) > 2 else None, "src": str(a[3]) if len(a) > 3 else None,
                              "thread": str(Thread.currentThread().getName())})
                return JClass("java.lang.Boolean").TRUE

        @JImplements("java.util.function.Function")
        class Thrower(object):
            def __init__(self):
                self.n = 0

            @JOverride
            def apply(self, o):
                self.n += 1
                raise JClass("java.lang.IllegalStateException")("pets boom")

        @JImplements("java.util.function.Function")
        class PKey(object):
            @JOverride
            def apply(self, o):
                k = ACTIVE.get(str(o))
                return k if k is not None else str(o)
        bridge.put("profile:fn:key", PKey())
        me = str(Thread.currentThread().getName())
        D["thread"] = me
        u = UUID(0x3029, 7)
        pr = mkpr(u, "PetTester")

        def xp_of(slot, key=None):
            return int(Store.dataK(key if key else str(u), u)[slot])

        def award(tag, fn, slot, key=None):
            del CALLS[:]
            b = xp_of(slot, key)
            err = None
            try:
                fn()
            except Exception as e:
                err = str(e)[:300]
            D[tag] = {"delta": xp_of(slot, key) - b, "calls": list(CALLS), "err": err}
        bridge.put("pets:fn:onxp", PetStub())
        award("gain", lambda: Xp.gain(pr, MINING, JLong(7)), MINING)
        award("gain2", lambda: Xp.gain2(pr, ACRO, JLong(5), False), ACRO)
        award("gain3", lambda: Xp.gain3(pr, ALCHEMY, JLong(9), True, False), ALCHEMY)
        award("gain4p", lambda: Xp.gain4(pr, FORAGING, JLong(13), False, False, "Killer"), FORAGING)
        award("class", lambda: Xp.gain3(pr, ARCHERY, JLong(11), True, False), ARCHERY)
        TEXTS.clear()
        award("levelup", lambda: Xp.gain3(pr, COOKING, JLong(5000), True, False), COOKING)
        D["levelup"]["texts"] = [str(t) for t in TEXTS][:6]
        D["levelup"]["lv"] = int(Store.level(u, COOKING))
        # the REAL bridge grant: BridgeXp.offerX -> FakeWorld.execute -> BridgeTask.run (gain3) (Exploration / Fishing / Cooking / heals)
        rr = []
        award("bridge", lambda: rr.append(int(Bx.offerX(u, EXPLORATION, JLong(25), "harness", None, None, 0, True, True))), EXPLORATION)
        D["bridge"]["ret"] = rr[:]
        rr2 = []
        award("bridge_mining", lambda: rr2.append(int(Bx.offerX(u, MINING, JLong(4), "harness fishing", None, None, 0, True, True))), MINING)
        D["bridge_mining"]["ret"] = rr2[:]
        award("smelt", lambda: Smelt(u, SMITHING, JLong(6), str(u)).run(), SMITHING)
        PLAYERS.remove(u)
        award("smelt_off", lambda: Smelt(u, SMITHING, JLong(8), str(u)).run(), SMITHING)
        PLAYERS.put(u, pr)
        award("zero", lambda: Xp.gain(pr, MINING, JLong(0)), MINING)
        rr3 = []
        award("refused", lambda: rr3.append(int(Bx.offerX(u, COMBAT, JLong(5), "harness", None, None, 0, True, True))), COMBAT)
        D["refused"]["ret"] = rr3[:]
        # absent / not a Function / throwing
        bridge.remove("pets:fn:onxp")
        award("absent", lambda: Xp.gain(pr, MINING, JLong(3)), MINING)
        award("absent_smelt_off", lambda: (PLAYERS.remove(u), Smelt(u, SMITHING, JLong(2), str(u)).run(), PLAYERS.put(u, pr)), SMITHING)
        bridge.put("pets:fn:onxp", JStr("not a function"))
        award("notfn", lambda: Xp.gain(pr, MINING, JLong(3)), MINING)
        th = Thrower()
        bridge.put("pets:fn:onxp", th)
        D["warned0"] = bool(getattr(Xp, "PET_WARNED", False))
        print("[harness-mark] throw-start", flush=True)
        award("throw1", lambda: Xp.gain(pr, MINING, JLong(3)), MINING)
        award("throw2", lambda: Xp.gain3(pr, ALCHEMY, JLong(4), True, False), ALCHEMY)
        print("[harness-mark] throw-end", flush=True)
        D["throw_n"] = th.n
        D["warned1"] = bool(getattr(Xp, "PET_WARNED", False))
        # profile switch: the active profile is now <uuid>-p2
        bridge.put("pets:fn:onxp", PetStub())
        k1 = str(u)
        k2 = str(u) + "-p2"
        ACTIVE[str(u)] = k2
        b1 = xp_of(MINING, k1)
        award("p2", lambda: Xp.gain(pr, MINING, JLong(10)), MINING, k2)
        D["p2"]["p1_delta"] = xp_of(MINING, k1) - b1
        award("p2_stale_smelt", lambda: Smelt(u, SMITHING, JLong(6), k1).run(), SMITHING, k1)
        rr4 = []
        award("p2_stale_bridge", lambda: rr4.append(int(Bx.offerX(u, EXPLORATION, JLong(5), "harness", k1, None, 0, True, True))), EXPLORATION, k1)
        D["p2_stale_bridge"]["ret"] = rr4[:]
        award("p2_bridge", lambda: Bx.offerX(u, EXPLORATION, JLong(5), "harness", k2, None, 0, True, True), EXPLORATION, k2)
        ACTIVE.clear()
        D["names"] = [str(x) for x in Defs.NAMES]
        # ---------------------------------------------------------------- PT: the REAL SkyyPets 0.1 PetXpFn (own loader)
        if pets_jar and os.path.isfile(pets_jar):
            URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
            urls = JArray(URL)(1)
            urls[0] = File(pets_jar).toURI().toURL()
            ld = URLCL(urls, JClass("java.lang.ClassLoader").getSystemClassLoader())
            PFn = JClass("com.skyy.pets.PetXpFn", loader=ld)
            PXp = JClass("com.skyy.pets.PetXp", loader=ld)
            P = {"hooked0": bool(PXp.HOOKED)}
            fn = PFn()
            fn.apply(JArray(JObj)([u, JStr("Mining"), JLongC.valueOf(5)]))
            P["hooked_3el"] = bool(PXp.HOOKED)
            bridge.put("pets:fn:onxp", fn)
            b = xp_of(MINING)
            err = None
            try:
                Xp.gain(pr, MINING, JLong(6))
            except Exception as e:
                err = str(e)[:300]
            P["err"] = err
            P["delta"] = xp_of(MINING) - b
            P["hooked_after"] = bool(PXp.HOOKED)
            try:
                P["poll"] = int(PXp.poll())
            except Exception as e:
                P["poll"] = "error " + str(e)[:200]
            bridge.remove("pets:fn:onxp")
            D["PT"] = P
        else:
            D["PT"] = {"missing": pets_jar}
        Store.DATA.clear()
        Store.DIRTY.clear()
    except Exception:
        import traceback
        D["error"] = traceback.format_exc()[-3000:]
    R["D"] = D
    json.dump(R, open(out, "w"), indent=1)


# ============================================================================================ parent
def child(env, log, *a):
    with open(log, "wb") as lf:
        p = subprocess.run([sys.executable, os.path.abspath(__file__)] + list(a) + ["--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
    return p.returncode


def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--hook" in sys.argv:
        return run_hook(arg("--hook"), arg("--fake"), arg("--pets-jar"), arg("--home"), arg("--out"))
    if "--callers" in sys.argv:
        return run_callers(arg("--callers"), arg("--out"))
    if "--cc" in sys.argv:
        t27 = tmod("test_skyyskills_0.4.27.py", "t0427")
        return t27.run_cc(arg("--cc"), arg("--prev-jar"), arg("--out"), arg("--repl"))
    if "--start" in sys.argv:
        t25 = tmod("test_skyyskills_0.4.25.py", "t0425")
        t25.SCRATCH = arg("--start-dir")
        return t25.run_start(arg("--start"), arg("--out"), "new")
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/, not %s" % SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live0 = snap(LIVE_DIR)
    fake = os.path.join(SCRATCH, "fake")
    check(child(env, os.path.join(SCRATCH, "mkfake.log"), "--mkfake", fake) == 0, "stand-in classes generated")
    # ---------------------------------------------------------------- H + PT (new jar) and the control (0.4.28)
    res = {}
    for tag, jar in (("new", JAR), ("prev", PREV_JAR)):
        home = os.path.join(SCRATCH, "home-" + tag)
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(SCRATCH, "hook-%s.json" % tag)
        log = os.path.join(SCRATCH, "hook-%s.log" % tag)
        rc = child(env, log, "--hook", jar, "--fake", fake, "--pets-jar", PETS_JAR if tag == "new" else "", "--home", home, "--out", out)
        check(rc == 0 and os.path.isfile(out), "H %s: child JVM ran (log %s)" % (tag, log))
        res[tag] = json.load(open(out)) if os.path.isfile(out) else {"D": {"error": "no output"}}
        res[tag]["log"] = open(log, "rb").read().decode("utf-8", "replace")
    N = res["new"]
    check(not N.get("load_fails") and N.get("loaded") == N.get("classes"), "A: %s / %s classes load + verify + initialise under -Xverify:all %s"
          % (N.get("loaded"), N.get("classes"), (N.get("load_fails") or [])[:3]))
    D = N["D"]
    check("error" not in D, "H ran: %s" % D.get("error"))
    if "error" in D:
        return finish()
    names = D["names"]
    me = D["thread"]

    def one(tag, slot, amt=None):
        d = D[tag]
        c = d["calls"]
        exp = d["delta"] if amt is None else amt
        ok = (d["err"] is None and d["delta"] > 0 and len(c) == 1 and c[0]["n"] == 4 and c[0]["u_cls"] == "java.util.UUID"
              and c[0]["u"] == "00000000-0000-3029-0000-000000000007" and c[0]["skill"] == names[slot] and c[0]["amt_cls"] == "java.lang.Long"
              and c[0]["amt"] == exp and c[0]["src"] == "SkyySkills" and c[0]["thread"] == me)
        check(ok, "H %s: one call {player UUID, %s, Long %s, SkyySkills} on the award's thread: %s" % (tag, names[slot], exp, d))
    one("gain", MINING)
    one("gain2", ACRO)
    one("gain3", ALCHEMY, 9)
    one("gain4p", FORAGING)
    one("class", ARCHERY, 11)
    one("levelup", COOKING, 5000)
    check(D["levelup"]["lv"] >= 2 and any("SKILL LEVEL UP" in t for t in D["levelup"]["texts"]), "H levelup: level-up lines still sent: %s" % D["levelup"])
    one("bridge", EXPLORATION)
    check(D["bridge"]["ret"] == [D["bridge"]["delta"]], "H bridge: offerX accepted = the XP paid (BridgeTask ran): %s" % D["bridge"]["ret"])
    one("bridge_mining", MINING)
    one("smelt", SMITHING)
    one("smelt_off", SMITHING, 8)
    check(D["zero"]["delta"] == 0 and D["zero"]["calls"] == [] and D["zero"]["err"] is None, "H zero: amount 0 = no XP, no call")
    check(D["refused"]["ret"] == [-2] and D["refused"]["calls"] == [], "H refused: a refused bridge offer (bare Combat) = no call: %s" % D["refused"])
    for t in ("absent", "absent_smelt_off", "notfn"):
        check(D[t]["delta"] > 0 and D[t]["calls"] == [] and D[t]["err"] is None, "H %s: XP stored, nothing called, no exception: %s" % (t, D[t]))
    check(D["throw1"]["delta"] == 3 and D["throw2"]["delta"] > 0 and D["throw1"]["err"] is None and D["throw2"]["err"] is None and D["throw_n"] == 2
          and not D["warned0"] and D["warned1"], "H throwing SkyyPets: both awards stored, no exception, called twice, PET_WARNED set")
    lg = N["log"]
    i, j = lg.find("[harness-mark] throw-start"), lg.find("[harness-mark] throw-end")
    nwarn = lg.count("pets:fn:onxp (SkyyPets) failed")
    check(nwarn == 1, "H throwing SkyyPets: exactly one WARN line in the log (%d)" % nwarn)
    p2 = D["p2"]
    check(p2["delta"] == 10 and p2["p1_delta"] == 0 and len(p2["calls"]) == 1 and p2["calls"][0]["u"] == "00000000-0000-3029-0000-000000000007"
          and p2["calls"][0]["u_cls"] == "java.util.UUID" and p2["calls"][0]["amt"] == 10 and p2["calls"][0]["skill"] == "Mining",
          "H profile switch: XP in <uuid>-p2, the hook gets the PLAYER UUID (SkyyPets resolves the profile): %s" % p2)
    check(D["p2_stale_smelt"]["delta"] == 0 and D["p2_stale_smelt"]["calls"] == [], "H profile switch: a SmeltTask of the old profile pays + calls nothing")
    check(D["p2_stale_bridge"]["ret"] == [-1] and D["p2_stale_bridge"]["calls"] == [], "H profile switch: a bridge grant expecting the old profile = refused, no call")
    check(D["p2_bridge"]["delta"] > 0 and len(D["p2_bridge"]["calls"]) == 1, "H profile switch: a bridge grant for the active profile = one call")
    P = D["PT"]
    check(P.get("hooked0") is False and P.get("hooked_3el") is False and P.get("err") is None and P.get("delta") == 6 and P.get("hooked_after") is True
          and P.get("poll") == 0, "PT REAL SkyyPets 0.1 PetXpFn: 3 elements leave the fallback on; the 0.4.29 award switches it off (poll 0): %s" % P)
    nl = "SkyySkills reports XP to pets itself now"
    check(lg.count(nl) <= 1, "PT: the SkyyPets 'reports XP itself' line at most once")
    C = res["prev"]["D"]
    check("error" not in C and all(C[t]["calls"] == [] for t in ("gain", "gain3", "levelup", "bridge", "smelt", "smelt_off", "p2"))
          and C["gain"]["delta"] == D["gain"]["delta"] and C["gain3"]["delta"] == 9, "H control 0.4.28: same XP, never calls pets:fn:onxp")
    print("H/PT. %d award paths -> one call each; absent / not a Function / throwing / profile switch; real SkyyPets switched its poll off" % 12)
    # ---------------------------------------------------------------- CL
    out = os.path.join(SCRATCH, "callers.json")
    check(child(env, os.path.join(SCRATCH, "callers.log"), "--callers", JAR, "--out", out) == 0, "CL child ran")
    CL = json.load(open(out))
    check(sorted(CL["addK"]) == ["SkillXp.gain4", "SmeltTask.run"] and sorted(CL["petXp"]) == ["SkillXp.gain4", "SmeltTask.run"]
          and "SkillXp.petXp" in CL["onxp_ldc"] and set(CL["onxp_ldc"]) <= {"SkillXp.petXp", "SkyySkillsPlugin.setup"},
          "CL: addK only in gain4 + SmeltTask.run, both call petXp; pets:fn:onxp only in petXp (+ the ready line): %s" % CL)
    check(CL["gain"].get("gain4") and all(set(v) for v in CL["gain"].values()), "CL: gain callers %s" % CL["gain"])
    print("CL. award callers: %s" % json.dumps(CL["gain"]))
    # ---------------------------------------------------------------- CC
    out = os.path.join(SCRATCH, "cc.json")
    repl = json.dumps({"versions": [VERSION, PREV_VERSION], "rules": []})
    check(child(env, os.path.join(SCRATCH, "cc.log"), "--cc", JAR, "--prev-jar", PREV_JAR, "--out", out, "--repl", repl) == 0, "CC child ran")
    CC = json.load(open(out))
    ch = CC["classes"]
    struct = dict((c, v["structural"]) for c, v in ch.items() if v["structural"] or v["fields_new"] or v["fields_gone"])
    check(CC["added"] == [] and CC["gone"] == [], "CC: no class added / removed: %s %s" % (CC["added"], CC["gone"]))
    check(set(struct) == {"SkillXp", "SmeltTask", "SkyySkillsPlugin"}
          and sorted(struct["SkillXp"]) == sorted(["<clinit> (new)", "gain4(Lcom/hypixel/hytale/server/core/universe/PlayerRef;IJZZLjava/lang/String;)V", "petXp(Ljava/util/UUID;IJ)V (new)"])
          and ch["SkillXp"]["fields_new"] == ["PET_WARNED:Z"] and struct["SmeltTask"] == ["run()V"]
          and len(struct["SkyySkillsPlugin"]) == 1 and struct["SkyySkillsPlugin"][0].startswith("setup"),
          "CC: only SkillXp.gain4 + petXp (+ PET_WARNED and its <clinit>), SmeltTask.run, the plugin setup differ: %s" % json.dumps(struct)[:800])
    print("CC. class compare: %s" % json.dumps(struct))
    # ---------------------------------------------------------------- ST
    st = {}
    for tag, jar in (("new", JAR), ("prev", PREV_JAR)):
        sd = os.path.join(SCRATCH, "st-" + tag)
        os.makedirs(sd)
        shutil.copytree(LIVE_DIR, os.path.join(sd, "live-copy-new"))
        out = os.path.join(SCRATCH, "st-%s.json" % tag)
        check(child(env, os.path.join(SCRATCH, "st-%s.log" % tag), "--start", jar, "--start-dir", sd, "--out", out) == 0, "ST %s child ran" % tag)
        st[tag] = json.load(open(out))
    a, b = st["new"], st["prev"]
    check("error" not in a and "error" not in b and not a["load_fails"], "ST ran: %s %s" % (a.get("error"), b.get("error")))
    check(a.get("changed1") == b.get("changed1") and a.get("changed2") == [] and b.get("changed2") == [] and a.get("players_same") and a.get("players", 0) > 0
          and a.get("xp1") == b.get("xp1"), "ST: start 1 changes what 0.4.28 changes %s, start 2 nothing, %s player files untouched"
          % (a.get("changed1"), a.get("players")))
    print("ST. start twice on a live copy: start 1 changed %s (= 0.4.28), start 2 nothing" % a.get("changed1"))
    # ---------------------------------------------------------------- AU
    auo = os.path.join(SCRATCH, "audit.json")
    check(child(env, os.path.join(SCRATCH, "audit.log"), "--audit", JAR, "--fake", fake, "--out", auo) == 0, "AU child ran")
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references, refused %s, control refused %s" % (au["refs"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references in %d classes, 0 refused (control refused)" % (au["refs"], au["classes"]))
    check(snap(LIVE_DIR) == live0, "the live Skyy_SkyySkills folder is byte-identical afterwards")
    return finish()


def finish():
    print("\n%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    if not KEEP and not FAILS:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
