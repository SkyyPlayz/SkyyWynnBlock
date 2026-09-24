"""Derive SkyyTrees/build_skyytrees_0.2.py from build_skyytrees_0.1.py (the skills_0_4_patch.py style: rep(old, new) with asserted single
anchors, newline-agnostic; 0.1 stays untouched and its CRLF/LF line endings are kept). Edit THIS file, not the generated script.
0.2 = research/Exploration-Build-Spec.md section 4 (SkyyTrees 0.2 on 0.1), from Skyy's Exploration call 2026-09-24
      (SkyyExploration-Plan.md 'trees' row: Exploration AND Acrobatics each get their own skill tree):
 - TREES += Acrobatics (tree 4), Exploration (tree 5); NT = 6, N = 72; every literal 48 / 4 of the 0.1 template replaced.
   Tree indices 0-3, every 0.1 node id, kind number, default and saved key stay as they were, so 0.1 player files load unchanged.
 - KINDS += RSPD, RJMP, RFALL, RDODGE, LUCK, SCAV, SOON (the 0.1 kind numbers 0-14 unchanged).
 - Acrobatics tree (spec 4.2): speed / jump / fall damage as the movement protocol source "trees.acrobatics" (TreeFx.acroPost, every
   second in TreeTick right after the trees.tools post), three Stamina nodes in skyytree_stamina, dodge push as skill:bonus
   "dodge.acrobatics" (SkyySkills 0.4.1 reads it).
 - Exploration tree (spec 4.3, SMALL DRAFT): two Health nodes in skyytree_health, Treasure Sense / Scavenger read by SkyyExploration
   through tree:fn:bonus, 8 SOON placeholders ("Coming later": TreeCfg.EN baked false, state / pathOk / texts / buy / toggle gated).
 - Per-tree Dust rate dust.xpPerDust.<Tree> (defaults Acrobatics 2, Exploration 5, others the global dust.xpPerDust),
   TreeCalc.dustEarned(tree, xp), texts show the tree's own rate.
 - Bridge tree:names (setup / shutdown), 6 page tabs (96 px + 4 px gaps, labels 140 / 110 / 120), /tree acrobatics | exploration.
 - An existing 0.1 trees.properties gets the 0.2 lines appended once (TreeCfg.has02 / ADD02); same numbers as the code defaults.
Run:  python tools/trees_0_2_patch.py   then   python SkyyTrees/build_skyytrees_0.2.py   (NO --deploy: coordinated deploy)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.1.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.1"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def rep_block(start, end, new):
    """replace from the unique `start` through the first `end` after it (inclusive)"""
    global s
    assert s.count(start) == 1, "block start count %d: %s" % (s.count(start), start[:100])
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + new + s[b:]


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyyTrees 0.1 - build script (javassist via jpype, tools/skyybuild.py). NEW mod. Owner: Skyy (they/them).
''', '''"""SkyyTrees 0.2 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.1.py by tools/trees_0_2_patch.py - edit the patch, not this file (0.1 stays untouched).
0.2 = research/Exploration-Build-Spec.md section 4, from Skyy's Exploration call 2026-09-24 (SkyyExploration-Plan.md 'trees' row):
  TWO NEW TREES on the same 12-slot template: Acrobatics (tree 4, #c8a0ff) and Exploration (tree 5, #e0a040); NT = 6, N = 72.
    Tree indices 0-3 and every 0.1 node id, kind number, default and saved key are unchanged, so 0.1 player files load as they are
    (players/<pkey>.properties: <Tree>.<Id>=level, <Tree>.off, <Tree>.respecAt; the two new trees simply start empty).
  ACROBATICS (12 nodes, verified hooks only): Fleet Foot / Sprinter / Windrunner = flat speed, Spring Step / High Jumper = flat jump
    (blocks), Soft Landing / Featherfall = flat fallDamage (negative), all posted as the movement protocol source "trees.acrobatics"
    (tools/skyymove.py; SkyySkills 0.2+ / SkyyAccessories 0.3+ apply it, the stat:owner:fallDamage owner sums fallDamage; TreeFx.acroPost
    every second, all zeros removes the entry, never another source). Second Wind / Marathon / Endurance = skyytree_stamina (+8 max
    Stamina at max). Quick Dodge / Evasion = skill:bonus:<uuid>["trees"] "dodge.acrobatics" (SkyySkills 0.4.1 reads it and caps it with
    acro.treeDodgeMax). At max: +20% speed, +0.7 blocks jump, -15% fall damage, +20% dodge push, +8 max Stamina.
  EXPLORATION (SMALL FIRST DRAFT - Skyy designs the rest later): Wanderer's Heart + Hearty Wanderer = skyytree_health (+20 max Health
    at max); Treasure Sense (LUCK) and Scavenger (SCAV) are numbers SkyyExploration reads through tree:fn:bonus ("Exploration.ELuck" /
    "Exploration.EScav", level x per); S5-S12 are "Coming later" placeholders (kind SOON): TreeCfg.EN baked false (no trees.properties
    line can turn one on), no trees.properties lines, TreeCalc.state / pathOk / tokSpent / dustSpent and the tree:<uuid> owned count skip
    them, the page shows "Coming later" (card #1a1a24 / #8890a0, no Turn off button), TreeOps.buy / toggle refuse them first, the load
    summary counts them apart ("N of 64 nodes on (8 coming later)"). Nothing in this tree boosts Exploration XP (Skyy Q3: no boosters).
  PER-TREE DUST RATE: dust.xpPerDust.<Tree> overrides dust.xpPerDust (defaults Acrobatics 2, Exploration 5; the other trees follow the
    global 10). Acrobatics XP is capped per minute and Exploration XP is one-time, so at 10 XP per Dust neither tree could be levelled.
    TreeCalc.dustEarned(tree, xp); the page note, the Dust need line and the load summary show each tree's own rate.
  BRIDGE: new tree:names = "Mining,Foraging,Farming,Cooking,Acrobatics,Exploration" (put in setup, removed in shutdown) - SkyySkills
    0.4.1 and SkyyExploration show their Tree buttons from it. clearOne also takes back move:<uuid>["trees.acrobatics"].
  CONFIG: an existing trees.properties (written by 0.1) gets the 0.2 block (per-tree Dust rates + the Acrobatics / Exploration node
    lines) appended ONCE, when it has no dust.xpPerDust.* / Acrobatics.* / Exploration.* key; it holds the same numbers as the
    built-in defaults, so the trees work the same whether or not the append succeeds.
  PAGE: 6 tabs of 96 px with 4 px gaps, level / tokens / Dust labels 140 / 110 / 120 (970 of the 972 px inner width). The Exploration
    tab's note: "Draft tree - Skyy designs the rest later - nothing here boosts Exploration XP", prefixed with "Exploration levels need
    SkyySkills 0.4.1" when the running SkyySkills publishes no Exploration level in skill:<uuid> (SkyySkills 0.4).
  COMMANDS: /tree acrobatics | exploration (3+ letter prefixes acr / exp work), help texts updated, same permission groups.
UNVERIFIED in 0.2 (needs Skyy's in-game test, spec 4.4): the SkyySkills / SkyyAccessories appliers picking up the new
  "trees.acrobatics" source (built against tools/skyymove.py), dodge.acrobatics (needs SkyySkills 0.4.1), and the Exploration numbers
  (need SkyyExploration 0.1 + SkyySkills 0.4.1).

=== SkyyTrees 0.1 notes (history; still true unless 0.2 above says otherwise) ===
SkyyTrees 0.1 - NEW mod.
''')
rep('''Run:   python build_skyytrees_0.1.py            -> SkyyTrees/SkyyTrees-0.1.jar
       python build_skyytrees_0.1.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''',
    '''Run:   python build_skyytrees_0.2.py            -> SkyyTrees/SkyyTrees-0.2.jar
       python build_skyytrees_0.2.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''')
rep('VERSION = "0.1"', 'VERSION = "0.2"')

# ================================================================ trees, kinds, tokens
rep('''TREES = ["Mining", "Foraging", "Farming", "Cooking"]
TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070"]''',
    '''TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration"]   # 0.2: append-only (tree index = saved key order)
TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070", "#c8a0ff", "#e0a040"]
for n, tn in enumerate(TREES): T["T_" + tn.upper()] = str(n)
# 0.2 per-tree Dust rate defaults (dust.xpPerDust.<Tree>); a tree not listed follows the global dust.xpPerDust
DUST_DEF = {"Acrobatics": 2, "Exploration": 5}''')
rep('''KINDS = ["DMG", "DD", "XP", "HP", "STA", "ITEM", "EXTRA", "COINS", "SPREAD", "MOVE", "VEIN", "FELLER", "EXTRA2", "COOK", "MASTER"]''',
    '''KINDS = ["DMG", "DD", "XP", "HP", "STA", "ITEM", "EXTRA", "COINS", "SPREAD", "MOVE", "VEIN", "FELLER", "EXTRA2", "COOK", "MASTER"]
KINDS += ["RSPD", "RJMP", "RFALL", "RDODGE", "LUCK", "SCAV", "SOON"]   # 0.2 (existing kind numbers unchanged)
assert KINDS.index("MASTER") == 14 and KINDS.index("SOON") == 21''')

# ================================================================ the two new node tables (spec 4.2 / 4.3)
rep('''  ("CMaster", "Master Chef", "Bench_Cooking", "MASTER", 5, 0.05, 0, "", "Level 1 = +1 Grade on every dish - each level after adds a chance of one more", "", ""),
 ],
}''', '''  ("CMaster", "Master Chef", "Bench_Cooking", "MASTER", 5, 0.05, 0, "", "Level 1 = +1 Grade on every dish - each level after adds a chance of one more", "", ""),
 ],
 # 0.2 (research/Exploration-Build-Spec.md 4.2): verified hooks only - movement protocol source trees.acrobatics, skyytree_stamina,
 # skill:bonus dodge.acrobatics (SkyySkills 0.4.1)
 "Acrobatics": [
  ("RSpeed", "Fleet Foot", "Armor_Leather_Light_Legs", "RSPD", 25, 0.004, 0, "+%V move speed", AFLAT + " - always on", "", ""),
  ("RJump", "Spring Step", "Ingredient_Feathers_Light", "RJMP", 20, 0.02, 0, "+%V blocks jump height", AFLAT + " - always on", "", ""),
  ("RStamina", "Second Wind", "Food_Bread", "STA", 15, 0.2, 0, "+%V max Stamina", ON, "", ""),
  ("RFall", "Soft Landing", "Glider", "RFALL", 10, 0.01, 0, "-%V fall damage", AFALL, "", ""),
  ("RDodge", "Quick Dodge", "Ingredient_Feathers_Blue", "RDODGE", 10, 0.01, 0, "+%V dodge push", ADODGE, "", ""),
  ("RStamina2", "Marathon", "Food_Pie_Apple", "STA", 15, 0.2, 0, "+%V max Stamina - adds to Second Wind", ON, "", ""),
  ("RSpeed2", "Sprinter", "Armor_Leather_Light_Legs", "RSPD", 10, 0.005, 0, "+%V move speed - adds to Fleet Foot", AFLAT + " - always on", "", ""),
  ("RJump2", "High Jumper", "Ingredient_Feathers_Red", "RJMP", 10, 0.03, 0, "+%V blocks jump height - adds to Spring Step", AFLAT + " - always on", "", ""),
  ("RFall2", "Featherfall", "Ingredient_Feathers_Dark", "RFALL", 10, 0.005, 0, "-%V fall damage - adds to Soft Landing", AFALL, "", ""),
  ("RStamina3", "Endurance", "Food_Wildmeat_Cooked", "STA", 20, 0.1, 0, "+%V max Stamina - adds to Marathon", ON, "", ""),
  ("RDodge2", "Evasion", "Glider", "RDODGE", 10, 0.01, 0, "+%V dodge push - adds to Quick Dodge", ADODGE, "", ""),
  ("RSpeed3", "Windrunner", "Armor_Leather_Light_Legs", "RSPD", 5, 0.01, 0, "+%V move speed - adds to Sprinter", AFLAT + " - always on", "", ""),
 ],
 # 0.2 (spec 4.3): SMALL FIRST DRAFT - Skyy designs the rest of the Exploration tree later. Nothing here boosts Exploration XP.
 "Exploration": [
  ("EHeart", "Wanderer's Heart", "Plant_Fruit_Apple", "HP", 25, 0.4, 0, "+%V max Health", ON, "", ""),
  ("ELuck", "Treasure Sense", "Rock_Gem_Ruby", "LUCK", 20, 0.005, 0, "+%V chest luck - the chance of an extra roll on a first-opened loot chest", ELOOT + " - adds to the chest luck of your Exploration level", "", ""),
  ("EScav", "Scavenger", "Ingredient_Bar_Gold", "SCAV", 15, 0.01, 0, "%V chance of coins (10 x Exploration level) on a first-opened loot chest", ELOOT + " - needs SkyyCoins", "", ""),
  ("EHeart2", "Hearty Wanderer", "Plant_Fruit_Berries_Red", "HP", 10, 1.0, 0, "+%V max Health - adds to Wanderer's Heart", ON, "", ""),
 ] + [("ESoon%d" % n, "Coming later", "Deco_Scroll", "SOON", SLOT_MAX[n - 1], 0.0, 0, "", SOONHOW, "", "") for n in range(5, 13)],
}''')
before('''# (id, name, icon, kind, max, per, base, now, how, list key, default list)
NODES = {''', '''AFLAT = "Flat layer of the movement protocol (trees.acrobatics) - applied by SkyySkills or SkyyAccessories"
AFALL = "Less damage from every fall (SkyySkills applies it) - a bigger fall is needed for Acrobatics fall XP"
ADODGE = "Your vanilla dodge pushes you further (SkyySkills dodge boost) - needs SkyySkills 0.4.1"
ELOOT = "SkyyExploration reads it when you open a world loot chest for the first time"
SOONHOW = "Draft slot - nothing here yet and it cannot be unlocked"
''')
rep('''assert len(ROWS) == 48 and len(set(r["id"] for r in ROWS)) == 48''',
    '''assert len(ROWS) == 72 and len(set(r["id"] for r in ROWS)) == 72
SOON_ROWS = [r for r in ROWS if KINDS[r["kind"]] == "SOON"]
assert len(SOON_ROWS) == 8 and all(TREES[r["t"]] == "Exploration" and r["s"] >= 5 for r in SOON_ROWS)
# spec 4.2 totals at max (Acrobatics) and 4.3 (Exploration)
def _tot(ids): return round(sum(r["max"] * r["per"] for r in ROWS if r["id"] in ids), 6)
assert _tot(("RSpeed", "RSpeed2", "RSpeed3")) == 0.2 and _tot(("RJump", "RJump2")) == 0.7 and _tot(("RFall", "RFall2")) == 0.15
assert _tot(("RDodge", "RDodge2")) == 0.2 and _tot(("RStamina", "RStamina2", "RStamina3")) == 8.0 and _tot(("EHeart", "EHeart2")) == 20.0
assert _tot(("ELuck",)) == 0.1 and _tot(("EScav",)) == 0.15
# spec 4.3: the 4 draft nodes cost 989,375 Dust (about 4.9M Exploration XP at 5 XP per Dust)
assert sum(sum(r["B"] * n ** 3 for n in range(1, r["max"])) for r in ROWS if TREES[r["t"]] == "Exploration" and KINDS[r["kind"]] != "SOON") == 989375''')

# ================================================================ trees.properties defaults (+ the 0.2 block for an existing 0.1 file)
rep('''DL = ["# SkyyTrees %s - skill trees for Mining, Foraging, Farming and Cooking. /tree reload re-reads this file (perm skyytrees.admin)." % VERSION,''',
    '''DL = ["# SkyyTrees %s - skill trees for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration. /tree reload re-reads this file (perm skyytrees.admin)." % VERSION,''')
DUST_LINES = '''["# Per-tree Dust rate: dust.xpPerDust.<Tree> overrides dust.xpPerDust for that tree (a tree without a line uses dust.xpPerDust).",
      "# Acrobatics XP is capped per minute and Exploration XP is one-time, so their trees get more Dust per XP."] + \\
     ["dust.xpPerDust.%s=%d" % (t, DUST_DEF[t]) for t in TREES if t in DUST_DEF]'''
rep('''      "dust.xpPerDust=10",
''', '''      "dust.xpPerDust=10"] + ''' + DUST_LINES + ''' + [
''')
rep_block('''for r in ROWS:
    tn = TREES[r["t"]]
    k = "%s.%s." % (tn, r["id"])''', '''DEFAULTS = "\\n".join(DL) + "\\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)''', '''def node_lines(r):
    tn = TREES[r["t"]]
    k = "%s.%s." % (tn, r["id"])
    out = ["# %s S%d %s (tier %s)" % (tn, r["s"], r["name"], ["I", "II", "III", "IV", "V", "VI"][r["tier"] - 1])]
    out.append(k + "max=%d" % r["max"])
    out.append(k + "per=%s" % repr(float(r["per"])))
    if KINDS[r["kind"]] in ("VEIN", "FELLER"): out.append(k + "base=%s" % repr(float(r["base"])))
    out.append(k + "B=%d" % r["B"])
    out.append(k + "tokens=%d" % r["tok"])
    out.append(k + "enabled=true")
    if r["lk"]: out.append(k + r["lk"] + "=" + r["lst"])
    return out
SOON_NOTE = "# Exploration S5-S12 are 'Coming later' placeholders of the draft tree: they have no lines and can never be turned on"
for r in ROWS:
    if KINDS[r["kind"]] == "SOON": continue   # 0.2 spec 4.1: no node lines for SOON slots
    DL.extend(node_lines(r))
DL.append(SOON_NOTE)
DEFAULTS = "\\n".join(DL) + "\\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
# 0.2: appended ONCE to a trees.properties that 0.1 wrote (TreeCfg.has02 finds none of these keys). Same numbers as the code defaults.
ADD02 = ["# ---------- SkyyTrees 0.2 (appended once to a 0.1 file): Acrobatics and Exploration trees, per-tree Dust rates ----------"]
ADD02 += ''' + DUST_LINES + '''
for r in ROWS:
    if TREES[r["t"]] in ("Acrobatics", "Exploration") and KINDS[r["kind"]] != "SOON": ADD02.extend(node_lines(r))
ADD02.append(SOON_NOTE)
ADD02 = "\\n".join(ADD02) + "\\n"
assert all(ord(ch) < 128 for ch in ADD02)
assert "SOON" not in DEFAULTS and "ESoon" not in DEFAULTS and "ESoon" not in ADD02
assert "dust.xpPerDust.Acrobatics=2" in DEFAULTS and "dust.xpPerDust.Exploration=5" in DEFAULTS and "dust.xpPerDust.Exploration=5" in ADD02
assert "Acrobatics.RSpeed.max=25" in ADD02 and "Exploration.EHeart2.enabled=true" in ADD02 and "Mining." not in ADD02''')

# ================================================================ TreeDefs
rep('''F(defs, "public static final int NT = 4;")
F(defs, "public static final int N = 48;")''',
    '''F(defs, "public static final int NT = %d;" % len(TREES))
F(defs, "public static final int N = %d;" % len(ROWS))
F(defs, "public static final int SOON_N = %d;" % len(SOON_ROWS))
F(defs, "public static final String NAMES_CSV = %s;" % json.dumps(",".join(TREES)))
F(defs, "public static final long[] D_DUST = %s;" % jlong([DUST_DEF.get(t, 0) for t in TREES]))''')
# 0.2: SOON placeholder test (spec 4.1) - added before every caller
before('''M(defs, r"""
public static int tree(String s) {''', '''M(defs, r"""
public static boolean soon(int i) {
  return i >= 0 && i < N && KIND[i] == @K_SOON@;
}""")
''')
rep('''  if (k == @K_HP@ || k == @K_STA@) return num(v);''', '''  if (k == @K_HP@ || k == @K_STA@ || k == @K_RJMP@) return num(v);''')

# ================================================================ TreeCfg
rep('''F(cfg, "public static final String DEFAULTS = " + json.dumps(DEFAULTS) + ";")''',
    '''F(cfg, "public static final String DEFAULTS = " + json.dumps(DEFAULTS) + ";")
F(cfg, "public static final String ADD02 = " + json.dumps(ADD02) + ";")''')
rep('''             "long FEEDBACK_MS = 2000L", "long EXTRA_TOKENS = 0L", "long EXTRA_DUST = 0L",''',
    '''             "long FEEDBACK_MS = 2000L", "long EXTRA_TOKENS = 0L", "long EXTRA_DUST = 0L",
             "long[] XP_T = " + jlong([DUST_DEF.get(t, 10) for t in TREES]),''')
rep('''"boolean[] EN = new boolean[] { " + ", ".join(["true"] * 48) + " }",
             "Object[] LIST = new Object[48]"):''',
    '''"boolean[] EN = new boolean[] { " + ", ".join("false" if KINDS[r["kind"]] == "SOON" else "true" for r in ROWS) + " }",
             "Object[] LIST = new Object[%d]" % len(ROWS)):''')
# per-tree Dust rate reader (before apply / load / TreeCalc)
before('''M(cfg, r"""
public static void apply(java.util.Properties p) {''', '''M(cfg, r"""
public static long rate(int t) {
  long[] xt = XP_T;
  if (t >= 0 && t < xt.length && xt[t] > 0L) return xt[t];
  return XP_PER_DUST < 1L ? 1L : XP_PER_DUST;
}""")
M(cfg, r"""
public static boolean has02(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("dust.xpPerDust.") || k.startsWith("Acrobatics.") || k.startsWith("Exploration.")) return true;
  }
  return false;
}""")
''')
rep('''  XP_PER_DUST = clampL(lng(p, "dust.xpPerDust", 10L), 1L, 1000000000L);
''', '''  XP_PER_DUST = clampL(lng(p, "dust.xpPerDust", 10L), 1L, 1000000000L);
  long[] xt = new long[@PKG@.TreeDefs.NT];
  for (int tt = 0; tt < xt.length; tt++) {
    long dd = @PKG@.TreeDefs.D_DUST[tt] > 0L ? @PKG@.TreeDefs.D_DUST[tt] : XP_PER_DUST;
    xt[tt] = clampL(lng(p, "dust.xpPerDust." + @PKG@.TreeDefs.TREES[tt], dd), 1L, 1000000000L);
  }
  XP_T = xt;
''')
rep('''    en[i] = bool(p, k + "enabled", true);''', '''    en[i] = !@PKG@.TreeDefs.soon(i) && bool(p, k + "enabled", true);''')
rep_block('''M(cfg, r"""
public static synchronized String load() {''', '''  return on + " of 48 nodes on, tiers " + tl[0] + "/" + tl[1] + "/" + tl[2] + "/" + tl[3] + "/" + tl[4] + "/" + tl[5] + ", 1 Dust per " + XP_PER_DUST + " XP" + (EXTRA_TOKENS > 0L || EXTRA_DUST > 0L ? " (DEBUG extra tokens/Dust on)" : "");
}""")''', '''M(cfg, r"""
public static synchronized String load() {
  java.util.Properties p = new java.util.Properties();
  boolean loaded = false;
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
      info("wrote default " + FILE);
    }
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    loaded = true;
  } catch (Throwable t) { warn("could not read trees.properties (built-in defaults used): " + t); }
  if (loaded && !has02(p)) {
    try {
      java.nio.file.Files.write(FILE, ("\\n" + ADD02).getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.APPEND });
      info("added the SkyyTrees 0.2 lines (Acrobatics and Exploration trees, per-tree Dust rates) to " + FILE);
    } catch (Throwable t2) { warn("could not add the 0.2 lines to trees.properties (their built-in defaults apply anyway): " + t2); }
  }
  apply(p);
  int on = 0;
  for (int i = 0; i < EN.length; i++) if (EN[i] && !@PKG@.TreeDefs.soon(i)) on++;
  int[] tl = TIER_LV;
  StringBuilder rt = new StringBuilder();
  for (int tt = 0; tt < @PKG@.TreeDefs.NT; tt++) {
    if (rate(tt) == XP_PER_DUST) continue;
    rt.append(rt.length() == 0 ? " (" : ", ").append(@PKG@.TreeDefs.TREES[tt]).append(' ').append(rate(tt));
  }
  if (rt.length() > 0) rt.append(')');
  return on + " of " + (@PKG@.TreeDefs.N - @PKG@.TreeDefs.SOON_N) + " nodes on (" + @PKG@.TreeDefs.SOON_N + " coming later), tiers " + tl[0] + "/" + tl[1] + "/" + tl[2] + "/" + tl[3] + "/" + tl[4] + "/" + tl[5] + ", 1 Dust per " + XP_PER_DUST + " XP" + rt.toString() + (EXTRA_TOKENS > 0L || EXTRA_DUST > 0L ? " (DEBUG extra tokens/Dust on)" : "");
}""")''')

# ================================================================ TreeData (sizes follow the table)
rep('''F(dat, "public int[] lv = new int[48];")
F(dat, "public boolean[] off = new boolean[48];")
F(dat, "public long[] respecAt = new long[4];")''',
    '''F(dat, "public int[] lv = new int[%d];" % len(ROWS))
F(dat, "public boolean[] off = new boolean[%d];" % len(ROWS))
F(dat, "public long[] respecAt = new long[%d];" % len(TREES))''')

# ================================================================ TreeCalc
after('''M(calc, r"""
public static boolean hasXp() {
  return fn("skill:fn:xp") != null;
}""")''', '''
# 0.2: does the running SkyySkills know this skill? skill:<uuid> = "Mining:12,...,Exploration:3,..." (SkyySkills 0.4.1 adds Exploration).
# Unknown (nothing published yet) counts as yes, so the page never claims a missing skill it cannot see.
M(calc, r"""
public static boolean skillKnown(java.util.UUID u, int t) {
  try {
    Object o = @PKG@.TreeStore.bridge().get("skill:" + u.toString());
    if (!(o instanceof String)) return true;
    return ("," + (String) o).indexOf("," + @PKG@.TreeDefs.TREES[t] + ":") >= 0;
  } catch (Throwable e) { return true; }
}""")''')
rep('''public static long dustEarned(long xp) {
  return xp / @PKG@.TreeCfg.XP_PER_DUST + @PKG@.TreeCfg.EXTRA_DUST;
}''', '''public static long dustEarned(int t, long xp) {
  return xp / @PKG@.TreeCfg.rate(t) + @PKG@.TreeCfg.EXTRA_DUST;
}''')
rep('''  for (int k = 0; k < 12; k++) { int i = t * 12 + k; if (d.lv[i] >= 1) s = s + (long) @PKG@.TreeCfg.TOK[i]; }''',
    '''  for (int k = 0; k < 12; k++) { int i = t * 12 + k; if (d.lv[i] >= 1 && !@PKG@.TreeDefs.soon(i)) s = s + (long) @PKG@.TreeCfg.TOK[i]; }''')
rep('''    int i = t * 12 + k;
    for (int n = 1; n < d.lv[i]; n++) s = s + cost(i, n);''', '''    int i = t * 12 + k;
    if (@PKG@.TreeDefs.soon(i)) continue;
    for (int n = 1; n < d.lv[i]; n++) s = s + cost(i, n);''')
rep('''  r[2] = dustEarned(xp(u, t, lvl));''', '''  r[2] = dustEarned(t, xp(u, t, lvl));''')
rep('''    if (@PKG@.TreeDefs.TIER[i] == tier - 1 && d.lv[i] >= 1) return true;''',
    '''    if (@PKG@.TreeDefs.soon(i)) continue;
    if (@PKG@.TreeDefs.TIER[i] == tier - 1 && d.lv[i] >= 1) return true;''')
rep('''public static int state(@PKG@.TreeData d, int i, int lvl, long tokA) {
  int l = d.lv[i];''', '''public static int state(@PKG@.TreeData d, int i, int lvl, long tokA) {
  if (@PKG@.TreeDefs.soon(i)) return 0;
  int l = d.lv[i];''')
rep('''  if (d.bad) return "Unreadable";
  if (!@PKG@.TreeCfg.EN[i]) return "Turned off";''', '''  if (d.bad) return "Unreadable";
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
  if (!@PKG@.TreeCfg.EN[i]) return "Turned off";''')

# ================================================================ TreeFx (Acrobatics + Exploration effects)
rep('''F(fx, 'public static final String MOVE_SRC = "trees.tools";')''',
    '''F(fx, 'public static final String MOVE_SRC = "trees.tools";')
F(fx, 'public static final String ACRO_SRC = "trees.acrobatics";')''')
rep('''  putNZ(m, "dd.farming", v[@I_AFORTUNE@] + v[@I_AFORTUNE2@]);
  return m;''', '''  putNZ(m, "dd.farming", v[@I_AFORTUNE@] + v[@I_AFORTUNE2@]);
  putNZ(m, "dodge.acrobatics", v[@I_RDODGE@] + v[@I_RDODGE2@]);
  return m;''')
rep('''    for (int s = 0; s < 12; s++) if (d.lv[t * 12 + s] >= 1) owned++;''',
    '''    for (int s = 0; s < 12; s++) if (d.lv[t * 12 + s] >= 1 && !@PKG@.TreeDefs.soon(t * 12 + s)) owned++;''')
after('''  e.put("fallDamage", Float.valueOf(0.0f));
  if (e.equals(m.get(MOVE_SRC))) return;
  m.put(MOVE_SRC, e);
}""")''', '''
# 0.2 Acrobatics tree: movement protocol v1 source "trees.acrobatics" (layer flat: speed = fraction of the default speed, jump = blocks,
# fallDamage = added to the multiplier, negative = less). All zeros removes our entry; never touches another source (skyymove rule 1).
M(fx, r"""
public static void acroPost(java.util.UUID u, double[] v) {
  float sp = (float) r6(v[@I_RSPEED@] + v[@I_RSPEED2@] + v[@I_RSPEED3@]);
  float jp = (float) r6(v[@I_RJUMP@] + v[@I_RJUMP2@]);
  float fd = (float) r6(0.0 - (v[@I_RFALL@] + v[@I_RFALL2@]));
  if (fd == 0.0f) fd = 0.0f;
  java.util.Map b = @PKG@.TreeStore.bridge();
  String k = "move:" + u.toString();
  Object o = b.get(k);
  if (sp == 0.0f && jp == 0.0f && fd == 0.0f) { if (o instanceof java.util.Map) ((java.util.Map) o).remove(ACRO_SRC); return; }
  java.util.Map m = null;
  if (o instanceof java.util.Map) m = (java.util.Map) o;
  else {
    java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
    Object prev = b.putIfAbsent(k, n);
    if (prev instanceof java.util.Map) m = (java.util.Map) prev; else m = n;
  }
  java.util.HashMap e = new java.util.HashMap();
  e.put("layer", "flat");
  e.put("speed", Float.valueOf(sp));
  e.put("jump", Float.valueOf(jp));
  e.put("fallDamage", Float.valueOf(fd));
  if (e.equals(m.get(ACRO_SRC))) return;
  m.put(ACRO_SRC, e);
}""")''')
rep('''    double hp = v[@I_FVIGOR@] + v[@I_AHEARTY@] + v[@I_CFED@];
    double sta = v[@I_MSTAMINA@];''', '''    double hp = v[@I_FVIGOR@] + v[@I_AHEARTY@] + v[@I_CFED@] + v[@I_EHEART@] + v[@I_EHEART2@];
    double sta = v[@I_MSTAMINA@] + v[@I_RSTAMINA@] + v[@I_RSTAMINA2@] + v[@I_RSTAMINA3@];''')
rep('''    if (mv instanceof java.util.Map) ((java.util.Map) mv).remove(MOVE_SRC);''',
    '''    if (mv instanceof java.util.Map) ((java.util.Map) mv).remove(MOVE_SRC);
    if (mv instanceof java.util.Map) ((java.util.Map) mv).remove(ACRO_SRC);''')

# ================================================================ TreeTick: post the Acrobatics source every second
rep('''    @PKG@.TreeFx.movePost(u, (float) @PKG@.TreeFx.toolSpeed(v, hid));''',
    '''    @PKG@.TreeFx.movePost(u, (float) @PKG@.TreeFx.toolSpeed(v, hid));
    @PKG@.TreeFx.acroPost(u, v);''')

# ================================================================ TreeOps: SOON slots are refused first
before('''M(ops, r"""
public static String buy(@PR@ pr, int t, int s) {''', '''M(ops, r"""
public static String soonText(int t, int s) {
  return "Node S" + s + " of the " + @PKG@.TreeDefs.TREES[t] + " tree is coming later - Skyy designs the rest of this draft tree later";
}""")
''')
rep('''  String nm = @PKG@.TreeDefs.NAME[i];
  String tn = @PKG@.TreeDefs.TREES[t];
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  if (!@PKG@.TreeCfg.EN[i]) return nm + " is turned off on this server";''', '''  String nm = @PKG@.TreeDefs.NAME[i];
  String tn = @PKG@.TreeDefs.TREES[t];
  if (@PKG@.TreeDefs.soon(i)) return soonText(t, s);
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  if (!@PKG@.TreeCfg.EN[i]) return nm + " is turned off on this server";''')
rep('''  int i = t * 12 + s - 1;
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  if (d.lv[i] <= 0) return "You do not own " + @PKG@.TreeDefs.NAME[i] + " yet";''', '''  int i = t * 12 + s - 1;
  if (@PKG@.TreeDefs.soon(i)) return soonText(t, s);
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  if (d.lv[i] <= 0) return "You do not own " + @PKG@.TreeDefs.NAME[i] + " yet";''')

# ================================================================ TreePage
rep('''F(page, "public static final java.util.concurrent.ConcurrentHashMap LASTTREE = new java.util.concurrent.ConcurrentHashMap();")''',
    '''F(page, "public static final java.util.concurrent.ConcurrentHashMap LASTTREE = new java.util.concurrent.ConcurrentHashMap();")
F(page, 'public static final String SOON_BG = "#1a1a24";')
F(page, 'public static final String SOON_HV = "#262634";')
F(page, 'public static final String SOON_FG = "#8890a0";')''')
rep('''public static String stateLine(@PKG@.TreeData d, int i, int stt) {
''', '''public static String stateLine(@PKG@.TreeData d, int i, int stt) {
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
''')
rep('''public static String nowLine(@PKG@.TreeData d, int i) {
''', '''public static String nowLine(@PKG@.TreeData d, int i) {
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
''')
rep('''public static String nextLine(@PKG@.TreeData d, int i) {
''', '''public static String nextLine(@PKG@.TreeData d, int i) {
  if (@PKG@.TreeDefs.soon(i)) return "";
''')
rep('''public static String costLine(@PKG@.TreeData d, int i) {
''', '''public static String costLine(@PKG@.TreeData d, int i) {
  if (@PKG@.TreeDefs.soon(i)) return "Cost: -";
''')
rep('''public static String needLine(@PKG@.TreeData d, int i, int lvl, long tokA, long dustA) {
''', '''public static String needLine(@PKG@.TreeData d, int i, int lvl, long tokA, long dustA) {
  if (@PKG@.TreeDefs.soon(i)) return "Draft - Skyy designs the rest of the " + @PKG@.TreeDefs.TREES[i / 12] + " tree later";
''')
rep('''  if (dustA < c) return "Needs: " + @PKG@.TreeDefs.grp(c - dustA) + " more Dust (1 per " + @PKG@.TreeCfg.XP_PER_DUST + " " + tn + " XP)";''',
    '''  if (dustA < c) return "Needs: " + @PKG@.TreeDefs.grp(c - dustA) + " more Dust (1 per " + @PKG@.TreeCfg.rate(t) + " " + tn + " XP)";''')
rep('''public static String buyText(@PKG@.TreeData d, int i, int stt, int lvl, long tokA, long dustA) {
''', '''public static String buyText(@PKG@.TreeData d, int i, int stt, int lvl, long tokA, long dustA) {
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
''')
rep('''public static String note(@PKG@.TreeData d, int t, int lvl, long tokA, long dustA) {''',
    '''public static String note(java.util.UUID u, @PKG@.TreeData d, int t, int lvl, long tokA, long dustA) {''')
rep('''  if (tokA < 0L || dustA < 0L) return "Costs changed - your balance is negative: effects keep working, buying is blocked, a respec is free right now";
''', '''  if (tokA < 0L || dustA < 0L) return "Costs changed - your balance is negative: effects keep working, buying is blocked, a respec is free right now";
  if (t == @T_EXPLORATION@) return (@PKG@.TreeCalc.skillKnown(u, t) ? "" : "Exploration levels need SkyySkills 0.4.1 - ") + "Draft tree - Skyy designs the rest later - nothing here boosts Exploration XP";
''')
rep('''  return "Tokens unlock nodes - Dust (1 per " + @PKG@.TreeCfg.XP_PER_DUST + " XP) levels them up - a respec gives everything back";''',
    '''  return "Tokens unlock nodes - Dust (1 per " + @PKG@.TreeCfg.rate(t) + " XP) levels them up - a respec gives everything back";''')
# header: 6 tabs of 96 px + 4 px gaps, labels 140 / 110 / 120 (970 of the 972 px inner width)
rep(r'''"TextButton #SkyyTrTab" + i + " { Anchor: (Width: 108, Height: 32); Text: \""''',
    r'''"TextButton #SkyyTrTab" + i + " { Anchor: (Width: 96, Height: 32); Text: \""''')
rep(r'''    b.appendInline("#SkyyTrHead", "Label { Anchor: (Width: 6, Height: 32); Text: \"\"; }");''',
    r'''    b.appendInline("#SkyyTrHead", "Label { Anchor: (Width: 4, Height: 32); Text: \"\"; }");''')
rep('''"Label #SkyyTrLvl { Anchor: (Width: 170, Height: 32);''', '''"Label #SkyyTrLvl { Anchor: (Width: 140, Height: 32);''')
rep('''"Label #SkyyTrTok { Anchor: (Width: 150, Height: 32);''', '''"Label #SkyyTrTok { Anchor: (Width: 110, Height: 32);''')
rep('''"Label #SkyyTrDust { Anchor: (Width: 190, Height: 32);''', '''"Label #SkyyTrDust { Anchor: (Width: 120, Height: 32);''')
rep('''  b.set("#SkyyTrNote.Text", note(d, t, lvl, tokA, dustA));''', '''  b.set("#SkyyTrNote.Text", note(u, d, t, lvl, tokA, dustA));''')
# SOON cards: their own colours (spec 4.1: #1a1a24 / #8890a0); the selected card uses the hover colour like every state
rep('''      int stt = @PKG@.TreeCalc.state(d, i, lvl, tokA);
      String hv = HV[stt];
      String bg = s == sl ? hv : BG[stt];
      String fg = FG[stt];''', '''      int stt = @PKG@.TreeCalc.state(d, i, lvl, tokA);
      boolean so = @PKG@.TreeDefs.soon(i);
      String hv = so ? SOON_HV : HV[stt];
      String bg = s == sl ? hv : (so ? SOON_BG : BG[stt]);
      String fg = so ? SOON_FG : FG[stt];''')
rep('''  int st0 = @PKG@.TreeCalc.state(d, i0, lvl, tokA);
  String fg0 = FG[st0];''', '''  int st0 = @PKG@.TreeCalc.state(d, i0, lvl, tokA);
  String fg0 = @PKG@.TreeDefs.soon(i0) ? SOON_FG : FG[st0];''')
rep('''  if (d.lv[i0] >= 1) {
    b.appendInline("#SkyyTrDet", "TextButton #SkyyTrToggle''', '''  if (d.lv[i0] >= 1 && !@PKG@.TreeDefs.soon(i0)) {
    b.appendInline("#SkyyTrDet", "TextButton #SkyyTrToggle''')

# ================================================================ commands (same permission groups; texts list the new trees)
rep('''  super("Open one skill tree: /tree mining | foraging | farming | cooking");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | cooking", @ATY@.STRING);''',
    '''  super("Open one skill tree: /tree mining | foraging | farming | cooking | acrobatics | exploration");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | cooking | acrobatics | exploration", @ATY@.STRING);''')
rep('''"[Trees] Unknown tree - use /tree mining, foraging, farming or cooking"''',
    '''"[Trees] Unknown tree - use /tree mining, foraging, farming, cooking, acrobatics or exploration"''')
rep('''  super("tree", "Open your skill trees: /tree, /tree mining | foraging | farming | cooking, /tree quiet");''',
    '''  super("tree", "Open your skill trees: /tree, /tree mining | foraging | farming | cooking | acrobatics | exploration, /tree quiet");''')

# ================================================================ plugin: tree:names
rep('''  b.put("tree:fn:bonus", @PKG@.TreeStore.BFN);''', '''  b.put("tree:fn:bonus", @PKG@.TreeStore.BFN);
  b.put("tree:names", @PKG@.TreeDefs.NAMES_CSV);''')
rep('''    if (@PKG@.TreeStore.BFN != null) b.remove("tree:fn:bonus", @PKG@.TreeStore.BFN);''',
    '''    if (@PKG@.TreeStore.BFN != null) b.remove("tree:fn:bonus", @PKG@.TreeStore.BFN);
    b.remove("tree:names", @PKG@.TreeDefs.NAMES_CSV);''')
rep('''"SkyWynn skill trees (Heart of the Mountain style) for Mining, Foraging, Farming and Cooking: tokens from your skill level unlock nodes, Dust from your skill XP levels them. Breaking power, double drops, XP, max health / stamina, gems, bars, saplings, seeds, extra drops, coins, tool speed, Spread, Vein Burst, Tree Feller and the Cooking bonuses SkyyCooking reads.''',
    '''"SkyWynn skill trees (Heart of the Mountain style) for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration (draft): tokens from your skill level unlock nodes, Dust from your skill XP levels them. Breaking power, double drops, XP, max health / stamina, gems, bars, saplings, seeds, extra drops, coins, tool speed, Spread, Vein Burst, Tree Feller, the Cooking bonuses SkyyCooking reads, move speed / jump / fall damage / dodge push and the chest luck SkyyExploration reads.''')

# ================================================================ sanity
assert 'VERSION = "0.2"' in s and "DERIVED from build_skyytrees_0.1.py by tools/trees_0_2_patch.py" in s
for bad in ("new int[48]", "new boolean[48]", "respecAt = new long[4]", "new Object[48]", '["true"] * 48', "of 48 nodes", "== 48", "NT = 4;", "N = 48;",
            "dustEarned(long xp)", "dustEarned(xp(", "TreeCfg.XP_PER_DUST + \" \"", "(1 per \" + @PKG@.TreeCfg.XP_PER_DUST", "Width: 108", "Width: 170, Height: 32",
            "note(d, t, lvl"):
    assert bad not in s, "0.1 leftover: " + bad
assert s.count("@PKG@.TreeDefs.soon(") == 19, s.count("@PKG@.TreeDefs.soon(")
assert s.count("@PKG@.TreeFx.acroPost(u, v);") == 1 and s.count("public static void acroPost(") == 1
assert s.count('b.put("tree:names"') == 1 and s.count('b.remove("tree:names"') == 1
assert s.count("remove(ACRO_SRC)") == 2 and s.count('putNZ(m, "dodge.acrobatics"') == 1
assert s.count("registerSystem(") == 2   # one registerSystem per class, unchanged: TreeDmgSys + TreeTick
assert s.count('setPermissionGroups(new String[] { "hytale:Adventurer" })') == 3 and s.count("setPermissionGroups(new String[0])") == 1
assert "--deploy" in s   # the script keeps its optional deploy switch; workflows never pass it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.1
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
