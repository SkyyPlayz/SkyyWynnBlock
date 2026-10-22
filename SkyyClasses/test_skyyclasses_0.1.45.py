"""Harness for SkyyClasses 0.1.45 (BALANCE PASS P8b, the SkyyClasses part: the skill-tree fight rows; tools/classes_0_1_45_patch.py). Build first:
    python tools/classes_0_1_45_patch.py && python SkyyClasses/build_skyyclasses_0.1.45.py
    python SkyyClasses/test_skyyclasses_0.1.45.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/balp8bfix/cls):
  S   static   the patch re-runs to identical bytes; one class added (UpSk); no new system / command; line endings kept
  A   verify   every class loads + initialises
  C   compare  0.1.44 -> 0.1.45: exactly the planned members (EXPECT)
  X   exec     UpSk EXECUTED: the 6 rows = tools/trees_v3_effects.py; ranks through a fake SkyyTrees tree:fn:level (every key, the free
               Combat Focus key); vals at max = Hardened Edge 4.5 + Combat Focus 3, Finisher 12, Trophy Hunter 9, Thick Skin 8, Iron Will 9;
               the 1 s cache; a Server Setup ceiling applies; a throwing tree:fn:level = nothing (logged once); outB (Finisher only below
               30 % Health, Trophy Hunter only on a boss), cut (0 while OFF), rankOf (boss / mini = 1, elite / "" = 0, no answer = -1), kbOn
               on a REAL KnockbackComponent (applyModifiers: velocity x 0.91 at 9 %); loadV3 seeds trees.properties; tree:reads lists the keys
  W   wiring   bytecode: outW adds skOut before the dmgCap; out() uses skOut when the player has no class codes (the same cap); outAbil
               adds skOut before its cap and runs while UpSk.ON; cutOf starts from UpSk.cut (inside drCap); inc() applies kbOn on the
               Damage's KNOCKBACK_COMPONENT after the cut; the damage hooks run while UpFx.ON || UpSk.ON; setup: load -> loadV3 -> ON
  ST  start twice on a scratch COPY of the live Skyy_SkyyClasses (every one-time update + load + UpSk.loadV3 + the kit): start 1 adds only
      trees.properties (config.properties untouched), start 2 writes nothing; the live folder is only read
  AA  engine-access audit
NOT COVERED (UNVERIFIED in game): a real hit's damage with the rows (UpFx.out / outAbil / inc need a live Store), Hytale actually
shortening the knockback (the vanilla ArmorKnockbackReduction does the same call).
"""
import os, sys, json, shutil, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E

