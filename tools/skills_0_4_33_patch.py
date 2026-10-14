"""Derive SkyySkills/build_skyyskills_0.4.33.py from the LIVE generated SkyySkills/build_skyyskills_0.4.32.py (= the tools/deploy_set.py SET
pin; 0.4.32 came from 0.4.31 by tools/skills_0_4_32_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.32 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_33_patch.py   then   python SkyySkills/build_skyyskills_0.4.33.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.33.py --dir tools/dev/scratch/<yours>/h   (bare JVM, -Xverify:all)

0.4.33 (2026-10-13) = MANA REGEN 3.3 A SECOND (Skyy, docs/answered/classes.md 2026-10-13 MAGE / ABILITY SPEC ANSWERS, M11: "Vanilla 0.7's
3.3 per second"). 0.4.31's MANA GEN set the generated Mana.json's flat refill to +1 every 0.2 s (5 Mana a second, Hytale 0.6's rate);
MANA_INTERVAL is now 0.3 s = Hytale 0.7's own interval (+1 every 0.3 s = 3.33 Mana a second). Hytale 0.7's vanilla file already refills
every 0.3 s, so the generated Mana.json now changes only InitialValue / Max -> 0 (the Base Mana table) and adds the NoDamageTaken 6 s
pause (combat) - its Interval stays vanilla's 0.3. Everything else of MANA GEN is unchanged (max from the Base Mana table, the 6 s combat
pause for the flat refill, Mana keeps regenerating while charging, Min / ResetType / Shared / the Creative entry = 0.7's).
  - IN COMBAT: SkyySkills' in-combat refill was never a fixed number - ManaRegen reads the live Mana stat's refill (rates / baseOf) and
    refills mana.regen.inCombat % (75) of (that + boosts). It follows the new rate by itself: 75 % of 3.33 = 2.5 Mana a second in combat
    (was 75 % of 5 = 3.75). Mana Regen % boosts (class level, accessories, class balance) are percents of the refill, so they scale too
    (+20 % = 4 a second, was 6).
  - ManaRegen.PULSE (SkyySkills' own refill / combat-state clock) = MANA_INTERVAL (0.3 s, was 0.2) so it keeps stepping in time with the
    engine's refill as before (the Soul Binding take-back and the combat HUD state run on that pulse; the amounts are per second x the
    seconds since the last pulse, so the rate does not depend on it).
  - ManaGuard's live check expects a refill of 3.333 a second (MANA_PS from the generated file).
  - TEXTS: the default xp.properties comments that named the rate (Overall / base Mana block: "+1 every 0.3 s after 6 s"; Mana regen in
    combat block: "Mana refills 3.3 per second", "+20 percent = 4 per second"). Only a NEW file or a newly appended block gets them; an
    existing xp.properties keeps its comment text (no config migration, no saved data touched). The Server Setup rows never stated the
    rate (their help says "% of the normal refill") and /skills mana + the "Mana Regen: show mine" action read the live rate.
No config key, no saved data, no migration, no command, no new class. Rolling back to 0.4.32 is safe (Mana refills 5 a second again).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.32.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.33.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.32"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.32"' in s and "derived from the generated 0.4.31 by tools/skills_0_4_32_patch.py" in s, "not the live generated 0.4.32"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "SkyySkills-IO" in s, "not 0.4.32 (the lag fixes are missing)"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "expected %d occurrence(s), found %d of:\n%s" % (count, n, old[:300])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.33 (2026-10-13)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.32 - build script (derived from the generated 0.4.31 by tools/skills_0_4_32_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.33 - build script (derived from the generated 0.4.32 by tools/skills_0_4_33_patch.py - edit the patch, not this file;
0.4.32 was derived from the generated 0.4.31 by tools/skills_0_4_32_patch.py;
''')
rep('''0.4.32 (2026-10-13) = LAG FIXES from the code audit''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.33.py.
0.4.32 (2026-10-13) = LAG FIXES from the code audit''')
rep('VERSION = "0.4.32"', 'VERSION = "0.4.33"')

# ---------------------------------------------------------------- MANA GEN: the refill interval
rep('''# damage; SkyySkills refills mana.regen.inCombat % there) and the MANA_INTERVAL interval (5 Mana a second, the tuned rate). Nothing else.''',
    '''# damage; SkyySkills refills mana.regen.inCombat % there) and the MANA_INTERVAL interval (0.4.33: 3.3 Mana a second = 0.7's own). Nothing else.''')
rep('''MANA_INTERVAL = 0.2      # +1 every 0.2 s = 5 Mana a second (0.6; 0.7 vanilla 0.3 s = 3.3 a second)''',
    '''MANA_INTERVAL = 0.3      # 0.4.33 (Skyy 2026-10-13 M11 "Vanilla 0.7's 3.3 per second"): +1 every 0.3 s = 3.33 Mana a second (0.4.31-0.4.32: 0.2 s = 5)
assert MANA_INTERVAL == 0.3 and round(1.0 / MANA_INTERVAL, 2) == 3.33''')

# ---------------------------------------------------------------- ManaRegen.PULSE follows the refill interval
rep('''mrg.addField(CtField.make("public static final float PULSE = 0.2f;", mrg))   # = vanilla Mana.json's 0.2 s regen interval''',
    '''mrg.addField(CtField.make("public static final float PULSE = %rf;" % MANA_INTERVAL, mrg))   # = the shipped Mana.json's regen interval (0.4.33: MANA_INTERVAL 0.3 s)''')
rep('''    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own 0.2 s clock, own try; first, so no call below can skip it)''',
    '''    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own PULSE clock, own try; first, so no call below can skip it)''')
rep('''# research/Mana-Cost-And-Regen-Research.md 2.1-2.3: vanilla Mana.json = every 0.2 s +1 Additive while Alive, NoDamageTaken (6 s) and not
# Charging (inverse) - 5 a second out of combat, 0 for 6 s after taking damage, 0 while holding a charge. SRC = UUID -> ConcurrentHashMap''',
    '''# research/Mana-Cost-And-Regen-Research.md 2.1-2.3: vanilla Mana.json = every 0.2 s +1 Additive while Alive, NoDamageTaken (6 s) and not
# Charging (inverse) - 5 a second out of combat, 0 for 6 s after taking damage, 0 while holding a charge (0.6; 0.4.33 ships +1 every 0.3 s
# = 3.33 a second; the code reads the rate from the live stat). SRC = UUID -> ConcurrentHashMap''')
rep('''# per second of one regen entry: Additive with a positive amount and interval -> amount / interval (vanilla Mana: 1 / 0.2 s = 5), else 0''',
    '''# per second of one regen entry: Additive with a positive amount and interval -> amount / interval (shipped Mana: 1 / 0.3 s = 3.33), else 0''')
rep('''# vanilla's base Mana refill per second from the Mana stat asset (5 in vanilla; 0 when it cannot be read) - texts only''',
    '''# vanilla's base Mana refill per second from the Mana stat asset (3.33 as shipped since 0.4.33; 0 when it cannot be read) - texts only''')

# ---------------------------------------------------------------- default config comments that named the rate
rep('''OVL_L.append("# 0.4.8, replaced mana.magicBase / mana.magicClasses). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after 6 s")''',
    '''OVL_L.append("# 0.4.8, replaced mana.magicBase / mana.magicClasses). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.3 s after 6 s")''')
rep('''MREG_L.append("# Vanilla Mana refills 5 per second, but not at all for 6 seconds after you take damage (in combat) and never while you hold")''',
    '''MREG_L.append("# Mana refills 3.3 per second, but not at all for 6 seconds after you take damage (in combat) and never while you hold")''')
rep('''MREG_L.append("# out of combat +20 percent = 6 per second, in combat the whole refill (vanilla + boosts) runs at mana.regen.inCombat percent.")''',
    '''MREG_L.append("# out of combat +20 percent = 4 per second, in combat the whole refill (vanilla + boosts) runs at mana.regen.inCombat percent.")''')

# ---------------------------------------------------------------- checks
assert "MANA_INTERVAL = 0.2 " not in s and s.count("MANA_INTERVAL = 0.3 ") == 1
assert 'PULSE = 0.2f' not in s
assert "5 per second" not in s and "6 per second" not in s
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.32 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.32,", len(_gone), "0.4.32 lines replaced;", len(OLDS), "anchors")
