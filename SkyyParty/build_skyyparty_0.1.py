import jpype, sys, os, zipfile, json
from jdk4py import JAVA_HOME
jpype.startJVM(str(JAVA_HOME/"lib"/"server"/"libjvm.so"), "--add-opens=java.base/java.lang=ALL-UNNAMED", classpath=["/tmp/javassist/javassist.jar"])
J = jpype.JClass
ClassPool, CtField, CtNewMethod, CtNewConstructor = J("javassist.ClassPool"), J("javassist.CtField"), J("javassist.CtNewMethod"), J("javassist.CtNewConstructor")
REL = sys.argv[1]
pool = ClassPool(False); pool.appendSystemPath(); pool.appendClassPath(REL)
OUT = "/tmp/skyyparty_classes"; os.system(f"rm -rf {OUT}"); os.makedirs(OUT)

JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"

PKG = "com.skyy.party"
ps   = pool.makeClass(PKG + ".PartyStore")
root = pool.makeClass(PKG + ".PartyCmd", pool.get(APC))
inv  = pool.makeClass(PKG + ".InviteCmd", pool.get(APC))
acc  = pool.makeClass(PKG + ".AcceptCmd", pool.get(APC))
lev  = pool.makeClass(PKG + ".LeaveCmd", pool.get(APC))
lst  = pool.makeClass(PKG + ".ListCmd", pool.get(APC))
pc   = pool.makeClass(PKG + ".PartyChatCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyPartyPlugin", pool.get(JP))

# ================= PartyStore (in-memory; THE data feed for future map + HUD widget) =================
ps.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PARTY_OF = new java.util.concurrent.ConcurrentHashMap();", ps))   # uuid -> party leader uuid
ps.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MEMBERS = new java.util.concurrent.ConcurrentHashMap();", ps))    # leader uuid -> Set<uuid>
ps.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap INVITES = new java.util.concurrent.ConcurrentHashMap();", ps))    # invitee -> [inviter, expiryMs]
ps.addMethod(CtNewMethod.make("""
public static java.util.Set membersOf(java.util.UUID anyMember) {
  java.util.UUID leader = (java.util.UUID) PARTY_OF.get(anyMember);
  if (leader == null) return null;
  return (java.util.Set) MEMBERS.get(leader);
}""", ps))
ps.addMethod(CtNewMethod.make("""
public static void joinParty(java.util.UUID leader, java.util.UUID member) {
  java.util.Set s = (java.util.Set) MEMBERS.get(leader);
  if (s == null) {
    s = java.util.concurrent.ConcurrentHashMap.newKeySet();
    s.add(leader);
    MEMBERS.put(leader, s);
    PARTY_OF.put(leader, leader);
  }
  s.add(member);
  PARTY_OF.put(member, leader);
}""", ps))
ps.addMethod(CtNewMethod.make("""
public static void leave(java.util.UUID member) {
  java.util.UUID leader = (java.util.UUID) PARTY_OF.remove(member);
  if (leader == null) return;
  java.util.Set s = (java.util.Set) MEMBERS.get(leader);
  if (s == null) return;
  s.remove(member);
  if (member.equals(leader) || s.size() <= 1) {
    java.util.Iterator it = s.iterator();
    while (it.hasNext()) PARTY_OF.remove(it.next());
    MEMBERS.remove(leader);
  }
}""", ps))
ps.addMethod(CtNewMethod.make(f"""
public static {PR} online(java.util.UUID u) {{
  java.util.Iterator it = {UNI}.get().getPlayers().iterator();
  while (it.hasNext()) {{
    {PR} p = ({PR}) it.next();
    if (p != null && p.isValid() && u.equals(p.getUuid())) return p;
  }}
  return null;
}}""", ps))
ps.addMethod(CtNewMethod.make(f"""
public static void broadcast(java.util.UUID anyMember, String msg) {{
  java.util.Set s = membersOf(anyMember);
  if (s == null) return;
  java.util.Iterator it = s.iterator();
  while (it.hasNext()) {{
    {PR} p = online((java.util.UUID) it.next());
    if (p != null) p.sendMessage({MSG}.raw(msg));
  }}
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
    if (t == null) return;
    {PR} target = ({PR}) t;
    if (target.getUuid().equals(pr.getUuid())) {{ pr.sendMessage({MSG}.raw("You can't invite yourself.")); return; }}
    if ({PKG}.PartyStore.PARTY_OF.containsKey(target.getUuid())) {{ pr.sendMessage({MSG}.raw(target.getUsername() + " is already in a party.")); return; }}
    {PKG}.PartyStore.INVITES.put(target.getUuid(), new Object[] {{ pr.getUuid(), Long.valueOf(System.currentTimeMillis() + 60000L) }});
    pr.sendMessage({MSG}.raw("Invited " + target.getUsername() + " to your party (60s)."));
    target.sendMessage({MSG}.raw(pr.getUsername() + " invited you to a party! /party accept within 60s."));
  }} catch (Throwable t2) {{ pr.sendMessage({MSG}.raw("Invite failed: " + t2)); }}
}}""", inv))

