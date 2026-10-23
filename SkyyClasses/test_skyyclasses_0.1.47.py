"""Harness for SkyyClasses 0.1.47 (COMBAT INTO CLASS + CLASS TREE CLARITY, the SkyyClasses part; tools/classes_0_1_47_patch.py). Build first:
    python tools/classes_0_1_47_patch.py && python SkyyClasses/build_skyyclasses_0.1.47.py
    python SkyyClasses/test_skyyclasses_0.1.47.py [--keep]
Deploys + rolls back TOGETHER with SkyyTrees 0.6.0, SkyySkills 0.4.64, SkyyRebirth 0.5.2 (SkyyTrees/test_skyytrees_0.6.0.py runs both jars
in one JVM: the map PICK, the panel equip, the Weaponcraft rows through tree:fn:level).
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/cls060/cls):
  S    static  the patch re-runs to identical bytes; two classes added (AbilAltFn, AbilFold); no new system / command; line endings kept
  A    verify  every class loads + initialises
  C    compare 0.1.46 -> 0.1.47: exactly the planned members (EXPECT)
  X46  the whole 0.1.46 EXEC + WIRE phases on the 0.1.47 jar (Wynn names, classes:fn:dot, affinity - unchanged)
  X    exec    EXECUTED: mods.treeUnlock (a v4 tree list: a modifier is usable only with its unlock node; the level from use; the lock
               text names the tree), the fixed keys (fixedOrder A / B, AbilStore.slots under V4K, "place" refused), THE PICK (both alts
               needed, out of combat, abil.altSwitch.wait between switches, the new alt on cooldown / abil.altSwitch.cooldown off, a
               class with one alt), class:fn:altPick, THE FOLD (AbilFold.apply: old ranks -> use counts raised to the level's step, never
               lowered, capped, the fixed key rows, a verified History copy, fold-changes.log, abil.fold=done, twice = once, waits for
               the fold list), the Weaponcraft rows (UpSk: Reprisal thorns 3 %, Second Wind lowHeal 5 % a rank, the ceilings), the 3 rows
  W    wiring  bytecode: abilDo "alt" -> altSwitch; ClassTick runs AbilFold.tick; setup / shutdown class:fn:altPick; UpFx.inc runs
               Reprisal (hit UpThorns) + secondWind after the cut
  ST   start twice on a scratch COPY of the live Skyy_SkyyClasses: nothing written; the live folder only read
  AA   engine-access audit
NOT COVERED (UNVERIFIED in game): Reprisal / Second Wind on a real hit in the ECS (inc needs a live Store), the fold's chat line at login,
the 10 s switch wait across a restart (memory only, by design).
"""
import os, sys, json, shutil, subprocess, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_46", os.path.join(HERE, "test_skyyclasses_0.1.46.py"))
T46 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T46)
sys.argv[:] = _argv

