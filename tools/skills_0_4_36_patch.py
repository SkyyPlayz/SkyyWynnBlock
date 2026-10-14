"""Derive SkyySkills/build_skyyskills_0.4.36.py from the LIVE generated SkyySkills/build_skyyskills_0.4.35.py (= the tools/deploy_set.py SET
pin; 0.4.35 came from 0.4.34 by tools/skills_0_4_35_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.35 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_36_patch.py   then   python SkyySkills/build_skyyskills_0.4.36.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.36.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.36 (2026-10-14) = REBIRTH ROUND R3, the SkyySkills part (research/cloud/Rebirth-Spec.md section 5 + 6 R3; Skyy's answers
docs/answered/economy.md 2026-10-13 REBIRTH + 2026-10-14; the whole rebirth stays OFF until Server Setup -> Rebirth switches it on):
  THE REBIRTH PARTICIPANT rebirth:part:skills (SkillRb; spec 4.3 / 5.2). apply(Object[] { String op, String pkey, String txid, ... })
    -> String, never throws, never calls another mod back except rebirth:fn:decision (stale staged files):
      measure  the facts of the ACTIVE profile pkey (nothing written): x.<saved skill name>=<total XP> for every slot a rebirth resets
               (every slot but Exploration - Skyy Q3 "acrobatics yes, exploration, no."), arm.<class|foraging|mining|smithing|alchemy|
               farming|fishing|cooking>=<run XP>/<XP from 0 to the cap>/<level>/<cap> (the points curve, spec 3.5; Fishing has no
               SkyySkills row yet = no arm line). "ok:<k=v;k=v...>"
      prepare  = measure + a BACKUP of the profile's data (memory = the authority, written as players/<pkey>.properties would be) into
               Skyy_SkyySkills/rebirth-backup/<pkey>/<txid>/ (the last 3 per profile are kept; restore by hand) + the STAGED file
               Skyy_SkyySkills/rebirth/<pkey>.rb-<txid>.properties (atomic tmp + fsync + rename). Live data untouched. A staged file of
               an OLDER txid of the same profile is deleted (aborted), unless rebirth:fn:decision says it was committed (refused).
      commit   applies the staged facts as DELTAS in ONE atomic write of players/<pkey>.properties that also carries rb.lastTx=<txid>:
               every reset slot's XP = (XP now - XP at prepare), at least 0 (XP earned while the rebirth runs is kept - "SkyySkills
               keeps adding XP", spec 5.4), its paid marker = 0 (level-up coins pay again, below); Exploration untouched. Already
               applied (rb.lastTx = txid, in memory or on disk) = "done" after making sure it is on disk. A failed save answers err
               (the coordinator retries; the reset is in memory and the IO thread retries too) - so "ok" / "done" always means ON DISK.
      abort    deletes the staged file (refused once committed). status = committed / staged / none.
    players/<pkey>.properties gains ONE line rb.lastTx=<txid> after the first rebirth (written with every save from then on). Rolling
    back to 0.4.35 is safe: 0.4.35 ignores and drops that line (only matters while a rebirth is half way - SkyyRebirth 0.2 then
    re-applies; never roll back with an unfinished rebirth, /rebirthadmin status shows it).
  LEVEL-UP COINS AFTER A REBIRTH (Skyy 2026-10-14 "Yes but a little less each rebirth"): the commit puts every reset skill's paid marker
    back to 0, so its levels pay their coins again, times rebirth.coinFactor ^ n (n = the profile's rebirths from rebirth:fn:count). Server
    Setup -> Skills -> general "Level coins after each rebirth" (rebirth.coinFactor, default 0.9: 90 % after rebirth 1, 81 % after 2,
    ~35 % after 10; 1 = full coins every time; 0 = no level coins after a rebirth). With 0 rebirths (every profile today) the coins are
    exactly 0.4.35's. While SkyyRebirth is still reading a profile's file (rebirth:fn:count answers null) the coins stay owed and are
    paid at the next XP gain - never at the wrong factor. The level-up chat line and the Stats page "+N coins when you reach level"
    show the same scaled number.
  LEVELS ABOVE 100 STAY OUT (Skyy 2026-10-14: "No" to counting them for Overall Level / Mana / class-weapon bonus / leaderboards). Checked:
    0.4.35 already keeps the TABLE levels (levelOf, never above the table max) for the Overall Level (Overall.sums / levelUp), the Overall
    + class Mana (Overall.mana, ClassMana.amountFor, ClassPower.classLevel) and the leaderboards (SkillTop / /skills top). NOT yet for the
    CLASS-WEAPON BONUS: CombatDmgSys used the capped level (Perks.damage = level x perk.combat.damagePerLevel, so a level 110 class hit
    harder than 100) - 0.4.36 clamps it to the table max there, and the Stats page damage line says the same (no "+" line above the max).
  NOTHING ELSE CHANGES: no rebirth can run unless SkyyRebirth 0.2 is loaded AND switched on (or an admin runs /rebirthadmin); the
    participant only answers. New bridge key rebirth:part:skills (removed at shutdown).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.35.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.36.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.35"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.35"' in s and "derived from the generated 0.4.34 by tools/skills_0_4_35_patch.py" in s, "not the live generated 0.4.35"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert 'srun = pool.makeClass(PKG + ".SkillRunFn")' in s, "not 0.4.35 (SkillRunFn missing)"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.36 (2026-10-14)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.35 - build script (derived from the generated 0.4.34 by tools/skills_0_4_35_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.36 - build script (derived from the generated 0.4.35 by tools/skills_0_4_36_patch.py - edit the patch, not this file;
0.4.35 was derived from the generated 0.4.34 by tools/skills_0_4_35_patch.py;
''')
rep('''0.4.35 (2026-10-13) = REBIRTH ROUND R1''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.36.py.
0.4.35 (2026-10-13) = REBIRTH ROUND R1''')
rep('VERSION = "0.4.35"', 'VERSION = "0.4.36"')

# ---------------------------------------------------------------- SkillCfg: rebirth.coinFactor (Server Setup row, default 0.9)
rep('''cfg.addField(CtField.make("public static volatile long COINS_PER_LEVEL = 100L;", cfg))''',
    '''cfg.addField(CtField.make("public static volatile long COINS_PER_LEVEL = 100L;", cfg))
cfg.addField(CtField.make("public static volatile double RB_COIN = 0.9;", cfg))   # 0.4.36: rebirth.coinFactor (level coins x this ^ rebirths)''')
rep('''    COINS_PER_LEVEL = lng(p, "coinsPerLevel", 100L);
''', '''    COINS_PER_LEVEL = lng(p, "coinsPerLevel", 100L);
    double rbc = dbl(p, "rebirth.coinFactor", 0.9);   // 0.4.36: a bad / missing number = 0.9, clamped 0 - 1
    RB_COIN = Double.isNaN(rbc) ? 0.9 : (rbc < 0.0 ? 0.0 : (rbc > 1.0 ? 1.0 : rbc));
''')
rep('''     "A level up pays this x the new level in coins (needs SkyyCoins).", "reload"),
''', '''     "A level up pays this x the new level in coins (needs SkyyCoins).", "reload"),
    # 0.4.36 (Skyy 2026-10-14 "Yes but a little less each rebirth"): level coins pay again after each rebirth, x this once per rebirth
    ("rebirth.coinFactor", "Level coins after each rebirth", "general", "dec", "0.9", "0", "1", "", "x", "live",
     "After a rebirth level coins pay again, x this per rebirth (0.9: 90 %, then 81 %...). 1 = full coins.", "reload"),
''')
rep('''assert len(CFG_ROWS) == 229, ("0.4.35: + farming.tierUpXpFactor;''',
    '''assert len(CFG_ROWS) == 230, ("0.4.36: + rebirth.coinFactor; 0.4.35: + farming.tierUpXpFactor;''')
rep('''L.append("coinsPerLevel=100")
''', '''L.append("coinsPerLevel=100")
L.append("# After a rebirth the level-up coins pay again, times rebirth.coinFactor once per rebirth (0.9 = 90 % after 1, 81 % after 2).")
L.append("rebirth.coinFactor=0.9")
''')

# ---------------------------------------------------------------- SkillStore: rb.lastTx in the profile file (RBTX), read + saved with it
rep('''sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap OWNER = new java.util.concurrent.ConcurrentHashMap();", sto))''',
    '''sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap OWNER = new java.util.concurrent.ConcurrentHashMap();", sto))
# 0.4.36: RBTX = pkey -> the txid of the last rebirth applied to that profile (rb.lastTx in its file, written with every save)
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RBTX = new java.util.concurrent.ConcurrentHashMap();", sto))''')
rep('''  String nm = null;
  boolean quiet = false;
  try {{
    java.nio.file.Path f = DIR.resolve(k + ".properties");''', '''  String nm = null;
  boolean quiet = false;
  String rbtx = null;   // 0.4.36: rb.lastTx
  try {{
    java.nio.file.Path f = DIR.resolve(k + ".properties");''')
rep('''      quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
''', '''      quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
      String rt = p.getProperty("rb.lastTx");
      if (rt != null && rt.trim().length() > 0) rbtx = rt.trim();
''')
rep('''  return new Object[] {{ d, nm, Boolean.valueOf(quiet) }};''', '''  return new Object[] {{ d, nm, Boolean.valueOf(quiet), rbtx }};''')
rep('''  if (((Boolean) got[2]).booleanValue()) QUIET.put(k, Boolean.TRUE);
''', '''  if (((Boolean) got[2]).booleanValue()) QUIET.put(k, Boolean.TRUE);
  if (got.length > 3 && got[3] instanceof String) RBTX.put(k, got[3]);   // 0.4.36
''')
rep('''  p.setProperty("quiet", QUIET.containsKey(k) ? "true" : "false");
''', '''  p.setProperty("quiet", QUIET.containsKey(k) ? "true" : "false");
  Object rbt = RBTX.get(k);   // 0.4.36: the last rebirth applied - in the SAME write as the XP it reset
  if (rbt instanceof String) p.setProperty("rb.lastTx", (String) rbt);
''')

# ---------------------------------------------------------------- level coins x rebirth.coinFactor ^ n
rep('''# pay every owed level of one skill, lowest first; the paid marker only moves past a level whose coins really arrived.
''', '''# 0.4.36: the profile's rebirths for the level coins (rebirth:fn:count): 0 without SkyyRebirth, -1 while it is still reading that profile's
# file (the coins then stay owed - paid at the next XP gain, never at the wrong factor). Any thread, never throws.
sto.addMethod(CtNewMethod.make("""
public static int rbN(String k) {
  try {
    Object f = bridge().get("rebirth:fn:count");
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(k);
    if (r instanceof Number) { int n = ((Number) r).intValue(); return n < 0 ? 0 : n; }
    return -1;
  } catch (Throwable t) { return 0; }
}""", sto))
# 0.4.36 (Skyy 2026-10-14 "Yes but a little less each rebirth"): coins x rebirth.coinFactor ^ n, rounded; n = 0 = unchanged
sto.addMethod(CtNewMethod.make(f"""
public static long rbCoins(long coins, int n) {{
  if (coins <= 0L || n <= 0) return coins;
  double f = {PKG}.SkillCfg.RB_COIN;
  if (!(f < 1.0)) return coins;
  if (!(f > 0.0)) return 0L;
  double x = (double) coins * Math.pow(f, (double) n);
  if (x >= 9.0E18) return coins;
  long r = Math.round(x);
  return r < 0L ? 0L : r;
}}""", sto))
# pay every owed level of one skill, lowest first; the paid marker only moves past a level whose coins really arrived.
''')
rep('''  int lv = {PKG}.SkillCap.level(k, skill, rd(d, skill));   // 0.4.35: up to the cap of profile k (the paid marker still pays each level once)
  boolean stop = false;''', '''  int lv = {PKG}.SkillCap.level(k, skill, rd(d, skill));   // 0.4.35: up to the cap of profile k (the paid marker still pays each level once)
  int rbn = rbN(k);   // 0.4.36: the profile's rebirths (coins x rebirth.coinFactor ^ rbn); -1 = not known yet -> owed, nothing paid now
  if (rbn < 0) return new long[] {{ -1L, -1L, 0L, per, 0L, 0L }};
  boolean stop = false;''')
rep('''    long coins = per * next;
    if (per <= 0L || coins / next != per) {{
      wr(d, {PKG}.SkillDefs.N + skill, next);
      changed = 1L;
    }} else if (coinsAdd(u, coins)) {{''', '''    long coins = per * next;
    if (per <= 0L || coins / next != per) {{
      wr(d, {PKG}.SkillDefs.N + skill, next);
      changed = 1L;
    }} else if ((coins = rbCoins(coins, rbn)) <= 0L) {{   // 0.4.36: rebirth.coinFactor 0 after a rebirth: the level counts as paid, no coins
      wr(d, {PKG}.SkillDefs.N + skill, next);
      changed = 1L;
    }} else if (coinsAdd(u, coins)) {{''')
rep('''  return new long[] {{ first, last, sum, per, changed }};''', '''  return new long[] {{ first, last, sum, per, changed, (long) rbn }};   // 0.4.36: [5] = the rebirths the coins were scaled by''')
rep('''        long coins = paid[3] * lv;''', '''        long coins = {PKG}.SkillStore.rbCoins(paid[3] * lv, paid.length > 5 ? (int) paid[5] : 0);   // 0.4.36: what was paid''')
rep('''  if (next && {PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillCfg.COINS_PER_LEVEL * (long) b) + " coins when you reach level " + b);''',
    '''  if (next && {PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.SkillCfg.COINS_PER_LEVEL * (long) b, {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + b);   // 0.4.36: x rebirth.coinFactor ^ rebirths''')

# ---------------------------------------------------------------- the class-weapon bonus counts the table levels only (Skyy 2026-10-14 "No")
rep('''    int clv = {PKG}.SkillStore.level(u, slot);
    double bonus = {PKG}.Perks.damage(clv)''', '''    int clv = Math.min({PKG}.SkillStore.level(u, slot), {PKG}.SkillDefs.maxOf(slot));   // 0.4.36: levels above the table max (rebirth caps) add no weapon damage
    double bonus = {PKG}.Perks.damage(clv)''')
rep('''    double dm = next ? {PKG}.PerkCfg.DMG : {PKG}.Perks.damage(lv);''',
    '''    double dm = next ? (lv >= {PKG}.SkillDefs.maxOf(s) ? 0.0 : {PKG}.PerkCfg.DMG) : {PKG}.Perks.damage(Math.min(lv, {PKG}.SkillDefs.maxOf(s)));   // 0.4.36: the table levels only''')

# ---------------------------------------------------------------- SkillRb: the rebirth participant (after SkillRunFn, before MsgRoute)
rep('''# ================= 0.4.34 MsgRoute: chat / feed / off per message kind (tools/skyyroute.py; SkyyHud 0.3.20+ bridge API) =================
mrt = pool.makeClass(PKG + ".MsgRoute")''', '''# ================= 0.4.36 the rebirth participant rebirth:part:skills (research/cloud/Rebirth-Spec.md 4.3 / 5.2 / 5.3) =================
# SkillStore.rbReset0: the reset of one profile under the SkillStore lock (the lock bump / rd / wr / snap hold): every slot with prep >= 0
# gets XP = now - prep (at least 0) and paid marker 0; RBTX = tx in the same step, so the next snap / save carries both. false = this tx was
# already applied (nothing changed).
sto.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean rbReset0(String k, long[] d, String tx, long[] prep) {
  if (tx.equals(RBTX.get(k))) return false;
  int n = @PKG@.SkillDefs.N;
  for (int s = 0; s < n && s < prep.length; s++) {
    if (prep[s] < 0L) continue;
    long v = d[s] - prep[s];
    d[s] = v < 0L ? 0L : v;
    d[n + s] = 0L;
  }
  RBTX.put(k, tx);
  return true;
}"""), sto))
# fix round: rbReset holds the profile's data array FIRST (the lock payGuarded holds for the whole level-coin loop), then the SkillStore
# class lock (rbReset0) - the same order as payGuarded -> rd / wr, so a reset never lands inside a payout loop that computed its level
# before the reset (it would pay levels 1..old level again on the emptied profile).
sto.addMethod(CtNewMethod.make(J14(r"""
public static boolean rbReset(String k, long[] d, String tx, long[] prep) {
  synchronized (d) { return rbReset0(k, d, tx, prep); }
}"""), sto))
srb = pool.makeClass(PKG + ".SkillRb")
srb.addInterface(pool.get("java.util.function.Function"))
srb.addConstructor(CtNewConstructor.make("public SkillRb() { }", srb))
for _d in ("public static volatile int FAIL_SAVE = 0;",   # test hook: the next N commit saves fail (a crash inside the participant's write)
           "public static final java.util.concurrent.atomic.AtomicLong APPLIED = new java.util.concurrent.atomic.AtomicLong();",
           'public static final String[] ARMS = new String[] { "class", "foraging", "mining", "smithing", "alchemy", "farming", "fishing", "cooking" };'):
    srb.addField(CtField.make(_d, srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static java.nio.file.Path home() {
  java.nio.file.Path d = @PKG@.SkillStore.DIR;
  return d == null ? null : d.getParent();
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static boolean validTx(String tx) {
  return tx != null && tx.matches("tx[0-9]{13}-[0-9a-f]{6}");
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static java.util.UUID owner(String k) {
  try { return java.util.UUID.fromString(k.substring(0, 36)); } catch (Throwable t) { return null; }
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static java.nio.file.Path staged(String k, String tx) {
  return home().resolve("rebirth").resolve(k + ".rb-" + tx + ".properties");
}"""), srb))
# tmp + fsync + atomic rename (SkillStore.moveRetry: ATOMIC_MOVE, 5 tries on a Windows sharing violation)
srb.addMethod(CtNewMethod.make(J14(r"""
public static void writeProps(java.nio.file.Path f, java.util.Properties p, String comment) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try { p.store(out, comment); out.flush(); out.getFD().sync(); } finally { out.close(); }
  @PKG@.SkillStore.moveRetry(tmp, f);
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static java.util.Properties readProps(java.nio.file.Path f) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    return @PKG@.SkillStore.readProps(f);
  } catch (Throwable t) { return null; }
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static String text(java.util.Properties p) {
  java.util.TreeSet ks = new java.util.TreeSet(p.stringPropertyNames());
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = ks.iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    if (sb.length() > 0) sb.append(';');
    sb.append(key).append('=').append(p.getProperty(key));
  }
  return sb.toString();
}"""), srb))
# the facts (spec 5.2 step 1): x.<saved name> = total XP of every slot a rebirth resets; arm.<arm> = run XP / XP to the cap / level / cap
srb.addMethod(CtNewMethod.make(J14(r"""
public static java.util.Properties facts(String k, java.util.UUID u, long[] d) {
  java.util.Properties p = new java.util.Properties();
  int n = @PKG@.SkillDefs.N;
  for (int s = 0; s < n; s++) {
    if (@PKG@.SkillDefs.rebirthResets(s)) p.setProperty("x." + @PKG@.SkillDefs.NAMES[s], String.valueOf(@PKG@.SkillStore.rd(d, s)));
  }
  for (int i = 0; i < ARMS.length; i++) {
    int s = i == 0 ? @PKG@.SkillClass.slot(u) : @PKG@.SkillDefs.indexOf(ARMS[i]);
    if (s < 0 || s >= n) continue;
    long total = @PKG@.SkillStore.rd(d, s);
    int cap = @PKG@.SkillCap.cap(k, s);
    p.setProperty("arm." + ARMS[i], total + "/" + @PKG@.SkillDefs.cumAt(s, cap) + "/" + @PKG@.SkillDefs.levelCap(s, total, cap) + "/" + cap);
  }
  return p;
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static void deleteTree(java.io.File f) {
  if (f == null) return;
  java.io.File[] c = f.listFiles();
  if (c != null) for (int i = 0; i < c.length; i++) deleteTree(c[i]);
  f.delete();
}"""), srb))
# the backup (spec 5.1 item 5): the profile's data as memory holds it, the last 3 rebirths per profile kept (older ones deleted)
srb.addMethod(CtNewMethod.make(J14(r"""
public static void backup(String k, String tx, java.util.Properties snap) throws java.io.IOException {
  java.nio.file.Path dir = home().resolve("rebirth-backup").resolve(k);
  writeProps(dir.resolve(tx).resolve(k + ".properties"), snap, "SkyySkills rebirth backup of players/" + k + ".properties before " + tx + " - restore by hand while the server is stopped");
  java.io.File[] all = dir.toFile().listFiles();
  if (all == null || all.length <= 3) return;
  java.util.Arrays.sort(all);
  for (int i = 0; i < all.length - 3; i++) deleteTree(all[i]);
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static String decision(String tx) {
  try {
    Object f = @PKG@.SkillStore.bridge().get("rebirth:fn:decision");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(tx);
      if (r instanceof String) return (String) r;
    }
  } catch (Throwable t) { }
  return "unknown";
}"""), srb))
# a staged file of an OLDER txid of this profile = a rebirth that was aborted while this mod could not hear it: deleted (live data was never
# touched); one SkyyRebirth says was committed is refused instead (that rebirth is still finishing)
srb.addMethod(CtNewMethod.make(J14(r"""
public static String cleanStale(String k, String tx) {
  java.io.File[] fs = home().resolve("rebirth").toFile().listFiles();
  if (fs == null) return null;
  String pre = k + ".rb-";
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!nm.startsWith(pre)) continue;
    String old;
    if (nm.endsWith(".properties")) old = nm.substring(pre.length(), nm.length() - 11);
    else if (nm.endsWith(".properties.tmp")) old = nm.substring(pre.length(), nm.length() - 15);   // a staged write torn by a crash
    else continue;
    if (old.equals(tx)) continue;
    if ("commit".equals(decision(old))) return "err:an older rebirth of this profile is still finishing (" + old + ")";
    fs[i].delete();
  }
  return null;
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static String prepare(String k, String tx, boolean write) {
  java.util.UUID u = owner(k);
  if (u == null) return "err:bad profile key";
  if (!k.equals(@PKG@.SkillStore.pkey(u))) return "err:" + k + " is not the player's active profile";
  long[] d = @PKG@.SkillStore.dataK(k, u);
  if (tx.equals(@PKG@.SkillStore.RBTX.get(k))) return "err:already committed";
  java.util.Properties f = facts(k, u, d);
  if (!write) return "ok:" + text(f);
  String st = cleanStale(k, tx);
  if (st != null) return st;
  try {
    java.util.Properties snap = @PKG@.SkillStore.snap(k);
    if (snap != null) backup(k, tx, snap);
    java.util.Properties sp = new java.util.Properties();
    sp.putAll(f);
    sp.setProperty("tx", tx);
    sp.setProperty("pkey", k);
    writeProps(staged(k, tx), sp, "SkyySkills rebirth " + tx + " - staged (live data untouched until the commit)");
  } catch (Throwable t) { return "err:could not write the staged file: " + t; }
  return "ok:" + text(f);
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static boolean saveIt(String k) {
  if (FAIL_SAVE > 0) { FAIL_SAVE = FAIL_SAVE - 1; return false; }
  return @PKG@.SkillStore.save(k);
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static String commit(String k, String tx) {
  java.util.UUID u = owner(k);
  if (u == null) return "err:bad profile key";
  long[] d = @PKG@.SkillStore.dataK(k, u);
  java.nio.file.Path sp = staged(k, tx);
  if (tx.equals(@PKG@.SkillStore.RBTX.get(k))) {
    if (!saveIt(k)) { @PKG@.SkillStore.DIRTY.put(k, Boolean.TRUE); return "err:could not save players/" + k + ".properties (retried)"; }
    try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
    return "done";
  }
  java.util.Properties p = readProps(sp);
  if (p == null || !tx.equals(p.getProperty("tx"))) return "err:no staged file for " + tx;
  int n = @PKG@.SkillDefs.N;
  long[] prep = new long[n];
  for (int s = 0; s < n; s++) {
    prep[s] = -1L;
    if (!@PKG@.SkillDefs.rebirthResets(s)) continue;
    String v = p.getProperty("x." + @PKG@.SkillDefs.NAMES[s]);
    if (v == null) return "err:the staged file has no x." + @PKG@.SkillDefs.NAMES[s];
    try { prep[s] = Long.parseLong(v.trim()); } catch (Throwable t) { return "err:bad x." + @PKG@.SkillDefs.NAMES[s]; }
    if (prep[s] < 0L) return "err:bad x." + @PKG@.SkillDefs.NAMES[s];
  }
  @PKG@.SkillStore.rbReset(k, d, tx, prep);
  @PKG@.SkillStore.topPut(k, null, d);
  @PKG@.SkillCap.CACHE.remove(k);
  if (!saveIt(k)) { @PKG@.SkillStore.DIRTY.put(k, Boolean.TRUE); return "err:could not save players/" + k + ".properties (the reset is in memory; retried)"; }
  try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
  APPLIED.incrementAndGet();
  @PKG@.SkillStore.republishAll();
  @PKG@.SkillCfg.info("rebirth " + tx + ": skills of " + k + " reset (Exploration kept), level coins pay again x" + @PKG@.SkillCfg.RB_COIN + " per rebirth");
  return "ok";
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static String abort(String k, String tx) {
  if (tx.equals(@PKG@.SkillStore.RBTX.get(k))) return "err:already committed";
  try {
    java.nio.file.Path sp = staged(k, tx);
    java.nio.file.Files.deleteIfExists(sp);
    java.nio.file.Files.deleteIfExists(sp.resolveSibling(sp.getFileName().toString() + ".tmp"));   // a staged write torn by a crash
  } catch (Throwable t) { return "err:" + t; }
  return "done";
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public static String status(String k, String tx) {
  java.util.UUID u = owner(k);
  if (u != null) @PKG@.SkillStore.dataK(k, u);
  if (tx.equals(@PKG@.SkillStore.RBTX.get(k))) return "committed";
  return java.nio.file.Files.exists(staged(k, tx), new java.nio.file.LinkOption[0]) ? "staged" : "none";
}"""), srb))
srb.addMethod(CtNewMethod.make(J14(r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "err:bad arguments";
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof String) || !(a[2] instanceof String)) return "err:bad arguments";
    String op = (String) a[0];
    String k = ((String) a[1]).trim();
    String tx = (String) a[2];
    if (!@PKG@.SkillRunFn.validKey(k)) return "err:bad profile key";
    if (!validTx(tx)) return "err:bad txid";
    if (@PKG@.SkillStore.DIR == null) return "err:SkyySkills is not started";
    if ("measure".equals(op)) return prepare(k, tx, false);
    if ("prepare".equals(op)) return prepare(k, tx, true);
    if ("commit".equals(op)) return commit(k, tx);
    if ("abort".equals(op)) return abort(k, tx);
    if ("status".equals(op)) return status(k, tx);
    return "err:unknown op " + op;
  } catch (Throwable t) { return "err:" + t; }
}"""), srb))

# ================= 0.4.34 MsgRoute: chat / feed / off per message kind (tools/skyyroute.py; SkyyHud 0.3.20+ bridge API) =================
mrt = pool.makeClass(PKG + ".MsgRoute")''')

# ---------------------------------------------------------------- plugin: bridge key, shutdown, ready line, class list
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:run", new {PKG}.SkillRunFn());   // 0.4.35: run XP + the capped level for SkyyRebirth
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:run", new {PKG}.SkillRunFn());   // 0.4.35: run XP + the capped level for SkyyRebirth
  {PKG}.SkillStore.bridge().put("rebirth:part:skills", new {PKG}.SkillRb());   // 0.4.36: the rebirth participant (SkyyRebirth 0.2+)
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:run"); }} catch (Throwable t) {{ }}   // 0.4.35
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:run"); }} catch (Throwable t) {{ }}   // 0.4.35
  try {{ {PKG}.SkillStore.bridge().remove("rebirth:part:skills"); }} catch (Throwable t) {{ }}   // 0.4.36
''')
rep('''+ ", XP past max counts (skill:fn:run), Exploration never resets" + ''',
    '''+ ", XP past max counts (skill:fn:run), Exploration never resets" + "; rebirth participant rebirth:part:skills (level coins after a rebirth x" + {PKG}.SkillCfg.RB_COIN + " per rebirth, rebirth.coinFactor; the class-weapon bonus counts the table levels only)" + ''')
rep('''          rbf, pset, sio, polm, mrt, scap, ftr, srun):   # 0.4.35: + SkillCap, FarmTier, SkillRunFn;''',
    '''          rbf, pset, sio, polm, mrt, scap, ftr, srun, srb):   # 0.4.36: + SkillRb; 0.4.35: + SkillCap, FarmTier, SkillRunFn;''')

# ---------------------------------------------------------------- checks
assert s.index("public static int rbN(String k)") < s.index("public static long[] payLocked(")
assert s.index("public static synchronized boolean rbReset0(") < s.index("public static boolean rbReset(String k")
assert s.index("public static boolean rbReset(String k") < s.index("public static String commit(String k, String tx)")
assert s.index('srun = pool.makeClass(PKG + ".SkillRunFn")') < s.index('srb = pool.makeClass(PKG + ".SkillRb")')
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.35 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.35,", len(_gone), "0.4.35 lines replaced;", len(OLDS), "anchors")
