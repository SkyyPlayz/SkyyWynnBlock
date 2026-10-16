"""Derive SkyySacks/build_skyysacks_0.8.9.py from the SET pin 0.8.8 (the GENERATED build_skyysacks_0.8.8.py; edit THIS file, then
regenerate: python tools/sacks_0_8_9_patch.py; never re-run sacks_0_8_8_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.8 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_9_patch.py   then   python SkyySacks/build_skyysacks_0.8.9.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]
KIT: built against the COMMITTED tools/skyyui.py (kit 1.5) while the working tree holds another builder's uncommitted kit 1.6 edits: a
scratch runner puts `git show HEAD:tools/skyyui.py` into sys.modules["skyyui"] before it runs the build script (the build imports
`skyyui` by name); the harness does the same. Once the working-tree kit is committed, a plain build uses it.

0.8.9 = VOID COSTS + FABRIC TO COMBAT + STORAGE REBALANCE (round sacks089, 2026-10-15).
A. SMITHING COSTS (Skyy, on the SkyyVoid Smithing 'Upgrade to Unique (x1.5)' box needing Light Hide 200, Linen Scraps 100, Wool Scraps 100:
   "make this cost leather not hide, scrap fabric is good, but make it cost copper ingots, not whatever that thing is"; then "actually
   fabric is combat not smithing. move it to combat bag, and replace the feathers with the linen scraps"). Smithing takes NO fabric now:
   every hide -> the leather of the same weight (the Tannery product), fabric -> metal bars of the matching tier (Linen -> Copper,
   Shadoweave -> Iron, Cindercloth -> Thorium; same amounts):
     Unique    Light Leather 200, Copper Ingot 100                       (two lines, like Combat Unique - no filler material)
     Rare      Light Leather 750, Medium Leather 500, Copper Ingot 250, Iron Ingot 100
     Legendary Light Leather 2000, Medium Leather 1000, Heavy Leather 250, Iron Ingot 250, Thorium Ingot 100
B. FABRIC -> COMBAT. Ingredient_Fabric_Scrap_* (mob drops) leave the Smithing category for Combat (SackDefs.homeOf; cloth bolts, leather,
   hides, bars, straps, studs and charcoal stay Smithing). The pool is keyed by item id - nothing is moved or rewritten: a player's stored
   fabric simply shows (and counts) in the Combat tab from the first sweep on, exactly as hides / fabric moved Combat -> Smithing in 0.7.5.
   Combat full: storage is only ever checked at INTAKE - an over-full Combat keeps every item (take out works), new Combat pickups go to the
   inventory (then the ground at the feet, as for any full category) until there is room again; Smithing gets the room back.
   Combat costs: White Feathers -> Linen Scraps at the same amounts; Rare also takes Shadoweave 100 (the old Smithing Rare had it);
   Legendary already has the 6 lines the upgrade box shows, so it takes no Cindercloth:
     Unique    Bone Fragment 250, Linen Scraps 100
     Rare      Bone Fragment 1000, Linen Scraps 500, Venom Sac 100, Sturdy Chitin 100, Shadoweave Scraps 100
     Legendary Bone Fragment 2500, Linen Scraps 1000, Venom Sac 250, Sturdy Chitin 250, Void Essence 100, Voidheart 10
C. STORAGE REBALANCE (Skyy, on Foraging Lv 14 Unique 'Stored 1,079 / 2,100', '3,425 / 3,920 collected to Lv 15', Rare needing 3,750 items
   and Lv 25: "make the level ups give a little more storage, and scale down how much each level cost goes up. the cost to upgrade rarity
   iss about 2x what i can hold. and what i can hold doesn't scale fast enough to really keep up with the amount i need to collect to level
   it."). (a) pd.perLevel 100 -> 150 space per level (x the rarity; multipliers 1 / 1.5 / 2 / 3 / 5 and gates Lv 10 / 25 / 50 unchanged -
   Omni stays x5). (b) NEW row pd.curve (default 1.75; 2 = the old curve): items to REACH level L = pd.step.<Cat> x (L-1)^pd.curve (was
   ^2), so each level costs less more than the one before (Foraging step 20: Lv 5 320 -> 227, Lv 10 1,620 -> 936, Lv 15 3,920 -> 2,027,
   Lv 25 11,520 -> 5,205, Lv 50 48,020 -> 18,150). levelOf / totalFor stay exact inverses (checked +-1 against totalFor). (c) at each
   gate the bag ALONE holds >= 1.25 x that upgrade's cost (asserted at build time for every category; worst Mining Rare 1.32x, was 0.88x).
   Levels only go up: the saved best level stays, a player whose total now reads a higher level gets it (and its space) at the next sweep.
D. NAMES IN THE UPGRADE BOX. Every cost cell shows the item's real name (SackDefs.lineName = the tier-log label, else the 0.8.8 dname
   resolver) over its count - the two-line cell the tier logs already use; no translation -> the plain count cell as before. The refusal
   lines ("Not enough Light Leather (50 / 200)") use the same name. Icons are the item ids' own (vanilla icons, checked in Assets.zip).
E. ONE-TIME CONFIG UPDATE (PROJECT-RULES 4; SackMig089, setup() before SackCfg.reload): in an existing Skyy_SkyySacks/config.properties
   the six cost lines pd.cost.Smithing.* / pd.cost.Combat.* and pd.perLevel are rewritten ONLY while they still hold the 0.8.8 default
   (text compared without spaces, numbers by value); a hand-edited, doubled or continued line is KEPT and named in an INFO line; a missing
   line = the new built-in default. The commented template lines (#pd.cost...=<0.8.8 default>, #pd.perLevel=100) get the new default too,
   so un-commenting one never brings an old cost back. Only the value part of a line changes - every other byte and each line's own ending
   stay; one marker comment line (skyysacks-0.8.9-void, the run-once marker; a new default file carries it) is appended. Before the
   write: a Properties check (only those keys change, to exactly the new values), CfgHist.snapshot + a read-back of the copy; after it one
   config-changes.log line per changed value (Server Setup -> SkyyVoid and Crafting -> Changes -> Undo). Any failure: file untouched,
   WARN, next start tries again.
F. No saved-data change, no new command / system / bridge key; one new Server Setup row (pd.curve). ROLLBACK to 0.8.8: safe - fabric shows
   in Smithing again (same pool), the 0.8.8 curve / 100 per level / old costs come back unless the file holds the 0.8.9 values (Changes ->
   Undo or History puts them back; the marker stops a second run); saved best levels reached under 0.8.9 stay (levels never go down).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.8.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.9.py"))
assert P.has('VERSION = "0.8.8"\n') and P.has("benchScore") and not P.has("SackMig089"), "not the live generated SkyySacks 0.8.8"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.9 = VOID COSTS"):].rstrip() + "\n"

OLD_COST = {
    ("Combat", 1): '''    ("Combat", 1): [("Ingredient_Bone_Fragment", 250), ("Ingredient_Feathers_Light", 100)],
''',
    ("Combat", 2): '''    ("Combat", 2): [("Ingredient_Bone_Fragment", 1000), ("Ingredient_Feathers_Light", 500), ("Ingredient_Sac_Venom", 100),
                    ("Ingredient_Chitin_Sturdy", 100)],
''',
    ("Combat", 3): '''    ("Combat", 3): [("Ingredient_Bone_Fragment", 2500), ("Ingredient_Feathers_Light", 1000), ("Ingredient_Sac_Venom", 250),
                    ("Ingredient_Chitin_Sturdy", 250), ("Ingredient_Void_Essence", 100), ("Ingredient_Voidheart", 10)],
''',
    ("Smithing", 1): '''    ("Smithing", 1): [("Ingredient_Hide_Light", 200), ("Ingredient_Fabric_Scrap_Linen", 100), ("Ingredient_Fabric_Scrap_Wool", 100)],
''',
    ("Smithing", 2): '''    ("Smithing", 2): [("Ingredient_Hide_Light", 750), ("Ingredient_Hide_Medium", 500), ("Ingredient_Fabric_Scrap_Linen", 250),
                      ("Ingredient_Fabric_Scrap_Shadoweave", 100)],
''',
    ("Smithing", 3): '''    ("Smithing", 3): [("Ingredient_Hide_Light", 2000), ("Ingredient_Hide_Medium", 1000), ("Ingredient_Hide_Heavy", 250),
                      ("Ingredient_Fabric_Scrap_Shadoweave", 250), ("Ingredient_Fabric_Scrap_Cindercloth", 100)],
''',
}
NEW_COST = {
    ("Combat", 1): [("Ingredient_Bone_Fragment", 250), ("Ingredient_Fabric_Scrap_Linen", 100)],
    ("Combat", 2): [("Ingredient_Bone_Fragment", 1000), ("Ingredient_Fabric_Scrap_Linen", 500), ("Ingredient_Sac_Venom", 100),
                    ("Ingredient_Chitin_Sturdy", 100), ("Ingredient_Fabric_Scrap_Shadoweave", 100)],
    ("Combat", 3): [("Ingredient_Bone_Fragment", 2500), ("Ingredient_Fabric_Scrap_Linen", 1000), ("Ingredient_Sac_Venom", 250),
                    ("Ingredient_Chitin_Sturdy", 250), ("Ingredient_Void_Essence", 100), ("Ingredient_Voidheart", 10)],
    ("Smithing", 1): [("Ingredient_Leather_Light", 200), ("Ingredient_Bar_Copper", 100)],
    ("Smithing", 2): [("Ingredient_Leather_Light", 750), ("Ingredient_Leather_Medium", 500), ("Ingredient_Bar_Copper", 250),
                      ("Ingredient_Bar_Iron", 100)],
    ("Smithing", 3): [("Ingredient_Leather_Light", 2000), ("Ingredient_Leather_Medium", 1000), ("Ingredient_Leather_Heavy", 250),
                      ("Ingredient_Bar_Iron", 250), ("Ingredient_Bar_Thorium", 100)],
}
_RAR = ("Normal", "Unique", "Rare", "Legendary")


def _text(v):
    return ",".join("%s:%d" % (i, q) for i, q in v)


def _old_text(src):
    """the 0.8.8 default text of a cost line, from its literal source"""
    import ast
    body = src.strip().split(":", 1)[1].strip().rstrip(",")
    return _text(ast.literal_eval(body))


assert not any("Fabric_Scrap" in i for i, _q in sum((NEW_COST[("Smithing", r)] for r in (1, 2, 3)), [])), "Skyy: no fabric in Smithing"
assert not any("Feathers" in i for i, _q in sum((NEW_COST[("Combat", r)] for r in (1, 2, 3)), [])), "Skyy: linen replaces the feathers"
MIG = [("pd.perLevel", "100", "150", "n")]
for (c, r) in sorted(NEW_COST, key=lambda x: (("Combat", "Smithing").index(x[0]), x[1])):
    MIG.append(("pd.cost.%s.%s" % (c, _RAR[r]), _old_text(OLD_COST[(c, r)]), _text(NEW_COST[(c, r)]), "t"))
assert len(MIG) == 7 and MIG[1] == ("pd.cost.Combat.Unique", "Ingredient_Bone_Fragment:250,Ingredient_Feathers_Light:100",
                                     "Ingredient_Bone_Fragment:250,Ingredient_Fabric_Scrap_Linen:100", "t")
MK_ID = "skyysacks-0.8.9-void"

# ---------- header + version
P.rep('''D. No saved-data change, no new command / system / bridge key. ROLLBACK to 0.8.7: safe (the Furnace may show "needs no fuel" again;
   costs count only the named log again; /craft lists go back to material order + id names).
"""
''', '''D. No saved-data change, no new command / system / bridge key. ROLLBACK to 0.8.7: safe (the Furnace may show "needs no fuel" again;
   costs count only the named log again; /craft lists go back to material order + id names).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.8"\n', 'VERSION = "0.8.9"\n')

