"""Derive SkyySkills/build_skyyskills_0.4.30.py from the LIVE generated SkyySkills/build_skyyskills_0.4.29.py (= the tools/deploy_set.py SET
pin; 0.4.29 came from 0.4.28 by tools/skills_0_4_29_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_29_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.29
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_30_patch.py   then   python SkyySkills/build_skyyskills_0.4.30.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.30.py --dir tools/dev/scratch/<yours>/h   (bare JVM, -Xverify:all)

0.4.30 = THE REGEN BLOCK BRIDGE for the Soul Orb (SkyyArmory 0.1.19; Skyy LOCKED 2026-10-04 "no natural Mana regen while any Binding is
active - but Mana Steal still works", research/classes/Priest.md "How soul Bindings work" 6).
  - NEW bridge skill:fn:regenblock (RegenBlockFn, java.lang types only, any thread, never throws):
      apply(Object[] { UUID player, Number untilMs })  -> Boolean.TRUE   block that player's natural Mana regen until untilMs (wall clock);
                                                                          0 / a past time = clear. At most BLOCK_MAX_MS (10 s) ahead - a
                                                                          caller that stops renewing (crash, unload) never blocks for long.
      apply(UUID) or apply(Object[] { UUID })          -> Long  ms the block still runs (0 = none)
      anything else                                    -> null
    SkyyArmory 0.1.19 renews it every Binding pulse (until = the pulse + 2 s) and clears it when the Bindings end.
  - ManaRegen.tick (the 0.2 s Mana regen pulse, world thread): while blocked, SkyySkills adds NOTHING (no in-combat refill, no Mana Regen %
    boosts, no charging refill - 0.4.13 refills what vanilla withholds while charging, and the soul hold IS a charge) and takes back the part
    of vanilla's own refill that ran this pulse (rates()[1]: the vanilla entries whose conditions all pass; 0 while charging - vanilla's
    ChargingCondition already stops it). The combat state (skill:fn:combat) is still recorded first. Mana Steal (SkyyGear), Mana on hit
    (ManaHit) and any direct Mana gift are NOT regen and are never touched.
  - Acro.retainOnline prunes the block map like CLK / CMB / CARRY. Shutdown removes the bridge entry.
  No config key, no saved data, no migration, no command. Without SkyyArmory 0.1.19 nobody calls it: every path is 0.4.29's.
  Rolling back to 0.4.29 is safe (the Soul Orb then binds with SkyySkills' regen on - its start line says so).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.29.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.30.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.29"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.29"' in s and "derived from the generated 0.4.28 by tools/skills_0_4_29_patch.py" in s, "not the live generated 0.4.29"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "skill:fn:regenblock" not in s, "0.4.29 already has the regen block"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.29 - build script (derived from the generated 0.4.28 by tools/skills_0_4_29_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.30 - build script (derived from the generated 0.4.29 by tools/skills_0_4_30_patch.py - edit the patch, not this file;
0.4.29 was derived from the generated 0.4.28 by tools/skills_0_4_29_patch.py; ''')
rep('''0.4.29: THE PET XP HOOK (research/cloud/Pet-Core-Spec.md 1 "XP in"; full notes in tools/skills_0_4_29_patch.py). After every XP award
''', '''0.4.30: THE REGEN BLOCK BRIDGE (SkyyArmory 0.1.19's Soul Orb: "no natural Mana regen while any Binding is active"; full notes in
  tools/skills_0_4_30_patch.py). skill:fn:regenblock (RegenBlockFn): Object[]{UUID, Long untilMs} blocks that player's natural Mana regen
  until then (0 = clear; at most 10 s ahead); while blocked ManaRegen.tick adds nothing and takes back vanilla's own refill of that pulse;
  Mana Steal / Mana on hit untouched. No config key, saved data, migration or command. CHECKED: SkyySkills/test_skyyskills_0.4.30.py.
0.4.29: THE PET XP HOOK (research/cloud/Pet-Core-Spec.md 1 "XP in"; full notes in tools/skills_0_4_29_patch.py). After every XP award
''')
rep('VERSION = "0.4.29"', 'VERSION = "0.4.30"')

# ---------------------------------------------------------------------------------------------------------------- the class + the fields
rep('''cmbf = pool.makeClass(PKG + ".CombatFn")
''', '''cmbf = pool.makeClass(PKG + ".CombatFn")
rbf  = pool.makeClass(PKG + ".RegenBlockFn")          # 0.4.30: skill:fn:regenblock (SkyyArmory 0.1.19's Soul Bindings)
''')
rep('''mrg.addField(CtField.make("public static final long CARRY_SLACK = 1000000000L;", mrg))   # 1 s of slack on the late-hit / fresh-hit windows (ns)
''', '''mrg.addField(CtField.make("public static final long CARRY_SLACK = 1000000000L;", mrg))   # 1 s of slack on the late-hit / fresh-hit windows (ns)
# 0.4.30: BLOCK = UUID -> Long untilMs (skill:fn:regenblock: no natural Mana regen until then); the counters for /skills mana + the harness
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BLOCK = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static final long BLOCK_MAX_MS = 10000L;", mrg))
mrg.addField(CtField.make("public static volatile long BLOCKED = 0L;", mrg))
mrg.addField(CtField.make("public static volatile double TAKEN_BACK = 0.0;", mrg))
''')

# ---------------------------------------------------------------------------------------------------------------- block / blocked + the tick
rep('''# world thread, every tick from AcroSys (before its 1 s gate): one pulse per PULSE seconds (vanilla's own interval), at most 1 s at a time
''', '''# 0.4.30: the regen block (skill:fn:regenblock). block(u, until): until <= now = clear, else at most BLOCK_MAX_MS ahead; blockLeft = ms left
# (an expired entry is dropped). Any thread, no I/O.
mrg.addMethod(CtNewMethod.make("""
public static boolean block(java.util.UUID u, long until, long now) {
  if (u == null) return false;
  if (until <= now) { BLOCK.remove(u); return true; }
  long cap = now + BLOCK_MAX_MS;
  BLOCK.put(u, Long.valueOf(until > cap ? cap : until));
  return true;
}""", mrg))
mrg.addMethod(CtNewMethod.make("""
public static long blockLeft(java.util.UUID u, long now) {
  if (u == null) return 0L;
  Object o = BLOCK.get(u);
  if (!(o instanceof Long)) return 0L;
  long left = ((Long) o).longValue() - now;
  if (left <= 0L) { BLOCK.remove(u, o); return 0L; }
  return left;
}""", mrg))
# world thread, every tick from AcroSys (before its 1 s gate): one pulse per PULSE seconds (vanilla's own interval), at most 1 s at a time
''')
rep('''    combat(u, cb, ref, now, rv);   // 0.4.13: skill:fn:combat - the entries, conditions and clock the refill below uses (own try)
    int f = IN_COMBAT;
''', '''    combat(u, cb, ref, now, rv);   // 0.4.13: skill:fn:combat - the entries, conditions and clock the refill below uses (own try)
    if (blockLeft(u, System.currentTimeMillis()) > 0L) {{   // 0.4.30: a Soul Binding holds - no natural regen at all (Mana Steal is no regen)
      BLOCKED = BLOCKED + 1L;
      float[] br = rates(cb, ref, now, rv);
      float back = br[1] * secs;   // vanilla's own refill that ran this pulse (0 while charging: its ChargingCondition stops it)
      float have = v.get();
      if (back > have) back = have;
      if (back > 0.0f) {{ m.subtractStatValue(mi, back); TAKEN_BACK = TAKEN_BACK + (double) back; }}
      return;
    }}
    int f = IN_COMBAT;
''')
# the tick is an f-string: every brace of the block above is doubled
assert s.count("if (blockLeft(u, System.currentTimeMillis()) > 0L) {{   // 0.4.30") == 1

# ---------------------------------------------------------------------------------------------------------------- the bridge Function
rep('''# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''', '''# ================= skill:fn:regenblock (0.4.30): SkyyArmory 0.1.19's Soul Bindings - no natural Mana regen while any Binding holds
#   apply(Object[] { UUID player, Number untilMs }) -> Boolean.TRUE (blocked until then; 0 / past = clear; at most 10 s ahead)
#   apply(UUID) / apply(Object[] { UUID })         -> Long ms the block still runs (0 = none);   anything else -> null
rbf.addInterface(pool.get("java.util.function.Function"))
rbf.addConstructor(CtNewConstructor.make("public RegenBlockFn() { }", rbf))
rbf.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    long now = System.currentTimeMillis();
    if (arg instanceof java.util.UUID) return Long.valueOf({PKG}.ManaRegen.blockLeft((java.util.UUID) arg, now));
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 1 || !(a[0] instanceof java.util.UUID)) return null;
    java.util.UUID u = (java.util.UUID) a[0];
    if (a.length == 1) return Long.valueOf({PKG}.ManaRegen.blockLeft(u, now));
    if (!(a[1] instanceof Number)) return null;
    return Boolean.valueOf({PKG}.ManaRegen.block(u, ((Number) a[1]).longValue(), now));
  }} catch (Throwable t) {{ return null; }}
}}""", rbf))

# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''')
rep('''    {PKG}.ManaRegen.CARRY.keySet().retainAll(online);   // 0.4.13 fix F1's per-player record
''', '''    {PKG}.ManaRegen.CARRY.keySet().retainAll(online);   // 0.4.13 fix F1's per-player record
    {PKG}.ManaRegen.BLOCK.keySet().retainAll(online);   // 0.4.30: the regen blocks of players who left
''')
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:combat", new {PKG}.CombatFn());   // 0.4.13: the combat state (SkyyHud's Combat widget)
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:combat", new {PKG}.CombatFn());   // 0.4.13: the combat state (SkyyHud's Combat widget)
  {PKG}.SkillStore.bridge().put("skill:fn:regenblock", new {PKG}.RegenBlockFn());   // 0.4.30: SkyyArmory's Soul Bindings block natural Mana regen
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:combat"); }} catch (Throwable t) {{ }}   // 0.4.13
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:combat"); }} catch (Throwable t) {{ }}   // 0.4.13
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:regenblock"); }} catch (Throwable t) {{ }}   // 0.4.30
''')
rep('''+ skill:fn:manaregen + skill:fn:combat; trees bridge on''', '''+ skill:fn:manaregen + skill:fn:combat + skill:fn:regenblock (SkyyArmory's Soul Bindings: no natural Mana regen while bound); trees bridge on''')
rep('''          ctb, cpw, mhit, sdef, dsy, dsyu, mhs, pmig):   # 0.4.25:''', '''          ctb, cpw, mhit, sdef, dsy, dsyu, mhs, pmig,
          rbf):   # 0.4.30: + RegenBlockFn; 0.4.25:''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.30 adds no system and no command"
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.29 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.29,", len(_gone), "0.4.29 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
