"""Derive SkyyArmory/build_skyyarmory_0.1.9.py (+ its harness SkyyArmory/test_skyyarmory_0.1.9.py) from the GENERATED 0.1.8
(SkyyArmory/build_skyyarmory_0.1.8.py = the tools/deploy_set.py SET pin, made by tools/armory_0_1_8_patch.py; test_skyyarmory_0.1.8.py =
its harness). Every anchor is asserted (rep = exactly one hit). Edit THIS file, never the generated scripts.
Run:  python tools/armory_0_1_9_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.9.py   then   python SkyyArmory/test_skyyarmory_0.1.9.py
      (never --deploy; deploy partner: SkyyTrees 0.3.3 - the class path trees whose nodes this build reads)

0.1.9 = THE CLASS TREE READER (Skyy 2026-10-07 overnight: "try to get the new updated class skill trees out tonight if you can"; the contract =
research/cloud/Class-Tree-Build-Map.md section 6 + research/cloud/Class-Tree-Paths.md): SkyyArmory reads the SkyyTrees 0.3.3 class nodes it
applies through the existing bridge (tree:fn:bonus, Object[]{UUID, "Class.<Class>.<Id>"} -> Double, plain java.lang types; cached 1 s per
player and key) at the moment of the move, and lists exactly the keys it FULLY applies in tree:reads:SkyyArmory (set in setup() after the
config load, removed at shutdown) - SkyyTrees keeps every other node "Coming with SkyyArmory". No new saved data, no new setting: the Server
Setup rows stay the base, a node adds on top. 12 nodes are coded (the map's 13 minus Mage Rift Master PA5 - its 1-block wall pass + the 25 %
slow are not built; it stays waiting); 11 are LISTED - fix 2 holds Monk Hard Knuckles PB1 back (its power-hit test is UNVERIFIED in game, so
SkyyTrees keeps it waiting until Skyy has seen it; the code runs in the harness). A profile switch (profile:epoch:<uuid>, PROFILES-CONTRACT
rule 3) drops that player's cached answers, Rift Echo window and Double Step state (fix 2):
  MAGE (staff blink): T2 Spell Focus = the blink trail and the spellbook Page Burst x (1 + Amount %); T3 Long Blink = blink.distance + the
    ranked Amount (SkyyTrees answers +2 / +3 / +4 / +5 at Sorcery 15 / 30 / 42 / 55) and the trail +1 s; PA1 Blink Slash = trail damage
    x (1 + Amount %) and the blink costs 20 % more Mana (too little = no blink, nothing spent); PA2 Rift Echo = a second blink within 2 s is
    free (the chain's Mana back, half the Stamina), then the next blink waits Amount s; PB1 Radiant Trail = the trail also heals you and your
    party Amount % of max Health a second (a direct, room-clamped heal like the orb without SkyyClasses - no Divinity XP: the Mage is no
    Priest) and its damage x 0.75.
  PRIEST: T1 Gentle Hands = the wand heal orb heals Amount % more.
  MONK (coded, NOT listed - fix 2): PB1 Hard Knuckles = the wraps' power hit and the gauntlets' finisher x (1 + Amount %), the other jabs x 0.95 - ArmoryTuneSys tells the
    power hit apart by the hit's initial damage (the closer of the weapon's jab / power number, read from our own chains at build time) -
    UNVERIFIED in game (the engine may scale the initial amount).
  ASSASSIN: T3 Long Reach = kunai teleport range + Amount, Shadow Step targetRange + Amount and its no-target step + 2/3 of it (24 -> 27,
    18 -> 20); PC1 Long Throw = kunai teleport range + Amount (20 -> 26) and kunai hits x 0.9; PC2 Hard Return = the return knockback x Amount,
    the return window 2 s shorter (at least 1 s) and a 0.4 s vanilla Stun effect on every enemy it pushes (the Stun on mobs is UNVERIFIED);
    PC3 Double Step = a second teleport throw within 3 s of a teleport ignores the cooldown and costs half the Stamina and no Mana, then the
    next waits the cooldown + Amount s; PC4 Blink Strike = arriving within 3 blocks of an enemy after a kunai teleport or a TARGETED Shadow
    Step hits the nearest one for Amount / 10 kunai hits (the metal's kunai hit; 10 = 1.0), the teleport costs 10 % more (Stamina + Mana; the
    Shadow Step's Stamina).
  UNCHANGED: every 0.1.8 move, item, row, file and number for a player without these nodes (or without SkyyTrees: tree:fn:bonus missing = 0).
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.8.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.9.py")
TSRC = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.8.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.9.py")

raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.8"\nMOD = "SkyyArmory"' in s and "0.1.8 = THE DAGGER SHADOW STEP" in s, "build_skyyarmory_0.1.8.py is not the 0.1.8 pin"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:140])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


TREE_KEYS = ["Class.Mage.T2", "Class.Mage.T3", "Class.Mage.PA1", "Class.Mage.PA2", "Class.Mage.PB1", "Class.Priest.T1", "Class.Monk.PB1",
             "Class.Assassin.T3", "Class.Assassin.PC1", "Class.Assassin.PC2", "Class.Assassin.PC3", "Class.Assassin.PC4"]
assert len(TREE_KEYS) == 12 and "Class.Mage.PA5" not in TREE_KEYS
# fix 2 (critic): Hard Knuckles' power-hit test reads Damage.getInitialAmount, which the engine builds in DamageCalculatorSystems (the weapon's
# calculator, its random / sequence modifiers) - UNVERIFIED in game, so Class.Monk.PB1 is NOT listed in tree:reads:SkyyArmory (the map: list only
# what is fully applied; SkyyTrees keeps the node "Coming with SkyyArmory", nobody can buy a mis-scaled node). The code stays and the harness
# runs it; listing it later = drop it from HELD.
HELD = ["Class.Monk.PB1"]
READS = [k_ for k_ in TREE_KEYS if k_ not in HELD]
assert len(READS) == 11 and "Class.Monk.PB1" not in READS

# ================================================================================================ header + version
rep('''"""SkyyArmory 0.1.8 - build script (javassist via jpype). GENERATED by tools/armory_0_1_8_patch.py from the GENERATED 0.1.7 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.8.py -> SkyyArmory/SkyyArmory-0.1.8.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.8.py (scratch tools/dev/scratch/armory018/).
''', '"""SkyyArmory 0.1.9 - build script (javassist via jpype). GENERATED by tools/armory_0_1_9_patch.py from the GENERATED 0.1.8 - edit the\n'
    'patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.9.py -> SkyyArmory/SkyyArmory-0.1.9.jar (never --deploy). Harness:\n'
    'python SkyyArmory/test_skyyarmory_0.1.9.py (scratch tools/dev/scratch/armory019/).\n\n'
    + open(__file__, encoding="utf8").read().split('"""')[1].split("\n", 3)[3].strip() + "\n\n"
    '0.1.8 (the base, everything below is still true unless 0.1.9 above says otherwise):\n')
rep('VERSION = "0.1.8"\nMOD = "SkyyArmory"', 'VERSION = "0.1.9"\nMOD = "SkyyArmory"')

# ================================================================================================ engine members (the stun effect), probed
before('''# ================================================================= classes (all top-level; methods before callers)''', r'''# ---- 0.1.9 the class tree reader: the Hard Return stun = the vanilla Stun effect for a set time (EffectControllerComponent.addEffect with
# a duration + OverlapBehavior - SkyyTrees 0.2.3's swing-marker call, live since 2026-09-25); the effect asset exists in Assets.zip
T["OVB"] = "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior"
probe_sig(T["ECC"], "addEffect", "boolean", [T["REF"], T["EFX"], "float", T["OVB"], T["CAC"]])
assert JMod.isPublic(pool.get(T["OVB"]).getField("OVERWRITE").getModifiers()), "OverlapBehavior.OVERWRITE is not public"
PROBED.append("OverlapBehavior.OVERWRITE")
TREE_STUN = "Stun"
assert json.loads(AZ.read("Server/Entity/Effects/Status/Stun.json").decode("utf-8-sig"))["ApplicationEffects"]["MovementEffects"]["DisableAll"] is True, \
    "the vanilla Stun effect changed"
PROBED.append("EntityEffect Stun (Assets.zip: Status/Stun.json, movement disabled)")
# Hard Knuckles: every Monk fist weapon's jab / power (finisher) damage, read from our own chains above (the build's numbers, not typed)
FIST_TAB = [("Weapon_Fist_Gauntlets_" + _m, float(GAUNT[_m]["jab"]), float(GAUNT[_m]["fin"])) for _m in GAUNT_METALS] + \
           [("Weapon_Fist_Wraps_" + _c, float(WRAP[_c]["jab"]), float(WRAP[_c]["pow"])) for _c, _col, _k, _p in WRAPS]
assert len(FIST_TAB) == len(GAUNT_METALS) + len(WRAPS) and all(p_ > j_ > 0.0 for _i, j_, p_ in FIST_TAB), FIST_TAB

''')
rep('''shd = pool.makeClass(PKG + ".Shadow")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun, srec, stun, shd]''',
    '''shd = pool.makeClass(PKG + ".Shadow")
# 0.1.9 the class tree reader (tree:fn:bonus, cached 1 s; tree:reads:SkyyArmory)
atree = pool.makeClass(PKG + ".ArmoryTree")
ALL = [lg, dfs, cfg, hooks, spn, tune, spsys, chk, info, tgrid, tmath, wgrid, tshot, tfx, tworld, tjob, theal, trav, travsys, hitsys, ttick,
       gmath, gstate, grap, gimp, gbolt, gfall, lstate, leap, lvst, levc, kst, kimp, kjob, kun, srec, stun, shd, atree]''')

# ================================================================================================ ArmoryTree (no dependency on our other classes)
ATREE = r'''
# ---- 0.1.9 ArmoryTree: the class tree reader. b(u, key) = SkyyTrees' tree:fn:bonus answer (the node's ranked Amount while the player owns it;
# 0 otherwise / without SkyyTrees), cached 1 s per player + key (moves call it at the moment they happen); KEYS = tree:reads:SkyyArmory = only
# the nodes this build fully applies. Plain java.lang types over the shared bridge map. Methods before their callers (ArmoryTrav, Kunai, Stun,
# Shadow, ArmoryTuneSys and the plugin call them).
for f in ("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",   # "u|key" -> double[]{v, at}
          "public static final java.util.concurrent.ConcurrentHashMap ECHO = new java.util.concurrent.ConcurrentHashMap();",    # u -> long[]{at, used, cdUntil}
          "public static final String KEYS = %s;" % json.dumps(",".join(READS)),
          "public static final String READS_KEY = \"tree:reads:SkyyArmory\";",
          "public static final long CACHE_MS = 1000L;", "public static final long ECHO_MS = 2000L;", "public static final long DOUBLE_MS = 3000L;",
          "public static final double SLASH_MANA = 0.2;", "public static final double RAD_DMG = 0.75;", "public static final double PC1_DMG = 0.9;",
          "public static final double STUN_S = 0.4;", "public static final double WIN_CUT = 2.0;", "public static final double STRIKE_R = 3.0;",
          "public static final double PC4_COST = 1.1;", "public static final double FIST_OTHER = 0.95;",
          "public static final String STUN_FX = %s;" % json.dumps(TREE_STUN),
          "public static volatile long LOOKUPS = 0L;", "public static volatile long STUNS = 0L;", "public static volatile long ECHOES = 0L;",
          "public static volatile long DOUBLES = 0L;", "public static volatile long STRIKES = 0L;", "public static volatile long FISTS = 0L;",
          "public static volatile long HEALS = 0L;", "public static volatile String LAST_WHY = \"\";",
          # fix 2 (PROFILES-CONTRACT rule 3): u -> the last profile:epoch:<uuid> seen (first sight = baseline); u -> Long generation (+1 a change)
          "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap GEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long SWITCHES = 0L;"):
    F(atree, f)
