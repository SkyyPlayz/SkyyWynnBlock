"""Harness for SkyyPets 0.1 (NEW mod: slot pets, phase 1). Build first: python SkyyPets/build_skyypets_0.1.py

    python SkyyPets/test_skyypets_0.1.py [--jar <SkyyPets-0.1.jar>] [--dir <scratch>] [--live <world mods folder>] [--keep]

Parent (plain Python, read only): J the jar (manifest, exactly the expected classes, NO asset / lang / .ui file, no installed mod ships the
package); K Assets.zip facts (every launch pet's model id, the icon items).
Children (fresh JVMs, the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  stand-ins compiled with javassist (MapStore / MapBuffer / MapChunk ECS parts, FakePr, TestPage = PetsPage with rebuild / close
     recorded, FakeStatValue / FakeStatMap = an EntityStatMap that applies MAX / ADDITIVE modifiers, LookupIn / BadAccess for the audit)
  A  every class loads + verifies (-Xverify:all)
  X  EVERY NEW CODE PATH: config (seed, kinds table, every check= hook, the kit console set + table add / remove + RELOAD), PetKind
     parsing, the level curve against the Pets-Spec 3 table, records (create / ids / remove / addXp with fractions + Lv 100), the store
     (pkey with and without SkyyProfiles, atomic save + seq, unreadable files never written: folder / bad escape / newer format),
     the ledger + restore source, the startup check (duplicate id -> higher seq kept, quarantine file + ledger; equal seq; a clean scan
     writes nothing), buffs (slot 1 full, slot 2 locked / quest-unlocked / always / off, 50%, rarity x level, kinds off, no-buff
     worlds, Fortune + swing caps), delivery (pets:stats map, skill:bonus "pets" dd. / xp., move "pets" pct, change-only, clear, the
     skyypet_* modifiers on a stand-in stat map: put / update / remove), XP (own 100% / other 50% / Combat.<class>, level-up chat,
     slot 2 locked = none, part off), pets:fn:onxp (bad args, TRUE / FALSE, HOOKED by SkyySkills only), the fallback poll (baseline,
     growth, drop, jump, profile switch, hooked, switched off, no SkyySkills), slots (page ops), starter (once, none, kind off, bad
     file), every /petadmin path (help, kinds, unknown, offline, list, unlock / lock, give + rarity + level + refusals, take + restore,
     xp), the per-second tick (buffs, starter, profile switch flush, part off), leave (clear + flush + forget), the timer, the page
     (list, paging, details, slot moves, take out, back, stale token, close, a bad file, part off), the commands
  E  THE ECS SYSTEM on a stand-in store (allocated component types): PetTickSys.tick (once a second per player, waiting client skipped,
     the stat map from the CommandBuffer, a broken chunk logged once)
  R  RESTART x3 (fresh JVMs, the same folder): R1 records + XP + slot 2 + shutdown flush; R2 everything read back (levels, XP, slots,
     seq up), a duplicate planted -> quarantined once; R3 a corrupt file: reported, never written, the others fine
  D  START TWICE on a scratch COPY of the live world mods folder: only Skyy_SkyyPets/config.properties appears; start 2 changes nothing
  P  /petadmin + its 5 usage variants: skyypets.admin, empty permission groups, no group leak; /pets (alias /pet) = hytale:Adventurer
  B  BYTECODE: setup() order (config, scan, kit, bridge fn, 2 commands, ONE registerSystem, the disconnect event, the 1 s timer);
     the tick system never opens a page; the stat modifiers are StaticModifier(MAX, ADDITIVE)
  C  CLASS COMPARE: new mod - no older SkyyPets exists; the class list is the expected list (J)
  AA THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every referencing class)
Scratch: tools/dev/scratch/pets01/test (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets01", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyypetstest"
PKG = "com.skyy.pets."
NODE = "skyypets.admin"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
OURS = ["PetsLog", "PetsApi", "PetsEng", "PetKind", "PetsCfg", "PetMath", "PetRec", "PetStore", "PetBuff", "PetXp", "PetXpFn", "PetOps",
        "PetsPage", "PetTick", "PetTickSys", "PetLeave", "PetQuit", "PetTimer", "PetCmds", "PetsCmd", "PetAdminArg1Cmd", "PetAdminArg2Cmd",
        "PetAdminArg3Cmd", "PetAdminArg4Cmd", "PetAdminArg5Cmd", "PetAdminCmd", "SkyyPetsPlugin"]
KITC = ["CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask"]
CLASSES = sorted(PKG + c for c in OURS + KITC)
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                return l.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "mods")))


# ====================================================================================================== parent: J K
def part_static():
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    man = json.loads(z.read("manifest.json"))
    check(man.get("Main") == PKG + "SkyyPetsPlugin" and man.get("IncludesAssetPack") is False and man.get("Version") == VERSION
          and man.get("Name") == "%s SkyyPets" % VERSION and man.get("Group") == "Skyy", "J: manifest Main / IncludesAssetPack false / Version / Name: %r" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(cls == CLASSES, "J/C: exactly the %d expected classes: extra %s missing %s" % (len(CLASSES), sorted(set(cls) - set(CLASSES)), sorted(set(CLASSES) - set(cls))))
    other = [n for n in names if not n.endswith(".class") and n != "manifest.json" and not n.endswith("/")]
    check(not other, "J: no asset / lang / .ui file ships: %s" % other)
    clash = []
    if os.path.isdir(B.MODS_DIR):
        for f in os.listdir(B.MODS_DIR):
            p = os.path.join(B.MODS_DIR, f)
            if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyPets"):
                continue
            try:
                with zipfile.ZipFile(p) as mz:
                    if any(n.startswith("com/skyy/pets/") for n in mz.namelist()):
                        clash.append(f)
            except Exception:
                pass
    check(not clash, "J: no installed mod ships com.skyy.pets classes: %s" % clash)
    az = zipfile.ZipFile(ASSETS)
    an = az.namelist()
    models = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/Models/") and n.endswith(".json"))
    items = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    src = open(os.path.join(HERE, "build_skyypets_0.1.py"), encoding="utf-8").read()
    import re
    kinds = re.findall(r'^\s+\("(\w+)", "(\w+)", "(\w+)", .*, "(\w+)", "Z(\d)"\),', src, re.M)
    check(len(kinds) == 30 and all(k[3] in models for k in kinds), "K: 30 launch pets, every model id is in Assets.zip Server/Models (%d)" % len(kinds))
    for want in ("Rat", "Fox", "Wolf", "Skeleton", "VoidEye", "VoidCrawler", "VoidLarva", "Rabbit", "Horse"):
        check(any(k[0] == want for k in kinds), "K: Skyy's / the spec's pet %s is in the launch roster" % want)
    for it in ("Tool_Hoe_Iron", "Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Weapon_Sword_Iron", "Tool_Map"):
        check(it in items, "K: icon item %s exists" % it)


# ====================================================================================================== children
def _jvm(cp, verify=True, big=False):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + (["-Xmx2g"] if big else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED",
                                                                                 "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


class Child(object):
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)

    def save(self, **extra):
        d = {"ok": self.ok, "fails": self.fails, "notes": self.notes}
        d.update(extra)
        json.dump(d, open(self.out, "w"), indent=1)


def run_mkfake(out_dir):
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG

    def mk(name, sup=None):
        c = cp.makeClass(P + "." + name)
        if sup:
            c.setSuperclass(cp.get(sup))
        return c

    def F(c, s):
        c.addField(CtField.make(s, c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(s, c))
    CR = "com.hypixel.hytale.component."
    ms = mk("MapStore", CR + "Store")
    for d in ("java.util.Map comps", "java.lang.Object ext"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""")
    M(ms, """public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}""")
    M(ms, "public java.lang.Object getExternalData() { return this.ext; }")
    ms.writeFile(out_dir)
    mb = mk("MapBuffer", CR + "CommandBuffer")
    F(mb, "public " + P + ".MapStore st;")
    mb.addConstructor(CtNewConstructor.make("public MapBuffer() { super(null); }", mb))
    M(mb, "public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) { return this.st.getComponent(r, t); }")
    mb.writeFile(out_dir)
    mc = mk("MapChunk", CR + "ArchetypeChunk")
    F(mc, "public com.hypixel.hytale.component.Ref ref;")
    F(mc, "public boolean boom;")
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))
    M(mc, "public com.hypixel.hytale.component.Ref getReferenceTo(int i) { if (this.boom) throw new IllegalStateException(\"boom\"); return this.ref; }")
    mc.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    F(fp, "public java.util.List msgs;")
    F(fp, "public java.util.UUID fu;")
    F(fp, "public String fname;")
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public java.util.UUID getUuid() { return this.fu; }")
    M(fp, "public String getUsername() { return this.fname; }")
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs == null) this.msgs = new java.util.ArrayList(); this.msgs.add(m == null ? \"null\" : m.getRawText()); }")
    fp.writeFile(out_dir)
    tp = mk("TestPage", PKG + "PetsPage")
    F(tp, "public int rebuilds;")
    F(tp, "public int closes;")
    tp.addConstructor(CtNewConstructor.make("public TestPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", tp))
    M(tp, "public void rebuild() { this.rebuilds = this.rebuilds + 1; }")
    M(tp, "public void close() { this.closes = this.closes + 1; }")
    tp.writeFile(out_dir)
    ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
    ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
    MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
    SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
    MTG, CAL = MOD + "$ModifierTarget", SMO + "$CalculationType"
    fv = mk("FakeStatValue", ESV)
    for fs_ in ("public float cur;", "public float base;", "public float mx;", "public java.util.HashMap mods;"):
        F(fv, fs_)
    fv.addConstructor(CtNewConstructor.make("public FakeStatValue(float b) { super(); this.base = b; this.cur = b; this.mx = b; this.mods = new java.util.HashMap(); }", fv))
    for m_ in ("public float get() { return this.cur; }", "public float getMax() { return this.mx; }"):
        M(fv, m_)
    fv.writeFile(out_dir)
    fm = mk("FakeStatMap", ESM)
    for fs_ in ("public %s.FakeStatValue[] vals;" % P, "public int puts;", "public int removes;"):
        F(fm, fs_)
    fm.addConstructor(CtNewConstructor.make("public FakeStatMap(int n) { super(); this.vals = new %s.FakeStatValue[n]; for (int i = 0; i < n; i++) this.vals[i] = new %s.FakeStatValue(100.0f); }" % (P, P), fm))
    M(fm, ("public static void recompute(%s.FakeStatValue v) { float m = v.base; java.util.Iterator it = v.mods.values().iterator(); "
           "while (it.hasNext()) { Object o = it.next(); if (!(o instanceof %s)) continue; %s s = (%s) o; "
           "if (s.getTarget() == %s.MAX && s.getCalculationType() == %s.ADDITIVE) m = m + s.getAmount(); } v.mx = m; "
           "if (v.cur > m) v.cur = m; }") % (P, SMO, SMO, SMO, MTG, CAL))
    M(fm, "public %s get(int i) { if (i < 0 || i >= this.vals.length) return null; return this.vals[i]; }" % ESV)
    M(fm, "public %s getModifier(int i, String k) { if (i < 0 || i >= this.vals.length) return null; return (%s) this.vals[i].mods.get(k); }" % (MOD, MOD))
    M(fm, "public %s putModifier(int i, String k, %s m) { Object o = this.vals[i].mods.put(k, m); this.puts = this.puts + 1; recompute(this.vals[i]); return (%s) o; }" % (MOD, MOD, MOD))
    M(fm, "public %s removeModifier(int i, String k) { Object o = this.vals[i].mods.remove(k); if (o != null) { this.removes = this.removes + 1; recompute(this.vals[i]); } return (%s) o; }" % (MOD, MOD))
    fm.writeFile(out_dir)
    lk = mk("LookupIn")
    M(lk, "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
          "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}")
    lk.writeFile(out_dir)
    ba = mk("BadAccess")
    M(ba, "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
          "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}")
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== shared JVM helpers
def boot_bare(universe):
    """Options + a stand-in HytaleServer / Universe (no world), the stat indices 0 / 1 / 2 (no assets in a bare JVM)."""
    from jpype import JClass, JArray, JString, JInt
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", universe]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", CHM()),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jf(UNI, n).set(uni, v)
    jf(UNI, "instance").set(None, uni)
    D = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    for n, v in (("HEALTH", 0), ("STAMINA", 1), ("MANA", 2)):
        jf(D, n).setInt(None, v)
    return U, jf, uni


