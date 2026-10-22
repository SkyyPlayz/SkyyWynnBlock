"""Derive SkyySacks/build_skyysacks_0.8.26.py from the SET pin 0.8.24 (the GENERATED build_skyysacks_0.8.24.py; edit THIS file, then
regenerate: python tools/sacks_0_8_26_patch.py; never re-run sacks_0_8_24_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.24 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_26_patch.py   then   python SkyySacks/build_skyysacks_0.8.26.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.26.py [--dir <folder inside tools/dev/scratch/>] [--keep]
0.8.25 (the off-hand refill, tools/sacks_0_8_25_patch.py) is NOT in 0.8.26: Skyy parked it ("skip for now"); 0.8.26 is built from 0.8.24.

0.8.26 (2026-10-21) = BALANCE P6 PART A: THE FURNACE NEVER THE BOTTLENECK (research/Balance-P6-Gathering-Spec.md Part 4, Q6 [yes]; full round
  balp6a with SkyyWorldGen 0.7.8 + SkyyShards 0.4.4). Skyy 2026-10-20 "just go with the recommended on all of them" (Q6: "Furnace 4x faster
  (25 % of vanilla time, the charm still on top) and a 1,000-bar queue? [yes]"). Why (spec 4.1, DERIVED): a Thorium armor set at the P6 costs
  (729 bars x 18 s) took 3.6 h in the Furnace and the queue held only 256.
  1. NEW Server Setup row "Furnace time (% of vanilla)" bench.furnacePct (int 1-100, default 25, live): a Furnace unit takes vanilla recipe
     time x (1 - bench tier reduction) x pct / 100 (ProcBench.unitMs, the one unit-time formula: the queue, the row's "each" time and the
     queue's "done in" all read it), THEN the Furnace Charm's time cut on top (charmMs, unchanged). The Tannery is untouched. A job keeps the
     unit time it was queued with (0.8.24 rule): bars queued before the update (or before a change of the row) finish at their old speed.
     Copper bar 10 s -> 2.5 s (charm 50 % -> 1.25 s); Thorium 18 s -> 4.5 s (a 1,000-bar queue = 1.25 h).
  2. bench.queueCap default 256 -> 1000 (units per player's Furnace / Tannery queue).
  3. ONE-TIME CONFIG UPDATE (PROJECT-RULES 4; SackMig0826 = SackMig0824's reviewed code, run right AFTER it in setup, before SackCfg.reload):
     bench.queueCap moves 256 -> 1000 ONLY while its line still holds 256 (a number by value); a hand-edited, doubled or continued line is kept
     and named in an INFO line; the commented template line "#bench.queueCap=256" gets the new default; a verified History copy first, one
     change-log line per moved value (Server Setup -> Changes -> Undo), a Properties check that only that key changed, the marker line
     skyysacks-0.8.26-bench appended LAST (runs once; a fresh file carries it), every other byte and each line's own ending kept.
     bench.furnacePct is a NEW row: no line = 25, no migration needed. (Skyy's NewBetaTest file holds "#bench.queueCap=256" commented = the
     code default: only that comment line is refreshed; the running cap becomes 1000.)
  No saved-data change (queued jobs, fuel and output untouched). No new command / system / bridge key.
  ROLLBACK to 0.8.24: safe (0.8.24 ignores bench.furnacePct = vanilla speed again; a migrated bench.queueCap=1000 line stays - 0.8.24 reads it;
  Undo it in Server Setup -> Changes first if wanted).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.24.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.26.py"))
assert P.has('VERSION = "0.8.24"\n') and P.has('smig24 = pool.makeClass(PKG + ".SackMig0824")') and not P.has("utilCounts") \
    and not P.has("SackMig0826"), "not the live generated SkyySacks 0.8.24 (0.8.25's off-hand refill must not be in the base)"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.26 (2026-10-21)"):].rstrip() + "\n"

# ---- header, version
P.rep('''  costs naming Beech / Dry / Bottletree logs then count 0.8.23's 5-group log tiers) - Undo them in Server Setup -> Changes first if wanted.
"""
''', '''  costs naming Beech / Dry / Bottletree logs then count 0.8.23's 5-group log tiers) - Undo them in Server Setup -> Changes first if wanted.
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.24"\n', 'VERSION = "0.8.26"\n')

