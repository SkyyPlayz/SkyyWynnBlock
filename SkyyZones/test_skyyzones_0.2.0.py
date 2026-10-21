"""Harness for SkyyZones 0.2.0 (Z2 regrowing blocks; derived from the 0.1.0 harness, every 0.1.0 check kept or adapted). Build first:
    python tools/zones_0_2_0_patch.py
    python SkyyZones/build_skyyzones_0.2.0.py
    python SkyyZones/test_skyyzones_0.2.0.py [--keep]

0.2.0 adds (phase X runs with regrowing OFF = the 0.1.0 behaviour, then phase R with it ON):
  J   class compare old vs new: every 0.1.0 class is still there, + exactly ZDep / ZRw / ZPass / ZRegen / ZTicker; the 0.2.0 ready line
  C   regen.properties defaults (spec Q2 times, Rock_Bedrock, logs / crops 0, the defaultSec fallback), bad regrow lines skipped + warned,
      clamps, an unreadable file keeps the old settings, the checkRegrow hook (bad seconds, bad / unknown placeholder, removal)
  G   the 0.1.0 critic's FAIL-OPEN case: a typo'd region with NO history/ copy comes back from regions.good.properties; with no good copy
      anywhere and no readable box its WHOLE world is locked FULL (warned), unlocked by a fixed reload; a missing / blank / unreadable
      file at a start is restored from regions.good.properties (exact, not one change behind)
  R   EXECUTED regrow flow on the real ZGuard / ZRegen / ZPass / ZTicker with a stand-in world: break -> journal line FIRST -> engine
      removes -> queued pass places the placeholder -> regrow at regrowAt (id + rotation back, R line); the waiting spot refuses break /
      dig / place for everyone (never mined twice); CONTESTED (two breaks in one tick: one drop); a player standing in the block (retry 1 s,
      warned after 12, then 5 s); a break another mod cancelled; a spot changed by hand (never overwritten); RESTART MID-TIMER (snapshot
      + journal replayed, a torn line skipped, compacted, same times, still protected, grows back on time); offlineCounts off; UNLOADED
      chunk catch-up; /zones restore all (forced, an unloaded chunk asked for + put back when it arrives, a world not loaded reported);
      /zones status; regen off (all back, vanilla breaks); a journal write failure REFUSES the break; regrow 0 (logs); a multi-block
      part; builder mode; mobs; regen.maxDepleted; /zones info line; bridge deny; /zones audit (+ fix, a waiting placeholder left
      alone); the 60 s snapshot tick; the scheduler start / stop
  K   the 9 new Server Setup rows (speedMult field + file, the regrow table through the kit + its reload, refusals, the Restore all action)
  E   the new real engine branches (API off) fail safely on stand-ins
  D   live copy: start 1 adds regen.properties (+ the 0.1.0 files when the folder is new), start 2 changes nothing

Every phase runs in a FRESH child JVM (the game's JRE, -XX:-UsePerfData, TEMP / TMP in the scratch folder - never AppData):
  J   parent: the jar = exactly the 42 expected classes (35 + 7 kit) + manifest + the wand item JSON + server.lang (every vanilla path the
      JSON names exists in Assets.zip, the lang has the 4 keys), manifest Name / Version / Main / IncludesAssetPack, the ready line text
  A   verify: every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  X   exec: EVERY new code path on stand-ins (subclasses of the engine's Store / ArchetypeChunk / World / PlayerRef / CommandContext,
      allocated without constructors) + the REAL engine classes for events (BreakBlockEvent, DamageBlockEvent, PlaceBlockEvent,
      UseBlockEvent$Pre, PlayerDisconnectEvent), BlockType (fields set by reflection), ItemStack, InteractionContext, Message,
      TransformComponent, the REAL config kit (CfgPub / CfgFn) and the REAL ZRules / ZStore / ZIndex / ZGuard / ZTick / ZCmds / ZFn code:
        rules (glob, bare, decide matrix incl. overlap priority + union, why / verdict, useKind table, useAction on real block types),
        config (default files, clamps, unreadable files, check hooks, protectedWorld / tools caches), regions (create / addbox / mode /
        priority / title / types / flags / delete, every refusal, file text, history <= 10, change log, RESTART RELOAD = same regions,
        bad line -> edits blocked + good regions kept, unreadable file -> memory kept, async save path, flush), guards (FULL break / dig /
        place refused + note throttled, SKYBLOCK allow + deny, doors / chests / furnaces / F-harvest / hoe, unprotected + island worlds
        untouched, protection off, builder mode, op bypass, mobs, the wand: corners A / B / repeat / non-admin / use / place),
        commands (every /zones word incl. kit protect / type, region create from the wand AND from the vanilla selection, refusals, the
        crash branch), the 4 command variants executed through a stand-in CommandContext (permission node + empty groups checked),
        tick (enter title, stay, leave note, re-enter gap, outline particles to the owner only + capped, expiry, world switch, build
        reminder), logout clean-up (real PlayerDisconnectEvent), bridge functions, the real engine branches of ZEng (API off: each one
        fails safely on the stand-ins and logs once), the plugin's setup() on an allocated plugin (never throws) + shutdown pieces
  D   live: a scratch COPY of the live world's mods/ folder (read-only source), the plugin's file start + the kit started TWICE: only
      Skyy_SkyyZones/ is added, every other file byte-identical, the second start changes nothing
  AA  audit: every class / field / method reference resolved with the JVM's access rules (tools/harness_kit.py), the control refused
Scratch: tools/dev/scratch/zones02fix2/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.0"
PKG = "com.skyy.zones."
JAR = os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)
SCRATCH = os.path.join(ROOT, "tools", "dev", "scratch", "zones02fix2", "h")
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE = HK.FAKE_PKG
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
CLASSES = ["ZApi", "ZCfg", "ZRegion", "ZIndex", "ZRules", "ZSave", "ZStore", "ZEng", "ZMsg", "ZBuild", "ZSel", "ZWand", "ZGuard",
           "ZGuardBreak", "ZGuardDamage", "ZGuardPlace", "ZGuardUse", "ZShow", "ZTick", "ZFn", "ZRegKit", "ZCmds", "ZCmd1", "ZCmd2", "ZCmd3", "ZCmd4", "ZCmd5",
           "ZCmd", "ZQuit", "SkyyZonesPlugin", "CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub",
           "ZDep", "ZRw", "ZPass", "ZRegen", "ZTicker"]
NEW_CLASSES = ["ZDep", "ZRw", "ZPass", "ZRegen", "ZTicker"]
OLD_JAR = os.path.join(HERE, "SkyyZones-0.1.0.jar")
WORLD, OTHER, ISLAND = "skywynn_server", "zone_test", "skyy-island-0000"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


# ====================================================================================================== F: stand-ins
def run_mkfake(out_dir):
    from jpype import JClass
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")

    def mk(name, sup=None):
        c = cp.makeClass(FAKE + "." + name)
        if sup:
            c.setSuperclass(cp.get(sup))
        return c

    def F(c, s):
        c.addField(CtField.make(s, c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(s, c))
    CR = "com.hypixel.hytale.component."
    ms = mk("MapStore", CR + "Store")
    for d in ("java.util.Map comps", "java.lang.Object ext", "boolean boom"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.boom) throw new IllegalStateException("boom");
  if (r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""")
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
    fw.addConstructor(CtNewConstructor.make("public FakeWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }", fw))
    fw.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    F(fp, "public java.util.List msgs;")
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs != null) this.msgs.add(m); }")
    fp.writeFile(out_dir)
    lk = mk("LookupIn")
    M(lk, "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
          "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}")
    lk.writeFile(out_dir)
    ba = mk("BadAccess")
    M(ba, "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
          "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}")
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== X: exec
def engine(K):
    from jpype import JClass, JArray, JString, JInt
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
    names = ["Rock_Stone", "Rock_Bedrock", "Ore_Copper_Stone", "Ore_Iron_Stone", "Soil_Grass", "Furniture_Crude_Chest", "Furniture_Door", "Bench_Furnace",
             "Bench_Workbench", "Plant_Crop_Carrot_Block", "Wood_Oak_Trunk", "Skyy_Island_Hub_Portal", "Bed_Test", "Seat_Test",
             "Rock_Stone_Cobble"]
    l_ = AL()
    l_.add(BT.EMPTY)
    l_.add(BT.UNKNOWN)
    for n in names:
        l_.add(BT(n))
    r_ = BT.getAssetStore().loadAssets("Hytale:Hytale", l_)
    K.check(not r_.hasFailed(), "E: the BlockType store holds the %d test blocks" % len(names))
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
    upr = U.allocateInstance(CT.class_)
    n_[0] += 1
    jfield(CT, "index").set(upr, JInt(n_[0]))
    jfield(UNI, "playerRefComponentType").set(uni, upr)
    return {"U": U, "jfield": jfield, "BT": BT}


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JInt, JLong, JFloat, JBoolean, JImplements, JOverride, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, FAKE_DIR], verify=True)
    E = engine(K)
    try:
        xrun(K, E)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:500])
    K.save()


