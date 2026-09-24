"""SkyyIslands 0.1 - build script (javassist via jpype). P0 spike: private per-player island worlds.
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

VERSION = "0.1"
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

for c, m in ((INS, "spawnInstance"), (INS, "teleportPlayerToLoadingInstance"), (INS, "teleportPlayerToInstance"), (INS, "exitInstance"),
             (UNI, "isWorldLoadable"), (UNI, "addWorld"), (UNI, "getDefaultWorld"), (WLD, "getChunkAsync"), (WCH, "setBlock"),
             (CHU, "indexChunk"), (TC, "getTransform"), (TP, "createForPlayer"), (CTX, "provided"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

PKG = "com.skyy.islands"
st_  = pool.makeClass(PKG + ".IslandStore")
fill = pool.makeClass(PKG + ".FillTask")
cfl  = pool.makeClass(PKG + ".ChunkFill")
bld  = pool.makeClass(PKG + ".IslandBuild")
icmd = pool.makeClass(PKG + ".IslandCmd", pool.get(APC))
hcmd = pool.makeClass(PKG + ".HubCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyIslandsPlugin", pool.get(JP))

# ================= IslandStore =================
st_.addField(CtField.make("public static java.nio.file.Path DIR;", st_))
st_.addField(CtField.make(f"public static {LOG} LOG;", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CREATING = new java.util.concurrent.ConcurrentHashMap();", st_))
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
public static String worldName(java.util.UUID u) {
  String s = read(u).getProperty("world");
  return s == null || s.trim().isEmpty() ? null : s.trim();
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void setWorldName(java.util.UUID u, String name) {
  java.util.Properties p = read(u);
  p.setProperty("world", name);
  p.setProperty("created", String.valueOf(System.currentTimeMillis()));
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
  addAliases(new String[] {{ "is", "home" }});
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
        return;
      }}
      if (uni.isWorldLoadable(name)) {{
        pr.sendMessage({MSG}.raw("[Island] Loading the island..."));
        java.util.concurrent.CompletableFuture f = openSaved(name);
        {INS}.teleportPlayerToLoadingInstance(ref, ({CA}) store, f, ret, null);
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
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {WLD} def = {UNI}.get().getDefaultWorld();
    if (def == world) {{ pr.sendMessage({MSG}.raw("[Island] You are already in the main world.")); return; }}
    pr.sendMessage({MSG}.raw("[Island] Returning to the hub..."));
    try {{
      {INS}.exitInstance(ref, ({CA}) store);
      return;
    }} catch (Throwable t) {{ {PKG}.IslandStore.info("exitInstance fell back to default spawn: " + t); }}
    {TRF} spawn = def.getWorldConfig().getSpawnProvider().getSpawnPoint(def, pr.getUuid());
    (({CA}) store).addComponent(ref, {TP}.getComponentType(), {TP}.createForPlayer(def, spawn));
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/hub failed: " + t);
    pr.sendMessage({MSG}.raw("[Island] Could not return: " + t.getMessage()));
  }}
}}""", hcmd))

# ================= plugin =================
pl.addConstructor(CtNewConstructor.make(f"public SkyyIslandsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.IslandStore.LOG = getLogger();
  {PKG}.IslandStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyIslands").resolve("islands");
  getCommandRegistry().registerCommand(new {PKG}.IslandCmd());
  getCommandRegistry().registerCommand(new {PKG}.HubCmd());
  boolean tpl = false;
  try {{ tpl = {INS}.doesInstanceAssetExist("SkyyIsland"); }} catch (Throwable t) {{ }}
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyIslands] {VERSION} ready - /island /hub (template SkyyIsland " + (tpl ? "found" : "NOT FOUND - check Server/Instances in the jar") + ")");
}}""", pl))

for c in (st_, fill, cfl, bld, icmd, hcmd, pl):
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
    "WorldGen": {"Type": "Void"},
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
m = B.manifest("SkyyIslands", VERSION, "SkyWynn private islands: /island creates and loads your own instanced sky island, /hub returns, /island invite|visit for co-op. Zero dependencies.", PKG + ".SkyyIslandsPlugin")
B.assemble(jar, m, OUT, extra_files=files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyIslands.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyIslands" % VERSION, disable_prefix="Skyy:")
