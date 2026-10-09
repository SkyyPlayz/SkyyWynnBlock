"""SkyySkills 0.4.22 - bare-JVM harness for THE MONK MOVES' SKYYSKILLS PART (tools/skills_0_4_22_patch.py; Skyy 2026-10-08 "start building the
monk moves"). The new parts run on the REAL classes of the 0.4.22 jar and, as the control, the SET pin 0.4.21, with the REAL engine classes
(HytaleServer.jar on the class path, -Xverify:all); the live save data is only ever READ and copied into the scratch folder.

    python SkyySkills/test_skyyskills_0.4.22.py [--jar <SkyySkills-0.4.22.jar>] [--prev <SkyySkills-0.4.21.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep] [--no21]

SECTIONS
  A   every class of both jars loads under -Xverify:all
  B   THE MONK FLAG EXECUTED on the real classes (both jars; 0.4.21 = the control): Acro.monkMove (no key / a Long in the future / in the past /
      not a Long), Acro.noteFall + noteRoll note nothing while the flag is on (and note as before without it), Acro.airJump keeps tracking
      the crouch edge but returns before any engine call while the flag is on (the debug probe on, a null command buffer: without the flag
      it reaches the engine = the control), Acro.move with creative = the flag pays no run / jump XP (the path AcroSys.tick now takes)
  W   the wiring (bytecode): AcroSys.tick ORs Acro.monkMove into the creative flag it passes to move / dodge / falls; airJump asks it right
      after airTrack; noteFall / noteRoll ask it first
  J   the jar: 0.4.21's files minus exactly the 2 vanilla Bo item overrides; every other non-class file byte-identical
  H21 the 0.4.21 harness run against the 0.4.22 jar (control: the 0.4.21 jar): it fails nothing beyond the version-shape checks (DEF21 header,
      its F class / asset compare - only the 2 Bo files, its nested H20 for the same reasons) - its nested H20 / H19 ... = START TWICE on a
      scratch copy of the live data, saved XP read + re-saved identically, the default file
  F   class compare 0.4.21 -> 0.4.22 METHOD BY METHOD: only the planned methods differ
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.22", "0.4.21"
PKG = "com.skyy.skills."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "monkmoves01", "skills0422")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]
BO = ["Server/Item/Items/Weapon/Staff/Weapon_Staff_Bo_Bamboo.json", "Server/Item/Items/Weapon/Staff/Weapon_Staff_Bo_Wood.json"]


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
    """the 0.4.15 harness module (JVM start, class loader, access audit, stand-ins) - imported, never run"""
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t20():
    """the 0.4.20 harness module (the method-by-method class compare) - imported, never run"""
    return tmod("test_skyyskills_0.4.20.py", "t0420")


# ============================================================================================ child: one jar
def run_child(jar, out, mode):
    from jpype import JClass, JLong
    T = t15()
    res, path = T.common(jar, [])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    NEW = mode == "new"
    Acro, Store, ACfg = JClass(PKG + "Acro"), JClass(PKG + "SkillStore"), JClass(PKG + "AcroCfg")
    UUID, MST, Long = JClass("java.util.UUID"), JClass("com.hypixel.hytale.protocol.MovementStates"), JClass("java.lang.Long")
    br = Store.bridge()
    now = int(JClass("java.lang.System").currentTimeMillis())
    u = UUID.fromString("00000000-0000-0000-0000-0000000005d1")
    key = "armory:monkmove:" + str(u)
    B = {}
    if NEW:
        br.remove(key)
        B["none"] = bool(Acro.monkMove(u, now))
        br.put(key, Long(now + 500))
        B["future"] = bool(Acro.monkMove(u, now))
        B["edge"] = bool(Acro.monkMove(u, now + 500))
        br.put(key, Long(now - 1))
        B["past"] = bool(Acro.monkMove(u, now))
        br.put(key, "soon")
        B["string"] = bool(Acro.monkMove(u, now))
        B["null_u"] = bool(Acro.monkMove(None, now))
    # noteFall / noteRoll: the flag on = nothing noted; off = noted as before (both jars: the control notes in both cases)
    s = Acro.state(u)
    s[15], s[288] = 0.0, 0.0
    br.put(key, Long(int(JClass("java.lang.System").currentTimeMillis()) + 60000))
    Acro.noteFall(u, 12.5)
    Acro.noteRoll(u, 7.5)
    B["on"] = [float(s[15]), float(s[288])]
    br.remove(key)
    Acro.noteFall(u, 12.5)
    B["off_fall"] = [float(s[15]) > 0.0, float(s[16])]
    s[288] = 0.0
    s[15] = 0.0
    Acro.noteRoll(u, 7.5)
    B["off_roll"] = [float(s[288]) > 0.0, float(s[289])]
    # airJump: in the air, a crouch edge; the debug probe on so the code past the gate touches the (null) command buffer
    ACfg.DJ_DEBUG = True

    def ms_(crouch):
        m_ = MST()
        m_.onGround = False
        m_.crouching = crouch
        return m_
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000005d2")
    s2 = Acro.state(u2)
    k2 = "armory:monkmove:" + str(u2)
    out_ = {}
    for tag, flag in (("on", True), ("off", False)):
        if flag:
            br.put(k2, Long(int(JClass("java.lang.System").currentTimeMillis()) + 60000))
        else:
            br.remove(k2)
        Acro.airJump(s2, None, None, None, None, u2, ms_(False), JLong(1000))
        e_ = None
        try:
            Acro.airJump(s2, None, None, None, None, u2, ms_(True), JLong(2000))
        except Exception as ex:
            e_ = type(ex).__name__ + ": " + str(ex)[:120]
        out_[tag] = [e_, float(s2[281])]
    B["air"] = out_
    br.remove(k2)
    # Acro.move with creative = true (what AcroSys.tick passes while the flag is on): no run XP, no jump XP
    V3 = JClass("org.joml.Vector3d")
    xp = {}
    for tag, cr in (("monk", True), ("plain", False)):
        s3 = Acro.state(UUID.fromString("00000000-0000-0000-0000-0000000005d3" if cr else "00000000-0000-0000-0000-0000000005d4"))
        for i_ in range(40):
            m_ = MST()
            m_.onGround = True
            m_.running = True
            m_.jumping = (i_ % 10 == 5)
            Acro.move(s3, m_, V3(0.2 * i_, 64.0, 0.0), 0.05, 1000 + i_ * 900, cr)
        xp[tag] = round(float(s3[11]), 3)
    B["move"] = xp
    D["B"] = B
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the bytecode wiring
def run_wiring(jar, out):
    import jpype
    from jpype import JClass
    import skyybuild as SB
    jpype.startJVM(SB._jvm(), "-XX:-UsePerfData", classpath=[SB.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.insertClassPath(jar)
    cp.appendClassPath(SB.SERVER_JAR)
    cp.appendSystemPath()
    CP = JClass("javassist.bytecode.ConstPool")

    def calls(cls, meth):
        cc = cp.get(PKG + cls)
        m = [x for x in cc.getDeclaredMethods() if str(x.getName()) == meth][0]
        it, cpool = m.getMethodInfo().getCodeAttribute().iterator(), m.getMethodInfo().getConstPool()
        r = []
        while it.hasNext():
            p = it.next()
            op = it.byteAt(p)
            if op in (0xb6, 0xb7, 0xb8, 0xb9):
                i = it.u16bitAt(p + 1)
                if cpool.getTag(i) == CP.CONST_InterfaceMethodref:
                    r.append(str(cpool.getInterfaceMethodrefName(i)))
                else:
                    r.append(str(cpool.getMethodrefName(i)))
            elif op == 0x80:          # ior
                r.append("|ior")
        return r
    W = {"tick": calls("AcroSys", "tick"), "air": calls("Acro", "airJump"), "fall": calls("Acro", "noteFall"), "roll": calls("Acro", "noteRoll")}
    json.dump(W, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--child" in sys.argv:
        return run_child(arg("--child"), arg("--out"), arg("--mode"))
    if "--wiring" in sys.argv:
        return run_wiring(arg("--wiring"), arg("--out"))
    if "--audit" in sys.argv:
        return t15().run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    if "--compare" in sys.argv:
        m = t20()
        m.VERSION, m.PREV_VERSION = VERSION, PREV_VERSION
        return m.run_compare(arg("--compare"), arg("--prevjar"), arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isdir(os.path.join(LIVE_DIR, "players")):
        sys.exit("the live players folder is not in %s (pass --live <folder>; it is only ever read and copied)" % LIVE_DIR)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    rel = here[len(scratch_root) + 1:] if here.startswith(scratch_root + "/") else ""
    if here == scratch_root or not rel or "/" not in rel:
        sys.exit("--dir must be a sub-folder of a task folder inside tools/dev/scratch/ (e.g. tools/dev/scratch/<task>/skills0422; that folder is "
                 "deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0, "the stand-in classes were generated")
    outs = {}
    for mode, jar in (("prev", PREV_JAR), ("new", JAR)):
        outp = os.path.join(SCRATCH, "run-%s.json" % mode)
        logp = os.path.join(SCRATCH, "run-%s.log" % mode)
        with open(logp, "wb") as lf:
            p = subprocess.run([sys.executable, me, "--child", jar, "--out", outp, "--mode", mode, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
        check(p.returncode == 0 and os.path.isfile(outp), "child JVM (%s) ran (log %s)" % (mode, logp))
        if os.path.isfile(outp):
            outs[mode] = json.load(open(outp))
    wo = os.path.join(SCRATCH, "wiring.json")
    pw = subprocess.run([sys.executable, me, "--wiring", JAR, "--out", wo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pw.returncode == 0 and os.path.isfile(wo), "wiring child ran: %s" % pw.stderr[-500:])
    cmpo = os.path.join(SCRATCH, "compare.json")
    pc = subprocess.run([sys.executable, me, "--compare", JAR, "--prevjar", PREV_JAR, "--out", cmpo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pc.returncode == 0 and os.path.isfile(cmpo), "class compare child ran: %s" % pc.stderr[-500:])
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    h21 = None
    if "--no21" not in sys.argv:
        h21 = {}
        for tag, jj in (("new", JAR), ("ctl", PREV_JAR)):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyskills_0.4.21.py"), "--jar", jj, "--prev",
                                 os.path.join(HERE, "SkyySkills-0.4.20.jar"), "--dir", os.path.join(SCRATCH, "h21-" + tag), "--live", LIVE_DIR],
                                env=env, capture_output=True)
            h21[tag] = ph.stdout.decode("utf-8", "replace")
    if FAILS:
        return finish()
    for mode in ("new", "prev"):
        r = outs[mode]
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A (%s): %d / %d classes load under -Xverify:all %s" % (mode, r["loaded"], r["classes"], r["load_fails"][:3]))
    if FAILS:
        return finish()
    N, P = outs["new"]["data"]["B"], outs["prev"]["data"]["B"]
    print("A. both jars: every class loads under -Xverify:all (%d / %d classes)" % (outs["new"]["loaded"], outs["prev"]["loaded"]))
    # ---------------------------------------------------------------- B
    check(N["none"] is False and N["future"] is True and N["edge"] is True and N["past"] is False and N["string"] is False and N["null_u"] is False,
          "B: Acro.monkMove - no key / a Long in the past / not a Long / no player = off; a Long now or later = on: %s" % N)
    check(N["on"] == [0.0, 0.0] and P["on"][0] > 0.0 and P["on"][1] > 0.0 and N["off_fall"] == [True, 12.5] and N["off_roll"] == [True, 7.5]
          and P["off_fall"] == N["off_fall"] and P["off_roll"] == N["off_roll"],
          "B: with the flag on, noteFall + noteRoll note NOTHING (0.4.21 noted both: the Monk landing XP probe M11 saw); without it both note as "
          "before (12.5 / 7.5): %s | 0.4.21 %s" % ([N["on"], N["off_fall"], N["off_roll"]], [P["on"], P["off_fall"], P["off_roll"]]))
    an, ap = N["air"], P["air"]
    check(an["on"][0] is None and an["on"][1] == 1.0 and an["off"][0] is not None and ap["on"][0] is not None and ap["off"][0] is not None,
          "B: airJump with the flag on returns right after airTrack (the crouch edge IS tracked: 1.0) - no engine call; without the flag it goes on "
          "to the engine (the null buffer throws = it would push), as 0.4.21 always did: %s | 0.4.21 %s" % (an, ap))
    check(N["move"]["monk"] == 0.0 and N["move"]["plain"] > 0.0 and P["move"] == N["move"],
          "B: Acro.move with creative = true (what AcroSys.tick passes during a Monk move) adds no run / jump XP; false pays as before: %s" % N["move"])
    print("B. flag: monkMove on / off / edge / bad value; noteFall + noteRoll silent while on; airJump stops after tracking; move pays nothing as creative")
    # ---------------------------------------------------------------- W
    W = json.load(open(wo))
    tk = W["tick"]
    i_mm = [i for i, x in enumerate(tk) if x == "monkMove"]
    i_cr = [i for i, x in enumerate(tk) if x == "creative"]
    check(len(i_mm) == 1 and len(i_cr) == 1 and i_cr[0] < i_mm[0] and tk.index("move") > i_mm[0] and tk.index("dodge") > i_mm[0] and tk.index("falls") > i_mm[0],
          "W: AcroSys.tick asks SkillXp.creative, THEN Acro.monkMove (creative || monkMove), before Acro.move / dodge / falls: %s" % tk[:30])
    air = W["air"]
    check(air.index("airTrack") < air.index("monkMove") < air.index("getComponent") and W["fall"][0] == "currentTimeMillis" and W["fall"][1] == "monkMove"
          and W["roll"][0] == "currentTimeMillis" and W["roll"][1] == "monkMove",
          "W: airJump asks monkMove right after airTrack (before any component read); noteFall / noteRoll ask it first: %s %s %s" % (air[:6], W["fall"][:3], W["roll"][:3]))
    # ---------------------------------------------------------------- J
    jz, jp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
    nn, pn = set(jz.namelist()), set(jp.namelist())
    other = sorted(n for n in nn & pn if not n.endswith(".class") and n != "manifest.json" and jz.read(n) != jp.read(n))
    check(sorted(pn - nn) == BO and not (nn - pn) and other == [] and sorted(n for n in nn if "Weapon_Staff_Bo_" in n) == [],
          "J: the 0.4.22 jar = 0.4.21's files minus exactly the 2 vanilla Bo item overrides; every other non-class file byte-identical: gone %s new %s "
          "changed %s" % (sorted(pn - nn), sorted(nn - pn), other[:3]))
    # ---------------------------------------------------------------- H21
    if h21 is not None:
        def fails_of(txt):
            return [ln.strip()[len("FAILED: "):] for ln in txt.splitlines() if ln.strip().startswith("FAILED: ")]
        fn_, fc_ = fails_of(h21["new"]), fails_of(h21["ctl"])
        ctl_keys = set(f[:60] for f in fc_)
        expected = ("DEF21: the 0.4.21 default xp.properties = 0.4.20's except the version header line",
                    "F: 0.4.20 -> 0.4.21 differs only in the planned methods / fields", "H20: the 0.4.20 harness on the 0.4.21 jar fails nothing",
                    "F: every asset file byte-identical")
        other = [f for f in fn_ if f[:60] not in ctl_keys and not f.startswith(expected)]
        assets = [f for f in fn_ if f.startswith(expected[3])]
        defs = [f for f in fn_ if f.startswith(expected[0])]
        mn = (list(re.finditer(r"(?m)^(\d+) checks passed, (\d+) failed", h21["new"])) or [None])[-1]          # its OWN summary line (not a quoted one)
        mc_ = (list(re.finditer(r"(?m)^(\d+) checks passed, (\d+) failed", h21["ctl"])) or [None])[-1]
        check(mn is not None and mc_ is not None and other == [] and int(mn.group(1)) > 30 and int(mc_.group(2)) == 0
              and all(("Weapon_Staff_Bo_Bamboo.json" in f and "Weapon_Staff_Bo_Wood.json" in f and f.count(".json") == 2) for f in assets)
              and all(("0.4.22" in f) for f in defs),
              "H21: the 0.4.21 harness on the 0.4.22 jar fails nothing it does not also fail on the 0.4.21 jar beyond the version-shape checks (its "
              "default-file header, its class compare, its asset compare = only the 2 Bo files, its nested H20 for the same): %s | new %s, control %s"
              % (other[:3], mn.group(0) if mn else h21["new"][-800:], mc_.group(0) if mc_ else h21["ctl"][-800:]))
        print("H21. 0.4.21 harness: on the 0.4.22 jar %s, on the 0.4.21 jar %s; extra on 0.4.22 = %s" % (
            mn.group(0) if mn else "?", mc_.group(0) if mc_ else "?", [f[:70] for f in fn_ if f[:60] not in ctl_keys]))
        hm = [ln for ln in h21["new"].splitlines() if ln.startswith(("X. saved XP", "H20.", "DEF21."))]
        print("H21. evidence (nested start-twice / saved XP lines): %s" % hm[:3])
    # ---------------------------------------------------------------- F
    cmpd = json.load(open(cmpo))
    plan = {"Acro": {"methods": ["monkMove(Ljava/util/UUID;J)Z", "noteFall(Ljava/util/UUID;F)V", "noteRoll(Ljava/util/UUID;F)V",
                                 "airJump([DLcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;"
                                 "Lcom/hypixel/hytale/server/core/universe/PlayerRef;Ljava/util/UUID;Lcom/hypixel/hytale/protocol/MovementStates;J)V"], "fields": []},
            "AcroSys": {"methods": ["tick(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"],
                        "fields": []}}
    bad = {}
    for c, v in cmpd.items():
        if isinstance(v, str):
            bad[c] = v
        elif c in plan:
            if sorted(v["methods"]) != sorted(plan[c]["methods"]) or sorted(v["fields"]) != sorted(plan[c]["fields"]):
                bad[c] = v
        elif c.endswith("Plugin") and not v["fields"] and all(m.startswith("setup") for m in v["methods"]):
            continue
        elif c == "ManaGuard" and v == {"methods": ["packTick()V"], "fields": []}:
            continue          # packTick inlines ManaCost.N (the item overrides: 24 -> 22, the 2 Bo staffs) - bytecode 'bipush 24' -> 'bipush 22' only
        else:
            bad[c] = v
    print("F. compare 0.4.21 -> 0.4.22: %s" % json.dumps(cmpd)[:3000])
    check(not bad, "F: 0.4.21 -> 0.4.22 differs only in the planned methods (Acro monkMove / noteFall / noteRoll / airJump, AcroSys.tick, the "
                   "plugin's ready line, ManaGuard.packTick's inlined override count 24 -> 22): %s" % json.dumps(bad)[:1500])
    # ---------------------------------------------------------------- AU
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references in %d classes, refused %s; control refused: %s" % (
        au["refs"], au["classes"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references, %d refused (control refused: %s)" % (au["refs"], len(au["refused"]), bool(au["control"])))
    live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    check(live_after == live_snap, "the live Skyy_SkyySkills folder was never written")
    return finish()


def finish():
    if not KEEP and GUARD_OK[0]:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
