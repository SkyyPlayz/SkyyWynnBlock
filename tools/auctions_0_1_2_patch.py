"""Derive SkyyAuctions/build_skyyauctions_0.1.2.py from the LIVE 0.1.1 script (python tools/auctions_0_1_2_patch.py, then build the result:
python SkyyAuctions/build_skyyauctions_0.1.2.py). Edit THIS patch, never the generated script.

0.1.2 (2026-09-28) = research/SkyyGear-Stage1-Spec.md 7.3.1 (SkyyGear compat) + Skyy's LOCKED Auction House answers (OPEN-QUESTIONS.md
"Auction House" 2, 4 and 15; HANDOFF log 2026-09-25):

A. Gear text and rarity through the SkyyGear bridge (spec 7.1 keys gear:fn:describe / rollsLine / rarity / level / identified / sig and the
   plain value gear:tiers; every call passes Object[]{itemId, a CLONE of the listed metadata}, so a listing record is never handed out).
   - Row / item page / Manage / Create names = gear:fn:describe line 0 ("Unidentified Iron Sword", "Sharp Iron Sword") in the rarity colour
     (Mythic uses the readable page variant #CC66CC, spec 5.8; tooltips are SkyyGear's own). Row sub-line = "x1 - " + gear:fn:rollsLine
     ("Rare - Lv 20 - Strength +12 - Crit Chance +5%", unidentified: "Unidentified (Rare, Lv 20)"; a Normal without modifiers: "Normal -
     Lv 5"). The item page's text lines = gear:fn:describe (owner-neutral, spec 6.3), its first fact "Gear: <rollsLine>".
   - "A cheaper one is listed" caveat: with SkyyGear "- rolls differ" only when the cheapest same-id listing's gear:fn:sig differs from this
     one's (nothing when equal); without SkyyGear the old "- rolls are not compared" for SkyyRolls items.
   - Rarity filter: the Wynn ladder from gear:tiers (Normal, Unique, Rare, Legendary, Fabled, Mythic, Set) followed by the vanilla tiers
     whose names are not on it (Common, Uncommon, Epic), so vanilla items stay filterable. A listing's tier = gear:fn:rarity for gear,
     else its engine quality ("as today"); matching is by tier name. The quality scan (QualityValue 1-5) SKIPS every quality id that starts
     with Skyy_ (SkyyGear's Skyy_Gear_* and SkyySacks' Skyy_Bag_*), so they never double the vanilla tiers; a Skyy_ quality name is shown
     as its last word ("Skyy_Bag_Rare" -> "Rare"). The tier of a listing is cached per id + rev + gear:tiers + config:epoch:SkyyGear.
   - WITHOUT SkyyGear (no gear:fn:describe in the bridge) everything falls back to 0.1.1: SkyyRolls reforge + roll line, vanilla tiers.
   - Unidentified gear is listable and sellable (spec Q6 default "yes", 5.6) - nothing refuses it; new listings of gear get the rarity
     name (+ "unidentified") in their search text, so /ah search rare or unidentified finds them.
B. 48h pays DOUBLE the listing fee (Skyy) - a premium long listing, never a discount. A duration preset's fee may be written xN: the
   listing fee is multiplied by N and no flat fee is added, BUT (xFloorPrev=true, default) the total is never less than the total of the
   preset right before it in the list, so 48h always costs at least what 24h costs (price 1,000: 24h 360, 48h 360 - not 20). New default
   durations=1h:20,6h:45,12h:100,24h:350,48h:x2. The record keeps fee.listing = the tier fee, fee.duration = total - tier fee (so
   fee.listing + fee.duration is exactly what was paid; cancel / admin-refund sums stay right) and fee.mult = N. The Create page line says
   "48h: double listing fee (1% = 10, x2 = 20), at least the 24h price -> you pay 360 coins now ..." (AhCfg.feeLine); /ahadmin info says
   "raised to the price of the preset before it" when the floor was used (derived: listing x mult < listing + duration); /ahadmin status lists
   xFloorPrev. xFloorPrev=false = exactly N x the listing fee.
   AhCfg.migrate() at start (reads and writes ISO-8859-1 = byte-preserving, what Properties.load reads): a config.properties whose
   durations line is EXACTLY the 0.1.1 stock default 1h:20,6h:45,12h:100,24h:350,48h:1200 gets that line rewritten to the new default
   (plus the stock comment line right above it, which would otherwise say the fee is added); a line that is neither the old nor the new
   stock line is kept and logged ("custom durations kept"). Atomic write, line endings kept, one INFO line.
C. A DIFFERENT profile of the same account may buy your listing; the SAME profile may not (Skyy). New key otherProfileBuy=true;
   false restores 0.1.1's account-wide refusal. The own-listing check by profile key stays ("That is your own listing."). sameAccountBuy
   is retired: it is only read to log once that it is ignored and replaced (its old default false would contradict Skyy's lock, its old
   non-default true equals the new default), its status line and "solo testing only" warnings are gone. The item page no longer shows
   "you cannot buy from yourself" to another profile; with otherProfileBuy=false it says buying from your own account is off.
D. Magic Bags (every Skyy_Sack_* incl. SkyySacks 0.7.7's Skyy_Sack_<Type>_Rare and Skyy_Sack_Omni) and Skyy_Accessory_Bag are blocked
   BUILT IN (config blockBags=true, default): AhItem.blockedReason answers for them first, so listing (tradeable) AND buying (buy0) are
   refused, lowestBin ignores them, rows say OFF THE MARKET; a bag listed before 0.1.2 cannot be bought - its seller cancels or lets it
   expire and claims it back. They are also published to the shared market:blocked map with owner "builtin" (never written into
   blocked.txt; removed on shutdown and when blockBags=false). The "Contents not included" notes stay for blockBags=false.
   migrate() also appends the three new keys (otherProfileBuy, blockBags, xFloorPrev) with their comments when the file lacks them (new
   files get them from the template; the "added by" head line is written only once); the old sameAccountBuy line is left where it is
   (ignored) and its old "# sameAccountBuy ..." comment line gets " (retired, ignored)" appended once.
E. Review fixes (2026-09-29): Browse row sub-lines are capped at 52 characters ending in ".." (AhItem.clip; " - OFF THE MARKET" always
   stays whole), the Create page's picked-item line at 96 + the slot text, the item page's "Gear: ..." fact at 96 (all measured with the
   game's NunitoSans metrics: 380 px @ 13 px, 980 px @ 14 px, 840 px @ 16 px); the item page's gear text box (266 px @ 15 px, line height
   1.364 em = 13 lines) shows at most 12 lines, the 12th being "..." when there are more (AhItem.descText, ~90 characters per wrapped
   line). New listings compute the gear name + search words BEFORE the fee is taken and the item removed (list0 -> newRecord args). A
   picked bag on the Create page shows its off-the-market reason while blockBags=true; the pick message uses the gear name. migrate()'s
   failure text says the old file is used as it is. setPaused() (pre-existing) reads / writes ISO-8859-1 too (same byte-preserving swap).
   Rollback to 0.1.1 needs no code: restore durations ...,48h:1200 by hand (0.1.1 cannot read 48h:x2 - it drops that preset with a
   warning), the sameAccountBuy line is still in the file (0.1.1 reads it again), bags become listable / buyable again under 0.1.1.
Kept: the metadata-free ItemGridSlot fix of 0.1.1 and everything else. No config kit here (the AH still reads its own config.properties;
the Server Setup rows come with SkyyEconomy), so the kit's KEEP=10 does not apply.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.1.py")
dst = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.2.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


def rep_method(cls, head, new_src):
    """Replace one whole M(cls, r'''...''') block whose Java starts with `head` by new_src (Java text from 'public ...' to the last '}')."""
    global s
    start_mark = 'M(%s, r"""\n%s' % (cls, head)
    assert s.count(start_mark) == 1, "method anchor count %d: %s" % (s.count(start_mark), head)
    a = s.index(start_mark)
    b = s.index('\n}""")', a) + len('\n}""")')
    s = s[:a] + 'M(%s, r"""\n%s\n}""")' % (cls, new_src.strip("\n").rstrip("}").rstrip()) + s[b:]


rep('VERSION = "0.1.1"', 'VERSION = "0.1.2"')
first = s.index('"""') + 3
s = s[:first] + ("0.1.2 (2026-09-28): SkyyGear compat (names, rarity filter on the Wynn ladder, modifier lines via the gear:fn bridge, SkyyRolls\n"
                 "  fallback) + Skyy's AH locks (48h = double listing fee but never less than 24h - xFloorPrev, another profile of the same\n"
                 "  account may buy, Magic Bags + Accessory Bag blocked built in); 2026-09-29 review fixes (capped row sub-lines, config\n"
                 "  migration fixes). Notes in tools/auctions_0_1_2_patch.py.\n") + s[first:]

# ======================================================================= config template (B, C, D)
# the 0.1.1 stock durations comment + line: used as the rep() anchor below (so they are proven byte-identical to what 0.1.1 wrote) AND
# emitted as the constants AhCfg.migrate() compares against
OLD_NOTE_TXT = "# durations = up to 8 presets length:fee (m, h or d; a bare number means hours; 14 days at most). The fee is added to the listing fee."
OLD_DURS_TXT = "1h:20,6h:45,12h:100,24h:350,48h:1200"
TEMPLATE_HEAD = '''# 0.1.2 (tools/auctions_0_1_2_patch.py): the 0.1.1 stock lines AhCfg.migrate() recognises, and the new keys' comments
OLD_DURS = "@OLDDURS@"   # the 0.1.1 stock line - rewritten ONCE to NEW_DURS; a hand-edited line is kept
NEW_DURS = "1h:20,6h:45,12h:100,24h:350,48h:x2"     # Skyy 2026-09-25: a 48h listing pays double the listing fee
OLD_DUR_NOTE = "@OLDNOTE@"
NEW_DUR_NOTE = ("# durations = up to 8 presets length:fee (m, h or d; a bare number means hours; 14 days at most). A number is added to the "
                "listing fee; xN multiplies the listing fee instead (48h:x2 = double).")
OTHER_NOTE = ("# otherProfileBuy = true: ANOTHER profile of the same account may buy a listing (the same profile never can). "
              "false = no buying from your own account at all.")
BAGS_NOTE = ("# blockBags = true: Magic Bags (Skyy_Sack_*) and the Accessory Bag cannot be listed or bought - they open their owner's own "
             "storage. false = tradeable (the contents are never included).")
XFLOOR_NOTE = "# xFloorPrev = true: an xN preset never costs less than the preset before it; false = exactly N x the listing fee"
ADDED_HEAD = "# ---- added by SkyyAuctions 0.1.2 ----"
SAB_MARK = " (retired, ignored)"     # appended once to the old "# sameAccountBuy ..." comment line by migrate()
CFG_LINES = [
    "# SkyyAuctions config'''.replace("@OLDDURS@", OLD_DURS_TXT).replace("@OLDNOTE@", OLD_NOTE_TXT)
