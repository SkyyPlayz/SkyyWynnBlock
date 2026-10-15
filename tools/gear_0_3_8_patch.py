"""Derive SkyyGear/build_skyygear_0.3.8.py from the LIVE 0.3.7 (build_skyygear_0.3.7.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_7_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_8_patch.py      then      python SkyyGear/build_skyygear_0.3.8.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.8.py   (needs SkyyArmory/SkyyArmory-0.1.26.jar - the H38 child loads it as a pack)

0.3.8 (2026-10-15, round "caster", with SkyyArmory 0.1.26) = WEAPON SPEED TIERS FOR WANDS AND STAFFS. Skyy's words:
  2026-10-05 "next pass on skyyGear should add the wynncraft style weapon speed.  so weapons come in slow medium fast and super fast. (DPS stays
             the same. so if you had 2 identical level 10 wands. with the same modifier ..."
  2026-10-06 tier "Fully random per item"; "Those speed tiers only roll on weapons. Not tools"
  2026-10-15 "still no weapon speed on mage staff"          (docs/answered/gear.md 2026-10-15 STAFF SPEED)
0.2.6 rolled tiers on the 9 melee families only ("No staff / wand has a tier in this round, left for SkyyArmory's tier pass"). SkyyArmory
0.1.26 now re-times the quick shot of every wand / staff root it owns behind its own hidden tier effects (SkyyArmory_Speed_Slow / _Fast /
_SuperFast); SkyyGear does the rest:
1. TWO CASTER FAMILIES (GearSpeed: NM = 9 melee families, NM = Wand, NM + 1 = Staff): a gear spell weapon whose Primary root is one of
   SkyyArmory's tier roots (armory:fn:speed answers its family - the 7 metal wands, the Wood / Rotten / Tribal wands, the 8 ladder staffs incl.
   the Wooden Earth Staff, the Untiered Loophole / Second Opinion). Spellbooks, the Soul Orb / Cages, Bo staffs and every other item: no
   tier. No SkyyArmory answer yet = not cached (asked again), like an item that is not loaded.
2. THE ROLL: the 0.2.6 roll, unchanged and the same way for casters - fully random per item (swing.odds), at craft / drop / chest / identify,
   never changed by reforge / level-up. EXISTING casters get theirs ON FIRST SIGHT: the stamp scan writes every identified gear stack through
   GearData.put -> GearSpeed.ensure, which adds only "spd" (the 0.2.13 Crude / Scrap "lazy heal"; one gear.log SPEED line per item, never on
   an unidentified one, never twice). No config row, no file, no marker - no one-time migration (nothing a server owner saved changes).
3. THE TIER EFFECT: GearHandSys puts SkyyArmory's caster effect of the held weapon's tier next to SkyyGear's own (both sets on / off together:
   the melee roots read ours, the caster roots read SkyyArmory's) - the same 3 s / 1.5 s refresh, lost-effect check and swap window. The
   caster set resolves on its own (GearSpeed.readyC, retried every 10 s; missing = casters stay Medium, melee untouched).
4. THE HIT: a caster QUICK shot (the projectile is the weapon's own quick projectile, armory:fn:speed) records at its spawn the hit weight of
   the tier the shot really ran (GearSpeed.shotW = appliedW: the tier effect on the player, the smaller one inside the swap window);
   GearHit.weaponHit multiplies that hit by it (GearSpeed.shotWeight) with True Damage / flat element lines and knockback x the same weight (the
   0.2.6 per-hit rules). Charged shots (hop / blink / orb) are never weighted - SkyyArmory keeps their charge time and Mana too.
   With SkyyArmory's quick shot every 0.35 s x w costing Mana x w: damage per second AND Mana per second are equal on every tier.
5. gear:fn:speed: + {"applied", UUID player, String item id} -> Double the applied hit weight of that held item (1 = none) - SkyyArmory's wand
   signature meter fills x it per quick hit.
6. THE TOOLTIP (the melee style): "<Tier> Attack Speed" in the head, and the Quick Shot row shows the PER-HIT damage and the Mana per cast of
   that tier ("Quick Shot 7 damage - 1.4 Mana - pierces 3 - 32 blocks"; Mana x w in tenths = GearSpeed.manaCost). The Charged Shot rows are
   unchanged. /gear read describes a caster's tier and whether SkyyArmory's tree is live.
7. FIX ROUND (critics): GearSpeed.reset() (the Item reload) also drops SkyyArmory's caster effect set, and a caster set that was missing at
   the last try is retried every 10 s while only a wand / staff is held (casterOn waits only until IDXC_NEXT; before, casters stayed Medium
   until a restart unless a melee tier weapon was held).
SAVED DATA: only the per-item "spd" key on caster stacks (as 0.2.6 / 0.2.13). ROLLBACK 0.3.8 -> 0.3.7 is item-safe: 0.3.7 keeps the unknown key in
every rewrite and ignores it for casters (no family = no line, no weight); with SkyyArmory 0.1.26 still in place nobody gets a caster effect
(0.3.7 never puts it), so every wand / staff shoots at Medium.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.7.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.8.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.7"' in s and "GENERATED by tools/gear_0_3_7_patch.py" in s and "0.3.8" not in s[:400], "not the generated 0.3.7 script"
assert "casterFam(" not in s and "shotWeight(" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.7":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.7" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.7 - build script (javassist via jpype). GENERATED by tools/gear_0_3_7_patch.py from the LIVE 0.3.6 (itself GENERATED by
tools/gear_0_3_6_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.7.py -> SkyyGear/SkyyGear-0.3.7.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.7.py
''', '''"""SkyyGear 0.3.8 - build script (javassist via jpype). GENERATED by tools/gear_0_3_8_patch.py from the LIVE 0.3.7 (itself GENERATED by
tools/gear_0_3_7_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.8.py -> SkyyGear/SkyyGear-0.3.8.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.8.py

0.3.8 = WEAPON SPEED TIERS FOR WANDS AND STAFFS (notes: tools/gear_0_3_8_patch.py; Skyy 2026-10-15 "still no weapon speed on mage staff"):
with SkyyArmory 0.1.26's tier trees, gear wands / staffs roll Slow / Medium / Fast / Super Fast like melee (existing ones on first sight);
GearHandSys puts SkyyArmory's caster tier effect too; a quick shot hits x its tier's weight (charged shots never), so damage and Mana per
second stay equal; the tooltip shows "<Tier> Attack Speed" and the quick shot's per-hit damage + Mana of that tier; gear:fn:speed "applied".

--- 0.3.7 notes ---
''')
rep('VERSION = "0.3.7"\n', 'VERSION = "0.3.8"\n')

# ================================================================================================================ 1. the caster families (arrays)
rep('''F(gspd, "public static final String[] F_NAME = %s;" % jarr([_f["fam"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_ROOT = %s;" % jarr([_f["root"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_TREE = %s;" % jarr([_f["tree"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_ANIM = %s;" % jarr([_f["anim"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_VARS = %s;" % jarr([",".join(_f["vars"]) for _f in SPEED_FAMLIST]))
''', '''# 0.3.8: two CASTER families after the melee ones - index NM = Wand, NM + 1 = Staff (SkyyArmory 0.1.26's tier trees re-time their quick shot;
# no root / tree / walk of SkyyGear's own; weights = SPEED_FACTOR, checked against armory:fn:speed's at run time)
CASTER_FAMS = ["Wand", "Staff"]
CASTER_EFF = ["SkyyArmory_Speed_Slow", "", "SkyyArmory_Speed_Fast", "SkyyArmory_Speed_SuperFast"]          # = SkyyArmory 0.1.26 SPD_EFF
CASTER_SMAX = 0.39          # the longest tier tap step of SkyyArmory's quick shots (the Slow staff 0.39 s): the caster swap window
assert len(SPEED_FAMLIST) == 9 and not [_f for _f in SPEED_FAMLIST if _f["fam"] in CASTER_FAMS]
F(gspd, "public static final String[] F_NAME = %s;" % jarr([_f["fam"] for _f in SPEED_FAMLIST] + CASTER_FAMS))
F(gspd, "public static final String[] F_ROOT = %s;" % jarr([_f["root"] for _f in SPEED_FAMLIST] + ["", ""]))
F(gspd, "public static final String[] F_TREE = %s;" % jarr([_f["tree"] for _f in SPEED_FAMLIST] + ["", ""]))
F(gspd, "public static final String[] F_ANIM = %s;" % jarr([_f["anim"] for _f in SPEED_FAMLIST] + ["", ""]))
F(gspd, "public static final String[] F_VARS = %s;" % jarr([",".join(_f["vars"]) for _f in SPEED_FAMLIST] + ["", ""]))
''')
rep('''F(gspd, "public static final String[] F_WALK = %s;" % jarr([_w for _f in SPEED_FAMLIST for _w in _f["walk"]]))
F(gspd, "public static final double[] F_W = new double[] { %s };" % ", ".join(repr(float(_x)) for _f in SPEED_FAMLIST for _x in _f["w"]))
F(gspd, "public static final double[] F_SMAX = new double[] { %s };" % ", ".join(repr(float(_x)) for _f in SPEED_FAMLIST for _x in _f["smax"]))
''', '''F(gspd, "public static final String[] F_WALK = %s;" % jarr([_w for _f in SPEED_FAMLIST for _w in _f["walk"]] + [""] * 8))
F(gspd, "public static final double[] F_W = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in [_y for _f in SPEED_FAMLIST for _y in _f["w"]] + SPEED_FACTOR * 2))
F(gspd, "public static final double[] F_SMAX = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in [_y for _f in SPEED_FAMLIST for _y in _f["smax"]] + [CASTER_SMAX] * 8))
F(gspd, "public static final int NM = %d;" % len(SPEED_FAMLIST))          # 0.3.8: the melee families (NM = Wand, NM + 1 = Staff)
F(gspd, "public static final String[] CEFF = %s;" % jarr(CASTER_EFF))          # 0.3.8: SkyyArmory's caster tier effects
F(gspd, "public static volatile int[] IDXC = null;")
F(gspd, "public static volatile long IDXC_NEXT = 0L;")
F(gspd, "public static volatile boolean IDXC_TOLD = false;")
# 0.3.8: caster id -> Object[] { Boolean ok (SkyyArmory's tree live + the same weights), String its quick projectile id, Long valid until }
F(gspd, "public static final java.util.concurrent.ConcurrentHashMap CACT = new java.util.concurrent.ConcurrentHashMap();")
''')

# ================================================================================================================ 2. casterFam + famCalc
before('''# famCalc: f (0-8) = a tier weapon of family f; -2 - f = an item that swings with family f's replaced root but gets no tier (not gear, another''',
       '''# 0.3.8: SkyyArmory 0.1.26's family of a wand / staff id (armory:fn:speed): 0 Wand, 1 Staff (it shoots through a tier tree), -1 none, -100 not
# known yet (SkyyArmory not loaded / the item not loaded - famRaw never caches it)
M(gspd, r"""
public static int casterFam(String id) {
  if (id == null || !(id.startsWith("Weapon_Wand_") || id.startsWith("Weapon_Staff_"))) return -1;
  java.util.function.Function f = @PKG@.Gear.fn("armory:fn:speed");
  if (f == null) return -100;
  Object r = null;
  try { r = f.apply(id); } catch (Throwable t) { return -100; }
  if (r instanceof String) return -100;
  if (!(r instanceof Object[])) return -1;
  Object[] a = (Object[]) r;
  if (a.length < 9) return -1;
  if ("Wand".equals(a[0])) return 0;
  if ("Staff".equals(a[0])) return 1;
  return -1;
}""")
''')
rep('''  @ITM@ it = @PKG@.Gear.item(id);
  if (it == null) return -100;
  java.util.Map in = it.getInteractions();
  Object r = null;
  if (in != null) r = in.get(@ITYPE@.Primary);
  if (!(r instanceof String)) return -1;
  int f = -1;
  for (int i = 0; i < F_ROOT.length; i++) if (F_ROOT[i].equals(r)) { f = i; break; }
''', '''  @ITM@ it = @PKG@.Gear.item(id);
  if (it == null) return -100;
  // 0.3.8: a wand / staff on one of SkyyArmory's tier roots = caster family NM (Wand) / NM + 1 (Staff); a gear spell weapon gets the tier
  int cf = casterFam(id);
  if (cf == -100) return -100;
  if (cf >= 0) {
    if (!@PKG@.GearData.isGear(id) || @PKG@.GearData.slotOf(id) != 1) return -2 - (NM + cf);
    return NM + cf;
  }
  java.util.Map in = it.getInteractions();
  Object r = null;
  if (in != null) r = in.get(@ITYPE@.Primary);
  if (!(r instanceof String)) return -1;
  int f = -1;
  for (int i = 0; i < NM; i++) if (F_ROOT[i].equals(r)) { f = i; break; }
''')

# ================================================================================================================ 3. manaText (after manaCost)
rep('''public static double manaCost(double base, double w) {
  if (!(base > 0.0)) return 0.0;
  if (!(w > 0.0) || Double.isInfinite(w)) return base;
  return Math.floor(base * w * 10.0 + 0.5) / 10.0;
}""")
''', '''public static double manaCost(double base, double w) {
  if (!(base > 0.0)) return 0.0;
  if (!(w > 0.0) || Double.isInfinite(w)) return base;
  return Math.floor(base * w * 10.0 + 0.5) / 10.0;
}""")
# 0.3.8: Mana for a tooltip: whole numbers plain ("2"), else one decimal ("1.4")
M(gspd, r"""
public static String manaText(double m) {
  long r = Math.round(m * 10.0);
  if (r % 10L == 0L) return Long.toString(r / 10L);
  return Long.toString(r / 10L) + "." + Long.toString(Math.abs(r % 10L));
}""")
''')

# ================================================================================================================ 4. active / caster live / rootsText / shows / walk
rep('''public static boolean active(int f) {
  if (f < 0 || f >= F_ROOT.length) return false;
  int[] a = ACT;
  long now = System.currentTimeMillis();
  if (a == null || now >= ACT_AT) {
    a = new int[F_ROOT.length];''', '''public static boolean active(int f) {
  if (f < 0 || f >= NM) return false;
  int[] a = ACT;
  long now = System.currentTimeMillis();
  if (a == null || now >= ACT_AT) {
    a = new int[NM];''')
rep('''public static void reset() {
  ACT = null;
  NORM.clear();
  FAM.clear();''', '''public static void reset() {
  ACT = null;
  NORM.clear();
  FAM.clear();
  CACT.clear();          // 0.3.8
  IDXC = null;          // 0.3.8 fix: SkyyArmory's caster effect set re-resolves too (like IDX below)
  IDXC_NEXT = 0L;
  IDXC_TOLD = false;''')
rep('''public static String rootsText() {
  int n = 0;
  StringBuilder no = new StringBuilder();
  for (int i = 0; i < F_ROOT.length; i++) {''', '''public static String rootsText() {
  int n = 0;
  StringBuilder no = new StringBuilder();
  for (int i = 0; i < NM; i++) {''')
rep('''  return "weapon speed tiers ready: " + n + "/" + F_ROOT.length + " melee families on SkyyGear's swing roots" + (no.length() > 0 ? " - NOT SkyyGear's (no tier works there): " + no.toString() : "");
}""")''', '''  return "weapon speed tiers ready: " + n + "/" + NM + " melee families on SkyyGear's swing roots" + (no.length() > 0 ? " - NOT SkyyGear's (no tier works there): " + no.toString() : "")
    + "; wands / staffs: SkyyArmory's caster tier effects " + (IDXC != null ? "loaded" : (@PKG@.Gear.fn("armory:fn:speed") != null ? "not loaded yet" : "absent (SkyyArmory 0.1.26 not loaded) - casters stay Medium"));
}""")
# 0.3.8: SkyyArmory's answer for a caster id, cached 30 s (an asset reload / another pack replacing a root shows within that): Object[] {
# Boolean ok = the tree is live and its weights are SkyyGear's, String its quick projectile id ("" = none), Long valid until }
M(gspd, r"""
public static Object[] casterInfo(String id) {
  long now = System.currentTimeMillis();
  Object[] e = (Object[]) CACT.get(id);
  if (e != null && now < ((Long) e[2]).longValue()) return e;
  boolean ok = false;
  String qp = "";
  try {
    java.util.function.Function fn = @PKG@.Gear.fn("armory:fn:speed");
    Object r = fn == null ? null : fn.apply(id);
    if (r instanceof Object[] && ((Object[]) r).length >= 9) {
      Object[] a = (Object[]) r;
      int f = "Wand".equals(a[0]) ? NM : ("Staff".equals(a[0]) ? NM + 1 : -1);
      boolean live = f >= 0 && Boolean.TRUE.equals(a[3]);
      ok = live;
      for (int t = 0; ok && t < 4; t++) ok = a[5 + t] instanceof Number && Math.abs(((Number) a[5 + t]).doubleValue() - F_W[f * 4 + t]) < 1.0E-9;
      if (live && !ok) @PKG@.Gear.warnOnce("spdcw", "weapon speed: SkyyArmory's caster hit weights differ from SkyyGear's - wands / staffs keep no tier (update both mods together)");
      if (a[4] instanceof String) qp = (String) a[4];
    }
  } catch (Throwable t) { ok = false; }
  e = new Object[] { Boolean.valueOf(ok), qp, Long.valueOf(now + 30000L) };
  if (CACT.size() > 512) CACT.clear();
  CACT.put(id, e);
  return e;
}""")
# 0.3.8: a caster family works for this id while SkyyArmory's tree is live (and its tier effects did not fail to load)
M(gspd, r"""
public static boolean casterOn(String id, int f) {
  if (id == null || f < NM || f >= F_NAME.length) return false;
  // fix: missing at the last try = Medium only until the next 10 s retry is due (then the tick's put -> readyC tries again; before, a
  // caster-only player never reached put again and stayed Medium until a restart)
  if (IDXC == null && IDXC_TOLD && System.currentTimeMillis() < IDXC_NEXT) return false;
  return Boolean.TRUE.equals(casterInfo(id)[0]);
}""")
M(gspd, r"""
public static boolean activeFor(String id, int f) {
  if (f < NM) return active(f);
  return casterOn(id, f);
}""")''')
rep('''  if (IDX == null && IDX_TOLD) return false;
  int f = famOf(id);
  return f >= 0 && active(f);
}""")''', '''  if (IDX == null && IDX_TOLD) return false;
  int f = famOf(id);
  return f >= 0 && activeFor(id, f);          // 0.3.8: a caster = SkyyArmory's tree live
}""")''')
rep('''  java.util.IdentityHashMap m = new java.util.IdentityHashMap();
  int f = rootFam(id);
  if (f < 0 || t < 0 || t > 3 || t == 1) return m;''', '''  java.util.IdentityHashMap m = new java.util.IdentityHashMap();
  int f = rootFam(id);
  if (f < 0 || f >= NM || t < 0 || t > 3 || t == 1) return m;          // 0.3.8: casters have no melee tap walk''')

# ================================================================================================================ 5. appliedFor + shotW (after appliedW)
rep('''  int pv = (int) L[3];
  if (pv != ap && System.currentTimeMillis() - L[4] < winMs(f, pv)) {
    double w2 = weight(f, pv < 0 ? 1 : pv);
    if (w2 < w) w = w2;
  }
  return w;
}""")
''', '''  int pv = (int) L[3];
  if (pv != ap && System.currentTimeMillis() - L[4] < winMs(f, pv)) {
    double w2 = weight(f, pv < 0 ? 1 : pv);
    if (w2 < w) w = w2;
  }
  return w;
}""")
# 0.3.8 gear:fn:speed {"applied", UUID, item id}: the applied hit weight of that held item (SkyyArmory's wand signature meter); 1 = none
M(gspd, r"""
public static Double appliedFor(Object uo, Object io) {
  try {
    if (!(uo instanceof java.util.UUID) || !(io instanceof String) || !on()) return Double.valueOf(1.0);
    String id = (String) io;
    int f = famOf(id);
    if (f < 0 || !activeFor(id, f)) return Double.valueOf(1.0);
    return Double.valueOf(appliedW((java.util.UUID) uo, f));
  } catch (Throwable x) { return Double.valueOf(1.0); }
}""")
# 0.3.8 THE CASTER SHOT WEIGHT, taken when the projectile spawns (GearShotTrack): a QUICK shot (the weapon's own quick projectile) of a tier
# wand / staff = the weight of the tier the shot really ran (appliedW: the tier effect on the player = the tree branch SkyyArmory's root took,
# the smaller one inside the swap window); 0 = not weighted (charged shots, other projectiles, Medium, no tier, SkyyArmory's tree not live)
M(gspd, r"""
public static double shotW(java.util.UUID u, @IS@ main, String pid) {
  try {
    if (!on() || u == null || main == null || main.isEmpty() || pid == null) return 0.0;
    String id = main.getItemId();
    int f = famOf(id);
    if (f < NM || !casterOn(id, f)) return 0.0;
    Object[] e = casterInfo(id);
    if (!pid.equals(e[1])) return 0.0;
    double w = appliedW(u, f);
    return w == 1.0 ? 0.0 : w;
  } catch (Throwable x) { return 0.0; }
}""")
''')

# ================================================================================================================ 6. the caster effect set (readyC, put, tick, wantOf)
rep('''M(gspd, r"""
public static int wantOf(@IS@ h, int[] out) {''', '''# 0.3.8: SkyyArmory's caster tier effects (resolved on their own, retried every 10 s; missing = casters stay Medium, melee untouched)
M(gspd, r"""
public static synchronized boolean readyC() {
  if (IDXC != null) return true;
  long now = System.currentTimeMillis();
  if (now < IDXC_NEXT) return false;
  IDXC_NEXT = now + 10000L;
  int[] r = new int[] { -1, -1, -1, -1 };
  for (int t = 0; t < 4; t++) {
    if (t == 1) continue;
    int x = Integer.MIN_VALUE;
    try { x = @EFX@.getAssetMap().getIndex(CEFF[t]); } catch (Throwable e) { x = Integer.MIN_VALUE; }
    if (x == Integer.MIN_VALUE || x < 0) {
      if (!IDXC_TOLD) {
        IDXC_TOLD = true;
        if (@PKG@.Gear.fn("armory:fn:speed") != null) @PKG@.Gear.warn("weapon speed: SkyyArmory's caster tier effect " + CEFF[t] + " is not loaded - wands / staffs shoot at Medium speed (retried every 10 s)");
      }
      return false;
    }
    r[t] = x;
  }
  IDXC = r;
  return true;
}""")
M(gspd, r"""
public static int wantOf(@IS@ h, int[] out) {''')
rep('''  String id = h.getItemId();
  int f = famOf(id);
  if (f < 0 || !active(f)) return -1;
  @BD@ d = @PKG@.GearData.effective(id, h.getMetadata());''', '''  String id = h.getItemId();
  int f = famOf(id);
  if (f < 0 || !activeFor(id, f)) return -1;          // 0.3.8: + casters
  @BD@ d = @PKG@.GearData.effective(id, h.getMetadata());''')
rep('''public static void put(@CB@ cb, @REF@ ref, @ECC@ ecc, int want) {
  int[] idx = IDX;
  @I2O@ map = ecc.getActiveEffects();
  if (idx == null || map == null) return;
  for (int t = 0; t < 4; t++) {
    if (t == 1 || t == want) continue;
    if (map.get(idx[t]) != null) { ecc.removeEffect(ref, idx[t], cb); N.incrementAndGet(1); }
  }
  if (want < 0 || want == 1) return;
  Object o = map.get(idx[want]);
  if (o instanceof @AEE@ && ((@AEE@) o).getRemainingDuration() >= 1.5f) return;
  @EFX@ fx = (@EFX@) @EFX@.getAssetMap().getAsset(idx[want]);
  if (fx == null) return;
  ecc.addEffect(ref, idx[want], fx, 3.0f, @OVB@.OVERWRITE, cb);
  N.incrementAndGet(0);
}""")''', '''public static void putOne(@CB@ cb, @REF@ ref, @ECC@ ecc, @I2O@ map, int x) {
  Object o = map.get(x);
  if (o instanceof @AEE@ && ((@AEE@) o).getRemainingDuration() >= 1.5f) return;
  @EFX@ fx = (@EFX@) @EFX@.getAssetMap().getAsset(x);
  if (fx == null) return;
  ecc.addEffect(ref, x, fx, 3.0f, @OVB@.OVERWRITE, cb);
  N.incrementAndGet(0);
}""")
# 0.3.8: SkyyArmory's caster set goes on / off with SkyyGear's own (the melee roots read ours, the caster roots read SkyyArmory's)
M(gspd, r"""
public static void put(@CB@ cb, @REF@ ref, @ECC@ ecc, int want) {
  int[] idx = IDX;
  @I2O@ map = ecc.getActiveEffects();
  if (idx == null || map == null) return;
  int[] ic = null;
  if (readyC()) ic = IDXC;
  for (int t = 0; t < 4; t++) {
    if (t == 1 || t == want) continue;
    if (map.get(idx[t]) != null) { ecc.removeEffect(ref, idx[t], cb); N.incrementAndGet(1); }
    if (ic != null && map.get(ic[t]) != null) { ecc.removeEffect(ref, ic[t], cb); N.incrementAndGet(1); }
  }
  if (want < 0 || want == 1) return;
  putOne(cb, ref, ecc, map, idx[want]);
  if (ic != null) putOne(cb, ref, ecc, map, ic[want]);
}""")
# 0.3.8: the caster effect of the applied tier is missing (died / cleared) - the record is not true any more
M(gspd, r"""
public static boolean lostC(@I2O@ map, int ap) {
  int[] ic = IDXC;
  return ic != null && ap >= 0 && ap < 4 && ap != 1 && map.get(ic[ap]) == null;
}""")''')
rep('''      if (map == null || map.get(idx[ap]) == null) {
        L[3] = (long) ap;''', '''      if (map == null || map.get(idx[ap]) == null || lostC(map, ap)) {          // 0.3.8: + the caster effect
        L[3] = (long) ap;''')

# ================================================================================================================ 7. describe + readyText
rep('''  if (f < 0) return s + "no tier for this item (not one of the " + F_NAME.length + " melee families, or it changes its own swing steps / animation set)";
  int t = tierOf(d);
  String st;
  if (t >= 0) st = TIER[t] + " - swing time and hit x" + @PKG@.Gear.fnum(weight(f, t));''', '''  if (f < 0) return s + "no tier for this item (not one of the " + NM + " melee families or a SkyyArmory wand / staff on its tier root, or it changes its own swing steps / animation set)";
  int t = tierOf(d);
  String st;
  if (t >= 0) st = TIER[t] + (f >= NM ? " - quick-shot time, Mana and hit x" : " - swing time and hit x") + @PKG@.Gear.fnum(weight(f, t));''')
rep('''  return s + F_NAME[f] + " family (" + (active(f) ? "SkyyGear's swing root loaded" : "root " + F_ROOT[f] + " is NOT SkyyGear's (" + rootFirst(F_ROOT[f]) + ") - no tier works") + "), " + st''',
    '''  String rt = f >= NM ? (casterOn(id, f) ? "SkyyArmory's tier tree live, caster effects " + (IDXC != null ? "loaded" : "not loaded yet") : "SkyyArmory's tier tree NOT live (needs SkyyArmory 0.1.26 + its caster effects) - no tier works")
    : (active(f) ? "SkyyGear's swing root loaded" : "root " + F_ROOT[f] + " is NOT SkyyGear's (" + rootFirst(F_ROOT[f]) + ") - no tier works");          // 0.3.8
  return s + F_NAME[f] + " family (" + rt + "), " + st''')
rep('''  return "weapon speed tiers " + (on() ? "on" : "OFF (swing.tiers)") + " (" + F_ROOT.length + " melee families, odds "''',
    '''  return "weapon speed tiers " + (on() ? "on" : "OFF (swing.tiers)") + " (" + NM + " melee families + wands / staffs on SkyyArmory's tier trees, odds "''')

# ================================================================================================================ 8. gear:fn:speed "applied"
rep('''    if (m == 11) {
      Object[] xs = x(o);''', '''    if (m == 11) {
      if (o instanceof Object[] && ((Object[]) o).length >= 3 && "applied".equals(((Object[]) o)[0])) return @PKG@.GearSpeed.appliedFor(((Object[]) o)[1], ((Object[]) o)[2]);          // 0.3.8
      Object[] xs = x(o);''')

# ================================================================================================================ 9. the shot: GearShot.w, the record, the hit
rep('''           "public boolean charged;", "public String pid;", "public boolean snap;"):
    F(gsho, _f)
''', '''           "public boolean charged;", "public String pid;", "public boolean snap;",
           "public double w;"):          # 0.3.8: a caster quick shot's hit weight (0 = x1), GearSpeed.shotW at the spawn
    F(gsho, _f)
# 0.3.8 GearHit.weaponHit: a projectile hit whose launch record holds a caster quick-shot weight hits x it (kept for perHit: knockback)
M(gspd, r"""
public static double shotWeight(@PKG@.GearShot rec, @DMG@ d) {
  if (rec == null || d == null || !(rec.w > 0.0) || rec.w == 1.0 || !on()) return 1.0;
  N.incrementAndGet(2);
  LAST.set(new Object[] { d, Double.valueOf(rec.w) });
  return rec.w;
}""")
''')
rep('''    rec.charged = pid != null && mh != null && !mh.isEmpty() && @PKG@.GearChg.launchCode(mh.getItemId(), pid) == 1;
''', '''    rec.charged = pid != null && mh != null && !mh.isEmpty() && @PKG@.GearChg.launchCode(mh.getItemId(), pid) == 1;
    rec.w = @PKG@.GearSpeed.shotW(u, mh, pid);          // 0.3.8: a caster quick shot's tier weight
''')
rep('''  // 0.2.6 WEAPON SPEED TIERS: a melee tap of a tier weapon hits x its hit weight (Slow x1.4 ... Super Fast x0.5) - the same damage per second
  double sw = shot ? 1.0 : @PKG@.GearSpeed.hitWeight(d, u, main);''', '''  // 0.2.6 WEAPON SPEED TIERS: a melee tap of a tier weapon hits x its hit weight (Slow x1.4 ... Super Fast x0.5) - the same damage per second;
  // 0.3.8: a caster QUICK shot x the weight its launch record took (charged shots and every other projectile x1)
  double sw = shot ? @PKG@.GearSpeed.shotWeight(rec, d) : @PKG@.GearSpeed.hitWeight(d, u, main);''')

# ================================================================================================================ 10. the tooltip
rep('''    String q = null;
    long qv = -1L;
    if (qp.length() > 0 && qm > 0 && qd > 0) {
      double qf = (ton && qp.startsWith("SkyyArmory_")) ? tune / 100.0 * armoryQuickPct() / 20.0 * (1.0 + qb / 100.0) : 1.0;
      qv = shown(prjDamage(qp, qd) * qf * m);''', '''    String q = null;
    long qv = -1L;
    double qraw = -1.0;          // 0.3.8: the unrounded quick hit ([8]; GearView scales it by a caster's tier weight)
    if (qp.length() > 0 && qm > 0 && qd > 0) {
      double qf = (ton && qp.startsWith("SkyyArmory_")) ? tune / 100.0 * armoryQuickPct() / 20.0 * (1.0 + qb / 100.0) : 1.0;
      qraw = prjDamage(qp, qd) * qf * m;
      qv = shown(qraw);''')
rep('''    return new Object[] { c, q, Long.valueOf(cv), Long.valueOf(qv), Integer.valueOf(cm), Integer.valueOf(qm), tw.length() > 0 ? tw : null, qw };''',
    '''    return new Object[] { c, q, Long.valueOf(cv), Long.valueOf(qv), Integer.valueOf(cm), Integer.valueOf(qm), tw.length() > 0 ? tw : null, qw, Double.valueOf(qraw) };''')
rep('''# a weapon's head (speed), base rows and Ability rows. 0.2.2 rules kept: a SkyyArmory wand / staff shows its two shots and never the melee line''',
    '''# 0.3.8: a tier wand / staff: { "<Tier> Attack Speed", its quick row at that tier (the per-hit damage x w, Mana x w in tenths) } or null
M(gvw, r"""
public static String[] casterRows(String id, @BD@ d, Object[] sh) {
  if (sh == null || sh.length < 8 || sh[1] == null || !@PKG@.GearSpeed.shows(id, d)) return null;
  int f = @PKG@.GearSpeed.famOf(id);
  if (f < @PKG@.GearSpeed.NM) return null;
  int t = @PKG@.GearSpeed.tierOf(d);
  double w = @PKG@.GearSpeed.weight(f, t);
  String qw = sh[7] instanceof String ? (String) sh[7] : "";
  double raw = (double) ((Long) sh[3]).longValue();
  if (sh.length > 8 && sh[8] instanceof Number) raw = ((Number) sh[8]).doubleValue();
  String q = "Quick Shot " + @PKG@.GearBase.shown(raw * w) + " damage - " + @PKG@.GearSpeed.manaText(@PKG@.GearSpeed.manaCost((double) ((Integer) sh[5]).intValue(), w)) + " Mana" + (qw.length() > 0 ? " - " + qw : "");
  return new String[] { @PKG@.GearSpeed.tierName(t) + " Attack Speed", q };
}""")
# a weapon's head (speed), base rows and Ability rows. 0.2.2 rules kept: a SkyyArmory wand / staff shows its two shots and never the melee line''')
rep('''  Object[] sh = @PKG@.GearBase.shots(id, d);
  String[] spd = null;
  if (sh == null && slot == 0) spd = speedRows(id, d);
''', '''  Object[] sh = @PKG@.GearBase.shots(id, d);
  String[] spd = null;
  if (sh == null && slot == 0) spd = speedRows(id, d);
  String[] cst = null;
  if (sh != null) cst = casterRows(id, d, sh);          // 0.3.8: a tier wand / staff
  if (cst != null) add(ht, hc, cst[0], @PKG@.GearDefs.C_GRAY);
''')
rep('''    if (sh[1] != null) add(bt, bc, quickRow(sh), null);''', '''    if (sh[1] != null) add(bt, bc, cst != null ? cst[1] : quickRow(sh), null);          // 0.3.8: the tier's per-hit numbers''')

# ================================================================================================================ the manifest
rep('''summoned lifelong tools land in your hotbar first; one tier up ore and logs take 2.5x the hits of the right-tier tool (two up 10x); Server Setup -> Gear.''',
    '''summoned lifelong tools land in your hotbar first; one tier up ore and logs take 2.5x the hits of the right-tier tool (two up 10x); wands and staffs roll speed tiers too (with SkyyArmory 0.1.26: quick shots Slow to Super Fast, same damage and Mana per second); Server Setup -> Gear.''')

# ================================================================================================================ checks on the result
assert s.index("public static int casterFam(") < s.index("public static int famCalc(")
assert s.index("public static String manaText(") < s.index("public static String[] casterRows(")
assert s.index("public static Object[] casterInfo(") < s.index("public static boolean shows(String id, @BD@ d)") < s.index("public static double shotW(")
assert s.index("public static synchronized boolean readyC(") < s.index("public static void put(@CB@ cb") and s.index("public static boolean lostC(") < s.index("public static void tick(@CB@ cb")
assert s.index("public static double shotW(") < s.index("rec.w = @PKG@.GearSpeed.shotW(") and s.index("public double w;") < s.index("public static double shotWeight(") < s.index("GearSpeed.shotWeight(rec, d)")
assert s.index("public static Double appliedFor(") < s.index("GearSpeed.appliedFor(((Object[]) o)[1]")
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.7 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.7 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
