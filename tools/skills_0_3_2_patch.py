"""Derive SkyySkills/build_skyyskills_0.3.2.py from 0.3.1 (same style as skills_0_3_patch.py: rep(old, new) with asserted anchors,
newline-agnostic; 0.3.1 stays untouched, the CRLF/LF line endings of 0.3.1 are preserved).
0.3.2 = per-profile storage (tools/PROFILES-CONTRACT.md v1):
 - SkillStore.pkey(u) = the contract helper, verbatim (bridge profile:fn:key, fallback uuid.toString() = profile 1).
 - Rule 1: players/<pkey>.properties (profile 1 = the existing players/<uuid>.properties, no migration).
 - Rule 2: DATA / QUIET / DIRTY keyed by the pkey String (+ OWNER key -> UUID for the saved name); NAMES / PUBLISHED / chat throttle /
   TOLD / Acrobatics tracker / movement applier stay per UUID (they describe the physical player, not a save).
 - Rule 3: skill:<uuid> stays UUID-keyed; the existing 1 s AcroSys player tick compares profile:epoch:<uuid> with the last value seen
   (Perks.EPOCH) and republishes on change.
 - Rule 4: on an epoch change the same tick drops the Acrobatics tracker's unpaid fractions / pending landing (earned on the old
   profile), then recomputes the "skills.acrobatics" movement source and the skyyskill_* MAX modifiers from the new profile.
 - Class for combat stays class:<uuid> (SkyyClasses publishes the active profile's class). While profile:class:<uuid> exists and
   class:<uuid> does not match it yet (SkyyClasses has not caught up with a switch), no combat XP / damage perk / legacy migration.
   Bounded (review fix): a mismatch older than SkillClass.GRACE_MS (10 s = five SkyyClasses 0.1.3 ticks) fails OPEN - one SkillCfg
   warning per player per switch, then the three follow class:<uuid> again (the 0.3.1 behaviour), so an older SkyyClasses (0.1.2
   never reads profile:class) or a SkyyClasses bug can never pause combat XP forever. Pairing: SkyyClasses 0.1.3+ with SkyyProfiles.
 - Leaderboards: one row per profile file; rows of profile N >= 2 show "(profile N)"; your rank = your active profile's row.
 - Without SkyyProfiles every key is uuid.toString(), no epoch, no profile:class -> behaviour identical to 0.3.1.
 - Review fix (pre-existing since 0.3.1): /skills top|stats help and the unknown-skill message say "shaman" instead of the removed
   "berserking" (SkillDefs.indexOf resolves "shaman" to the Shaman placeholder slot; "berserking" never resolved since 0.3.1).
Run:  python tools/skills_0_3_2_patch.py   then   python SkyySkills/build_skyyskills_0.3.2.py   (NO --deploy: coordinated deploy)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.3.1.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.3.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.3.1"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


# ---------------------------------------------------------------- header / version
rep('''"""SkyySkills 0.3 - build script (derived from 0.2 by tools/skills_0_3_patch.py - edit the patch, not this file)
0.3.1 (design lock''', '''"""SkyySkills 0.3.2 - build script (derived from 0.3.1 by tools/skills_0_3_2_patch.py - edit the patch, not this file;
0.3 was derived from 0.2 by tools/skills_0_3_patch.py)
0.3.2: per-profile storage (tools/PROFILES-CONTRACT.md). XP, paid markers, the per-class combat XP (Combat.<Class>), perks,
  Acrobatics level and the /skills quiet flag belong to the ACTIVE profile: players/<pkey>.properties, pkey = the contract's pkey()
  helper (SkillStore.pkey: bridge profile:fn:key applied to the UUID). Without SkyyProfiles (or when it answers nothing) pkey =
  uuid.toString() = profile 1, and profile 1's file is the existing players/<uuid>.properties (no migration, behaviour identical to
  0.3.1). In-memory caches DATA / QUIET / DIRTY are keyed by the pkey String (OWNER maps a key back to its UUID for the saved name);
  NAMES (username), PUBLISHED, the chat throttle, the once-per-session hints (TOLD) and the Acrobatics movement tracker stay per
  player (UUID). Bridge values stay UUID keys describing the active profile: skill:<uuid>, skill:fn:level. Every level read goes
  through pkey, so the per-second skyyskill_health / stamina / mana MAX modifiers and the "skills.acrobatics" movement source follow
  the active profile. EPOCH CHECK in the existing once-per-second AcroSys player tick (world thread), BEFORE the Acrobatics flush,
  movement sync and perk tick: profile:epoch:<uuid> differs from the last value seen for that UUID (Perks.EPOCH) -> republish
  skill:<uuid>, drop the Acrobatics tracker's unpaid XP fraction, pending landing / fall note and unshown chat XP (earned on the old
  profile, never credited to the new one), forget the pending +XP chat line and the hints; the same tick then recomputes the
  movement source and the MAX modifiers from the new profile's levels. The class for combat is still class:<uuid> (SkyyClasses
  publishes the active profile's class); while profile:class:<uuid> is published and class:<uuid> does not match it yet (SkyyClasses
  has not caught up with a switch), no combat XP (one hint), no class damage perk and no legacy Combat migration, so nothing lands
  in the wrong class slot. That pause is BOUNDED: a mismatch still there after SkillClass.GRACE_MS (10 s; SkyyClasses 0.1.3
  republishes every 2 s) fails open - one warning in the server log per player per switch, then combat XP, the damage perk and the
  legacy move follow class:<uuid> again (0.3.1 behaviour), so SkyyClasses 0.1.2 (never reads profile:class) or a SkyyClasses bug
  can never pause them forever. DEPLOY PAIRING: with SkyyProfiles, ship SkyyClasses 0.1.3+ (0.1.2 would make every profile switch
  run on the class of the class file after the 10 s grace). /skills top: one row per profile file, profile N >= 2 rows show
  "(profile N)", your rank is your active profile's. The vanilla inventory is never touched for a switch (contract rule 5; double
  drops still go to the live inventory). The first read of a switched-to profile's file happens on the player's world thread in
  that 1 s tick (same as PublishTask: the shared SCHEDULED_EXECUTOR never does player-file I/O); one small file per manual switch.
  Skill args: "shaman" replaces the removed "berserking" in the /skills top|stats help and the unknown-skill message.
0.3.1 (design lock''')
rep('''Run:   python build_skyyskills_0.3.py            -> SkyySkills/SkyySkills-0.3.jar
       python build_skyyskills_0.3.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.3.2.py            -> SkyySkills/SkyySkills-0.3.2.jar
       python build_skyyskills_0.3.2.py --deploy   -> also copies''')
rep('VERSION = "0.3.1"', 'VERSION = "0.3.2"')

# ---------------------------------------------------------------- SkillStore: keys, pkey helper (contract, verbatim), OWNER, quiet
rep('''# ================= SkillStore: per-player XP, persistence, bridge =================
# data layout: long[2*N] = xp[0..N-1], paid level[N..2N-1]   (0.2: N = 5; 0.1 hard-coded long[8] / offset 4)
''', '''# ================= SkillStore: per-player XP, persistence, bridge =================
# data layout: long[2*N] = xp[0..N-1], paid level[N..2N-1]   (0.2: N = 5; 0.1 hard-coded long[8] / offset 4)
# 0.3.2 (tools/PROFILES-CONTRACT.md): DATA / QUIET / DIRTY / OWNER are keyed by the profile storage key pkey(u) (a String:
# "<uuid>" = profile 1, "<uuid>-pN" = profile N); NAMES (username) and PUBLISHED (bridge state) stay keyed by the player's UUID.
''')
rep('''sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", sto))
''', '''sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap OWNER = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", sto))
# 0.3.2: storage key of the player's ACTIVE profile - the contract's helper, verbatim (tools/PROFILES-CONTRACT.md)
sto.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", sto))
# /skills quiet is stored in the profile file, so it is per profile like everything else in that file
sto.addMethod(CtNewMethod.make("""
public static boolean quiet(java.util.UUID u) {
  return QUIET.containsKey(pkey(u));
}""", sto))
''')

# readFile: one profile file
rep('''public static Object[] readFile(java.util.UUID u) {{''', '''public static Object[] readFile(String k, java.util.UUID u) {{''')
rep('''    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");''', '''    java.nio.file.Path f = DIR.resolve(k + ".properties");''')
rep('''  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load skills for " + u + ": " + t); }}''',
    '''  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load skills for " + k + ": " + t); }}''')
rep('''# player file -> {long[2*N] data, String name, Boolean quiet}. Runs WITHOUT any lock (no disk I/O under the SkillStore lock).''',
    '''# player file (players/<pkey>.properties, 0.3.2) -> {long[2*N] data, String name, Boolean quiet}. Runs WITHOUT any lock (no disk I/O
# under the SkillStore lock).''')

# data(u): key once, install under the SkillStore lock (a synchronized method instead of the 0.3.1 multi-statement block)
rep('''# cached data; a first load reads the file BEFORE taking the lock, the lock only decides whose copy is installed
sto.addMethod(CtNewMethod.make(f"""
public static long[] data(java.util.UUID u) {{
  long[] d = (long[]) DATA.get(u);
  if (d != null) return d;
  Object[] got = readFile(u);
  synchronized ({PKG}.SkillStore.class) {{
    d = (long[]) DATA.get(u);
    if (d == null) {{
      d = (long[]) got[0];
      if (got[1] != null) NAMES.putIfAbsent(u, got[1]);
      if (((Boolean) got[2]).booleanValue()) QUIET.put(u, Boolean.TRUE);
      DATA.put(u, d);
    }}
  }}
  return d;
}}""", sto))
''', '''# cached data; a first load reads the file BEFORE taking the lock, the lock only decides whose copy is installed.
# 0.3.2: keyed by the profile storage key k = pkey(u) (contract rule 2); OWNER k -> UUID (for the name saved in the file).
sto.addMethod(CtNewMethod.make("""
public static synchronized long[] install(String k, java.util.UUID u, Object[] got) {
  long[] d = (long[]) DATA.get(k);
  if (d != null) return d;
  d = (long[]) got[0];
  if (got[1] != null) NAMES.putIfAbsent(u, got[1]);
  if (((Boolean) got[2]).booleanValue()) QUIET.put(k, Boolean.TRUE);
  OWNER.put(k, u);
  DATA.put(k, d);
  return d;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] dataK(String k, java.util.UUID u) {
  long[] d = (long[]) DATA.get(k);
  if (d != null) return d;
  Object[] got = readFile(k, u);
  return install(k, u, got);
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] data(java.util.UUID u) {
  return dataK(pkey(u), u);
}""", sto))
''')

# snap / save / flush by key
rep('''public static synchronized java.util.Properties snap(java.util.UUID u) {{
  long[] d = (long[]) DATA.get(u);
  if (d == null) return null;
  java.util.Properties p = new java.util.Properties();
  String nm = (String) NAMES.get(u);
  if (nm != null) p.setProperty("name", nm);
  p.setProperty("quiet", QUIET.containsKey(u) ? "true" : "false");''', '''public static synchronized java.util.Properties snap(String k) {{
  long[] d = (long[]) DATA.get(k);
  if (d == null) return null;
  java.util.Properties p = new java.util.Properties();
  Object ou = OWNER.get(k);
  String nm = ou == null ? null : (String) NAMES.get(ou);
  if (nm != null) p.setProperty("name", nm);
  p.setProperty("quiet", QUIET.containsKey(k) ? "true" : "false");''')
rep('''public static void saveNow(java.util.UUID u) {{
  try {{
    java.util.Properties p = snap(u);
    if (p == null) return;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyySkills"); }} finally {{ out.close(); }}
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not save skills for " + u + ": " + t); }}
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  synchronized (IO) { saveNow(u); }
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    save(u);
  }
}""", sto))''', '''public static void saveNow(String k) {{
  try {{
    java.util.Properties p = snap(k);
    if (p == null) return;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyySkills"); }} finally {{ out.close(); }}
    java.nio.file.Files.move(tmp, DIR.resolve(k + ".properties"), new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not save skills for " + k + ": " + t); }}
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void save(String k) {
  synchronized (IO) { saveNow(k); }
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    it.remove();
    save(k);
  }
}""", sto))''')

# publishOnline: "in memory" = the ACTIVE profile's data is loaded
rep('''      if (DATA.containsKey(u)) {{ publish(u); continue; }}''', '''      if (DATA.containsKey(pkey(u))) {{ publish(u); continue; }}''')

# add / owes / payOwed resolve the key ONCE per award (gain2) so one award never spans two profiles
rep('''public static long[] add(java.util.UUID u, String name, int skill, long amount) {{
  long[] d = data(u);
  long[] ba = bump(d, skill, amount);
  if (name != null) NAMES.put(u, name);
  DIRTY.put(u, Boolean.TRUE);''', '''public static long[] addK(String k, java.util.UUID u, String name, int skill, long amount) {{
  long[] d = dataK(k, u);
  long[] ba = bump(d, skill, amount);
  if (name != null) NAMES.put(u, name);
  DIRTY.put(k, Boolean.TRUE);''')
rep('''public static boolean owes(java.util.UUID u, int skill) {{
  long[] d = data(u);''', '''public static boolean owesK(String k, java.util.UUID u, int skill) {{
  long[] d = dataK(k, u);''')
rep('''public static long[] payOwed(java.util.UUID u, int skill) {
  long[] d = data(u);
  long[] res = payGuarded(u, skill, d);
  if (res == null) return null;
  if (res[4] != 0L) DIRTY.put(u, Boolean.TRUE);''', '''public static long[] payOwedK(String k, java.util.UUID u, int skill) {
  long[] d = dataK(k, u);
  long[] res = payGuarded(u, skill, d);
  if (res == null) return null;
  if (res[4] != 0L) DIRTY.put(k, Boolean.TRUE);''')
rep('''public static boolean toggleQuiet(java.util.UUID u) {
  data(u);
  boolean q;
  if (QUIET.remove(u) != null) q = false; else { QUIET.put(u, Boolean.TRUE); q = true; }
  DIRTY.put(u, Boolean.TRUE);
  return q;
}''', '''public static boolean toggleQuiet(java.util.UUID u) {
  String k = pkey(u);
  dataK(k, u);
  boolean q;
  if (QUIET.remove(k) != null) q = false; else { QUIET.put(k, Boolean.TRUE); q = true; }
  DIRTY.put(k, Boolean.TRUE);
  return q;
}''')
# quiet readers (SkillMsg.note, Perks.doubled)
rep('''  if ({PKG}.SkillStore.QUIET.containsKey(u)) return;''', '''  if ({PKG}.SkillStore.quiet(u)) return;''', count=2)

# gain2: one key for the whole award
rep('''  java.util.UUID u = pr.getUuid();
  String name = null;
  try {{ name = pr.getUsername(); }} catch (Throwable t) {{ }}
  long[] r = {PKG}.SkillStore.add(u, name, skill, amount);
  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
  long[] paid = null;
  if ({PKG}.SkillStore.owes(u, skill)) paid = {PKG}.SkillStore.payOwed(u, skill);''', '''  java.util.UUID u = pr.getUuid();
  String k = {PKG}.SkillStore.pkey(u);
  String name = null;
  try {{ name = pr.getUsername(); }} catch (Throwable t) {{ }}
  long[] r = {PKG}.SkillStore.addK(k, u, name, skill, amount);
  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
  long[] paid = null;
  if ({PKG}.SkillStore.owesK(k, u, skill)) paid = {PKG}.SkillStore.payOwedK(k, u, skill);''')

# ---------------------------------------------------------------- SkillClass: class:<uuid> vs profile:class:<uuid>
rep('''scls.addMethod(CtNewMethod.make("""
public static int slot(java.util.UUID u) {
  return slotOfClass(className(u));
}""", scls))
''', '''scls.addMethod(CtNewMethod.make("""
public static int slot(java.util.UUID u) {
  return slotOfClass(className(u));
}""", scls))
# 0.3.2: false only while SkyyProfiles publishes the active profile's class (profile:class:<uuid>) and SkyyClasses' class:<uuid> does not
# match it yet (right after a profile switch) - then nothing class-based may write into the (new) profile. No profile:class key (no
# SkyyProfiles, or a profile without a class) = true, exactly the 0.3.1 behaviour.
# BOUNDED (review fix): SINCE = UUID -> Long ms the current mismatch was first seen (Perks.tick asks every second, so it starts within
# 1 s of a switch); after GRACE_MS it fails OPEN (true = class:<uuid> decides again, the 0.3.1 behaviour) and warns once per mismatch
# (GAVEUP). A match, a new epoch (Perks.switched) or a disconnect (Acro.retainOnline) resets both, so every switch gets a fresh grace.
scls.addField(CtField.make("public static final long GRACE_MS = 10000L;", scls))
scls.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SINCE = new java.util.concurrent.ConcurrentHashMap();", scls))
scls.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap GAVEUP = new java.util.concurrent.ConcurrentHashMap();", scls))
scls.addMethod(CtNewMethod.make("""
public static void resync(java.util.UUID u) {
  if (SINCE.isEmpty() && GAVEUP.isEmpty()) return;
  SINCE.remove(u);
  GAVEUP.remove(u);
}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static boolean overdue(java.util.UUID u, String pc, String c) {{
  long now = System.currentTimeMillis();
  Object first = SINCE.putIfAbsent(u, Long.valueOf(now));
  if (first == null) return false;
  if (now - ((Long) first).longValue() < GRACE_MS) return false;
  if (GAVEUP.putIfAbsent(u, Boolean.TRUE) == null) {{
    {PKG}.SkillCfg.warn("class:" + u + " (SkyyClasses) is " + (c == null ? "not set" : c) + " but profile:class:" + u + " (SkyyProfiles) is " + pc
      + " for " + (GRACE_MS / 1000L) + " s - SkyyClasses is not following the profile (SkyyProfiles needs SkyyClasses 0.1.3+). Combat XP, the class"
      + " damage perk and the legacy Combat move follow class:" + u + " again for this player until the next profile switch.");
  }}
  return true;
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static boolean consistent(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("profile:class:" + u.toString());
    if (!(o instanceof String)) {{ resync(u); return true; }}
    String pc = ((String) o).trim();
    if (pc.length() == 0) {{ resync(u); return true; }}
    String c = className(u);
    if (c != null && c.equalsIgnoreCase(pc)) {{ resync(u); return true; }}
    return overdue(u, pc, c);
  }} catch (Throwable t) {{ return true; }}
}}""", scls))
''')
rep('''  String c = className(u);
  if (c == null) {{ tellOnce(pr, 2, "Choose a class''', '''  if (!consistent(u)) {{ tellOnce(pr, 16, "Your class is still switching to this profile's class - combat XP resumes in a moment."); return -1; }}
  String c = className(u);
  if (c == null) {{ tellOnce(pr, 2, "Choose a class''')

# ---------------------------------------------------------------- Perks: epoch check (contract rule 3/4), migration by key
rep('''perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DDMSG = new java.util.concurrent.ConcurrentHashMap();", perk))
''', '''perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DDMSG = new java.util.concurrent.ConcurrentHashMap();", perk))
perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", perk))   # 0.3.2: UUID -> Long last profile:epoch seen
''')
rep('''public static void migrate({PR} pr, java.util.UUID u, int slot) {{
  long x = {PKG}.SkillStore.moveLegacy({PKG}.SkillStore.data(u), slot);
  if (x <= 0L) return;
  {PKG}.SkillStore.DIRTY.put(u, Boolean.TRUE);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("moved legacy Combat XP " + x + " of " + u + " to " + {PKG}.SkillDefs.NAMES[slot]);''', '''public static void migrate({PR} pr, java.util.UUID u, int slot) {{
  String k = {PKG}.SkillStore.pkey(u);
  long x = {PKG}.SkillStore.moveLegacy({PKG}.SkillStore.dataK(k, u), slot);
  if (x <= 0L) return;
  {PKG}.SkillStore.DIRTY.put(k, Boolean.TRUE);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("moved legacy Combat XP " + x + " of " + k + " to " + {PKG}.SkillDefs.NAMES[slot]);''')
rep('''# once per second per player from AcroSys (world thread): first tick of the session or class change -> republish skill:<uuid>,''',
    '''# 0.3.2 contract rule 3: profile:epoch:<uuid> (Long, +1 on every profile switch / creation; -1 here = no SkyyProfiles)
perk.addMethod(CtNewMethod.make(f"""
public static long epoch(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) return ((Number) o).longValue();
  }} catch (Throwable t) {{ }}
  return -1L;
}}""", perk))
# true when the epoch differs from the one seen on this player's previous 1 s tick (the first tick of a session only records it:
# Perks.tick republishes on a session's first tick anyway). Without SkyyProfiles the epoch is always -1 -> never true.
perk.addMethod(CtNewMethod.make("""
public static boolean epochChanged(java.util.UUID u) {
  long e = epoch(u);
  Object last = EPOCH.put(u, Long.valueOf(e));
  return last != null && ((Long) last).longValue() != e;
}""", perk))
# world thread, right after an epoch change (AcroSys, before the flush / movement sync / perk tick of the same second): skill:<uuid>
# now describes the new profile (data(u) resolves the new pkey; its file is loaded here on first use); the +XP line still pending
# and the once-per-session hints belonged to the old profile; the class-sync grace (SkillClass.SINCE / GAVEUP) starts over.
# Review note (kept on purpose): that first load of the new profile's small players/<pkey>.properties is a synchronous read on this
# world thread, exactly like PublishTask for a new session. It cannot move to the ticker (HytaleServer.SCHEDULED_EXECUTOR is ONE
# thread shared by every mod - no player-file I/O there, 0.2 design), and deferring only this publish would not help: the flush /
# movement sync / MAX modifiers of the same second read the new profile's levels anyway, and a non-blocking read would show level 0
# for a moment (health MAX modifier drop). Profile switches are manual and rare; revisit only if they become frequent.
perk.addMethod(CtNewMethod.make(f"""
public static void switched(java.util.UUID u) {{
  {PKG}.SkillMsg.PEND.remove(u);
  {PKG}.SkillClass.TOLD.remove(u);
  {PKG}.SkillClass.resync(u);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("profile switch: " + u + " now uses skills of " + {PKG}.SkillStore.pkey(u));
}}""", perk))
# once per second per player from AcroSys (world thread): first tick of the session or class change -> republish skill:<uuid>,''')
# consistent() is asked every second (also without a class) so its fail-open grace clock starts within 1 s of a mismatch
rep('''    if (cs >= 0) migrate(pr, u, cs);''', '''    boolean synced = {PKG}.SkillClass.consistent(u);
    if (cs >= 0 && synced) migrate(pr, u, cs);''')

# ---------------------------------------------------------------- Acro: drop the old profile's unpaid progress on a switch
rep('''acro.addMethod(CtNewMethod.make("""
public static void reset(double[] s) {
  s[3] = 0.0; s[5] = 0.0; s[6] = 0.0; s[8] = 0.0; s[18] = 0.0; s[23] = 0.0;
}""", acro))
''', '''acro.addMethod(CtNewMethod.make("""
public static void reset(double[] s) {
  s[3] = 0.0; s[5] = 0.0; s[6] = 0.0; s[8] = 0.0; s[18] = 0.0; s[23] = 0.0;
}""", acro))
# 0.3.2 profile switch: XP earned on the old profile but not paid yet is dropped (at most one second of movement / one landing) so it
# never lands on the new profile; the position is re-seeded (a switch usually teleports to the profile's island). The jump / dodge
# edges and the per-minute cap ring stay: they describe the physical player, not the save.
acro.addMethod(CtNewMethod.make("""
public static void profileReset(double[] s) {
  s[3] = 0.0; s[8] = 0.0; s[10] = 0.0; s[11] = 0.0;
  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0;
}""", acro))
''')
rep('''    {PKG}.Perks.DDMSG.keySet().retainAll(online);
''', '''    {PKG}.Perks.DDMSG.keySet().retainAll(online);
    {PKG}.Perks.EPOCH.keySet().retainAll(online);
    {PKG}.SkillClass.SINCE.keySet().retainAll(online);
    {PKG}.SkillClass.GAVEUP.keySet().retainAll(online);
''')
# AcroSys: the epoch check runs in the existing 1 s block, BEFORE flush (XP), bonuses (movement source + sync) and Perks.tick
# (skill:<uuid> class check, stat modifiers), so all three already use the new profile in the same second (contract rule 4)
rep('''    s[14] = 0.0;
    {PKG}.Acro.flush(pr, s, now);''', '''    s[14] = 0.0;
    if ({PKG}.Perks.epochChanged(u)) {{ {PKG}.Acro.profileReset(s); {PKG}.Perks.switched(u); }}
    {PKG}.Acro.flush(pr, s, now);''')

# ---------------------------------------------------------------- CombatDmgSys: no class perk while the class is still switching
rep('''    int slot = {PKG}.SkillClass.slot(u);
    if (slot < 0) return;
    java.util.function.Function f = {PKG}.SkillClass.allowedFn();''', '''    int slot = {PKG}.SkillClass.slot(u);
    if (slot < 0) return;
    if (!{PKG}.SkillClass.consistent(u)) return;
    java.util.function.Function f = {PKG}.SkillClass.allowedFn();''')

# ---------------------------------------------------------------- leaderboard: one row per profile file
rep('''# rows: Object[]{name, Long xp, uuidString}, sorted, all players on disk + in memory; cached 30s
''', '''# 0.3.2: a row per profile file / profile key; profile N >= 2 ("<uuid>-pN") shows "name (profile N)" (a UUID string never contains "-p")
top.addMethod(CtNewMethod.make("""
public static String label(String nm, String key) {
  if (key == null) return nm;
  int p = key.indexOf("-p");
  if (p <= 0 || p + 2 >= key.length()) return nm;
  return nm + " (profile " + key.substring(p + 2) + ")";
}""", top))
# rows: Object[]{name, Long xp, profile key (0.3.2; = uuidString for profile 1)}, sorted, all profiles on disk + in memory; cached 30s
''')
rep('''        m.put(us, new Object[] {{ nm == null ? us.substring(0, 8) : nm, Long.valueOf(x), us }});''',
    '''        m.put(us, new Object[] {{ label(nm == null ? us.substring(0, 8) : nm, us), Long.valueOf(x), us }});''')
rep('''    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    java.util.UUID u = (java.util.UUID) e.getKey();
    long[] d = (long[]) e.getValue();
    String nm = (String) {PKG}.SkillStore.NAMES.get(u);
    m.put(u.toString(), new Object[] {{ nm == null ? u.toString().substring(0, 8) : nm, Long.valueOf(d[skill]), u.toString() }});''',
    '''    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String k = (String) e.getKey();
    long[] d = (long[]) e.getValue();
    Object ou = {PKG}.SkillStore.OWNER.get(k);
    String nm = ou == null ? null : (String) {PKG}.SkillStore.NAMES.get(ou);
    m.put(k, new Object[] {{ label(nm == null ? (k.length() > 8 ? k.substring(0, 8) : k) : nm, k), Long.valueOf(d[skill]), k }});''')
rep('''top.addMethod(CtNewMethod.make("""
public static int rankOf(java.util.ArrayList rows, java.util.UUID u) {
  String s = u.toString();
  for (int i = 0; i < rows.size(); i++) if (s.equals(((Object[]) rows.get(i))[2])) return i + 1;
  return 0;
}""", top))''', '''top.addMethod(CtNewMethod.make(f"""
public static int rankOf(java.util.ArrayList rows, java.util.UUID u) {{
  String s = {PKG}.SkillStore.pkey(u);
  for (int i = 0; i < rows.size(); i++) if (s.equals(((Object[]) rows.get(i))[2])) return i + 1;
  return 0;
}}""", top))''')
rep('''    boolean me = u.toString().equals(e[2]);''', '''    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);''')

# ---------------------------------------------------------------- skill args: "shaman" replaces the removed "berserking" (review fix)
# SkillDefs.indexOf("shaman") = the Shaman placeholder slot (CLASSES match); "berserking" matches nothing since 0.3.1 renamed the slot.
rep('''or a class skill: archery, swordsmanship, assassination, berserking, sorcery."''',
    '''or a class skill: archery, swordsmanship, assassination, shaman, sorcery."''')
rep('''| archery | swordsmanship | assassination | berserking | sorcery"''', '''| archery | swordsmanship | assassination | shaman | sorcery"''', count=2)

# ---------------------------------------------------------------- manifest
rep('''Level ups pay SkyyCoins. /skills. Zero dependencies."''', '''Level ups pay SkyyCoins. /skills. Per profile with SkyyProfiles (optional). Zero dependencies."''')

# ---------------------------------------------------------------- sanity
for bad in ("DATA.get(u)", "DATA.put(u,", "DATA.containsKey(u)", "QUIET.containsKey(u)", "QUIET.put(u,", "QUIET.remove(u)",
            "DIRTY.put(u,", 'u.toString() + ".properties', "SkillStore.add(", "SkillStore.owes(", "SkillStore.payOwed(",
            "readFile(u)", "snap(u)", "saveNow(u)", "save(u)"):
    assert bad not in s, "per-player storage still keyed by UUID: " + bad
assert s.count('Object f = bridge().get("profile:fn:key");') == 1
assert s.count("Perks.epochChanged(u)") == 1
assert "EPOCH.keySet().retainAll(online)" in s
assert "SINCE.keySet().retainAll(online)" in s and "GAVEUP.keySet().retainAll(online)" in s
assert s.count("SkillClass.consistent(u)") == 2 and s.count("if (!consistent(u))") == 1   # Perks.tick, CombatDmgSys, killSlot
assert "SkillClass.resync(u);" in s and "return overdue(u, pc, c);" in s
assert "berserking" not in s.split("\n# ================= SkillDefs", 1)[1], "a player-facing string still says berserking"
assert 'VERSION = "0.3.2"' in s and "0.3.2: per-profile storage (tools/PROFILES-CONTRACT.md)" in s
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.3.1
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
