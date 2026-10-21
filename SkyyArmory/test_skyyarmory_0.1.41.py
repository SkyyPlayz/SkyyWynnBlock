"""Harness for SkyyArmory 0.1.41 (Skill Trees 3 R3a: Blink Step + Smite; tools/armory_0_1_41_patch.py). Build first:
    python tools/armory_0_1_41_patch.py && python SkyyArmory/build_skyyarmory_0.1.41.py
    python SkyyArmory/test_skyyarmory_0.1.41.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.40 -> 0.1.41: exactly the planned members (EXPECT) + the new class BlinkStep; non-class entries: manifest.json only
  X   exec     BlinkStep's pure rules (Smite's reach: + blocks, never past the shot's range; the Stamina a roll took: the larger drop of
               two ticks, at most 30, never negative); the roll edge (tickPlayer / start) returns quietly with no player / no stats; the
               reader list tree:reads:SkyyArmory = the 0.1.40 keys + Class.fx.blinkStep + Class.fx.smiteReach; ArmoryTree.b reads a fake
               tree:fn:bonus "Class.fx.<code>" (SkyyTrees 0.4.1) with its 1 s cache
  W   wiring   TravTick.tick calls BlinkStep.tickPlayer; ArmoryTrav.added reads Class.fx.smiteReach through ArmoryTree.b; BlinkStep.run uses the
               staff blink's path (TravMath.scanL, Teleport, the portal effect, the shadow trail, the blink sound)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration in setup's order + load): no 0.1.41 change
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the blink on a real roll, the Stamina refund vs SkyySkills' roll cost, a wand shot's range.
"""
import os, sys, json, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.41", "0.1.40"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "st3r3a", "arm")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"ArmoryTrav": ["~m added"], "TravTick": ["~m tick"],   # Smite's reach; Blink Step's tick
          "ArmoryTree": ["~m publish", "~m unpublish"],   # KEYS (inlined): + Class.fx.blinkStep, Class.fx.smiteReach
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "SkyyArmoryPlugin": ["~m setup", "~m start"]}   # the version text
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040")
OLD_KEYS = "Class.Mage.T2,Class.Mage.T3,Class.Mage.PA1,Class.Mage.PA2,Class.Mage.PB1,Class.Priest.T1,Class.Assassin.T3,Class.Assassin.PC1,Class.Assassin.PC2,Class.Assassin.PC3,Class.Assassin.PC4"


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def setup_jvm(jar, *more):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR] + list(more) + [jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    return JClass


def run_exec(out, jar, scratch, _home):
    from jpype import JImplements, JOverride
    K = HK.Child(out)
    JClass = setup_jvm(jar, B.JAVASSIST)
    BS, AT = JClass(PKG + "BlinkStep"), JClass(PKG + "ArmoryTree")
    K.eq([float(BS.reach(16.0, 32.0, 4.0)), float(BS.reach(30.0, 32.0, 6.0)), float(BS.reach(16.0, 32.0, 0.0)), float(BS.reach(0.0, 32.0, 4.0))],
         [20.0, 32.0, 16.0, 0.0], "X Smite reach: +4 blocks; never past the shot's range (32); no rank / no far part = unchanged")
    K.eq([float(BS.paid(50.0, 45.0, 40.0)), float(BS.paid(40.0, 50.0, 45.0)), float(BS.paid(40.0, 40.0, 45.0)), float(BS.paid(100.0, 0.0, 10.0))],
         [10.0, 5.0, 0.0, 30.0], "X the Stamina a roll took: the larger drop of two ticks, never negative, at most 30")
    K.eq((float(BS.DIST), str(BS.KEY), str(BS.SMITE)), (4.0, "Class.fx.blinkStep", "Class.fx.smiteReach"), "X Blink Step 4 blocks; the two fx keys")
    K.check(BS.tickPlayer(None, None, None) is None, "X tickPlayer with no player returns quietly")
    K.eq(str(BS.start(None, None, None, None, None, 5.0)), "nostats", "X start with no stats map = nothing taken")
    bj = BS(None, None, None, 7.0, 5.0)   # FIX ROUND: the failed blink's job keeps its Mana cost + the roll's Stamina
    K.eq((float(bj.cost), float(bj.stam), str(bj.undo(None, None, "no free spot ahead")), str(BS.LAST_WHY)),
         (7.0, 5.0, "gone", "no free spot ahead - an ordinary roll (Mana back)"), "X FIX a blink that cannot happen = an ordinary roll (undo; no player left = nothing to give)")
    keys = str(AT.KEYS)
    K.eq(keys, OLD_KEYS + ",Class.fx.blinkStep,Class.fx.smiteReach", "X tree:reads:SkyyArmory = the 0.1.40 keys + the two fx codes")
    br = AT.bridge()
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("12345678-2222-3333-4444-555555555555")

    @JImplements("java.util.function.Function")
    class Bonus(object):
        @JOverride
        def apply(self, a):
            k = str(a[1])
            return JClass("java.lang.Double").valueOf(1.0 if k == "Class.fx.blinkStep" else (6.0 if k == "Class.fx.smiteReach" else 0.0))
    br.put("tree:fn:bonus", Bonus())
    AT.CACHE.clear()
    K.eq((float(AT.b(u, "Class.fx.blinkStep")), float(AT.b(u, "Class.fx.smiteReach"))), (1.0, 6.0), "X ArmoryTree.b reads SkyyTrees 0.4.1's Class.fx.<code> answers")
    br.remove("tree:fn:bonus")
    K.eq(float(AT.b(u, "Class.fx.smiteReach")), 6.0, "X ... cached 1 s (the 0.1.9 rule)")
    K.save()


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def refs(cls, meth):
        c = cp.get(PKG + cls)
        out_ = set()
        for m in c.getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ci = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while ci.hasNext():
                pos = ci.next()
                op = ci.byteAt(pos)
                if op in (0xb6, 0xb8, 0xb7, 0xb9):
                    idx = ci.u16bitAt(pos + 1)
                    out_.add(str(cpl.getMethodrefClassName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." +
                             str(cpl.getMethodrefName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefName(idx)))
                if op in (0x12, 0x13):
                    try:
                        out_.add("ldc:" + str(cpl.getStringInfo(ci.byteAt(pos + 1) if op == 0x12 else ci.u16bitAt(pos + 1))))
                    except Exception:
                        pass
        return out_
    K.check("BlinkStep.tickPlayer" in refs("TravTick", "tick"), "W TravTick.tick calls BlinkStep.tickPlayer")
    a = refs("ArmoryTrav", "added")
    K.check("ArmoryTree.b" in a and "ldc:Class.fx.smiteReach" in a, "W ArmoryTrav.added reads Class.fx.smiteReach through ArmoryTree.b")
    r = refs("BlinkStep", "run")
    K.check(all(x in r for x in ("TravMath.scanL", "Teleport.createForPlayer", "ArmoryTrav.effect", "ArmoryTrav.shadowTrail", "ArmoryTrav.sound")),
            "W BlinkStep.run = the staff blink's path: %s" % sorted(x for x in r if not x.startswith("ldc:"))[:12])
    K.check("BlinkStep.undo" in r, "W FIX BlinkStep.run undoes the payment when no blink happens")
    ud = refs("BlinkStep", "undo")
    K.check("ArmoryTrav.addStat" in ud and "EntityStatMap.subtractStatValue" in ud, "W FIX BlinkStep.undo: the Mana back + the roll's Stamina taken again (%s)" % sorted(ud))
    s = refs("BlinkStep", "start")
    K.check("ArmoryTrav.addStat" in s and "EntityStatMap.subtractStatValue" in s and "World.execute" in s, "W BlinkStep.start: Stamina back, Mana taken, the job on the world thread")

    def seq(cls, meth):   # FIX ROUND 2: the calls of one method in bytecode order
        c = cp.get(PKG + cls)
        o = []
        for m in c.getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ci = m.getMethodInfo().getCodeAttribute().iterator()
            cpl = m.getMethodInfo().getConstPool()
            while ci.hasNext():
                pos = ci.next()
                op = ci.byteAt(pos)
                if op in (0xb6, 0xb8, 0xb7, 0xb9):
                    idx = ci.u16bitAt(pos + 1)
                    o.append(str(cpl.getMethodrefClassName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." +
                             str(cpl.getMethodrefName(idx) if op != 0xb9 else cpl.getInterfaceMethodrefName(idx)))
        return o
    sq = seq("BlinkStep", "start")
    K.check(sq.index("ArmoryTrav.look") < sq.index("EntityStatMap.subtractStatValue") and sq.index("ArmoryTrav.worldOf") < sq.index("EntityStatMap.subtractStatValue")
            and sq.count("ArmoryTrav.addStat") == 1 and sq.index("ArmoryTrav.addStat") > sq.index("EntityStatMap.subtractStatValue"),
            "W FIX 2 BlinkStep.start checks the look + world BEFORE paying (no look / world = nothing paid, nothing refunded; one addStat = the roll's Stamina): %s" % sq)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    before = tree_hash(home)
    hashes = []
    for start in (1, 2):
        for m in MIGS:
            getattr(Cfg, m)()
        Cfg.load()
        hashes.append(tree_hash(home))
    ch1 = sorted(k for k in set(before) | set(hashes[0]) if before.get(k) != hashes[0].get(k))
    K.check(all(k in ("config.properties", "config-changes.log") or k.startswith("config-history") for k in ch1),
            "D: start 1 writes only an older version's pending config update, if any (%s)" % ch1)
    K.check(hashes[0] == hashes[1], "D: start 2 changes nothing")
    K.notes.append("D: start 1 changed %s" % ch1)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["BlinkStep"],
           phases=[("exec", run_exec), ("wire", run_wire), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
