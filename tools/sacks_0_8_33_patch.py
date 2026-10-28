"""Derive SkyySacks/build_skyysacks_0.8.33.py from the SET pin 0.8.32 (the GENERATED build_skyysacks_0.8.32.py; edit THIS file, then
regenerate: python tools/sacks_0_8_33_patch.py; never re-run sacks_0_8_32_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.32 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_33_patch.py   then   python SkyySacks/build_skyysacks_0.8.33.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.33.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.33 (2026-10-27) = HOTFIX "CRAFT ALL CRAFTS 1" (round sacks33; Skyy 2026-10-27: "the craft all doesnt work, it crafts 1" - inventory
  -> Pocket Crafting > Compressing -> Enchanted Wheat showed "Wheat 100/100" from the Pocket while far more Wheat was in it).
  CAUSE (VERIFIED in the 0.8.32 code + the harness): the pocket window's shared BagMirror is rebuilt with BenchLink.fieldWanted(), which
  took the inputs of EVERY Fieldcraft recipe through BagMirror.addInputs - not addRecipe, the 0.8.1 ench01fix2 rule that keeps Enchanted
  compress recipes out of a bench's wanted set. Since SkyyCollections 0.2.34 Fieldcraft holds ~113 forward (100 base -> 1 Enchanted) + ~113
  reverse + the Greater Essence pair, so ~230 ids are "wanted"; BagMirror.rebuild's pass 0 gives ONE stack to every wanted id until the
  36 mirror slots are full, so Wheat got one 100-stack, and the client computes ALL / x10 from what the section offers (the engine's
  CraftingWindow takes the quantity from the client) -> ALL = 1. The lowest piles of real Fieldcraft ingredients got no slot at all.
  FIX (the pocket window only; benches, /craft and every other rebuild keep the 0.8.32 order exactly):
  1. fieldWanted() sorts the Fieldcraft recipes with the new BagMirror.fieldRecipe: a COMPRESS recipe (primary output an Enchanted item -
     Skyy_Ench_* or a VoidCompact Enchanted id such as Greater Essence of Life) adds its inputs as "!cb:<id>" markers only; every other
     recipe (the reverse 1 -> 100 ones included) adds its inputs as before (addInputs: ids + the "!open" / "!e:" / "!nv:" markers).
  2. FOCUS: the recipe a player last crafted in the pocket window (PocketCraftWindow.handleAction -> BenchLink.focus) marks its inputs
     "!f:<id>" (BenchLink.PFOCUS, memory only, per player); BenchLink.union adds those markers while that player's pocket window is
     attached, plus "!bench" while a bench window shares the mirror.
  3. ROOM: the mirror container holds BagMirror.CAP = 512 slots; a rebuild without "!pocket" still fills at most 36 (benches, /craft,
     Furnace: the 0.8.32 layout exactly), the pocket window up to 512 (111 compress bases x 4 stacks + the rest fit; one id is still one line in the section's list however many
     stacks it has; sync / fit0 / quantities / empty / holds walk all CAP slots).
  4. BagMirror.rebuild, when the set holds "!pocket", fills the slots in this order (W = wanted, F = focus, C = compress base, O = rest):
       pocket alone:  W 1 stack each -> F up to 12 -> C 1 -> C up to 4 -> W up to 4 -> O up to 4
       with a bench:  W 1 -> W up to 4 (the bench keeps every slot it had) -> F up to 12 -> C 1 -> C 4 -> O 4
     So every real Fieldcraft ingredient (and every Enchanted item a reverse recipe uses) keeps its slot first, the compress bases share
     the rest (every pile up to 4 stacks = ALL 4 on the first look), and after one craft of a recipe its inputs get up to 12 stacks:
     Enchanted Wheat with 859 Wheat -> ALL = 8, x10 refused (short), 2500 Wheat -> 1200 offered (x10 works, ALL = 12). No virtual stacks for a compress base (it is not "wanted", the
     0.8.30 virtuals only follow wanted ids; the reverse recipes' "!e:" markers block them as before), a virtual entry never gets the
     extra passes. Without "!pocket" the passes are the old three (W 1, W 4, O 4) - byte for byte the same layout.
  Safety unchanged: craftItem(Combined{inventory, section}) takes exactly what the recipe needs per craft, sync() books every removed
  item from the pool by slot, fit / fit0 trim to the pool, the content version moves only when the layout really changes (the focus
  changes only on a pocket craft -> one new layout, no refresh ping-pong).
  No saved-data change, no config row, no migration, no new system / command. ROLLBACK to 0.8.32: safe alone (pocket ALL back to the
  one-stack offer; nothing stored).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.32.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.33.py"))
assert P.has('VERSION = "0.8.32"\n') and P.has("takeOpen(") and not P.has("fieldRecipe("), "not the live generated SkyySacks 0.8.32"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.33 (2026-10-27)"):].rstrip() + "\n"

P.rep('''  a vanilla item and stays; sacks:fn:takeOpen disappears - SkyyShards does not call it yet; the dispatchers go back to their old threads).
"""
''', '''  a vanilla item and stays; sacks:fn:takeOpen disappears - SkyyShards does not call it yet; the dispatchers go back to their old threads).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.32"\n', 'VERSION = "0.8.33"\n')

