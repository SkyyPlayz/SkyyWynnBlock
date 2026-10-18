"""Derive SkyyMobs/build_skyymobs_0.1.10.py from the GENERATED 0.1.9 (build_skyymobs_0.1.9.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_9_patch.py). Every anchor is asserted; line endings are kept.
Run:  python tools/mobs_0_1_10_patch.py [--out <path>]   then   python SkyyMobs/build_skyymobs_0.1.10.py   then
      python SkyyMobs/test_skyymobs_0.1.10.py      (never --deploy; --static = the text checks only, no jars needed)
Edit THIS file, never the generated script. --out writes the result somewhere else (the harness's determinism check).

0.1.10 (2026-10-17) = WHO IS A BOSS, WHICH ZONE, WHO HURT IT (the SkyyMobs part of the "pack armor + weapons as mob drops" round; SkyyGear
0.3.19 rolls a Mythic mystery bag per credited player when a BOSS dies, for that boss's ZONE). Skyy 2026-10-17 (docs/answered/gear.md
"PACK ARMOR AS MOB DROPS"): "lets build the arcane robes and armory into the mod so you drop from enemy's with our modifiers next. ...
we need to pick some to make UT items for each tier, and mythic mob drops." + popup "UT SCOPE": "good catch! UT and mythic per zone! not
tier. always make the UT and mythic the highest tier of that zone" (5 zones: Zone 5 = the dinosaur caves Lv 60-75). LOCKED 2026-10-08
(popup batch 2): "Mythic boss-only (out of random drops + Smithing step-up), 10% per kill (20% Challenge) per participant with 15% credit
+ own-class lean x3". Zone bands LOCKED 2026-10-01 (docs/answered/mobs.md): Zone 1 = Lv 1-20, Zone 2 = 20-30, Zone 3 = 30-45, Zone 4 =
45-60; R8 (docs/answered/world.md): Zone 5 = Lv 60-75. SkyyMobs owns "who is a boss", "which zone" and "who hurt it", so it answers:
  1. NEW BRIDGE mob:fn:boss (java.util.function.Function, put in setup next to mob:fn:setLevel, removed in shutdown):
       apply(Object[] { String worldName, java.util.UUID npc (may be null), String roleId, Number x, Number y, Number z })
       -> Object[] { Integer zone, String role, String[] players, double[] shares }
     null = the role is not a boss (Boss roles row; an empty row = no bosses), bad / missing arguments (not an array, fewer than 6
     elements, a blank world or role, npc not a UUID, a coordinate not a Number / NaN / huge), any error. Never throws, never loads a
     chunk, never writes a file. Any thread (on the world's own thread the block environment is read too, exactly like mob:fn:levelAt).
     zone (MobBossFn.zoneAt): the LEVEL BAND at x,y,z = exactly mob:fn:levelAt's answer (MobBossFn.bandHi -> MobLevelAtFn.at, its hi);
     no band there (null: islands, bands.default 0, part.levels off, unknown world) -> the NPC's own level (MobBossFn.npcLevel = the
     mob:fn:level path, MobLevel.MOBS: a scale.role fixed level or a mob:fn:setLevel level counts); then MobBossFn.zoneOf = the first zone
     whose top (Zone top levels row) >= that level, above the last top = the last zone; neither known = 0 (SkyyGear rolls nothing).
     role = the role id as given (trimmed). players / shares = MobCredit.sharesOf(npc): every player credited on that mob (0.1.7 kill
     credit; a pet's damage counts for its owner, 0.1.8), top damager first (a tie keeps the first hitter on top, like snap()), share =
     that player's credited damage / the total credited (0..1, sum 1); empty arrays when nobody is credited or npc is null. READ ONLY:
     the MobCredit entry stays (SkyySacks takes it later with mob:fn:credit). MobCredit.shares() is the new synchronized full list.
     Review H1: when SkyySacks' death mark took the entry first (same tick), MobCredit.read(take) keeps it in DEAD for 10 s, and
     sharesOf still answers from there (DEAD holds at most 512 entries: expired ones go first, then the oldest - never all at once;
     critic fix of the local rebuild).
  2. TWO NEW Server Setup rows, tab "Which mobs" (levels), live (an edit applies to the next boss kill), not danger:
       bosses.roles     "Boss roles" (text, max 2000) default "Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*" (= the
                        built-in BOSSES list + the *_Boss* guard); matched with MobGlob (the levels.exclude / levels.roles matcher: any
                        case, exact, Prefix*, *Part*). Empty = no bosses (mob:fn:boss always null). Field MobCfg.BOSS_ROLES.
       bosses.zoneTops  "Zone top levels" (text, max 60) default "20 30 45 60 75" (the LOCKED zone bands); 1-10 whole numbers going up,
                        each 1..levels.max (MobHooks.checkZoneTops in Server Setup; MobCfg.tops parses). A bad hand-edited value = one
                        WARN + the default. Field MobCfg.BOSS_TOPS.
     Both are read by MobCfg.apply (the config loader; after=MobCfg.bosses on an in-game edit) with c.getProperty(key, default): a file
     without the lines = the defaults (no update step, like strength.floor in 0.1.2); a fresh file carries them at its end, and the kit
     appends a line the first time an admin changes one.
  3. The ready line names mob:fn:boss with the pattern count and the zone tops (MobCfg.bossText).
SAVED DATA: none (memory only; the two new config lines are optional). No new command, no new system (asserted below).
ROLLBACK 0.1.10 -> 0.1.9: safe. The bridge goes, so SkyyGear 0.3.19 drops no boss Mythic bags; the two rows stay in the file, unread.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.9.py")
DST = os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.10.py")
if "--out" in sys.argv:
    DST = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.9"' in s and s.startswith('"""SkyyMobs 0.1.9 - build script'), "build_skyymobs_0.1.9.py is not the SET pin 0.1.9"