VERSION, OLD = "0.1.47", "0.1.46"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_47_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cls060", "cls")))
LIVE = T46.LIVE
ADDED = ["AbilAltFn", "AbilFold"]
EXPECT = {   # checked 2026-10-23 (the class compare vs 0.1.46 of the first harness run; every member is a change of tools/classes_0_1_47_patch.py)
    'Abil': ['+m altSwitch', '+m lockText', '+m treeUnlock', '~m doAction', '~m equipMod', '~m holdText', '~m mlvlT', '~m modOk', '~m modRows', '~m treeCsv'],
    'AbilCfg': ['+f ALT_CD', '+f ALT_WAIT', '+f MODS_TREE', '~<clinit>', '~m read'],
    'AbilDefs': ['+m fixedOrder'],
    'AbilPage': ['~m handleDataEvent'],
    'AbilStore': ['+f ALTSW', '+f V4K', '~<clinit>', '~m slots'],
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'ClassCfg': ['~<clinit>'],
    'ClassTick': ['~m run'],
    'KitMigrate': ['~m runOnce'],
    'SkyyClassesPlugin': ['~m setup', '~m shutdown'],
    'UpFx': ['+f SECONDW', '+f SWIND', '+f SWIND_GAP', '+f THORNS', '+m secondWind', '~<clinit>', '~m inc'],
    'UpSk': ['+f V3P6', '+f V3P7', '+f V3P8', '+f V3X6', '+f V3X7', '+f V3X8', '~<clinit>', '~m compute', '~m loadV3', '~m v3most', '~m v3per', '~m vals'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000147"
W = "00000000-0000-0000-0000-0000000001f7"
tree_hash = T46.tree_hash


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.47 - build script') and g.count('VERSION = "0.1.47"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 2, "S two classes added (AbilAltFn, AbilFold)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec46(out, jar, scratch, home):
    T46.run_exec(out, jar, scratch, home)


def run_wire46(out, jar, scratch, home):
    T46.run_wire(out, jar, scratch, home)


def _fn(JImplements, JOverride, f):
    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    A, AD, AMD, AS, CFG, CS, CC, UpSk, Fold = J("Abil"), J("AbilDefs"), J("AbilModDefs"), J("AbilStore"), J("AbilCfg"), J("ClassStore"), J("ClassCfg"), J("UpSk"), J("AbilFold")
    Paths, UUID, Long, Int, Sys = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.System")
    SA = lambda xs: jpype.JArray(jpype.JString)(xs)
    br = CC.bridge()
    d0 = os.path.join(scratch, "x")
    os.makedirs(os.path.join(d0, "abilities"), exist_ok=True)
    AS.DIR = Paths.get(os.path.join(d0, "abilities"))
    K.eq([bool(CFG.MODS_TREE), int(CFG.ALT_WAIT), bool(CFG.ALT_CD), bool(CFG.TREE_GATE)], [True, 10, True, True],
         "CFG mods.treeUnlock ON, abil.altSwitch.wait 10 s, abil.altSwitch.cooldown ON (abil tree gate on)")
    gsrc = open(GEN, encoding="utf-8").read()
    K.check(all(('"%s"' % k) in gsrc for k in ("mods.treeUnlock", "abil.altSwitch.wait", "abil.altSwitch.cooldown")), "CFG the three Server Setup rows")
    IDS = [str(x) for x in AD.IDS]
    NAMES = [str(x) for x in AD.NAMES]
    wi = [str(x) for x in J("ClassDefs").NAMES].index("Warrior")
    ai = int(AD.of(wi, 0))
    K.eq(IDS[ai], "RallyingGuard", "the Warrior A1")
    v4 = "v3,v4,fold,A1,A4a,A4b"
    v3 = "v3,A1,A4a,A4b"
    # ---- 1. modifiers unlock in the tree
    K.eq([bool(A.treeUnlock(v4)), bool(A.treeUnlock(v3)), bool(A.treeUnlock(None))], [True, False, False], "MOD treeUnlock: a v4 list only")
    CFG.MODS_TREE = False
    K.check(not bool(A.treeUnlock(v4)), "MOD mods.treeUnlock off = the old rule")
    CFG.MODS_TREE = True
    m0 = str(AMD.MID[int(AMD.at(ai, 0))])
    K.eq([bool(A.modOk(v4, ai, 0, 9)), bool(A.modOk(v4 + ",m.RallyingGuard.%s=1" % m0, ai, 0, 1)), bool(A.modOk(v3, ai, 0, 9))], [False, True, True],
         "MOD modOk: v4 without the node = locked even at Lv 9; with the node = open at Lv 1; a v3 list = by level")
    lt = str(A.lockText(v4, ai, 0, 3))
    K.check("unlock it in your class tree (1 point" in lt and "then it levels by use" in lt, "MOD the lock text names the tree: %s" % lt)
    K.check("unlocks at" in str(A.lockText(v3, ai, 0, 1)), "MOD a v3 list: the old level text")
    mi0 = int(AMD.at(ai, 0))
    P = JClass("java.util.Properties")()
    K.eq([int(A.mlvlT(P, "RallyingGuard", mi0, v4 + ",m.RallyingGuard.%s=1" % m0)), int(A.mlvlT(P, "RallyingGuard", mi0, v3 + ",m.RallyingGuard.%s=3" % m0))], [1, 3],
         "MOD mlvlT: a v4 unlock node = Lv 1 (no ranks added); a v3 rank 3 = Lv 3 (as before)")
    P.setProperty("m.RallyingGuard." + m0, str(int(Fold.usesFor(3))))
    K.eq(int(A.mlvlT(P, "RallyingGuard", mi0, v4 + ",m.RallyingGuard.%s=1" % m0)), 3, "MOD the level comes from use (uses for Lv 3 = Lv 3)")
    # ---- 2. the fixed keys
    fa, fb = [str(x) for x in AD.fixedOrder(wi, "A")], [str(x) for x in AD.fixedOrder(wi, "B")]
    K.eq([fa, fb[2]], [["RallyingGuard", "ShieldShockwave", "Challenge", "IronChain"], "GuardiansOath"], "KEY fixedOrder: A1, A2, the picked alt, A3")
    bad = []
    for ci in range(len(list(J("ClassDefs").NAMES))):
        if not bool(AD.classHas(ci)):
            continue
        f = [str(x) for x in AD.fixedOrder(ci, "A")]
        if f[0] != IDS[int(AD.of(ci, 0))] or f[1] != IDS[int(AD.of(ci, 1))] or f[3] != IDS[int(AD.of(ci, 2))]:
            bad.append(ci)
    K.eq(bad, [], "KEY fixedOrder of every class: Ability 2 = A1, Ability 3 = A2, Crouch + 3 = A3")
    br.put("profile:class:" + U, "Warrior")
    br.put("class:" + U, "Warrior")
    u = UUID.fromString(U)
    k = str(CC.pkey(u))
    ci = int(CS.classIndex(u))
    K.eq(ci, wi, "a Warrior")
    AS.set(k, SA(["p1", "p2", "a1", "a2"]), SA(["ShieldShockwave", "RallyingGuard", "IronChain", "Challenge"]))
    K.eq([str(x) for x in AS.slots(k, ci)][:2], ["ShieldShockwave", "RallyingGuard"], "KEY no v4 list: the stored order (0.1.46)")
    AS.V4K.put(k, True)
    K.eq([str(x) for x in AS.slots(k, ci)], fa, "KEY a v4 list (V4K): the fixed keys")
    r = str(A.doAction(u, "place", "RallyingGuard", "1", v4)) if hasattr(A, "doAction") else None
    K.notes.append("place: %s" % r)
    if r is not None:
        K.check(r.startswith("-Your keys come from your class tree now"), "KEY 'place' answers why: %s" % r[:80])
    # ---- 3. THE PICK
    CB = {"ms": 0}
    br.put("skill:fn:combat", _fn(JImplements, JOverride, lambda a: Long(CB["ms"])))
    Alt = J("AbilAltFn")()
    K.eq(str(Alt.apply(u)), "A", "PICK class:fn:altPick = A at the start")
    r = str(A.altSwitch(u, "B", "v3,v4,A1,A4a"))
    K.check(r.startswith("-Both Ability 1 alts come with row 2"), "PICK only one alt owned: refused (%s)" % r)
    CB["ms"] = 3000
    r = str(A.altSwitch(u, "B", v4))
    K.check(r.startswith("-Leave combat first") and str(AS.pick(k)) == "A", "PICK in combat refused: %s" % r)
    CB["ms"] = 0
    r = str(A.altSwitch(u, "B", v4))
    now = int(Sys.currentTimeMillis())
    K.check(r.startswith("+Your Ability 1 alt is now Guardian's Oath (Crouch + Ability 2) - it starts on its cooldown.") and str(AS.pick(k)) == "B" and str(Alt.apply(u)) == "B",
            "PICK out of combat: B (%s)" % r)
    gi = IDS.index("GuardiansOath")
    K.check(int(AS.left(k, "GuardiansOath", now)) > 0 and int(AS.left(k, "GuardiansOath", now)) <= int(AD.cdMs(gi, 0)), "PICK the new alt starts on its full cooldown")
    K.eq([str(x) for x in AS.slots(k, ci)][2], "GuardiansOath", "PICK Crouch + Ability 2 = the new alt")
    r = str(A.altSwitch(u, "B", v4))
    K.check("already your Ability 1 alt" in r, "PICK the same alt again: %s" % r)
    r = str(A.altSwitch(u, "A", v4))
    K.check(r.startswith("-Wait ") and "before switching your Ability 1 alt again" in r, "PICK 10 s between switches: %s" % r)
    CFG.ALT_WAIT = 0
    CFG.ALT_CD = False
    AS.arm(k, "Challenge", now, 0)
    r = str(A.altSwitch(u, "A", v4))
    K.check(r.startswith("+Your Ability 1 alt is now Challenge (Crouch + Ability 2).") and int(AS.left(k, "Challenge", int(Sys.currentTimeMillis()))) == 0,
            "PICK abil.altSwitch.wait 0 + abil.altSwitch.cooldown off: switches at once, no cooldown (%s)" % r)
    CFG.ALT_WAIT = 10
    CFG.ALT_CD = True
    one = [c for c in range(len(list(J("ClassDefs").NAMES))) if bool(AD.classHas(c)) and int(AD.of(c, 4)) < 0]
    K.notes.append("classes with one Ability 1 alt: %s" % one)
    if one:
        br.put("profile:class:" + W, str(J("ClassDefs").NAMES[one[0]]))
        r = str(A.altSwitch(UUID.fromString(W), "B", v4))
        K.check(r.startswith("-" + str(J("ClassDefs").NAMES[one[0]]) + "s have one Ability 1 alt"), "PICK a class with one alt: %s" % r)
    # ---- 4. THE FOLD
    AS.V4K.remove(k)
    AS.set(k, SA(["m.RallyingGuard." + m0, "u.RallyingGuard"]), SA(["0", "40"]))
    m1 = str(AMD.MID[int(AMD.at(ai, 1))])
    AS.set(k, SA(["m.RallyingGuard." + m1]), SA([str(int(Fold.usesFor(4)) + 7)]))
    HAND = ["ShieldShockwave", "RallyingGuard", "IronChain", "Challenge"]   # fix round 2: a hand-arranged key order (kept + logged)
    AS.set(k, SA(["p1", "p2", "a1", "a2"]), SA(HAND))
    mgi = [str(x) for x in J("ClassDefs").NAMES].index("Mage")
    mai = int(AD.of(mgi, 0))
    mid_ = IDS[mai]
    mm0 = str(AMD.MID[int(AMD.at(mai, 0))])
    AS.save(k)
    f = os.path.join(d0, "abilities", k + ".properties")
    before = open(f, "rb").read()
    K.check(Fold.apply(k, ci, "v3,v4,A1,o.RallyingGuard.%s=3" % m0) is None, "FOLD waits for the tree's fold list (no 'fold' token)")
    csv = "v3,v4,fold,A1,A4a,A4b,o.RallyingGuard.%s=3,o.RallyingGuard.%s=1,o.Nope.Power=2,o.RallyingGuard.Nope=4,o.%s.%s=2" % (m0, m1, mid_, mm0)   # + another class tree's rank (fix round 2)
    r = Fold.apply(k, ci, csv)
    K.check(r is not None and "your levels stay" in str(r) and "Lv 3" in str(r), "FOLD the chat text: %s" % r)
    AS.save(k)
    p = AS.load(k)
    K.eq([int(A.numOf(p, "m.RallyingGuard." + m0)), int(A.numOf(p, "m.RallyingGuard." + m1)), str(p.getProperty("abil.fold"))],
         [int(Fold.usesFor(3)), int(Fold.usesFor(4)) + 7, "done"], "FOLD old ranks 3 -> the uses of Lv 3; a modifier already above its level keeps its uses (never lowered); abil.fold=done")
    K.eq(int(A.numOf(p, "m.%s.%s" % (mid_, mm0))), int(Fold.usesFor(2)), "FOLD another class tree's old ranks are kept too (a Warrior profile with Mage ranks: %s.%s -> Lv 2 uses)" % (mid_, mm0))
    K.eq([str(p.getProperty(x)) for x in ("p1", "p2", "a1", "a2")], HAND, "FOLD a hand-arranged key order is KEPT (PROJECT-RULES 4; the v4 tree uses the fixed keys anyway)")
    AS.V4K.put(k, True)
    K.eq([str(x) for x in AS.slots(k, ci)], fa, "FOLD ... and the v4 keys stay the fixed ones")
    h = os.path.join(d0, "history", "fold", k + ".properties")
    K.check(os.path.isfile(h) and open(h, "rb").read() == before, "FOLD the History copy = the file before, byte for byte")
    lg = open(os.path.join(d0, "fold-changes.log"), encoding="utf-8").read()
    K.check(sum(1 for ln in lg.splitlines() if k in ln) == 1 and "Undo: stop the server, copy history/fold/" + k in lg, "FOLD one fold-changes.log line with the Undo")
    K.check("key order kept as arranged" in lg, "FOLD the kept key order is logged")
    K.eq(str(Fold.apply(k, ci, csv)), "", "FOLD twice = once (abil.fold=done)")
    K.eq(int(Fold.usesFor(1)), 0, "FOLD Lv 1 = 0 uses")
    # ---- 5. the Weaponcraft rows (UpSk vals [6] thorns, [7] lowHeal)
    RK = {"Skill.Combat.b2.r3b": 3, "Skill.Combat.b2.r3c": 2}
    br.put("tree:fn:level", _fn(JImplements, JOverride, lambda a: Int(RK.get(str(a[1]), 0))))
    UpSk.C.clear()
    v = [float(x) for x in UpSk.compute(u, Sys.currentTimeMillis())]
    K.eq([round(v[6], 6), round(v[7], 6)], [9.0, 10.0], "UPSK Reprisal 3 = 9 % thorns, Second Wind 2 = 10 %")
    RK["Skill.Combat.b2.r3b"] = 50
    RK["Skill.Combat.b2.r3c"] = 50
    UpSk.C.clear()
    v = [float(x) for x in UpSk.compute(u, Sys.currentTimeMillis())]
    keys = [str(x) for x in UpSk.KEY]
    K.check(v[6] == float(UpSk.v3most(keys.index("Skill.Combat.b2.r3b"))) and v[7] == float(UpSk.v3most(keys.index("Skill.Combat.b2.r3c"))), "UPSK each row capped at its ceiling (%s / %s)" % (v[6], v[7]))
    K.eq(int(J("UpFx").SWIND_GAP), 15000, "UPSK a fight for Second Wind = hits less than 15 s apart")
    K.save()


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    da = "\n".join(code("Abil", n) for n in ("doAction", "abilDo") if code("Abil", n))
    K.check("Abil.altSwitch" in da and '"alt"' in da or "Abil.altSwitch" in da, "W abilDo 'alt' -> altSwitch")
    K.check("AbilFold.tick" in code("ClassTick", "run") or "AbilFold.tick" in "\n".join(code("ClassTick", n) for n in ("tick", "run")), "W ClassTick runs AbilFold.tick")
    s = code("SkyyClassesPlugin", "setup")
    K.check("class:fn:altPick" in s and "AbilAltFn" in s, "W setup puts class:fn:altPick")
    K.check("class:fn:altPick" in code("SkyyClassesPlugin", "shutdown"), "W shutdown removes it")
    inc = code("UpFx", "inc")
    K.check("UpThorns" in inc and "UpFx.secondWind" in inc and inc.index("UpFx.cutOf") < inc.index("UpThorns") < inc.index("UpFx.secondWind"), "W inc: the cut, then Reprisal, then Second Wind")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS, S = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore"), JClass(PKG + "UpSk")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "m41": str(Cfg.migrate0141()),
         "p4": str(Cfg.migrateP4()), "load": str(Cfg.load()), "sk": str(S.loadV3(Paths.get(base)))}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if step == "1":
        K.check(ch in ([], ["trees.properties"]), "ST start 1 on a scratch COPY of the live data: 0.1.47 writes nothing of its own (%s; %s)" % (ch, o["p4"][:80]))
    else:
        K.check(not ch and o["p4"] == "", "ST start 2: nothing written (%s)" % ch)
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("exec46", run_exec46), ("wire46", run_wire46), ("exec", run_exec), ("wire", run_wire), ("st1", run_st1), ("st2", run_st2)],
           script=__file__)
