"""Derive SkyyBazaar/build_skyybazaar_0.1.9.py from the LIVE 0.1.8 (build_skyybazaar_0.1.8.py = the tools/deploy_set.py SET pin; 0.1.8 and every
older script stay untouched).
Run:  python tools/bazaar_0_1_9_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.9.py   then   python SkyyBazaar/test_skyybazaar_0.1.9.py
(never --deploy: coordinated deploy with SkyySacks 0.8.0). Edit THIS patch, never the generated script.

0.1.9 (2026-10-13) = BAGS V2 (research/Bags-v2-Spec.md section 5; Skyy's LOCKED rule 2026-10-03 "if it goes in the bag, it goes in a matching
section in the bizzar."). Ships with SkyySacks 0.8.0 (SkyyVoid):
 A. A FISHING TAB: SkyySacks 0.8.0's catOf puts Fish_* and Food_Fish_Raw* in the new Fishing category, so the build's bag tabs are
    Mining / Foraging / Farming / Fishing / Combat / Smithing (BAG_TABS = SackDefs.CATS of the SkyySacks jar it reads; the page already
    fits 6 tabs: BZ_MAXT 6). The build reads max(the SET pin, 0.8.0) of SkyySacks (this Bazaar ships with 0.8.0).
    NO products.properties REWRITE for the fish: a product line whose category is exactly the item's OLD bag (Farming, the 0.1.8 default
    of a fish) no longer adds that category as an extra tab (Catalog.OLDBAG / tabsOf) - the fish leave Farming and show in Fishing, and a
    rollback to 0.1.8 reads the same file as before (fish back in Farming). An admin's own category (anything else) still adds its tab.
 B. CRYSTALS: SkyySacks 0.8.0 puts Ingredient_Crystal_* in Mining, so the build's TOTAL guard needs them: 9 new Mining products (the 8
    coloured Crystal Shards 25 coins, Void Crystal Shards 60 - DECISION, placeholders like every price; no recipe makes or uses them as a
    product, so the money-loop checks stay clean). They reach a LIVE products.properties through a ONE-TIME update (PROJECT-RULES 4,
    the 0.1.4 pattern): Catalog.migrate19 runs once (marker migrated.0.1.9 in pricing.properties, kept by writeModes): a verified byte copy
    of products.properties goes to config-history/ first, then each NEW product whose id is not in the file yet is APPENDED as its seed
    line (every existing byte and line ending kept; the file's own line ending style; a missing final newline added first); nothing else
    changes. One trades.log line per added product with its undo ("delete the line <id>=..." / put the history copy back) + a summary
    line; one INFO line. A failed step writes no marker and retries at the next start. A fresh install is seeded with every product.
 C. Player texts: "from your bags" -> "from the Void" (SkyyVoid is the players' name for the bags since 0.8.0); the locked-item refusal
    says "Void bags (the Pocket Dimension, old Magic Bags) can never be bought or sold" (fix round 2).
Rolling back to 0.1.8: safe - the appended crystal lines are ordinary product lines (0.1.8 shows them in their file category, Mining, and
trades them; crystals are not bag items for SkyySacks 0.7.18 - a rollback normally goes with SkyySacks 0.7.18 anyway).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.8.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.9.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.8"' in s and "Market.PEND" in s and "migrate19" not in s, "the source must be the generated 0.1.8 script"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:160])
    s = s.replace(old, new)


def T(x):
    return x.replace("QQQ", "'" * 3)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep(T(r'''"""SkyyBazaar 0.1.8 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.8.py            -> SkyyBazaar/SkyyBazaar-0.1.8.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.8 is GENERATED from build_skyybazaar_0.1.7.py by tools/bazaar_0_1_8_patch.py - edit the patch, not this file; 0.1.7 came
       from 0.1.6 by tools/bazaar_0_1_7_patch.py, 0.1.6 from 0.1.5, 0.1.5 from 0.1.4, 0.1.4 from 0.1.3, 0.1.3 from 0.1.2, 0.1.2 from
       0.1.1, 0.1.1 from 0.1; every older script is kept as it was)
