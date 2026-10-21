"""SkyyClasses 0.1.43 - THE CLASS-TREE EFFECTS ENGINE (UpFx) as Java source for tools/classes_0_1_43_patch.py (imported by the patch; the
generated build script carries the text). Skill Trees 3 round R3a (research/Skill-Trees-3-Spec.md section 3; tools/trees_v3_data.py
CLASS_FX = the codes + numbers). SkyyTrees 0.4.1 sends "f.<code>=<rank x per rank summed>" in tree:fn:abil; UpFx reads it (cached per
list text) and applies every SkyyClasses code at the hooks below. Java for javassist: no generics / lambdas / autoboxing / enhanced for /
inner classes; methods before callers. @C_<code>@ = the code's index in CODES (UPFX_CODES), replaced at build time.

THE FIRST-PASS CONSTANTS (no number in the spec; the four power sources rule: a tree is one source of four, so small; listed in the report):
  DR_CAP 50 % (all tree damage cuts together), DMG_CAP +80 % (all tree damage bonuses on one hit), slows 3 s on ability hits / 2 s on
  weapon hits, standing still = 1 s without moving 0.3 block, the lethal hit x1.5, Focus Fire 5 stacks within 3 s, debuffs counted 3 at
  most, every-5th melee hit (Echo), the chain / bounce budget per ability per 0.5 s, the heal budget 5 hits per cast window (2 s), the
  Shadow Clone 3 s + 1 s a rank, then it strikes the ONE nearest enemy within 3 blocks for 60 % of a hit (40 % per extra clone; fix round:
  single target - the Assassin has no AoE), distract radius 6, Last Ward 60 s, Ghost Protocol 8 s, No
  Mind 6 s, Rumble 5 s, Untouchable 1 s / 2.5 blocks / 30 %, Thousand Palms 3 blocks / 40 %, Aegis 6 blocks / 10 % / 30 s / blocks slow 40 %,
  Warden's Grip 8 blocks / root 2 s / 10 % ward, Domain 60 % and kills +2 s, Endless Fury 2 Stamina a pulse, Cataclysm 3 stars, Prism 4 %
  Mana/s + 2 %/s (max 40 %), Glacial 10 s + frozen +20 %, Miracle below 20 % / 8 s per ally, Vigil -30 % wait, Holy Land +50 % / +50 %.
FIX ROUND (PROJECT-RULES 4, everything a server owner might change is editable in game): Server Setup -> Classes -> Abilities "Class tree
effects" (abil.treeFx, AbilCfg.TREE_FX; off = no class-tree effect in SkyyClasses) and Ability numbers "Class tree numbers"
(ab.ClassTree.numbers -> AbilNum.UX_*): drCap, dmgCap, slowAbility, slowWeapon, cloneTime, cloneHit, cloneExtra, cloneLure, lastWard,
ghost, noMind, rumble, aegisHold, aegisRadius, gripRadius, glacial, miracle (times in seconds). DR_CAP / DMG_CAP stay as the defaults' record.
FIX ROUND 2: + lethal, focusStacks, chainGap in "Class tree numbers"; a second row "Capstone numbers" (ab.Capstones.numbers -> AbilNum.CP_*):
rumbleStun, aegisCut, aegisSlow, gripRoot, gripWard, domain, domainKill, furyMax, furyMana, furyStamina, furyBack, furySlow, imageHit,
palmsHit, lotus, deadEye, spiderStun, cataStars, prismDrain, prismRamp, prismMax, glacialHit, miracleBelow, vigil, holyOverlap.
Three capstones get their spec mechanic back (they had become stat tweaks): ENDLESS FURY = a Whirlwind toggle (cast again to stop, furyMax s
at most, 70 % move speed, furyMana + furyStamina a second, furyBack Stamina per full spin that hit; the cooldown starts when it ends);
SPIDER'S DEN + HOLY LAND = a spare charge (a cast on cooldown spends it, the main cooldown keeps running); Holy Land's overlap heals 150 %
(the younger Sanctuary heals holyOverlap - 100 % there). RUMB is a ThreadLocal (worlds tick on their own threads); quit drops NOVA.
"""

UPFX_STATE = [
    # per player
    "MANAF", "STILL", "ROLL", "TRAPS", "LATER", "MOVEB", "MREGB", "DRB", "FOCUS", "HITS", "BUDG", "FSHIT", "GKHIT", "BUFF", "VANT",
    "CLOAKEND", "LASTW", "GHOST", "NOMIND", "RUMBLE", "UNTOUCH", "CLONES", "CASC", "TICKAT", "POSTED", "MREGP", "BLOCKT", "IMBT", "BOWT",
    "MIRACLE", "GLACIAL", "PRISM",
    "FURYZ", "FURYN", "CHG",   # fix 2: Endless Fury's toggled spin + its full-spin clock; the spare charge (Spider's Den, Holy Land)
    # per mob (Ref keys)
    "VULN", "WEAK", "KMARK", "NETTED", "LOTUS", "SPELLS", "RT", "SLOWED", "FIRED",
]

