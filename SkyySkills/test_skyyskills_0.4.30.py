"""SkyySkills 0.4.30 - bare-JVM harness for THE REGEN BLOCK BRIDGE (tools/skills_0_4_30_patch.py; SkyyArmory 0.1.19's Soul Orb - Skyy LOCKED
2026-10-04 "no natural Mana regen while any Binding is active - but Mana Steal still works").
Every child JVM runs the game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP /
java.io.tmpdir in the scratch folder. Live save data is only ever READ and copied into scratch (checked: the live files are unchanged).

    python SkyySkills/test_skyyskills_0.4.30.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyySkills-0.4.30.jar] [--prev SkyySkills-0.4.29.jar] [--live <Skyy_SkyySkills folder>]

SECTIONS
  A   every class of the new jar loads, verifies (-Xverify:all) and initialises
  RB  skill:fn:regenblock EXECUTED (the real RegenBlockFn): { UUID, Long until } = TRUE + the block (capped 10 s ahead), { UUID, 0 } / a past
      time = cleared, UUID / { UUID } = the ms left (0 none), bad arguments = null; ManaRegen.block / blockLeft (expiry drops the entry)
  RT  the REAL ManaRegen.tick (the 0.4.13 stand-ins: a real TimeResource, real RegeneratingValue with vanilla's Mana entry - Alive,
      NoDamageTaken 6 s, Charging inverse -, a real DamageDataComponent; FakeStatMap2 records add AND subtract), one 0.2 s pulse per case,
      Mana Regen +20 %, in-combat 75 %: out of combat / charging out of combat / in combat / dead - UNBLOCKED = 0.4.29's exact refill (the
      0.4.29 jar run the same way = the control), BLOCKED = nothing added, vanilla's own refill of the pulse taken back where vanilla ran it
      (out of combat: 1.0; charging / in combat / dead: vanilla ran nothing = nothing taken), at most the Mana there is (0.5 -> 0.5); the
      combat state (skill:fn:combat) still recorded while blocked; the block expiring = the refill back on the next pulse; retainOnline
      prunes BLOCK
  CC  CLASS COMPARE 0.4.29 -> 0.4.30: only ManaRegen (block, blockLeft, tick, the new fields), Acro.retainOnline, the plugin's setup +
      shutdown differ; one class added (RegenBlockFn)
  ST  START TWICE on a scratch COPY of the live Skyy_SkyySkills (the 0.4.25 harness's start routine), both jars: 0.4.30 changes exactly what
      0.4.29 changes; start 2 changes nothing; player files untouched
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.30", "0.4.29"
PKG = "com.skyy.skills."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0430", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
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


# ============================================================================================ child: the stand-ins (+ FakeStatMap2)
def run_mkfake(out_dir):
    t15().run_mkfake(out_dir)          # starts the JVM (javassist on the class path)
    from jpype import JClass
    import skyybuild as B
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(out_dir)
    CtField, CtNewMethod = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    sm = cp.makeClass("skyytest.FakeStatMap2", cp.get("skyytest.FakeStatMap"))          # + subtractStatValue recorded (0.4.30's take-back)
    for decl in ("int subCalls", "float subtracted", "float subLast"):
        sm.addField(CtField.make("public %s;" % decl, sm))
    sm.addMethod(CtNewMethod.make("""public float subtractStatValue(int i, float a) {
  this.subCalls = this.subCalls + 1;
  this.subtracted = this.subtracted + a;
  this.subLast = a;
  return a;
}""", sm))
    sm.writeFile(out_dir)


# ============================================================================================ child: A + RB + RT (one jar)
def run_regen(jar, fake, out, new):
    from jpype import JClass, JFloat, JArray, JLong, JObject
    T = t15()
    res, path = T.common(jar, [fake])
    R = {"loaded": res["loaded"], "classes": res["classes"], "load_fails": res["load_fails"]}
    D = {}
    try:
        E = T.regen_env()
        Mana = JClass(PKG + "ManaRegen")
        UUID, Sys, ChronoUnit = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.time.temporal.ChronoUnit")
        Instant, setf, ESV, ESM, RGV = E["Instant"], E["setf"], E["ESV"], E["ESM"], E["RGV"]
        tr, store, cb, mv, dd2, U = E["tr"], E["store"], E["cb"], E["mv"], E["dd2"], E["U"]
        fsm = U.allocateInstance(JClass("skyytest.FakeStatMap2").class_)
        setf(fsm, ESM, "values", JArray(ESV)([mv]))
        cb.stats = fsm
        u = UUID(0x430, 1)
        other = UUID(0x430, 2)
        Mana.CLK.clear()
        Mana.SRC.clear()
        Mana.put(u, "Test", 20.0)
        store.ext = None
        cb.arch = E["Arch"].empty()
        dd2.setLastDamageTime(Instant.MIN)
        E["charging"].v = True
        setf(mv, ESV, "value", JFloat(10.0))
        setf(mv, ESV, "max", JFloat(1000.0))
        dt = JFloat(0.2)
        nanos = JLong(200000000)
        D["in_combat_pct"] = int(Mana.IN_COMBAT)

        def wall():
            return int(Sys.currentTimeMillis())

        def blk(until):
            if not new:
                return None
            f = JClass(PKG + "RegenBlockFn")()
            r = f.apply(JArray(JObject)([u, JLong(until)]))
            return None if r is None else bool(r)

        def pulse(tag, block, charging=False, combat=False, dead=False, mana=10.0):
            setf(mv, ESV, "value", JFloat(mana))
            E["charging"].v = not charging
            cb.arch = E["Arch"].of(E["deathType"]) if dead else E["Arch"].empty()
            tr.add(nanos, ChronoUnit.NANOS)
            dd2.setLastDamageTime(tr.getNow() if combat else Instant.MIN)
            if block:
                blk(wall() + 5000)
            else:
                blk(0)
            a0, s0 = int(fsm.calls), int(fsm.subCalls)
            b0 = int(getattr(Mana, "BLOCKED", 0)) if new else 0
            Mana.tick(u, store, cb, None, dt)
            D[tag] = {"added": round(float(fsm.last), 5) if int(fsm.calls) != a0 else None,
                      "taken": round(float(fsm.subLast), 5) if int(fsm.subCalls) != s0 else None,
                      "blocked_pulse": (int(Mana.BLOCKED) - b0) if new else None,
                      "combat_ms": int(Mana.combatNow(u, wall()))}
        for tag, kw in (("out", {}), ("charging", {"charging": True}), ("combat", {"combat": True}), ("dead", {"dead": True})):
            pulse(tag, False, **kw)
            pulse(tag + "_blocked", True, **kw)
        pulse("low_blocked", True, mana=0.5)
        pulse("after_unblock", False)
        D["warn"] = bool(Mana.FAILED_ONCE)
        if new:
            RB = JClass(PKG + "RegenBlockFn")()
            now = wall()
            rb = {}
            rb["set"] = bool(RB.apply(JArray(JObject)([u, JLong(now + 3000)])))
            rb["left_uuid"] = int(RB.apply(u))
            rb["left_arr"] = int(RB.apply(JArray(JObject)([u])))
            rb["clear"] = bool(RB.apply(JArray(JObject)([u, JLong(0)])))
            rb["left_after_clear"] = int(RB.apply(u))
            rb["past"] = (bool(RB.apply(JArray(JObject)([u, JLong(now + 3000)]))), bool(RB.apply(JArray(JObject)([u, JLong(now - 5)]))), int(RB.apply(u)))
            rb["capped"] = (bool(RB.apply(JArray(JObject)([u, JLong(now + 60000)]))), int(RB.apply(u)))
            rb["unknown"] = int(RB.apply(other))
            rb["bad"] = [RB.apply(x) for x in (None, "x", JArray(JObject)([]), JArray(JObject)(["u", JLong(1)]), JArray(JObject)([u, "soon"]))]
            Mana.block(u, JLong(now + 30), JLong(now))
            rb["expiry"] = (int(Mana.blockLeft(u, JLong(now))), int(Mana.blockLeft(u, JLong(now + 31))), Mana.BLOCK.containsKey(u))
            Mana.block(u, JLong(now + 4000), JLong(now))
            Mana.block(other, JLong(now + 4000), JLong(now))
            rb["map"] = sorted(str(k) for k in Mana.BLOCK.keySet())
            # Acro.retainOnline: the Universe with nobody online drops every block (the real method, a stand-in Universe)
            Universe, CHM = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("java.util.concurrent.ConcurrentHashMap")
            uni = U.allocateInstance(Universe.class_)
            players = CHM()
            setf(uni, Universe, "playersByUuid", players)
            setf(uni, Universe, "players", players.values())
            setf(None, Universe, "instance", uni)
            JClass(PKG + "Acro").retainOnline()
            rb["after_retain"] = sorted(str(k) for k in Mana.BLOCK.keySet())
            rb["taken_back"] = round(float(Mana.TAKEN_BACK), 5)
            D["RB"] = rb
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
        return run_mkfake(arg("--mkfake"))
    if "--regen" in sys.argv:
        return run_regen(arg("--regen"), arg("--fake"), arg("--out"), arg("--tag") == "new")
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
    check(child(env, os.path.join(SCRATCH, "mkfake.log"), "--mkfake", fake) == 0, "stand-in classes generated (+ FakeStatMap2)")
    # ---------------------------------------------------------------- A + RB + RT (new) and the control (0.4.29)
    res = {}
    for tag, jar in (("new", JAR), ("prev", PREV_JAR)):
        out = os.path.join(SCRATCH, "regen-%s.json" % tag)
        log = os.path.join(SCRATCH, "regen-%s.log" % tag)
        rc = child(env, log, "--regen", jar, "--fake", fake, "--out", out, "--tag", tag)
        check(rc == 0 and os.path.isfile(out), "RT %s: child JVM ran (log %s)" % (tag, log))
        res[tag] = json.load(open(out)) if os.path.isfile(out) else {"D": {"error": "no output"}}
    N, P = res["new"], res["prev"]
    check(not N.get("load_fails") and N.get("loaded") == N.get("classes") and N.get("classes", 0) > 100,
          "A: %s / %s classes load + verify + initialise under -Xverify:all %s" % (N.get("loaded"), N.get("classes"), (N.get("load_fails") or [])[:3]))
    D, C = N["D"], P["D"]
    check("error" not in D and "error" not in C, "RT ran: %s %s" % (D.get("error"), C.get("error")))
    if "error" in D or "error" in C:
        return finish()
    near = lambda a, b: a is not None and b is not None and abs(a - b) < 1e-4
    # unblocked = 0.4.29 exactly; the expected numbers (vanilla 5 / s, +20 %, in combat 75 %, one 0.2 s pulse)
    check(D["in_combat_pct"] == 75 and near(D["out"]["added"], 0.2) and D["out"]["taken"] is None and near(D["charging"]["added"], 1.2)
          and near(D["combat"]["added"], 0.9) and D["dead"]["added"] is None
          and all(D[t]["added"] == C[t]["added"] and D[t]["taken"] is None for t in ("out", "charging", "combat", "dead")),
          "RT UNBLOCKED (= 0.4.29): out of combat +0.2 (the +20 %% boost on vanilla's 5 / s), charging out of combat +1.2 (what vanilla withholds "
          "+ the boost, 0.4.13), in combat +0.9 (75 %% of 6 / s), dead nothing - the same floats on the 0.4.29 jar: %s | %s" % (
              dict((t, D[t]) for t in ("out", "charging", "combat", "dead")), dict((t, C[t]) for t in ("out", "charging", "combat", "dead"))))
    check(D["out_blocked"]["added"] is None and near(D["out_blocked"]["taken"], 1.0) and D["charging_blocked"]["added"] is None
          and D["charging_blocked"]["taken"] is None and D["combat_blocked"]["added"] is None and D["combat_blocked"]["taken"] is None
          and D["dead_blocked"]["added"] is None and D["dead_blocked"]["taken"] is None and near(D["low_blocked"]["taken"], 0.5)
          and all(D[t]["blocked_pulse"] == 1 for t in ("out_blocked", "charging_blocked", "combat_blocked", "dead_blocked", "low_blocked"))
          and D["combat_blocked"]["combat_ms"] > 0 and near(D["after_unblock"]["added"], 0.2) and D["after_unblock"]["blocked_pulse"] == 0 and not D["warn"],
          "RT BLOCKED (skill:fn:regenblock, Skyy: no natural Mana regen while bound): NOTHING added out of combat / charging / in combat / dead; "
          "vanilla's own refill of the pulse taken back where vanilla ran it (out of combat 1.0 = 5 / s x 0.2; charging, in combat, dead: vanilla "
          "ran nothing = nothing taken), never more than the Mana there (0.5); the combat state still recorded while blocked; cleared = the refill "
          "back at once; no failure logged: %s" % dict((t, D[t]) for t in ("out_blocked", "charging_blocked", "combat_blocked", "dead_blocked",
                                                                            "low_blocked", "after_unblock")))
    check(all(C[t]["added"] == C[t[:-len("_blocked")]]["added"] for t in ("out_blocked", "charging_blocked", "combat_blocked")),
          "RT control 0.4.29: no block exists - the 'blocked' pulses refill like the unblocked ones (the Soul Orb then binds with SkyySkills' regen on)")
    rb = D["RB"]
    check(rb["set"] is True and 2900 <= rb["left_uuid"] <= 3000 and 2900 <= rb["left_arr"] <= 3000 and rb["clear"] is True and rb["left_after_clear"] == 0
          and rb["past"][0] is True and rb["past"][1] is True and rb["past"][2] == 0 and rb["capped"][0] is True and 9900 <= rb["capped"][1] <= 10000
          and rb["unknown"] == 0 and rb["bad"] == [None] * 5 and tuple(rb["expiry"]) == (30, 0, False)
          and rb["map"] == sorted(["00000000-0000-0430-0000-000000000001", "00000000-0000-0430-0000-000000000002"]) and rb["after_retain"] == []
          and rb["taken_back"] >= 1.5,
          "RB skill:fn:regenblock (the real RegenBlockFn): {UUID, until} = TRUE + blocked (3 s left), UUID / {UUID} = ms left, {UUID, 0} and a past "
          "time = cleared, 60 s asked = capped at 10 s, an unknown player 0, bad arguments null; ManaRegen.blockLeft drops an expired block; "
          "Acro.retainOnline prunes the blocks of players who left: %s" % rb)
    print("RB/RT. regen block: unblocked = 0.4.29, blocked = nothing added + vanilla's pulse taken back, the bridge forms, expiry, prune")
    # ---------------------------------------------------------------- CC
    out = os.path.join(SCRATCH, "cc.json")
    repl = json.dumps({"versions": [VERSION, PREV_VERSION], "rules": []})
    check(child(env, os.path.join(SCRATCH, "cc.log"), "--cc", JAR, "--prev-jar", PREV_JAR, "--out", out, "--repl", repl) == 0, "CC child ran")
    CC = json.load(open(out))
    ch = CC["classes"]
    struct = dict((c, v["structural"]) for c, v in ch.items() if v["structural"] or v["fields_new"] or v["fields_gone"])
    check(CC["added"] == ["RegenBlockFn"] and CC["gone"] == [], "CC: one class added (RegenBlockFn), none removed: %s %s" % (CC["added"], CC["gone"]))
    mr = sorted(struct.get("ManaRegen", []))
    check(set(struct) == {"ManaRegen", "Acro", "SkyySkillsPlugin"}
          and any(m.startswith("block(") and m.endswith("(new)") for m in mr) and any(m.startswith("blockLeft(") and m.endswith("(new)") for m in mr)
          and any(m.startswith("tick(") for m in mr) and len(mr) == 4
          and sorted(ch["ManaRegen"]["fields_new"]) == sorted(["BLOCK:Ljava/util/concurrent/ConcurrentHashMap;", "BLOCK_MAX_MS:J", "BLOCKED:J", "TAKEN_BACK:D"])
          and [m.split("(")[0] for m in struct["Acro"]] == ["retainOnline"]
          and sorted(m.split("(")[0] for m in struct["SkyySkillsPlugin"]) == ["setup", "shutdown"],
          "CC: only ManaRegen (block + blockLeft new, tick, <clinit> + 4 fields), Acro.retainOnline and the plugin's setup / shutdown differ: %s"
          % json.dumps(struct)[:900])
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
          and a.get("xp1") == b.get("xp1"), "ST: start 1 changes what 0.4.29 changes %s, start 2 nothing, %s player files untouched"
          % (a.get("changed1"), a.get("players")))
    print("ST. start twice on a live copy: start 1 changed %s (= 0.4.29), start 2 nothing" % a.get("changed1"))
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
