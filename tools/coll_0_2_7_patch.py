"""Derive SkyyCollections/build_skyycollections_0.2.7.py from the LIVE 0.2.6 (build_skyycollections_0.2.6.py = the tools/deploy_set.py
SET pin; 0.2.6 stays untouched; same style as coll_0_2_6_patch.py: rep() with asserted single anchors, newline-agnostic, the source's
line endings kept). Edit THIS file, never the generated build script (it is overwritten on every run of this patch).
Run:  python tools/coll_0_2_7_patch.py   then   python SkyyCollections/build_skyycollections_0.2.7.py   (never --deploy)
Test: python SkyyCollections/test_skyycollections_0.2.7.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/, deleted afterwards)

0.2.7 = THE LANTERN RECIPES UNLOCK FROM THE TREE SAP COLLECTION (Skyy 2026-10-05, LOCKED, docs/answered/economy.md: "add the lantern
accessory's crafting recipe to the sap collection. so you have to collect a lot to get a legendary lantern"). The SkyySacks bag ladder's
mechanism (coll:recipes:<uuid> -> the player's known recipes -> the engine refuses a KnowledgeRequired craft at a bench unless known);
SkyyAccessories 0.5.6 is the other half (its four Lantern recipes become KnowledgeRequired and follow coll:recipes).
  - The four Lantern recipe ids (Skyy_Talisman_Lantern_Common / _Uncommon / _Rare / _Epic + _Recipe_Generated_0 = Normal / Unique / Rare /
    Legendary) are recipe unlocks of the TreeSap collection (Foraging, Standard curve 50,100,250,500,1000,2500,5000,10000,20000 - it
    already existed) at the tiers of four NEW config.properties keys, each an editable Server Setup row (Collections -> Lantern recipes):
    lantern.tier.normal 1 (50 sap), lantern.tier.unique 3 (250), lantern.tier.rare 5 (1,000), lantern.tier.legendary 8 (10,000)
    - proposed numbers, Skyy confirms. No file is rewritten: an existing config.properties has no lantern line, so the defaults apply
    (a missing key = its default) until an admin sets one in game; a fresh install gets the four lines in its default file.
  - CollReg.validate (start, /collections reload, every Server Setup change) merges them into RECIPES like a rewards.properties line, so
    every existing path shows / publishes / explains them unchanged: the TreeSap tier rows ("Normal Lantern Accessory recipe"), the
    tier-up chat, the Unlocked recipes view, coll:recipes:<uuid>, coll:fn:where. Past tiers count at once (computed from the counts).
  - The rows are the ONE place: a Lantern recipe token in rewards.properties is ignored (WARN, counted in the recipe-check line) and the
    Tier rewards table refuses one (CollKit.rewardToken). A tier past the collection's ladder uses its last tier (WARN); the row's check
    refuses it (CollKit.checkLanTier). A bad / missing value = the default (WARN on a bad one).
  - COINS NEVER BUY A LANTERN (Coins never skip collections or recipe unlocks, LOCKED): CollUtil.bagRank (the coin rank every bought-tier
    path already checks against bypass.bagMax) answers 9 for a Lantern recipe, above every bagMax word, so a BOUGHT tier never unlocks
    one (coll:recipes, the Unlocked recipes view) and its row says "(gather this tier)" (also while bags are free); CollBypass.buyable
    is false for it (a TreeSap chain with nothing else to buy refuses the purchase) and unlockText names it "must be gathered" (also
    while bags are free). Coin unlocks are off by default anyway (0.2.5).
  - Bridge (plain java.lang): coll:lantern = "TreeSap|<normal>|<unique>|<rare>|<legendary>" (the tiers in effect) while this mod
    manages the Lantern recipes - published by validate; "off" when it does not (SkyyAccessories missing: its recipe ids are not in
    the asset store; no visible TreeSap collection - SkyyAccessories then frees every Lantern at once, also after a reload); removed
    at shutdown. SkyyAccessories 0.5.6 locks Lanterns ONLY while it sees this key;
    without it (SkyyCollections missing, an older SkyyCollections, no TreeSap) every Lantern stays craftable (0.5.5 behaviour).
  - SkyyAccessories missing: the four ids are not merged (no unknown-recipe WARN for them), coll:lantern = "off", an INFO note in the
    recipe-check line. Nothing else changes.
  - Config kit KEEP 20 -> 10 (AGENT-BRIEF rule, kit default since 2026-10-05).
  - Review fixes (2026-10-06): the opt-in "auto" recipe rule never adds a Lantern recipe (it could unlock Unique at 50 sap and Rare /
    Legendary at Fire Essence tier I); coll:lantern = "off" instead of a removed key when not managed (a reload that hides TreeSap
    used to freeze SkyyAccessories' locks until a restart).
Existing players: nothing they own changes (no item is touched by either mod); anyone with enough Tree Sap gets the recipes at once.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.6.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.7.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.6"
LF = "\n"
s = raw.decode("utf8").replace("\r\n", LF)
OLD = s
assert 'VERSION = "0.2.6"' in s and "GENERATED by tools/coll_0_2_6_patch.py from the LIVE 0.2.5" in s, "not the live generated 0.2.6"
assert "coll:lantern" not in s and "Skyy_Talisman_Lantern" not in s


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


LAN_WORDS = ["Common", "Uncommon", "Rare", "Epic"]            # SkyyAccessories' id words (LAN_IDS)
LAN_RAR = ["Normal", "Unique", "Rare", "Legendary"]
LAN_RIDS = ["Skyy_Talisman_Lantern_%s_Recipe_Generated_0" % w for w in LAN_WORDS]
LAN_KEYS = ["lantern.tier.%s" % r.lower() for r in LAN_RAR]
LAN_DEF = [1, 3, 5, 8]
LAN_COLL = "TreeSap"


def jarr(xs):
    return "new String[] { " + ", ".join('"%s"' % x for x in xs) + " }"


# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyCollections 0.2.6 - build script (javassist via jpype). GENERATED by tools/coll_0_2_6_patch.py from the LIVE 0.2.5
(build_skyycollections_0.2.5.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.5 was derived from 0.2.4 by
tools/coll_0_2_5_patch.py;''', '''"""SkyyCollections 0.2.7 - build script (javassist via jpype). GENERATED by tools/coll_0_2_7_patch.py from the LIVE 0.2.6
(build_skyycollections_0.2.6.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.6 was derived from 0.2.5 by
tools/coll_0_2_6_patch.py; 0.2.5 from 0.2.4 by tools/coll_0_2_5_patch.py;''')
rep('''0.2.6 (2026-10-05, lean): LEADERBOARDS''', '''0.2.7 (2026-10-06): THE LANTERN RECIPES UNLOCK FROM THE TREE SAP COLLECTION (Skyy 2026-10-05 LOCKED, docs/answered/economy.md; the
  SkyySacks bag-ladder mechanism; SkyyAccessories 0.5.6 is the other half). Normal / Unique / Rare / Legendary Lantern recipes at TreeSap
  tiers 1 / 3 / 5 / 8 (50 / 250 / 1,000 / 10,000 sap; proposed, Skyy confirms) - four new config.properties keys lantern.tier.<rarity>,
  each a Server Setup row (Collections -> Lantern recipes); no file is rewritten (missing keys = the defaults). validate merges them
  into the recipe unlocks, so the tier rows, chat, Unlocked recipes, coll:recipes and coll:fn:where show them. Coins never unlock a
  Lantern (bagRank 9 > any bypass.bagMax; buyable false). Bridge coll:lantern = "TreeSap|1|3|5|8" while the Lanterns are managed
  (SkyyAccessories installed, TreeSap visible), "off" otherwise; SkyyAccessories locks Lanterns only while it is a tier string. The
  opt-in auto recipe rule never adds a Lantern. Lantern tokens in rewards.properties are ignored (WARN) and refused in the Tier rewards
  table. Config kit KEEP 20 -> 10. Full notes: tools/coll_0_2_7_patch.py.
  CHECKED with SkyyCollections/test_skyycollections_0.2.7.py.
0.2.6 (2026-10-05, lean): LEADERBOARDS''')
rep("Run:   python build_skyycollections_0.2.6.py          -> SkyyCollections/SkyyCollections-0.2.6.jar",
    "Run:   python build_skyycollections_0.2.7.py          -> SkyyCollections/SkyyCollections-0.2.7.jar")
rep('VERSION = "0.2.6"', 'VERSION = "0.2.7"')
rep('"[SkyyCollections] 0.2.6 ready (', '"[SkyyCollections] 0.2.7 ready (')

# ---------------------------------------------------------------------------------------------------------------- python constants
rep('''print("registry:", len(REG), "collections,", len(ALL_ITEMS), "items")''', '''print("registry:", len(REG), "collections,", len(ALL_ITEMS), "items")
# 0.2.7 (Skyy 2026-10-05): the Lantern Accessory recipes (SkyyAccessories) unlock from the Tree Sap collection; tiers = config rows
LAN_COLL = "%s"
LAN_RAR = %r
LAN_RIDS = %r
LAN_KEYS = %r
LAN_DEF = %r
_lan = [r for r in REG if r[0] == LAN_COLL]
assert len(_lan) == 1 and _lan[0][1] == "Foraging" and _lan[0][5] == ["Ingredient_Tree_Sap"] and "hidden" not in _lan[0][6], _lan
assert all(1 <= t <= 9 for t in LAN_DEF) and LAN_DEF == sorted(LAN_DEF)''' % (LAN_COLL, LAN_RAR, LAN_RIDS, LAN_KEYS, LAN_DEF))
rep('''assert len(_lan) == 1 and _lan[0][1] == "Foraging" and _lan[0][5] == ["Ingredient_Tree_Sap"] and "hidden" not in _lan[0][6], _lan
assert all(1 <= t <= 9 for t in LAN_DEF) and LAN_DEF == sorted(LAN_DEF)''', '''assert len(_lan) == 1 and _lan[0][1] == "Foraging" and _lan[0][5] == ["Ingredient_Tree_Sap"] and "hidden" not in _lan[0][6], _lan
assert all(1 <= t <= 9 for t in LAN_DEF) and LAN_DEF == sorted(LAN_DEF)
print("lantern recipes: %s at %s tiers %s" % ("/".join(LAN_RAR), LAN_COLL, "/".join(str(t) for t in LAN_DEF)))''')
# the curve check needs CURVES (defined after the registry): assert the Standard curve reaches the Legendary tier
rep('''TIER_COINS = [50, 100, 200, 400, 800, 1500, 3000, 6000, 12000, 25000]''', '''assert len(CURVES[_lan[0][2]]) >= max(LAN_DEF), "TreeSap's curve is shorter than the Legendary Lantern tier"
TIER_COINS = [50, 100, 200, 400, 800, 1500, 3000, 6000, 12000, 25000]''')
# the default config.properties (a fresh install only; an existing file is never rewritten - missing keys = these defaults)
rep('''    "bridge.add.felled=true",
]''', '''    "bridge.add.felled=true",
    "# Lantern Accessory recipes (SkyyAccessories): the Tree Sap collection tier that unlocks each rarity's recipe (1-20; coins never buy",
    "# them). Without SkyyAccessories these do nothing.",
] + ["%s=%d" % kv for kv in zip(LAN_KEYS, LAN_DEF)]''')

# ---------------------------------------------------------------------------------------------------------------- CollReg fields
rep('''          "public static volatile int BYP_BAGMAX = 2;",''', '''          "public static volatile int BYP_BAGMAX = 2;",
          "public static volatile int[] LAN_TIER = new int[] { %s };",
          "public static volatile boolean LAN_ON = false;",
          "public static volatile String LAN_NOTE = \\"\\";",
          "public static final String LAN_COLL = \\"%s\\";",
          "public static final String[] LAN_RID = %s;",
          "public static final String[] LAN_KEY = %s;",
          "public static final int[] LAN_DEF = new int[] { %s };",''' % (
    ", ".join(str(t) for t in LAN_DEF), LAN_COLL, jarr(LAN_RIDS).replace('"', '\\"'), jarr(LAN_KEYS).replace('"', '\\"'),
    ", ".join(str(t) for t in LAN_DEF)))

# ---------------------------------------------------------------------------------------------------------------- CollUtil
rep('''# 0.2.3: bag rank of a recipe id (spec 7): Skyy_Sack_*_Small 1, _Medium 2, _Rare 3, _Large 4, Skyy_Sack_Omni 5, anything else 0 (never limited)
M(util, r"""
public static int bagRank(String rid) {
  if (rid == null) return 0;
  String id = rid.trim();''', '''# 0.2.7: a SkyyAccessories Lantern recipe (or item) id - Skyy_Talisman_Lantern_Common .. _Epic (+ _Recipe_Generated_0)
M(util, r"""
public static boolean isLantern(String rid) {
  return rid != null && rid.trim().startsWith("Skyy_Talisman_Lantern_");
}""")
M(util, r"""
public static String lanRarity(String w) {
  if ("Common".equals(w)) return "Normal";
  if ("Uncommon".equals(w)) return "Unique";
  if ("Rare".equals(w)) return "Rare";
  if ("Epic".equals(w)) return "Legendary";
  return w;
}""")
# 0.2.3: bag rank of a recipe id (spec 7): Skyy_Sack_*_Small 1, _Medium 2, _Rare 3, _Large 4, Skyy_Sack_Omni 5, anything else 0 (never limited)
# 0.2.7: a Lantern recipe = 9, above every bypass.bagMax word (legendary = 4): every bought-tier path skips it - coins never unlock one
M(util, r"""
public static int bagRank(String rid) {
  if (rid == null) return 0;
  if (isLantern(rid)) return 9;
  String id = rid.trim();''')
rep('''  if (id.startsWith("Skyy_Sack_") && p.length >= 4) return rarityOf(p[3]) + " " + p[2] + " Bag";''',
    '''  if (id.startsWith("Skyy_Sack_") && p.length >= 4) return rarityOf(p[3]) + " " + p[2] + " Bag";
  if (id.startsWith("Skyy_Talisman_Lantern_") && p.length == 4) return lanRarity(p[3]) + " Lantern Accessory";''')

# ---------------------------------------------------------------------------------------------------------------- CollReg: config, merge
rep('''M(reg, r"""
public static String loadConfig() {''', '''# 0.2.7: lantern.tier.<rarity> (1-20; missing = the default, a bad value = the default + WARN). A tier past the collection's ladder is
# clamped when merged (lanMerge), so this only reads.
M(reg, r"""
public static String loadLan(java.util.Properties p) {
  int[] t = new int[4];
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < 4; k++) {
    t[k] = LAN_DEF[k];
    String v = p.getProperty(LAN_KEY[k]);
    if (v != null) {
      int n = -1;
      try { n = Integer.parseInt(v.trim()); } catch (Throwable e) { n = -1; }
      if (n >= 1 && n <= 20) t[k] = n;
      else @PKG@.CollUtil.warn("config.properties: " + LAN_KEY[k] + "=" + @PKG@.CollUtil.clip(v.trim(), 40) + " is not a tier 1-20 - using " + LAN_DEF[k]);
    }
    if (k > 0) sb.append('/');
    sb.append(t[k]);
  }
  LAN_TIER = t;
  return sb.toString();
}""")
M(reg, r"""
public static String loadConfig() {''')
rep('''  BYP_BAGMAX = bi;
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS + " bagMax=" + bi + " felled=" + felled;''',
    '''  BYP_BAGMAX = bi;
  String lt = loadLan(p);
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS + " bagMax=" + bi + " felled=" + felled + " lantern=" + lt;''')
rep('''# after the asset stores loaded (start(), reload): recipe ids -> RECIPES["c.t"], registry item / icon check. Logged, never fatal.
M(reg, r"""
public static synchronized String validate() {''', '''# 0.2.7: the Lantern recipe ids the asset store knows (SkyyAccessories installed = all four; missing = none)
M(reg, r"""
public static java.util.HashSet lanPresent() {
  java.util.HashSet out = new java.util.HashSet();
  for (int k = 0; k < LAN_RID.length; k++) {
    try { if (@CRR@.getAssetMap().getAsset(LAN_RID[k]) != null) out.add(LAN_RID[k]); } catch (Throwable t) { }
  }
  return out;
}""")
# 0.2.7: merge the Lantern recipes into out ("c.t" -> String[]) at the lantern.tier rows of the TreeSap collection, for the ids in have.
# LAN_ON = at least one merged (then coll:lantern is published); a tier past the ladder uses its last tier (WARN); no / hidden TreeSap
# collection = none merged (WARN: the Lanterns then stay craftable in SkyyAccessories). Returns the note for the recipe-check line.
M(reg, r"""
public static String lanMerge(java.util.HashMap out, @PKG@.RegData R, java.util.Set have, int[] eff) {
  LAN_ON = false;
  if (have == null || have.isEmpty()) return "Lantern recipes: SkyyAccessories not installed";
  if (R == null) return "Lantern recipes: no registry";
  Object ci = R.byId.get(LAN_COLL.toLowerCase());
  if (!(ci instanceof Integer) || R.hidden[((Integer) ci).intValue()]) {
    @PKG@.CollUtil.warn("no visible " + LAN_COLL + " collection in collections.properties - the Lantern recipes are not unlocked by collections (SkyyAccessories keeps every Lantern craftable)");
    return "Lantern recipes: no " + LAN_COLL + " collection";
  }
  int c = ((Integer) ci).intValue();
  int mx = maxTier(R, c);
  int[] t = LAN_TIER;
  int n = 0;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < 4; k++) {
    int tk = t[k];
    if (tk > mx) {
      @PKG@.CollUtil.warn(LAN_KEY[k] + "=" + tk + " but " + R.name[c] + " has " + mx + " tiers - the recipe unlocks at tier " + mx);
      tk = mx;
    }
    if (tk < 1) tk = 1;
    eff[k] = tk;
    if (k > 0) sb.append('/');
    sb.append(tk);
    if (!have.contains(LAN_RID[k])) continue;
    String key = c + "." + tk;
    String[] cur = (String[]) out.get(key);
    boolean dup = false;
    if (cur != null) for (int i = 0; i < cur.length; i++) if (cur[i].equals(LAN_RID[k])) dup = true;
    if (dup) continue;
    String[] nx = new String[cur == null ? 1 : cur.length + 1];
    if (cur != null) for (int i = 0; i < cur.length; i++) nx[i] = cur[i];
    nx[nx.length - 1] = LAN_RID[k];
    out.put(key, nx);
    n++;
  }
  LAN_ON = n > 0;
  return "Lantern recipes at " + R.name[c] + " " + sb.toString() + " (" + n + " merged)";
}""")
# 0.2.7: coll:lantern = "TreeSap|n|u|r|l" while the Lanterns are managed (SkyyAccessories 0.5.6 locks them only while it is there);
# review fix: "off" (not a removed key) when they are not - so a reload that hides TreeSap frees every Lantern in SkyyAccessories at
# once instead of freezing it in "hold" (a missing key after a seen one = a shutdown / reload in progress)
M(reg, r"""
public static void lanPublish(int[] eff) {
  try {
    java.util.Map b = @PKG@.CollUtil.bridge();
    if (LAN_ON) b.put("coll:lantern", LAN_COLL + "|" + eff[0] + "|" + eff[1] + "|" + eff[2] + "|" + eff[3]);
    else b.put("coll:lantern", "off");
  } catch (Throwable t) { }
}""")
# after the asset stores loaded (start(), reload): recipe ids -> RECIPES["c.t"], registry item / icon check. Logged, never fatal.
M(reg, r"""
public static synchronized String validate() {''')
rep('''  int ok = 0; int miss = 0; int excl = 0;
  StringBuilder ms = new StringBuilder();''', '''  int ok = 0; int miss = 0; int excl = 0; int lanIgn = 0;
  StringBuilder ms = new StringBuilder();
  StringBuilder lg = new StringBuilder();''')
rep('''        String rid = toks[i].substring(7).trim();
        @CRR@ rr = null;
        try { rr = (@CRR@) @CRR@.getAssetMap().getAsset(rid); } catch (Throwable t2) { }
        if (rr == null) { miss++; if (ms.length() < 400) ms.append(rid).append(' '); continue; }''',
    '''        String rid = toks[i].substring(7).trim();
        if (@PKG@.CollUtil.isLantern(rid)) { lanIgn++; if (lg.length() < 300) lg.append(R.id[c]).append('.').append(t).append(' '); continue; }
        @CRR@ rr = null;
        try { rr = (@CRR@) @CRR@.getAssetMap().getAsset(rid); } catch (Throwable t2) { }
        if (rr == null) { miss++; if (ms.length() < 400) ms.append(rid).append(' '); continue; }''')
rep('''  if (uk.length() > 0) @PKG@.CollUtil.warn("rewards.properties names unknown collection(s): " + uk);
  RECIPES = out;
  VALIDATED = true;
  String res = ok + " recipe unlock(s)";''', '''  if (uk.length() > 0) @PKG@.CollUtil.warn("rewards.properties names unknown collection(s): " + uk);
  if (lanIgn > 0) @PKG@.CollUtil.warn("rewards.properties: " + lanIgn + " Lantern recipe token(s) ignored (" + lg.toString().trim() + ") - the Lantern recipes unlock at the Server Setup rows Collections > Lantern recipes (config.properties lantern.tier.*)");
  int[] eff = new int[4];
  String ln = lanMerge(out, R, lanPresent(), eff);
  LAN_NOTE = ln;
  RECIPES = out;
  VALIDATED = true;
  lanPublish(eff);
  String res = ok + " recipe unlock(s)";''')
rep('''  if (excl > 0) res = res + ", " + excl + " on excluded benches skipped";
  return res;''', '''  if (excl > 0) res = res + ", " + excl + " on excluded benches skipped";
  if (lanIgn > 0) res = res + ", " + lanIgn + " Lantern token(s) in rewards.properties ignored";
  return res + "; " + ln;''')

# ---------------------------------------------------------------------------------------------------------------- coin rule
# review fix: the opt-in "auto" rule (every recipe whose collection inputs reached tier I) never adds a Lantern - only the Tree Sap rows do
rep('''      if (anyTier && !blocked) { String rid = r.getId(); if (rid != null) out.add(rid); }''',
    '''      if (anyTier && !blocked) { String rid = r.getId(); if (rid != null && !@PKG@.CollUtil.isLantern(rid)) out.add(rid); }''')
rep('''    if (bought && !free && @PKG@.CollUtil.bagRank(rs[i]) > BYP_BAGMAX) sb.append(" (gather this tier)");''',
    '''    if (bought && (!free || @PKG@.CollUtil.isLantern(rs[i])) && @PKG@.CollUtil.bagRank(rs[i]) > BYP_BAGMAX) sb.append(" (gather this tier)");''')
rep('''public static boolean buyable(String rid, boolean free) {
  if (!@PKG@.CollUtil.isBag(rid)) return true;''', '''public static boolean buyable(String rid, boolean free) {
  if (@PKG@.CollUtil.isLantern(rid)) return false;   // 0.2.7: coins never unlock a Lantern recipe
  if (!@PKG@.CollUtil.isBag(rid)) return true;''')

rep('''    else if (!free) { if (no.length() > 0) no.append(" - "); no.append(nm); }''',
    '''    else if (!free || @PKG@.CollUtil.isLantern(rs[i])) { if (no.length() > 0) no.append(" - "); no.append(nm); }''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup
rep('''KIT_CATS = [("curves", "Curves"), ("rewards", "Rewards"), ("bags", "Magic Bags"), ("bypass", "Coin unlocks"), ("rules", "Rules"),
            ("registry", "Registry")]   # 0.2.3: + Magic Bags''', '''KIT_CATS = [("curves", "Curves"), ("rewards", "Rewards"), ("bags", "Magic Bags"), ("lantern", "Lantern recipes"), ("bypass", "Coin unlocks"),
            ("rules", "Rules"), ("registry", "Registry")]   # 0.2.3: + Magic Bags; 0.2.7: + Lantern recipes''')
rep('''# 0.2.3: one read-only row per bag type = where its Normal / Unique / Rare / Legendary recipes unlock (live from the rewards table)''',
    '''# 0.2.7: the Tree Sap tier of each Lantern recipe (SkyyAccessories) - one int row per rarity, checked against TreeSap's ladder
for _i, _r in enumerate(LAN_RAR):
    KIT_ROWS.append((LAN_KEYS[_i], "%s Lantern: Tree Sap tier" % _r, "lantern", "int", str(LAN_DEF[_i]), "1", "20", "step=1", "", "live",
                     "The %s Lantern recipe unlocks at this Tree Sap collection tier. Coins never buy it." % _r,
                     "reload@config.properties:%s;check=CollKit.checkLanTier" % LAN_KEYS[_i]))
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in KIT_ROWS if _r[2] == "lantern")
# 0.2.3: one read-only row per bag type = where its Normal / Unique / Rare / Legendary recipes unlock (live from the rewards table)''')
rep('''                RELOAD="CollKit.reloadAll", KEEP=20, ITEMS=ITEM_IDS,''', '''                RELOAD="CollKit.reloadAll", KEEP=10, ITEMS=ITEM_IDS,''')
rep('''M(ckit, r"""
public static String idList(String value, String extra, String what) {''', '''# 0.2.7: a Lantern tier row - a whole number from 1 to the TreeSap collection's last tier
M(ckit, r"""
public static String checkLanTier(String key, String value) {
  int n = -1;
  try { n = Integer.parseInt(String.valueOf(value).trim()); } catch (Throwable t) { n = -1; }
  int mx = 20;
  try {
    @PKG@.RegData R = @PKG@.CollReg.D;
    Object ci = R == null ? null : R.byId.get(@PKG@.CollReg.LAN_COLL.toLowerCase());
    if (ci instanceof Integer) mx = @PKG@.CollReg.maxTier(R, ((Integer) ci).intValue());
  } catch (Throwable t) { }
  if (n < 1 || n > mx) return "Must be a Tree Sap tier from 1 to " + mx + ".";
  return null;
}""")
M(ckit, r"""
public static String idList(String value, String extra, String what) {''')
rep('''    if (rid.length() == 0) return "recipe: needs a recipe id, like recipe:Tool_Hoe_Copper_Recipe_Generated_0.";''',
    '''    if (rid.length() == 0) return "recipe: needs a recipe id, like recipe:Tool_Hoe_Copper_Recipe_Generated_0.";
    if (@PKG@.CollUtil.isLantern(rid)) return "Lantern recipes unlock at the Lantern recipes rows (Tree Sap tiers), not here.";''')

# ---------------------------------------------------------------------------------------------------------------- shutdown
rep('''    b.remove("coll:fn:count"); b.remove("coll:fn:tier"); b.remove("coll:fn:add"); b.remove("coll:fn:where"); b.remove("coll:list");''',
    '''    b.remove("coll:fn:count"); b.remove("coll:fn:tier"); b.remove("coll:fn:add"); b.remove("coll:fn:where"); b.remove("coll:list");
    b.remove("coll:lantern");   // 0.2.7''')
rep('''    coll:epoch:<uuid>, coll:list, coll:fn:count, coll:fn:tier, coll:fn:add (sources in bridge.add.sources, default skills:double).''',
    '''    coll:epoch:<uuid>, coll:list, coll:fn:count, coll:fn:tier, coll:fn:add (sources in bridge.add.sources, default skills:double);
    0.2.7: coll:lantern = "TreeSap|n|u|r|l" while the Lantern recipes are managed (SkyyAccessories 0.5.6 locks them only then), else "off".''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("public static boolean isLantern(String rid)") < s.index("public static int bagRank(String rid)") < s.index("public static String prettyItem(")
assert s.index("public static String loadLan(") < s.index("public static String loadConfig()")
assert s.index("public static String lanMerge(") < s.index("public static synchronized String validate()")
assert s.index("public static String checkLanTier(") < s.index("public static String rewardToken(")
assert "KEEP=20" not in s and s.count("coll:lantern") >= 4
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyCollections 0.2.6 - build script (javassist via jpype). GENERATED by tools/coll_0_2_6_patch.py from the LIVE 0.2.5',
    "(build_skyycollections_0.2.5.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.5 was derived from 0.2.4 by",
    "tools/coll_0_2_5_patch.py; 0.2.4 from 0.2.3 by tools/coll_0_2_4_patch.py; 0.2.3 from 0.2.2 by tools/coll_0_2_3_patch.py; 0.2.2 from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2",
    "Run:   python build_skyycollections_0.2.6.py          -> SkyyCollections/SkyyCollections-0.2.6.jar",
    'VERSION = "0.2.6"',
    "]",
    "  return \"migrate=\" + MIGRATE + \" auto=\" + AUTO + \" bypass=\" + BYPASS + \" bagMax=\" + bi + \" felled=\" + felled;",
    "  int ok = 0; int miss = 0; int excl = 0;",
    "  return res;",
    "    else if (!free) { if (no.length() > 0) no.append(\" - \"); no.append(nm); }",
    "    if (bought && !free && @PKG@.CollUtil.bagRank(rs[i]) > BYP_BAGMAX) sb.append(\" (gather this tier)\");",
    "KIT_CATS = [(\"curves\", \"Curves\"), (\"rewards\", \"Rewards\"), (\"bags\", \"Magic Bags\"), (\"bypass\", \"Coin unlocks\"), (\"rules\", \"Rules\"),",
    "            (\"registry\", \"Registry\")]   # 0.2.3: + Magic Bags",
    "                RELOAD=\"CollKit.reloadAll\", KEEP=20, ITEMS=ITEM_IDS,",
    "    coll:epoch:<uuid>, coll:list, coll:fn:count, coll:fn:tier, coll:fn:add (sources in bridge.add.sources, default skills:double).",
    "      if (anyTier && !blocked) { String rid = r.getId(); if (rid != null) out.add(rid); }",
}
_bad = [ln for ln in _gone if ln not in _ALLOWED and "0.2.6 ready (" not in ln]
assert not _bad, "0.2.6 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.2.6 had %d)" % (s.count(LF), OLD.count(LF)))
