"""Derive SkyyCollections/build_skyycollections_0.1.3.py from 0.1.2.
0.1.3: publishes recipe unlocks to the JVM bridge ("coll:recipes:<uuid>" -> "id,id,id") so the SkyySacks craft page (/craft,
Collections tab) can list them. Unlock sources:
  * AUTO rule (Skyy_SkyyCollections/unlocks.properties auto=true): a vanilla recipe is unlocked when at least one of its input
    items has reached collection tier I (50) and every input item that you have started collecting is at tier I or better
    (inputs you never collected, e.g. crafted intermediates, are ignored).
  * explicit table in the same file: <CollectionId>.<tier>=RecipeId,RecipeId  (tier 1-5)
Published on: first load of a player's counts, every milestone, CollSaver tick for online players not yet published, /collections reload.
/collections unlocks lists them; /collections reload (perm skyycollections.admin) re-reads the file and republishes.
"""
import re, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.2.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.3.py")
s = open(src, encoding="utf8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:70]
    s = s.replace(old, new, count)

rep('VERSION = "0.1.2"', 'VERSION = "0.1.3"')
rep('"""SkyyCollections 0.1.1 - build script', '"""SkyyCollections 0.1.3 - build script\n0.1.3: recipe unlocks published to the bridge (coll:recipes:<uuid>), auto rule + unlocks.properties, /collections unlocks|reload.')
rep('HSV = "com.hypixel.hytale.server.core.HytaleServer"', '''HSV = "com.hypixel.hytale.server.core.HytaleServer"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"''')
rep('sav   = pool.makeClass(PKG + ".CollSaver")', 'unl   = pool.makeClass(PKG + ".CollUnlocks")\nsav   = pool.makeClass(PKG + ".CollSaver")')

# ---- CollUnlocks class, inserted before CollSystem (after CollStore.bump) ----
UNLOCKS = '''
# ================= CollUnlocks (bridge publisher) =================
unl.addField(CtField.make("public static java.nio.file.Path FILE;", unl))
unl.addField(CtField.make("public static volatile boolean AUTO = true;", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap TABLE = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static synchronized void load() {{
  TABLE.clear();
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String text = "# SkyyCollections recipe unlocks\\\\n"
        + "# auto=true : a recipe unlocks when one of its inputs reaches tier I (50 collected) and every input you have started\\\\n"
        + "#             collecting is at tier I or better (inputs you never collected are ignored)\\\\n"
        + "# explicit  : <CollectionId>.<tier 1-5>=RecipeId,RecipeId   e.g.  Rock_Stone.2=Rock_Stone_Brick\\\\n"
        + "# collection ids are the BLOCK ids you break (see /collections); recipe ids are CraftingRecipe asset ids (/craft shows names)\\\\n"
        + "auto=true\\\\n";
      java.nio.file.Files.write(FILE, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    AUTO = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("auto", "true")).trim());
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {{
      String k = ((String) en.nextElement()).trim();
      if (k.equals("auto")) continue;
      int dot = k.lastIndexOf('.');
      if (dot <= 0) continue;
      try {{
        int tier = Integer.parseInt(k.substring(dot + 1));
        if (tier < 1 || tier > 5) continue;
        TABLE.put(k, p.getProperty(k).trim());
      }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("could not load unlocks.properties: " + t); }}
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet compute(java.util.Map counts) {{
  java.util.TreeSet out = new java.util.TreeSet();
  if (counts == null || counts.isEmpty()) return out;
  try {{
    java.util.Iterator it = TABLE.entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String k = (String) e.getKey();
      int dot = k.lastIndexOf('.');
      String coll = k.substring(0, dot);
      int tier = Integer.parseInt(k.substring(dot + 1));
      Long c = (Long) counts.get(coll);
      if (c == null || {PKG}.CollStore.tierOf(c.longValue()) < tier) continue;
      String[] ids = ((String) e.getValue()).split(",");
      for (int i = 0; i < ids.length; i++) if (ids[i].trim().length() > 0) out.add(ids[i].trim());
    }}
    if (!AUTO) return out;
    long t1 = {PKG}.CollStore.TIERS[0];
    java.util.Iterator rit = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (rit.hasNext()) {{
      {CRR} r = ({CRR}) rit.next();
      if (r == null) continue;
      {MQ}[] in = r.getInput();
      if (in == null || in.length == 0) continue;
      boolean anyTier = false; boolean blocked = false;
      for (int i = 0; i < in.length; i++) {{
        if (in[i] == null) continue;
        String id = in[i].getItemId();
        if (id == null) continue;
        Long c = (Long) counts.get(id);
        if (c == null || c.longValue() <= 0L) continue;
        if (c.longValue() >= t1) anyTier = true; else blocked = true;
      }}
      if (anyTier && !blocked) {{ String rid = (String) r.getId(); if (rid != null) out.add(rid); }}
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("unlock compute failed: " + t); }}
  return out;
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static int publish(java.util.UUID u) {{
  try {{
    java.util.TreeSet ids = compute({PKG}.CollStore.counts(u));
    StringBuilder sb = new StringBuilder();
    java.util.Iterator it = ids.iterator();
    while (it.hasNext()) {{ if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }}
    bridge().put("coll:recipes:" + u.toString(), sb.toString());
    PUBLISHED.put(u, Integer.valueOf(ids.size()));
    return ids.size();
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("publish failed for " + u + ": " + t); return 0; }}
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) publish(u);
    }}
    PUBLISHED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", unl))
unl.addMethod(CtNewMethod.make("""
public static void republishAll() {
  java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
  while (it.hasNext()) publish((java.util.UUID) it.next());
}""", unl))

# ================= CollSystem (BreakBlockEvent listener) ================='''
rep('\n# ================= CollSystem (BreakBlockEvent listener) =================', UNLOCKS)

# milestone message + publish
rep('''    if (newTier > 0) {{
      pr.sendMessage({MSG}.raw("Collection milestone! " + {PKG}.CollStore.pretty(id) + " " + {PKG}.CollStore.roman(newTier) + "  (recipe unlocks land in a later update)"));
    }}''', '''    if (newTier > 0) {{
      int before = {PKG}.CollUnlocks.PUBLISHED.containsKey(u) ? ((Integer) {PKG}.CollUnlocks.PUBLISHED.get(u)).intValue() : 0;
      int now = {PKG}.CollUnlocks.publish(u);
      pr.sendMessage({MSG}.raw("Collection milestone! " + {PKG}.CollStore.pretty(id) + " " + {PKG}.CollStore.roman(newTier) + (now > before ? "  +" + (now - before) + " recipe(s) unlocked - /craft" : "")));
    }}''')

# saver tick also publishes for newly-online players
rep('''  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
}}""", sav))''', '''  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollUnlocks.publishOnline(); }} catch (Throwable t) {{ }}
}}""", sav))''')

# command: optional action
rep('''cmd.addConstructor(CtNewConstructor.make("""
public CollCmd() {
  super("collections", "View your collections");
  addAliases(new String[] { "coll" });
}""", cmd))''', '''cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public CollCmd() {{
  super("collections", "View your collections; /collections unlocks | reload");
  addAliases(new String[] {{ "coll" }});
  this.actionArg = withOptionalArg("action", "unlocks | reload", {ATY}.STRING);
}}""", cmd))''')
rep('''    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CollPage(pr));''', '''    if (ctx.provided(this.actionArg)) {{
      String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
      if (a.equals("unlocks") || a.equals("recipes")) {{
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
      }}
    }}
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CollPage(pr));''')

# plugin setup
rep('''  getEntityStoreRegistry().registerSystem(new {PKG}.CollSystem());''', '''  {PKG}.CollUnlocks.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCollections").resolve("unlocks.properties");
  {PKG}.CollUnlocks.load();
  getEntityStoreRegistry().registerSystem(new {PKG}.CollSystem());''')
rep('''"[SkyyCollections] {VERSION} ready - break blocks, /collections to view"''', '''"[SkyyCollections] {VERSION} ready - break blocks, /collections to view, unlocks auto=" + {PKG}.CollUnlocks.AUTO + " explicit=" + {PKG}.CollUnlocks.TABLE.size()''')
rep('for c in (store, sysc, sav, ccmp, page, cmd, pl):', 'for c in (store, unl, sysc, sav, ccmp, page, cmd, pl):')
rep('/collections to view. Recipe unlocks come later."', '/collections to view. Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties)."')

# probes
rep('''for c, m in (''', '''for c, m in ((CRR, "getInput"), (CRR, "getAssetMap"), (MQ, "getItemId"), (UNI, "getPlayers"), (PR, "hasPermission"), ("com.hypixel.hytale.server.core.command.system.CommandContext", "provided"),
             ''', 1)

open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
