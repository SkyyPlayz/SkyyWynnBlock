"""Harness for SkyyGear 0.3.42 (gear042: Breaking Speed on the hoe / sickle / Harvester, published as gear:swing:harvest:<uuid> for SkyyTrees 0.5.2 -
tools/gear_0_3_42_patch.py).
Build first:
    python tools/gear_0_3_42_patch.py && python SkyyGear/build_skyygear_0.3.42.py
    python SkyyGear/test_skyygear_0.3.42.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the non-class jar entries = 0.3.41's
              except the manifest (no art / item / lang change)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.41 -> 0.3.42 (EXPECT below)
  X  exec     EXECUTES in a bare JVM (bridge map, a registry Properties in GearLL.REG, stand-in ItemStacks with a lifelong gear document):
              the swing line belongs to pickaxe / hatchet / hoe / sickle (not pole / can); every Harvester id (the 25 ids in the jar) + the hoes are
              family 4 / 5 and kind 2 / 3; harvOf / harvSwing = level x lifelong.perkSwing inside the 10 x tier cap, 0 for another player's /
              a non-lifelong / a retired tool; swingPost with a Harvester -> gear:swing:harvest:<uuid> = line + Farming armor, gear:swing:<uuid>
              absent; with the pickaxe / hatchet / multitool -> gear:swing:<uuid> = exactly the 0.3.41 numbers (line + Mining / Foraging armor),
              harvest key absent; 0 -> both removed; forget removes both; the reader gate (swing.harvest); the Upgrade row text; the
              tooltip line (green #7ee08a) on your Harvester, none on someone else's
  D  live     start TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: the second start changes nothing, no row written
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the swing itself getting faster on crops (that is SkyyTrees 0.5.2's effect), the tooltip / Upgrade page look.
Scratch: tools/dev/scratch/gear042/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.42"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear042", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.41.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_42_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.41.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = []
EXPECT = {
    "GearCfg": ["~m defaultsText"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "CfgFn": ["~m opExport"],          # the version text
    "GearDefs": ["+f C_UP"],
    "GearLL": ["+m harvOf", "+m harvSwing", "+m readerHas", "+m swingPut", "~<clinit>", "~m perkOn2", "~m swingPost"],
    "GearTool": ["~m forget", "~m lines"],
    "LifePage": ["~m effect"],
    "SkyyGearPlugin": ["~m setup", "~m start"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.42 - build script') and g.count('VERSION = "0.3.42"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S no entry added / removed")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is the manifest (no art / item / lang / config file)")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JInt, JString
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, LL, Tool, Data, Defs, GArm, LP = P("GearCfg"), P("GearLL"), P("GearTool"), P("GearData"), P("GearDefs"), P("GearGArm"), P("LifePage")
    UUID, Props, AL = JClass("java.util.UUID"), JClass("java.util.Properties"), JClass("java.util.ArrayList")
    BD, BS, BI = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32")
    SW = int(LL.PK_SWING)
    K.check(bool(Cfg.LL_ON) and abs(float(Cfg.LL_PSWING) - 3.0) < 1e-12, "X setup: lifelong tools on, lifelong.perkSwing 3 (default)")
    K.eq([bool(LL.perkFor(k, SW)) for k in range(6)], [True, True, True, True, False, False], "X the Breaking Speed line: pickaxe, hatchet, hoe, sickle (Harvester); not pole / can")
    K.eq(int(LL.PKMASK[SW]), 15, "X PKMASK swing = 1|2|4|8")
    # ---- every Harvester id in the jar + the hoes
    z = zipfile.ZipFile(jar)
    harv = sorted(set(n.rsplit("/", 1)[1][:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.rsplit("/", 1)[1].startswith("Tool_Sickle_Harvester_") and n.endswith(".json")))
    harv = sorted(set(harv) | set(str(LL.HARV_LAD).split(",")))
    K.check(len(harv) >= 16, "X %d Harvester ids found (jar items + GearLL.HARV_LAD): %s" % (len(harv), harv[:4]))
    K.notes.append("X Harvester ids: %d (%s)" % (len(harv), ", ".join(harv)))
    bad = [i for i in harv if not (int(Data.toolFam(JString(i))) == 5 and int(LL.kOf(JString(i))) == 3 and bool(LL.harv(JString(i))))]
    K.eq(bad, [], "X every Harvester id = family 5 (sickle), kind 3, harv()")
    hoes = ["Tool_Hoe_Crude", "Tool_Hoe_Copper", "Tool_Hoe_Iron", "Tool_Hoe_Thorium"]
    K.eq([(int(Data.toolFam(JString(i))), int(LL.kOf(JString(i)))) for i in hoes], [(4, 2)] * 4, "X the hoes: family 4, kind 2")

    u = UUID.fromString("00000000-0000-0000-0000-00000000a042")
    other = UUID.fromString("00000000-0000-0000-0000-00000000b042")
    pk = str(u)
    R = Props()
    for k_, v_ in (("sickle.id", "Tool_Sickle_Harvester_Iron"), ("sickle.up.swing", "7"), ("pickaxe.id", "Tool_Pickaxe_Copper"), ("pickaxe.up.swing", "5"),
                   ("hatchet.id", "Tool_Hatchet_Iron"), ("hatchet.up.swing", "4")):
        R.setProperty(k_, v_)
    LL.REG.put(pk, R)

    def doc(owner=pk, rt=0, ll=1):
        g_ = BD()
        g_.put("ll", BI(ll))
        g_.put("lo", BS(owner))
        if rt:
            g_.put("lrt", BI(1))
        return g_
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    un = fu.get(None)
    fl = dict((str(f.getName()), f) for f in IS.class_.getDeclaredFields())
    K.check("metadata" in fl, "X ItemStack has a metadata field (%s)" % sorted(fl))

    def stack(iid, gd):
        s_ = un.allocateInstance(IS.class_)
        md = BD()
        if gd is not None:
            md.put(str(Defs.DOC_KEY), gd)
        for n_, v_ in (("itemId", JString(iid)), ("quantity", JInt(1)), ("metadata", md)):
            fl[n_].setAccessible(True)
            fl[n_].set(s_, v_)
        return s_
    HV = "Tool_Sickle_Harvester_Iron"
    hs = stack(HV, doc())
    K.check(str(hs.getItemId()) == HV and not bool(hs.isEmpty()) and Data.gearDoc(hs.getMetadata()) is not None, "X stand-in Harvester stack with a lifelong document")
    K.check(abs(float(LL.harvOf(u, JString(HV), doc())) - 21.0) < 1e-9, "X harvOf: Breaking Speed 7 on your Iron Harvester = 21 %")
    K.check(abs(float(LL.harvSwing(u, hs)) - 21.0) < 1e-9, "X harvSwing (the stack) = 21 %")
    R.setProperty("sickle.up.swing", "45")
    K.check(abs(float(LL.harvOf(u, JString(HV), doc())) - 90.0) < 1e-9, "X 45 saved on an Iron Harvester work at the 30 cap (10 x tier) = 90 %")
    R.setProperty("sickle.up.swing", "7")
    K.eq([float(LL.harvOf(u, JString(HV), doc(owner=str(other)))), float(LL.harvOf(u, JString(HV), doc(rt=1))), float(LL.harvOf(u, JString(HV), doc(ll=0))),
          float(LL.harvOf(u, JString(HV), None)), float(LL.harvOf(u, JString("Tool_Pickaxe_Copper"), doc())), float(LL.harvOf(None, JString(HV), doc()))],
         [0.0] * 6, "X harvOf 0: another player's / retired / not lifelong / no document / a pickaxe / no player")
    R.setProperty("hoe.id", "Tool_Hoe_Copper")
    R.setProperty("hoe.up.swing", "3")
    K.check(abs(float(LL.harvOf(u, JString("Tool_Hoe_Copper"), doc())) - 9.0) < 1e-9, "X a (pre-merge) lifelong hoe: its own hoe.up.swing 3 = 9 %")
    # ---- swingPost: the two keys
    KS, KH = "gear:swing:" + pk, "gear:swing:harvest:" + pk
    LL.swingPost(u, hs)
    K.eq((br.get(KS), None if br.get(KH) is None else float(br.get(KH))), (None, 21.0), "X a Harvester in hand: gear:swing:harvest:<uuid> = 21.0 (Double, %), gear:swing:<uuid> absent")
    K.check(isinstance(br.get(KH), JClass("java.lang.Double")) or str(br.get(KH).getClass().getName()) == "java.lang.Double", "X the value is a java.lang.Double")
    arm = JClass("double[]")(14)
    arm[11], arm[12], arm[13] = 6.0, 8.0, 10.0
    GArm.ARM.put(u, arm)
    LL.swingPost(u, hs)
    K.eq(float(br.get(KH)), 31.0, "X + the worn Farming armor (10 %) = 31.0")
    ps = stack("Tool_Pickaxe_Copper", doc())
    LL.swingPost(u, ps)
    K.eq((float(br.get(KS)), br.get(KH)), (15.0 + 6.0, None), "X the pickaxe: gear:swing:<uuid> = line 15 + Mining armor 6 (0.3.41's numbers), harvest key removed")
    K.eq(float(LL.swingOf(u, ps)), 15.0, "X swingOf (pickaxe) unchanged: 5 x 3")
    hts = stack("Tool_Hatchet_Iron", doc())
    LL.swingPost(u, hts)
    K.eq((float(br.get(KS)), br.get(KH)), (12.0 + 8.0, None), "X the hatchet: gear:swing:<uuid> = line 12 + Foraging armor 8, harvest key absent")
    LL.swingPost(u, stack("Tool_Shovel_Iron", None))
    K.eq((float(br.get(KS)), br.get(KH)), (6.0, None), "X a plain shovel: the Mining armor 6 as in 0.3.41")
    LL.swingPost(u, stack("Tool_Hoe_Iron", None))
    K.eq((br.get(KS), float(br.get(KH))), (None, 10.0), "X a plain (not lifelong) hoe: only the Farming armor 10 on the harvest key")
    GArm.ARM.remove(u)
    LL.swingPost(u, stack("Tool_Hoe_Iron", None))
    K.eq((br.get(KS), br.get(KH)), (None, None), "X a plain hoe, no armor: both keys absent")
    LL.swingPost(u, hs)
    LL.swingPost(u, None)
    K.eq((br.get(KS), br.get(KH)), (None, None), "X an empty hand: both removed")
    LL.swingPost(u, hs)
    Tool.forget(u)
    Tool.back(u)
    K.eq(br.get(KH), None, "X GearTool.forget (leave) removes the harvest key")
    # ---- the reader gate
    br.put("gear:perk:readers", "vein,fell,swing")
    K.eq([bool(LL.perkOn2(k, SW)) for k in range(4)], [True, True, False, False], "X SkyyTrees 0.5.1 readers (vein,fell,swing): pickaxe / hatchet buy, hoe / Harvester wait")
    br.put("gear:perk:readers", "vein,fell,swing,swing.harvest")
    K.eq([bool(LL.perkOn2(k, SW)) for k in range(4)], [True, True, True, True], "X with swing.harvest (SkyyTrees 0.5.2): all four")
    br.put("gear:perk:readers", "swing.harvest")
    K.eq([bool(LL.perkOn2(k, SW)) for k in range(4)], [False, False, False, False], "X swing.harvest alone is not enough (swing too)")
    K.check(bool(LL.perkOn2(3, 1)) and bool(LL.perkOn2(3, 2)), "X the Harvester's Fortune / Wisdom gates unchanged")
    br.remove("gear:perk:readers")
    K.eq([str(LP.effect(k, SW, 4)) for k in range(4)], ["+12% swing speed", "+12% swing speed", "+12% swing speed on crops", "+12% swing speed on crops"],
         "X the Upgrade row text")
    # ---- the tooltip line
    txt, col = AL(), AL()
    Tool.lines(u, JString(HV), doc(), txt, col)
    tl = [(str(txt.get(i)), None if col.get(i) is None else str(col.get(i))) for i in range(txt.size())]
    K.notes.append("X Harvester tooltip lines: %s" % tl)
    hit = [c for t, c in tl if t == "Breaking Speed +21% - swings faster on crops"]
    K.eq(hit, ["#7ee08a"], "X your Harvester's tooltip: 'Breaking Speed +21% - swings faster on crops' in green #7ee08a")
    K.check(any(t.startswith("Upgrades: ") and "Breaking Speed 7" in t for t, c in tl), "X ... and 'Upgrades: ... Breaking Speed 7'")
    txt2, col2 = AL(), AL()
    Tool.lines(u, JString(HV), doc(owner=str(other)), txt2, col2)
    K.check(not [str(t) for t in txt2 if "swings faster" in str(t)], "X another player's Harvester: no Breaking Speed line")
    txt3, col3 = AL(), AL()
    Tool.lines(u, JString("Tool_Pickaxe_Copper"), doc(), txt3, col3)
    K.check(not [str(t) for t in txt3 if "swings faster" in str(t)], "X the pickaxe tooltip: no crop line (unchanged)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]
    before = open(fc, "rb").read()
    t0 = HK.tree_hash(home)
    m1 = [str(getattr(Cfg, m)()) for m in MIG]
    Cfg.load()
    t1 = HK.tree_hash(home)
    m2 = "".join(str(getattr(Cfg, m)()) for m in MIG)
    Cfg.load()
    t2 = HK.tree_hash(home)
    K.notes.append("D start 1 on the live copy: %s" % [x[:160] for x in m1 if x])
    K.check(m2 == "" and t1 == t2, "D start 2: nothing changes (%r)" % m2[:120])
    txt = open(fc, "rb").read().decode("latin-1")
    K.check((b"\r\n" in before) == ("\r\n" in txt), "D line endings kept")
    K.check("0.3.42" not in txt and "swing.harvest" not in txt, "D 0.3.42 writes no row of its own (no migration)")
    K.notes.append("D files changed by start 1 (older rounds' one-time updates the live world has not run yet): %s" % sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))[:8])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
