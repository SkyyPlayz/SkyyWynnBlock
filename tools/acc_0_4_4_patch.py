"""Derive SkyyAccessories/build_skyyaccessories_0.4.4.py from 0.4.3 (same style as acc_0_4_3_patch.py: rep(old, new) with asserted
anchors, newline-agnostic; 0.4.3 stays untouched, its line endings are preserved).
0.4.4 = ADMIN CONFIG IN GAME (Skyy's rule: "everything a server owner might change must be doable in game, config files stay and always
match"; research/Server-Setup-Spec.md 4.14 + 7, tools/CONFIG-CONTRACT.md, the kit tools/skyycfg.py). The mod gets its FIRST config file.
 1. Skyy_SkyyAccessories/config.properties (next to bags/), written by the mod on its first start with TODAY'S values, so nothing
    changes until an admin changes something:
      slots=9                      bag slots a player can fill (1-9)
      regenEverySeconds=2          how often the Regeneration talisman heals (1-30 s)
      bonus.<Family>=c,u,r,e,l     talisman percent per rarity Common..Legendary (0-100, up to 2 decimals), one line per family:
                                   Vitality/Endurance/Intelligence 2,4,6,8,10, Regeneration 0.5,1,1.5,2,3, Speed 2,4,6,8,10
    The defaults are generated from the SAME Python numbers the item tooltips print (CAP, REGEN_EVERY, TALISMANS) and the build asserts
    that the floats the loader computes equal the 0.4.3 float literals, so the running numbers are bit-identical by default.
 2. Rows (SkyWynn Menu -> Server Setup -> Accessories, SkyyMenu 0.3; key = file key):
      slots              int 9, 1-9, step 1   new,danger  field:AccStore.SLOTS;confirm=down (asks only when LOWERED)
      regenEverySeconds  int 2, 1-30 s        live,adv    field:AccDefs.REGEN_EVERY
      bonus              table (entry = talisman family, one text column "Common..Legendary %"), live,danger,
                         reload@config.properties:bonus. + check=AccCfg.checkBonus (the 5 families only, 5 percents 0-100, no removal)
    RELOAD = AccCfg.reload (the mod's own loader, also run for hand edits); config:def / config:fn:SkyyAccessories are published by
    CfgPub.start as the LAST statement of setup(), after AccCfg.load(true). CfgPub.shutdown() in shutdown().
 3. slots semantics ("new" = new equips only; spec: "a lowered cap hides slots but never deletes what is in them"): AccStore.CAP stays
    the STORAGE size 9 (bag files slot0..slot8, the page loop, the un:<i> buttons), AccStore.SLOTS (volatile) is the server limit.
    Equip only looks for a FREE slot below SLOTS (canEquipK + equipK); an upgrade of an accessory already in the bag still replaces it
    in place, wherever it sits; the stash safety net (an item that could not be handed back) still uses any slot so nothing vanishes.
    Accessories already in a slot at or above the limit stay, keep counting and can be unequipped: the page hides only EMPTY slots
    above the limit. With the default 9 every loop is exactly the 0.4.3 loop.
    (The spec's field audit says "remove final from CAP"; CAP sizes the stored arrays, so a separate volatile SLOTS is used instead.)
 4. REGEN_EVERY and the talisman arrays VIT / END / INT / REG / SPD in AccDefs lose `final` (volatile); the loader swaps in whole new
    arrays (index 0 = 0, 1..5 = Common..Legendary; SPD = percent / 100). Everything that reads them (AccEffects, bonusText on the bag page)
    picks the new numbers up on its next read - no periodic work added.
 5. The loader (AccCfg.load) clamps like every Skyy loader: slots 1-9, regenEverySeconds 1-30, each percent 0-100; a bad or missing line
    falls back to the built-in value with one warning; an unreadable file keeps the current settings on a reload. One INFO line whenever
    this server's numbers differ from what the item tooltips print (they are assets: built-in numbers until a rebuild).
 6. EXTRA: /accessories reload - server admins only (requirePermission skyyaccessories.admin + setPermissionGroups(new String[0]) so it
    does not inherit /accessories' hytale:Adventurer - the SkyyIslands 0.5 leak, lint rule perm_group_leaks). It calls the kit's reload op
    (via=command): hand edits of config.properties are applied, logged and versioned without SkyyMenu. Plain /accessories is unchanged.
 7. No player Settings switches: Settings-Spec 3.13 lists SkyyAccessories under "No change" (its only chat line, the retired-accessory
    refusal, is a reply to the player's own click).
Unchanged: every 0.4.3 behaviour (Campfire quick cook + live factors, retired Alchemy/Cooking Bench, per-profile bags, Omni, talisman
effects, movement protocol, acc:has / acc:tal / acc:fn:has), all item assets and recipes (upgrade recipes + rarity colours stay assets).
Run:  python tools/acc_0_4_4_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.4.4.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.3.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.3"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.4.3 - build script (derived from 0.4.2 by tools/acc_0_4_3_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.3.py            -> SkyyAccessories/SkyyAccessories-0.4.3.jar
       python build_skyyaccessories_0.4.3.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.3: the CAMPFIRE accessory is BACK''', '''"""SkyyAccessories 0.4.4 - build script (derived from 0.4.3 by tools/acc_0_4_4_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.4.py            -> SkyyAccessories/SkyyAccessories-0.4.4.jar
       python build_skyyaccessories_0.4.4.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.4: ADMIN CONFIG IN GAME (research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md; full notes in tools/acc_0_4_4_patch.py):
     - FIRST config file Skyy_SkyyAccessories/config.properties, written on the first start with today's values: slots=9,
       regenEverySeconds=2, bonus.<Family>=<Common..Legendary percents> (the numbers the talisman tooltips print).
     - SkyWynn Menu -> Server Setup -> Accessories (SkyyMenu 0.3) edits them through the kit (tools/skyycfg.py): validated, logged in
       config-changes.log, versioned in config-history/, written back line by line. config:def/fn:SkyyAccessories published LAST in setup().
     - slots limits NEW equips only: accessories already in a higher slot stay, keep counting and can be unequipped (the page hides only
       empty slots above the limit). The bonus table and the regeneration interval apply at once.
     - /accessories reload (skyyaccessories.admin only, groups cleared) re-reads the file after hand edits (logged via=command).
     - Item tooltips keep the built-in numbers (assets); the bag page's Bonuses line shows the live ones.
0.4.3 notes:
0.4.3: the CAMPFIRE accessory is BACK''')
rep('VERSION = "0.4.3"\n', 'VERSION = "0.4.4"\n')
rep('''import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyySkills 0.2)
''', '''import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyySkills 0.2)
import skyycfg as CFG   # 0.4.4: the admin config kit (research/Server-Setup-Spec.md 1.3-1.4, tools/CONFIG-CONTRACT.md)
''')

# ---------------------------------------------------------------- probes + new classes
rep('''
PKG = "com.skyy.accessories"
''', '''# 0.4.4: /accessories reload (admin sub-command, groups cleared) + the kit's reload op with the admin's name
for c, m in ((ACM, "requirePermission"), (ACM, "addSubCommand"), (ACM, "setPermissionGroups"), (PR, "getUsername"), (PR, "getUuid"),
             (PR, "sendMessage")):
    B.probe(pool, c, m)

