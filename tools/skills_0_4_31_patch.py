"""Derive SkyySkills/build_skyyskills_0.4.31.py from the LIVE generated SkyySkills/build_skyyskills_0.4.30.py (= the tools/deploy_set.py SET
pin; 0.4.30 came from 0.4.29 by tools/skills_0_4_30_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_30_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.30
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_31_patch.py   then   python SkyySkills/build_skyyskills_0.4.31.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.31.py --dir tools/dev/scratch/<yours>/h   (bare JVM, -Xverify:all)

0.4.31 = THE ACROBATICS XP LINE NO LONGER SPANS A LEVEL-UP (Skyy 2026-10-11 play test chat, found by tools/chat_digest.py / Jev:
"next: Acrobatics 12 at 1/7500 XP" then "+70 Acrobatics XP (40/7500)" - 1 + 70 is not 40).
  WHY: Acrobatics movement XP is PAID every second (Acro.flush -> SkillXp.gain2(..., note false)) but only SHOWN every acro.feedbackMs
  (30 s) from its own counter s[21]. Every other skill's pending "+N XP" line is flushed by gain4 right before SKILL LEVEL UP
  (SkillMsg.send); the Acrobatics counter is not in SkillMsg, so the 30 s line after a level-up summed the XP from BEFORE the level-up
  (31) and after it (39) = "+70 (40/7500)". The stored XP was always right (4970 + 70 = 5040 = level 11 + 40); only the chat line was off.
  FIX (display only - the XP paid, the stored totals, the per-minute cap and the 30 s pace are unchanged):
  - SkillMsg.STAGE (UUID -> long[]{skill, amount}) + stage / unstage: Acro.flush STAGES its whole unshown counter (s[21], this second's
    award included) around each Acrobatics award; SkillMsg.take (the only place a "+N XP" line is built) merges a staged amount into the
    line. So when the award levels up, gain4's existing SkillMsg.send prints "+31 Acrobatics XP (1/7500)" BEFORE "SKILL LEVEL UP" (like
    every other skill) and Acro.flush, seeing the stage consumed, zeroes s[21] and restarts its 30 s clock - the next line is "+39
    Acrobatics XP (40/7500)". No level-up = unstaged unchanged = 0.4.30's exact behaviour.
  - The same around the fall-XP award (note true): a landing that levels up also shows the movement XP counted so far first.
  - Only staged while skills.xpGain is on for that player and xp feedback is on (otherwise nothing would show the counter anyway).
  - A throwing award unstages before the exception leaves (AcroSys already catches it) - a stage never outlives its award.
  - Fixer round: the award catches every Throwable (a stage never outlives it, and an award that threw before paying takes its amount back
    out of s[21], as 0.4.30 never counted it); Acro.retainOnline also prunes SkillMsg.STAGE; the Mana.json build guard is left as it was.
  No config key, no saved data, no migration, no command, no new class. Rolling back to 0.4.30 is safe.
  SCOPE: only the Acrobatics XP Acro pays (running, jumping, dodging, rolling, falls) is staged. Acrobatics XP from elsewhere (admin
  /skills xp, a bridge grant) that levels up still lets the next 30 s movement line include movement XP from before that level-up.

0.4.31 ALSO = THE HYTALE 0.7.0 ASSET PORT (skills07 round, 2026-10-13; Skyy: "hytale 0.7.0  is out!" + "work through your whole list, so
everything is ready to play when i get off work."; research/Hytale-0.7-Port.md). The 0.4.30 script stopped on the 0.7 Assets.zip:
  (1) MANA GEN - 0.7's vanilla Mana.json gives everyone InitialValue / Max 100 and refills +1 every 0.3 s while Alive with no combat and no
      charging pause. Generated from that file at every build (never committed) is an override Server/Entity/Stats/Mana.json with ONLY:
      InitialValue / Max -> 0 (the Base Mana table is a TOTAL base again: none 25, Mage 45, Priest 42 ...; with 100 every class had 100+),
      the flat refill + NoDamageTaken 6 s (combat = 6 s after taking damage; SkyySkills refills mana.regen.inCombat 75 % there - the
      ManaRegen / combat-HUD code is unchanged) and interval 0.2 s (5 Mana a second, the tuned rate; 0.7: 3.3). Min, ResetType, Shared,
      the Creative entry: 0.7's. No Charging pause is added (Skyy: Mana keeps regenerating while charging). A vanilla file already in that
      shape -> no override. Build stops on any shape it does not know; no other live-set jar / pack mod may ship a Mana stat file.
  (2) SPELL GEN - 0.7 removed the DEAD cast-check var (Staff_Cast_Summon_Charged Costs 50) from the staffs + Halloween Broomstick (32 -> 12
      items with both vars). It never mattered (research 1.2: only the charged step interaction checks; 0.4.9 already turns the Simple
      staff step into a 10-Mana StatsCondition). spell_plan now accepts one drain var + at most one dead check var. Result on 0.7: 24 item
      overrides (0.6: 22; + the new Weapon_Staff_Scrap_Lightbulb / Weapon_Staff_Voidcrystal), the same 8 interaction overrides, 26 casters:
      wand 5 / staff 10 / spellbook 20 / blunderbuss 10, every paid cast checks what it spends (gate simulation).
  (3) Every vanilla-derived file regenerates from 0.7 (spell items / interactions, dodge files: bodies unchanged in 0.7, build-checked).
      vs the 0.4.30 jar: + Mana.json, + Scrap_Lightbulb, + Voidcrystal; the 12 staff-folder items lose the dead var (0.4.30's copies would
      have put it back); nothing dropped (0.7 still costs 25 / 50 / 100 Mana, the dodge is still Left / Right only).
  Rolling back to 0.4.30 on Hytale 0.7: no data risk, but everyone gets 100 Mana and full regen in combat again.
  FIXER ROUND (skills07fix, critic findings):
  (4) ONHIT GEN - NEW in 0.7.0 (0.6.8 / 0.7.0-pre.4 had none): 9 weapon signature damage interactions give the attacker Mana on hit
      (Groundslam 25, crossbow signature bolt 50, Volley 20, Lunge / Stab 15, Slash / Sweep / Spin 5, Whirlwind 4), sized for 100-Mana
      pools. Generated overrides: ONLY those Amounts / SPELL_DIVISOR (5 / 10 / 4 / 3 / 1 / 1), the 0.4.8 "Mana / 5" rule. Clash-checked
      like the spell files. + the MANA CONSUMER SCAN: every Server/ JSON naming the Mana stat is printed by what covers it (NOTE for new).
      Vanilla RUNE costs (30-50) stay 0.7's - the SkyyClasses ability round owns the rune policy (printed; question for Skyy).
      FIXER 2 (skills07fix2): live-set items that inherit a generated on-hit file by "Parent" are printed as a NOTE (SkyyArmory's Wynn
      crossbows' Signature_BigArrow_Damage -> Weapon_Crossbow_Damage_Signature_Projectile: +10 Mana a hit, not 50); the rune NOTE says
      what an unscaled rune means (below its cost a player cannot cast it).
  (5) ManaGuard reads the LIVE Mana stat once (pack tick): Max / refill a second / NoDamageTaken pause vs the shipped Mana.json; INFO when
      they match, one WARN naming each difference (another mod's Mana.json / Mana.patch loading later). Logging only.
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.30.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.31.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.30"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.30"' in s and "derived from the generated 0.4.29 by tools/skills_0_4_30_patch.py" in s, "not the live generated 0.4.30"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "SkillMsg.stage(" not in s, "0.4.30 already has the staged Acrobatics line"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CLS0 = s.count("pool.makeClass(")
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
rep('''"""SkyySkills 0.4.30 - build script (derived from the generated 0.4.29 by tools/skills_0_4_30_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.31 - build script (derived from the generated 0.4.30 by tools/skills_0_4_31_patch.py - edit the patch, not this file;
0.4.30 was derived from the generated 0.4.29 by tools/skills_0_4_30_patch.py; ''')
rep('''0.4.30: THE REGEN BLOCK BRIDGE (SkyyArmory 0.1.19's Soul Orb: "no natural Mana regen while any Binding is active"; full notes in
''', '''0.4.31: THE ACROBATICS XP LINE NO LONGER SPANS A LEVEL-UP (Skyy 2026-10-11 chat: "next: Acrobatics 12 at 1/7500 XP" then "+70
  Acrobatics XP (40/7500)"; full notes in tools/skills_0_4_31_patch.py). Acro.flush stages its unshown counter in SkillMsg around each
  Acrobatics award; a level-up's SkillMsg.send shows it BEFORE "SKILL LEVEL UP" (like every other skill) and the counter restarts.
  Display only. CHECKED: SkyySkills/test_skyyskills_0.4.31.py.
  + THE HYTALE 0.7.0 ASSET PORT (skills07): MANA GEN (a generated Mana.json: Max / InitialValue 0, NoDamageTaken 6 s, +1 every 0.2 s) and
  SPELL GEN for 0.7's drain-only staffs; every override regenerated from the 0.7 Assets.zip; ONHIT GEN (0.7's signature Mana on hit / 5)
  + the Mana consumer scan; ManaGuard checks the live Mana stat. Notes in tools/skills_0_4_31_patch.py.
0.4.30: THE REGEN BLOCK BRIDGE (SkyyArmory 0.1.19's Soul Orb: "no natural Mana regen while any Binding is active"; full notes in
''')
rep('VERSION = "0.4.30"', 'VERSION = "0.4.31"')

# ---------------------------------------------------------------------------------------------------------------- SkillMsg: STAGE + take
rep('''msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();", msg))
''', '''msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();", msg))
# 0.4.31: STAGE = UUID -> long[]{skill, amount}: XP that was paid but not shown yet (Acro.flush's 30 s counter), staged only for the length
# of one award; take() merges it into the "+N XP" line, so a level-up inside that award shows it first. unstage = true while not shown.
msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap STAGE = new java.util.concurrent.ConcurrentHashMap();", msg))
msg.addMethod(CtNewMethod.make("""
public static void stage(java.util.UUID u, int skill, long amount) {
  if (u == null || amount <= 0L) return;
  long[] a = new long[2];
  a[0] = (long) skill;
  a[1] = amount;
  STAGE.put(u, a);
}""", msg))
msg.addMethod(CtNewMethod.make("""
public static boolean unstage(java.util.UUID u) {
  return u != null && STAGE.remove(u) != null;
}""", msg))
''')
rep('''msg.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
''', '''msg.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  long[] sg = (long[]) STAGE.remove(u);   // 0.4.31: the staged Acrobatics counter is shown with this line
  if (sg != null && sg[0] >= 0L && sg[0] < (long) {PKG}.SkillDefs.N && sg[1] > 0L) {{
    if (p == null) {{ p = new long[{PKG}.SkillDefs.N]; PEND.put(u, p); }}
    p[(int) sg[0]] += sg[1];
  }}
  if (p == null) return null;
''')

# ---------------------------------------------------------------------------------------------------------------- Acro: award + stage
rep('''# once per second: pay whole XP (sliding per-minute cap, global multiplier), throttled chat line
acro.addMethod(CtNewMethod.make(f"""
public static void flush({PR} pr, double[] s, long now) {{
''', '''# 0.4.31: one Acrobatics award with the unshown counter s[21] staged in SkillMsg (counted = amt is movement XP, added to s[21] first;
# false = fall XP, which gain2 notes itself). If the award levels up, gain4's SkillMsg.send shows the counter BEFORE "SKILL LEVEL UP" ->
# the stage is gone -> s[21] = 0 and the 30 s clock restarts. Not staged when the line could not show (feedback / skills.xpGain off).
# A THROWING award (any Throwable, Errors too - fixer round): the stage is always removed; a stage the line already took -> the counter
# restarts as above; otherwise the movement amount is taken back out of s[21] (0.4.30 never counted an award whose gain2 threw).
acro.addMethod(CtNewMethod.make(f"""
public static void award({PR} pr, double[] s, double t, long amt, boolean counted) {{
  if (counted) s[21] = s[21] + (double) amt;
  java.util.UUID u = pr.getUuid();
  boolean st = s[21] >= 1.0 && {PKG}.SkillCfg.FEEDBACK && {PKG}.SkillStore.notifyOn(u, "skills.xpGain");
  if (st) {PKG}.SkillMsg.stage(u, {PKG}.SkillDefs.ACROBATICS, (long) s[21]);
  try {{
    {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, amt, !counted);
  }} catch (Throwable x) {{
    if (st && !{PKG}.SkillMsg.unstage(u)) {{
      s[21] = 0.0;
      s[22] = t;
    }} else if (counted) s[21] = s[21] - (double) amt;
    if (x instanceof RuntimeException) throw (RuntimeException) x;
    if (x instanceof Error) throw (Error) x;
    throw new RuntimeException(x);
  }}
  if (st && !{PKG}.SkillMsg.unstage(u)) {{
    s[21] = 0.0;
    s[22] = t;
  }}
}}""", acro))
# once per second: pay whole XP (sliding per-minute cap, global multiplier), throttled chat line
acro.addMethod(CtNewMethod.make(f"""
public static void flush({PR} pr, double[] s, long now) {{
''')
rep('''      if (amt > 0L) {{
        {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, amt, false);
        s[21] = s[21] + (double) amt;
      }}
''', '''      if (amt > 0L) award(pr, s, t, amt, true);   // 0.4.31: was gain2(..., false) then s[21] += amt (the line spanned a level-up)
''')
rep('''      if (famt > 0L) {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, famt, true);
''', '''      if (famt > 0L) award(pr, s, t, famt, false);   // 0.4.31: was gain2(..., true) - same award, the counter staged around it
''')

# ---------------------------------------------------------------------------------------------------------------- retain
# fixer round: a player who leaves never keeps a stage (belt and braces - award already removes it on every exit path)
rep('''    {PKG}.ManaRegen.BLOCK.keySet().retainAll(online);   // 0.4.30: the regen blocks of players who left
''', '''    {PKG}.ManaRegen.BLOCK.keySet().retainAll(online);   // 0.4.30: the regen blocks of players who left
    {PKG}.SkillMsg.STAGE.keySet().retainAll(online);   // 0.4.31: a staged Acrobatics counter of a player who left
''')

# ================================================================================================ 0.7 PORT (skills07 round, 2026-10-13)
# Hytale 0.7.0 release assets (research/Hytale-0.7-Port.md). The fixer round left the Mana.json guard an assert; the port replaces it with
# MANA GEN (a generated Mana.json override, below) and teaches SPELL GEN 0.7's staff items (drain var only).

# ---------------------------------------------------------------------------------------------------------------- MANA GEN
# 0.7.0's vanilla Mana.json: InitialValue / Max 100 for everyone, flat refill every 0.3 s +1 while Alive with NO combat pause and NO
# charging pause, + a Creative 1 %/0.5 s entry. Skyy's locked Mana rests on 0.6's file (InitialValue / Max 0, every 0.2 s +1 while Alive,
# NoDamageTaken 6 s, not while Charging):
#   - max Mana = the Base Mana table (docs/answered/skills.md + classes.md: base 25, Mage 45, Priest 42 ... - a TOTAL base). Overall.baseMana
#     posts base - the stat type's max, floored at 0: with type max 100 every player would have 100+ whatever their class (research/
#     Mana-Cost-And-Regen-Research.md 2.4, PreRelease-Compat-Report 3c) -> InitialValue / Max back to 0.
#   - combat = 6 s after TAKING damage, in combat SkyySkills refills mana.regen.inCombat % (75) of (vanilla + boosts) (skills.md R1 / R2,
#     the combat HUD widget = the same window). ManaRegen keys on vanilla's NoDamageTaken pause of the flat entry -> the condition comes back.
#   - Mana keeps regenerating while charging (skills.md 2026-10-02 LOCKED): 0.7 has no Charging pause - nothing to add (ManaRegen still
#     handles one if a later version brings it back).
#   - RATE: 0.6's 5 Mana a second (every 0.2 s +1) - every class number (Class-Power-Split, ability costs, the balance workbench, the
#     /skills mana texts) was tuned and play-tested on it; 0.7's 3.3 a second would cut every class's regen by a third (QUESTION for Skyy).
# Only these keys change; Min, ResetType, Shared and the Creative entry stay 0.7's. A vanilla file already in this shape = no override.
MANA_GEN_SRC = r'''# ================= 0.4.31 MANA GEN (Hytale 0.7.0 port; full notes in tools/skills_0_4_31_patch.py) =================
# Generated from Assets.zip's Server/Entity/Stats/Mana.json read in memory at every build (never committed): InitialValue / Max -> 0 (the
# Base Mana table is a TOTAL base), the flat Additive Alive refill gets the NoDamageTaken MANA_COMBAT_S pause (combat = 6 s after taking
# damage; SkyySkills refills mana.regen.inCombat % there) and the MANA_INTERVAL interval (5 Mana a second, the tuned rate). Nothing else.
MANA_PATH = "Server/Entity/Stats/Mana.json"
MANA_COMBAT_S = 6        # Skyy LOCKED 2026-10-02: in combat = 6 s after taking damage (vanilla 0.6's window)
MANA_INTERVAL = 0.2      # +1 every 0.2 s = 5 Mana a second (0.6; 0.7 vanilla 0.3 s = 3.3 a second)
# >>> MANA GEN (pure Python: SkyySkills/test_skyyskills_0.4.31.py execs this block on the 0.7 file and on synthetic ones)
import copy as _mcopy


def mana_fail(msg):
    raise SystemExit("Mana override: " + msg)


def _mana_num(v):
    return not isinstance(v, bool) and isinstance(v, (int, float))


def mana_gen(van, delay, interval):
    """van = vanilla Mana.json (parsed). Returns (new JSON, [change texts]); new is None when vanilla already has the locked shape.
    Anything this build does not know stops it (mana_fail)."""
    if not isinstance(van, dict):
        mana_fail("Mana.json is not a JSON object")
    new = _mcopy.deepcopy(van)
    ch = []
    if van.get("Min") not in (0, 0.0) or not _mana_num(van.get("Min")):
        mana_fail("Min is %r (expected 0)" % (van.get("Min"),))
    for k in ("InitialValue", "Max"):
        if not _mana_num(van.get(k)) or van.get(k) < 0:
            mana_fail("%s is %r (expected a number >= 0)" % (k, van.get(k)))
        if van[k] != 0:
            new[k] = 0
            ch.append("%s %r -> 0" % (k, van[k]))
    reg = van.get("Regenerating")
    if not isinstance(reg, list) or not all(isinstance(r, dict) for r in reg):
        mana_fail("Regenerating is not a list of objects: %r" % (reg,))
    flat = []
    for i in range(len(reg)):
        r = reg[i]
        cs = r.get("Conditions", [])
        if not isinstance(cs, list) or not all(isinstance(c, dict) for c in cs):
            mana_fail("regen entry %d: Conditions is not a list of objects" % i)
        if str(r.get("RegenType", "")).lower() == "additive" and _mana_num(r.get("Amount")) and r["Amount"] > 0 \
                and _mana_num(r.get("Interval")) and r["Interval"] > 0:
            flat.append(i)
    if len(flat) != 1:
        mana_fail("%d positive Additive regen entries (expected exactly 1: the flat refill)" % len(flat))
    i = flat[0]
    r = reg[i]
    cs = r.get("Conditions", [])
    ids = [c.get("Id") for c in cs]
    if r.get("Amount") != 1:
        mana_fail("the flat refill adds %r a pulse (expected 1)" % (r.get("Amount"),))
    if ids.count("Alive") != 1 or [c for c in cs if c.get("Id") == "Alive"][0].get("Inverse"):
        mana_fail("the flat refill's conditions %r do not hold exactly one plain Alive" % (ids,))
    bad = [x for x in ids if x not in ("Alive", "NoDamageTaken", "Charging")]
    if bad:
        mana_fail("the flat refill has condition(s) %r this build does not know" % (bad,))
    nds = [c for c in cs if c.get("Id") == "NoDamageTaken"]
    if len(nds) > 1 or any(c.get("Inverse") for c in nds):
        mana_fail("the flat refill has %d NoDamageTaken condition(s), inverse %r" % (len(nds), [c.get("Inverse") for c in nds]))
    if not nds:
        ncs = _mcopy.deepcopy(cs)
        ncs.insert(ids.index("Alive") + 1, {"Id": "NoDamageTaken", "Delay": delay})
        new["Regenerating"][i]["Conditions"] = ncs
        ch.append("flat refill + NoDamageTaken %s s (the combat pause)" % delay)
    if r.get("Interval") != interval:
        new["Regenerating"][i]["Interval"] = interval
        ch.append("flat refill every %r s -> %r s (%s -> %s Mana a second)" % (
            r.get("Interval"), interval, round(1.0 / r["Interval"], 2), round(1.0 / interval, 2)))
    # self-check: exactly the planned keys differ, and putting vanilla's values back gives vanilla
    back = _mcopy.deepcopy(new)
    for k in ("InitialValue", "Max"):
        back[k] = van[k]
    back["Regenerating"][i]["Interval"] = r["Interval"]
    if "Conditions" in r:
        back["Regenerating"][i]["Conditions"] = _mcopy.deepcopy(r["Conditions"])
    if back != van or json.dumps(back) != json.dumps(van):
        mana_fail("the generated file differs from vanilla in more than the planned keys")
    if [k for k in new] != [k for k in van] or len(new["Regenerating"]) != len(reg):
        mana_fail("the generated file's key order / entry count changed")
    return (new if ch else None), ch
# <<< MANA GEN
with zipfile.ZipFile(ASSETS) as _mz:
    _mnames = [n for n in _mz.namelist() if n.startswith("Server/Entity/Stats/") and n.endswith(("/Mana.json", "/Mana.patch"))]
    if _mnames != [MANA_PATH]:
        mana_fail("Assets.zip has %r (expected exactly %s)" % (_mnames, MANA_PATH))
    if json.loads(_mz.read(MANA_PATH).decode("utf-8-sig")) != _mana:
        mana_fail("%s is not the Mana stat the checks read" % MANA_PATH)
MANA_VANILLA = _mana
MANA_NEW, MANA_CHANGES = mana_gen(MANA_VANILLA, MANA_COMBAT_S, MANA_INTERVAL)
MANA_FILES = {}
if MANA_NEW is not None:
    _mtxt = json.dumps(MANA_NEW, indent=2, ensure_ascii=True) + "\n"
    assert json.loads(_mtxt) == MANA_NEW and all(ord(ch) < 128 for ch in _mtxt)
    MANA_FILES[MANA_PATH] = _mtxt
    _mana = MANA_NEW
print("Mana override (0.4.31, generated from Assets.zip): %s" % ("; ".join(MANA_CHANGES) if MANA_CHANGES else
                                                                 "none needed - vanilla Mana.json already has the locked shape"))
'''
rep('''_mreg = _mana.get("Regenerating") or []
print("vanilla Mana: Max %r, ResetType %r, Regenerating %s" % (_mana.get("Max"), _mana.get("ResetType"),
''', MANA_GEN_SRC + '''_mreg = _mana.get("Regenerating") or []
print("Mana as this jar ships it: Max %r, ResetType %r, Regenerating %s" % (_mana.get("Max"), _mana.get("ResetType"),
''')
# ---------------------------------------------------------------------------------------------------------------- SPELL GEN on 0.7
# 0.7.0 dropped the DEAD cast-check var (Staff_Cast_Summon_Charged {Costs Mana 50}) from the staffs and the Halloween Broomstick - research
# 1.2 / 2.4: nothing ever read it (no Replace names it); the engine's check is the charged cast step's own interaction, which spell_int_plan
# already turns into a StatsCondition ("check+") and spell_verify proves item by item. So an item may now carry its drain var alone; the
# override then changes only that drain (the gate simulation still requires every paid cast to check what it spends). The item table's
# cast check columns hold -1 ("none") for such an item (ManaCost.OLD / COST: nothing reads them, texts only).
rep('''        if len(nc) != 1 or len(nd) != 1:
            spell_fail("%s has %d Mana cast check(s) and %d drain(s) - expected exactly one of each" % (iid, len(nc), len(nd)))
''', '''        if len(nc) > 1 or len(nd) != 1:   # 0.4.31 (Hytale 0.7): the dead cast check var may be gone (staffs, Broomstick)
            spell_fail("%s has %d Mana cast check(s) and %d drain(s) - expected one drain and at most one (dead) cast check var" % (
                iid, len(nc), len(nd)))
''')
rep('''    _c = [x for x in _e if x[1] == "Costs"][0]
''', '''    _c = ([x for x in _e if x[1] == "Costs"] or [(None, "Costs", -1, -1)])[0]   # 0.4.31: -1 = no (dead) cast check var (Hytale 0.7)
''')
rep('''for _t in SPELL_TABLE:
    print("  %-34s cast check %3d -> %2d   drain %3d -> %2d" % _t)
''', '''for _t in SPELL_TABLE:
    print("  %-34s cast check %4s -> %4s   drain %3d -> %2d" % (_t[0], "none" if _t[1] < 0 else _t[1], "none" if _t[2] < 0 else _t[2], _t[3], _t[4]))
''')

# MANA GEN clash check: no other jar of the live set and no pack mod may ship a Mana stat file (Mana.json or a 0.7 Mana.patch) - two would
# fight over the stat (research: Hexcode ships a Mana.patch; it is not in the pack). Other installed mods are listed as a NOTE.
rep('''    _cl = _spell_clash(_nm, armory=(_man.get("Group") == "Skyy" and str(_man.get("Name", "")).endswith(" SkyyArmory")))   # 0.4.15: it owns the 8
''', '''    _cl = _spell_clash(_nm, armory=(_man.get("Group") == "Skyy" and str(_man.get("Name", "")).endswith(" SkyyArmory")))   # 0.4.15: it owns the 8
    _mcl = [_n for _n in _nm if _n.startswith("Server/Entity/Stats/") and os.path.basename(_n) in ("Mana.json", "Mana.patch")]   # 0.4.31
    if _mcl and MANA_FILES and _key in _packs:
        mana_fail("pack mod %s (%s) also ships %s - two Mana stat files would fight" % (_key, _f, _mcl))
    if _mcl and MANA_FILES and not str(_man.get("Name", "")).endswith("SkyySkills"):
        _mana_other.append("%s (%s)" % (_f, ", ".join(os.path.basename(_x) for _x in _mcl)))
''')
rep('''_pk_found, _other, _pk_mana = [], [], []
''', '''_pk_found, _other, _pk_mana = [], [], []
_mana_other = []   # 0.4.31: installed mods outside the pack that ship a Mana stat file (NOTE only)
for _mod, _ver in _pins:   # 0.4.31: no other jar of the live set ships a Mana stat file
    _jp = os.path.join(os.path.dirname(HERE), _mod, "%s-%s.jar" % (_mod, _ver))
    if _mod != "SkyySkills" and MANA_FILES and os.path.isfile(_jp):
        with zipfile.ZipFile(_jp) as _mj:
            _mcl = [_n for _n in _mj.namelist() if _n.startswith("Server/Entity/Stats/") and os.path.basename(_n) in ("Mana.json", "Mana.patch")]
        if _mcl:
            mana_fail("%s %s also ships %s - two Mana stat files would fight" % (_mod, _ver, _mcl))
''')
rep('''if _other:
    print("spell costs: NOTE mods in the Mods folder that are NOT in the live set also replace some of these items (only a problem if "
''', '''ONHIT_INHERIT = []   # 0.4.31 critic 2: live-set items that inherit a generated on-hit file by "Parent" get OUR Amount (NOTE)
for _mod, _ver in _pins:
    _jp = os.path.join(os.path.dirname(HERE), _mod, "%s-%s.jar" % (_mod, _ver))
    if _mod != "SkyySkills" and ONHIT_IDS and os.path.isfile(_jp):
        with zipfile.ZipFile(_jp) as _ij:
            _itx = dict((_n, _ij.read(_n).decode("utf-8-sig", "replace")) for _n in _ij.namelist()
                        if _n.startswith("Server/Item/Items/") and _n.endswith(".json"))
        for _iid, _par in onhit_inheritors(_itx, ONHIT_IDS):
            ONHIT_INHERIT.append("%s %s %s (Parent %s)" % (_mod, _ver, _iid, _par))
if ONHIT_INHERIT:
    print("Mana on hit: NOTE %d live-set item(s) inherit a generated on-hit file by Parent and so get its Mana / %d too: %s" % (
        len(ONHIT_INHERIT), SPELL_DIVISOR, "; ".join(ONHIT_INHERIT)))
print("Mana override (0.4.31): no other live-set jar and no pack mod ships a Mana stat file%s" % (
    ("; NOTE installed mods outside the pack that do (only a problem if they are ever enabled): " + ", ".join(_mana_other)) if _mana_other else ""))
if _other:
    print("spell costs: NOTE mods in the Mods folder that are NOT in the live set also replace some of these items (only a problem if "
''')

# the generated Mana.json goes into the asset pack next to the spell and dodge files
rep('''ASSET_FILES.update(DODGE_FILES)
B.assemble(jar, m, OUT, ASSET_FILES)
''', '''ASSET_FILES.update(DODGE_FILES)
assert list(MANA_FILES) in ([], [MANA_PATH]) and not set(MANA_FILES) & set(ASSET_FILES)   # 0.4.31: the generated Mana.json (MANA GEN)
ASSET_FILES.update(MANA_FILES)
assert not set(ONHIT_FILES) & set(ASSET_FILES) and all(_p.startswith("Server/Item/Interactions/") for _p in ONHIT_FILES)   # 0.4.31 fixer
ASSET_FILES.update(ONHIT_FILES)   # 0.4.31 fixer round: the Mana-on-hit overrides (ONHIT GEN)
# 0.4.31 fixer round: the Mana consumer scan - every Server/ JSON of Assets.zip naming the Mana stat, by what covers it
MANA_COVER = mana_consumers(MANA_NAMED, set(ASSET_FILES), set(ARMORY_OWNED + BO_OWNED), set(SPELL_UNCHANGED))
print("Mana consumer scan (0.4.31, Assets.zip): %d files name the Mana stat - %s" % (
    len(MANA_NAMED), "; ".join("%s %d" % (_k, len(_v)) for _k, _v in MANA_COVER.items() if _v)))
print("Mana consumer scan: NOTE vanilla rune abilities keep 0.7's Mana cost (not / %d - the SkyyClasses ability round decides; until then "
      "a player below that max Mana cannot cast them, e.g. a no-class 25 pool casts none): %s" % (SPELL_DIVISOR, ", ".join(RUNE_COSTS) or "none"))
if MANA_COVER["NOT COVERED"]:
    print("Mana consumer scan: NOTE %d Mana file(s) this build does not cover (new in this Hytale version? check them): %s" % (
        len(MANA_COVER["NOT COVERED"]), ", ".join(MANA_COVER["NOT COVERED"])))
B.assemble(jar, m, OUT, ASSET_FILES)
''')

# ================================================================================================ 0.7 PORT FIXER ROUND (skills07fix)
# ---------------------------------------------------------------------------------------------------------------- ONHIT GEN
# Hytale 0.7.0 (NEW - 0.6.8 / 0.7.0-pre.4 gave SignatureEnergy +2 or nothing there): 9 weapon SIGNATURE damage interactions give the attacker
# Mana on hit (EntityStatsOnHit EntityStatId Mana: Mace Groundslam 25, Crossbow signature bolt 50, Shortbow Volley 20, Daggers Lunge 15 /
# Slash 5 / Sweep 5, Sword Vortexstrike Stab 15 / Spin 5, Battleaxe Whirlwind 4; x MultipliersPerEntitiesHit per extra target), sized for
# 0.7's 100-Mana pools and 25-50 Mana runes. On our pools (25-55: the Base Mana table) one Groundslam / crossbow signature hit would fill
# any bar, past SkyySkills' own capped Mana on hit (+1 a class-weapon hit, 0.5 s cooldown). Same rule as every vanilla spell cost since
# 0.4.8 (Skyy 2026-09-30: Mana / 5): generated overrides with ONLY those Amounts / SPELL_DIVISOR (rounded half up, at least 1): 25 -> 5,
# 50 -> 10, 20 -> 4, 15 -> 3, 5 -> 1, 4 -> 1. QUESTION for Skyy (default this / 5): keep 0.7's full grants, or none at all.
# MANA CONSUMER SCAN: every Server/ JSON of Assets.zip that names the Mana stat is listed by what covers it; anything new prints a NOTE.
# Vanilla RUNE abilities (Rune_* Cost 30-50 Mana) are NOT scaled here (the rune keys / vanilla-rune policy belong to the SkyyClasses ability
# round - research/cloud/Ability-Engine-Plan.md Q8 [vanilla runes blocked for classed players]); the build prints them (QUESTION for Skyy).
ONHIT_GEN_SRC = r'''# ================= 0.4.31 MANA ON HIT / SPELL_DIVISOR (Hytale 0.7.0 port, fixer round; notes in tools/skills_0_4_31_patch.py) =================
# 0.7's weapon signature damage interactions give the attacker Mana on hit (EntityStatsOnHit, EntityStatId Mana: Groundslam 25, crossbow
# signature bolt 50 ...), sized for 0.7's 100-Mana pools. Generated from Assets.zip at every build (never committed): ONLY each such
# Amount / SPELL_DIVISOR (rounded half up, at least 1). Plus the Mana consumer scan (every Server/ JSON naming the Mana stat, by what covers it).
# >>> ONHIT GEN (pure Python: SkyySkills/test_skyyskills_0.4.31.py execs this block on the 0.7 files and on synthetic ones)
import copy as _ocopy
import math as _omath
ONHIT_KEYS = ("EntityStatId", "Amount", "MultipliersPerEntitiesHit", "MultiplierPerExtraEntityHit")


def onhit_fail(msg):
    raise SystemExit("Mana on hit: " + msg)


def onhit_new(v, div):
    """|v| / div rounded half up, at least 1; 0 stays 0; the sign is kept (spell_new's rule, numbers may be fractional)"""
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
        onhit_fail("an Amount %r is not a number" % (v,))
    if v == 0:
        return 0
    m = int(_omath.floor(abs(v) / float(div) + 0.5))
    if m < 1:
        m = 1
    return m if v > 0 else -m


def _onhit_walk(x, path, out):
    """every Mana entry of every EntityStatsOnHit list in x, in document order: [(where, entry dict)]"""
    if isinstance(x, dict):
        for k in x:
            if k == "EntityStatsOnHit":
                lst = x[k]
                if not isinstance(lst, list):
                    onhit_fail("%s/EntityStatsOnHit is not a list" % path)
                for i in range(len(lst)):
                    if isinstance(lst[i], dict) and lst[i].get("EntityStatId") == "Mana":
                        out.append(("%s/EntityStatsOnHit[%d]" % (path, i), lst[i]))
            else:
                _onhit_walk(x[k], path + "/" + k, out)
    elif isinstance(x, list):
        for i in range(len(x)):
            _onhit_walk(x[i], "%s[%d]" % (path, i), out)
    return out


def onhit_plan(files, div):
    """files = {asset path: parsed JSON} -> [(path, new JSON, [(where, old, new)])] sorted by path, for every file whose Mana-on-hit
    Amounts change. An entry with keys this build does not know (an AmountType ...) or no number Amount stops the build."""
    plan = []
    for p in sorted(files):
        van = files[p]
        new = _ocopy.deepcopy(van)
        hits = _onhit_walk(new, "", [])
        if not hits:
            continue
        ch = []
        for where, e in hits:
            if "Amount" not in e or [k for k in e if k not in ONHIT_KEYS]:
                onhit_fail("%s %s: a Mana on-hit entry this build does not know: %r" % (p, where, e))
            o = e["Amount"]
            n = onhit_new(o, div)
            if n != o:
                e["Amount"] = n
                ch.append((where, o, n))
        back = _ocopy.deepcopy(new)   # self-check: the old Amounts put back give vanilla, key order included
        vh = _onhit_walk(_ocopy.deepcopy(van), "", [])
        bh = _onhit_walk(back, "", [])
        if len(vh) != len(bh):
            onhit_fail("%s: the Mana entry count changed" % p)
        for i in range(len(bh)):
            bh[i][1]["Amount"] = vh[i][1]["Amount"]
        if back != van or json.dumps(back) != json.dumps(van):
            onhit_fail("%s: the generated file differs from vanilla in more than the Mana on-hit Amounts" % p)
        if ch:
            plan.append((p, new, ch))
    return plan


def mana_consumers(names, shipped, owned, left0):
    """names = the Server/ JSON paths of Assets.zip whose text names the Mana stat; shipped = this jar's asset paths; owned = SkyyArmory's
    item ids; left0 = the spell items left alone (all 0 costs) -> {category: [paths]} ("NOT COVERED" = new to this build: a NOTE)"""
    out = {"overridden by this jar": [], "SkyyArmory's items": [], "0 Mana cost (left alone)": [],
           "left as vanilla (armor max Mana, effects, tests, debug, saved prefabs)": [], "vanilla runes (not scaled)": [], "NOT COVERED": []}
    for n in sorted(names):
        b = n.rsplit("/", 1)[-1][:-5]
        if n in shipped:
            k = "overridden by this jar"
        elif n.startswith("Server/Item/Items/") and b in owned:
            k = "SkyyArmory's items"
        elif n.startswith("Server/Item/Items/") and b in left0:
            k = "0 Mana cost (left alone)"
        elif "/_Debug/" in n or n.startswith(("Server/Item/Items/Armor/", "Server/Entity/Effects/Mana/", "Server/Item/Interactions/Tests/",
                                             "Server/Prefabs/")):
            k = "left as vanilla (armor max Mana, effects, tests, debug, saved prefabs)"
        elif n.startswith("Server/Item/Items/Rune/Ability/"):
            k = "vanilla runes (not scaled)"
        else:
            k = "NOT COVERED"
        out[k].append(n)
    return out


def _onhit_parents(x, ids, out):
    """every "Parent" value in x that names one of ids (document order)"""
    if isinstance(x, dict):
        for k in x:
            if k == "Parent" and isinstance(x[k], str) and x[k] in ids:
                out.append(x[k])
            else:
                _onhit_parents(x[k], ids, out)
    elif isinstance(x, list):
        for v in x:
            _onhit_parents(v, ids, out)
    return out


def onhit_inheritors(texts, ids):
    """texts = {jar path: JSON text} of another live-set jar; ids = the generated on-hit interaction ids -> [(item id, parent id)] for every
    Server/Item/Items JSON that inherits one of them by "Parent" (it then gets OUR Mana-on-hit Amount: a NOTE, not a clash - 0.4.31 critic 2)"""
    out = []
    ids = set(ids)
    for n in sorted(texts):
        if not (n.startswith("Server/Item/Items/") and n.endswith(".json")):
            continue
        t = texts[n]
        if not [i for i in ids if i in t]:
            continue
        for par in sorted(set(_onhit_parents(json.loads(t), ids, []))):
            out.append((n.rsplit("/", 1)[-1][:-5], par))
    return out
# <<< ONHIT GEN
ONHIT_SRC, MANA_NAMED, RUNE_COSTS = {}, [], []
with zipfile.ZipFile(ASSETS) as _oz:
    for _n in _oz.namelist():
        if not (_n.startswith("Server/") and _n.endswith(".json")):
            continue
        _t = _oz.read(_n).decode("utf-8-sig", "replace")
        if '"Mana"' not in _t:
            continue
        MANA_NAMED.append(_n)
        if '"EntityStatsOnHit"' in _t:
            _j = json.loads(_t)
            if _onhit_walk(_j, "", []):
                if not _n.startswith("Server/Item/Interactions/"):
                    onhit_fail("%s gives Mana on hit outside Server/Item/Interactions - this build does not know it" % _n)
                ONHIT_SRC[_n] = _j
        if _n.startswith("Server/Item/Items/Rune/Ability/") and "/_Debug/" not in _n:
            _ab = (json.loads(_t).get("Ability") or {})
            if _ab.get("CostType") == "Mana":
                RUNE_COSTS.append("%s %s" % (_n.rsplit("/", 1)[-1][:-5], _ab.get("Cost")))
ONHIT_PLAN = onhit_plan(ONHIT_SRC, SPELL_DIVISOR)
ONHIT_FILES = {}
for _p, _nj, _ch in ONHIT_PLAN:
    _txt = json.dumps(_nj, indent=2, ensure_ascii=True) + "\n"
    assert json.loads(_txt) == _nj and all(ord(ch) < 128 for ch in _txt) and _p not in SPELL_FILES
    ONHIT_FILES[_p] = _txt
ONHIT_IDS = [_p.rsplit("/", 1)[-1][:-5] for _p in sorted(ONHIT_FILES)]
assert len(set(ONHIT_IDS)) == len(ONHIT_IDS) and not set(ONHIT_IDS) & set(SPELL_INT_IDS)
print("Mana on hit /%d (0.4.31, Hytale 0.7): %d signature interaction overrides generated from Assets.zip%s" % (
    SPELL_DIVISOR, len(ONHIT_PLAN), "" if ONHIT_PLAN else " (none - 0.7's Mana on hit is gone)"))
for _p, _nj, _ch in ONHIT_PLAN:
    print("  %-52s Mana on hit %s" % (_p.rsplit("/", 1)[-1][:-5], ", ".join("%s -> %s" % (_c[1], _c[2]) for _c in _ch)))
'''
rep('''def _spell_clash(names, armory=False):
''', ONHIT_GEN_SRC + '''

def _spell_clash(names, armory=False):
''')
# a live-set jar / pack mod shipping one of the generated on-hit files (path, or an interaction of the same id) clashes like a spell file
rep('''    return sorted(n for n in names if n in SPELL_FILES or (n.startswith("Server/Item/Items/") and n.endswith(".json")
''', '''    return sorted(n for n in names if n in SPELL_FILES or n in ONHIT_FILES   # 0.4.31: + the Mana-on-hit overrides
                  or (n.startswith("Server/Item/Interactions/") and n.endswith(".json") and os.path.basename(n)[:-5] in ONHIT_IDS)
                  or (n.startswith("Server/Item/Items/") and n.endswith(".json")
''')

# ---------------------------------------------------------------------------------------------------------------- ManaGuard: the live Mana stat
# Critic finding (LOW): nothing at runtime proved the generated Mana.json is the stat the server uses. Another enabled mod's Mana.json /
# Mana.patch loaded later would silently give everyone Max 100, no combat pause and no class Base Mana. ManaGuard's pack tick (once, from
# 10 s, the same retries) now reads the LIVE Mana stat type (EntityStatType asset map, DefaultEntityStatTypes.getMana()) and compares its
# Max, its flat refill per second and the NoDamageTaken pause with what this jar ships: INFO when they match, one WARN naming each
# difference (and the pack that won, if readable). Logging only - never a number changed.
rep('''# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
''', '''# 0.4.31 (fixer round): the LIVE Mana stat vs the Mana.json this jar ships (MANA GEN) - Max, flat refill a second, the NoDamageTaken pause
_mg_flat = [_r for _r in (_mana.get("Regenerating") or []) if str(_r.get("RegenType", "")).lower() == "additive"
            and _mana_num(_r.get("Amount")) and _r["Amount"] > 0 and _mana_num(_r.get("Interval")) and _r["Interval"] > 0]
MANA_EXP_MAX = float(_mana.get("Max", 0))
MANA_EXP_PS = round(sum(_r["Amount"] / float(_r["Interval"]) for _r in _mg_flat), 4)
MANA_EXP_PAUSE = any(_c.get("Id") == "NoDamageTaken" and not _c.get("Inverse") for _r in _mg_flat for _c in (_r.get("Conditions") or []))
assert (not MANA_FILES) or (MANA_EXP_MAX == 0.0 and MANA_EXP_PS == round(1.0 / MANA_INTERVAL, 4) and MANA_EXP_PAUSE), (MANA_EXP_MAX, MANA_EXP_PS)
mgd.addField(CtField.make("public static final float MANA_MAX = %sf;" % repr(MANA_EXP_MAX), mgd))
mgd.addField(CtField.make("public static final float MANA_PS = %sf;" % repr(MANA_EXP_PS), mgd))
mgd.addField(CtField.make("public static final boolean MANA_PAUSE = %s;" % ("true" if MANA_EXP_PAUSE else "false"), mgd))
mgd.addField(CtField.make("public static final boolean MANA_SHIPPED = %s;" % ("true" if MANA_FILES else "false"), mgd))
mgd.addField(CtField.make("public static volatile boolean MANA_DONE = false;", mgd))
mgd.addField(CtField.make('public static volatile String MANA_LAST = "";', mgd))
# {max, initial, flat refill a second (ManaRegen.baseOf: positive Additive entries), 1 = a positive Additive entry has a NoDamageTaken
# condition} of a Mana stat type; null = none
mgd.addMethod(CtNewMethod.make(J14(r"""
public static float[] manaFacts(@ESTT@ t) {
  if (t == null) return null;
  float ps = 0.0f;
  boolean pause = false;
  @RGN@[] rs = t.getRegenerating();
  if (rs != null) {
    for (int i = 0; i < rs.length; i++) {
      float b = @PKG@.ManaRegen.baseOf(rs[i]);
      if (!(b > 0.0f)) continue;
      ps = ps + b;
      @CND@[] cs = rs[i].getConditions();
      if (cs == null) continue;
      for (int j = 0; j < cs.length; j++) if (cs[j] instanceof @NDT@) pause = true;
    }
  }
  return new float[] { t.getMax(), t.getInitialValue(), ps, pause ? 1.0f : 0.0f };
}"""), mgd))
# facts (null = not readable yet) + the pack the live stat came from (null = unknown) -> {level "info" / "warn" / "" (try again), message}
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String[] manaReport(float[] f, String pack) {
  if (f == null || f.length < 4) return new String[] { "", "the game's Mana stat could not be read" };
  String pre = "Mana stat (Hytale 0.7, " + (MANA_SHIPPED ? "this jar's generated Mana.json" : "vanilla's Mana.json") + "): ";
  String from = pack != null ? " (the game takes it from " + pack + ")" : "";
  StringBuilder bad = new StringBuilder();
  if (Math.abs(f[0] - MANA_MAX) > 0.001f) bad.append("max ").append(@PKG@.Overall.num((double) f[0])).append(" instead of ").append(@PKG@.Overall.num((double) MANA_MAX)).append(" (the Base Mana by class table ").append(f[0] > MANA_MAX ? "is cut by it - everyone has at least " + @PKG@.Overall.num((double) f[0]) + " Mana" : "is off by it").append(")");
  if (Math.abs(f[2] - MANA_PS) > 0.01f) { if (bad.length() > 0) bad.append("; "); bad.append("refill ").append(@PKG@.Overall.num((double) f[2])).append(" a second instead of ").append(@PKG@.Overall.num((double) MANA_PS)); }
  if ((f[3] > 0.5f) != MANA_PAUSE) { if (bad.length() > 0) bad.append("; "); bad.append(MANA_PAUSE ? "no combat pause (NoDamageTaken) - the in-combat Mana regen and the combat HUD never run" : "a combat pause this jar does not ship"); }
  if (bad.length() == 0) return new String[] { "info", pre + "active - max " + @PKG@.Overall.num((double) f[0]) + ", refill " + @PKG@.Overall.num((double) f[2]) + " a second, " + (MANA_PAUSE ? "paused 6 s after taking damage (in combat SkyySkills refills its share)" : "no combat pause") + from };
  return new String[] { "warn", pre + "NOT the one in effect - " + bad.toString() + from + ". Another mod's Mana.json / Mana.patch probably loads after SkyySkills: remove or disable it, or the class Mana numbers are wrong." };
}"""), mgd))
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String[] manaCheck() {
  try {
    int mi = @DST@.getMana();
    @ESTT@ t = (@ESTT@) @ESTT@.getAssetMap().getAsset(mi);
    if (t == null) return manaReport(null, null);
    String pk = null;
    try {
      Object m = @ESTT@.getAssetMap();
      if (m instanceof com.hypixel.hytale.assetstore.map.DefaultAssetMap) pk = ((com.hypixel.hytale.assetstore.map.DefaultAssetMap) m).getAssetPack(t.getId());
    } catch (Throwable x) { pk = null; }
    return manaReport(manaFacts(t), pk);
  } catch (Throwable e) { return manaReport(null, null); }
}"""), mgd))
# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
''')
rep('''  if (!ARM_DONE) {{   // 0.4.15: the staff handover - which pack the 8 SkyyArmory-owned staffs come from
    String[] a = armCheck();
''', '''  if (!MANA_DONE) {{   // 0.4.31: the live Mana stat vs the generated Mana.json
    String[] q2 = manaCheck();
    if (q2[0].length() > 0) {{
      MANA_DONE = true;
      MANA_LAST = q2[1];
      if ("warn".equals(q2[0])) {PKG}.SkillCfg.warn(q2[1]);
      else {PKG}.SkillCfg.info(q2[1]);
    }}
  }}
  if (!ARM_DONE) {{   // 0.4.15: the staff handover - which pack the 8 SkyyArmory-owned staffs come from
    String[] a = armCheck();
''')
rep('''  if (ITEMS_DONE && INT_DONE && ARM_DONE) {{
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
''', '''  if (ITEMS_DONE && INT_DONE && ARM_DONE && MANA_DONE) {{   // 0.4.31: + MANA_DONE
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
    if (!MANA_DONE) {{
      MANA_LAST = "Mana stat: the game's Mana stat could not be read to check it against the Mana.json this jar ships - not checked";
      {PKG}.SkillCfg.info(MANA_LAST);
    }}
''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.31 adds no system and no command"
assert s.count("pool.makeClass(") == CLS0, "0.4.31 adds no class"
assert s.count("SkillMsg.stage(") == 1 and s.count("SkillMsg.unstage(") == 2 and s.count("SkillMsg.STAGE.keySet().retainAll(online)") == 1
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.30 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.30,", len(_gone), "0.4.30 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