UPFX_JAVA = r'''
# ================= 0.1.43 UpFx: THE CLASS-TREE EFFECTS (Skill Trees 3 round R3a; tools/classes_0_1_43_upfx.py has the notes) =================
upfx = pool.makeClass(PKG + ".UpFx")
F(upfx, "public static volatile boolean ON = false;")          # a player with fx codes was seen since the start (every hook's fast exit)
F(upfx, "public static final String[] CODES = %s;" % jarr(UPFX_CODES))
F(upfx, "public static final double[] PER = new double[] { %s };" % ", ".join(repr(float(UPFX_PER[_c])) for _c in UPFX_CODES))
F(upfx, "public static final int NP = %d;" % len(V3D.FX_AP))
F(upfx, "public static final int[] AP = new int[] { %s };" % ", ".join(str(_x) for _x in UPFX_AP))
for _f in UPFX_STATE + ["VC"]:
    F(upfx, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
for _f in ("public static volatile long PROCS = 0L;", "public static volatile long CUTS = 0L;", "public static volatile long BOOSTS = 0L;",
           "public static volatile long KILLS = 0L;", "public static volatile long CASTS = 0L;", "public static volatile long TICKS = 0L;",
           "public static volatile long CLONEBURSTS = 0L;", "public static volatile long CAPS = 0L;", "public static volatile String LAST = \"\";",
           "public static volatile boolean FAILED_ONCE = false;", "public static final java.lang.ThreadLocal RUMB = new java.lang.ThreadLocal();",   # fix 2: per world thread
           "public static final double DR_CAP = 50.0;", "public static final double DMG_CAP = 80.0;",
           "public static final String MOVE_SRC = \"classes.tree\";", "public static final String MREG_SRC = \"classes\";"):
    F(upfx, _f)
M(upfx, r"""
public static void warn(String what, Throwable t) {
  if (FAILED_ONCE) return;
  FAILED_ONCE = true;
  @PKG@.ClassCfg.warn("class tree effects: " + what + " failed (logged once; that effect was skipped): " + t);
}""")
M(upfx, r"""
public static void addLater(java.util.ArrayList l, int kind, long at) {
  if (l.size() < 16) l.add(new long[] { (long) kind, at });
}""")
M(upfx, r"""
public static void dueOf(java.util.ArrayList l, java.util.ArrayList due, long now) {
  for (int i = l.size() - 1; i >= 0; i--) {
    long[] a = (long[]) l.get(i);
    if (now >= a[1]) { due.add(a); l.remove(i); }
  }
}""")
M(upfx, r"""
public static java.util.ArrayList takeDue(java.util.ArrayList l, long now) {
  java.util.ArrayList due = new java.util.ArrayList();
  synchronized (l) { dueOf(l, due, now); }
  return due;
}""")
M(upfx, r"""
public static int idx(String code) {
  if (code == null) return -1;
  for (int i = 0; i < CODES.length; i++) if (CODES[i].equals(code)) return i;
  return -1;
}""")
# the codes of one tree list ("v3,...,f.<code>=<n>"): null = none; cached per list text (SkyyTrees answers the same text until a rank changes)
M(upfx, r"""
public static double[] vec(String csv) {
  if (!@PKG@.AbilCfg.TREE_FX || csv == null || csv.indexOf(",f.") < 0) return null;   // fix round: Server Setup "Class tree effects" off = no codes
  Object o = VC.get(csv);
  if (o instanceof double[]) return (double[]) o;
  double[] v = new double[CODES.length];
  boolean any = false;
  String[] ps = csv.split(",");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    if (!p.startsWith("f.")) continue;
    int e = p.indexOf('=');
    if (e < 3) continue;
    int ix = idx(p.substring(2, e));
    if (ix < 0) continue;
    try {
      double x = Double.parseDouble(p.substring(e + 1).trim());
      if (x != x || Double.isInfinite(x)) continue;
      if (x > 100000.0) x = 100000.0;
      if (x < 0.0) x = 0.0;
      v[ix] = v[ix] + x;
      any = true;
    } catch (Throwable t) { }
  }
  if (VC.size() > 512) VC.clear();
  VC.put(csv, v);
  if (any) ON = true;
  return v;
}""")
M(upfx, r"""
public static double[] of(java.util.UUID u) {
  if (u == null) return null;
  try { return vec(@PKG@.Abil.treeCsv(u)); } catch (Throwable t) { return null; }
}""")
M(upfx, "public static double g(double[] v, int i) { return v == null || i < 0 || i >= v.length ? 0.0 : v[i]; }")
M(upfx, r"""
public static double ap(double[] v, int ai, int p) {
  if (v == null || ai < 0 || p < 0 || p >= NP || ai * NP + p >= AP.length) return 0.0;
  return g(v, AP[ai * NP + p]);
}""")
# how many ranks a code's total stands for (FX_RANKED codes: one per-rank value)
M(upfx, r"""
public static int ranks(double[] v, int i) {
  double t = g(v, i);
  if (!(t > 0.0) || i < 0 || i >= PER.length || !(PER[i] > 0.0)) return 0;
  return (int) Math.round(t / PER[i]);
}""")
M(upfx, r"""
public static int rk(double[] v, int ai, int p) {
  if (v == null || ai < 0 || p < 0 || p >= NP) return 0;
  return ranks(v, AP[ai * NP + p]);
}""")
M(upfx, "public static boolean has(double[] v, int i) { return g(v, i) > 0.0; }")
M(upfx, r"""
public static double[] copy(double[] a) {
  double[] b = new double[a.length];
  for (int i = 0; i < a.length; i++) b[i] = a[i];
  return b;
}""")
M(upfx, "public static String uk(java.util.UUID u, String what) { return String.valueOf(u) + \"|\" + what; }")
# a timed value: { until, value } (0 once past)
M(upfx, r"""
public static double timed(java.util.concurrent.ConcurrentHashMap m, Object k, long now) {
  if (k == null) return 0.0;
  Object o = m.get(k);
  if (!(o instanceof double[])) return 0.0;
  double[] a = (double[]) o;
  if ((double) now >= a[0]) { m.remove(k); return 0.0; }
  return a[1];
}""")
M(upfx, r"""
public static void prune(java.util.concurrent.ConcurrentHashMap m, long now) {
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object o = m.get(k);
    boolean dead = false;
    try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
    if (dead || (o instanceof double[] && ((double[]) o).length > 0 && ((double[]) o)[0] <= (double) now)) it.remove();
  }
}""")
M(upfx, r"""
public static void timedPut(java.util.concurrent.ConcurrentHashMap m, Object k, long until, double val) {
  if (k == null || !(val > 0.0)) return;
  Object o = m.get(k);
  if (o instanceof double[]) {
    double[] a = (double[]) o;
    if (a[0] > (double) System.currentTimeMillis() && a[1] > val) return;   // a stronger one runs: kept
    if (a[0] >= (double) until && a[1] >= val) return;                       // as strong and longer: kept
  }
  if (m.size() > 2048) prune(m, System.currentTimeMillis());
  m.put(k, new double[] { (double) until, val });
}""")
# FIX ROUND (critic: KMARK / NETTED had no cap): the mob-keyed marks keep at most 2048 entries - past that, gone mobs, expired kunai marks
# (long[] {until, ..}) and net times older than 6 s (Long) are dropped first (the same 2048 rule as timedPut)
M(upfx, r"""
public static void capMob(java.util.concurrent.ConcurrentHashMap m, long now) {
  if (m.size() <= 2048) return;
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object o = m.get(k);
    boolean dead = false;
    try { dead = (k instanceof @REF@) && !((@REF@) k).isValid(); } catch (Throwable t) { dead = false; }
    if (dead || (o instanceof long[] && ((long[]) o).length > 0 && ((long[]) o)[0] <= now) || (o instanceof Long && now - ((Long) o).longValue() >= 6000L)) it.remove();
  }
  if (m.size() > 2048) m.clear();
}""")
# a budget: at most n uses per window ms per key (chains, bounces, heals per cast)
M(upfx, r"""
public static boolean take(String key, int n, long win, long now) {
  if (n <= 0) return false;
  Object o = BUDG.get(key);
  long[] b = null;
  if (o instanceof long[]) b = (long[]) o;
  if (b == null || now - b[0] >= win || now < b[0]) { b = new long[] { now, 0L }; BUDG.put(key, b); if (BUDG.size() > 4096) BUDG.clear(); }
  if (b[1] >= (long) n) return false;
  b[1] = b[1] + 1L;
  return true;
}""")
M(upfx, r"""
public static boolean gap(java.util.concurrent.ConcurrentHashMap m, Object k, long ms, long now) {
  if (k == null) return false;
  Object o = m.get(k);
  if (o instanceof Long && now - ((Long) o).longValue() < ms && now >= ((Long) o).longValue()) return false;
  m.put(k, Long.valueOf(now));
  return true;
}""")
M(upfx, r"""
public static double frac(@CAC@ acc, @REF@ r, int idx) {
  @ESM@ m = @PKG@.Abil.map(acc, r);
  double c = @PKG@.Abil.cur(m, idx);
  double x = @PKG@.Abil.max(m, idx);
  if (!(x > 0.0) || c < 0.0) return -1.0;
  return c / x;
}""")
M(upfx, r"""
public static double heal(@CAC@ acc, @REF@ r, double pctMax) {
  if (r == null || !(pctMax > 0.0)) return 0.0;
  double mx = @PKG@.Abil.max(@PKG@.Abil.map(acc, r), @DST@.getHealth());
  if (!(mx > 0.0)) return 0.0;
  return @PKG@.Abil.apply(acc, r, mx * pctMax / 100.0, mx * pctMax / 100.0);
}""")
M(upfx, r"""
public static void stat(@CAC@ acc, @REF@ r, int idx, double amt) {
  if (r == null || !(amt > 0.0) || idx < 0) return;
  @ESM@ m = @PKG@.Abil.map(acc, r);
  if (m == null) return;
  double c = @PKG@.Abil.cur(m, idx);
  double x = @PKG@.Abil.max(m, idx);
  if (c < 0.0 || !(x > 0.0)) return;
  double a = c + amt > x ? x - c : amt;
  if (a > 0.0) m.addStatValue(idx, (float) a);
}""")
M(upfx, r"""
public static void slow(@CAC@ acc, @REF@ t, double pct, double secs) {
  if (t == null || !(pct > 0.0) || !(secs > 0.0)) return;
  int p = (int) Math.round(pct > 30.0 ? 30.0 : pct);
  @PKG@.Abil.effect(acc, t, pct >= 40.0 ? @PKG@.Abil.EF_SLOW : @PKG@.Abil.spdId(-p), secs);
  timedPut(SLOWED, t, System.currentTimeMillis() + Math.round(secs * 1000.0), 1.0);
}""")
M(upfx, r"""
public static boolean pushFrom(@CAC@ acc, @REF@ t, double x, double z, double blocks) {
  if (t == null || !(blocks > 0.0)) return false;
  @VEC@ q = @PKG@.Abil.pos(acc, t);
  if (q == null) return false;
  double dx = q.x - x;
  double dz = q.z - z;
  double d = Math.sqrt(dx * dx + dz * dz);
  if (d < 0.05) { dx = 1.0; dz = 0.0; d = 1.0; }
  double f = blocks * @PKG@.AbilCfg.PUSH_PER_BLOCK;
  return @PKG@.Abil.push(acc, t, dx / d * f, f * 0.25, dz / d * f);
}""")
M(upfx, r"""
public static int debuffs(@REF@ t, long now) {
  if (t == null) return 0;
  int n = 0;
  if (@PKG@.AbilStore.POISONED.get(t) instanceof long[] && ((long[]) @PKG@.AbilStore.POISONED.get(t))[0] > now) n++;
  if (@PKG@.Abil.breachPct(t, now) > 0.0) n++;
  if (@PKG@.AbilStore.SUNDER.get(t) instanceof double[] && ((double[]) @PKG@.AbilStore.SUNDER.get(t))[0] > (double) now) n++;
  if (@PKG@.AbilStore.MARKD.get(t) instanceof double[] && ((double[]) @PKG@.AbilStore.MARKD.get(t))[0] > (double) now) n++;
  if (timed(RT, t, now) > 0.0) n++;
  if (timed(SLOWED, t, now) > 0.0) n++;
  if (timed(WEAK, t, now) > 0.0) n++;
  if (@PKG@.AbilStore.FROZEN.get(t) instanceof long[]) n++;
  return n;
}""")
# a zone of player u of one kind in this world (null = none / ended)
M(upfx, r"""
public static @PKG@.AbilZone zoneOf(@ST@ st, java.util.UUID u, int kind) {
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null || aw.nz == 0 || u == null) return null;
  @PKG@.AbilZone[] zs = aw.zoneArr();
  for (int i = 0; i < zs.length; i++) {
    @PKG@.AbilZone z = zs[i];
    if (z != null && !z.ended && z.kind == kind && u.equals(z.caster)) return z;
  }
  return null;
}""")
M(upfx, r"""
public static boolean inZone(@PKG@.AbilZone z, double x, double y, double z0) {
  return z != null && !z.ended && @PKG@.AbilMath.inRange(x - z.x, y - z.y, z0 - z.z, z.r);
}""")
# the strongest zone effect of ANY caster's zones of one kind at a spot: the caster's code value (Sanctuary / bubble / banner effects)
M(upfx, r"""
public static double zoneCode(@ST@ st, int kind, int code, double x, double y, double z0) {
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null || aw.nz == 0) return 0.0;
  @PKG@.AbilZone[] zs = aw.zoneArr();
  double best = 0.0;
  for (int i = 0; i < zs.length; i++) {
    @PKG@.AbilZone z = zs[i];
    if (z == null || z.ended || z.kind != kind || !inZone(z, x, y, z0)) continue;
    double v = g(of(z.caster), code);
    if (v > best) best = v;
  }
  return best;
}""")
M(upfx, r"""
public static boolean ranged(@CAC@ acc, @DMG@ d) {
  try { return d.getSource() instanceof @DPRJ@; } catch (Throwable t) { return false; }
}""")
M(upfx, r"""
public static String shotItem(@CB@ buf, @DMG@ d) {
  try {
    @DSRC@ s = d.getSource();
    if (!(s instanceof @DPRJ@)) return null;
    @PKG@.ShotRec rec = @PKG@.ShotTrack.find(buf, ((@DPRJ@) s).getProjectile());
    return rec == null ? null : rec.item;
  } catch (Throwable t) { return null; }
}""")
M(upfx, r"""
public static boolean bow(String item) {
  return item != null && (item.startsWith("Weapon_Shortbow_") || item.startsWith("Weapon_Crossbow_") || item.startsWith("Weapon_Longbow_") || item.startsWith("Weapon_Bow_"));
}""")
M(upfx, "public static boolean kunai(String item) { return item != null && item.startsWith(\"Weapon_Kunai_\"); }")
M(upfx, r"""
public static int flowStacks(java.util.UUID u, long now) {
  Object o = @PKG@.AbilStore.FLOWS.get(u);
  if (!(o instanceof @PKG@.AbilZone)) return 0;
  @PKG@.AbilZone z = (@PKG@.AbilZone) o;
  if (z.ended || now >= z.until) return 0;
  return @PKG@.Abil.stacks(z, now);
}""")
M(upfx, r"""
public static boolean manaFull(java.util.UUID u) {
  Object o = MANAF.get(u);
  return o instanceof Double && ((Double) o).doubleValue() >= 0.99;
}""")
M(upfx, r"""
public static void cdCut(String k, String id, long ms, long now) {
  if (k == null || id == null || ms <= 0L) return;
  String key = k + "|" + id;
  Object o = @PKG@.AbilStore.CD.get(key);
  if (!(o instanceof Long)) return;
  long v = ((Long) o).longValue() - ms;
  if (v <= now) { @PKG@.AbilStore.CD.remove(key); @PKG@.AbilStore.CDLEN.remove(key); }
  else @PKG@.AbilStore.CD.put(key, Long.valueOf(v));
}""")
# the move source of the movement protocol (SkyySkills / SkyyAccessories apply every source; tools/skyymove.py): flat layer, speed = frac
M(upfx, r"""
public static void movePost(java.util.UUID u, double frac) {
  if (u == null) return;
  try {
    double f = Math.round(frac * 10000.0) / 10000.0;
    Object last = POSTED.get(u);
    if (last instanceof Double && ((Double) last).doubleValue() == f) return;
    java.util.Map b = @PKG@.ClassCfg.bridge();
    String k = "move:" + u.toString();
    Object o = b.get(k);
    if (f == 0.0) { if (o instanceof java.util.Map) ((java.util.Map) o).remove(MOVE_SRC); POSTED.put(u, Double.valueOf(0.0)); return; }
    java.util.Map m = null;
    if (o instanceof java.util.Map) m = (java.util.Map) o;
    else {
      java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
      Object prev = b.putIfAbsent(k, n);
      if (prev instanceof java.util.Map) m = (java.util.Map) prev; else m = n;
    }
    java.util.HashMap e = new java.util.HashMap();
    e.put("layer", "flat");
    e.put("speed", Float.valueOf((float) f));
    e.put("jump", Float.valueOf(0.0f));
    e.put("fallDamage", Float.valueOf(0.0f));
    m.put(MOVE_SRC, e);
    POSTED.put(u, Double.valueOf(f));
  } catch (Throwable t) { warn("the move source", t); }
}""")
# the Mana regen registry of SkyySkills (skill:fn:manaregen {"add", uuid, source, percent}; 0 removes)
M(upfx, r"""
public static void mregPost(java.util.UUID u, double pct) {
  if (u == null) return;
  try {
    double p = Math.round(pct * 100.0) / 100.0;
    Object last = MREGP.get(u);
    if (last instanceof Double && ((Double) last).doubleValue() == p) return;
    Object f = @PKG@.ClassCfg.bridge().get("skill:fn:manaregen");
    if (!(f instanceof java.util.function.Function)) return;
    if (p == 0.0) ((java.util.function.Function) f).apply(new Object[] { "remove", u, MREG_SRC });
    else ((java.util.function.Function) f).apply(new Object[] { "add", u, MREG_SRC, Double.valueOf(p) });
    MREGP.put(u, Double.valueOf(p));
  } catch (Throwable t) { warn("the Mana regen source", t); }
}""")
M(upfx, r"""
public static void quit(java.util.UUID u) {
  if (u == null) return;
  try {
    movePost(u, 0.0);
    mregPost(u, 0.0);
    java.util.concurrent.ConcurrentHashMap[] ms = new java.util.concurrent.ConcurrentHashMap[] { MANAF, STILL, ROLL, TRAPS, LATER, MOVEB, MREGB, DRB, FOCUS, HITS,
      FSHIT, GKHIT, BUFF, VANT, CLOAKEND, RUMBLE, UNTOUCH, CLONES, CASC, TICKAT, BLOCKT, IMBT, BOWT, PRISM, NOVA, FURYN, CHG };   // fix 2: + NOVA, FURYN, CHG
    Object fz = FURYZ.remove(u);   // fix 2: an Endless Fury spin ends with its player (spinTick arms the cooldown)
    if (fz instanceof @PKG@.AbilZone) { ((@PKG@.AbilZone) fz).ended = true; ((@PKG@.AbilZone) fz).why = "quit"; }
    for (int i = 0; i < ms.length; i++) ms[i].remove(u);
    POSTED.remove(u);
    MREGP.remove(u);
  } catch (Throwable t) { }
}""")

# ---------------------------------------------------------------- 1. CAST TIME: the ability's numbers (Abil.ctxFor, before main)
M(upfx, r"""
public static void ctx(@PKG@.AbilCtx c) {
  if (c == null || c.ai < 0) return;
  double[] v = vec(c.tree);
  if (v == null) return;
  long now = System.currentTimeMillis();
  int ai = c.ai;
  double pw = ap(v, ai, 0);
  if ("Mage".equals(c.cls)) {
    pw = pw + g(v, @C_spellPow@);
    if (has(v, @C_overflow@) && manaFull(c.u)) pw = pw + g(v, @C_overflow@);
  }
  if (pw != 0.0) c.treeMain = c.treeMain * (1.0 + pw / 100.0);
  double rad = ap(v, ai, 1);
  if (ai == @PKG@.AbilDefs.SACRED) rad = rad + @PKG@.AbilCfg.S_RADIUS * ap(v, ai, 16) / 100.0;
  if (ai == @PKG@.AbilDefs.METEOR && has(v, @C_xCataclysm@)) rad = rad + @PKG@.AbilCfg.M_RADIUS;
  if (ai == @PKG@.AbilDefs.GUARD) c.radAdd = c.radAdd + g(v, @C_spiritReach@);
  c.radTree = c.radTree + rad;
  c.durAdd = c.durAdd + ap(v, ai, 2);
  if (ai == @PKG@.AbilDefs.BEAM && has(v, @C_xPrism@)) c.durMult = c.durMult * 2.0;   // fix 2: Endless Fury is a toggle now (furyUp), not x2
  double cost = ap(v, ai, 3);
  if (cost > 0.0) c.costMult = c.costMult * (1.0 - (cost > 90.0 ? 90.0 : cost) / 100.0);
  double cd = ap(v, ai, 4) + g(v, @C_cdAll@);
  if (cd > 0.0) c.cdMult = c.cdMult * (1.0 - (cd > 90.0 ? 90.0 : cd) / 100.0);
  if (ai == @PKG@.AbilDefs.SUNDER && has(v, @C_xFracture@)) c.cdMult = c.cdMult * 0.5;
  if (ai == @PKG@.AbilDefs.PALM && has(v, @C_xPalms@) && flowStacks(c.u, now) >= 10) c.cdMult = c.cdMult * 0.1;
  c.hotAdd = c.hotAdd + ap(v, ai, 15);
  if (ai == @PKG@.AbilDefs.RIFT && has(v, @C_xRiftmaw@) && !c.echo && c.echoPct < 0.6) c.echoPct = 0.6;
  if (has(v, @C_xCascade@) && "Spellblade".equals(c.cls) && !c.echo && c.u != null) {
    long[] x = @PKG@.Abil.momX(c.u);
    int mx = x == null ? 20 : @PKG@.Abil.momMax(x[6]);
    if (@PKG@.Abil.momN(c.u, now) >= mx) { c.radTree = c.radTree + 2.0; CASC.put(c.u, Long.valueOf(now)); }
  }
}""")
# the extra stun seconds of an ability's hits (Shockwave, Iron Chain, Palm Strike: their own code paths add it)
M(upfx, r"""
public static double stunAdd(@PKG@.AbilCtx c, int ai) {
  if (c == null || c.echo) return 0.0;
  double[] v = vec(c.tree);
  return ap(v, ai, 5);
}""")
M(upfx, r"""
public static double shockStun(@PKG@.AbilCtx c, double stun) {
  if (c == null) return stun;
  double s = stun + stunAdd(c, @PKG@.AbilDefs.SHOCK);
  if (Boolean.TRUE.equals(RUMB.get()) && s < @PKG@.AbilNum.CP_RUMBLES) s = @PKG@.AbilNum.CP_RUMBLES;   // Rumble's free Shockwave (fix 2: a per-thread flag - worlds tick on their own threads)
  return s;
}""")
M(upfx, r"""
public static int comboCap(@PKG@.AbilCtx c) {
  if (c == null) return 0;
  return (int) Math.round(g(vec(c.tree), @C_comboCap@));
}""")
M(upfx, r"""
public static int flowMove(@PKG@.AbilZone z) {
  if (z == null || z.cx == null || z.ai != @PKG@.AbilDefs.FFORM) return 0;
  return (int) Math.round(g(vec(z.cx.tree), @C_flowMove@));
}""")
M(upfx, r"""
public static int stars(@PKG@.AbilCtx c) {
  if (c == null || c.echo) return 0;
  return (int) Math.round(ap(vec(c.tree), @PKG@.AbilDefs.STARF, 17));
}""")
M(upfx, r"""
public static double range() {
  @PKG@.AbilCtx c = @PKG@.AbilCtx.get();
  if (c == null || !"Mage".equals(c.cls)) return 1.0;
  double r = g(vec(c.tree), @C_rangeAll@);
  return 1.0 + r / 100.0;
}""")
# Starfall Follow: a star lands on the nearest enemy within 4 blocks of its spot
M(upfx, r"""
public static double[] starAt(@CB@ cb, @REF@ cr, @PKG@.AbilCtx c, double px, double py, double pz) {
  if (c == null || !has(vec(c.tree), @C_starFollow@)) return null;
  @REF@ t = @PKG@.Abil.nearest(cb, cr, px, py, pz, 4.0, null);
  if (t == null) return null;
  @VEC@ q = @PKG@.Abil.pos(cb, t);
  if (q == null) return null;
  return new double[] { q.x, q.z };
}""")

# ---------------------------------------------------------------- 2. AFTER A CAST (castAt0, once it went off)
M(upfx, r"""
public static double wardPct(java.util.UUID u, double pct) {
  return pct * (1.0 + g(of(u), @C_wardBoost@) / 100.0);
}""")
# LATER: a per-player delayed action (1 = Vanishing Act's echo smoke) run by the player's own tick
M(upfx, r"""
public static void later(java.util.UUID u, int kind, long at) {
  Object o = LATER.get(u);
  java.util.ArrayList l = o instanceof java.util.ArrayList ? (java.util.ArrayList) o : new java.util.ArrayList();
  synchronized (l) { addLater(l, kind, at); }
  LATER.put(u, l);
}""")
M(upfx, r"""
public static void cloneAt(java.util.UUID u, double[] v, double[] me, double h, long now) {
  int n = 1 + (int) Math.round(g(v, @C_cloneSplit@));
  double secs = @PKG@.AbilNum.UX_CLONET + g(v, @C_cloneDur@);
  Object o = CLONES.get(u);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < n && i < 4; i++) {
    double ang = (double) i * 2.0944;
    double off = i == 0 ? 0.0 : 1.5;
    l.add(new double[] { me[0] + Math.cos(ang) * off, me[1], me[2] + Math.sin(ang) * off, (double) (now + Math.round(secs * 1000.0)), h * (i == 0 ? @PKG@.AbilNum.UX_CLONEH : @PKG@.AbilNum.UX_CLONEX) / 100.0, 0.0 });
  }
  CLONES.put(u, l);
}""")
# Warden's Grip: every enemy within 8 blocks yanked to you and rooted 2 s; your party warded 10 % of max Health
M(upfx, r"""
public static void warden(@ST@ st, @REF@ ref, java.util.UUID u, long now) {
  double[] me = @PKG@.Abil.here(st, ref);
  if (me == null) return;
  java.util.List l = @PKG@.Abil.near(st, me[0], me[1], me[2], @PKG@.AbilNum.UX_GRIPR);
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@) || !@PKG@.Abil.enemy(st, (@REF@) o, ref)) continue;
    @REF@ t = (@REF@) o;
    @VEC@ q = @PKG@.Abil.pos(st, t);
    if (q == null) continue;
    double dx = me[0] - q.x;
    double dz = me[2] - q.z;
    double d = Math.sqrt(dx * dx + dz * dz);
    if (d > 1.6) @PKG@.Abil.push(st, t, dx / d * (d - 1.5) * @PKG@.AbilCfg.PUSH_PER_BLOCK, 1.0, dz / d * (d - 1.5) * @PKG@.AbilCfg.PUSH_PER_BLOCK);
    @PKG@.Abil.rootMob(st, t, u, @PKG@.AbilNum.CP_GRIPT, now, false, false);
    n++;
  }
  @PKG@.Abil.wardArea(st, u, me[0], me[1], me[2], @PKG@.AbilNum.UX_GRIPR, @PKG@.AbilNum.CP_GRIPW, now + 8000L);   // wardArea adds the ward boost
  CAPS = CAPS + 1L;
  @PR@ pr = @PKG@.Abil.prOf(u);
  if (pr != null) @PKG@.Abil.say(pr, "Warden's Grip: " + n + (n == 1 ? " enemy" : " enemies") + " yanked and rooted; your party is warded.");
}""")
# Arc Cascade: the cast's cost back, a 5-block nova of 10 % of a hit per Momentum, every Momentum spent
M(upfx, r"""
public static void cascade(@ST@ st, @REF@ ref, java.util.UUID u, double mana, double stam, double h, long now) {
  @ESM@ m = @PKG@.Abil.map(st, ref);
  if (m != null) { if (mana > 0.0) m.addStatValue(@DST@.getMana(), (float) mana); if (stam > 0.0) m.addStatValue(@DST@.getStamina(), (float) stam); }
  int n = @PKG@.Abil.momN(u, now);
  double[] me = @PKG@.Abil.here(st, ref);
  if (n > 0 && me != null && ref != null) {
    @PKG@.Abil.momSpend(u, n, 0, now);
    NOVA.put(u, new double[] { me[0], me[1], me[2], h * 0.1 * (double) n });   // the burst needs a CommandBuffer: the caster's next tick
  }
  CAPS = CAPS + 1L;
  @PR@ pr = @PKG@.Abil.prOf(u);
  if (pr != null) @PKG@.Abil.say(pr, "Arc Cascade: the cast was free; " + n + " Momentum burst out.");
}""")
M(upfx, r"""
public static void cast(@PR@ pr, @ST@ st, @REF@ ref, java.util.UUID u, String k, int ai, int sh, @PKG@.AbilCtx cx, double[] at, double mana, double stam, long now) {
  if (cx == null || u == null || ai < 0) return;
  double[] v = vec(cx.tree);
  if (v == null) return;
  CASTS = CASTS + 1L;
  double h = cx.h;
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(st.getExternalData()));
  double[] me = @PKG@.Abil.here(st, ref);
  double wr = ap(v, ai, 14);
  if (ai == @PKG@.AbilDefs.RALLY && wr > 0.0 && me != null) @PKG@.Abil.wardArea(st, u, me[0], me[1], me[2], @PKG@.AbilNum.RG_PARTY, wr, now + 8000L);   // wardArea adds the ward boost
  int mom = (int) Math.round(ap(v, ai, 13)) + (ai == @PKG@.AbilDefs.RIFT && has(v, @C_xRiftmaw@) ? 2 : 0);
  if (mom > 0) @PKG@.Abil.momAdd(u, mom, now);
  if (ai == @PKG@.AbilDefs.METEOR && has(v, @C_meteorMove@)) timedPut(MOVEB, u, now + 3000L, g(v, @C_meteorMove@));
  if (ai == @PKG@.AbilDefs.METEOR && has(v, @C_xCataclysm@) && at != null && aw != null && sh != 2) {
    @PKG@.AbilJob sj = @PKG@.Abil.starJob(u, k, at, @PKG@.AbilCfg.M_RADIUS, Math.round(@PKG@.AbilNum.CP_CATAN), 1.5, h * @PKG@.AbilCfg.T_POWER * cx.main, 0, now + Math.round(@PKG@.AbilCfg.M_DELAY * 1000.0));
    if (sj != null) { sj.at = now + Math.round(@PKG@.AbilCfg.M_DELAY * 1000.0); aw.add(sj); }
  }
  if (ai == @PKG@.AbilDefs.VANISH) {
    if (has(v, @C_vanishHit@)) VANT.put(u, Long.valueOf(now + 6000L));
    if (has(v, @C_vanishEcho@)) later(u, 1, now + 2000L);
  }
  if ((ai == @PKG@.AbilDefs.CLOAK || ai == @PKG@.AbilDefs.VANISH) && has(v, @C_ShadowClone@) && me != null) cloneAt(u, v, me, h, now);
  if (ai == @PKG@.AbilDefs.IRONC && has(v, @C_xWarden@)) warden(st, ref, u, now);
  Object cc = CASC.remove(u);
  if (cc instanceof Long && now - ((Long) cc).longValue() < 2000L && "Spellblade".equals(cx.cls)) cascade(st, ref, u, mana, stam, h, now);
  LAST = "cast " + @PKG@.AbilDefs.IDS[ai];
}""")
'''

