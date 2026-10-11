"""Harness for SkyyPetProbe 0.1. Build first: python SkyyPetProbe/build_skyypetprobe_0.1.py

    python SkyyPetProbe/test_skyypetprobe_0.1.py [--jar <SkyyPetProbe-0.1.jar>] [--live <a world mods folder>] [--keep]

Parent (plain Python, Assets.zip + the jar read-only):
  J  the jar: manifest (Main, IncludesAssetPack false, Version, Name), exactly the 25 expected classes, NO other file (no asset of any
     kind: nothing for the engine's asset validators to refuse), no class package shared with an installed mod (read-only scan)
  K  every vanilla role / model the probe names is in Assets.zip; Test_Pet = Invulnerable + Teleport + Corgi; Risen_Knight =
     Template_Summoned_Ally (JoinFlock, DespawnTimer 300); Tamed_Horse IsMountable + anchor 1.6; Empty_Role has no instructions; the
     'Mount' movement config exists
Children (fresh JVMs: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  the stand-ins generated with javassist (MapStore, MapBuffer, MapChunk, FakeWorld, FakePr, FakeHolder, FakeStatMap, FakeStatValue,
     LookupIn, BadAccess)
  A  every class loads and verifies (-Xverify:all)
  E  ENGINE ASSETS the probe uses at run time go through the engine's own codecs: the vanilla ModelAsset JSON of every model the probe
     spawns (parents first) decodes with no validation failure and loads; the REAL Model.createScaledModel keeps the id + scale and
     scales the hitbox (Fox x0.8 = 0.72 x 0.88 x 0.72)
  X  EVERY NEW CODE PATH EXECUTED on stand-ins (PpEng.API = a Python stand-in for the NPC plugin; everything else real): PpLogic on plain
     data; PpFile append / load (no file = nothing written; SPAWN at= / WHERE / GONE / START; fix round: NO ghost expires by run count),
     addGhost / removeGhost; the ghost sweep (5 s at the spot: found = removed, not there = confirmed gone; list / clear show the ghost
     list and 'do NOT remove the mod yet'); P7 credit only on the P7 pig + reset on clear / stop; p7 again removes the last run; the P6
     ATTACK line; P10 x0.5 / Camel / Ram with per-role anchors; a code mount that never takes resets movement (3 s / clear); PpLog; PpPre on a holder (Invulnerable ensured, the REAL EntityStore.REGISTRY NonSerialized type added); PpSpawn (success
     + every refusal: cap, role, model, scaled model, spawn throws / null / invalid ref, no UUID); every /petprobe action through
     PpCmds.run (help, list, clear, nosave, all, p1 / air / water, p2, p3 / own, p4, p5 spawn + every report branch, p6, p7 / credit, p8,
     p9, p10 / big / ride, bad options, unreadable position); PpTick.run second by second (spawn checks, P8 bridge answers, P2 6 s, P1 20 s,
     P3 10-60 s + vanilla-teleport detection + our fallback teleport + own steering, P4 steps A-D with read-back, P6 flock same / other,
     P10 riding on / off); PpLife (owner died once, profile epoch change, world change -> queued on the old world); PpDmgFilter (P9 lethal
     -> cancelled + removed, non-lethal, credit rewrite, cancelled events, non-entity source); PpDmgInspect (hits on pets, pet hits, kill
     with / without credit); PpLoadSys (ghost removed on load, saved / NonSerialized, pet reloaded, unload, removed by the game);
     PpQuit (accept with a REAL PlayerDisconnectEvent); PpRemove (now / queue / run / viaBuffer / unride); PpMount (mountInfo, watch,
     ride + every refusal); the 3 commands' execute() through reflection with a real CommandContext; plugin census / start / shutdown
  P  /petprobe and its 2 usage variants: node skyypetprobe.admin, empty permission groups, getPermissionGroupsRecursive() gives the
     node to no group; alias /pprobe
  B  BYTECODE: setup()'s calls in order (load, registerCommand, registerSystem once each for the 4 systems, registerGlobal
     PlayerDisconnectEvent); every real engine line in PpEng / PpPre / PpFollow has the SAME call descriptor as the vanilla code it copies
     (NPCPlugin.spawnEntity 7-arg, ActionMount requestRoleChange + the Mount movement calls, MountPlugin.checkDismountNpc, BodyMotionTeleport
     Teleport.createExact, EntitySpawnPage NonSerialized, RoleBuilderSystem ensureComponent(Invulnerable) + createScaledModel, NPCEntity
     .setAppearance, FlockPlugin.getFlockReference); engine facts: spawnEntity calls the PRE consumer before Store.addEntity;
     NPCMountSystems$OnAdd reads getOwnerPlayerRef and sends MountNPC; the damage groups
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the live world mods folder (read-only, copied): start 1 and start 2 load with no probe
     folder -> 0 ghosts, NOTHING written (every file byte-identical, no new file); start 3 writes SPAWN lines (one NonSerialized, one
     saved); start 4 loads both as ghosts (+ a START line); start 5 keeps BOTH (no expiry by run count) with their spots;
     every other mod folder byte-identical
  AA the ENGINE-ACCESS AUDIT: every class / field / method / constructor reference in the jar looked up with MethodHandles.privateLookupIn
     the referencing class (the JVM's own access rules) - 0 refused; the control refused
Not testable without the game (UNVERIFIED in the build report): what the client draws (scale, legs, nameplates, hitbox feel), whether
Test_Pet / Risen_Knight / Tamed_Horse keep the passed Model in a live world, the real flock join, real NPC teleports, a real mount from
code, chunk save / unload of NonSerialized NPCs, SkyyMobs' real answer, the real damage pipeline order.
Scratch: tools/dev/scratch/petprobe/test (deleted at the end unless --keep). Exit code 1 on any failure.
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


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyPetProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "petprobe", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyypettest"
PKG = "com.skyy.petprobe."
CLASSES = sorted(PKG + c for c in ["PpFile", "PpLog", "PpLogic", "PpPet", "PpReg", "PpEngApi", "PpEng", "PpPre", "PpCheck", "PpSpawn",
                                   "PpRemove", "PpFollow", "PpMount", "PpProbe", "PpLife", "PpTick", "PpDmgFilter", "PpDmgInspect",
                                   "PpLoadSys", "PpQuit", "PpCmds", "PetProbeArgCmd", "PetProbeArg2Cmd", "PetProbeCmd", "SkyyPetProbePlugin"])
NODE = "skyypetprobe.admin"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
ROLES_USED = ["Bat", "Bluegill", "Empty_Role", "Fox", "Jellyfish_Blue", "Owl_Brown", "Pig", "Risen_Knight", "Tamed_Camel", "Tamed_Horse",
              "Tamed_Ram", "Test_Pet"]
MODELS_USED = ["Bat", "Bison", "Bluegill", "Camel", "Corgi", "Eye_Void", "Fox", "Horse", "Jellyfish_Blue", "Owl_Brown", "Pig", "Ram",
               "Rex_Cave", "Skeleton_Fighter", "Whale_Humpback", "Wolf_Black"]
MOUNT_Y = {"Tamed_Horse": 1.6, "Tamed_Camel": 2.25, "Tamed_Ram": 1.3}
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
    check(man.get("Main") == PKG + "SkyyPetProbePlugin" and man.get("IncludesAssetPack") is False and man.get("Version") == VERSION
          and man.get("Name") == "%s SkyyPetProbe" % VERSION, "J: manifest Main / IncludesAssetPack false / Version / Name: %r" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(cls == CLASSES, "J: exactly the %d expected classes: extra %s missing %s" % (len(CLASSES), sorted(set(cls) - set(CLASSES)), sorted(set(CLASSES) - set(cls))))
    other = [n for n in names if not n.endswith(".class") and n != "manifest.json" and not n.endswith("/")]
    check(not other, "J: no asset / lang / .ui / other file ships (nothing for the asset validators): %s" % other)
    clash = []
    if os.path.isdir(B.MODS_DIR):
        for f in os.listdir(B.MODS_DIR):
            p = os.path.join(B.MODS_DIR, f)
            if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyPetProbe"):
                continue
            try:
                with zipfile.ZipFile(p) as mz:
                    if any(n.startswith("com/skyy/petprobe/") for n in mz.namelist()):
                        clash.append(f)
            except Exception:
                pass
    check(not clash, "J: no installed mod ships com.skyy.petprobe classes: %s" % clash)
    az = zipfile.ZipFile(ASSETS)
    an = az.namelist()
    roles = dict((n.rsplit("/", 1)[1][:-5], n) for n in an if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
    models = dict((n.rsplit("/", 1)[1][:-5], n) for n in an if n.startswith("Server/Models/") and n.endswith(".json"))
    check(all(r in roles for r in ROLES_USED), "K: every role in Assets.zip: missing %s" % [r for r in ROLES_USED if r not in roles])
    check(all(m in models for m in MODELS_USED), "K: every model in Assets.zip: missing %s" % [m for m in MODELS_USED if m not in models])
    j = lambda n: json.loads(az.read(n).decode("utf-8-sig"))
    tp = j(roles["Test_Pet"])
    check(tp.get("Invulnerable") is True and tp.get("Appearance") == "Corgi" and '"Teleport"' in json.dumps(tp), "K: Test_Pet = Invulnerable, Corgi, Teleport body motion")
    rk, tsa = j(roles["Risen_Knight"]), j(roles["Template_Summoned_Ally"])
    check(rk.get("Reference") == "Template_Summoned_Ally" and '"JoinFlock"' in json.dumps(tsa) and tsa["Parameters"]["DespawnTimer"]["Value"] == 300,
          "K: Risen_Knight = Template_Summoned_Ally (JoinFlock, DespawnTimer 300)")
    th = j(roles["Tamed_Horse"])["Modify"]
    check(th.get("IsMountable") is True and th.get("MountAnchorY") == 1.6, "K: Tamed_Horse IsMountable, anchor Y 1.6")
    for r_, y_ in sorted(MOUNT_Y.items()):
        md_ = j(roles[r_])["Modify"]
        check(md_.get("IsMountable") is True and float(md_.get("MountAnchorY")) == y_, "K: %s IsMountable, anchor Y %s (fix round: per-role anchor)" % (r_, y_))
    check(j(roles["Empty_Role"]).get("Instructions") == [{}], "K: Empty_Role has no instructions")
    check("Server/Entity/MovementConfig/Mount.json" in an, "K: the 'Mount' movement config")


# ====================================================================================================== children
def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


def run_mkfake(out_dir):
    """child F: the stand-ins as .class files (subclasses of engine classes, created with Unsafe.allocateInstance - no constructor runs)"""
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG

    def mk(name, sup=None, ifaces=()):
        c = cp.makeClass(P + "." + name)
        if sup:
            c.setSuperclass(cp.get(sup))
        for i in ifaces:
            c.addInterface(cp.get(i))
        return c

    def F(c, s):
        c.addField(CtField.make(s, c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(s, c))
    CR = "com.hypixel.hytale.component."
    ms = mk("MapStore", CR + "Store")
    for d in ("java.util.Map comps", "java.util.List removed", "java.lang.Object ext", "boolean boomPut"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""")
    M(ms, """public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  if (this.boomPut) throw new IllegalStateException("put boom");
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}""")
    M(ms, """public static void kill(com.hypixel.hytale.component.Ref r) {
  try {
    java.lang.reflect.Field f = Class.forName("com.hypixel.hytale.component.Ref").getDeclaredField("index");
    f.setAccessible(true);
    f.setInt(r, Integer.MIN_VALUE);
  } catch (Exception e) { throw new RuntimeException(e); }
}""")
    M(ms, """public com.hypixel.hytale.component.Holder removeEntity(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.RemoveReason why) {
  this.removed.add(r);
  this.comps.remove(r);
  kill(r);
  return null;
}""")
    M(ms, "public boolean isProcessing() { return false; }")
    M(ms, "public java.lang.Object getExternalData() { return this.ext; }")
    ms.writeFile(out_dir)
    mb = mk("MapBuffer", CR + "CommandBuffer")
    F(mb, "public %s.MapStore st;" % P)
    F(mb, "public java.util.List puts;")
    F(mb, "public java.util.List removed;")
    mb.addConstructor(CtNewConstructor.make("public MapBuffer() { super(null); }", mb))
    M(mb, "public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) { return this.st.getComponent(r, t); }")
    M(mb, """public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  this.puts.add(c);
  this.st.putComponent(r, t, c);
}""")
    M(mb, """public void removeEntity(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.RemoveReason why) {
  this.removed.add(r);
  this.st.removeEntity(r, why);
}""")
    mb.writeFile(out_dir)
    mc = mk("MapChunk", CR + "ArchetypeChunk")
    F(mc, "public com.hypixel.hytale.component.Ref ref;")
    F(mc, "public boolean boom;")
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))
    M(mc, "public com.hypixel.hytale.component.Ref getReferenceTo(int i) { if (this.boom) throw new IllegalStateException(\"boom\"); return this.ref; }")
    mc.writeFile(out_dir)
    fw = mk("FakeWorld", "com.hypixel.hytale.server.core.universe.world.World")
    F(fw, "public int ran;")
    F(fw, "public boolean boom;")
    F(fw, "public boolean hold;")
    F(fw, "public java.util.List held;")
    fw.addConstructor(CtNewConstructor.make("public FakeWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", fw))
    M(fw, """public void execute(java.lang.Runnable r) {
  if (this.boom) throw new java.util.concurrent.RejectedExecutionException("world stopping");
  this.ran = this.ran + 1;
  if (this.hold) { this.held.add(r); return; }
  r.run();
}""")
    fw.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    F(fp, "public boolean admin;")
    F(fp, "public java.util.List msgs;")
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public boolean hasPermission(java.lang.String n) { return this.admin && \"%s\".equals(n); }" % NODE)
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs != null) this.msgs.add(m); }")
    fp.writeFile(out_dir)
    fh = mk("FakeHolder", CR + "Holder")
    F(fh, "public java.util.Map m;")
    F(fh, "public java.util.List ensured;")
    fh.addConstructor(CtNewConstructor.make("public FakeHolder() { super(); }", fh))   # never run: the harness allocates it (Holder() is package-private)
    M(fh, "public void addComponent(com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) { if (this.m.containsKey(t)) throw new IllegalArgumentException(\"already has \" + t); this.m.put(t, c); }")
    M(fh, "public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) this.m.get(t); }")
    M(fh, "public void ensureComponent(com.hypixel.hytale.component.ComponentType t) { this.ensured.add(t); }")
    fh.writeFile(out_dir)
    sv = mk("FakeStatValue", "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    F(sv, "public float v;")
    M(sv, "public float get() { return this.v; }")
    sv.writeFile(out_dir)
    sm = mk("FakeStatMap", "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    F(sm, "public %s.FakeStatValue hp;" % P)
    M(sm, "public com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue get(int i) { return this.hp; }")
    sm.writeFile(out_dir)
    lk = mk("LookupIn")
    M(lk, "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
          "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}")
    lk.writeFile(out_dir)
    ba = mk("BadAccess")
    M(ba, "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
          "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}")
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


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


def engine_setup(K):
    """allocated HytaleServer / Universe, AssetRegistryLoader.init, the ModelAsset store with every model the probe spawns (vanilla JSON
    through the engine's own codec), allocated module instances with their component types / system groups"""
    from jpype import JClass, JArray, JString, JInt
    az = zipfile.ZipFile(ASSETS)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jfield(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", CHM()),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jfield(UNI, n).set(uni, v)
    jfield(UNI, "instance").set(None, uni)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AL = JClass("java.util.ArrayList")
    MDA = JClass("com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset")
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths")
    st_ = MDA.getAssetStore()
    K.check(st_ is not None, "E: the ModelAsset store is registered by AssetRegistryLoader")
    mfiles = dict((n.rsplit("/", 1)[1][:-5], n) for n in az.namelist() if n.startswith("Server/Models/") and n.endswith(".json"))
    # parents first (Skeleton_Fighter -> Skeleton -> Player, Owl_Brown -> Sparrow, Whale -> Bluegill, Jellyfish_Blue -> Jellyfish_Cyan)
    order, seen = [], set()

    def need(mid):
        if mid in seen or mid not in mfiles:
            return
        seen.add(mid)
        par = json.loads(az.read(mfiles[mid]).decode("utf-8-sig")).get("Parent")
        if par:
            need(par)
        order.append(mid)
    for m_ in MODELS_USED:
        need(m_)
    loaded = []
    for mid in order:
        txt = az.read(mfiles[mid]).decode("utf-8-sig")
        if mid == "Player":
            # the Player model's DefaultAttachments name cosmetic attachment assets the bare JVM does not hold; stripped here only
            pj = json.loads(txt)
            pj.pop("DefaultAttachments", None)
            txt = json.dumps(pj)
            K.notes.append("E: Player (the Skeleton chain's root) decoded without DefaultAttachments (needs the cosmetic attachment assets)")
        pj = json.loads(txt)
        if pj.get("Parent"):
            # the bare JVM's single decode does not inherit from Parent (the game's asset loader does): flatten the chain here
            chain, cur = [], pj
            while cur.get("Parent") and cur["Parent"] in mfiles and len(chain) < 8:
                par = json.loads(az.read(mfiles[cur["Parent"]]).decode("utf-8-sig"))
                chain.append(par)
                cur = par
            flat = {}
            for d_ in reversed(chain):
                flat.update(d_)
            flat.update(pj)
            flat.pop("Parent", None)
            flat.pop("DefaultAttachments", None)
            txt = json.dumps(flat)
        ei = AEI(Paths.get(mid + ".json"), ADT(MDA.class_, mid, None))
        try:
            o = st_.getCodec().decodeJsonAsset(RJR.fromJsonString(txt), ei)
            vr = ei.getValidationResults()
            bad = vr is not None and vr.hasFailed()
            K.check(o is not None and not bad, "E: vanilla model %s decodes through ModelAsset's codec, no validation failure" % mid)
            l_ = AL()
            l_.add(o)
            r_ = st_.loadAssets("Hytale:Hytale", l_)
            K.check(not r_.hasFailed() and MDA.getAssetMap().getAsset(mid) is not None, "E: model %s loads into the ModelAsset store" % mid)
            loaded.append(mid)
        except Exception as e:
            K.check(False, "E: model %s decode / load: %s" % (mid, str(e)[:240]))
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    RT = JClass("com.hypixel.hytale.component.ResourceType")
    SG = JClass("com.hypixel.hytale.component.SystemGroup")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]

    def newct():
        v = U.allocateInstance(CT.class_)
        n_[0] += 1
        jfield(CT, "index").set(v, JInt(n_[0]))
        return v

    def fill(cls_name, getter=None):
        cls = JClass(cls_name)
        inst = U.allocateInstance(cls.class_)
        for f in cls.class_.getDeclaredFields():
            t = f.getType()
            if MOD.isStatic(f.getModifiers()):
                if t == cls.class_:
                    f.setAccessible(True)
                    f.set(None, inst)
                continue
            v = None
            if t == CT.class_:
                v = newct()
            elif t == RT.class_:
                v = U.allocateInstance(RT.class_)
            elif t == SG.class_:
                v = U.allocateInstance(SG.class_)
            if v is not None:
                f.setAccessible(True)
                f.set(inst, v)
        return inst
    em = fill("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    for mn in ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule", "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
               "com.hypixel.hytale.server.flock.FlockPlugin", "com.hypixel.hytale.builtin.mounts.MountPlugin"):
        fill(mn)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    c2t = JClass("java.util.HashMap")()
    npc_t = newct()
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    c2t.put(NPCc.class_, npc_t)
    jfield(EM, "classToComponentType").set(em, c2t)
    jfield(UNI, "playerRefComponentType").set(uni, newct())
    types = {}
    for cn in ("server.core.modules.entity.component.TransformComponent", "server.core.modules.entity.component.HeadRotation",
               "server.core.modules.entity.component.ModelComponent", "server.core.modules.entity.component.PersistentModel",
               "server.core.modules.entity.component.EntityScaleComponent", "server.core.modules.entity.component.BoundingBox",
               "server.core.modules.entity.component.Invulnerable", "server.core.entity.UUIDComponent", "server.core.entity.nameplate.Nameplate",
               "server.core.modules.entity.component.DisplayNameComponent", "server.core.modules.entity.component.PersistentDisplayName",
               "server.core.modules.entity.tracker.NetworkId", "server.core.modules.entity.teleport.Teleport",
               "server.core.modules.entitystats.EntityStatMap", "server.core.modules.entity.damage.DeathComponent", "server.npc.entities.NPCEntity",
               "server.core.universe.PlayerRef", "server.core.entity.entities.Player", "server.flock.FlockMembership", "builtin.mounts.NPCMountComponent"):
        try:
            types[cn.rsplit(".", 1)[1]] = JClass("com.hypixel.hytale." + cn).getComponentType()
        except Exception as e:
            K.check(False, "E: %s.getComponentType() on the allocated modules: %s" % (cn, e))
    K.check(len(types) == 20 and None not in types.values() and len(set(int(t.getIndex()) for t in types.values())) == 20,
            "E: the 20 component types the probe uses resolve through the allocated modules, all distinct")
    return {"U": U, "jfield": jfield, "az": az, "em": em, "uni": uni, "types": types, "loaded": loaded}


def run_engine(out):
    """child X (+ A, E): every probe path on stand-ins"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    bad = []
    for cn in CLASSES:
        try:
            JClass("java.lang.Class").forName(cn, True, JClass("java.lang.ClassLoader").getSystemClassLoader())
        except Exception as e:
            bad.append("%s: %s" % (cn, str(e)[:160]))
    K.check(not bad, "A: every class loads and verifies under -Xverify:all: %s" % bad)
    E = engine_setup(K)
    try:
        xrun(K, E)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:600])
    K.save()


def xrun(K, E):
    from jpype import JClass, JArray, JObject, JInt, JFloat, JDouble, JLong, JString, JImplements, JOverride, JBoolean
    U, jfield, TY = E["U"], E["jfield"], E["types"]
    AL, IHM, HM, UUID = JClass("java.util.ArrayList"), JClass("java.util.IdentityHashMap"), JClass("java.util.HashMap"), JClass("java.util.UUID")
    Paths, SYS = JClass("java.nio.file.Paths"), JClass("java.lang.System")
    REF = JClass("com.hypixel.hytale.component.Ref")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HR = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    V3D = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    UUC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    MC = JClass("com.hypixel.hytale.server.core.modules.entity.component.ModelComponent")
    PMc = JClass("com.hypixel.hytale.server.core.modules.entity.component.PersistentModel")
    MDL = JClass("com.hypixel.hytale.server.core.asset.type.model.config.Model")
    MDA = JClass("com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset")
    BBX = JClass("com.hypixel.hytale.server.core.modules.entity.component.BoundingBox")
    NID = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId")
    NPL = JClass("com.hypixel.hytale.server.core.entity.nameplate.Nameplate")
    INV = JClass("com.hypixel.hytale.server.core.modules.entity.component.Invulnerable")
    ESC = JClass("com.hypixel.hytale.server.core.modules.entity.component.EntityScaleComponent")
    TEL = JClass("com.hypixel.hytale.server.core.modules.entity.teleport.Teleport")
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    MNT = JClass("com.hypixel.hytale.builtin.mounts.NPCMountComponent")
    FLM = JClass("com.hypixel.hytale.server.flock.FlockMembership")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    PAIR = JClass("it.unimi.dsi.fastutil.Pair")
    ADR, RR = JClass("com.hypixel.hytale.component.AddReason"), JClass("com.hypixel.hytale.component.RemoveReason")
    NSER = JClass("com.hypixel.hytale.component.NonSerialized")
    MS, MB, MCH = JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".MapBuffer"), JClass(FAKE_PKG + ".MapChunk")
    FW, FP, FH = JClass(FAKE_PKG + ".FakeWorld"), JClass(FAKE_PKG + ".FakePr"), JClass(FAKE_PKG + ".FakeHolder")
    FSM, FSV = JClass(FAKE_PKG + ".FakeStatMap"), JClass(FAKE_PKG + ".FakeStatValue")
    Log, Logic, Fil, Pet, Reg, Eng = (JClass(PKG + n) for n in ("PpLog", "PpLogic", "PpFile", "PpPet", "PpReg", "PpEng"))
    Pre, Chk, Spn, Rmv, Fol, Mnt = (JClass(PKG + n) for n in ("PpPre", "PpCheck", "PpSpawn", "PpRemove", "PpFollow", "PpMount"))
    Prb, Life, Tick, DF, DI, LS, Quit, Cmds = (JClass(PKG + n) for n in ("PpProbe", "PpLife", "PpTick", "PpDmgFilter", "PpDmgInspect",
                                                                         "PpLoadSys", "PpQuit", "PpCmds"))
    sink, lines = AL(), AL()
    Log.SINK, Log.LINES = sink, lines

    def said():
        r = [str(x).split("|", 1)[1] for x in sink]
        sink.clear()
        return r

    def logged():
        r = [str(x) for x in lines]
        lines.clear()
        return r

    def now():
        return int(SYS.currentTimeMillis())

    # ================= L: PpLogic on plain data
    K.check([str(Logic.f1(JDouble(v))) for v in (0.0, 1.25, -0.44, -2.06, 12.0)] == ["0.0", "1.3", "-0.4", "-2.1", "12.0"], "L: f1")
    K.check([str(Logic.f2(JDouble(v))) for v in (0.0, 0.72, -1.005, 3.1)] == ["0.0", "0.72", "-1.0", "3.10"] or
            [str(Logic.f2(JDouble(v))) for v in (0.0, 0.72, 3.1)] == ["0.00", "0.72", "3.10"], "L: f2: %s" % [str(Logic.f2(JDouble(v))) for v in (0.0, 0.72, -1.005, 3.1)])
    K.check(str(Logic.f1(JFloat(0.35))) == "0.4" or str(Logic.f1(JFloat(0.35))) == "0.3", "L: f1(float) overload")
    K.check(str(Logic.f2(JFloat(0.5))) == "0.50", "L: f2(float) overload")
    K.check(abs(float(Logic.dist(0.0, 0.0, 0.0, 3.0, 4.0, 0.0)) - 5.0) < 1e-9, "L: dist")
    K.check([int(Logic.probeNo(s)) for s in (None, "all", "ALL", "p1", "P10", "p0", "p11", "px", "q1", "p", " p3 ", "p100")]
            == [-1, 0, 0, 1, 10, -1, -1, -1, -1, -1, 3, -1], "L: probeNo")
    K.check(abs(float(Logic.yawToward(0.0, -1.0))) < 1e-6 and float(Logic.yawToward(0.0, 0.0)) == 0.0, "L: yawToward")
    s0 = list(Logic.slot(0, 3, 10.0, 20.0, 0, 1, 4.0, 2.5))
    s2 = list(Logic.slot(2, 3, 10.0, 20.0, 0, 1, 4.0, 2.5))
    s1 = list(Logic.slot(0, 1, 0.0, 0.0, 1, 0, 5.0, 2.5))
    K.check(s0 == [12.5, 24.0] and s2 == [7.5, 24.0] and s1 == [5.0, 0.0], "L: slot (row ahead, centred, sideways): %s %s %s" % (s0, s2, s1))
    K.check(list(Logic.step(0.0, 0.0, 10.0, 0.0, 0.25, 3.0)) == [0.25, 0.0] and list(Logic.step(0.0, 0.0, 3.1, 0.0, 1.0, 3.0))[0] < 0.11
            and list(Logic.step(0.0, 0.0, 2.0, 0.0, 1.0, 3.0)) == [0.0, 0.0] and list(Logic.step(1.0, 1.0, 1.0, 1.0, 1.0, 0.0)) == [1.0, 1.0],
            "L: step (max step, never past stop, nothing inside stop, zero distance)")
    K.check(float(Logic.clamp(5.0, -1.0, 1.0)) == 1.0 and float(Logic.clamp(-5.0, -1.0, 1.0)) == -1.0 and float(Logic.clamp(0.5, -1.0, 1.0)) == 0.5, "L: clamp")
    K.check(bool(Logic.followOk(48, 60)) and not bool(Logic.followOk(47, 60)) and not bool(Logic.followOk(0, 0)), "L: followOk = 80 %")
    K.check(bool(Logic.scaleIs(JFloat(0.6), JFloat(0.6000001))) and not bool(Logic.scaleIs(JFloat(0.6), JFloat(0.61))), "L: scaleIs")
    K.check(str(Logic.up("p10")) == "P10" and str(Logic.up(None)) == "?" and str(Logic.shortId("12345678-abcd")) == "12345678" and str(Logic.shortId("ab")) == "ab"
            and str(Logic.shortId(None)) == "?", "L: up / shortId")

    # ================= PF: the probe log
    pdir = os.path.join(SCRATCH, "plog", "Skyy_SkyyPetProbe")
    Fil.DIR = None
    K.check(not bool(Fil.append("x")) and int(Fil.load()) == 0 and Fil.file() is None, "PF: no data folder -> append false, load 0")
    Fil.DIR = Paths.get(pdir)
    K.check(int(Fil.load()) == 0 and not os.path.exists(pdir), "PF: no probe.log -> load 0 and NOTHING written (no folder created)")
    K.check(str(Fil.clean("a\nb\rc")) == "a b c" and str(Fil.clean(None)) == "", "PF: clean")
    ua, ub, uc = "aaaaaaaa-0000-0000-0000-000000000001", "bbbbbbbb-0000-0000-0000-000000000002", "cccccccc-0000-0000-0000-000000000003"
    ud = "dddddddd-0000-0000-0000-00000000000d"
    for l_ in ("SPAWN %s nonser=true at=default,3.0,4.0 p5 A fox" % ua, "SPAWN %s nonser=false at=default,5.5,-2.0 p5 B corgi" % ub,
               "SPAWN %s nonser=false at=default,1.0,1.0 p1 gone one" % uc, "GONE %s /petprobe clear" % uc, "WHERE %s default,40.0,-7.5" % ub,
               "SPAWN %s nonser=true p1 old format" % ud, "RESULT P1 PASS: whatever", "junk"):
        K.check(bool(Fil.append(l_)), "PF: append %s" % l_[:12])
    txt = open(os.path.join(pdir, "probe.log"), encoding="utf-8").read().splitlines()
    K.check(len(txt) == 8 and txt[0].split(" ")[1] == "SPAWN" and "T" in txt[0].split(" ")[0], "PF: lines = <instant> <text>")
    g = int(Fil.load())
    K.check(g == 3 and Fil.GHOSTS.containsKey(ua) and Fil.GHOSTS.containsKey(ub) and Fil.GHOSTS.containsKey(ud) and not Fil.GHOSTS.containsKey(uc)
            and bool(Fil.GHOST_NONSER.get(ua)) and not bool(Fil.GHOST_NONSER.get(ub)) and str(Fil.GHOSTS.get(ua)) == "p5 A fox"
            and str(Fil.GHOSTS.get(ud)) == "p1 old format",
            "PF: load: SPAWN without GONE = ghosts (A NonSerialized, B saved, an old-format line), the GONE one is not: %s" % dict(Fil.GHOSTS))
    K.check(str(Fil.GHOST_AT.get(ua)) == "default,3.0,4.0" and str(Fil.GHOST_AT.get(ub)) == "default,40.0,-7.5" and Fil.GHOST_AT.get(ud) is None,
            "PF: load: the spot = the SPAWN at=, moved by a later WHERE line; an old-format line has none: %s" % dict(Fil.GHOST_AT))
    g2 = int(Fil.load())
    g3 = int(Fil.load())
    txt = open(os.path.join(pdir, "probe.log"), encoding="utf-8").read()
    K.check(g2 == 3 and g3 == 3 and Fil.GHOSTS.containsKey(ua) and "expired" not in txt and txt.count("START") == 3,
            "PF FIX critic-1: a NonSerialized ghost NEVER expires by run count (3 starts, still listed, no GONE line)")
    K.check(str(Fil.at("my world,x", 1.26, -3.04)) == "my_world_x,1.3,-3.0" and str(Fil.wname(None)) == "?", "PF: at() / wname() (spaces + commas made safe)")
    Fil.removeGhost(ua)
    Fil.removeGhost(None)
    K.check(not Fil.GHOSTS.containsKey(ua) and Fil.GHOST_AT.get(ua) is None and Fil.GHOST_NONSER.get(ua) is None, "PF: removeGhost clears every map")
    Fil.addGhost("eeeeeeee-0000-0000-0000-00000000000e", "p1 x", True, "default,9.0,9.0")
    Fil.addGhost(None, "x", True, None)
    K.check(str(Fil.GHOST_AT.get("eeeeeeee-0000-0000-0000-00000000000e")) == "default,9.0,9.0"
            and "WHERE eeeeeeee-0000-0000-0000-00000000000e default,9.0,9.0" in open(os.path.join(pdir, "probe.log"), encoding="utf-8").read(),
            "PF: addGhost lists it + writes its WHERE line")
    Fil.clearGhosts()
    K.check(Fil.GHOSTS.isEmpty() and Fil.GHOST_AT.isEmpty() and Fil.GHOST_NONSER.isEmpty() and Fil.GHOST_NEAR.isEmpty(), "PF: clearGhosts")

    # ================= LG: PpLog
    Log.info("hello")
    Log.warn("careful")
    Log.warnOnce("k1", "once")
    Log.warnOnce("k1", "once")
    lg_ = logged()
    K.check(lg_ == ["INFO hello", "WARN careful", "WARN once (logged once)"], "LG: info / warn / warnOnce: %s" % lg_)
    r_ = str(Log.result(None, "P1", 1, "ok"))
    K.check(r_ == "P1 PASS: ok" and said() == ["P1 PASS: ok"] and "RESULT P1 PASS: ok" in open(os.path.join(pdir, "probe.log"), encoding="utf-8").read(),
            "LG: result with no player -> log + probe.log")
    logged()

    # ================= the world + stand-ins
    st = U.allocateInstance(MS.class_)
    st.comps, st.removed = HM(), AL()
    cb = U.allocateInstance(MB.class_)
    cb.st, cb.puts, cb.removed = st, AL(), AL()
    w = U.allocateInstance(FW.class_)
    jfield(WLD, "name").set(w, "default")
    w.held = AL()
    es = U.allocateInstance(EST.class_)
    jfield(EST, "world").set(es, w)
    st.ext = es
    w2 = U.allocateInstance(FW.class_)
    jfield(WLD, "name").set(w2, "skywynn_z1")
    w2.held = AL()
    nref = [0]

    def mkref():
        nref[0] += 1
        r_ = REF(st, JInt(nref[0]))
        st.comps.put(r_, IHM())
        return r_

    def put(r_, t, c):
        st.comps.get(r_).put(t, c)

    def comp(r_, t):
        m_ = st.comps.get(r_)
        return None if m_ is None else m_.get(t)
    import math

    def mkplayer(name, n, x, y, z, fx=0, fz=1):
        r_ = mkref()
        pr_ = U.allocateInstance(FP.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-0000-0000-%012x" % (0xa000 + n)))
        jfield(PRc, "username").set(pr_, name)
        jfield(PRc, "entity").set(pr_, r_)
        pr_.admin = True
        pr_.msgs = AL()
        put(r_, PRc.getComponentType(), pr_)
        pl = U.allocateInstance(PLA.class_)
        put(r_, PLA.getComponentType(), pl)
        put(r_, TC.getComponentType(), TC(V3D(x, y, z), R3(0.0, 0.0, 0.0)))
        hr = HR()
        hr.setRotation(R3(JFloat(0.0), JFloat(math.atan2(-fx, -fz)), JFloat(0.0)))
        put(r_, HR.getComponentType(), hr)
        return {"ref": r_, "pr": pr_, "pl": pl, "uuid": pr_.getUuid()}
    A = mkplayer("Skyy", 1, 0.5, 64.0, 0.5)
    Bp = mkplayer("Friend", 2, 100.5, 64.0, 100.5)

    def setpos(r_, x, y, z):
        st.comps.get(r_).get(TC.getComponentType()).getPosition().set(JDouble(x), JDouble(y), JDouble(z))

    def newholder():
        h_ = U.allocateInstance(FH.class_)
        h_.m, h_.ensured = IHM(), AL()
        return h_

    def mount_id(pl, v):
        jfield(PLA, "mountEntityId").set(pl, JInt(v))

    # ================= PpEng.API: the NPC plugin stand-in (spawn = what NPCPlugin.spawnEntity does to a holder, then the store)
    ROLE_IX = dict((r, i + 3) for i, r in enumerate(ROLES_USED))
    mode = {"replace": None, "spawn": "ok", "flock": {}, "move": "", "roles": dict(ROLE_IX), "scaled": "ok", "nouuid": False}
    calls = {"spawn": [], "roleChange": [], "mountMove": [], "dismount": [], "appearance": [], "pre": [], "resetMove": []}
    netn = [500]

    @JImplements(PKG + "PpEngApi")
    class Api:
        @JOverride
        def roleIndex(self, role):
            return mode["roles"].get(str(role), -1)

        @JOverride
        def modelAsset(self, mid):
            return MDA.getAssetMap().getAsset(str(mid))

        @JOverride
        def scaled(self, asset, s):
            if mode["scaled"] == "boom":
                raise JClass("java.lang.IllegalStateException")("scale boom")
            if mode["scaled"] == "null":
                return None
            try:
                return MDL.createScaledModel(asset, JFloat(s))
            except Exception as e_:
                K.notes.append("API.scaled %s: %s" % (asset.getId(), str(e_)[:300]))
                raise

        @JOverride
        def spawn(self, st_, role, pos, rot, m, pre):
            calls["spawn"].append((int(role), str(m.getModelAssetId()), float(m.getScale())))
            if mode["spawn"] == "boom":
                raise JClass("java.lang.IllegalStateException")("spawn boom")
            if mode["spawn"] == "null":
                return None
            h = newholder()
            npc = U.allocateInstance(NPCc.class_)
            rn = [k for k, v in mode["roles"].items() if v == int(role)]
            jfield(NPCc, "roleName").set(npc, rn[0] if rn else "?")
            pre.accept(npc, h, st_)
            calls["pre"].append(h)
            r_ = mkref()
            if mode["spawn"] == "invalid":
                JClass(FAKE_PKG + ".MapStore").kill(r_)
                return PAIR.of(r_, npc)
            put(r_, NPCc.getComponentType(), npc)
            put(r_, TC.getComponentType(), TC(V3D(pos), R3(rot)))
            if not mode["nouuid"]:
                put(r_, UUC.getComponentType(), UUC.randomUUID())
            mm = m if mode["replace"] is None else MDL.createScaledModel(MDA.getAssetMap().getAsset(mode["replace"]), JFloat(1.0))
            put(r_, MC.getComponentType(), MC(mm))
            put(r_, BBX.getComponentType(), BBX(mm.getBoundingBox()))
            netn[0] += 1
            put(r_, NID.getComponentType(), NID(JInt(netn[0])))
            for t_ in h.ensured:
                put(r_, t_, INV.INSTANCE if t_ == INV.getComponentType() else None)
            for t_ in h.m.keySet():
                put(r_, t_, h.m.get(t_))
            return PAIR.of(r_, npc)

        @JOverride
        def refOf(self, w_, u):
            for r_ in list(st.comps.keySet()):
                c_ = comp(r_, UUC.getComponentType())
                if c_ is not None and str(c_.getUuid()) == str(u) and r_.isValid():
                    return r_
            return None

        @JOverride
        def store(self, w_):
            return None if mode.get("nostore") else st

        @JOverride
        def flockOf(self, r_, acc):
            return mode["flock"].get(int(r_.getIndex()))

        @JOverride
        def roleChange(self, r_, role, idx, acc):
            calls["roleChange"].append(int(idx))

        @JOverride
        def mountMove(self, pref, pr, acc):
            calls["mountMove"].append(str(pr.getUsername()))
            return mode["move"]

        @JOverride
        def dismount(self, acc, pref, p):
            calls["dismount"].append(int(pref.getIndex()))
            mount_id(p, 0)

        @JOverride
        def setAppearance(self, npc, r_, asset, acc):
            calls["appearance"].append(str(asset.getId()))
            acc.putComponent(r_, MC.getComponentType(), MC(MDL.createScaledModel(asset, JFloat(1.0))))

        @JOverride
        def resetMove(self, pref, acc):
            calls["resetMove"].append(int(pref.getIndex()))
            return True
    Eng.API = Api()

    # ================= E: the REAL createScaledModel on the decoded vanilla Fox
    fa = MDA.getAssetMap().getAsset("Fox")
    fm = MDL.createScaledModel(fa, JFloat(0.8))
    bb = fm.getBoundingBox()
    K.check(str(fm.getModelAssetId()) == "Fox" and abs(float(fm.getScale()) - 0.8) < 1e-6 and abs(float(bb.height()) - 0.88) < 1e-6
            and abs(float(bb.width()) - 0.72) < 1e-6, "E: Model.createScaledModel(Fox, 0.8): id + scale kept, hitbox 0.72 x 0.88 (vanilla 0.9 x 1.1)")
    K.check(str(Chk.boxText(bb)) == "0.72 x 0.88 x 0.72" and str(Chk.boxText(None)) == "none", "E: boxText on the real scaled box")
    missing_models = [m_ for m_ in MODELS_USED if MDA.getAssetMap().getAsset(m_) is None]
    K.check(not missing_models, "E: every probe model is in the harness's ModelAsset store: missing %s" % missing_models)

    # ================= PR: PpPre on a holder (REAL EntityStore.REGISTRY NonSerialized type)
    h0 = newholder()
    pc = Pre(True, True)
    pc.accept(None, h0, None)
    nst = EST.REGISTRY.getNonSerializedComponentType()
    K.check(int(pc.calls) == 1 and list(h0.ensured) == [INV.getComponentType()] and h0.m.get(nst) is NSER.get() or (h0.m.get(nst) is not None and h0.m.get(nst).getClass() == NSER.class_),
            "PR: invulnerable + NonSerialized -> ensureComponent(Invulnerable) + addComponent(REGISTRY.getNonSerializedComponentType(), NonSerialized.get())")
    h1 = newholder()
    Pre(False, False).accept(None, h1, None)
    K.check(h1.ensured.isEmpty() and h1.m.isEmpty(), "PR: neither flag -> the holder is untouched")

    # ================= bridge (SkyyMobs mob:fn:info, SkyyProfiles epoch)
    mobs = {"mode": "none"}

    @JImplements("java.util.function.Function")
    class MobFn:
        @JOverride
        def apply(self, o):
            m_ = mobs["mode"]
            if m_ == "boom":
                raise JClass("java.lang.IllegalStateException")("mobs boom")
            if m_ == "level":
                return JArray(JObject)([JInt(7), JDouble(30.0)])
            if m_ == "odd":
                return "weird"
            return None
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    SYS.getProperties().put("skyy.bridge", bridge)
    pdummy = Pet()
    pdummy.uuid, pdummy.worldName = "dddddddd-0000-0000-0000-000000000004", "default"
    K.check(str(Chk.mobInfo(pdummy)) == "SKIP", "B1: no mob:fn:info -> SKIP")
    bridge.put("mob:fn:info", MobFn())
    res = []
    for m_ in ("none", "level", "odd", "boom"):
        mobs["mode"] = m_
        res.append(str(Chk.mobInfo(pdummy)))
    K.check(res[0] == "" and res[1] == "level 7" and res[2] == "weird" and res[3].startswith("error"), "B1: mobInfo none / level / other / throws: %s" % res)
    mobs["mode"] = "none"
    K.check(Chk.bridge("nope") is None, "B1: bridge miss")
    SYS.getProperties().remove("skyy.bridge")
    K.check(Chk.bridge("mob:fn:info") is None, "B1: no bridge map -> null")
    SYS.getProperties().put("skyy.bridge", bridge)

    # ================= C: PpCheck reads
    K.check(Chk.pos(st, None) is None and Chk.worldOf(cb) is None and Chk.worldOf(st) == w, "C: pos(null), worldOf(buffer) null, worldOf(store) = the world")
    wh = list(Chk.where(st, A["ref"]))
    K.check(wh == [0.5, 64.0, 0.5, 0.0, 1.0], "C: where = feet + facing south: %s" % wh)
    rx = mkref()
    put(rx, TC.getComponentType(), TC(V3D(1.0, 2.0, 3.0), R3()))
    K.check(list(Chk.where(st, rx)) == [1.0, 2.0, 3.0, 0.0, 1.0] and Chk.where(st, mkref()) is None, "C: where with no HeadRotation -> south; no transform -> null")
    K.check(str(Chk.modelText(st, rx)) == "none" and not bool(Chk.modelIs(st, rx, "Fox", JFloat(1.0))) and str(Chk.hitbox(st, rx)) == "none"
            and float(Chk.health(st, rx)) == -1.0 and str(Chk.roleOf(st, rx)) == "?" and str(Chk.roleOf(st, A["ref"])) == "a player"
            and str(Chk.nameplate(st, rx)) == "none" and int(Chk.netId(st, rx)) == 0 and not bool(Chk.invulnerable(st, rx)),
            "C: the reads on a bare entity answer none / -1 / ? / 0")
    logged()

    # ================= S: PpSpawn - every refusal, then success
    Reg.PETS.clear()
    wh_ = Chk.where(st, A["ref"])
    mode["roles"]["Test_Pet"] = -1
    p_ = Spn.spawn(st, w, A["pr"], "p1", "x", "Test_Pet", "Fox", JFloat(0.8), "v", 1.0, 64.0, 1.0, 0.5, 0.5, True, True, 1)
    K.check(p_ is None and said() == ["P1 FAIL: x: role Test_Pet is not spawnable on this server (NPCPlugin index -1)"], "S: role not spawnable -> FAIL line")
    mode["roles"]["Test_Pet"] = ROLE_IX["Test_Pet"]
    p_ = Spn.spawn(st, w, A["pr"], "p1", "x", "Test_Pet", "NoSuchModel", JFloat(0.8), "v", 1.0, 64.0, 1.0, 0.5, 0.5, True, True, 1)
    K.check(p_ is None and said() == ["P1 FAIL: x: model NoSuchModel is not loaded"], "S: model missing -> FAIL line")
    for sm_, want in (("boom", "gave nothing"), ("null", "gave nothing")):
        mode["scaled"] = sm_
        p_ = Spn.spawn(st, w, A["pr"], "p1", "x", "Test_Pet", "Fox", JFloat(0.8), "v", 1.0, 64.0, 1.0, 0.5, 0.5, True, True, 1)
        K.check(p_ is None and want in said()[-1], "S: scaled model %s -> FAIL" % sm_)
    mode["scaled"] = "ok"
    for sp_, want in (("boom", "spawnEntity threw"), ("null", "gave no entity"), ("invalid", "gave no entity")):
        mode["spawn"] = sp_
        p_ = Spn.spawn(st, w, A["pr"], "p1", "x", "Test_Pet", "Fox", JFloat(0.8), "v", 1.0, 64.0, 1.0, 0.5, 0.5, True, True, 1)
        K.check(p_ is None and want in said()[-1], "S: spawn %s -> FAIL" % sp_)
    mode["spawn"] = "ok"
    mode["nouuid"] = True
    nrem = st.removed.size()
    p_ = Spn.spawn(st, w, A["pr"], "p1", "x", "Test_Pet", "Fox", JFloat(0.8), "v", 1.0, 64.0, 1.0, 0.5, 0.5, True, True, 1)
    K.check(p_ is None and "has no UUID - removed again" in said()[-1] and st.removed.size() == nrem + 1, "S: no UUID -> removed again + FAIL")
    mode["nouuid"] = False
    calls["spawn"] = []
    p_ = Spn.spawn(st, w, A["pr"], "p1", "Fox x0.8", "Test_Pet", "Fox", JFloat(0.8), "0.72 x 0.88 x 0.72", 3.0, 64.0, 4.0, 0.5, 0.5, True, True, 1)
    K.check(p_ is not None and Reg.PETS.get(p_.uuid) == p_ and str(p_.worldName) == "default" and p_.owner.equals(A["uuid"]) and str(p_.vbox) == "0.72 x 0.88 x 0.72"
            and int(p_.netId) > 0 and bool(p_.nonser) and bool(p_.invul) and int(p_.mode) == 1 and calls["spawn"] == [(ROLE_IX["Test_Pet"], "Fox", 0.800000011920929)],
            "S: spawn ok: tracked, owner, world, scaled box, network id, flags; NPCPlugin got role index + the scaled Fox: %s" % calls["spawn"])
    r_ = p_.ref
    K.check(str(comp(r_, NPL.getComponentType()).getText()) == "Fox x0.8" and comp(r_, INV.getComponentType()) is not None
            and comp(r_, EST.REGISTRY.getNonSerializedComponentType()) is not None, "S: nameplate + DisplayName, Invulnerable + NonSerialized through the pre-add consumer")
    lt = open(os.path.join(pdir, "probe.log"), encoding="utf-8").read()
    K.check(("SPAWN %s nonser=true at=default,3.0,4.0 p1 Fox x0.8" % p_.uuid) in lt and bool(p_.hasK) and float(p_.kx) == 3.0,
            "S: SPAWN line in the probe log (with the spawn spot at=world,x,z) + the pet's known spot")
    lg_ = logged()
    K.check(any(l.startswith("INFO SPAWN Fox x0.8: role Test_Pet (index %d)" % ROLE_IX["Test_Pet"]) and "pre-add consumer ran 1x" in l for l in lg_), "S: the SPAWN log line: %s" % lg_[-1:])
    K.check("Fox x0.8 [p1, " in str(p_.describe()) and "not saved" in str(p_.describe()), "S: describe")
    # the cap
    for i in range(int(Reg.MAX) - 1):
        Reg.PETS.put("cap-%d" % i, Pet())
    p2_ = Spn.spawn(st, w, A["pr"], "p1", "y", "Test_Pet", "Fox", JFloat(0.8), "v", 1.0, 64.0, 1.0, 0.5, 0.5, True, True, 1)
    K.check(p2_ is None and "Already 40 probe pets" in said()[-1], "S: the 40-pet cap refuses")
    for i in range(int(Reg.MAX) - 1):
        Reg.PETS.remove("cap-%d" % i)

    # ================= R: PpReg
    K.check(Reg.uuidOf(st, None) is None and Reg.petOf(st, None) is None and Reg.petOf(st, A["ref"]) is None and Reg.petOf(st, r_) == p_,
            "R: uuidOf / petOf")
    K.check(Reg.ofOwner(A["uuid"]).size() == 1 and Reg.ofOwner(None).size() == 0 and Reg.all().size() == 1, "R: ofOwner / all")
    q_ = Pet()
    q_.uuid, q_.label = "eeeeeeee-0000-0000-0000-000000000005", "q"
    Reg.PETS.put(q_.uuid, q_)
    Reg.drop(q_, "test")
    Reg.drop(q_, "again")
    K.check(bool(q_.gone) and not Reg.PETS.containsKey(q_.uuid) and ("GONE %s" % q_.uuid) not in open(os.path.join(pdir, "probe.log"), encoding="utf-8").read()
            and any("DROPPED q" in l for l in logged()), "R: drop = out of PETS, no GONE line (the ghost sweep may still find it)")
    K.check(Fil.GHOSTS.containsKey(q_.uuid) and Fil.GHOST_AT.get(q_.uuid) is None, "R FIX critic-1: drop puts it on the ghost list at once (no known spot here)")
    q3 = Pet()
    q3.uuid, q3.label, q3.tag, q3.worldName, q3.kx, q3.kz, q3.hasK, q3.nonser = "abababab-0000-0000-0000-00000000000f", "q3", "p5", "default", 12.34, -5.0, True, True
    Reg.PETS.put(q3.uuid, q3)
    Reg.drop(q3, "test")
    K.check(str(Fil.GHOSTS.get(q3.uuid)) == "p5 q3" and str(Fil.GHOST_AT.get(q3.uuid)) == "default,12.3,-5.0" and bool(Fil.GHOST_NONSER.get(q3.uuid))
            and ("WHERE %s default,12.3,-5.0" % q3.uuid) in open(os.path.join(pdir, "probe.log"), encoding="utf-8").read(),
            "R FIX critic-1: a dropped pet with a known spot -> ghost with that spot + a WHERE line for the next start")
    Fil.clearGhosts()
    logged()
    q2 = Pet()
    q2.uuid, q2.label = "ffffffff-0000-0000-0000-000000000006", "q2"
    Reg.PETS.put(q2.uuid, q2)
    Reg.forget(q2, "test forget")
    Reg.forget(None, "x")
    K.check(bool(q2.gone) and ("GONE %s test forget" % q2.uuid) in open(os.path.join(pdir, "probe.log"), encoding="utf-8").read(), "R: forget writes GONE")

    # ================= CMD: every /petprobe action
    def run(a, b=None, who=None):
        who = who or A
        Cmds.run(who["ref"], st, who["pr"], w, a, b)
        return said()
    Reg.PETS.clear()
    hl = run(None)
    K.check(len(hl) == 14 and hl[0].startswith("Pet probe (admin only)") and "0 probe pets out" in hl[-1], "CMD: /petprobe -> help (13 lines + state)")
    K.check(len(run("help")) == 14, "CMD: help")
    K.check(run("bogus")[0] == "Unknown option 'bogus'.", "CMD: unknown option -> help")
    K.check(run("nosave", "maybe")[0].startswith("Usage: /petprobe nosave on|off"), "CMD: nosave bad value")
    K.check("OFF" in run("nosave", "off")[0] and not bool(Reg.NOSAVE) and "ON" in run("nosave", "on")[0] and bool(Reg.NOSAVE), "CMD: nosave off / on")
    K.check(run("p2", "x")[0] == "/petprobe p2 takes no 'x'.", "CMD: an option where none is taken")
    K.check(run("p1", "lava")[0] == "/petprobe p1 takes no 'lava'.", "CMD: p1 bad option")
    nopos = mkref()
    put(nopos, PRc.getComponentType(), A["pr"])
    Cmds.run(nopos, st, A["pr"], w, "p1", None)
    K.check(said() == ["Your position is unreadable."], "CMD: unreadable position")
    out = run("p1")
    K.check(out[-1] == "P1: 7/7 spawned - walk around 20 s: legs skating? nameplates? hit the tiny whale / rex" and Reg.PETS.size() == 7, "CMD: p1 spawns 7: %s" % out)
    p1s = list(Reg.all())
    K.check(all(int(x.mode) == 1 and str(x.tag) == "p1" and bool(x.invul) and bool(x.nonser) for x in p1s), "CMD: p1 pets follow (mode 1), invulnerable, NonSerialized")
    K.check(sorted(str(x.model) for x in p1s) == sorted(["Skeleton_Fighter", "Fox", "Wolf_Black", "Eye_Void", "Rex_Cave", "Whale_Humpback", "Horse"]),
            "CMD: p1 models")
    out = run("p1", "air")
    K.check(out[-1].startswith("P1 air: 3/3 spawned"), "CMD: p1 air")
    out = run("p1", "water")
    K.check(out[-1].startswith("P1 water: 3/3 spawned") and Reg.PETS.size() == 13, "CMD: p1 water")
    lst = run("list")
    K.check(lst[0] == "13 probe pets (max 40):" and len(lst) == 15 and "blocks" in lst[1] and lst[-1].startswith("0 probe ghosts: nothing of the probe can sit in a saved chunk"),
            "CMD: list (+ the ghost list line: 0 ghosts = safe to remove): %s" % lst[-1:])
    # clear: this world now, a pet in another world queued, one not loaded -> dropped
    pw2 = Pet()
    pw2.uuid, pw2.label, pw2.world, pw2.worldName, pw2.owner = "11111111-0000-0000-0000-000000000007", "elsewhere", w2, "skywynn_z1", A["uuid"]
    Reg.PETS.put(pw2.uuid, pw2)
    pnl = Pet()
    pnl.uuid, pnl.label, pnl.world, pnl.owner = "22222222-0000-0000-0000-000000000008", "unloaded", w, A["uuid"]
    Reg.PETS.put(pnl.uuid, pnl)
    Reg.CREDIT = True
    out = run("clear")
    K.check(out[0] == "Cleared: 13 removed here, 1 queued in other worlds, 1 not loaded (kept on the ghost list until found or confirmed gone). P7 credit OFF."
            and Reg.PETS.isEmpty() and int(w2.ran) == 1 and not bool(Reg.CREDIT), "CMD: clear (FIX critic-2: P7 credit reset): %s" % out[:1])
    # the queued one ran on w2's thread and found nothing there (the stand-in store has no such entity) -> dropped -> a ghost too
    K.check(Fil.GHOSTS.containsKey(str(pnl.uuid)) and Fil.GHOSTS.containsKey(str(pw2.uuid)) and len(out) == 4
            and out[1].startswith("2 probe ghosts (pets that were not loaded, they may sit in a saved chunk) - do NOT remove the mod yet")
            and any("unloaded (22222222) at an unknown spot" in l for l in out[2:]), "CMD FIX critic-1: clear lists the not-loaded pets as ghosts + 'do NOT remove the mod yet': %s" % out[1:])
    Fil.clearGhosts()
    K.check(run("clear")[-1].startswith("0 probe ghosts"), "CMD: clear with no ghosts -> 'safe to remove'")
    logged()

    # ================= T: the second-by-second probe steps (PpTick.run with dt 1.0)
    def tick(who=None, dt=1.0):
        who = who or A
        Tick.run(JFloat(dt), who["ref"], st, cb)

    def age(p, ms):
        p.t0 = JLong(now() - ms)

    def P(tag):
        return [x for x in Reg.all() if str(x.tag) == tag]
    Tick.run(JFloat(1.0), None, st, cb)
    tick()
    K.check(said() == [], "T: no pets -> nothing")
    # P2: the model kept (Test_Pet / Risen / Tamed / Empty) and a role that REPLACES it
    run("p2")
    p2 = P("p2")
    K.check(len(p2) == 4, "T: p2 spawned 4")
    for x in p2:
        age(x, 1500)
    tick()
    o = said()
    fx_ = [l for l in o if "Fox on Test_Pet" in l]
    K.check(len(o) == 4 and all(l.startswith("P2 PASS: ") for l in o) and len(fx_) == 1 and "hitbox 0.72 x 0.88 x 0.72 (scaled model box 0.72 x 0.88 x 0.72)" in fx_[0]
            and "nameplate 'Fox on Test_Pet(Corgi)'" in fx_[0] and "invulnerable true" in fx_[0], "T: P2 spawn check (1 s): 4 x PASS with hitbox / nameplate: %s" % o)
    for x in p2:
        age(x, 6500)
    tick()
    o = said()
    K.check(len([l for l in o if l.startswith("P2")]) == 4 and all("KEPT" in l for l in o if l.startswith("P2")) and all(l.startswith("P8 PASS") for l in o if not l.startswith("P2")),
            "T: P2 at 6 s: KEPT x4 (the P8 check ran at 3 s too: PASS, no level): %s" % o)
    mode["replace"] = "Pig"
    run("p2")
    p2b = [x for x in P("p2") if int(x.stage) == 0]
    for x in p2b:
        age(x, 1500)
    tick()
    o = [l for l in said() if l.startswith("P2")]
    K.check(len(o) == 4 and all(l.startswith("P2 FAIL") and "model now Pig x1.0" in l for l in o), "T: a role that replaces the model -> P2 FAIL (shows what replaced it): %s" % o)
    for x in p2b:
        age(x, 6500)
    tick()
    o = [l for l in said() if "after 6 s" in l]
    K.check(len(o) == 4 and all("REPLACED" in l for l in o), "T: P2 at 6 s: REPLACED: %s" % o)
    mode["replace"] = None
    run("clear")
    # P8: SkyyMobs answers (the control + a probe pet)
    bridge.remove("mob:fn:info")
    run("p8")
    run("p6")
    for x in P("p8") + P("p6"):
        age(x, 3500)
    tick()
    o = said()
    K.check("P8 LOOK: SkyyMobs is not on this server (no mob:fn:info) - nothing to test" in o and not any(l.startswith("P8") and "P6" in l for l in o),
            "T: P8 with no SkyyMobs: the control says SKIP, other pets stay silent: %s" % o)
    bridge.put("mob:fn:info", MobFn())
    for x in P("p8") + P("p6"):
        x.mobChecked = False
    mobs["mode"] = "level"
    tick()
    o = said()
    K.check(any(l.startswith("P8 LOOK: CONTROL P8 control Fox") and "level 7" in l for l in o) and any(l.startswith("P8 FAIL: P6 Skeleton") and "level 7" in l for l in o),
            "T: P8 levelled: control LOOK, a probe pet FAIL: %s" % o)
    for x in P("p8") + P("p6"):
        x.mobChecked = False
    mobs["mode"] = "none"
    tick()
    o = said()
    K.check(any(l.startswith("P8 LOOK: CONTROL") and "NOT levelled" in l for l in o) and any(l.startswith("P8 PASS: P6 Skeleton") for l in o), "T: P8 not levelled: PASS")
    # P6 flock: 2 s not in the flock (silent), 5 s FAIL; then a joined one PASS at 2 s
    p6 = P("p6")[0]
    p6.stage = 0
    age(p6, 2500)
    tick()
    K.check(not any(l.startswith("P6") for l in said()), "T: P6 at 2 s not joined -> silent (waits for 5 s)")
    age(p6, 5500)
    tick()
    o = [l for l in said() if l.startswith("P6")]
    K.check(len(o) == 1 and o[0].startswith("P6 FAIL: P6 Skeleton (summon flock) is NOT in your flock") and "membership no FlockMembership" in o[0], "T: P6 at 5 s -> FAIL: %s" % o)
    run("p6")
    p6b = [x for x in P("p6") if int(x.stage) == 0][0]
    fl = mkref()
    mode["flock"][int(p6b.ref.getIndex())] = fl
    mode["flock"][int(A["ref"].getIndex())] = fl
    fmem = U.allocateInstance(FLM.class_)
    put(p6b.ref, FLM.getComponentType(), fmem)
    age(p6b, 2500)
    tick()
    o = [l for l in said() if l.startswith("P6 PASS:") or l.startswith("P6 FAIL:")]
    K.check(len(o) == 1 and "is in YOUR flock" in o[0] and o[0].startswith("P6 PASS"), "T: P6 joined -> PASS at 2 s: %s" % o)
    mode["flock"] = {}
    run("clear")
    # P1 follow + 20 s summary; P3 vanilla jump, our fallback teleport, 60 s verdict
    run("p3")
    p3 = P("p3")[0]
    tick()
    K.check(int(p3.secs) == 1 and int(p3.near) == 1, "T: P3 sample 1 (near)")
    setpos(p3.ref, 30.0, 64.0, 0.5)
    tick()
    setpos(p3.ref, 2.0, 64.0, 2.0)
    tick()
    o = said()
    K.check(sum(1 for l in o if "the role TELEPORTED it" in l) == 2 and int(p3.jumps) == 2, "T: P3 a 30-block move away and a 28-block move back in 1 s = 2 vanilla teleports seen: %s" % o)
    setpos(p3.ref, 40.0, 64.0, 40.0)
    tick()
    K.check(int(p3.far) == 1 and int(p3.ours) == 0 and int(p3.jumps) == 3, "T: far 1 s -> wait (the 53-block move counted as a role teleport)")
    cb.puts.clear()
    tick()
    tp_ = [c_ for c_ in cb.puts if isinstance(c_, TEL)]
    K.check(int(p3.ours) == 1 and len(tp_) == 1 and abs(float(tp_[0].getPosition().x()) - 2.0) < 1e-9, "T: far 2 s -> OUR teleport (Teleport.createExact next to you)")
    setpos(p3.ref, 41.0, 64.0, 41.0)
    tick()
    K.check(int(p3.jumps) == 3, "T: the move right after OUR teleport is not counted as a vanilla jump")
    setpos(p3.ref, 1.0, 64.0, 1.0)
    age(p3, 10500)
    tick()
    K.check(int(p3.stage) == 1 and any("P3 P3 Fox (vanilla follow)" in l for l in logged()), "T: P3 10 s summary (log)")
    for s_ in range(2, 7):
        age(p3, s_ * 10000 + 500)
        tick()
    o = said()
    K.check(int(p3.stage) == 6 and any(l.startswith("P3 FAIL: P3 Fox (vanilla follow)") and "within 8 blocks" in l for l in o), "T: P3 60 s verdict (FAIL: far too often): %s" % o[-1:])
    p3.near = p3.secs
    p3.stage = 5
    tick()
    K.check(any(l.startswith("P3 PASS") for l in said()), "T: P3 verdict PASS when within 8 blocks 80 %")
    # P3 own: our steering every tick; teleport at once when > 24
    run("p3", "own")
    po = [x for x in P("p3") if int(x.mode) == 2][0]
    setpos(po.ref, 10.5, 64.0, 0.5)
    cb.puts.clear()
    Tick.run(JFloat(0.05), A["ref"], st, cb)
    tp_ = [c_ for c_ in cb.puts if isinstance(c_, TEL)]
    K.check(len(tp_) == 1 and abs(float(tp_[0].getPosition().x()) - 10.25) < 1e-6 and int(po.steps) == 1, "T: P3 own: one 0.25-block step per 0.05 s tick toward you")
    setpos(po.ref, 2.5, 64.0, 0.5)
    cb.puts.clear()
    Tick.run(JFloat(0.05), A["ref"], st, cb)
    K.check(not any(isinstance(c_, TEL) for c_ in cb.puts), "T: P3 own: inside 3 blocks -> no step")
    setpos(po.ref, 60.0, 64.0, 0.5)
    Tick.ACC.clear()
    cb.puts.clear()
    tick()
    K.check(int(po.ours) == 1 and any(isinstance(c_, TEL) for c_ in cb.puts), "T: P3 own: > 24 blocks -> our teleport at once (mode 2)")
    K.check("our steering steps 1" in str(Fol.summary(po)), "T: summary names the steering steps")
    run("clear")
    run("p1")
    for x in P("p1"):
        x.checked = True
        x.mobChecked = True
        age(x, 20500)
    tick()
    o = [l for l in said() if l.startswith("P1 LOOK")]
    K.check(len(o) == 7 and "legs skating?" in o[0], "T: P1 20 s summary x7")
    run("clear")
    # P4: steps A-D read back
    run("p4")
    p4 = P("p4")[0]
    p4.checked = True
    p4.mobChecked = True
    calls["appearance"] = []
    for s_ in range(0, 5):
        age(p4, (s_ + 1) * 4000 + 100)
        tick()
    o = [l for l in said() if l.startswith("P4")]
    K.check(len(o) == 8 and "step A (new ModelComponent x0.8" in o[0] and o[1].startswith("P4 PASS: step A read back: Fox x0.8") and "step B" in o[2]
            and "step B read back: Fox x1.0" in o[3] and "step C (EntityScaleComponent 1.5" in o[4] and "EntityScaleComponent 1.5" in o[5]
            and "step D (setAppearance(Wolf_Black)" in o[6] and "step D read back: Wolf_Black x1.0" in o[7] and calls["appearance"] == ["Fox", "Wolf_Black"],
            "T: P4 steps A-D + read backs: %s" % o)
    K.check(comp(p4.ref, PMc.getComponentType()) is not None and int(p4.stage) == 5, "T: P4 step A also put a PersistentModel")
    run("p4")
    p4b = [x for x in P("p4") if int(x.stage) == 0][0]
    p4b.checked, p4b.mobChecked = True, True
    st.comps.get(p4b.ref).remove(NPCc.getComponentType())
    age(p4b, 4100)
    tick()
    age(p4b, 8100)
    tick()
    o = [l for l in said() if l.startswith("P4")]
    K.check(any("step B: no NPCEntity" in l for l in o), "T: P4 step B with no NPCEntity -> FAIL line")
    for s_ in (3, 4):
        p4b.stage = s_
        age(p4b, (s_ + 1) * 4000 + 100)
        tick()
    K.check(int(p4b.stage) == 5, "T: P4 steps C/D/E run with no NPCEntity without crashing")
    run("clear")
    # missing for 3 s
    run("p6")
    p6c = P("p6")[0]
    p6c.checked, p6c.mobChecked, p6c.stage = True, True, 2
    st.comps.get(p6c.ref).remove(TC.getComponentType())
    for _ in range(3):
        tick()
    o = said()
    K.check(int(p6c.missing) == 3 and any("is not loaded / not found for 3 s" in l for l in o), "T: a pet unreadable 3 s in a row -> LOOK line")
    run("clear")
    # P10: riding on / off, code ride + refusals
    out = run("p10", "ride")
    K.check(out == ["P10 ride: no probe mount within 8 blocks - /petprobe p10 first, then stand next to one"], "CMD: p10 ride with none")
    out = run("p10")
    K.check(out[-1].startswith("P10: 6/6 spawned") and all(bool(x.mount) for x in P("p10")), "CMD: p10 spawns 6 mounts: %s" % out[-1:])
    got10 = sorted((str(x.role), str(x.model), round(float(x.scale), 2), round(float(x.anchorY), 3)) for x in P("p10"))
    K.check(got10 == sorted([("Tamed_Horse", "Horse", 1.0, 1.6), ("Tamed_Horse", "Horse", 1.3, 2.08), ("Tamed_Horse", "Bison", 1.0, 1.6),
                             ("Tamed_Horse", "Horse", 0.5, 0.8), ("Tamed_Camel", "Camel", 1.0, 2.25), ("Tamed_Ram", "Ram", 1.0, 1.3)]),
            "CMD FIX critic-4.3: p10 = Horse x1.0 / x1.3 / pet-size x0.5, Bison, Camel, Ram, each with ITS role's anchor x scale: %s" % got10)
    xs10 = sorted(round(float(Chk.pos(st, x.ref)[0]), 2) for x in P("p10"))
    K.check(xs10 == [-8.25, -4.75, -1.25, 2.25, 5.75, 9.25], "CMD: p10 row is 3.5 blocks apart (mounts are wide): %s" % xs10)
    h13 = [x for x in P("p10") if abs(float(x.scale) - 1.3) < 1e-6][0]
    for x in P("p10"):
        x.checked, x.mobChecked = True, True
    mount_id(A["pl"], int(h13.netId))
    tick()
    o = said()
    K.check(any(l.startswith("P10 PASS: you RIDE P10 Horse x1.3 (bigger)") and "via F = the vanilla mount" in l and "no NPCMountComponent" in l for l in o), "T: P10 riding seen (vanilla F): %s" % o)
    mount_id(A["pl"], 0)
    tick()
    K.check(any(l.startswith("P10 LOOK: you got off P10 Horse x1.3") for l in said()), "T: P10 got off")
    setpos(h13.ref, 0.5, 64.0, 2.5)
    out = run("p10", "ride")
    K.check(len(out) == 1 and out[0].startswith("P10 LOOK: code mount sent on P10 Horse x1.3 (bigger) (2.0 blocks)") and "anchor Y 2.08" in out[0] and "role -> Empty_Role (index %d)" % ROLE_IX["Empty_Role"] in out[0]
            and "'Mount' applied" in out[0] and calls["roleChange"] == [ROLE_IX["Empty_Role"]] and calls["mountMove"] == ["Skyy"], "CMD: p10 ride (nearest = the middle x1.3 horse): %s" % out)
    h10 = [x for x in P("p10") if bool(x.codeMount)][0]
    mc_ = comp(h10.ref, MNT.getComponentType())
    K.check(mc_ is not None and mc_.getOwnerPlayerRef() == A["pr"] and abs(float(mc_.getAnchorY()) - 2.08) < 1e-5 and int(mc_.getOriginalRoleIndex()) == ROLE_IX["Tamed_Horse"],
            "CMD: p10 ride put NPCMountComponent: owner, anchor 1.6 x scale, original role index")
    K.check("NPCMountComponent owner Skyy, anchor 0.00 2.08 0.00" in str(Mnt.mountInfo(st, h10.ref)), "MT: mountInfo")
    mount_id(A["pl"], int(h10.netId))
    tick()
    K.check(any("via our code mount" in l for l in said()), "T: P10 riding via our code mount")
    mode["move"] = "no MovementManager / Player on you"
    for x in P("p10"):
        if not bool(x.codeMount):
            st.comps.get(x.ref).remove(NPCc.getComponentType())
    out = run("p10", "ride")
    K.check(out[0].startswith("P10 ride: P10 ") and "has no NPCEntity" in out[0], "CMD: p10 ride on a mount with no NPCEntity -> refused: %s" % out)
    mode["move"] = ""
    # unride: clear while riding -> dismount first
    calls["dismount"] = []
    run("clear")
    K.check(calls["dismount"] == [int(A["ref"].getIndex())] and int(A["pl"].getMountEntityId()) == 0, "CMD: clear dismounts you from a probe mount first")
    run("p10", "big")
    K.check(len(P("p10")) == 1 and abs(float(P("p10")[0].scale) - 1.3) < 1e-6, "CMD: p10 big = the x1.3 horse only")
    hb = P("p10")[0]
    put(hb.ref, MNT.getComponentType(), MNT())
    out = run("p10", "ride")
    K.check("already has an NPCMountComponent" in out[0], "CMD: p10 ride refuses a mount that already has one")
    run("clear")
    # FIX critic-3: a code mount that never takes resets your movement (after 3 s in watch, or at once on clear); the camel's own anchor
    run("p10")
    for x in P("p10"):
        x.checked, x.mobChecked = True, True
    cam = [x for x in P("p10") if str(x.role) == "Tamed_Camel"][0]
    setpos(cam.ref, 0.5, 64.0, 2.0)
    calls["resetMove"] = []
    out = run("p10", "ride")
    K.check(out[0].startswith("P10 LOOK: code mount sent on P10 Camel x1.0") and "anchor Y 2.25 (Tamed_Camel 2.25 x 1.0)" in out[0] and int(cam.moveAt) > 0
            and abs(float(comp(cam.ref, MNT.getComponentType()).getAnchorY()) - 2.25) < 1e-6, "CMD FIX critic-4.3: p10 ride on the camel uses ITS anchor 2.25: %s" % out)
    mount_id(A["pl"], 0)
    Tick.ACC.clear()
    tick()
    K.check(not any(l.startswith("P10 FAIL") for l in said()) and calls["resetMove"] == [] and int(cam.moveAt) > 0, "T FIX critic-3: within 3 s nothing is reset yet")
    cam.moveAt = JLong(now() - 3500)
    tick()
    o = [l for l in said() if l.startswith("P10")]
    K.check(len(o) == 1 and o[0].startswith("P10 FAIL: our code mount on P10 Camel x1.0 did not take within 3 s") and "movement was reset to normal (true)" in o[0]
            and calls["resetMove"] == [int(A["ref"].getIndex())] and int(cam.moveAt) == 0, "T FIX critic-3: no ride 3 s after the code mount -> movement reset + FAIL line: %s" % o)
    tick()
    K.check(calls["resetMove"] == [int(A["ref"].getIndex())], "T FIX critic-3: the reset runs once")
    ram = [x for x in P("p10") if str(x.role) == "Tamed_Ram"][0]
    setpos(ram.ref, 0.5, 64.0, 2.0)
    setpos(cam.ref, 30.0, 64.0, 30.0)
    out = run("p10", "ride")
    K.check("anchor Y 1.30 (Tamed_Ram 1.3 x 1.0)" in out[0] and int(ram.moveAt) > 0, "CMD: p10 ride on the ram: anchor 1.3")
    calls["resetMove"] = []
    run("clear")
    K.check(calls["resetMove"] == [int(A["ref"].getIndex())] and any("never took" in l for l in logged()), "CMD FIX critic-3: clear right after a code mount that never took -> movement reset")
    run("p10", "big")
    hb2 = P("p10")[0]
    setpos(hb2.ref, 0.5, 64.0, 2.0)
    mode["move"] = "no 'Mount' movement config"
    out = run("p10", "ride")
    K.check("NOT applied: no 'Mount' movement config" in out[0] and int(hb2.moveAt) == 0, "CMD: movement not applied -> nothing to reset later")
    mode["move"] = ""
    calls["resetMove"] = []
    run("clear")
    K.check(calls["resetMove"] == [], "CMD: clear with no pending code mount -> no reset")
    # P5: spawn A (NonSerialized) + B (saved), then every report branch
    out = run("p5")
    a5 = [x for x in P("p5") if bool(x.nonser)][0]
    b5 = [x for x in P("p5") if not bool(x.nonser)][0]
    K.check(out[-1].startswith("P5: 2/2 spawned - A has NonSerialized, B not") and comp(a5.ref, EST.REGISTRY.getNonSerializedComponentType()) is not None
            and comp(b5.ref, EST.REGISTRY.getNonSerializedComponentType()) is None, "CMD: p5 spawns A with and B without NonSerialized")
    out = run("p5")
    K.check(len(out) == 2 and all(l.startswith("P5 LOOK") and "chunk never unloaded" in l for l in out), "CMD: p5 report: nothing unloaded yet -> LOOK x2: %s" % out)
    # the chunk unloads: both leave memory (UNLOAD)
    for x in (a5, b5):
        LS.removed(x.ref, RR.UNLOAD, st)
        st.removeEntity(x.ref, RR.UNLOAD)
    K.check(int(a5.unloads) == 1 and int(b5.unloads) == 1 and any("UNLOAD P5 A" in l for l in logged()), "LS: UNLOAD noted")
    # B comes back from the chunk (LOAD), A does not
    rb = mkref()
    put(rb, UUC.getComponentType(), UUC(UUID.fromString(str(b5.uuid))))
    put(rb, TC.getComponentType(), TC(V3D(3.0, 64.0, 4.0), R3()))
    LS.added(rb, ADR.LOAD, st, cb)
    o = said()
    K.check(int(b5.reloads) == 1 and b5.ref == rb and any(l.startswith("P5 LOOK: P5 B Corgi (saved control) was LOADED back") for l in o), "LS: the saved control reloads (LOOK line)")
    Fil.GHOSTS.put("99999999-0000-0000-0000-000000000009", "p5 A old")
    out = run("p5")
    K.check(any(l.startswith("P5 PASS: P5 A Fox (NonSerialized) is GONE after its chunk unloaded") for l in out)
            and any(l.startswith("P5 PASS: P5 B Corgi (saved control) (no NonSerialized) was saved and LOADED back") for l in out)
            and any("1 probe pets from before the last restart" in l for l in out), "CMD: p5 report: A gone = PASS, B reloaded = PASS, ghosts pending: %s" % out)
    Fil.GHOSTS.clear()
    # A coming back would be a FAIL
    ra = mkref()
    put(ra, UUC.getComponentType(), UUC(UUID.fromString(str(a5.uuid))))
    put(ra, TC.getComponentType(), TC(V3D(3.0, 64.0, 4.0), R3()))
    LS.added(ra, ADR.LOAD, st, cb)
    said()
    out = run("p5")
    K.check(any(l.startswith("P5 FAIL: P5 A Fox (NonSerialized) came back") for l in out), "CMD: p5 report: A came back = FAIL")
    a5.reloads, a5.unloads = 0, 0
    st.removeEntity(ra, RR.REMOVE)
    a5.ref = None
    out = run("p5")
    K.check(any("is not found but no unload was seen" in l for l in out), "CMD: p5 report: A missing without an unload = LOOK")
    b5.reloads = 0
    out = run("p5")
    K.check(any(l.startswith("P5 LOOK: P5 B") and "is here, its chunk never unloaded" in l for l in out), "CMD: p5 report: B here without a reload = LOOK")
    run("clear")
    K.check(Fil.GHOSTS.containsKey(str(a5.uuid)) and bool(Fil.GHOST_NONSER.get(str(a5.uuid))), "CMD FIX critic-1: clear while the P5 A fox is not loaded -> it stays on the ghost list")
    Fil.clearGhosts()
    logged()
    # LS: ghosts after a restart (saved = PASS, NonSerialized = FAIL), SPAWN reason ignored, no uuid, removed by the game
    gu, gn = "33333333-0000-0000-0000-00000000000a", "44444444-0000-0000-0000-00000000000b"
    Fil.GHOSTS.put(gu, "p5 B corgi")
    Fil.GHOST_NONSER.put(gu, JBoolean(False))
    Fil.GHOSTS.put(gn, "p5 A fox")
    Fil.GHOST_NONSER.put(gn, JBoolean(True))
    for u_ in (gu, gn):
        rg = mkref()
        put(rg, UUC.getComponentType(), UUC(UUID.fromString(u_)))
        cb.removed.clear()
        LS.added(rg, ADR.LOAD, st, cb)
        K.check(cb.removed.size() == 1 and not rg.isValid(), "LS: ghost %s removed through the CommandBuffer when its chunk loads" % u_[:8])
    o = said()
    K.check(any(l.startswith("P5 PASS: a probe pet that was not loaded (restart / clear / logout) came back: the saved one, as expected (p5 B corgi)") for l in o)
            and any(l.startswith("P5 FAIL: a probe pet that was not loaded (restart / clear / logout) came back: a NonSerialized one (p5 A fox)") for l in o) and Fil.GHOSTS.isEmpty()
            and ("GONE %s ghost removed" % gu) in open(os.path.join(pdir, "probe.log"), encoding="utf-8").read(), "LS: ghost results + GONE lines: %s" % o)
    LS.added(mkref(), ADR.LOAD, st, cb)
    rq = mkref()
    put(rq, UUC.getComponentType(), UUC.randomUUID())
    Fil.GHOSTS.put("x", "y")
    LS.added(rq, ADR.SPAWN, st, cb)
    Fil.GHOSTS.clear()
    K.check(said() == [], "LS: no uuid / a stranger -> nothing")
    run("p6")
    p6d = P("p6")[0]
    LS.added(p6d.ref, ADR.SPAWN, st, cb)
    K.check(int(p6d.reloads) == 0, "LS: SPAWN of our own pet is not a reload")
    LS.removed(p6d.ref, RR.REMOVE, st)
    o = said()
    K.check(any("was removed BY THE GAME" in l and "Template_Summoned_Ally despawns after 300 s" in l for l in o) and bool(p6d.gone), "LS: removed by the game (Risen note) -> LOOK + GONE: %s" % o)
    LS.removed(p6d.ref, RR.REMOVE, st)
    Reg.PETS.clear()
    LS.removed(mkref(), RR.REMOVE, st)
    Fil.GHOSTS.clear()
    LS.added(mkref(), ADR.LOAD, st, cb)
    K.check(said() == [], "LS: nothing tracked -> early returns")
    lsys = LS()
    lsys.onEntityAdded(None, ADR.LOAD, st, cb)
    lsys.onEntityRemove(None, RR.REMOVE, st, cb)
    K.check(lsys.getQuery() is not None, "LS: the system wrappers + query")
    # ================= GS: the ghost sweep (FIX critic-1): a ghost leaves the list only when found or its spot was loaded without it
    Reg.PETS.clear()
    Fil.clearGhosts()
    gnear, gfar, gother, gnoat, gfound = ("5a5a5a5a-0000-0000-0000-0000000000%02x" % i for i in range(1, 6))
    Fil.addGhost(gnear, "p5 near", True, "default,3.0,4.0")
    Fil.addGhost(gfar, "p5 far", False, "default,500.0,500.0")
    Fil.addGhost(gother, "p5 other world", True, "skywynn_z1,1.0,1.0")
    Fil.addGhost(gnoat, "p1 no spot", True, None)
    Fil.addGhost(gfound, "p5 found", False, "default,-2.0,1.0")
    rfound = mkref()
    put(rfound, UUC.getComponentType(), UUC(UUID.fromString(gfound)))
    lst = run("list")
    K.check(lst[1].startswith("5 probe ghosts") and "do NOT remove the mod yet" in lst[1] and any("p5 far (5a5a5a5a) at default 500.0 500.0" in l for l in lst)
            and any("p1 no spot (5a5a5a5a) at an unknown spot" in l for l in lst), "GS: list shows every ghost with its spot + 'do NOT remove the mod yet': %s" % lst)
    Tick.ACC.clear()
    for _ in range(4):
        tick()
    K.check(Fil.GHOSTS.size() == 5 and list(Fil.GHOST_NEAR.get(gnear)) == [4] and list(Fil.GHOST_NEAR.get(gfar)) == [0] and Fil.GHOST_NEAR.get(gother) is None
            and said() == [], "GS: 4 s at the spot (no pets out, the tick still sweeps) -> still listed, counting; far / other-world ghosts not counted")
    cb.removed.clear()
    tick()
    o = said()
    lt = open(os.path.join(pdir, "probe.log"), encoding="utf-8").read()
    K.check(not Fil.GHOSTS.containsKey(gnear) and not Fil.GHOSTS.containsKey(gfound) and Fil.GHOSTS.size() == 3 and cb.removed.size() == 1
            and ("GONE %s confirmed gone" % gnear) in lt and ("GONE %s ghost found at its spot and removed" % gfound) in lt
            and any(l.startswith("Probe ghost confirmed gone") and "p5 near" in l for l in o) and any(l.startswith("Probe ghost FOUND") and "p5 found" in l for l in o)
            and o[-1] == "3 probe ghosts left (/petprobe list shows where).", "GS: 5 s at the spot -> not there = confirmed gone (GONE), there = removed (GONE): %s" % o)
    Fil.GHOST_AT.put(gfar, "default,1.0,1.0")
    tick()
    tick()
    Fil.GHOST_AT.put(gfar, "default,500.0,500.0")
    tick()
    K.check(list(Fil.GHOST_NEAR.get(gfar)) == [0] and Fil.GHOSTS.containsKey(gfar), "GS: leaving the spot resets the count")
    Fil.removeGhost(gother)
    Fil.removeGhost(gnoat)
    Fil.GHOST_AT.put(gfar, "default,1.0,1.0")
    for _ in range(5):
        tick()
    o = said()
    K.check(Fil.GHOSTS.isEmpty() and o[-1].startswith("No probe ghosts left") and "safe to remove" in o[-1], "GS: the last ghost gone -> 'safe to remove': %s" % o[-1:])
    Fil.addGhost(gnear, "p5 near", True, "garbage")
    Fil.addGhost(gfar, "p5 bad", True, "default,x,y")
    for _ in range(6):
        tick()
    K.check(Fil.GHOSTS.size() == 2 and said() == [] and int(Life.sweep(st, cb, A["pr"], None, None)) == 0, "GS: a malformed spot is skipped (stays listed); no world / position -> 0")
    Fil.clearGhosts()
    logged()
    # ================= DMG: P9 DOWN, P7 hits / credit / kills, hits on pets
    run("p9")
    p9 = P("p9")[0]
    K.check(bool(p9.down) and not bool(p9.invul) and comp(p9.ref, INV.getComponentType()) is None, "CMD: p9 = DOWN test pet, not invulnerable")
    smap = U.allocateInstance(FSM.class_)
    smap.hp = U.allocateInstance(FSV.class_)
    smap.hp.v = JFloat(20.0)
    put(p9.ref, TY["EntityStatMap"], smap)
    atk = mkref()
    put(atk, TC.getComponentType(), TC(V3D(0.0, 64.0, 0.0), R3()))

    def dmg(src_ref, amt):
        try:
            d_ = DMG(DENT(src_ref), JInt(0), JFloat(amt))
        except Exception:
            d_ = U.allocateInstance(DMG.class_)
            jfield(DMG, "source").set(d_, DENT(src_ref))
            jfield(DMG, "amount").set(d_, JFloat(amt))
        return d_
    d1 = dmg(A["ref"], 5.0)
    DF.filter(p9.ref, st, cb, d1)
    K.check(not d1.isCancelled() and any("took a hit: 5.0 damage, health 20.0 -> 15.0" in l for l in said()), "DMG: P9 non-lethal hit -> LOOK, not cancelled")
    d2 = dmg(A["ref"], 25.0)
    cb.removed.clear()
    DF.filter(p9.ref, st, cb, d2)
    o = said()
    K.check(d2.isCancelled() and float(d2.getAmount()) == 0.0 and cb.removed.size() == 1 and bool(p9.gone)
            and any(l.startswith("P9 PASS: P9 Skeleton - hit me (DOWN test): the lethal hit (25.0 vs 20.0 health) was CANCELLED") for l in o), "DMG: P9 lethal -> cancelled + removed (DOWN): %s" % o)
    d3 = dmg(A["ref"], 99.0)
    d3.setCancelled(True)
    DF.filter(A["ref"], st, cb, d3)
    K.check(said() == [], "DMG: a cancelled event is left alone")
    # P7: credit off -> the pet's hits stay the pet's; a kill -> LOOK
    run("p7")
    knight = [x for x in P("p7")][0]
    pig = P("p7t")[0]
    K.check(bool(knight.fight) and not bool(pig.fight), "CMD: p7 = fighter + target")
    pmap = U.allocateInstance(FSM.class_)
    pmap.hp = U.allocateInstance(FSV.class_)
    pmap.hp.v = JFloat(10.0)
    put(pig.ref, TY["EntityStatMap"], pmap)
    d4 = dmg(knight.ref, 4.0)
    DF.filter(pig.ref, st, cb, d4)
    K.check(isinstance(d4.getSource(), DENT) and d4.getSource().getRef() == knight.ref, "DMG: credit off -> source stays the pet")
    DI.inspect(pig.ref, st, d4)
    K.check(any("P7 HIT: P7 Skeleton fighter hit Pig for 4.0 (health 10.0)" in l for l in logged()) and int(knight.hitsDealt) == 1 and int(pig.hitsTaken) == 1,
            "DMG: inspect: a pet hit (log) + hit counted on the target pet")
    d5 = dmg(knight.ref, 12.0)
    DI.inspect(pig.ref, st, d5)
    o = said()
    K.check(any(l.startswith("P7 LOOK: KILL: P7 Skeleton fighter hit Pig for 12.0 (health 10.0)") and "the PET (credit off)" in l for l in o), "DMG: a kill by the pet (credit off) -> LOOK: %s" % o)
    out = run("p7", "credit")
    K.check(bool(Reg.CREDIT) and "P7 credit ON" in out[0], "CMD: p7 credit -> ON")
    d6 = dmg(knight.ref, 12.0)
    DF.filter(pig.ref, st, cb, d6)
    K.check(d6.getSource().getRef() == A["ref"] and Reg.REWRITE.containsKey(str(pig.uuid)), "DMG: credit on -> the source is rewritten to YOUR entity")
    DI.inspect(pig.ref, st, d6)
    o = said()
    K.check(any(l.startswith("P7 PASS: KILL: P7 Skeleton fighter (source rewritten to a player) hit Pig for 12.0") and "YOU (credit on)" in l for l in o)
            and not Reg.REWRITE.containsKey(str(pig.uuid)), "DMG: the rewritten kill -> PASS line (Skyy checks Combat XP): %s" % o)
    d7 = dmg(atk, 3.0)
    DF.filter(pig.ref, st, cb, d7)
    K.check(d7.getSource().getRef() == atk, "DMG: credit on, a non-pet attacker -> untouched")
    d8 = dmg(knight.ref, 3.0)
    d8.setCancelled(True)
    DI.inspect(pig.ref, st, d8)
    K.check(said() == [] and int(pig.hitsTaken) == 4, "DMG: a cancelled hit by a pet is not reported (but the hit on the pet is counted)")
    for i in range(20):
        DI.inspect(pig.ref, st, dmg(atk, 1.0))
    K.check(sum(1 for l in logged() if "HIT ON PET" in l) <= 6, "DMG: hits on a pet are logged at most 5 times + every 20th")
    Log.result(None, "x", -1, "y")
    said()
    run("p7", "credit")
    K.check(not bool(Reg.CREDIT), "CMD: p7 credit -> OFF again")
    knight.pr = None
    Reg.CREDIT = True
    d9 = dmg(knight.ref, 1.0)
    DF.filter(pig.ref, st, cb, d9)
    K.check(d9.getSource().getRef() == knight.ref, "DMG: credit on but no owner PlayerRef -> untouched")
    Reg.CREDIT = False
    K.check(DF.attacker(st, U.allocateInstance(DMG.class_)) is None, "DMG: attacker with no entity source -> null")
    # FIX critic-2: the credit rewrite only ever touches the P7 pig
    Reg.CREDIT = True
    knight.pr = A["pr"]
    run("p6")
    p6k = P("p6")[0]
    dA = dmg(knight.ref, 2.0)
    DF.filter(atk, st, cb, dA)
    dB = dmg(knight.ref, 2.0)
    DF.filter(p6k.ref, st, cb, dB)
    dC = dmg(knight.ref, 2.0)
    DF.filter(pig.ref, st, cb, dC)
    K.check(dA.getSource().getRef() == knight.ref and dB.getSource().getRef() == knight.ref and dC.getSource().getRef() == A["ref"],
            "DMG FIX critic-2: credit on -> a real mob / another probe pet hit by the fighter keeps the PET as source; only the P7 pig is rewritten")
    Reg.REWRITE.clear()
    Reg.CREDIT = False
    # FIX critic-4.4: a non-P7 probe pet's first hit = a LOOK line naming its target (assist / defend); later hits = log only
    said()
    logged()
    DI.inspect(atk, st, dmg(p6k.ref, 2.0))
    DI.inspect(atk, st, dmg(p6k.ref, 2.0))
    o, lg_ = said(), logged()
    K.check(len(o) == 1 and o[0].startswith("P6 LOOK: ATTACK: P6 Skeleton (summon flock) hit ? for 2.0") and "defend / assist" in o[0]
            and any(l.startswith("INFO P6 HIT: P6 Skeleton (summon flock) hit") for l in lg_) and not any("P7 HIT" in l for l in lg_),
            "DMG FIX critic-4.4: P6 summon's first hit -> 'P6 LOOK: ATTACK' line, the next one -> 'P6 HIT' log: %s" % o)
    DI.inspect(pig.ref, st, dmg(p6k.ref, 50.0))
    K.check(any(l.startswith("P6 LOOK: KILL: P6 Skeleton (summon flock) hit Pig") for l in said()), "DMG: a P6 kill -> 'P6 LOOK: KILL'")
    # FIX critic-4.2: a second p7 run removes the last run's fighter + pig first
    k_old, pig_old = str(knight.uuid), str(pig.uuid)
    out = run("p7")
    K.check(out[0] == "P7: removed the 2 pets of the last P7 run first (one fighter + one pig per run)." and len(P("p7")) == 1 and len(P("p7t")) == 1
            and str(P("p7")[0].uuid) != k_old and str(P("p7t")[0].uuid) != pig_old and not Reg.PETS.containsKey(k_old)
            and len(P("p6")) == 1 and out[-1].startswith("P7: 2/2 spawned - with ONLY the pig nearby"), "CMD FIX critic-4.2: p7 again -> the old fighter + pig removed, one of each left: %s" % out)
    out = run("p7", "credit")
    K.check("ON THE P7 PIG count as YOURS" in out[0] and "XP you get is real and stays" in out[0], "CMD: credit ON says it is the pig only + XP is real")
    run("clear")
    K.check(not bool(Reg.CREDIT), "CMD FIX critic-2: clear turns credit OFF")
    run("p7")
    # the system wrappers: handle() with a damage event and with another event; getGroup / getQuery
    ch = U.allocateInstance(MCH.class_)
    ch.ref = pig.ref
    dfs, dis = DF(), DI()
    dfs.handle(0, ch, st, cb, dmg(atk, 1.0))
    dis.handle(0, ch, st, cb, dmg(atk, 1.0))
    dfs.handle(0, ch, st, cb, None)
    dis.handle(0, ch, st, cb, None)
    ch.boom = True
    dfs.handle(0, ch, st, cb, dmg(atk, 1.0))
    dis.handle(0, ch, st, cb, dmg(atk, 1.0))
    lg_ = logged()
    K.check(any("damage filter failed" in l for l in lg_) and any("damage inspect failed" in l for l in lg_), "DMG: a broken chunk is logged once per system: %s" % [l for l in lg_ if "failed" in l])
    IDH = JClass("java.lang.System").identityHashCode
    K.check(dfs.getGroup() is not None and dis.getGroup() is not None and int(IDH(dfs.getGroup())) != int(IDH(dis.getGroup())) and dfs.getQuery() is not None,
            "DMG: filter / inspect groups (DamageModule) differ")
    run("clear")
    logged()
    said()

    # ================= LIFE: died, profile switch, world change; logout
    run("p6")
    p6e = P("p6")[0]
    p6e.checked, p6e.mobChecked, p6e.stage = True, True, 2
    put(A["ref"], DTH.getComponentType(), U.allocateInstance(DTH.class_))
    Tick.ACC.clear()
    tick()
    o = said()
    K.check(any(l.startswith("LIFE LOOK: you died: 1 probe pets removed") for l in o) and bool(p6e.gone), "LIFE: owner died -> pets removed")
    tick()
    K.check(said() == [], "LIFE: still dead -> nothing more")
    st.comps.get(A["ref"]).remove(DTH.getComponentType())
    run("p6")
    p6f = P("p6")[0]
    p6f.checked, p6f.mobChecked, p6f.stage = True, True, 2
    bridge.put("profile:epoch:" + str(A["uuid"]), JLong(4))
    tick()
    K.check(said() == [] and not bool(p6f.gone), "LIFE: the first epoch seen is only remembered")
    bridge.put("profile:epoch:" + str(A["uuid"]), JLong(5))
    tick()
    o = said()
    K.check(any(l.startswith("LIFE LOOK: profile switch seen (epoch 4 -> 5): 1 probe pets removed") for l in o) and bool(p6f.gone), "LIFE: profile switch -> removed")
    run("p6")
    p6g = P("p6")[0]
    p6g.checked, p6g.mobChecked, p6g.stage = True, True, 2
    p6g.world = w2
    w2.ran = 0
    tick()
    o = said()
    K.check(any(l.startswith("LIFE LOOK: you changed world (now default): 1 probe pets in the old world queued") for l in o) and int(w2.ran) == 1 and bool(p6g.gone),
            "LIFE: world change -> queued on the old world's thread + removed there")
    # a pet in another world while you are dead -> queued too
    run("p6")
    p6h = P("p6")[0]
    p6h.world = w2
    lst_ = AL()
    lst_.add(p6h)
    K.check(int(Life.removeHere(cb, lst_, w, "test")) == 1, "LIFE: removeHere queues a pet of another world")
    # logout: PpQuit with a REAL PlayerDisconnectEvent
    run("p6")
    run("p6")
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    try:
        ev = PDE(A["pr"])
    except Exception:
        ev = U.allocateInstance(PDE.class_)
        for f in PDE.class_.getDeclaredFields():
            if f.getType() == PRc.class_:
                f.setAccessible(True)
                f.set(ev, A["pr"])
    K.check(ev.getPlayerRef() == A["pr"], "Q: a PlayerDisconnectEvent for Skyy")
    Quit().accept(ev)
    o = said()
    K.check(any(l.startswith("LIFE LOOK: Skyy logged out: 2 of 2 probe pets queued") for l in o) and Reg.ofOwner(A["uuid"]).isEmpty(), "Q: logout -> both pets removed on their world thread: %s" % o)
    Quit().accept(None)
    K.check(int(Quit.leave(None, "x")) == 0 and any("logout handler failed" in l for l in logged()), "Q: a broken event is logged once")

    # ================= RM: PpRemove odds and ends
    run("p6")
    pr6 = P("p6")[0]
    w.boom = True
    K.check(bool(Rmv.queue(pr6, "t")) is False and bool(pr6.gone), "RM: queue on a world that refuses the job -> dropped")
    w.boom = False
    K.check(not bool(Rmv.queue(pr6, "again")) and not bool(Rmv.queue(None, "x")), "RM: queue a gone / null pet -> false")
    run("p6")
    pr7 = P("p6")[0]
    pr7.world = None
    K.check(not bool(Rmv.queue(pr7, "t")) and bool(pr7.gone), "RM: queue with no world -> dropped")
    run("p6")
    pr8 = P("p6")[0]
    mode["nostore"] = True
    Rmv(pr8, "no store").run()
    mode["nostore"] = False
    K.check(bool(pr8.gone) and str(pr8.goneWhy) == "no store (no world store)", "RM: run with no store -> dropped")
    Rmv(None, "x").run()
    run("p6")
    pr9 = P("p6")[0]
    st.removeEntity(pr9.ref, RR.REMOVE)
    K.check(not bool(Rmv.now(st, pr9, "x")) and bool(pr9.gone) and not bool(Rmv.now(st, pr9, "y")), "RM: now on an entity that is gone -> dropped; twice -> false")
    run("p6")
    pra = P("p6")[0]
    st.removeEntity(pra.ref, RR.REMOVE)
    K.check(not bool(Rmv.viaBuffer(cb, pra, "x")) and bool(pra.gone) and not bool(Rmv.viaBuffer(cb, pra, "y")), "RM: viaBuffer on an entity that is gone -> dropped")
    Rmv.unride(st, pra)
    logged()

    # ================= TK: the ticking system wrapper
    run("p6")
    tk = Tick()
    ch2 = U.allocateInstance(MCH.class_)
    ch2.ref = A["ref"]
    Tick.ACC.clear()
    tk.tick(JFloat(1.0), 0, ch2, st, cb)
    ch2.boom = True
    tk.tick(JFloat(1.0), 0, ch2, st, cb)
    K.check(any("probe tick failed" in l for l in logged()) and tk.getQuery() is not None and not bool(tk.isParallel(0, 1)), "TK: tick wrapper, failure logged once, query, not parallel")
    Tick.run(JFloat(1.0), Bp["ref"], st, cb)
    nopr = mkref()
    Tick.run(JFloat(1.0), nopr, st, cb)
    K.check(said() == [], "TK: a player with no probe pets / no PlayerRef -> nothing")
    # a probe step that throws is logged once
    p6t = P("p6")[0]
    p6t.tag = None
    Tick.ACC.clear()
    tick()
    K.check(any("probe step null failed" in l for l in logged()), "TK: a probe step that throws is logged once")
    p6t.tag = "p6"
    run("clear")

    # ================= MT: watch with no Player component; ride with no position
    run("p10")
    hz = P("p10")[0]
    rz = mkref()
    Mnt.watch(st, rz, A["pr"], hz, hz.ref)
    K.check(str(Mnt.mountInfo(st, rz)) == "no NPCMountComponent", "MT: mountInfo with none")
    K.check(str(Mnt.ride(st, rz, A["pr"])) == "your position is unreadable", "MT: ride with no position")
    run("clear")

    # ================= ALL + the remaining one-liners
    out = run("all")
    K.check(out[-4].startswith("P1: 7/7") and out[-3].startswith("P2: 4/4") and out[-2].startswith("P4: 1/1") and out[-1].startswith("P8: 1/1") and Reg.PETS.size() == 13,
            "CMD: all = p1 + p2 + p4 + p8 (13 pets): %s" % out)
    run("clear")
    out = run("p9")
    K.check(out[-1].startswith("P9: 1/1 spawned"), "CMD: p9 line")
    run("clear")
    mode["roles"]["Pig"] = -1
    out = run("p9")
    K.check(out[-1].startswith("P9: 0/1 spawned") and out[0].startswith("P9 FAIL: P9 Skeleton - hit me (DOWN test): role Pig is not spawnable"), "CMD: a probe whose role is missing -> FAIL + 0/1")
    mode["roles"]["Pig"] = ROLE_IX["Pig"]
    out = run("p3", "jump")
    K.check(out == ["/petprobe p3 takes no 'jump'."], "CMD: p3 bad option")
    run("p7", "nope")
    run("p10", "nope")
    out = run("p5", "x")
    K.check(out == ["/petprobe p5 takes no 'x'."], "CMD: p5 takes no option")
    run("clear")

    # ================= CE: the 3 commands' execute() through reflection with a real CommandContext
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    STc = JClass("com.hypixel.hytale.component.Store")
    cm0, cm1, cm2 = (JClass(PKG + n)() for n in ("PetProbeCmd", "PetProbeArgCmd", "PetProbeArg2Cmd"))

    def execute(c, ctx):
        m_ = c.getClass().getDeclaredMethod("execute", CTXc.class_, STc.class_, REF.class_, PRc.class_, WLD.class_)
        m_.setAccessible(True)
        m_.invoke(c, JArray(JObject)([ctx, st, A["ref"], A["pr"], w]))

    def ctx_of(pairs):
        c = U.allocateInstance(CTXc.class_)
        av = HM()
        for a_, v in pairs:
            av.put(a_, v)
        jfield(CTXc, "argValues").set(c, av)
        return c
    execute(cm0, None)
    K.check(len(said()) == 14, "CE: /petprobe execute -> help")
    execute(cm1, ctx_of([(cm1.aArg, "list")]))
    K.check(said()[0] == "0 probe pets (max 40):", "CE: /petprobe list through PetProbeArgCmd + CommandContext.get")
    execute(cm2, ctx_of([(cm2.aArg, "nosave"), (cm2.bArg, "on")]))
    K.check("NonSerialized on new probe pets: ON" in said()[0], "CE: /petprobe nosave on through PetProbeArg2Cmd")
    for c_ in (cm1, cm2):
        execute(c_, None)
    K.check(len(said()) == 28, "CE: every variant without a context -> help")

    # ================= PL: plugin census / start / shutdown
    PLc = JClass(PKG + "SkyyPetProbePlugin")
    cen = str(PLc.census())
    K.check(cen.startswith("roles Bat=") and "(0 not spawnable)" in cen and "models 16/16 loaded" in cen, "PL: census: %s" % cen[-80:])
    mode["roles"]["Bat"] = -1
    K.check("(1 not spawnable)" in str(PLc.census()), "PL: census counts a missing role")
    mode["roles"]["Bat"] = ROLE_IX["Bat"]
    plg = U.allocateInstance(PLc.class_)
    sm_ = PLc.class_.getDeclaredMethod("start")
    sm_.setAccessible(True)
    sm_.invoke(plg, JArray(JObject)([]))
    K.check(any(l.startswith("INFO census at start: roles") for l in logged()), "PL: start logs the census")
    run("p6")
    run("p6")
    Reg.REWRITE.put("a", "b")
    Tick.ACC.put(A["uuid"], JArray(JDouble)([0.5]))
    Fil.GHOSTS.put("g", "h")
    Reg.CREDIT = True
    w.ran = 0
    try:
        sd = PLc.class_.getDeclaredMethod("shutdown")
        sd.setAccessible(True)
        sd.invoke(plg, JArray(JObject)([]))
    except Exception as e:
        K.notes.append("plugin shutdown: super.shutdown() on an allocated plugin: %s" % str(e)[:120])
    K.check(Reg.PETS.isEmpty() and Reg.REWRITE.isEmpty() and Tick.ACC.isEmpty() and Fil.GHOSTS.isEmpty() and int(w.ran) == 2
            and any("stop: 2 of 2 probe pets queued for removal" in l for l in logged()) and not bool(Reg.CREDIT),
            "PL: shutdown queues every pet on its world + clears memory (FIX critic-2: credit OFF)")
    lt = open(os.path.join(pdir, "probe.log"), encoding="utf-8").read().splitlines()
    K.check(sum(1 for l in lt[-8:] if " WHERE " in l) >= 2, "PL FIX critic-1: shutdown writes each pet's last known spot (WHERE) for the next start's ghost list")
    Eng.API = None
    Log.SINK, Log.LINES = None, None
    SYS.getProperties().remove("skyy.bridge")
    print("X. every probe path executed")


def run_perm(out):
    """child P: permissions with the engine's own AbstractCommand code"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("PetProbeCmd", "PetProbeArgCmd", "PetProbeArg2Cmd"):
        c = JClass(PKG + cn)()
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "PetProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
            K.check("pprobe" in [str(a) for a in c.getAliases()] and str(c.getName()) == "petprobe", "P. /petprobe + alias /pprobe")
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
            elif op in (0xb2, 0xb3):
                calls.append(("get " if op == 0xb2 else "put ") + str(cpool.getFieldrefClassName(it.u16bitAt(p + 1))).rsplit(".", 1)[-1] + "."
                             + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
            elif op in (0x12, 0x13):
                i = it.byteAt(p + 1) if op == 0x12 else it.u16bitAt(p + 1)
                if cpool.getTag(i) == JClass("javassist.bytecode.ConstPool").CONST_String:
                    calls.append("ldc " + str(cpool.getStringInfo(i)))
    return calls


def run_bytecode(out):
    """child B: setup() order; the real engine lines = vanilla's call shapes; the engine facts the probe relies on"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    nm = lambda cs: [c.split("(")[0] for c in cs]
    calls = nm(bytecode_calls(cp, PKG + "SkyyPetProbePlugin", "setup"))
    want = ["PluginBase.getLogger", "put PpLog.LOG", "PluginBase.getDataDirectory", "put PpFile.DIR", "PpFile.load", "PluginBase.getCommandRegistry",
            "new PetProbeCmd", "CommandRegistry.registerCommand", "new PpTick", "ComponentRegistryProxy.registerSystem", "new PpDmgFilter",
            "ComponentRegistryProxy.registerSystem", "new PpDmgInspect", "ComponentRegistryProxy.registerSystem", "new PpLoadSys",
            "ComponentRegistryProxy.registerSystem", "PluginBase.getEventRegistry", "new PpQuit", "EventRegistry.registerGlobal"]
    pos, ok = 0, True
    for x in want:
        try:
            pos = calls.index(x, pos) + 1
        except ValueError:
            ok = False
            break
    K.check(ok and calls.count("ComponentRegistryProxy.registerSystem") == 4, "B: setup() = LOG, data folder, load, registerCommand, registerSystem once each for 4 systems, registerGlobal(PlayerDisconnectEvent): %s" % calls)
    full = lambda cls, m, sig=None: bytecode_calls(cp, cls, m, sig)
    eng = PKG + "PpEng"
    SPAWN7 = "NPCPlugin.spawnEntity(Lcom/hypixel/hytale/component/Store;ILorg/joml/Vector3dc;Lcom/hypixel/hytale/math/vector/Rotation3fc;Lcom/hypixel/hytale/server/core/asset/type/model/config/Model;Lcom/hypixel/hytale/function/consumer/TriConsumer;Lcom/hypixel/hytale/function/consumer/TriConsumer;)"
    K.check(any(c.startswith(SPAWN7) for c in full(eng, "spawn")), "B: PpEng.spawn = NPCPlugin.spawnEntity 7-argument form (pre-add consumer, null post)")
    van7 = full("com.hypixel.hytale.server.npc.NPCPlugin", "spawnEntity", "TriConsumer;Lcom/hypixel/hytale/function/consumer/TriConsumer;)")
    i_pre = [i for i, c in enumerate(van7) if c.startswith("TriConsumer.accept")]
    i_add = [i for i, c in enumerate(van7) if c.startswith("Store.addEntity")]
    K.check(len(i_pre) == 2 and len(i_add) == 1 and i_pre[0] < i_add[0] < i_pre[1] and any(c.startswith("Model.toReference") for c in van7),
            "B: engine fact: spawnEntity calls the PRE consumer (our PpPre) before Store.addEntity, the post one after; it puts ModelComponent + PersistentModel")
    am = full("com.hypixel.hytale.builtin.mounts.npc.ActionMount", "execute")
    our_rc = [c for c in full(eng, "roleChange") if "requestRoleChange" in c]
    K.check(our_rc and our_rc == [c for c in am if "requestRoleChange" in c], "B: PpEng.roleChange = ActionMount's RoleChangeSystem.requestRoleChange: %s" % our_rc)
    mm = full(eng, "mountMove")
    for k in ("MovementConfig.getAssetMap", "MovementManager.setDefaultSettings", "MovementManager.applyDefaultSettings",
              "MovementManager.update", "PlayerRef.getPacketHandler", "Player.getGameMode"):
        ours = [c for c in mm if c.startswith(k)]
        K.check(ours and ours[0] in am, "B: PpEng.mountMove %s = ActionMount's" % k)
    # javassist names the declaring class of the inherited getAsset (DefaultAssetMap); same method + descriptor, same virtual call
    ga = lambda cs: [c.split(".", 1)[1] for c in cs if ".getAsset(" in c]
    K.check(ga(mm) and ga(mm) == ga(am), "B: PpEng.mountMove getAsset(Object) = ActionMount's (same method, inherited owner): %s" % ga(mm))
    K.check("ldc Mount" in mm, "B: PpEng.mountMove asks the 'Mount' movement config")
    K.check(any(c.startswith("MountPlugin.checkDismountNpc") for c in full(eng, "dismount")), "B: PpEng.dismount = MountPlugin.checkDismountNpc")
    rst = [c for c in full(eng, "resetMove") if c.startswith("MovementManager.resetDefaultsAndUpdate")]
    van_rst = [c for c in full("com.hypixel.hytale.builtin.mounts.MountPlugin", "resetOriginalPlayerMovementSettings") if c.startswith("MovementManager.resetDefaultsAndUpdate")]
    K.check(rst and van_rst and rst[0] == van_rst[0], "B FIX critic-3: PpEng.resetMove = MountPlugin.resetOriginalPlayerMovementSettings' MovementManager.resetDefaultsAndUpdate: %s" % rst)
    bmt = full("com.hypixel.hytale.server.npc.corecomponents.movement.BodyMotionTeleport", "computeSteering")
    ours = [c for c in full(PKG + "PpFollow", "teleport") if c.startswith("Teleport.createExact")]
    K.check(ours and ours[0] in bmt, "B: PpFollow.teleport = BodyMotionTeleport's Teleport.createExact")
    esp = full("com.hypixel.hytale.server.npc.pages.EntitySpawnPage", "createOrUpdatePreview")
    pre = full(PKG + "PpPre", "accept")
    for k in ("get EntityStore.REGISTRY", "ComponentRegistry.getNonSerializedComponentType", "NonSerialized.get"):
        K.check(any(c.startswith(k) for c in pre) and any(c.startswith(k) for c in esp), "B: PpPre %s = vanilla EntitySpawnPage's" % k)
    rbs = full("com.hypixel.hytale.server.npc.systems.RoleBuilderSystem", "onEntityAdd")
    K.check(any(c.startswith("Holder.ensureComponent") for c in pre) and any(c.startswith("Holder.ensureComponent") for c in rbs) and any(c.startswith("Invulnerable.getComponentType") for c in rbs),
            "B: PpPre ensureComponent(Invulnerable) = what RoleBuilderSystem does for an Invulnerable role")
    sc = [c for c in full(eng, "scaled") if c.startswith("Model.createScaledModel")]
    K.check(sc == ["Model.createScaledModel(Lcom/hypixel/hytale/server/core/asset/type/model/config/ModelAsset;F)Lcom/hypixel/hytale/server/core/asset/type/model/config/Model;"],
            "B: PpEng.scaled = Model.createScaledModel(ModelAsset, float)")
    K.check(any(c.startswith("NPCEntity.setAppearance(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/asset/type/model/config/ModelAsset;Lcom/hypixel/hytale/component/ComponentAccessor;)") for c in full(eng, "setAppearance")),
            "B: PpEng.setAppearance = NPCEntity.setAppearance(Ref, ModelAsset, ComponentAccessor)")
    K.check(any(c.startswith("FlockPlugin.getFlockReference") for c in full(eng, "flockOf")) and any(c.startswith("EntityStore.getRefFromUUID") for c in full(eng, "refOf"))
            and any(c.startswith("NPCPlugin.getIndex") for c in full(eng, "roleIndex")) and any(c.startswith("ModelAsset.getAssetMap") for c in full(eng, "modelAsset"))
            and any(c.startswith("EntityStore.getStore") for c in full(eng, "store")), "B: flockOf / refOf / roleIndex / modelAsset / store use the engine calls")
    oa = full("com.hypixel.hytale.builtin.mounts.NPCMountSystems$OnAdd", "onEntityAdded")
    K.check(any(c.startswith("NPCMountComponent.getOwnerPlayerRef") for c in oa) and "new MountNPC" in oa and any(c.startswith("Player.setMountEntityId") for c in oa),
            "B: engine fact: NPCMountSystems$OnAdd reads the owner, sends MountNPC and sets Player.mountEntityId (our ride puts a FULL component)")
    rd = full(PKG + "PpMount", "ride")
    K.check(any(c.startswith("Store.putComponent") for c in rd) and not any(c.startswith("Store.ensureAndGetComponent") for c in rd)
            and any(c.startswith("NPCMountComponent.setOwnerPlayerRef") for c in rd) and any(c.startswith("NPCMountComponent.setAnchor") for c in rd)
            and any(c.startswith("NPCMountComponent.setOriginalRoleIndex") for c in rd) and "ldc Empty_Role" in rd,
            "B: PpMount.ride builds the whole NPCMountComponent, then putComponent; Empty_Role")
    K.check(any(c.startswith("DamageModule.getFilterDamageGroup") for c in full(PKG + "PpDmgFilter", "getGroup"))
            and any(c.startswith("DamageModule.getInspectDamageGroup") for c in full(PKG + "PpDmgInspect", "getGroup")), "B: the damage groups")
    K.check(any(c.startswith("NPCEntity.getComponentType") for c in full(PKG + "PpLoadSys", "getQuery")), "B: PpLoadSys queries NPC entities")
    K.check(any(c.startswith("Damage.setSource") for c in full(PKG + "PpDmgFilter", "filter")) and any(c.startswith("CancellableEcsEvent.setCancelled") for c in full(PKG + "PpDmgFilter", "filter")),
            "B: the filter cancels (P9) and rewrites the source (P7)")
    K.save()


def run_live(step, out):
    """child D: one 'server start' on the scratch copy of the live world mods folder"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    home = os.path.join(SCRATCH, "live")

    def snapshot():
        d = {}
        for root, _, files in os.walk(home):
            for f in files:
                p = os.path.join(root, f)
                d[os.path.relpath(p, home)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        return d
    Fil, Log = JClass(PKG + "PpFile"), JClass(PKG + "PpLog")
    Log.LINES = JClass("java.util.ArrayList")()
    mine = os.path.join(home, "Skyy_SkyyPetProbe")
    before = snapshot()
    Fil.DIR = JClass("java.nio.file.Paths").get(mine)
    n = int(Fil.load())
    ua, ub = "aaaaaaaa-1111-0000-0000-000000000001", "bbbbbbbb-1111-0000-0000-000000000002"
    if step in ("start1", "start2"):
        K.check(n == 0 and Fil.GHOSTS.isEmpty() and not os.path.exists(mine), "D %s: load on the live copy: 0 ghosts, no probe folder created" % step)
        K.check(snapshot() == before, "D %s: the probe wrote nothing - every scratch file byte-identical, no new file" % step)
    elif step == "start3":
        K.check(bool(Fil.append("SPAWN %s nonser=true at=default,3.0,4.0 p5 A fox" % ua)) and bool(Fil.append("SPAWN %s nonser=false at=default,5.0,4.0 p5 B corgi" % ub)),
                "D start3: two SPAWN lines")
        K.check(os.listdir(mine) == ["probe.log"], "D start3: the probe folder holds only probe.log")
    elif step == "start4":
        K.check(n == 2 and Fil.GHOSTS.containsKey(ua) and Fil.GHOSTS.containsKey(ub), "D start4: both SPAWN lines load as ghosts")
    elif step == "start5":
        txt = open(os.path.join(mine, "probe.log"), encoding="utf-8").read()
        K.check(n == 2 and Fil.GHOSTS.containsKey(ua) and Fil.GHOSTS.containsKey(ub) and "GONE" not in txt and txt.count("START") == 2
                and str(Fil.GHOST_AT.get(ua)) == "default,3.0,4.0",
                "D start5 (FIX critic-1): both ghosts stay listed with their spots - no expiry by run count")
    others = dict((k, v) for k, v in snapshot().items() if not k.startswith("Skyy_SkyyPetProbe"))
    base = dict((k, v) for k, v in before.items() if not k.startswith("Skyy_SkyyPetProbe"))
    K.check(others == base, "D %s: every other mod's live-copy file byte-identical" % step)
    Log.LINES = None
    K.save(files=len(others))


def run_audit(out):
    """child AA: the engine-access audit (the SkyyTownProbe harness part AA)"""
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
    if "--mkfake" in sys.argv:
        run_mkfake(arg("--mkfake"))
        return
    if "--engine" in sys.argv:
        run_engine(arg("--out"))
        return
    if "--live-step" in sys.argv:
        run_live(arg("--live-step"), arg("--out"))
        return
    if "--perm" in sys.argv:
        run_perm(arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--out"))
        return
    if "--audit" in sys.argv:
        run_audit(arg("--out"))
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
        out = os.path.join(SCRATCH, "engine.json")
        child(env, "--engine", "x", "--out", out)
        take(out, "engine")
        home = os.path.join(SCRATCH, "live")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        n = sum(len(f) for _, _, f in os.walk(home))
        print("D. %d live mod data files copied (read-only source %s)" % (n, LIVE))
        check(n > 0 and not os.path.exists(os.path.join(home, "Skyy_SkyyPetProbe")), "D: live mod data copied, no probe folder there yet (%s)" % LIVE)
        for step in ("start1", "start2", "start3", "start4", "start5"):
            out = os.path.join(SCRATCH, "live-%s.json" % step)
            child(env, "--live-step", step, "--out", out)
            take(out, "live " + step)
        for label, flag in (("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            child(env, flag, "--out", out)
            take(out, label)
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
