"""Derive SkyyMerchants/build_skyymerchants_0.1.1.py (+ its harness test_skyymerchants_0.1.1.py) from the CURRENT generated 0.1
(build_skyymerchants_0.1.py / test_skyymerchants_0.1.py = the tools/deploy_set.py SET pin; 0.1 had no patch chain - this file starts it).
Run:  python tools/merchants_0_1_1_patch.py   then   python SkyyMerchants/build_skyymerchants_0.1.1.py   then
      python SkyyMerchants/test_skyymerchants_0.1.1.py --dir <tools/dev/scratch/...>     (never --deploy: tools/deploy_set.py deploys)
Edit THIS file, never the generated scripts.

0.1.1 (2026-10-10) - ONE WEAPON PER CLASS. Skyy tested the merchant (shop opened, bought a Flame Shortbow for 2,000, sold-out row worked):
"nothing for my class but i got a flame bow" + popup "How should its stock work? -> One per class" (docs/answered/economy.md 2026-10-10).
  - Every restock (= every visit) now carries AT LEAST ONE weapon for EACH class SkyyClasses lists (bridge class:list - Archer, Warrior,
    Mage, Berserker, Priest, Assassin, Monk today; a Spellblade appears by itself once SkyyClasses lists it). Which class a weapon belongs
    to = SkyyClasses' own rule, read live from its bridge: class:weapons:<Class> / :free / :unassigned prefixes, the LONGEST prefix wins
    (equal length: classes in list order first) - so Weapon_Staff_Bo_* is Monk, Weapon_Staff_* Mage, a shield or a pack recolour without a
    Weapon_<family>_ prefix (Sword_Iron_Green) belongs to no class.
  - Per class, in class order: a random weapon of that class from the zone's stock table (merchant.weapons: in zone, Stock > 0, the server
    knows the id, not walled) - its table price and Stock. None in the table -> a random VANILLA weapon of that class's families whose
    Hytale ItemLevel lies in the zone's Levels band (lo..hi inclusive; band 0 = any): the build-time list FB_IDS / FB_LV from Assets.zip
    = metal ladder weapons only (a Copper / Bronze / Iron / Thorium / Cobalt / Adamantite / Mithril / Onyxium word in the id), Quality
    Common / Uncommon / Rare / Epic (never Developer, never Legendary), no ammo (Weapon_Arrow_*), no shield, never a Rusty / NPC / Test id,
    never on the never-sell list; at runtime also never walled (never-sell list, Magic Bags, SkyyGear Mythic / Untiered / Set) and only ids
    the server knows. Its price = the median price of the zone's table weapons this visit (none: 150 x its level, at least 100), Stock 1.
    Still nothing for a class -> that class is skipped and the server log says so once (add a row in Server Setup > Merchants > Stock).
  - A zone whose table has NO sellable weapon (rows cleared, or every row Stock 0) sells no weapons at all, as in 0.1 - an admin can still
    stop weapon sales per zone; the class rule (and its vanilla fallback) only tops up a zone that sells weapons.
  - Then the existing random extras: up to merchant.offers (4) more table weapons of the zone that were not picked yet (table permitting).
    Mounts / pet eggs unchanged. Prices + stock stay frozen for the visit.
  - Old behaviour (exactly 0.1: merchant.offers random table weapons) when SkyyClasses is missing (no class:list) or the new switch
    merchant.everyClass (Server Setup > Merchants > Merchants, "One weapon for every class", live, default ON) is off.
  - Page: a weapon row of a class reads "<Class> - <name>" ('Berserker - Iron Battleaxe'); class picks come first, in class order.
  - SAVED DATA: unchanged. The stock line keeps "cat:id:price:left"; a 0.1 stock line is read as before (the class name is worked out
    when the page is drawn) and the next move restocks with the new rule. config.properties: the new merchant.everyClass line is only in
    the default text of a NEW file - an existing file has no line = the default (on); nothing is rewritten.
  - Harness hook (null in game): MerchEng.EXTRA - ids the harness declares known (the pack / SkyyArmory items it does not load).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "SkyyMerchants")
CR, LF = chr(13), chr(10)


def load(name):
    raw = open(os.path.join(D, name), encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


S = {}


def rep(key, old, new, count=1):
    n = S[key].count(old)
    assert n == count, "%s: anchor count %d (want %d): %s" % (key, n, count, old[:120])
    S[key] = S[key].replace(old, new)


# ============================================================================================================= build script
S["b"], NLB = load("build_skyymerchants_0.1.py")
rep("b", 'VERSION = "0.1"\n', 'VERSION = "0.1.1"\n')
rep("b", "Owner: Skyy (they/them). Run:  python SkyyMerchants/build_skyymerchants_0.1.py   -> SkyyMerchants/SkyyMerchants-0.1.jar",
    "Owner: Skyy (they/them). Run:  python SkyyMerchants/build_skyymerchants_0.1.1.py   -> SkyyMerchants/SkyyMerchants-0.1.1.jar")
rep("b", "Test: python SkyyMerchants/test_skyymerchants_0.1.py\n",
    "Test: python SkyyMerchants/test_skyymerchants_0.1.1.py\n"
    "GENERATED by tools/merchants_0_1_1_patch.py from build_skyymerchants_0.1.py - edit the patch, never this file.\n\n"
    "0.1.1 (2026-10-10, Skyy: \"nothing for my class but i got a flame bow\" -> \"One per class\"): every visit's weapon stock carries at\n"
    "  least one weapon for EACH class SkyyClasses lists (class:list + class:weapons:<Class>, longest prefix wins): from the zone's table,\n"
    "  else a vanilla metal-ladder weapon of that class whose ItemLevel is in the zone band (median table price, stock 1); then up to\n"
    "  merchant.offers random extras. Rows read '<Class> - <name>'. No SkyyClasses / merchant.everyClass off = the 0.1 rule. Saved data\n"
    "  unchanged. Notes in tools/merchants_0_1_1_patch.py.\n")

# ---- the vanilla fallback pool (build time, Assets.zip read only), right after the desk line
DESK_END = """      len(MOUNTS), len(PETS)))
"""
rep("b", DESK_END, DESK_END + r'''
# 0.1.1: the VANILLA FALLBACK POOL for a class the zone's table has nothing for (the class itself is decided live from SkyyClasses'
# prefixes). Metal-ladder weapons only, with Hytale's own ItemLevel (the level Item.getItemLevel reports) - Quality Common..Epic.
FB_METALS = ("Copper", "Bronze", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
FB_QUAL = ("Common", "Uncommon", "Rare", "Epic")
_FB_PATH = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def _fb_get(i, key, depth=0):
    d = json.loads(az.read(_FB_PATH[i]).decode("utf-8-sig"))
    if key in d or depth > 8 or not d.get("Parent") or d.get("Parent") not in _FB_PATH:
        return d.get(key)
    return _fb_get(d["Parent"], key, depth + 1)


FB = []
for _i in sorted(_FB_PATH):
    _w = _i.split("_")
    if not _i.startswith("Weapon_") or _i.startswith(("Weapon_Arrow_", "Weapon_Shield_")) or walled(_i):
        continue
    if not any(m in _w for m in FB_METALS) or any(x in _w for x in ("Rusty", "NPC", "Test")):
        continue
    _lv, _q = _fb_get(_i, "ItemLevel"), _fb_get(_i, "Quality")
    if not isinstance(_lv, int) or _lv <= 0 or _q not in FB_QUAL:
        continue
    FB.append((_i, _lv))
    if LANG.get("items.%s.name" % _i):
        NAMES.setdefault(_i, LANG["items.%s.name" % _i])
FB_IDS = [i for i, _l in FB]
FB_LV = [l for _i, l in FB]
for _need in ("Weapon_Sword_Iron", "Weapon_Daggers_Iron", "Weapon_Battleaxe_Iron", "Weapon_Staff_Iron", "Weapon_Shortbow_Iron",
              "Weapon_Sword_Onyxium", "Weapon_Daggers_Onyxium"):
    assert _need in FB_IDS, "0.1.1 fallback pool lost %s" % _need
assert not any(walled(i) or i.startswith("Weapon_Arrow_") for i in FB_IDS)
print("0.1.1 fallback pool: %d vanilla metal weapons, levels %d-%d" % (len(FB), min(FB_LV), max(FB_LV)))
''')

# ---- MerchEng: the harness hook for ids it does not load
rep("b", r"""M(eng, r'''
public static boolean itemOk(String id) {
  if (id == null || id.length() == 0) return false;
  try { return @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}''')""".replace("'''", '"""'), r"""F(eng, "public static volatile java.util.Set EXTRA = null;")   # 0.1.1 harness hook: ids declared known (null in game)