# ================================================================ 1. fieldRecipe (after addRecipe; addInputs + VoidCompact.idxEnch exist)
P.rep('''  addInputs(s, (({CRR}) o).getInput());
  return true;
}}""", mir))
''', '''  addInputs(s, (({CRR}) o).getInput());
  return true;
}}""", mir))
# 0.8.33 (sacks33): one Fieldcraft recipe into the pocket window's set - a COMPRESS recipe (primary output an Enchanted item) adds its inputs
# as "!cb:<id>" markers only (they share the slots after the real Fieldcraft ingredients); every other recipe adds them as addInputs does
mir.addMethod(CtNewMethod.make(f"""
public static boolean fieldRecipe(java.util.Set s, Object o) {{
  if (s == null || !(o instanceof {CRR})) return false;
  {MQ} po = (({CRR}) o).getPrimaryOutput();
  String out = po == null ? null : po.getItemId();
  boolean cmp = out != null && (out.startsWith("Skyy_Ench_") || {PKG}.VoidCompact.idxEnch(out) >= 0);
  {MQ}[] in = (({CRR}) o).getInput();
  if (!cmp) {{ addInputs(s, in); return true; }}
  for (int i = 0; in != null && i < in.length; i++) {{
    if (in[i] == null) continue;
    if (in[i].getItemId() != null) s.add("!cb:" + in[i].getItemId());
    else if (in[i].getResourceTypeId() != null) s.add("!cb:" + in[i].getResourceTypeId());
  }}
  return false;
}}""", mir))
''')
# marked (after wants; rtsOf exists)
P.rep('''  for (int i = 0; i < r.length; i++) if (s.contains(r[i])) return true;
  return false;
}""", mir))
''', '''  for (int i = 0; i < r.length; i++) if (s.contains(r[i])) return true;
  return false;
}""", mir))
# 0.8.33: does s mark id (or a resource type id has) with the prefix ("!cb:" compress base, "!f:" the pocket focus)
mir.addMethod(CtNewMethod.make("""
public static boolean marked(java.util.Set s, String pfx, String id) {
  if (s == null || id == null) return false;
  if (s.contains(pfx + id)) return true;
  String[] r = rtsOf(id);
  for (int i = 0; i < r.length; i++) if (s.contains(pfx + r[i])) return true;
  return false;
}""", mir))
''')

