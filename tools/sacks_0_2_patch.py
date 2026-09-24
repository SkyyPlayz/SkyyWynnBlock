# one-off (2026-09-22): derive SkyySacks/build_skyysacks_0.2.py from 0.1.4
# v0.2 page = SkyBlock-style sack GUI: category tabs, capacity line, 9x4 icon grid (left click = stack, right click = 1,
# hover = info line), Pick up all, Deposit all. See SkyySacks-Plan.md "v0.2 page design".
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.1.4.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.2.py")
s = open(src, encoding="utf8").read()
s = s.replace('VERSION = "0.1.4"', 'VERSION = "0.2"').replace("build_skyysacks_0.1.4.py", "build_skyysacks_0.2.py")
s = s.replace('"""SkyySacks 0.1.4 - build script', '"""SkyySacks 0.2 - build script')

def replace_section(text, start_marker, end_marker, new_body):
    a = text.index(start_marker); b = text.index(end_marker, a)
    return text[:a] + new_body + text[b:]

# ---------------- SweepTask: static sweep(player, uuid, onlyCat, allContainers) ----------------
sweep = r'''# ================= SweepTask (runs ON world thread; no disk I/O) =================
swp.addInterface(pool.get("java.lang.Runnable"))
swp.addField(CtField.make(f"public {PR} pr;", swp))
swp.addField(CtField.make("public java.util.UUID expectedWorld;", swp))
swp.addConstructor(CtNewConstructor.make(f"public SweepTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", swp))
# capacity per category = sum of sack tiers carried anywhere (storage + hotbar + backpack)
swp.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap caps({INV} inv) {{
  java.util.HashMap caps = new java.util.HashMap();
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id != null && id.startsWith("Skyy_Sack_")) {{
        String[] parts = id.split("_");
        if (parts.length >= 4) {{
          String cat = parts[2]; String tier = parts[3];
          Integer cur = (Integer) caps.get(cat);
          caps.put(cat, Integer.valueOf((cur == null ? 0 : cur.intValue()) + {PKG}.SackDefs.tierCap(tier)));
        }}
      }}
    }}
  }}
  return caps;
}}""", swp))
# sweep matching items into the pool. onlyCat == null -> every category; allContainers -> hotbar + backpack too. Returns items moved.
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, java.util.UUID u, String onlyCat, boolean allContainers) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  int moved = 0;
  {IC}[] conts = allContainers ? new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }} : new {IC}[] {{ inv.getStorage() }};
  for (int c = 0; c < conts.length; c++) {{
    {IC} stor = conts[c];
    if (stor == null) continue;
    short cap2 = stor.getCapacity();
    for (short s = 0; s < cap2; s++) {{
      {IS} it = stor.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      if (onlyCat != null && !onlyCat.equals(cat)) continue;
      Integer catCap = (Integer) caps.get(cat);
      if (catCap == null) continue;
      long have = {PKG}.SackPool.catTotal(u, cat);
      long room = (long) catCap.intValue() - have;
      if (room <= 0L) continue;
      int qty = it.getQuantity();
      int take = (long) qty < room ? qty : (int) room;
      if (take <= 0) continue;
      {ISS} tx = stor.removeItemStackFromSlot(s, take);
      if (tx == null || !tx.succeeded()) continue;
      {IS} rem = tx.getRemainder();
      int removed = take - (rem == null ? 0 : rem.getQuantity());
      if (removed > 0) {{ {PKG}.SackPool.add(u, id, (long) removed); moved += removed; }}
    }}
  }}
  return moved;
}}""", swp))
# withdraw up to n of an item into STORAGE; returns how many actually left the pool
swp.addMethod(CtNewMethod.make(f"""
public static int withdraw({PLA} p, java.util.UUID u, String id, int n) {{
  long have = {PKG}.SackPool.get(u, id);
  if (have <= 0L || n <= 0) return 0;
  int take = (long) n < have ? n : (int) have;
  {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, take));
  {IS} rem = tx == null ? null : tx.getRemainder();
  int added = (tx == null || !tx.succeeded()) ? 0 : take - (rem == null ? 0 : rem.getQuantity());
  if (added > 0) {PKG}.SackPool.add(u, id, -(long) added);
  return added;
}}""", swp))
swp.addMethod(CtNewMethod.make(f"""
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
    sweep(p, pr.getUuid(), null, false);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sweep failed: " + t); }}
}}""", swp))

'''
s = replace_section(s, "# ================= SweepTask", "# ================= SackTick", sweep)