def make_api(state):
    from jpype import JImplements, JOverride, JArray, JClass
    UUID = JClass("java.util.UUID")

    @JImplements(PKG + "PetsApi")
    class Api:
        @JOverride
        def online(self):
            return JArray(UUID)([UUID.fromString(u) for u in state["online"]])

        @JOverride
        def byName(self, name):
            for u, n in state["names"].items():
                if n.lower() == str(name).lower() and u in state["online"]:
                    return UUID.fromString(u)
            return None

        @JOverride
        def nameOf(self, u):
            return state["names"].get(str(u), str(u))

        @JOverride
        def tell(self, u, text, color):
            state["tells"].append((str(u), str(text)))
    return Api()


def bridge_setup(state):
    from jpype import JImplements, JOverride, JClass, JLong
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)

    @JImplements("java.util.function.Function")
    class Xp:
        @JOverride
        def apply(self, a):
            state["xpcalls"] += 1
            return JLong(state["totals"].get((str(a[0]), str(a[1])), 0))

    @JImplements("java.util.function.Function")
    class Key:
        @JOverride
        def apply(self, u):
            return state["profile"].get(str(u), str(u))
    return br, Xp(), Key()


def jall(o):
    return [str(x) for x in o] if o is not None else []


def tree_hash(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


# ====================================================================================================== A + X
def run_core(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    bad = []
    for cn in CLASSES:
        try:
            JClass("java.lang.Class").forName(cn, True, JClass("java.lang.ClassLoader").getSystemClassLoader())
        except Exception as e:
            bad.append("%s: %s" % (cn, str(e)[:160]))
    K.check(not bad, "A: every class loads and verifies under -Xverify:all: %s" % bad)
    boot_bare(os.path.join(SCRATCH, "x-universe"))
    try:
        xrun(K)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:600])
    K.save()