assert "MobBossFn" not in s and 'put("mob:fn:boss"' not in s and "bosses.roles" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.10 (2026-10-17)"):].rstrip() + "\n\n"

# ================================================================================================================ header + version
rep('''"""SkyyMobs 0.1.9 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_9_patch.py from the SET pin 0.1.8 - edit the patch,
never this file. Run: python SkyyMobs/build_skyymobs_0.1.9.py -> SkyyMobs/SkyyMobs-0.1.9.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.9.py
''', '''"""SkyyMobs 0.1.10 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_10_patch.py from the SET pin 0.1.9 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.10.py -> SkyyMobs/SkyyMobs-0.1.10.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.10.py   (--static: the text checks only)

''' + NOTE + '''0.1.9 (the base, everything below is still true unless 0.1.10 above says otherwise):
''')
rep('VERSION = "0.1.9"', 'VERSION = "0.1.10"')

# ================================================================================================================ the class
rep('''sfn = pool.makeClass(PKG + ".MobSetLevelFn")   # 0.1.9: mob:fn:setLevel (a level for a mob another mod spawns - SkyyIslands' camp / boss)
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn]
''', '''sfn = pool.makeClass(PKG + ".MobSetLevelFn")   # 0.1.9: mob:fn:setLevel (a level for a mob another mod spawns - SkyyIslands' camp / boss)
bfn = pool.makeClass(PKG + ".MobBossFn")   # 0.1.10: mob:fn:boss (who is a boss, which zone, who hurt it - SkyyGear's Mythic bags)
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn]
''')

