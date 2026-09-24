"""SkyyParty 0.1.1 - build script (javassist via jpype).
Run:   python build_skyyparty_0.1.1.py            -> SkyyParty/SkyyParty-0.1.1.jar
       python build_skyyparty_0.1.1.py --deploy   -> also copies to Mods/SkyyParty.jar and enables it in the HUD mod world
Fixes vs 0.1 (code review 2026-09-22): synchronized party store (no lost members on concurrent accept),
accept refuses when already in a party, leader leaving promotes the next member instead of disbanding,
players are removed from their party on disconnect, expired invites are pruned, direct Universe.getPlayer
lookup, no exception text leaked to chat. Still in-memory only (by design; feeds the future HUD widget + map).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.1"
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
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"
LOG = "com.hypixel.hytale.logger.HytaleLogger"

for c, m in ((UNI, "getPlayer"), (PDE, "getPlayerRef"), (HSV, "SCHEDULED_EXECUTOR"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

PKG = "com.skyy.party"
ps   = pool.makeClass(PKG + ".PartyStore")
root = pool.makeClass(PKG + ".PartyCmd", pool.get(APC))
inv  = pool.makeClass(PKG + ".InviteCmd", pool.get(APC))
acc  = pool.makeClass(PKG + ".AcceptCmd", pool.get(APC))
lev  = pool.makeClass(PKG + ".LeaveCmd", pool.get(APC))
lst  = pool.makeClass(PKG + ".ListCmd", pool.get(APC))
pc   = pool.makeClass(PKG + ".PartyChatCmd", pool.get(APC))
quit_ = pool.makeClass(PKG + ".PartyQuit")
prune = pool.makeClass(PKG + ".PartyPrune")
pl   = pool.makeClass(PKG + ".SkyyPartyPlugin", pool.get(JP))

# ================= PartyStore (in-memory; THE data feed for future map + HUD widget) =================
ps.addField(CtField.make(f"public static {LOG} LOG;", ps))
ps.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PARTY_OF = new java.util.concurrent.ConcurrentHashMap();", ps))   # uuid -> party leader uuid
ps.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MEMBERS = new java.util.concurrent.ConcurrentHashMap();", ps))    # leader uuid -> Set<uuid>
ps.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap INVITES = new java.util.concurrent.ConcurrentHashMap();", ps))    # invitee -> Object[]{inviter uuid, Long expiryMs}
ps.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyParty] " + msg); } catch (Throwable t) { }
}""", ps))
ps.addMethod(CtNewMethod.make("""
public static java.util.UUID leaderOf(java.util.UUID anyMember) {
  return (java.util.UUID) PARTY_OF.get(anyMember);
}""", ps))
ps.addMethod(CtNewMethod.make("""
public static java.util.Set membersOf(java.util.UUID anyMember) {
  java.util.UUID leader = (java.util.UUID) PARTY_OF.get(anyMember);
  if (leader == null) return null;
  return (java.util.Set) MEMBERS.get(leader);
}""", ps))
ps.addMethod(CtNewMethod.make("""
public static synchronized boolean joinParty(java.util.UUID leader, java.util.UUID member) {
  if (PARTY_OF.containsKey(member)) return false;
  java.util.UUID realLeader = (java.util.UUID) PARTY_OF.get(leader);
  if (realLeader != null) leader = realLeader;
  java.util.Set s = (java.util.Set) MEMBERS.get(leader);
  if (s == null) {
    s = java.util.concurrent.ConcurrentHashMap.newKeySet();
    s.add(leader);
    MEMBERS.put(leader, s);
    PARTY_OF.put(leader, leader);
  }
  s.add(member);
  PARTY_OF.put(member, leader);
  return true;
}""", ps))
# returns: null = party dissolved or member not in a party; otherwise the (possibly new) leader uuid
ps.addMethod(CtNewMethod.make("""
public static synchronized java.util.UUID leave(java.util.UUID member) {
  java.util.UUID leader = (java.util.UUID) PARTY_OF.remove(member);
  if (leader == null) return null;
  java.util.Set s = (java.util.Set) MEMBERS.get(leader);
  if (s == null) return null;
  s.remove(member);
  if (s.size() <= 1) {
    java.util.Iterator it = s.iterator();
    while (it.hasNext()) PARTY_OF.remove(it.next());
    MEMBERS.remove(leader);
    return null;
  }
  if (member.equals(leader)) {
    java.util.Iterator it = s.iterator();
    java.util.UUID newLeader = (java.util.UUID) it.next();
    MEMBERS.remove(leader);
    MEMBERS.put(newLeader, s);
    java.util.Iterator it2 = s.iterator();
    while (it2.hasNext()) PARTY_OF.put(it2.next(), newLeader);
    return newLeader;
  }
  return leader;
}""", ps))
ps.addMethod(CtNewMethod.make("""
public static void pruneInvites() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = INVITES.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (v == null || ((Long) v[1]).longValue() < now) it.remove();
  }
}""", ps))
ps.addMethod(CtNewMethod.make(f"""
public static {PR} online(java.util.UUID u) {{
  {PR} p = {UNI}.get().getPlayer(u);
  return (p != null && p.isValid()) ? p : null;
}}""", ps))
ps.addMethod(CtNewMethod.make(f"""
public static void broadcastTo(java.util.Set s, String msg) {{
  java.util.Iterator it = s.iterator();
  while (it.hasNext()) {{
    {PR} p = online((java.util.UUID) it.next());
    if (p != null) p.sendMessage({MSG}.raw(msg));
  }}
}}""", ps))