# the nova of Arc Cascade needs a CommandBuffer: the cast runs with the Store, so the nova waits for the caster's next tick (NOVA)
UPFX_STATE.append("NOVA")

UPFX_JAVA2 = r'''
# ---------------------------------------------------------------- 3. OUTGOING: a player's weapon hit (DamageLock.outHook, the Filter group)
# the target-side bonuses ANY hit gets (Hunter's Mark / Barbed Mesh vulnerability; Radiant Beacon for an attacker inside a Sanctuary)
M(upfx, r"""
public static double vulnOf(@CAC@ acc, @REF@ t, @REF@ att, long now) {
  double b = timed(VULN, t, now);
  if (att != null && att.isValid()) {
    @VEC@ p = @PKG@.Abil.pos(acc, att);
    if (p != null) b = b + zoneCode(att.getStore(), 5, @C_sanctDmg@, p.x, p.y, p.z);
  }
  return b;
}""")
# an ABILITY hit's extra multiplier (Abil.hit, before the damage is made): the tree's conditional bonuses + the target-side ones
M(upfx, r"""
public static double outAbil(@CAC@ acc, @REF@ t, java.util.UUID u, String what, long now) {
  try {
    if (!ON || t == null || u == null || what == null || what.startsWith("Up")) return 1.0;
    double[] v = of(u);
    double b = 0.0;
    @PR@ pr = @PKG@.Abil.prOf(u);
    @REF@ att = pr == null ? null : pr.getReference();
    b = b + vulnOf(acc, t, att, now);
    if (v != null) {
      int ai = @PKG@.AbilDefs.find(what);
      if (has(v, @C_dmgElite@) && @PKG@.Abil.bossFor(acc, t, true)) b = b + g(v, @C_dmgElite@);
      if (has(v, @C_dmgDebuff@)) { int n = debuffs(t, now); b = b + g(v, @C_dmgDebuff@) * (double) (n > 3 ? 3 : n); }
      if (has(v, @C_dmgMarked@) && @PKG@.AbilStore.MARKD.get(t) instanceof double[] && ((double[]) @PKG@.AbilStore.MARKD.get(t))[0] > (double) now) b = b + g(v, @C_dmgMarked@);
      if (has(v, @C_dmgLowHp@) && att != null && att.isValid()) { double f = frac(acc, att, @DST@.getHealth()); if (f >= 0.0 && f < 0.6) b = b + g(v, @C_dmgLowHp@); }
      b = b + timed(BUFF, u, now);
      if (has(v, @C_comboSpell@)) {
        Object so = SPELLS.get(t);
        if (so instanceof Object[] && u.equals(((Object[]) so)[2]) && now - ((Long) ((Object[]) so)[1]).longValue() < 3000L && !what.equals(((Object[]) so)[0])) b = b + g(v, @C_comboSpell@);
        SPELLS.put(t, new Object[] { what, Long.valueOf(now), u });
        if (SPELLS.size() > 1024) SPELLS.clear();
      }
      if (ai == @PKG@.AbilDefs.RAPID && has(v, @C_xDeadEye@) && timed(RT, t, now) > 0.0) { b = b + @PKG@.AbilNum.CP_DEADEYE; timedPut(VULN, t, now + 5000L, g(v, @C_pinVuln@)); }
      if (ai == @PKG@.AbilDefs.SHATTER && has(v, @C_xFracture@) && @PKG@.AbilStore.SUNDER.get(t) instanceof double[] && ((double[]) @PKG@.AbilStore.SUNDER.get(t))[0] > (double) now) b = b + 50.0;
      if (has(v, @C_xGlacial@) && @PKG@.AbilStore.FROZEN.get(t) instanceof long[]) b = b + @PKG@.AbilNum.CP_GLACIALP;
      if (ai == @PKG@.AbilDefs.BEAM && has(v, @C_xPrism@)) {
        Object jo = @PKG@.AbilStore.CHAN.get(u);
        if (jo instanceof @PKG@.AbilJob) { double secs = (double) (now - ((@PKG@.AbilJob) jo).start) / 1000.0; double r = secs * @PKG@.AbilNum.CP_PRISMR; b = b + (r > @PKG@.AbilNum.CP_PRISMX ? @PKG@.AbilNum.CP_PRISMX : (r < 0.0 ? 0.0 : r)); }
      }
    }
    if (b > @PKG@.AbilNum.UX_DMGCAP) b = @PKG@.AbilNum.UX_DMGCAP;
    return 1.0 + b / 100.0;
  } catch (Throwable x) { warn("an ability hit bonus", x); return 1.0; }
}""")
M(upfx, r"""
public static void clonePull(@CB@ buf, @REF@ t, java.util.UUID u, double amt, long now) {
  Object o = CLONES.get(u);
  if (!(o instanceof java.util.ArrayList)) return;
  java.util.ArrayList l = (java.util.ArrayList) o;
  if (l.isEmpty()) return;
  double[] c = (double[]) l.get(0);
  if ((double) now >= c[3]) return;
  @VEC@ q = @PKG@.Abil.pos(buf, t);
  if (q == null) return;
  double dx = c[0] - q.x;
  double dz = c[2] - q.z;
  double dd = Math.sqrt(dx * dx + dz * dz);
  if (dd > 0.5) { double go = dd < 3.0 ? dd : 3.0; @PKG@.Abil.push(buf, t, dx / dd * go * @PKG@.AbilCfg.PUSH_PER_BLOCK, 0.6, dz / dd * go * @PKG@.AbilCfg.PUSH_PER_BLOCK); }
  QUEUE.put(t, new Object[] { u, Double.valueOf(amt * 0.4), "UpClone", Long.valueOf(now + 300L) });
}""")

# ---------------------------------------------------------------- 4. INCOMING: a hit on a player (AbilShieldSys, the Filter group)
M(upfx, r"""
public static double outW(@ST@ st, @CB@ buf, @REF@ t, @DMG@ d, java.util.UUID u, double[] v, long now) {
  @DSRC@ src = d.getSource();
  boolean proj = src instanceof @DPRJ@;
  String item = proj ? shotItem(buf, d) : null;
  @REF@ att = null;
  try { att = ((@DENT@) src).getRef(); } catch (Throwable x) { att = null; }
  boolean melee = !proj;
  boolean isBow = proj && bow(item);
  boolean isKunai = proj && kunai(item);
  double b = g(v, @C_dmgWeapon@);
  if (melee) b = b + g(v, @C_dmgMelee@);
  if (isBow) {
    b = b + g(v, @C_dmgBow@);
    if (has(v, @C_dmgFar@) && att != null) {
      @VEC@ p = @PKG@.Abil.pos(buf, att);
      @VEC@ q = @PKG@.Abil.pos(buf, t);
      if (p != null && q != null && (p.x - q.x) * (p.x - q.x) + (p.y - q.y) * (p.y - q.y) + (p.z - q.z) * (p.z - q.z) >= 225.0) b = b + g(v, @C_dmgFar@);
    }
  }
  if (has(v, @C_dmgLowHp@) && att != null) { double f = frac(buf, att, @DST@.getHealth()); if (f >= 0.0 && f < 0.6) b = b + g(v, @C_dmgLowHp@); }
  if (has(v, @C_dmgElite@) && @PKG@.Abil.bossFor(buf, t, true)) b = b + g(v, @C_dmgElite@);
  if (has(v, @C_dmgBehind@) && att != null && @PKG@.Abil.behindHit(buf, t, att)) b = b + g(v, @C_dmgBehind@);
  if (has(v, @C_dmgDebuff@)) { int n = debuffs(t, now); b = b + g(v, @C_dmgDebuff@) * (double) (n > 3 ? 3 : n); }
  if (has(v, @C_dmgMarked@) && @PKG@.AbilStore.MARKD.get(t) instanceof double[] && ((double[]) @PKG@.AbilStore.MARKD.get(t))[0] > (double) now) b = b + g(v, @C_dmgMarked@);
  if (has(v, @C_dmgFocus@)) {
    Object fo = FOCUS.get(u);
    int stk = 0;
    if (fo instanceof Object[] && t.equals(((Object[]) fo)[0]) && now - ((Long) ((Object[]) fo)[2]).longValue() < 3000L) stk = ((Integer) ((Object[]) fo)[1]).intValue();
    b = b + g(v, @C_dmgFocus@) * (double) stk;
    FOCUS.put(u, new Object[] { t, Integer.valueOf(stk >= (int) @PKG@.AbilNum.UX_FOCUSN ? (int) @PKG@.AbilNum.UX_FOCUSN : stk + 1), Long.valueOf(now) });
  }
  if (has(v, @C_fistsDmg@)) {
    Object fz = @PKG@.AbilStore.FLOWS.get(u);
    if (fz instanceof @PKG@.AbilZone && !((@PKG@.AbilZone) fz).ended && ((@PKG@.AbilZone) fz).ai == @PKG@.AbilDefs.HFISTS) b = b + g(v, @C_fistsDmg@);
  }
  b = b + timed(BUFF, u, now);
  if (has(v, @C_vanishHit@)) { Object vo = VANT.remove(u); if (vo instanceof Long && now < ((Long) vo).longValue()) b = b + g(v, @C_vanishHit@); }
  if (melee && has(v, @C_kunaiMark@)) {
    Object ko = KMARK.get(t);
    if (ko instanceof long[] && ((long[]) ko)[0] > now && ((long[]) ko)[1] == u.getMostSignificantBits() && ((long[]) ko)[2] == u.getLeastSignificantBits()) { b = b + g(v, @C_kunaiMark@); KMARK.remove(t); }
  }
  // the First Strike / God Killer hit about to land (outHit consumes them after this): Bloodthirst, Ambush / Ghost kill tracking, Deicide, clone pull
  boolean fs = @PKG@.AbilStore.STRIKE.get(u) instanceof double[] && (double) now < ((double[]) @PKG@.AbilStore.STRIKE.get(u))[0];
  boolean gk = @PKG@.AbilStore.ARMED.get(u) instanceof double[] && (double) now < ((double[]) @PKG@.AbilStore.ARMED.get(u))[0] && @PKG@.Abil.bossFor(buf, t, ((double[]) @PKG@.AbilStore.ARMED.get(u))[6] > 0.0);
  if (fs) FSHIT.put(u, new Object[] { t, Long.valueOf(now) });
  if (gk) GKHIT.put(u, new Object[] { t, Long.valueOf(now) });
  if ((fs || gk) && has(v, @C_bigHitBuff@)) timedPut(BUFF, u, now + 4000L, g(v, @C_bigHitBuff@));
  if (gk && has(v, @C_xDeicide@)) {
    double f = frac(buf, t, @DST@.getHealth());
    if (f >= 0.0) { double miss = (1.0 - f) * 100.0; b = b + (miss > 60.0 ? 60.0 : miss); }
  }
  if (fs && has(v, @C_clonePull@)) clonePull(buf, t, u, (double) d.getAmount(), now);
  if (b > @PKG@.AbilNum.UX_DMGCAP) b = @PKG@.AbilNum.UX_DMGCAP;
  double mult = 1.0 + b / 100.0;
  if (has(v, @C_lethal@) && Math.random() * 100.0 < g(v, @C_lethal@)) { mult = mult * (1.0 + @PKG@.AbilNum.UX_LETHAL / 100.0); PROCS = PROCS + 1L; }
  if (isKunai) {
    if (has(v, @C_kunaiMark@)) { capMob(KMARK, now); KMARK.put(t, new long[] { now + 5000L, u.getMostSignificantBits(), u.getLeastSignificantBits() }); }
    if (has(v, @C_kunaiWeak@)) timedPut(WEAK, t, now + 4000L, g(v, @C_kunaiWeak@));
  }
  return mult;
}""")
M(upfx, r"""
public static void out(@ST@ st, @CB@ buf, @REF@ t, @DMG@ d, java.util.UUID u, long now) {
  try {
    if (d == null || t == null || u == null || d.isCancelled()) return;
    float a0 = d.getAmount();
    if (!(a0 > 0.0f)) return;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return;
    double[] v = of(u);
    @REF@ att = null;
    try { att = ((@DENT@) d.getSource()).getRef(); } catch (Throwable x) { att = null; }
    double vb = vulnOf(st, t, att, now);
    double m = v == null ? 1.0 : outW(st, buf, t, d, u, v, now);
    if (vb > 0.0) m = m * (1.0 + vb / 100.0);
    if (m != 1.0 && m > 0.0) { d.setAmount((float) ((double) a0 * m)); BOOSTS = BOOSTS + 1L; }
  } catch (Throwable x) { warn("a weapon hit bonus", x); }
}""")
# a rooted enemy within rad blocks (RT = every root an ability put on, Abil.rootMob)
M(upfx, r"""
public static boolean rootedNear(@CAC@ acc, @REF@ r, double rad, long now) {
  if (RT.isEmpty()) return false;
  @VEC@ p = @PKG@.Abil.pos(acc, r);
  if (p == null) return false;
  java.util.Iterator it = RT.keySet().iterator();
  int seen = 0;
  while (it.hasNext() && seen < 64) {
    Object k = it.next();
    seen++;
    if (!(k instanceof @REF@) || timed(RT, k, now) <= 0.0) continue;
    @REF@ t = (@REF@) k;
    if (!t.isValid() || t.getStore() != r.getStore()) continue;
    @VEC@ q = @PKG@.Abil.pos(acc, t);
    if (q != null && @PKG@.AbilMath.inRange(q.x - p.x, q.y - p.y, q.z - p.z, rad)) return true;
  }
  return false;
}""")
# Aegis Eternal: a Warrior with the capstone whose Challenge holds, within 6 blocks -> 10 % less
M(upfx, r"""
public static double aegisNear(@ST@ st, @CAC@ acc, @VEC@ p, long now) {
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
  if (aw == null || aw.nz == 0) return 0.0;
  @PKG@.AbilZone[] zs = aw.zoneArr();
  for (int i = 0; i < zs.length; i++) {
    @PKG@.AbilZone z = zs[i];
    if (z == null || z.ended || z.kind != 14 || !has(of(z.caster), @C_xAegis@)) continue;
    if (@PKG@.AbilMath.inRange(p.x - z.x, p.y - z.y, p.z - z.z, @PKG@.AbilNum.UX_AEGISR)) return @PKG@.AbilNum.CP_AEGISC;
  }
  return 0.0;
}""")
M(upfx, r"""
public static double cutOf(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, java.util.UUID u, double[] v, @REF@ att, boolean proj, boolean ent, long now) {
  double c = 0.0;
  if (v != null) {
    if (!proj && ent) c = c + g(v, @C_drMelee@);
    if (proj) c = c + g(v, @C_drRanged@);
    if (proj) c = c + g(v, @C_drMagic@);   // magic = the projectiles mobs throw (never fall / fire / drowning)
    if (has(v, @C_drStill@)) { Object so = STILL.get(u); if (so instanceof double[] && now - (long) ((double[]) so)[3] >= 1000L) c = c + g(v, @C_drStill@); }
    if (has(v, @C_drShieldUp@) && (@PKG@.AbilStore.WARD.get(u) instanceof double[] || zoneOf(st, u, 2) != null)) c = c + g(v, @C_drShieldUp@);
    if (has(v, @C_drRooted@) && rootedNear(buf, r, 8.0, now)) c = c + g(v, @C_drRooted@);
    if (att != null) {
      if (has(v, @C_debuffWeak@) && (@PKG@.Abil.breachPct(att, now) > 0.0 || (@PKG@.AbilStore.SUNDER.get(att) instanceof double[] && ((double[]) @PKG@.AbilStore.SUNDER.get(att))[0] > (double) now))) c = c + g(v, @C_debuffWeak@);
      if (has(v, @C_rootWeak@) && timed(RT, att, now) > 0.0) c = c + g(v, @C_rootWeak@);
      if (has(v, @C_poisonWeak@) && @PKG@.AbilStore.POISONED.get(att) instanceof long[] && ((long[]) @PKG@.AbilStore.POISONED.get(att))[0] > now) c = c + g(v, @C_poisonWeak@);
    }
  }
  if (att != null) {
    c = c + timed(WEAK, att, now);
    @VEC@ ap0 = @PKG@.Abil.pos(buf, att);
    if (ap0 != null) c = c + zoneCode(st, 5, @C_sanctWeak@, ap0.x, ap0.y, ap0.z);
  }
  c = c + timed(DRB, u, now);
  @VEC@ p = @PKG@.Abil.pos(buf, r);
  if (p != null) {
    c = c + zoneCode(st, 2, @C_bubbleDr@, p.x, p.y, p.z);
    c = c + aegisNear(st, buf, p, now);
  }
  return c;
}""")
M(upfx, r"""
public static boolean blocked(@DMG@ d) {
  try { Object o = d.getIfPresentMetaObject(@DMG@.BLOCKED); return Boolean.TRUE.equals(o); } catch (Throwable t) { return false; }
}""")
M(upfx, r"""
public static String inc(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  try {
    if (d == null || r == null || d.isCancelled()) return null;
    float a0 = d.getAmount();
    Object po = buf.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return null;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null) return null;
    double[] v = of(u);
    @DSRC@ src = d.getSource();
    boolean ent = src instanceof @DENT@;
    boolean proj = src instanceof @DPRJ@;
    @REF@ att = null;
    if (ent) { try { att = ((@DENT@) src).getRef(); } catch (Throwable x) { att = null; } }
    if (att != null && (!att.isValid() || buf.getComponent(att, @NPC@.getComponentType()) == null)) att = null;
    String out = "";
    if (a0 > 0.0f) {   // a fully blocked hit (0 left) still runs the block effects below
      double cut = cutOf(st, buf, r, d, u, v, att, proj, ent, now);
      if (cut > @PKG@.AbilNum.UX_DRCAP) cut = @PKG@.AbilNum.UX_DRCAP;
      if (cut > 0.0) { d.setAmount((float) ((double) a0 * (1.0 - cut / 100.0))); CUTS = CUTS + 1L; out = "cut" + @PKG@.AbilMath.fmt(cut); }
    }
    if (v != null && att != null && blocked(d)) {
      double sl = g(v, @C_blockSlow@) + (has(v, @C_xAegis@) ? @PKG@.AbilNum.CP_AEGISS : 0.0);
      if (sl > 0.0) { slow(buf, att, sl, @PKG@.AbilNum.UX_SLOWW); out = out + " blockslow"; }
      if (has(v, @C_blockHeal@) && gap(BLOCKT, u, 500L, now)) { heal(buf, r, g(v, @C_blockHeal@)); out = out + " blockheal"; }
    }
    if (v != null && att != null && has(v, @C_barrierSlow@)) {
      @PKG@.AbilZone bz = zoneOf(st, u, 1);
      @VEC@ p = @PKG@.Abil.pos(buf, r);
      if (bz != null && p != null && inZone(bz, p.x, p.y, p.z)) slow(buf, att, g(v, @C_barrierSlow@), @PKG@.AbilNum.UX_SLOWW);
    }
    @VEC@ p2 = @PKG@.Abil.pos(buf, r);
    if (p2 != null && zoneCode(st, 5, @C_xHolyLand@, p2.x, p2.y, p2.z) > 0.0) { buf.tryRemoveComponent(r, @KBC@.getComponentType()); out = out + " steady"; }
    return out.length() == 0 ? null : out.trim();
  } catch (Throwable x) { warn("a damage cut", x); return null; }
}""")
# LAST WARD (before Guardian Spirit, after every shield): a killing blow is cancelled once per 60 s and leaves a 1 s ward
M(upfx, r"""
public static String incLast(@ST@ st, @CB@ buf, @REF@ r, @DMG@ d, long now) {
  try {
    if (d == null || r == null || d.isCancelled()) return null;
    Object po = buf.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return null;
    java.util.UUID u = ((@PR@) po).getUuid();
    double[] v = of(u);
    if (v == null || !has(v, @C_lastWard@)) return null;
    @ESM@ m = @PKG@.Abil.map(buf, r);
    double h = @PKG@.Abil.cur(m, @DST@.getHealth());
    double mx = @PKG@.Abil.max(m, @DST@.getHealth());
    if (!(h > 0.0) || (double) d.getAmount() < h - 1.0E-4) return null;
    if (!gap(LASTW, u, Math.round(@PKG@.AbilNum.UX_LASTW * 1000.0), now)) return null;
    d.setAmount(0.0f);
    d.setCancelled(true);
    @PKG@.Abil.wardGive(u, mx > 0.0 ? mx * 10.0 : 1000.0, now + 1000L);
    CAPS = CAPS + 1L;
    @PKG@.Abil.say((@PR@) po, "Last Ward: a killing blow was cancelled (again in 60 s).");
    return "lastward";
  } catch (Throwable x) { warn("Last Ward", x); return null; }
}""")
# a deflected projectile (Still Water) hits its shooter back
M(upfx, r"""
public static void deflect(@CB@ buf, @REF@ r, @REF@ att, double amt, java.util.UUID u) {
  try {
    double[] v = of(u);
    if (v == null || att == null || !has(v, @C_deflectBack@) || !@PKG@.Abil.enemy(buf, att, r)) return;
    @PKG@.Abil.hit(buf, att, r, u, amt * g(v, @C_deflectBack@) / 100.0, "UpDeflect");
    PROCS = PROCS + 1L;
  } catch (Throwable x) { warn("a deflect back", x); }
}""")
M(upfx, r"""
public static void countered(@CB@ buf, @REF@ r, java.util.UUID u, @REF@ att, @PKG@.AbilZone z, long now) {
  try {
    double[] v = of(u);
    if (v == null) return;
    if (has(v, @C_stanceSlow@)) slow(buf, att, g(v, @C_stanceSlow@), @PKG@.AbilNum.UX_SLOWW);
    if (has(v, @C_xNoMind@) && gap(NOMIND, u, Math.round(@PKG@.AbilNum.UX_NOMIND * 1000.0), now)) {
      String k = @PKG@.ClassCfg.pkey(u);
      for (int i = 0; i < @PKG@.AbilDefs.IDS.length; i++) {
        if (@PKG@.AbilDefs.CLS[i] != @PKG@.AbilDefs.CLS[@PKG@.AbilDefs.STILLW] || i == @PKG@.AbilDefs.STILLW) continue;
        @PKG@.AbilStore.arm(k, @PKG@.AbilDefs.IDS[i], now, 0L);
      }
      if (z != null && !z.ended) z.until = z.until + 3000L;
      CAPS = CAPS + 1L;
      @PR@ pr = @PKG@.Abil.prOf(u);
      if (pr != null) @PKG@.Abil.say(pr, "No Mind: your other cooldowns reset; Still Water holds 3 s longer.");
    }
  } catch (Throwable x) { warn("a counter", x); }
}""")
M(upfx, r"""
public static void flowEnded(@PKG@.AbilZone z, @CAC@ acc, @REF@ cr) {
  try {
    if (z == null || z.cx == null || cr == null || !cr.isValid()) return;
    double[] v = vec(z.cx.tree);
    if (!has(v, @C_flowWard@)) return;
    double mx = @PKG@.Abil.max(@PKG@.Abil.map(acc, cr), @DST@.getHealth());
    if (mx > 0.0) @PKG@.Abil.wardGive(z.caster, mx * wardPct(z.caster, g(v, @C_flowWard@)) / 100.0, System.currentTimeMillis() + 6000L);
  } catch (Throwable x) { warn("Flowing Form's ward", x); }
}""")
M(upfx, r"""
public static void cloakEnded(@PKG@.AbilZone z, @CAC@ acc, @REF@ cr) {
  try {
    if (z == null || z.cx == null || cr == null) return;
    long now = System.currentTimeMillis();
    CLOAKEND.put(z.caster, Long.valueOf(now));
    double[] v = vec(z.cx.tree);
    if (!"attack".equals(z.why) || !has(v, @C_cloakBlind@)) return;
    @VEC@ p = @PKG@.Abil.pos(acc, cr);
    if (p == null) return;
    java.util.List l = @PKG@.Abil.near(acc, p.x, p.y, p.z, 3.0);
    for (int i = 0; i < l.size(); i++) {
      Object o = l.get(i);
      if (o instanceof @REF@ && @PKG@.Abil.enemy(acc, (@REF@) o, cr)) @PKG@.Abil.stunMob(acc, (@REF@) o, z.caster, g(v, @C_cloakBlind@), now);
    }
  } catch (Throwable x) { warn("Smoke Veil", x); }
}""")
# the leech heal of the class tree: Red Mist (more below 30 %), Crimson Eternal (overheal -> a ward up to 10 % of max Health)
M(upfx, r"""
public static double leech(@CAC@ acc, @REF@ r, java.util.UUID u, double amt) {
  if (r == null || !(amt > 0.0)) return 0.0;
  double[] v = of(u);
  double a = amt;
  double f = frac(acc, r, @DST@.getHealth());
  if (has(v, @C_redMist@) && f >= 0.0 && f < 0.3) a = a * (1.0 + g(v, @C_redMist@) / 100.0);
  double got = @PKG@.Abil.apply(acc, r, a, a);
  if (has(v, @C_xCrimson@) && a - got > 0.5) {
    double mx = @PKG@.Abil.max(@PKG@.Abil.map(acc, r), @DST@.getHealth());
    double w = a - got;
    if (mx > 0.0 && w > mx * 0.1) w = mx * 0.1;
    Object wo = @PKG@.AbilStore.WARD.get(u);
    double have = wo instanceof double[] && ((double[]) wo)[1] > (double) System.currentTimeMillis() ? ((double[]) wo)[0] : 0.0;
    double cap = mx > 0.0 ? mx * 0.1 : w;
    double nw = have + w > cap ? cap : have + w;
    if (nw > have) @PKG@.AbilStore.WARD.put(u, new double[] { nw, (double) (System.currentTimeMillis() + 5000L) });
    @PKG@.AbilStore.WARDP.put(u, @PKG@.ClassCfg.pkey(u));
  }
  return got;
}""")
'''

