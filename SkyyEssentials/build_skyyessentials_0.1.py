"""SkyyEssentials 0.1 - build script (javassist via jpype).
Run:   python build_skyyessentials_0.1.py            -> SkyyEssentials/SkyyEssentials-0.1.jar
       python build_skyyessentials_0.1.py --deploy   -> also copies to Mods/SkyyEssentials.jar and enables it in the HUD mod world

Skyy's rule: "use vanilla everywhere possible, and only add what we need to". HyperEssentials is gone (world crash on death),
so this mod fills ONLY the gaps vanilla leaves. Vanilla check (2026-09-23, HytaleServer.jar, all 763 AbstractCommand
subclasses: constructor name + addAliases strings, plus a String-constant scan of every com/hypixel class):
  tpa, tpahere, tpaccept, tpdeny, tpacancel, msg, tell, w, whisper, reply, fly  -> NOT in vanilla (built here)
  r      -> OWNED BY VANILLA: alias of /redo (builtin.buildertools.commands.RedoCommand, registered top-level by
            BuilderToolsPlugin.setup). So the reply command is /reply only, never /r.
  (/tp, /tp back, /spawn, /warp, /whereami stay vanilla; our teleports append to vanilla TeleportHistory so /tp back works.)

Commands (all players, vanilla "hytale:Adventurer" permission group like /ping /who /whereami /emote). How that gate works
(bytecode, 2026-09-23 review): CommandRegistry.registerCommand -> AbstractCommand.setOwner() generates the command's permission
node (plugin base permission + ".command.<name>"; a usage variant inherits its parent's node) unless requireNoPermission() was
called, so AbstractCommand.hasPermission() does NOT short-circuit. setPermissionGroups() feeds CommandManager.createVirtualPermissionGroups
-> PermissionsModule virtual groups, which grant that node to "hytale:Adventurer" = HytalePermissionsProvider.DEFAULT_GROUP_LIST
(every player who has no explicit group). So everyone can use them, and a player moved out of that group chain loses them.
  /tpa <player>        ask to teleport to a player          /tpahere <player>   ask a player to teleport to you
  /tpaccept [player]   accept (newest, or from that player) /tpdeny [player]    refuse
  /tpacancel           cancel all your outgoing requests
  /msg <player> <text> (aliases tell, w, whisper)          /reply <text>       answer your last message partner
Admin: /fly (permission skyyessentials.fly) - toggles MovementSettings.fly = FlyMode.Allowed (engine API verified;
  pattern from HyperEssentials FlyCommand.applyFly, which used the old canFly boolean). Off = vanilla resetFly(gameMode).
  Vanilla re-derives movement settings on world change / gamemode change / model change / mount, so a 2s tick re-asserts it.

Rules: requests expire after 60s, 10s cooldown per requester, max 1 pending per requester->target pair.
Cross-world teleport = the vanilla TeleportToPlayerCommand pattern: read the destination player's TransformComponent +
HeadRotation ON THEIR world thread, then add Teleport.createForPlayer(destWorld, transform) to the mover ON THE MOVER'S
world thread (world.execute). Each step re-validates both players and re-dispatches if a player changed worlds.
Teleporting INTO an instance world (a SkyyIslands island, a portal world): like InstancesPlugin.teleportPlayerToInstance, the mover's
pre-teleport world + transform is stored as InstanceEntityConfig.setReturnPointOverride(WorldReturnPoint) (built exactly like the
engine's private makeWorldReturnPoint), so vanilla /instance exit (alias leave) and world-drain send a TPA visitor back to where they
were instead of to the island's own spawnInstance return point (the owner's position when the island was first created). Only set
when the destination is an instance AND a different world: onPlayerAddToWorld consumes the override only on instance entry.
State is in memory only; a tick prunes everything that is not keyed by an online UUID (every 10s).
"""
import sys, os
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
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
TC  = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
HR  = "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation"
TP  = "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport"
TPH = "com.hypixel.hytale.builtin.teleport.components.TeleportHistory"
TRF = "com.hypixel.hytale.math.vector.Transform"
R3F = "com.hypixel.hytale.math.vector.Rotation3f"
V3D = "org.joml.Vector3d"
MM  = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager"
MS  = "com.hypixel.hytale.protocol.MovementSettings"
FM  = "com.hypixel.hytale.protocol.FlyMode"
GM  = "com.hypixel.hytale.protocol.GameMode"
PLY = "com.hypixel.hytale.server.core.entity.entities.Player"
IEC = "com.hypixel.hytale.builtin.instances.config.InstanceEntityConfig"
IWC = "com.hypixel.hytale.builtin.instances.config.InstanceWorldConfig"
WRP = "com.hypixel.hytale.builtin.instances.config.WorldReturnPoint"
WCF = "com.hypixel.hytale.server.core.universe.world.WorldConfig"