M(eng, r'''
public static boolean itemOk(String id) {
  if (id == null || id.length() == 0) return false;
  java.util.Set x = EXTRA;
  if (x != null && x.contains(id)) return true;
  try { return @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}''')""".replace("'''", '"""'))

# ---- the switch (Server Setup > Merchants > Merchants) + the offers help text
rep("b", '''    ("merchant.offers", "Weapons per visit", "merch", "int", "4", "1", "30", "", "", "live",
     "How many weapons of its zone list a merchant brings each visit (picked at random).", "OFFERS", "int"),
''', '''    ("merchant.offers", "Weapons per visit", "merch", "int", "4", "1", "30", "", "", "live",
     "Random weapons of its zone list each visit - on top of the one weapon per class.", "OFFERS", "int"),
    # 0.1.1 (Skyy 2026-10-10 "One per class")
    ("merchant.everyClass", "One weapon for every class", "merch", "bool", "true", "", "", "", "", "live",
     "On = every visit has at least one weapon for each class (SkyyClasses). Applies from the next move.", "EVERY_CLASS", "boolean"),
''')

# ---- MerchShop: the class rule + the new restock
OLD_RESTOCK = r'''# the stock of one visit: "cat:id:price:left" comma separated (prices frozen for the visit)
M(shop, r"""
public static String restock(@PKG@.MerchZone z) {
  @PKG@.MerchItem[] all = @PKG@.MerchCfg.ITEMS;
  java.util.ArrayList w = new java.util.ArrayList();
  java.util.ArrayList rest = new java.util.ArrayList();
  for (int i = 0; i < all.length; i++) {
    @PKG@.MerchItem it = all[i];
    if (it.stock <= 0 || !it.inZone(z) || !@PKG@.MerchEng.itemOk(it.id) || @PKG@.MerchWall.why(it.id) != null) continue;
    if (it.cat == 0) w.add(it); else rest.add(it);
  }
  java.util.Collections.shuffle(w, RNG);
  int n = Math.min(w.size(), Math.max(1, @PKG@.MerchCfg.OFFERS));
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < n; i++) {
    @PKG@.MerchItem it = (@PKG@.MerchItem) w.get(i);
    if (b.length() > 0) b.append(',');
    b.append(it.cat).append(':').append(it.id).append(':').append(it.price).append(':').append(it.stock);
  }
  for (int i = 0; i < rest.size(); i++) {
    @PKG@.MerchItem it = (@PKG@.MerchItem) rest.get(i);
    if (b.length() > 0) b.append(',');
    b.append(it.cat).append(':').append(it.id).append(':').append(it.price).append(':').append(it.stock);
  }
  return b.toString();
}""")
'''
NEW_RESTOCK = r'''# ---- 0.1.1: ONE WEAPON PER CLASS (Skyy 2026-10-10). The class of an id = SkyyClasses' own rule, read live from its bridge.
F(shop, "public static final String[] FB_IDS = %s;" % jarr(FB_IDS))
F(shop, "public static final int[] FB_LV = new int[] { %s };" % ", ".join(str(l) for l in FB_LV))
F(shop, "public static volatile long CLASS_PICKS = 0L;")      # class slots filled from the zone's table
F(shop, "public static volatile long FALLBACK_PICKS = 0L;")   # class slots filled from the vanilla pool
F(shop, "public static volatile long CLASS_MISSES = 0L;")     # class slots nothing could fill
# the classes SkyyClasses lists (class:list "Archer:Archery,Warrior:..."); empty = no SkyyClasses
M(shop, r"""
public static String[] classNames() {
  Object o = null;
  try { o = @PKG@.MerchLog.bridge().get("class:list"); } catch (Throwable t) { o = null; }
  if (!(o instanceof String)) return new String[0];
  String[] a = ((String) o).split(",");
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) {
    String s = a[i].trim();
    int c = s.indexOf(':');
    if (c >= 0) s = s.substring(0, c).trim();
    if (s.length() > 0 && !l.contains(s)) l.add(s);
  }
  String[] r = new String[l.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) l.get(i);
  return r;
}""")
M(shop, r"""
public static String[] prefixes(String key) {
  Object o = null;
  try { o = @PKG@.MerchLog.bridge().get(key); } catch (Throwable t) { o = null; }
  if (!(o instanceof String)) return new String[0];
  return ((String) o).split(",");
}""")
# the class owning an id: the longest matching prefix of class:weapons:<Class> / :free / :unassigned (equal length: classes in list order,
# then free, then unassigned - SkyyClasses' stable sort); a free / unassigned / unmatched id = null
M(shop, r"""
public static String ownerOf(String id, String[] names) {
  if (id == null || names == null || names.length == 0) return null;
  String best = null;
  int bl = -1;
  for (int k = 0; k < names.length + 2; k++) {
    String key = k < names.length ? "class:weapons:" + names[k] : (k == names.length ? "class:weapons:free" : "class:weapons:unassigned");
    String[] ps = prefixes(key);
    for (int i = 0; i < ps.length; i++) {
      String p = ps[i].trim();
      if (p.length() == 0 || p.length() <= bl || !id.startsWith(p)) continue;
      bl = p.length();
      best = k < names.length ? names[k] : "";
    }
  }
  return best == null || best.length() == 0 ? null : best;
}""")
M(shop, r"""
public static String classOf(String id) {
  return ownerOf(id, classNames());
}""")
# the page row name: "Berserker - Iron Battleaxe" (no class = the plain name)
M(shop, r"""
public static String rowName(String id) {
  String c = classOf(id);
  return c == null ? name(id) : c + " - " + name(id);
}""")
M(shop, r"""
public static boolean inBand(@PKG@.MerchZone z, int lv) {
  if (z == null) return false;
  if (z.lo <= 0 && z.hi <= 0) return true;
  return lv >= z.lo && lv <= z.hi;
}""")
# a fallback weapon's price: the median price of the zone's table weapons this visit; none = 150 x its level (at least 100)
M(shop, r"""
public static long fallbackPrice(java.util.ArrayList w, int lv) {
  if (w != null && w.size() > 0) {
    long[] a = new long[w.size()];
    for (int i = 0; i < a.length; i++) a[i] = ((@PKG@.MerchItem) w.get(i)).price;
    java.util.Arrays.sort(a);
    return a[a.length / 2];
  }
  return Math.max(100L, 150L * (long) lv);
}""")
M(shop, r"""
public static void entry(StringBuilder b, int cat, String id, long price, int stock) {
  if (b.length() > 0) b.append(',');
  b.append(cat).append(':').append(id).append(':').append(price).append(':').append(stock);
}""")
# the stock of one visit: "cat:id:price:left" comma separated (prices frozen for the visit). 0.1.1: one weapon per class first (class
# order), then up to merchant.offers random extras; no SkyyClasses / merchant.everyClass off = the 0.1 rule (offers random weapons)
M(shop, r"""
public static String restock(@PKG@.MerchZone z) {
  @PKG@.MerchItem[] all = @PKG@.MerchCfg.ITEMS;
  java.util.ArrayList w = new java.util.ArrayList();
  java.util.ArrayList rest = new java.util.ArrayList();
  for (int i = 0; i < all.length; i++) {
    @PKG@.MerchItem it = all[i];
    if (it.stock <= 0 || !it.inZone(z) || !@PKG@.MerchEng.itemOk(it.id) || @PKG@.MerchWall.why(it.id) != null) continue;
    if (it.cat == 0) w.add(it); else rest.add(it);
  }
  java.util.Collections.shuffle(w, RNG);
  StringBuilder b = new StringBuilder();
  // fixer: a zone whose table has no sellable weapon (cleared / all Stock 0) sells NO weapons, as in 0.1 - the class rule only tops up a live table
  String[] names = (@PKG@.MerchCfg.EVERY_CLASS && w.size() > 0) ? classNames() : new String[0];
  if (names.length == 0) {
    int n = Math.min(w.size(), Math.max(1, @PKG@.MerchCfg.OFFERS));
    for (int i = 0; i < n; i++) {
      @PKG@.MerchItem it = (@PKG@.MerchItem) w.get(i);
      entry(b, it.cat, it.id, it.price, it.stock);
    }
  } else {
    java.util.HashSet used = new java.util.HashSet();
    boolean[] taken = new boolean[w.size()];
    String[] wo = new String[w.size()];
    for (int i = 0; i < wo.length; i++) wo[i] = ownerOf(((@PKG@.MerchItem) w.get(i)).id, names);
    String[] fo = new String[FB_IDS.length];
    for (int i = 0; i < fo.length; i++) fo[i] = ownerOf(FB_IDS[i], names);
    long fp = -1L;
    for (int c = 0; c < names.length; c++) {
      int hit = -1;
      for (int i = 0; i < wo.length && hit < 0; i++) if (!taken[i] && names[c].equals(wo[i])) hit = i;
      if (hit >= 0) {
        taken[hit] = true;
        @PKG@.MerchItem it = (@PKG@.MerchItem) w.get(hit);
        used.add(it.id);
        entry(b, it.cat, it.id, it.price, it.stock);
        CLASS_PICKS = CLASS_PICKS + 1L;
        continue;
      }
      int[] cand = new int[FB_IDS.length];
      int nc = 0;
      for (int i = 0; i < FB_IDS.length; i++) {
        if (!names[c].equals(fo[i]) || used.contains(FB_IDS[i]) || !inBand(z, FB_LV[i])) continue;
        if (!@PKG@.MerchEng.itemOk(FB_IDS[i]) || @PKG@.MerchWall.why(FB_IDS[i]) != null) continue;
        cand[nc] = i;
        nc++;
      }
      if (nc == 0) {
        CLASS_MISSES = CLASS_MISSES + 1L;
        @PKG@.MerchLog.warnOnce("nocls:" + z.key + ":" + names[c], "the " + z.key + " merchant has no weapon for the " + names[c] + " class (none in its stock table, no vanilla " + names[c] + " weapon at " + z.band() + ") - add one: Server Setup > Merchants > Stock");
        continue;
      }
      int k = cand[RNG.nextInt(nc)];
      if (fp < 0L) fp = fallbackPrice(w, FB_LV[k]);
      used.add(FB_IDS[k]);
      entry(b, 0, FB_IDS[k], fp, 1);
      FALLBACK_PICKS = FALLBACK_PICKS + 1L;
    }
    int n = 0;
    int extras = Math.max(1, @PKG@.MerchCfg.OFFERS);
    for (int i = 0; i < w.size() && n < extras; i++) {
      @PKG@.MerchItem it = (@PKG@.MerchItem) w.get(i);
      if (taken[i] || used.contains(it.id)) continue;
      taken[i] = true;
      used.add(it.id);
      entry(b, it.cat, it.id, it.price, it.stock);
      n++;
    }
  }
  for (int i = 0; i < rest.size(); i++) {
    @PKG@.MerchItem it = (@PKG@.MerchItem) rest.get(i);
    entry(b, it.cat, it.id, it.price, it.stock);
  }
  return b.toString();
}""")
'''
rep("b", OLD_RESTOCK, NEW_RESTOCK)

