# one-off (2026-09-23): derive SkyySacks/build_skyysacks_0.6.0.py from 0.5.2 - THE CRAFT PAGE (inventory crafting v1).
# /craft (+ "Craft" tab button in /pd): recipe sources merged = (1) Fieldcraft categories, (2) bench accessories carried
# (items Skyy_Accessory_<BenchId>, scaffold: benches enumerated from all recipes' BenchRequirement ids), (3) collection
# unlocks published by SkyyCollections in the JVM bridge as "coll:recipes:<uuid>" (comma-separated recipe ids).
# Materials counted from CombinedItemContainer{inventory backpack+storage+hotbar, bag mirror} with the engine's own
# countRemovableMaterial; crafting via CraftingManager.craftItem (engine consumes inputs, gives output); pool synced after.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.5.2.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.0.py")
s = open(src, encoding="utf8").read()
s = s.replace('VERSION = "0.5.2"', 'VERSION = "0.6.0"').replace("build_skyysacks_0.5.2.py", "build_skyysacks_0.6.0.py")

def rep(a, b, count=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, count)

rep('IQ  = "com.hypixel.hytale.protocol.ItemQuantity"', '''IQ  = "com.hypixel.hytale.protocol.ItemQuantity"
CRP = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
CRM = "com.hypixel.hytale.builtin.crafting.component.CraftingManager"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
FCC = "com.hypixel.hytale.server.core.asset.type.item.config.FieldcraftCategory"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"
OPT = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"''')
rep('("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (OCU, "registerSimple")):\n    B.probe(pool, c, m)',
    '("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (OCU, "registerSimple"), (CRP, "getAvailableRecipesForCategory"),\n             (CRM, "getInputMaterials"), (CRR, "getInput"), (FCC, "getAssetMap"), (IC, "countRemovableMaterial"), (IC, "removeMaterials"), (INV, "getCombinedBackpackStorageHotbar"), (SIC, "addOrDropItemStack")):\n    B.probe(pool, c, m)')
rep('pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))',
    'cpg  = pool.makeClass(PKG + ".CraftPage", pool.get(PAGE))\nccmd = pool.makeClass(PKG + ".CraftCmd", pool.get(APC))\npl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))')

# ---- bag page: "Craft" button in the tab row (opens CraftPage)
rep('''  b.appendInline("#SkyySacks", "Label #SkyySCap {{ Anchor: (Height: 24);''',
'''  b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 20, Height: 28); Text: \\\\"\\\\"; }}");
  b.appendInline("#SkyySTabs", "TextButton #SkyySTabCraft {{ Anchor: (Width: 110, Height: 28); Text: \\\\"Craft\\\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySTabCraft", {EVD}.of("a", "craft"));
  b.appendInline("#SkyySacks", "Label #SkyySCap {{ Anchor: (Height: 24);''')
rep('''    for (int c = 0; c < cats.length; c++) {{
      if (data.indexOf("tab:" + cats[c] + "\\\\"") >= 0) {{ this.cat = cats[c]; this.info = ""; rebuild(); return; }}
    }}''',
'''    for (int c = 0; c < cats.length; c++) {{
      if (data.indexOf("tab:" + cats[c] + "\\\\"") >= 0) {{ this.cat = cats[c]; this.info = ""; rebuild(); return; }}
    }}
    if (data.indexOf("\\\\"craft\\\\"") >= 0) {{
      {PLA} pl0 = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (pl0 != null) pl0.getPageManager().openCustomPage(ref, st, new {PKG}.CraftPage(this.playerRef, (String) null));
      return;
    }}''')

