"""SkyyIslands 0.2.2 - build script
0.2.2: blocks placed by FillTask rendered BLACK (their light update was lost while the world was still starting; the chunk then saved
  with zero light). Now every arrival schedules a relight of chunks (-1..1,-1..1) 4s later via ChunkLightingManager.invalidateLightInChunk.
  Template WorldGen gets Environment Env_Default_Void (new islands only).

0.2.1: PlayerReadyEvent fires on EVERY world switch (verified in the log: joined island, routed to hub 3s later). Login routing now
  runs only on the first ready per online session (SEEN set, pruned every 10s against Universe.getPlayers()).

0.2: /sethub + fixed-point /hub + login routing to the hub + island world registry (see tools/islands_0_2_patch.py).
 (javassist via jpype). P0 spike: private per-player island worlds.
Run:   python build_skyyislands_0.1.py            -> SkyyIslands/SkyyIslands-0.1.jar
       python build_skyyislands_0.1.py --deploy   -> also copies to Mods/SkyyIslands.jar and enables it in the HUD mod world
How it works (all engine, verified against HytaleServer.jar bytecode 2026-09-23):
 - Template instance shipped in the jar at Server/Instances/SkyyIsland/instance.bson (plain JSON despite the name, same as every
   reference mod): Void world gen, Global spawn at (8.5,129,8.5), Instance.RemovalConditions=[WorldEmpty], DeleteOnRemove=false.
 - First /island: InstancesPlugin.spawnInstance("SkyyIsland", "skyy-island-<uuid>", fromWorld, returnTransform) copies the template
   into the universe worlds folder and loads it. We chain IslandBuild: load chunk (0,0) and place a 12x12 floating starter island
   (grass/dirt/stone, oak tree, chest) with WorldChunk.setBlock(x,y,z,"<BlockId>") on the world thread, then
   InstancesPlugin.teleportPlayerToLoadingInstance(ref, store, future, null, null) sends the player once the future completes
   (return point = current transform, spawn = the world's SpawnProvider).
 - The world name is saved to Skyy_SkyyIslands/islands/<uuid>.properties. When the island empties the engine unloads it (folder stays).
   Later /island: Universe.getWorld(name) if loaded, else Universe.addWorld(name) (isWorldLoadable checks config.json exists).
 - /hub: InstancesPlugin.exitInstance(ref, store) (return point saved by the engine); fallback = Teleport to the default world spawn.
 - Co-op: /island invite <player> adds them to your members list; /island visit <player> works for members (and the owner).
UNVERIFIED (test): the copied world folder really survives unload; addWorld reloads it with blocks intact; login while your island is
unloaded (engine should fall back to the default world); void death handling.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.2.2"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
CA  = "com.hypixel.hytale.component.ComponentAccessor"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
WCH = "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk"
CHU = "com.hypixel.hytale.math.util.ChunkUtil"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
INS = "com.hypixel.hytale.builtin.instances.InstancesPlugin"
TRF = "com.hypixel.hytale.math.vector.Transform"
TC  = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
TP  = "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
R3F = "com.hypixel.hytale.math.vector.Rotation3f"

for c, m in ((INS, "spawnInstance"), (INS, "teleportPlayerToLoadingInstance"), (INS, "teleportPlayerToInstance"), (INS, "exitInstance"),
             (UNI, "isWorldLoadable"), (UNI, "addWorld"), (UNI, "getDefaultWorld"), (WLD, "getChunkAsync"), (WCH, "setBlock"),
             (CHU, "indexChunk"), (TC, "getTransform"), (TP, "createForPlayer"), (CTX, "provided"), (HSV, "SCHEDULED_EXECUTOR"), (PRE, "getPlayerRef"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

PKG = "com.skyy.islands"
st_  = pool.makeClass(PKG + ".IslandStore")
fill = pool.makeClass(PKG + ".FillTask")
cfl  = pool.makeClass(PKG + ".ChunkFill")
reln = pool.makeClass(PKG + ".RelightNow")
relt = pool.makeClass(PKG + ".RelightTask")
bld  = pool.makeClass(PKG + ".IslandBuild")
icmd = pool.makeClass(PKG + ".IslandCmd", pool.get(APC))
hcmd = pool.makeClass(PKG + ".HubCmd", pool.get(APC))
shub = pool.makeClass(PKG + ".SetHubCmd", pool.get(APC))
rdy  = pool.makeClass(PKG + ".IslandReady")
rout = pool.makeClass(PKG + ".RouteTask")
disp = pool.makeClass(PKG + ".RouteDispatch")
seen = pool.makeClass(PKG + ".SeenTick")
pl   = pool.makeClass(PKG + ".SkyyIslandsPlugin", pool.get(JP))

# ================= IslandStore =================
st_.addField(CtField.make("public static java.nio.file.Path DIR;", st_))
st_.addField(CtField.make(f"public static {LOG} LOG;", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CREATING = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.Set ISLAND_WORLDS = java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap());", st_))
st_.addField(CtField.make("public static java.nio.file.Path HUB_FILE;", st_))
st_.addField(CtField.make("public static volatile String HUB_WORLD;", st_))
st_.addField(CtField.make("public static volatile double[] HUB_POS;", st_))
st_.addField(CtField.make("public static volatile float[] HUB_ROT;", st_))
st_.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyIslands] " + msg); } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyIslands] " + msg); } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized java.util.Properties read(java.util.UUID u) {
  java.util.Properties p = new java.util.Properties();
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) { warn("could not read island file for " + u + ": " + t); }
  return p;
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void write(java.util.UUID u, java.util.Properties p) {
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyIslands"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not write island file for " + u + ": " + t); }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void loadHub() {
  try {
    if (HUB_FILE == null || !java.nio.file.Files.exists(HUB_FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(HUB_FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    String w = p.getProperty("world");
    if (w == null || w.trim().isEmpty()) return;
    HUB_WORLD = w.trim();
    HUB_POS = new double[] { Double.parseDouble(p.getProperty("x", "0")), Double.parseDouble(p.getProperty("y", "100")), Double.parseDouble(p.getProperty("z", "0")) };
    HUB_ROT = new float[] { Float.parseFloat(p.getProperty("rx", "0")), Float.parseFloat(p.getProperty("ry", "0")), Float.parseFloat(p.getProperty("rz", "0")) };
  } catch (Throwable t) { warn("could not load hub.properties: " + t); }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void saveHub(String world, double x, double y, double z, float rx, float ry, float rz) {
  HUB_WORLD = world; HUB_POS = new double[] { x, y, z }; HUB_ROT = new float[] { rx, ry, rz };
  try {
    java.nio.file.Files.createDirectories(HUB_FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("world", world);
    p.setProperty("x", String.valueOf(x)); p.setProperty("y", String.valueOf(y)); p.setProperty("z", String.valueOf(z));
    p.setProperty("rx", String.valueOf(rx)); p.setProperty("ry", String.valueOf(ry)); p.setProperty("rz", String.valueOf(rz));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(HUB_FILE, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyIslands hub point (/sethub)"); } finally { out.close(); }
  } catch (Throwable t) { warn("could not save hub.properties: " + t); }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void loadIslandWorlds() {
  try {
    if (DIR == null || !java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) return;
    java.util.stream.Stream st = java.nio.file.Files.list(DIR);
    try {
      java.util.Iterator it = st.iterator();
      while (it.hasNext()) {
        java.nio.file.Path f = (java.nio.file.Path) it.next();
        String n = f.getFileName().toString();
        if (!n.endsWith(".properties")) continue;
        java.util.Properties p = new java.util.Properties();
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { p.load(in); } finally { in.close(); }
        String w = p.getProperty("world");
        if (w != null && w.trim().length() > 0) ISLAND_WORLDS.add(w.trim());
      }
    } finally { st.close(); }
  } catch (Throwable t) { warn("could not scan island files: " + t); }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean isIslandWorld(String name) {
  return name != null && ISLAND_WORLDS.contains(name);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String worldName(java.util.UUID u) {
  String s = read(u).getProperty("world");
  return s == null || s.trim().isEmpty() ? null : s.trim();
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void setWorldName(java.util.UUID u, String name) {
  java.util.Properties p = read(u);
  p.setProperty("world", name);
  p.setProperty("created", String.valueOf(System.currentTimeMillis()));
  ISLAND_WORLDS.add(name);
  write(u, p);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean isMember(java.util.UUID owner, java.util.UUID who) {
  if (owner.equals(who)) return true;
  String m = read(owner).getProperty("members", "");
  return ("," + m + ",").indexOf("," + who.toString() + ",") >= 0;
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized boolean addMember(java.util.UUID owner, java.util.UUID who) {
  if (isMember(owner, who)) return false;
  java.util.Properties p = read(owner);
  String m = p.getProperty("members", "");
  p.setProperty("members", m.isEmpty() ? who.toString() : m + "," + who.toString());
  write(owner, p);
  return true;
}""", st_))