# ---- the page: class rows read "<Class> - <name>"
rep("b", "    String nm = @PKG@.MerchShop.name(ic);\n", "    String nm = @PKG@.MerchShop.rowName(ic);   // 0.1.1: 'Berserker - Iron Battleaxe'\n")

# ---- the ready line names the rule
rep("b", '" s, " + (@PKG@.MerchCfg.ON ? "ON" : "OFF") + "; /merchants',
    '" s, " + (@PKG@.MerchCfg.ON ? "ON" : "OFF") + ", one weapon per class " + (@PKG@.MerchCfg.EVERY_CLASS ? "on" : "off") + " (" + @PKG@.MerchShop.FB_IDS.length + " vanilla fallbacks); /merchants')

open(os.path.join(D, "build_skyymerchants_0.1.1.py"), "w", encoding="utf8", newline="").write(S["b"].replace(LF, NLB))
print("wrote", os.path.join(D, "build_skyymerchants_0.1.1.py"))

# ============================================================================================================= harness
S["t"], NLT = load("test_skyymerchants_0.1.py")
rep("t", '"""Harness for SkyyMerchants 0.1 (NEW mod: roaming merchants). Build first: python SkyyMerchants/build_skyymerchants_0.1.py\n',
    '"""Harness for SkyyMerchants 0.1.1 (one weapon per class). Build first: python SkyyMerchants/build_skyymerchants_0.1.1.py\n'
    "GENERATED by tools/merchants_0_1_1_patch.py from test_skyymerchants_0.1.py - edit the patch, never this file.\n"
    "0.1.1 adds: CL = THE CLASS RULE in the core child (every class covered in all 4 zones with every pack id known, the vanilla fallback\n"
    "  with only vanilla known, missing SkyyClasses / switch off = the 0.1 rule, never a walled id, longest prefix, a Spellblade appears by\n"
    "  itself, the page row '<Class> - <name>', a 0.1 stock line still reads) + CC = CLASS COMPARE against SkyyMerchants-0.1.jar + the\n"
    "  class table this harness fakes = SkyyClasses' SET script.\n")
