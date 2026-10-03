"""Derive SkyySkills/build_skyyskills_0.4.13.py from the LIVE generated SkyySkills/build_skyyskills_0.4.12.py (= the tools/deploy_set.py SET
pin; 0.4.12 came from 0.4.11 by tools/skills_0_4_12_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_12_patch.py: rep(old, new) with asserted single anchors, newline-agnostic;
0.4.12 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_13_patch.py   then   python SkyySkills/build_skyyskills_0.4.13.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.13.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0413/, deleted afterwards)

0.4.13 = THE COMBAT STATE ON THE BRIDGE, for the SkyyHud 0.3.12 Combat widget (Skyy 2026-10-02: "id add a widget for combat indicator
too. goes red when in combat. and id either do a small count down, or use the animation to indicate how close you are to being out of
combat."; OPEN-QUESTIONS LOCKED 2026-10-02: "same rule as the in-combat Mana regen: 6 s after taking damage"), + THE FIX ROUND below
(cross-check 2026-10-02 NOT READY - fixed in place before the first deploy, the version stays 0.4.13).

ONE SOURCE OF TRUTH = the in-combat test the 0.4.12 Mana regen already runs (ManaRegen.state / rates): IN COMBAT = a NoDamageTaken
condition of one of the positive Additive regen entries of the player's Mana value FAILS (Condition.eval - vanilla's 6 s combat pause:
NoDamageTakenCondition.eval0 = TimeUtil.compareDifference(DamageDataComponent.lastDamageTime, now, Delay) >= 0) at the world's own clock
(TimeResource.getNow - the clock DamageSystems$TrackLastDamage stamps the hit with), read on the world thread at the Mana regen's own
0.2 s pulse. Exactly the entries rates() counts (baseOf > 0), exactly the conditions state() keys on, exactly the instant tick() uses.

  ManaRegen (changed: + 8 methods, + 10 fields, tick, state, rates, amount, text):
    tick: at each pulse (the existing CLK clock) it reads the world's clock FIRST, carries stamps from another world's clock (carry, FIX
          F1 below), reads the Mana value / the regen entries and calls combat(u, cb, ref, now, rv) - before the no-Mana-pool return and
          the full-Mana return, so the combat state works for every player and setting - then the refill runs on the SAME now / rv:
          amount(rates(cb, ref, now, rv), pct, f, secs, cur, max). The 0.4.12 "in-combat 0 % and no boosts" early return is gone (charging
          out of combat refills even then); the numbers are 0.4.12's everywhere but while charging (the harness replays a pulse sequence
          through the real tick() on the 0.4.12 and the 0.4.13 jar: identical Mana after every pulse outside the charging window).
    combatLeft(acc, ref, now, rv) -> long ms: for every NoDamageTaken condition (of those entries) that FAILS now: its Delay minus the
          time since the last hit (DamageDataComponent.lastDamageTime - the component the condition reads - until now in ns), rounded UP
          to whole ms, at least 1 and at most the Delay while the engine says in combat; the largest of them; 0 = no such condition
          fails = out of combat. So "> 0" IS the Mana regen's in-combat test, by construction. Sets WINDOW (the Delay in ms).
    delayOf(cond, acc, ref, last) -> long ns: the condition's Delay. NoDamageTakenCondition.delay is protected (AGENT-BRIEF: protected
          engine members only from a subclass on this), so it is ASKED FROM THE CONDITION ITSELF: the smallest d with
          cond.eval0(acc, ref, last + d) true (doubling from 1 ms, then halving to the nanosecond; at most 1 hour) = exactly the Delay the
          engine compares with. Cached per condition object (NDLY, cleared above 64 entries); needs a real hit (last != Instant.MIN),
          which every in-combat state has. -1 = not found (then the countdown shows 1 ms while the engine says in combat).
    combat(u, acc, ref, now, rv): world thread, every pulse: CMB.put(u, {ms left, System.currentTimeMillis()}) while in combat, else
          CMB.remove(u) (so the map only holds players in combat). Own try: a failure there can never stop the Mana refill (logged once).
    combatNow(u, wall) -> long ms (ANY thread, memory only): the last pulse's value counted down on the wall clock; while that pulse is
          at most STALE_MS (1 s) old it never drops below 1 - only the next pulse (the Mana regen's own test) ends combat, so the bridge
          never says "out" while the refill still runs at the in-combat rate; a player no longer ticked (loading screen, world switch,
          left) runs out on the wall clock. Unknown / offline / never in combat = 0.
  CombatFn (new) = the bridge Function skill:fn:combat (java.lang types only, never throws, any thread, one ConcurrentHashMap read):
      apply(java.util.UUID player)      -> Long  ms left in combat; 0 = out of combat (also unknown / offline players)
      apply("window")                   -> Long  the whole combat window in ms (vanilla 6000 = the Mana regen's NoDamageTaken Delay, read
                                                 from the engine condition); 0 until somebody was in combat since the server started
      apply(new Object[] { UUID })      -> Long  the same as apply(UUID); new Object[] { "window" } the same as apply("window")
      anything else                     -> null
    A bar = left / window; a countdown = ceil(left / 1000) s. The value moves at the Mana regen pulse (5 a second) and counts down
    smoothly on the wall clock in between, so any HUD refresh rate reads a correct number.
  SkyySkillsPlugin (changed): setup() puts skill:fn:combat right after skill:fn:manaregen (+ the ready line names it); shutdown()
    removes it.

THE FIX ROUND (cross-check 2026-10-02 + Skyy's LOCKED charging line; version stays 0.4.13 - it was never deployed):
  F1 (blocking) EVERY WORLD HAS ITS OWN CLOCK: TimeResource.now is saved per world (resources/Time.json "Now"; live 2026-10-02: default
     09:12:57, islands 03:13 - 08:24) and the player's DamageDataComponent (not saved, kept in the Holder) travels to the next world with
     its stamps unchanged. A hit in 'default' then /island compared a 09:12 stamp with a 03:13 clock: "in combat" (and the in-combat Mana
     rate, and every NoDamageTaken pause - an NPC-style Health 15 s too) for hours, combatLeft = the whole window; the reverse (small ->
     big clock) cleared combat at once = vanilla's own teleport-to-regen hole. The Charging condition reads lastChargeTime the same way
     (a charge released in 'default' kept "charging" - no vanilla Mana refill at all - for hours on an island), OutOfCombat reads
     lastCombatAction. FIX (ManaRegen.carry, world thread, at every Mana regen pulse, own try, logged once):
       the record CARRY: UUID -> {world name, that world's clock now, System.nanoTime() of the pulse, the world's time dilation, the three
       stamps after this pulse} (elapsed since a stamp on that clock = clock - stamp). The first pulse in ANOTHER world (name differs)
       rewrites a stamp that is still the old world's - the same Instant as recorded, or a hit in the old world after its last pulse (later
       than the recorded clock by at most the wall gap x the old dilation + 1 s, and not inside this world's own window now - gap x
       dilation - 1 s .. now, which is where a FRESH hit here lies: left alone) - to now - the REAL time since it, converted:
       real = (old clock - stamp) / old dilation + (nanoTime now - nanoTime of that pulse); new stamp = now - real x this world's
       dilation. THE CLOCK RATE (bytecode, HytaleServer.jar 2026-10-02, asserted by the build): TickingThread.run ticks with the
       MEASURED System.nanoTime() step / 1e9 (no fixed step, no cap), World.tick multiplies it by TimeResource.getTimeDilationModifier()
       (1.0 unless /time dilation set it; not saved) before Store.tick, TimeSystem.tick adds (long) (dt x 1e9f) ns to TimeResource.now;
       a paused world ticks only RunWhenPaused systems (not TimeSystem, not AcroSys) - so a world's clock = real time x its dilation
       while it runs, and nothing moves it backwards (setNow: only the codec). More than 1 hour real (CARRY_CAP) = Instant.MIN (the
       engine's "never hit": TimeUtil.compareDifference passes it for every Delay). And always: a stamp in the FUTURE of this world's
       clock (no record, a lost record, a recreated world) = now (at most one window, never stuck). Applied to lastDamageTime,
       lastCombatAction and lastChargeTime alike; only public engine members (getExternalData / getWorld / getName, the three get / set
       pairs, getTimeDilationModifier). The combat state and the refill of the same pulse already read the carried stamp.
  F2 (low) Acro.retainOnline prunes ManaRegen.CMB (and the new CARRY) beside CLK.
  CHARGING (Skyy 2026-10-02, LOCKED: "mana doesn't continue regening while charging an attack, id change that"): vanilla Mana.json's
     entry = +1 / 0.2 s if Alive, NoDamageTaken (6 s) and Charging (Inverse). state() now tells 3 = only an inverse Charging fails (its
     eval0 says the player IS charging: out of combat) and 4 = Charging + NoDamageTaken (charging in combat); a non-inverse Charging that
     fails stays "anything else" (2), and so does dead (Alive fails) - never while dead. rates() -> {base, out, in, chargeOut, chargeIn}:
     in counts states 1 and 4 (in combat, charging or not), chargeOut state 3. amount() adds chargeOut x (1 + MR / 100) = the whole
     out-of-combat refill vanilla withholds (its +1 / 0.2 s) + the same boosts the out-of-combat path adds; in combat the existing
     in-combat amount (F% of vanilla + boosts). Never on top of vanilla's own refill: vanilla pays only when every condition passes
     (Condition.allConditionsMet = state 0), SkyySkills pays the base only in states 1 / 3 / 4. /skills mana: ManaCmd's state line moved
     into ManaRegen.stateLine (pure) - "charging - Mana still regenerates: SkyySkills refills 6/s (vanilla pauses while you charge)",
     "IN COMBAT (vanilla's 6 s pause), charging - Mana still regenerates - ..."; text() says "Charging - Mana still regenerates (...)".
     No asset override (Mana.json stays vanilla: any server or mod change to it keeps working, nothing to clean up on uninstall).
  Every other class: byte-identical or the version string only (harness section F). No new row, command, setting, file, event binding or
  system; the player file format, every other bridge contract and the Server Setup action are unchanged.
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.12.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.13.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.12"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
# the source must be the generated 0.4.12 of the edited lineage
assert 'VERSION = "0.4.12"' in s and "derived from the generated 0.4.11 by tools/skills_0_4_12_patch.py" in s, "not the live generated 0.4.12"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "skill:fn:combat" not in s and "CombatFn" not in s and "cmbf" not in s and "combatLeft" not in s and "NDLY" not in s
assert "CARRY" not in s and "stateLine" not in s and "ChargingCondition" not in s and "carried(" not in s
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical: the ManaRegen registry methods + baseOf, vanillaRate + text() up to its charging
# sentence, compact / showAction / ManaRegenFn, AcroSys + everything after it up to the plugin (the commands: all of ManaCmd but its state
# line), the systems, the config rows, SPELL GEN, ClassCurve, Acro up to its CLK prune and after it
KEEP = [block("# ================= ManaRegen (0.4.12)", "# the entry's OWN engine conditions, one by one"),
        block("# vanilla's base Mana refill per second from the Mana stat asset", '  sb.append(". Never while charging.");'),
        block("# review fix R4: the action answer is shown by SkyyMenu", "# AcroSys: EntityTickingSystem on Player entities"),
        block("# AcroSys: EntityTickingSystem on Player entities", "      String st;\n"),
        block('      String hit = "";\n', "# ================= plugin ================="),
        block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= ECS systems", "# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)"),
        block("# ================= SkillDefs: names, icons, level table", "    {PKG}.ManaRegen.CLK.keySet().retainAll(online);"),
        block('  }} catch (Throwable t) {{ }}\n}}""", acro))\nacro.addMethod(CtNewMethod.make("""\npublic static boolean isFall(',
              "# ================= ManaRegen (0.4.12)")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.12 - build script (derived from the generated 0.4.11 by tools/skills_0_4_12_patch.py - edit the patch, not this file;
0.4.11 was derived''', '''"""SkyySkills 0.4.13 - build script (derived from the generated 0.4.12 by tools/skills_0_4_13_patch.py - edit the patch, not this file;
0.4.12 was derived from the generated 0.4.11 by tools/skills_0_4_12_patch.py; 0.4.11 was derived''')
HEAD_0413 = '''0.4.13: THE COMBAT STATE ON THE BRIDGE for the SkyyHud 0.3.12 Combat widget (Skyy 2026-10-02; full notes in tools/skills_0_4_13_patch.py).
  skill:fn:combat (CombatFn): apply(UUID) -> Long ms left in combat (0 = out of combat); apply("window") -> Long the whole window in ms
  (vanilla 6000; 0 until somebody was in combat since the start). In combat = EXACTLY the in-combat test of the Mana regen above: a
  NoDamageTaken condition of a positive Additive Mana regen entry fails on the world's clock (6 s after TAKING damage), read on the world
  thread at the Mana regen's own 0.2 s pulse (ManaRegen.tick -> combat, before any of its returns); the countdown = the condition's Delay
  (asked from the condition itself: the field is protected) minus the time since the last hit; between pulses it counts down on the wall
  clock and never reaches 0 before the next pulse says so. Memory only, any thread.
  FIX ROUND before the first deploy (cross-check 2026-10-02 NOT READY; the version stays 0.4.13):
  F1 every world keeps its own clock (TimeResource "Now", saved per world: live default ~09:12, islands 03:13 - 08:24) and the player's
     hit / combat / charge stamps (DamageDataComponent) travelled to the next world unchanged: a smaller clock kept you in combat (and
     "charging") for hours, a bigger one cleared combat at once. Now every Mana regen pulse records the world, its clock, the stamps and
     System.nanoTime() (ManaRegen.CARRY); the first pulse in another world rewrites a stamp that is still the old world's (the same
     Instant, or a hit there after its last pulse) to now - the REAL time since it (old clock time / old dilation + the wall time since
     that pulse, x this world's dilation: a world's clock = real time x its time dilation - TickingThread / World.tick / TimeSystem
     bytecode, asserted below); over 1 hour = Instant.MIN (never hit); a fresh hit in the new world is left alone; a stamp in the future
     of the world's clock = now.
  F2 Acro.retainOnline prunes ManaRegen.CMB (and CARRY) like CLK.
  MANA WHILE CHARGING (Skyy 2026-10-02, LOCKED): vanilla's Mana entry pauses while Charging; when the only failing conditions are an
     inverse Charging (out of combat) or Charging + NoDamageTaken (in combat), SkyySkills refills what vanilla withholds: the whole
     out-of-combat rate (vanilla's +1 / 0.2 s + the same boosts) or the in-combat rate. Never while dead, never on top of vanilla's own
     refill; /skills mana says "charging - Mana still regenerates".
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.13.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.12: THE CLASS''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_0413 + '''0.4.12: THE CLASS''')
rep('VERSION = "0.4.12"\n', 'VERSION = "0.4.13"\n')

# ---------------------------------------------------------------------------------------------------------------- the new class + fields
# (declared with the 0.4.12 classes: CombatFn reads ManaRegen.WINDOW / combatNow, compiled after them)
rep('''mcmd = pool.makeClass(PKG + ".ManaCmd", pool.get(APC))
''', '''mcmd = pool.makeClass(PKG + ".ManaCmd", pool.get(APC))
# 0.4.13: the combat state for other mods (skill:fn:combat - SkyyHud's Combat widget); "cfn" is SkillCraftFn
cmbf = pool.makeClass(PKG + ".CombatFn")
''')
rep('''mrg.addField(CtField.make("public static final float PULSE = 0.2f;", mrg))   # = vanilla Mana.json's 0.2 s regen interval
''', '''mrg.addField(CtField.make("public static final float PULSE = 0.2f;", mrg))   # = vanilla Mana.json's 0.2 s regen interval
# 0.4.13 (skill:fn:combat): CMB = UUID -> long[]{ms left at the last pulse, wall ms of that pulse} (players IN combat only); NDLY =
# NoDamageTakenCondition -> Long its Delay in ns (asked from the condition, once per condition object); WINDOW = the Delay in ms
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CMB = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap NDLY = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static volatile long WINDOW = 0L;", mrg))   # vanilla 6000; 0 = nobody in combat since the start
mrg.addField(CtField.make("public static boolean CFAILED_ONCE = false;", mrg))
mrg.addField(CtField.make("public static final long STALE_MS = 1000L;", mrg))   # a pulse older than this no longer holds the countdown at >= 1
mrg.addField(CtField.make("public static final long NDLY_CAP = 3600000000000L;", mrg))   # the Delay search stops at 1 hour (ns)
# 0.4.13 fix F1: CARRY = UUID -> Object[]{world name, that world's clock (Instant), Long System.nanoTime() of the pulse, Float its time
# dilation, the stamps after the pulse: lastDamageTime, lastCombatAction, lastChargeTime} (pruned to online players by Acro.retainOnline)
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CARRY = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static boolean KFAILED_ONCE = false;", mrg))
mrg.addField(CtField.make("public static final long CARRY_CAP = 3600000000000L;", mrg))   # over 1 hour (ns, real) since a stamp = Instant.MIN
mrg.addField(CtField.make("public static final long CARRY_SLACK = 1000000000L;", mrg))   # 1 s of slack on the late-hit / fresh-hit windows (ns)
''')
rep('DDC = "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent"\n',
    'DDC = "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent"\n'
    'CHG = "com.hypixel.hytale.server.core.modules.entity.condition.ChargingCondition"   # 0.4.13 fix: Mana keeps regenerating while charging\n')

# ---------------------------------------------------------------------------------------------------------------- ManaRegen: charging (state / rates / amount)
rep('''# regenerates: OUT of combat), 1 = only NoDamageTaken fails (vanilla's in-combat pause), 2 = anything else fails (charging, dead)
''', '''# regenerates: OUT of combat), 1 = only NoDamageTaken fails (vanilla's in-combat pause), 2 = anything else fails (dead, ...).
# 0.4.13 (Skyy: Mana keeps regenerating while you charge): 3 = only Charging fails - an INVERSE Charging, its eval0 says the player IS
# charging (vanilla withholds its refill: out of combat), 4 = NoDamageTaken + that Charging (charging in combat). A non-inverse Charging
# that fails (eval0 false) is "anything else" (2), and so is dead (Alive fails) whatever else fails with it.
''')
rep('''  boolean nd = false;
''', '''  boolean nd = false;
  boolean ch = false;
''')
rep('''    if (cs[i] instanceof {NDT}) nd = true;
    else return 2;
''', '''    if (cs[i] instanceof {NDT}) nd = true;
    else if (cs[i] instanceof {CHG} && cs[i].eval0(acc, ref, now)) ch = true;
    else return 2;
''')
rep('''  return nd ? 1 : 0;
''', '''  if (ch) return nd ? 4 : 3;
  return nd ? 1 : 0;
''')
rep('''# {{base, out, in}} per second over the Mana value's regen entries: base = every positive Additive entry (vanilla 5), out = the ones running
# now, in = the ones only vanilla's combat pause stops
''', '''# {{base, out, in, chargeOut, chargeIn}} per second over the Mana value's regen entries: base = every positive Additive entry (vanilla 5),
# out = the ones running now, in = the ones vanilla's combat pause stops (charging or not - 0.4.13), chargeOut = the ones only charging
# stops (out of combat: SkyySkills refills them whole, 0.4.13), chargeIn = the part of in that is also charging (texts only)
''')
rep('''  float[] r = new float[] {{ 0.0f, 0.0f, 0.0f }};
''', '''  float[] r = new float[] {{ 0.0f, 0.0f, 0.0f, 0.0f, 0.0f }};
''')
rep('''    else if (st == 1) r[2] = r[2] + b;
''', '''    else if (st == 1) r[2] = r[2] + b;
    else if (st == 3) r[3] = r[3] + b;
    else if (st == 4) {{ r[2] = r[2] + b; r[4] = r[4] + b; }}
''')
rep('''# Mana pool (max 0) or at max. MR = Mana Regen % (below 0 = 0, at most MAX_PCT), F = mana.regen.inCombat (0-100).
''', '''# Mana pool (max 0) or at max. MR = Mana Regen % (below 0 = 0, at most MAX_PCT), F = mana.regen.inCombat (0-100).
# 0.4.13: + chargeOut x (1 + MR / 100) when r has a 4th entry (rates' chargeOut): the refill vanilla withholds while charging out of
# combat, whole, + the boosts the out-of-combat path adds; charging in combat is in r[2] (the in-combat amount).
''')
rep('''  double per = (double) r[1] * p / 100.0 + (double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0;
''', '''  double per = (double) r[1] * p / 100.0 + (double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0;
  if (r.length > 3) per = per + (double) r[3] * (1.0 + p / 100.0);
''')

# ---------------------------------------------------------------------------------------------------------------- ManaRegen: the combat state + the stamp carry
CMB_METHODS = r'''# ================= 0.4.13: the combat state for skill:fn:combat (SkyyHud's Combat widget) - ONE source of truth with the Mana regen
# In combat = vanilla's combat pause on the Mana regen: a NoDamageTaken condition of one of the positive Additive Mana regen entries (the
# entries rates() counts, the conditions state() keys on) FAILS at the world's own clock - the test the in-combat refill runs.
# The condition's Delay (NoDamageTakenCondition.delay is protected): the smallest d with eval0 true d after the last hit (eval0 =
# TimeUtil.compareDifference(last, last + d, Delay) >= 0) - doubling from 1 ms, then halving to the nanosecond; at most NDLY_CAP. Cached
# per condition object. -1 = unknown (no real hit yet, or not found).
mrg.addMethod(CtNewMethod.make(f"""
public static long delayOf({CND} c, {CAC} acc, {REF} ref, java.time.Instant last) {{
  Object k = NDLY.get(c);
  if (k != null) return ((Long) k).longValue();
  if (last == null || last.equals(java.time.Instant.MIN)) return -1L;
  long d = -1L;
  if (c.eval0(acc, ref, last)) d = 0L;
  else {{
    long lo = 0L;
    long hi = 1000000L;
    while (hi <= NDLY_CAP && !c.eval0(acc, ref, last.plusNanos(hi))) {{ lo = hi; hi = hi * 2L; }}
    if (hi <= NDLY_CAP) {{
      while (hi - lo > 1L) {{
        long mid = lo + (hi - lo) / 2L;
        if (c.eval0(acc, ref, last.plusNanos(mid))) hi = mid;
        else lo = mid;
      }}
      d = hi;
    }}
  }}
  if (d >= 0L) {{
    if (NDLY.size() > 64) NDLY.clear();
    NDLY.put(c, Long.valueOf(d));
  }}
  return d;
}}""", mrg))
# ms until the combat pause ends: every NoDamageTaken condition (of those entries) that FAILS now -> its Delay minus the time since the
# last hit (the DamageDataComponent the condition reads, the same instant), rounded UP, at least 1 and at most the Delay while the engine
# says in combat; the largest; 0 = none fails = out of combat. Sets WINDOW. Any accessor (the harness drives it with real conditions).
mrg.addMethod(CtNewMethod.make(f"""
public static long combatLeft({CAC} acc, {REF} ref, java.time.Instant now, {RGV}[] rv) {{
  if (rv == null || now == null) return 0L;
  long best = 0L;
  long win = 0L;
  java.time.Instant last = null;
  boolean got = false;
  for (int i = 0; i < rv.length; i++) {{
    if (rv[i] == null) continue;
    {RGN} rg = rv[i].getRegenerating();
    if (!(baseOf(rg) > 0.0f)) continue;
    {CND}[] cs = rg.getConditions();
    if (cs == null) continue;
    for (int j = 0; j < cs.length; j++) {{
      if (!(cs[j] instanceof {NDT})) continue;
      if (cs[j].eval(acc, ref, now)) continue;
      if (!got) {{
        got = true;
        {DDC} dd = ({DDC}) acc.getComponent(ref, {DDC}.getComponentType());
        if (dd != null) last = dd.getLastDamageTime();
      }}
      long d = delayOf(cs[j], acc, ref, last);
      long w = d > 0L ? (d + 999999L) / 1000000L : 0L;
      long l = 1L;
      if (d > 0L && last != null) {{
        long el = -1L;
        try {{ el = last.until(now, java.time.temporal.ChronoUnit.NANOS); }} catch (Throwable t) {{ el = -1L; }}
        if (el < 0L) l = w;
        else if (el < d) l = (d - el + 999999L) / 1000000L;
      }}
      if (l < 1L) l = 1L;
      if (w > 0L && l > w) l = w;
      if (l > best) {{ best = l; win = w; }}
    }}
  }}
  if (win > 0L) WINDOW = win;
  return best;
}}""", mrg))
# world thread, every Mana regen pulse (ManaRegen.tick, before any of its returns): remember the state; out of combat = no entry. Own try.
mrg.addMethod(CtNewMethod.make(f"""
public static void combat(java.util.UUID u, {CAC} acc, {REF} ref, java.time.Instant now, {RGV}[] rv) {{
  if (u == null) return;
  try {{
    long l = combatLeft(acc, ref, now, rv);
    if (l > 0L) CMB.put(u, new long[] {{ l, System.currentTimeMillis() }});
    else CMB.remove(u);
  }} catch (Throwable t) {{
    CMB.remove(u);
    if (!CFAILED_ONCE) {{ CFAILED_ONCE = true; {PKG}.SkillCfg.warn("combat state (skill:fn:combat) failed (logged once): " + t); }}
  }}
}}""", mrg))
# skill:fn:combat's answer at wall time w (ANY thread, memory only): the last pulse's ms counted down on the wall clock; while that pulse
# is at most STALE_MS old it stays >= 1 (only the next pulse - the Mana regen's own test - ends combat); a player no longer ticked runs out
# on the wall clock (and the entry is dropped). 0 = out of combat / unknown.
mrg.addMethod(CtNewMethod.make("""
public static long combatNow(java.util.UUID u, long w) {
  if (u == null) return 0L;
  Object o = CMB.get(u);
  if (o == null) return 0L;
  long[] e = (long[]) o;
  if (e.length < 2 || e[0] <= 0L) return 0L;
  long age = w - e[1];
  if (age < 0L) age = 0L;
  long l = e[0] - age;
  if (age <= STALE_MS) return l < 1L ? 1L : l;
  if (l > 0L) return l;
  CMB.remove(u, o);
  return 0L;
}""", mrg))
# ================= 0.4.13 fix F1: stamps from another world's clock (every world saves its own TimeResource clock; the player's
# DamageDataComponent travels with its Holder). ns from a to b on the world clock, never throwing (an overflow = the far end of a long).
mrg.addMethod(CtNewMethod.make("""
public static long nsBetween(java.time.Instant a, java.time.Instant b) {
  try {
    return a.until(b, java.time.temporal.ChronoUnit.NANOS);
  } catch (Throwable t) {
    return b.isAfter(a) ? Long.MAX_VALUE : Long.MIN_VALUE;
  }
}""", mrg))
# THE carry rule (pure, any thread; the harness drives it with records it builds): the stamp to write instead of s, null = keep s.
# s = one stamp now (i: 0 lastDamageTime, 1 lastCombatAction, 2 lastChargeTime), wn / now / dil / wall = this pulse's world name, clock,
# time dilation and System.nanoTime(); rec = the last pulse's CARRY record. In ANOTHER world (wn differs from the record's): s is still
# the old world's stamp when it equals the recorded one, or when it lies after the recorded clock by at most the wall gap x the old
# dilation + CARRY_SLACK (a hit there after its last pulse) and NOT in this world's own window (now - gap x dil - CARRY_SLACK .. now =
# where a fresh hit here lies: left alone). Then real ns since s = (old clock - s) / old dilation + gap, and the new stamp = now - real x
# dil (a world's clock = real time x its dilation); real over CARRY_CAP = Instant.MIN (never hit: passes every NoDamageTaken Delay).
# Always: a stamp in the future of this world's clock (nothing else can make one: the clock only moves forward) = now. Instant.MIN stays.
mrg.addMethod(CtNewMethod.make("""
public static java.time.Instant carried(java.time.Instant s, String wn, java.time.Instant now, float dil, long wall, Object[] rec, int i) {
  if (s == null || now == null || s.equals(java.time.Instant.MIN)) return null;
  java.time.Instant out = null;
  if (wn != null && rec != null && rec.length >= 7 && i >= 0 && i < 3 && rec[0] instanceof String && !wn.equals(rec[0])
      && rec[1] instanceof java.time.Instant && rec[2] instanceof Long && rec[3] instanceof Float) {
    java.time.Instant rn = (java.time.Instant) rec[1];
    long gap = wall - ((Long) rec[2]).longValue();
    if (gap < 0L) gap = 0L;
    double od = (double) ((Float) rec[3]).floatValue();
    if (!(od > 0.0)) od = 1.0;
    double nd = (double) dil;
    if (!(nd > 0.0)) nd = 1.0;
    boolean take = s.equals(rec[4 + i]);
    if (!take && s.isAfter(rn)) {
      boolean fresh = !s.isAfter(now) && (double) nsBetween(s, now) <= (double) gap * nd + (double) CARRY_SLACK;
      take = !fresh && (double) nsBetween(rn, s) <= (double) gap * od + (double) CARRY_SLACK;
    }
    if (take) {
      double el = (double) nsBetween(s, rn) / od + (double) gap;
      if (el < 0.0) el = 0.0;
      if (el > (double) CARRY_CAP) out = java.time.Instant.MIN;
      else out = now.minusNanos((long) (el * nd));
    }
  }
  if (out == null && s.isAfter(now)) out = now;
  return out;
}""", mrg))
# world thread, every Mana regen pulse (ManaRegen.tick, first after the clock): the three stamps through carried() against the last
# pulse's record, then this pulse's record. Own try: a failure drops the record and can never stop the combat state or the refill.
mrg.addMethod(CtNewMethod.make(f"""
public static void carry(java.util.UUID u, {ST} store, {CB} cb, {REF} ref, java.time.Instant now, float dil) {{
  if (u == null) return;
  try {{
    {DDC} dd = ({DDC}) cb.getComponent(ref, {DDC}.getComponentType());
    if (dd == null || now == null) {{ CARRY.remove(u); return; }}
    String wn = null;
    Object ext = store.getExternalData();
    if (ext instanceof {EST}) {{
      {WLD} w = (({EST}) ext).getWorld();
      if (w != null) wn = w.getName();
    }}
    float d = dil > 0.0f ? dil : 1.0f;
    long wall = System.nanoTime();
    Object o = CARRY.get(u);
    Object[] rec = null;
    if (o instanceof Object[]) rec = (Object[]) o;
    java.time.Instant a = dd.getLastDamageTime();
    java.time.Instant x = carried(a, wn, now, d, wall, rec, 0);
    if (x != null) {{ dd.setLastDamageTime(x); a = x; }}
    java.time.Instant b = dd.getLastCombatAction();
    x = carried(b, wn, now, d, wall, rec, 1);
    if (x != null) {{ dd.setLastCombatAction(x); b = x; }}
    java.time.Instant c = dd.getLastChargeTime();
    x = carried(c, wn, now, d, wall, rec, 2);
    if (x != null) {{ dd.setLastChargeTime(x); c = x; }}
    CARRY.put(u, new Object[] {{ wn, now, Long.valueOf(wall), Float.valueOf(d), a, b, c }});
  }} catch (Throwable t) {{
    CARRY.remove(u);
    if (!KFAILED_ONCE) {{ KFAILED_ONCE = true; {PKG}.SkillCfg.warn("combat stamp carry (world switch) failed (logged once): " + t); }}
  }}
}}""", mrg))
# /skills mana's state line (pure, any thread; ManaCmd's 0.4.12 lines + the charging cases): r = rates(...), pct = Mana Regen %, factor =
# mana.regen.inCombat, max = the Mana max
mrg.addMethod(CtNewMethod.make(f"""
public static String stateLine(float[] r, double pct, int factor, float max) {{
  if (!(max > 0.0f)) return "no Mana pool (max 0) - nothing refills";
  if (r == null || r.length < 3) return "no refill right now";
  double p = pct > 0.0 ? (pct > MAX_PCT ? MAX_PCT : pct) : 0.0;
  int f = factor < 0 ? 0 : (factor > 100 ? 100 : factor);
  float co = r.length > 3 ? r[3] : 0.0f;
  float ci = r.length > 4 ? r[4] : 0.0f;
  if (r[1] > 0.0f) return "out of combat - vanilla refills " + {PKG}.Overall.num((double) r[1]) + "/s" + (p > 0.0 ? ", SkyySkills adds " + {PKG}.Overall.num((double) r[1] * p / 100.0) + "/s" : "");
  if (co > 0.0f) return "charging - Mana still regenerates: SkyySkills refills " + {PKG}.Overall.num((double) co * (1.0 + p / 100.0)) + "/s (vanilla pauses while you charge)";
  if (r[2] > 0.0f) return "IN COMBAT (vanilla's 6 s pause)" + (ci > 0.0f ? ", charging - Mana still regenerates" : "") + " - SkyySkills refills " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0) + "/s (" + f + "% of " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0)) + "/s)";
  return "no refill right now (dead, or another regen condition stops it)";
}}""", mrg))
'''
rep('''# world thread, every tick from AcroSys (before its 1 s gate): one pulse per PULSE seconds (vanilla's own interval), at most 1 s at a time
''', CMB_METHODS + '''# world thread, every tick from AcroSys (before its 1 s gate): one pulse per PULSE seconds (vanilla's own interval), at most 1 s at a time
# 0.4.13: each pulse reads the world's clock first and carries stamps from another world's clock (carry, fix F1), then reads the Mana value
# and the regen entries and records the combat state (combat - before every return below, so it works at full Mana and without a Mana
# pool), then the refill runs on the same now / entries (the 0.4.12 "0 % and no boosts" return is gone: charging still refills there)
''')
rep('''    if (secs > 1.0f) secs = 1.0f;
    int f = IN_COMBAT;
    double pct = total(u);
    if (f <= 0 && !(pct > 0.0)) return;
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return;
    int mi = {DST}.getMana();
    if (mi < 0) return;
    {ESV} v = m.get(mi);
    if (v == null) return;
    float max = v.getMax();
    float cur = v.get();
    if (!(max > 0.0f) || !(cur < max)) return;
    java.time.Instant now = (({TMR}) store.getResource({TMR}.getResourceType())).getNow();
    float a = amount(rates(cb, ref, now, v.getRegeneratingValues()), pct, f, secs, cur, max);
    if (a > 0.0f) m.addStatValue(mi, a);''', '''    if (secs > 1.0f) secs = 1.0f;
    {TMR} tr = ({TMR}) store.getResource({TMR}.getResourceType());
    java.time.Instant now = tr.getNow();
    carry(u, store, cb, ref, now, tr.getTimeDilationModifier());   // 0.4.13 fix F1: stamps from another world's clock (own try)
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    int mi = {DST}.getMana();
    {ESV} v = null;
    if (m != null && mi >= 0) v = m.get(mi);
    if (v == null) {{ CMB.remove(u); return; }}
    {RGV}[] rv = v.getRegeneratingValues();
    combat(u, cb, ref, now, rv);   // 0.4.13: skill:fn:combat - the entries, conditions and clock the refill below uses (own try)
    int f = IN_COMBAT;
    double pct = total(u);
    float max = v.getMax();
    float cur = v.get();
    if (!(max > 0.0f) || !(cur < max)) return;
    float a = amount(rates(cb, ref, now, rv), pct, f, secs, cur, max);   // 0.4.13: + what vanilla withholds while charging
    if (a > 0.0f) m.addStatValue(mi, a);''')
# text(): the charging sentence (the rest of the line is 0.4.12's)
rep('''  sb.append(". Never while charging.");
''', '''  sb.append(f <= 0 ? ". Charging - Mana still regenerates out of combat (the normal refill)." : ". Charging - Mana still regenerates (the normal refill out of combat, the in-combat refill in combat).");   // 0.4.13
''')

# ---------------------------------------------------------------------------------------------------------------- /skills mana: the state line
rep('''      String st;
      if (!(v.getMax() > 0.0f)) st = "no Mana pool (max 0) - nothing refills";
      else if (r[1] > 0.0f) st = "out of combat - vanilla refills " + {PKG}.Overall.num((double) r[1]) + "/s" + (p > 0.0 ? ", SkyySkills adds " + {PKG}.Overall.num((double) r[1] * p / 100.0) + "/s" : "");
      else if (r[2] > 0.0f) st = "IN COMBAT (vanilla's 6 s pause) - SkyySkills refills " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0) + "/s (" + f + "% of " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0)) + "/s)";
      else st = "no refill right now (holding a charge, or dead)";
''', '''      String st = {PKG}.ManaRegen.stateLine(r, p, f, v.getMax());   // 0.4.13: 0.4.12's lines + "charging - Mana still regenerates"
''')

# ---------------------------------------------------------------------------------------------------------------- F2: the prune
rep('''    {PKG}.ManaRegen.CLK.keySet().retainAll(online);   // 0.4.12 (the Mana Regen % entries belong to the mods that registered them)
''', '''    {PKG}.ManaRegen.CLK.keySet().retainAll(online);   // 0.4.12 (the Mana Regen % entries belong to the mods that registered them)
    {PKG}.ManaRegen.CMB.keySet().retainAll(online);   // 0.4.13 fix F2: a player who left in combat
    {PKG}.ManaRegen.CARRY.keySet().retainAll(online);   // 0.4.13 fix F1's per-player record
''')

# ---------------------------------------------------------------------------------------------------------------- CombatFn
CMBF = r'''# ================= skill:fn:combat (0.4.13): the combat state for other mods (SkyyHud's Combat widget) - java.lang types only, memory only,
# never throws, any thread (one ConcurrentHashMap read: cheap enough for every HUD refresh of every online player)
#   apply(java.util.UUID player) -> Long  ms left in combat; 0 = out of combat (unknown / offline players 0)  = ManaRegen.combatNow
#   apply("window")              -> Long  the whole combat window in ms (vanilla 6000 = the Mana regen's NoDamageTaken Delay, read from
#                                         the engine condition); 0 until somebody was in combat since the start. A bar = left / window
#   apply(new Object[] { x })    -> the same as apply(x);   anything else -> null
cmbf.addInterface(pool.get("java.util.function.Function"))
cmbf.addConstructor(CtNewConstructor.make("public CombatFn() { }", cmbf))
cmbf.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  Object x = arg;
  try {{
    if (x instanceof Object[]) {{
      Object[] a = (Object[]) x;
      x = a.length > 0 ? a[0] : null;
    }}
    if (x instanceof java.util.UUID) return Long.valueOf({PKG}.ManaRegen.combatNow((java.util.UUID) x, System.currentTimeMillis()));
    if (x instanceof String && ((String) x).trim().equalsIgnoreCase("window")) return Long.valueOf({PKG}.ManaRegen.WINDOW);
    return null;
  }} catch (Throwable t) {{
    if (x instanceof java.util.UUID) return Long.valueOf(0L);
    return null;
  }}
}}""", cmbf))

'''
rep('''# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''', CMBF + '''# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''')

# ---------------------------------------------------------------------------------------------------------------- the plugin
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:manaregen", new {PKG}.ManaRegenFn());   // 0.4.12: the Mana Regen % registry
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:manaregen", new {PKG}.ManaRegenFn());   // 0.4.12: the Mana Regen % registry
  {PKG}.SkillStore.bridge().put("skill:fn:combat", new {PKG}.CombatFn());   // 0.4.13: the combat state (SkyyHud's Combat widget)
''')
rep('''+ skill:fn:overall + skill:overall:<uuid> + skill:fn:manaregen; trees bridge on''',
    '''+ skill:fn:overall + skill:overall:<uuid> + skill:fn:manaregen + skill:fn:combat; trees bridge on''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:manaregen"); }} catch (Throwable t) {{ }}   // 0.4.12
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:manaregen"); }} catch (Throwable t) {{ }}   // 0.4.12
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:combat"); }} catch (Throwable t) {{ }}   // 0.4.13
''')
rep('''          mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd''',
    '''          mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd, cmbf):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; 0.4.13: + CombatFn''')

# ---------------------------------------------------------------------------------------------------------------- engine probes
rep('''assert pool.get(NDT).subclassOf(pool.get(CND)), "NoDamageTakenCondition is no longer a Condition"
''', '''assert pool.get(NDT).subclassOf(pool.get(CND)), "NoDamageTakenCondition is no longer a Condition"
# 0.4.13 (skill:fn:combat): the Delay is asked from the condition (eval0 at last hit + d), the countdown = Delay - (now - last hit); both rest
# on NoDamageTakenCondition.eval0 = TimeUtil.compareDifference(DamageDataComponent.getLastDamageTime(), now, this.delay) >= 0 (bytecode,
# HytaleServer.jar 2026-10-02) and on the hit being stamped with the world's TimeResource clock (DamageSystems$TrackLastDamage)
for c, m, d in ((CND, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (NDT, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
import jpype as _jp
def _bc_lines(cls, meth):
    """the instructions of every declared method of cls named meth (bridge methods included), as InstructionPrinter text"""
    _ip, _out = _jp.JClass("javassist.bytecode.InstructionPrinter"), []
    for _mm in pool.get(cls).getDeclaredMethods():
        if str(_mm.getName()) != meth or _mm.getMethodInfo().getCodeAttribute() is None:
            continue
        _it, _cp = _mm.getMethodInfo().getCodeAttribute().iterator(), _mm.getMethodInfo().getConstPool()
        while _it.hasNext():
            _out.append(str(_ip.instructionString(_it, _it.next(), _cp)))
    return _out
_ndl = _bc_lines(NDT, "eval0")
assert (any(DDC + ".getLastDamageTime" in x for x in _ndl) and any("com.hypixel.hytale.common.util.TimeUtil.compareDifference" in x for x in _ndl)
        and any(NDT + ".delay" in x for x in _ndl) and any(x.startswith("iflt") for x in _ndl)), \\
    "NoDamageTakenCondition.eval0 is no longer compareDifference(lastDamageTime, now, delay) >= 0 - re-check skill:fn:combat's countdown"
_tll = _bc_lines("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$TrackLastDamage", "handle")
assert any(TMR + ".getNow" in x for x in _tll) and any(DDC + ".setLastDamageTime" in x for x in _tll), \\
    "DamageSystems$TrackLastDamage no longer stamps the hit with TimeResource.getNow - the combat clock would differ"
# 0.4.13 FIX F1 (cross-check 2026-10-02): a world's clock = real time x its time dilation, so a stamp from another world is carried as REAL
# time: TickingThread.run hands tick() the measured System.nanoTime() step / 1e9, World.tick multiplies it by
# TimeResource.getTimeDilationModifier() before Store.tick, TimeSystem.tick adds (long) (dt x 1e9) ns to TimeResource.now (bytecode,
# HytaleServer.jar 2026-10-02; the dilation is not saved: 1.0 after a restart). Every engine member the carry calls must stay public.
_ttr = _bc_lines("com.hypixel.hytale.server.core.util.thread.TickingThread", "run")
assert (any("java.lang.System.nanoTime" in x for x in _ttr) and any("float 1.0E9" in x for x in _ttr) and any(x.strip() == "fdiv" for x in _ttr)
        and any("com.hypixel.hytale.server.core.util.thread.TickingThread.tick((F)V)" in x for x in _ttr)), \\
    "TickingThread.run no longer ticks with the measured System.nanoTime() step - re-check the clock rate the stamp carry converts with"
_wtk = _bc_lines(WLD, "tick")
assert (any(TMR + ".getTimeDilationModifier" in x for x in _wtk) and any(x.strip() == "fmul" for x in _wtk)
        and any("com.hypixel.hytale.component.Store.tick((F)V)" in x for x in _wtk)), \\
    "World.tick no longer scales dt by TimeResource's time dilation - re-check the stamp carry's conversion"
_tsk = _bc_lines("com.hypixel.hytale.server.core.modules.time.TimeSystem", "tick")
assert (any("float 1.0E9" in x for x in _tsk) and any(TMR + ".add((JLjava/time/temporal/TemporalUnit;)V)" in x for x in _tsk)
        and any("java.time.temporal.ChronoUnit.NANOS" in x for x in _tsk)), \\
    "TimeSystem.tick no longer adds dt x 1e9 ns to TimeResource.now - re-check the world clock"
# the Charging condition (Mana.json: Charging, Inverse) reads the charge stamp the same way: eval0 = a charging interaction runs, or
# TimeUtil.compareDifference(lastChargeTime, now, delay) <= 0 - its stamp is carried too; while an INVERSE Charging is the only failing
# condition (with or without NoDamageTaken) SkyySkills refills what vanilla withholds
assert pool.get(CHG).subclassOf(pool.get(CND)), "ChargingCondition is no longer a Condition"
_chl = _bc_lines(CHG, "eval0")
assert any(DDC + ".getLastChargeTime" in x for x in _chl) and any("com.hypixel.hytale.common.util.TimeUtil.compareDifference" in x for x in _chl), \\
    "ChargingCondition.eval0 no longer reads DamageDataComponent.lastChargeTime - re-check the charging refill and the stamp carry"
_JMd = _jp.JClass("javassist.Modifier")
for c, m, d in ((DDC, "getLastDamageTime", "()Ljava/time/Instant;"), (DDC, "setLastDamageTime", "(Ljava/time/Instant;)V"),
                (DDC, "getLastCombatAction", "()Ljava/time/Instant;"), (DDC, "setLastCombatAction", "(Ljava/time/Instant;)V"),
                (DDC, "getLastChargeTime", "()Ljava/time/Instant;"), (DDC, "setLastChargeTime", "(Ljava/time/Instant;)V"),
                (TMR, "getNow", "()Ljava/time/Instant;"), (TMR, "getTimeDilationModifier", "()F"),
                (CND, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (CHG, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (ST, "getExternalData", "()Ljava/lang/Object;"), (EST, "getWorld", "()L" + WLD.replace(".", "/") + ";"),
                (WLD, "getName", "()Ljava/lang/String;")):
    try:
        _mm = pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
    assert _JMd.isPublic(_mm.getModifiers()) and _JMd.isPublic(pool.get(c).getModifiers()), \\
        "%s.%s is no longer public - the stamp carry / charging refill may not call it (protected engine members only from a subclass)" % (c, m)
''')
rep('''print("in-combat Mana regen: vanilla refills %s Mana a second, paused %s s after taking damage; SkyySkills refills %s%% of (vanilla + boosts) there" % (''',
    '''print("combat state (skill:fn:combat, 0.4.13): in combat while that pause runs - its Delay is read from the engine condition at run time (Mana.json: %s s)"
      % ",".join(str(c.get("Delay")) for r in _mpause for c in r.get("Conditions") or [] if c.get("Id") == "NoDamageTaken"))
# 0.4.13 fix (Skyy 2026-10-02): Mana keeps regenerating while charging - the entries that also pause while Charging (inverse)
_mchg = [r for r in _mpause if any(c.get("Id") == "Charging" and c.get("Inverse") for c in (r.get("Conditions") or []))]
print("Mana regen while charging (0.4.13): %d of the %d paused Mana regen entries also pause while Charging (inverse) - SkyySkills refills "
      "there (out of combat the whole rate + boosts, in combat the in-combat rate)" % (len(_mchg), len(_mpause)))
if not _mchg:
    print("NOTE: vanilla Mana.json no longer pauses its regen while charging - the charging refill has nothing to add")
print("in-combat Mana regen: vanilla refills %s Mana a second, paused %s s after taking damage; SkyySkills refills %s%% of (vanilla + boosts) there" % (''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
# methods before callers: state < rates < amount; delayOf < combatLeft < combat < tick; nsBetween < carried < carry < tick; stateLine before
# the ManaCmd; combatNow before CombatFn.apply; CombatFn before the plugin's setup
_ix = lambda t: s.index(t)
assert _ix("public static int state(") < _ix("public static float[] rates(") < _ix("public static float amount(") < _ix("public static long delayOf(")
assert (_ix("public static long delayOf(") < _ix("public static long combatLeft(") < _ix("public static void combat(java.util.UUID u,")
        < _ix("public static long combatNow(") < _ix("public static long nsBetween(") < _ix("public static java.time.Instant carried(")
        < _ix("public static void carry(java.util.UUID u,") < _ix("public static String stateLine(")
        < _ix('mrg.addMethod(CtNewMethod.make(f"""\npublic static void tick(') < _ix("public static float vanillaRate()"))
assert _ix("public static float baseOf(") < _ix("public static long combatLeft(")
assert _ix("public static String stateLine(") < _ix("protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{\n  try {{\n    if (!pr.hasPermission(\"skyyskills.admin\")) {{ pr.sendMessage({MSG}.raw(\"[Skills] no permission (skyyskills.admin)\")); return; }}\n    java.util.UUID u = pr.getUuid();\n    {ESM} m")
assert _ix("public static long combatNow(") < _ix("public CombatFn() { }") < _ix("public Object apply(Object arg) {{\n  Object x = arg;") < _ix("public void setup() {{")
assert s.count("combat(u, cb, ref, now, rv);") == 1 and s.count("amount(rates(cb, ref, now, rv), pct, f, secs, cur, max)") == 1
assert s.count("carry(u, store, cb, ref, now, tr.getTimeDilationModifier());") == 1 and s.count("{PKG}.ManaRegen.stateLine(r, p, f, v.getMax())") == 1
assert s.count("CHG = ") == 1 and s.index("CHG = ") < s.index("{CHG}")
_tk = s[_ix('mrg.addMethod(CtNewMethod.make(f"""\npublic static void tick('):_ix("public static float vanillaRate()")]
assert "if (f <= 0 && !(pct > 0.0)) return;" not in _tk
assert (_tk.index("if (c[0] < PULSE) return;") < _tk.index("java.time.Instant now = tr.getNow();") < _tk.index("carry(u, store, cb, ref, now,")
        < _tk.index("{ESM} m = ") < _tk.index("combat(u, cb, ref, now, rv);") < _tk.index("int f = IN_COMBAT;")
        < _tk.index("if (!(max > 0.0f) || !(cur < max)) return;") < _tk.index("m.addStatValue(mi, a);"))
assert s.count('bridge().put("skill:fn:combat", new {PKG}.CombatFn());') == 1 and s.count('bridge().remove("skill:fn:combat");') == 1
assert s.count("{PKG}.ManaRegen.CMB.keySet().retainAll(online);") == 1 and s.count("{PKG}.ManaRegen.CARRY.keySet().retainAll(online);") == 1
# the WHOLE diff against 0.4.12: only the places above (docstring, version, the new class / fields / methods, CHG, state / rates / amount,
# tick, text's charging sentence, ManaCmd's state line, the CMB / CARRY prune, CombatFn, the plugin's put / ready line / remove, the class
# list, the probes + build prints) - every other line is the 0.4.12 line
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_head_end = _a.index("0.4.12: THE CLASS SKILL CURVE + MANA REGEN IN COMBAT (Skyy's Q&A 2026-10-02 rounds 1-2; full notes in tools/skills_0_4_12_patch.py).")
_tick_old = {"    int f = IN_COMBAT;", "    double pct = total(u);", "    if (f <= 0 && !(pct > 0.0)) return;",
             "    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());", "    int mi = {DST}.getMana();",
             "    if (m == null) return;", "    if (mi < 0) return;", "    {ESV} v = m.get(mi);", "    if (v == null) return;",
             "    float max = v.getMax();", "    float cur = v.get();", "    if (!(max > 0.0f) || !(cur < max)) return;",
             "    java.time.Instant now = (({TMR}) store.getResource({TMR}.getResourceType())).getNow();",
             "    float a = amount(rates(cb, ref, now, v.getRegeneratingValues()), pct, f, secs, cur, max);"}
_fix_old = {"# regenerates: OUT of combat), 1 = only NoDamageTaken fails (vanilla's in-combat pause), 2 = anything else fails (charging, dead)",
            "# {{base, out, in}} per second over the Mana value's regen entries: base = every positive Additive entry (vanilla 5), out = the ones running",
            "# now, in = the ones only vanilla's combat pause stops", "  float[] r = new float[] {{ 0.0f, 0.0f, 0.0f }};",
            '  sb.append(". Never while charging.");', "      String st;",
            '      if (!(v.getMax() > 0.0f)) st = "no Mana pool (max 0) - nothing refills";',
            '      else if (r[1] > 0.0f) st = "out of combat - vanilla refills " + {PKG}.Overall.num((double) r[1]) + "/s" + (p > 0.0 ? ", SkyySkills adds " + {PKG}.Overall.num((double) r[1] * p / 100.0) + "/s" : "");',
            '      else if (r[2] > 0.0f) st = "IN COMBAT (vanilla\'s 6 s pause) - SkyySkills refills " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0) + "/s (" + f + "% of " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0)) + "/s)";',
            '      else st = "no refill right now (holding a charge, or dead)";'}
_bad = [(i, ln) for i, ln in _gone if not (i < _head_end or ln == 'VERSION = "0.4.12"' or ln in _tick_old or ln in _fix_old
                                         or "skill:fn:manaregen; trees bridge on" in ln or "mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd):" in ln)]
assert not _bad, "0.4.12 lines changed outside the planned places: %r" % _bad[:5]
_tick_gone = [ln for i, ln in _gone if ln in _tick_old]
assert len(_tick_gone) <= len(_tick_old), _tick_gone
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.12,", len(_gone), "0.4.12 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net")