# ---------------- SacksPage: SkyBlock-style grid ----------------
page = r'''# ================= SacksPage (SkyBlock-style: tabs, capacity, 9x4 icon grid, pick up all / deposit all) =================
page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String info;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SacksPage({PR} pr, String cat) {{
  super(pr, {LIFE}.CanDismiss);
  this.cat = cat;
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public String pickCat(java.util.UUID u) {{
  if (this.cat != null) return this.cat;
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) if ({PKG}.SackPool.catTotal(u, cats[c]) > 0L) return cats[c];
  return cats[0];
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  this.cat = pickCat(u);
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  java.util.HashMap caps = player == null ? new java.util.HashMap() : {PKG}.SweepTask.caps(player.getInventory());
  Integer capObj = (Integer) caps.get(this.cat);
  long capacity = capObj == null ? 0L : (long) capObj.intValue();
  long stored = {PKG}.SackPool.catTotal(u, this.cat);
  String bs = "{BTN}";
  String tabOn = "{TABON}";
  b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 420, Height: 372); Background: #0b1524(0.96); Padding: (Horizontal: 12, Vertical: 8); LayoutMode: Top; }}");
  b.appendInline("#SkyySacks", "Group {{ Anchor: (Height: 2); Background: #e0b060; }}");
  b.appendInline("#SkyySacks", "Group #SkyySTabs {{ Anchor: (Height: 26); LayoutMode: Left; Padding: (Top: 4); }}");
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) {{
    boolean sel = cats[c].equals(this.cat);
    b.appendInline("#SkyySTabs", "TextButton #SkyySTab" + cats[c] + " {{ Anchor: (Width: 96, Height: 22); Text: \\"" + cats[c] + "\\"; " + (sel ? tabOn : bs) + " }}");
    b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 4, Height: 22); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySTab" + cats[c], {EVD}.of("a", "tab:" + cats[c]));
  }}
  b.appendInline("#SkyySacks", "Label #SkyySCap {{ Anchor: (Height: 16); Text: \\"" + this.cat + " sack   " + stored + " / " + capacity + (capacity == 0L ? "   (carry a " + this.cat + " sack to pool items)" : "") + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = {PKG}.SackPool.pool(u).entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (this.cat.equals({PKG}.SackDefs.catOf((String) e.getKey()))) entries.add(e);
  }}
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  this.cells = new String[36];
  for (int r = 0; r < 4; r++) {{
    b.appendInline("#SkyySacks", "Group #SkyySRow" + r + " {{ Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 2); }}");
    for (int c = 0; c < 9; c++) {{
      int idx = r * 9 + c;
      if (idx < entries.size()) {{
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
        String id = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = id;
        b.appendInline("#SkyySRow" + r, "Button #SkyySCell" + idx + " {{ Anchor: (Width: 42, Height: 42); Style: ButtonStyle( Default: ( Background: #1d3a5f ), Hovered: ( Background: #2f5a8f ), Disabled: ( Background: #1a2c3c ) ); ItemIcon {{ Anchor: (Width: 32, Height: 32, Left: 5, Top: 3); ItemId: \\"" + id + "\\"; }} Label {{ Anchor: (Width: 40, Height: 10, Right: 2, Bottom: 1); Text: \\"" + cnt + "\\"; Style: (FontSize: 8, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); }} }}");
        ev.addEventBinding({BT}.Activating, "#SkyySCell" + idx, {EVD}.of("a", "cell:" + idx + ":stack"));
        ev.addEventBinding({BT}.RightClicking, "#SkyySCell" + idx, {EVD}.of("a", "cell:" + idx + ":one"));
        ev.addEventBinding({BT}.MouseEntered, "#SkyySCell" + idx, {EVD}.of("a", "hover:" + idx));
      }} else {{
        this.cells[idx] = null;
        b.appendInline("#SkyySRow" + r, "Group {{ Anchor: (Width: 42, Height: 42); Background: #101820(0.85); }}");
      }}
      b.appendInline("#SkyySRow" + r, "Label {{ Anchor: (Width: 2, Height: 42); Text: \\"\\"; }}");
    }}
  }}
  b.appendInline("#SkyySacks", "Label #SkyySInfo {{ Anchor: (Height: 16); Text: \\"" + this.info + "\\"; Style: (FontSize: 10, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Group #SkyySAct {{ Anchor: (Height: 28); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyySAct", "TextButton #SkyySPickAll {{ Anchor: (Width: 120, Height: 22); Text: \\"Pick up all\\"; " + bs + " }}");
  b.appendInline("#SkyySAct", "Label {{ Anchow: (Width: 8, Height: 22); Anchor: (Width: 8, Height: 22); Text: \\"\\"; }}");
  b.appendInline("#SkyySAct", "TextButton #SkyySDepAll {{ Anchor: (Width: 120, Height: 22); Text: \\"Deposit all\\"; " + bs + " }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 8, Height: 22); Text: \\"\\"; }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 130, Height: 22); Text: \\"left: stack  right: 1\\"; Style: (FontSize: 9, TextColor: #8fa4b8, VerticalAlignment: Center); }}");
  ev.addEventBinding({BT}.Activating, "#SkyySPickAll", {EVD}.of("a", "pickall"));
  ev.addEventBinding({BT}.Activating, "#SkyySDepAll", {EVD}.of("a", "depall"));
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    String[] cats = {PKG}.SackDefs.CATS;
    for (int c = 0; c < cats.length; c++) {{
      if (data.indexOf("tab:" + cats[c] + "\\"") >= 0) {{ this.cat = cats[c]; this.info = ""; rebuild(); return; }}
    }}
    for (int i = 0; i < 36; i++) {{
      if (this.cells == null || this.cells[i] == null) continue;
      if (data.indexOf("hover:" + i + "\\"") >= 0) {{
        this.info = this.cells[i] + "   " + {PKG}.SackPool.get(u, this.cells[i]) + " stored";
        {UCB} b = new {UCB}();
        b.set("#SkyySInfo.Text", this.info);
        sendUpdate(b);
        return;
      }}
    }}
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    for (int i = 0; i < 36; i++) {{
      if (this.cells == null || this.cells[i] == null) continue;
      int n = 0;
      if (data.indexOf("cell:" + i + ":stack\\"") >= 0) n = 64;
      else if (data.indexOf("cell:" + i + ":one\\"") >= 0) n = 1;
      if (n == 0) continue;
      int added = {PKG}.SweepTask.withdraw(player, u, this.cells[i], n);
      this.info = added > 0 ? ("took " + added + " " + this.cells[i]) : "storage is full";
      {PKG}.SackPool.save(u);
      rebuild();
      return;
    }}
    if (data.indexOf("pickall\\"") >= 0) {{
      int total = 0;
      for (int i = 0; i < 36; i++) {{
        if (this.cells[i] == null) continue;
        int added; int guard = 0;
        do {{ added = {PKG}.SweepTask.withdraw(player, u, this.cells[i], 64); total += added; guard++; }} while (added > 0 && guard < 64);
      }}
      this.info = total > 0 ? ("picked up " + total + " items") : "storage is full";
      {PKG}.SackPool.save(u);
      rebuild();
      return;
    }}
    if (data.indexOf("depall\\"") >= 0) {{
      int moved = {PKG}.SweepTask.sweep(player, u, this.cat, true);
      this.info = moved > 0 ? ("deposited " + moved + " items") : "nothing to deposit (or sack full)";
      {PKG}.SackPool.save(u);
      rebuild();
      return;
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sacks page event failed: " + t); }}
}}""", page))

'''
BTN = 'Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 10, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
TABON = 'Style: TextButtonStyle(Default: (Background: #e0b060, LabelStyle: (FontSize: 10, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #f0c878, LabelStyle: (FontSize: 10, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #b08040, LabelStyle: (FontSize: 10, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
page = page.replace("{BTN}", BTN).replace("{TABON}", TABON)
page = page.replace('"Label {{ Anchow: (Width: 8, Height: 22); Anchor: (Width: 8, Height: 22); Text: \\"\\"; }}"', '"Label {{ Anchor: (Width: 8, Height: 22); Text: \\"\\"; }}"')
s = replace_section(s, "# ================= SacksPage", "# ================= SacksCmd", page)

