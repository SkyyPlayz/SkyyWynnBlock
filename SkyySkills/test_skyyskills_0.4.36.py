"""SkyySkills 0.4.36 - harness for REBIRTH R3 (the participant rebirth:part:skills, level coins x rebirth.coinFactor ^ rebirths, the class-weapon
bonus at the table levels) - tools/skills_0_4_36_patch.py.
Build first: python tools/skills_0_4_36_patch.py && python SkyySkills/build_skyyskills_0.4.36.py

    python SkyySkills/test_skyyskills_0.4.36.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.35 -> 0.4.36: exactly the planned members differ; SkillRb added
  R3  rebirth  EXECUTED: the participant (every op, every refusal, the facts, backups kept 3, staged files, cleanStale with a stand-in
               rebirth:fn:decision, commit = deltas + paid markers 0 + Exploration kept + rb.lastTx in the same file, idempotent commit,
               FAIL_SAVE = err then done, a FRESH class loader (restart) reads rb.lastTx and answers done), rbN / rbCoins, payOwedK with
               a stand-in coins:fn:add at 0 / 2 rebirths / an unknown count (owed) / factor 0, rebirth.coinFactor read + clamped + in the
               fresh default file + a config row, StatsPage.lines (the coin line scaled, the class-weapon damage line at the table max),
               static: CombatDmgSys.handle clamps with SkillDefs.maxOf, gain4 shows rbCoins, the plugin publishes / removes
               rebirth:part:skills; levels above 100 stay out of Overall / class Mana / leaderboards (Overall.sums, ClassMana.amountFor
               and SkillTop use levelOf - the table levels)
  RB  r1       test_skyyskills_0.4.35.py's rebirth phase on the 0.4.36 jar (every R1 path still holds at 0 rebirths)
  R   route    test_skyyskills_0.4.34.py's route phase on the 0.4.36 jar
  X   exec     test_skyyskills_0.4.32.py's exec phase on the 0.4.36 jar
  D   live     test_skyyskills_0.4.35.py's live phase on the 0.4.36 jar (START TWICE on a scratch COPY of the live Skyy_SkyySkills) +
               every live player file: measure answers, nothing written; a save of a file without rb.lastTx writes no such line
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, time, importlib.util, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.36"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.35.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth3", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))

EXPECT = {
    "SkillStore": ["+f RBTX", "+m rbCoins", "+m rbN", "+m rbReset", "+m rbReset0", "~<clinit>", "~m install", "~m payLocked", "~m readFile", "~m snap"],
    "SkillCfg": ["+f RB_COIN", "~<clinit>", "~m load"],
    "SkillXp": ["~m gain4"],
    "StatsPage": ["~m lines"],
    "CombatDmgSys": ["~m handle"],
    "SkyySkillsPlugin": ["~m setup", "~m shutdown"],
    # version texts / the kit's rows + default file (rebirth.coinFactor)
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "CfgFile": ["~<clinit>"],
}
ADDED = ["SkillRb"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T35 = tmod("test_skyyskills_0.4.35.py", "t0435")
T32 = T35.T32


def fn_class():
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    return Fn


def props(path):
    out = {}
    if not os.path.exists(path):
        return None
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        a, b = ln.split("=", 1)
        out[a.strip()] = b.strip()
    return out


# ====================================================================================================== R3: the 0.4.36 paths
def run_r3(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Defs, Cfg, Sto, Cap, Rb, SP, Ovl = P("SkillDefs"), P("SkillCfg"), P("SkillStore"), P("SkillCap"), P("SkillRb"), P("StatsPage"), P("Overall")
    UUID, Long, Integer, Obj = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.Object")
    OA = lambda *xs: JArray(Obj)(list(xs))
    Fn = fn_class()
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    base = os.path.join(scratch, "r3", "Skyy_SkyySkills")
    pd = os.path.join(base, "players")
    os.makedirs(pd)
    Cfg.FILE = T32.path(os.path.join(base, "xp.properties"))
    Cfg.load()
    Sto.DIR = T32.path(pd)
    br = Sto.bridge()
    for k_ in list(br.keySet()):
        br.remove(k_)
    N = int(Defs.N)
    NAMES = [str(x) for x in Defs.NAMES]
    MIN, EXP, FOR, ACRO = int(Defs.MINING), int(Defs.EXPLORATION), int(Defs.FORAGING), int(Defs.ACROBATICS)
    arch = int(Defs.indexOf("archery"))

    # ---- rebirth.coinFactor: default, file line, clamps, the fresh default file, the kit row
    txt = open(os.path.join(base, "xp.properties"), encoding="latin-1").read()
    K.check(abs(float(Cfg.RB_COIN) - 0.9) < 1e-9 and "rebirth.coinFactor=0.9" in txt, "R3 rebirth.coinFactor: default 0.9, in the fresh default xp.properties")
    for line, want in (("rebirth.coinFactor=0.5", 0.5), ("rebirth.coinFactor=7", 1.0), ("rebirth.coinFactor=-2", 0.0), ("rebirth.coinFactor=abc", 0.9)):
        open(os.path.join(base, "xp.properties"), "w", encoding="latin-1").write(txt.replace("rebirth.coinFactor=0.9", line))
        Cfg.load()
        K.check(abs(float(Cfg.RB_COIN) - want) < 1e-9, "R3 %s -> %s (clamped 0-1, a bad number = 0.9)" % (line, want))
    open(os.path.join(base, "xp.properties"), "w", encoding="latin-1").write(txt)
    Cfg.load()
    P("CfgPub").start(T32.path(os.path.dirname(base)), Cfg.LOG)
    hdr = br.get("config:def:SkyySkills")
    rows = dict((str(rw[0]), [str(x) for x in rw]) for rw in hdr[7]) if hdr is not None else {}
    K.check(len(rows) == 230 and rows.get("rebirth.coinFactor", [""] * 5)[4] == "0.9", "R3 the Server Setup row rebirth.coinFactor (default 0.9; 230 rows)")
    P("CfgPub").shutdown()

    # ---- rbN / rbCoins
    K.eq(int(Sto.rbN("k")), 0, "R3 rbN without SkyyRebirth = 0")
    cnt = {"v": Integer(2)}
    br.put("rebirth:fn:count", Fn(lambda o: cnt["v"]))
    K.eq(int(Sto.rbN("k")), 2, "R3 rbN = rebirth:fn:count")
    cnt["v"] = None
    K.eq(int(Sto.rbN("k")), -1, "R3 rbN while SkyyRebirth still reads the file (null) = -1")
    cnt["v"] = Integer(-3)
    K.eq(int(Sto.rbN("k")), 0, "R3 rbN negative = 0")

    def boom(o):
        raise RuntimeError("x")
    br.put("rebirth:fn:count", Fn(boom))
    K.eq(int(Sto.rbN("k")), 0, "R3 rbN throwing = 0")
    K.check([int(Sto.rbCoins(1000, n)) for n in (0, 1, 2, 10)] == [1000, 900, 810, 349] and int(Sto.rbCoins(0, 3)) == 0 and int(Sto.rbCoins(-5, 3)) == -5,
            "R3 rbCoins: 0.9^n rounded (1000 -> 900 / 810 / 349)")
    Cfg.RB_COIN = 1.0
    K.eq(int(Sto.rbCoins(1000, 5)), 1000, "R3 rbCoins factor 1 = full")
    Cfg.RB_COIN = 0.0
    K.eq(int(Sto.rbCoins(1000, 1)), 0, "R3 rbCoins factor 0 = none")
    Cfg.RB_COIN = 0.9

    # ---- payOwedK with a stand-in coins:fn:add at 0 / 2 / unknown rebirths and factor 0
    paid = []

    def add(o):
        paid.append(int(o[1]))
        return Long(1)
    br.put("coins:fn:add", Fn(add))
    u1 = UUID.fromString("00000000-0000-4000-8000-0000000436a1")
    k1 = str(u1)
    cm = [int(x) for x in Defs.cumOf(FOR)]
    per = int(Cfg.COINS_PER_LEVEL)
    for n_, want_f in ((None, None), (0, 1.0), (2, 0.81)):
        d = Sto.dataK(k1, u1)
        Sto.wr(d, FOR, cm[3])
        Sto.wr(d, N + FOR, 0)
        del paid[:]
        if n_ is None:
            br.put("rebirth:fn:count", Fn(lambda o: None))
            r = Sto.payOwedK(k1, u1, FOR)
            K.check(r is None and not paid and int(d[N + FOR]) == 0, "R3 payOwedK while the rebirth count is unknown: nothing paid, levels stay owed")
            continue
        br.put("rebirth:fn:count", Fn(lambda o, n_=n_: Integer(n_)))
        r = Sto.payOwedK(k1, u1, FOR)
        want = [int(round(per * L * want_f)) for L in (1, 2, 3)]
        K.check(paid == want and int(d[N + FOR]) == 3 and r is not None and int(r[2]) == sum(want) and int(r[5]) == n_,
                "R3 payOwedK at %d rebirths: levels 1-3 pay %s (x%.2f), marker 3, res[5] = %d: %s" % (n_, want, want_f, n_, paid))
    Cfg.RB_COIN = 0.0
    Sto.wr(d, N + FOR, 0)
    del paid[:]
    r = Sto.payOwedK(k1, u1, FOR)
    K.check(not paid and int(d[N + FOR]) == 3, "R3 rebirth.coinFactor 0 after a rebirth: the levels count as paid, no coins")
    Cfg.RB_COIN = 0.9
    br.remove("rebirth:fn:count")

    # ---- fix round: a rebirth reset waits for a level-coin payout loop that is running (lock order: the data array, then SkillStore)
    import threading
    JLong = JClass("java.lang.Long")
    u2 = UUID.fromString("00000000-0000-4000-8000-0000000436a2")
    k2 = str(u2)
    d2 = Sto.dataK(k2, u2)
    Sto.wr(d2, FOR, cm[3])
    Sto.wr(d2, N + FOR, 0)
    br.put("rebirth:fn:count", Fn(lambda o: Integer(0)))
    prep2 = JArray(JClass("long"))([-1] * N)
    prep2[FOR] = cm[3]
    seen = {"alive": None, "res": None}
    th = {}

    def reset():
        seen["res"] = bool(Sto.rbReset(k2, d2, "tx1760000000777-abcdef", prep2))

    def add2(o):
        paid.append(int(o[1]))
        if "t" not in th:
            th["t"] = threading.Thread(target=reset)
            th["t"].start()
            time.sleep(0.4)
            seen["alive"] = th["t"].is_alive()
        return Long(1)
    br.put("coins:fn:add", Fn(add2))
    del paid[:]
    Sto.payOwedK(k2, u2, FOR)
    th["t"].join(10)
    K.check(seen["alive"] is True and seen["res"] is True and paid == [per * L for L in (1, 2, 3)] and int(d2[FOR]) == 0 and int(d2[N + FOR]) == 0,
            "FIX rbReset during a level-coin payout: waits for the loop (blocked %s), levels 1-3 paid ONCE %s, then XP 0 + marker 0 (%d / %d)"
            % (seen["alive"], paid, int(d2[FOR]), int(d2[N + FOR])))
    br.put("coins:fn:add", Fn(add))
    br.remove("rebirth:fn:count")

    # ---- StatsPage.lines: the coin line scaled; the class-weapon damage line at the table max
    br.put("rebirth:fn:count", Fn(lambda o: Integer(1)))
    ls = [str(x) for x in SP.lines(u1, FOR, 4, True)]
    want_c = "+%s coins when you reach level 5" % str(Defs.fmt(int(round(per * 5 * 0.9))))
    K.check(want_c in ls, "R3 Stats page next level coins x0.9 at 1 rebirth: %s in %s" % (want_c, ls))
    br.remove("rebirth:fn:count")
    amax = int(Defs.maxOf(arch))
    br.put("class:" + k1, "Archer")
    perk = P("PerkCfg")
    if bool(perk.ENABLED) and float(perk.DMG) > 0.0:
        at_max = [str(x) for x in SP.lines(u1, arch, amax, False)]
        above = [str(x) for x in SP.lines(u1, arch, amax + 10, False)]
        dline = [x for x in at_max if "damage with" in x]
        K.check(dline and dline == [x for x in above if "damage with" in x], "R3 Stats page: the class-weapon damage line at level %d = at %d (table levels only): %s" % (amax + 10, amax, dline))
        nxt = [str(x) for x in SP.lines(u1, arch, amax + 3, True)]
        K.check(not [x for x in nxt if "damage with" in x], "R3 Stats page: no '+ damage' next-level line above the table max")
    else:
        K.notes.append("R3 perk damage off in the default file - damage line not checked by execution")
    g = PW.calls(jar)
    cd = g.get("CombatDmgSys.handle", set())
    K.check(PKG + "SkillDefs.maxOf" in cd and "java.lang.Math.min" in cd, "R3 static: CombatDmgSys.handle clamps the class level with SkillDefs.maxOf (table levels only)")
    K.check(PKG + "SkillStore.rbCoins" in g.get("SkillXp.gain4", set()), "R3 static: gain4's level-up line shows rbCoins (what was paid)")
    K.check(PKG + "SkillDefs.levelOf" in g.get("Overall.sums", set()) and PKG + "SkillCap.level" not in g.get("Overall.sums", set())
            and PKG + "SkillDefs.levelOf" in g.get("ClassMana.amountFor", set()) and PKG + "SkillDefs.levelOf" in g.get("ClassPower.classLevel", set()),
            "R3 static (Skyy 'No'): Overall Level, Overall + class Mana use the TABLE levels (levelOf), never the rebirth caps")
    tops = [m for m in g if m.startswith("SkillTop.")]
    K.check(tops and not any(PKG + "SkillCap.level" in g[m] or PKG + "SkillCap.levelU" in g[m] for m in tops),
            "R3 static: the leaderboards (SkillTop) never use the capped level")
    su, sd = g.get("SkyySkillsPlugin.setup", set()), g.get("SkyySkillsPlugin.shutdown", set())
    K.check("java.util.Map.put" in su and "java.util.Map.remove" in sd, "R3 static: the plugin puts / removes its bridge keys")

    # ---- rb.lastTx in the profile file
    u2 = UUID.fromString("00000000-0000-4000-8000-0000000436b2")
    k2 = str(u2)
    open(os.path.join(pd, k2 + ".properties"), "w", encoding="latin-1").write("Mining=500\nrb.lastTx=tx1700000000000-abcdef\n")
    Sto.dataK(k2, u2)
    K.eq(str(Sto.RBTX.get(k2)), "tx1700000000000-abcdef", "R3 readFile + install: rb.lastTx loaded")
    Sto.saveNow(k2)
    K.eq(props(os.path.join(pd, k2 + ".properties")).get("rb.lastTx"), "tx1700000000000-abcdef", "R3 snap / save: rb.lastTx kept")
    Sto.saveNow(k1)
    K.check("rb.lastTx" not in open(os.path.join(pd, k1 + ".properties"), encoding="latin-1").read(), "R3 a profile that never rebirthed: no rb.lastTx line")

    # ---- the participant
    R = Rb()
    dec = {"v": "unknown"}
    br.put("rebirth:fn:decision", Fn(lambda o: dec["v"]))
    keymap = {}
    br.put("profile:fn:key", Fn(lambda o: keymap.get(str(o), str(o))))
    u = UUID.fromString("00000000-0000-4000-8000-0000000436c3")
    k = str(u)
    br.put("class:" + k, "Archer")
    ca = [int(x) for x in Defs.cumOf(arch)]
    seed = {NAMES[MIN]: 123456, NAMES[FOR]: 2222, NAMES[arch]: ca[-1] + 999, NAMES[EXP]: 4444, NAMES[ACRO]: 77}
    open(os.path.join(pd, k + ".properties"), "w", encoding="latin-1").write(
        "".join("%s=%d\n%s.paid=%d\n" % (a, b, a, 5) for a, b in seed.items()))
    TX1, TX0 = "tx1760000000001-a1b2c3", "tx1760000000000-000001"
    for bad, what in ((None, "null"), (OA("prepare"), "one element"), (OA("prepare", k, "nope"), "bad txid"), (OA("prepare", "../" + k, TX1), "bad key"),
                      (OA("fly", k, TX1), "unknown op"), (OA(Integer(1), k, TX1), "op not a String")):
        r = str(R.apply(bad))
        K.check(r.startswith("err:"), "R3 part refuses %s: %s" % (what, r))
    d0 = Sto.DIR
    Sto.DIR = None
    K.check(str(R.apply(OA("measure", k, TX1))).startswith("err:SkyySkills is not started"), "R3 part: not started = err")
    Sto.DIR = d0
    keymap[k] = k + "-p2"
    K.check(str(R.apply(OA("measure", k, TX1))).startswith("err:") , "R3 measure of a profile that is not the active one = err (the class arm needs it)")
    del keymap[k]
    m = str(R.apply(OA("measure", k, TX1)))
    f = dict(x.split("=", 1) for x in m[3:].split(";"))
    K.check(m.startswith("ok:") and f.get("x." + NAMES[MIN]) == "123456" and ("x." + NAMES[EXP]) not in f and f.get("x." + NAMES[ACRO]) == "77"
            and all(("x." + NAMES[s]) in f for s in range(N) if s != EXP) and "arm.fishing" not in f,
            "R3 measure: x.<every slot but Exploration> (Acrobatics too), no Fishing arm: %d facts" % len(f))
    acl = f.get("arm.class", "").split("/")
    K.check(len(acl) == 4 and int(acl[0]) == ca[-1] + 999 and int(acl[2]) == int(acl[3]) == amax and int(acl[1]) == ca[-1],
            "R3 measure: arm.class = run / to cap / level / cap at the max: %s" % f.get("arm.class"))
    K.check(not os.path.exists(os.path.join(base, "rebirth")) and not os.path.exists(os.path.join(base, "rebirth-backup")), "R3 measure writes nothing")
    # stale staged files: an older aborted txid is deleted; one the coordinator says was committed refuses
    os.makedirs(os.path.join(base, "rebirth"))
    stale = os.path.join(base, "rebirth", k + ".rb-" + TX0 + ".properties")
    other = os.path.join(base, "rebirth", k + "-p2.rb-" + TX0 + ".properties")
    open(stale, "w").write("tx=%s\n" % TX0)
    open(other, "w").write("tx=%s\n" % TX0)
    dec["v"] = "commit"
    K.check(str(R.apply(OA("prepare", k, TX1))).startswith("err:an older rebirth"), "R3 prepare refuses while an older txid of this profile is committed but unfinished")
    dec["v"] = "unknown"
    pr = str(R.apply(OA("prepare", k, TX1)))
    stg = os.path.join(base, "rebirth", k + ".rb-" + TX1 + ".properties")
    bk = os.path.join(base, "rebirth-backup", k, TX1, k + ".properties")
    K.check(pr == m and os.path.exists(stg) and not os.path.exists(stale) and os.path.exists(other) and os.path.exists(bk),
            "R3 prepare: staged + backup written, the stale staged file of THIS profile deleted (another profile's kept), facts = measure")
    K.eq(props(bk).get(NAMES[MIN]), "123456", "R3 backup = the profile data at prepare")
    live_before = hashlib.sha1(open(os.path.join(pd, k + ".properties"), "rb").read()).hexdigest()
    # XP that lands after prepare (the coordinator's window) is kept by the delta
    Sto.addK(k, u, "T", MIN, 500)
    Sto.addK(k, u, "T", EXP, 50)
    Sto.saveNow(k)
    K.eq(str(R.apply(OA("status", k, TX1))), "staged", "R3 status: staged")
    K.check(str(R.apply(OA("commit", k, "tx1760000000009-ffffff"))).startswith("err:no staged file"), "R3 commit without a staged file = err")
    # a broken staged file = err, nothing applied
    good = open(stg, encoding="latin-1").read()
    open(stg, "w", encoding="latin-1").write(good.replace("x." + NAMES[FOR] + "=2222", "x." + NAMES[FOR] + "=abc"))
    K.check(str(R.apply(OA("commit", k, TX1))).startswith("err:bad x."), "R3 commit with a bad staged number = err")
    open(stg, "w", encoding="latin-1").write("\n".join(l for l in good.splitlines() if not l.startswith("x." + NAMES[FOR] + "=")) + "\n")
    K.check(str(R.apply(OA("commit", k, TX1))).startswith("err:the staged file has no"), "R3 commit with a missing staged slot = err")
    K.check(Sto.RBTX.get(k) is None and int(Sto.dataK(k, u)[MIN]) == 123956, "R3 a refused commit changed nothing")
    open(stg, "w", encoding="latin-1").write(good)
    Rb.FAIL_SAVE = 1
    r1 = str(R.apply(OA("commit", k, TX1)))
    d = Sto.dataK(k, u)
    K.check(r1.startswith("err:could not save") and str(Sto.RBTX.get(k)) == TX1 and int(d[MIN]) == 500 and os.path.exists(stg)
            and "rb.lastTx" not in open(os.path.join(pd, k + ".properties"), encoding="latin-1").read(),
            "R3 commit whose save fails: err (the reset in memory, the file still old, the staged file kept): %s" % r1)
    r2 = str(R.apply(OA("commit", k, TX1)))
    pf = props(os.path.join(pd, k + ".properties"))
    K.check(r2 == "done" and not os.path.exists(stg) and pf.get("rb.lastTx") == TX1, "R3 the retried commit: done, saved with rb.lastTx, staged deleted: %s" % r2)
    want = {NAMES[MIN]: 500, NAMES[FOR]: 0, NAMES[arch]: 0, NAMES[ACRO]: 0, NAMES[EXP]: 4494}
    got = dict((a, int(pf.get(a, "0"))) for a in want)
    K.check(got == want and all(int(pf.get(NAMES[s] + ".paid", "-1")) == 0 for s in range(N) if s != EXP) and int(pf.get(NAMES[EXP] + ".paid")) == 5,
            "R3 commit: every reset slot = XP gained since prepare (Mining 500), paid markers 0; Exploration kept (4444 + 50, paid 5): %s" % got)
    K.check(int(Sto.TOPIDX.get(k)[1][MIN]) == 500, "R3 commit: the leaderboard index follows")
    K.check(str(R.apply(OA("commit", k, TX1))) == "done" and int(Sto.dataK(k, u)[MIN]) == 500, "R3 commit again = done, nothing twice")
    K.check(str(R.apply(OA("abort", k, TX1))).startswith("err:already committed") and str(R.apply(OA("prepare", k, TX1))).startswith("err:already committed"),
            "R3 abort / prepare of a committed txid = err")
    K.eq(str(R.apply(OA("status", k, TX1))), "committed", "R3 status: committed")
    K.eq(str(R.apply(OA("status", k, "tx1760000000002-a1b2c3"))), "none", "R3 status: none")
    # abort of a staged txid
    TX2 = "tx1760000000003-a1b2c3"
    K.check(str(R.apply(OA("prepare", k, TX2))).startswith("ok:"), "R3 prepare #2")
    s2 = os.path.join(base, "rebirth", k + ".rb-" + TX2 + ".properties")
    K.check(os.path.exists(s2) and str(R.apply(OA("abort", k, TX2))) == "done" and not os.path.exists(s2), "R3 abort deletes the staged file")
    K.eq(str(R.apply(OA("abort", k, TX2))), "done", "R3 abort again = done")
    open(s2 + ".tmp", "w").write("torn")
    K.check(str(R.apply(OA("abort", k, TX2))) == "done" and not os.path.exists(s2 + ".tmp"), "R3 abort also deletes a staged write torn by a crash (.tmp)")
    old_tmp = os.path.join(base, "rebirth", k + ".rb-tx1750000000000-000001.properties.tmp")
    open(old_tmp, "w").write("torn")
    R.apply(OA("prepare", k, "tx1760000000003-a1b2c4"))
    K.check(not os.path.exists(old_tmp), "R3 prepare cleans an older torn staged write (.tmp) of the profile")
    R.apply(OA("abort", k, "tx1760000000003-a1b2c4"))
    # backups: the last 3 kept
    for i in range(4, 8):
        R.apply(OA("prepare", k, "tx176000000000%d-a1b2c3" % i))
    bdirs = sorted(os.listdir(os.path.join(base, "rebirth-backup", k)))
    K.check(len(bdirs) == 3 and bdirs[-1] == "tx1760000000007-a1b2c3", "R3 backups: the last 3 per profile kept: %s" % bdirs)
    K.check(int(Rb.APPLIED.get()) == 0, "R3 APPLIED counts the first commit only once it is on disk (FAIL_SAVE path = 0 applied, done path no count)")
    K.notes.append("R3 participant facts: %s" % m[:160])
    K.save()


# a FRESH class loader = a restart: rb.lastTx read from the file, a repeated commit answers done
def run_restart(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    base = os.path.join(scratch, "rs", "Skyy_SkyySkills")
    pd = os.path.join(base, "players")
    os.makedirs(pd)
    k = "00000000-0000-4000-8000-0000000436d4"
    TX = "tx1760000000001-a1b2c3"
    seen = []
    for rnd in range(3):
        L = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())
        C = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto, Rb = C("SkillCfg"), C("SkillStore"), C("SkillRb")
        Sto.BRIDGE = None
        br = Sto.bridge()
        for k_ in list(br.keySet()):
            br.remove(k_)
        Cfg.FILE = T32.path(os.path.join(base, "xp.properties"))
        Cfg.load()
        Sto.DIR = T32.path(pd)
        Obj = JClass("java.lang.Object")
        R = Rb()
        if rnd == 0:
            open(os.path.join(pd, k + ".properties"), "w", encoding="latin-1").write("Mining=9000\nForaging=10\n")
            Fn = fn_class()
            br.put("class:" + k, "Archer")
            r = str(R.apply(JArray(Obj)(["prepare", k, TX])))
            seen.append(r[:3])
            r = str(R.apply(JArray(Obj)(["commit", k, TX])))
            seen.append(r)
        else:
            r = str(R.apply(JArray(Obj)(["commit", k, TX])))
            seen.append(r)
            K.check(str(Sto.RBTX.get(k)) == TX, "RS restart %d: rb.lastTx read from the file" % rnd)
        p = props(os.path.join(pd, k + ".properties"))
        K.check(p.get("Mining") == "0" and p.get("rb.lastTx") == TX, "RS restart %d: the file holds the reset once" % rnd)
    K.eq(seen, ["ok:", "ok", "done", "done"], "RS prepare + commit, then a commit after each restart = done")
    K.save()


def run_r1(out, jar, scratch, home):
    return T35.run_rebirth(out, jar, scratch, home)


def run_route(out, jar, scratch, home):
    return T35.run_route(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    # the 0.4.32 exec phase; ONE of its static checks lists every caller of SkillStore.save - 0.4.36 adds SkillRb.saveIt on purpose (the
    # rebirth commit writes the reset at once): that single expected difference is checked here instead of failing
    import json
    tmp = os.path.join(scratch, "exec32.json")
    T35.run_exec(tmp, jar, scratch, home)
    d = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.notes = d["ok"], d["notes"]
    want = "got ['ClassCurve.flush', 'OwnCurve.deliver', 'OwnCurve.flush', 'SkillRb.saveIt', 'SkillStore.flushDirty'], want ['ClassCurve.flush', 'OwnCurve.deliver', 'OwnCurve.flush', 'SkillStore.flushDirty']"
    for f in d["fails"]:
        if f.startswith("X static: SkillStore.save only from") and want in f:
            K.ok += 1
            K.notes.append("X: the only new SkillStore.save caller is SkillRb.saveIt (the rebirth commit) - expected")
        else:
            K.fails.append(f)
    K.save()


def run_live(out, jar, scratch, home):
    import json
    T35.run_live(os.path.join(scratch, "live35.json"), jar, scratch, home)
    from jpype import JClass, JArray
    K = HK.Child(out)
    prev = json.load(open(os.path.join(scratch, "live35.json")))
    K.ok += prev["ok"]
    K.fails += prev["fails"]
    K.notes += prev["notes"]
    L = T32.loader_for(jar)
    Jc = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Rb = Jc("SkillCfg"), Jc("SkillStore"), Jc("SkillRb")
    lc = os.path.join(os.path.dirname(home), "copy36")
    import shutil
    shutil.copytree(home, lc)
    before = dict((fn, hashlib.sha1(open(os.path.join(r, fn), "rb").read()).hexdigest()) for r, _d, fs in os.walk(lc) for fn in fs)
    Cfg.FILE = T32.path(os.path.join(lc, "xp.properties"))
    Cfg.load()
    Sto.DIR = T32.path(os.path.join(lc, "players"))
    R = Rb()
    Obj = JClass("java.lang.Object")
    n, oks = 0, 0
    for fn in sorted(os.listdir(os.path.join(lc, "players"))):
        if not fn.endswith(".properties"):
            continue
        kk = fn[:-11]
        r = str(R.apply(JArray(Obj)(["measure", kk, "tx1760000000001-a1b2c3"])))
        n += 1
        oks += 1 if (r.startswith("ok:") or r.startswith("err:")) else 0
    after = dict((fn, hashlib.sha1(open(os.path.join(r, fn), "rb").read()).hexdigest()) for r, _d, fs in os.walk(lc) for fn in fs)
    K.check(n > 0 and oks == n and before == after and not os.path.exists(os.path.join(lc, "rebirth")),
            "D 0.4.36: measure on every live profile (%d) answers and writes nothing" % n)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("r3", run_r3), ("restart", run_restart), ("r1", run_r1), ("route", run_route), ("exec", run_exec), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
