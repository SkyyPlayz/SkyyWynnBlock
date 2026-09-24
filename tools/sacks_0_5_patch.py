# one-off (2026-09-22 late): derive SkyySacks/build_skyysacks_0.5.0.py from 0.4.0 - BENCH CRAFTING FROM MAGIC BAGS.
# Engine facts (agent research 2026-09-22): BenchWindow/SimpleCraftingWindow implement MaterialContainerWindow; the crafting
# manager checks AND consumes materials from getExtraResourcesSection().getItemContainer() merged with the inventory.
# Vanilla feeds that section with nearby chests and invalidates it after each craft, so we re-apply every 300ms on the world
# thread: mirror the pool into a SimpleItemContainer, wrap vanilla's container + ours in a CombinedItemContainer, set it,
# push UpdateWindow. Consumption = expected-vs-actual diff of the mirror, applied to the pool before every rebuild.
# Pocket crafting (FieldCraftingWindow) has no such hook - later.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.4.0.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.5.0.py")
s = open(src, encoding="utf8").read()
s = s.replace('VERSION = "0.4.0"', 'VERSION = "0.5.0"').replace("build_skyysacks_0.4.0.py", "build_skyysacks_0.5.0.py")

# --- constants + probes
s = s.replace('LOG = "com.hypixel.hytale.logger.HytaleLogger"',
'''LOG = "com.hypixel.hytale.logger.HytaleLogger"
MCW = "com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialContainerWindow"
MERS= "com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialExtraResourcesSection"
WIN = "com.hypixel.hytale.server.core.entity.entities.player.windows.Window"
WM  = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
IQ  = "com.hypixel.hytale.protocol.ItemQuantity"''')
s = s.replace('("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):\n    B.probe(pool, c, m)',
              '("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (MCW, "getExtraResourcesSection"), (MERS, "setItemContainer"),\n             (WM, "updateWindow"), (PLA, "getWindowManager"), (IC, "setItemStackForSlot")):\n    B.probe(pool, c, m)')

# --- new classes
s = s.replace('pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))',
              'mir  = pool.makeClass(PKG + ".BagMirror")\nclt  = pool.makeClass(PKG + ".CraftLinkTask")\nctk  = pool.makeClass(PKG + ".CraftTick")\npl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))')