# ---------------- command opens with no category (auto-pick); factory carries the category ----------------
s = s.replace("player.getPageManager().openCustomPage(ref, store, new {PKG}.SacksPage(pr));", "player.getPageManager().openCustomPage(ref, store, new {PKG}.SacksPage(pr, (String) null));")
fac = r'''# ================= SacksPageFactory (right-click on a sack item -> OpenCustomUI "SkyySacks<Cat>") =================
fac.addInterface(pool.get("java.util.function.Function"))
fac.addField(CtField.make("public String cat;", fac))
fac.addConstructor(CtNewConstructor.make("public SacksPageFactory(String cat) { this.cat = cat; }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.SacksPage(({PR}) o, this.cat);
}}""", fac))

'''
s = replace_section(s, "# ================= SacksPageFactory", "# ================= plugin", fac)
old_reg = '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacks", new {PKG}.SacksPageFactory());'
assert old_reg in s
s = s.replace(old_reg, '''  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacks", new {PKG}.SacksPageFactory((String) null));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksMining", new {PKG}.SacksPageFactory("Mining"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksForaging", new {PKG}.SacksPageFactory("Foraging"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFarming", new {PKG}.SacksPageFactory("Farming"));''')
# item JSON: page id per category
old_json = '"Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyySacks"}}]}}'
assert old_json in s
s = s.replace(old_json, '"Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyySacks" + cat}}]}}')
# ROWS constant no longer used by the page but harmless; probe Button-less. Done.
open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