# ================================================================================================================ the defaults (Python side)
rep('''EXCLUDE_DEF = ",".join(["Test_*", "Tamed_*", "Temple_*", "*_Merchant*", "Risen_*"] + BOSSES + GUARDS)
''', '''EXCLUDE_DEF = ",".join(["Test_*", "Tamed_*", "Temple_*", "*_Merchant*", "Risen_*"] + BOSSES + GUARDS)
# 0.1.10: the Boss roles row (mob:fn:boss, SkyyGear's Mythic bags) = the built-in BOSSES list + the *_Boss* guard; Zone top levels = the
# LOCKED zone bands (docs/answered/mobs.md 2026-10-01 Zone 1-4 = 20 / 30 / 45 / 60, world.md R8 Zone 5 = 75)
BOSS_ROLES_DEF = ", ".join(BOSSES + ["*_Boss*"])
assert BOSS_ROLES_DEF == "Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*", BOSS_ROLES_DEF
BOSS_TOPS_DEF = "20 30 45 60 75"
BOSS_PATS = [p.strip() for p in BOSS_ROLES_DEF.split(",") if p.strip()]


def boss_tops(v, mx):
    """the Python mirror of MobCfg.tops: 1-10 whole numbers (space / comma separated), strictly going up, each 1..mx; None = bad"""
    p = [t for t in re.split(r"[\\s,]+", (v or "").strip()) if t]
    if not 1 <= len(p) <= 10 or not all(t.isdigit() and len(t) <= 5 for t in p):
        return None
    n = [int(t) for t in p]
    if any(x < 1 or x > mx for x in n) or any(b <= a for a, b in zip(n, n[1:])):
        return None
    return n


def boss_zone(lv, tops):
    """the Python mirror of MobBossFn.zoneOf: the first zone whose top >= lv, above the last top = the last zone, 0 = unknown"""
    if not tops or lv < 1:
        return 0
    return next((i + 1 for i, t in enumerate(tops) if t >= lv), len(tops))


assert boss_tops(BOSS_TOPS_DEF, 100) == [20, 30, 45, 60, 75] and boss_tops(BOSS_TOPS_DEF, 74) is None
assert [boss_zone(h, [20, 30, 45, 60, 75]) for h in (1, 20, 21, 30, 31, 45, 46, 60, 61, 75, 76, 90)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
assert boss_zone(0, [20]) == 0 and boss_zone(5, []) == 0
assert all(boss_tops(b, 100) is None for b in ("", "0 10", "20 20", "30 20", "5 x", "1 2 3 4 5 6 7 8 9 10 11", "20.5", "-5 10", "101"))
for _n in VANILLA:      # every built-in boss is a boss; no mob that gets a level by default is one
    assert not matches(BOSSES, _n) or matches(BOSS_PATS, _n), "0.1.10: Boss roles misses the built-in boss " + _n
for _n in LEVELLED:
    assert not matches(BOSS_PATS, _n), "0.1.10: a levelled built-in mob would count as a boss: " + _n
assert matches(BOSS_PATS, "Dungeon_Crypt_Boss") and matches(BOSS_PATS, "trork_boss_warlord") and matches(BOSS_PATS, "Goblin_Duke")
assert not matches(BOSS_PATS, "Trork_Warrior") and not matches(BOSS_PATS, "Skeleton_Fighter") and not matches(BOSS_PATS, "Goblin_Scrapper")
''')

# ================================================================================================================ the default file
rep('''] + ["plate.colors.%s=%s" % (k, v) for k, v in COLOR_ROWS]
CFG_TEXT = "\\n".join(CFG_LINES) + "\\n"
''', '''] + ["plate.colors.%s=%s" % (k, v) for k, v in COLOR_ROWS] + [
    # 0.1.10: mob:fn:boss (SkyyGear's Mythic bags). A file without these lines uses the same defaults (no update step).
    "# Bosses: role ids or Prefix* / *Part* patterns, comma separated. A boss kill can drop Mythic gear (SkyyGear). Empty = no bosses.",
    "bosses.roles=" + BOSS_ROLES_DEF,
    "# Top level of zones 1, 2, 3 ... (Zone 1 = Lv 1-20, 2 = 20-30, 3 = 30-45, 4 = 45-60, 5 = 60-75). A boss's zone = the first top at",
    "# or above the top of the level band where it dies (no band there: its own level).",
    "bosses.zoneTops=" + BOSS_TOPS_DEF,
]
CFG_TEXT = "\\n".join(CFG_LINES) + "\\n"
''')

# ================================================================================================================ MobCfg fields
rep('''          "public static volatile Object[] ROLES_TAB;", "public static volatile String ROLE_SIG = \\"\\";"):
    F(cfg, f)
''', '''          "public static volatile Object[] ROLES_TAB;", "public static volatile String ROLE_SIG = \\"\\";"):
    F(cfg, f)
# 0.1.10: Boss roles + Zone top levels (bosses.roles / bosses.zoneTops; mob:fn:boss) and what MobCfg.bosses derives from them
for f in ("public static final String BOSS_ROLES_DEF = %s;" % jstr(BOSS_ROLES_DEF),
          "public static final String BOSS_TOPS_DEF = %s;" % jstr(BOSS_TOPS_DEF),
          "public static volatile String BOSS_ROLES = %s;" % jstr(BOSS_ROLES_DEF),
          "public static volatile String BOSS_TOPS = %s;" % jstr(BOSS_TOPS_DEF),
          "public static volatile String[] P_BOSS;", "public static volatile int[] BOSS_TOP;"):
    F(cfg, f)
''')