UPFX_JAVA3 = r'''
# ---------------------------------------------------------------- 5. LANDED: a hit that really landed (AbilFrostSys, the Inspect group)
M(upfx, r"""
public static @REF@ other(@CAC@ acc, @REF@ cr, @REF@ t, double r) {
  @VEC@ q = @PKG@.Abil.pos(acc, t);
  if (q == null) return null;
  return @PKG@.Abil.nearest(acc, cr, q.x, q.y, q.z, r, t);
}""")
M(upfx, r"""
public static boolean cloneUp(java.util.UUID u, long now) {
  Object o = CLONES.get(u);
  if (!(o instanceof java.util.ArrayList)) return false;
  java.util.ArrayList l = (java.util.ArrayList) o;
  for (int i = 0; i < l.size(); i++) if ((double) now < ((double[]) l.get(i))[3]) return true;
  return false;
}""")
M(upfx, r"""
public static void firestorm(@CB@ buf, @REF@ cr, @REF@ t, java.util.UUID u, double amt, long now) {
  @VEC@ q = @PKG@.Abil.pos(buf, t);
  @PKG@.AbilWorld aw = null;
  try { aw = @PKG@.AbilWorld.at(t.getStore()); } catch (Throwable x) { aw = null; }
  if (q == null || aw == null) return;
  @PKG@.AbilZone[] zs = aw.zoneArr();
  for (int i = 0; i < zs.length; i++) {
    @PKG@.AbilZone z = zs[i];
    if (z == null || z.ended || z.kind != 19 || !u.equals(z.caster) || FIRED.containsKey(z) || !inZone(z, q.x, q.y, q.z)) continue;
    FIRED.put(z, Long.valueOf(now));
    if (FIRED.size() > 256) FIRED.clear();
    int n = @PKG@.Abil.burst(buf, cr, u, z.x, z.y, z.z, z.r, amt * 1.5, "UpFirestorm");
    CAPS = CAPS + 1L;
    @PR@ pr = @PKG@.Abil.prOf(u);
    if (pr != null) @PKG@.Abil.say(pr, "Firestorm: your Arrow Rain exploded on " + n + (n == 1 ? " enemy." : " enemies."));
    return;
  }
}""")
M(upfx, r"""
public static void landedAbil(@CB@ buf, @REF@ t, @REF@ att, java.util.UUID u, double[] v, String what, double amt, boolean dead, long now) {
  int ai = @PKG@.AbilDefs.find(what);
  if (ai < 0) return;
  String k = @PKG@.ClassCfg.pkey(u);
  double sl = ap(v, ai, 6);
  if (sl > 0.0) slow(buf, t, sl, @PKG@.AbilNum.UX_SLOWA);
  double kb = ap(v, ai, 7) + (ai == @PKG@.AbilDefs.METEOR ? 0.0 : 0.0);
  if (kb > 0.0 && ai != @PKG@.AbilDefs.METEOR) { @VEC@ p = @PKG@.Abil.pos(buf, att); if (p != null) pushFrom(buf, t, p.x, p.z, kb); }
  double dot = ap(v, ai, 8);
  if (dot > 0.0) @PKG@.Abil.dotOn(buf, t, u, "UpDot", amt * dot / 100.0, 3.0, 1, now);
  double hl = ap(v, ai, 9);
  if (hl > 0.0 && take(uk(u, "heal" + ai), 5, 2000L, now)) heal(buf, att, hl);
  int ch = rk(v, ai, 10);
  if (ch > 0 && take(uk(u, "chain" + ai), ch, Math.round(@PKG@.AbilNum.UX_CHAING * 1000.0), now)) { @REF@ o = other(buf, att, t, 6.0); if (o != null) { @PKG@.Abil.hit(buf, o, att, u, amt * 0.5, "UpChain"); PROCS = PROCS + 1L; } }
  double bo = ap(v, ai, 11);
  if (bo > 0.0 && take(uk(u, "bounce" + ai), 1, 250L, now)) { @REF@ o = other(buf, att, t, 6.0); if (o != null) { @PKG@.Abil.hit(buf, o, att, u, amt * bo / 100.0, "UpBounce"); PROCS = PROCS + 1L; } }
  double rp = ap(v, ai, 12);
  if (rp > 0.0 && !dead) { @PKG@.Abil.hit(buf, t, att, u, amt * rp / 100.0, "UpRepeat"); PROCS = PROCS + 1L; }
  double rc = ap(v, ai, 18);
  if (rc > 0.0 && Math.random() * 100.0 < rc) @PKG@.Abil.rootMob(buf, t, u, 0.5, now, false, false);
  double sc = ap(v, ai, 19);
  if (sc > 0.0 && Math.random() * 100.0 < sc) @PKG@.Abil.stunMob(buf, t, u, @PKG@.AbilNum.SS_STUN + 1.0, now);
  if (ai == @PKG@.AbilDefs.STARF && has(v, @C_starCd@)) cdCut(k, "Meteor", Math.round(g(v, @C_starCd@) * 1000.0), now);
  if (ai == @PKG@.AbilDefs.PIN) {
    if (has(v, @C_pinVuln@)) timedPut(VULN, t, now + 5000L, g(v, @C_pinVuln@));
    if (has(v, @C_pinBounce@) && take(uk(u, "pinb"), 1, 500L, now)) { @REF@ o = other(buf, att, t, 6.0); if (o != null) @PKG@.Abil.rootMob(buf, o, u, @PKG@.AbilNum.PN_ROOT * g(v, @C_pinBounce@) / 100.0, now, false, false); }
  }
  if (ai == @PKG@.AbilDefs.NET) {
    if (has(v, @C_netVuln@)) timedPut(VULN, t, now + Math.round((@PKG@.AbilNum.HN_TIME + 2.0) * 1000.0), g(v, @C_netVuln@));
    if (has(v, @C_netSlow@)) slow(buf, t, 15.0, @PKG@.AbilNum.HN_TIME + g(v, @C_netSlow@));
    if (has(v, @C_xSpider@)) { Object no = NETTED.get(t); if (no instanceof Long && now - ((Long) no).longValue() < 6000L && now - ((Long) no).longValue() > 400L) @PKG@.Abil.stunMob(buf, t, u, @PKG@.AbilNum.CP_SPIDERS, now); capMob(NETTED, now); NETTED.put(t, Long.valueOf(now)); }
  }
  if (ai == @PKG@.AbilDefs.EXPLO && has(v, @C_xFirestorm@)) firestorm(buf, att, t, u, amt, now);
  if (ai == @PKG@.AbilDefs.TOXIN && has(v, @C_xLotus@)) {
    Object lo = LOTUS.get(t);
    long[] lc = null;
    if (lo instanceof long[] && ((long[]) lo)[0] == u.getMostSignificantBits() && ((long[]) lo)[1] == u.getLeastSignificantBits()) lc = (long[]) lo;
    if (lc == null) lc = new long[] { u.getMostSignificantBits(), u.getLeastSignificantBits(), 0L };
    lc[2] = lc[2] + 1L;
    if (lc[2] >= 3L) { lc[2] = 0L; if (!dead) { @PKG@.Abil.hit(buf, t, att, u, amt * @PKG@.AbilNum.CP_LOTUS / 100.0, "UpLotus"); CAPS = CAPS + 1L; } }
    LOTUS.put(t, lc);
    if (LOTUS.size() > 1024) LOTUS.clear();
  }
  if (has(v, @C_cloneMirror@) && cloneUp(u, now) && take(uk(u, "mirror"), 1, 300L, now) && !dead) {
    @PKG@.Abil.hit(buf, t, att, u, amt * (15.0 + g(v, @C_cloneMirror@)) / 100.0, "UpMirror");
    PROCS = PROCS + 1L;
  }
}""")
M(upfx, r"""
public static void landedWeapon(@CB@ buf, @REF@ t, @REF@ att, java.util.UUID u, double[] v, @DMG@ d, double amt, long now) {
  boolean proj = false;
  try { proj = d.getSource() instanceof @DPRJ@; } catch (Throwable x) { proj = false; }
  String item = proj ? shotItem(buf, d) : null;
  boolean isBow = proj && bow(item);
  boolean melee = !proj;
  if (melee) {
    Object ho = HITS.get(u);
    int[] hc = null;
    if (ho instanceof int[]) hc = (int[]) ho;
    if (hc == null) hc = new int[2];
    HITS.put(u, hc);
    hc[0] = hc[0] + 1;
    if (has(v, @C_echo5@) && hc[0] % 5 == 0) { @PKG@.Abil.hit(buf, t, att, u, amt * g(v, @C_echo5@) / 100.0, "UpEcho"); PROCS = PROCS + 1L; }
    if (has(v, @C_xPalms@) && hc[0] % 5 == 0 && flowStacks(u, now) > 0) { @VEC@ q = @PKG@.Abil.pos(buf, t); if (q != null) { @PKG@.Abil.burst(buf, att, u, q.x, q.y, q.z, 3.0, amt * @PKG@.AbilNum.CP_PALMSH / 100.0, "UpPalms"); CAPS = CAPS + 1L; } }
    if (has(v, @C_cleave@)) { @REF@ o = other(buf, att, t, 3.0); if (o != null) { @PKG@.Abil.hit(buf, o, att, u, amt * g(v, @C_cleave@) / 100.0, "UpCleave"); PROCS = PROCS + 1L; } }
    if (has(v, @C_kbMelee@)) { @VEC@ p = @PKG@.Abil.pos(buf, att); if (p != null) pushFrom(buf, t, p.x, p.z, g(v, @C_kbMelee@)); }
    if (has(v, @C_momChance@) && Math.random() * 100.0 < g(v, @C_momChance@)) @PKG@.Abil.momAdd(u, 1, now);
    if (has(v, @C_comboStam@)) { int s = flowStacks(u, now); if (s > 0 && s % 5 == 0) stat(buf, att, @DST@.getStamina(), g(v, @C_comboStam@)); }
  }
  if (isBow) {
    if (has(v, @C_bowSlow@)) slow(buf, t, g(v, @C_bowSlow@), @PKG@.AbilNum.UX_SLOWW);
    if (has(v, @C_bowKb@)) { @VEC@ p = @PKG@.Abil.pos(buf, att); if (p != null) pushFrom(buf, t, p.x, p.z, g(v, @C_bowKb@)); }
    if (has(v, @C_bowSplit@)) {
      int n = ranks(v, @C_bowSplit@);
      java.util.HashSet done = new java.util.HashSet();
      done.add(t);
      @VEC@ q = @PKG@.Abil.pos(buf, t);
      for (int i = 0; i < n && q != null; i++) {
        java.util.List l = @PKG@.Abil.near(buf, q.x, q.y, q.z, 4.0);
        @REF@ best = null;
        for (int j = 0; j < l.size() && best == null; j++) { Object o = l.get(j); if (o instanceof @REF@ && !done.contains(o) && @PKG@.Abil.enemy(buf, (@REF@) o, att)) best = (@REF@) o; }
        if (best == null) break;
        done.add(best);
        @PKG@.Abil.hit(buf, best, att, u, amt * PER[@C_bowSplit@] / 100.0, "UpSplit");
        PROCS = PROCS + 1L;
      }
    }
    if (has(v, @C_bowCdRapid@) && gap(BOWT, u, 500L, now)) cdCut(@PKG@.ClassCfg.pkey(u), "RapidFire", Math.round(g(v, @C_bowCdRapid@) * 1000.0), now);
  }
  if (proj && kunai(item) && has(v, @C_kunaiChain@)) { @REF@ o = other(buf, att, t, 6.0); if (o != null) { @PKG@.Abil.hit(buf, o, att, u, amt * g(v, @C_kunaiChain@) / 100.0, "UpKunai"); PROCS = PROCS + 1L; } }
  Object io = @PKG@.AbilStore.IMBUE.get(u);
  if (io instanceof double[] && ((double[]) io)[0] > (double) now) {
    if (has(v, @C_imbueSlow@)) slow(buf, t, g(v, @C_imbueSlow@), @PKG@.AbilNum.UX_SLOWW);
    if (has(v, @C_imbueHeal@) && gap(IMBT, u, 500L, now)) heal(buf, att, g(v, @C_imbueHeal@));
  }
  Object so = @PKG@.AbilStore.STANCES.get(u);
  if (so instanceof @PKG@.AbilZone && !((@PKG@.AbilZone) so).ended && has(v, @C_stanceSlow@)) slow(buf, t, g(v, @C_stanceSlow@), @PKG@.AbilNum.UX_SLOWW);
}""")
M(upfx, r"""
public static void recloak(@CB@ buf, @REF@ att, java.util.UUID u, String k, double secs, long now, String why) {
  @PR@ pr = @PKG@.Abil.prOf(u);
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(buf.getExternalData()));
  @PKG@.Abil.cloakAt(pr, buf, att, u, k, aw, secs, 0, now, -1);
  CAPS = CAPS + 1L;
  if (pr != null) @PKG@.Abil.say(pr, why + ": cloaked " + @PKG@.AbilMath.fmt(secs) + " s.");
}""")

# a kill: Thirst, Fleet Ranger, Feedback, a First Strike / God Killer kill (Ambush, Ghost Protocol, Deicide), Slipstream, Contagion, Second Wind,
# the debuff spread (Spellblade), Warlord's Domain (+2 s to Enrage / Blood Frenzy)
M(upfx, r"""
public static void killed(@CB@ buf, @REF@ t, @REF@ att, java.util.UUID u, double[] v, boolean abil, String what, long now) {
  KILLS = KILLS + 1L;
  String k = @PKG@.ClassCfg.pkey(u);
  if (has(v, @C_killHeal@)) heal(buf, att, g(v, @C_killHeal@));
  if (has(v, @C_killStam@)) stat(buf, att, @DST@.getStamina(), g(v, @C_killStam@));
  if (abil && "ArcaneBeam".equals(what) && has(v, @C_beamKillMana@)) { double mx = @PKG@.Abil.max(@PKG@.Abil.map(buf, att), @DST@.getMana()); if (mx > 0.0) stat(buf, att, @DST@.getMana(), mx * g(v, @C_beamKillMana@) / 100.0); }
  Object fo = FSHIT.get(u);
  boolean fsKill = fo instanceof Object[] && t.equals(((Object[]) fo)[0]) && now - ((Long) ((Object[]) fo)[1]).longValue() < 1000L;
  if (fsKill) {
    FSHIT.remove(u);
    if (has(v, @C_fsKillCd@)) cdCut(k, "CloakFirstStrike", Math.round(g(v, @C_fsKillCd@) * 1000.0), now);
    if (has(v, @C_xGhost@) && gap(GHOST, u, Math.round(@PKG@.AbilNum.UX_GHOST * 1000.0), now)) recloak(buf, att, u, k, 3.0, now, "Ghost Protocol");
  }
  Object go = GKHIT.get(u);
  if (go instanceof Object[] && t.equals(((Object[]) go)[0]) && now - ((Long) ((Object[]) go)[1]).longValue() < 1000L && has(v, @C_xDeicide@)) {
    GKHIT.remove(u);
    @PKG@.AbilStore.arm(k, "GodKiller", now, 0L);
    CAPS = CAPS + 1L;
    @PR@ pr = @PKG@.Abil.prOf(u);
    if (pr != null) @PKG@.Abil.say(pr, "Deicide: God Killer is ready again.");
  }
  if (has(v, @C_killCloak@)) {
    Object co = @PKG@.AbilStore.CLOAKS.get(u);
    Object eo = CLOAKEND.get(u);
    if (co instanceof @PKG@.AbilZone && !((@PKG@.AbilZone) co).ended) ((@PKG@.AbilZone) co).until = ((@PKG@.AbilZone) co).until + Math.round(g(v, @C_killCloak@) * 1000.0);
    else if (eo instanceof Long && now - ((Long) eo).longValue() < 400L) recloak(buf, att, u, k, g(v, @C_killCloak@), now, "Slipstream");
  }
  Object pso = @PKG@.AbilStore.POISONED.get(t);
  boolean pois = pso instanceof long[] && ((long[]) pso)[0] > now - 1000L && ((long[]) pso)[1] == u.getMostSignificantBits() && ((long[]) pso)[2] == u.getLeastSignificantBits();
  if (pois && has(v, @C_poisonKillStam@)) stat(buf, att, @DST@.getStamina(), g(v, @C_poisonKillStam@));
  if (pois && has(v, @C_contagion@)) {
    int n = (int) Math.round(g(v, @C_contagion@));
    @VEC@ q = @PKG@.Abil.pos(buf, t);
    double amt = @PKG@.Abil.hOf(@PKG@.Abil.hand(buf, att)) * @PKG@.AbilNum.TX_POISON;
    java.util.List l = q == null ? new java.util.ArrayList() : @PKG@.Abil.near(buf, q.x, q.y, q.z, 5.0);
    int done = 0;
    for (int i = 0; i < l.size() && done < n; i++) {
      Object o = l.get(i);
      if (!(o instanceof @REF@) || t.equals(o) || !@PKG@.Abil.enemy(buf, (@REF@) o, att)) continue;
      @PKG@.Abil.poisonOne(buf, (@REF@) o, att, u, amt, (double) @PKG@.AbilNum.TX_WEAKEN, false, false, now);
      done++;
    }
  }
  if (has(v, @C_spreadDebuff@)) {
    Object bo = @PKG@.AbilStore.BREACH.get(t);
    Object so = @PKG@.AbilStore.SUNDER.get(t);
    if ((bo instanceof double[] && ((double[]) bo)[0] > (double) now) || (so instanceof double[] && ((double[]) so)[0] > (double) now)) {
      int n = (int) Math.round(g(v, @C_spreadDebuff@));
      @VEC@ q = @PKG@.Abil.pos(buf, t);
      java.util.List l = q == null ? new java.util.ArrayList() : @PKG@.Abil.near(buf, q.x, q.y, q.z, 6.0);
      int done = 0;
      for (int i = 0; i < l.size() && done < n; i++) {
        Object o = l.get(i);
        if (!(o instanceof @REF@) || t.equals(o) || !@PKG@.Abil.enemy(buf, (@REF@) o, att)) continue;
        if (bo instanceof double[]) @PKG@.AbilStore.BREACH.put(o, copy((double[]) bo));
        if (so instanceof double[]) @PKG@.AbilStore.SUNDER.put(o, copy((double[]) so));
        done++;
      }
    }
  }
  if (has(v, @C_xDomain@)) {
    Object ro = @PKG@.AbilStore.RAGE.get(u);
    if (ro instanceof double[] && ((double[]) ro).length > 2) ((double[]) ro)[2] = ((double[]) ro)[2] + @PKG@.AbilNum.CP_DOMAINK * 1000.0;
    Object fu = @PKG@.AbilStore.FURY.get(u);
    if (fu instanceof double[] && ((double[]) fu).length > 1) ((double[]) fu)[1] = ((double[]) fu)[1] + @PKG@.AbilNum.CP_DOMAINK * 1000.0;
  }
}""")
M(upfx, r"""
public static void landed(@CB@ buf, @REF@ t, @DMG@ d, long now) {
  try {
    if (d == null || t == null || d.isCancelled() || !(d.getAmount() > 0.0f)) return;
    if (buf.getComponent(t, @NPC@.getComponentType()) == null) return;
    boolean abil = @PKG@.AbilDmg.mine(d);
    String what = abil ? @PKG@.AbilDmg.whatOf(d) : null;
    if (what != null && what.startsWith("Up")) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid() || att.equals(t)) return;
    Object po = buf.getComponent(att, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null) return;
    double amt = (double) d.getAmount();
    boolean dead = !@PKG@.Abil.alive(buf, t);
    // Blood Price: any player inside a banner whose Berserker has it leeches (the banner's owner's code)
    @VEC@ ap0 = @PKG@.Abil.pos(buf, att);
    if (ap0 != null && !@PKG@.AbilStore.BANNERS.isEmpty()) {
      double bl = 0.0;
      java.util.Iterator it = new java.util.ArrayList(@PKG@.AbilStore.BANNERS.values()).iterator();
      while (it.hasNext()) {
        Object o = it.next();
        if (!(o instanceof @PKG@.AbilZone)) continue;
        @PKG@.AbilZone z = (@PKG@.AbilZone) o;
        if (z.ended || !inZone(z, ap0.x, ap0.y, ap0.z)) continue;
        double x = g(of(z.caster), @C_bannerLeech@);
        if (x > bl) bl = x;
      }
      if (bl > 0.0) leech(buf, att, u, amt * bl / 100.0);
    }
    double[] v = of(u);
    if (v == null) return;
    if (abil) landedAbil(buf, t, att, u, v, what, amt, dead, now);
    else landedWeapon(buf, t, att, u, v, d, amt, now);
    if (dead) killed(buf, t, att, u, v, abil, what, now);
  } catch (Throwable x) { warn("an on-hit effect", x); }
}""")'''