def xrun(K):
    from jpype import JClass, JArray, JObject, JLong, JString, JInt, JDouble
    P = lambda n: JClass(PKG + n)
    Cfg, Kind, Math_, Rec, Store, Buff, Xp, XpFn, Ops, Page, Tick, Leave, Timer, Cmds, Log, Eng = (
        P("PetsCfg"), P("PetKind"), P("PetMath"), P("PetRec"), P("PetStore"), P("PetBuff"), P("PetXp"), P("PetXpFn"), P("PetOps"),
        P("PetsPage"), P("PetTick"), P("PetLeave"), P("PetTimer"), P("PetCmds"), P("PetsLog"), P("PetsEng"))
    Paths, UUID, AL = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.util.ArrayList")
    lines = AL()
    Log.LINES = lines
    state = {"online": [], "names": {}, "tells": [], "totals": {}, "xpcalls": 0, "profile": {}}
    br, xpfn, keyfn = bridge_setup(state)
    Eng.API = make_api(state)
    FSM = JClass(FAKE_PKG + ".FakeStatMap")
    # ---------------------------------------------------------------- config
    mods = os.path.join(SCRATCH, "x-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    cf = os.path.join(mods, "Skyy_SkyyPets", "config.properties")
    txt = open(cf, encoding="latin-1").read()
    K.check("kind.Rabbit=Farming/Common/fortune.farming:10" in txt and "pets.slot2.buffPercent=50" in txt, "X: the default config.properties is seeded")
    K.check(len(Cfg.KINDS) == 30 and bool(Cfg.ON) and int(Cfg.SLOT2_PCT) == 50 and str(Cfg.SLOT2_MODE) == "quest" and int(Cfg.OWNED_MAX) == 120
            and str(Cfg.STARTER) == "Rabbit" and int(Cfg.XP_OWN) == 100 and int(Cfg.XP_OTHER) == 50 and abs(float(Cfg.F3) - 0.6) < 1e-9,
            "X: 30 kinds, part on, quest 50%%, owned 120, starter Rabbit, XP 100/50, Rare 0.6: %d" % len(Cfg.KINDS))
    w = Cfg.kind("wolf")
    K.check(w is not None and str(w.skill) == "Combat" and int(w.rarity) == 3 and abs(float(w.value("str")) - 20.0) < 1e-9 and str(w.model) == "Wolf_Black"
            and str(w.icon) == "Weapon_Sword_Iron" and str(Cfg.kind("VoidEye").name) == "Void Eye", "X: Wolf kind (case-insensitive lookup), model, icon; Void Eye name")
    K.check(Cfg.kind("nope") is None and not Cfg.kindOn("nope") and Cfg.kindOn("Fox"), "X: unknown kind / kindOn")
    K.check(int(Kind.rarityOf("legendary")) == 5 and int(Kind.rarityOf("3")) == 3 and int(Kind.rarityOf("x")) == 0 and int(Kind.rarityOf("9")) == 0
            and int(Kind.rarityOf(None)) == 0 and str(Kind.rarityName(6)) == "Mythic" and str(Kind.rarityName(0)) == "Unknown", "X: rarity names / numbers")
    K.check(Kind.parseStats("str:1,STR:2") is None and Kind.parseStats("bogus:1") is None and Kind.parseStats("str:x") is None and Kind.parseStats("str") is None
            and len(Kind.parseStats("-")[0]) == 0 and len(Kind.parseStats("none")[0]) == 0 and Kind.parseStats("str:999999") is None
            and Kind.parseStats(None) is None and len(Kind.parseStats(" str:1 , , cc:2")[0]) == 2, "X: stat parsing (dupes, unknown, numbers, - / none)")
    K.check(all(Kind.parse(k, v, "|") is None for k, v in (("Fox", "Combat|Rare"), ("Fox", "C|Rare|-"), ("Fox", "Combat|Mythic|-"), ("Fox", "Combat|Rare|x:1"),
                                                           ("Fo x", "Combat|Rare|-"), ("", "Combat|Rare|-"), ("Fox", "Com bat|Rare|-")))
            and Kind.parse("New_Pet", "Mining|2|-", "|") is not None and Kind.parse(None, "a", "|") is None, "X: kind lines refused / accepted")
    K.check(Kind.skillMatch("Combat", "Combat.Archer") and Kind.skillMatch("Mining", "mining") and not Kind.skillMatch("Mining", "Combat")
            and not Kind.skillMatch("Combat", "Mining") and not Kind.skillMatch(None, "x"), "X: skill match (Combat = every Combat.<class> row)")
    K.check(str(Kind.display("VoidCrawler")) == "Void Crawler" and str(Kind.display("Bear_Grizzly")) == "Bear Grizzly" and str(Kind.display(None)) == "", "X: display names")
    for k, v, ok in (("pets.kinds[Fox]", "Combat|Rare|str:20", True), ("pets.kinds[Fox]", "Combat/Rare|x", False), ("pets.kinds[Fox]", "bad", False),
                     ("pets.kinds[Fox]", None, True)):
        K.check((Cfg.checkKind(k, v) is None) == ok, "X: checkKind %s=%s" % (k, v))
    K.check(Cfg.checkStarter("k", "none") is None and Cfg.checkStarter("k", "Fox") is None and Cfg.checkStarter("k", "Dragon") is not None
            and Cfg.checkStarter("k", None) is None, "X: checkStarter")
    K.check(Cfg.checkList("k", "a,b") is None and Cfg.checkList("k", "a/b") is not None and Cfg.checkList("k", None) is None
            and Cfg.checkSkills("k", "Mining,Combat") is None and Cfg.checkSkills("k", "Min ing") is not None and Cfg.checkSkills("k", None) is None,
            "X: checkList / checkSkills")
    K.check(str(Cfg.entryOf("pets.kinds[Fox]")) == "Fox" and str(Cfg.entryOf("plain")) == "plain" and str(Cfg.entryOf(None)) == "", "X: entryOf")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    P("CfgPub").start(Paths.get(mods), HL.get("SkyyPetsHarness"))
    CfgFn = P("CfgFn")
    m = str(CfgFn.cmdSetConsole("pets.slot2.buffPercent", "40"))
    K.check(int(Cfg.SLOT2_PCT) == 40, "X: kit console set pets.slot2.buffPercent 40: %s" % m)
    CfgFn.cmdSetConsole("pets.slot2.buffPercent", "500")
    K.check(int(Cfg.SLOT2_PCT) == 40, "X: kit refuses 500%% (max 100)")
    CfgFn.cmdSetConsole("pets.slot2.buffPercent", "50")
    m = str(CfgFn.cmdSetConsole("pets.starter", "Dragon"))
    K.check(str(Cfg.STARTER) == "Rabbit", "X: kit refuses an unknown starter kind (check hook): %s" % m)
    fnk = br.get("config:fn:SkyyPets")
    K.check(fnk is not None and br.get("config:def:SkyyPets") is not None, "X: the kit published config:def / config:fn:SkyyPets")
    loads0 = int(Cfg.LOADS)
    r = fnk.apply(JArray(JObject)(["add", "pets.kinds", "Hamster", "Farming|Common|fortune.farming:5", None, "console", "yes", "console"]))
    K.check(r is not None and str(r[0]) == "ok", "X: kit add of a new pet kind: %s" % (jall(r),))
    for _ in range(60):
        if int(Cfg.LOADS) > loads0 and Cfg.kind("Hamster") is not None:
            break
        time.sleep(0.1)
    K.check(Cfg.kind("Hamster") is not None and "kind.Hamster=Farming/Common/fortune.farming:5" in open(cf, encoding="latin-1").read(),
            "X: the kind line is written with sep / and RELOAD made it live")
    r = fnk.apply(JArray(JObject)(["add", "pets.kinds", "Bad", "Farming|Mythic|-", None, "console", "yes", "console"]))
    K.check(r is not None and str(r[0]) == "bad", "X: kit refuses a Mythic start rarity (check hook): %s" % (jall(r),))
    fnk.apply(JArray(JObject)(["remove", "pets.kinds", "Hamster", None, "console", "yes", "console"]))
    for _ in range(60):
        if Cfg.kind("Hamster") is None:
            break
        time.sleep(0.1)
    K.check(Cfg.kind("Hamster") is None, "X: kit remove reloads the kind away")
    P("CfgPub").flush()
    K.check(abs(float(Cfg.factor(1)) - 0.3) < 1e-9 and abs(float(Cfg.factor(6)) - 1.25) < 1e-9 and float(Cfg.factor(0)) == 0.0 and float(Cfg.factor(2)) == 0.45
            and float(Cfg.factor(4)) == 0.8 and float(Cfg.factor(5)) == 1.0, "X: rarity factors")
    K.check("Fox" in str(Cfg.kindList()) and not Cfg.listed(None, "a") and Cfg.listed("a, B", "b"), "X: kindList / listed")
    # ---------------------------------------------------------------- the level curve (Pets-Spec 3 table)
    want = {2: 60, 5: 240, 10: 570, 15: 950, 20: 1400, 25: 2000, 30: 2700, 40: 4700, 50: 7650, 60: 12000, 70: 17500, 80: 24500, 90: 33500, 100: 45000}
    got = dict((l, int(Math_.need(l))) for l in want)
    K.check(got == want, "X: XP per level = the Pets-Spec 3 table: %s" % got)
    tot = int(Math_.total(100))
    K.check(1200000 < tot < 1350000 and int(Math_.need(1)) == 0 and int(Math_.clampLevel(0)) == 1 and int(Math_.clampLevel(500)) == 100,
            "X: total to Lv 100 about 1.28 million (%d), clamps" % tot)
    # ---------------------------------------------------------------- records
    rc = Rec("k1")
    rc.create("aaaaaaaa", "Wolf", 3, 1, 0, "test", 1000)
    rc.create("bbbbbbbb", "Rabbit", 1, 99, 0, "test", 1000)
    K.check(jall(rc.ids()) == ["aaaaaaaa", "bbbbbbbb"] and rc.count() == 2 and rc.has("aaaaaaaa") and not rc.has("") and not rc.has(None)
            and str(rc.kindOf("aaaaaaaa")) == "Wolf" and int(rc.rarityOf("aaaaaaaa")) == 3 and str(rc.get("album")) == "Wolf,Rabbit"
            and str(rc.get("pet.aaaaaaaa.skin")) == "Wolf_Black" and str(rc.get("cmd")) == "follow" and str(rc.get("shown.1")) == "true",
            "X: record create (ids, kind, rarity, album, skin = model id, cmd follow, shown.1 true)")
    K.check(int(rc.addXp("aaaaaaaa", 30.4)) == 0 and int(rc.xpOf("aaaaaaaa")) == 30 and int(rc.addXp("aaaaaaaa", 29.7)) == 1 and int(rc.levelOf("aaaaaaaa")) == 2
            and int(rc.xpOf("aaaaaaaa")) == 0, "X: addXp keeps the fraction in memory (30.4 + 29.7 = 60 = Lv 2)")
    K.check(int(rc.addXp("aaaaaaaa", 120 + 180 + 5)) == 2 and int(rc.levelOf("aaaaaaaa")) == 4, "X: several levels at once")
    K.check(int(rc.addXp("bbbbbbbb", 10 ** 9)) == 1 and int(rc.levelOf("bbbbbbbb")) == 100 and int(rc.xpOf("bbbbbbbb")) == 0
            and int(rc.addXp("bbbbbbbb", 500)) == 0, "X: Lv 100 is the max (XP stops)")
    K.check(int(rc.addXp("nope", 5)) == 0 and int(rc.addXp("aaaaaaaa", -5)) == 0 and int(rc.addXp("aaaaaaaa", float("inf"))) == 0, "X: addXp refusals")
    rc.set("active.1", "aaaaaaaa")
    rc.set("active.2", "zzzz")
    K.check(str(rc.active(1)) == "aaaaaaaa" and str(rc.active(2)) == "" and int(rc.slotOf("aaaaaaaa")) == 1 and int(rc.slotOf("")) == 0
            and rc.anyActive() and not rc.unlocked(), "X: slots (a slot pointing at a pet not in the file = empty)")
    gone = rc.remove("aaaaaaaa")
    K.check(gone.size() >= 7 and not rc.has("aaaaaaaa") and str(rc.get("active.1")) == "" and rc.remove(None).size() == 0, "X: remove takes the lines + clears its slot")
    K.check(int(rc.lv("nope", 7)) == 7 and int(rc.lv("pet.bbbbbbbb.kind", 3)) == 3, "X: lv default on missing / non-number")
    # ---------------------------------------------------------------- store: pkey, save / load, unreadable files
    root = os.path.join(mods, "Skyy_SkyyPets")
    Store.ROOT = Paths.get(root)
    Store.DIR = Paths.get(root, "pets")
    u1 = UUID.fromString("11111111-1111-4111-8111-111111111111")
    K.check(str(Store.pkey(u1)) == str(u1) and str(Store.pkey(None)) == "", "X: pkey without SkyyProfiles = the UUID")
    br.put("profile:fn:key", keyfn)
    state["profile"][str(u1)] = str(u1) + "-p2"
    K.check(str(Store.pkey(u1)) == str(u1) + "-p2", "X: pkey through profile:fn:key")
    state["profile"].clear()
    K.check(Store.keyOk("abc-p2") and not Store.keyOk("a/b") and not Store.keyOk("") and not Store.keyOk(None) and Store.file("..x") is None, "X: key sanitising")
    ra = Store.get("alpha")
    K.check(not ra.bad and ra.count() == 0 and ra.equals(Store.get("alpha")), "X: a profile without a file = an empty record (cached)")
    K.check(not os.path.exists(os.path.join(root, "pets", "alpha.properties")), "X: nothing written for a fresh record")
    nid = str(Ops.create(ra, None, "Fox", 2, 5, 17, "admin", "tester", True))
    pf = os.path.join(root, "pets", "alpha.properties")
    K.check(len(nid) == 8 and os.path.isfile(pf) and str(ra.active(1)) == nid and str(Store.INDEX.get(nid)) == "alpha", "X: create -> saved at once, slot 1, index")
    t1 = open(pf, encoding="latin-1").read()
    K.check("seq=1" in t1 and "v=1" in t1 and ("pet.%s.kind=Fox" % nid) in t1 and t1.startswith("# SkyyPets"), "X: file format (seq, v, sorted lines)")
    ra.addXp(nid, 50)
    K.check(Store.save(ra) and "seq=2" in open(pf, encoding="latin-1").read() and not ra.isDirty(), "X: seq + 1 on every save")
    K.check(not os.path.exists(pf + ".tmp"), "X: no tmp file left")
    led = open(os.path.join(root, "ledger.log"), encoding="utf-8").read()
    K.check(("\t%s\tFox\t2\t5\t17\t\talpha\tadmin\ttester" % nid) in led, "X: ledger line of the create: %r" % led[-200:])
    lf = Store.ledgerFind(nid)
    K.check(lf is not None and str(lf[2]) == "Fox" and Store.ledgerFind("zzzzzzzz") is None, "X: ledgerFind")
    Store.REC.clear()
    rb = Store.get("alpha")
    K.check(not rb.bad and rb.has(nid) and int(rb.levelOf(nid)) == 5 and int(rb.xpOf(nid)) == 67 and str(rb.active(1)) == nid, "X: read back after the cache was cleared")
    # unreadable: a folder, a bad \\u escape, a newer format -> bad, never written
    os.makedirs(os.path.join(root, "pets", "folder.properties"))
    with open(os.path.join(root, "pets", "esc.properties"), "w", encoding="latin-1") as f_:
        f_.write("v=1\npet.x.kind=\\uZZZZ\n")
    with open(os.path.join(root, "pets", "newer.properties"), "w", encoding="latin-1") as f_:
        f_.write("v=2\npet.abcdefgh.kind=Fox\n")
    open(os.path.join(root, "pets", "empty.properties"), "wb").close()
    with open(os.path.join(root, "pets", "nov.properties"), "w", encoding="latin-1") as f_:
        f_.write("# SkyyPets pet records\nactive.1=abcdefgh\npet.abcdefgh.kind=Fox\npet.abcdefgh.level=40\n")
    h_bad = tree_hash(os.path.join(root, "pets"))
    for key in ("folder", "esc", "newer", "empty", "nov"):
        rr = Store.get(key)
        K.check(rr.bad and Store.BAD.containsKey(key), "X: unreadable %s -> bad (%s)" % (key, rr.why))
        K.check(not Store.save(rr), "X: a bad record is never saved (%s)" % key)
    state["online"] = [str(u1)]
    state["names"][str(u1)] = "Alice"
    state["profile"][str(u1)] = "esc"
    K.check(str(Ops.toSlot(u1, "x", 1, "a")).startswith("-Your pet file could not be read"), "X: slot change on a bad file refused")
    K.check("empty" in str(Store.get("empty").why) and "no v=1" in str(Store.get("nov").why), "FIX1: 0-byte / no v=1 files say why")
    state["profile"][str(u1)] = "nov"
    K.check(not Ops.starter(u1, Store.get("nov")) and str(Ops.admin("adm", "give", "Alice", "Fox", None, None)).startswith("-"),
            "FIX1: a cut-off file (no v=1) gets no new starter and no give")
    state["profile"][str(u1)] = "empty"
    K.check(not Ops.starter(u1, Store.get("empty")), "FIX1: a 0-byte file gets no new starter")
    state["profile"][str(u1)] = "esc"
    K.check("could not be read" in str(Ops.admin("adm", "list", "Alice", None, None, None)), "X: /petadmin list shows why")
    K.check(str(Ops.admin("adm", "give", "Alice", "Fox", None, None)).startswith("-") and not Ops.starter(u1, Store.get("esc")), "X: give / starter refused on a bad file")
    K.check(Buff.text(Buff.compute(Store.get("esc"), None)) == "" and int(Xp.give(u1, "Mining", 100)) == 0, "X: a bad file gives no buffs and gets no XP")
    K.check(tree_hash(os.path.join(root, "pets")) == h_bad, "X: the unreadable files are byte-identical after every attempt")
    state["profile"].clear()
    # ---------------------------------------------------------------- the startup check: duplicate ids, quarantine, clean scans write nothing
    shutil.rmtree(os.path.join(root, "pets", "folder.properties"))
    os.remove(os.path.join(root, "pets", "esc.properties"))
    os.remove(os.path.join(root, "pets", "newer.properties"))
    os.remove(os.path.join(root, "pets", "empty.properties"))
    os.remove(os.path.join(root, "pets", "nov.properties"))
    with open(os.path.join(root, "pets", "beta.properties"), "w", encoding="latin-1") as f_:
        f_.write("seq=9\nv=1\npet.%s.kind=Fox\npet.%s.rarity=4\npet.%s.level=30\nactive.1=%s\n" % (nid, nid, nid, nid))
    sc = list(Store.scanAll())
    K.check(sc == [2, 1, 0, 1] and str(Store.INDEX.get(nid)) == "beta", "X: scan: 2 files, the id in both -> kept in beta (seq 9 > 2): %s" % sc)
    qd = os.path.join(root, "quarantine")
    qf = os.listdir(qd) if os.path.isdir(qd) else []
    K.check(len(qf) == 1 and qf[0].startswith(nid + "-alpha-") and ("pet.%s.kind=Fox" % nid) in open(os.path.join(qd, qf[0]), encoding="latin-1").read(),
            "X: the alpha copy went to quarantine/: %s" % qf)
    at = open(os.path.join(root, "pets", "alpha.properties"), encoding="latin-1").read()
    K.check(("pet.%s." % nid) not in at and "active.1=\n" in at, "X: alpha no longer holds the pet (and its slot is empty)")
    K.check("quarantine\tduplicate (kept in beta)\tstartup" in open(os.path.join(root, "ledger.log"), encoding="utf-8").read(), "X: quarantine ledger line")
    h1 = tree_hash(root)
    sc2 = list(Store.scanAll())
    K.check(sc2 == [2, 1, 0, 0] and tree_hash(root) == h1, "X: a scan without conflicts writes nothing: %s" % sc2)
    with open(os.path.join(root, "pets", "gamma.properties"), "w", encoding="latin-1") as f_:
        f_.write("seq=9\nv=1\npet.%s.kind=Fox\n" % nid)
    sc3 = list(Store.scanAll())
    K.check(sc3[3] == 1 and str(Store.INDEX.get(nid)) == "beta" and ("pet.%s." % nid) not in open(os.path.join(root, "pets", "gamma.properties"), encoding="latin-1").read(),
            "X: equal seq -> the first file name keeps it: %s" % sc3)
    for f_ in ("beta", "gamma", "alpha"):
        os.remove(os.path.join(root, "pets", f_ + ".properties"))
    Store.scanAll()
    # ---------------------------------------------------------------- buffs + delivery
    u2 = UUID.fromString("22222222-2222-4222-8222-222222222222")
    state["online"] = [str(u1), str(u2)]
    state["names"][str(u2)] = "Bob"
    rr = Store.get(str(u2))
    wolf = str(Ops.create(rr, None, "Wolf", 5, 100, 0, "test", "t", True))
    rab = str(Ops.create(rr, None, "Rabbit", 3, 50, 0, "test", "t", True))
    t = Buff.compute(rr, None)
    K.check(abs(Buff.get(t, "str") - 20.0) < 1e-6 and abs(Buff.get(t, "cd") - 15.0) < 1e-6 and Buff.get(t, "fortune.farming") == 0.0,
            "X: slot 1 Legendary Lv 100 Wolf = the full table values; slot 2 empty")
    K.check(str(Ops.toSlot(u2, rab, 2, "t")).startswith("-The summon slot is locked"), "X: slot 2 locked (quest mode, not unlocked)")
    rr.set("slot2.unlocked", "true")
    K.check(str(Ops.toSlot(u2, rab, 2, "t")).startswith("+") and str(rr.active(2)) == rab, "X: slot 2 after unlock")
    t = Buff.compute(rr, None)
    K.check(abs(Buff.get(t, "fortune.farming") - 10.0 * 0.6 * 0.5 * 0.5) < 1e-6, "X: slot 2 = 50%% x Rare 0.6 x Lv 50/100 (1.5 Fortune): %s" % Buff.get(t, "fortune.farming"))
    CfgFn.cmdSetConsole("pets.slot2.unlock", "off")
    K.check(Buff.get(Buff.compute(rr, None), "fortune.farming") == 0.0 and not Buff.slot2Open(rr), "X: summon slot closed for everyone")
    _m = str(Ops.toSlot(u2, wolf, 2, "t"))
    K.check(_m.startswith("-The summon slot is locked") and "closed on this server" in _m and "Stable" not in _m, "FIX5: closed mode says closed, not the quest: %s" % _m)
    CfgFn.cmdSetConsole("pets.slot2.unlock", "quest")
    K.check("Zone 2 Stable" in str(Buff.lockedWhy()) and not Buff.slot2Open(Rec("lockq")), "FIX5: quest mode still names the Stable quest")
    CfgFn.cmdSetConsole("pets.slot2.unlock", "off")
    CfgFn.cmdSetConsole("pets.slot2.unlock", "always")
    rr.set("slot2.unlocked", None)
    K.check(Buff.slot2Open(rr) and Buff.get(Buff.compute(rr, None), "fortune.farming") > 0.0, "X: summon slot always open")
    CfgFn.cmdSetConsole("pets.slot2.unlock", "quest")
    rr.set("slot2.unlocked", "true")
    CfgFn.cmdSetConsole("pets.kinds.off", "Wolf")
    t = Buff.compute(rr, None)
    K.check(Buff.get(t, "str") == 0.0 and Buff.get(t, "fortune.farming") > 0.0, "X: a kind switched off gives nothing (the other still does)")
    CfgFn.cmdSetConsole("pets.kinds.off", "-")
    CfgFn.cmdSetConsole("pets.worlds.noBuffs", "dungeon1, arena")
    K.check(Buff.text(Buff.compute(rr, "arena")) == "" and Buff.get(Buff.compute(rr, "default"), "str") > 0.0, "X: no buffs in a listed world")
    CfgFn.cmdSetConsole("pets.worlds.noBuffs", "-")
    goat = str(Ops.create(rr, None, "Goat", 5, 100, 0, "test", "t", True))
    rr.set("active.1", goat)
    rr.set("active.2", None)
    rab2 = str(Ops.create(rr, None, "Bunny", 5, 100, 0, "test", "t", True))
    CfgFn.cmdSetConsole("pets.swing.cap", "3")
    t = Buff.compute(rr, None)
    K.check(abs(Buff.get(t, "fortune.mining") - 10.0) < 1e-6 and abs(Buff.get(t, "swing.mining") - 3.0) < 1e-6, "X: swing capped at the row (3)")
    CfgFn.cmdSetConsole("pets.swing.cap", "5")
    Ops.toSlot(u2, rab2, 2, "t")
    CfgFn.cmdSetConsole("pets.fortune.cap", "4")
    K.check(abs(Buff.get(Buff.compute(rr, None), "fortune.farming") - 4.0) < 1e-6, "X: Fortune capped at the row (4)")
    CfgFn.cmdSetConsole("pets.fortune.cap", "10")
    rr.set("active.1", wolf)
    t = Buff.compute(rr, None)
    Buff.publish(u2, t)
    ps = br.get("pets:stats:" + str(u2))
    sb = br.get("skill:bonus:" + str(u2))
    K.check(ps is not None and abs(float(ps.get("str")) - 20.0) < 1e-6 and ps.get("health") is None and ps.get("fortune.farming") is None,
            "X: pets:stats carries only what SkyyPets does not apply (SkyyGear keys): %s" % ps)
    K.check(sb is not None and abs(float(sb.get("pets").get("dd.farming")) - 0.05) < 1e-9, "X: skill:bonus pets dd.farming = Fortune / 100: %s" % (sb.get("pets") if sb else None))
    try:
        ps.put("x", 1.0)
        K.check(False, "X: pets:stats map must be unmodifiable")
    except Exception:
        K.check(True, "X: pets:stats map is unmodifiable")
    K.check(Buff.LAST.get(u2) is not None, "X: publish remembers what it sent")
    Sys_ = JClass("java.lang.System")
    id0 = int(Sys_.identityHashCode(br.get("pets:stats:" + str(u2))))
    Buff.publish(u2, t)
    K.check(int(Sys_.identityHashCode(br.get("pets:stats:" + str(u2)))) == id0, "X: publish with unchanged totals touches nothing")
    br.remove("pets:stats:" + str(u2))
    sb.remove("pets")
    K.check(not bool(Buff.intact(u2, t)), "FIX2-B2: intact() sees the removed entries")
    Buff.publish(u2, t)
    K.check(br.get("pets:stats:" + str(u2)) is not None and sb.get("pets") is not None, "FIX2-B2: unchanged totals but entries removed by another mod -> re-posted")
    br.remove("skill:bonus:" + str(u2))
    Buff.publish(u2, t)
    sb = br.get("skill:bonus:" + str(u2))
    K.check(sb is not None and sb.get("pets") is not None, "FIX2-B2: a replaced (removed) skill:bonus container is re-created + re-filled")
    horse = str(Ops.create(rr, None, "Horse", 5, 100, 0, "test", "t", True))
    rr.set("active.1", horse)
    rr.set("active.2", None)
    rr.set("slot2.unlocked", "false")
    t = Buff.compute(rr, None)
    Buff.publish(u2, t)
    mv = br.get("move:" + str(u2))
    K.check(mv is not None and str(mv.get("pets").get("layer")) == "pct" and abs(float(mv.get("pets").get("speed")) - 0.05) < 1e-6
            and br.get("pets:stats:" + str(u2)) is None and (sb.get("pets") is None), "X: move pets = +5%% pct speed; gear + bonus removed when empty")
    sm = FSM(3)
    Buff.stats(sm, t)
    K.check(abs(float(sm.vals[1].mx) - 120.0) < 1e-3 and sm.vals[1].mods.get("skyypet_stamina") is not None and int(sm.puts) == 1, "X: skyypet_stamina MAX +20 applied")
    Buff.stats(sm, t)
    K.check(int(sm.puts) == 1, "X: an equal modifier is not put again")
    t2 = Buff.compute(rr, None)
    t2[Kind.statIndex("stamina")] = 7.5
    t2[Kind.statIndex("health")] = 60.0
    Buff.stats(sm, t2)
    K.check(abs(float(sm.vals[1].mx) - 107.5) < 1e-3 and abs(float(sm.vals[0].mx) - 160.0) < 1e-3, "X: modifiers updated (stamina 7.5, health 60)")
    Buff.stats(sm, JArray(JDouble)([0.0] * len(t2)))
    K.check(int(sm.removes) == 2 and abs(float(sm.vals[0].mx) - 100.0) < 1e-3 and sm.vals[0].mods.isEmpty(), "X: modifiers removed at 0")
    Buff.mod(None, 0, "k", 1.0)
    Buff.mod(sm, -1, "k", 1.0)
    Buff.stats(None, t2)
    Buff.clear(u2)
    K.check(br.get("pets:stats:" + str(u2)) is None and mv.get("pets") is None and Buff.LAST.get(u2) is None, "X: clear removes every bridge entry")
    Buff.publish(u2, Buff.compute(rr, None))
    Store.KEYOF.put(u2, str(u2))
    K.check(br.get("move:" + str(u2)).get("pets") is not None and int(Buff.clearAll()) >= 1 and br.get("move:" + str(u2)).get("pets") is None
            and Buff.LAST.get(u2) is None, "FIX2-B1: clearAll (shutdown) takes every player's pets entries off the bridge")
    Store.KEYOF.remove(u2)
    K.check(str(Buff.fmt(0.03)) == "0.03" and str(Buff.fmt(0.015)) == "0.02" and str(Buff.fmt(0.5)) == "0.5" and str(Buff.fmt(0.25)) == "0.25"
            and str(Buff.fmt(2.5)) == "2.5" and str(Buff.fmt(20.0)) == "20" and str(Buff.fmt(-0.07)) == "-0.07", "FIX2-C2: small values keep two decimals")
    rz = Rec("rz")
    rz.create("rabbit01", "Rabbit", 1, 1, 0, "t", 1)
    K.check(str(Buff.petText(rz, "rabbit01", 100.0)) == "+0.03 Farming Fortune" and str(Buff.petText(rz, "rabbit01", 50.0)) == "+0.02 Farming Fortune",
            "FIX2-C2: the Common Lv 1 starter Rabbit shows its buff, not 'nothing': %s / %s" % (Buff.petText(rz, "rabbit01", 100.0), Buff.petText(rz, "rabbit01", 50.0)))
    K.check("+5 Speed %" in str(Buff.text(t)) and "+2.5 Speed %" in str(Buff.petText(rr, horse, 50.0)) and str(Buff.petText(rr, "nope", 100.0)) == "nothing",
            "X: buff texts: %s / %s" % (Buff.text(t), Buff.petText(rr, horse, 50.0)))
    # ---------------------------------------------------------------- XP: give, pets:fn:onxp, the fallback poll
    rr.set("active.1", wolf)
    rr.set("slot2.unlocked", "true")
    rr.set("active.2", rab)
    lvr = int(rr.levelOf(rab))
    x0 = int(rr.xpOf(rab))
    K.check(int(Xp.give(u2, "Combat.Archer", 1000)) == 2, "X: XP into both slotted pets")
    K.check(int(rr.levelOf(wolf)) == 100 and int(rr.xpOf(rab)) == x0 + 500 and int(rr.levelOf(rab)) == lvr, "X: the Rabbit got 50%% of Combat XP (%d -> %d)" % (x0, int(rr.xpOf(rab))))
    xb = int(Rec("t").xpOf("x"))
    r5 = Rec("r5")
    r5.create("cccccccc", "Rabbit", 1, 1, 0, "t", 1)
    r5.set("active.1", "cccccccc")
    Store.REC.put(str(UUID.fromString("55555555-5555-4555-8555-555555555555")), r5)
    u5 = UUID.fromString("55555555-5555-4555-8555-555555555555")
    Xp.give(u5, "Mining", 100)
    K.check(int(r5.xpOf("cccccccc")) == 50 and xb == 0, "X: other skill = 50%% (100 Mining XP -> 50 into a Farming pet)")
    Xp.give(u5, "farming", 10)
    K.check(int(r5.levelOf("cccccccc")) == 2 and int(r5.xpOf("cccccccc")) == 0 and any("reached Lv 2" in m_[1] for m_ in state["tells"]),
            "X: own skill = 100%% (case-insensitive), level-up chat line")
    r5.set("active.2", None)
    K.check(int(Xp.give(u5, "Farming", 0)) == 0 and int(Xp.give(None, "Farming", 5)) == 0 and int(Xp.give(u5, None, 5)) == 0
            and int(Xp.give(UUID.randomUUID(), "Farming", 5)) == 0, "X: give refusals (0, no player, no skill, record not loaded)")
    CfgFn.cmdSetConsole("pets.xp.otherPercent", "0")
    K.check(int(Xp.give(u5, "Mining", 100)) == 0, "X: other percent 0 -> nothing")
    CfgFn.cmdSetConsole("pets.xp.otherPercent", "50")
    fn = XpFn()
    Obj = JClass("java.lang.Object")
    jb = lambda o: o is not None and bool(o.booleanValue())
    K.check(not jb(fn.apply(None)) and not jb(fn.apply(JArray(Obj)([u5, "Farming"]))) and fn.apply(None) is not None
            and not jb(fn.apply(JArray(Obj)(["notauuid", "Farming", JLong(5)]))), "X: pets:fn:onxp bad arguments -> FALSE")
    K.check(not bool(Xp.HOOKED), "X: not hooked before a SkyySkills call")
    K.check(jb(fn.apply(JArray(Obj)([u5, "Farming", JLong(10), "SkyyFishing"]))) and not bool(Xp.HOOKED),
            "X: another mod's call (4th element) gives XP but does not switch the fallback off")
    K.check(jb(fn.apply(JArray(Obj)([u5, "Farming", JLong(10)]))) and not bool(Xp.HOOKED), "FIX2-B3: a call without a 4th element gives XP but leaves the fallback on")
    K.check(jb(fn.apply(JArray(Obj)([u5, "Farming", JLong(10), "skyyskills"]))) and bool(Xp.HOOKED), "X: a SkyySkills call (4th element SkyySkills) -> TRUE + fallback off")
    K.check(any("reports XP to pets itself" in str(x) for x in lines), "X: the switch is logged")
    Xp.HOOKED = False
    br.put("skill:fn:xp", xpfn)
    Store.KEYOF.put(u5, str(u5))
    state["online"] = [str(u5)]
    state["totals"][(str(u5), "Mining")] = 1000
    x1 = int(r5.xpOf("cccccccc"))
    DEF_POLL = str(Cfg.POLL_SKILLS)
    K.check("Combat.Priest" in DEF_POLL and "Combat" not in [x.strip() for x in DEF_POLL.split(",")], "FIX2: default fallback skills = per-class rows, no bare Combat: %s" % DEF_POLL)
    Cfg.POLL_SKILLS = "Mining,Farming"
    K.check(int(Xp.poll()) == 0 and int(r5.xpOf("cccccccc")) == x1, "X: fallback: the first read is only the baseline")
    state["totals"][(str(u5), "Mining")] = 1100
    K.check(int(Xp.poll()) == 1 and int(r5.xpOf("cccccccc")) == x1 + 50, "X: fallback: +100 Mining -> +50 into the Farming pet")
    state["totals"][(str(u5), "Mining")] = 900
    Xp.poll()
    state["totals"][(str(u5), "Mining")] = 900 + 5000000
    Xp.poll()
    K.check(int(r5.xpOf("cccccccc")) == x1 + 50, "X: fallback: a drop and a jump over 1,000,000 only re-baseline")
    Store.KEYOF.put(u5, "other-key")
    state["totals"][(str(u5), "Mining")] = 900 + 5000100
    Xp.poll()
    K.check(int(r5.xpOf("cccccccc")) == x1 + 50, "X: fallback: a new profile key starts a new baseline")
    Store.KEYOF.put(u5, str(u5))
    # FIX3: the profile flipped (profile:fn:key) before the tick refreshed KEYOF -> no cross-profile delta, poll skips the player
    Xp.poll()
    xs = int(r5.xpOf("cccccccc"))
    sk0 = int(Xp.SKIPPED.get())
    state["profile"][str(u5)] = str(u5) + "-B"
    state["totals"][(str(u5), "Mining")] += 75000
    K.check(int(Xp.poll()) == 0 and int(r5.xpOf("cccccccc")) == xs and int(Xp.SKIPPED.get()) == sk0 + 1,
            "FIX3: a poll in the profile-switch gap pays nothing (key %s vs KEYOF %s)" % (Store.pkey(u5), Store.KEYOF.get(u5)))
    state["profile"][str(u5)] = str(u5)
    state["totals"][(str(u5), "Mining")] -= 75000
    Xp.forget(u5)
    # FIX2: the bare "Combat" (= current class skill) is never polled - a class switch must not read as a gain
    Cfg.POLL_SKILLS = "Combat,Combat.Warrior"
    state["totals"][(str(u5), "Combat")] = 50000
    state["totals"][(str(u5), "Combat.Warrior")] = 50000
    Xp.poll()
    xc = int(r5.xpOf("cccccccc"))
    lc = int(r5.levelOf("cccccccc"))
    state["totals"][(str(u5), "Combat")] = 200000
    K.check(int(Xp.poll()) == 0 and int(r5.xpOf("cccccccc")) == xc and int(r5.levelOf("cccccccc")) == lc
            and not any(str(k).endswith("|Combat") for k in Xp.BASE.keySet()), "FIX2: a class switch (Combat 50k -> 200k) gives no pet XP, Combat never baselined")
    state["totals"][(str(u5), "Combat.Warrior")] = 50100
    K.check(int(Xp.poll()) == 1 and int(r5.xpOf("cccccccc")) == xc + 50, "FIX2: a per-class row still pays (+100 Combat.Warrior -> +50 into the Farming pet)")
    Cfg.POLL_SKILLS = "Mining,Farming"
    Xp.HOOKED = True
    state["totals"][(str(u5), "Mining")] += 100
    K.check(int(Xp.poll()) == 0, "X: fallback off once hooked")
    Xp.HOOKED = False
    CfgFn.cmdSetConsole("pets.xp.fallback", "false")
    K.check(int(Xp.poll()) == 0, "X: fallback switched off in Server Setup")
    CfgFn.cmdSetConsole("pets.xp.fallback", "true")
    br.remove("skill:fn:xp")
    K.check(int(Xp.poll()) == 0, "X: no SkyySkills -> nothing to read")
    br.put("skill:fn:xp", xpfn)
    Xp.forget(u5)
    K.check(not any(str(k).startswith(str(u5)) for k in Xp.BASE.keySet()) and Xp.forget(None) is None, "X: forget drops the baselines")
    Cfg.POLL_SKILLS = DEF_POLL
    # ---------------------------------------------------------------- slots, starter, admin
    state["online"] = [str(u1), str(u2)]
    rr1 = Store.get(str(u1))
    K.check(Ops.starter(u1, rr1) and rr1.count() == 1 and str(rr1.kindOf(rr1.active(1))) == "Rabbit" and int(rr1.rarityOf(rr1.active(1))) == 1
            and rr1.get("starter") is not None and any("your first pet" in m_[1] for m_ in state["tells"]), "X: starter Rabbit once, in the pet slot")
    K.check(not Ops.starter(u1, rr1) and rr1.count() == 1, "X: never a second starter")
    r6 = Rec("r6")
    Cfg.STARTER = "none"
    K.check(not Ops.starter(u1, r6) and r6.get("starter") is None, "X: starter none")
    Cfg.STARTER = "Rabbit"
    CfgFn.cmdSetConsole("pets.kinds.off", "Rabbit")
    K.check(not Ops.starter(u1, r6), "X: starter kind switched off -> none")
    CfgFn.cmdSetConsole("pets.kinds.off", "-")
    p1 = rr1.active(1)
    K.check(str(Ops.toSlot(u1, p1, 1, "a")).startswith("=That pet is already"), "X: already in that slot")
    K.check(str(Ops.toSlot(u1, "nope", 1, "a")).startswith("-That pet is not yours"), "X: not yours")
    K.check(str(Ops.toSlot(u1, p1, 3, "a")).startswith("-") , "X: no slot 3")
    K.check(str(Ops.takeOut(u1, p1, "a")).startswith("+") and str(rr1.active(1)) == "" and str(Ops.takeOut(u1, p1, "a")).startswith("=That pet is not in a slot")
            and str(Ops.takeOut(u1, "nope", "a")).startswith("-"), "X: take out")
    CfgFn.cmdSetConsole("pets.enabled", "false")
    K.check(str(Ops.toSlot(u1, p1, 1, "a")).startswith("-Pets are switched off") and str(Ops.takeOut(u1, p1, "a")).startswith("-Pets are switched off")
            and int(Xp.give(u2, "Combat", 5)) == 0 and Buff.text(Buff.compute(rr, None)) == "" and not Ops.starter(u1, r6), "X: part off: no moves, XP, buffs, starter")
    CfgFn.cmdSetConsole("pets.enabled", "true")
    A = lambda *a: str(Ops.admin("Adm", *(list(a) + [None] * (5 - len(a)))))
    K.check(A("help").startswith("=/petadmin give") and A("").startswith("=/petadmin") and "Stat keys" in A("kinds") and A("bogus").startswith("-Unknown"),
            "X: admin help / kinds / unknown")
    K.check(A("give").startswith("-Which player") and A("give", "Nobody").startswith("-Nobody is not online"), "X: admin needs an online player")
    K.check("Alice (" in A("list", "Alice") and A("list", "alice").count("\n") >= 1, "X: admin list (case-insensitive name)")
    K.check(A("unlock", "Alice").startswith("+") and Store.get(str(u1)).unlocked() and A("unlock", "Alice").startswith("=") and any("summon slot is unlocked" in m_[1] for m_ in state["tells"]),
            "X: admin unlock (+ chat), twice = already")
    K.check(A("lock", "Alice").startswith("+") and not Store.get(str(u1)).unlocked(), "X: admin lock")
    K.check(A("give", "Alice").startswith("-Which kind") and A("give", "Alice", "Dragon").startswith("-No pet kind") and A("give", "Alice", "Fox", "Mythic").startswith("-Rarity")
            and A("give", "Alice", "Fox", "Rare", "0").startswith("-Level") and A("give", "Alice", "Fox", "Rare", "x").startswith("-Level"), "X: admin give refusals")
    CfgFn.cmdSetConsole("pets.kinds.off", "Fox")
    K.check("switched off" in A("give", "Alice", "Fox"), "X: admin give of a switched-off kind")
    CfgFn.cmdSetConsole("pets.kinds.off", "-")
    g = A("give", "Alice", "Fox")
    K.check(g.startswith("+Gave Alice a Uncommon Fox Lv 1") and "in the pet slot" in g, "X: give default rarity + level, empty pet slot filled: %s" % g)
    g2 = A("give", "Alice", "Skeleton", "Legendary", "42")
    gid = g2.split("(id ")[1].split(")")[0].split(",")[0]
    K.check(g2.startswith("+Gave Alice a Legendary Skeleton Lv 42") and int(Store.get(str(u1)).levelOf(gid)) == 42, "X: give rarity + level: %s" % g2)
    CfgFn.cmdSetConsole("pets.owned.max", "3")
    K.check(A("give", "Alice", "Fox").startswith("-That collection is full"), "X: the owned cap")
    CfgFn.cmdSetConsole("pets.owned.max", "120")
    tk = A("take", "Alice", gid)
    K.check(tk.startswith("+Took Alice's Legendary Skeleton") and not Store.get(str(u1)).has(gid) and Store.INDEX.get(gid) is None, "X: admin take: %s" % tk)
    K.check(A("take", "Alice", "nope").startswith("-Alice has no pet"), "X: take unknown id")
    K.check(A("restore", "Alice").startswith("-Which pet id") and A("restore", "Alice", "zzzzzzzz").startswith("-Pet zzzzzzzz is not in ledger")
            and "still belongs" in A("restore", "Alice", str(Store.get(str(u1)).active(1))), "X: restore refusals")
    K.check(A("restore", "Alice", "-").startswith("-- is not a pet id") and A("restore", "Alice", "abc").startswith("-abc is not a pet id")
            and not any(str(i_).startswith("pet.-.") for i_ in Store.get(str(u1)).p.stringPropertyNames()), "FIX2-A2: restore '-' (the unlock / lock ledger lines) refused, no junk pet")
    K.check(Store.ledgerFind("-") is None, "FIX2-A2: ledgerFind never returns a '-' line")
    Store.BAD.put("brokenkey", "test")
    rb = A("restore", "Alice", gid)
    K.check(rb.startswith("-Not now: 1 pet file(s) could not be read (brokenkey)") and not Store.get(str(u1)).has(gid), "FIX2-A1: restore refused while a pet file is unreadable: %s" % rb)
    Store.BAD.remove("brokenkey")
    with open(os.path.join(root, "ledger.log"), "a", encoding="utf-8") as lf_:
        lf_.write(chr(9).join(["1", "qqqqqqqq", "Griffin", "3", "5", "0", "", "someone", "admin", "Adm"]) + chr(10))
    K.check(A("restore", "Alice", "qqqqqqqq").startswith("-Pet qqqqqqqq was a Griffin, and that pet kind does not exist"), "FIX2-A2: restore of a kind that does not exist refused")
    rs = A("restore", "Alice", gid)
    K.check(rs.startswith("+Restored Legendary Skeleton Lv 42") and Store.get(str(u1)).has(gid) and str(Store.INDEX.get(gid)) == str(u1), "X: restore from the ledger: %s" % rs)
    with open(os.path.join(root, "pets", "latekey.properties"), "w", encoding="latin-1") as f_:
        f_.write(chr(10).join(["pet.late0001.kind=Fox", "pet.late0001.level=3", "pet.late0001.rarity=2", "seq=1", "v=1", ""]))
    K.check(Store.INDEX.get("late0001") is None and Store.get("latekey").has("late0001") and str(Store.INDEX.get("late0001")) == "latekey",
            "FIX2-A1: a file read after the startup scan puts its pet ids into INDEX")
    K.check("still belongs to latekey" in A("restore", "Alice", "late0001"), "FIX2-A1: restore of an id from a file read later is refused (no duplicate)")
    lc0 = int(Store.LATE_CLASH)
    with open(os.path.join(root, "pets", "latekey2.properties"), "w", encoding="latin-1") as f_:
        f_.write(chr(10).join(["pet.%s.kind=Skeleton" % gid, "seq=1", "v=1", ""]))
    Store.get("latekey2")
    K.check(int(Store.LATE_CLASH) == lc0 + 1 and str(Store.INDEX.get(gid)) == str(u1) and any("read after the startup check" in str(x) for x in lines),
            "FIX2-A1: a late file holding an id another profile owns is logged, the index keeps the first owner")
    Store.REC.remove("latekey"); Store.REC.remove("latekey2"); Store.INDEX.remove("late0001")
    os.remove(os.path.join(root, "pets", "latekey.properties")); os.remove(os.path.join(root, "pets", "latekey2.properties"))
    K.check(A("xp", "Alice").startswith("-Use") and A("xp", "Alice", "Combat", "-5").startswith("-Amount") and A("xp", "Alice", "Combat", "x").startswith("-Amount"),
            "X: admin xp refusals")
    K.check(A("xp", "Alice", "Combat", "500").startswith("+1 slotted pet"), "X: admin xp -> PetXp.give: %s" % A("xp", "Alice", "Combat", "1"))
    st_lines = open(os.path.join(root, "ledger.log"), encoding="utf-8").read()
    K.check("\ttake\tAdm" in st_lines and "\trestore\tAdm" in st_lines and "unlock slot 2\tAdm" in st_lines and "\tslot\t" in st_lines and "\tstarter\tstarter" in st_lines,
            "X: ledger: take, restore, unlock, slot, starter lines")
    K.check(str(Ops.line(Store.get(str(u1)), gid)).startswith(gid + "  Legendary Skeleton  Lv 42"), "X: list line")
    # ---------------------------------------------------------------- the per-second tick, profile switch, leave, timer
    u3 = UUID.fromString("33333333-3333-4333-8333-333333333333")
    state["online"] = [str(u1), str(u2), str(u3)]
    state["names"][str(u3)] = "Cara"
    sm3 = FSM(3)
    Tick.second(u3, "default", sm3)
    r3 = Store.get(str(u3))
    K.check(r3.count() == 1 and str(Store.KEYOF.get(u3)) == str(u3) and os.path.isfile(os.path.join(root, "pets", str(u3) + ".properties")),
            "X: tick: first sight gives the starter (saved)")
    ps3 = br.get("skill:bonus:" + str(u3))
    K.check(ps3 is not None and ps3.get("pets") is not None and abs(float(ps3.get("pets").get("dd.farming")) - 0.0003) < 1e-12, "X: tick publishes (Common Lv 1 Rabbit = 0.03 Fortune)")
    r3.addXp(r3.active(1), 5)
    K.check(r3.isDirty(), "X: XP makes the record dirty")
    state["profile"][str(u3)] = str(u3) + "-p2"
    Tick.second(u3, "default", sm3)
    K.check(str(Store.KEYOF.get(u3)) == str(u3) + "-p2" and Store.REC.get(str(u3)) is None and "xp=5" in open(os.path.join(root, "pets", str(u3) + ".properties"), encoding="latin-1").read()
            and Store.get(str(u3) + "-p2").count() == 1, "X: profile switch: the old profile flushed + forgotten, the new one gets its own starter")
    K.check(any("profile switch" in str(x) for x in lines), "X: switch logged")
    CfgFn.cmdSetConsole("pets.enabled", "false")
    Tick.second(u3, "default", sm3)
    K.check(br.get("skill:bonus:" + str(u3)).get("pets") is None, "X: tick with part off clears the delivery")
    CfgFn.cmdSetConsole("pets.enabled", "true")
    K.check(Tick.due(u3, 0.4) and not Tick.due(u3, 0.4) and not Tick.due(u3, 0.4) and Tick.due(u3, 0.4), "X: due() once a second (first call due)")
    r3b = Store.get(str(u3) + "-p2")
    r3b.addXp(r3b.active(1), 7)
    Tick.leave(u3)
    for _ in range(50):
        if Store.REC.get(str(u3) + "-p2") is None:
            break
        time.sleep(0.1)
    K.check(Store.KEYOF.get(u3) is None and Store.REC.get(str(u3) + "-p2") is None and "xp=7" in open(os.path.join(root, "pets", str(u3) + "-p2.properties"), encoding="latin-1").read(),
            "X: leave: flushed on the scheduler + forgotten")
    # FIX4: one more tick after the disconnect re-adds everything; the 30 s sweep removes it again
    state["online"] = [str(u1), str(u2)]
    Tick.second(u3, "default", sm3)
    K.check(Store.KEYOF.get(u3) is not None and br.get("skill:bonus:" + str(u3)).get("pets") is not None,
            "FIX4: setup - a post-disconnect tick republished the offline player")
    _sw = int(Timer.sweep())
    K.check(_sw >= 1 and int(Timer.SWEPT.get()) >= 1, "FIX4: sweep finds the offline player(s): %d" % _sw)
    for _ in range(50):
        if Store.REC.get(str(u3) + "-p2") is None:
            break
        time.sleep(0.1)
    K.check(Store.KEYOF.get(u3) is None and Tick.CLOCK.get(u3) is None and Buff.LAST.get(u3) is None
            and br.get("skill:bonus:" + str(u3)).get("pets") is None and br.get("pets:stats:" + str(u3)) is None
            and Store.REC.get(str(u3) + "-p2") is None, "FIX4: sweep cleared KEYOF / CLOCK / LAST / bridge and released the record")
    K.check(int(Timer.sweep()) == 0, "FIX4: online players are left alone (second sweep = 0)")
    _s0 = int(Timer.SWEPT.get())
    Timer.NEXT_FLUSH = 10 ** 15
    Timer.NEXT_POLL = 10 ** 15
    Timer.NEXT_SWEEP = 0
    Tick.second(u3, "default", sm3)
    Timer().run()
    K.check(int(Timer.SWEPT.get()) >= _s0 + 1 and Store.KEYOF.get(u3) is None and int(Timer.NEXT_SWEEP) > 0, "FIX4: the timer runs the sweep (every 30 s)")
    state["online"] = [str(u1), str(u2), str(u3)]
    Tick.leave(None)
    Leave("nobody").run()
    rr.addXp(rr.active(1), 0)
    r2x = Store.get(str(u2))
    r2x.addXp(r2x.active(2), 3)
    Timer.NEXT_FLUSH = 0
    Timer.NEXT_POLL = 0
    Timer().run()
    K.check(not r2x.isDirty() and int(Timer.RUNS.get()) >= 1, "X: the timer flushes dirty records")
    K.check(int(Store.flushDirty()) == 0, "X: nothing left to flush")
    # ---------------------------------------------------------------- the page
    FP = JClass(FAKE_PKG + ".FakePr")
    U_ = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    U_.setAccessible(True)
    UN = U_.get(None)

    def fakepr(u, name):
        p_ = UN.allocateInstance(FP.class_)
        p_.fu = u
        p_.fname = name
        return p_
    pa = fakepr(u1, "Alice")
    TP = JClass(FAKE_PKG + ".TestPage")
    page = TP(pa)
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def build(pg):
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        return b_, e_
    ra1 = Store.get(str(u1))
    for i in range(8):
        Ops.create(ra1, None, "Mouse", 1, 1, 0, "test", "t", True)
    n1 = ra1.count()
    b_, e_ = build(page)
    ev0 = len(e_.getEvents())
    K.check(int(page.view) == 0 and len(page.ids) == 8 and ev0 == 1 + 8 + 2 + 1 and len(b_.getCommands()) > 40,
            "X: list view: slot 1 Open + 8 rows + prev / next + close = %d events, %d commands (%d pets)" % (ev0, len(b_.getCommands()), n1))
    page.handleDataEvent(None, None, '{"a":"next"}')
    build(page)
    K.check(int(page.pg) == 1 and len(page.ids) == n1 - 8, "X: Next page")
    page.handleDataEvent(None, None, '{"a":"next"}')
    page.handleDataEvent(None, None, '{"a":"next"}')
    build(page)
    K.check(int(page.pg) == 1, "X: Next past the end stays on the last page")
    page.handleDataEvent(None, None, '{"a":"prev"}')
    page.handleDataEvent(None, None, '{"a":"prev"}')
    build(page)
    K.check(int(page.pg) == 0 and page.rebuilds >= 5, "X: Prev (never below page 1)")
    page.handleDataEvent(None, None, '{"a":"open","i":"0","t":"stale"}')
    K.check(str(page.info).startswith("=The page changed"), "X: stale token")
    build(page)
    pick = [k for k in range(len(page.ids)) if str(page.ids[k]) != str(ra1.active(1)) and str(page.ids[k]) != str(ra1.active(2))][-1]
    page.handleDataEvent(None, None, '{"a":"open","i":"%d","t":"%s"}' % (pick, str(page.tok)))
    sel = str(page.sel)
    b_, e_ = build(page)
    K.check(int(page.view) == 1 and len(e_.getEvents()) == 1 + 4 + 1, "X: details view: 4 buttons (+ slot 1 Open + close): %d" % len(e_.getEvents()))
    page.handleDataEvent(None, None, '{"a":"to1","t":"%s"}' % str(page.tok))
    K.check(str(page.info).startswith("+") and str(ra1.active(1)) == sel, "X: Pet slot button: %s" % page.info)
    build(page)
    page.handleDataEvent(None, None, '{"a":"to2","t":"%s"}' % str(page.tok))
    K.check(str(page.info).startswith("-The summon slot is locked"), "X: Summon slot button while locked")
    ra1.set("slot2.unlocked", "true")
    build(page)
    page.handleDataEvent(None, None, '{"a":"to2","t":"%s"}' % str(page.tok))
    K.check(str(page.info).startswith("+") and str(ra1.active(2)) == sel and str(ra1.active(1)) == "", "X: moved from the pet slot to the summon slot")
    b_, e_ = build(page)
    K.check(len(e_.getEvents()) == 1 + 4 + 1, "X: details with slot 2 filled: slot 2 Open + 4 buttons + close")
    page.handleDataEvent(None, None, '{"a":"out","t":"%s"}' % str(page.tok))
    K.check(str(page.info).startswith("+") and str(ra1.active(2)) == "", "X: Take out")
    build(page)
    page.handleDataEvent(None, None, '{"a":"back"}')
    build(page)
    K.check(int(page.view) == 0, "X: Back")
    page.handleDataEvent(None, None, '{"a":"open","i":"99","t":"%s"}' % str(page.tok))
    K.check("gone" in str(page.info), "X: a row that is gone")
    build(page)
    ra1.set("active.1", sel)
    build(page)
    page.handleDataEvent(None, None, '{"a":"slot","i":"1","t":"%s"}' % str(page.tok))
    K.check(int(page.view) == 1 and str(page.sel) == sel, "X: slot row Open -> details of that pet")
    build(page)
    page.handleDataEvent(None, None, '{"a":"slot","i":"2","t":"%s"}' % str(page.tok))
    K.check("empty" in str(page.info), "X: an empty slot row")
    ra1.remove(sel)
    page.view = 1
    page.sel = sel
    build(page)
    K.check(int(page.view) == 0, "X: details of a pet that left -> back to the list")
    page.handleDataEvent(None, None, '{"a":"zzz","t":"%s"}' % str(page.tok))
    page.handleDataEvent(None, None, '{"a":"close"}')
    K.check(page.closes == 1, "X: Close")
    state["profile"][str(u1)] = "badfile"
    os.makedirs(os.path.join(root, "pets", "badfile.properties"))
    pb = TP(pa)
    b_, e_ = build(pb)
    K.check(len(pb.ids) == 0 and len(e_.getEvents()) == 3, "X: a bad file: an empty list (prev / next / close only)")
    state["profile"].clear()
    CfgFn.cmdSetConsole("pets.enabled", "false")
    build(TP(pa))
    CfgFn.cmdSetConsole("pets.enabled", "true")
    K.check(str(Page.jsonStr('{"a":"x\\"y"}', "a")) == 'x"y' and int(Page.toInt("x")) == -1 and str(Page.jsonStr(None, "a")) == "" and str(Page.rcol(9)) == str(Page.rcol(1)),
            "X: jsonStr / toInt / rcol")
    K.check(int(Page.BUILDS) >= 15 and int(Page.STALE) == 1, "X: page counters")
    # ---------------------------------------------------------------- commands
    pc = fakepr(u1, "Alice")
    res = str(Cmds.run(pc, JArray(JString)(["give", "Bob", "Cat"])))
    Cmds.reply(pc, res)
    Cmds.reply(pc, "=line one\nline two")
    Cmds.reply(pc, "-no")
    Cmds.reply(pc, "")
    K.check(res.startswith("+Gave Bob") and len(pc.msgs) == 4 and str(pc.msgs[0]).startswith("[Pets] Gave Bob") and str(pc.msgs[2]) == "  line two",
            "X: /petadmin run + reply lines: %s" % jall(pc.msgs))
    K.check(any("/petadmin give Bob" in str(x) for x in lines), "X: admin changes are logged")
    K.check(str(Cmds.run(None, JArray(JString)(["help"]))).startswith("=/petadmin"), "X: run without a player")
    Eng.say(None, "x", None)
    Eng.say(pc, "plain", None)
    K.check(str(pc.msgs[-1]) == "plain" and Eng.worldOf(None) is None and not Eng.open(None, None, None), "X: say / worldOf / open guards")
    K.check(not any(str(x).startswith("WARN") and "failed" in str(x) for x in lines), "X: no 'failed' warning in the log: %s" % [str(x) for x in lines if str(x).startswith("WARN")][:5])
    K.notes.append("X log tail: " + " | ".join(str(x) for x in list(lines)[-6:]))
    P("CfgPub").shutdown()


# ====================================================================================================== E: the ECS system
def run_ecs(out):
    from jpype import JClass, JInt
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    U, jf, uni = boot_bare(os.path.join(SCRATCH, "e-universe"))
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]

    def newct():
        v = U.allocateInstance(CT.class_)
        n_[0] += 1
        jf(CT, "index").set(v, JInt(n_[0]))
        return v

    def fill(cls, inst):
        for f in cls.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()):
                continue
            if f.getType() == CT.class_:
                f.setAccessible(True)
                f.set(inst, newct())
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    fill(EM, em)
    jf(EM, "instance").set(None, em)
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esm_ = U.allocateInstance(ESMOD.class_)
    fill(ESMOD, esm_)
    jf(ESMOD, "instance").set(None, esm_)
    jf(JClass("com.hypixel.hytale.server.core.universe.Universe"), "playerRefComponentType").set(uni, newct())
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    for c in (PLA, PRc, ESM):
        K.check(c.getComponentType() is not None, "E: %s.getComponentType resolves" % c.class_.getSimpleName())
    P = lambda n: JClass(PKG + n)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    mods = os.path.join(SCRATCH, "e-mods")
    os.makedirs(mods, exist_ok=True)
    P("PetsCfg").load(Paths.get(mods))
    P("PetStore").ROOT = Paths.get(mods, "Skyy_SkyyPets")
    P("PetStore").DIR = Paths.get(mods, "Skyy_SkyyPets", "pets")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    MS, MB, MC, FP, FSM = (JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".MapBuffer"), JClass(FAKE_PKG + ".MapChunk"), JClass(FAKE_PKG + ".FakePr"),
                           JClass(FAKE_PKG + ".FakeStatMap"))
    Ref = JClass("com.hypixel.hytale.component.Ref")
    st = U.allocateInstance(MS.class_)
    st.comps = JClass("java.util.HashMap")()
    W = JClass("com.hypixel.hytale.server.core.universe.world.World")
    w = U.allocateInstance(W.class_)
    jf(W, "name").set(w, "default")
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    es = U.allocateInstance(ES.class_)
    for f in ES.class_.getDeclaredFields():
        if f.getType() == W.class_:
            f.setAccessible(True)
            f.set(es, w)
    st.ext = es
    K.check(str(P("PetsEng").worldOf(st)) == "default", "E: the REAL PetsEng.worldOf reads the store's world")
    u = UUID.fromString("44444444-4444-4444-8444-444444444444")
    pr = U.allocateInstance(FP.class_)
    pr.fu = u
    pr.fname = "Dee"
    pl = U.allocateInstance(PLA.class_)
    rp = Ref(st, 7)
    sm = FSM(3)
    st.putComponent(rp, PLA.getComponentType(), pl)
    st.putComponent(rp, PRc.getComponentType(), pr)
    st.putComponent(rp, ESM.getComponentType(), sm)
    ch = U.allocateInstance(MC.class_)
    ch.ref = rp
    cb = U.allocateInstance(MB.class_)
    cb.st = st
    sys_ = P("PetTickSys")()
    K.check(sys_.getQuery() is not None, "E: PetTickSys query = Player")
    AR = JClass("java.util.concurrent.atomic.AtomicReference")
    jf(PLA, "waitingForClientReady").set(pl, AR("waiting"))
    waiting = bool(pl.isWaitingForClientReady())
    sys_.tick(1.0, 0, ch, st, cb)
    K.check(waiting and int(P("PetTick").SECONDS.get()) == 0, "E: a player still waiting for the client is skipped")
    jf(PLA, "waitingForClientReady").set(pl, AR())
    K.check(not bool(pl.isWaitingForClientReady()), "E: ready player")
    s0 = int(P("PetTick").SECONDS.get())
    sys_.tick(1.0, 0, ch, st, cb)
    sys_.tick(0.3, 0, ch, st, cb)
    K.check(int(P("PetTick").SECONDS.get()) == s0 + 1, "E: tick runs the second once per second")
    rec = P("PetStore").get(str(u))
    K.check(rec.count() == 1 and str(rec.kindOf(rec.active(1))) == "Rabbit", "E: the real tick gave the starter")
    hp = P("PetOps").create(rec, None, "Boar", 5, 100, 0, "test", "t", True)
    rec.set("active.1", hp)
    sys_.tick(1.0, 0, ch, st, cb)
    K.check(abs(float(sm.vals[0].mx) - 160.0) < 1e-3 and sm.vals[0].mods.get("skyypet_health") is not None, "E: the stat map from the CommandBuffer gets skyypet_health +60")
    ch.boom = True
    sys_.tick(1.0, 0, ch, st, cb)
    K.check(bool(P("PetTickSys").FAILED_ONCE), "E: a broken chunk is logged once")
    K.save()