rep('''CFG_LINES = [
    "# SkyyAuctions config''', TEMPLATE_HEAD)
rep('''    "%s",
    "durations=%s",''' % (OLD_NOTE_TXT, OLD_DURS_TXT), '''    NEW_DUR_NOTE,
    "durations=" + NEW_DURS,
    XFLOOR_NOTE,
    "xFloorPrev=true",''')
rep('''    "# sameAccountBuy = true lets another profile of the SAME account buy a listing. SOLO TESTING ONLY: it moves coins between profiles.",
    "sameAccountBuy=false",''', '''    OTHER_NOTE,
    "otherProfileBuy=true",''')
rep('''    "bazaarItemsAllowed=false",''', '''    "bazaarItemsAllowed=false",
    BAGS_NOTE,
    "blockBags=true",''')
rep('''    "#   Skyy_Sack_* = a bag only opens its owner's own storage",
    "#   Skyy_Accessory_Bag = a bag only opens its owner's own storage",''',
    '''    "#   (Magic Bags Skyy_Sack_* and the Accessory Bag are blocked built in - blockBags in Skyy_SkyyAuctions/config.properties)",''')
rep('''for _l in CFG_LINES + BLOCK_LINES:
    assert '"' not in _l and "\\\\" not in _l, _l''', '''for _l in CFG_LINES + BLOCK_LINES + [OLD_DUR_NOTE, ADDED_HEAD, SAB_MARK]:
    assert '"' not in _l and "\\\\" not in _l, _l
    assert all(32 <= ord(_c) < 127 for _c in _l), "config text must be plain ASCII (migrate() writes ISO-8859-1): " + _l''')

# ======================================================================= AhCfg fields + constants
rep('''F(cfg, "public static final String BLOCK_TEMPLATE = %s;" % jstr("\\n".join(BLOCK_LINES) + "\\n"))''',
    '''F(cfg, "public static final String BLOCK_TEMPLATE = %s;" % jstr("\\n".join(BLOCK_LINES) + "\\n"))
F(cfg, "public static final String OLD_DURS = %s;" % jstr(OLD_DURS))
F(cfg, "public static final String NEW_DURS = %s;" % jstr(NEW_DURS))
F(cfg, "public static final String OLD_DUR_NOTE = %s;" % jstr(OLD_DUR_NOTE))
F(cfg, "public static final String NEW_DUR_NOTE = %s;" % jstr(NEW_DUR_NOTE))
F(cfg, "public static final String OTHER_NOTE = %s;" % jstr(OTHER_NOTE))
F(cfg, "public static final String BAGS_NOTE = %s;" % jstr(BAGS_NOTE))
F(cfg, "public static final String ADDED_HEAD = %s;" % jstr(ADDED_HEAD))
F(cfg, "public static final String XFLOOR_NOTE = %s;" % jstr(XFLOOR_NOTE))
F(cfg, "public static final String SAB_MARK = %s;" % jstr(SAB_MARK))
F(cfg, "public static final String BAG_REASON = %s;" % jstr("Magic Bags and the Accessory Bag open their owner's own storage - they cannot be sold"))''')
rep('''F(cfg, "public static volatile long[] DUR_FEE = new long[] { 20L, 45L, 100L, 350L, 1200L };")''',
    '''F(cfg, "public static volatile long[] DUR_FEE = new long[] { 20L, 45L, 100L, 350L, 0L };")
F(cfg, "public static volatile int[] DUR_MUL = new int[] { 0, 0, 0, 0, 2 };")     # 0.1.2: xN = N x the listing fee, no flat fee
F(cfg, "public static volatile boolean X_FLOOR = true;")     # 0.1.2 xFloorPrev: an xN total is never below the preset before it''')
rep('''F(cfg, "public static volatile boolean SAME_ACCOUNT = false;")''',
    '''F(cfg, "public static volatile boolean OTHER_PROFILE = true;")      # 0.1.2 otherProfileBuy (replaces sameAccountBuy)
F(cfg, "public static volatile boolean BLOCK_BAGS = true;")         # 0.1.2 blockBags
F(cfg, "public static volatile boolean WARNED_SAB = false;")''')

# ---- parseDurs: xN presets
rep('''  java.util.ArrayList fee = new java.util.ArrayList();
  StringBuilder test = new StringBuilder();''', '''  java.util.ArrayList fee = new java.util.ArrayList();
  java.util.ArrayList mu = new java.util.ArrayList();
  StringBuilder test = new StringBuilder();''')
rep('''    long f = -1L;
    try { f = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable t) { f = -1L; }
    if (m <= 0L || f < 0L) { @PKG@.AhUtil.warn("config durations: bad entry " + x + " (use length:fee, like 24h:350)"); continue; }''',
    '''    long f = -1L;
    int mul = 0;
    String fs = x.substring(c + 1).trim().toLowerCase();
    if (fs.startsWith("x")) {
      try { mul = Integer.parseInt(fs.substring(1).trim()); } catch (Throwable t) { mul = -1; }
      if (mul < 1 || mul > 100) { @PKG@.AhUtil.warn("config durations: bad entry " + x + " (xN needs a whole number 1 to 100, like 48h:x2)"); continue; }
      f = 0L;
    } else {
      try { f = Long.parseLong(fs); } catch (Throwable t) { f = -1L; }
    }
    if (m <= 0L || f < 0L) { @PKG@.AhUtil.warn("config durations: bad entry " + x + " (use length:fee or length:xN, like 24h:350 or 48h:x2)"); continue; }''')
rep('''    if (f < MIN_DUR_FEE) {''', '''    if (mul == 0 && f < MIN_DUR_FEE) {''')
rep('''    lab.add(l);
    ms.add(Long.valueOf(m));
    fee.add(Long.valueOf(f));''', '''    lab.add(l);
    ms.add(Long.valueOf(m));
    fee.add(Long.valueOf(f));
    mu.add(Integer.valueOf(mul));''')
rep('''  long[] d = new long[lab.size()];
  for (int i = 0; i < a.length; i++) { a[i] = (String) lab.get(i); b[i] = ((Long) ms.get(i)).longValue(); d[i] = ((Long) fee.get(i)).longValue(); }
  DUR_LABEL = a;
  DUR_MS = b;
  DUR_FEE = d;''', '''  long[] d = new long[lab.size()];
  int[] e = new int[lab.size()];
  for (int i = 0; i < a.length; i++) { a[i] = (String) lab.get(i); b[i] = ((Long) ms.get(i)).longValue(); d[i] = ((Long) fee.get(i)).longValue(); e[i] = ((Integer) mu.get(i)).intValue(); }
  DUR_LABEL = a;
  DUR_MS = b;
  DUR_MUL = e;
  DUR_FEE = d;''')

# ---- load(): new default durations, otherProfileBuy, blockBags, sameAccountBuy retired
rep('''  if (!parseDurs(p.getProperty("durations", "1h:20,6h:45,12h:100,24h:350,48h:1200"))) {
    @PKG@.AhUtil.warn("config durations has no usable preset - using 1h:20,6h:45,12h:100,24h:350,48h:1200");
    parseDurs("1h:20,6h:45,12h:100,24h:350,48h:1200");
  }''', '''  if (!parseDurs(p.getProperty("durations", NEW_DURS))) {
    @PKG@.AhUtil.warn("config durations has no usable preset - using " + NEW_DURS);
    parseDurs(NEW_DURS);
  }
  X_FLOOR = boolP(p, "xFloorPrev", true);''')
rep('''  SAME_ACCOUNT = boolP(p, "sameAccountBuy", false);''', '''  OTHER_PROFILE = boolP(p, "otherProfileBuy", true);
  BLOCK_BAGS = boolP(p, "blockBags", true);
  String sab = p.getProperty("sameAccountBuy");
  if (sab != null && !WARNED_SAB) {
    WARNED_SAB = true;
    @PKG@.AhUtil.info("config sameAccountBuy=" + sab.trim() + " is retired and ignored - replaced by otherProfileBuy (now " + OTHER_PROFILE + "): another profile of the same account " + (OTHER_PROFILE ? "may" : "may not") + " buy a listing, the same profile never can");
  }''')
rep('''  if (SAME_ACCOUNT) @PKG@.AhUtil.warn("sameAccountBuy=true - profiles of one account can buy each other's listings (solo testing only)");\n''', '')