PKG = "com.skyy.accessories"
''')
rep('''pl   = pool.makeClass(PKG + ".SkyyAccessoriesPlugin", pool.get(JP))
''', '''pl   = pool.makeClass(PKG + ".SkyyAccessoriesPlugin", pool.get(JP))
cfg_ = pool.makeClass(PKG + ".AccCfg")                         # 0.4.4: config.properties loader + the kit's hooks
rcmd = pool.makeClass(PKG + ".AccReloadCmd", pool.get(APC))    # 0.4.4: /accessories reload (server admins only)
''')

# ---------------------------------------------------------------- config defaults (python side) = today's numbers
rep('''FAM = dict((t[0], i) for i, t in enumerate(TALISMANS))
''', r'''FAM = dict((t[0], i) for i, t in enumerate(TALISMANS))
# ---- 0.4.4 ADMIN CONFIG (research/Server-Setup-Spec.md 4.14): the mod's FIRST config file, Skyy_SkyyAccessories/config.properties.
# Its defaults ARE today's numbers - CAP, REGEN_EVERY and the TALISMANS percents, the same values the item tooltips print - so nothing
# changes until an admin changes something. The file is written by AccCfg.writeDefaults on the first start and is also the kit's DEFAULTS.
REGEN_MAX = 30
def _pcts(vals):
    return ",".join("%g" % v for v in vals)