# ================= FillTask (world thread): place the starter island in chunk (0,0) =================
fill.addInterface(pool.get("java.lang.Runnable"))
fill.addField(CtField.make(f"public {WLD} world;", fill))
fill.addField(CtField.make(f"public {WCH} chunk;", fill))
fill.addField(CtField.make("public java.util.concurrent.CompletableFuture done;", fill))
fill.addConstructor(CtNewConstructor.make(f"public FillTask({WLD} w, {WCH} c, java.util.concurrent.CompletableFuture d) {{ this.world = w; this.chunk = c; this.done = d; }}", fill))
fill.addMethod(CtNewMethod.make("""
public int put(int x, int y, int z, String id) {
  try { return chunk.setBlock(x, y, z, id) ? 1 : 0; } catch (Throwable t) { return 0; }
}""", fill))
fill.addMethod(CtNewMethod.make(f"""
public void run() {{
  int n = 0;
  try {{
    if (chunk.getBlock(8, 128, 8) != 0) {{ done.complete(world); return; }}
    for (int x = 2; x <= 13; x++) for (int z = 2; z <= 13; z++) {{
      boolean corner = (x == 2 || x == 13) && (z == 2 || z == 13);
      if (corner) continue;
      n += put(x, 128, z, "Soil_Grass");
      n += put(x, 127, z, "Soil_Dirt");
      if (x >= 3 && x <= 12 && z >= 3 && z <= 12) n += put(x, 126, z, "Soil_Dirt");
      if (x >= 4 && x <= 11 && z >= 4 && z <= 11) n += put(x, 125, z, "Rock_Stone");
      if (x >= 6 && x <= 9 && z >= 6 && z <= 9) n += put(x, 124, z, "Rock_Stone");
    }}
    for (int y = 129; y <= 133; y++) n += put(11, y, 11, "Wood_Oak_Trunk");
    for (int x = 9; x <= 13; x++) for (int z = 9; z <= 13; z++) for (int y = 132; y <= 134; y++) {{
      if (x == 11 && z == 11 && y <= 133) continue;
      boolean edge = (x == 9 || x == 13) && (z == 9 || z == 13);
      if (edge || (y == 134 && (x == 9 || x == 13 || z == 9 || z == 13))) continue;
      n += put(x, y, z, "Plant_Leaves_Oak");
    }}
    n += put(11, 135, 11, "Plant_Leaves_Oak");
    n += put(4, 129, 4, "Furniture_Crude_Chest_Small");
    {PKG}.IslandStore.info("starter island placed in " + world.getName() + " (" + n + " blocks)");
  }} catch (Throwable t) {{ {PKG}.IslandStore.warn("island fill failed: " + t); }}
  done.complete(world);
}}""", fill))