# ---- fee math helpers (after listingFee)
rep('''# tax fixed at sale time: only above TAX_FROM, never taking the net below TAX_FROM''', '''# 0.1.2 fee of a listing: { tier listing fee, duration part, N, raised }. A flat preset adds its fee (N = 0); an xN preset (48h:x2) charges
# N x the tier fee - with xFloorPrev (review 2026-09-29) never less than the total of the preset right before it in the list (raised = 1
# when that floor was used), so 48h is a premium, never a discount. The duration part is total - tier fee, so fee.listing + fee.duration
# is always exactly the total that was paid. Pure (bare-JVM tested).
M(cfg, r"""
public static long[] fees(long price, int i) {
  long l = listingFee(price);
  long[] df = DUR_FEE;
  int[] mu = DUR_MUL;
  boolean fl = X_FLOOR;
  if (i < 0 || i >= df.length) return new long[] { l, 0L, 0L, 0L };
  long prev = -1L;
  long tot = 0L;
  long raised = 0L;
  for (int j = 0; j <= i; j++) {
    int m = j < mu.length ? mu[j] : 0;
    raised = 0L;
    if (m > 0) {
      tot = l * (long) m;
      if (fl && prev >= 0L && tot < prev) { tot = prev; raised = 1L; }
    } else tot = l + df[j];
    prev = tot;
  }
  int mi = i < mu.length ? mu[i] : 0;
  return new long[] { l, tot - l, mi > 0 ? (long) mi : 0L, raised };
}""")
M(cfg, r"""
public static String mulWord(long m) {
  if (m == 2L) return "double";
  if (m == 3L) return "triple";
  return m + "x";
}""")
M(cfg, r"""
public static String durTok(int i) {
  String[] l = DUR_LABEL;
  long[] f = DUR_FEE;
  int[] m = DUR_MUL;
  if (i < 0 || i >= l.length) return "?";
  if (i < m.length && m[i] > 0) return l[i] + ":x" + m[i];
  return l[i] + ":" + (i < f.length ? f[i] : 0L);
}""")
# tax fixed at sale time: only above TAX_FROM, never taking the net below TAX_FROM''')

# ---- summary
rep('''  for (int i = 0; i < DUR_LABEL.length; i++) { if (i > 0) sb.append(','); sb.append(DUR_LABEL[i]).append(':').append(DUR_FEE[i]); }''',
    '''  for (int i = 0; i < DUR_LABEL.length; i++) { if (i > 0) sb.append(','); sb.append(durTok(i)); }''')
rep('''  sb.append(" | sameAccountBuy ").append(SAME_ACCOUNT).append(" | blockCreative ").append(BLOCK_CREATIVE)''',
    '''  sb.append(" | xFloorPrev ").append(X_FLOOR).append(" | otherProfileBuy ").append(OTHER_PROFILE).append(" | blockBags ").append(BLOCK_BAGS).append(" | blockCreative ").append(BLOCK_CREATIVE)''')

# ---- 0.1.2 review: the Create page fee line (pure, bare-JVM tested); after pctText, before its caller renderCreate
rep('''# /ahadmin pause | resume: rewrite only the paused= line of config.properties''', '''# 0.1.2 the Create page fee line: a flat preset as in 0.1.1; an xN preset names the multiplier, the tier fee and - with xFloorPrev and a
# preset before it - "at least the <previous> price", so a raised total (48h at a low price) explains itself
M(cfg, r"""
public static String feeLine(long pp, int i) {
  long[] fz = fees(pp, i);
  String[] dl = DUR_LABEL;
  String lab = i >= 0 && i < dl.length ? dl[i] : "?";
  String pc = pctText(pctFor(pp));
  String rfd = " coins now (" + (CANCEL_REFUND ? "refunded" : "not refunded") + " if you cancel).";
  long tot = fz[0] + fz[1];
  if (fz[2] > 0L) {
    String why = lab + ": " + mulWord(fz[2]) + " listing fee (" + pc + "% = " + @PKG@.AhUtil.fmt(fz[0]) + (fz[3] > 0L ? ", x" + fz[2] + " = " + @PKG@.AhUtil.fmt(fz[0] * fz[2]) : " x" + fz[2]) + ")";
    if (X_FLOOR && i > 0 && i - 1 < dl.length) why = why + ", at least the " + dl[i - 1] + " price";
    return why + " -> you pay " + @PKG@.AhUtil.fmt(tot) + rfd;
  }
  return "Listing fee " + pc + "% = " + @PKG@.AhUtil.fmt(fz[0]) + " + duration fee (" + lab + ") = " + @PKG@.AhUtil.fmt(fz[1]) + " -> you pay " + @PKG@.AhUtil.fmt(tot) + rfd;
}""")
# /ahadmin pause | resume: rewrite only the paused= line of config.properties''')

# ---- review 2026-09-29: config.properties is rewritten byte for byte (ISO-8859-1 = what Properties.load reads; UTF-8 turned ANSI bytes
# like an e-acute into U+FFFD). readText (UTF-8) stays for the JSON records and blocked.txt.
rep(r'''public static String readText(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
}""")''', r'''public static String readText(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
}""")
M(cfg, r"""
public static String readRaw(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "ISO-8859-1");
}""")''')
# setPaused (pre-existing, 0.1): the same one-line swap on its read and its write
rep(r'''    String txt = java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]) ? readText(FILE) : TEMPLATE;''',
    r'''    String txt = java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]) ? readRaw(FILE) : TEMPLATE;''')
rep(r'''    if (!done) sb.append("\npaused=").append(on).append('\n');
    atomicWrite(FILE, sb.toString().getBytes("UTF-8"));''', r'''    if (!done) sb.append("\npaused=").append(on).append('\n');
    atomicWrite(FILE, sb.toString().getBytes("ISO-8859-1"));''')

# ---- migrate(): the one-time config.properties update (before summary)
rep('''M(cfg, r"""
public static String summary() {''', '''# 0.1.2: key / value of one properties line (null key = comment or blank)
M(cfg, r"""
public static int keyEnd(String t) {
  int i = 0;
  while (i < t.length()) { char c = t.charAt(i); if (c == '=' || c == ':' || Character.isWhitespace(c)) break; i++; }
  return i;
}""")
M(cfg, r"""
public static String keyOf(String line) {
  if (line == null) return null;
  String t = line.trim();
  if (t.length() == 0 || t.charAt(0) == '#' || t.charAt(0) == '!') return null;
  return t.substring(0, keyEnd(t));
}""")
M(cfg, r"""
public static String valOf(String line) {
  String t = line.trim();
  String r = t.substring(keyEnd(t)).trim();
  if (r.length() > 0 && (r.charAt(0) == '=' || r.charAt(0) == ':')) r = r.substring(1).trim();
  return r;
}""")
# 0.1.2, once at start (before load): the durations line that is EXACTLY the 0.1.1 stock default becomes 48h:x2 (+ its stock comment); a
# line that is neither the old nor the new stock line is kept (logged). The new keys otherProfileBuy / blockBags / xFloorPrev are appended
# with their comments when absent (the "added by" head only once). sameAccountBuy stays where it is (load() logs it as retired); its old
# comment line gets SAB_MARK once. ISO-8859-1 in and out (byte-preserving, what Properties.load reads), line endings kept, atomic write, one
# INFO line. Returns what changed ("" = nothing; a failure leaves the old file untouched and load() reads it as it is).
M(cfg, r"""
public static synchronized String migrate() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return "";
    String raw = readRaw(FILE);
    boolean crlf = raw.indexOf("\\r\\n") >= 0;
    String[] lines = raw.replace("\\r\\n", "\\n").split("\\n", -1);
    boolean hasOther = false;
    boolean hasBags = false;
    boolean hasFloor = false;
    boolean hasHead = false;
    for (int i = 0; i < lines.length; i++) {
      String k = keyOf(lines[i]);
      if ("otherProfileBuy".equals(k)) hasOther = true;
      if ("blockBags".equals(k)) hasBags = true;
      if ("xFloorPrev".equals(k)) hasFloor = true;
      if (ADDED_HEAD.equals(lines[i].trim())) hasHead = true;
    }
    java.util.ArrayList out = new java.util.ArrayList();
    boolean durDone = false;
    boolean samSeen = false;
    boolean samDone = false;
    String custom = null;
    for (int i = 0; i < lines.length; i++) {
      String l = lines[i];
      if ("durations".equals(keyOf(l))) {
        String v = valOf(l);
        if (v.equals(OLD_DURS)) {
          if (!out.isEmpty() && OLD_DUR_NOTE.equals(out.get(out.size() - 1))) out.set(out.size() - 1, NEW_DUR_NOTE);
          out.add("durations=" + NEW_DURS);
          durDone = true;
          continue;
        }
        if (!v.equals(NEW_DURS)) custom = v;
      }
      String tt = l.trim();
      if (!samSeen && tt.length() > 1 && (tt.charAt(0) == '#' || tt.charAt(0) == '!') && tt.substring(1).trim().startsWith("sameAccountBuy")) {
        samSeen = true;
        if (l.indexOf(SAB_MARK.trim()) < 0) {
          int e = l.length();
          while (e > 0 && (l.charAt(e - 1) == ' ' || l.charAt(e - 1) == '\\t')) e--;
          l = l.substring(0, e) + SAB_MARK;
          samDone = true;
        }
      }
      out.add(l);
    }
    StringBuilder what = new StringBuilder();
    if (durDone) what.append("durations 48h:1200 -> 48h:x2 (a 48h listing pays double the listing fee, at least the 24h price)");
    if (samDone) { if (what.length() > 0) what.append("; "); what.append("sameAccountBuy comment marked retired"); }
    if (!hasOther || !hasBags || !hasFloor) {
      int at = out.size();
      if (at > 0 && ((String) out.get(at - 1)).length() == 0) at--;
      java.util.ArrayList add = new java.util.ArrayList();
      if (!hasHead) add.add(ADDED_HEAD);
      if (!hasOther) { add.add(OTHER_NOTE); add.add("otherProfileBuy=true"); }
      if (!hasBags) { add.add(BAGS_NOTE); add.add("blockBags=true"); }
      if (!hasFloor) { add.add(XFLOOR_NOTE); add.add("xFloorPrev=true"); }
      for (int j = 0; j < add.size(); j++) out.add(at + j, add.get(j));
      if (what.length() > 0) what.append("; ");
      what.append("added").append(hasOther ? "" : " otherProfileBuy=true").append(hasBags ? "" : " blockBags=true").append(hasFloor ? "" : " xFloorPrev=true");
    }
    if (custom != null) @PKG@.AhUtil.info("custom durations kept: " + custom + " (the new stock default is " + NEW_DURS + ": 48h pays double the listing fee, at least the 24h price)");
    if (what.length() == 0) return "";
    StringBuilder sb = new StringBuilder();
    String nl = crlf ? "\\r\\n" : "\\n";
    for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append(nl); sb.append((String) out.get(i)); }
    atomicWrite(FILE, sb.toString().getBytes("ISO-8859-1"));
    @PKG@.AhUtil.info("config.properties updated for 0.1.2: " + what);
    return what.toString();
  } catch (Throwable t) { @PKG@.AhUtil.warn("could not update config.properties for 0.1.2 (the old file is used as it is): " + t); return ""; }
}""")
M(cfg, r"""
public static String summary() {''')