# ================================================================================================================ the two rows
rep('''     "reload@%s:scale.role.;check=MobHooks.checkScaleRole" % CFG_FILE),
''', '''     "reload@%s:scale.role.;check=MobHooks.checkScaleRole" % CFG_FILE),
    # 0.1.10: mob:fn:boss (SkyyGear 0.3.19's Mythic bags per boss kill, for the boss's zone); live = the next boss kill uses it
    ("bosses.roles", "Boss roles", "levels", "text", BOSS_ROLES_DEF, "", "2000", "", "", "live",
     "Boss role ids or Prefix* / *Part* patterns. A boss kill can drop Mythic gear (SkyyGear).",
     "field:MobCfg.BOSS_ROLES;after=MobCfg.bosses"),
    ("bosses.zoneTops", "Zone top levels", "levels", "text", BOSS_TOPS_DEF, "", "60", "", "", "live",
     "Top level of zones 1, 2, 3 ... A boss's zone = the first top at or above its level band's top.",
     "field:MobCfg.BOSS_TOPS;after=MobCfg.bosses;check=MobHooks.checkZoneTops"),
''')
rep('''assert [r[0] for r in CFG_ROWS] == KEYS_014 and sorted(KEYS_014) == sorted(KEYS_012 + [r[0] for r in CFG_ROWS if r[0] not in KEYS_012]), KEYS_014
''', '''# 0.1.10 = 0.1.4's keys + the two boss rows after scale.role (the old keys, ids and order unchanged)
KEYS_0110 = KEYS_014[:KEYS_014.index("scale.role") + 1] + ["bosses.roles", "bosses.zoneTops"] + KEYS_014[KEYS_014.index("scale.role") + 1:]
assert [r[0] for r in CFG_ROWS] == KEYS_0110 and sorted(KEYS_0110) == sorted(KEYS_012 + [r[0] for r in CFG_ROWS if r[0] not in KEYS_012]), KEYS_0110
assert [k for k in KEYS_0110 if not k.startswith("bosses.")] == KEYS_014
''')