UPFX_JAVA4 = r'''
# ---------------------------------------------------------------- 6. THE PLAYER TICK (AbilTick, the world thread; every 250 ms per player)
M(upfx, r"""
public static void rollStart(@CB@ cb, @REF@ r, java.util.UUID u, double[] v, @VEC@ p, long now) {
  if (p == null) return;
  if (has(v, @C_tripwire@)) {
    Object o = TRAPS.get(u);
    java.util.ArrayList l = o instanceof java.util.ArrayList ? (java.util.ArrayList) o : new java.util.ArrayList();
    while (l.size() >= 3) l.remove(0);
    l.add(new double[] { p.x, p.y, p.z, (double) (now + 6000L), g(v, @C_tripwire@) });
    TRAPS.put(u, l);
  }
}""")
M(upfx, r"""
public static void dodgeStun(@CB@ cb, @REF@ r, java.util.UUID u, double[] v, long now) {
  @VEC@ p = @PKG@.Abil.pos(cb, r);
  if (p == null) return;
  java.util.List l = @PKG@.Abil.near(cb, p.x, p.y, p.z, 1.5);
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@) || !@PKG@.Abil.enemy(cb, (@REF@) o, r)) continue;
    if (!take(uk(u, "dodge" + o.hashCode()), 1, 1000L, now)) continue;
    @PKG@.Abil.stunMob(cb, (@REF@) o, u, g(v, @C_dodgeStun@), now);
    PROCS = PROCS + 1L;
  }
}""")
M(upfx, r"""
public static void traps(@CB@ cb, @REF@ r, java.util.UUID u, @VEC@ p, long now) {
  Object o = TRAPS.get(u);
  if (!(o instanceof java.util.ArrayList)) return;
  java.util.ArrayList l = (java.util.ArrayList) o;
  for (int i = l.size() - 1; i >= 0; i--) {
    double[] t = (double[]) l.get(i);
    if ((double) now >= t[3]) { l.remove(i); continue; }
    @REF@ e = @PKG@.Abil.nearest(cb, r, t[0], t[1], t[2], 1.5, null);
    if (e == null) continue;
    @PKG@.Abil.rootMob(cb, e, u, t[4], now, false, false);
    l.remove(i);
    PROCS = PROCS + 1L;
  }
  if (l.isEmpty()) TRAPS.remove(u);
}""")
M(upfx, r"""
public static void laters(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  Object o = LATER.get(u);
  if (!(o instanceof java.util.ArrayList)) return;
  java.util.ArrayList l = (java.util.ArrayList) o;
  java.util.ArrayList due = takeDue(l, now);
  for (int i = 0; i < due.size(); i++) {
    long[] a = (long[]) due.get(i);
    if (a[0] == 1L) {
      double[] me = @PKG@.Abil.here(cb, r);
      @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
      if (me != null) @PKG@.Abil.smokeAt(cb, u, @PKG@.ClassCfg.pkey(u), aw, me, @PKG@.AbilNum.VA_RADIUS * 0.5, 0, now);
    }
  }
  if (l.isEmpty()) LATER.remove(u);
}""")
# a queued strike of this player (the clone's First Strike follow-up, 0.3 s later)
M(upfx, r"""
public static void queued(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  java.util.Iterator it = QUEUE.keySet().iterator();
  while (it.hasNext()) {
    Object t = it.next();
    Object qo = QUEUE.get(t);
    if (!(qo instanceof Object[]) || !u.equals(((Object[]) qo)[0])) continue;
    Object[] q = (Object[]) qo;
    if (now < ((Long) q[3]).longValue()) continue;
    it.remove();
    if (t instanceof @REF@ && @PKG@.Abil.enemy(cb, (@REF@) t, r)) @PKG@.Abil.hit(cb, (@REF@) t, r, u, ((Double) q[1]).doubleValue(), (String) q[2]);
  }
}""")
# FIX ROUND 2 (critic: the clone burst was an area hit; Skyy 2026-10-08 LOCKED "the assassin trades AOE for insane single target damage"):
# a clone that ends strikes the ONE nearest enemy within rad blocks it can see (1 = struck, 0 = nobody there)
M(upfx, r"""
public static int cloneStrike(@CB@ cb, @REF@ cr, java.util.UUID u, double x, double y, double z, double rad, double amount) {
  if (!(amount > 0.0)) return 0;
  java.util.List l = @PKG@.Abil.near(cb, x, y, z, rad);
  @REF@ best = null;
  double bd = 1.0E9;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @REF@)) continue;
    @REF@ t = (@REF@) o;
    if (!@PKG@.Abil.enemy(cb, t, cr) || !@PKG@.Abil.losOk(cb, x, y + 0.5, z, t)) continue;
    @VEC@ q = @PKG@.Abil.pos(cb, t);
    if (q == null) continue;
    double d = (q.x - x) * (q.x - x) + (q.y - y) * (q.y - y) + (q.z - z) * (q.z - z);
    if (d < bd) { bd = d; best = t; }
  }
  @PKG@.Abil.particle(@PKG@.Abil.FX_HIT, x, y + 0.5, z, cb);
  if (best == null) return 0;
  return @PKG@.Abil.hit(cb, best, cr, u, amount, "UpClone") ? 1 : 0;
}""")
# the Shadow Clones: enemies within cloneLure (6) blocks of a clone lose you; at its end each clone strikes one enemy within 3 blocks
M(upfx, r"""
public static void clones(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  if (!QUEUE.isEmpty()) queued(cb, r, u, now);
  Object o = CLONES.get(u);
  if (!(o instanceof java.util.ArrayList)) return;
  java.util.ArrayList l = (java.util.ArrayList) o;
  for (int i = l.size() - 1; i >= 0; i--) {
    double[] c = (double[]) l.get(i);
    if ((double) now >= c[3]) {
      int n = cloneStrike(cb, r, u, c[0], c[1], c[2], 3.0, c[4]);   // fix round: one enemy, never an area (the Assassin has no AoE)
      CLONEBURSTS = CLONEBURSTS + 1L;
      l.remove(i);
      continue;
    }
    if ((double) now >= c[5]) {
      c[5] = (double) (now + 500L);
      @PKG@.Abil.particle(@PKG@.Abil.FX_SMOKE, c[0], c[1] + 1.0, c[2], cb);
      java.util.List near = @PKG@.Abil.near(cb, c[0], c[1], c[2], @PKG@.AbilNum.UX_CLONER);
      for (int j = 0; j < near.size(); j++) { Object e = near.get(j); if (e instanceof @REF@ && @PKG@.Abil.enemy(cb, (@REF@) e, r)) @PKG@.Abil.distract(cb, (@REF@) e, r); }
    }
  }
  if (l.isEmpty()) CLONES.remove(u);
}""")
# the zone effects a caster spreads each tick: banner move speed, Pilgrim, Sanctified Mana, Arrow Rain's pull (the caster's own zones)
M(upfx, r"""
public static void zones(@CB@ cb, @REF@ r, java.util.UUID u, double[] v, @VEC@ p, long now) {
  boolean bm = has(v, @C_bannerMove@);
  boolean zm = has(v, @C_zoneMove@);
  boolean sm = has(v, @C_sanctMreg@);
  boolean rp = has(v, @C_rainPull@);
  if (!bm && !zm && !sm && !rp) return;
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(r.getStore());
  if (aw == null || aw.nz == 0) return;
  @PKG@.AbilZone[] zs = aw.zoneArr();
  for (int i = 0; i < zs.length; i++) {
    @PKG@.AbilZone z = zs[i];
    if (z == null || z.ended || !u.equals(z.caster)) continue;
    if ((z.kind == 18 && bm) || ((z.kind == 5 || z.kind == 2) && (zm || (sm && z.kind == 5)))) {
      java.util.ArrayList us = new java.util.ArrayList();
      java.util.ArrayList rs = new java.util.ArrayList();
      @PKG@.Abil.gatherAt(r.getStore(), cb, new double[] { z.x, z.y, z.z }, z.r, us, rs);
      for (int j = 0; j < us.size(); j++) {
        java.util.UUID t = (java.util.UUID) us.get(j);
        if (z.kind == 18 && bm) timedPut(MOVEB, t, now + 1500L, g(v, @C_bannerMove@));
        if ((z.kind == 5 || z.kind == 2) && zm) timedPut(MOVEB, t, now + 1500L, g(v, @C_zoneMove@));
        if (z.kind == 5 && sm) timedPut(MREGB, t, now + 1500L, g(v, @C_sanctMreg@));
      }
    }
    if (z.kind == 19 && rp) {
      java.util.List l = @PKG@.Abil.near(cb, z.x, z.y, z.z, z.r);
      for (int j = 0; j < l.size(); j++) {
        Object o = l.get(j);
        if (!(o instanceof @REF@) || !@PKG@.Abil.enemy(cb, (@REF@) o, r)) continue;
        @VEC@ q = @PKG@.Abil.pos(cb, (@REF@) o);
        if (q == null) continue;
        double dx = z.x - q.x;
        double dz = z.z - q.z;
        double d = Math.sqrt(dx * dx + dz * dz);
        if (d > 0.8) @PKG@.Abil.push(cb, (@REF@) o, dx / d * g(v, @C_rainPull@) * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5, 0.0, dz / d * g(v, @C_rainPull@) * @PKG@.AbilCfg.PUSH_PER_BLOCK * 0.5);
      }
    }
  }
}""")
# Rumble: while your Challenge holds, a free Shockwave every 5 s (a shield in hand / off-hand), stun at least 1.5 s
M(upfx, r"""
public static void rumble(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  if (zoneOf(r.getStore(), u, 14) == null) return;
  Object o = RUMBLE.get(u);
  if (o instanceof Long && now < ((Long) o).longValue()) return;
  RUMBLE.put(u, Long.valueOf(now + Math.round(@PKG@.AbilNum.UX_RUMBLE * 1000.0)));
  if (!@PKG@.Abil.shieldIn(cb, r)) return;
  String k = @PKG@.ClassCfg.pkey(u);
  @PKG@.AbilCtx c = @PKG@.Abil.ctxFor(u, k, @PKG@.AbilDefs.SHOCK, 0, @PKG@.Abil.treeCsv(u));
  c.h = @PKG@.Abil.hOf(@PKG@.Abil.hand(cb, r));
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
  double[] me = @PKG@.Abil.here(cb, r);
  if (me == null) return;
  @PKG@.AbilCtx prev = @PKG@.AbilCtx.get();
  @PKG@.AbilCtx.put(c);
  RUMB.set(Boolean.TRUE);
  try { @PKG@.Abil.shockJob(aw, c, u, k, me, @PKG@.Abil.flat(cb, r), 0, c.h, now); }
  finally { RUMB.remove(); @PKG@.AbilCtx.put(prev); }
  CAPS = CAPS + 1L;
}""")
# Aegis Eternal: your Challenge holds while one of its targets lives (30 s at most from its start)
M(upfx, r"""
public static void aegisHold(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  @PKG@.AbilZone z = zoneOf(r.getStore(), u, 14);
  if (z == null || z.hit == null) return;
  long cap = z.start + Math.round(@PKG@.AbilNum.UX_AEGIST * 1000.0);
  if (z.until >= cap) return;
  if (z.until - now < 1500L) {
    long nu = now + 1500L;
    z.until = nu > cap ? cap : nu;
    java.util.Iterator it = z.hit.iterator();
    while (it.hasNext()) {
      Object t = it.next();
      Object co = @PKG@.AbilStore.CHALLS.get(t);
      if (co instanceof long[]) ((long[]) co)[0] = z.until;
    }
  }
}""")
# Crimson Eternal: Blood Frenzy's stacks hold while you hit something every 3 s
M(upfx, r"""
public static void crimson(java.util.UUID u, long now) {
  Object fz = @PKG@.AbilStore.FRENZ.get(u);
  if (!(fz instanceof @PKG@.AbilZone)) return;
  @PKG@.AbilZone z = (@PKG@.AbilZone) fz;
  if (z.ended || z.ring == null) return;
  Object so = @PKG@.AbilStore.SWINGS.get(u);
  if (!(so instanceof Long) || now - ((Long) so).longValue() > 3000L) return;
  long dec = Math.round(@PKG@.AbilNum.BF_DECAY * 1000.0);
  for (int i = 0; i < z.ring.length; i++) if (z.ring[i] > 0L && now - z.ring[i] < dec) z.ring[i] = now;
}""")
# Untouchable: an afterimage each second during Flowing Form (2.5 blocks, 30 % of a hit), 1 Stamina back per enemy hit
M(upfx, r"""
public static void untouch(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  Object fz = @PKG@.AbilStore.FLOWS.get(u);
  if (!(fz instanceof @PKG@.AbilZone)) return;
  @PKG@.AbilZone z = (@PKG@.AbilZone) fz;
  if (z.ended || now >= z.until || z.ai != @PKG@.AbilDefs.FFORM) return;
  Object o = UNTOUCH.get(u);
  if (o instanceof Long && now < ((Long) o).longValue()) return;
  UNTOUCH.put(u, Long.valueOf(now + 1000L));
  double[] me = @PKG@.Abil.here(cb, r);
  if (me == null) return;
  int n = @PKG@.Abil.burst(cb, r, u, me[0], me[1], me[2], 2.5, z.h * @PKG@.AbilNum.CP_IMAGEH / 100.0, "UpImage");
  if (n > 0) stat(cb, r, @DST@.getStamina(), (double) n);
}""")
# Prism Overload: past its normal time the beam drains 4 % of max Mana a second; out of Mana = it ends
M(upfx, r"""
public static void prism(@CB@ cb, @REF@ r, java.util.UUID u, long now) {
  Object jo = @PKG@.AbilStore.CHAN.get(u);
  if (!(jo instanceof @PKG@.AbilJob)) { PRISM.remove(u); return; }
  @PKG@.AbilJob j = (@PKG@.AbilJob) jo;
  long half = j.start + (j.until - j.start) / 2L;
  if (now < half) return;
  Object o = PRISM.get(u);
  long last = o instanceof Long ? ((Long) o).longValue() : now;
  PRISM.put(u, Long.valueOf(now));
  double secs = (double) (now - last) / 1000.0;
  if (!(secs > 0.0)) return;
  @ESM@ m = @PKG@.Abil.map(cb, r);
  double mx = @PKG@.Abil.max(m, @DST@.getMana());
  double cur = @PKG@.Abil.cur(m, @DST@.getMana());
  double want = mx * @PKG@.AbilNum.CP_PRISMD / 100.0 * secs;
  if (!(mx > 0.0) || cur < want) { j.until = now; return; }
  m.subtractStatValue(@DST@.getMana(), (float) want);
}""")

M(upfx, r"""
public static void tick(@REF@ r, @CB@ cb, long now) {
  try {
    if (r == null || !r.isValid()) return;
    Object po = cb.getComponent(r, @PR@.getComponentType());
    if (!(po instanceof @PR@)) return;
    java.util.UUID u = ((@PR@) po).getUuid();
    if (u == null) return;
    Object nx = TICKAT.get(u);
    if (nx instanceof Long && now < ((Long) nx).longValue()) return;
    TICKAT.put(u, Long.valueOf(now + 250L));
    double[] v = of(u);
    if (v == null) {   // no class-tree codes: only the buffs other players give (banner / zone / heal speed, Sanctified Mana)
      movePost(u, timed(MOVEB, u, now) / 100.0);
      mregPost(u, timed(MREGB, u, now));
      return;
    }
    TICKS = TICKS + 1L;
    @VEC@ p = @PKG@.Abil.pos(cb, r);
    double mf = frac(cb, r, @DST@.getMana());
    if (mf >= 0.0) MANAF.put(u, Double.valueOf(mf));
    if (p != null) {
      Object so = STILL.get(u);
      double[] s = null;
      if (so instanceof double[]) s = (double[]) so;
      if (s == null || Math.abs(s[0] - p.x) > 0.3 || Math.abs(s[2] - p.z) > 0.3 || Math.abs(s[1] - p.y) > 0.6) STILL.put(u, new double[] { p.x, p.y, p.z, (double) now });
    }
    boolean roll = @PKG@.Abil.rolling(cb, r);
    Object ro = ROLL.get(u);
    long[] rs = null;
    if (ro instanceof long[]) rs = (long[]) ro;
    if (rs == null) rs = new long[] { 0L, 0L };
    ROLL.put(u, rs);
    if (roll && rs[0] == 0L) { rs[1] = now; rollStart(cb, r, u, v, p, now); }
    if (roll && has(v, @C_dodgeStun@) && now - rs[1] < 700L) dodgeStun(cb, r, u, v, now);
    rs[0] = roll ? 1L : 0L;
    traps(cb, r, u, p, now);
    laters(cb, r, u, now);
    clones(cb, r, u, now);
    Object nv = NOVA.remove(u);
    if (nv instanceof double[]) { double[] n = (double[]) nv; @PKG@.Abil.burst(cb, r, u, n[0], n[1], n[2], 5.0, n[3], "UpNova"); }
    zones(cb, r, u, v, p, now);
    // the move source: Haste / Fleetfoot / Fleet Ranger + while Cloaked + while channelling + the timed buffs (Comet Tail, banner, heals, zones)
    double mv = g(v, @C_move@);
    if (has(v, @C_moveCloak@) && @PKG@.AbilStore.CLOAKS.get(u) instanceof @PKG@.AbilZone && !((@PKG@.AbilZone) @PKG@.AbilStore.CLOAKS.get(u)).ended) mv = mv + g(v, @C_moveCloak@);
    if (has(v, @C_chanMove@) && @PKG@.AbilStore.CHAN.get(u) instanceof @PKG@.AbilJob) mv = mv + g(v, @C_chanMove@);
    mv = mv + timed(MOVEB, u, now);
    Object fy = FURYZ.get(u);   // fix 2: Endless Fury - the toggled spin moves with you at 70 % speed (Capstone numbers furySlow)
    if (fy instanceof @PKG@.AbilZone && !((@PKG@.AbilZone) fy).ended) mv = mv - @PKG@.AbilNum.CP_FURYV;
    movePost(u, mv / 100.0);
    double mr = timed(MREGB, u, now);
    if (has(v, @C_barrierMreg@) && zoneOf(r.getStore(), u, 1) != null) mr = mr + g(v, @C_barrierMreg@);
    mregPost(u, mr);
    if (has(v, @C_xRumble@)) rumble(cb, r, u, now);
    if (has(v, @C_xAegis@)) aegisHold(cb, r, u, now);
    if (has(v, @C_xCrimson@)) crimson(u, now);
    if (has(v, @C_xUntouch@)) untouch(cb, r, u, now);
    if (has(v, @C_xPrism@)) prism(cb, r, u, now);
  } catch (Throwable x) { warn("the player tick", x); }
}""")'''