# ---- built-in bag block entries in the shared market:blocked map (owner "builtin"; never in blocked.txt)
rep('''# ================= AhLog: synced auctions.log''', '''# 0.1.2 (D): with blockBags=true the Magic Bags + Accessory Bag entries are published with owner "builtin"; an entry blocked.txt already
# holds for the same key keeps its owner. blockBags=false removes only builtin entries. Called after every loadBlocked().
M(cfg, r"""
public static void applyBuiltin() {
  try {
    java.util.Map m = blockedMap();
    String v = "builtin|" + BAG_REASON;
    String[] keys = new String[] { "Skyy_Sack_*", "Skyy_Accessory_Bag" };
    for (int i = 0; i < keys.length; i++) {
      Object cur = m.get(keys[i]);
      boolean ours = cur != null && String.valueOf(cur).startsWith("builtin|");
      if (BLOCK_BAGS) { if (cur == null || ours) m.put(keys[i], v); }
      else if (ours) m.remove(keys[i]);
    }
  } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void removeBuiltin() {
  try {
    java.util.Map m = blockedMap();
    java.util.Iterator it = new java.util.ArrayList(m.keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object v = m.get(k);
      if (v instanceof String && ((String) v).startsWith("builtin|")) m.remove(k);
    }
  } catch (Throwable t) { }
}""")

# ================= AhLog: synced auctions.log''')

# ======================================================================= AhItem: tiers, names, gear bridge (A), bag block (D)
rep('''F(itm, "public static String[] TIER_NAME;")
F(itm, "public static int[] TIER_VAL;")''', '''F(itm, "public static String[] TIER_NAME;")
F(itm, "public static String TIER_KEY = null;")
F(itm, "public static String[] G_ID = new String[0];")
F(itm, "public static String[] G_NAME = new String[0];")
F(itm, "public static String[] G_HEX = new String[0];")
F(itm, "public static final java.util.concurrent.ConcurrentHashMap TCACHE = new java.util.concurrent.ConcurrentHashMap();")
F(itm, "public static final java.util.Set GEAR_WARNED = java.util.concurrent.ConcurrentHashMap.newKeySet();")''')
rep_method("itm", "public static String qName(int idx) {", r"""
public static String qPretty(String s) {
  if (s == null || s.length() == 0) return "Common";
  if (s.startsWith("Skyy_")) { int u = s.lastIndexOf('_'); if (u >= 0 && u < s.length() - 1) return s.substring(u + 1); }
  return s;
}""")
# (qPretty took qName's place; qName follows it, before qColor) a Skyy_ quality shows its last word: Skyy_Gear_Legendary -> Legendary
rep('''M(itm, r"""
public static String qColor(int idx) {''', '''M(itm, r"""
public static String qName(int idx) {
  @IQ@ q = quality(idx);
  if (q == null) return "Common";
  String s = "Common";
  try { s = String.valueOf(q.getId()); } catch (Throwable t) { return "Common"; }
  return qPretty(s);
}""")
M(itm, r"""
public static String qColor(int idx) {''')
rep('''M(itm, r"""
public static String qColor(int idx) {''', '''# 0.1.2 spec 5.8: Mythic #AA00AA is hard to read on the page - pages use SkyySacks' readable variant #CC66CC (tooltips keep the real one)
M(itm, r"""
public static String pageHex(String hex) {
  if (hex == null) return null;
  if (hex.equalsIgnoreCase("#AA00AA")) return "#CC66CC";
  return hex;
}""")
M(itm, r"""
public static String qColor(int idx) {''')
rep('''  if (q != null) { try { String h = @PKG@.AhUtil.hex(q.getTextColor()); if (h != null) return h; } catch (Throwable t) { } }
  return "#c9d2dd";''', '''  if (q != null) { try { String h = @PKG@.AhUtil.hex(q.getTextColor()); if (h != null) return pageHex(h); } catch (Throwable t) { } }
  return "#c9d2dd";''')
rep_method("itm", "public static synchronized void tiers() {", r"""
public static synchronized void tiers() {
  String key = "";
  try { Object o = @PKG@.AhUtil.bridge().get("gear:tiers"); if (o instanceof String) key = (String) o; } catch (Throwable t) { key = ""; }
  if (TIER_NAME != null && key.equals(TIER_KEY)) return;
  java.util.ArrayList gi = new java.util.ArrayList();
  java.util.ArrayList gn = new java.util.ArrayList();
  java.util.ArrayList gh = new java.util.ArrayList();
  String[] parts = key.split(",");
  for (int i = 0; i < parts.length; i++) {
    String[] f = parts[i].trim().split(":");
    if (f.length < 2 || f[0].trim().length() == 0 || f[1].trim().length() == 0) continue;
    gi.add(f[0].trim());
    gn.add(f[1].trim());
    gh.add(f.length > 2 ? f[2].trim() : "#ffffff");
  }
  String[] ai = new String[gi.size()];
  String[] an = new String[gi.size()];
  String[] ah = new String[gi.size()];
  for (int i = 0; i < ai.length; i++) { ai[i] = (String) gi.get(i); an[i] = (String) gn.get(i); ah[i] = (String) gh.get(i); }
  java.util.ArrayList qn = new java.util.ArrayList();
  java.util.ArrayList qv = new java.util.ArrayList();
  try {
    java.util.Iterator it = @IQ@.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @IQ@)) continue;
      @IQ@ q = (@IQ@) o;
      qn.add(String.valueOf(q.getId()));
      qv.add(Integer.valueOf(q.getQualityValue()));
    }
  } catch (Throwable t) { }
  String[] a = new String[qn.size()];
  int[] v = new int[qn.size()];
  for (int i = 0; i < a.length; i++) { a[i] = (String) qn.get(i); v[i] = ((Integer) qv.get(i)).intValue(); }
  G_ID = ai;
  G_NAME = an;
  G_HEX = ah;
  TIER_NAME = tierList(an, a, v);
  TIER_KEY = key;
}""")
# tierList must come before tiers(): insert it in front of the tiers() block
rep('''# rarity filter tiers = the quality assets with QualityValue 1..5, sorted by value, named by asset id (SkyyGear tiers flow in later)''',
    '''# 0.1.2 rarity filter entries (pure, bare-JVM tested): the SkyyGear ladder first (gear:tiers), then the engine qualities with QualityValue
# 1..5 sorted by value - EXCEPT ids starting with Skyy_ (SkyyGear's / SkyySacks' own qualities never double the vanilla tiers) - named by
# asset id, each name once. No quality assets at all (bare JVM) -> Common .. Legendary.
M(itm, r"""
public static String[] tierList(String[] gearNames, String[] qn, int[] qv) {
  java.util.ArrayList names = new java.util.ArrayList();
  for (int i = 0; gearNames != null && i < gearNames.length; i++) if (gearNames[i] != null && !names.contains(gearNames[i])) names.add(gearNames[i]);
  java.util.ArrayList vn = new java.util.ArrayList();
  java.util.ArrayList vv = new java.util.ArrayList();
  for (int i = 0; qn != null && qv != null && i < qn.length && i < qv.length; i++) {
    String n = qn[i];
    int v = qv[i];
    if (n == null || n.length() == 0 || n.startsWith("Skyy_") || v < 1 || v > 5) continue;
    int at = vv.size();
    for (int k = 0; k < vv.size(); k++) { if (((Integer) vv.get(k)).intValue() > v) { at = k; break; } }
    vv.add(at, Integer.valueOf(v));
    vn.add(at, n);
  }
  if (vn.isEmpty()) {
    String[] dn = new String[] { "Common", "Uncommon", "Rare", "Epic", "Legendary" };
    for (int i = 0; i < dn.length; i++) vn.add(dn[i]);
  }
  for (int i = 0; i < vn.size(); i++) if (!names.contains(vn.get(i))) names.add(vn.get(i));
  String[] out = new String[names.size()];
  for (int i = 0; i < out.length; i++) out[i] = (String) names.get(i);
  return out;
}""")
# rarity filter tiers: gear ladder (gear:tiers, re-read when that bridge value changes) + the vanilla tiers (tierList)''')

