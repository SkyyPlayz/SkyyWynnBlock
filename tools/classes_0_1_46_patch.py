"""Derive SkyyClasses/build_skyyclasses_0.1.46.py from the GENERATED SkyyClasses 0.1.45 (build_skyyclasses_0.1.45.py = the tools/deploy_set.py
SET pin; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... -> classes_0_1_45_patch.py -> 0.1.45).
Never re-run an older patch, never edit a generated script - edit this patch. Every anchor is asserted once; at the end every change is
undone on a copy and compared with 0.1.45 (tools/soundpass_gen.Patch). Line endings kept.
Run:  python tools/classes_0_1_46_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.46.py   (never --deploy)
      then  python SkyyClasses/test_skyyclasses_0.1.46.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyelem as EL

NOTE = '''0.1.46 (2026-10-22) = WYNN ELEMENTS, the SkyyClasses part (research/Wynn-Elements-Build-Spec.md 4.3; FULL round elem1 with SkyyMobs
  0.1.17, SkyyGear 0.3.39, SkyyPets 0.4.10, SkyyAccessories 0.5.32, SkyyMenu 0.3.45 - pin + roll back TOGETHER). Skyy (docs/answered/
  classes.md 2026-10-17): "Lightning -> Thunder, Wind -> Air" (Wynn names everywhere) + gear.md 2026-10-18 Q8 "yes do poison. (do it like
  wynncraft where you get like 50/10 ... procs every second (poison damage doesnt stagger ...) but you can also get poison on your combat armor
  and it all stacks".
  1. WYNN NAMES: ELN = Fire, Water, Earth, Thunder, Air, Poison (index order unchanged); elemIdx reads the saved "Lightning" / "Wind" as
     Thunder / Air (a saved att1 / att2 / bub.el keeps working, the next attune writes the new word; 0.1.45 already reads Thunder / Air);
     every text says Thunder / Air (the attune refusal list too). classes:fn:imbue answers "Thunder;30" for an old "Lightning" file.
  2. classes:fn:imbue also takes Object[]{ UUID, String weaponItemId }: null unless that weapon is a Spellblade weapon the player may use
     (sbWeapon) - SkyyGear 0.3.39 adds the Imbue part to its element split only for those hits (then publishes gear:imbue:v2 = TRUE and our own
     x(1 + Imbue %) stops: no double count; outHit3 unchanged).
  3. NEW BRIDGE classes:fn:dot apply(Object[]{ UUID attacker, UUID victim, String what, String causeId, Double perSec, Double secs, Integer
     stacks, String world }) -> Boolean (TRUE = queued). SkyyGear's Poison line (what "GearPoison", cause "Poison"): ONE DoT engine (dotOn /
     dotTick, ticks every second, stacks like Burn - past the cap the oldest one is refreshed; "GearPoison" stacks apart from the Assassin's
     "ElemPoison"). Validated (what 1-32 characters, a known cause Poison / Fire / Lightning / Water / Earth / Wind, perSec 0-1e6, secs 1-600,
     stacks 1-20, abilities on, the world's job list not full); a job (kind 28) runs it on the world thread: the victim's Ref from its UUID
     (EntityStore.getRefFromUUID), then dotOn. FALSE for bad args / abilities off / a full job list. Any thread, never throws.
  4. TICK CAUSES: hit() gives a status / DoT hit the element's engine DamageCause asset (ElemBurn Fire, ElemShock Lightning, ElemPoison +
     GearPoison Poison; a classes:fn:dot caller's own cause) instead of PROJECTILE - looked up once in DamageCause.getAssetMap(), missing =
     PROJECTILE + one WARN. So SkyyGear's family() = 0 (a tick is never a weapon hit: no weapon lines, no Imbue part on it), SkyyGear's armour
     pass applies Thorium's Poison resistance on a player victim, and the death message is the element's. Direct ability hits keep
     PROJECTILE. Poison ticks show the toxin puff (no vanilla effect: probe P4 untested), no knockback (a plain Damage, no stagger).
  5. ELEMENT AFFINITY ON OUR OWN ELEMENT DAMAGE: Burn ticks + the Shock jump + Frost Nova (Water) + Meteor (Fire) hitting an NPC x (1 +
     mob:fn:elem {role, element} / 100) when SkyyMobs 0.1.17 runs (Weak +25 / Resist -25 / boss own -50 at the defaults; no SkyyMobs = x1).
     Gust boss immunity + the cc halving unchanged; the mob table never makes anything immune.
  6. Ready line: + classes:fn:dot (setup runs before the asset packs load - Abil.causesText, for /classadmin-style checks and the harness,
     counts the tick causes found).
  SAVED DATA: none new (saved words read through the aliases). No new command / system; one new class DotFn.
  ROLLBACK to 0.1.45: safe for saved data (it reads Thunder / Air); with SkyyGear 0.3.39 still in place its Poison line does nothing
  (no classes:fn:dot) and Gear finds no array-form answer, so only our own x(1 + Imbue %) runs (0.1.45 never reads gear:imbue:v2) - still roll back with the elem1 set.
'''

P = G.Patch(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.45.py"), os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.46.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.45"') and P.has("UpSk") and not P.has("DotFn"), "not the generated SkyyClasses 0.1.45 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyyClasses 0.1.45 - build script (javassist via jpype). GENERATED by tools/classes_0_1_45_patch.py from the generated 0.1.44 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_45_patch.py) - edit the patch, not this file.
''', '''"""SkyyClasses 0.1.46 - build script (javassist via jpype). GENERATED by tools/classes_0_1_46_patch.py from the generated 0.1.45 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> ... -> classes_0_1_46_patch.py) - edit the patch, not this file.
''' + NOTE + '''0.1.45 (the base, everything below is still true unless 0.1.46 above says otherwise):
''')
P.rep('VERSION = "0.1.45"', 'VERSION = "0.1.46"')

# ---------- 1. Wynn names
P.rep('''           "public static final String[] ELN = new String[] { \\"Fire\\", \\"Water\\", \\"Earth\\", \\"Lightning\\", \\"Wind\\", \\"Poison\\" };",''',
      '''           "public static final String[] ELN = new String[] { \\"Fire\\", \\"Water\\", \\"Earth\\", \\"Thunder\\", \\"Air\\", \\"Poison\\" };",          # 0.1.46: Wynn names''')
