"""Harness for SkyyGear 0.3.50 (round can1: THE WATERING CAN PROGRESSION - tools/gear_0_3_50_patch.py header).
Build first:
    python tools/gear_0_3_50_patch.py && python SkyyGear/build_skyygear_0.3.50.py
    python SkyyGear/test_skyygear_0.3.50.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.49 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, two new classes (GearCanClock / GearCanTick), no command / system;
              the jar's non-class files = 0.3.49's (only manifest.json differs - no vanilla-derived LightLevel.json is shipped)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.49 -> 0.3.50 (EXPECT below)
  E  engine   (the 0.2.11 harness's bare server boot: vanilla pack + THIS jar) - every new code path EXECUTED:
              P  parsers: 16 / 6 values, the per-step lists, the 0.3.49 squares by internal tier, bad text = the default
              L  lines: canStep / canTop / canCap per step (3 x step, Lumen uncapped, 0 = no cap), the six can lines are lines (1 point a level),
                 Lasting Water belongs to no kind; buying on the Tools rules (cap refused with the can's own text)
              N  plan(): levels inside the cap, can:bonus:<uuid> levels, the ceilings, top can never dry, a foreign / plain can none
              U  the Upgrade (Tools) page for the can: six rows, "(Thorium cap)", no Lasting Water - every selector walked in order
              T  the tooltip: square, waterings, wet / fertilizer seconds, "Lv 12 / 15", the cap line
              W  the click on the REAL GearCanWater.interactWithBlock (seams CTX / SOIL / FLUID / SUPER / GIVE): dry soil = full wet time +
                 rewards; re-watered wet soil = 15 % shorter each time down to the 50 % floor, no rewards; dried soil starts over; drying soil
                 (<= 25 % left) = rewards; Bloom -> the fertilizer clock (new + refresh; vanilla fertilizer never touched); Growth Boost divided
                 by the live modifier product; Miracle Grow push + chat; Dew Harvest item; Farming XP through skill:fn:addxp; the top can's bar;
                 hold-and-sweep skips wet soil; capacity per level
              F  the fertilizer clock: fertTick (done / unloaded waits / gone dropped), the file (write, re-read), FERTMAX drops the earliest,
                 GearCanTick / GearCanClock run
              G  farm.lightGrowth in the REAL loaded LightLevel GrowthModifierAsset (applyLight, lightNow live edit), the Water / Fertilizer reads
              M  migrations: migrateCan2 on a 0.3.49-default file (CRLF kept, values moved, custom kept + noted, can.lastPct noted, History
                 snapshot, change-log rows, run once); can2Mig on registries (Iron 5/5/5/5 -> 23 freed, Crude cap lowered, history, once)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: migrateCan2 + every older update; load() twice leaves
              config.properties byte-identical; can2Mig on every live registry twice (the second does nothing; the history copy matches)
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client's soil darkening after a shortened wet time (scheduleTick at the new end); Miracle Grow's push
reaching the final stage through the engine's own tickFarming; a farming tick reading the written light modifier; chunk unload timing.
Scratch: tools/dev/scratch/can1/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.50"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "can1", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.49.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_50_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.49.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = ["GearCanClock", "GearCanTick"]
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],          # the version + the can rows
    "GearCan": ["+f AREA_D", "+f CLOCK", "+f FDIR", "+f FDIRTY", "+f FERT", "+f FERTMAX", "+f FERT_X", "+f GAME_PER_REAL", "+f GIVE", "+f LIGHT_AT", "+f LIGHT_VAN",
                "+f LIGHT_WHY", "+f MIRA_SEC", "+f STD_CROP", "+f USES_D", "+f WATER_X", "+f WETM", "+f WETMAX", "+f XPACC", "+m applyLight", "+m bonus", "+m clock",
                "+m cropItem", "+m cropOf", "+m fdir", "+m fertHas", "+m fertMark", "+m fertTick", "+m ffile", "+m fmap", "+m fsave", "+m gameSecOf", "+m giveDew", "+m hasCrop",
                "+m light", "+m lightNow", "+m ripeAt", "+m ripeBt", "+m modOf", "+m pick", "+m realSec", "+m remember", "+m setLight", "+m setWet", "+m sideOf", "+m thirstWait", "+m thirsty", "+m unfert",
                "+m usesOf", "+m wetLen", "+m wkey", "+m wname", "+m xp", "-m side", "-m uses", "~<clinit>", "~m after", "~m before", "~m cells", "~m checkArea",
                "~m checkUses", "~m lines", "~m parseNums", "~m plan", "~m statusText"],
    "GearCfg": ["+f CAN_DEW", "+f CAN_FSEC", "+f CAN_GMAX", "+f CAN_LCAPS", "+f CAN_MIRA", "+f CAN_MIRMAX", "+f CAN_REW", "+f CAN_RICH", "+f CAN_THIRST", "+f CAN_WFLOOR",
                "+f CAN_XP", "+f FARM_LIGHT", "+f H50_KEYS", "+f H50_MARK", "+f H50_MARK_ID", "+f H50_NEW", "+f H50_OLD", "+f H50_WHO", "+m h50Log", "+m h50Old",
                "+m h50Update", "+m migrateCan2", "-f CAN_LAST", "~<clinit>", "~m apply", "~m defaultsText"],
    "GearFx": ["~m forget"],
    "GearLL": ["+f CAN_OLDC", "+f PK_DEW", "+f PK_MIRA", "+f PK_RICH", "+m canCap", "+m canShort", "+m canStep", "+m canTop", "+m canUps", "~<clinit>", "~m isLine", "~m lineCap",
               "~m lines", "~m upEffect"],
    "GearLife": ["+m can2Hist", "+m can2Mig", "+m can2Old", "~m capWhy", "~m sweep0"],
    "LifePage": ["~m perkRow"],
    "SkyyGearPlugin": ["~m setup", "~m shutdown", "~m start"],
}
U = "00000000-0000-0000-0000-000000000350"
STEPS = ["Crude", "Copper", "Iron", "Bronze_SkyWynn", "Thorium", "Lead_SkyWynn", "Dusk_SkyWynn", "Cobalt", "Chromium_SkyWynn", "Azurvane_SkyWynn",
         "Adamantite", "Slag_SkyWynn", "Cinder_SkyWynn", "Mithril", "Titanium_SkyWynn", "Lumen_SkyWynn"]
CANS = ["Tool_WaterCan_" + s for s in STEPS]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.50 - build script') and g.count('VERSION = "0.3.50"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 2), "S no new system / command; two new classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(n for n in nb - na if not n.endswith(".class")), sorted(na - nb)), ([], []), "S no file added or removed (no LightLevel.json shipped)")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is manifest.json")
    K.check(not any("Farming/Modifiers" in n for n in nb), "S no Server/Farming/Modifiers file in the jar (the light value is set live)")
    K.check('("last", "Lasting Water", 5, 0,' in g and '("rich", "Rich Soil", 10, 1 << 5' in g and '"can.lastPct"' not in g.split("G312_ROWK = [")[1].split("]")[0],
            "S Lasting Water has no kind; Rich Soil appended; can.lastPct gone from the rows")
    K.save()


IDRX = re.compile(r"#([A-Za-z0-9]+)\s*\{")
SELRX = re.compile(r"#([A-Za-z0-9]+)")


def walk(cmds, have=()):
    have = set(have)
    miss = []
    for i, c in enumerate(cmds):
        t = str(c.type)
        sel = str(c.selector) if c.selector is not None else ""
        for n in SELRX.findall(sel):
            if n not in have:
                miss.append((i, t, sel))
        if "Append" in t or "Insert" in t:
            have.update(IDRX.findall(str(c.text) if c.text is not None else ""))
        elif t == "Remove":
            for n in SELRX.findall(sel)[-1:]:
                have.discard(n)
        elif t == "Clear":
            miss.append((i, t, sel + " (Clear: not modelled)"))
    return have, miss


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JDouble, JBoolean
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    us = E["us"]
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, LL, Life, Can, Tool = P("GearCfg"), P("Gear"), P("GearData"), P("GearLL"), P("GearLife"), P("GearCan"), P("GearTool")
    GCW = P("GearCanWater")
    Props, AL = JClass("java.util.Properties"), JClass("java.util.ArrayList")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    Inst = JClass("java.time.Instant")
    V3 = JClass("org.joml.Vector3i")
    HM = JClass("java.util.HashMap")
    u = UUID.fromString(U)
    u2 = UUID.fromString("00000000-0000-0000-0000-000000000351")
    sysp = JClass("java.lang.System").getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data")
    os.makedirs(os.path.join(data, "lifelong"), exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)
    LV = {"Farming": 40}
    br.put("skill:fn:level", PyFn(lambda a: JObject(JInt(LV.get(str(a[1]), 1)), "java.lang.Integer")))
    XP = []

    def addxp(a):
        XP.append((str(a[0]), str(a[1]), int(a[2]), str(a[3]), str(a[4])))
        return JBoolean(True)
    br.put("skill:fn:addxp", PyFn(addxp))

    def fld(cls, name):
        k = cls.class_
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)
    pr = us.allocateInstance(PR.class_)
    fld(PR, "uuid").set(pr, u)
    fld(PR, "username").set(pr, JString("Tester"))
    pr2 = us.allocateInstance(PR.class_)
    fld(PR, "uuid").set(pr2, u2)
    fld(PR, "username").set(pr2, JString("Other"))
    pk = str(Gear.pkey(u))
    CAN = int(LL.CAN)
    PKI = dict((str(LL.PK[i]), i) for i in range(len(LL.PK)))

    # ================================================================================== P parsers
    K.eq([int(x) for x in Can.parseNums(JString("1,3,5,7,9,11"), 1, 15, True)], [1, 3, 5, 7, 9, 11], "P 6 values still parse")
    K.eq(len(Can.parseNums(JString(str(Cfg.CAN_AREA)), 1, 15, True)), 16, "P the 16-value default parses")
    K.check(Can.parseNums(JString("1,3,5"), 1, 15, True) is None and Can.parseNums(JString("1,3,5,7,9,12"), 1, 15, True) is None
            and Can.checkArea(JString("can.area"), JString("2,3,5,7,9,11")) is not None and Can.checkUses(JString("can.uses"), JString(str(Cfg.CAN_USES))) is None,
            "P bad texts refused (3 values, an even side, a 0 side); the default uses list passes check=")
    sides = [int(Can.sideOf(JString(c))) for c in CANS]
    uses = [int(Can.usesOf(JString(c))) for c in CANS]
    K.eq(sides, [1, 3, 5, 7, 7, 9, 9, 9, 11, 11, 11, 11, 11, 11, 11, 11], "P squares per step (= 0.3.49's)")
    K.eq(uses, [30, 35, 40, 50, 60, 70, 80, 90, 100, 110, 120, 135, 150, 165, 180, 200], "P waterings per step (Crude 30)")
    apply(can__area="1,3,5,7,9,11", can__uses="20,30,40,60,80,100")
    K.eq(([int(Can.sideOf(JString(c))) for c in CANS], [int(Can.usesOf(JString(c))) for c in CANS][:3]),
         ([1, 3, 5, 7, 7, 9, 9, 9, 11, 11, 11, 11, 11, 11, 11, 11], [20, 30, 40]), "P the old 6-value form = 0.3.49 by internal tier (same squares)")
    apply(can__area="nonsense")
    K.eq(int(Can.sideOf(JString(CANS[4]))), 7, "P a bad can.area = the default (one WARN)")
    apply()

    # ================================================================================== L lines + caps
    K.eq([int(LL.canStep(JString(c))) for c in CANS], list(range(1, 17)), "L canStep 1..16")
    K.eq([bool(LL.canTop(JString(c))) for c in CANS], [False] * 15 + [True], "L only Lumen is the top")
    K.eq([int(LL.canCap(JString(c))) for c in CANS[:15]], [3 * i for i in range(1, 16)], "L cap = 3 x step (Crude 3 .. Titanium 45)")
    K.eq(int(LL.canCap(JString(CANS[15]))), int(LL.LINE_BIG), "L Lumen uncapped")
    apply(can__lineCapPerStep="0")
    K.eq(int(LL.canCap(JString(CANS[2]))), int(LL.LINE_BIG), "L can.lineCapPerStep 0 = no cap")
    apply()
    six = ["cap", "grow", "bloom", "rich", "mira", "dew"]
    K.check(all(bool(LL.isLine(PKI[n])) and int(LL.pkCost(PKI[n], 7)) == 1 and bool(LL.perkFor(CAN, PKI[n])) for n in six),
            "L the six can upgrades are lines: 1 point a level, no hard max")
    K.check(not bool(LL.perkFor(CAN, PKI["last"])) and not any(bool(LL.perkFor(k_, PKI["last"])) for k_ in range(len(LL.KIND))), "L Lasting Water belongs to no kind")
    reg = Props()
    reg.setProperty("can.id", CANS[0])
    reg.setProperty("can.uid", "harness-can")
    reg.setProperty("t1", "1")
    reg.setProperty("can2", "1")
    LL.REG.put(JString(pk), reg)
    LL.save(JString(pk), reg)
    r3 = [str(Life.buy(u, JInt(CAN), JInt(PKI["grow"]))) for _ in range(4)]
    K.check(all(x.startswith("+") for x in r3[:3]) and r3[3].startswith("-") and "tier it up for 3 more levels" in r3[3],
            "L Crude: Growth Boost 1-3 bought (1 point each), the 4th refused at the cap with the can's own text: %s" % r3)
    rr = str(Life.buy(u, JInt(CAN), JInt(PKI["rich"])))
    rl = str(Life.buy(u, JInt(CAN), JInt(PKI["last"])))
    K.check(rr.startswith("+") and rl.startswith("-") and int(LL.spent(reg, CAN)) == 4, "L Rich Soil bought; Lasting Water refused; spent = 4: %s / %s" % (rr, rl))

    # ================================================================================== N plan()
    BD, BI, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonString")
    dC = BD()
    dC.append("ll", BI(1)); dC.append("lo", BS(pk)); dC.append("lu", BS("harness-can"))
    for k_ in list(reg.keySet()):
        if str(k_).startswith("can.up."):
            reg.remove(k_)
    reg.setProperty("can.id", CANS[4])          # Thorium: step 5, cap 15
    for n_, v_ in (("cap", 20), ("grow", 12), ("bloom", 10), ("rich", 4), ("mira", 6), ("dew", 8)):
        reg.setProperty("can.up." + n_, str(v_))
    pl = [float(x) for x in Can.plan(u, JString(CANS[4]), dC, JDouble(100.0))]
    K.check(abs(pl[0] - 7) < 1e-9 and abs(pl[1] - 10800) < 1e-9 and abs(pl[2] - 100.0 / (60 * (1 + 15 * 0.1))) < 1e-9 and abs(pl[3] - 12) < 1e-9
            and abs(pl[4] - 20) < 1e-9 and pl[5] == 15 and abs(pl[9] - 4) < 1e-9 and abs(pl[10] - 3) < 1e-9 and abs(pl[11] - 8) < 1e-9
            and abs(pl[12] - 21600 * 1.2) < 1e-6, "N Thorium plan: 7x7, 10800 s, Capacity 20 works at the cap 15 (+150 %%), Growth 12 %%, Bloom 20 %%, Rich 4 = +20 %%, Miracle 3 %%, Dew 8 %%: %s" % pl)
    pl2 = [float(x) for x in Can.plan(u2, JString(CANS[4]), dC, JDouble(100.0))]
    K.check(pl2[3] == 0 and pl2[4] == 0 and pl2[10] == 0 and abs(pl2[2] - 100.0 / 60) < 1e-9, "N another player holding your can: no points")
    bo = HM()
    bo.put("grow", JObject(JDouble(100.0), "java.lang.Double")); bo.put("mira", JObject(JDouble(100.0), "java.lang.Double")); bo.put("dew", JString("x"))
    br.put("can:bonus:" + U, bo)
    pl3 = [float(x) for x in Can.plan(u, JString(CANS[4]), dC, JDouble(100.0))]
    br.remove("can:bonus:" + U)
    K.check(pl3[3] == 50 and pl3[10] == 25 and abs(pl3[11] - 8) < 1e-9, "N can:bonus levels add, then the ceilings (Growth 50 %%, Miracle 25 %%); a bad value = 0: %s" % pl3[:12])
    plT = [float(x) for x in Can.plan(u, JString(CANS[15]), dC, JDouble(100.0))]
    K.check(plT[2] == 0.0, "N the top (Lumen) can never runs dry")

    # ================================================================================== U the Upgrade (Tools) page
    def page(name):
        C = P(name)
        pg = us.allocateInstance(C.class_)
        k = C.class_
        done = False
        while k is not None and not done:
            for f in k.getDeclaredFields():
                if f.getType() == PR.class_:
                    f.setAccessible(True)
                    f.set(pg, pr)
                    done = True
            k = k.getSuperclass()
        return pg
    reg.setProperty("can.up.grow", "15")
    lp = page("LifePage")
    lp.sel = CAN
    lp.info = JString("")
    lp.epoch = JString("")
    lp.armK = -1
    b, ev = UCB(), UEB()
    lp.build(None, b, ev, None)
    hv, miss = walk(b.getCommands())
    unb = [str(e.selector) for e in ev.getEvents() if any(n not in hv for n in SELRX.findall(str(e.selector)))]
    K.check(not miss and not unb, "U every selector exists when its command runs + every binding's element: %s %s" % (miss[:3], unb[:3]))
    import json as _j
    tx = {}
    for c in b.getCommands():
        if str(c.type) == "Set" and str(c.selector).endswith(".Text"):
            v = str(c.data) if c.data is not None else ""
            try:
                o_ = _j.loads(v)
                v = o_.get("0", "") if isinstance(o_, dict) else str(o_)
            except Exception:
                pass
            tx[str(c.selector)[1:-5]] = v
    rows_ = dict((k, v) for k, v in tx.items() if re.match(r"SkyyGPk\d+N$", k))
    K.notes.append("U rows: %s" % sorted(rows_.values()))
    K.check(len(rows_) == 6 and not any("Lasting" in v for v in tx.values()) and any("Rich Soil" in v for v in rows_.values())
            and any("Growth Boost   Lv 15 / 15 (Thorium cap)" in v for v in rows_.values()),
            "U six can rows, Rich Soil / Miracle / Dew there, no Lasting Water, 'Lv 15 / 15 (Thorium cap)': %s" % sorted(rows_.values()))
    K.check(any("tier up for 3 more" in v for k, v in tx.items() if k.endswith("D")), "U the capped row says 'tier up for 3 more'")
    dsc = dict((k, v) for k, v in tx.items() if re.match(r"SkyyGPk\d+D$", k))
    K.check(all(len(v) <= 44 and "%" not in v for v in rows_.values())
            and all(v.startswith("Now ") and len(v) <= 60 for v in dsc.values()) and any("Now +15% growth" in v for v in dsc.values()),
            "U FIX 2: the bold label is only 'Name   Lv x / cap (Tier cap)' (<= 44 chars), the second line a short 'Now ... > Next ...' (<= 60): %s %s" % (sorted(rows_.values()), sorted(dsc.values())))

    # ================================================================================== T the tooltip
    canT = Data.put(IS(JString(CANS[4]), JInt(1)), dC, u)
    tt, tc = AL(), AL()
    Tool.lines(u, JString(CANS[4]), dC, tt, tc)
    tl = [str(x).replace(chr(2), "|") for x in tt]
    K.notes.append("T tooltip: %s" % tl)
    K.check(any("Waters 7x7 tilled soil (hold right-click and sweep)" in x for x in tl) and any("Waterings per fill |150|" in x for x in tl)
            and any("Soil stays wet |360 s|" in x for x in tl) and any("Fertilizer lasts |864 s|" in x for x in tl)
            and any("Growth Boost |Lv 15 / 15|" in x for x in tl) and any("At the Thorium cap (15)" in x for x in tl),
            "T the can tooltip: square, 150 waterings (60 +150 %%), 360 s wet, 864 s fertilizer, Lv 15 / 15, the cap line: %s" % tl)

    # ================================================================================== W the click (the REAL GearCanWater.interactWithBlock)
    ST = {"pr": pr, "held": None, "failed": False, "time": Inst.ofEpochSecond(JLong(1000000)), "axis": JArray(JInt)([0, -1]), "eye": None, "super": []}
    SOILS = {}
    GIVEN = []

    @JImplements("java.util.function.Function")
    class CtxFn(object):
        @JOverride
        def apply(self, o):
            op = str(o[0])
            if op == "pr":
                return ST["pr"]
            if op == "held":
                return ST["held"]
            if op == "set":
                ST["held"] = o[1]
                return None
            if op == "fail":
                ST["failed"] = True
                return None
            if op == "failed":
                return JBoolean(ST["failed"])
            if op == "time":
                return ST["time"]
            if op == "axis":
                return ST["axis"]
            return None

    @JImplements("java.util.function.Function")
    class SoilFn(object):
        @JOverride
        def apply(self, o):
            op = str(o[0])
            x, z = int(o[1]), int(o[3])
            s = SOILS.get((x, z))
            if op == "get":
                if s is None:
                    return None
                return JArray(JObject)([s["until"], JObject(JBoolean(s["fert"]), JClass("java.lang.Boolean")), JObject(JInt(s["y"]), JClass("java.lang.Integer"))])
            if op == "fert":
                if s is None:
                    return JBoolean(False)
                s["fert"] = True
                return JBoolean(True)
            if op == "grow":
                if s is None or s.get("crop") is None:
                    return JBoolean(False)
                s["crop"] = s["crop"] - int(o[4])
                return JBoolean(True)
            if op == "wet":
                s["until"] = Inst.ofEpochSecond(JLong(int(o[4])))
                return JBoolean(True)
            if op == "has":
                return JBoolean(s is not None and s.get("crop") is not None)
            if op == "crop":
                return JString("Plant_Crop_Wheat_Item")
            if op == "ripe":
                return JBoolean(s is not None and bool(s.get("ripe")))
            if op == "unfert":
                y_ = int(o[2])
                st_ = UNF.get((x, y_, z), 1)
                if st_ == 1 and s is not None:
                    s["fert"] = False
                return JObject(JInt(st_), JClass("java.lang.Integer"))
            return None
    UNF = {}

    @JImplements("java.util.function.Function")
    class FluidFn(object):
        @JOverride
        def apply(self, o):
            return JBoolean(False)

    @JImplements("java.util.function.Function")
    class SuperFn(object):
        @JOverride
        def apply(self, o):
            pos, side, dur = o[0], int(o[1]), int(o[2])
            ST["super"].append((side, dur))
            lo = (side - 1) // 2
            any_ = False
            for dz in range(side):
                for dx in range(-lo, side - lo):
                    s = SOILS.get((int(pos.x()) + dx, int(pos.z()) - dz))
                    if s is not None:
                        s["until"] = ST["time"].plusSeconds(JLong(dur))
                        any_ = True
            if not any_:
                ST["failed"] = True
            return None

    @JImplements("java.util.function.Function")
    class GiveFn(object):
        @JOverride
        def apply(self, o):
            GIVEN.append((str(o[1]), int(o[2])))
            return None
    Can.CTX = CtxFn()
    Can.SOIL = SoilFn()
    Can.FLUID = FluidFn()
    Can.SUPER = SuperFn()
    Can.GIVE = GiveFn()
    Can.RNG = JClass("java.util.Random")(JLong(7))
    w_ = GCW()
    IWB = [m for m in GCW.class_.getDeclaredMethods() if str(m.getName()) == "interactWithBlock"][0]
    IWB.setAccessible(True)
    POS = V3(JInt(0), JInt(64), JInt(0))

    def click(held, p_=pr, keep=False):
        if not keep:
            Can.LAST.clear()
        ST["pr"] = p_
        ST["held"] = held
        ST["failed"] = False
        ST["super"] = []
        IWB.invoke(w_, JArray(JObject)([None, None, None, None, held, POS, None]))
        return ST["held"]

    def soil(until_in=None, fert=False, crop=100000):
        SOILS.clear()
        SOILS[(0, 0)] = {"y": 63, "until": None if until_in is None else ST["time"].plusSeconds(JLong(until_in)), "fert": fert, "crop": crop}
        return SOILS[(0, 0)]

    def left():
        s = SOILS[(0, 0)]
        return None if s["until"] is None else int(s["until"].getEpochSecond()) - int(ST["time"].getEpochSecond())
    Can.applyLight()
    lt, wx, fx = float(Can.light()), float(Can.WATER_X), float(Can.FERT_X)
    K.notes.append("W light %s (%s), water x%s, fertilizer x%s" % (lt, Can.LIGHT_WHY, wx, fx))
    # plain levels: Growth 12, the rest 0 (Crude-free Thorium can, cap 15)
    for k_ in list(reg.keySet()):
        if str(k_).startswith("can.up."):
            reg.remove(k_)
    reg.setProperty("can.up.grow", "12")
    Can.WETM.clear()
    del XP[:]
    Can.XPACC.clear()
    s0 = soil()
    h1 = click(canT)
    want_push = int(0.12 * 86400 / (wx * 1.0 * lt))
    K.check(ST["super"] == [(7, 10800)] and left() == 10800 and s0["crop"] == 100000 - want_push and abs(float(h1.getDurability()) - (100 - 100.0 / 60)) < 1e-9,
            "W dry soil: vanilla's watering 7x7 / 10800 s, full wet time, Growth Boost 12 %% of a crop / (water x light) = %d game s, 1/60 of the bar: %s %s" % (want_push, ST["super"], s0["crop"]))
    # FIX (critic C2): a click on still-wet (not thirsty) soil = nothing happens: no water, no shorter wet time, no reward, one line why
    LL.TOLD.clear()
    c0, l0, d0 = s0["crop"], left(), float(h1.getDurability())
    h_w = click(h1)
    K.check(s0["crop"] == c0 and left() == l0 and ST["super"] == [] and abs(float(h_w.getDurability()) - d0) < 1e-12
            and "%s:canwet" % U in [str(x) for x in LL.TOLD.keySet()],
            "W FIX C2: a fresh click on still-wet soil: refused with the 'still wet' line - no water used, wet time kept (%s), no reward" % left())
    # dried soil starts over at the full time and gets the rewards again
    s0["until"] = ST["time"].minusSeconds(JLong(5))
    c0 = s0["crop"]
    click(canT)
    K.check(left() == 10800 and s0["crop"] < c0, "W soil that dried: the full 10800 s again + the Growth Boost")
    # drying soil (<= 25 % of its own wet time left) = thirsty: rewards, and the row goes on (shorter)
    s0["until"] = ST["time"].plusSeconds(JLong(2000))          # 2000 <= 25 % of 10800 (2700)
    c0 = s0["crop"]
    click(canT)
    K.check(s0["crop"] < c0 and left() == int(10800 * 0.85), "W drying soil (2000 s of 10800 left): rewards + one more in the row (9180 s): %s" % left())
    t0 = ST["time"]
    ST["time"] = t0.plusSeconds(JLong(9180 - 2600))          # 2600 s of ITS 9180 left: > 25 % (2295) - not thirsty (with 10800 it would be)
    c0 = s0["crop"]
    click(canT)
    K.check(s0["crop"] == c0 and left() == 2600 and ST["super"] == [], "W 2600 s of a 9180 s wet time left = not thirsty (the soil's OWN wet time is the yardstick): no reward, nothing changed (FIX C2)")
    ST["time"] = t0
    # Farming XP: 0.5 a thirsty soil, whole points through skill:fn:addxp
    xp_got = sum(x[2] for x in XP)
    K.check(xp_got == 1 and all(x[1] == "Farming" and x[3] == "gear:can" and x[4] == pk for x in XP) and abs(float(Can.XPACC.get(u)) - 0.5) < 1e-9,
            "W Farming XP: 3 thirsty waterings x 0.5 = 1 point paid (Farming, gear:can, the profile) + 0.5 waiting: %s %s" % (XP, Can.XPACC.get(u)))
    nx0 = len(XP)
    Can.XPACC.clear()
    for i in range(4):
        soil(crop=None)
        click(canT)
    K.check(len(XP) == nx0, "W bare tilled soil (no crop): watered, but no Farming XP")
    # thirsty re-waterings in a row: 15 % shorter each time, floor 50 %, rewards every time
    Can.WETM.clear()
    s0 = soil()
    click(canT)
    seq = []
    for i in range(7):
        s0["until"] = ST["time"].plusSeconds(JLong(int(left() * 0.2)))          # 20 % of its wet time left = thirsty
        c0 = s0["crop"]
        click(canT)
        seq.append(left())
        K.check(s0["crop"] < c0, "W a thirsty re-watering gives the Growth Boost (round %d)" % i)
    exp = []
    for n in range(1, 8):
        exp.append(max(int(10800 * max(0.85 ** n, 0.5) + 1e-6), 60))
    K.eq(seq, exp, "W re-watered drying soil dries faster each time (x0.85 a time, floor 50 %% = 5400 s)")
    # FIX C2, a mixed square: the dry cell is watered, the still-wet neighbour keeps ITS wet time (no penalty)
    Can.WETM.clear()
    s0 = soil()
    SOILS[(1, 0)] = {"y": 63, "until": ST["time"].plusSeconds(JLong(9000)), "fert": False, "crop": 100000}
    click(canT)
    K.check(left() == 10800 and int(SOILS[(1, 0)]["until"].getEpochSecond()) - int(ST["time"].getEpochSecond()) == 9000 and SOILS[(1, 0)]["crop"] == 100000,
            "W FIX C2 mixed square: dry cell 10800 s + reward, the still-wet neighbour keeps its 9000 s and gets nothing")
    # FIX A1 / C1: a RIPE crop - no Growth Boost, no XP
    Can.XPACC.clear()
    nx1 = len(XP)
    s0 = soil()
    s0["ripe"] = True
    n20 = int(Can.N[20])
    for i in range(3):
        s0["until"] = None
        click(canT)
    K.check(s0["crop"] == 100000 and len(XP) == nx1 and Can.XPACC.get(u) is None and int(Can.N[20]) == n20 + 3,
            "W FIX A1/C1 ripe crop watered 3x: no Growth Boost, no Farming XP, counted as ripe skips")
    K.check(not bool(Can.ripeBt(None)), "W ripeBt(null) = false")
    # Bloom 100 % -> the can's fertilizer clock; vanilla fertilizer (no entry) never touched; refresh
    reg.setProperty("can.up.bloom", "5")
    apply(can__bloomPct="20")
    Can.FERT.clear()
    Can.FDIR = Paths.get(os.path.join(scratch, "fert"))
    s0 = soil()
    click(canT)
    fm = Can.fmap(JString(""))
    K.check(s0["fert"] and int(fm.get(JString("0,63,0"))) == 1000000 + 21600 and "%s:canbloom" % U in [str(x) for x in LL.TOLD.keySet()],
            "W Bloom 100 %%: fertilized + a clock entry ending now + 21600 game s + the 'Bloom!' line: %s" % fm)
    ST["time"] = Inst.ofEpochSecond(JLong(1005000))
    s0["until"] = None
    reg.setProperty("can.up.rich", "4")
    click(canT)
    K.check(int(fm.get(JString("0,63,0"))) == 1005000 + int(21600 * 1.2), "W Bloom on the can's own fertilizer refreshes its clock (Rich Soil 4 = +20 %%): %s" % fm.get(JString("0,63,0")))
    reg.remove("can.up.bloom")
    ST["time"] = Inst.ofEpochSecond(JLong(1009000))
    s0["until"] = None
    click(canT)
    K.check(int(fm.get(JString("0,63,0"))) == 1009000 + int(21600 * 1.2), "W FIX C4: a plain thirsty watering (Bloom 0) refreshes the can's own fertilizer, no roll: %s" % fm.get(JString("0,63,0")))
    reg.setProperty("can.up.bloom", "5")
    ST["time"] = Inst.ofEpochSecond(JLong(1005000))
    fm.clear()
    s0 = soil(fert=True)
    click(canT)
    K.check(fm.isEmpty() and s0["fert"], "W vanilla / totem fertilizer (no clock entry): Bloom leaves it alone - it never wears off")
    # Growth Boost on fertilized soil: divided by water x fertilizer x light
    reg.remove("can.up.bloom")
    s0 = soil(fert=True)
    click(canT)
    K.eq(100000 - s0["crop"], int(0.12 * 86400 / (wx * fx * lt)), "W Growth Boost on fertilized soil = 12 %% of a crop / (water x fertilizer x light)")
    # Miracle Grow 100 % + Dew 100 %: the push, the chat line, one crop item
    reg.setProperty("can.up.mira", "10")
    reg.setProperty("can.up.dew", "10")
    apply(can__miraclePct="10", can__miracleMax="100", can__dewPct="10")
    del GIVEN[:]
    s0 = soil()
    n12 = int(Can.N[12])
    click(canT)
    K.check(100000 - s0["crop"] == int(Can.MIRA_SEC) and int(Can.N[12]) == n12 + 1 and GIVEN == [("Plant_Crop_Wheat_Item", 1)]
            and "%s:canmira" % U in [str(x) for x in LL.TOLD.keySet()] and "%s:candew" % U in [str(x) for x in LL.TOLD.keySet()],
            "W Miracle Grow 100 %%: a 400,000 s push, counted, chat; Dew Harvest 100 %% x share 1 = one Wheat to the player: %s" % GIVEN)
    del GIVEN[:]
    n12 = int(Can.N[12])
    for i in range(4):
        s0["until"] = None
        s0["ripe"] = True
        click(canT)
    K.check(GIVEN == [] and int(Can.N[12]) == n12, "W FIX A1/C1: Miracle 100 %% + Dew 100 %% on a RIPE crop, 4 waterings: no free crop, no miracle: %s" % GIVEN)
    apply(can__bloomPct="20")
    for n_ in ("mira", "dew", "rich"):
        reg.remove("can.up." + n_)
    K.eq(str(Can.cropOf(JString("*Plant_Crop_Wheat_Block_State_Definitions_StageFinal"))), "Plant_Crop_Wheat_Item", "W cropOf: a crop block state -> its item")
    K.check(Can.cropOf(JString("Plant_Crop_Nothing_Block")) is None and Can.cropOf(JString("Rock_Stone")) is None, "W cropOf: no such item / no crop = null")
    # the top can: the bar never goes down; capacity per level
    canL = Data.put(IS(JString(CANS[15]), JInt(1)), dC, u)
    reg.setProperty("can.id", CANS[15])
    soil()
    hL = click(canL)
    K.check(abs(float(hL.getDurability()) - float(canL.getDurability())) < 1e-9, "W the top (Lumen) can: the water bar does not move")
    reg.setProperty("can.id", CANS[4])
    reg.setProperty("can.up.cap", "10")
    soil()
    hc = click(canT)
    K.check(abs(float(hc.getDurability()) - (100 - 100.0 / (60 * 2.0))) < 1e-9, "W Capacity 10 = +100 %% waterings (the bar moves half as much)")
    reg.remove("can.up.cap")
    # hold-and-sweep: a repeat over wet (not thirsty) soil is skipped, no water
    s0 = soil(until_in=9000)
    n11 = int(Can.N[11])
    h_ = click(canT)
    h2 = click(h_, keep=True)
    K.check(int(Can.N[10]) >= 0 and abs(float(h2.getDurability()) - float(h_.getDurability())) < 1e-12, "W held on the same block: skipped, no water")
    # a foreign can
    soil()
    click(canT, p_=pr2)
    K.check(ST["failed"] and not ST["super"], "W another player's lifelong can waters nothing")
    # wetLen / remember / thirsty direct
    K.eq([int(Can.wetLen(JLong(10800), JInt(n))) for n in (0, 1, 2, 5, 20)], [10800, 9180, 7803, 5400, 5400], "W wetLen 0 / 1 / 2 / 5 / 20 in a row")
    apply(can__rewaterPct="0")
    K.eq(int(Can.wetLen(JLong(10800), JInt(3))), 10800, "W can.rewaterPct 0 = no faster drying")
    apply()
    Can.WETM.clear()
    for i in range(int(Can.WETMAX) + 5):
        Can.remember(JString("k%d" % i), JInt(0), JLong(10), JLong(5), JLong(9))
    K.check(int(Can.WETM.size()) <= int(Can.WETMAX), "W the wet memory stays at most %d (expired ones go first)" % int(Can.WETMAX))
    Can.WETM.clear()
    # FIX 2: the wait until thirsty (the refusal's "ready in about N s"), and soil wet longer than this can ever wets (0.3.49 can / sprinkler / restart)
    tnow = ST["time"]
    K.eq([int(Can.thirstWait(JString("q|0|0|0"), tnow.plusSeconds(JLong(r_)), JLong(r_))) for r_ in (20000, 10801, 9000, 2700, 100, 0)], [0, 0, 6300, 0, 0, 0],
         "W FIX 2 thirstWait, no memory: wet 20000 / 10801 s (longer than can.waterSec) = thirsty now; 9000 s = 6300 s to wait; 2700 / 100 / 0 = now")
    uq = tnow.plusSeconds(JLong(2600))
    Can.remember(JString("q|1|0|0"), JInt(1), JLong(9180), JLong(int(uq.getEpochSecond())), JLong(int(tnow.getEpochSecond())))
    K.eq([int(Can.thirstWait(JString("q|1|0|0"), uq, JLong(2600))), bool(Can.thirsty(JString("q|1|0|0"), uq, JLong(2600)))], [2600 - 2295, False],
         "W FIX 2 thirstWait with memory: 2600 s of ITS 9180 left = 305 game s to wait (~10 real s), not thirsty")
    Can.WETM.clear()
    # a still-wet click on soil a 0.3.49 can wet for 86400 s: thirsty at once (rewards), then remembered (a 2nd click is refused)
    s0 = soil(until_in=50000)
    c0 = s0["crop"]
    click(canT)
    c1 = s0["crop"]
    click(canT)
    K.check(c1 < c0 and s0["crop"] == c1, "W FIX 2: soil wet 50000 s (a 0.3.49 can) is thirsty at once - rewarded once, then remembered and refused: %s %s %s" % (c0, c1, s0["crop"]))
    Can.WETM.clear()

    # ================================================================================== F the fertilizer clock
    Can.FERT.clear()
    Can.FDIRTY.clear()
    fm = Can.fmap(JString("w1"))
    Can.fertMark(JString("w1"), JInt(1), JInt(63), JInt(1), JLong(100), JDouble(50.0))          # ends 150
    Can.fertMark(JString("w1"), JInt(2), JInt(63), JInt(2), JLong(100), JDouble(500.0))         # ends 600
    Can.fertMark(JString("w1"), JInt(3), JInt(63), JInt(3), JLong(100), JDouble(10.0))          # ends 110, unloaded
    Can.fertMark(JString("w1"), JInt(4), JInt(63), JInt(4), JLong(100), JDouble(10.0))          # ends 110, gone
    UNF.clear()
    UNF[(3, 63, 3)] = -1
    UNF[(4, 63, 4)] = 0
    SOILS.clear()
    SOILS[(1, 1)] = {"y": 63, "until": None, "fert": True, "crop": None}
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    wfake = us.allocateInstance(WLD.class_)
    try:
        fld(WLD, "name").set(wfake, JString("w1"))
        wname_ok = str(Can.wname(wfake)) == "w1"
    except Exception as e_:
        wname_ok = False
        K.notes.append("F World.name field: %s" % e_)
    K.check(wname_ok, "F a world's name for the clock file")
    done = int(Can.fertTick(wfake, JLong(200)))
    ks = sorted(str(x) for x in fm.keySet())
    K.check(done == 1 and ks == ["2,63,2", "3,63,3"] and not SOILS[(1, 1)]["fert"], "F fertTick at 200: the 150 one off (done), unloaded waits, gone dropped, 600 stays: %s" % ks)
    ff = os.path.join(scratch, "fert", "fert-w1.properties")
    K.check(os.path.isfile(ff) and "2,63,2=600" in open(ff).read() and "3,63,3=110" in open(ff).read(), "F the file was written (atomic, sorted)")
    Can.FERT.clear()
    K.eq(sorted(str(x) for x in Can.fmap(JString("w1")).keySet()), ks, "F a restart reads the file back")
    fa, fb = [os.path.basename(str(Can.ffile(JString(n_)))) for n_ in ("a b", "a_b")]
    K.check(fa != fb and fb == "fert-a_b.properties" and fa.startswith("fert-a_b-"), "F FIX 2: worlds 'a b' and 'a_b' get their own clock files: %s %s" % (fa, fb))
    UNF[(3, 63, 3)] = 1
    K.eq(int(Can.fertTick(wfake, JLong(1000))), 2, "F later: the loaded ones end")
    fm2 = Can.fmap(JString("cap"))
    for i in range(int(Can.FERTMAX) + 3):
        fm2.put(JString("%d,0,0" % i), JObject(JLong(1000 + i), "java.lang.Long"))
    Can.fertMark(JString("cap"), JInt(-1), JInt(0), JInt(0), JLong(5000), JDouble(5.0))
    K.check(int(fm2.size()) == int(Can.FERTMAX) and fm2.get(JString("0,0,0")) is None and fm2.get(JString("-1,0,0")) is not None,
            "F past %d entries the earliest ends go first" % int(Can.FERTMAX))
    Can.FERT.remove(JString("cap"))
    Can.FDIRTY.remove(JString("cap"))
    tk = P("GearCanTick")(wfake)
    tk.run()
    P("GearCanClock")().run()
    K.check(int(Can.clock()) == 0, "F GearCanTick / GearCanClock run; clock() with no world = 0 queued")
    K.check(int(Can.gameSecOf(wfake)) == 1005000, "F gameSecOf (seam) = the click time")

    # ================================================================================== G the light value in the REAL loaded asset
    GMA = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.farming.GrowthModifierAsset")
    a_ = None
    try:
        a_ = GMA.getAssetMap().getAsset(JString("LightLevel"))
    except Exception as e_:
        K.notes.append("G asset map: %s" % e_)
    if a_ is not None:
        ok = bool(Can.applyLight())
        K.check(ok and abs(float(a_.getModifier()) - 1.7) < 1e-9 and abs(float(Can.LIGHT_VAN) - 2.0) < 1e-9, "G farm.lightGrowth 1.7 written into the loaded LightLevel modifier (was 2): %s" % Can.LIGHT_WHY)
        apply(farm__lightGrowth="2.4")
        Can.lightNow(JString("farm.lightGrowth"))
        K.check(abs(float(a_.getModifier()) - 2.4) < 1e-9 and abs(float(Can.light()) - 2.4) < 1e-9, "G a Server Setup edit (after= lightNow) is live: x2.4")
        apply()
        Can.applyLight()
        K.check(abs(float(Can.WATER_X) - 2.5) < 1e-9 and abs(float(Can.FERT_X) - 2.0) < 1e-9, "G the Water / Fertilizer modifiers read from their assets (2.5 / 2)")
    else:
        K.notes.append("G the bare boot has no GrowthModifierAsset store - the write is tested on a real LightLevelGrowthModifierAsset object instead")
        K.check(not bool(Can.applyLight()) and "no LightLevel" in str(Can.LIGHT_WHY) and abs(float(Can.light()) - 2.0) < 1e-9, "G no asset store = refused cleanly (no WARN), the divisor uses vanilla 2")
    LLA = JClass("com.hypixel.hytale.builtin.adventure.farming.config.modifiers.LightLevelGrowthModifierAsset")
    la = us.allocateInstance(LLA.class_)
    fld(GMA, "modifier").setDouble(la, JDouble(2.0))
    Can.LIGHT_VAN = JDouble(-1.0)
    okw = bool(Can.setLight(la))
    K.check(okw and abs(float(la.getModifier()) - 1.7) < 1e-9 and abs(float(Can.LIGHT_VAN) - 2.0) < 1e-9 and abs(float(Can.light()) - 1.7) < 1e-9,
            "G setLight on a REAL LightLevelGrowthModifierAsset: its modifier 2 -> 1.7 (getModifier, the field every farming tick reads): %s" % Can.LIGHT_WHY)
    apply(farm__lightGrowth="2.4")
    okw2 = bool(Can.setLight(la))
    K.check(okw2 and abs(float(la.getModifier()) - 2.4) < 1e-9, "G a Server Setup value 2.4 is written the same way (live)")
    apply()
    Can.setLight(la)
    K.check(not bool(Can.setLight(JString("x"))), "G setLight on a non-asset = false")

    # ================================================================================== M migrations
    # (a) migrateCan2 on a 0.3.49-default file, CRLF
    cfgd = os.path.join(scratch, "cfg")
    os.makedirs(cfgd, exist_ok=True)
    fc = os.path.join(cfgd, "config.properties")
    t49 = fresh.replace(str(Cfg.H50_MARK) + "\n", "")
    for k_, o_, n_ in zip([str(x) for x in Cfg.H50_KEYS], [str(x) for x in Cfg.H50_OLD], [str(x) for x in Cfg.H50_NEW]):
        assert ("\n%s=%s\n" % (k_, n_)) in t49, k_
        t49 = t49.replace("\n%s=%s\n" % (k_, n_), "\n%s=%s\n" % (k_, o_ if k_ != "can.bloomPct" else "7"))
    t49 = t49.replace("\ncan.bloomPct=7\n", "\ncan.bloomPct=7\ncan.lastPct=20\n")
    raw = t49.replace("\n", "\r\n").encode("latin-1")
    open(fc, "wb").write(raw)
    Cfg.FILE = Paths.get(fc)
    m1 = str(Cfg.migrateCan2())
    t1 = open(fc, "rb").read()
    tt1 = t1.decode("latin-1")
    K.check("can.waterSec=10800\r\n" in tt1 and ("can.uses=%s\r\n" % str(Cfg.CAN_USES)) in tt1 and "can.capacityPct=10\r\n" in tt1 and "can.growPct=1\r\n" in tt1
            and "can.bloomPct=7\r\n" in tt1 and "can.lastPct=20\r\n" in tt1 and str(Cfg.H50_MARK_ID) in tt1 and tt1.count("\n") == tt1.count("\r\n"),
            "M migrateCan2: the 5 untouched lines moved, the custom Bloom kept, can.lastPct left, the marker added, CRLF kept")
    K.check("can.bloomPct=7 kept" in m1 and "can.lastPct=20 is no longer read" in m1, "M the notes: custom value kept, can.lastPct unread: %s" % m1[-400:])
    hist = os.path.join(cfgd, "config-history")
    K.check(os.path.isdir(hist) and any(open(os.path.join(hist, f_), "rb").read() == raw for f_ in os.listdir(hist) if os.path.isfile(os.path.join(hist, f_))),
            "M a History snapshot of the old bytes first")
    chl = os.path.join(cfgd, "config-changes.log")
    K.check(os.path.isfile(chl) and open(chl, encoding="latin-1").read().count("SkyyGear 0.3.50") >= 5, "M one change-log row (Undo) per moved line")
    K.eq(str(Cfg.migrateCan2()), "", "M a second start: nothing (the marker)")
    K.check(open(fc, "rb").read() == t1, "M ... and the file is byte-identical")
    open(fc, "w", encoding="latin-1", newline="").write(t49.replace("\ncan.growPct=4\n", "\ncan.growPct=3\n"))
    m2 = str(Cfg.migrateCan2())
    K.check("can.growPct=3" in open(fc, encoding="latin-1").read() and "its meaning changed" in m2, "M a hand-edited can.growPct is kept with the meaning-change note")
    Cfg.FILE = None
    # (b) can2Mig on registries
    def mkreg(name, can, lv):
        p_ = Props()
        p_.setProperty("can.id", can)
        p_.setProperty("t1", "1")
        for n_, v_ in lv.items():
            p_.setProperty("can.up." + n_, str(v_))
        k_ = "harness-" + name
        LL.REG.put(JString(k_), p_)
        LL.save(JString(k_), p_)
        return k_, p_
    k1, p1 = mkreg("iron", CANS[2], {"cap": 5, "grow": 5, "last": 5, "bloom": 5})
    b1 = open(str(LL.file(JString(k1))), "rb").read()
    r1 = bool(Life.can2Mig(pr, JString(k1), p1))
    h1f = os.path.join(data, "lifelong", "history", os.path.basename(str(LL.file(JString(k1)))).replace(".properties", "") + ".pre-can2.properties")
    K.check(r1 and p1.getProperty("can.up.last") is None and [p1.getProperty("can.up." + n) for n in ("cap", "grow", "bloom")] == ["5", "5", "5"]
            and p1.getProperty("can2") == "1" and int(LL.spent(p1, CAN)) == 15 and os.path.isfile(h1f) and open(h1f, "rb").read() == b1,
            "M can2Mig Iron 5/5/5/5: Lasting Water gone, the rest kept (cap 9), spent 38 -> 15 (23 free), history copy = the old bytes")
    K.check(not bool(Life.can2Mig(pr, JString(k1), p1)), "M can2Mig runs once")
    k2, p2 = mkreg("crude", CANS[0], {"cap": 5, "grow": 1, "last": 2})
    Life.can2Mig(pr, JString(k2), p2)
    K.check(p2.getProperty("can.up.cap") == "3" and p2.getProperty("can.up.grow") == "1" and p2.getProperty("can.up.last") is None and int(LL.spent(p2, CAN)) == 4,
            "M can2Mig Crude cap 5 -> 3 (its cap), grow 1 kept, spent 9 + 1 + 2 = 12 -> 4")
    k4, p4 = mkreg("lost", "Bogus_Can_Id", {"cap": 9, "grow": 9, "last": 2})
    r4 = bool(Life.can2Mig(pr, JString(k4), p4))
    K.check(r4 and p4.getProperty("can.up.last") is None and p4.getProperty("can.up.cap") == "9" and p4.getProperty("can2a") == "1" and p4.getProperty("can2") is None,
            "M FIX B1 can id off the ladder: Lasting Water gone, levels NOT cut to the Crude cap, can2a=1, can2 waits")
    K.check(not bool(Life.can2Mig(pr, JString(k4), p4)) and p4.getProperty("can.up.cap") == "9", "M FIX B1 ... a second look with the id still unknown changes nothing")
    p4.setProperty("can.id", CANS[1])
    r4b = bool(Life.can2Mig(pr, JString(k4), p4))
    K.check(r4b and p4.getProperty("can.up.cap") == "6" and p4.getProperty("can.up.grow") == "6" and p4.getProperty("can2") == "1" and int(LL.spent(p4, CAN)) == 12,
            "M FIX B1 ... once the id is a Copper can: cap / grow 9 -> 6 (its cap), can2=1, spent 12")
    K.check(not bool(Life.can2Mig(pr, JString(k4), p4)), "M FIX B1 ... then never again")
    k3, p3 = mkreg("none", CANS[0], {})
    K.check(not bool(Life.can2Mig(pr, JString(k3), p3)) and p3.getProperty("can2") == "1", "M nothing to change = just the marker")
    gl = open(os.path.join(data, "gear.log"), encoding="utf8", errors="replace").read() if os.path.isfile(os.path.join(data, "gear.log")) else ""
    K.notes.append("M gear.log can2: %s" % [l for l in gl.splitlines() if "LL-CAN2MIG" in l][:3])
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    LL, Life = JClass(PKG + "GearLL"), JClass(PKG + "GearLife")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2"]
    m0 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[:600])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    K.check(c1 == c0 or "0.3.50" in m0, "D only the 0.3.50 update changed the file: %r" % m0[:120])
    K.check(str(Cfg.H50_MARK_ID) in c1.decode("latin-1"), "D the live copy carries the migrateCan2 marker now")
    K.check(int(Cfg.CAN_SEC) == 10800 and str(Cfg.CAN_USES).startswith("30,") and abs(float(Cfg.FARM_LIGHT) - 1.7) < 1e-9, "D the live copy reads the new can defaults (no can.* lines there)")
    ld = os.path.join(home, "lifelong")
    res = []
    for fn in sorted(os.listdir(ld)) if os.path.isdir(ld) else []:
        if not fn.endswith(".properties"):
            continue
        pk = fn[:-len(".properties")]
        P_ = LL.reg(JString(pk))
        if bool(LL.bad(P_)):
            res.append((pk, "bad"))
            continue
        before = open(os.path.join(ld, fn), "rb").read()
        sp0 = int(LL.spent(P_, int(LL.CAN)))
        r1 = bool(Life.can2Mig(None, JString(pk), P_))
        after = open(os.path.join(ld, fn), "rb").read()
        r2 = bool(Life.can2Mig(None, JString(pk), P_))
        hf = os.path.join(ld, "history", pk + ".pre-can2.properties")
        res.append((pk, r1, P_.getProperty("can.id"), sp0, int(LL.spent(P_, int(LL.CAN)))))
        K.check(not r2 and open(os.path.join(ld, fn), "rb").read() == after, "D %s: can2Mig once (the second does nothing)" % pk)
        if r1:
            K.check(os.path.isfile(hf) and open(hf, "rb").read() == before and P_.getProperty("can.up.last") is None, "D %s: history copy = the old bytes, Lasting Water gone" % pk)
    K.notes.append("D registries: %s" % res)
    K.check(any(x[1] is True for x in res if len(x) > 2), "D at least one live registry had can levels to migrate")
    K.save()


if "--expect-dump" in sys.argv:
    EXPECT = {}
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