GEAR_HELPERS = r'''# ---- 0.1.2 (A) SkyyGear bridge (spec 7.1). Every call gets Object[]{itemId, CLONE of the metadata}; any failure = "not gear" (the
# SkyyRolls / vanilla fallback), logged once per function. gearOn() = SkyyGear is loaded (gear:fn:describe present).
M(itm, r"""
public static Object gcall(String fn, Object arg) {
  Object f = null;
  try { f = @PKG@.AhUtil.bridge().get(fn); } catch (Throwable t) { f = null; }
  if (!(f instanceof java.util.function.Function)) return null;
  try { return ((java.util.function.Function) f).apply(arg); }
  catch (Throwable t) { if (GEAR_WARNED.add(fn)) @PKG@.AhUtil.warn(fn + " threw - shown without SkyyGear text: " + t); return null; }
}""")
M(itm, r"""
public static boolean gearOn() {
  try { return @PKG@.AhUtil.bridge().get("gear:fn:describe") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}""")
M(itm, r"""
public static Object[] gx(String iid, @BD@ meta) {
  return new Object[] { iid == null ? "" : iid, meta == null ? null : (@BD@) meta.clone() };
}""")
M(itm, r"""
public static int gIndex(String rid) {
  tiers();
  String[] a = G_ID;
  for (int i = 0; rid != null && i < a.length; i++) if (a[i].equals(rid)) return i;
  return -1;
}""")
M(itm, r"""
public static String gearTierName(String rid) {
  int i = gIndex(rid);
  String[] n = G_NAME;
  if (i >= 0 && i < n.length) return n[i];
  if (rid == null || rid.length() == 0) return "Normal";
  return String.valueOf(Character.toUpperCase(rid.charAt(0))) + rid.substring(1);
}""")
M(itm, r"""
public static String gearTierHex(String rid) {
  int i = gIndex(rid);
  String[] h = G_HEX;
  if (i >= 0 && i < h.length) return pageHex(h[i]);
  return null;
}""")
M(itm, r"""
public static String gearRarity(String iid, @BD@ meta) {
  Object r = gcall("gear:fn:rarity", gx(iid, meta));
  return r instanceof String ? (String) r : null;
}""")
M(itm, r"""
public static String tierName(String iid, @BD@ meta, int qi) {
  String r = gearRarity(iid, meta);
  if (r != null) return gearTierName(r);
  return qName(qi);
}""")
M(itm, r"""
public static String tierColor(String iid, @BD@ meta, int qi) {
  String r = gearRarity(iid, meta);
  if (r != null) { String h = gearTierHex(r); if (h != null) return h; }
  return qColor(qi);
}""")
# the filter tier of a listing, cached per id + rev + gear:tiers + SkyyGear's config epoch (its migrate table can change a SkyyRolls item)
M(itm, r"""
public static String tierOfRec(@BD@ r) {
  tiers();
  String id = @PKG@.AhRec.id(r);
  String rev = String.valueOf(@PKG@.AhRec.lng(r, "rev", 0L));
  Object ep = null;
  try { ep = @PKG@.AhUtil.bridge().get("config:epoch:SkyyGear"); } catch (Throwable t) { ep = null; }
  String k = TIER_KEY + "|" + ep;
  Object o = TCACHE.get(id);
  if (o instanceof String[]) { String[] a = (String[]) o; if (a[0].equals(rev) && a[1].equals(k)) return a[2]; }
  @BD@ it = @PKG@.AhRec.sub(r, "item");
  String n = tierName(@PKG@.AhRec.str(it, "id", ""), @PKG@.AhRec.sub(it, "meta"), (int) @PKG@.AhRec.lng(it, "quality", 0L));
  if (TCACHE.size() > 20000) TCACHE.clear();
  TCACHE.put(id, new String[] { rev, k, n });
  return n;
}""")
# gear:fn:describe lines (owner-neutral; line 0 = the name); null = not gear or no SkyyGear
M(itm, r"""
public static String[] gearLines(String iid, @BD@ meta) {
  Object o = gcall("gear:fn:describe", gx(iid, meta));
  if (!(o instanceof String[])) return null;
  String[] a = (String[]) o;
  if (a.length == 0 || a[0] == null) return null;
  return a;
}""")
M(itm, r"""
public static String gearName(String iid, @BD@ meta) {
  String[] a = gearLines(iid, meta);
  if (a == null) return null;
  String n = a[0].replace('\n', ' ').trim();
  if (n.length() == 0) return null;
  if (n.length() > 64) n = n.substring(0, 64);
  return n;
}""")
# gear:fn:rollsLine ("Rare - Lv 20 - Strength +12", "Unidentified (Rare, Lv 20)"); its "" (a Normal without modifiers) -> "Normal - Lv 5"
M(itm, r"""
public static String gearSummary(String iid, @BD@ meta) {
  Object o = gcall("gear:fn:rollsLine", gx(iid, meta));
  if (!(o instanceof String)) return null;
  String s = (String) o;
  if (s.length() > 0) return s;
  String r = gearRarity(iid, meta);
  Object lv = gcall("gear:fn:level", gx(iid, meta));
  return (r == null ? "Normal" : gearTierName(r)) + (lv instanceof Number ? " - Lv " + ((Number) lv).intValue() : "");
}""")
M(itm, r"""
public static String gearSig(String iid, @BD@ meta) {
  Object o = gcall("gear:fn:sig", gx(iid, meta));
  return o instanceof String ? (String) o : null;
}""")
'''
rep('''M(itm, r"""
public static String reforge(@BD@ meta) {
  if (meta == null) return null;''', GEAR_HELPERS + '''# SkyyRolls fallback only (SkyyGear migrates SkyyRolls documents itself): null while SkyyGear is loaded
M(itm, r"""
public static String reforge(@BD@ meta) {
  if (meta == null || gearOn()) return null;''')
rep('''M(itm, r"""
public static String plainName(@IS@ s) {''', '''# 0.1.2 roll text of a listing: SkyyGear's summary when SkyyGear is loaded, else the 0.1.1 SkyyRolls parse
M(itm, r"""
public static String rollsText(String iid, @BD@ meta) {
  if (gearOn()) { String g = gearSummary(iid, meta); return g == null ? "" : g; }
  return rollsLine(meta);
}""")
# 0.1.2 the caveat after "A cheaper one is listed": SkyyGear -> "rolls differ" only when the cheapest one's gear:fn:sig differs (spec 7.3.1 A2)
M(itm, r"""
public static String rollsCaveat(String iid, @BD@ meta, @BD@ other) {
  if (gearOn()) {
    String a = gearSig(iid, meta);
    if (a == null || other == null) return "";
    @BD@ oi = @PKG@.AhRec.sub(other, "item");
    String b = gearSig(@PKG@.AhRec.str(oi, "id", ""), @PKG@.AhRec.sub(oi, "meta"));
    return a.equals(b) ? "" : " - rolls differ";
  }
  return hasRolls(meta) ? " - rolls are not compared" : "";
}""")
M(itm, r"""
public static String plainName(@IS@ s) {''')
rep('''M(itm, r"""
public static boolean isBag(String id) {''', '''# 0.1.2 names / colours / sub-lines of a stack (Create page, new records) and of a listing record (rows, item page, Manage)
M(itm, r"""
public static String stackName(@IS@ s) {
  String g = gearName(s.getItemId(), s.getMetadata());
  return g != null ? g : plainName(s);
}""")
M(itm, r"""
public static String stackColor(@IS@ s) { return tierColor(s.getItemId(), s.getMetadata(), s.getQualityIndex()); }""")
M(itm, r"""
public static String stackSub(@IS@ s) {
  String g = gearSummary(s.getItemId(), s.getMetadata());
  if (g != null) return "x" + s.getQuantity() + " - " + g;
  String rf = reforge(s.getMetadata());
  return "x" + s.getQuantity() + " - " + qName(s.getQualityIndex()) + (rf != null ? " - " + rf : "");
}""")
# extra search words of a new listing: the gear rarity name (+ unidentified); "" for everything else
M(itm, r"""
public static String searchExtra(@IS@ s) {
  String r = gearRarity(s.getItemId(), s.getMetadata());
  if (r == null) return "";
  Object idf = gcall("gear:fn:identified", gx(s.getItemId(), s.getMetadata()));
  return gearTierName(r) + ((idf instanceof Boolean && !((Boolean) idf).booleanValue()) ? " unidentified" : "");
}""")
M(itm, r"""
public static String dispName(@BD@ r) {
  @BD@ it = @PKG@.AhRec.sub(r, "item");
  String iid = @PKG@.AhRec.str(it, "id", "");
  String g = gearName(iid, @PKG@.AhRec.sub(it, "meta"));
  return g != null ? g : @PKG@.AhRec.str(r, "name", iid);
}""")
M(itm, r"""
public static String dispColor(@BD@ r) {
  @BD@ it = @PKG@.AhRec.sub(r, "item");
  return tierColor(@PKG@.AhRec.str(it, "id", ""), @PKG@.AhRec.sub(it, "meta"), (int) @PKG@.AhRec.lng(it, "quality", 0L));
}""")
M(itm, r"""
public static String dispSub(@BD@ r) {
  @BD@ it = @PKG@.AhRec.sub(r, "item");
  String iid = @PKG@.AhRec.str(it, "id", "");
  @BD@ meta = @PKG@.AhRec.sub(it, "meta");
  long qty = @PKG@.AhRec.lng(it, "qty", 1L);
  String g = gearSummary(iid, meta);
  if (g != null) return "x" + qty + " - " + g;
  String rf = reforge(meta);
  return "x" + qty + " - " + qName((int) @PKG@.AhRec.lng(it, "quality", 0L)) + (rf != null ? " - " + rf : "");
}""")
M(itm, r"""
public static boolean isBag(String id) {''')
# review 2026-09-29 (finding 1): no-wrap text lines are cut to fit; sizes measured with the game's NunitoSans metrics (UI/Fonts/*.json:
# ~0.59 em per character, line height 1.364 em). Browse row sub-line 380 px @ 13 px -> 52 characters (a worst-case gear line = 330 px);
# Create page picked-item line 980 px @ 14 px -> 96 + " - backpack slot 36" (803 px); item page "Gear: ..." fact 840 px @ 16 px -> 96
# (774 px); item page gear text box 266 px @ 15 px = 13 lines of 20.5 px -> at most 12, ~90 characters per wrapped line of 840 px.
rep(r'''M(itm, r"""
public static boolean isBag(String id) {''', r'''F(itm, "public static final int ROW_SUB = 52;")
F(itm, "public static final int SEL_SUB = 96;")
F(itm, "public static final int FACT_SUB = 96;")
F(itm, "public static final int DESC_LINES = 12;")
F(itm, "public static final int DESC_WRAP = 90;")
# s cut to n characters ending in ".." (a trailing " - ", "+", ",", "(" or ":" is dropped before the dots); null -> ""
M(itm, r"""
public static String clip(String s, int n) {
  if (s == null) return "";
  if (s.length() <= n) return s;
  if (n < 3) return s.substring(0, n < 0 ? 0 : n);
  int e = n - 2;
  while (e > 0) {
    char c = s.charAt(e - 1);
    if (c == ' ' || c == '-' || c == '+' || c == ',' || c == '(' || c == ':') e--; else break;
  }
  return s.substring(0, e) + "..";
}""")
# the Browse row sub-line: dispSub cut to ROW_SUB; " - OFF THE MARKET" always stays whole (the item page keeps the full text)
M(itm, r"""
public static String rowSub(@BD@ r, boolean blocked) {
  String tail = blocked ? " - OFF THE MARKET" : "";
  return clip(dispSub(r), ROW_SUB - tail.length()) + tail;
}""")
M(itm, r"""
public static int vlines(String s, int perLine) {
  if (s == null || s.length() == 0 || perLine < 1) return 1;
  return 1 + (s.length() - 1) / perLine;
}""")
# the item page's gear text (lines from index `from`, one per row): at most maxLines rows; with more, the last row is "..."
M(itm, r"""
public static String descText(String[] gl, int from, int maxLines, int perLine) {
  if (gl == null) return "";
  int total = 0;
  for (int i = from; i < gl.length; i++) { if (gl[i] != null) total = total + vlines(gl[i], perLine); }
  int budget = total <= maxLines ? maxLines : maxLines - 1;
  StringBuilder sb = new StringBuilder();
  int used = 0;
  for (int i = from; i < gl.length; i++) {
    if (gl[i] == null) continue;
    int v = vlines(gl[i], perLine);
    if (used + v > budget) { if (sb.length() > 0) sb.append('\n'); sb.append("..."); break; }
    if (sb.length() > 0) sb.append('\n');
    sb.append(gl[i]);
    used = used + v;
  }
  return sb.toString();
}""")
M(itm, r"""
public static boolean isBag(String id) {''')
# (D) built-in bag block: answered first, whatever market:blocked holds
rep('''public static String blockedReason(String id) {
  if (id == null) return null;
  Object o = @PKG@.AhUtil.bridge().get("market:blocked");''', '''public static String blockedReason(String id) {
  if (id == null) return null;
  if (@PKG@.AhCfg.BLOCK_BAGS && isBag(id)) return @PKG@.AhCfg.BAG_REASON;
  Object o = @PKG@.AhUtil.bridge().get("market:blocked");''')

