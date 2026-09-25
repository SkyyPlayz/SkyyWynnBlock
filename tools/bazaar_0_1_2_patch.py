"""Derive SkyyBazaar/build_skyybazaar_0.1.2.py from the LIVE 0.1.1 (0.1.1 stays untouched).
0.1.2 (Skyy's beta backlog item 8, 2026-09-24): a custom-amount TextField with Buy / Sell buttons under the product's Buy/Sell buttons,
and the whole /bazaar page about 1.4x bigger. Prices, spread, demand factor, decay, files, log and bridge are the 0.1.1 logic.
Run:  python tools/bazaar_0_1_2_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.2.py   (never --deploy without Skyy's OK)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.1.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.2.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


# ---------------- docstring ----------------
rep('"""SkyyBazaar 0.1.1 - build script (javassist via jpype).', '"""SkyyBazaar 0.1.2 - build script (javassist via jpype).')
rep('''Run:   python build_skyybazaar_0.1.1.py            -> SkyyBazaar/SkyyBazaar-0.1.1.jar   (build only; --deploy only with Skyy's OK)
       python build_skyybazaar_0.1.1.py --deploy   -> also copies to Mods/SkyyBazaar.jar and enables it in the HUD mod world
       (0.1.1 is generated from build_skyybazaar_0.1.py by tools/bazaar_0_1_1_patch.py; 0.1 is kept as it was)
''', '''Run:   python build_skyybazaar_0.1.2.py            -> SkyyBazaar/SkyyBazaar-0.1.2.jar   (build only; --deploy only with Skyy's OK)
       python build_skyybazaar_0.1.2.py --deploy   -> also copies to Mods/SkyyBazaar.jar and enables it in the HUD mod world
       (0.1.2 is generated from build_skyybazaar_0.1.1.py by tools/bazaar_0_1_2_patch.py; 0.1.1 is generated from 0.1 by
       tools/bazaar_0_1_1_patch.py; both older scripts are kept as they were)

0.1.2 (2026-09-24, Skyy's beta backlog item 8) - custom amounts + a bigger page. Pricing (quote / unit / step / spread), the demand
factor, decay, anti-dupe trade core (buy0 / sell0 / sellInventory), files, trades.log, the bridge keys and /bazaaradmin are the
0.1.1 logic unchanged.
 - Custom amount row under the product's Buy / Sell buttons: "Custom amount" [TextField #SkyyBzAmt] [Buy] [Sell] + a hint, and a
   limits line under it ("You can buy up to N (your purse | inventory room | the per-trade limit) and sell up to H").
   TextField pattern copied from SkyyGuilds 0.1 (Amount field, in game on the beta test) / SkyySacks 0.7.3 (search, verified in game):
   Enter = Validating binding, the buttons = Activating bindings, every binding carries EventData .append("@BzAmount",
   "#SkyyBzAmt.Value") and the value is read back with jsonStr (SkyySacks CraftPage.jsonStr); the rebuild puts the last submitted
   text back with set("#SkyyBzAmt.Value"). While the field is on the page (a product is selected) the tab / product / 1 / 64 /
   Sell all / Sell inventory bindings carry the field value too, so typed text survives picking another product.
   Amounts: a whole number (500), k / m suffixes (2k, 1.5k, 1m), commas and spaces ignored, max / all = the limit of that side.
 - Validation (inside the Market lock at trade time, again in the page for the messages): Buy 1 .. min(what the purse affords
   (one walk with quote()'s exact arithmetic, stopping at the first unit the purse cannot cover), inventory room (empty slots x the item's max stack +
   the free part of partial stacks, storage + hotbar + backpack like Inv.give), 100000 per trade). Sell 1 .. what you hold
   (storage + hotbar + backpack). A refused amount says why and moves nothing.
 - The total price is always shown before a custom trade: Enter prices BOTH sides ("500 Copper Ore - buy for X coins - sell for Y
   coins") and arms them for 15 s; a Buy / Sell click that was not priced first only shows the price and arms that side for 10 s
   ("click Buy again within 10 s to confirm"). The trade then runs with the price the player saw as a cap: a buy that now costs
   MORE, or a sell that now pays LESS (someone else traded in between), is refused and re-armed at the new price. A sell that
   is now worth 0 coins is refused outright (like sell0). max / all is worked out again on every click; when the armed max
   changed the page says "your max changed from A to B" and asks for one more click at the new amount and price.
   Any other click disarms (like the Sell inventory confirm).
 - Page actions are matched exactly with jsonStr(data, "a") (SkyyGuilds pattern) instead of 0.1.1's has(data, key) substring test,
   so text typed into the amount field can never be read as another button's payload.
 - profile:busy:<uuid> (tools/PROFILES-CONTRACT.md rule 5, crash recovery at join): buy0 and sell0 refuse to move items while it is
   present ("your profile is still loading"), so no path (buttons, custom amount, Sell inventory) can dupe against the recovery.
   The page says so too: the limits line reads "trading is paused", and neither the custom amount nor Sell inventory shows a
   price or a Confirm prompt while it is set.
 - The 6-tab / 27-product caps are 0.1.1's (more rows or tabs need a client check first); anything past them is named in the
   line under the tabs ("N more products in this tab ... do not fit the page - tell an admin") instead of vanishing silently.
 - Page about 1.4x: root 1080 wide (was 760), 640 high with one grid row (+94 per extra row, 828 with the maximum 3 rows - fits a
   1080-high screen like the verified 830-930 pages); every font, button, cell (87 px, was 62), icon and row scaled ~1.4x; the grid
   is centred. The root height follows the grid rows (0.1.1 kept 560 even with 1 row) and does not change when a product is selected
   (the empty detail box takes the height of the detail + trade rows).
 - Offline checks only (session harness in tools/dev/scratch, deleted afterwards): -Xverify:all load of every class, parseAmt /
   jsonStr / maxBuyable / buyWhy / sellWhy cases, render() markup (balanced braces / parentheses / quotes, no underscore ids,
   root anchor only Width + Height, heights) and the amount click flow with fake SkyyCoins bridge functions. The page itself on a
   real client is UNVERIFIED until Skyy opens it.
''')

# ---------------- version + API probes ----------------
rep('VERSION = "0.1.1"' + LF, 'VERSION = "0.1.2"' + LF)
rep('''    B.probe(pool, c, m)

PKG = "com.skyy.bazaar"''', '''    B.probe(pool, c, m)
# 0.1.2: amount TextField (Validating + "@BzAmount" event data), set() for the field value / labels, max stack for inventory room
for c, m in ((BT, "Validating"), (EVD, "append"), (UCB, "set"), (ITM, "getMaxStack"), (DAM, "getAsset")):
    B.probe(pool, c, m)

PKG = "com.skyy.bazaar"''')

# ---------------- BzUtil: jsonStr + parseAmt ----------------
rep('''utl.addMethod(CtNewMethod.make("""
public static boolean has(String data, String key) {
  return data != null && data.indexOf("\\\\"" + key + "\\\\"") >= 0;
}""", utl))
''', '''utl.addMethod(CtNewMethod.make("""
public static boolean has(String data, String key) {
  return data != null && data.indexOf("\\\\"" + key + "\\\\"") >= 0;
}""", utl))
# 0.1.2: one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr, verified in game with the search TextField;
# the same copy runs the SkyyGuilds 0.1 page). quote = char 34, backslash = char 92, so no escape sequences are needed here.
utl.addMethod(CtNewMethod.make("""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""", utl))
# 0.1.2: custom amount text -> units. -1 = empty or not an amount, -2 = max / all, else the whole number (0 allowed, callers range-check).
# 500, 2k, 1.5k, 1m; commas, spaces and underscores are ignored; a fraction without a suffix (1.5) is refused.
utl.addMethod(CtNewMethod.make("""
public static long parseAmt(String raw) {
  if (raw == null) return -1L;
  String t = raw.trim().toLowerCase();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (c != ' ' && c != ',' && c != '_') sb.append(c);
  }
  String s = sb.toString();
  if (s.length() == 0) return -1L;
  if (s.equals("max") || s.equals("all")) return -2L;
  double mul = 1.0;
  char last = s.charAt(s.length() - 1);
  if (last == 'k') { mul = 1000.0; s = s.substring(0, s.length() - 1); }
  else if (last == 'm') { mul = 1000000.0; s = s.substring(0, s.length() - 1); }
  if (s.length() == 0 || s.length() > 12) return -1L;
  int dots = 0;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == '.') { dots++; continue; }
    if (c < '0' || c > '9') return -1L;
  }
  if (dots > 1 || s.equals(".")) return -1L;
  double v;
  try { v = Double.parseDouble(s) * mul; } catch (Throwable x) { return -1L; }
  if (!(v >= 0.0) || v > 1.0E12) return -1L;
  double r = Math.floor(v + 1.0E-9);
  if (Math.abs(v - r) > 1.0E-6) return -1L;
  return (long) r;
}""", utl))
''')

# ---------------- Market.maxBuyable (reads quote() only - pricing unchanged) ----------------
rep('''mkt.addMethod(CtNewMethod.make(f"""
public static synchronized double unit(String id, boolean buy) {{''', '''# 0.1.2: the most units a purse can pay for right now (cap = room / per-trade limit). Display + validation only - quote() is untouched.
# ONE walk with quote()'s exact arithmetic (same factor, step, spread, the same additions in the same order, the same rounding and
# 1e15 limit), so the running total after k units is bit-identical to quote(id, k, true); the total only ever rises (every unit adds
# base * factor * (1 + spread) > 0), so the first unit the purse cannot cover ends the walk. Work = min(answer + 1, cap) steps on the
# world thread (a binary search over quote() was about 2-3x cap per render, up to ~300k steps at the 100000 per-trade limit).
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized int maxBuyable(String id, long purse, int cap) {{
  {PKG}.Product p = {PKG}.Catalog.get(id);
  if (p == null || purse <= 0L || cap <= 0) return 0;
  if (cap > 1000000) cap = 1000000;
  double f = factor(id);
  double st = step(p);
  double mult = 1.0 + SPREAD;
  double total = 0.0;
  int best = 0;
  for (int i = 0; i < cap; i++) {{
    total += p.base * f * mult;
    f = clampF(f * st);
    if (!(total >= 0.0) || total > 1.0E15) break;
    long c = (long) Math.ceil(total - 1.0E-7);
    if (c > purse) break;
    best = i + 1;
  }}
  return best;
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized double unit(String id, boolean buy) {{''')

# ---------------- TradeResult: price-moved flag ----------------
rep('''res.addField(CtField.make("public boolean alert;", res))
''', '''res.addField(CtField.make("public boolean alert;", res))
# 0.1.2: moved = a custom trade was refused because the price changed since the player saw it; price = the new total (re-armed)
res.addField(CtField.make("public boolean moved;", res))
res.addField(CtField.make("public long price;", res))
''')

# ---------------- Trader: profile:busy, inventory room, custom-amount trades ----------------
rep('''trd.addField(CtField.make("public static final int MAXQ = 100000;", trd))
''', '''trd.addField(CtField.make("public static final int MAXQ = 100000;", trd))
# 0.1.2: SkyyProfiles crash recovery (tools/PROFILES-CONTRACT.md rule 5) - while profile:busy:<uuid> is present the live inventory may
# be replaced by a snapshot a moment later, so no trade may move items (a sale would pay coins AND get the items back).
trd.addMethod(CtNewMethod.make(f"""
public static boolean busy(java.util.UUID u) {{
  if (u == null) return false;
  try {{ return {PKG}.BzUtil.bridge().get("profile:busy:" + u) != null; }} catch (Throwable t) {{ return false; }}
}}""", trd))
# 0.1.2: how many units of id fit in storage + hotbar + backpack (the containers Inv.give fills): empty slot = max stack, partial stack
# of the same item = the rest of it. Max stack unknown -> MAXQ (no room limit; buy0 still refunds whatever does not fit).
trd.addMethod(CtNewMethod.make(f"""
public static int room({PLA} p, String id) {{
  if (p == null || id == null) return 0;
  int max = 0;
  try {{
    {ITM} it = ({ITM}) {ITM}.getAssetMap().getAsset(id);
    if (it != null) max = it.getMaxStack();
  }} catch (Throwable t) {{ max = 0; }}
  if (max <= 0) return MAXQ;
  {IC}[] cs = {PKG}.Inv.conts(p);
  long room = 0L;
  for (int c = 0; c < cs.length; c++) {{
    {IC} cont = cs[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short sl = 0; sl < cap; sl++) {{
      {IS} st = cont.getItemStack(sl);
      if (st == null || st.isEmpty()) room += (long) max;
      else if (id.equals(st.getItemId()) && st.getQuantity() < max) room += (long) (max - st.getQuantity());
    }}
  }}
  return room > (long) MAXQ ? MAXQ : (int) room;
}}""", trd))
''')
rep('''  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot take coins");
''', '''  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot take coins");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
''')
rep('''  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
''', '''  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
''')
rep('''trd.addMethod(CtNewMethod.make(f"""
public static {TR} sell({PLA} p, java.util.UUID u, String who, String id, int want) {{
  synchronized ({PKG}.Market.class) {{ return sell0(p, u, who, id, want); }}
}}""", trd))
''', '''trd.addMethod(CtNewMethod.make(f"""
public static {TR} sell({PLA} p, java.util.UUID u, String who, String id, int want) {{
  synchronized ({PKG}.Market.class) {{ return sell0(p, u, who, id, want); }}
}}""", trd))
# 0.1.2 custom amount BUY: exact qty (1 .. room, 1 .. MAXQ; the purse is checked by buy0), refused when the total now costs more than
# the maxCost the player was shown (moved + price = the new total so the page can re-arm), then the unchanged buy0.
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buyN0({PLA} p, java.util.UUID u, String who, String id, int qty, long maxCost) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (qty < 1 || qty > MAXQ) return new {TR}(false, 0, 0L, "type an amount from 1 to " + MAXQ);
  if ({PKG}.Catalog.get(id) == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  int rm = room(p, id);
  if (qty > rm) return new {TR}(false, 0, 0L, rm <= 0 ? "your inventory is full - nothing bought" : "only " + rm + " fit in your inventory - nothing bought");
  long cost = {PKG}.Market.quote(id, qty, true);
  if (cost <= 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  if (maxCost > 0L && cost > maxCost) {{
    {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now cost " + cost + " coins (you saw " + maxCost + ") - click Buy again to buy at the new price");
    mv.moved = true;
    mv.price = cost;
    return mv;
  }}
  return buy0(p, u, who, id, qty);
}}""", trd))
# 0.1.2 custom amount SELL: exact qty (1 .. held; sell0 alone would quietly sell less), refused when it now pays less than minPay.
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sellN0({PLA} p, java.util.UUID u, String who, String id, int qty, long minPay) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (qty < 1 || qty > MAXQ) return new {TR}(false, 0, 0L, "type an amount from 1 to " + MAXQ);
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  int held = {PKG}.Inv.count(p, id);
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  if (qty > held) return new {TR}(false, 0, 0L, "you only hold " + held + " " + pr.name + " - nothing sold");
  long pay = {PKG}.Market.quote(id, qty, false);
  if (pay < 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  // a sale now worth 0 is refused outright (sell0 refuses it too) - never a "price moved, click again" that nothing re-arms
  if (pay == 0L) return new {TR}(false, 0, 0L, qty + " " + pr.name + " is worth 0 coins right now - sell more at once");
  if (minPay > 0L && pay < minPay) {{
    {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now pay " + pay + " coins (you saw " + minPay + ") - click Sell again to sell at the new price");
    mv.moved = true;
    mv.price = pay;
    return mv;
  }}
  return sell0(p, u, who, id, qty);
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buyN({PLA} p, java.util.UUID u, String who, String id, int qty, long maxCost) {{
  synchronized ({PKG}.Market.class) {{ return buyN0(p, u, who, id, qty, maxCost); }}
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sellN({PLA} p, java.util.UUID u, String who, String id, int qty, long minPay) {{
  synchronized ({PKG}.Market.class) {{ return sellN0(p, u, who, id, qty, minPay); }}
}}""", trd))
''')

# ---------------- BzPage: replaced whole (1.4x layout + custom amount row + exact action matching) ----------------
P0 = '# ================= BzPage (inline page; syntax copied from SkyySacks 0.6.1 SacksPage/CraftPage) =================' + LF
P1 = 'fac.addInterface(pool.get("java.util.function.Function"))' + LF
a = s.index(P0)
b = s.index(P1, a)
assert s.count(P0) == 1 and s.count(P1) == 1

PAGE = r'''# ================= BzPage (inline page; syntax copied from SkyySacks 0.6.1 SacksPage/CraftPage) =================
# 0.1.2: about 1.4x (root 1080 wide; 640 high with one grid row, +94 per extra row, 828 max), a custom amount row (TextField
# #SkyyBzAmt - SkyyGuilds 0.1 Amount field / SkyySacks 0.7.3 search pattern: Enter = Validating, buttons = Activating, the typed text
# arrives as "@BzAmount"), and every action matched exactly with jsonStr(data, "a") (typed text can never look like a payload).
BS_BROWN = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 17, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 17, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 17, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
BS_ON    = "Style: TextButtonStyle(Default: (Background: #e0b060, LabelStyle: (FontSize: 17, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #f0c878, LabelStyle: (FontSize: 17, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #b08040, LabelStyle: (FontSize: 17, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
BS_BUY   = "Style: TextButtonStyle(Default: (Background: #2f5a34, LabelStyle: (FontSize: 16, TextColor: #dfffe0, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3f7a46, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #1f3a22, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
BS_SELL  = "Style: TextButtonStyle(Default: (Background: #6a2e2e, LabelStyle: (FontSize: 16, TextColor: #ffe0e0, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a4040, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #4a1e1e, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
for s in (BS_BROWN, BS_ON, BS_BUY, BS_SELL):
    assert '"' not in s and "{" not in s

page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String sel;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String[] tabs;", page))
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public long confirmUntil;", page))
# 0.1.2 custom amount: the last submitted field text (put back on every rebuild) and the totals the player was shown (armBuy / armSell
# = the price for armBQ / armSQ units of armId, -1 = that side is not armed) until armUntil.
page.addField(CtField.make("public String amount;", page))
page.addField(CtField.make("public String armId;", page))
page.addField(CtField.make("public int armBQ;", page))
page.addField(CtField.make("public long armBuy;", page))
page.addField(CtField.make("public int armSQ;", page))
page.addField(CtField.make("public long armSell;", page))
page.addField(CtField.make("public long armUntil;", page))
page.addConstructor(CtNewConstructor.make(f"""
public BzPage({PR} pr, String sel) {{
  super(pr, {LIFE}.CanDismiss);
  this.sel = sel;
  this.info = "";
  this.confirmUntil = 0L;
  this.amount = "";
  this.armId = null;
  this.armBQ = 0;
  this.armBuy = -1L;
  this.armSQ = 0;
  this.armSell = -1L;
  this.armUntil = 0L;
  {PKG}.Product p = {PKG}.Catalog.get(sel);
  this.cat = p == null ? null : p.cat;
}}""", page))
page.addMethod(CtNewMethod.make("""
public void disarm() {
  this.armId = null;
  this.armBQ = 0;
  this.armBuy = -1L;
  this.armSQ = 0;
  this.armSell = -1L;
  this.armUntil = 0L;
}""", page))
# event data for a binding; while the amount field is on the page every binding also carries its current text (@BzAmount)
page.addMethod(CtNewMethod.make(f"""
public {EVD} evd(String a, boolean amt) {{
  {EVD} d = {EVD}.of("a", a);
  if (amt) d = d.append("@BzAmount", "#SkyyBzAmt.Value");
  return d;
}}""", page))
# lim = {{afford (-1 = coin bank error; already capped by room and MAXQ), room, held}}. null = OK, else why the amount is refused.
page.addMethod(CtNewMethod.make(f"""
public static String buyWhy(int q, int[] lim) {{
  int afford = lim[0];
  int room = lim[1];
  if (afford < 0) return "the coin bank did not answer - try again";
  if (q < 1) return room <= 0 ? "your inventory is full" : (afford <= 0 ? "you cannot afford even 1" : "type 1 or more");
  if (q > {PKG}.Trader.MAXQ) return "at most " + {PKG}.Trader.MAXQ + " per trade";
  if (q > room) return room <= 0 ? "your inventory is full" : "only " + room + " fit in your inventory";
  if (q > afford) return afford <= 0 ? "you cannot afford even 1" : "your purse covers " + afford + " at most";
  return null;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public static String sellWhy(int q, int held) {{
  if (held <= 0) return "you have none to sell";
  if (q < 1) return "type 1 or more";
  if (q > {PKG}.Trader.MAXQ) return "at most " + {PKG}.Trader.MAXQ + " per trade";
  if (q > held) return "you only hold " + held;
  return null;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public int[] limits({PLA} p, java.util.UUID u, String id) {{
  int held = {PKG}.Inv.count(p, id);
  int room = {PKG}.Trader.room(p, id);
  int afford = -1;
  if ({PKG}.Coins.ready()) {{
    long purse = {PKG}.Coins.get(u);
    if (purse >= 0L) afford = {PKG}.Market.maxBuyable(id, purse, room < {PKG}.Trader.MAXQ ? room : {PKG}.Trader.MAXQ);
  }}
  return new int[] {{ afford, room, held }};
}}""", page))
# the whole page (build() only resolves the player; render() is also what the offline markup check calls)
page.addMethod(CtNewMethod.make(f"""
public void render({UCB} b, {UEB} ev, java.util.UUID u, {PLA} player) {{
  java.util.ArrayList cats = {PKG}.Catalog.categories();
  if (this.cat == null || !cats.contains(this.cat)) this.cat = cats.isEmpty() ? null : (String) cats.get(0);
  if (this.sel != null && !{PKG}.Catalog.usable(this.sel)) this.sel = null;
  boolean coinsOk = {PKG}.Coins.ready();
  boolean confirming = System.currentTimeMillis() <= this.confirmUntil;
  String bs = "{BS_BROWN}";
  String on = "{BS_ON}";
  String buyS = "{BS_BUY}";
  String sellS = "{BS_SELL}";
  {PKG}.Product sp = {PKG}.Catalog.get(this.sel);
  boolean amtOn = sp != null && player != null;
  java.util.ArrayList list = new java.util.ArrayList();
  java.util.ArrayList raw = this.cat == null ? new java.util.ArrayList() : {PKG}.Catalog.inCat(this.cat);
  for (int i = 0; i < raw.size(); i++) {{ {PKG}.Product p = ({PKG}.Product) raw.get(i); if ({PKG}.Catalog.usable(p.id)) list.add(p); }}
  int n = list.size() < 27 ? list.size() : 27;
  int rows = (n + 8) / 9;
  int h = 640 + ((rows < 1 ? 1 : rows) - 1) * 94;
  b.appendInline((String) null, "Group #SkyyBz {{ Anchor: (Width: 1080, Height: " + h + "); Background: #0b1524(0.96); Padding: (Horizontal: 22, Vertical: 14); LayoutMode: Top; }}");
  b.appendInline("#SkyyBz", "Group {{ Anchor: (Height: 3); Background: #e0b060; }}");
  b.appendInline("#SkyyBz", "Group #SkyyBzHead {{ Anchor: (Height: 44); LayoutMode: Left; }}");
  b.appendInline("#SkyyBzHead", "Label {{ Anchor: (Width: 420, Height: 44); Text: \\"Bazaar\\"; Style: (FontSize: 24, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }}");
  long pv = coinsOk ? {PKG}.Coins.get(u) : 0L;
  String purse = coinsOk ? (pv >= 0L ? ("Purse " + pv + " coins") : "Purse unavailable - coin bank error") : "SkyyCoins is not loaded - trading is off";
  b.appendInline("#SkyyBzHead", "Label {{ Anchor: (Width: 616, Height: 44); Text: \\"" + {PKG}.BzUtil.safe(purse) + "\\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + (coinsOk ? "#ffd766" : "#e07070") + ", HorizontalAlignment: End, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyBz", "Group #SkyyBzTabs {{ Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 6); }}");
  int nt = cats.size() < 6 ? cats.size() : 6;
  int tw = nt <= 4 ? 146 : (804 - nt * 8) / nt;
  this.tabs = new String[nt];
  for (int i = 0; i < nt; i++) {{
    String c = (String) cats.get(i);
    this.tabs[i] = c;
    b.appendInline("#SkyyBzTabs", "TextButton #SkyyBzTab" + i + " {{ Anchor: (Width: " + tw + ", Height: 40); Text: \\"" + {PKG}.BzUtil.safe(c) + "\\"; " + (c.equals(this.cat) ? on : bs) + " }}");
    b.appendInline("#SkyyBzTabs", "Label {{ Anchor: (Width: 8, Height: 40); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyyBzTab" + i, evd("tab:" + i, amtOn));
  }}
  int gap = 1036 - nt * (tw + 8) - 224; if (gap < 4) gap = 4;
  b.appendInline("#SkyyBzTabs", "Label {{ Anchor: (Width: " + gap + ", Height: 40); Text: \\"\\"; }}");
  b.appendInline("#SkyyBzTabs", "TextButton #SkyyBzSellInv {{ Anchor: (Width: 220, Height: 40); Text: \\"" + (confirming ? "Confirm sell" : "Sell inventory") + "\\"; " + sellS + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyBzSellInv", evd("sellinv", amtOn));
  // the page holds 6 tabs x 27 products (0.1.1 caps; more rows / tabs need a client check of the height and tab width first). Anything
  // past them is named here in the same fixed-height line instead of being hidden without a word.
  int hidP = list.size() - n;
  int hidC = cats.size() - nt;
  String sub = "Instant buy and sell with the market. Prices move with every trade and drift back over time.";
  if (hidP > 0 || hidC > 0) sub = (hidP > 0 ? hidP + " more products in this tab" : "") + (hidP > 0 && hidC > 0 ? " and " : "") + (hidC > 0 ? hidC + " more tabs" : "") + " do not fit the page (6 tabs of 27 products) - tell an admin";
  b.appendInline("#SkyyBz", "Label #SkyyBzSub {{ Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + (hidP > 0 || hidC > 0 ? "#ffb070" : "#9fb8cc") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyBzSub.Text", sub);
  this.cells = new String[27];
  if (n == 0) b.appendInline("#SkyyBz", "Label {{ Anchor: (Height: 94); Text: \\"No products here.\\"; Style: (FontSize: 17, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int r = 0; r < rows; r++) {{
    b.appendInline("#SkyyBz", "Group #SkyyBzRow" + r + " {{ Anchor: (Height: 94); LayoutMode: Left; Padding: (Top: 6); }}");
    b.appendInline("#SkyyBzRow" + r, "Label {{ Anchor: (Width: 99, Height: 87); Text: \\"\\"; }}");
    for (int c = 0; c < 9; c++) {{
      int idx = r * 9 + c;
      if (idx < n) {{
        {PKG}.Product p = ({PKG}.Product) list.get(idx);
        this.cells[idx] = p.id;
        int held = player == null ? 0 : {PKG}.Inv.count(player, p.id);
        String bg = p.id.equals(this.sel) ? "#4f7fb0" : "#1d3a5f";
        b.appendInline("#SkyyBzRow" + r, "Button #SkyyBzCell" + idx + " {{ Anchor: (Width: 87, Height: 87); Style: ButtonStyle( Default: ( Background: " + bg + " ), Hovered: ( Background: #2f5a8f ), Disabled: ( Background: #1a2c3c ) ); ItemIcon {{ Anchor: (Width: 64, Height: 64, Left: 11, Top: 6); ItemId: \\"" + p.id + "\\"; }} Label {{ Anchor: (Width: 81, Height: 20, Right: 4, Bottom: 3); Text: \\"" + (held > 0 ? String.valueOf(held) : "") + "\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); }} }}");
        ev.addEventBinding({BT}.Activating, "#SkyyBzCell" + idx, evd("cell:" + idx, amtOn));
      }} else {{
        b.appendInline("#SkyyBzRow" + r, "Group {{ Anchor: (Width: 87, Height: 87); Background: #142030(0.9); }}");
      }}
      b.appendInline("#SkyyBzRow" + r, "Label {{ Anchor: (Width: 6, Height: 87); Text: \\"\\"; }}");
    }}
  }}
  b.appendInline("#SkyyBz", "Group {{ Anchor: (Height: 10); }}");
  if (!amtOn) {{
    // same height as detail (168) + trade row (58) + amount row (58) + limits line (28), so selecting a product never resizes the page
    b.appendInline("#SkyyBz", "Group #SkyyBzDetail {{ Anchor: (Height: 312); LayoutMode: Top; Background: #10233a(0.9); }}");
    b.appendInline("#SkyyBzDetail", "Label {{ Anchor: (Height: 312); Text: \\"Click a product to see its prices and trade it.\\"; Style: (FontSize: 18, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  }} else {{
    String id = sp.id;
    long b1 = {PKG}.Market.quote(id, 1, true), b64 = {PKG}.Market.quote(id, 64, true);
    long s1 = {PKG}.Market.quote(id, 1, false), s64 = {PKG}.Market.quote(id, 64, false);
    int[] lim = limits(player, u, id);
    int held = lim[2];
    long sAll = held > 0 ? {PKG}.Market.quote(id, held > {PKG}.Trader.MAXQ ? {PKG}.Trader.MAXQ : held, false) : 0L;
    double f = {PKG}.Market.factor(id);
    b.appendInline("#SkyyBz", "Group #SkyyBzDetail {{ Anchor: (Height: 168); LayoutMode: Left; Padding: (Top: 8); Background: #10233a(0.9); }}");
    b.appendInline("#SkyyBzDetail", "Group {{ Anchor: (Width: 140, Height: 152); ItemIcon {{ Anchor: (Width: 118, Height: 118, Left: 11, Top: 8); ItemId: \\"" + id + "\\"; }} }}");
    b.appendInline("#SkyyBzDetail", "Group #SkyyBzDTxt {{ Anchor: (Width: 880, Height: 152); LayoutMode: Top; }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 34); Text: \\"" + {PKG}.BzUtil.safe(sp.name) + "\\"; Style: (FontSize: 21, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 28); Text: \\"" + {PKG}.BzUtil.safe("Instant buy   " + b1 + " coins for 1   -   " + b64 + " for 64   -   about " + {PKG}.BzUtil.num({PKG}.Market.unit(id, true)) + " each") + "\\"; Style: (FontSize: 17, TextColor: #9fe8a2, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 28); Text: \\"" + {PKG}.BzUtil.safe("Instant sell   " + s1 + " coins for 1   -   " + s64 + " for 64   -   about " + {PKG}.BzUtil.num({PKG}.Market.unit(id, false)) + " each") + "\\"; Style: (FontSize: 17, TextColor: #ffb0a0, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 28); Text: \\"" + {PKG}.BzUtil.safe("You hold " + held + (held > 0 ? "   -   selling all pays " + sAll + " coins" : "")) + "\\"; Style: (FontSize: 17, TextColor: #ffe9c9, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 26); Text: \\"" + {PKG}.BzUtil.safe("Demand " + {PKG}.BzUtil.num(f) + "x   -   buying pushes it up and selling pushes it down - it drifts back to 1.0x") + "\\"; Style: (FontSize: 14, TextColor: #8fa4b8, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBz", "Group #SkyyBzActs {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 8); }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzBuy1 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Buy 1 for " + b1) + "\\"; " + buyS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzBuy64 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Buy 64 for " + b64) + "\\"; " + buyS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzSell1 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Sell 1 for " + s1) + "\\"; " + sellS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzSell64 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Sell 64 for " + s64) + "\\"; " + sellS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzSellAll {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Sell all " + held) + "\\"; " + sellS + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyBzBuy1", evd("buy1", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzBuy64", evd("buy64", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzSell1", evd("sell1", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzSell64", evd("sell64", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzSellAll", evd("sellall", true));
    // 0.1.2 custom amount row (inline TextField exactly like SkyyGuilds' #SkyyGAmount / SkyySacks' #SkyyCSearch)
    b.appendInline("#SkyyBz", "Group #SkyyBzAmtRow {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 8); }}");
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 176, Height: 42); Text: \\"Custom amount\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzAmtRow", "Group #SkyyBzAmtBox {{ Anchor: (Width: 220, Height: 42); Background: #16263a; }}");
    b.appendInline("#SkyyBzAmtBox", "TextField #SkyyBzAmt {{ Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 12; PlaceholderText: \\"Amount\\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 18); Style: (TextColor: #ffffff, FontSize: 18); }}");
    if (this.amount != null && this.amount.length() > 0) b.set("#SkyyBzAmt.Value", this.amount);
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzAmtRow", "TextButton #SkyyBzABuy {{ Anchor: (Width: 170, Height: 42); Text: \\"Buy\\"; " + buyS + " }}");
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzAmtRow", "TextButton #SkyyBzASell {{ Anchor: (Width: 170, Height: 42); Text: \\"Sell\\"; " + sellS + " }}");
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 14, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzAmtRow", "Label #SkyyBzAmtHint {{ Anchor: (Width: 266, Height: 42); Text: \\"\\"; Style: (FontSize: 14, TextColor: #9fb8cc, VerticalAlignment: Center); }}");
    b.set("#SkyyBzAmtHint.Text", "Enter shows the price");
    ev.addEventBinding({BT}.Validating, "#SkyyBzAmt", evd("amt", true), false);
    ev.addEventBinding({BT}.Activating, "#SkyyBzABuy", evd("abuy", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzASell", evd("asell", true));
    int mq = {PKG}.Trader.MAXQ;
    String lt;
    if (!coinsOk) lt = "SkyyCoins is not loaded - trading is off.";
    else if ({PKG}.Trader.busy(u)) lt = "Your profile is still loading - trading is paused. Click again in a moment.";
    else if (lim[0] < 0) lt = "The coin bank did not answer - buy limit unknown. You can sell up to " + (held > mq ? mq : held) + ".";
    else {{
      int mb = lim[0];
      String why = mb >= mq ? "the per-trade limit" : (mb >= lim[1] ? (lim[1] <= 0 ? "your inventory is full" : "inventory room") : "your purse");
      lt = "You can buy up to " + mb + " (" + why + ") and sell up to " + (held > mq ? mq : held) + ".   Amounts like 500, 2k or max.";
    }}
    b.appendInline("#SkyyBz", "Label #SkyyBzLimits {{ Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 15, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.set("#SkyyBzLimits.Text", lt);
  }}
  b.appendInline("#SkyyBz", "Label #SkyyBzInfo {{ Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd766, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyBzInfo.Text", this.info == null ? "" : this.info);
  b.appendInline("#SkyyBz", "Label {{ Anchor: (Height: 25); Text: \\"Totals are whole coins - buys round up and sells round down. Sell inventory and custom amounts ask you to confirm.\\"; Style: (FontSize: 14, TextColor: #6f879c, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  render(b, ev, u, player);
}}""", page))
# 0.1.2 custom amount click: a = amt (Enter: price both sides, never trades) | abuy | asell. The price is always shown before a trade:
# an unpriced Buy / Sell click only arms that side; the armed click trades with the shown total as a cap (Trader.buyN / sellN).
page.addMethod(CtNewMethod.make(f"""
public void amountAction({PLA} p, java.util.UUID u, String who, String a, long now) {{
  {PKG}.Product sp = {PKG}.Catalog.get(this.sel);
  if (sp == null || !{PKG}.Catalog.usable(sp.id)) {{ this.info = "click a product first"; disarm(); return; }}
  if (!{PKG}.Coins.ready()) {{ this.info = "SkyyCoins is not loaded - trading is off"; disarm(); return; }}
  // never price or arm a trade that buy0 / sell0 would refuse anyway (profile crash recovery at join)
  if ({PKG}.Trader.busy(u)) {{ this.info = "your profile is still loading - try again in a moment"; disarm(); return; }}
  String id = sp.id;
  String nm = sp.name;
  long v = {PKG}.BzUtil.parseAmt(this.amount);
  if (v == -1L) {{
    boolean empty = this.amount == null || this.amount.trim().length() == 0;
    this.info = empty ? "type an amount first - for example 500 or 2k - or max" : "that is not an amount - type a whole number like 500 or 2k - or max";
    disarm();
    return;
  }}
  int[] lim = limits(p, u, id);
  int mq = {PKG}.Trader.MAXQ;
  int qb = 0;
  int qs = 0;
  if (v == -2L) {{ qb = lim[0] < 0 ? 0 : lim[0]; qs = lim[2] > mq ? mq : lim[2]; }}
  else {{ qb = v > (long) mq ? mq + 1 : (int) v; qs = qb; }}
  if (a.equals("amt")) {{
    String wb = buyWhy(qb, lim);
    String ws = sellWhy(qs, lim[2]);
    long cb = wb == null ? {PKG}.Market.quote(id, qb, true) : -1L;
    long cs = ws == null ? {PKG}.Market.quote(id, qs, false) : -1L;
    if (wb == null && cb <= 0L) wb = "no price right now";
    if (ws == null && cs <= 0L) ws = cs == 0L ? "worth 0 coins - sell more at once" : "no price right now";
    disarm();
    this.armId = id;
    if (wb == null) {{ this.armBQ = qb; this.armBuy = cb; }}
    if (ws == null) {{ this.armSQ = qs; this.armSell = cs; }}
    if (wb == null || ws == null) this.armUntil = now + 15000L;
    if (wb == null && ws == null && qb == qs) this.info = qb + " " + nm + " - buy for " + cb + " coins - sell for " + cs + " coins - click Buy or Sell";
    else {{
      String tb = wb == null ? "Buy " + qb + " for " + cb + " coins" : "Buy - " + wb;
      String ts = ws == null ? "Sell " + qs + " for " + cs + " coins" : "Sell - " + ws;
      this.info = nm + "   " + tb + "   /   " + ts;
    }}
    return;
  }}
  boolean buy = a.equals("abuy");
  int q = buy ? qb : qs;
  String why = buy ? buyWhy(qb, lim) : sellWhy(qs, lim[2]);
  if (why != null) {{ this.info = (buy ? "Buy " : "Sell ") + nm + " - " + why; disarm(); return; }}
  boolean armed = now <= this.armUntil && id.equals(this.armId) && (buy ? (this.armBuy > 0L && this.armBQ == q) : (this.armSell > 0L && this.armSQ == q));
  if (!armed) {{
    // max / all is worked out again on every click; if this side was priced for a different max a moment ago (prices, the purse or
    // the inventory changed), say so instead of a plain re-quote (a fixed number that moved is reported by Trader.buyN0 / sellN0)
    int was = 0;
    if (v == -2L && now <= this.armUntil && id.equals(this.armId)) was = buy ? (this.armBuy > 0L ? this.armBQ : 0) : (this.armSell > 0L ? this.armSQ : 0);
    long c = {PKG}.Market.quote(id, q, buy);
    disarm();
    if (c <= 0L) {{ this.info = c == 0L ? q + " " + nm + " is worth 0 coins right now - sell more at once" : "price error - tell an admin"; return; }}
    this.armId = id;
    if (buy) {{ this.armBQ = q; this.armBuy = c; }} else {{ this.armSQ = q; this.armSell = c; }}
    this.armUntil = now + 10000L;
    String pre = was > 0 && was != q ? "your max changed from " + was + " to " + q + " - " : "";
    this.info = pre + (buy ? "Buy " : "Sell ") + q + " " + nm + " for " + c + " coins - click " + (buy ? "Buy" : "Sell") + " again within 10 s to confirm";
    return;
  }}
  long seen = buy ? this.armBuy : this.armSell;
  {TR} r = null;
  if (buy) r = {PKG}.Trader.buyN(p, u, who, id, q, seen);
  else r = {PKG}.Trader.sellN(p, u, who, id, q, seen);
  disarm();
  if (r == null) return;
  if (r.moved && r.price > 0L) {{
    this.armId = id;
    if (buy) {{ this.armBQ = q; this.armBuy = r.price; }} else {{ this.armSQ = q; this.armSell = r.price; }}
    this.armUntil = now + 10000L;
  }}
  if (r.alert) this.playerRef.sendMessage({MSG}.raw("[Bazaar] " + r.msg));
  this.info = r.msg;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    // 0.1.2: the action is matched exactly (SkyyGuilds pattern) - text typed into the amount field can never look like a payload
    String a = {PKG}.BzUtil.jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    long now = System.currentTimeMillis();
    // while the amount field is on the page every binding carries its text - keep what was typed across clicks and rebuilds
    if (data.indexOf("\\"@BzAmount\\"") >= 0) {{
      String v = {PKG}.BzUtil.jsonStr(data, "@BzAmount").trim();
      if (v.length() > 12) v = v.substring(0, 12);
      this.amount = v;
    }}
    // any click other than the Sell inventory button itself cancels a pending "Confirm sell"
    // (selecting another item or trading must never leave the full-inventory sell armed)
    boolean sellInvClick = a.equals("sellinv");
    if (!sellInvClick) this.confirmUntil = 0L;
    // the same for a priced custom amount: only the amount field / its Buy and Sell buttons keep it armed
    boolean amtAct = a.equals("amt") || a.equals("abuy") || a.equals("asell");
    if (!amtAct) disarm();
    for (int i = 0; this.tabs != null && i < this.tabs.length; i++) {{
      if (a.equals("tab:" + i)) {{ this.cat = this.tabs[i]; this.info = ""; rebuild(); return; }}
    }}
    for (int i = 0; this.cells != null && i < this.cells.length; i++) {{
      if (this.cells[i] != null && a.equals("cell:" + i)) {{ this.sel = this.cells[i]; this.info = ""; rebuild(); return; }}
    }}
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    String who = {PKG}.BzUtil.safe(this.playerRef.getUsername()).replace(' ', '_');
    if (amtAct) {{ amountAction(p, u, who, a, now); rebuild(); return; }}
    {TR} r = null;
    if (a.equals("buy1")) r = {PKG}.Trader.buy(p, u, who, this.sel, 1);
    else if (a.equals("buy64")) r = {PKG}.Trader.buy(p, u, who, this.sel, 64);
    else if (a.equals("sell1")) r = {PKG}.Trader.sell(p, u, who, this.sel, 1);
    else if (a.equals("sell64")) r = {PKG}.Trader.sell(p, u, who, this.sel, 64);
    else if (a.equals("sellall")) r = {PKG}.Trader.sell(p, u, who, this.sel, 0);
    else if (sellInvClick) {{
      // no "sell N items - click Confirm sell" preview that every sell0 would then refuse (profile crash recovery at join)
      if ({PKG}.Trader.busy(u)) {{ this.info = "your profile is still loading - try again in a moment"; this.confirmUntil = 0L; rebuild(); return; }}
      if (now > this.confirmUntil) {{
        long[] pv = {PKG}.Trader.preview(p);
        if (pv[0] <= 0L) {{ this.info = "nothing to sell - no bazaar items in your inventory"; this.confirmUntil = 0L; }}
        else {{ this.info = "sell " + pv[0] + " items for about " + pv[1] + " coins - click Confirm sell within 10 seconds"; this.confirmUntil = now + 10000L; }}
        rebuild();
        return;
      }}
      this.confirmUntil = 0L;
      r = {PKG}.Trader.sellInventory(p, u, who);
    }}
    if (r == null) return;
    // chat copy for a finished Sell inventory and for anything where the player may be owed coins or items
    // (the info label is replaced by the next click; chat stays)
    if (r.alert || (sellInvClick && r.ok)) this.playerRef.sendMessage({MSG}.raw("[Bazaar] " + r.msg));
    this.info = r.msg;
    rebuild();
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("bazaar page event failed: " + t); }}
}}""", page))

'''
s = s[:a] + PAGE + s[b:]

assert 'VERSION = "0.1.2"' in s
assert "{PKG}.BzUtil.has(data" not in s, "an old substring action match survived"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
