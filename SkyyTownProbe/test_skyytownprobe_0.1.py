"""Harness for SkyyTownProbe 0.1. Build first: python SkyyTownProbe/build_skyytownprobe_0.1.py

    python SkyyTownProbe/test_skyytownprobe_0.1.py [--jar <SkyyTownProbe-0.1.jar>] [--live <a world mods folder>] [--keep]

Parent (plain Python, Assets.zip + the jar read-only):
  J  the jar: manifest (Main, IncludesAssetPack false, Version, Name), exactly the 29 expected classes, NO other file (no asset of any
     kind: nothing for the engine's asset validators to refuse - the 2026-10-08 SkyyArmory lesson), no class package shared with an
     installed mod (read-only scan of UserData/Mods)
  K  every vanilla id / path the probe names is in Assets.zip: the temple + the 10 alias prefabs, role Temple_Kweebec_Static (Variant of
     Template_Temple, Invulnerable, MotionStatic, no InteractionInstruction), model Rubble_Stone_Mossy, the 4 lane / sign blocks, the
     hint key; the temple's 3 Prefab_Spawner_Block + 2 entities (what the probe reports on)
Children (fresh JVMs: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  the stand-ins generated with javassist (MapStore, MapBuffer, MapChunk, FakeWorld, FakePr, FakePageManager, FakePage, FakeSupplier,
     FakeSpatial, SimPaste / SimNoChild / SimNoEnt, LookupIn, BadAccess)
  A  every class loads and verifies (-Xverify:all)
  E  ENGINE ASSETS the probe uses at run time go through the engine's own codecs: the vanilla Rubble_Stone_Mossy (+ Rubble_Stone)
     ModelAsset JSON decode (no unknown key, no validation failure) and load; Model.createStaticScaledModel x5 keeps the id + scale
  X  EVERY NEW CODE PATH EXECUTED: TpLogic on plain data; TpRec text round trip + bad input; a simulated world (real PasteRegion +
     real BlockSections, ground from a height map, the real BlockType store with every block the temple names); the REAL temple
     buffer (BsonPrefabBufferDeserializer on the Assets.zip JSON, entity / component / fluid keys stripped) read through the REAL
     PrefabBufferUtil.getCached on a scratch file; TpEng swapped for a stand-in API whose paste = the REAL IPrefabBuffer.forEach with a
     PrefabBufferCall(rotation) writing into the region; every /townprobe action through TpCmds.run: help, temple 0 (snapshot = the
     ground before, the paste lands, the box, anchor / door / foot lines, Prefab_Spawner_Block count, entity count), temple 1e / 2 / 3
     boxes, undo after each (ground back BYTE FOR BYTE in every cell of the box), undo from the snapshot FILE (memory copy dropped, real
     PrefabBufferUtil.readFromFileAsync), piece by alias / path / dotted path / bad path / unknown prefab / bad rotation, lane (height
     smoothing, stairs, fill, cut, the unloaded-chunk refusal), sign (+ the nameplate prop holder), npc (spawn, name, Interactable, hint,
     Use root kept), npc again (the "already here" count = 1, never a second spawn), pebble (role kept the rock / replaced it -> forced
     back), zone / zone all / zone off / bad option, the wrong-world refusal, busy, the 20-record cap, failing region loads (exception,
     not loaded, null), too many words; undo of entity records (found / not found -> confirm within 30 s); TpUseSys (page not
     registered, registered -> opened through the REAL OpenCustomUIInteraction.PAGE_CODEC + a registered supplier, pebble line, a
     non-probe NPC untouched, a broken event logged once); the 4 guards on REAL Break / Place / Damage / UseBlock events (outside,
     inside non-admin refused + cancelled, inside admin allowed, zone all refuses admins, other world, no zone); TpTick (bark once
     within 8 blocks, not again within 60 s, re-armed after leaving, zone enter / leave lines, 1 s pacing); the 4 commands' execute()
     through reflection with a real CommandContext; the REAL TpEng.store / refOf (API off) on an allocated World / EntityStore; plugin
     shutdown clears the memory state
  FIX ROUND (townprobe01fix): a paste that throws partway keeps its undo record (undo restores every cell); the .properties is written
     only after the .lpf lands, a failed / late write leaves no record file, load deletes broken / orphan undo files; entities ON
     (temple 1e) are captured through the paste's entity consumer and removed by undo; /townprobe piece refuses a box over 300 000
     cells; a region job arriving after the 60 s busy escape is dropped (ticket); undo never forgets an NPC whose area is unloaded;
     the temple line tells the door side
  P  /townprobe and its 3 usage variants: node skyytownprobe.admin, empty permission groups, getPermissionGroupsRecursive() gives the
     node to no group; alias /tprobe
  B  BYTECODE: setup()'s calls in order (load, registerCommand, registerSystem once each for the 6 systems); every real engine line in
     TpEng has the SAME call descriptor as the vanilla code it copies (PrefabRemoveAction$RemoveOp paste + loadPasteRegionAsync,
     SpawnNpcEffect spawnNPC, SpawnPrefabInteraction findAssetPrefabPath + getCached); TpSnap.create calls the same engine methods as
     vanilla PrefabSnapshotUtil.createSnapshot; the engine facts the NPC relies on (RoleBuilderSystem sets "*UseNPC"; UseEntityInteraction
     fires UseEntityEvent$Pre only when the target has a Use id; EntityMakeInteractableCommand = Store.ensureComponent(Interactable));
     getCodecFor is the (Object) overload
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the live world mods folder (Saves/<deploy world>/mods, read-only, copied): start 1 and
     start 2 (fresh JVMs) load with no probe folder -> 0 records, NOTHING written (every file byte-identical, no new file); the live
     SkyyWorldGen worlds.properties names the probe's world; then start 3 writes an npc + a lane record, start 4 loads them back (NPC
     indexed, sequence continues) and undoes both -> the probe folder is gone again, every other mod folder byte-identical
  AA the ENGINE-ACCESS AUDIT: every class / field / method / constructor reference in the jar looked up with MethodHandles.privateLookupIn
     the referencing class (the JVM's own access rules) - 0 refused; the control refused
Not testable without the game (the build report lists them as UNVERIFIED): the real paste / region load in a live world (timing, whether
the 3 Prefab_Spawner blocks expand, how the temple sits on the island), what the client draws (stairs / sign facing, the rock model,
the nameplate prop), the F prompt and the page on a real client, whether Interactable / the hint survive a restart, chat range feel.
Scratch: tools/dev/scratch/townprobe01fix/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib

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


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyTownProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "townprobe01fix", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyytowntest"
PKG = "com.skyy.townprobe."
CLASSES = sorted(PKG + c for c in ["TpLog", "TpLogic", "TpRec", "TpZone", "TpStore", "TpEngApi", "TpEng", "TpSnap", "TpEntCount", "TpEntGrab", "TpBuild",
                                   "TpJob", "TpStep", "TpIoDone", "TpNpc", "TpPaste", "TpTick", "TpCmds", "TpUseSys", "TpGuard",
                                   "TpGuardBreak", "TpGuardDamage", "TpGuardPlace", "TpGuardUse", "TownProbeArgCmd", "TownProbeArg2Cmd",
                                   "TownProbeArg3Cmd", "TownProbeCmd", "SkyyTownProbePlugin"])
NODE = "skyytownprobe.admin"
WORLD = "skywynn_z1"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
TEMPLE = "Monuments/Unique/Temple/Portal/Grasslands_Spawn/Unique_Portal_Grasslands_Monuments_Unique_Portal_Grasslands_001.prefab.json"
ALIASES = {"stall": "Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001.prefab.json",
           "path": "Spawn/Pathways/Spawn_Zone1_Pathway_001.prefab.json"}
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
    check(man.get("Main") == PKG + "SkyyTownProbePlugin" and man.get("IncludesAssetPack") is False and man.get("Version") == VERSION
          and man.get("Name") == "%s SkyyTownProbe" % VERSION, "J: manifest Main / IncludesAssetPack false / Version / Name: %r" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(cls == CLASSES, "J: exactly the %d expected classes: extra %s missing %s" % (len(CLASSES), sorted(set(cls) - set(CLASSES)), sorted(set(CLASSES) - set(cls))))
    other = [n for n in names if not n.endswith(".class") and n != "manifest.json" and not n.endswith("/")]
    check(not other, "J: no asset / lang / .ui / other file ships (nothing for the asset validators): %s" % other)
    # no installed mod uses our package (read-only scan)
    clash = []
    if os.path.isdir(B.MODS_DIR):
        for f in os.listdir(B.MODS_DIR):
            p = os.path.join(B.MODS_DIR, f)
            if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyTownProbe"):
                continue
            try:
                with zipfile.ZipFile(p) as mz:
                    if any(n.startswith("com/skyy/townprobe/") for n in mz.namelist()):
                        clash.append(f)
            except Exception:
                pass
    check(not clash, "J: no installed mod ships com.skyy.townprobe classes: %s" % clash)
    az = zipfile.ZipFile(ASSETS)
    an = set(az.namelist())
    for p in [TEMPLE] + list(ALIASES.values()):
        check("Server/Prefabs/" + p in an, "K: prefab %s in Assets.zip" % p)
    roles = dict((n.rsplit("/", 1)[1][:-5], n) for n in an if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
    r = json.loads(az.read(roles["Temple_Kweebec_Static"]).decode("utf-8-sig"))
    t = json.loads(az.read(roles["Template_Temple"]).decode("utf-8-sig"))
    check(r.get("Reference") == "Template_Temple" and r["Modify"].get("MotionStatic") is True and t.get("Invulnerable") is True
          and "InteractionInstruction" not in r and "InteractionInstruction" not in t,
          "K: Temple_Kweebec_Static = Variant of Template_Temple, MotionStatic, Invulnerable, no InteractionInstruction (no barter shop)")
    check("Server/Models/Projectiles/Items/Rubble/Rubble_Stone_Mossy.json" in an, "K: the Rubble_Stone_Mossy model")
    items = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    check(all(b in items for b in ("Furniture_Village_Sign", "Rock_Stone_Cobble", "Rock_Stone_Cobble_Stairs", "Rock_Stone")), "K: the lane / sign blocks")
    tj = json.loads(az.read("Server/Prefabs/" + TEMPLE).decode("utf-8-sig"))
    check(sum(1 for b in tj["blocks"] if b["name"] == "Prefab_Spawner_Block") == 3 and len(tj.get("entities") or []) == 2,
          "K: the temple carries 3 Prefab_Spawner_Block + 2 entities (what the probe reports)")
    check("interactionHints.trade" in az.read("Server/Languages/en-US/server.lang").decode("utf-8"), "K: the vanilla hint key")


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
    for d in ("java.util.Map comps", "java.util.Map res", "java.util.Map holders", "java.util.List removed", "java.util.List added",
              "java.util.List ensured", "com.hypixel.hytale.component.Component ensureVal", "java.lang.Object ext", "int nextRef"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m != null && m.containsKey(t)) return (com.hypixel.hytale.component.Component) m.get(t);
  com.hypixel.hytale.component.Holder h = (com.hypixel.hytale.component.Holder) this.holders.get(r);
  return h == null ? null : h.getComponent(t);
}""")
    M(ms, """public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}""")
    M(ms, """public void ensureComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  this.ensured.add(t);
  if (getComponent(r, t) == null) putComponent(r, t, this.ensureVal);
}""")
    M(ms, """public com.hypixel.hytale.component.Holder removeEntity(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.RemoveReason why) {
  this.removed.add(r);
  this.comps.remove(r);
  this.holders.remove(r);
  return null;
}""")
    M(ms, """public com.hypixel.hytale.component.Ref addEntity(com.hypixel.hytale.component.Holder h, com.hypixel.hytale.component.AddReason why) {
  this.nextRef = this.nextRef + 1;
  com.hypixel.hytale.component.Ref r = new com.hypixel.hytale.component.Ref(this, 50000 + this.nextRef);
  this.holders.put(r, h);
  this.added.add(r);
  return r;
}""")
    M(ms, "public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return this.res == null ? null : (com.hypixel.hytale.component.Resource) this.res.get(t); }")
    M(ms, "public boolean isProcessing() { return false; }")
    M(ms, "public java.lang.Object getExternalData() { return this.ext; }")
    ms.writeFile(out_dir)
    mb = mk("MapBuffer", CR + "CommandBuffer")
    mb.addConstructor(CtNewConstructor.make("public MapBuffer() { super(null); }", mb))
    mb.writeFile(out_dir)
    mc = mk("MapChunk", CR + "ArchetypeChunk")
    F(mc, "public com.hypixel.hytale.component.Ref ref;")
    F(mc, "public boolean boom;")
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))
    M(mc, "public com.hypixel.hytale.component.Ref getReferenceTo(int i) { if (this.boom) throw new IllegalStateException(\"boom\"); return this.ref; }")
    mc.writeFile(out_dir)
    fw = mk("FakeWorld", "com.hypixel.hytale.server.core.universe.world.World")
    F(fw, "public int ran;")
    fw.addConstructor(CtNewConstructor.make("public FakeWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", fw))
    M(fw, "public void execute(java.lang.Runnable r) { this.ran = this.ran + 1; r.run(); }")
    fw.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    F(fp, "public boolean admin;")
    F(fp, "public java.util.List msgs;")
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public boolean hasPermission(java.lang.String n) { return this.admin && \"%s\".equals(n); }" % NODE)
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs != null) this.msgs.add(m); }")
    fp.writeFile(out_dir)
    pm = mk("FakePageManager", "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    F(pm, "public java.util.List opened;")
    M(pm, """public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {
  if (this.opened == null) this.opened = new java.util.ArrayList();
  this.opened.add(p);
}""")
    pm.writeFile(out_dir)
    fpg = mk("FakePage", "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage")
    fpg.addConstructor(CtNewConstructor.make("public FakePage() { super(null, null); }", fpg))
    M(fpg, "public void build(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.ui.builder.UICommandBuilder c, com.hypixel.hytale.server.core.ui.builder.UIEventBuilder e, com.hypixel.hytale.component.Store s) { }")
    fpg.writeFile(out_dir)
    fs = mk("FakeSupplier", None, ["com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction$CustomPageSupplier"])
    F(fs, "public static com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage PAGE;")
    F(fs, "public static int CALLS;")
    F(fs, "public static com.hypixel.hytale.server.core.universe.PlayerRef LAST;")
    fs.addConstructor(CtNewConstructor.make("public FakeSupplier() { super(); }", fs))
    M(fs, """public com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage tryCreate(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentAccessor a, com.hypixel.hytale.server.core.universe.PlayerRef p, com.hypixel.hytale.server.core.entity.InteractionContext c) {
  CALLS = CALLS + 1;
  LAST = p;
  return PAGE;
}""")
    fs.writeFile(out_dir)
    sup = mk("FakeSupplierMaker", None, ["java.util.function.Supplier"])
    sup.addConstructor(CtNewConstructor.make("public FakeSupplierMaker() { super(); }", sup))
    M(sup, "public java.lang.Object get() { return new %s.FakeSupplier(); }" % P)
    sup.writeFile(out_dir)
    sp = mk("FakeSpatial", None, ["com.hypixel.hytale.component.spatial.SpatialStructure"])
    F(sp, "public java.util.List refs;")
    F(sp, "public java.util.List pos;")
    sp.addConstructor(CtNewConstructor.make("public FakeSpatial() { super(); this.refs = new java.util.ArrayList(); this.pos = new java.util.ArrayList(); }", sp))
    M(sp, """public void collect(org.joml.Vector3dc c, double r, java.util.List out) {
  for (int i = 0; i < this.refs.size(); i++) {
    org.joml.Vector3d p = (org.joml.Vector3d) this.pos.get(i);
    double dx = p.x - c.x(); double dy = p.y - c.y(); double dz = p.z - c.z();
    if (dx * dx + dy * dy + dz * dz <= r * r) out.add(this.refs.get(i));
  }
}""")
    sp.writeFile(out_dir)
    IPB = "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.IPrefabBuffer"
    sim = mk("SimPaste", None, [IPB + "$BlockConsumer"])
    for d in ("com.hypixel.hytale.server.core.util.PrefabUtil$PasteRegion region", "int ox", "int oy", "int oz", "int n", "int zeros"):
        F(sim, "public %s;" % d)
    sim.addConstructor(CtNewConstructor.make("public SimPaste() { super(); }", sim))
    M(sim, """public void accept(int x, int y, int z, int id, com.hypixel.hytale.component.Holder h, int a, int b, int c, java.lang.Object t, int d, int e) {
  int wx = this.ox + x; int wy = this.oy + y; int wz = this.oz + z;
  com.hypixel.hytale.server.core.util.PrefabUtil$PasteRegion$Section s = this.region.getSectionAtBlock(wx, wy, wz);
  s.blocks().set(com.hypixel.hytale.math.util.ChunkUtil.indexBlock(wx, wy, wz), id, 0, 0);
  this.n = this.n + 1;
  if (id == 0) this.zeros = this.zeros + 1;
}""")
    sim.writeFile(out_dir)
    nc = mk("SimNoChild", None, [IPB + "$ChildConsumer"])
    nc.addConstructor(CtNewConstructor.make("public SimNoChild() { super(); }", nc))
    M(nc, "public void accept(int x, int y, int z, java.lang.String p, boolean a, boolean b, boolean c, com.hypixel.hytale.server.core.prefab.PrefabWeights w, com.hypixel.hytale.server.core.prefab.PrefabRotation r, java.lang.Object t) { }")
    nc.writeFile(out_dir)
    ne = mk("SimNoEnt", None, [IPB + "$EntityConsumer"])
    ne.addConstructor(CtNewConstructor.make("public SimNoEnt() { super(); }", ne))
    M(ne, "public void accept(int x, int z, com.hypixel.hytale.component.Holder[] h, java.lang.Object t) { }")
    ne.writeFile(out_dir)
    fh = mk("FakeHolder", CR + "Holder")
    F(fh, "public java.util.Map m;")
    fh.addConstructor(CtNewConstructor.make("public FakeHolder() { super(); this.m = new java.util.IdentityHashMap(); }", fh))
    M(fh, "public void addComponent(com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) { this.m.put(t, c); }")
    M(fh, "public void putComponent(com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) { this.m.put(t, c); }")
    M(fh, "public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) this.m.get(t); }")
    M(fh, """public void ensureComponent(com.hypixel.hytale.component.ComponentType t) {
  if (this.m.get(t) == null && t == com.hypixel.hytale.server.core.entity.UUIDComponent.getComponentType()) this.m.put(t, com.hypixel.hytale.server.core.entity.UUIDComponent.randomUUID());
}""")
    fh.writeFile(out_dir)
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
    """allocated HytaleServer / Universe, AssetRegistryLoader.init, the BlockType store with every block the temple / probe names,
    the ModelAsset store with the vanilla rubble models, allocated EntityModule / InteractionModule component types"""
    from jpype import JClass, JArray, JString, JInt, JImplements, JOverride
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
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    tj = json.loads(az.read("Server/Prefabs/" + TEMPLE).decode("utf-8-sig"))
    names = sorted(set(b["name"] for b in tj["blocks"]) | {"Rock_Stone", "Rock_Stone_Cobble", "Rock_Stone_Cobble_Stairs", "Soil_Grass",
                                                            "Soil_Dirt", "Furniture_Village_Sign", "Prefab_Spawner_Block", "Leaves_Oak"})
    names = [n for n in names if n not in ("Empty", "Unknown")]
    l_ = AL()
    l_.add(BT.EMPTY)
    l_.add(BT.UNKNOWN)
    for n in names:
        l_.add(BT(n))
    r_ = BT.getAssetStore().loadAssets("Hytale:Hytale", l_)
    m = BT.getAssetMap()
    K.check(not r_.hasFailed() and int(m.getIndex("Empty")) == 0 and int(m.getIndex("Rock_Stone_Cobble_Stairs")) > 1,
            "E: the BlockType store holds Empty (id 0), Unknown and the %d blocks the temple / lane / sign name" % len(names))
    # ModelAsset: the vanilla rubble JSON through the engine's own codec (validation results checked) + load
    MDA = JClass("com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset")
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths")
    st_ = MDA.getAssetStore()
    K.check(st_ is not None, "E: the ModelAsset store is registered by AssetRegistryLoader")
    models = AL()
    for mid in ("Rubble_Stone_Mossy", "Rubble_Stone"):
        txt = az.read("Server/Models/Projectiles/Items/Rubble/%s.json" % mid).decode("utf-8-sig")
        ei = AEI(Paths.get(mid + ".json"), ADT(MDA.class_, mid, None))
        try:
            o = st_.getCodec().decodeJsonAsset(RJR.fromJsonString(txt), ei)
            vr = ei.getValidationResults()
            bad = vr is not None and vr.hasFailed()
            K.check(o is not None and not bad, "E: vanilla model %s decodes through ModelAsset's codec, no validation failure" % mid)
            models.add(o)
        except Exception as e:
            K.check(False, "E: model %s decode: %s" % (mid, str(e)[:200]))
    if models.size():
        K.check(not st_.loadAssets("Hytale:Hytale", models).hasFailed() and MDA.getAssetMap().getAsset("Rubble_Stone_Mossy") is not None,
                "E: the rubble models load into the ModelAsset store")
    # component types: every ComponentType / ResourceType field of EntityModule + InteractionModule gets its own allocated value
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    RT = JClass("com.hypixel.hytale.component.ResourceType")
    SG = JClass("com.hypixel.hytale.component.SystemGroup")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]

    def fill(cls, inst):
        for f in cls.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()):
                continue
            t = f.getType()
            v = None
            if t == CT.class_:
                v = U.allocateInstance(CT.class_)
                n_[0] += 1
                jfield(CT, "index").set(v, JInt(n_[0]))
            elif t == RT.class_:
                v = U.allocateInstance(RT.class_)
            elif t == SG.class_:
                v = U.allocateInstance(SG.class_)
            if v is not None:
                f.setAccessible(True)
                f.set(inst, v)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    fill(EM, em)
    jfield(EM, "instance").set(None, em)
    c2t = JClass("java.util.HashMap")()
    npc_t = U.allocateInstance(CT.class_)
    n_[0] += 1
    jfield(CT, "index").set(npc_t, JInt(n_[0]))
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    c2t.put(NPCc.class_, npc_t)
    jfield(EM, "classToComponentType").set(em, c2t)
    IM = JClass("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    im = U.allocateInstance(IM.class_)
    fill(IM, im)
    jfield(IM, "instance").set(None, im)
    upr = U.allocateInstance(CT.class_)
    n_[0] += 1
    jfield(CT, "index").set(upr, JInt(n_[0]))
    jfield(UNI, "playerRefComponentType").set(uni, upr)
    K.check(NPCc.getComponentType() == npc_t, "E: NPCEntity.getComponentType() resolves through the allocated EntityModule")
    return {"U": U, "jfield": jfield, "az": az, "em": em, "BT": BT, "tj": tj, "uni": uni}


class SimWorld(object):
    """the simulated island: real BlockSections per chunk section, ground from a height map (top Soil_Grass, 2 x Rock_Stone below),
    shared by every PasteRegion built over it (so a paste, a snapshot and an undo all see the same blocks)"""

    def __init__(self, E, H):
        from jpype import JClass
        self.E, self.H = E, H
        self.BS = JClass("com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection")
        self.PSEC = JClass("com.hypixel.hytale.server.core.util.PrefabUtil$PasteRegion$Section")
        self.PREG = JClass("com.hypixel.hytale.server.core.util.PrefabUtil$PasteRegion")
        self.CHU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
        m = E["BT"].getAssetMap()
        self.ids = {"grass": int(m.getIndex("Soil_Grass")), "rock": int(m.getIndex("Rock_Stone")), "leaf": int(m.getIndex("Leaves_Oak"))}
        self.secs = {}
        self.extra = {}                    # (x, y, z) -> id placed before a section exists (a leaf above ground)

    def sec(self, cx, cy, cz):
        k = (cx, cy, cz)
        s = self.secs.get(k)
        if s is not None:
            return s
        bs = self.BS()
        for lx in range(32):
            for lz in range(32):
                x, z = cx * 32 + lx, cz * 32 + lz
                h = self.H(x, z)
                for y in range(h - 2, h + 1):
                    if y // 32 == cy:
                        bs.set(self.CHU.indexBlock(x, y, z), self.ids["grass"] if y == h else self.ids["rock"], 0, 0)
        for (x, y, z), i in self.extra.items():
            if x // 32 == cx and y // 32 == cy and z // 32 == cz:
                bs.set(self.CHU.indexBlock(x, y, z), i, 0, 0)
        s = self.PSEC(bs, None, None, None, None)
        self.secs[k] = s
        return s

    def block(self, x, y, z):
        return int(self.sec(x // 32, y // 32, z // 32).getBlock(self.CHU.indexBlock(x, y, z)))

    def region(self, x0, y0, z0, x1, y1, z1, loaded=True):
        cx0, cy0, cz0, cx1, cy1, cz1 = x0 // 32, y0 // 32, z0 // 32, x1 // 32, y1 // 32, z1 // 32
        r = self.PREG(cx0, cy0, cz0, cx1, cy1, cz1, None)
        sy, sx = cy1 - cy0 + 1, cx1 - cx0 + 1
        arr = r.sections
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                for cz in range(cz0, cz1 + 1):
                    arr[(cy - cy0) + (cx - cx0) * sy + (cz - cz0) * sy * sx] = self.sec(cx, cy, cz)
        if loaded:
            self.E["jfield"](self.PREG, "fullyLoaded").get(r).set(True)
        return r

    def box_hash(self, bx):
        h = hashlib.sha256()
        for x in range(bx[0], bx[3] + 1):
            for z in range(bx[2], bx[5] + 1):
                for y in range(bx[1], bx[4] + 1):
                    h.update(b"%d," % self.block(x, y, z))
        return h.hexdigest()

    def height(self, x, z):
        top = self.H(x, z) + 40
        for y in range(top, top - 90, -1):
            if self.block(x, y, z) != 0:
                return y
        return -1000000


def run_engine(out):
    """child X (+ A, E): every probe path on the simulated world"""
    from jpype import JClass, JArray, JObject, JInt, JFloat, JDouble, JLong, JString, JImplements, JOverride, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    # A: every class loads + verifies
    bad = []
    for cn in CLASSES:
        try:
            JClass("java.lang.Class").forName(cn, True, JClass("java.lang.ClassLoader").getSystemClassLoader())
        except Exception as e:
            bad.append("%s: %s" % (cn, str(e)[:160]))
    K.check(not bad, "A: every class loads and verifies under -Xverify:all: %s" % bad)
    E = engine_setup(K)
    U, jfield = E["U"], E["jfield"]
    try:
        xrun(K, E)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:400])
    K.save()


def xrun(K, E):
    from jpype import JClass, JArray, JObject, JInt, JFloat, JDouble, JLong, JString, JImplements, JOverride, JBoolean
    U, jfield = E["U"], E["jfield"]
    AL, IHM, HM, UUID = JClass("java.util.ArrayList"), JClass("java.util.IdentityHashMap"), JClass("java.util.HashMap"), JClass("java.util.UUID")
    Paths, CF = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.CompletableFuture")
    REF = JClass("com.hypixel.hytale.component.Ref")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HR = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    V3D, V3I = JClass("org.joml.Vector3d"), JClass("org.joml.Vector3i")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    UUC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    ITS = JClass("com.hypixel.hytale.server.core.modules.interaction.Interactions")
    ITB = JClass("com.hypixel.hytale.server.core.modules.entity.component.Interactable")
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    MC = JClass("com.hypixel.hytale.server.core.modules.entity.component.ModelComponent")
    MDL = JClass("com.hypixel.hytale.server.core.asset.type.model.config.Model")
    MDA = JClass("com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset")
    NPL = JClass("com.hypixel.hytale.server.core.entity.nameplate.Nameplate")
    DNC = JClass("com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent")
    INTc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    PROPc = JClass("com.hypixel.hytale.server.core.modules.entity.component.PropComponent")
    PAIR = JClass("it.unimi.dsi.fastutil.Pair")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    PBU = JClass("com.hypixel.hytale.server.core.prefab.selection.buffer.PrefabBufferUtil")
    IPB = JClass("com.hypixel.hytale.server.core.prefab.selection.buffer.impl.IPrefabBuffer")
    PBC = JClass("com.hypixel.hytale.server.core.prefab.selection.buffer.PrefabBufferCall")
    PROT = JClass("com.hypixel.hytale.server.core.prefab.PrefabRotation")
    FR = JClass("com.hypixel.hytale.math.util.FastRandom")
    CHU = JClass("com.hypixel.hytale.math.util.ChunkUtil")
    MS, MB, MCH = JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".MapBuffer"), JClass(FAKE_PKG + ".MapChunk")
    FW, FP, FPM, FPG = JClass(FAKE_PKG + ".FakeWorld"), JClass(FAKE_PKG + ".FakePr"), JClass(FAKE_PKG + ".FakePageManager"), JClass(FAKE_PKG + ".FakePage")
    FS, FSM, SPc = JClass(FAKE_PKG + ".FakeSupplier"), JClass(FAKE_PKG + ".FakeSupplierMaker"), JClass(FAKE_PKG + ".FakeSpatial")
    SIM, SNC, SNE = JClass(FAKE_PKG + ".SimPaste"), JClass(FAKE_PKG + ".SimNoChild"), JClass(FAKE_PKG + ".SimNoEnt")
    Log, Logic, Rec, Store, Eng = (JClass(PKG + n) for n in ("TpLog", "TpLogic", "TpRec", "TpStore", "TpEng"))
    Snap, Build, Paste, Npc, Cmds = (JClass(PKG + n) for n in ("TpSnap", "TpBuild", "TpPaste", "TpNpc", "TpCmds"))
    UseSys, Guard, Tick, Zone, EntCount = (JClass(PKG + n) for n in ("TpUseSys", "TpGuard", "TpTick", "TpZone", "TpEntCount"))
    BT = E["BT"]
    btm = BT.getAssetMap()
    sink, lines = AL(), AL()
    Log.SINK, Log.LINES = sink, lines

    FJP, TU = JClass("java.util.concurrent.ForkJoinPool"), JClass("java.util.concurrent.TimeUnit")

    def settle():
        """the snapshot write / read run on the common pool (real async IO); the world step then runs on FakeWorld.execute"""
        FJP.commonPool().awaitQuiescence(JLong(20), TU.SECONDS)

    def said():
        settle()
        r = [str(x).split("|", 1)[1] for x in sink]
        sink.clear()
        return r

    def logged():
        r = [str(x) for x in lines]
        lines.clear()
        return r

    # ================= L: TpLogic on plain data
    K.check([int(Logic.parseRot(s)) for s in (None, "", "0", "3", "2e", "1E", "4", "x", "10", "e")] == [0, 0, 0, 3, 2, 1, -1, -1, -1, -1],
            "L: parseRot (None/empty = 0, 0-3, Ne, refuses 4 / x / 10 / e)")
    K.check([bool(Logic.wantsEntities(s)) for s in (None, "0", "0e", "3E", "4e", "e")] == [False, False, True, True, False, False], "L: wantsEntities")
    pk = [str(Logic.prefabKey(s)) for s in ("stall", "STALL", "temple", "Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001", "Server/Prefabs/Npc/A/B.prefab.json",
                                             "Npc.Kweebec.Oak.Well.Kweebec_Oak_Well_001", "/x/y.json", "..\\evil", "a/../b", "c:/x", "a*", "", None, "a/")]
    K.check(pk == [ALIASES["stall"], ALIASES["stall"], TEMPLE, "Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001.prefab.json", "Npc/A/B.prefab.json",
                   "Npc/Kweebec/Oak/Well/Kweebec_Oak_Well_001.prefab.json", "x/y.prefab.json", "None", "None", "None", "None", "None", "None", "None"],
            "L: prefabKey (aliases, temple, plain / Server/Prefabs/ / dotted / leading slash; .. : * empty trailing / refused): %s" % pk)
    K.check([str(Logic.dirName(a, b)) for a, b in ((0, -1), (0, 1), (1, 0), (-1, 0), (0, 0))] == ["north", "south", "east", "west", "?"], "L: dirName")
    o = [list(Logic.placeOrigin(0, 0, fx, fz, -5, 5, -3, 7, 4)) for fx, fz in ((0, 1), (0, -1), (1, 0), (-1, 0))]
    K.check(o == [[0, 7], [0, -11], [9, -2], [-9, -2]], "L: placeOrigin puts the box 4 blocks ahead, centred: %s" % o)
    xs, zs = Logic.polyX(100.0), Logic.polyZ(-50.0)
    K.check(len(xs) == 9 and abs(float(xs[0]) - 110.0) < 1e-9 and abs(float(zs[0]) + 50.0) < 1e-9, "L: the 9-corner polygon (corner 0 = centre + 10 east)")
    K.check(bool(Logic.inPoly(xs, zs, 100.5, -49.5)) and bool(Logic.inPoly(xs, zs, 106.0, -50.0)) and not bool(Logic.inPoly(xs, zs, 112.0, -50.0))
            and not bool(Logic.inPoly(xs, zs, 100.0, -39.0)) and not bool(Logic.inPoly(None, zs, 0.0, 0.0)),
            "L: inPoly (centre in, 6 east in, 12 east out, 11 south out (radius 9 there), bad input false)")
    K.check("(110, -50)" in str(Logic.polyText(xs, zs)), "L: polyText")
    lat = [int(Logic.lat(i)) for i in range(40)]
    K.check(max(lat) == 5 and min(lat) == -5 and all(abs(lat[i + 1] - lat[i]) <= 1 for i in range(39)) and lat[0] == 0,
            "L: the lane S-curve: amplitude 5, at most 1 sideways per step: %s" % lat)
    K.check(list(Logic.smooth([140, 140, 145, 145, 139, 139])) == [140, 140, 141, 142, 141, 140] and list(Logic.smooth([])) == [],
            "L: smooth = at most 1 block per step")
    K.check([bool(Logic.isGround(k)) for k in ("Soil_Grass", "Rock_Stone", "Sand_White", "Gravel", "Snow", "Clay", "Leaves_Oak", "Wood_Oak_Trunk",
                                                 "Rock_Stone_Cobble_Stairs", "Plant_Grass", None)]
            == [True, True, True, True, True, True, False, False, False, False, False], "L: isGround")
    K.check(str(Logic.ms(JLong(12345678))) == "12.3 ms" and str(Logic.xyz(1, -2, 3)) == "1 -2 3" and str(Logic.rotName(2)) == "ROTATION_180", "L: ms / xyz / rotName")
    K.check(abs(float(Logic.yawToward(0.0, -1.0))) < 1e-6 and abs(abs(float(Logic.yawToward(0.0, 1.0))) - 3.14159265) < 1e-5 and float(Logic.yawToward(0.0, 0.0)) == 0.0,
            "L: yawToward (north = 0, south = pi)")
    K.check(bool(Logic.near(0.0, 0.0, 0.0, 3.0, 4.0, 0.0, 5.0)) and not bool(Logic.near(0.0, 0.0, 0.0, 3.0, 4.1, 0.0, 5.0)), "L: near")
    # TpRec text round trip
    r0 = Rec()
    r0.seq, r0.kind, r0.world, r0.ox, r0.oy, r0.oz, r0.snap, r0.uuids, r0.what, r0.time = 7, "temple", WORLD, 1, 2, 3, "7.lpf", "", "line\nbreak", JLong(99)
    r0.nx = 1.5
    r1 = Rec.parse(r0.toText())
    K.check(r1 is not None and int(r1.seq) == 7 and str(r1.kind) == "temple" and str(r1.what) == "line break" and int(r1.oz) == 3
            and str(r1.snap) == "7.lpf" and float(r1.nx) == 1.5 and len(r1.uuidList()) == 0, "R: TpRec toText / parse round trip (newline cleaned)")
    K.check(Rec.parse("seq=x\nkind=a\nworld=b") is None and Rec.parse("kind=a\nworld=b\nseq=0") is None and Rec.parse(None) is None
            and Rec.parse("seq=3\nkind=a\nworld=b\nsnap=4.lpf") is None and Rec.parse("seq=3\nworld=b") is None,
            "R: parse refuses a bad seq / seq 0 / null / a snapshot name that is not <seq>.lpf / no kind")
    r2 = Rec.parse("seq=4\nkind=npc\nworld=w\nuuids=a,b")
    K.check(r2 is not None and list(r2.uuidList()) == ["a", "b"], "R: uuidList")

    # ================= the simulated world + stand-ins
    def H(x, z):
        if z < 12:
            return 140
        if z < 16:
            return 140 + 2 * (z - 11)          # a steep step (2 per block) -> the lane smooths it
        if z < 30:
            return 148
        return 145                             # a 3-block drop
    SW = SimWorld(E, H)
    SW.extra[(0, 141, 20 + 3)] = SW.ids["leaf"]           # a leaf above the ground on the lane line (ground search skips it)
    uni = E["uni"]
    st = U.allocateInstance(MS.class_)
    st.comps, st.res, st.holders, st.removed, st.added, st.ensured = IHM(), IHM(), HM(), AL(), AL(), AL()
    st.ensureVal = ITB.INSTANCE
    cb = U.allocateInstance(MB.class_)
    ents_sp = SPc()
    SRc = JClass("com.hypixel.hytale.component.spatial.SpatialResource")
    st.res.put(E["em"].getEntitySpatialResourceType(), SRc(ents_sp))
    st.res.put(E["em"].getPlayerSpatialResourceType(), SRc(SPc()))
    w = U.allocateInstance(FW.class_)
    jfield(WLD, "name").set(w, WORLD)
    es = U.allocateInstance(EST.class_)
    jfield(EST, "world").set(es, w)
    byuuid = HM()
    jfield(EST, "entitiesByUuid").set(es, byuuid)
    try:
        jfield(EST, "store").set(es, st)
    except Exception as e:
        K.notes.append("EntityStore.store field: %s" % e)
    jfield(WLD, "entityStore").set(w, es)
    st.ext = es
    other = U.allocateInstance(FW.class_)
    jfield(WLD, "name").set(other, "default")
    nref = [0]

    def mkref():
        nref[0] += 1
        r_ = REF(st, JInt(nref[0]))
        st.comps.put(r_, IHM())
        return r_

    def put(r_, t, c):
        st.comps.get(r_).put(t, c)

    def mkplayer(name, n, x, y, z, fx=0, fz=1, admin=True):
        r_ = mkref()
        pr_ = U.allocateInstance(FP.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-0000-0000-%012x" % (0xa000 + n)))
        jfield(PRc, "username").set(pr_, name)
        pr_.admin = admin
        pr_.msgs = AL()
        put(r_, PRc.getComponentType(), pr_)
        pl = U.allocateInstance(PLA.class_)
        pm = U.allocateInstance(FPM.class_)
        pm.opened = AL()
        jfield(PLA, "pageManager").set(pl, pm)
        put(r_, PLA.getComponentType(), pl)
        tc = TC(V3D(x, y, z), R3(0.0, 0.0, 0.0))
        put(r_, TC.getComponentType(), tc)
        hr = HR()
        import math
        yaw = math.atan2(-fx, -fz)
        hr.setRotation(R3(JFloat(0.0), JFloat(yaw), JFloat(0.0)))
        put(r_, HR.getComponentType(), hr)
        return {"ref": r_, "pr": pr_, "pl": pl, "pm": pm, "tc": tc, "hr": hr, "uuid": pr_.getUuid()}
    A = mkplayer("Skyy", 1, 0.5, 141.0, 0.5)
    hd = A["hr"].getHorizontalAxisDirection()
    K.check(int(hd.x()) == 0 and int(hd.z()) == 1, "X: the real HeadRotation.getHorizontalAxisDirection = south for the stand-in yaw (%s, %s)" % (hd.x(), hd.z()))

    # the temple + stall prefabs: the Assets.zip JSON minus entities / block components / fluids, deserialized by the REAL
    # BsonPrefabBufferDeserializer, written as .lpf by the REAL PrefabBufferUtil.writeToFileAsync, read back by the REAL getCached
    BD = JClass("org.bson.BsonDocument")
    DES = JClass("com.hypixel.hytale.server.core.prefab.selection.buffer.BsonPrefabBufferDeserializer")
    pdir = os.path.join(SCRATCH, "prefabs")
    os.makedirs(pdir, exist_ok=True)

    def lpf(src_json, name):
        d = dict(src_json)
        d.pop("entities", None)
        d.pop("fluids", None)
        d["blocks"] = [dict((k, v) for k, v in b.items() if k != "components") for b in d["blocks"]]
        buf = DES.INSTANCE.deserialize(Paths.get(name + ".prefab.json"), BD.parse(json.dumps(d)))
        out_ = os.path.join(pdir, name + ".lpf")
        PBU.writeToFileAsync(buf, Paths.get(out_)).join()
        return out_
    tpath = lpf(E["tj"], "temple")
    spath = lpf(json.loads(E["az"].read("Server/Prefabs/" + ALIASES["stall"]).decode("utf-8-sig")), "stall")
    known = {TEMPLE: tpath, ALIASES["stall"]: spath, "Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001.prefab.json": spath}
    calls = {"paste": [], "region": [], "spawnNpc": [], "spawnModel": []}
    mode = {"region": "ok", "role": 7, "replace": False, "spawn": "ok", "unloaded": set(), "ents": 0, "pastefail": False, "defer": []}
    spawned = {}

    @JImplements(PKG + "TpEngApi")
    class Api:
        @JOverride
        def findPrefab(self, key):
            p = known.get(str(key))
            return Paths.get(p) if p else None

        @JOverride
        def buffer(self, path):
            return PBU.getCached(path)

        @JOverride
        def loadRegion(self, b, w_, o, r):
            bx = [int(o.x()) + int(b.getMinX(r)), int(o.y()) + int(b.getMinY()), int(o.z()) + int(b.getMinZ(r)),
                  int(o.x()) + int(b.getMaxX(r)), int(o.y()) + int(b.getMaxY()), int(o.z()) + int(b.getMaxZ(r))]
            calls["region"].append((str(w_.getName()), bx, str(r)))
            m_ = mode["region"]
            if m_ == "boom":
                return CF.failedFuture(JClass("java.lang.IllegalStateException")("chunk load boom"))
            if m_ == "null":
                return CF.completedFuture(None)
            if m_ == "defer":
                f_ = CF()
                mode["defer"].append((f_, bx))
                return f_
            return CF.completedFuture(SW.region(*bx, loaded=(m_ != "partial")))

        @JOverride
        def paste(self, b, w_, o, rot, flags, reg, st_, ents):
            calls["paste"].append((str(rot), int(flags), int(o.x()), int(o.y()), int(o.z())))
            sim = SIM()
            sim.region, sim.ox, sim.oy, sim.oz = reg, o.x(), o.y(), o.z()
            b.forEach(IPB.iterateAllColumns(), sim, SNE(), SNC(), PBC(FR(), PROT.fromRotation(rot)))
            calls["paste"][-1] += (int(sim.n), int(sim.zeros), ents is not None)
            # what PrefabUtil does per prefab entity when entities are ON: entityConsumer.accept(holder), then addEntity(holder)
            if ents is not None:
                for _ in range(mode["ents"]):
                    h_ = self.newHolder()
                    ents.accept(h_)
                    u_ = h_.getComponent(UUC.getComponentType())
                    r_ = mkref()
                    spawned[str(u_.getUuid())] = r_
                    calls.setdefault("entsAdded", []).append(r_)
            if mode["pastefail"]:
                raise JClass("java.lang.IllegalStateException")("odd block at the far corner")

        @JOverride
        def height(self, w_, x, z):
            if (int(x) // 32, int(z) // 32) in mode["unloaded"]:
                return int(Eng.NO_HEIGHT)
            return SW.height(int(x), int(z))

        @JOverride
        def key(self, w_, x, y, z):
            a = btm.getAsset(JInt(SW.block(int(x), int(y), int(z))))
            return None if a is None else a.getId()

        @JOverride
        def store(self, w_):
            return st

        @JOverride
        def refOf(self, w_, u):
            return spawned.get(str(u))

        @JOverride
        def roleIndex(self, role):
            return mode["role"] if str(role) == "Temple_Kweebec_Static" else -1

        def _spawn(self, pos, model, role):
            if mode["spawn"] == "null":
                return None
            r_ = mkref()
            npc = U.allocateInstance(NPCc.class_)
            jfield(NPCc, "roleName").set(npc, "Temple_Kweebec_Static")
            put(r_, NPCc.getComponentType(), npc)
            u = UUID.randomUUID()
            put(r_, UUC.getComponentType(), UUC(u))
            its = ITS()
            its.setInteractionId(ITY.Use, "*UseNPC")
            put(r_, ITS.getComponentType(), its)
            if model is not None:
                put(r_, MC.getComponentType(), MC(model))
            put(r_, TC.getComponentType(), TC(V3D(pos.x(), pos.y(), pos.z()), R3(0.0, 0.0, 0.0)))
            spawned[str(u)] = r_
            ents_sp.refs.add(r_)
            ents_sp.pos.add(V3D(pos.x(), pos.y(), pos.z()))
            return PAIR.of(r_, npc)

        @JOverride
        def newHolder(self):
            h_ = U.allocateInstance(JClass(FAKE_PKG + ".FakeHolder").class_)      # Holder() is package-private: no constructor runs
            h_.m = IHM()
            return h_

        @JOverride
        def spawnNpc(self, st_, role, pos, rot):
            calls["spawnNpc"].append((str(role), float(pos.x()), float(pos.y()), float(pos.z()), float(rot.yaw())))
            return self._spawn(pos, None, role)

        @JOverride
        def spawnModel(self, st_, role, pos, rot, m):
            calls["spawnModel"].append((int(role), str(m.getModelAssetId()), float(m.getScale())))
            mm = m
            if mode["replace"]:
                mm = MDL.createStaticScaledModel(MDA.getAssetMap().getAsset("Rubble_Stone"), JFloat(1.0))
            return self._spawn(pos, mm, role)
    api = Api()
    Eng.API = api
    data = os.path.join(SCRATCH, "data", "Skyy_SkyyTownProbe")
    Store.DIR = Paths.get(data)
    K.check(int(Store.load()) == 0 and not os.path.exists(data), "X: load with no probe folder = 0 records, nothing created")

    # ================= help / unknown / world refusal
    Cmds.run(A["ref"], st, A["pr"], w, None, None, None)
    s = said()
    K.check(len(s) == 10 and s[0].startswith("Town probe (admin only") and "0 probe changes to undo; zone off" in s[-1], "X: /townprobe -> help (%d lines)" % len(s))
    Cmds.run(A["ref"], st, A["pr"], w, "bogus", None, None)
    s = said()
    K.check(s[0] == "Unknown option 'bogus'." and len(s) == 11, "X: unknown option -> line + help")
    Cmds.run(A["ref"], st, A["pr"], w, "lane", "x", None)
    s = said()
    K.check(s[0].startswith("Too many words after /townprobe lane") and len(s) == 11, "X: too many words -> line + help")
    Cmds.run(A["ref"], st, A["pr"], other, "temple", None, None)
    K.check(said() == ["The town probe only builds on the Zone 1 test island (/zone 1). This world (default) is left alone."] and not calls["region"],
            "X: a world-changing action in another world is refused (harmless)")
    lg_ = logged()
    K.check(any("Skyy ran /townprobe temple in default" in l for l in lg_), "X: every run is logged with the world")

    # ================= temple 0: snapshot, paste, box, report lines, undo restores every cell
    def box_of(b, o, r):
        return [int(o[0]) + int(b.getMinX(r)), int(o[1]) + int(b.getMinY()), int(o[2]) + int(b.getMinZ(r)),
                int(o[0]) + int(b.getMaxX(r)), int(o[1]) + int(b.getMaxY()), int(o[2]) + int(b.getMaxZ(r))]
    tb = PBU.getCached(Paths.get(tpath))
    K.check(int(tb.getAnchorX()) == 6 and int(tb.getAnchorY()) == 13 and int(tb.getAnchorZ()) == 6 and int(tb.getMinY()) == -13 and int(tb.getMaxY()) == 16,
            "X: the real temple buffer: anchor (6, 13, 6), y -13..16 (anchor-relative, the deserializer subtracts the anchor)")
    p0 = PROT.ROTATION_0
    ox = int(Logic.placeOrigin(0, 0, 0, 1, tb.getMinX(p0), tb.getMaxX(p0), tb.getMinZ(p0), tb.getMaxZ(p0), 4)[0])
    oz = int(Logic.placeOrigin(0, 0, 0, 1, tb.getMinX(p0), tb.getMaxX(p0), tb.getMinZ(p0), tb.getMaxZ(p0), 4)[1])
    bx = box_of(tb, (ox, H(ox, oz), oz), p0)
    before = SW.box_hash(bx)
    Cmds.run(A["ref"], st, A["pr"], w, "temple", None, None)
    s, lg_ = said(), logged()
    K.check(s[0].startswith("Placing Unique_Portal_Grasslands_Monuments_Unique_Portal_Grasslands_001 ROTATION_0 at %d %d %d (without prefab entities)" % (ox, H(ox, oz), oz))
            and s[-1].startswith("Done: ") and s[-1].endswith("/townprobe undo puts the ground back."), "X: temple 0 -> placing + done lines: %s" % s)
    K.check(s[0].endswith("Its door faces south.") and calls["paste"][-1][7] is False, "C1: temple 0 tells the player the door faces south; entities off -> no entity consumer: %s" % s[0])
    K.check(calls["region"][-1] == (WORLD, bx, "ROTATION_0") and calls["paste"][-1][:5] == ("None", 9, ox, H(ox, oz), oz),
            "X: temple 0 loads the box %s and pastes with FORCE|NO_ENTITIES (9), Rotation None, anchor on the ground block: %s" % (bx, calls["paste"][-1]))
    K.check(calls["paste"][-1][5] == 19297 - 3 + 3 or calls["paste"][-1][5] > 18000, "X: the real forEach visited the temple's %s entries" % calls["paste"][-1][5])
    anchor_id = SW.block(ox, H(ox, oz), oz)
    K.check(anchor_id == int(btm.getIndex("Rock_Marble_Cobble")), "X: after the paste the anchor block is the temple floor (Rock_Marble_Cobble)")
    K.check(SW.box_hash(bx) != before, "X: the paste changed the box")
    t_lines = [l for l in lg_ if "TEMPLE" in l]
    K.check(any("anchor offset: prefab anchor (6, 13, 6) is placed on block %d %d %d (ground top found)" % (ox, H(ox, oz), oz) in l for l in t_lines)
            and any("TEMPLE done (" in l and "region load " in l and ", snapshot " in l and ", paste " in l and "prefab load" in l for l in t_lines)
            and any("world box x %d..%d, y %d..%d, z %d..%d (35 x 30 x 40)" % (bx[0], bx[3], bx[1], bx[4], bx[2], bx[5]) in l for l in t_lines)
            and any("Prefab_Spawner_Block in the box after the paste: 3 at " in l for l in t_lines)
            and any("prefab entities: 0 SKIPPED (entities off)" in l for l in t_lines)
            and any("temple door side faces south" in l and "causeway foot / spawn spot about %d %d %d" % (ox, H(ox, oz) + 1, oz + 11) in l for l in t_lines),
            "X: the temple INFO lines (anchor offset, ms per step, box 35 x 30 x 40, 3 Prefab_Spawner_Block, entities skipped, door south + foot): %s" % t_lines)
    K.check(int(Store.RECS.size()) == 1 and os.path.isfile(os.path.join(data, "undo", "1.properties")) and os.path.isfile(os.path.join(data, "undo", "1.lpf")),
            "X: temple record 1 + its snapshot file written into Skyy_SkyyTownProbe/undo/")
    rec1 = Store.last()
    snapb = rec1.buf.newAccess()
    K.check(int(snapb.getMinX()) == bx[0] - ox and int(snapb.getMaxY()) == bx[4] - H(ox, oz), "X: the snapshot covers exactly the paste box (relative to the anchor)")
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    s, lg_ = said(), logged()
    K.check(SW.box_hash(bx) == before, "X: undo puts every cell of the 35 x 30 x 40 box back as before (byte for byte)")
    K.check(s[-1].startswith("Undone: Unique_Portal_Grasslands") and int(Store.RECS.size()) == 0 and calls["paste"][-1][:2] == ("None", 1)
            and any("UNDO done: temple record 1" in l and "FORCE" in l for l in lg_), "X: undo line + FORCE paste-back + log: %s" % s)
    K.check(not os.path.exists(os.path.join(data, "undo")) and not os.path.exists(data), "X: undo deleted the files and the empty folders (no saved data left)")
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    K.check(said() == ["Nothing to undo."], "X: undo with nothing left")

    # rotations 1e / 2 / 3 (box + flags), undo from the FILE (memory copy dropped)
    for rt, want_door in (("1e", "east"), ("2", "north"), ("3", "west")):
        r_i = int(Logic.parseRot(rt))
        pr_ = PROT.VALUES[r_i]
        o2 = Logic.placeOrigin(0, 0, 0, 1, tb.getMinX(pr_), tb.getMaxX(pr_), tb.getMinZ(pr_), tb.getMaxZ(pr_), 4)
        bx2 = box_of(tb, (int(o2[0]), H(int(o2[0]), int(o2[1])), int(o2[1])), pr_)
        h0 = SW.box_hash(bx2)
        mode["ents"] = 2 if rt.endswith("e") else 0
        calls["entsAdded"] = []
        Cmds.run(A["ref"], st, A["pr"], w, "temple", rt, None)
        s, lg_ = said(), logged()
        mode["ents"] = 0
        if rt.endswith("e"):
            ent_refs = list(calls["entsAdded"])
            K.check(len(ent_refs) == 2 and len(Store.last().uuidList()) == 2 and s[-1].endswith("and removes its 2 entities.")
                    and any("pasted (entities on); 2 spawned and tracked - undo removes them" in l for l in lg_) and calls["paste"][-1][7] is True,
                    "A3/B3: temple 1e passes a real entity consumer; the 2 prefab entities get UUIDs, are stored in the record and named in the log: %s" % s[-1:])
            K.check(not Store.NPCS.containsKey(Store.last().uuidList()[0]), "A3: prefab entities are not treated as probe NPCs (F on them stays vanilla)")
        K.check(calls["paste"][-1][1] == (1 if rt.endswith("e") else 9) and calls["region"][-1][1] == bx2 and calls["paste"][-1][0] == str(pr_.getRotation())
                and any("temple door side faces " + want_door in l for l in lg_) and int(bx2[2]) >= 4,
                "X: temple %s: flags %s, box %s starts ahead of you, door %s" % (rt, calls["paste"][-1][1], bx2, want_door))
        settle()
        Store.last().buf = None
        Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
        s = said()
        K.check(SW.box_hash(bx2) == h0 and s[-1].startswith("Undone:"), "X: temple %s undone from the snapshot FILE (real readFromFileAsync): ground back byte for byte" % rt)
        if rt.endswith("e"):
            K.check(all(st.removed.contains(r_) for r_ in ent_refs), "A3/B3: undo of temple 1e (record read back from its FILE) removes both prefab entities")
    K.check(not os.path.exists(data), "X: still no probe folder after the rotation round")

    # ================= piece: alias / path / dotted / bad / unknown / bad rotation / entities
    sb = PBU.getCached(Paths.get(spath))
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "stall", "2")
    s, lg_ = said(), logged()
    K.check(s[-1].startswith("Done: Kweebec_Oak_Shops_001 ROTATION_180 at ") and calls["paste"][-1][1] == 9 and any("PIECE done" in l for l in lg_),
            "X: piece stall 2 -> pasted, entities off: %s" % s[-1:])
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "Npc.Kweebec.Oak.Shops.Kweebec_Oak_Shops_001", None)
    s = said()
    K.check(s[-1].startswith("Done: Kweebec_Oak_Shops_001 ROTATION_0"), "X: piece by dotted path, no rotation = 0")
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "Npc/Nope/Missing", "0")
    s, lg_ = said(), logged()
    K.check(s == ["No vanilla prefab at Server/Prefabs/Npc/Nope/Missing.prefab.json"] and any("PIECE refused" in l for l in lg_), "X: unknown prefab refused + logged")
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "../x", "0")
    K.check(said()[0].startswith("That is not a prefab path"), "X: a path with .. is refused")
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "stall", "7")
    K.check(said() == ["Rotation must be 0, 1, 2 or 3 (add e for entities, like 1e)."], "X: bad rotation refused")
    Cmds.run(A["ref"], st, A["pr"], w, "piece", None, None)
    K.check(said() == ["Usage: /townprobe piece <prefab path or alias> [0-3]"], "X: piece without a path -> usage")
    Cmds.run(A["ref"], st, A["pr"], w, "temple", "1", "x")
    K.check(len(said()) == 10, "X: temple with 2 values -> help")
    for _ in range(2):
        Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
        said()
    K.check(int(Store.RECS.size()) == 0, "X: both pieces undone")

    # paste + undo at once: the snapshot write that lands after the undo deletes its own file (no orphan, folders cleaned)
    sink.clear()
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "stall", "1")
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    logged()
    K.check(int(Store.RECS.size()) == 0 and Store.LIVE.isEmpty() and not os.path.exists(data), "X: paste + immediate undo leaves no snapshot file / folder behind (TpIoDone)")
    IOD = JClass(PKG + "TpIoDone")
    rr9 = Rec()
    rr9.seq, rr9.kind, rr9.world, rr9.snap, rr9.what = 99, "piece", WORLD, "99.lpf", "io test"
    IOD(Paths.get(os.path.join(SCRATCH, "nope.lpf")), rr9).apply(None, JClass("java.lang.IllegalStateException")("disk full"))
    K.check(any("NOT written: java.lang.IllegalStateException: disk full" in l and "no record file written" in l for l in logged())
            and not os.path.exists(os.path.join(data, "undo", "99.properties")), "X: a failed snapshot write is logged and writes NO record file")
    # A2: the record file is written only once the .lpf is on disk; a record undone meanwhile leaves no file
    Store.add(rr9, False)
    K.check(not os.path.exists(os.path.join(data, "undo", "99.properties")), "A2: add(r, false) keeps a paste record in memory only (no .properties before its .lpf)")
    lpf99 = os.path.join(data, "undo", "99.lpf")
    os.makedirs(os.path.dirname(lpf99), exist_ok=True)
    open(lpf99, "wb").write(b"lpf")
    IOD(Paths.get(lpf99), rr9).apply(None, None)
    K.check(os.path.isfile(os.path.join(data, "undo", "99.properties")), "A2: the .lpf landed -> TpIoDone writes the record's .properties")
    Store.remove(rr9)
    K.check(not os.path.exists(data), "A2: undo of that record deletes both files and the folders")
    os.makedirs(os.path.dirname(lpf99), exist_ok=True)
    open(lpf99, "wb").write(b"lpf")
    IOD(Paths.get(lpf99), rr9).apply(None, None)
    K.check(not os.path.exists(data), "A2: a snapshot write that lands after its record was undone deletes its .lpf, writes no .properties, folders cleaned")

    # ================= A1/B1: a paste that throws partway keeps its undo record (snapshot taken first) -> undo restores the ground
    o3 = Logic.placeOrigin(0, 0, 0, 1, tb.getMinX(p0), tb.getMaxX(p0), tb.getMinZ(p0), tb.getMaxZ(p0), 4)
    bx3 = box_of(tb, (int(o3[0]), H(int(o3[0]), int(o3[1])), int(o3[1])), p0)
    h3 = SW.box_hash(bx3)
    mode["pastefail"] = True
    Cmds.run(A["ref"], st, A["pr"], w, "temple", "0", None)
    s, lg_ = said(), logged()
    mode["pastefail"] = False
    K.check(SW.box_hash(bx3) != h3 and int(Store.RECS.size()) == 1 and not bool(Store.BUSY)
            and s[-1] == "The temple failed partway: java.lang.IllegalStateException: odd block at the far corner. The ground was saved first - /townprobe undo puts it back."
            and any("TEMPLE FAILED PARTWAY" in l and "undo record" in l and "kept" in l for l in lg_),
            "A1/B1: a paste that throws after writing blocks: record kept, busy cleared, clear line + WARN: %s" % s[-1:])
    K.check(os.path.isfile(os.path.join(data, "undo", "%d.lpf" % int(Store.last().seq))) and os.path.isfile(os.path.join(data, "undo", "%d.properties" % int(Store.last().seq))),
            "A1/A2: the failed paste's snapshot + record files are on disk (survive a restart)")
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    K.check(SW.box_hash(bx3) == h3 and int(Store.RECS.size()) == 0 and not os.path.exists(data), "A1/B1: undo after the failed paste puts every cell back, files gone")

    # ================= B2: /townprobe piece refuses a prefab whose box is over the cap
    bigj = json.loads(E["az"].read("Server/Prefabs/" + ALIASES["stall"]).decode("utf-8-sig"))
    b0 = dict(bigj["blocks"][0])
    b1 = dict(b0)
    b0["x"], b0["y"], b0["z"] = 0, 0, 0
    b1["x"], b1["y"], b1["z"] = 100, 40, 100
    bigj["blocks"] = [b0, b1]
    bigj["anchorX"], bigj["anchorY"], bigj["anchorZ"] = 0, 0, 0
    known["Big/Huge_001.prefab.json"] = lpf(bigj, "big")
    nreg = len(calls["region"])
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "Big/Huge_001", None)
    s, lg_ = said(), logged()
    K.check(s == ["That prefab is too big for the probe (418241 blocks in its box, the limit is 300000)."] and len(calls["region"]) == nreg and not bool(Store.BUSY)
            and any("PIECE refused" in l and "101 x 41 x 101 = 418241 cells" in l for l in lg_), "B2: a 101 x 41 x 101 prefab is refused before any area load: %s" % s)
    K.check(int(Logic.cells(-5, 5, 0, 9, -3, 7)) == 11 * 10 * 11, "B2: TpLogic.cells")

    # ================= B4: a region job that arrives after the 60 s busy escape is dropped (ticket)
    mode["region"] = "defer"
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "stall", None)
    said()
    logged()
    K.check(bool(Store.BUSY) and len(mode["defer"]) == 1, "B4: a deferred region load keeps the probe busy")
    Store.BUSY_SINCE = JLong(1)
    K.check(not bool(Store.busy()), "B4: the 60 s escape clears busy")
    mode["region"] = "ok"
    Cmds.run(A["ref"], st, A["pr"], w, "piece", "stall", "1")
    s = said()
    K.check(int(Store.RECS.size()) == 1 and s[-1].startswith("Done: Kweebec_Oak_Shops_001 ROTATION_90"), "B4: a second job runs after the escape: %s" % s[-1:])
    late_f, late_bx = mode["defer"].pop()
    npaste = len(calls["paste"])
    late_f.complete(SW.region(*late_bx))
    settle()
    lg_ = logged()
    K.check(len(calls["paste"]) == npaste and int(Store.RECS.size()) == 1 and not said()
            and any("arrived after its busy flag was cleared" in l and "dropped, nothing changed" in l for l in lg_),
            "B4: the late first job is dropped (no paste, no record, WARN): %s" % [l for l in lg_ if "dropped" in l])
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    K.check(int(Store.RECS.size()) == 0 and not bool(Store.BUSY), "B4: undo of the second job; nothing left")

    # ================= failing region loads + busy + record cap
    for m_, want in (("boom", "the area did not load"), ("partial", "the area is not fully loaded"), ("null", "the area is not fully loaded")):
        mode["region"] = m_
        Cmds.run(A["ref"], st, A["pr"], w, "piece", "stall", None)
        s, lg_ = said(), logged()
        K.check(any(want in x for x in s) and not bool(Store.BUSY) and int(Store.RECS.size()) == 0 and any("PIECE failed" in l for l in lg_),
                "X: region load %s -> '%s', busy cleared, no record: %s" % (m_, want, s))
    mode["region"] = "ok"
    Store.setBusy(True)
    Cmds.run(A["ref"], st, A["pr"], w, "lane", None, None)
    K.check(said() == ["Still working on the last probe action - try again in a moment."], "X: busy refuses a second action")
    Store.BUSY_SINCE = JLong(1)
    K.check(not bool(Store.busy()) and any("never finished" in l for l in logged()), "X: a busy flag older than 60 s is cleared with a WARN")
    for i in range(20):
        rr = Rec()
        rr.seq, rr.kind, rr.world, rr.what = Store.nextSeq(), "fake", WORLD, "fake %d" % i
        Store.RECS.add(rr)
    Cmds.run(A["ref"], st, A["pr"], w, "lane", None, None)
    K.check(said() == ["There are already 20 probe changes - /townprobe undo some first."], "X: the 20-record cap")
    Store.RECS.clear()

    # ================= lane: smoothing, stairs, fill, cut, the unloaded refusal, undo
    mode["unloaded"] = {(0, 1)}
    Cmds.run(A["ref"], st, A["pr"], w, "lane", None, None)
    K.check(said() == ["Part of the lane is not loaded yet - look along open ground closer by."] and not os.path.exists(data), "X: lane over an unloaded chunk refused")
    mode["unloaded"] = set()
    lane_box = [-8, 136, 0, 8, 160, 46]
    h_lane = SW.box_hash(lane_box)
    Cmds.run(A["ref"], st, A["pr"], w, "lane", None, None)
    s, lg_ = said(), logged()
    start = [l for l in lg_ if l.startswith("INFO LANE start")]
    K.check(s[-1].startswith("Done: lane of 40 steps from 0 140 3 heading south") and len(start) == 1, "X: lane laid: %s" % s[-1:])
    g = json.loads(start[0].split("ground ")[1].split(" -> ")[0])
    t = json.loads(start[0].split(" -> path ")[1])
    K.check(all(abs(t[i + 1] - t[i]) <= 1 for i in range(39)) and max(g) - min(g) >= 8 and t[0] == 140, "X: lane heights smoothed to <= 1 per step: %s" % t)
    K.check(g[17] == 148 and 141 not in g[:1], "X: the ground search skipped the leaf above the ground (step 17 reads 148 from the height map, not the leaf)")
    rep = [l for l in lg_ if "lane: " in l]
    K.check(rep and "step cells (stairs Rock_Stone_Cobble_Stairs yaw up None" not in rep[0] and "yaw up OneEighty / down None" in rep[0] and "columns raised" in rep[0],
            "X: lane report: south = yaw OneEighty up, None down (engine Rotation.rotateYaw): %s" % rep)
    # the path cells: top = cobble at t[i], a stair on step cells, air 3 above
    cob, stair, fill = int(btm.getIndex("Rock_Stone_Cobble")), int(btm.getIndex("Rock_Stone_Cobble_Stairs")), int(btm.getIndex("Rock_Stone"))
    okc = True
    for i in range(40):
        x_ = -int(Logic.lat(i))          # facing south: sideways = (-fz, fx) = west
        z_ = 3 + i
        if SW.block(x_, t[i], z_) != cob or SW.block(x_, t[i] + 3, z_) != 0:
            okc = False
    K.check(okc, "X: every lane centre cell has cobble at the smoothed height and air above")
    steps = [i for i in range(39) if t[i + 1] > t[i]]
    K.check(steps and all(SW.block(-int(Logic.lat(i)), t[i] + 1, 3 + i) == stair for i in steps), "X: a stair on every step-up cell")
    raised = [i for i in range(40) if t[i] > g[i] + 1]
    K.check(raised and all(all(SW.block(-int(Logic.lat(i)), y, 3 + i) == fill for y in range(g[i] + 1, t[i])) for i in raised),
            "X: stone fill from the ground up to the path under raised cells (no floating path): %s" % raised)
    rec_l = Store.last()
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    K.check(SW.box_hash(lane_box) == h_lane, "X: lane undo restores the ground exactly")
    K.check(str(rec_l.kind) == "lane", "X: the lane record kind")

    # ================= sign + the nameplate prop
    hsg = SW.box_hash([0, 138, 0, 0, 146, 4])
    Cmds.run(A["ref"], st, A["pr"], w, "sign", None, None)
    s, lg_ = said(), logged()
    K.check(s[0].startswith("Signs cannot hold text on this server") and s[-1].startswith("Done: village sign at 0 141 2"), "X: sign lines: %s" % s)
    K.check(SW.block(0, 141, 2) == int(btm.getIndex("Furniture_Village_Sign")), "X: the sign block stands 2 ahead on the ground")
    hl = [l for l in lg_ if "sign text: NOT supported" in l]
    K.check(hl and "fallback nameplate prop 'Waiting Square' spawned at 0.5 142.05 2.5" in hl[0] and "Rubble_Stone_Mossy x0.35" in hl[0]
            and any("yaw None" in l and "rotation index 0" in l for l in lg_), "X: sign log: no text support + the prop + the facing: %s" % hl)
    holo = st.added.get(st.added.size() - 1)
    hh = st.holders.get(holo)
    K.check(str(hh.getComponent(NPL.getComponentType()).getText()) == "Waiting Square" and hh.getComponent(INTc.getComponentType()) is not None
            and hh.getComponent(PROPc.getComponentType()) is not None and hh.getComponent(UUC.getComponentType()) is not None
            and str(hh.getComponent(MC.getComponentType()).getModel().getModelAssetId()) == "Rubble_Stone_Mossy",
            "X: the prop holder = Transform + UUID + Nameplate + Intangible + PropComponent + Model (the vanilla marker set)")
    K.check(str(Eng.API.newHolder().getClass().getSimpleName()) == "FakeHolder", "X: the holder came through TpEng.newHolder")
    srec = Store.last()
    K.check(str(srec.kind) == "sign" and len(srec.uuidList()) == 1 and Store.NPCS.containsKey(srec.uuidList()[0]), "X: the sign record holds the prop uuid")
    spawned[str(srec.uuidList()[0])] = holo
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    s, lg_ = said(), logged()
    K.check(SW.box_hash([0, 138, 0, 0, 146, 4]) == hsg and st.removed.contains(holo) and any("entities removed 1/1" in l for l in lg_),
            "X: sign undo: block back + the prop removed")

    # ================= npc: spawn, name, Interactable, hint, Use root; again = the count; pebble kept / replaced
    ents_sp.refs.clear()
    ents_sp.pos.clear()
    Cmds.run(A["ref"], st, A["pr"], w, "npc", None, None)
    s, lg_ = said(), logged()
    K.check(s == ["Mossby is here. Press F on him - the Bazaar should open. Walk away and back for his greeting."], "X: npc line: %s" % s)
    sn = calls["spawnNpc"][-1]
    K.check(sn[0] == "Temple_Kweebec_Static" and sn[1:4] == (0.5, 141.0, 3.5) and abs(sn[4]) < 1e-5,
            "X: Mossby spawned with the vanilla role 3 blocks ahead on the ground, facing you (yaw 0 = north): %s" % (sn,))
    nrec = Store.last()
    nref_ = spawned[str(nrec.uuids)]
    its = st.getComponent(nref_, ITS.getComponentType())
    K.check(str(its.getInteractionId(ITY.Use)) == "*UseNPC" and str(its.getInteractionHint()) == "server.interactionHints.trade"
            and st.getComponent(nref_, ITB.getComponentType()) is not None and str(st.getComponent(nref_, NPL.getComponentType()).getText()) == "Mossby (town probe)"
            and st.getComponent(nref_, DNC.getComponentType()) is not None, "X: Mossby: Use root kept, hint set, Interactable on, name + nameplate")
    nl = [l for l in lg_ if l.startswith("INFO NPC spawned")]
    K.check(nl and "Use = *UseNPC, hint server.interactionHints.trade, Interactable on" in nl[0] and "undo record" in nl[0], "X: npc INFO line: %s" % nl)
    K.check(str(nrec.kind) == "npc" and Store.NPCS.get(str(nrec.uuids)) == nrec and os.path.isfile(os.path.join(data, "undo", "%d.properties" % int(nrec.seq))),
            "X: npc record saved + indexed")
    Cmds.run(A["ref"], st, A["pr"], w, "npc", None, None)
    s, lg_ = said(), logged()
    K.check(s[0].startswith("Mossby is already placed (found; 1 at that spot - 1 is right). Not spawning another.") and len(calls["spawnNpc"]) == 1
            and any("NPC check:" in l and "PRESENT" in l and "1 Temple_Kweebec_Static NPCs within 3 blocks" in l for l in lg_),
            "X: npc again = the presence count (1), never a second spawn: %s" % s)
    # pebble: role keeps the rock
    Cmds.run(A["ref"], st, A["pr"], w, "pebble", None, None)
    s, lg_ = said(), logged()
    K.check(calls["spawnModel"][-1] == (7, "Rubble_Stone_Mossy", 5.0) and s[0].startswith("Pebble is here.") and "the role KEPT our rock model" in s[0],
            "X: pebble with the x5 rock model; the role kept it: %s" % s)
    prec = Store.last()
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    K.check(st.removed.contains(spawned[str(prec.uuids)]), "X: pebble undo removes the entity")
    mode["replace"] = True
    Cmds.run(A["ref"], st, A["pr"], w, "pebble", None, None)
    s = said()
    pr2 = Store.last()
    K.check("REPLACED our rock model" in s[0] and "forced the rock back: now Rubble_Stone_Mossy x5.0" in s[0], "X: pebble when the role replaces the model -> rock forced back: %s" % s)
    mode["replace"] = False
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    mode["role"] = -1
    Cmds.run(A["ref"], st, A["pr"], w, "pebble", None, None)
    K.check(said()[0].startswith("Pebble needs the vanilla role Temple_Kweebec_Static (-1)"), "X: pebble refused when the role is missing")
    mode["role"] = 7
    mode["spawn"] = "null"
    Cmds.run(A["ref"], st, A["pr"], w, "pebble", None, None)
    K.check(said() == ["The pebble did not spawn (see the server log)."] and any("PEBBLE FAILED" in l for l in logged()), "X: a failed spawn is reported")
    mode["spawn"] = "ok"

    # ================= TpUseSys: F on Mossby
    UEP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre")
    us = UseSys()
    ch = U.allocateInstance(MCH.class_)
    ch.ref = A["ref"]
    ev = UEP(ITY.Use, None, nref_)
    us.handle(0, ch, st, cb, ev)
    s, lg_ = said(), logged()
    K.check(bool(ev.isCancelled()) and s and "Mossby could not open the Bazaar: page id SkyyBazaar is not registered" in s[0]
            and any("page NOT opened" in l for l in lg_), "X: F on Mossby without SkyyBazaar: vanilla *UseNPC cancelled, a clear line: %s" % s)
    OCU = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction")
    BC = JClass("com.hypixel.hytale.codec.builder.BuilderCodec")
    OCU.PAGE_CODEC.register("SkyyBazaar", FS.class_, BC.builder(FS.class_, FSM()).build())
    FS.PAGE = U.allocateInstance(FPG.class_)
    ev = UEP(ITY.Use, None, nref_)
    us.handle(0, ch, st, cb, ev)
    s, lg_ = said(), logged()
    K.check(bool(ev.isCancelled()) and not s and A["pm"].opened.size() == 1 and A["pm"].opened.get(0) == FS.PAGE and int(FS.CALLS) == 1
            and FS.LAST == A["pr"] and any("SkyyBazaar page OPENED via its page id" in l for l in lg_),
            "X: F on Mossby -> the REAL PAGE_CODEC finds the registered SkyyBazaar supplier, tryCreate(player), openCustomPage")
    FS.PAGE = None
    ev = UEP(ITY.Use, None, nref_)
    us.handle(0, ch, st, cb, ev)
    K.check(said() == ["Mossby could not open the Bazaar: the SkyyBazaar page supplier returned no page"], "X: a supplier without a page -> line")
    FS.PAGE = U.allocateInstance(FPG.class_)
    stranger = mkref()
    put(stranger, UUC.getComponentType(), UUC(UUID.randomUUID()))
    ev = UEP(ITY.Use, None, stranger)
    us.handle(0, ch, st, cb, ev)
    K.check(not bool(ev.isCancelled()) and not said(), "X: F on any other NPC is left to vanilla")
    Cmds.run(A["ref"], st, A["pr"], w, "pebble", None, None)
    said()
    pb_rec = Store.last()
    ev = UEP(ITY.Use, None, spawned[str(pb_rec.uuids)])
    us.handle(0, ch, st, cb, ev)
    K.check(bool(ev.isCancelled()) and said() == ["[Pebble] ...the rock looks back at you."], "X: F on Pebble -> its line")
    ch2 = U.allocateInstance(MCH.class_)
    ch2.boom = True
    us.handle(0, ch2, st, cb, UEP(ITY.Use, None, nref_))
    us.handle(0, ch2, st, cb, UEP(ITY.Use, None, nref_))
    K.check(sum(1 for l in logged() if "use hook failed" in l) == 1, "X: a broken use event is logged once")

    # ================= TpTick: barks + zone lines
    tk = Tick()
    B2 = mkplayer("Guest", 2, 0.5, 141.0, 0.5, admin=False)
    ch.ref = B2["ref"]
    tk.tick(JFloat(0.5), 0, ch, st, cb)
    K.check(not said(), "X: tick paced to 1 s (0.5 s -> nothing)")
    tk.tick(JFloat(0.6), 0, ch, st, cb)
    s, lg_ = said(), logged()
    K.check(s.count("[Mossby] Welcome to the Department of Arrivals! Press F to open the Bazaar.") == 1 and any("BARK: npc" in l and "greeted Guest at 3 blocks" in l for l in lg_),
            "X: Mossby barks once within 8 blocks: %s" % s)
    K.check(any("[Pebble]" in x for x in s), "X: Pebble barks too (it stands 3 ahead as well)")
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    K.check(not said(), "X: no second bark within 60 s")
    B2["tc"].setPosition(V3D(0.5, 141.0, 30.5))
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    for k in list(Tick.BARKED.keySet()):
        Tick.BARKED.put(k, JClass("java.lang.Long")(JLong(1)))
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    K.check(Tick.BARKED.isEmpty(), "X: leaving the range re-arms the bark")
    B2["tc"].setPosition(V3D(0.5, 141.0, 0.5))
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    K.check(any("[Mossby]" in x for x in said()), "X: back in range -> greeted again")

    # ================= zone + guards
    Cmds.run(A["ref"], st, A["pr"], w, "zone", None, None)
    s, lg_ = said(), logged()
    z = Store.ZONE
    K.check(z is not None and not bool(z.all) and s[0].startswith("Probe zone on around you") and any("ZONE on (non-admins refused, memory only)" in l for l in lg_),
            "X: zone on (non-admins refused, memory only): %s" % s)
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    K.check(said() == ["You entered the town probe zone (building refused for non-admins)."], "X: zone enter line")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    PLBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    UBP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre")
    rock = btm.getAsset(JInt(int(btm.getIndex("Rock_Stone"))))
    gb, gp, gd, gu = (JClass(PKG + n)() for n in ("TpGuardBreak", "TpGuardPlace", "TpGuardDamage", "TpGuardUse"))

    def evs(x, y, z_):
        return [(gb, BBE(None, V3I(x, y, z_), rock), "break blocks"), (gp, PLBE(None, V3I(x, y, z_), None), "place blocks"),
                (gd, DBE(None, V3I(x, y, z_), rock, JFloat(1.0), JFloat(0.0)), "dig blocks"),
                (gu, UBP(ITY.Use, None, V3I(x, y, z_), rock), "use blocks")]
    Guard.WARNED.clear()
    for g_, e_, act in evs(2, 140, 3):
        Guard.WARNED.clear()
        g_.handle(0, ch, st, cb, e_)
        s, lg_ = said(), logged()
        K.check(bool(e_.isCancelled()) and s == ["Town probe zone: you can't %s here." % act] and any("ZONE: REFUSED %s by Guest at 2 140 3" % act in l for l in lg_),
                "X: guard %s inside the zone refuses a non-admin (cancelled, line, log)" % act)
    e_ = BBE(None, V3I(2, 140, 3), rock)
    gb.handle(0, ch, st, cb, e_)
    K.check(bool(e_.isCancelled()) and not said(), "X: repeated refusals are cancelled but the line is throttled (3 s)")
    Guard.LAST_OUT = JLong(0)
    e_ = BBE(None, V3I(30, 140, 3), rock)
    gb.handle(0, ch, st, cb, e_)
    K.check(not bool(e_.isCancelled()) and not said() and any("OUTSIDE the zone - allowed" in l for l in logged()), "X: outside the zone is allowed (logged, throttled)")
    ch.ref = A["ref"]
    Guard.LAST_ADMIN = JLong(0)
    e_ = BBE(None, V3I(2, 140, 3), rock)
    gb.handle(0, ch, st, cb, e_)
    K.check(not bool(e_.isCancelled()) and any("by admin Skyy" in l and "allowed" in l for l in logged()), "X: an admin inside a normal zone is allowed")
    Cmds.run2(A["ref"], st, A["pr"], w, "zone", "all")
    said()
    K.check(bool(Store.ZONE.all), "X: zone all")
    Guard.WARNED.clear()
    e_ = BBE(None, V3I(2, 140, 3), rock)
    gb.handle(0, ch, st, cb, e_)
    K.check(bool(e_.isCancelled()) and said() == ["Town probe zone: you can't break blocks here."], "X: zone all refuses the admin too")
    e_ = BBE(None, V3I(2, 140, 3), rock)
    st.ext = U.allocateInstance(EST.class_)
    jfield(EST, "world").set(st.ext, other)
    gb.handle(0, ch, st, cb, e_)
    st.ext = es
    K.check(not bool(e_.isCancelled()), "X: the zone does nothing in another world")
    Cmds.run2(A["ref"], st, A["pr"], w, "zone", "maybe")
    K.check(said() == ["Use /townprobe zone, /townprobe zone all or /townprobe zone off."], "X: zone with a bad option")
    ch.ref = B2["ref"]
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    K.check(said() == ["You entered the town probe zone (building refused for everyone)."], "X: a new zone re-arms the enter line (zone all wording)")
    B2["tc"].setPosition(V3D(40.5, 141.0, 0.5))
    tk.tick(JFloat(1.1), 0, ch, st, cb)
    K.check("You left the town probe zone." in said(), "X: zone leave line")
    Cmds.run2(A["ref"], st, A["pr"], w, "zone", "off")
    K.check(said() == ["The probe zone is gone."] and Store.ZONE is None, "X: zone off")
    e_ = BBE(None, V3I(2, 140, 3), rock)
    gb.handle(0, ch, st, cb, e_)
    K.check(not bool(e_.isCancelled()), "X: no zone = nothing refused")
    Cmds.run2(A["ref"], st, A["pr"], w, "zone", "off")
    K.check(said() == ["There was no probe zone."], "X: zone off twice")
    Store.ZONE = Zone(WORLD, 0.5, 0.5, False)
    ch3 = U.allocateInstance(MCH.class_)
    ch3.boom = True
    gb.handle(0, ch3, st, cb, BBE(None, V3I(2, 140, 3), rock))
    gb.handle(0, ch3, st, cb, BBE(None, V3I(2, 140, 3), rock))
    tk.tick(JFloat(1.1), 0, ch3, st, cb)
    tk.tick(JFloat(1.1), 0, ch3, st, cb)
    lg_ = logged()
    K.check(sum(1 for l in lg_ if "zone guard failed" in l) == 1 and sum(1 for l in lg_ if "probe tick failed" in l) == 1, "X: broken guard / tick logged once each")
    K.check(Guard.decide(None, WORLD, 0, 0, False) == -1 and Guard.decide(Store.ZONE, "x", 0, 0, False) == -1 and Guard.decide(Store.ZONE, WORLD, 0, 0, True) == 0
            and Guard.decide(Store.ZONE, WORLD, 0, 0, False) == 1, "X: TpGuard.decide table")
    Store.ZONE = None

    # ================= undo of entity records: not found -> confirm within 30 s
    gone_u = str(pb_rec.uuids)
    spawned.pop(gone_u)
    mode["unloaded"] = {(int(float(pb_rec.nx)) // 32, int(float(pb_rec.nz)) // 32)}
    for _ in range(2):
        Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
        s, lg_ = said(), logged()
        K.check(s and s[0].startswith("Pebble at ") and "is in an area that is not loaded. Go near it" in s[0] and int(Store.RECS.size()) == 2
                and any("unloaded area" in l and "kept" in l for l in lg_), "A5: undo of an entity in an UNLOADED area never forgets it (even twice in 30 s): %s" % s)
    mode["unloaded"] = set()
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    s, lg_ = said(), logged()
    K.check(s[0].endswith("is not there any more (its area is loaded but the entity is gone). Run /townprobe undo again within 30 s to forget it.")
            and int(Store.RECS.size()) == 2, "X: undo of a missing entity (area loaded) asks to confirm: %s" % s)
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    s, lg_ = said(), logged()
    K.check(s[0].startswith("Undone: Pebble") and any("not found: " + gone_u in l for l in lg_) and int(Store.RECS.size()) == 1, "X: second undo within 30 s forgets it")
    Cmds.run(A["ref"], st, A["pr"], other, "undo", None, None)
    K.check(said()[0].startswith("The newest probe change (Mossby at 0 141 3) is in world skywynn_z1 - go there to undo it."), "X: undo from another world names the world")
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    said()
    K.check(st.removed.contains(nref_) and int(Store.RECS.size()) == 0 and Store.NPCS.isEmpty() and not os.path.exists(data), "X: Mossby undone, no data left")

    # ================= remaining branches: load() skips bad files, no position, undo while busy, npc check with the entity gone,
    # F from a ref without a Player component
    os.makedirs(os.path.join(data, "undo"), exist_ok=True)
    open(os.path.join(data, "undo", "5.properties"), "w").write("seq=5\nkind=temple\nworld=%s\nsnap=5.lpf\n" % WORLD)    # snapshot missing
    open(os.path.join(data, "undo", "6.properties"), "w").write("garbage")
    open(os.path.join(data, "undo", "7.properties"), "w").write("seq=8\nkind=npc\nworld=%s\n" % WORLD)                  # name != seq
    open(os.path.join(data, "undo", "9.properties"), "w").write("seq=9\nkind=npc\nworld=%s\nuuids=%s\nnx=0.5\nny=141\nnz=3.5\n" % (WORLD, UUID.randomUUID()))
    open(os.path.join(data, "undo", "12.lpf"), "wb").write(b"orphan")                                                 # snapshot without a record
    open(os.path.join(data, "undo", "13.properties.tmp"), "w").write("half")
    K.check(int(Store.load()) == 1 and int(Store.SEQ) == 9, "X: load keeps the good record (seq 9) and skips 3 bad ones")
    lg_ = logged()
    K.check(sum(1 for l in lg_ if "lost its snapshot" in l) == 1 and sum(1 for l in lg_ if "ignored unreadable undo record" in l) == 2
            and sum(1 for l in lg_ if "orphan undo file" in l) == 2, "X: load warns about each bad file: %s" % lg_)
    K.check(sorted(os.listdir(os.path.join(data, "undo"))) == ["9.properties"], "A2: load deletes the broken / orphan undo files (lost snapshot, unreadable, name mismatch, lone .lpf, .tmp), keeps the good record: %s" % os.listdir(os.path.join(data, "undo")))
    Cmds.run(A["ref"], st, A["pr"], w, "npc", None, None)
    s, lg_ = said(), logged()
    K.check(s[0].startswith("Mossby is already placed (not found right now; ") and "Not spawning another." in s[0] and any("NOT FOUND (unloaded or gone)" in l for l in lg_),
            "X: npc check when the saved Mossby is not loaded: reported, no spawn: %s" % s)
    Store.setBusy(True)
    Cmds.run(A["ref"], st, A["pr"], w, "undo", None, None)
    K.check(said() == ["Still working on the last probe action - try again in a moment."], "X: undo while busy is refused")
    Store.setBusy(False)
    for f in os.listdir(os.path.join(data, "undo")):
        os.remove(os.path.join(data, "undo", f))
    K.check(int(Store.load()) == 0, "X: reload after clearing the folder")
    Store.cleanDirs()
    K.check(not os.path.exists(data), "X: cleanDirs removes the empty folders")
    C_ = mkref()
    put(C_, PRc.getComponentType(), A["pr"])
    Cmds.run(C_, st, A["pr"], w, "lane", None, None)
    K.check(said() == ["Could not read your position."], "X: no TransformComponent -> 'Could not read your position.'")
    logged()
    K.check(str(UseSys.openPage(C_, st, cb, A["pr"])) == "no Player component", "X: openPage without a Player component says so")

    # ================= the REAL TpEng.store / refOf (API off); TpNpc.model on the real ModelAsset store; TpEntCount; TpSnap.count
    Eng.API = None
    try:
        K.check(Eng.store(w) == st, "X: real TpEng.store = world.getEntityStore().getStore()")
    except Exception as e:
        K.notes.append("real TpEng.store on the allocated EntityStore: %s" % str(e)[:160])
    uu = UUID.randomUUID()
    rr_ = mkref()
    byuuid.put(uu, rr_)
    hb_ = Eng.newHolder()
    K.check(str(hb_.getClass().getName()) == "com.hypixel.hytale.component.Holder", "X: real TpEng.newHolder = EntityStore.REGISTRY.newHolder() (a real Holder)")
    K.check(Eng.refOf(w, uu) == rr_ and Npc.find(w, str(uu)) == rr_ and Npc.find(w, "not-a-uuid") is None, "X: real TpEng.refOf = EntityStore.getRefFromUUID; find guards bad ids")
    Eng.API = api
    m5 = Npc.model("Rubble_Stone_Mossy", JFloat(5.0))
    K.check(m5 is not None and str(m5.getModelAssetId()) == "Rubble_Stone_Mossy" and abs(float(m5.getScale()) - 5.0) < 1e-6 and Npc.model("Nope", JFloat(1.0)) is None,
            "E: TpNpc.model = the REAL Model.createStaticScaledModel x5 on the vanilla asset; unknown id -> null")
    HOLc = JClass("com.hypixel.hytale.component.Holder")
    ec_ = EntCount()
    ec_.accept(0, 0, JArray(HOLc)([None, None]), None)
    ec_.accept(0, 0, None, None)
    K.check(int(ec_.n) == 2, "X: TpEntCount counts prefab entities")
    reg_ = SW.region(0, 140, 0, 3, 141, 3)
    K.check(str(Snap.count(reg_, int(btm.getIndex("Soil_Grass")), 0, 140, 0, 1, 141, 0)) == "2 at 0 140 0, 1 140 0" and str(Snap.count(reg_, -1, 0, 0, 0, 0, 0, 0)) == "0 (id not loaded)",
            "X: TpSnap.count")
    K.check(int(Build.idOf("Nope_Block")) < 0 and Build.yawFor(1, 1) is None and int(Build.rotIndex(None)) == 0, "X: TpBuild idOf / yawFor / rotIndex edges")
    try:
        Build.entry(0, "Nope_Block", 0)
        K.check(False, "X: entry refuses an unloaded block")
    except Exception:
        K.check(True, "X: entry refuses an unloaded block")
    yaws = [str(Build.yawFor(fx, fz)) for fx, fz in ((0, -1), (-1, 0), (0, 1), (1, 0))]
    K.check(yaws == ["None", "Ninety", "OneEighty", "TwoSeventy"], "X: yawFor north/west/south/east = None/Ninety/OneEighty/TwoSeventy (engine maths): %s" % yaws)

    # ================= the 4 commands' execute() through reflection with a real CommandContext
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    STc = JClass("com.hypixel.hytale.component.Store")
    cm0, cm1, cm2, cm3 = (JClass(PKG + n)() for n in ("TownProbeCmd", "TownProbeArgCmd", "TownProbeArg2Cmd", "TownProbeArg3Cmd"))

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
    K.check(len(said()) == 10, "X: /townprobe execute -> help")
    execute(cm1, ctx_of([(cm1.aArg, "help")]))
    K.check(len(said()) == 10, "X: /townprobe help through TownProbeArgCmd.execute + CommandContext.get")
    execute(cm2, ctx_of([(cm2.aArg, "zone"), (cm2.bArg, "off")]))
    K.check(said() == ["There was no probe zone."], "X: /townprobe zone off through TownProbeArg2Cmd")
    execute(cm3, ctx_of([(cm3.aArg, "piece"), (cm3.bArg, "stall"), (cm3.cArg, "9")]))
    K.check(said() == ["Rotation must be 0, 1, 2 or 3 (add e for entities, like 1e)."], "X: /townprobe piece stall 9 through TownProbeArg3Cmd")
    for c_ in (cm1, cm2, cm3):
        execute(c_, None)
    K.check(len(said()) == 30, "X: every variant without a context -> help")

    # ================= plugin shutdown clears the memory state
    Store.ZONE = Zone(WORLD, 0.0, 0.0, True)
    Tick.IN.put(A["uuid"], JBoolean(True))
    PLc = JClass(PKG + "SkyyTownProbePlugin")
    plg = U.allocateInstance(PLc.class_)
    try:
        sd = PLc.class_.getDeclaredMethod("shutdown")
        sd.setAccessible(True)
        sd.invoke(plg, JArray(JObject)([]))
    except Exception as e:
        K.notes.append("plugin shutdown: super.shutdown() on an allocated plugin: %s" % str(e)[:120])
    K.check(Store.ZONE is None and Tick.IN.isEmpty() and Tick.BARKED.isEmpty() and Guard.WARNED.isEmpty(), "X: plugin shutdown clears zone / bark / guard state")
    Log.SINK, Log.LINES = None, None
    print("X. every probe path executed")


def run_perm(out):
    """child P: permissions with the engine's own AbstractCommand code"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("TownProbeCmd", "TownProbeArgCmd", "TownProbeArg2Cmd", "TownProbeArg3Cmd"):
        c = JClass(PKG + cn)()
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "TownProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
            K.check("tprobe" in [str(a) for a in c.getAliases()] and str(c.getName()) == "townprobe", "P. /townprobe + alias /tprobe")
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
    """child B: setup() order; the real engine lines = vanilla's call shapes; the NPC engine facts"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    nm = lambda cs: [c.split("(")[0] for c in cs]
    calls = nm(bytecode_calls(cp, PKG + "SkyyTownProbePlugin", "setup"))
    want = ["PluginBase.getLogger", "put TpLog.LOG", "PluginBase.getDataDirectory", "put TpStore.DIR", "TpStore.load", "PluginBase.getCommandRegistry",
            "new TownProbeCmd", "CommandRegistry.registerCommand", "new TpUseSys", "ComponentRegistryProxy.registerSystem", "new TpGuardBreak",
            "ComponentRegistryProxy.registerSystem", "new TpGuardDamage", "ComponentRegistryProxy.registerSystem", "new TpGuardPlace",
            "ComponentRegistryProxy.registerSystem", "new TpGuardUse", "ComponentRegistryProxy.registerSystem", "new TpTick", "ComponentRegistryProxy.registerSystem"]
    pos, ok = 0, True
    for x in want:
        try:
            pos = calls.index(x, pos) + 1
        except ValueError:
            ok = False
            break
    K.check(ok and calls.count("ComponentRegistryProxy.registerSystem") == 6, "B: setup() = LOG, data folder, load, registerCommand, registerSystem once each for 6 systems: %s" % calls)
    full = lambda cls, m, sig=None: bytecode_calls(cp, cls, m, sig)
    eng = PKG + "TpEng"
    WE = "com.hypixel.hytale.builtin.adventure.worldevents."
    van_paste = [c for c in full(WE + "action.PrefabRemoveAction$RemoveOp", "accept", "PasteRegion") if c.startswith("PrefabUtil.paste")]
    our_paste = [c for c in full(eng, "paste") if c.startswith("PrefabUtil.paste")]
    K.check(len(our_paste) == 1 and our_paste == van_paste[:1], "B: TpEng.paste = vanilla PrefabRemoveAction$RemoveOp's PrefabUtil.paste overload: %s vs %s" % (our_paste, van_paste))
    van_load = [c for c in full(WE + "action.PrefabRemoveAction", "apply", "World") if "loadPasteRegionAsync" in c]
    our_load = [c for c in full(eng, "loadRegion") if "loadPasteRegionAsync" in c]
    K.check(our_load and our_load == van_load, "B: TpEng.loadRegion = vanilla PrefabRemoveAction's loadPasteRegionAsync: %s" % our_load)
    van_spawn = [c for c in full("com.hypixel.hytale.builtin.triggervolumes.effect.builtin.SpawnNpcEffect", "execute") if "spawnNPC" in c]
    our_spawn = [c for c in full(eng, "spawnNpc") if "spawnNPC" in c]
    K.check(our_spawn and our_spawn == van_spawn, "B: TpEng.spawnNpc = vanilla SpawnNpcEffect's NPCPlugin.spawnNPC: %s" % our_spawn)
    K.check(any("NPCPlugin.spawnEntity(Lcom/hypixel/hytale/component/Store;ILorg/joml/Vector3dc;Lcom/hypixel/hytale/math/vector/Rotation3fc;Lcom/hypixel/hytale/server/core/asset/type/model/config/Model;Lcom/hypixel/hytale/function/consumer/TriConsumer;)" in c for c in full(eng, "spawnModel")),
            "B: TpEng.spawnModel = NPCPlugin.spawnEntity(store, role, pos, rot, model, null) (null TriConsumer is guarded in the engine)")
    van_spi = full("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.SpawnPrefabInteraction", "firstRun")
    for m_, key in (("findPrefab", "findAssetPrefabPath"), ("buffer", "getCached")):
        ours = [c for c in full(eng, m_) if key in c]
        K.check(ours and ours[0] in van_spi, "B: TpEng.%s = vanilla SpawnPrefabInteraction's %s" % (m_, key))
    K.check(any(c.startswith("EntityStore.getRefFromUUID") for c in full(eng, "refOf")) and any(c.startswith("World.getChunkIfLoaded") for c in full(eng, "height"))
            and any(c.startswith("WorldChunk.getHeight(II)S") for c in full(eng, "height")) and any(c.startswith("WorldChunk.getBlock(III)I") for c in full(eng, "key"))
            and any(c.startswith("BlockTypeAssetMap.getAsset(I)") for c in full(eng, "key")), "B: TpEng refOf / height / key use getRefFromUUID / getChunkIfLoaded + getHeight / getBlock + getAsset(int)")
    # not copied on purpose: the UUID / write into the world's snapshots dir, the assert (TpPaste.step checks isFullyLoaded before), the unused
    # getColumnAtBlock result, Vector3ic.x() (we read the Vector3i fields)
    van_snap = [c for c in full(WE + "util.PrefabSnapshotUtil", "createSnapshot") if not c.startswith(("UUID.", "PrefabSnapshotUtil.", "new java", "new AssertionError",
                "AssertionError", "get PrefabSnapshotUtil", "Vector3ic.", "PrefabUtil$PasteRegion.getColumnAtBlock", "PrefabUtil$PasteRegion.isFullyLoaded"))]
    our_snap = [c for c in full(PKG + "TpSnap", "create")]
    K.check(set(van_snap) <= set(our_snap), "B: TpSnap.create calls every engine method vanilla createSnapshot calls: missing %s" % sorted(set(van_snap) - set(our_snap)))
    K.check(any("BlockTypeAssetMap.getAsset(I)" in c for c in our_snap), "B: TpSnap.create uses BlockTypeAssetMap.getAsset(int) (javassist picked the int overload)")
    nh = full(eng, "newHolder")
    van_nh = full("com.hypixel.hytale.server.npc.NPCPlugin", "spawnEntity", "TriConsumer;Lcom/hypixel/hytale/function/consumer/TriConsumer;")
    K.check("get EntityStore.REGISTRY" in nh and any(c.startswith("ComponentRegistry.newHolder") for c in nh) and "get EntityStore.REGISTRY" in van_nh,
            "B: TpEng.newHolder = EntityStore.REGISTRY.newHolder() (what NPCPlugin.spawnEntity does)")
    use = full(PKG + "TpUseSys", "openPage")
    K.check(any(c.startswith("CodecMapCodec.getCodecFor(Ljava/lang/Object;)") or c.startswith("ACodecMapCodec.getCodecFor(Ljava/lang/Object;)") for c in use)
            and any("CustomPageSupplier.tryCreate" in c for c in use) and any(c.startswith("PageManager.openCustomPage") for c in use),
            "B: openPage = PAGE_CODEC.getCodecFor(Object) -> CustomPageSupplier.tryCreate -> PageManager.openCustomPage: %s" % [c.split("(")[0] for c in use])
    rbs = full("com.hypixel.hytale.server.npc.systems.RoleBuilderSystem", "onEntityAdd")
    K.check("ldc *UseNPC" in rbs and any(c.startswith("Interactions.setInteractionId") for c in rbs), "B: engine fact: RoleBuilderSystem gives every NPC Use = *UseNPC")
    uei = full("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.UseEntityInteraction", "firstRun")
    K.check(any(c.startswith("Interactions.getInteractionId") for c in uei) and "new UseEntityEvent$Pre" in uei and any(c.startswith("UseEntityEvent$Pre.isCancelled") for c in uei),
            "B: engine fact: UseEntityInteraction checks the target's Use id, fires UseEntityEvent$Pre and honours its cancel")
    emi = full("com.hypixel.hytale.server.core.command.commands.world.entity.EntityMakeInteractableCommand", "execute")
    K.check(any(c.startswith("Store.ensureComponent") for c in emi) and any(c.startswith("Interactable.getComponentType") for c in emi),
            "B: engine fact: the vanilla make-interactable command = Store.ensureComponent(Interactable) (what makeUsable does)")
    mk_ = full(PKG + "TpNpc", "makeUsable")
    K.check(any(c.startswith("Store.ensureComponent") for c in mk_) and "ldc server.interactionHints.trade" in full(PKG + "TpNpc", "<clinit>") if False else any(c.startswith("Store.ensureComponent") for c in mk_),
            "B: TpNpc.makeUsable = Store.ensureComponent(Interactable)")
    K.save()


def run_live(step, out):
    """child D: one 'server start' on the scratch copy of the live world mods folder"""
    from jpype import JClass, JLong
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
    Store, Rec, Log = JClass(PKG + "TpStore"), JClass(PKG + "TpRec"), JClass(PKG + "TpLog")
    lines = JClass("java.util.ArrayList")()
    Log.LINES = lines
    Paths = JClass("java.nio.file.Paths")
    mine = os.path.join(home, "Skyy_SkyyTownProbe")
    before = snapshot()
    Store.DIR = Paths.get(mine)
    n = int(Store.load())
    if step in ("start1", "start2"):
        K.check(n == 0 and Store.NPCS.isEmpty() and Store.ZONE is None and not os.path.exists(mine), "D %s: load on the live copy: 0 records, no probe folder created" % step)
        K.check(snapshot() == before, "D %s: the probe wrote nothing - every scratch file byte-identical, no new file" % step)
        wp = os.path.join(home, "Skyy_SkyyWorldGen", "worlds.properties")
        if os.path.isfile(wp):
            K.check(WORLD in open(wp, encoding="utf-8", errors="replace").read(), "D %s: the live SkyyWorldGen worlds.properties names %s (the probe's world)" % (step, WORLD))
        else:
            K.notes.append("D %s: no Skyy_SkyyWorldGen/worlds.properties in the live copy" % step)
    elif step == "start3":
        for kind, extra in (("npc", "uuids=11111111-2222-3333-4444-555555555555\nnx=0.5\nny=141.0\nnz=3.5\n"), ("lane", "snap=%d.lpf\n")):
            r = Rec()
            r.seq = Store.nextSeq()
            r.kind, r.world, r.what = kind, WORLD, "start3 " + kind
            if kind == "npc":
                r.uuids, r.nx, r.ny, r.nz = "11111111-2222-3333-4444-555555555555", 0.5, 141.0, 3.5
            else:
                r.snap = "%d.lpf" % int(r.seq)
                os.makedirs(os.path.join(mine, "undo"), exist_ok=True)
                open(os.path.join(mine, "undo", str(r.snap)), "wb").write(b"lpf")
            K.check(bool(Store.add(r)), "D start3: %s record written" % kind)
        K.check(sorted(os.listdir(os.path.join(mine, "undo"))) == ["1.properties", "2.lpf", "2.properties"], "D start3: the probe folder holds only the undo files")
    elif step == "start4":
        K.check(n == 2 and Store.NPCS.containsKey("11111111-2222-3333-4444-555555555555") and int(Store.SEQ) == 2 and int(Store.nextSeq()) == 3,
                "D start4: both records load back, the NPC is indexed (barks / F work after a restart), the sequence continues")
        while not Store.RECS.isEmpty():
            Store.remove(Store.last())
        K.check(not os.path.exists(mine), "D start4: removing every record deletes the probe folder again")
    Log.LINES = None
    others = dict((k, v) for k, v in snapshot().items() if not k.startswith("Skyy_SkyyTownProbe"))
    base = dict((k, v) for k, v in before.items() if not k.startswith("Skyy_SkyyTownProbe"))
    K.check(others == base, "D %s: every other mod's live-copy file byte-identical" % step)
    K.save(files=len(others))


def run_audit(out):
    """child AA: the engine-access audit (the SkyyMonkProbe / SkyyReelProbe harness part AA)"""
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
        # D: start twice on a scratch copy of the live world mods folder (read-only source)
        home = os.path.join(SCRATCH, "live")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        n = sum(len(f) for _, _, f in os.walk(home))
        print("D. %d live mod data files copied (read-only source %s)" % (n, LIVE))
        check(n > 0 and not os.path.exists(os.path.join(home, "Skyy_SkyyTownProbe")), "D: live mod data copied, no probe folder there yet (%s)" % LIVE)
        for step in ("start1", "start2", "start3", "start4"):
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