# ================================================================ 2. rebuild: the pocket order
P.rep('''  int[] stacks = new int[n];
  boolean[] want = new boolean[n];
''', '''  int[] stacks = new int[n];
  boolean[] want = new boolean[n];
  // 0.8.33: the pocket window's classes (compress base, focus) - only when the set holds "!pocket"
  boolean pocket = wanted != null && wanted.contains("!pocket");
  boolean[] cb = new boolean[n];
  boolean[] fo = new boolean[n];
''')
P.rep('''    max[e] = mx;
    want[e] = wanted != null && wants(wanted, id);
  }}
''', '''    max[e] = mx;
    want[e] = wanted != null && wants(wanted, id);
    cb[e] = pocket && marked(wanted, "!cb:", id);   // 0.8.33
    fo[e] = pocket && marked(wanted, "!f:", id);
  }}
''')
P.rep('''  int slot = 0;
  for (int pass = 0; pass < 3 && slot < 36; pass++) {{
    int lim = pass == 0 ? 1 : 4;
    for (int e = 0; e < n && slot < 36; e++) {{
      if (ids[e] == null) continue;
      if (pass < 2 && !want[e]) continue;
      if (pass == 2 && want[e]) continue;
''', '''  // 0.8.33 the passes: cls 0 = wanted, 1 = focus, 2 = compress base, 3 = the rest; lim = stacks per item after that pass.
  // No "!pocket": W 1, W 4, O 4 (the 0.8.32 order). Pocket alone: W 1, F 12, C 1, C 4, W 4, O 4. With a bench: W 1, W 4 first.
  int[] pcls = new int[] {{ 0, 0, 3 }};
  int[] plim = new int[] {{ 1, 4, 4 }};
  if (pocket && wanted.contains("!bench")) {{ pcls = new int[] {{ 0, 0, 1, 2, 2, 3 }}; plim = new int[] {{ 1, 4, 12, 1, 4, 4 }}; }}
  else if (pocket) {{ pcls = new int[] {{ 0, 1, 2, 2, 0, 3 }}; plim = new int[] {{ 1, 12, 1, 4, 4, 4 }}; }}
  int smax = pocket ? CAP : 36;   // 0.8.33: the pocket window may use CAP slots; every other set keeps the 36
  int slot = 0;
  for (int pass = 0; pass < pcls.length && slot < smax; pass++) {{
    int lim = plim[pass];
    int cl = pcls[pass];
    for (int e = 0; e < n && slot < smax; e++) {{
      if (ids[e] == null) continue;
      if (cl == 0 && !want[e]) continue;
      if (cl == 1 && !fo[e]) continue;
      if (cl == 2 && !cb[e]) continue;
      if (cl == 3 && (want[e] || cb[e])) continue;
''')

# ================================================================ 2b. the slot room: CAP slots (the pocket window), 36 for every other set
P.rep("""mir.addConstructor(CtNewConstructor.make(f\"\"\"
public BagMirror(String key) {{""", """# 0.8.33: the container holds CAP slots; rebuild fills at most 36 of them unless the set holds "!pocket" (the pocket window: ~110 compress
# bases + the real Fieldcraft ingredients need more than 36 stacks - one id = one line in the section's list, however many stacks)
mir.addField(CtField.make("public static final int CAP = 512;", mir))
mir.addConstructor(CtNewConstructor.make(f\"\"\"
public BagMirror(String key) {{""")
P.rep("this.cont = new {SIC}((short) 36);", "this.cont = new {SIC}((short) CAP);   // 0.8.33")
P.rep("this.slotIds = new String[36];", "this.slotIds = new String[CAP];")
P.rep("this.slotQty = new int[36];", "this.slotQty = new int[CAP];")
P.rep("""  java.util.HashMap vd = null;
  for (int i = 0; i < 36; i++) {{""", """  java.util.HashMap vd = null;
  for (int i = 0; i < CAP; i++) {{""")
P.rep("""  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb""", """  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < CAP; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb""")
P.rep("""      while (left[e] > 0L && stacks[e] < lim && slot < 36) {{""", """      while (left[e] > 0L && stacks[e] < lim && slot < smax) {{""")
P.rep("""  this.vpair = new java.util.HashMap();   // 0.8.30
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}""", """  this.vpair = new java.util.HashMap();   // 0.8.30
  for (int i = 0; i < CAP; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}""")
P.rep("for (int i = 0; i < 36; i++) if (this.slotIds[i] != null) return true;", "for (int i = 0; i < CAP; i++) if (this.slotIds[i] != null) return true;")
P.rep("""  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  for (int i = 0; i < 36; i++) {{""", """  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  for (int i = 0; i < CAP; i++) {{""")
P.rep("for (int i = 0; i < 36; i++) if (id.equals(this.slotIds[i]))", "for (int i = 0; i < CAP; i++) if (id.equals(this.slotIds[i]))")
P.rep("for (int j = 35; j >= 0", "for (int j = CAP - 1; j >= 0")