# ---------- B. fabric scraps -> Combat
P.rep('''SMITH_PREFIX = ("Ingredient_Bar_", "Ingredient_Leather_", "Ingredient_Hide_", "Ingredient_Bolt_", "Ingredient_Fabric_Scrap_")
''', '''SMITH_PREFIX = ("Ingredient_Bar_", "Ingredient_Leather_", "Ingredient_Hide_", "Ingredient_Bolt_")
# 0.8.9 (Skyy "actually fabric is combat not smithing. move it to combat bag"): the fabric scraps (mob drops) are Combat again - homeOf's
# Combat rule; cloth bolts stay Smithing. The pool is keyed by item id: stored fabric simply shows in the Combat tab (nothing moves).
COMBAT_PREFIX_089 = "Ingredient_Fabric_Scrap_"
''')
P.rep('''            "Combat": "bones, feathers, essences, venom sacs, chitin, voidhearts and boom powder",
            "Smithing": "bars and ingots, leather, hides, cloth bolts, fabric scraps, leather straps, iron studs and charcoal"}
assert set(PD_HOLDS) == set(PD_CATS)''', '''            "Combat": "bones, feathers, fabric scraps, essences, venom sacs, chitin, voidhearts and boom powder",
            "Smithing": "bars and ingots, leather, hides, cloth bolts, leather straps, iron studs and charcoal"}   # 0.8.9: fabric -> Combat
assert set(PD_HOLDS) == set(PD_CATS)''')
P.rep('''  // 0.7.5 Smithing bag: bars / ingots, leather, hides, cloth bolts, fabric scraps, strap, stud - checked BEFORE Combat, which held hides and
  // fabric scraps until 0.7.4 (the pool is keyed by item id, so those stacks simply show in the Smithing tab now)
  if (@SMITH@) return "Smithing";
  if (itemId.startsWith("Ingredient_Bone") || itemId.startsWith("Ingredient_Chitin")''', '''  // 0.7.5 Smithing bag: bars / ingots, leather, hides, cloth bolts, strap, stud - checked BEFORE Combat, which held hides and
  // fabric scraps until 0.7.4 (the pool is keyed by item id, so those stacks simply show in the Smithing tab now)
  // 0.8.9 (Skyy "fabric is combat not smithing"): fabric scraps are Combat again (stored stacks show in the Combat tab; nothing moves)
  if (@SMITH@) return "Smithing";
  if (itemId.startsWith("@FABRIC@")) return "Combat";
  if (itemId.startsWith("Ingredient_Bone") || itemId.startsWith("Ingredient_Chitin")''')
