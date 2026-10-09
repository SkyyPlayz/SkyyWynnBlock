"""Derive SkyyCollections/build_skyycollections_0.2.8.py from the LIVE 0.2.7 (build_skyycollections_0.2.7.py = the tools/deploy_set.py
SET pin; 0.2.7 stays untouched; same style as coll_0_2_7_patch.py: rep() with asserted single anchors, newline-agnostic, the source's
line endings kept). Edit THIS file, never the generated build script (it is overwritten on every run of this patch).
Run:  python tools/collections_0_2_8_patch.py   then   python SkyyCollections/build_skyycollections_0.2.8.py   (never --deploy)
Test: python SkyyCollections/test_skyycollections_0.2.8.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/, deleted afterwards)

0.2.8 = UNLOCKED RECIPES OPEN IN THE CRAFTER (Skyy 2026-10-09: "any unlocked recipes shown here should open in the crafter if i click
it."). On a collection's tier table (STATE / TIER / NEEDED / REWARDS) every row whose rewards hold a recipe the player has UNLOCKED gets a
small vanilla Secondary CRAFT button at the end of the row (skyyui kit button, 80 x 32 = the row height; the rewards cell gives up
84 px: 802 -> 718). A click runs /craft <words> AS THE PLAYER (CommandManager.get().handleCommand(playerRef, line) - the SkyyMenu
"cmdc:" pattern, the same permission checks as typing it): SkyySacks' pocket crafting page opens already searching for that recipe's
item, so the recipe is the (only) result on the page - the closest thing to "selected" the craft page has.
  - WHERE IT OPENS (research): the vanilla bench pages are client windows tied to a bench BLOCK (BenchWindow / SimpleCraftingWindow need
    the block's BlockType; research/Accessory-Table-Spec.md, Bag-Craft-Link-Fix.md) and the client picks the recipe there, so a plugin
    cannot open "the Workbench on recipe X" without a bench in the world. SkyySacks' /craft is the crafter we can open for a player
    anywhere; its only public entry points are the command (/craft [words] = the page searching, 0.7.3) and the OpenCustomUI page ids
    (no tab choice for the Collections tab). Cross-mod calls only through the bridge / commands (AGENT-BRIEF), so /craft <words> it is.
  - The words: the recipe id the page already shows (CollReg.recipesAt) minus "_Recipe_Generated_<n>" = the output item id, split on
    "_" and lower-cased (Tool_Hoe_Copper -> "tool hoe copper"); SkyySacks' search matches every word inside the item id, so the recipe
    is found. A row with several unlocked recipes searches the words they all share when that is 2 or more words (all of them show);
    otherwise (review fix: e.g. Cobblestone I = Copper Pickaxe + Normal Mining Bag, Wheat I, Oak Log I) its CRAFT opens a CHOOSER = the
    Unlocked recipes list of just that tier, one CRAFT per recipe, whose Back returns to the collection. At most 40 characters, whole
    words (SkyySacks' cleanQuery limit).
  - Rewards text on a CRAFT row (84 px shorter): review fix - whole " - " parts drop off the end first ("Copper Hoe - Unique Farming
    Bag - ..."), so a recipe name is never cut while the names fit; only a first part that alone is too wide is cut inside a word.
  - UNLOCKED = the recipe is in CollUnlocks.compute (the exact coll:recipes set the Collections tab of /craft lists) AND the row's tier
    is reached (DONE) or bought (BOUGHT). LOCKED / NEXT rows and rows without an unlocked recipe stay plain text (0.2.7's row markup).
  - No /craft on the server (SkyySacks missing: CommandManager.resolveCommand("craft") is null) = no button anywhere: the page is
    0.2.7's, command for command. A forged / stale click is re-checked against the live data (a locked tier, no /craft, no permission,
    a throwing dispatch) and answered in the result line; nothing else happens.
  - The CRAFT binding does not lock the interface (addEventBinding(..., false), the Sacks search field / SkyyMenu grid pattern): the
    craft page replaces this page, and if /craft cannot open its page (SkyySacks says so in chat) this page is not left waiting.
  - KNOWN LIMIT (SkyySacks 0.7.15 / 0.7.16, not this mod - review finding, CONFIRMED): /craft's search (CraftPage.searchRecipes)
    only scans craftSet = Fieldcraft + the benches whose bench accessory the player wears, never the Collections tab set; the bag
    recipes and the copper tools are Workbench recipes, so WITHOUT a Workbench accessory the search says "Nothing matches" (the player
    then clicks the Collections tab, which lists them). The unlocked list says so. Fix = SkyySacks: searchRecipes also scans this.coll
    (the coll:recipes set it already holds) - then this mod's CRAFT shows the recipe with no change here.
  - /craft words need SkyySacks 0.7.3+ (setAllowsExtraArguments); the SkyySacks rollback floor is 0.7.7, so an older one cannot meet
    this build.
  - LOCKED RECIPES rows (review fix, docs/answered/bags.md "click = that collection"): the whole row is the click (the vanilla list-row
    select Button, the kit's row_style) plus the OPEN button at its end.
ROLLBACK FLOOR (review): do not roll SkyyCollections back below 0.2.8 once it ran: 0.2.7 reads the migrated rewards.properties but
ignores _keptbag.Mining, so a profile that had a Mining bag only through Iron (and not yet the Cobblestone tier) would lose that recipe.
Record the floor in tools/deploy_set.py when 0.2.8 is pinned.
No setting, bridge key, command or ECS system changes. Saved data: CollCobMig (part 3 below) moves the Mining bag lines of
rewards.properties once and writes _keptbag.Mining into counts files; the rest of the page is 0.2.7's.
NORMAL BAGS AT TIER I (Skyy 2026-10-09: "move normal bags to tier 1"): checked, nothing else to move. Since 0.2.3 the default ladder
(BAG_LADDER) and Skyy's live rewards.properties (migrated by CollBagMigrate on 2026-09-29) put every Normal (Skyy_Sack_*_Small) bag at
its collection's tier I, Unique III, Rare V, Legendary VII (live: Iron.1 / OakLog.1 / Wheat.1 / Bone.1 / HideLight.1). The "tier 3"
lines (OakLog.3 / Cobblestone.3 / Bone.3 = Small) are only in rewards-0.2.properties, the 0.2.2 archive CollBagMigrate keeps and no
version reads. After CollCobMig the Mining Normal bag sits on Cobblestone.1 (with the Copper Pickaxe). The harness checks all 5
types at I / III / V / VII on the fresh default table and on the migrated live copy (U9, M1).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.7.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.8.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.7"
LF = "\n"
s = raw.decode("utf8").replace("\r\n", LF)
OLD = s
assert 'VERSION = "0.2.7"' in s and "GENERATED by tools/coll_0_2_7_patch.py from the LIVE 0.2.6" in s, "not the live generated 0.2.7"
assert 'COLL_PAGE_CHECKED = "be0dca34bcb2"' in s, "build_skyycollections_0.2.7.py is not the checked 0.2.7 page"
assert "CollCraft" not in s and "ccraft" not in s

# the page id SkyyCollections/test_skyycollections_0.2.8.py last passed on (set after a passing harness run, then regenerate + rebuild)
PAGE_CHECKED = "e3b045f3048d"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


GONE_OK = set()


def rep_ok(old, new, count=1):
    """rep() whose replaced 0.2.7 lines may disappear (the lost-lines guard below)"""
    GONE_OK.update(old.split(LF))
    GONE_OK.update(ln for ln in s.split(LF) if any(len(p) > 8 and p in ln for p in old.split(LF)))   # whole lines of a fragment
    rep(old, new, count)


# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyCollections 0.2.7 - build script (javassist via jpype). GENERATED by tools/coll_0_2_7_patch.py from the LIVE 0.2.6
(build_skyycollections_0.2.6.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.6 was derived from 0.2.5 by
tools/coll_0_2_6_patch.py;''', '''"""SkyyCollections 0.2.8 - build script (javassist via jpype). GENERATED by tools/collections_0_2_8_patch.py from the LIVE 0.2.7
(build_skyycollections_0.2.7.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.7 was derived from 0.2.6 by
tools/coll_0_2_7_patch.py; 0.2.6 from 0.2.5 by tools/coll_0_2_6_patch.py;''')
rep('''0.2.7 (2026-10-06): THE LANTERN RECIPES UNLOCK''', '''0.2.8 (2026-10-09): UNLOCKED RECIPES OPEN IN THE CRAFTER (Skyy 2026-10-09: "any unlocked recipes shown here should open in the
  crafter if i click it."). A tier row of a collection whose rewards hold a recipe the player has unlocked (in coll:recipes, the row
  DONE or BOUGHT) ends in a small vanilla CRAFT button; a click runs /craft <the item's words> as the player, so SkyySacks' craft page
  opens searching for that recipe. No /craft on the server (SkyySacks missing) = no button (the 0.2.7 page). Locked rows stay plain.
  The vanilla bench windows need a bench block, so they cannot be opened on a recipe. Full notes: tools/collections_0_2_8_patch.py.
  LOCKED RECIPES (Skyy 2026-10-09: "we have unlocked recopies, we need a locked recopies tab, that tells you which collection you
  unlock something in."): a home button next to Unlocked recipes; a paged list of every recipe a visible collection unlocks that the
  player has not got (free bags count as unlocked), each with "<Collection> tier <roman>" and "count / threshold", closest first; a row
  click (or OPEN) = that collection's page (Back returns to the list). The Unlocked recipes view is the same paged list with CRAFT
  buttons; a tier row with 2+ unlocked recipes one search cannot show opens that list for just its tier.
  MINING BAG FROM COBBLESTONE (Skyy 2026-10-09: "the mining bag should come from cobble collection, not iron"): the Mining bag ladder
  (Normal I, Unique III, Rare V, Legendary VII) unlocks from Cobblestone; CollCobMig moves untouched Iron bag lines of an existing
  rewards.properties once (History, Undo, marker, bytes kept) and every profile that had a Mining bag through Iron keeps it
  (_keptbag.Mining). Full notes: tools/collections_0_2_8_patch.py.
  CHECKED with SkyyCollections/test_skyycollections_0.2.8.py.
0.2.7 (2026-10-06): THE LANTERN RECIPES UNLOCK''')
rep("Run:   python build_skyycollections_0.2.7.py          -> SkyyCollections/SkyyCollections-0.2.7.jar",
    "Run:   python build_skyycollections_0.2.8.py          -> SkyyCollections/SkyyCollections-0.2.8.jar")
rep('VERSION = "0.2.7"', 'VERSION = "0.2.8"')
rep('"[SkyyCollections] 0.2.7 ready (', '"[SkyyCollections] 0.2.8 ready (')

# ---------------------------------------------------------------------------------------------------------------- engine names + probes
rep('''    "IMOD": "com.hypixel.hytale.server.core.modules.item.ItemModule",''',
    '''    "IMOD": "com.hypixel.hytale.server.core.modules.item.ItemModule",
    "CMGR": "com.hypixel.hytale.server.core.command.system.CommandManager",   # 0.2.8: /craft as the player (SkyyMenu runCmd)''')
rep('''             (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"), (T["V3I"], "x"), (T["V3I"], "y"), (T["V3I"], "z")):''',
    '''             (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"), (T["V3I"], "x"), (T["V3I"], "y"), (T["V3I"], "z"),
             (T["CMGR"], "get"), (T["CMGR"], "resolveCommand"), (T["CMGR"], "handleCommand"), (T["AC"], "hasPermission")):   # 0.2.8''')

# ---------------------------------------------------------------------------------------------------------------- the new class
rep('''ckit = K("CollKit")   # 0.2.2: admin config kit hooks + the shared reload''',
    '''ckit = K("CollKit")   # 0.2.2: admin config kit hooks + the shared reload
kraft = K("CollCraft")   # 0.2.8: the CRAFT button of a tier row -> /craft <words> as the player''')
rep('''       plsy, ksy, tcmp, top, fnc, page, ckit, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''',
    '''       plsy, ksy, tcmp, top, fnc, page, ckit, kraft, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''')

CRAFT_JAVA = r'''# ================= 0.2.8 CollCraft: a tier row's CRAFT button opens SkyySacks' /craft searching for the unlocked recipe =================
# The search words of a recipe id: the output item id (the id minus "_Recipe_Generated_<n>", as CollUtil.prettyRecipe reads it) split
# into lower-case letter / digit words - SkyySacks' CraftPage.nameMatches finds an item when every word is inside its id.
M(kraft, r"""
public static java.util.ArrayList words(String rid) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (rid == null) return out;
  String id = rid.trim();
  int g = id.indexOf("_Recipe_Generated_");
  if (g > 0) id = id.substring(0, g);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i <= id.length(); i++) {
    char ch = i < id.length() ? id.charAt(i) : ' ';
    if (ch < 128 && Character.isLetterOrDigit(ch)) { sb.append(Character.toLowerCase(ch)); continue; }
    if (sb.length() > 0) { String w = sb.toString(); if (!out.contains(w)) out.add(w); sb.setLength(0); }
  }
  return out;
}""")
# The /craft words for one tier row, or null = no button: only the row's recipes the player has UNLOCKED (un = CollUnlocks.compute,
# the coll:recipes set). Several unlocked: the words they all share when that is 2+ words (every one of them shows), else the first.
# At most 40 characters of whole words (SkyySacks' CraftPage.cleanQuery keeps 40).
M(kraft, r"""
public static String query(String[] rs, java.util.Set un) {
  if (rs == null || un == null) return null;
  java.util.ArrayList first = null;
  java.util.ArrayList common = null;
  int n = 0;
  for (int i = 0; i < rs.length; i++) {
    if (rs[i] == null || !un.contains(rs[i])) continue;
    java.util.ArrayList w = words(rs[i]);
    if (w.isEmpty()) continue;
    n++;
    if (first == null) { first = w; common = new java.util.ArrayList(w); }
    else common.retainAll(w);
  }
  if (first == null) return null;
  java.util.ArrayList use = n > 1 && common.size() >= 2 ? common : first;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < use.size(); i++) {
    String w = (String) use.get(i);
    if (sb.length() + (sb.length() > 0 ? 1 : 0) + w.length() > 40) break;
    if (sb.length() > 0) sb.append(' ');
    sb.append(w);
  }
  return sb.length() == 0 ? null : sb.toString();
}""")
# 0.2.8 review fix: does query() find EVERY unlocked recipe of the row? (one unlocked, or 2+ shared words). false = the CRAFT click opens
# the row's chooser (the Unlocked recipes list of just that tier, one CRAFT per recipe) - e.g. Cobblestone I = Copper Pickaxe + Normal
# Mining Bag share no word, so one search cannot show both.
M(kraft, r"""
public static boolean one(String[] rs, java.util.Set un) {
  if (rs == null || un == null) return true;
  java.util.ArrayList common = null;
  int n = 0;
  for (int i = 0; i < rs.length; i++) {
    if (rs[i] == null || !un.contains(rs[i])) continue;
    java.util.ArrayList w = words(rs[i]);
    if (w.isEmpty()) continue;
    n++;
    if (common == null) common = new java.util.ArrayList(w);
    else common.retainAll(w);
  }
  return n <= 1 || common.size() >= 2;
}""")
# /craft on this server (SkyySacks' CraftCmd; resolveCommand: root names, then aliases), or null = no CRAFT buttons
M(kraft, r"""
public static @AC@ cmd() {
  try { return @CMGR@.get().resolveCommand("craft"); } catch (Throwable t) { return null; }
}""")
# 0.2.8 review: the rewards text of a CRAFT row has 84 px less (718): fitPx cuts it to whole characters + "..." when it would run past
# the cell (a bought row's "(paid when reached)" / "(gather this tier)" texts, an admin's long line). ADV = the client's glyph advances of
# the 16 px Default font (skyyui.text_width, no kerning) for ' '..'~' in 1/1000 px; any other character counts as the widest one.
_ADV = [int(round(SUI.text_width(chr(_i), 16) * 1000)) for _i in range(32, 127)]
F(kraft, "public static final int[] ADV = new int[] { %s };" % ", ".join(str(_a) for _a in _ADV))
F(kraft, "public static final int ADV_MAX = %d;" % max(_ADV))
M(kraft, r"""
public static int adv(char ch) {
  return ch >= 32 && ch < 127 ? ADV[ch - 32] : ADV_MAX;
}""")
M(kraft, r"""
public static long width(String s) {
  long w = 0L;
  for (int i = 0; s != null && i < s.length(); i++) w += (long) adv(s.charAt(i));
  return w;
}""")
# review fix: whole " - " parts drop off the END first (the rewards text lists the recipe names first, then coins / XP / the bought
# note), so a cut never hides a recipe name while the names fit: "Copper Hoe - Unique Farming Bag - ..."; only text whose FIRST part
# alone is too wide is cut inside a word
M(kraft, r"""
public static String fitPx(String s, int px) {
  if (s == null) return "";
  long lim = (long) px * 1000L;
  if (width(s) <= lim) return s;
  long tail = width(" - ...");
  int at = s.lastIndexOf(" - ");
  while (at > 0) {
    String h = s.substring(0, at);
    if (width(h) + tail <= lim) return h + " - ...";
    at = s.lastIndexOf(" - ", at - 1);
  }
  long ell = 3L * (long) adv('.');
  long u = 0L;
  int n = 0;
  while (n < s.length() && u + (long) adv(s.charAt(n)) + ell <= lim) { u += (long) adv(s.charAt(n)); n++; }
  String h = s.substring(0, n);
  while (h.length() > 0 && (h.charAt(h.length() - 1) == ' ' || h.charAt(h.length() - 1) == '-')) h = h.substring(0, h.length() - 1);
  return h + "...";
}""")
# runs "/craft <q>" AS the player (vanilla /su, SkyyMenu runCmd: installed + permission checked first, the engine checks again);
# null = sent (SkyySacks opens its page in place of this one), else the result-line text (an error: CollPage.statusColor -> red)
M(kraft, r"""
public static String open(@PR@ pr, String q) {
  if (pr == null || q == null || q.length() == 0) return "Could not open crafting.";
  @AC@ c = cmd();
  if (c == null) return "Crafting (/craft) is not on this server.";
  boolean ok = false;
  try { ok = c.hasPermission(pr); }
  catch (Throwable t) { @PKG@.CollUtil.warn("permission check for /craft failed: " + t); return "Could not check your permission for /craft. Ask an admin."; }
  if (!ok) return "You do not have permission for /craft. Ask an admin.";
  try { @CMGR@.get().handleCommand(pr, "craft " + q); }
  catch (Throwable t) { @PKG@.CollUtil.warn("/craft " + q + " failed: " + t); return "/craft could not be run."; }
  return null;
}""")

'''
rep('''# ================= CollPage: one inline page, views switched with rebuild()''',
    CRAFT_JAVA + '''# ================= CollPage: one inline page, views switched with rebuild()''')

# ---------------------------------------------------------------------------------------------------------------- the tier row look
rep('''COLL_TIER_LOOK = (("LOCKED", "disabled", "text"), ("DONE", "success", "rowName"), ("BOUGHT", "info", "rowName"),
                  ("NEXT", "warning", "rowName"))''', '''COLL_TIER_LOOK = (("LOCKED", "disabled", "text"), ("DONE", "success", "rowName"), ("BOUGHT", "info", "rowName"),
                  ("NEXT", "warning", "rowName"))
# 0.2.8: the CRAFT button at the end of a tier row with an unlocked recipe - a small vanilla Secondary button as tall as the row (32 =
# @SmallButtonHeight), 80 px (its label "CRAFT" 47 px at 14 px bold + 2 x 16 px padding: no shrink), 4 px left margin (row_action's);
# the rewards cell of that row gives up the 84 px (802 -> 718; the widest DONE text of the shipped registry is 619 px)
COLL_GO_W, COLL_GO_GAP = 80, 4
COLL_TR_REW_GO = COLL_TR_REW - COLL_GO_W - COLL_GO_GAP
assert COLL_TR_H == SUI.BTN_SMALL_H and COLL_TR_REW_GO > 0''')
rep('''def coll_det_tier(t=None, col=None, tc=None):''', '''def coll_det_tier(t=None, col=None, tc=None, craft=False):''')
rep('''             SUI.label("SkyyCRew" + t, "", "default", w=w[3], h=COLL_TR_H, col=tc, fit=False)]
    row = SUI.panel(''', '''             SUI.label("SkyyCRew" + t, "", "default", w=w[3] if not craft else COLL_TR_REW_GO, h=COLL_TR_H, col=tc, fit=False)]
    if craft:      # 0.2.8: the CRAFT button #SkyyCTr<t>Go (bound ccraft<t>, not locking: CollPage.bindFree)
        cells.append(SUI.button("SkyyCTr" + t + "Go", "Craft", "secondary", "small", w=COLL_GO_W, h=COLL_TR_H, anchor={"left": COLL_GO_GAP}))
    row = SUI.panel(''')

# ---------------------------------------------------------------------------------------------------------------- buildDetail
rep('''  String fc = ct >= mx ? "/*=MAXCOL=*/" : acc;
  bind(ev, "SkyyCBack", "cback");''', '''  String fc = ct >= mx ? "/*=MAXCOL=*/" : acc;
  boolean craftOn = @PKG@.CollCraft.cmd() != null;
  java.util.TreeSet un = craftOn ? @PKG@.CollUnlocks.compute(d) : null;
  bind(ev, "SkyyCBack", "cback");''')
rep_ok('''    b.set("#SkyyCRew" + t + ".Text", @PKG@.CollReg.rewardTextB(R, c, t, t > ct && t <= bt) + (t > ct && t <= bt ? "  (paid when reached)" : ""));''',
       '''    String rtx = @PKG@.CollReg.rewardTextB(R, c, t, t > ct && t <= bt) + (t > ct && t <= bt ? "  (paid when reached)" : "");
    b.set("#SkyyCRew" + t + ".Text", cq != null ? @PKG@.CollCraft.fitPx(rtx, CRAFTREW) : rtx);   // 0.2.8: a CRAFT row's cell is 84 px shorter''')
rep('''/*=LOOK=*/
/*=TIER=*/
    b.set("#SkyyCTr" + t + "S.Text", st);''', '''/*=LOOK=*/
    String cq = craftOn && t <= eff ? @PKG@.CollCraft.query(@PKG@.CollReg.recipesAt(c, t), un) : null;
    if (cq != null) {
/*=TIERGO=*/
      bindFree(ev, "SkyyCTr" + t + "Go", "ccraft" + t);
    } else {
/*=TIER=*/
    }
    b.set("#SkyyCTr" + t + "S.Text", st);''')
rep('''    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 4), "BUYROW": coll_java(coll_det_buyrow(), 4),''',
    '''    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 6), "TIERGO": coll_java(coll_det_tier(craft=True), 6),
    "BUYROW": coll_java(coll_det_buyrow(), 4),''')

# ---------------------------------------------------------------------------------------------------------------- sample states
rep('''        for t in range(1, kw.get("tiers", 10) + 1):
            put(coll_det_tier(str(t), SUI.COLOR["success"], SUI.COLOR["rowName"]))''',
    '''        for t in range(1, kw.get("tiers", 10) + 1):
            put(coll_det_tier(str(t), SUI.COLOR["success"], SUI.COLOR["rowName"], craft=t in kw.get("craft", ())))''')
rep('''              ("detail", {"tiers": 7, "icon": False, "off": True}), ("detail", {"tiers": 20, "off": True}), ("recipes", {"lines": 0}),''',
    '''              ("detail", {"tiers": 7, "icon": False, "off": True}), ("detail", {"tiers": 20, "off": True}), ("recipes", {"lines": 0}),
              ("detail", {"tiers": 10, "off": True, "craft": [1, 2, 3]}), ("detail", {"tiers": 20, "craft": list(range(1, 21))}),
              ("detail", {"tiers": 9, "icon": False, "off": True, "craft": [1, 3, 5, 8]}),''')
rep('''COLL_VIEWS = coll_views()''', '''COLL_VIEWS = coll_views()
# 0.2.8: a CRAFT row is exactly as wide as a plain row (the rewards cell gave up the button's room) and the button fits the row height
assert SUI.render(coll_det_tier("1", "#ffffff", "#ffffff", craft=True)[0][1]).count("TextButton #SkyyCTr1Go ") == 1
assert "TextButton" not in SUI.render(coll_det_tier("1", "#ffffff", "#ffffff")[0][1])
assert sum(COLL_TR_SPEC.widths[:3]) + COLL_TR_REW_GO + COLL_GO_GAP + COLL_GO_W == sum(COLL_TR_SPEC.widths), COLL_TR_SPEC.widths''')

# ---------------------------------------------------------------------------------------------------------------- page id + checked
rep('''COLL_PAGE_CHECKED = "be0dca34bcb2"''', '''COLL_PAGE_CHECKED = "%s"   # 0.2.8: SkyyCollections/test_skyycollections_0.2.8.py (tools/collections_0_2_8_patch.py PAGE_CHECKED)''' % PAGE_CHECKED)
for _old in ('''    print("collections page %s = the page SkyyCollections/test_skyycollections_0.2.5.py last passed on" % COLL_PAGE_ID)''',):
    rep(_old, _old.replace("test_skyycollections_0.2.5.py", "test_skyycollections_0.2.8.py"))
rep('''    raise SystemExit("collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.5.py last passed on (%s) and "
                     "SKYY_REQUIRE_CHECKED_PAGE=1: no jar assembled. Build without the flag, run the harness, then set PAGE_CHECKED "
                     "in tools/coll_0_2_5_patch.py and regenerate" % (COLL_PAGE_ID, COLL_PAGE_CHECKED))''',
    '''    raise SystemExit("collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.8.py last passed on (%s) and "
                     "SKYY_REQUIRE_CHECKED_PAGE=1: no jar assembled. Build without the flag, run the harness, then set PAGE_CHECKED "
                     "in tools/collections_0_2_8_patch.py and regenerate" % (COLL_PAGE_ID, COLL_PAGE_CHECKED))''')
rep('''    print("WARNING: collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.5.py last passed on (%s): the kit "
          "output changed the page. Run the harness, then set PAGE_CHECKED in tools/coll_0_2_5_patch.py and regenerate; never deploy "''',
    '''    print("WARNING: collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.8.py last passed on (%s): the kit "
          "output changed the page. Run the harness, then set PAGE_CHECKED in tools/collections_0_2_8_patch.py and regenerate; never deploy "''')

# ---------------------------------------------------------------------------------------------------------------- bindFree + the click
rep('''M(page, r"""
public static void bind(@UEB@ ev, String id, String payload) {
  ev.addEventBinding(@BT@.Activating, "#" + id, @EVD@.of("a", payload));
}""")''', '''M(page, r"""
public static void bind(@UEB@ ev, String id, String payload) {
  ev.addEventBinding(@BT@.Activating, "#" + id, @EVD@.of("a", payload));
}""")
# 0.2.8: the CRAFT button's binding does not lock the interface (the SkyySacks search field / SkyyMenu grid pattern): its click opens
# another mod's page through a command, which answers the client in place of a rebuild of this page
M(page, r"""
public static void bindFree(@UEB@ ev, String id, String payload) {
  ev.addEventBinding(@BT@.Activating, "#" + id, @EVD@.of("a", payload), false);
}""")''')
rep('''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''', '''# 0.2.8: a CRAFT click (tier t of the open collection) - re-checked against the live data (a stale / forged click on a locked tier,
# no /craft, no permission, a throwing dispatch -> the result line + a rebuild); sent -> nothing else (SkyySacks' page replaces this one)
M(page, r"""
public void craftClick(int t) {
  String msg = null;
  @PKG@.RegData R = @PKG@.CollReg.D;
  @PKG@.CollData d = @PKG@.CollStore.data(this.playerRef.getUuid());
  int c = this.coll;
  if (R == null || d == null || this.view != 2 || c < 0 || c >= R.n || R.hidden[c]) msg = "Collections are not loaded.";
  else {
    int ct = @PKG@.CollReg.tierOf(R, c, @PKG@.CollStore.sum(d, R, c));
    int bt = @PKG@.CollStore.boughtTier(d, R, c);
    int eff = ct > bt ? ct : bt;
    String[] rs = null;
    if (t >= 1 && t <= eff) rs = @PKG@.CollReg.recipesAt(c, t);
    java.util.TreeSet un = @PKG@.CollUnlocks.compute(d);
    String q = null;
    if (rs != null) q = @PKG@.CollCraft.query(rs, un);
    if (q == null) msg = "That recipe is not unlocked yet.";
    else if (@PKG@.CollCraft.cmd() == null) msg = "Crafting (/craft) is not on this server.";
    else if (!@PKG@.CollCraft.one(rs, un)) {
      this.fcol = c; this.ftier = t; this.view = 3; this.rpage = 0; this.status = "";
      rebuild();
      return;
    }
    else msg = @PKG@.CollCraft.open(this.playerRef, q);
  }
  if (msg != null) { this.status = msg; rebuild(); }
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''')
rep('''    if (data.indexOf("cclose\\"") >= 0) { closePage(ref, st); return; }''',
    '''    if (data.indexOf("cclose\\"") >= 0) { closePage(ref, st); return; }
    if (data.indexOf("ccraft") >= 0) {
      for (int i = 1; i <= 20; i++) {
        if (data.indexOf("ccraft" + i + "\\"") >= 0) { craftClick(i); return; }
      }
      return;
    }''')

# ================================================================================================================ 0.2.8 part 2: the recipe lists
# Skyy 2026-10-09: "we have unlocked recopies, we need a locked recopies tab, that tells you which collection you unlock something in."
# The UNLOCKED RECIPES view (3) and the new LOCKED RECIPES view (4) are one paged list well (14 rows of 32 px, the tier table's row look,
# column heads) built by buildRecipes. Unlocked rows end in a CRAFT button (the tier rows' /craft path, no button without /craft);
# locked rows (every recipe a visible collection lists that CollUnlocks.compute does not give the player; free bags = unlocked) say
# "<Collection> tier <roman>" + "count / threshold" of the tier the player is closest to, closest first, and end in OPEN = that
# collection's page, whose Back button then returns to the list ("< Back to list").
def rep_span(start, end, new):
    """replace the text from the unique `start` up to (not including) the unique `end`"""
    global s
    assert s.count(start) == 1 and s.count(end) == 1 and s.index(start) < s.index(end), (start[:80], end[:80])
    a, b = s.index(start), s.index(end)
    GONE_OK.update(s[a:b].split(LF))
    s = s[:a] + new + s[b:]


# ---- the page state: the list page, where the collection page's Back goes, the rows on the page (recipe id / collection)
rep('''F(page, "public int[] cards;")''', '''F(page, "public int[] cards;")
F(page, "public int rpage;")       # 0.2.8: the page of the recipe lists (views 3 / 4)
F(page, "public int back;")        # 0.2.8: 4 = the collection page was opened from the locked list (Back returns there)
F(page, "public String[] rrid;")   # 0.2.8: the recipe id of each list row on the page (a click re-checks it)
F(page, "public int[] rcol;")      # 0.2.8: the collection of each list row (-1 = auto rule)
F(page, "public int fcol;")        # 0.2.8 review: the Unlocked list shows only collection fcol tier ftier (a CRAFT row's chooser) ...
F(page, "public int ftier;")       # ... while ftier > 0; its Back returns to that collection's page''')

# ---- the look: the two lists (kit calls), the height budget
rep_span('''# ---------------------------------------------------------------- UNLOCKED RECIPES: heading + two list columns''',
         '''# ---------------------------------------------------------------- ERROR (the counts file or the registry cannot be read)''',
         '''# ---------------------------------------------------------------- RECIPE LISTS (0.2.8): UNLOCKED (view 3) + LOCKED (view 4), one paged list
# the heading, #SkyyCRSub, the column heads #SkyyCRHead, the list well #SkyyCRList of 14 rows #SkyyCRr<i> (the tier rows' look: the
# list row panel, one 32 px line) and the pager #SkyyCRPager. A row: the recipe #SkyyCRr<i>N, where #SkyyCRr<i>W, (locked) the
# progress #SkyyCRr<i>P and the small Secondary button #SkyyCRr<i>Go (CRAFT / OPEN, 80 px like the tier rows' CRAFT).
COLL_RL_ROWS = 14
COLL_RL_H = SUI.BTN_SMALL_H                                                # 32
COLL_RL_LIST_H = SUI.list_well_h(COLL_RL_ROWS, COLL_RL_H)                  # 498
COLL_RL_PAD = 8
COLL_RL_TXT = COLL_GRID_IN - COLL_RL_PAD - COLL_GO_GAP - COLL_GO_W         # 986: the text cells
COLL_RL_COLS = {"un": [("Recipe", 470), ("Unlocked by", COLL_RL_TXT - 470)],
                "lk": [("Recipe", 420), ("Unlocks at", 340), ("Progress", COLL_RL_TXT - 760)]}
COLL_RL_SPEC = dict((k, SUI.column_spec(v, avail=COLL_GRID_IN, pad_left=COLL_RL_PAD)) for k, v in COLL_RL_COLS.items())
COLL_RL_TITLE = {"un": "Unlocked recipes", "lk": "Locked recipes"}
COLL_RL_GO = {"un": "Craft", "lk": "Open"}
assert all(sum(sp.widths) == COLL_RL_TXT for sp in COLL_RL_SPEC.values())


def coll_rl_head(kind):
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.label(None, COLL_RL_TITLE[kind], "heading", h=28, wrap=False))
    ap.add("SkyyColl", SUI.label("SkyyCRSub", "", "default", h=26, anchor={"bottom": 8}))
    ap.add("SkyyColl", COLL_RL_SPEC[kind].heads("SkyyCRHead", outside=SUI.WELL_LIST_PAD))
    ap.add("SkyyColl", SUI.list_well("SkyyCRList", w=COLL_IW, h=COLL_RL_LIST_H))
    return ap


def coll_rl_row(kind, i=None, go=False):
    """One list row; the cells are runtime texts (fit=False: clipped in the Java, CollUtil.clip)."""
    i = _J(i, "i", "0")
    w = COLL_RL_SPEC[kind].widths
    r = "SkyyCRr" + i
    cells = [SUI.label(r + "N", "", "default", w=w[0], h=COLL_RL_H, col="rowName", fit=False),
             SUI.label(r + "W", "", "default", w=w[1], h=COLL_RL_H, fit=False)]
    if kind == "lk":
        cells.append(SUI.label(r + "P", "", "default", w=w[2], h=COLL_RL_H, col="value", fit=False))
    if go:
        cells.append(SUI.button(r + "Go", COLL_RL_GO[kind], "secondary", "small", w=COLL_GO_W, h=COLL_RL_H, anchor={"left": COLL_GO_GAP}))
    if kind == "lk":   # 0.2.8 review: the whole row is clickable - the WorldEventListRow select Button (SUI.panel_row's #<id>Sel,
        # the kit's row_style: the row colour + hover / pressed + the light click), fixed width, then the OPEN button outside it
        sel = "Button #%sSel { %sLayoutMode: Left; Padding: (Left: %d); %s }" % (
            r, SUI._anchor(COLL_RL_PAD + COLL_RL_TXT, COLL_RL_H), COLL_RL_PAD, SUI.row_style("normal"))
        row = SUI.group(r, "Left", h=COLL_RL_H, anchor={"bottom": SUI.ROW_GAP})
        txt, btn = (cells[:-1], cells[-1:]) if go else (cells, [])
        return SUI.Appends([("SkyyCRList", coll_inside(row, [coll_inside(sel, txt)] + btn))])
    row = SUI.panel(r, "row", h=COLL_RL_H, layout="Left", pad={"left": COLL_RL_PAD}, anchor={"bottom": SUI.ROW_GAP})
    return SUI.Appends([("SkyyCRList", coll_inside(row, cells))])


def coll_rl_pager():
    return SUI.pager("SkyyColl", "SkyyCRPager", COLL_IW, prev_on=SUI.J("this.rpage > 0"), next_on=SUI.J("this.rpage < pages - 1"),
                     btn_w=COLL_PG_BTN, caption_w=COLL_PG_CAP, gap=COLL_PG_GAP,
                     ids={"row": "SkyyCRPager", "prev": "SkyyCRPrev", "page": "SkyyCRPage", "next": "SkyyCRNext"})


def coll_rl_page1():
    ap = SUI.Appends()
    ap.add("SkyyColl", SUI.group("SkyyCRPager", "Left", h=SUI.BTN_SMALL_H, anchor={"top": 8}))
    ap.add("SkyyCRPager", SUI.label("SkyyCRPage", "", "default", w=COLL_PG_CAP, h=SUI.BTN_SMALL_H, align="Center",
                                    anchor={"left": COLL_PG_CAP_X}))
    return ap


def coll_rl_bottom():
    return coll_bottom("SkyyCFoot", [COLL_BACK], [COLL_CLOSE], COLL_RC_USED)


''')
rep_ok('''COLL_RC_USED = 28 + (26 + 8) + COLL_RC_H + COLL_BOTTOM_H''',
       '''COLL_RC_USED = 28 + (26 + 8) + 30 + COLL_RL_LIST_H + (SUI.BTN_SMALL_H + 8) + COLL_BOTTOM_H   # 0.2.8: the recipe lists''')

# ---- Home: LOCKED RECIPES next to UNLOCKED RECIPES
rep_ok('''    ap += coll_bottom("SkyyCFoot", [coll_foot_btn("SkyyCRecipes", "Unlocked recipes", COLL_RECIPES_W),
                                    coll_foot_btn("SkyyCRefresh", "Refresh", COLL_BTN, left=True)], [COLL_CLOSE], COLL_HOME_USED)''',
       '''    ap += coll_bottom("SkyyCFoot", [coll_foot_btn("SkyyCRecipes", "Unlocked recipes", COLL_RECIPES_W),
                                    coll_foot_btn("SkyyCLocked", "Locked recipes", COLL_RECIPES_W, left=True),   # 0.2.8
                                    coll_foot_btn("SkyyCRefresh", "Refresh", COLL_BTN, left=True)], [COLL_CLOSE], COLL_HOME_USED)''')
rep_ok('''COLL_RECIPES_W = coll_btn_w(["Unlocked recipes"])''', '''COLL_RECIPES_W = coll_btn_w(["Unlocked recipes", "Locked recipes"])''')
rep('''  bind(ev, "SkyyCRecipes", "crecipes");''', '''  bind(ev, "SkyyCRecipes", "crecipes");
  bind(ev, "SkyyCLocked", "clocked");''')

# ---- the collection page's Back: "< Back to list" when it was opened from the locked list
rep_ok('''  b.appendInline("#SkyyCHead", CATBACK[R.cat[c]]);''', '''  b.appendInline("#SkyyCHead", this.back == 4 ? LISTBACK : CATBACK[R.cat[c]]);''')
rep_ok('''for _m in COLL_CATOPEN + COLL_CATBACK:''', '''COLL_LISTBACK = coll_foot_btn("SkyyCBack", "< Back to list", COLL_BACKTO_W, sound="cancel")   # 0.2.8
for _m in COLL_CATOPEN + COLL_CATBACK + [COLL_LISTBACK]:''')
rep_ok('''               "public static final String[] CATBACK = new String[] { %s };" % ", ".join(SUI.java_lit(m) for m in COLL_CATBACK)]''',
       '''               "public static final String[] CATBACK = new String[] { %s };" % ", ".join(SUI.java_lit(m) for m in COLL_CATBACK),
               "public static final String LISTBACK = %s;" % SUI.java_lit(COLL_LISTBACK),
               "public static final int RLROWS = %d;" % COLL_RL_ROWS,
               "public static final int CRAFTREW = %d;" % COLL_TR_REW_GO]''')

# ---- the list method (views 3 and 4)
rep_span('''COLL_RC_TPL = r"""''', '''COLL_BUILD_TPL = r"""''', r'''COLL_RC_TPL = r"""
public void buildRecipes(@UCB@ b, @UEB@ ev, @PKG@.CollData d, @PKG@.RegData R) {
  boolean lk = this.view == 4;
  java.util.ArrayList rows = lk ? lockedRows(d, R) : unlockedRows(d, R);
  boolean craftOn = !lk && @PKG@.CollCraft.cmd() != null;
  boolean flt = !lk && this.ftier > 0 && this.fcol >= 0 && this.fcol < R.n;
  if (flt) {
    String[] frs = @PKG@.CollReg.recipesAt(this.fcol, this.ftier);
    java.util.ArrayList keep = new java.util.ArrayList();
    for (int k = 0; k < rows.size(); k++) {
      Object[] e = (Object[]) rows.get(k);
      for (int j = 0; j < frs.length; j++) if (e[0].equals(frs[j])) { keep.add(e); break; }
    }
    rows = keep;
  }
  int pages = (rows.size() + RLROWS - 1) / RLROWS;
  if (pages < 1) pages = 1;
  if (this.rpage >= pages) this.rpage = pages - 1;
  if (this.rpage < 0) this.rpage = 0;
  this.rrid = new String[RLROWS];
  this.rcol = new int[RLROWS];
  for (int i = 0; i < RLROWS; i++) this.rcol[i] = -1;
  if (lk) {
/*=HEADLK=*/
  } else {
/*=HEADUN=*/
  }
  String sub;
  if (lk) sub = rows.isEmpty() ? "No locked recipes - every recipe the collections unlock is yours." : rows.size() + " recipe(s) still locked, closest first. Click a row to see that collection.";
  else if (flt) sub = R.name[this.fcol] + " tier " + @PKG@.CollUtil.roman(this.ftier) + ": " + rows.size() + " unlocked recipe(s) - CRAFT the one you want. Back returns to " + R.name[this.fcol] + ".";
  else if (rows.isEmpty()) sub = "No recipes yet - reach tier I of Wheat, Oak Log or Cobblestone for the first ones.";
  else sub = rows.size() + " recipe(s). " + (craftOn ? "CRAFT opens /craft searching for it (Nothing matches? Use its Collections tab)." : "Craft them in /craft - Collections tab (materials still needed, no bench).");
  b.set("#SkyyCRSub.Text", sub);
  for (int i = 0; i < RLROWS; i++) {
    int k = this.rpage * RLROWS + i;
    if (k >= rows.size()) break;
    Object[] e = (Object[]) rows.get(k);
    if (lk) {
/*=ROWLK=*/
      bind(ev, "SkyyCRr" + i + "Sel", "crgo" + i);   // review fix: the whole row is the click (the vanilla list row button)
      bind(ev, "SkyyCRr" + i + "Go", "crgo" + i);
      b.set("#SkyyCRr" + i + "P.Text", (String) e[3]);
    } else if (craftOn) {
/*=ROWUNGO=*/
      bindFree(ev, "SkyyCRr" + i + "Go", "crcraft" + i);
    } else {
/*=ROWUN=*/
    }
    this.rrid[i] = (String) e[0];
    this.rcol[i] = ((Integer) e[4]).intValue();
    b.set("#SkyyCRr" + i + "N.Text", (String) e[1]);
    b.set("#SkyyCRr" + i + "W.Text", (String) e[2]);
  }
  if (pages > 1) {
/*=PAGER=*/
    bind(ev, "SkyyCRPrev", "crprev");
    bind(ev, "SkyyCRNext", "crnext");
  } else {
/*=PAGE1=*/
  }
  b.set("#SkyyCRPage.Text", "Page " + (this.rpage + 1) + " / " + pages);
/*=BOTTOM=*/
  bind(ev, "SkyyCBack", "cback");
  bind(ev, "SkyyCClose", "cclose");
}"""
''')
rep_ok('''  else if (this.view == 3) buildRecipes(b, ev, d, R);''', '''  else if (this.view == 3 || this.view == 4) buildRecipes(b, ev, d, R);''')
rep_span('''COLL_SRC["buildRecipes"] = coll_fill(COLL_RC_TPL, {''', '''COLL_SRC["build"] = coll_fill(COLL_BUILD_TPL,''',
         '''COLL_SRC["buildRecipes"] = coll_fill(COLL_RC_TPL, {
    "HEADUN": coll_java(coll_rl_head("un"), 4), "HEADLK": coll_java(coll_rl_head("lk"), 4),
    "ROWLK": coll_java(coll_rl_row("lk", go=True), 6), "ROWUNGO": coll_java(coll_rl_row("un", go=True), 6),
    "ROWUN": coll_java(coll_rl_row("un"), 6), "PAGER": coll_java(coll_rl_pager(), 4), "PAGE1": coll_java(coll_rl_page1(), 4),
    "BOTTOM": coll_java(coll_rl_bottom(), 2)})
''')

# ---- sample states: the lists (both kinds, with / without buttons, 0 / some / 14 rows, one page / a pager), the list Back
rep_span('''    elif view == "recipes":''', '''    return ap


def coll_views():''', '''    elif view == "recipes":                # 0.2.8 (kw: kind "un" / "lk", rows, go, pages)
        kind = kw.get("kind", "un")
        put(coll_rl_head(kind))
        for i in range(kw.get("rows", COLL_RL_ROWS)):
            put(coll_rl_row(kind, str(i), go=kw.get("go", True) or kind == "lk"))
        put(coll_rl_pager() if kw.get("pages", 1) > 1 else coll_rl_page1())
        put(coll_rl_bottom())
''')
rep_ok('''        ap.add("SkyyCHead", COLL_CATBACK[2])''', '''        ap.add("SkyyCHead", COLL_LISTBACK if kw.get("listback") else COLL_CATBACK[2])''')
rep_ok('''("recipes", {"lines": 0}),''', '''("detail", {"tiers": 9, "listback": True}),''')
GONE_OK.add('''              ("detail", {"tiers": 7, "icon": False, "off": True}), ("detail", {"tiers": 20, "off": True}), ("recipes", {"lines": 0}),''')
rep_ok('''              ("recipes", {"lines": 40}), ("recipes", {"lines": 57})]''',
       '''              ("recipes", {"kind": "un", "rows": 0}), ("recipes", {"kind": "un", "rows": 14, "pages": 3}),
              ("recipes", {"kind": "un", "rows": 5, "go": False}), ("recipes", {"kind": "un", "rows": 14, "go": False, "pages": 2}),
              ("recipes", {"kind": "lk", "rows": 0}), ("recipes", {"kind": "lk", "rows": 3}), ("recipes", {"kind": "lk", "rows": 14, "pages": 9})]''')

# ---- the list rows (Java). unlockedRows = 0.2.7's Unlocked recipes lines (the same set as CollUnlocks.compute), split into cells;
# lockedRows = every recipe of a visible collection's tier the player has not reached that compute() does not give them (free bags =
# unlocked, as sacks:freebags makes them), each at the tier the player is closest to (count / threshold highest, then fewest items
# missing, then registry order), sorted closest first, then by name. Row = {recipe id, name, where, progress, Integer collection}.
rep('''M(page, COLL_SRC["statusColor"])''', '''M(page, COLL_SRC["statusColor"])
M(page, r"""
public static java.util.ArrayList unlockedRows(@PKG@.CollData d, @PKG@.RegData R) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    int ct = @PKG@.CollStore.countTier(d, R, c);
    int eff = @PKG@.CollStore.effTier(d, R, c);
    for (int t = 1; t <= eff; t++) {
      String[] rs = @PKG@.CollReg.recipesAt(c, t);
      for (int i = 0; i < rs.length; i++) {
        if (t > ct && @PKG@.CollUtil.bagRank(rs[i]) > @PKG@.CollReg.BYP_BAGMAX) continue;
        if (!seen.add(rs[i])) continue;
        out.add(new Object[] { rs[i], @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rs[i]), 44), R.name[c] + " tier " + @PKG@.CollUtil.roman(t) + (t > ct ? " (bought)" : ""), null, Integer.valueOf(c) });
      }
    }
  }
  java.util.Iterator it = @PKG@.CollUnlocks.compute(d).iterator();
  while (it.hasNext()) {
    String rid = (String) it.next();
    if (seen.add(rid)) out.add(new Object[] { rid, @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rid), 44), "auto rule", null, Integer.valueOf(-1) });
  }
  return out;
}""")
M(page, r"""
public static int lockCmp(Object[] a, Object[] b) {
  long sa = ((Long) a[6]).longValue();
  long ta = ((Long) a[7]).longValue();
  long sb = ((Long) b[6]).longValue();
  long tb = ((Long) b[7]).longValue();
  double ra = ta > 0L ? (double) sa / (double) ta : 0.0;
  double rb = tb > 0L ? (double) sb / (double) tb : 0.0;
  if (ra > rb) return -1;
  if (ra < rb) return 1;
  long ma = ta - sa;
  long mb = tb - sb;
  if (ma < mb) return -1;
  if (ma > mb) return 1;
  return 0;
}""")
M(page, r"""
public static java.util.ArrayList lockedRows(@PKG@.CollData d, @PKG@.RegData R) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (d == null || R == null) return out;
  java.util.TreeSet un = @PKG@.CollUnlocks.compute(d);
  boolean free = @PKG@.CollUtil.freeBags();
  java.util.HashMap best = new java.util.HashMap();
  java.util.ArrayList order = new java.util.ArrayList();
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    long sm = @PKG@.CollStore.sum(d, R, c);
    int ct = @PKG@.CollReg.tierOf(R, c, sm);
    int mx = @PKG@.CollReg.maxTier(R, c);
    for (int t = ct + 1; t <= mx; t++) {
      String[] rs = @PKG@.CollReg.recipesAt(c, t);
      for (int i = 0; i < rs.length; i++) {
        String rid = rs[i];
        if (rid == null || un.contains(rid)) continue;
        if (free && @PKG@.CollUtil.isBag(rid)) continue;
        Object[] e = new Object[] { rid, null, null, null, Integer.valueOf(c), Integer.valueOf(t), Long.valueOf(sm), Long.valueOf(@PKG@.CollReg.threshold(R, c, t)) };
        Object[] cur = (Object[]) best.get(rid);
        if (cur == null) { best.put(rid, e); order.add(rid); }
        else if (lockCmp(e, cur) < 0) best.put(rid, e);
      }
    }
  }
  for (int j = 0; j < order.size(); j++) {
    Object[] e = (Object[]) best.get(order.get(j));
    int c = ((Integer) e[4]).intValue();
    e[1] = @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe((String) e[0]), 40);
    e[2] = @PKG@.CollUtil.clip(R.name[c] + " tier " + @PKG@.CollUtil.roman(((Integer) e[5]).intValue()), 36);
    e[3] = @PKG@.CollUtil.fmt(((Long) e[6]).longValue()) + " / " + @PKG@.CollUtil.fmt(((Long) e[7]).longValue());
    int at = out.size();
    for (int k = 0; k < out.size(); k++) {
      Object[] o = (Object[]) out.get(k);
      int cmp = lockCmp(e, o);
      if (cmp == 0) cmp = ((String) e[1]).compareTo((String) o[1]);
      if (cmp < 0) { at = k; break; }
    }
    out.add(at, e);
  }
  return out;
}""")''')

# ---- the clicks: CRAFT of a list row (re-checked: still unlocked), OPEN of a locked row (a visible collection), the pager
rep('''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''', '''M(page, r"""
public void rowCraft(int i) {
  String msg = null;
  @PKG@.RegData R = @PKG@.CollReg.D;
  @PKG@.CollData d = @PKG@.CollStore.data(this.playerRef.getUuid());
  String rid = this.view == 3 && this.rrid != null && i >= 0 && i < this.rrid.length ? this.rrid[i] : null;
  if (R == null || d == null) msg = "Collections are not loaded.";
  else if (rid == null) msg = "That recipe is not on this page any more.";
  else {
    String q = @PKG@.CollCraft.query(new String[] { rid }, @PKG@.CollUnlocks.compute(d));
    if (q == null) msg = "That recipe is not unlocked yet.";
    else msg = @PKG@.CollCraft.open(this.playerRef, q);
  }
  if (msg != null) { this.status = msg; rebuild(); }
}""")
M(page, r"""
public void rowOpen(int i) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  int c = this.view == 4 && this.rcol != null && i >= 0 && i < this.rcol.length ? this.rcol[i] : -1;
  if (R == null || c < 0 || c >= R.n || R.hidden[c]) { this.status = "That collection is not available."; rebuild(); return; }
  this.coll = c; this.cat = R.cat[c]; this.view = 2; this.back = 4;
  rebuild();
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''')
rep('''    this.status = "";
    if (data.indexOf("chome\\"") >= 0)''', '''    if (data.indexOf("crcraft") >= 0) {
      for (int i = 0; i < RLROWS; i++) {
        if (data.indexOf("crcraft" + i + "\\"") >= 0) { rowCraft(i); return; }
      }
      return;
    }
    this.status = "";
    if (data.indexOf("clocked\\"") >= 0) { this.view = 4; this.rpage = 0; this.ftier = 0; rebuild(); return; }
    if (data.indexOf("cback\\"") >= 0 && this.view == 3 && this.ftier > 0) { this.view = 2; this.coll = this.fcol; this.ftier = 0; rebuild(); return; }
    if (data.indexOf("chome\\"") >= 0) this.ftier = 0;
    if (data.indexOf("crprev\\"") >= 0) { if (this.rpage > 0) this.rpage = this.rpage - 1; rebuild(); return; }
    if (data.indexOf("crnext\\"") >= 0) { this.rpage = this.rpage + 1; rebuild(); return; }
    for (int i = 0; i < RLROWS; i++) {
      if (data.indexOf("crgo" + i + "\\"") >= 0) { rowOpen(i); return; }
    }
    if (data.indexOf("chome\\"") >= 0)''')
rep_ok('''    if (data.indexOf("cback\\"") >= 0) { this.view = this.view == 2 ? 1 : 0; rebuild(); return; }''',
       '''    if (data.indexOf("cback\\"") >= 0) { this.view = this.view == 2 ? (this.back == 4 ? 4 : 1) : 0; rebuild(); return; }''')
rep_ok('''    if (data.indexOf("crecipes\\"") >= 0) { this.view = 3; rebuild(); return; }''',
       '''    if (data.indexOf("crecipes\\"") >= 0) { this.view = 3; this.rpage = 0; this.ftier = 0; rebuild(); return; }''')
rep_ok('''        if (this.cards != null && i < this.cards.length && this.cards[i] >= 0) { this.coll = this.cards[i]; this.view = 2; }''',
       '''        if (this.cards != null && i < this.cards.length && this.cards[i] >= 0) { this.coll = this.cards[i]; this.view = 2; this.back = 0; }''')

PART3 = True   # (marker for the guards below)
# ================================================================================================================ 0.2.8 part 3: Mining bag from Cobblestone
# Skyy 2026-10-09: "the mining bag should come from cobble collection, not iron" (docs/answered/bags.md LOCKED; replaces the 0.2.3
# Mining = Iron lock). The four Mining bag recipes (Normal I, Unique III, Rare V, Legendary VII) unlock from the Cobblestone collection.
#  - Default rewards.properties: Cobblestone.1 = Copper Pickaxe + Normal Mining Bag, Cobblestone.3 / .5 / .7 = the Unique / Rare /
#    Legendary Mining Bag; Iron has no bag line; the proposed ore comment lines go back to their plain 0.2.2 form; a second marker comment
#    "# bags: Mining from Cobblestone (0.2.8)" under the 0.2.3 one (a fresh file never migrates; CollBagMigrate writes both markers when
#    it moves a 0.2.2 file, whose Mining ladder then lands on Cobblestone directly).
#  - CollCobMig.run (setup(), right after CollReg.loadAll - it needs the registry - and before CfgPub.start), ONCE (the marker), per
#    PROJECT-RULES 4: only lines still holding the 0.2.7 default change - an Iron.<t> line that is exactly its Mining bag token is removed
#    and the token goes to Cobblestone.<t>: appended to a Cobblestone.<t> line still at its 0.2.7 default (Cobblestone.1 = the Copper
#    Pickaxe), or a new Cobblestone.<t> line in the Iron line's place where 0.2.7 had none, or nothing more when Cobblestone.<t> already
#    lists it. A hand-edited Iron.<t> or Cobblestone.<t> line keeps that rarity where it is (both lines kept, logged with how to move it
#    by hand). The four comment lines that said "Mining from Iron" change only where they are still exactly 0.2.7's. Every other byte and
#    the line endings are kept (ISO-8859-1 in and out); a check re-reads both texts with the loader's rules and refuses to write unless
#    the only differences are the moved tokens. Before the write: the old file becomes a History version (config-history, verified),
#    then the kit's atomicWrite, one config-changes.log line per changed table entry (rewards[Iron.1] ... -> (none); rewards[Cobblestone.1]
#    old -> old,bag) = Server Setup -> Changes -> Undo, a block in migration-bags.log, one INFO line, and the rewards table is re-read.
#  - NEVER TAKE A RECIPE AWAY: before the rewards file is written, every counts file (each profile) whose Iron collection had a moved
#    bag tier - reached by count, or bought within bagMax, exactly 0.2.7's CollUnlocks.compute rule - gets the meta key _keptbag.Mining
#    (a bit per rarity, OR-ed, so a retried start never loses one); CollUnlocks.compute adds those bag recipes for that profile forever.
#    A failed counts write stops the move (WARN, nothing else written, retried at the next start).
#  - Cobblestone tiers already past: unlocks are computed from the counts, so a player whose Cobblestone is at tier I / III / V / VII
#    has those Mining bags the moment their unlock list is next built (when they join, a collection credit, /collections, /craft).
#  - Texts: Server Setup help, the read-only Magic Bags rows, the gaps WARN example, the manifest; coll:fn:where follows the table.
#  - Unlocked recipes list: a kept bag says "Iron Ore - kept (unlocked before 0.2.8)".
rep_ok('''BAG_COLL = {"Mining": "Iron", "Foraging": "OakLog", "Farming": "Wheat", "Combat": "Bone", "Smithing": "HideLight"}  # Mining = Skyy's lock''',
    '''BAG_COLL_027 = {"Mining": "Iron", "Foraging": "OakLog", "Farming": "Wheat", "Combat": "Bone", "Smithing": "HideLight"}  # 0.2.3 - 0.2.7
BAG_COLL = dict(BAG_COLL_027, Mining="Cobblestone")   # 0.2.8: Skyy 2026-10-09 "the mining bag should come from cobble collection, not iron"''')
rep_ok('''BAG_PREFIX = {"Mining": "Ore_", ''', '''BAG_PREFIX = {"Mining": "Rock_", ''')   # SkyySacks homeOf: Ore_ / Rubble_ / Rock_ / Soil_ = Mining
rep('''RW_MARK = "# bags: rarity ladder (0.2.3)"''', '''RW_MARK = "# bags: rarity ladder (0.2.3)"
RW_MARK2 = "# bags: Mining from Cobblestone (0.2.8)"   # 0.2.8: CollCobMig's run-once marker (a comment the loader skips)''')
rep_ok('''    "# Mining from Iron, Foraging from OakLog, Farming from Wheat, Combat from Bone, Smithing from HideLight. Keep one line per tier.",
    RW_MARK,''', '''    "# Mining from Cobblestone, Foraging from OakLog, Farming from Wheat, Combat from Bone, Smithing from HideLight. Keep one line per tier.",
    RW_MARK,
    RW_MARK2,''')
rep_ok('''assert [o for o, _n in ORE_MERGED] == ["#Iron.3=" + REC("Armor_Iron_Hands"), "#Iron.5=" + REC("Armor_Iron_Chest")], ORE_MERGED''',
       '''assert ORE_MERGED == [], ORE_MERGED   # 0.2.8: no bag shares a key with a proposed ore line any more (0.2.3 - 0.2.7: Iron.3 / Iron.5)
# ---- 0.2.8 CollCobMig tables: the 0.2.7 default lines of the moved keys and the 0.2.7 comment lines that named Iron
MV_TIERS = [tier for (_sfx, _rar, tier) in BAG_LADDER]
MV_IRON = ["%s.%d" % (BAG_COLL_027["Mining"], t) for t in MV_TIERS]
MV_COB = ["%s.%d" % (BAG_COLL["Mining"], t) for t in MV_TIERS]
MV_TOK = [BAG("Mining", sfx) for (sfx, _rar, _t) in BAG_LADDER]
_RW027 = {}
for _k, _tok in BASE_RW + [("%s.%d" % (BAG_COLL_027[t], tier), BAG(t, sfx)) for t in BAG_TYPES for (sfx, _rar, tier) in BAG_LADDER]:
    _RW027.setdefault(_k, []).append(_tok)
assert all(_RW027[k] == [tok] for k, tok in zip(MV_IRON, MV_TOK)), "0.2.7 default: each Iron bag line is exactly its bag token"
MV_COB_OLD = [",".join(_RW027.get(k, [])) for k in MV_COB]          # "" = 0.2.7 had no line for that key
assert MV_COB_OLD == [REC("Tool_Pickaxe_Copper"), "", "", ""], MV_COB_OLD
assert [RW_ENTRIES[k] for k in MV_COB] == [[REC("Tool_Pickaxe_Copper"), MV_TOK[0]], [MV_TOK[1]], [MV_TOK[2]], [MV_TOK[3]]]
assert not any(k.startswith("Iron.") for k in RW_ENTRIES), "0.2.8 default: no Iron bag line"
CM_OLD = ["# Mining from Iron, Foraging from OakLog, Farming from Wheat, Combat from Bone, Smithing from HideLight. Keep one line per tier.",
          RW_IRON_NOTE,
          "#Iron.3=%s,%s" % (BAG("Mining", "Medium"), REC("Armor_Iron_Hands")),
          "#Iron.5=%s,%s" % (BAG("Mining", "Rare"), REC("Armor_Iron_Chest"))]
CM_NEW = [CM_OLD[0].replace("Mining from Iron,", "Mining from Cobblestone,"), "",
          "#Iron.3=" + REC("Armor_Iron_Hands"), "#Iron.5=" + REC("Armor_Iron_Chest")]
assert CM_NEW[0] in RW and CM_NEW[2] in RW and CM_NEW[3] in RW and not any(c in RW for c in CM_OLD)
assert RW.index(RW_MARK2) == RW.index(RW_MARK) + 1''')

# ---- the class + its fields (constants only, so CollBagMigrate / CollUnlocks / CollPage compiled earlier can read them)
rep('''bpm = K("CollBypassMig")     # 0.2.5:''', '''cobm = K("CollCobMig")       # 0.2.8: the Mining bag ladder Iron -> Cobblestone in rewards.properties (once) + the kept bags
bpm = K("CollBypassMig")     # 0.2.5:''')
rep_ok('''ALL = (util, cio, rd, reg, drp, mig, cdat, sto, bmig, bpm, rew,''', '''ALL = (util, cio, rd, reg, drp, mig, cdat, sto, bmig, cobm, bpm, rew,''')
rep('''          "public static final String[] C_NEW = " + _jarr(["\\n".join(n) for _o, n in ORE_MERGED]) + ";"):
    F(bmig, f)''', '''          "public static final String[] C_NEW = " + _jarr(["\\n".join(n) for _o, n in ORE_MERGED]) + ";"):
    F(bmig, f)
for f in ("public static final String MARK2 = " + _jarr([RW_MARK2])[15:-2] + ";",            # 0.2.8 CollCobMig
          "public static final String OLD_MARK = " + _jarr([RW_MARK])[15:-2] + ";",
          "public static final String WHO = \\"SkyyCollections 0.2.8\\";",
          "public static final String KEEP_META = \\"_keptbag.Mining\\";",
          "public static final String[] MV_IRON = " + _jarr(MV_IRON) + ";",
          "public static final String[] MV_COB = " + _jarr(MV_COB) + ";",
          "public static final String[] MV_TOK = " + _jarr(MV_TOK) + ";",
          "public static final String[] KEEP_RID = " + _jarr([t[7:] for t in MV_TOK]) + ";",
          "public static final int[] MV_TIER = new int[] { " + ", ".join(str(t) for t in MV_TIERS) + " };",
          "public static final String[] MV_RAR = " + _jarr([r for (_s, r, _t) in BAG_LADDER]) + ";",
          "public static final String[] COB_OLD = " + _jarr(MV_COB_OLD) + ";",
          "public static final String[] CM_OLD = " + _jarr(CM_OLD) + ";",
          "public static final String[] CM_NEW = " + _jarr(CM_NEW) + ";"):
    F(cobm, f)''')
# CollBagMigrate (a 0.2.2 file): its ladder now puts Mining on Cobblestone directly, so it writes the 0.2.8 marker with its own
rep('''    lines.add(top, MARK);''', '''    lines.add(top, MARK);
    lines.add(top + 1, @PKG@.CollCobMig.MARK2);   // 0.2.8: the Mining ladder is already on Cobblestone''')

# ---- the pure parts (compiled before CollRewards / CollUnlocks / CollPage use them)
COB_JAVA = r'''# ================= 0.2.8 CollCobMig: the Mining bag ladder Iron -> Cobblestone (once) + the kept bags =================
# the loader's key form (CollReg.loadRewards): lower-case collection id + "." + the tier number; null for a line that is no entry
M(cobm, r"""
public static String rkey(String line) {
  if (line == null) return null;
  String ln = line.trim();
  if (ln.length() == 0 || ln.startsWith("#")) return null;
  int eq = ln.indexOf('=');
  if (eq <= 0) return null;
  String k = ln.substring(0, eq).trim();
  int dot = k.lastIndexOf('.');
  if (dot <= 0) return null;
  try { return k.substring(0, dot).trim().toLowerCase() + "." + Integer.parseInt(k.substring(dot + 1).trim()); } catch (Throwable t) { return null; }
}""")
M(cobm, r"""
public static String tok(String s) {
  String t = s.trim();
  if (t.startsWith("recipe:")) return "recipe:" + t.substring(7).trim();
  return t;
}""")
# the tokens of an entry line as the loader reads them (CollUtil.csv of the text after the first '='), "recipe: X" read as "recipe:X"
M(cobm, r"""
public static java.util.ArrayList toks(String line) {
  java.util.ArrayList out = new java.util.ArrayList();
  String ln = line.trim();
  int eq = ln.indexOf('=');
  if (eq <= 0) return out;
  String[] p = @PKG@.CollUtil.csv(ln.substring(eq + 1));
  for (int i = 0; i < p.length; i++) out.add(tok(p[i]));
  return out;
}""")
M(cobm, r"""
public static java.util.ArrayList toksOf(String value) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] p = @PKG@.CollUtil.csv(value);
  for (int i = 0; i < p.length; i++) out.add(tok(p[i]));
  return out;
}""")
# the whole table as the loader builds it: rkey -> tokens of every line of that key in file order
M(cobm, r"""
public static java.util.HashMap table(String[] l) {
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < l.length; i++) {
    String k = rkey(l[i]);
    if (k == null) continue;
    java.util.ArrayList t = (java.util.ArrayList) m.get(k);
    if (t == null) { t = new java.util.ArrayList(); m.put(k, t); }
    t.addAll(toks(l[i]));
  }
  return m;
}""")
M(cobm, r"""
public static String rtrim(String s) {
  int e = s.length();
  while (e > 0 && (s.charAt(e - 1) == ' ' || s.charAt(e - 1) == '\t')) e--;
  return s.substring(0, e);
}""")
M(cobm, r"""
public static String keyText(String line) {
  String ln = line.trim();
  return ln.substring(0, ln.indexOf('=')).trim();
}""")
M(cobm, r"""
public static String valText(String line) {
  String ln = line.trim();
  return ln.substring(ln.indexOf('=') + 1).trim();
}""")
# Pure text step (ISO-8859-1 chars in and out). null = the 0.2.8 marker is already in a comment line (nothing to do). Else
# { new text, String[] { entry, old, new }* for config-changes.log, String log lines, Integer mask of the moved rarities (bit j = MV_TOK[j]),
#   Integer lines kept by hand, Boolean the loader reads exactly the old table with only the moved tokens moved }.
M(cobm, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  int n = raw.length;
  String[] l = new String[n];
  for (int i = 0; i < n; i++) l[i] = raw[i].endsWith("\r") ? raw[i].substring(0, raw[i].length() - 1) : raw[i];
  int oldMark = -1;
  for (int i = 0; i < n; i++) {
    String t = l[i].trim();
    if (!t.startsWith("#")) continue;
    if (t.indexOf(MARK2.substring(2)) >= 0) return null;
    if (oldMark < 0 && t.equals(OLD_MARK)) oldMark = i;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  String[] rep = new String[n];
  boolean[] del = new boolean[n];
  java.util.ArrayList rows = new java.util.ArrayList();
  StringBuilder log = new StringBuilder();
  int mask = 0;
  int hand = 0;
  for (int j = 0; j < MV_TOK.length; j++) {
    String ik = rkey(MV_IRON[j] + "=x");
    String ck = rkey(MV_COB[j] + "=x");
    java.util.ArrayList il = new java.util.ArrayList();
    java.util.ArrayList cl = new java.util.ArrayList();
    for (int i = 0; i < n; i++) {
      String k = rkey(l[i]);
      if (k == null) continue;
      if (k.equals(ik)) il.add(Integer.valueOf(i));
      if (k.equals(ck)) cl.add(Integer.valueOf(i));
    }
    String what = "the " + MV_RAR[j] + " Mining Bag (" + MV_TOK[j].substring(7) + ")";
    if (il.size() != 1 || !toks(l[((Integer) il.get(0)).intValue()]).equals(toksOf(MV_TOK[j]))) {
      if (il.isEmpty()) log.append("  ").append(MV_IRON[j]).append(": no line (an admin's choice) - ").append(what).append(" left where it is\n");
      else {
        hand += il.size();
        for (int q = 0; q < il.size(); q++) log.append("  kept hand-edited line ").append(((Integer) il.get(q)).intValue() + 1).append(": ").append(l[((Integer) il.get(q)).intValue()].trim()).append(" - ").append(what).append(" stays there; move it to ").append(MV_COB[j]).append(" by hand if you like\n");
      }
      continue;
    }
    int ii = ((Integer) il.get(0)).intValue();
    boolean has = false;
    for (int q = 0; q < cl.size(); q++) if (toks(l[((Integer) cl.get(q)).intValue()]).contains(MV_TOK[j])) has = true;
    String iv = valText(l[ii]);
    if (has) {
      del[ii] = true;
      rows.add(keyText(l[ii])); rows.add(iv); rows.add("(none)");
      log.append("  removed line ").append(ii + 1).append(": ").append(l[ii].trim()).append(" (").append(MV_COB[j]).append(" already lists it)\n");
    } else if (cl.isEmpty() && COB_OLD[j].length() == 0) {
      String cr1 = raw[ii].endsWith("\r") ? "\r" : "";
      rep[ii] = MV_COB[j] + "=" + MV_TOK[j] + cr1;
      rows.add(keyText(l[ii])); rows.add(iv); rows.add("(none)");
      rows.add(MV_COB[j]); rows.add("(none)"); rows.add(MV_TOK[j]);
      log.append("  line ").append(ii + 1).append(": ").append(l[ii].trim()).append(" -> ").append(MV_COB[j]).append('=').append(MV_TOK[j]).append('\n');
    } else if (cl.size() == 1 && COB_OLD[j].length() > 0 && toks(l[((Integer) cl.get(0)).intValue()]).equals(toksOf(COB_OLD[j]))) {
      int ci = ((Integer) cl.get(0)).intValue();
      String cr2 = raw[ci].endsWith("\r") ? "\r" : "";
      String cv = valText(l[ci]);
      rep[ci] = rtrim(l[ci]) + "," + MV_TOK[j] + cr2;
      del[ii] = true;
      rows.add(keyText(l[ii])); rows.add(iv); rows.add("(none)");
      rows.add(keyText(l[ci])); rows.add(cv); rows.add(cv + "," + MV_TOK[j]);
      log.append("  removed line ").append(ii + 1).append(": ").append(l[ii].trim()).append("; appended to line ").append(ci + 1).append(": ").append(rtrim(l[ci]).trim()).append(',').append(MV_TOK[j]).append('\n');
    } else {
      hand += cl.size();
      if (cl.isEmpty()) log.append("  ").append(MV_COB[j]).append(": no line (an admin removed it) - so ").append(what).append(" stays at ").append(MV_IRON[j]).append("; add it to ").append(MV_COB[j]).append(" by hand and remove the ").append(MV_IRON[j]).append(" line if you like\n");
      for (int q = 0; q < cl.size(); q++) log.append("  kept hand-edited line ").append(((Integer) cl.get(q)).intValue() + 1).append(": ").append(l[((Integer) cl.get(q)).intValue()].trim()).append(" - so ").append(what).append(" stays at ").append(MV_IRON[j]).append("; add it to ").append(MV_COB[j]).append(" by hand and remove the ").append(MV_IRON[j]).append(" line if you like\n");
      continue;
    }
    mask = mask | (1 << j);
  }
  int cm = 0;
  for (int i = 0; i < n; i++) {
    if (rep[i] != null || del[i]) continue;
    String t = l[i].trim();
    if (!t.startsWith("#")) continue;
    for (int m = 0; m < CM_OLD.length; m++) {
      if (!t.equals(CM_OLD[m])) continue;
      String cr3 = raw[i].endsWith("\r") ? "\r" : "";
      if (CM_NEW[m].length() == 0) del[i] = true; else rep[i] = CM_NEW[m] + cr3;
      cm++;
      break;
    }
  }
  if (cm > 0) log.append("  ").append(cm).append(" comment line(s) that named Iron updated\n");
  java.util.ArrayList out = new java.util.ArrayList();
  int at = oldMark;
  if (at < 0) {
    at = -1;
    while (at + 1 < n && l[at + 1].trim().startsWith("#")) at++;
  }
  if (at < 0) out.add(MARK2 + (n > 1 ? (raw[0].endsWith("\r") ? "\r" : "") : cr));
  for (int i = 0; i < n; i++) {
    if (!del[i]) out.add(rep[i] != null ? rep[i] : raw[i]);
    if (i == at) out.add(MARK2 + (raw[i].endsWith("\r") ? "\r" : (i + 1 < n ? "" : cr)));
  }
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  String nt = sb.toString();
  java.util.HashMap want = table(l);
  for (int j = 0; j < MV_TOK.length; j++) {
    if ((mask & (1 << j)) == 0) continue;
    String ik = rkey(MV_IRON[j] + "=x");
    String ck = rkey(MV_COB[j] + "=x");
    java.util.ArrayList a = (java.util.ArrayList) want.get(ik);
    a.remove(MV_TOK[j]);
    if (a.isEmpty()) want.remove(ik);
    java.util.ArrayList c = (java.util.ArrayList) want.get(ck);
    if (c == null) { c = new java.util.ArrayList(); want.put(ck, c); }
    if (!c.contains(MV_TOK[j])) c.add(MV_TOK[j]);
  }
  String[] nl = nt.split("\n", -1);
  for (int i = 0; i < nl.length; i++) if (nl[i].endsWith("\r")) nl[i] = nl[i].substring(0, nl[i].length() - 1);
  boolean ok = table(nl).equals(want);
  return new Object[] { nt, (String[]) rows.toArray(new String[0]), log.toString(), Integer.valueOf(mask), Integer.valueOf(hand), Boolean.valueOf(ok) };
}""")
# the bags a profile keeps from the move (CollUnlocks.compute adds them): bit j of its _keptbag.Mining = KEEP_RID[j]
M(cobm, r"""
public static boolean isKept(@PKG@.CollData d, String rid) {
  if (d == null || rid == null) return false;
  long km = @PKG@.CollStore.meta(d, KEEP_META);
  for (int j = 0; j < KEEP_RID.length; j++) if (KEEP_RID[j].equals(rid) && (km & (1L << j)) != 0L) return true;
  return false;
}""")
# the bits a counts file (java.util.Properties) earns from the moved rarities `mask`: 0.2.7's CollUnlocks.compute rule for the Iron
# collection - the tier reached by count, or bought (_bought.Iron, clamped to the ladder) when the bag is within bagMax
M(cobm, r"""
public static long had(java.util.Properties p, @PKG@.RegData R, int c, int mask) {
  long s = @PKG@.CollStore.sumMap(p, (String[]) R.items[c]);
  int ct = @PKG@.CollReg.tierOf(R, c, s);
  long b = 0L;
  try { b = Long.parseLong(String.valueOf(p.getProperty("_bought." + R.id[c], "0")).trim()); } catch (Throwable t) { }
  int mx = @PKG@.CollReg.maxTier(R, c);
  if (b > (long) mx) b = (long) mx;
  long bits = 0L;
  for (int j = 0; j < KEEP_RID.length; j++) {
    if ((mask & (1 << j)) == 0) continue;
    int t = MV_TIER[j];
    if (t <= ct || ((long) t <= b && @PKG@.CollUtil.bagRank(KEEP_RID[j]) <= @PKG@.CollReg.BYP_BAGMAX)) bits = bits | (1L << j);
  }
  return bits;
}""")

'''
rep('''# ================= CollRewards: coins + skill XP per tier, owed-and-retry''', COB_JAVA + '''# ================= CollRewards: coins + skill XP per tier, owed-and-retry''')

# ---- CollUnlocks.compute: the kept bags (never take a recipe away)
rep('''    if (!@PKG@.CollReg.AUTO) return out;''', '''    long km = @PKG@.CollStore.meta(d, @PKG@.CollCobMig.KEEP_META);   // 0.2.8: Mining bags unlocked through Iron before the move
    if (km > 0L) {
      for (int j = 0; j < @PKG@.CollCobMig.KEEP_RID.length; j++) if ((km & (1L << j)) != 0L) out.add(@PKG@.CollCobMig.KEEP_RID[j]);
    }
    if (!@PKG@.CollReg.AUTO) return out;''')
# ---- the Unlocked recipes list names a kept bag
rep('''    if (seen.add(rid)) out.add(new Object[] { rid, @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rid), 44), "auto rule", null, Integer.valueOf(-1) });''',
    '''    if (seen.add(rid)) out.add(new Object[] { rid, @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rid), 44), @PKG@.CollCobMig.isKept(d, rid) ? "Iron Ore - kept (unlocked before 0.2.8)" : "auto rule", null, Integer.valueOf(-1) });''')

# ---- the start-up step (needs the registry, the config kit, CollBypassMig.mgKit / mgSaved): compiled right before the plugin
COB_RUN = r'''# 0.2.8: one pass over every counts file (each profile): OR the bits it earns into _keptbag.Mining (written with CollIO.write, the mod's
# own counts writer; setup() runs before any player is loaded). null = a file could not be read or written (the move then waits).
M(cobm, r"""
public static String keepAll(java.nio.file.Path base, int mask, StringBuilder log) {
  if (mask == 0) return "";
  @PKG@.RegData R = @PKG@.CollReg.D;
  if (R == null) return null;
  Object ci = R.byId.get("iron");
  if (!(ci instanceof Integer)) return "no Iron collection - no profile had these bags";
  int c = ((Integer) ci).intValue();
  if (R.hidden[c]) return "the Iron collection is hidden - no profile had these bags";
  java.nio.file.Path dir = base.resolve("counts");
  java.io.File[] fs = dir.toFile().listFiles();
  if (fs == null) return "no counts files";
  int kept = 0; int old = 0;
  for (int i = 0; i < fs.length; i++) {
    String fn = fs[i].getName();
    if (!fn.endsWith(".properties") || !fs[i].isFile()) continue;
    String key = fn.substring(0, fn.length() - 11);
    try {
      java.util.Properties p = @PKG@.CollIO.read(fs[i].toPath());
      if (!"2".equals(String.valueOf(p.getProperty("_schema", "")).trim())) { if (!p.isEmpty()) old++; continue; }
      long bits = had(p, R, c, mask);
      long have = 0L;
      try { have = Long.parseLong(String.valueOf(p.getProperty(KEEP_META, "0")).trim()); } catch (Throwable t) { }
      if ((have | bits) == have) continue;
      p.setProperty(KEEP_META, String.valueOf(have | bits));
      @PKG@.CollIO.write(dir, key, p);
      kept++;
      String nm = p.getProperty("_name");
      log.append("  ").append(key).append(nm != null ? " (" + nm + ")" : "").append(" keeps:");
      for (int j = 0; j < KEEP_RID.length; j++) if ((bits & (1L << j)) != 0L) log.append(' ').append(MV_RAR[j]);
      log.append(" Mining Bag (Iron Ore tier ").append(@PKG@.CollReg.tierOf(R, c, @PKG@.CollStore.sumMap(p, (String[]) R.items[c]))).append(", bought ").append(p.getProperty("_bought." + R.id[c], "0")).append(")\n");
    } catch (Throwable t) {
      @PKG@.CollUtil.warn("could not record the Mining bags of counts/" + fn + " kept from Iron: " + t);
      return null;
    }
  }
  return kept + " profile(s) keep Mining bags they unlocked through Iron" + (old > 0 ? " (" + old + " old 0.1 counts file(s) skipped - they never had them)" : "");
}""")
M(cobm, r"""
public static int fileIdx() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith("/rewards.properties")) return k;
  return -1;
}""")
M(cobm, r"""
public static String logLine(String e, String o, String nw) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine("rewards[" + e + "]") + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + @PKG@.CfgRows.oneLine(nw) + "\tok";
}""")
# setup(), right after CollReg.loadAll: "" = nothing done (no file - the loader writes the 0.2.8 default -, marker already there, or a
# failure: WARN, the file untouched, retried at the next start); else the INFO line
M(cobm, r"""
public static synchronized String run(java.nio.file.Path base) {
  if (base == null) return "";
  java.nio.file.Path f = base.resolve("rewards.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    if (!((Boolean) r[5]).booleanValue()) {
      @PKG@.CollUtil.warn("rewards.properties NOT updated for the 0.2.8 Mining bag move: the update would change more than the moved bag tokens (the file is used as it is; the next start tries again)");
      return "";
    }
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    int mask = ((Integer) r[3]).intValue();
    StringBuilder klog = new StringBuilder();
    String kp = keepAll(base, mask, klog);
    if (kp == null) {
      @PKG@.CollUtil.warn("rewards.properties NOT updated for the 0.2.8 Mining bag move: the profiles that keep their Iron Mining bags could not all be recorded (the next start tries again)");
      return "";
    }
    int fi = fileIdx();
    if (fi < 0) return "";
    @PKG@.CollBypassMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.2.8 Mining bag move (Iron -> Cobblestone)");
    if (!@PKG@.CollBypassMig.mgSaved(fi, old)) {
      @PKG@.CollUtil.warn("rewards.properties NOT updated for the 0.2.8 Mining bag move: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    int moved = Integer.bitCount(mask);
    int hand = ((Integer) r[4]).intValue();
    String msg = "Mining bags now unlock from Cobblestone (Skyy 2026-10-09): " + moved + " of 4 moved from Iron" + (hand > 0 ? ", " + hand + " hand-edited line(s) kept" : "") + "; " + kp + " (the old file is in config-history; Server Setup -> Changes can undo it; details in migration-bags.log)";
    @PKG@.CollIO.append(base.resolve("migration-bags.log"), "# " + new java.util.Date() + " - SkyyCollections 0.2.8: the Mining bag ladder moves from Iron to Cobblestone (" + moved + " of 4 moved, " + hand + " hand-edited line(s) kept)\n" + ((String) r[2]) + klog.toString());
    @PKG@.CollReg.loadRewards();
    @PKG@.CollUtil.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.CollUtil.warn("could not move the Mining bags to Cobblestone in rewards.properties (the file is used as it is; the next start tries again): " + t);
    return "";
  }
}""")

'''
rep('''# ================= plugin =================''', COB_RUN + '''# ================= plugin =================''')
rep('''  String s = @PKG@.CollReg.loadAll();''', '''  String s = @PKG@.CollReg.loadAll();
  String cb = @PKG@.CollCobMig.run(base);   // 0.2.8: Mining bags Iron -> Cobblestone (once; History first; Undo in Server Setup; kept bags)''')
rep('''(cm.length() > 0 ? "; " + cm.replace('\\n', ' ') : ""));''', '''(cm.length() > 0 ? "; " + cm.replace('\\n', ' ') : "") + (cb.length() > 0 ? "; " + cb : ""));''')

# ---- texts that named Iron as the Mining bag collection
_H_OLD = "Wheat.3 = recipe:<id>,coins:<n>,xp:<Skill>:<n>. Bags: Iron, OakLog, Wheat, Bone, HideLight 1/3/5/7."
_H_NEW = "Wheat.3=recipe:<id>,coins:<n>,xp:<Skill>:<n>. Bags 1/3/5/7: Cobblestone OakLog Wheat Bone HideLight"
assert len(_H_NEW) <= 100, len(_H_NEW)
rep_ok('     "%s",' % _H_OLD, '     "%s",' % _H_NEW)
rep_ok('''(entries like Iron.3).''', '''(entries like Cobblestone.3).''')
rep_ok('''(e.g. Iron.5=recipe:Skyy_Sack_Mining_Rare_Recipe_Generated_0)''', '''(e.g. Cobblestone.5=recipe:Skyy_Sack_Mining_Rare_Recipe_Generated_0)''')
rep_ok('''(Mining bags from Iron Ore)''', '''(Mining bags from Cobblestone)''')

# ---------------------------------------------------------------------------------------------------------------- docs inside the build
rep('''  Page (/collections, /coll, /coll <name>): one inline page, three views switched with rebuild() (HOME 2 x 2 category cards ->''',
    '''  0.2.8: a tier row with a recipe the player has unlocked ends in a CRAFT button -> /craft <the item's words> as the player.
  Page (/collections, /coll, /coll <name>): one inline page, three views switched with rebuild() (HOME 2 x 2 category cards ->''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("public static java.util.ArrayList words(String rid)") < s.index("public static String query(String[] rs, java.util.Set un)") \
    < s.index("public static @AC@ cmd()") < s.index("public static String open(@PR@ pr, String q)") \
    < s.index("public void buildDetail(") < s.index("public static void bindFree(") < s.index("public void craftClick(int t)") \
    < s.index("public void handleDataEvent(")
# bindFree must be compiled before buildDetail (javassist: a method before its callers)
assert s.index("public static void bindFree(") < s.index('for _name in ("catCard", "buildHome", "card", "buildCat", "buildDetail", "buildRecipes", "build"):')
assert len([l for l in s.split(LF) if "ccraft" in l]) == 4 and s.count("CollCraft") >= 6 and "kraft, ulc" in s
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyCollections 0.2.7 - build script (javassist via jpype). GENERATED by tools/coll_0_2_7_patch.py from the LIVE 0.2.6',
    "(build_skyycollections_0.2.6.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.6 was derived from 0.2.5 by",
    "tools/coll_0_2_6_patch.py; 0.2.5 from 0.2.4 by tools/coll_0_2_5_patch.py; 0.2.4 from 0.2.3 by tools/coll_0_2_4_patch.py; 0.2.3 from 0.2.2 by tools/coll_0_2_3_patch.py; 0.2.2 from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2",
    "Run:   python build_skyycollections_0.2.7.py          -> SkyyCollections/SkyyCollections-0.2.7.jar",
    'VERSION = "0.2.7"',
    '             (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"), (T["V3I"], "x"), (T["V3I"], "y"), (T["V3I"], "z")):',
    "       plsy, ksy, tcmp, top, fnc, page, ckit, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)",
    "def coll_det_tier(t=None, col=None, tc=None):",
    '             SUI.label("SkyyCRew" + t, "", "default", w=w[3], h=COLL_TR_H, col=tc, fit=False)]',
    '    "LOOK": coll_look_java(), "TIER": coll_java(coll_det_tier(), 4), "BUYROW": coll_java(coll_det_buyrow(), 4),',
    '            put(coll_det_tier(str(t), SUI.COLOR["success"], SUI.COLOR["rowName"]))',
    'COLL_PAGE_CHECKED = "be0dca34bcb2"',
    '    print("collections page %s = the page SkyyCollections/test_skyycollections_0.2.5.py last passed on" % COLL_PAGE_ID)',
    '    raise SystemExit("collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.5.py last passed on (%s) and "',
    '                     "in tools/coll_0_2_5_patch.py and regenerate" % (COLL_PAGE_ID, COLL_PAGE_CHECKED))',
    '    print("WARNING: collections page %s is NOT the page SkyyCollections/test_skyycollections_0.2.5.py last passed on (%s): the kit "',
    '          "output changed the page. Run the harness, then set PAGE_CHECKED in tools/coll_0_2_5_patch.py and regenerate; never deploy "',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED and ln not in GONE_OK and "0.2.7 ready (" not in ln]
assert not _bad, "0.2.7 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.2.7 had %d)" % (s.count(LF), OLD.count(LF)))
