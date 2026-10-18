"""Derive SkyySacks/build_skyysacks_0.8.22.py from the SET pin 0.8.21 (the GENERATED build_skyysacks_0.8.21.py; edit THIS file, then
regenerate: python tools/sacks_0_8_22_patch.py; never re-run sacks_0_8_21_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.21 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_22_patch.py   then   python SkyySacks/build_skyysacks_0.8.22.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.22.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.22 (2026-10-17) = THE 15-STEP TIER LADDER in the /craft sort (round L1, tools/tier_tags.py TT_VERSION 2, built with SkyyGear 0.3.22 G1).
Skyy 2026-10-17 popup "tools follow ONE tier ladder of all 15 metals in zone order - Copper, Iron, Bronze, Thorium, Lead, Dusk, Cobalt,
Chromium, Azurvane, Adamantite, Slag, Cinder, Mithril, Titanium, Lumen - each one tier above the last (so the tier tags renumber, e.g. Thorium
becomes T4, Lumen T15)?" -> "Yes, full 15-step ladder (Recommended)".
  1. RecipeCmp's build-time copy of tools/tier_tags.py (TT_IDS / TT_TIER / TT_GRP / TT_RANK, LADDER, METAL_W / METAL_T) is re-baked from the
     TT_VERSION 2 table: every recipe list sorts on the 15-step ladder (T1 Copper .. T15 Lumen, T16 Onyxium), crop families grouped as before.
  2. The tier tag a recipe row shows next to its name keeps the WORD tools/tier_tags.py gives (tier_tags.word / metal_word) instead of the
     ladder noun at that number: TT_VERSION 2 puts Crude and Copper both at T1, so a Crude / Wood item says "T1 Crude" (as before) and not
     "T1 Copper"; Steel says "T2 Iron", Scrap "T1 Copper". New baked arrays TT_WORD (per table id) and METAL_WD (per metal word).
  No lang text, no saved data, no config change.
  ROLLBACK to 0.8.21: safe (sort order + the row tag numbers only).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.21.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.22.py"))
assert P.has('VERSION = "0.8.21"\n') and P.has("public static String tierText(String id) {") and P.has("ProcJob.sf"), "not the live generated SkyySacks 0.8.21"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.22 (2026-10-17)"):].rstrip() + "\n"

# ---- header, version
P.rep('''  ROLLBACK to 0.8.20: safe - older Sacks ignores q.<i>.sf / fu (the queued units smelt 1:1, only the extras are lost), the reads flag goes.
"""
''', '''  ROLLBACK to 0.8.20: safe - older Sacks ignores q.<i>.sf / fu (the queued units smelt 1:1, only the extras are lost), the reads flag goes.
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.21"\n', 'VERSION = "0.8.22"\n')

# ---- 1. the table: TT_VERSION 2 (asserted), + the words
P.rep('''assert all(1 <= _t <= len(TT.LADDER) for _t in TT_TIERS) and all('"' not in _i and "," not in _i for _i in TT_IDS)
''', '''assert all(1 <= _t <= len(TT.LADDER) for _t in TT_TIERS) and all('"' not in _i and "," not in _i for _i in TT_IDS)
# 0.8.22 (round L1): THE 15-step ladder (tools/tier_tags.py TT_VERSION 2) + the word each tag shows (Crude / Wood items "T1 Crude")
assert TT.TT_VERSION == "2" and TT.tier("Ingredient_Bar_Thorium") == 4 and len(TT.LADDER) == 16, "0.8.22: tools/tier_tags.py = the 15-step ladder"
TT_WORDS = [TT.word(_i) for _i in TT_IDS]
METAL_WDS = [TT.metal_word(_w) for _w, _t in TT.TOOL_METALS]
assert all(_w and '"' not in _w for _w in TT_WORDS + METAL_WDS), "0.8.22: every tagged id has a word"
assert dict(zip([_w for _w, _t in TT.TOOL_METALS], METAL_WDS))["Wood"] == "Crude" and TT.word("Ore_Lead_SkyWynn") == "Lead", "0.8.22: words"
''')
P.rep('''rcmp.addField(CtField.make("public static final int[] METAL_T = %s;" % _jia([_t for _w, _t in TT.TOOL_METALS]), rcmp))
''', '''rcmp.addField(CtField.make("public static final int[] METAL_T = %s;" % _jia([_t for _w, _t in TT.TOOL_METALS]), rcmp))
rcmp.addField(CtField.make("public static final String[] TT_WORD = %s;" % _jsa(TT_WORDS), rcmp))        # 0.8.22
rcmp.addField(CtField.make("public static final String[] METAL_WD = %s;" % _jsa(METAL_WDS), rcmp))      # 0.8.22
''')
# ---- 2. the row tag keeps the table's word
P.rep('''public static String tierText(String id) {
  if (id == null) return "";
  int st = suffixTier(id);
  if (st > 0) return "T" + st;
  int x = ttIndex(id);
  int t = x >= 0 ? TT_TIER[x] : metalTier(id);
  if (t < 1 || t > LADDER.length) return "";
  return "T" + t + " " + LADDER[t - 1];''', '''public static String tierText(String id) {
  if (id == null) return "";
  int st = suffixTier(id);
  if (st > 0) return "T" + st;
  int x = ttIndex(id);
  int t = x >= 0 ? TT_TIER[x] : metalTier(id);
  if (t < 1 || t > LADDER.length) return "";
  String w = x >= 0 ? TT_WORD[x] : metalWord(id);
  return "T" + t + " " + (w == null || w.length() == 0 ? LADDER[t - 1] : w);''')
P.rep('''# 0.8.11: an own-ladder tier suffix _T<n> (accessories, bags), 0 = none
''', '''# 0.8.22: the tag word of the tool metal word in the id (tools/tier_tags.py metal_word: Wood -> Crude, Steel -> Iron), null = none
rcmp.addMethod(CtNewMethod.make("""
public static String metalWord(String id) {
  if (id == null) return null;
  String[] w = id.split("_");
  for (int i = 0; i < w.length; i++) for (int j = 0; j < METAL_W.length; j++) if (w[i].equals(METAL_W[j])) return METAL_WD[j];
  return null;
}""", rcmp))
# 0.8.11: an own-ladder tier suffix _T<n> (accessories, bags), 0 = none
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.22 adds no system / command"
P.finish()