rep("t", "    python SkyyMerchants/test_skyymerchants_0.1.py [--jar <SkyyMerchants-0.1.jar>]",
    "    python SkyyMerchants/test_skyymerchants_0.1.1.py [--jar <SkyyMerchants-0.1.1.jar>]")
rep("t", 'VERSION = "0.1"\n', 'VERSION = "0.1.1"\nOLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.jar")\n')
rep("t", 'os.path.join(TOOLS, "dev", "scratch", "merch01", "test")', 'os.path.join(TOOLS, "dev", "scratch", "merch011", "test")')
rep("t", 'Scratch: tools/dev/scratch/merch01/test', 'Scratch: tools/dev/scratch/merch011/test')
rep("t", 'open(os.path.join(HERE, "build_skyymerchants_0.1.py"), encoding="utf-8")', 'open(os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION), encoding="utf-8")')

# the class table SkyyClasses publishes (checked against its SET script by the parent, CC)
CL_PARENT = r'''

# ====================================================================================================== 0.1.1: CC (parent)
CLASS_LIST = "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity,Assassin:Assassination,Monk:Zen"
CLASS_W = {"Archer": "Weapon_Shortbow_,Weapon_Crossbow_,Weapon_Arrow_", "Warrior": "Weapon_Sword_,Weapon_Longsword_,Weapon_Spear_",
           "Mage": "Weapon_Staff_,Halloween_Broomstick,Weapon_Spellbook_", "Berserker": "Weapon_Axe_,Weapon_Battleaxe_,Weapon_Mace_,Weapon_Club_",
           "Priest": "Weapon_Wand_,Weapon_Deployable_Healing_Totem", "Assassin": "Weapon_Daggers_,Weapon_Kunai",
           "Monk": "Weapon_Staff_Bo_,Weapon_Bo_,Weapon_Fist_"}
CLASS_FREE = "Weapon_Shield_"


def class_pin():
    for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
        if '("SkyyClasses", "' in l:
            return l.split('("SkyyClasses", "')[1].split('"')[0]
    return None


def part_classes():
    import re
    pin = class_pin()
    p = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_%s.py" % pin)
    check(pin and os.path.isfile(p), "CC: the SkyyClasses SET script exists (%s)" % pin)
    if not (pin and os.path.isfile(p)):
        return
    src = open(p, encoding="utf-8").read()
    got = {}
    for m in re.finditer(r'\{"name": "([A-Za-z]+)", "skill": "([A-Za-z]+)".*?"weapons": \[(.*?)\],\n', src, re.S):
        got[m.group(1)] = (m.group(2), ",".join(re.findall(r'\("([A-Za-z_]+)", "', m.group(3))))
    want = dict((n, (s, CLASS_W[n])) for n, s in (x.split(":") for x in CLASS_LIST.split(",")))
    check(got == want, "CC: the class list + weapon prefixes this harness fakes = SkyyClasses %s (got %s)" % (pin, got))
    check('("Weapon_Shield_", "shields")' in src.split("FREE_WEAPONS = [")[1].split("]")[0], "CC: SkyyClasses free prefixes = shields")
    check('b.put("class:list", @PKG@.ClassDefs.listText());' in src and 'b.put("class:weapons:" + @PKG@.ClassDefs.NAMES[i], @PKG@.ClassDefs.prefixesOf(i));' in src,
          "CC: SkyyClasses publishes class:list + class:weapons:<Class> as Strings")


def class_compare():
    if not os.path.isfile(OLD_JAR):
        check(False, "CC: SkyyMerchants-0.1.jar (the SET pin) is there to compare")
        return
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    co = dict((n, zo.read(n)) for n in zo.namelist() if n.endswith(".class"))
    cn = dict((n, zn.read(n)) for n in zn.namelist() if n.endswith(".class"))
    check(sorted(co) == sorted(cn), "CC: same class list as 0.1 (added %s removed %s)" % (sorted(set(cn) - set(co)), sorted(set(co) - set(cn))))
    changed = sorted(n.rsplit("/", 1)[1][:-6] for n in cn if n in co and co[n] != cn[n])
    print("CC. class compare 0.1 -> 0.1.1: %d classes, changed: %s" % (len(cn), ", ".join(changed)))
    must = {"MerchShop", "MerchEng", "MerchCfg", "MerchPage", "SkyyMerchantsPlugin"}
    allowed = must | {"CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask"}
    check(must <= set(changed) and set(changed) <= allowed, "CC: only the expected classes changed: %s" % changed)
    import re
    for n in ("MerchReg", "MerchSite", "MerchCore"):
        k = "com/skyy/merchants/%s.class" % n
        check(k in co and co.get(k) == cn.get(k), "CC: %s (saved data / registry / the second) is byte-identical to 0.1" % n)


# ====================================================================================================== 0.1.1: CL (core child)
def stock_of(s):
    return [x.split(":") for x in str(s).split(",") if x]


def xclass(K, c):
    import re
    from jpype import JClass
    Cfg, Shop, Eng, Log, br, bst, lines, CfgFn, TP, build, fakepr = (c["Cfg"], c["Shop"], c["Eng"], c["Log"], c["br"], c["bst"], c["lines"],
                                                                     c["CfgFn"], c["TP"], c["build"], c["fakepr"])
    Reg, sites = c["Reg"], c["sites"]
    HS = JClass("java.util.HashSet")
    fb = dict(zip([str(x) for x in Shop.FB_IDS], [int(x) for x in Shop.FB_LV]))
    K.check(len(fb) >= 40 and fb.get("Weapon_Sword_Iron") == 20 and fb.get("Weapon_Sword_Onyxium") == 50 and "Weapon_Arrow_Crude" not in fb
            and not any(i.startswith("Weapon_Shield_") for i in fb), "CL: the vanilla fallback pool (%d ids, Iron 20, Onyxium 50, no arrows / shields)" % len(fb))
    # ---- missing SkyyClasses = the 0.1 rule (no class:list)
    br.remove("class:list")
    K.check(len(Shop.classNames()) == 0 and Shop.classOf("Weapon_Sword_Iron") is None and str(Shop.rowName("Weapon_Sword_Frost")) == str(Shop.name("Weapon_Sword_Frost")),
            "CL: no SkyyClasses -> no classes, plain row names")
    z1, z2, z3, z4 = Cfg.zone("zone1"), Cfg.zone("zone2"), Cfg.zone("zone3"), Cfg.zone("zone4")
    tab = {}
    for it in Cfg.ITEMS:
        if int(it.cat) == 0:
            tab[str(it.id)] = it
    fp0 = int(Shop.FALLBACK_PICKS) + int(Shop.CLASS_PICKS)
    old = [stock_of(Shop.restock(z2)) for _ in range(20)]
    K.check(all(len(s) == min(4, len(s)) and len(s) >= 1 and len(s) <= 4 and all(e[1] in tab for e in s) for s in old)
            and int(Shop.FALLBACK_PICKS) + int(Shop.CLASS_PICKS) == fp0, "CL: no SkyyClasses = the 0.1 rule: up to merchant.offers table weapons, no class picks")
    # ---- SkyyClasses present
    br.put("class:list", CLASS_LIST)
    for n, p in CLASS_W.items():
        br.put("class:weapons:" + n, p)
    br.put("class:weapons:free", CLASS_FREE)
    br.put("class:weapons:unassigned", "Weapon_Bomb,Weapon_Gun,Flamethrower_,Weapon_Deployable_,Weapon_Claws_,Weapon_")
    names = [str(x) for x in Shop.classNames()]
    K.check(names == ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"], "CL: classNames from class:list: %s" % names)
    own = dict((i, Shop.classOf(i)) for i in ("Weapon_Staff_Bo_Wood", "Weapon_Staff_Iron", "Weapon_Shield_Iron", "Sword_Iron_Green", "Weapon_Kunai_Onyxium",
                                              "Weapon_Deployable_Healing_Totem", "Weapon_Deployable_Turret", "Weapon_Battleaxe_Iron_Blue", "Weapon_Bo_Iron",
                                              "Weapon_Spellbook_Iron", "Weapon_Wand_Iron", "Weapon_Crossbow_Thorium", None))
    own = dict((k, None if v is None else str(v)) for k, v in own.items())
    K.check(own == {"Weapon_Staff_Bo_Wood": "Monk", "Weapon_Staff_Iron": "Mage", "Weapon_Shield_Iron": None, "Sword_Iron_Green": None,
                    "Weapon_Kunai_Onyxium": "Assassin", "Weapon_Deployable_Healing_Totem": "Priest", "Weapon_Deployable_Turret": None,
                    "Weapon_Battleaxe_Iron_Blue": "Berserker", "Weapon_Bo_Iron": "Monk", "Weapon_Spellbook_Iron": "Mage", "Weapon_Wand_Iron": "Priest",
                    "Weapon_Crossbow_Thorium": "Archer", None: None},
            "CL: ownerOf = SkyyClasses' longest-prefix rule (Bo staff Monk, staff Mage, shield / recolour / turret nobody): %s" % own)
    K.check(str(Shop.rowName("Weapon_Battleaxe_Iron")).startswith("Berserker - ") and str(Shop.rowName("Weapon_Shield_Iron")) == str(Shop.name("Weapon_Shield_Iron")),
            "CL: rowName 'Berserker - <name>' / no class = the name: %s" % Shop.rowName("Weapon_Battleaxe_Iron"))
    # ---- every pack + SkyyArmory id known (the live server): every class in all 4 zones, from the table where it has one
    ext = HS()
    for i in tab:
        ext.add(i)
    Eng.EXTRA = ext

    def verify(z, runs, label, need, from_table=None):
        bad = []
        for _ in range(runs):
            s = stock_of(Shop.restock(z))
            ids = [e[1] for e in s]
            cls = [Shop.classOf(i) for i in ids]
            cls = [None if x is None else str(x) for x in cls]
            if len(ids) != len(set(ids)):
                bad.append("dup %s" % ids)
            for n in need:
                if n not in cls:
                    bad.append("no %s in %s" % (n, ids))
            # class picks come first, in class order
            head = cls[:len(need)]
            if head != list(need):
                bad.append("order %s" % head)
            for e in s:
                if not re.match(r"^[012]:[A-Za-z0-9_]+:\d+:\d+$", ":".join(e)):
                    bad.append("format %s" % e)
                i = e[1]
                if Shop.classOf(i) is not None and JClass(PKG + "MerchWall").why(i) is not None:
                    bad.append("walled %s" % i)
                if i in tab:
                    t = tab[i]
                    if not t.inZone(z) or int(e[2]) != int(t.price) or int(e[3]) != int(t.stock):
                        bad.append("table row wrong %s" % e)
                elif i in fb:
                    if not (int(z.lo) <= fb[i] <= int(z.hi)) or int(e[3]) != 1:
                        bad.append("fallback out of band / stock %s (%d)" % (e, fb[i]))
                else:
                    bad.append("unknown id %s" % i)
            if from_table is not None:
                for n in from_table:
                    picked = [i for i, c_ in zip(ids, cls) if c_ == n]
                    if not any(i in tab for i in picked):
                        bad.append("%s not from the table: %s" % (n, picked))
            extras = len(ids) - len(need)
            avail = len([i for i in tab if tab[i].inZone(z) and Eng.itemOk(i) and JClass(PKG + "MerchWall").why(i) is None]) - len([i for i in ids[:len(need)] if i in tab])
            if extras != min(int(Cfg.OFFERS), avail):
                bad.append("extras %d (avail %d)" % (extras, avail))
        K.check(not bad, "CL: %s: %s" % (label, bad[:4]))

    allc = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]
    l0 = len(lines)
    verify(z1, 40, "zone 1 (every pack known): all 7 classes, table where it can (Archer / Mage / Berserker / Priest / Monk), Warrior + Assassin vanilla Lv 1-20", allc,
           ["Archer", "Mage", "Berserker", "Priest", "Monk"])
    verify(z2, 40, "zone 2 (every pack known): all 7 classes from its table", allc, allc)
    verify(z3, 40, "zone 3 (every pack known): all 7 classes from its table", allc, allc)
    verify(z4, 40, "zone 4 (every pack known): all 7 classes from its table", allc, allc)
    K.check(not any("has no weapon for the" in str(x) for x in list(lines)[l0:]), "CL: no 'no weapon for a class' line with every pack known")
    s1 = stock_of(Shop.restock(z1))
    war = [e for e in s1 if str(Shop.classOf(e[1])) == "Warrior"]
    zp = sorted(int(tab[i].price) for i in tab if tab[i].inZone(z1))
    K.check(war and war[0][1] in fb and int(war[0][2]) == zp[len(zp) // 2] and war[0][3] == "1",
            "CL: zone 1 Warrior = a vanilla Lv 1-20 sword / longsword / spear at the median zone price (%d), stock 1: %s" % (zp[len(zp) // 2], war))
    # ---- only vanilla known (no pack installed): the fallback fills what it can; Priest / Monk have no vanilla metal weapon -> one log line
    Eng.EXTRA = None
    l0 = len(lines)
    mi0 = int(Shop.CLASS_MISSES)
    verify(z1, 30, "zone 1 (vanilla only): Archer table + Warrior / Mage / Berserker / Assassin vanilla", ["Archer", "Warrior", "Mage", "Berserker", "Assassin"], ["Archer"])
    miss = [str(x) for x in list(lines)[l0:] if "has no weapon for the" in str(x)]
    K.check(len(miss) == 2 and any("Priest" in m for m in miss) and any("Monk" in m for m in miss) and int(Shop.CLASS_MISSES) > mi0,
            "CL: vanilla only: Priest + Monk have nothing in zone 1 -> one WARN each (logged once): %s" % miss)
    for z, lab in ((z2, "zone 2"), (z3, "zone 3"), (z4, "zone 4")):
        s = stock_of(Shop.restock(z))
        cl = set(str(Shop.classOf(e[1])) for e in s)
        K.check({"Archer", "Warrior", "Mage", "Berserker", "Assassin"} <= cl and all(e[1] in tab or (e[1] in fb and int(z.lo) <= fb[e[1]] <= int(z.hi)) for e in s),
                "CL: %s vanilla only: the 5 classes with vanilla weapons covered, every id from the table or in band: %s" % (lab, [e[1] for e in s]))
    # ---- never walled: Mythic table row, Untiered + never-sell fallback ids
    Eng.EXTRA = ext
    bst["rarity"]["Weapon_Battleaxe_Iron_Blue"] = "mythic"
    bst["rarity"]["Weapon_Daggers_Iron"] = "untiered"
    bst["rarity"]["Weapon_Sword_Iron"] = "set"
    nv0 = str(Cfg.NEVER)
    CfgFn.cmdSetConsole("merchant.neverSell", nv0 + ",Weapon_Daggers_Copper,Weapon_Longsword_*")
    seen = set()
    lw = len(lines)
    for _ in range(40):
        for e in stock_of(Shop.restock(z1)):
            seen.add(e[1])
    walled = [i for i in seen if JClass(PKG + "MerchWall").why(i) is not None]
    K.check(not walled and not ({"Weapon_Battleaxe_Iron_Blue", "Weapon_Daggers_Iron", "Weapon_Sword_Iron", "Weapon_Daggers_Copper"} & seen)
            and not any(i.startswith("Weapon_Longsword_") for i in seen) and any(str(Shop.classOf(i)) == "Berserker" and i in fb for i in seen),
            "CL: never a walled id (Mythic table row -> Berserker from vanilla; Untiered / Set / never-sell fallbacks skipped): walled %s" % walled)
    K.check(not any(str(Shop.classOf(i)) == "Assassin" for i in seen) and len([x for x in list(lines)[lw:] if "for the Assassin class" in str(x)]) == 1,
            "CL: zone 1 with both vanilla Lv 1-20 daggers walled (and no table dagger) -> no Assassin pick, logged once")
    bst["rarity"].clear()
    CfgFn.cmdSetConsole("merchant.neverSell", nv0)
    # ---- a Spellblade appears by itself once SkyyClasses lists it (a longer prefix takes the Frost sword from the Warrior)
    br.put("class:list", CLASS_LIST + ",Spellblade:Spellcraft")
    br.put("class:weapons:Spellblade", "Weapon_Sword_Frost,Weapon_Spellblade_")
    verify(z2, 20, "zone 2 with a Spellblade listed: 8 classes, the Spellblade gets the Frost Sword (the Warrior then a vanilla Lv 20-30 one)",
           allc + ["Spellblade"], [c_ for c_ in allc if c_ != "Warrior"] + ["Spellblade"])
    sb = [e for e in stock_of(Shop.restock(z2)) if str(Shop.classOf(e[1])) == "Spellblade"]
    K.check([e[1] for e in sb] == ["Weapon_Sword_Frost"], "CL: the Spellblade's zone 2 pick = the Frost Sword: %s" % sb)
    s = stock_of(Shop.restock(z1))
    K.check("Spellblade" not in [str(Shop.classOf(e[1])) for e in s] and Log.ONCE.containsKey("nocls:zone1:Spellblade"),
            "CL: zone 1 has nothing for the Spellblade (no Frost Sword there) -> skipped + logged once")
    br.put("class:list", CLASS_LIST)
    br.remove("class:weapons:Spellblade")
    # ---- the switch: merchant.everyClass off = the 0.1 rule, live
    m = str(CfgFn.cmdSetConsole("merchant.everyClass", "false"))
    K.check(not bool(Cfg.EVERY_CLASS), "CL: merchant.everyClass off via the kit: %s" % m[:120])
    cp0 = int(Shop.CLASS_PICKS) + int(Shop.FALLBACK_PICKS)
    s = stock_of(Shop.restock(z1))
    K.check(1 <= len(s) <= 4 and int(Shop.CLASS_PICKS) + int(Shop.FALLBACK_PICKS) == cp0, "CL: switch off = up to merchant.offers random table weapons: %s" % s)
    CfgFn.cmdSetConsole("merchant.everyClass", "true")
    K.check(bool(Cfg.EVERY_CLASS), "CL: switch back on")
    # ---- offers 1 / 30
    CfgFn.cmdSetConsole("merchant.offers", "1")
    verify(z2, 10, "zone 2 offers=1: 7 class picks + 1 extra", allc, allc)
    CfgFn.cmdSetConsole("merchant.offers", "30")
    verify(z2, 10, "zone 2 offers=30: 7 class picks + every other table weapon", allc, allc)
    CfgFn.cmdSetConsole("merchant.offers", "4")
    # ---- a band-less zone (Levels 0) may use any level; inBand edges
    zx = JClass(PKG + "MerchZone").parse("zone9", "default|*|0", "|")
    K.check(Shop.inBand(zx, 50) and Shop.inBand(zx, 3) and Shop.inBand(z1, 20) and Shop.inBand(z1, 1) and not Shop.inBand(z1, 21) and not Shop.inBand(None, 5)
            and int(Shop.fallbackPrice(None, 20)) == 3000 and int(Shop.fallbackPrice(None, 0)) == 100, "CL: inBand edges + fallbackPrice with no table")
    fx0 = int(Shop.FALLBACK_PICKS) + int(Shop.CLASS_PICKS)
    sx = stock_of(Shop.restock(zx))
    K.check(not [e for e in sx if e[0] == "0"] and int(Shop.FALLBACK_PICKS) + int(Shop.CLASS_PICKS) == fx0,
            "CL (fixer): a zone with no table weapon rows sells NO weapons (no vanilla fallback), as in 0.1: %s" % [e[1] for e in sx])
    # fixer: zeroing every Stock of a zone's weapon rows stops its weapon sales (critic: the fallback used to refill it)
    zs = [it for it in Cfg.ITEMS if int(it.cat) == 0 and it.inZone(z2)]
    keep = [int(it.stock) for it in zs]
    for it in zs:
        it.stock = 0
    fx0 = int(Shop.FALLBACK_PICKS) + int(Shop.CLASS_PICKS)
    sz = [stock_of(Shop.restock(z2)) for _ in range(10)]
    for it, k in zip(zs, keep):
        it.stock = k
    K.check(len(zs) > 0 and all(not [e for e in s_ if e[0] == "0"] for s_ in sz) and int(Shop.FALLBACK_PICKS) + int(Shop.CLASS_PICKS) == fx0,
            "CL (fixer): zone 2 with every weapon row Stock 0 (%d rows) sells NO weapons, no vanilla fallback: %s" % (len(zs), sz[0]))
    # fixer: one sellable table weapon left = the class rule tops it up again (fallback for the other classes)
    for it in zs[1:]:
        it.stock = 0
    s1 = stock_of(Shop.restock(z2))
    for it, k in zip(zs, keep):
        it.stock = k
    K.check(len([e for e in s1 if e[0] == "0"]) >= 5 and str(zs[0].id) in [e[1] for e in s1],
            "CL (fixer): zone 2 with ONE weapon row left: that row + vanilla picks for the other classes: %s" % [e[1] for e in s1])
    # ---- the page: class rows read '<Class> - <name>', class picks first; a 0.1 stock line still reads
    a1 = Reg.find(sites, "zone1")
    a1.stock = "0:Weapon_Battleaxe_Iron:2500:1,0:Weapon_Shield_Iron:2000:1,0:Weapon_Sword_Frost:7500:0"
    pp = fakepr("ClassShopper")
    page = TP(pp, "default", "zone1", str(a1.uuid))
    b_, e_ = build(page)
    txt = " | ".join("%s=%s/%s" % (x.selector, x.data, x.text) for x in b_.getCommands())
    of = JClass(PKG + "MerchShop").offers(a1, 0)
    K.check(len(of[0]) == 3 and "Berserker - " in txt and "Warrior - " in txt and len(e_.getEvents()) == 6,
            "CL: page rows 'Berserker - ...' / 'Warrior - ...' (a 0.1-format stock line reads as before; 2 Buy + 4 base bindings): %d events" % len(e_.getEvents()))
    if "Berserker - " not in txt:
        K.notes.append("page commands: " + txt[:600])
    Eng.EXTRA = None

'''
rep("t", "\n\n# ====================================================================================================== children\n",
    CL_PARENT + "\n\n# ====================================================================================================== children\n")
