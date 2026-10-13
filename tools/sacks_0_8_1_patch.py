"""Derive SkyySacks/build_skyysacks_0.8.1.py from the SET pin 0.8.0 (the GENERATED build_skyysacks_0.8.0.py; edit THIS file, then
regenerate: python tools/sacks_0_8_1_patch.py; never re-run sacks_0_8_0_patch.py on top of it).
Run:  python tools/sacks_0_8_1_patch.py   then   python SkyySacks/build_skyysacks_0.8.1.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.1.py

0.8.1 = THE ENCHANTED MATERIALS GO IN THE VOID (research/Gathering-Shards-Spec.md section 11 phase 1 = research/Gathering-Progression-Spec.md
phase A, F13 "Enchanted in bags": "SackDefs.homeOf gets an explicit Skyy_Ench_<Key> -> bag TABLE from tools/skyyench.py (a prefix cannot
tell Iron from Oak from Wheat)"; Skyy 2026-10-05 "i want to use sky blocks enchanted iron and enchanted cobble. (basically compressed
materials.)", 2026-10-11 "it costs a enchanted iron ingot to upgrade copper to iron").
  - NEW SackDefs.enchCat(id): the Void category of each of the 19 SkyyCollections 0.2.11 Enchanted ids (tools/skyyench.py TABLE, built
    in - one source with SkyyCollections and SkyyBazaar): Cobblestone, Rubble and the five Enchanted ingots -> Mining (the metals follow
    their COLLECTION / skill, not the ingot's Smithing category: DECISION, the spec's "each Enchanted item belongs to the same bag as its
    base" read as the base COLLECTION - a Mining bag holds Enchanted Iron, Gathering-Shards-Spec 3), the five logs -> Foraging, the seven
    crops -> Farming. An unknown Skyy_Ench_ id (a later table, an old jar) -> null = never stored, like every other Skyy_ item.
  - SackDefs.homeOf asks enchCat FIRST for a Skyy_Ench_ id (before the Skyy_ = cooked-food rule); catOf, sacks:fn:catOf, the sweep,
    Deposit all, withdraw, the bench / craft mirror and the Bazaar bridges all follow homeOf, so Enchanted items are auto-picked into
    the Void, withdrawn, used by /craft and benches and sold from the Void like any gathered item. Nothing else changes (no saved data,
    no new setting: a stored Enchanted stack is an ordinary pool line).
Rollback to 0.8.0: Enchanted items already in the Void stay in the pool file (0.8.0 lists a pool line it cannot place only through
homeOf - they are not shown or withdrawable until 0.8.1 is back; NOTHING is deleted). Roll SkyyCollections back with it (or the items
stay plain inventory items).
  - ench01fix2 (critic: the 19 Compressing recipes are Workbench recipes, so their inputs - 7 crops no vanilla Workbench recipe uses -
    joined the Workbench's "wanted" set and big crop piles won the 36 mirror slots over real low-count ingredients): NEW
    BagMirror.addRecipe skips a recipe whose primary output is a Skyy_Ench_ id when wantedFor builds a bench's wanted set. Enchanted
    inputs fall back to the count-ordered spare slots (pass 2), so vanilla Workbench crafting from the Void is as in 0.8.0; /craft
    (its own per-recipe wanted set) still finds every Enchanted input in the Void.
Classes changed: SackDefs (+ enchCat, homeOf), BagMirror (+ addRecipe, wantedFor). Everything else = 0.8.0 (version constants).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyySacks")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyench as EN
assert set(EN.CATS) <= {"Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"}
src = os.path.join(HERE, "build_skyysacks_0.8.0.py")
dst = os.path.join(HERE, "build_skyysacks_0.8.1.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.8.0"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
assert 'VERSION = "0.8.0"' in s and "enchCat" not in s, "not the live generated 0.8.0"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


GONE_OK = set()


def gone(*lines):
    for ln in lines:
        GONE_OK.add(ln)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''sacks:fn:catOf. 0.7.18's private writer, idle-hop gating and inventory-change sweeps are kept. Details: the patch docstring.
"""
''', '''sacks:fn:catOf. 0.7.18's private writer, idle-hop gating and inventory-change sweeps are kept. Details: the patch docstring.
0.8.1 (derived from 0.8.0 by tools/sacks_0_8_1_patch.py - edit the patch, not this file; research/Gathering-Shards-Spec.md phase 1): THE
ENCHANTED MATERIALS GO IN THE VOID - SackDefs.enchCat (tools/skyyench.py: the 19 SkyyCollections 0.2.11 Skyy_Ench_* ids -> Mining /
Foraging / Farming) is asked first by homeOf, so auto-pickup, Deposit all, withdraw, /craft + benches and the Bazaar bridges handle them
like any gathered item. No saved data or setting changes. Details: the patch docstring.
"""
''')
rep('''import skyyui as SUI     # 0.7.11: the shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md) for the new stack refill row
''', '''import skyyui as SUI     # 0.7.11: the shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md) for the new stack refill row
import skyyench as EN    # 0.8.1: the Enchanted materials table (one source with SkyyCollections 0.2.11 + SkyyBazaar 0.1.10)
''')
rep('VERSION = "0.8.0"\n', 'VERSION = "0.8.1"\n')
gone('VERSION = "0.8.0"')

# ---------------------------------------------------------------------------------------------------------------- SackDefs.enchCat + homeOf
rep('''defs.addMethod(CtNewMethod.make("""
public static String homeOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
''', '''# 0.8.1 (Gathering-Shards-Spec phase 1, spec F13): the Enchanted materials' Void category - tools/skyyench.py's table, built in
defs.addMethod(CtNewMethod.make(EN.sacks_home_java(), defs))
defs.addMethod(CtNewMethod.make("""
public static String homeOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  // 0.8.1: the 19 Enchanted materials (SkyyCollections 0.2.11) -> their collection's category; an unknown Skyy_Ench_ id -> null
  if (itemId.startsWith("Skyy_Ench_")) return enchCat(itemId);
''')

# ---------------------------------------------------------------------------------------------------------------- BagMirror.addRecipe (ench01fix2)
rep('''mir.addMethod(CtNewMethod.make(f"""
public static java.util.Set wantedFor(Object w) {{
''', '''# 0.8.1 (ench01fix2): one recipe's inputs into a bench's wanted set - an Enchanted compress recipe (primary output Skyy_Ench_*) is
# skipped, so its inputs (crops no vanilla Workbench recipe uses) never outrank real Workbench ingredients in the 36 mirror slots
mir.addMethod(CtNewMethod.make(f"""
public static boolean addRecipe(java.util.Set s, Object o) {{
  if (!(o instanceof {CRR})) return false;
  {MQ} po = (({CRR}) o).getPrimaryOutput();
  if (po != null && po.getItemId() != null && po.getItemId().startsWith("Skyy_Ench_")) return false;
  addInputs(s, (({CRR}) o).getInput());
  return true;
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static java.util.Set wantedFor(Object w) {{
''')
rep('''      if (o instanceof {CRR}) addInputs(s, (({CRR}) o).getInput());
''', '''      addRecipe(s, o);   // 0.8.1 (ench01fix2): Enchanted compress recipes do not widen the wanted set
''')
gone("      if (o instanceof {CRR}) addInputs(s, (({CRR}) o).getInput());")

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("CtNewMethod.make(EN.sacks_home_java(), defs)") < s.index("public static String homeOf(String itemId)") and "public static String enchCat(" in EN.sacks_home_java()
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_bad = [ln for ln in _gone if ln not in GONE_OK]
assert not _bad, "0.8.0 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.8.0 had %d)" % (s.count(LF), OLD.count(LF)))