P.rep('''  for (int i = 0; i < ELN.length; i++) if (ELN[i].equalsIgnoreCase(t)) return i;
  if ("Thunder".equalsIgnoreCase(t)) return 3;
  if ("Air".equalsIgnoreCase(t)) return 4;
  return -1;''', '''  for (int i = 0; i < ELN.length; i++) if (ELN[i].equalsIgnoreCase(t)) return i;
  if ("Lightning".equalsIgnoreCase(t)) return 3;          // 0.1.46: the old saved words
  if ("Wind".equalsIgnoreCase(t)) return 4;
  return -1;''')
P.rep('''  if (e < 0 || e > 4) return "-Elements: Fire, Water, Earth, Lightning, Wind.";''', '''  if (e < 0 || e > 4) return "-Elements: Fire, Water, Earth, Thunder, Air.";          // 0.1.46''')
assert "Lightning" not in P.s.split("ELN = new String[]")[1].split("\n")[0]

# ---------- 2. classes:fn:imbue {UUID, weapon id}
P.rep('''    java.util.UUID u = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof String) u = java.util.UUID.fromString(((String) o).trim());
    if (u == null) return null;
    if (@PKG@.ClassStore.classIndex(u) != @PKG@.Abil.sbCi()) return null;   // FIX 2 (critic): a pending Imbue never follows a switch to another class''',
      '''    java.util.UUID u = null;
    String item = null;
    boolean withItem = false;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof String) u = java.util.UUID.fromString(((String) o).trim());
    else if (o instanceof Object[] && ((Object[]) o).length >= 2 && ((Object[]) o)[0] instanceof java.util.UUID) {          // 0.1.46: { UUID, weapon id }
      u = (java.util.UUID) ((Object[]) o)[0];
      item = ((Object[]) o)[1] instanceof String ? (String) ((Object[]) o)[1] : null;
      withItem = true;
    }
    if (u == null) return null;
    if (@PKG@.ClassStore.classIndex(u) != @PKG@.Abil.sbCi()) return null;   // FIX 2 (critic): a pending Imbue never follows a switch to another class
    if (withItem && !@PKG@.Abil.sbWeapon(u, item)) return null;          // 0.1.46: only a Spellblade weapon the player may use''')

