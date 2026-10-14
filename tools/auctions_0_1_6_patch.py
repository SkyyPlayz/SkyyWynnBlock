"""Derive SkyyAuctions/build_skyyauctions_0.1.6.py from the GENERATED 0.1.5 script (the SET pin; 0.1.5 and every older script stay untouched):
    python tools/auctions_0_1_6_patch.py
    python SkyyAuctions/build_skyyauctions_0.1.6.py          (must end 'assembled ...SkyyAuctions-0.1.6.jar')
    python SkyyAuctions/test_skyyauctions_0.1.6.py           (harness)
Edit THIS patch, never the generated script.

0.1.6 (2026-10-14) = ECONOMY ROUND econ38, the Auction House part - SAME-ACCOUNT BUYS BLOCKED (Skyy's popup 2026-10-14 "Block them
(Recommended)" - docs/answered/economy.md 2026-10-14 ALT TRANSFERS: "/pay and AH buys between profiles of the SAME account are refused;
trading with other players unchanged"):
 A. BUY: a listing made by ANOTHER profile of the buyer's own account (seller.uuid = the buyer's UUID, a different profile key - the
    same profile could never buy its own listing) is refused when SkyyCoins' switch says so: Coins.ownBlocked asks coins:fn:sameacct
    (SkyyCoins 0.1.8+; Server Setup -> Coins -> "Block coins between own profiles", default ON) with { buyer key, seller key }.
    TRUE -> refused: "You can't buy from your own other profile - coins never move between your own profiles on this server." No
    answer (SkyyCoins older than 0.1.8, missing, a throw, a non-Boolean) = refused too (Skyy's default). The check runs inside the
    Auction House lock, BEFORE any coin is taken (coins:fn:sameacct is pure: no lock, no I/O, never calls back).
    The old AH-only switch otherProfileBuy (config.properties, default true) still works on top: false = refused whatever SkyyCoins says
    (its own old message). So: SkyyCoins' switch ON -> refused; OFF -> otherProfileBuy decides (true = allowed, as 0.1.5).
 B. THE PAGE: the listing's detail view shows "Listed by your other profile <name> - coins never move between your own profiles on this
    server." instead of the Buy button when A would refuse (asked when the page is drawn; the buy re-checks).
 C. BIDS: none - the Auction House is Buy It Now only (Skyy 2026-09-24), so there is no bid path to block.
 D. /ahadmin status + the ready line say whether same-account buys are blocked (and why).
 E. The otherProfileBuy comment written into a NEW config.properties (and by the 0.1.2 append) now says SkyyCoins' switch decides when
    it is true (critic 2026-10-14: the old "may buy" wording read as "allowed"). Existing files keep their old comment - a comment line
    only, so no migration.
 Other players' buys are unchanged (different UUID = never asked). Nothing in the saved data changes; no config key added or migrated.
 ROLLBACK to 0.1.5 is safe (0.1.5 follows otherProfileBuy alone = same-account buys allowed again with the default file).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.5.py")
dst = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.6.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
S0 = s
assert 'VERSION = "0.1.5"' in s and "closeAll0" in s and "ownBlocked" not in s, "the source must be the generated 0.1.5 script"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append((old, new))


rep('VERSION = "0.1.5"', 'VERSION = "0.1.6"')
assert s.startswith('"""0.1.5 (2026-10-14)')
s = ('"""0.1.6 (2026-10-14): SAME-ACCOUNT BUYS BLOCKED (Skyy "Block them") - a listing of your OTHER profile cannot be bought while\n'
     '  SkyyCoins\' switch (coins:fn:sameacct, Server Setup -> Coins) says so (default ON; no answer = blocked); the page says why.\n'
     '  Notes in tools/auctions_0_1_6_patch.py.\n' + s[3:])

# ---- A: Coins.ownBlocked (the AH's SkyyCoins wrapper class; before AhStore / the page, which call it)
rep('''M(coin, r"""
public static int take(java.util.UUID u, long n) {''', '''# 0.1.6 A: may the profile buyerKey buy from the profile sellerKey of the SAME player? SkyyCoins 0.1.8+ coins:fn:sameacct answers TRUE =
# refuse (its switch is ON). No answer (older / missing SkyyCoins, a throw, a non-Boolean) = refuse (Skyy 2026-10-14 "Block them").
F(coin, "public static final java.util.concurrent.atomic.AtomicLong SAME_REFUSED = new java.util.concurrent.atomic.AtomicLong();")
M(coin, r"""
public static boolean ownBlocked(String buyerKey, String sellerKey) {
  Object f = @PKG@.AhUtil.bridge().get("coins:fn:sameacct");
  if (!(f instanceof java.util.function.Function)) return true;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { buyerKey, sellerKey });
    if (r instanceof Boolean) return ((Boolean) r).booleanValue();
  } catch (Throwable t) { @PKG@.AhUtil.warn("coins:fn:sameacct threw (" + buyerKey + " / " + sellerKey + ") - the buy is refused: " + t); }
  return true;
}""")
M(coin, r"""
public static String sameText() {
  Object f = @PKG@.AhUtil.bridge().get("coins:fn:sameacct");
  if (!@PKG@.AhCfg.OTHER_PROFILE) return "blocked (otherProfileBuy=false)";
  if (!(f instanceof java.util.function.Function)) return "blocked by default (SkyyCoins 0.1.8+ coins:fn:sameacct not loaded yet - it is asked again at every buy)";
  return "asks SkyyCoins (Server Setup -> Coins -> Block coins between own profiles)";
}""")
M(coin, r"""
public static int take(java.util.UUID u, long n) {''')