ps.addMethod(CtNewMethod.make(f"""
public static void broadcast(java.util.UUID anyMember, String msg) {{
  java.util.Set s = membersOf(anyMember);
  if (s == null) return;
  broadcastTo(s, msg);
}}""", ps))
# ================= commands =================
inv.addField(CtField.make(f"public {RA} targetArg;", inv))
inv.addConstructor(CtNewConstructor.make(f"""
public InviteCmd() {{
  super("invite", "Invite a player to your party");
  this.targetArg = withRequiredArg("player", "Player to invite", {ATY}.PLAYER_REF);
}}""", inv))
inv.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object t = ctx.get(this.targetArg);
    if (t == null) {{ pr.sendMessage({MSG}.raw("Usage: /party invite <player>")); return; }}
    {PR} target = ({PR}) t;
    if (target.getUuid().equals(pr.getUuid())) {{ pr.sendMessage({MSG}.raw("You can't invite yourself.")); return; }}
    if (!target.isValid()) {{ pr.sendMessage({MSG}.raw("That player is not online.")); return; }}
    if ({PKG}.PartyStore.PARTY_OF.containsKey(target.getUuid())) {{ pr.sendMessage({MSG}.raw(target.getUsername() + " is already in a party.")); return; }}
    {PKG}.PartyStore.INVITES.put(target.getUuid(), new Object[] {{ pr.getUuid(), Long.valueOf(System.currentTimeMillis() + 60000L) }});
    pr.sendMessage({MSG}.raw("Invited " + target.getUsername() + " to your party (60s)."));
    target.sendMessage({MSG}.raw(pr.getUsername() + " invited you to a party! /party accept within 60s."));
  }} catch (Throwable t2) {{ {PKG}.PartyStore.warn("invite failed: " + t2); pr.sendMessage({MSG}.raw("Invite failed.")); }}
}}""", inv))

acc.addConstructor(CtNewConstructor.make('public AcceptCmd() { super("accept", "Accept a party invite"); }', acc))
acc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if ({PKG}.PartyStore.PARTY_OF.containsKey(pr.getUuid())) {{ pr.sendMessage({MSG}.raw("Leave your current party first (/party leave).")); return; }}
    Object[] invd = (Object[]) {PKG}.PartyStore.INVITES.remove(pr.getUuid());
    if (invd == null || ((Long) invd[1]).longValue() < System.currentTimeMillis()) {{
      pr.sendMessage({MSG}.raw("No active party invite.")); return;
    }}
    java.util.UUID inviter = (java.util.UUID) invd[0];
    if ({PKG}.PartyStore.online(inviter) == null) {{ pr.sendMessage({MSG}.raw("The player who invited you is no longer online.")); return; }}
    if (!{PKG}.PartyStore.joinParty(inviter, pr.getUuid())) {{ pr.sendMessage({MSG}.raw("Could not join the party.")); return; }}
    {PKG}.PartyStore.broadcast(pr.getUuid(), pr.getUsername() + " joined the party!");
  }} catch (Throwable t2) {{ {PKG}.PartyStore.warn("accept failed: " + t2); pr.sendMessage({MSG}.raw("Accept failed.")); }}
}}""", acc))