def xrun(K, E):
    from jpype import JClass, JArray, JString, JInt, JLong, JFloat, JBoolean, JImplements, JOverride, JObject, JProxy
    import time
    U, jfield, BT = E["U"], E["jfield"], E["BT"]
    P = lambda n: JClass(PKG + n)
    Cfg, Reg, Idx, Rules, Save, Sto, Eng, Msg, Bld, Wand, Guard, Tick, Fn, Cmds, Quit, Plug = (P(n) for n in (
        "ZCfg", "ZRegion", "ZIndex", "ZRules", "ZSave", "ZStore", "ZEng", "ZMsg", "ZBuild", "ZWand", "ZGuard", "ZTick", "ZFn", "ZCmds",
        "ZQuit", "SkyyZonesPlugin"))
    CPub, CFn = P("CfgPub"), P("CfgFn")
    AL, HM, IHM, UUID, Paths = (JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"),
                                JClass("java.util.UUID"), JClass("java.nio.file.Paths"))
    Bool = JClass("java.lang.Boolean")
    MS, MB, MCH, FW, FP = (JClass(FAKE + "." + n) for n in ("MapStore", "MapBuffer", "MapChunk", "FakeWorld", "FakePr"))
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")

    def mkctx(vc, words):
        c_ = U.allocateInstance(CTXc.class_)
        mp = HM()
        for i_, w_ in enumerate(words):
            fa = vc.getClass().getDeclaredField("a%d" % i_)
            mp.put(fa.get(vc), w_)
        jfield(CTXc, "argValues").set(c_, mp)
        return c_
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    V3D, V3I = JClass("org.joml.Vector3d"), JClass("org.joml.Vector3i")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    REF = JClass("com.hypixel.hytale.component.Ref")
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICTX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    PLBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent")
    UBP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre")
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    Bench = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench")
    BenchType = JClass("com.hypixel.hytale.protocol.BenchType")
    Farm = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.farming.FarmingData")
    btm = BT.getAssetMap()

    def bt(n):
        return btm.getAsset(JInt(int(btm.getIndex(n))))
    lines = AL()
    Cfg.LINES = lines

    def logged():
        r = [str(x) for x in lines]
        lines.clear()
        return r

    # ---------------------------------------------------------------- the engine stand-in (ZApi)
    @JImplements(PKG + "ZApi")
    class Api(object):
        def __init__(self):
            self.notes, self.titles, self.parts, self.tgt, self.sel, self.give_r, self.blocks, self.boom = [], [], [], None, None, 0, {}, False
            # 0.2.0 the regrow world: (world, x, y, z) -> id, unloaded chunks (world, cx, cz), rotation / filler, players inside blocks,
            # block writes, chunk load requests, the world's task queue (World.execute), worlds by name
            self.wb, self.unloaded, self.state, self.occ, self.writes, self.loads, self.tasks, self.put_ok, self.worlds = {}, set(), {}, set(), [], [], [], True, {}
            self.lat = []   # fixer 2: delayed tasks (ZEng.later -> the server scheduler)

        def gone(self, wn, x, z):
            return (wn, int(x) >> 5, int(z) >> 5) in self.unloaded

        @JOverride
        def notify(self, pr, text):
            self.notes.append((str(pr.getUsername()), str(text)))

        @JOverride
        def title(self, pr, t, sub):
            self.titles.append((str(pr.getUsername()), str(t), str(sub)))

        @JOverride
        def particle(self, id_, x, y, z, to, st):
            self.parts.append((str(id_), float(x), float(y), float(z), [str(r) for r in to]))

        @JOverride
        def target(self, r, st):
            if self.boom:
                raise RuntimeError("boom")
            return None if self.tgt is None else JArray(JInt)(self.tgt)

        @JOverride
        def selection(self, r, st, pr):
            return None if self.sel is None else JArray(JInt)(self.sel)

        @JOverride
        def give(self, r, st, id_):
            return self.give_r

        @JOverride
        def blockAt(self, w, x, y, z):
            wn = str(w.getName()) if w is not None else None
            if self.gone(wn, x, z):
                return None
            k = (wn, int(x), int(y), int(z))
            if k in self.wb:
                return self.wb[k]
            return self.blocks.get((int(x), int(y), int(z)), "Rock_Stone")

        @JOverride
        def stateAt(self, w, x, y, z):
            wn = str(w.getName())
            if self.gone(wn, x, z):
                return None
            return JArray(JInt)(self.state.get((wn, int(x), int(y), int(z)), [0, 0]))

        @JOverride
        def put(self, w, x, y, z, id_, rot):
            wn = str(w.getName())
            if not self.put_ok or self.gone(wn, x, z):
                return False
            k = (wn, int(x), int(y), int(z))
            self.writes.append(k + (str(id_), int(rot)))
            self.wb[k] = str(id_)
            return True

        @JOverride
        def occupied(self, w, x, y, z):
            return (str(w.getName()), int(x), int(y), int(z)) in self.occ

        @JOverride
        def load(self, w, x, y, z, after):
            self.loads.append(((str(w.getName()), int(x) >> 5, int(z) >> 5), after))

        @JOverride
        def world(self, name):
            return self.worlds.get(str(name))

        @JOverride
        def exec(self, w, r):
            self.tasks.append(r)
            return True

        @JOverride
        def later(self, r, ms):
            self.lat.append((r, int(ms)))

        @JOverride
        def scan(self, w, box, ids, stats):
            wn, b, idl, out = str(w.getName()), list(box), [str(i) for i in ids], AL()
            stats[0] = (b[3] - b[0] + 1) * (b[4] - b[1] + 1) * (b[5] - b[2] + 1)
            for (kw, x, y, z), v in sorted(self.wb.items()):
                if kw == wn and b[0] <= x <= b[3] and b[1] <= y <= b[4] and b[2] <= z <= b[5] and v in idl:
                    out.add(JArray(JInt)([x, y, z, idl.index(v)]))
            return out
    api = Api()
    Eng.API = api
    perms = {}

    @JImplements("java.util.function.Function")
    class PermFn(object):
        @JOverride
        def apply(self, o):
            return Bool.valueOf(bool(perms.get((str(o[0]), str(o[1])), False)))
    Cfg.PERM_TEST = PermFn()

    # ---------------------------------------------------------------- R: pure rules
    K.check([str(Rules.bare(x)) for x in ("*Ore_Copper_Stone_State_X", "**A", "Rock", None)] == ["Ore_Copper_Stone_State_X", "A", "Rock", ""], "R: bare strips leading *")
    G = [("Ore_Copper*", "Ore_Copper_Stone", True), ("Ore_Copper+", "Ore_Copper_Stone", True), ("ore_copper*", "Ore_Copper_Stone", True),
         ("Wood_*_Trunk", "Wood_Oak_Trunk", True), ("Wood_*_Trunk", "Wood_Oak_Trunk_Stripped", False), ("Rock_Stone", "Rock_Stone", True),
         ("Rock_Stone", "Rock_Stone_Cobble", False), ("*", "x", True), ("a*b*c", "aXXbYYc", True), ("a*b*c", "aXXbYY", False),
         ("", "", True), (None, "x", False), ("x", None, False), ("*Trunk", "Wood_Oak_Trunk", True)]
    K.check(all(bool(Rules.glob(p, s)) == w for p, s, w in G), "R: glob table: %s" % [(p, s) for p, s, w in G if bool(Rules.glob(p, s)) != w])

    # ---------------------------------------------------------------- C: config + files
    home = os.path.join(SCRATCH, "x", "Skyy_SkyyZones")
    os.makedirs(os.path.dirname(home), exist_ok=True)
    r = str(Plug.paths(Paths.get(home)))
    files = sorted(os.listdir(home))
    K.check(files == ["config.properties", "regen.properties", "regions.properties", "types.properties"], "C: the first start writes the 4 default files: %s" % files)
    K.check(open(os.path.join(home, "config.properties"), encoding="utf8").read() == str(Cfg.DEFAULT_TEXT)
            and open(os.path.join(home, "types.properties"), encoding="utf8").read() == str(Cfg.TYPES_TEXT)
            and open(os.path.join(home, "regions.properties"), encoding="utf8").read() == str(Sto.HEAD) + "\n", "C: the default texts")
    K.check(r.startswith("default config.properties written; protection ON") and "default types.properties written; 13 resource types" in r
            and "default regen.properties written; regrowing ON (13 regrow rows)" in r and r.endswith("0 regions in 0 worlds; no block waiting to grow back"), "C: the start answer: %s" % r)
    K.check((bool(Cfg.ON), str(Cfg.WORLDS), bool(Cfg.OP_BYPASS), bool(Cfg.MOBS), int(Cfg.MSG_GAP), bool(Cfg.TITLES), bool(Cfg.LEAVE),
             int(Cfg.TITLE_GAP), int(Cfg.SHOW_SECS), str(Cfg.PARTICLE), int(Cfg.REMIND)) == (True, "", False, True, 2, True, True, 10, 30, "Alerted", 300),
            "C: defaults (on, no world, no admin bypass, mobs blocked, 2 s, titles on / leave / 10 s, 30 s outline, Alerted, 300 s reminder)")
    K.check(str(Plug.paths(Paths.get(home))).startswith("protection ON"), "C: the second start rewrites nothing")
    cfgf = os.path.join(home, "config.properties")
    open(cfgf, "w", encoding="utf8").write("zones.on=no\nzones.worlds=A, b ;c\nmsg.gapSec=99\ntitles.gapSec=-4\nshow.seconds=x\nbuild.remindSec=99999\nshow.particle=" + "p" * 90 + "\n")
    Cfg.loadCfg(False)
    K.check((bool(Cfg.ON), int(Cfg.MSG_GAP), int(Cfg.TITLE_GAP), int(Cfg.SHOW_SECS), int(Cfg.REMIND), len(str(Cfg.PARTICLE))) == (False, 30, 0, 30, 3600, 80),
            "C: hand-edited values are clamped (a bad number = the default)")
    K.check(bool(Cfg.protectedWorld("a")) and bool(Cfg.protectedWorld("B")) and bool(Cfg.protectedWorld("c")) and not bool(Cfg.protectedWorld("d"))
            and not bool(Cfg.protectedWorld(None)), "C: protectedWorld (comma / space / ; list, any case)")
    open(cfgf, "w", encoding="utf8").write(str(Cfg.DEFAULT_TEXT))
    Cfg.loadCfg(False)
    K.check(not bool(Cfg.protectedWorld("a")), "C: the world cache follows the setting")
    K.check(len(Cfg.tools()) == 12 and str(Cfg.tools()[0]) == "Tool_Bark_Scraper*", "C: use.tools parsed (12 patterns)")
    K.check(list(map(str, Cfg.splitList(" a, b;c  d ,"))) == ["a", "b", "c", "d"] and len(Cfg.splitList(None)) == 0, "C: splitList")
    K.check(bool(Cfg.bool("YES", False)) and not bool(Cfg.bool("off", True)) and bool(Cfg.bool("maybe", True)) and not bool(Cfg.bool(None, False))
            and int(Cfg.intOf(" 7 ", 1, 0, 9)) == 7 and str(Cfg.str(None, "d", 3)) == "d" and str(Cfg.str(" abcdef ", "d", 3)) == "abc", "C: bool / intOf / str")
    K.check(Cfg.checkWorlds("zones.worlds", "a b") is None and Cfg.checkWorlds("zones.worlds", None) is None and Cfg.checkWorlds("zones.worlds", "a/b") is not None
            and Cfg.checkWorlds("zones.worlds", ",".join("w%d" % i for i in range(33))) is not None, "C: checkWorlds")
    K.check(Cfg.checkType("type[ore_x]", "Ore_X*,Rock_Y") is None and Cfg.checkType("type[Bad]", "x") is not None and Cfg.checkType("type[ok]", "a/b") is not None
            and Cfg.checkType("type[ok]", " , ") is not None and Cfg.checkType("bogus", "x") is not None and Cfg.checkType("type[ok]", None) is None
            and Cfg.checkType("type[ok]", ",".join("a%d" % i for i in range(65))) is not None, "C: checkType (entry id, patterns, removal ok)")
    K.check(Cfg.checkTools("use.tools", "") is None and Cfg.checkTools("use.tools", "Tool_*") is None and Cfg.checkTools("use.tools", "a b!") is not None, "C: checkTools")
    cp_ = Cfg.checkParticle("show.particle", "Alerted")
    K.check((cp_ is None or str(cp_) == "No particle system 'Alerted' in the game files.") and Cfg.checkParticle("show.particle", "a b") is not None
            and Cfg.checkParticle("show.particle", None) is None, "C: checkParticle (the bare JVM's particle map is empty: %s)" % cp_)
    # unreadable types file keeps the old types; a bad type id is skipped
    tf = os.path.join(home, "types.properties")
    open(tf, "a", encoding="utf8").write("type.Bad-Id=X\ntype.empty=\n")
    K.check(str(Cfg.loadTypes(False)) == "13 resource types" and any("Bad-Id" in l for l in logged()), "C: a bad type id is skipped (warned), an empty one ignored")
    old = open(tf, encoding="utf8").read()
    os.remove(tf)
    os.makedirs(tf)
    K.check("could not be read - the old types are kept (13)" in str(Cfg.loadTypes(False)) and Cfg.TYPES.size() == 13, "C: types.properties unreadable -> old types kept")
    K.check(Cfg.read(Paths.get(tf)) is None and not bool(Cfg.writeIfMissing(Paths.get(tf), "x")), "C: read null on a folder; writeIfMissing never overwrites")
    os.rmdir(tf)
    open(tf, "w", encoding="utf8").write(old)
    Cfg.reloadTypes()
    K.check(Cfg.TYPES.size() == 13 and any("resource types re-read: 13 resource types" in l for l in logged()), "C: reloadTypes (the kit's table routine)")
    # 0.2.0 regen.properties
    regf = os.path.join(home, "regen.properties")
    K.check(open(regf, encoding="utf8").read() == str(Cfg.REGEN_TEXT) and Cfg.REGROW.size() == 13
            and [int(Cfg.regrowSec(t)) for t in ("stone", "copper", "iron", "silver", "gold", "thorium", "cobalt", "adamantite", "mithril", "onyxium", "gem", "logs", "crops")]
            == [3, 4, 5, 6, 6, 6, 8, 10, 12, 15, 30, 0, 0] and str(Cfg.placeholder("iron")) == "Rock_Bedrock" and str(Cfg.placeholder("logs")) == "Rock_Bedrock"
            and int(Cfg.regrowSec("nope")) == 5 and str(Cfg.placeholder("nope")) == "Rock_Bedrock" and int(Cfg.regrowSec(None)) == 5,
            "C: regen.properties defaults (spec Q2: stone 3 .. onyxium 15, gems 30; logs + crops 0 = Z3 later; bedrock; a type with no row = regen.defaultSec 5)")
    K.check((bool(Cfg.REGEN_ON), float(Cfg.SPEED), float(Cfg.JITTER), bool(Cfg.OFFLINE), int(Cfg.DEFSEC), int(Cfg.PASS), int(Cfg.MAXDEP)) == (True, 1.0, 0.2, True, 5, 200, 20000),
            "C: regen defaults (on, x1, 0.2, downtime counts, 5 s, 200 a pass, 20,000)")
    rtext = open(regf, encoding="utf8").read()
    open(regf, "a", encoding="utf8").write("regrow.Bad-Id=3,X\nregrow.copper2=abc\nregrow.badph=5,a/b\nregrow.iron=7|Rock_Bedrock\nregen.jitter=9\nregen.speedMult=0\nregen.passBatch=1\nregen.defaultSec=x\n")
    logged()
    rl_ = str(Cfg.loadRegen(False))
    lg_ = logged()
    K.check(Cfg.REGROW.size() == 13 and int(Cfg.regrowSec("iron")) == 7 and int(Cfg.regrowSec("copper2")) == 5 and sum(1 for l in lg_ if "regen.properties: 'regrow." in l) == 3
            and (float(Cfg.JITTER), float(Cfg.SPEED), int(Cfg.PASS), int(Cfg.DEFSEC)) == (0.5, 0.1, 10, 5),
            "C: bad regrow lines skipped + warned (their type falls back to defaultSec), a | line read, values clamped: %s %s" % (rl_, lg_))
    open(regf, "w", encoding="utf8").write(rtext)
    os.remove(regf)
    os.makedirs(regf)
    K.check(str(Cfg.loadRegen(False)) == "regen.properties could not be read - regrowing keeps its old settings" and Cfg.REGROW.size() == 13, "C: regen.properties unreadable -> the old settings stay")
    os.rmdir(regf)
    open(regf, "w", encoding="utf8").write(rtext)
    Cfg.reloadRegen()
    K.check(int(Cfg.regrowSec("iron")) == 5 and float(Cfg.SPEED) == 1.0 and any("regrow table re-read: regrowing ON (13 regrow rows)" in l for l in logged()), "C: reloadRegen (the kit's table routine)")
    CR_ = [("regrow[copper]", "4,Rock_Bedrock", None), ("regrow[copper]", "4|Rock_Bedrock", None), ("regrow[copper]", "0,none", None), ("regrow[copper]", "12", None),
           ("regrow[copper]", None, None), ("regrow[Bad]", "4", "A type id"), ("regrow[copper]", "x,Rock_Bedrock", "Write <seconds>"), ("regrow[copper]", "4000", "Write <seconds>"),
           ("regrow[copper]", "4,a b", "Write <seconds>"), ("regrow[copper]", "4,a,b", "Write <seconds>"), ("regrow[copper]", "4,No_Such_Block_X", "No block 'No_Such_Block_X'"),
           ("bogus", "4", "Unknown table line"),
           # fixer: a placeholder that is a listed block of a type is refused (it could be mined at once); logs / crops stay 0 until Z3
           ("regrow[copper]", "4,Rock_Stone", "The placeholder Rock_Stone is itself a block of type stone"),
           ("regrow[stone]", "3,Ore_Copper_Stone", "The placeholder Ore_Copper_Stone is itself a block of type copper"),
           ("regrow[logs]", "5,Rock_Bedrock", "logs cannot grow back yet"), ("regrow[crops]", "1", "crops cannot grow back yet"), ("regrow[logs]", "0,none", None)]
    got_ = [(k, v, Cfg.checkRegrow(k, v)) for k, v, w in CR_]
    K.check(all((g is None) if w is None else (g is not None and str(g).startswith(w)) for (k, v, g), (_, _, w) in zip(got_, CR_)),
            "C: checkRegrow (the regrow table's check: seconds 0-3600, a known placeholder block, removal ok): %s" % [(k, v, str(g)) for k, v, g in got_])
    K.check(bool(Rules.typeHas("copper", "Ore_Copper_Shale")) and not bool(Rules.typeHas("copper", "Ore_Iron")) and not bool(Rules.typeHas("nope", "x"))
            and bool(Rules.typeHas("logs", "Wood_Oak_Trunk")) and bool(Rules.typeHas("stone", "Rock_Basalt")) and not bool(Rules.anyGlob(None, "x"))
            and not bool(Rules.anyGlob(JArray(JString)(["*"]), "")), "C: typeHas / anyGlob")
    K.check(all(str(Rules.listedAny(b)) == "stone" for b in ("Rock_Stone_Cobble", "Rock_Shale_Cobble", "Rock_Basalt_Cobble", "Rock_Stone_Mossy"))
            and Rules.listedAny("Rock_Bedrock") is None and str(Rules.listedAny("Ore_Iron_Stone")) == "iron",
            "C: (fixer, spec 4.2 'Cobble') the stone type lists the cobbles + mossy stone; bedrock is no listed block")
    Props = JClass("java.util.Properties")
    pp_ = Props()
    pp_.setProperty("regrow.logs", "5,Rock_Bedrock")
    pp_.setProperty("regrow.crops", "2")
    pp_.setProperty("regrow.iron", "7,Rock_Bedrock")
    logged()
    pr_ = Cfg.parseRegrow(pp_)
    K.check(int(pr_.get("logs")[0]) == 0 and int(pr_.get("crops")[0]) == 0 and int(pr_.get("iron")[0]) == 7 and sum(1 for l in logged() if "cannot regrow yet" in l) == 2,
            "C: (fixer) a hand-edited logs / crops row above 0 is read as 0 (warned) until Z3")

    # ---------------------------------------------------------------- G: regions
    Sto.SYNC = True
    rr = Reg()
    K.check(list(Reg.norm(5, 1, 9, 2, 3, 4)) == [2, 1, 4, 5, 3, 9], "G: norm")
    K.check(str(Reg.boxProblem(JArray(JInt)([0, 0, 0, 511, 383, 511]))) == "" and "at most 512 x 384 x 512" in str(Reg.boxProblem(JArray(JInt)([0, 0, 0, 512, 0, 0])))
            and "y must stay" in str(Reg.boxProblem(JArray(JInt)([0, -65, 0, 1, 1, 1]))) and str(Reg.boxProblem(None)) == "no box", "G: boxProblem")
    bx = Reg.parseBoxes("10,5,-3..0,9,4; -1,0,0..1,2,3")
    K.check(bx is not None and list(bx) == [0, 5, -3, 10, 9, 4, -1, 0, 0, 1, 2, 3] and str(Reg.boxText(bx)) == "0,5,-3..10,9,4;-1,0,0..1,2,3", "G: parseBoxes normalises, boxText")
    K.check(all(Reg.parseBoxes(s) is None for s in (None, "", "1,2..3,4,5", "a,b,c..1,2,3", "0,0,0..600,1,1", ";".join(["0,0,0..1,1,1"] * 65), "1,2,3"))
            and Reg.parseBoxes(";".join(["0,0,0..1,1,1"] * 64)) is not None, "G: parseBoxes refuses bad text / too big / 65 boxes (64 ok, spec 5.3)")
    K.check(Reg.modeOf(" SkyBlock ") == 1 and Reg.modeOf("full") == 0 and Reg.modeOf("x") == -1 and Reg.modeOf(None) == -1, "G: modeOf")
    pw_home = home
    who = "Skyy"

    def ftext():
        return open(os.path.join(home, "regions.properties"), encoding="utf8").read()
    box1 = JArray(JInt)([0, 60, 0, 20, 80, 20])
    K.eq(str(Sto.create("mine", WORLD, "skyblock", box1, who)), "Region mine created (skyblock) in %s: 21 x 21 x 21 blocks. Nothing breaks there until you list its resource types: /zones region types mine stone,copper" % WORLD, "G: create skyblock")
    K.check(ftext() == str(Sto.text()) and "region.mine.boxes=0,60,0..20,80,20\n" in ftext() and "region.mine.mode=skyblock" in ftext(), "G: the file = the text after create")
    for args_, want in ((("mine", WORLD, "full", box1), "!Region mine already exists"), (("Bad!", WORLD, "full", box1), "!A region id"),
                        (("x", WORLD, "wet", box1), "!The mode is full or skyblock."), (("x", WORLD, "full", JArray(JInt)([0, 0, 0, 900, 0, 0])), "!a box may be at most")):
        K.check(str(Sto.create(*(list(args_) + [who]))).startswith(want), "G: create refused: %s" % want)
    K.check(str(Sto.set("mine", "types", "stone,copper", who)) == "Region mine: types = stone,copper." and list(map(str, Sto.get("mine").types)) == ["stone", "copper"], "G: types")
    K.check(str(Sto.set("mine", "types", "stone,nope", who)).startswith("!No resource type 'nope'. Types: adamantite, cobalt, copper"), "G: unknown type refused")
    K.check(str(Sto.set("mine", "priority", "5", who)) == "Region mine: priority = 5." and str(Sto.set("mine", "priority", "x", who)).startswith("!")
            and str(Sto.set("mine", "priority", "1001", who)).startswith("!"), "G: priority (+ refusals)")
    K.check(str(Sto.set("mine", "title", "Copper_Mine", who)) == "Region mine: title = Copper Mine." and str(Sto.set("mine", "title", "<bad>", who)).startswith("!")
            and str(Sto.set("mine", "title", "x" * 41, who)).startswith("!"), "G: title (_ = space, refusals)")
    K.check(str(Sto.set("mine", "flags", "furnaces", who)) == "Region mine: flags = furnaces." and bool(Sto.get("mine").fFurn) and not bool(Sto.get("mine").fCont)
            and str(Sto.set("mine", "flags", "doors", who)).startswith("!"), "G: flags")
    K.check(str(Sto.set("mine", "mode", "wet", who)).startswith("!") and str(Sto.set("nope", "mode", "full", who)) == "!No region nope."
            and str(Sto.set("mine", "colour", "x", who)).startswith("!Unknown region setting"), "G: set refusals")
    K.check(str(Sto.create("town", WORLD, "full", JArray(JInt)([5, 60, 5, 15, 90, 15]), who)).endswith("Nothing breaks or is placed there now."), "G: create full")
    K.check("(It is a FULL region" in str(Sto.set("town", "types", "stone", who)), "G: types on a FULL region explain the mode")
    Sto.set("town", "types", "none", who)
    K.check(str(Sto.set("town", "priority", "10", who)).endswith("= 10.") and str(Sto.set("town", "title", "Town", who)).endswith("= Town."), "G: town priority 10 + title")
    K.check(str(Sto.addBox("mine", OTHER, JArray(JInt)([0, 0, 0, 1, 1, 1]), who)).startswith("!Region mine is in world") and
            str(Sto.addBox("nope", WORLD, box1, who)) == "!No region nope." and
            str(Sto.addBox("mine", WORLD, JArray(JInt)([0, 0, 0, 999, 1, 1]), who)).startswith("!a box"), "G: addbox refusals")
    K.check(str(Sto.addBox("mine", WORLD, JArray(JInt)([100, 60, 100, 101, 61, 101]), who)) == "Box 2 added to mine (2 x 2 x 2 blocks).", "G: addbox")
    for i in range(62):
        Sto.addBox("mine", WORLD, JArray(JInt)([200 + i, 0, 0, 200 + i, 0, 0]), who)
    K.check(Sto.get("mine").boxes() == 64 and str(Sto.addBox("mine", WORLD, box1, who)).startswith("!Region mine already has 64 boxes"), "G: the 64-box cap (spec 5.3)")
    hist = os.path.join(home, "history")
    K.check(os.path.isdir(hist) and len(os.listdir(hist)) == 10, "G: history keeps the newest 10 copies: %d" % (len(os.listdir(hist)) if os.path.isdir(hist) else -1))
    chg = open(os.path.join(home, "region-changes.log"), encoding="utf8").read().splitlines()
    K.check(len(chg) >= 50 and chg[0].endswith("\tSkyy\tcreate mine skyblock in %s 0,60,0..20,80,20" % WORLD), "G: one change-log line per change: %d" % len(chg))
    K.check(str(Sto.create("other1", OTHER, "full", box1, who)).startswith("Region other1 created"), "G: a region in a second world")
    import time
    hist_keep = os.path.join(SCRATCH, "histkeep")
    # ---- restart reload = the same regions
    before = dict((str(k), str(Sto.get(k).summary())) for k in ("mine", "town", "other1"))
    btext = str(Sto.text())
    Sto.REGIONS.clear()
    Sto.publish()
    r2 = str(Sto.load())
    K.check(r2 == "3 regions in 2 worlds" and dict((k, str(Sto.get(k).summary())) for k in before) == before and str(Sto.text()) == btext,
            "G: RESTART RELOAD - the file gives back the same 3 regions: %s" % r2)
    K.check([str(x.id) for x in getattr(Sto.INDEX, "in_")(WORLD)] == ["town", "mine"], "G: index order = priority (town 10 before mine 5)")
    # ---- delete
    K.check(str(Sto.delete("other1", who)) == "Region other1 deleted." and str(Sto.delete("other1", who)) == "!No region other1."
            and not Sto.INDEX.has(OTHER), "G: delete")
    # ---- bad file: edits blocked, the good regions keep protecting, nothing overwritten
    good = ftext()
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good + "region.broken.world=%s\nregion.broken.boxes=1,2\nregion.zzz.colour=red\n" % WORLD)
    r3 = str(Sto.load())
    K.check(r3.startswith("2 regions in 1 worlds - PROBLEM:") and Sto.BAD is not None and Sto.get("mine") is not None and Sto.get("broken") is None,
            "G: a bad region is skipped, the good ones load: %s" % r3)
    K.check(str(Sto.create("x", WORLD, "full", box1, who)).startswith("!The regions file has a problem") and str(Sto.set("mine", "priority", "1", who)).startswith("!The regions file")
            and str(Sto.delete("mine", who)).startswith("!The regions file") and str(Sto.addBox("mine", WORLD, box1, who)).startswith("!The regions file"),
            "G: every edit is blocked while the file is bad")
    K.check("region.broken.world" in ftext(), "G: the bad file is never overwritten")
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good)
    K.check(str(Sto.load()) == "2 regions in 1 worlds" and Sto.BAD is None, "G: fixed + reload -> edits allowed again")
    for bad_line, kept in (("region.q.world=a/b\nregion.q.boxes=0,0,0..1,1,1\n", False), ("region.q.world=w\nregion.q.mode=x\nregion.q.boxes=0,0,0..1,1,1\n", True),
                           ("region.q.world=w\nregion.q.priority=x\nregion.q.boxes=0,0,0..1,1,1\n", True),
                           ("region.q.world=w\nregion.q.priority=5000\nregion.q.boxes=0,0,0..1,1,1\n", True),
                           ("region.q.world=w\nregion.q.mode=skyblock\nregion.q.types=A!\nregion.q.boxes=0,0,0..1,1,1\n", True),
                           ("region.q.world=w\nregion.q.flags=pvp\nregion.q.boxes=0,0,0..1,1,1\n", True),
                           ("region.q.world=w\nregion.q.title=<x>\nregion.q.boxes=0,0,0..1,1,1\n", True)):
        open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good + bad_line)
        Sto.REGIONS.remove("q")
        Sto.load()
        q_ = Sto.get("q")
        K.check(Sto.BAD is not None and ((q_ is None) if not kept else (q_ is not None and int(q_.mode) == 0 and len(q_.types) == 0 and str(q_.flags) == ""
                                                                          and int(Rules.decide(Sto.INDEX, "w", False, 1, 1, 1, int(Rules.BREAK), "Rock_Stone")) != int(Rules.ALLOW))),
                "G: a NEW bad region (no copy anywhere) %s: %r" % ("protects as FULL with its boxes (fail closed)" if kept else "with no readable world is left out", bad_line))
    # C1 #1: a GOOD region whose lines turn bad keeps protecting as its last good version (reload) / its newest history copy (restart)
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good)
    Sto.load()
    mine_before = str(Sto.get("mine").summary())
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good.replace("region.mine.boxes=", "region.mine.boxes=1,2,x;"))
    logged()
    r5 = str(Sto.load())
    K.check(Sto.get("mine") is not None and str(Sto.get("mine").summary()) == mine_before and Sto.BAD is not None and "1 bad region keeps protecting" in r5
            and any("keeps protecting as before" in l for l in logged()), "G: reload - a typo in a good region keeps its last good version protecting: %s" % r5)
    K.check(int(Rules.decide(Sto.INDEX, WORLD, False, 5, 70, 5, int(Rules.BREAK), "Ore_Iron_Stone")) != int(Rules.ALLOW), "G: ... and the guard still refuses inside it")
    Sto.REGIONS.clear()
    Sto.publish()
    r6 = str(Sto.load())
    K.check(Sto.get("mine") is not None and str(Sto.get("mine").summary()) == mine_before and any("last good copy (regions.good.properties / history/)" in l for l in logged()),
            "G: restart - the typo'd region comes back from its last good copy: %s" % r6)
    goodf = os.path.join(home, "regions.good.properties")
    K.check(os.path.isfile(goodf) and open(goodf, encoding="utf8").read() == good, "G: regions.good.properties = the last clean text (written by every save / clean load)")
    hist_keep = os.path.join(SCRATCH, "histkeep")
    good_keep = os.path.join(SCRATCH, "goodkeep")
    shutil.move(os.path.join(home, "history"), hist_keep)
    Sto.REGIONS.clear()
    Sto.publish()
    Sto.load()
    K.check(Sto.get("mine") is not None and str(Sto.get("mine").summary()) == mine_before and int(Rules.decide(Sto.INDEX, WORLD, False, 5, 70, 5, int(Rules.BREAK), "Ore_Iron_Stone")) != int(Rules.ALLOW),
            "G: 0.1.0 CRITIC FAIL-OPEN CASE - restart, NO history/, a typo in the boxes line: regions.good.properties alone keeps the region protecting")
    shutil.move(goodf, good_keep)
    Sto.REGIONS.clear()
    Sto.publish()
    logged()
    Sto.load()
    lg_ = logged()
    K.check(Sto.get("mine") is None and bool(Cfg.protectedWorld(WORLD)) and any("the WHOLE WORLD %s is protected" % WORLD in l for l in lg_)
            and int(Rules.decide(Sto.INDEX, WORLD, bool(Cfg.protectedWorld(WORLD)), 500, 70, 500, int(Rules.BREAK), "Rock_Stone")) != int(Rules.ALLOW)
            and not bool(Cfg.protectedWorld(OTHER)), "G: no good copy anywhere + no readable box - its WHOLE world is locked FULL (fail closed, warned), other worlds untouched: %s" % lg_)
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good.replace("region.mine.types=", "region.mine.types=B@D,"))
    Sto.load()
    K.check(Sto.get("mine") is not None and int(Sto.get("mine").mode) == 0 and any("protects as a FULL region" in l for l in logged()) and not bool(Cfg.protectedWorld(WORLD)),
            "G: restart, no copy, readable boxes - the bad SKYBLOCK region protects as FULL (the world lock is lifted by the next load)")
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good.replace("region.mine.world=", "region.mine.world=a/").replace("region.mine.boxes=", "region.mine.boxes=x"))
    Sto.REGIONS.clear()
    Sto.publish()
    Sto.load()
    K.check(Sto.get("mine") is None and any("no readable world - it does NOT protect" in l for l in logged()) and not bool(Cfg.protectedWorld(WORLD)),
            "G: no copy, no readable world (nor box) - left out, warned (nothing to protect with)")
    shutil.move(hist_keep, os.path.join(home, "history"))
    shutil.move(good_keep, goodf)
    open(os.path.join(home, "regions.properties"), "w", encoding="utf8").write(good)
    Sto.load()
    rp = os.path.join(home, "regions.properties")
    os.remove(rp)
    os.makedirs(rp)
    r4 = str(Sto.load())
    K.check(r4 == "regions.properties UNREADABLE (2 regions kept)" and Sto.get("mine") is not None and Sto.BAD is not None, "G: unreadable file -> memory kept, edits blocked")
    os.rmdir(rp)
    open(rp, "w", encoding="utf8").write(good)
    Sto.load()
    # fixer 2 (critic 2 #1): a MISSING file / one with NO region line never drops the regions in memory; only /zones reload clear accepts it
    os.remove(rp)
    r8 = str(Sto.load())
    K.check(r8 == "regions.properties MISSING (2 regions kept; /zones reload clear removes them)" and Sto.BAD is not None and Sto.get("mine") is not None
            and str(Sto.create("x", WORLD, "full", box1, who)).startswith("!The regions file has a problem") and not os.path.exists(rp)
            and int(Rules.decide(Sto.INDEX, WORLD, False, 5, 70, 5, int(Rules.BREAK), "Ore_Iron_Stone")) != int(Rules.ALLOW),
            "G: reload with the file MISSING - the 2 regions keep protecting, edits blocked, nothing written: %s" % r8)
    for txt_, nm_ in (("# only a comment\n", "comments only"), ("", "zero bytes")):
        open(rp, "w", encoding="utf8").write(txt_)
        r9 = str(Sto.load())
        K.check(r9 == "regions.properties EMPTY (2 regions kept; /zones reload clear removes them)" and Sto.BAD is not None and Sto.get("town") is not None
                and open(rp, encoding="utf8").read() == txt_, "G: reload with the file EMPTY (%s) - regions kept, edits blocked: %s" % (nm_, r9))
    open(rp, "w", encoding="utf8").write("# no regions on purpose\n")
    hist_n = len(os.listdir(hist))
    logged()
    r10 = str(Sto.load(True))
    newest_ = sorted(os.listdir(hist))[-1]
    K.check(r10 == "0 regions in 0 worlds" and Sto.BAD is None and Sto.get("mine") is None and "region.mine.world" in open(os.path.join(hist, newest_), encoding="utf8").read()
            and any("reload clear: every region removed (2)" in l for l in logged()) and "/zones reload clear\tevery region removed (2" in open(os.path.join(home, "region-changes.log"), encoding="utf8").read(),
            "G: /zones reload clear accepts the empty file, the old text kept in history/ (%d -> %d copies): %s" % (hist_n, len(os.listdir(hist)), r10))
    K.check(str(Sto.load()) == "0 regions in 0 worlds" and Sto.BAD is None, "G: a restart with a comments-only file = no regions on purpose (never restored)")
    os.remove(rp)
    r11 = str(Sto.load())
    K.check(r11 == "2 regions in 1 worlds (RESTORED from regions.good.properties)" and Sto.BAD is None and Sto.get("mine") is not None and ftext() == good
            and any("was missing - the 2 regions of regions.good.properties" in l for l in logged()), "G: a start with the file MISSING - the last good copy is restored + written back: %s" % r11)
    Sto.REGIONS.clear()
    Sto.publish()
    open(rp, "w", encoding="utf8").write("  \n")
    r12 = str(Sto.load())
    K.check("RESTORED from regions.good.properties" in r12 and Sto.get("town") is not None and ftext() == good, "G: a start with a BLANK file - restored too: %s" % r12)
    # engine #1: an unreadable file at a start (nothing in memory) - the newest history copy protects; 3 tries 100 ms apart first
    Sto.REGIONS.clear()
    Sto.publish()
    os.remove(rp)
    os.makedirs(rp)
    logged()
    t0_ = time.time()
    r13 = str(Sto.load())
    dt_ = time.time() - t0_
    K.check(r13 == "regions.properties UNREADABLE (2 regions from regions.good.properties protect)" and Sto.BAD is not None and Sto.get("mine") is not None
            and int(Rules.decide(Sto.INDEX, WORLD, False, 5, 70, 5, int(Rules.BREAK), "Ore_Iron_Stone")) != int(Rules.ALLOW)
            and dt_ >= 0.18 and any("(3 tries)" in l for l in logged()), "G: a start with the file UNREADABLE - history protects, edits blocked, read 3 times (%.2f s): %s" % (dt_, r13))
    shutil.move(hist, hist_keep)
    shutil.move(goodf, good_keep)
    Sto.REGIONS.clear()
    Sto.publish()
    r14 = str(Sto.load())
    K.check(r14 == "regions.properties UNREADABLE - NO region protects" and any("NO region protects" in l for l in logged()), "G: ... and with no history - says so loudly: %s" % r14)
    shutil.move(hist_keep, hist)
    shutil.move(good_keep, goodf)
    os.rmdir(rp)
    open(rp, "w", encoding="utf8").write(good)
    K.check(str(Sto.load()) == "2 regions in 1 worlds" and Sto.BAD is None, "G: (back to the good file)")
    os.remove(goodf)
    Sto.REGIONS.clear()
    Sto.publish()
    os.remove(rp)
    r17 = str(Sto.load())
    K.check(r17.startswith("2 regions in 1 worlds (RESTORED from history/regions.") and ftext() == good and os.path.isfile(goodf),
            "G: no regions.good.properties (an upgrade from 0.1.0) - a missing file still comes back from history/, and the good copy is written: %s" % r17)
    # critic 3 #1: spec 5.3 placeAllow / gate (later phases) and other region.<id>.<field> lines are kept verbatim, never a problem
    open(rp, "w", encoding="utf8").write(good + "region.mine.placeAllow=Scaffolding_+\nregion.mine.gate=Mining:0\nregion.mine.prority=3\nregion.mine.note=a\\\\b\n")
    logged()
    r15 = str(Sto.load())
    lg_ = logged()
    ex_ = Sto.get("mine").extra
    K.check(r15 == "2 regions in 1 worlds" and Sto.BAD is None and str(ex_.get("placeAllow")) == "Scaffolding_+" and str(ex_.get("gate")) == "Mining:0" and str(ex_.get("note")) == "a\\b"
            and any("'region.mine.prority' is not used by SkyyZones" in l for l in lg_) and not any("placeAllow" in l or "region.mine.gate" in l for l in lg_),
            "G: placeAllow / gate kept quietly, an unknown field kept + warned, no problem: %s %s" % (r15, lg_))
    Sto.set("mine", "priority", "5", who)
    ft_ = ftext()
    K.check("region.mine.placeAllow=Scaffolding_+\n" in ft_ and "region.mine.gate=Mining:0\n" in ft_ and "region.mine.prority=3\n" in ft_ and "region.mine.note=a\\\\b\n" in ft_,
            "G: ... and written back verbatim on the next edit (a backslash stays one)")
    Sto.REGIONS.clear()
    Sto.publish()
    K.check(str(Sto.load()) == "2 regions in 1 worlds" and str(Sto.get("mine").extra.get("note")) == "a\\b" and str(Sto.get("mine").copy().extra.get("gate")) == "Mining:0",
            "G: ... a restart reads them back the same; copy() keeps them")
    open(rp, "w", encoding="utf8").write(good + "region.solo.gate=Mining:0\n")
    r16 = str(Sto.load())
    K.check("PROBLEM: region solo: bad " in r16 and Sto.get("solo") is None, "G: a region with only later-phase lines (no world) is a problem: %s" % r16)
    open(rp, "w", encoding="utf8").write(good)
    Sto.load()
    K.check(Sto.get("mine").extra.isEmpty() and "placeAllow" not in str(Sto.text()), "G: lines removed by hand are gone after a reload")
    # async save path (the scheduler; in the bare JVM it may run inline) + flush
    Sto.SYNC = False
    w0 = int(Save.WRITES.get())
    Sto.set("mine", "priority", "6", who)
    import time
    for _ in range(50):
        if int(Save.WRITES.get()) > w0:
            break
        time.sleep(0.1)
    K.check(int(Save.WRITES.get()) > w0 and "region.mine.priority=6" in ftext(), "G: the scheduled save writes the file")
    # C1 #2: a reload right after an edit keeps the edit (a pending write lands first); a write that never lands = ~1 s wait, warned, disk read
    Sto.set("mine", "priority", "7", who)
    r7 = str(Sto.load())
    K.check(int(Sto.get("mine").priority) == 7 and "region.mine.priority=7" in ftext(), "G: /zones reload right after an edit keeps the edit: %s" % r7)
    Sto.SYNC = True
    Sto.LAST_SEQ = JLong(int(Save.written()) + 1000)
    logged()
    t0_ = time.time()
    Sto.load()
    dt_ = time.time() - t0_
    K.check(0.9 <= dt_ < 3.0 and any("write is still pending" in l for l in logged()), "G: a write that never lands - reload waits ~1 s, warns, reads the disk (%.2f s)" % dt_)
    Sto.LAST_SEQ = JLong(int(Save.written()))
    Sto.SYNC = False
    Sto.SYNC = True
    Save.WRITTEN = JLong(0)
    os.remove(rp)
    Sto.flush()
    K.check(os.path.isfile(rp) and ftext() == str(Sto.LAST_TEXT), "G: flush writes the newest text")
    K.check(not bool(Save.write(JLong(1), "old", None)) and ftext() == str(Sto.LAST_TEXT), "G: an older text never overwrites a newer one")
    Save.prune()
    K.check(str(Sto.typeList()).startswith("adamantite, cobalt, copper") and Reg().boxes() == 0, "G: typeList, empty region")

    # ---------------------------------------------------------------- D: decide matrix (indexes built directly)
    def region(id_, w, mode, prio, box, types=(), flags=""):
        g = Reg()
        g.id, g.world, g.mode, g.priority, g.box = id_, w, mode, prio, JArray(JInt)(box)
        g.types = JArray(JString)(list(types))
        g.setFlags(flags)
        return g

    def ix(*regs):
        l = AL()
        for g in regs:
            l.add(g)
        return Idx.build(l)
    BRK, PLC, CON, FUR, OTH = (int(getattr(Rules, n)) for n in ("BREAK", "PLACE", "CONTAINER", "FURNACE", "OTHER"))
    ALW, DNY, NRS, LCK, NPL = (int(getattr(Rules, n)) for n in ("ALLOW", "DENY", "NOT_RES", "LOCKED", "NO_PLACE"))
    e0 = ix()
    K.check([int(Rules.decide(e0, "w", False, 0, 0, 0, a, "Rock_Stone")) for a in (BRK, PLC, CON, FUR, OTH)] == [ALW] * 5, "D: unprotected world, no region = all allowed")
    K.check([int(Rules.decide(e0, "w", True, 0, 0, 0, a, "Rock_Stone")) for a in (BRK, PLC, CON, FUR, OTH)] == [DNY, NPL, LCK, LCK, ALW],
            "D: protected world, no region = FULL default (break / place / chests / furnaces refused, other uses ok)")
    K.check(int(Rules.decide(None, "w", True, 0, 0, 0, BRK, "x")) == DNY, "D: no index")
    full = region("t", "w", 0, 0, [0, 0, 0, 9, 9, 9])
    K.check(int(Rules.decide(ix(full), "w", False, 5, 5, 5, BRK, "Ore_Copper")) == DNY and int(Rules.decide(ix(full), "w", False, 50, 5, 5, BRK, "x")) == ALW
            and int(Rules.decide(ix(full), "w", False, 9, 9, 9, BRK, "x")) == DNY and int(Rules.decide(ix(full), "w", False, 10, 9, 9, BRK, "x")) == ALW
            and int(Rules.decide(ix(full), "other", False, 5, 5, 5, BRK, "x")) == ALW, "D: a FULL region in an unprotected world (inside / edge / outside / other world)")
    sky = region("m", "w", 1, 0, [0, 0, 0, 9, 9, 9], ("stone", "copper"))
    K.check([int(Rules.decide(ix(sky), "w", False, 1, 1, 1, BRK, b)) for b in ("Rock_Stone", "Ore_Copper_Stone", "*Ore_Copper_Stone_State_Definitions_X", "Ore_Iron_Stone", "")]
            == [ALW, ALW, ALW, NRS, NRS] and int(Rules.decide(ix(sky), "w", False, 1, 1, 1, PLC, "Rock_Stone")) == NPL, "D: SKYBLOCK listed allowed, unlisted refused, no placing")
    top_full = region("a_town", "w", 0, 10, [0, 0, 0, 4, 9, 9])
    K.check(int(Rules.decide(ix(sky, top_full), "w", False, 2, 2, 2, BRK, "Rock_Stone")) == DNY and int(Rules.decide(ix(sky, top_full), "w", False, 7, 2, 2, BRK, "Rock_Stone")) == ALW,
            "D: overlap - a FULL region with higher priority wins where it covers")
    vein = region("vein", "w", 1, 10, [0, 0, 0, 4, 9, 9], ("iron",))
    K.check([int(Rules.decide(ix(sky, vein), "w", False, 2, 2, 2, BRK, b)) for b in ("Ore_Iron_Stone", "Rock_Stone", "Ore_Gold")] == [ALW, ALW, NRS]
            and int(Rules.decide(ix(sky, vein), "w", False, 7, 2, 2, BRK, "Ore_Iron_Stone")) == NRS, "D: overlap - SKYBLOCK over SKYBLOCK = the union of their types, only where both cover")
    low_full = region("base", "w", 0, -5, [0, 0, 0, 30, 30, 30])
    K.check(int(Rules.decide(ix(sky, low_full), "w", False, 2, 2, 2, BRK, "Rock_Stone")) == ALW and int(Rules.decide(ix(sky, low_full), "w", False, 20, 2, 2, BRK, "Rock_Stone")) == DNY,
            "D: a SKYBLOCK region over a lower FULL one lets its types break")
    tie_a, tie_b = region("aa", "w", 0, 3, [0, 0, 0, 1, 1, 1]), region("bb", "w", 1, 3, [0, 0, 0, 1, 1, 1], ("stone",))
    K.check(str(ix(tie_b, tie_a).top("w", 0, 0, 0).id) == "bb" and int(Rules.decide(ix(tie_b, tie_a), "w", False, 0, 0, 0, BRK, "Rock_Stone")) == ALW,
            "D: equal priority - a SKYBLOCK region wins over a FULL one (fixer 2: a mine drawn inside a town gathers), whatever the names")
    tie_c = region("cc", "w", 0, 3, [0, 0, 0, 1, 1, 1])
    K.check(str(ix(tie_c, tie_a).top("w", 0, 0, 0).id) == "aa" and str(ix(region("zz", "w", 1, 3, [0, 0, 0, 1, 1, 1]), tie_b).top("w", 0, 0, 0).id) == "bb",
            "D: equal priority + equal mode - the smaller id wins")
    flg = region("shop", "w", 0, 0, [0, 0, 0, 9, 9, 9], (), "containers,furnaces")
    K.check([int(Rules.decide(ix(flg), "w", False, 1, 1, 1, a, "x")) for a in (CON, FUR, BRK)] == [ALW, ALW, DNY], "D: region flags containers / furnaces")
    K.check(str(ix(sky, vein).topTitled("w", 2, 2, 2)) == "None" and ix(sky).at("w", 50, 50, 50).isEmpty() and bool(sky.near(12, 1, 1, 3)) and not bool(sky.near(13, 1, 1, 3)),
            "D: topTitled none, at outside, near")
    K.check([str(Rules.why(c)) for c in (DNY, NRS, LCK, NPL)] == ["This area is protected.", "You can only gather the marked resource blocks here.",
                                                                    "That is locked in this area.", "You can't place blocks in this area."]
            and str(Rules.verdict(ALW)) == "allowed" and str(Rules.verdict(DNY)) == "refused - This area is protected.", "D: why / verdict texts")
    # useKind table + useAction on REAL block types (fields set by reflection)
    UK = [((True, False, False, False, False, False, False, False, "Tool_Hoe_Iron"), OTH), ((False, True, False, False, False, False, False, False, None), OTH),
          ((False, False, True, False, False, False, False, False, None), OTH), ((False, False, False, True, False, False, False, False, None), FUR),
          ((False, False, False, False, True, False, False, False, None), OTH), ((False, False, False, False, False, True, False, False, None), OTH),
          ((False, False, False, False, False, False, True, False, None), BRK), ((False, False, False, False, False, False, False, True, None), CON),
          ((False, False, False, False, False, False, False, False, "Tool_Hoe_Iron"), BRK), ((False, False, False, False, False, False, False, False, "Container_Bucket"), BRK),
          ((False, False, False, False, False, False, False, False, "Tool_Pickaxe_Iron"), OTH), ((False, False, False, False, False, False, False, False, None), OTH)]
    K.check(all(int(Rules.useKind(*a)) == w for a, w in UK), "D: useKind table: %s" % [a for a, w in UK if int(Rules.useKind(*a)) != w])

    def setf(cls, inst, name, v):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(inst, v)
    proc = U.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench").class_)
    craft = U.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench").class_)
    setf(Bench, proc, "type", BenchType.Processing)
    setf(Bench, craft, "type", BenchType.Crafting)
    setf(BT, bt("Bench_Furnace"), "bench", proc)
    setf(BT, bt("Bench_Workbench"), "bench", craft)
    setf(BT, bt("Furniture_Door"), "isDoor", JBoolean(True))
    im = HM()
    im.put(ITY.Use, "Open_Container")
    setf(BT, bt("Furniture_Crude_Chest"), "interactions", im)
    fd = U.allocateInstance(Farm.class_)
    stg_f = [f for f in Farm.class_.getDeclaredFields() if str(f.getName()) == "stages"]
    if stg_f:
        stg_f[0].setAccessible(True)
        stg_f[0].set(fd, HM())
    setf(BT, bt("Plant_Crop_Carrot_Block"), "farming", fd)
    UA = [("Bench_Furnace", ITY.Use, None, FUR), ("Bench_Workbench", ITY.Use, None, OTH), ("Furniture_Door", ITY.Secondary, "Tool_Hoe_Iron", OTH),
          ("Furniture_Crude_Chest", ITY.Use, None, CON), ("Plant_Crop_Carrot_Block", ITY.Use, None, BRK), ("Soil_Grass", ITY.Secondary, "Tool_Hoe_Iron", BRK),
          ("Soil_Grass", ITY.Use, None, OTH), ("Rock_Stone", ITY.Primary, None, BRK), ("Skyy_Island_Hub_Portal", ITY.Use, "Tool_Hoe_Iron", OTH),
          ("Rock_Stone", ITY.Pick, None, OTH)]
    got = [(n, int(Rules.useAction(bt(n), t, h))) for n, t, h, w in UA]
    K.check(all(g == w for (n, g), (_, _, _, w) in zip(got, UA)) and int(Rules.useAction(None, ITY.Use, None)) == OTH and int(Rules.useAction(bt("Rock_Stone"), None, None)) == OTH,
            "D: useAction on real block types (furnace, workbench, door, chest, crop, hoe on grass, plain use, primary, Skyy portal, other type): %s" % got)

    # ---------------------------------------------------------------- the stand-in world / store / players
    def mkworld(name):
        w = U.allocateInstance(FW.class_)
        jfield(WLD, "name").set(w, name)
        es = U.allocateInstance(EST.class_)
        jfield(EST, "world").set(es, w)
        st = U.allocateInstance(MS.class_)
        st.comps = IHM()
        st.ext = es
        return w, st
    wA, stA = mkworld(WORLD)
    wO, stO = mkworld(OTHER)
    wI, stI = mkworld(ISLAND)
    cb = U.allocateInstance(MB.class_)
    nref = [0]

    def mkref(st):
        nref[0] += 1
        r_ = REF(st, JInt(nref[0]))
        st.comps.put(r_, IHM())
        return r_

    def mkplayer(st, name, n, x, y, z, admin=False, builder=False):
        r_ = mkref(st)
        pr_ = U.allocateInstance(FP.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-4000-8000-%012x" % (0xb000 + n)))
        jfield(PRc, "username").set(pr_, name)
        pr_.msgs = AL()
        st.comps.get(r_).put(PRc.getComponentType(), pr_)
        tc = TC(V3D(x, y, z), R3(0.0, 0.0, 0.0))
        st.comps.get(r_).put(TC.getComponentType(), tc)
        perms[(str(pr_.getUuid()), "skyyzones.admin")] = admin
        perms[(str(pr_.getUuid()), "skyyzones.build")] = admin or builder
        ch = U.allocateInstance(MCH.class_)
        ch.ref = r_
        return {"ref": r_, "pr": pr_, "tc": tc, "ch": ch, "st": st, "u": pr_.getUuid()}
    A = mkplayer(stA, "Skyy", 1, 2.5, 70.0, 2.5, admin=True)
    Gst = mkplayer(stA, "Guest", 2, 2.5, 70.0, 2.5)
    Bd = mkplayer(stA, "Builder", 3, 2.5, 70.0, 2.5, builder=True)
    mob_ref = mkref(stA)
    mob = U.allocateInstance(MCH.class_)
    mob.ref = mob_ref

    def said(p):
        r_ = [str(m.getRawText()) for m in p["pr"].msgs]
        p["pr"].msgs.clear()
        return r_

    def notes():
        r_ = list(api.notes)
        del api.notes[:]
        return r_
    gB, gD, gP, gU = (P(n)() for n in ("ZGuardBreak", "ZGuardDamage", "ZGuardPlace", "ZGuardUse"))

    def item(i):
        if i is None:
            return None
        try:
            return IS(i, 1)
        except Exception:
            s_ = U.allocateInstance(IS.class_)
            for fn_, v_ in (("itemId", i), ("quantity", JInt(1))):
                f_ = IS.class_.getDeclaredField(fn_)
                f_.setAccessible(True)
                f_.set(s_, v_)
            return s_

    def ctx_with(held):
        c = U.allocateInstance(ICTX.class_)
        if held is not None:
            f = ICTX.class_.getDeclaredField("heldItem")
            f.setAccessible(True)
            f.set(c, item(held))
        return c

    def ev(kind, x, y, z, block="Rock_Stone", held=None, ity=None):
        if kind == "break":
            return gB, BBE(item(held), V3I(x, y, z), bt(block))
        if kind == "dig":
            return gD, DBE(item(held), V3I(x, y, z), bt(block), JFloat(1.0), JFloat(0.5))
        if kind == "place":
            return gP, PLBE(item(held or "Rock_Stone"), V3I(x, y, z), None)
        return gU, UBP(ity or ITY.Use, ctx_with(held), V3I(x, y, z), bt(block))

    def fire(p, kind, x, y, z, **kw):
        g_, e_ = ev(kind, x, y, z, **kw)
        Msg.LAST.clear()
        g_.handle(0, p["ch"] if isinstance(p, dict) else p, (p["st"] if isinstance(p, dict) else stA), cb, e_)
        return bool(e_.isCancelled())
    # regions for the guard run: mine (skyblock, stone+copper, prio 5) + town (full, prio 10, title Town) in WORLD
    Sto.REGIONS.clear()
    Sto.publish()
    Sto.create("mine", WORLD, "skyblock", JArray(JInt)([0, 60, 0, 20, 80, 20]), who)
    Sto.set("mine", "types", "stone,copper", who)
    Sto.set("mine", "title", "Copper Mine", who)
    Sto.set("mine", "priority", "5", who)
    Sto.create("town", WORLD, "full", JArray(JInt)([30, 60, 0, 40, 80, 10]), who)
    Sto.set("town", "title", "Town", who)
    Sto.set("town", "flags", "containers", who)
    logged()
    Cfg.REGEN_ON = False   # phase X = the 0.1.0 guard behaviour (regrowing off); phase R below runs with it on
    # FULL
    K.check(fire(Gst, "break", 35, 70, 5) and notes() == [("Guest", "This area is protected.")], "X: FULL - break refused (no drop: cancelled in the handler) + note")
    K.check(fire(Gst, "dig", 35, 70, 5) and fire(Gst, "place", 35, 70, 5) and notes() == [("Guest", "This area is protected."), ("Guest", "You can't place blocks in this area.")],
            "X: FULL - dig (no crack) + place refused")
    Msg.LAST.clear()
    del api.notes[:]
    g_, e_ = ev("break", 35, 70, 5)
    g_.handle(0, Gst["ch"], stA, cb, e_)
    g_, e2 = ev("break", 35, 70, 5)
    g_.handle(0, Gst["ch"], stA, cb, e2)
    K.check(bool(e_.isCancelled()) and bool(e2.isCancelled()) and len(notes()) == 1, "X: the note is throttled (msg.gapSec), the refusal is not")
    K.check(not fire(Gst, "use", 35, 70, 5, block="Furniture_Crude_Chest") and not fire(Gst, "use", 35, 70, 5, block="Furniture_Door")
            and fire(Gst, "use", 35, 70, 5, block="Bench_Furnace") and notes() == [("Guest", "That is locked in this area.")],
            "X: FULL town - chest allowed (containers flag), door allowed, furnace locked")
    # SKYBLOCK
    K.check(not fire(Gst, "break", 5, 70, 5, block="Ore_Copper_Stone") and not fire(Gst, "dig", 5, 70, 5, block="Rock_Stone") and not notes(),
            "X: SKYBLOCK - listed stone / copper break like vanilla (not cancelled)")
    K.check(fire(Gst, "break", 5, 70, 5, block="Ore_Iron_Stone") and fire(Gst, "dig", 5, 70, 5, block="Wood_Oak_Trunk")
            and notes()[-1] == ("Guest", "You can only gather the marked resource blocks here."), "X: SKYBLOCK - unlisted blocks refused")
    K.check(fire(Gst, "use", 5, 70, 5, block="Plant_Crop_Carrot_Block") and fire(Gst, "use", 5, 70, 5, block="Soil_Grass", held="Tool_Hoe_Iron", ity=ITY.Secondary)
            and fire(Gst, "use", 5, 70, 5, block="Rock_Stone", ity=ITY.Primary) is False and not fire(Gst, "use", 5, 70, 5, block="Soil_Grass"),
            "X: SKYBLOCK - F-harvest of an unlisted crop + hoe refused, a Primary hit on listed stone ok, a plain use ok")
    K.check(fire(Gst, "place", 5, 70, 5), "X: SKYBLOCK - placing refused")
    # outside regions / other worlds
    K.check(not fire(Gst, "break", 100, 70, 100) and not fire(Gst, "place", 100, 70, 100), "X: outside every region in an unprotected world - vanilla")
    O = mkplayer(stO, "Guest2", 4, 0.5, 70.0, 0.5)
    I_ = mkplayer(stI, "Islander", 5, 0.5, 70.0, 0.5)
    K.check(not fire(O, "break", 5, 70, 5) and not fire(I_, "break", 5, 70, 5) and not fire(I_, "place", 5, 70, 5),
            "X: another world / a player island with no region - untouched")
    Cfg.WORLDS = OTHER
    K.check(fire(O, "break", 5, 70, 5) and fire(O, "use", 5, 70, 5, block="Furniture_Crude_Chest") and not fire(O, "use", 5, 70, 5, block="Furniture_Door"),
            "X: a protected world (zones.worlds) - break + chest refused everywhere, doors ok")
    Cfg.WORLDS = ""
    Cfg.ON = False
    Wand.SEL.remove(A["u"])
    K.check(not fire(Gst, "break", 35, 70, 5) and fire(A, "dig", 7, 7, 7, held="Skyy_Zones_Wand") and Wand.SEL.containsKey(A["u"]),
            "X: zone protection off - nothing refused, the wand still marks corners")
    Wand.SEL.remove(A["u"])
    said(A)
    Cfg.ON = True
    # builder mode + op bypass
    Bld.set(Bd["u"], "Builder", True)
    K.check(not fire(Bd, "break", 35, 70, 5) and not fire(Bd, "place", 5, 70, 5) and not fire(Bd, "use", 35, 70, 5, block="Bench_Furnace")
            and Cfg.bridge().get("zones:build:" + str(Bd["u"])) == Bool.TRUE, "X: builder mode - everything allowed, bridge key set")
    Bld.set(Bd["u"], "Builder", False)
    K.check(fire(Bd, "break", 35, 70, 5) and Cfg.bridge().get("zones:build:" + str(Bd["u"])) is None, "X: builder mode off - refused again, key gone")
    # fixer 2 (engine #2): the node is re-checked every 30 s while builder mode is on
    Bld.set(Bd["u"], "Builder", True)
    perms[(str(Bd["u"]), "skyyzones.build")] = False
    K.check(not fire(Bd, "break", 35, 70, 5) and bool(Bld.on(Bd["u"])), "X: a builder who lost the node keeps builder mode until the 30 s re-check")
    Bld.ON.get(Bd["u"])[2] = JLong(0)
    said(Bd)
    K.check(fire(Bd, "break", 35, 70, 5) and not bool(Bld.on(Bd["u"])) and Cfg.bridge().get("zones:build:" + str(Bd["u"])) is None
            and ("Builder", "Builder mode off - you no longer have skyyzones.build.") in notes(), "X: ... at the re-check builder mode switches off (refused, key gone, told)")
    perms[(str(Bd["u"]), "skyyzones.build")] = True
    Bld.set(Bd["u"], "Builder", True)
    Bld.ON.get(Bd["u"])[2] = JLong(0)
    K.check(not fire(Bd, "break", 35, 70, 5) and bool(Bld.on(Bd["u"])) and int(Bld.ON.get(Bd["u"])[2]) > 0, "X: a builder who still has the node passes the re-check")
    perms[(str(Bd["u"]), "skyyzones.build")] = False
    perms[(str(Bd["u"]), "skyyzones.admin")] = True
    Bld.ON.get(Bd["u"])[2] = JLong(0)
    K.check(not fire(Bd, "break", 35, 70, 5) and bool(Bld.on(Bd["u"])), "X: skyyzones.admin alone also passes the re-check")
    perms[(str(Bd["u"]), "skyyzones.build")] = True
    perms[(str(Bd["u"]), "skyyzones.admin")] = False
    Bld.set(Bd["u"], "Builder", False)
    said(Bd)
    K.check(fire(A, "break", 35, 70, 5), "X: an admin is refused while the op-bypass row is off (admins test as players)")
    Cfg.OP_BYPASS = True
    K.check(not fire(A, "break", 35, 70, 5) and fire(Gst, "break", 35, 70, 5), "X: op bypass on - the admin passes, a guest does not")
    Cfg.OP_BYPASS = False
    # mobs
    m0 = int(Guard.MOBS.get())
    K.check(fire(mob, "break", 35, 70, 5) and fire(mob, "place", 35, 70, 5) and not fire(mob, "use", 35, 70, 5, block="Bench_Furnace")
            and not fire(mob, "break", 100, 70, 100) and int(Guard.MOBS.get()) == m0 + 2, "X: a mob breaking / placing in a protected spot is refused (uses are not guarded)")
    Cfg.MOBS = False
    K.check(not fire(mob, "break", 35, 70, 5), "X: zones.blockMobs off - mobs pass")
    Cfg.MOBS = True
    # the wand
    said(A)
    K.check(fire(A, "dig", 500, 64, 500, held="Skyy_Zones_Wand") and said(A) == ["Zone Wand: corner A = 500 64 500. Now hit the opposite corner (B)."],
            "X: wand hit (outside any region) = corner A, never breaks")
    K.check(fire(A, "dig", 500, 64, 500, held="Skyy_Zones_Wand") and said(A) == [], "X: the same block again says nothing")
    K.check(fire(A, "break", 510, 70, 505, held="Skyy_Zones_Wand") and said(A) == ["Zone Wand: corner B = 510 70 505 - box 11 x 7 x 6. Next: /zones region create <name> <full or skyblock> (or /zones region addbox <name>)."],
            "X: wand second block = corner B with the box size")
    K.check(list(Wand.box(A["u"], WORLD)) == [500, 64, 500, 510, 70, 505] and Wand.box(A["u"], OTHER) is None, "X: wand box (this world only)")
    K.check(fire(A, "use", 520, 70, 505, held="Skyy_Zones_Wand", ity=ITY.Secondary) and said(A)[0].startswith("Zone Wand: corner A = 520 70 505"), "X: wand Use = the next corner")
    K.check(not fire(A, "place", 1000, 70, 1000, held="Skyy_Zones_Wand"), "X: a place event never counts as a wand click")
    K.check(not fire(A, "use", 520, 70, 505, held="Skyy_Zones_Wand", ity=ITY.Ability1), "X: other interaction types are not wand clicks")
    del api.notes[:]
    K.check(fire(Gst, "dig", 1, 1, 1, held="Skyy_Zones_Wand") and notes() == [("Guest", "Only zone admins can use the Zone Wand.")] and Wand.box(Gst["u"], WORLD) is None,
            "X: a non-admin with a wand - cancelled + note, no corner")
    Wand.SEL.remove(A["u"])
    big = Wand.hit(A["u"], WORLD, 0, 0, 0)
    big = Wand.hit(A["u"], WORLD, 0, 0, 0)
    big2 = str(Wand.hit(A["u"], WORLD, 900, 10, 0))
    K.check(big is None and "(too big:" in big2, "X: wand hit repeat = None, a too-big box says so")
    K.check(str(Wand.hit(A["u"], OTHER, 1, 2, 3)).startswith("Zone Wand: corner A = 1 2 3"), "X: a world switch starts a new box")
    Wand.SEL.remove(A["u"])
    K.check(str(Wand.hitAt(A["u"], WORLD, 3, 3, 3, JLong(1000))).startswith("Zone Wand: corner A = 3 3 3") and Wand.hitAt(A["u"], WORLD, 3, 3, 3, JLong(1300)) is None
            and Wand.hitAt(A["u"], WORLD, 3, 3, 3, JLong(1650)) is None, "X: a held click on one block (hits under 400 ms apart) says nothing")
    K.check(str(Wand.hitAt(A["u"], WORLD, 3, 3, 3, JLong(2200))).startswith("Zone Wand: corner B = 3 3 3 - box 1 x 1 x 1") and list(Wand.box(A["u"], WORLD)) == [3, 3, 3, 3, 3, 3],
            "X: the same block after a pause counts - a 1-block box is possible")
    K.check(str(Wand.hitAt(A["u"], WORLD, 3, 3, 3, JLong(3000))).startswith("Zone Wand: corner A = 3 3 3"), "X: hitting the B corner again after a pause starts the next box")
    Wand.SEL.remove(A["u"])
    # broken chunk = logged once
    bad_ch = U.allocateInstance(MCH.class_)
    bad_ch.boom = True
    f0_ = int(Guard.FAILS.get())
    canc_ = []
    for _ in range(2):
        g_, e_ = ev("break", 35, 70, 5)
        g_.handle(0, bad_ch, stA, cb, e_)
        canc_.append(bool(e_.isCancelled()))
    K.check(sum(1 for l in logged() if "guard failed (logged once; the action was REFUSED - fail closed" in l) == 1, "X: a broken guard call is logged once")
    K.check(canc_ == [True, True] and int(Guard.FAILS.get()) == f0_ + 2, "X: a guard error in a protected spot REFUSES the action (fail closed) and is counted: %s" % canc_)
    g_, e_ = ev("break", 500, 70, 500)
    g_.handle(0, bad_ch, stA, cb, e_)
    K.check(not bool(e_.isCancelled()), "X: an error outside every region (same world) refuses nothing")
    Cfg.ON = False
    g_, e_ = ev("break", 35, 70, 5)
    g_.handle(0, bad_ch, stA, cb, e_)
    K.check(not bool(e_.isCancelled()), "X: protection off - a broken chunk refuses nothing")
    Cfg.ON = True
    RD = JClass("com.hypixel.hytale.component.dependency.RootDependency")
    deps_ = [gc_.getDependencies() for gc_ in (gB, gD, gP, gU)]
    K.check(all(d_ is not None and d_.size() == 1 and isinstance(list(d_)[0], RD) for d_ in deps_), "X: every guard asks to run FIRST (RootDependency.firstSet): %s" % [str(d_) for d_ in deps_])

    # ---------------------------------------------------------------- R: 0.2.0 REGROWING BLOCKS (Z2) - the real guard / ZRegen / ZPass / ZTicker
    Dep, Rw, Pass, Rgn, Tkr, Lng = P("ZDep"), P("ZRw"), P("ZPass"), P("ZRegen"), P("ZTicker"), JClass("java.lang.Long")
    Cfg.REGEN_ON = True
    Cfg.JITTER = 0.0
    Cfg.SPEED = 1.0
    api.worlds = {WORLD: wA}
    T0 = 1800000000000
    Dep.CLOCK = JLong(T0)
    rdir = os.path.join(home, "regen")
    jfile = os.path.join(rdir, WORLD + ".journal")
    sfile = os.path.join(rdir, WORLD + ".snap")
    K.check(str(Rgn.DIR) == rdir and Rgn.WORLDS.isEmpty(), "R: the start set the regen/ folder; nothing waits yet")

    def W(x, y, z):
        return (WORLD, x, y, z)

    def drain():
        n = 0
        while api.tasks:
            api.tasks.pop(0).run()
            n += 1
        return n

    def tick(at=None):
        if at is not None:
            Dep.CLOCK = JLong(at)
        Tkr().run()
        return drain()

    def jlines():
        return open(jfile, encoding="utf8").read().splitlines() if os.path.isfile(jfile) else []

    def waiting(x, y, z, w=WORLD):
        return bool(Rgn.depleted(w, x, y, z))

    def mine(p, x, y, z, block="Ore_Copper_Stone"):
        api.wb[W(x, y, z)] = block
        c_ = fire(p, "break", x, y, z, block=block)
        if not c_:
            api.wb[W(x, y, z)] = "Empty"   # the engine removes the block after the uncancelled event (performBlockBreak)
        return c_
    def zrun(p, *words):
        Cmds.run(p["ref"], p["st"], p["pr"], wA if p["st"] is stA else (wO if p["st"] is stO else wI), JArray(JString)(list(words)))
        return said(p)
    M2 = mkplayer(stA, "Miner2", 7, 3.5, 70.0, 3.5)
    notes()
    logged()
    # ---- break -> journal FIRST -> engine removes -> the queued pass puts the placeholder
    api.state[W(5, 70, 5)] = [2, 0]
    c_ = mine(Gst, 5, 70, 5)
    jl_ = jlines()
    K.check(not c_ and waiting(5, 70, 5) and jl_ == ["D 5 70 5 Ore_Copper_Stone copper %d 2 Rock_Bedrock" % (T0 + 4000)] and len(api.tasks) == 1 and not notes(),
            "R: a listed copper break in a SKYBLOCK region is allowed (vanilla drop); its D line (id, type, regrowAt +4 s, rotation 2, placeholder) is journaled BEFORE the block changes; one pass queued: %s" % jl_)
    K.check(drain() == 1 and api.writes[-1] == (WORLD, 5, 70, 5, "Rock_Bedrock", 0) and api.wb[W(5, 70, 5)] == "Rock_Bedrock" and int(Rgn.at(WORLD, 5, 70, 5).state) == 1
            and int(Pass.PLACED.get()) == 1, "R: the queued pass (after the engine removed the block) puts the placeholder Rock_Bedrock in")
    # ---- never mined twice for one regrow
    nj_ = len(jlines())
    K.check(fire(M2, "break", 5, 70, 5, block="Rock_Bedrock") and fire(M2, "dig", 5, 70, 5, block="Rock_Bedrock") and fire(Gst, "place", 5, 70, 5)
            and fire(Gst, "use", 5, 70, 5, block="Rock_Bedrock", ity=ITY.Primary) and notes()[0] == ("Miner2", "Growing back - wait a moment.") and len(jlines()) == nj_,
            "R: the waiting spot refuses break / dig (no crack) / place / Primary hit for everyone ('Growing back') - no 2nd drop, nothing journaled")
    api.wb[W(6, 70, 5)] = "Ore_Copper_Stone"
    c1_ = fire(Gst, "break", 6, 70, 5, block="Ore_Copper_Stone")
    c2_ = fire(M2, "break", 6, 70, 5, block="Ore_Copper_Stone")   # the same tick: the engine has not removed it yet
    api.wb[W(6, 70, 5)] = "Empty"
    K.check(not c1_ and c2_ and sum(1 for l in jlines() if l.startswith("D 6 70 5 ")) == 1 and notes()[-1] == ("Miner2", "Growing back - wait a moment."),
            "R: CONTESTED - two players break one block in one tick: the first wins, the second is refused (one drop roll)")
    drain()
    # ---- the timer
    tick(T0 + 3999)
    K.check(api.wb[W(5, 70, 5)] == "Rock_Bedrock" and waiting(5, 70, 5), "R: before regrowAt nothing comes back")
    nw_ = len(api.writes)
    tick(T0 + 4000)
    K.check(api.wb[W(5, 70, 5)] == "Ore_Copper_Stone" and (WORLD, 5, 70, 5, "Ore_Copper_Stone", 2) in api.writes[nw_:] and not waiting(5, 70, 5) and not waiting(6, 70, 5)
            and "V 5 70 5 Ore_Copper_Stone copper %d 2 Rock_Bedrock" % (T0 + 4000) in jlines() and api.wb[W(6, 70, 5)] == "Ore_Copper_Stone",
            "R: at regrowAt the ORIGINAL block is back (id + rotation 2), a V line (grown back, when) journaled")
    K.check(not fire(Gst, "dig", 5, 70, 5, block="Ore_Copper_Stone") and int(Pass.RESTORED.get()) == 2, "R: ... and it can be mined again")
    # ---- a player standing in the block
    mine(Gst, 7, 70, 5, block="Rock_Stone")
    drain()
    K.check(api.wb[W(7, 70, 5)] == "Rock_Bedrock" and "D 7 70 5 Rock_Stone stone %d 0 Rock_Bedrock" % (T0 + 7000) in jlines(), "R: stone regrows after 3 s (spec Q2)")
    api.occ.add(W(7, 70, 5))
    tick(T0 + 7000)
    d7 = Rgn.at(WORLD, 7, 70, 5)
    K.check(api.wb[W(7, 70, 5)] == "Rock_Bedrock" and int(d7.tries) == 1 and int(d7.next) == T0 + 8000 and int(Pass.BLOCKED.get()) == 1,
            "R: a player standing in the block's space - nothing written, tried again in 1 s")
    d7.tries = 11
    logged()
    tick(T0 + 8000)
    K.check(int(d7.tries) == 12 and int(d7.next) == T0 + 13000 and sum(1 for l in logged() if "stood in the block" in l) == 1, "R: after 12 tries - warned once, then every 5 s")
    api.occ.clear()
    tick(T0 + 12999)
    K.check(waiting(7, 70, 5), "R: ... not before those 5 s")
    tick(T0 + 13000)
    K.check(not waiting(7, 70, 5) and api.wb[W(7, 70, 5)] == "Rock_Stone", "R: the player stepped out - it grows back")
    # ---- another system cancelled the break after us (the block is still there at the pass)
    c0_ = int(Pass.CANCELLED.get())
    api.wb[W(8, 70, 5)] = "Ore_Copper_Stone"
    fire(Gst, "break", 8, 70, 5, block="Ore_Copper_Stone")
    drain()
    K.check(not waiting(8, 70, 5) and api.wb[W(8, 70, 5)] == "Ore_Copper_Stone" and int(Pass.CANCELLED.get()) == c0_ + 1 and jlines()[-1] == "R 8 70 5",
            "R: a break another mod cancelled (the ore is still there next tick) - the entry is dropped, no placeholder")
    # ---- the spot changed by hand meanwhile
    mine(Gst, 9, 70, 5)
    drain()
    api.wb[W(9, 70, 5)] = "Furniture_Crude_Chest"
    nw_ = len(api.writes)
    tick(T0 + 17000)
    K.check(not waiting(9, 70, 5) and api.wb[W(9, 70, 5)] == "Furniture_Crude_Chest" and len(api.writes) == nw_ and int(Pass.CHANGED.get()) == 1,
            "R: a spot changed by hand while waiting is left as it is (never overwritten), the entry dropped")
    # ---- RESTART MID-TIMER
    Dep.CLOCK = JLong(T0 + 20000)
    for x_ in (10, 11):
        mine(Gst, x_, 70, 5)
    drain()
    Rgn.snapshotAll(True)
    K.check(not os.path.exists(jfile) and open(sfile, encoding="utf8").read().count("\nD ") == 2, "R: the snapshot (temp file + rename) holds both waiting blocks, the journal is emptied")
    mine(Gst, 12, 70, 5)
    drain()
    Rgn.at(WORLD, 10, 70, 5).due = JLong(T0 + 20000)
    tick(T0 + 20000)
    K.check(not waiting(10, 70, 5) and jlines()[0].startswith("D 12 70 5 ") and any(l.startswith("V 10 70 5 ") for l in jlines()), "R: after the snapshot: a new block + a regrown one only in the journal")
    open(jfile, "a", encoding="utf8").write("D 1 2\n")   # a torn last line (crash in the middle of a write)
    before_ = dict(((int(d.x), int(d.y), int(d.z)), (str(d.orig), int(d.due), int(d.rot), str(d.type), str(d.ph))) for d in Rgn.rw(WORLD, False).dep.values())
    r_ = str(Rgn.start(Paths.get(rdir)))
    after_ = dict(((int(d.x), int(d.y), int(d.z)), (str(d.orig), int(d.due), int(d.rot), str(d.type), str(d.ph))) for d in Rgn.rw(WORLD, False).dep.values())
    K.check(after_ == before_ and sorted(after_) == [(11, 70, 5), (12, 70, 5)] and r_ == "2 blocks waiting to grow back in 1 world (1 unreadable lines skipped)"
            and all(int(d.state) == 1 for d in Rgn.rw(WORLD, False).dep.values()),
            "R: RESTART MID-TIMER - snapshot + journal replayed: the same 2 waiting blocks with the same times; the torn line skipped: %s" % r_)
    K.check(not os.path.exists(jfile) and open(sfile, encoding="utf8").read().count("\nD ") == 2, "R: ... compacted into a fresh snapshot at the start")
    K.check(fire(Gst, "break", 11, 70, 5, block="Rock_Bedrock") and api.wb[W(11, 70, 5)] == "Rock_Bedrock", "R: ... the spot is still protected after the restart")
    tick(T0 + 23999)
    K.check(waiting(11, 70, 5), "R: ... not back before its old time")
    tick(T0 + 24000)
    K.check(not waiting(11, 70, 5) and not waiting(12, 70, 5) and api.wb[W(11, 70, 5)] == "Ore_Copper_Stone", "R: ... and grows back at its old time")
    # regen.offlineCounts off: the downtime is added
    Dep.CLOCK = JLong(T0 + 30000)
    mine(Gst, 13, 70, 5)
    drain()
    Rgn.snapshotAll(True)
    os.utime(sfile, ((T0 + 30000) / 1000.0, (T0 + 30000) / 1000.0))
    Dep.CLOCK = JLong(T0 + 130000)
    Cfg.OFFLINE = False
    Rgn.start(Paths.get(rdir))
    Cfg.OFFLINE = True
    K.check(int(Rgn.at(WORLD, 13, 70, 5).due) == T0 + 34000 + 100000, "R: regen.offlineCounts off - the 100 s the server was off are added to the timer: %d" % (int(Rgn.at(WORLD, 13, 70, 5).due) - T0))
    # fixer: the downtime is measured from regen/alive (the 60 s heartbeat), not from the last mined block (a crash after an idle hour)
    d13_ = int(Rgn.at(WORLD, 13, 70, 5).due)
    alivef = os.path.join(rdir, "alive")
    Dep.CLOCK = JLong(T0 + 140000)
    Rgn.beat()
    K.check(open(alivef, encoding="utf8").read() == str(T0 + 140000) and int(Rgn.lastBeat()) == T0 + 140000, "R: (fixer) the heartbeat regen/alive holds the time (written while blocks wait)")
    os.utime(sfile, ((T0 + 130000) / 1000.0, (T0 + 130000) / 1000.0))
    Dep.CLOCK = JLong(T0 + 150000)
    Cfg.OFFLINE = False
    Rgn.start(Paths.get(rdir))
    Cfg.OFFLINE = True
    K.check(int(Rgn.at(WORLD, 13, 70, 5).due) == d13_ + 10000,
            "R: (fixer) regen.offlineCounts off - the downtime counts from the last heartbeat (10 s), not the snapshot time (20 s): %d" % (int(Rgn.at(WORLD, 13, 70, 5).due) - d13_))
    Rgn.at(WORLD, 13, 70, 5).due = JLong(d13_)
    os.remove(alivef)
    # fixer: a torn last line (no newline) is skipped, never half-parsed, warned with its text + the file kept; a bad byte only skips its line
    Rgn.rw(WORLD, False).close()
    with open(jfile, "ab") as f_:
        f_.write(b"D 42 70 5 Ore_Copper_St\xff\xfe copper 1 0 Rock_Bedrock\nD 41 70 5 Ore_Copper_Stone copper 1 0 Rock_Bedr")
    logged()
    rt_ = str(Rgn.start(Paths.get(rdir)))
    lt_ = logged()
    torn_ = [f for f in os.listdir(rdir) if f.startswith(WORLD + ".journal.torn-")]
    K.check(not waiting(41, 70, 5) and not waiting(42, 70, 5) and waiting(13, 70, 5) and "(2 unreadable lines skipped)" in rt_ and len(torn_) == 1
            and any("was cut off" in l and "Rock_Bedr'" in l for l in lt_) and not bool(Rgn.rw(WORLD, False).hold),
            "R: (fixer) a torn last journal line is skipped (not parsed as a 'Rock_Bedr' placeholder), warned, the file kept as %s; a bad byte skips only its line: %s" % (torn_, rt_))
    for f_ in torn_:
        os.remove(os.path.join(rdir, f_))
    bad_ = [f for f in os.listdir(rdir) if ".journal.bad-" in f]
    K.check(len(bad_) >= 1 and any("unreadable lines in " + WORLD + ".journal skipped - the file is kept as " in l for l in lt_),
            "R: (fixer 2) a journal with a bad MIDDLE line is kept as <file>.bad-<ms> before the start compacts it (the evidence stays): %s" % bad_)
    for f_ in bad_:
        os.remove(os.path.join(rdir, f_))
    # fixer: an UNREADABLE file holds that world's files - no snapshot rewrites or deletes them (else its waiting blocks were lost for good)
    hw = "heldw"
    hsnap, hjour = os.path.join(rdir, hw + ".snap"), os.path.join(rdir, hw + ".journal")
    os.makedirs(hsnap)
    open(hjour, "w", encoding="utf8").write("D 1 70 1 Rock_Stone stone %d 0 Rock_Bedrock\n" % (T0 + 999000))
    logged()
    Rgn.start(Paths.get(rdir))
    rh_ = Rgn.rw(hw, False)
    K.check(rh_ is not None and bool(rh_.hold) and int(rh_.dep.size()) == 1 and any("could not read" in l for l in logged()),
            "R: (fixer) an unreadable regen/ file - its world is HELD (the readable journal entry still waits)")
    K.check(bool(rh_.append("D 2 70 1 Rock_Stone stone %d 0 Rock_Bedrock" % (T0 + 999000))) and not bool(rh_.snapshot(False)) and not bool(rh_.snapshot(True))
            and os.path.isdir(hsnap) and open(hjour, encoding="utf8").read().count("D ") == 2 and any("NOT rewritten" in l for l in logged()),
            "R: (fixer) a held world: new breaks still journal, but the periodic / forced snapshot neither rewrites nor deletes its files")
    K.check(any("ITS REGROW FILES COULD NOT BE READ" in str(l) for l in Rgn.status()), "R: (fixer) /zones status names the held world")
    rh_.close()
    os.rmdir(hsnap)
    os.remove(hjour)
    Rgn.start(Paths.get(rdir))
    K.check(Rgn.rw(hw, False) is None and waiting(13, 70, 5), "R: (the held files fixed - a start reads them normally)")
    # ---- an UNLOADED chunk: catch-up when it is loaded again
    Sto.create("far", WORLD, "skyblock", JArray(JInt)([600, 60, 600, 620, 80, 620]), who)
    Sto.set("far", "types", "stone", who)
    Dep.CLOCK = JLong(T0 + 140000)
    mine(Gst, 610, 70, 610, block="Rock_Stone")
    drain()
    api.unloaded.add((WORLD, 610 >> 5, 610 >> 5))
    nu_ = int(Pass.UNLOADED.get())
    tick(T0 + 150000)
    K.check(waiting(610, 70, 610) and not api.loads and int(Pass.UNLOADED.get()) > nu_ and not waiting(13, 70, 5),
            "R: due in an UNLOADED chunk - nothing written and nothing loaded (the chunk saved the placeholder); a loaded one comes back meanwhile")
    api.unloaded.clear()
    tick()
    K.check(not waiting(610, 70, 610) and api.wb[W(610, 70, 610)] == "Rock_Stone", "R: CATCH-UP - the first pass after the chunk is loaded again puts it back")
    # ---- /zones restore all (forced: early, unloaded chunks asked for, worlds not loaded reported) + status
    Dep.CLOCK = JLong(T0 + 200000)
    mine(Gst, 14, 70, 5)
    mine(Gst, 15, 70, 5)
    mine(Gst, 611, 70, 610, block="Rock_Stone")
    drain()
    api.unloaded.add((WORLD, 611 >> 5, 610 >> 5))
    od_ = Dep(1, 70, 3, "Rock_Stone", "stone", "Rock_Bedrock", 0, JLong(T0 + 999999))
    Rgn.rw(OTHER, True).dep.put(Lng.valueOf(JLong(Dep.key(1, 70, 3))), od_)
    st_ = zrun(Gst, "status")
    K.check(st_[0].startswith("Regrowing blocks: ON - 4 waiting; since the start ") and " %s: 1 waiting (stone 1); next back in 800 s" % OTHER in st_
            and " %s: 3 waiting (copper 2, stone 1); next back in 3 s" % WORLD in st_, "R: /zones status (builders): waiting per world + type, next due: %s" % st_)
    ra_ = zrun(A, "restore", "all")
    K.check(ra_ == ["Putting back 4 waiting blocks now (loaded chunks at once, the others are loaded first). /zones status shows what is left.",
                    "1 of them are in 1 world that are not loaded - they come back when the world loads."], "R: /zones restore all - the answer: %s" % ra_)
    drain()
    K.check(not waiting(14, 70, 5) and not waiting(15, 70, 5) and api.wb[W(14, 70, 5)] == "Ore_Copper_Stone" and waiting(611, 70, 610) and len(api.loads) == 1
            and api.loads[0][0] == (WORLD, 611 >> 5, 610 >> 5), "R: restore all - the loaded ones are back at once (before their time), the unloaded chunk is ASKED for")
    st2_ = zrun(A, "status")
    K.check(any("being put back now" in l for l in st2_), "R: status shows the forced ones: %s" % st2_)
    key_, after_r = api.loads.pop()
    api.unloaded.clear()
    after_r.run()
    K.check(len(api.tasks) == 1 and waiting(611, 70, 610), "R: (fixer) the chunk-load callback only QUEUES one merged pass - never a full pass per loaded chunk")
    drain()
    K.check(not waiting(611, 70, 610) and api.wb[W(611, 70, 610)] == "Rock_Stone", "R: ... and put back as soon as the chunk arrives (the pass runs on the world)")
    Rgn.WORLDS.remove(OTHER)
    K.check(zrun(A, "restore", "nope") == ["No region nope (/zones list) - or /zones restore all."] and zrun(A, "restore", "mine") == ["Nothing is waiting to grow back in mine."]
            and zrun(A, "restore", "all") == ["Nothing is waiting to grow back."], "R: restore refusals / nothing waiting")
    mine(Gst, 16, 70, 5)
    drain()
    K.check(zrun(A, "restore", "far") == ["Nothing is waiting to grow back in far."] and waiting(16, 70, 5), "R: restore <region> only touches that region")
    zrun(A, "restore", "mine")
    drain()
    K.check(not waiting(16, 70, 5), "R: restore <region>")
    # fixer: a forced catch-up asks each unloaded chunk ONCE, at most 8 new loads a pass; never answered -> asked again after 30 s
    Dep.CLOCK = JLong(T0 + 205000)
    Sto.create("wide", WORLD, "skyblock", JArray(JInt)([1000, 60, 1000, 1400, 80, 1010]), who)
    Sto.set("wide", "types", "stone", who)
    wx_ = [1000 + 32 * i for i in range(12)] + [1001, 1002, 1003]
    for x_ in wx_:
        mine(Gst, x_, 70, 1005, block="Rock_Stone")
    drain()
    for x_ in wx_:
        api.unloaded.add((WORLD, x_ >> 5, 1005 >> 5))
    del api.loads[:]
    zrun(A, "restore", "wide")
    drain()
    ch1_ = [k for k, _ in api.loads]
    K.check(len(ch1_) == 8 and len(set(ch1_)) == 8 and int(Pass.ASKED.get()) >= 8 and all(waiting(x_, 70, 1005) for x_ in wx_),
            "R: (fixer) restore with 15 blocks in 12 unloaded chunks - 8 chunk loads in the first pass, one per chunk (3 blocks share one): %s" % ch1_)
    tick()
    ch2_ = [k for k, _ in api.loads]
    K.check(len(ch2_) == 12 and len(set(ch2_)) == 12, "R: (fixer) the next pass asks the 4 chunks left - none twice: %d" % len(ch2_))
    tick(T0 + 205000 + 29999)
    K.check(len(api.loads) == 12, "R: (fixer) a chunk that has not come yet is not asked again before 30 s")
    tick(T0 + 205000 + 30000)
    K.check(len(api.loads) == 20, "R: (fixer) ... after 30 s it is asked again (a failed / lost load is never stuck), still at most 8 a pass: %d" % len(api.loads))
    api.unloaded.clear()
    cbs_ = [cb_ for _, cb_ in api.loads]
    del api.loads[:]
    for cb_ in cbs_:
        cb_.run()
    K.check(len(api.tasks) == 1, "R: (fixer) 20 load callbacks queue ONE merged pass (no N x N work on the world thread)")
    drain()
    K.check(not any(waiting(x_, 70, 1005) for x_ in wx_) and api.wb[W(1001, 70, 1005)] == "Rock_Stone", "R: (fixer) ... and every block is back once the chunks are there")
    Sto.delete("wide", who)
    # ---- regen.enabled off: everything back at once, listed blocks break like 0.1.0
    mine(Gst, 16, 70, 5)
    drain()
    Cfg.REGEN_ON = False
    api.wb[W(17, 70, 5)] = "Ore_Copper_Stone"
    K.check(not fire(Gst, "break", 17, 70, 5, block="Ore_Copper_Stone") and not waiting(17, 70, 5), "R: regen.enabled off - a listed block breaks like 0.1.0 (no regrow)")
    tick()
    K.check(not waiting(16, 70, 5) and api.wb[W(16, 70, 5)] == "Ore_Copper_Stone" and zrun(Gst, "status")[0].startswith("Regrowing blocks: OFF"),
            "R: regen.enabled off - every waiting block comes back at once")
    Cfg.REGEN_ON = True
    # ---- the journal line cannot be written -> the break is REFUSED
    Rgn.rw(WORLD, True).close()
    if os.path.exists(jfile):
        os.remove(jfile)
    os.makedirs(jfile)
    j0_ = int(Rw.JFAIL.get())
    notes()
    api.wb[W(18, 70, 5)] = "Ore_Copper_Stone"
    K.check(fire(Gst, "break", 18, 70, 5, block="Ore_Copper_Stone") and not waiting(18, 70, 5) and int(Rw.JFAIL.get()) == j0_ + 1
            and notes()[-1][1].startswith("You can't gather here right now") and any("JOURNAL WRITE ERRORS: " in l for l in zrun(A, "status")),
            "R: the journal line cannot be written - the break is REFUSED (no drop, nothing changes), status says so")
    os.rmdir(jfile)
    # ---- no regrow: logs (0 s), a multi-block part; builder mode; mobs
    Sto.create("forest", WORLD, "skyblock", JArray(JInt)([700, 60, 700, 720, 80, 720]), who)
    Sto.set("forest", "types", "logs", who)
    api.wb[W(710, 70, 710)] = "Wood_Oak_Trunk"
    K.check(not fire(Gst, "break", 710, 70, 710, block="Wood_Oak_Trunk") and not waiting(710, 70, 710), "R: logs (regrow 0 until Z3 whole trees) break like vanilla - no placeholder")
    api.wb[W(19, 70, 5)] = "Ore_Copper_Stone"
    api.state[W(19, 70, 5)] = [0, 3]
    logged()
    K.check(not fire(Gst, "break", 19, 70, 5, block="Ore_Copper_Stone") and not waiting(19, 70, 5) and any("part of a bigger block" in l for l in logged()),
            "R: a multi-block part (filler) breaks like vanilla, warned once")
    Dep.CLOCK = JLong(T0 + 210000)
    Bld.set(Bd["u"], "Builder", True)
    api.wb[W(20, 70, 5)] = "Ore_Copper_Stone"
    K.check(not fire(Bd, "break", 20, 70, 5, block="Ore_Copper_Stone") and not waiting(20, 70, 5), "R: builder mode - breaks start no regrow (spec 3.1)")
    mine(Gst, 18, 70, 6)
    drain()
    K.check(not fire(Bd, "break", 18, 70, 6, block="Rock_Bedrock"), "R: builder mode passes a waiting spot too")
    Bld.set(Bd["u"], "Builder", False)
    Dep.CLOCK = JLong(T0 + 211000)
    api.wb[W(17, 70, 6)] = "Ore_Copper_Stone"
    cm_ = fire(mob, "break", 17, 70, 6, block="Ore_Copper_Stone")
    api.wb[W(17, 70, 6)] = "Empty"
    drain()
    K.check(not cm_ and waiting(17, 70, 6) and api.wb[W(17, 70, 6)] == "Rock_Bedrock" and fire(mob, "break", 18, 70, 6, block="Rock_Bedrock"),
            "R: a mob breaking a listed block starts a regrow too; a mob at a waiting spot is refused")
    # ---- regen.maxDepleted: the one due first comes back early
    rwW = Rgn.rw(WORLD, False)
    n_ = int(rwW.dep.size())
    first_ = min(rwW.dep.values(), key=lambda d: int(d.due))
    Cfg.MAXDEP = n_
    Dep.CLOCK = JLong(T0 + 212000)
    mine(Gst, 16, 70, 6)
    Cfg.MAXDEP = 20000
    K.check(int(first_.due) == 0 and int(first_.x) == 18 and int(rwW.dep.size()) == n_ + 1 and bool(first_.force),
            "R: regen.maxDepleted reached - the waiting block due first (18 70 6) comes back early (FORCED: an unloaded one is loaded too)")
    drain()
    K.check(not waiting(18, 70, 6) and api.wb[W(18, 70, 6)] == "Ore_Copper_Stone", "R: ... put back at the next pass")
    # ---- /zones info + the bridge
    api.tgt = [17, 70, 6]
    inf_ = zrun(A, "info")
    api.tgt = None
    K.check(any(l.startswith("Mined: grows back as Ore_Copper_Stone in ") and l.endswith(" s (type copper).") for l in inf_), "R: /zones info shows the waiting block: %s" % inf_)
    Fn.publish()
    chk_ = Cfg.bridge().get("zones:fn:check")
    K.check(str(chk_.apply(JArray(JObject)([WORLD, JInt(17), JInt(70), JInt(6), "break", "Rock_Bedrock"]))) == "deny"
            and str(chk_.apply(JArray(JObject)([WORLD, JInt(17), JInt(70), JInt(6), "place", "Rock_Stone"]))) == "deny"
            and str(chk_.apply(JArray(JObject)([WORLD, JInt(5), JInt(70), JInt(5), "break", "Ore_Copper_Stone"]))) == "allow", "R: zones:fn:check - a waiting spot is deny")
    Fn.unpublish()
    # ---- /zones audit (+ fix): placeholders with no waiting entry (a lost write); a waiting one is left alone
    api.wb[W(3, 61, 3)] = "Rock_Bedrock"
    au_ = zrun(A, "audit", "mine")
    K.check(au_[0].startswith("Audit of mine: 9261 blocks read; ") and au_[0].endswith(" placeholder blocks, 1 with no timer.") and au_[1] == " e.g. at [3 61 3]"
            and "audit mine fix turns them" in au_[2], "R: /zones audit lists the lost placeholder: %s" % au_)
    au2_ = zrun(A, "audit", "mine", "fix")
    K.check(api.wb[W(3, 61, 3)] == "Rock_Stone" and au2_[-1] == " Put back: 1." and api.wb[W(17, 70, 6)] == "Rock_Bedrock" and waiting(17, 70, 6),
            "R: audit fix - the lost one back to stone's first block id (Rock_Stone); a WAITING placeholder is left alone: %s" % au2_)
    K.check(zrun(A, "audit", "town") == ["Region town has no regrowing resource types - nothing to audit."] and zrun(A, "audit", "nope") == ["No region nope in this world (/zones list)."],
            "R: audit - a FULL region / an unknown region")
    K.check(str(Rgn.plain("iron")) == "Ore_Iron_Stone" and str(Rgn.plain("copper")) == "Ore_Copper_Stone" and str(Rgn.plain("gem")) == "Rock_Gem_Diamond"
            and str(Rgn.plain("stone")) == "Rock_Stone" and Rgn.plain("onyxium") is None, "R: (fixer) audit fix ids - a wildcard type uses its vanilla block (build-time table)")
    Sto.create("cu", WORLD, "skyblock", JArray(JInt)([50, 60, 50, 60, 80, 60]), who)
    Sto.set("cu", "types", "copper", who)
    Sto.create("cs", WORLD, "skyblock", JArray(JInt)([70, 60, 70, 80, 80, 80]), who)
    Sto.set("cs", "types", "copper,stone", who)
    api.wb[W(55, 61, 55)] = "Rock_Bedrock"
    api.wb[W(75, 61, 75)] = "Rock_Bedrock"
    au3_ = zrun(A, "audit", "cu", "fix")
    au4_ = zrun(A, "audit", "cs", "fix")
    K.check(api.wb[W(55, 61, 55)] == "Ore_Copper_Stone" and au3_[-1] == " Put back: 1." and api.wb[W(75, 61, 75)] == "Rock_Stone" and au4_[-1] == " Put back: 1.",
            "R: (fixer) audit fix puts a lost ORE back (copper -> Ore_Copper_Stone); with copper + stone sharing bedrock it prefers stone: %s %s" % (au3_, au4_))
    Sto.delete("cu", who)
    Sto.delete("cs", who)
    api.wb[W(3, 62, 3)] = "Rock_Stone_Cobble"
    K.check(not fire(Gst, "break", 3, 62, 3, block="Rock_Stone_Cobble") and waiting(3, 62, 3), "R: (fixer) cobble in a stone mine is mined + regrows")
    api.wb[W(3, 62, 3)] = "Empty"
    drain()
    # ---- the 60 s snapshot tick + the scheduler
    mine(Gst, 19, 70, 6)
    drain()
    K.check(any(l.startswith("D 19 70 6 ") for l in jlines()), "R: (a fresh journal line)")
    Tkr.N = JLong(59)
    Tkr().run()
    drain()
    K.check(not os.path.exists(jfile) and "D 19 70 6 " in open(sfile, encoding="utf8").read(), "R: every 60th tick writes the snapshot and empties the journal")
    Tkr().run()
    drain()
    ok_ = False
    try:
        Tkr.start()
        ok_ = Tkr.FUT is not None
    finally:
        Tkr.stop()
    K.check(ok_ and Tkr.FUT is None, "R: the 1 s regrow timer starts on the server scheduler and stops")
    # ---- fixer: a region deleted (any change of the region index) puts its waiting blocks back at once (spec 9); notes for no-regrow types
    Dep.CLOCK = JLong(T0 + 300000)
    mine(Gst, 605, 70, 605, block="Rock_Stone")
    drain()
    K.check(waiting(605, 70, 605) and api.wb[W(605, 70, 605)] == "Rock_Bedrock", "R: (a block waits in region far)")
    Sto.delete("far", who)
    tick()
    K.check(not waiting(605, 70, 605) and api.wb[W(605, 70, 605)] == "Rock_Stone",
            "R: (fixer) region far DELETED - its waiting block is back at the next pass, before its time (nothing stays bedrock)")
    nt_ = zrun(A, "region", "types", "forest", "logs,stone")
    K.check(any(l.startswith("Note: logs (does NOT grow back yet") for l in nt_) and not any(l.startswith("Note: stone") for l in nt_),
            "R: (fixer) /zones region types warns that logs do not grow back yet (Z3): %s" % nt_)
    Rgn.restore(None)
    drain()
    # ---- fixer: a placeholder that is itself a listed block is replaced by Rock_Bedrock at run time (never mined twice for one regrow)
    pp2_ = Props()
    pp2_.setProperty("regrow.stone", "3,Ore_Copper_Stone")
    Cfg.REGROW = Cfg.parseRegrow(pp2_)
    logged()
    mine(Gst, 2, 62, 2, block="Rock_Stone")
    drain()
    K.check(api.wb[W(2, 62, 2)] == "Rock_Bedrock" and str(Rgn.at(WORLD, 2, 62, 2).ph) == "Rock_Bedrock" and any("is itself a block of type copper" in l for l in logged()),
            "R: (fixer) a hand-edited placeholder that is a listed block (Ore_Copper_Stone) - Rock_Bedrock is used instead, warned")
    Cfg.loadRegen(False)
    # ---- fixer 2: a regrow pass is never re-queued into the same world tick (World.consumeTaskQueue drains until EMPTY - read from the jar);
    # the harness drain() is that same loop, so a backlog that ran in one drain would show here
    Rgn.restore(None)
    drain()
    Dep.CLOCK = JLong(T0 + 400000)
    Cfg.JITTER = 0.0
    Cfg.PASS = 2
    del api.lat[:]
    for x_ in range(1, 6):
        mine(Gst, x_, 75, 15, block="Rock_Stone")
    nd_ = drain()
    K.check(nd_ == 1 and sum(1 for x_ in range(1, 6) if api.wb[W(x_, 75, 15)] == "Rock_Bedrock") == 2 and len(api.lat) == 1 and api.lat[0][1] == 50,
            "R: (fixer 2) regen.passBatch 2 with 5 fresh breaks - ONE pass in the drain-until-empty loop writes 2, the rest waits for a pass 50 ms later: %d %s" % (nd_, api.lat))
    r_, _ = api.lat.pop(0)
    r_.run()
    K.check(drain() == 1 and sum(1 for x_ in range(1, 6) if api.wb[W(x_, 75, 15)] == "Rock_Bedrock") == 4 and len(api.lat) == 1,
            "R: (fixer 2) ... the delayed pass (from the scheduler) queues one world pass, 2 more")
    r_, _ = api.lat.pop(0)
    r_.run()
    drain()
    K.check(all(api.wb[W(x_, 75, 15)] == "Rock_Bedrock" for x_ in range(1, 6)) and not api.lat, "R: (fixer 2) ... and the last one, nothing more delayed")
    Cfg.PASS = 200
    # ---- fixer 2: a queued pass that never ran (its world stopped) blocks that world's kicks for at most 5 s
    rwq_ = Rgn.rw(WORLD, False)
    wq_ = api.worlds.get(WORLD)
    rwq_.queued.set(JLong(T0 + 400000))
    nt_ = len(api.tasks)
    k1_ = bool(Pass.kick(wq_, rwq_))
    Dep.CLOCK = JLong(T0 + 404999)
    k2_ = bool(Pass.kick(wq_, rwq_))
    Dep.CLOCK = JLong(T0 + 405000)
    k3_ = bool(Pass.kick(wq_, rwq_))
    K.check(not k1_ and not k2_ and k3_ and len(api.tasks) == nt_ + 1 and int(rwq_.queued.get()) == T0 + 405000,
            "R: (fixer 2) a pass queued but never run - kicks are merged for 5 s, then a new pass is queued (no world stuck until restart)")
    drain()
    K.check(int(rwq_.queued.get()) == 0, "R: (fixer 2) ... running clears it")
    # ---- fixer 2: a waiting spot is refused while zones.on is OFF too (the placeholder is never mined; builder mode still passes)
    for x_ in (1, 2, 3):
        mine(Gst, x_, 75, 15, block="Rock_Stone")
    drain()
    Cfg.ON = False
    Fn.publish()
    chk2_ = Cfg.bridge().get("zones:fn:check")
    notes()
    api.wb[W(6, 75, 15)] = "Ore_Copper_Stone"
    K.check(fire(Gst, "break", 1, 75, 15, block="Rock_Bedrock") and notes()[-1][1] == "Growing back - wait a moment." and waiting(1, 75, 15)
            and not fire(Gst, "break", 6, 75, 15, block="Ore_Copper_Stone") and not waiting(6, 75, 15)
            and str(chk2_.apply(JArray(JObject)([WORLD, JInt(1), JInt(75), JInt(15), "break", "Rock_Bedrock"]))) == "deny"
            and str(chk2_.apply(JArray(JObject)([WORLD, JInt(6), JInt(75), JInt(15), "break", "Rock_Stone"]))) == "allow",
            "R: (fixer 2) zones.on OFF - a waiting spot is still refused (guard + bridge deny); every other block is free (no protection, no regrow)")
    K.check(fire(mob, "break", 2, 75, 15, block="Rock_Bedrock") and waiting(2, 75, 15), "R: (fixer 2) ... a mob too")
    Bld.set(Bd["u"], "Builder", True)
    K.check(not fire(Bd, "break", 3, 75, 15, block="Rock_Bedrock"), "R: (fixer 2) ... builder mode still passes")
    Bld.set(Bd["u"], "Builder", False)
    Fn.unpublish()
    Cfg.ON = True
    Rgn.restore(None)
    drain()
    # ---- fixer 2: a CRASH after a block grew back but before its chunk was saved (the saved chunk reloads the placeholder, no D entry)
    Dep.CLOCK = JLong(T0 + 410000)
    mine(Gst, 7, 75, 15)
    mine(Gst, 8, 75, 15)
    drain()
    tick(T0 + 414000)
    jv_ = jlines()
    K.check(api.wb[W(7, 75, 15)] == "Ore_Copper_Stone" and "V 7 75 15 Ore_Copper_Stone copper %d 0 Rock_Bedrock" % (T0 + 414000) in jv_
            and int(Rgn.rw(WORLD, False).recent.size()) >= 2, "R: (fixer 2) grown back -> a V line (when) + kept as recent")
    Rgn.snapshotAll(True)
    sv_ = open(sfile, encoding="utf8").read()
    K.check("V 7 75 15 " in sv_ and "V 8 75 15 " in sv_, "R: (fixer 2) the snapshot keeps the recent V lines (30 min)")
    api.wb[W(7, 75, 15)] = "Rock_Bedrock"   # the crash: the chunk was last saved while 21 was the placeholder
    api.unloaded.add((WORLD, 7 >> 5, 15 >> 5))
    Rgn.rw(WORLD, False).close()
    Dep.CLOCK = JLong(T0 + 500000)
    logged()
    r2_ = str(Rgn.start(Paths.get(rdir)))
    rwc_ = Rgn.rw(WORLD, False)
    K.check(rwc_ is not None and int(rwc_.check.size()) >= 2 and not waiting(7, 75, 15) and any("grew back just before the last stop" in str(l) for l in Rgn.status()),
            "R: (fixer 2) after the restart the recent spots are CHECKED (not waiting - nothing refused for them), status says so: %s" % r2_)
    nw_ = len(api.writes)
    tick()
    K.check(api.wb[W(7, 75, 15)] == "Rock_Bedrock" and len(api.writes) == nw_ and int(rwc_.check.size()) >= 2, "R: (fixer 2) ... not while the chunk is unloaded")
    api.unloaded.clear()
    mine(Gst, 8, 75, 15)   # 22 is mined again before the check ran: the new D entry wins, the check entry is dropped
    tick()
    K.check(api.wb[W(7, 75, 15)] == "Ore_Copper_Stone" and int(Pass.VERIFIED.get()) == 1 and waiting(8, 75, 15) and not rwc_.check.containsKey(Lng.valueOf(JLong(Dep.key(8, 75, 15))))
            and any("still held the placeholder" in l for l in logged()) and "V 7 75 15 Ore_Copper_Stone copper %d 0 Rock_Bedrock" % (T0 + 500000) in jlines()
            and api.wb[W(5, 70, 5)] == "Ore_Copper_Stone" and int(rwc_.check.size()) == 0,
            "R: (fixer 2) ... chunk loaded: the spot still holding the placeholder gets its ORIGINAL back (logged, V again); spots holding the original are dropped; a re-mined one is left to its new timer")
    K.check(any("placeholders left by an unclean stop put back" in str(l) for l in Rgn.status()), "R: (fixer 2) /zones status counts them")
    Rgn.restore(None)
    drain()
    Dep.CLOCK = JLong(T0 + 500000 + 1800001)
    rwc_.append("R 0 0 0")
    Rgn.snapshotAll(False)
    K.check(int(rwc_.recent.size()) == 0 and not os.path.exists(sfile) and not os.path.exists(jfile),
            "R: (fixer 2) recent spots are forgotten after 30 min; nothing waiting / recent / to check = both files removed")
    K.check(int(Rgn.AUDIT_CAP) == 500000, "R: (fixer 2) /zones audit reads at most 500,000 blocks a run (world-thread stall cap)")
    # ---- clean up for the later phases: everything back, the extra regions gone
    Rgn.restore(None)
    drain()
    K.check(Rgn.rw(WORLD, False).dep.isEmpty() and int(Rgn.BROKE.get()) > 10, "R: (all back)")
    Sto.delete("far", who)
    Sto.delete("forest", who)
    said(A)
    said(Gst)
    notes()
    Dep.CLOCK = JLong(0)

    # ---------------------------------------------------------------- K: the kit (Server Setup)
    mods = os.path.dirname(home)
    CPub.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones"))
    hdr = Cfg.bridge().get("config:def:SkyyZones")
    rows = dict((str(rw[0]), [str(x) for x in rw]) for rw in hdr[7]) if hdr is not None else {}
    K.check(hdr is not None and str(hdr[1]) == "SkyyZones" and str(hdr[2]) == "Zones" and str(hdr[3]) == VERSION and str(hdr[4]) == "skyyzones.admin"
            and sorted(rows) == sorted(["zones.on", "zones.worlds", "zones.opBypass", "zones.blockMobs", "msg.gapSec", "use.tools", "titles.on", "titles.leave",
                                        "titles.gapSec", "show.seconds", "show.particle", "build.remindSec", "reload.files", "region", "type",
                                        "regen.enabled", "regen.speedMult", "regen.jitter", "regen.offlineCounts", "regen.defaultSec", "regen.passBatch",
                                        "regen.maxDepleted", "regrow", "regen.restoreAll"]),
            "K: config:def:SkyyZones - the 24 rows: %s" % sorted(rows))
    K.check("ro" not in rows.get("region", [""] * 10)[9].split(",") and rows.get("region", [""] * 7)[6] == "200" and rows.get("type", [""] * 7)[6] == "200",
            "K: the regions table is editable (PROJECT-RULES 4); both cells max 200 (SkyyMenu 0.3)")
    K.check("part" in rows.get("zones.on", [""] * 10)[9] and rows.get("zones.opBypass", [""] * 5)[4] == "false", "K: zones.on is a part switch, admins bypass defaults off")
    m_ = str(CFn.cmdSetConsole("titles.gapSec", "25"))
    CPub.flush()
    K.check(int(Cfg.TITLE_GAP) == 25 and "titles.gapSec=25" in open(cfgf, encoding="utf8").read(), "K: a field row (console) sets the field + the file line: %s" % m_)
    CFn.cmdSetConsole("titles.gapSec", "10")
    # 0.2.0 the regrowing rows (regen.properties)
    regf = os.path.join(home, "regen.properties")

    def wait_for(cond):
        CPub.flush()
        for _ in range(50):
            if cond():
                return True
            time.sleep(0.1)
        return False
    m2_ = str(CFn.cmdSetConsole("regen.speedMult", "0.5"))
    CPub.flush()
    K.check(float(Cfg.SPEED) == 0.5 and "regen.speedMult=0.5" in open(regf, encoding="utf8").read(), "K: regen.speedMult (a dec field row) sets the field + the regen.properties line: %s" % m2_)
    CFn.cmdSetConsole("regen.speedMult", "1")
    m3_ = str(CFn.cmdSetConsole("regen.enabled", "false"))
    K.check(not bool(Cfg.REGEN_ON), "K: regen.enabled off (console): %s" % m3_)
    CFn.cmdSetConsole("regen.enabled", "true")
    K.check(bool(Cfg.REGEN_ON), "K: regen.enabled on again")
    tr_ = CFn().apply(JArray(JObject)(["tset", "regrow", "copper", "7|Rock_Bedrock", A["u"], "Skyy", "yes", "menu"]))
    K.check(tr_ is not None and str(tr_[0]) == "ok" and wait_for(lambda: int(Cfg.regrowSec("copper")) == 7) and "regrow.copper=7,Rock_Bedrock\n" in open(regf, encoding="utf8").read(),
            "K: the regrow table (copper 7 s) -> regen.properties -> reloadRegen: %s" % (tr_ and str(tr_[2])))
    for v_ in ("x|Rock_Bedrock", "5|No_Such_Block_X", "9999|Rock_Bedrock", "5|a b"):
        rb_ = CFn().apply(JArray(JObject)(["tset", "regrow", "copper", v_, A["u"], "Skyy", "yes", "menu"]))
        K.check(rb_ is not None and str(rb_[0]) == "bad" and int(Cfg.regrowSec("copper")) == 7, "K: a bad regrow line is refused, nothing changes: %s -> %s" % (v_, rb_ and str(rb_[2])))
    ta_ = CFn().apply(JArray(JObject)(["add", "regrow", "fiber", "2|Rock_Bedrock", A["u"], "Skyy", "yes", "menu"]))
    K.check(ta_ is not None and str(ta_[0]) == "ok" and wait_for(lambda: int(Cfg.regrowSec("fiber")) == 2), "K: a new regrow row (add): %s" % (ta_ and str(ta_[2])))
    tk_ = CFn().apply(JArray(JObject)(["keys", "regrow", ""]))
    ke_ = dict(zip([str(x) for x in tk_[0]], [str(x) for x in tk_[2]])) if tk_ is not None else {}
    K.check(len(ke_) == 14 and ke_.get("copper") == "7|Rock_Bedrock" and ke_.get("logs") == "0|none" and ke_.get("gem") == "30|Rock_Bedrock", "K: the regrow table lists every type: %s" % ke_)
    tr2_ = CFn().apply(JArray(JObject)(["remove", "regrow", "fiber", A["u"], "Skyy", "yes", "menu"]))
    K.check(tr2_ is not None and str(tr2_[0]) == "ok" and wait_for(lambda: not Cfg.REGROW.containsKey("fiber")) and int(Cfg.regrowSec("fiber")) == 5,
            "K: a removed row - the type falls back to regen.defaultSec")
    CFn().apply(JArray(JObject)(["tset", "regrow", "copper", "4|Rock_Bedrock", A["u"], "Skyy", "yes", "menu"]))
    K.check(wait_for(lambda: int(Cfg.regrowSec("copper")) == 4), "K: (copper back to 4 s)")
    ra_ = CFn().apply(JArray(JObject)(["action", "regen.restoreAll", A["u"], "Skyy", "yes", "menu"]))
    K.check(ra_ is not None and str(ra_[0]) == "ok" and str(ra_[2]) == "Nothing is waiting to grow back.", "K: the Restore all action: %s" % (ra_ and str(ra_[2])))
    K.check(str(CFn.cmdSetConsole("zones.worlds", "a/b")) and str(Cfg.WORLDS) == "", "K: zones.worlds check hook refuses a bad name")
    act = CFn().apply(JArray(JObject)(["action", "reload.files", A["u"], "Skyy", "yes", "menu"]))
    K.check(act is not None and str(act[0]) == "ok" and str(act[2]).startswith("Re-read: 13 resource types; 2 regions in 1 worlds"), "K: the Re-read files action: %s" % (act and str(act[2])))
    kr = CFn().apply(JArray(JObject)(["keys", "region", ""]))
    ents_ = [str(x) for x in kr[0]] if kr is not None else []
    vals_ = [str(x) for x in kr[2]] if kr is not None else []
    mine_cell = "skyblock; priority 5; types stone,copper; flags none; title Copper Mine; world %s; 1 box 21 x 21 x 21" % WORLD
    town_cell = "full; priority 0; types none; flags containers; title Town; world %s; 1 box 11 x 21 x 11" % WORLD
    K.check(ents_ == ["mine", "town"] and vals_ == [mine_cell, town_cell], "K: the regions table lists every region: %s %s" % (ents_, vals_))
    # fixer 2 (critic 3 #2): the regions table edits mode / priority / types / flags / title, all or nothing, through ZStore
    RK = P("ZRegKit")

    def tset(cell, ent="mine"):
        return CFn().apply(JArray(JObject)(["tset", "region", ent, cell, A["u"], "Skyy", "yes", "menu"]))
    chg0 = len(open(os.path.join(home, "region-changes.log"), encoding="utf8").read().splitlines())
    ts_ = tset(mine_cell.replace("priority 5", "priority 8").replace("title Copper Mine", "title Copper Pit").replace("types stone,copper", "types stone,copper,iron"))
    chg1 = open(os.path.join(home, "region-changes.log"), encoding="utf8").read().splitlines()
    K.check(ts_ is not None and str(ts_[0]) == "ok" and int(Sto.get("mine").priority) == 8 and str(Sto.get("mine").title) == "Copper Pit"
            and list(map(str, Sto.get("mine").types)) == ["stone", "copper", "iron"] and "region.mine.priority=8" in ftext()
            and len(chg1) == chg0 + 1 and chg1[-1].endswith("\tServer Setup\tedit mine: mode skyblock, priority 8, types stone,copper,iron, flags (none), title Copper Pit"),
            "K: a table edit changes several fields at once (file + ONE change-log line): %s / %s" % (ts_ and str(ts_[2]), chg1[-1:]))
    for cell_, want_ in ((mine_cell.replace("world %s" % WORLD, "world elsewhere"), "world can't change"), (mine_cell.replace("1 box 21", "2 boxes 21"), "Boxes change by command"),
                         (mine_cell.replace("priority 5", "priority 5000"), "priority is a whole number"), (mine_cell.replace("types stone,copper", "types nope"), "No resource type 'nope'"),
                         ("colour red", "Unknown part 'colour red'"), (" ; ", "Nothing to change"), (mine_cell[:150] + "...", "too long to edit here")):
        r_ = tset(cell_)
        K.check(r_ is not None and str(r_[0]) == "bad" and want_ in str(r_[2]) and int(Sto.get("mine").priority) == 8, "K: table edit refused, nothing changed: %s -> %s" % (want_, r_ and str(r_[2])))
    r_ = tset("skyblock; priority 5; types stone,copper; title Copper_Mine")
    K.check(r_ is not None and str(r_[0]) == "ok" and str(RK.customGet("region[mine]")) == mine_cell,
            "K: a partial line changes only the parts it names (the cell is back to the start): %s" % (r_ and str(r_[2])))
    r_ = tset("full", "town")
    K.check(r_ is not None and str(r_[0]) == "ok", "K: an unchanged line is fine: %s" % (r_ and str(r_[2])))
    ad_ = CFn().apply(JArray(JObject)(["add", "region", "newone", "full", A["u"], "Skyy", "yes", "menu"]))
    rm_ = CFn().apply(JArray(JObject)(["remove", "region", "town", A["u"], "Skyy", "yes", "menu"]))
    K.check(ad_ is not None and str(ad_[0]) == "bad" and "needs wand corners" in str(ad_[2]) and rm_ is not None and str(rm_[0]) == "bad"
            and "/zones region delete town" in str(rm_[2]) and Sto.get("town") is not None and Sto.get("newone") is None,
            "K: adding / removing a region in the table points to the commands: %s / %s" % (ad_ and str(ad_[2]), rm_ and str(rm_[2])))
    Sto.BAD = "test"
    K.check(str(tset(mine_cell.replace("priority 5", "priority 9"))[0]) == "bad" and int(Sto.get("mine").priority) == 5, "K: a table edit is blocked while the regions file has a problem")
    Sto.BAD = None
    K.check(RK.customGet("region[nope]") is None and str(RK.customGet("region")) == "" and str(RK.customSet("bogus", "x")[0]) == "bad"
            and len(str(RK.customGet("region[mine]"))) <= 200, "K: ZRegKit customGet / customSet edges")

    # ---------------------------------------------------------------- M: commands
    def run(p, *words):
        Cmds.run(p["ref"], p["st"], p["pr"], wA if p["st"] is stA else (wO if p["st"] is stO else wI), JArray(JString)(list(words)))
        return said(p)
    h_admin, h_guest = run(A), run(Gst)
    K.check(len(h_admin) == 10 and len(h_guest) == 3 and h_admin[0] == "SkyyZones - protected worlds and areas:" and h_guest[1].endswith("/zones status - regrowing blocks")
            and any(l_.startswith("Overlap: the higher priority wins; on a tie a skyblock region wins") for l_ in h_admin), "M: help (admins see 6 more lines, incl. the tie rule)")
    K.check(run(A, "help") == h_admin and run(Gst, "bogus") == h_guest, "M: help word + an unknown word = help")
    api.tgt, api.blocks = [5, 70, 5], {(5, 70, 5): "Ore_Copper_Stone"}
    inf = run(A, "info")
    K.check(inf[0] == "Zones info - the block you look at: Ore_Copper_Stone at 5 70 5 in %s" % WORLD and inf[1] == "World: protected only inside regions"
            and inf[2].startswith("Region here (wins): mine (skyblock, priority 5") and inf[2].endswith("- this block is type copper (grows back after about 4 s)")
            and inf[3].startswith("Break: allowed | Place: refused - You can't place") and inf[-1] == "You: builder mode off"
            and inf[4].startswith("Guard errors since start: "), "M: info (looked-at block; the guard error count shows): %s" % inf)
    api.tgt = None
    inf2 = run(Gst, "info")
    K.check(inf2[0] == "Zones info - the block under you: Rock_Stone at 2 69 2 in %s" % WORLD and inf2[2].startswith("Region here (wins): mine"), "M: info (no target = under you): %s" % inf2[:3])
    Cfg.OP_BYPASS = True
    Cfg.ON = False
    inf3 = run(A, "info")
    Cfg.OP_BYPASS = False
    Cfg.ON = True
    K.check("ZONE PROTECTION IS OFF" in inf3[1] and not any(l.startswith("Break:") for l in inf3) and inf3[-1].endswith("admins always bypass (Server Setup)"), "M: info with protection off + bypass on")
    K.check(run(O, "info")[2] == "Regions here: none", "M: info with no region")
    li = run(A, "list")
    K.check(li[0].startswith("World %s: protected only inside regions; 2 regions:" % WORLD) and li[1].startswith(" mine (skyblock, priority 5")
            and li[2].startswith(" town (full, priority 0"), "M: list: %s" % li)
    K.check(run(O, "show") == ["This world has no regions."] and run(A, "show", "nope") == ["No region nope in this world (/zones list)."], "M: show refusals")
    K.check(run(A, "show")[0].startswith("Outlining the regions within 64 blocks for 30 s") and run(A, "show", "mine")[0].startswith("Outlining region mine")
            and run(A, "show", "off") == ["Outline off."], "M: show / show <region> / show off")
    K.check(run(A, "show", "mine", "60")[0].startswith("Outlining region mine for 60 s") and run(A, "show", "mine", "9999")[0].startswith("Outlining region mine for 300 s")
            and run(Gst, "show", "mine", "x")[0].startswith("Outlining region mine for 30 s") and run(A, "show", "off") == ["Outline off."], "M: show <region> <seconds> (5-300; a bad number = the setting)")
    K.check(run(A, "show", "45")[0].startswith("Outlining the regions within 64 blocks for 45 s") and run(A, "show", "off") == ["Outline off."],
            "M: /zones show <seconds> = every region near you (a number is never a region name)")
    run(Gst, "show", "off")
    K.check(run(Gst, "build", "maybe") == ["Use /zones build on or /zones build off."] and run(Gst, "build", "off") == ["Builder mode is already off."], "M: build bad word / already off")
    b_on = run(Gst, "build", "on")
    K.check(b_on[0].startswith("Builder mode ON") and api.titles[-1] == ("Guest", "BUILD MODE", "Protection is off for you - /zones build off") and bool(Bld.on(Gst["u"])), "M: build on (title)")
    K.check(run(Gst, "build")[0].startswith("Builder mode off") and not bool(Bld.on(Gst["u"])), "M: build = toggle")
    for w_ in ("wand", "reload", "protect", "type", "region", "restore", "audit"):
        K.check(run(Gst, w_, "x") == ["Only zone admins (skyyzones.admin) can use /zones %s." % w_] or run(Gst, w_) == ["Only zone admins (skyyzones.admin) can use /zones %s." % w_],
                "M: %s is admin-only" % w_)
    for g_r, want in ((0, "A Zone Wand is in your inventory."), (1, "You already have a Zone Wand."), (2, "No room for the Zone Wand"), (3, "Could not give the Zone Wand")):
        api.give_r = g_r
        K.check(run(A, "wand")[0].startswith(want), "M: wand answer %d" % g_r)
    K.check(run(A, "reload")[0].startswith("Re-read: 13 resource types; 2 regions"), "M: reload")
    K.check(run(A, "protect", "maybe") == ["Use /zones protect on or /zones protect off."] and run(A, "protect", "off")[0].startswith("World %s is already not protected" % WORLD), "M: protect refusals")
    p_on = run(A, "protect", "on")
    CPub.flush()
    K.check(str(Cfg.WORLDS) == WORLD and "zones.worlds=%s" % WORLD in open(cfgf, encoding="utf8").read() and p_on[-1].startswith("World %s is now protected everywhere" % WORLD),
            "M: protect on (through the kit: field + file + log): %s" % p_on)
    K.check(fire(Gst, "break", 100, 70, 100), "M: ... now refused outside the regions too")
    run(A, "protect", "off")
    CPub.flush()
    K.check(str(Cfg.WORLDS) == "" and not fire(Gst, "break", 100, 70, 100), "M: protect off")
    t1 = run(A, "type", "fiber", "Plant_Fiber*,Plant_Grass_*")
    CPub.flush()
    import time
    for _ in range(50):
        if Cfg.TYPES.containsKey("fiber"):
            break
        time.sleep(0.1)
    K.check(t1 and "types.properties is re-read" in t1[0] and Cfg.TYPES.containsKey("fiber") and "type.fiber=Plant_Fiber*,Plant_Grass_*" in open(tf, encoding="utf8").read(),
            "M: type add (kit table -> file -> the reload routine): %s" % t1)
    run(A, "type", "fiber", "Plant_Fiber*")
    CPub.flush()
    K.check("type.fiber=Plant_Fiber*\n" in open(tf, encoding="utf8").read(), "M: type change (tset)")
    t3 = run(A, "type", "fiber", "a/b")
    K.check(t3 and "is not a block id pattern" in t3[0], "M: type refused by the check hook: %s" % t3)
    run(A, "type", "fiber", "none")
    CPub.flush()
    for _ in range(50):
        if not Cfg.TYPES.containsKey("fiber"):
            break
        time.sleep(0.1)
    K.check("type.fiber" not in open(tf, encoding="utf8").read() and not Cfg.TYPES.containsKey("fiber"), "M: type none removes it")

    def wait_types(cond):
        CPub.flush()
        for _ in range(50):
            if cond():
                return True
            time.sleep(0.1)
        return False
    # C3 #3: /zones type <type> look
    api.tgt, api.blocks = [7, 70, 7], {(7, 70, 7): "Ore_Copper_Stone"}
    K.check(run(A, "type", "copper", "look") == ["Type copper already covers Ore_Copper_Stone."], "M: type look - a block the type already covers")
    api.blocks = {(7, 70, 7): "Plant_Fiber_Test"}
    tl_ = run(A, "type", "fiber", "look")
    K.check(wait_types(lambda: Cfg.TYPES.containsKey("fiber")) and tl_ and "types.properties is re-read" in tl_[0]
            and "type.fiber=Plant_Fiber_Test\n" in open(tf, encoding="utf8").read(), "M: type look makes a new type from the looked-at block: %s" % tl_)
    api.blocks = {(7, 70, 7): "*Plant_Grass_X"}
    run(A, "type", "fiber", "look")
    K.check(wait_types(lambda: len(Cfg.TYPES.get("fiber")) == 2) and "type.fiber=Plant_Fiber_Test,Plant_Grass_X\n" in open(tf, encoding="utf8").read(),
            "M: type look appends to an existing type (state prefix * stripped)")
    api.tgt = None
    K.check(run(A, "type", "fiber", "look")[0].startswith("Look at a block"), "M: type look without a target block")
    run(A, "type", "fiber", "none")
    K.check(wait_types(lambda: not Cfg.TYPES.containsKey("fiber")), "M: (fiber removed again)")
    # spec 5.1 /zones type add <type> <ids|look>: adds (a new type is made)
    run(A, "type", "add", "fiber", "Plant_Fiber_A")
    K.check(wait_types(lambda: Cfg.TYPES.containsKey("fiber")) and "type.fiber=Plant_Fiber_A\n" in open(tf, encoding="utf8").read(), "M: type add makes a new type")
    run(A, "type", "add", "fiber", "Plant_Fiber_B,Plant_Fiber_A")
    K.check(wait_types(lambda: len(Cfg.TYPES.get("fiber")) == 2) and "type.fiber=Plant_Fiber_A,Plant_Fiber_B\n" in open(tf, encoding="utf8").read(), "M: type add appends (no doubles)")
    K.check(run(A, "type", "add", "fiber", "Plant_Fiber_B") == ["Type fiber already lists Plant_Fiber_B."] and run(A, "type", "add", "fiber", "none")[0].startswith("Use /zones type fiber none"),
            "M: type add - already listed / none")
    api.tgt, api.blocks = [7, 70, 7], {(7, 70, 7): "Plant_Fiber_C"}
    run(A, "type", "add", "fiber", "look")
    K.check(wait_types(lambda: len(Cfg.TYPES.get("fiber")) == 3), "M: type add <type> look appends the looked-at block")
    api.tgt = None
    K.check(run(A, "type", "frob", "fiber", "x") == h_admin, "M: a 4-word type that is not 'add' = help")
    run(A, "type", "fiber", "none")
    K.check(wait_types(lambda: not Cfg.TYPES.containsKey("fiber")), "M: (fiber removed again)")
    # regions by command
    Wand.SEL.clear()
    api.sel = None
    K.check(run(A, "region", "create", "z1", "full")[0].startswith("Mark a box first"), "M: create without corners")
    api.sel = [-10, 60, -10, -5, 65, -5]
    c1_ = run(A, "region", "create", "z1", "full")
    K.check(c1_[0].startswith("Region z1 created (full) in %s: 6 x 6 x 6" % WORLD)
            and c1_[1] == "(Corners from the vanilla selection tool: -10,60,-10..-5,65,-5 in %s - /zones show z1 to check it.)" % WORLD,
            "M: create from the vanilla selection (Z6) says which corners it used: %s" % c1_)
    Wand.hit(A["u"], WORLD, -20, 60, -20)
    Wand.hit(A["u"], WORLD, -18, 61, -19)
    K.check(run(A, "region", "addbox", "z1") == ["Box 2 added to z1 (3 x 2 x 2 blocks)."], "M: addbox from the wand corners (wand wins over the selection; no selection note)")
    for sub_, val, want in (("mode", "skyblock", "Region z1: mode = skyblock."), ("priority", "3", "Region z1: priority = 3."), ("title", "Zone_One", "Region z1: title = Zone One."),
                            ("types", "stone", "Region z1: types = stone."), ("flags", "furnaces", "Region z1: flags = furnaces."), ("title", "none", "Region z1: title = (none).")):
        K.eq(run(A, "region", sub_, "z1", val), [want], "M: region %s" % sub_)
    K.check(run(A, "region", "mode", "z1", "x") == ["The mode is full or skyblock."], "M: a refusal comes back red (the ! stripped)")
    K.check(run(A, "region", "frob", "z1")[0].startswith("Use /zones region create") and run(A, "region", "frob", "z1", "x")[0].startswith("Use /zones region create"), "M: unknown region word")
    K.check(run(A, "region", "delete", "z1") == ["Region z1 deleted."], "M: region delete")
    # spec 5.1 /zones region create <id> <mode> [types] (5 words)
    K.check(run(A, "region", "create", "z2", "skyblock", "stone,nope")[0].startswith("No resource type 'nope'") and Sto.get("z2") is None, "M: 5-word create checks the types first (nothing created)")
    c5_ = run(A, "region", "create", "z2", "skyblock", "stone,copper")
    K.check(c5_[0].startswith("Region z2 created (skyblock)") and c5_[1] == "Region z2: types = stone,copper." and list(map(str, Sto.get("z2").types)) == ["stone", "copper"],
            "M: 5-word create = create + types: %s" % c5_)
    K.check(run(A, "region", "delete", "z2") == ["Region z2 deleted."], "M: (z2 deleted)")
    # /zones reload clear (admin) - a normal file: nothing special
    K.check(run(A, "reload", "clear")[0].startswith("Re-read: 13 resource types; 2 regions") and run(Gst, "reload", "clear") == ["Only zone admins (skyyzones.admin) can use /zones reload."],
            "M: reload clear (admins only; a file with regions is read as usual)")
    K.check(run(A, "wand", "extra") == h_admin, "M: a word with the wrong count = help")
    api.boom = True
    K.check(run(A, "info") == ["Something went wrong - the server log has the details."] and any("/zones failed" in l for l in logged()), "M: a crash inside a command is caught")
    api.boom = False
    Cmds.run(A["ref"], stA, None, wA, JArray(JString)(["help"]))
    # the 4 variants through a stand-in CommandContext
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    root = P("ZCmd")()
    vm = jfield(AC, "variantCommands").get(root)
    K.check(str(root.getName()) == "zones" and vm.size() == 5 and sorted(int(k) for k in vm.keySet()) == [1, 2, 3, 4, 5], "V: /zones has usage variants for 1-5 words")
    grp = jfield(AC, "permissionGroups").get(root)
    K.check(grp is not None and grp.isEmpty() and "skyyzones.build" in str(jfield(AC, "permission").get(root)), "V: root needs skyyzones.build, no permission group")
    ex = P("ZCmd1").class_.getSuperclass().getDeclaredMethod("execute", JClass("com.hypixel.hytale.server.core.command.system.CommandContext").class_,
                                                             JClass("com.hypixel.hytale.component.Store").class_, REF.class_, PRc.class_, WLD.class_)
    for n_words, words, want in ((1, ["list"], "World %s" % WORLD), (2, ["show", "off"], "Outline off."), (3, ["region", "delete", "nope"], "No region nope."),
                                 (4, ["region", "mode", "nope", "full"], "No region nope."), (5, ["region", "create", "z9", "full", "nope"], "No resource type 'nope'")):
        vc = vm.get(JInt(n_words))
        g2 = jfield(AC, "permissionGroups").get(vc)
        K.check(g2 is not None and g2.isEmpty() and "skyyzones.build" in str(jfield(AC, "permission").get(vc)), "V: variant %d: skyyzones.build, no group" % n_words)
        cx = mkctx(vc, words)
        m_ = vc.getClass().getDeclaredMethod("execute", ex.getParameterTypes())
        m_.setAccessible(True)
        m_.invoke(vc, cx, stA, A["ref"], A["pr"], wA)
        K.check(said(A)[0].startswith(want), "V: variant %d executes %s" % (n_words, words))
    CS = JClass("com.hypixel.hytale.server.core.command.system.CommandSender")

    def sender(nodes):
        def hp(*a):
            x_ = a[0]
            n_ = str(x_.getId()) if hasattr(x_, "getId") else str(x_)
            return n_ in nodes
        return JProxy(CS, dict={"hasPermission": hp, "getUsername": lambda: "x", "getUuid": lambda: None, "sendMessage": lambda m: None})
    nodes_all = [root] + [vm.get(JInt(i)) for i in (1, 2, 3, 4, 5)]
    for ns_, want in (({"skyyzones.admin"}, True), ({"skyyzones.build"}, True), ({"skyyzones.admin", "skyyzones.build"}, True), (set(), False), ({"hytale.x"}, False)):
        got_ = [bool(c_.hasPermission(sender(ns_))) for c_ in nodes_all]
        K.check(got_ == [want] * 6, "V: hasPermission with %s = %s on /zones and its 5 variants: %s" % (sorted(ns_), want, got_))
    K.check(not bool(root.hasPermission(None)), "V: hasPermission(null) = false")
    m0_ = root.getClass().getDeclaredMethod("execute", ex.getParameterTypes())
    m0_.setAccessible(True)
    m0_.invoke(root, mkctx(root, []), stA, A["ref"], A["pr"], wA)
    K.check(said(A) == h_admin, "V: /zones alone = help")
    vc = vm.get(JInt(1))
    cx = mkctx(vc, [])
    m_ = vc.getClass().getDeclaredMethod("execute", ex.getParameterTypes())
    m_.setAccessible(True)
    m_.invoke(vc, cx, stA, A["ref"], A["pr"], wA)
    K.check(said(A) == h_admin, "V: a variant whose argument is missing (null) falls back to help")

    # ---------------------------------------------------------------- T: tick (titles, outline, reminder)
    tk = P("ZTick")()
    Tick.ACC.clear()
    Tick.CUR.clear()
    Tick.SHOWN.clear()
    del api.titles[:]
    Pw = mkplayer(stA, "Walker", 6, 35.5, 70.0, 5.5)

    def step(p, x=None, z=None, dt=0.6):
        if x is not None:
            p["tc"].setPosition(V3D(x, 70.0, z))
        tk.tick(JFloat(dt), 0, p["ch"], stA, cb)
    step(Pw)
    K.check(api.titles == [("Walker", "Town", "Protected area")], "T: entering a titled FULL region shows its title: %s" % api.titles)
    step(Pw)
    step(Pw, dt=0.2)
    K.check(len(api.titles) == 1, "T: staying shows nothing new; under 0.5 s nothing runs")
    del api.notes[:]
    step(Pw, 100.5, 100.5)
    K.check(notes() == [("Walker", "You left Town.")], "T: leaving shows a small note")
    step(Pw, 35.5, 5.5)
    K.check(len(api.titles) == 1, "T: re-entering inside titles.gapSec shows no title again")
    step(Pw, 5.5, 5.5)
    K.check(api.titles[-1] == ("Walker", "Copper Mine", "Gathering area"), "T: walking into the mine shows the mine (gathering area)")
    Cfg.LEAVE = False
    step(Pw, 100.5, 100.5)
    K.check(not notes(), "T: titles.leave off - no note")
    Cfg.LEAVE = True
    Tick.SHOWN.put(str(Pw["u"]) + "|" + WORLD + "|town", JLong(0))
    step(Pw, 35.5, 5.5)
    K.check(api.titles[-1] == ("Walker", "Town", "Protected area"), "T: after the gap the title shows again")
    del api.notes[:]
    Tick.titles(Pw["pr"], Pw["u"], OTHER, 35, 70, 5, JLong(int(time.time() * 1000)))
    K.check(not notes(), "T: going to another world from a titled region shows no false 'You left' note")
    Tick.titles(Pw["pr"], Pw["u"], WORLD, 100, 70, 100, JLong(int(time.time() * 1000)))
    K.check(not notes(), "T: ... nor coming back outside a region")
    # outline
    del api.parts[:]
    Cmds.show(Pw["pr"], WORLD, "", 30)
    step(Pw)
    n1 = len(api.parts)
    K.check(0 < n1 <= 160 and all(pp[0] == "Alerted" and pp[4] == [str(Pw["ref"])] for pp in api.parts), "T: the outline = particles to the owner only, capped (%d)" % n1)
    logged()
    Cfg.PARTICLE = "bad id!"
    K.check(str(Cfg.particle()) == "Alerted" and str(Cfg.particle()) == "Alerted" and sum(1 for l in logged() if "cannot be drawn" in l) == 1,
            "T: a hand-edited show.particle the game cannot draw falls back to Alerted (warned once)")
    Cfg.PARTICLE = "Some_Particle"
    cpv_ = Cfg.checkParticle("show.particle", "Some_Particle")
    K.check(str(Cfg.particle()) == ("Alerted" if cpv_ is not None else "Some_Particle"), "T: a particle id is checked against the game's particle map at use time (%s)" % cpv_)
    Cfg.PARTICLE = "Alerted"
    step(Pw)
    K.check(len(api.parts) == n1, "T: at most one outline pass a second")
    Tick.SHOW.get(Pw["u"]).last = JLong(0)
    Tick.SHOW.get(Pw["u"]).until = JLong(0)
    step(Pw)
    K.check(len(api.parts) == n1 and not Tick.SHOW.containsKey(Pw["u"]), "T: the outline expires")
    Cmds.show(Pw["pr"], WORLD, "mine", 30)
    Tick.SHOW.get(Pw["u"]).world = OTHER
    step(Pw)
    K.check(not Tick.SHOW.containsKey(Pw["u"]), "T: a world switch ends the outline")
    sh = P("ZShow")(WORLD, "mine", JLong(10 ** 15))
    K.check(int(Tick.draw(Pw["ref"], stA, sh, 5000, 70, 5000)) == 0, "T: no box within 64 blocks = nothing drawn")
    # reminder
    Bld.set(Pw["u"], "Walker", True)
    Bld.ON.get(Pw["u"])[1] = JLong(0)
    step(Pw)
    K.check(notes()[-1] == ("Walker", "Build mode is ON - protection does not stop you. /zones build off"), "T: the builder-mode reminder")
    step(Pw)
    K.check(not notes(), "T: ... not again before build.remindSec")
    Cfg.REMIND = 0
    Bld.ON.get(Pw["u"])[1] = JLong(0)
    step(Pw)
    K.check(not notes(), "T: build.remindSec 0 = no reminder")
    Cfg.REMIND = 300
    bad_ch = U.allocateInstance(MCH.class_)
    bad_ch.boom = True
    tk.tick(JFloat(1.0), 0, bad_ch, stA, cb)
    tk.tick(JFloat(1.0), 0, bad_ch, stA, cb)
    K.check(sum(1 for l in logged() if "tick failed (logged once)" in l) == 1, "T: a broken tick is logged once")
    K.check(tk.getQuery() is not None and not bool(tk.isParallel(1, 1)), "T: query + not parallel")
    # logout clean-up through a REAL PlayerDisconnectEvent
    Wand.hit(Pw["u"], WORLD, 1, 1, 1)
    Quit = P("ZQuit")()
    Quit.accept(PDE(Pw["pr"]))
    K.check(not bool(Bld.on(Pw["u"])) and not Wand.SEL.containsKey(Pw["u"]) and not Tick.CUR.containsKey(Pw["u"]) and not Tick.ACC.containsKey(Pw["u"])
            and not any(str(k).startswith(str(Pw["u"])) for k in Tick.SHOWN.keySet()) and Cfg.bridge().get("zones:build:" + str(Pw["u"])) is None,
            "T: logout - builder mode off (key gone), corners / titles / outline forgotten")
    Quit.accept("not an event")
    Quit.accept(None)

    # ---------------------------------------------------------------- B: bridge functions
    Fn.publish()
    b_ = Cfg.bridge()
    chk, regf = b_.get("zones:fn:check"), b_.get("zones:fn:region")
    K.check(str(b_.get("zones:version")) == VERSION and chk is not None and regf is not None, "B: published")
    O_ = lambda *a: JArray(JObject)(list(a))
    K.check(str(chk.apply(O_(WORLD, JInt(35), JInt(70), JInt(5), "break", "Rock_Stone"))) == "deny" and str(chk.apply(O_(WORLD, JInt(5), JInt(70), JInt(5), "break", "Rock_Stone"))) == "allow"
            and str(chk.apply(O_(WORLD, "5", JInt(70), JInt(5), "place", "x"))) == "deny" and str(chk.apply(O_(WORLD, JInt(35), JInt(70), JInt(5), "container"))) == "allow"
            and str(chk.apply(O_(WORLD, JInt(35), JInt(70), JInt(5), "furnace"))) == "deny" and str(chk.apply(O_(WORLD, JInt(35), JInt(70), JInt(5)))) == "deny",
            "B: zones:fn:check (break / place / container / furnace / default break)")
    K.check(chk.apply("x") is None and chk.apply(O_(WORLD, "x", JInt(1), JInt(1))) is None and chk.apply(O_(WORLD)) is None, "B: bad input = null")
    Cfg.ON = False
    K.check(str(chk.apply(O_(WORLD, JInt(35), JInt(70), JInt(5), "break"))) == "allow", "B: protection off = allow")
    Cfg.ON = True
    K.check(str(regf.apply(O_(WORLD, JInt(35), JInt(70), JInt(5)))) == "town" and regf.apply(O_(WORLD, JInt(500), JInt(70), JInt(5))) is None, "B: zones:fn:region")
    b_.put("zones:fn:check", "someone else")
    Fn.unpublish()
    K.check(str(b_.get("zones:fn:check")) == "someone else" and b_.get("zones:fn:region") is None and b_.get("zones:version") is None, "B: unpublish removes only OUR entries")
    b_.remove("zones:fn:check")

    # ---------------------------------------------------------------- E: the real engine branches (API off) fail safely, logged once
    Eng.API = None
    Cfg.WARNED.clear()
    logged()
    Eng.notify(A["pr"], "x")
    Eng.notify(A["pr"], "x")
    Eng.title(A["pr"], "t", None)
    Eng.particle("Alerted", 1.0, 2.0, 3.0, AL(), stA)
    t_ = Eng.target(A["ref"], stA)
    s_ = Eng.selection(A["ref"], stA, A["pr"])
    g_ = int(Eng.give(A["ref"], stA, "Skyy_Zones_Wand"))
    b2_ = Eng.blockAt(wA, 1, 70, 1)
    Eng.notify(None, "x")
    Eng.title(None, "t", "s")
    K.check(Eng.blockAt(wA, 1, -5, 1) is None and Eng.blockAt(None, 1, 1, 1) is None, "E: blockAt out of range / no world = null")
    lg = logged()
    K.check(t_ is None and s_ is None and g_ == 3 and b2_ is None, "E: target / selection / give / blockAt on stand-ins: null, null, 3, null")
    K.check(sum(1 for l in lg if "notification failed" in l) == 1, "E: the real notification path ran (fails on the stand-in PlayerRef, logged once): %s" % lg)
    K.check(int(Eng.count(None, "x")) == 0, "E: count(null)")
    # 0.2.0: the regrow engine calls on the stand-in world (no chunk store) - each answers safely
    Cfg.WARNED.clear()
    logged()
    st0_ = Eng.stateAt(wA, 1, 70, 1)
    pu0_ = bool(Eng.put(wA, 1, 70, 1, "Rock_Stone", 0))
    oc0_ = bool(Eng.occupied(wA, 1, 70, 1))
    Eng.load(wA, 1, 70, 1, None)
    wo0_ = Eng.world(WORLD)
    ex0_ = bool(getattr(Eng, "exec_")(wA, P("ZTicker")()))
    sc0_ = Eng.scan(wA, JArray(JInt)([0, 0, 0, 40, 40, 40]), JArray(JString)(["Rock_Bedrock"]), JArray(JInt)([0, 0]), JLong(1000))
    lg = logged()
    K.check(st0_ is None and not pu0_ and wo0_ is None and not ex0_ and sc0_ is not None and sc0_.size() == 0
            and not bool(Eng.put(None, 1, 1, 1, "x", 0)) and Eng.stateAt(None, 1, 1, 1) is None and not bool(Eng.put(wA, 1, -5, 1, "Rock_Stone", 0)),
            "E: stateAt / put / world / exec / scan on stand-ins: null, false, null, false, empty (logged once each): %s" % lg)
    K.check(any("chunk load failed" in l for l in lg) and any("audit scan failed" in l for l in lg) and any("player-in-block check failed" in l for l in lg) == (oc0_ is True),
            "E: the real chunk-load / scan / player-check paths ran (fail on the stand-in world, logged once)")
    Eng.API = api
    # ---------------------------------------------------------------- P: the plugin
    pl = U.allocateInstance(Plug.class_)
    try:
        pl.setup()
        K.check(True, "P: setup() on an allocated plugin never throws (its catch logs)")
    except Exception as e:
        K.check(False, "P: setup() threw: %s" % e)
    Bld.set(A["u"], "Skyy", True)
    Bld.clearAll()
    K.check(Bld.ON.isEmpty() and Cfg.bridge().get("zones:build:" + str(A["u"])) is None, "P: clearAll (shutdown) removes builder mode + keys")
    Eng.API = api
    Dep.CLOCK = JLong(T0 + 900000)
    api.wb[(WORLD, 4, 70, 4)] = "Rock_Stone"
    fire(Gst, "break", 4, 70, 4, block="Rock_Stone")
    P("ZTicker").stop()
    P("ZRegen").shutdown()
    K.check(not os.path.exists(os.path.join(rdir, WORLD + ".journal")) and "D 4 70 4 Rock_Stone stone" in open(os.path.join(rdir, WORLD + ".snap"), encoding="utf8").read(),
            "P: shutdown - the regrow timer stops, a final snapshot holds every waiting block, the journal is emptied")
    Dep.CLOCK = JLong(0)
    CPub.shutdown()
    K.check(Guard.REFUSED.get() > 0 and Guard.ALLOWED.get() > 0 and Guard.BYPASSED.get() > 0, "X: counters moved")


# ====================================================================================================== D: live copy, started twice
def snap(d):
    out = {}
    for base, _dirs, fs in os.walk(d):
        for f in fs:
            p_ = os.path.join(base, f)
            out[os.path.relpath(p_, d).replace(os.sep, "/")] = hashlib.sha1(open(p_, "rb").read()).hexdigest()
    return out


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Plug, CPub, Cfg, Sto = (JClass(PKG + n) for n in ("SkyyZonesPlugin", "CfgPub", "ZCfg", "ZStore"))
    Paths = JClass("java.nio.file.Paths")
    mods = home
    before = snap(mods)
    had = sorted(f for f in before if f.startswith("Skyy_SkyyZones/"))
    Sto.SYNC = True

    def start():
        r = str(Plug.paths(Paths.get(os.path.join(mods, "Skyy_SkyyZones"))))
        CPub.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones"))
        CPub.flush()
        CPub.shutdown()
        return r
    r1 = start()
    s1 = snap(mods)
    r2 = start()
    s2 = snap(mods)
    added = sorted(set(s1) - set(before))
    want = sorted(set(["Skyy_SkyyZones/config.properties", "Skyy_SkyyZones/regen.properties", "Skyy_SkyyZones/regions.properties",
                       "Skyy_SkyyZones/types.properties"]) - set(had))
    K.check(added == want or (had and set(added) <= set(want + ["Skyy_SkyyZones/regions.good.properties"]) and "Skyy_SkyyZones/regen.properties" in added),
            "D start 1 adds only the SkyyZones files (the folder had %d files): %s" % (len(had), added))
    K.check(all(before[f] == s1.get(f) for f in before if not f.startswith("Skyy_SkyyZones/regen/")), "D start 1: every other live file (%d) byte-identical" % len(before))
    K.check(s1 == s2, "D start 2 changes nothing (%s)" % sorted(f for f in set(s1) | set(s2) if s1.get(f) != s2.get(f)))
    K.check((had or r1.startswith("default config.properties written; protection ON")) and "regrowing ON" in r2 and r2.startswith("protection ON")
            and r2.endswith("waiting to grow back") and "default regen.properties written" in r1, "D: start 1 writes the defaults, start 2 reads them: %s | %s" % (r1, r2))
    K.check(not bool(Cfg.protectedWorld("NewBetaTest")) and not bool(Cfg.protectedWorld("skywynn_zones2")), "D: no live world is protected until an admin says so")
    K.save()


# ====================================================================================================== parent
def part_jar():
    FAILS = HK.FAILS
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    cls = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    HK.check(cls == sorted(PKG + c for c in CLASSES), "J: exactly the %d expected classes: +%s -%s" % (len(CLASSES), sorted(set(cls) - set(PKG + c for c in CLASSES)),
                                                                                                   sorted(set(PKG + c for c in CLASSES) - set(cls))))
    other = sorted(n for n in names if not n.endswith(".class"))
    HK.check(other == ["Server/Item/Items/SkyyZones/Skyy_Zones_Wand.json", "Server/Languages/en-US/server.lang", "manifest.json"], "J: non-class entries: %s" % other)
    man = json.loads(z.read("manifest.json"))
    HK.check(man["Name"] == "%s SkyyZones" % VERSION and man["Version"] == VERSION and man["Main"] == PKG + "SkyyZonesPlugin" and man["IncludesAssetPack"] is True
             and man["Group"] == "Skyy" and "Dependencies" not in man, "J: manifest (Group Skyy, Name, Version, Main, asset pack, no dependency)")
    item = json.loads(z.read("Server/Item/Items/SkyyZones/Skyy_Zones_Wand.json"))
    az = set(zipfile.ZipFile(ASSETS).namelist())
    paths = ["Common/" + item["Icon"], "Common/" + item["Model"], "Common/" + item["Texture"], "Server/Item/Qualities/%s.json" % item["Quality"]]
    HK.check(all(p in az for p in paths) and item["MaxStack"] == 1 and item["DropOnDeath"] is False, "J: every vanilla path the wand JSON names exists: %s" % [p for p in paths if p not in az])
    HK.check(not any(n.endswith("/Skyy_Zones_Wand.json") for n in az), "J: Skyy_Zones_Wand is not a vanilla id")
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines()
    keys = sorted(l.split("=", 1)[0] for l in lang)
    HK.check(keys == sorted(["items.Skyy_Zones_Wand.name", "items.Skyy_Zones_Wand.description", "server.items.Skyy_Zones_Wand.name", "server.items.Skyy_Zones_Wand.description"])
             and "items.Skyy_Zones_Wand.name=Zone Wand" in lang, "J: server.lang = the 4 wand keys")
    pl = z.read("com/skyy/zones/SkyyZonesPlugin.class")
    HK.check(b"[SkyyZones] 0.2.0 ready - " in pl, "J: the ready line the smoke test reads")
    # class compare old (0.1.0) vs new
    if os.path.isfile(OLD_JAR):
        oz = zipfile.ZipFile(OLD_JAR)
        old_c = set(n for n in oz.namelist() if n.endswith(".class"))
        new_c = set(n for n in names if n.endswith(".class"))
        HK.check(old_c <= new_c and sorted(n.rsplit("/", 1)[1][:-6] for n in new_c - old_c) == sorted(NEW_CLASSES),
                 "J: class compare 0.1.0 -> 0.2.0: none removed, added exactly %s: +%s -%s" % (NEW_CLASSES, sorted(new_c - old_c), sorted(old_c - new_c)))
        ch_ = sorted(n for n in old_c & new_c if oz.read(n) != z.read(n))
        print("J. class compare: %d kept (%d changed: %s), %d added" % (len(old_c & new_c), len(ch_), [c.rsplit("/", 1)[1][:-6] for c in ch_], len(new_c - old_c)))
    else:
        HK.check(False, "J: the 0.1.0 jar for the class compare is missing: %s" % OLD_JAR)
    for n in names:
        HK.check(not n.lower().endswith(".ui"), "J: no .ui file")


def main():
    phases = {"mkfake": lambda: run_mkfake(FAKE_DIR), "verify": lambda: HK.run_verify(arg("--out"), JAR),
              "exec": lambda: run_exec(arg("--out"), JAR, SCRATCH, None), "live": lambda: run_live(arg("--out"), JAR, SCRATCH, arg("--home")),
              "audit": lambda: HK.run_audit(arg("--out"), JAR, FAKE_DIR)}
    if "--phase" in sys.argv:
        try:
            phases[arg("--phase")]()
        except SystemExit:
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    assert os.path.isfile(JAR), JAR
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    os.makedirs(FAKE_DIR, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    part_jar()

    def child(label, *extra):
        out = os.path.join(SCRATCH, "%s.json" % label)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out] + list(extra), env=env)
        HK.check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (label, p.returncode))
        return out
    try:
        child("mkfake")
        for label in ("verify", "exec"):
            HK.take(child(label), label)
        if os.path.isdir(LIVE):
            home = os.path.join(SCRATCH, "live", "mods")
            shutil.copytree(LIVE, home)
            print("D. live mods/ copied (read-only source %s)" % LIVE)
            HK.take(child("live", "--home", home), "live")
        else:
            HK.check(False, "D: no live folder %s" % LIVE)
        outa = child("audit")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyZones %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
    for f in HK.FAILS:
        print("FAIL:", f)
    sys.exit(1 if HK.FAILS else 0)


if __name__ == "__main__":
    main()