# ================================================================ 3. BenchLink: PFOCUS, fieldWanted, focus, union
P.rep('''blink.addField(CtField.make("public static volatile java.util.Set FIELD;", blink))
''', '''blink.addField(CtField.make("public static volatile java.util.Set FIELD;", blink))
# 0.8.33: player uuid -> String[] "!f:<id>" markers of the recipe last crafted in the pocket window (memory only)
blink.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PFOCUS = new java.util.concurrent.ConcurrentHashMap();", blink))
''')
P.rep("""      if (o instanceof @CRR@) @PKG@.BagMirror.addInputs(s, ((@CRR@) o).getInput());
    }
  } catch (Throwable t) { }
  if (!s.isEmpty()) { s.add("!pocket"); FIELD = s; }   // 0.8.30 fixer 2
  return s;
}'''), blink))
""", """      @PKG@.BagMirror.fieldRecipe(s, o);   // 0.8.33: compress recipes -> "!cb:" markers (they no longer crowd the 36 slots)
    }
  } catch (Throwable t) { }
  if (!s.isEmpty()) { s.add("!pocket"); FIELD = s; }   // 0.8.30 fixer 2
  return s;
}'''), blink))
# 0.8.33: the recipe u just crafted in the pocket window - its inputs get up to 12 stacks in the next rebuild (ALL / x10 work)
blink.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void focus(java.util.UUID u, @CRR@ r) {
  if (u == null || r == null) return;
  @MQ@[] in = r.getInput();
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; in != null && i < in.length; i++) {
    if (in[i] == null) continue;
    if (in[i].getItemId() != null) l.add("!f:" + in[i].getItemId());
    else if (in[i].getResourceTypeId() != null) l.add("!f:" + in[i].getResourceTypeId());
  }
  if (l.isEmpty()) PFOCUS.remove(u);
  else PFOCUS.put(u, (String[]) l.toArray(new String[0]));
}\'\'\'), blink))
""")
P.rep("""    if (r.attached && k != null && k.equals(r.key) && r.wanted != null) out.addAll(r.wanted);
  }
  return out;
}'''), blink))
""", """    if (r.attached && k != null && k.equals(r.key) && r.wanted != null) {
      out.addAll(r.wanted);
      // 0.8.33: the pocket window's focus markers; "!bench" = a bench shares the mirror (it keeps W 1 + W 4 first)
      if (r.wanted.contains("!pocket")) {
        String[] f = null;
        if (u != null) f = (String[]) PFOCUS.get(u);
        for (int j = 0; f != null && j < f.length; j++) out.add(f[j]);
      } else out.add("!bench");
    }
  }
  return out;
}'''), blink))
""")
P.rep('''  WARNED.clear();
  FIELD = null;
''', '''  WARNED.clear();
  FIELD = null;
  PFOCUS.clear();   // 0.8.33
''')
# ================================================================ 4. the pocket craft sets the focus
P.rep('''  @IC@ inv = @INVC@.getCombined(store, ref, @INVC@.BACKPACK_STORAGE_HOTBAR);
  cm.craftItem(ref, store, recipe, a.quantity, craftContainer(inv));
''', '''  @IC@ inv = @INVC@.getCombined(store, ref, @INVC@.BACKPACK_STORAGE_HOTBAR);
  try { @PR@ fpr = getPlayerRef(); if (fpr != null) @PKG@.BenchLink.focus(fpr.getUuid(), recipe); } catch (Throwable tf) { }   // 0.8.33
  cm.craftItem(ref, store, recipe, a.quantity, craftContainer(inv));
''')
P.rep('''; Greater Essence of Life opens like an Enchanted item; bridge sacks:fn:takeOpen");''',
      '''; Greater Essence of Life opens like an Enchanted item; bridge sacks:fn:takeOpen; pocket ALL / x10 offer the last recipe's inputs (0.8.33)");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.33 adds no system / command"
P.finish()