# ====================================================================================================== R: restarts
def run_restart(step, out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    boot_bare(os.path.join(SCRATCH, "r-universe"))
    P = lambda n: JClass(PKG + n)
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    mods = os.path.join(SCRATCH, "r-mods")
    os.makedirs(mods, exist_ok=True)
    state = {"online": [], "names": {}, "tells": [], "totals": {}, "xpcalls": 0, "profile": {}}
    br, xpfn, keyfn = bridge_setup(state)
    br.put("profile:fn:key", keyfn)
    P("PetsEng").API = make_api(state)
    Cfg, Store, Ops, Tick = P("PetsCfg"), P("PetStore"), P("PetOps"), P("PetTick")
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    sc = list(Store.scanAll())
    u = UUID.fromString("66666666-6666-4666-8666-666666666666")
    state["online"], state["names"][str(u)] = [str(u)], "Eve"
    pdir = os.path.join(mods, "Skyy_SkyyPets", "pets")
    if step == "R1":
        K.check(sc == [0, 0, 0, 0], "R1: fresh start, nothing on disk: %s" % sc)
        Tick.second(u, "default", None)
        r = Store.get(str(u))
        g = str(Ops.admin("Adm", "give", "Eve", "Wolf", "Epic", "10"))
        Ops.admin("Adm", "unlock", "Eve", None, None, None)
        wid = g.split("(id ")[1].split(")")[0]
        Ops.toSlot(u, wid, 2, "Eve")
        P("PetXp").give(u, "Combat", 4000)
        state["profile"][str(u)] = str(u) + "-p2"
        Tick.second(u, "default", None)
        Store.flushDirty()
        json.dump({"wid": wid, "lvl": int(r.levelOf(wid)), "xp": int(r.xpOf(wid)), "seq": int(r.lv("seq", 0))}, open(os.path.join(SCRATCH, "r1.json"), "w"))
        K.check(int(r.levelOf(wid)) > 10, "R1: XP raised the Wolf above Lv 10")
    elif step == "R2":
        d = json.load(open(os.path.join(SCRATCH, "r1.json")))
        K.check(sc == [2, 3, 0, 0], "R2: 2 files (profile 1 + 2), 3 pets read back: %s" % sc)
        r = Store.get(str(u))
        K.check(int(r.levelOf(d["wid"])) == d["lvl"] and int(r.xpOf(d["wid"])) == d["xp"] and str(r.active(2)) == d["wid"] and r.unlocked()
                and int(r.lv("seq", 0)) >= d["seq"], "R2: level, XP, summon slot, unlock and seq survived the restart")
        with open(os.path.join(pdir, "zzdup.properties"), "w", encoding="latin-1") as f_:
            f_.write("seq=1\nv=1\npet.%s.kind=Wolf\n" % d["wid"])
        sc2 = list(Store.scanAll())
        K.check(sc2[3] == 1 and str(Store.INDEX.get(d["wid"])) == str(u), "R2: a planted duplicate is quarantined (the real owner keeps it): %s" % sc2)
        sc3 = list(Store.scanAll())
        K.check(sc3[3] == 0, "R2: the next scan finds no duplicate")
    elif step == "R3":
        with open(os.path.join(pdir, "broken.properties"), "w", encoding="latin-1") as f_:
            f_.write("v=1\npet.q.kind=\\u12\n")
        hb = hashlib.sha256(open(os.path.join(pdir, "broken.properties"), "rb").read()).hexdigest()
        sc = list(Store.scanAll())
        K.check(sc[2] == 1 and Store.BAD.containsKey("broken") and sc[1] == 3, "R3: the corrupt file is reported, the others still read: %s" % sc)
        state["profile"][str(u)] = "broken"
        Tick.second(u, "default", None)
        K.check(hashlib.sha256(open(os.path.join(pdir, "broken.properties"), "rb").read()).hexdigest() == hb and Store.get("broken").count() == 0,
                "R3: the corrupt profile gets nothing (no starter) and its file is never written")
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(step, out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    home = os.path.join(SCRATCH, "live")
    P = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    # setup()'s order: config load, the store + startup scan, the kit
    P("PetsCfg").load(Paths.get(home))
    P("PetStore").ROOT = Paths.get(home).resolve("Skyy_SkyyPets")
    P("PetStore").DIR = P("PetStore").ROOT.resolve("pets")
    sc = list(P("PetStore").scanAll())
    P("CfgPub").start(Paths.get(home), HL.get("SkyyPetsLive"))
    K.check(len(P("PetsCfg").KINDS) == 30 and sc == [0, 0, 0, 0], "D %s: config read (30 kinds), no pet files yet: %s" % (step, sc))
    P("CfgPub").shutdown()
    P("PetStore").flushDirty()
    K.save()


# ====================================================================================================== P / B / AA
def run_perm(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("PetAdminCmd", "PetAdminArg1Cmd", "PetAdminArg2Cmd", "PetAdminArg3Cmd", "PetAdminArg4Cmd", "PetAdminArg5Cmd"):
        c = JClass(PKG + cn)()
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty" % cn)
        if cn == "PetAdminCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak and str(c.getName()) == "petadmin", "P. /petadmin gives %s to no group (leak %s)" % (NODE, leak))
    m = JClass(PKG + "PetsCmd")()
    K.check(list(fld.get(m)) == ["hytale:Adventurer"] and str(m.getName()) == "pets" and "pet" in [str(a) for a in m.getAliases()] and m.getPermission() is None
            or (list(fld.get(m)) == ["hytale:Adventurer"] and str(m.getName()) == "pets" and "pet" in [str(a) for a in m.getAliases()] and NODE not in str(m.getPermission())),
            "P. /pets (alias /pet) = hytale:Adventurer")
    K.save()


def bytecode_calls(cp, cls, meth, sig=None):
    from jpype import JClass
    cc = cp.get(cls)
    ms = [m for m in cc.getClassFile2().getMethods() if str(m.getName()) == meth and (sig is None or sig in str(m.getDescriptor()))]
    calls = []
    for mi in ms:
        cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
        while it.hasNext():
            p = it.next()
            op = it.byteAt(p)
            if op in (0xb6, 0xb7, 0xb8, 0xb9):
                i = it.u16bitAt(p + 1)
                if cpool.getTag(i) == JClass("javassist.bytecode.ConstPool").CONST_InterfaceMethodref:
                    calls.append(str(cpool.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getInterfaceMethodrefName(i)) + str(cpool.getInterfaceMethodrefType(i)))
                else:
                    calls.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)) + str(cpool.getMethodrefType(i)))
            elif op == 0xbb:
                calls.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
            elif op in (0x12, 0x13):
                i = it.byteAt(p + 1) if op == 0x12 else it.u16bitAt(p + 1)
                if cpool.getTag(i) == JClass("javassist.bytecode.ConstPool").CONST_String:
                    calls.append("ldc " + str(cpool.getStringInfo(i)))
            elif op in (0xb2, 0xb3):
                i = it.u16bitAt(p + 1)
                calls.append("field " + str(cpool.getFieldrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getFieldrefName(i)))
    return calls