craft = r'''
# ================= CraftPage (inventory crafting v1: Fieldcraft + bench accessories + collection unlocks) =================
cpg.addField(CtField.make("public String tab;", cpg))
cpg.addField(CtField.make("public int pageNo;", cpg))
cpg.addField(CtField.make("public String info;", cpg))
cpg.addField(CtField.make("public java.util.ArrayList rows;", cpg))
cpg.addField(CtField.make("public java.util.ArrayList tabs;", cpg))
cpg.addConstructor(CtNewConstructor.make(f"""
public CraftPage({PR} pr, String tab) {{
  super(pr, {LIFE}.CanDismiss);
  this.tab = tab; this.pageNo = 0; this.info = "";
}}""", cpg))
cpg.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ');
  int q = s.indexOf(':');
  if (q >= 0 && q + 1 < s.length()) s = s.substring(q + 1);
  return s;
}""", cpg))
# accessory item ids the player carries anywhere -> bench ids granted
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashSet accessories({PLA} p) {{
  java.util.HashSet out = new java.util.HashSet();
  {INV} inv = p.getInventory();
  if (inv == null) return out;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id != null && id.startsWith("Skyy_Accessory_")) out.add(id.substring("Skyy_Accessory_".length()));
    }}
  }}
  return out;
}}""", cpg))
# collection unlocks published by SkyyCollections via the JVM bridge: "coll:recipes:<uuid>" -> "id,id,id"
cpg.addMethod(CtNewMethod.make("""
public static java.util.HashSet collectionRecipes(java.util.UUID u) {
  java.util.HashSet out = new java.util.HashSet();
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (b == null) return out;
    Object v = ((java.util.Map) b).get("coll:recipes:" + u.toString());
    if (v == null) return out;
    String[] parts = String.valueOf(v).split(",");
    for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) out.add(parts[i].trim());
  } catch (Throwable t) { }
  return out;
}""", cpg))
# tabs: list of String[]{tabId, label} ; recipes for a tab: list of CraftingRecipe
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{
  java.util.ArrayList t = new java.util.ArrayList();
  java.util.Iterator it = {FCC}.getAssetMap().getAssetMap().values().iterator();
  java.util.ArrayList fc = new java.util.ArrayList();
  while (it.hasNext()) {{ {FCC} c = ({FCC}) it.next(); fc.add(c); }}
  for (int i = 0; i < fc.size(); i++) {{ {FCC} c = ({FCC}) fc.get(i); t.add(new String[] {{ "F:" + c.getId(), pretty(c.getId()) }}); }}
  java.util.HashSet acc = accessories(p);
  java.util.Iterator ai = acc.iterator();
  while (ai.hasNext()) {{ String bench = (String) ai.next(); t.add(new String[] {{ "B:" + bench, pretty(bench) }}); }}
  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});
  return t;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.TreeSet ids = new java.util.TreeSet();
  if (tabId.startsWith("F:")) {{
    java.util.Set s = {CRP}.getAvailableRecipesForCategory("Fieldcraft", tabId.substring(2));
    if (s != null) ids.addAll(s);
  }} else if (tabId.startsWith("B:")) {{
    String bench = tabId.substring(2);
    java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      {CRR} r = ({CRR}) it.next();
      {BRQ}[] br = r.getBenchRequirement();
      if (br == null) continue;
      for (int i = 0; i < br.length; i++) if (br[i] != null && bench.equalsIgnoreCase(String.valueOf(br[i].id))) {{ ids.add(r.getId()); break; }}
    }}
  }} else if (tabId.startsWith("C:")) {{
    ids.addAll(collectionRecipes(u));
  }}
  java.util.Iterator ii = ids.iterator();
  while (ii.hasNext()) {{
    Object r = {CRR}.getAssetMap().getAsset(ii.next());
    if (r != null) out.add(r);
  }}
  return out;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materials({PLA} p, java.util.UUID u) {{
  {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
  m.sync(u);
  m.rebuild(u, {PKG}.SweepTask.caps(p.getInventory()));
  return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar(), m.cont }});
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static int limit({CRR} r, {IC} c) {{
  {MQ}[] in = r.getInput();
  if (in == null || in.length == 0) return 0;
  int lim = Integer.MAX_VALUE;
  for (int i = 0; i < in.length; i++) {{
    int q = in[i].getQuantity(); if (q <= 0) continue;
    int have = c.countRemovableMaterial(in[i]);
    int l = have / q;
    if (l < lim) lim = l;
  }}
  return lim == Integer.MAX_VALUE ? 0 : lim;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  String bs = "{BTN}";
  String on = "{TABON}";
  b.appendInline((String) null, "Group #SkyyCraft {{ Anchor: (Width: 720, Height: 620); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyCraft", "Group {{ Anchor: (Height: 2); Background: #7fb0e0; }}");
  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 26); Text: \\"Crafting\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  if (p == null) return;
  this.tabs = buildTabs(p, u);
  if (this.tab == null && this.tabs.size() > 0) this.tab = ((String[]) this.tabs.get(0))[0];
  b.appendInline("#SkyyCraft", "Group #SkyyCTabs {{ Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 4); }}");
  for (int i = 0; i < this.tabs.size(); i++) {{
    String[] t = (String[]) this.tabs.get(i);
    boolean sel = t[0].equals(this.tab);
    b.appendInline("#SkyyCTabs", "TextButton #SkyyCTab" + i + " {{ Anchor: (Width: 96, Height: 26); Text: \\"" + {PKG}.SacksPage.safe(t[1]) + "\\"; " + (sel ? on : bs) + " }}");
    b.appendInline("#SkyyCTabs", "Label {{ Anchor: (Width: 4, Height: 26); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCTab" + i, {EVD}.of("a", "tab:" + i));
  }}
  b.appendInline("#SkyyCTabs", "Label {{ Anchor: (Width: 12, Height: 26); Text: \\"\\"; }}");
  b.appendInline("#SkyyCTabs", "TextButton #SkyyCBags {{ Anchor: (Width: 80, Height: 26); Text: \\"Bags\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCBags", {EVD}.of("a", "bags"));
  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 16); Text: \\"Materials are counted from your inventory and your magic bags.\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  this.rows = this.tab == null ? new java.util.ArrayList() : recipesFor(this.tab, u);
  {CIC} mats = materials(p, u);
  int per = 9;
  int pages = (this.rows.size() + per - 1) / per; if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1; if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  for (int i = start; i < this.rows.size() && i < start + per; i++) {{
    {CRR} r = ({CRR}) this.rows.get(i);
    {MQ} outq = r.getPrimaryOutput();
    String outId = outq == null ? "?" : outq.getItemId();
    int lim = limit(r, mats);
    StringBuilder need = new StringBuilder();
    {MQ}[] in = r.getInput();
    for (int k = 0; in != null && k < in.length; k++) {{
      if (need.length() > 0) need.append("   ");
      String nm = in[k].getItemId() != null ? pretty(in[k].getItemId()) : (in[k].getResourceTypeId() != null ? in[k].getResourceTypeId() : "?");
      need.append(nm).append(" ").append(mats.countRemovableMaterial(in[k])).append("/").append(in[k].getQuantity());
    }}
    b.appendInline("#SkyyCraft", "Group #SkyyCRow" + i + " {{ Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 4); " + (lim > 0 ? "Background: #10233a(0.9); " : "Background: #0e1826(0.6); ") + "}}");
    b.appendInline("#SkyyCRow" + i, "Group {{ Anchor: (Width: 42, Height: 42); ItemIcon {{ Anchor: (Width: 36, Height: 36, Left: 3, Top: 3); ItemId: \\"" + {PKG}.SacksPage.safe(outId) + "\\"; }} }}");
    b.appendInline("#SkyyCRow" + i, "Group #SkyyCTxt" + i + " {{ Anchor: (Width: 420, Height: 42); LayoutMode: Top; }}");
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 20); Text: \\"" + {PKG}.SacksPage.safe(pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "")) + "\\"; Style: (FontSize: 12, RenderBold: true, TextColor: " + (lim > 0 ? "#ffffff" : "#8a97a8") + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 18); Text: \\"" + {PKG}.SacksPage.safe(need.toString()) + "\\"; Style: (FontSize: 10, TextColor: " + (lim > 0 ? "#9fd8a2" : "#c07070") + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyCCraft" + i + " {{ Anchor: (Width: 64, Height: 26); Text: \\"Craft\\"; " + bs + " }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 4, Height: 26); Text: \\"\\"; }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyCTen" + i + " {{ Anchor: (Width: 52, Height: 26); Text: \\"x10\\"; " + bs + " }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 4, Height: 26); Text: \\"\\"; }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyCAll" + i + " {{ Anchor: (Width: 52, Height: 26); Text: \\"All " + lim + "\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCCraft" + i, {EVD}.of("a", "craft:" + i + ":1"));
    ev.addEventBinding({BT}.Activating, "#SkyyCTen" + i, {EVD}.of("a", "craft:" + i + ":10"));
    ev.addEventBinding({BT}.Activating, "#SkyyCAll" + i, {EVD}.of("a", "craft:" + i + ":0"));
  }}
  if (this.rows.size() == 0) b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 30); Text: \\"No recipes here yet.\\"; Style: (FontSize: 12, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Label #SkyyCInfo {{ Anchor: (Height: 18); Text: \\"" + {PKG}.SacksPage.safe(this.info) + "\\"; Style: (FontSize: 11, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Group #SkyyCNav {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCPrev {{ Anchor: (Width: 70, Height: 26); Text: \\"< Prev\\"; " + bs + " }}");
  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 120, Height: 26); Text: \\"Page " + (this.pageNo + 1) + " / " + pages + "\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCNext {{ Anchor: (Width: 70, Height: 26); Text: \\"Next >\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCPrev", {EVD}.of("a", "prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyCNext", {EVD}.of("a", "next"));
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (data.indexOf("\\"prev\\"") >= 0) {{ this.pageNo--; rebuild(); return; }}
    if (data.indexOf("\\"next\\"") >= 0) {{ this.pageNo++; rebuild(); return; }}
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("\\"bags\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.SacksPage(this.playerRef, (String) null)); return; }}
    for (int i = 0; this.tabs != null && i < this.tabs.size(); i++) {{
      if (data.indexOf("tab:" + i + "\\"") >= 0) {{ this.tab = ((String[]) this.tabs.get(i))[0]; this.pageNo = 0; this.info = ""; rebuild(); return; }}
    }}
    int c = data.indexOf("craft:");
    if (c < 0) return;
    int e = data.indexOf('\\"', c);
    String[] parts = data.substring(c + 6, e).split(":");
    int idx = Integer.parseInt(parts[0]); int want = Integer.parseInt(parts[1]);
    if (this.rows == null || idx < 0 || idx >= this.rows.size()) return;
    {CRR} r = ({CRR}) this.rows.get(idx);
    {CIC} mats = materials(p, u);
    int lim = limit(r, mats);
    int qty = want == 0 ? lim : (want < lim ? want : lim);
    if (qty <= 0) {{ this.info = "not enough materials"; rebuild(); return; }}
    java.util.List inputs = {CRM}.getInputMaterials(r, qty);
    if (!mats.canRemoveMaterials(inputs)) {{ this.info = "not enough materials"; rebuild(); return; }}
    Object tx = mats.removeMaterials(inputs);
    boolean ok = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();
    {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
    int consumed = m.sync(u);
    if (consumed > 0) {PKG}.SackPool.save(u);
    {MQ}[] outs = r.getOutputs();
    if (ok && outs != null) {{
      for (int k = 0; k < outs.length; k++) {{
        if (outs[k] == null || outs[k].getItemId() == null) continue;
        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedBackpackStorageHotbar(), new {IS}(outs[k].getItemId(), outs[k].getQuantity() * qty));
      }}
    }}
    {MQ} outq = r.getPrimaryOutput();
    this.info = ok ? ("crafted " + qty + " x " + pretty(outq == null ? "?" : outq.getItemId()) + (consumed > 0 ? " (" + consumed + " from bags)" : "")) : "could not remove the materials";
    rebuild();
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft page event failed: " + t); }}
}}""", cpg))

# ================= CraftCmd (/craft) =================
ccmd.addConstructor(CtNewConstructor.make("""
public CraftCmd() {
  super("craft", "Open inventory crafting (materials from your inventory and your magic bags)");
  addAliases(new String[] { "recipes" });
}""", ccmd))
ccmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CraftPage(pr, (String) null));
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("/craft failed: " + t); pr.sendMessage({MSG}.raw("[SkyySacks] could not open crafting")); }}
}}""", ccmd))

# ================= plugin ================='''
BTN = 'Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
TABON = 'Style: TextButtonStyle(Default: (Background: #7fb0e0, LabelStyle: (FontSize: 10, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0c8f0, LabelStyle: (FontSize: 10, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5f90c0, LabelStyle: (FontSize: 10, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
craft = craft.replace("{BTN}", BTN).replace("{TABON}", TABON)
rep("\n# ================= plugin =================", craft)
# CraftPage constructor must be declared before SacksPage.handleDataEvent references it: move field+ctor up
start = s.index('cpg.addField(CtField.make("public String tab;", cpg))')
end = s.index('}}""", cpg))', start) + len('}}""", cpg))')
block = s[start:end]; s = s[:start] + s[end:]
s = s.replace("# ================= SacksPage", "# CraftPage fields + constructor first (SacksPage references it)\n" + block + "\n\n# ================= SacksPage", 1)
rep('  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());', '  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());\n  getCommandRegistry().registerCommand(new {PKG}.CraftCmd());')
rep('for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, pl):', 'for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, cpg, ccmd, pl):')
rep('log("[SkyySacks] {VERSION} ready - /pd, right-click a magic bag; workbenches craft from your bags")', 'log("[SkyySacks] {VERSION} ready - /pd, /craft, right-click a magic bag; workbenches craft from your bags")')
open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
