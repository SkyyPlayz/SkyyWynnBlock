"""Derive SkyyGear/build_skyygear_0.3.20.py from the LIVE 0.3.19 (build_skyygear_0.3.19.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_19_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_20_patch.py      then      python SkyyGear/build_skyygear_0.3.20.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.20.py   (--static runs without jars / Assets.zip)

0.3.20 (2026-10-17) = SALVAGEBENCH HOOK (lean follow-up of 0.3.19 patch item 10 h; research/Pack-Drops-Spec.md Q15). Skyy's popup answer,
word for word (docs/answered/gear.md 2026-10-17): Q "...The Armory's own Salvagebench gives back 100% of the materials from its pieces (a
Demon piece -> 6 Adamantite ore + 30 Fire essence). With mob drops that becomes a big material source outside our Requip salvage rules
(drops give 10%). Block salvaging rolled (dropped / identified) pieces at their bench?" -> "Yes, Requip only (Recommended)". And today:
"Start the Salvagebench hook round next."
WHY A TICK HOOK: 0.3.19 blocks it only for crafting that fires CraftRecipeEvent$Pre (SkyySacks /craft lists Salvagebench recipes as an
instant bench). The PLACED Salvagebench is a vanilla Processing bench (Bench_Salvage: Type Processing, one input slot with
FilterValidIngredients, 4 output slots, no fuel, Id "Salvagebench"; The Armory adds its Salvage_* recipes to it): it runs in
BenchSystems$ProcessingBenchTick -> ProcessingBenchBlock.advanceProcessing -> tryCompleteOneRecipe -> ItemContainer.removeMaterials and fires
no event (VERIFIED bytecode 0.7, again this round). Its tick re-checks the recipe every tick (checkForRecipeUpdate, getInputMaterials ->
getSlotMaterialsToRemove on the INPUT container; nothing there = setInputProgress(0) + clearCurrentRecipe) - so a stack that is not in the
input container when that tick runs can never be salvaged. Bench_Salvage has no fuel, so ProcessingBenchBlock.setActive(false) would NOT
stop it (advanceProcessing only checks "active" for a bench with fuel) - "leave it in the input and stop the recipe" has no safe form; the
piece always leaves the input.
  1. GearBenchSys (EntityTickingSystem on the ChunkStore, query ProcessingBenchBlock; ordered BEFORE BenchSystems$ProcessingBenchTick by a
     SystemDependency, the GearChestMark / StashSystem pattern; an unordered GearBenchSysU + one WARN if the order is refused). Per Processing
     bench per tick it reads its input slots (Salvagebench: 1) and stops at once unless a stack is a pack table id (GearPackId.has: a hash
     lookup; part.packDrops off = nothing); only then is the bench id read (ProcessingBenchBlock.getBench().getId() = "Salvagebench" - the id
     the engine itself passes to CraftingPlugin.getBenchRecipes) and GearBench.onBench runs. No chunk scans, no per-world lists.
  2. GearBench.sweep: every input stack with GearPack.salvBlocked semantics (a pack piece whose SkyyGear document is not a craft one: drop /
     chest / boss bag / identified) leaves the input; crafted pieces, undocumented pieces and vanilla items are untouched (they still salvage
     at the bench). Where it goes, first that works: (a) an EMPTY slot of the bench's output container (written with the filter off - the
     output has the ALLOW_OUTPUT_ONLY global filter, the engine writes its own outputs the same way), (b) the storage / hotbar / backpack of a
     player who has the bench window open in this world, (c) an item entity on top of the bench (ItemComponent.generateItemDrops +
     EntityStore.addEntities SPAWN - what vanilla's own ProcessingBenchBlock.ejectItems does with output that does not fit), (d) nothing
     worked = put back into its input slot + WARN + gear.log (the bench may then salvage it - only when every write above failed).
     ITEM SAFETY: one world thread; SALV-BEGIN (the document) is in gear.log and flushed BEFORE the stack leaves; the stack leaves the input
     first (never a second copy), every write is checked by reading the slot back (id, quantity, metadata), the item is counted over input +
     output + the viewers' containers before and after (a mismatch = WARN + SALV-COUNT line); a drop that throws = logged UNSURE, never put
     back (a copy is worse than a logged loss - the GearMerge rule).
  3. The players with that bench's window open (BenchBlock.getWindows -> Window.getPlayerRef) get ONE red chat line per 5 s: "<item> is a
     dropped / identified piece - salvage it with Requip's SALVAGE button, not at a Salvagebench." + where it went. gear.log: SALV-BLOCK
     <how> <world x y z> <id> <viewers> <document>.
  4. /gear loot (packText) adds the guard state (ordered / UNORDERED / off) + counters: blocked, output, inventory, ground, put back, unsure.
  5. CRITIC FIXES (same version): M1 every write is GearBench.tryPut: 1 = read back exactly, 0 = the slot is empty again (a container
     that stored a changed / normalised copy has it taken out again - SALV-UNDO), -1 = something it cannot take back out stays there ->
     the move stops as UNSURE (never a second copy at the next target). M2 nothing after the input removal can skip the put-back: the
     targets are tried inside one catch-all, a container that throws while read is no target (safeEmpty), an exception before anything
     landed = put back into the input (else the first empty output slot, else SALV-LOST with the document); a drop that throws = UNSURE.
     L3 a bench whose piece had to be put back rests 5 s (GearBench.COOL / COOLMS: no SALV lines + log flush every tick). L5 checked:
     The Armory 1.23.0's 23 Salvagebench recipes take 4 s (19) or 12 s (4), vanilla's 4 s or 0.5 s - all far over one tick, so even the
     unordered GearBenchSysU (it can run AFTER the bench tick - the engine then orders the two freely) takes a piece out a tick after it
     went in, long before a recipe completes; only a game-time jump inside that one tick (the bench tick's dt is game time) could finish
     it. L6 accepted, no start INFO line: the load catch-up (setupSlots) runs before ANY tick system, so a start check would only see
     pieces the bench left over - and GearBenchSys moves those out on its first tick anyway (the KNOWN LIMIT below). L7 isSalv =
     "Salvagebench".equals (the exact id the engine passes to getBenchRecipes).
Learned from (read only, CLAUDE rule "check existing mods"): SimpleEnchantments 1.2.1's EnchantmentSalvageSystem tracks salvage benches
through ItemContainer.registerChangeEvent on ProcessingBenchBlock.getInputContainer - not in the pack, and an event hook misses benches
loaded with a piece already inside and automation that writes without the player's InventoryChangeEvent; the tick hook sees every input.
GlymeraBluestone (hoppers) / Clay Factoria (workers) also touch bench containers - none is in the pack; a hopper that feeds a blocked piece
again just sees it moved out again (output -> ground when full), never consumed.
KNOWN LIMIT (UNVERIFIED in game): ProcessingBenchLifecycle.onEntityAdded -> setupSlots catches a bench up on load (advanceProcessing with up
to 86400 s of game time) BEFORE any tick system. A blocked piece can only be inside a bench at a chunk save if it was put in during the
same world tick the chunk unloaded / the server stopped (GearBenchSys moves it out on the next tick), so this is a narrow window, logged by
nothing; a RefSystem before ProcessingBenchLifecycle would close it (the bench id is not known there yet - next round if Skyy wants it).
Commands: none new. Config: none new (part.packDrops off = the guard does nothing). Classes: + GearBench, GearBenchDrop, GearBenchSys,
GearBenchSysU; GearPool (SN / SORD + packText), GearFx (setup registers the system). SAVED DATA: none.
Unchanged on purpose: 0.3.19's CraftRecipeEvent$Pre salvage veto (/craft) and its wording; Requip SALVAGE; crafted pieces still salvage at
the bench; vanilla gear still salvages at the bench (the rule is pack pieces only, GearPack.salvBlocked).
ROLLBACK 0.3.20 -> 0.3.19: safe (no saved data, no config rows); the placed Salvagebench then salvages dropped pack pieces again.
"""
import os
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.19.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.20.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.19"' in s and "GENERATED by tools/gear_0_3_19_patch.py" in s, "not the generated 0.3.19 script"
assert "GearBenchSys" not in s and "GearBench" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.19":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.19" % _set.get("SkyyGear"))

HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.20 (2026-10-17)"):].rstrip() + "\n"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.19 - build script (javassist via jpype). GENERATED by tools/gear_0_3_19_patch.py from the LIVE 0.3.18 (itself GENERATED by
tools/gear_0_3_18_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.19.py -> SkyyGear/SkyyGear-0.3.19.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.19.py

''', '''"""SkyyGear 0.3.20 - build script (javassist via jpype). GENERATED by tools/gear_0_3_20_patch.py from the LIVE 0.3.19 (itself GENERATED by
tools/gear_0_3_19_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.20.py -> SkyyGear/SkyyGear-0.3.20.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.20.py

''' + NOTE + '''
--- 0.3.19 notes ---
''')
rep('VERSION = "0.3.19"\n', 'VERSION = "0.3.20"\n')

# ================================================================================================================ GearPool: guard counters + /gear loot
rep('''F(gpool, "public static final long[] BN = new long[7];")
''', '''F(gpool, "public static final long[] BN = new long[7];")
# 0.3.20 Salvagebench guard (GearBench): 0 blocked pieces seen, 1 -> output, 2 -> a viewer's inventory, 3 -> on the bench (item entity),
# 4 put back (every write failed), 5 unsure (a drop threw - logged, never put back), 6 count mismatches. SORD: 0 off, 1 ordered, 2 unordered
F(gpool, "public static final long[] SN = new long[7];")
F(gpool, "public static volatile int SORD = 0;")
''')
rep(''' + ", zone unknown " + BN[4] + ", same fight " + BN[6] + ", opened from Mythic sets " + BN[5];''',
    ''' + ", zone unknown " + BN[4] + ", same fight " + BN[6] + ", opened from Mythic sets " + BN[5]
    + "; Salvagebench guard " + (SORD == 1 ? "on" : SORD == 2 ? "on (UNORDERED)" : "OFF") + ": " + SN[0] + " dropped pieces taken out - output "
    + SN[1] + ", inventory " + SN[2] + ", on the bench " + SN[3] + ", put back " + SN[4] + ", unsure " + SN[5] + ", count mismatches " + SN[6];''')

# ================================================================================================================ the classes (before GearFx.setup)
SALV = r'''# ================================================================= 0.3.20 SALVAGEBENCH HOOK (tools/gear_0_3_20_patch.py; Pack-Drops-Spec Q15)
# Skyy 2026-10-17 popup "Yes, Requip only (Recommended)": a dropped / identified pack piece never salvages for 100 % at the placed
# Salvagebench. The bench is a vanilla Processing bench: BenchSystems$ProcessingBenchTick takes the recipe's materials from
# ProcessingBenchBlock.getInputContainer() and fires no event (VERIFIED bytecode 0.7) - GearBenchSys runs BEFORE it and takes such a piece
# out of the input first (output slot -> a viewer's inventory -> on the bench; counted, logged first, never copied).
SV = {"PBBK": "com.hypixel.hytale.builtin.crafting.component.ProcessingBenchBlock",
      "BBLK": "com.hypixel.hytale.builtin.crafting.component.BenchBlock",
      "BNCH": "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench",
      "WNDW": "com.hypixel.hytale.server.core.entity.entities.player.windows.Window"}
for _k in SV:
    assert _k not in T, "0.3.20 token clashes: " + _k
    assert re.match(r"^[A-Z]+$", _k), _k
T.update(SV)
SALV_TICK = "com.hypixel.hytale.builtin.crafting.system.BenchSystems$ProcessingBenchTick"
for c, m in ((SV["PBBK"], "getComponentType"), (SV["PBBK"], "getInputContainer"), (SV["PBBK"], "getOutputContainer"), (SV["PBBK"], "getBench"),
             (SV["BBLK"], "getComponentType"), (SV["BBLK"], "getWindows"), (SV["BNCH"], "getId"), (SV["WNDW"], "getPlayerRef"),
             (IC, "setItemStackForSlot"), (IC, "removeItemStackFromSlot"), (IC, "getItemStack"), (IC, "getCapacity"),
             (PB["BSI"], "getComponentType"), (PB["BSI"], "getSectionRef"), (PB["BSI"], "getIndex"), (PB["CHS"], "getWorld"),
             (WLD, "getEntityStore"), (EST, "getStore"), (PB["ITC"], "generateItemDrops"), (ST, "addEntities"), (PB["ADDR"], "SPAWN"),
             (SALV_TICK, "tick"), (SALV_TICK, "getQuery")):
    B.probe(pool, c, m)
# the engine facts this hook stands on (re-read from the server jar at every build - a change stops the build)
_sbt = _calls(SALV_TICK, "tick")
assert _sbt.find("ProcessingBenchBlock.checkForRecipeUpdate") >= 0 and _sbt.find("CraftingManager.getInputMaterials") > _sbt.find("ProcessingBenchBlock.checkForRecipeUpdate")
assert _sbt.find("ProcessingBenchBlock.getInputContainer") > _sbt.find("CraftingManager.getInputMaterials") and "ItemContainer.getSlotMaterialsToRemove" in _sbt
assert _sbt.find("ProcessingBenchBlock.advanceProcessing") > _sbt.find("ItemContainer.getSlotMaterialsToRemove"), "the bench tick no longer re-reads its input before processing"
_sbc = _calls(SV["PBBK"], "tryCompleteOneRecipe")
assert "ProcessingBenchBlock.inputContainer" in _sbc and "ItemContainer.removeMaterials" in _sbc, "a Processing bench no longer takes its materials from its input container"
assert "FilterType.ALLOW_OUTPUT_ONLY" in _calls(SV["PBBK"], "setupSlots"), "the bench output filter changed (GearBench writes the output with the filter off)"
assert str(pool.get(SV["PBBK"]).getDeclaredMethod("getBench").getReturnType().getName()) == SV["BNCH"]
assert any("(SLcom/hypixel/hytale/server/core/inventory/ItemStack;Z)" in str(m_.getSignature()) for m_ in pool.get(IC).getDeclaredMethods() if str(m_.getName()) == "setItemStackForSlot")
assert any(str(m_.getSignature()).startswith("(SZ)") for m_ in pool.get(IC).getDeclaredMethods() if str(m_.getName()) == "removeItemStackFromSlot")
import json as _json
_bsv = _json.loads(AZ.read("Server/Item/Items/Bench/Bench_Salvage.json").decode("utf-8-sig"))["BlockType"]["Bench"]
assert _bsv.get("Type") == "Processing" and _bsv.get("Id") == "Salvagebench" and not _bsv.get("Fuel"), "Bench_Salvage changed: %s" % _bsv
print("0.3.20 Salvagebench hook: Bench_Salvage = Processing bench %s (%d input slot(s), %s output slots, no fuel) - GearBenchSys BEFORE %s"
      % (_bsv.get("Id"), len(_bsv.get("Input") or []), _bsv.get("OutputSlotsCount"), SALV_TICK.rsplit(".", 1)[1]))
gbench = mk("GearBench")                    # the sweep: blocked input stacks out (output -> viewer -> on the bench), counted, logged first
gbdrop = mk("GearBenchDrop")                # Function: one stack as an item entity on top of the bench (vanilla's ejectItems way)
gbsys = mk("GearBenchSys", ETS)             # ChunkStore EntityTickingSystem on ProcessingBenchBlock, BEFORE BenchSystems$ProcessingBenchTick
F(gbench, 'public static final String BENCH = "Salvagebench";')
F(gbench, "public static final java.util.concurrent.ConcurrentHashMap SAID = new java.util.concurrent.ConcurrentHashMap();")
F(gbench, "public static volatile long QUIET = 5000L;")
# critic L3: a bench whose piece had to be put back rests COOLMS (5 s) - no SALV lines + gear.log flush every tick
F(gbench, "public static final java.util.concurrent.ConcurrentHashMap COOL = new java.util.concurrent.ConcurrentHashMap();")
F(gbench, "public static volatile long COOLMS = 5000L;")
M(gbench, r"""
public static boolean isSalv(String b) { return BENCH.equals(b); }""")          # critic L7: the exact engine id
M(gbench, r"""
public static String benchId(@PBBK@ pb) {
  try {
    @BNCH@ b = pb == null ? null : pb.getBench();
    return b == null ? null : b.getId();
  } catch (Throwable t) { return null; }
}""")
M(gbench, r"""
public static boolean emptyAt(@IC@ c, int i) {
  @IS@ x = c.getItemStack((short) i);
  return x == null || x.isEmpty();
}""")
# the slot holds exactly this stack (id, quantity, metadata) - every write is checked this way
M(gbench, r"""
public static boolean sameAt(@IC@ c, int i, @IS@ s) {
  if (c == null || s == null || i < 0 || i >= c.getCapacity()) return false;
  @IS@ x = c.getItemStack((short) i);
  if (x == null || x.isEmpty() || x.getQuantity() != s.getQuantity() || !String.valueOf(s.getItemId()).equals(x.getItemId())) return false;
  return x.getMetadata() == null ? s.getMetadata() == null : x.getMetadata().equals(s.getMetadata());
}""")
M(gbench, r"""
public static int emptySlot(@IC@ c) {
  if (c == null) return -1;
  for (int i = 0; i < c.getCapacity(); i++) if (emptyAt(c, i)) return i;
  return -1;
}""")
# critic M2: a container that throws while being read is simply no target (-1), never an exception in the middle of a move
M(gbench, r"""
public static int safeEmpty(@IC@ c) {
  try { return emptySlot(c); } catch (Throwable t) { return -1; }
}""")
# write s into EMPTY slot j; filter false for the bench output (ALLOW_OUTPUT_ONLY - the engine writes its own outputs with the filter off).
# 1 = it is there (read back: id, quantity, metadata), 0 = nothing is left in the slot, -1 = UNKNOWN (something stays there that is not
# exactly s and could not be taken back out, or the slot cannot be read after the write) - the caller then stops: never a second copy.
# Critic M1: a container that stores a changed (normalised) copy gets that copy taken out again (0), so the next target never adds one.
M(gbench, r"""
public static int tryPut(@IC@ c, int j, @IS@ s, boolean filter) {
  if (c == null || s == null || j < 0) return 0;
  try { if (j >= c.getCapacity() || !emptyAt(c, j)) return 0; } catch (Throwable t0) { return 0; }
  try { c.setItemStackForSlot((short) j, s, filter); } catch (Throwable x) { @PKG@.Gear.warnOnce("salvput", "Salvagebench guard: a container refused a write: " + x); }
  try {
    if (sameAt(c, j, s)) return 1;
    if (emptyAt(c, j)) return 0;
    try { c.removeItemStackFromSlot((short) j, false); } catch (Throwable x2) { }
    if (emptyAt(c, j)) {
      @PKG@.GearLog.line("SALV-UNDO " + s.getItemId() + " - a container kept a changed copy, taken out again");
      return 0;
    }
  } catch (Throwable x3) { }
  @PKG@.Gear.warnOnce("salvkept", "Salvagebench guard: a container kept a changed copy of " + s.getItemId() + " that could not be taken out - see gear.log (SALV-UNSURE)");
  return -1;
}""")
M(gbench, r"""
public static int cnt(@IC@[] cs, String id) {
  int n = 0;
  for (int k = 0; cs != null && k < cs.length; k++) { try { n = n + @PKG@.GearPackGive.cnt(cs[k], id); } catch (Throwable t) { } }
  return n;
}""")
M(gbench, r"""
public static String docText(@IS@ s) {
  try {
    @BD@ g = s == null ? null : @PKG@.GearData.gearDoc(s.getMetadata());
    return g == null ? "plain" : g.toJson();
  } catch (Throwable t) { return "?"; }
}""")
# the viewers: players with this bench's window open (BenchBlock.getWindows: UUID -> BenchWindow, a Window)
M(gbench, r"""
public static @PR@[] viewers(@BBLK@ bb) {
  java.util.ArrayList l = new java.util.ArrayList();
  try {
    java.util.Map m = bb == null ? null : bb.getWindows();
    Object[] ws = m == null ? new Object[0] : m.values().toArray();
    for (int k = 0; k < ws.length; k++) {
      if (!(ws[k] instanceof @WNDW@)) continue;
      @PR@ pr = ((@WNDW@) ws[k]).getPlayerRef();
      if (pr != null && !l.contains(pr)) l.add(pr);
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("salvview", "Salvagebench guard: the bench windows could not be read: " + t); }
  @PR@[] out = new @PR@[l.size()];
  for (int k = 0; k < out.length; k++) out[k] = (@PR@) l.get(k);
  return out;
}""")
# a viewer's storage, hotbar, backpack (the GearPackGive order) - only while their Ref lives in this world's entity store
M(gbench, r"""
public static @IC@[] invs(@PR@[] vs, @ST@ es) {
  java.util.ArrayList l = new java.util.ArrayList();
  for (int k = 0; vs != null && k < vs.length; k++) {
    try {
      @PR@ pr = vs[k];
      @REF@ r = pr == null || !pr.isValid() ? null : pr.getReference();
      if (r == null || !r.isValid() || (es != null && r.getStore() != es)) continue;
      @INV@ inv = @PKG@.GearStamp.invOf(pr);
      if (inv == null) continue;
      @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
      for (int i = 0; i < cs.length; i++) if (cs[i] != null) l.add(cs[i]);
    } catch (Throwable t) { }
  }
  @IC@[] out = new @IC@[l.size()];
  for (int k = 0; k < out.length; k++) out[k] = (@IC@) l.get(k);
  return out;
}""")
M(gbench, r"""
public static String names(@PR@[] vs) {
  StringBuilder b = new StringBuilder();
  for (int k = 0; vs != null && k < vs.length; k++) {
    if (vs[k] == null) continue;
    if (b.length() > 0) b.append(',');
    try { b.append(vs[k].getUsername()); } catch (Throwable t) { b.append('?'); }
  }
  return b.length() == 0 ? "nobody" : b.toString();
}""")
# one red line per viewer per QUIET ms (5 s)
M(gbench, r"""
public static int tell(@PR@[] vs, String id, String how) {
  long now = System.currentTimeMillis();
  int n = 0;
  if (SAID.size() > 256) SAID.clear();
  String w = "output".equals(how) ? "It was moved to the bench's output slot."
    : "inventory".equals(how) ? "The bench's output is full - it went back into your inventory."
    : "The bench's output and your inventory are full - it lies on the bench.";
  for (int k = 0; vs != null && k < vs.length; k++) {
    try {
      @PR@ pr = vs[k];
      if (pr == null || pr.getUuid() == null) continue;
      Object last = SAID.get(pr.getUuid());
      if (last instanceof Long && now - ((Long) last).longValue() < QUIET && now >= ((Long) last).longValue()) continue;
      SAID.put(pr.getUuid(), Long.valueOf(now));
      pr.sendMessage(@MSG@.raw("[Gear] " + @PKG@.Gear.itemName(id) + " is a dropped / identified piece - salvage it with Requip's SALVAGE button, not at a Salvagebench. " + w).color(@PKG@.GearDefs.C_BAD));
      n++;
    } catch (Throwable t) { }
  }
  return n;
}""")
# one blocked stack out of input slot i. Returns where it went ("output" / "inventory" / "ground" / "unsure") or null (put back / refused).
M(gbench, r"""
public static String move(@IC@ in, int i, @IS@ s, @IC@ out, @IC@[] inv, java.util.function.Function drop, String where, String who) {
  String id = s.getItemId();
  int q = s.getQuantity();
  @IC@[] all = new @IC@[inv.length + 2];
  all[0] = in;
  all[1] = out;
  for (int k = 0; k < inv.length; k++) all[k + 2] = inv[k];
  int before = cnt(all, id);
  String doc = docText(s);
  @PKG@.GearLog.line("SALV-BEGIN " + where + " " + id + " x" + q + " (" + who + ") " + doc);
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }          // the document is ON DISK before the stack leaves the input
  // (a) the stack leaves the input first: a crash after this can only lose it (its document is in SALV-BEGIN), never copy it
  try { in.removeItemStackFromSlot((short) i, false); } catch (Throwable x1) { @PKG@.Gear.warnOnce("salvrm", "Salvagebench guard: the input refused the removal: " + x1); }
  boolean gone = false;
  try { gone = emptyAt(in, i); } catch (Throwable x1b) { gone = false; }
  if (!gone) {
    @PKG@.GearPool.SN[4] = @PKG@.GearPool.SN[4] + 1L;
    COOL.put(where, Long.valueOf(System.currentTimeMillis()));          // critic L3: this bench rests COOLMS
    @PKG@.GearLog.line("SALV-FAILED " + where + " " + id + " - the input slot kept it (the bench may salvage it)");
    @PKG@.Gear.warnOnce("salvkeep:" + where, "Salvagebench guard: a dropped " + id + " could not be taken out of the bench at " + where + " - see gear.log");
    return null;
  }
  String how = null;
  int r = 0;
  try {          // critic M2: nothing after the removal may skip the put-back - each step leaves a known state (r), an exception keeps it
    r = tryPut(out, safeEmpty(out), s, false);                                              // (b) an empty output slot
    if (r == 1) how = "output";
    for (int k = 0; how == null && r == 0 && k < inv.length; k++) {                         // (c) a viewer
      r = tryPut(inv[k], safeEmpty(inv[k]), s, true);
      if (r == 1) how = "inventory";
    }
    if (how == null && r == 0 && drop != null) {                                            // (d) on the bench, like vanilla's output overflow
      r = -1;          // a drop that throws may have spawned it already: unsure, never put back
      Object d = drop.apply(s);
      r = 0;
      if (Boolean.TRUE.equals(d)) { how = "ground"; r = 1; }
    }
  } catch (Throwable x2) {
    @PKG@.Gear.warn("Salvagebench guard: moving " + id + " at " + where + " failed (" + x2 + ")" + (r == 0 ? " - putting it back" : " - its document is in gear.log (SALV-UNSURE)"));
  }
  if (how == null && r != 0) how = "unsure";
  if (how == null) {                                                                        // (e) nothing took it: back where it was
    int b = tryPut(in, i, s, false);
    boolean toOut = false;
    if (b == 0) { b = tryPut(out, safeEmpty(out), s, false); toOut = true; }
    if (b == 1 && toOut) how = "output";                                                     // a second output try worked: a normal move
    else if (b == -1) how = "unsure";
    else {
      @PKG@.GearPool.SN[b == 1 ? 4 : 5] = @PKG@.GearPool.SN[b == 1 ? 4 : 5] + 1L;
      COOL.put(where, Long.valueOf(System.currentTimeMillis()));          // critic L3: this bench rests COOLMS
      @PKG@.GearLog.line((b == 1 ? "SALV-FAILED " : "SALV-LOST ") + where + " " + id + " x" + q + (b == 1 ? " - nowhere to put it, back in the input (the bench may salvage it)" : " - nowhere to put it and the input refused it back ") + (b == 1 ? "" : doc));
      @PKG@.Gear.warn("Salvagebench guard: " + id + " at " + where + (b == 1 ? " had nowhere to go and is back in the bench input" : " could not be put anywhere - its document is in gear.log (SALV-LOST)"));
      return null;
    }
  }
  int after = cnt(all, id);
  int want = "output".equals(how) || "inventory".equals(how) ? before : before - q;
  if (!"unsure".equals(how) && after != want) {
    @PKG@.GearPool.SN[6] = @PKG@.GearPool.SN[6] + 1L;
    @PKG@.Gear.warn("SALVAGE GUARD COUNT MISMATCH " + id + " at " + where + ": " + before + " before, " + after + " after, want " + want + " (" + how + ")");
    @PKG@.GearLog.line("SALV-COUNT " + where + " " + id + " before " + before + " after " + after + " want " + want + " " + how);
  }
  int c = "output".equals(how) ? 1 : "inventory".equals(how) ? 2 : "ground".equals(how) ? 3 : 5;
  @PKG@.GearPool.SN[c] = @PKG@.GearPool.SN[c] + 1L;
  @PKG@.GearLog.line(("unsure".equals(how) ? "SALV-UNSURE " : "SALV-BLOCK " + how + " ") + where + " " + id + " x" + q + " (" + who + ") " + doc);
  return how;
}""")
# every blocked input stack of one bench (the tick calls it only for a Salvagebench); returns how many left the input
M(gbench, r"""
public static int sweep(@IC@ in, @IC@ out, @PR@[] vs, @ST@ es, java.util.function.Function drop, String where) {
  if (in == null) return 0;
  long now = System.currentTimeMillis();
  Object cl = where == null ? null : COOL.get(where);
  if (cl instanceof Long && now - ((Long) cl).longValue() < COOLMS && now >= ((Long) cl).longValue()) return 0;          // critic L3
  if (COOL.size() > 256) COOL.clear();
  int moved = 0;
  @IC@[] inv = null;
  for (int i = 0; i < in.getCapacity(); i++) {
    @IS@ s = in.getItemStack((short) i);
    if (s == null || s.isEmpty() || !@PKG@.GearPack.salvBlocked(s.getItemId(), s.getMetadata())) continue;
    @PKG@.GearPool.SN[0] = @PKG@.GearPool.SN[0] + 1L;
    if (inv == null) inv = invs(vs, es);
    String how = move(in, i, s, out, inv, drop, where, names(vs));
    if (how == null) continue;
    moved++;
    tell(vs, s.getItemId(), how);
  }
  return moved;
}""")
# the block position of a block entity (vanilla ProcessingBenchTick's own formula: BlockStateInfo index in its ChunkSection)
M(gbench, r"""
public static int[] pos(@ACH@ chunk, int idx, @ST@ store) {
  try {
    @BSI@ bsi = (@BSI@) chunk.getComponent(idx, @BSI@.getComponentType());
    @REF@ sr = bsi == null ? null : bsi.getSectionRef();
    if (sr == null || !sr.isValid()) return null;
    @CSEC@ cs = (@CSEC@) store.getComponent(sr, @CSEC@.getComponentType());
    if (cs == null) return null;
    int bi = bsi.getIndex();
    return new int[] { @CHU@.worldCoordFromLocalCoord(cs.getX(), @CHU@.xFromIndex(bi)), @CHU@.worldCoordFromLocalCoord(cs.getY(), @CHU@.yFromIndex(bi)), @CHU@.worldCoordFromLocalCoord(cs.getZ(), @CHU@.zFromIndex(bi)) };
  } catch (Throwable t) { return null; }
}""")
F(gbdrop, "public @ST@ es;")
F(gbdrop, "public @VEC@ at;")
gbdrop.addInterface(pool.get("java.util.function.Function"))
C(gbdrop, "public GearBenchDrop(@ST@ es, @VEC@ at) { this.es = es; this.at = at; }")
M(gbdrop, r"""
public Object apply(Object o) {
  if (this.es == null || this.at == null || !(o instanceof @IS@)) return Boolean.FALSE;
  java.util.ArrayList l = new java.util.ArrayList();
  l.add((@IS@) o);
  @HLDR@[] hs = @ITC@.generateItemDrops(this.es, l, this.at, new @RTF@());
  if (hs == null || hs.length == 0) return Boolean.FALSE;
  @REF@[] rs = this.es.addEntities(hs, @ADDR@.SPAWN);
  return Boolean.valueOf(rs != null && rs.length > 0 && rs[0] != null);
}""")
M(gbench, r"""
public static int onBench(@PBBK@ pb, @ACH@ chunk, int idx, @ST@ store) {
  @BBLK@ bb = (@BBLK@) chunk.getComponent(idx, @BBLK@.getComponentType());
  @PR@[] vs = viewers(bb);
  @ST@ es = null;
  String wn = "?";
  try {
    Object ext = store.getExternalData();
    if (ext instanceof @CHS@) {
      @WLD@ w = ((@CHS@) ext).getWorld();
      if (w != null) { wn = w.getName(); es = w.getEntityStore().getStore(); }
    }
  } catch (Throwable t) { es = null; }
  int[] p = pos(chunk, idx, store);
  String where = wn + " " + (p == null ? "?" : p[0] + " " + p[1] + " " + p[2]);
  @PKG@.GearBenchDrop d = es == null || p == null ? null : new @PKG@.GearBenchDrop(es, new @VEC@(p[0] + 0.5, p[1] + 1.1, p[2] + 0.5));
  return sweep(pb.getInputContainer(), pb.getOutputContainer(), vs, es, d, where);
}""")
F(gbsys, "public java.util.Set deps;")
F(gbsys, "public static Class TICK;")
F(gbsys, "public @QRY@ query;")
C(gbsys, r"""
public GearBenchSys(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  if (ordered && TICK != null) this.deps.add(new @SDEP@(@ORD@.BEFORE, TICK));
  this.query = null;
}""")
M(gbsys, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = (@QRY@) @PBBK@.getComponentType();
  return this.query;
}""")
M(gbsys, "public java.util.Set getDependencies() { return this.deps; }")
M(gbsys, "public boolean isParallel(int a, int b) { return false; }")
# per Processing bench per tick: its input slots (Salvagebench: 1); out at once unless a stack is a pack table id - only then the bench id
M(gbsys, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PBBK@ pb = (@PBBK@) chunk.getComponent(idx, @PBBK@.getComponentType());
    @IC@ in = pb == null ? null : pb.getInputContainer();
    if (in == null) return;
    boolean any = false;
    for (int i = 0; i < in.getCapacity() && !any; i++) {
      @IS@ s = in.getItemStack((short) i);
      any = s != null && !s.isEmpty() && @PKG@.GearPackId.has(s.getItemId());
    }
    if (!any || !@PKG@.GearBench.isSalv(@PKG@.GearBench.benchId(pb))) return;
    @PKG@.GearBench.onBench(pb, chunk, idx, store);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("salvsys", "Salvagebench guard tick failed: " + t); }
}""")
gbsysU = mk("GearBenchSysU", PKG + ".GearBenchSys")
C(gbsysU, "public GearBenchSysU() { super(false); }")
G320_CLASSES = [gbench, gbdrop, gbsys, gbsysU]

'''
before('''# ================================================================= GearFx.setup: every PART B registration (PARTB_SETUP calls it)
''', SALV)
# the registration (GearFx.setup, with the other ChunkStore systems): ordered first, an unordered fallback + one WARN (the 0.1.x pattern)
before('''  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearFxInvSys()); } catch (Throwable t9) { @PKG@.Gear.warn("GearFxInvSys could not be registered: " + t9); }
''', '''  // 0.3.20 Salvagebench guard (Skyy 2026-10-17 "Yes, Requip only"): BEFORE BenchSystems$ProcessingBenchTick on the ChunkStore
  Class sbt = cls("com.hypixel.hytale.builtin.crafting.system.BenchSystems$ProcessingBenchTick");
  if (sbt == null) @PKG@.Gear.warn("BenchSystems$ProcessingBenchTick not found - no Processing benches; the Salvagebench guard is off");
  else {
    try { @PKG@.GearBenchSys.TICK = sbt; pl.getChunkStoreRegistry().registerSystem(new @PKG@.GearBenchSys(true)); @PKG@.GearPool.SORD = 1; }
    catch (Throwable t11) {
      @PKG@.Gear.warn("could not order the Salvagebench guard before BenchSystems$ProcessingBenchTick (" + t11 + ") - unordered fallback: a dropped piece is still taken out of the bench before its 4 s recipe ends");
      try { pl.getChunkStoreRegistry().registerSystem(new @PKG@.GearBenchSysU()); @PKG@.GearPool.SORD = 2; } catch (Throwable t11b) { @PKG@.Gear.warn("GearBenchSysU could not be registered - the Salvagebench guard is off: " + t11b); }
    }
  }
''')

# ================================================================================================================ the jar: classes
rep('''+ G317_CLASSES + G318_CLASSES + G319_CLASSES''', '''+ G317_CLASSES + G318_CLASSES + G319_CLASSES + G320_CLASSES''')

# ================================================================================================================ checks on the result
_i = s.index
assert _i('gpack = mk("GearPack")') < _i('gbench = mk("GearBench")') and _i("public static boolean salvBlocked(") < _i("public static int sweep(@IC@ in, @IC@ out")
assert _i('gpgv = mk("GearPackGive")') < _i('gbench = mk("GearBench")') and _i('gsp  = mk("GearStamp")') < _i('gbench = mk("GearBench")')
assert _i("public static String move(@IC@ in, int i") < _i("public static int sweep(@IC@ in, @IC@ out") < _i("public static int onBench(@PBBK@ pb") < _i("public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {\n  try {\n    @PBBK@")
assert _i("public Object apply(Object o) {\n  if (this.es == null") < _i("public static int onBench(@PBBK@ pb")
assert _i('gbsysU = mk("GearBenchSysU"') < _i("# ================================================================= GearFx.setup: every PART B registration") < _i("new @PKG@.GearBenchSys(true)")
assert _i('F(gpool, "public static final long[] SN = new long[7];")') < _i("public static synchronized String packText()") < _i("public static int sweep(@IC@ in, @IC@ out")
assert s.count("registerSystem(") == SYS0 + 2, "exactly the two new registrations (ordered + unordered fallback)"
assert s.count("registerCommand(") == CMD0, "no new command"
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.19 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.19 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
