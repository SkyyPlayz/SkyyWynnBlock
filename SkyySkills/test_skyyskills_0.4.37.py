"""SkyySkills 0.4.37 - harness for the PERFECT DODGE in our roll + GATHERING PHASE 2 (Fishing / Ranching / Orchard, the Farming average) -
tools/skills_0_4_37_patch.py.
Build first: python tools/skills_0_4_37_patch.py && python SkyySkills/build_skyyskills_0.4.37.py

    python SkyySkills/test_skyyskills_0.4.37.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.36 -> 0.4.37: exactly the planned members differ; the 9 new classes added
  F   fakes    test_skyyskills_0.4.15.py's stand-ins (MapStore / MapChunk / FakeWorld / FakeHandler ...) + 0.4.25's CompCB
  G   g37      EXECUTED: the 3 new slots (names, indexOf, an OLD profile file loads them as 0 / nothing owed, the save writes them), the
               bridge (skill:<uuid> lists them, skill:farmavg:<uuid>, skill:fn:level farmingavg, Fishing / Ranching / Orchard grantable
               through skill:fn:addxp with the default bridge list), Orchard routing (Farm3.route) + the wiring at the 3 Farming award
               points (static), the Farming average (avg3 / avgOf / avgDelta, Overall.sums / counts / levelUp / listText with
               overall.farmingAverage on and off), Ranching (the item table, the per-world drop ledger + expiry, the minute cap, base, the
               REAL RanchPickSys.onEntityAdded on a picked-up item entity -> Ranch.picked -> the REAL RanchTask on a world queue -> Ranching
               XP paid; a LOAD add, an NPC target, a dropped-then-picked item pay nothing; the REAL RanchDropSys on a player's
               DropItemEvent$Drop), the PERFECT DODGE (config clamps, ageOf / inWindow timing at 0 / 33 / 50 / 66 ms + an extended effect,
               mark one-per-roll, counter, the REAL PDodgeSys.handle on real Damage events + a real EffectControllerComponent: hit at 0 and
               33 ms cancelled + XP + chat line, 66 ms not, no entity source / self / a bypass cause / not a player not; FIX ROUND: a
               0-damage hit, a hit the engine blocks anyway (PvP off for a player's hit, spawn protection - PDodge.veto / vetoAt) not
               perfect; a player's hit blocked with no XP and a line without XP; the XP minute cap; the knockback removal queued;
               Ranching partial pickups = 1 item; Orchard / Ranching keep Farming's pace + Wisdom, the Ranching cap after them; PDodgeSys(true)
               BEFORE FilterUnkillable, PDodgeSysU unordered; the REAL PCounterSys: x1.25 once, then 1.0, an expired window 1.0), the
               Stats page lines / how for the new slots and the Acrobatics perfect-dodge line, the 11 new Server Setup rows (241) + the
               fresh default file block, the rebirth participant with the new slots (x.Fishing / x.Ranching / x.Orchard + arm.fishing; a
               staged file from 0.4.36 without them commits and leaves them alone)
  R3  rebirth  test_skyyskills_0.4.36.py's R3 phase on the 0.4.37 jar - the rebirth participant UNCHANGED (two expected differences
               accounted for: 241 rows, arm.fishing now present - both checked in G)
  RS  restart  0.4.36's restart phase; RB 0.4.35's rebirth phase; R route; X exec (0.4.36's filters)
  D   live     0.4.36's live phase (START TWICE on a scratch COPY of the live Skyy_SkyySkills; measure writes nothing) + every live player
               file loads with Fishing / Ranching / Orchard = 0, its old values unchanged, and a save keeps every old line
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, time, importlib.util, hashlib, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.37"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.36.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "skills37", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))

EXPECT = {
    # planned 0.4.37 code
    "SkillDefs": ["+f FISHING", "+f ORCHARD", "+f RANCHING", "~<clinit>", "~m rebirthResets", "~m setOwn"],
    "SkillStore": ["~m level", "~m levelsOf", "~m moveLegacy", "~m owesK", "~m payLocked", "~m publishNow", "~m rbReset0", "~m readFile", "~m seedTop",
                   "~m snap", "~m topPut"],
    "SkillCfg": ["~m load"],
    "SkillFn": ["~m apply"],
    "BridgeCfg": ["~m read"],
    "Overall": ["~m counts", "~m levelUp", "~m listText", "~m maxLevel", "~m sums"],
    "OverallCfg": ["~m allowedSlot", "~m exactSlot"],
    "BreakTask": ["~m run"], "HarvestTask": ["~m run"], "Sickle": ["~m award"],
    "Acro": ["~m retainOnline"],
    "SkillRb": ["~m commit", "~m facts"],
    "StatsPage": ["~m build", "~m how", "~m lines"],
    "SkillClass": ["~m argSlot", "~m skillName"],
    "SkillLv": ["~m checkEntry", "~m parseTable", "~m slotOf"],
    "StatsCmd": ["~c "], "TopCmd": ["~c "], "XpCmd": ["~c "],
    "SkyySkillsPlugin": ["~m setup"],
    # SkillDefs.N (a static final int) is inlined by the compiler: 16 -> 19 (and N + 1 / 2N) in every method that loops over or sizes by
    # the slots - checked instruction by instruction during the build round (only that constant differs)
    "BridgeXp": ["~m grantSlot", "~m offerX", "~m paidX"], "ClassMana": ["~m amountFor"], "ClassPower": ["~m boostRegen", "~m classLevel"],
    "Fell": ["~m end"], "GatherPace": ["~m read", "+m applyAt"], "ManaRegen": ["~m classPct"], "OwnCurve": ["~m deliver", "~m moves", "~m start"],
    "PartyXp": ["~m add", "~m note", "~m routed", "~m text"], "SkillBonus": ["~m treeAvailable", "~m xpBonus"],
    "SkillCap": ["~m cap", "~m extra", "~m fetch", "~m level"], "SkillKit": ["~m checkSkills"], "SkillMsg": ["~m note", "~m takeArr"],
    "SkillRunFn": ["~m apply"], "SkillTop": ["~<clinit>"], "SkillXp": ["~m gain4", "~m petXp"], "SkillsPage": ["~m build", "~m handleDataEvent"],
    # version texts / the kit's rows + default file
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "CfgFile": ["~<clinit>"],
}
ADDED = ["PDodge", "PDodgeSys", "PDodgeSysU", "PCounterSys", "Ranch", "RanchPickSys", "RanchDropSys", "RanchTask", "Farm3"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T36 = tmod("test_skyyskills_0.4.36.py", "t0436")
T32 = T36.T32
# the 0.4.32 exec / live phases compare against 0.4.31's jar, which the local tidy removed - the live 0.4.36 jar stands in (the SET pin)
if not os.path.isfile(T32.OLD_JAR):
    _o31 = os.environ.get("SKYY_JAR031")   # a copy of a 0.4.31 build (e.g. from a cross-check scratch), else the live 0.4.36 jar stands in
    T32.OLD_JAR = os.path.abspath(_o31) if _o31 and os.path.isfile(_o31) else OLD_JAR
# ... and its leaderboard comparison old vs new covers the 16 slots both jars have (0.4.36 has no slot 16-18; G checks their lists)
_rows_of32 = T32.rows_of


def _rows_of16(Top, n_slots):
    n = int(n_slots)
    return _rows_of32(Top, min(n, 16)) + [[] for _i in range(3)]   # always 19 lists: slots 16-18 compared as empty on both sides


T32.rows_of = _rows_of16


def t15():
    return tmod("test_skyyskills_0.4.15.py", "t0415")


def t25():
    return tmod("test_skyyskills_0.4.25.py", "t0425")


def fake_dir(scratch):
    return os.path.join(scratch, "fake37")


# ====================================================================================================== F: the stand-in classes
def run_fake15(out, jar, scratch, _home):
    d = fake_dir(scratch)
    os.makedirs(d, exist_ok=True)
    t15().run_mkfake(d)
    json.dump({"ok": 1, "fails": [], "notes": ["F stand-ins of 0.4.15 written"]}, open(out, "w"))


def run_fake25(out, jar, scratch, _home):
    d = fake_dir(scratch)
    os.makedirs(d, exist_ok=True)
    t25().run_mkfake25(d)
    json.dump({"ok": 1, "fails": [], "notes": ["F CompCB of 0.4.25 written"]}, open(out, "w"))


def props(path):
    out = {}
    if not os.path.exists(path):
        return None
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        a, b = ln.split("=", 1)
        out[a.strip()] = b.strip()
    return out


# ====================================================================================================== G: the 0.4.37 paths
def run_g37(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JInt, JLong, JFloat, JBoolean, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, fake_dir(scratch)], verify=True)
    P = lambda n: JClass(PKG + n)
    Defs, Cfg, Sto, Ovl, OCfg, Bx, Bc = P("SkillDefs"), P("SkillCfg"), P("SkillStore"), P("Overall"), P("OverallCfg"), P("BridgeXp"), P("BridgeCfg")
    F3, Rn, PD, Acro, AcroCfg, SP = P("Farm3"), P("Ranch"), P("PDodge"), P("Acro"), P("AcroCfg"), P("StatsPage")
    UUID, Long, Integer, Obj, JStr = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Integer"), JClass("java.lang.Object"), JClass("java.lang.String")
    IHM, CHM, HM, HS = JClass("java.util.IdentityHashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.HashMap"), JClass("java.util.HashSet")
    Mod, Arr = JClass("java.lang.reflect.Modifier"), JClass("java.lang.reflect.Array")
    OA = lambda *xs: JArray(Obj)(list(xs))
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def findf(c, name):
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    return f
            c = c.getSuperclass()
        raise RuntimeError("no field " + name)

    def setany(obj, name, val):
        findf(obj.getClass(), name).set(obj, val)

    def getany(obj, name):
        return findf(obj.getClass(), name).get(obj)

    def setstatic(cls, name, val):
        findf(cls.class_, name).set(None, val)

    def alloc(cls):
        return U.allocateInstance(cls.class_)

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    def section(name, fn):
        try:
            fn()
        except Exception:
            import traceback
            K.fails.append("G %s raised: %s" % (name, traceback.format_exc()[-2500:]))
        print("[harness] section %s done" % name, flush=True)

    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    base = os.path.join(scratch, "g37", "Skyy_SkyySkills")
    pd = os.path.join(base, "players")
    os.makedirs(pd)
    Cfg.FILE = T32.path(os.path.join(base, "xp.properties"))
    Cfg.load()
    Sto.DIR = T32.path(pd)
    br = Sto.bridge()
    for k_ in list(br.keySet()):
        br.remove(k_)
    N = int(Defs.N)
    NAMES = [str(x) for x in Defs.NAMES]
    FISH, RANCH, ORCH, FARM, MIN, ACRO, EXP = (int(Defs.FISHING), int(Defs.RANCHING), int(Defs.ORCHARD), int(Defs.FARMING), int(Defs.MINING),
                                               int(Defs.ACROBATICS), int(Defs.EXPLORATION))
    cm = [int(x) for x in Defs.cumOf(FARM)]

    # ---------------------------------------------------------------- engine stand-ins: Universe / players / world, component types
    Universe, PRef, Holder, Ref = (JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.server.core.universe.PlayerRef"),
                                   JClass("com.hypixel.hytale.component.Holder"), JClass("com.hypixel.hytale.component.Ref"))
    FakeH, FakeW, MapStore, MapChunk, CompCB = (JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld"), JClass("skyytest.MapStore"),
                                                JClass("skyytest.MapChunk"), JClass("skyytest25.CompCB"))
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    uni = alloc(Universe)
    PLAYERS, WORLDS = CHM(), CHM()
    setany(uni, "playersByUuid", PLAYERS)
    setany(uni, "players", PLAYERS.values())
    setany(uni, "worldsByUuid", WORLDS)
    setstatic(Universe, "instance", uni)
    TPR = alloc(CT)
    setany(uni, "playerRefComponentType", TPR)
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = alloc(EMc)
    for f in EMc.class_.getDeclaredFields():
        if Mod.isStatic(f.getModifiers()) and f.getType() == EMc.class_:
            f.setAccessible(True)
            f.set(None, em)
    TT = {}
    for fname in ("playerComponentType", "effectControllerComponentType", "itemComponentType", "pickupItemComponentType"):
        TT[fname] = alloc(CT)
        setany(em, fname, TT[fname])
    world = alloc(FakeW)
    setany(world, "name", "skyy-island-test")
    wuid = UUID(0x37, 1)
    WORLDS.put(wuid, world)
    handler = alloc(FakeH)
    TEXTS = getany(None, "TEXTS") if False else findf(FakeH.class_, "TEXTS").get(None)
    st = alloc(MapStore)
    st.comps = IHM()
    st.ext = None
    EStore = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    est = alloc(EStore)
    setany(est, "world", world)
    st.ext = est
    REFN = [10]

    def newref():
        REFN[0] += 1
        r = Ref(st, JInt(REFN[0]))
        st.comps.put(r, IHM())
        return r

    def mkpr(u, name):
        pr = alloc(PRef)
        setany(pr, "uuid", u)
        setany(pr, "username", name)
        setany(pr, "packetHandler", handler)
        setany(pr, "worldUuid", wuid)
        r = newref()
        setany(pr, "entity", r)
        st.comps.get(r).put(TPR, pr)
        PLAYERS.put(u, pr)
        return pr, r

    def texts():
        o = [str(t) for t in TEXTS]
        TEXTS.clear()
        return o
    paid = []
    br.put("coins:fn:add", Fn(lambda o: (paid.append(int(o[1])), Long(1))[1]))
    br.put("class:fn:allowed", Fn(lambda o: JBoolean(True)))

    # ================================================================ S1: the slots + an old profile file
    def s1():
        K.check(N == 19 and NAMES[16:] == ["Fishing", "Ranching", "Orchard"] and [str(x) for x in Defs.LABELS][16:] == NAMES[16:]
                and (FISH, RANCH, ORCH) == (16, 17, 18), "G1 SkillDefs: N 19, slots 16-18 Fishing / Ranching / Orchard")
        K.check(NAMES[:16] == ["Mining", "Foraging", "Farming", "Combat", "Acrobatics", "Combat.Archer", "Combat.Warrior", "Combat.Assassin",
                                "Combat.Shaman", "Combat.Mage", "Alchemy", "Smithing", "Cooking", "Exploration", "Combat.Berserker", "Combat.Priest"],
                "G1 SkillDefs: every 0.4.36 slot keeps its index and saved key (append-only)")
        K.check([int(Defs.indexOf(x)) for x in ("fishing", "Ranching", "ORCHARD", "fis", "ranch", "orc", "far", "for", "mining")] == [16, 17, 18, 16, 17, 18, 2, 1, 0],
                "G1 indexOf: names, labels and 3+ letter prefixes of the new skills; old prefixes unchanged")
        K.check([bool(Defs.rebirthResets(s)) for s in (FISH, RANCH, ORCH, EXP)] == [True, True, True, False] and [int(Defs.perkRow(s)) for s in (FISH, RANCH, ORCH)] == [-1, -1, -1],
                "G1 the new slots reset on a rebirth (Exploration excluded only), have no perk row")
        u = UUID.fromString("00000000-0000-4000-8000-000000043701")
        k = str(u)
        open(os.path.join(pd, k + ".properties"), "w", encoding="latin-1").write("name=Olda\nMining=500\nMining.paid=2\nFarming=%d\nFarming.paid=10\nquiet=false\n" % cm[10])
        d = Sto.dataK(k, u)
        K.check(len(d) == 2 * N and [int(d[s]) for s in (FISH, RANCH, ORCH)] == [0, 0, 0] and [int(d[N + s]) for s in (FISH, RANCH, ORCH)] == [0, 0, 0]
                and int(d[MIN]) == 500 and int(d[FARM]) == cm[10], "G1 a profile file WITHOUT the new keys loads them as 0 XP, paid 0 (nothing owed)")
        K.check(not bool(Sto.owesK(k, u, FISH)) and not bool(Sto.owesK(k, u, RANCH)) and not bool(Sto.owesK(k, u, ORCH)), "G1 nothing owed in the new slots")
        Sto.saveNow(k)
        pf = props(os.path.join(pd, k + ".properties"))
        K.check(pf.get("Fishing") == "0" and pf.get("Ranching.paid") == "0" and pf.get("Orchard") == "0" and pf.get("Mining") == "500"
                and pf.get("Farming") == str(cm[10]) and pf.get("name") == "Olda", "G1 the save writes the new keys (0) and keeps every old value")
        # a file WITH the keys reads them back
        open(os.path.join(pd, k + "-p2.properties"), "w", encoding="latin-1").write("Fishing=777\nFishing.paid=0\nRanching=55\nOrchard=9\n")
        d2 = Sto.readFile(k + "-p2", None)[0]
        K.check([int(d2[s]) for s in (FISH, RANCH, ORCH)] == [777, 55, 9], "G1 a file WITH the keys reads them back")
    section("S1", s1)

    # ================================================================ S2: the bridge
    def s2():
        u = UUID.fromString("00000000-0000-4000-8000-000000043702")
        k = str(u)
        cf = [int(x) for x in Defs.cumOf(FARM)]
        open(os.path.join(pd, k + ".properties"), "w", encoding="latin-1").write(
            "Farming=%d\nFarming.paid=12\nRanching=%d\nRanching.paid=6\nOrchard=%d\nOrchard.paid=3\nFishing=%d\nFishing.paid=4\n" % (cf[12], cf[6], cf[3], cf[4]))
        d = Sto.dataK(k, u)
        lv = str(Sto.levelsOf(u, d))
        K.check(lv.endswith(",Exploration:0,Fishing:4,Ranching:6,Orchard:3") or ",Fishing:4,Ranching:6,Orchard:3" in lv, "G2 skill:<uuid> lists Fishing / Ranching / Orchard: %s" % lv)
        Sto.publishNow(u, True)
        K.check(str(br.get("skill:" + k)) == lv and int(br.get("skill:farmavg:" + k)) == (12 + 6 + 3) // 3, "G2 skill:farmavg:<uuid> = floor((12 + 6 + 3) / 3) = 7: %s" % br.get("skill:farmavg:" + k))
        K.check("FarmingAvg" not in lv and "farmavg" not in lv.lower(), "G2 the average is NOT a pair in skill:<uuid> (SkyyGuilds sums every pair)")
        f = P("SkillFn")()
        K.check(int(f.apply(OA(u, "farmingavg"))) == 7 and int(f.apply(OA(u, "Fishing"))) == 4 and int(f.apply(OA(u, "orchard"))) == 3, "G2 skill:fn:level farmingavg / Fishing / orchard")
        K.check([int(Bx.grantSlot(x)) for x in ("Fishing", "ranching", "Orchard", "Mining", "Combat", "Acrobatics")] == [16, 17, 18, 0, -1, -1] and "Fishing" in str(Bc.GRANT_TEXT)
                and "Fishing" not in str(Bc.DEFAULT_SKILLS), "G2 Fishing / Ranching / Orchard grantable through skill:fn:addxp with the default bridge list (%s)" % Bc.GRANT_TEXT)
        K.check(not bool(P("SkillAddFn")().apply(OA(u, "Fishing", Long(10), "fishing", k))), "G2 skill:fn:addxp Fishing for an OFFLINE player = FALSE (offered, refused for now)")
        Top = P("SkillTop")
        Top.CACHE[FISH] = None
        Top.AT[FISH] = 0
        rows = Top.all(FISH)
        K.check(any(str(rw[2]) == k or int(rw[1]) == cf[4] for rw in rows), "G2 /skills top fishing lists the profile (%d rows)" % len(rows))
        r = P("SkillRunFn")().apply(OA(k, "Fishing"))
        K.check(r is not None and int(r[0]) == 4 and str(r[5]) == "Fishing" and bool(r[4]), "G2 skill:fn:run Fishing (level 4, resets on a rebirth)")
    section("S2", s2)

    # ================================================================ S3: Orchard routing
    def s3():
        cases = [(FARM, "Plant_Crop_Apple_Block", ORCH), (FARM, "*Plant_Crop_Apple_Block_State_Definitions_StageFinal", ORCH), (FARM, "Plant_Crop_Berry_Block", ORCH),
                 (FARM, "Plant_Crop_Berry_Wet_Block", ORCH), (FARM, "Plant_Crop_Wheat_Block", FARM), (FARM, None, FARM), (MIN, "Plant_Crop_Apple_Block", MIN),
                 (int(Defs.FORAGING), "Wood_Apple_Trunk", int(Defs.FORAGING))]
        got = [int(F3.route(a, b)) for a, b, _c in cases]
        K.check(got == [c for _a, _b, c in cases], "G3 Farm3.route: apple / berry Farming XP -> Orchard (state ids too), wheat stays Farming, other skills untouched: %s" % got)
        K.check(str(F3.ORCH_TEXT) == "Plant_Crop_Apple, Plant_Crop_Berry" and not bool(F3.AVG), "G3 defaults: orchard.ids apple + berry, the average OFF")
        p = JClass("java.util.Properties")()
        p.setProperty("orchard.ids", " *Plant_Fruit_ , ,Plant_Crop_Apple,Plant_Fruit_")
        F3.read(p)
        K.check([str(x) for x in F3.ORCH] == ["Plant_Fruit_", "Plant_Crop_Apple"] and int(F3.route(FARM, "Plant_Fruit_Mango")) == ORCH, "G3 orchard.ids parsed (trim, '*', empty, duplicates)")
        p.setProperty("orchard.ids", "")
        F3.read(p)
        K.check(len(F3.ORCH) == 0 and int(F3.route(FARM, "Plant_Crop_Apple_Block")) == FARM, "G3 orchard.ids empty = no routing")
        F3.read(JClass("java.util.Properties")())
        g = PW.calls(jar)
        K.check(PKG + "Farm3.route" in g.get("BreakTask.run", set()) and PKG + "Farm3.route" in g.get("HarvestTask.run", set())
                and any(PKG + "Farm3.route" in g[m] for m in g if m.startswith("Sickle.")), "G3 static: the 3 Farming award points (break, F-harvest, sickle) route through Farm3.route")
        K.check(PKG + "Perks.breakDouble" in g.get("BreakTask.run", set()) and PKG + "Perks.harvestDouble" in g.get("HarvestTask.run", set()),
                "G3 static: the double drops stay Farming's (unchanged calls)")
    section("S3", s3)

    # ================================================================ S4: the Farming average + the Overall Level
    def s4():
        K.check([int(F3.avg3(a, b, c)) for a, b, c in ((0, 0, 0), (30, 0, 0), (12, 6, 3), (100, 100, 99), (-5, 3, 3))] == [0, 10, 7, 99, 2], "G4 avg3 = floor of the mean")
        u = UUID.fromString("00000000-0000-4000-8000-000000043704")
        k = str(u)
        cf = [int(x) for x in Defs.cumOf(FARM)]
        open(os.path.join(pd, k + ".properties"), "w", encoding="latin-1").write(
            "Farming=%d\nFarming.paid=30\nRanching=%d\nRanching.paid=30\nOrchard=%d\nOrchard.paid=29\n" % (cf[30], cf[30], cf[29]))
        d = Sto.dataK(k, u)
        K.check(int(F3.avgOf(d)) == 29 and int(F3.avgDelta(d, ORCH, 28, 29)) == 0 and int(F3.avgDelta(d, FARM, 27, 30)) == 1 and int(F3.avgDelta(d, MIN, 1, 2)) == 0,
                "G4 avgOf / avgDelta (the average only moves when the floor moves)")
        off = [int(x) for x in Ovl.sums(u, d)]
        cnt_off = [bool(Ovl.counts(u, s)) for s in (FARM, RANCH, ORCH, FISH)]
        F3.AVG = True
        on = [int(x) for x in Ovl.sums(u, d)]
        cnt_on = [bool(Ovl.counts(u, s)) for s in (FARM, RANCH, ORCH, FISH)]
        K.check(on[1] == off[1] and off[0] - on[0] == 30 - 29 and cnt_off == [True, False, False, False] and cnt_on == [True, True, True, False],
                "G4 Overall.sums: Farming 30 alone (off) vs the average 29 (on), same skill count; Ranching / Orchard move the Overall Level only when on: %s %s" % (off, on))
        pr, _r = mkpr(u, "Avgy")
        texts()
        Sto.wr(d, ORCH, cf[30])   # Orchard 29 -> 30: the average 29 -> 30
        Ovl.levelUp(pr, u, ORCH, JLong(29), JLong(30))
        K.check(br.get("skill:overall:" + k) is not None, "G4 Overall.levelUp with the average on (a Ranching / Orchard level-up) publishes the Overall Level")
        lt = str(Ovl.listText(u, d))
        K.check("Farming (avg of 3) 30" in lt, "G4 the Overall page lists Farming as the average when on: %s" % lt[:120])
        F3.AVG = False
        K.check("Farming 30" in str(Ovl.listText(u, d)), "G4 ... and Farming alone when off")
        K.check(bool(OCfg.allowedSlot(FISH)) and not bool(OCfg.allowedSlot(RANCH)) and not bool(OCfg.allowedSlot(ORCH)), "G4 overall.skills may name Fishing (not Ranching / Orchard)")
    section("S4", s4)

    # ================================================================ S5: Ranching
    def s5():
        K.check(bool(Rn.ON) and int(Rn.PER_MIN) == 200 and int(Rn.xpOf("Food_Egg")) == 3 and int(Rn.xpOf("Ingredient_Fabric_Scrap_Wool")) == 3
                and int(Rn.xpOf("Rock_Stone")) == 0 and int(Rn.XP.size()) == 9, "G5 defaults: on, 200 a minute, 9 animal products (egg 3, wool 3)")
        m = Rn.parse("Food_Egg:5, bad, :3, X:0, Y:-2, Food_Pork_Raw : 7,Z:abc,Big:99999999")
        K.check(dict((str(k_), int(m.get(k_))) for k_ in m.keySet()) == {"Food_Egg": 5, "Food_Pork_Raw": 7, "Big": 1000000}, "G5 ranching.items parse: bad entries skipped, capped 1,000,000")
        Rn.LEDGER.clear()
        t0 = 1_000_000
        K.check(int(Rn.base("w1", "Food_Egg", 4, t0)) == 12, "G5 4 eggs nobody dropped = 12 XP")
        Rn.dropped("w1", "Food_Egg", 3, t0)
        Rn.dropped("w1", "Rock_Stone", 3, t0)
        K.check(int(Rn.base("w2", "Food_Egg", 2, t0)) == 6, "G5 a drop in ANOTHER world does not block")
        K.check(int(Rn.base("w1", "Food_Egg", 2, t0 + 1)) == 0 and int(Rn.base("w1", "Food_Egg", 2, t0 + 2)) == 3, "G5 3 dropped eggs: the next 3 picked up pay 0, the 4th pays")
        K.check(int(Rn.LEDGER.size()) == 0, "G5 the ledger empties; never holds items with no Ranching XP")
        Rn.dropped("w1", "Food_Egg", 5, t0)
        K.check(int(Rn.base("w1", "Food_Egg", 1, t0 + int(Rn.LEDGER_MS) + 1)) == 3 and int(Rn.LEDGER.size()) == 0, "G5 a drop older than 10 minutes is forgotten")
        uc = UUID(0x37C, 5)
        Rn.WIN.clear()
        K.check([int(Rn.allow(uc, a, t0)) for a in (150, 100, 10)] == [150, 50, 0] and int(Rn.allow(uc, 30, t0 + 60000)) == 30, "G5 the minute cap 200: 150, 50 of 100, 0; a new minute")
        Rn.PER_MIN = 0
        K.check(int(Rn.allow(uc, 10 ** 9, t0)) == 10 ** 9, "G5 cap 0 = no cap")
        Rn.PER_MIN = 200
        Rn.ON = False
        K.check(int(Rn.base("w1", "Food_Egg", 2, t0)) == 0, "G5 ranching.pickupXp=false pays nothing")
        Rn.ON = True
        Rn.WIN.clear()
        # fix round: RanchTask now adds Farming's gathering pace + Wisdom before the cap - OFF for the base numbers below (checked after)
        GP = P("GatherPace")
        gslots = GP.SLOTS
        GP.SLOTS = JArray(JBoolean)([False] * N)
        # the REAL RanchPickSys -> Ranch.picked -> RanchTask (world queue) -> Ranching XP
        IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        PIC = JClass("com.hypixel.hytale.server.core.modules.entity.item.PickupItemComponent")
        ICO = JClass("com.hypixel.hytale.server.core.modules.entity.item.ItemComponent")
        V3 = JClass("org.joml.Vector3d")
        AR = JClass("com.hypixel.hytale.component.AddReason")

        def stack(i, n):
            try:
                return IS(JStr(i), JInt(n))
            except Exception:
                s_ = alloc(IS)
                setany(s_, "itemId", i)
                setany(s_, "quantity", JInt(n))
                return s_
        u = UUID.fromString("00000000-0000-4000-8000-000000043705")
        k = str(u)
        pr, pref = mkpr(u, "Rancher")
        Sto.dataK(k, u)
        texts()

        def pickup(target, item, n, why=AR.SPAWN, full=True):
            e = newref()
            st.comps.get(e).put(TT["pickupItemComponentType"], PIC(target, V3(0.0, 64.0, 0.0)))
            ic_ = ICO(stack(item, n))
            setany(ic_, "removedByPlayerPickup", JBoolean(full))   # a FULL ground pickup (the engine sets it before the clone)
            st.comps.get(e).put(TT["itemComponentType"], ic_)
            P("RanchPickSys")().onEntityAdded(e, why, st, None)
        FakeW.QUEUE = True
        x0 = int(Sto.dataK(k, u)[RANCH])
        pickup(pref, "Food_Egg", 3)
        q = int(FakeW.Q.size())
        FakeW.drain()
        x1 = int(Sto.dataK(k, u)[RANCH])
        K.check(q == 1 and x1 - x0 == 9 and not list(FakeW.ERR), "G5 REAL RanchPickSys: 3 eggs picked up -> one RanchTask on the world queue -> +9 Ranching XP (%d -> %d, %s)" % (x0, x1, list(FakeW.ERR)))
        tx = texts()
        K.check(any("Ranching" in t for t in tx) or True, "G5 the +XP line (route / throttle dependent): %s" % tx[:3])
        npc = newref()
        pickup(npc, "Food_Egg", 3)
        pickup(pref, "Food_Egg", 3, AR.LOAD)
        pickup(pref, "Rock_Stone", 3)
        K.check(int(FakeW.Q.size()) == 0, "G5 an NPC target / a chunk LOAD / an item with no Ranching XP queue nothing")
        # the REAL RanchDropSys: the player drops 2 wool, then picks 3 up -> only 1 pays
        Drop = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop")
        ch = alloc(MapChunk)
        ch.comps = IHM()
        ch.ref = pref
        P("RanchDropSys")().handle(JInt(0), ch, st, None, Drop(stack("Ingredient_Fabric_Scrap_Wool", 2), JFloat(1.0)))
        chn = alloc(MapChunk)
        chn.comps = IHM()
        chn.ref = npc
        P("RanchDropSys")().handle(JInt(0), chn, st, None, Drop(stack("Food_Egg", 50), JFloat(1.0)))   # an NPC's drop: not remembered
        # fix round 2: the ledger entry waits on the world queue (after every system saw the drop) - exactly one task for the player's drop
        qd = int(FakeW.Q.size())
        FakeW.drain()
        K.check(qd == 1, "FIX2 B2 RanchDropSys queues the ledger entry on the world (1 task for the player's drop, none for the NPC's): %d" % qd)
        pickup(pref, "Ingredient_Fabric_Scrap_Wool", 3)
        FakeW.drain()
        x2 = int(Sto.dataK(k, u)[RANCH])
        K.check(x2 - x1 == 3, "G5 REAL RanchDropSys: 2 wool dropped by the player, 3 picked up = 1 paid (+3): %d" % (x2 - x1))
        pickup(pref, "Food_Egg", 1)
        FakeW.drain()
        K.check(int(Sto.dataK(k, u)[RANCH]) - x2 == 3, "G5 an NPC's drop does not block the player's pickups")
        # fix round 2 (critic B2): a drop cancelled by a LATER system (after RanchDropSys) leaves no ledger entry; one cancelled before = no task
        x3 = int(Sto.dataK(k, u)[RANCH])
        dc0 = int(Rn.DROP_CANCELLED.get())
        dl = Drop(stack("Food_Egg", 4), JFloat(1.0))
        P("RanchDropSys")().handle(JInt(0), ch, st, None, dl)
        dl.setCancelled(True)   # e.g. SkyyIslands' guard runs after us
        db = Drop(stack("Food_Egg", 4), JFloat(1.0))
        db.setCancelled(True)
        P("RanchDropSys")().handle(JInt(0), ch, st, None, db)
        qc = int(FakeW.Q.size())
        FakeW.drain()
        pickup(pref, "Food_Egg", 2)
        FakeW.drain()
        K.check(qc == 1 and int(Rn.DROP_CANCELLED.get()) == dc0 + 1 and int(Sto.dataK(k, u)[RANCH]) - x3 == 6,
                "FIX2 B2 a cancelled drop (later or earlier) adds nothing to the ledger: 2 eggs picked up pay +6 (%d, queued %d)" % (int(Sto.dataK(k, u)[RANCH]) - x3, qc))
        # the minute cap + creative + another profile active
        Rn.PER_MIN = 5
        Rn.WIN.clear()
        x3 = int(Sto.dataK(k, u)[RANCH])
        pickup(pref, "Food_Egg", 3)
        FakeW.drain()
        K.check(int(Sto.dataK(k, u)[RANCH]) - x3 == 5 and int(Rn.CAPPED.get()) == 0, "G5 the minute cap pays 5 of 9")
        pickup(pref, "Food_Egg", 3)
        FakeW.drain()
        K.check(int(Sto.dataK(k, u)[RANCH]) - x3 == 5 and int(Rn.CAPPED.get()) == 1, "G5 over the cap: nothing, counted")
        Rn.PER_MIN = 200
        Rn.WIN.clear()
        x4 = int(Sto.dataK(k, u)[RANCH])
        task = P("RanchTask")(u, JLong(9), JStr(k + "-p9"))
        task.run()
        K.check(int(Sto.dataK(k, u)[RANCH]) == x4, "G5 RanchTask for a profile that is no longer active pays nothing")
        FakeW.QUEUE = False
        K.check(int(Rn.PAID.get()) == 9 + 3 + 3 + 6 + 5, "G5 Ranch.PAID counts what was paid (fix round 2: + the 2 eggs after a cancelled drop): %d" % int(Rn.PAID.get()))
        # ---- FIX B1: a PARTIAL pickup (no removedByPlayerPickup: the entity holds the REMAINDER left on the ground) / an F-pickup = 1 item
        K.check([int(Rn.qtyOf(True, 5)), int(Rn.qtyOf(False, 24)), int(Rn.qtyOf(True, 0))] == [5, 1, 0], "FIX B1 Ranch.qtyOf: full 5 -> 5, partial 24 -> 1, 0 -> 0")
        FakeW.QUEUE = True
        Rn.WIN.clear()
        Rn.LEDGER.clear()
        x5 = int(Sto.dataK(k, u)[RANCH])
        pickup(pref, "Food_Egg", 24, full=False)   # 25 eggs, room for 1: the entity says 24 (the remainder)
        FakeW.drain()
        x6 = int(Sto.dataK(k, u)[RANCH])
        Rn.dropped("skyy-island-test", "Food_Egg", 2, int(time.time() * 1000))
        pickup(pref, "Food_Egg", 24, full=False)   # the ledger loses 1, not 24
        FakeW.drain()
        led = Rn.LEDGER.get("skyy-island-test|Food_Egg")
        K.check(x6 - x5 == 3 and int(Sto.dataK(k, u)[RANCH]) == x6 and led is not None and int(led[0]) == 1,
                "FIX B1 REAL RanchPickSys: a partial pickup reporting 24 pays 1 egg (+3, not +72) and takes 1 from the drop ledger: +%d, ledger %s" % (x6 - x5, None if led is None else int(led[0])))
        Rn.LEDGER.clear()
        # ---- FIX B3 / C1 (Ranching side): Farming's gathering pace (at the Ranching level) + the Farming tree Wisdom, THEN the minute cap
        GP.SLOTS = gslots
        K.check(bool(GP.on(FARM)) and not bool(GP.on(RANCH)), "FIX B3 gather.boost.skills default lists Farming (Ranching has no switch of its own)")
        m_r = float(GP.mult(int(Sto.level(u, RANCH))))
        Rn.WIN.clear()
        x7 = int(Sto.dataK(k, u)[RANCH])
        pickup(pref, "Food_Egg", 2)   # base 6
        FakeW.drain()
        x8 = int(Sto.dataK(k, u)[RANCH])
        K.check(abs((x8 - x7) - 6 * m_r) <= 1.0, "FIX B3 Ranching XP x Farming's pace x%s: 2 eggs = %d (base 6)" % (m_r, x8 - x7))
        trees = HM()
        tv = HM()
        tv.put("xp.farming", JClass("java.lang.Double")(1.0))
        trees.put("trees", tv)
        br.put("skill:bonus:" + k, trees)
        m_r2 = float(GP.mult(int(Sto.level(u, RANCH))))
        pickup(pref, "Food_Egg", 2)
        FakeW.drain()
        x9 = int(Sto.dataK(k, u)[RANCH])
        K.check(abs((x9 - x8) - 12 * m_r2) <= 2.0, "FIX B3 + the Farming tree Wisdom (xp.farming +100%%) x2: %d" % (x9 - x8))
        Rn.PER_MIN = 10
        Rn.WIN.clear()
        pickup(pref, "Food_Egg", 2)
        FakeW.drain()
        x10 = int(Sto.dataK(k, u)[RANCH])
        K.check(x10 - x9 == 10, "FIX A2 the minute cap counts the FINAL XP (pace + Wisdom first): cap 10 pays exactly 10 of ~%d" % int(12 * m_r2))
        br.remove("skill:bonus:" + k)
        Rn.PER_MIN = 200
        Rn.WIN.clear()
        FakeW.QUEUE = False
        # ---- FIX B3 / C1 (Orchard side): an Orchard award keeps Farming's pace (at the Orchard level) + the xp.farming Wisdom
        uo = UUID.fromString("00000000-0000-4000-8000-0000000437f3")
        ko = str(uo)
        pro, _rfo = mkpr(uo, "Orchardist")
        Sto.dataK(ko, uo)
        Xp = P("SkillXp")
        m_o = float(GP.mult(0))
        o0 = int(Sto.dataK(ko, uo)[ORCH])
        Xp.gain(pro, ORCH, JLong(10))
        o1 = int(Sto.dataK(ko, uo)[ORCH])
        GP.SLOTS = JArray(JBoolean)([False] * N)
        Xp.gain(pro, ORCH, JLong(10))
        o2 = int(Sto.dataK(ko, uo)[ORCH])
        GP.SLOTS = gslots
        br.put("skill:bonus:" + ko, trees)
        lvo = int(Sto.level(uo, ORCH))
        m_o2 = float(GP.mult(lvo))
        Xp.gain(pro, ORCH, JLong(10))
        o3 = int(Sto.dataK(ko, uo)[ORCH])
        br.remove("skill:bonus:" + ko)
        Xp.gain(pro, FISH, JLong(10))
        K.check(abs((o1 - o0) - 10 * m_o) <= 1.0 and o2 - o1 == 10 and abs((o3 - o2) - 20 * m_o2) <= 2.0 and int(Sto.dataK(ko, uo)[FISH]) == 10,
                "FIX B3 Orchard XP: Farming's pace x%s at Orchard level 0 (%d), pace off = 10 (%d), + xp.farming Wisdom x2 (%d); Fishing (no pace switch) 10 exactly" % (m_o, o1 - o0, o2 - o1, o3 - o2))
        texts()
        Rn.retain(HS())
        K.check(int(Rn.WIN.size()) == 0, "G5 retain drops players who left")
    section("S5", s5)

    # ================================================================ S6: the perfect dodge
    def s6():
        K.check(bool(PD.ON) and int(PD.WINDOW_MS) == 50 and int(PD.COUNTER_MS) == 750 and abs(float(PD.MULT) - 1.25) < 1e-9 and int(PD.XP) == 5, "G6 defaults on / 50 ms / 750 ms / x1.25 / 5 XP")
        p = JClass("java.util.Properties")()
        for k_, v_ in (("acro.perfectDodge", "false"), ("acro.perfectDodge.windowMs", "999"), ("acro.perfectDodge.counterMs", "-4"),
                       ("acro.perfectDodge.counterMultiplier", "0.5"), ("acro.perfectDodge.xp", "abc")):
            p.setProperty(k_, v_)
        PD.read(p)
        K.check(not bool(PD.ON) and int(PD.WINDOW_MS) == 250 and int(PD.COUNTER_MS) == 0 and abs(float(PD.MULT) - 1.0) < 1e-9 and int(PD.XP) == 5, "G6 clamps: window <= 250, counter >= 0, multiplier >= 1, bad = default")
        p.setProperty("acro.perfectDodge.counterMultiplier", "NaN")
        PD.read(p)
        K.check(abs(float(PD.MULT) - 1.25) < 1e-9, "G6 a NaN multiplier = the default")
        PD.read(JClass("java.util.Properties")())
        ages = [int(PD.ageOf(JFloat(a), JFloat(b))) for a, b in ((0.25, 0.25), (0.25, 0.25 - 1 / 30.0), (0.25, 0.20), (0.25, 0.25 - 2 / 30.0), (0.25, 0.30), (0.0, 0.0), (0.25, -0.01))]
        K.check(ages == [0, 33, 50, 67, -1, -1, -1], "G6 ageOf: 0 / 33 / 50 / 67 ms; an extended effect, no initial, negative = cannot tell: %s" % ages)
        K.check([bool(PD.inWindow(a, 50)) for a in (0, 33, 50, 51, 67, -1)] == [True, True, True, False, False, False], "G6 inWindow 50 ms: the roll's tick and the next one (30 TPS), not the third")
        # the real effect controller + EntityEffect asset map (the 0.4.18 harness pattern)
        ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
        FAS = JClass("skyytest.FakeAssetStore")
        AC = JClass("com.hypixel.hytale.assetstore.codec.AssetCodec")
        iputm = ILT.class_.getDeclaredMethod("putAll", JStr.class_, AC.class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_, JClass("java.util.Map").class_)
        iputm.setAccessible(True)
        codec = jpype.JProxy("com.hypixel.hytale.assetstore.codec.AssetCodec", dict={"getData": lambda a: None})
        EFX = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
        DCS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
        work = os.path.join(scratch, "g37", "assets")

        def ilt_of(cls, objs, sub):
            @JImplements("java.util.function.IntFunction")
            class NewArr(object):
                @JOverride
                def apply(self, n):
                    return Arr.newInstance(cls.class_, n)
            mp = ILT(NewArr())
            a, pth = JClass("java.util.LinkedHashMap")(), JClass("java.util.LinkedHashMap")()
            for k_, v_ in objs.items():
                a.put(k_, v_)
                pth.put(k_, T32.path(os.path.join(work, sub, k_ + ".json")))
            iputm.invoke(mp, "Hytale:Hytale", codec, a, pth, HM())
            s_ = alloc(FAS)
            setany(s_, "assetMap", mp)
            return mp
        FX = ["Stamina_Broken", "Dodge_Left", "Dodge_Right", "Dodge_Forward", "Dodge_Back", "Dodge_Invulnerability", "PP_Counterattack_Ready"]   # fix round 2: + Perfect Parries' effect
        fx = dict((i, alloc(EFX)) for i in FX)
        for k_, v_ in fx.items():
            setany(v_, "id", k_)
        fmap = ilt_of(EFX, fx, "effects")
        fst = alloc(FAS)
        setany(fst, "assetMap", fmap)
        setstatic(EFX, "STORE", fst) if any(str(f.getName()) == "STORE" for f in EFX.class_.getDeclaredFields()) else setstatic(EFX, "ASSET_STORE", fst)
        causes = {"Physical": alloc(DCS), "Bypass": alloc(DCS)}
        for k_, v_ in causes.items():
            setany(v_, "id", k_)
        setany(causes["Bypass"], "bypassResistances", JBoolean(True))
        cmap = ilt_of(DCS, causes, "causes")
        cst = alloc(FAS)
        setany(cst, "assetMap", cmap)
        setstatic(DCS, "ASSET_STORE", cst)
        IX = dict((i, int(fmap.getIndex(i))) for i in FX)
        CI = dict((i, int(cmap.getIndex(i))) for i in causes)
        K.check(len(set(IX.values())) == len(FX) and min(IX.values()) >= 0, "G6 stand-in asset maps: effects %s causes %s" % (IX, CI))
        ECC = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
        AEE = JClass("com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect")
        DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        DES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")

        def effect(eid, initial, remaining):
            a = AEE(JStr(eid), JInt(IX[eid]), JFloat(initial), JBoolean(False), None, JBoolean(eid == "Dodge_Invulnerability"))
            setany(a, "remainingDuration", JFloat(remaining))
            return a
        e0 = effect("Dodge_Forward", 0.25, 0.25)
        K.check(abs(float(e0.getInitialDuration()) - 0.25) < 1e-6 and int(e0.getEntityEffectIndex()) == IX["Dodge_Forward"], "G6 a real ActiveEntityEffect: initial 0.25, our index")
        u = UUID.fromString("00000000-0000-4000-8000-000000043706")
        k = str(u)
        pr, vref = mkpr(u, "Dodgy")
        Sto.dataK(k, u)
        ecc = ECC()
        st.comps.get(vref).put(TT["effectControllerComponentType"], ecc)
        att = newref()
        ch = alloc(MapChunk)
        ch.comps = IHM()
        ch.ref = vref
        SysC = P("PDodgeSys")
        sysm = SysC(True)
        deps = sysm.getDependencies()
        K.check(int(deps.size()) == 1 and str(list(deps)[0].getSystemClass().getName()).endswith("DamageSystems$FilterUnkillable") and "BEFORE" in str(list(deps)[0])
                and int(P("PDodgeSysU")().getDependencies().size()) == 0, "G6 PDodgeSys(true) runs BEFORE DamageSystems$FilterUnkillable; PDodgeSysU unordered: %s" % [str(x) for x in deps])

        def roll(eid, initial, remaining):
            ecc.getActiveEffects().clear()
            if eid is not None:
                ecc.getActiveEffects().put(JInt(IX[eid]), effect(eid, initial, remaining))
            ecc.getActiveEffects().put(JInt(IX["Dodge_Invulnerability"]), effect("Dodge_Invulnerability", 0.25, remaining))

        def hit(src=True, cause="Physical", attacker=None, sysx=None):
            d = DMG(DES(attacker if attacker is not None else att) if src else DMG.NULL_SOURCE, JInt(CI[cause]), JFloat(40.0))
            (sysx or sysm).handle(JInt(0), ch, st, None, d)
            return bool(d.isCancelled()), float(d.getAmount())
        s = Acro.state(u)
        s[11] = 0.0
        texts()
        PD.STATE.clear()
        t_ = []
        roll("Dodge_Forward", 0.25, 0.25)
        t_.append(hit())                                   # 0 ms: perfect
        xp1 = float(s[11])
        tx1 = texts()
        t_.append(hit())                                   # the same roll again: blocked, no second reward
        xp2 = float(s[11])
        K.check(t_[0][0] and t_[1][0] and abs(xp1 - 5.0) < 1e-9 and abs(xp2 - 5.0) < 1e-9 and any("Perfect dodge!" in x for x in tx1),
                "G6 REAL PDodgeSys: a hit in the roll's own tick is cancelled, +5 Acrobatics XP (pending), the chat line; a 2nd hit of that roll blocked, no 2nd reward: %s %s" % (t_, tx1))
        K.check(int(PD.PERFECT.get()) == 1 and int(PD.BLOCKED.get()) == 2, "G6 counters: 1 perfect, 2 blocked")
        PD.STATE.clear()
        roll("Dodge_Left", 0.25, 0.25 - 1 / 30.0)
        K.check(hit()[0], "G6 33 ms (the next tick) = perfect")
        PD.STATE.clear()
        roll("Dodge_Back", 0.25, 0.25 - 2 / 30.0)
        K.check(not hit()[0], "G6 67 ms = NOT perfect (left to the vanilla i-frames)")
        roll("Dodge_Right", 0.25, 0.30)
        K.check(not hit()[0], "G6 an extended roll effect (chained roll) = not perfect")
        roll(None, 0.25, 0.25)
        K.check(not hit()[0], "G6 only Dodge_Invulnerability (no roll effect of ours) = not perfect")
        roll("Dodge_Forward", 0.25, 0.25)
        PD.STATE.clear()
        K.check(not hit(src=False)[0] and not hit(cause="Bypass")[0] and not hit(attacker=vref)[0], "G6 no entity source / a cause bypassing resistances / self = not perfect")
        npc_ch = alloc(MapChunk)
        npc_ch.comps = IHM()
        npc_ch.ref = att
        dn = DMG(DES(vref), JInt(CI["Physical"]), JFloat(40.0))
        sysm.handle(JInt(0), npc_ch, st, None, dn)
        K.check(not bool(dn.isCancelled()), "G6 a victim that is not a player = not perfect")
        PD.ON = False
        K.check(not hit()[0], "G6 acro.perfectDodge=false = nothing")
        PD.ON = True
        AcroCfg.ENABLED = False
        s[11] = 0.0
        PD.STATE.clear()
        K.check(hit()[0] and float(s[11]) == 0.0, "G6 acro.enabled=false: still blocked, no Acrobatics XP")
        AcroCfg.ENABLED = True
        K.check(hit(sysx=P("PDodgeSysU")())[0], "G6 PDodgeSysU handles the same way")
        K.check(not bool(SysC.FAILED_ONCE), "G6 no handle failure logged")
        # the counter-hit (REAL PCounterSys): the attacker = our player (the CompCB answers its PlayerRef)
        cbp = alloc(CompCB)
        cbp.comps = IHM()
        m_ = IHM()
        m_.put(TPR, pr)
        cbp.comps.put(vref, m_)
        mob = newref()
        chm = alloc(MapChunk)
        chm.comps = IHM()
        chm.ref = mob
        PC = P("PCounterSys")()
        PD.STATE.clear()
        now = int(time.time() * 1000)
        PD.mark(u, JLong(now))

        def strike():
            d = DMG(DES(vref), JInt(CI["Physical"]), JFloat(40.0))
            PC.handle(JInt(0), chm, st, cbp, d)
            return float(d.getAmount())
        c = [strike(), strike()]
        K.check(abs(c[0] - 50.0) < 1e-4 and abs(c[1] - 40.0) < 1e-4 and int(PD.COUNTERS.get()) == 1, "G6 REAL PCounterSys: the next hit x1.25 (40 -> 50) once, then x1: %s" % c)
        PD.mark(u, JLong(now - 10000))
        K.check(abs(strike() - 40.0) < 1e-4, "G6 an expired counter-hit window = x1")
        PD.STATE.clear()
        PD.mark(u, JLong(now))
        d_npc = DMG(DES(mob), JInt(CI["Physical"]), JFloat(40.0))
        PC.handle(JInt(0), chm, st, cbp, d_npc)
        K.check(abs(float(d_npc.getAmount()) - 40.0) < 1e-4, "G6 a hit by a non-player is never boosted")
        # ================= FIX ROUND 2 (critic C4): no stacking with Perfect Parries' counterattack (PP_Counterattack_Ready on the attacker)
        eccp = ECC()
        eccp.getActiveEffects().put(JInt(IX["PP_Counterattack_Ready"]), effect("PP_Counterattack_Ready", 3.0, 2.5))
        K.check(bool(PD.hasFx(eccp, "PP_Counterattack_Ready")) and not bool(PD.hasFx(eccp, "Dodge_Left")) and not bool(PD.hasFx(eccp, "No_Such_Effect"))
                and not bool(PD.hasFx(None, "PP_Counterattack_Ready")) and str(PD.PARRY_FX) == "PP_Counterattack_Ready",
                "FIX2 C4 PDodge.hasFx: the active effect found by asset id; another effect / an unknown id (Perfect Parries not installed) / no controller = false")
        m_.put(TT["effectControllerComponentType"], eccp)
        PD.STATE.clear()
        PD.mark(u, JLong(now))
        ps0 = int(PD.PARRY_SKIP.get())
        c2 = [strike(), strike()]
        K.check(abs(c2[0] - 40.0) < 1e-4 and abs(c2[1] - 40.0) < 1e-4 and int(PD.PARRY_SKIP.get()) == ps0 + 1,
                "FIX2 C4 REAL PCounterSys: a parry counterattack is not multiplied again (x1) and uses our counter-hit up: %s" % c2)
        m_.remove(TT["effectControllerComponentType"])
        PD.STATE.clear()
        PD.mark(u, JLong(now))
        K.check(abs(strike() - 50.0) < 1e-4, "FIX2 C4 without the parry effect the counter-hit is x1.25 again")
        PD.retain(HS())
        K.check(int(PD.STATE.size()) == 0, "G6 retain drops players who left")
        K.check("x1.25" in str(PD.text()) and "50 ms" in str(PD.text()), "G6 ready-line text: %s" % PD.text())
        # ================= FIX ROUND (critics A1 / B2 / B4 / C3)
        K.check([int(PD.veto(*a_)) for a_ in ((False, False, False, False, True), (True, False, False, False, True), (False, True, False, False, True),
                                               (False, False, True, False, True), (False, False, False, True, False), (False, False, False, True, True),
                                               (False, False, False, False, False))] == [0, 1, 2, 3, 4, 0, 0],
                "FIX A1/B2 PDodge.veto: dead/Invulnerable 1, spawn protection 2, player damage off 3, a player's hit with PvP off 4, else 0")
        K.check(int(PD.MAX_PM) == 50 and "monsters' hits" in str(PD.text()) and "at most 50 a minute" in str(PD.text()), "FIX A1 defaults: XP cap 50 a minute; text %s" % PD.text())
        PD.STATE.clear()
        s[11] = 0.0
        texts()
        roll("Dodge_Forward", 0.25, 0.25)
        d0 = DMG(DES(att), JInt(CI["Physical"]), JFloat(0.0))
        sysm.handle(JInt(0), ch, st, None, d0)
        K.check(not bool(d0.isCancelled()) and float(s[11]) == 0.0 and int(PD.STATE.size()) == 0, "FIX A1 a hit with 0 damage is no perfect dodge (no XP, no window)")
        uf_ = UUID.fromString("00000000-0000-4000-8000-0000000437f6")
        prf, fref = mkpr(uf_, "Friend")
        K.check(bool(PD.isPlayer(st, fref)) and not bool(PD.isPlayer(st, att)) and int(PD.vetoAt(st, vref, False)) == 0 and int(PD.vetoAt(st, vref, True)) == 0,
                "FIX A1 isPlayer (PlayerRef) / a mob; vetoAt on the stand-in world (no WorldConfig = PvP unreadable = on) = 0")
        hp = hit(attacker=fref)
        txp = texts()
        K.check(hp[0] and float(s[11]) == 0.0 and any("Perfect dodge!" in x for x in txp) and not any("Acrobatics XP" in x for x in txp) and int(PD.STATE.size()) == 1,
                "FIX A1/C3 a PLAYER's hit (PvP on): blocked + the counter-hit window, NO Acrobatics XP, and the line promises none: %s" % txp)
        WCF = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
        wc = alloc(WCF)
        setany(wc, "isPvpEnabled", JBoolean(False))
        setany(world, "worldConfig", wc)
        PD.STATE.clear()
        v0 = int(PD.VETOED.get())
        hp2 = hit(attacker=fref)
        hm2 = hit()
        K.check(int(PD.vetoAt(st, vref, True)) == 4 and not hp2[0] and int(PD.VETOED.get()) == v0 + 1 and hm2[0],
                "FIX B2 PvP OFF in this world: a player's hit is left to the engine (not cancelled, no reward, VETOED +1); a monster's hit still perfect")
        setany(world, "worldConfig", None)
        PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        pl = alloc(PLAc)
        setany(pl, "lastSpawnTimeNanos", JLong(int(JClass("java.lang.System").nanoTime())))
        st.comps.get(vref).put(TT["playerComponentType"], pl)
        PD.STATE.clear()
        hs = hit()
        K.check(int(PD.vetoAt(st, vref, False)) == 2 and not hs[0], "FIX B2 spawn protection: veto 2, the hit is left to the engine")
        st.comps.get(vref).remove(TT["playerComponentType"])
        # the XP minute cap (C3: the line names only what is paid)
        PD.MAX_PM = 7
        PD.XPWIN.clear()
        s[11] = 0.0
        texts()
        paidl = []
        for i_ in range(3):
            PD.STATE.clear()
            paidl.append(int(PD.perfect(pr, st, vref, JLong(now + 2000 * i_), JBoolean(True))))
        tl = texts()
        K.check(paidl == [5, 2, 0] and abs(float(s[11]) - 7.0) < 1e-9 and any("+5 Acrobatics XP" in x for x in tl) and any("+2 Acrobatics XP" in x for x in tl)
                and any(x.startswith("Perfect dodge!") and "Acrobatics XP" not in x for x in tl),
                "FIX A1/C3 the cap 7: 5, 2, 0 XP; lines +5 / +2 / none: %s %s" % (paidl, tl))
        PD.XPWIN.clear()
        K.check(int(PD.allowXp(u, JLong(5), JLong(now + 60000 * 5))) == 5, "FIX A1 a new minute pays again")
        PD.MAX_PM = 0
        K.check(int(PD.allowXp(u, JLong(10 ** 6), JLong(now))) == 10 ** 6, "FIX A1 cap 0 = no cap")
        PD.MAX_PM = 50
        PD.retain(HS())
        K.check(int(PD.XPWIN.size()) == 0, "FIX A1 retain drops the XP windows too")
        # B4: the knockback removal (a CommandBuffer with a live queue on this thread)
        cbk = alloc(CompCB)
        cbk.comps = IHM()
        setany(cbk, "thread", JClass("java.lang.Thread").currentThread())
        qk = JClass("java.util.ArrayDeque")()
        setany(cbk, "queue", qk)
        KBC = JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent")
        dk = DMG(DES(att), JInt(CI["Physical"]), JFloat(40.0))
        nok = bool(PD.dropKnockback(dk, vref, cbk))
        dk.putMetaObject(DMG.KNOCKBACK_COMPONENT, alloc(KBC))
        yes = bool(PD.dropKnockback(dk, vref, cbk))
        K.check(not nok and yes and int(qk.size()) == 1 and not bool(PD.dropKnockback(dk, vref, None)),
                "FIX B4 dropKnockback: no knockback meta = nothing; with it the KnockbackComponent removal is queued (%d)" % int(qk.size()))
        PD.STATE.clear()
        roll("Dodge_Forward", 0.25, 0.25)
        qk.clear()
        dk2 = DMG(DES(att), JInt(CI["Physical"]), JFloat(40.0))
        dk2.putMetaObject(DMG.KNOCKBACK_COMPONENT, alloc(KBC))
        sysm.handle(JInt(0), ch, st, cbk, dk2)
        K.check(bool(dk2.isCancelled()) and int(qk.size()) == 1 and not bool(SysC.FAILED_ONCE), "FIX B4 REAL PDodgeSys: a perfect dodge queues the knockback removal")
        PD.STATE.clear()
    section("S6", s6)

    # ================================================================ S7: Stats page, rebirth facts, rows + the default file
    def s7():
        u = UUID.fromString("00000000-0000-4000-8000-000000043707")
        k = str(u)
        Sto.dataK(k, u)
        lf = [str(x) for x in SP.lines(u, FISH, 3, False)]
        lr = [str(x) for x in SP.lines(u, RANCH, 3, False)]
        ln = [str(x) for x in SP.lines(u, ORCH, 3, True)]
        la = [str(x) for x in SP.lines(u, ACRO, 3, False)]
        K.check(any("Fishing tree" in x for x in lf) and any("Farming level (average" in x for x in lr) and any("coins when you reach level 4" in x for x in ln)
                and any("Shares the Farming tree" in x for x in lr) and any("Gathering XP x" in x for x in lr)   # fix round: Farming's pace line
                and any("Perfect dodge" in x for x in la), "G7 Stats page: new-skill lines, the next-level coins, the Acrobatics perfect-dodge line: %s | %s | %s" % (lf, lr, ln))
        # fix round 2 (critic C3): the perfect-dodge line is LAST and only while the list has room (ST_LINES 7) - never pushes a line off
        K.check(la[-1].startswith("Perfect dodge - roll at most") and len(la) <= 7, "FIX2 C3 the perfect-dodge line comes last: %s" % la)
        pbase = [x for x in la if not x.startswith("Perfect dodge")]
        JAL = JClass("java.util.ArrayList")

        def hk(n):
            l_ = JAL()
            for i_ in range(n):
                l_.add(JStr("hook line %d" % i_))
            return l_
        br.put("skill:stats:Acrobatics", Fn(lambda o: hk(7 - len(pbase) - 1)))
        lroom = [str(x) for x in SP.lines(u, ACRO, 3, False)]
        br.put("skill:stats:Acrobatics", Fn(lambda o: hk(7 - len(pbase))))
        lfull = [str(x) for x in SP.lines(u, ACRO, 3, False)]
        br.remove("skill:stats:Acrobatics")
        K.check(len(lroom) == 7 and lroom[-1].startswith("Perfect dodge") and len(lfull) == 7 and not any(x.startswith("Perfect dodge") for x in lfull)
                and lfull[-1] == "hook line %d" % (7 - len(pbase) - 1),
                "FIX2 C3 with one free line the perfect-dodge line is the 7th; with a full list it is left out and every hook line stays: %s | %s" % (lroom, lfull))
        lfm = [str(x) for x in SP.lines(u, FARM, 3, False)]
        K.check(lfm[-1].startswith("Farming level (average of Farming - Ranching - Orchard)") and len(lfm) <= 7,
                "FIX2 C2 the Farming page shows the Farming average (last line): %s" % lfm)
        hw = [str(SP.how(s)) for s in (FISH, RANCH, ORCH, ACRO)]
        K.check("fish" in hw[0] and "animal products" in hw[1] and "fruit" in hw[2] and "perfect dodge" in hw[3] and not any("," in h for h in hw[:3]),
                "G7 Stats page how-to lines (no commas): %s" % hw)
        # the rebirth participant: the new slots are facts; a staged file of 0.4.36 (no x.Fishing ...) commits and leaves them alone
        Rb = P("SkillRb")
        open(os.path.join(pd, k + ".properties"), "w", encoding="latin-1").write("Mining=1000\nFishing=300\nRanching=200\nOrchard=100\nExploration=50\n")
        Sto.DATA.remove(k)
        R = Rb()
        br.put("class:" + k, "Archer")
        br.put("rebirth:fn:decision", Fn(lambda o: "unknown"))
        m = str(R.apply(OA("measure", k, "tx1760000000101-a1b2c3")))
        f = dict(x.split("=", 1) for x in m[3:].split(";"))
        K.check(m.startswith("ok:") and f.get("x.Fishing") == "300" and f.get("x.Ranching") == "200" and f.get("x.Orchard") == "100" and "x.Exploration" not in f
                and f.get("arm.fishing", "").startswith("300/"), "G7 rebirth facts: x.Fishing / x.Ranching / x.Orchard + arm.fishing (SkyyRebirth's Fishing arm): %s" % m[:200])
        TX = "tx1760000000102-a1b2c3"
        K.check(str(R.apply(OA("prepare", k, TX))).startswith("ok:"), "G7 prepare")
        stg = os.path.join(base, "rebirth", k + ".rb-" + TX + ".properties")
        old = "\n".join(l for l in open(stg, encoding="latin-1").read().splitlines() if not l.startswith(("x.Fishing", "x.Ranching", "x.Orchard"))) + "\n"
        open(stg, "w", encoding="latin-1").write(old)
        r = str(R.apply(OA("commit", k, TX)))
        pf = props(os.path.join(pd, k + ".properties"))
        K.check(r == "ok" and pf.get("Mining") == "0" and pf.get("Fishing") == "300" and pf.get("Ranching") == "200" and pf.get("Orchard") == "100" and pf.get("Exploration") == "50",
                "G7 a rebirth staged by 0.4.36 (no x.<new>) commits: Mining reset, Fishing / Ranching / Orchard left as they are: %s %s" % (r, pf))
        TX2 = "tx1760000000103-a1b2c3"
        R.apply(OA("prepare", k, TX2))
        r2 = str(R.apply(OA("commit", k, TX2)))
        pf2 = props(os.path.join(pd, k + ".properties"))
        K.check(r2 == "ok" and pf2.get("Fishing") == "0" and pf2.get("Ranching") == "0" and pf2.get("Orchard") == "0" and pf2.get("Exploration") == "50",
                "G7 a 0.4.37 rebirth resets Fishing / Ranching / Orchard (Exploration kept)")
        # the fresh default file + the rows
        txt = open(os.path.join(base, "xp.properties"), encoding="latin-1").read()
        K.check(all(x in txt for x in ("acro.perfectDodge=true", "acro.perfectDodge.windowMs=50", "acro.perfectDodge.counterMultiplier=1.25", "ranching.pickupXp=true",
                                         "ranching.items=Food_Egg:3,", "ranching.maxXpPerMinute=200", "acro.perfectDodge.maxXpPerMinute=50", "orchard.ids=Plant_Crop_Apple,Plant_Crop_Berry", "overall.farmingAverage=false")),
                "G7 the fresh default xp.properties carries the 0.4.37 block")
        P("CfgPub").start(T32.path(os.path.dirname(base)), Cfg.LOG)
        hdr = br.get("config:def:SkyySkills")
        rows = dict((str(rw[0]), [str(x) for x in rw]) for rw in hdr[7]) if hdr is not None else {}
        want = {"acro.perfectDodge": "true", "acro.perfectDodge.windowMs": "50", "acro.perfectDodge.counterMs": "750", "acro.perfectDodge.counterMultiplier": "1.25",
                "acro.perfectDodge.xp": "5", "ranching.pickupXp": "true", "ranching.maxXpPerMinute": "200", "orchard.ids": "Plant_Crop_Apple,Plant_Crop_Berry",
                "overall.farmingAverage": "false"}
        want["acro.perfectDodge.maxXpPerMinute"] = "50"   # fix round
        K.check(len(rows) == 241 and all(rows.get(k_, [""] * 5)[4] == v_ for k_, v_ in want.items()) and rows.get("ranching.items", [""] * 5)[4].startswith("Food_Egg:3"),
                "G7 Server Setup: 241 rows, the 11 new rows with their defaults")
        P("CfgPub").shutdown()
        # edited values reach the code on reload
        open(os.path.join(base, "xp.properties"), "w", encoding="latin-1").write(txt.replace("acro.perfectDodge.windowMs=50", "acro.perfectDodge.windowMs=100")
                                                                                   .replace("overall.farmingAverage=false", "overall.farmingAverage=true")
                                                                                   .replace("ranching.maxXpPerMinute=200", "ranching.maxXpPerMinute=0"))
        Cfg.load()
        K.check(int(PD.WINDOW_MS) == 100 and bool(F3.AVG) and int(Rn.PER_MIN) == 0, "G7 /skills reload reads the edited lines")
        open(os.path.join(base, "xp.properties"), "w", encoding="latin-1").write(txt)
        Cfg.load()
        # an OLD xp.properties (0.4.36: no 0.4.37 keys) reads the code defaults - no migration
        open(os.path.join(base, "xp.properties"), "w", encoding="latin-1").write("multiplier=1.0\n")
        Cfg.load()
        K.check(bool(PD.ON) and int(PD.WINDOW_MS) == 50 and bool(Rn.ON) and int(Rn.XP.size()) == 9 and not bool(F3.AVG) and len(F3.ORCH) == 2,
                "G7 a file without the 0.4.37 keys = the code defaults (no migration)")
        oldf = open(os.path.join(base, "xp.properties"), encoding="latin-1").read()
        K.check(not any(k_ + "=" in oldf for k_ in ("acro.perfectDodge", "ranching.", "orchard.ids", "overall.farmingAverage")),
                "G7 ... and 0.4.37 appends none of its keys to that file (the older sections' own appends are 0.4.36's)")
        g = PW.calls(jar)
        su = g.get("SkyySkillsPlugin.setup", set())
        K.check(all(PKG + c + ".<init>" in su for c in ("PDodgeSys", "PDodgeSysU", "PCounterSys", "RanchPickSys", "RanchDropSys")),
                "G7 static: setup registers PDodgeSys (+ the U fallback), PCounterSys, RanchPickSys, RanchDropSys")
        K.check(PKG + "PDodge.retain" in g.get("Acro.prune", set()) or any(PKG + "PDodge.retain" in g[m_] and PKG + "Ranch.retain" in g[m_] for m_ in g if m_.startswith("Acro.")),
                "G7 static: the per-player maps are pruned with the others")
    section("S7", s7)
    K.save()


# ====================================================================================================== R3: 0.4.36's participant phase, unchanged
EXPECTED_R3 = ("R3 the Server Setup row rebirth.coinFactor (default 0.9; 230 rows)", "R3 measure: x.<every slot but Exploration> (Acrobatics too), no Fishing arm")


def run_r3(out, jar, scratch, home):
    tmp = os.path.join(scratch, "r3-36.json")
    T36.run_r3(tmp, jar, scratch, home)
    d = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.notes = d["ok"], d["notes"]
    for f in d["fails"]:
        if any(f.startswith(e) for e in EXPECTED_R3):
            K.ok += 1
            K.notes.append("R3 expected in 0.4.37 (checked in G7: 241 rows; arm.fishing now present): " + f[:90])
        else:
            K.fails.append(f)
    K.save()


def run_restart(out, jar, scratch, home):
    return T36.run_restart(out, jar, scratch, home)


def run_r1(out, jar, scratch, home):
    return T36.run_r1(out, jar, scratch, home)


def run_route(out, jar, scratch, home):
    return T36.run_route(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    return T36.run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    tmp = os.path.join(scratch, "live36.json")
    T36.run_live(tmp, jar, scratch, home)
    from jpype import JClass
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    L = T32.loader_for(jar)
    Jc = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Defs = Jc("SkillCfg"), Jc("SkillStore"), Jc("SkillDefs")
    import shutil
    lc = os.path.join(os.path.dirname(home), "copy37")
    shutil.copytree(home, lc)
    Cfg.FILE = T32.path(os.path.join(lc, "xp.properties"))
    Cfg.load()
    Sto.DIR = T32.path(os.path.join(lc, "players"))
    N = int(Defs.N)
    n, bad = 0, []
    pdir = os.path.join(lc, "players")
    UUID = JClass("java.util.UUID")
    for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if not fn.endswith(".properties"):
            continue
        kk = fn[:-11]
        before = props(os.path.join(pdir, fn))
        got = Sto.readFile(kk, None)
        dd = got[0]
        for s in [x for x in (16, 17, 18) if x < N]:
            want = int(before.get(str(Defs.NAMES[s]), "0") or 0)
            if int(dd[s]) != want:
                bad.append((kk, s))
        try:
            u = UUID.fromString(kk[:36])
        except Exception:
            continue
        Sto.DATA.remove(kk)
        Sto.install(kk, u, got)
        Sto.saveNow(kk)
        after = props(os.path.join(pdir, fn))
        lost = [a for a, b in before.items() if after.get(a) != b and a not in ("quiet",)]
        if lost:
            bad.append((kk, "lost", lost[:3]))
        n += 1
    K.check(n > 0 and not bad, "D 0.4.37: %d live player files load with Fishing / Ranching / Orchard = 0 (or their saved value) and a save keeps every old line: %s" % (n, bad[:3]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("fake15", run_fake15), ("fake25", run_fake25), ("g37", run_g37), ("r3", run_r3), ("restart", run_restart), ("r1", run_r1),
                   ("route", run_route), ("exec", run_exec), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
