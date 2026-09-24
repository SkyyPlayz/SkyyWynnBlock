"""Derive SkyyCollections/build_skyycollections_0.1.4.py from 0.1.3 (0.1.3 is left untouched; CRLF line endings preserved).
0.1.4 = the two COMMAND RULES (HANDOFF, verified against HytaleServer.jar 2026-09-23):
  1. /collections (alias /coll) gets setPermissionGroups({"hytale:Adventurer"}) so ordinary players can run it (before, the
     auto node skyy_0.1.3_skyycollections.command.collections was only held by "*" admins).
  2. Optional args are not positional, so "/collections unlocks" and "/collections reload" failed with
     wrongNumberRequiredParameters. They are now real SUBCOMMANDS:
       unlocks (alias recipes)  -> CollUnlocksCmd, Adventurer group
       reload                   -> CollReloadCmd, requirePermission("skyycollections.admin") + setPermissionGroups(new String[0])
     The empty group list on reload is REQUIRED: AbstractCommand.putRecursivePermissionGroups gives a subcommand with a null
     permissionGroups its PARENT's groups and adds the subcommand's permission id to them, so without it every Adventurer would be
     granted "skyycollections.admin" through the virtual group.
  The old "--action unlocks|reload" flag keeps working (root optional arg, 0 positional tokens -> root execute; reload there keeps
  the pr.hasPermission("skyycollections.admin") check because no subcommand gate covers that path).
Messages are unchanged: the unlocks/reload bodies moved into CollUnlocks.sendUnlocks(pr) / CollUnlocks.reloadAndReport(pr) and
both the subcommands and the flag path call them.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.3.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.4.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CRLF = "\r\n" in raw
s = raw.replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------- docstring + version ----------------
rep('''"""SkyyCollections 0.1.3 - build script
0.1.3: recipe unlocks''', '''"""SkyyCollections 0.1.4 - build script
0.1.4: command rules (engine-verified 2026-09-23). /collections (alias /coll) is open to every player (permission group
       hytale:Adventurer; before, only "*" admins held the auto node). "/collections unlocks" (alias recipes) and
       "/collections reload" are real subcommands now (optional args are not positional, so the 0.1.3 forms failed with
       wrongNumberRequiredParameters). unlocks = Adventurer group; reload = requirePermission("skyycollections.admin") plus
       setPermissionGroups(new String[0]) so it does NOT inherit the parent's Adventurer group (putRecursivePermissionGroups
       would otherwise grant skyycollections.admin to every player). "--action unlocks|reload" still works.
       Derived by tools/coll_0_1_4_patch.py.
0.1.3: recipe unlocks''')
rep('''Run:   python build_skyycollections_0.1.2.py            -> SkyyCollections/SkyyCollections-0.1.1.jar
       python build_skyycollections_0.1.2.py --deploy   -> also''', '''Run:   python build_skyycollections_0.1.4.py            -> SkyyCollections/SkyyCollections-0.1.4.jar
       python build_skyycollections_0.1.4.py --deploy   -> also''')
rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')

# ---------------- constants + probes ----------------
rep('APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"',
    'APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"\n'
    'AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"')
rep('''             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), ("com.hypixel.hytale.component.Archetype", "empty")):''',
    '''             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), ("com.hypixel.hytale.component.Archetype", "empty"),
             (AC, "setPermissionGroups"), (AC, "addSubCommand"), (AC, "requirePermission"), (AC, "addAliases")):''')

# ---------------- classes ----------------
rep('''cmd   = pool.makeClass(PKG + ".CollCmd", pool.get(APC))''',
    '''ulc   = pool.makeClass(PKG + ".CollUnlocksCmd", pool.get(APC))
rlc   = pool.makeClass(PKG + ".CollReloadCmd", pool.get(APC))
cmd   = pool.makeClass(PKG + ".CollCmd", pool.get(APC))
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'   # vanilla /help /who /ping pattern (SkyyEssentials 0.1)''')

# ---------------- CollUnlocks: shared bodies for the subcommands and the --action flag ----------------
rep('''unl.addMethod(CtNewMethod.make("""
public static void republishAll() {
  java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
  while (it.hasNext()) publish((java.util.UUID) it.next());
}""", unl))
''', '''unl.addMethod(CtNewMethod.make("""
public static void republishAll() {
  java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
  while (it.hasNext()) publish((java.util.UUID) it.next());
}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static void sendUnlocks({PR} pr) {{
  java.util.TreeSet ids = compute({PKG}.CollStore.counts(pr.getUuid()));
  publish(pr.getUuid());
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = ids.iterator(); int n = 0;
  while (it.hasNext() && n < 12) {{ if (sb.length() > 0) sb.append(", "); sb.append({PKG}.CollStore.pretty((String) it.next())); n++; }}
  pr.sendMessage({MSG}.raw("[Collections] " + ids.size() + " recipe(s) unlocked" + (ids.size() > 0 ? ": " + sb + (ids.size() > 12 ? ", ..." : "") + "  -> /craft (Collections tab)" : ". Break blocks to reach tier I (50) of a material.")));
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static void reloadAndReport({PR} pr) {{
  load();
  republishAll();
  pr.sendMessage({MSG}.raw("[Collections] unlocks.properties reloaded (" + TABLE.size() + " explicit rule(s), auto=" + AUTO + ")"));
}}""", unl))
''')

# ---------------- command: subcommands first (constructor + execute before CollCmd's constructor builds them) ----------------
rep('''# ================= command =================
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public CollCmd() {{
  super("collections", "View your collections; /collections unlocks | reload");
  addAliases(new String[] {{ "coll" }});
  this.actionArg = withOptionalArg("action", "unlocks | reload", {ATY}.STRING);
}}""", cmd))''', '''# ================= command =================
# /collections unlocks (alias recipes) - every player
ulc.addConstructor(CtNewConstructor.make(f"""
public CollUnlocksCmd() {{
  super("unlocks", "List the recipes your collections have unlocked");
  addAliases(new String[] {{ "recipes" }});
  {ADV}
}}""", ulc))
ulc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PKG}.CollUnlocks.sendUnlocks(pr);
  }} catch (Throwable t) {{
    {PKG}.CollStore.warn("/collections unlocks failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyCollections] could not open the page"));
  }}
}}""", ulc))
# /collections reload - admin. Empty group list = do NOT inherit the parent's hytale:Adventurer group (see docstring).
rlc.addConstructor(CtNewConstructor.make(f"""
public CollReloadCmd() {{
  super("reload", "Reload unlocks.properties and republish recipe unlocks (admin)");
  requirePermission("skyycollections.admin");
  setPermissionGroups(new String[0]);
}}""", rlc))
rlc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PKG}.CollUnlocks.reloadAndReport(pr);
  }} catch (Throwable t) {{
    {PKG}.CollStore.warn("/collections reload failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyCollections] could not open the page"));
  }}
}}""", rlc))
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public CollCmd() {{
  super("collections", "View your collections; /collections unlocks | reload");
  addAliases(new String[] {{ "coll" }});
  this.actionArg = withOptionalArg("action", "unlocks | reload", {ATY}.STRING);
  {ADV}
  addSubCommand(new {PKG}.CollUnlocksCmd());
  addSubCommand(new {PKG}.CollReloadCmd());
}}""", cmd))''')

# root execute: the --action flag path now calls the shared bodies (same messages, same admin check)
rep('''      if (a.equals("unlocks") || a.equals("recipes")) {{
        java.util.TreeSet ids = {PKG}.CollUnlocks.compute({PKG}.CollStore.counts(pr.getUuid()));
        {PKG}.CollUnlocks.publish(pr.getUuid());
        StringBuilder sb = new StringBuilder();
        java.util.Iterator it = ids.iterator(); int n = 0;
        while (it.hasNext() && n < 12) {{ if (sb.length() > 0) sb.append(", "); sb.append({PKG}.CollStore.pretty((String) it.next())); n++; }}
        pr.sendMessage({MSG}.raw("[Collections] " + ids.size() + " recipe(s) unlocked" + (ids.size() > 0 ? ": " + sb + (ids.size() > 12 ? ", ..." : "") + "  -> /craft (Collections tab)" : ". Break blocks to reach tier I (50) of a material.")));
        return;
      }}
      if (a.equals("reload")) {{
        if (!pr.hasPermission("skyycollections.admin")) {{ pr.sendMessage({MSG}.raw("[Collections] no permission")); return; }}
        {PKG}.CollUnlocks.load();
        {PKG}.CollUnlocks.republishAll();
        pr.sendMessage({MSG}.raw("[Collections] unlocks.properties reloaded (" + {PKG}.CollUnlocks.TABLE.size() + " explicit rule(s), auto=" + {PKG}.CollUnlocks.AUTO + ")"));
        return;
      }}''', '''      if (a.equals("unlocks") || a.equals("recipes")) {{
        {PKG}.CollUnlocks.sendUnlocks(pr);
        return;
      }}
      if (a.equals("reload")) {{
        if (!pr.hasPermission("skyycollections.admin")) {{ pr.sendMessage({MSG}.raw("[Collections] no permission")); return; }}
        {PKG}.CollUnlocks.reloadAndReport(pr);
        return;
      }}''')

rep('for c in (store, unl, sysc, sav, ccmp, page, cmd, pl):', 'for c in (store, unl, sysc, sav, ccmp, page, ulc, rlc, cmd, pl):')

out = s.replace("\n", "\r\n") if CRLF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(CRLF)" if CRLF else "(LF)")
