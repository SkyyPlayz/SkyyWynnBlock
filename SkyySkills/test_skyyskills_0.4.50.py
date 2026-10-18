"""SkyySkills 0.4.50 - harness for round "fortune" builder F2 (tools/skills_0_4_50_patch.py; research/Metals-Tools-Fortune-Spec.md 2.1 - 2.4):
Mining Fortune = tool + tree uncapped, the per-profile mined-ore budget + bridge skill:fn:oreBudget, the placed-furnace switch, the feed
bridge skill:fn:fortunefeed. Build first: python tools/skills_0_4_50_patch.py && python SkyySkills/build_skyyskills_0.4.50.py

    python SkyySkills/test_skyyskills_0.4.50.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.49 -> 0.4.50: + OreBud, OreBudgetFn, SmFeed, SmFeedTask, FortuneFeedFn, SmeltFortTask; only the planned members
  FO / MG / ZO / LIVE49  the 0.4.48 + 0.4.49 phases unchanged on this jar (Foraging Fortune maths, the migrations, the zone XP lines)
  FT  the config rows + reads; Perks.fortune Mining (tree joins the uncapped tool part; switch off = 0.4.49; doubleDropMax < 1 / fortuneMax
      still cap; the gear only.mining filter never hides the tree; Foraging unchanged); the budget (addList, caps, take / peek / give back,
      bad ids, 256 ids); OreBudgetFn + FortuneFeedFn argument handling; save -> reload round trip (ore.<id> lines in the player file);
      extraBars maths; placedExtras off by default; SmFeed grouping + texts; the setup / shutdown bridge lines
  FL  the felled-tree search limits (Skyy's Fens bug): defaults 16 / 1024 / 2048 / 40000, Fl50Mig.plan + run (old defaults migrate,
      hand edits kept, CRLF, last entry wins, multi-line untouched, marker, History, change log, second run nothing, fresh file untouched)
      and the search timed on the biggest vanilla tree prefabs (old vs new caps: logs claimed, reads, ms per fell)
  LIVE50  every one-time update in setup() order on a scratch COPY of the live data, twice
  RB  rollback: a 0.4.50 player file with ore.* lines read + saved by 0.4.49 keeps every XP line (only ore.* dropped), 0.4.50 reads it back
  PK / PG  0.4.47's asset-pack + page phases on this jar (skip with --no-old)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T49 = _mod("test_skyyskills_0.4.49.py", "test_skyyskills_0_4_49")
T48 = T49.T48
VERSION = "0.4.50"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.49.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "fort-f2", "sk")))
LIVE_DIR = T49.LIVE_DIR
ADDED = ["Fl50Mig", "OreBud", "OreBudgetFn", "SmFeed", "SmFeedTask", "FortuneFeedFn", "SmeltFortTask"]
EXPECT = {"Perks": ["~m breakDouble", "~m fortune"], "PerkCfg": ["+f TREE_UNCAP", "~m read", "~<clinit>", "~m ensureDefaults"],
          "SmithCfg": ["+f PLACED", "+f BUDGET_MAX", "+m oreOf", "~m read", "~<clinit>", "~m ensureDefaults"],
          "SkillStore": ["+f ORE", "+m oreId", "+m oreMap", "+m oreAdd", "+m oreTake", "+m oreGet", "~m readFile", "~m install", "~m snap", "~<clinit>"],
          "SkillBonus": ["+m ddExcept2"], "BreakTask": ["~m run"], "SmeltSys": ["~m handle"], "Acro": ["~m retainOnline"],
          "SkillCfg": ["~m load"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
          "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
          "SkyySkillsPlugin": ["~m setup", "~m shutdown"], "FellCfg": ["~<clinit>", "~m read", "~m ensureDefaults"]}
jpath, loader_for = T48.jpath, T48.loader_for
BUILD = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)


def fake_items(scratch):
    """ItemStack(id, n) needs the Item store: T48's stand-in HytaleAssetStore over an empty DefaultAssetMap (every id -> Item.UNKNOWN)"""
    from jpype import JClass
    U, setf = T48._unsafe(), T48._setf
    am = U.allocateInstance(JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_)
    setf(am, "assetMap", JClass("java.util.HashMap")())
    setf(am, "assetMapLock", JClass("java.util.concurrent.locks.StampedLock")())
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    fas = cp.makeClass("skyytest.FakeAssetStore50")
    fas.setSuperclass(cp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fas.addConstructor(JClass("javassist.CtNewConstructor").make("public FakeAssetStore50() { super(null); }", fas))
    fdir = os.path.join(scratch, "fake50")
    fas.writeFile(fdir)
    ua = JClass("java.lang.reflect.Array").newInstance(JClass("java.net.URL").class_, 1)
    ua[0] = JClass("java.io.File")(fdir).toURI().toURL()
    FL = JClass("java.net.URLClassLoader")(ua, JClass("java.lang.ClassLoader").getSystemClassLoader())
    st_ = U.allocateInstance(JClass("java.lang.Class").forName("skyytest.FakeAssetStore50", False, FL))
    setf(st_, "assetMap", am)
    setf(None, "ASSET_STORE", st_, JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_)


# ============================================================================================ FT: Fortune + the budget + the feed
def run_ft(out, jar, scratch, _home):
    from jpype import JClass, JDouble, JInt, JLong, JString, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Perks, PCfg, Cfg, Sto, Defs, BCfg, SC = J("Perks"), J("PerkCfg"), J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("BridgeCfg"), J("SmithCfg")
    OB, SF = J("OreBud"), J("SmFeed")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Props, UUID = JClass("java.util.Properties"), JClass("java.util.UUID")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Int, Long, Dbl, Str = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Double"), JClass("java.lang.String")
    OA = JArray(JClass("java.lang.Object"))
    D = str(Cfg.DEFAULTS)
    fake_items(scratch)
    # ---- the default file + reads
    for ln in ("perk.treeFortuneUncapped=true", "smelt.fortune.placed=false", "smelt.fortune.budgetMax=100000"):
        K.check(("\n" + ln + "\n") in ("\n" + D) and D.count(ln.split("=")[0] + "=") == 1, "FT default file: %s (once)" % ln)
    PCfg.read(Props())
    SC.read(Props())
    K.check(bool(PCfg.TREE_UNCAP) and not bool(SC.PLACED) and int(SC.BUDGET_MAX) == 100000, "FT read: defaults tree uncapped, placed off, budgetMax 100000")
    for txt, want in (("0", 0), ("-5", 0), ("250", 250), ("999999999999", 100000000), ("x", 100000)):
        p = Props()
        p.setProperty("smelt.fortune.budgetMax", txt)
        SC.read(p)
        K.eq(int(SC.BUDGET_MAX), want, "FT read: smelt.fortune.budgetMax=%s -> 0..100000000" % txt)
    p = Props()
    p.setProperty("perk.treeFortuneUncapped", "false")
    p.setProperty("smelt.fortune.placed", "true")
    PCfg.read(p)
    SC.read(p)
    K.check(not bool(PCfg.TREE_UNCAP) and bool(SC.PLACED), "FT read: treeFortuneUncapped=false / placed=true are read")
    PCfg.read(Props())
    SC.read(Props())
    # ---- Perks.fortune, Mining
    bridge = Sto.bridge()
    BCfg.BONUS = True
    u = UUID(0x450, 1)
    MIN, FOR = int(Defs.MINING), int(Defs.FARMING) - 1
    key = "skill:bonus:" + str(u)
    CHM, HM = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap")

    def srcs(**kw):
        bridge.remove(key)
        m = CHM()
        for k, v in kw.items():
            hm = HM()
            for kk, vv in v.items():
                hm.put(kk, JString(vv) if isinstance(vv, str) else Dbl(vv))
            m.put(k, JClass("java.util.Collections").unmodifiableMap(hm))
        bridge.put(key, m)

    fo = lambda row, lvl=0, fam=None: round(float(Perks.fortune(u, JInt(row), JInt(lvl), JString(fam) if fam else JObject(None, Str))), 9)
    srcs(gear={"dd.mining": 1.5}, trees={"dd.mining": 0.5})
    K.eq(fo(MIN), 2.0, "FT Mining: tool 1.5 + tree 0.5 = 2.0 (always 3 drops) - the spec's 150 % + 50 % example")
    srcs(trees={"dd.mining": 2.0})
    K.eq(fo(MIN), 2.0, "FT Mining: tree alone 2.0 is NOT capped at 1 any more (0.4.49: 1.0)")
    srcs(gear={"dd.mining": 1.5}, trees={"dd.mining": 0.5}, acc={"dd.mining": 0.8})
    K.eq(fo(MIN, 100), 3.0, "FT Mining: base min(perk 0.5 + acc 0.8, 1) = 1 + tool 1.5 + tree 0.5 = 3.0")
    PCfg.TREE_UNCAP = False
    K.eq(fo(MIN, 100), 2.5, "FT Mining switch off: 0.4.49 maths - min(0.5 + 0.8 + 0.5, 1) + 1.5 = 2.5")
    srcs(trees={"dd.mining": 2.0})
    K.eq(fo(MIN), 1.0, "FT Mining switch off: the tree alone is capped at 1.0 again")
    PCfg.TREE_UNCAP = True
    PCfg.DD_MAX = 0.5
    srcs(gear={"dd.mining": 1.5}, trees={"dd.mining": 0.5})
    K.eq(fo(MIN), 0.5, "FT Mining: an admin's doubleDropMax 0.5 is still a hard cap of the total")
    PCfg.DD_MAX = 1.0
    PCfg.FORT_MAX = 1.2
    K.eq(fo(MIN), 1.2, "FT Mining: an admin's fortuneMax 1.2 still caps the total")
    PCfg.FORT_MAX = 0.0
    srcs(gear={"dd.mining": 1.0, "only.mining": "Rock_"}, trees={"dd.mining": 0.4})
    K.eq(fo(MIN, 0, "Wood_Oak_Trunk"), 0.4, "FT Mining: the gear only.mining filter hides the tool part, never the tree part")
    K.eq(fo(MIN, 0, "Rock_Stone"), 1.4, "FT Mining: on a matching block both count (1.0 + 0.4)")
    srcs(gear={"dd.foraging": 1.5}, trees={"dd.foraging": 0.8})
    K.eq(fo(FOR, 100), 2.5, "FT Foraging unchanged: min(0.5 + 0.8, 1) + 1.5 = 2.5 (the tree stays capped there)")
    BCfg.BONUS = False
    srcs(gear={"dd.mining": 1.5}, trees={"dd.mining": 0.5})
    K.eq(fo(MIN), 0.0, "FT Mining: bridge.bonus.enabled=false ignores tool + tree (as before)")
    BCfg.BONUS = True
    srcs()
    # ---- the budget
    pdir = os.path.join(scratch, "ft", "players")
    os.makedirs(pdir)
    Sto.DIR = jpath(pdir)
    Sto.DATA.clear()
    Sto.ORE.clear()
    Sto.DIRTY.clear()
    k = str(Sto.pkey(u))
    K.eq(k, str(u), "FT pkey without SkyyProfiles = the UUID")
    L = JClass("java.util.ArrayList")
    l = L()
    l.add(IS(JString("Ore_Iron"), JInt(3)))
    l.add(IS(JString("Rock_Stone_Cobble"), JInt(1)))
    l.add(IS(JString("Ore_Lead_SkyWynn"), JInt(2)))
    l.add(JString("not a stack"))
    K.eq(int(OB.addList(u, l)), 5, "FT addList: 3 Ore_Iron + 2 Ore_Lead_SkyWynn counted, cobble / junk skipped")
    K.check(int(Sto.oreGet(k, "Ore_Iron")) == 3 and int(Sto.oreGet(k, "Ore_Lead_SkyWynn")) == 2 and int(Sto.oreGet(k, "Rock_Stone_Cobble")) == 0, "FT oreGet after addList")
    K.check(Sto.DIRTY.containsKey(k), "FT a budget change marks the profile dirty (saved by the 10 s flush)")
    K.eq(int(OB.extras(u, JInt(FOR), l)), 0, "FT extras: a Foraging drop list never counts")
    K.eq(int(OB.extras(u, JInt(MIN), l)), 5, "FT extras: Mining Fortune extras count")
    K.eq(int(Sto.oreGet(k, "Ore_Iron")), 6, "FT Ore_Iron = 6")
    ask = lambda oid, n: int(OB.ask(u, JString(oid), JLong(n)))
    K.eq(ask("Ore_Iron", 4), 4, "FT ask take 4 of 6 -> 4")
    K.eq(ask("Ore_Iron", 0), 2, "FT ask 0 = the balance (2), nothing taken")
    K.eq(ask("Ore_Iron", 5), 2, "FT ask take 5 of 2 -> 2 granted (the rest smelts 1:1)")
    K.eq(ask("Ore_Iron", 3), 0, "FT ask on an empty budget -> 0")
    K.eq(ask("Ore_Iron", -3), 3, "FT ask -3 = 3 given back (a cancelled unit)")
    K.eq(ask("Ore_Iron", 0), 3, "FT balance 3 after the give-back")
    for bad in ("Ingredient_Bar_Iron", "../../x", "Ore_", "Ore_Iron x", "", "Ore_" + "A" * 100):
        K.eq(ask(bad, 5), 0, "FT ask refuses a non-ore id %r" % bad)
    SC.BUDGET_MAX = 10
    l3 = L()
    l3.add(IS(JString("Ore_Gold"), JInt(25)))
    K.eq(int(OB.addList(u, l3)), 10, "FT budgetMax 10: 25 mined -> 10 remembered")
    K.eq(int(OB.addList(u, l3)), 0, "FT budgetMax 10: full -> nothing more")
    K.eq(ask("Ore_Gold", -50), 0, "FT give-back never passes budgetMax")
    SC.BUDGET_MAX = 0
    l4 = L()
    l4.add(IS(JString("Ore_Copper"), JInt(5)))
    K.eq(int(OB.addList(u, l4)), 0, "FT budgetMax 0: nothing remembered")
    SC.BUDGET_MAX = 100000
    for i in range(300):
        Sto.oreAdd(k, JString("Ore_T%d" % i), JLong(1), JLong(100))
    K.check(Sto.oreMap(k).size() <= 256, "FT at most 256 ore ids per profile (%d)" % Sto.oreMap(k).size())
    # ---- the bridge Functions
    Fn = J("OreBudgetFn")()

    def call(f, *a):
        arr = OA(len(a))
        for i, x in enumerate(a):
            arr[i] = x
        return f.apply(arr)
    r = call(Fn, u, JString("Ore_Iron"), Int(2))
    K.check(isinstance(r, Int) or str(type(r)).find("Integer") >= 0, "FT OreBudgetFn returns an Integer (%s)" % type(r))
    K.eq(int(r), 2, "FT OreBudgetFn take 2 -> 2")
    K.eq(int(call(Fn, u, JString("Ore_Iron"), Int(0))), 1, "FT OreBudgetFn peek -> 1")
    K.eq(int(call(Fn, u, JString("Ore_Iron"), Long(1))), 1, "FT OreBudgetFn accepts any Number (Long)")
    for args, what in (((u, JString("Ore_Iron")), "2 args"), ((JString(str(u)), JString("Ore_Iron"), Int(1)), "a String player"),
                       ((u, Int(3), Int(1)), "a non-String ore"), ((u, JString("Ore_Iron"), JString("1")), "a String n")):
        K.eq(int(call(Fn, *args)), 0, "FT OreBudgetFn bad args (%s) -> 0" % what)
    K.eq(int(Fn.apply(JString("x"))), 0, "FT OreBudgetFn not an Object[] -> 0")
    K.check(call(Fn, u, JString("Ore_Iron"), Int(-2000000000)) is not None, "FT OreBudgetFn a huge give-back is clamped, never throws")
    # ---- save -> reload
    K.check(bool(Sto.save(k)), "FT save")
    txt = open(os.path.join(pdir, k + ".properties"), encoding="latin-1").read()
    K.check("ore.Ore_Lead_SkyWynn=4" in txt and "ore.Ore_Gold=10" in txt and "ore.Ore_Copper" not in txt, "FT the player file holds ore.<id>=<n> lines (empty ids left out)")
    want = dict((str(i), int(Sto.oreGet(k, i))) for i in ("Ore_Iron", "Ore_Lead_SkyWynn", "Ore_Gold"))
    Sto.DATA.clear()
    Sto.ORE.clear()
    Sto.dataK(JString(k), u)
    K.eq(dict((i, int(Sto.oreGet(k, i))) for i in want), want, "FT reload: the budget comes back from the file")
    with open(os.path.join(pdir, k + ".properties"), "a", encoding="latin-1") as f:
        f.write("ore.Bad_Id=5\nore.Ore_Neg=-3\nore.Ore_Txt=abc\nore.Ore_Ok=7\n")
    Sto.DATA.clear()
    Sto.ORE.clear()
    Sto.dataK(JString(k), u)
    K.check(int(Sto.oreGet(k, "Ore_Ok")) == 7 and int(Sto.oreGet(k, "Ore_Neg")) == 0 and int(Sto.oreGet(k, "Ore_Txt")) == 0 and Sto.oreMap(k).get("Bad_Id") is None,
            "FT reload: bad ore lines (not Ore_, negative, not a number) are skipped")
    # ---- extraBars + placedExtras
    Rnd = JClass("java.util.Random")
    K.eq(int(OB.extraBars(JDouble(2.0), JLong(10), Rnd(1))), 20, "FT extraBars: F 2.0 x 10 units = 20 extra bars")
    x = int(OB.extraBars(JDouble(1.5), JLong(1000), Rnd(7)))
    K.check(1400 <= x <= 1600, "FT extraBars: F 1.5 x 1000 ~ 1500 (%d)" % x)
    K.check(int(OB.extraBars(JDouble(0.0), JLong(10), Rnd(1))) == 0 and int(OB.extraBars(JDouble(1.0), JLong(0), Rnd(1))) == 0, "FT extraBars: F 0 / 0 units -> 0")
    K.eq(int(OB.extraBars(JDouble(500.0), JLong(3), Rnd(1))), 300, "FT extraBars: per unit at most perk.fortuneGuard (100)")
    K.eq(int(OB.placedExtras(u, JString("Ingredient_Bar_Iron"), JInt(5))), 0, "FT placedExtras: smelt.fortune.placed off (default) -> nothing")
    SC.PLACED = True
    K.eq(int(OB.placedExtras(u, JString("Ingredient_Bar_Iron"), JInt(5))), 0, "FT placedExtras: no SkyyTrees (no Smelting Fortune) -> nothing, no budget taken")
    K.eq(int(Sto.oreGet(k, "Ore_Iron")), want["Ore_Iron"], "FT placedExtras without Fortune takes no budget")
    SC.PLACED = False
    # ---- SmFeed + FortuneFeedFn
    SF.MANUAL = True
    fu = UUID(0x450, 2)
    K.check(bool(SF.hit(fu, JString("Ingredient_Bar_Iron"), JLong(3))) and bool(SF.hit(fu, JString("Ingredient_Bar_Iron"), JLong(2))), "FT SmFeed.hit queues (shown by default)")
    FF = J("FortuneFeedFn")()
    K.check(bool(call(FF, fu, JString("Ingredient_Bar_Lead_SkyWynn"), Int(4))), "FT FortuneFeedFn -> TRUE (queued)")
    K.check(not bool(call(FF, fu, JString("Ingredient_Bar_Iron"), Int(0))) and not bool(call(FF, fu, JString("x"))) and not bool(FF.apply(JString("x"))), "FT FortuneFeedFn bad args / 0 -> FALSE")
    t = SF.take(fu)
    ids, qs = [str(i) for i in t[0]], [int(q) for q in t[1]]
    K.eq(list(zip(ids, qs)), [("Ingredient_Bar_Iron", 5), ("Ingredient_Bar_Lead_SkyWynn", 4)], "FT SmFeed groups per item (3 + 2 = 5)")
    line = str(SF.chatLine(t[0], t[1]))
    card = str(SF.cardText(t[0]))
    K.check(line.startswith("Smelting Fortune! +5 ") and ", +4 " in line and card.startswith("Smelting Fortune! ") and card.endswith(", +1 more"), "FT texts: %r / %r" % (line, card))
    PCfg.DD_MSG = False
    K.check(not bool(SF.hit(fu, JString("Ingredient_Bar_Iron"), JLong(1))), "FT SmFeed: the admin's Fortune indicator off -> hidden")
    PCfg.DD_MSG = True
    # ---- the plugin wiring (build script text: the two bridge keys put in setup, removed in shutdown)
    src = open(BUILD, encoding="utf8").read()
    for kk in ("skill:fn:oreBudget", "skill:fn:fortunefeed"):
        K.check(src.count('bridge().put("%s"' % kk) == 1 and src.count('bridge().remove("%s"' % kk) == 1, "FT %s is put in setup and removed in shutdown" % kk)
    K.save()


# ============================================================================================ RB: 0.4.50 file -> 0.4.49 -> 0.4.50
def run_rb(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    d = os.path.join(scratch, "rb", "players")
    os.makedirs(d)
    u = JClass("java.util.UUID")(0x450, 9)
    k = str(u)
    res = {}
    for tag, jr in (("new1", jar), ("old", OLD_JAR), ("new2", jar)):
        L = loader_for(jr)
        J = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto = J("SkillCfg"), J("SkillStore")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
        Sto.DIR = jpath(d)
        Sto.DATA.clear()
        dd = Sto.dataK(JString(k), u)
        if tag == "new1":
            Sto.wr(dd, 0, JLong(1234))
            Sto.wr(dd, 1, JLong(55))
            Sto.oreAdd(JString(k), JString("Ore_Iron"), JLong(9), JLong(100000))
        if tag == "new2":
            res["ore2"] = int(Sto.oreGet(JString(k), JString("Ore_Iron")))
        res[tag] = (int(Sto.rd(dd, 0)), int(Sto.rd(dd, 1)))
        Sto.save(JString(k))
        res[tag + "txt"] = open(os.path.join(d, k + ".properties"), encoding="latin-1").read()
    K.check("ore.Ore_Iron=9" in res["new1txt"], "RB 0.4.50 writes ore.Ore_Iron=9")
    K.check(res["old"] == (1234, 55) and res["new2"] == (1234, 55), "RB XP kept through 0.4.49 and back: %s" % res)
    strip = lambda t: sorted(ln for ln in t.splitlines() if not ln.startswith("#") and not ln.startswith("ore."))
    K.check(strip(res["oldtxt"]) == strip(res["new1txt"]) and "ore." not in res["oldtxt"], "RB 0.4.49's save keeps every other line, drops only ore.*")
    K.eq(res["ore2"], 0, "RB after a 0.4.49 save the budget is gone (documented rollback cost), nothing else")
    K.save()


# ============================================================================================ FL: felled-tree search limits (Skyy's Fens bug)
FL_KEYS = [("fell.radius", "8", "16"), ("fell.maxLogs", "256", "1024"), ("fell.maxLeaves", "384", "2048"), ("fell.maxReads", "8000", "40000")]
FL_PREFABS = 10   # the biggest vanilla tree prefabs (by wood blocks) timed


def tree_prefabs():
    """(wood count, leaves, name, blocks) of every Server/Prefabs/Trees prefab in Assets.zip (read only, in memory)"""
    import zipfile, json
    out = []
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as z:   # read only
        for n in z.namelist():
            if not (n.startswith("Server/Prefabs/Trees/") and n.endswith(".prefab.json")):
                continue
            bl = json.loads(z.read(n)).get("blocks", [])
            w = [b for b in bl if str(b.get("name", "")).startswith("Wood_")]
            if w:
                out.append((len(w), sum(1 for b in bl if "Leaves" in str(b.get("name", ""))), n.split("/")[-1], bl))
    out.sort(key=lambda r: -r[0])
    return out


def run_fl(out, jar, scratch, _home):
    from jpype import JClass, JString, JInt, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    M, Cfg, Hist, CLog, Rows, FC = J("Fl50Mig"), J("SkillCfg"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("FellCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    S = lambda x: JString(x)
    D = str(Cfg.DEFAULTS)
    MARK_ID = str(M.MARK_ID)
    # ---- defaults
    for k, o, n in FL_KEYS:
        K.check(("\n%s=%s\n" % (k, n)) in ("\n" + D) and D.count(k + "=") == 1, "FL default file: %s=%s" % (k, n))
    K.check(D.count(MARK_ID) == 1 and M.plan(S(D)) is None, "FL default file carries the Fl50Mig marker -> never migrated")
    K.check(int(FC.RADIUS) == 16 and int(FC.MAX_LOGS) == 1024 and int(FC.MAX_LEAVES) == 2048 and int(FC.MAX_READS) == 40000, "FL FellCfg field defaults 16 / 1024 / 2048 / 40000")
    # ---- plan (pure)
    old = "a=1\nfell.radius=8\nfell.height=64\nfell.maxLogs=256\nfell.maxLeaves=384\nfell.maxReads=8000\nz=2\n"
    r = M.plan(S(old))
    body = str(r[0])
    want = old.replace("radius=8", "radius=16").replace("maxLogs=256", "maxLogs=1024").replace("maxLeaves=384", "maxLeaves=2048").replace("maxReads=8000", "maxReads=40000") + str(M.MARK) + "\n"
    K.check(body == want, "FL plan: the four old defaults -> new, every other byte kept, the marker at the end: %r" % body[-200:])
    K.eq([str(x) for x in r[1]], [x for k, o, n in FL_KEYS for x in (k, o, n)], "FL plan: one change-log row per key")
    K.check(bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(body).getBytes("ISO-8859-1"), r[2])), "FL sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(body.replace("a=1", "a=9")).getBytes("ISO-8859-1"), r[2])), "FL sameAfter refuses another change (control)")
    hand = old.replace("maxLogs=256", "maxLogs=300").replace("radius=8", "radius = 12")
    r = M.plan(S(hand))
    b2 = str(r[0])
    K.check("fell.maxLogs=300\n" in b2 and "fell.radius = 12\n" in b2 and "fell.maxLeaves=2048\n" in b2 and "fell.maxReads=40000\n" in b2
            and "fell.maxLogs=300 kept" in str(r[3]), "FL plan: an admin's own values (300 logs, radius 12) are kept, the others migrate: %s" % str(r[3])[:160])
    r = M.plan(S(old.replace("\n", "\r\n")))
    K.check(str(r[0]) == want.replace("\n", "\r\n"), "FL plan: a CRLF file stays CRLF")
    K.check(M.plan(S(old + "# " + MARK_ID + " x\n")) is None, "FL plan: the marker -> nothing (run once)")
    r = M.plan(S("fell.maxLogs=256\nfell.maxLogs=500\n"))
    K.check("fell.maxLogs=256\nfell.maxLogs=500\n" in str(r[0]), "FL plan: the LAST entry decides (an admin's later 500 wins, nothing rewritten)")
    r = M.plan(S("fell.maxLogs=2\\\n56\n"))
    K.check(str(r[0]).startswith("fell.maxLogs=2\\\n56\n"), "FL plan: a continued (multi-line) value is never touched")
    r = M.plan(S("a=1\n"))
    K.check(len(r[1]) == 0 and str(r[0]) == "a=1\n" + str(M.MARK) + "\n", "FL plan: no fell lines -> only the marker (the new code defaults apply)")

    # ---- run, end to end
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
    for tag, txt in (("lf", old), ("crlf", old.replace("\n", "\r\n"))):
        d = os.path.join(scratch, "fl", tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snap(d)
        r1 = start(d)
        s1 = snap(d)
        nl = "\r\n" if tag == "crlf" else "\n"
        K.check(s1["xp.properties"].decode("latin-1") == want.replace("\n", nl), "FL run %s: the file = the plan" % tag)
        K.check(any(k.startswith("config-history/") and v == s0["xp.properties"] for k, v in s1.items()), "FL run %s: the old file is in config-history" % tag)
        logs = [v.decode("latin-1") for k, v in s1.items() if k.endswith("config-changes.log")]
        K.check(logs and all(("fell.%s" % kk) in logs[0] for kk in ("radius", "maxLogs", "maxLeaves", "maxReads")), "FL run %s: a change-log line per key (Undo): %s" % (tag, [k for k in s1 if "change" in k]))
        K.check("Undo" in r1 and "config-history" in r1, "FL run %s: the INFO line: %s" % (tag, r1[:200]))
        K.check(start(d) == "" and snap(d) == s1, "FL run %s: a second start changes nothing" % tag)
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Cfg.load()
        K.check(int(FC.RADIUS) == 16 and int(FC.MAX_LOGS) == 1024 and int(FC.MAX_LEAVES) == 2048 and int(FC.MAX_READS) == 40000, "FL run %s: SkillCfg.load reads 16 / 1024 / 2048 / 40000" % tag)
    d = os.path.join(scratch, "fl", "fresh")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(D.encode("latin-1"))
    s0 = snap(d)
    K.check(start(d) == "" and snap(d) == s0, "FL run fresh: a fresh default file is untouched")
    d = os.path.join(scratch, "fl", "none")
    os.makedirs(d)
    K.check(start(d) == "" and snap(d) == {}, "FL run none: no file -> nothing")

    # ---- the search on the biggest vanilla tree prefabs: claims + cost (ms per fell; the handler runs it on the world thread)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    mf = cp.makeClass("skyytest.MapFn50")
    mf.addInterface(cp.get("java.util.function.Function"))
    mf.addField(JClass("javassist.CtField").make("public static java.util.HashMap M = new java.util.HashMap();", mf))
    mf.addMethod(JClass("javassist.CtNewMethod").make("public Object apply(Object k) { Object v = M.get(k); return v == null ? (Object) Integer.valueOf(0) : v; }", mf))
    fdir = os.path.join(scratch, "fl", "mapfn")
    mf.writeFile(fdir)
    ua = JClass("java.lang.reflect.Array").newInstance(JClass("java.net.URL").class_, 1)
    ua[0] = JClass("java.io.File")(fdir).toURI().toURL()
    MapFn = JClass("java.lang.Class").forName("skyytest.MapFn50", True, JClass("java.net.URLClassLoader")(ua, JClass("java.lang.ClassLoader").getSystemClassLoader()))
    fn = MapFn.getDeclaredConstructor().newInstance()
    MM = MapFn.getField("M").get(None)
    Defs, Fell, Snap, Read, PS = J("FellDefs"), J("Fell"), J("FellSnap"), J("FellRead"), J("PlacedStore")
    PS.DIR = jpath(os.path.join(scratch, "fl", "placed"))
    Read.TEST = fn
    Integer = JClass("java.lang.Integer")
    UUID = JClass("java.util.UUID")
    idx_of = {}
    rows = []
    allp = tree_prefabs()
    mid = [r for r in allp if 600 <= r[0] <= 1024]
    sel = allp[:FL_PREFABS] + mid[:5]   # + mid-size trees (the Fens case: 600 - 1024 wood) that the new caps claim whole
    caps = {"old": (8, 256, 384, 8000), "new": (16, 1024, 2048, 40000)}
    seq = [0]

    def fell_once(blocks, base, fam, cap):
        FC.RADIUS, FC.MAX_LOGS, FC.MAX_LEAVES, FC.MAX_READS = cap
        s = Snap()
        seq[0] += 1
        s.wn = "fl-test"
        s.u = UUID(0x4500, seq[0])
        s.trig = 1
        s.bx, s.by, s.bz = base
        s.fam = fam
        R = Read(None, JInt(cap[3]))
        Fell.run(s, R, False)
        return int(s.logs) + int(s.ln), int(s.leaves), int(R.reads), bool(R.over), int(s.took) / 1e6
    lv0 = bool(FC.LEAVES)
    FC.LEAVES = True   # the worst case: leaves claimed too (fell.leaves)
    for wood, leaves, name, bl in sel:
        MM.clear()
        oy = 100
        for b in bl:
            nm = str(b.get("name", ""))
            if nm not in idx_of:
                i = len(idx_of) + 1
                idx_of[nm] = i
                k = int(Defs.kindOfId(S(nm)))
                FC.CODE.put(Integer(i), Integer(k))
                FC.FAM.put(Integer(i), S("" if k in (0, 4) else str(Defs.familyOfId(S(nm)))))
            MM.put(JClass("java.lang.Long")(int(PS.key(JInt(b["x"]), JInt(b["y"] + oy), JInt(b["z"])))), Integer(idx_of[nm]))
        tr = [b for b in bl if int(Defs.kindOfId(S(str(b["name"])))) == 1] or [b for b in bl if str(b["name"]).startswith("Wood_")]
        bb = min(tr, key=lambda b: (b["y"], abs(b["x"]) + abs(b["z"])))
        fam = str(Defs.familyOfId(S(str(bb["name"]))))
        base = (bb["x"], bb["y"] + oy, bb["z"])
        res = {}
        for tag, cap in caps.items():
            first = fell_once(bl, base, fam, cap)
            warm = sorted(fell_once(bl, base, fam, cap)[4] for _ in range(5))
            res[tag] = first[:4] + (round(first[4], 2), round(warm[2], 2))
        rows.append((name, wood, leaves, res))
    FC.RADIUS, FC.MAX_LOGS, FC.MAX_LEAVES, FC.MAX_READS = caps["new"]
    Read.TEST = None
    FC.LEAVES = lv0
    # a mid-size tree's search now ends by itself (no read budget hit, under maxLogs) = every connected log of its family is claimed (roots of
    # another family / below the cut never were part of a fell)
    K.check(all(not r["new"][3] and r["new"][0] < 1024 for n, w, lv, r in rows if w <= 1024), "FL the mid-size trees (600 - 1024 wood): the search ends by itself with the new caps: %s" % [(n, w, r["new"][0], r["new"][3]) for n, w, lv, r in rows if w <= 1024])
    K.check(all(r["old"][0] in (256,) or r["old"][0] < 256 for n, w, lv, r in rows), "FL control: the old caps stop at 256 logs")
    tbl = ["%s: %d wood %d leaves | old caps %d logs %d leaves %d reads%s %.2f ms (warm %.2f) | new caps %d logs %d leaves %d reads%s %.2f ms (warm %.2f)"
           % (n, w, lv, r["old"][0], r["old"][1], r["old"][2], " OVER" if r["old"][3] else "", r["old"][4], r["old"][5],
              r["new"][0], r["new"][1], r["new"][2], " OVER" if r["new"][3] else "", r["new"][4], r["new"][5]) for n, w, lv, r in rows]
    K.notes.append("FL search cost (biggest vanilla tree prefabs; warm = median of 5):\n    " + "\n    ".join(tbl))
    K.check(all(r["new"][0] >= r["old"][0] for n, w, lv, r in rows), "FL the new caps never claim fewer logs than the old ones")
    K.check(any(r["new"][0] > r["old"][0] for n, w, lv, r in rows), "FL the new caps claim more logs on the big trees")
    worst = max(r["new"][5] for n, w, lv, r in rows)
    K.notes.append("FL worst warm search %.2f ms per fell (new caps); prefabs over 1024 wood: %d of %d" % (worst, sum(1 for r in allp if r[0] > 1024), len(allp)))
    K.check(worst < 50.0, "FL the worst warm search stays under 50 ms per fell (%.2f ms)" % worst)
    K.save()


# ============================================================================================ LIVE50: every update in setup() order on a COPY of the live data
def run_live50(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy50")
    shutil.copytree(home, lc)
    L = loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, FC = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("FellCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    migs = T49.OLD_MIGS + ["Zo49Mig", "Fl50Mig"]

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def start():
        Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
        Sto.DATA.clear()
        Sto.DIR = jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = dict((nm, str(J(nm).run())) for nm in migs)
        r["load"] = str(Cfg.load())
        return r
    s0 = snap(lc)
    r1 = start()
    s1 = snap(lc)
    vals = (int(FC.RADIUS), int(FC.MAX_LOGS), int(FC.MAX_LEAVES), int(FC.MAX_READS))
    r2 = start()
    s2 = snap(lc)
    xp0 = s0.get("xp.properties", b"").decode("latin-1")
    K.notes.append("LIVE50: Fl50Mig: %s; live fell values now %s" % (r1.get("Fl50Mig", "")[:300], vals))
    held_old = all(("\n%s=%s" % (k, o)) in ("\n" + xp0.replace("\r", "")) for k, o, n in FL_KEYS)
    K.check(not held_old or vals == (16, 1024, 2048, 40000), "LIVE50: the live copy's untouched old limits are now 16 / 1024 / 2048 / 40000 (%s)" % (vals,))
    K.check(vals[1] >= 256, "LIVE50: fell.maxLogs never drops")
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2.get("Fl50Mig") == "", "LIVE50: start 2 changes nothing")
    K.check(all(s0.get(k) == s1.get(k) for k in s0 if k.startswith("players/")), "LIVE50: player files untouched")
    K.save()


if __name__ == "__main__":
    phases = [("fo", T48.run_fo), ("mg", T48.run_mg), ("zo", T49.run_zo), ("live49", T49.run_live49), ("ft", run_ft), ("rb", run_rb), ("fl", run_fl), ("live50", run_live50)]
    if "--no-old" not in sys.argv:
        T47 = _mod("test_skyyskills_0.4.47.py", "test_skyyskills_0_4_47")
        phases += [("pack", T47.T46.run_pack), ("pages", T47.run_pages)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
