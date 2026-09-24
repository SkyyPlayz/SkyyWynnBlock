"""Derive SkyyIslands/build_skyyislands_0.2.py from 0.1 (server-mode hub handling, Skyy 2026-09-23).
0.2:
 - /sethub (perm skyyislands.admin): saves your current world + position + rotation as THE hub (Skyy_SkyyIslands/hub.properties).
 - /hub (alias /lobby): teleports to the hub point in any world (Teleport component). If no hub is set: default world spawn.
   (0.1 used InstancesPlugin.exitInstance = "back where you came from"; a server hub must be a fixed place.)
 - Login routing: PlayerReadyEvent -> 1.5s later, if the player is inside an island world they are sent to the hub
   (SkyBlock servers always start you in the hub; also avoids joining into a world that may be mid-unload).
 - /island alias "home" removed (vanilla + HyperEssentials own /home). Alias "is" stays.
 - Island world names are remembered (Skyy_SkyyIslands/islands/*.properties) so isIslandWorld(name) works after restarts.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.1.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.2.py")
s = open(src, encoding="utf8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    s = s.replace(old, new, count)

rep('VERSION = "0.1"', 'VERSION = "0.2"')
s = s.replace('"""SkyyIslands 0.1 - build script', '"""SkyyIslands 0.2 - build script\n0.2: /sethub + fixed-point /hub + login routing to the hub + island world registry (see tools/islands_0_2_patch.py).\n', 1)
rep('TP  = "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport"',
    'TP  = "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport"\nPRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"\nHSV = "com.hypixel.hytale.server.core.HytaleServer"\nR3F = "com.hypixel.hytale.math.vector.Rotation3f"')
rep('(TC, "getTransform"), (TP, "createForPlayer"), (CTX, "provided"),',
    '(TC, "getTransform"), (TP, "createForPlayer"), (CTX, "provided"), (HSV, "SCHEDULED_EXECUTOR"), (PRE, "getPlayerRef"),\n             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),')
rep('hcmd = pool.makeClass(PKG + ".HubCmd", pool.get(APC))',
    'hcmd = pool.makeClass(PKG + ".HubCmd", pool.get(APC))\nshub = pool.makeClass(PKG + ".SetHubCmd", pool.get(APC))\nrdy  = pool.makeClass(PKG + ".IslandReady")\nrout = pool.makeClass(PKG + ".RouteTask")\ndisp = pool.makeClass(PKG + ".RouteDispatch")')

# ---- IslandStore: hub point + island world registry
rep('''st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CREATING = new java.util.concurrent.ConcurrentHashMap();", st_))''',
'''st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CREATING = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.Set ISLAND_WORLDS = java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap());", st_))
st_.addField(CtField.make("public static java.nio.file.Path HUB_FILE;", st_))
st_.addField(CtField.make("public static volatile String HUB_WORLD;", st_))
st_.addField(CtField.make("public static volatile double[] HUB_POS;", st_))
st_.addField(CtField.make("public static volatile float[] HUB_ROT;", st_))''')

rep('''st_.addMethod(CtNewMethod.make("""
public static String worldName(java.util.UUID u) {''',
'''st_.addMethod(CtNewMethod.make("""
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
public static String worldName(java.util.UUID u) {''')

rep('''  p.setProperty("world", name);
  p.setProperty("created", String.valueOf(System.currentTimeMillis()));''',
'''  p.setProperty("world", name);
  p.setProperty("created", String.valueOf(System.currentTimeMillis()));
  ISLAND_WORLDS.add(name);''')

# ---- /island: drop the "home" alias
rep('addAliases(new String[] {{ "is", "home" }});', 'addAliases(new String[] {{ "is" }});')

# ---- /hub: fixed hub point
start = s.index('hcmd.addMethod(CtNewMethod.make(f"""\nprotected void execute(')
end = s.index('}}""", hcmd))', start) + len('}}""", hcmd))')
hub_exec = '''hcmd.addMethod(CtNewMethod.make(f"""
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
}}""", hcmd))'''
s = s[:start] + hub_exec + s[end:]

# ---- /sethub + login routing classes, inserted before the plugin section
rep('# ================= plugin =================', '''# ================= /sethub =================
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
    {PKG}.RouteTask.schedule(pr);
  }} catch (Throwable t) {{ }}
}}""", rdy))

# ================= plugin =================''')

rep('''  getCommandRegistry().registerCommand(new {PKG}.HubCmd());''',
'''  getCommandRegistry().registerCommand(new {PKG}.HubCmd());
  getCommandRegistry().registerCommand(new {PKG}.SetHubCmd());
  {PKG}.IslandStore.HUB_FILE = getDataDirectory().resolveSibling("Skyy_SkyyIslands").resolve("hub.properties");
  {PKG}.IslandStore.loadHub();
  {PKG}.IslandStore.loadIslandWorlds();
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.IslandReady());''')
rep('''"[SkyyIslands] {VERSION} ready - /island /hub (template SkyyIsland "''',
    '''"[SkyyIslands] {VERSION} ready - /island /hub /sethub (hub " + ({PKG}.IslandStore.HUB_WORLD == null ? "NOT set - run /sethub" : "in " + {PKG}.IslandStore.HUB_WORLD) + ", " + {PKG}.IslandStore.ISLAND_WORLDS.size() + " island worlds known, template SkyyIsland "''')
rep('for c in (st_, fill, cfl, bld, icmd, hcmd, pl):', 'for c in (st_, fill, cfl, bld, icmd, hcmd, shub, rout, disp, rdy, pl):')
rep('m = B.manifest("SkyyIslands", VERSION, "SkyWynn private islands: /island creates and loads your own instanced sky island, /hub returns,',
    'm = B.manifest("SkyyIslands", VERSION, "SkyWynn private islands: /island creates and loads your own instanced sky island, /hub warps to the hub (/sethub), logins start in the hub,')

open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
