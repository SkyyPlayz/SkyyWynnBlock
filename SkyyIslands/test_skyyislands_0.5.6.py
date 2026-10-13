"""Harness for SkyyIslands 0.5.6 - the HYTALE 0.7.0 PORT (tools/islands_0_5_6_patch.py). Committed next to the build so the build docstring's
CHECKED claims can be re-run instead of trusted; copy it to the next version and keep it passing.

    python SkyyIslands/test_skyyislands_0.5.6.py [--jar <SkyyIslands-0.5.6.jar>] [--old <SkyyIslands-0.5.5.jar>] [--dir <scratch>]
                                                 [--live <a save's mods folder>] [--no-server] [--keep]

Build first (python tools/islands_0_5_6_patch.py, then python SkyyIslands/build_skyyislands_0.5.6.py). Part 1 = one bare JVM (the game's
JRE, -Xverify:all, -XX:-UsePerfData; the installed 0.7 HytaleServer.jar + tools/javassist.jar; EACH SkyyIslands jar in its own class
loader). Part 2 = the REAL 0.7 server through tools/smoke_test.py (game closed; offline, on its scratch copy of the test world) with a
scratch-only probe plugin built here.
  A  every class of both jars loads, verifies and initialises (-Xverify:all) on the 0.7 engine
  B  class compare 0.5.5 vs 0.5.6: every class byte-identical or different only in version strings, except exactly TintFix, FillTask,
     ChunkFill, RelightNow, HubCmd and IslandBuild (each method gone / new / changed exactly as planned) + the new HubSpawn;
     IslandMenuPage byte-identical; SkyyIslandsPlugin = 0.5.5's bytes once its ready constant is swapped back
  C  engine-access audit on the 0.7 jar: every method / field reference of every 0.5.6 class resolves with its exact descriptor (class,
     superclasses, interfaces); 0.5.5 shows the 9 known misses (control); no concrete class leaves an engine abstract method open; no
     method shadows an engine method of the same name with another descriptor (a lost override)
  D  the new code paths executed in the bare JVM on real engine objects (Unsafe-allocated World / Universe / ChunkStore, javassist fakes
     only at the edges: the entity Store's addComponent = the teleport, PacketHandler = chat, ChunkLightingManager = the relight call,
     ISpawnProvider = a provider that answers late):
     D1 /hub with no hub, default world on the REAL GlobalSpawnProvider: teleport added at once (same call) at the spawn point; 0.5.5
        throws NoSuchMethodError there (the bug); D2 a late answer: sendToHub returns true at once without blocking, nothing is added
        off the world thread, the completion queues HubSpawn on the player's world, draining it adds the teleport; D3 a failed answer and
        D4 an empty answer: no teleport, the no-hub line + a warning; D5 the player left the world (ref invalid) before the answer: no
        teleport; D6 the /sethub hub: identical to 0.5.5 (fixed point, no spawn lookup); D7 ChunkFill.load with no chunk store: the
        future still completes (no hung creation chain); D8 FillTask on a real ChunkStore with the island sections not loaded: "chunk
        (0,0) did not load" + done; D9 FillTask.accept with a load error queues the fill on the world thread; D10 TintFix.fix with no
        loaded chunk = 0; D11 RelightNow: 9 x invalidateLightInChunkSections(the world's ChunkStore, cx, cz, 0, 10), "9/9 chunks"
  E  start twice on a SCRATCH COPY of the live Skyy_SkyyIslands data (the plugin's setup data path: config load, hub, island worlds,
     0.5.3 plan, config kit start / stop, 0.5.3 apply): no file written either time
  S  the REAL 0.7 server (tools/smoke_test.py --jar <0.5.6> --jar <probe>): SkyyIslands 0.5.6 ready, no SkyyIslands SEVERE / exception;
     the probe makes an island the way /island does (InstancesPlugin.spawnInstance("SkyyIsland") -> IslandBuild) and checks on the
     world thread: every island block at its place (block for block = the 0.5.5 FillTask layout), the starter chest's ItemContainerBlock
     holding the whole starter kit (in the chest's block HOLDER: nobody is near, so the section is NonTicking), green tint, the
     island's own log lines (island world, N blocks, kit placed n of n stacks, relight 9/9); a second fill is skipped; TintFix on the
     real BlockChunk; H6 the section switched to ticking by the engine (flag 4, what a nearby player / /chunk load causes) turns the
     holder into the chest ENTITY with the same kit; H7 (before H6) the island's chunks saved (saveChunksInWorld = /world save),
     chunk (0,0) unloaded (ChunkStore.remove UNLOAD = /chunk unload) and loaded again without any fill: every block and the kit in the
     chest are still there (kitGiven is set at fill time, so a lost holder would lose the kit for good); the default world's spawn point through getSpawnPointAsync
Not testable without a client: the teleport itself on a real player (seen as the Teleport component / HubSpawn queued on the world).
Nothing is deployed; nothing outside the scratch folder is written (default tools/dev/scratch/islands056/h, deleted unless --keep;
tools/smoke_test.py keeps only its log under tools/dev/scratch/smoke/). The live save is only read (copied). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, struct, zipfile, time, subprocess, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.5.6", "0.5.5"
PKG = "com.skyy.islands."
PROBE_NAME, PROBE_VER = "SkyyIslandsProbe", "0.1"
GRASS = -10772952


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "islands056", "h")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyIslands-%s.jar" % OLD_VERSION)))
KEEP = "--keep" in sys.argv
NO_SERVER = "--no-server" in sys.argv
FAILS, OKS = [], [0]
NOTES = []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        if len(FAILS) < 80:
            print("FAIL", what)
    return cond


# ------------------------------------------------------------------------------------------------ class-file helpers (no JVM)
def cp_split(b):
    """(utf8 entries [(start, end, bytes)], the class bytes with every Utf8 entry's bytes cut out)"""
    n = struct.unpack(">H", b[8:10])[0]
    i, k, out = 10, 1, []
    while k < n:
        tag = b[i]
        if tag == 1:
            ln = struct.unpack(">H", b[i + 1:i + 3])[0]
            out.append((i, i + 3 + ln, b[i + 3:i + 3 + ln]))
            i += 3 + ln
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            i += 5
        elif tag in (5, 6):
            i += 9
            k += 1
        elif tag in (7, 8, 16, 19, 20):
            i += 3
        elif tag == 15:
            i += 4
        else:
            raise ValueError("constant pool tag %d" % tag)
        k += 1
    rest, pos = [], 0
    for s0, e0, _t in out:
        rest.append(b[pos:s0 + 1])
        pos = e0
    rest.append(b[pos:])
    return out, b"|".join(rest)


def version_only(old, new):
    uo, ro = cp_split(old)
    un, rn = cp_split(new)
    if ro != rn or len(uo) != len(un):
        return False
    norm = lambda t: t.replace(OLD_VERSION.encode(), b"<V>").replace(VERSION.encode(), b"<V>")
    return all(a[2] == b[2] or norm(a[2]) == norm(b[2]) for a, b in zip(uo, un))


def classes(jar):
    z = zipfile.ZipFile(jar)
    out = dict((n[:-6].replace("/", "."), z.read(n)) for n in z.namelist() if n.endswith(".class"))
    z.close()
    return out


def snap(d):
    out = {}
    for root, _ds, fs in os.walk(d):
        for f in fs:
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = (open(p, "rb").read(), os.path.getmtime(p))
    return out


def island_layout():
    """the 0.5.5 FillTask.run layout (world x,y,z -> block id), the same loops in the same order (later puts overwrite)"""
    L = {}
    for x in range(2, 14):
        for z in range(2, 14):
            if (x in (2, 13)) and (z in (2, 13)):
                continue
            L[(x, 128, z)] = "Soil_Grass"
            L[(x, 127, z)] = "Soil_Dirt"
            if 3 <= x <= 12 and 3 <= z <= 12:
                L[(x, 126, z)] = "Soil_Dirt"
            if 4 <= x <= 11 and 4 <= z <= 11:
                L[(x, 125, z)] = "Rock_Stone"
            if 6 <= x <= 9 and 6 <= z <= 9:
                L[(x, 124, z)] = "Rock_Stone"
    for y in range(129, 134):
        L[(11, y, 11)] = "Wood_Oak_Trunk"
    for x in range(9, 14):
        for z in range(9, 14):
            for y in range(132, 135):
                if x == 11 and z == 11 and y <= 133:
                    continue
                edge = (x in (9, 13)) and (z in (9, 13))
                if edge or (y == 134 and (x in (9, 13) or z in (9, 13))):
                    continue
                L[(x, y, z)] = "Plant_Leaves_Oak"
    L[(11, 135, 11)] = "Plant_Leaves_Oak"
    L[(4, 129, 4)] = "Furniture_Crude_Chest_Small"
    return L


# ================================================================================================ the probe plugin (S), built by javassist
PROBE_SRC = {
    "plugin_fields": ["public static com.hypixel.hytale.logger.HytaleLogger LOG;",
                      "public static java.util.concurrent.ScheduledFuture TICK;"],
    "log": r"""
public static void log(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyIslandsProbe] " + s); } catch (Throwable t) { }
}""",
    "setup": r"""
public void setup() {
  LOG = getLogger();
  log("%s ready - scratch-only engine probe for SkyyIslands %s (built by SkyyIslands/test_skyyislands_%s.py, never deployed)");
  TICK = com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new com.skyy.islandsprobe.ProbeTask(0), 3L, 2L, java.util.concurrent.TimeUnit.SECONDS);
}""" % (PROBE_VER, VERSION, VERSION),
}

DUMP_RUN = r"""
public void run() {
  try {
    if (this.mode == 1) {
      java.lang.reflect.Method fx = Class.forName("com.skyy.islands.TintFix", true, this.cl).getMethod("fix", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class });
      com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs0 = this.world.getChunkStore();
      com.hypixel.hytale.component.Ref cr0 = cs0.getChunkReference(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(0, 0));
      com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk bc0 = (com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk) cs0.getStore().getComponent(cr0, com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk.getComponentType());
      bc0.setTint(1, 1, 255); bc0.setTint(20, 7, 255); bc0.setTint(31, 31, 255);
      Object n = fx.invoke(null, new Object[] { this.world });
      com.skyy.islandsprobe.ProbePlugin.log(this.tag + " TintFix.fix after 3 columns were set wrong: " + n + " columns re-tinted");
    }
    if (this.mode == 3) {
      this.fut = com.hypixel.hytale.server.core.universe.world.storage.component.ChunkSavingSystems.saveChunksInWorld(this.world.getChunkStore().getStore(), this.world);
      com.skyy.islandsprobe.ProbePlugin.log(this.tag + " saving the island's chunks (ChunkSavingSystems.saveChunksInWorld - what /world save uses)");
      this.latch.countDown();
      return;
    }
    if (this.mode == 4) {
      com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs4 = this.world.getChunkStore();
      com.hypixel.hytale.component.Ref c4 = cs4.getChunkReference(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(0, 0));
      if (c4 != null) cs4.remove(c4, com.hypixel.hytale.component.RemoveReason.UNLOAD);
      com.hypixel.hytale.component.Ref c4b = cs4.getChunkReference(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(0, 0));
      com.hypixel.hytale.component.Ref s4 = cs4.getChunkSectionReferenceAtBlock(4, 129, 4);
      com.skyy.islandsprobe.ProbePlugin.log(this.tag + " chunk (0,0) unloaded (ChunkStore.remove UNLOAD - what /chunk unload does): was loaded " + (c4 != null) + ", loaded now " + (c4b != null) + ", chest section loaded now " + (s4 != null));
      this.latch.countDown();
      return;
    }
    if (this.mode == 2) {
      com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs2 = this.world.getChunkStore();
      com.hypixel.hytale.component.Ref sr = cs2.getChunkSectionReferenceAtBlock(4, 129, 4);
      boolean nt = cs2.getStore().getArchetype(sr).contains(com.hypixel.hytale.server.core.universe.world.storage.ChunkStore.REGISTRY.getNonTickingComponentType());
      cs2.getChunkSectionReferenceAsync(0, 4, 0, 4);
      boolean nt2 = cs2.getStore().getArchetype(sr).contains(com.hypixel.hytale.server.core.universe.world.storage.ChunkStore.REGISTRY.getNonTickingComponentType());
      com.skyy.islandsprobe.ProbePlugin.log(this.tag + " section (0,4,0) NonTicking " + nt + " -> " + nt2 + " (the engine's own switch: getChunkSectionReferenceAsync flag 4 = ticking, on the world thread - what /chunk load uses)");
      this.latch.countDown();
      return;
    }
    java.lang.reflect.Method ba = Class.forName("com.skyy.islands.FillTask", true, this.cl).getMethod("blockAt", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, Integer.TYPE, Integer.TYPE, Integer.TYPE });
    java.lang.reflect.Method be = Class.forName("com.skyy.islands.FillTask", true, this.cl).getMethod("blockEntity", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, Integer.TYPE, Integer.TYPE, Integer.TYPE });
    StringBuilder sb = new StringBuilder();
    int n = 0;
    int miss = 0;
    for (int y = 116; y <= 140; y++) for (int x = 0; x <= 15; x++) for (int z = 0; z <= 15; z++) {
      int id = ((Integer) ba.invoke(null, new Object[] { this.world, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) })).intValue();
      if (id < 0) { miss++; continue; }
      if (id == 0) continue;
      com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType bt = (com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType) com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType.getAssetMap().getAsset(id);
      sb.append(x).append(',').append(y).append(',').append(z).append('=').append(bt == null ? ("#" + id) : bt.getId()).append(';');
      n++;
    }
    com.skyy.islandsprobe.ProbePlugin.log(this.tag + " blocks " + n + " (positions in unloaded sections " + miss + ")");
    String s = sb.toString();
    int parts = (s.length() + 1499) / 1500;
    for (int i = 0; i < parts; i++) com.skyy.islandsprobe.ProbePlugin.log(this.tag + " dump " + (i + 1) + "/" + parts + " " + s.substring(i * 1500, Math.min(s.length(), (i + 1) * 1500)));
    java.lang.reflect.Method bh = Class.forName("com.skyy.islands.FillTask", true, this.cl).getMethod("blockHolder", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class, Integer.TYPE, Integer.TYPE, Integer.TYPE });
    com.hypixel.hytale.component.Ref r = (com.hypixel.hytale.component.Ref) be.invoke(null, new Object[] { this.world, Integer.valueOf(4), Integer.valueOf(129), Integer.valueOf(4) });
    Object comp = null;
    String kind = "none";
    if (r != null && r.isValid()) { comp = this.world.getChunkStore().getStore().getComponent(r, com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock.getComponentType()); kind = "entity"; }
    else {
      com.hypixel.hytale.component.Holder h = (com.hypixel.hytale.component.Holder) bh.invoke(null, new Object[] { this.world, Integer.valueOf(4), Integer.valueOf(129), Integer.valueOf(4) });
      if (h != null) { comp = h.getComponent(com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock.getComponentType()); kind = "holder"; }
    }
    if (!(comp instanceof com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock)) com.skyy.islandsprobe.ProbePlugin.log(this.tag + " chest " + kind + ": no ItemContainerBlock at 4,129,4");
    else {
      com.hypixel.hytale.server.core.inventory.container.ItemContainer c = ((com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock) comp).getItemContainer();
      StringBuilder k = new StringBuilder();
      int cap = c.getCapacity();
      for (int i = 0; i < cap; i++) {
        com.hypixel.hytale.server.core.inventory.ItemStack is = c.getItemStack((short) i);
        if (is != null && !is.isEmpty()) k.append(is.getItemId()).append(" x").append(is.getQuantity()).append(';');
      }
      com.skyy.islandsprobe.ProbePlugin.log(this.tag + " chest " + kind + " capacity " + cap + ": " + k.toString());
    }
    com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs = this.world.getChunkStore();
    com.hypixel.hytale.component.Ref cr = cs.getChunkReference(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(0, 0));
    com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk bc = (com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk) cs.getStore().getComponent(cr, com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk.getComponentType());
    int bad = 0;
    for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) if (bc.getTint(x, z) != %d) bad++;
    com.skyy.islandsprobe.ProbePlugin.log(this.tag + " tint: " + bad + " non-grass columns in chunk (0,0)");
  } catch (Throwable t) { com.skyy.islandsprobe.ProbePlugin.log(this.tag + " dump FAILED: " + t); }
  this.latch.countDown();
}""" % GRASS

PROBE_MAIN = r"""
public void run() {
  if (this.mode == 0) {
    if (STARTED) return;
    try {
      TRIES++;
      com.hypixel.hytale.server.core.universe.Universe u = com.hypixel.hytale.server.core.universe.Universe.get();
      com.hypixel.hytale.server.core.universe.world.World dw = u == null ? null : u.getDefaultWorld();
      java.util.Map b = (java.util.Map) System.getProperties().get("skyy.bridge");
      Object perm = b == null ? null : b.get("island:perm:fn");
      if (dw == null || perm == null || com.hypixel.hytale.builtin.instances.InstancesPlugin.get() == null) {
        if (TRIES > 120) { STARTED = true; com.skyy.islandsprobe.ProbePlugin.log("H0 gave up: no default world / SkyyIslands bridge after 240 s"); }
        return;
      }
      STARTED = true;
      new Thread(new com.skyy.islandsprobe.ProbeTask(1), "SkyyIslandsProbe").start();
    } catch (Throwable t) { STARTED = true; com.skyy.islandsprobe.ProbePlugin.log("H0 FAILED: " + t); }
    return;
  }
  try {
    com.hypixel.hytale.server.core.universe.world.World dw = com.hypixel.hytale.server.core.universe.Universe.get().getDefaultWorld();
    java.util.Map b = (java.util.Map) System.getProperties().get("skyy.bridge");
    ClassLoader cl = b.get("island:perm:fn").getClass().getClassLoader();
    String key = "%s";
    Object fn = Class.forName("com.skyy.islands.IslandBuild", true, cl).getConstructor(new Class[] { String.class }).newInstance(new Object[] { key });
    com.skyy.islandsprobe.ProbePlugin.log("H1 making island " + key + " the /island way (spawnInstance SkyyIsland -> IslandBuild) from " + dw.getName());
    java.util.concurrent.CompletableFuture f = com.hypixel.hytale.builtin.instances.InstancesPlugin.get().spawnInstance("SkyyIsland", "skyy-island-" + key, dw, new com.hypixel.hytale.math.vector.Transform(0.0, 128.0, 0.0));
    f = f.thenCompose((java.util.function.Function) fn);
    com.hypixel.hytale.server.core.universe.world.World w = (com.hypixel.hytale.server.core.universe.world.World) f.get(180L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islandsprobe.ProbePlugin.log("H1 IslandBuild finished: " + w.getName() + " alive " + w.isAlive());
    Thread.sleep(7000L);
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H2", 0);
    java.util.concurrent.CompletableFuture f2 = (java.util.concurrent.CompletableFuture) Class.forName("com.skyy.islands.ChunkFill", true, cl).getMethod("load", new Class[] { com.hypixel.hytale.server.core.universe.world.World.class }).invoke(null, new Object[] { w });
    Object r2 = f2.get(60L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islandsprobe.ProbePlugin.log("H3 second ChunkFill.load completed: " + (r2 == w));
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H3", 0);
    com.skyy.islandsprobe.DumpTask sv = com.skyy.islandsprobe.DumpTask.on(w, cl, "H7", 3);
    if (sv.fut != null) sv.fut.get(120L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islandsprobe.ProbePlugin.log("H7 save finished");
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H7", 4);
    Thread.sleep(1000L);
    com.hypixel.hytale.server.core.universe.world.storage.ChunkStore cs7 = w.getChunkStore();
    cs7.getChunkReferenceAsync(com.hypixel.hytale.math.util.ChunkUtil.indexChunk(0, 0)).get(60L, java.util.concurrent.TimeUnit.SECONDS);
    cs7.getChunkSectionReferenceAsync(0, 3, 0).get(60L, java.util.concurrent.TimeUnit.SECONDS);
    cs7.getChunkSectionReferenceAsync(0, 4, 0).get(60L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islandsprobe.ProbePlugin.log("H7 chunk (0,0) + island sections loaded again from the save (no SkyyIslands fill call)");
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H7", 0);
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H4", 1);
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H6", 2);
    Thread.sleep(3000L);
    com.skyy.islandsprobe.DumpTask.on(w, cl, "H6", 0);
    com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider sp = dw.getWorldConfig().getSpawnProvider();
    java.util.concurrent.CompletableFuture sf = sp.getSpawnPointAsync(dw, java.util.UUID.randomUUID());
    boolean d0 = sf.isDone();
    Object t = sf.get(60L, java.util.concurrent.TimeUnit.SECONDS);
    com.skyy.islandsprobe.ProbePlugin.log("H5 default world " + dw.getName() + " spawn provider " + sp.getClass().getSimpleName() + " answered " + (d0 ? "at once" : "later") + ": " + (t instanceof com.hypixel.hytale.math.vector.Transform ? String.valueOf(((com.hypixel.hytale.math.vector.Transform) t).getPosition()) : String.valueOf(t)));
    com.skyy.islandsprobe.ProbePlugin.log("DONE");
  } catch (Throwable t) { com.skyy.islandsprobe.ProbePlugin.log("PROBE FAILED: " + t); }
}"""
PROBE_KEY = "00000000-0000-4000-8000-0000000a0056"


def build_probe(out_dir):
    """javassist build of the scratch-only probe jar (separate process: python <this> --probe-build <dir>)"""
    import skyybuild as B
    J = B.start()
    pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
    P = "com.skyy.islandsprobe."
    cls_dir = os.path.join(out_dir, "probe_classes")
    shutil.rmtree(cls_dir, ignore_errors=True)
    os.makedirs(cls_dir)
    pl = pool.makeClass(P + "ProbePlugin", pool.get("com.hypixel.hytale.server.core.plugin.JavaPlugin"))
    pt = pool.makeClass(P + "ProbeTask")
    dt = pool.makeClass(P + "DumpTask")
    for f in PROBE_SRC["plugin_fields"]:
        pl.addField(CtField.make(f, pl))
    pl.addConstructor(CtNewConstructor.make("public ProbePlugin(com.hypixel.hytale.server.core.plugin.JavaPluginInit init) { super(init); }", pl))
    pl.addMethod(CtNewMethod.make(PROBE_SRC["log"], pl))
    dt.addInterface(pool.get("java.lang.Runnable"))
    for f in ("public com.hypixel.hytale.server.core.universe.world.World world;", "public ClassLoader cl;", "public String tag;",
              "public int mode;", "public java.util.concurrent.CompletableFuture fut;", "public java.util.concurrent.CountDownLatch latch = new java.util.concurrent.CountDownLatch(1);"):
        dt.addField(CtField.make(f, dt))
    dt.addConstructor(CtNewConstructor.make("public DumpTask(com.hypixel.hytale.server.core.universe.world.World w, ClassLoader c, String t, int m) { this.world = w; this.cl = c; this.tag = t; this.mode = m; }", dt))
    dt.addMethod(CtNewMethod.make(DUMP_RUN, dt))
    dt.addMethod(CtNewMethod.make(r"""
public static com.skyy.islandsprobe.DumpTask on(com.hypixel.hytale.server.core.universe.world.World w, ClassLoader c, String tag, int mode) throws Exception {
  com.skyy.islandsprobe.DumpTask d = new com.skyy.islandsprobe.DumpTask(w, c, tag, mode);
  w.execute(d);
  if (!d.latch.await(60L, java.util.concurrent.TimeUnit.SECONDS)) com.skyy.islandsprobe.ProbePlugin.log(tag + " world thread did not run the dump in 60 s");
  return d;
}""", dt))
    pt.addInterface(pool.get("java.lang.Runnable"))
    for f in ("public static volatile boolean STARTED = false;", "public static int TRIES = 0;", "public int mode;"):
        pt.addField(CtField.make(f, pt))
    pt.addConstructor(CtNewConstructor.make("public ProbeTask(int m) { this.mode = m; }", pt))
    pt.addMethod(CtNewMethod.make(PROBE_MAIN % PROBE_KEY, pt))
    pl.addMethod(CtNewMethod.make(PROBE_SRC["setup"], pl))
    for c in (pl, dt, pt):
        c.writeFile(cls_dir)
    jar = os.path.join(out_dir, "%s-%s.jar" % (PROBE_NAME, PROBE_VER))
    m = B.manifest(PROBE_NAME, PROBE_VER, "Scratch-only engine probe for SkyyIslands %s (harness; never deployed)." % VERSION,
                   P + "ProbePlugin")
    m["IncludesAssetPack"] = False
    B.assemble(jar, m, cls_dir)
    print("probe built:", jar)


# ================================================================================================ part 1: the bare JVM
def run_jvm():
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    import skyybuild as B
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    Modifier = JClass("java.lang.reflect.Modifier")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")

    def loader(jar):
        urls = JArray(URL)(1)
        urls[0] = File(jar).toURI().toURL()
        return URLCL(urls, sysl)

    L = {"old": loader(OLD), "new": loader(JAR)}
    CB = {"old": classes(OLD), "new": classes(JAR)}
    cnt = {}

    # ---------------- A
    for k in ("old", "new"):
        for n in sorted(CB[k]):
            try:
                Cls.forName(n, True, L[k])
                OKS[0] += 1
                cnt[k] = cnt.get(k, 0) + 1
            except Exception as e:
                check(False, "A. %s: load %s: %s" % (k, n, e))
    print("A. loaded + verified + initialised on the 0.7 jar: %s %d, %s %d classes (-Xverify:all)" % (OLD_VERSION, cnt.get("old", 0), VERSION, cnt.get("new", 0)))

    # ---------------- B
    old, new = CB["old"], CB["new"]
    page_c, plug_c = PKG + "IslandMenuPage", PKG + "SkyyIslandsPlugin"
    check(sorted(set(old) - set(new)) == [] and sorted(set(new) - set(old)) == [PKG + "HubSpawn"],
          "B. the same classes + HubSpawn: gone %s, new %s" % (sorted(set(old) - set(new)), sorted(set(new) - set(old))))
    W_ = "Lcom/hypixel/hytale/server/core/universe/world/World;"
    WC_ = "Lcom/hypixel/hytale/server/core/universe/world/chunk/WorldChunk;"
    CF_ = "Ljava/util/concurrent/CompletableFuture;"
    REF_ = "Lcom/hypixel/hytale/component/Ref;"
    # class -> (gone methods, new methods, changed methods) by name + descriptor; every other method byte-identical
    EXPECT = {
        "TintFix": ({"tintChunk(%s)I" % WC_, "resend(%s%s)V" % (W_, WC_)}, {"tintChunk(%sJ)I" % W_, "resend(%sJ)V" % W_}, {"fix(%s)I" % W_}),
        "FillTask": ({"<init>(%s%s%s)V" % (W_, WC_, CF_), "starterKit(%s%s)I" % (W_, WC_)},
                     {"<init>(%s%s)V" % (W_, CF_), "starterKit(%s)I" % W_, "section(%sIII)%s" % (W_, REF_), "blockAt(%sIII)I" % W_,
                      "blockEntity(%sIII)%s" % (W_, REF_), "blockHolder(%sIII)Lcom/hypixel/hytale/component/Holder;" % W_,
                      "accept(Ljava/lang/Object;Ljava/lang/Object;)V"},
                     {"put(IIILjava/lang/String;)I", "run()V"}),
        "ChunkFill": ({"<init>(%s)V" % W_, "apply(Ljava/lang/Object;)Ljava/lang/Object;"}, {"<init>()V", "load(%s)%s" % (W_, CF_)}, set()),
        "RelightNow": (set(), set(), {"run()V"}),
        "HubCmd": (set(), set(), {"sendToHub(Lcom/hypixel/hytale/component/Store;%sLcom/hypixel/hytale/server/core/universe/PlayerRef;%s)Z" % (REF_, W_)}),
        "IslandBuild": (set(), set(), {"apply(Ljava/lang/Object;)Ljava/lang/Object;"}),
    }
    vonly, changed_cls, ident = [], [], 0
    for n in sorted(old):
        if n == plug_c or n not in new:
            continue
        if old[n] == new[n]:
            ident += 1
            OKS[0] += 1
        elif version_only(old[n], new[n]):
            vonly.append(n.split(".")[-1])
            OKS[0] += 1
        else:
            changed_cls.append(n.split(".")[-1])
    check(sorted(changed_cls) == sorted(EXPECT), "B. the changed classes are exactly %s: %s" % (sorted(EXPECT), sorted(changed_cls)))
    check(old[page_c] == new[page_c], "B. IslandMenuPage is byte-identical to %s" % OLD_VERSION)
    uo, _ro = cp_split(old[plug_c])
    un, _rn = cp_split(new[plug_c])
    ready_old = [e for e in uo if ("] %s ready" % OLD_VERSION).encode() in e[2]]
    ready_new = [e for e in un if ("] %s ready" % VERSION).encode() in e[2]]
    if check(len(ready_old) == 1 and len(ready_new) == 1, "B. one ready-log constant in each SkyyIslandsPlugin"):
        s0, e0, t0 = ready_old[0]
        s1, e1, t1 = ready_new[0]
        swapped = new[plug_c][:s1] + old[plug_c][s0:e0] + new[plug_c][e1:]
        check(swapped == old[plug_c], "B. SkyyIslandsPlugin = %s's bytes once the ready-log constant is swapped back (setup unchanged)" % OLD_VERSION)
        a_, b_ = t0.decode("utf8"), t1.decode("utf8")
        a_n = re.sub(r"skyyui \S+ [0-9a-f]{12}", "KIT", a_.replace("] %s ready" % OLD_VERSION, "] %s ready" % VERSION))
        check(a_n == re.sub(r"skyyui \S+ [0-9a-f]{12}", "KIT", b_), "B. the ready constant only changes its version (and the kit id): %r" % b_[:120])
    CP = JClass("javassist.ClassPool")
    BAIS = JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def ct(bb):
        return CP(False).makeClass(BAIS(bb))

    def code_of(m):
        mi = m.getMethodInfo()
        ca = mi.getCodeAttribute()
        cp = mi.getConstPool()
        if ca is None:
            return ["<no code>"]
        it, out = ca.iterator(), []
        while it.hasNext():
            pos = it.next()
            ln = re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cp))).replace("ldc_w ", "ldc ")
            out.append(re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln))
        et = ca.getExceptionTable()
        for i in range(et.size()):
            ctp = et.catchType(i)
            out.append("try %s" % (cp.getClassInfo(ctp) if ctp else "any"))
        return out

    def methods(c):
        out = {}
        for m in list(c.getDeclaredMethods()) + list(c.getDeclaredConstructors()):
            out[str(m.getMethodInfo().getName()) + str(m.getSignature())] = code_of(m)
        ci = c.getClassInitializer()
        if ci is not None:
            out["<clinit>()V"] = code_of(ci)
        return out

    det = []
    for cn, (g_want, a_want, c_want) in sorted(EXPECT.items()):
        co, cnw = ct(old[PKG + cn]), ct(new[PKG + cn])
        mo, mn = methods(co), methods(cnw)
        gone = set(k for k in mo if k not in mn)
        added = set(k for k in mn if k not in mo)
        changed = set(k for k in mo if k in mn and mo[k] != mn[k])
        check(gone == g_want, "B. %s gone: %s (want %s)" % (cn, sorted(gone), sorted(g_want)))
        check(added == a_want, "B. %s new: %s (want %s)" % (cn, sorted(added), sorted(a_want)))
        check(changed == c_want, "B. %s changed: %s (want %s)" % (cn, sorted(changed), sorted(c_want)))
        fo = sorted((str(f.getName()), str(f.getSignature())) for f in co.getDeclaredFields())
        fn_ = sorted((str(f.getName()), str(f.getSignature())) for f in cnw.getDeclaredFields())
        want_f = {"FillTask": [("chunk", WC_)], "ChunkFill": [("world", W_)]}.get(cn, [])
        check(sorted(set(fo) - set(fn_)) == sorted(want_f) and not (set(fn_) - set(fo)), "B. %s fields: gone %s, new %s"
              % (cn, sorted(set(fo) - set(fn_)), sorted(set(fn_) - set(fo))))
        io_ = sorted(str(x) for x in co.getClassFile().getInterfaces())
        in_ = sorted(str(x) for x in cnw.getClassFile().getInterfaces())
        want_i = {"FillTask": io_ + ["java.util.function.BiConsumer"], "ChunkFill": []}.get(cn, io_)
        check(in_ == sorted(want_i), "B. %s interfaces %s (want %s)" % (cn, in_, sorted(want_i)))
        det.append("%s -%d +%d ~%d" % (cn, len(gone), len(added), len(changed)))
    # FillTask.starterKit: the kit code after the chest lookup is 0.5.5's (only the entity lookup + the method signature changed)
    sk_o = [v for k, v in methods(ct(old[PKG + "FillTask"])).items() if k.startswith("starterKit(")][0]
    sk_n = [v for k, v in methods(ct(new[PKG + "FillTask"])).items() if k.startswith("starterKit(")][0]
    # local variable slots shift by one (0.5.5 had the chunk parameter): compare with the slot numbers taken out
    loc = lambda x: re.sub(r"^(\w*(?:load|store))(?:_\d| \d+)$", r"\1 L", re.sub(r"^iinc \d+", "iinc L", x))
    cut = lambda c: [loc(x) for x in c[next(i for i, x in enumerate(c) if "starter kit: chest has no ItemContainerBlock in " in x) - 6:]]
    check(cut(sk_o) == cut(sk_n), "B. FillTask.starterKit: everything from the ItemContainerBlock check on is %s's" % OLD_VERSION)
    hs = ct(new[PKG + "HubSpawn"])
    check(sorted(str(x) for x in hs.getClassFile().getInterfaces()) == ["java.lang.Runnable", "java.util.function.BiConsumer"] and
          sorted(str(m.getName()) for m in hs.getDeclaredMethods()) == ["accept", "run"],
          "B. HubSpawn = Runnable + BiConsumer with run / accept")
    print("B. %d classes byte-identical (IslandMenuPage included), %d version-string only (%s), SkyyIslandsPlugin = %s but its ready "
          "constant, + HubSpawn; changed exactly as planned: %s" % (ident, len(vonly), ", ".join(vonly), OLD_VERSION, "; ".join(det)))

    # ---------------- C. engine-access audit (javassist over the 0.7 jar + the JDK) and the override audit
    ap = CP(True)
    ap.appendClassPath(B.SERVER_JAR)
    ap.appendClassPath(JAR)
    CPool = JClass("javassist.bytecode.ConstPool")

    def supers(c):
        seen, todo, out = set(), [c], []
        while todo:
            x = todo.pop(0)
            nm = str(x.getName())
            if nm in seen:
                continue
            seen.add(nm)
            out.append(x)
            try:
                s = x.getSuperclass()
                if s is not None:
                    todo.append(s)
            except Exception:
                pass
            try:
                todo.extend(list(x.getInterfaces()))
            except Exception:
                pass
        return out

    def has_method(cn, name, desc):
        try:
            c = ap.get(cn)
        except Exception:
            return False
        for x in supers(c):
            for m in x.getDeclaredMethods():
                if str(m.getName()) == name and str(m.getSignature()) == desc:
                    return True
            if name == "<init>":
                for m in x.getDeclaredConstructors():
                    if str(m.getSignature()) == desc:
                        return True
                return False
        return False

    def has_field(cn, name, desc):
        try:
            c = ap.get(cn)
        except Exception:
            return False
        for x in supers(c):
            for f in x.getDeclaredFields():
                if str(f.getName()) == name and str(f.getFieldInfo2().getDescriptor()) == desc:
                    return True
        return False

    def audit(bytes_map):
        miss, refs = [], 0
        for n, bb in sorted(bytes_map.items()):
            c = ct(bb)
            cp = c.getClassFile().getConstPool()
            for i in range(1, cp.getSize()):
                try:
                    tag = cp.getTag(i)
                except Exception:
                    continue
                if tag in (CPool.CONST_Methodref, CPool.CONST_InterfaceMethodref):
                    owner = str(cp.getMethodrefClassName(i)) if tag == CPool.CONST_Methodref else str(cp.getInterfaceMethodrefClassName(i))
                    nm = str(cp.getMethodrefName(i)) if tag == CPool.CONST_Methodref else str(cp.getInterfaceMethodrefName(i))
                    ds = str(cp.getMethodrefType(i)) if tag == CPool.CONST_Methodref else str(cp.getInterfaceMethodrefType(i))
                    if owner.startswith("com.skyy.") or owner.startswith("["):
                        continue
                    refs += 1
                    if not has_method(owner, nm, ds):
                        miss.append("%s -> %s.%s%s" % (n.split(".")[-1], owner.replace("com.hypixel.hytale.server.core.", ""), nm, ds))
                elif tag == CPool.CONST_Fieldref:
                    owner, nm, ds = str(cp.getFieldrefClassName(i)), str(cp.getFieldrefName(i)), str(cp.getFieldrefType(i))
                    if owner.startswith("com.skyy."):
                        continue
                    refs += 1
                    if not has_field(owner, nm, ds):
                        miss.append("%s -> field %s.%s %s" % (n.split(".")[-1], owner, nm, ds))
        return miss, refs

    miss_n, refs_n = audit(new)
    miss_o, refs_o = audit(old)
    check(not miss_n, "C. every engine / JDK reference of %s resolves on the 0.7 jar (%d refs): %s" % (VERSION, refs_n, miss_n[:6]))
    known = ["getBlockComponentEntity", "setBlock(IIILjava/lang/String;)", "getBlock(III)", ".getSpawnPoint(", "getChunkAsync", "invalidateLightInChunk(",
             "getChunkIfLoaded", "getBlockChunk"]
    check(all(any(k in m for m in miss_o) for k in known) and len(miss_o) >= 9,
          "C. control: %s misses the known 0.7 removals (%d): %s" % (OLD_VERSION, len(miss_o), miss_o[:12]))
    # override audit: concrete classes with an engine supertype implement every abstract method; no lost override
    lost, open_abs, ov = [], [], 0
    for n in sorted(new):
        jc = Cls.forName(n, False, L["new"])
        if not Modifier.isAbstract(jc.getModifiers()) and not jc.isInterface():
            for m in jc.getMethods():
                if Modifier.isAbstract(m.getModifiers()):
                    open_abs.append("%s.%s" % (n.split(".")[-1], m.getName()))
        c = ct(new[n])
        eng = supers(ap.get(str(c.getClassFile().getSuperclass()))) if str(c.getClassFile().getSuperclass()) != "java.lang.Object" else []
        for i_ in c.getClassFile().getInterfaces():
            try:
                eng.extend(supers(ap.get(str(i_))))
            except Exception:
                pass
        eng = [x for x in eng if str(x.getName()).startswith("com.hypixel.")]
        if not eng:
            continue
        eng_m = {}
        for x in eng:
            for m in x.getDeclaredMethods():
                if not JClass("javassist.Modifier").isStatic(m.getModifiers()) and not JClass("javassist.Modifier").isPrivate(m.getModifiers()):
                    eng_m.setdefault(str(m.getName()), set()).add(str(m.getSignature()))
        for m in c.getDeclaredMethods():
            nm, sg = str(m.getName()), str(m.getSignature())
            if JClass("javassist.Modifier").isStatic(m.getModifiers()) or nm not in eng_m:
                continue
            ov += 1
            if sg not in eng_m[nm]:
                lost.append("%s.%s%s (engine has %s)" % (n.split(".")[-1], nm, sg, sorted(eng_m[nm])[:2]))
    check(not open_abs, "C. no concrete %s class leaves an abstract method open: %s" % (VERSION, open_abs[:6]))
    check(not lost, "C. no %s method shadows an engine method with another descriptor (a lost override): %s" % (VERSION, lost[:6]))
    print("C. engine-access audit on the 0.7 jar: %s %d references, 0 missing; %s misses %d (the known removals: %s); %d engine overrides "
          "matched, 0 open abstract methods" % (VERSION, refs_n, OLD_VERSION, len(miss_o), ", ".join(sorted(set(re.sub(r"^\w+ -> ", "", m).split("(")[0].split(".")[-1] for m in miss_o))), ov))

    # ---------------- D. the new paths on engine objects
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

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

    def setf(o, c, n, v):
        jf(c, n).set(o, v)

    # the asset stores registered (not loaded) the way the server does it first: WorldConfig's class init reads GameplayConfig's store
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JClass("java.lang.String"))(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    setf_ =lambda o, c, n, v: jf(c, n).set(o, v)
    setf_(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    setf_(hs, HS, "shutdown", JClass("java.util.concurrent.atomic.AtomicReference")())
    setf_(None, HS, "instance", hs)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    UUID, Integer = JClass("java.util.UUID"), JClass("java.lang.Integer")
    CHM, COWAL, CLDeque = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.concurrent.CopyOnWriteArrayList"), JClass("java.util.concurrent.ConcurrentLinkedDeque")
    AtomicBoolean = JClass("java.util.concurrent.atomic.AtomicBoolean")
    CF = JClass("java.util.concurrent.CompletableFuture")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe = JClass("com.hypixel.hytale.server.core.universe.Universe")
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    WCFG = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
    Holder = JClass("com.hypixel.hytale.component.Holder")
    Ref_ = JClass("com.hypixel.hytale.component.Ref")
    Store_ = JClass("com.hypixel.hytale.component.Store")
    EntStore = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EntMod = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    CompType = JClass("com.hypixel.hytale.component.ComponentType")
    TRF = JClass("com.hypixel.hytale.math.vector.Transform")
    GSP = JClass("com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider")
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    HSC = JClass("com.hypixel.hytale.server.core.HytaleServerConfig")
    HSCD = JClass("com.hypixel.hytale.server.core.HytaleServerConfig$Defaults")
    CSc = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore")
    CGc = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkGrid")
    # log capture (IslandStore.LOG = a real HytaleLogger; the backend's subscribers see every record)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = COWAL()
    HLB.subscribe(CAPLOG)
    LOGGER = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslandsHarness")

    def logs(start=0):
        out = []
        for r in list(CAPLOG)[start:]:
            try:
                out.append((str(r.getLevel()), str(r.getMessage())))
            except Exception as e:
                out.append(("?", str(e)))
        return out

    # fakes (javassist into the scratch folder)
    fdir = os.path.join(SCRATCH, "fakes")
    os.makedirs(fdir, exist_ok=True)
    jcp = CP(True)
    jcp.appendClassPath(B.SERVER_JAR)
    CtF_, CtM_ = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")

    def fake(name, sup, fields, meths, iface=None):
        c = jcp.makeClass("skyyfake." + name, jcp.get(sup)) if sup else jcp.makeClass("skyyfake." + name)
        if iface:
            c.addInterface(jcp.get(iface))
        if sup:
            k0 = JClass("javassist.CtNewConstructor").defaultConstructor(c)
            c.addConstructor(k0)
            c.removeConstructor(k0)
        for f in fields:
            c.addField(CtF_.make(f, c))
        for m in meths:
            c.addMethod(CtM_.make(m, c))
        c.writeFile(fdir)

    fake("ChatCap", "com.hypixel.hytale.server.core.io.PacketHandler",
         ["public static java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();"],
         ["public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { Q.add(p); }"])
    fake("FakeStore", "com.hypixel.hytale.component.Store",
         ["public static java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();",
          "public static volatile Thread T;"],
         ["public void addComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) { Q.add(new Object[] { r, c, Thread.currentThread() }); }"])
    fake("FakeLight", "com.hypixel.hytale.server.core.universe.world.lighting.ChunkLightingManager",
         ["public static java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();"],
         ["public boolean invalidateLightInChunkSections(com.hypixel.hytale.server.core.universe.world.storage.ChunkGrid g, int cx, int cz, int a, int b) { Q.add(new Object[] { g, new int[] { cx, cz, a, b } }); return true; }"])
    ISP = "com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider"
    sp_meths = []
    for m in jcp.get(ISP).getDeclaredMethods():
        if JClass("javassist.Modifier").isAbstract(m.getModifiers()):
            rt = str(m.getReturnType().getName())
            ps = ", ".join("%s a%d" % (str(p.getName()), i) for i, p in enumerate(m.getParameterTypes()))
            if str(m.getName()) == "getSpawnPointAsync":
                body = "{ CALLS++; return F; }"
            elif rt == "boolean":
                body = "{ return false; }"
            elif rt in ("int", "long", "double", "float", "short", "byte", "char"):
                body = "{ return 0; }"
            elif rt == "void":
                body = "{ }"
            else:
                body = "{ return null; }"
            sp_meths.append("public %s %s(%s) %s" % (rt, m.getName(), ps, body))
    fake("LateSpawn", None, ["public static volatile java.util.concurrent.CompletableFuture F;", "public static volatile int CALLS = 0;"],
         sp_meths, iface=ISP)
    ld = jcp.get("skyyfake.LateSpawn")
    FL = loader(fdir)
    ChatCap, FakeStore, FakeLight, LateSpawn = [Cls.forName("skyyfake." + n, True, FL) for n in ("ChatCap", "FakeStore", "FakeLight", "LateSpawn")]
    CHATQ, TPQ, LIGHTQ = ChatCap.getField("Q").get(None), FakeStore.getField("Q").get(None), FakeLight.getField("Q").get(None)

    # the server: HytaleServer (config -> default world "default"), Universe (worlds), EntityModule (teleport type)
    hcfg = U.allocateInstance(HSC.class_)
    hdef = U.allocateInstance(HSCD.class_)
    setf(hdef, HSCD, "world", "default")
    setf(hcfg, HSC, "defaults", hdef)
    setf(hs, HS, "hytaleServerConfig", hcfg)
    uni = U.allocateInstance(Universe.class_)
    WORLDS = CHM()
    setf(uni, Universe, "worlds", WORLDS)
    setf(uni, Universe, "playersByUuid", CHM())
    setf(None, Universe, "instance", uni)
    em = U.allocateInstance(EntMod.class_)
    TP_TYPE = U.allocateInstance(CompType.class_)
    setf(em, EntMod, "teleportComponentType", TP_TYPE)
    setf(None, EntMod, "instance", em)
    FSTORE = U.allocateInstance(FakeStore)
    ESTORE = U.allocateInstance(EntStore.class_)
    setf(FSTORE, Store_, "externalData", ESTORE)
    holder = U.allocateInstance(Holder.class_)

    def mkworld(name, provider=None):
        w = U.allocateInstance(World.class_)
        setf(w, World, "alive", AtomicBoolean(True))
        setf(w, World, "acceptingTasks", AtomicBoolean(True))
        setf(w, World, "name", name)
        setf(w, World, "taskQueue", CLDeque())
        setf(w, World, "playerRefs", COWAL())
        wc = U.allocateInstance(WCFG.class_)
        if provider is not None:
            setf(wc, WCFG, "spawnProvider", provider)
        setf(w, World, "worldConfig", wc)
        WORLDS.put(name.lower(), w)
        return w

    def drain(w):
        dq = jf(World, "taskQueue").get(w)
        n = 0
        while not dq.isEmpty():
            dq.poll().run()
            n += 1
        return n

    def qlen(w):
        return int(jf(World, "taskQueue").get(w).size())

    def mkplayer(n):
        p = U.allocateInstance(PR.class_)
        setf(p, PR, "uuid", UUID(0x15a0, n))
        setf(p, PR, "username", "Player%d" % n)
        setf(p, PR, "holder", holder)
        setf(p, PR, "packetHandler", U.allocateInstance(ChatCap))
        r = U.allocateInstance(Ref_.class_)
        setf(r, Ref_, "index", Integer(1))
        setf(r, Ref_, "store", FSTORE)
        setf(p, PR, "entity", r)
        return p, r

    def texts(o, depth=0, seen=None):
        """every String reachable from a packet through its fields (the chat text sits in its FormattedMessage)"""
        seen = set() if seen is None else seen
        if o is None or depth > 4 or id(o) in seen:
            return []
        seen.add(id(o))
        if isinstance(o, str):
            return [o]
        out = []
        k = o.getClass()
        while k is not None and str(k.getName()).startswith("com.hypixel"):
            for f in k.getDeclaredFields():
                if JClass("java.lang.reflect.Modifier").isStatic(f.getModifiers()) or f.getType().isPrimitive():
                    continue
                f.setAccessible(True)
                v = f.get(o)
                if v is None:
                    continue
                if isinstance(v, str) or str(v.getClass().getName()) == "java.lang.String":
                    out.append(str(v))
                elif str(f.getType().getName()).startswith("com.hypixel"):
                    out.extend(texts(v, depth + 1, seen))
            k = k.getSuperclass()
        return out

    def chat():
        out = []
        while not CHATQ.isEmpty():
            pk = CHATQ.poll()
            try:
                out.append(" ".join(texts(pk)))
            except Exception as e:
                out.append("? %s" % e)
        return out

    def tps():
        out = []
        while not TPQ.isEmpty():
            out.append(TPQ.poll())
        return out

    J = lambda k, n: Cls.forName(PKG + n, True, L[k])
    for k in ("old", "new"):
        J(k, "IslandStore").getField("LOG").set(None, LOGGER)
        J(k, "IslandStore").getField("HUB_WORLD").set(None, None)
    HubN = J("new", "HubCmd")
    sendN = HubN.getMethod("sendToHub", Store_.class_, Ref_.class_, PR.class_, World.class_)
    sendO = J("old", "HubCmd").getMethod("sendToHub", Store_.class_, Ref_.class_, PR.class_, World.class_)
    SPAWN = TRF(8.5, 129.0, 8.5, 0.0, 90.0, 0.0)
    dflt = mkworld("default", GSP(SPAWN))
    isl = mkworld("skyy-island-x")
    p1, r1 = mkplayer(1)

    def tp_of(e):
        """(ref, Teleport, thread) -> (target world name, x, y, z)"""
        t = e[1]
        tw = None
        for fn in ("world", "targetWorld"):
            try:
                tw = jf(t.getClass(), fn).get(t)
                break
            except Exception:
                pass
        pos = None
        for fn in ("position", "targetPosition"):
            try:
                pos = jf(t.getClass(), fn).get(t)
                break
            except Exception:
                pass
        return (str(tw.getName()) if tw is not None else None, round(float(pos.x()), 2) if pos is not None else None,
                round(float(pos.y()), 2) if pos is not None else None, round(float(pos.z()), 2) if pos is not None else None)

    # D1 Global provider: complete at once
    tps(), chat()
    n0 = len(CAPLOG)
    ok = bool(sendN.invoke(None, FSTORE, r1, p1, isl))
    got = tps()
    check(ok and len(got) == 1 and tp_of(got[0]) == ("default", 8.5, 129.0, 8.5) and got[0][0] == r1 and qlen(isl) == 0,
          "D1 /hub with no hub, Global spawn provider: sent at once in the same call (%s, %s, queued %d)" % (ok, [tp_of(g) for g in got], qlen(isl)))
    old_err = None
    try:
        sendO.invoke(None, FSTORE, r1, p1, isl)
    except Exception as e:
        old_err = str(e.getCause() if hasattr(e, "getCause") and e.getCause() is not None else e)
    check(old_err is not None and "NoSuchMethodError" in old_err and "getSpawnPoint" in old_err and not tps(),
          "D1 control: %s's sendToHub throws NoSuchMethodError getSpawnPoint on 0.7 (the bug): %s" % (OLD_VERSION, (old_err or "")[:160]))
    # D2 a late answer
    late = U.allocateInstance(LateSpawn)
    setf(dflt, World, "worldConfig", U.allocateInstance(WCFG.class_))
    setf(dflt.getWorldConfig(), WCFG, "spawnProvider", late)
    F = CF()
    LateSpawn.getField("F").set(None, F)
    t0 = time.time()
    ok = bool(sendN.invoke(None, FSTORE, r1, p1, isl))
    dt = time.time() - t0
    check(ok and dt < 0.5 and not F.isDone() and not tps() and qlen(isl) == 0 and int(LateSpawn.getField("CALLS").get(None)) == 1,
          "D2 a late spawn answer: sendToHub returns true at once (%.3f s) without waiting; no teleport yet, nothing queued" % dt)
    F.complete(TRF(1.5, 70.0, -3.5, 0.0, 0.0, 0.0))
    check(not tps() and qlen(isl) == 1, "D2 the answer arrives (off the world thread): nothing added there, HubSpawn queued on the player's world (%d)" % qlen(isl))
    drain(isl)
    got = tps()
    check(len(got) == 1 and tp_of(got[0]) == ("default", 1.5, 70.0, -3.5) and got[0][0] == r1,
          "D2 the world thread runs HubSpawn: the teleport to the late spawn point (%s)" % [tp_of(g) for g in got])
    # D3 a failed answer, D4 an empty one
    for tag, finish in (("D3 a failed answer", lambda f: f.completeExceptionally(JClass("java.lang.IllegalStateException")("probe"))),
                        ("D4 an empty answer", lambda f: f.complete(None))):
        F = CF()
        LateSpawn.getField("F").set(None, F)
        chat()
        n0 = len(CAPLOG)
        ok = bool(sendN.invoke(None, FSTORE, r1, p1, isl))
        finish(F)
        nq = qlen(isl)
        drain(isl)
        lines = chat()
        w_ = [m for lv, m in logs(n0) if "default world spawn point not found" in m]
        check(ok and nq == 0 and not tps() and len(lines) == 1 and "No hub is set" in lines[0] and len(w_) == 1,
              "%s: no teleport, the no-hub line (%s) + a warning (%s)" % (tag, lines, w_[:1]))
    # D5 the player left the world before the answer (the ref is no longer valid)
    F = CF()
    LateSpawn.getField("F").set(None, F)
    ok = bool(sendN.invoke(None, FSTORE, r1, p1, isl))
    setf(r1, Ref_, "index", Integer(-2147483648))
    F.complete(TRF(2.5, 71.0, 2.5, 0.0, 0.0, 0.0))
    drain(isl)
    check(ok and not tps(), "D5 the player changed world (ref invalid) before the answer: no teleport")
    setf(r1, Ref_, "index", Integer(1))
    # D6 the /sethub hub: identical to 0.5.5 (fixed point, the spawn provider is not asked)
    hubw = mkworld("hubworld")
    calls0 = int(LateSpawn.getField("CALLS").get(None))
    res = {}
    for k in ("old", "new"):
        S_ = J(k, "IslandStore")
        S_.getField("HUB_WORLD").set(None, "hubworld")
        hp = JArray(JClass("double"))([10.5, 80.0, -4.5])
        hr = JArray(JClass("float"))([0.0, 45.0, 0.0])
        S_.getField("HUB_POS").set(None, hp)
        S_.getField("HUB_ROT").set(None, hr)
        m_ = J(k, "HubCmd").getMethod("sendToHub", Store_.class_, Ref_.class_, PR.class_, World.class_)
        res[k] = (bool(m_.invoke(None, FSTORE, r1, p1, isl)), [tp_of(g) for g in tps()])
        S_.getField("HUB_WORLD").set(None, None)
    check(res["old"] == res["new"] == (True, [("hubworld", 10.5, 80.0, -4.5)]) and int(LateSpawn.getField("CALLS").get(None)) == calls0,
          "D6 the /sethub hub: %s = %s, the spawn provider not asked: %s" % (VERSION, OLD_VERSION, res))
    # D7 ChunkFill.load with no chunk store: the future still completes (the creation chain never hangs)
    nw = mkworld("skyy-island-d7")
    n0 = len(CAPLOG)
    fut = J("new", "ChunkFill").getMethod("load", World.class_).invoke(None, nw)
    check(fut.isDone() and fut.getNow(None) == nw and any("island fill dispatch failed" in m for _l, m in logs(n0)),
          "D7 ChunkFill.load without a chunk store: completed with the world + 'island fill dispatch failed' (%s)" % [m for _l, m in logs(n0)][:2])
    # a REAL ChunkStore (the engine class; its chunk / section maps empty = nothing loaded)
    cs = U.allocateInstance(CSc.class_)
    setf(cs, CGc, "lock", JClass("java.util.concurrent.locks.StampedLock")())
    setf(cs, CGc, "chunkSections", JClass("com.hypixel.hytale.math.data.Int3ObjectOpenHashMap")())
    setf(cs, CGc, "chunks", JClass("com.hypixel.fastutil.longs.Long2ObjectConcurrentHashMap")(True, jpype.JLong(0)))
    setf(nw, World, "chunkStore", cs)
    # D8 FillTask on unloaded sections
    FT = J("new", "FillTask")
    done = CF()
    task = FT.getConstructor(World.class_, CF.class_).newInstance(nw, done)
    n0 = len(CAPLOG)
    task.run()
    check(done.isDone() and done.getNow(None) == nw and any("chunk (0,0) did not load, island left empty" in m for _l, m in logs(n0))
          and not any("starter island placed" in m for _l, m in logs(n0)),
          "D8 FillTask with the island sections not loaded: 'chunk (0,0) did not load, island left empty', done completed, nothing placed")
    check(int(FT.getMethod("blockAt", World.class_, JClass("int"), JClass("int"), JClass("int")).invoke(None, nw, Integer(8), Integer(128), Integer(8))) == -1 and
          FT.getMethod("blockEntity", World.class_, JClass("int"), JClass("int"), JClass("int")).invoke(None, nw, Integer(4), Integer(129), Integer(4)) is None,
          "D8 blockAt = -1 and blockEntity = null on an unloaded section (the real ChunkStore lookup)")
    # D9 FillTask.accept with a load error: logged, the fill still queued on the world thread (and completes there)
    done = CF()
    task = FT.getConstructor(World.class_, CF.class_).newInstance(nw, done)
    n0 = len(CAPLOG)
    task.accept(None, JClass("java.lang.RuntimeException")("probe load error"))
    q9 = qlen(nw)
    d9 = done.isDone()
    drain(nw)
    check(q9 == 1 and not d9 and done.isDone() and any("island chunk load for skyy-island-d7 reported" in m for _l, m in logs(n0)),
          "D9 FillTask.accept with a load error: logged, the fill queued on the world thread (%d) and done there" % q9)
    # D10 TintFix.fix with no loaded chunk
    check(int(J("new", "TintFix").getMethod("fix", World.class_).invoke(None, nw)) == 0 and
          int(J("new", "TintFix").getMethod("tintChunk", World.class_, JClass("long")).invoke(None, nw, JClass("java.lang.Long")(0))) == 0,
          "D10 TintFix.fix / tintChunk with no loaded chunk: 0 columns, no error")
    # D11 RelightNow: the 0.7 relight call on the world's ChunkStore, 9 chunks
    fl = U.allocateInstance(FakeLight)
    setf(nw, World, "chunkLighting", fl)
    LIGHTQ.clear()
    n0 = len(CAPLOG)
    J("new", "RelightNow").getConstructor(World.class_).newInstance(nw).run()
    calls = []
    while not LIGHTQ.isEmpty():
        e = LIGHTQ.poll()
        calls.append((e[0] == cs, tuple(int(x) for x in e[1])))
    want = [(True, (cx, cz, 0, 10)) for cx in (-1, 0, 1) for cz in (-1, 0, 1)]
    check(calls == want and any("relight queued for skyy-island-d7 (9/9 chunks)" in m for _l, m in logs(n0)),
          "D11 RelightNow: invalidateLightInChunkSections(the world's ChunkStore, cx, cz, 0, 10) for the 9 chunks + '9/9 chunks' (%s)" % calls[:3])
    print("D. the new paths on engine objects: /hub on the real Global provider (sent at once; %s throws NoSuchMethodError), a late answer "
          "(no wait, queued on the player's world, teleport there), failed / empty answer (no-hub line + warning), player gone, the /sethub "
          "hub = %s; ChunkFill.load never hangs; FillTask on unloaded sections; accept with a load error; TintFix with nothing loaded; "
          "RelightNow 9 x invalidateLightInChunkSections(.., 0, 10)" % (OLD_VERSION, OLD_VERSION))

    # ---------------- E. start twice on a scratch copy of the live data
    saves = os.path.join(B.HYTALE, "UserData", "Saves")
    live = arg("--live")
    if not live:
        try:
            import deploy_set as D_
            cand = os.path.join(saves, D_.WORLD, "mods")
            if os.path.isdir(os.path.join(cand, "Skyy_SkyyIslands")):
                live = cand
        except Exception:
            pass
    if not check(bool(live) and os.path.isdir(os.path.join(live, "Skyy_SkyyIslands")), "E. live Skyy_SkyyIslands data found (%s)" % live):
        return
    eroot = os.path.join(SCRATCH, "E")
    shutil.rmtree(eroot, ignore_errors=True)
    shutil.copytree(os.path.join(live, "Skyy_SkyyIslands"), os.path.join(eroot, "Skyy_SkyyIslands"))
    base = os.path.join(eroot, "Skyy_SkyyIslands")
    um, _r = cp_split(new[plug_c])
    animals = max((t.decode("utf8") for _a, _b, t in um if re.match(rb"^[A-Za-z0-9_]+(,[A-Za-z0-9_]+){5,}$", t)), key=len, default="")
    Paths = JClass("java.nio.file.Paths")
    BR = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", BR)
    S0 = snap(eroot)
    notes = []
    for rnd in range(2):
        S_ = J("new", "IslandStore")
        C_ = J("new", "IslandCfg")
        S_.getField("DIR").set(None, Paths.get(os.path.join(base, "islands")))
        C_.getField("FILE").set(None, Paths.get(os.path.join(base, "config.properties")))
        C_.getMethod("load", JClass("java.lang.String")).invoke(None, animals)
        S_.getField("HUB_FILE").set(None, Paths.get(os.path.join(base, "hub.properties")))
        S_.getMethod("loadHub").invoke(None)
        S_.getMethod("loadIslandWorlds").invoke(None)
        mig = C_.getMethod("plan053").invoke(None)
        J("new", "CfgPub").getMethod("start", JClass("java.nio.file.Path"), JClass("com.hypixel.hytale.logger.HytaleLogger")).invoke(None, Paths.get(eroot), LOGGER)
        a53 = J("new", "IslandHooks").getMethod("apply053", JClass("int")).invoke(None, mig)
        J("new", "CfgPub").getMethod("shutdown").invoke(None)
        notes.append((int(mig), str(a53)[:60], int(S_.getField("ISLAND_WORLDS").get(None).size()), str(S_.getField("HUB_WORLD").get(None))))
        S1 = snap(eroot)
        chg = sorted(k for k in set(S0) | set(S1) if S0.get(k) != S1.get(k))
        check(not chg, "E. start %d on the live copy: no file written (%d files): %s" % (rnd + 1, len(S0), chg[:4]))
    print("E. two starts on a copy of the live Skyy_SkyyIslands data (%d files, %s): nothing written; %s" % (len(S0), live, notes[-1]))
    NOTES.append("E live copy %d files, island worlds %d, hub %s" % (len(S0), notes[-1][2], notes[-1][3]))


# ================================================================================================ part 2: the real server (S)
def run_server():
    pdir = os.path.join(SCRATCH, "probe")
    os.makedirs(pdir, exist_ok=True)
    env = dict(os.environ)
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--probe-build", pdir, "--dir", SCRATCH], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    pjar = os.path.join(pdir, "%s-%s.jar" % (PROBE_NAME, PROBE_VER))
    if not check(r.returncode == 0 and os.path.isfile(pjar), "S. probe jar built: %s" % (r.stdout[-400:] + r.stderr[-800:])):
        return
    smoke_dir = os.path.join(TOOLS, "dev", "scratch", "smoke")
    before = set(glob.glob(os.path.join(smoke_dir, "*.log")))
    print("S. starting the real 0.7 server through tools/smoke_test.py (about 1-3 minutes) ...", flush=True)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "smoke_test.py"), "--jar", JAR, "--jar", pjar, "--linger", "75"],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    if r.returncode == 2:
        check(False, "S. smoke test NOT RUN: %s" % out[-600:])
        return
    new_logs = sorted(set(glob.glob(os.path.join(smoke_dir, "*.log"))) - before)
    if not check(bool(new_logs), "S. the smoke log was written"):
        return
    lines = open(new_logs[-1], encoding="utf-8", errors="replace").read().splitlines()
    NOTES.append("S smoke exit %d, log %s" % (r.returncode, os.path.relpath(new_logs[-1], ROOT)))
    verdict = [ln for ln in out.splitlines() if ln.startswith("smoke:") or "PASS" in ln or "FAIL" in ln][-6:]
    text = "\n".join(lines)
    check(re.search(r"\[SkyyIslands\] %s ready\b" % re.escape(VERSION), text) is not None, "S. [SkyyIslands] %s ready in the real server log" % VERSION)
    check(re.search(r"\[%s\] %s ready\b" % (PROBE_NAME, re.escape(PROBE_VER)), text) is not None, "S. the probe loaded")
    bad = [ln for ln in lines if ("com.skyy.islands" in ln or "[SkyyIslands]" in ln) and re.search(r"SEVERE|Exception|Error:|NoSuchMethod", ln)]
    check(not bad, "S. no SkyyIslands SEVERE / exception line: %s" % bad[:4])
    P = [re.sub(r"^.*?\[%s\] " % PROBE_NAME, "", ln) for ln in lines if "[%s]" % PROBE_NAME in ln]
    I = [re.sub(r"^.*?\[SkyyIslands\] ", "", ln) for ln in lines if "[SkyyIslands]" in ln]
    for ln in P:
        if not ln.startswith(("H2 dump", "H3 dump", "H7 dump")):
            print("   probe:", ln[:240])
    check("DONE" in P and not any("FAILED" in ln or "gave up" in ln for ln in P), "S. the probe ran to the end: %s" % [ln for ln in P if "FAIL" in ln or "gave up" in ln][:3])
    wname = "skyy-island-" + PROBE_KEY
    check(any(ln.startswith("island world for %s = %s" % (PROBE_KEY, wname)) for ln in I), "S. IslandBuild: 'island world for <key> = %s'" % wname)
    placed = [ln for ln in I if ln.startswith("starter island placed in %s" % wname)]
    want = island_layout()
    m_ = re.search(r"\((\d+) blocks\)", placed[0]) if placed else None
    check(len(placed) == 1 and m_ and int(m_.group(1)) == len(want),
          "S. one 'starter island placed in %s (%d blocks)' line: %s" % (wname, len(want), placed))
    kit = [ln for ln in I if ln.startswith("starter kit placed in %s" % wname)]
    check(len(kit) == 1, "S. 'starter kit placed in %s' (%s)" % (wname, kit))
    rel = [ln for ln in I if ln.startswith("relight queued for %s" % wname)]
    check(bool(rel) and all(ln.endswith("(9/9 chunks)") or "(9/9 chunks)," in ln for ln in rel), "S. RelightTask ran on the real world, 9/9 chunks queued: %s" % rel)
    NOTES.append("S relight " + "; ".join(rel))

    def dump(tag):
        parts = sorted((int(m.group(1)), m.group(3)) for m in (re.match(r"%s dump (\d+)/(\d+) (.*)$" % tag, ln) for ln in P) if m)
        s = "".join(p for _i, p in parts)
        out = {}
        for it in s.split(";"):
            if "=" in it:
                k, v = it.split("=", 1)
                x, y, z = (int(a) for a in k.split(","))
                out[(x, y, z)] = v
        return out
    d2, d3 = dump("H2"), dump("H3")
    diff = sorted(set(want.items()) ^ set(d2.items()))
    check(d2 == want, "S. H2 every island block at its place = the %s FillTask layout (%d blocks): diff %s" % (OLD_VERSION, len(want), diff[:8]))
    check(d3 == d2, "S. H3 a second ChunkFill.load skips the built island (blocks unchanged)")
    check(len(placed) == 1, "S. H3 no second 'starter island placed' line")
    chest = [ln for ln in P if ln.startswith("H2 chest")]
    m_k = re.search(r"\((\d+) of (\d+) stacks", kit[0]) if kit else None
    items2 = chest[0].split(": ", 1)[1] if chest and ": " in chest[0] else ""
    check(bool(chest) and re.match(r"H2 chest (holder|entity) capacity \d+: ", chest[0]) is not None and m_k is not None and
          m_k.group(1) == m_k.group(2) and items2.count(";") == int(m_k.group(1)) > 0,
          "S. H2 the starter chest's ItemContainerBlock holds the whole kit (%s / %s)" % (chest, kit))
    # H7 (fixer 2026-10-13): the kit in the chest HOLDER survives a save + unload + reload (kitGiven is set at fill time)
    d7 = dump("H7")
    un7 = [ln for ln in P if ln.startswith("H7 chunk (0,0) unloaded")]
    check(bool(un7) and "was loaded true, loaded now false, chest section loaded now false" in un7[0] and "H7 save finished" in P,
          "S. H7 the island's chunks saved, then chunk (0,0) unloaded (sections gone): %s" % un7)
    check(d7 == want, "S. H7 reloaded from the save: every island block at its place (%d blocks): diff %s" % (len(want), sorted(set(want.items()) ^ set(d7.items()))[:8]))
    ch7 = [ln for ln in P if ln.startswith("H7 chest")]
    items7 = ch7[0].split(": ", 1)[1] if ch7 and ": " in ch7[0] else None
    check(bool(ch7) and re.match(r"H7 chest (holder|entity) capacity \d+: ", ch7[0]) is not None and items7 == items2,
          "S. H7 reloaded from the save: the starter chest still holds the whole kit (%s)" % ch7)
    check(len(placed) == 1 and len(kit) == 1, "S. H7 no second fill / kit after the reload")
    NOTES.append("S chest after save + unload + reload " + (ch7[0] if ch7 else "-"))
    sw = [ln for ln in P if ln.startswith("H6 section")]
    ch6 = [ln for ln in P if ln.startswith("H6 chest")]
    items6 = ch6[0].split(": ", 1)[1] if ch6 and ": " in ch6[0] else None
    check(bool(sw) and sw[0].endswith("(the engine's own switch: getChunkSectionReferenceAsync flag 4 = ticking, on the world thread - what /chunk load uses)") and " -> false" in sw[0] and
          bool(ch6) and ch6[0].startswith("H6 chest entity") and items6 == items2,
          "S. H6 the section starts ticking (as when a player comes near): the chest is an ENTITY with the same kit (%s | %s)" % (sw, ch6))
    NOTES.append("S chest after ticking " + (ch6[0] if ch6 else "-"))
    tint2 = [ln for ln in P if ln.startswith("H2 tint")]
    check(tint2 == ["H2 tint: 0 non-grass columns in chunk (0,0)"], "S. H2 chunk (0,0) is all grass tint: %s" % tint2)
    tf = [ln for ln in P if ln.startswith("H4 TintFix.fix")]
    t4 = [ln for ln in P if ln.startswith("H4 tint")]
    check(tf == ["H4 TintFix.fix after 3 columns were set wrong: 3 columns re-tinted"] and t4 == ["H4 tint: 0 non-grass columns in chunk (0,0)"],
          "S. H4 TintFix.fix on the real BlockChunk: 3 wrong columns re-tinted, all grass again: %s %s" % (tf, t4))
    sp = [ln for ln in P if ln.startswith("H5 ")]
    check(bool(sp) and "answered" in sp[0], "S. H5 the default world's spawn point through getSpawnPointAsync: %s" % sp)
    NOTES.append("S chest " + (chest[0] if chest else "-"))
    NOTES.append("S spawn " + (sp[0] if sp else "-"))
    NOTES.append("S smoke verdict: " + " | ".join(verdict))
    print("S. real 0.7 server: SkyyIslands %s ready; island made the /island way: %d blocks = the %s layout, chest + kit, grass tint, relight "
          "%s; second fill skipped; TintFix on the real chunk; spawn point %s" % (VERSION, len(d2), OLD_VERSION,
                                                                                  ", ".join(re.findall(r"\(\d/9 chunks\)", " ".join(rel))),
                                                                                  sp[0][3:] if sp else "-"))


def main():
    if "--probe-build" in sys.argv:
        build_probe(os.path.abspath(arg("--probe-build")))
        return 0
    for j in (JAR, OLD):
        if not os.path.isfile(j):
            print("no jar at", j, "- build it first")
            return 1
    os.makedirs(SCRATCH, exist_ok=True)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp
    os.environ["TMP"] = tmp
    try:
        if not NO_SERVER:
            run_server()
        run_jvm()
    except Exception as e:
        import traceback
        traceback.print_exc()
        FAILS.append("harness error: %s" % e)
    for n in NOTES:
        print("  note:", n[:400])
    print("SkyyIslands %s harness: %d ok, %d fail(s)%s" % (VERSION, OKS[0], len(FAILS), " (part 2 skipped: --no-server)" if NO_SERVER else ""))
    for f in FAILS[:40]:
        print("  FAIL", f[:500])
    return 1 if FAILS else 0


if __name__ == "__main__":
    code = main()
    if "--probe-build" not in sys.argv and not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.stdout.flush()
    os._exit(code)
