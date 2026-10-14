"""Derive SkyyCollections/build_skyycollections_0.2.12.py from the LIVE generated 0.2.11 (build_skyycollections_0.2.11.py, the
tools/deploy_set.py SET pin; 0.2.11 stays untouched, its line endings are kept). Edit this patch, never the generated file.
Run:  python tools/collections_0_2_12_patch.py   then   python SkyyCollections/build_skyycollections_0.2.12.py   (never --deploy)
Test: python SkyyCollections/test_skyycollections_0.2.12.py [--dir <scratch>] [--keep]

0.2.12 (2026-10-13) = CHAT OVERFLOW -> FEED + COLLECTION LEVEL-UP RECIPES (docs/answered/ui.md 2026-10-12, Skyy word for word:
  "watch for things i probably wont notice, and figure out ways to reduce the chat overflow while still giving players the info they need.
  the chat has top move slow enough people can read it for server use. (unless we set up a second notification system that uses our
  widgets or something.)" and "if you can, on collection level up do like skyblock does, and tell you what crafting recopies you unlocked
  with that level up, and allow users to click it in chat to pull it up in the menu.")
  1. ONE RANK-UP LINE: "COLLECTION UP  Wheat III" + its reward lines + "N new recipe(s) in /craft" (3-5 chat lines a tier in 0.2.11) is
     now ONE line: "COLLECTION UP  Wheat III  New: Bread, Hay Bale  +500 coins, +200 Farming XP  /craft bread". Each recipe name is in its
     output item's RARITY colour (ItemQuality text colour; Mythic's #AA00AA -> the readable #CC66CC like SkyyAuctions; an unknown item =
     0.2.11's recipe green). The line ends with a short command that opens that recipe: "/craft <words>" = SkyySacks' craft page searching
     for it - the exact query 0.2.8's CRAFT button runs (CollMsg.craftQ = CollCraft.query's rule: the words a tier's recipes share, else
     the first's; the harness proves them equal on every tier). No /craft on the server -> "/collections <name>" (the collection page).
     DECISION: no new "/recipe" command - Hytale's own /recipe (learn / forget / list, WorldEditor group) owns that name; /craft is the
     command 0.2.8's button already uses. CLICK: the 0.7 chat Message only carries URL links (no click-to-run) - not faked.
  2. ROUTES (tools/skyyroute.py MsgRoute; SkyyHud 0.3.20+ msgroute:fn:get, cached 2 s per player + kind):
     "rankup" (server default Chat): chat = the line above; feed = a card (kind rankup, the collection icon, "Wheat III - 2 new recipes");
     off = nothing; no SkyyHud / an old SkyyHud / a refused card = the chat line.
     "collection" (server default Feed): NEW - a counted gather pushes a card (kind collection, the gathered item's icon, "Pumpkin
     340 / 500" with the amount as the count, so SkyyHud merges "Pumpkin x9"). 0.2.11 never had a progress chat line, so chat / off /
     a refused card = nothing. A gather that ranks up shows the rank-up instead. REVIEW FIX: SkyyHud sends a card pushed out of its
     4-card stack before it was drawn as a CHAT line, so MsgRoute.gate lets a NEW item's card through at most once a second per player
     and any progress card at most once per 300 ms; a skipped amount waits (CollMsg.PEND) and joins that item's next card.
     The rank-up card names the first recipe: "Wheat III - Bread, +1".
  3. NEW RECIPES: a tier reached by gathering whose rewards hold a recipe is marked NEW (per profile: the counts file's meta key
     "_new.<collection id>" = a bit per tier; tiers already bought with coins are not marked). The collection page shows "NEW" in that
     tier row's state cell (instead of DONE) and the Unlocked recipes list puts "NEW" before those recipe names, until the player opens
     that collection's page (the markers are cleared after that page is drawn - it shows them once). The marker rides the existing
     per-profile counts save (dirty flag, the 10 s writer, tmp + fsync + atomic move).
  Chat KEEPS: "New collection: X!", the late-reward note, /collections replies (one line each). Rollback to 0.2.11 is safe: it reads the
  "_new.*" lines as unknown meta numbers and writes them back unchanged (never used); rank-ups go back to 3-5 lines.
Saved data: only the "_new.<id>" meta lines in counts/<profile key>.properties (PROFILES-CONTRACT: per profile, follows the profile key).
Classes: NEW MsgRoute (tools/skyyroute.py), CollMsg (the rank-up line / card / progress card + its PEND amounts, rarity colour, craft query), CollNew (the
markers); changed CollCredit (announce, creditOne), CollPage (buildDetail, unlockedRows); version texts.
"""
import os, sys, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyCollections")
src = os.path.join(HERE, "build_skyycollections_0.2.11.py")
dst = os.path.join(HERE, "build_skyycollections_0.2.12.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.11"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
assert 'VERSION = "0.2.11"' in s and "GENERATED by tools/collections_0_2_11_patch.py from the LIVE 0.2.10" in s, "not the live generated 0.2.11"
assert "MsgRoute" not in s and "_new." not in s
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.2.12 (2026-10-13)"):HEAD.index("Saved data: only")].rstrip()

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyCollections 0.2.11 - build script (javassist via jpype). GENERATED by tools/collections_0_2_11_patch.py from the LIVE 0.2.10
(build_skyycollections_0.2.10.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.10 was derived from 0.2.9 by
''', '''"""SkyyCollections 0.2.12 - build script (javassist via jpype). GENERATED by tools/collections_0_2_12_patch.py from the LIVE 0.2.11
(build_skyycollections_0.2.11.py, the tools/deploy_set.py SET pin) - edit the patch, never this file. 0.2.11 was derived from 0.2.10 by
tools/collections_0_2_11_patch.py; 0.2.10 was derived from 0.2.9 by
''')
rep('''0.2.11 (2026-10-13): ENCHANTED MATERIALS''', NOTE.replace(LF, LF + "  ") + '''
  Full notes: tools/collections_0_2_12_patch.py. CHECKED with SkyyCollections/test_skyycollections_0.2.12.py.
0.2.11 (2026-10-13): ENCHANTED MATERIALS''')
rep('VERSION = "0.2.11"\n', 'VERSION = "0.2.12"\n')
rep('''import skyywbtab as WB      # 0.2.11: only its engine probe (the Compressing tab relies on the same CraftingBench facts)
''', '''import skyywbtab as WB      # 0.2.11: only its engine probe (the Compressing tab relies on the same CraftingBench facts)
import skyyroute as RT      # 0.2.12: the shared message route (MsgRoute class source; also SkyySkills 0.4.34, SkyyClasses 0.1.20)
''')
rep('''    "PKG":  "com.skyy.collections",
}''', '''    "IQ":   "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality",                # 0.2.12: a recipe's rarity colour
    "PCOL": "com.hypixel.hytale.protocol.Color",
    "PKG":  "com.skyy.collections",
}''')
rep('''for c, m in ((T["PLA"], "getPlayerConfigData"), (T["PCD"], "getKnownRecipes"),''', '''for c, m in ((T["ITM"], "getQualityIndex"), (T["IQ"], "getAssetMap"), (T["IQ"], "getTextColor"), (T["MSG"], "insert")):   # 0.2.12
    B.probe(pool, c, m)
for c, m in ((T["PLA"], "getPlayerConfigData"), (T["PCD"], "getKnownRecipes"),''')
rep('''ALL = ALL + (ench, ktsk) + tuple(ETAB)   # 0.2.11
''', '''ALL = ALL + (ench, ktsk) + tuple(ETAB)   # 0.2.11
mrt = K("MsgRoute")         # 0.2.12: chat / feed / off per message kind (tools/skyyroute.py)
cmsg = K("CollMsg")         # 0.2.12: the one-line rank-up (rarity colours, /craft words), the rank-up / progress feed cards
cnew = K("CollNew")         # 0.2.12: the NEW recipe markers (per profile, the counts file's "_new.<id>" meta lines)
ALL = ALL + (mrt, cmsg, cnew)   # 0.2.12
''')

# ---------------------------------------------------------------------------------------------------------------- MsgRoute, CollMsg, CollNew
# compiled right before CollCredit (their caller); everything they call (CollUtil, CollReg, CollStore) is compiled above
MSG_JAVA = r'''
RT.add_msg_route(mrt, CtField, CtNewMethod, PKG + ".CollUtil.bridge()")
# ================= 0.2.12 CollNew: NEW recipe markers - meta "_new.<collection id>" = one bit per tier (1 << t, t 1..62) =================
M(cnew, r"""
public static String mkey(@PKG@.RegData R, int c) {
  return "_new." + R.id[c];
}""")
M(cnew, r"""
public static boolean isNew(@PKG@.CollData d, @PKG@.RegData R, int c, int t) {
  if (d == null || R == null || c < 0 || c >= R.n || t < 1 || t > 62) return false;
  return (@PKG@.CollStore.meta(d, mkey(R, c)) & (1L << t)) != 0L;
}""")
# the tiers from..to reached by gathering whose rewards hold a recipe (a tier already bought with coins was unlocked then - not new)
M(cnew, r"""
public static long mark(@PKG@.CollData d, String key, @PKG@.RegData R, int c, int from, int to) {
  if (d == null || key == null || R == null || c < 0 || c >= R.n) return 0L;
  int bt = @PKG@.CollStore.boughtTier(d, R, c);
  long m0 = @PKG@.CollStore.meta(d, mkey(R, c));
  long m = m0;
  for (int t = from < 1 ? 1 : from; t <= to && t <= 62; t++) {
    if (t <= bt || @PKG@.CollReg.recipesAt(c, t).length == 0) continue;
    m = m | (1L << t);
  }
  if (m != m0) @PKG@.CollStore.setMeta(d, key, mkey(R, c), m);
  return m;
}""")
M(cnew, r"""
public static boolean seen(@PKG@.CollData d, String key, @PKG@.RegData R, int c) {
  if (d == null || key == null || R == null || c < 0 || c >= R.n) return false;
  if (@PKG@.CollStore.meta(d, mkey(R, c)) == 0L) return false;
  @PKG@.CollStore.setMeta(d, key, mkey(R, c), 0L);
  return true;
}""")

# ================= 0.2.12 CollMsg: the one-line rank-up, the rank-up card, the progress card =================
M(cmsg, r"""
public static String outId(String rid) {
  if (rid == null) return null;
  int g = rid.indexOf("_Recipe_Generated_");
  return g > 0 ? rid.substring(0, g) : rid;
}""")
M(cmsg, r"""
public static String hex(@PCOL@ c) {
  if (c == null) return null;
  return "#" + Integer.toHexString(256 | (c.red & 255)).substring(1) + Integer.toHexString(256 | (c.green & 255)).substring(1)
    + Integer.toHexString(256 | (c.blue & 255)).substring(1);
}""")
# the recipe output item's rarity text colour (ItemQuality); Mythic #AA00AA -> #CC66CC (readable - SkyyAuctions / SkyySacks); else 0.2.11's
# recipe green
M(cmsg, r"""
public static String rarityHex(String rid) {
  try {
    Object it = @ITM@.getAssetMap().getAsset(outId(rid));
    if (it instanceof @ITM@) {
      Object q = @IQ@.getAssetMap().getAsset(((@ITM@) it).getQualityIndex());
      if (q instanceof @IQ@) {
        String h = hex(((@IQ@) q).getTextColor());
        if (h != null) return h.equalsIgnoreCase("#AA00AA") ? "#CC66CC" : h;
      }
    }
  } catch (Throwable t) { }
  return "#c8f0a0";
}""")
# CollCraft.words / query, the same rule (CollCraft is compiled after CollCredit - javassist needs callees first; the harness proves
# craftQ(rs) == CollCraft.query(rs, all of rs) on every tier of the registry)
M(cmsg, r"""
public static java.util.ArrayList words(String rid) {
  java.util.ArrayList out = new java.util.ArrayList();
  String id = outId(rid);
  if (id == null) return out;
  id = id.trim();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i <= id.length(); i++) {
    char ch = i < id.length() ? id.charAt(i) : ' ';
    if (ch < 128 && Character.isLetterOrDigit(ch)) { sb.append(Character.toLowerCase(ch)); continue; }
    if (sb.length() > 0) { String w = sb.toString(); if (!out.contains(w)) out.add(w); sb.setLength(0); }
  }
  return out;
}""")
M(cmsg, r"""
public static String craftQ(String[] rs) {
  if (rs == null) return null;
  java.util.ArrayList first = null;
  java.util.ArrayList common = null;
  int n = 0;
  for (int i = 0; i < rs.length; i++) {
    if (rs[i] == null) continue;
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
M(cmsg, r"""
public static boolean craftOn() {
  try { return @CMGR@.get().resolveCommand("craft") != null; } catch (Throwable t) { return false; }
}""")
M(cmsg, r"""
public static void part(java.util.ArrayList out, String text, String col) {
  if (text != null && text.length() > 0) out.add(new String[] { text, col });
}""")
# the rank-up line as { text, colour } parts: header (gold), "New:" + each recipe in its rarity colour, the coins / skill XP, the command
M(cmsg, r"""
public static java.util.ArrayList rankParts(@PKG@.RegData R, int c, int t, boolean craft) {
  java.util.ArrayList out = new java.util.ArrayList();
  part(out, "COLLECTION UP  " + R.name[c] + " " + @PKG@.CollUtil.roman(t), "#ffc800");
  String[] rs = @PKG@.CollReg.recipesAt(c, t);
  int n = 0;
  for (int i = 0; i < rs.length; i++) {
    if (rs[i] == null) continue;
    part(out, n == 0 ? "  New: " : ", ", "#e8d8a0");
    part(out, @PKG@.CollUtil.prettyRecipe(rs[i]) + (@PKG@.CollUtil.isBag(rs[i]) && @PKG@.CollUtil.freeBags() ? " (free)" : ""), rarityHex(rs[i]));
    n++;
  }
  StringBuilder rw = new StringBuilder();
  long co = @PKG@.CollReg.coinsAt(R, c, t);
  if (co > 0L) rw.append("+").append(@PKG@.CollUtil.fmt(co)).append(" coins");
  java.util.ArrayList xs = @PKG@.CollReg.xpAt(R, c, t);
  for (int i = 0; i < xs.size(); i++) {
    Object[] a = (Object[]) xs.get(i);
    if (rw.length() > 0) rw.append(", ");
    rw.append("+").append(@PKG@.CollUtil.fmt(((Long) a[1]).longValue())).append(" ").append((String) a[0]).append(" XP");
  }
  if (rw.length() > 0) part(out, "  " + rw.toString(), "#e8d8a0");
  if (n > 0) {
    String q = craft ? craftQ(rs) : null;
    part(out, q != null ? "  /craft " + q : "  /collections " + R.name[c].replace(" ", "").toLowerCase(), "#7fdcff");
  }
  return out;
}""")
M(cmsg, r"""
public static String text(java.util.ArrayList parts) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < parts.size(); i++) sb.append(((String[]) parts.get(i))[0]);
  return sb.toString();
}""")
M(cmsg, r"""
public static @MSG@ message(java.util.ArrayList parts) {
  String[] p0 = (String[]) parts.get(0);
  @MSG@ m = @MSG@.raw(p0[0]).color(p0[1]);
  for (int i = 1; i < parts.size(); i++) {
    String[] p = (String[]) parts.get(i);
    m.insert(@MSG@.raw(p[0]).color(p[1]));
  }
  return m;
}""")
# REVIEW FIX (2026-10-13): the card NAMES the first new recipe ("Wheat III - Bread, +1") - Skyy: "tell you what crafting recopies you
# unlocked" (the 0.2.12 first cut only said "2 new recipes")
M(cmsg, r"""
public static String cardText(@PKG@.RegData R, int c, int t) {
  String[] rs = @PKG@.CollReg.recipesAt(c, t);
  String first = null;
  int n = 0;
  for (int i = 0; i < rs.length; i++) {
    if (rs[i] == null) continue;
    if (first == null) first = @PKG@.CollUtil.prettyRecipe(rs[i]);
    n++;
  }
  String h = R.name[c] + " " + @PKG@.CollUtil.roman(t);
  if (n == 0) return h;
  return h + " - " + @PKG@.CollUtil.clip(first, 28) + (n > 1 ? ", +" + (n - 1) : "");
}""")
M(cmsg, r"""
public static String icon(@PKG@.RegData R, int c) {
  return R.iconOk != null && c >= 0 && c < R.iconOk.length && R.iconOk[c] ? R.icon[c] : null;
}""")
# "Pumpkin 340 / 500" (or "... (max)") with the gathered amount as the count; only when the player's route is feed - 0.2.11 never had a
# progress chat line, so chat / off / a refused card = nothing
M(cmsg, r"""
public static String progText(@PKG@.RegData R, int c, long sum, int tier) {
  int mx = @PKG@.CollReg.maxTier(R, c);
  return R.name[c] + " " + @PKG@.CollUtil.fmt(sum) + (tier >= mx ? " (max)" : " / " + @PKG@.CollUtil.fmt(@PKG@.CollReg.threshold(R, c, tier + 1)));
}""")
# REVIEW FIX (2026-10-13): SkyyHud turns a card pushed out of its 4-card stack before it was drawn into a CHAT line, and a sickle over 5
# crops / a felled tree pushes many different items at once - so a NEW item's card at most once a second per player, any progress card at
# most once per 300 ms (SkyyHud draws every 250 ms: at most one undrawn progress card at a time); a skipped amount waits in PEND
# ("<uuid>|<item>", bounded 4096) and joins that item's next card, so the "x9" count stays right
cmsg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();", cmsg))
M(cmsg, r"""
public static void addPend(String k, long q) {
  Object o = PEND.get(k);
  if (o instanceof long[]) { long[] a = (long[]) o; a[0] = a[0] + q; return; }
  if (PEND.size() > 4096) PEND.clear();
  PEND.put(k, new long[] { q });
}""")
M(cmsg, r"""
public static long takePend(String k) {
  Object o = PEND.remove(k);
  return o instanceof long[] ? ((long[]) o)[0] : 0L;
}""")
M(cmsg, r"""
public static boolean progress(java.util.UUID u, @PKG@.RegData R, int c, String item, long q, long sum, int tier) {
  try {
    if (u == null || R == null || q <= 0L || c < 0 || c >= R.n) return false;
    if (!"feed".equals(@PKG@.MsgRoute.route(u, "collection"))) return false;
    String pk = u.toString() + "|" + item;
    if (!@PKG@.MsgRoute.gate(u, "collection", item, 1000L, 300L)) { addPend(pk, q); return false; }
    return @PKG@.MsgRoute.feed(u, "collection", item, progText(R, c, sum, tier), q + takePend(pk));
  } catch (Throwable t) { return false; }
}""")
'''
rep('''# ================= CollCredit: the one path every counted item takes =================
''', '''# ================= 0.2.12 MsgRoute (tools/skyyroute.py; SkyyHud 0.3.20+ bridge API) =================''' + MSG_JAVA + '''
# ================= CollCredit: the one path every counted item takes =================
''')

# ---------------------------------------------------------------------------------------------------------------- CollCredit
rep('''M(cred, r"""
public static void announce(@PR@ pr, @PKG@.RegData R, int c, int from, int to) {
  for (int t = from; t <= to; t++) {
    pr.sendMessage(@MSG@.raw("COLLECTION UP  " + R.name[c] + " " + @PKG@.CollUtil.roman(t)).color("#ffc800"));
    java.util.ArrayList ls = @PKG@.CollReg.rewardLines(R, c, t);
    for (int i = 0; i < ls.size(); i++) pr.sendMessage(@MSG@.raw("   " + (String) ls.get(i)).color(((String) ls.get(i)).indexOf(" recipe") >= 0 ? "#c8f0a0" : "#e8d8a0"));
  }
}""")''', '''# 0.2.12: ONE line per tier (CollMsg.rankParts) - route "rankup": off = nothing, feed = a card (a refused card = the line)
M(cred, r"""
public static void announce(@PR@ pr, @PKG@.RegData R, int c, int from, int to) {
  java.util.UUID u = pr.getUuid();
  String r = @PKG@.MsgRoute.route(u, "rankup");
  if ("off".equals(r)) { @PKG@.MsgRoute.off(); return; }
  boolean craft = @PKG@.CollMsg.craftOn();
  for (int t = from; t <= to; t++) {
    if ("feed".equals(r) && @PKG@.MsgRoute.feed(u, "rankup", @PKG@.CollMsg.icon(R, c), @PKG@.CollMsg.cardText(R, c, t), 0L)) continue;
    java.util.ArrayList ps = @PKG@.CollMsg.rankParts(R, c, t, craft);
    @PKG@.MsgRoute.said(@PKG@.CollMsg.text(ps));
    pr.sendMessage(@PKG@.CollMsg.message(ps));
  }
}""")''')
rep('''    if (on && r[0] <= 0L && r[1] > 0L && @PKG@.CollUtil.notifyOn(u, "coll.newCollection")) pr.sendMessage(@MSG@.raw("New collection: " + R.name[c] + "!   /collections").color("#7fdcff"));
    if (nt <= ot) return;''', '''    if (on && r[0] <= 0L && r[1] > 0L && @PKG@.CollUtil.notifyOn(u, "coll.newCollection")) pr.sendMessage(@MSG@.raw("New collection: " + R.name[c] + "!   /collections").color("#7fdcff"));
    if (nt <= ot) { if (on) @PKG@.CollMsg.progress(u, R, c, item, q, r[1], nt); return; }   // 0.2.12: the progress card (feed route only)''')
rep('''    long[] paid = @PKG@.CollRewards.settle(d, R, c, u, key);
    int now = @PKG@.CollUnlocks.publish(u);
    if (!on) return;
    boolean tierOn = @PKG@.CollUtil.notifyOn(u, "coll.tierUp");
    if (tierOn) announce(pr, R, c, ot + 1, nt);
    if (tierOn && now > before) pr.sendMessage(@MSG@.raw("   " + (now - before) + " new recipe(s) in /craft - Collections tab").color("#c8f0a0"));''',
    '''    long[] paid = @PKG@.CollRewards.settle(d, R, c, u, key);
    int now = @PKG@.CollUnlocks.publish(u);
    @PKG@.CollNew.mark(d, key, R, c, ot + 1, nt);   // 0.2.12: NEW on the collection page until it is opened
    if (!on) return;
    boolean tierOn = @PKG@.CollUtil.notifyOn(u, "coll.tierUp");
    if (tierOn) announce(pr, R, c, ot + 1, nt);     // 0.2.12: the recipes are on the rank-up line (0.2.11's "N new recipe(s)" line folded in)''')

# ---------------------------------------------------------------------------------------------------------------- CollPage: NEW
rep('''    b.set("#SkyyCTr" + t + "S.Text", st);''', '''    b.set("#SkyyCTr" + t + "S.Text", t <= ct && @PKG@.CollNew.isNew(d, R, c, t) ? "NEW" : st);   // 0.2.12''')
rep('''    b.set("#SkyyCRew" + t + ".Text", cq != null ? @PKG@.CollCraft.fitPx(rtx, CRAFTREW) : rtx);   // 0.2.8: a CRAFT row's cell is 84 px shorter
  }
''', '''    b.set("#SkyyCRew" + t + ".Text", cq != null ? @PKG@.CollCraft.fitPx(rtx, CRAFTREW) : rtx);   // 0.2.8: a CRAFT row's cell is 84 px shorter
  }
  @PKG@.CollNew.seen(d, @PKG@.CollUtil.pkey(this.playerRef.getUuid()), R, c);   // 0.2.12: shown once - the markers are cleared
''')
rep('''        out.add(new Object[] { rs[i], @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rs[i]), 44), R.name[c] + " tier "''',
    '''        out.add(new Object[] { rs[i], t <= ct && @PKG@.CollNew.isNew(d, R, c, t) ? "NEW  " + @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rs[i]), 39) : @PKG@.CollUtil.clip(@PKG@.CollUtil.prettyRecipe(rs[i]), 44), R.name[c] + " tier "''')

# ---------------------------------------------------------------------------------------------------------------- the checked page id
# the NEW state cell + the NEW list prefix change the page source -> a new page id; SkyyCollections/test_skyycollections_0.2.12.py EXECUTES
# buildDetail / unlockedRows on it (R) and checks this id against the jar's ready line
rep('''COLL_PAGE_CHECKED = "e3b045f3048d"   # 0.2.8 page, unchanged in 0.2.9 / 0.2.10 / 0.2.11: SkyyCollections/test_skyycollections_0.2.11.py checks it''',
    '''COLL_PAGE_CHECKED = "d02487bb8475"   # 0.2.12 page (the NEW tier cell + list prefix): SkyyCollections/test_skyycollections_0.2.12.py checks it''')
for _o in ("SkyyCollections/test_skyycollections_0.2.11.py last passed on", "in tools/collections_0_2_11_patch.py and regenerate"):
    rep(_o, _o.replace("0.2.11", "0.2.12").replace("0_2_11", "0_2_12"), s.count(_o))
# the ready line names the version as text (smoke_test.py needs "[SkyyCollections] 0.2.12 ready")
rep('''log("[SkyyCollections] 0.2.11 ready (""" + KIT_ID''', '''log("[SkyyCollections] 0.2.12 ready (""" + KIT_ID''')

# ---------------------------------------------------------------------------------------------------------------- manifest text
rep('''Tiers pay coins (SkyyCoins), gathering skill XP (SkyySkills) and recipe unlocks for the SkyySacks craft page,''',
    '''Tiers pay coins (SkyyCoins), gathering skill XP (SkyySkills) and recipe unlocks for the SkyySacks craft page (a rank-up is one chat line naming the new recipes in their rarity colour + the /craft words to open them; the recipes show NEW on the collection page; progress and rank-ups can go to the SkyyHud notification feed),''')

# ---------------------------------------------------------------------------------------------------------------- checks
assert s.index("cnew = K(\"CollNew\")") < s.index("ALL = ALL + (mrt, cmsg, cnew)")
assert s.index("public static boolean progress(java.util.UUID u") < s.index("public static void announce(@PR@ pr") < s.index("public static void creditOne(")
assert s.count("@PKG@.CollNew.isNew(") == 2 and s.count("@PKG@.CollNew.mark(") == 1 and s.count("@PKG@.CollNew.seen(") == 1
_a, _b = OLD.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.2.11 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, "(%d lines; 0.2.11 had %d; %d anchors, %d hunks)" % (s.count(LF), OLD.count(LF), len(OLDS), len(_hunks)))