# ---------- 3 + 4 + 5: the late methods (stubs first, bodies at the end: free order)
P.rep('''for _src in ABIL_LATE:
    M(abil, _late_stub(_src))''', '''# 0.1.46 (elem1): classes:fn:dot's job (kind 28), the tick causes, the element affinity of our own element damage
for _f in ("public static final java.util.concurrent.ConcurrentHashMap CAUSES = new java.util.concurrent.ConcurrentHashMap();",          # cause id -> DamageCause
           "public static final java.util.concurrent.ConcurrentHashMap WHATCAUSE = new java.util.concurrent.ConcurrentHashMap();",       # what -> cause id (classes:fn:dot callers)
           "public static volatile long DOTS_IN = 0L;", "public static volatile long DOTS_RUN = 0L;", "public static volatile long AFFIN = 0L;"):
    F(abil, _f)
DOT_CAUSES = ["Poison", "Fire", "Lightning", "Water", "Earth", "Wind"]
import skyyelem as EL          # tools/skyyelem.py: the one element table
assert sorted(DOT_CAUSES) == sorted(set(EL.CAUSE.values())), "0.1.46: the classes:fn:dot causes = tools/skyyelem.py CAUSE"
ABIL_LATE += [
r"""
public static String causeId(String what) {
  if (what == null) return null;
  if ("ElemBurn".equals(what)) return "Fire";
  if ("ElemShock".equals(what)) return "Lightning";
  if ("ElemPoison".equals(what)) return "Poison";
  Object c = WHATCAUSE.get(what);
  return c instanceof String ? (String) c : null;
}
""",
r"""
public static @DCS@ causeOf(String id) {
  if (id == null) return @DCS@.PROJECTILE;
  Object o = CAUSES.get(id);
  if (o instanceof @DCS@) return (@DCS@) o;
  if (o != null) return @DCS@.PROJECTILE;
  Object a = null;
  try { a = @DCS@.getAssetMap().getAsset(id); } catch (Throwable t) { a = null; }
  if (a instanceof @DCS@) { CAUSES.put(id, a); return (@DCS@) a; }
  CAUSES.put(id, Boolean.FALSE);
  @PKG@.ClassCfg.warn("the DamageCause asset " + id + " is not loaded - its element / poison ticks use PROJECTILE (they may count as weapon hits in SkyyGear)");
  return @DCS@.PROJECTILE;
}
""",
r"""
public static String causesText() {
  StringBuilder sb = new StringBuilder();
  String[] ids = new String[] { @CAUSEIDS@ };
  int ok = 0;
  for (int i = 0; i < ids.length; i++) {
    Object a = null;
    try { a = @DCS@.getAssetMap().getAsset(ids[i]); } catch (Throwable t) { a = null; }
    if (a instanceof @DCS@) ok++;
    else { if (sb.length() > 0) sb.append(','); sb.append(ids[i]); }
  }
  return ok + " / " + ids.length + " tick causes found" + (sb.length() > 0 ? " (missing " + sb.toString() + ")" : "");
}
""".replace("@CAUSEIDS@", ", ".join('"%s"' % _c for _c in DOT_CAUSES)),
r"""
public static String elemOfWhat(String what) {
  if (what == null) return null;
  if ("ElemBurn".equals(what) || "Meteor".equals(what)) return "Fire";
  if ("ElemShock".equals(what)) return "Thunder";
  if ("FrostNova".equals(what)) return "Water";
  return null;
}
""",
r"""
public static double affinity(String role, String elem) {
  if (role == null || elem == null) return 1.0;
  try {
    Object f = @PKG@.ClassCfg.bridge().get("mob:fn:elem");
    if (!(f instanceof java.util.function.Function)) return 1.0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { role, elem });
    if (!(r instanceof Number)) return 1.0;
    double m = 1.0 + ((Number) r).doubleValue() / 100.0;
    if (m < 0.0) m = 0.0;
    if (m != 1.0) AFFIN = AFFIN + 1L;
    return m;
  } catch (Throwable t) { return 1.0; }
}
""",
r"""
public static boolean dotWant(java.util.UUID att, java.util.UUID vic, String what, String cause, double perSec, double secs, int stacks, String world) {
  if (att == null || vic == null || what == null || world == null || !@PKG@.AbilCfg.PART) return false;
  if (what.length() == 0 || what.length() > 32 || what.startsWith("Elem")) return false;
  boolean known = false;
  String[] ids = new String[] { @CAUSEIDS@ };
  for (int i = 0; i < ids.length; i++) if (ids[i].equals(cause)) known = true;
  if (!known) return false;
  if (!(perSec > 0.0) || perSec > 1000000.0 || !(secs >= 1.0) || secs > 600.0 || stacks < 1 || stacks > 20) return false;
  @PKG@.AbilWorld aw = @PKG@.AbilWorld.of(world);
  if (aw.dotFull()) return false;          // elem1fix2: DoT jobs have their own cap (never block class casts)
  WHATCAUSE.put(what, cause);
  @PKG@.AbilJob j = new @PKG@.AbilJob(28, System.currentTimeMillis(), att, what, 0.0, 0.0, 0.0, 0.0, perSec);
  j.pkey = @PKG@.ClassCfg.pkey(att);
  j.ai = @PKG@.AbilDefs.IMBUE;
  j.tref = vic;
  j.secs = secs;
  j.len = (double) stacks;
  aw.add(j);
  DOTS_IN = DOTS_IN + 1L;
  return true;
}
""".replace("@CAUSEIDS@", ", ".join('"%s"' % _c for _c in DOT_CAUSES)),
r"""
public static boolean dotRun(@PKG@.AbilJob j, @ST@ st, @CB@ cb, long now) {
  if (!(j.tref instanceof java.util.UUID)) return false;
  @REF@ t = null;
  try { t = ((@ES@) cb.getExternalData()).getRefFromUUID((java.util.UUID) j.tref); } catch (Throwable x) { t = null; }
  if (t == null || !t.isValid()) return false;
  dotOn(cb, t, j.caster, j.what, j.amount, j.secs, (int) Math.round(j.len), now);
  DOTS_RUN = DOTS_RUN + 1L;
  return false;
}
""",
]
for _src in ABIL_LATE:
    M(abil, _late_stub(_src))''')
