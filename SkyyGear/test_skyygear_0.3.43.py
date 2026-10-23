"""Harness for SkyyGear 0.3.43 (sig1: the Ability 1 tooltip block, the Mythic / Untiered charge rates, the pack meter fix - tools/gear_0_3_43_patch.py).
Build first (SkyyArmory 0.1.44 too - the exec phase calls its REAL armory:fn:sig):
    python tools/armory_0_1_44_patch.py && python SkyyArmory/build_skyyarmory_0.1.44.py
    python tools/gear_0_3_43_patch.py && python SkyyGear/build_skyygear_0.3.43.py
    python SkyyGear/test_skyygear_0.3.43.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, one new class (GearSigX), no command / system; the non-class jar
              entries = 0.3.42's except the manifest; the fresh config file carries the 4 rows, no sig.ut entry
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.42 -> 0.3.43 (EXPECT below)
  X  exec     EXECUTES in a bare JVM (the bridge map with SkyyArmory 0.1.44's real ArmorySigFn, the item seam GearSigX.ITEM, stand-in stacks
              with gear documents, a REAL EntityStatMap with the SignatureEnergy stat type):
              the table answers (vanilla sword, battleaxe "(battleaxe)", an Armory wand + its UT copy through the bridge, a dev bow, a
              root-less weapon = none, a dead meter = none, the pack Mythic with sig.packMeter on / off, a malformed / throwing / "off"
              bridge answer); the tooltip block lines + colours (heading gold, text #d6e4ee, Charge segments soft / #e8c25a / #7ee08a, the
              "Fills N% faster (Mythic)" green / "slower (Untiered)" red line, "Ability 1 - none" #7f93a6, sig.tooltip off = nothing, every
              line <= 70 characters); GearView.seg builds one child per segment; plain() strips the joints + folds the block; the Mythic %
              at T1 / T8 / T15 / Onyxium + after a live row edit; the Untiered row faster / slower / clamped; the rate step (baseline, settle,
              rise x 1.4, our own add never counted again, cap at max, a drop re-baselines, swap / slot / busy re-baseline, a slower UT takes
              back, a config epoch move re-reads the rate, normal items untouched); the pack meter modifier put / kept / removed on the
              REAL EntityStatMap (max 0 -> 8 -> 0, Razorstrike 27) and sig.packMeter off removes it; the pack meter charging (step + addStatValue)
  D  live     start TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: the second start changes nothing, no row written
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the tick order against the engine's own hit gain, the client meter showing the server top-up, the
skyygear_sig modifier surviving the engine's Recalculate in game, the real hover text look.
Scratch: tools/dev/scratch/sig1fix/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.43"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig1fix", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.42.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_43_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.42.jar")
ARM_JAR = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.44.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = ["GearSigX"]
EXPECT = {
    "GearCfg": ["+f SIG_MHI", "+f SIG_MLO", "+f SIG_PACK", "+f SIG_TIP", "+f SIG_UT", "~<clinit>", "~m apply", "~m defaultsText"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"],          # the 5 new rows
    "GearView": ["+m sigRows", "~m plain", "~m seg", "~m weaponRows"],
    "GearHandSys": ["~m tick"], "GearCharged": ["~m forget"],
    "SkyyGearPlugin": ["~m setup", "~m start"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
SEP = chr(2)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.43 - build script') and g.count('VERSION = "0.3.43"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 1), "S no new system / command; one new class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (["com/skyy/gear/GearSigX.class"], []), "S the only entry added = GearSigX")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is the manifest (no art / item / lang / config file)")
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JInt, JString, JFloat, JArray, JImplements, JOverride, JObject
    K = HK.Child(out)
    HK.jvm([jar, ARM_JAR, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, SX, GV, Data, Defs = P("GearCfg"), P("GearSigX"), P("GearView"), P("GearData"), P("GearDefs")
    ASig, ACfg, ADefs = JClass("com.skyy.armory.ArmorySigFn"), JClass("com.skyy.armory.ArmoryCfg"), JClass("com.skyy.armory.ArmoryDefs")
    UUID, AL, HM = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.util.HashMap")
    BD, BS, BI, BB = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonBoolean")
    K.check(bool(Cfg.SIG_TIP) and int(Cfg.SIG_MLO) == 40 and int(Cfg.SIG_MHI) == 60 and bool(Cfg.SIG_PACK) and Cfg.SIG_UT.isEmpty(),
            "X defaults: sig.tooltip on, Mythic 40 / 60, pack meter on, no Untiered row")

    # ---- the item seam: id -> Object[] { root, Float meter } (the live Item.getInteractions / Weapon stat modifiers in game)
    ITEMS = {"Weapon_Sword_Iron": ("Root_Weapon_Sword_Signature_Vortexstrike", 20.0),
             "Weapon_Sword_UT_Paperweight": ("Root_Weapon_Sword_Signature_Vortexstrike", 20.0),
             "Weapon_Battleaxe_Iron": ("Root_Weapon_Battleaxe_Signature_Whirlwind", 9.0),
             "Weapon_Mace_Iron": ("Root_Weapon_Mace_Signature_Groundslam", 8.0),
             "Weapon_Crossbow_Iron": ("Root_Weapon_Crossbow_Signature_BigArrow", 5.0),
             "Weapon_Shortbow_Vampire": ("*Weapon_Shortbow_Vampire_Interactions_Ability1", 10.0),
             "Weapon_Longsword_Iron": (None, 0.0),
             "Weapon_Bo_Iron_SkyWynn": (None, 0.0),
             "Some_Pack_Dead": ("Root_Weapon_Mace_Signature_Groundslam", 0.0),
             "Zweihander": ("Root_Weapon_Mace_Signature_Groundslam", 0.0),
             "DualRuneBlade": ("Root_Weapon_Daggers_Signature_Razorstrike", 0.0),
             "Hepta_Axe": (None, 9.0)}
    asked = []

    @JImplements("java.util.function.Function")
    class ItemSeam(object):
        @JOverride
        def apply(self, o):
            i = str(o)
            asked.append(i)
            if i not in ITEMS:
                return None
            r, m = ITEMS[i]
            a = JArray(JObject)(2)
            a[0] = None if r is None else JString(r)
            a[1] = JClass("java.lang.Float").valueOf(JFloat(m))
            return a
    SX.ITEM = ItemSeam()
    br.put("armory:fn:sig", ASig())

    def sig(i):
        r = SX.sigOf(JString(i))
        return None if r is None else (str(r[0]), str(r[1]), int(r[2]), str(r[3]))
    K.eq(sig("Weapon_Sword_Iron"), ("Vortexstrike", "Spin slash around you, then a lunging stab forward.", 20, "swing +1~, thrust +3~"), "X a vanilla sword: Vortexstrike, meter 20")
    K.eq(sig("Weapon_Battleaxe_Iron")[0], "Whirlwind (battleaxe)", "X the battleaxe says (battleaxe)")
    # an Armory wand: the first code-100..199 id of ArmoryDefs.items()
    wands = sorted(str(k) for k in ADefs.items().keySet() if int(ADefs.wandIndex(JString(str(k)))) >= 0)
    K.check(len(wands) >= 10 and "Weapon_Wand_Wood" in wands and "Weapon_Wand_Tribal" in wands, "X Armory wand ids (+ SkyySkills' Wood / Tribal): %s" % wands[:4])
    wid = [w for w in wands if "Iron" in w][0] if [w for w in wands if "Iron" in w] else wands[0]
    K.eq(sig(wid), ("Ricochet", "A bolt jumps from your target to the nearest enemy, up to 8 hits.", 20, "quick hit +1~, charged hit +2"),
         "X an Armory wand (%s) through the REAL armory:fn:sig" % wid)
    ut_ids = [str(x) for x in ADefs.UT_IDS]
    wut = [u for u in ut_ids if "Wand" in u]
    K.check(bool(wut) and sig(wut[0]) is not None and sig(wut[0])[0] == "Ricochet", "X the Armory's Untiered wand (%s) answers as its base" % (wut[:1],))
    n0 = len(asked)
    sig(wid)
    K.eq(len(asked), n0, "X an Armory answer never reads the item (no fallback)")
    ACfg.SIG_HITS = 12
    K.check(sig(wid)[1].endswith("up to 12 hits."), "X the Armory text follows its live sig.wand.maxHits")
    ACfg.SIG_HITS = 8
    ACfg.SIG_ON = False
    K.eq(sig(wid), None, "X sig.wand.enabled off -> none")
    ACfg.SIG_ON = True
    K.eq(sig("Weapon_Shortbow_Vampire")[:3], ("Supershot", "Fires one big arrow that steals life.", 10), "X a dev bow by id (inline root): Supershot, 10")
    K.eq([sig("Weapon_Longsword_Iron"), sig("Weapon_Bo_Iron_SkyWynn"), sig("Hepta_Axe"), sig("Some_Pack_Dead"), sig("No_Such_Item")], [None] * 5,
         "X none: no root (longsword, Bo), meter without root (Hepta Axe), a dead meter not on the pack list, an unknown id")
    K.eq(sig("Zweihander")[:3], ("Groundslam", "Leap up and slam down, knocking up everything where you land.", 8), "X pack meter on: the Zweihander = Groundslam, meter 8")
    K.eq(sig("DualRuneBlade")[2], 27, "X ... the Dual Rune Blade = Razorstrike 27")
    Cfg.SIG_PACK = False
    K.eq((sig("Zweihander"), sig("DualRuneBlade")), (None, None), "X sig.packMeter off -> none (back to dead)")
    Cfg.SIG_PACK = True

    # mutants of the bridge: malformed answer / a throw / null
    @JImplements("java.util.function.Function")
    class Bad(object):
        def __init__(self, mode):
            self.mode = mode

        @JOverride
        def apply(self, o):
            if self.mode == "throw":
                raise JClass("java.lang.IllegalStateException")("boom")
            if self.mode == "short":
                a = JArray(JObject)(2)
                a[0] = JString("X")
                return a
            return None
    br.put("armory:fn:sig", Bad("short"))
    K.eq(sig("Weapon_Sword_Iron"), None, "X mutant: a malformed Armory answer -> none, no crash")
    br.put("armory:fn:sig", Bad("throw"))
    K.eq(sig("Weapon_Sword_Iron")[0], "Vortexstrike", "X mutant: a throwing bridge -> our own answer")
    br.put("armory:fn:sig", Bad("null"))
    K.eq(sig("Weapon_Sword_Iron")[0], "Vortexstrike", "X mutant: the bridge says null -> our own answer")
    br.remove("armory:fn:sig")
    K.eq(sig(wid), None, "X without SkyyArmory a wand id is none (no root in the seam)")
    br.put("armory:fn:sig", ASig())

    # ---- rates
    def doc(r, lvl=10, ident=True):
        d = BD()
        d.put("r", BS(r))
        d.put("lvl", BI(lvl))
        d.put("id", BB(ident))
        return d
    K.eq([int(SX.mythPct(t)) for t in (0, 1, 8, 15, 16)], [40, 40, 50, 60, 60], "X Mythic %: T1 40, T8 50, T15 60 (clamped at both ends)")
    K.eq([int(SX.pctOf(JString("Weapon_Sword_Iron"), doc("mythic", lv))) for lv in (1, 15, 48, 95, 108)], [40, 43, 50, 60, 60],
         "X a Mythic sword at Lv 1 / 15 / 48 / 95 / 108 (T1 / T3 / T8 / T15 / T15)")
    K.eq(int(SX.pctOf(JString("Weapon_Sword_Onyxium"), doc("mythic", 20))), 60, "X an Onyxium Mythic = the top (T16)")
    K.eq([int(SX.pctOf(JString("Weapon_Sword_Iron"), doc(r))) for r in ("normal", "rare", "legendary", "fabled", "set")], [0] * 5, "X other rarities: normal rate")
    K.eq(int(SX.pctOf(JString("Weapon_Sword_UT_Paperweight"), doc("untiered"))), 0, "X an Untiered item without a row: normal")
    m = HM()
    m.put("Weapon_Sword_UT_Paperweight", JClass("java.lang.Integer").valueOf(25))
    m.put("Weapon_Shortbow_Vampire", JClass("java.lang.Integer").valueOf(-30))
    Cfg.SIG_UT = m
    K.eq(int(SX.pctOf(JString("Weapon_Sword_UT_Paperweight"), doc("untiered"))), 25, "X sig.ut row +25 on the Paperweight")
    K.eq(int(SX.pctOf(JString("Weapon_Shortbow_Vampire"), doc("mythic", 1))), 40, "X a sig.ut row on a Mythic is ignored (Mythic = by tier)")
    K.eq(int(SX.pctOf(JString("Weapon_Shortbow_Vampire"), doc("untiered"))), -30, "X a slower Untiered row (-30)")
    K.eq([round(float(SX.multOf(p)), 9) for p in (0, 40, 60, -30, -90, -200)], [1.0, 1.4, 1.6, 0.7, 0.1, 0.1], "X multOf: % faster -> x (1 + p / 100), floor -90")
    Cfg.SIG_MLO, Cfg.SIG_MHI = 10, 30
    K.eq([int(SX.mythPct(1)), int(SX.mythPct(15))], [10, 30], "X a live edit of the two Mythic rows")
    Cfg.SIG_MLO, Cfg.SIG_MHI = 40, 60
    # the load path (the config file lines)
    cfgd = os.path.join(scratch, "cfgload")
    os.makedirs(cfgd, exist_ok=True)
    fc = os.path.join(cfgd, "config.properties")
    open(fc, "w").write("sig.mythic.low=45\nsig.mythic.high=300\nsig.tooltip=false\nsig.packMeter=false\nsig.ut.Weapon_Sword_UT_Paperweight=-20\nsig.ut.Bad_One=abc\nsig.ut.Too_Fast=999\n")
    old_file = Cfg.FILE
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    Cfg.load()
    K.eq((int(Cfg.SIG_MLO), int(Cfg.SIG_MHI), bool(Cfg.SIG_TIP), bool(Cfg.SIG_PACK), sorted((str(k), int(Cfg.SIG_UT.get(k))) for k in Cfg.SIG_UT.keySet())),
         (45, 200, False, False, [("Weapon_Sword_UT_Paperweight", -20)]), "X load: the rows read + clamped, bad sig.ut lines dropped")
    os.remove(fc)
    Cfg.load()
    K.eq((int(Cfg.SIG_MLO), int(Cfg.SIG_MHI), bool(Cfg.SIG_TIP), bool(Cfg.SIG_PACK), int(Cfg.SIG_UT.size())), (40, 60, True, True, 0), "X load without the lines = the defaults")
    Cfg.FILE = old_file
    Cfg.SIG_UT = m

    # ---- the tooltip block
    def block(i, d):
        at, ac = AL(), AL()
        GV.sigRows(JString(i), d, at, ac)
        return [(str(at.get(k)), None if ac.get(k) is None else str(ac.get(k))) for k in range(at.size())]
    GOLD = "*" + str(Defs.C_GOLD)
    b = block("Weapon_Sword_Iron", doc("rare", 10))
    K.eq([t.replace(SEP, "") for t, c in b], ["Ability 1 - Vortexstrike", "Spin slash around you, then a lunging stab forward.", "Charge: 20 energy - swing +1, thrust +3"],
         "X tooltip: a vanilla Iron sword")
    K.eq([c for t, c in b][:2], [GOLD, "#d6e4ee"], "X heading bold gold (the section's style), text soft white #d6e4ee")
    K.eq(b[2][0].split(SEP), ["Charge: ", "20 energy", " - ", "swing ", "+1", ", thrust ", "+3"], "X the Charge line's segments")
    K.eq(b[2][1], "&#d6e4ee&#e8c25a&#d6e4ee&#d6e4ee&#7ee08a&#d6e4ee&#7ee08a", "X ... their colours: soft / gold #e8c25a / green #7ee08a")
    K.notes.append("X Iron sword block: %s" % [t.replace(SEP, "|") for t, c in b])
    bw = block(wid, doc("rare", 10))
    K.eq([t.replace(SEP, "") for t, c in bw], ["Ability 1 - Ricochet", "A bolt jumps from your target to the nearest enemy, up to 8 hits.", "Charge: 20 energy - quick hit +1, charged hit +2"],
         "X tooltip: an Armory wand (SkyyArmory's text)")
    bm = block("Weapon_Shortbow_Vampire", doc("mythic", 1))
    K.eq([(t.replace(SEP, ""), c) for t, c in bm][2:], [("Charge: 10 energy - +0.7 to +4.2 per hit (by draw)", bm[2][1]), ("Fills 40% faster (Mythic)", "#7ee08a")],
         "X tooltip: a T1 Mythic dev bow - gains x 1.4, the green Fills line")
    bm2 = block("Weapon_Shortbow_Vampire", doc("mythic", 95))
    K.eq(bm2[3], ("Fills 60% faster (Mythic)", "#7ee08a"), "X ... at T15: 60 %")
    bu = block("Weapon_Sword_UT_Paperweight", doc("untiered", 15))
    K.eq([t.replace(SEP, "") for t, c in bu][2:], ["Charge: 20 energy - swing +1.3, thrust +3.8", "Fills 25% faster (Untiered)"], "X tooltip: an Untiered row +25")
    m.put("Weapon_Sword_UT_Paperweight", JClass("java.lang.Integer").valueOf(-25))
    bu2 = block("Weapon_Sword_UT_Paperweight", doc("untiered", 15))
    K.eq([(t.replace(SEP, ""), c) for t, c in bu2][2:], [("Charge: 20 energy - swing +0.8, thrust +2.3", bu2[2][1]), ("Fills 25% slower (Untiered)", str(Defs.C_BAD))],
         "X tooltip: a slower Untiered row (-25): gains x 0.75, the red line")
    m.put("Weapon_Sword_UT_Paperweight", JClass("java.lang.Integer").valueOf(25))
    K.eq(block("Weapon_Longsword_Iron", doc("rare")), [("Ability 1 - none", "#7f93a6")], "X tooltip: a weapon with none = one grey line")
    K.eq(block("Weapon_Battleaxe_Iron", doc("rare"))[0][0], "Ability 1 - Whirlwind (battleaxe)", "X tooltip: the battleaxe heading")
    K.eq(block("Zweihander", doc("mythic", 75))[2][0].replace(SEP, ""), "Charge: 8 energy - swing +1.6, charged swing +3.1", "X tooltip: the pack Mythic Zweihander (Lv 75 = T12, 56 %)")
    Cfg.SIG_TIP = False
    K.eq(block("Weapon_Sword_Iron", doc("rare")), [], "X sig.tooltip off: no block")
    Cfg.SIG_TIP = True
    alls = []
    for i in list(ITEMS) + [wid]:
        for r in ("rare", "mythic", "untiered"):
            alls += [t.replace(SEP, "") for t, c in block(i, doc(r, 95))]
    K.check(alls and max(len(t) for t in alls) <= 70, "X every block line <= 70 characters (longest %d)" % max(len(t) for t in alls))
    # the x w gains (a tier hit weight; the bare JVM has no tier effect, so charge() is driven directly)
    ch = SX.charge(20, JString("swing +1~, thrust +3~"), 1.4, 1.0)
    K.eq(str(ch[0]).replace(SEP, ""), "Charge: 20 energy - swing +1.4, thrust +4.2", "X a Slow sword (w 1.4): the tap gains x w")
    ch = SX.charge(8, JString("swing +1~, charged swing +2"), 0.6, 1.5)
    K.eq(str(ch[0]).replace(SEP, ""), "Charge: 8 energy - swing +0.9, charged swing +3", "X a Fast mace (w 0.6) at x 1.5: only the tap gain x w, both x the rate")
    K.eq(float(SX.hitW(JString("Weapon_Sword_Iron"), doc("rare"))), 1.0, "X hitW: no speed tier = 1")
    # GearView.seg -> one child per segment, its colour
    msg = GV.seg(JString(b[2][0]), JString(b[2][1]))
    kids = msg.getChildren()
    K.eq([(str(kids.get(k).getRawText()), str(kids.get(k).getColor())) for k in range(kids.size())],
         [("Charge: ", "#d6e4ee"), ("20 energy", "#e8c25a"), (" - ", "#d6e4ee"), ("swing ", "#d6e4ee"), ("+1", "#7ee08a"), (", thrust ", "#d6e4ee"), ("+3", "#7ee08a")],
         "X GearView.seg: the Charge line = 7 coloured children")
    ms = GV.seg(JString("plain"), JString("#123456"))
    K.eq((str(ms.getRawText()), str(ms.getColor())), ("plain", "#123456"), "X GearView.seg: a one-colour line unchanged")
    # plain(): through GearView.lines when the bare JVM can run it (it reads many tables); else the fold is checked on its own text
    try:
        pl = [str(x) for x in GV.plain(JString("Weapon_Sword_Iron"), doc("rare", 10), None)]
        K.notes.append("X plain(Weapon_Sword_Iron): %s" % pl)
        K.check([x for x in pl if x == "Ability 1 - Vortexstrike - Charge: 20 energy - swing +1, thrust +3"]
                and not [x for x in pl if SEP in x or "Spin slash" in x], "X plain(): the block folded into one line (no sentence - the Auctions box fits), no joints left")
    except Exception as ex:
        K.notes.append("X plain() could not run in the bare JVM (%s) - UNVERIFIED there" % str(ex)[:160])

    # ---- the rate step (pure; then on a REAL EntityStatMap)
    u = UUID.fromString("00000000-0000-0000-0000-0000000005a1")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    un = fu.get(None)
    fl = dict((str(f.getName()), f) for f in IS.class_.getDeclaredFields())

    def stack(iid, gd):
        s_ = un.allocateInstance(IS.class_)
        md = BD()
        if gd is not None:
            md.put(str(Defs.DOC_KEY), gd)
        for n_, v_ in (("itemId", JString(iid)), ("quantity", JInt(1)), ("metadata", md)):
            fl[n_].setAccessible(True)
            fl[n_].set(s_, v_)
        return s_
    myt = stack("Weapon_Sword_Iron", doc("mythic", 1))
    st = lambda i, slot, h, v, mx, now, busy=False: float(SX.step(u, JString(i) if i else None, slot, h, JFloat(v), JFloat(mx), busy, now))
    R = []
    R.append(st("Weapon_Sword_Iron", 0, myt, 0.0, 20.0, 1000))          # baseline
    R.append(st("Weapon_Sword_Iron", 0, myt, 1.0, 20.0, 1300))          # inside the 0.75 s settle window (a kept-charge restore)
    R.append(st("Weapon_Sword_Iron", 0, myt, 2.0, 20.0, 2000))          # a rise of 1 -> +0.4
    R.append(st("Weapon_Sword_Iron", 0, myt, 2.4, 20.0, 2050))          # our own add is no rise
    R.append(st("Weapon_Sword_Iron", 0, myt, 5.4, 20.0, 2100))          # +3 (a thrust) -> +1.2
    R.append(st("Weapon_Sword_Iron", 0, myt, 19.6, 20.0, 2200))         # +13 -> capped at the max 20
    R.append(st("Weapon_Sword_Iron", 0, myt, 0.0, 20.0, 2300))          # the signature fired: a drop re-baselines
    R.append(st("Weapon_Sword_Iron", 0, myt, 1.0, 20.0, 2400))          # +1 -> +0.4 again
    K.eq([round(x, 4) for x in R], [0.0, 0.0, 0.4, 0.0, 1.2, 0.4, 0.0, 0.4], "X step: baseline, settle, x1.4 rises, never our own add, cap, drop")
    K.eq(round(float(SX.W.get(u)[2][0]), 4), 1.4, "X ... the baseline holds the value after our add")
    R = [st("Weapon_Sword_Iron", 1, myt, 5.0, 20.0, 2500), st("Weapon_Sword_Iron", 1, myt, 6.0, 20.0, 2600),
         st("Weapon_Sword_Iron", 1, myt, 7.0, 20.0, 3400)]
    K.eq([round(x, 4) for x in R], [0.0, 0.0, 0.4], "X a hotbar slot change re-baselines + settles (the kept charge is never multiplied)")
    R = [st("Weapon_Mace_Iron", 1, stack("Weapon_Mace_Iron", doc("mythic", 1)), 7.0, 8.0, 3500), st("Weapon_Mace_Iron", 1, myt, 8.0, 8.0, 4500, True)]
    K.eq(R, [0.0, 0.0], "X an item change and profile busy re-baseline")
    nrm = stack("Weapon_Sword_Iron", doc("rare", 10))
    R = [st("Weapon_Sword_Iron", 2, nrm, 0.0, 20.0, 5000), st("Weapon_Sword_Iron", 2, nrm, 3.0, 20.0, 6000)]
    K.eq(R, [0.0, 0.0], "X a normal (Rare) sword: never touched")
    slow = stack("Weapon_Sword_UT_Paperweight", doc("untiered", 15))
    m.put("Weapon_Sword_UT_Paperweight", JClass("java.lang.Integer").valueOf(-25))
    R = [st("Weapon_Sword_UT_Paperweight", 3, slow, 0.0, 20.0, 7000), st("Weapon_Sword_UT_Paperweight", 3, slow, 4.0, 20.0, 8000)]
    K.eq([round(x, 4) for x in R], [0.0, -1.0], "X a slower Untiered row (-25): a rise of 4 gives 1 back")
    m.put("Weapon_Sword_UT_Paperweight", JClass("java.lang.Integer").valueOf(25))
    top = stack("Weapon_Sword_Iron", doc("mythic", 95))
    R = [st("Weapon_Sword_Iron", 4, top, 0.0, 20.0, 9000), st("Weapon_Sword_Iron", 4, top, 1.0, 20.0, 10000)]
    K.eq([round(x, 4) for x in R], [0.0, 0.6], "X a T15 Mythic: x 1.6")
    Cfg.SIG_MHI = 0
    Cfg.SIG_MLO = 0
    Cfg.EPOCH = int(Cfg.EPOCH) + 1
    K.eq(st("Weapon_Sword_Iron", 4, top, 2.0, 20.0, 11000), 0.0, "X a config edit (epoch moved) re-reads the rate: Mythic 0 % = untouched")
    Cfg.SIG_MLO, Cfg.SIG_MHI = 40, 60
    Cfg.EPOCH = int(Cfg.EPOCH) + 1
    K.eq(round(st("Weapon_Sword_Iron", 4, top, 3.0, 20.0, 12000), 4), 0.6, "X ... and back to 60 %")
    # review fix: a Server Setup edit of the field-bound sig.mythic.* rows does NOT bump EPOCH - the held Mythic must still re-read the rate
    ep0 = int(Cfg.EPOCH)
    Cfg.SIG_MHI = 20
    K.eq(round(st("Weapon_Sword_Iron", 4, top, 4.6, 20.0, 12500), 4), 0.2, "X fix: sig.mythic.high 60 -> 20 (no epoch bump) reaches the HELD T15 Mythic: x 1.2")
    Cfg.SIG_MLO = 0
    Cfg.SIG_MHI = 0
    K.eq(st("Weapon_Sword_Iron", 4, top, 5.8, 20.0, 12600), 0.0, "X fix: both rows 0 (no epoch bump): the held Mythic is untouched")
    Cfg.SIG_MLO, Cfg.SIG_MHI = 40, 60
    K.eq(round(st("Weapon_Sword_Iron", 4, top, 6.8, 20.0, 12700), 4), 0.6, "X fix: rows back (no epoch bump): x 1.6 again")
    K.eq(int(Cfg.EPOCH), ep0, "X fix: the cases above never moved EPOCH")
    K.eq(st("Weapon_Sword_Iron", 4, top, 4.0, 0.0, 13000), 0.0, "X a meter of max 0: nothing")
    SX.forget(u)
    K.check(SX.W.get(u) is None, "X forget drops the player")

    # ---- the REAL EntityStatMap: SignatureEnergy (Min 0 / Max 0, Shared - Assets.zip) at index 0
    ENGK = "com.hypixel.hytale.server.core."
    ESTk = JClass(ENGK + "modules.entitystats.asset.EntityStatType")
    DSTk = JClass(ENGK + "modules.entitystats.asset.DefaultEntityStatTypes")
    ESMk = JClass(ENGK + "modules.entitystats.EntityStatMap")

    def acf(cls_name, name):
        f_ = JClass(cls_name).class_.getDeclaredField(name)
        f_.setAccessible(True)
        return f_
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyySig1FakeStore", AS.class_.getName() and jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyySig1FakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FKC = fake.toClass(AS.class_)
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMz = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
    est = un.allocateInstance(ESTk.class_)
    for n_, v_ in (("id", JString("SignatureEnergy")),):
        acf(ESTk.class_.getName(), n_).set(est, v_)
    for n_ in ("initialValue", "min", "max"):
        acf(ESTk.class_.getName(), n_).setFloat(est, JFloat(0.0))
    acf(ESTk.class_.getName(), "shared").setBoolean(est, True)
    am = un.allocateInstance(ILT.class_)
    acf(DAMz.class_.getName(), "assetMapLock").set(am, JClass("java.util.concurrent.locks.StampedLock")())
    hm = HM()
    hm.put("SignatureEnergy", est)
    acf(DAMz.class_.getName(), "assetMap").set(am, hm)
    acf(ILT.class_.getName(), "keyToIndexLock").set(am, JClass("java.util.concurrent.locks.StampedLock")())
    kti = JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")()
    kti.defaultReturnValue(-2147483648)
    kti.put(JString("SignatureEnergy"), JInt(0))
    arr = JArray(JAWM)(1)
    arr[0] = est
    acf(ILT.class_.getName(), "keyToIndex").set(am, kti)
    acf(ILT.class_.getName(), "array").set(am, arr)
    acf(ILT.class_.getName(), "nextIndex").set(am, JClass("java.util.concurrent.atomic.AtomicInteger")(1))
    store = un.allocateInstance(FKC)
    acf(AS.class_.getName(), "assetMap").set(store, am)
    acf(ESTk.class_.getName(), "ASSET_STORE").set(None, store)
    acf(DSTk.class_.getName(), "SIGNATURE_ENERGY").setInt(None, JInt(0))
    esm = ESMk()
    esm.update()
    E = int(DSTk.getSignatureEnergy())
    sv = lambda: (float(esm.get(E).get()), float(esm.get(E).getMax()))
    K.eq((E, sv()), (0, (0.0, 0.0)), "X real EntityStatMap: SignatureEnergy at 0, value 0, max 0 (no weapon meter)")
    K.eq(int(SX.packApply(esm, E, JString("Zweihander"))), 1, "X packApply: the Zweihander in hand puts skyygear_sig")
    K.eq(sv(), (0.0, 8.0), "X ... the meter max is 8 (Groundslam can fill)")
    K.eq(int(SX.packApply(esm, E, JString("Zweihander"))), 0, "X ... the next tick keeps it (no re-put)")
    # the pack meter charging: the engine's hit gain (+1) seen by the rate step at the Zweihander's Mythic T12 rate, applied with addStatValue
    zw = stack("Zweihander", doc("mythic", 75))
    float(SX.step(u, JString("Zweihander"), 0, zw, JFloat(0.0), JFloat(8.0), False, 20000))
    esm.addStatValue(E, JFloat(1.0))
    a1 = float(SX.step(u, JString("Zweihander"), 0, zw, JFloat(esm.get(E).get()), JFloat(esm.get(E).getMax()), False, 21000))
    esm.addStatValue(E, JFloat(a1))
    K.eq((round(a1, 4), round(sv()[0], 4)), (0.56, 1.56), "X the Zweihander charges: +1 hit gain + 0.56 (Mythic T12 56 %) on the real map")
    for _k in range(10):
        esm.addStatValue(E, JFloat(1.0))
        a = float(SX.step(u, JString("Zweihander"), 0, zw, JFloat(esm.get(E).get()), JFloat(esm.get(E).getMax()), False, 22000 + _k))
        esm.addStatValue(E, JFloat(a))
    K.eq(sv(), (8.0, 8.0), "X ... and fills to its meter 8 (never above): Groundslam can fire")
    K.eq(int(SX.packApply(esm, E, JString("DualRuneBlade"))), 1, "X DualRuneBlade: the modifier is re-put at 27")
    K.eq(sv()[1], 27.0, "X ... max 27 (Razorstrike)")
    K.eq(int(SX.packApply(esm, E, JString("Weapon_Sword_Iron"))), 2, "X another hand: the modifier goes")
    K.eq(sv()[1], 0.0, "X ... max back to 0")
    K.check(esm.getModifier(E, JString("skyygear_sig")) is None, "X ... no skyygear_sig left")
    SX.packApply(esm, E, JString("Zweihander"))
    Cfg.SIG_PACK = False
    K.eq((int(SX.packApply(esm, E, JString("Zweihander"))), sv()[1]), (2, 0.0), "X sig.packMeter off removes it while held (back to dead)")
    Cfg.SIG_PACK = True
    ITEMS["Zweihander"] = ("Root_Weapon_Mace_Signature_Groundslam", 8.0)
    K.eq(int(SX.packApply(esm, E, JString("Zweihander"))), 0, "X a pack update that gives it its own meter: no modifier")
    K.eq([int(SX.packApply(esm, E, None)), int(SX.packApply(None, E, JString("Zweihander")))], [0, 0], "X an empty hand / no stat map: nothing, no crash")
    K.notes.append("X status: %s" % str(SX.statusText()))
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
    K.check("0.3.43" not in txt and "sig.mythic" not in txt and "sig.ut." not in txt, "D 0.3.43 writes no row of its own (no migration)")
    K.check(bool(Cfg.SIG_TIP) and int(Cfg.SIG_MLO) == 40 and int(Cfg.SIG_MHI) == 60 and bool(Cfg.SIG_PACK), "D the live file without the lines = the defaults")
    K.notes.append("D files changed by start 1 (older rounds' one-time updates the live world has not run yet): %s" % sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))[:8])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