def run_bytecode(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    full = lambda cls, m, sig=None: bytecode_calls(cp, cls, m, sig)
    calls = [c.split("(")[0] for c in full(PKG + "SkyyPetsPlugin", "setup")]
    want = ["PetsCfg.load", "PetStore.scanAll", "CfgPub.start", "ldc pets:fn:onxp", "new PetXpFn", "new PetsCmd", "CommandRegistry.registerCommand",
            "new PetAdminCmd", "CommandRegistry.registerCommand", "new PetTickSys", "ComponentRegistryProxy.registerSystem", "new PetQuit",
            "EventRegistry.registerGlobal", "new PetTimer", "ScheduledExecutorService.scheduleWithFixedDelay"]
    pos, ok = 0, True
    for x in want:
        try:
            pos = calls.index(x, pos) + 1
        except ValueError:
            ok = False
            break
    K.check(ok and calls.count("ComponentRegistryProxy.registerSystem") == 1, "B: setup() = config, scan, kit, onxp fn, 2 commands, ONE system, disconnect, timer: %s" % calls)
    tk = full(PKG + "PetTickSys", "tick")
    K.check(not any("openCustomPage" in c for c in tk) and any(c.startswith("CommandBuffer.getComponent") for c in tk), "B: the tick reads the stat map from the CommandBuffer, never opens a page")
    md = full(PKG + "PetBuff", "mod")
    K.check("field Modifier$ModifierTarget.MAX" in md and "field StaticModifier$CalculationType.ADDITIVE" in md and any(c.startswith("EntityStatMap.putModifier") for c in md),
            "B: stat modifiers are StaticModifier(MAX, ADDITIVE) (never MULTIPLICATIVE)")
    wa = full(PKG + "PetStore", "writeAtomic")
    K.check("field StandardCopyOption.ATOMIC_MOVE" in wa and any(c.startswith("FileDescriptor.sync") for c in wa), "B: writes = fsync + atomic move")
    sd = [c.split("(")[0] for c in full(PKG + "SkyyPetsPlugin", "shutdown")]
    K.check("PetStore.flushDirty" in sd and "CfgPub.shutdown" in sd, "B: shutdown flushes the pets + the kit")
    K.check("PetBuff.clearAll" in sd and any(c_.endswith(".remove") for c_ in sd), "FIX2-B1: shutdown clears the bridge entries + removes pets:fn:onxp: %s" % sd)
    K.save()


def run_audit(out):
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR, FAKE_DIR):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass(FAKE_PKG + ".LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)
    cs_ = set()

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
    json.dump(res, open(out, "w"), indent=1)


# ====================================================================================================== parent driver
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--live", LIVE], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake(arg("--mkfake"))), ("--core", lambda: run_core(arg("--out"))),
                     ("--ecs", lambda: run_ecs(arg("--out"))), ("--restart", lambda: run_restart(arg("--restart"), arg("--out"))),
                     ("--live-step", lambda: run_live(arg("--live-step"), arg("--out"))), ("--perm", lambda: run_perm(arg("--out"))),
                     ("--bytecode", lambda: run_bytecode(arg("--out"))), ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            fn()
            return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        part_static()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0 and os.path.isfile(os.path.join(FAKE_DIR, FAKE_PKG, "MapStore.class")), "F: the stand-ins were generated")
        for label, flag in (("core", "--core"), ("ecs", "--ecs"), ("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            child(env, flag, "--out", out)
            take(out, label)
        for step in ("R1", "R2", "R3"):
            out = os.path.join(SCRATCH, "restart-%s.json" % step)
            child(env, "--restart", step, "--out", out)
            take(out, "restart " + step)
        home = os.path.join(SCRATCH, "live")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        h0 = tree_hash(home)
        check(len(h0) > 0 and not os.path.exists(os.path.join(home, "Skyy_SkyyPets")), "D: live mod data copied (%d files), no pets folder yet" % len(h0))
        out = os.path.join(SCRATCH, "live-1.json")
        child(env, "--live-step", "start1", "--out", out)
        take(out, "live start1")
        h1 = tree_hash(home)
        new = sorted(set(h1) - set(h0))
        changed = sorted(k for k in h0 if h1.get(k) != h0[k])
        check(new == [os.path.join("Skyy_SkyyPets", "config.properties")] and not changed,
              "D: start 1 writes only Skyy_SkyyPets/config.properties, every other file byte-identical (new %s changed %s)" % (new, changed))
        out = os.path.join(SCRATCH, "live-2.json")
        child(env, "--live-step", "start2", "--out", out)
        take(out, "live start2")
        h2 = tree_hash(home)
        check(h2 == h1, "D: start 2 changes nothing (%s)" % sorted(k for k in set(h1) | set(h2) if h1.get(k) != h2.get(k)))
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 400 and a["classes"] == len(CLASSES),
                  "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: control refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused; caller-sensitive: %s"
                  % (a["refs"], a["classes"], len(a["refused"]), a["caller_sensitive"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