# ---- 1 + 2: the caps table (one source for the field, the row, the file line and reload's clamp)
P.rep('''    ("bench.queueCap",   "ProcBench.QUEUE_CAP",   256, 1, 10000),
''', '''    ("bench.queueCap",   "ProcBench.QUEUE_CAP",  1000, 1, 10000),   # 0.8.26 (Balance P6 Q6): 256 -> 1000
''')
P.rep('''    ("bench.outputCap",  "ProcBench.OUT_CAP",   20000, 1, 1000000),
]
''', '''    ("bench.outputCap",  "ProcBench.OUT_CAP",   20000, 1, 1000000),
    ("bench.furnacePct", "ProcBench.FURNACE_PCT",   25, 1, 100),     # 0.8.26 (Balance P6 Q6): Furnace unit time in % of vanilla
]
# 0.8.26: the one-time config update (SackMig0826, right after SackMig0824): bench.queueCap 256 -> 1000 while untouched
MIG0826 = [("bench.queueCap", "256", "1000", "n")]
MIG0826_MK = 'skyysacks-0.8.26-bench'
assert [(k, d) for (k, _f, d, _lo, _hi) in SACK_CAPS if k.startswith("bench.")] == [("bench.queueCap", 1000), ("bench.fuelCap", 1000),
                                                                                   ("bench.outputCap", 20000), ("bench.furnacePct", 25)]
''')
P.rep('''    "# Furnace and Tannery (each player has their own): queue size in units, fuel slot size in items, output held before it pauses.",
''', '''    "# Furnace and Tannery (each player has their own): queue size in units, fuel slot size in items, output held before it pauses;",
    "# furnacePct: the Furnace smelt time in percent of the vanilla time (25 makes it 4x faster; the Furnace Charm cuts more; not the Tannery).",
    "# SkyySacks 0.8.26 defaults (marker %s): Furnace 4x faster, queue 1000 units." % MIG0826_MK,
''')
# SackCfg.reload: the new key (read, clamped, published, logged)
P.rep('''    int oc = intKey(p, "bench.outputCap", @D:bench.outputCap@);
''', '''    int oc = intKey(p, "bench.outputCap", @D:bench.outputCap@);
    int fp = intKey(p, "bench.furnacePct", @D:bench.furnacePct@);   // 0.8.26
''')
P.rep('''      || qc != com.skyy.sacks.ProcBench.QUEUE_CAP || fc != com.skyy.sacks.ProcBench.FUEL_CAP || oc != com.skyy.sacks.ProcBench.OUT_CAP;''',
      '''      || qc != com.skyy.sacks.ProcBench.QUEUE_CAP || fc != com.skyy.sacks.ProcBench.FUEL_CAP || oc != com.skyy.sacks.ProcBench.OUT_CAP
      || fp != com.skyy.sacks.ProcBench.FURNACE_PCT;''')
P.rep('''    com.skyy.sacks.ProcBench.OUT_CAP = oc;
''', '''    com.skyy.sacks.ProcBench.OUT_CAP = oc;
    com.skyy.sacks.ProcBench.FURNACE_PCT = fp;
''')
P.rep('''+ "; Furnace / Tannery queue " + qc + " units, fuel " + fc + ", output " + oc); } catch (Throwable t3) { }''',
      '''+ "; Furnace / Tannery queue " + qc + " units, fuel " + fc + ", output " + oc + "; Furnace time " + fp + " % of vanilla"); } catch (Throwable t3) { }''')
P.rep('''   .replace("@D:bench.outputCap@", "%d, %d, %d" % _jfield("bench.outputCap")[1:]), scfg))''',
      '''   .replace("@D:bench.outputCap@", "%d, %d, %d" % _jfield("bench.outputCap")[1:])
   .replace("@D:bench.furnacePct@", "%d, %d, %d" % _jfield("bench.furnacePct")[1:]), scfg))''')