craft = r'''
# ================= BagMirror (per player: SimpleItemContainer mirroring the pool for bench crafting) =================
mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MIRRORS = new java.util.concurrent.ConcurrentHashMap();", mir))
mir.addField(CtField.make(f"public {SIC} cont;", mir))
mir.addField(CtField.make("public String[] slotIds;", mir))
mir.addField(CtField.make("public int[] slotQty;", mir))
mir.addField(CtField.make(f"public {CIC} combined;", mir))
mir.addField(CtField.make("public Object vanilla;", mir))
mir.addField(CtField.make("public String sig;", mir))
mir.addConstructor(CtNewConstructor.make(f"""
public BagMirror() {{
  this.cont = new {SIC}((short) 36);
  this.slotIds = new String[36];
  this.slotQty = new int[36];
  this.sig = "";
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static {PKG}.BagMirror of(java.util.UUID u) {{
  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.get(u);
  if (m == null) {{ m = new {PKG}.BagMirror(); {PKG}.BagMirror prev = ({PKG}.BagMirror) MIRRORS.putIfAbsent(u, m); if (prev != null) m = prev; }}
  return m;
}}""", mir))
# apply consumption: anything missing from the mirror vs. what we put there left the pool (the bench took it)
mir.addMethod(CtNewMethod.make(f"""
public int sync(java.util.UUID u) {{
  int consumed = 0;
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    {IS} it = this.cont.getItemStack((short) i);
    int actual = (it == null || it.isEmpty()) ? 0 : it.getQuantity();
    if (actual < this.slotQty[i]) {{ int d = this.slotQty[i] - actual; {PKG}.SackPool.add(u, this.slotIds[i], -(long) d); consumed += d; }}
  }}
  return consumed;
}}""", mir))
# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots
mir.addMethod(CtNewMethod.make(f"""
public String rebuild(java.util.UUID u, java.util.HashMap caps) {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb = new StringBuilder();
  int slot = 0;
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.SackPool.pool(u).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  for (int e = 0; e < entries.size() && slot < 36; e++) {{
    java.util.Map.Entry en = (java.util.Map.Entry) entries.get(e);
    String id = (String) en.getKey();
    long cnt = ((Long) en.getValue()).longValue();
    String cat = {PKG}.SackDefs.catOf(id);
    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;
    int max = 64;
    try {{ {IS} probe = new {IS}(id, 1); if (probe.getItem() != null && probe.getItem().getMaxStack() > 0) max = probe.getItem().getMaxStack(); }} catch (Throwable t) {{ }}
    int stacks = 0;
    while (cnt > 0L && stacks < 4 && slot < 36) {{
      int q = cnt < (long) max ? (int) cnt : max;
      this.cont.setItemStackForSlot((short) slot, new {IS}(id, q));
      this.slotIds[slot] = id; this.slotQty[slot] = q;
      sb.append(id).append('=').append(q).append(';');
      cnt -= q; slot++; stacks++;
    }}
  }}
  return sb.toString();
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public {IQ}[] quantities() {{
  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    Integer cur = (Integer) sum.get(this.slotIds[i]);
    sum.put(this.slotIds[i], Integer.valueOf((cur == null ? 0 : cur.intValue()) + this.slotQty[i]));
  }}
  {IQ}[] out = new {IQ}[sum.size()];
  java.util.Iterator it = sum.entrySet().iterator(); int k = 0;
  while (it.hasNext()) {{ java.util.Map.Entry e = (java.util.Map.Entry) it.next(); out[k++] = new {IQ}((String) e.getKey(), ((Integer) e.getValue()).intValue()); }}
  return out;
}}""", mir))

# ================= CraftLinkTask (world thread, every 300ms per player) =================
clt.addInterface(pool.get("java.lang.Runnable"))
clt.addField(CtField.make(f"public {PR} pr;", clt))
clt.addField(CtField.make("public java.util.UUID expectedWorld;", clt))
clt.addConstructor(CtNewConstructor.make(f"public CraftLinkTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", clt))
clt.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    java.util.UUID u = pr.getUuid();
    {WM} wm = p.getWindowManager();
    if (wm == null) return;
    java.util.List wins = wm.getWindows();
    boolean any = false;
    for (int i = 0; wins != null && i < wins.size(); i++) {{
      Object w = wins.get(i);
      if (!(w instanceof {MCW})) continue;
      any = true;
      {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
      int consumed = m.sync(u);
      java.util.HashMap caps = {PKG}.SweepTask.caps(p.getInventory());
      String sig = m.rebuild(u, caps);
      {MERS} sec = (({MCW}) w).getExtraResourcesSection();
      if (sec == null) continue;
      {IC} existing = sec.getItemContainer();
      boolean ours = existing != null && (existing == m.combined || existing == m.cont);
      if (!ours) {{
        if (existing == null) {{ m.vanilla = null; m.combined = new {CIC}(new {IC}[] {{ m.cont }}); }}
        else {{ m.vanilla = existing; m.combined = new {CIC}(new {IC}[] {{ existing, m.cont }}); }}
      }}
      sec.setItemContainer(m.combined);
      sec.setExtraMaterials(m.quantities());
      sec.setValid(true);
      if (!ours || consumed > 0 || !sig.equals(m.sig)) {{
        m.sig = sig;
        try {{ wm.updateWindow(({WIN}) w); }} catch (Throwable t) {{ }}
      }}
      if (consumed > 0) {PKG}.SackPool.save(u);
    }}
    if (!any) {{
      {PKG}.BagMirror m = ({PKG}.BagMirror) {PKG}.BagMirror.MIRRORS.get(u);
      if (m != null) {{ int c = m.sync(u); if (c > 0) {PKG}.SackPool.save(u); {PKG}.BagMirror.MIRRORS.remove(u); }}
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft link failed: " + t); }}
}}""", clt))

ctk.addInterface(pool.get("java.lang.Runnable"))
ctk.addConstructor(CtNewConstructor.make("public CraftTick() { }", ctk))
ctk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new {PKG}.CraftLinkTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ctk))

# ================= plugin ================='''
s = s.replace("\n# ================= plugin =================", craft, 1)
# schedule + shutdown + class list
s = s.replace('pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))',
              'pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))\npl.addField(CtField.make("public java.util.concurrent.ScheduledFuture crafter;", pl))')
old = '  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);'
assert old in s
s = s.replace(old, old + '\n  this.crafter = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CraftTick(), 1000L, 300L, java.util.concurrent.TimeUnit.MILLISECONDS);')
old = '  try {{ if (this.saver != null) this.saver.cancel(false); }} catch (Throwable t) {{ }}'
assert old in s
s = s.replace(old, old + '\n  try {{ if (this.crafter != null) this.crafter.cancel(false); }} catch (Throwable t) {{ }}')
s = s.replace('for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, pl):', 'for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, pl):')
s = s.replace('log("[SkyySacks] {VERSION} ready - /sacks (/pd) or right-click a magic bag")', 'log("[SkyySacks] {VERSION} ready - /pd, right-click a magic bag; workbenches craft from your bags")')
open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