UPFX_JAVA5 = r'''
# ---------------------------------------------------------------- 7. THE PRIEST / MAGE / BERSERKER HOOKS called from the ability code
# Sacred Heal follows the most hurt party member within 20 blocks (healFollow)
M(upfx, r"""
public static @VEC@ healAt(@ST@ st, @REF@ ref, java.util.UUID u, @VEC@ c) {
  try {
    if (c == null) return c;
    double[] v = of(u);
    if (!has(v, @C_healFollow@)) return c;
    java.util.ArrayList us = new java.util.ArrayList();
    java.util.ArrayList rs = new java.util.ArrayList();
    @PKG@.Abil.gather(st, u, c, 20.0, us, rs);
    double best = 2.0;
    @VEC@ bp = null;
    for (int i = 0; i < us.size(); i++) {
      java.util.UUID t = (java.util.UUID) us.get(i);
      if (!@PKG@.HealTask.inParty(u, t)) continue;
      @REF@ r = (@REF@) rs.get(i);
      double f = frac(st, r, @DST@.getHealth());
      if (f >= 0.0 && f < best && f < 0.99) { best = f; bp = @PKG@.Abil.pos(st, r); }
    }
    double fs = frac(st, ref, @DST@.getHealth());
    if (bp == null || (fs >= 0.0 && fs <= best)) return c;
    return bp;
  } catch (Throwable x) { warn("Sacred Heal's follow", x); return c; }
}""")
# after the heal landed: Chain (reach), Triage, Overheal, Benediction, Miracle, the Sanctuary chain
M(upfx, r"""
public static void healed(@ST@ st, @REF@ ref, java.util.UUID u, java.util.ArrayList us, java.util.ArrayList rs, double[] done, double[] want, @VEC@ c, double rad) {
  try {
    double[] v = of(u);
    if (v == null || c == null) return;
    long now = System.currentTimeMillis();
    double healPct = (double) @PKG@.AbilCfg.S_HEAL;
    for (int i = 0; i < us.size() && i < done.length; i++) {
      java.util.UUID t = (java.util.UUID) us.get(i);
      @REF@ r = (@REF@) rs.get(i);
      if (r == null || !r.isValid() || !@PKG@.Abil.healable(st, r)) continue;
      double f = frac(st, r, @DST@.getHealth());
      double mx = @PKG@.Abil.max(@PKG@.Abil.map(st, r), @DST@.getHealth());
      if (!(mx > 0.0)) continue;
      double before = f - done[i] / mx;
      if (has(v, @C_triage@) && before < 0.4) heal(st, r, g(v, @C_triage@));
      if (has(v, @C_xMiracle@) && before < @PKG@.AbilNum.CP_MIRACLEB / 100.0 && gap(MIRACLE, uk(u, String.valueOf(t)), Math.round(@PKG@.AbilNum.UX_MIRACLE * 1000.0), now)) {
        @PKG@.Abil.apply(st, r, done[i] > 0.0 ? done[i] : mx * healPct / 100.0, mx);
        @PKG@.Abil.cleanse(st, r);
        CAPS = CAPS + 1L;
      }
      if (has(v, @C_overheal@) && f >= 0.999) @PKG@.Abil.wardGive(t, mx * wardPct(u, g(v, @C_overheal@)) / 100.0, now + 5000L);
      if (has(v, @C_healMove@) && done[i] > 0.0) timedPut(MOVEB, t, now + 3000L, g(v, @C_healMove@));
    }
    int reach = ranks(v, @C_healReach@);
    if (reach > 0) {
      java.util.ArrayList fu = new java.util.ArrayList();
      java.util.ArrayList fr = new java.util.ArrayList();
      @PKG@.Abil.gather(st, u, c, 20.0, fu, fr);
      int n = 0;
      for (int i = 0; i < fu.size() && n < reach; i++) {
        if (us.contains(fu.get(i)) || !@PKG@.HealTask.inParty(u, (java.util.UUID) fu.get(i))) continue;
        @REF@ r = (@REF@) fr.get(i);
        if (!@PKG@.Abil.healable(st, r)) continue;
        heal(st, r, healPct * 0.6);
        n++;
      }
    }
    if (has(v, @C_sanctChain@)) {
      @PKG@.AbilZone sz = zoneOf(st, u, 5);
      if (sz != null) {
        boolean in = false;
        for (int i = 0; i < rs.size() && !in; i++) { @VEC@ q = @PKG@.Abil.pos(st, (@REF@) rs.get(i)); if (q != null && inZone(sz, q.x, q.y, q.z)) in = true; }
        if (in) {
          java.util.ArrayList zu = new java.util.ArrayList();
          java.util.ArrayList zr = new java.util.ArrayList();
          @PKG@.Abil.gatherAt(st, st, new double[] { sz.x, sz.y, sz.z }, sz.r, zu, zr);
          for (int i = 0; i < zr.size(); i++) heal(st, (@REF@) zr.get(i), healPct * g(v, @C_sanctChain@) / 100.0);
        }
      }
    }
  } catch (Throwable x) { warn("Sacred Heal's extras", x); }
}""")
# a zone ended (Mana Barrier 1, Shield Bubble 2, Sanctuary 5): Glacial Aegis, Rebound, Hold the Line, the Sanctuary ward
M(upfx, r"""
public static void zoneEnded(@PKG@.AbilZone z, @CAC@ acc) {
  try {
    if (z == null || z.cx == null || z.cx.echo || "left".equals(z.why)) return;
    double[] v = vec(z.cx.tree);
    if (v == null || !(acc instanceof @CB@)) return;
    @CB@ cb = (@CB@) acc;
    @REF@ cr = @PKG@.Abil.casterRef(cb, z.caster);
    if (cr == null || !cr.isValid()) return;
    long now = System.currentTimeMillis();
    boolean broken = "broken".equals(z.why) || "cap".equals(z.why) || "mana".equals(z.why);
    if (z.kind == 1 && has(v, @C_xGlacial@) && broken && gap(GLACIAL, z.caster, Math.round(@PKG@.AbilNum.UX_GLACIAL * 1000.0), now)) {
      @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(cb.getExternalData()));
      double h = z.h > 0.0 ? z.h : @PKG@.AbilCfg.H_FALLBACK;
      @PKG@.AbilJob j = @PKG@.Abil.novaJob(z.caster, z.pkey, new double[] { z.x, z.y, z.z }, @PKG@.AbilCfg.F_RADIUS, h * @PKG@.AbilCfg.F_POWER, @PKG@.AbilCfg.F_FREEZE, @PKG@.AbilCfg.F_BREAK, @PKG@.AbilCfg.F_CHILL, now, 0);
      if (j != null) { j.brkAmt = h * @PKG@.AbilCfg.F_BREAK_P; aw.add(j); CAPS = CAPS + 1L; }
    }
    if (z.kind == 2 && "broken".equals(z.why)) {
      if (has(v, @C_bubbleKb@)) @PKG@.Abil.knockArea(cb, cr, z.x, z.y, z.z, z.r + 1.0, 3.0 * @PKG@.AbilCfg.PUSH_PER_BLOCK);
      if (has(v, @C_bubbleHold@)) {
        java.util.ArrayList us = new java.util.ArrayList();
        java.util.ArrayList rs = new java.util.ArrayList();
        @PKG@.Abil.gatherAt(cr.getStore(), cb, new double[] { z.x, z.y, z.z }, z.r, us, rs);
        for (int i = 0; i < us.size(); i++) timedPut(DRB, us.get(i), now + 3000L, g(v, @C_bubbleHold@));
      }
    }
    if (z.kind == 5 && has(v, @C_sanctWard@)) {
      java.util.ArrayList us = new java.util.ArrayList();
      java.util.ArrayList rs = new java.util.ArrayList();
      @PKG@.Abil.gatherAt(cr.getStore(), cb, new double[] { z.x, z.y, z.z }, z.r, us, rs);
      for (int i = 0; i < us.size(); i++) {
        double mx = @PKG@.Abil.max(@PKG@.Abil.map(cb, (@REF@) rs.get(i)), @DST@.getHealth());
        if (mx > 0.0) @PKG@.Abil.wardGive((java.util.UUID) us.get(i), mx * wardPct(z.caster, g(v, @C_sanctWard@)) / 100.0, now + 5000L);
      }
    }
  } catch (Throwable x) { warn("a zone's end", x); }
}""")
# a Guardian Spirit save: spiritDr (the saved player takes 50 % less for 0.5 s a rank), Undying Vigil (a free bubble + a 30 % shorter wait)
M(upfx, r"""
public static void saved(@CB@ buf, @REF@ r, java.util.UUID u, @PR@ best, @REF@ bestRef, @PKG@.AbilCtx bc, @VEC@ p, long cd, String gk, long now) {
  try {
    if (bc == null || best == null) return;
    double[] v = vec(bc.tree);
    if (v == null) return;
    if (has(v, @C_spiritDr@)) timedPut(DRB, u, now + Math.round(g(v, @C_spiritDr@) * 1000.0), 50.0);
    if (has(v, @C_xVigil@)) {
      Object ro = @PKG@.AbilStore.GUARD.get(gk);
      if (ro instanceof long[]) ((long[]) ro)[1] = now + Math.round((double) cd * (1.0 - @PKG@.AbilNum.CP_VIGIL / 100.0));
      if (p != null) {
        @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(@PKG@.AbilWorld.nameOf(buf.getExternalData()));
        @PKG@.AbilCtx prev = @PKG@.AbilCtx.get();
        @PKG@.AbilCtx.put(bc);
        try { @PKG@.Abil.bubbleAt(best, buf, bestRef, best.getUuid(), bc.pkey, aw, new double[] { p.x, p.y, p.z }, now, @PKG@.AbilCfg.U_AROUND_R, @PKG@.AbilCfg.U_AROUND_HP, 3); }
        finally { @PKG@.AbilCtx.put(prev); }
      }
      CAPS = CAPS + 1L;
    }
  } catch (Throwable x) { warn("a Guardian Spirit save", x); }
}""")
# Meteor's impact: Knockback outward (the code a.Meteor.kb)
M(upfx, r"""
public static void impact(@PKG@.AbilJob j, @CB@ cb, @REF@ cr, int n) {
  try {
    if (j == null || j.cx == null || cr == null || n <= 0) return;
    double kb = ap(vec(j.cx.tree), @PKG@.AbilDefs.METEOR, 7);
    if (kb > 0.0) @PKG@.Abil.knockArea(cb, cr, j.x, j.y, j.z, j.r + 0.5, kb * @PKG@.AbilCfg.PUSH_PER_BLOCK);
  } catch (Throwable x) { warn("Meteor's knockback", x); }
}""")
# Warlord's Domain: the banner follows its Berserker at 60 % and never falls (re-armed while held); Endless Fury: Stamina back per pulse
M(upfx, r"""
public static void bannerUp(@PKG@.AbilZone z, @PKG@.AbilCtx c) {
  if (z == null || c == null || !has(vec(c.tree), @C_xDomain@)) return;
  z.follow = true;
  z.pct = z.pct * @PKG@.AbilNum.CP_DOMAIN / 100.0;
  z.n2 = 41;
  long far = z.start + 3600000L;
  z.until = far;
  z.t1 = far;
}""")
M(upfx, r"""
public static boolean domain(@PKG@.AbilZone z) {
  return z != null && z.n2 == 41;
}""")
# FIX ROUND 2 (critic: Endless Fury had become "x2 time"; the spec: "Whirlwind becomes a holdable toggle that moves with you at 70% speed;
# each full spin refunds 5 stamina"): the spin runs until you cast it again (furyOff), run out of Mana / Stamina, or furyMax s pass; it drains
# furyMana + furyStamina a second (paid every pulse), every full spin (1 s) that hit an enemy gives furyBack Stamina back; the cooldown starts
# when it ends (furyEnd - the Blood Frenzy rule). Numbers: Server Setup -> Classes -> Ability numbers "Capstone numbers".
M(upfx, r"""
public static boolean furyOn(@PKG@.AbilCtx c) {
  return c != null && !c.echo && c.ai == @PKG@.AbilDefs.WHIRL && has(vec(c.tree), @C_xFury@);
}""")
M(upfx, r"""
public static void furyUp(@PKG@.AbilZone z, @PKG@.AbilCtx c, long now) {
  if (z == null || z.caster == null || !furyOn(c)) return;
  z.until = now + Math.round(@PKG@.AbilNum.CP_FURYT * 1000.0);
  FURYZ.put(z.caster, z);
  FURYN.put(z.caster, new long[] { now + 1000L, 0L });
  CAPS = CAPS + 1L;
  @PR@ pr = @PKG@.Abil.prOf(z.caster);
  if (pr != null) @PKG@.Abil.say(pr, "Endless Fury: the spin holds until you cast Whirlwind again (" + @PKG@.AbilMath.secs(Math.round(@PKG@.AbilNum.CP_FURYT * 1000.0)) + " s at most) - you move at " + Math.round(100.0 - @PKG@.AbilNum.CP_FURYV) + " % speed.");
}""")
M(upfx, r"""
public static String furyOff(@PR@ pr, java.util.UUID u, String k, long now) {
  if (u == null) return null;
  Object o = FURYZ.get(u);
  if (!(o instanceof @PKG@.AbilZone)) return null;
  @PKG@.AbilZone z = (@PKG@.AbilZone) o;
  if (z.ended || now >= z.until) return null;
  z.ended = true;
  z.why = "off";
  FURYZ.remove(u);
  long cd = @PKG@.Abil.cdCx(z.cx, @PKG@.AbilDefs.WHIRL, z.shape);
  @PKG@.AbilStore.arm(k, @PKG@.AbilDefs.IDS[@PKG@.AbilDefs.WHIRL], now, cd);
  if (pr != null) @PKG@.Abil.say(pr, "Endless Fury off - Whirlwind is ready again in " + @PKG@.AbilMath.secs(cd) + " s.");
  return "ok:Whirlwind off cd=" + cd;
}""")
M(upfx, r"""
public static String furyEnd(@PKG@.AbilZone z, long now) {
  if (z == null || z.caster == null) return "none";
  boolean mine = FURYZ.get(z.caster) == z;
  if (mine) FURYZ.remove(z.caster);
  else if (!"quit".equals(z.why)) return "none";   // not a toggled spin (or furyOff armed it already)
  FURYN.remove(z.caster);
  if ("off".equals(z.why) || "replaced".equals(z.why) || z.pkey == null) return "none";
  long cd = @PKG@.Abil.cdCx(z.cx, @PKG@.AbilDefs.WHIRL, z.shape);
  @PKG@.AbilStore.arm(z.pkey, @PKG@.AbilDefs.IDS[@PKG@.AbilDefs.WHIRL], now, cd);
  @PR@ pr = @PKG@.Abil.prOf(z.caster);
  if (pr != null) @PKG@.Abil.say(pr, "Endless Fury ended" + ("mana".equals(z.why) ? " (out of Mana)" : ("stamina".equals(z.why) ? " (out of Stamina)" : "")) + " - Whirlwind is ready again in " + @PKG@.AbilMath.secs(cd) + " s.");
  return "armed";
}""")
M(upfx, r"""
public static void spinPulse(@PKG@.AbilZone z, @CB@ cb, @REF@ cr, int n) {
  if (z == null || z.cx == null || cr == null || z.ended || z.caster == null || FURYZ.get(z.caster) != z) return;   // only the toggled Endless Fury spin
  long now = System.currentTimeMillis();
  Object so = FURYN.get(z.caster);
  long[] s = null;
  if (so instanceof long[]) s = (long[]) so;
  if (s == null) { s = new long[] { now + 1000L, 0L }; FURYN.put(z.caster, s); }
  if (n > 0) s[1] = 1L;
  if (!(@PKG@.AbilCfg.CREATIVE_FREE && @PKG@.Abil.creative(cb, cr))) {
    double sec = z.d1 > 0.0 ? z.d1 : 0.5;
    double cm = @PKG@.AbilNum.CP_FURYM * sec;
    double cs = @PKG@.AbilNum.CP_FURYS * sec;
    @ESM@ m = @PKG@.Abil.map(cb, cr);
    double mana = @PKG@.Abil.cur(m, @DST@.getMana());
    double stam = @PKG@.Abil.cur(m, @DST@.getStamina());
    if (mana >= 0.0 && cm > 0.0 && mana < cm) { z.ended = true; z.why = "mana"; return; }
    if (stam >= 0.0 && cs > 0.0 && stam < cs) { z.ended = true; z.why = "stamina"; return; }
    if (m != null && mana >= 0.0 && cm > 0.0) m.subtractStatValue(@DST@.getMana(), (float) cm);
    if (m != null && stam >= 0.0 && cs > 0.0) m.subtractStatValue(@DST@.getStamina(), (float) cs);
  }
  if (now >= s[0]) {
    if (s[1] > 0L) stat(cb, cr, @DST@.getStamina(), @PKG@.AbilNum.CP_FURYB);
    s[0] = now + 1000L;
    s[1] = 0L;
  }
}""")
# FIX ROUND 2 (critic: Spider's Den / Holy Land had become a cooldown cut / +50 %; the spec: "Hunter's Net gains 2 charges", "you can keep 2
# Sanctuaries active"): a SPARE CHARGE - a cast while the ability is on cooldown spends the spare instead (castAt0), the main cooldown keeps
# running, the spare comes back one full cooldown later. CHG: u -> long[] { Net spare ready at, Sanctuary spare ready at }.
M(upfx, r"""
public static int spareSlot(int ai, double[] v) {
  if (ai == @PKG@.AbilDefs.NET && has(v, @C_xSpider@)) return 0;
  if (ai == @PKG@.AbilDefs.SANCT && has(v, @C_xHolyLand@)) return 1;
  return -1;
}""")
M(upfx, r"""
public static boolean spare(java.util.UUID u, int ai, String csv, long now) {
  if (u == null) return false;
  int sl = spareSlot(ai, vec(csv));
  if (sl < 0) return false;
  Object o = CHG.get(u);
  return !(o instanceof long[]) || now >= ((long[]) o)[sl];
}""")
M(upfx, r"""
public static long spareUse(java.util.UUID u, int ai, long now, long cd) {
  int sl = ai == @PKG@.AbilDefs.NET ? 0 : (ai == @PKG@.AbilDefs.SANCT ? 1 : -1);
  if (u == null || sl < 0) return 0L;
  Object o = CHG.get(u);
  long[] c = null;
  if (o instanceof long[]) c = (long[]) o;
  if (c == null) c = new long[] { 0L, 0L };
  c[sl] = now + (cd > 0L ? cd : 0L);
  CHG.put(u, c);
  CAPS = CAPS + 1L;
  @PR@ pr = @PKG@.Abil.prOf(u);
  if (pr != null) @PKG@.Abil.say(pr, (sl == 0 ? "Spider's Den" : "Holy Land") + ": your second charge - it is back in " + @PKG@.AbilMath.secs(cd) + " s.");
  return c[sl];
}""")
# Holy Land: where two of your Sanctuaries overlap, the younger one heals (holyOverlap - 100) % of its pulse (150 % together by default)
M(upfx, r"""
public static double overlap(@PKG@.AbilZone z, @ST@ st, @VEC@ q) {
  try {
    if (z == null || q == null || z.cx == null || z.caster == null || !has(vec(z.cx.tree), @C_xHolyLand@)) return 1.0;
    @PKG@.AbilWorld aw = @PKG@.AbilWorld.at(st);
    if (aw == null) return 1.0;
    long now = System.currentTimeMillis();
    @PKG@.AbilZone[] zs = aw.zoneArr();
    for (int i = 0; i < zs.length; i++) {
      @PKG@.AbilZone o = zs[i];
      if (o == null || o == z || o.kind != 5 || o.ended || now >= o.until || !z.caster.equals(o.caster)) continue;
      if (!@PKG@.AbilMath.inRange(q.x - o.x, q.y - o.y, q.z - o.z, o.r)) continue;
      if (o.start < z.start || (o.start == z.start && System.identityHashCode(o) < System.identityHashCode(z))) {
        double f = (@PKG@.AbilNum.CP_HOLYO - 100.0) / 100.0;
        return f < 0.0 ? 0.0 : f;
      }
    }
  } catch (Throwable x) { warn("Holy Land's overlap", x); }
  return 1.0;
}""")
M(upfx, r"""
public static void rooted(@REF@ t, long until) {
  if (t == null) return;
  timedPut(RT, t, until, 1.0);
}""")
'''

UPFX_STATE.append("QUEUE")