P.rep('''  if (j.kind == 26) return dotTick(j, st, cb, now);''', '''  if (j.kind == 26) return dotTick(j, st, cb, now);
  if (j.kind == 28) return dotRun(j, st, cb, now);   // 0.1.46: classes:fn:dot (SkyyGear's Poison line)''')
P.rep('''  if (q != null) particle("ElemPoison".equals(j.what) ? FX_TOXIN : FX_FIRE, q.x, q.y + 1.0, q.z, cb);''',
      '''  if (q != null) particle(j.what != null && j.what.endsWith("Poison") ? FX_TOXIN : FX_FIRE, q.x, q.y + 1.0, q.z, cb);          // 0.1.46: + GearPoison''')
P.rep('''    @DCS@ cause = @DCS@.PROJECTILE;
    if (cause == null) return false;
    double amt0 = amount * outMult(buf, t, cu, System.currentTimeMillis()) * upOut(buf, t, cu, what);   // 0.1.24: Enrage / Frenzy / banner / Mark ... on ability hits too; 0.1.43: + the class tree''',
      '''    String cid = causeId(what);          // 0.1.46: a status / DoT tick takes its element's engine cause (never a weapon hit in SkyyGear)
    @DCS@ cause = cid == null ? @DCS@.PROJECTILE : causeOf(cid);
    if (cause == null) return false;
    double amt0 = amount * outMult(buf, t, cu, System.currentTimeMillis()) * upOut(buf, t, cu, what);   // 0.1.24: Enrage / Frenzy / banner / Mark ... on ability hits too; 0.1.43: + the class tree
    String el = elemOfWhat(what);          // 0.1.46: our own element damage x the mob's affinity (SkyyMobs mob:fn:elem)
    if (el != null) {
      Object no = buf.getComponent(t, @NPC@.getComponentType());
      if (no instanceof @NPC@) amt0 = amt0 * affinity(((@NPC@) no).getRoleName(), el);
    }''')

# elem1fix2 (critic: common Poison stacks filled abil.maxLive and refused every class cast in the world): full() - the cast gate - counts
# only non-DoT jobs (kinds 26 tick / 28 queued classes:fn:dot are left out); dotFull() caps those on their own at 8 x abil.maxLive
P.rep('''M(abworld, "public synchronized boolean full() { prune(System.currentTimeMillis()); return (long) (this.jobs.size() + this.zones.size()) >= @PKG@.AbilCfg.MAX_LIVE; }")''',
      '''M(abworld, r"""
public synchronized int dots() {
  int n = 0;
  for (int i = 0; i < this.jobs.size(); i++) {
    @PKG@.AbilJob j = (@PKG@.AbilJob) this.jobs.get(i);
    if (j.kind == 26 || j.kind == 28) n++;
  }
  return n;
}""")   # 0.1.46 (elem1fix2): the DoT jobs (Burn / Shock / Poison ticks + queued classes:fn:dot)
M(abworld, "public synchronized boolean full() { prune(System.currentTimeMillis()); return (long) (this.jobs.size() - dots() + this.zones.size()) >= @PKG@.AbilCfg.MAX_LIVE; }")   # FIX ROUND: row abil.maxLive; 0.1.17: + zones; 0.1.46: DoT jobs left out
M(abworld, "public synchronized boolean dotFull() { prune(System.currentTimeMillis()); return (long) dots() >= 8L * (long) @PKG@.AbilCfg.MAX_LIVE; }")   # 0.1.46: the DoT cap (8 x abil.maxLive)''')
# elem1fix2 (critic: Gear 0.3.39 publishing the OLD key gear:imbue switched off Classes <= 0.1.45's own Imbue x while those cannot answer the
# array-form classes:fn:imbue = Imbue did nothing in a partial deploy / rollback): the hand-over key is gear:imbue:v2, read only from 0.1.46 on
P.rep('''    if (imb != null && !Boolean.TRUE.equals(@PKG@.ClassCfg.bridge().get("gear:imbue"))) {''',
      '''    if (imb != null && !Boolean.TRUE.equals(@PKG@.ClassCfg.bridge().get("gear:imbue:v2"))) {          // 0.1.46 (elem1fix2): the new key - SkyyGear 0.3.39+ only''')
