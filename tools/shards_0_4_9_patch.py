"""Derive SkyyShards/build_skyyshards_0.4.9.py from the GENERATED SkyyShards 0.4.8 (build_skyyshards_0.4.8.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_8_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.8 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_9_patch.py   then   python SkyyShards/build_skyyshards_0.4.9.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.9.py

0.4.9 (2026-10-24) = THE SHARD UPGRADE MAP (starter archipelago round R3, research/Starter-Archipelago-Spec.md section 6 + section 16 row R3)
  + THE SHARD RE-BALANCE. Skyy's words (docs/answered/world.md): 2026-10-23 SHARD UPGRADE MAP "but i also want the shard upgrade menu to be
  much more visual. i want it to use a similar visual to the new trees we just added. ..." + 2026-10-24 SHARD UPGRADE BONUS "+2% or more per
  lvl, new islands stay the same. max islands out put should far exceed player productivity. (you can make itr slower offline or can how
  long it keeps harvesting offline (make the offline harvest time another upgrade.) but with the numbers required for late game collection,
  and money making, the shards will be the primary way to collect late game, so players can focus on the combat." + "Start the next queued
  rounds from RESUME (Shards R3 re-balance, ...)".
  1. THE MAP TAB (spec 6): the shard menu is one 1600 x 980 window (Menu-Pattern 3.6) with ONE tab row Map | Totems | Collect (the old
     Upgrades + Islands tabs are the map now; the menu opens on the Map). Map = left rail 232 (the 6 shards: icon, name in the shard colour,
     "Farming 7 - 3 islands" or red "Locked - Farming 5"; click = that shard's map when its portal is on this island; the legend) | the map
     840 x 688 (tools/skyymap.py shard_layout 1.0: the shard hub in the centre - click = shard view -, one disc per island in tier order at
     its WORLD slot angle (inner ring = the 6 hexagon places, outer ring = the 10 places between), lines = the world's bridges, gold when
     the island is yours, captions "T2 Lettuce"; disc pictures: yours = the shard colour ring + Small / Medium / Large pips, complete =
     glow, can buy now = gold ring, next but not affordable = light ring, locked = padlock, selected = the cyan halo; zoom 100 / 150 / 200 %
     in the 2-axis scroll box) | the right panel 456 with THREE views: SHARD (Automation, Storage, Auto-Compactor, Time Compressor, Offline
     Harvest - each name, now -> next, coins + items as a green / red requirement list, one Upgrade button; the Totem Bench note), ISLAND
     (Size with pips + Grow, Amount / Decorations / Irrigation with 5 pips each, what the next level adds, their costs, the seed store) and
     BUY (the island's costs as a requirement list, the tier-order gate, Buy island). Every click answers with ONE page packet: a rebuild,
     or at 150 / 200 % (shard.ui.keepScroll, ON) ONE sendUpdate that keeps the zoomed view where it is (kit 1.9 keep mode: every line drawn,
     the halo moved, pre-placed pictures, every panel text + colour variant set in place); a change that cannot be shown that way rebuilds.
  2. RE-BALANCE (Skyy 2026-10-24): each sub-upgrade level is +3 % (was +0.5 %; Skyy "+2% or more" - 3 % because it is the smallest whole
     % that meets the x2.5 "far exceed" target: a maxed Large island at Totem V makes x3.05 a focused hand-gathering hour (x6.1 with Time
     Compressor III; 2 % gives only x2.2, 4 % x4.1) and Zone 5 earns x3.98 of the active coin target per played hour with that island maxed
     (balance_model.py --p11), so shards are the primary late-game source); a new island keeps today's output (subs 0 = x1);
     tools/balance_model.py --p11 re-fitted (the P6 idle cap row replaced by the shard target). ShMig049 (PROJECT-RULES 4, ShMig048's
     reviewed machinery): isl.amount.bonus / isl.deco.pct / isl.irrigation.pct 0.5 -> 3 ONLY while a line still holds 0.5 (hand-edited
     values kept + INFO), History snapshot first, one change-log line each with Undo, marker skyyshards-0.4.9-bonus, bytes + line endings kept.
  3. OFFLINE HARVEST = ITS OWN SHARD UPGRADE (Skyy: "make the offline harvest time another upgrade"): Offline Harvest 0-5 per shard =
     production counts at most 12 / 18 / 24 / 36 / 48 / 72 h between visits (up.offline.hours; shard.maxOfflineSec stays the server's hard
     ceiling; before Automation shard.manualOfflineSec 2 h still applies); levels 1-5 cost the shard ladder steps 3 / 5 / 6 / 7 / 8 (1,400 ..
     105,000 coins) + 1 / 2 / 4 / 8 / 16 of the shard's upgrade item (up.offline.steps / up.offline.ench). No player file is rewritten: a
     shard made by 0.4.9 starts at level 0 (<kind>.offline=0 written with its first island); a shard without the key (every shard owned
     before 0.4.9) counts as level 5 = the old 3 days (nothing anyone owns gets worse).
  4. STORAGE KEEPS ITS TIME: an island's storage = the shard storage tier x the island's upgrade multiplier (a maxed Large island holds 3x as
     many items, so the same hours) - never less than before.
  NOT IN THIS ROUND: /island archipelago retry + the 12 / 24 block shift for a blocked starter island (SkyyIslands - a follow-up round), the
  Combat zone islands (R5), multi-block decoration set pieces (windmill / barn / fountain - the 0.4.8 single-cell props stay).
  SAVED DATA: one new key per shard made from now on (<kind>.offline 0-5); nothing migrated. Config: 4 new rows (up.offline.hours / steps /
  ench, shard.ui.keepScroll) + 3 new defaults moved by ShMig049 (isl.amount.bonus / isl.deco.pct / isl.irrigation.pct).
  ROLLBACK 0.4.9 -> 0.4.8: alone (no FLOOR entry needed beyond 0.4.8's own with SkyyIslands 0.5.25). Undo the ShMig049 rows first if wanted
  (Server Setup -> Shards -> Changes); 0.4.8 ignores <kind>.offline and the new rows (bought Offline Harvest levels are then unused, 3 days).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.8.py"), os.path.join(HERE, "build_skyyshards_0.4.9.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.8"\n') and P.has("GENERATED by tools/shards_0_4_8_patch.py") and not P.has("ShMig049"), "not the generated SkyyShards 0.4.8"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.9 (2026-10-24)"):].rstrip() + "\n"

P.rep('''"""SkyyShards 0.4.8 - build script (javassist via jpype). GENERATED by tools/shards_0_4_8_patch.py from build_skyyshards_0.4.7.py
(generated by tools/shards_0_4_7_patch.py from 0.4.6, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.8.py   -> SkyyShards/SkyyShards-0.4.8.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.8.py
''', '''"""SkyyShards 0.4.9 - build script (javassist via jpype). GENERATED by tools/shards_0_4_9_patch.py from build_skyyshards_0.4.8.py
(generated by tools/shards_0_4_8_patch.py from 0.4.7, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.9.py   -> SkyyShards/SkyyShards-0.4.9.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.9.py
''' + NOTE + '''
0.4.8 notes:
''')
P.rep('VERSION = "0.4.8"\n', 'VERSION = "0.4.9"\n')

# ================================================================================================ engine members of the keep update
P.rep('''             (T["FSC"], "getComponentType"), (T["FSC"], "setFluid"), (T["FSC"], "getFluidId"), (T["FLU"], "getAssetMap"), (T["FLU"], "getMaxFluidLevel")):
    B.probe(pool, c, m)''', '''             (T["FSC"], "getComponentType"), (T["FSC"], "setFluid"), (T["FSC"], "getFluidId"), (T["FLU"], "getAssetMap"), (T["FLU"], "getMaxFluidLevel"),
             # 0.4.9: the map tab's keep update (kit 1.9: one sendUpdate, the halo Anchor)
             (T["PAGE"], "sendUpdate"), (T["UCB"], "setObject"), (SUI.MAP_KEEP_TYPES["ANC"], "setLeft"), (SUI.MAP_KEEP_TYPES["ANC"], "setTop"),
             (SUI.MAP_KEEP_TYPES["ANC"], "setWidth"), (SUI.MAP_KEEP_TYPES["ANC"], "setHeight"), (SUI.MAP_KEEP_TYPES["VAL"], "of")):
    B.probe(pool, c, m)''')

# ================================================================================================ 2. the re-balance numbers + 3. offline harvest
P.rep('''BONUS48 = 0.5                            # % per level of each sub-upgrade, kept across sizes (maxed Large = 1.075 ^ 3 = x1.24; the spec's +2 %: see the header, item 5)
DECO_N48 = 5                             # fix (critic): props each Decorations level places (a border section; Server Setup isl.deco.props 1-8)
assert (1 + BONUS48 * 15 / 100.0) ** 3 <= 1.25, "0.4.8: a maxed Large stays under the spec's x1.25"''',
      '''BONUS48 = 0.5                            # the 0.4.8 default (ShMig049 moves rows still holding it)
DECO_N48 = 5                             # fix (critic): props each Decorations level places (a border section; Server Setup isl.deco.props 1-8)
# 0.4.9 RE-BALANCE (Skyy 2026-10-24 "+2% or more per lvl, new islands stay the same. max islands out put should far exceed player
# productivity"): +3 % a level on each sub-upgrade, levels count on across the sizes: a new island x1.000, a maxed Large = 1.45 ^ 3 = x3.05
# (tools/balance_model.py --p11: Totem V maxed = 305 % of a focused hand hour; the P6 idle cap no longer binds shards)
BONUS49 = 3.0
assert BONUS49 >= 2.0 and (1 + BONUS49 * 15 / 100.0) ** 3 >= 2.5, "0.4.9: +2 % or more a level, a maxed Large far above hand gathering"
assert abs(_BM48.P11_BONUS - BONUS49) < 1e-9 and abs(_BM48.P11_BONUS_048 - BONUS48) < 1e-9, "0.4.9: tools/balance_model.py --p11 models these numbers"
# 0.4.9 OFFLINE HARVEST (Skyy: "make the offline harvest time another upgrade"): level 0..5 hours, levels 1..5 cost these ladder steps + this
# many of the shard's upgrade item; a shard without the key (owned before 0.4.9) = level 5 = the old 3 days
OFF_H49 = [12, 18, 24, 36, 48, 72]
OFF_STEP49 = [3, 5, 6, 7, 8]
OFF_ENCH49 = [1, 2, 4, 8, 16]
assert OFF_H49 == _BM48.P11_OFF_H and OFF_STEP49 == _BM48.P11_OFF_STEP and OFF_H49[-1] * 3600 == 259200, "0.4.9: the --p11 offline ladder; level 5 = 3 days"
MIG049 = [(_k, "%g" % BONUS48, "%g" % BONUS49, "n") for _k in ("isl.amount.bonus", "isl.deco.pct", "isl.irrigation.pct")]
MIG049_MK = "skyyshards-0.4.9-bonus"
MIG049_LINE = "# ---------- SkyyShards 0.4.9 (marker %s, runs once): shards are the primary late-game source - +3 %% a sub-upgrade level (was 0.5 %%); only untouched old default lines were changed ----------" % MIG049_MK''')

# ---- the config text: the bonus rows at the new default, the offline rows, the keep switch, the 0.4.9 marker
P.rep('''    "isl.amount.pct=" + ",".join(str(_x) for _x in AMT_PCT48), "isl.amount.bonus=%g" % BONUS48, "isl.deco.pct=%g" % BONUS48, "isl.irrigation.pct=%g" % BONUS48,''',
      '''    "isl.amount.pct=" + ",".join(str(_x) for _x in AMT_PCT48), "isl.amount.bonus=%g" % BONUS49, "isl.deco.pct=%g" % BONUS49, "isl.irrigation.pct=%g" % BONUS49,''')
P.rep('''    "# SkyyShards 0.4.8 defaults (marker %s): shards come with the starter islands, the cheap-first ladder - keep this line." % MIG048_MK,''',
      '''    "# SkyyShards 0.4.8 defaults (marker %s): shards come with the starter islands, the cheap-first ladder - keep this line." % MIG048_MK,
    "# up.offline.hours = 0.4.9 OFFLINE HARVEST: hours production counts between two visits at Offline Harvest level 0..5 (6 numbers; a",
    "# shard owned before 0.4.9 is level 5; shard.maxOfflineSec stays the ceiling, shard.manualOfflineSec before Automation).",
    "# up.offline.steps = the shard ladder step each level 1..5 costs; up.offline.ench = the shard's upgrade item per level 1..5.",
    "up.offline.hours=" + ",".join(str(_x) for _x in OFF_H49), "up.offline.steps=" + ",".join(str(_x) for _x in OFF_STEP49),
    "up.offline.ench=" + ",".join(str(_x) for _x in OFF_ENCH49),
    "# shard.ui.keepScroll = 0.4.9: at 150 / 200 % a click on the shard map updates it in place (the view stays); false = every click redraws.",
    "shard.ui.keepScroll=true",
    "# SkyyShards 0.4.9 defaults (marker %s): +3 %% a sub-upgrade level, Offline Harvest upgrades - keep this line." % MIG049_MK,''')
P.rep('''    "shard.maxOfflineSec=259200",''', '''    "shard.maxOfflineSec=259200",   # 0.4.9: the ceiling of Offline Harvest (up.offline.hours)''')

# ---- ShCfg fields
P.rep('''          "public static volatile double AMT_BONUS = %r;" % BONUS48, "public static volatile double DECO_PCT = %r;" % BONUS48,
          "public static volatile double IRR_PCT = %r;" % BONUS48, "public static volatile int DECO_N = %d;" % DECO_N48,''',
      '''          "public static volatile double AMT_BONUS = %r;" % BONUS49, "public static volatile double DECO_PCT = %r;" % BONUS49,   # 0.4.9: +3 %
          "public static volatile double IRR_PCT = %r;" % BONUS49, "public static volatile int DECO_N = %d;" % DECO_N48,
          # 0.4.9: Offline Harvest (hours per level 0..5, the ladder step + upgrade items per level 1..5), the map's keep switch
          "public static final double[] DEF_OFF_H = new double[] { %s };" % ", ".join("%r" % float(_x) for _x in OFF_H49),
          "public static final int[] DEF_OFF_STEP = new int[] { %s };" % ", ".join(str(_x) for _x in OFF_STEP49),
          "public static final int[] DEF_OFF_ENCH = new int[] { %s };" % ", ".join(str(_x) for _x in OFF_ENCH49),
          "public static volatile double[] OFF_H = new double[] { %s };" % ", ".join("%r" % float(_x) for _x in OFF_H49),
          "public static volatile int[] OFF_STEP = new int[] { %s };" % ", ".join(str(_x) for _x in OFF_STEP49),
          "public static volatile int[] OFF_ENCH = new int[] { %s };" % ", ".join(str(_x) for _x in OFF_ENCH49),
          "public static volatile boolean UI_KEEP = true;",''')

# ---- Server Setup rows (category ladder "Island upgrades")
P.rep('''         ("isl.amount.bonus", "Amount: output per level", "ladder", "dec", "%g" % BONUS48, "0", "100", "", "%", "live",
          "Percent more output per Amount level (levels count on across sizes).", "reload@config.properties:isl.amount.bonus"),
         ("isl.deco.pct", "Decorations: output per level", "ladder", "dec", "%g" % BONUS48, "0", "100", "", "%", "live",
          "Happier workers: percent more output per Decorations level (across sizes).", "reload@config.properties:isl.deco.pct"),
         ("isl.irrigation.pct", "Irrigation: output per level", "ladder", "dec", "%g" % BONUS48, "0", "100", "", "%", "live",
          "Faster regrowth: percent more output per Irrigation level (across sizes).", "reload@config.properties:isl.irrigation.pct"),''',
      '''         ("isl.amount.bonus", "Amount: output per level", "ladder", "dec", "%g" % BONUS49, "0", "100", "", "%", "live",
          "Percent more output per Amount level (levels count on across sizes; 0.4.9: 3).", "reload@config.properties:isl.amount.bonus"),
         ("isl.deco.pct", "Decorations: output per level", "ladder", "dec", "%g" % BONUS49, "0", "100", "", "%", "live",
          "Happier workers: percent more output per Decorations level (across sizes).", "reload@config.properties:isl.deco.pct"),
         ("isl.irrigation.pct", "Irrigation: output per level", "ladder", "dec", "%g" % BONUS49, "0", "100", "", "%", "live",
          "Faster regrowth: percent more output per Irrigation level (across sizes).", "reload@config.properties:isl.irrigation.pct"),
         # 0.4.9: Offline Harvest + the map's keep switch
         ("up.offline.hours", "Offline Harvest: hours, level 0-5", "ladder", "text", ",".join(str(_x) for _x in OFF_H49), "", "80", "", "", "live",
          "6 numbers: hours production counts between visits at Offline Harvest 0..5.", "reload@config.properties:up.offline.hours"),
         ("up.offline.steps", "Offline Harvest: ladder steps", "ladder", "text", ",".join(str(_x) for _x in OFF_STEP49), "", "40", "", "", "live",
          "5 numbers: the shard ladder step levels 1..5 cost (coins = up.hours at up.levels).", "reload@config.properties:up.offline.steps"),
         ("up.offline.ench", "Offline Harvest: upgrade items", "ladder", "text", ",".join(str(_x) for _x in OFF_ENCH49), "", "60", "", "", "live",
          "5 numbers: the shard's upgrade item (Enchanted) levels 1..5 cost.", "reload@config.properties:up.offline.ench"),
         ("shard.ui.keepScroll", "Zoomed map keeps its place", "ladder", "bool", "true", "", "", "", "", "live",
          "ON: at 150 / 200 % a shard map click updates in place (the view stays). OFF: each click redraws.", "reload@config.properties:shard.ui.keepScroll"),''')
P.rep('''     "Production counts at most this long between two menu visits (259200 = 3 days).", "field:ShCfg.MAX_OFF_SEC@config.properties:shard.maxOfflineSec"),''',
      '''     "The Offline Harvest ceiling: production never counts longer between visits (259200 = 3 days).", "field:ShCfg.MAX_OFF_SEC@config.properties:shard.maxOfflineSec"),''')

# ---- the loader
P.rep('''          "  AMT_BONUS = decOf(p.getProperty(\\"isl.amount.bonus\\"), %r, 0.0, 100.0);" % BONUS48,
          "  DECO_PCT = decOf(p.getProperty(\\"isl.deco.pct\\"), %r, 0.0, 100.0);" % BONUS48,
          "  IRR_PCT = decOf(p.getProperty(\\"isl.irrigation.pct\\"), %r, 0.0, 100.0);" % BONUS48,''',
      '''          "  AMT_BONUS = decOf(p.getProperty(\\"isl.amount.bonus\\"), %r, 0.0, 100.0);" % BONUS49,
          "  DECO_PCT = decOf(p.getProperty(\\"isl.deco.pct\\"), %r, 0.0, 100.0);" % BONUS49,
          "  IRR_PCT = decOf(p.getProperty(\\"isl.irrigation.pct\\"), %r, 0.0, 100.0);" % BONUS49,
          "  OFF_H = decsOf(p.getProperty(\\"up.offline.hours\\"), DEF_OFF_H, 0.0, 720.0, \\"up.offline.hours\\");",   # 0.4.9
          "  OFF_STEP = intsOf(p.getProperty(\\"up.offline.steps\\"), DEF_OFF_STEP, 1, 10, \\"up.offline.steps\\");",
          "  OFF_ENCH = intsOf(p.getProperty(\\"up.offline.ench\\"), DEF_OFF_ENCH, 0, 100000, \\"up.offline.ench\\");",
          "  UI_KEEP = bool(p.getProperty(\\"shard.ui.keepScroll\\"), true);",''')

# ================================================================================================ ShMig049 = ShMig048's machinery, the 0.4.9 table
_a = P.s.index('''smig48 = mk("ShMig048")''')
_b = P.s.index('''M(cfg, r"""
public static int stacks(int tier) {''', _a)
_P49 = P.s[_a:_b]
for _x, _y in (('smig48 = mk("ShMig048")', 'smig49 = mk("ShMig049")'), ("F(smig48, _d)", "F(smig49, _d)"), ("M(smig48, r", "M(smig49, r"),
               ("jlit(MIG048_MK)", "jlit(MIG049_MK)"), ('"SkyyShards 0.4.8";', '"SkyyShards 0.4.9";'), ("jlit(MIG048_LINE)", "jlit(MIG049_LINE)"),
               ("for m in MIG048)", "for m in MIG049)"),
               ("the 0.4.8 default is", "the 0.4.9 default is"),
               ("NOT updated for SkyyShards 0.4.8 (starter shards, cheap-first ladder)", "NOT updated for SkyyShards 0.4.9 (+3 % a sub-upgrade level)"),
               ('"before the 0.4.8 update (starter shards, cheap-first ladder)"', '"before the 0.4.9 update (+3 % a sub-upgrade level)"'),
               ('"config.properties updated for SkyyShards 0.4.8 (shards come with the starter islands - level 20 grants off; cheaper totem tier-ups; storage on the cheap-first ladder): "',
                '"config.properties updated for SkyyShards 0.4.9 (shards are the primary late-game source: +3 % output a sub-upgrade level, was 0.5 %): "'),
               ("could not update config.properties for SkyyShards 0.4.8 (starter shards;", "could not update config.properties for SkyyShards 0.4.9 (+3 % a level;"),
               ("loadCfg writes the 0.4.8 default with the marker", "loadCfg writes the 0.4.9 default with the marker")):
    assert _P49.count(_x) >= 1, _x
    _P49 = _P49.replace(_x, _y)
assert "smig48" not in _P49 and "MIG048" not in _P49 and "0.4.8" not in _P49, [l for l in _P49.split("\n") if "0.4.8" in l or "MIG048" in l][:5]
P.rep('''M(cfg, r"""
public static int stacks(int tier) {''', '''# ================= 0.4.9 ShMig049 (PROJECT-RULES 4; ShMig048's reviewed machinery copied by tools/shards_0_4_9_patch.py): the 3 sub-upgrade
# bonus rows 0.5 -> 3 (Skyy 2026-10-24 "+2% or more per lvl"), only while a line still holds its old default; setup() runs it right after ShMig048
for _k, _o, _n, _t in MIG049:
    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k            # the new default file holds the new value
    assert _o != _n
assert CONFIG_TEXT.count(MIG049_MK) == 1
''' + _P49 + '''M(cfg, r"""
public static int stacks(int tier) {''')
P.rep('''  try { @PKG@.ShMig048.run(@PKG@.ShCfg.FILE); }   // 0.4.8: untouched lv20.* 20 -> 0, totem.upCost + storage.coins onto the cheap-first ladder, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.8 settings update was skipped: " + t); }''',
      '''  try { @PKG@.ShMig048.run(@PKG@.ShCfg.FILE); }   // 0.4.8: untouched lv20.* 20 -> 0, totem.upCost + storage.coins onto the cheap-first ladder, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.8 settings update was skipped: " + t); }
  try { @PKG@.ShMig049.run(@PKG@.ShCfg.FILE); }   // 0.4.9: untouched sub-upgrade bonus rows 0.5 -> 3 (+3 % a level), once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.9 settings update was skipped: " + t); }''')

# ================================================================================================ 3. Offline Harvest: the level, the cap, the purchase
P.rep('''M(isl48, r"""
public static long offMs(int kd, java.util.Properties p) {
  long a = (long) @PKG@.ShCfg.MAX_OFF_SEC;
  if (auto(kd, p)) return 1000L * a;
  long m = (long) @PKG@.ShCfg.MAN_OFF_SEC;
  return 1000L * (m < a ? m : a);
}""")''', '''# 0.4.9 OFFLINE HARVEST: the shard's level 0..5 (<kind>.offline; no key = a shard owned before 0.4.9 = level 5, the old 3 days), its hours
M(isl48, r"""
public static int offLv(int kd, java.util.Properties p) {
  if (p == null) return 0;
  String v = @PKG@.ShStore.str(p, kk(kd, "offline"));
  if (v.length() == 0) return 5;
  return @PKG@.ShStore.intv(p, kk(kd, "offline"), 0, 0, 5);
}""")
M(isl48, r"""
public static double offH(int lv) {
  return @PKG@.ShCfg.OFF_H[lv < 0 ? 0 : (lv > 5 ? 5 : lv)];   // decsOf always gives the 6 default-length hours
}""")
# the most ms production counts between two visits: Offline Harvest hours (shard.maxOfflineSec the ceiling); before Automation also
# shard.manualOfflineSec (0.4.8)
M(isl48, r"""
public static long offMs(int kd, java.util.Properties p) {
  long a = (long) @PKG@.ShCfg.MAX_OFF_SEC;
  long o = (long) Math.floor(offH(offLv(kd, p)) * 3600.0 + 0.5);
  if (o < 60L) o = 60L;
  if (o < a) a = o;
  if (auto(kd, p)) return 1000L * a;
  long m = (long) @PKG@.ShCfg.MAN_OFF_SEC;
  return 1000L * (m < a ? m : a);
}""")''')
P.rep('''  if (kd == FK) p.setProperty(ik(kd, 0, "eternal"), "8");   // 0.4.8 (Skyy): "it starts with like 8 eternal wheat around the totem, and a bunch of tilled soil"
}""")''', '''  if (kd == FK) p.setProperty(ik(kd, 0, "eternal"), "8");   // 0.4.8 (Skyy): "it starts with like 8 eternal wheat around the totem, and a bunch of tilled soil"
  p.setProperty(kk(kd, "offline"), "0");   // 0.4.9: a new shard starts at Offline Harvest 0 (a shard without the key = owned before 0.4.9 = level 5)
}""")''')
# 4. storage keeps its time: x the island's upgrade multiplier (never below the 0.4.8 storage)
P.rep('''M(mth, r"""
public static long capOf(int kd, java.util.Properties p, int slot) {
  return cap(kd, p) + 300L * (long) @PKG@.ShTotem.modsOnIsland(kd, p, slot, "storage");
}""")''', '''M(mth, r"""
public static long capOf(int kd, java.util.Properties p, int slot) {
  long c = cap(kd, p) + 300L * (long) @PKG@.ShTotem.modsOnIsland(kd, p, slot, "storage");
  double m = hasIsland(kd, p, slot) ? @PKG@.ShIsl.mult(kd, p, slot, size(kd, p, slot)) : 1.0;   // 0.4.9: the same hours at every upgrade level
  if (m > 1.0) { double x = Math.floor((double) c * m); c = x > 9.0E15 ? 9000000000000000L : (long) x; }
  return c;
}""")''')
# the purchase (owner only; the shard ladder step of the level + the shard's upgrade item); settled first at the old cap (purchaseM)
P.rep('''M(core, "public static String buyAuto(java.util.UUID u, String k, int kd, @IC@[] cs) { String r = buyAuto0(u, k, kd, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")''',
      '''M(core, "public static String buyAuto(java.util.UUID u, String k, int kd, @IC@[] cs) { String r = buyAuto0(u, k, kd, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# 0.4.9 OFFLINE HARVEST (Skyy: "make the offline harvest time another upgrade"): level l -> l + 1 costs ladder step up.offline.steps[l] +
# up.offline.ench[l] of the shard's upgrade item
M(core, r"""
public static long offCoins(int lv, double cv) {
  if (lv < 0 || lv >= 5) return 0L;
  return @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(@PKG@.ShCfg.OFF_STEP[lv]), cv);
}""")
M(core, r"""
public static int offStep(int lv) {
  return (lv < 0 || lv >= 5) ? 1 : @PKG@.ShCfg.OFF_STEP[lv];   // intsOf always gives 5
}""")
M(core, r"""
public static long offEnch(int lv) {
  return (lv < 0 || lv >= 5) ? 0L : (long) @PKG@.ShCfg.OFF_ENCH[lv];
}""")
M(core, r"""
public static String buyOffline0(java.util.UUID u, String k, int kd, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  int lv0; boolean au0;
  @PKG@.ShStore.LOCK.lock(); try { lv0 = @PKG@.ShIsl.offLv(kd, p); au0 = @PKG@.ShIsl.auto(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (lv0 >= 5) return "=Offline Harvest is at its highest level.";
  if (!au0) return "-Buy Automation first - before it this shard harvests only " + @PKG@.ShCfg.dec((double) @PKG@.ShCfg.MAN_OFF_SEC / 3600.0) + " h while nobody visits.";   // fix: no paying for a level that changes nothing
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(offStep(lv0)));   // the bridge asked outside the lock
  int nl;
  @PKG@.ShStore.LOCK.lock(); try {
    int lv = @PKG@.ShIsl.offLv(kd, p);
    if (lv != lv0) return "-Offline Harvest changed meanwhile - open the menu again.";
    nl = lv + 1;
    long coins = offCoins(lv, cv);
    long q = offEnch(lv);
    String it = @PKG@.ShKind.UPG[kd];
    Object[] mats = (q > 0L && it.length() > 0) ? new Object[] { new String[] { it }, new long[] { q } } : new Object[] { new String[0], new long[0] };
    String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.kk(kd, "offline") }, new String[] { String.valueOf(nl) },
                         "offline", @PKG@.ShKind.KEYS[kd] + " offline harvest " + lv + " -> " + nl);
    if (r != null) return r;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return "+Offline Harvest " + nl + "/5: this " + @PKG@.ShKind.NAMES[kd] + " Shard keeps harvesting " + @PKG@.ShCfg.dec(@PKG@.ShIsl.offH(nl)) + " h while nobody visits.";
}""")
M(core, "public static String buyOffline(java.util.UUID u, String k, int kd, @IC@[] cs) { String r = buyOffline0(u, k, kd, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")''')

# ================================================================================================ the classes written
P.rep('''ALLC = [cfg, smig, smig45, smig46, smig48, st, knd, isl48, lv,''', '''ALLC = [cfg, smig, smig45, smig46, smig48, smig49, st, knd, isl48, lv,''')

# ================================================================================================ 1. THE MAP TAB: the menu markup (build time)
_i0 = P.s.index('''# ================= the page (tools/skyyui.py; inline only; ids SkyySh..., no underscores) =================
P = "SkyySh"
PW, PH = 1100, 860
''')
_i1 = P.s.index('''# --- 0.4 VIEW 1: the stand inside the shard hub = an EXIT page''', _i0)
OLD_MENU = P.s[_i0:_i1]


def _cut(a, b):
    i = OLD_MENU.index(a)
    j = OLD_MENU.index(b, i)
    assert OLD_MENU.count(a) == 1 and OLD_MENU.count(b) == 1, (a, b)
    return OLD_MENU[i:j]


def _sub(s, old, new, n=1):
    assert s.count(old) == n, "section anchor count %d (want %d): %s" % (s.count(old), n, old[:160])
    return s.replace(old, new)


HEAD_OLD = _cut('# ================= the page (tools/skyyui.py; inline only', '# --- the summary strip (always).')
STRIP_OLD = _cut('# --- the summary strip (always).', '# --- tabs (0.4: the Craft tab moved')
COLLECT_OLD = _cut('# --- Collect tab (0.4:', '# --- Upgrades tab: three cards')
TOTEMS_OLD = _cut('# --- Totems tab (the selected island', '# --- status + footer (always).')
FOOT_OLD = _cut('# --- status + footer (always).', '# the page check: every element of every segment together')
HEAD_NEW = _sub(HEAD_OLD, '''PW, PH = 1100, 860
''', '''PW, PH = 1600, 980          # 0.4.9: the menu window is 1600 x 980 (Menu-Pattern 3.6; the Map tab's rail | map | panel row) - the bench keeps 1100 x 860
''')
HEAD_NEW = _sub(HEAD_NEW, '''assert (IW, IH) == (1066, 788), (IW, IH)''', '''assert (IW, IH) == (1566, 908), (IW, IH)''')
STRIP_NEW = _sub(STRIP_OLD, '''base.append((STRIP, SUI.group(P + "Sum", layout="Top", w=480, h=60)))
base.text("#" + P + "Sum", P + "Sum1", J_("this.sum1", "1 island - 1 totem - 60 items / hour"), "bold", size=15, h=30, w=480)
base.text("#" + P + "Sum", P + "Sum2", J_("this.sum2", "Portal on your island"), "caption", size=13, h=26, w=480)''',
                 '''SUMW = IW - 24 - (60 + 12 + 260 + 12 + 200) - 12      # 0.4.9: the wider window's summary column
base.append((STRIP, SUI.group(P + "Sum", layout="Top", w=SUMW, h=60)))
base.text("#" + P + "Sum", P + "Sum1", J_("this.sum1", "1 island - 1 totem - 60 items / hour"), "bold", size=15, h=30, w=SUMW)
base.text("#" + P + "Sum", P + "Sum2", J_("this.sum2", "Portal on your island"), "caption", size=13, h=26, w=SUMW)''')
STRIP_NEW = _sub(STRIP_NEW, '''assert 60 + 12 + 480 + 260 + 12 + 200 <= IW - 24, "the strip is wider than the page"''',
                 '''assert 60 + 12 + SUMW + 260 + 12 + 200 <= IW - 24 and SUMW >= 480, "the strip is wider than the page"''')
TOTEMS_NEW = _sub(TOTEMS_OLD, '''"Island 1 - Wheat Small - 1 of 3 pads (pick the island on the Islands tab)"''', '''"Island 1 - Wheat Small - 1 of 3 pads (pick the island on the Map tab)"''')
TOTEMS_NEW = _sub(TOTEMS_NEW, '''TROW_W_TX, TROW_W_ST, TROW_W_BTN = 430, 110, 100''', '''TROW_W_TX, TROW_W_ST, TROW_W_BTN = ROWW - 20 - 110 - 10 - 100 - 10, 110, 100   # 0.4.9: the wider window''')
FOOT_NEW = _sub(FOOT_OLD, '''base2.text(BODY, P + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=IW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})''',
                '''# 0.4.9: the status line = 3 colour variants in a holder (the Map tab's in-place update recolours it with .Visible; stSets fills them; KP_ST above)
base2.append((BODY, SUI.group(P + "StatusH", None, w=IW, h=30, anchor={"top": 4})))
for _vi, _vc in enumerate(KP_ST):
    base2.append(("#" + P + "StatusH", SUI.label(P + "Status%d" % _vi, "", "bold", size=15, h=30, w=IW, align="Center", col=_vc, anchor={"left": 0, "top": 0})))''')

MAP_BLOCK = r'''# ================= 0.4.9 THE SHARD UPGRADE MAP - the Map tab (research/Starter-Archipelago-Spec.md 6; tools/skyymap.py shard_layout + kit 1.8 /
# 1.9 node maps in keep mode, the SkyyRebirth 0.5.1 way). Skyy: "i want it to use a similar visual to the new trees we just added. so in the
# center in the hub of the shard ... you click it, and the menu on the right will show the overall shard upgrades and modifiers you can do.
# then in a radius around it it will show each island in the shard." The map = page data per shard + zoom (com/skyy/shards/map/K<kd>Z<z>K.txt),
# drawn by ShMap.mapDrawK with the island pictures ShPage.fillMap picks from the profile. Every coordinate + picture is fixed + checked here.
import skyymap as SMAP
assert SUI.KIT_MAP_VERSION == "1.8" and SUI.KIT_KEEP_VERSION == "1.9" and SMAP.SHARD_MAP_VERSION == "1.0", "0.4.9: kit 1.8 / 1.9 node maps + skyymap shard maps"
MP = P + "M"                            # every map id starts with this
MRES = "com/skyy/shards/map/"           # the page data resources (next to the classes)
MDIR = "SkyyShards/Map/"                # markup texture paths (relative to Common/UI/Custom/, written WITHOUT @2x)
MJAR = "Common/UI/Custom/"
MZOOMS = tuple(_z / 100.0 for _z in SUI.MAP_ZOOMS)          # 1.0 / 1.5 / 2.0
MW, MH = SUI.MAP_CANVAS_W, CH                               # 840 x 688 (the window's content height)
MNODE, MEMB, MHUB, MHALO, MHUBH = 40, 96, 44, 56, 72        # disc, emblem, hub, the selected halo, the hub's halo
MROW_W = SUI.MAP_RAIL_W + SUI.MAP_GAP + MW + SUI.MAP_GAP + SUI.MAP_PANEL_W
assert MROW_W == 1552 and MROW_W <= IW, MROW_W
KCOL = [SUI.TREE_COLOR[{"Ranching": "Beastmastery", "Orchard": "Cooking"}.get(_k, _k)] for _k in KINDS]   # the shard colours (kit tree colours)
KCN = [SMAP.colour_name(_c) for _c in KCOL]
MOTTO = {"Mining": "Dig deeper cave by cave", "Foraging": "Grow a forest tier by tier", "Farming": "Grow it island by island",
         "Ranching": "Raise a herd pen by pen", "Orchard": "Fill the orchard tree by tree", "Combat": "Zone islands come later"}
# the world slot angles (SLOT_POS x = east, z = south): map 0 = up = north, clockwise - the map mirrors the shard world (spec 6)
MSLOTS = []
for _i in range(SLOTS):          # the exact slot angles of SLOT_POS (inner 60 x i, outer 18 + 36 x j), checked against the rounded block places
    _deg = 60.0 * _i if _i < NINNER else 18.0 + 36.0 * (_i - NINNER)
    _x, _z = SLOT_POS[_i]
    _dw = (math.degrees(math.atan2(_x, -_z)) - _deg + 540.0) % 360.0 - 180.0
    assert abs(_dw) < 1.0, (_i, _deg, _dw)
    MSLOTS.append((_deg, 0 if _i < NINNER else 1, -1 if _i < NINNER else SLOT_SRC[_i]))
MCAP = [["T%d %s" % (_t["tier"], _t["name"]) for _t in LAD[_k]] for _k in range(NK)]   # the disc captions (tier tag first)
MLAY = []                       # per kind: [layout at each zoom]
for _k in range(NK):
    _lw = [int(math.ceil(SUI.text_width(_c, 13) / 2.0 + 5)) * 2 for _c in MCAP[_k]]
    _l0 = SMAP.shard_layout(MSLOTS[:len(LAD[_k])], key=KKEYS[_k], col=KCOL[_k], W=MW, H=MH, node=MNODE, emb=MEMB, hub=MHUB, r_in=150.0, r_out=290.0,
                            label_w=_lw, banner=(8, 8, 270, 44), what="the %s map" % KINDS[_k])
    MLAY.append([_l0 if _z == 1.0 else SMAP.shard_scaled(_l0, _z, "the %s map" % KINDS[_k]) for _z in MZOOMS])
MBOX = [SMAP.edge_boxes(MLAY[_k][0]) for _k in range(NK)]
# edge e of kind k lights when ITS FAR island is yours (the bridge to it): edges are in island order (one per island)
assert all([int(_e[1][3]) for _e in MLAY[_k][0]["edges"]] == list(range(len(LAD[_k]))) for _k in range(NK)), "0.4.9: one bridge line per island, in island order"
# ---- the pictures (pure Python, our own geometry - nothing vanilla-derived): island states per shard colour, halos, emblem, hubs, lines, pips
MAP_ASSETS = {}                 # jar path -> bytes (pictures + page data)
MPATHS = {}                     # picture name -> markup path


def map_ship(name, pic):
    data = SMAP.png(pic)
    w_, h_ = SMAP.png_size(data)
    assert w_ % 2 == 0 and h_ % 2 == 0 and "_" not in name, name
    jp = MJAR + MDIR + name + "@2x.png"
    assert jp not in MAP_ASSETS, name
    MAP_ASSETS[jp] = data
    MPATHS[name] = MDIR + name + ".png"
    SUI.register_map_textures([MPATHS[name]])
    return MPATHS[name]


for _st in ("Locked", "Open", "Ready"):
    map_ship("Node/" + _st, SMAP.node_picture(2 * MNODE, _st.lower()))
for _k in range(NK):
    for _s in (1, 2, 3):
        map_ship("Node/%sS%d" % (KCN[_k], _s), SMAP.node_picture(2 * MNODE, "learnt", KCOL[_k], (3, _s)))
    map_ship("Node/%sDone" % KCN[_k], SMAP.node_picture(2 * MNODE, "max", KCOL[_k], (3, 3)))
    map_ship("Hub" + KINDS[_k], SMAP.hub_picture(KCOL[_k], 2 * MHUB))
    map_ship("Base" + KINDS[_k], SMAP.base_picture(MLAY[_k][0]))
    for _e, _pic in sorted(SMAP.gold_pictures(MLAY[_k][0]).items()):
        map_ship("%sE%d" % (KINDS[_k], _e), _pic)
map_ship("Node/Own", SMAP.node_picture(2 * MNODE, "learnt", "#d6e4ee", (3, 2)))          # ui-data: the legend's neutral "yours" disc (a picture colour)
map_ship("Halo", SMAP.halo_picture(2 * MHALO))
map_ship("HubSel", SMAP.halo_picture(2 * MHUBH))
map_ship("Emblem", SMAP.emblem_picture(2 * MEMB))
MPIP_W, MPIP_H = 12, 14                 # one pip box (a 10 px disc), 14 high


def pip_picture(n, lit):
    """a strip of n pips @2x, `lit` of them gold (the skyymap pip colours)"""
    pic = SMAP.Pic(2 * MPIP_W * n, 2 * MPIP_H)
    for i in range(n):
        cx, cy = 2 * MPIP_W * i + MPIP_W, MPIP_H
        SMAP.disc(pic, cx, cy, 9.0, SMAP.rgb(SMAP.ART["disc"]), 1.0)
        SMAP.disc(pic, cx, cy, 6.5, SMAP.rgb(SMAP.ART["pipLit"]) if i < lit else SMAP.rgb(SMAP.ART["pipDim"]), 1.0)
    return pic


for _n in range(6):
    map_ship("Pip5L%d" % _n, pip_picture(5, _n))
for _n in (1, 2, 3):
    map_ship("Pip3L%d" % _n, pip_picture(3, _n))
# ---- the page data: kit node_map per shard + zoom, in keep form (kit 1.9): + the disc captions, the hub's click square + halo
MEL = {}
MNMS = {}
for _k in range(NK):
    for _zi, _z in enumerate(MZOOMS):
        _lz = MLAY[_k][_zi]
        _bx = MBOX[_k] if _z == 1.0 else SMAP.scaled_boxes(MBOX[_k], _z, _lz["W"], _lz["H"])
        _nm = SUI.node_map(MP, MP + "Cv", _lz, tex=lambda n: MPATHS[n], node_tex=lambda k, n: "Node/Locked",
                           node_icon=lambda k, n, _kk=_k: LAD[_kk][k]["prod"], hub_tex=lambda h, _kk=_k: "Hub" + KINDS[_kk],
                           hub_icon=lambda h, _kk=_k: SHARD_ITEMS[_kk], base_tex="Base" + KINDS[_k], edge_tex=lambda e, _kk=_k: "%sE%d" % (KINDS[_kk], e),
                           emblem_tex="Emblem", halo_tex="Halo", banner_texts=[(KINDS[_k] + " Shard", MOTTO[KINDS[_k]])], banner_cols=[KCOL[_k]], edge_boxes=_bx)
        _hz = int(round(MHALO * _z))
        for _i, _nd in enumerate(_nm.nodes):      # the kit's halo is 44 px (a 32 px disc): ours rings a 40 px disc
            _n = _lz["nodes"][_i]
            _nd["k_halo"] = (int(round(_n["cx"] - _hz / 2.0)), int(round(_n["cy"] - _hz / 2.0)), _hz, _hz)
        for _i, _b in enumerate(_lz["labels"]):
            _nm.static.append(("#" + MP + "Cv", SUI.label(MP + "Cp%d" % _i, "", "caption", size=13, w=_b[2], h=_b[3], align="Center",
                                                          anchor={"left": _b[0], "top": _b[1]})))
            _nm.sets.append(("#%sCp%d.Text" % (MP, _i), MCAP[_k][_i]))
        _hs = int(round(MHUBH * _z))
        _cx, _cy = _lz["W"] / 2.0, _lz["H"] / 2.0
        _nm.static.append(("#" + MP + "Cv", SUI.map_pic(MP + "HubSel", int(round(_cx - _hs / 2.0)), int(round(_cy - _hs / 2.0)), _hs, _hs, MPATHS["HubSel"])))
        _nm.static.append(("#" + MP + "Cv", SUI.map_hit(MP + "HubB", _lz["emb_l"], _lz["emb_t"], _lz["emb"])))   # click the centre = the shard view
        MAP_ASSETS[MRES + "K%dZ%dK.txt" % (_k, _zi)] = _nm.keep_text().encode("utf-8")
        MEL[(_k, _zi)] = _nm.keep_elements()
        MNMS[(_k, _zi)] = _nm
for _p in sorted(MAP_ASSETS):
    assert "_" not in _p.split("/")[-1], _p
print("0.4.9 shard maps: %s islands, %d px discs, %d pictures + %d page data files, %d KB; keep map elements (zoom 100 / 150 / 200 %%) %s" % (
    "/".join(str(len(LAD[_k])) for _k in range(NK)), MNODE, sum(1 for p_ in MAP_ASSETS if p_.endswith(".png")),
    sum(1 for p_ in MAP_ASSETS if p_.startswith(MRES)), sum(len(v_) for v_ in MAP_ASSETS.values()) // 1024,
    [max(MEL[(_k, _zi)] for _k in range(NK)) for _zi in range(len(MZOOMS))]))

# ---- the Map tab markup: rail | map | panel (3 views). Every runtime text is a "slot" (ShPage.mTx / mCol); a slot whose colour can change
# on a click is a holder of colour VARIANTS (one shows: .Visible), so the in-place update never rebuilds (kit 1.9 keep mode)
ROWNAME = SUI.COLOR["rowName"]
KP_ST = [GOOD, BAD, INFO]               # the status line's variants (base2 below draws them)
KP = {"name": [ROWNAME, GOLD], "line": [TEXT, GOOD, BAD, GOLD, WARN], "req": [GOOD, BAD, TEXT]}
MSLOT = []                      # (name, [ids], palette key or None)
MBTN = []                       # (name, id, action)
MPIP = []                       # (name, [ids], first index)


def mslot(a, parent, name, kind="default", size=14, h=20, w=316, pal="line", bold=None, wrap=None, align=None, col0=None):
    """one runtime text: palette None = one label coloured by J(this.mCol[i]) at build time; else a holder of its colour variants"""
    idx = len(MSLOT)
    sid = MP + name
    if pal is None:
        a.append((parent, SUI.label(sid, "", kind, size=size, h=h, w=w, bold=bold, wrap=wrap, align=align, col=J_("this.mCol[%d]" % idx, col0 or TEXT))))
        MSLOT.append((name, [sid], None, w, size, bool(bold) or kind == "bold", bool(wrap)))
        return idx
    a.append((parent, SUI.group(sid + "H", None, w=w, h=h)))
    ids = []
    for vi, vc in enumerate(KP[pal]):
        a.append(("#" + sid + "H", SUI.label(sid + "%d" % vi, "", kind, size=size, h=h, w=w, bold=bold, wrap=wrap, align=align, col=vc,
                                            anchor={"left": 0, "top": 0})))
        ids.append(sid + "%d" % vi)
    MSLOT.append((name, ids, pal, w, size, bool(bold) or kind == "bold", bool(wrap)))
    return idx


def mbtn(a, parent, name, text, act, w=110, h=None, size="small", top=0):
    """a button in a fixed holder (its place stays when it is hidden: ShPage.mOn[i] -> .Visible); bound to `act` in every build"""
    bid = MP + name
    hh = h or (SUI.BTN_SMALL_H if size == "small" else SUI.BTN_H)
    a.append((parent, SUI.group(bid + "H", None, w=w, h=hh, anchor={"top": top} if top else None)))
    a.append(("#" + bid + "H", SUI.keep_at0(SUI.button(bid, text, "secondary", size, w=w))))
    MBTN.append((name, bid, act))
    return len(MBTN) - 1


def mpips(a, parent, name, n, levels, w, h=22, top=4):
    """a pip strip: one pre-placed picture per level (ShPage.mPip[i] picks one: .Visible)"""
    hid = MP + name
    a.append((parent, SUI.group(hid, None, w=w, h=h)))
    ids = []
    for lv_ in levels:
        pid = hid + "L%d" % lv_
        a.append(("#" + hid, SUI.map_pic(pid, 0, top, MPIP_W * n, MPIP_H, MPATHS["Pip%dL%d" % (n, lv_)])))
        ids.append(pid)
    MPIP.append((name, ids, levels[0]))
    return len(MPIP) - 1


MPIN = SUI.MAP_PANEL_W - 2 * SUI.WELL_PAD           # 440 inside the right panel
MCOL_W = MPIN - 8 - 8 - 8 - 110                     # 306: a row's text column (8 pad, 8 gap, 110 button, 8 pad)
MA_PANEL = SUI.Appends()
_pn = MP + "Pn"
MA_PANEL.append(("#" + MP + "Row", SUI.panel(_pn, "well", w=SUI.MAP_PANEL_W, h=CH)))
_zr, _zk = SUI.map_zoom_row(MP, MPIN)
MA_PANEL.append(("#" + _pn, _zr))
for _p, _m in _zk:
    MA_PANEL.append((_p, _m))
MA_PANEL.append(("#" + _pn, SUI.spacer(h=6)))
MA_PANEL.append(("#" + _pn, SUI.separator("content", w=MPIN, anchor={"top": 2, "bottom": 4})))
MVH = CH - 2 * SUI.WELL_PAD - SUI.BTN_SMALL_H - 6 - 7 - 8
MA_PANEL.append(("#" + _pn, SUI.group(MP + "V", None, w=MPIN, h=MVH)))
MVIEW = [MP + "V0", MP + "V1", MP + "V2"]
for _v in MVIEW:
    MA_PANEL.append(("#" + MP + "V", SUI.group(_v, "Top", w=MPIN, h=MVH, anchor={"left": 0, "top": 0})))
# view 0 = THE SHARD (click the centre): the head, the 5 shard-wide upgrades, the bench note
_v = "#" + MP + "V0"
MA_PANEL.append((_v, SUI.group(MP + "V0Hd", "Left", w=MPIN, h=48)))
MA_PANEL.append(("#" + MP + "V0Hd", SUI.item_icon(MP + "V0Ic", J_("this.shardItem", SHARD_ITEM), size=40, anchor={"top": 4})))
MA_PANEL.append(("#" + MP + "V0Hd", SUI.spacer(w=10)))
MA_PANEL.append(("#" + MP + "V0Hd", SUI.group(MP + "V0HdT", "Top", w=MPIN - 50, h=48)))
mslot(MA_PANEL, "#" + MP + "V0HdT", "V0Nm", "bold", 18, 26, MPIN - 50, None, col0=KCOL[FARM_K])
mslot(MA_PANEL, "#" + MP + "V0HdT", "V0Sb", "default", 15, 22, MPIN - 50, "line")
MA_PANEL.append((_v, SUI.spacer(h=6)))
MROWH = 92
MUPS = [("Auto", "Buy", "iauto"), ("Store", "Upgrade", "buy"), ("Comp", "Upgrade", "cmpbuy"), ("Time", "Upgrade", "tcbuy"), ("Off", "Upgrade", "offbuy")]
for _r, (_nm_, _bt, _ac) in enumerate(MUPS):
    _rid = MP + "R" + _nm_
    MA_PANEL.append((_v, SUI.group(_rid, "Left", w=MPIN, h=MROWH, bg="row")))
    MA_PANEL.append(("#" + _rid, SUI.spacer(w=8)))
    MA_PANEL.append(("#" + _rid, SUI.group(_rid + "T", "Top", w=MCOL_W, h=MROWH)))
    MA_PANEL.append(("#" + _rid + "T", SUI.spacer(h=4)))
    mslot(MA_PANEL, "#" + _rid + "T", "R%sN" % _nm_, "bold", 15, 22, MCOL_W, "name")
    mslot(MA_PANEL, "#" + _rid + "T", "R%sA" % _nm_, "default", 14, 20, MCOL_W, "line")
    mslot(MA_PANEL, "#" + _rid + "T", "R%sC" % _nm_, "default", 14, 20, MCOL_W, "req")
    mslot(MA_PANEL, "#" + _rid + "T", "R%sI" % _nm_, "default", 14, 20, MCOL_W, "req")
    MA_PANEL.append(("#" + _rid, SUI.spacer(w=8)))
    mbtn(MA_PANEL, "#" + _rid, "B" + _nm_, _bt, _ac, top=(MROWH - SUI.BTN_SMALL_H) // 2)
    MA_PANEL.append((_v, SUI.spacer(h=4)))
# fix (critic: Skyy "the overall shard upgrades and modifiers"): the Totem modifiers of this shard, read-only (placed / in your bag) + its Bench tier
mslot(MA_PANEL, _v, "V0Md", "bold", 15, 22, MPIN, "name")
mslot(MA_PANEL, _v, "V0Nt", "caption", 13, 60, MPIN, None, wrap=True)
_V0H = 48 + 6 + len(MUPS) * (MROWH + 4) + 22 + 60
assert _V0H <= MVH, ("the shard view is too tall", _V0H, MVH)
# view 1 = AN ISLAND OF YOURS: the head, Size (pips + Grow), the 3 sub-upgrades (5 pips each), the seed store
_v = "#" + MP + "V1"
mslot(MA_PANEL, _v, "V1Nm", "bold", 18, 26, MPIN, "name")
mslot(MA_PANEL, _v, "V1Sb", "default", 15, 22, MPIN, "line")
mslot(MA_PANEL, _v, "V1Ot", "default", 14, 20, MPIN, "line")
MA_PANEL.append((_v, SUI.spacer(h=6)))
MROWH1 = 112
for _r, (_nm_, _pn_, _bt, _ac) in enumerate((("Sz", 3, "Grow", "grow"), ("U0", 5, "Upgrade", "isub0"), ("U1", 5, "Upgrade", "isub1"), ("U2", 5, "Upgrade", "isub2"))):
    _rid = MP + "R" + _nm_
    MA_PANEL.append((_v, SUI.group(_rid, "Left", w=MPIN, h=MROWH1, bg="row")))
    MA_PANEL.append(("#" + _rid, SUI.spacer(w=8)))
    MA_PANEL.append(("#" + _rid, SUI.group(_rid + "T", "Top", w=MCOL_W, h=MROWH1)))
    MA_PANEL.append(("#" + _rid + "T", SUI.spacer(h=4)))
    MA_PANEL.append(("#" + _rid + "T", SUI.group(_rid + "L", "Left", w=MCOL_W, h=22)))
    mslot(MA_PANEL, "#" + _rid + "L", "R%sN" % _nm_, "bold", 15, 22, MCOL_W - 8 - MPIP_W * _pn_ - 4, "name")
    MA_PANEL.append(("#" + _rid + "L", SUI.spacer(w=8)))
    mpips(MA_PANEL, "#" + _rid + "L", "P" + _nm_, _pn_, list(range(1, 4)) if _pn_ == 3 else list(range(6)), MPIP_W * _pn_ + 4)
    mslot(MA_PANEL, "#" + _rid + "T", "R%sA" % _nm_, "default", 14, 20, MCOL_W, "line")
    mslot(MA_PANEL, "#" + _rid + "T", "R%sC" % _nm_, "default", 14, 20, MCOL_W, "req")
    mslot(MA_PANEL, "#" + _rid + "T", "R%sI" % _nm_, "default", 14, 20, MCOL_W, "req")
    mslot(MA_PANEL, "#" + _rid + "T", "R%sJ" % _nm_, "default", 14, 20, MCOL_W, "req")
    MA_PANEL.append(("#" + _rid, SUI.spacer(w=8)))
    mbtn(MA_PANEL, "#" + _rid, "B" + _nm_, _bt, _ac, top=(MROWH1 - SUI.BTN_SMALL_H) // 2)
    MA_PANEL.append((_v, SUI.spacer(h=6)))
mslot(MA_PANEL, _v, "SdA", "default", 14, 20, MPIN, "line")
MA_PANEL.append((_v, SUI.group(MP + "SdB", "Left", w=MPIN, h=SUI.BTN_SMALL_H)))
mbtn(MA_PANEL, "#" + MP + "SdB", "BSd", "Give seeds", "iseed", w=150)
MA_PANEL.append(("#" + MP + "SdB", SUI.spacer(w=8)))
mbtn(MA_PANEL, "#" + MP + "SdB", "BSdB", "Take seeds", "iseedb", w=150)
# view 2 = AN ISLAND TO BUY: the head, what it makes, the cost (a requirement list), the tier-order gate, Buy island
_v = "#" + MP + "V2"
mslot(MA_PANEL, _v, "V2Nm", "bold", 18, 26, MPIN, "name")
mslot(MA_PANEL, _v, "V2Sb", "default", 15, 22, MPIN, "line")
MA_PANEL.append((_v, SUI.spacer(h=6)))
mslot(MA_PANEL, _v, "V2A", "default", 14, 40, MPIN, None, wrap=True)
MA_PANEL.append((_v, SUI.spacer(h=6)))
MA_PANEL.append((_v, SUI.label(MP + "V2Ct", "Cost", "section", h=24)))
for _i in range(4):
    mslot(MA_PANEL, _v, "V2R%d" % _i, "default", 14, 22, MPIN, "req")
MA_PANEL.append((_v, SUI.spacer(h=6)))
mslot(MA_PANEL, _v, "V2G", "default", 14, 40, MPIN, "line", wrap=True)
MA_PANEL.append((_v, SUI.spacer(h=10)))
mbtn(MA_PANEL, _v, "BBuy", "Buy island", "ibuy", w=200, size="normal")
MS = dict((_n[0], _i) for _i, _n in enumerate(MSLOT))
MB = dict((_n[0], _i) for _i, _n in enumerate(MBTN))
MPI = dict((_n[0], _i) for _i, _n in enumerate(MPIP))
for _vid in MVIEW:
    _u = SUI.used_height(MA_PANEL, _vid)
    assert _u <= MVH, "0.4.9: the panel view %s holds %d of %d px" % (_vid, _u, MVH)
# ---- the rail: one row per shard (selected = this one), the hint, the legend
MA_RAIL0 = SUI.Appends([(BODY, SUI.group(MP + "Row", "Left", w=MROW_W, h=CH)), ("#" + MP + "Row", SUI.group(MP + "Rail", "Top", w=SUI.MAP_RAIL_W, h=CH))])
MA_RK = {}                      # (kind, selected) -> Appends
for _k in range(NK):
    for _sel in (False, True):
        _rid = MP + "Rk%d" % _k
        _a = SUI.Appends([("#" + MP + "Rail", SUI.map_rail_row(_rid, "tree", _sel))])
        for _p, _m in SUI.map_rail_parts(_rid, "tree", icon=SHARD_ITEMS[_k], col=KCOL[_k]):
            if ("#%sS {" % _rid) in _m:          # the sub line: its colour comes from the page (red = locked)
                _m = SUI.label(_rid + "S", "", "rowSub", size=SUI.MAP_CAP_SIZE, h=20, w=SUI.MAP_RAIL_W - 50, col=J_("this.railCol[%d]" % _k, SUI.COLOR["rowSub"]))
            _a.append((_p, _m))
        _a.sets.append((_rid + "N", "Text", KINDS[_k] + " Shard"))
        MA_RK[(_k, _sel)] = _a
MHINT_H = 64
MLEGEND = [("Node/Own", "yours - S / M / L pips"), ("Node/%sDone" % KCN[FARM_K], "complete - all maxed"), ("Node/Ready", "can buy now"),
           ("Node/Open", "next - need more"), ("Node/Locked", "locked - tier order"), ("Halo", "selected")]
MRAIL_SP = CH - NK * SUI.MAP_TREE_ROW_H - 8 - MHINT_H - len(MLEGEND) * SUI.MAP_LEGEND_ROW_H
assert MRAIL_SP >= 0, MRAIL_SP
MA_RAIL1 = SUI.Appends()
MA_RAIL1.append(("#" + MP + "Rail", SUI.spacer(h=8)))
MA_RAIL1.append(("#" + MP + "Rail", SUI.label(MP + "Hint", "", "caption", size=15, h=MHINT_H, w=SUI.MAP_RAIL_W - 16, wrap=True, anchor={"left": 8})))
MA_RAIL1.append(("#" + MP + "Rail", SUI.spacer(h=MRAIL_SP)))
for _lrow, _kids in SUI.map_legend(MP, [(MPATHS[t_], c_) for t_, c_ in MLEGEND]):
    MA_RAIL1.append(("#" + MP + "Rail", _lrow))
    for _p, _m in _kids:
        MA_RAIL1.append((_p, _m))
for _t, _c in MLEGEND:
    assert SUI.text_width(_c, SUI.MAP_CAP_SIZE) <= SUI.MAP_RAIL_W - 26, _c
MA_RAIL1.append(("#" + MP + "Row", SUI.spacer(w=SUI.MAP_GAP)))
# ---- the map: the canvas at 100 %, the 2-axis scroll box above (kit map_scroll, probe M7)
MA_MAP = {}
for _zi in range(len(MZOOMS)):
    if _zi == 0:
        MA_MAP[_zi] = SUI.Appends([("#" + MP + "Row", "Group #%sCv { Anchor: (Width: %d, Height: %d); Background: %s; }" % (MP, MW, MH, SUI.COLOR["well"]))])
    else:
        _a_, _b_, _c_ = SUI.map_scroll(MP + "Out", MP + "In", MP + "Cv", MW, MH, MLAY[FARM_K][_zi]["W"], MLAY[FARM_K][_zi]["H"])
        MA_MAP[_zi] = SUI.Appends([("#" + MP + "Row", _a_), ("#" + MP + "Out", _b_), ("#" + MP + "In", _c_)])
    assert all(MLAY[_k][_zi]["W"] == MLAY[FARM_K][_zi]["W"] and MLAY[_k][_zi]["H"] == MLAY[FARM_K][_zi]["H"] for _k in range(NK))
MA_MAP2 = SUI.Appends([("#" + MP + "Row", SUI.spacer(w=SUI.MAP_GAP))])


def map_preview(kd, zi=0, sel=None, v=0):
    """every (parent, markup) the Map tab draws for shard kd at zoom zi (the Python mirror of buildFull's map part): checks + previews"""
    a = SUI.Appends(MA_RAIL0)
    for k2 in range(NK):
        a.extend(MA_RK[(k2, k2 == kd)])
    a.extend(MA_RAIL1)
    a.extend(MA_MAP[zi])
    for p_, m_ in MNMS[(kd, zi)].keep_markups(sel=sel):
        a.append((p_, m_))
    a.extend(MA_MAP2)
    a.extend(MA_PANEL)
    return a


# ---- the Java: kSets = every slot's text on each of its variants + the variant / button / pip / view shown; the rail + strip + zoom texts
KSET = []
for _i, (_n, _ids, _pal) in enumerate(s_[:3] for s_ in MSLOT):
    for _id in _ids:
        KSET.append('b.set("#%s.Text", this.mTx[%d]);' % (_id, _i))
    if _pal is not None:
        KSET.append(SUI.java_show([x_ for x_ in _ids], "kci(this.mCol[%d], @PKG@.ShPage.KP_%s)" % (_i, _pal.upper())))
for _i, (_n, _bid, _ac) in enumerate(MBTN):
    KSET.append('b.set("#%s.Visible", this.mOn[%d]);' % (_bid, _i))
for _i, (_n, _ids, _l0) in enumerate(MPIP):
    KSET.append(SUI.java_show(_ids, "this.mPip[%d] - %d" % (_i, _l0)))
KSET.append(SUI.java_show(MVIEW, "this.mV"))
for _k in range(NK):
    KSET.append('b.set("#%sRk%dS.Text", this.railSub[%d]);' % (MP, _k, _k))
KSET.append('b.set("#%sHint.Text", this.mHint);' % MP)
KSET.append('b.set("#%sZmL.Text", @PKG@.ShMap.ZPCT[this.kZ] + " %%");' % MP)
KSET.append('b.set("#%sHubSel.Visible", this.mview == 0);' % MP)
for _id, _ex in ((P + "Sum1", "this.sum1"), (P + "Sum2", "this.sum2"), (P + "Sto1", "this.sto1"), (P + "Sto2", "this.sto2"), (P + "Title", "this.title")):
    KSET.append('b.set("#%s.Text", %s);' % (_id, _ex))
KSET.append("stSets(b);")
STSET = ['b.set("#%sStatus%d.Text", this.stText);' % (P, _i) for _i in range(len(KP_ST))] + [SUI.java_show([P + "Status%d" % _i for _i in range(len(KP_ST))], "kci(this.stCol, @PKG@.ShPage.KP_ST)")]
MAP_BINDS = ['  ev.addEventBinding(@BT@.Activating, "#%s", @EVD@.of("a", "%s"));' % (_bid, _ac) for _n, _bid, _ac in MBTN]
MAP_BINDS += ['  ev.addEventBinding(@BT@.Activating, "#%sRk%d", @EVD@.of("a", "mk%d"));' % (MP, _k, _k) for _k in range(NK)]
MAP_BINDS += ['  ev.addEventBinding(@BT@.Activating, "#%sZmO", @EVD@.of("a", "mzo"));' % MP, '  ev.addEventBinding(@BT@.Activating, "#%sZmI", @EVD@.of("a", "mzi"));' % MP,
              '  ev.addEventBinding(@BT@.Activating, "#%sHubB", @EVD@.of("a", "mhub"));' % MP]
MAP_JAVA = "\n".join(
    [MA_RAIL0.java("b")]
    + ["  if (this.kind == %d) {\n%s\n  } else {\n%s\n  }" % (_k, MA_RK[(_k, True)].java("b"), MA_RK[(_k, False)].java("b")) for _k in range(NK)]
    + [MA_RAIL1.java("b"), "  if (mz == 0) {", MA_MAP[0].java("b"), "  } else if (mz == 1) {", MA_MAP[1].java("b"), "  } else {", MA_MAP[2].java("b"), "  }",
       "  Object[] alts = @PKG@.ShMap.mapAlloc(@PKG@.ShMap.cand(this.mTex, @PKG@.ShMap.CPIC[this.kind]), @PKG@.ShMap.budget(mz));",
       "  this.kst = @PKG@.ShMap.mapKeepNew(this.mTex.length, this.mLit.length);",
       '  this.mapEls = @PKG@.ShMap.mapDrawK(b, ev, @PKG@.ShMap.linesK(this.kind, mz), "#%sCv", this.mLit, this.mTex, alts, this.mview == 1 ? this.sel : -1, "mn", this.kst);' % MP,
       MA_MAP2.java("b"), MA_PANEL.java("b")] + MAP_BINDS
    + ["  this.kZ = mz;", "  this.kKind = this.kind;", "  this.kSigD = kSig();", "  kSets(b);"])
print("0.4.9 Map tab: rail %d + map %d x %d + panel %d (views %d px: %s); %d text slots (%d variant labels), %d buttons, %d pip strips; %d keep sets" % (
    SUI.MAP_RAIL_W, MW, MH, SUI.MAP_PANEL_W, MVH, "/".join(str(SUI.used_height(MA_PANEL, v_)) for v_ in MVIEW), len(MSLOT),
    sum(len(s_[1]) for s_ in MSLOT if s_[2]), len(MBTN), len(MPIP), len(KSET)))

'''

NEW_MENU = (HEAD_NEW + STRIP_NEW + r'''# --- tabs (0.4.9: Map | Totems | Collect - the Upgrades + Islands tabs are the Map now; internal tab numbers 1 = Map, 3 = Totems, 0 = Collect,
# so every 0.4.x click keeps its action; tab 2 (the old Islands tab) shows the Map)
TABS = ["Map", "Totems", "Collect"]
TAB_NUM = [1, 3, 0]
NTAB = len(TABS)
TAB_IDS = [P + "Tab%d" % i for i in TAB_NUM]


def sub_row(parent, row_id, ids, names, sel):
    """0.4.2 (Menu-Pattern 3.6): a window's ONE tab row in the 32 px sub-tab style - small buttons SUB_TAB_W wide, 5 apart, left aligned,
    the active one Primary (the vanilla kit buttons: the decorated window has no sky theme). Same ids as the 0.4 tab_row (same bindings)."""
    SUI.assert_sub_tabs_fit(names, room=IW)
    a_ = SUI.Appends([(parent, SUI.group(row_id, layout="Left", h=SUI.SUB_TAB_H, anchor={"top": SUI.TAB_MARGIN, "bottom": SUI.TAB_MARGIN}))])
    for i_, (tid, nm) in enumerate(zip(ids, names)):
        if i_:
            a_.append(("#" + row_id, SUI.spacer(w=SUI.SUB_TAB_GAP)))
        a_.append(("#" + row_id, SUI.button(tid, nm, "primary" if i_ == sel else "secondary", "small", w=SUI.SUB_TAB_W)))
    return a_


for _ti, t in enumerate(TAB_NUM):
    a = seg("tabs%d" % t)
    a.extend(sub_row(BODY, P + "Tabs", TAB_IDS, TABS, _ti))
TAB_H = SUI.SUB_TAB_H + 2 * SUI.TAB_MARGIN          # 0.4.2: the sub-tab row (was the 44 px tab_row)
CH = IH - STRIP_H - TAB_H - 34 - 50
assert CH == 688, CH
base2 = SUI.Appends()          # after the tab content: status + footer (always)
LW, RW = 1000, IW - 1000 - 14          # 0.4.9: the Collect / Totems panels in the wider window
assert RW == 552


def panel_pair(a, tag, pre=None):
    pre = pre or P
    a.append((("#" + pre + "Body") if pre != P else BODY, SUI.group(pre + tag, layout="Left", w=IW, h=CH)))
    a.append(("#" + pre + tag, SUI.panel(pre + tag + "L", "simple", w=LW, h=CH, layout="Top", pad=12)))
    a.append(("#" + pre + tag, SUI.spacer(w=14)))
    a.append(("#" + pre + tag, SUI.panel(pre + tag + "R", "simple", w=RW, h=CH, layout="Top", pad=12)))
    return "#" + pre + tag + "L", "#" + pre + tag + "R"


ROWW = LW - 24
''' + COLLECT_OLD + TOTEMS_NEW + MAP_BLOCK + FOOT_NEW + r'''# the page check: every element of every segment together (ids unique, parents exist, kit-proven markup)
for a_ in list(SEG.values()) + [base2, base3]:
    ALL.extend(a_)
# 0.4.9: the windows checked one coherent variant each: Map (every shard, zoom 100 % and 200 %), Totems (owner / empty / co-op), Collect
# (owner / co-op / grown rows / empty)
VARIANTS = []


def _menu(tseg):
    v = SUI.Appends(sh.appends)
    v.extend(SEG["enter"])
    v.extend(SEG[tseg])
    return v


def _foot(v, pick="pick"):
    v.extend(base2)
    v.extend(SEG[pick])
    v.extend(base3)
    return v


MAP_VARIANTS = []
for _k in range(NK):
    for _zi in (0, len(MZOOMS) - 1):
        v = _menu("tabs1")
        v.extend(map_preview(_k, _zi, sel=0))
        VARIANTS.append(_foot(v))
        MAP_VARIANTS.append((_k, _zi, VARIANTS[-1]))
v = _menu("tabs0")
for k_ in ["c0"] + ["crow%d_0" % i for i in range(SLOTS)] + ["c1", "c1b"]:
    v.extend(SEG[k_])
VARIANTS.append(_foot(v))
v = _menu("tabs3")
v.extend(SEG["t0"])
for i in range(5):
    v.extend(SEG["trow%d" % i])
v.extend(SEG["t0b"])
for i in range(4):
    v.extend(SEG["prow%d" % i])
v.extend(SEG["tside"]); v.extend(SEG["tdbtn"])
VARIANTS.append(_foot(v, "pickrec"))
# the co-op variants (no Collect buttons, no place rows / totem buttons, no Pick up) + the empty Totems tab
v = _menu("tabs0"); v.extend(SEG["c0"])
for i in range(SLOTS):
    v.extend(SEG["crowv%d_0" % i])
v.extend(SEG["c1"]); VARIANTS.append(_foot(v, "nopick"))
for k_ in range(1, len(CHS)):          # 0.4.2: the grown Collect rows (owner + co-op), the empty list
    for _vo in (False, True):
        v = _menu("tabs0"); v.extend(SEG["c0"])
        for i in range(SLOTS):
            v.extend(SEG[("crowv%d_%d" if _vo else "crow%d_%d") % (i, k_)])
        v.extend(SEG["c1"]); v.extend(SEG["c1b"]); VARIANTS.append(_foot(v))
v = _menu("tabs0"); v.extend(SEG["c0"]); v.extend(SEG["cempty"]); v.extend(SEG["c1"]); VARIANTS.append(_foot(v))
v = _menu("tabs3"); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"]); v.extend(SEG["pcoop"]); v.extend(SEG["tside"]); VARIANTS.append(_foot(v, "nopick"))
v = _menu("tabs3"); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"]); v.extend(SEG["pempty"]); v.extend(SEG["tside"]); VARIANTS.append(_foot(v))
for v in VARIANTS:
    v.check(P)
# the element guard (kit 1.8: a map page <= MAP_MAX_ELEMENTS): the worst Map tab (every edge drawn, every variant) + room for the pre-placed
# pictures of the keep update (mapAlloc's budget per zoom)
MSTATIC = max(sum(SUI._strip_quoted(SUI.render(mk_ if isinstance(mk_, str) else mk_.a)).count("{") for p_, mk_ in v_) - MNMS[(k_, z_)].keep_elements()
              for k_, z_, v_ in MAP_VARIANTS)
MBUD = [SUI.MAP_MAX_ELEMENTS - MSTATIC - max(MEL[(_k, _zi)] for _k in range(NK)) - 6 for _zi in range(len(MZOOMS))]
assert min(MBUD) >= 3 * max(len(LAD[_k]) for _k in range(NK)), "0.4.9: room for 3 pre-placed pictures a disc: %s" % MBUD
print("0.4.9 Map tab: %d elements without the map, keep maps %s, pre-placed picture budget %s (guard %d)" % (
    MSTATIC, [max(MEL[(_k, _zi)] for _k in range(NK)) for _zi in range(len(MZOOMS))], MBUD, SUI.MAP_MAX_ELEMENTS))


def jseg(name):
    return SEG[name].java("b")


def binds(ids_vals):
    return "\n".join('  ev.addEventBinding(@BT@.Activating, "#%s", @EVD@.of("a", "%s"));' % (i, v) for i, v in ids_vals)


BUILD_JAVA = "\n".join([
    sh.java("b"),          # 0.4: the shell WITH its title b.set (0.1-0.3.2 emitted sh.appends only - a blank title bar)
    jseg("enter"), binds([(P + "Enter", "enter")]),
    "  if (this.tab == 1) {", jseg("tabs1"), "  } else if (this.tab == 3) {", jseg("tabs3"), "  } else {", jseg("tabs0"), "  }",
    binds([(TAB_IDS[i], "tab%d" % TAB_NUM[i]) for i in range(NTAB)]),
    "  if (this.tab == 0) {", jseg("c0"),
    "    if (this.cN == 0) {", jseg("cempty"), "    }",
    "    int growC = growSize(this.cN, %d, new int[] { %s }, 4);" % (CLIST_H, ", ".join(str(x) for x in CHS)),          # 0.4.2: rule 7
] + ["    if (growC == %d) {\n%s\n    }" % (k_, "\n".join("    if (this.cN > %d && this.manage) {\n%s\n%s\n    } else if (this.cN > %d) {\n%s\n    }" % (
    i, jseg("crow%d_%d" % (i, k_)), binds([(P + "CRow%dBtn" % i, "col%d" % i)]), i, jseg("crowv%d_%d" % (i, k_))) for i in range(SLOTS)))
     for k_ in range(len(CHS))] + [
    jseg("c1"), "    if (this.manage) {", jseg("c1b"), binds([(P + "CAll", "colall")]), "    }",
    "  } else if (this.tab == 3) {", jseg("t0"),
    "    if (this.tN == 0) {", jseg("tempty"), "    }",
] + ["    if (this.tN > %d) {\n%s\n%s\n    }" % (i, jseg("trow%d" % i), binds([(P + "TRow%dBtn" % i, "tsel%d" % i)])) for i in range(5)] + [
    jseg("t0b"),
    "    if (!this.mine) {", jseg("pcoop"), "    } else if (this.pN == 0) {", jseg("pempty"), "    }",
] + ["    if (this.mine && this.pN > %d) {\n%s\n%s\n    }" % (i, jseg("prow%d" % i), binds([(P + "PRow%dBtn" % i, "tplace%d" % i)])) for i in range(4)] + [
    jseg("tside"), "    if (this.dHas && this.mine) {", jseg("tdbtn"), binds(TD_BINDS), tup_bind(P + "TUp"), "    }",
    "  } else {",
    "  int mz = this.zoom < 0 ? 0 : (this.zoom >= @PKG@.ShMap.ZN ? @PKG@.ShMap.ZN - 1 : this.zoom);",   # 0.4.9: THE MAP TAB
    MAP_JAVA,
    "  }",
    base2.java("b"),
    "  stSets(b);",
    "  if (this.mine && this.lostKind >= 0) {", jseg("pickrec"), binds([(P + "Pick", "pick"), (P + "Rec", "reclaim")]),
    "  } else if (this.mine) {", jseg("pick"), binds([(P + "Pick", "pick")]), "  } else {", jseg("nopick"), "  }",
    base3.java("b"), binds([(P + "Close", "close")]),
])
MENU_W, MENU_H, MENU_CH = PW, PH, CH
# 0.4.9: the bench (view 4) keeps the 0.4.8 window (1100 x 860) and its panel sizes - the names it reads are set back here
PW, PH = 1100, 860
IW, IH = 1066, 788
CH = IH - STRIP_H - TAB_H - 34 - 50
LW, RW = 700, IW - 700 - 14
ROWW = LW - 24
assert (CH, RW) == (568, 352), (CH, RW)

''')
P.rep(OLD_MENU, NEW_MENU)

P.rep('''print("shard pages: menu %d segments + bench %d segments, %d variants checked, menu %d x %d (content %d px), exit 640 x 340, totem 660 x 700, bench %d x %d"
      % (len(SEG), len(BSEG), len(VARIANTS), PW, PH, CH, PW, PH))''',
      '''print("shard pages: menu %d segments + bench %d segments, %d variants checked, menu %d x %d (content %d px), exit 640 x 340, totem 660 x 700, bench %d x %d"
      % (len(SEG), len(BSEG), len(VARIANTS), MENU_W, MENU_H, MENU_CH, PW, PH))''')

# ================================================================================================ ShMap: the map tables + the kit's drawer / keep update
P.rep('''# ================= ShPage (0.4: four views - 0 the shard's menu from its portal, 1 the hub stand = exit, 3 a totem's own page, 4 a bench) =================
page = mk("ShPage", T["PAGE"])''', r'''# ================= 0.4.9 ShMap: the Map tab's tables (per shard: islands, lines, picture colour) + the kit 1.8 / 1.9 node map drawer and keep
# update (tools/skyyui.py java_node_map_methods / java_node_map_keep_methods, the SkyyRebirth 0.5.1 way) =================
smap = mk("ShMap")
for f in ("public static final String RES = %s;" % jlit(MRES), "public static final int ZN = %d;" % len(MZOOMS),
          "public static final int[] ZPCT = new int[] { %s };" % ", ".join(str(int(round(z_ * 100))) for z_ in MZOOMS),
          "public static final int[] BUD = new int[] { %s };" % ", ".join(str(b_) for b_ in MBUD),
          "public static final int[] NN = new int[] { %s };" % ", ".join(str(len(LAD[_k])) for _k in range(NK)),
          "public static final String[] CPIC = new String[] { %s };" % ", ".join(jlit(c_) for c_ in KCN),
          "public static final String[] KCOL = new String[] { %s };" % ", ".join(jlit(c_) for c_ in KCOL),
          "public static final java.lang.Object[] LINESK = new java.lang.Object[%d];" % (NK * len(MZOOMS)),
          "public static final java.util.concurrent.atomic.AtomicLong READS = new java.util.concurrent.atomic.AtomicLong();"):
    F(smap, f)
for _m in SUI.java_node_map_methods(dict((k_, T[k_]) for k_ in ("UCB", "UEB", "BT", "EVD"))):
    M(smap, _m)
for _m in SUI.java_node_map_keep_methods(dict((k_, T[k_]) for k_ in ("UCB", "UEB", "BT", "EVD"))):
    M(smap, _m)
M(smap, r"""
public static synchronized String[] linesK(int kd, int z) {
  int k = kd < 0 ? 0 : (kd >= NN.length ? NN.length - 1 : kd);
  int zz = z < 0 ? 0 : (z >= ZN ? ZN - 1 : z);
  Object o = LINESK[k * ZN + zz];
  if (o == null) { o = mapRead(@PKG@.ShMap.class.getClassLoader(), RES + "K" + k + "Z" + zz + "K.txt"); LINESK[k * ZN + zz] = o; READS.incrementAndGet(); }
  return (String[]) o;
}""")
M(smap, r"""
public static int budget(int z) {
  return z < 0 || z >= BUD.length ? 0 : BUD[z];
}""")
# the pictures a click can bring an island to, most likely first: a bought island -> yours Small; a grow -> the next size; maxed -> complete;
# the next island's affordability (gold ring <-> light ring); a locked island becomes the next one after a buy
M(smap, r"""
public static Object[] cand(String[] tex, String cp) {
  int n = tex == null ? 0 : tex.length;
  Object[] out = new Object[n];
  for (int i = 0; i < n; i++) {
    String c = tex[i];
    String[] a = new String[0];
    if (c == null) a = new String[0];
    else if (c.equals(cp + "S1")) a = new String[] { cp + "S2" };
    else if (c.equals(cp + "S2")) a = new String[] { cp + "S3" };
    else if (c.equals(cp + "S3")) a = new String[] { cp + "Done" };
    else if (c.equals("Ready")) a = new String[] { cp + "S1", "Open" };
    else if (c.equals("Open")) a = new String[] { "Ready", cp + "S1" };
    else if (c.equals("Locked")) a = new String[] { "Ready", "Open" };
    out[i] = mapCand(c, a);
  }
  return out;
}""")

# ================= ShPage (0.4: four views - 0 the shard's menu from its portal, 1 the hub stand = exit, 3 a totem's own page, 4 a bench) =================
page = mk("ShPage", T["PAGE"])''')

# ================================================================================================ ShPage: fields, the map fill, kSets / kSig, the keep update
P.rep('''          "public int bTab;", "public String bIcon;", "public String bTitle;", "public String bSub;", "public String bSubC;", "public String bCap;", "public String bCap2;",''',
      '''          "public int bTab;", "public String bIcon;", "public String bTitle;", "public String bSub;", "public String bSubC;", "public String bCap;", "public String bCap2;",
          # 0.4.9 THE MAP TAB: the view (0 shard / 1 island), the zoom, every slot's text + colour, the buttons, the pips, the panel view, the island
          # pictures + lit lines, the rail lines; the keep state (kit 1.9) + what it was drawn with; the harness counters
          "public int mview;", "public int zoom;", "public String[] mTx;", "public String[] mCol;", "public boolean[] mOn;", "public int[] mPip;", "public int mV;",
          "public String[] mTex;", "public boolean[] mLit;", "public String[] railSub;", "public String[] railCol;", "public String mHint;", "public String wnNow;",
          "public Object[] kst;", "public int kZ;", "public int kKind;", "public String kSigD;", "public int keeps;", "public int kFalls;", "public int mapEls;",
          "public Object kLast;",''')
P.rep('''              " this.rSel = 0; this.rN = 0; this.title = \\"\\";")''', '''              " this.rSel = 0; this.rN = 0; this.title = \\"\\"; this.tab = 1; this.mview = 0; this.zoom = 0; this.kZ = -1; this.kKind = -1;")   # 0.4.9: the menu opens on the Map''')

_PAL = "\n".join('F(page, "public static final String[] KP_%s = new String[] { %%s };" %% ", ".join(jlit(c_) for c_ in KP[%r]))' % (k_.upper(), k_) for k_ in ("line", "name", "req"))
FILLMAP = r'''# 0.4.9 THE MAP TAB TEXTS (spec 6; Style Guide 15 colours: green = what helps / you have it, red = what you still need, gold = maxed). The
# slot numbers come from the markup (MS / MB / MPI); every value the fill reads is the 0.4.8 menu's (the same rules, the same costs).
''' + _PAL + '''
F(page, "public static final String[] KP_ST = new String[] { %s };" % ", ".join(jlit(c_) for c_ in KP_ST))
F(page, "public static final String[] DECO_TXT = new String[] { %s };" % ", ".join(jlit(x_) for st_ in ("farm", "grove", "orchard", "mine", "ranch", "arena")
                                                                                     for x_ in DECO_TXT49[st_]))
F(page, "public static final String[] STYLES = new String[] { \\"farm\\", \\"grove\\", \\"orchard\\", \\"mine\\", \\"ranch\\", \\"arena\\" };")
# the slot table (name, width, font size, bold, wrap): the harness measures every runtime text against its own label
F(page, "public static final String[] SLOT_NAME = new String[] { %s };" % ", ".join(jlit(s_[0]) for s_ in MSLOT))
F(page, "public static final int[] SLOT_W = new int[] { %s };" % ", ".join(str(s_[3]) for s_ in MSLOT))
F(page, "public static final int[] SLOT_SIZE = new int[] { %s };" % ", ".join(str(s_[4]) for s_ in MSLOT))
F(page, "public static final int[] SLOT_FLAGS = new int[] { %s };" % ", ".join(str((1 if s_[5] else 0) + (2 if s_[6] else 0)) for s_ in MSLOT))
M(page, r"""
public static int kci(String c, String[] cols) {
  if (c == null || cols == null) return 0;
  for (int i = 0; i < cols.length; i++) if (cols[i].equalsIgnoreCase(c)) return i;
  return 0;
}""")
M(page, r"""
public static String decoTxt(int kd, int lvl) {
  String st = @PKG@.ShIsl.STYLE[kd];
  int s = -1;
  for (int i = 0; i < STYLES.length; i++) if (STYLES[i].equals(st)) s = i;
  if (s < 0 || lvl < 1 || lvl > 5) return "";
  return DECO_TXT[s * 5 + lvl - 1];
}""")
M(page, r"""
public void mapInit() {
  int ns = @NS@;
  this.mTx = new String[ns]; this.mCol = new String[ns];
  for (int i = 0; i < ns; i++) { this.mTx[i] = ""; this.mCol[i] = "@TEXT@"; }
  this.mOn = new boolean[@NB@];
  this.mPip = new int[@NP@];
  this.mPip[0] = 1;
  int kd = @PKG@.ShKind.ok(this.kind) ? this.kind : @PKG@.ShKind.FARM;
  int nn = @PKG@.ShMap.NN[kd];
  this.mTex = new String[nn];
  for (int i = 0; i < nn; i++) this.mTex[i] = "Locked";
  this.mLit = new boolean[nn];
  this.railSub = new String[@PKG@.ShKind.N]; this.railCol = new String[@PKG@.ShKind.N];
  for (int i = 0; i < @PKG@.ShKind.N; i++) { this.railSub[i] = ""; this.railCol[i] = "@RSUB@"; }
  this.mV = 0;
  this.mHint = "Click the shard in the middle for its own upgrades, an island for its upgrades - or the next island to buy it.";
}""".replace("@NS@", str(len(MSLOT))).replace("@NB@", str(len(MBTN))).replace("@NP@", str(len(MPIP))).replace("@TEXT@", TEXT).replace("@RSUB@", SUI.COLOR["rowSub"]))
# a requirement row (Menu-Pattern rule 9: one requirement a line, green = you have it, red = you still need it); a long one says "(have N)"
M(page, r"""
public void reqLine(int s, long have, long need, String what) {
  if (s < 0 || s >= this.mTx.length) return;
  String h = have < 0L ? "?" : @PKG@.ShCfg.num(have);
  String t = @PKG@.ShCfg.num(need) + " " + what + " (you have " + h + ")";
  if (t.length() > 38) t = @PKG@.ShCfg.num(need) + " " + what + " (have " + h + ")";
  this.mTx[s] = t;
  this.mCol[s] = (have < 0L || have >= need) ? "@GOOD@" : "@BAD@";
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD))
# an item's short name on the Map panel (the shard's own long ids read better turned round; else the 0.4.x pretty name)
M(page, r"""
public static String nameOf(String id) {
  if (id == null) return "";
  if (id.equals("Plant_Spores_Mushroom_Eternal")) return "Eternal Mushroom Spores";
  return @PKG@.ShTotem.pretty(id);
}""")
# a material list into up to two requirement rows (a third item is named on the second row); -> true when you have every item
M(page, r"""
public boolean reqMats(Object[] m, @IC@[] cs, int s1, int s2) {
  String[] ids = (String[]) m[0];
  long[] q = (long[]) m[1];
  boolean all = true;
  for (int i = 0; i < ids.length; i++) {
    long h = cs == null ? -1L : @PKG@.ShInv.count(cs, ids[i]);
    if (h >= 0L && h < q[i]) all = false;
    int s = i == 0 ? s1 : (i == 1 ? s2 : -1);
    if (s >= 0) reqLine(s, h, q[i], nameOf(ids[i]));
  }
  if (ids.length > 2 && s2 >= 0) this.mTx[s2] = this.mTx[s2] + " + " + (ids.length - 2) + " more";
  return all;
}""")
M(page, r"""
public static String hrs(double h) {
  return @PKG@.ShCfg.dec(h) + " h";
}""")
# the rail: each shard's line (the CLICKING player's level for its lock; the bridge asked outside the store lock) - no change to any file
M(page, r"""
public void fillRail(java.util.Properties p) {
  String wn = this.wnNow;
  for (int k2 = 0; k2 < @PKG@.ShKind.N; k2++) {
    int need = k2 < @PKG@.ShCfg.LOCK.length ? @PKG@.ShCfg.LOCK[k2] : 0;
    int lv = (need > 0 || this.me != null) ? @PKG@.ShIsl.level(this.me, k2) : -1;
    boolean own = false;
    int n = 0;
    String placed = "";
    if (p != null) {
      @PKG@.ShStore.LOCK.lock();
      try {
        own = @PKG@.ShMath.owned(k2, p);
        for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) if (@PKG@.ShMath.hasIsland(k2, p, s)) n++;
        placed = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(k2, "placed"));
      } finally { @PKG@.ShStore.LOCK.unlock(); }
    }
    boolean here = wn != null && placed.startsWith(wn + "|");
    this.railCol[k2] = "@RSUB@";
    if (need > 0 && lv >= 0 && lv < need) { this.railSub[k2] = "Locked - " + @PKG@.ShIsl.skillWord(k2) + " " + need; this.railCol[k2] = "@BAD@"; }
    else if (!own) this.railSub[k2] = "No shard yet";
    else if (!here) this.railSub[k2] = n + (n == 1 ? " island - portal elsewhere" : " islands - portal elsewhere");
    else this.railSub[k2] = (lv >= 0 ? @PKG@.ShIsl.skillWord(k2) + " " + lv + " - " : "") + n + (n == 1 ? " island" : " islands");
  }
}""".replace("@RSUB@", SUI.COLOR["rowSub"]).replace("@BAD@", BAD))
# the Map tab of shard kd (under the ShStore lock, settled already; tcv / acv / ocv = the coin curve the costs need, asked outside the lock)
M(page, r"""
public void fillMap(java.util.Properties p, @IC@[] cs, long now, long purse, double[] tcv, double acv, double[] ocv, boolean ownedNow, int lockNeed, int lockLv) {
  int kd = this.kind;
  String nm = @PKG@.ShKind.NAMES[kd];
  String upg = @PKG@.ShKind.UPG[kd];
  boolean act = this.mine && !this.locked && ownedNow;
  int nn = @PKG@.ShIsl.LADN[kd];
  int nx = @PKG@.ShIsl.nextTier(kd, p);
  boolean au = @PKG@.ShIsl.auto(kd, p);
  String cp = @PKG@.ShMap.CPIC[kd];
  // ---- the islands: pictures + lit lines (+ the next island's price: gold ring = you can buy it now)
  int islands = 0; int large = 0; double rate = 0.0;
  for (int i = 0; i < nn; i++) {
    int t = @PKG@.ShIsl.LAD0[kd] + i;
    int sl = @PKG@.ShIsl.slotOf(kd, p, t);
    if (sl >= 0) {
      islands++;
      int sz = @PKG@.ShMath.size(kd, p, sl);
      if (sz >= 3) large++;
      rate += @PKG@.ShMath.rate(kd, p, sl, now);
      boolean done = sz >= 3 && @PKG@.ShIsl.sub(p, kd, sl, 0) >= 5 && @PKG@.ShIsl.sub(p, kd, sl, 1) >= 5 && @PKG@.ShIsl.sub(p, kd, sl, 2) >= 5;
      this.mTex[i] = cp + (done ? "Done" : "S" + (sz < 1 ? 1 : (sz > 3 ? 3 : sz)));
    } else if (i == nx && ownedNow) {
      long bc = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[i]);
      Object[] bm = @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
      boolean items = true;
      String[] bi = (String[]) bm[0]; long[] bq = (long[]) bm[1];
      for (int j = 0; j < bi.length; j++) if (cs == null || @PKG@.ShInv.count(cs, bi[j]) < bq[j]) items = false;
      this.mTex[i] = ((purse < 0L || purse >= bc) && items) ? "Ready" : "Open";
    } else this.mTex[i] = "Locked";
  }
  for (int e = 0; e < this.mLit.length; e++) this.mLit[e] = @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + e) >= 0;   // line e = the bridge to island e
  // ---- view 0: THE SHARD
  this.mTx[@@V0Nm@@] = nm + " Shard"; this.mCol[@@V0Nm@@] = @PKG@.ShMap.KCOL[kd];
  if (this.locked) { this.mTx[@@V0Sb@@] = "Locked - reach " + @PKG@.ShIsl.skillWord(kd) + " " + lockNeed + " (you: " + lockLv + ")"; this.mCol[@@V0Sb@@] = "@BAD@"; }
  else if (!ownedNow) { this.mTx[@@V0Sb@@] = "No " + nm + " Shard yet - its door is on your starter islands"; this.mCol[@@V0Sb@@] = "@TEXT@"; }
  else { this.mTx[@@V0Sb@@] = islands + (islands == 1 ? " island - " : " islands - ") + large + " at Large - " + perHour(rate) + " items / hour"; this.mCol[@@V0Sb@@] = "@TEXT@"; }
  // Automation (once per shard, spec 7)
  this.mTx[@@RAutoN@@] = "Automation";
  if (!ownedNow) { this.mTx[@@RAutoA@@] = "Comes with the shard's first island"; }
  else if (au) { this.mCol[@@RAutoN@@] = "@GOLD@"; this.mTx[@@RAutoA@@] = "Automated - every island works by itself"; this.mCol[@@RAutoA@@] = "@GOOD@"; }
  else {
    long ac = @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(@PKG@.ShCfg.AUTO_STEP), acv);
    Object[] am = @PKG@.ShIsl.mats(kd, @PKG@.ShIsl.LAD0[kd], @PKG@.ShCfg.AUTO_ITEMS[kd], 0, 1L);
    this.mTx[@@RAutoA@@] = "Manual now (" + @PKG@.ShCfg.MAN_PCT + " %) - next: 100 % + replanting";
    this.mCol[@@RAutoA@@] = "@WARN@";
    reqLine(@@RAutoC@@, purse, ac, "coins");
    reqMats(am, cs, @@RAutoI@@, -1);
    this.mOn[@@BAuto@@] = act;
  }
  // Storage II-V
  int tier = @PKG@.ShMath.storageTier(kd, p);
  long cap = @PKG@.ShMath.cap(kd, p);
  long hu = @PKG@.ShInv.count(cs, upg);
  this.mTx[@@RStoreN@@] = "Storage " + @PKG@.ShTotem.ROMAN[tier < 1 ? 0 : (tier > 5 ? 4 : tier - 1)] + " of V";
  if (tier >= 5) { this.mCol[@@RStoreN@@] = "@GOLD@"; this.mTx[@@RStoreA@@] = "Fully upgraded - " + @PKG@.ShCfg.num(cap) + " a new island"; this.mCol[@@RStoreA@@] = "@GOLD@"; }
  else {
    long nc = @PKG@.ShCfg.storeCoins(tier + 1);
    long ne = (long) @PKG@.ShCfg.storeEnch(tier + 1);
    this.mTx[@@RStoreA@@] = "Now " + @PKG@.ShCfg.num(cap) + " -> next " + @PKG@.ShCfg.num(100L * (long) @PKG@.ShCfg.stacks(tier + 1)) + " a new island";
    this.mCol[@@RStoreA@@] = "@GOOD@";
    reqLine(@@RStoreC@@, purse, nc, "coins");
    if (ne > 0L) reqLine(@@RStoreI@@, cs == null ? -1L : hu, ne, @PKG@.ShTotem.pretty(upg));
    this.mOn[@@BStore@@] = act;
  }
  // Auto-Compactor I-II
  int cm = @PKG@.ShMath.compactor(kd, p);
  String en0 = @PKG@.ShKind.ENCH[kd];
  String en1 = @PKG@.ShKind.SMELT_ENCH[kd];
  boolean form = en0.length() > 0 || en1.length() > 0;
  this.mTx[@@RCompN@@] = "Auto-Compactor " + cm + " of 2";
  if (!form) this.mTx[@@RCompA@@] = "Nothing here has an Enchanted form yet";
  else if (cm >= 2) { this.mCol[@@RCompN@@] = "@GOLD@"; this.mTx[@@RCompA@@] = "Fully upgraded (+" + @PKG@.ShCfg.CMP_STORE + " % storage)"; this.mCol[@@RCompA@@] = "@GOLD@"; }
  else {
    long cc = @PKG@.ShCfg.CMP_COINS[cm + 1];
    long ci = (long) @PKG@.ShCfg.CMP_ITEMS[cm + 1];
    if (cm == 0 && en0.length() == 0) { this.mTx[@@RCompA@@] = "Next: Compactor I - needs an Auto-Smelt Pole"; this.mCol[@@RCompA@@] = "@WARN@"; }
    else if (cm == 0) { this.mTx[@@RCompA@@] = "Next: 1 " + @PKG@.ShTotem.pretty(en0) + " for every 100"; this.mCol[@@RCompA@@] = "@GOOD@"; }
    else { this.mTx[@@RCompA@@] = "Next: II - +" + @PKG@.ShCfg.CMP_STORE + " % storage an island"; this.mCol[@@RCompA@@] = "@GOOD@"; }
    reqLine(@@RCompC@@, purse, cc, "coins");
    if (ci > 0L) reqLine(@@RCompI@@, cs == null ? -1L : hu, ci, @PKG@.ShTotem.pretty(upg));
    this.mOn[@@BComp@@] = act;
  }
  // Time Compressor I-III
  int tc = @PKG@.ShMath.compressor(kd, p);
  this.mTx[@@RTimeN@@] = "Time Compressor " + tc + " of 3";
  if (tc >= 3) { this.mCol[@@RTimeN@@] = "@GOLD@"; this.mTx[@@RTimeA@@] = "Fully upgraded - x" + @PKG@.ShCfg.dec(@PKG@.ShTotem.tcMult(kd, p)) + " as fast"; this.mCol[@@RTimeA@@] = "@GOLD@"; }
  else {
    long tcc = @PKG@.ShCfg.TC_COINS[tc + 1];
    long tv = (long) @PKG@.ShCfg.TC_VOID[tc + 1];
    this.mTx[@@RTimeA@@] = "Now x" + @PKG@.ShCfg.dec(@PKG@.ShTotem.tcMult(kd, p)) + " -> next x" + @PKG@.ShCfg.dec(@PKG@.ShCfg.TC_MULT[tc + 1]) + " as fast";
    this.mCol[@@RTimeA@@] = "@GOOD@";
    reqLine(@@RTimeC@@, purse, tcc, "coins");
    if (tv > 0L) reqLine(@@RTimeI@@, cs == null ? -1L : @PKG@.ShInv.count(cs, "Ingredient_Void_Essence"), tv, "Void Essence");
    this.mOn[@@BTime@@] = act;
  }
  // Offline Harvest 0-5 (0.4.9)
  int ol = @PKG@.ShIsl.offLv(kd, p);
  double cap0 = (double) @PKG@.ShCfg.MAX_OFF_SEC / 3600.0;
  double oh = @PKG@.ShIsl.offH(ol); if (oh > cap0) oh = cap0;
  this.mTx[@@ROffN@@] = "Offline Harvest " + ol + " of 5";
  if (ol >= 5) { this.mCol[@@ROffN@@] = "@GOLD@"; this.mTx[@@ROffA@@] = "Harvests " + hrs(oh) + " while nobody visits"; this.mCol[@@ROffA@@] = "@GOLD@"; }
  else {
    double nh = @PKG@.ShIsl.offH(ol + 1); if (nh > cap0) nh = cap0;
    long oc = @PKG@.ShCore.offCoins(ol, ocv[ol < 0 ? 0 : (ol > 4 ? 4 : ol)]);
    long oq = @PKG@.ShCore.offEnch(ol);
    this.mTx[@@ROffA@@] = (au || !ownedNow ? "Harvests " + hrs(oh) : "Manual: " + hrs((double) @PKG@.ShCfg.MAN_OFF_SEC / 3600.0) + " (Automation: " + hrs(oh) + ")") + " -> next " + hrs(nh);
    this.mCol[@@ROffA@@] = "@GOOD@";
    if (ownedNow && !au) { this.mTx[@@ROffC@@] = "Buy Automation first"; this.mCol[@@ROffC@@] = "@BAD@"; }   // fix: before Automation a level changes nothing
    else {
      reqLine(@@ROffC@@, purse, oc, "coins");
      if (oq > 0L) reqLine(@@ROffI@@, cs == null ? -1L : hu, oq, @PKG@.ShTotem.pretty(upg));
      this.mOn[@@BOff@@] = act;
    }
  }
  // Totem modifiers (read-only here: crafted + tiered at the bench, added on a totem's page)
  int bt = ownedNow ? @PKG@.ShCore.benchTier(kd, p, now) : 1;
  this.mTx[@@V0Md@@] = "Totem modifiers - Totem Bench " + @PKG@.ShTotem.ROMAN[bt < 1 ? 0 : (bt > 4 ? 3 : bt - 1)] + " of IV";
  StringBuilder mdb = new StringBuilder();
  long bag = 0L;
  for (int mi = 0; mi < @PKG@.ShTotem.MOD_KEYS.length; mi++) {
    int pl = 0;
    for (int i = 0; i < nn; i++) { int sl2 = @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + i); if (sl2 >= 0) pl += @PKG@.ShTotem.modsOnIsland(kd, p, sl2, @PKG@.ShTotem.MOD_KEYS[mi]); }
    if (cs != null) bag += @PKG@.ShInv.count(cs, @PKG@.ShTotem.MOD_ITEMS[mi]);
    if (pl > 0) { if (mdb.length() > 0) mdb.append(", "); mdb.append(@PKG@.ShTotem.MOD_NAMES[mi]).append(" x").append(pl); }
  }
  String mds = mdb.length() == 0 ? "None on your totems yet" : "On your totems: " + mdb.toString();
  if (bag > 0L) mds = mds + " - " + @PKG@.ShCfg.num(bag) + " more in your bag";
  this.mTx[@@V0Nt@@] = mds + ". Craft them and tier up totems at the Totem Bench on the hub island; add one on a totem's page.";
  this.mCol[@@V0Nt@@] = "@CAP@";
  // ---- view 1 / 2: the selected island (yours) or the island to buy
  int s = this.sel < 0 || this.sel >= nn ? 0 : this.sel;
  int ts = @PKG@.ShIsl.LAD0[kd] + s;
  int sl = @PKG@.ShIsl.slotOf(kd, p, ts);
  this.mV = this.mview != 1 ? 0 : (sl >= 0 ? 1 : 2);
  if (sl >= 0) {
    int sz = @PKG@.ShMath.size(kd, p, sl);
    int a0 = @PKG@.ShIsl.sub(p, kd, sl, 0); int d0 = @PKG@.ShIsl.sub(p, kd, sl, 1); int i0 = @PKG@.ShIsl.sub(p, kd, sl, 2);
    boolean all5 = a0 >= 5 && d0 >= 5 && i0 >= 5;
    boolean done = sz >= 3 && all5;
    double r = @PKG@.ShMath.rate(kd, p, sl, now);
    double mu = @PKG@.ShIsl.mult(kd, p, sl, sz);
    this.mTx[@@V1Nm@@] = @PKG@.ShIsl.tname(ts) + " Island"; this.mCol[@@V1Nm@@] = done ? "@GOLD@" : "@ROWNAME@";
    this.mTx[@@V1Sb@@] = sizeName(sz) + " - " + (au ? "Automated" : "Manual phase (" + @PKG@.ShCfg.MAN_PCT + " %)");
    this.mCol[@@V1Sb@@] = au ? "@GOOD@" : "@WARN@";
    this.mTx[@@V1Ot@@] = "Makes " + perHour(r) + " / hour - " + @PKG@.ShMath.totems(kd, p, sl) + " of " + @PKG@.ShMath.pads(sz) + " pads - +" + @PKG@.ShCfg.dec((mu - 1.0) * 100.0) + " % from upgrades";
    // size + Grow
    this.mTx[@@RSzN@@] = "Size: " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small"));
    this.mCol[@@RSzN@@] = sz >= 3 ? "@GOLD@" : "@ROWNAME@";
    this.mPip[@@PSz@@] = sz < 1 ? 1 : (sz > 3 ? 3 : sz);
    if (done) { this.mTx[@@RSzA@@] = "Island complete - every upgrade maxed"; this.mCol[@@RSzA@@] = "@GOLD@"; }
    else if (sz >= 3) { this.mTx[@@RSzA@@] = "Largest size - max the 3 upgrades below"; }
    else if (!all5) { this.mTx[@@RSzA@@] = "Grow: max the 3 below first (" + a0 + "/5, " + d0 + "/5, " + i0 + "/5)"; this.mCol[@@RSzA@@] = "@BAD@"; }
    else {
      long gc = @PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), tcv[s]);
      Object[] gm = @PKG@.ShIsl.mats(kd, ts, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L);
      this.mTx[@@RSzA@@] = "Grow to " + (sz == 1 ? "Medium" : "Large") + " - the 3 restart, gains kept";
      this.mCol[@@RSzA@@] = "@GOOD@";
      reqLine(@@RSzC@@, purse, gc, "coins");
      reqMats(gm, cs, @@RSzI@@, @@RSzJ@@);
      this.mOn[@@BSz@@] = this.mine && !this.locked;
    }
    // the 3 sub-upgrades
    int[] rn = new int[] { @@RU0N@@, @@RU1N@@, @@RU2N@@ };
    int[] ra = new int[] { @@RU0A@@, @@RU1A@@, @@RU2A@@ };
    int[] rc = new int[] { @@RU0C@@, @@RU1C@@, @@RU2C@@ };
    int[] ri = new int[] { @@RU0I@@, @@RU1I@@, @@RU2I@@ };
    int[] rj = new int[] { @@RU0J@@, @@RU1J@@, @@RU2J@@ };
    int[] rb = new int[] { @@BU0@@, @@BU1@@, @@BU2@@ };
    int[] rp = new int[] { @@PU0@@, @@PU1@@, @@PU2@@ };
    String st = @PKG@.ShIsl.STYLE[kd];
    for (int w = 0; w < 3; w++) {
      int lv = @PKG@.ShIsl.sub(p, kd, sl, w);
      this.mTx[rn[w]] = @PKG@.ShIsl.subName(kd, w) + " " + lv + "/5";
      this.mCol[rn[w]] = lv >= 5 ? "@GOLD@" : "@ROWNAME@";
      this.mPip[rp[w]] = lv < 0 ? 0 : (lv > 5 ? 5 : lv);
      if (lv >= 5) { this.mTx[ra[w]] = sz >= 3 ? "Highest level" : "5/5 - grow the island to go on"; this.mCol[ra[w]] = "@GOLD@"; continue; }
      double pc = w == 0 ? @PKG@.ShCfg.AMT_BONUS : (w == 1 ? @PKG@.ShCfg.DECO_PCT : @PKG@.ShCfg.IRR_PCT);
      String ex = "";
      if (w == 0) {
        if (st.equals("farm") || st.equals("grove") || st.equals("orchard")) ex = " - " + @PKG@.ShIsl.pct(lv) + " -> " + @PKG@.ShIsl.pct(lv + 1) + " % of spots";
        else if (st.equals("mine")) ex = " - more ore in the cave";
        else if (st.equals("ranch")) ex = " - a bigger herd";
      } else if (w == 1) { String dt = decoTxt(kd, lv + 1); if (dt.length() > 0) ex = " - adds " + dt; }
      else ex = " - adds a water pool";
      this.mTx[ra[w]] = "Next: +" + @PKG@.ShCfg.dec(pc) + " % output" + ex;
      this.mCol[ra[w]] = "@GOOD@";
      long sc = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lv + 1), tcv[s]);
      String tm = w == 0 ? @PKG@.ShCfg.MAT_AMT : (w == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);
      Object[] sm = @PKG@.ShIsl.mats(kd, ts, tm, sz - 1, (long) (lv + 1));
      reqLine(rc[w], purse, sc, "coins");
      reqMats(sm, cs, ri[w], rj[w]);
      this.mOn[rb[w]] = this.mine && !this.locked;
    }
    // the seed store (manual phase, spec 7)
    boolean seedy = !au && ("farm".equals(st) || @PKG@.ShIsl.trees(kd)) && @PKG@.ShIsl.SEED[ts].length() > 0;
    if (seedy) {
      this.mTx[@@SdA@@] = "Seed store: " + @PKG@.ShIsl.seeds(kd, p, sl) + " " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.SEED[ts]) + ("farm".equals(st) ? " - " + @PKG@.ShIsl.eternal(kd, p, sl) + " Eternal cells" : "");
      this.mCol[@@SdA@@] = "@WARN@";
      this.mOn[@@BSd@@] = this.mine && !this.locked;
      this.mOn[@@BSdB@@] = this.mine && !this.locked;
    } else this.mTx[@@SdA@@] = au ? "Automated - nothing to replant" : ("mine".equals(st) ? "Ore regrows by itself" : "Nothing to replant here");
  } else {
    this.mTx[@@V2Nm@@] = @PKG@.ShIsl.tname(ts) + " Island";
    this.mTx[@@V2A@@] = "Makes " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[ts]) + ". It starts Small with its own 3 upgrades and appears at its place in the shard world.";
    long bc = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[s]);
    Object[] bm2 = @PKG@.ShIsl.mats(kd, ts, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
    reqLine(@@V2R0@@, purse, bc, "coins");
    String[] bi = (String[]) bm2[0];
    long[] bq = (long[]) bm2[1];
    int[] rr = new int[] { @@V2R1@@, @@V2R2@@, @@V2R3@@ };
    for (int j = 0; j < bi.length && j < 3; j++) reqLine(rr[j], cs == null ? -1L : @PKG@.ShInv.count(cs, bi[j]), bq[j], nameOf(bi[j]));
    if (!ownedNow) { this.mTx[@@V2Sb@@] = "No " + nm + " Shard yet"; this.mCol[@@V2Sb@@] = "@BAD@"; this.mTx[@@V2G@@] = "Its door is on your starter islands."; }
    else if (this.locked) { this.mTx[@@V2Sb@@] = "Not yours yet"; this.mTx[@@V2G@@] = "Locked - reach " + @PKG@.ShIsl.skillWord(kd) + " " + lockNeed + " to buy islands here."; this.mCol[@@V2G@@] = "@BAD@"; }
    else if (s != nx) {
      this.mTx[@@V2Sb@@] = "Not yours yet";
      this.mTx[@@V2G@@] = nx < 0 ? "Every island is yours." : "Buy the " + @PKG@.ShIsl.tname(@PKG@.ShIsl.LAD0[kd] + nx) + " island first - islands come in tier order.";
      this.mCol[@@V2G@@] = "@BAD@";
    } else {
      this.mTx[@@V2Sb@@] = "Next in line - you can buy it here"; this.mCol[@@V2Sb@@] = "@GOOD@";
      this.mTx[@@V2G@@] = this.mine ? "Buy island takes the items first, then the coins." : "Only the island owner buys islands.";
      this.mOn[@@BBuy@@] = this.mine;
    }
  }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@GOLD@", GOLD).replace("@WARN@", WARN).replace("@TEXT@", TEXT).replace("@ROWNAME@", ROWNAME).replace("@CAP@", SUI.COLOR["caption"]))
M(page, r"""
public String kSig() {
  StringBuilder s = new StringBuilder();
  s.append(this.kind).append('|').append(this.tab).append('|').append(this.zoom).append('|').append(this.mine).append('|').append(this.manage).append('|');
  s.append(this.locked).append('|').append(this.lostKind).append('|').append(this.sto2c).append('|').append(@PKG@.ShCfg.ON).append('|').append(this.view);
  if (this.railCol != null) { for (int i = 0; i < this.railCol.length; i++) s.append('|').append(this.railCol[i]); }
  return s.toString();
}""")
M(page, "public void stSets(@UCB@ b) {\\n" + "\\n".join("  " + l_ for l_ in "\\n".join(STSET).split("\\n")) + "\\n}")
M(page, "public void kSets(@UCB@ b) {\\n" + "\\n".join("  " + l_ for l_ in "\\n".join(KSET).split("\\n")) + "\\n}")
'''
FILLMAP = FILLMAP.replace('''M(page, r"""
public void fillMap(''', '''M(page, _r49(r"""
public void fillMap(''', 1)
assert FILLMAP.count('''.replace("@CAP@", SUI.COLOR["caption"]))''') == 1
FILLMAP = FILLMAP.replace('''.replace("@CAP@", SUI.COLOR["caption"]))''', '''.replace("@CAP@", SUI.COLOR["caption"])))''')
P.rep('''# every text of a shard's menu (view 0) for profile k (settles first; never writes). 0.3: of the open shard (this.kind)
M(page, r"""
public void fill(String k, @IC@[] cs) {''', '''# 0.4.9: the decoration words per style and level (what each Decorations level places, DECO48 - Skyy: "visual differences per lvl")
DECO_TXT49 = {"farm": ["flowers", "fences + lanterns", "hay + barrels", "crates + planters", "brick paving + pots"],
              "grove": ["ferns + mushrooms", "log stumps + crates", "barrels + bushes", "lanterns + torches", "planters + paving"],
              "orchard": ["flower beds", "fruit crates + buckets", "beehives + pots", "fences + lanterns", "planters + paving"],
              "mine": ["lanterns + torches", "rails + crates", "timber + barrels", "crystals + buckets", "big crystals + brick"],
              "ranch": ["hay + buckets", "paddock fences", "barrels + hay", "crates + lanterns", "brick yard + planters"],
              "arena": ["", "", "", "", ""]}
assert sorted(DECO_TXT49) == sorted(DECO48) and all(len(v_) == 5 for v_ in DECO_TXT49.values())


def _r49(src):
    """the Map tab's slot / button / pip numbers (MS / MB / MPI, from the markup) into the Java: @@Name@@ -> its index"""
    def one(m_):
        n_ = m_.group(1)
        v_ = MS.get(n_, MB.get(n_, MPI.get(n_)))
        assert v_ is not None, "0.4.9: unknown map slot @@%s@@" % n_
        return str(v_)
    out = re.sub(r"@@([A-Za-z0-9]+)@@", one, src)
    assert "@@" not in out
    return out


''' + FILLMAP + '''# every text of a shard's menu (view 0) for profile k (settles first; never writes). 0.3: of the open shard (this.kind)
M(page, r"""
public void fill(String k, @IC@[] cs) {''')

# ---- fill(): the map slots first (every return leaves them set), the rail + the offline costs' curve outside the lock, the map inside it
P.rep('''  this.title = nm + " Shard";
  this.shardItem = @PKG@.ShKind.SHARD[kd];
  this.prodItem = @PKG@.ShKind.PROD[kd];''', '''  this.title = nm + " Shard";
  this.shardItem = @PKG@.ShKind.SHARD[kd];
  this.prodItem = @PKG@.ShKind.PROD[kd];
  mapInit();   // 0.4.9: the Map tab's slots (every early return below leaves them filled)''')
P.rep('''  double acv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(@PKG@.ShCfg.AUTO_STEP));''', '''  double acv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(@PKG@.ShCfg.AUTO_STEP));
  double[] ocv = new double[5];   // 0.4.9: Offline Harvest's ladder steps (the bridge asked outside the lock)
  for (int oi = 0; oi < 5; oi++) ocv[oi] = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(@PKG@.ShCore.offStep(oi)));
  fillRail(p);   // 0.4.9: the rail (each shard's lock level via the bridge, outside the lock)''')
P.rep('''      this.iTx[8] = auTxt;
      this.iCol[8] = "@WARN@";
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }''', '''      this.iTx[8] = auTxt;
      this.iCol[8] = "@WARN@";
    }
    fillMap(p, cs, now, purse, tcv, acv, ocv, ownedNow, lockNeed, lockLv);   // 0.4.9: the Map tab (pictures, lines, the 3 panel views)
  } finally { @PKG@.ShStore.LOCK.unlock(); }''')

# ---- the Totems tab caption names the Map tab (the island picked there)
P.rep(''' items / min (pick the island on the Islands tab)";''', ''' items / min (pick the island on the Map tab)";''')
# ---- build(): the world name (the rail's "portal here?"), the old Islands tab number = the Map
P.rep('''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  String k = resolve(st);''', '''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.wnNow = worldName(st);   // 0.4.9
  String k = resolve(st);''')
# ---- 0.4.9 THE KEEP UPDATE (kit 1.9, the SkyyRebirth 0.5.1 way): the Map tab at 150 / 200 % still shown with the same shard + zoom, nothing
# structural changed (kSig) -> ONE sendUpdate (kSets + mapUpdK); false (nothing sent) = the caller rebuilds (one packet either way)
P.rep('''M(page, r"""
public static String jsonA(String data) {''', '''M(page, r"""
public boolean kUpd(@REF@ ref, @ST@ st) {
  if (!@PKG@.ShCfg.UI_KEEP || this.kst == null || this.view != 0 || this.tab != 1) return false;
  int z = this.zoom < 0 ? 0 : (this.zoom >= @PKG@.ShMap.ZN ? @PKG@.ShMap.ZN - 1 : this.zoom);
  if (z < 1 || z != this.kZ || this.kind != this.kKind) return false;
  this.wnNow = worldName(st);
  String k = resolve(st);
  if (k == null || !@PKG@.ShCfg.ON) return false;
  fill(k, invOf(ref, st));
  if (this.kSigD == null || !this.kSigD.equals(kSig())) return false;
  @UCB@ b = new @UCB@();
  kSets(b);
  if (!@PKG@.ShMap.mapUpdK(b, this.kst, this.mTex, this.mLit, this.mview == 1 ? this.sel : -1)) return false;
  if (this.testMode) { this.kLast = b; return true; }
  this.sendUpdate(b);
  return true;
}""")
M(page, r"""
public boolean kTry(@REF@ ref, @ST@ st) {
  try { return kUpd(ref, st); } catch (Throwable t) { @PKG@.ShCfg.warnOnce("kupd", "the shard map's in-place update failed - redrawing (logged once): " + t); return false; }
}""")
M(page, r"""
public static boolean keepable(String a) {
  return a.equals("mhub") || a.startsWith("mn") || a.equals("buy") || a.equals("cmpbuy") || a.equals("tcbuy") || a.equals("offbuy") || a.equals("iauto")
      || a.equals("ibuy") || a.startsWith("isub") || a.equals("grow") || a.equals("iseed") || a.equals("iseedb");
}""")
M(page, r"""
public boolean canSwitch(String k, int k2) {
  if (k == null || k2 < 0 || k2 >= @PKG@.ShKind.N || this.wnNow == null) return false;
  java.util.Properties p = @PKG@.ShStore.get(k);
  return p != null && @PKG@.ShStore.str(p, @PKG@.ShMath.kk(k2, "placed")).startsWith(this.wnNow + "|");
}""")
M(page, r"""
public static String jsonA(String data) {''')
# ---- the clicks: the map (centre / an island / zoom / another shard), Offline Harvest; tab 2 = the Map
P.rep('''  if (a.startsWith("tab")) { int t = a.length() > 3 ? (int) (a.charAt(3) - '0') : 0; if (t >= 0 && t <= 3) this.tab = t; return ""; }''',
      '''  if (a.startsWith("tab")) { int t = a.length() > 3 ? (int) (a.charAt(3) - '0') : 0; if (t == 2) t = 1; if (t >= 0 && t <= 3) this.tab = t; return ""; }   // 0.4.9: 1 = the Map
  if (a.equals("mhub")) { this.mview = 0; return ""; }   // 0.4.9: the centre = the shard view
  if (a.startsWith("mn")) {   // 0.4.9: an island of the map (its tier index)
    int n = -1;
    try { n = Integer.parseInt(a.substring(2)); } catch (Throwable x) { n = -1; }
    int kn = @PKG@.ShKind.ok(this.kind) ? this.kind : @PKG@.ShKind.FARM;
    if (n >= 0 && n < @PKG@.ShIsl.LADN[kn]) { this.sel = n; this.mview = 1; this.tpad = 0; }
    return "";
  }
  if (a.equals("mzo") || a.equals("mzi")) {   // 0.4.9: zoom 100 / 150 / 200 %
    int zz = this.zoom + (a.equals("mzi") ? 1 : -1);
    this.zoom = zz < 0 ? 0 : (zz >= @PKG@.ShMap.ZN ? @PKG@.ShMap.ZN - 1 : zz);
    return "";
  }''')
P.rep('''  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  int kd = this.kind;''', '''  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  int kd = this.kind;
  if (a.startsWith("mk") && this.view == 0) {   // 0.4.9: the rail - another shard whose portal stands on this island
    int n = -1;
    try { n = Integer.parseInt(a.substring(2)); } catch (Throwable x) { n = -1; }
    if (n < 0 || n >= @PKG@.ShKind.N) return "";
    if (n == kd) { this.mview = 0; return ""; }
    this.wnNow = worldName(st);
    if (!canSwitch(k, n)) return "-Open the " + @PKG@.ShKind.NAMES[n] + " Shard from its own portal on this island.";
    this.kind = n; this.sel = 0; this.mview = 0; this.tpad = 0; this.pickArm = 0L; this.recArm = 0L;
    return "";
  }''')
P.rep('''    if (a.equals("iauto")) return @PKG@.ShCore.buyAuto(u, k, kd, invOf(ref, st));   // 0.4.8''',
      '''    if (a.equals("iauto")) return @PKG@.ShCore.buyAuto(u, k, kd, invOf(ref, st));   // 0.4.8
    if (a.equals("offbuy")) return @PKG@.ShCore.buyOffline(u, k, kd, invOf(ref, st));   // 0.4.9: Offline Harvest''')
# ---- every click answers with ONE packet: the in-place update for a Map click at 150 / 200 %, else the rebuild (0.4.x)
P.rep('''  if (r != null && r.length() > 0) status(r);
  if (!this.testMode) {
    if ((a.equals("enter") || a.equals("back")) && r != null && r.startsWith("+")) { close(); return; }
    rebuild();
  }
}""")''', '''  if (r != null && r.length() > 0) status(r);
  if ((a.equals("enter") || a.equals("back")) && r != null && r.startsWith("+")) { if (!this.testMode) close(); return; }
  if (keepable(a) && kTry(ref, st)) { this.keeps = this.keeps + 1; return; }   // 0.4.9: the zoomed map keeps its place
  if (this.testMode && this.kst != null && @PKG@.ShCfg.UI_KEEP && keepable(a) && this.zoom > 0) this.kFalls = this.kFalls + 1;   // the harness's fall-back count
  if (!this.testMode) rebuild();
}""")''')

# ================================================================================================ the jar: the map pictures + page data, ShMap written
P.rep('''+ [admc, gfn, dfn, pl]   # 0.4.8: + ShMig048, ShIsl, ShDoor''', '''+ [admc, gfn, dfn, smap, pl]   # 0.4.9: + ShMig049, ShMap   # 0.4.8: + ShMig048, ShIsl, ShDoor''')
P.rep('''    for _p, _b in SHARD_GEN.items():    # 0.3: the other five portals' textures + icons
        _jz.writestr(_p, _b)''', '''    for _p, _b in SHARD_GEN.items():    # 0.3: the other five portals' textures + icons
        _jz.writestr(_p, _b)
    for _p, _b in sorted(MAP_ASSETS.items()):   # 0.4.9: the shard map pictures (our own geometry) + page data
        _jz.writestr(_p, _b)''')
P.rep('''print("assembled", jar, os.path.getsize(jar), "bytes (with the generated gold portal texture + the icon)")''',
      '''with zipfile.ZipFile(jar) as _jz:
    assert all(_jz.read(_p) == _b for _p, _b in MAP_ASSETS.items()), "0.4.9: the map files in the jar"
    assert all(_p.startswith(MJAR + MDIR) or _p.startswith(MRES) for _p in MAP_ASSETS), "0.4.9: map pictures under Common/UI/Custom/SkyyShards/Map/"
print("assembled", jar, os.path.getsize(jar), "bytes (with the generated gold portal texture + the icon)")''')
P.rep('''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.8: STARTER SHARD DOORS''',
      '''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.9: THE SHARD UPGRADE MAP (Map | Totems | Collect; the shard in the centre, an island per tier around it, zoom " + @PKG@.ShMap.ZPCT[0] + "-" + @PKG@.ShMap.ZPCT[@PKG@.ShMap.ZN - 1] + " %), +" + @PKG@.ShCfg.dec(@PKG@.ShCfg.AMT_BONUS) + " % a sub-upgrade level, Offline Harvest 0-5; 0.4.8: STARTER SHARD DOORS''')

# fix (critic): the Storage buy message names the base a NEW island holds (capOf = base x the island's upgrades since 0.4.9)
P.rep('''return "+Storage is now tier " + nt + ": " + @PKG@.ShCfg.num(@PKG@.ShMath.cap(kd, p)) + " items per island.";''',
      '''return "+Storage is now tier " + nt + ": " + @PKG@.ShCfg.num(@PKG@.ShMath.cap(kd, p)) + " items a new island (more with island upgrades).";''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_k = P.s.index
assert _k('smap = mk("ShMap")') < _k('page = mk("ShPage"') and _k("public void fillMap(") < _k("public void fill(String k") < _k("public boolean kUpd(") < _k("public String act(") < _k("public void handleDataEvent(")
P.finish()