# every engine member this mod touches (checked against HytaleServer.jar with scratchpad/reflect.py + bc.py)
for c, m in ((PR, "getUuid"), (PR, "getUsername"), (PR, "getReference"), (PR, "getWorldUuid"), (PR, "isValid"),
             (PR, "sendMessage"), (PR, "getPacketHandler"), (PR, "hasPermission"),
             (UNI, "get"), (UNI, "getPlayer"), (UNI, "getWorld"),
             (REF, "getStore"), (ST, "getComponent"), (ST, "addComponent"), (ST, "ensureAndGetComponent"), (ST, "getExternalData"),
             (EST, "getWorld"), (WLD, "execute"), (WLD, "isAlive"),
             (TC, "getComponentType"), (TC, "getPosition"), (HR, "getComponentType"), (HR, "getRotation"),
             (TP, "getComponentType"), (TP, "createForPlayer"), (TPH, "getComponentType"), (TPH, "append"),
             (R3F, "x"), (R3F, "y"), (R3F, "z"), (V3D, "x"), (V3D, "y"), (V3D, "z"),
             (MM, "getComponentType"), (MM, "getSettings"), (MM, "getDefaultSettings"), (MM, "update"), (MM, "resetFly"),
             (MS, "fly"), (FM, "Allowed"), (FM, "Disabled"), (FM, "Forced"), (GM, "Creative"), (GM, "Adventure"),
             (PLY, "getComponentType"), (PLY, "getGameMode"),
             (AC, "addAliases"), (AC, "requirePermission"), (AC, "addUsageVariant"), (AC, "setPermissionGroups"), (AC, "withRequiredArg"),
             (ATY, "PLAYER_REF"), (ATY, "GREEDY_STRING"), (CTX, "get"), (MSG, "raw"), (MSG, "color"),
             (HSV, "SCHEDULED_EXECUTOR"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             (TC, "getTransform"), (WLD, "getWorldConfig"), (WCF, "getUuid"),
             (IEC, "getComponentType"), (IEC, "setReturnPointOverride"),
             (IWC, "get"), (IWC, "shouldRespawnWhenTargeted"), (IWC, "getInstanceKey"), (IWC, "getInstanceName"),
             (WRP, "getReturnPoint"), (WRP, "getWorld")):
    B.probe(pool, c, m)

PKG = "com.skyy.essentials"
ES = PKG + ".EssStore"
rq   = pool.makeClass(PKG + ".TpReq")
es   = pool.makeClass(ES)
hop  = pool.makeClass(PKG + ".HopDispatch")
mv   = pool.makeClass(PKG + ".MoveTask")
rd   = pool.makeClass(PKG + ".ReadDestTask")
fly  = pool.makeClass(PKG + ".FlyTask")
tick = pool.makeClass(PKG + ".EssTick")
tpa  = pool.makeClass(PKG + ".TpaCmd", pool.get(APC))
tph  = pool.makeClass(PKG + ".TpaHereCmd", pool.get(APC))
tacn = pool.makeClass(PKG + ".TpAcceptNamedCmd", pool.get(APC))
tac  = pool.makeClass(PKG + ".TpAcceptCmd", pool.get(APC))
tdnn = pool.makeClass(PKG + ".TpDenyNamedCmd", pool.get(APC))
tdn  = pool.makeClass(PKG + ".TpDenyCmd", pool.get(APC))
tcan = pool.makeClass(PKG + ".TpaCancelCmd", pool.get(APC))
msg  = pool.makeClass(PKG + ".MsgCmd", pool.get(APC))
rep  = pool.makeClass(PKG + ".ReplyCmd", pool.get(APC))
flc  = pool.makeClass(PKG + ".FlyCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyEssentialsPlugin", pool.get(JP))

# vanilla: /ping /who /whereami /emote /help. NOT dead code: setOwner() auto-generates the permission node at registration and
# this grants it to the default player group via the virtual permission groups (see the docstring).
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'

# ================= TpReq (one pending teleport request) =================
for f in ("public java.util.UUID from;", "public java.util.UUID to;", "public boolean here;",
          "public String fromName;", "public String toName;", "public long created;", "public long expires;"):
    rq.addField(CtField.make(f, rq))
rq.addConstructor(CtNewConstructor.make("""
public TpReq(java.util.UUID from, java.util.UUID to, boolean here, String fromName, String toName, long created, long expires) {
  this.from = from; this.to = to; this.here = here; this.fromName = fromName; this.toName = toName;
  this.created = created; this.expires = expires;
}""", rq))

# ================= EssStore (in-memory state + shared helpers) =================
es.addField(CtField.make(f"public static {LOG} LOG;", es))
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap REQ = new java.util.concurrent.ConcurrentHashMap();", es))        # "from>to" -> TpReq
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST_SENT = new java.util.concurrent.ConcurrentHashMap();", es))  # requester uuid -> Long millis
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST_PM = new java.util.concurrent.ConcurrentHashMap();", es))    # uuid -> partner uuid
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FLY = new java.util.concurrent.ConcurrentHashMap();", es))        # uuid -> Boolean (flight on)
es.addField(CtField.make("public static final long EXPIRE_MS = 60000L;", es))
es.addField(CtField.make("public static final long COOLDOWN_MS = 10000L;", es))
es.addField(CtField.make('public static final String INFO = "#FFD37A";', es))
es.addField(CtField.make('public static final String OK = "#9CFF9C";', es))
es.addField(CtField.make('public static final String ERR = "#FF8A8A";', es))
es.addField(CtField.make('public static final String PM = "#E9A6FF";', es))
es.addField(CtField.make('public static final String FLY_PERM = "skyyessentials.fly";', es))
es.addMethod(CtNewMethod.make("""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyEssentials] " + m); } catch (Throwable t) { }
}""", es))
es.addMethod(CtNewMethod.make(f"""
public static {PR} online(java.util.UUID u) {{
  if (u == null) return null;
  {PR} p = {UNI}.get().getPlayer(u);
  return (p != null && p.isValid()) ? p : null;
}}""", es))
# the world a player is in right now (vanilla: ref.getStore().getExternalData() -> EntityStore.getWorld())
es.addMethod(CtNewMethod.make(f"""
public static {WLD} worldOf({PR} p) {{
  if (p == null) return null;
  try {{
    {REF} r = p.getReference();
    if (r != null) {{
      Object ext = r.getStore().getExternalData();
      if (ext instanceof {EST}) return (({EST}) ext).getWorld();
    }}
    java.util.UUID wu = p.getWorldUuid();
    if (wu != null) return {UNI}.get().getWorld(wu);
  }} catch (Throwable t) {{ }}
  return null;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void say({PR} p, String text, String color) {{
  if (p == null) return;
  try {{ p.sendMessage({MSG}.raw(text).color(color)); }} catch (Throwable t) {{ }}
}}""", es))
es.addMethod(CtNewMethod.make("""
public static void sayTo(java.util.UUID u, String text, String color) { say(online(u), text, color); }""", es))
es.addMethod(CtNewMethod.make("""
public static String key(java.util.UUID a, java.util.UUID b) { return a.toString() + ">" + b.toString(); }""", es))
es.addMethod(CtNewMethod.make("""
public static String secs(long ms) { if (ms < 0L) ms = 0L; return ((ms + 999L) / 1000L) + "s"; }""", es))
# ---- request book (all synchronized on EssStore.class)
es.addMethod(CtNewMethod.make(f"""
public static synchronized String tryAdd(java.util.UUID from, java.util.UUID to, boolean here, String fromName, String toName) {{
  long now = System.currentTimeMillis();
  {PKG}.TpReq old = ({PKG}.TpReq) REQ.get(key(from, to));
  if (old != null && old.expires > now)
    return "You already have a pending request to " + toName + " (" + secs(old.expires - now) + " left). /tpacancel to cancel it.";
  Long last = (Long) LAST_SENT.get(from);
  if (last != null && now - last.longValue() < COOLDOWN_MS)
    return "Please wait " + secs(COOLDOWN_MS - (now - last.longValue())) + " before sending another teleport request.";
  REQ.put(key(from, to), new {PKG}.TpReq(from, to, here, fromName, toName, now, now + EXPIRE_MS));
  LAST_SENT.put(from, Long.valueOf(now));
  return null;
}}""", es))
# newest live request addressed to `to` (optionally only from `from`); removed atomically so it can be accepted once
es.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.TpReq take(java.util.UUID to, java.util.UUID from) {{
  long now = System.currentTimeMillis();
  {PKG}.TpReq best = null;
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null || !r.to.equals(to) || r.expires <= now) continue;
    if (from != null && !r.from.equals(from)) continue;
    if (best == null || r.created > best.created) best = r;
  }}
  if (best != null) REQ.remove(key(best.from, best.to));
  return best;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static synchronized int pendingFor(java.util.UUID to) {{
  long now = System.currentTimeMillis();
  int n = 0;
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r != null && r.to.equals(to) && r.expires > now) n++;
  }}
  return n;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.List cancelFrom(java.util.UUID from) {{
  java.util.ArrayList out = new java.util.ArrayList();
  long now = System.currentTimeMillis();
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null || !r.from.equals(from)) continue;
    it.remove();
    if (r.expires > now) out.add(r);
  }}
  return out;
}}""", es))

# ================= HopDispatch (scheduler -> the right world thread, used for retries) =================
hop.addInterface(pool.get("java.lang.Runnable"))
hop.addField(CtField.make(f"public {PKG}.ReadDestTask rd;", hop))
hop.addField(CtField.make(f"public {PKG}.MoveTask mv;", hop))
hop.addConstructor(CtNewConstructor.make(f"""
public HopDispatch({PKG}.ReadDestTask rd, {PKG}.MoveTask mv) {{ this.rd = rd; this.mv = mv; }}""", hop))

# ================= MoveTask (runs on the MOVING player's world thread) =================
mv.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID moverU;", "public java.util.UUID destU;", "public String moverName;", "public String destName;",
          f"public {WLD} destWorld;", f"public {TRF} dest;", f"public {WLD} expected;", "public int attempts;"):
    mv.addField(CtField.make(f, mv))
mv.addConstructor(CtNewConstructor.make(f"""
public MoveTask(java.util.UUID moverU, java.util.UUID destU, String moverName, String destName, {WLD} destWorld, {TRF} dest) {{
  this.moverU = moverU; this.destU = destU; this.moverName = moverName; this.destName = destName;
  this.destWorld = destWorld; this.dest = dest; this.attempts = 0;
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void fail(String why) {{
  {ES}.sayTo(this.moverU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
  {ES}.sayTo(this.destU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void retryLater(String why) {{
  this.attempts++;
  if (this.attempts > 8) {{ fail(why); return; }}
  {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.HopDispatch(null, this), 500L, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void hop() {{
  {PR} m = {ES}.online(this.moverU);
  if (m == null) {{ fail(this.moverName + " went offline."); return; }}
  {WLD} w = {ES}.worldOf(m);
  if (w == null || !w.isAlive()) {{ retryLater(this.moverName + " is changing worlds, try again."); return; }}
  this.expected = w;
  w.execute(this);
}}""", mv))
# InstancesPlugin.teleportPlayerToInstance bookkeeping (bytecode-copied): when entering an instance world from another world,
# store the mover's current world + transform as the return-point override. makeWorldReturnPoint(from, t, false) is private, so
# it is rebuilt here: instanceName/instanceKey only when the FROM world is an instance with RespawnWhenTargeted and a key.
# run() calls it right AFTER addComponent(Teleport) in the same world-thread runnable (the teleport system only runs on the next
# tick, so the override is in place before AddPlayerToWorldEvent; a failed addComponent leaves no stale override behind).
# Same order as vanilla TeleportToPlayerCommand, which does Store.addComponent(Teleport) and THEN ensureAndGet(TeleportHistory).append.
mv.addMethod(CtNewMethod.make(f"""
public void markReturn({ST} st, {REF} ref, {WLD} here, {TC} mtc) {{
  try {{
    if (here == null || this.destWorld == null || here == this.destWorld) return;
    if (mtc == null || mtc.getTransform() == null) return;
    if ({IWC}.get(this.destWorld.getWorldConfig()) == null) return;
    {WCF} hc = here.getWorldConfig();
    if (hc == null || hc.getUuid() == null) return;
    {IWC} hic = {IWC}.get(hc);
    String iname = null;
    String ikey = null;
    if (hic != null && hic.shouldRespawnWhenTargeted() && hic.getInstanceKey() != null) {{
      iname = hic.getInstanceName();
      ikey = hic.getInstanceKey();
    }}
    {WRP} wrp = new {WRP}(hc.getUuid(), new {TRF}(mtc.getTransform()), false, iname, ikey);
    {IEC} iec = ({IEC}) st.ensureAndGetComponent(ref, {IEC}.getComponentType());
    if (iec != null) iec.setReturnPointOverride(wrp);
  }} catch (Throwable t) {{
    {ES}.warn("could not record the instance return point for " + this.moverName + ": " + t);
  }}
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} m = {ES}.online(this.moverU);
    {PR} d = {ES}.online(this.destU);
    if (m == null) {{ fail(this.moverName + " went offline."); return; }}
    if (d == null) {{ fail(this.destName + " went offline."); return; }}
    {REF} ref = m.getReference();
    {WLD} here = {ES}.worldOf(m);
    if (ref == null || here == null || here != this.expected) {{ retryLater(this.moverName + " is changing worlds, try again."); return; }}
    if (this.destWorld == null || !this.destWorld.isAlive()) {{ fail("the destination world is closed."); return; }}
    {ST} st = ref.getStore();
    if (st.getComponent(ref, {TP}.getComponentType()) != null) {{ retryLater(this.moverName + " is already teleporting."); return; }}
    {TC} mtc = ({TC}) st.getComponent(ref, {TC}.getComponentType());
    {HR} mhr = ({HR}) st.getComponent(ref, {HR}.getComponentType());
    st.addComponent(ref, {TP}.getComponentType(), {TP}.createForPlayer(this.destWorld, this.dest));
    markReturn(st, ref, here, mtc);
    try {{
      if (mtc != null && mtc.getPosition() != null) {{
        {V3D} p = mtc.getPosition();
        {R3F} r = mhr != null ? mhr.getRotation() : null;
        {TPH} h = ({TPH}) st.ensureAndGetComponent(ref, {TPH}.getComponentType());
        if (h != null) h.append(here, new {V3D}(p.x, p.y, p.z), r != null ? new {R3F}(r.x, r.y, r.z) : new {R3F}(), "TPA to " + this.destName);
      }}
    }} catch (Throwable t2) {{ }}
    {ES}.say(m, "[TPA] Teleporting to " + this.destName + ".", {ES}.OK);
  }} catch (Throwable t) {{
    {ES}.warn("teleport failed: " + t);
    fail("something went wrong.");
  }}
}}""", mv))

# ================= ReadDestTask (runs on the DESTINATION player's world thread) =================
rd.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID moverU;", "public java.util.UUID destU;", "public String moverName;", "public String destName;",
          f"public {WLD} expected;", "public int attempts;"):
    rd.addField(CtField.make(f, rd))
rd.addConstructor(CtNewConstructor.make("""
public ReadDestTask(java.util.UUID moverU, java.util.UUID destU, String moverName, String destName) {
  this.moverU = moverU; this.destU = destU; this.moverName = moverName; this.destName = destName; this.attempts = 0;
}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void fail(String why) {{
  {ES}.sayTo(this.moverU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
  {ES}.sayTo(this.destU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
}}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void retryLater(String why) {{
  this.attempts++;
  if (this.attempts > 8) {{ fail(why); return; }}
  {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.HopDispatch(this, null), 500L, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void hop() {{
  {PR} d = {ES}.online(this.destU);
  if (d == null) {{ fail(this.destName + " went offline."); return; }}
  {WLD} w = {ES}.worldOf(d);
  if (w == null || !w.isAlive()) {{ retryLater(this.destName + " is changing worlds, try again."); return; }}
  this.expected = w;
  w.execute(this);
}}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} m = {ES}.online(this.moverU);
    {PR} d = {ES}.online(this.destU);
    if (m == null) {{ fail(this.moverName + " went offline."); return; }}
    if (d == null) {{ fail(this.destName + " went offline."); return; }}
    {REF} ref = d.getReference();
    {WLD} here = {ES}.worldOf(d);
    if (ref == null || here == null || here != this.expected) {{ retryLater(this.destName + " is changing worlds, try again."); return; }}
    {ST} st = ref.getStore();
    {TC} tc = ({TC}) st.getComponent(ref, {TC}.getComponentType());
    if (tc == null || tc.getPosition() == null) {{ fail("could not read the position of " + this.destName + "."); return; }}
    {HR} hr = ({HR}) st.getComponent(ref, {HR}.getComponentType());
    {V3D} p = tc.getPosition();
    {R3F} r = hr != null ? hr.getRotation() : null;
    {TRF} tr = new {TRF}(new {V3D}(p.x, p.y, p.z), r != null ? new {R3F}(r.x, r.y, r.z) : new {R3F}());
    new {PKG}.MoveTask(this.moverU, this.destU, this.moverName, this.destName, here, tr).hop();
  }} catch (Throwable t) {{
    {ES}.warn("reading teleport destination failed: " + t);
    fail("something went wrong.");
  }}
}}""", rd))

hop.addMethod(CtNewMethod.make("""
public void run() {
  try {
    if (this.rd != null) this.rd.hop();
    if (this.mv != null) this.mv.hop();
  } catch (Throwable t) { }
}""", hop))

# ================= FlyTask (runs on the player's world thread; mode 1 = on, 0 = off, 2 = re-assert) =================
fly.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID u;", "public int mode;", f"public {WLD} expected;", "public int attempts;"):
    fly.addField(CtField.make(f, fly))
fly.addConstructor(CtNewConstructor.make(f"""
public FlyTask(java.util.UUID u, int mode, {WLD} expected) {{ this.u = u; this.mode = mode; this.expected = expected; this.attempts = 0; }}""", fly))
fly.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {ES}.online(this.u);
    if (pr == null) return;
    {REF} ref = pr.getReference();
    {WLD} here = {ES}.worldOf(pr);
    if (ref == null || here == null || here != this.expected) {{
      if (this.mode != 2 && this.attempts < 3 && here != null) {{ this.attempts++; this.expected = here; here.execute(this); }}
      return;
    }}
    {ST} st = ref.getStore();
    {MM} mm = ({MM}) st.getComponent(ref, {MM}.getComponentType());
    if (mm == null) {{
      if (this.mode != 2) {ES}.say(pr, "[Fly] Could not change your flight right now, try again.", {ES}.ERR);
      return;
    }}
    if (this.mode == 0) {{
      {PLY} p = ({PLY}) st.getComponent(ref, {PLY}.getComponentType());
      {GM} gm = p != null ? p.getGameMode() : {GM}.Adventure;
      if (gm == null) gm = {GM}.Adventure;
      mm.resetFly(gm);
      mm.update(pr.getPacketHandler());
      {ES}.say(pr, "[Fly] Flight disabled." + (gm == {GM}.Creative ? " (Creative mode still lets you fly.)" : ""), {ES}.INFO);
      return;
    }}
    if (this.mode == 2 && !{ES}.FLY.containsKey(this.u)) return;
    {MS} s = mm.getSettings();
    {MS} d = mm.getDefaultSettings();
    boolean changed = false;
    if (s != null && s.fly != {FM}.Allowed && s.fly != {FM}.Forced) {{ s.fly = {FM}.Allowed; changed = true; }}
    if (d != null && d.fly != {FM}.Allowed && d.fly != {FM}.Forced) {{ d.fly = {FM}.Allowed; }}
    if (changed || this.mode == 1) mm.update(pr.getPacketHandler());
    if (this.mode == 1) {ES}.say(pr, "[Fly] Flight enabled - take off the same way as in creative. /fly again to turn it off.", {ES}.OK);
  }} catch (Throwable t) {{ {ES}.warn("fly task failed: " + t); }}
}}""", fly))

# ================= EssStore: prune + request actions (need the task classes above) =================
es.addMethod(CtNewMethod.make(f"""
public static synchronized void prune() {{
  long now = System.currentTimeMillis();
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null) {{ it.remove(); continue; }}
    {PR} f = online(r.from);
    {PR} t = online(r.to);
    if (f == null || t == null) {{
      it.remove();
      if (f != null) say(f, "[TPA] " + r.toName + " went offline, your teleport request was cancelled.", INFO);
      if (t != null) say(t, "[TPA] " + r.fromName + " went offline, their teleport request was cancelled.", INFO);
    }} else if (r.expires <= now) {{
      it.remove();
      say(f, "[TPA] Your teleport request to " + r.toName + " expired.", INFO);
      say(t, "[TPA] The teleport request from " + r.fromName + " expired.", INFO);
    }}
  }}
  it = LAST_SENT.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Long v = (Long) e.getValue();
    if (v == null || now - v.longValue() >= COOLDOWN_MS || online((java.util.UUID) e.getKey()) == null) it.remove();
  }}
  it = LAST_PM.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (online((java.util.UUID) e.getKey()) == null || online((java.util.UUID) e.getValue()) == null) it.remove();
  }}
  it = FLY.keySet().iterator();
  while (it.hasNext()) {{
    java.util.UUID u = (java.util.UUID) it.next();
    {PR} p = online(u);
    if (p == null) {{ it.remove(); continue; }}
    boolean allowed = true;
    try {{ allowed = p.hasPermission(FLY_PERM); }} catch (Throwable t2) {{ }}
    if (!allowed) {{
      it.remove();
      {WLD} w = worldOf(p);
      if (w != null && w.isAlive()) w.execute(new {PKG}.FlyTask(u, 0, w));
    }}
  }}
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void request({PR} pr, Object t, boolean here) {{
  String cmd = here ? "/tpahere" : "/tpa";
  if (!(t instanceof {PR})) {{ say(pr, "[TPA] Usage: " + cmd + " <player>", ERR); return; }}
  {PR} target = ({PR}) t;
  if (target.getUuid().equals(pr.getUuid())) {{ say(pr, "[TPA] You can't send a teleport request to yourself.", ERR); return; }}
  if (online(target.getUuid()) == null) {{ say(pr, "[TPA] " + target.getUsername() + " is not online.", ERR); return; }}
  String me = pr.getUsername();
  String them = target.getUsername();
  String err = tryAdd(pr.getUuid(), target.getUuid(), here, me, them);
  if (err != null) {{ say(pr, "[TPA] " + err, ERR); return; }}
  if (here) {{
    say(pr, "[TPA] Asked " + them + " to teleport to you. They have 60s to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + me + " wants you to teleport to them. /tpaccept " + me + " to go, /tpdeny " + me + " to refuse (60s).", INFO);
  }} else {{
    say(pr, "[TPA] Request sent to " + them + ". They have 60s to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + me + " wants to teleport to you. /tpaccept " + me + " to allow, /tpdeny " + me + " to refuse (60s).", INFO);
  }}
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void accept({PR} pr, java.util.UUID from) {{
  {PKG}.TpReq r = take(pr.getUuid(), from);
  if (r == null) {{
    say(pr, from == null ? "[TPA] You have no pending teleport requests." : "[TPA] No pending teleport request from that player.", ERR);
    return;
  }}
  {PR} req = online(r.from);
  if (req == null) {{ say(pr, "[TPA] " + r.fromName + " is no longer online.", ERR); return; }}
  java.util.UUID moverU = r.here ? r.to : r.from;
  java.util.UUID destU = r.here ? r.from : r.to;
  String moverName = r.here ? pr.getUsername() : req.getUsername();
  String destName = r.here ? req.getUsername() : pr.getUsername();
  if (r.here) {{
    say(pr, "[TPA] Accepted. Teleporting you to " + destName + "...", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted and is teleporting to you.", OK);
  }} else {{
    say(pr, "[TPA] Accepted. " + moverName + " is teleporting to you.", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted your request. Teleporting...", OK);
  }}
  int left = pendingFor(pr.getUuid());
  if (left > 0) say(pr, "[TPA] You still have " + left + " pending request(s). /tpaccept <player> or /tpdeny <player>.", INFO);
  new {PKG}.ReadDestTask(moverU, destU, moverName, destName).hop();
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void deny({PR} pr, java.util.UUID from) {{
  {PKG}.TpReq r = take(pr.getUuid(), from);
  if (r == null) {{
    say(pr, from == null ? "[TPA] You have no pending teleport requests." : "[TPA] No pending teleport request from that player.", ERR);
    return;
  }}
  say(pr, "[TPA] Denied the teleport request from " + r.fromName + ".", INFO);
  sayTo(r.from, "[TPA] " + pr.getUsername() + " denied your teleport request.", ERR);
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void pm({PR} pr, {PR} target, String text) {{
  if (text == null) text = "";
  text = text.trim();
  if (text.length() == 0) {{ say(pr, "Usage: /msg <player> <message>", ERR); return; }}
  if (target == null || online(target.getUuid()) == null) {{ say(pr, "That player is not online.", ERR); return; }}
  if (target.getUuid().equals(pr.getUuid())) {{ say(pr, "You can't message yourself.", ERR); return; }}
  say(pr, "[you -> " + target.getUsername() + "] " + text, PM);
  say(target, "[" + pr.getUsername() + " -> you] " + text, PM);
  LAST_PM.put(pr.getUuid(), target.getUuid());
  LAST_PM.put(target.getUuid(), pr.getUuid());
}}""", es))

# ================= EssTick (scheduler, every 2s: fly re-assert; every 10s: prune) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make("public int n;", tick))
tick.addConstructor(CtNewConstructor.make("public EssTick() { this.n = 0; }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    this.n++;
    java.util.Iterator it = {ES}.FLY.keySet().iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      {PR} p = {ES}.online(u);
      if (p == null) continue;
      {WLD} w = {ES}.worldOf(p);
      if (w != null && w.isAlive()) w.execute(new {PKG}.FlyTask(u, 2, w));
    }}
    if (this.n % 5 == 0) {ES}.prune();
  }} catch (Throwable t) {{ {ES}.warn("tick failed: " + t); }}
}}""", tick))

# ================= commands =================
def player_cmd(cls, ctor_src, body):
    cls.addConstructor(CtNewConstructor.make(ctor_src, cls))
    cls.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
{body}
  }} catch (Throwable t) {{
    {ES}.warn("{cls.getSimpleName()} failed: " + t);
    {ES}.say(pr, "Something went wrong with that command.", {ES}.ERR);
  }}
}}""", cls))