# the Server Setup row (SkyyVoid and Crafting -> Furnace and Tannery)
P.rep('''    "bench.outputCap": ("Output held before pausing", "benches", "live,adv",
                        "Output a Furnace or Tannery keeps before it pauses until the player collects. Nothing is lost."),
''', '''    "bench.outputCap": ("Output held before pausing", "benches", "live,adv",
                        "Output a Furnace or Tannery keeps before it pauses until the player collects. Nothing is lost."),
    # 0.8.26 (Balance P6 Q6, Skyy "just go with the recommended on all of them")
    "bench.furnacePct": ("Furnace time (% of vanilla)", "benches", "live",
                         "25 = smelts 4x faster than vanilla; the Furnace Charm cuts more. Not the Tannery. Next queued bars."),
''')
# ProcBench.unitMs: the Furnace percent (before the charm, which charmMs applies on top)
P.rep('''public static long unitMs({CRR} r, String bench, int tier) {{
  double t = (double) r.getTimeSeconds();
  if (t < 0.0) t = 0.0;
  double red = (double) reduction(bench, tier);
  long v = Math.round((t - t * red) * 1000.0);''', '''public static long unitMs({CRR} r, String bench, int tier) {{
  double t = (double) r.getTimeSeconds();
  if (t < 0.0) t = 0.0;
  double red = (double) reduction(bench, tier);
  double pct = 1.0;
  if ("Furnace".equalsIgnoreCase(bench)) {{   // 0.8.26 (Balance P6 Q6): bench.furnacePct of the vanilla time; the Tannery untouched
    int fp = FURNACE_PCT;
    if (fp < 1) fp = 1;
    if (fp > 100) fp = 100;
    pct = (double) fp / 100.0;
  }}
  long v = Math.round((t - t * red) * pct * 1000.0);''')

# ---- 3: SackMig0826 = SackMig0824's code (generated from the same block, names / texts swapped) - built right after SackMig0824
_a = P.s.index("# ================= 0.8.24 SackMig0824: SackMig089's code for the 0.8.23 -> 0.8.24 cost defaults")
_b = P.s.index("}'''), smig24))\n\n# ================= 0.7.10: the Workbench tab") + len("}'''), smig24))\n")
M = P.s[_a:_b]
assert M.count("smig24 = pool.makeClass") == 1 and M.count("public static synchronized String run(") == 1
for o, n in (("0.8.24", "@NEW@"), ("0.8.23", "0.8.24"), ("@NEW@", "0.8.26"), ("MIG0824", "MIG0826"), ("SackMig0824", "SackMig0826"), ("smig24", "smig26"),
             ("SackMig089's code for the 0.8.24 -> 0.8.26 cost defaults (Skyy \"i want the upgrade cost to be fair.\n# expensive but manageable\"); "
              "setup() runs it right after SackMig089 (a pre-0.8.9 file: 0.8.8 -> 0.8.9 -> 0.8.26), before SackCfg.reload",
              "SackMig0824's code for the bench.queueCap default 256 -> 1000 (Balance P6\n# Q6); setup() runs it right after SackMig0824, before SackCfg.reload"),
             ("Void upgrade costs on the 15-step tiers (every category also starts with pd.base space)", "Furnace 4x faster (bench.furnacePct) and a 1,000-unit queue"),
             ("(Void upgrade costs on the 15-step tiers)", "(Furnace 4x faster, queue 1000)"),
             ("(Void costs / space;", "(Furnace queue size;"), ("(Void upgrade costs)", "(Furnace queue size)"),
             ("before the 0.8.26 Void upgrade costs update", "before the 0.8.26 Furnace queue size update")):
    assert o in M, o
    M = M.replace(o, n)
assert "0.8.23" not in M and M.count("SackMig0824") == 2 and "smig24" not in M and M.count('"SkyySacks 0.8.26"') == 1 and M.count("MIG0826_MK in l") == 2
P.rep("}'''), smig24))\n\n# ================= 0.7.10: the Workbench tab", "}'''), smig24))\n" + M + "\n# ================= 0.7.10: the Workbench tab")
P.rep('''  {PKG}.SackMig0824.run({PKG}.SackCfg.FILE);  // 0.8.24: untouched 0.8.23 Void cost defaults -> the 15-step tier ones, once (History first; Undo)
''', '''  {PKG}.SackMig0824.run({PKG}.SackCfg.FILE);  // 0.8.24: untouched 0.8.23 Void cost defaults -> the 15-step tier ones, once (History first; Undo)
  {PKG}.SackMig0826.run({PKG}.SackCfg.FILE);  // 0.8.26: an untouched bench.queueCap 256 -> 1000, once (History first; Undo)
''')
P.rep('''          smig24,   # 0.8.24: SackMig0824
''', '''          smig24,   # 0.8.24: SackMig0824
          smig26,   # 0.8.26: SackMig0826
''')

assert P.s.count("SackMig0826.run(") == 1 and P.s.count('pool.makeClass(PKG + ".SackMig0826")') == 1
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.26 adds no system / command"
P.finish()