# ======================================================================= AhStore
rep('''  String id = @PKG@.AhRec.id(r);
  STACKS.remove(id);
  if (@PKG@.AhRec.bool(r, "closed", false)) {''', '''  String id = @PKG@.AhRec.id(r);
  STACKS.remove(id);
  @PKG@.AhItem.TCACHE.remove(id);
  if (@PKG@.AhRec.bool(r, "closed", false)) {''')
rep('''# display cache (deliveries always restore fresh from the record)''', '''# 0.1.2: the cheapest buyable listing of an item id (ties: the lower listing number) - the record whose gear:fn:sig the item page compares
M(sto, r"""
public static @BD@ cheapest(String itemId, String skipId, long now) {
  if (itemId == null) return null;
  @BD@ best = null;
  long bestEach = -1L;
  java.util.Iterator it = LIVE.values().iterator();
  while (it.hasNext()) {
    @BD@ r = (@BD@) it.next();
    if (!buyable(r, now) || !itemId.equals(@PKG@.AhRec.subStr(r, "item", "id", ""))) continue;
    if (skipId != null && skipId.equals(@PKG@.AhRec.id(r))) continue;
    long q = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
    if (q < 1L) q = 1L;
    long each = @PKG@.AhUtil.ceilDiv(@PKG@.AhRec.lng(r, "price", 0L), q);
    if (best == null || each < bestEach || (each == bestEach && @PKG@.AhRec.numId(r) < @PKG@.AhRec.numId(best))) { best = r; bestEach = each; }
  }
  return best;
}""")
# display cache (deliveries always restore fresh from the record)''')
# review (finding 5): the listing name (gear name) and the extra search words come in as arguments - list0 asks the gear bridge BEFORE it
# takes the fee and removes the item, so no bridge call runs between moving coins / items and writing the record
rep('''public static @BD@ newRecord(String id, java.util.UUID u, String key, String name, String prof, @BD@ snap, @IS@ orig, long price, int durIdx, long feeL, long feeD, long now) {''',
    '''public static @BD@ newRecord(String id, java.util.UUID u, String key, String name, String prof, @BD@ snap, @IS@ orig, long price, int durIdx, long feeL, long feeD, long now, String nm0, String gxs0) {''')
rep('''  String nm = @PKG@.AhItem.plainName(orig);
  r.put("name", new org.bson.BsonString(nm));
  r.put("search", new org.bson.BsonString((nm + " " + orig.getItemId() + " " + (name == null ? "" : name)).toLowerCase()));''',
    '''  String nm = nm0 == null || nm0.length() == 0 ? orig.getItemId() : nm0;
  r.put("name", new org.bson.BsonString(nm));
  String gxs = gxs0 == null ? "" : gxs0;
  r.put("search", new org.bson.BsonString((nm + " " + orig.getItemId() + " " + (name == null ? "" : name) + (gxs.length() > 0 ? " " + gxs : "")).toLowerCase()));''')
rep('''  String tw = @PKG@.AhItem.tradeable(orig);
  if (tw != null) return new @RES@(false, tw);''', '''  String tw = @PKG@.AhItem.tradeable(orig);
  if (tw != null) return new @RES@(false, tw);
  String gName = @PKG@.AhItem.stackName(orig);
  String gExtra = @PKG@.AhItem.searchExtra(orig);''')
rep('''  long feeL = @PKG@.AhCfg.listingFee(price);
  long feeD = @PKG@.AhCfg.DUR_FEE[durIdx];
  long fee = feeL + feeD;''', '''  long[] fz = @PKG@.AhCfg.fees(price, durIdx);
  long feeL = fz[0];
  long feeD = fz[1];
  long fee = feeL + feeD;''')
rep('''  @BD@ r = newRecord(id, u, key, name, prof, snap, orig, price, durIdx, feeL, feeD, now);
  if (!write(r)) {''', '''  @BD@ r = newRecord(id, u, key, name, prof, snap, orig, price, durIdx, feeL, feeD, now, gName, gExtra);
  if (fz[2] > 0L) { @BD@ fd = @PKG@.AhRec.sub(r, "fee"); if (fd != null) fd.put("mult", new org.bson.BsonInt64(fz[2])); }
  if (!write(r)) {''')
rep('''" fee=" + fee + " ends=" + @PKG@.AhCfg.DUR_LABEL[durIdx]);''',
    '''" fee=" + fee + " ends=" + @PKG@.AhCfg.DUR_LABEL[durIdx] + (fz[2] > 0L ? " feeMult=x" + fz[2] + (fz[3] > 0L ? " feeFloor=prev" : "") : ""));''')
rep('''  if (sUuid.equals(u.toString()) && !@PKG@.AhCfg.SAME_ACCOUNT) return new @RES@(false, "You cannot buy from your own account (another of your profiles listed it).");''',
    '''  if (sUuid.equals(u.toString()) && !@PKG@.AhCfg.OTHER_PROFILE) return new @RES@(false, "Buying from your own account is switched off on this server (another of your profiles listed it).");''')

# ======================================================================= AhPage
rep('''  int tv = -1;
  if (this.rar > 0 && this.rar <= @PKG@.AhItem.TIER_VAL.length) tv = @PKG@.AhItem.TIER_VAL[this.rar - 1];''', '''  String tn = null;
  String[] tnames = @PKG@.AhItem.TIER_NAME;
  if (this.rar > 0 && tnames != null && this.rar <= tnames.length) tn = tnames[this.rar - 1];''')
rep('''    if (tv >= 0 && @PKG@.AhItem.qValue((int) @PKG@.AhRec.subLng(r, "item", "quality", 0L)) != tv) continue;''',
    '''    if (tn != null && !tn.equals(@PKG@.AhItem.tierOfRec(r))) continue;''')
rep('''      long qty = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
      int qi = (int) @PKG@.AhRec.subLng(r, "item", "quality", 0L);
      String row = "#SkyyAhRow" + i;''', '''      long qty = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
      String row = "#SkyyAhRow" + i;''')
rep('''      txt(b, "#SkyyAhRowTxt" + i, "SkyyAhRowName" + i, 0, 32, 17, true, @PKG@.AhItem.qColor(qi), null, false, @PKG@.AhRec.str(r, "name", iid));
      String rf = @PKG@.AhItem.reforge(@PKG@.AhRec.sub(@PKG@.AhRec.sub(r, "item"), "meta"));
      String blk = @PKG@.AhItem.blockedReason(iid);
      String sub = "x" + qty + " - " + @PKG@.AhItem.qName(qi) + (rf != null ? " - " + rf : "") + (blk != null ? " - OFF THE MARKET" : "");''',
    '''      txt(b, "#SkyyAhRowTxt" + i, "SkyyAhRowName" + i, 0, 32, 17, true, @PKG@.AhItem.dispColor(r), null, false, @PKG@.AhItem.dispName(r));
      String blk = @PKG@.AhItem.blockedReason(iid);
      String sub = @PKG@.AhItem.rowSub(r, blk != null);''')