lev.addConstructor(CtNewConstructor.make('public LeaveCmd() { super("leave", "Leave your party"); }', lev))
lev.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    java.util.Set s = {PKG}.PartyStore.membersOf(pr.getUuid());
    if (s == null) {{ pr.sendMessage({MSG}.raw("You're not in a party.")); return; }}
    java.util.UUID oldLeader = {PKG}.PartyStore.leaderOf(pr.getUuid());
    java.util.UUID newLeader = {PKG}.PartyStore.leave(pr.getUuid());
    pr.sendMessage({MSG}.raw("You left the party."));
    if (newLeader == null) {{
      {PKG}.PartyStore.broadcastTo(s, pr.getUsername() + " left. The party has been disbanded.");
    }} else {{
      {PKG}.PartyStore.broadcastTo(s, pr.getUsername() + " left the party.");
      if (!newLeader.equals(oldLeader)) {{
        {PR} nl = {PKG}.PartyStore.online(newLeader);
        {PKG}.PartyStore.broadcastTo(s, (nl != null ? nl.getUsername() : "A member") + " is now the party leader.");
      }}
    }}
  }} catch (Throwable t2) {{ {PKG}.PartyStore.warn("leave failed: " + t2); }}
}}""", lev))

lst.addConstructor(CtNewConstructor.make('public ListCmd() { super("list", "List party members"); }', lst))
lst.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.Set s = {PKG}.PartyStore.membersOf(pr.getUuid());
  if (s == null) {{ pr.sendMessage({MSG}.raw("You're not in a party. /party invite <player> to start one.")); return; }}
  java.util.UUID leader = {PKG}.PartyStore.leaderOf(pr.getUuid());
  StringBuilder sb = new StringBuilder("Party (" + s.size() + "): ");
  java.util.Iterator it = s.iterator();
  boolean first = true;
  while (it.hasNext()) {{
    java.util.UUID u = (java.util.UUID) it.next();
    {PR} p = {PKG}.PartyStore.online(u);
    if (!first) sb.append(", ");
    sb.append(p != null ? p.getUsername() : "(offline)");
    if (u.equals(leader)) sb.append(" [leader]");
    first = false;
  }}
  pr.sendMessage({MSG}.raw(sb.toString()));
}}""", lst))

pc.addField(CtField.make(f"public {RA} msgArg;", pc))
pc.addConstructor(CtNewConstructor.make(f"""
public PartyChatCmd() {{
  super("pc", "Party chat");
  this.msgArg = withRequiredArg("message", "Message to your party", {ATY}.GREEDY_STRING);
}}""", pc))
pc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  Object m = ctx.get(this.msgArg);
  if (m == null) return;
  if ({PKG}.PartyStore.membersOf(pr.getUuid()) == null) {{ pr.sendMessage({MSG}.raw("You're not in a party.")); return; }}
  {PKG}.PartyStore.broadcast(pr.getUuid(), "[Party] " + pr.getUsername() + ": " + m.toString());
}}""", pc))

root.addConstructor(CtNewConstructor.make(f"""
public PartyCmd() {{
  super("party", "Party commands");
  addAliases(new String[] {{ "p" }});
  addSubCommand(new {PKG}.InviteCmd());
  addSubCommand(new {PKG}.AcceptCmd());
  addSubCommand(new {PKG}.LeaveCmd());
  addSubCommand(new {PKG}.ListCmd());
}}""", root))
root.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  pr.sendMessage({MSG}.raw("Party: /party invite <player> - /party accept - /party leave - /party list - /pc <msg>"));
}}""", root))

# ================= disconnect cleanup + invite pruning =================
quit_.addInterface(pool.get("java.util.function.Consumer"))
quit_.addConstructor(CtNewConstructor.make("public PartyQuit() { }", quit_))
quit_.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    {PR} pr = (({PDE}) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    {PKG}.PartyStore.INVITES.remove(u);
    java.util.Set s = {PKG}.PartyStore.membersOf(u);
    if (s == null) return;
    java.util.UUID oldLeader = {PKG}.PartyStore.leaderOf(u);
    java.util.UUID newLeader = {PKG}.PartyStore.leave(u);
    String name = pr.getUsername();
    if (newLeader == null) {PKG}.PartyStore.broadcastTo(s, name + " disconnected. The party has been disbanded.");
    else {{
      {PKG}.PartyStore.broadcastTo(s, name + " disconnected and left the party.");
      if (!newLeader.equals(oldLeader)) {{
        {PR} nl = {PKG}.PartyStore.online(newLeader);
        {PKG}.PartyStore.broadcastTo(s, (nl != null ? nl.getUsername() : "A member") + " is now the party leader.");
      }}
    }}
  }} catch (Throwable t) {{ {PKG}.PartyStore.warn("disconnect cleanup failed: " + t); }}
}}""", quit_))

prune.addInterface(pool.get("java.lang.Runnable"))
prune.addConstructor(CtNewConstructor.make("public PartyPrune() { }", prune))
prune.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.PartyStore.pruneInvites(); }} catch (Throwable t) {{ }}
}}""", prune))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture pruner;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyPartyPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.PartyStore.LOG = getLogger();
  getCommandRegistry().registerCommand(new {PKG}.PartyCmd());
  getCommandRegistry().registerCommand(new {PKG}.PartyChatCmd());
  getEventRegistry().registerGlobal({PDE}.class, new {PKG}.PartyQuit());
  this.pruner = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.PartyPrune(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyParty] {VERSION} ready - /party invite|accept|leave|list, /pc");
}}""", pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.pruner != null) this.pruner.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (ps, inv, acc, lev, lst, pc, root, quit_, prune, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyParty-%s.jar" % VERSION)
m = B.manifest("SkyyParty", VERSION, "SkyWynn party system: invites, party chat, member list, leader handoff. Built as the data feed for the future map + party HUD widget. Zero dependencies.", PKG + ".SkyyPartyPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyParty.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyParty" % VERSION, disable_prefix="Skyy:")