# ================= ChunkFill: Function<WorldChunk, CompletableFuture<World>> =================
cfl.addInterface(pool.get("java.util.function.Function"))
cfl.addField(CtField.make(f"public {WLD} world;", cfl))
cfl.addConstructor(CtNewConstructor.make(f"public ChunkFill({WLD} w) {{ this.world = w; }}", cfl))
cfl.addMethod(CtNewMethod.make(f"""
public Object apply(Object chunk) {{
  java.util.concurrent.CompletableFuture done = new java.util.concurrent.CompletableFuture();
  try {{
    if (chunk == null) {{ {PKG}.IslandStore.warn("chunk (0,0) did not load, island left empty"); done.complete(world); return done; }}
    world.execute(new {PKG}.FillTask(world, ({WCH}) chunk, done));
  }} catch (Throwable t) {{ {PKG}.IslandStore.warn("island fill dispatch failed: " + t); done.complete(world); }}
  return done;
}}""", cfl))

# ================= RelightNow (world thread) / RelightTask (scheduler -> world thread) =================
reln.addInterface(pool.get("java.lang.Runnable"))
reln.addField(CtField.make(f"public {WLD} world;", reln))
reln.addConstructor(CtNewConstructor.make(f"public RelightNow({WLD} w) {{ this.world = w; }}", reln))
reln.addMethod(CtNewMethod.make(f"""
public void run() {{
  int ok = 0;
  try {{
    for (int cx = -1; cx <= 1; cx++) for (int cz = -1; cz <= 1; cz++) {{
      try {{ if (world.getChunkLighting().invalidateLightInChunk(world.getChunkStore(), cx, cz)) ok++; }} catch (Throwable t) {{ }}
    }}
    {PKG}.IslandStore.info("relight queued for " + world.getName() + " (" + ok + "/9 chunks)");
  }} catch (Throwable t) {{ {PKG}.IslandStore.warn("relight failed: " + t); }}
}}""", reln))
relt.addInterface(pool.get("java.lang.Runnable"))
relt.addField(CtField.make("public String name;", relt))
relt.addConstructor(CtNewConstructor.make("public RelightTask(String n) { this.name = n; }", relt))
relt.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {WLD} w = {UNI}.get().getWorld(this.name);
    if (w == null || !w.isAlive()) return;
    w.execute(new {PKG}.RelightNow(w));
  }} catch (Throwable t) {{ }}
}}""", relt))
relt.addMethod(CtNewMethod.make(f"""
public static void schedule(String name) {{
  if (name == null) return;
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.RelightTask(name), 4000L, java.util.concurrent.TimeUnit.MILLISECONDS); }} catch (Throwable t) {{ }}
}}""", relt))

# ================= IslandBuild: Function<World, CompletableFuture<World>> (thenCompose) =================
bld.addInterface(pool.get("java.util.function.Function"))
bld.addField(CtField.make("public java.util.UUID owner;", bld))
bld.addConstructor(CtNewConstructor.make("public IslandBuild(java.util.UUID u) { this.owner = u; }", bld))
bld.addMethod(CtNewMethod.make(f"""
public Object apply(Object w) {{
  {WLD} world = ({WLD}) w;
  {PKG}.IslandStore.CREATING.remove(owner);
  try {{
    {PKG}.IslandStore.setWorldName(owner, world.getName());
    {PKG}.IslandStore.info("island world for " + owner + " = " + world.getName());
    {PKG}.RelightTask.schedule(world.getName());
    return world.getChunkAsync({CHU}.indexChunk(0, 0)).thenCompose(new {PKG}.ChunkFill(world));
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("island build failed: " + t);
    return java.util.concurrent.CompletableFuture.completedFuture(world);
  }}
}}""", bld))

# ================= /island =================
icmd.addField(CtField.make(f"public {OA} actionArg;", icmd))
icmd.addField(CtField.make(f"public {OA} targetArg;", icmd))
icmd.addConstructor(CtNewConstructor.make(f"""
public IslandCmd() {{
  super("island", "Go to your private island (creates it the first time). /island invite <player>, /island visit <player>, /island info");
  addAliases(new String[] {{ "is" }});
  this.actionArg = withOptionalArg("action", "invite | visit | info (omit to go home)", {ATY}.STRING);
  this.targetArg = withOptionalArg("player", "player to invite / visit", {ATY}.PLAYER_REF);
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
public static {TRF} here({ST} store, {REF} ref) {{
  try {{
    {TC} tc = ({TC}) store.getComponent(ref, {TC}.getComponentType());
    if (tc != null && tc.getTransform() != null) return new {TRF}(tc.getTransform());
  }} catch (Throwable t) {{ }}
  return null;
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.concurrent.CompletableFuture openSaved(String name) {{
  {UNI} uni = {UNI}.get();
  {WLD} again = uni.getWorld(name);
  if (again != null) return java.util.concurrent.CompletableFuture.completedFuture(again);
  try {{
    return uni.addWorld(name);
  }} catch (IllegalArgumentException dup) {{
    again = uni.getWorld(name);
    if (again != null) return java.util.concurrent.CompletableFuture.completedFuture(again);
    throw dup;
  }}
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
public static void go({ST} store, {REF} ref, {PR} pr, {WLD} from, java.util.UUID owner, boolean own) {{
  java.util.UUID u = pr.getUuid();
  {UNI} uni = {UNI}.get();
  String name = {PKG}.IslandStore.worldName(owner);
  {TRF} ret = here(store, ref);
  try {{
    if (name != null) {{
      {WLD} w = uni.getWorld(name);
      if (w != null && w.isAlive()) {{
        if (from == w) {{ pr.sendMessage({MSG}.raw("[Island] You are already on this island.")); return; }}
        pr.sendMessage({MSG}.raw("[Island] Teleporting..."));
        {INS}.teleportPlayerToInstance(ref, ({CA}) store, w, ret);
        {PKG}.RelightTask.schedule(name);
        return;
      }}
      if (uni.isWorldLoadable(name)) {{
        pr.sendMessage({MSG}.raw("[Island] Loading the island..."));
        java.util.concurrent.CompletableFuture f = openSaved(name);
        {INS}.teleportPlayerToLoadingInstance(ref, ({CA}) store, f, ret, null);
        {PKG}.RelightTask.schedule(name);
        return;
      }}
      {PKG}.IslandStore.warn("island world '" + name + "' for " + owner + " is gone from disk");
    }}
    if (!own) {{ pr.sendMessage({MSG}.raw("[Island] That player has no island yet.")); return; }}
    Long since = (Long) {PKG}.IslandStore.CREATING.get(u);
    if (since != null && System.currentTimeMillis() - since.longValue() < 60000L) {{ pr.sendMessage({MSG}.raw("[Island] Your island is still being created, hold on...")); return; }}
    {PKG}.IslandStore.CREATING.put(u, Long.valueOf(System.currentTimeMillis()));
    pr.sendMessage({MSG}.raw("[Island] Creating your island... (first time only)"));
    java.util.concurrent.CompletableFuture f = {INS}.get().spawnInstance("SkyyIsland", "skyy-island-" + u.toString(), from, ret);
    f = f.thenCompose(new {PKG}.IslandBuild(u));
    {INS}.teleportPlayerToLoadingInstance(ref, ({CA}) store, f, ret, null);
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/island failed for " + u + ": " + t);
    pr.sendMessage({MSG}.raw("[Island] Could not open the island: " + t.getMessage()));
  }}
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  try {{
    if (!ctx.provided(this.actionArg)) {{ go(store, ref, pr, world, u, true); return; }}
    String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
    if (a.equals("info")) {{
      String name = {PKG}.IslandStore.worldName(u);
      String members = {PKG}.IslandStore.read(u).getProperty("members", "");
      pr.sendMessage({MSG}.raw("[Island] " + (name == null ? "No island yet, /island to create one." : "world " + name + (({UNI}.get().getWorld(name) != null) ? " (loaded)" : " (unloaded)")) + "  members: " + (members.isEmpty() ? "none" : String.valueOf(members.split(",").length))));
      pr.sendMessage({MSG}.raw("[Island] You are in world: " + world.getName()));
      return;
    }}
    if (a.equals("home") || a.equals("go")) {{ go(store, ref, pr, world, u, true); return; }}
    if (!ctx.provided(this.targetArg)) {{ pr.sendMessage({MSG}.raw("[Island] Usage: /island | /island invite <player> | /island visit <player> | /island info")); return; }}
    {PR} target = ({PR}) ctx.get(this.targetArg);
    if (target == null || !target.isValid()) {{ pr.sendMessage({MSG}.raw("[Island] That player is not online.")); return; }}
    if (a.equals("invite") || a.equals("add")) {{
      if (target.getUuid().equals(u)) {{ pr.sendMessage({MSG}.raw("[Island] That is you.")); return; }}
      if ({PKG}.IslandStore.addMember(u, target.getUuid())) {{
        pr.sendMessage({MSG}.raw("[Island] " + target.getUsername() + " can now visit your island (/island visit " + pr.getUsername() + ")."));
        target.sendMessage({MSG}.raw("[Island] " + pr.getUsername() + " invited you to their island! /island visit " + pr.getUsername()));
      }} else pr.sendMessage({MSG}.raw("[Island] " + target.getUsername() + " is already a member."));
      return;
    }}
    if (a.equals("visit") || a.equals("warp")) {{
      if (!{PKG}.IslandStore.isMember(target.getUuid(), u)) {{ pr.sendMessage({MSG}.raw("[Island] " + target.getUsername() + " has not invited you.")); return; }}
      go(store, ref, pr, world, target.getUuid(), false);
      return;
    }}
    pr.sendMessage({MSG}.raw("[Island] Usage: /island | /island invite <player> | /island visit <player> | /island info"));
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/island error: " + t);
    pr.sendMessage({MSG}.raw("[Island] Something went wrong: " + t.getMessage()));
  }}
}}""", icmd))

# ================= /hub =================
hcmd.addConstructor(CtNewConstructor.make("""
public HubCmd() {
  super("hub", "Leave your island and return to the main world");
  addAliases(new String[] { "lobby" });
}""", hcmd))
hcmd.addMethod(CtNewMethod.make(f"""
public static boolean sendToHub({ST} store, {REF} ref, {PR} pr, {WLD} from) {{
  {UNI} uni = {UNI}.get();
  {WLD} target = null; {TRF} where = null;
  if ({PKG}.IslandStore.HUB_WORLD != null) {{
    target = uni.getWorld({PKG}.IslandStore.HUB_WORLD);
    if (target != null && target.isAlive()) {{
      double[] p = {PKG}.IslandStore.HUB_POS; float[] r = {PKG}.IslandStore.HUB_ROT;
      where = new {TRF}(p[0], p[1], p[2], r[0], r[1], r[2]);
    }} else {{ {PKG}.IslandStore.warn("hub world '" + {PKG}.IslandStore.HUB_WORLD + "' is not loaded, using default spawn"); target = null; }}
  }}
  if (target == null) {{
    target = uni.getDefaultWorld();
    if (target == null) return false;
    where = target.getWorldConfig().getSpawnProvider().getSpawnPoint(target, pr.getUuid());
  }}
  if (where == null) return false;
  (({CA}) store).addComponent(ref, {TP}.getComponentType(), {TP}.createForPlayer(target, where));
  return true;
}}""", hcmd))
hcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    pr.sendMessage({MSG}.raw("[Island] Warping to the hub..."));
    if (!sendToHub(store, ref, pr, world)) pr.sendMessage({MSG}.raw("[Island] No hub is set and no default world spawn was found. An admin can stand somewhere and run /sethub."));
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/hub failed: " + t);
    pr.sendMessage({MSG}.raw("[Island] Could not warp: " + t.getMessage()));
  }}
}}""", hcmd))

# ================= /sethub =================
shub.addConstructor(CtNewConstructor.make("""
public SetHubCmd() {
  super("sethub", "(admin) Set the server hub point to where you stand");
  requirePermission("skyyislands.admin");
}""", shub))
shub.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if ({PKG}.IslandStore.isIslandWorld(world.getName())) {{ pr.sendMessage({MSG}.raw("[Island] The hub cannot be inside an island world.")); return; }}
    {TC} tc = ({TC}) store.getComponent(ref, {TC}.getComponentType());
    if (tc == null || tc.getTransform() == null) {{ pr.sendMessage({MSG}.raw("[Island] Could not read your position.")); return; }}
    {TRF} t = tc.getTransform();
    org.joml.Vector3d p = t.getPosition();
    {R3F} r = t.getRotation();
    {PKG}.IslandStore.saveHub(world.getName(), p.x, p.y, p.z, r == null ? 0f : r.x, r == null ? 0f : r.y, r == null ? 0f : r.z);
    pr.sendMessage({MSG}.raw("[Island] Hub set here in world '" + world.getName() + "' (" + (int) p.x + ", " + (int) p.y + ", " + (int) p.z + "). /hub and island logins now come here."));
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/sethub failed: " + t);
    pr.sendMessage({MSG}.raw("[Island] Could not set the hub: " + t.getMessage()));
  }}
}}""", shub))

# ================= login routing: PlayerReadyEvent -> RouteTask on the player's world thread =================
rout.addInterface(pool.get("java.lang.Runnable"))
rout.addField(CtField.make(f"public {PR} pr;", rout))
rout.addConstructor(CtNewConstructor.make(f"public RouteTask({PR} pr) {{ this.pr = pr; }}", rout))
rout.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    {WLD} w = {UNI}.get().getWorld(wu);
    if (w == null || !{PKG}.IslandStore.isIslandWorld(w.getName())) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    if ({PKG}.HubCmd.sendToHub(st, r, pr, w)) pr.sendMessage({MSG}.raw("[Island] Welcome back! You start in the hub - /island takes you home."));
  }} catch (Throwable t) {{ {PKG}.IslandStore.warn("login routing failed: " + t); }}
}}""", rout))
# Dispatch: scheduler thread -> world thread
disp.addInterface(pool.get("java.lang.Runnable"))
disp.addField(CtField.make(f"public {PR} pr;", disp))
disp.addConstructor(CtNewConstructor.make(f"public RouteDispatch({PR} pr) {{ this.pr = pr; }}", disp))
disp.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    {WLD} w = {UNI}.get().getWorld(wu);
    if (w == null) return;
    w.execute(new {PKG}.RouteTask(pr));
  }} catch (Throwable t) {{ }}
}}""", disp))

rout.addMethod(CtNewMethod.make(f"""
public static void schedule({PR} pr) {{
  {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.RouteDispatch(pr), 1500L, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", rout))
rdy.addInterface(pool.get("java.util.function.Consumer"))
rdy.addConstructor(CtNewConstructor.make("public IslandReady() { }", rdy))
rdy.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    {PRE} e = ({PRE}) ev;
    {REF} r = e.getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    if ({PKG}.IslandStore.SEEN.putIfAbsent(pr.getUuid(), Boolean.TRUE) != null) return;
    {PKG}.RouteTask.schedule(pr);
  }} catch (Throwable t) {{ }}
}}""", rdy))

# ================= SeenTick: forget players who logged out so their next login routes again =================
seen.addInterface(pool.get("java.lang.Runnable"))
seen.addConstructor(CtNewConstructor.make("public SeenTick() { }", seen))
seen.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{ {PR} pr = ({PR}) it.next(); if (pr != null && pr.isValid()) online.add(pr.getUuid()); }}
    {PKG}.IslandStore.SEEN.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", seen))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyIslandsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.IslandStore.LOG = getLogger();
  {PKG}.IslandStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyIslands").resolve("islands");
  getCommandRegistry().registerCommand(new {PKG}.IslandCmd());
  getCommandRegistry().registerCommand(new {PKG}.HubCmd());
  getCommandRegistry().registerCommand(new {PKG}.SetHubCmd());
  {PKG}.IslandStore.HUB_FILE = getDataDirectory().resolveSibling("Skyy_SkyyIslands").resolve("hub.properties");
  {PKG}.IslandStore.loadHub();
  {PKG}.IslandStore.loadIslandWorlds();
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.IslandReady());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SeenTick(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  boolean tpl = false;
  try {{ tpl = {INS}.doesInstanceAssetExist("SkyyIsland"); }} catch (Throwable t) {{ }}
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyIslands] {VERSION} ready - /island /hub /sethub (hub " + ({PKG}.IslandStore.HUB_WORLD == null ? "NOT set - run /sethub" : "in " + {PKG}.IslandStore.HUB_WORLD) + ", " + {PKG}.IslandStore.ISLAND_WORLDS.size() + " island worlds known, template SkyyIsland " + (tpl ? "found" : "NOT FOUND - check Server/Instances in the jar") + ")");
}}""", pl))

pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (st_, fill, cfl, reln, relt, bld, icmd, hcmd, shub, rout, disp, rdy, seen, pl):
    c.writeFile(OUT)
print("classes written")

template = {
    "$Comment": "SkyyIslands starter island template - void world; the mod places the island blocks on first visit",
    "RequiredPlugins": {},
    "ChunkStorage": {"Type": "Hytale"},
    "GameMode": "Adventure",
    "IsPvpEnabled": False,
    "IsSpawningNPC": False,
    "GameTime": "0001-01-01T09:00:00Z",
    "UUID": {"$binary": "AAAAAAAAAAAAAAAAAAAAAA==", "$type": "04"},
    "GameplayConfig": "Default",
    "IsCompassUpdating": True,
    "IsTicking": True,
    "Seed": 0,
    "IsGameTimePaused": False,
    "IsObjectiveMarkersEnabled": True,
    "IsAllNPCFrozen": False,
    "IsSavingPlayers": True,
    "WorldGen": {"Type": "Void", "Environment": "Env_Default_Void"},
    "SpawnProvider": {"Id": "Global", "SpawnPoint": {"X": 8.5, "Y": 129.0, "Z": 8.5, "Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0}},
    "IsSpawnMarkersEnabled": True,
    "Instance": {"RemovalConditions": [{"Type": "WorldEmpty"}]},
    "DeleteOnRemove": False,
    "Version": 4,
}
files = {
    "Server/Instances/SkyyIsland/instance.bson": json.dumps(template, indent=2) + "\n",
    "Server/Instances/SkyyIsland/resources/InstanceData.json": '{\n  "HadPlayer": false\n}\n',
}

jar = os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)
m = B.manifest("SkyyIslands", VERSION, "SkyWynn private islands: /island creates and loads your own instanced sky island, /hub warps to the hub (/sethub), logins start in the hub, /island invite|visit for co-op. Zero dependencies.", PKG + ".SkyyIslandsPlugin")
B.assemble(jar, m, OUT, extra_files=files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyIslands.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyIslands" % VERSION, disable_prefix="Skyy:")