# ================================================================================================================ MobCfg methods (before apply)
CFGM = r'''# 0.1.10: Zone top levels = 1-10 whole numbers (space or comma separated), strictly going up, each 1..max; null = not that
M(cfg, r"""
public static int[] tops(String v, int max) {
  if (v == null) return null;
  String t = v.trim();
  if (t.length() == 0) return null;
  String[] p = t.split("[\\s,]+");
  if (p.length < 1 || p.length > 10) return null;
  int[] r = new int[p.length];
  int prev = 0;
  for (int i = 0; i < p.length; i++) {
    String q = p[i];
    if (q.length() == 0 || q.length() > 5) return null;
    for (int k = 0; k < q.length(); k++) if (q.charAt(k) < '0' || q.charAt(k) > '9') return null;
    int n = Integer.parseInt(q);
    if (n < 1 || n > max || n <= prev) return null;
    r[i] = n;
    prev = n;
  }
  return r;
}""")
# 0.1.10: the after= hook of both boss rows + the loader's last step: the boss patterns (MobGlob, as levels.exclude) and the zone tops;
# a bad value (a hand edit, or levels.max lowered under a top) = one WARN per value + the default
M(cfg, r"""
public static void bosses(String key) {
  P_BOSS = @PKG@.MobGlob.list(BOSS_ROLES);
  int[] t = tops(BOSS_TOPS, MAX_LEVEL);
  if (t == null) {
    @PKG@.MobLog.warnOnce("bosstops:" + BOSS_TOPS + ":" + MAX_LEVEL, "bosses.zoneTops '" + BOSS_TOPS + "' is not 1-10 whole numbers going up, each 1-" + MAX_LEVEL + " - using the default " + BOSS_TOPS_DEF);
    BOSS_TOPS = BOSS_TOPS_DEF;
    t = tops(BOSS_TOPS_DEF, 1000);
  }
  BOSS_TOP = t;
}""")
M(cfg, r"""
public static boolean isBoss(String role) {
  if (role == null) return false;
  String r = role.trim();
  return r.length() > 0 && @PKG@.MobGlob.any(P_BOSS, r);
}""")
M(cfg, r"""
public static String bossText() {
  String[] p = P_BOSS;
  if (p == null || p.length == 0) return "mob:fn:boss (no bosses)";
  return "mob:fn:boss (" + p.length + " boss patterns, zone tops " + BOSS_TOPS + ")";
}""")
'''
rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c, java.util.Properties b) {
''', CFGM + '''M(cfg, r"""
public static synchronized void apply(java.util.Properties c, java.util.Properties b) {
''')
rep('''  colors(c);
''', '''  colors(c);
  BOSS_ROLES = c.getProperty("bosses.roles", BOSS_ROLES_DEF).trim();   // 0.1.10: a file without the line = the default
  BOSS_TOPS = c.getProperty("bosses.zoneTops", BOSS_TOPS_DEF).trim();
  bosses(null);
''')

# ================================================================================================================ the check hook
rep('''# ---------------------------------------------------------------- MobMig (0.1.1): the one-time difficulty update of an existing config.properties
''', '''# 0.1.10: Zone top levels in Server Setup (value null = back to the default)
M(mh, r"""
public static String checkZoneTops(String key, String value) {
  if (value == null) return null;
  int mx = @PKG@.MobCfg.MAX_LEVEL;
  if (@PKG@.MobCfg.tops(value, mx) == null) return "Type 1-10 whole numbers going up, each 1-" + mx + ", like 20 30 45 60 75.";
  return null;
}""")

# ---------------------------------------------------------------- MobMig (0.1.1): the one-time difficulty update of an existing config.properties
''')

# ================================================================================================================ MobCredit: the full list
rep('''M(mcr, r"""
public static void prune(long now) {
''', '''# 0.1.10: every credited player, top damager first (a tie keeps the first hitter on top, as snap()), share = credited / total (sum 1):
# Object[] { String[] players, double[] shares } (empty arrays when nobody is credited)
M(mcr, r"""
public synchronized Object[] shares() {
  int c = this.n;
  String[] w = new String[c];
  double[] d = new double[c];
  double tot = 0.0;
  int m = 0;
  for (int i = 0; i < c; i++) {
    if (this.who[i] == null || !(this.dmg[i] > 0.0)) continue;
    String p = this.who[i];
    double x = this.dmg[i];
    int j = m;
    while (j > 0 && d[j - 1] < x) { w[j] = w[j - 1]; d[j] = d[j - 1]; j--; }
    w[j] = p;
    d[j] = x;
    m++;
    tot = tot + x;
  }
  String[] ps = new String[m];
  double[] sh = new double[m];
  for (int i = 0; i < m; i++) { ps[i] = w[i]; sh[i] = tot > 0.0 ? d[i] / tot : 0.0; }
  return new Object[] { ps, sh };
}""")
# 0.1.10 review H1: an entry SkyySacks took (mob:fn:credit take, its death mark may run BEFORE SkyyGear's in the same tick) stays readable
# here for DEAD_MS: DEAD = mob UUID string -> Object[] { Long taken at, MobCredit }
F(mcr, "public static final java.util.concurrent.ConcurrentHashMap DEAD = new java.util.concurrent.ConcurrentHashMap();")
F(mcr, "public static final long DEAD_MS = 10000L;")
# 0.1.10: READ ONLY (the entry stays for SkyySacks' mob:fn:credit take); a taken entry within DEAD_MS still answers; null = none
M(mcr, r"""
public static Object[] sharesOf(String mob) {
  if (mob == null) return null;
  Object o = T.get(mob);
  if (o == null) {
    Object d = DEAD.get(mob);
    if (d instanceof Object[] && System.currentTimeMillis() - ((Long) ((Object[]) d)[0]).longValue() <= DEAD_MS) o = ((Object[]) d)[1];
  }
  if (!(o instanceof @PKG@.MobCredit)) return null;
  return ((@PKG@.MobCredit) o).shares();
}""")
M(mcr, r"""
public static void prune(long now) {
''')

# 0.1.10 review H1: a take keeps the entry in DEAD for DEAD_MS (mob:fn:boss reads it after SkyySacks took it); DEAD never holds more than 512
rep('''  if (take) o = T.remove(mob); else o = T.get(mob);
  if (o == null) return null;
  return ((@PKG@.MobCredit) o).snap();''', '''  if (take) o = T.remove(mob); else o = T.get(mob);
  if (o == null) return null;
  if (take) {          // 0.1.10: kept readable for mob:fn:boss (sharesOf) for DEAD_MS
    long now = System.currentTimeMillis();
    if (DEAD.size() > 512) {
      Object[] ks = DEAD.keySet().toArray();
      for (int i = 0; i < ks.length; i++) {
        Object d = DEAD.get(ks[i]);
        if (!(d instanceof Object[]) || now - ((Long) ((Object[]) d)[0]).longValue() > DEAD_MS) DEAD.remove(ks[i]);
      }
      while (DEAD.size() > 512) {          // critic fix (local rebuild): evict the OLDEST entry, never clear them all
        Object[] k2 = DEAD.keySet().toArray();
        Object old = null;
        long ot = Long.MAX_VALUE;
        for (int j = 0; j < k2.length; j++) {
          Object d2 = DEAD.get(k2[j]);
          long tt = d2 instanceof Object[] ? ((Long) ((Object[]) d2)[0]).longValue() : 0L;
          if (tt < ot) { ot = tt; old = k2[j]; }
        }
        if (old == null) break;
        DEAD.remove(old);
      }
    }
    DEAD.put(mob, new Object[] { Long.valueOf(now), o });
  }
  return ((@PKG@.MobCredit) o).snap();''')

# ================================================================================================================ mob:fn:boss
BOSSFN = r'''
# ---------------------------------------------------------------- 0.1.10 mob:fn:boss (bridge, any thread, never throws; see the header)
# Object[]{ String world, UUID npc (or null), String role, Number x, Number y, Number z } -> Object[]{ Integer zone, String role,
# String[] players, double[] shares } or null (not a boss / bad arguments / any error)
bfn.addInterface(pool.get("java.util.function.Function"))
C(bfn, "public MobBossFn() { }")
M(bfn, r"""
public static int zoneOf(int lv, int[] tops) {
  if (tops == null || tops.length == 0 || lv < 1) return 0;
  for (int i = 0; i < tops.length; i++) if (tops[i] >= lv) return i + 1;
  return tops.length;
}""")
# the level band's top at the block = mob:fn:levelAt's hi (its core MobLevelAtFn.at; the environment only on the world's own thread)
M(bfn, r"""
public static int bandHi(@WLD@ w, double x, double y, double z) {
  if (w == null) return -1;
  Object[] r = @PKG@.MobLevelAtFn.at(w, x, y, z, @PKG@.MobLevelAtFn.onThread(w));
  if (r == null || r.length < 2 || !(r[1] instanceof Integer)) return -1;
  return ((Integer) r[1]).intValue();
}""")
# the NPC's own level = the mob:fn:level path (MobLevel.MOBS; a scale.role fixed level or a mob:fn:setLevel level counts); -1 = none
M(bfn, r"""
public static int npcLevel(String wn, java.util.UUID u) {
  if (u == null) return -1;
  Object o = new @PKG@.MobLevelFn().apply(new Object[] { wn, u });
  if (!(o instanceof Integer)) return -1;
  int l = ((Integer) o).intValue();
  return l > 0 ? l : -1;
}""")
M(bfn, r"""
public static int zoneAt(@WLD@ w, String wn, java.util.UUID u, double x, double y, double z) {
  int lv = bandHi(w, x, y, z);
  if (lv < 1) lv = npcLevel(wn, u);
  if (lv < 1) return 0;
  return zoneOf(lv, @PKG@.MobCfg.BOSS_TOP);
}""")
# the testable core (the harness runs it on stand-in worlds); the credit list is read, never taken
M(bfn, r"""
public static Object[] answer(@WLD@ w, String wn, java.util.UUID u, String role, double x, double y, double z) {
  if (!@PKG@.MobCfg.isBoss(role)) return null;
  int zone = zoneAt(w, wn, u, x, y, z);
  String[] ps = new String[0];
  double[] sh = new double[0];
  Object[] c = null;
  if (u != null) c = @PKG@.MobCredit.sharesOf(u.toString());
  if (c != null && c.length >= 2 && c[0] != null && c[1] != null) { ps = (String[]) c[0]; sh = (double[]) c[1]; }
  return new Object[] { Integer.valueOf(zone), role.trim(), ps, sh };
}""")
M(bfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 6 || !(a[0] instanceof String) || !(a[2] instanceof String)) return null;
    if (a[1] != null && !(a[1] instanceof java.util.UUID)) return null;
    if (!(a[3] instanceof Number) || !(a[4] instanceof Number) || !(a[5] instanceof Number)) return null;
    String wn = ((String) a[0]).trim();
    String role = ((String) a[2]).trim();
    if (wn.length() == 0 || role.length() == 0) return null;
    double x = ((Number) a[3]).doubleValue(), y = ((Number) a[4]).doubleValue(), z = ((Number) a[5]).doubleValue();
    if (Double.isNaN(x) || Double.isNaN(y) || Double.isNaN(z) || Math.abs(x) > 1.0E8 || Math.abs(z) > 1.0E8 || Math.abs(y) > 1.0E5) return null;
    if (!@PKG@.MobCfg.isBoss(role)) return null;
    return answer(@PKG@.MobLevelAtFn.world(wn), wn, (java.util.UUID) a[1], role, x, y, z);
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("bossfn", "mob:fn:boss failed (logged once): " + t); return null; }
}""")

'''
rep('''# ================================================================= plugin
C(pl, "public SkyyMobsPlugin(@JPI@ init) { super(init); }")
''', BOSSFN + '''# ================================================================= plugin
C(pl, "public SkyyMobsPlugin(@JPI@ init) { super(init); }")
''')
rep('''  @PKG@.MobLevel.bridge().put("mob:fn:setLevel", new @PKG@.MobSetLevelFn());   // 0.1.9: a level for a mob another mod spawns (SkyyIslands)
''', '''  @PKG@.MobLevel.bridge().put("mob:fn:setLevel", new @PKG@.MobSetLevelFn());   // 0.1.9: a level for a mob another mod spawns (SkyyIslands)
  @PKG@.MobLevel.bridge().put("mob:fn:boss", new @PKG@.MobBossFn());   // 0.1.10: boss / zone / credited players (SkyyGear's Mythic bags)
''')
rep('''  try { @PKG@.MobLevel.bridge().remove("mob:fn:setLevel"); } catch (Throwable t) { }   // 0.1.9
''', '''  try { @PKG@.MobLevel.bridge().remove("mob:fn:setLevel"); } catch (Throwable t) { }   // 0.1.9
  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
''')
rep('''"; mob:fn:setLevel; /mobs; settings in Server Setup > Mobs; data in "''',
    '''"; mob:fn:setLevel; " + @PKG@.MobCfg.bossText() + "; /mobs; settings in Server Setup > Mobs; data in "''')

# ================================================================================================================ guards
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
_i = s.index
assert _i("BOSS_ROLES_DEF = \", \".join(") < _i('"bosses.roles=" + BOSS_ROLES_DEF') < _i("public static volatile String BOSS_ROLES = ") \
    < _i('("bosses.roles", "Boss roles"') < _i("kit = CFG.emit(") < _i("public static int[] tops(String v, int max)") \
    < _i("public static void bosses(String key)") < _i("public static synchronized void apply(java.util.Properties c") \
    < _i("public static String checkZoneTops(") < _i("public synchronized Object[] shares()") < _i("public static Object[] sharesOf(") \
    < _i("public MobBossFn()") < _i('put("mob:fn:boss"') < _i('remove("mob:fn:boss")')
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.9 outside the recorded changes"
compile(s, DST, "exec")
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL) if NL != LF else s)
print("wrote %s (%d lines; 0.1.9 had %d; %d changes)" % (os.path.relpath(DST, ROOT), s.count(LF), OLD.count(LF), len(CHANGES)))
