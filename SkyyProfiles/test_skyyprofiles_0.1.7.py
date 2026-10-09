"""SkyyProfiles 0.1.7 - bare-JVM harness: THE BIG SWITCH CONFIRMS + HEALTH PER PROFILE (tools/profiles_0_1_7_patch.py; Skyy 2026-10-08:
"the big switch button should work to confirm" / "damage from the monk carried over to a new assassin profile."). Built ON the 0.1.5 /
0.1.6 harnesses (imported for their page builder, state lists, bytecode lister and start routine - never edited).

    python SkyyProfiles/test_skyyprofiles_0.1.7.py [--jar <SkyyProfiles-0.1.7.jar>] [--old <SkyyProfiles-0.1.6.jar>] [--dir <scratch>]
                                                   [--live <Skyy_SkyyProfiles folder>] [--keep] [--no16]

  A    every class of the 0.1.7 jar (and 0.1.6) loads + initializes under -Xverify:all
  P    PAGES: the 0.1.6 harness's 54 page states (0.1.5's 48 + 0.1.6's 6) built by the REAL ProfilePage of 0.1.7 and of 0.1.6: every
       state identical (commands + bindings) = the drawing did not change
  G17  executed in a JVM with the engine's own stat types (Assets.zip Entity/Stats through the engine codec + asset store) and a REAL
       EntityStatMap, the module component types, a map-backed Store, a World whose execute runs the task, a PlayerRef with a recording
       PacketHandler, the REAL ProfilePage + ProfSwitch + ProfStore on a scratch players folder:
       - PAGE: SWITCH asks (pending); SWITCH on the same card again = the switch runs (players file active, the switch commit, chat line);
         SWITCH on another card only moves the question; the bottom CONFIRM still switches; Cancel cancels; DELETE twice only asks
         (players file byte for byte unchanged), only the bottom Delete deletes - then Cancel
       - HEALTH: Monk at 30 / 100 switches to a NEW Assassin -> p.<monk>.hp=0.3 in the switch commit; the Assassin starts FULL
         (Health, Stamina, Mana); other mods' max modifiers land after the switch (Accessories +24 Health, Trees +26 Health, Classes +40
         Mana, Stamina +5) -> the hold keeps full; damage between max changes is the player's own (tracked, not refilled); switching back
         saves the Assassin's ratio (through the running hold) and restores the Monk's 0.3 of the CURRENT max, Stamina / Mana untouched;
         a modifier removed after that keeps 0.3; the bottom-CONFIRM path restores the Assassin's own ratio
       - the hold task: the world hop + world change (calm restarts), death stops it (never revives), MIN / CALM / MAX end it, an invalid
         player stops it, a newer hold replaces an older one (the old task does nothing)
       - PURE (stand-in stat map): parse / text / ratioNow / step over many cases (floor 1 HP, clamp-on-shrink, NaN, garbage, > 1)
       - FILES: setActive 3-arg (join repair) = 4-arg with null; null removes an old p.<id>.hp; the live copy has no p.<id>.hp (= every
         existing profile starts full once); no other key changes
       - SETTING (review fix): Server Setup row healthPerProfile (bool, live); a file without the line runs ON, =false loads OFF; OFF =
         a switch saves / removes / restores nothing and a running hold stops; ON again saves + restores
  Z    engine-access audit: every class / field / method reference of every class passes MethodHandles.Lookup in its own class
  F    class bytes 0.1.6 vs 0.1.7: exactly the planned changes (ProfHp new; ProfStore.setActive; ProfSwitch.switchLocked; ProfilePage
       confirmSwitch + handleDataEvent; the KEEP 20 -> 10 kit constant; version strings)
  S    start twice on a scratch COPY of the live data (the plugin's setup order): nothing in the folder changes
  H16  the 0.1.6 harness (--no15) and H15 the 0.1.5 harness (delete / restore / archive / restart / start on the live copy; --classes =
       SkyyClasses 0.1.14, its 0.1.9 default is gone) run against 0.1.7, control = the same harness on the 0.1.6 jar: no failure beyond
       the control's except their class-byte plans (F)
Nothing is deployed; the live world is only read (copied into the scratch folder). Default scratch folder:
tools/dev/scratch/profiles01/profiles-017 (git-ignored), deleted at the end unless --keep. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, hashlib, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.7", "0.1.6"
PKG = "com.skyy.profiles."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "profiles01", "profiles-017")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyProfiles-%s.jar" % OLD_VERSION)))
LIVE = os.path.abspath(arg("--live", os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod",
                                                  "mods", "Skyy_SkyyProfiles")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
SYN_U = "00000000-0000-0000-0000-0000000017a1"


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _mod(fname, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def m15():
    return _mod("test_skyyprofiles_0.1.5.py", "t015")


def m16():
    return _mod("test_skyyprofiles_0.1.6.py", "t016")


def props(path):
    out = {}
    for ln in open(path, encoding="latin-1").read().splitlines():
        if ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        out[k.strip()] = v.strip()
    return out


# ============================================================================================ child: page states (0.1.6 harness lists)
def run_states(jar, out):
    t16 = m16()
    t16.run_states16(jar, out, None)


# ============================================================================================ child: G17 (page + Health, real stat map)
def run_g17(jar, home, out):
    import skyybuild as B
    t15 = m15()
    hcls = os.path.join(SCRATCH, "hcls")
    os.makedirs(hcls, exist_ok=True)
    # the stand-in classes are written BEFORE the JVM loads them: javassist in a first JVM step is impossible (one JVM per process), so
    # they are compiled by the same JVM right after start - hcls is on the class path and empty until then (the JVM looks it up lazily)
    t15._jvm_start([jar], [B.JAVASSIST, hcls])
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JString
    R = {"log": []}
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def setf(o, cls, name, v):
        jfield(cls, name).set(o, v)

    # ---------------- stand-ins (only ever created by Unsafe.allocateInstance; their constructors never run)
    CP = JClass("javassist.ClassPool")(True)
    CP.appendClassPath(B.SERVER_JAR)
    CtNM, CNC, CTF = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def stub(name, sup, fields, methods, ctor):
        c_ = CP.makeClass("p17h." + name, CP.get(sup))
        c_.addConstructor(CNC.make(ctor, c_))
        for f_ in fields:
            c_.addField(CTF.make(f_, c_))
        for m_ in methods:
            c_.addMethod(CtNM.make(m_, c_))
        c_.writeFile(hcls)
        return JClass("p17h." + name)
    C_ = "com.hypixel.hytale.component."
    StubStore = stub("TStore", C_ + "Store", ["public static java.util.HashMap COMP = new java.util.HashMap();"],
                     ["public " + C_ + "Component getComponent(" + C_ + "Ref r, " + C_ + "ComponentType t) { return (" + C_ + "Component) COMP.get(t); }",
                      "public " + C_ + "Resource getResource(" + C_ + "ResourceType t) { return null; }"],
                     "public TStore() { super((" + C_ + "ComponentRegistry) null, 0, (Object) null, (" + C_ + "IResourceStorage) null); }")
    StubWorld = stub("TWorld", "com.hypixel.hytale.server.core.universe.world.World", ["public static int RUNS = 0;"],
                     ["public void execute(java.lang.Runnable r) { RUNS++; r.run(); }"],
                     "public TWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }")
    PP = "com.hypixel.hytale.protocol."
    StubPH = stub("TPH", "com.hypixel.hytale.server.core.io.PacketHandler", ["public static java.util.ArrayList SENT = new java.util.ArrayList();"],
                  ["public void accept(" + PP + "ToServerPacket p) { }", "public String getIdentifier() { return \"p17h\"; }",
                   "public void write(" + PP + "ToClientPacket p) { SENT.add(p); }", "public void writeNoCache(" + PP + "ToClientPacket p) { SENT.add(p); }",
                   "public void write(" + PP + "ToClientPacket[] p) { SENT.add(p); }",
                   "public void write(" + PP + "ToClientPacket[] p, " + PP + "ToClientPacket q) { SENT.add(q); }",
                   "public boolean writePacket(" + PP + "ToClientPacket p, boolean b) { SENT.add(p); return true; }"],
                  "public TPH() { super((" + PP + "io.ChannelConnection) null, (com.hypixel.hytale.server.core.io.ProtocolVersion) null); }")

    # ---------------- engine statics: HytaleServer (event bus for the asset registry), Universe (worlds), the module component types
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    setf(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    wmap, wbu = CHM(), CHM()
    setf(uni, UNI, "playersByUuid", CHM())
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", wbu)
    setf(uni, UNI, "unmodifiableWorlds", JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    CT = JClass(C_ + "ComponentType")
    ctn = [100]

    def new_ct():           # a distinct type: ComponentType.equals compares index (+ registry), hashCode is a field
        c = U.allocateInstance(CT.class_)
        ctn[0] += 1
        jfield(CT, "index").setInt(c, ctn[0])
        jfield(CT, "hashCode").setInt(c, ctn[0])
        return c
    for mc in ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule", "com.hypixel.hytale.server.core.modules.entity.EntityModule",
               "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule"):
        M_ = JClass(mc)
        inst = U.allocateInstance(M_.class_)
        for f in M_.class_.getDeclaredFields():
            if str(f.getType().getName()) == C_ + "ComponentType":
                f.setAccessible(True)
                f.set(inst, new_ct())
        jfield(M_, "instance").set(None, inst)
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    DEATH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    check(ESM.getComponentType() is not None and PLA.getComponentType() is not None and DEATH.getComponentType() is not None
          and not ESM.getComponentType().equals(PLA.getComponentType()), "G17 setup: the module component types are distinct objects")

    # ---------------- the engine's own stat types from Assets.zip
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None
    EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    if AR.getAssetStore(EST.class_) is None:
        AR.register(HAS.builder(EST.class_, ILT(ArrOf(EST))).setPath("Entity/Stats").setCodec(EST.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths")
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    objs, names = JClass("java.util.ArrayList")(), []
    for n in AZ.namelist():
        if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
            d = json.loads(AZ.read(n).decode("utf-8-sig"))
            for x in ("Regenerating", "MinValueEffects", "MaxValueEffects"):   # their condition / effect codecs need the modules; ids + ranges only here
                d.pop(x, None)
            k = os.path.basename(n)[:-5]
            ei = AEI(Paths.get(k + ".json"), ADT(EST.class_, k, None))
            o = AR.getAssetStore(EST.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), ei)
            if o is not None:
                objs.add(o)
                names.append(k)
    AR.getAssetStore(EST.class_).loadAssets("Hytale:Hytale", objs)
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DST.update()
    HI, SI, MI = int(DST.getHealth()), int(DST.getStamina()), int(DST.getMana())
    check(HI >= 0 and SI >= 0 and MI >= 0 and {"Health", "Stamina", "Mana"} <= set(names), "G17 setup: vanilla stat types loaded (%d): H %d S %d M %d" % (len(names), HI, SI, MI))
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    esm = ESM()
    esm.update()

    def hv(i=HI):
        v = esm.get(i)
        return [round(float(v.get()), 3), round(float(v.getMax()), 3)]

    def mod(i, key, amt):          # another mod's max modifier (SkyyAccessories / SkyyTrees / SkyyClasses pattern: ADDITIVE MAX)
        if amt == 0:
            esm.removeModifier(i, key)
        else:
            esm.putModifier(i, key, SMO(MTG.MAX, CAL.ADDITIVE, float(amt)))
    R["base"] = {"H": hv(HI), "S": hv(SI), "M": hv(MI)}
    mod(MI, "skyyclass_mana_monk", 30)          # a class-given Mana max (vanilla base 0)

    # ---------------- SkyyProfiles on the scratch home
    Cfg, Sto, Sw, Page, Hp = JClass(PKG + "ProfCfg"), JClass(PKG + "ProfStore"), JClass(PKG + "ProfSwitch"), JClass(PKG + "ProfilePage"), JClass(PKG + "ProfHp")
    UUID = JClass("java.util.UUID")
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Sto.DIR, Sto.SWDIR = Paths.get(os.path.join(home, "players")), Paths.get(os.path.join(home, "switching"))
    Sto.INVDIR, Sto.LOGF = Paths.get(os.path.join(home, "inventories")), Paths.get(os.path.join(home, "switches.log"))
    for d_ in ("players", "switching", "inventories"):
        os.makedirs(os.path.join(home, d_), exist_ok=True)
    Cfg.load()
    Cfg.ISLAND_ON_SWITCH = False          # no /island: there is no command manager here (travel() is 0.1.6 code, unchanged)
    Hp.STEP_MS = 3600000                  # the executor never runs a hold step during the test: the harness runs each step itself
    u = UUID.fromString(SYN_U)
    pf = os.path.join(home, "players", SYN_U + ".properties")
    open(pf, "w", newline="\n").write("active=1\nepoch=4\nusername=Tester\np.1.name=Pineapple\np.1.class=Monk\np.1.created=1700000000000\n"
                                      "p.1.lastPlayed=1700000000000\np.2.name=Lime\np.2.class=Assassin\np.2.created=1700000000000\n"
                                      "p.2.lastPlayed=1700000000000\np.3.name=Kiwi\np.3.class=Mage\np.3.created=1700000000000\n"
                                      "p.3.lastPlayed=1700000000000\n")
    Sto.DATA.clear()
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    store = U.allocateInstance(StubStore.class_)
    REFc = JClass(C_ + "Ref")
    ref = REFc(store, 0)
    w1, w2 = U.allocateInstance(StubWorld.class_), U.allocateInstance(StubWorld.class_)
    W1, W2 = UUID.fromString("00000000-0000-0000-0000-00000000aa01"), UUID.fromString("00000000-0000-0000-0000-00000000aa02")
    wbu.put(W1, w1)
    wbu.put(W2, w2)
    pr = U.allocateInstance(PRc.class_)
    setf(pr, PRc, "uuid", u)
    setf(pr, PRc, "username", "Tester")
    setf(pr, PRc, "packetHandler", U.allocateInstance(StubPH.class_))
    setf(pr, PRc, "entity", ref)
    setf(pr, PRc, "worldUuid", W1)
    player = U.allocateInstance(PLA.class_)
    StubStore.COMP.put(PLA.getComponentType(), player)
    StubStore.COMP.put(ESM.getComponentType(), esm)
    check(bool(pr.isValid()) and pr.getReference() is not None and str(pr.getWorldUuid()) == str(W1), "G17 setup: the stand-in player is valid, in world 1")

    def P():
        return props(pf)

    def same(a, b):          # Java identity (ProfHp does not override equals); Python wrappers of one object may differ
        return a is not None and b is not None and bool(a.equals(b))

    def click(pg, a):
        pg.handleDataEvent(ref, store, '{"a":"%s"}' % a)

    def sent():
        n = StubPH.SENT.size()
        return n

    # ======================================================================== PAGE + HEALTH: Monk (damaged) -> NEW Assassin by the big SWITCH
    esm.setStatValue(HI, 30.0)
    esm.setStatValue(SI, 4.0)
    esm.setStatValue(MI, 12.0)
    R["monk_before"] = {"H": hv(HI), "S": hv(SI), "M": hv(MI)}
    raw0 = open(pf, "rb").read()
    pg = Page(pr, 0, False)
    click(pg, "pfsw2")
    R["ask"] = [None if pg.pending is None else str(pg.pending), open(pf, "rb").read() == raw0, hv(HI)]
    click(pg, "pfsw3")                    # another card: the question moves, nothing switches
    R["move"] = [None if pg.pending is None else str(pg.pending), open(pf, "rb").read() == raw0]
    click(pg, "pfsw2")
    R["move2"] = [None if pg.pending is None else str(pg.pending), open(pf, "rb").read() == raw0]
    n0 = sent()
    click(pg, "pfsw2")                    # the highlighted SWITCH again = CONFIRM
    p1 = P()
    hold = Hp.HOLD.get(u)
    R["sw1"] = {"pending": None if pg.pending is None else str(pg.pending), "active": p1.get("active"), "hp1": p1.get("p.1.hp"),
                "hp2": p1.get("p.2.hp"), "inv1": p1.get("p.1.inv"), "epoch": p1.get("epoch"), "switches": p1.get("switches"),
                "H": hv(HI), "S": hv(SI), "M": hv(MI), "hold": hold is not None, "msgs": sent() - n0, "info": str(pg.info),
                "bridge_class": str(Cfg.bridge().get("profile:class:" + SYN_U)), "key": str(Cfg.bridge().get("profile:key:" + SYN_U))}
    # other mods land their max modifiers in their next ticks: the hold (one step per tick here) keeps the new profile full
    steps = []
    w1runs = int(StubWorld.RUNS)
    mod(HI, "skyyacc_health", 24)
    steps.append(("acc +24 before the step", hv(HI)))
    hold.run()
    steps.append(("acc +24 after", hv(HI)))
    mod(SI, "skyyskill_stamina", 5)
    mod(MI, "skyyclass_mana_monk", 0)
    mod(MI, "skyyclass_mana_assassin", 40)
    hold.run()
    steps.append(("stamina +5, mana 30 -> 40", hv(HI), hv(SI), hv(MI)))
    R["w1hop"] = int(StubWorld.RUNS) - w1runs
    esm.setStatValue(HI, 62.0)            # a hit: 62 / 124 = 0.5 (the player's own - not refilled)
    esm.setStatValue(SI, 7.5)             # sprinting
    hold.run()
    steps.append(("hit to 62, sprint to 7.5", hv(HI), hv(SI)))
    mod(HI, "skyytree_health", 26)        # 124 -> 150 while at 0.5 -> 75
    hold.run()
    steps.append(("trees +26", hv(HI)))
    R["steps"] = steps
    # world change (the /island transfer): calm restarts, the hold follows the player
    hold.calm = 0
    setf(pr, PRc, "worldUuid", W2)
    w2runs = int(StubWorld.RUNS)
    hold.run()
    R["w2"] = [int(StubWorld.RUNS) - w2runs, int(time.time() * 1000) - int(hold.calm) < 5000, str(hold.lastWorld) == str(W2), same(Hp.HOLD.get(u), hold)]
    # SWITCH BACK through the big SWITCH: the Assassin's ratio (0.5, read through the running hold) is saved, the Monk's 0.3 restored
    esm.setStatValue(SI, 6.0)
    mod(HI, "skyytree_health", 0)         # removed in the SAME tick as the switch, before the hold saw it: 150 -> 124 (75 kept)
    pg2 = Page(pr, 0, False)
    click(pg2, "pfsw1")
    click(pg2, "pfsw1")
    p2 = P()
    hold2 = Hp.HOLD.get(u)
    R["sw2"] = {"active": p2.get("active"), "hp1": p2.get("p.1.hp"), "hp2": p2.get("p.2.hp"), "H": hv(HI), "S": hv(SI), "M": hv(MI),
                "new_hold": hold2 is not None and not same(hold2, hold), "old_gone": not same(Hp.HOLD.get(u), hold)}
    before_old = hv(HI)
    hold.run()                             # the replaced hold does nothing
    R["old_noop"] = hv(HI) == before_old
    mod(HI, "skyyacc_health", 0)          # 124 -> 100 at 0.3 -> 30
    hold2.run()
    R["sw2_settle"] = hv(HI)
    # the bottom CONFIRM path (pfyes) still switches and restores the Assassin's own 0.5
    pg3 = Page(pr, 0, False)
    click(pg3, "pfsw2")
    click(pg3, "pfyes")
    p3 = P()
    R["sw3"] = {"active": p3.get("active"), "hp1": p3.get("p.1.hp"), "hp2": p3.get("p.2.hp"), "H": hv(HI)}
    # Cancel
    raw3 = open(pf, "rb").read()
    pg4 = Page(pr, 0, False)
    click(pg4, "pfsw1")
    click(pg4, "pfno")
    R["cancel"] = [pg4.pending is None, open(pf, "rb").read() == raw3]
    # DELETE twice only asks; the bottom Delete deletes; restore it back (Cancel path too)
    pg5 = Page(pr, 0, False)
    click(pg5, "pfdel3")
    click(pg5, "pfdel3")
    R["del2"] = [None if pg5.delAsk is None else str(pg5.delAsk), open(pf, "rb").read() == raw3]
    click(pg5, "pfdelno")
    R["delno"] = [pg5.delAsk is None, open(pf, "rb").read() == raw3]
    click(pg5, "pfdel3")
    click(pg5, "pfdelyes")
    p5 = P()
    R["delyes"] = [p5.get("p.3.deleted") is not None, p5.get("active")]

    # ======================================================================== the hold task's ends
    h = Hp.begin(pr, "0.5")
    h.applyMap(esm)
    now = int(time.time() * 1000)
    h.start, h.calm = now - 9000, now - 5000
    h.lastWorld = pr.getWorldUuid()       # same world as its last step (a new world restarts the calm)
    h.run()
    R["end_calm"] = Hp.HOLD.get(u) is None
    h = Hp.begin(pr, "0.5")
    h.applyMap(esm)
    h.start = now - 46000
    h.calm = now
    h.run()
    R["end_max"] = Hp.HOLD.get(u) is None
    h = Hp.begin(pr, "0.5")
    h.applyMap(esm)
    h.run()
    R["keeps_running"] = same(Hp.HOLD.get(u), h)        # inside MIN: still holding
    esm.setStatValue(HI, 0.0)                            # dead
    h.run()
    R["end_dead"] = [Hp.HOLD.get(u) is None, hv(HI)[0]]
    esm.setStatValue(HI, 50.0)
    h = Hp.begin(pr, "0.5")
    setf(pr, PRc, "entity", None)
    h.run()
    R["end_invalid"] = Hp.HOLD.get(u) is None
    setf(pr, PRc, "entity", ref)
    # arrive() on a dead player: nothing written, no hold
    esm.setStatValue(HI, 0.0)
    Hp.arrive(store, ref, pr, None)
    R["arrive_dead"] = [Hp.HOLD.get(u) is None, hv(HI)[0]]
    esm.setStatValue(HI, 40.0)
    # leaving() without a hold = cur / max; with no stat map = null
    R["leaving"] = [str(Hp.leaving(store, ref, u)), None if Hp.leavingMap(None, u) is None else "x"]
    StubStore.COMP.remove(ESM.getComponentType())
    R["leaving_nomap"] = Hp.leaving(store, ref, u) is None
    StubStore.COMP.put(ESM.getComponentType(), esm)

    # ======================================================================== PURE (stand-in stat map: the engine's clamp-never-scale rule)
    pure = {}
    pure["parse"] = [float(Hp.parse(x)) for x in (None, "0.5", " 0.25 ", "1", "2", "0", "-1", "NaN", "abc", "", "0.0001")]
    pure["text"] = [None if Hp.text(x) is None else str(Hp.text(x)) for x in (1.0, 0.99999, 0.5, 0.30004, 0.00001, 0.0, -1.0, float("nan"), 1.5, 0.123456)]

    class Stand:
        """a stand-in stat: setting max clamps the value (never scales it) - EntityStatValue.computeModifiers"""
        def __init__(self, cur, mx):
            self.cur, self.max = cur, mx

        def set_max(self, mx):
            self.max = mx
            self.cur = min(self.cur, mx)

    def run_seq(start_ratio, cur, mx, events, floor=1.0):
        s = JArray(jpype.JFloat)([1.0, start_ratio, 0.0, 0.0, 0.0, 0.0])
        st = Stand(cur, mx)
        trace = []
        for ev in [None] + events:
            if ev is not None:
                kind, val = ev
                if kind == "max":
                    st.set_max(val)
                else:
                    st.cur = val
            w = float(Hp.step(float(st.cur), float(st.max), s, float(floor)))
            if w >= 0:
                st.cur = w
            trace.append(round(st.cur, 3))
        return trace
    pure["new_full"] = run_seq(1.0, 50.0, 100.0, [("max", 124.0), ("cur", 100.0), ("max", 150.0)])
    pure["ratio_shrink"] = run_seq(0.5, 100.0, 100.0, [("max", 80.0), ("max", 120.0)])
    pure["clamp_shrink"] = run_seq(0.8, 120.0, 150.0, [("max", 100.0)])
    pure["floor"] = run_seq(0.0001, 100.0, 100.0, [("max", 200.0)])
    pure["regen_tracked"] = run_seq(0.5, 100.0, 100.0, [("cur", 70.0), ("max", 140.0)])
    pure["swap_clamp"] = run_seq(1.0, 30.0, 30.0, [("max", 0.0), ("max", 40.0)], 0.0)          # class Mana modifier removed, then the new one
    pure["swap_clamp2"] = run_seq(1.0, 30.0, 30.0, [("max", 10.0), ("max", 40.0)], 0.0)        # ... with a sample in between
    pure["gain_on_change"] = run_seq(0.5, 100.0, 100.0, [("cur", 60.0), ("max", 120.0)])     # regen, then a max change in the same window
    pure["no_change_no_write"] = run_seq(1.0, 100.0, 100.0, [("cur", 90.0), ("cur", 80.0)])
    s0 = JArray(jpype.JFloat)([0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    pure["unheld"] = float(Hp.step(5.0, 10.0, s0, 0.0))
    s1 = JArray(jpype.JFloat)([1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    pure["zero_max"] = float(Hp.step(0.0, 0.0, s1, 0.0))
    pure["ratioNow"] = [round(float(Hp.ratioNow(*a)), 4) for a in ((50.0, 100.0, 100.0, 0.9, 50.0), (100.0, 124.0, 100.0, 1.0, 100.0),
                                                                  (80.0, 80.0, 100.0, 0.8, 100.0), (124.0, 124.0, 100.0, 0.7, 100.0),
                                                                  (30.0, 0.0, 100.0, 0.4, 30.0), (40.0, 80.0, 100.0, 0.9, 60.0), (70.0, 140.0, 100.0, 0.5, 50.0))]
    R["pure"] = pure

    # ======================================================================== FILES: setActive forms
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000017a2")
    f2 = os.path.join(home, "players", str(u2) + ".properties")
    open(f2, "w", newline="\n").write("active=1\nepoch=1\np.1.name=A\np.1.class=Monk\np.1.created=1\np.1.lastPlayed=1\np.1.hp=0.4\n"
                                      "p.2.name=B\np.2.class=Mage\np.2.created=1\np.2.lastPlayed=1\np.2.hp=0.7\n")
    Sto.DATA.clear()
    a0 = props(f2)
    ok = bool(Sto.setActive(u2, "1", "2"))           # 3-arg = null: removes p.1.hp (unreadable stats = full later)
    a1 = props(f2)
    ok2 = bool(Sto.setActive(u2, "2", "1", "0.6543"))
    a2 = props(f2)
    ok3 = bool(Sto.setActive(u2, None, "2"))         # the join repair form: no leaving profile, no hp key touched
    a3 = props(f2)
    strip = lambda d: dict((k, v) for k, v in d.items() if not k.endswith(".lastPlayed") and k not in ("epoch", "switches", "active"))
    R["files"] = {"ok": [ok, ok2, ok3], "a1_hp": [a1.get("p.1.hp"), a1.get("p.2.hp")], "a2_hp": [a2.get("p.1.hp"), a2.get("p.2.hp")],
                  "a3_hp": [a3.get("p.1.hp"), a3.get("p.2.hp")],
                  "a1_other": sorted(set(strip(a1).items()) ^ set(strip(a0).items())), "a2_other": sorted(set(strip(a2).items()) ^ set(strip(a1).items())),
                  "a3_other": sorted(set(strip(a3).items()) ^ set(strip(a2).items()))}
    # ======================================================================== SERVER SETUP healthPerProfile (review fix): load + OFF path
    cfgp = os.path.join(home, "config.properties")
    cfg_raw = open(cfgp, "rb").read() if os.path.isfile(cfgp) else None
    Cfg.load()                            # Skyy's live file has no healthPerProfile line: the field keeps its default (true)
    R["cfg_absent"] = [bool(Cfg.HP_PER_PROFILE), "healthPerProfile" in (cfg_raw or b"").decode("latin-1"), "healthPerProfile=true" in str(Cfg.summary())]
    open(cfgp, "wb").write((cfg_raw or b"") + b"\nhealthPerProfile=false\n")
    Cfg.load()
    R["cfg_false"] = [bool(Cfg.HP_PER_PROFILE), "healthPerProfile=false" in str(Cfg.summary())]
    dl = [str(x) for x in Cfg.DEFAULT_LINES]
    R["cfg_default"] = [dl[-1], dl.count("deleteUndoHours=6"), all(ord(c) < 128 for c in "".join(dl))]
    rows = JClass(PKG + "CfgRows")
    ri = int(rows.index("healthPerProfile"))
    R["cfg_row"] = [ri >= 0, str(rows.TYPES[ri]) if ri >= 0 else None, str(rows.FLAGS[ri]) if ri >= 0 else None]
    # OFF: a switch (big SWITCH twice) neither saves, removes nor restores Health; no hold; a running hold stops at its next step
    Sto.DATA.clear()
    pOff0 = P()
    hold_off = Hp.begin(pr, "0.5")
    hold_off.applyMap(esm)
    esm.setStatValue(HI, 23.0)
    hOff = hv(HI)
    pgo = Page(pr, 0, False)
    click(pgo, "pfsw1")
    click(pgo, "pfsw1")
    pOff = P()
    R["off_switch"] = {"active": pOff.get("active"), "hp1": [pOff0.get("p.1.hp"), pOff.get("p.1.hp")], "hp2": [pOff0.get("p.2.hp"), pOff.get("p.2.hp")],
                       "H": [hOff, hv(HI)], "hold": Hp.HOLD.get(u) is None}
    h3 = Hp.begin(pr, "0.5")
    h3.applyMap(esm)
    bh = hv(HI)
    mod(HI, "skyyacc_health", 24)
    h3.run()
    R["off_run"] = [Hp.HOLD.get(u) is None, bh, hv(HI)]
    mod(HI, "skyyacc_health", 0)
    R["off_leaving"] = str(Hp.leaving(store, ref, u))
    # ON again: the same switch saves and restores
    Cfg.HP_PER_PROFILE = True
    esm.setStatValue(HI, 80.0)
    pgn = Page(pr, 0, False)
    click(pgn, "pfsw2")
    click(pgn, "pfsw2")
    pOn = P()
    R["on_again"] = {"active": pOn.get("active"), "hp1": pOn.get("p.1.hp"), "H": hv(HI), "hp2": pOn.get("p.2.hp")}
    if cfg_raw is not None:
        open(cfgp, "wb").write(cfg_raw)
    live_hp = []
    for fn in os.listdir(os.path.join(home, "players")):
        if fn.endswith(".properties") and fn[:36] not in (SYN_U, str(u2)):
            live_hp += [k for k in props(os.path.join(home, "players", fn)) if k.endswith(".hp")]
    R["live_hp"] = live_hp
    R["switches_log"] = open(os.path.join(home, "switches.log"), encoding="utf-8", errors="replace").read()[-2000:] if os.path.isfile(os.path.join(home, "switches.log")) else ""
    R["warns"] = []
    json.dump(R, open(out, "w"), indent=1, default=str)
    sys.stdout.flush()
    os._exit(0)                                       # ClearLater / hold tasks sit in the server executor: do not wait for them


# ============================================================================================ child: Z engine-access audit
def run_audit(jar, out):
    import skyybuild as B
    t15 = m15()
    hcls = os.path.join(SCRATCH, "hcls-z")
    os.makedirs(hcls, exist_ok=True)
    t15._jvm_start([jar], [B.JAVASSIST, hcls])
    from jpype import JClass
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPj.appendClassPath(jar)
    lk = CPj.makeClass("p17z.LookupIn")
    lk.addMethod(JClass("javassist.CtNewMethod").make("public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
                                                      "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(hcls)
    LIN, MTc, CPool, JMod_ = JClass("p17z.LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"), JClass("java.lang.reflect.Modifier")
    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    XOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}

    def jc(name):
        return Cls.forName(name.replace("/", "."), False, sysl)
    refused, n, cs = [], 0, [0]
    names = [x[:-6].replace("/", ".") for x in zipfile.ZipFile(jar).namelist() if x.endswith(".class")]
    for cn in names:
        D = jc(cn)
        lk_ = LIN.lookupIn(D)
        cc = CPj.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it.hasNext():
                p_ = it.next()
                op = it.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d" % (cn.rsplit(".", 1)[-1], mi.getName(), p_)
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it.byteAt(p_ + 1) if op == 0x12 else it.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk_.accessClass(jc(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C2 = jc(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", sysl).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk_.findStaticGetter(C2, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk_.findGetter(C2, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx))
                        else:
                            cname, name, desc = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx))
                        C2 = jc(cname)
                        mt = MTc.fromMethodDescriptorString(desc, sysl)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C2.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn):
                                raise ValueError("constructor %s%s not accessible" % (cname, desc))
                        elif name == "<init>":
                            lk_.findConstructor(C2, mt)
                        elif op == 0xb8:
                            lk_.findStatic(C2, name, mt)
                        elif op == 0xb7:
                            lk_.findSpecial(C2, name, mt, D)
                        else:
                            lk_.findVirtual(C2, name, mt)
                except Exception as e:
                    if "caller-sensitive" in str(e) and (op in (0xb6, 0xb8, 0xb9)) and                             (str(cp.getMethodrefClassName(idx)) if tag != CPool.CONST_InterfaceMethodref else "x").startswith("java."):
                        cs[0] += 1          # a JDK caller-sensitive reflection call (Field.get / Method.invoke): no Lookup can model it
                        continue
                    refused.append("%s: %s" % (where, str(e)[:160]))
    json.dump({"refs": n, "classes": len(names), "refused": refused, "cs": cs[0]}, open(out, "w"), indent=1)


# ============================================================================================ child: S (start, the 0.1.5 routine)
def run_start(jar, home, out):
    t15 = m15()
    t15.run_start(jar, home, out)
    os._exit(0)


# ============================================================================================ parent
def main():
    if "--states" in sys.argv:
        return run_states(arg("--states"), arg("--out"))
    if "--g17" in sys.argv:
        return run_g17(arg("--g17"), arg("--home"), arg("--out"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--out"))
    if "--start" in sys.argv:
        return run_start(arg("--start"), arg("--home"), arg("--out"))
    if "--bytecode" in sys.argv:
        m = m15()
        m.VERSION, m.OLD_VERSION = VERSION, OLD_VERSION
        return m.run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    if not SCRATCH.replace("\\", "/").lower().startswith(sroot + "/"):
        sys.exit("--dir must be inside tools/dev/scratch/ (it is deleted afterwards): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    m = m15()
    live_before = m.all_hashes(LIVE)
    copy = os.path.join(SCRATCH, "live", "Skyy_SkyyProfiles")
    shutil.copytree(LIVE, copy)
    me = os.path.abspath(__file__)

    def child(*a):
        return subprocess.run([sys.executable, me] + list(a) + ["--dir", SCRATCH], env=env)
    # ---------------------------------------------------------------- A + P
    outs = {"new": os.path.join(SCRATCH, "states-new.json"), "old": os.path.join(SCRATCH, "states-old.json")}
    for tag, jj in (("new", JAR), ("old", OLD_JAR)):
        p = child("--states", jj, "--out", outs[tag])
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "P: state child (%s) ran" % tag)
    if os.path.isfile(outs["new"]) and os.path.isfile(outs["old"]):
        new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
        for r in (new, old):
            check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load + initialize under -Xverify:all %s"
                  % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"][:3]))
        print("A. -Xverify:all: %s %d / %d, %s %d / %d" % (os.path.basename(new["jar"]), new["loaded"], new["classes"], os.path.basename(old["jar"]),
                                                         old["loaded"], old["classes"]))
        check(new["classes"] == old["classes"] + 1, "A: exactly one class more (ProfHp): %d vs %d" % (new["classes"], old["classes"]))
        core = lambda st_: dict((k, v) for k, v in (st_ or {}).items() if k != "now")     # "now" = the clock of that run
        diff = [nm for nm in old["states"] if core(new["states"].get(nm)) != core(old["states"][nm])]
        check(len(old["states"]) >= 54 and set(new["states"]) == set(old["states"]) and not diff,
              "P: all %d page states identical in 0.1.7 and 0.1.6 (the drawing did not change): differ %s" % (len(old["states"]), diff[:5]))
        swq = [nm for nm in new["states"] if "Switch to " in json.dumps(new["states"][nm]["commands"])]
        print("P. %d page states identical (commands + bindings); %d of them show the switch question" % (len(new["states"]), len(swq)))
    # ---------------------------------------------------------------- G17
    ghome = os.path.join(SCRATCH, "g17", "Skyy_SkyyProfiles")
    shutil.copytree(LIVE, ghome)
    gout = os.path.join(SCRATCH, "g17.json")
    p = child("--g17", JAR, "--home", ghome, "--out", gout)
    check(p.returncode == 0 and os.path.isfile(gout), "G17: child ran")
    if os.path.isfile(gout):
        G = json.load(open(gout))
        check(G["base"]["H"] == [100.0, 100.0] and G["base"]["S"][1] > 0, "G17: a fresh EntityStatMap = vanilla Health 100 / 100, Stamina %s" % G["base"]["S"])
        check(G["ask"] == ["2", True, [30.0, 100.0]], "G17 page: SWITCH asks (pending 2), nothing written, Health untouched: %s" % G["ask"])
        check(G["move"] == ["3", True] and G["move2"] == ["2", True], "G17 page: SWITCH on another card only moves the question: %s %s" % (G["move"], G["move2"]))
        s1 = G["sw1"]
        check(s1["pending"] is None and s1["active"] == "2" and s1["inv1"] == "1" and s1["switches"] == "1" and s1["epoch"] == "5"
              and s1["bridge_class"] == "Assassin" and s1["key"] == SYN_U + "-p2" and s1["msgs"] >= 1 and s1["info"] == "",
              "G17 page: the highlighted SWITCH again SWITCHES (active 2, the commit, profile:class Assassin, the chat line): %s" % s1)
        check(s1["hp1"] == "0.3000" and s1["hp2"] is None, "G17 health: the Monk's 30 / 100 saved as p.1.hp=0.3 in the switch commit: %s" % s1["hp1"])
        check(s1["H"] == [100.0, 100.0] and s1["S"][0] == s1["S"][1] and s1["M"] == [30.0, 30.0] and s1["hold"],
              "G17 health: the NEW Assassin starts full (Health, Stamina, Mana) and the hold runs: %s %s %s" % (s1["H"], s1["S"], s1["M"]))
        st = G["steps"]
        check(st[0][1] == [100.0, 124.0] and st[1][1] == [124.0, 124.0], "G17 hold: +24 max lands (engine keeps 100 / 124), the hold step -> 124 / 124: %s" % st[:2])
        check(st[2][1] == [124.0, 124.0] and st[2][2][0] == st[2][2][1] and st[2][3] == [40.0, 40.0],
              "G17 hold: Stamina +5 and the class Mana 30 -> 40 follow to full: %s" % (st[2],))
        check(st[3][1] == [62.0, 124.0] and st[3][2][0] == 7.5, "G17 hold: a hit (62) and sprinting (7.5) are the player's own - not refilled: %s" % (st[3],))
        check(st[4][1] == [75.0, 150.0], "G17 hold: +26 max at 0.5 -> 75 / 150 (the ratio kept): %s" % (st[4],))
        check(G["w1hop"] == 2, "G17 hold: each step hops onto the player's world (World.execute): %d" % G["w1hop"])
        check(G["w2"] == [1, True, True, True], "G17 hold: a world change (the /island transfer) - the hold follows, calm restarts: %s" % G["w2"])
        s2 = G["sw2"]
        check(s2["active"] == "1" and s2["hp2"] == "0.5000" and s2["hp1"] == "0.3000" and s2["new_hold"] and s2["old_gone"],
              "G17 switch back (big SWITCH): the Assassin's 0.5 saved through the running hold (max moved 150 -> 124 in the same tick): %s" % s2)
        check(s2["H"] == [37.2, 124.0] and s2["S"][0] == 6.0 and s2["M"] == [40.0, 40.0],
              "G17 switch back: the Monk's 0.3 of the CURRENT max (37.2 / 124), Stamina / Mana untouched (saved profile): %s" % s2)
        check(G["old_noop"] and G["sw2_settle"] == [30.0, 100.0], "G17 hold: the replaced hold does nothing; a modifier removed later keeps 0.3 (30 / 100): %s" % G["sw2_settle"])
        s3 = G["sw3"]
        check(s3["active"] == "2" and s3["hp1"] == "0.3000" and s3["hp2"] == "0.5000" and s3["H"] == [50.0, 100.0],
              "G17 page: the bottom CONFIRM still switches; the Assassin gets its own 0.5 back: %s" % s3)
        check(G["cancel"] == [True, True], "G17 page: Cancel - nothing switched: %s" % G["cancel"])
        check(G["del2"] == ["3", True] and G["delno"] == [True, True], "G17 page: DELETE twice only asks (no double-click delete); Cancel: %s %s" % (G["del2"], G["delno"]))
        check(G["delyes"] == [True, "2"], "G17 page: only the bottom Delete deletes: %s" % G["delyes"])
        check(G["end_calm"] and G["end_max"] and G["keeps_running"] and G["end_invalid"], "G17 hold ends: calm %s, max %s, inside MIN keeps %s, invalid player %s" % (
            G["end_calm"], G["end_max"], G["keeps_running"], G["end_invalid"]))
        check(G["end_dead"] == [True, 0.0] and G["arrive_dead"] == [True, 0.0], "G17 hold: a dead player stops it and is never revived: %s %s" % (G["end_dead"], G["arrive_dead"]))
        check(G["leaving"] == ["0.4000", None] and G["leaving_nomap"], "G17 leaving: 40 / 100 -> 0.4; no stat map -> nothing saved: %s %s" % (G["leaving"], G["leaving_nomap"]))
        pu = G["pure"]
        check(pu["parse"] == [1.0, 0.5, 0.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0001] or
              [round(x, 4) for x in pu["parse"]] == [1.0, 0.5, 0.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0001],
              "G17 pure parse: missing / garbage / <= 0 / NaN / > 1 = full: %s" % pu["parse"])
        check(pu["text"] == ["1", "1", "0.5000", "0.3000", "0.0001", None, None, None, "1", "0.1235"], "G17 pure text: %s" % pu["text"])
        check(pu["new_full"] == [100.0, 124.0, 100.0, round(100.0 / 124.0 * 150.0, 3)], "G17 pure: a hit to 100 / 124 then max 150 keeps 0.806: %s" % pu["new_full"])
        check(pu["ratio_shrink"] == [50.0, 40.0, 60.0], "G17 pure: 0.5 restored, max 80 -> 40, max 120 -> 60: %s" % pu["ratio_shrink"])
        check(pu["clamp_shrink"] == [120.0, 80.0], "G17 pure: 0.8 of 150, the engine clamps to 100 on a smaller max -> 0.8 of 100 = 80: %s" % pu["clamp_shrink"])
        check(pu["floor"] == [1.0, 1.0], "G17 pure: never below 1 Health: %s" % pu["floor"])
        check(pu["regen_tracked"] == [50.0, 70.0, 98.0], "G17 pure: regen to 70 is tracked (0.7 of 140 = 98): %s" % pu["regen_tracked"])
        check(pu["swap_clamp"] == [30.0, 0.0, 40.0] and pu["swap_clamp2"] == [30.0, 10.0, 40.0],
              "G17 pure: a modifier swap (max 30 -> 0 / 10 -> 40, the engine clamps in between) keeps full: %s %s" % (pu["swap_clamp"], pu["swap_clamp2"]))
        check(pu["gain_on_change"] == [50.0, 60.0, 72.0], "G17 pure: a gain on a max-change step is kept (0.6 of 120): %s" % pu["gain_on_change"])
        check(pu["no_change_no_write"] == [100.0, 90.0, 80.0], "G17 pure: no max change = nothing written: %s" % pu["no_change_no_write"])
        check(pu["unheld"] < 0 and pu["zero_max"] < 0, "G17 pure: an unheld stat / a 0 max is never written")
        check(pu["ratioNow"] == [0.5, 1.0, 0.8, 1.0, 0.4, 0.9, 0.7], "G17 pure ratioNow: %s" % pu["ratioNow"])
        fl = G["files"]
        check(fl["ok"] == [True, True, True] and fl["a1_hp"] == [None, "0.7"] and fl["a2_hp"] == [None, "0.6543"],
              "G17 files: setActive 3-arg = null removes the leaving profile's hp; 4-arg writes it: %s %s" % (fl["a1_hp"], fl["a2_hp"]))
        check(fl["a3_hp"] == fl["a2_hp"], "G17 files: the join-repair form (no leaving profile) touches no hp key: %s" % fl["a3_hp"])
        check(fl["a1_other"] == [["p.1.hp", "0.4"], ["p.1.inv", "1"]] and fl["a2_other"] == [["p.1.inv", "1"], ["p.2.hp", "0.6543"], ["p.2.hp", "0.7"], ["p.2.inv", "1"]]
              and fl["a3_other"] == [["p.2.inv", "1"]], "G17 files: no other key changes (besides 0.1.6's inv / lastPlayed / epoch / switches / active): %s %s %s" % (
                  fl["a1_other"], fl["a2_other"], fl["a3_other"]))
        check(G["live_hp"] == [], "G17 files: the live players files hold no p.<id>.hp (every existing profile = full once): %s" % G["live_hp"])
        # ---- review fix (LOW): Server Setup healthPerProfile
        check(G["cfg_absent"] == [True, False, True] and G["cfg_false"] == [False, True],
              "G17 setting: a config.properties without healthPerProfile (Skyy's live copy) runs ON; healthPerProfile=false loads OFF: %s %s" % (G["cfg_absent"], G["cfg_false"]))
        check(G["cfg_default"] == ["healthPerProfile=true", 1, True] and G["cfg_row"] == [True, "bool", "live"],
              "G17 setting: the default file ends with healthPerProfile=true; Server Setup row bool / live: %s %s" % (G["cfg_default"], G["cfg_row"]))
        of = G["off_switch"]
        check(of["active"] == "1" and of["hp1"] == ["0.3000", "0.3000"] and of["hp2"] == ["0.5000", "0.5000"] and of["H"][0] == of["H"][1] == [23.0, 100.0] and of["hold"],
              "G17 setting OFF: a switch (big SWITCH) saves nothing, removes nothing, restores nothing (23 carries over), no hold: %s" % of)
        check(G["off_run"][0] and G["off_run"][1][0] == G["off_run"][2][0] and G["off_leaving"] == "",
              "G17 setting OFF: a running hold stops at its next step (no refill on +24); leaving() = keep: %s %s" % (G["off_run"], G["off_leaving"]))
        on = G["on_again"]
        check(on["active"] == "2" and on["hp1"] == "0.8000" and on["hp2"] == "0.5000" and on["H"] == [50.0, 100.0],
              "G17 setting back ON: the switch saves 0.8 and restores the Assassin's 0.5: %s" % on)
        check("SWITCH " + SYN_U in G["switches_log"], "G17: the switches.log line was written for the page switches")
        print("G17. page: SWITCH twice switches, another card moves the question, CONFIRM / Cancel unchanged, DELETE twice only asks; health: "
              "Monk 0.3 saved, new Assassin full -> held full through +24 / +26 / Mana / Stamina, 0.5 kept, back to the Monk 0.3 of the current max")
    # ---------------------------------------------------------------- Z
    zout = os.path.join(SCRATCH, "audit.json")
    p = child("--audit", JAR, "--out", zout)
    check(p.returncode == 0 and os.path.isfile(zout), "Z: audit child ran")
    if os.path.isfile(zout):
        Z = json.load(open(zout))
        check(not Z["refused"] and Z["refs"] > 3000, "Z: all %d references in the %d classes pass MethodHandles.Lookup in their own class: refused %s" % (
            Z["refs"], Z["classes"], Z["refused"][:5]))
        print("Z. engine-access audit: %d references, %d classes, %d refused (%d JDK caller-sensitive reflection calls skipped)" % (
            Z["refs"], Z["classes"], len(Z["refused"]), Z.get("cs", 0)))
    # ---------------------------------------------------------------- F
    bco = os.path.join(SCRATCH, "bytecode.json")
    p = child("--bytecode", OLD_JAR, "--new", JAR, "--out", bco)
    check(p.returncode == 0 and os.path.isfile(bco), "F: bytecode child ran")
    if os.path.isfile(bco):
        bc = json.load(open(bco))
        plan = {
            "com/skyy/profiles/ProfStore.class": {"changed": ["setActive(Ljava/util/UUID;Ljava/lang/String;Ljava/lang/String;)Z"],
                                                  "new": ["setActive(Ljava/util/UUID;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z"]},
            "com/skyy/profiles/ProfSwitch.class": {"changed": ["switchLocked(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;"
                                                               "Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/entity/entities/Player;"
                                                               "Ljava/util/UUID;Ljava/util/Properties;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"]},
            "com/skyy/profiles/ProfilePage.class": {"changed": ["handleDataEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V"],
                                                    "new": ["confirmSwitch(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;)V"]},
            # review fix: the Server Setup row healthPerProfile (field HP_PER_PROFILE, load + summary, the default-file lines in <clinit>;
            # capMigrate only by its version string)
            "com/skyy/profiles/ProfCfg.class": {"changed": ["<clinit>()V", "capMigrate()Ljava/lang/String;", "load()Ljava/lang/String;",
                                                            "summary()Ljava/lang/String;"], "fields_new": ["HP_PER_PROFILE Z"]},
        }
        bad, seen, other = [], set(), {}
        for n_, v in sorted(bc.items()):
            seen.add(n_)
            if n_ in plan:
                w = plan[n_]
                if sorted(v["changed"]) != sorted(w.get("changed", [])) or v["new"] != w.get("new", []) or v["gone"] or v["fields_new"] != w.get("fields_new", []) or v["fields_gone"]:
                    bad.append((n_, v["changed"], v["new"], v["gone"]))
            elif not v["version_only"]:
                other[n_.split("/")[-1]] = (v["changed"], v["consts"])
        print("F. class bytes 0.1.6 -> 0.1.7: planned %s; not version-only elsewhere: %s" % (sorted(k.split("/")[-1] for k in plan), other))
        check(not bad and all(c in seen for c in plan), "F: ProfStore / ProfSwitch / ProfilePage / ProfCfg change exactly as planned: %s" % bad[:4])
        cml = bc.get("com/skyy/profiles/ProfCfg.class", {}).get("listing", {}).get("capMigrate()Ljava/lang/String;", "")
        check(cml != "" and "0.1.7" in cml, "F: ProfCfg.capMigrate differs only by its version string (listing has 0.1.7)")
        # the only other change: the config kit's history KEEP 20 -> 10 (one constant in the kit's file / history class)
        oth = json.dumps(other)
        check(all(k.startswith("Cfg") for k in other) and ("20" in oth and "10" in oth or not other),
              "F: outside the plan only the config kit changes (KEEP 20 -> 10): %s" % other)
        pgl = json.dumps(bc.get("com/skyy/profiles/ProfilePage.class", {}).get("listing", {}))
        check("confirmSwitch" in pgl and "ProfSwitch.switchTo" in pgl, "F: the page's confirm calls ProfSwitch.switchTo; handleDataEvent calls confirmSwitch")
        swl = json.dumps(bc.get("com/skyy/profiles/ProfSwitch.class", {}).get("listing", {}))
        check("ProfHp.leaving" in swl and "ProfHp.arrive" in swl and swl.index("ProfHp.leaving") < swl.index("ProfInv.clearAll")
              and swl.index("ProfStore.publish") < swl.index("ProfHp.arrive"),
              "F: switchLocked reads the leaving Health before the inventory swap and restores after the commit + publish")
        zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
        check(set(zn.namelist()) - set(zo.namelist()) == {"com/skyy/profiles/ProfHp.class"} and not set(zo.namelist()) - set(zn.namelist()),
              "F: one class added (ProfHp), none removed: %s" % sorted(set(zo.namelist()) ^ set(zn.namelist())))
    # ---------------------------------------------------------------- S
    shome = os.path.join(SCRATCH, "start", "mods", "Skyy_SkyyProfiles")
    shutil.copytree(LIVE, shome)
    trees, starts = [m.all_hashes(shome)], []
    for k in (1, 2):
        sout = os.path.join(SCRATCH, "start-%d.json" % k)
        p = child("--start", JAR, "--home", shome, "--out", sout)
        check(p.returncode == 0 and os.path.isfile(sout), "S start %d ran" % k)
        starts.append(json.load(open(sout)) if os.path.isfile(sout) else {})
        trees.append(m.all_hashes(shome))
    check(trees[1] == trees[0] and trees[2] == trees[1], "S: two starts on the live copy change nothing in Skyy_SkyyProfiles: %s" % sorted(
        set(trees[2].items()) ^ set(trees[0].items()))[:6])
    lp_ = props(os.path.join(LIVE, "players", m.LIVE_UUID + ".properties")) if os.path.isfile(os.path.join(LIVE, "players", m.LIVE_UUID + ".properties")) else {}
    for k, st_ in enumerate(starts, 1):
        check(st_.get("up") is None and st_.get("capm") is None and st_.get("archived") == 0 and "deleteUndoHours=6" in st_.get("summary", "")
              and (not lp_ or all(("%s %s - " % (i, lp_["p.%s.name" % i])) in st_.get("describe", "") for i in
                                  sorted(set(x.split(".")[1] for x in lp_ if re.match(r"p\.\d+\.name$", x) and "p.%s.deleted" % x.split(".")[1] not in lp_)))),
              "S start %d: no migration, nothing archived, Skyy's live profiles read back: %s" % (k, st_.get("describe")))
    print("S. two starts on a copy of the live folder: unchanged; %s" % (starts[-1].get("describe", "")[:200]))
    # ---------------------------------------------------------------- H16 + H15 (the older harnesses, control = the 0.1.6 jar)
    if "--no16" not in sys.argv:
        def fails_of(t_):
            return [ln.strip()[len("FAILED: "):] for ln in t_.splitlines() if ln.strip().startswith("FAILED: ")] +                    [ln[len("FAIL "):] for ln in t_.splitlines() if ln.startswith("FAIL ")]

        def summ(t_):
            mm = (list(re.finditer(r"(\d+) checks passed, (\d+) failed", t_)) or [None])[-1]
            return mm.group(0) if mm else None
        cls_jar = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.14.jar")       # the 0.1.5 harness's default 0.1.9 jar is gone (tidied)
        runs = {}
        for tag, jj in (("new", JAR), ("ctl", OLD_JAR)):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyprofiles_0.1.6.py"), "--jar", jj, "--old",
                                 os.path.join(HERE, "SkyyProfiles-0.1.5.jar"), "--dir", os.path.join(SCRATCH, "h16-" + tag), "--live", LIVE, "--no15"],
                                env=env, capture_output=True)
            runs["16" + tag] = ph.stdout.decode("utf-8", "replace")
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyprofiles_0.1.5.py"), "--jar", jj, "--old",
                                 os.path.join(HERE, "SkyyProfiles-0.1.4.jar"), "--classes", cls_jar, "--dir", os.path.join(SCRATCH, "h15-" + tag), "--live", LIVE],
                                env=env, capture_output=True)
            runs["15" + tag] = ph.stdout.decode("utf-8", "replace") + ph.stderr.decode("utf-8", "replace")[-3000:]
        # the 0.1.5 harness's part G picks random fruit names (ProfNames.pick): a new profile can take a deleted one's name, and an admin
        # restore then renames it - two of its checks fail by chance (seen 2026-10-08 on one run of 0.1.7, gone on the next two). A failure
        # beyond the control's must repeat on a second run to count.
        x1 = set(fails_of(runs["15new"])) - set(fails_of(runs["15ctl"]))
        if any(not f.startswith("F") for f in x1):
            ph = subprocess.run([sys.executable, os.path.join(HERE, "test_skyyprofiles_0.1.5.py"), "--jar", JAR, "--old",
                                 os.path.join(HERE, "SkyyProfiles-0.1.4.jar"), "--classes", cls_jar, "--dir", os.path.join(SCRATCH, "h15-new2"), "--live", LIVE],
                                env=env, capture_output=True)
            t2 = ph.stdout.decode("utf-8", "replace")
            keep = set(fails_of(t2))
            print("H15 retry (random fruit names): first run extra %s; second run %s" % (sorted(f for f in x1 if not f.startswith("F"))[:3], summ(t2)))
            runs["15new"] = chr(10).join("FAIL " + f for f in sorted(set(fails_of(runs["15new"])) & keep)) + chr(10) + (summ(t2) or "")
        for v_ in ("16", "15"):
            fn_, fc_ = set(fails_of(runs[v_ + "new"])), set(fails_of(runs[v_ + "ctl"]))
            extra = sorted(f for f in fn_ - fc_ if not f.startswith("F: ") and not f.startswith("F "))
            sn, sc = summ(runs[v_ + "new"]), summ(runs[v_ + "ctl"])
            check(sn is not None and sc is not None and not extra, "H%s: the 0.1.%s harness on 0.1.7 fails nothing beyond the control's (0.1.6 jar) "
                  "+ its class-byte plan: %s" % (v_, v_[1], extra[:4]))
            print("H%s. 0.1.%s harness: on 0.1.7 %s, on 0.1.6 (control) %s; control failures %s; extra on 0.1.7 (class bytes only): %d" % (
                v_, v_[1], sn, sc, sorted(fc_)[:3], len(fn_ - fc_)))
            if extra or sn is None:
                open(os.path.join(os.path.dirname(SCRATCH), "h%s-new.txt" % v_), "w", encoding="utf-8").write(runs[v_ + "new"][-20000:])
    return finish(live_before, m)


def finish(live_before, m):
    check(m.all_hashes(LIVE) == live_before, "the live Skyy_SkyyProfiles folder was never written")
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyyProfiles %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