rep_method("page", "public void renderItem(@UCB@ b, @UEB@ ev, java.util.UUID u, long now) {", r"""
public void renderItem(@UCB@ b, @UEB@ ev, java.util.UUID u, long now) {
  @BD@ r = @PKG@.AhStore.get(this.detailId);
  boolean live = @PKG@.AhStore.buyable(r, now);
  b.appendInline("#SkyyAh", "Group #SkyyAhDBody { Anchor: (Height: 560); LayoutMode: Left; }");
  b.appendInline("#SkyyAhDBody", "Group #SkyyAhDLeft { Anchor: (Width: 220, Height: 560); }");
  b.appendInline("#SkyyAhDLeft", "ItemGrid #SkyyAhDGrid { Anchor: (Left: 20, Top: 10, Width: 180, Height: 180); SlotsPerRow: 1; AreItemsDraggable: false; InfoDisplay: None; Style: (SlotSize: 180, SlotIconSize: 140, SlotSpacing: 0); }");
  b.appendInline("#SkyyAhDBody", "Group #SkyyAhDRight { Anchor: (Width: 840, Height: 560); LayoutMode: Top; }");
  int qi = r == null ? 0 : (int) @PKG@.AhRec.subLng(r, "item", "quality", 0L);
  String iid = r == null ? "" : @PKG@.AhRec.subStr(r, "item", "id", "");
  @BD@ meta = r == null ? null : @PKG@.AhRec.sub(@PKG@.AhRec.sub(r, "item"), "meta");
  String[] gl = null;
  if (r != null) gl = @PKG@.AhItem.gearLines(iid, meta);
  b.appendInline("#SkyyAhDRight", lab("SkyyAhDName", 0, 40, 22, true, r == null ? @PKG@.AhItem.qColor(0) : @PKG@.AhItem.dispColor(r), null, false));
  b.appendInline("#SkyyAhDRight", "Label #SkyyAhDDesc { Anchor: (Height: 266); Text: \"\"; Style: (FontSize: 15, TextColor: #c9dff0, Wrap: true); }");
  for (int i = 0; i < 9; i++) b.appendInline("#SkyyAhDRight", lab("SkyyAhDFact" + i, 0, 28, 16, i == 4, i == 8 ? "#ffb070" : (i == 4 ? "#ffd36a" : "#dfe9f5"), null, false));
  String[] facts = new String[9];
  for (int i = 0; i < 9; i++) facts[i] = "";
  String cheaper = null;
  String nm = "";
  long price = -1L;
  boolean sameAcc = r != null && u.toString().equals(@PKG@.AhRec.subStr(r, "seller", "uuid", ""));
  if (r == null) {
    b.set("#SkyyAhDName.Text", "This listing is gone");
    b.set("#SkyyAhDDesc.Text", "It was bought, cancelled or it expired. Go back to the results.");
    this.detailPrice = -1L;
  } else {
    price = @PKG@.AhRec.lng(r, "price", 0L);
    this.detailPrice = price;
    nm = @PKG@.AhItem.dispName(r);
    @IS@ st = @PKG@.AhStore.stackOf(r);
    if (st != null) {
      java.util.ArrayList slots = new java.util.ArrayList();
      slots.add(new @IGS@(new @IS@(st.getItemId(), st.getQuantity())));   // 0.1.1: NO metadata in a grid slot (client disconnect)
      b.set("#SkyyAhDGrid.Slots", slots);
    }
    boolean named = false;
    if (gl != null) {
      // 0.1.2: SkyyGear's own owner-neutral lines (spec 6.3: the AH shows its text via gear:fn:describe, not the seller's tooltip)
      b.set("#SkyyAhDName.Text", gl[0]);
      b.set("#SkyyAhDDesc.Text", @PKG@.AhItem.descText(gl, 1, @PKG@.AhItem.DESC_LINES, @PKG@.AhItem.DESC_WRAP));   // review: fits the 266 px box
      named = true;
    } else if (st != null && @PKG@.AhCfg.SPANS) {
      try {
        @MSG@ dn = st.getDisplayName();
        if (dn != null && @PKG@.AhUtil.plain(dn).trim().length() > 0) { b.set("#SkyyAhDName.TextSpans", dn); named = true; }
        @MSG@ dd = st.getDisplayDescription();
        if (dd != null && @PKG@.AhUtil.plain(dd).trim().length() > 0) b.set("#SkyyAhDDesc.TextSpans", dd);
        else b.set("#SkyyAhDDesc.Text", "");
      } catch (Throwable t) { named = false; }
    }
    if (!named) {
      b.set("#SkyyAhDName.Text", nm);
      String d = "";
      if (st != null) { try { d = @PKG@.AhUtil.plain(st.getDisplayDescription()); } catch (Throwable t) { d = ""; } }
      String rl = @PKG@.AhItem.rollsText(iid, meta);
      if (rl.length() > 0 && d.indexOf("Reforge") < 0) d = (d.length() > 0 ? d + "\n\n" : "") + rl;
      b.set("#SkyyAhDDesc.Text", d);
    }
    long qty = @PKG@.AhRec.subLng(r, "item", "qty", 1L);
    @BD@ it = @PKG@.AhRec.sub(r, "item");
    double cd = @PKG@.AhRec.dbl(it, "durability", 0.0);
    double md = @PKG@.AhRec.dbl(it, "maxDurability", 0.0);
    String sk = @PKG@.AhRec.subStr(r, "seller", "key", "");
    String gs = gl != null ? @PKG@.AhItem.gearSummary(iid, meta) : null;
    facts[0] = gs != null ? @PKG@.AhItem.clip("Gear: " + gs, @PKG@.AhItem.FACT_SUB) : "Rarity: " + @PKG@.AhItem.qName(qi);
    facts[1] = "Quantity: " + qty;
    facts[2] = md > 0.0 ? "Durability: " + Math.round(cd) + " / " + Math.round(md) : "Durability: -";
    String sprof = @PKG@.AhRec.subStr(r, "seller", "profile", "");
    facts[3] = "Seller: " + @PKG@.AhRec.subStr(r, "seller", "name", "?") + (this.key.equals(sk) ? " (you)" : (sameAcc ? " (your other profile" + (sprof.length() > 0 ? " " + sprof : "") + ")" : ""));
    facts[4] = "Price: " + @PKG@.AhUtil.fmt(price) + " coins" + (qty > 1L ? " - " + @PKG@.AhUtil.fmt(@PKG@.AhUtil.ceilDiv(price, qty)) + " each" : "");
    facts[5] = live ? "Ends in: " + @PKG@.AhUtil.timeLeft(@PKG@.AhRec.lng(r, "endsAt", 0L) - now) : "Ends in: ended";
    facts[6] = "Listed: " + @PKG@.AhUtil.ago(now - @PKG@.AhRec.lng(r, "createdAt", now));
    facts[7] = "Listing #" + @PKG@.AhRec.id(r);
    long[] lo = @PKG@.AhStore.lowestBin(iid, @PKG@.AhRec.id(r), now);
    long each = @PKG@.AhUtil.ceilDiv(price, qty < 1L ? 1L : qty);
    String w = "";
    if (lo[0] > 0L && lo[0] < each) {
      cheaper = @PKG@.AhUtil.fmt(lo[0]);
      w = "A cheaper one is listed: " + cheaper + " each (" + lo[1] + " listed)" + @PKG@.AhItem.rollsCaveat(iid, meta, @PKG@.AhStore.cheapest(iid, @PKG@.AhRec.id(r), now));
    }
    if (@PKG@.AhItem.isBag(iid) && !@PKG@.AhCfg.BLOCK_BAGS) w = w + (w.length() > 0 ? " - " : "") + "Contents not included.";
    facts[8] = w;
  }
  for (int i = 0; i < 9; i++) b.set("#SkyyAhDFact" + i + ".Text", facts[i]);
  b.appendInline("#SkyyAh", "Group #SkyyAhDAct { Anchor: (Height: 60); LayoutMode: Left; Padding: (Top: 5); }");
  String note = null;
  if (r == null) note = "This listing is no longer for sale.";
  else if (@PKG@.AhRec.readOnly(r)) note = "This listing needs a newer SkyyAuctions.";
  else if (!live) note = "This listing is no longer for sale.";
  boolean own = r != null && this.key.equals(@PKG@.AhRec.subStr(r, "seller", "key", ""));
  if (note == null && own) {
    if (armedFor("cancel", this.detailId, this.detailPrice)) {
      long fee = @PKG@.AhRec.subLng(r, "fee", "listing", 0L) + @PKG@.AhRec.subLng(r, "fee", "duration", 0L);
      txt(b, "#SkyyAhDAct", "SkyyAhDAsk", 420, 50, 15, true, "#ffd36a", null, true, @PKG@.AhCfg.CANCEL_REFUND ? "Cancel this listing? The fee is refunded." : "Cancel? The " + @PKG@.AhUtil.fmt(fee) + " coin fee is not refunded.");
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDConfirm", 180, 50, "Yes, cancel", BS_RED, "confirm");
      sp(b, "#SkyyAhDAct", 10, 50);
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDNo", 180, 50, "No", BS, "no");
      sp(b, "#SkyyAhDAct", 20, 50);
    } else {
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDCancel", 360, 50, "Cancel listing", BS_RED, "dcancel");
      sp(b, "#SkyyAhDAct", 450, 50);
    }
  } else if (note == null && sameAcc && !@PKG@.AhCfg.OTHER_PROFILE) {
    note = "Listed by your other profile " + @PKG@.AhRec.subStr(r, "seller", "profile", "") + " - buying from your own account is off on this server.";
  } else if (note == null && @PKG@.AhItem.blockedReason(iid) != null) {
    note = "Off the market (" + @PKG@.AhItem.blockedReason(iid) + ") - it cannot be bought.";
  } else if (note == null) {
    long grace = @PKG@.AhRec.lng(r, "graceUntil", 0L);
    if (now < grace) {
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDBuy", 360, 50, "Buy (opens in " + ((grace - now + 999L) / 1000L) + " s)", BS, "buy");
      sp(b, "#SkyyAhDAct", 450, 50);
    } else if (armedFor("buy", this.detailId, this.detailPrice)) {
      String q = "Pay " + @PKG@.AhUtil.fmt(price) + " coins for " + nm + "?" + (cheaper != null ? " A cheaper one is listed at " + cheaper + " each." : "");
      txt(b, "#SkyyAhDAct", "SkyyAhDAsk", 420, 50, 15, true, "#ffd36a", null, true, q);
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDConfirm", 180, 50, "Confirm", BS_GREEN, "confirm");
      sp(b, "#SkyyAhDAct", 10, 50);
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDNo", 180, 50, "Cancel", BS, "no");
      sp(b, "#SkyyAhDAct", 20, 50);
    } else {
      btn(b, ev, "#SkyyAhDAct", "SkyyAhDBuy", 360, 50, "Buy now - " + @PKG@.AhUtil.fmt(price) + " coins", BS_GREEN, "buy");
      sp(b, "#SkyyAhDAct", 450, 50);
    }
  }
  if (note != null) {
    txt(b, "#SkyyAhDAct", "SkyyAhDNote", 810, 50, 16, true, "#ffb070", null, true, note);
  }
  btn(b, ev, "#SkyyAhDAct", "SkyyAhDBack", 240, 50, "< Back to results", BS_BLUE, "back");
}""")