'''), T(r'''"""SkyyBazaar 0.1.9 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.9.py            -> SkyyBazaar/SkyyBazaar-0.1.9.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.9 is GENERATED from build_skyybazaar_0.1.8.py by tools/bazaar_0_1_9_patch.py - edit the patch, not this file; 0.1.8 came
       from 0.1.7 by tools/bazaar_0_1_8_patch.py, 0.1.7 from 0.1.6, 0.1.6 from 0.1.5, 0.1.5 from 0.1.4, 0.1.4 from 0.1.3, 0.1.3 from
       0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)

''') + HEAD[HEAD.index("0.1.9 (2026-10-13)"):].strip() + '''
''')
rep('VERSION = "0.1.8"', 'VERSION = "0.1.9"')

# ---- A: the Fishing tab
rep(T(r'''BAG_TABS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")          # tab order = SkyySacks' bag order'''),
    T(r'''BAG_TABS = ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")   # tab order = SkyySacks 0.8.0's categories (0.1.9: + Fishing)
# 0.1.9: the bag of a product in 0.1.8 when it differs now (the fish were Farming): the file category that is exactly this OLD default adds no
# extra tab (Catalog.OLDBAG) - no products.properties rewrite; the 0.1.3 seed lines (SEED013, the one-time updates' "untouched default"
# test) keep their old category too
OLD_BAG_OF = {"Fishing": "Farming"}'''))
rep(T(r'''SACKS_VER = sacks_pin()'''), T(r'''# 0.1.9: the Fishing tab and the crystals come from SkyySacks 0.8.0's rule - read max(the SET pin, 0.8.0) (this Bazaar ships with 0.8.0)
SACKS_MIN = "0.8.0"
SACKS_VER = max(sacks_pin(), SACKS_MIN, key=lambda v: tuple(int(x) for x in v.split(".")))'''))
rep(T(r'''SEED013_LINES = ["%s=%s,%s,%s" % (pid, BAG_OF[pid], "%g" % (_auto013[pid] if base is AUTO else _fb013[pid]), name) for pid, base, name in PRODUCTS]'''),
    T(r'''SEED013_LINES = ["%s=%s,%s,%s" % (pid, OLD_BAG_OF.get(BAG_OF[pid], BAG_OF[pid]), "%g" % (_auto013[pid] if base is AUTO else _fb013[pid]), name) for pid, base, name in PRODUCTS]   # 0.1.9: the 0.1.3 category
# 0.1.9: ids whose bag moved (fish: Farming -> Fishing) -> their old bag; the NEW products of 0.1.9 (appended once by Catalog.migrate19)
OLDBAG_ID = [pid for pid, _b, _n in PRODUCTS if BAG_OF[pid] in OLD_BAG_OF]
OLDBAG_TAB = [OLD_BAG_OF[BAG_OF[pid]] for pid in OLDBAG_ID]
NEW019 = ["Ingredient_Crystal_Blue", "Ingredient_Crystal_Cyan", "Ingredient_Crystal_Green", "Ingredient_Crystal_Pink", "Ingredient_Crystal_Purple",
          "Ingredient_Crystal_Red", "Ingredient_Crystal_White", "Ingredient_Crystal_Yellow", "Ingredient_Crystal_Void"]
assert all(i in BAG_OF and BAG_OF[i] == "Mining" for i in NEW019), "0.1.9: the crystals must be Mining bag products"
assert OLDBAG_ID and all(BAG_OF[i] == "Fishing" for i in OLDBAG_ID)
print("0.1.9: %d fish products moved Farming -> Fishing (no file rewrite: OLDBAG), %d new Mining products appended once (migrate19): %s"
      % (len(OLDBAG_ID), len(NEW019), ", ".join(NEW019)))'''))
# ---- B: the crystal products (Mining)
rep(T(r'''    ("Rock_Gem_Voidstone", 120, "Voidstone"),
'''), T(r'''    ("Rock_Gem_Voidstone", 120, "Voidstone"),
    # 0.1.9 (SkyySacks 0.8.0 puts the crystal shards in Mining): crystal rocks and golems drop them; no recipe makes one (DECISION prices)
    ("Ingredient_Crystal_Blue", 25, "Blue Crystal Shards"),
    ("Ingredient_Crystal_Cyan", 25, "Cyan Crystal Shards"),
    ("Ingredient_Crystal_Green", 25, "Green Crystal Shards"),
    ("Ingredient_Crystal_Pink", 25, "Pink Crystal Shards"),
    ("Ingredient_Crystal_Purple", 25, "Purple Crystal Shards"),
    ("Ingredient_Crystal_Red", 25, "Red Crystal Shards"),
    ("Ingredient_Crystal_White", 25, "White Crystal Shards"),
    ("Ingredient_Crystal_Yellow", 25, "Yellow Crystal Shards"),
    ("Ingredient_Crystal_Void", 60, "Void Crystal Shards"),
'''))
rep(T(r'''    "# Every Magic Bag material shows in its bag's tab (Mining, Foraging, Farming, Combat, Smithing - building shapes and decoration\n"'''),
    T(r'''    "# Every Void material shows in its category's tab (Mining, Foraging, Farming, Fishing, Combat, Smithing - building shapes and decoration\n"'''))
# ---- the Catalog: OLDBAG (no extra tab for an old default category) + the 0.1.9 one-time append
rep(T(r'''cat_.addField(CtField.make('public static volatile String MIGRATED14 = "";', cat_))'''),
    T(r'''cat_.addField(CtField.make('public static volatile String MIGRATED14 = "";', cat_))
# 0.1.9: OLDBAG = id -> its 0.1.8 bag where it moved (fish: Farming); NEW019 = the products 0.1.9 appends once; MIGRATED19 = its marker
cat_.addField(CtField.make("public static final String[] OLDBAG_ID = %s;" % jarr(OLDBAG_ID), cat_))
cat_.addField(CtField.make("public static final String[] OLDBAG_TAB = %s;" % jarr(OLDBAG_TAB), cat_))
cat_.addField(CtField.make("public static final java.util.HashMap OLDBAG = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final String[] NEW019 = %s;" % jarr(NEW019), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED19 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M19_LOG = new java.util.ArrayList();", cat_))'''))
rep(T(r'''    ORDER_IX.put(id, Integer.valueOf(i));'''), T(r'''    ORDER_IX.put(id, Integer.valueOf(i));
    if (i == 0) { for (int o = 0; o < OLDBAG_ID.length; o++) OLDBAG.put(OLDBAG_ID[o], OLDBAG_TAB[o]); }   // 0.1.9'''))
rep(T(r'''  if (p.cat != null && p.cat.length() > 0 && !raw.contains(p.cat)) raw.add(p.cat);'''),
    T(r'''  // 0.1.9: a file category that is exactly the item's OLD bag (a fish line still saying Farming) adds no tab - the fish show in Fishing only
  if (p.cat != null && p.cat.length() > 0 && !raw.contains(p.cat) && !p.cat.equals(OLDBAG.get(p.id))) raw.add(p.cat);'''))
rep(T(r'''  if (MIGRATED14 != null && MIGRATED14.length() > 0) {
    sb.append("# the one-time 0.1.4 progression price update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.4=").append(MIGRATED14).append('\n');
  }'''), T(r'''  if (MIGRATED14 != null && MIGRATED14.length() > 0) {
    sb.append("# the one-time 0.1.4 progression price update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.4=").append(MIGRATED14).append('\n');
  }
  if (MIGRATED19 != null && MIGRATED19.length() > 0) {
    sb.append("# the one-time 0.1.9 new-products update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.9=").append(MIGRATED19).append('\n');
  }'''))
rep(T(r'''  String mg14 = pp.getProperty("migrated.0.1.4");
  if (mg14 != null && mg14.trim().length() > 0) MIGRATED14 = mg14.trim();'''), T(r'''  String mg14 = pp.getProperty("migrated.0.1.4");
  if (mg14 != null && mg14.trim().length() > 0) MIGRATED14 = mg14.trim();
  String mg19 = pp.getProperty("migrated.0.1.9");
  if (mg19 != null && mg19.trim().length() > 0) MIGRATED19 = mg19.trim();'''))
rep(T(r'''# the raw-input value of a processed good: inputs (qty x the cheapest listed product of each input) + fuel (seconds x the cheapest'''),
    T(r'''# ---- 0.1.9: THE ONE-TIME NEW-PRODUCTS UPDATE (PROJECT-RULES one-time migrations; the migrate14 pattern). Runs after migrate14 while
# pricing.properties has migrated.0.1.4 and no migrated.0.1.9. Each NEW019 product whose id is in no line load() would read gets its seed
# line APPENDED (nothing else changes: every existing byte and line ending stays; the file's own newline style; a missing final newline is
# added first). Before products.properties is written its bytes go to config-history/ (read back + compared - a mismatch throws, nothing
# changes). products.properties first, the marker last (appended to pricing.properties, its bytes kept): a failed step changes nothing it
# cannot redo. The trades.log lines wait in M19_LOG (setup writes them after Market.load).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate19() {
  init();
  M19_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.9");
    if (done != null && done.trim().length() > 0) { MIGRATED19 = done.trim(); return null; }
    int added = 0;
    int already = 0;
    java.util.ArrayList lines = new java.util.ArrayList();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      java.util.HashSet have = new java.util.HashSet();
      String[] ls = txt.split("\n", -1);
      for (int i = 0; i < ls.length; i++) {
        @PKG@.Product p = peek(ls[i].endsWith("\r") ? ls[i].substring(0, ls[i].length() - 1) : ls[i]);
        if (p != null) have.add(p.id);
      }
      StringBuilder sb = new StringBuilder(txt);
      boolean nlDone = txt.length() == 0 || txt.endsWith("\n");
      for (int i = 0; i < NEW019.length; i++) {
        if (have.contains(NEW019[i])) { already++; continue; }
        String sl = seedLine(NEW019[i]);
        if (sl == null) continue;
        if (!nlDone) { sb.append(nl); nlDone = true; }
        sb.append(sl).append(nl);
        added++;
        lines.add("MIGRATE-0.1.9 ADDED " + sl + " (undo: delete that line from products.properties, then /bazaaradmin reload)");
      }
      if (added > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.9 new-products update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.9=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED19 = stamp;
    String head = "MIGRATE-0.1.9 added " + added + " already " + already + (backup.length() > 0 ? " backup " + backup : "") + " (undo all: put the backup back as products.properties)";
    M19_LOG.add(head);
    M19_LOG.addAll(lines);
    @PKG@.BzUtil.info("one-time 0.1.9 update (SkyyVoid puts crystal shards in Mining): " + added + " new Mining product(s) added" + (already > 0 ? ", " + already + " were already listed" : "") + (backup.length() > 0 ? "; the old file is " + backup + ", every line + its undo is in trades.log" : ""));
    return head;
  } catch (Throwable t) {
    M19_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.9 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# the raw-input value of a processed good: inputs (qty x the cheapest listed product of each input) + fuel (seconds x the cheapest'''))
rep(T(r'''  String mig14 = @PKG@.Catalog.migrate14();
'''), T(r'''  String mig14 = @PKG@.Catalog.migrate14();
  String mig19 = @PKG@.Catalog.migrate19();   // 0.1.9: the crystal shards appended once
'''))
rep(T(r'''  @PKG@.Catalog.M14_LOG.clear();
'''), T(r'''  @PKG@.Catalog.M14_LOG.clear();
  if (mig19 != null) { for (int i = 0; i < @PKG@.Catalog.M19_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M19_LOG.get(i)); }
  @PKG@.Catalog.M19_LOG.clear();
'''))
# ---- C: player texts
rep(T(r'''" (" + bagTaken + " from your bags)"'''), T(r'''" (" + bagTaken + " from the Void)"'''))
rep(T(r'''"nothing to sell - no bazaar items in your inventory or bags"'''), T(r'''"nothing to sell - no bazaar items in your inventory or the Void"'''), count=2)
rep(T(r'''" in your bags)"'''), T(r'''" in the Void)"'''))
rep(T(r'''" from your bags)"'''), T(r'''" from the Void)"'''), count=2)
rep(T(r'''"SkyWynn bazaar: /bazaar instant buy and sell of the Magic Bag materials (Mining, Foraging, Farming, Combat, Smithing tabs) against a demand-driven market maker; processed goods cost a premium over their raw inputs. Uses the SkyyCoins bridge, zero dependencies."'''),
    T(r'''"SkyWynn bazaar: /bazaar instant buy and sell of the Void materials (Mining, Foraging, Farming, Fishing, Combat, Smithing tabs) against a demand-driven market maker; processed goods cost a premium over their raw inputs. Uses the SkyyCoins bridge, zero dependencies."'''))

# fix round 2: the locked-item refusal names what a player can still hold (the Pocket Dimension + old bags; Skyy_Sack_*), same red colour
rep(T(r'''"Magic Bags can never be bought or sold"'''), T(r'''"Void bags (the Pocket Dimension, old Magic Bags) can never be bought or sold"'''), count=2)
rep(T(r'''("startsWith", "Magic Bags", "-"),'''), T(r'''("startsWith", "Void bags", "-"),'''))

out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote %s (%d lines)" % (dst, s.count(LF) + 1))