P.rep('''}""".replace("@SMITH@", SMITH_JAVA).replace("@SAP@", TREE_SAP), defs))''',
      '''}""".replace("@SMITH@", SMITH_JAVA).replace("@SAP@", TREE_SAP).replace("@FABRIC@", COMBAT_PREFIX_089), defs))''')

# ---------- A/B. the costs; C. space per level + the curve
for k in sorted(OLD_COST):
    c, r = k
    new = '    ("%s", %d): [%s],\n' % (c, r, ", ".join('("%s", %d)' % (i, q) for i, q in NEW_COST[k]))
    if len(new) > 141:
        cut = new.rindex("), (", 0, 140) + 2
        new = new[:cut] + "\n" + " " * (len('    ("%s", %d): [' % (c, r))) + new[cut + 1:]
    P.rep(OLD_COST[k], new)
P.rep('''PD_PER_LEVEL, PD_MAX_LEVEL = 100, 250
''', '''PD_PER_LEVEL, PD_MAX_LEVEL = 150, 250   # 0.8.9 (Skyy "make the level ups give a little more storage"): 100 -> 150
# 0.8.9 (Skyy "scale down how much each level cost goes up"): items to reach level L = pd.step x (L-1)^PD_CURVE (0.8.0-0.8.8: ^2)
PD_CURVE = 1.75
PD_CURVE_LO, PD_CURVE_HI = 1.0, 3.0
''')
P.rep('''assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
''', '''assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
# 0.8.9 (Skyy "the cost to upgrade rarity iss about 2x what i can hold"): at every gate the bag ALONE holds >= 1.25 x that upgrade's cost
# (space at the gate level with the rarity before the step: level x pd.perLevel x the multiplier)
def _gate_room_check():
    rows = []
    for c in PD_CATS:
        cells = []
        for r in (1, 2, 3):
            g = PD_GATE[r - 1]
            room = g * PD_PER_LEVEL * PD_MULT[r - 1]
            need = sum(q for _i, q in PD_COST[(c, r)])
            assert room >= 1.25 * need, "0.8.9: %s %s at Lv %d holds %d < 1.25 x its cost %d" % (c, PD_RAR[r], g, room, need)
            cells.append("Lv%d %s %d/%d %.2fx" % (g, PD_RAR[r - 1], room, need, room / need))
        rows.append(c + " " + ", ".join(cells))
    print("gate room (space at the gate / upgrade cost, >= 1.25x): " + " | ".join(rows))
_gate_room_check()
# 0.8.9: the one-time config update (SackMig089): (key, the 0.8.8 default, the 0.8.9 default, n = number / t = cost text)
MIG089 = ''' + repr(MIG) + '''
MIG089_MK = ''' + repr(MK_ID) + '''
_pdt = dict(("pd.cost.%s.%s" % (c, PD_RAR[r]), ",".join("%s:%d" % x for x in v)) for (c, r), v in PD_COST.items())
assert all(_pdt[k_] == n_ for k_, o_, n_, t_ in MIG089 if t_ == "t") and MIG089[0] == ("pd.perLevel", "100", str(PD_PER_LEVEL), "n")
''')

