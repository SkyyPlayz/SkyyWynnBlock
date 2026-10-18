"""Harness for SkyyArmory 0.1.32 (THE BLINK-LANDING BRIDGE; tools/armory_0_1_32_patch.py). Build first:
    python tools/armory_0_1_32_patch.py && python SkyyArmory/build_skyyarmory_0.1.32.py

    python SkyyArmory/test_skyyarmory_0.1.32.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.31 -> 0.1.32: exactly the bridge pieces (ArmoryTrav LAND_KEY / ON_KEY / LANDS / LISTENED / LAST_LAND + publishLand +
               landed, the one call in blink) + the version texts differ
  X   exec     publishLand / landed on the real bridge map: the record armory:blink:<uuid> (8 plain java.lang elements), every
               armory:on:blink:* Function called once with it, other keys / non-Functions skipped, a throwing listener caught (the others
               still run), bad records refused (-1), counters; blink() calls landed only after the Teleport (bytecode order)
  D   live     START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyArmory: nothing rewritten
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.32", "0.1.31"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "pa4", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"ArmoryTrav": ["~<clinit>", "+f LAND_KEY", "+f ON_KEY", "+f LANDS", "+f LISTENED", "+f LAST_LAND", "+m publishLand", "+m landed", "+m forgetLand", "+m clearLands", "~m blink"],
          # the version text "0.1.32" (ldc strings in the loader / export / Server Setup header / ready line)
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "CfgFn": ["~m opExport"], "ArmoryCheck": ["~m packCheck", "~m packOf"],
          "CfgRows": ["~<clinit>", "~m header"],
          "SkyyArmoryPlugin": ["~m setup", "~m start", "~m publish", "~m unpublish", "~m systems"]}   # + armory:blinkland, clearLands, the leave hook


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    AT = JClass(PKG + "ArmoryTrav")
    Defs = JClass(PKG + "ArmoryDefs")
    UUID = JClass("java.util.UUID")
    Dbl, Lng, Bool = JClass("java.lang.Double"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    b = Defs.bridge()
    K.eq(str(AT.LAND_KEY), "armory:blink:", "X: LAND_KEY")
    K.eq(str(AT.ON_KEY), "armory:on:blink:", "X: ON_KEY")
    GOT = []

    @JImplements("java.util.function.Function")
    class L:
        def __init__(self, tag, boom=False):
            self.tag, self.boom = tag, boom

        @JOverride
        def apply(self, o):
            GOT.append((self.tag, [o[i] for i in range(len(o))]))
            if self.boom:
                raise RuntimeError("boom")
            return "ignored"
    b.put("armory:on:blink:SkyyClasses", L("cls"))
    b.put("armory:on:blink:Other", L("oth"))
    b.put("armory:on:blink:Boom", L("boom", True))
    b.put("armory:on:blink:NotAFn", "just a string")
    b.put("armory:on:blinkX", L("wrongprefix"))
    b.put("class:fn:heal", L("unrelated"))
    u = UUID.fromString("00000000-0000-0000-00ab-000000000001")
    l0, n0 = int(AT.LANDS), int(AT.LISTENED)
    n = int(AT.landed(u, None, 10.5, 65.0, -3.25, 1234567, 16.0, False))
    K.eq(n, 2, "X: landed -> 2 listeners ran cleanly (the throwing one is caught, the string / other keys skipped)")
    tags = sorted(t for t, _ in GOT)
    K.eq(tags, ["boom", "cls", "oth"], "X: exactly the armory:on:blink:* Functions were called, once each: %s" % tags)
    rec = b.get("armory:blink:" + str(u))
    K.check(rec is not None and len(rec) == 8, "X: armory:blink:<uuid> holds the 8-element record")
    vals = [rec[i] for i in range(8)]
    K.check(vals[0].equals(u) and vals[1] is None, "X: [0] the UUID, [1] the world name (null without a world)")
    K.check(isinstance(vals[2], Dbl) or str(vals[2].getClass().getName()) == "java.lang.Double", "X: [2] is a java.lang.Double")
    K.eq([float(vals[2]), float(vals[3]), float(vals[4])], [10.5, 65.0, -3.25], "X: x / y / z = the landing")
    K.eq(str(vals[5].getClass().getName()), "java.lang.Long", "X: [5] is a java.lang.Long")
    K.eq(int(vals[5]), 1234567, "X: [5] the time")
    K.eq(float(vals[6]), 16.0, "X: [6] blocks")
    K.eq(str(vals[7].getClass().getName()) + "=" + str(vals[7]).lower(), "java.lang.Boolean=false", "X: [7] Rift Echo flag")
    K.check(all(t_[1][0].equals(u) and float(t_[1][2]) == 10.5 for t_ in GOT), "X: every listener got the same record")
    K.eq(int(AT.LANDS) - l0, 1, "X: LANDS +1")
    K.eq(int(AT.LISTENED) - n0, 2, "X: LISTENED +2 (clean calls)")
    K.check("listeners=2" in str(AT.LAST_LAND), "X: LAST_LAND: " + str(AT.LAST_LAND))
    # a second blink overwrites the record (Rift Echo flag on)
    del GOT[:]
    AT.landed(u, None, 1.0, 2.0, 3.0, 99, 5.0, True)
    rec = b.get("armory:blink:" + str(u))
    K.eq([float(rec[2]), int(rec[5]), str(rec[7]).lower()], [1.0, 99, "true"], "X: the next blink overwrites the record (echo true)")
    # bad input
    K.eq(int(AT.landed(None, None, 1.0, 2.0, 3.0, 1, 1.0, False)), -1, "X: no UUID -> -1, nothing published")
    K.eq(int(AT.publishLand(None, JArray(JObject)(8))), -1, "X: no bridge -> -1")
    K.eq(int(AT.publishLand(b, JArray(JObject)(3))), -1, "X: a short record -> -1")
    K.eq(int(AT.publishLand(b, None)), -1, "X: no record -> -1")
    # no listeners at all = still published, 0 calls
    for k_ in ("armory:on:blink:SkyyClasses", "armory:on:blink:Other", "armory:on:blink:Boom", "armory:on:blink:NotAFn"):
        b.remove(k_)
    del GOT[:]
    u2 = UUID.fromString("00000000-0000-0000-00ab-000000000002")
    K.eq(int(AT.landed(u2, None, 0.0, 0.0, 0.0, 5, 1.0, False)), 0, "X: no listener -> 0 calls")
    K.check(b.get("armory:blink:" + str(u2)) is not None and not GOT, "X: ... the record is still there, nothing else called")
    # blink(): landed is called after the Teleport component was put and BLINKS counted (bytecode order)
    import zipfile
    with zipfile.ZipFile(jar) as z:
        raw = z.read("com/skyy/armory/ArmoryTrav.class")
    K.check(b"landed" in raw and b"armory:on:blink:" in raw, "X: ArmoryTrav carries the bridge")
    with zipfile.ZipFile(jar) as z:
        rp = z.read("com/skyy/armory/SkyyArmoryPlugin.class")
    K.check(b"armory:blinkland" in rp and b"PlayerDisconnectEvent" in rp and b"ArmoryQuit" in rp,
            "X: the plugin puts armory:blinkland (and unpublishes it) + registers the leave hook")
    # leave + shutdown: the records go
    b.put("armory:blink:" + str(u), "x")
    b.put("armory:blinkland", "1")
    K.eq(int(AT.forgetLand(u)), 1, "X: forgetLand removes that player's record")
    K.check(b.get("armory:blink:" + str(u)) is None and b.get("armory:blink:" + str(u2)) is not None, "X: ... only theirs")
    K.eq(int(AT.forgetLand(u)), 0, "X: ... a second time = 0")
    K.eq(int(AT.forgetLand(None)), 0, "X: forgetLand(null) = 0")
    AT.landed(u, None, 1.0, 1.0, 1.0, 1, 1.0, False)
    K.eq(int(AT.clearLands()), 2, "X: clearLands removes every armory:blink:<uuid> record (2)")
    K.check(b.get("armory:blinkland") is not None and b.get("armory:on:blinkX") is not None, "X: ... and nothing else")
    Q = JClass(PKG + "ArmoryQuit")()
    Q.accept(None)
    K.check(True, "X: ArmoryQuit.accept(null) does not throw")
    K.save()


def run_order(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    p_ = CPc(False)
    p_.appendSystemPath()
    p_.appendClassPath(B.SERVER_JAR)
    p_.appendClassPath(jar)
    c_ = p_.get(PKG + "ArmoryTrav")
    m_ = [x for x in c_.getDeclaredMethods() if str(x.getName()) == "blink"][0]
    mi = m_.getMethodInfo()
    it = mi.getCodeAttribute().iterator()
    cp = mi.getConstPool()
    seq = []
    while it.hasNext():
        pos = it.next()
        s_ = str(IP.instructionString(it, pos, cp))
        if "putComponent" in s_ or "ArmoryTrav.landed" in s_ or "BLINKS" in s_ and s_.startswith("putstatic"):
            seq.append("put" if "putComponent" in s_ else ("landed" if "landed" in s_ else "blinks"))
    K.eq(seq.count("landed"), 1, "O: blink calls landed exactly once: %s" % seq)
    K.check("put" in seq and "blinks" in seq and seq.index("landed") > seq.index("put") and seq.index("landed") > seq.index("blinks"),
            "O: ... after the Teleport is put and BLINKS counted (a refused blink returns earlier): %s" % seq)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.32")
    K.save()



# appended to both harnesses: the tier table v2 (Skyy-approved 15-step renumber, tools/tier_tags.py TT_VERSION 2) ships with these jars, so
# the lang file may differ from the old jar - but ONLY in the "T<n> <Material> - " tags at the start of descriptions
import re as _re
import zipfile


def _tier_only(old_jar, new_jar):
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(new_jar)
    n = "Server/Languages/en-US/server.lang"
    if n not in za.namelist() or n not in zb.namelist():
        return False, "no lang"
    a = za.read(n).decode("utf8").splitlines()
    b = zb.read(n).decode("utf8").splitlines()
    if len(a) != len(b):
        return False, "line count %d -> %d" % (len(a), len(b))
    strip = lambda l: _re.sub(r"= T\d+ ", "= T# ", l)
    bad = [i for i in range(len(a)) if a[i] != b[i] and strip(a[i]) != strip(b[i])]
    return not bad, "%d tier-tag lines changed, %d other lines%s" % (sum(1 for i in range(len(a)) if a[i] != b[i]) - len(bad), len(bad),
                                                                      (": " + b[bad[0]][:120]) if bad else "")


_eq0 = HK.Child.eq


def _eq(self, got, want, what):
    if what == "C: non-class entries changed" and got == ["Server/Languages/en-US/server.lang", "manifest.json"] and want == ["manifest.json"]:
        ok, why = _tier_only(OLD_JAR, JAR)
        self.notes.append("C: server.lang differs only by the tier table v2 tags: " + why)
        return self.check(ok, "C: non-class entries changed = manifest.json + server.lang tier tags only (%s)" % why)
    return _eq0(self, got, want, what)


HK.Child.eq = _eq


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ArmoryQuit"],
           phases=[("exec", run_exec), ("order", run_order), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