acc.addConstructor(CtNewConstructor.make('public AcceptCmd() { super("accept", "Accept a party invite"); }', acc))
acc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  Object[] invd = (Object[]) {PKG}.PartyStore.INVITES.remove(pr.getUuid());
  if (invd == null || ((Long) invd[1]).longValue() < System.currentTimeMillis()) {{
    pr.sendMessage({MSG}.raw("No active party invite.")); return;
  }}
  java.util.UUID inviter = (java.util.UUID) invd[0];
  java.util.UUID leader = (java.util.UUID) {PKG}.PartyStore.PARTY_OF.get(inviter);
  if (leader == null) leader = inviter;
  {PKG}.PartyStore.joinParty(leader, pr.getUuid());
  {PKG}.PartyStore.broadcast(pr.getUuid(), pr.getUsername() + " joined the party!");
}}""", acc))

lev.addConstructor(CtNewConstructor.make('public LeaveCmd() { super("leave", "Leave your party"); }', lev))
lev.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  if (!{PKG}.PartyStore.PARTY_OF.containsKey(pr.getUuid())) {{ pr.sendMessage({MSG}.raw("You're not in a party.")); return; }}
  {PKG}.PartyStore.broadcast(pr.getUuid(), pr.getUsername() + " left the party.");
  {PKG}.PartyStore.leave(pr.getUuid());
  pr.sendMessage({MSG}.raw("You left the party."));
}}""", lev))

lst.addConstructor(CtNewConstructor.make('public ListCmd() { super("list", "List party members"); }', lst))
lst.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.Set s = {PKG}.PartyStore.membersOf(pr.getUuid());
  if (s == null) {{ pr.sendMessage({MSG}.raw("You're not in a party. /party invite <player> to start one.")); return; }}
  StringBuilder sb = new StringBuilder("Party (" + s.size() + "): ");
  java.util.Iterator it = s.iterator();
  boolean first = true;
  while (it.hasNext()) {{
    java.util.UUID u = (java.util.UUID) it.next();
    {PR} p = {PKG}.PartyStore.online(u);
    if (!first) sb.append(", ");
    sb.append(p != null ? p.getUsername() : "(offline)");
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

pl.addConstructor(CtNewConstructor.make(f"public SkyyPartyPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  getCommandRegistry().registerCommand(new {PKG}.PartyCmd());
  getCommandRegistry().registerCommand(new {PKG}.PartyChatCmd());
  getLogger().at(java.util.logging.Level.WARNING).log("[SkyyParty] 0.1 ready - /party invite|accept|leave|list, /pc");
}}""", pl))

for c in (ps, inv, acc, lev, lst, pc, root, pl): c.writeFile(OUT)
print("classes written")

manifest = {
  "Group": "Skyy", "Name": "0.1 SkyyParty", "Version": "0.1.0",
  "Description": "SkyWynn party system: invites, party chat, member list. Built as the data feed for the future map + party HUD widget. Zero dependencies.",
  "Authors": [{"Name": "Skyy"}], "ServerVersion": "*", "DisabledByDefault": False,
  "IncludesAssetPack": False, "Main": "com.skyy.party.SkyyPartyPlugin"
}
with zipfile.ZipFile("/tmp/SkyyParty.jar", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2))
    for root2, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(".class"):
                full = os.path.join(root2, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
print("assembled", os.path.getsize("/tmp/SkyyParty.jar"))