# ---- A: the buy
rep('''  if (sUuid.equals(u.toString()) && !@PKG@.AhCfg.OTHER_PROFILE) return new @RES@(false, "Buying from your own account is switched off on this server (another of your profiles listed it).");
''', '''  if (sUuid.equals(u.toString()) && !@PKG@.AhCfg.OTHER_PROFILE) return new @RES@(false, "Buying from your own account is switched off on this server (another of your profiles listed it).");
  if (sUuid.equals(u.toString()) && @PKG@.Coins.ownBlocked(key, @PKG@.AhRec.subStr(r, "seller", "key", ""))) {   // 0.1.6 A
    @PKG@.Coins.SAME_REFUSED.incrementAndGet();
    return new @RES@(false, "You can't buy from your own other profile - coins never move between your own profiles on this server.");
  }
''')
# ---- B: the page
rep('''  } else if (note == null && sameAcc && !@PKG@.AhCfg.OTHER_PROFILE) {
    note = "Listed by your other profile " + @PKG@.AhRec.subStr(r, "seller", "profile", "") + " - buying from your own account is off on this server.";
''', '''  } else if (note == null && sameAcc && !@PKG@.AhCfg.OTHER_PROFILE) {
    note = "Listed by your other profile " + @PKG@.AhRec.subStr(r, "seller", "profile", "") + " - buying from your own account is off on this server.";
  } else if (note == null && sameAcc && @PKG@.Coins.ownBlocked(this.key, @PKG@.AhRec.subStr(r, "seller", "key", ""))) {   // 0.1.6 B
    note = "Listed by your other profile " + @PKG@.AhRec.subStr(r, "seller", "profile", "") + " - coins never move between your own profiles on this server.";
''')
# ---- D: the ready line + the config summary (/ahadmin status prints AhCfg.summary)
rep('''", other profiles " + (@PKG@.AhCfg.OTHER_PROFILE ? "may" : "may not") + " buy, coins bridge "''',
    '''", buys from your own other profile " + @PKG@.Coins.sameText() + ", coins bridge "''')
rep('''  sb.append(" | xFloorPrev ").append(X_FLOOR).append(" | otherProfileBuy ").append(OTHER_PROFILE).append(''',
    '''  sb.append(" | xFloorPrev ").append(X_FLOOR).append(" | otherProfileBuy ").append(OTHER_PROFILE).append(" (+ SkyyCoins' same-account switch)").append(''')

# ---- E: the otherProfileBuy note (fresh files + the 0.1.2 append; a comment only - existing files are not touched)
rep('''OTHER_NOTE = ("# otherProfileBuy = true: ANOTHER profile of the same account may buy a listing (the same profile never can). "
              "false = no buying from your own account at all.")''',
    '''OTHER_NOTE = ("# otherProfileBuy = true: SkyyCoins' switch decides if ANOTHER profile of the same account may buy a listing "
              "(Server Setup -> Coins -> Block coins between own profiles; ON by default = refused). The same profile never can. "
              "false = no buying from your own account at all, whatever SkyyCoins says.")''')

# ---- checks
assert s.index("public static boolean ownBlocked(") < s.index("@PKG@.Coins.ownBlocked(key,") and s.index("public static boolean ownBlocked(") < s.index("@PKG@.Coins.ownBlocked(this.key,")
assert s.index("@PKG@.Coins.ownBlocked(key,") < s.index("long bal = @PKG@.Coins.get(u);\n  if (bal < 0L) return new @RES@(false, \"The coin bank did not answer - nothing bought.")
_u = s[s.index("\n", s.index("Notes in tools/auctions_0_1_6_patch.py.")) + 1:]
_u = '"""' + _u
for _o, _n in reversed(OLDS):
    assert _u.count(_n) == 1
    _u = _u.replace(_n, _o, 1)
assert _u == S0, "0.1.5 changed outside the planned places"
if os.path.exists(dst):
    os.remove(dst)
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d changes)" % len(OLDS))