rep('''    txt(b, "#SkyyAhSelTxt", "SkyyAhSelName", 0, 30, 18, true, @PKG@.AhItem.qColor(picked.getQualityIndex()), null, false, @PKG@.AhItem.plainName(picked));
    String rf = @PKG@.AhItem.reforge(picked.getMetadata());
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelInfo", 0, 22, 14, false, "#9fb8cc", null, false, "x" + pq + " - " + @PKG@.AhItem.qName(picked.getQualityIndex()) + (rf != null ? " - " + rf : "") + " - " + @PKG@.AhItem.secName(this.pickSec) + " slot " + (this.pickSlot + 1));
    long[] lo = @PKG@.AhStore.lowestBin(pid, null, now);
    String h = lo[0] > 0L ? "Lowest BIN for this item now: " + @PKG@.AhUtil.fmt(lo[0]) + " each (" + lo[1] + " listed)" : "None listed right now.";''',
    '''    txt(b, "#SkyyAhSelTxt", "SkyyAhSelName", 0, 30, 18, true, @PKG@.AhItem.stackColor(picked), null, false, @PKG@.AhItem.stackName(picked));
    txt(b, "#SkyyAhSelTxt", "SkyyAhSelInfo", 0, 22, 14, false, "#9fb8cc", null, false, @PKG@.AhItem.clip(@PKG@.AhItem.stackSub(picked), @PKG@.AhItem.SEL_SUB) + " - " + @PKG@.AhItem.secName(this.pickSec) + " slot " + (this.pickSlot + 1));
    long[] lo = @PKG@.AhStore.lowestBin(pid, null, now);
    boolean gearPick = @PKG@.AhItem.gearRarity(pid, picked.getMetadata()) != null;
    String h = lo[0] > 0L ? "Lowest BIN for this item now: " + @PKG@.AhUtil.fmt(lo[0]) + " each (" + lo[1] + " listed" + (gearPick ? ", any rarity" : "") + ")" : "None listed right now.";''')
# review (finding 8): a picked bag shows why it cannot be sold while blockBags=true (the "Contents not included" note is for blockBags=false)
rep('''    if (@PKG@.AhItem.isBag(pid)) h = h + " Contents not included - a bag opens its owner's own storage.";''',
    '''    if (@PKG@.AhItem.isBag(pid)) h = @PKG@.AhCfg.BLOCK_BAGS ? "Off the market: " + @PKG@.AhCfg.BAG_REASON + "." : h + " Contents not included - a bag opens its owner's own storage.";''')
rep('''    long lf = @PKG@.AhCfg.listingFee(pp);
    long df = @PKG@.AhCfg.DUR_FEE[this.durIdx];
    f0 = "Listing fee " + @PKG@.AhCfg.pctText(@PKG@.AhCfg.pctFor(pp)) + "% = " + @PKG@.AhUtil.fmt(lf) + " + duration fee (" + dl[this.durIdx] + ") = " + @PKG@.AhUtil.fmt(df) + " -> you pay " + @PKG@.AhUtil.fmt(lf + df) + " coins now (" + (@PKG@.AhCfg.CANCEL_REFUND ? "refunded" : "not refunded") + " if you cancel).";''',
    '''    f0 = @PKG@.AhCfg.feeLine(pp, this.durIdx);     // 0.1.2: flat presets as before; xN names the multiplier and the xFloorPrev floor''')
# review (finding 8): the pick message names the item as the page does (gear name)
rep('''say("Picked " + @PKG@.AhItem.plainName(x) + " - type a price.", 0);''', '''say("Picked " + @PKG@.AhItem.stackName(x) + " - type a price.", 0);''')
rep('''      txt(b, "#SkyyAhMTxt" + i, "SkyyAhMName" + i, 0, 32, 17, true, @PKG@.AhItem.qColor(qi), null, false, @PKG@.AhRec.str(r, "name", iid));''',
    '''      txt(b, "#SkyyAhMTxt" + i, "SkyyAhMName" + i, 0, 32, 17, true, @PKG@.AhItem.dispColor(r), null, false, @PKG@.AhItem.dispName(r));''')

# ======================================================================= admin commands, plugin
rep('''  if (@PKG@.AhCfg.SAME_ACCOUNT) atell(pr, "sameAccountBuy=true - solo testing only");''',
    '''  atell(pr, "Gear text: " + (@PKG@.AhItem.gearOn() ? "SkyyGear bridge (rarity filter = the Wynn ladder, then the vanilla tiers)" : "SkyyGear not loaded - SkyyRolls fallback, vanilla tiers") + " | Magic Bags + Accessory Bag " + (@PKG@.AhCfg.BLOCK_BAGS ? "blocked (built in)" : "tradeable (blockBags=false)"));''')
rep('''" + duration " + @PKG@.AhRec.subLng(r, "fee", "duration", 0L) + " refunded "''',
    '''" + duration " + @PKG@.AhRec.subLng(r, "fee", "duration", 0L) + @PKG@.AhCmds.multNote(r) + " refunded "''')
# /ahadmin info: the xN note of a record; "raised to the price of the preset before it" when listing x mult < listing + duration (the xFloorPrev floor)
rep('''M(cmds, r"""
public static void info(@PR@ pr, String id) {''', '''M(cmds, r"""
public static String multNote(@BD@ r) {
  long m = @PKG@.AhRec.subLng(r, "fee", "mult", 0L);
  if (m <= 0L) return "";
  long l = @PKG@.AhRec.subLng(r, "fee", "listing", 0L);
  long d = @PKG@.AhRec.subLng(r, "fee", "duration", 0L);
  return " (x" + m + " listing fee" + (l * m < l + d ? ", raised to the price of the preset before it (xFloorPrev)" : "") + ")";
}""")
M(cmds, r"""
public static void info(@PR@ pr, String id) {''')
rep('''  int n = @PKG@.AhCfg.loadBlocked();
  atell(pr, "config.properties and Skyy_Market/blocked.txt re-read (" + n + " blocked entries from the file). Listings are not re-read.");''',
    '''  int n = @PKG@.AhCfg.loadBlocked();
  @PKG@.AhCfg.applyBuiltin();
  atell(pr, "config.properties and Skyy_Market/blocked.txt re-read (" + n + " blocked entries from the file; Magic Bags + Accessory Bag " + (@PKG@.AhCfg.BLOCK_BAGS ? "blocked built in" : "tradeable") + "). Listings are not re-read.");''')
rep('''  @PKG@.AhCfg.load();
  int nb = @PKG@.AhCfg.loadBlocked();''', '''  @PKG@.AhCfg.migrate();
  @PKG@.AhCfg.load();
  int nb = @PKG@.AhCfg.loadBlocked();
  @PKG@.AhCfg.applyBuiltin();''')
rep('''" blocked entries from Skyy_Market/blocked.txt, coins bridge "''',
    '''" blocked entries from Skyy_Market/blocked.txt, Magic Bags + Accessory Bag " + (@PKG@.AhCfg.BLOCK_BAGS ? "blocked" : "tradeable") + ", durations " + @PKG@.AhCfg.durTok(0) + ".." + @PKG@.AhCfg.durTok(@PKG@.AhCfg.DUR_LABEL.length - 1) + ", other profiles " + (@PKG@.AhCfg.OTHER_PROFILE ? "may" : "may not") + " buy, coins bridge "''')
rep('''  try { @PKG@.AhCfg.removeFileEntries(); } catch (Throwable t) { }
  if (clean)''', '''  try { @PKG@.AhCfg.removeFileEntries(); } catch (Throwable t) { }
  try { @PKG@.AhCfg.removeBuiltin(); } catch (Throwable t) { }
  if (clean)''')

# nothing of the retired names may survive
for _gone in ("SAME_ACCOUNT", "TIER_VAL", "DUR_FEE[durIdx]", "DUR_FEE[this.durIdx]",
              # review 2026-09-29: config.properties only through readRaw (ISO-8859-1); no gear bridge call inside newRecord; old texts
              "readText(FILE)", "AhItem.stackName(orig);\n  r.put", "AhItem.searchExtra(orig);\n  r.put", "the defaults still apply",
              "AhItem.plainName(x)", "AhItem.dispSub(r) + (blk"):
    assert _gone not in s, "left over: " + _gone
for _need in ("X_FLOOR = boolP(p, \"xFloorPrev\", true);", "f0 = @PKG@.AhCfg.feeLine(pp, this.durIdx);", "AhItem.rowSub(r, blk != null)",
              "AhItem.descText(gl, 1,", "newRecord(id, u, key, name, prof, snap, orig, price, durIdx, feeL, feeD, now, gName, gExtra)",
              "if (!v.equals(NEW_DURS)) custom = v;", "getBytes(\"ISO-8859-1\")"):
    assert s.count(_need) >= 1, "missing: " + _need
# gear name + search words are computed before the fee is taken (list0: tradeable -> gName/gExtra -> ... -> Coins.take)
_l0 = s.index("public static @RES@ list0(")
assert s.index("String gExtra = @PKG@.AhItem.searchExtra(orig);", _l0) < s.index("@PKG@.Coins.take(u, fee)", _l0), "gear calls after Coins.take"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