# ---------- C. the template lines (a new file: the new wording, the curve row, the 0.8.9 marker - nothing to update)
P.rep('''    "# The Void (SkyyVoid): space of a category = storage level x pd.perLevel x the rarity multiplier; level = 1 + square root of",
    "# (items collected in that category / pd.step.<Category>). Remove the # in front of a line to change it. Lowering never deletes items.",
] + (["#pd.perLevel=%d" % PD_PER_LEVEL, "#pd.maxLevel=%d" % PD_MAX_LEVEL, "#pd.omniAuto=true"]''',
      '''    "# The Void (SkyyVoid): space of a category = storage level x pd.perLevel x the rarity multiplier; level L needs pd.step.<Category>",
    "# x (L-1)^pd.curve items collected in that category. Remove the # in front of a line to change it. Lowering never deletes items.",
    "# SkyySacks 0.8.9 defaults (marker %s): 150 space per level, curve 1.75, Smithing costs leather + bars, Combat costs fabric." % MIG089_MK,
] + (["#pd.perLevel=%d" % PD_PER_LEVEL, "#pd.maxLevel=%d" % PD_MAX_LEVEL, "#pd.curve=%g" % PD_CURVE, "#pd.omniAuto=true"]''')

# ---------- C. SackCfg: PD_CURVE (field, loader, signature)
P.rep('''_PD_CFG_FIELDS = (["public static volatile int PD_PER_LEVEL = %d;" % PD_PER_LEVEL, "public static volatile int PD_MAX_LEVEL = %d;" % PD_MAX_LEVEL]
''', '''_PD_CFG_FIELDS = (["public static volatile int PD_PER_LEVEL = %d;" % PD_PER_LEVEL, "public static volatile int PD_MAX_LEVEL = %d;" % PD_MAX_LEVEL]
                  + ["public static volatile double PD_CURVE = %r;" % PD_CURVE]   # 0.8.9
''')
P.rep('''_PD_LOAD.append('  PD_OMNI_AUTO = boolKey(p, "pd.omniAuto", true);')
''', '''_PD_LOAD.append('  PD_OMNI_AUTO = boolKey(p, "pd.omniAuto", true);')
_PD_LOAD.append('  PD_CURVE = decKey(p, "pd.curve", %r, %r, %r);' % (PD_CURVE, PD_CURVE_LO, PD_CURVE_HI))   # 0.8.9
''')
P.rep('''_PD_SIG = ' + "," + '.join(["PD_PER_LEVEL", "PD_MAX_LEVEL"] + ''', '''_PD_SIG = ' + "," + '.join(["PD_PER_LEVEL", "PD_MAX_LEVEL", "PD_CURVE"] + ''')
P.rep('''# the highest storage level in use (pd.maxLevel, at least 1)
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int maxLevel() {''', '''# 0.8.9: the level curve in use (pd.curve, %g .. %g)
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static double curve() {
  double e = PD_CURVE;
  if (e != e || e < %r) return %r;
  return e > %r ? %r : e;
}\'\'\'), scfg))
# the highest storage level in use (pd.maxLevel, at least 1)
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int maxLevel() {''' % (1.0, 3.0, 1.0, 1.0, 3.0, 3.0))
P.rep('''"[SkyySacks] config: Void - " + PD_PER_LEVEL + " items per storage level (max level " + PD_MAX_LEVEL + "), multipliers''',
      '''"[SkyySacks] config: Void - " + PD_PER_LEVEL + " items per storage level (max level " + PD_MAX_LEVEL + ", level curve " + PD_CURVE + "), multipliers''')

