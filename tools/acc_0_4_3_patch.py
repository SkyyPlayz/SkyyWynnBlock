"""Derive SkyyAccessories/build_skyyaccessories_0.4.3.py from 0.4.2 (same style as acc_0_4_2_patch.py: rep(old, new) with asserted
anchors, newline-agnostic; 0.4.2 stays untouched, its line endings are preserved).
0.4.3 (Skyy's feedback on the build round, 2026-09-24, HANDOFF section 1): "add the campfire accessory back for quick inventory cooking
as it already limits what you can make ... so you get 50% xp and 75% of your normal buffs when using it, so its an emergency cook".
UN-RETIRE the Campfire bench accessory (Skyy_Accessory_Campfire_T1) ONLY:
 1. RETIRED = Alchemybench + Cookingbench (0.4.2: + Campfire). ACTIVE = 11 benches, 25 accessory ids. The Java arrays built from ACTIVE
    (AccDefs.BENCH_IDS / BENCH_NAMES / BENCH_MAX) gain "Campfire" at the end; RETIRED / RETIRED_NAMES / RETIRED_MAX lose it.
 2. Recipe back: Bench_Campfire + 4 Copper Bars at a Workbench (the 0.4.1 recipe - the unchanged T1 rule simply keeps it now). Name
    "Campfire Accessory" (no "(retired)"), Quality Common. Description starts with Skyy's call in the orchestrator's words: "Quick
    inventory cooking: campfire dishes in /craft at 50% Cooking XP and 75% of your cooking bonus." + how to use it. The two numbers are
    SkyyCooking 0.1.1's defaults campfire.xpFactor=0.5 / campfire.buffFactor=0.75: the build reads the newest SkyyCooking build script
    when it is there and fails on a mismatch, so the tooltip cannot drift from the defaults (a server that edits cooking.properties
    changes the real factors; the item text shows the defaults).
    REVIEW FIXES (same 0.4.3, never deployed):
    - The item text says the numbers are the defaults ("by default - your Accessory Bag page shows this server's numbers").
    - LIVE factors: AccStore.campFactors() reads SkyyCooking's live campfire factors (the public static volatile doubles CookCfg.CAMP_XP /
      CAMP_BUFF that cooking.properties + /cookadmin reload set), found through the class loader of the cook:fn:campfire object - read
      only, nothing called, no dependency (null without SkyyCooking 0.1.1). SkyyCooking publishes no factor key; if a later SkyyCooking
      publishes one, read that instead.
      * Accessory Bag page: while the Campfire accessory or the Omni is equipped, the status line (when no click result is showing)
        says "Campfire accessory on this server - campfire dishes in /craft at X% Cooking XP and Y% of your cooking bonus" (live), or
        that SkyyCooking is not running (plain dishes, no Cooking XP). No new element, no layout change, no periodic update.
      * Server log: the 5 s tick (AccTick) warns ONCE per distinct value pair when the live factors differ from the item text (also
        after /cookadmin reload), and once when SkyyCooking runs but its factors cannot be read (a renamed field = the check would
        otherwise switch itself off silently).
    - The build-time check fails hard when a SkyyCooking build script is found but its CAMP_BUFF_DEF / CAMP_XP_DEF line cannot be read
      (only "no SkyyCooking build script at all" stays a printed note).
 3. AccDefs.isRetired is false for it again, so: Equip works (no page refusal, canEquipK / equipK guards off), rarityOf = 1 (Common,
    counts like any T1 accessory), it is published in acc:has:<uuid> again (AccDefs.benchList) and acc:fn:has answers true
    (AccStore.has). Copies owned or left in a bag since 0.4.2 simply work again: same item id, nothing to migrate.
 4. Omni: covers the Campfire again (BENCH_IDS has it -> synthetic Skyy_Accessory_Campfire_T1 in acc:has), recipe = the 11 ACTIVE
    top-tier bench accessories incl. Skyy_Accessory_Campfire_T1 (0.4.2: 10). Omnis crafted under 0.4.2 cover it too (same item). The
    description says campfire dishes made through it are the same quick inventory cooking, and that the retired Alchemy Bench and
    Cooking Bench are not covered.
 5. AccDefs.retiredWhy / retiredChat: the Campfire text is gone; their fall-through is a generic "retired" line that no current id
    reaches (only Alchemybench / Cookingbench are retired and both have their own branch).
 6. Build checks: 5 retired ids (was 6), none has a recipe and no recipe takes one (0.4.2 check kept); Campfire T1 has exactly the
    Workbench recipe above, Quality Common, the new name + description; the Omni takes exactly the 11 top-tier ACTIVE accessories.
 7. Ready log (25 bench accessories + Omni, 5 retired) and manifest text.
Unchanged: Alchemy Bench T1-T4 and Cooking Bench stay retired exactly as in 0.4.2 (no recipe, refused on Equip with page + chat line,
filtered from acc:has / acc:fn:has, grey "DOES NOTHING", listed last); every 0.4.2 / 0.4.1 behaviour (per-profile bags via pkey, one key
per click, epoch republish, profile:busy / unknown-profile move block, page-key check, talismans, movement protocol) is untouched.
NOT IN THIS MOD (pairing): the XP x0.5 / bonus x0.75 is SkyyCooking 0.1.1 (cook:fn:campfire), called by SkyySacks' /craft page.
SkyySacks 0.7.3 still hard-codes the Campfire as retired (CraftPage.retiredBench) and as a timed table-only bench (tableOnly), so with
Sacks 0.7.3 the equipped Campfire accessory unlocks nothing in /craft - it needs the SkyySacks build that shows its cook:campfire:ids
recipes again and calls cook:fn:campfire.
Run:  python tools/acc_0_4_3_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.4.3.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.2.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.2"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.4.2 - build script (derived from 0.4.1 by tools/acc_0_4_2_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.2.py            -> SkyyAccessories/SkyyAccessories-0.4.2.jar
       python build_skyyaccessories_0.4.2.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.2: RETIRED bench accessories''', '''"""SkyyAccessories 0.4.3 - build script (derived from 0.4.2 by tools/acc_0_4_3_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.3.py            -> SkyyAccessories/SkyyAccessories-0.4.3.jar
       python build_skyyaccessories_0.4.3.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.3: the CAMPFIRE accessory is BACK (Skyy 2026-09-24: quick inventory cooking, an emergency cook). Full notes in
     tools/acc_0_4_3_patch.py:
     - Skyy_Accessory_Campfire_T1: recipe back (Bench_Campfire + 4 Copper Bars at a Workbench), equippable, Common, in acc:has:<uuid> and
       acc:fn:has again. Description "Quick inventory cooking: campfire dishes in /craft at 50% Cooking XP and 75% of your cooking
       bonus" (SkyyCooking 0.1.1 cook:fn:campfire does the reduction; SkyySacks has to show + call it - 0.7.3 still treats it as retired).
     - Omni: covers the Campfire again; recipe = the 11 active top-tier bench accessories (0.4.2: 10).
     - Review fixes: the item text calls 50% / 75% the defaults; the bag page status line shows SkyyCooking's LIVE campfire factors
       while the Campfire accessory or the Omni is equipped (AccStore.campFactors / campLine); the 5 s tick logs one warning per
       distinct live pair that differs from the item text (AccStore.campCheck); the build fails if the SkyyCooking defaults line
       cannot be read.
     - Alchemy Bench T1-T4 and Cooking Bench stay retired exactly as in 0.4.2; every other 0.4.2 behaviour is unchanged.
0.4.2 notes:
0.4.2: RETIRED bench accessories''')
rep('VERSION = "0.4.2"\n', 'VERSION = "0.4.3"\n')

# ---------------------------------------------------------------- RETIRED / ACTIVE (python side): the Campfire is active again
rep('''# 0.4.2 RETIRED bench accessories (Smithing-Smelting spec section 6; the Campfire goes with them - its whole recipe list is 3 cooked
# foods). Their rows stay in BENCHES so the item assets are still generated (owned copies stay valid items), but they get no recipe,
# Equip refuses them, acc:has / acc:fn:has leave them out, the Omni does not cover them and they never count for rarity/power.
# AccDefs.retiredWhy / retiredChat name these three ids literally - keep them in sync.
RETIRED = ["Alchemybench", "Cookingbench", "Campfire"]
assert RETIRED == ["Alchemybench", "Cookingbench", "Campfire"], "AccDefs.retiredWhy / retiredChat and RETIRED_DESC name these literally"
ACTIVE = [b for b in BENCHES if b[0] not in RETIRED]
assert all(any(b[0] == r for b in BENCHES) for r in RETIRED), RETIRED
assert len(ACTIVE) == len(BENCHES) - len(RETIRED) == 10, [b[0] for b in ACTIVE]
''', '''# 0.4.2 RETIRED bench accessories (Smithing-Smelting spec section 6). Their rows stay in BENCHES so the item assets are still generated
# (owned copies stay valid items), but they get no recipe, Equip refuses them, acc:has / acc:fn:has leave them out, the Omni does not
# cover them and they never count for rarity/power. AccDefs.retiredWhy / retiredChat name these two ids literally - keep them in sync.
# 0.4.3: the Campfire is NOT retired any more (Skyy 2026-09-24: quick inventory cooking at 50% Cooking XP and 75% of the cooking
# bonus - SkyyCooking 0.1.1 cook:fn:campfire, called by SkyySacks' /craft page). It is an ordinary ACTIVE bench accessory again.
RETIRED = ["Alchemybench", "Cookingbench"]
assert RETIRED == ["Alchemybench", "Cookingbench"], "AccDefs.retiredWhy / retiredChat and RETIRED_DESC name these literally"
ACTIVE = [b for b in BENCHES if b[0] not in RETIRED]
assert all(any(b[0] == r for b in BENCHES) for r in RETIRED), RETIRED
assert len(ACTIVE) == len(BENCHES) - len(RETIRED) == 11, [b[0] for b in ACTIVE]
assert [b[3] for b in ACTIVE if b[0] == "Campfire"] == [1], "0.4.3: the Campfire must be an active single-tier bench"
''')
rep('''assert RETIRED_MAX == [4, 1, 1], RETIRED_MAX
''', '''assert RETIRED_MAX == [4, 1], RETIRED_MAX
# 0.4.3 Campfire accessory description (Skyy's call, orchestrator wording). The two numbers are SkyyCooking's defaults
# campfire.xpFactor / campfire.buffFactor (cook:fn:campfire applies the real, configurable factors) - checked against the newest
# SkyyCooking build script when it is present, so the tooltip cannot drift from those defaults.
# 0.4.3 review fix: a server can change the real factors in cooking.properties, so the text calls them the defaults and points at the
# Accessory Bag page, whose status line shows the LIVE factors (AccStore.campLine); AccStore.campCheck logs a mismatch once.
CAMP_XP_PCT, CAMP_BUFF_PCT = 50, 75
CAMPFIRE_DESC = ("Quick inventory cooking: campfire dishes in /craft at %d%% Cooking XP and %d%% of your cooking bonus by default (your "
                 "Accessory Bag page shows this server's numbers). Put it in your Accessory Bag and /craft cooks the Campfire recipes "
                 "straight from your inventory - an emergency cook; a Cooking Bench gives the full bonus and XP.") % (CAMP_XP_PCT, CAMP_BUFF_PCT)
assert CAMPFIRE_DESC.startswith("Quick inventory cooking: campfire dishes in /craft at 50% Cooking XP and 75% of your cooking bonus by default"), CAMPFIRE_DESC
def _camp_defaults_check():
    import re, glob
    def _v(p):
        m = re.search(r"_(\\d+(?:\\.\\d+)*)\\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(glob.glob(os.path.join(HERE, "..", "SkyyCooking", "build_skyycooking_*.py")), key=_v)
    if not found:
        print("note: no SkyyCooking build script next to this mod - Campfire description numbers not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    m = re.search(r"^CAMP_BUFF_DEF, CAMP_XP_DEF = ([0-9.]+), ([0-9.]+)", txt, re.M)
    if not m:   # 0.4.3 review fix: SkyyCooking IS here but changed shape - fail instead of silently skipping the check
        raise SystemExit("0.4.3: %s has no 'CAMP_BUFF_DEF, CAMP_XP_DEF = <buff>, <xp>' line any more - find SkyyCooking's campfire "
                         "defaults, update CAMP_*_PCT and this check (tools/acc_0_4_3_patch.py)" % os.path.basename(found[-1]))
    buff, xp = int(round(float(m.group(1)) * 100)), int(round(float(m.group(2)) * 100))
    if (buff, xp) != (CAMP_BUFF_PCT, CAMP_XP_PCT):
        raise SystemExit("0.4.3: %s defaults are buff %d%% / XP %d%% but the Campfire accessory text says %d%% / %d%% - update CAMP_*_PCT"
                         % (os.path.basename(found[-1]), buff, xp, CAMP_BUFF_PCT, CAMP_XP_PCT))
    print("campfire accessory text matches %s defaults (XP %d%%, bonus %d%%)" % (os.path.basename(found[-1]), xp, buff))
_camp_defaults_check()
''')

# ---------------------------------------------------------------- Java arrays: Campfire is in BENCH_IDS again (build-time check)
rep('''bench_names = ", ".join('"%s"' % b[2] for b in ACTIVE)''', '''bench_names = ", ".join('"%s"' % b[2] for b in ACTIVE)
assert '"Campfire"' in bench_ids and '"Alchemybench"' not in bench_ids and '"Cookingbench"' not in bench_ids, bench_ids   # 0.4.3''')

# ---------------------------------------------------------------- AccDefs.retiredWhy / retiredChat: Campfire texts gone
rep('''# 0.4.2: a retired bench accessory (Alchemy Bench T1-T4, Cooking Bench, Campfire): kept as an item, does nothing''',
    '''# 0.4.2: a retired bench accessory (Alchemy Bench T1-T4, Cooking Bench; 0.4.3: no longer the Campfire): kept as an item, does nothing''')
rep('''  return "Retired - cooked food is table-only now - cook at a real Cooking Bench or Campfire";''',
    '''  return "Retired - this accessory does nothing any more";   // 0.4.3: the Campfire is active again - no retired id reaches this''')
rep('''  return "The Campfire accessory is retired: its recipes are all cooked food, and cooking is table-only now. Cook at a real Cooking Bench or Campfire." + tail;''',
    '''  return "This accessory is retired." + tail;   // 0.4.3: the Campfire is active again - no retired id reaches this''')

# ---------------------------------------------------------------- review fix: SkyyCooking's LIVE campfire factors (page line + log)
rep('''# ================= AccFn (bridge function acc:fn:has) =================
''', '''# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors. The item text can only carry the defaults (CAMP_*_PCT), but a server
# can change campfire.xpFactor / campfire.buffFactor in cooking.properties (+ /cookadmin reload). SkyyCooking 0.1.1 keeps them in the
# public static volatile doubles CookCfg.CAMP_XP / CAMP_BUFF (package of its cook:fn:campfire object) and publishes no factor key, so
# they are read by reflection through that object's class loader: read only, nothing is called, no dependency, never throws.
# campFactors() -> {xpFactor, buffFactor} or null (SkyyCooking absent / pre-0.1.1 / fields not found). Any thread (volatile reads).
st_.addField(CtField.make("public static volatile Object CF_OWNER;", st_))
st_.addField(CtField.make("public static volatile java.lang.reflect.Field CF_XP;", st_))
st_.addField(CtField.make("public static volatile java.lang.reflect.Field CF_BUFF;", st_))
st_.addField(CtField.make('public static volatile String CF_SEEN = "";', st_))   # campCheck: last state logged (tick thread only)
st_.addField(CtField.make("public static final double CAMP_XP_TEXT = %s;" % repr(CAMP_XP_PCT / 100.0), st_))
st_.addField(CtField.make("public static final double CAMP_BUFF_TEXT = %s;" % repr(CAMP_BUFF_PCT / 100.0), st_))
st_.addField(CtField.make('public static final String CAMPFIRE_ID = "Skyy_Accessory_Campfire_T1";', st_))
st_.addMethod(CtNewMethod.make("""
public static double[] campFactors() {
  try {
    Object f = bridge().get("cook:fn:campfire");
    if (f == null) return null;
    if (f != CF_OWNER) {
      CF_XP = null;
      CF_BUFF = null;
      CF_OWNER = f;
      String n = f.getClass().getName();
      Class c = Class.forName(n.substring(0, n.lastIndexOf('.') + 1) + "CookCfg", false, f.getClass().getClassLoader());
      java.lang.reflect.Field fx = c.getField("CAMP_XP");
      java.lang.reflect.Field fb = c.getField("CAMP_BUFF");
      if (fx.getType() != Double.TYPE || fb.getType() != Double.TYPE) return null;
      CF_XP = fx;
      CF_BUFF = fb;
    }
    java.lang.reflect.Field x = CF_XP;
    java.lang.reflect.Field b = CF_BUFF;
    if (x == null || b == null) return null;
    double xv = x.getDouble((Object) null);
    double bv = b.getDouble((Object) null);
    if (!(xv >= 0.0 && xv <= 1.0 && bv >= 0.0 && bv <= 1.0)) return null;
    return new double[] { xv, bv };
  } catch (Throwable t) { return null; }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String campPct(double v) {
  long c = Math.round(v * 1000.0);
  if (c % 10L == 0L) return String.valueOf(c / 10L) + "%";
  return String.valueOf(c / 10L) + "." + String.valueOf(c % 10L) + "%";
}""", st_))
# 5 s tick (AccTick, scheduler thread): one WARNING per distinct state - live factors that differ from the item text, or SkyyCooking
# running with factors that cannot be read. Silent while they match the text or SkyyCooking (0.1.1+) is absent.
st_.addMethod(CtNewMethod.make("""
public static void campCheck() {
  try {
    if (bridge().get("cook:fn:campfire") == null) return;
    double[] f = campFactors();
    String seen = "unreadable";
    if (f != null) seen = (Math.abs(f[0] - CAMP_XP_TEXT) < 0.0005 && Math.abs(f[1] - CAMP_BUFF_TEXT) < 0.0005) ? "default" : campPct(f[0]) + " " + campPct(f[1]);
    if (seen.equals(CF_SEEN)) return;
    CF_SEEN = seen;
    if (seen.equals("default")) return;
    if (f == null) warn("SkyyCooking runs, but its live Campfire accessory factors could not be read (CookCfg.CAMP_XP / CAMP_BUFF next to cook:fn:campfire - a newer SkyyCooking?). The Campfire Accessory item text shows the defaults " + campPct(CAMP_XP_TEXT) + " Cooking XP / " + campPct(CAMP_BUFF_TEXT) + " of the cooking bonus and the Accessory Bag page cannot show this server's numbers.");
    else warn("cooking.properties sets the Campfire accessory to " + campPct(f[0]) + " Cooking XP and " + campPct(f[1]) + " of the cooking bonus (campfire.xpFactor / campfire.buffFactor), but the Campfire Accessory item text says the defaults " + campPct(CAMP_XP_TEXT) + " / " + campPct(CAMP_BUFF_TEXT) + ". The Accessory Bag page shows the live numbers; the item text only changes with a SkyyAccessories rebuild (CAMP_XP_PCT / CAMP_BUFF_PCT).");
  } catch (Throwable t) { }
}""", st_))
# Accessory Bag page status line while the Campfire accessory or the Omni is equipped ("" otherwise, or when the factors cannot be read)
st_.addMethod(CtNewMethod.make("""
public static String campLine(String[] s) {
  try {
    boolean on = false;
    if (s != null) for (int i = 0; i < s.length; i++) if (CAMPFIRE_ID.equals(s[i]) || com.skyy.accessories.AccDefs.OMNI.equals(s[i])) on = true;
    if (!on) return "";
    if (bridge().get("cook:fn:campfire") == null) return "Campfire accessory - SkyyCooking is not running - campfire dishes in /craft come out plain with no Cooking XP";
    double[] f = campFactors();
    if (f == null) return "";
    return "Campfire accessory on this server - campfire dishes in /craft at " + campPct(f[0]) + " Cooking XP and " + campPct(f[1]) + " of your cooking bonus";
  } catch (Throwable t) { return ""; }
}""", st_))

# ================= AccFn (bridge function acc:fn:has) =================
''')
rep('''tick.addMethod(CtNewMethod.make(f"public void run() {{ {PKG}.AccStore.publishOnline(); }}", tick))''',
    '''tick.addMethod(CtNewMethod.make(f"public void run() {{ {PKG}.AccStore.publishOnline(); {PKG}.AccStore.campCheck(); }}", tick))   # 0.4.3 review fix''')
rep(r'''"Label #SkyyAccInfo {{ Anchor: (Height: 22); Text: \\"" + safe(this.info) + "\\";''',
    r'''"Label #SkyyAccInfo {{ Anchor: (Height: 22); Text: \\"" + safe(this.info != null && this.info.length() > 0 ? this.info : {PKG}.AccStore.campLine(s)) + "\\";''')

# ---------------------------------------------------------------- item assets: Campfire gets its recipe + the new description
rep('''    "Campfire": "Retired. Its recipes are all cooked food, and cooking is table-only now: cook at a real Cooking Bench or a placed Campfire." + RETIRED_TAIL,
''', '')
rep('''        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)''',
    '''        if bench_id == "Campfire":   # 0.4.3: back as quick inventory cooking (SkyyCooking cook:fn:campfire through SkyySacks /craft)
            d = CAMPFIRE_DESC
        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)''')

# ---------------------------------------------------------------- Omni: 11 active inputs incl. the Campfire
rep('''for bench_id, bench_item, name, tiers, ups in ACTIVE:   # 0.4.2: the retired three are not inputs any more (13 -> 10)''',
    '''for bench_id, bench_item, name, tiers, ups in ACTIVE:   # 0.4.2: retired benches are no inputs (13 -> 10); 0.4.3: the Campfire is again (11)''')
rep('''assert len(omni_in) == len(ACTIVE) == 10''', '''assert len(omni_in) == len(ACTIVE) == 11
assert {"ItemId": "Skyy_Accessory_Campfire_T1", "Quantity": 1} in omni_in   # 0.4.3''')
rep('''     "top-tier bench accessories. Alchemy and Cooking are table-only, so the retired Alchemy Bench, Cooking Bench and Campfire "
     "accessories are not part of it and are not covered.") % (''',
    '''     "top-tier bench accessories. Campfire dishes made through it are quick inventory cooking, like the Campfire accessory. Alchemy "
     "and Cooking are table-only, so the retired Alchemy Bench and Cooking Bench accessories are not part of it and are not covered.") % (''')

# ---------------------------------------------------------------- build checks
rep('''assert retired_count == len(_RET_IDS) == 6, (retired_count, sorted(_RET_IDS))''',
    '''assert retired_count == len(_RET_IDS) == 5, (retired_count, sorted(_RET_IDS))   # 0.4.3: Alchemy Bench T1-T4 + Cooking Bench''')
rep('''        assert _inp.get("ItemId") not in _RET_IDS, "%s still takes the retired %s" % (_iid, _inp.get("ItemId"))
''', '''        assert _inp.get("ItemId") not in _RET_IDS, "%s still takes the retired %s" % (_iid, _inp.get("ItemId"))
# 0.4.3 build check: the Campfire accessory is back - the 0.4.1 Workbench recipe, Common, its own name + description, an Omni input
_CF = "Skyy_Accessory_Campfire_T1"
assert _CF not in _RET_IDS
_cfn = json.loads(files["Server/Item/Items/Utility/%s.json" % _CF])
assert (_cfn.get("Recipe") or {}).get("Input") == [{"ItemId": "Bench_Campfire", "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}], _cfn.get("Recipe")
assert _cfn["Recipe"]["BenchRequirement"] == WB_REQ and _cfn["Quality"] == "Common", _cfn
for _pre in ("items.", "server.items."):
    assert (_pre + _CF + ".name=Campfire Accessory") in lang, _pre
    assert (_pre + _CF + ".description=" + CAMPFIRE_DESC) in lang, _pre
assert not any(l.startswith(("items." + _CF + ".", "server.items." + _CF + ".")) and "etired" in l for l in lang), "Campfire text still says retired"
_omn = json.loads(files["Server/Item/Items/Utility/%s.json" % OMNI])["Recipe"]["Input"]
assert sorted(i["ItemId"] for i in _omn) == sorted("Skyy_Accessory_%s_T%d" % (b[0], b[3]) for b in ACTIVE) and len(_omn) == 11, _omn
print("campfire accessory: recipe back, Omni input %d of %d, retired ids: %s" % (_omn.index({"ItemId": _CF, "Quantity": 1}) + 1, len(_omn), ", ".join(sorted(_RET_IDS))))
''')

# ---------------------------------------------------------------- log line + manifest
rep('''%d bench accessories + Omni (%d retired kept as items that do nothing - Alchemy Bench, Cooking Bench, Campfire), %d talismans''',
    '''%d bench accessories + Omni (%d retired kept as items that do nothing - Alchemy Bench, Cooking Bench), Campfire accessory back for quick inventory cooking, %d talismans''')
rep('''one bag per SkyyProfiles profile when that mod is installed; the Alchemy Bench, Cooking Bench and Campfire accessories are retired (Alchemy and Cooking are table-only). Zero dependencies."''',
    '''one bag per SkyyProfiles profile when that mod is installed; the Campfire accessory is quick inventory cooking (campfire dishes in /craft at reduced Cooking XP and bonus with SkyyCooking); the Alchemy Bench and Cooking Bench accessories are retired (Alchemy and Cooking are table-only). Zero dependencies."''')

assert 'VERSION = "0.4.3"' in s
assert 'RETIRED = ["Alchemybench", "Cookingbench"]\n' in s
assert '"Cookingbench", "Campfire"' not in s, "Campfire still in a retired list"
assert "Campfire accessory is retired" not in s and "Bench or Campfire" not in s
assert "assert len(omni_in) == len(ACTIVE) == 10" not in s
assert "for b in BENCHES), dfs))" not in s, "a Java bench array still built from BENCHES"
assert s.count("isRetired(id)") >= 8
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.2
print("wrote", dst)
