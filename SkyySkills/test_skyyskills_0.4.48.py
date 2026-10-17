"""SkyySkills 0.4.48 - harness for round T1, the SkyySkills part: TOOL FORTUNE UNCAPPED (tools/skills_0_4_48_patch.py).
Build first: python tools/skills_0_4_48_patch.py && python SkyySkills/build_skyyskills_0.4.48.py

    python SkyySkills/test_skyyskills_0.4.48.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.47 -> 0.4.48: + Fm48Mig; only the planned members of Perks / PerkCfg / Sickle / the version texts / the default file
  FO  Perks.extras at many totals (guard 100 / 5), Perks.fortune (perk.fortuneMax 0 = uncapped, 2.0 = capped, doubleDropMax < 1 = hard
      cap), PerkCfg.read (default 0 / 100, no clamp at 10, the guard 1..10000), qtyN / splitQ / bulk / timesN on real ItemStacks;
      bytecode: breakDouble / harvestDouble / Sickle.award = n 1 the old call, n >= 2 ONE doubled() with bulk(...N); breakDropsN rolls
      getDrops with qtyN(q, n); setup runs Fm48Mig after Pd44Mig and before SkillCfg.load
  MG  Fm48Mig.plan (2.0 / 2 -> 0; 3.5 kept + INFO; continued entry, LAST entry decides, marker = run once, CRLF kept) and Fm48Mig.run
      end to end on scratch files: History copy + change-log row + marker, second run nothing, hand-edited 3.5 kept, a fresh default
      file untouched, CRLF bytes kept
  LIVE48  every one-time update in setup() order + SkillCfg.load, twice, 0.4.47 vs 0.4.48, each on its own scratch COPY of the live data
  PK / PG  0.4.47's asset-pack + page phases on this jar (skip with --no-old)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.48"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.47.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "t1skills", "h")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")   # read only - HK.run copies it into scratch
ADDED = ["Fm48Mig"]
EXPECT = {"Perks": ["+m breakDropsN", "+m bulk", "+m harvestDropsN", "+m maxStack", "+m qtyN", "+m splitQ", "+m timesN",
                    "~m breakDouble", "~m extras", "~m fortune", "~m harvestDouble"],
          "PerkCfg": ["+f GUARD", "~<clinit>", "~m ensureDefaults", "~m read"],   # ensureDefaults: the inlined DEFAULTS text
          "Sickle": ["~m award"],
          "CfgFile": ["~<clinit>"], "SkillCfg": ["~m load"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "CfgRows": ["~<clinit>", "~m header"],
          "CfgFn": ["~m opExport"], "SkyySkillsPlugin": ["~m setup"]}
OLD_MIGS = ["ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig", "PerkMig", "PollMig", "RbCoinMig", "Pd44Mig"]


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def loader_for(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def jpath(p):
    from jpype import JClass
    return JClass("java.nio.file.Paths").get(p, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))


def _unsafe():
    from jpype import JClass
    f = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    f.setAccessible(True)
    return f.get(None)


def _setf(obj, name, val, cls=None):
    """set a (private / final-static) field by reflection, searching the class hierarchy"""
    c = cls if cls is not None else obj.getClass()
    while c is not None:
        for f in c.getDeclaredFields():
            if str(f.getName()) == name:
                f.setAccessible(True)
                f.set(obj, val)
                return
        c = c.getSuperclass()
    raise RuntimeError("no field " + name)


def _code(cls_name, meth, jar, pos=False):
    """javassist instruction lines of one method (all overloads) of the jar (pos: (offset, line) pairs)"""
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    out = []
    for m in cp.get(cls_name).getDeclaredMethods():
        if str(m.getName()) != meth:
            continue
        mi = m.getMethodInfo()
        it = mi.getCodeAttribute().iterator()
        while it.hasNext():
            pos_ = it.next()
            out.append((int(pos_), str(IP.instructionString(it, pos_, mi.getConstPool()))) if pos else str(IP.instructionString(it, pos_, mi.getConstPool())))
    return out


# ============================================================================================ FO: Fortune maths + bulk drops (pure)
def run_fo(out, jar, scratch, _home):
    from jpype import JClass, JDouble, JInt, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Perks, PCfg, Cfg, Sto, Defs, BCfg = J("Perks"), J("PerkCfg"), J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("BridgeCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Props, UUID = JClass("java.util.Properties"), JClass("java.util.UUID")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    # ---- T1 critic note: Fortune's extra drops never count in Collections by default (no collection tool points from skills:double)
    FCfg = J("FellCfg")
    FCfg.read(Props()) if hasattr(FCfg, "read") else None
    K.check(not bool(FCfg.DD_COLLECTIONS), "FO: collections.doubleDrops stays OFF by default (extra drops never raise collection tool points)")
    # ---- PerkCfg.read
    PCfg.read(Props())
    K.check(float(PCfg.FORT_MAX) == 0.0 and int(PCfg.GUARD) == 100 and float(PCfg.DD_MAX) == 1.0, "FO read: defaults fortuneMax 0 (no cap), guard 100, doubleDropMax 1")
    for txt, want_f, want_g in (("12.5", 12.5, None), ("1000", 1000.0, None), ("2.0", 2.0, None), ("-3", 0.0, None), ("abc", 0.0, None)):
        p = Props()
        p.setProperty("perk.fortuneMax", txt)
        PCfg.read(p)
        K.eq(float(PCfg.FORT_MAX), want_f, "FO read: perk.fortuneMax=%s (no clamp at 10; bad / negative = 0)" % txt)
    for txt, want in (("0", 1), ("1", 1), ("250", 250), ("10000", 10000), ("99999", 10000), ("-5", 1), ("x", 100)):
        p = Props()
        p.setProperty("perk.fortuneGuard", txt)
        PCfg.read(p)
        K.eq(int(PCfg.GUARD), want, "FO read: perk.fortuneGuard=%s -> 1..10000" % txt)
    PCfg.read(Props())
    # ---- extras
    E = lambda t, r: int(Perks.extras(JDouble(t), JDouble(r)))
    cases = [((0.0, 0.0), 0), ((0.4, 0.39), 1), ((0.4, 0.4), 0), ((1.0, 0.0), 1), ((1.0, 0.999), 1), ((1.5, 0.2), 2), ((1.5, 0.7), 1),
             ((2.0, 0.0), 2), ((2.0, 0.999), 2), ((2.5, 0.49), 3), ((2.5, 0.5), 2), ((10.0, 0.5), 10), ((10.5, 0.1), 11), ((37.5, 0.2), 38),
             ((37.5, 0.6), 37), ((99.5, 0.9), 99), ((99.5, 0.1), 100), ((100.0, 0.0), 100), ((150.0, 0.1), 100), ((float("inf"), 0.1), 100),
             ((float("nan"), 0.1), 0), ((-1.0, 0.0), 0)]
    got = [(c, E(*c)) for c, _w in cases]
    K.check(all(g == w for (c, g), (_c, w) in zip(got, cases)), "FO extras (whole part sure, the rest a chance; 2.0 = always 2 extras = 3 drops; guard 100): %s"
            % [(c, g, w) for (c, g), (_c, w) in zip(got, cases) if g != w])
    PCfg.GUARD = 5
    K.check(E(37.5, 0.1) == 5 and E(4.5, 0.1) == 5 and E(4.5, 0.9) == 4, "FO extras: perk.fortuneGuard 5 clamps (37.5 -> 5)")
    PCfg.GUARD = 100
    # ---- fortune (the skill:bonus bridge: source gear = SkyyGear's tool Fortune)
    bridge = Sto.bridge()
    BCfg.BONUS = True
    u = UUID(0x448, 1)
    FOR = int(Defs.FARMING) - 1
    key = "skill:bonus:" + str(u)
    CHM, HM = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap")

    def srcs(**kw):
        bridge.remove(key)
        m = CHM()
        for k, v in kw.items():
            hm = HM()
            for kk, vv in v.items():
                hm.put(kk, JClass("java.lang.Double")(vv))
            m.put(k, JClass("java.util.Collections").unmodifiableMap(hm))
        bridge.put(key, m)

    fo = lambda lvl=0: round(float(Perks.fortune(u, JInt(FOR), JInt(lvl))), 9)
    srcs(gear={"dd.foraging": 3.0})
    K.eq(fo(), 3.0, "FO fortune: fortuneMax 0 = uncapped (gear 3.0 -> 3.0)")
    srcs(gear={"dd.foraging": 37.5})
    K.eq(fo(), 37.5, "FO fortune: uncapped 37.5")
    srcs(gear={"dd.foraging": 1.5}, trees={"dd.foraging": 0.8})
    K.eq(fo(100), 2.5, "FO fortune: base min(0.5 + 0.8, 1.0) + gear 1.5 = 2.5 (0.4.47 capped it at 2.0)")
    PCfg.FORT_MAX = 2.0
    srcs(gear={"dd.foraging": 3.0})
    K.eq(fo(), 2.0, "FO fortune: an admin's fortuneMax 2.0 still caps (3.0 -> 2.0)")
    PCfg.FORT_MAX = 12.0
    srcs(gear={"dd.foraging": 30.0})
    K.eq(fo(), 12.0, "FO fortune: fortuneMax 12 caps above the old clamp of 10")
    PCfg.FORT_MAX = 0.0
    PCfg.DD_MAX = 0.5
    srcs(gear={"dd.foraging": 3.0})
    K.eq(fo(), 0.5, "FO fortune: doubleDropMax 0.5 (< 1) stays a hard cap for tool Fortune, fortuneMax 0 or not")
    PCfg.FORT_MAX = 2.0
    K.eq(fo(), 0.5, "FO fortune: doubleDropMax 0.5 with fortuneMax 2.0 -> 0.5")
    PCfg.DD_MAX = 1.0
    PCfg.FORT_MAX = 0.0
    srcs(gear={"dd.foraging": 0.5}, trees={"dd.foraging": 0.3})
    K.eq(fo(40), 1.0, "FO fortune: base 0.2 + 0.3 + gear 0.5 = 1.0 (always 2 drops)")
    srcs()
    K.eq(fo(40), 0.2, "FO fortune: no tool = the level chance only (0.2 at 40)")
    bridge.remove(key)
    # ---- the bulk drops
    K.eq(int(Perks.qtyN(JInt(3), JInt(5))), 15, "FO qtyN 3 x 5")
    K.eq(int(Perks.qtyN(JInt(2000000000), JInt(10000))), 1000000, "FO qtyN overflow-safe: at most 1000000")
    K.eq(int(Perks.qtyN(JInt(0), JInt(5))) + int(Perks.qtyN(JInt(4), JInt(0))), 0, "FO qtyN 0 / 0")
    sp = lambda q, m: [int(x) for x in Perks.splitQ(JLong(q), JInt(m))]
    K.eq(sp(250, 100), [100, 100, 50], "FO splitQ 250 of a max-100 item -> 100, 100, 50")
    K.eq(sp(100, 100), [100], "FO splitQ 100 / 100 -> one stack")
    K.eq(sp(5, 64), [5], "FO splitQ 5 / 64")
    K.eq(sp(0, 64), [], "FO splitQ 0 -> none")
    K.eq(sp(130, 0), [64, 64, 2], "FO splitQ max unknown (0) -> 64")
    K.eq(len(sp(1000000, 1)), 1000000, "FO splitQ 1000000 / 1 (the qtyN ceiling)")
    # ItemStack(id, n) needs the Item store: a stand-in HytaleAssetStore (allocated, no constructor) over a DefaultAssetMap holding ONE
    # stand-in Item "Skyy_Test_Max100" with maxStack 100 (every other id -> Item.UNKNOWN; the 0.4.26 harness way)
    U = _unsafe()
    HM2 = JClass("java.util.HashMap")
    am = U.allocateInstance(JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_)
    amap = HM2()
    _setf(am, "assetMap", amap)
    _setf(am, "assetMapLock", JClass("java.util.concurrent.locks.StampedLock")())
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    fas = cp.makeClass("skyytest.FakeAssetStore48")   # a concrete AssetStore (the 0.4.15 harness's FakeAssetStore)
    fas.setSuperclass(cp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fas.addConstructor(JClass("javassist.CtNewConstructor").make("public FakeAssetStore48() { super(null); }", fas))
    fdir = os.path.join(scratch, "fake48")
    fas.writeFile(fdir)
    ua = JClass("java.lang.reflect.Array").newInstance(JClass("java.net.URL").class_, 1)
    ua[0] = JClass("java.io.File")(fdir).toURI().toURL()
    FL = JClass("java.net.URLClassLoader")(ua, JClass("java.lang.ClassLoader").getSystemClassLoader())
    st_ = U.allocateInstance(JClass("java.lang.Class").forName("skyytest.FakeAssetStore48", False, FL))
    _setf(st_, "assetMap", am)
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    _setf(None, "ASSET_STORE", st_, ITM.class_)
    it100 = U.allocateInstance(ITM.class_)
    _setf(it100, "id", JString("Skyy_Test_Max100"))
    _setf(it100, "maxStack", JInt(100))
    amap.put(JString("Skyy_Test_Max100"), it100)
    AL = JClass("java.util.ArrayList")
    l = AL()
    l.add(IS(JString("Skyy_Test_Max100"), JInt(250)))
    K.eq(int(Perks.maxStack(l.get(0))), 100, "FO maxStack = the item's getMaxStack (100)")
    K.eq([(str(s.getItemId()), int(s.getQuantity())) for s in Perks.bulk(l)], [("Skyy_Test_Max100", 100), ("Skyy_Test_Max100", 100), ("Skyy_Test_Max100", 50)],
         "FO bulk: a stack of 250 of a max-100 item -> 100, 100, 50")
    unk = IS(JString("Ore_Iron"), JInt(1))
    mu = int(Perks.maxStack(unk))
    K.notes.append("FO maxStack(an unknown id = Item.UNKNOWN) = %d" % mu)
    K.check(mu >= 1, "FO maxStack never below 1 (unknown / 0 -> 64)")
    K.eq(int(Perks.maxStack(None)), 64, "FO maxStack(null) = 64")
    l2 = AL()
    for _i in range(5):
        l2.add(IS(JString("Plant_Crop_Wheat_Item"), JInt(1)))
    l2.add(IS(JString("Plant_Seeds_Wheat"), JInt(2)))
    l2.add(IS(JString("Plant_Crop_Wheat_Item"), JInt(3)))
    l2.add(JString("not a stack"))
    b2 = [(str(s.getItemId()), int(s.getQuantity())) for s in Perks.bulk(l2)]
    K.eq(b2, [("Plant_Crop_Wheat_Item", 8), ("Plant_Seeds_Wheat", 2)], "FO bulk: a drop list rolled n times (5 x 1 + 3 wheat, 2 seeds) -> ONE stack per kind (stackable merged)")
    K.check(Perks.bulk(None) is None and int(Perks.bulk(AL()).size()) == 0, "FO bulk: null -> null, empty -> empty")
    t = Perks.timesN(l2, JInt(4))
    K.eq([(str(s.getItemId()), int(s.getQuantity())) for s in t], [("Plant_Crop_Wheat_Item", 4)] * 5 + [("Plant_Seeds_Wheat", 8), ("Plant_Crop_Wheat_Item", 12)],
         "FO timesN (the sickle's copies x n, fresh stacks)")
    # ---- bytecode: the call shape
    for meth, nn in (("breakDouble", "breakDrops"), ("harvestDouble", "harvestDrops")):
        c = _code(PKG + "Perks", meth, jar)
        calls = [x for x in c if "invokestatic" in x and "Perks." in x]
        names = [x.split("Perks.")[1].split("(")[0] for x in calls]
        K.check(names.count("doubled") == 2 and names.count(nn) == 1 and names.count(nn + "N") == 1 and names.count("bulk") == 1,
                "FO %s: n 1 = doubled(%s) as before, n >= 2 = ONE doubled(bulk(%sN)): %s" % (meth, nn, nn, names))
        # no backward jump = no loop
        back = []
        for pos, x in _code(PKG + "Perks", meth, jar, pos=True):
            parts = x.split()
            if parts and (parts[0].startswith("goto") or parts[0].startswith("if")) and parts[-1].isdigit() and int(parts[-1]) <= pos:
                back.append("%d: %s" % (pos, x))
        K.check(not back, "FO %s: no loop any more (%s)" % (meth, back))
    bd = _code(PKG + "Perks", "breakDropsN", jar)
    K.check(sum(1 for x in bd if "BlockHarvestUtils.getDrops" in x) == 2 and sum(1 for x in bd if "Perks.qtyN" in x) == 2,
            "FO breakDropsN: the engine's getDrops with qtyN(q, n) (soft + breaking)")
    hd = _code(PKG + "Perks", "harvestDropsN", jar)
    K.check(sum(1 for x in hd if "BlockHarvestUtils.getDrops" in x) == 1 and any("Perks.qtyN" in x for x in hd), "FO harvestDropsN: getDrops with qtyN(1, n)")
    sa = _code(PKG + "Sickle", "award", jar)
    K.check(any("Perks.timesN" in x for x in sa) and any("Perks.bulk" in x for x in sa) and sum(1 for x in sa if "Perks.doubled" in x) == 2,
            "FO Sickle.award: fx 1 = copies as before, fx >= 2 = ONE doubled(bulk(timesN))")
    st = [x for x in _code(PKG + "SkyySkillsPlugin", "setup", jar) if "invokestatic" in x]
    ix = lambda s: [i for i, x in enumerate(st) if s in x]
    a, b_, c_ = ix("Pd44Mig.run"), ix("Fm48Mig.run"), ix("SkillCfg.load")
    K.check(len(a) == len(b_) == 1 and c_ and a[0] < b_[0] < c_[0], "FO setup: Pd44Mig.run -> Fm48Mig.run -> SkillCfg.load")
    # ---- the default file + the rows
    D = str(Cfg.DEFAULTS)
    K.check("\nperk.fortuneMax=0\n" in D and "\nperk.fortuneGuard=100\n" in D and D.count(str(J("Fm48Mig").MARK_ID)) == 1 and "perk.fortuneMax=2.0" not in D,
            "FO the fresh xp.properties: fortuneMax=0, fortuneGuard=100, the Fm48Mig marker")
    Rows = J("CfgRows")
    keys = [str(x) for x in Rows.KEYS]
    i = keys.index("perk.fortuneMax")
    K.check(keys[i + 1] == "perk.fortuneGuard" and str(Rows.DEFS[i]) == "0" and str(Rows.DEFS[i + 1]) == "100", "FO rows: fortuneMax (default 0) + fortuneGuard (100) next to it")
    K.notes.append("rows: %s | %s" % ([str(Rows.LABELS[i]), str(Rows.HELPS[i])], [str(Rows.LABELS[i + 1]), str(Rows.HELPS[i + 1])]))
    K.save()


# ============================================================================================ MG: Fm48Mig
def run_mg(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    M, Cfg, Hist, CLog, Rows, PCfg = J("Fm48Mig"), J("SkillCfg"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("PerkCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    S = lambda x: JString(x)
    MARK = str(M.MARK)
    # ---- plan (pure)
    for old in ("2.0", "2"):
        t1 = "a=1\nperk.fortuneMax=%s\nperk.doubleDropMax=1.0\n" % old
        r = M.plan(S(t1))
        body = str(r[0])
        K.check(body == "a=1\nperk.fortuneMax=0\nperk.doubleDropMax=1.0\n" + MARK + "\n", "MG plan: untouched %s -> 0, marker at the end" % old)
        K.eq([str(x) for x in r[1]], ["perk.fortuneMax", old, "0"], "MG plan: the change-log row (old %s)" % old)
        K.check(bool(M.sameAfter(JString(t1).getBytes("ISO-8859-1"), JString(body).getBytes("ISO-8859-1"), r[2])), "MG sameAfter accepts the plan (%s)" % old)
    K.check(not bool(M.sameAfter(JString(t1).getBytes("ISO-8859-1"), JString(body.replace("a=1", "a=2")).getBytes("ISO-8859-1"), r[2])), "MG sameAfter refuses another changed key (control)")
    r = M.plan(S("perk.fortuneMax=3.5\n"))
    K.check(str(r[0]) == "perk.fortuneMax=3.5\n" + MARK + "\n" and len(r[1]) == 0 and "perk.fortuneMax=3.5 kept" in str(r[3]), "MG plan: an admin's 3.5 kept (INFO): %s" % str(r[3]))
    r = M.plan(S("perk.fortuneMax = 2.0 \n"))
    K.check(len(r[1]) == 3 and str(r[0]).startswith("perk.fortuneMax = 0\n"), "MG plan: spaces around the value: %r" % str(r[0])[:40])
    r = M.plan(S("a=1\n"))
    K.check(str(r[0]) == "a=1\n" + MARK + "\n" and len(r[1]) == 0, "MG plan: no line -> only the marker (the new code default 0 applies)")
    K.check(M.plan(S("a=1\n" + MARK + "\nperk.fortuneMax=2.0\n")) is None, "MG plan: the marker -> nothing again (run once)")
    r = M.plan(S("x=1\r\nperk.fortuneMax=2.0\r\n"))
    K.check(str(r[0]) == "x=1\r\nperk.fortuneMax=0\r\n" + MARK + "\r\n", "MG plan: a CRLF file keeps CRLF")
    r = M.plan(S("perk.fortuneMax=2\\\n.0\n"))
    K.check(len(r[1]) == 0 and "perk.fortuneMax=2\\\n.0\n" in str(r[0]), "MG plan: a continued entry is never rewritten")
    r = M.plan(S("perk.fortuneMax=2.0\nperk.fortuneMax=5\n"))
    K.check(len(r[1]) == 0, "MG plan: the LAST entry decides (2.0 then 5 = the admin's 5)")
    r = M.plan(S("perk.fortuneMax=5\nperk.fortuneMax=2.0\n"))
    K.check(len(r[1]) == 3 and str(r[0]).startswith("perk.fortuneMax=5\nperk.fortuneMax=0\n"), "MG plan: 5 then 2.0 -> the 2.0 entry becomes 0")
    K.check(str(Cfg.DEFAULTS).count(str(M.MARK_ID)) == 1 and M.plan(Cfg.DEFAULTS) is None, "MG plan: the fresh default file carries the marker -> never migrated")

    # ---- run, end to end (scratch files)
    def start(d):
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        return str(M.run())

    def snap(d):
        return dict((os.path.relpath(os.path.join(r_, fn), d).replace(os.sep, "/"), open(os.path.join(r_, fn), "rb").read())
                    for r_, ds, fs in os.walk(d) for fn in fs)
    base = os.path.join(scratch, "mg")
    old_txt = str(Cfg.DEFAULTS).replace(MARK + "\n", "").replace("perk.fortuneMax=0\n", "perk.fortuneMax=2.0\n")
    assert old_txt.count("perk.fortuneMax=2.0\n") == 1 and str(M.MARK_ID) not in old_txt
    for tag, txt, nl in (("lf", old_txt, "\n"), ("crlf", old_txt.replace("\n", "\r\n"), "\r\n")):
        d = os.path.join(base, tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snap(d)
        r1 = start(d)
        s1 = snap(d)
        new = s1["xp.properties"].decode("latin-1")
        K.check(new == txt.replace("perk.fortuneMax=2.0" + nl, "perk.fortuneMax=0" + nl) + MARK + nl, "MG run %s: 2.0 -> 0 + the marker, every other byte kept" % tag)
        hist = [k for k in s1 if k.startswith("config-history/") and s1[k] == s0["xp.properties"]]
        K.check(len(hist) == 1, "MG run %s: the old file is in config-history (%s)" % (tag, hist))
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("perk.fortuneMax") == 1 and "2.0" in lg and "SkyySkills 0.4.48" in lg, "MG run %s: one config-changes.log row: %r" % (tag, lg.strip()[-160:]))
        K.check("perk.fortuneMax 2.0 -> 0" in r1 and "Undo" in r1, "MG run %s: the INFO line: %s" % (tag, r1[:160]))
        r2 = start(d)
        s2 = snap(d)
        K.check(r2 == "" and s2 == s1, "MG run %s: a second start changes nothing" % tag)
        p = JClass("java.util.Properties")()
        p.load(JClass("java.io.StringReader")(new))
        PCfg.read(p)
        K.check(float(PCfg.FORT_MAX) == 0.0 and int(PCfg.GUARD) == 100, "MG run %s: the migrated file reads uncapped, guard 100 (no line = the default)" % tag)
    d = os.path.join(base, "hand")
    os.makedirs(d)
    ht = old_txt.replace("perk.fortuneMax=2.0\n", "perk.fortuneMax=3.5\n")
    open(os.path.join(d, "xp.properties"), "wb").write(ht.encode("latin-1"))
    r1 = start(d)
    s1 = snap(d)
    K.check(s1["xp.properties"].decode("latin-1") == ht + MARK + "\n" and "3.5 kept" in r1 and "perk.fortuneMax" not in s1.get("config-changes.log", b"").decode("latin-1"),
            "MG run hand: an admin's 3.5 kept, only the marker added, no change-log row: %s" % r1[:200])
    d = os.path.join(base, "fresh")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(str(Cfg.DEFAULTS).encode("latin-1"))
    s0 = snap(d)
    r1 = start(d)
    K.check(r1 == "" and snap(d) == s0, "MG run fresh: a fresh default file is untouched")
    d = os.path.join(base, "none")
    os.makedirs(d)
    K.check(start(d) == "" and snap(d) == {}, "MG run none: no xp.properties -> nothing")
    K.save()


# ============================================================================================ LIVE48: start twice on a scratch COPY of the live data
def run_live48(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    res = {}
    lc_root = os.path.dirname(home)

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)
    for tag, jr, mg in (("old", OLD_JAR, OLD_MIGS), ("new", jar, OLD_MIGS + ["Fm48Mig"])):
        lc = os.path.join(lc_root, "copy48-" + tag)
        shutil.copytree(home, lc)
        L = loader_for(jr)
        J = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto, Hist, CLog, Rows = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")

        def start():
            Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
            Sto.DATA.clear()
            Sto.DIRTY.clear()
            Sto.DIR = jpath(os.path.join(lc, "players"))
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            r = {}
            for nm in mg:
                r[nm] = str(J(nm).run())
            r["load"] = str(Cfg.load())
            return r
        s0 = snap(lc)
        r1 = start()
        s1 = snap(lc)
        r2 = start()
        s2 = snap(lc)
        PC = J("PerkCfg")
        res[tag] = {"r1": r1, "r2": r2, "s0": s0, "s1": s1, "s2": s2, "fm": float(PC.FORT_MAX),
                    "guard": int(PC.GUARD) if tag == "new" else None, "mark": str(J("Fm48Mig").MARK) if tag == "new" else None}
    o, n = res["old"], res["new"]
    ch_o = sorted(k for k in set(o["s0"]) | set(o["s1"]) if o["s0"].get(k) != o["s1"].get(k))
    ch_n = sorted(k for k in set(n["s0"]) | set(n["s1"]) if n["s0"].get(k) != n["s1"].get(k))
    extra = sorted(set(ch_n) - set(ch_o))
    K.notes.append("LIVE48: 0.4.47 start 1 changed %s; 0.4.48 changed %s; Fm48Mig: %s" % (ch_o, ch_n, n["r1"].get("Fm48Mig", "")[:300]))
    K.check(set(extra) <= {"xp.properties", "config-changes.log"} | set(k for k in extra if k.startswith("config-history/")),
            "LIVE48: 0.4.48 start 1 changes what 0.4.47 changes + only xp.properties / its History copy / the change log: %s" % extra)
    xp0 = n["s0"].get("xp.properties", b"").decode("latin-1")
    xp1 = n["s1"].get("xp.properties", b"").decode("latin-1")
    nl = "\r\n" if "\r\n" in xp0 else "\n"
    if "perk.fortuneMax" not in xp0:
        # 0.4.47's own start already rewrites the live copy (older updates / appended sections); 0.4.48 = that + the Fm48Mig marker
        ox1 = o["s1"].get("xp.properties", b"").decode("latin-1")
        strip = "".join(ln for ln in xp1.splitlines(True) if ln.rstrip("\r\n") != n["mark"])
        diff = [ln for ln in strip.splitlines() if ln not in ox1.splitlines()] + ["-" + ln for ln in ox1.splitlines() if ln not in strip.splitlines()]
        K.check(xp1.count(n["mark"]) >= 1 and strip == ox1, "LIVE48: the live xp.properties (no perk.fortuneMax line): 0.4.47's result + only the marker: %s" % diff[:6])
    else:
        K.notes.append("LIVE48: the live xp.properties has a perk.fortuneMax line - plan() decided: %s" % n["r1"].get("Fm48Mig", "")[:200])
    K.check(n["fm"] == 0.0 or "kept" in n["r1"].get("Fm48Mig", ""), "LIVE48: the live copy reads tool Fortune uncapped (0.4.47 read %s; 0.4.48 %s)" % (o["fm"], n["fm"]))
    K.check(n["guard"] == 100, "LIVE48: the guard 100 (no line = the default)")
    if xp0 != xp1:
        K.check(any(k.startswith("config-history/") and v == n["s0"]["xp.properties"] for k, v in n["s1"].items() if k not in n["s0"]),
                "LIVE48: the live xp.properties before the update is in config-history")
    K.check(all(n["s1"].get(k) == n["s2"].get(k) for k in set(n["s1"]) | set(n["s2"])) and n["r2"].get("Fm48Mig") == "", "LIVE48: 0.4.48 start 2 changes nothing")
    K.check(all(n["s0"].get(k) == n["s1"].get(k) for k in n["s0"] if k.startswith("players/")), "LIVE48: player files untouched")
    K.save()


if __name__ == "__main__":
    phases = [("fo", run_fo), ("mg", run_mg), ("live48", run_live48)]
    if "--no-old" not in sys.argv:
        T47 = _mod("test_skyyskills_0.4.47.py", "test_skyyskills_0_4_47")
        phases += [("pack", T47.T46.run_pack), ("pages", T47.run_pages)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