# ---------- C. the level <-> items curve (totalFor first: levelOf checks itself against it)
P.rep('''vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int levelOf(long total, int ci) {
  int step = @PKG@.SackCfg.step(ci);
  if (step < 1) step = 1;
  int max = @PKG@.SackCfg.maxLevel();
  if (total <= 0L) return 1;
  double q = Math.floor(Math.sqrt((double) total / (double) step) + 1.0E-9);
  long lv = 1L + (long) q;
  if (lv > (long) max) lv = (long) max;
  return (int) lv;
}\'\'\'), vst))
# the items a level needs (the inverse): step x (level - 1)^2
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long totalFor(int level, int ci) {
  long n = (long) (level < 1 ? 0 : level - 1);
  long step = (long) @PKG@.SackCfg.step(ci);
  return step * n * n;
}\'\'\'), vst))
''', '''# 0.8.9 (Skyy "scale down how much each level cost goes up"): the items a level needs = step x (level - 1)^pd.curve, rounded up
# (pd.curve 2 = the 0.8.0-0.8.8 curve exactly)
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long totalFor(int level, int ci) {
  long n = (long) (level < 1 ? 0 : level - 1);
  if (n <= 0L) return 0L;
  long step = (long) @PKG@.SackCfg.step(ci);
  if (step < 1L) step = 1L;
  double v = (double) step * Math.pow((double) n, @PKG@.SackCfg.curve());
  if (v > 1.0E17) return 100000000000000000L;
  return (long) Math.ceil(v - 1.0E-6);
}\'\'\'), vst))
# the level of a total = the highest L with totalFor(L) <= total (the estimate checked against totalFor, so both always agree)
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int levelOf(long total, int ci) {
  int step = @PKG@.SackCfg.step(ci);
  if (step < 1) step = 1;
  int max = @PKG@.SackCfg.maxLevel();
  if (total <= 0L) return 1;
  double q = Math.floor(Math.pow((double) total / (double) step, 1.0 / @PKG@.SackCfg.curve()) + 1.0E-9);
  long lv = 1L + (long) q;
  if (lv > (long) max) lv = (long) max;
  if (lv < 1L) lv = 1L;
  while (lv > 1L && totalFor((int) lv, ci) > total) lv--;
  while (lv < (long) max && totalFor((int) lv + 1, ci) <= total) lv++;
  return (int) lv;
}\'\'\'), vst))
''')

# ---------- C. the rows: the step help line, the new curve row
P.rep('''            "Level = 1 + square root of (%s items collected / this). Higher = slower levels." % c, "PD_STEP_" + c.upper())''',
      '''            "Level L needs this x (L-1)^pd.curve %s items collected. Higher = slower levels." % c, "PD_STEP_" + c.upper())''')
P.rep('''    _pdrow("pd.omniAuto", "Omni comes by itself", "void", "bool", "true", "", "", "", "live",
           "On: all six categories at Legendary = Omni. Off: only /pdadmin omni gives it.", "PD_OMNI_AUTO"),
''', '''    _pdrow("pd.omniAuto", "Omni comes by itself", "void", "bool", "true", "", "", "", "live",
           "On: all six categories at Legendary = Omni. Off: only /pdadmin omni gives it.", "PD_OMNI_AUTO"),
    # 0.8.9 (Skyy "scale down how much each level cost goes up")
    _pdrow("pd.curve", "Level curve", "void", "dec", "%g" % PD_CURVE, "%g" % PD_CURVE_LO, "%g" % PD_CURVE_HI, "", "live,adv",
           "Level L needs pd.step x (L-1)^this items. 2 = the old steep curve, lower = cheaper later levels.", "PD_CURVE"),
''')
P.rep('''print("Void: %s | level = 1 + sqrt(collected / step %s) to %d | space = level x %d x %s | gates %s | Pocket %s" % (
    "/".join(PD_CATS), "/".join(str(PD_STEP[c]) for c in PD_CATS), PD_MAX_LEVEL,''', '''print("Void: %s | level L needs step %s x (L-1)^%g to %d | space = level x %d x %s | gates %s | Pocket %s" % (
    "/".join(PD_CATS), "/".join(str(PD_STEP[c]) for c in PD_CATS), PD_CURVE, PD_MAX_LEVEL,''')