# ---------- the DotFn class + the bridge
P.rep('''abimb = pool.makeClass(PKG + ".ImbueFn")
abimb.addInterface(pool.get("java.util.function.Function"))
C(abimb, "public ImbueFn() { }")''', '''abimb = pool.makeClass(PKG + ".ImbueFn")
abimb.addInterface(pool.get("java.util.function.Function"))
C(abimb, "public ImbueFn() { }")
# 0.1.46 (elem1): classes:fn:dot (SkyyGear's Poison line through the ONE DoT engine; see the header)
abdot = pool.makeClass(PKG + ".DotFn")
abdot.addInterface(pool.get("java.util.function.Function"))
C(abdot, "public DotFn() { }")
M(abdot, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 8 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof java.util.UUID) || !(a[2] instanceof String) || !(a[3] instanceof String)
        || !(a[4] instanceof Number) || !(a[5] instanceof Number) || !(a[6] instanceof Number) || !(a[7] instanceof String)) return Boolean.FALSE;
    double ps = ((Number) a[4]).doubleValue();
    double sc = ((Number) a[5]).doubleValue();
    if (Double.isNaN(ps) || Double.isInfinite(ps) || Double.isNaN(sc) || Double.isInfinite(sc)) return Boolean.FALSE;
    return Boolean.valueOf(@PKG@.Abil.dotWant((java.util.UUID) a[0], (java.util.UUID) a[1], (String) a[2], (String) a[3], ps, sc, ((Number) a[6]).intValue(), (String) a[7]));
  } catch (Throwable t) { return Boolean.FALSE; }
}""")''')
P.rep('''  b.put("classes:fn:imbue", new @PKG@.ImbueFn());            // 0.1.25: the Spellblade's Imbue element (SkyyGear's element split, later)''',
      '''  b.put("classes:fn:imbue", new @PKG@.ImbueFn());            // 0.1.25: the Spellblade's Imbue element (SkyyGear's element split, later)
  b.put("classes:fn:dot", new @PKG@.DotFn());                // 0.1.46 (elem1): SkyyGear's Poison line through the one DoT engine''')
P.rep('''  try { @PKG@.ClassCfg.bridge().remove("classes:fn:imbue"); } catch (Throwable t) { }       // 0.1.25''',
      '''  try { @PKG@.ClassCfg.bridge().remove("classes:fn:imbue"); } catch (Throwable t) { }       // 0.1.25
  try { @PKG@.ClassCfg.bridge().remove("classes:fn:dot"); } catch (Throwable t) { }         // 0.1.46''')
P.rep('''rebirth participant rebirth:part:classes (+ rebirth modifier slots), classes:fn:imbue; bridge''',
      '''rebirth participant rebirth:part:classes (+ rebirth modifier slots), classes:fn:imbue, classes:fn:dot (status / DoT ticks on their element's DamageCause); bridge''')
P.rep('''          abimb,                         # 0.1.25: + classes:fn:imbue''', '''          abimb,                         # 0.1.25: + classes:fn:imbue
          abdot,                         # 0.1.46: + classes:fn:dot''')
P.rep('''             (T["SNU"], "playSoundEvent2dToPlayer"), (T["SEV"], "getAssetMap"), (T["SCAT"], "SFX"), (T["NPC"], "getRoleName")):   # + FIX ROUND
    B.probe(pool, c, m)''', '''             (T["SNU"], "playSoundEvent2dToPlayer"), (T["SEV"], "getAssetMap"), (T["SCAT"], "SFX"), (T["NPC"], "getRoleName")):   # + FIX ROUND
    B.probe(pool, c, m)
B.probe(pool, T["DCS"], "getAssetMap")          # 0.1.46: the tick causes by id''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0 + 1, "0.1.46 adds DotFn only"
P.finish()