BONUS_DEF = [_pcts(t[4]) for t in TALISMANS]   # index = AccDefs.FAMILIES (TALISMANS order)
assert BONUS_DEF == ["2,4,6,8,10", "2,4,6,8,10", "2,4,6,8,10", "0.5,1,1.5,2,3", "2,4,6,8,10"], BONUS_DEF
# the loader computes (float) (percent / div) from the parsed text; 0.4.3 compiled the "%.4ff" literals of jfloats - both must give the
# same float32 for every default, so the running numbers are bit-identical until an admin changes one
import struct as _st
def _f32(x):
    return _st.unpack("<f", _st.pack("<f", x))[0]
for _t, _txt in zip(TALISMANS, BONUS_DEF):
    _div, _sc = (100.0, 0.01) if _t[0] == "Speed" else (1.0, 1.0)
    for _v, _p in zip(_t[4], _txt.split(",")):
        assert _f32(float(_p) / _div) == _f32(float("%.4f" % (_v * _sc))), (_t[0], _v, _p)
    assert all(0 <= _v <= 100 and round(_v, 2) == _v for _v in _t[4]), _t[0]
CONFIG_TEXT = "\n".join([
    "# SkyyAccessories settings. Change them in game: SkyWynn Menu -> Server Setup -> Accessories (SkyyMenu 0.3), or edit this file",
    "# and run /accessories reload (server admins: skyyaccessories.admin). Every change is logged in config-changes.log.",
    "#",
    "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP,
    "# keep counting and can still be unequipped - only a newly equipped accessory needs a free slot within the limit.",
    "slots=%d" % CAP,
    "# How often the Regeneration talisman heals, in seconds (1-%d)." % REGEN_MAX,
    "regenEverySeconds=%d" % REGEN_EVERY,
    "# Talisman bonuses in percent for Common,Uncommon,Rare,Epic,Legendary (0-100 each, up to 2 decimals), one line per family.",
    "# Vitality / Endurance / Intelligence = percent of your flat max Health / Stamina / Mana, Regeneration = percent of max Health",
    "# healed every regenEverySeconds, Speed = percent movement speed. The item tooltips keep printing the built-in numbers",
    "# (%s, Regeneration %s); the Accessory Bag page shows the ones below." % (BONUS_DEF[FAM["Vitality"]], BONUS_DEF[FAM["Regeneration"]]),
] + ["bonus.%s=%s" % (t[0], BONUS_DEF[i]) for i, t in enumerate(TALISMANS)] + [""])
assert all(ord(ch) < 128 for ch in CONFIG_TEXT), "config text must stay ASCII"
def jlit(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
def JX(src):
    return src.replace("@PKG@", PKG)
''')

# ---------------------------------------------------------------- AccDefs: talisman numbers + regen interval become configurable
for fam_, arr_ in (("Vitality", "VIT"), ("Endurance", "END"), ("Intelligence", "INT"), ("Regeneration", "REG")):
    rep('''dfs.addField(CtField.make('public static final float[] %s = new float[] { %%s };' %% jfloats(TALISMANS[FAM["%s"]][4]), dfs))''' % (arr_, fam_),
        '''dfs.addField(CtField.make('public static volatile float[] %s = new float[] { %%s };' %% jfloats(TALISMANS[FAM["%s"]][4]), dfs))   # 0.4.4: AccCfg.load swaps it''' % (arr_, fam_))
rep('''dfs.addField(CtField.make('public static final float[] SPD = new float[] { %s };' % jfloats(TALISMANS[FAM["Speed"]][4], 0.01), dfs))''',
    '''dfs.addField(CtField.make('public static volatile float[] SPD = new float[] { %s };' % jfloats(TALISMANS[FAM["Speed"]][4], 0.01), dfs))   # 0.4.4: AccCfg.load swaps it''')
rep('''dfs.addField(CtField.make('public static final int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))''',
    '''dfs.addField(CtField.make('public static volatile int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))   # 0.4.4: config row regenEverySeconds (kit field:)''')

# ---------------------------------------------------------------- AccStore: SLOTS = the server limit for NEW equips
rep('''st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
''', '''st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
# 0.4.4: CAP stays the STORAGE size (bag files slot0..slot8, the page loop, the un:<i> buttons); SLOTS = this server's limit for NEW
# equips (config row slots, kit field:). Accessories already in a slot >= SLOTS stay, keep counting and can be unequipped.
st_.addField(CtField.make("public static volatile int SLOTS = %d;" % CAP, st_))
''')
rep('''# would equip(u, id) take the item? same rule as equip - asked BEFORE the item leaves the inventory
''', '''# 0.4.4: the number of slots a NEW accessory may go into (SLOTS clamped to 1..the bag's length); = s.length with the default 9
st_.addMethod(CtNewMethod.make("""
public static int capOf(String[] s) {
  int c = SLOTS;
  if (c < 1) c = 1;
  if (s != null && c > s.length) c = s.length;
  return c;
}""", st_))
# would equip(u, id) take the item? same rule as equip - asked BEFORE the item leaves the inventory
''')
rep('''    for (int i = 0; i < s.length; i++) if (s[i] == null) return true;
    return false;''', '''    int cap = capOf(s);   // 0.4.4: a free slot below this server's limit (an in-place upgrade above is still fine)
    for (int i = 0; i < cap; i++) if (s[i] == null) return true;
    return false;''')
rep('''    for (int i = 0; i < s.length; i++) if (s[i] == null) {{ s[i] = id; saveK(u, k); return ""; }}''',
    '''    int cap = capOf(s);   // 0.4.4: new accessories only go below this server's limit (canEquipK asks the same)
    for (int i = 0; i < cap; i++) if (s[i] == null) {{ s[i] = id; saveK(u, k); return ""; }}''')

# ---------------------------------------------------------------- AccCfg (loader + hooks) and the kit, before AccFn
rep('''# ================= AccFn (bridge function acc:fn:has) =================
''', r'''# ================= AccCfg (0.4.4): config.properties - loader, first-run file, the kit's RELOAD routine and check hook =================
cfg_.addField(CtField.make("public static java.nio.file.Path FILE;", cfg_))
cfg_.addField(CtField.make("public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT), cfg_))
cfg_.addField(CtField.make("public static final String[] BONUS_DEF = new String[] { %s };" % ", ".join('"%s"' % v for v in BONUS_DEF), cfg_))
cfg_.addField(CtField.make('public static volatile String TIP_SEEN = "";', cfg_))   # the last "differs from the tooltips" text logged
for _src in [
r"""
public static void info(String msg) {
  try { if (@PKG@.AccStore.LOG != null) @PKG@.AccStore.LOG.at(java.util.logging.Level.INFO).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""",
# first start: the file with the built-in values (never overwrites; an existing file - even a broken one - is left alone)
r"""
public static void writeDefaults() {
  try {
    if (FILE == null || java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
    info("wrote the first config.properties with the built-in settings: " + FILE);
  } catch (Throwable t) { @PKG@.AccStore.warn("could not write the default config.properties: " + t); }
}""",
# one percent: digits with at most one '.', up to 2 decimals (no signs, exponents, NaN or Infinity); -1 = not a percent
r"""
public static double num(String t) {
  if (t == null) return -1.0;
  String x = t.trim();
  if (x.length() == 0 || x.length() > 12) return -1.0;
  int dot = -1;
  for (int i = 0; i < x.length(); i++) {
    char c = x.charAt(i);
    if (c == '.') {
      if (dot >= 0 || i == 0 || i == x.length() - 1) return -1.0;
      dot = i;
    } else if (c < '0' || c > '9') return -1.0;
  }
  if (dot >= 0 && x.length() - dot - 1 > 2) return -1.0;
  try { return Double.parseDouble(x); } catch (Throwable e) { return -1.0; }
}""",
# "2,4,6,8,10" -> the 5 percents Common..Legendary, or null when it is not exactly 5 percents
r"""
public static double[] parseRow(String v) {
  if (v == null) return null;
  String[] p = v.split(",", -1);
  if (p.length != 5) return null;
  double[] out = new double[5];
  for (int i = 0; i < 5; i++) {
    double x = num(p[i]);
    if (x < 0.0) return null;
    out[i] = x;
  }
  return out;
}""",
r"""
public static boolean sameRow(double[] a, double[] b) {
  if (a == null || b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) if (Math.abs(a[i] - b[i]) > 0.0000001) return false;
  return true;
}""",
r"""
public static String dtext(double v) {
  long c = Math.round(v * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  if (c % 10L == 0L) return String.valueOf(c / 100L) + "." + String.valueOf((c % 100L) / 10L);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""",
r"""
public static String rowText(double[] r) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < r.length; i++) { if (i > 0) sb.append(','); sb.append(dtext(r[i])); }
  return sb.toString();
}""",
# the AccDefs array layout: index 0 = no talisman, 1..5 = Common..Legendary; Speed is stored as a fraction (div 100)
r"""
public static float[] row(double[] v, double div) {
  float[] o = new float[6];
  o[0] = 0.0f;
  for (int i = 0; i < 5; i++) o[i + 1] = (float) (v[i] / div);
  return o;
}""",
# whole number from the file, clamped like the kit validates (the kit logs a clamped field: row itself)
r"""
public static int intIn(String v, int def, int lo, int hi, String key) {
  if (v == null) return def;
  int n = def;
  try { n = Integer.parseInt(v.trim()); }
  catch (Throwable t) { @PKG@.AccStore.warn("config.properties: " + key + "=" + v.trim() + " is not a whole number - " + def + " is used"); return def; }
  if (n < lo) { @PKG@.AccStore.warn("config.properties: " + key + "=" + n + " is below " + lo + " - " + lo + " is used"); return lo; }
  if (n > hi) { @PKG@.AccStore.warn("config.properties: " + key + "=" + n + " is above " + hi + " - " + hi + " is used"); return hi; }
  return n;
}""",
r"""
public static double[] bonusIn(String v, int f) {
  double[] d = parseRow(BONUS_DEF[f]);
  if (v == null) return d;
  String k = "bonus." + @PKG@.AccDefs.FAMILIES[f];
  double[] r = parseRow(v);
  if (r == null) {
    @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " is not 5 percents like " + BONUS_DEF[f] + " (Common,Uncommon,Rare,Epic,Legendary) - the built-in numbers are used");
    return d;
  }
  boolean cl = false;
  for (int i = 0; i < 5; i++) if (r[i] > 100.0) { r[i] = 100.0; cl = true; }
  if (cl) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " has a percent above 100 - 100 is used there");
  return r;
}""",
# the mod's loader: setup() (first = true: writes the default file first) and the kit's RELOAD after every save / hand edit
r"""
public static String load(boolean first) {
  if (first) writeDefaults();
  java.util.Properties p = new java.util.Properties();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    if (!first) {
      @PKG@.AccStore.warn("config.properties could not be read - the current settings stay: " + t);
      return "config.properties could not be read - the current settings stay";
    }
    @PKG@.AccStore.warn("config.properties could not be read - the built-in settings are used: " + t);
    p = new java.util.Properties();
  }
  int sl = intIn(p.getProperty("slots"), @CAP@, 1, @CAP@, "slots");
  int rg = intIn(p.getProperty("regenEverySeconds"), @REGEN@, 1, @RMAX@, "regenEverySeconds");
  Object[] bo = new Object[@NF@];
  StringBuilder bt = new StringBuilder();
  for (int f = 0; f < @NF@; f++) {
    double[] r = bonusIn(p.getProperty("bonus." + @PKG@.AccDefs.FAMILIES[f]), f);
    bo[f] = r;
    if (!sameRow(r, parseRow(BONUS_DEF[f]))) bt.append(", ").append(@PKG@.AccDefs.FAMILIES[f]).append(' ').append(rowText(r));
  }
  @PKG@.AccStore.SLOTS = sl;
  @PKG@.AccDefs.REGEN_EVERY = rg;
  @PKG@.AccDefs.VIT = row((double[]) bo[@V@], 1.0);
  @PKG@.AccDefs.END = row((double[]) bo[@E@], 1.0);
  @PKG@.AccDefs.INT = row((double[]) bo[@I@], 1.0);
  @PKG@.AccDefs.REG = row((double[]) bo[@R@], 1.0);
  @PKG@.AccDefs.SPD = row((double[]) bo[@S@], 100.0);
  StringBuilder tip = new StringBuilder();
  if (sl != @CAP@) tip.append(", ").append(sl).append(" bag slots");
  if (rg != @REGEN@) tip.append(", Regeneration every ").append(rg).append(" s");
  tip.append(bt.toString());
  String ts = "";
  if (tip.length() > 0) ts = tip.substring(2);
  if (!ts.equals(TIP_SEEN)) {
    TIP_SEEN = ts;
    if (ts.length() > 0) info("this server's accessory settings differ from what the item tooltips print (built-in numbers - the Accessory Bag page shows the live ones): " + ts);
  }
  String bs = "built-in";
  if (bt.length() > 0) bs = "custom (" + bt.substring(2) + ")";
  return "config " + sl + " bag slots, Regeneration every " + rg + " s, talisman bonuses " + bs;
}""",
# RELOAD routine of the kit (runs on its save task after the atomic write, outside every kit lock; only parses the file into fields)
r"""
public static String reload() {
  String r = load(false);
  info("config.properties applied: " + r);
  return r;
}""",
# check= hook of the bonus table: key = bonus[<entry>], value = the canonical text, null = a removal
r"""
public static String checkBonus(String key, String value) {
  String fam = key == null ? "" : key;
  int a = fam.indexOf('[');
  int b = fam.lastIndexOf(']');
  if (a >= 0 && b > a) fam = fam.substring(a + 1, b);
  int f = @PKG@.AccDefs.familyIndex(fam);
  if (f < 0) return "Only the talisman families have bonuses: Vitality, Endurance, Intelligence, Regeneration, Speed (spelled like that).";
  if (value == null) return "The " + fam + " line stays - set it to " + BONUS_DEF[f] + " to go back to the built-in numbers.";
  double[] r = parseRow(value);
  if (r == null) return "Needs 5 percents for Common,Uncommon,Rare,Epic,Legendary like " + BONUS_DEF[f] + " (0-100, up to 2 decimals).";
  for (int i = 0; i < 5; i++) if (r[i] > 100.0) return "Each percent must be from 0 to 100 - " + @PKG@.AccDefs.RARITY[i + 1] + " is " + dtext(r[i]) + ".";
  return null;
}""",
]:
    _src = JX(_src).replace("@CAP@", str(CAP)).replace("@REGEN@", str(REGEN_EVERY)).replace("@RMAX@", str(REGEN_MAX)) \
        .replace("@NF@", str(len(TALISMANS))).replace("@V@", str(FAM["Vitality"])).replace("@E@", str(FAM["Endurance"])) \
        .replace("@I@", str(FAM["Intelligence"])).replace("@R@", str(FAM["Regeneration"])).replace("@S@", str(FAM["Speed"]))
    assert "@" not in _src.replace("@PKG@", ""), _src[:80]
    cfg_.addMethod(CtNewMethod.make(_src, cfg_))

# ================= the admin config kit (0.4.4; research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md) =================
# (key, label, cat, type, default, min, max, opts, unit, flags, help, bind) - row key = file key (spec 7: the file key never changes)
CFG_CATS = [("bag", "Accessory Bag"), ("talismans", "Talismans")]
CFG_ROWS = [
    ("slots", "Accessory slots", "bag", "int", str(CAP), "1", str(CAP), "step=1", "", "new,danger",
     "Lowering it deletes nothing: accessories already in higher slots stay and count until taken out.",
     "field:AccStore.SLOTS@config.properties:slots;confirm=down"),
    ("regenEverySeconds", "Regeneration heals every", "talismans", "int", str(REGEN_EVERY), "1", str(REGEN_MAX), "step=1", "s", "live,adv",
     "How often the Regeneration talisman heals. Its item tooltip keeps saying %d seconds." % REGEN_EVERY,
     "field:AccDefs.REGEN_EVERY@config.properties:regenEverySeconds"),
    ("bonus", "Talisman bonuses", "talismans", "table", "", "", "", "text;type;Common..Legendary %", "", "live,danger",
     "Percent per rarity Common,Uncommon,Rare,Epic,Legendary. Item tooltips keep the built-in numbers.",
     "reload@config.properties:bonus.;check=AccCfg.checkBonus"),
]
CFG_NOTE = "Item tooltips show the built-in numbers - the Accessory Bag page shows this server's."
kit = CFG.emit(pool, PKG, MOD="SkyyAccessories", TITLE="Accessories", VERSION=VERSION, NODE="skyyaccessories.admin", CATS=CFG_CATS,
               ROWS=CFG_ROWS, FILES=["Skyy_SkyyAccessories/config.properties"], NOTE=CFG_NOTE, RELOAD="AccCfg.reload", KEEP=20,
               DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= AccFn (bridge function acc:fn:has) =================
''')

# ---------------------------------------------------------------- page: empty slots above this server's limit are hidden
rep('''  for (int i = 0; i < s.length; i++) {{
    b.appendInline("#SkyyAcc", "Group #SkyyAccSlot" + i''', '''  int cap = {PKG}.AccStore.capOf(s);   // 0.4.4
  for (int i = 0; i < s.length; i++) {{
    if (i >= cap && s[i] == null) continue;   // 0.4.4: a slot above this server's limit shows only while something is still in it
    b.appendInline("#SkyyAcc", "Group #SkyyAccSlot" + i''')

# ---------------------------------------------------------------- /accessories reload (server admins only) + the sub-command
rep('''# ================= /accessories =================
''', '''# ================= /accessories reload (0.4.4, server admins only) =================
# COMMAND RULES: an admin sub-command under a player command needs requirePermission AND setPermissionGroups(new String[0]) - otherwise
# the engine copies skyyaccessories.admin into /accessories' hytale:Adventurer group (the SkyyIslands 0.5 leak; lint perm_group_leaks).
# The kit's reload op re-checks the node too (denied), reads the file on this thread and the save task runs AccCfg.reload.
rcmd.addConstructor(CtNewConstructor.make("""
public AccReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyAccessories/config.properties after hand edits");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
}""", rcmd))
rcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "reload", pr.getUuid(), pr.getUsername(), "command" }});
    String m = "could not reload - see the server log";
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) m = String.valueOf(((Object[]) o)[2]);
    pr.sendMessage({MSG}.raw("[Accessories] " + m));
  }} catch (Throwable t) {{
    {PKG}.AccStore.warn("/accessories reload failed: " + t);
    pr.sendMessage({MSG}.raw("[Accessories] could not reload - see the server log"));
  }}
}}""", rcmd))

# ================= /accessories =================
''')
rep('''  setPermissionGroups(new String[] { "hytale:Adventurer" });   // 0.4: COMMAND RULES - ordinary players lack the auto node
}""", cmd))''', '''  setPermissionGroups(new String[] { "hytale:Adventurer" });   // 0.4: COMMAND RULES - ordinary players lack the auto node
  addSubCommand(new com.skyy.accessories.AccReloadCmd());   // 0.4.4: server admins only (its own groups are cleared)
}""", cmd))''')

# ---------------------------------------------------------------- plugin: load the config first, publish config:def/fn LAST
rep('''  {PKG}.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
''', '''  {PKG}.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
  {PKG}.AccCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("config.properties");   // 0.4.4
  String cs = {PKG}.AccCfg.load(true);   // 0.4.4: the first start writes the file with the built-in (0.4.3) values
''')
rep('''one bag per profile when SkyyProfiles runs" );
}}""" % (''', '''one bag per profile when SkyyProfiles runs; " + cs + "; admin settings: SkyWynn Menu -> Server Setup -> Accessories or /accessories reload");
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());   // 0.4.4: config:def / config:fn:SkyyAccessories - LAST, after the config load
}}""" % (''')
rep('''  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  super.shutdown();''', '''  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  try { com.skyy.accessories.CfgPub.shutdown(); } catch (Throwable t) { }   // 0.4.4: pending config saves + change-log lines now
  super.shutdown();''')
rep('''for c in (dfs, st_, fn, page, fac, cmd, tick, eff, pl, mvs_):
    c.writeFile(OUT)
print("classes written")''', '''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_):
    c.writeFile(OUT)
kit.write(OUT)   # 0.4.4: deferred kit checks (AccCfg.reload / checkBonus exist with the right signatures), then the 7 kit classes
print("classes written (+%d config kit)" % len(kit.classes))''')

# ---------------------------------------------------------------- manifest
rep('''the Alchemy Bench and Cooking Bench accessories are retired (Alchemy and Cooking are table-only). Zero dependencies."''',
    '''the Alchemy Bench and Cooking Bench accessories are retired (Alchemy and Cooking are table-only); bag slots, the regeneration interval and the talisman bonuses are server settings (config.properties, editable in game through SkyWynn Menu -> Server Setup). Zero dependencies."''')

# ---------------------------------------------------------------- self-checks on the generated script
assert 'VERSION = "0.4.4"' in s and "import skyycfg as CFG" in s
assert s.count("public static final float[]") == 0 and s.count("public static volatile float[]") == 5
assert "public static volatile int REGEN_EVERY" in s and "public static volatile int SLOTS" in s
assert "public static final int CAP = %d;" in s, "CAP stays the storage size"
assert s.count("int cap = capOf(s);") == 2 and s.count("capOf(s);   // 0.4.4") == 1 + 2
assert "for (int i = 0; i < s.length; i++) if (s[i] == null) { s[i] = id; saveK(u, k); return true; }" in s, "stash safety net unchanged"
assert s.index("public static int capOf(String[] s)") < s.index("public static boolean canEquipK("), "javassist: methods before callers"
assert s.index("cfg_.addMethod(CtNewMethod.make(_src, cfg_))") < s.index("kit = CFG.emit(") < s.index("# ================= AccFn")
assert s.index("rcmd.addConstructor(") < s.index("cmd.addConstructor(CtNewConstructor.make(\"\"\"\npublic AccCmd()"), "sub-command first"
assert s.index("{PKG}.AccCfg.load(true)") < s.index("{PKG}.CfgPub.start(") < s.index("pl.addMethod(CtNewMethod.make(\"\"\"\nprotected void shutdown()")
assert s.index("{PKG}.CfgPub.start(") > s.index("getLogger().at(java.util.logging.Level.INFO).log(\"[SkyyAccessories] {VERSION} ready"), "CfgPub.start LAST"
assert 'requirePermission("skyyaccessories.admin");\n  setPermissionGroups(new String[0]);' in s
assert s.count("kit.write(OUT)") == 1
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.3
print("wrote", dst)