# ---------- D. real names in the upgrade box + the refusal lines
P.rep('''  if (n == null) return rt.replace('_', ' ');
  if (DNAMES.size() < 8192) DNAMES.put("res:" + rt, n);
  return n;
}""", defs))
''', '''  if (n == null) return rt.replace('_', ' ');
  if (DNAMES.size() < 8192) DNAMES.put("res:" + rt, n);
  return n;
}""", defs))
# 0.8.9 (Skyy could not tell what a cost icon was: "not whatever that thing is"): the name a Void cost line shows - the tier-log label
# ("Oak-tier logs"), else the item's real name (dname), else null (the plain count cell / the id in a message)
defs.addMethod(CtNewMethod.make("""
public static String lineName(String id) {
  String n = unitName(id);
  return n != null ? n : dname(id);
}""", defs))
''')
P.rep('''    String un = @PKG@.SackDefs.unitName(id);
    if (have < need) return "-Not enough "''', '''    String un = @PKG@.SackDefs.lineName(id);   // 0.8.9: the real name
    if (have < need) return "-Not enough "''')
P.rep('''      String un = @PKG@.SackDefs.unitName(id);
      if (rest > 0L) bad = "-Not enough "''', '''      String un = @PKG@.SackDefs.lineName(id);   // 0.8.9: the real name
      if (rest > 0L) bad = "-Not enough "''')
P.rep('''      String un = @PKG@.SackDefs.unitName(cid2);
      b.appendInline("#SkyyVCostR" + cr, @@costic@@);''', '''      String un = @PKG@.SackDefs.lineName(cid2);   // 0.8.9: every line with a real name shows it over the count
      b.appendInline("#SkyyVCostR" + cr, @@costic@@);''')
P.rep('''    # 0.8.8 TIER LOGS: a tier log line = "Oak-tier logs" (12) over the count (13), the same 130 x 32 cell
''', '''    # 0.8.8 TIER LOGS: a tier log line = "Oak-tier logs" (12) over the count (13), the same 130 x 32 cell
    # 0.8.9: so is every line whose item has a real name ("Light Leather" over "50 / 200")
''')