# /tpa <player>
tpa.addField(CtField.make(f"public {RA} targetArg;", tpa))
player_cmd(tpa, f"""
public TpaCmd() {{
  super("tpa", "Ask a player if you may teleport to them");
  this.targetArg = withRequiredArg("player", "Player to teleport to", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"    {ES}.request(pr, ctx.get(this.targetArg), false);")
# /tpahere <player>
tph.addField(CtField.make(f"public {RA} targetArg;", tph))
player_cmd(tph, f"""
public TpaHereCmd() {{
  super("tpahere", "Ask a player to teleport to you");
  this.targetArg = withRequiredArg("player", "Player to bring to you", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"    {ES}.request(pr, ctx.get(this.targetArg), true);")
# /tpaccept <player> (usage variant, description-only constructor like vanilla WhereAmIOtherCommand)
tacn.addField(CtField.make(f"public {RA} fromArg;", tacn))
player_cmd(tacn, f"""
public TpAcceptNamedCmd() {{
  super("Accept the teleport request from this player");
  this.fromArg = withRequiredArg("player", "Player whose request to accept", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"""    Object t = ctx.get(this.fromArg);
    if (!(t instanceof {PR})) {{ {ES}.say(pr, "[TPA] Usage: /tpaccept [player]", {ES}.ERR); return; }}
    {ES}.accept(pr, (({PR}) t).getUuid());""")
player_cmd(tac, f"""
public TpAcceptCmd() {{
  super("tpaccept", "Accept a teleport request (newest, or /tpaccept <player>)");
  {ADV}
  addUsageVariant(new {PKG}.TpAcceptNamedCmd());
}}""", f"    {ES}.accept(pr, null);")
# /tpdeny [player]
tdnn.addField(CtField.make(f"public {RA} fromArg;", tdnn))
player_cmd(tdnn, f"""
public TpDenyNamedCmd() {{
  super("Deny the teleport request from this player");
  this.fromArg = withRequiredArg("player", "Player whose request to deny", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"""    Object t = ctx.get(this.fromArg);
    if (!(t instanceof {PR})) {{ {ES}.say(pr, "[TPA] Usage: /tpdeny [player]", {ES}.ERR); return; }}
    {ES}.deny(pr, (({PR}) t).getUuid());""")
player_cmd(tdn, f"""
public TpDenyCmd() {{
  super("tpdeny", "Deny a teleport request (newest, or /tpdeny <player>)");
  {ADV}
  addUsageVariant(new {PKG}.TpDenyNamedCmd());
}}""", f"    {ES}.deny(pr, null);")
# /tpacancel
player_cmd(tcan, f"""
public TpaCancelCmd() {{
  super("tpacancel", "Cancel your outgoing teleport requests");
  {ADV}
}}""", f"""    java.util.List l = {ES}.cancelFrom(pr.getUuid());
    if (l.isEmpty()) {{ {ES}.say(pr, "[TPA] You have no outgoing teleport requests.", {ES}.INFO); return; }}
    for (int i = 0; i < l.size(); i++) {{
      {PKG}.TpReq r = ({PKG}.TpReq) l.get(i);
      {ES}.sayTo(r.to, "[TPA] " + pr.getUsername() + " cancelled their teleport request.", {ES}.INFO);
    }}
    {ES}.say(pr, "[TPA] Cancelled " + l.size() + " teleport request(s).", {ES}.INFO);""")
# /msg <player> <message>  (aliases tell, w, whisper - none used by vanilla)
msg.addField(CtField.make(f"public {RA} targetArg;", msg))
msg.addField(CtField.make(f"public {RA} textArg;", msg))
player_cmd(msg, f"""
public MsgCmd() {{
  super("msg", "Send a private message to a player");
  this.targetArg = withRequiredArg("player", "Who to message", {ATY}.PLAYER_REF);
  this.textArg = withRequiredArg("message", "Your message", {ATY}.GREEDY_STRING);
  addAliases(new String[] {{ "tell", "w", "whisper" }});
  {ADV}
}}""", f"""    Object t = ctx.get(this.targetArg);
    Object m = ctx.get(this.textArg);
    if (!(t instanceof {PR})) {{ {ES}.say(pr, "Usage: /msg <player> <message>", {ES}.ERR); return; }}
    {ES}.pm(pr, ({PR}) t, m == null ? "" : m.toString());""")
# /reply <message>   (/r is vanilla's /redo alias, so reply has no short alias)
rep.addField(CtField.make(f"public {RA} textArg;", rep))
player_cmd(rep, f"""
public ReplyCmd() {{
  super("reply", "Reply to the last player you messaged or who messaged you");
  this.textArg = withRequiredArg("message", "Your message", {ATY}.GREEDY_STRING);
  {ADV}
}}""", f"""    java.util.UUID partner = (java.util.UUID) {ES}.LAST_PM.get(pr.getUuid());
    if (partner == null) {{ {ES}.say(pr, "Nobody to reply to yet. Use /msg <player> <message>.", {ES}.ERR); return; }}
    {PR} target = {ES}.online(partner);
    if (target == null) {{ {ES}.LAST_PM.remove(pr.getUuid()); {ES}.say(pr, "The player you were talking to is no longer online.", {ES}.ERR); return; }}
    Object m = ctx.get(this.textArg);
    {ES}.pm(pr, target, m == null ? "" : m.toString());""")
# /fly (admin)
player_cmd(flc, f"""
public FlyCmd() {{
  super("fly", "Toggle flight (admin)");
  requirePermission("skyyessentials.fly");
}}""", f"""    java.util.UUID u = pr.getUuid();
    if ({ES}.FLY.remove(u) != null) {{
      new {PKG}.FlyTask(u, 0, world).run();
    }} else {{
      {ES}.FLY.put(u, Boolean.TRUE);
      new {PKG}.FlyTask(u, 1, world).run();
    }}""")

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyEssentialsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {ES}.LOG = getLogger();
  getCommandRegistry().registerCommand(new {PKG}.TpaCmd());
  getCommandRegistry().registerCommand(new {PKG}.TpaHereCmd());
  getCommandRegistry().registerCommand(new {PKG}.TpAcceptCmd());
  getCommandRegistry().registerCommand(new {PKG}.TpDenyCmd());
  getCommandRegistry().registerCommand(new {PKG}.TpaCancelCmd());
  getCommandRegistry().registerCommand(new {PKG}.MsgCmd());
  getCommandRegistry().registerCommand(new {PKG}.ReplyCmd());
  getCommandRegistry().registerCommand(new {PKG}.FlyCmd());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.EssTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyEssentials] {VERSION} ready - /tpa /tpahere /tpaccept /tpdeny /tpacancel /msg (tell, w, whisper) /reply /fly");
}}""", pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (rq, es, hop, mv, rd, fly, tick, tpa, tph, tacn, tac, tdnn, tdn, tcan, msg, rep, flc, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)
m = B.manifest("SkyyEssentials", VERSION, "SkyWynn essentials, only what vanilla lacks: /tpa /tpahere /tpaccept /tpdeny /tpacancel (cross-world, 60s expiry), /msg /reply private messages, admin /fly. Zero dependencies.", PKG + ".SkyyEssentialsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyEssentials.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyEssentials" % VERSION, disable_prefix="Skyy:")