M(atree, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# fix 2: gen(u) = the player's profile generation; a profile:epoch:<uuid> different from the last one seen (an absent epoch / the first value =
# baseline, no change) drops the player's cached answers and Rift Echo window and counts +1 (Kunai drops its Double Step state on a new gen)
M(atree, r"""
public static long gen(java.util.UUID u) {
  if (u == null) return 0L;
  Object g = GEN.get(u);
  long gv = g instanceof Long ? ((Long) g).longValue() : 0L;
  Object e = null;
  try { e = bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { e = null; }
  if (e == null) return gv;
  Object seen = EPOCH.put(u, e);
  if (seen == null || seen.equals(e)) return gv;
  gv = gv + 1L;
  GEN.put(u, Long.valueOf(gv));
  String pre = u.toString() + "|";
  java.util.Iterator it = CACHE.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k.startsWith(pre)) it.remove(); }
  ECHO.remove(u);
  SWITCHES = SWITCHES + 1L;
  return gv;
}""")
M(atree, r"""
public static double b(java.util.UUID u, String key) {
  if (u == null || key == null) return 0.0;
  gen(u);          // fix 2: a profile switch drops this player's cache first
  String ck = u.toString() + "|" + key;
  long now = System.currentTimeMillis();
  Object c = CACHE.get(ck);
  if (c instanceof double[] && now - (long) ((double[]) c)[1] < CACHE_MS) return ((double[]) c)[0];
  double v = 0.0;
  try {
    Object f = bridge().get("tree:fn:bonus");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Number) v = ((Number) r).doubleValue();
    }
  } catch (Throwable t) { v = 0.0; }
  if (Double.isNaN(v) || Double.isInfinite(v) || v < 0.0) v = 0.0;
  if (CACHE.size() > 4096) CACHE.clear();
  CACHE.put(ck, new double[] { v, (double) now });
  LOOKUPS = LOOKUPS + 1L;
  return v;
}""")
M(atree, r"""
public static void publish() {
  try { bridge().put(READS_KEY, KEYS); } catch (Throwable t) { }
}""")
M(atree, r"""
public static void unpublish() {
  try { bridge().remove(READS_KEY, KEYS); } catch (Throwable t) { }
}""")
M(atree, r"""
public static void clear() {
  CACHE.clear();
  ECHO.clear();
  EPOCH.clear();
  GEN.clear();
}""")
# Shadow Step's no-target step grows by 2/3 of the reach (Long Reach +3: 18 -> 20)
M(atree, r"""
public static double farOf(double reach) {
  return reach > 0.0 ? (double) Math.round(reach * 2.0 / 3.0) : 0.0;
}""")
# one stat paid only when the move happens (ArmoryTrav.takeStamina's rules for any stat): 1 = paid, 0 = too little (nothing taken), -1 = no
# stat readable (nothing taken, the move goes on)
M(atree, r"""
public static int take(@CAC@ acc, @REF@ r, int idx, double cost) {
  if (!(cost > 0.0)) return 1;
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null || idx < 0) return -1;
    @ESV@ v = m.get(idx);
    if (v == null) return -1;
    if ((double) v.get() + 1.0E-4 < cost) return 0;
    m.subtractStatValue(idx, (float) cost);
    return 1;
  } catch (Throwable t) { return -1; }
}""")
# Hard Return: the vanilla Stun effect on one enemy for secs (its own particles / tint; movement disabled) - false = it has no effect controller
M(atree, r"""
public static boolean stun(@CAC@ acc, @REF@ t, double secs) {
  try {
    if (t == null || !t.isValid() || !(secs > 0.0)) return false;
    @ECC@ c = (@ECC@) acc.getComponent(t, @ECC@.getComponentType());
    Object fx = @EFX@.getAssetMap().getAsset(STUN_FX);
    if (c == null || !(fx instanceof @EFX@)) return false;
    boolean ok = c.addEffect(t, (@EFX@) fx, (float) secs, @OVB@.OVERWRITE, acc);
    if (ok) STUNS = STUNS + 1L;
    return ok;
  } catch (Throwable x) { LAST_WHY = "stun failed: " + x; return false; }
}""")
'''
ATREE = ATREE.replace('json.dumps(",".join(READS))', repr(json.dumps(",".join(READS))))
assert "TREE_KEYS" not in ATREE and "READS" not in ATREE.replace("READS_KEY", "")
before('''# ---- TravFx: one live effect (kind 1 = blink trail, 2 = heal orb, 0 = a marker to remove)''', ATREE + "\n")

# ================================================================================================ TravFx + TravHeal: the Radiant Trail heal
rep('''  this.fxNext = 0L;
  this.ticks = 0;
}""")''', '''  this.fxNext = 0L;
  this.ticks = 0;
}""")
F(tfx, "public double heal;")          # 0.1.9 Radiant Trail: % of max Health a second the trail heals you + your party (0 = none)''')
rep('''for f in ("public java.util.UUID healer;", "public java.util.UUID[] who;", "public double[] hp;", "public @ST@ st;", "public String wand;"):
    F(theal, f)''', '''for f in ("public java.util.UUID healer;", "public java.util.UUID[] who;", "public double[] hp;", "public @ST@ st;", "public String wand;",
          "public boolean direct;"):          # 0.1.9: direct = Radiant Trail (a Mage heal: never class:fn:heal, which heals for Priests only)
    F(theal, f)''')
rep('''public void run() {
  try {
    java.util.function.Function f = @PKG@.ArmoryTrav.fn("class:fn:heal");''', '''public void run() {
  try {
    if (this.direct) {          // 0.1.9 Radiant Trail: straight into Health (room-clamped, never a dead player, no XP)
      for (int k = 0; k < this.who.length; k++) {
        if (this.who[k] == null || !(this.hp[k] > 0.0)) continue;
        double g = @PKG@.ArmoryTrav.healDirect(this.st, this.who[k], this.hp[k]);
        if (g > 0.0) { @PKG@.ArmoryTrav.HEALED = @PKG@.ArmoryTrav.HEALED + g; @PKG@.ArmoryTree.HEALS = @PKG@.ArmoryTree.HEALS + 1L; }
      }
      return;
    }
    java.util.function.Function f = @PKG@.ArmoryTrav.fn("class:fn:heal");''')

# ================================================================================================ the staff blink
OLD_BLINK_A = '''public static void blink(@PKG@.TravJob j) {'''
OLD_BLINK_B = '''# trav-fix: the world's MovementConfig MinFallSpeedToEngageRoll'''
NEW_BLINK = r'''public static void blink(@PKG@.TravJob j) {
  long now = System.currentTimeMillis();
  @PKG@.TravWorld tw = @PKG@.TravWorld.get(j.mst);
  int i = j.idx;
  double mana = (double) @PKG@.ArmoryDefs.S_C[i];
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(j.u); } catch (Throwable t0) { pr = null; }
  @REF@ ref = (pr == null || !pr.isValid()) ? null : pr.getReference();
  @ST@ st = (ref == null || !ref.isValid()) ? null : ref.getStore();
  if (st == null || st != j.mst) { LAST_WHY = "the caster left this world"; dropMarker(tw, j.marker, now); return; }
  String why = null;
  @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  @VEC@ pos = tc == null ? null : tc.getPosition();
  double[] d = j.dir;
  @WLD@ w = worldOf(st);
  Object last = LAST.get(j.u);
  // 0.1.9 the class tree (SkyyTrees tree:fn:bonus, 1 s cache): Long Blink (T3: + ranked blocks, trail + 1 s), Spell Focus (T2 %), Blink Slash
  // (PA1 %, + 20 % Mana), Rift Echo (PA2: a 2nd blink within 2 s is free - Mana back, half Stamina - then Amount s cooldown), Radiant Trail (PB1)
  double tLong = @PKG@.ArmoryTree.b(j.u, "Class.Mage.T3");
  double tFocus = @PKG@.ArmoryTree.b(j.u, "Class.Mage.T2");
  double tSlash = @PKG@.ArmoryTree.b(j.u, "Class.Mage.PA1");
  double tEcho = @PKG@.ArmoryTree.b(j.u, "Class.Mage.PA2");
  double tRad = @PKG@.ArmoryTree.b(j.u, "Class.Mage.PB1");
  Object eoo = @PKG@.ArmoryTree.ECHO.get(j.u);
  long[] eo = null;
  if (eoo instanceof long[]) eo = (long[]) eoo;
  boolean echo = tEcho > 0.0 && eo != null && now - eo[0] <= @PKG@.ArmoryTree.ECHO_MS && eo[1] == 0L;
  if (pos == null || d == null || w == null) why = "no position or direction";
  else if (dead(st, ref)) why = "dead";
  else if (!allowed(j.u, @PKG@.ArmoryDefs.S_IDS[i]) || !allowed(j.u, handItem(st, ref))) why = "class lock";     // trav-fix: the CAST staff too
  else if (eo != null && eo[2] > now) why = "cooldown";          // 0.1.9: Rift Echo's cooldown after the free second blink
  else if (!echo && @PKG@.ArmoryCfg.BLINK_CD > 0.0 && last instanceof Long && now - ((Long) last).longValue() < Math.round(@PKG@.ArmoryCfg.BLINK_CD * 1000.0)) why = "cooldown";
  double t = 0.0;
  if (why == null) {
    t = @PKG@.TravMath.scan(grid(w), pos.x, pos.y, pos.z, d[0], d[1], d[2], (double) @PKG@.ArmoryCfg.BLINK_DIST + tLong, @PKG@.ArmoryCfg.BLINK_FLOOR);
    if (!(t > 0.0)) why = "no free spot ahead";
  }
  double cost = @PKG@.TravMath.staminaCost(mana, @PKG@.ArmoryCfg.STAMINA_PCT, @PKG@.ArmoryCfg.STAMINA_CAP);
  if (echo) cost = cost / 2.0;
  if (why == null && takeStamina(st, ref, cost) == 0) {
    why = "too little Stamina";
    tell(pr, "Not enough Stamina to blink - " + @PKG@.TravMath.fmt(cost) + " needed.");
  }
  double extra = (!echo && tSlash > 0.0) ? mana * @PKG@.ArmoryTree.SLASH_MANA : 0.0;
  if (why == null && extra > 0.0 && @PKG@.ArmoryTree.take(st, ref, @DST@.getMana(), extra) == 0) {
    addStat(st, ref, @DST@.getStamina(), cost);          // the Stamina just paid comes back
    why = "too little Mana (Blink Slash)";
    tell(pr, "Not enough Mana to blink - Blink Slash needs " + @PKG@.TravMath.fmt(extra) + " more.");
  }
  if (why != null) {
    addStat(st, ref, @DST@.getMana(), mana);     // a blink that does not move you costs NOTHING (Skyy 2026-10-05): the chain's Mana back
    REFUNDS = REFUNDS + 1L;
    LAST_WHY = why;
    dropMarker(tw, j.marker, now);
    return;
  }
  double sx = pos.x;
  double sy = pos.y;
  double sz = pos.z;
  double ex = sx + d[0] * t;
  double ey = sy + d[1] * t;
  double ez = sz + d[2] * t;
  @TP@ tp = @TP@.createForPlayer(w, new @VEC@(ex, ey, ez), tc.getRotation());
  try {
    @HR@ hr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
    if (hr != null && hr.getRotation() != null) tp.setHeadRotation(hr.getRotation());
  } catch (Throwable t2) { }
  if (@PKG@.ArmoryCfg.BLINK_KEEPFALL) tp = tp.withoutVelocityReset();
  st.putComponent(ref, @TP@.getComponentType(), tp);
  LAST.put(j.u, Long.valueOf(now));
  if (echo) {
    addStat(st, ref, @DST@.getMana(), mana);          // Rift Echo: the second blink is free (the chain's Mana back)
    @PKG@.ArmoryTree.ECHO.put(j.u, new long[] { now, 1L, now + Math.round(tEcho * 1000.0) });
    @PKG@.ArmoryTree.ECHOES = @PKG@.ArmoryTree.ECHOES + 1L;
  } else @PKG@.ArmoryTree.ECHO.put(j.u, new long[] { now, 0L, 0L });
  BLINKS = BLINKS + 1L;
  LAST_WHY = "blink " + @PKG@.TravMath.fmt(t) + " blocks" + (echo ? " (Rift Echo - free)" : "");
  effect(ref, FX_PORTAL, st);
  sound(SND_BLINK, sx, sy, sz, st);
  sound(SND_BLINK, ex, ey, ez, st);
  double secs = @PKG@.ArmoryCfg.TRAIL_SECONDS + (tLong > 0.0 ? 1.0 : 0.0);          // 0.1.9 Long Blink: the trail lasts 1 s longer
  if (!@PKG@.ArmoryCfg.TRAIL_ON || !(@PKG@.ArmoryCfg.TRAIL_SECONDS > 0.0)) { dropMarker(tw, j.marker, now); return; }
  long step = Math.round(@PKG@.ArmoryCfg.BLINK_TICK * 1000.0);
  if (step < 50L) step = 50L;
  double per = @PKG@.TravMath.perTick((double) @PKG@.ArmoryDefs.S_CD[i], (double) @PKG@.ArmoryCfg.TRAIL_PCT, step);
  per = per * (1.0 + tFocus / 100.0) * (1.0 + tSlash / 100.0) * (tRad > 0.0 ? @PKG@.ArmoryTree.RAD_DMG : 1.0);
  @PKG@.TravFx tf = new @PKG@.TravFx(1, sx, sy + 0.9, sz, ex, ey + 0.9, ez, @PKG@.ArmoryCfg.TRAIL_WIDTH / 2.0, now + Math.round(secs * 1000.0),
    now, step, per, j.u, j.marker, 5000 + i);
  tf.heal = tRad;
  tw.add(tf, @PKG@.ArmoryCfg.TRAV_MAXLIVE, now);
}""")
'''
_ob = s[s.index(OLD_BLINK_A):s.index(OLD_BLINK_B)]
assert s.count(OLD_BLINK_A) == 1 and _ob.count("public static void blink(") == 1 and _ob.rstrip().endswith('}""")'), _ob[-80:]
s = s.replace(_ob, NEW_BLINK)

# ================================================================================================ the trail tick: Radiant Trail heals you + your party
rep('''      if (hit(buf, r, caster, f.marker, f.amount)) TRAIL_HITS = TRAIL_HITS + 1L;
    }
    f.ticks = f.ticks + 1;
    return;
  }''', '''      if (hit(buf, r, caster, f.marker, f.amount)) TRAIL_HITS = TRAIL_HITS + 1L;
    }
    if (f.heal > 0.0) {          // 0.1.9 Radiant Trail: you + your party inside the trail heal heal % of max Health a second
      java.util.ArrayList hu = new java.util.ArrayList();
      java.util.ArrayList hh = new java.util.ArrayList();
      for (int k = 0; k < l.size(); k++) {
        @REF@ r = (@REF@) l.get(k);
        if (kind(buf, r, caster, f.caster, pvp) != 2) continue;
        @VEC@ p = posOf(buf, r);
        if (p == null) continue;
        if (@PKG@.TravMath.segDist(p.x, p.y + 0.9, p.z, f.ax, f.ay, f.az, f.bx, f.by, f.bz) > f.r + 0.4) continue;
        try {
          @PR@ hp = (@PR@) buf.getComponent(r, @PR@.getComponentType());
          @ESM@ m = (@ESM@) buf.getComponent(r, @ESM@.getComponentType());
          @ESV@ hv = m == null ? null : m.get(@DST@.getHealth());
          if (hp == null || hp.getUuid() == null || hv == null) continue;
          double amt = (double) hv.getMax() * f.heal / 100.0 * (double) f.step / 1000.0;
          if (amt > 0.0) { hu.add(hp.getUuid()); hh.add(Double.valueOf(amt)); }
        } catch (Throwable th) { }
      }
      @WLD@ hw = worldOf(buf);
      if (!hu.isEmpty() && hw != null) {
        java.util.UUID[] who = new java.util.UUID[hu.size()];
        double[] hps = new double[hu.size()];
        for (int k = 0; k < who.length; k++) { who[k] = (java.util.UUID) hu.get(k); hps[k] = ((Double) hh.get(k)).doubleValue(); }
        @PKG@.TravHeal th2 = new @PKG@.TravHeal(f.caster, who, hps, st, null);
        th2.direct = true;
        hw.execute(th2);
      }
    }
    f.ticks = f.ticks + 1;
    return;
  }''')

# ================================================================================================ Gentle Hands (orb) + Spell Focus (Page Burst)
rep('''    double per = @PKG@.TravMath.perTick(healBase, (double) @PKG@.ArmoryCfg.ORB_HEAL_PCT, step);''',
    '''    double per = @PKG@.TravMath.perTick(healBase, (double) @PKG@.ArmoryCfg.ORB_HEAL_PCT, step);
    per = per * (1.0 + @PKG@.ArmoryTree.b(s.caster, "Class.Priest.T1") / 100.0);          // 0.1.9 Gentle Hands: the orb heals Amount % more''')
rep('''  if (!allowed(s.caster, @PKG@.ArmoryDefs.B_IDS[bi])) { LAST_WHY = "book: class lock"; return 0; }''',
    '''  if (!allowed(s.caster, @PKG@.ArmoryDefs.B_IDS[bi])) { LAST_WHY = "book: class lock"; return 0; }
  base = base * (1.0 + @PKG@.ArmoryTree.b(s.caster, "Class.Mage.T2") / 100.0);          // 0.1.9 Spell Focus: the Page Burst + Amount %''')

# ================================================================================================ the kunai
rep('''          "public static final java.util.concurrent.ConcurrentHashMap KNOCK = new java.util.concurrent.ConcurrentHashMap();",    # u -> {x, y, z, r, f, dmg}''',
    '''          "public static final java.util.concurrent.ConcurrentHashMap KNOCK = new java.util.concurrent.ConcurrentHashMap();",    # u -> {x, y, z, r, f, dmg, stun}
          "public static final java.util.concurrent.ConcurrentHashMap STRIKE = new java.util.concurrent.ConcurrentHashMap();",   # 0.1.9 u -> {x, y, z, dmg}
          "public static final java.util.concurrent.ConcurrentHashMap DUSED = new java.util.concurrent.ConcurrentHashMap();",    # 0.1.9 u -> Long (the port used)
          "public static final java.util.concurrent.ConcurrentHashMap DCD = new java.util.concurrent.ConcurrentHashMap();",      # 0.1.9 u -> Long (cooldown until)
          "public static final java.util.concurrent.ConcurrentHashMap DGEN = new java.util.concurrent.ConcurrentHashMap();",     # fix 2 u -> Long (the profile gen of DUSED / DCD)''')
# the metal's kunai hit (the return knockback's damage base) + the kunai test for the tune (Long Throw)
rep('''# kunai.noCombat (ArmoryHitSys, Inspect group): the time of a hit a player dealt or took''', '''# 0.1.9: one kunai hit of metal ki (the return's damage base): the jar's kunai damage x kunai.dpsShare / 0.8
M(kun, r"""
public static double hitOf(int ki) {
  if (ki < 0 || ki >= @PKG@.ArmoryDefs.K_DMG.length) ki = 0;
  return (double) @PKG@.ArmoryDefs.K_DMG[ki] * @PKG@.ArmoryCfg.K_SHARE / @PKG@.ArmoryDefs.K_SHARE_DEF;
}""")
# 0.1.9 Long Throw: a kunai hit (one of our kunai models) from an owner of Class.Assassin.PC1 x 0.9
M(kun, r"""
public static float treeTune(@CB@ buf, @REF@ proj, Object src) {
  try {
    if (proj == null || !proj.isValid() || !(src instanceof @DENT@)) return 1.0f;
    Object mc = buf.getComponent(proj, @MODC@.getComponentType());
    if (!(mc instanceof @MODC@) || ((@MODC@) mc).getModel() == null) return 1.0f;
    if (@PKG@.ArmoryDefs.kunaiModel(((@MODC@) mc).getModel().getModelAssetId()) < 0) return 1.0f;
    @REF@ a = ((@DENT@) src).getRef();
    @PR@ p = a == null ? null : prOf(buf, a);
    if (p == null) return 1.0f;
    return @PKG@.ArmoryTree.b(p.getUuid(), "Class.Assassin.PC1") > 0.0 ? (float) @PKG@.ArmoryTree.PC1_DMG : 1.0f;
  } catch (Throwable t) { return 1.0f; }
}""")
# kunai.noCombat (ArmoryHitSys, Inspect group): the time of a hit a player dealt or took''')
# onShot: Double Step (PC3) + Blink Strike's cost (PC4)
rep('''  Object lp = LASTPORT.get(u);
  String why = null;
  if (lp instanceof Long && now - ((Long) lp).longValue() < Math.round(@PKG@.ArmoryCfg.K_CD[i] * 1000.0)) why = "cooldown";''',
    '''  Object lp = LASTPORT.get(u);
  String why = null;
  // 0.1.9 Double Step (Class.Assassin.PC3): a second teleport throw within 3 s of a teleport ignores the cooldown (half Stamina, no Mana), then
  // the next waits the cooldown + Amount s
  double pc3 = @PKG@.ArmoryTree.b(u, "Class.Assassin.PC3");
  long lpv = lp instanceof Long ? ((Long) lp).longValue() : -1L;
  long dgen = @PKG@.ArmoryTree.gen(u);          // fix 2: another profile's Double Step state does not carry over
  Object dg = DGEN.get(u);
  if (dg instanceof Long && ((Long) dg).longValue() != dgen) { DUSED.remove(u); DCD.remove(u); DGEN.remove(u); }
  Object du = DUSED.get(u);
  boolean dbl = pc3 > 0.0 && lpv > 0L && now - lpv <= @PKG@.ArmoryTree.DOUBLE_MS && !(du instanceof Long && ((Long) du).longValue() == lpv);
  Object dc = DCD.get(u);
  if (dc instanceof Long && now < ((Long) dc).longValue()) why = "cooldown";
  else if (!dbl && lp instanceof Long && now - ((Long) lp).longValue() < Math.round(@PKG@.ArmoryCfg.K_CD[i] * 1000.0)) why = "cooldown";''')
rep('''  double stam = @PKG@.ArmoryCfg.K_STAM[i];
  double mana = @PKG@.ArmoryCfg.K_MANA[i];
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;
  if (@PKG@.Leap.take(buf, r, stam, mana) == 0) {''', '''  double stam = @PKG@.ArmoryCfg.K_STAM[i];
  double mana = @PKG@.ArmoryCfg.K_MANA[i];
  if (@PKG@.ArmoryTree.b(u, "Class.Assassin.PC4") > 0.0) { stam = stam * @PKG@.ArmoryTree.PC4_COST; mana = mana * @PKG@.ArmoryTree.PC4_COST; }   // 0.1.9 Blink Strike
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;
  if (dbl) { stam = stam / 2.0; mana = 0.0; }          // 0.1.9 Double Step
  if (@PKG@.Leap.take(buf, r, stam, mana) == 0) {''')
rep('''  @PKG@.KunaiState old = (@PKG@.KunaiState) STATES.get(u);
  if (old != null) cancel(old, buf, st, "a newer teleport kunai");''', '''  if (dbl) {
    DGEN.put(u, Long.valueOf(dgen));
    DUSED.put(u, Long.valueOf(lpv));
    DCD.put(u, Long.valueOf(now + Math.round(@PKG@.ArmoryCfg.K_CD[i] * 1000.0) + Math.round(pc3 * 1000.0)));
    @PKG@.ArmoryTree.DOUBLES = @PKG@.ArmoryTree.DOUBLES + 1L;
  }
  @PKG@.KunaiState old = (@PKG@.KunaiState) STATES.get(u);
  if (old != null) cancel(old, buf, st, "a newer teleport kunai");''')
# the return knockback: Hard Return's stun (the 7th number); Blink Strike (strike) - both on the next tick with the CommandBuffer
rep('''    if (kn[5] > 0.0) @PKG@.ArmoryTrav.hit(buf, t, r, null, kn[5]);
  }
  return n;
}""")''', '''    if (kn[5] > 0.0) @PKG@.ArmoryTrav.hit(buf, t, r, null, kn[5]);
    if (kn.length > 6 && kn[6] > 0.0) @PKG@.ArmoryTree.stun(buf, t, kn[6]);          // 0.1.9 Hard Return
  }
  return n;
}""")
# 0.1.9 Blink Strike: the nearest enemy within 3 blocks of where you arrived takes s[3] (a kunai teleport or a targeted Shadow Step)
M(kun, r"""
public static int strike(@REF@ r, @ST@ st, @CB@ buf, java.util.UUID u, double[] s) {
  if (s == null || s.length < 4 || !(s[3] > 0.0)) return 0;
  if (s.length > 4 && System.currentTimeMillis() - (long) s[4] > 1500L) { @PKG@.ArmoryTree.LAST_WHY = "Blink Strike: too old (left the game?)"; return 0; }   // fix: a strike left by a disconnect never fires later
  boolean pvp = @PKG@.ArmoryTrav.pvp(@PKG@.ArmoryTrav.worldOf(buf));
  java.util.List l = @PKG@.ArmoryTrav.near(buf, s[0], s[1], s[2], @PKG@.ArmoryTree.STRIKE_R + 1.0);
  @REF@ best = null;
  double bd = 1.0E9;
  for (int k = 0; k < l.size(); k++) {
    @REF@ t = (@REF@) l.get(k);
    if (t == null || t.equals(r)) continue;
    if (@PKG@.ArmoryTrav.kind(buf, t, r, u, pvp) != 0) continue;
    @VEC@ tp = @PKG@.ArmoryTrav.posOf(buf, t);
    if (tp == null) continue;
    double dx = tp.x - s[0];
    double dy = tp.y - s[1];
    double dz = tp.z - s[2];
    double dd = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (dd <= @PKG@.ArmoryTree.STRIKE_R && dd < bd) { best = t; bd = dd; }
  }
  if (best == null) { @PKG@.ArmoryTree.LAST_WHY = "Blink Strike: no enemy within 3 blocks"; return 0; }
  if (!@PKG@.ArmoryTrav.hit(buf, best, r, null, s[3])) return 0;
  @PKG@.ArmoryTree.STRIKES = @PKG@.ArmoryTree.STRIKES + 1L;
  @PKG@.ArmoryTree.LAST_WHY = "Blink Strike " + @PKG@.TravMath.fmt(s[3]);
  return 1;
}""")''')
rep('''  if (STATES.isEmpty() && FLY.isEmpty() && KNOCK.isEmpty()) return;''', '''  if (STATES.isEmpty() && FLY.isEmpty() && KNOCK.isEmpty() && STRIKE.isEmpty()) return;''')
rep('''  Object kn = KNOCK.remove(u);
  if (kn instanceof double[]) knock(r, st, buf, u, (double[]) kn);''', '''  Object kn = KNOCK.remove(u);
  if (kn instanceof double[]) knock(r, st, buf, u, (double[]) kn);
  Object sk0 = STRIKE.remove(u);          // 0.1.9 Blink Strike
  if (sk0 instanceof double[]) strike(r, st, buf, u, (double[]) sk0);''')
rep('''  double rg = @PKG@.ArmoryCfg.K_RANGE[i];
  double ox = s.lx - s.ex;''', '''  double rg = @PKG@.ArmoryCfg.K_RANGE[i] + @PKG@.ArmoryTree.b(u, "Class.Assassin.T3") + @PKG@.ArmoryTree.b(u, "Class.Assassin.PC1");   // 0.1.9 Long Reach + Long Throw
  double ox = s.lx - s.ex;''')
rep('''  RET.put(j.u, new double[] { sx, sy, sz, (double) (now + Math.round(@PKG@.ArmoryCfg.K_WIN[j.idx] * 1000.0)), (double) j.idx });''',
    '''  double win = @PKG@.ArmoryCfg.K_WIN[j.idx];
  if (@PKG@.ArmoryTree.b(j.u, "Class.Assassin.PC2") > 0.0) win = Math.max(1.0, win - @PKG@.ArmoryTree.WIN_CUT);          // 0.1.9 Hard Return: 2 s shorter
  RET.put(j.u, new double[] { sx, sy, sz, (double) (now + Math.round(win * 1000.0)), (double) j.idx });
  double pc4 = @PKG@.ArmoryTree.b(j.u, "Class.Assassin.PC4");          // 0.1.9 Blink Strike: the next tick hits the nearest enemy within 3 blocks
  if (pc4 > 0.0) STRIKE.put(j.u, new double[] { ex, ey, ez, hitOf(j.idx) * pc4 / 10.0, (double) now });''')
rep('''  KNOCK.put(j.u, new double[] { sp[0], sp[1], sp[2], @PKG@.ArmoryCfg.K_RAD[ki], @PKG@.ArmoryCfg.K_FORCE, hit });''',
    '''  double pc2 = @PKG@.ArmoryTree.b(j.u, "Class.Assassin.PC2");          // 0.1.9 Hard Return: knockback x Amount + a 0.4 s stun
  KNOCK.put(j.u, new double[] { sp[0], sp[1], sp[2], @PKG@.ArmoryCfg.K_RAD[ki], @PKG@.ArmoryCfg.K_FORCE * (pc2 > 0.0 ? pc2 : 1.0), hit, pc2 > 0.0 ? @PKG@.ArmoryTree.STUN_S : 0.0 });''')

# ================================================================================================ Shadow Step: Long Reach + Blink Strike
rep('''public static @REF@ pick(@CAC@ acc, @REF@ me, java.util.UUID u, double ex, double ey, double ez, double[] d, @PKG@.TravGrid g, boolean pvp) {
  if (g == null || d == null) return null;
  java.util.List l = near(acc, ex, ey, ez, (double) @PKG@.ArmoryCfg.SS_RANGE + 2.0);''',
    '''public static @REF@ pickR(@CAC@ acc, @REF@ me, java.util.UUID u, double ex, double ey, double ez, double[] d, @PKG@.TravGrid g, boolean pvp, double rng) {
  if (g == null || d == null) return null;
  java.util.List l = near(acc, ex, ey, ez, rng + 2.0);''')
rep('''    if (dist > (double) @PKG@.ArmoryCfg.SS_RANGE || dist < 0.3) continue;''', '''    if (dist > rng || dist < 0.3) continue;''')
rep('''    if (tr < bt || off < bo - 1.0E-6 || (Math.abs(off - bo) <= 1.0E-6 && dist < bd)) { best = t; bt = tr; bo = off; bd = dist; }
  }
  return best;
}""")''', '''    if (tr < bt || off < bo - 1.0E-6 || (Math.abs(off - bo) <= 1.0E-6 && dist < bd)) { best = t; bt = tr; bo = off; bd = dist; }
  }
  return best;
}""")
# 0.1.8's signature (the targetRange row); 0.1.9's step passes the range + Long Reach
M(shd, r"""
public static @REF@ pick(@CAC@ acc, @REF@ me, java.util.UUID u, double ex, double ey, double ez, double[] d, @PKG@.TravGrid g, boolean pvp) {
  return pickR(acc, me, u, ex, ey, ez, d, g, pvp, (double) @PKG@.ArmoryCfg.SS_RANGE);
}""")''')
rep('''  @REF@ tgt = pick(st, ref, j.u, ex, ey, ez, new double[] { dx, dy, dz }, g, @PKG@.ArmoryTrav.pvp(w));''',
    '''  double reach = @PKG@.ArmoryTree.b(j.u, "Class.Assassin.T3");          // 0.1.9 Long Reach: 24 -> 27 (no target 18 -> 20)
  double pc4 = @PKG@.ArmoryTree.b(j.u, "Class.Assassin.PC4");            // 0.1.9 Blink Strike
  @REF@ tgt = pickR(st, ref, j.u, ex, ey, ez, new double[] { dx, dy, dz }, g, @PKG@.ArmoryTrav.pvp(w), (double) @PKG@.ArmoryCfg.SS_RANGE + reach);''')
rep('''    double t = @PKG@.TravMath.scan(g, sx, sy, sz, dx, dy, dz, (double) @PKG@.ArmoryCfg.SS_FAR, 0);          // no void check (Skyy)''',
    '''    double t = @PKG@.TravMath.scan(g, sx, sy, sz, dx, dy, dz, (double) @PKG@.ArmoryCfg.SS_FAR + @PKG@.ArmoryTree.farOf(reach), 0);          // no void check (Skyy)''')
rep('''  double stam = @PKG@.ArmoryCfg.SS_STAM;
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;''',
    '''  double stam = @PKG@.ArmoryCfg.SS_STAM;
  if (pc4 > 0.0) stam = stam * @PKG@.ArmoryTree.PC4_COST;          // 0.1.9 Blink Strike: the step costs 10 % more Stamina
  if (@PKG@.ArmoryCfg.STAMINA_CAP > 0 && stam > (double) @PKG@.ArmoryCfg.STAMINA_CAP) stam = (double) @PKG@.ArmoryCfg.STAMINA_CAP;''')
rep('''  if (tgt != null) {
    ARMED.put(j.u, Long.valueOf(now + Math.round(@PKG@.ArmoryCfg.SS_WINDOW * 1000.0)));
    TARGETED = TARGETED + 1L;''', '''  if (tgt != null) {
    ARMED.put(j.u, Long.valueOf(now + Math.round(@PKG@.ArmoryCfg.SS_WINDOW * 1000.0)));
    TARGETED = TARGETED + 1L;
    if (pc4 > 0.0) {          // 0.1.9 Blink Strike: the next tick hits the target (the dagger metal's kunai hit x Amount / 10)
      int ki = 0;
      for (int k = 0; k < @PKG@.ArmoryDefs.K_METALS.length; k++) if (@PKG@.ArmoryDefs.K_METALS[k].equals(@PKG@.ArmoryDefs.SS_METALS[mi])) ki = k;
      @PKG@.Kunai.STRIKE.put(j.u, new double[] { tx, ty, tz, @PKG@.Kunai.hitOf(ki) * pc4 / 10.0, (double) now });
    }''')

# ================================================================================================ Hard Knuckles (Stun.fist) + the tune wiring
rep('''# the engine glue (ArmoryTuneSys, the Filter group): a player's MELEE hit (EntitySource, not a projectile) on an NPC -> onHit (true = cancelled);''',
    '''# 0.1.9 Hard Knuckles (Class.Monk.PB1): a player's melee fist hit - the wraps' power hit / the gauntlets' finisher x (1 + Amount %), the other
# jabs x 0.95. The power hit is told apart by the hit's INITIAL damage: the closer of the fist weapon's jab / power number (our own chains,
# FIST_*); UNVERIFIED in game (another mod's earlier filter changes only the amount, never the initial one - read in Damage)
for f in ("public static final String[] FIST_IDS = %s;" % jarr([i_ for i_, j_, p_ in FIST_TAB]),
          "public static final double[] FIST_JAB = new double[] { %s };" % ", ".join(repr(j_) for i_, j_, p_ in FIST_TAB),
          "public static final double[] FIST_POW = new double[] { %s };" % ", ".join(repr(p_) for i_, j_, p_ in FIST_TAB)):
    F(stun, f)
M(stun, r"""
public static void fist(@CB@ buf, @DMG@ d) {
  try {
    if (d == null || d.isCancelled() || d.getAmount() <= 0.0f) return;
    Object src = d.getSource();
    if (!(src instanceof @DENT@) || src instanceof @DPRJ@) return;
    if (@PKG@.ArmoryTrav.MINE.containsKey(d)) return;
    @REF@ a = ((@DENT@) src).getRef();
    if (a == null) return;
    @PR@ ap = @PKG@.Kunai.prOf(buf, a);
    if (ap == null) return;
    java.util.UUID u = ap.getUuid();
    String item = hand(buf, a, u);
    if (item == null || !item.startsWith("Weapon_Fist_")) return;
    int fi = -1;
    for (int i = 0; i < FIST_IDS.length; i++) if (FIST_IDS[i].equals(item)) fi = i;
    if (fi < 0) return;
    double pb = @PKG@.ArmoryTree.b(u, "Class.Monk.PB1");
    if (!(pb > 0.0)) return;
    double init = (double) d.getInitialAmount();
    boolean power = Math.abs(init - FIST_POW[fi]) < Math.abs(init - FIST_JAB[fi]);
    double f = power ? 1.0 + pb / 100.0 : @PKG@.ArmoryTree.FIST_OTHER;
    d.setAmount((float) ((double) d.getAmount() * f));
    @PKG@.ArmoryTree.FISTS = @PKG@.ArmoryTree.FISTS + 1L;
    @PKG@.ArmoryTree.LAST_WHY = (power ? "Hard Knuckles power hit x" : "Hard Knuckles jab x") + @PKG@.TravMath.fmt(f);
  } catch (Throwable t) { warn("fist:" + t.getClass().getName(), "Hard Knuckles failed (" + t + ") - that hit was left alone"); }
}""")
# the engine glue (ArmoryTuneSys, the Filter group): a player's MELEE hit (EntitySource, not a projectile) on an NPC -> onHit (true = cancelled);''')
rep('''    if (chunk != null) @PKG@.Shadow.filter(buf, chunk.getReferenceTo(idx), (@DMG@) ev);        // 0.1.8: the Shadow Step backstab''',
    '''    if (chunk != null) @PKG@.Shadow.filter(buf, chunk.getReferenceTo(idx), (@DMG@) ev);        // 0.1.8: the Shadow Step backstab
    @PKG@.Stun.fist(buf, (@DMG@) ev);                                                            // 0.1.9: Hard Knuckles (Class.Monk.PB1)''')
rep('''      float kf = @PKG@.Kunai.tuneOf(buf, ((@DPRJ@) src).getProjectile());''',
    '''      float kf = @PKG@.Kunai.tuneOf(buf, ((@DPRJ@) src).getProjectile()) * @PKG@.Kunai.treeTune(buf, ((@DPRJ@) src).getProjectile(), src);   // 0.1.9 Long Throw x0.9''')

# ================================================================================================ the plugin: tree:reads:SkyyArmory, the caches
rep('''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow"]''',
    '''               "armory:grapple", "armory:leap", "armory:book", "armory:kunai", "armory:stun", "armory:shadow"]
# 0.1.9: tree:reads:SkyyArmory is put by ArmoryTree.publish (setup, after the config load) and removed by ArmoryTree.unpublish (only our value)''')
rep('''  b.put("armory:shadow", @PKG@.ArmoryCfg.SHADOW_TEXT);          // 0.1.8
}""")''', '''  b.put("armory:shadow", @PKG@.ArmoryCfg.SHADOW_TEXT);          // 0.1.8
  @PKG@.ArmoryTree.publish();          // 0.1.9: tree:reads:SkyyArmory = the class nodes this build applies
}""")''')
rep('''    for (int i = 0; i < k.length; i++) b.remove(k[i]);
  } catch (Throwable t) { }
}""" % jarr(BRIDGE_KEYS))''', '''    for (int i = 0; i < k.length; i++) b.remove(k[i]);
  } catch (Throwable t) { }
  @PKG@.ArmoryTree.unpublish();          // 0.1.9
}""" % jarr(BRIDGE_KEYS))''')
rep('''  @PKG@.Shadow.LAST.clear();          // 0.1.8
  @PKG@.Shadow.ARMED.clear();
  systems();''', '''  @PKG@.Shadow.LAST.clear();          // 0.1.8
  @PKG@.Shadow.ARMED.clear();
  @PKG@.ArmoryTree.clear();          // 0.1.9
  @PKG@.Kunai.STRIKE.clear();
  @PKG@.Kunai.DUSED.clear();
  @PKG@.Kunai.DCD.clear();
  @PKG@.Kunai.DGEN.clear();
  systems();''')
rep('''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SHADOW_TEXT);''', '''  @PKG@.ArmoryLog.info("@VERSION@ " + @PKG@.ArmoryCfg.SHADOW_TEXT);
  @PKG@.ArmoryLog.info("@VERSION@ class tree reader: tree:reads:SkyyArmory = " + @PKG@.ArmoryTree.KEYS + " (SkyyTrees tree:fn:bonus " + (@PKG@.ArmoryTree.bridge().get("tree:fn:bonus") != null ? "found" : "not loaded yet - read at use time") + ")");''')
rep('''  @PKG@.Shadow.LAST.clear();          // 0.1.8
  @PKG@.Shadow.ARMED.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  @PKG@.Shadow.LAST.clear();          // 0.1.8
  @PKG@.Shadow.ARMED.clear();
  @PKG@.ArmoryTree.clear();          // 0.1.9
  @PKG@.Kunai.STRIKE.clear();
  @PKG@.Kunai.DUSED.clear();
  @PKG@.Kunai.DCD.clear();
  @PKG@.Kunai.DGEN.clear();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')

# ================================================================================================ checks on the result + write
assert s.count("registerSystem(") == SYS0, "0.1.9 adds no system"
_ix = s.index
assert _ix('atree = pool.makeClass(PKG + ".ArmoryTree")') < _ix("public static double b(java.util.UUID u, String key) {") < _ix("public static void blink(@PKG@.TravJob j) {")
assert _ix("public static boolean stun(@CAC@ acc, @REF@ t, double secs) {") < _ix("public static int knock(@REF@ r, @ST@ st, @CB@ buf, java.util.UUID u, double[] kn) {")
assert _ix("public static int strike(@REF@ r, @ST@ st, @CB@ buf, java.util.UUID u, double[] s) {") < _ix("if (STATES.isEmpty() && FLY.isEmpty() && KNOCK.isEmpty() && STRIKE.isEmpty()) return;")
assert _ix("public static double hitOf(int ki) {") < _ix("public static void teleport(@PKG@.KunaiJob j) {") < _ix("public static void step(@PKG@.KunaiJob j) {")
assert _ix("public static float treeTune(@CB@ buf, @REF@ proj, Object src) {") < _ix("public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {\n  try {\n    if (!(ev instanceof @DMG@)) return;\n    if (chunk != null) @PKG@.Stun.filter")
assert _ix("public static void fist(@CB@ buf, @DMG@ d) {") < _ix("@PKG@.Stun.fist(buf, (@DMG@) ev);")
assert _ix("public static @REF@ pickR(") < _ix("public static @REF@ pick(@CAC@ acc") < _ix("public static void step(@PKG@.KunaiJob j) {")
compile(s, DST, "exec")
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))

R13_TEXT = r'''    # ============================================================================ R13. 0.1.9 THE CLASS TREE READER - every new path EXECUTED
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    ATR = JClass(PKG + "ArmoryTree")
    Lng = JClass("java.lang.Long")
    TREEV = {}

    @JImplements("java.util.function.Function")
    class TreeBonus:          # the stand-in SkyyTrees: tree:fn:bonus answers per (player, key)
        def __init__(self): self.calls = []
        @JOverride
        def apply(self, o):
            k_ = (str(o[0]), str(o[1]))
            self.calls.append(k_)
            return JClass("java.lang.Double").valueOf(float(TREEV.get(k_, 0.0)))
    tbonus = TreeBonus()
    br.put("tree:fn:bonus", tbonus)

    def tree(**kv):
        TREEV.clear()
        for k_, v_ in kv.items():
            TREEV[(str(cu), "Class." + k_.replace("_", "."))] = float(v_)
        ATR.CACHE.clear()
    # --- R13a. the reader + tree:reads:SkyyArmory
    tree(Mage_T3=2)
    r1_ = float(ATR.b(cu, "Class.Mage.T3"))
    TREEV[(str(cu), "Class.Mage.T3")] = 5.0
    r2_ = float(ATR.b(cu, "Class.Mage.T3"))          # cached (1 s)
    ATR.CACHE.clear()
    r3_ = float(ATR.b(cu, "Class.Mage.T3"))
    br.remove("tree:fn:bonus")
    ATR.CACHE.clear()
    r4_ = float(ATR.b(cu, "Class.Mage.T3"))
    br.put("tree:fn:bonus", tbonus)
    TREEV[(str(cu), "Class.Mage.T3")] = -3.0
    ATR.CACHE.clear()
    r5_ = float(ATR.b(cu, "Class.Mage.T3"))
    PL13 = JClass(PKG + "SkyyArmoryPlugin")
    PL13.publish()
    rd_ = str(br.get("tree:reads:SkyyArmory"))
    PL13.unpublish()
    rd2_ = br.get("tree:reads:SkyyArmory")
    br.put("tree:reads:SkyyArmory", "someone else")
    PL13.unpublish()
    rd3_ = str(br.get("tree:reads:SkyyArmory"))
    br.remove("tree:reads:SkyyArmory")
    want_keys = ["Class.Mage.T2", "Class.Mage.T3", "Class.Mage.PA1", "Class.Mage.PA2", "Class.Mage.PB1", "Class.Priest.T1",
                 "Class.Assassin.T3", "Class.Assassin.PC1", "Class.Assassin.PC2", "Class.Assassin.PC3", "Class.Assassin.PC4"]
    check((r1_, r2_, r3_, r4_, r5_) == (2.0, 2.0, 5.0, 0.0, 0.0) and rd_.split(",") == want_keys and rd2_ is None and rd3_ == "someone else"
          and "Class.Mage.PA5" not in rd_ and "Class.Monk.PB1" not in rd_,
          "R13a (map section 6): ArmoryTree.b = SkyyTrees' tree:fn:bonus answer (2), cached 1 s (still 2 after a change), fresh after the cache (5); "
          "no SkyyTrees / a negative answer = 0; tree:reads:SkyyArmory = exactly the 11 keys it applies (Rift Master PA5 waits; fix 2: Hard Knuckles held) at publish, removed "
          "at unpublish, another mod's value kept: %s %s %s %s" % ((r1_, r2_, r3_, r4_, r5_), rd_, rd2_, rd3_))

    # --- R13a2 fix 2: a profile switch (PROFILES-CONTRACT rule 3) drops the player's cached answers + Rift Echo window
    ek13 = "profile:epoch:" + str(cu)
    ATR.EPOCH.clear()
    ATR.GEN.clear()
    br.remove(ek13)
    tree(Mage_T3=2)
    g0_ = int(ATR.gen(cu))
    br.put(ek13, Lng(3))
    g1_ = int(ATR.gen(cu))
    e1_ = float(ATR.b(cu, "Class.Mage.T3"))
    TREEV[(str(cu), "Class.Mage.T3")] = 4.0
    ATR.ECHO.put(cu, Lng(1))
    e2_ = float(ATR.b(cu, "Class.Mage.T3"))
    echo_kept = ATR.ECHO.get(cu) is not None
    sw0_ = int(ATR.SWITCHES)
    br.put(ek13, Lng(4))
    e3_ = float(ATR.b(cu, "Class.Mage.T3"))
    echo_gone = ATR.ECHO.get(cu) is None
    g2_ = int(ATR.gen(cu))
    g3_ = int(ATR.gen(cu))
    br.remove(ek13)
    g4_ = int(ATR.gen(cu))
    check((g0_, g1_, e1_, e2_, echo_kept, e3_, echo_gone, g2_, g3_, g4_, int(ATR.SWITCHES) - sw0_) == (0, 0, 2.0, 2.0, True, 4.0, True, 1, 1, 1, 1),
          "R13a2 FIX (profile switch): no epoch / the first epoch = a baseline (gen 0); the same epoch keeps the 1 s cache and the Echo window; a new "
          "epoch drops both (the fresh answer 4) and counts one switch: %s" % ((g0_, g1_, e1_, e2_, echo_kept, e3_, echo_gone, g2_, g3_, g4_),))
    ATR.EPOCH.clear()
    ATR.GEN.clear()
    ATR.ECHO.clear()

    # --- R13b. the staff blink (TravJob kind 1 -> ArmoryTrav.blink) with the Mage nodes
    AT.GRID = Grid(world_fn())
    AT.NEAR = NearR()
    nb_ = [9300]

    def blink13(mana=200.0, stam=10.0, d=(1.0, 0.0, 0.0)):
        put(rc, TPc.getComponentType(), None)
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        mc.setStatValue(MANA, JFloat(mana))
        mc.setStatValue(STAM, JFloat(stam))
        tw_ = TW.of(tst)
        n0_ = 0 if tw_ is None else int(tw_.fx.size())
        nb_[0] += 1
        TJ(1, cu, "trav-test", tst, REFc(tst, nb_[0]), JArray(JDouble)([float(x_) for x_ in d]), I_IRON).run()
        tp_ = comp(rc, TPc.getComponentType())
        tw_ = TW.of(tst)
        fx_ = tw_.fx.get(tw_.fx.size() - 1) if tw_ is not None and int(tw_.fx.size()) > n0_ else None
        return (None if tp_ is None else round(float(tp_.getPosition().x()), 3), sv(mc, MANA), sv(mc, STAM),
                None if fx_ is None else round(float(fx_.amount), 5), None if fx_ is None else int(round((int(fx_.until) - nowms()) / 1000.0)),
                None if fx_ is None else float(fx_.heal), str(AT.LAST_WHY)), fx_

    def breset():
        AT.LAST.clear()
        ATR.ECHO.clear()
        ATR.CACHE.clear()
        TW.ALL.clear()
    breset()
    tree()
    b0, _f = blink13()
    breset()
    tree(Mage_T3=2)
    bl, _f = blink13()
    breset()
    tree(Mage_T2=5, Mage_PA1=50)
    bs_, _f = blink13()
    breset()
    tree(Mage_PA1=50)
    blow, _f = blink13(mana=3.0)
    check(b0[:5] == (16.5, 200.0, 5.0, 26.25, 3) and b0[5] == 0.0 and bl[0] == 18.5 and bl[4] == 4 and bl[3] == 26.25
          and bs_[0] == 16.5 and bs_[3] == round(26.25 * 1.05 * 1.5, 5) and bs_[1] == 194.0 and blow[0] is None and blow[1:3] == (33.0, 10.0)
          and blow[6] == "too little Mana (Blink Slash)",
          "R13b (Class-Tree-Paths Mage): no node = 16 blocks, trail 26.25 / tick for 3 s; Long Blink +2 = 18 blocks and a 4 s trail; Spell Focus 5 %% x "
          "Blink Slash 50 %% = 26.25 x 1.05 x 1.5 per tick and Blink Slash takes 6 more Mana (20 %% of 30: 200 -> 194); too little Mana for it = no "
          "blink, the chain's 30 Mana back and the Stamina back: %s | %s | %s | %s" % (b0, bl, bs_, blow))
    breset()
    tree(Mage_PA2=3)
    e1, _f = blink13()
    e2, _f = blink13()
    eo2 = ATR.ECHO.get(cu)
    e3, _f = blink13()
    breset()
    ACfg.BLINK_CD = 5.0
    e4, _f = blink13()
    e5, _f = blink13()
    e6, _f = blink13()
    ACfg.BLINK_CD = 0.0
    breset()
    tree()
    n1, _f = blink13()
    n2, _f = blink13()
    check(e1[:3] == (16.5, 200.0, 5.0) and e2[:3] == (16.5, 230.0, 7.5) and "Rift Echo" in e2[6] and eo2 is not None and int(eo2[1]) == 1
          and 2900 <= int(eo2[2]) - nowms() <= 3100 and e3[0] is None and e3[6] == "cooldown" and e3[1] == 230.0
          and e4[0] == 16.5 and e5[0] == 16.5 and "Rift Echo" in e5[6] and e6[0] is None and n1[:3] == (16.5, 200.0, 5.0) and n2[:3] == (16.5, 200.0, 5.0),
          "R13b (Rift Echo): a second blink within 2 s is free - the chain's 30 Mana back (200 -> 230), half the Stamina (2.5) - then the next blink "
          "waits 3 s (cooldown, nothing spent); it passes blink.cooldown 5 s; without the node every blink costs the same: %s %s %s %s %s %s %s" % (
              e1, e2, e3, e4, e5, e6, n2))
    breset()
    tree(Mage_PB1=5)
    rb, rfx = blink13()
    mp.setStatValue(HP, JFloat(50.0))
    ms.setStatValue(HP, JFloat(50.0))
    put(rp, TCc.getComponentType(), TCc(V3(8.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    put(rs, TCc.getComponentType(), TCc(V3(9.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    NEARL[:] = [rc, rp, rs]
    br.put("party:fn:members", Members())          # p2 is the caster's party (the Q section left the grapple player's party in)
    reset_buf()
    AT.tickFx(rfx, tst, tbuf, nowms())
    jh_ = list(TWd.JOBS)
    TWd.JOBS.clear()
    heal_who = [] if not jh_ else [str(x_) for x_ in jh_[0].who]
    heal_dir = bool(jh_[0].direct) if jh_ else None
    for j_ in jh_:
        j_.run()
    hp_p, hp_s = sv(mp, HP), sv(ms, HP)
    check(rb[3] == round(26.25 * 0.75, 5) and rb[5] == 5.0 and len(jh_) == 1 and heal_dir is True and heal_who == [str(cu), str(pu)]
          and hp_p == 52.5 and hp_s == 50.0 and events() == [],
          "R13b (Radiant Trail): the trail deals x 0.75 (19.6875 / tick) and every 0.5 s tick heals you + your party inside it 5 %% of max Health a "
          "second (2.5 per tick: 50 -> 52.5) through ONE direct TravHeal (no class:fn:heal - the Mage is no Priest); a stranger is never healed, "
          "nobody is hit: %s, %s, %s, %s / %s" % (rb, heal_dir, heal_who, hp_p, hp_s))
    NEARL[:] = []

    # --- R13c. the wand heal orb (Gentle Hands) + the spellbook Page Burst (Spell Focus)
    TSh = JClass(PKG + "TravShot")

    def orb13():
        TW.ALL.clear()
        TW.get(tst)
        AT.burst(tst, tbuf, None, TSh(0.5, 64.0, 0.5, 0.0, 2001, cu, "x"), 0.5, 64.0, 0.5, None, 0.0, 100.0)
        tw_ = TW.of(tst)
        return None if tw_ is None or tw_.fx.size() == 0 else round(float(tw_.fx.get(tw_.fx.size() - 1).amount), 6)
    tree()
    o0 = orb13()
    tree(Priest_T1=10)
    o1 = orb13()
    mob13 = mob(9351, 3.0, 64.0, 0.5, (0.6, 1.8, 0.6))
    NEARL[:] = [mob13]

    def book13():
        reset_buf()
        AT.bookBurst(tst, tbuf, None, TSh(3.0, 64.9, 0.5, 30.0, 7000, cu, "x"), 3.0, 64.9, 0.5, None, 100.0)
        ev_ = events()
        return ev_[0][1] if ev_ else None
    tree()
    k0 = book13()
    tree(Mage_T2=5)
    k1 = book13()
    NEARL[:] = []
    check(o0 is not None and o1 is not None and abs(o1 - o0 * 1.1) < 1e-6 and k0 is not None and k1 is not None and abs(k1 - k0 * 1.05) < 1e-3,
          "R13c: Gentle Hands 10 %% = the heal orb's per-tick heal x 1.1 (%s -> %s); Spell Focus 5 %% = the Page Burst hit x 1.05 (%s -> %s)" % (o0, o1, k0, k1))

    # --- R13d. the kunai (Assassin Blink path + Long Reach)
    LP.HAND.put(cu, "Weapon_Kunai_Copper")

    def kreset13(stam=10.0, mana=200.0):
        kreset(stam, mana)
        KU.STRIKE.clear()
        KU.DUSED.clear()
        KU.DCD.clear()
        ATR.CACHE.clear()
        AT.GRID = Grid(world_fn())

    def kfar13():
        kreset13()
        bo_, spo_, _f = kthrow(KP["Copper"])
        comp(bo_, TCc.getComponentType()).getPosition().set(40.0, 65.6, 0.5)
        KU.tickPlayer(rc, tst, tbuf)
        for j_ in list(TWd.JOBS):
            j_.run()
        TWd.JOBS.clear()
        tpo_ = comp(rc, TPc.getComponentType())
        return None if tpo_ is None else round(float(tpo_.getPosition().x()), 2)
    tree()
    far0 = kfar13()
    tree(Assassin_T3=3, Assassin_PC1=6)
    far1 = kfar13()
    check(far0 is not None and far1 is not None and 20.0 <= far0 <= 21.5 and abs(far1 - far0 - 9.0) < 0.6,
          "R13d (Long Reach 3 + Long Throw 6): a teleport kunai that flies on lands you where it left your range - 20 blocks without, 29 with "
          "(%s -> %s)" % (far0, far1))
    tree(Assassin_PC4=10)
    kreset13()
    n_st = mob(9361, 12.0, 64.0, 0.5, (0.6, 1.8, 0.6))
    NEARL[:] = [n_st]
    bs4, sp4, _f = kthrow(KP["Copper"])
    cost4 = (sv(mc, STAM), sv(mc, MANA))
    tpl4, _n = kland(bs4, sp4, (10.5, 64.0, 0.5))
    reset_buf()
    KU.tickPlayer(rc, tst, tbuf)
    ev4 = events()
    check(cost4 == (5.0, 196.7) and tpl4 is not None and [(e_[0], e_[1]) for e_ in ev4] == [(9361, 7.0)] and KU.STRIKE.isEmpty(),
          "R13d (Blink Strike): the teleport costs 10 %% more (Mana 3 -> 3.3; Stamina 6.6 capped at 5); on the next tick after you arrive the "
          "nearest enemy within 3 blocks takes one Copper kunai hit (7): %s %s %s" % (cost4, tpl4, ev4))
    NEARL[:] = []
    tree(Assassin_PC3=3)
    kreset13()
    KU.LASTPORT.put(cu, Lng(nowms() - 1000))
    bd1, _s, _f = kthrow(KP["Copper"])
    dcd1 = KU.DCD.get(cu)
    dbl1 = (KU.STATES.get(cu) is not None, sv(mc, STAM), sv(mc, MANA), dcd1 is not None and 8800 <= int(dcd1) - nowms() <= 9100)
    bd2, _s, _f = kthrow(KP["Copper"])
    dbl2 = (KU.FLY.containsKey(bd2), "cooldown" in str(KU.LAST_WHY))
    tree()
    kreset13()
    KU.LASTPORT.put(cu, Lng(nowms() - 1000))
    bd3, _s, _f = kthrow(KP["Copper"])
    dbl3 = KU.FLY.containsKey(bd3)
    check(dbl1 == (True, 7.5, 200.0, True) and dbl2 == (True, True) and dbl3,
          "R13d (Double Step): 1 s after a teleport a second teleport throw ignores the 6 s cooldown and costs half the Stamina (5 -> 2.5) and no "
          "Mana; then the next one waits 6 + 3 s (a normal throw); without the node it is a normal throw: %s %s %s" % (dbl1, dbl2, dbl3))
    # fix 2: a profile switch drops the Double Step state - the other profile does not inherit the 6 + 3 s wait
    tree(Assassin_PC3=3)
    kreset13()
    KU.DGEN.clear()
    ATR.EPOCH.clear()
    ATR.GEN.clear()
    br.put(ek13, Lng(7))
    KU.LASTPORT.put(cu, Lng(nowms() - 1000))
    bp1, _s, _f = kthrow(KP["Copper"])
    pA = (KU.DCD.get(cu) is not None, KU.DGEN.get(cu) is not None and int(KU.DGEN.get(cu)) == 0)
    KU.LASTPORT.put(cu, Lng(nowms() - 7000))
    KU.STATES.clear()
    KU.LAST_WHY = ""
    bp2, _s, _f = kthrow(KP["Copper"])
    pB = ("cooldown" in str(KU.LAST_WHY), KU.STATES.get(cu) is not None)
    kreset13()
    KU.DGEN.clear()
    KU.LASTPORT.put(cu, Lng(nowms() - 1000))
    bp3, _s, _f = kthrow(KP["Copper"])
    br.put(ek13, Lng(8))
    KU.LASTPORT.put(cu, Lng(nowms() - 7000))
    KU.STATES.clear()
    KU.LAST_WHY = ""
    bp4, _s, _f = kthrow(KP["Copper"])
    pC = (KU.STATES.get(cu) is not None, KU.DCD.get(cu) is None, KU.DGEN.get(cu) is None)
    br.remove(ek13)
    ATR.EPOCH.clear()
    ATR.GEN.clear()
    KU.DGEN.clear()
    check(pA == (True, True) and pB == (True, False) and pC == (True, True, True),
          "R13d FIX (Double Step + profile switch): the same profile still waits 6 + 3 s after the free throw; after a new profile:epoch the "
          "old wait and the used port are dropped (a normal teleport throw goes): %s %s %s" % (pA, pB, pC))
    # Hard Return: the knockback x 2, the 6 s window, the vanilla Stun effect on the pushed mob
    EFXc13 = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    stun_dec = None
    if EFXc13.getAssetMap().getAsset("Stun") is None:
        os_, ws_ = dec(EFXc13, "Stun", AZ.read("Server/Entity/Effects/Status/Stun.json").decode("utf-8-sig"))
        stun_dec = ws_
        keep13 = HashMap(pbu)
        pbu.clear()
        if os_ is not None:
            load(EFXc13, [os_], "Hytale:Hytale")
        pbu.putAll(keep13)
    stun_loaded = EFXc13.getAssetMap().getAsset("Stun") is not None
    nret = [9370]

    def ret13():
        kreset13()
        bq_, spq_, _f = kthrow(KP["Copper"])
        kland(bq_, spq_, (10.5, 64.0, 0.5))
        rt_ = KU.RET.get(cu)
        win_ = None if rt_ is None else int(round((float(rt_[3]) - nowms()) / 1000.0))
        put(rc, TPc.getComponentType(), None)
        put(rc, TCc.getComponentType(), TCc(V3(10.8, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        nret[0] += 2
        nk_ = mob(nret[0], 1.5, 64.0, 0.5, (0.6, 1.8, 0.6))
        put(nk_, ECCc.getComponentType(), ECCc())
        NEARL[:] = [nk_, rc]
        reset_buf()
        om_, opm_ = launched(KRM["Copper"], nret[0] + 1, 10.8, 65.5, 0.5)
        AT.added(om_, opm_, int(ADf.pidCode(KRM["Copper"])), tst, tbuf)
        for j_ in list(TWd.JOBS):
            j_.run()
        TWd.JOBS.clear()
        kn_ = KU.KNOCK.get(cu)
        put(rc, TCc.getComponentType(), TCc(V3(0.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
        s0_ = int(ATR.STUNS)
        KU.tickPlayer(rc, tst, tbuf)
        kk_ = last_instr(nk_)
        ecc_ = comp(nk_, ECCc.getComponentType())
        act_ = [] if ecc_ is None else [round(float(a_.getRemainingDuration()), 2) for a_ in ecc_.getActiveEffects().values()]
        NEARL[:] = []
        return win_, None if kn_ is None else [round(float(x_), 2) for x_ in list(kn_)], kk_[0] if kk_ else None, int(ATR.STUNS) - s0_, act_
    tree()
    rr0 = ret13()
    tree(Assassin_PC2=2)
    rr1 = ret13()
    check(stun_loaded and rr0[0] == 8 and rr0[2] == (10.0, 4.0, 0.0) and rr0[3] == 0 and rr1[0] == 6 and rr1[1] is not None and rr1[1][4] == 2.0
          and rr1[1][6] == 0.4 and rr1[2] == (20.0, 8.0, 0.0) and rr1[3] == 1 and rr1[4] == [0.4],
          "R13d (Hard Return): the return window 8 -> 6 s; the knockback ring pushes x 2 (10 -> 20 b/s outward, 4 -> 8 up) and puts the vanilla Stun "
          "effect on the pushed mob for 0.4 s; without the node: 8 s, x 1, no stun: %s | %s (Stun decode %s)" % (rr0, rr1, stun_dec))
    tree(Assassin_PC1=6)
    kreset13()
    bk13, _s, _f = kthrow(KP["Copper"])
    dk13 = DMGc(DPS(rc, bk13), DCSc.PROJECTILE, JFloat(7.0))
    TS10.handle(0, None, tst, tbuf, dk13)
    btu13, _s = bolt(1.0, 65.6, 0.5, creator=cu, model=G_BOLT)
    dg13 = DMGc(DPS(rc, btu13), DCSc.PROJECTILE, JFloat(7.0))
    TS10.handle(0, None, tst, tbuf, dg13)
    tree()
    dk13b = DMGc(DPS(rc, bk13), DCSc.PROJECTILE, JFloat(7.0))
    TS10.handle(0, None, tst, tbuf, dk13b)
    check(abs(float(dk13.getAmount()) - 6.3) < 1e-3 and float(dg13.getAmount()) == 7.0 and float(dk13b.getAmount()) == 7.0,
          "R13d (Long Throw): a kunai hit x 0.9 through ArmoryTuneSys (7 -> 6.3); the grapple bolt and a player without the node untouched: %s %s %s" % (
              float(dk13.getAmount()), float(dg13.getAmount()), float(dk13b.getAmount())))

    # --- R13e. Shadow Step: Long Reach + Blink Strike
    m_26 = ss_mob(9381, 26.5, 64.0, 0.5, PI_ / 2.0)          # 26 blocks ahead (the 24-block range misses it)
    tree()
    ss_reset(near=[m_26, rc])
    sa_ = ss_run()
    tree(Assassin_T3=3)
    ss_reset(near=[m_26, rc])
    sb_ = ss_run()
    ss_reset(near=[])
    sc_ = ss_run()
    check(sa_ is not None and sa_[0] == 18.5 and sb_ is not None and sb_[0] == 28.0 and sc_ is not None and sc_[0] == 20.5,
          "R13e (Long Reach): a mob 26 blocks ahead - without the node a straight 18-block step, with it you appear behind the mob (x 28); the "
          "no-target step 18 -> 20: %s %s %s" % (sa_, sb_, sc_))
    tree(Assassin_PC4=10)
    m_8 = ss_mob(9382, 8.5, 64.0, 0.5, PI_ / 2.0)
    ss_reset(near=[m_8, rc])
    sd_ = ss_run()
    stam_ = sv(mc, STAM)
    strk_ = KU.STRIKE.get(cu)
    reset_buf()
    put(rc, TCc.getComponentType(), TCc(V3(10.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    KU.tickPlayer(rc, tst, tbuf)
    ev5 = events()
    check(sd_ is not None and sd_[0] == 10.0 and stam_ == 5.6 and strk_ is not None and [(e_[0], e_[1]) for e_ in ev5] == [(9382, 7.0)],
          "R13e (Blink Strike after a targeted Shadow Step): the step costs 4.4 Stamina (4 x 1.1: 10 -> 5.6) and on the next tick the target takes one "
          "Copper kunai hit (7): %s %s %s" % (sd_, stam_, ev5))
    check(strk_ is not None and len(strk_) == 5 and abs(float(strk_[4]) - time.time() * 1000.0) < 60000.0,
          "R13e FIX: a Blink Strike entry carries its time: %s" % (list(strk_) if strk_ is not None else None,))
    ss_reset(near=[m_8, rc])
    KU.STRIKE.put(cu, JArray(JDouble)([10.0, 64.0, 0.5, 7.0, time.time() * 1000.0 - 5000.0]))
    reset_buf()
    put(rc, TCc.getComponentType(), TCc(V3(10.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    KU.tickPlayer(rc, tst, tbuf)
    ev6 = events()
    check(ev6 == [] and KU.STRIKE.get(cu) is None and "too old" in str(ATR.LAST_WHY),
          "R13e FIX (stale Blink Strike): an entry 5 s old (a disconnect before the tick) is dropped, no hit: %s %s" % (ev6, ATR.LAST_WHY))
    NEARL[:] = []
    SH.LAST.clear()
    SH.ARMED.clear()

    # --- R13f. Hard Knuckles (Stun.fist) on REAL Damage objects + ArmoryTuneSys
    ST13 = JClass(PKG + "Stun")
    fids_ = [str(x_) for x_ in ST13.FIST_IDS]
    fj_ = [float(x_) for x_ in ST13.FIST_JAB]
    fp_ = [float(x_) for x_ in ST13.FIST_POW]
    ST13.HAND = HashMap()

    def fist13(item, amount, src=None):
        ST13.HAND.put(cu, item)
        d_ = DMGc(src if src is not None else DENTc(rc), 0, JFloat(amount))
        ST13.fist(tbuf, d_)
        return round(float(d_.getAmount()), 4)
    gi_ = fids_.index("Weapon_Fist_Gauntlets_Iron")
    wi_ = fids_.index("Weapon_Fist_Wraps_Linen")
    tree(Monk_PB1=20)
    fk = [fist13(fids_[gi_], fj_[gi_]), fist13(fids_[gi_], fp_[gi_]), fist13(fids_[wi_], fj_[wi_]), fist13(fids_[wi_], fp_[wi_]),
          fist13("Weapon_Sword_Iron", 10.0), fist13(fids_[gi_], fp_[gi_], src=DPS(rc, REFc(tst, 9399)))]
    ST13.HAND.put(cu, fids_[gi_])
    dtn_ = DMGc(DENTc(rc), 0, JFloat(fp_[gi_]))
    TS10.handle(0, None, tst, tbuf, dtn_)
    tree()
    fk0 = fist13(fids_[gi_], fp_[gi_])
    ST13.HAND = None
    check(len(fids_) == 12 and fk == [round(fj_[gi_] * 0.95, 4), round(fp_[gi_] * 1.2, 4), round(fj_[wi_] * 0.95, 4), round(fp_[wi_] * 1.2, 4), 10.0, round(fp_[gi_], 4)]
          and abs(float(dtn_.getAmount()) - fp_[gi_] * 1.2) < 1e-3 and fk0 == round(fp_[gi_], 4),
          "R13f (Hard Knuckles 20 %%): the Iron gauntlets' finisher %s x 1.2, a jab %s x 0.95, the Linen wraps' power hit %s x 1.2 / jab x 0.95; a sword, "
          "a projectile and a player without the node untouched; ArmoryTuneSys runs it (the Filter group): %s %s" % (fp_[gi_], fj_[gi_], fp_[wi_], fk, float(dtn_.getAmount())))
    OLD18 = os.path.join(HERE, "SkyyArmory-0.1.8.jar")
    if not os.path.isfile(OLD18):
        print("R13f. NOTE no SkyyArmory-0.1.8.jar here - the old-vs-new file compare is skipped")
    else:
        with zipfile.ZipFile(OLD18) as oz_:
            on_ = oz_.namelist()
            new_ = sorted(set(JN) - set(on_))
            gone_ = sorted(set(on_) - set(JN))
            diff_ = [n_ for n_ in on_ if n_ in JSET and not n_.endswith(".class") and n_ != "manifest.json" and oz_.read(n_) != JZ.read(n_)]
            ccl = sorted(n_ for n_ in on_ if n_.endswith(".class") and n_ in JSET and oz_.read(n_) != JZ.read(n_))
        check(new_ == ["com/skyy/armory/ArmoryTree.class"] and not gone_ and not diff_,
              "R13f: vs SkyyArmory-0.1.8.jar - the only new file is ArmoryTree.class, none gone, every non-class file byte-identical: %s %s %s" % (new_, gone_, diff_[:3]))
        print("R13f. vs 0.1.8: + ArmoryTree.class, %d classes changed: %s" % (len(ccl), ", ".join(c_.split("/")[-1][:-6] for c_ in ccl)))
    br.remove("tree:fn:bonus")
    ATR.CACHE.clear()
    ATR.ECHO.clear()
    AT.NEAR = None
    ACfg.useDefaults()
    ACfg.TRAV_FX = False
    print("R13. 0.1.9 class tree reader: every path executed (lookups %d, stuns %d, echoes %d, doubles %d, strikes %d, fists %d, heals %d)" % (
        int(ATR.LOOKUPS), int(ATR.STUNS), int(ATR.ECHOES), int(ATR.DOUBLES), int(ATR.STRIKES), int(ATR.FISTS), int(ATR.HEALS)))
'''

# ================================================================================================ the harness: 0.1.8's checks (+ the set changes) + R13
traw = open(TSRC, encoding="utf8", newline="").read()
TNL = CR + LF if (CR + LF) in traw else LF
ts = traw.replace(CR + LF, LF)


def hrep(old, new, count=1):
    global ts
    n = ts.count(old)
    assert n == count, "harness anchor count %d (want %d): %s" % (n, count, old[:140])
    ts = ts.replace(old, new)


hrep('"""SkyyArmory 0.1.8 - test harness. GENERATED by tools/armory_0_1_8_patch.py from test_skyyarmory_0.1.7.py - edit the patch, never this file.',
     '''"""SkyyArmory 0.1.9 - test harness. GENERATED by tools/armory_0_1_9_patch.py from test_skyyarmory_0.1.8.py - edit the patch, never this file.
Every 0.1.8 check below still runs, patched only where 0.1.9 changed the set on purpose: + the ArmoryTree class in the counts; R12f's 0.1.7 ->
0.1.8 compare allows the new ArmoryTree.class (R13f compares 0.1.8 -> 0.1.9).
NEW R13 (JVM, after R12) EXECUTES every 0.1.9 path with a stand-in SkyyTrees (tree:fn:bonus answering per player + key):
  R13a the reader: ArmoryTree.b (the answer, the 1 s cache, no SkyyTrees / a bad answer = 0), tree:reads:SkyyArmory = the 11 keys at publish (fix 2: Hard Knuckles held back), a profile switch drops the player's cache + Echo + Double Step,
       removed at unpublish (another mod's value is kept);
  R13b the staff blink: Long Blink (+ ranked blocks, trail + 1 s), Spell Focus x Blink Slash on the trail, Blink Slash's + 20 % Mana (too
       little = no blink, nothing spent), Rift Echo (the second blink within 2 s free: Mana back, half Stamina; then the Amount-s cooldown; it
       passes blink.cooldown), Radiant Trail (trail x 0.75 + the heal of you and your party, never a stranger, through a direct TravHeal);
  R13c the wand heal orb x 1.1 (Gentle Hands); the spellbook Page Burst x 1.05 (Spell Focus);
  R13d the kunai: Long Reach + Long Throw range (29), Blink Strike's + 10 % cost and its hit on arrival, Double Step (no cooldown, half
       Stamina, no Mana, then cooldown + 3 s), Hard Return (knockback x 2, the 6 s window, the vanilla Stun effect 0.4 s on the pushed mob),
       Long Throw's x 0.9 kunai hit through ArmoryTuneSys (the grapple bolt untouched);
  R13e Shadow Step: Long Reach (a mob at 26 becomes a target, the no-target step 20), Blink Strike after a targeted step (the hit + 4.4 Stamina);
  R13f Hard Knuckles on REAL Damage objects (power hit x 1.2, jab x 0.95, projectiles / other weapons / no node untouched; through
       ArmoryTuneSys too); vs the 0.1.8 jar: + ArmoryTree.class, every non-class file byte-identical.

0.1.8 harness: SkyyArmory 0.1.8 - test harness. GENERATED by tools/armory_0_1_8_patch.py from test_skyyarmory_0.1.7.py - edit the patch, never this file.''')
hrep('VERSION = "0.1.8"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.8 SkyyArmory"',
     'VERSION = "0.1.9"\nMOD = "SkyyArmory"\nPKG = "com.skyy.armory."\nPACK = "Skyy:0.1.9 SkyyArmory"')
hrep('os.path.join(SCRATCH_ROOT, "armory018", "harness")', 'os.path.join(SCRATCH_ROOT, "armory019", "harness")')
hrep('raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.8.py', 'raise SystemExit("build first: python SkyyArmory/build_skyyarmory_0.1.9.py')
hrep('Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.8"))', 'Paths.get(os.path.join(troot, "Skyy_SkyyArmory-0.1.9"))')
hrep('"[SkyyArmory] 0.1.8 ready" in m_', '"[SkyyArmory] 0.1.9 ready" in m_')
hrep('"0.1.8 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_', '"0.1.9 magic traversals: traversals on (Stamina 50% of the Mana, cap " in m_')
hrep('"0.1.8 crossbow grapple: grapple on" in m_', '"0.1.9 crossbow grapple: grapple on" in m_')
hrep('come from Skyy:0.1.8 SkyyArmory" in str(r[1])', 'come from Skyy:0.1.9 SkyyArmory" in str(r[1])')
hrep('''    check(len(names) == 46, "A: 46 classes (39 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 7 kit)")''',
     '''    check(len(names) == 47, "A: 47 classes (40 SkyyArmory incl. 0.1.1's 12 traversal + 0.1.2's 6 grapple + 0.1.3's 2 leap + 0.1.6's 6 book / kunai + 0.1.7's 2 stunlock + 0.1.8's Shadow + 0.1.9's ArmoryTree + 7 kit)")''')
hrep('''        check(sorted(n_ for n_ in new_ if not n_.endswith(".class")) == sorted(_l18p) and [n_ for n_ in new_ if n_.endswith(".class")] == ["com/skyy/armory/Shadow.class"]''',
     '''        check(sorted(n_ for n_ in new_ if not n_.endswith(".class")) == sorted(_l18p) and [n_ for n_ in new_ if n_.endswith(".class")] == ["com/skyy/armory/ArmoryTree.class", "com/skyy/armory/Shadow.class"]   # 0.1.9: + ArmoryTree''')

R13 = R13_TEXT
hrep('''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''',
     R13 + '''    # ---------------- L2. (last: it changes the store) another pack wins one interaction with a wrong number -> ONE WARN naming both''')

out_t = ts.replace(LF, TNL)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(out_t)
print("wrote %s (%d lines)" % (os.path.relpath(TDST, ROOT), out_t.count(TNL) + 1))