VERSION, OLD = "0.1.45", "0.1.44"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_45_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "balp8bfix", "cls")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyClasses")
ADDED = ["UpSk"]
EXPECT = {
    "UpFx": ["+m bossy", "+m skOut", "~m cutOf", "~m inc", "~m out", "~m outAbil", "~m outW"],
    "AbilShieldSys": ["~m handle"], "DamageLock": ["~m outHook"],
    "CfgFn": ["~m opExport"], "CfgRows": ["+f DL1", "~<clinit>", "~m header", "~m defLines"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["+f DL1", "~<clinit>"],
    "CfgFile": ["~<clinit>", "~m init"], "SkyyClassesPlugin": ["~m setup"], "KitMigrate": ["~m runOnce"],
}
U = "00000000-0000-0000-0000-000000000145"


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.45 - build script') and g.count('VERSION = "0.1.45"') == 1, "S header + VERSION")
    import zipfile as _zf
    _jb = b"".join(_zf.ZipFile(jar).read(_n) for _n in _zf.ZipFile(jar).namelist() if _n.endswith((".class", ".properties", ".json")))
    # fixer (critics 2026-10-22): the trees.properties header names the real page (the 12 rows sit in Abilities, Advanced); the free perk
    # row is "(perk)" and never doubles the tree name; the ceiling help is the tree's own sentence
    K.check(b"Classes -> Abilities (Advanced)" in _jb and b"Classes -> Skill trees" not in _jb, "S fixer: trees.properties points to Server Setup -> Classes -> Abilities (Advanced)")
    K.check(b"Combat Focus Damage (perk)" in _jb and b"Combat Combat Focus" not in _jb, "S fixer: Server Setup row 'Combat Focus Damage (perk)' (no doubled tree name, no 'a rank')")
    K.check(b"whatever the rank, gear or pet" not in _jb and b"Most Combat Focus gives (a flat Combat perk, in %)." in _jb, "S fixer: tree-row ceiling help is the tree's own words")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("makeClass(") - o.count("makeClass("), 1, "S one class added (UpSk)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    S, CC = J("UpSk"), J("ClassCfg")
    rows = V3E.rows("SkyyClasses")
    K.eq([str(x) for x in S.KEY], [V3E.key(e[0], e[1], e[2]) for e in rows], "X UpSk.KEY = trees_v3_effects' SkyyClasses rows")
    K.eq([round(float(S.v3per(i)), 9) for i in range(len(rows))], [e[5] for e in rows], "X per rank (whole %) = the table")
    K.eq([round(float(S.v3most(i)), 9) for i in range(len(rows))], [round(V3E.vmax(e), 9) for e in rows], "X ceilings = the table's natural tops")
    br = CC.bridge()
    uu = JClass("java.util.UUID").fromString(U)
    RK = {}
    CALLS = [0]

    @JImplements("java.util.function.Function")
    class Lvl(object):
        @JOverride
        def apply(self, a):
            CALLS[0] += 1
            if RK.get("throw"):
                raise RuntimeError("boom")
            return JClass("java.lang.Integer")(RK.get(str(a[1]), 0))
    br.remove("tree:fn:level")
    S.C.clear()
    K.eq([round(float(x), 6) for x in list(S.vals(uu))[1:]], [0.0] * 5, "X no SkyyTrees: every row 0")
    br.put("tree:fn:level", Lvl())
    for e in rows:
        RK[V3E.key(e[0], e[1], e[2])] = V3E.maxrank(e[0], e[1], e[2])
    S.C.clear()
    v = [round(float(x), 6) for x in list(S.vals(uu))[1:]]
    K.eq(v, [7.5, 12.0, 9.0, 8.0, 9.0], "X vals at max: dmg 4.5 + 3 (Hardened Edge + Combat Focus), dmgLow 12, dmgBoss 9, drAll 8, kbRes 9")
    n0 = CALLS[0]
    RK["Skill.Combat.b2.r3a"] = 1
    K.eq((round(float(S.vals(uu)[4]), 6), CALLS[0] - n0), (8.0, 0), "X the 1 s cache: a rank change inside it asks SkyyTrees nothing")
    S.C.clear()
    K.eq(round(float(S.vals(uu)[4]), 6), 2.0, "X after the cache: Thick Skin rank 1 = 2 %")
    RK["Skill.Combat.b2.r3a"] = 4
    S.V3X5 = 5.0
    S.C.clear()
    K.eq(round(float(S.vals(uu)[4]), 6), 5.0, "X a Server Setup ceiling (Thick Skin most 5) applies at once")
    S.V3X5 = 8.0
    S.ON = False
    K.eq(float(S.cut(uu)), 0.0, "X cut() = 0 while UpSk is off")
    S.ON = True
    S.C.clear()
    K.eq(float(S.cut(uu)), 8.0, "X cut() = Thick Skin 8 (inside drCap in cutOf)")
    s = S.vals(uu)
    K.eq((float(S.outB(s, 0.2, True)), float(S.outB(s, 0.5, False)), float(S.outB(s, -1.0, True)), float(S.outB(s, 0.29, False))),
         (28.5, 7.5, 16.5, 19.5), "X outB: + Finisher below 30 % Health only, + Trophy Hunter on a boss only")
    OA = JClass("java.lang.Object[]")
    ri = lambda a: int(S.rankOf(a))
    K.eq((ri(OA([1, 2, 3, 4, 5, 6, "boss"])), ri(OA([1, 2, 3, 4, 5, 6, "mini"])), ri(OA([1, 2, 3, 4, 5, 6, "elite"])), ri(OA([1, 2, 3, 4, 5, 6, ""])),
          ri(None), ri(OA([1, 2]))), (1, 1, 0, 0, -1, -1), "X rankOf: boss / mini = 1, elite / plain = 0, no answer = -1 (the Boss role words)")
    KBC, V3 = JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"), JClass("org.joml.Vector3d")
    kb = KBC()
    kb.setVelocity(V3(1.0, 0.5, 0.0))
    ok = bool(S.kbOn(kb, 9.0))
    kb.applyModifiers()
    vel = kb.getVelocity()
    K.check(ok and abs(float(vel.x()) - 0.91) < 1e-9 and abs(float(vel.y()) - 0.455) < 1e-9, "X kbOn on a real KnockbackComponent: x 0.91 at 9 %% (%s)" % vel)
    K.check(not bool(S.kbOn(None, 9.0)) and not bool(S.kbOn(kb, 0.0)), "X kbOn: no knockback / 0 % = nothing")
    RK["throw"] = True
    S.C.clear()
    K.eq([round(float(x), 6) for x in list(S.vals(uu))[1:]], [0.0] * 5, "X a throwing tree:fn:level = every row 0 (logged once)")
    K.check(bool(S.FAILED), "X ... and the once-flag is set")
    RK["throw"] = False
    d = os.path.join(scratch, "x")
    os.makedirs(d, exist_ok=True)
    r = str(S.loadV3(JClass("java.nio.file.Paths").get(d)))
    K.check("read" in r and open(os.path.join(d, "trees.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyClasses"), "X loadV3 seeds trees.properties: %s" % r)
    import zipfile
    pc = zipfile.ZipFile(jar).read("com/skyy/classes/SkyyClassesPlugin.class")
    K.check(V3E.reads_csv("SkyyClasses").encode() in pc and b"tree:reads:SkyyClasses" in pc, "X tree:reads:SkyyClasses (the setup constant in the jar) carries the 6 Skill keys")
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
    ow = code("UpFx", "outW")
    K.check("UpFx.skOut" in ow and ow.index("UpFx.skOut") < ow.rindex("AbilNum.UX_DMGCAP") < ow.rindex("AbilNum.UX_LETHAL"), "W outW: skOut, then the dmgCap, then Lethal")
    o = code("UpFx", "out")
    K.check("UpFx.skOut" in o and "UpFx.outW" in o and o.index("UpFx.skOut") < o.rindex("AbilNum.UX_DMGCAP"), "W out(): no class codes -> skOut under the same cap")
    oa = code("UpFx", "outAbil")
    K.check("UpSk.ON" in oa and "UpFx.skOut" in oa and oa.index("UpFx.skOut") < oa.rindex("AbilNum.UX_DMGCAP"), "W outAbil: runs while UpSk.ON, skOut before its cap")
    c = code("UpFx", "cutOf")
    K.check("UpSk.cut" in c and c.index("UpSk.cut") < c.index("UpFx.g"), "W cutOf starts from UpSk.cut (the cap in inc() covers it)")
    i = code("UpFx", "inc")
    K.check("UpSk.kbOn" in i and "KNOCKBACK_COMPONENT" in i and i.index("AbilNum.UX_DRCAP") < i.index("UpSk.kbOn"), "W inc(): drCap on the cut, then Iron Will on the hit's KNOCKBACK_COMPONENT")
    K.check("UpSk.ON" in code("AbilShieldSys", "handle") and "UpSk.ON" in code("DamageLock", "outHook"), "W the damage hooks run while UpFx.ON || UpSk.ON")
    s = code("SkyyClassesPlugin", "setup")
    K.check(s.index("ClassCfg.load") < s.index("UpSk.loadV3") < s.index("UpSk.ON"), "W setup: ClassCfg.load -> UpSk.loadV3 -> UpSk.ON = true")
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
        K.eq(ch, ["trees.properties"], "ST start 1 on a scratch COPY of the live data: only the new trees.properties is written (%s; %s)" % (o["p4"][:80], o["sk"]))
        K.check(open(os.path.join(base, "trees.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyClasses"), "ST trees.properties = the table's numbers")
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
           phases=[("static", run_static), ("exec", run_exec), ("wire", run_wire), ("st1", run_st1), ("st2", run_st2)], script=__file__)