rep("t", '''    K.notes.append("X log tail: " + " | ".join(str(x) for x in list(lines)[-6:]))
    P("CfgPub").shutdown()
''', '''    K.notes.append("X log tail: " + " | ".join(str(x) for x in list(lines)[-6:]))
    try:
        xclass(K, dict(locals()))   # 0.1.1: CL - the class rule on the same stand-in world + the REAL item store
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "CL: run crashed: %s" % str(e)[:400])
    P("CfgPub").shutdown()
''')
rep("t", '''    try:
        part_static()
''', '''    try:
        part_static()
        part_classes()     # 0.1.1 CC: the faked class table = SkyyClasses' SET script
        class_compare()    # 0.1.1 CC: 0.1 -> 0.1.1 class compare
''')
rep("t", """        check(len(h0) > 0 and not os.path.exists(os.path.join(home, "Skyy_SkyyMerchants")), "D: live mod data copied (%d files), no merchants folder yet" % len(h0))
""", """        had = os.path.exists(os.path.join(home, "Skyy_SkyyMerchants"))   # 0.1.1: SkyyMerchants 0.1 is deployed - its folder is usually there
        check(len(h0) > 0, "D: live mod data copied (%d files), merchants folder %s" % (len(h0), "there (0.1 deployed)" if had else "not there yet"))
""")
rep("t", """        check(new == [os.path.join("Skyy_SkyyMerchants", "config.properties")] and not changed,
              "D: start 1 writes only Skyy_SkyyMerchants/config.properties, every other file byte-identical (new %s changed %s)" % (new, changed))
""", """        want_new = [] if had else [os.path.join("Skyy_SkyyMerchants", "config.properties")]
        check(new == want_new and not changed,
              "D: start 1 writes %s, every other file byte-identical (new %s changed %s)" % (want_new or "nothing (0.1's files kept byte-identical)", new, changed))
""")
rep("t", """    K.check(P("MerchReg").sites("default") is not None, "D %s: the registry of world default reads (none yet)" % step)
""", """    K.check(P("MerchReg").sites("default") is not None, "D %s: the registry of world default reads" % step)
    cfgt = open(os.path.join(home, "Skyy_SkyyMerchants", "config.properties"), encoding="latin-1").read()
    K.check(bool(P("MerchCfg").EVERY_CLASS) and (("merchant.everyClass=true" in cfgt) or ("merchant.everyClass" not in cfgt)),
            "D %s: one weapon per class is ON (a 0.1 config.properties has no merchant.everyClass line = the default; nothing rewritten)" % step)
""")
open(os.path.join(D, "test_skyymerchants_0.1.1.py"), "w", encoding="utf8", newline="").write(S["t"].replace(LF, NLT))
print("wrote", os.path.join(D, "test_skyymerchants_0.1.1.py"))
