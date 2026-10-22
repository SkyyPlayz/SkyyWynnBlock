"""Harness for SkyyArmory 0.1.42 (Balance P4: a charged shot restarts SkyySkills' quick refill wait; tools/armory_0_1_42_patch.py). Build first:
    python tools/armory_0_1_42_patch.py && python SkyyArmory/build_skyyarmory_0.1.42.py
    python SkyyArmory/test_skyyarmory_0.1.42.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.41 -> 0.1.42: exactly the planned members (EXPECT); non-class entries: manifest.json only
  X   exec     ArmoryDefs.isCharged for every projectile id of ours (wand / staff charged, Page Burst = yes; quick shots, blinks, markers = no);
               ArmorySpawn.castNote through a fake skill:fn:manaregen: {"cast", UUID} sent, TRUE counted; no function / a throwing one / a
               null UUID = false, never throws; the real SkyySkills 0.4.58 ManaRegenFn in the same JVM keeps the cast time
  W   wiring   ArmorySpawn.apply: isQuick, then isCharged -> castNote (getCreatorUuid) on the non-quick branch only
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration in setup's order + load): no 0.1.42 change
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the creator UUID of a real charged orb at its SPAWN (ArmoryTrav.added reads the same field).
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.42", "0.1.41"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.58.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp4b", "arm")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"ArmoryDefs": ["+m isCharged"], "ArmorySpawn": ["+f CASTS", "+m castNote", "~<clinit>", "~m apply"],
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "SkyyArmoryPlugin": ["~m setup", "~m start"]}   # the version text
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, SKILLS_JAR], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    D, S = JClass(PKG + "ArmoryDefs"), JClass(PKG + "ArmorySpawn")
    pids = D.pids()
    bad = []
    n = {"charged": 0, "other": 0}
    it = pids.entrySet().iterator()
    while it.hasNext():
        e = it.next()
        pid, code = str(e.getKey()), int(e.getValue())
        want = (2000 <= code < 3000) or (4000 <= code < 5000) or (7000 <= code < 8000)
        n["charged" if want else "other"] += 1
        if bool(D.isCharged(JString(pid))) != want or (want and bool(D.isQuick(JString(pid)))):
            bad.append((pid, code))
    K.check(not bad and n["charged"] > 10 and n["other"] > 10 and not bool(D.isCharged(None)) and not bool(D.isCharged(JString("Nope"))),
            "X isCharged: every wand / staff charged orb + Page Burst yes, quick / blink / markers no (%s): %s" % (n, bad[:4]))
    br = D.bridge()
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000142")
    got = []

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, ret, boom=False):
            self.ret, self.boom = ret, boom

        @JOverride
        def apply(self, a):
            if self.boom:
                raise RuntimeError("boom")
            got.append([str(x) for x in a])
            return JClass("java.lang.Boolean").valueOf(self.ret)
    br.remove("skill:fn:manaregen")
    K.check(not bool(S.castNote(U)), "X castNote without SkyySkills: false, nothing thrown")
    br.put("skill:fn:manaregen", Fn(True))
    c0 = int(S.CASTS)
    K.check(bool(S.castNote(U)) and got == [["cast", str(U)]] and int(S.CASTS) == c0 + 1, "X castNote sends {\"cast\", UUID} and counts a TRUE: %s" % got)
    K.check(not bool(S.castNote(None)) and len(got) == 1, "X castNote(null) sends nothing")
    br.put("skill:fn:manaregen", Fn(True, boom=True))
    K.check(not bool(S.castNote(U)), "X a throwing skill:fn:manaregen: false, nothing thrown")
    # the REAL SkyySkills 0.4.58 verb in the same JVM (the bridge map is shared)
    br.put("skill:fn:manaregen", JClass("com.skyy.skills.ManaRegenFn")())
    CS = JClass("com.skyy.skills.ClassStat")
    K.check(bool(S.castNote(U)) and 0 <= int(CS.sinceCast(U, JClass("java.lang.System").currentTimeMillis())) < 5000,
            "X with the real SkyySkills 0.4.58 ManaRegenFn: TRUE and ClassStat keeps the cast time")
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
    bos = BOS()
    for m in cp.get(PKG + "ArmorySpawn").getDeclaredMethods():
        if str(m.getName()) == "apply":
            IP(PS(bos)).print_(m)
    code = str(bos.toString())
    K.check("ArmoryDefs.isCharged" in code and "ArmorySpawn.castNote" in code and "getCreatorUuid" in code
            and code.index("ArmoryDefs.isQuick") < code.index("ArmoryDefs.isCharged") < code.index("ArmorySpawn.castNote"),
            "W ArmorySpawn.apply: isQuick, then isCharged -> castNote(the creator UUID)")
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
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("exec", run_exec), ("wire", run_wire), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