# ---------- E. SackMig089 (after the kit classes exist) + its call in setup() + the class list
P.rep('''print("config kit: %d rows, files %s" % (kit.info["rows"], ", ".join(kit.info["files"])))
''', '''print("config kit: %d rows, files %s" % (kit.info["rows"], ", ".join(kit.info["files"])))
# ================= 0.8.9 SackMig089: the ONE-TIME update of an existing config.properties (PROJECT-RULES 4; SkyyTrees TreeMig317's pattern)
# setup() only, BEFORE SackCfg.reload and CfgPub.start. The MIG089 lines move from the 0.8.8 default to the 0.8.9 one ONLY while they still
# hold the old default (cost text without spaces, numbers by value); a value an admin changed, a doubled or continued line is kept and
# named in an INFO line; a missing line = the new built-in value. The commented template lines holding the old default get the new one
# too (no value changes). Only the VALUE part of a line changes - every other byte and each line's own ending stay; the marker comment
# line is appended (a missing final newline added first, with the ending of the file's last ended line). Properties check, History copy verified before
# the write, one change-log line per moved value (Server Setup -> Changes -> Undo). The marker = never again.
for _k, _o, _n, _t in MIG089:
    assert ("#%s=%s" % (_k, _n)) in SACK_CFG_LINES, _k                  # the new default file holds the new value
assert sum(1 for l in SACK_CFG_LINES if MIG089_MK in l) == 1 and [l for l in SACK_CFG_LINES if MIG089_MK in l][0].startswith("# ")
MIG089_LINE = "# ---------- SkyySacks 0.8.9 (marker %s, runs once): Smithing costs leather + metal bars, Combat costs fabric (not feathers), 150 space per level; only untouched old default lines were changed ----------" % MIG089_MK
smig = pool.makeClass(PKG + ".SackMig089")
for _d in ("public static final String MK = %s;" % jlit(MIG089_MK),
           'public static final String WHO = "SkyySacks 0.8.9";',
           "public static final String MARK_LINE = %s;" % jlit(MIG089_LINE),
           "public static final String[] KEY = %s;" % _jarr([m[0] for m in MIG089]),
           "public static final String[] OLDV = %s;" % _jarr([m[1] for m in MIG089]),
           "public static final String[] NEWV = %s;" % _jarr([m[2] for m in MIG089]),
           "public static final String[] KIND = %s;" % _jarr([m[3] for m in MIG089])):
    smig.addField(CtField.make(_d, smig))
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean marked(java.util.ArrayList l) {
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { if (s.indexOf(MK) >= 0) return true; k++; continue; }
    k = @PKG@.CfgFile.end(l, k) + 1;
  }
  return false;
}\'\'\'), smig))
# a cost text without any spaces / a number by value ("100", "100.0")
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String squeeze(String a) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length(); i++) { char c = a.charAt(i); if (c != ' ' && c != '\\t') sb.append(c); }
  return sb.toString();
}\'\'\'), smig))
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean same(int j, String a, String b) {
  if (a == null || b == null) return false;
  if (squeeze(a).equals(squeeze(b))) return true;
  if (!"n".equals(KIND[j])) return false;
  try { return Double.parseDouble(a.trim()) == Double.parseDouble(b.trim()); } catch (Throwable t) { return false; }
}\'\'\'), smig))
# a commented template line "#<key>=<value>" (exactly as the default file writes it) -> the key's index, else -1
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int docKey(String s) {
  String x = s.trim();
  if (!x.startsWith("#")) return -1;
  for (int j = 0; j < KEY.length; j++) if (x.startsWith("#" + KEY[j] + "=")) return j;
  return -1;
}\'\'\'), smig))
# pure text step (ISO-8859-1 chars in and out). null = the marker is already in a comment line or the text cannot be read as Properties.
# Else { new text, String[] { key, old, new }* (the change-log rows), String[] notes, String[] moved keys, Integer doc lines updated }.
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static Object[] update(String text) {
  try {
    java.util.ArrayList l = @PKG@.CfgFile.split(text);
    if (marked(l)) return null;
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.StringReader(text));
    int n = l.size();
    int[] st = new int[n + 1];
    int pos = 0;
    for (int i = 0; i < n; i++) { st[i] = pos; int e = text.indexOf('\\n', pos); pos = e < 0 ? text.length() : e + 1; }
    st[n] = text.length();
    int[] cnt = new int[KEY.length];
    int[] at = new int[KEY.length];
    String[] repl = new String[n];
    int docs = 0;
    int k = 0;
    while (k < n) {
      String s = (String) l.get(k);
      if (@PKG@.CfgFile.isComment(s)) {
        int j = docKey(s);
        if (j >= 0) {
          int eq = s.indexOf('=');
          String v = s.substring(eq + 1);
          if (same(j, v, OLDV[j])) { repl[k] = s.substring(0, eq + 1) + NEWV[j]; docs++; }
        }
        k++;
        continue;
      }
      int e = @PKG@.CfgFile.end(l, k);
      String key = @PKG@.CfgFile.unesc(s.substring(@PKG@.CfgFile.lead(s), @PKG@.CfgFile.keyEnd(s)));
      for (int j = 0; j < KEY.length; j++) if (KEY[j].equals(key)) { cnt[j]++; at[j] = e == k ? k : -1; }
      k = e + 1;
    }
    java.util.ArrayList rows = new java.util.ArrayList();
    java.util.ArrayList notes = new java.util.ArrayList();
    java.util.ArrayList moved = new java.util.ArrayList();
    for (int j = 0; j < KEY.length; j++) {
      String v = p.getProperty(KEY[j]);
      if (v == null) continue;   // no line: the new built-in value applies
      String vt = v.trim();
      if (same(j, vt, NEWV[j])) continue;
      if (cnt[j] != 1 || at[j] < 0) { notes.add(KEY[j] + "=" + @PKG@.CfgRows.oneLine(vt) + " kept - the line is doubled or continues on the next line; the 0.8.9 default is " + NEWV[j] + " (Server Setup -> SkyyVoid and Crafting)"); continue; }
      if (!same(j, vt, OLDV[j])) { notes.add(KEY[j] + "=" + @PKG@.CfgRows.oneLine(vt) + " kept - an admin changed it (the 0.8.8 default was " + OLDV[j] + ", the 0.8.9 default is " + NEWV[j] + ")"); continue; }
      String s = (String) l.get(at[j]);
      repl[at[j]] = s.substring(0, @PKG@.CfgFile.valStart(s)) + NEWV[j];
      rows.add(KEY[j]); rows.add(vt); rows.add(NEWV[j]);
      moved.add(KEY[j]);
    }
    StringBuilder sb = new StringBuilder(text.length() + 1024);
    for (int i = 0; i < n; i++) {
      String rawl = text.substring(st[i], st[i + 1]);
      if (repl[i] == null) { sb.append(rawl); continue; }
      sb.append(repl[i]).append(rawl.substring(((String) l.get(i)).length()));   // the line's own ending
    }
    int ln = text.lastIndexOf('\\n');   // the ending of the file's last ended line (a mixed file: the one next to the marker)
    String eol = (ln > 0 && text.charAt(ln - 1) == '\\r') ? "\\r\\n" : "\\n";
    if (text.length() > 0 && !text.endsWith("\\n")) sb.append(eol);
    sb.append(MARK_LINE).append(eol);
    return new Object[] { sb.toString(), (String[]) rows.toArray(new String[0]), (String[]) notes.toArray(new String[0]), (String[]) moved.toArray(new String[0]), Integer.valueOf(docs) };
  } catch (Throwable t) { return null; }
}\'\'\'), smig))
# the update may change only the moved keys, each to exactly its new value: both texts as Properties, nothing added or removed
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean sameAfter(byte[] old, byte[] nb, String[] moved) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (a.size() != b.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      int m = -1;
      for (int i = 0; i < moved.length; i++) if (moved[i].equals(k)) m = i;
      if (m >= 0) {
        int j = -1;
        for (int q = 0; q < KEY.length; q++) if (KEY[q].equals(k)) j = q;
        if (j < 0 || !NEWV[j].equals(b.getProperty(k))) return false;
        continue;
      }
      if (!a.getProperty(k).equals(b.getProperty(k))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}\'\'\'), smig))
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int fileIdx() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith("/config.properties")) return k;
  return -1;
}\'\'\'), smig))
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyySacks)
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void kit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.SackPool.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}\'\'\'), smig))
# CfgHist.snapshot swallows its own errors: config-history must really hold a copy with exactly these bytes (newest first)
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean saved(int f, byte[] old) {
  String[] have = @PKG@.CfgHist.list(f);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(f, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}\'\'\'), smig))
# "" = nothing done (no file - SackCfg.reload writes the 0.8.9 default with the marker -, marker already there, or a failure: WARN, file
# untouched, retried at the next start); else the INFO lines joined by \\n
smig.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized String run(java.nio.file.Path f) {
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] moved = (String[]) r[3];
    if (!sameAfter(old, data, moved)) {
      @PKG@.SackPool.warn("config.properties NOT updated for SkyySacks 0.8.9 (Void costs / space): the update would change more than those lines (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = fileIdx();
    if (fi < 0) return "";
    kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.8.9 Void costs / space update");
    if (!saved(fi, old)) {
      @PKG@.SackPool.warn("config.properties NOT updated for SkyySacks 0.8.9 (Void costs / space): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    StringBuilder ch = new StringBuilder();
    for (int i = 0; i + 2 < rows.length; i += 3) {
      @PKG@.CfgLog.enqueue(@PKG@.CfgLog.now() + "\\t" + WHO + "\\t-\\tupdate\\t" + rows[i] + "\\t" + rows[i + 1] + "\\t" + rows[i + 2] + "\\tok");
      ch.append(ch.length() == 0 ? "" : ", ").append(rows[i]).append(' ').append(rows[i + 1]).append(" -> ").append(rows[i + 2]);
    }
    if (rows.length > 0) @PKG@.CfgLog.flush();
    int docs = ((Integer) r[4]).intValue();
    String msg = "config.properties updated for SkyySacks 0.8.9 (Smithing costs leather + bars, Combat costs fabric, 150 space per level): " + (rows.length == 0 ? "no setting line held the old default" : ch.toString() + " (the old file is in config-history; Server Setup -> SkyyVoid and Crafting -> Changes can undo each)") + "; " + docs + " commented default line(s) refreshed [marker " + MK + " added, runs once]";
    try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] " + msg); } catch (Throwable t2) { }
    StringBuilder all = new StringBuilder(msg);
    String[] notes = (String[]) r[2];
    for (int i = 0; i < notes.length; i++) {
      try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config.properties: " + notes[i]); } catch (Throwable t3) { }
      all.append('\\n').append(notes[i]);
    }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.SackPool.warn("could not update config.properties for SkyySacks 0.8.9 (Void costs / space; the file is used as it is): " + t);
    return "";
  }
}\'\'\'), smig))
''')
P.rep('''  {PKG}.SackCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("config.properties");
  {PKG}.SackCfg.reload();
''', '''  {PKG}.SackCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("config.properties");
  {PKG}.SackMig089.run({PKG}.SackCfg.FILE);   // 0.8.9: untouched 0.8.8 cost / space defaults -> the new ones, once (History first; Undo)
  {PKG}.SackCfg.reload();
''')
P.rep('''          plt):   # 0.8.6: PickLate
''', '''          plt,    # 0.8.6: PickLate
          smig):  # 0.8.9: SackMig089
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
_i = P.s.index
assert _i("public static long totalFor(int level") < _i("public static int levelOf(long total") < _i("public static int level(java.util.UUID u")
assert _i("public static String rtName(String rt)") < _i("public static String lineName(String id)") < _i("public static String upgrade(@PLA@ p")
assert _i("public static double curve()") < _i("public static long totalFor(int level") and _i("smig = pool.makeClass") > _i("kit = CFG.emit(")
assert _i("SackMig089.run({PKG}.SackCfg.FILE)") < _i("{PKG}.SackCfg.reload();\n  // 0.7.7")
P.finish()
