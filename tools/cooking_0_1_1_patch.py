"""Derive SkyyCooking/build_skyycooking_0.1.1.py from build_skyycooking_0.1.py (rep(old, new) with asserted anchors, newline-agnostic;
0.1 stays untouched and its CRLF line endings are kept in 0.1.1).

0.1.1 (Skyy 2026-09-24, HANDOFF "Feedback on the build round"): the CAMPFIRE ACCESSORY comes back for quick inventory cooking -
"just reduce the XP by half when using the campfire accessory. and reduce the buffs added by cooking skill by 0.25. so you get 50% xp
and 75% of your normal buffs when using it, so its an emergency cook". This mod's side of it:
 - bridge Function cook:fn:campfire (SkyySacks calls it on the world thread when a player crafts a Campfire dish in /craft):
   Object[]{UUID, String recipeOrOutputId, Number crafts [, String expectKey [, Boolean creative]]} -> String item id to give
   (graded "Skyy_Cook_<dish>_G<c>" or the plain dish id; null = not a campfire dish), paying Cooking XP x campfire.xpFactor through
   skill:fn:addxp. Grade c = the highest Grade whose multiplier M(c) = 2^(c/5) is <= 1 + campfire.buffFactor x (M(G) - 1), G = the
   Grade a Cooking Bench guarantees (level / 10 + Master Chef). Reuses the 0.1 Grade assets (no new asset set).
 - bridge String cook:campfire:ids = the dish ids it accepts (every vanilla Campfire recipe output, build-checked).
 - cooking.properties campfire.buffFactor=0.75, campfire.xpFactor=0.5 (appended once to a 0.1 file).
 - /cookadmin campfire <dish> <count> (admin test of the bridge), /cooking + Skills Stats page lines.
 - build self-checks: campfire outputs = graded T1 dishes with XP and Grade assets, no effect cap binds on them, mapping table
   asserted, and the COMPILED Java campGrade is run through jpype against the Python mirror.
Full contract: the 0.1.1 docstring section of the generated script.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.py")
dst = os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.1.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


# ---------------------------------------------------------------------------------------------------------------- docstring
rep('''"""SkyyCooking 0.1 - build script (javassist via jpype). NEW mod, never deployed: edit this file directly (no patch script yet).
Run:   python build_skyycooking_0.1.py            -> SkyyCooking/SkyyCooking-0.1.jar
       python build_skyycooking_0.1.py --deploy   -> also copies to Mods/SkyyCooking.jar (ONLY with Skyy's OK - HANDOFF deploy rule)
''', '''"""SkyyCooking 0.1.1 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.py by tools/cooking_0_1_1_patch.py:
edit the patch (or 0.1) and re-run it, not this file. 0.1 was never deployed.
Run:   python build_skyycooking_0.1.1.py            -> SkyyCooking/SkyyCooking-0.1.1.jar
       python build_skyycooking_0.1.1.py --deploy   -> also copies to Mods/SkyyCooking.jar (ONLY with Skyy's OK - HANDOFF deploy rule)

0.1.1 = THE CAMPFIRE ACCESSORY COMES BACK (Skyy 2026-09-24, HANDOFF "Feedback on the build round"): "add the campfire accessory back for
 quick inventory cooking as it already limits what you can make ... 50% xp and 75% of your normal buffs when using it, so its an
 emergency cook". Cooking a Campfire dish THROUGH THE ACCESSORY (SkyySacks' /craft page, instant) gives a graded dish whose Cooking-skill
 bonus is x campfire.buffFactor (0.75) and pays Cooking XP x campfire.xpFactor (0.5). NO new assets: the 0.1 Grade 1-12 dishes are
 reused. The placed vanilla Campfire is unchanged (plain food, no XP). The Alchemy Bench and Cooking Bench accessories stay retired.
 Everything 0.1 does is unchanged.
 GRADE: G = the Grade a Cooking Bench guarantees right now = min(floor(Cooking level / 10), 10) + 1 if Master Chef (CMaster) >= 1,
  clamped to maxGrade (the number cook:fn:grade and /cooking show). Target multiplier T = 1 + buffFactor x (M(G) - 1), M(g) = 2^(g/5).
  The dish comes out at c = the highest Grade 0..G with M(c) <= T (the existing Grade whose multiplier does not exceed the target).
  No chance rolls (Gourmet, Signature Dish, ...) and no tree extras (Batch Cook, Frugal) through the accessory: the emergency cook gets
  the guaranteed Grade only. The 3 campfire dishes are T1 dishes and hit no effect cap, so M is their real heal / buff strength and
  duration factor (build self-check).
  Default table (buffFactor 0.75), Cooking Bench Grade -> campfire-accessory Grade (printed and asserted by the build):
   G0->0  G1->0  G2->1  G3->2  G4->3  G5->4  G6->4  G7->5  G8->6  G9->7  G10->8  G11->9  G12->10
 BRIDGE (new; published in setup, removed in shutdown):
  cook:fn:campfire   java.util.function.Function, apply(Object[] a) -> String or null
     a[0] java.util.UUID   the crafting player (required)
     a[1] String           the CraftingRecipe id SkyySacks crafted (a Campfire-bench recipe, String.valueOf(recipe.getId())) OR the
                           dish's output item id (one of cook:campfire:ids) (required). A Cooking Bench recipe id is NOT accepted.
     a[2] Number           finished crafts (1 craft = 1 dish), required. >= 1 = a real craft: pays XP (at most 10,000 crafts per call).
                           <= 0 = PREVIEW: returns the id a craft would give now; no XP, no chat, no cap use.
     a[3] String           OPTIONAL expectKey = the profile key (pkey) the caller resolved when the craft started. null or absent = no
                           check. Different from the current key -> plain id and no XP.
     a[4] Boolean          OPTIONAL creative flag (the player's GameMode == Creative). Absent = read from the player's live entity (only
                           possible on that player's world thread).
     RETURNS the item id to hand out INSTEAD of the recipe's primary output id, same quantity (crafts x 1): "Skyy_Cook_<dish>_G<c>" or
      the plain dish id. null = not a campfire dish, malformed arguments or an internal error: give your normal (plain) output.
     THREAD: the player's world thread (SkyySacks' craft page handleDataEvent), after the materials were removed. No disk I/O, no ECS
      writes. The XP grant happens inside the call (skill:fn:addxp, which queues it on the world thread).
     XP: base = round(xp.<dish> x crafts x campfire.xpFactor) (defaults: Cooked Wildmeat 1,600 -> 800, Grilled Fish 2,000 -> 1,000,
      Roast Vegetable 1,200 -> 600 per dish) -> this mod's maxXpPerMinute window (shared with bench cooking; over it the XP is dropped,
      the dish still comes out graded) -> x xpMultiplier -> skill:fn:addxp(Object[]{UUID, "Cooking", Long, "cook:campfire:<dish>", pkey})
      in parts of <= 400,000 (SkyySkills adds the Cooking tree Wisdom bonus there). SkyySkills 0.4's skill:fn:craftxp pays 0 for
      Campfire recipes (RecipeXp.classify -> null), so SkyySacks may keep calling it for every craft: no double XP.
     PLAIN id + NO XP (the bench rules): enabled=false; profile:busy:<uuid>; expectKey differs; creative (flag TRUE or read as Creative,
      unless creativeGrades=true); game mode unreadable and no flag passed; SkyySkills missing (no skill:fn:level).
     PLAIN id + XP: campfire Grade 0 (low Cooking level), the dish removed from graded=, or its Grade asset not loaded.
     CHAT: after a real craft, one hint per session (and again when the campfire Grade rises), only with messages=true.
  cook:campfire:ids  String "Food_Wildmeat_Cooked,Food_Fish_Grilled,Food_Vegetable_Cooked" = the dish ids cook:fn:campfire accepts (every
      vanilla Campfire recipe output, build-checked). SkyySacks shows exactly the Campfire-bench recipes whose primary output is listed.
 CONFIG (cooking.properties; appended once to a 0.1 file that lacks both lines): campfire.buffFactor=0.75, campfire.xpFactor=0.5
  (each 0..1, clamped with a log line; /cookadmin reload re-reads them).
 COMMAND: /cookadmin campfire <dish> <count 0-64> (skyycooking.admin) runs the bridge exactly as /craft would, on the admin's world
  thread, and gives count x the returned id (no materials used) + the XP; count 0 = preview. /cooking and the Skills Stats page show
  the campfire Grade and XP share.
 NOT IN THIS MOD: SkyyAccessories has to un-retire Skyy_Accessory_Campfire_T1 and SkyySacks has to show its tab again (only the
  cook:campfire:ids recipes) and call cook:fn:campfire for them. Until then nothing calls the bridge (test it with /cookadmin campfire).
''')
rep('''        cook:prefix     "Skyy_Cook_Food_" (SkyySacks catOf -> Farming bag; Bazaar)
''', '''        cook:prefix     "Skyy_Cook_Food_" (SkyySacks catOf -> Farming bag; Bazaar)
        cook:fn:campfire / cook:campfire:ids   0.1.1 Campfire accessory - exact contract in the 0.1.1 section at the top
''')
rep(''' /cookadmin give <dish> <grade> (5 dishes, grade 0-12, dish = Food_Pie_Meat or pie_meat), /cookadmin reload: requirePermission''',
    ''' /cookadmin give <dish> <grade> (5 dishes, grade 0-12, dish = Food_Pie_Meat or pie_meat), /cookadmin campfire <dish> <count> (0.1.1),
 /cookadmin reload: requirePermission''')
rep(''' plain, no XP; second player eats your Grade 5 pie -> Grade 5 effects; fresh profile -> plain food; SkyyTrees Master Chef -> +1 Grade.
''', ''' plain, no XP; second player eats your Grade 5 pie -> Grade 5 effects; fresh profile -> plain food; SkyyTrees Master Chef -> +1 Grade.
 0.1.1: log "[SkyyCooking] 0.1.1 ready ... Campfire accessory bridge cook:fn:campfire"; cooking.properties of a 0.1 run gains the
 campfire.* lines once; at Cooking 50 /cookadmin campfire wildmeat_cooked 0 -> "bench Grade 5 -> campfire Grade 4 ... would give
 Skyy_Cook_Food_Wildmeat_Cooked_G4" and no XP; /cookadmin campfire wildmeat_cooked 2 -> 2 x "Cooked Wildmeat (Grade 4)" + 1,600 Cooking XP
 (half of 2 x 1,600) + the one-time campfire chat hint; at Cooking 100 -> Grade 8; at Cooking 0-19 -> plain dish + half XP; creative ->
 plain + 0 XP; campfire.xpFactor=1.0 + /cookadmin reload -> full XP; placed Campfire still plain + no XP.
''')
rep('VERSION = "0.1"', 'VERSION = "0.1.1"')

# ---------------------------------------------------------------------------------------------------------------- build-time: campfire dishes, mapping table, config lines
CAMP_PY = r'''# =====================================================================================================================
# 0.1.1 CAMPFIRE ACCESSORY (Skyy 2026-09-24): /craft (SkyySacks) cooks the Campfire dishes instantly through the Campfire accessory -
# an emergency cook: the Cooking-skill part of the Grade bonus x campfire.buffFactor, Cooking XP x campfire.xpFactor. Reuses the
# Grade 1-12 assets generated above (no new asset set).
# =====================================================================================================================
CAMP_BUFF_DEF, CAMP_XP_DEF = 0.75, 0.5
_camp_found = []
for rid, r in ALLREC:
    if not any(isinstance(b, dict) and b.get("Id") == "Campfire" for b in (r.get("BenchRequirement") or [])): continue
    po = r.get("PrimaryOutput")
    outs = [po["ItemId"]] if isinstance(po, dict) and po.get("ItemId") else [o.get("ItemId") for o in (r.get("Output") or []) if o.get("ItemId")]
    if not outs: outs = [rid]
    for o in outs:
        if o not in _camp_found: _camp_found.append(o)
CAMP_DISHES = [d for d in DISHES if d in _camp_found]
if sorted(CAMP_DISHES) != sorted(_camp_found):
    raise SystemExit("self-check 0.1.1: a vanilla Campfire recipe makes something that is not a graded dish: %s" % sorted(set(_camp_found) - set(CAMP_DISHES)))
if CAMP_DISHES != ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked"]:
    raise SystemExit("self-check 0.1.1: the vanilla Campfire recipe list changed (%s) - re-check the docstring, texts and XP" % CAMP_DISHES)
def _bonus(e):
    if e.get("RawStatModifiers"): return list(e["RawStatModifiers"].values())[0][0]["Amount"] - 1.0
    return e["StatModifiers"]["Health"]
for d in CAMP_DISHES:
    if DISH_TIER[d] != 1 or XP.get(d, 0) <= 0:
        raise SystemExit("self-check 0.1.1: campfire dish %s must be a T1 graded dish with Cooking XP (tier %s, xp %s)" % (d, DISH_TIER[d], XP.get(d)))
    for g in range(1, GEN_MAX + 1):
        if dish_id(d, g) not in G_ITEMS: raise SystemExit("self-check 0.1.1: no Grade asset " + dish_id(d, g))
    # its heal and buffs scale by exactly M(g) (no cap binds on T1 numbers), so the multiplier the mapping uses is the real one
    for f in DISH_FX[d]:
        b = f[1] if f[0] == "I" else "%s_Buff_T%d" % (f[1], f[2])
        e0 = scale_effect(b, 0)
        for g in range(1, GEN_MAX + 1):
            eg = scale_effect(b, g)
            if abs(_bonus(eg) - _bonus(e0) * SF(g)) > 0.0002 or (e0.get("Duration", 0) > 0.5 and abs(eg["Duration"] - e0["Duration"] * DF(g)) > 0.01):
                raise SystemExit("self-check 0.1.1: %s Grade %d of %s hits a cap - the campfire mapping would not be x%.2f" % (b, g, d, SF(g)))
def camp_grade(g, f):
    """Python mirror of Cook.campGrade (Java) - the build runs the compiled one against this"""
    g = max(0, min(int(g), GEN_MAX))
    if g <= 0 or f <= 0.0: return 0
    if f >= 1.0: return g
    target = 1.0 + f * (M(g) - 1.0) + 1e-9
    c = 0
    for k in range(1, g + 1):
        if M(k) <= target: c = k
    return c
CAMP_TABLE = [camp_grade(g, CAMP_BUFF_DEF) for g in range(GEN_MAX + 1)]
for g, c in enumerate(CAMP_TABLE):
    tg = 1.0 + CAMP_BUFF_DEF * (M(g) - 1.0)
    assert c <= g and M(c) <= tg + 1e-9 and (c == g or M(c + 1) > tg + 1e-9), (g, c)
    assert g == 0 or CAMP_TABLE[g] >= CAMP_TABLE[g - 1], CAMP_TABLE
if CAMP_TABLE != [0, 0, 1, 2, 3, 4, 4, 5, 6, 7, 8, 9, 10]:
    raise SystemExit("self-check 0.1.1: campfire Grade table changed: %s (update the docstring table)" % CAMP_TABLE)
print("campfire accessory (buffFactor %s, xpFactor %s), bench Grade -> campfire Grade: " % (CAMP_BUFF_DEF, CAMP_XP_DEF) +
      ", ".join("G%d x%.2f -> G%d x%.2f (target x%.2f)" % (g, M(g), c, M(c), 1.0 + CAMP_BUFF_DEF * (M(g) - 1.0)) for g, c in enumerate(CAMP_TABLE)))
print("campfire XP per dish: " + ", ".join("%s %d -> %d" % (d, XP[d], int(round(XP[d] * CAMP_XP_DEF))) for d in CAMP_DISHES))
CAMP_LINES = [
    "# Campfire ACCESSORY (SkyyCooking 0.1.1): the /craft page (SkyySacks) cooks " + ", ".join(CAMP_DISHES) + " instantly - an emergency cook.",
    "# campfire.buffFactor = share of the Cooking-skill part of the Grade bonus: the dish comes out at the highest Grade whose multiplier is",
    "# <= 1 + buffFactor x (the Cooking Bench multiplier - 1). %s: bench Grade 5 (x%.2f) -> Grade %d (x%.2f), Grade 10 (x%.2f) -> Grade %d (x%.2f). 0..1"
    % (CAMP_BUFF_DEF, M(5), CAMP_TABLE[5], M(CAMP_TABLE[5]), M(10), CAMP_TABLE[10], M(CAMP_TABLE[10])),
    "campfire.buffFactor=%s" % repr(CAMP_BUFF_DEF),
    "# campfire.xpFactor = share of the Cooking XP the same dish pays at a Cooking Bench (its xp.<dish> line). 0..1",
    "campfire.xpFactor=%s" % repr(CAMP_XP_DEF)]
CAMP_BLOCK_TEXT = "\n" + "\n".join(CAMP_LINES) + "\n"

'''
rep("# ---- the generated cooking.properties (written on first run; comments must stay on their own lines)",
    CAMP_PY + "# ---- the generated cooking.properties (written on first run; comments must stay on their own lines)")
rep('''      "graded=" + ",".join(DISHES),
''', '''      "graded=" + ",".join(DISHES)] + CAMP_LINES + [
''')

# ---------------------------------------------------------------------------------------------------------------- class creation
rep('sfn  = pool.makeClass(PKG + ".CookStatsFn")',
    'sfn  = pool.makeClass(PKG + ".CookStatsFn")' + LF + 'cfn  = pool.makeClass(PKG + ".CookCampFn")')
rep('rcmd = pool.makeClass(PKG + ".CookReloadCmd", pool.get(APC))',
    'rcmd = pool.makeClass(PKG + ".CookReloadCmd", pool.get(APC))' + LF + 'fcmd = pool.makeClass(PKG + ".CookCampCmd", pool.get(APC))')

# ---------------------------------------------------------------------------------------------------------------- CookCfg
rep('F(cfg, "public static final String DEFAULTS = %s;" % json.dumps(DEFAULTS_TEXT))',
    'F(cfg, "public static final String DEFAULTS = %s;" % json.dumps(DEFAULTS_TEXT))' + LF + r'''# 0.1.1 Campfire accessory
F(cfg, "public static final String[] CAMP = %s;" % jstr_arr(CAMP_DISHES))
F(cfg, "public static final double[] MUL = %s;" % jdbl_arr([M(g) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final double DEF_CAMP_BUFF = %s;" % repr(CAMP_BUFF_DEF))
F(cfg, "public static final double DEF_CAMP_XP = %s;" % repr(CAMP_XP_DEF))
F(cfg, "public static volatile double CAMP_BUFF = %s;" % repr(CAMP_BUFF_DEF))
F(cfg, "public static volatile double CAMP_XP = %s;" % repr(CAMP_XP_DEF))
F(cfg, "public static final String CAMP_BLOCK = %s;" % json.dumps(CAMP_BLOCK_TEXT))''')
rep('Mk(cfg, """' + LF + 'public static void fillDefaults(', r'''# 0.1.1: the Campfire accessory dishes (cook:campfire:ids)
Mk(cfg, """
public static int campIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < CAMP.length; i++) if (CAMP[i].equals(id)) return i;
  return -1;
}""")
Mk(cfg, """
public static String campList() {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < CAMP.length; i++) {
    if (i > 0) b.append(',');
    b.append(CAMP[i]);
  }
  return b.toString();
}""")
Mk(cfg, """
public static String campNames() {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < CAMP.length; i++) {
    if (i > 0) {
      if (i == CAMP.length - 1) b.append(" and ");
      else b.append(", ");
    }
    b.append(nameOf(CAMP[i]));
  }
  return b.toString();
}""")
''' + 'Mk(cfg, """' + LF + 'public static void fillDefaults(')
rep('''    MESSAGES = bool(p, "messages", true);
''', '''    MESSAGES = bool(p, "messages", true);
    double cb = dbl(p, "campfire.buffFactor", DEF_CAMP_BUFF);
    if (cb < 0.0 || cb > 1.0) { bad++; warn("campfire.buffFactor=" + cb + " is outside 0..1 - clamped"); cb = cb < 0.0 ? 0.0 : 1.0; }
    CAMP_BUFF = cb;
    double cx = dbl(p, "campfire.xpFactor", DEF_CAMP_XP);
    if (cx < 0.0 || cx > 1.0) { bad++; warn("campfire.xpFactor=" + cx + " is outside 0..1 - clamped"); cx = cx < 0.0 ? 0.0 : 1.0; }
    CAMP_XP = cx;
    if (p.getProperty("campfire.buffFactor") == null && p.getProperty("campfire.xpFactor") == null) {
      try {
        java.nio.file.Files.write(FILE, CAMP_BLOCK.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.APPEND });
        info("cooking.properties: added the campfire.* lines (0.1.1 Campfire accessory, defaults buffFactor " + DEF_CAMP_BUFF + " / xpFactor " + DEF_CAMP_XP + ")");
      } catch (Throwable t) { warn("could not add the campfire.* lines to cooking.properties (the defaults are used): " + t); }
    }
''')
rep('''", cap " + MAX_PER_MIN + "/min" + (bad > 0 ?''',
    '''", cap " + MAX_PER_MIN + "/min, campfire accessory x" + CAMP_BUFF + " Grade bonus x" + CAMP_XP + " XP" + (bad > 0 ?''')

# ---------------------------------------------------------------------------------------------------------------- Cook: campfire logic
rep('F(ck, "public static final java.util.HashMap RATE = new java.util.HashMap();")',
    'F(ck, "public static final java.util.HashMap RATE = new java.util.HashMap();")' + LF +
    'F(ck, "public static final java.util.concurrent.ConcurrentHashMap CAMP_TOLD = new java.util.concurrent.ConcurrentHashMap();")')
COOK_CAMP = r'''# ================= 0.1.1 Campfire accessory (cook:fn:campfire; contract in the 0.1.1 docstring section) =================
# a vanilla Campfire-bench recipe (the only recipes the accessory cooks)
Mk(ck, """
public static boolean isCampfire(@CRR@ rc) {
  if (rc == null) return false;
  @BRQ@[] b = rc.getBenchRequirement();
  if (b == null) return false;
  for (int i = 0; i < b.length; i++) if (b[i] != null && "Campfire".equals(b[i].id)) return true;
  return false;
}""")
# a[1] -> the campfire dish id: a listed dish id as is, or a Campfire-bench recipe id whose primary output is listed; else null
Mk(ck, """
public static String campDish(String what) {
  if (what == null) return null;
  String w = what.trim();
  if (w.length() == 0) return null;
  if (@PKG@.CookCfg.campIndex(w) >= 0) return w;
  try {
    @CRR@ rc = (@CRR@) @CRR@.getAssetMap().getAsset(w);
    if (rc == null || !isCampfire(rc)) return null;
    String out = outId(rc);
    if (@PKG@.CookCfg.campIndex(out) >= 0) return out;
  } catch (Throwable t) { }
  return null;
}""")
# bench Grade g -> campfire Grade: the highest Grade 0..g whose multiplier M <= 1 + f x (M(g) - 1) (Python mirror camp_grade)
Mk(ck, """
public static int campGrade(int g, double f) {
  int b = clampGrade(g);
  if (b <= 0 || f <= 0.0) return 0;
  if (f >= 1.0) return b;
  double target = 1.0 + f * (@PKG@.CookCfg.MUL[b] - 1.0) + 1.0E-9;
  int c = 0;
  for (int k = 1; k <= b; k++) if (@PKG@.CookCfg.MUL[k] <= target) c = k;
  return c;
}""")
# one chat hint per session, and again when the campfire Grade rises (messages=true)
Mk(ck, """
public static void campHint(java.util.UUID u, int g, int c) {
  try {
    if (!@PKG@.CookCfg.MESSAGES) return;
    Integer told = (Integer) CAMP_TOLD.get(u);
    if (told != null && told.intValue() >= c) return;
    CAMP_TOLD.put(u, Integer.valueOf(c));
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return;
    String s = "Campfire accessory = quick emergency cooking: your campfire dishes come out ";
    if (c > 0) s = s + "Grade " + c + " (" + pc(@PKG@.CookCfg.CAMP_BUFF) + " of your Grade " + g + " bonus - heal and buffs x" + x2(@PKG@.CookCfg.SF[c]) + ")";
    else if (g > 0) s = s + "plain (" + pc(@PKG@.CookCfg.CAMP_BUFF) + " of your Grade " + g + " bonus rounds down to Grade 0)";
    else s = s + "plain";
    s = s + " and pay " + pc(@PKG@.CookCfg.CAMP_XP) + " of the Cooking XP. A Cooking Bench gives the full Grade and XP.";
    tell(pr, s, true);
  } catch (Throwable t) { }
}""")
# THE campfire cook. null = not a campfire dish. Else Object[]{ String id to give, Integer bench Grade G, Integer campfire Grade c,
# Long XP sent to SkyySkills, String why-plain or null }. crafts <= 0 = preview (no XP, no hint).
Mk(ck, """
public static Object[] campfire(java.util.UUID u, String what, int crafts, String expectKey, Boolean creativeFlag) {
  if (u == null) return null;
  String dish = campDish(what);
  if (dish == null) return null;
  int n = crafts;
  boolean preview = n <= 0;
  if (n > 10000) n = 10000;
  String key = pkey(u);
  String why = null;
  if (!@PKG@.CookCfg.ENABLED) why = "graded cooking is off (enabled=false)";
  else if (busy(u)) why = "profile loading (profile:busy)";
  else if (expectKey != null && !expectKey.equals(key)) why = "the caller's profile key differs";
  else if (!@PKG@.CookCfg.CREATIVE) {
    if (creativeFlag != null && creativeFlag.booleanValue()) why = "creative mode";
    else {
      int cm = creativeOf(u);
      if (cm == 1) why = "creative mode";
      else if (cm < 0 && creativeFlag == null) {
        why = "game mode unreadable (not on the player's world thread)";
        @PKG@.CookCfg.once("campfn:mode", "cook:fn:campfire: cannot read the game mode of " + u + " (not on that player's world thread?) and the caller passed no creative flag - plain dish and no XP. Call it on the world thread or pass Object[]{UUID, id, crafts, expectKey, Boolean creative}.");
      }
    }
  }
  int lv = -1;
  if (why == null) {
    lv = level(u);
    if (lv < 0) why = "SkyySkills is not loaded";
  }
  if (why != null) return new Object[] { dish, Integer.valueOf(0), Integer.valueOf(0), Long.valueOf(0L), why };
  int[] t = tree(u);
  int g = clampGrade(baseGrade(lv) + (t[9] >= 1 ? 1 : 0));
  int c = campGrade(g, @PKG@.CookCfg.CAMP_BUFF);
  String id = dish;
  if (c > 0 && @PKG@.CookCfg.GRADED.contains(dish)) {
    String gid = gradedId(dish, c);
    if (exists(gid)) id = gid;
    else c = 0;
  } else c = 0;
  long sent = 0L;
  if (!preview) {
    long base = Math.round((double) @PKG@.CookCfg.xpFor(dish) * (double) n * @PKG@.CookCfg.CAMP_XP);
    if (base > 0L && allowXp(u, base)) sent = sendXp(u, Math.round(base * @PKG@.CookCfg.XP_MULT), "cook:campfire:" + dish, key);
    campHint(u, g, c);
  }
  return new Object[] { id, Integer.valueOf(g), Integer.valueOf(c), Long.valueOf(sent), null };
}""")

'''
rep("# ================= CookXpTask: the deferred award", COOK_CAMP + "# ================= CookXpTask: the deferred award")

# ---------------------------------------------------------------------------------------------------------------- bridge Function
CAMP_FN = r'''# cook:fn:campfire (0.1.1): apply(Object[]{UUID, String recipeOrOutputId, Number crafts [, String expectKey [, Boolean creative]]})
# -> String item id to give (graded or plain) or null (not a campfire dish / malformed / error). World thread. Docstring 0.1.1 section.
cfn.addInterface(pool.get("java.util.function.Function"))
Ct(cfn, "public CookCampFn() { }")
Mk(cfn, """
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || a[1] == null || !(a[2] instanceof Number)) return null;
    String ek = null;
    if (a.length > 3 && a[3] != null) ek = String.valueOf(a[3]);
    Boolean cf = null;
    if (a.length > 4 && a[4] instanceof Boolean) cf = (Boolean) a[4];
    Object[] r = @PKG@.Cook.campfire((java.util.UUID) a[0], String.valueOf(a[1]), ((Number) a[2]).intValue(), ek, cf);
    if (r == null) return null;
    return r[0];
  } catch (Throwable t) { @PKG@.CookCfg.every("campfn", 30000L, "cook:fn:campfire failed (the caller gives its plain output): " + t); return null; }
}""")

'''
rep("# skill:stats:Cooking (SkyySkills 0.4 Stats page hook)", CAMP_FN + "# skill:stats:Cooking (SkyySkills 0.4 Stats page hook)")
rep('''    } else out.add("Grades 11 and 12 come only from the Cooking skill tree");
''', '''    } else out.add("Grades 11 and 12 come only from the Cooking skill tree");
    int cg = @PKG@.Cook.campGrade(g, @PKG@.CookCfg.CAMP_BUFF);
    out.add("Campfire accessory quick cook - " + (cg > 0 ? "Grade " + cg + " food x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[cg]) : "plain food") + " - " + @PKG@.Cook.pc(@PKG@.CookCfg.CAMP_XP) + " of the XP");
''')

# ---------------------------------------------------------------------------------------------------------------- commands
CAMP_CMD = r'''# /cookadmin campfire <dish> <count> (0.1.1): runs cook:fn:campfire exactly as /craft does, gives count x the returned id (no materials)
F(fcmd, "public %s dishArg;" % RA)
F(fcmd, "public %s countArg;" % RA)
Ct(fcmd, """
public CookCampCmd() {
  super("campfire", "(admin) Test the Campfire accessory cook like /craft: /cookadmin campfire wildmeat_cooked 5 (gives the dishes and the XP, uses no materials; 0 = preview)");
  this.dishArg = withRequiredArg("dish", "Food_Wildmeat_Cooked, Food_Fish_Grilled or Food_Vegetable_Cooked (Food_ may be left out)", @ATY@.STRING);
  this.countArg = withRequiredArg("count", "0-64 (0 = preview: shows the Grade, gives nothing, no XP)", @ATY@.STRING);
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
}""")
Mk(fcmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyycooking.admin")) { pr.sendMessage(@MSG@.raw("[Cooking] no permission (skyycooking.admin)")); return; }
    String d = String.valueOf(ctx.get(this.dishArg)).trim();
    String dish = null;
    for (int i = 0; i < @PKG@.CookCfg.CAMP.length; i++) {
      String x = @PKG@.CookCfg.CAMP[i];
      if (x.equalsIgnoreCase(d) || x.equalsIgnoreCase("Food_" + d)) dish = x;
    }
    if (dish == null) { pr.sendMessage(@MSG@.raw("[Cooking] '" + d + "' is not a campfire dish. Campfire dishes: " + @PKG@.CookCfg.campList())); return; }
    int n = -1;
    try { n = Integer.parseInt(String.valueOf(ctx.get(this.countArg)).trim()); } catch (Throwable t) { n = -1; }
    if (n < 0 || n > 64) { pr.sendMessage(@MSG@.raw("[Cooking] count must be 0-64 (0 = preview)")); return; }
    Object[] r = @PKG@.Cook.campfire(pr.getUuid(), dish, n, (String) null, (Boolean) null);
    if (r == null) { pr.sendMessage(@MSG@.raw("[Cooking] " + dish + " was not accepted as a campfire dish")); return; }
    String id = (String) r[0];
    if (n > 0) {
      @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
      if (p != null) @SIC@.addOrDropItemStack(store, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, n));
    }
    String why = r[4] == null ? "" : " - plain because " + String.valueOf(r[4]);
    String act = n > 0 ? "gave " + n + " x " : "would give ";
    pr.sendMessage(@MSG@.raw("[Cooking] Campfire accessory test: bench Grade " + String.valueOf(r[1]) + " -> campfire Grade " + String.valueOf(r[2]) + " (buffFactor " + @PKG@.CookCfg.CAMP_BUFF + ", xpFactor " + @PKG@.CookCfg.CAMP_XP + ") - " + act + id + " - Cooking XP sent " + String.valueOf(r[3]) + why));
  } catch (Throwable t) { @PKG@.CookCfg.warn("/cookadmin campfire failed: " + t); pr.sendMessage(@MSG@.raw("[Cooking] campfire test failed: " + t)); }
}""")
'''
rep('Ct(acmd, """', CAMP_CMD + 'Ct(acmd, """')
rep('''  super("cookadmin", "(admin) SkyyCooking: /cookadmin give <dish> <grade>, /cookadmin reload");''',
    '''  super("cookadmin", "(admin) SkyyCooking: /cookadmin give <dish> <grade>, /cookadmin campfire <dish> <count>, /cookadmin reload");''')
rep('''  addSubCommand(new @PKG@.CookReloadCmd());''',
    '''  addSubCommand(new @PKG@.CookReloadCmd());''' + LF + '''  addSubCommand(new @PKG@.CookCampCmd());''')
rep('''/cookadmin give <dish> <grade>  (e.g. /cookadmin give pie_meat 5)  |  /cookadmin reload"''',
    '''/cookadmin give <dish> <grade>  (e.g. /cookadmin give pie_meat 5)  |  /cookadmin campfire <dish> <count>  (e.g. /cookadmin campfire wildmeat_cooked 0)  |  /cookadmin reload"''')
rep('''    } else if (base >= 10) pr.sendMessage(@MSG@.raw("[Cooking] Grades 11 and 12 come only from the Cooking skill tree (SkyyTrees)."));
''', '''    } else if (base >= 10) pr.sendMessage(@MSG@.raw("[Cooking] Grades 11 and 12 come only from the Cooking skill tree (SkyyTrees)."));
    int cg = @PKG@.Cook.campGrade(g, @PKG@.CookCfg.CAMP_BUFF);
    pr.sendMessage(@MSG@.raw("[Cooking] Campfire accessory (quick cooking in /craft, an emergency cook): " + @PKG@.CookCfg.campNames() + " come out " + (cg > 0 ? "Grade " + cg + " (x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[cg]) + ")" : "plain") + " and pay " + @PKG@.Cook.pc(@PKG@.CookCfg.CAMP_XP) + " of the Cooking XP."));
''')
rep('''A placed Campfire gives plain food and no XP; its dishes are on the Cooking Bench too."));''',
    '''A placed Campfire gives plain food and no XP; its dishes are on the Cooking Bench too (full Grade and XP)."));''')

# ---------------------------------------------------------------------------------------------------------------- plugin
rep('''  b.put("skill:stats:Cooking", new @PKG@.CookStatsFn());''',
    '''  b.put("skill:stats:Cooking", new @PKG@.CookStatsFn());''' + LF +
    '''  b.put("cook:fn:campfire", new @PKG@.CookCampFn());''' + LF +
    '''  b.put("cook:campfire:ids", @PKG@.CookCfg.campList());''')
rep('''and Cooking XP through SkyySkills; /cooking; config: "''',
    '''and Cooking XP through SkyySkills; Campfire accessory bridge cook:fn:campfire (" + @PKG@.CookCfg.campList() + "); /cooking; config: "''')
rep('''b.remove("skill:stats:Cooking"); }''',
    '''b.remove("skill:stats:Cooking"); b.remove("cook:fn:campfire"); b.remove("cook:campfire:ids"); }''')

# ---------------------------------------------------------------------------------------------------------------- write classes + compiled-Java parity check + manifest
rep('''for c in (cfg, ck, xpt, csy, gfn, ofn, sfn, gcmd, rcmd, acmd, ccmd, pl):
    c.writeFile(OUT)
print("classes written")
''', r'''for c in (cfg, ck, xpt, csy, gfn, ofn, sfn, cfn, gcmd, rcmd, fcmd, acmd, ccmd, pl):
    c.writeFile(OUT)
print("classes written")

# 0.1.1 self-check: the COMPILED Cook.campGrade / CookCfg.campList (loaded from build_classes with the server jar) match the Python mirror
import jpype
_URL, _File = jpype.JClass("java.net.URL"), jpype.JClass("java.io.File")
_ld = jpype.JClass("java.net.URLClassLoader")(jpype.JArray(_URL)([_File(OUT).toURI().toURL(), _File(J["server_jar"]).toURI().toURL()]))
_JCook = jpype.JClass(PKG + ".Cook", loader=_ld)
_JCfg = jpype.JClass(PKG + ".CookCfg", loader=_ld)
for _f in (CAMP_BUFF_DEF, 0.5, 0.25, 0.0, 1.0, 0.9):
    _jt = [int(_JCook.campGrade(g, _f)) for g in range(GEN_MAX + 1)]
    _pt = [camp_grade(g, _f) for g in range(GEN_MAX + 1)]
    if _jt != _pt:
        raise SystemExit("self-check 0.1.1: compiled Cook.campGrade(g, %s) = %s but the Python mirror says %s" % (_f, _jt, _pt))
if str(_JCfg.campList()) != ",".join(CAMP_DISHES) or int(_JCfg.campIndex("Food_Pie_Meat")) != -1 or int(_JCfg.campIndex(CAMP_DISHES[0])) != 0:
    raise SystemExit("self-check 0.1.1: compiled CookCfg.campList / campIndex disagree with CAMP_DISHES")
if str(_JCook.campDish(" " + CAMP_DISHES[1] + " ")) != CAMP_DISHES[1]:
    raise SystemExit("self-check 0.1.1: compiled Cook.campDish does not accept a listed dish id")
print("compiled campfire mapping matches the Python mirror (buffFactor 0.75 / 0.5 / 0.25 / 0 / 1 / 0.9); cook:campfire:ids = " + str(_JCfg.campList()))
''')
rep('''the Campfire dishes can be cooked at the Cooking Bench too; Cooking XP goes to SkyySkills.''',
    '''the Campfire dishes can be cooked at the Cooking Bench too, or instantly through the Campfire accessory in /craft (SkyySacks) as an emergency cook at 75% of the Grade bonus and 50% of the XP; Cooking XP goes to SkyySkills.''')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
