"""Harness for SkyyCollections 0.2.30 (Balance P3: collection tier XP x the item's tier factor, tier.xpTierScale; tools/collections_0_2_30_patch.py).
Build first: python tools/collections_0_2_30_patch.py && python SkyyCollections/build_skyycollections_0.2.30.py

    python SkyyCollections/test_skyycollections_0.2.30.py [--jar <SkyyCollections-0.2.30.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.29 -> 0.2.30: RegData (+ tierScale), CollReg (+ TF table, tierF, xpAt, parseReg), the kit's row / version texts
  P3   EXECUTED CollReg.loadAll on a fresh folder + CollReg.xpAt (what every tier-up grant pays) on the REAL default registry: Wheat (T1) tier III
       500, Iron (T2) 1055, Adamantite (T10) 11295, Mithril's last tier 25000 x 36.23; an xp.route collection scaled too; rewards.properties
       xp: extras stay exact; tier.xpTierScale=false = the 0.2.29 numbers; a file without the line = true; an unknown (admin) collection x1
  LIVE CollReg.loadAll on a scratch COPY of the live Skyy_SkyyCollections (NewBetaTest), twice: no file changes, tierScale true
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.2.30", "0.2.29"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp3", "coll")))
PKG = "com.skyy.collections."
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the new row + the kit's version texts
          "CollReg": ["+f TF_F", "+f TF_ID", "+m tierF", "~<clinit>", "~m parseReg", "~m regText", "~m xpAt"],
          "CollTier": ["~<clinit>"],   # tools/tier_tags.py gained Tool_SkyyInfiniteWaterBucket (SkyyGear 0.3.31, 2026-10-20) after 0.2.29 was built
          "RegData": ["+f tierScale", "~c "],
          "SkyyCollectionsPlugin": ["~m setup"]}   # fix round: the ready line says 0.2.30
ADDED = []
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")


def snapd(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read()) for r, ds, fs in os.walk(d) for f in fs)


def grants(Reg, R, cid, t):
    c = [str(x) for x in R.id].index(cid)
    return [(str(g[0]), int(g[1])) for g in Reg.xpAt(R, c, t)]


def boot(base):
    from jpype import JClass
    Reg = JClass(PKG + "CollReg")
    JClass(PKG + "CollUtil").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCollTest")
    Reg.BASE = JClass("java.nio.file.Paths").get(base)
    JClass(PKG + "CollStore").DIR = Reg.BASE.resolve("counts")
    return Reg


def run_p3(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    base = os.path.join(scratch, "p3", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg = boot(base)
    Reg.loadAll()
    R = Reg.D
    K.check(R is not None and int(R.n) > 50 and bool(R.tierScale), "P3 the default registry loaded, tierScale on (%s collections)" % (None if R is None else int(R.n)))
    t = open(os.path.join(base, "collections.properties"), encoding="latin-1").read()
    K.check("\ntier.xpTierScale=true\n" in t, "P3 a fresh collections.properties carries tier.xpTierScale=true")
    mx = lambda cid: int(Reg.maxTier(R, [str(x) for x in R.id].index(cid)))
    K.eq(grants(Reg, R, "Wheat", 3), [("Farming", 500)], "P3 Wheat (T1) tier III 500 (x1)")
    K.eq(grants(Reg, R, "Iron", 3), [("Mining", 1055)], "P3 Iron (T2) tier III 500 x 2.11")
    K.eq(grants(Reg, R, "Adamantite", 3), [("Mining", 11295)], "P3 Adamantite (T10) tier III 500 x 22.59 (the spec's ~11,300)")
    K.eq(grants(Reg, R, "Mithril", mx("Mithril")), [("Mining", 905750)], "P3 Mithril (T13) last tier 25000 x 36.23")
    K.eq(grants(Reg, R, "Wheat", 2), [], "P3 a tier without tier XP stays without")
    routed = [c for c in [str(x) for x in R.id] if R.route is not None and R.route.get(c.lower()) is not None]
    K.check(len(routed) > 0, "P3 the default xp.route collections exist (%s)" % routed[:4])
    # tier.xpTierScale=false -> the 0.2.29 numbers; no line -> true
    t2 = t.replace("\ntier.xpTierScale=true\n", "\ntier.xpTierScale=false\n")
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(t2)
    Reg.loadAll()
    K.check(not bool(Reg.D.tierScale) and grants(Reg, Reg.D, "Adamantite", 3) == [("Mining", 500)] and grants(Reg, Reg.D, "Iron", 3) == [("Mining", 500)],
            "P3 tier.xpTierScale=false: the flat 0.2.29 numbers")
    open(os.path.join(base, "collections.properties"), "w", encoding="latin-1", newline="\n").write(t.replace("\ntier.xpTierScale=true\n", "\n"))
    Reg.loadAll()
    K.check(bool(Reg.D.tierScale) and grants(Reg, Reg.D, "Iron", 3) == [("Mining", 1055)], "P3 a file without the line (0.2.29) reads true")
    K.check(float(Reg.tierF("NoSuchCollection")) == 1.0 and float(Reg.tierF("onyxium")) == 53.07 and float(Reg.tierF("SEEDS")) == 1.0,
            "P3 tierF: unknown x1, Onyxium x53.07, the mixed Seeds collection x1 (case-insensitive)")
    import zipfile   # fix round: the ready line names 0.2.30 (the smoke test needs '[SkyyCollections] 0.2.30 ready')
    zb = zipfile.ZipFile(jar)
    rd = [n for n in zb.namelist() if n.endswith(".class") and b"[SkyyCollections] 0.2.30 ready (" in zb.read(n)]
    old = [n for n in zb.namelist() if n.endswith(".class") and b"[SkyyCollections] 0.2.29 ready" in zb.read(n)]
    K.check(len(rd) == 1 and not old, "fix: the ready line says 0.2.30 (%s; old %s)" % (rd, old))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Reg = boot(home)
    s0 = snapd(home)
    Reg.loadAll()
    s1 = snapd(home)
    Reg.loadAll()
    s2 = snapd(home)
    K.check(Reg.D is not None and bool(Reg.D.tierScale), "LIVE the live registry loads, tierScale on (no line = true)")
    K.check(s0 == s1 == s2, "LIVE loading twice changes no file: %s" % sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))[:6])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("p3", run_p3), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
